"""
Verification Pipeline Connection Tests (NADR-F17BIS-25 §5.2 R7, parcial).

Verifica que la cadena local de Continuous Verification funciona:

    build_extraction_pipeline() → PdfParserAdapter → parse(pdf) → AST

Estos tests son de integración: requieren filesystem del proyecto y
PyMuPDF instalado. No ejecutan evaluación topológica ni consumen la
baseline sellada (eso es Gate 2). Solo verifican la conexión entre
el verification entry point y el production pipeline.

NADR-F17BIS-25:
- R7 (parcial): La cadena ENTRY_POINT → PRODUCTION_PIPELINE → CANDIDATE_AST
  MUST estar completa y ser demostrable.

Nota: La parte CI de R5-R7 se verifica en Gate 3 (Task 3.2.1-3.2.3).
"""
from __future__ import annotations

import pathlib

import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from infra.adapters.pdf_parser import PdfParserAdapter

# ── Paths relativos al root del proyecto ──────────────────────────────────────
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL_PDF_DIR = PROJECT_ROOT / "tests" / "corpus" / "canonical" / "pdf"

# PDF más simple del corpus canónico (single page, trackeado en git)
SAMPLE_CANONICAL_PDF = CANONICAL_PDF_DIR / "doc_01_single.pdf"


def _require_canonical_pdf() -> pathlib.Path:
    """Retorna el path al PDF canónico de muestra, o skip si no existe.

    14 de 21 PDFs están gitignored (HITO 6.2 E-6.2-001). doc_01_single.pdf
    está trackeado en git, pero si el workspace no lo tiene, skip.
    """
    if not SAMPLE_CANONICAL_PDF.exists():
        pytest.skip(
            f"Canonical PDF not available: {SAMPLE_CANONICAL_PDF}. "
            f"This test requires the canonical corpus PDFs to be present "
            f"locally. See HITO 6.2 E-6.2-001 for materialization gaps."
        )
    return SAMPLE_CANONICAL_PDF


# ── Tests: Conexión Entry Point → Production Pipeline ─────────────────────────


@pytest.mark.integration
class TestVerificationPipelineConnection:
    """NADR-F17BIS-25 §5.2 R7 (parcial): la conexión local
    build_extraction_pipeline() → parse(pdf) → AST funciona."""

    def test_build_extraction_pipeline_returns_pdf_parser_adapter(self) -> None:
        """build_extraction_pipeline() retorna un PdfParserAdapter funcional.

        Verifica que la composition root canónica produce el tipo esperado
        sin invocar I/O externo (no se parsea ningún PDF en este test).
        """
        pipeline = build_extraction_pipeline()
        assert isinstance(pipeline, PdfParserAdapter), (
            f"build_extraction_pipeline() returned "
            f"{type(pipeline).__name__}, expected PdfParserAdapter. "
            f"NADR-F17BIS-25 §5.1 R1 requires the verification subject to "
            f"be the production pipeline canonical composition root."
        )

    def test_pipeline_extracts_nonempty_ast_from_canonical_pdf(self) -> None:
        """El pipeline extrae un AST no vacío de un PDF del corpus canónico.

        Verifica que la cadena parse() → AST funciona con un documento real.
        No verifica contra la baseline sellada (eso es Gate 2).
        """
        pdf_path = _require_canonical_pdf()
        pipeline = build_extraction_pipeline()

        nodes = pipeline.parse(str(pdf_path))

        assert nodes is not None, (
            "pipeline.parse() returned None. "
            "NADR-F17BIS-25 §5.2 R7 requires a complete chain from "
            "production pipeline to candidate AST."
        )
        assert len(nodes) > 0, (
            f"pipeline.parse() returned empty AST for {pdf_path.name}. "
            f"The production pipeline must produce a non-empty candidate AST "
            f"for a valid PDF document."
        )

    def test_extracted_ast_nodes_have_minimum_structure(self) -> None:
        """Los nodos del AST extraído tienen la estructura mínima esperada.

        Verifica que cada nodo tiene los atributos fundamentales de ASTNode
        (node_id, node_type) sin acoplarse a la implementación completa.
        """
        pdf_path = _require_canonical_pdf()
        pipeline = build_extraction_pipeline()

        nodes = pipeline.parse(str(pdf_path))

        assert len(nodes) > 0, "Expected non-empty AST"

        for i, node in enumerate(nodes):
            assert hasattr(node, "node_id"), (
                f"Node {i} lacks 'node_id' attribute. "
                f"AST nodes must have a stable identifier."
            )
            assert hasattr(node, "node_type"), (
                f"Node {i} lacks 'node_type' attribute. "
                f"AST nodes must declare their type."
            )
            assert node.node_id is not None, (
                f"Node {i} has None node_id."
            )

    def test_extracted_ast_is_deterministic(self) -> None:
        """Dos ejecuciones sobre el mismo PDF producen el mismo AST.

        Verifica determinismo (ADR_F17_BIS_MASTER §5: Determinismo y
        Reproducibilidad). El AST no debe variar entre ejecuciones.
        """
        pdf_path = _require_canonical_pdf()
        pipeline = build_extraction_pipeline()

        nodes_first = pipeline.parse(str(pdf_path))
        nodes_second = pipeline.parse(str(pdf_path))

        assert len(nodes_first) == len(nodes_second), (
            f"AST node count differs between executions: "
            f"{len(nodes_first)} vs {len(nodes_second)}. "
            f"The production pipeline must be deterministic."
        )

        ids_first = [n.node_id for n in nodes_first]
        ids_second = [n.node_id for n in nodes_second]
        assert ids_first == ids_second, (
            "AST node IDs differ between executions on the same PDF. "
            "The production pipeline must be deterministic."
        )