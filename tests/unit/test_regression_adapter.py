"""Tests del RegressionAdapter (NADR-19 §5.4 R15-R19).

CORRECCIONES P2:
- Test de completitud antes de estado sellado (fail-fast order).
- test_fail_fast_identity_first más explícito sobre QUÉ error espera y POR QUÉ.
"""
from __future__ import annotations

from typing import Tuple

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.models import CorpusDocumentMetadata, DocumentFingerprint
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator
from core.benchmark.ground_truth.models import SealedOracle
from core.benchmark.topology.regression.adapter import RegressionAdapter
from core.benchmark.topology.regression.errors import (
    MissingOracleHashError,
    OracleDocumentMismatchError,
    OracleIntegrityError,
    OracleNotSealedError,
)


def _make_node(node_id: str, content: str = "test") -> ASTNode:
    return ASTNode(
        node_id=node_id,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


def _make_oracle(
    document_id: str = "doc1",
    nodes: Tuple[ASTNode, ...] | None = None,
) -> SealedOracle:
    if nodes is None:
        nodes = (_make_node("n1"), _make_node("n2"))
    return SealedOracle(document_id=document_id, nodes=nodes)


def _make_metadata(
    document_id: str = "doc1",
    oracle_hash: str | None = None,
    ground_truth_state: str | None = "sealed",
) -> CorpusDocumentMetadata:
    return CorpusDocumentMetadata(
        document_id=document_id,
        fingerprint=DocumentFingerprint(sha256="a" * 64),
        traits=frozenset({ExtractionChallengeTrait.MULTI_COLUMN}),
        page_count=3,
        oracle_hash=oracle_hash,
        ground_truth_state=ground_truth_state,
    )


class TestVerifyDocumentIdentity:
    @pytest.fixture
    def adapter(self) -> RegressionAdapter:
        return RegressionAdapter()

    def test_matching_ids_passes(self, adapter):
        oracle = _make_oracle(document_id="doc1")
        metadata = _make_metadata(document_id="doc1")
        adapter.verify_document_identity(oracle, metadata)

    def test_mismatched_ids_raises(self, adapter):
        oracle = _make_oracle(document_id="doc_A")
        metadata = _make_metadata(document_id="doc_B")
        with pytest.raises(OracleDocumentMismatchError) as exc_info:
            adapter.verify_document_identity(oracle, metadata)
        assert exc_info.value.oracle_document_id == "doc_A"
        assert exc_info.value.metadata_document_id == "doc_B"


class TestVerifyOracleIntegrity:
    @pytest.fixture
    def adapter(self) -> RegressionAdapter:
        return RegressionAdapter()

    def test_valid_hash_passes(self, adapter):
        oracle = _make_oracle()
        expected = OracleSemanticIdentityCalculator.calculate(oracle.nodes)
        metadata = _make_metadata(oracle_hash=expected)
        adapter.verify_oracle_integrity(oracle, metadata)

    def test_invalid_hash_raises(self, adapter):
        oracle = _make_oracle()
        metadata = _make_metadata(oracle_hash="b" * 64)
        with pytest.raises(OracleIntegrityError) as exc_info:
            adapter.verify_oracle_integrity(oracle, metadata)
        assert exc_info.value.document_id == "doc1"

    def test_none_hash_raises_missing_error(self, adapter):
        oracle = _make_oracle()
        metadata = _make_metadata(oracle_hash=None)
        with pytest.raises(MissingOracleHashError):
            adapter.verify_oracle_integrity(oracle, metadata)


class TestVerifySealedState:
    @pytest.fixture
    def adapter(self) -> RegressionAdapter:
        return RegressionAdapter()

    def test_sealed_passes(self, adapter):
        metadata = _make_metadata(ground_truth_state="sealed")
        adapter.verify_sealed_state(metadata)

    def test_draft_raises(self, adapter):
        metadata = _make_metadata(ground_truth_state="draft")
        with pytest.raises(OracleNotSealedError) as exc_info:
            adapter.verify_sealed_state(metadata)
        assert exc_info.value.actual_state == "draft"

    def test_none_state_raises(self, adapter):
        metadata = _make_metadata(ground_truth_state=None)
        with pytest.raises(OracleNotSealedError):
            adapter.verify_sealed_state(metadata)


class TestVerifyCompleteness:
    @pytest.fixture
    def adapter(self) -> RegressionAdapter:
        return RegressionAdapter()

    def test_complete_passes(self, adapter):
        ids = frozenset({"doc1", "doc2"})
        adapter.verify_completeness(ids, ids)

    def test_missing_raises(self, adapter):
        with pytest.raises(IncompleteBaselineError):
            adapter.verify_completeness(
                frozenset({"doc1", "doc2"}),
                frozenset({"doc1"}),
            )

    def test_orphan_raises(self, adapter):
        with pytest.raises(IncompleteBaselineError):
            adapter.verify_completeness(
                frozenset({"doc1"}),
                frozenset({"doc1", "doc2"}),
            )


class TestVerifyAll:
    @pytest.fixture
    def adapter(self) -> RegressionAdapter:
        return RegressionAdapter()

    def test_all_valid_passes(self, adapter):
        oracle = _make_oracle()
        expected = OracleSemanticIdentityCalculator.calculate(oracle.nodes)
        metadata = _make_metadata(oracle_hash=expected, ground_truth_state="sealed")
        adapter.verify_all(
            oracle, metadata,
            frozenset({"doc1"}), frozenset({"doc1"}),
        )

    def test_fail_fast_identity_first(self, adapter):
        """P2 CORREGIDO: Identidad se verifica primero (Fail-Fast).

        Este test es EXPLÍCITO sobre QUÉ error espera y POR QUÉ:
        - El oráculo tiene document_id="doc_A".
        - La metadata tiene document_id="doc_B".
        - La completitud está rota (doc2 falta en artifacts).
        - El estado es "draft" (no sellado).
        - El hash es inválido.

        El error esperado es OracleDocumentMismatchError porque la
        identidad se verifica ANTES que la completitud, el estado y
        la integridad. Si el orden cambiara, este test fallaría con
        un error diferente, detectando el cambio de orden.
        """
        oracle = _make_oracle(document_id="doc_A")
        metadata = _make_metadata(
            document_id="doc_B",
            oracle_hash="b" * 64,
            ground_truth_state="draft",
        )
        # Completitud rota: doc2 en manifiesto pero no en artifacts.
        with pytest.raises(OracleDocumentMismatchError) as exc_info:
            adapter.verify_all(
                oracle, metadata,
                frozenset({"doc1", "doc2"}), frozenset({"doc1"}),
            )
        # Verificar que el error es de identidad, no de completitud.
        assert exc_info.value.oracle_document_id == "doc_A"
        assert exc_info.value.metadata_document_id == "doc_B"

    def test_fail_fast_completeness_before_sealed_state(self, adapter):
        """P2 NUEVO: Completitud se verifica antes del estado sellado.

        Este test verifica el orden de verificación en verify_all():
        1. Identidad documental (pasa en este test).
        2. Completitud biyectiva (FALLA en este test).
        3. Estado SEALED (no se alcanza).
        4. Integridad criptográfica (no se alcanza).

        El error esperado es IncompleteBaselineError porque la
        completitud se verifica ANTES que el estado sellado.
        Si el orden cambiara, este test fallaría con
        OracleNotSealedError, detectando el cambio de orden.
        """
        oracle = _make_oracle(document_id="doc1")
        # Identidad coincide (doc1 == doc1), así que pasa el paso 1.
        metadata = _make_metadata(
            document_id="doc1",
            oracle_hash="b" * 64,  # Hash inválido, pero no se alcanza.
            ground_truth_state="draft",  # Estado inválido, pero no se alcanza.
        )
        # Completitud rota: doc2 en manifiesto pero no en artifacts.
        with pytest.raises(IncompleteBaselineError) as exc_info:
            adapter.verify_all(
                oracle, metadata,
                frozenset({"doc1", "doc2"}), frozenset({"doc1"}),
            )
        # Verificar que el error es de completitud, no de estado.
        assert isinstance(exc_info.value, IncompleteBaselineError)

    def test_fail_fast_sealed_state_before_integrity(self, adapter):
        """P2 NUEVO: Estado sellado se verifica antes de la integridad.

        Este test verifica el orden de verificación en verify_all():
        1. Identidad documental (pasa en este test).
        2. Completitud biyectiva (pasa en este test).
        3. Estado SEALED (FALLA en este test).
        4. Integridad criptográfica (no se alcanza).

        El error esperado es OracleNotSealedError porque el estado
        se verifica ANTES que la integridad. Si el orden cambiara,
        este test fallaría con OracleIntegrityError, detectando el
        cambio de orden.
        """
        oracle = _make_oracle(document_id="doc1")
        # Identidad coincide y completitud pasa, así que se alcanza el paso 3.
        metadata = _make_metadata(
            document_id="doc1",
            oracle_hash="b" * 64,  # Hash inválido, pero no se alcanza.
            ground_truth_state="draft",  # Estado inválido, se alcanza.
        )
        with pytest.raises(OracleNotSealedError) as exc_info:
            adapter.verify_all(
                oracle, metadata,
                frozenset({"doc1"}), frozenset({"doc1"}),
            )
        # Verificar que el error es de estado, no de integridad.
        assert exc_info.value.actual_state == "draft"