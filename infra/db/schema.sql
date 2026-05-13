-- Añadir ast_hash al historial
CREATE TABLE IF NOT EXISTS document_state_machine (
    event_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL, 
    node_id TEXT NOT NULL,
    PRIMARY KEY (document_id, ast_hash) -- SOTA: Aislamiento estricto de generación
);

-- Llave primaria compuesta generacional
CREATE TABLE IF NOT EXISTS valid_chunks_cache (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    normalized_response TEXT NOT NULL,
    last_updated REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash, node_id)
);

-- SOTA: Idempotencia para protección contra Replay Attacks / Network Retries
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_idempotency 
ON chunk_events_log(document_id, ast_hash, node_id, content_hash);

-- SOTA FSM: Tabla Maestra de Coordinación (Control Plane)
CREATE TABLE IF NOT EXISTS document_state_machine (
    document_id TEXT PRIMARY KEY,
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
    failure_reason TEXT
);

-- Índices para el Sweeper (Recovery Daemon)
CREATE INDEX IF NOT EXISTS idx_fsm_recovery ON document_state_machine(is_terminal, lease_expires_at);
CREATE INDEX IF NOT EXISTS idx_fsm_status ON document_state_machine(current_state);
