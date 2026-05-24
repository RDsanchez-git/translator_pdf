import os
import sys
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from infra.db.connection import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("db_bootstrap")

# Matriz de Configuración SOTA para el Triple Plane Split
DB_CONFIGS = {
    "infra/db/control.db": "infra/db/schema_control.sql",
    "infra/db/event.db": "infra/db/schema_event.sql",
    "infra/db/materialized.db": "infra/db/schema_materialized.sql"
}

def bootstrap_all_databases():
    logger.info("=========================================================")
    logger.info("   STARTING TRIPLE PLANE SPLIT INFRASTRUCTURE BOOTSTRAP  ")
    logger.info("=========================================================")
    
    Path("infra/db").mkdir(parents=True, exist_ok=True)

    for db_path, schema_path in DB_CONFIGS.items():
        logger.info(f"Evaluando plano de persistencia: {db_path}")
        
        if not os.path.exists(schema_path):
            logger.critical(f"Error de consistencia: Script DDL ausente en {schema_path}")
            sys.exit(1)
            
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl_sql = f.read()
            
        conn = None
        try:
            conn = get_connection(db_path, timeout=30)
            
            # Ajustes de pragmas iniciales de performance
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            
            # Aplicar estrictamente el DDL correspondiente a su plano
            conn.executescript(ddl_sql)
            
            # AJUSTE 2: Commit explícito defensivo post-DDL
            conn.commit()
            
            # AJUSTE 3: Truncate del WAL para garantizar archivos compactos y en frío
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            conn.close()
            logger.info(f"Ok: {db_path} estructurada limpiamente con {schema_path}.")
            
        except Exception as err:
            logger.error(f"Fallo crítico inicializando el plano {db_path}: {err}")
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            sys.exit(1)
            
    logger.info("=========================================================")
    logger.info("   BOOTSTRAP TPS EXITOSO - PLATAFORMA LISTA PARA CARGA   ")
    logger.info("=========================================================")

if __name__ == "__main__":
    bootstrap_all_databases()