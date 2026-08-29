"""Property-based tests de inyectividad del framing criptográfico (Wave 2.3 Fase 3).

Verifica NADR-F17BIS-17 §5.2 R5-R8:
- Inyectividad del encoding: dos payloads válidos distintos dentro del dominio
  producen representaciones de framing distintas antes del hash.

Nota terminológica (SOTA):
Lo que verificamos es inyectividad del FRAMING (la representación string
antes del hash), NO inyectividad de SHA-256 (matemáticamente imposible:
dominio infinito → rango finito de 2^256 valores). El framing es inyectivo
si dos payloads válidos distintos producen representaciones string distintas.

Lo que estos tests NO reemplazan:
- Tests de sensibilidad existentes (TestManifestFingerprintSensitivity,
  TestOracleSemanticIdentity) — los complementan con generación masiva.
- Tests de determinismo unitarios — ya existen y son suficientes.

Lo que estos tests SÍ aportan:
- Generación masiva de casos aleatorios válidos dentro del dominio.
- Shrink automático si se encuentra un caso de colisión.
- Cobertura de edge cases que no se nos ocurrirían manualmente.

HALLAZGO REGISTRADO (Wave 2.3):
ground_truth_state es Optional[str] sin validación explícita de que no
contenga ':'. En la práctica los valores vienen de GroundTruthLifecycleState
enum ("draft", "audited", "validated", "sealed"), pero el contrato del DTO
permite cualquier string. La estrategia de este archivo genera strings sin
':' para mantenerse dentro del dominio válido. El gap se difiere a decisión
del Architecture Board (riesgo bajo mientras el enum permanezca cerrado).

Tasks 2.3.1 (manifest_hash) y 2.3.2 (oracle_hash).
"""

from __future__ import annotations

from hypothesis import assume, given, settings
import hypothesis.strategies as st

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator


# ─────────────────────────────────────────────────────────────────────────────
# ESTRATEGIAS DE HYPOTHESIS
# ─────────────────────────────────────────────────────────────────────────────

# Estrategia para document_id válido (sin ':', sin surrogates, respetando DocumentId)
valid_document_ids = st.text(
    alphabet=st.characters(
        blacklist_characters=":",
        blacklist_categories=("Cs",),  # Excluir surrogates Unicode
    ),
    min_size=1,
    max_size=50,
)

# Estrategia para node_id válido (sin ':', sin surrogates, respetando NodeId)
valid_node_ids = st.text(
    alphabet=st.characters(
        blacklist_characters=":",
        blacklist_categories=("Cs",),  # Excluir surrogates Unicode
    ),
    min_size=1,
    max_size=50,
)

# Estrategia para SHA-256 hex lowercase válido (64 chars)
valid_sha256 = st.text(
    alphabet="0123456789abcdef",
    min_size=64,
    max_size=64,
)

# Estrategia para traits válidos (frozenset de ExtractionChallengeTrait)
valid_traits = st.frozensets(
    st.sampled_from(list(ExtractionChallengeTrait)),
    min_size=1,
)

# Estrategia para page_count válido (entero positivo)
valid_page_counts = st.integers(min_value=1, max_value=10000)

# Estrategia para oracle_hash (None o hex lowercase)
valid_oracle_hashes = st.one_of(
    st.none(),
    valid_sha256,
)

# Estrategia para ground_truth_state (None o string sin ':' ni surrogates)
# NOTA: Se genera texto sin ':' para mantenerse dentro del dominio válido.
# Ver hallazgo registrado en el docstring del módulo sobre este campo.
valid_ground_truth_states = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(
            blacklist_characters=":",
            blacklist_categories=("Cs",),  # Excluir surrogates Unicode
        ),
        min_size=1,
        max_size=20,
    ),
)

# Estrategia para corpus_version (string sin ':' ni surrogates)
valid_corpus_versions = st.text(
    alphabet=st.characters(
        blacklist_characters=":",
        blacklist_categories=("Cs",),  # Excluir surrogates Unicode
    ),
    min_size=1,
    max_size=20,
)

# Estrategia para ContentNodeType
valid_node_types = st.sampled_from(list(ContentNodeType))

# Estrategia para TranslationStrategy
valid_strategies = st.sampled_from(list(TranslationStrategy))

# Estrategia para contenido de payload (sin surrogates)
valid_payload_contents = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),  # Excluir surrogates Unicode
    ),
    min_size=1,
    max_size=100,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _make_metadata(
    doc_id: str,
    sha256: str,
    traits: frozenset[ExtractionChallengeTrait],
    page_count: int,
    oracle_hash: str | None,
    gt_state: str | None,
) -> CorpusDocumentMetadata:
    """Factory para construir CorpusDocumentMetadata en tests."""
    return CorpusDocumentMetadata(
        document_id=doc_id,
        fingerprint=DocumentFingerprint(sha256=sha256),
        traits=traits,
        page_count=page_count,
        oracle_hash=oracle_hash,
        ground_truth_state=gt_state,
    )


def _make_node(
    node_id: str,
    content: str = "Contenido.",
    node_type: ContentNodeType = ContentNodeType.PARAGRAPH,
    strategy: TranslationStrategy = TranslationStrategy.TRANSLATE,
) -> ASTNode:
    """Factory para construir ASTNode en tests."""
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=node_type,
        strategy=strategy,
        payload=ParagraphPayload(content=content),
    )


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DE INYECTIVIDAD DEL FRAMING DE manifest_hash (Task 2.3.1)
# ─────────────────────────────────────────────────────────────────────────────

class TestManifestFramingInjectivity:
    """Property-based tests de inyectividad del framing de ManifestFingerprintCalculator.

    NADR-F17BIS-17 §5.2 R5-R8: El framing debe ser inyectivo dentro del
    dominio válido. Es decir, dos CorpusDocumentMetadata válidos que difieran
    en al menos un campo de identidad deben producir hashes distintos.
    """

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_determinism_same_input_same_hash(
        self, doc_id, sha256, traits, page_count, oracle_hash, gt_state
    ) -> None:
        """Propiedad base: mismo input → mismo hash (determinismo)."""
        v = CorpusVersion(value="v1.0")
        doc = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc])

        assert hash_a == hash_b

    @given(
        doc_id=valid_document_ids,
        new_doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_document_id_sensitivity(
        self, doc_id, new_doc_id, sha256, traits, page_count, oracle_hash, gt_state
    ) -> None:
        """Sensibilidad a document_id: cambio de document_id → hash distinto."""
        assume(doc_id != new_doc_id)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(new_doc_id, sha256, traits, page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        new_sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_fingerprint_sensitivity(
        self, doc_id, sha256, new_sha256, traits, page_count, oracle_hash, gt_state
    ) -> None:
        """Sensibilidad a fingerprint.sha256: cambio de hash físico → hash distinto."""
        assume(sha256 != new_sha256)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(doc_id, new_sha256, traits, page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
        data=st.data(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_traits_sensitivity(
        self, doc_id, sha256, page_count, oracle_hash, gt_state, data
    ) -> None:
        """Sensibilidad a traits: cambio de traits → hash distinto."""
        all_traits = list(ExtractionChallengeTrait)
        assume(len(all_traits) >= 2)

        traits_a = data.draw(st.frozensets(st.sampled_from(all_traits), min_size=1))
        traits_b = data.draw(st.frozensets(st.sampled_from(all_traits), min_size=1))
        assume(traits_a != traits_b)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits_a, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(doc_id, sha256, traits_b, page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        new_page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_page_count_sensitivity(
        self, doc_id, sha256, traits, page_count, new_page_count, oracle_hash, gt_state
    ) -> None:
        """Sensibilidad a page_count: cambio de page_count → hash distinto."""
        assume(page_count != new_page_count)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(doc_id, sha256, traits, new_page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        new_oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_oracle_hash_sensitivity(
        self, doc_id, sha256, traits, page_count, oracle_hash, new_oracle_hash, gt_state
    ) -> None:
        """Sensibilidad a oracle_hash: cambio de identidad semántica → hash distinto."""
        assume(oracle_hash != new_oracle_hash)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(doc_id, sha256, traits, page_count, new_oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
        new_gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_ground_truth_state_sensitivity(
        self, doc_id, sha256, traits, page_count, oracle_hash, gt_state, new_gt_state
    ) -> None:
        """Sensibilidad a ground_truth_state: cambio de estado → hash distinto."""
        assume(gt_state != new_gt_state)

        v = CorpusVersion(value="v1.0")
        doc_a = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_b = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, new_gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(v, [doc_a])
        hash_b = ManifestFingerprintCalculator.compute_hash(v, [doc_b])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
        version_a=valid_corpus_versions,
        version_b=valid_corpus_versions,
    )
    @settings(max_examples=50, deadline=5000)
    def test_corpus_version_sensitivity(
        self, doc_id, sha256, traits, page_count, oracle_hash, gt_state, version_a, version_b
    ) -> None:
        """Sensibilidad a corpus_version: cambio de versión → hash distinto."""
        assume(version_a != version_b)

        doc = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)

        hash_a = ManifestFingerprintCalculator.compute_hash(CorpusVersion(value=version_a), [doc])
        hash_b = ManifestFingerprintCalculator.compute_hash(CorpusVersion(value=version_b), [doc])

        assert hash_a != hash_b

    @given(
        doc_id=valid_document_ids,
        sha256=valid_sha256,
        traits=valid_traits,
        page_count=valid_page_counts,
        oracle_hash=valid_oracle_hashes,
        gt_state=valid_ground_truth_states,
    )
    @settings(max_examples=50, deadline=5000)
    def test_document_order_insensitivity(
        self, doc_id, sha256, traits, page_count, oracle_hash, gt_state
    ) -> None:
        """Insensibilidad al orden: ManifestFingerprintCalculator ordena por document_id.

        Dos manifiestos con los mismos documentos en distinto orden producen
        el mismo hash porque el calculador ordena internamente.
        """
        v = CorpusVersion(value="v1.0")
        doc_1 = _make_metadata(doc_id, sha256, traits, page_count, oracle_hash, gt_state)
        doc_2 = _make_metadata(
            doc_id + "_other",  # Segundo documento distinto
            sha256,
            traits,
            page_count,
            oracle_hash,
            gt_state,
        )

        hash_forward = ManifestFingerprintCalculator.compute_hash(v, [doc_1, doc_2])
        hash_reverse = ManifestFingerprintCalculator.compute_hash(v, [doc_2, doc_1])

        assert hash_forward == hash_reverse


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DE INYECTIVIDAD DEL FRAMING DE oracle_hash (Task 2.3.2)
# ─────────────────────────────────────────────────────────────────────────────

class TestOracleFramingInjectivity:
    """Property-based tests de inyectividad del framing de OracleSemanticIdentityCalculator.

    NADR-F17BIS-17 §5.2 R5-R8: El framing debe ser inyectivo dentro del
    dominio válido. Es decir, dos tuplas de nodos válidas que difieran en
    al menos un campo de identidad deben producir hashes distintos.
    """

    @given(
        node_id=valid_node_ids,
        content=valid_payload_contents,
        node_type=valid_node_types,
        strategy=valid_strategies,
    )
    @settings(max_examples=50, deadline=5000)
    def test_determinism_same_oracle_same_hash(
        self, node_id, content, node_type, strategy
    ) -> None:
        """Propiedad base: mismo oráculo → mismo hash (determinismo)."""
        oracle_a = (_make_node(node_id, content, node_type, strategy),)
        oracle_b = (_make_node(node_id, content, node_type, strategy),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a == hash_b

    @given(
        node_id=valid_node_ids,
        new_node_id=valid_node_ids,
        content=valid_payload_contents,
    )
    @settings(max_examples=50, deadline=5000)
    def test_node_id_sensitivity(
        self, node_id, new_node_id, content
    ) -> None:
        """Sensibilidad a node_id: cambio de node_id → hash distinto."""
        assume(node_id != new_node_id)

        oracle_a = (_make_node(node_id, content),)
        oracle_b = (_make_node(new_node_id, content),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    @given(
        node_id=valid_node_ids,
        content=valid_payload_contents,
        new_content=valid_payload_contents,
    )
    @settings(max_examples=50, deadline=5000)
    def test_content_sensitivity(
        self, node_id, content, new_content
    ) -> None:
        """Sensibilidad al contenido: cambio de texto → hash distinto."""
        assume(content != new_content)

        oracle_a = (_make_node(node_id, content),)
        oracle_b = (_make_node(node_id, new_content),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    @given(
        node_id=valid_node_ids,
        content=valid_payload_contents,
        node_type=valid_node_types,
        new_node_type=valid_node_types,
    )
    @settings(max_examples=50, deadline=5000)
    def test_node_type_sensitivity(
        self, node_id, content, node_type, new_node_type
    ) -> None:
        """Sensibilidad al tipo: cambio de node_type → hash distinto."""
        assume(node_type != new_node_type)

        oracle_a = (_make_node(node_id, content, node_type=node_type),)
        oracle_b = (_make_node(node_id, content, node_type=new_node_type),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    @given(
        node_id=valid_node_ids,
        content=valid_payload_contents,
        strategy=valid_strategies,
        new_strategy=valid_strategies,
    )
    @settings(max_examples=50, deadline=5000)
    def test_strategy_sensitivity(
        self, node_id, content, strategy, new_strategy
    ) -> None:
        """Sensibilidad a la estrategia: cambio de strategy → hash distinto."""
        assume(strategy != new_strategy)

        oracle_a = (_make_node(node_id, content, strategy=strategy),)
        oracle_b = (_make_node(node_id, content, strategy=new_strategy),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    @given(
        node_id_1=valid_node_ids,
        node_id_2=valid_node_ids,
        content=valid_payload_contents,
    )
    @settings(max_examples=50, deadline=5000)
    def test_node_order_sensitivity(
        self, node_id_1, node_id_2, content
    ) -> None:
        """Sensibilidad al orden: cambiar orden de nodos → hash distinto.

        OracleSemanticIdentityCalculator NO ordena internamente, a diferencia
        de ManifestFingerprintCalculator. El orden de los nodos es parte de
        la identidad semántica del oráculo.
        """
        assume(node_id_1 != node_id_2)

        node_1 = _make_node(node_id_1, content)
        node_2 = _make_node(node_id_2, content)

        oracle_forward = (node_1, node_2)
        oracle_reverse = (node_2, node_1)

        hash_forward = OracleSemanticIdentityCalculator.calculate(oracle_forward)
        hash_reverse = OracleSemanticIdentityCalculator.calculate(oracle_reverse)

        assert hash_forward != hash_reverse

    @given(
        node_id_a=valid_node_ids,
        node_id_b=valid_node_ids,
        content=valid_payload_contents,
    )
    @settings(max_examples=50, deadline=5000)
    def test_cardinality_sensitivity(
        self, node_id_a, node_id_b, content
    ) -> None:
        """Sensibilidad a cardinalidad: 1 nodo vs 2 nodos → hash distinto.

        El framing debe ser sensible a la cantidad de nodos. Un oráculo con
        un nodo no puede producir el mismo hash que uno con dos nodos,
        aunque el primer nodo sea idéntico.
        """
        assume(node_id_a != node_id_b)

        node_a = _make_node(node_id_a, content)
        node_b = _make_node(node_id_b, content)

        oracle_single = (node_a,)
        oracle_double = (node_a, node_b)

        hash_single = OracleSemanticIdentityCalculator.calculate(oracle_single)
        hash_double = OracleSemanticIdentityCalculator.calculate(oracle_double)

        assert hash_single != hash_double

    @given(
        node_id=valid_node_ids,
        content=valid_payload_contents,
        sequence_id=st.integers(min_value=1, max_value=1000),
        new_sequence_id=st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=50, deadline=5000)
    def test_sequence_id_insensitivity(
        self, node_id, content, sequence_id, new_sequence_id
    ) -> None:
        """Insensibilidad a metadata física: sequence_id NO afecta el hash.

        Esto verifica que OracleSemanticIdentityCalculator captura solo
        identidad semántica, no metadata física incidental.
        """
        assume(sequence_id != new_sequence_id)

        node_a = ASTNode(
            node_id=node_id,
            sequence_id=sequence_id,
            node_type=ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.TRANSLATE,
            payload=ParagraphPayload(content=content),
        )
        node_b = ASTNode(
            node_id=node_id,
            sequence_id=new_sequence_id,
            node_type=ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.TRANSLATE,
            payload=ParagraphPayload(content=content),
        )

        hash_a = OracleSemanticIdentityCalculator.calculate((node_a,))
        hash_b = OracleSemanticIdentityCalculator.calculate((node_b,))

        assert hash_a == hash_b