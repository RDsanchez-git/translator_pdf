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

-- OPTIMIZACIÓN SOTA: Índice parcial de cobertura y ordenamiento para suprimir Filesort
DROP INDEX IF EXISTS idx_chunk_tasks_pickup;
DROP INDEX IF EXISTS idx_chunk_tasks_pickup_v2;

CREATE INDEX IF NOT EXISTS idx_chunk_tasks_ready_queue
ON chunk_tasks (document_id, ast_hash, created_at, lease_expires_at, lease_owner)
WHERE task_state IN ('PENDING', 'RETRYABLE_ERROR');

CREATE INDEX IF NOT EXISTS idx_chunk_tasks_scheduler 
ON chunk_tasks (worker_type, lease_expires_at, created_at)
WHERE task_state IN ('PENDING', 'RETRYABLE_ERROR');

CREATE TABLE IF NOT EXISTS system_leases (
    lease_name TEXT PRIMARY KEY,
    owner_id TEXT,
    lease_expires_at REAL,
    updated_at REAL,
    lease_version INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO system_leases (lease_name) VALUES ('global_reconciler');