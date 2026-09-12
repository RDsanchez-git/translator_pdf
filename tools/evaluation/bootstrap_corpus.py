import pathlib
import argparse
from pathlib import Path
from typing import Sequence
from core.benchmark.corpus.use_cases import BootstrapCorpusManifestUseCase
from infra.adapters.document_metadata import PyMuPdfDocumentMetadataExtractor
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap del manifiesto del corpus (GAP-5.0-03, NADR-24 R10)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus (contiene pdf/ y manifest.json).")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    base_path: pathlib.Path = args.corpus_dir

    # Un único adaptador implementa ambos puertos segregados.
    loader = LocalFileSystemCorpusLoader(base_path)
    extractor = PyMuPdfDocumentMetadataExtractor()

    # Inyección de puertos segregados (NADR-14 §5.1 R1).
    use_case = BootstrapCorpusManifestUseCase(
        reader=loader,
        writer=loader,
        extractor=extractor,
    )
    result = use_case.execute(base_path / "pdf")

    print("[SUCCESS] Cierre criptográfico del Corpus canónico exitoso.")
    print(f"Hash del Manifiesto: {result.manifest_hash}")
    print(f"Documentos indexados: {result.documents_processed} | Páginas totales: {result.total_pages_indexed}")


if __name__ == "__main__":
    main()