from enum import Enum

class RouteChannel(str, Enum):
    """Canales de destino excluyentes para el flujo del pipeline."""
    TRANSLATE = "TRANSLATE"
    PASSTHROUGH = "PASSTHROUGH"
    OMIT = "OMIT"