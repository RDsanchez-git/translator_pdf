"""
core/benchmark/types.py

Tipos base, enums y protocolos marcadores para la infraestructura de benchmarking.
Aísla las abstracciones fundamentales para evitar dependencias circulares entre
models.py y ports.py.
"""

from enum import Enum
from typing import Protocol, runtime_checkable


class ProviderKind(str, Enum):
    """SOTA: Categoría funcional inmutable de un proveedor dentro del framework."""

    OCR_PARSER = "ocr_parser"
    LLM_INFERENCE = "llm_inference"
    SEGMENTER = "segmenter"
    TRANSLATOR = "translator"
    LAYOUT = "layout"
    GENERAL = "general"


@runtime_checkable
class BenchmarkArtifact(Protocol):
    """Marcador de tipo abstracto para cualquier artefacto producido por un proveedor."""

    ...