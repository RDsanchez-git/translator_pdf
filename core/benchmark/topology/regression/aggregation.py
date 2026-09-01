"""
Agregación de veredictos por corpus (NADR-F17BIS-19 §5.1 R2-R3).

NADR-19 §5.1 R3: El veredicto por corpus es el PEOR veredicto
de todos los documentos individuales.
"""
from __future__ import annotations

from typing import Sequence

from core.benchmark.topology.regression.models import RegressionVerdict


def aggregate_corpus_verdicts(
    verdicts: Sequence[RegressionVerdict],
) -> RegressionVerdict:
    """Agrega veredictos por documento en un veredicto por corpus.

    Args:
        verdicts: Secuencia de veredictos por documento. No vacía.

    Returns:
        El peor veredicto de la secuencia.

    Raises:
        ValueError: Si la secuencia está vacía.
    """
    if not verdicts:
        raise ValueError(
            "Cannot aggregate empty verdict sequence. "
            "At least one document verdict is required."
        )

    return max(verdicts, key=lambda v: v.severity_rank)