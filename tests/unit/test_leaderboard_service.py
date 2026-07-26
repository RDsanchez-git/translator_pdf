"""
tests/unit/test_leaderboard_service.py

Suite de pruebas unitarias para LeaderboardService adaptada a los modelos reales (Hito 2 - ADR F17.5).
"""

from unittest.mock import patch
import pytest

from core.benchmark.models import (
    BenchmarkDataset,
    BenchmarkMetadata,
    BenchmarkMode,
    BenchmarkRunReport,
    ChunkBenchmarkRecord,
    DocumentComplexity,
    HardwareTelemetry,
    LatencyMetrics,
    ProviderBenchmarkMetrics,
    ProviderDescriptor,
    QualityPolicy,
    QuotaSnapshot,
    StatisticalMoments,
    StructuralQualityMetrics,
    TranslatedArtifact,
)
from core.benchmark.reporter import (
    LeaderboardError,
    LeaderboardService,
    MissingProviderIdentityError,
    MissingReportMetricsError,
    ScientificSignificanceReport,
    StatisticalComparator,
)
from core.benchmark.score_policy import (
    MetricDirection,
    MetricName,
    MetricRule,
    ScorePolicy,
)

import json
from pathlib import Path
from unittest.mock import MagicMock, call
from core.benchmark.persistence import BenchmarkPersistenceGateway


def make_provider_metrics(
    provider_name: str,
    reliability_score: float = 1.0,
    latex_syntax_score: float = 1.0,
    total_chunks: int = 2,
) -> ProviderBenchmarkMetrics:
    successful = int(total_chunks * reliability_score)
    return ProviderBenchmarkMetrics(
        descriptor=ProviderDescriptor(provider=provider_name),
        benchmark_mode=BenchmarkMode.CAPABILITY,
        quota_snapshot=QuotaSnapshot(rpm_limit=100, tpm_limit=100000, concurrency=5),
        total_chunks=total_chunks,
        successful_chunks=successful,
        total_input_tokens=1000,
        total_output_tokens=1000,
        cumulative_chunk_latency_seconds=10.0,
        document_completion_seconds=10.0,
        latency=LatencyMetrics(p50_ms=100.0, p95_ms=200.0, p99_ms=300.0, max_ms=400.0),
        latency_moments=StatisticalMoments(median_ci_95=(90.0, 110.0), p95_ci_95=(180.0, 220.0)),
        total_cost_usd=0.01,
        total_documents=1,
        p95_cost_per_chunk_usd=0.005,
        p99_cost_per_chunk_usd=0.005,
        quality=StructuralQualityMetrics(
            operational_reliability=reliability_score,
            token_structure_proxy=1.0,
            latex_syntax_score=latex_syntax_score,
            markdown_syntax_score=1.0,
        ),
        context_overflow_ratio=0.0,
        provider_switch_ratio=0.0,
        average_compression_ratio=1.0,
        p95_compression_ratio=1.0,
        p99_compression_ratio=1.0,
        max_compression_ratio=1.0,
        total_quota_wait_seconds=0.0,
        average_quota_attempts=1.0,
        hardware_telemetry=HardwareTelemetry(
            cpu_peak_percent=10.0, rss_peak_mb=100.0, rss_avg_mb=50.0, sampling_interval_ms=1000
        ),
        p50_tps=100.0,
        p95_tps=100.0,
        p99_tps=100.0,
    )


def make_chunk_record(
    chunk_id: str,
    success: bool = True,
    is_latex_valid: bool = True,
) -> ChunkBenchmarkRecord:
    artifact = TranslatedArtifact(
        chunk_id=chunk_id,
        translated_text="sample text",
        text_sha256="dummy_sha256",
        is_latex_valid=is_latex_valid,
        is_markdown_valid=True,
    )
    return ChunkBenchmarkRecord(
        chunk_id=chunk_id,
        chunk_index=0,
        complexity=DocumentComplexity.STANDARD_PROSE,
        latency_ms=100.0,
        input_tokens=100,
        output_tokens=100,
        cost_usd=0.001,
        success=success,
        failure_reason=None,
        is_local_rejection=False,
        quota_wait_seconds=0.0,
        quota_attempts=1,
        did_overflow=False,
        did_fallback=False,
        compression_ratio_used=1.0,
        execution_stage="translation",
        billing_model_used="standard",
        tps_instantaneous=50.0,
        artifact_metadata=artifact,
    )


def make_benchmark_report(
    baseline_provider: str,
    challenger_provider: str,
    baseline_reliability: float = 1.0,
    challenger_reliability: float = 0.5,
    baseline_records: list[ChunkBenchmarkRecord] | None = None,
    challenger_records: list[ChunkBenchmarkRecord] | None = None,
    total_chunks: int = 2,
) -> BenchmarkRunReport:
    b_metrics = make_provider_metrics(
        baseline_provider,
        reliability_score=baseline_reliability,
        total_chunks=total_chunks,
    )
    c_metrics = make_provider_metrics(
        challenger_provider,
        reliability_score=challenger_reliability,
        total_chunks=total_chunks,
    )
    b_records = baseline_records if baseline_records is not None else [
        make_chunk_record(f"b_chunk_{i}", success=(i < int(total_chunks * baseline_reliability)))
        for i in range(total_chunks)
    ]
    c_records = challenger_records if challenger_records is not None else [
        make_chunk_record(f"c_chunk_{i}", success=(i < int(total_chunks * challenger_reliability)))
        for i in range(total_chunks)
    ]

    return BenchmarkRunReport(
        metadata=BenchmarkMetadata(
            benchmark_version="1.0.0",
            run_timestamp=1234567890.0,
            git_commit_sha="abc1234",
            chunking_strategy="semantic",
        ),
        dataset=BenchmarkDataset(
            dataset_id="test_ds",
            dataset_sha256="hash123",
            documents=[],
        ),
        quality_policy=QualityPolicy(
            structural_weight=0.5,
            semantic_weight=0.5,
        ),
        baseline_metrics=b_metrics,
        challenger_metrics=c_metrics,
        raw_baseline_records=b_records,
        raw_challenger_records=c_records,
    )


def build_test_policy() -> ScorePolicy:
    return ScorePolicy(
        rules={
            MetricName("reliability_score"): MetricRule(weight=0.6, direction=MetricDirection.HIGHER_IS_BETTER),
            MetricName("latex_syntax_score"): MetricRule(weight=0.4, direction=MetricDirection.HIGHER_IS_BETTER),
        }
    )


def test_leaderboard_tie_break_is_deterministic() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    report = make_benchmark_report(
        baseline_provider="ZetaProvider",
        challenger_provider="AlphaProvider",
        baseline_reliability=0.5,
        challenger_reliability=0.5,
    )

    result = service.generate_leaderboard([report], policy)

    assert result.entries[0].provider_name == "AlphaProvider"
    assert result.entries[1].provider_name == "ZetaProvider"
    assert result.entries[0].rank == 1
    assert result.entries[1].rank == 2


def test_asymmetric_insufficient_observations_yields_no_significance_report() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    b_recs = [make_chunk_record("b1"), make_chunk_record("b2")]
    c_recs = [make_chunk_record("c1")]  # n = 1

    report = make_benchmark_report(
        baseline_provider="ProviderA",
        challenger_provider="ProviderB",
        baseline_records=b_recs,
        challenger_records=c_recs,
    )

    result = service.generate_leaderboard([report], policy)
    assert result.significance_report is None


def test_defensive_copy_protects_leaderboard_entry_metrics_from_external_mutation() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    report = make_benchmark_report("ProviderA", "ProviderB")
    result = service.generate_leaderboard([report], policy)

    entry_metrics = result.entries[0].metrics

    with pytest.raises(TypeError):
        entry_metrics[MetricName("reliability_score")] = 0.5  # type: ignore


def test_leaderboard_delegates_to_statistical_comparator_correctly() -> None:
    policy = build_test_policy()

    mock_sig_report = ScientificSignificanceReport(
        metric_name="composite_score",
        mw_u_statistic=10.0,
        mw_p_value=0.01,
        ks_d_statistic=0.5,
        ks_p_value=0.01,
        is_statistically_significant=True,
        cliffs_delta_effect_size=0.8,
        effect_size_magnitude="large",
        baseline_median_ci95=(0.8, 0.9),
        challenger_median_ci95=(0.4, 0.6),
        baseline_p95_ci95=(0.85, 0.95),
        challenger_p95_ci95=(0.45, 0.65),
    )

    with patch.object(StatisticalComparator, "compare_series", return_value=mock_sig_report) as mock_compare:
        service = LeaderboardService()

        b_recs = [make_chunk_record("b1", True), make_chunk_record("b2", True)]
        c_recs = [make_chunk_record("c1", False), make_chunk_record("c2", False)]

        report = make_benchmark_report(
            baseline_provider="ProviderA",
            challenger_provider="ProviderB",
            baseline_reliability=1.0,
            challenger_reliability=0.0,
            baseline_records=b_recs,
            challenger_records=c_recs,
        )

        result = service.generate_leaderboard([report], policy)

        mock_compare.assert_called_once_with(
            metric_name="composite_score",
            base_vals=[1.0, 1.0],
            chall_vals=[0.4, 0.4],
        )
        assert result.significance_report == mock_sig_report


def test_missing_provider_identity_raises_fail_fast() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    report = make_benchmark_report("", "ValidChallenger")

    with pytest.raises(MissingProviderIdentityError):
        service.generate_leaderboard([report], policy)


def test_missing_metrics_raises_fail_fast() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    report = make_benchmark_report("ValidProvider", "Challenger", total_chunks=0)

    with pytest.raises(MissingReportMetricsError):
        service.generate_leaderboard([report], policy)


def test_empty_reports_raises_leaderboard_error() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    with pytest.raises(LeaderboardError):
        service.generate_leaderboard([], policy)

# ===========================================================================
# PRUEBAS UNITARIAS HITO 3: PERSISTENCIA Y FORMATEO DE ARTEFACTOS
# ===========================================================================

def test_format_json_structural_contract_and_key_sorting() -> None:
    policy = build_test_policy()
    service = LeaderboardService()
    report = make_benchmark_report("ProviderA", "ProviderB")

    result = service.generate_leaderboard([report], policy)
    json_str = service.format_json(result)

    # 1. Determinismo en serialización interna
    assert json_str == service.format_json(result)

    # 2. Validación estructural del contrato JSON
    data = json.loads(json_str)
    assert sorted(list(data.keys())) == ["entries", "policy_rules", "significance_report"]
    assert len(data["entries"]) == 2
    assert data["entries"][0]["rank"] == 1


def test_format_json_reproducibility_across_independent_runs() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    report_a = make_benchmark_report("ProviderA", "ProviderB")
    report_b = make_benchmark_report("ProviderA", "ProviderB")

    res_a = service.generate_leaderboard([report_a], policy)
    res_b = service.generate_leaderboard([report_b], policy)

    # Verificación de reproducibilidad de salida ante entradas equivalentes
    assert service.format_json(res_a) == service.format_json(res_b)


def test_format_markdown_translates_semantics_and_uses_flags() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    b_recs = [make_chunk_record("b1", True), make_chunk_record("b2", True)]
    c_recs = [make_chunk_record("c1", False), make_chunk_record("c2", False)]
    report = make_benchmark_report(
        "ProviderA", "ProviderB", baseline_records=b_recs, challenger_records=c_recs
    )

    result = service.generate_leaderboard([report], policy)
    md_str = service.format_markdown(result)

    assert "Rank #1 (Winner) Median 95% CI" in md_str
    assert "Rank #2 (Runner-up) Median 95% CI" in md_str
    assert "Baseline Median" not in md_str
    assert "Challenger Median" not in md_str
    assert "🟢 SIGNIFICANT" in md_str or "🔴 NOT SIGNIFICANT" in md_str


def test_format_markdown_handles_missing_significance_report() -> None:
    policy = build_test_policy()
    service = LeaderboardService()

    # n=1 por grupo -> fuerzas result.significance_report = None
    b_recs = [make_chunk_record("b1", True)]
    c_recs = [make_chunk_record("c1", False)]
    report = make_benchmark_report(
        "ProviderA", "ProviderB", baseline_records=b_recs, challenger_records=c_recs
    )

    result = service.generate_leaderboard([report], policy)
    assert result.significance_report is None

    md_str = service.format_markdown(result)
    assert "🔴 N/A" in md_str
    assert "Insufficient observations" in md_str


def test_persist_leaderboard_delegates_strictly_to_gateway() -> None:
    policy = build_test_policy()
    service = LeaderboardService()
    report = make_benchmark_report("ProviderA", "ProviderB")

    result = service.generate_leaderboard([report], policy)

    mock_gateway = MagicMock(spec=BenchmarkPersistenceGateway)
    mock_gateway.save_artifact.side_effect = [
        Path("/fake/leaderboard.json"),
        Path("/fake/leaderboard.md"),
    ]

    json_path, md_path = service.persist_leaderboard(result, mock_gateway)

    # Verificación contractual de delegación mediante Spy Test
    assert mock_gateway.save_artifact.call_count == 2

    expected_calls = [
        call("leaderboard.json", service.format_json(result)),
        call("leaderboard.md", service.format_markdown(result)),
    ]
    mock_gateway.save_artifact.assert_has_calls(expected_calls, any_order=False)