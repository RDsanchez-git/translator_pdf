"""
core/telemetry/regression_gateway.py

Adaptador síncrono SQLite para TelemetryPort.

Resuelve DF-07: provee la implementación síncrona de TelemetryPort
que faltaba para instrumentar entry points no-async como run_regression.py.

Diseño:
- Synchronous: usa sqlite3.connect() directamente (no asyncio).
- WAL mode: consistencia con SQLiteTelemetryGateway existente.
- Fail-safe: errores de escritura se loguean pero no propagan
  (NADR-F18-02 §5.7 R26: observabilidad mínima, no deep observability).
- Context manager: garantiza cierre de conexión ante excepción.
- Schema creation en __enter__: elimina doble conexión (Mejora 1).

NADR-F18-02 §5.7 R25: La telemetría es evidencia operacional separada
de la evidencia científica. Se persiste en archivo propio, no en el
regression_report.json.

NADR-F18-01 §5.2 R8: El telemetry_execution_id es evidencia operacional,
NO scientific identity. Se genera como uuid4 y no se mezcla con
identity_chain.execution_id.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

from core.telemetry.ports import StageExecutionRecord, TelemetryPort

logger = logging.getLogger(__name__)

# Schema DDL separado para testabilidad
TELEMETRY_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS stage_execution_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT NOT NULL,
        stage_name TEXT NOT NULL,
        stage_index INTEGER NOT NULL,
        latency_sec REAL NOT NULL,
        input_type TEXT NOT NULL,
        output_type TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT,
        timestamp TEXT NOT NULL,
        metadata TEXT
    )
"""

TELEMETRY_INDEX_DDL = """
    CREATE INDEX IF NOT EXISTS idx_stage_exec
    ON stage_execution_records(execution_id, stage_index)
"""

INSERT_SQL = """
    INSERT INTO stage_execution_records (
        execution_id, stage_name, stage_index, latency_sec,
        input_type, output_type, status, error_message,
        timestamp, metadata
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class RegressionTelemetryGateway(TelemetryPort):
    """
    Adaptador síncrono SQLite para TelemetryPort.

    Implementa record_execution(StageExecutionRecord) con persistencia
    síncrona en SQLite WAL. Diseñado para entry points no-async como
    run_regression.py.

    Contract (TelemetryPort):
        - record_execution(record: StageExecutionRecord) -> None
        - Atomic: cada record es una transacción independiente
        - Fail-safe: errores de I/O y serialización se loguean, no propagan

    Lifecycle:
        - Context manager: with RegressionTelemetryGateway(db_path) as gw:
        - Manual: gw.close() para flush explícito
        - Schema creation ocurre en __enter__ (no en __init__)

    Thread safety:
        - SQLite en WAL mode soporta lecturas concurrentes.
        - Escrituras son serialized por SQLite. El gateway es
          single-thread por diseño (entry point de regression es síncrono).
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        # Nota: _init_db() NO se llama aquí. Se llama en __enter__
        # para evitar doble conexión (Mejora 1).

    def _init_db(self) -> None:
        """Idempotente: crea schema si no existe.

        Debe llamarse con self._conn ya abierto (desde __enter__).
        """
        if self._conn is None:
            raise RuntimeError(
                "RegressionTelemetryGateway._init_db() requires open connection. "
                "Use as context manager."
            )
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute(TELEMETRY_TABLE_DDL)
        self._conn.execute(TELEMETRY_INDEX_DDL)
        self._conn.commit()

    def __enter__(self) -> RegressionTelemetryGateway:
        self._conn = sqlite3.connect(self._db_path)
        self._init_db()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Cierra la conexión SQLite de forma idempotente."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def record_execution(self, record: StageExecutionRecord) -> None:
        """
        Persiste StageExecutionRecord de forma atómica.

        Fail-safe: errores de escritura y serialización se loguean
        pero no propagan (principio de observabilidad mínima,
        NADR-F18-02 §5.7 R26).

        Error handling:
        - sqlite3.Error: errores de I/O de SQLite
        - TypeError: metadata no serializable (objetos no JSON-serializables)
        - ValueError: errores de serialización JSON

        No se catchea Exception genérico para no ocultar bugs de programación.

        Args:
            record: StageExecutionRecord con stage_name, latency, status, etc.
        """
        if self._conn is None:
            logger.error(
                "RegressionTelemetryGateway: connection not open. "
                "Use as context manager: with RegressionTelemetryGateway(path) as gw:"
            )
            return

        try:
            metadata_json = json.dumps(record.metadata) if record.metadata else None

            self._conn.execute(
                INSERT_SQL,
                (
                    record.execution_id,
                    record.stage_name,
                    record.stage_index,
                    record.latency_sec,
                    record.input_type,
                    record.output_type,
                    record.status,
                    record.error_message,
                    record.timestamp.isoformat(),
                    metadata_json,
                ),
            )
            self._conn.commit()
        except (sqlite3.Error, TypeError, ValueError) as e:
            # Fail-safe: loguear pero no propagar
            logger.error(
                "RegressionTelemetryGateway: fallo escritura de "
                "StageExecutionRecord stage=%s execution_id=%s: %s",
                record.stage_name,
                record.execution_id,
                str(e),
            )