import pathlib
from typing import Tuple

from core.ast.models import ASTNode
from core.benchmark.ground_truth.ports import (
    GroundTruthArtifactPort,
    GroundTruthDraftWriterPort,
    GroundTruthReaderPort,
)
from infra.serialization.ast_json import read_ast_json, write_ast_json_atomic


class LocalFileSystemGroundTruthReader(GroundTruthReaderPort):
    """Adaptador físico de lectura. Hidrata vía contrato canónico.

    NADR-F17BIS-12 §5.1 R3: el artefacto se hidrata mediante
    `read_ast_json` (contrato canónico, NADR-F17BIS-01) antes de ser
    retornado. La conversión a `Tuple` garantiza inmutabilidad de la
    colección (ENGINEERING_PRINCIPLES §II, lección E-2.0-14).
    """

    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def load_ground_truth(self, document_id: str) -> Tuple[ASTNode, ...]:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        if not target_path.exists():
            raise FileNotFoundError(
                f"Oracle consistency error: Ground Truth for '{document_id}' not found."
            )
        return tuple(read_ast_json(target_path))


class LocalFileSystemGroundTruthDraftWriter(GroundTruthDraftWriterPort):
    """Adaptador físico de escritura de borradores. Atómico (SOTA SRE)."""

    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def save_draft_ast(self, document_id: str, nodes: Tuple[ASTNode, ...]) -> None:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        write_ast_json_atomic(list(nodes), target_path, indent=2)


class LocalFileSystemGroundTruthArtifactAdapter(GroundTruthArtifactPort):
    """Adaptador físico puro. Responsable único del contacto de bajo nivel
    con el Filesystem."""

    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def artifact_exists(self, document_id: str) -> bool:
        return (self._ground_truth_directory / f"{document_id}.json").exists()

    def read_artifact_bytes(self, document_id: str) -> bytes:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        return target_path.read_bytes()

    def list_artifact_ids(self) -> Tuple[str, ...]:
        artifact_ids = sorted(
            p.stem
            for p in self._ground_truth_directory.glob("*.json")
            if p.is_file()
        )
        return tuple(artifact_ids)

