import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, isolation_level="IMMEDIATE")
    # SOTA: Ajustado a 5s para revelar starvation rápidamente en logs 
    # en lugar de enmascararla con hilos congelados 30s.
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn