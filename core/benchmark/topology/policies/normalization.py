from core.benchmark.topology.ports import NormalizationPolicy
from core.benchmark.topology.models import NormalizationInput, NormalizationResult, NormalizationDiagnostics

NUMERIC_TOLERANCE = 1e-9

class MaxBoundNormalizationPolicy(NormalizationPolicy):
    """
    Escala de demeritación analítica acotada estrictamente al intervalo [0.0, 1.0].
    Valida y hace cumplir la invariante geométrica superior del modelo de edición.
    """
    def normalize(self, input_data: NormalizationInput) -> NormalizationResult:
        worst_case = input_data.total_gt_destructive_cost + input_data.total_candidate_constructive_cost
        
        if worst_case <= 0.0:
            return NormalizationResult(
                score=1.0,
                diagnostics=NormalizationDiagnostics(
                    total_gt_destructive_cost=0.0,
                    total_candidate_constructive_cost=0.0,
                    worst_case_bound=0.0
                )
            )

        if input_data.accumulated_distance > worst_case + NUMERIC_TOLERANCE:
            raise ValueError(
                f"Invariante geométrica rota: La distancia calculada ({input_data.accumulated_distance}) "
                f"supera el límite superior del peor escenario teórico ({worst_case})."
            )

        raw_score = 1.0 - (input_data.accumulated_distance / worst_case)
        normalized_score = max(0.0, raw_score)

        diagnostics = NormalizationDiagnostics(
            total_gt_destructive_cost=input_data.total_gt_destructive_cost,
            total_candidate_constructive_cost=input_data.total_candidate_constructive_cost,
            worst_case_bound=worst_case
        )

        return NormalizationResult(score=normalized_score, diagnostics=diagnostics)