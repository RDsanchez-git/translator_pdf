from typing import Dict, Tuple

from core.ast.models import ASTNode
from core.benchmark.corpus.ports import (
    CorpusManifestReaderPort,
    CorpusManifestWriterPort,
)
from core.benchmark.corpus.services import ManifestLineageSealer
from core.benchmark.ground_truth.errors import BaselineContractError
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator
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


class LoadGroundTruthUseCase:
    def __init__(self, reader: GroundTruthReaderPort):
        self._reader = reader

    def execute(self, document_id: str) -> Tuple[ASTNode, ...]:
        if not document_id:
            raise ValueError("Invariant failure: document_id cannot be an empty string.")
        return self._reader.load_ground_truth(document_id)


class GenerateGoldenDraftUseCase:
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

        manifest = self._corpus_reader.load_raw_manifest()
        doc_entry = next(
            (d for d in manifest.documents if d.document_id == document_id),
            None,
        )
        if (
            doc_entry is not None
            and doc_entry.ground_truth_state == GroundTruthLifecycleState.SEALED.value
        ):
            from core.benchmark.ground_truth.errors import SealedOracleOverwriteError
            raise SealedOracleOverwriteError(
                f"Cannot overwrite sealed oracle for document '{document_id}'. "
                f"Sealed oracles are immutable (NADR-12 §5.3 R9)."
            )

        extracted_nodes = self._extractor.extract_ast(document_id)
        if not extracted_nodes:
            from core.benchmark.ground_truth.errors import EmptyGroundTruthDraftError
            raise EmptyGroundTruthDraftError(
                f"Extraction returned empty sequence for '{document_id}'"
            )
        self._writer.save_draft_ast(document_id, extracted_nodes)


class SealGroundTruthUseCase:
    """Autoridad única de sellado de la baseline (NADR-14 §5.2 R4-R6).

    Recibe oráculos ya validados y transicionados al estado VALIDATED.
    Su responsabilidad es:
    (1) verificar completitud bidireccional contra el manifiesto,
    (2) verificar estado VALIDATED (invariante defensiva),
    (3) sellar cada draft con LifecycleTransitionAuthority,
    (4) calcular identidad semántica (oracle_hash) de cada oráculo,
    (5) persistir estado SEALED y oracle_hash en el manifiesto,
    (6) recalcular firma global.

    Atomicidad (NADR-13 §5.3 R9-R10): si cualquier invariante falla,
    el caso de uso lanza BaselineContractError sin mutar el manifiesto.

    DC-08 resuelto (Wave 1.2 Fase 3): Se eliminó el cálculo de detected_hashes
    y target_version porque eran utilizados únicamente para alimentar campos
    huérfanos (ground_truth_sha256 y ground_truth_version). Esto elimina I/O
    de disco innecesario durante el sellado. YAGNI.
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
    ) -> str:
        # 1. Cargar manifiesto
        current_manifest = self._corpus_reader.load_raw_manifest()
        manifest_doc_ids = frozenset(d.document_id for d in current_manifest.documents)

        # 2. Verificar completitud bidireccional (biyección estricta).
        draft_doc_ids = frozenset(d.document_id for d in validated_drafts)
        orphan_drafts = draft_doc_ids - manifest_doc_ids
        missing_drafts = manifest_doc_ids - draft_doc_ids
        if orphan_drafts or missing_drafts:
            completeness_errors = []
            for doc_id in sorted(orphan_drafts):
                completeness_errors.append(f"Validated draft not in manifest: {doc_id}")
            for doc_id in sorted(missing_drafts):
                completeness_errors.append(f"Manifest document without validated draft: {doc_id}")
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

        # 5. Calcular identidad semántica (H_semantic) de cada oráculo sellado.
        oracle_hashes: Dict[str, str] = {}
        for doc_id in sorted(sealed_oracles.keys()):
            oracle = sealed_oracles[doc_id]
            oracle_hashes[doc_id] = OracleSemanticIdentityCalculator.calculate(oracle.nodes)

        # 6. Construir ground_truth_states como dict de strings genéricos.
        ground_truth_states: Dict[str, str] = {
            doc_id: GroundTruthLifecycleState.SEALED.value
            for doc_id in sorted(sealed_oracles.keys())
        }

        # 7. Aplicar firmas + recalcular hash global
        sealed_manifest = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=current_manifest,
            oracle_hashes=oracle_hashes,
            ground_truth_states=ground_truth_states,
        )

        # 8. Guardar manifiesto (solo si todo pasó)
        self._corpus_writer.save_manifest_dto(sealed_manifest)
        return sealed_manifest.manifest_hash