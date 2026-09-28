"""Tests de _get_subject_identity (NADR-F17BIS-28 §5.1 R3, §5.5 R29)."""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

import pytest

from tools.evaluation.run_regression import _get_subject_identity


@pytest.mark.unit
class TestGetSubjectIdentity:
    """NADR-F17BIS-28 §5.1 R3: identidad del sujeto via git."""

    def test_returns_sha_when_git_available(self, monkeypatch) -> None:
        """Git accesible → retorna commit SHA."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456\n"

        def mock_run(*args, **kwargs):
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert _get_subject_identity() == "abc123def456"

    def test_returns_none_when_git_fails(self, monkeypatch) -> None:
        """Git retorna error → None (limitación observable)."""
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""

        def mock_run(*args, **kwargs):
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert _get_subject_identity() is None

    def test_returns_none_on_os_error(self, monkeypatch) -> None:
        """Git no existe (OSError) → None."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert _get_subject_identity() is None

    def test_returns_none_on_timeout(self, monkeypatch) -> None:
        """Timeout → None."""
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="git", timeout=10)

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert _get_subject_identity() is None

    def test_returns_none_when_stdout_empty(self, monkeypatch) -> None:
        """Git retorna éxito pero stdout vacío → None."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "   \n"

        def mock_run(*args, **kwargs):
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert _get_subject_identity() is None