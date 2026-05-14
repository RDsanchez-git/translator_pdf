-- 1. SOTA FSM: Tabla Maestra de Coordinación (Padre)
CREATE TABLE IF NOT EXISTS document_state_machine (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    current_state TEXT NOT NULL,
    state_version INTEGER NOT NULL DEFAULT 0,
    fsm_version INTEGER NOT NULL DEFAULT 1,
    is_terminal INTEGER NOT NULL DEFAULT 0,
    entered_state_at REAL NOT NULL,
    lease_owner TEXT,
    lease_expires_at REAL,
    last_heartbeat_at REAL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    failure_reason TEXT,
    suspended_state TEXT, -- SOTA: Necesario para el Sweeper
    PRIMARY KEY (document_id, ast_hash) -- SOTA: PK Compuesta requerida por FK
);

CREATE INDEX IF NOT EXISTS idx_fsm_recovery ON document_state_machine(is_terminal, lease_expires_at);
CREATE INDEX IF NOT EXISTS idx_fsm_status ON document_state_machine(current_state);

-- 2. Command Side: Event Sourcing Log
CREATE TABLE IF NOT EXISTS chunk_events_log (
    event_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    raw_response TEXT,
    normalized_response TEXT,
    lifecycle TEXT NOT NULL,
    failure_type TEXT,
    processing_stage TEXT NOT NULL,
    validation_errors TEXT,
    prompt_hash TEXT,
    prompt_template_version TEXT,
    normalizer_version TEXT,
    validator_version TEXT,
    timestamp REAL NOT NULL
);

-- SOTA: Idempotencia transaccional
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_idempotency 
ON chunk_events_log(document_id, ast_hash, node_id, content_hash);

-- 3. Query Side: CQRS Materialized View
CREATE TABLE IF NOT EXISTS valid_chunks_cache (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    normalized_response TEXT NOT NULL,
    last_updated REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash, node_id)
);

CREATE INDEX IF NOT EXISTS idx_valid_chunks_lookup 
ON valid_chunks_cache(document_id, ast_hash);

-- 4. SOTA: Durable Task Queue (Hija)
CREATE TABLE IF NOT EXISTS chunk_tasks (
    task_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    task_state TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED, RETRYABLE_ERROR
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Coordinación y Leases (Independiente del Lease del Documento)
    lease_owner TEXT,
    lease_expires_at REAL,
    last_heartbeat_at REAL,
    
    -- Auditoría y Resultados
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    error_log TEXT,

    -- SOTA: Referencia estricta a la PK compuesta generacional
    FOREIGN KEY (document_id, ast_hash) REFERENCES document_state_machine(document_id, ast_hash),
    UNIQUE(document_id, ast_hash, node_id) 
);

CREATE INDEX IF NOT EXISTS idx_tasks_discovery ON chunk_tasks(task_state, lease_expires_at) WHERE task_state != 'COMPLETED';