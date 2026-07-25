"""
tests/integration/test_benchmark_orchestration_integration.py

Prueba de Integración y Validación de Arquitectura (Hito 5 - Fase 17.4).
Demuestra el cumplimiento del Principio Open/Closed (OCP) y la retrocompatibilidad
completa del SequentialBenchmarkOrchestrator para parsers y LLMs.
"""

import asyncio
from typing import Any, List, Optional
from unittest.mock import MagicMock

import pytest

from core.benchmark.models import (
    BenchmarkDataset,
    BenchmarkDocument,
    BenchmarkMode,
    DocumentComplexity,
    HardwareTelemetry,
    MetricResult,
    PreparedBenchmarkDataset,
    ProviderDescriptor,
    QualityPolicy,
    QuotaSnapshot,
    RunnerExecutionResult,
)
from core.benchmark.orchestrator import SequentialBenchmarkOrchestrator
from core.benchmark.ports import (
    BenchmarkArtifact,
    BenchmarkCandidateProvider,
    BenchmarkEvaluatorProtocol,
    BenchmarkRunnerProtocol,
    GroundTruthProviderProtocol,
)
from core.benchmark.types import ProviderKind


# =====================================================================
# FIXTURES Y MOCKS DE INTEGRACIÓN (Conformes a Protocolos)
# =====================================================================

class DummyArtifact(BenchmarkArtifact):
    """Artefacto neutro de prueba."""
    def __init__(self, content: str) -> None:
        self.content = content


class MockCandidateProvider(BenchmarkCandidateProvider):
    """Proveedor genérico para simular candidatos de extracción."""
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def provider_name(self) -> str:
        return self._name

    def provide(self, document_id: str) -> Optional[BenchmarkArtifact]:
        return DummyArtifact(f"AST_{self._name}_{document_id}")


class MockGroundTruthProvider(GroundTruthProviderProtocol):
    """Proveedor de Ground Truth de referencia."""
    def get_ground_truth(self, document_id: str) -> Any:
        return f"GT_{document_id}"


class MockEvaluator(BenchmarkEvaluatorProtocol):
    """Evaluador neutro de prueba."""

    def __init__(self, name: str, mock_score: float) -> None:
        self._name = name
        self._score = mock_score

    @property
    def metric_name(self) -> str:
        return self._name

    def evaluate(self, candidate: Any, ground_truth: Any) -> MetricResult:
        return MetricResult(
            metric_name=self._name,
            value=self._score,
            details={"candidate": str(candidate), "gt": str(ground_truth)},
        )


class MockLLMRunner(BenchmarkRunnerProtocol):
    """Runner A/B de prueba para benchmark de LLM."""
    def __init__(self, provider_id: str) -> None:
        self.provider_id = provider_id
        self.mode = BenchmarkMode.EQUALIZED
        self.quota_snapshot = QuotaSnapshot(rpm_limit=100, tpm_limit=1000, concurrency=1)

    async def warmup(self) -> None:
        pass

    async def teardown(self) -> None:
        pass

    async def execute_dataset(
        self, dataset: PreparedBenchmarkDataset, force_cache_bypass: bool = True
    ) -> RunnerExecutionResult:
        return RunnerExecutionResult(
            provider_id=self.provider_id,
            raw_records=[],
            document_completion_seconds=0.15,
            hardware_telemetry=HardwareTelemetry(
                cpu_peak_percent=12.5,
                rss_peak_mb=256.0,
                rss_avg_mb=128.0,
                sampling_interval_ms=100
            )
        )


# =====================================================================
# SUITE DE PRUEBAS
# =====================================================================

def test_orchestrator_parser_evaluation_ocp() -> None:
    """
    Verifica OCP: Evalúa candidatos de PyMuPDF, Docling y un NUEVO proveedor
    sin modificar una sola línea de SequentialBenchmarkOrchestrator.
    """
    orchestrator = SequentialBenchmarkOrchestrator()
    gt_provider = MockGroundTruthProvider()
    evaluators: List[BenchmarkEvaluatorProtocol] = [
        MockEvaluator("structural_score", 0.95),
        MockEvaluator("recall_score", 0.88),
    ]

    # 1. Proveedores Estándar (PyMuPDF vs Docling)
    pymupdf_provider = MockCandidateProvider("pymupdf")
    docling_provider = MockCandidateProvider("docling")

    _, artifact_py, metrics_py = orchestrator.evaluate_candidate(
        document_id="doc_001",
        provider=pymupdf_provider,
        ground_truth_provider=gt_provider,
        evaluators=evaluators,
    )

    _, artifact_doc, metrics_doc = orchestrator.evaluate_candidate(
        document_id="doc_001",
        provider=docling_provider,
        ground_truth_provider=gt_provider,
        evaluators=evaluators,
    )

    # Verificación por contrato e interfaz (sin depender del contenido concreto)
    assert artifact_py is not None
    assert isinstance(artifact_py, BenchmarkArtifact)
    assert len(metrics_py) == 2
    assert metrics_py[0].metric_name == "structural_score"
    assert metrics_py[0].value == 0.95

    assert artifact_doc is not None
    assert isinstance(artifact_doc, BenchmarkArtifact)

    # 2. Verificación Abierta/Cerrada (OCP): Nuevo proveedor sin cambios en el orquestador
    class CustomMarkerProvider(MockCandidateProvider):
        pass

    marker_provider = CustomMarkerProvider("marker_v2")
    _, artifact_mk, metrics_mk = orchestrator.evaluate_candidate(
        document_id="doc_001",
        provider=marker_provider,
        ground_truth_provider=gt_provider,
        evaluators=evaluators,
    )

    assert artifact_mk is not None
    assert isinstance(artifact_mk, BenchmarkArtifact)
    assert len(metrics_mk) == 2


def test_orchestrator_llm_run_experiment_smoke() -> None:
    """
    Prueba de Humo: Garantiza la retrocompatibilidad completa del método `run_experiment`
    para ejecuciones A/B de LLMs sin alterar el pipeline preexistente.
    """
    baseline_runner = MockLLMRunner("gemini-flash")
    challenger_runner = MockLLMRunner("groq-llama3")
    mock_persistence = MagicMock()

    orchestrator = SequentialBenchmarkOrchestrator(
        baseline_runner=baseline_runner,
        challenger_runner=challenger_runner,
        persistence=mock_persistence,
        cooldown_seconds=0.01,
        git_commit_sha="test_commit_sha"
    )

    doc = BenchmarkDocument(
        id="doc_test",
        file_path="tests/fixtures/dummy.pdf",
        file_sha256="dummy_sha",
        complexity=DocumentComplexity.STANDARD_PROSE,
        expected_pages=1,
        input_tokens_actual=100,
        expected_chunks=1
    )
    dataset = PreparedBenchmarkDataset(
        manifest=BenchmarkDataset(dataset_id="ds_test", dataset_sha256="sha", documents=[doc]),
        prepared_units=[],
        unit_complexity_map={}
    )

    base_desc = ProviderDescriptor(provider="gemini", model="flash", provider_type=ProviderKind.LLM_INFERENCE)
    chal_desc = ProviderDescriptor(provider="groq", model="llama3", provider_type=ProviderKind.LLM_INFERENCE)
    policy = QualityPolicy(structural_weight=0.5, semantic_weight=0.5)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("core.benchmark.orchestrator.DatasetIntegrityValidator.verify", lambda x: True)
        
        report = asyncio.run(
            orchestrator.run_experiment(
                dataset=dataset,
                baseline_desc=base_desc,
                challenger_desc=chal_desc,
                quality_policy=policy
            )
        )

    assert report is not None
    assert report.metadata.git_commit_sha == "test_commit_sha"
    assert report.baseline_metrics.descriptor.provider == "gemini"
    assert report.challenger_metrics.descriptor.provider == "groq"
    
    # Aserción estricta sobre la llamada de persistencia
    mock_persistence.save_final_report.assert_called_once()