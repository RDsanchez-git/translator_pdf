"""
Estrategia REAL de evaluación de regresión topológica graduada.

NADR-F17BIS-19:
- §5.1 R1-R2: Veredicto graduado por documento y por corpus.
- §5.2 R8-R11: Doble mecanismo de protección.
- §5.6 R23-R25: Interacción con EntityRecallEvaluator ponderada por criticidad.

Implementa el protocolo EvaluationStrategy (evaluate_run).
Orquesta internamente TED + Recall + Criticidad + Doble mecanismo.

CORRECCIONES APLICADAS:
- P0-1: _evaluate_recall_once() evalúa UNA sola vez por evaluador,
  retornando tanto RecallByNodeType como MetricScoreDTO.
- P2: recall_evaluators vacío se valida en __init__ (fail-fast).
- P2: isinstance(RecallDiagnostics) se mantiene como defensa
  perimetral contra cambios futuros en la jerarquía de evaluadores.

Diseño de inyección:
- ted_evaluator: TreeEditDistanceEvaluator ya configurado con
  CriticalityAwareCostContext (construido en el composition root).
- recall_evaluators: Mapping[ContentNodeType, EntityRecallEvaluator],
  un evaluador por tipo de nodo. El dict evita parsing de strings
  del metric_name (acoplamiento frágil eliminado).
"""
from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode
from core.benchmark.topology.criticality.verdict import (
    CriticalityVerdictEmitter,
    RecallByNodeType,
)
from core.benchmark.topology.evaluators.recall import EntityRecallEvaluator
from core.benchmark.topology.ports import TopologicalEvaluatorProtocol
from core.benchmark.topology.models import (
    MetricScoreDTO,
    RecallDiagnostics,
    TopologicalEvaluationReport,
)
from core.benchmark.topology.regression.mechanism import DoubleProtectionMechanism
from core.benchmark.topology.regression.models import RegressionEvaluationReport


class RegressionEvaluationStrategy:
    """Strategy REAL de evaluación de regresión topológica graduada.

    Implementa el protocolo EvaluationStrategy vía evaluate_run().
    Expone evaluate_regression() para acceso al veredicto completo.

    Stateless, determinista, sin I/O (ENGINEERING_PRINCIPLES §II).

    Uso:
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=ted_with_criticality_costs,
            recall_evaluators={
                node_type: EntityRecallEvaluator(node_type, matching_policy)
                for node_type in ContentNodeType
            },
        )
        # Para protocolo EvaluationStrategy (el veredicto se pierde):
        topo_report = strategy.evaluate_run(doc_id, candidate, ground_truth)
        # Para veredicto completo (usar en Gate 3):
        regression_report = strategy.evaluate_regression(doc_id, candidate, ground_truth)
    """

    __slots__ = (
        "_ted_evaluator",
        "_recall_evaluators",
        "_verdict_emitter",
        "_mechanism",
    )

    def __init__(
        self,
        ted_evaluator: TopologicalEvaluatorProtocol,
        recall_evaluators: Mapping[ContentNodeType, EntityRecallEvaluator],
        verdict_emitter: CriticalityVerdictEmitter | None = None,
        mechanism: DoubleProtectionMechanism | None = None,
    ) -> None:
        """Inicializa la strategy con todos los componentes necesarios.

        Args:
            ted_evaluator: TreeEditDistanceEvaluator configurado con
                CriticalityAwareCostContext. metric_name es
                "normalized_structural_score".
            recall_evaluators: Dict mapeando ContentNodeType a su
                EntityRecallEvaluator. El dict garantiza que cada
                evaluador está mapeado a su tipo sin parsing de strings.
                MUST NOT ser vacío.
            verdict_emitter: CriticalityVerdictEmitter. Si None,
                usa default con warning_threshold=1.
            mechanism: DoubleProtectionMechanism. Si None, usa default.

        Raises:
            ValueError: Si recall_evaluators está vacío.
        """
        # P2: Validar que recall_evaluators no esté vacío (fail-fast).
        # Un dict vacío produciría un veredicto de "sin pérdida"
        # incorrecto en vez de fallar explícitamente.
        if not recall_evaluators:
            raise ValueError(
                "recall_evaluators must not be empty. "
                "At least one EntityRecallEvaluator is required."
            )

        self._ted_evaluator = ted_evaluator
        self._recall_evaluators = dict(recall_evaluators)
        self._verdict_emitter = verdict_emitter or CriticalityVerdictEmitter()
        self._mechanism = mechanism or DoubleProtectionMechanism()

    def evaluate_run(
        self,
        document_id: str,
        candidate_ast: Sequence[ASTNode],
        ground_truth_ast: Sequence[ASTNode],
    ) -> TopologicalEvaluationReport:
        """Implementa EvaluationStrategy.evaluate_run().

        Cumple el protocolo existente. Retorna TopologicalEvaluationReport
        con NSS como overall_score.

        Nota: El veredicto y la señal de criticidad se pierden en esta
        conversión. Para acceso completo, usar evaluate_regression().
        """
        report = self._evaluate_full(document_id, candidate_ast, ground_truth_ast)
        return report.to_topological_report()

    def evaluate_regression(
        self,
        document_id: str,
        candidate_ast: Sequence[ASTNode],
        ground_truth_ast: Sequence[ASTNode],
    ) -> RegressionEvaluationReport:
        """Evaluación completa de regresión con veredicto graduado.

        Expone toda la información: veredicto, señal de criticidad,
        falsos negativos por nivel, NSS.

        Este es el método que debe usar el entry point de Gate 3.
        """
        return self._evaluate_full(document_id, candidate_ast, ground_truth_ast)

    def _evaluate_full(
        self,
        document_id: str,
        candidate_ast: Sequence[ASTNode],
        ground_truth_ast: Sequence[ASTNode],
    ) -> RegressionEvaluationReport:
        """Orquestación interna completa.

        Flujo:
        1. TED ponderado → NSS (overall_score)
        2. Recall por tipo de nodo (UNA SOLA PASADA) → RecallByNodeType[] + MetricScoreDTO[]
        3. CriticalityVerdictEmitter → CriticalityVerdict
        4. DoubleProtectionMechanism → DoubleProtectionResult
        5. Construir RegressionEvaluationReport
        """
        # ── Paso 1: TED ponderado → NSS ──────────────────────────
        ted_dto = self._ted_evaluator.evaluate(candidate_ast, ground_truth_ast)
        nss_score = ted_dto.primary_score

        # ── Paso 2: Recall por tipo de nodo (UNA SOLA PASADA) ────
        # P0-1 CORREGIDO: evaluar UNA vez por evaluador, retornar ambos.
        recall_results, recall_dtos = self._evaluate_recall_once(
            candidate_ast, ground_truth_ast
        )

        # ── Paso 3: Veredicto de criticidad ──────────────────────
        criticality_verdict = self._verdict_emitter.evaluate(recall_results)

        # ── Paso 4: Doble mecanismo de protección ────────────────
        dual_result = self._mechanism.evaluate(
            nss_score=nss_score,
            criticality_verdict=criticality_verdict,
        )

        # ── Paso 5: Construir reporte (reutilizando recall_dtos) ─
        all_metrics = (ted_dto, *recall_dtos)

        return RegressionEvaluationReport(
            document_id=document_id,
            metrics=all_metrics,
            overall_score=nss_score,
            verdict=dual_result.verdict,
            criticality_signal=dual_result.criticality_signal,
            critical_false_negatives=dual_result.critical_false_negatives,
            warning_false_negatives=dual_result.warning_false_negatives,
            info_false_negatives=dual_result.info_false_negatives,
        )

    def _evaluate_recall_once(
        self,
        candidate_ast: Sequence[ASTNode],
        ground_truth_ast: Sequence[ASTNode],
    ) -> Tuple[Tuple[RecallByNodeType, ...], Tuple[MetricScoreDTO, ...]]:
        """Evalúa recall UNA SOLA VEZ por evaluador y retorna ambos resultados.

        P0-1 CORREGIDO: En la versión anterior se llamaba evaluator.evaluate()
        dos veces (una en _evaluate_recall, otra en _evaluate_full). Ahora
        se evalúa una sola vez y se retornan ambos resultados.

        El dict recall_evaluators garantiza que cada evaluador está
        mapeado a su ContentNodeType. No se parsea el metric_name.

        Returns:
            Tupla de (RecallByNodeType para veredicto, MetricScoreDTO para reporte).
        """
        recall_results: list[RecallByNodeType] = []
        recall_dtos: list[MetricScoreDTO] = []

        for node_type, evaluator in self._recall_evaluators.items():
            # UNA SOLA llamada por evaluador.
            dto = evaluator.evaluate(candidate_ast, ground_truth_ast)
            recall_dtos.append(dto)

            # Defensa perimetral (NO es YAGNI puro): protege contra
            # cambios futuros en la jerarquía de evaluadores. Si mañana
            # se crea un WeightedRecallEvaluator que produce un diagnóstico
            # diferente, este check evita un crash silencioso.
            # El type system ya garantiza el tipo, pero el runtime check
            # es un seguro adicional de costo cero.
            if dto.diagnostics is None:
                continue
            if not isinstance(dto.diagnostics, RecallDiagnostics):
                continue

            recall_results.append(
                RecallByNodeType(
                    node_type=node_type,
                    diagnostics=dto.diagnostics,
                )
            )

        return tuple(recall_results), tuple(recall_dtos)

    @property
    def ted_evaluator(self) -> TopologicalEvaluatorProtocol:
        return self._ted_evaluator

    @property
    def mechanism(self) -> DoubleProtectionMechanism:
        return self._mechanism