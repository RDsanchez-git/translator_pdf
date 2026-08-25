"""Tests del verificador de completitud biyectiva (Wave 2.2).

Verifica NADR-F17BIS-13 §5.2 R4-R8 (Zero Partial Sealing).
"""

from __future__ import annotations

from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier


class TestBaselineCompletenessVerifier:
    def test_complete_bijection_returns_empty_list(self) -> None:
        manifest = frozenset({"doc-1", "doc-2"})
        artifacts = frozenset({"doc-1", "doc-2"})
        errors = BaselineCompletenessVerifier.verify(manifest, artifacts)
        assert errors == []

    def test_missing_oracle_reports_error(self) -> None:
        manifest = frozenset({"doc-1", "doc-2"})
        artifacts = frozenset({"doc-1"})
        errors = BaselineCompletenessVerifier.verify(manifest, artifacts)
        assert len(errors) == 1
        assert "Missing oracle for manifest document: doc-2" in errors[0]

    def test_orphan_oracle_reports_error(self) -> None:
        manifest = frozenset({"doc-1"})
        artifacts = frozenset({"doc-1", "doc-orphan"})
        errors = BaselineCompletenessVerifier.verify(manifest, artifacts)
        assert len(errors) == 1
        assert "Orphan oracle (not in manifest): doc-orphan" in errors[0]

    def test_missing_and_orphan_report_both_errors(self) -> None:
        manifest = frozenset({"doc-1", "doc-missing"})
        artifacts = frozenset({"doc-1", "doc-orphan"})
        errors = BaselineCompletenessVerifier.verify(manifest, artifacts)
        assert len(errors) == 2

    def test_errors_are_deterministically_sorted(self) -> None:
        manifest = frozenset({"b-doc", "a-doc", "c-doc"})
        artifacts = frozenset()
        errors = BaselineCompletenessVerifier.verify(manifest, artifacts)
        # Los faltantes deben estar ordenados alfabéticamente (determinismo)
        assert errors[0].endswith("a-doc")
        assert errors[1].endswith("b-doc")
        assert errors[2].endswith("c-doc")

    def test_empty_manifest_and_empty_artifacts_is_complete(self) -> None:
        errors = BaselineCompletenessVerifier.verify(frozenset(), frozenset())
        assert errors == []