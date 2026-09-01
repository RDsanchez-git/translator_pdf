"""
Adaptador Baseline→Evaluación con verificaciones Fail-Fast.

NADR-F17BIS-19 §5.4 R15-R19: Verificaciones previas a la evaluación.
Reutiliza OracleSemanticIdentityCalculator y BaselineCompletenessVerifier.

Nota: GroundTruthState es Annotated[str, StringConstraints] (NO es un enum).
Se usa directamente como str, sin .value.
"""
from __future__ import annotations

from typing import FrozenSet

from core.benchmark.corpus.models import CorpusDocumentMetadata
from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator
from core.benchmark.ground_truth.models import SealedOracle
from core.benchmark.topology.regression.errors import (
    MissingOracleHashError,
    OracleDocumentMismatchError,
    OracleIntegrityError,
    OracleNotSealedError,
)


class RegressionAdapter:
    """Adaptador Baseline→Evaluación con verificaciones Fail-Fast.

    Stateless, determinista, sin I/O (ENGINEERING_PRINCIPLES §II).

    Orden de verificación en verify_all():
    1. Identidad documental (document_id match)
    2. Completitud biyectiva
    3. Estado SEALED
    4. Integridad criptográfica (oracle_hash)
    """

    __slots__ = ()

    def verify_document_identity(
        self,
        oracle: SealedOracle,
        metadata: CorpusDocumentMetadata,
    ) -> None:
        """Verifica que document_id del oráculo coincide con metadata.

        Raises:
            OracleDocumentMismatchError: Si los IDs no coinciden.
        """
        if oracle.document_id != metadata.document_id:
            raise OracleDocumentMismatchError(
                oracle_document_id=str(oracle.document_id),
                metadata_document_id=str(metadata.document_id),
            )

    def verify_oracle_integrity(
        self,
        oracle: SealedOracle,
        metadata: CorpusDocumentMetadata,
    ) -> None:
        """NADR-19 §5.4 R15: Verifica oracle_hash vs. calculado.

        Raises:
            MissingOracleHashError: Si metadata.oracle_hash es None.
            OracleIntegrityError: Si el hash no coincide.
        """
        if metadata.oracle_hash is None:
            raise MissingOracleHashError(document_id=str(metadata.document_id))

        calculated_hash = OracleSemanticIdentityCalculator.calculate(oracle.nodes)

        if calculated_hash != metadata.oracle_hash:
            raise OracleIntegrityError(
                document_id=str(metadata.document_id),
                expected_hash=metadata.oracle_hash,
                actual_hash=calculated_hash,
            )

    def verify_sealed_state(
        self,
        metadata: CorpusDocumentMetadata,
    ) -> None:
        """NADR-19 §5.4 R16: Verifica ground_truth_state == SEALED.

        Nota: GroundTruthState es str, NO enum. Sin .value.

        Raises:
            OracleNotSealedError: Si el estado no es "sealed".
        """
        state_value = metadata.ground_truth_state

        if state_value != "sealed":
            raise OracleNotSealedError(
                document_id=str(metadata.document_id),
                actual_state=str(state_value) if state_value is not None else None,
            )

    def verify_completeness(
        self,
        manifest_doc_ids: FrozenSet[str],
        artifact_doc_ids: FrozenSet[str],
    ) -> None:
        """NADR-19 §5.4 R17: Verifica completitud biyectiva.

        Raises:
            IncompleteBaselineError: Si la verificación falla.
        """
        errors = BaselineCompletenessVerifier.verify(
            manifest_doc_ids=manifest_doc_ids,
            artifact_doc_ids=artifact_doc_ids,
        )

        if errors:
            raise IncompleteBaselineError("; ".join(errors))

    def verify_all(
        self,
        oracle: SealedOracle,
        metadata: CorpusDocumentMetadata,
        manifest_doc_ids: FrozenSet[str],
        artifact_doc_ids: FrozenSet[str],
    ) -> None:
        """Ejecuta todas las verificaciones en secuencia Fail-Fast.

        NADR-19 §5.4 R18: Si cualquier verificación falla,
        abortar inmediatamente.

        Orden:
        1. Identidad documental (detecta cruce de documentos)
        2. Completitud biyectiva (detecta corpus incompleto)
        3. Estado SEALED (detecta oráculo no sellado)
        4. Integridad criptográfica (detecta oráculo mutado)
        """
        self.verify_document_identity(oracle, metadata)
        self.verify_completeness(manifest_doc_ids, artifact_doc_ids)
        self.verify_sealed_state(metadata)
        self.verify_oracle_integrity(oracle, metadata)