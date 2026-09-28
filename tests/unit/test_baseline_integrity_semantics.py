"""Tests de semántica de fallo de integridad de la baseline.

NADR-F17BIS-26 §5.6 R23-R25, §5.7 R26-R28.

Tests unitarios que verifican:
- R24: Fallo de integridad se distingue de divergencia del pipeline.
- R25: Fallo de integridad no se interpreta como regresión.
- R26-R28: Separación de identidades (global vs individual).
"""
from __future__ import annotations

import pytest

from core.benchmark.corpus.integrity import (
    BaselineIntegrityError,
    GTUnreadableError,
    ManifestHashMismatchError,
    PdfIntegrityError,
    PdfMissingError,
)
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.topology.regression.errors import RegressionError


@pytest.mark.unit
class TestBaselineIntegrityErrorSemantics:
    """NADR-F17BIS-26 §5.6 R24-R25: Fallo de integridad ≠ regresión."""

    def test_baseline_integrity_error_is_not_regression_error(self) -> None:
        """R24: BaselineIntegrityError no es subclass de RegressionError."""
        assert not issubclass(BaselineIntegrityError, RegressionError)
        assert not issubclass(RegressionError, BaselineIntegrityError)

    def test_incomplete_baseline_error_is_not_regression_error(self) -> None:
        """R24: IncompleteBaselineError no es subclass de RegressionError."""
        assert not issubclass(IncompleteBaselineError, RegressionError)

    def test_gt_unreadable_error_is_baseline_integrity_error(self) -> None:
        """R23: GTUnreadableError es BaselineIntegrityError."""
        assert issubclass(GTUnreadableError, BaselineIntegrityError)

    def test_manifest_hash_mismatch_is_baseline_integrity_error(self) -> None:
        """R23: ManifestHashMismatchError es BaselineIntegrityError."""
        assert issubclass(ManifestHashMismatchError, BaselineIntegrityError)

    def test_pdf_integrity_error_is_baseline_integrity_error(self) -> None:
        """R23: PdfIntegrityError es BaselineIntegrityError."""
        assert issubclass(PdfIntegrityError, BaselineIntegrityError)

    def test_pdf_missing_error_is_baseline_integrity_error(self) -> None:
        """R23: PdfMissingError es BaselineIntegrityError."""
        assert issubclass(PdfMissingError, BaselineIntegrityError)

    def test_regression_error_is_not_baseline_integrity_error(self) -> None:
        """R24: RegressionError no es subclass de BaselineIntegrityError."""
        assert not issubclass(RegressionError, BaselineIntegrityError)


@pytest.mark.unit
class TestIdentitySeparation:
    """NADR-F17BIS-26 §5.7 R26-R28: Separación de identidades."""

    def test_manifest_hash_is_global_identity(self) -> None:
        """R26: manifest_hash es identidad global, no individual."""
        error = ManifestHashMismatchError(expected="a" * 64, actual="b" * 64)
        assert error.expected_hash == "a" * 64
        assert error.actual_hash == "b" * 64
        assert not hasattr(error, "document_id")

    def test_pdf_integrity_is_individual_identity(self) -> None:
        """R26: PdfIntegrityError es identidad individual, no global."""
        error = PdfIntegrityError(
            document_id="doc_01", expected="a" * 64, actual="b" * 64
        )
        assert error.document_id == "doc_01"
        assert error.expected_sha256 == "a" * 64
        assert error.actual_sha256 == "b" * 64

    def test_global_and_individual_errors_are_distinct(self) -> None:
        """R26: Identidad global e individual son tipos distintos."""
        assert ManifestHashMismatchError is not PdfIntegrityError
        assert not issubclass(ManifestHashMismatchError, PdfIntegrityError)
        assert not issubclass(PdfIntegrityError, ManifestHashMismatchError)