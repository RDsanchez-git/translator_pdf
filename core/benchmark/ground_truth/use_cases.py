from typing import Dict, Tuple
from core.ast.models import ASTNode
from core.benchmark.corpus.ports import CorpusManifestLoaderPort
from core.benchmark.corpus.services import ManifestLineageSealer
from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier
from core.benchmark.ground_truth.errors import BaselineContractError, OracleValidityError
from core.benchmark.ground_truth.ports import (
    ASTExtractionPort,
    GroundTruthArtifactPort,
    GroundTruthDraftWriterPort,
    GroundTruthReaderPort,
)
from core.benchmark.ground_truth.validity import OracleValidityContract
from core.shared.crypto import compute_sha256


class LoadGroundTruthUseCase:
    """Caso de uso de lectura del Ground Truth.

    NADR-F17BIS-12 §5.1 R3: retorna la secuencia hidratada vía contrato
    canónico. NO construye la entidad de dominio porque el estado
    (DRAFT vs SEALED) no está en el artefacto y debe ser provisto por
    contexto. La construcción de la entidad es responsabilidad de la
    fábrica `hydrate_ground_truth` invocada por el consumidor que conoce
    el estado (Task 1.2.1 para sellado, casos de uso específicos para
    lectura con estado conocido).
    """

    def __init__(self, reader: GroundTruthReaderPort):
        self._reader = reader

    def execute(self, document_id: str) -> Tuple[ASTNode, ...]:
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
    """Sellado atómico con reporte agregado (NADR-13 §5.3 R9-R10)."""

    def __init__(
        self,
        corpus_loader: CorpusManifestLoaderPort,
        artifact_port: GroundTruthArtifactPort,
        reader: GroundTruthReaderPort,
    ):
        self._corpus_loader = corpus_loader
        self._artifact_port = artifact_port
        self._reader = reader

    def execute(self, target_version: str = "v1.0") -> str:
        current_manifest = self._corpus_loader.load_raw_manifest()
        manifest_doc_ids = frozenset(
            d.document_id for d in current_manifest.documents
        )

        # 1. Completitud (R4-R8)
        artifact_doc_ids = frozenset(self._artifact_port.list_artifact_ids())
        completeness_errors = BaselineCompletenessVerifier.verify(
            manifest_doc_ids, artifact_doc_ids
        )

        # 2. Validez (R1-R3) — solo intersección existente
        validity_errors = []
        existing_doc_ids = manifest_doc_ids & artifact_doc_ids
        for doc_id in sorted(existing_doc_ids):
            nodes = self._reader.load_ground_truth(doc_id)
            try:
                OracleValidityContract.validate(doc_id, tuple(nodes))
            except OracleValidityError as e:
                validity_errors.append(str(e))

        # 3. Reporte agregado: fallar sin mutar nada
        if completeness_errors or validity_errors:
            raise BaselineContractError(completeness_errors, validity_errors)

        # 4. Compute hashes + seal (solo si todo pasó)
        detected_hashes: Dict[str, str] = {}
        for doc_id in sorted(existing_doc_ids):
            raw_bytes = self._artifact_port.read_artifact_bytes(doc_id)
            detected_hashes[doc_id] = compute_sha256(raw_bytes)

        sealed_manifest = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=current_manifest,
            detected_hashes=detected_hashes,
            target_version=target_version,
        )

        self._corpus_loader.save_manifest_dto(sealed_manifest)
        return sealed_manifest.manifest_hash