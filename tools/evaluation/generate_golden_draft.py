import logging
from pathlib import Path
import argparse
from typing import Sequence

# Imports del flujo del Benchmark y Ground Truth
# Wave 3.1: CorpusManifestLoaderPort eliminado; este entry point solo
# necesita lectura (iterar documentos del manifiesto).
# Wave 3.3: Se inyecta CorpusManifestReaderPort en GenerateGoldenDraftUseCase
# para verificar estado sellado antes de escribir (DF-14).
from core.benchmark.corpus.ports import CorpusManifestReaderPort
from core.benchmark.ground_truth.errors import (
    SealedOracleOverwriteError,
)
from core.benchmark.ground_truth.use_cases import GenerateGoldenDraftUseCase
from infra.benchmarks.adapters.ground_truth_parser_adapter import BenchmarkParserBridge
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthDraftWriter

# Imports exactos del Pipeline Oficial de Producción
from apps.bootstrap.pipeline_factory import build_extraction_pipeline

from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("generate_golden_draft")

def classify_document_error(exc: Exception) -> str:
    """D1: sealed oracle es skip esperado (idempotencia R33); resto es failure (R22)."""
    if isinstance(exc, SealedOracleOverwriteError):
        return "skip"
    return "failure"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generacion de Golden Draft (GAP-5.0-03, NADR-24 R10)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus (contiene pdf/ y manifest.json).")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Imperative Shell. Composes production components and triggers the drafting pipeline."""
    args = parse_args(argv)
    base_path: Path = args.corpus_dir
    pdf_directory = base_path / "pdf"

    skips: list[str] = []
    failures: list[str] = []

    # Un único adaptador implementa ambos puertos segregados.
    # Este entry point solo necesita lectura (NADR-14 §5.1 R1).
    corpus_reader: CorpusManifestReaderPort = LocalFileSystemCorpusLoader(base_path)
    writer_adapter = LocalFileSystemGroundTruthDraftWriter(base_path)

    # NADR-10 §5.3 R9: Reutilizar la Composition Root
    production_parser = build_extraction_pipeline()

    extractor_adapter = BenchmarkParserBridge(
        pdf_directory=pdf_directory,
        pipeline_parser=production_parser,
    )

    # DF-14: Inyectar corpus_reader para que el caso de uso verifique
    # el estado sellado antes de escribir (NADR-14 §5.3 R7-R9).
    use_case = GenerateGoldenDraftUseCase(
        extractor=extractor_adapter,
        writer=writer_adapter,
        corpus_reader=corpus_reader,
    )

    try:
        # El fail-fast (E-2.0-05) lanza FileNotFoundError si el manifiesto
        # no existe. Este entry point ya captura y maneja ese caso.
        manifest_dto = corpus_reader.load_raw_manifest()
    except FileNotFoundError as e:
        logger.critical("[DRAFT-001] Bootstrap aborted: Unable to load corpus manifest. %s", str(e))
        return EXIT_EXECUTION_FAILURE

    logger.info(
        "Starting automated drafting campaign. Corpus version: %s",
        manifest_dto.corpus_version,
    )

    for doc_entry in manifest_dto.documents:
        doc_id = doc_entry.document_id
        logger.info("Executing extraction for document: %s", doc_id)

        try:
            use_case.execute(document_id=doc_id)
            logger.info("Draft successfully generated for document: %s", doc_id)
        except Exception as e:
            outcome = classify_document_error(e)
            if outcome == "skip":
                skips.append(doc_id)
                logger.warning("[DRAFT-W01] Document skipped (sealed oracle): %s", str(e))
            else:
                failures.append(doc_id)
                logger.error("[DRAFT-002] Document execution failed: %s", str(e))

    if failures:
        logger.critical(
            "[DRAFT-003] %d unidad(es) obligatoria(s) no procesada(s): %s",
            len(failures),
            failures,
        )
        return EXIT_EXECUTION_FAILURE
    if skips:
        logger.warning("[DRAFT-W02] %d skip(s) esperados (oraculos sellados): %s", len(skips), skips)
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)
