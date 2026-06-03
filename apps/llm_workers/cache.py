import sqlite3
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class SQLiteTranslationCache:
    """SOTA Pragmática: Caché local persistente en SQLite con soporte WAL y bloqueo mitigado por timeout."""
    
    def __init__(self, db_path: str = "infra/db/cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        # Ajuste 1 y 2: Inyección de timeout de 30s para mitigar bloqueos bajo concurrencia masiva
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translation_cache (
                    cache_key TEXT PRIMARY KEY,
                    payload_sha256 TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    translated_payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Ajuste 3: Reemplazo por índice compuesto óptimo para auditorías operativas futuras
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_admin_lookup 
                ON translation_cache(payload_sha256, model_name, prompt_version)
            """)
            conn.commit()

    def _compute_key(self, payload_sha256: str, model_name: str, prompt_version: str) -> str:
        raw_key = f"{payload_sha256}:{model_name}:{prompt_version}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def get(self, payload_sha256: str, model_name: str, prompt_version: str) -> Optional[str]:
        cache_key = self._compute_key(payload_sha256, model_name, prompt_version)
        
        def _read():
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.execute(
                    "SELECT translated_payload FROM translation_cache WHERE cache_key = ?", 
                    (cache_key,)
                )
                row = cursor.fetchone()
                return row[0] if row else None

        return await asyncio.to_thread(_read)

    async def set(self, payload_sha256: str, model_name: str, prompt_version: str, translated_payload: str) -> None:
        cache_key = self._compute_key(payload_sha256, model_name, prompt_version)
        
        def _write():
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO translation_cache 
                    (cache_key, payload_sha256, model_name, prompt_version, translated_payload)
                    VALUES (?, ?, ?, ?, ?)
                """, (cache_key, payload_sha256, model_name, prompt_version, translated_payload))
                # Ajuste 1: Commit explícito mandatorio para entornos distribuidos
                conn.commit()
        
        await asyncio.to_thread(_write)