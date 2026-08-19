import os
import time
import asyncio
import logging
from typing import Iterator
from typing import List, Tuple, Optional
import numpy as np

from core.benchmark.models import (
    PreparedBenchmarkDataset, 
    BenchmarkDocument,
    ProviderDescriptor,
    BenchmarkMetadata,
    BenchmarkRunReport,
    MetricAggregator,
    QualityPolicy,
    BenchmarkMode,   
    QuotaSnapshot,
    StatisticalMoments,
    HardwareTelemetry,
    MetricResult,
)
from core.benchmark.ports import (
    BenchmarkRunnerProtocol,
    BenchmarkCandidateProvider,
    BenchmarkEvaluatorProtocol,
    GroundTruthProviderProtocol,
    BenchmarkArtifact,
)
from core.benchmark.persistence import BenchmarkPersistenceGateway
from core.benchmark.quality import StructuralQualityEvaluator
from core.benchmark.reporter import StatisticalComparator

logger = logging.getLogger(__name__)




def _iter_file_chunks(file_path: os.PathLike | str, chunk_size: int = 8192) -> Iterator[bytes]:
    """Imperative Shell: I/O aislado en el borde."""
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


class DatasetIntegrityValidator:
    """Validador de consistencia del set de datos."""
    
    @staticmethod
    def verify(document: BenchmarkDocument) -> bool:
        if not os.path.exists(document.file_path):
            logger.error(f"Falla de Fixture: Archivo ausente en {document.file_path}")
            return False
            
        from core.shared.crypto import compute_sha256_stream
        computed_hash = compute_sha256_stream(_iter_file_chunks(document.file_path))
        if computed_hash != document.file_sha256:
            logger.error(
                f"Corrupción detectada en {document.id}. Esperado: {document.file_sha256}, Obtenido: {computed_hash}"
            )
            return False
            
        return True


class SequentialBenchmarkOrchestrator:
    """
    Driver de aislamiento físico y orquestación polimórfica de benchmark.
    Soporta evaluaciones individuales de candidatos (parsers) y experimentos A/B (LLMs).
    """
    
    def __init__(
        self, 
        baseline_runner: Optional[BenchmarkRunnerProtocol] = None, 
        challenger_runner: Optional[BenchmarkRunnerProtocol] = None,
        persistence: Optional[BenchmarkPersistenceGateway] = None,
        cooldown_seconds: float = 10.0,
        git_commit_sha: str = "unknown"
    ):
        self._baseline = baseline_runner
        self._challenger = challenger_runner
        self._persistence = persistence
        self.cooldown_seconds = cooldown_seconds
        self.git_commit_sha = git_commit_sha

    def evaluate_candidate(
        self,
        document_id: str,
        provider: BenchmarkCandidateProvider,
        ground_truth_provider: GroundTruthProviderProtocol,
        evaluators: List[BenchmarkEvaluatorProtocol]
    ) -> Tuple[float, Optional[BenchmarkArtifact], List[MetricResult]]:
        """
        Coordina la evaluación de un candidato individual (ej. parser/extractor)
        recorriendo la lista de evaluadores inyectados.
        """
        logger.info(f"Evaluando documento '{document_id}' con proveedor '{provider.provider_name}'...")
        
        start_time = time.monotonic()
        candidate_artifact = provider.provide(document_id)
        execution_time = time.monotonic() - start_time

        ground_truth = ground_truth_provider.get_ground_truth(document_id)

        metric_results: List[MetricResult] = []
        for evaluator in evaluators:
            result = evaluator.evaluate(candidate_artifact, ground_truth)
            metric_results.append(result)

        artifact_out = candidate_artifact if isinstance(candidate_artifact, BenchmarkArtifact) else None
        
        return execution_time, artifact_out, metric_results

    async def run_experiment(
        self, 
        dataset: PreparedBenchmarkDataset, 
        baseline_desc: ProviderDescriptor,
        challenger_desc: ProviderDescriptor,
        quality_policy: QualityPolicy 
    ) -> BenchmarkRunReport:
        if not self._baseline or not self._challenger:
            raise RuntimeError("run_experiment requiere que baseline_runner y challenger_runner estén configurados.")

        # 1. Validación Pre-vuelo
        for doc in dataset.manifest.documents:  
            if not DatasetIntegrityValidator.verify(doc):
                raise RuntimeError(f"Dataset no reproducible: {dataset.manifest.dataset_id}")

        baseline_name = f"{baseline_desc.provider}_{baseline_desc.model}"
        challenger_name = f"{challenger_desc.provider}_{challenger_desc.model}"

        # 2. Baseline Run
        logger.info(f"Evaluación Baseline: {baseline_name}")
        await self._baseline.warmup()
        b_start = time.monotonic()
        baseline_res = await self._baseline.execute_dataset(dataset, force_cache_bypass=True)
        baseline_makespan = time.monotonic() - b_start
        await self._baseline.teardown()
        
        if self._persistence:
            self._persistence.save_raw_records_checkpoint(
                dataset.manifest.dataset_id, baseline_name, baseline_res.raw_records
            )

        # 3. Cooldown
        logger.info(f"Cooldown de {self.cooldown_seconds}s...")
        await asyncio.sleep(self.cooldown_seconds)

        # 4. Challenger Run
        logger.info(f"Evaluación Challenger: {challenger_name}")
        await self._challenger.warmup()
        c_start = time.monotonic()
        challenger_res = await self._challenger.execute_dataset(dataset, force_cache_bypass=True)
        challenger_makespan = time.monotonic() - c_start
        await self._challenger.teardown()
        
        if self._persistence:
            self._persistence.save_raw_records_checkpoint(
                dataset.manifest.dataset_id, challenger_name, challenger_res.raw_records
            )

        # 5. Agregación y Ensamblaje
        baseline_quality = StructuralQualityEvaluator.evaluate(dataset, baseline_res)
        challenger_quality = StructuralQualityEvaluator.evaluate(dataset, challenger_res)
        
        b_mode = getattr(self._baseline, 'mode', BenchmarkMode.EQUALIZED)
        b_quota = getattr(self._baseline, 'quota_snapshot', QuotaSnapshot(0, 0, 0))
        c_mode = getattr(self._challenger, 'mode', BenchmarkMode.EQUALIZED)
        c_quota = getattr(self._challenger, 'quota_snapshot', QuotaSnapshot(0, 0, 0))

        b_lats = [r.latency_ms for r in baseline_res.raw_records if r.success]
        c_lats = [r.latency_ms for r in challenger_res.raw_records if r.success]

        b_moments = StatisticalMoments(
            median_ci_95=StatisticalComparator._bootstrap_estimator_ci(b_lats, np.median),
            p95_ci_95=StatisticalComparator._bootstrap_estimator_ci(b_lats, lambda x: np.percentile(x, 95))
        )
        c_moments = StatisticalMoments(
            median_ci_95=StatisticalComparator._bootstrap_estimator_ci(c_lats, np.median),
            p95_ci_95=StatisticalComparator._bootstrap_estimator_ci(c_lats, lambda x: np.percentile(x, 95))
        )

        b_hardware = baseline_res.hardware_telemetry or HardwareTelemetry(
            cpu_peak_percent=0.0, rss_peak_mb=0.0, rss_avg_mb=0.0, sampling_interval_ms=0
        )
        c_hardware = challenger_res.hardware_telemetry or HardwareTelemetry(
            cpu_peak_percent=0.0, rss_peak_mb=0.0, rss_avg_mb=0.0, sampling_interval_ms=0
        )

        report = BenchmarkRunReport(
            metadata=BenchmarkMetadata(
                benchmark_version="v1.1", 
                run_timestamp=time.time(), 
                git_commit_sha=self.git_commit_sha,
                chunking_strategy="equalized_standard" 
            ),
            dataset=dataset.manifest,
            quality_policy=quality_policy,
            baseline_metrics=MetricAggregator.aggregate(
                descriptor=baseline_desc, 
                records=baseline_res.raw_records, 
                document_completion_seconds=baseline_makespan, 
                total_documents=len(dataset.manifest.documents), 
                quality_assessment=baseline_quality,           
                benchmark_mode=b_mode,                       
                quota_snapshot=b_quota,                      
                hardware_telemetry=b_hardware,
                latency_moments=b_moments
            ),
            challenger_metrics=MetricAggregator.aggregate(
                descriptor=challenger_desc, 
                records=challenger_res.raw_records, 
                document_completion_seconds=challenger_makespan, 
                total_documents=len(dataset.manifest.documents), 
                quality_assessment=challenger_quality,         
                benchmark_mode=c_mode,                       
                quota_snapshot=c_quota,                      
                hardware_telemetry=c_hardware,
                latency_moments=c_moments
            ),
            raw_baseline_records=baseline_res.raw_records,
            raw_challenger_records=challenger_res.raw_records
        )

        if self._persistence:
            self._persistence.save_final_report(report)

        return report