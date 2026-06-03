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