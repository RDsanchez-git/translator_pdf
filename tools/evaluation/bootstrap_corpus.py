import pathlib
from core.benchmark.corpus.use_cases import BootstrapCorpusManifestUseCase
from infra.adapters.document_metadata import PyMuPdfDocumentMetadataExtractor
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader

def main() -> None:
    base_path = pathlib.Path("tests/corpus/benchmark_v1")
    
    loader = LocalFileSystemCorpusLoader(base_path)
    extractor = PyMuPdfDocumentMetadataExtractor()
    
    # Invocación limpia del caso de uso mutador
    use_case = BootstrapCorpusManifestUseCase(loader=loader, extractor=extractor)
    result = use_case.execute(base_path / "pdf")
    
    print("[SUCCESS] Cierre criptográfico del Corpus canónico exitoso.")
    print(f"Hash del Manifiesto: {result.manifest_hash}")
    print(f"Documentos indexados: {result.documents_processed} | Páginas totales: {result.total_pages_indexed}")

if __name__ == "__main__":
    main()