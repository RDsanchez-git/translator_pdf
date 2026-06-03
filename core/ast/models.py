from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

# =====================================================================
# FAMILIA 1: NODOS ESTRUCTURALES (Contenedores lógicos / Layout)
# =====================================================================
class StructuralNodeType(str, Enum):
    DOCUMENT = "document"
    PART = "part"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"

# =====================================================================
# FAMILIA 2: NODOS SEMÁNTICOS (Payloads de contenido / Traducibles)
# =====================================================================
class ContentNodeType(str, Enum):
    # Texto
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    
    # STEM
    EQUATION = "equation"
    INLINE_EQUATION = "inline_equation"
    TABLE = "table"
    FIGURE = "figure"
    IMAGE = "image"
    CAPTION = "caption"
    ALGORITHM = "algorithm"
    CODE_BLOCK = "code_block"
    
    # Académico
    FOOTNOTE = "footnote"
    CITATION = "citation"
    REFERENCE_ENTRY = "reference_entry"
    BIBLIOGRAPHY = "bibliography"
    APPENDIX = "appendix"
    
    # Recuperación (SOTA Fallbacks)
    MACRO_CHUNK = "macro_chunk"
    COMPOSITE_BLOCK = "composite_block"
    UNKNOWN = "unknown"

# Tipo compuesto para flexibilidad en tipado estático
NodeType = Union[StructuralNodeType, ContentNodeType]

class ASTNode(BaseModel):
    node_id: str
    sequence_id: int = -1  # Control de evolución del esquema
    type: NodeType
    content: Optional[str] = None  
    latex: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None 

    @property
    def has_valid_sequence(self) -> bool:
        """Garantiza que el nodo posee un índice topológico real en base 1."""
        return self.sequence_id >= 1


# SEMANTIC PACKAGING LAYER ---

class TokenEstimator(ABC):
    """SOTA: Interfaz base para inyección de dependencias del tokenizador."""
    @abstractmethod
    def estimate(self, text: str) -> int:
        pass

class FastWordEstimator(TokenEstimator):
    """Fallback heurístico ultra-rápido si el tokenizador nativo no está disponible."""
    def estimate(self, text: str) -> int:
        if not text:
            return 0
        return int(len(text.split()) * 1.3)

@dataclass(frozen=True)
class TranslationUnit:
    """
    SOTA: Contrato estricto e inmutable entre el empaquetador (Chunker) y el LLM.
    Implementa Sliding Window Asimétrico con presupuesto inclusivo, telemetría e integridad criptográfica.
    """
    chunk_index: int                        # Identificador secuencial continuo (Indexación lineal)
    chunk_id: str                           # Identificador único determinista con prefijo de short_hash
    chunk_type: str                         # "translate" o "passthrough"
    source_sequence_range: Tuple[int, int]  # Rango topológico de nodos absorbidos (Base 1)
    node_count: int                         # Densidad atómica de nodos procesados
    reference_context: str                  # Ventana de contexto histórico (Solo Lectura)
    target_payload: str                     # Bloque exclusivo de transformación para el LLM
    estimated_tokens: int                   # Conteo indexado de tokens del payload objetivo
    payload_sha256: str                     # Firma SHA256 completa para almacenamiento e invalidación de caché

@dataclass(frozen=True)
class TranslatedUnit:
    """SOTA: Contrato inmutable de salida de la capa de ejecución distribuida (Fase 10C)."""
    chunk_index: int
    chunk_id: str
    chunk_type: str
    source_sequence_range: Tuple[int, int]
    translated_payload: str
    payload_sha256: str
    model_name: str
    prompt_version: str                     # Corrección 5: Trazabilidad inmutable para Cache Key
    input_tokens: int
    output_tokens: int
    latency_ms: float

@dataclass(frozen=True)
class ReconstructedDocument:
    """SOTA: DTO final inmutable que encapsula el documento ensamblado y su telemetría base."""
    content: str
    total_chunks: int
    translated_chunks: int
    passthrough_chunks: int
    total_input_tokens: int
    total_output_tokens: int