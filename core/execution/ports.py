from enum import Enum
from typing import Protocol, List, Optional, runtime_checkable
from dataclasses import dataclass

# ==========================================
# ENUMS SEMÁNTICOS (Exhaustiveness)
# ==========================================

class ProcessingOutcome(Enum):
    MATERIALIZED = "MATERIALIZED"
    REMATERIALIZED = "REMATERIALIZED"
    ALREADY_CURRENT = "ALREADY_CURRENT"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SKIPPED_UNSUPPORTED = "SKIPPED_UNSUPPORTED"

class ProjectionState(Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    MISSING = "MISSING"
    CORRUPTED = "CORRUPTED"

class EventLifecycle(Enum):
    GENERATED = "GENERATED"
    REMATERIALIZED = "REMATERIALIZED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    RECONCILED = "RECONCILED"

# ==========================================
# DTOs: Data Transfer Objects
# ==========================================

@dataclass(frozen=True)
class TaskLease:
    task_id: str
    node_id: str
    execution_id: str

@dataclass(frozen=True)
class ReplayPayload:
    raw_response: str
    projection_version: int
    execution_id: str

@dataclass(frozen=True)
class ProjectionStatus:
    state: ProjectionState
    projection_version: int | None
    normalized_hash: str | None

@dataclass(frozen=True)
class ProjectionRecord:
    node_id: str
    normalized_response: str
    projection_version: int

# ==========================================
# PROTOCOLS: Contratos con DIP
# ==========================================

@runtime_checkable
class ControlPlanePort(Protocol):
    def enqueue_tasks(self, document_id: str, ast_hash: str, nodes: List[str]) -> None: ...
    def pick_task(self, worker_id: str, document_id: str, ast_hash: str) -> Optional[TaskLease]: ...
    def acknowledge_execution(self, task_id: str, worker_id: str) -> None: ...
    def abandon_execution(self, task_id: str, worker_id: str, error: str) -> None: ...
    def renew_task_lease(self, task_id: str, worker_id: str, additional_ttl_sec: int) -> bool: ...
    
@runtime_checkable
class EventPlanePort(Protocol):
    def get_replay(self, content_hash: str, prompt_v: str, model_v: str) -> Optional[ReplayPayload]: ...
    def append_wal(self, execution_id: str, document_id: str, node_id: str, content_hash: str, 
                   raw_response: str, prompt_v: str, model_v: str, projection_v: int, lifecycle: EventLifecycle) -> None: ...

@runtime_checkable
class MaterializedPlanePort(Protocol):
    def get_projection_status(self, document_id: str, ast_hash: str, node_id: str, required_version: int) -> ProjectionStatus: ...
    def upsert_projection(self, document_id: str, ast_hash: str, node_id: str, content_hash: str, 
                          normalized_text: str, normalized_hash: str, projection_v: int) -> None: ...
    def get_assemblable_chunks(self, document_id: str, ast_hash: str, expected_node_ids: List[str], required_projection_v: int) -> List[ProjectionRecord]: ...