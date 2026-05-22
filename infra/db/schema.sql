-- PLANO 1: CONTROL PLANE (control.db)
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
    PRIMARY KEY (document_id, ast_hash)
);

CREATE TABLE IF NOT EXISTS chunk_tasks (
    task_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    task_state TEXT NOT NULL DEFAULT 'PENDING', 
    worker_type TEXT NOT NULL DEFAULT 'LLM', -- SOTA: Clasificación física de Daemons
    execution_id TEXT, 
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    lease_owner TEXT,
    error_log TEXT,
    lease_expires_at REAL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    UNIQUE(document_id, ast_hash, node_id)
);

-- Índices de alta velocidad para el Control Plane
CREATE INDEX IF NOT EXISTS idx_chunk_tasks_pickup ON chunk_tasks(document_id, ast_hash, task_state, lease_expires_at);

-- SOTA: Cobertura total para queries de sondeo paralelo (claim_next_pending_task / pick_task)
CREATE INDEX IF NOT EXISTS idx_chunk_tasks_scheduler ON chunk_tasks(worker_type, task_state, lease_expires_at, created_at);


-- PLANO 2: EVENT PLANE (event.db)
CREATE TABLE IF NOT EXISTS chunk_events_log (
    event_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    raw_response TEXT,
    prompt_version TEXT NOT NULL, 
    model_version TEXT NOT NULL,  
    projection_version INTEGER,   
    lifecycle TEXT NOT NULL,      -- SOTA: Integración FSM-CQRS
    timestamp REAL NOT NULL,
    UNIQUE(execution_id, node_id) -- SOTA: Idempotencia estricta para ON CONFLICT
);

-- SOTA: Índice compuesto optimizado para filtrado y sort nativo inverso sin temporary B-Tree
CREATE INDEX IF NOT EXISTS idx_replay_lookup 
ON chunk_events_log(
    content_hash, 
    prompt_version, 
    model_version, 
    execution_id DESC
);


-- PLANO 3: MATERIALIZED PLANE (materialized.db)
CREATE TABLE IF NOT EXISTS valid_chunks_cache (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    normalized_response TEXT NOT NULL,
    normalized_hash TEXT NOT NULL, 
    projection_version INTEGER NOT NULL, 
    last_updated REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash, node_id)
);

CREATE INDEX IF NOT EXISTS idx_valid_chunks_lookup ON valid_chunks_cache(document_id, ast_hash, projection_version);


-- PLANO 4: Tabla de Idempotencia para el Reconciliador
CREATE TABLE IF NOT EXISTS processed_reconciliation_commands (
    reconciliation_id TEXT PRIMARY KEY,
    processed_at REAL NOT NULL
);

-- Tabla genérica para Global Singleton Actors (Leader Election)
CREATE TABLE IF NOT EXISTS system_leases (
    lease_name TEXT PRIMARY KEY,
    owner_id TEXT,
    lease_expires_at REAL,
    updated_at REAL,
    lease_version INTEGER NOT NULL DEFAULT 0 -- SOTA: Fencing Epoch integrado
);

-- Inicialización del candado del Reconciliador
INSERT OR IGNORE INTO system_leases (lease_name) VALUES ('global_reconciler');