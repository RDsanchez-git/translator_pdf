"""
Taxonomía de errores del bounded context regression.

Jerarquía:
- RegressionError (base)
  ├── OracleIntegrityError (oracle_hash no coincide)
  ├── OracleNotSealedError (ground_truth_state != SEALED)
  ├── OracleDocumentMismatchError (document_id no coincide)
  ├── MissingOracleHashError (oracle_hash is None en manifiesto)
  └── InvalidNSSScoreError (NSS fuera de [0.0, 1.0] o NaN)

Nota: IncompleteBaselineError se re-exporta desde ground_truth.errors
para conveniencia del consumidor, sin redefinirla.
"""
from __future__ import annotations

from core.benchmark.ground_truth.errors import IncompleteBaselineError


class RegressionError(Exception):
    """Base exception for the regression bounded context."""
    pass


class OracleIntegrityError(RegressionError):
    """NADR-19 §5.4 R15: oracle_hash calculado no coincide con el manifiesto.

    Indica que el oráculo fue mutado en disco o que el manifiesto
    contiene un hash incorrecto.
    """

    def __init__(
        self,
        document_id: str,
        expected_hash: str,
        actual_hash: str,
    ) -> None:
        self.document_id = document_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(
            f"Oracle integrity violation for document '{document_id}': "
            f"expected oracle_hash '{expected_hash[:16]}...' "
            f"but calculated '{actual_hash[:16]}...'. "
            f"The oracle may have been tampered with."
        )


class OracleNotSealedError(RegressionError):
    """NADR-19 §5.4 R16: ground_truth_state no es SEALED.

    No se puede evaluar contra un oráculo que no ha sido sellado.
    """

    def __init__(
        self,
        document_id: str,
        actual_state: str | None,
    ) -> None:
        self.document_id = document_id
        self.actual_state = actual_state
        super().__init__(
            f"Oracle not sealed for document '{document_id}': "
            f"ground_truth_state is '{actual_state}', expected 'sealed'. "
            f"Cannot evaluate against an unsealed oracle."
        )


class OracleDocumentMismatchError(RegressionError):
    """NADR-19 §5.4 R19: document_id del oráculo no coincide con metadata.

    Detecta errores de identidad documental antes de verificar integridad.
    """

    def __init__(
        self,
        oracle_document_id: str,
        metadata_document_id: str,
    ) -> None:
        self.oracle_document_id = oracle_document_id
        self.metadata_document_id = metadata_document_id
        super().__init__(
            f"Document identity mismatch: oracle has document_id "
            f"'{oracle_document_id}' but metadata has "
            f"'{metadata_document_id}'. Cannot verify oracle."
        )


class MissingOracleHashError(RegressionError):
    """NADR-19 §5.4 R19: metadata.oracle_hash es None.

    El manifiesto no tiene hash del oráculo para este documento.
    """

    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(
            f"Document '{document_id}' has no oracle_hash in manifest. "
            f"Cannot verify oracle integrity. The document may not have "
            f"been sealed."
        )


class InvalidNSSScoreError(RegressionError):
    """NADR-19 §5.2 R14: NSS fuera de rango [0.0, 1.0] o NaN.

    El NSS debe ser un valor finito en el rango [0.0, 1.0].
    """

    def __init__(self, nss_score: float) -> None:
        self.nss_score = nss_score
        super().__init__(
            f"NSS score must be a finite value in [0.0, 1.0], "
            f"got {nss_score!r}."
        )


__all__ = [
    "RegressionError",
    "OracleIntegrityError",
    "OracleNotSealedError",
    "OracleDocumentMismatchError",
    "MissingOracleHashError",
    "InvalidNSSScoreError",
    "IncompleteBaselineError",
]