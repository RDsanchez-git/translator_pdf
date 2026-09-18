"""tools/evaluation/curate_gt.py — Imperative Shell delgado (Batch 2a).

Escritor operacional de <corpus-dir>/curation_checklist.json, el mecanismo de
gate de curaduria pre-sellado (NADR-21 §5.1 R5) que lee freeze_ground_truth.py
(Batch 1, H-5.5-7). El registro durable de la curaduria es el Curation Report
(destino de report_ref); el checklist es estado operacional excluido de toda
identidad y del repo (.gitignore), conforme Register v0.21.0.

Frontera: NO escribe Ground Truths ni importa autoridades de ciclo de vida;
solo lee el manifest (existencia + estado de sellado) y escribe el checklist
en la raiz del corpus (precedente: lineage en canonical/, H-5.2-3).
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("curate_gt")

CHECKLIST_FILENAME = "curation_checklist.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Registro operacional de curaduria pre-sellado (Batch 2a, H-5.5-7)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus canonico.")
    parser.add_argument("--doc-id", type=str, required=True,
                        help="Identidad del documento a registrar.")
    parser.add_argument("--status", type=str, choices=["CURATED", "PENDING"], default="CURATED",
                        help="Estado de curaduria a registrar (default: CURATED).")
    parser.add_argument("--report-ref", type=str, default=None,
                        help="Referencia al Curation Report (obligatoria si --status CURATED).")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    corpus_dir: Path = args.corpus_dir
    doc_id: str = args.doc_id
    status: str = args.status
    report_ref: str | None = args.report_ref

    if status == "CURATED" and not (report_ref or "").strip():
        logger.critical(
            "[CURATE-004] --report-ref vacio o ausente con --status CURATED para '%s'. "
            "remediation: pasar --report-ref con la seccion del Curation Report que evidencia la curaduria.",
            doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    if status == "PENDING" and report_ref:
        logger.warning(
            "[CURATE-W01] --report-ref provisto con --status PENDING para '%s'; se ignora "
            "(report_ref y curated_at solo existen al curar).",
            doc_id,
        )

    loader = LocalFileSystemCorpusLoader(corpus_dir)
    try:
        manifest_dto = loader.load_raw_manifest()
    except FileNotFoundError as exc:
        logger.critical(
            "[CURATE-001] manifest no resoluble en %s (%s) para doc '%s'. "
            "remediation: verificar --corpus-dir o ejecutar paso 2 del runbook (add_document_to_corpus).",
            corpus_dir, exc, doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    entry = next((d for d in manifest_dto.documents if d.document_id == doc_id), None)
    if entry is None:
        logger.critical(
            "[CURATE-001] doc '%s' ausente en manifest de %s. "
            "remediation: registrar la identidad con add_document_to_corpus (paso 2) antes de curar.",
            doc_id, corpus_dir,
        )
        return EXIT_EXECUTION_FAILURE

    if entry.ground_truth_state == GroundTruthLifecycleState.SEALED.value:
        logger.critical(
            "[CURATE-003] doc '%s' ya esta sellado; la curaduria es pre-sellado (NADR-21 §5.1 R5). "
            "remediation: una correccion post-sellado exige nueva version del artefacto y repetir "
            "lifecycle de elegibilidad y sealing (Rollback Plan Gate 2).",
            doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    checklist_path = corpus_dir / CHECKLIST_FILENAME
    checklist: dict[str, Any] = {}
    if checklist_path.exists():
        try:
            raw = json.loads(checklist_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("raiz del checklist no es un objeto JSON")
            checklist = raw
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            logger.critical(
                "[CURATE-002] curation_checklist.json corrupto o ilegible en %s (%s). "
                "remediation: reconstruir el checklist desde el Curation Report (registro durable) "
                "o eliminar el archivo corrupto y re-registrar las entradas.",
                checklist_path, exc,
            )
            return EXIT_EXECUTION_FAILURE

    if status == "CURATED":
        new_entry: dict[str, Any] = {
            "status": "CURATED",
            "report_ref": report_ref,
            "curated_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        new_entry = {"status": "PENDING", "report_ref": None, "curated_at": None}
    checklist[doc_id] = new_entry
    checklist_path.write_text(
        json.dumps(checklist, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "[CURATE-OK] doc '%s' registrado como %s en %s (report_ref=%s).",
        doc_id, status, checklist_path, report_ref if status == "CURATED" else "n/a",
    )
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)