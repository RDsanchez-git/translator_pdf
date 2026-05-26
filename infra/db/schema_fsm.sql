CREATE TABLE IF NOT EXISTS document_fsm (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    current_state TEXT NOT NULL,
    state_version INTEGER NOT NULL DEFAULT 0,
    entered_state_at REAL,
    created_at REAL,
    updated_at REAL NOT NULL,
    is_terminal INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT,
    suspended_state TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (document_id, ast_hash)
);