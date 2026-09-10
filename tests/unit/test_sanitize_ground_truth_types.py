"""Tests de proteccion GAP-5.2-05 para sanitize_ground_truth_types.py (Task 2.1.2).

Verifica:
- GAP-5.2-05: sanitize_ground_truth_types no puede modificar oraculos sellados
- NADR-21: oraculo sellado es inmutable
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.ground_truth.errors import SealedOracleOverwriteError
from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from tools.evaluation.sanitize_ground_truth_types import sanitize_corpus


_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class FakeCorpusReader:
    def __init__(self, entries: list[RawDocumentEntryDTO]):
        self._entries = entries

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        return RawCorpusManifestDTO(
            corpus_version="v1.0",
            manifest_hash="abc",
            documents=self._entries,
        )


def _make_entry(doc_id: str, state: str | None = None) -> RawDocumentEntryDTO:
    return RawDocumentEntryDTO(
        document_id=doc_id,
        sha256=_VALID_SHA256,
        traits=["native_pdf"],
        page_count=1,
        ground_truth_state=state,
    )


def _write_gt(gt_dir: Path, doc_id: str, node_type: str) -> None:
    gt_dir.mkdir(parents=True, exist_ok=True)
    content = [
        {
            "node_id": doc_id + "_n1",
            "node_type": node_type,
            "payload": {"content": "test content"},
        }
    ]
    (gt_dir / (doc_id + ".json")).write_text(json.dumps(content), encoding="utf-8")


def test_sealed_oracle_raises_overwrite_error(tmp_path: Path) -> None:
    """GAP-5.2-05: un oraculo sellado no puede ser sanitizado."""
    _write_gt(tmp_path / "ground_truth", "doc-1", "title")

    reader = FakeCorpusReader([
        _make_entry("doc-1", state=GroundTruthLifecycleState.SEALED.value)
    ])

    with pytest.raises(SealedOracleOverwriteError):
        sanitize_corpus(tmp_path, reader)


def test_draft_document_is_sanitized(tmp_path: Path) -> None:
    """Un documento en estado DRAFT se sanitiza normalmente."""
    _write_gt(tmp_path / "ground_truth", "doc-1", "title")

    reader = FakeCorpusReader([
        _make_entry("doc-1", state=GroundTruthLifecycleState.DRAFT.value)
    ])

    sanitize_corpus(tmp_path, reader)

    gt_file = tmp_path / "ground_truth" / "doc-1.json"
    content = json.loads(gt_file.read_text(encoding="utf-8"))
    assert content[0]["node_type"] == "heading"


def test_no_manifest_allows_sanitization(tmp_path: Path) -> None:
    """Sin manifest (corpus legacy), no hay sellados y se sanitiza."""
    _write_gt(tmp_path / "ground_truth", "doc-1", "footer")

    class _NoManifestReader:
        def load_raw_manifest(self) -> RawCorpusManifestDTO:
            raise FileNotFoundError("no manifest")

    sanitize_corpus(tmp_path, _NoManifestReader())

    gt_file = tmp_path / "ground_truth" / "doc-1.json"
    content = json.loads(gt_file.read_text(encoding="utf-8"))
    assert content[0]["node_type"] == "paragraph"
