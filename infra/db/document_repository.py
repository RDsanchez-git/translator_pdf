import sqlite3
import hashlib
from typing import List
from core.ast.models import TranslationUnit

# SOTA: Importación segregada del Read Path (Ensamblado)
from core.compiler.assembler import (
    IntegrityCheckedDocumentRepository, 
    PayloadNotFoundError, 
    HashMismatchError
)

# SOTA: Importación segregada del Write Path (Orquestación)
from core.pipeline.orchestrator import DocumentRepositoryProtocol


class SQLiteDocumentRepository(IntegrityCheckedDocumentRepository, DocumentRepositoryProtocol):
    """SOTA: Implementación física del repositorio de hidratación con integridad bidireccional."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self._ensure_schema()

    def _ensure_schema(self):
        with self.conn:
            # SOTA FIX: executescript permite procesar el lote completo de tablas e índices secuencialmente
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS original_chunks (
                job_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (job_id, chunk_id)
            );
            CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON original_chunks(created_at);
            """)

    def save_batch(self, job_id: str, units: List[TranslationUnit]) -> None:
        """SOTA Write Path: Persistencia transaccional masiva aislada por job_id."""
        data = [
            (job_id, unit.chunk_id, unit.target_payload, unit.payload_sha256)
            for unit in units
        ]
        with self.conn:
            self.conn.executemany(
                "INSERT OR REPLACE INTO original_chunks (job_id, chunk_id, payload, payload_sha256) VALUES (?, ?, ?, ?)",
                data
            )

    def get_verified_payload(self, job_id: str, chunk_id: str, expected_sha256: str) -> str:
        """SOTA Read Path: Hidratación criptográfica con aislamiento multi-tenant."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT payload, payload_sha256 FROM original_chunks WHERE job_id = ? AND chunk_id = ?", 
            (job_id, chunk_id)
        )
        row = cursor.fetchone()
        
        if not row:
            raise PayloadNotFoundError(f"Chunk {chunk_id} no encontrado para el job {job_id} en repositorio físico.")
            
        payload, stored_sha256 = row[0], row[1]
        
        # Validación 1: Mutación en base de datos
        if stored_sha256 != expected_sha256:
            raise HashMismatchError(f"Corrupción relacional: SHA almacenado difiere del esperado para {chunk_id}.")
            
        # Validación 2: Mutación de I/O o codificación
        calculated_sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if calculated_sha != expected_sha256:
            raise HashMismatchError("Corrupción silenciosa: El payload rehidratado no coincide con la firma criptográfica.")
            
        return payload