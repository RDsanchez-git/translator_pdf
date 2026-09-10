import json
from pathlib import Path

from core.benchmark.corpus.ports import CorpusManifestReaderPort
from core.benchmark.ground_truth.errors import SealedOracleOverwriteError
from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader

VALID_AST_NODE_TYPES = {
    "composite_block",
    "heading",
    "paragraph",
    "display_equation",
    "inline_equation",
    "table_simple",
    "table_complex",
    "image",
    "caption",
    "code",
    "list",
}

TYPE_MAPPING = {
    "title": "heading",
    "author": "paragraph",
    "abstract": "paragraph",
    "header": "paragraph",
    "footer": "paragraph",
    "footnote": "paragraph",
    "page_number": "paragraph",
}


def _load_sealed_document_ids(corpus_reader: CorpusManifestReaderPort) -> set:
    """Retorna el conjunto de document_ids en estado SEALED.

    Si el manifest no existe, no hay documentos sellados (corpus legacy
    sin manifest). Sin manifest no hay estado de sellado que proteger.
    """
    try:
        manifest_dto = corpus_reader.load_raw_manifest()
    except FileNotFoundError:
        return set()

    sealed_value = GroundTruthLifecycleState.SEALED.value
    return {
        doc.document_id
        for doc in manifest_dto.documents
        if doc.ground_truth_state == sealed_value
    }


def sanitize_corpus(corpus_dir: Path, corpus_reader: CorpusManifestReaderPort) -> None:
    """Sanitiza los node_type de los Ground Truths del corpus.

    Proteccion GAP-5.2-05 (NADR-21 R39-R43): ningun oraculo sellado puede
    ser modificado. Si se intenta sanitizar un documento sellado, se lanza
    SealedOracleOverwriteError (fail-hard, no skip silencioso).
    """
    gt_dir = corpus_dir / "ground_truth"
    if not gt_dir.exists():
        raise FileNotFoundError(f"No existe el directorio '{gt_dir}'.")

    sealed_ids = _load_sealed_document_ids(corpus_reader)

    for json_file in sorted(gt_dir.glob("*.json")):
        doc_id = json_file.stem

        # PROTECCION FAIL-HARD: oraculo sellado es inmutable (GAP-5.2-05)
        if doc_id in sealed_ids:
            raise SealedOracleOverwriteError(
                f"Cannot sanitize '{doc_id}': oracle is SEALED. "
                f"Sealed oracles are immutable (NADR-21)."
            )

        content = json.loads(json_file.read_text(encoding="utf-8"))
        modified = False

        for node in content:
            current_type = node.get("node_type")
            if current_type not in VALID_AST_NODE_TYPES:
                new_type = TYPE_MAPPING.get(current_type, "paragraph")
                # Cero Fallos Silenciosos: warning indexable explicito
                if current_type not in TYPE_MAPPING:
                    print(
                        f"[AST-SANITIZE-001] node_type desconocido "
                        f"'{current_type}' en '{json_file.name}' "
                        f"mapeado a 'paragraph'"
                    )
                node["node_type"] = new_type
                modified = True

        if modified:
            json_file.write_text(
                json.dumps(content, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"[OK] Ground Truth normalizado: '{json_file.name}'")


def main() -> None:
    corpus_dir = Path("tests/corpus/calibration_v1")
    corpus_reader = LocalFileSystemCorpusLoader(corpus_dir)
    sanitize_corpus(corpus_dir, corpus_reader)


if __name__ == "__main__":
    main()
