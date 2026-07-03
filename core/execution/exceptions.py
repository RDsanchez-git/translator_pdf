from core.validation.budget import BudgetViolationReason
from core.ast.models import FailureReason

class PipelineIntegrityError(Exception):
    """Clase base para violaciones de invariantes del framework."""
    pass

class IncompleteDocumentError(PipelineIntegrityError):
    """Se dispara cuando el CQRS no tiene el 100% de los chunks requeridos para ensamblar."""
    def __init__(self, document_id: str, expected: int, actual: int):
        self.document_id = document_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Invariante rota para doc {document_id[:8]}: Se esperaban {expected} chunks válidos, se obtuvieron {actual}.")

class OptimisticLockError(PipelineIntegrityError):
    """Fallo en la concurrencia: otro proceso modificó el documento primero."""
    pass

class LeaseExpiredError(PipelineIntegrityError):
    """El worker perdió la propiedad del documento durante la ejecución."""
    pass

class IllegalStateTransitionError(PipelineIntegrityError):
    """El comando intentó una transición no permitida por el grafo FSM."""
    pass

class CircuitOpenError(Exception):
    """Lanzada cuando el circuito está abierto y rechaza peticiones instantáneamente."""
    def __init__(self, cooldown_remaining: float):
        self.cooldown_remaining = cooldown_remaining
        super().__init__(f"Circuit OPEN. Cooldown remaining: {cooldown_remaining:.1f}s")

class CircuitTripError(Exception):
    """Lanzada por el hilo que provocó la apertura del circuito (la gota que rebalsó el vaso)."""
    pass

class TransientAPIError(Exception):
    """Clasificación estandarizada para fallos de red/API (429, 50x, Timeout)."""
    pass

class ChunkExecutionError(Exception):
    """SOTA: Excepción específica para fallos irrecuperables en la capa de ejecución de chunks."""
    def __init__(self, chunk_index: int, chunk_id: str, original_error: Exception):
        self.chunk_index = chunk_index
        self.chunk_id = chunk_id
        self.original_error = original_error
        super().__init__(f"Fallo de ejecución en chunk_index={chunk_index} ({chunk_id}): {str(original_error)}")

class ChunkValidationError(ChunkExecutionError):
    """Lanzada cuando la validación de un chunk produce un resultado HARD_FAIL."""
    def __init__(self, chunk_index: int, chunk_id: str, invariant_id: str, message: str):
        super().__init__(chunk_index, chunk_id, Exception(message))
        self.invariant_id = invariant_id

class DocumentValidationError(Exception):
    """Lanzada cuando la validación del documento completo produce un resultado HARD_FAIL."""
    def __init__(self, invariant_id: str, message: str):
        self.invariant_id = invariant_id
        super().__init__(message)


class TranslationDomainError(Exception):
    """SOTA: Clase base estricta para errores esperados del dominio, separada de errores técnicos (ej. KeyError)."""
    pass

class ContextOverflowError(TranslationDomainError):
    """
    SOTA: Excepción de dominio enriquecida.
    Informa a la capa superior (Dispatcher) por qué el presupuesto falló, 
    permitiendo telemetría fina y mapeo directo a políticas de degradación.
    """
    def __init__(self, message: str, violation_reason: BudgetViolationReason, utilization_ratio: float):
        super().__init__(message)
        self.violation_reason = violation_reason
        self.utilization_ratio = utilization_ratio
        
        # SOTA: Enlace duro con la taxonomía del Assembler (Fase 15.4-D)
        # Esto permite que el Dispatcher marque el outcome como degradable automáticamente.
        self.failure_reason_enum = FailureReason.CONTEXT_OVERFLOW

    def __str__(self) -> str:
        return (
            f"{super().__str__()} | "
            f"Razón: {self.violation_reason.value} | "
            f"Utilización: {self.utilization_ratio:.2f}x"
        )

class PermanentQuotaRejection(TranslationDomainError):
    """SOTA: Fallo matemático insalvable o timeout de retención en el bucket de cuotas."""
    pass

class QuotaTimeoutError(TranslationDomainError):
    """SOTA: Timeout de retención excedido esperando disponibilidad de cuota."""
    pass


# =================================================================================
# Proveedores de OCR
# =================================================================================

class DomainException(Exception):
    """Base inmutable para todas las excepciones del dominio del sistema."""
    pass

class ExtractionError(DomainException):
    """Heredado si ocurre un fallo crítico durante el proceso de ingesta o parsing."""
    def __init__(self, message: str, provider_name: str, pdf_path: str):
        super().__init__(f"[{provider_name}] Fallo de extracción en {pdf_path}: {message}")
        self.provider_name = provider_name
        self.pdf_path = pdf_path

class ProviderFailure(ExtractionError):
    """Heredado ante caídas de subprocesos, timeouts de API o fallos de binaries físicos (Tesseract/Drivers)."""
    pass

class LayoutRecoveryError(ExtractionError):
    """Heredado ante corrupciones geométricas o incapacidad de validar invariantes topológicos."""
    pass

class ASTMappingError(DomainException):
    """Heredado ante fallas de traducción estructural desde el Layout físico hacia el AST lógico."""
    def __init__(self, message: str, pdf_path: str):
        super().__init__(f"Fallo en mapeo lógico de AST para {pdf_path}: {message}")
        self.pdf_path = pdf_path