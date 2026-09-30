"""Helper de ejecución de Continuous Verification vía subprocess.

Representa fielmente lo que observa CI: el exit code del proceso
`python -m tools.evaluation.run_regression`. NADR-F17BIS-27 §5.6 R32:
sys.exit propaga el exit code sin reinterpretar; GitHub Actions trata
exit != 0 como failure del check.

SSOT del mecanismo de invocación para tests de paths end-to-end
(Wave 4.2). No duplica lógica de construcción de baseline: los tests
preparan su propio corpus en tmp_path o usan el canónico.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CORPUS_DIR = REPO_ROOT / "tests" / "corpus" / "canonical"
PDF_DIR = CORPUS_DIR / "pdf"


def run_cv(
    profile: str,
    corpus_dir: Path,
    pdf_dir: Path,
    output_dir: Path,
    timeout: int = 600,
) -> subprocess.CompletedProcess[str]:
    """Ejecuta el entry point de CV como subprocess y retorna el proceso.

    Args:
        profile: "FULL" o "SMOKE".
        corpus_dir: Directorio del corpus (manifest.json + ground_truth/).
        pdf_dir: Directorio de PDFs (puede no existir para failure paths).
        output_dir: Directorio de salida para reportes.
        timeout: Timeout de seguridad en segundos.

    Returns:
        CompletedProcess con returncode, stdout y stderr reales.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.evaluation.run_regression",
            "--corpus-dir",
            str(corpus_dir),
            "--pdf-dir",
            str(pdf_dir),
            "--output-dir",
            str(output_dir),
            "--profile",
            profile,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_cv_report(output_dir: Path) -> dict[str, Any]:
    """Carga el único ContinuousVerificationReport JSON persistido.

    NADR-F17BIS-28 §5.4 R21: filename único por ejecución; debe existir
    exactamente uno en output_dir.
    """
    files = sorted(output_dir.glob("regression_report_*.json"))
    assert len(files) == 1, (
        f"Esperado exactamente 1 CV report en {output_dir}, "
        f"encontrados {len(files)}: {[f.name for f in files]}"
    )
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data