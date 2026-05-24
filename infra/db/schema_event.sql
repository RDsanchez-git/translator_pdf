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
    lifecycle TEXT NOT NULL,      
    timestamp REAL NOT NULL,
    UNIQUE(execution_id, node_id) 
);

-- Índice compuesto optimizado para filtrado y sort nativo inverso sin temporary B-Tree
CREATE INDEX IF NOT EXISTS idx_replay_lookup 
ON chunk_events_log(
    content_hash, 
    prompt_version, 
    model_version, 
    execution_id DESC
);