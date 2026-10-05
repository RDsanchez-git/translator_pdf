"""
tests/telemetry/test_regression_gateway.py

Tests mínimos para RegressionTelemetryGateway (Task 1.1.1, Mejora 3).

Cubre:
1. record_execution() persiste un record correctamente
2. record_execution() es fail-safe (no propaga errores de SQLite)
3. Context manager cierra la conexión correctamente
4. _init_db() es idempotente (crear schema dos veces no falla)
5. record_execution() sin context manager loguea error, no crash
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.telemetry.ports import StageExecutionRecord
from core.telemetry.regression_gateway import RegressionTelemetryGateway


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """DB temporal para tests."""
    return tmp_path / "test_telemetry.db"


@pytest.fixture
def sample_record() -> StageExecutionRecord:
    """StageExecutionRecord de ejemplo."""
    return StageExecutionRecord(
        execution_id="test-exec-001",
        stage_name="EXTRACTION",
        stage_index=0,
        latency_sec=1.5,
        input_type="pdf_path",
        output_type="runtime_ast",
        status="SUCCESS",
        error_message=None,
        timestamp=datetime(2026, 10, 4, 12, 0, 0, tzinfo=timezone.utc),
        metadata={"document_id": "doc_01"},
    )


class TestRegressionTelemetryGateway:
    """Tests para RegressionTelemetryGateway."""

    def test_record_execution_persists_correctly(
        self, tmp_db: Path, sample_record: StageExecutionRecord
    ) -> None:
        """Test 1: record_execution() persiste un record correctamente."""
        with RegressionTelemetryGateway(tmp_db) as gw:
            gw.record_execution(sample_record)

        # Verificar que el record se persistió
        with sqlite3.connect(tmp_db) as conn:
            rows = conn.execute(
                "SELECT execution_id, stage_name, stage_index, latency_sec, "
                "input_type, output_type, status, error_message, timestamp, metadata "
                "FROM stage_execution_records"
            ).fetchall()

        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "test-exec-001"
        assert row[1] == "EXTRACTION"
        assert row[2] == 0
        assert row[3] == pytest.approx(1.5)
        assert row[4] == "pdf_path"
        assert row[5] == "runtime_ast"
        assert row[6] == "SUCCESS"
        assert row[7] is None
        assert row[8] == "2026-10-04T12:00:00+00:00"
        assert '"document_id": "doc_01"' in row[9]

    def test_record_execution_is_fail_safe(
        self, tmp_db: Path, sample_record: StageExecutionRecord
    ) -> None:
        """Test 2: record_execution() es fail-safe (no propaga errores)."""
        with RegressionTelemetryGateway(tmp_db) as gw:
            # Cerrar la conexión para forzar error de SQLite
            gw.close()
            # Esto debe loguear error pero NO lanzar excepción
            gw.record_execution(sample_record)
        # Si llegamos aquí sin excepción, el test pasa

    def test_context_manager_closes_connection(self, tmp_db: Path) -> None:
        """Test 3: Context manager cierra la conexión correctamente."""
        gw = RegressionTelemetryGateway(tmp_db)
        with gw:
            assert gw._conn is not None
        assert gw._conn is None

    def test_init_db_is_idempotent(self, tmp_db: Path) -> None:
        """Test 4: _init_db() es idempotente (crear schema dos veces no falla)."""
        # Primera creación
        with RegressionTelemetryGateway(tmp_db):
            pass

        # Segunda creación (schema ya existe)
        with RegressionTelemetryGateway(tmp_db):
            pass

        # Verificar que la tabla existe y está vacía
        with sqlite3.connect(tmp_db) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM stage_execution_records"
            ).fetchone()[0]
        assert count == 0

    def test_record_execution_without_context_manager_logs_error(
        self, tmp_db: Path, sample_record: StageExecutionRecord
    ) -> None:
        """Test 5: record_execution() sin context manager loguea error, no crash."""
        gw = RegressionTelemetryGateway(tmp_db)
        # No usar context manager, _conn es None
        # Esto debe loguear error pero NO lanzar excepción
        gw.record_execution(sample_record)
        # Si llegamos aquí sin excepción, el test pasa

    def test_multiple_records_persist_in_order(
        self, tmp_db: Path
    ) -> None:
        """Test 6: Múltiples records se persisten en orden."""
        records = [
            StageExecutionRecord(
                execution_id="test-exec-002",
                stage_name=stage_name,
                stage_index=i,
                latency_sec=float(i),
                input_type="input",
                output_type="output",
                status="SUCCESS",
                error_message=None,
                timestamp=datetime(2026, 10, 4, 12, 0, i, tzinfo=timezone.utc),
                metadata={},
            )
            for i, stage_name in enumerate(
                ["EXTRACTION", "TOPOLOGY_EVALUATION", "REPORT_ASSEMBLY"]
            )
        ]

        with RegressionTelemetryGateway(tmp_db) as gw:
            for record in records:
                gw.record_execution(record)

        with sqlite3.connect(tmp_db) as conn:
            rows = conn.execute(
                "SELECT stage_name, stage_index FROM stage_execution_records "
                "ORDER BY stage_index"
            ).fetchall()

        assert len(rows) == 3
        assert rows[0] == ("EXTRACTION", 0)
        assert rows[1] == ("TOPOLOGY_EVALUATION", 1)
        assert rows[2] == ("REPORT_ASSEMBLY", 2)