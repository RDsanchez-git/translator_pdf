import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(frozen=True, slots=True)
class WarningEntry:
    """SOTA: Observabilidad estructurada libre de parseo de strings."""
    severity: str  # "INFO", "WARNING", "SEVERE"
    message: str

@dataclass(frozen=True, slots=True)
class NormalizerResult:
    """Contrato de salida de un micro-normalizador con soporte de telemetría segregada."""
    text: str
    fixes: List[str] = field(default_factory=list)
    warnings: List[WarningEntry] = field(default_factory=list)
    hard_fails: List[str] = field(default_factory=list)

@dataclass(frozen=True, slots=True)
class NormalizerTrace:
    """Registro inmutable de auditoría profunda por componente."""
    normalizer_id: str
    fixes: List[str]

@dataclass(frozen=True, slots=True)
class NormalizationReport:
    """Estado final del procesamiento de un nodo del AST."""
    node: Any
    changed: bool
    traces: List[NormalizerTrace] = field(default_factory=list)
    metrics: Dict[str, int] = field(default_factory=dict)
    warnings: List[WarningEntry] = field(default_factory=list)
    hard_fails: List[str] = field(default_factory=list)

@dataclass(frozen=True, slots=True)
class NormalizationEvent:
    """DTO estructurado para el Write-Ahead Log (WAL)."""
    node_id: str
    node_type: str
    changed: bool
    metrics_json: str
    traces_json: str
    timestamp: float

class BaseNormalizer(ABC):
    """Interfaz inmutable para los fixers lógicos del DNL."""
    
    @property
    @abstractmethod
    def normalizer_id(self) -> str:
        pass

    @property
    @abstractmethod
    def normalizer_version(self) -> str:
        pass

    @property
    def signature(self) -> str:
        """
        SOTA: Huella digital determinista basada en el estado de ejecución puro.
        Captura bytecode, constantes lógicas y nombres globales; ignora metadatos de compilación locales.
        """
        co = self.normalize.__code__
        execution_payload = (co.co_code, co.co_consts, co.co_names)
        logic_hash = hashlib.sha256(str(execution_payload).encode("utf-8")).hexdigest()[:12]
        return f"{self.normalizer_id}|v{self.normalizer_version}|logic:{logic_hash}"

    @abstractmethod
    def normalize(self, text: str) -> NormalizerResult:
        pass