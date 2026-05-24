CREATE TABLE IF NOT EXISTS document_fsm (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    current_state TEXT NOT NULL,
    state_version INTEGER NOT NULL DEFAULT 0,
    entered_state_at REAL,
    created_at REAL,
    updated_at REAL NOT NULL,
    last_heartbeat_at REAL,
    lease_owner TEXT,
    lease_expires_at REAL,
    is_terminal INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT,
    suspended_state TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (document_id, ast_hash)
);

CREATE TABLE IF NOT EXISTS chunk_tasks (
    task_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    task_state TEXT NOT NULL DEFAULT 'PENDING', 
    worker_type TEXT NOT NULL DEFAULT 'LLM', 
    execution_id TEXT, 
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    lease_owner TEXT,
    error_log TEXT,
    lease_expires_at REAL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    state_version INTEGER NOT NULL DEFAULT 1,
    UNIQUE(document_id, ast_hash, node_id)
);

-- Índices de alta velocidad para el Control Plane
CREATE INDEX IF NOT EXISTS idx_chunk_tasks_pickup ON chunk_tasks(document_id, ast_hash, task_state, lease_expires_at);
CREATE INDEX IF NOT EXISTS idx_chunk_tasks_scheduler ON chunk_tasks(worker_type, task_state, lease_expires_at, created_at);

-- Tabla genérica para Global Singleton Actors (Leader Election / Fencing distributed locks)
CREATE TABLE IF NOT EXISTS system_leases (
    lease_name TEXT PRIMARY KEY,
    owner_id TEXT,
    lease_expires_at REAL,
    updated_at REAL,
    lease_version INTEGER NOT NULL DEFAULT 0
);

-- Inicialización del candado del Reconciliador
INSERT OR IGNORE INTO system_leases (lease_name) VALUES ('global_reconciler');