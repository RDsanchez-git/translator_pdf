"""tools/evaluation/canonicalize_gt.py — Imperative Shell (Batch 2a hardening).

Reescritura determinista de node_ids legacy ("value='pX_bY'" -> "pX_bY") en un
Ground Truth DRAFT, con lineage por documento en la raiz del corpus (leccion
H-5.2-3: nunca dentro de ground_truth/).

Codigos indexables (Batch 2a):
  [CANON-001] manifest o GT no resoluble     -> exit 2
  [CANON-002] colision de node_ids canonicos -> exit 2
  [CANON-003] documento sellado              -> exit 2 (NADR-21 §5.4 R19/R25)
  [CANON-OK]  legacy auto-corregido con lineage; sin legacy = no-op (R33)
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Sequence

from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from tools.evaluation.entry_guard import run_entry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("canonicalize_gt")

LEGACY_NODE_ID = re.compile(r"^value='([^']+)'$")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Canonicalizacion de node_ids legacy en un GT DRAFT (Batch 2a)."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True,
                        help="Directorio raiz del corpus canonico.")
    parser.add_argument("--doc-id", type=str, required=True,
                        help="Identidad del documento a canonicalizar.")
    return parser.parse_args(argv)


def _canonical(value: str) -> str | None:
    match = LEGACY_NODE_ID.match(value)
    return match.group(1) if match else None


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    corpus_dir: Path = args.corpus_dir
    doc_id: str = args.doc_id

    loader = LocalFileSystemCorpusLoader(corpus_dir)
    try:
        manifest_dto = loader.load_raw_manifest()
    except FileNotFoundError as exc:
        logger.critical(
            "[CANON-001] manifest no resoluble en %s (%s). "
            "remediation: verificar --corpus-dir o ejecutar paso 2 del runbook (add_document_to_corpus).",
            corpus_dir, exc,
        )
        return EXIT_EXECUTION_FAILURE

    entry = next((d for d in manifest_dto.documents if d.document_id == doc_id), None)
    if entry is None:
        logger.critical(
            "[CANON-001] doc '%s' ausente en manifest. "
            "remediation: registrar identidad con add_document_to_corpus (paso 2).",
            doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    if entry.ground_truth_state == GroundTruthLifecycleState.SEALED.value:
        logger.critical(
            "[CANON-003] doc '%s' sellado; canonicalizar post-sellado violaria inmutabilidad "
            "(NADR-21 §5.4 R19/R25). remediation: nueva version del artefacto y repetir "
            "lifecycle de elegibilidad y sealing (Rollback Plan Gate 2).",
            doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    gt_path = corpus_dir / "ground_truth" / f"{doc_id}.json"
    if not gt_path.exists():
        logger.critical(
            "[CANON-001] GT ausente en %s. remediation: ejecutar paso 3 del runbook (generate_golden_draft).",
            gt_path,
        )
        return EXIT_EXECUTION_FAILURE
    try:
        nodes: list[dict[str, Any]] = json.loads(gt_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.critical(
            "[CANON-001] GT ilegible en %s (%s). remediation: re-generar draft (paso 3).",
            gt_path, exc,
        )
        return EXIT_EXECUTION_FAILURE

    lineage: list[dict[str, str]] = []
    for node in nodes:
        nid = node.get("node_id")
        if isinstance(nid, str):
            canon = _canonical(nid)
            if canon is not None:
                lineage.append({"old_id": nid, "new_id": canon})
                node["node_id"] = canon
        md = node.get("metadata")
        if isinstance(md, dict):
            pid = md.get("parent_node_id")
            if isinstance(pid, str):
                pcanon = _canonical(pid)
                if pcanon is not None:
                    md["parent_node_id"] = pcanon

    ids = [n.get("node_id") for n in nodes]
    if len(ids) != len(set(ids)):
        logger.critical(
            "[CANON-002] colision de node_ids post-canonicalizacion en '%s'. "
            "remediation: curaduria manual del draft (paso 5) para desambiguar ids duplicados antes de sellar.",
            doc_id,
        )
        return EXIT_EXECUTION_FAILURE

    if not lineage:
        logger.info("[CANON-OK] doc '%s': 0 node_ids legacy; no-op idempotente (R33).", doc_id)
        return EXIT_OK

    gt_path.write_text(json.dumps(nodes, indent=2, ensure_ascii=False), encoding="utf-8")
    lineage_path = corpus_dir / f"{doc_id}_canonicalization_lineage.json"
    lineage_path.write_text(json.dumps(lineage, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(
        "[CANON-OK] doc '%s': %d/%d node_ids canonicalizados; lineage en %s.",
        doc_id, len(lineage), len(nodes), lineage_path,
    )
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)