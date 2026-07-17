from typing import Protocol, Sequence
from core.ast.models import ASTNode

class GroundTruthReaderPort(Protocol):
    """Hexagonal port for strict read-only retrieval of the oracle in runtime."""
    def load_ground_truth(self, document_id: str) -> Sequence[ASTNode]: ...


class GroundTruthDraftWriterPort(Protocol):
    """Hexagonal port for asymmetric write operations during the bootstrapping campaign."""
    def save_draft_ast(self, document_id: str, nodes: Sequence[ASTNode]) -> None: ...


class ASTExtractionPort(Protocol):
    """Hexagonal port to decouple application layer from specific third-party parser engines."""
    def extract_ast(self, document_id: str) -> Sequence[ASTNode]: ...


class GroundTruthArtifactPort(Protocol):
    """Hexagonal port dedicated strictly to artifact location and physical byte retrieval."""
    def artifact_exists(self, document_id: str) -> bool: ...
    def read_artifact_bytes(self, document_id: str) -> bytes: ...