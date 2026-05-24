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

-- Tabla de Idempotencia dedicada para el Reconciliador (Evita reprocesar comandos en la proyección)
CREATE TABLE IF NOT EXISTS processed_reconciliation_commands (
    reconciliation_id TEXT PRIMARY KEY,
    processed_at REAL NOT NULL
);