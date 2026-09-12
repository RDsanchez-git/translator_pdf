"""Tests de semantica de salida DF-18 y guard de traduccion (NADR-24 R15-R19)."""
from __future__ import annotations

import pytest

from core.benchmark.ground_truth.errors import SealedOracleOverwriteError
from core.shared.errors import IndexedError
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from tools.evaluation.entry_guard import run_entry
from tools.evaluation.generate_golden_draft import classify_document_error


class TestRunEntryTranslation:
    def test_indexed_error_translates_to_exit_2(self):
        def boom() -> int:
            raise IndexedError("X-001", "fallo")

        with pytest.raises(SystemExit) as exc:
            run_entry(boom)
        assert exc.value.code == EXIT_EXECUTION_FAILURE

    def test_generic_exception_translates_to_exit_2(self):
        def boom() -> int:
            raise RuntimeError("inesperado")

        with pytest.raises(SystemExit) as exc:
            run_entry(boom)
        assert exc.value.code == EXIT_EXECUTION_FAILURE

    def test_main_int_passes_through(self):
        with pytest.raises(SystemExit) as exc:
            run_entry(lambda: EXIT_OK)
        assert exc.value.code == EXIT_OK


class TestClassifyDocumentError:
    def test_sealed_oracle_is_skip(self):
        assert classify_document_error(SealedOracleOverwriteError("doc")) == "skip"

    def test_other_errors_are_failure(self):
        assert classify_document_error(FileNotFoundError("pdf")) == "failure"
        assert classify_document_error(RuntimeError("x")) == "failure"
