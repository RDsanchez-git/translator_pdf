import logging
import pathlib

from core.benchmark.corpus.ports import (
    CorpusManifestReaderPort,
    CorpusManifestWriterPort,
)
from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier
from core.benchmark.ground_truth.errors import (
    BaselineContractError,
    OracleValidityError,
)
from core.benchmark.ground_truth.lifecycle import LifecycleTransitionAuthority
from core.benchmark.ground_truth.models import DraftSubState, GroundTruthDraft
from core.benchmark.ground_truth.use_cases import SealGroundTruthUseCase
from core.benchmark.ground_truth.validity import OracleValidityContract
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("freeze_ground_truth")


def main() -> None:
    """Imperative Shell. Orquesta el ciclo de vida en memoria.

    Secuencia atómica (sin I/O intermedio entre verificar y transicionar):
    1. Cargar manifiesto + enumerar artefactos
    2. Verificar biyección (BaselineCompletenessVerifier)
    3. Para cada documento:
       a. Cargar nodos desde disco
       b. Validar estructura (OracleValidityContract)
       c. Construir GroundTruthDraft y transicionar DRAFT → AUDITED → VALIDATED
    4. Pasar validated_drafts al SealGroundTruthUseCase (autoridad única)

    ENGINEERING_PRINCIPLES §II (Functional Core, Imperative Shell):
    el caso de uso es el Functional Core; este entry point es el Imperative
    Shell que gestiona el ciclo de vida en memoria.
    """
    base_path = pathlib.Path("tests/corpus/benchmark_v1")

    corpus_loader = LocalFileSystemCorpusLoader(base_path)
    artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path)
    reader = LocalFileSystemGroundTruthReader(base_path)

    corpus_reader: CorpusManifestReaderPort = corpus_loader
    corpus_writer: CorpusManifestWriterPort = corpus_loader

    logger.info("Loading corpus manifest and enumerating ground truth artifacts.")
    try:
        manifest_dto = corpus_reader.load_raw_manifest()
    except FileNotFoundError as e:
        logger.critical("Manifest not found. Aborting sealing: %s", str(e))
        return

    manifest_doc_ids = frozenset(d.document_id for d in manifest_dto.documents)
    artifact_doc_ids = frozenset(artifact_adapter.list_artifact_ids())

    # Verificación de completitud biyectiva (Gate 2)
    completeness_errors = BaselineCompletenessVerifier.verify(
        manifest_doc_ids, artifact_doc_ids
    )
    if completeness_errors:
        logger.critical(
            "Baseline incompleta. Sellado abortado con %d errores.",
            len(completeness_errors),
        )
        for err in completeness_errors:
            logger.critical("  - %s", err)
        return

    # Cargar, validar y transicionar cada draft
    validated_drafts: list[GroundTruthDraft] = []
    validation_errors: list[str] = []

    for doc_id in sorted(manifest_doc_ids):
        try:
            nodes = reader.load_ground_truth(doc_id)

            # Validar estructura (Gate 2)
            OracleValidityContract.validate(doc_id, nodes)

            # Construir draft directamente y transicionar DRAFT → AUDITED → VALIDATED
            draft = GroundTruthDraft(
                document_id=doc_id,
                nodes=nodes,
                sub_state=DraftSubState.DRAFT,
            )
            audited = LifecycleTransitionAuthority.audit(draft)
            validated = LifecycleTransitionAuthority.validate(audited)
            validated_drafts.append(validated)

        except OracleValidityError as e:
            validation_errors.append(str(e))
            logger.error("Oracle '%s' failed validity: %s", doc_id, str(e))

    if validation_errors:
        logger.critical(
            "Sellado abortado: %d oráculos inválidos.", len(validation_errors)
        )
        return

    # Invocar la autoridad única de sellado (NADR-14 §5.2 R4-R6)
    use_case = SealGroundTruthUseCase(
        corpus_reader=corpus_reader,
        corpus_writer=corpus_writer,
        artifact_port=artifact_adapter,
    )

    logger.info(
        "All %d oracles valid and transitioned to VALIDATED. Sealing baseline.",
        len(validated_drafts),
    )
    try:
        global_manifest_hash = use_case.execute(
            validated_drafts=tuple(validated_drafts),
            target_version="v1.0",
        )
        logger.info(
            "Cryptographic lock complete. Manifest verified under global SHA-256: %s",
            global_manifest_hash,
        )
    except BaselineContractError as e:
        logger.critical("Seal aborted by contract violation: %s", str(e))
    except Exception as e:
        logger.critical("Catastrophic lineage sealing breakdown: %s", str(e))


if __name__ == "__main__":
    main()