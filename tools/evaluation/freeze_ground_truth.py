import json  # B1-NEW: gate O2 de curaduria (H-5.5-7)
import logging
from pathlib import Path
from typing import Sequence
import argparse

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
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("freeze_ground_truth")


# B1-NEW BEGIN — gate O2 de curaduria (H-5.5-7)
def _check_curation_gate(
    pending_doc_ids: Sequence[str],
    checklist_path: Path,
    allow_uncurated: bool,
) -> tuple[bool, str | None, list[str]]:
    """Verifica gate de curaduria sobre drafts pendientes.

    Retorna (ok, error_code, warning_doc_ids).
    - ok=True: el gate paso (o no aplica)
    - error_code: "FREEZE-GT-001" (checklist ausente) / "FREEZE-GT-002" (entrada invalida) / None
    - warning_doc_ids: lista de doc_ids sin CURATED cuando allow_uncurated=True
    """
    if not pending_doc_ids:
        return (True, None, [])

    if not checklist_path.exists():
        if allow_uncurated:
            # D2/R26: el override explicito cubre tambien la ausencia del
            # checklist; todos los drafts pendientes se reportan en el
            # warning indexable [FREEZE-W01] y el sellado continua.
            return (True, None, list(pending_doc_ids))
        return (False, "FREEZE-GT-001", [])

    try:
        with checklist_path.open("r", encoding="utf-8") as fh:
            checklist = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.critical(
            "[FREEZE-GT-001] curation_checklist.json corrupto o ilegible: %s", str(exc)
        )
        return (False, "FREEZE-GT-001", [])

    uncurated: list[str] = []
    for doc_id in pending_doc_ids:
        entry = checklist.get(doc_id)
        if (
            not isinstance(entry, dict)
            or entry.get("status") != "CURATED"
            or not entry.get("report_ref")
        ):
            uncurated.append(doc_id)

    if not uncurated:
        return (True, None, [])

    if allow_uncurated:
        return (True, None, uncurated)

    return (False, "FREEZE-GT-002", uncurated)
# B1-NEW END


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sellado de Ground Truths (GAP-5.0-03, NADR-24 R10)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus canonico sellado.")
    # B1-NEW: override para ejecucion no certificante (D2/R26)
    parser.add_argument(
        "--allow-uncurated",
        action="store_true",
        help="Bypasea el gate de curaduria (H-5.5-7) con warning indexable. "
             "Uso legitimo: re-sellado de corpus completo tras re-baseline.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Imperative Shell. Orquesta el ciclo de vida en memoria.

    Secuencia atomica (sin I/O intermedio entre verificar y transicionar):
    1. Cargar manifiesto + enumerar artefactos
    2. Verificar biyeccion (BaselineCompletenessVerifier)
    3. Gate de curaduria sobre drafts pendientes (H-5.5-7)   # B1-NEW
    4. Para cada documento:
       a. Cargar nodos desde disco
       b. Validar estructura (OracleValidityContract)
       c. Construir GroundTruthDraft y transicionar DRAFT -> AUDITED -> VALIDATED
    5. Pasar validated_drafts al SealGroundTruthUseCase (autoridad unica)

    ENGINEERING_PRINCIPLES SSII (Functional Core, Imperative Shell):
    el caso de uso es el Functional Core; este entry point es el Imperative
    Shell que gestiona el ciclo de vida en memoria.
    """
    args = parse_args(argv)
    base_path: Path = args.corpus_dir

    corpus_loader = LocalFileSystemCorpusLoader(base_path)
    artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path)
    reader = LocalFileSystemGroundTruthReader(base_path)

    corpus_reader: CorpusManifestReaderPort = corpus_loader
    corpus_writer: CorpusManifestWriterPort = corpus_loader

    logger.info("Loading corpus manifest and enumerating ground truth artifacts.")
    try:
        manifest_dto = corpus_reader.load_raw_manifest()
    except FileNotFoundError as e:
        logger.critical("[FREEZE-001] Manifest not found. Aborting sealing: %s", str(e))
        return EXIT_EXECUTION_FAILURE

    manifest_doc_ids = frozenset(d.document_id for d in manifest_dto.documents)
    artifact_doc_ids = frozenset(artifact_adapter.list_artifact_ids())

    # Verificacion de completitud biyectiva (Gate 2)
    completeness_errors = BaselineCompletenessVerifier.verify(
        manifest_doc_ids, artifact_doc_ids
    )
    if completeness_errors:
        logger.critical(
            "[FREEZE-004] Baseline incompleta. Sellado abortado con %d errores.",
            len(completeness_errors),
        )
        for err in completeness_errors:
            logger.critical("  - %s", err)
        return EXIT_EXECUTION_FAILURE

    # B1-NEW BEGIN — gate O2 de curaduria (H-5.5-7)
    pending_doc_ids = [
        d.document_id
        for d in manifest_dto.documents
        if d.ground_truth_state is None
    ]
    checklist_path = base_path / "curation_checklist.json"
    gate_ok, error_code, warning_ids = _check_curation_gate(
        pending_doc_ids=pending_doc_ids,
        checklist_path=checklist_path,
        allow_uncurated=args.allow_uncurated,
    )
    if not gate_ok:
        if error_code == "FREEZE-GT-001":
            logger.critical(
                "[FREEZE-GT-001] curation_checklist.json ausente en %s con %d drafts "
                "pendientes. remediation: crear checklist via verbo `curate` (paso 5 "
                "del runbook de FASE_5_BENCHMARK_METHODOLOGY).",
                checklist_path,
                len(pending_doc_ids),
            )
        else:  # FREEZE-GT-002
            logger.critical(
                "[FREEZE-GT-002] %d drafts sin curaduria registrada: %s. "
                "remediation: registrar curaduria en curation_checklist.json con "
                "status=CURATED y report_ref al Curation Report (verbo `curate`).",
                len(warning_ids),
                ", ".join(warning_ids),
            )
        return EXIT_EXECUTION_FAILURE
    if warning_ids:
        logger.warning(
            "[FREEZE-W01] --allow-uncurated activo: %d drafts sin curaduria "
            "registrada (%s). Sellado continua fuera de ejecucion certificante.",
            len(warning_ids),
            ", ".join(warning_ids),
        )
    # B1-NEW END

    # Cargar, validar y transicionar cada draft
    validated_drafts: list[GroundTruthDraft] = []
    validation_errors: list[str] = []

    for doc_id in sorted(manifest_doc_ids):
        try:
            nodes = reader.load_ground_truth(doc_id)

            # Validar estructura (Gate 2)
            OracleValidityContract.validate(doc_id, nodes)

            # Construir draft directamente y transicionar DRAFT -> AUDITED -> VALIDATED
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
            "[FREEZE-005] Sellado abortado: %d oraculos invalidos.", len(validation_errors)
        )
        return EXIT_EXECUTION_FAILURE

    # Invocar la autoridad unica de sellado (NADR-14 SS5.2 R4-R6)
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
        )
        logger.info(
            "Cryptographic lock complete. Manifest verified under global SHA-256: %s",
            global_manifest_hash,
        )
    except BaselineContractError as e:
        logger.critical("[FREEZE-002] Seal aborted by contract violation: %s", str(e))
        return EXIT_EXECUTION_FAILURE
    except Exception as e:
        logger.critical("[FREEZE-003] Catastrophic lineage sealing breakdown: %s", str(e))
        return EXIT_EXECUTION_FAILURE

    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)