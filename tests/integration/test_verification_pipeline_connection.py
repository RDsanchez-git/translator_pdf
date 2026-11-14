"""Integration smoke for the *production extraction composition root*.

Exercises build_extraction_pipeline() -> PdfParserAdapter -> parse(PDF) -> AST.
A disposable, text-only PDF tests the happy path without requiring the
copyright-restricted scientific baseline. A second PDF verifies B02 fail-close.

This is NOT Continuous Verification: NADR-F17BIS-25 requires the normative
verification entry point to consume the *sealed canonical corpus* when
producing scientific regression verdicts. These fixtures never replace it.
"""
from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.execution.exceptions import LayoutRecoveryError
from infra.adapters.pdf_parser import PdfParserAdapter


@pytest.fixture
def text_only_pdf(tmp_path: Path) -> Path:
    """Representable source; keep vector drawings and external assets absent."""
    path = tmp_path / "verification_text_only.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=595, height=842)
        page.insert_text(
            (72, 100),
            "Controlled production extraction pipeline verification.",
            fontsize=11,
        )
        page.insert_text(
            (72, 140),
            "Scientific observations must remain traceable.",
            fontsize=11,
        )
        pdf.save(str(path))
    return path


@pytest.fixture
def vector_pdf(tmp_path: Path) -> Path:
    """A drawing the current PyMuPDF->Layout/AST route cannot represent."""
    path = tmp_path / "verification_vector_unrepresented.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=595, height=842)
        page.insert_text((72, 100), "Text plus an unsupported vector.", fontsize=11)
        page.draw_line(fitz.Point(100, 160), fitz.Point(230, 220))
        pdf.save(str(path))
    return path


@pytest.mark.integration
class TestVerificationPipelineConnection:
    """Smoke the actual extraction root, with positive and fail-closed PDFs."""

    def test_build_extraction_pipeline_returns_pdf_parser_adapter(self) -> None:
        """The production root builds the expected parser adapter."""
        pipeline = build_extraction_pipeline()
        assert isinstance(pipeline, PdfParserAdapter), (
            f"build_extraction_pipeline() returned {type(pipeline).__name__}, "
            "expected PdfParserAdapter"
        )

    def test_pipeline_extracts_nonempty_ast_from_text_pdf(
        self, text_only_pdf: Path,
    ) -> None:
        """The production root maps representable PDF text to nonempty AST."""
        pipeline = build_extraction_pipeline()
        nodes = pipeline.parse(str(text_only_pdf))
        assert nodes is not None
        assert len(nodes) > 0

    def test_extracted_ast_nodes_have_minimum_structure(
        self, text_only_pdf: Path,
    ) -> None:
        """Each generated AST node carries a stable identity and type."""
        nodes = build_extraction_pipeline().parse(str(text_only_pdf))
        assert len(nodes) > 0
        for i, node in enumerate(nodes):
            assert hasattr(node, "node_id"), f"Node {i} lacks node_id"
            assert hasattr(node, "node_type"), f"Node {i} lacks node_type"
            assert node.node_id is not None, f"Node {i} has no identity"

    def test_extracted_ast_is_deterministic(self, text_only_pdf: Path) -> None:
        """Parsing the same physical PDF twice yields the same node IDs."""
        pipeline = build_extraction_pipeline()
        first = pipeline.parse(str(text_only_pdf))
        second = pipeline.parse(str(text_only_pdf))
        assert first and second
        assert len(first) == len(second)
        assert [node.node_id for node in first] == [
            node.node_id for node in second
        ]

    def test_production_root_rejects_unrepresented_vector_pdf(
        self, vector_pdf: Path,
    ) -> None:
        """B02 must remain fail-closed through the production parser root."""
        pipeline = build_extraction_pipeline()
        with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
            pipeline.parse(str(vector_pdf))
