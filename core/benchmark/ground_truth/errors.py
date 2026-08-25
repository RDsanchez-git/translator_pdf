"""Taxonomía de errores del bounded context ground_truth.

Jerarquía:
- GroundTruthError (base)
  ├── EmptyGroundTruthDraftError (extracción vacía)
  ├── OracleValidityError (validez estructural, Gate 2)
  ├── IncompleteBaselineError (completitud biyectiva, Gate 2)
  │   └── OrphanOracleError (oráculo huérfano, Gate 2)
  ├── BaselineContractError (reporte agregado, Gate 2)
  └── SealedOracleOverwriteError (protección contra sobrescritura, Gate 3)
"""


class GroundTruthError(Exception):
    """Base exception for the ground_truth bounded context."""
    pass


class EmptyGroundTruthDraftError(GroundTruthError):
    """Raised when the extracted AST sequence is empty during the drafting campaign."""
    pass


# --- Gate 2: Errores de contrato de baseline ---


class OracleValidityError(GroundTruthError):
    """Raised when an oracle fails structural validity (NADR-13 §5.1 R1-R3)."""
    pass


class IncompleteBaselineError(GroundTruthError):
    """Raised when manifest/oracle bijection is incomplete (NADR-13 §5.2 R4-R8)."""
    pass


class OrphanOracleError(IncompleteBaselineError):
    """Raised when an oracle exists without corresponding manifest entry (NADR-13 §5.2 R7)."""
    pass


class BaselineContractError(GroundTruthError):
    """Reporte agregado de todos los fallos de contrato de baseline.

    Construido por SealGroundTruthUseCase tras recolectar errores individuales
    de completitud y validez. Inmutabilidad: listas congeladas como tuples.
    """

    def __init__(
        self,
        completeness_errors: list[str],
        validity_errors: list[str],
    ) -> None:
        self.completeness_errors: tuple[str, ...] = tuple(completeness_errors)
        self.validity_errors: tuple[str, ...] = tuple(validity_errors)
        total = len(self.completeness_errors) + len(self.validity_errors)
        msg = (
            f"Baseline contract violated ({total} errors): "
            f"{len(self.completeness_errors)} completeness, "
            f"{len(self.validity_errors)} validity."
        )
        super().__init__(msg)


# --- Gate 3: Errores de superficie de curaduría gobernada ---


class SealedOracleOverwriteError(GroundTruthError):
    """Raised when a curation operation attempts to overwrite a sealed oracle.

    NADR-12 §5.3 R9 + DF-14: Un oráculo sellado no puede ser alterado
    ni sobrescrito por operaciones de curaduría. Materializa la protección
    a nivel de persistencia (la protección de modelo ya existe desde Gate 1
    vía frozen=True en SealedOracle).
    """
    pass