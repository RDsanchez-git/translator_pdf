import numpy as np
from scipy import stats
from dataclasses import dataclass, replace
from typing import List, Dict, Tuple, Any, cast
from core.benchmark.models import BenchmarkRunReport, DocumentComplexity

@dataclass(frozen=True, slots=True)
class ScientificSignificanceReport:
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
    def _bootstrap_estimator_ci(data: List[float], estimator_func) -> Tuple[float, float]:
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

        # SOTA FIX: Type Casting a Any para evadir las limitaciones de los stubs de SciPy en Pylance
        # 1. Mann-Whitney U Test
        mw_res = cast(Any, stats.mannwhitneyu(base_vals, chall_vals, alternative='two-sided'))
        u_stat = float(mw_res.statistic if hasattr(mw_res, 'statistic') else mw_res[0])
        mw_p = float(mw_res.pvalue if hasattr(mw_res, 'pvalue') else mw_res[1])
        
        # 2. Kolmogorov-Smirnov Test
        ks_res = cast(Any, stats.ks_2samp(base_vals, chall_vals))
        d_stat = float(ks_res.statistic if hasattr(ks_res, 'statistic') else ks_res[0])
        ks_p = float(ks_res.pvalue if hasattr(ks_res, 'pvalue') else ks_res[1])
        
        # 3. Cliff's Delta
        n1, n2 = len(base_vals), len(chall_vals)
        cliffs_d = (2 * u_stat) / (n1 * n2) - 1
        
        is_significant = (mw_p < cls.ALPHA) or (ks_p < cls.ALPHA)

        # 4. Bootstrap de Colas
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