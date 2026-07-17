from typing import Sequence, Dict
from core.ast.models import ASTNode
from core.benchmark.corpus.ports import CorpusManifestLoaderPort
from core.benchmark.corpus.services import ManifestLineageSealer
from core.benchmark.ground_truth.ports import GroundTruthReaderPort, GroundTruthDraftWriterPort, ASTExtractionPort, GroundTruthArtifactPort
from core.shared.crypto import compute_sha256


class LoadGroundTruthUseCase:
    def __init__(self, reader: GroundTruthReaderPort):
        self._reader = reader

    def execute(self, document_id: str) -> Sequence[ASTNode]:
        if not document_id:
            raise ValueError("Invariant failure: document_id cannot be an empty string.")
        return self._reader.load_ground_truth(document_id)


class GenerateGoldenDraftUseCase:
    def __init__(self, extractor: ASTExtractionPort, writer: GroundTruthDraftWriterPort):
        self._extractor = extractor
        self._writer = writer

    def execute(self, document_id: str) -> None:
        if not document_id:
            raise ValueError("Invariant failure: document_id cannot be empty.")

        extracted_nodes = self._extractor.extract_ast(document_id)
        if not extracted_nodes:
            from core.benchmark.ground_truth.errors import EmptyGroundTruthDraftError
            raise EmptyGroundTruthDraftError(f"Extraction returned empty sequence for '{document_id}'")

        self._writer.save_draft_ast(document_id, extracted_nodes)


class SealGroundTruthUseCase:
    """Orquestador purificado de aplicación. Totalmente desacoplado de los modelos internos del Corpus."""
    def __init__(self, corpus_loader: CorpusManifestLoaderPort, artifact_port: GroundTruthArtifactPort):
        self._corpus_loader = corpus_loader
        self._artifact_port = artifact_port

    def execute(self, target_version: str = "v1.0") -> str:
        current_manifest = self._corpus_loader.load_raw_manifest()
        detected_hashes: Dict[str, str] = {}

        # 1. Recolección de firmas binarias puras sin tocar modelos de dominio extraños
        for doc_entry in current_manifest.documents:
            doc_id = doc_entry.document_id
            if self._artifact_port.artifact_exists(doc_id):
                raw_bytes = self._artifact_port.read_artifact_bytes(doc_id)
                detected_hashes[doc_id] = compute_sha256(raw_bytes)

        # 2. Delegación inter-contexto al servicio especialista del Corpus
        sealed_manifest = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=current_manifest,
            detected_hashes=detected_hashes,
            target_version=target_version
        )

        # 3. Persistencia a través del puerto
        self._corpus_loader.save_manifest_dto(sealed_manifest)
        return sealed_manifest.manifest_hash