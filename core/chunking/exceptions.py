class ChunkingException(Exception):
    """Excepción base del subdominio de empaquetado."""
    pass

class AtomicNodeTooLargeException(ChunkingException):
    """Lanzada cuando un nodo indivisible supera la ventana máxima de tokens del LLM."""
    pass

class ChunkConstructionException(ChunkingException):
    """Lanzada por violaciones lógicas o asimetrías topológicas durante el ensamblado del bloque."""
    pass