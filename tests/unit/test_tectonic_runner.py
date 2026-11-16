# tests/unit/test_tectonic_runner.py
"""
Tests de contrato para HostTectonicRunner.
NADR-09 §5.2 R6: I/O aislado en espacio efímero.
NADR-09 §5.2 R9: Nomenclatura veraz.
"""
import os
import tempfile
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from apps.compiler.tectonic_runner import HostTectonicRunner


class TestHostTectonicRunner:

    def _make_runner(self) -> HostTectonicRunner:
        return HostTectonicRunner()

    def test_successful_compilation_writes_to_output_dir(self):
        """El PDF se persiste en output_dir explícito."""
        runner = self._make_runner()

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("apps.compiler.tectonic_runner.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")

                # Simular que tectonic crea doc.pdf en el sandbox
                def fake_run(*args, **kwargs):
                    cwd = kwargs.get("cwd")
                    if cwd:
                        pdf_path = os.path.join(cwd, "doc.pdf")
                        with open(pdf_path, "wb") as f:
                            f.write(b"%PDF-1.4 fake")
                    return MagicMock(returncode=0, stderr="")

                mock_run.side_effect = fake_run

                result = runner.compile(
                    tex_content=r"\documentclass{article}\begin{document}test\end{document}",
                    output_dir=output_dir,
                    output_filename="test.pdf"
                )

                assert os.path.basename(result) == "test.pdf"
                assert result.startswith(output_dir)
                assert os.path.exists(result)

    def test_compilation_runs_in_sandbox_cwd(self):
        """Tectonic se ejecuta con cwd=sandbox, no con os.getcwd()."""
        runner = self._make_runner()

        with tempfile.TemporaryDirectory() as output_dir:
            captured_cwd = []

            def capture_run(*args, **kwargs):
                captured_cwd.append(kwargs.get("cwd"))
                cwd = kwargs.get("cwd")
                if cwd:
                    with open(os.path.join(cwd, "doc.pdf"), "wb") as f:
                        f.write(b"%PDF")
                return MagicMock(returncode=0, stderr="")

            with patch("apps.compiler.tectonic_runner.subprocess.run", side_effect=capture_run):
                runner.compile(r"\documentclass{article}\begin{document}x\end{document}", output_dir=output_dir)

            # El cwd debe ser un directorio temporal, no el cwd del proceso
            assert len(captured_cwd) == 1
            assert captured_cwd[0] != os.getcwd()
            assert captured_cwd[0] is not None

    def test_no_crash_log_written_to_cwd(self, monkeypatch, tmp_path):
        """No se escribe tectonic_crash.log en el cwd temporal del test."""
        runner = self._make_runner()

        # El CWD del test es descartable; jamás borrar el log ajeno del owner.
        monkeypatch.chdir(tmp_path)
        crash_log = tmp_path / "tectonic_crash.log"
        assert not crash_log.exists()

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("apps.compiler.tectonic_runner.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="some error")

                with pytest.raises(Exception, match="Fallo de Tectonic"):
                    runner.compile(r"\documentclass{article}", output_dir=output_dir)

        assert not crash_log.exists(), (
            "tectonic_crash.log no debe existir en cwd. "
            "NADR-09 §5.2 R6: el runner no escribe en el directorio del proceso."
        )

    def test_tectonic_failure_propagates(self):
        """Exit code non-zero de tectonic propaga excepción."""
        runner = self._make_runner()

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("apps.compiler.tectonic_runner.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="Fatal error")

                try:
                    runner.compile(r"\documentclass{article}", output_dir=output_dir)
                    assert False, "Should have raised Exception"
                except Exception as e:
                    assert "Fallo de Tectonic" in str(e)

    def test_timeout_propagates(self):
        """Timeout de tectonic propaga excepción."""
        runner = self._make_runner()

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("apps.compiler.tectonic_runner.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(cmd="tectonic", timeout=120)

                try:
                    runner.compile(r"\documentclass{article}", output_dir=output_dir)
                    assert False, "Should have raised Exception"
                except Exception as e:
                    assert "Timeout" in str(e)

    def test_output_dir_required(self):
        """output_dir es obligatorio (sin default)."""
        runner = self._make_runner()
        import inspect
        sig = inspect.signature(runner.compile)
        output_dir_param = sig.parameters["output_dir"]
        assert output_dir_param.default is inspect.Parameter.empty, \
            "output_dir no debe tener default"