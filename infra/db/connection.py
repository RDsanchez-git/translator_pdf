import sqlite3
from typing import Optional
from core.utils.fs import ensure_parent_dir


def get_connection(
    db_path: str,
    timeout: Optional[float] = None,
    isolation_level=None
) -> sqlite3.Connection:

    ensure_parent_dir(db_path)

    if timeout is None:
        conn = sqlite3.connect(
            db_path,
            isolation_level=isolation_level,
            check_same_thread=False # Parche, luego quitar para mudar a multi threads
        )
    else:
        conn = sqlite3.connect(
            db_path,
            timeout=timeout,
            isolation_level=isolation_level,
            check_same_thread=False # Parche, luego quitar para mudar a multi threads
        )

    # SOTA: Ajustado a 5s para revelar starvation rápidamente
    # en lugar de enmascararla con hilos congelados 30s.
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn