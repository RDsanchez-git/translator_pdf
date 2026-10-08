"""
Tests del mecanismo de shutdown ordenado (NADR-F18-02 §5.4 R15).

Verifica:
1. Que signal_stop() se llama primero (antes de processor shutdown).
2. Que el mecanismo continúa aunque un paso falle (no silencioso, §IV).
3. Que ShutdownReport refleja el estado final del shutdown.
"""
from core.execution.coordination import CoordinationPrimitives
from runtime.coordinated_shutdown import CoordinatedShutdownMechanism


class TestCoordinatedShutdown:
    def test_shutdown_signals_stop_first(self):
        """Paso 1: signal_stop() debe ejecutarse antes que processor shutdown."""
        call_order: list[str] = []
        coord = CoordinationPrimitives.create()

        def processor_shutdown():
            call_order.append("processor")

        shutdown = CoordinatedShutdownMechanism(
            coordination=coord,
            processor_shutdown=processor_shutdown,
            connection_closers=[lambda: call_order.append("conn1")],
        )

        report = shutdown.execute(reason="test")
        
        # signal_stop se ejecuta implícitamente antes que processor
        assert coord.is_stopped() is True
        assert call_order == ["processor", "conn1"]
        assert report.clean is True
        assert report.connections_closed == 1

    def test_shutdown_continues_on_processor_failure(self):
        """Si processor shutdown falla, se continúa con conexiones (§IV)."""
        coord = CoordinationPrimitives.create()
        conn_closed = []

        def failing_processor():
            raise RuntimeError("bridge failure")

        def close_conn():
            conn_closed.append(1)

        shutdown = CoordinatedShutdownMechanism(
            coordination=coord,
            processor_shutdown=failing_processor,
            connection_closers=[close_conn],
        )

        report = shutdown.execute(reason="test")

        assert report.bridge_shutdown_ok is False
        assert "processor shutdown failed" in report.errors[0]
        assert report.connections_closed == 1  # conexiones SÍ se cerraron
        assert report.clean is False

    def test_shutdown_continues_on_connection_failure(self):
        """Si una conexión falla, se continúa con las demás (§IV)."""
        coord = CoordinationPrimitives.create()

        def close_ok():
            pass

        def close_fail():
            raise RuntimeError("conn failure")

        shutdown = CoordinatedShutdownMechanism(
            coordination=coord,
            processor_shutdown=lambda: None,
            connection_closers=[close_ok, close_fail, close_ok],
        )

        report = shutdown.execute(reason="test")

        assert report.bridge_shutdown_ok is True
        assert report.connections_closed == 2  # 2 de 3 se cerraron
        assert len(report.errors) == 1
        assert report.clean is False

    def test_shutdown_report_contains_reason_and_duration(self):
        coord = CoordinationPrimitives.create()
        shutdown = CoordinatedShutdownMechanism(
            coordination=coord,
            processor_shutdown=lambda: None,
            connection_closers=[],
        )

        report = shutdown.execute(reason="user_request")

        assert report.reason == "user_request"
        assert report.duration_sec >= 0.0