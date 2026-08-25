class GroundTruthError(Exception):
    """Base exception for the ground_truth bounded context."""
    pass


class EmptyGroundTruthDraftError(GroundTruthError):
    """Raised when the extracted AST sequence is empty during the drafting campaign."""
    pass


# --- Errores INDIVIDUALES (recolectados como strings por el caso de uso) ---


class OracleValidityError(GroundTruthError):
    """Raised when an oracle fails structural validity (NADR-13 §5.1 R1-R3)."""
    pass


class IncompleteBaselineError(GroundTruthError):
    """Raised when manifest/oracle bijection is incomplete (NADR-13 §5.2 R4-R8)."""
    pass


class OrphanOracleError(IncompleteBaselineError):
    """Raised when an oracle exists without corresponding manifest entry (NADR-13 §5.2 R7)."""
    pass


# --- Error COMPUESTO del caso de uso (reporte agregado) ---


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