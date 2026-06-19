import time
import asyncio
import logging
from typing import Optional, Dict
import aiosqlite
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult, LLMProvider

logger = logging.getLogger(__name__)

class CachedLLMProvider:
    """SOTA: Decorador de persistencia con prevención de Cache Stampede y limpieza de memoria."""
    
    def __init__(self, underlying: LLMProvider, db_path: str):
        self._underlying = underlying
        self._db_path = db_path
        
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        
        self.metrics = {
            "cache_hits": 0, "cache_misses": 0,
            "cache_writes": 0, "cache_write_failures": 0
        }

    async def initialize(self) -> None:
        """SOTA: Configuración estructural inmutable. El modo WAL se establece una única vez."""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS llm_translation_cache (
                    prompt_hash TEXT PRIMARY KEY, chunk_id TEXT NOT NULL,
                    model_name TEXT NOT NULL, prompt_version TEXT NOT NULL,
                    translated_text TEXT NOT NULL, input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL, latency_ms REAL NOT NULL,
                    cached_at REAL NOT NULL
                );
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_cache_chunk ON llm_translation_cache(chunk_id);")
            await db.commit()

    async def _read_cache(self, prompt_hash: str) -> Optional[ProviderResult]:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                async with db.execute(
                    "SELECT translated_text, input_tokens, output_tokens, chunk_id FROM llm_translation_cache WHERE prompt_hash = ?",
                    (prompt_hash,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return ProviderResult(
                            chunk_id=row[3], translated_text=row[0],
                            input_tokens=row[1], output_tokens=row[2],
                            latency_ms=0.0, finish_reason="cache_hit"
                        )
            return None
        except Exception as exc:
            # SOTA: Un fallo de lectura (ej. base de datos bloqueada o corrupta) 
            # se degrada silenciosamente a un Cache Miss para no detener la inferencia.
            logger.warning(f"Error I/O lectura caché (asumiendo MISS): {exc}")
            return None

    async def _write_cache(self, envelope: PromptEnvelope, result: ProviderResult) -> None:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    """
                    INSERT INTO llm_translation_cache (
                        prompt_hash, chunk_id, model_name, prompt_version, 
                        translated_text, input_tokens, output_tokens, latency_ms, cached_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(prompt_hash) DO NOTHING
                    """,
                    (
                        envelope.prompt_hash, result.chunk_id, envelope.model_name,
                        envelope.prompt_version, result.translated_text, result.input_tokens,
                        result.output_tokens, result.latency_ms, time.time()
                    )
                )
                await db.commit()
                self.metrics["cache_writes"] += 1
        except Exception as exc:
            self.metrics["cache_write_failures"] += 1
            logger.warning(f"Error I/O caché: {exc}")

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        # PASO 1: Lectura optimista rápida
        result = await self._read_cache(envelope.prompt_hash)
        if result:
            self.metrics["cache_hits"] += 1
            return ProviderResult(
                chunk_id=envelope.chunk_id, translated_text=result.translated_text,
                input_tokens=result.input_tokens, output_tokens=result.output_tokens,
                latency_ms=0.0, finish_reason="cache_hit"
            )

        # PASO 2: Adquisición de Lock Anti-Stampede
        async with self._global_lock:
            if envelope.prompt_hash not in self._locks:
                self._locks[envelope.prompt_hash] = asyncio.Lock()
            target_lock = self._locks[envelope.prompt_hash]

        try:
            async with target_lock:
                # PASO 3: Doble comprobación post-lock
                result = await self._read_cache(envelope.prompt_hash)
                if result:
                    self.metrics["cache_hits"] += 1
                    return ProviderResult(
                        chunk_id=envelope.chunk_id, translated_text=result.translated_text,
                        input_tokens=result.input_tokens, output_tokens=result.output_tokens,
                        latency_ms=0.0, finish_reason="cache_hit"
                    )

                # PASO 4: Inferencia física (Miss)
                self.metrics["cache_misses"] += 1
                result = await self._underlying.translate(envelope)
                await self._write_cache(envelope, result)

                return result
        finally:
            # SOTA: Limpieza atómica para prevenir Memory Leak.
            # Se verifica identidad (`is`) para no eliminar un lock recién creado por otro coroutine.
            async with self._global_lock:
                if self._locks.get(envelope.prompt_hash) is target_lock:
                    self._locks.pop(envelope.prompt_hash, None)