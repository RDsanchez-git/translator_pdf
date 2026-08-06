# apps/bootstrap/extraction_config.py
"""
NADR-02 §5.2 R1: Configuración del subsistema de extracción.

Pertenece al Composition Root (wiring), NO al dominio.
El dominio conoce únicamente ExtractionProvider (contrato abstracto).
Los identificadores concretos (PYMUPDF, DOCLING, TESSERACT) son
decisiones de infraestructura que el dominio jamás debe ver.
"""

from enum import Enum
from dataclasses import dataclass


class ExtractionProviderId(str, Enum):
    """
    Identidad concreta del proveedor de extracción.
    
    NADR-02 §5.2 R1: Cada valor representa un motor específico.
    Este enum vive en el Composition Root porque el dominio
    no debe conocer implementaciones concretas.
    """
    PYMUPDF = "pymupdf"
    DOCLING = "docling"
    TESSERACT = "tesseract"


@dataclass(frozen=True)
class ExtractionConfiguration:
    """
    Configuración inmutable para el wiring de extracción.
    
    Existe exclusivamente para construir el grafo de objetos
    en el Composition Root. No es un concepto de dominio.
    """
    provider_id: ExtractionProviderId