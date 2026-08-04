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
from apps.bootstrap.pipeline_factory import build_extraction_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("generate_golden_draft")

def main() -> None:
    """Imperative Shell. Composes production components and triggers the drafting pipeline."""
    base_path = pathlib.Path("tests/corpus/benchmark_v1")
    pdf_directory = base_path / "pdf"

    corpus_loader: CorpusManifestLoaderPort = LocalFileSystemCorpusLoader(base_path)
    writer_adapter = LocalFileSystemGroundTruthDraftWriter(base_path)

    # NADR-10 §5.3 R9: Reutilizar la Composition Root
    production_parser = build_extraction_pipeline()

    extractor_adapter = BenchmarkParserBridge(
        pdf_directory=pdf_directory,
        pipeline_parser=production_parser
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