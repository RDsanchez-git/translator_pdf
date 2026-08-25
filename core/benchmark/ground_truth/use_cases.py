from typing import Dict, Tuple

from core.ast.models import ASTNode
from core.benchmark.corpus.dtos import RawCorpusManifestDTO
from core.benchmark.corpus.ports import (
    CorpusManifestReaderPort,
    CorpusManifestWriterPort,
)
from core.benchmark.corpus.services import ManifestLineageSealer
from core.benchmark.ground_truth.errors import (
    BaselineContractError,
    EmptyGroundTruthDraftError,
    SealedOracleOverwriteError,
)
from core.benchmark.ground_truth.lifecycle import LifecycleTransitionAuthority
from core.benchmark.ground_truth.models import (
    DraftSubState,
    GroundTruthDraft,
    GroundTruthLifecycleState,
    SealedOracle,
)
from core.benchmark.ground_truth.ports import (
    ASTExtractionPort,
    GroundTruthArtifactPort,
    GroundTruthDraftWriterPort,
    GroundTruthReaderPort,
)
from core.shared.crypto import compute_sha256


class LoadGroundTruthUseCase:
    def __init__(self, reader: GroundTruthReaderPort):
        self._reader = reader

    def execute(self, document_id: str) -> Tuple[ASTNode, ...]:
        if not document_id:
            raise ValueError("Invariant failure: document_id cannot be an empty string.")
        return self._reader.load_ground_truth(document_id)


class GenerateGoldenDraftUseCase:
    """Genera un draft de oráculo para un documento específico.

    NADR-14 §5.3 R7-R9 (DF-14): Impide que un oráculo sellado sea
    sobreescrito por curaduría. Antes de escribir, verifica que el
    documento NO esté en estado SEALED.

    Dependencia entre bounded contexts (M2): Este caso de uso (ground_truth)
    depende de CorpusManifestReaderPort (corpus) para verificar el estado
    del documento. Esto es aceptable porque:
    - La verificación de estado sellado es inherentemente una operación cruzada
    - Solo es lectura (reader, no writer)
    - Respeta la asimetría de puertos (NADR-14 §5.1 R1)
    """

    def __init__(
        self,
        extractor: ASTExtractionPort,
        writer: GroundTruthDraftWriterPort,
        corpus_reader: CorpusManifestReaderPort,
    ):
        self._extractor = extractor
        self._writer = writer
        self._corpus_reader = corpus_reader

    def execute(self, document_id: str) -> None:
        if not document_id:
            raise ValueError("Invariant failure: document_id cannot be empty.")

        # DF-14 (NADR-14 §5.3 R7): Verificar estado sellado antes de escribir.
        # Si el documento no está en el manifiesto, se permite (documento nuevo).
        # Si está en el manifiesto con state != sealed, se permite (curaduría).
        # Si está en el manifiesto con state == sealed, se rechaza (inmutabilidad).
        manifest = self._corpus_reader.load_raw_manifest()
        doc_entry = next(
            (d for d in manifest.documents if d.document_id == document_id),
            None,
        )
        if (
            doc_entry is not None
            and doc_entry.ground_truth_state == GroundTruthLifecycleState.SEALED.value
        ):
            raise SealedOracleOverwriteError(
                f"Cannot overwrite sealed oracle for document '{document_id}'. "
                f"Sealed oracles are immutable (NADR-12 §5.3 R9)."
            )

        extracted_nodes = self._extractor.extract_ast(document_id)
        if not extracted_nodes:
            raise EmptyGroundTruthDraftError(
                f"Extraction returned empty sequence for '{document_id}'"
            )
        self._writer.save_draft_ast(document_id, extracted_nodes)


class SealGroundTruthUseCase:
    """Autoridad única de sellado de la baseline (NADR-14 §5.2 R4-R6).

    Recibe oráculos ya validados y transicionados al estado VALIDATED
    (responsabilidad del entry point). Su responsabilidad es:
    (1) verificar completitud bidireccional contra el manifiesto,
    (2) verificar estado VALIDATED (invariante defensiva),
    (3) sellar cada draft con LifecycleTransitionAuthority,
    (4) persistir estado SEALED en el manifiesto (DF-13),
    (5) calcular hashes de artefactos en disco y recalcular firma global.

    Atomicidad (NADR-13 §5.3 R9-R10): si cualquier invariante falla,
    el caso de uso lanza BaselineContractError sin mutar el manifiesto.
    La verificación de completitud es bidireccional para garantizar que
    solo se sellan baselines completas, independientemente de que el
    entry point haya verificado previamente.

    NADR-14 §5.2 R5: ManifestGroundTruthUpdater fue eliminado (Zero Debt).
    Este caso de uso es el único camino hacia el sellado.
    """

    def __init__(
        self,
        corpus_reader: CorpusManifestReaderPort,
        corpus_writer: CorpusManifestWriterPort,
        artifact_port: GroundTruthArtifactPort,
    ):
        self._corpus_reader = corpus_reader
        self._corpus_writer = corpus_writer
        self._artifact_port = artifact_port

    def execute(
        self,
        validated_drafts: Tuple[GroundTruthDraft, ...],
        target_version: str = "v1.0",
    ) -> str:
        # 1. Cargar manifiesto
        current_manifest = self._corpus_reader.load_raw_manifest()
        manifest_doc_ids = frozenset(d.document_id for d in current_manifest.documents)

        # 2. Verificar completitud bidireccional (biyección estricta).
        # El entry point verifica completitud por eficiencia (fail-fast
        # temprano); el caso de uso verifica por corrección (garantiza
        # que solo sella baselines completas).
        draft_doc_ids = frozenset(d.document_id for d in validated_drafts)
        orphan_drafts = draft_doc_ids - manifest_doc_ids
        missing_drafts = manifest_doc_ids - draft_doc_ids
        if orphan_drafts or missing_drafts:
            completeness_errors = []
            for doc_id in sorted(orphan_drafts):
                completeness_errors.append(
                    f"Validated draft not in manifest: {doc_id}"
                )
            for doc_id in sorted(missing_drafts):
                completeness_errors.append(
                    f"Manifest document without validated draft: {doc_id}"
                )
            raise BaselineContractError(
                completeness_errors=completeness_errors,
                validity_errors=[],
            )

        # 3. Verificar estado VALIDATED (invariante defensiva)
        invalid_state_drafts = [
            d.document_id for d in validated_drafts
            if d.sub_state != DraftSubState.VALIDATED
        ]
        if invalid_state_drafts:
            raise BaselineContractError(
                completeness_errors=[],
                validity_errors=[
                    f"Draft '{doc_id}' not in VALIDATED state (required for sealing)"
                    for doc_id in sorted(invalid_state_drafts)
                ],
            )

        # 4. Sellar cada draft con LifecycleTransitionAuthority
        sealed_oracles: Dict[str, SealedOracle] = {}
        for draft in validated_drafts:
            oracle = LifecycleTransitionAuthority.seal(draft)
            sealed_oracles[draft.document_id] = oracle

        # 5. Calcular hashes DESDE DISCO (no desde memoria)
        detected_hashes: Dict[str, str] = {}
        for doc_id in sorted(sealed_oracles.keys()):
            raw_bytes = self._artifact_port.read_artifact_bytes(doc_id)
            detected_hashes[doc_id] = compute_sha256(raw_bytes)

        # 6. Aplicar firmas + recalcular hash global
        sealed_manifest = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=current_manifest,
            detected_hashes=detected_hashes,
            target_version=target_version,
        )

        # DF-17 (DEFERRED — FASE 4): El manifest_hash calculado por
        # ManifestLineageSealer NO incluye ground_truth_state. La protección
        # criptográfica del estado sellado se completará en Gate 4
        # (NADR-15 §5.3 R9). Entre Gate 3 y Gate 4 existe una ventana donde
        # el estado no está protegido por el hash.
        updated_documents = []
        for entry in sealed_manifest.documents:
            if entry.document_id in sealed_oracles:
                updated_documents.append(
                    entry.model_copy(
                        update={
                            "ground_truth_state": GroundTruthLifecycleState.SEALED.value
                        }
                    )
                )
            else:
                updated_documents.append(entry)

        final_manifest = RawCorpusManifestDTO(
            corpus_version=sealed_manifest.corpus_version,
            manifest_hash=sealed_manifest.manifest_hash,
            documents=updated_documents,
        )

        # 7. Guardar manifiesto (solo si todo pasó)
        self._corpus_writer.save_manifest_dto(final_manifest)
        return final_manifest.manifest_hash