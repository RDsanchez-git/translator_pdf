import os
import time
import asyncio
import hashlib
import logging
import numpy as np  # SOTA FIX: Requerido para cálculo de percentiles en colas pesadas
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
    StatisticalMoments  # SOTA FIX: Importación requerida
)
from core.benchmark.ports import BenchmarkRunnerProtocol
from core.benchmark.persistence import BenchmarkPersistenceGateway
from core.benchmark.quality import StructuralQualityEvaluator  # SOTA FIX: Importación de taxonomía estructural
from core.benchmark.reporter import StatisticalComparator      # SOTA FIX: Motor de remuestreo Bootstrap

logger = logging.getLogger(__name__)

class DatasetIntegrityValidator:
    """SOTA: Validador de consistencia genética del set de datos."""
    
    @staticmethod
    def verify(document: BenchmarkDocument) -> bool:
        if not os.path.exists(document.file_path):
            logger.error(f"Falla de Fixture: Archivo ausente en {document.file_path}")
            return False
            
        sha256 = hashlib.sha256()
        with open(document.file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
                
        computed_hash = sha256.hexdigest()
        if computed_hash != document.file_sha256:
            logger.error(f"Corrupción detectada en {document.id}. Esperado: {document.file_sha256}, Obtenido: {computed_hash}")
            return False
            
        return True

class SequentialBenchmarkOrchestrator:
    """SOTA: Driver de aislamiento físico. Pura orquestación, cero persistencia."""
    
    def __init__(
        self, 
        baseline_runner: BenchmarkRunnerProtocol, 
        challenger_runner: BenchmarkRunnerProtocol,
        persistence: BenchmarkPersistenceGateway,
        cooldown_seconds: float = 10.0,
        git_commit_sha: str = "unknown"
    ):
        self._baseline = baseline_runner
        self._challenger = challenger_runner
        self._persistence = persistence
        self.cooldown_seconds = cooldown_seconds
        self.git_commit_sha = git_commit_sha

    async def run_experiment(
        self, 
        dataset: PreparedBenchmarkDataset, 
        baseline_desc: ProviderDescriptor,
        challenger_desc: ProviderDescriptor,
        quality_policy: QualityPolicy 
    ) -> BenchmarkRunReport:
        
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
        
        self._persistence.save_raw_records_checkpoint(dataset.manifest.dataset_id, baseline_name, baseline_res.raw_records)

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
        
        self._persistence.save_raw_records_checkpoint(dataset.manifest.dataset_id, challenger_name, challenger_res.raw_records)

        # 5. Agregación y Ensamblaje SOTA
        # Evaluador estructural con parsers formales acoplado a la respuesta inmutable
        baseline_quality = StructuralQualityEvaluator.evaluate(dataset, baseline_res)
        challenger_quality = StructuralQualityEvaluator.evaluate(dataset, challenger_res)
        
        b_mode = getattr(self._baseline, 'mode', BenchmarkMode.EQUALIZED)
        b_quota = getattr(self._baseline, 'quota_snapshot', QuotaSnapshot(0, 0, 0))
        c_mode = getattr(self._challenger, 'mode', BenchmarkMode.EQUALIZED)
        c_quota = getattr(self._challenger, 'quota_snapshot', QuotaSnapshot(0, 0, 0))

        b_lats = [r.latency_ms for r in baseline_res.raw_records if r.success]
        c_lats = [r.latency_ms for r in challenger_res.raw_records if r.success]

        # SOTA FIX: Uso del motor Bootstrap centralizado para cálculo de IC robustos
        b_moments = StatisticalMoments(
            median_ci_95=StatisticalComparator._bootstrap_estimator_ci(b_lats, np.median),
            p95_ci_95=StatisticalComparator._bootstrap_estimator_ci(b_lats, lambda x: np.percentile(x, 95))
        )
        c_moments = StatisticalMoments(
            median_ci_95=StatisticalComparator._bootstrap_estimator_ci(c_lats, np.median),
            p95_ci_95=StatisticalComparator._bootstrap_estimator_ci(c_lats, lambda x: np.percentile(x, 95))
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
                hardware_telemetry=baseline_res.hardware_telemetry,
                latency_moments=b_moments  # SOTA FIX: Inyección del DTO de colas
            ),
            challenger_metrics=MetricAggregator.aggregate(
                descriptor=challenger_desc, 
                records=challenger_res.raw_records, 
                document_completion_seconds=challenger_makespan, 
                total_documents=len(dataset.manifest.documents), 
                quality_assessment=challenger_quality,         
                benchmark_mode=c_mode,                       
                quota_snapshot=c_quota,                      
                hardware_telemetry=challenger_res.hardware_telemetry,
                latency_moments=c_moments  # SOTA FIX: Inyección del DTO de colas
            ),
            raw_baseline_records=baseline_res.raw_records,
            raw_challenger_records=challenger_res.raw_records
        )

        self._persistence.save_final_report(report)
        return report