import pathlib
from core.benchmark.corpus.models import CorpusManifest
from core.benchmark.corpus.services import DocumentComplexityClassifier, ManifestFingerprintCalculator
from core.benchmark.models import BenchmarkDataset, BenchmarkDocument

class CorpusToBenchmarkDatasetMapper:
    """Transformador estructural limpio. Cero filtraciones de políticas (Problema 2)."""
    
    @staticmethod
    def map_to_dataset(manifest: CorpusManifest, pdf_directory: pathlib.Path) -> BenchmarkDataset:
        mapped_documents = []
        
        for doc in manifest.documents:
            # Delegación formal de la política al clasificador del dominio
            complexity = DocumentComplexityClassifier.classify(doc.traits)
            absolute_pdf_path = pdf_directory / f"{doc.document_id}.pdf"

            mapped_documents.append(
                BenchmarkDocument(
                    id=doc.document_id,
                    file_path=str(absolute_pdf_path),
                    file_sha256=doc.fingerprint.sha256,
                    complexity=complexity,
                    expected_pages=doc.page_count,
                    input_tokens_actual=0,  
                    expected_chunks=0       
                )
            )

        # Erradicación de la mentira semántica (Problema 3): Identidad matemática real del conjunto
        actual_manifest_hash = ManifestFingerprintCalculator.compute_hash(manifest.corpus_version, manifest.documents)

        return BenchmarkDataset(
            dataset_id=f"dataset_{manifest.corpus_version.value}",
            dataset_sha256=actual_manifest_hash,
            documents=mapped_documents
        )