import json
from pathlib import Path

from tools.evaluation.infrastructure.ast_deserializer import ASTJsonDeserializer
from tools.evaluation.topology.models import BenchmarkDocument


class LocalFileSystemCorpusRepository:
    """Repositorio de infraestructura para la carga del corpus de calibración desde disco."""

    def __init__(self, base_path: Path = Path(".")) -> None:
        self._base_path = base_path

    def load_corpus_documents(
        self,
        provider_name: str,
        corpus_name: str,
    ) -> tuple[BenchmarkDocument, ...]:
        candidates_dir = self._base_path / "candidates" / provider_name
        gt_dir = self._base_path / "tests" / "corpus" / corpus_name / "ground_truth"

        if not candidates_dir.exists():
            raise FileNotFoundError(f"Directorio de candidatos no encontrado: {candidates_dir}")
        if not gt_dir.exists():
            raise FileNotFoundError(f"Directorio Ground Truth no encontrado: {gt_dir}")

        corpus_documents: list[BenchmarkDocument] = []
        gt_files = sorted(gt_dir.glob("*.json"))

        for gt_path in gt_files:
            doc_id = gt_path.stem
            cand_path = candidates_dir / f"{doc_id}.json"

            if not cand_path.exists():
                continue

            with open(cand_path, "r", encoding="utf-8") as f:
                cand_json = json.load(f)
            with open(gt_path, "r", encoding="utf-8") as f:
                gt_json = json.load(f)

            cand_nodes = ASTJsonDeserializer.deserialize_nodes(cand_json)
            gt_nodes = ASTJsonDeserializer.deserialize_nodes(gt_json)

            corpus_documents.append(
                BenchmarkDocument(
                    doc_id=doc_id,
                    candidate=cand_nodes,
                    ground_truth=gt_nodes,
                )
            )

        return tuple(corpus_documents)