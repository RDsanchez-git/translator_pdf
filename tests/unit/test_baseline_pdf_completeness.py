"""Tests de completitud biyectiva manifest ↔ PDFs (NADR-F17BIS-26 §5.3 R11-R12).

Tests unitarios para BaselineCompletenessVerifier.verify_pdf_ids().
Función pura, sin I/O.
"""
from __future__ import annotations

import pytest

from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier


@pytest.mark.unit
class TestVerifyPdfIds:
    """NADR-F17BIS-26 §5.3 R11-R12: Completitud biyectiva manifest ↔ PDFs."""

    def test_complete_bijection_returns_empty(self) -> None:
        """Biyección completa → lista vacía."""
        manifest_ids = frozenset({"doc_01", "doc_02", "doc_03"})
        pdf_ids = frozenset({"doc_01", "doc_02", "doc_03"})
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_ids, pdf_doc_ids=pdf_ids,
        )
        assert errors == []

    def test_missing_pdf_reports_error(self) -> None:
        """PDF faltante → error."""
        manifest_ids = frozenset({"doc_01", "doc_02"})
        pdf_ids = frozenset({"doc_01"})
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_ids, pdf_doc_ids=pdf_ids,
        )
        assert len(errors) == 1
        assert "Missing PDF" in errors[0]
        assert "doc_02" in errors[0]

    def test_orphan_pdf_reports_error(self) -> None:
        """PDF orfano → error."""
        manifest_ids = frozenset({"doc_01"})
        pdf_ids = frozenset({"doc_01", "doc_extra"})
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_ids, pdf_doc_ids=pdf_ids,
        )
        assert len(errors) == 1
        assert "Orphan PDF" in errors[0]
        assert "doc_extra" in errors[0]

    def test_missing_and_orphan_report_both(self) -> None:
        """Faltante y orfano → ambos reportados."""
        manifest_ids = frozenset({"doc_01", "doc_02"})
        pdf_ids = frozenset({"doc_01", "doc_extra"})
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_ids, pdf_doc_ids=pdf_ids,
        )
        assert len(errors) == 2
        assert any("Missing PDF" in e and "doc_02" in e for e in errors)
        assert any("Orphan PDF" in e and "doc_extra" in e for e in errors)

    def test_errors_are_deterministically_sorted(self) -> None:
        """Los errores están ordenados determinísticamente."""
        manifest_ids = frozenset({"doc_03", "doc_01"})
        pdf_ids = frozenset({"doc_02", "doc_04"})
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_ids, pdf_doc_ids=pdf_ids,
        )
        assert errors[0] == "Missing PDF for manifest document: doc_01"
        assert errors[1] == "Missing PDF for manifest document: doc_03"
        assert errors[2] == "Orphan PDF (not in manifest): doc_02"
        assert errors[3] == "Orphan PDF (not in manifest): doc_04"

    def test_empty_both_is_complete(self) -> None:
        """Ambos conjuntos vacíos → completo."""
        errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=frozenset(), pdf_doc_ids=frozenset(),
        )
        assert errors == []