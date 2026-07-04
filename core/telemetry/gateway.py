import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Optional
from core.telemetry.models import ProductionTelemetryEvent

logger = logging.getLogger(__name__)

class SQLiteTelemetryGateway:
    """SOTA: Colector asíncrono no bloqueante con persistencia SQLite WAL."""
    
    def __init__(self, db_path: str = "infra/telemetry/production.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._queue: asyncio.Queue[Optional[ProductionTelemetryEvent]] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    execution_id TEXT,
                    chunk_id TEXT,
                    provider TEXT,
                    event_type TEXT,
                    selection_reason TEXT,
                    latency_ms REAL,
                    quota_wait_ms REAL,
                    input_tokens INTEGER,
                    output_tokens INTEGER
                )
            ''')
            conn.execute("CREATE INDEX IF NOT EXISTS idx_exec_event ON telemetry_events(execution_id, event_type);")

    async def start(self) -> None:
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._flush_worker())

    async def stop(self) -> None:
        if self._worker_task:
            await self._queue.put(None)  # Poison pill para cerrado limpio
            await self._worker_task
            self._worker_task = None

    def emit(self, event: ProductionTelemetryEvent) -> None:
        """Fire-and-forget. Cero impacto en la latencia de inferencia."""
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.error("Telemetría descartada: Event Loop saturado.")

    async def _flush_worker(self) -> None:
        batch = []
        while True:
            try:
                event = await self._queue.get()
                if event is None:
                    if batch:
                        self._write_batch(batch)
                    self._queue.task_done()
                    break
                
                batch.append(event)
                # Flush por lotes para minimizar I/O o cada 50 eventos
                if len(batch) >= 50 or self._queue.empty():
                    self._write_batch(batch)
                    batch.clear()
                    
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Falla crítica en Telemetry Worker: {e}")

    def _write_batch(self, events: list[ProductionTelemetryEvent]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany('''
                INSERT INTO telemetry_events (
                    execution_id, chunk_id, provider, event_type, 
                    selection_reason, latency_ms, quota_wait_ms, input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [(
                e.execution_id, e.chunk_id, e.provider, e.event_type.value, 
                e.selection_reason.value if e.selection_reason else None, 
                e.latency_ms, e.quota_wait_ms, e.input_tokens, e.output_tokens
            ) for e in events])