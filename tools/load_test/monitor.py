import os
import sys
import time
import sqlite3

def start_telemetry(db_path: str, interval_sec: float = 3.0):
    absolute_db = os.path.abspath(db_path)
    print(f"[DEBUG] Inicializando Monitor. Buscando DB en: {absolute_db}", flush=True)
    
    if not os.path.exists(absolute_db):
        print("[INFO] Esperando inicializacion fisica del archivo control.db...", flush=True)
        while not os.path.exists(absolute_db):
            time.sleep(0.5)

    print("=" * 85, flush=True)
    print("      SOTA HIGH-FIDELITY TELEMETRY MONITOR - VERBOSE HARDENING (8B)", flush=True)
    print("=" * 85, flush=True)

    last_completed = 0
    last_pending = 0
    consecutive_empty_windows = 0
    REQUIRED_STABLE_WINDOWS = 3
    start_time = time.perf_counter()
    db_uri = f"file:{absolute_db}?mode=ro"

    while True:
        try:
            now_epoch = int(time.time())
            conn_start = time.perf_counter()
            conn = sqlite3.connect(db_uri, uri=True, timeout=1.0)
            conn.execute("PRAGMA busy_timeout = 1000")
            conn.execute("PRAGMA query_only = ON")
            conn.row_factory = sqlite3.Row
            conn_latency = time.perf_counter() - conn_start
            
            cursor = conn.cursor()
            exec_start = time.perf_counter()
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN task_state = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN task_state = 'PENDING' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN task_state = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN task_state = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN task_state = 'PROCESSING' AND lease_expires_at < {now_epoch} THEN 1 ELSE 0 END) as orphans,
                    MIN(CASE WHEN task_state = 'PENDING' THEN created_at END) as oldest_pending,
                    MAX(retry_count) as max_retries
                FROM chunk_tasks
            """)
            row = cursor.fetchone()
            exec_latency = time.perf_counter() - exec_start
            
            wal_size_mb = 0.0
            if os.path.exists(f"{absolute_db}-wal"):
                wal_size_mb = os.path.getsize(f"{absolute_db}-wal") / (1024 * 1024)
            conn.close()

            total = row["total"] or 0
            completed = row["completed"] or 0
            pending = row["pending"] or 0
            processing = row["processing"] or 0
            failed = row["failed"] or 0
            orphans = row["orphans"] or 0
            oldest_pending = row["oldest_pending"]
            max_retries = row["max_retries"] or 0

            aging_sec = max(0, now_epoch - int(oldest_pending)) if oldest_pending else 0
            delta_completed = completed - last_completed
            instant_throughput = delta_completed / interval_sec
            last_completed = completed
            backlog_growth = (pending - last_pending) / interval_sec if last_pending > 0 else 0.0
            last_pending = pending
            elapsed = time.perf_counter() - start_time

            # Inyección de la variable 'failed' en la consola para monitoreo forense
            print(f"T+{elapsed:5.1f}s | Conn: {conn_latency:6.4f}s | Exec: {exec_latency:6.4f}s | Backlog: {pending:4d} ({backlog_growth:+.1f}/s) | ERR_PERM: {failed:3d} | MaxAge: {aging_sec}s | MaxRetries: {max_retries:2d} | Zombies: {orphans:2d} | THR: {instant_throughput:5.1f} chk/s | WAL: {wal_size_mb:5.2f} MB", flush=True)

            # Si hay chunks en FAILED definitivo, el benchmark debe terminar por colapso, no por éxito
            if total > 0 and pending == 0 and processing == 0 and orphans == 0:
                consecutive_empty_windows += 1
                if consecutive_empty_windows >= REQUIRED_STABLE_WINDOWS:
                    print("-" * 85, flush=True)
                    print(f"=== BENCHMARK CONVERGIDO EN {elapsed:.2f} SEGUNDOS ===", flush=True)
                    print(f"Throughput Promedio Sostenido: {completed / elapsed:.2f} valid_chunks/sec", flush=True)
                    break
            else:
                consecutive_empty_windows = 0
            time.sleep(interval_sec)
        except KeyboardInterrupt:
            print("\n[INFO] Monitoreo abortado.", flush=True)
            sys.exit(0)
        except Exception as err:
            # Revelar de inmediato la causa raíz en la consola
            print(f"[CRÍTICO RUNTIME] Error interno en loop de monitoreo: {err}", flush=True)
            time.sleep(2.0)

if __name__ == "__main__":
    # Redirección estricta al plano de colas segregado físico
    start_telemetry(db_path=os.getenv("QUEUE_DB_PATH", "./infra/db/queue.db"))