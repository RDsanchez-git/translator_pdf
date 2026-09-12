import json
import logging
from pathlib import Path
import argparse
from typing import Sequence

from core.benchmark.corpus.ports import CorpusManifestReaderPort
from core.benchmark.ground_truth.errors import SealedOracleOverwriteError
from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from core.shared.errors import IndexedError
from core.shared.exit_codes import EXIT_OK
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sanitize_ground_truth_types")

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


def _load_sealed_document_ids(
    corpus_reader: CorpusManifestReaderPort,
    allow_missing_manifest: bool,
) -> set[str]:
    """Retorna el conjunto de document_ids en estado SEALED.

    D2: sin manifest, la verificacion de sellado es imposible (NADR-24 R26).
    Aborta por defecto con IndexedError; requiere override explicito
    --allow-missing-manifest para continuar asumiendo sin oraculos sellados
    (caso de corpus legacy). Evolucion normativa NADR-21 -> NADR-24.
    """
    try:
        manifest_dto = corpus_reader.load_raw_manifest()
    except FileNotFoundError:
        if not allow_missing_manifest:
            raise IndexedError(
                "SANITIZE-001",
                "Manifest ausente: verificacion de sellado imposible (NADR-24 R26). "
                "Usa --allow-missing-manifest para override explicito (corpus legacy).",
            )
        logger.warning(
            "[SANITIZE-W01] Manifest ausente: override explicito; se asume sin oraculos sellados"
        )
        return set()

    sealed_value = GroundTruthLifecycleState.SEALED.value
    return {
        doc.document_id
        for doc in manifest_dto.documents
        if doc.ground_truth_state == sealed_value
    }


def sanitize_corpus(
    corpus_dir: Path,
    corpus_reader: CorpusManifestReaderPort,
    allow_missing_manifest: bool = False,
) -> None:
    """Sanitiza los node_type de los Ground Truths del corpus.

    Proteccion GAP-5.2-05 (NADR-21 R39-R43): ningun oraculo sellado puede
    ser modificado. Si se intenta sanitizar un documento sellado, se lanza
    SealedOracleOverwriteError (fail-hard, no skip silencioso).
    """
    gt_dir = corpus_dir / "ground_truth"
    if not gt_dir.exists():
        raise IndexedError("SANITIZE-002", f"No existe el directorio '{gt_dir}'.")

    sealed_ids = _load_sealed_document_ids(corpus_reader, allow_missing_manifest)

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
                    logger.warning(
                        "[AST-SANITIZE-001] node_type desconocido "
                        "'%s' en '%s' mapeado a 'paragraph'",
                        current_type,
                        json_file.name,
                    )
                node["node_type"] = new_type
                modified = True

        if modified:
            json_file.write_text(
                json.dumps(content, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("[OK] Ground Truth normalizado: '%s'", json_file.name)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sanitizacion de tipos de Ground Truths (GAP-5.0-03, NADR-24 R10)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus.")
    parser.add_argument(
        "--allow-missing-manifest",
        action="store_true",
        help=(
            "Override explicito e indexable: continuar sin manifest asumiendo "
            "sin oraculos sellados (caso de corpus legacy). Sin este flag, "
            "la ausencia de manifest aborta con SANITIZE-001 (NADR-24 R26)."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    corpus_dir: Path = args.corpus_dir
    corpus_reader = LocalFileSystemCorpusLoader(corpus_dir)
    sanitize_corpus(
        corpus_dir,
        corpus_reader,
        allow_missing_manifest=args.allow_missing_manifest,
    )
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)