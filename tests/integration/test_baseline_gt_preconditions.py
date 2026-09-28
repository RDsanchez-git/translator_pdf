"""Tests de precondiciones de Ground Truths (NADR-F17BIS-26 §5.3 R13-R14).

Tests de integración que verifican que los Ground Truths son legibles
antes de la evaluación. Requieren filesystem temporal (tmp_path).
"""
from __future__ import annotations

import pathlib

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.integrity import GTUnreadableError
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.ground_truth.use_cases import LoadGroundTruthUseCase
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthReader
from infra.serialization.ast_json import write_ast_json_atomic
from tools.evaluation.run_regression import verify_ground_truth_preconditions


def _make_node() -> ASTNode:
    """Crea un ASTNode mínimo válido para tests."""
    return ASTNode(
        node_id="test-node-001",
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content="test content"),
        sequence_id=1,
    )


def _make_manifest(doc_ids: list[str]) -> CorpusManifest:
    """Crea un manifest con los document_ids dados."""
    docs = [
        CorpusDocumentMetadata(
            document_id=doc_id,
            fingerprint=DocumentFingerprint(sha256="a" * 64),
            traits=frozenset({ExtractionChallengeTrait.HEAVY_MATH}),
            page_count=1,
        )
        for doc_id in doc_ids
    ]
    return CorpusManifest(
        corpus_version=CorpusVersion(value="test-v1"),
        documents=docs,
    )


@pytest.mark.integration
class TestVerifyGroundTruthPreconditions:
    """NADR-F17BIS-26 §5.3 R13-R14: Precondiciones de GTs."""

    def test_passes_with_valid_gt(self, tmp_path: pathlib.Path) -> None:
        """GT válido → no lanza excepción."""
        corpus_dir = tmp_path / "corpus"
        gt_dir = corpus_dir / "ground_truth"
        gt_dir.mkdir(parents=True)
        write_ast_json_atomic([_make_node()], gt_dir / "doc_01.json", indent=2)

        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        manifest = _make_manifest(["doc_01"])
        verify_ground_truth_preconditions(load_gt_uc, manifest)

    def test_raises_on_missing_gt(self, tmp_path: pathlib.Path) -> None:
        """R13: GT ausente → GTUnreadableError."""
        corpus_dir = tmp_path / "corpus"
        gt_dir = corpus_dir / "ground_truth"
        gt_dir.mkdir(parents=True)

        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        manifest = _make_manifest(["doc_01"])

        with pytest.raises(GTUnreadableError, match="unreadable"):
            verify_ground_truth_preconditions(load_gt_uc, manifest)

    def test_raises_on_corrupt_gt(self, tmp_path: pathlib.Path) -> None:
        """R13: GT corrupto (JSON inválido) → GTUnreadableError."""
        corpus_dir = tmp_path / "corpus"
        gt_dir = corpus_dir / "ground_truth"
        gt_dir.mkdir(parents=True)
        (gt_dir / "doc_01.json").write_text("{invalid json", encoding="utf-8")

        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        manifest = _make_manifest(["doc_01"])

        with pytest.raises(GTUnreadableError, match="unreadable"):
            verify_ground_truth_preconditions(load_gt_uc, manifest)

    def test_error_contains_document_id(self, tmp_path: pathlib.Path) -> None:
        """El mensaje de error contiene el document_id."""
        corpus_dir = tmp_path / "corpus"
        gt_dir = corpus_dir / "ground_truth"
        gt_dir.mkdir(parents=True)

        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        manifest = _make_manifest(["doc_42"])

        with pytest.raises(GTUnreadableError) as exc_info:
            verify_ground_truth_preconditions(load_gt_uc, manifest)
        assert exc_info.value.document_id == "doc_42"