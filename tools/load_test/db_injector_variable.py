import os
import sys
import time
import uuid
import sqlite3
import argparse
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infra.db.control_repo import ControlPlaneRepository

def run_db_injection(target_docs: int, chunks_per_doc: int, db_path: str, mode: str):
    absolute_db = os.path.abspath(db_path)

    print("=" * 70, flush=True)
    print(f"      SOTA CONTROL PLANE INJECTOR - MODE: {mode.upper()}", flush=True)
    print("=" * 70, flush=True)

    start_time = time.perf_counter()
    conn = sqlite3.connect(absolute_db, timeout=10.0)
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")

    task_repo = ControlPlaneRepository(conn)
    injected_docs = 0
    injected_chunks = 0

    # Definición de la distribución asimétrica ponderada (Fase 3)
    # Promedia ~8.1 chunks por documento -> 600 docs * 8.1 = ~4,860 chunks
    chunk_sizes = [2, 6, 20, 60]
    weights = [0.50, 0.35, 0.10, 0.05]

    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM chunk_tasks")

        for _ in range(target_docs):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            ast_hash = f"hash_{uuid.uuid4().hex[:8]}"

            if mode == "variable":
                actual_chunks = random.choices(chunk_sizes, weights=weights, k=1)[0]
            else:
                actual_chunks = chunks_per_doc

            nodes = [f"node_{doc_id[-4:]}_{j}" for j in range(actual_chunks)]
            task_repo.enqueue_tasks(doc_id, ast_hash, nodes)

            injected_docs += 1
            injected_chunks += len(nodes)

        conn.commit()

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"[CRÍTICO] Colapso del injector: {e}", flush=True)
        sys.exit(1)
    finally:
        conn.close()

    delta = time.perf_counter() - start_time
    print(f"[OK] {injected_docs} documentos | {injected_chunks} chunks inyectados en {delta:.2f}s", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=int, default=200)
    parser.add_argument("--chunks", type=int, default=8)
    parser.add_argument("--db", type=str, default="./infra/db/queue.db")
    parser.add_argument("--mode", type=str, choices=["fixed", "variable"], default="fixed")
    args = parser.parse_args()

    run_db_injection(
        target_docs=args.docs,
        chunks_per_doc=args.chunks,
        db_path=args.db,
        mode=args.mode
    )