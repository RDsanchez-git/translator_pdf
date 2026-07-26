"""
core/benchmark/reporter.py

Servicios de reportería, comparación estadística no paramétrica y generación
de leaderboards de evaluación para benchmarking.
"""

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Sequence, Tuple, cast

import numpy as np
from scipy import stats

from core.benchmark.models import (
    BenchmarkRunReport,
    ChunkBenchmarkRecord,
    DocumentComplexity,
    ProviderBenchmarkMetrics,
)
from core.benchmark.score_policy import MetricName, ScorePolicy

import json
from pathlib import Path
from core.benchmark.persistence import BenchmarkPersistenceGateway


# ===========================================================================
# 1. MOTOR ESTADÍSTICO NO PARAMÉTRICO SOTA (EXISTENTE - INMUTABLE)
# ===========================================================================

@dataclass(frozen=True, slots=True)
class ScientificSignificanceReport:
    """Reporte de significancia estadística entre dos series de ejecuciones (12 campos exactos)."""
    metric_name: str
    mw_u_statistic: float
    mw_p_value: float
    ks_d_statistic: float
    ks_p_value: float
    is_statistically_significant: bool
    cliffs_delta_effect_size: float
    effect_size_magnitude: str
    baseline_median_ci95: Tuple[float, float]
    challenger_median_ci95: Tuple[float, float]
    baseline_p95_ci95: Tuple[float, float]
    challenger_p95_ci95: Tuple[float, float]


class StatisticalComparator:
    """SOTA: Motor matemático no paramétrico con corrección FWER."""

    ALPHA = 0.05
    BOOTSTRAP_RESETS = 1000

    @staticmethod
    def _interpret_cliffs_delta(d: float) -> str:
        abs_d = abs(d)
        if abs_d < 0.147:
            return "negligible"
        if abs_d < 0.330:
            return "small"
        if abs_d < 0.474:
            return "medium"
        return "large"

    @staticmethod
    def _bootstrap_estimator_ci(data: List[float], estimator_func: Any) -> Tuple[float, float]:
        if not data:
            return (0.0, 0.0)
        arr = np.array(data)
        resamples = [estimator_func(np.random.choice(arr, size=len(arr), replace=True)) for _ in range(StatisticalComparator.BOOTSTRAP_RESETS)]
        return (round(float(np.percentile(resamples, 2.5)), 2), round(float(np.percentile(resamples, 97.5)), 2))

    @classmethod
    def compare_series(
        cls, metric_name: str, base_vals: List[float], chall_vals: List[float]
    ) -> ScientificSignificanceReport:

        if not base_vals or not chall_vals:
            empty_ci = (0.0, 0.0)
            return ScientificSignificanceReport(metric_name, 0.0, 1.0, 0.0, 1.0, False, 0.0, "negligible", empty_ci, empty_ci, empty_ci, empty_ci)

        mw_res = cast(Any, stats.mannwhitneyu(base_vals, chall_vals, alternative='two-sided'))
        u_stat = float(mw_res.statistic if hasattr(mw_res, 'statistic') else mw_res[0])
        mw_p = float(mw_res.pvalue if hasattr(mw_res, 'pvalue') else mw_res[1])

        ks_res = cast(Any, stats.ks_2samp(base_vals, chall_vals))
        d_stat = float(ks_res.statistic if hasattr(ks_res, 'statistic') else ks_res[0])
        ks_p = float(ks_res.pvalue if hasattr(ks_res, 'pvalue') else ks_res[1])

        n1, n2 = len(base_vals), len(chall_vals)
        cliffs_d = (2 * u_stat) / (n1 * n2) - 1

        is_significant = (mw_p < cls.ALPHA) or (ks_p < cls.ALPHA)

        b_median_ci = cls._bootstrap_estimator_ci(base_vals, np.median)
        c_median_ci = cls._bootstrap_estimator_ci(chall_vals, np.median)

        def _p95_estimator(x: np.ndarray) -> float:
            return float(np.percentile(x, 95))

        b_p95_ci = cls._bootstrap_estimator_ci(base_vals, _p95_estimator)
        c_p95_ci = cls._bootstrap_estimator_ci(chall_vals, _p95_estimator)

        return ScientificSignificanceReport(
            metric_name=metric_name,
            mw_u_statistic=u_stat,
            mw_p_value=mw_p,
            ks_d_statistic=d_stat,
            ks_p_value=ks_p,
            is_statistically_significant=is_significant,
            cliffs_delta_effect_size=round(float(cliffs_d), 4),
            effect_size_magnitude=cls._interpret_cliffs_delta(cliffs_d),
            baseline_median_ci95=b_median_ci,
            challenger_median_ci95=c_median_ci,
            baseline_p95_ci95=b_p95_ci,
            challenger_p95_ci95=c_p95_ci
        )

    @classmethod
    def _apply_holm_bonferroni(
        cls,
        reports: Dict[str, ScientificSignificanceReport]
    ) -> Dict[str, ScientificSignificanceReport]:
        """SOTA: Mitigación de Falsos Positivos en testing múltiple."""
        items = list(reports.items())
        items.sort(key=lambda x: min(x[1].mw_p_value, x[1].ks_p_value))

        m = len(items)
        adjusted_reports = {}

        for k, (key, report) in enumerate(items):
            adjusted_alpha = cls.ALPHA / (m - k)
            lowest_p = min(report.mw_p_value, report.ks_p_value)
            is_sig = lowest_p < adjusted_alpha

            adjusted_reports[key] = replace(report, is_statistically_significant=is_sig)

            if not is_sig:
                for remaining_key, remaining_report in items[k+1:]:
                    adjusted_reports[remaining_key] = replace(remaining_report, is_statistically_significant=False)
                break

        return adjusted_reports

    @classmethod
    def run_stratified_analysis(cls, report: BenchmarkRunReport) -> Dict[str, ScientificSignificanceReport]:
        raw_analysis = {}

        for complexity in DocumentComplexity:
            b_lat = [r.latency_ms for r in report.raw_baseline_records if r.complexity == complexity and r.success]
            c_lat = [r.latency_ms for r in report.raw_challenger_records if r.complexity == complexity and r.success]

            if b_lat and c_lat:
                raw_analysis[complexity.value] = cls.compare_series(f"latency_{complexity.value}", b_lat, c_lat)

        b_all = [r.latency_ms for r in report.raw_baseline_records if r.success]
        c_all = [r.latency_ms for r in report.raw_challenger_records if r.success]
        raw_analysis["global"] = cls.compare_series("latency_global", b_all, c_all)

        return cls._apply_holm_bonferroni(raw_analysis)


# ===========================================================================
# 2. SERVICIO DE LEADERBOARD (HITO 2 - ADR F17.5)
# ===========================================================================

class LeaderboardError(ValueError):
    """Excepción base para errores en la generación de leaderboards."""
    pass


class MissingProviderIdentityError(LeaderboardError):
    """Falla Fail-Fast cuando un ProviderBenchmarkMetrics no posee identidad de proveedor validada."""
    pass


class MissingReportMetricsError(LeaderboardError):
    """Falla Fail-Fast cuando un ProviderBenchmarkMetrics no posee métricas evaluables."""
    pass


@dataclass(frozen=True, slots=True)
class LeaderboardEntry:
    """Entrada individual inmutable en el ranking del leaderboard."""
    rank: int
    provider_name: str
    composite_score: float
    metrics: Mapping[MetricName, float]


@dataclass(frozen=True, slots=True)
class LeaderboardResult:
    """Resultado completo del leaderboard con ranking y significancia estadística."""
    entries: tuple[LeaderboardEntry, ...]
    policy: ScorePolicy
    significance_report: ScientificSignificanceReport | None


class LeaderboardService:
    """
    Servicio puro de segundo orden encargado de calcular el ranking compuesto
    y delegar la evaluación estadística al @classmethod compare_series de StatisticalComparator.
    """

    def generate_leaderboard(
        self,
        reports: Sequence[BenchmarkRunReport],
        policy: ScorePolicy,
    ) -> LeaderboardResult:
        """
        Genera el leaderboard ordenado por composite_score e invoca a StatisticalComparator.compare_series
        entre el 1.º y 2.º lugar únicamente si ambos proveedores cumplen la política conservadora de n >= 2.
        """
        if not reports:
            raise LeaderboardError("La secuencia de reportes para el leaderboard no puede estar vacía.")

        unranked_entries: list[tuple[float, str, Mapping[MetricName, float], list[float]]] = []
        seen_providers: set[str] = set()

        for report in reports:
            provider_pairs = [
                (report.baseline_metrics, report.raw_baseline_records),
                (report.challenger_metrics, report.raw_challenger_records),
            ]

            for p_metrics, raw_records in provider_pairs:
                provider_name = self._extract_provider_name_strict(p_metrics)
                if provider_name in seen_providers:
                    continue
                seen_providers.add(provider_name)

                metrics_map = self._extract_metrics_map_strict(p_metrics, policy)
                composite_score = policy.compute_composite_score(metrics_map)
                series = self._extract_observation_series_strict(raw_records, policy)

                unranked_entries.append((composite_score, provider_name, metrics_map, series))

        # Ordenamiento determinista: score compuesto descendente, desempate alfabético por nombre
        unranked_entries.sort(key=lambda x: (-x[0], x[1]))

        ranked_entries: list[LeaderboardEntry] = []
        for rank, (score, name, metrics, _) in enumerate(unranked_entries, start=1):
            ranked_entries.append(
                LeaderboardEntry(
                    rank=rank,
                    provider_name=name,
                    composite_score=score,
                    metrics=MappingProxyType(dict(metrics)),
                )
            )

        significance_report: ScientificSignificanceReport | None = None
        if len(unranked_entries) >= 2:
            winner_series = unranked_entries[0][3]
            runner_up_series = unranked_entries[1][3]

            # Invariante de Política Conservadora: Se exige n >= 2 observaciones por grupo
            if len(winner_series) >= 2 and len(runner_up_series) >= 2:
                significance_report = StatisticalComparator.compare_series(
                    metric_name="composite_score",
                    base_vals=winner_series,
                    chall_vals=runner_up_series,
                )

        return LeaderboardResult(
            entries=tuple(ranked_entries),
            policy=policy,
            significance_report=significance_report,
        )

    @staticmethod
    def _extract_provider_name_strict(p_metrics: ProviderBenchmarkMetrics) -> str:
        if not p_metrics or not p_metrics.descriptor or not p_metrics.descriptor.provider:
            raise MissingProviderIdentityError(
                "Falla Fail-Fast: El reporte no contiene una identidad de proveedor válida en 'descriptor.provider'."
            )
        desc = p_metrics.descriptor
        if desc.model:
            return f"{desc.provider}:{desc.model}"
        return str(desc.provider)

    @staticmethod
    def _extract_metrics_map_strict(
        p_metrics: ProviderBenchmarkMetrics,
        policy: ScorePolicy,
    ) -> Mapping[MetricName, float]:
        if p_metrics.total_chunks == 0 and p_metrics.successful_chunks == 0:
            raise MissingReportMetricsError(
                f"Falla Fail-Fast: Las métricas para el proveedor '{p_metrics.descriptor.provider}' están vacías o no procesaron chunks."
            )

        all_metrics: dict[MetricName, float] = {
            MetricName("reliability_score"): float(p_metrics.reliability_score),
            MetricName("input_tps"): float(p_metrics.input_tps),
            MetricName("output_tps"): float(p_metrics.output_tps),
            MetricName("total_tps"): float(p_metrics.total_tps),
            MetricName("cost_per_1m_tokens_usd"): float(p_metrics.cost_per_1m_tokens_usd),
            MetricName("cost_per_1k_tokens_usd"): float(p_metrics.cost_per_1k_tokens_usd),
            MetricName("operational_reliability"): float(p_metrics.quality.operational_reliability),
            MetricName("token_structure_proxy"): float(p_metrics.quality.token_structure_proxy),
            MetricName("latex_syntax_score"): float(p_metrics.quality.latex_syntax_score),
            MetricName("markdown_syntax_score"): float(p_metrics.quality.markdown_syntax_score),
            MetricName("context_overflow_ratio"): float(p_metrics.context_overflow_ratio),
            MetricName("provider_switch_ratio"): float(p_metrics.provider_switch_ratio),
            MetricName("average_compression_ratio"): float(p_metrics.average_compression_ratio),
            MetricName("p50_tps"): float(p_metrics.p50_tps),
            MetricName("p95_tps"): float(p_metrics.p95_tps),
            MetricName("p99_tps"): float(p_metrics.p99_tps),
        }

        filtered: dict[MetricName, float] = {
            k: v for k, v in all_metrics.items() if k in policy.rules
        }

        return filtered

    @staticmethod
    def _extract_observation_series_strict(
        raw_records: Sequence[ChunkBenchmarkRecord],
        policy: ScorePolicy,
    ) -> list[float]:
        if not raw_records:
            return []

        series: list[float] = []
        for record in raw_records:
            artifact = record.artifact_metadata
            latex_val = 1.0 if (artifact and artifact.is_latex_valid) else 0.0
            md_val = 1.0 if (artifact and artifact.is_markdown_valid) else 0.0
            succ_val = 1.0 if record.success else 0.0

            record_metrics: dict[MetricName, float] = {
                MetricName("reliability_score"): succ_val,
                MetricName("operational_reliability"): succ_val,
                MetricName("latex_syntax_score"): latex_val,
                MetricName("markdown_syntax_score"): md_val,
                MetricName("token_structure_proxy"): 1.0 if (record.input_tokens > 0 or record.output_tokens > 0) else 0.0,
                MetricName("input_tps"): float(record.tps_instantaneous),
                MetricName("output_tps"): float(record.tps_instantaneous),
                MetricName("total_tps"): float(record.tps_instantaneous),
                MetricName("cost_per_1m_tokens_usd"): float(record.cost_usd),
                MetricName("cost_per_1k_tokens_usd"): float(record.cost_usd),
                MetricName("context_overflow_ratio"): 1.0 if record.did_overflow else 0.0,
                MetricName("provider_switch_ratio"): 1.0 if record.did_fallback else 0.0,
                MetricName("average_compression_ratio"): float(record.compression_ratio_used),
                MetricName("p50_tps"): float(record.tps_instantaneous),
                MetricName("p95_tps"): float(record.tps_instantaneous),
                MetricName("p99_tps"): float(record.tps_instantaneous),
            }

            filtered_item = {
                k: v for k, v in record_metrics.items() if k in policy.rules
            }

            series.append(policy.compute_composite_score(filtered_item))

        return series

    @staticmethod
    def format_json(result: LeaderboardResult) -> str:
        """Serializa el LeaderboardResult en un JSON estructurado con claves ordenadas determinísticamente."""
        policy_rules = {
            str(k): {
                "weight": rule.weight,
                "direction": rule.direction.value,
            }
            for k, rule in result.policy.rules.items()
        }

        entries_payload = [
            {
                "rank": entry.rank,
                "provider_name": entry.provider_name,
                "composite_score": entry.composite_score,
                "metrics": {str(mk): mv for mk, mv in entry.metrics.items()},
            }
            for entry in result.entries
        ]

        sig = result.significance_report
        sig_payload = None
        if sig is not None:
            sig_payload = {
                "metric_name": sig.metric_name,
                "mw_u_statistic": sig.mw_u_statistic,
                "mw_p_value": sig.mw_p_value,
                "ks_d_statistic": sig.ks_d_statistic,
                "ks_p_value": sig.ks_p_value,
                "is_statistically_significant": sig.is_statistically_significant,
                "cliffs_delta_effect_size": sig.cliffs_delta_effect_size,
                "effect_size_magnitude": sig.effect_size_magnitude,
                "baseline_median_ci95": list(sig.baseline_median_ci95),
                "challenger_median_ci95": list(sig.challenger_median_ci95),
                "baseline_p95_ci95": list(sig.baseline_p95_ci95),
                "challenger_p95_ci95": list(sig.challenger_p95_ci95),
            }

        payload = {
            "policy_rules": policy_rules,
            "entries": entries_payload,
            "significance_report": sig_payload,
        }

        # Ordenamiento explícito de claves para garantizar determinismo en la serialización
        return json.dumps(payload, indent=2, sort_keys=True)

    @staticmethod
    def format_markdown(result: LeaderboardResult) -> str:
        """Genera un reporte ejecutivo en Markdown puro garantizando consistencia semántica y Fail-Fast."""
        lines: list[str] = ["# Benchmark Leaderboard", ""]

        metric_names = list(result.policy.rules.keys())
        header = ["Rank", "Provider", "Composite Score"] + [str(m) for m in metric_names]
        lines.append("| " + " | ".join(header) + " |")

        alignments = [":---:"] + [":---"] + [":---:"] * (1 + len(metric_names))
        lines.append("| " + " | ".join(alignments) + " |")

        for entry in result.entries:
            row = [
                str(entry.rank),
                entry.provider_name,
                f"{entry.composite_score:.4f}",
            ]
            for m in metric_names:
                # Acceso directo por clave. Genera KeyError si la métrica requerida no existe en el DTO
                val = entry.metrics[m]
                row.append(f"{val:.4f}")
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")
        lines.append("## Statistical Significance (#1 vs #2)")
        lines.append("")

        sig = result.significance_report
        if sig is None:
            lines.append("- **Status**: 🔴 N/A (Insufficient observations, $n < 2$ bilateral required)")
        else:
            flag = "🟢 SIGNIFICANT" if sig.is_statistically_significant else "🔴 NOT SIGNIFICANT"
            lines.append(f"- **Metric**: `{sig.metric_name}`")
            lines.append(f"- **Status**: {flag}")
            lines.append(f"- **Effect Size (Cliff's Delta)**: {sig.cliffs_delta_effect_size:.4f} ({sig.effect_size_magnitude})")
            lines.append(f"- **Mann-Whitney U p-value**: {sig.mw_p_value:.4f}")
            lines.append(f"- **Kolmogorov-Smirnov p-value**: {sig.ks_p_value:.4f}")
            # Presentación contextual de las series desde la perspectiva del ranking
            lines.append(f"- **Rank #1 (Winner) Median 95% CI**: [{sig.baseline_median_ci95[0]:.4f}, {sig.baseline_median_ci95[1]:.4f}]")
            lines.append(f"- **Rank #2 (Runner-up) Median 95% CI**: [{sig.challenger_median_ci95[0]:.4f}, {sig.challenger_median_ci95[1]:.4f}]")

        return "\n".join(lines)

    def persist_leaderboard(
        self,
        result: LeaderboardResult,
        gateway: BenchmarkPersistenceGateway,
        json_filename: str = "leaderboard.json",
        md_filename: str = "leaderboard.md",
    ) -> tuple[Path, Path]:
        """Materializa y persiste los artefactos delegando exclusivamente en el gateway."""
        json_content = self.format_json(result)
        md_content = self.format_markdown(result)

        json_path = gateway.save_artifact(json_filename, json_content)
        md_path = gateway.save_artifact(md_filename, md_content)

        return json_path, md_path