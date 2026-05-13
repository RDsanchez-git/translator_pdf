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
