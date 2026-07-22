from pathlib import Path
from core.extraction.ocr_providers.pymupdf_provider import PyMuPDFProvider
from core.layout.models import LayoutBlockDraft, LayoutBlockCollection
from core.ast.builder import FlatASTBuilder
from infra.serialization.ast_json import write_ast_json_atomic

def main() -> None:
    pdf_dir = Path("tests/corpus/calibration_v1/pdf")
    out_dir = Path("tests/corpus/calibration_v1/candidates/pymupdf")
    out_dir.mkdir(parents=True, exist_ok=True)

    provider = PyMuPDFProvider()
    builder = FlatASTBuilder()

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"[ERROR] No se encontraron archivos PDF en '{pdf_dir}'.")
        return

    for pdf_path in pdf_files:
        doc_id = pdf_path.stem
        layout = provider.extract(str(pdf_path))

        draft_blocks: list[LayoutBlockDraft] = []
        for page in layout.pages:
            for block in page.blocks:
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
        print(f"[OK] Candidato generado para '{doc_id}' -> '{out_file}'")

if __name__ == "__main__":
    main()