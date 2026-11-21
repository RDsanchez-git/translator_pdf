from typing import Protocol, runtime_checkable
from collections.abc import Sequence
from core.ast.models import ASTNode
from core.document_profile.models import InferredDocumentProfile, SamplingReport

class ProfileStore(Protocol):
    """
    SOTA: Puerto de persistencia temporal. 
    Permite al perfil sobrevivir la frontera asincrónica entre el Router y el Assembler.
    """
    def save(self, document_id: str, profile: InferredDocumentProfile) -> None:
        ...
        
    def get(self, document_id: str) -> InferredDocumentProfile | None:
        ...

class ProfileSamplingPolicy(Protocol):
    """Puerto de estrategia de muestreo documental (Bounded Workload)."""
    def sample(self, nodes: Sequence[ASTNode]) -> Sequence[ASTNode]:
        ...

@runtime_checkable
class ReportingSamplingPolicy(Protocol):
    """Puerto opcional para no inferir cobertura a partir de una lista."""
    def sample_with_report(self, nodes: Sequence[ASTNode]) -> SamplingReport:
        ...
