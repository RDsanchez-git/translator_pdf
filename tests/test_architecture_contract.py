import sqlite3
import pytest
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from core.execution.ports import ControlPlanePort, EventPlanePort, MaterializedPlanePort

def test_ports_compliance():
    """SOTA: Validación dinámica de Protocolos estructurales."""
    # SOTA: Conexiones en memoria simuladas para pasar el Type Hint checker
    dummy_conn = sqlite3.connect(":memory:")
    
    control = ControlPlaneRepository(dummy_conn)
    event = EventPlaneRepository(dummy_conn)
    mat = MaterializedPlaneRepository(dummy_conn)

    assert isinstance(control, ControlPlanePort), "Fallo de contrato en Control Plane"
    assert isinstance(event, EventPlanePort), "Fallo de contrato en Event Plane"
    assert isinstance(mat, MaterializedPlanePort), "Fallo de contrato en Materialized Plane"