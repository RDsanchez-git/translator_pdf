import pathlib
from typing import Sequence
from core.ast.models import ASTNode
from core.benchmark.ground_truth.ports import GroundTruthReaderPort, GroundTruthDraftWriterPort, GroundTruthArtifactPort
from infra.serialization.ast_json import read_ast_json, write_ast_json_atomic

class LocalFileSystemGroundTruthReader(GroundTruthReaderPort):
    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def load_ground_truth(self, document_id: str) -> Sequence[ASTNode]:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        if not target_path.exists():
            raise FileNotFoundError(f"Oracle consistency error: Ground Truth for '{document_id}' not found.")
        return read_ast_json(target_path)


class LocalFileSystemGroundTruthDraftWriter(GroundTruthDraftWriterPort):
    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def save_draft_ast(self, document_id: str, nodes: Sequence[ASTNode]) -> None:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        write_ast_json_atomic(list(nodes), target_path, indent=2)


class LocalFileSystemGroundTruthArtifactAdapter(GroundTruthArtifactPort):
    """Adaptador físico puro. Responsable único del contacto de bajo nivel con el Filesystem."""
    def __init__(self, base_path: pathlib.Path):
        self._ground_truth_directory = base_path / "ground_truth"

    def artifact_exists(self, document_id: str) -> bool:
        return (self._ground_truth_directory / f"{document_id}.json").exists()

    def read_artifact_bytes(self, document_id: str) -> bytes:
        target_path = self._ground_truth_directory / f"{document_id}.json"
        return target_path.read_bytes()