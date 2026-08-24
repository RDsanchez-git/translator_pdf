from typing import Protocol, Tuple
from core.ast.models import ASTNode


class GroundTruthReaderPort(Protocol):
    """Puerto hexagonal para lectura estricta del oráculo en runtime.

    NADR-F17BIS-12 §5.1 R3: el artefacto serializado se hidrata vía
    contrato canónico antes de ser tratado como oráculo. El puerto
    retorna la secuencia hidratada e inmutable; la construcción de la
    entidad de dominio (GroundTruthDraft o SealedOracle) es
    responsabilidad de la capa de aplicación mediante la fábrica
    `hydrate_ground_truth`.
    """
    def load_ground_truth(self, document_id: str) -> Tuple[ASTNode, ...]: ...


class GroundTruthDraftWriterPort(Protocol):
    """Puerto hexagonal para escritura asimétrica durante la curaduría.

    NADR-F17BIS-14 §5.1: superficie de curaduría segregada de la
    superficie de lectura runtime.
    """
    def save_draft_ast(self, document_id: str, nodes: Tuple[ASTNode, ...]) -> None: ...


class ASTExtractionPort(Protocol):
    """Puerto hexagonal para desacoplar la extracción del motor concreto."""
    def extract_ast(self, document_id: str) -> Tuple[ASTNode, ...]: ...


class GroundTruthArtifactPort(Protocol):
    """Puerto hexagonal dedicado a localización y lectura física de bytes."""
    def artifact_exists(self, document_id: str) -> bool: ...
    def read_artifact_bytes(self, document_id: str) -> bytes: ...