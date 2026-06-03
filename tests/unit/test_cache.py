import unittest
import os
import asyncio
from apps.llm_workers.cache import SQLiteTranslationCache

class TestSQLiteTranslationCache(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación de ciclos de vida, salting de prompt e invalidación criptográfica."""

    def setUp(self):
        self.test_db = "tests/fixtures/test_cache.db"
        self.cache = SQLiteTranslationCache(db_path=self.test_db)

    def tearDown(self):
        # Ajuste 4: Control defensivo de excepciones de E/S específicas de Windows NT
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.test_db}{suffix}"
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    pass

    async def test_cache_hit_and_miss_lifecycle(self):
        """10C.6.1: Certifica el almacenamiento y recuperación exacta de payloads."""
        res_miss = await self.cache.get("sha_crypt_123", "gemini-1.5", "v1.0")
        self.assertIsNone(res_miss)

        await self.cache.set("sha_crypt_123", "gemini-1.5", "v1.0", "Resultado Persistido")
        
        res_hit = await self.cache.get("sha_crypt_123", "gemini-1.5", "v1.0")
        self.assertEqual(res_hit, "Resultado Persistido")

    async def test_cache_invalidation_by_prompt_salting(self):
        """10C.6.2: Certifica que mutaciones en la versión del prompt fuercen un descarte preventivo."""
        await self.cache.set("sha_crypt_123", "gemini-1.5", "v1.0", "Traducción Vieja")
        
        res_invalidated = await self.cache.get("sha_crypt_123", "gemini-1.5", "v2.0")
        self.assertIsNone(res_invalidated)

    async def test_cache_persistence_between_instances(self):
        """10C.6.3: Ajuste 5: Certifica el almacenamiento en almacenamiento físico real no-volátil."""
        # Instancia A escribe en el archivo físico
        cache_instance_a = SQLiteTranslationCache(db_path=self.test_db)
        await cache_instance_a.set("sha_persistent_999", "gemini-flash", "v1.0", "Payload Guardado")
        
        # Forzar recolección de basura destruyendo la referencia del objeto
        del cache_instance_a
        await asyncio.sleep(0.001)

        # Instancia B lee desde el mismo archivo físico
        cache_instance_b = SQLiteTranslationCache(db_path=self.test_db)
        persisted_result = await cache_instance_b.get("sha_persistent_999", "gemini-flash", "v1.0")
        
        self.assertEqual(persisted_result, "Payload Guardado", "La caché opera en memoria RAM volátil, falló la persistencia en disco.")