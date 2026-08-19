"""
Adaptador de persistencia para estado de cuotas con backend SQLite WAL.

NADR-08 §5.1 R1: Implementa el puerto RateLimitStore.
NADR-08 §5.1 R3: El estado NO reside exclusivamente en RAM.
NADR-08 §5.1 R4: Se instancia desde la Composition Root.
GF-01: Backend local. No distribuido. Single-node.

Nota sobre BucketState.last_update:
Este campo almacena time.time() (epoch seconds), NO time.monotonic().
El QuotaManager se encarga de la conversión epoch → monotonic al cargar
y monotonic → epoch al guardar.
"""
import sqlite3
from typing import Optional
from core.resilience.rate_limit_store import BucketState


class SQLiteRateLimitStore:
    """
    Persistencia de estado de cuotas en SQLite WAL.
    
    Recibe la conexión por constructor (patrón DI de infra/db/).
    El caller es responsable del ciclo de vida de la conexión.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_buckets (
                bucket_id   TEXT PRIMARY KEY,
                tokens      REAL NOT NULL,
                last_update REAL NOT NULL
            )
        """)
        self._conn.commit()

    def load(self, bucket_id: str) -> Optional[BucketState]:
        cursor = self._conn.execute(
            "SELECT tokens, last_update FROM rate_limit_buckets WHERE bucket_id = ?",
            (bucket_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return BucketState(tokens=row[0], last_update=row[1])

    def save(self, bucket_id: str, state: BucketState) -> None:
        self._conn.execute(
            """INSERT INTO rate_limit_buckets (bucket_id, tokens, last_update)
               VALUES (?, ?, ?)
               ON CONFLICT(bucket_id)
               DO UPDATE SET tokens = excluded.tokens,
                             last_update = excluded.last_update""",
            (bucket_id, state.tokens, state.last_update)
        )
        self._conn.commit()