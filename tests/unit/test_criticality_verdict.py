# ============================================================================
# ARCHIVO 4: tests/unit/test_criticality_verdict.py
# Task: 1.3.5
# NADRs: NADR-18 §5.4 R16-R19, §5.5 R20, R22
# ============================================================================

"""
Tests unitarios del mecanismo de veredicto por criticidad y trazabilidad.

Verifica:
- NADR-18 §5.4 R16: Pérdida CRITICAL → fallo absoluto independiente del NSS
- NADR-18 §5.4 R17: Precedencia del mecanismo absoluto
- NADR-18 §5.4 R18: Pérdida WARNING → veredicto según umbral
- NADR-18 §5.4 R19: Pérdida INFO → PASS con observación, nunca fallo
- NADR-18 §5.5 R20: Trazabilidad de clasificación por nodo
- NADR-18 §5.5 R22: Evento de gobernanza para reclasificaciones
"""
from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import (
    ASTNode,
    ParagraphPayload,
    HeadingPayload,
    MathPayload,
    ImagePayload,
)

from core.benchmark.topology.models import RecallDiagnostics

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy
from core.benchmark.topology.criticality.verdict import (
    CriticalityVerdictEmitter,
    CriticalityVerdict,
    RecallByNodeType,
)
from core.benchmark.topology.criticality.traceability import (
    ClassificationRecord,
    ClassificationTrace,
    ClassificationTracer,
    create_reclassification_event,
    CRITICALITY_POLICY_VERSION,
)


# =====================================================================
# HELPERS
# =====================================================================


def _make_node(
    node_id: str,
    node_type: ContentNodeType,
    content: str = "test content",
) -> ASTNode:
    """Helper para crear ASTNode de prueba."""
    payload_map = {
        ContentNodeType.PARAGRAPH: ParagraphPayload(content=content),
        ContentNodeType.HEADING: HeadingPayload(content=content),
        ContentNodeType.DISPLAY_EQUATION: MathPayload(content=content),
        ContentNodeType.INLINE_EQUATION: MathPayload(content=content),
        ContentNodeType.IMAGE: ImagePayload(),
    }
    payload = payload_map.get(node_type, ParagraphPayload(content=content))
    return ASTNode(
        node_id=node_id,
        node_type=node_type,
        strategy=TranslationStrategy.TRANSLATE,
        payload=payload,
    )


def _make_recall(
    node_type: ContentNodeType,
    false_negatives: int,
    true_positives: int = 10,
    false_positives: int = 0,
) -> RecallByNodeType:
    """Helper para crear RecallByNodeType."""
    tp = true_positives
    fp = false_positives
    fn = false_negatives
    return RecallByNodeType(
        node_type=node_type,
        diagnostics=RecallDiagnostics(
            precision=tp / (tp + fp) if (tp + fp) > 0 else 0.0,
            recall=tp / (tp + fn) if (tp + fn) > 0 else 0.0,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
        ),
    )


# =====================================================================
# 1. CriticalityVerdict — Properties
# =====================================================================


class TestCriticalityVerdictProperties:
    """Tests de las propiedades derivadas de CriticalityVerdict."""

    def test_is_absolute_failure_when_critical_loss(self):
        """NADR-18 §5.4 R16: Pérdida CRITICAL = fallo absoluto."""
        verdict = CriticalityVerdict(
            has_critical_loss=True,
            has_warning_loss=False,
            has_info_loss=False,
            critical_false_negatives=1,
            warning_false_negatives=0,
            info_false_negatives=0,
        )
        assert verdict.is_absolute_failure is True

    def test_is_absolute_failure_false_when_no_critical_loss(self):
        """Sin pérdida CRITICAL, no es fallo absoluto."""
        verdict = CriticalityVerdict(
            has_critical_loss=False,
            has_warning_loss=True,
            has_info_loss=False,
            critical_false_negatives=0,
            warning_false_negatives=3,
            info_false_negatives=0,
        )
        assert verdict.is_absolute_failure is False

    def test_is_warning_when_warning_loss_and_no_critical(self):
        """NADR-18 §5.4 R18: WARNING sin CRITICAL = warning."""
        verdict = CriticalityVerdict(
            has_critical_loss=False,
            has_warning_loss=True,
            has_info_loss=False,
            critical_false_negatives=0,
            warning_false_negatives=2,
            info_false_negatives=0,
        )
        assert verdict.is_warning is True

    def test_is_warning_false_when_critical_loss_present(self):
        """NADR-18 §5.4 R17: CRITICAL tiene precedencia sobre WARNING."""
        verdict = CriticalityVerdict(
            has_critical_loss=True,
            has_warning_loss=True,
            has_info_loss=False,
            critical_false_negatives=1,
            warning_false_negatives=5,
            info_false_negatives=0,
        )
        assert verdict.is_warning is False
        assert verdict.is_absolute_failure is True

    def test_is_pass_with_observation_when_only_info_loss(self):
        """NADR-18 §5.4 R19: Solo INFO = PASS con observación."""
        verdict = CriticalityVerdict(
            has_critical_loss=False,
            has_warning_loss=False,
            has_info_loss=True,
            critical_false_negatives=0,
            warning_false_negatives=0,
            info_false_negatives=3,
        )
        assert verdict.is_pass_with_observation is True

    def test_is_pass_with_observation_false_when_warning_present(self):
        """INFO + WARNING no es pass_with_observation (es warning)."""
        verdict = CriticalityVerdict(
            has_critical_loss=False,
            has_warning_loss=True,
            has_info_loss=True,
            critical_false_negatives=0,
            warning_false_negatives=2,
            info_false_negatives=3,
        )
        assert verdict.is_pass_with_observation is False
        assert verdict.is_warning is True

    def test_total_false_negatives(self):
        """Suma correcta de falsos negativos."""
        verdict = CriticalityVerdict(
            has_critical_loss=True,
            has_warning_loss=True,
            has_info_loss=True,
            critical_false_negatives=1,
            warning_false_negatives=2,
            info_false_negatives=3,
        )
        assert verdict.total_false_negatives == 6

    def test_verdict_is_immutable(self):
        """CriticalityVerdict es inmutable (frozen dataclass)."""
        verdict = CriticalityVerdict(
            has_critical_loss=True,
            has_warning_loss=False,
            has_info_loss=False,
            critical_false_negatives=1,
            warning_false_negatives=0,
            info_false_negatives=0,
        )
        with pytest.raises(AttributeError):
            verdict.has_critical_loss = False  # type: ignore[misc]


# =====================================================================
# 2. CriticalityVerdictEmitter — NADR-18 §5.4 R16 (ABSOLUTE_FAIL)
# =====================================================================


class TestCriticalityVerdictEmitterAbsoluteFailure:
    """NADR-18 §5.4 R16: Pérdida CRITICAL → fallo absoluto."""

    @pytest.fixture
    def emitter(self) -> CriticalityVerdictEmitter:
        return CriticalityVerdictEmitter()

    def test_single_critical_fn_triggers_absolute_failure(
        self, emitter: CriticalityVerdictEmitter
    ):
        """1 FN de CRITICAL → fallo absoluto."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=1),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=0),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_critical_loss is True
        assert verdict.critical_false_negatives == 1
        assert verdict.is_absolute_failure is True

    def test_multiple_critical_fns_accumulate(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Múltiples FNs de CRITICAL se acumulan."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=2),
            _make_recall(ContentNodeType.TABLE_SIMPLE, false_negatives=1),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.critical_false_negatives == 3
        assert verdict.is_absolute_failure is True

    def test_critical_precedence_over_warning_and_info(
        self, emitter: CriticalityVerdictEmitter
    ):
        """NADR-18 §5.4 R17: CRITICAL tiene precedencia sobre WARNING e INFO."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=1),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=10),
            _make_recall(ContentNodeType.IMAGE, false_negatives=5),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.is_absolute_failure is True
        assert verdict.is_warning is False
        assert verdict.critical_false_negatives == 1
        assert verdict.warning_false_negatives == 10
        assert verdict.info_false_negatives == 5

    def test_critical_loss_independent_of_nss(
        self, emitter: CriticalityVerdictEmitter
    ):
        """ABSOLUTE_FAIL es independiente del NSS (R16, R17)."""
        results = [_make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=1)]
        verdict = emitter.evaluate(results)
        assert verdict.is_absolute_failure is True


# =====================================================================
# 3. CriticalityVerdictEmitter — NADR-18 §5.4 R18 (WARNING)
# =====================================================================


class TestCriticalityVerdictEmitterWarning:
    """NADR-18 §5.4 R18: Pérdida WARNING → veredicto según umbral."""

    def test_warning_at_threshold_triggers_warning(self):
        """FN == threshold → señal WARNING."""
        emitter = CriticalityVerdictEmitter(warning_threshold=2)
        results = [
            _make_recall(ContentNodeType.HEADING, false_negatives=1),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=1),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_warning_loss is True
        assert verdict.warning_false_negatives == 2
        assert verdict.is_warning is True

    def test_warning_above_threshold_triggers_warning(self):
        """FN > threshold → señal WARNING."""
        emitter = CriticalityVerdictEmitter(warning_threshold=1)
        results = [
            _make_recall(ContentNodeType.HEADING, false_negatives=1),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=2),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_warning_loss is True
        assert verdict.warning_false_negatives == 3

    def test_warning_below_threshold_no_warning_signal(self):
        """FN < threshold → no señal WARNING."""
        emitter = CriticalityVerdictEmitter(warning_threshold=3)
        results = [
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=2),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_warning_loss is False
        assert verdict.is_warning is False

    def test_default_threshold_is_one(self):
        """Umbral por defecto es 1."""
        emitter = CriticalityVerdictEmitter()
        assert emitter.warning_threshold == 1

    def test_invalid_threshold_raises(self):
        """Umbral < 1 → ValueError."""
        with pytest.raises(ValueError, match="warning_threshold must be >= 1"):
            CriticalityVerdictEmitter(warning_threshold=0)

    def test_custom_threshold(self):
        """Umbral configurable mediante inyección (R18)."""
        emitter = CriticalityVerdictEmitter(warning_threshold=5)
        results = [
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=4),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_warning_loss is False  # 4 < 5


# =====================================================================
# 4. CriticalityVerdictEmitter — NADR-18 §5.4 R19 (INFO)
# =====================================================================


class TestCriticalityVerdictEmitterInfo:
    """NADR-18 §5.4 R19: Pérdida INFO → PASS con observación, nunca fallo."""

    @pytest.fixture
    def emitter(self) -> CriticalityVerdictEmitter:
        return CriticalityVerdictEmitter()

    def test_info_loss_only_produces_pass_with_observation(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Solo pérdida INFO → PASS con observación."""
        results = [
            _make_recall(ContentNodeType.IMAGE, false_negatives=5),
            _make_recall(ContentNodeType.CAPTION, false_negatives=2),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_info_loss is True
        assert verdict.info_false_negatives == 7
        assert verdict.is_pass_with_observation is True
        assert verdict.is_absolute_failure is False
        assert verdict.is_warning is False

    def test_info_loss_must_not_cause_fail(
        self, emitter: CriticalityVerdictEmitter
    ):
        """INFO MUST NOT causar un veredicto de fallo (R19)."""
        results = [_make_recall(ContentNodeType.IMAGE, false_negatives=100)]
        verdict = emitter.evaluate(results)
        assert verdict.is_absolute_failure is False
        assert verdict.is_warning is False

    def test_info_loss_accumulates(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Múltiples pérdidas INFO se acumulan."""
        results = [
            _make_recall(ContentNodeType.IMAGE, false_negatives=3),
            _make_recall(ContentNodeType.LIST, false_negatives=2),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.info_false_negatives == 5


# =====================================================================
# 5. CriticalityVerdictEmitter — Sin pérdida y edge cases
# =====================================================================


class TestCriticalityVerdictEmitterNoLoss:
    """Sin pérdida de nodos → veredicto limpio."""

    @pytest.fixture
    def emitter(self) -> CriticalityVerdictEmitter:
        return CriticalityVerdictEmitter()

    def test_no_false_negatives_produces_clean_verdict(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Sin FNs, veredicto limpio."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=0),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=0),
            _make_recall(ContentNodeType.IMAGE, false_negatives=0),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.has_critical_loss is False
        assert verdict.has_warning_loss is False
        assert verdict.has_info_loss is False
        assert verdict.total_false_negatives == 0
        assert verdict.is_absolute_failure is False

    def test_empty_results_produces_clean_verdict(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Sin resultados, veredicto limpio."""
        verdict = emitter.evaluate([])
        assert verdict.total_false_negatives == 0
        assert verdict.is_absolute_failure is False

    def test_deterministic_same_input_same_output(
        self, emitter: CriticalityVerdictEmitter
    ):
        """Mismo input → mismo output (determinismo)."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=1),
            _make_recall(ContentNodeType.PARAGRAPH, false_negatives=2),
        ]
        first = emitter.evaluate(results)
        second = emitter.evaluate(results)
        assert first == second

    def test_default_policy_used_when_none(self):
        """Si no se inyecta policy, usa DefaultCriticalityPolicy."""
        emitter = CriticalityVerdictEmitter(policy=None)
        assert isinstance(emitter.policy, DefaultCriticalityPolicy)

    def test_negative_fn_ignored(self, emitter: CriticalityVerdictEmitter):
        """FNs negativos se ignoran (no deberían ocurrir, pero son seguros)."""
        results = [
            _make_recall(ContentNodeType.DISPLAY_EQUATION, false_negatives=-1),
        ]
        verdict = emitter.evaluate(results)
        assert verdict.critical_false_negatives == 0
        assert verdict.is_absolute_failure is False


# =====================================================================
# 6. ClassificationTracer — NADR-18 §5.5 R20
# =====================================================================


class TestClassificationTracer:
    """NADR-18 §5.5 R20: Trazabilidad de clasificación por nodo."""

    @pytest.fixture
    def tracer(self) -> ClassificationTracer:
        return ClassificationTracer()

    def test_trace_nodes_records_all_classifications(
        self, tracer: ClassificationTracer
    ):
        """Registra la clasificación de cada nodo evaluado."""
        nodes = [
            _make_node("eq1", ContentNodeType.DISPLAY_EQUATION),
            _make_node("h1", ContentNodeType.HEADING),
            _make_node("img1", ContentNodeType.IMAGE),
        ]
        trace = tracer.trace_nodes(nodes)

        assert trace.total_nodes == 3
        assert trace.critical_count == 1
        assert trace.warning_count == 1
        assert trace.info_count == 1

    def test_trace_nodes_records_policy_version(
        self, tracer: ClassificationTracer
    ):
        """Cada registro incluye la versión de la política."""
        nodes = [_make_node("eq1", ContentNodeType.DISPLAY_EQUATION)]
        trace = tracer.trace_nodes(nodes)

        assert len(trace.records) == 1
        assert trace.records[0].policy_version == CRITICALITY_POLICY_VERSION

    def test_trace_nodes_empty_returns_empty_trace(
        self, tracer: ClassificationTracer
    ):
        """Lista vacía → trace vacío."""
        trace = tracer.trace_nodes([])

        assert trace.is_empty is True
        assert trace.total_nodes == 0

    def test_trace_is_deterministic(self, tracer: ClassificationTracer):
        """Mismos inputs → mismo trace (determinismo)."""
        nodes = [
            _make_node("eq1", ContentNodeType.DISPLAY_EQUATION),
            _make_node("h1", ContentNodeType.HEADING),
        ]
        trace1 = tracer.trace_nodes(nodes)
        trace2 = tracer.trace_nodes(nodes)

        assert trace1 == trace2

    def test_classification_record_is_immutable(self):
        """ClassificationRecord es inmutable (frozen dataclass)."""
        record = ClassificationRecord(
            node_id="n1",
            node_type=ContentNodeType.PARAGRAPH,
            criticality=NodeCriticality.WARNING,
        )
        with pytest.raises(AttributeError):
            record.criticality = NodeCriticality.CRITICAL  # type: ignore[misc]

    def test_classification_trace_is_immutable(self):
        """ClassificationTrace es inmutable (frozen dataclass)."""
        trace = ClassificationTrace(
            records=(
                ClassificationRecord(
                    node_id="n1",
                    node_type=ContentNodeType.PARAGRAPH,
                    criticality=NodeCriticality.WARNING,
                ),
            ),
            total_nodes=1,
            critical_count=0,
            warning_count=1,
            info_count=0,
        )
        with pytest.raises(AttributeError):
            trace.total_nodes = 999  # type: ignore[misc]

    def test_default_policy_used_when_none(self):
        """Si no se inyecta policy, usa DefaultCriticalityPolicy."""
        tracer = ClassificationTracer(policy=None)
        assert isinstance(tracer.policy, DefaultCriticalityPolicy)

    def test_stateless_multiple_calls_independent(
        self, tracer: ClassificationTracer
    ):
        """Componente STATELESS: llamadas múltiples son independientes."""
        nodes_a = [_make_node("a1", ContentNodeType.DISPLAY_EQUATION)]
        nodes_b = [
            _make_node("b1", ContentNodeType.HEADING),
            _make_node("b2", ContentNodeType.PARAGRAPH),
        ]

        trace_a = tracer.trace_nodes(nodes_a)
        trace_b = tracer.trace_nodes(nodes_b)

        # Cada llamada produce su propio trace independiente
        assert trace_a.total_nodes == 1
        assert trace_b.total_nodes == 2
        assert trace_a.critical_count == 1
        assert trace_b.warning_count == 2


# =====================================================================
# 7. ReclassificationEvent — NADR-18 §5.5 R22
# =====================================================================


class TestReclassificationEvent:
    """NADR-18 §5.5 R22: Evento de gobernanza para reclasificaciones."""

    def test_create_reclassification_event(self):
        """Crea un evento de reclasificación válido."""
        event = create_reclassification_event(
            node_type=ContentNodeType.PARAGRAPH,
            previous_criticality=NodeCriticality.WARNING,
            new_criticality=NodeCriticality.CRITICAL,
            justification="Impact analysis: paragraph loss affects scientific content",
            timestamp="2026-08-30T00:00:00Z",
        )

        assert event.node_type is ContentNodeType.PARAGRAPH
        assert event.previous_criticality is NodeCriticality.WARNING
        assert event.new_criticality is NodeCriticality.CRITICAL
        assert event.justification == "Impact analysis: paragraph loss affects scientific content"
        assert event.timestamp == "2026-08-30T00:00:00Z"

    def test_reclassification_same_criticality_raises(self):
        """Reclasificación con misma criticidad → ValueError."""
        with pytest.raises(ValueError, match="different criticalities"):
            create_reclassification_event(
                node_type=ContentNodeType.PARAGRAPH,
                previous_criticality=NodeCriticality.WARNING,
                new_criticality=NodeCriticality.WARNING,
                justification="Not a real reclassification",
                timestamp="2026-08-30T00:00:00Z",
            )

    def test_reclassification_empty_justification_raises(self):
        """Justificación vacía → ValueError (NADR-18 §5.2 R10)."""
        with pytest.raises(ValueError, match="MUST NOT be empty"):
            create_reclassification_event(
                node_type=ContentNodeType.PARAGRAPH,
                previous_criticality=NodeCriticality.WARNING,
                new_criticality=NodeCriticality.CRITICAL,
                justification="",
                timestamp="2026-08-30T00:00:00Z",
            )

    def test_reclassification_whitespace_justification_raises(self):
        """Justificación con solo whitespace → ValueError."""
        with pytest.raises(ValueError, match="MUST NOT be empty"):
            create_reclassification_event(
                node_type=ContentNodeType.PARAGRAPH,
                previous_criticality=NodeCriticality.WARNING,
                new_criticality=NodeCriticality.CRITICAL,
                justification="   ",
                timestamp="2026-08-30T00:00:00Z",
            )

    def test_reclassification_event_is_immutable(self):
        """ReclassificationEvent es inmutable (frozen dataclass)."""
        event = create_reclassification_event(
            node_type=ContentNodeType.PARAGRAPH,
            previous_criticality=NodeCriticality.WARNING,
            new_criticality=NodeCriticality.CRITICAL,
            justification="Valid justification",
            timestamp="2026-08-30T00:00:00Z",
        )
        with pytest.raises(AttributeError):
            event.justification = "Modified"  # type: ignore[misc]

    def test_reclassification_critical_to_info(self):
        """Reclasificación de CRITICAL a INFO es válida."""
        event = create_reclassification_event(
            node_type=ContentNodeType.IMAGE,
            previous_criticality=NodeCriticality.CRITICAL,
            new_criticality=NodeCriticality.INFO,
            justification="Empirical evidence: image loss does not affect scientific content",
            timestamp="2026-08-30T00:00:00Z",
        )
        assert event.previous_criticality is NodeCriticality.CRITICAL
        assert event.new_criticality is NodeCriticality.INFO