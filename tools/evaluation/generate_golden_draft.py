import logging
import pathlib

# Imports del flujo del Benchmark y Ground Truth
from core.benchmark.corpus.ports import CorpusManifestLoaderPort
from core.benchmark.ground_truth.use_cases import GenerateGoldenDraftUseCase
from core.benchmark.ground_truth.errors import EmptyGroundTruthDraftError
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthDraftWriter
from infra.benchmarks.adapters.ground_truth_parser_adapter import BenchmarkParserBridge

# Imports exactos del Pipeline Oficial de Producción
from infra.adapters.pdf_parser import PdfParserAdapter
from core.extraction.ocr_providers.pymupdf_provider import PyMuPDFProvider
from core.ast.builder import FlatASTBuilder
from core.ast.models import ASTNode
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft
from core.layout.builder import DocumentLayout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("generate_golden_draft")



def _pipeline_layout_to_ast(document_layout: DocumentLayout) -> list[ASTNode]:
    draft_blocks: list[LayoutBlockDraft] = []
    
    for page in document_layout.pages:
        for block in page.blocks:
            # Transformación explícita de LayoutBlock (Dominio) -> LayoutBlockDraft (DTO Layout)
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
    return FlatASTBuilder().build(collection)


def main() -> None:
    """Imperative Shell. Composes production components and triggers the drafting pipeline."""
    base_path = pathlib.Path("tests/corpus/benchmark_v1")
    pdf_directory = base_path / "pdf"

    corpus_loader: CorpusManifestLoaderPort = LocalFileSystemCorpusLoader(base_path)
    writer_adapter = LocalFileSystemGroundTruthDraftWriter(base_path)

    # 1. Instanciación exacta de la infraestructura de extracción de producción
    concrete_provider = PyMuPDFProvider()  
    
    # 2. Composición del parser delegando al aplanador y al ASTBuilder real
    production_parser = PdfParserAdapter(
        provider=concrete_provider,
        layout_to_ast_mapper=_pipeline_layout_to_ast
    )
    
    # 3. Inyección en el puente del benchmark
    extractor_adapter = BenchmarkParserBridge(
        pdf_directory=pdf_directory,
        pipeline_parser=production_parser
    )

    use_case = GenerateGoldenDraftUseCase(extractor=extractor_adapter, writer=writer_adapter)

    try:
        manifest_dto = corpus_loader.load_raw_manifest()
    except FileNotFoundError as e:
        logger.error("Bootstrap aborted: Unable to load corpus manifest. %s", str(e))
        return

    logger.info("Starting automated drafting campaign. Corpus version: %s", manifest_dto.corpus_version)

    for doc_entry in manifest_dto.documents:
        doc_id = doc_entry.document_id
        logger.info("Executing extraction for document: %s", doc_id)
        
        try:
            use_case.execute(document_id=doc_id)
            logger.info("Draft successfully generated for document: %s", doc_id)
        except FileNotFoundError as e:
            logger.warning("Document execution skipped: %s", str(e))
        except EmptyGroundTruthDraftError as e:
            logger.error("Invalid state detected: %s", str(e))
        except Exception as e:
            logger.error("Unexpected failure processing document %s: %s", doc_id, str(e))


if __name__ == "__main__":
    main()