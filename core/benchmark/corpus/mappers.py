import pathlib
from typing import FrozenSet
from core.benchmark.corpus.models import CorpusManifest
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.benchmark.models import BenchmarkDataset, BenchmarkDocument, DocumentComplexity

class CorpusToBenchmarkDatasetMapper:
    """Transformador estructural limpio. Traduce las propiedades del corpus al modelo de evaluación."""
    
    @staticmethod
    def _determine_complexity(traits: FrozenSet[ExtractionChallengeTrait]) -> DocumentComplexity:
        """Derivación determinista de la complejidad de evaluación basada en los descriptores físicos."""
        trait_values = {t.value.lower() for t in traits}
        
        has_math = any("math" in t or "equation" in t for t in trait_values)
        has_table = any("table" in t or "tabular" in t for t in trait_values)
        
        if has_math and has_table:
            return DocumentComplexity.MIXED_HYBRID
        if has_math:
            return DocumentComplexity.DENSE_MATH
        if has_table:
            return DocumentComplexity.HEAVY_TABLES
            
        return DocumentComplexity.STANDARD_PROSE

    @staticmethod
    def map_to_dataset(manifest: CorpusManifest, pdf_directory: pathlib.Path) -> BenchmarkDataset:
        mapped_documents = []
        
        for doc in manifest.documents:
            absolute_pdf_path = pdf_directory / f"{doc.document_id}.pdf"
            
            # El mapper asume la transformación de los traits hacia el Enum tipado
            derived_complexity = CorpusToBenchmarkDatasetMapper._determine_complexity(doc.traits)

            mapped_documents.append(
                BenchmarkDocument(
                    id=doc.document_id,
                    file_path=str(absolute_pdf_path),
                    file_sha256=doc.fingerprint.sha256,
                    complexity=derived_complexity,
                    expected_pages=doc.page_count,
                    input_tokens_actual=0,  
                    expected_chunks=0       
                )
            )

        # Erradicación de la mentira semántica: Identidad matemática real del conjunto
        actual_manifest_hash = ManifestFingerprintCalculator.compute_hash(
            version=manifest.corpus_version, 
            documents=manifest.documents
        )

        return BenchmarkDataset(
            dataset_id=f"dataset_{manifest.corpus_version.value}",
            dataset_sha256=actual_manifest_hash,
            documents=mapped_documents
        )