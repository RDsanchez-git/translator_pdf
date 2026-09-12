import logging
from pathlib import Path
import argparse
from typing import Sequence

from infra.extraction.providers.pymupdf_provider import PyMuPDFProvider
from core.layout.models import LayoutBlockDraft, LayoutBlockCollection
from core.ast.builder import FlatASTBuilder
from infra.serialization.ast_json import write_ast_json_atomic
from core.layout.classification import HeuristicLayoutClassifier
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("generate_pymupdf_candidate")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generacion de candidatos PyMuPDF (GAP-5.0-03, NADR-24 R10)."
    )
    parser.add_argument("--pdf-dir", type=Path, required=True,
                        help="Directorio de PDFs fuente.")
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="Directorio de salida de candidatos.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    pdf_dir: Path = args.pdf_dir
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    provider = PyMuPDFProvider(classifier=HeuristicLayoutClassifier())
    builder = FlatASTBuilder()

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.critical("[PYMUPDF-001] No se encontraron archivos PDF en '%s'.", pdf_dir)
        return EXIT_EXECUTION_FAILURE

    for pdf_path in pdf_files:
        doc_id = pdf_path.stem
        layout = provider.extract(str(pdf_path))

        draft_blocks: list[LayoutBlockDraft] = []
        for page in layout.pages:
            for block in page.blocks:
                assert block.bbox is not None, f"El bloque {block.block_id} requiere BoundingBox espacial."

                draft = LayoutBlockDraft(
                    block_id=block.block_id,
                    logical_type=block.logical_type.value if hasattr(block.logical_type, "value") else str(block.logical_type),
                    content=block.content.cleaned,
                    bbox=block.bbox,
                    confidence=block.metadata.confidence.ocr if block.metadata and block.metadata.confidence else 1.0,
                    provider_native_id=str(block.metadata.provider.native_block_index) if block.metadata and block.metadata.provider else None,
                    column_index=block.metadata.spatial.column_index if block.metadata and block.metadata.spatial else 0,
                    page_index=page.page_number
                )
                draft_blocks.append(draft)

        collection = LayoutBlockCollection(blocks=draft_blocks)
        ast_nodes = builder.build(collection)

        out_file = out_dir / f"{doc_id}.json"
        write_ast_json_atomic(ast_nodes, out_file)
        logger.info("[OK] Candidato generado para '%s' -> '%s'", doc_id, out_file)

    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)