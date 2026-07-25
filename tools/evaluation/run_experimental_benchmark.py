"""
tools/evaluation/run_experimental_benchmark.py

[DEPRECATED] Script experimental de evaluación topológica.
Redirige de forma transparente al entrypoint unificado run_benchmark.py.
"""

import sys
import warnings
from tools.evaluation.run_benchmark import main as unificado_main


def main() -> None:
    warnings.warn(
        "run_experimental_benchmark.py está obsoleto y ha sido unificado. "
        "Utilice 'python -m tools.evaluation.run_benchmark' en su lugar.",
        DeprecationWarning,
        stacklevel=2,
    )
    print("⚠️  [DEPRECATED] Redirigiendo a run_benchmark.py...\n", file=sys.stderr)
    unificado_main()


if __name__ == "__main__":
    main()