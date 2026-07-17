import hashlib
from typing import List, FrozenSet
from core.benchmark.corpus.models import CorpusVersion, CorpusDocumentMetadata
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.models import DocumentComplexity

class ManifestFingerprintCalculator:
    """Servicio de Dominio. Única fuente de verdad para la identidad criptográfica del manifiesto."""
    @staticmethod
    def compute_hash(version: CorpusVersion, documents: List[CorpusDocumentMetadata]) -> str:
        sorted_docs = sorted(documents, key=lambda d: d.document_id)
        payload_parts = [version.value]
        for doc in sorted_docs:
            traits_str = ",".join(sorted([t.value for t in doc.traits]))
            payload_parts.append(f"{doc.document_id}:{doc.fingerprint.sha256}:{traits_str}:{doc.page_count}")
            
        raw_stream = "|".join(payload_parts)
        return hashlib.sha256(raw_stream.encode("utf-8")).hexdigest()

class DocumentComplexityClassifier:
    """Servicio de Dominio. Centraliza la política de clasificación taxonómica (Problema 2)."""
    @staticmethod
    def classify(traits: FrozenSet[ExtractionChallengeTrait]) -> DocumentComplexity:
        if ExtractionChallengeTrait.HEAVY_MATH in traits:
            return DocumentComplexity.DENSE_MATH
        if ExtractionChallengeTrait.NESTED_TABLES in traits:
            return DocumentComplexity.HEAVY_TABLES
        if len(traits) >= 3:
            return DocumentComplexity.MIXED_HYBRID
        return DocumentComplexity.STANDARD_PROSE