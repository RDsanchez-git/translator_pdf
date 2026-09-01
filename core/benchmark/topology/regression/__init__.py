"""
Subsistema de regresión topológica graduada (NADR-F17BIS-19).

Exports públicos del bounded context.
Nota: La construcción del dict de recall evaluadores pertenece
al composition root (Gate 3), no a este módulo.
"""
from core.benchmark.topology.regression.aggregation import (
    aggregate_corpus_verdicts,
)
from core.benchmark.topology.regression.adapter import RegressionAdapter
from core.benchmark.topology.regression.errors import (
    IncompleteBaselineError,
    InvalidNSSScoreError,
    MissingOracleHashError,
    OracleDocumentMismatchError,
    OracleIntegrityError,
    OracleNotSealedError,
    RegressionError,
)
from core.benchmark.topology.regression.mechanism import (
    DoubleProtectionMechanism,
    DoubleProtectionResult,
)
from core.benchmark.topology.regression.models import (
    DEFAULT_REGRESSION_THRESHOLDS,
    RegressionCriticalitySignal,
    RegressionEvaluationReport,
    RegressionThresholds,
    RegressionVerdict,
)
from core.benchmark.topology.regression.strategy import (
    RegressionEvaluationStrategy,
)

__all__ = [
    # Errors
    "RegressionError",
    "OracleIntegrityError",
    "OracleNotSealedError",
    "OracleDocumentMismatchError",
    "MissingOracleHashError",
    "InvalidNSSScoreError",
    "IncompleteBaselineError",
    # Models
    "RegressionVerdict",
    "RegressionCriticalitySignal",
    "RegressionThresholds",
    "RegressionEvaluationReport",
    "DEFAULT_REGRESSION_THRESHOLDS",
    # Aggregation
    "aggregate_corpus_verdicts",
    # Mechanism
    "DoubleProtectionMechanism",
    "DoubleProtectionResult",
    # Adapter
    "RegressionAdapter",
    # Strategy
    "RegressionEvaluationStrategy",
]