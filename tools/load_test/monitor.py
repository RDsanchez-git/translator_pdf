import os
import time
import json
import sqlite3
import argparse
from collections import deque

def calculate_percentile(data, p):
    if not data:
        return 0.0
    sorted_data = sorted(data) # Funciona nativamente con deques
    idx = min(int(len(sorted_data) * p), len(sorted_data) - 1)
    return sorted_data[idx]

def start_telemetry(db_path: str, output_path: str, interval_sec: float = 3.0, quiet: bool = False):
    absolute_db = os.path.abspath(db_path)
    output_path = os.path.abspath(output_path)
    
    # SOTA Directory Hardening: Asegura la ruta para dumps .live antes de entrar al bucle
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"[DEBUG] Inicializando Monitor. Buscando DB en: {absolute_db}", flush=True)
    
    if not os.path.exists(absolute_db):
        print("[INFO] Esperando inicializacion fisica del archivo control.db...", flush=True)
        while not os.path.exists(absolute_db):
            time.sleep(0.5)

    print("=" * 85, flush=True)
    print("      SOTA HIGH-FIDELITY TELEMETRY MONITOR - VERBOSE HARDENING (8B)", flush=True)
    print("=" * 85, flush=True)

    # SOTA Circular Buffers: Consumo O(1) inmune a fugas en Soak Testing
    history_throughput = deque(maxlen=50000)
    history_smoothed_thr = deque(maxlen=50000)
    history_conn_latency = deque(maxlen=50000)
    history_exec_latency = deque(maxlen=50000)
    history_wal_size = deque(maxlen=50000)
    history_wal_growth = deque(maxlen=50000)
    
    # Variables de control para Ajuste 1 (Suavizado)
    window_completed = 0
    window_elapsed = 0.0
    
    # Variables de control para Ajuste 2 (Starvation Real)
    consecutive_low_thr_windows = 0
    starvation_events_count = 0
    
    # Contadores de eventos de infraestructura
    wal_checkpoints_detected = 0
    lock_spikes_5ms = 0
    lock_spikes_10ms = 0
    last_wal_size_mb = 0.0
    initial_backlog = None
    last_printed_elapsed = -30.0
    last_live_dump_time = 0.0

    last_completed = 0
    consecutive_empty_windows = 0
    REQUIRED_STABLE_WINDOWS = 3
    start_time = time.perf_counter()
    db_uri = f"file:{absolute_db}?mode=ro"

    # SOTA Scope Initialization: Previene reportWithUnboundVariable en Pylance
    completed = 0
    pending = 0
    failed = 0
    orphans = 0
    max_retries = 0
    elapsed = 0.0

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
            max_retries = row["max_retries"] or 0

            if initial_backlog is None:
                initial_backlog = pending

            
            delta_completed = completed - last_completed
            instant_throughput = delta_completed / interval_sec
            last_completed = completed
            elapsed = time.perf_counter() - start_time

            # Ajuste 3: Medición de Deriva del WAL (Drift Rate)
            wal_growth_rate = wal_size_mb - last_wal_size_mb
            history_wal_growth.append(wal_growth_rate)

            # Ajuste 1: Suavizado de Throughput Movil (Ventanas de 30s)
            window_completed += delta_completed
            window_elapsed += interval_sec
            if window_elapsed >= 30.0:
                smoothed_thr = window_completed / window_elapsed
                history_smoothed_thr.append(smoothed_thr)
                window_completed = 0
                window_elapsed = 0.0

            # Guardado en buffers
            history_conn_latency.append(conn_latency)
            history_exec_latency.append(exec_latency)
            history_wal_size.append(wal_size_mb)
            if elapsed > interval_sec:
                history_throughput.append(instant_throughput)

            # Ajuste 2: Detección de Starvation Real mediante Media Móvil Dinámica (Fase 3 Hardening)
            if len(history_throughput) > 5:
                running_avg = sum(history_throughput) / len(history_throughput)
                if instant_throughput < (running_avg * 0.10):
                    consecutive_low_thr_windows += 1
                    if consecutive_low_thr_windows >= 4:
                        starvation_events_count += 1
                        consecutive_low_thr_windows = 0  # Reseteo de ciclo para evitar falsos positivos continuos
                        if not quiet:
                            print("\n[ALERTA] STARVATION_EVENT detectado. Inanición estructural sostenida en canal de control.", flush=True)
                else:
                    consecutive_low_thr_windows = 0

            # Detección de Eventos: Lock contention
            if exec_latency > 0.010:
                lock_spikes_10ms += 1
            elif exec_latency > 0.005:
                lock_spikes_5ms += 1

            # Detección de Eventos: Checkpoint del WAL
            if wal_size_mb < last_wal_size_mb * 0.5 and last_wal_size_mb > 0.5:
                wal_checkpoints_detected += 1
                if not quiet:
                    print(f"\n[EVENTO] WAL Checkpoint Detectado: {last_wal_size_mb:.2f} MB -> {wal_size_mb:.2f} MB", flush=True)

            # Ajuste 4: Persistencia Incremental en Caliente (Cada 60s)
            if elapsed - last_live_dump_time >= 60.0:
                partial_report = {
                    "elapsed_seconds": round(elapsed, 2),
                    "current_backlog": pending,
                    "running_avg_thr": round(sum(history_throughput)/len(history_throughput), 2) if history_throughput else 0.0,
                    "starvation_events": starvation_events_count,
                    "max_wal_reached": round(max(history_wal_size), 2) if history_wal_size else 0.0
                }
                with open(f"{output_path}.live", "w") as lf:
                    json.dump(partial_report, lf, indent=2)
                last_live_dump_time = elapsed

            # Reducción de verbosidad periódica sin variables huérfanas
            should_print = (elapsed - last_printed_elapsed >= 30.0) or (failed > 0) or (orphans > 0)
            if not quiet and should_print:
                print(f"T+{elapsed:5.1f}s | Conn: {conn_latency:6.4f}s | Exec: {exec_latency:6.4f}s | Backlog: {pending:4d} | ERR_PERM: {failed:3d} | Zombies: {orphans:2d} | THR: {instant_throughput:5.1f} chk/s | WAL: {wal_size_mb:5.2f} MB", flush=True)
                last_printed_elapsed = elapsed

            if total > 0 and pending == 0 and processing == 0 and orphans == 0:
                consecutive_empty_windows += 1
                if consecutive_empty_windows >= REQUIRED_STABLE_WINDOWS:
                    print("-" * 85, flush=True)
                    print(f"=== BENCHMARK CONVERGIDO EN {elapsed:.2f} SEGUNDOS ===", flush=True)
                    break
            else:
                consecutive_empty_windows = 0
                
            last_wal_size_mb = wal_size_mb
            time.sleep(interval_sec)
            
        except KeyboardInterrupt:
            print("\n[INFO] Monitoreo abortado por usuario. Salvando datos parciales...", flush=True)
            break
        except Exception as err:
            print(f"[CRÍTICO RUNTIME] Error interno en loop de monitoreo: {err}", flush=True)
            time.sleep(2.0)

    # Reporte de Cierre Consolidado
    avg_thr = sum(history_throughput) / len(history_throughput) if history_throughput else (completed / elapsed)
    peak_thr = max(history_throughput) if history_throughput else avg_thr
    min_thr = min([t for t in history_throughput if t > 0.0]) if [t for t in history_throughput if t > 0.0] else 0.0
    
    avg_exec = sum(history_exec_latency) / len(history_exec_latency) if history_exec_latency else 0.0
    p95_exec = calculate_percentile(history_exec_latency, 0.95)
    p99_exec = calculate_percentile(history_exec_latency, 0.99)
    max_spike = max(history_exec_latency) if history_exec_latency else 0.0
    max_wal = max(history_wal_size) if history_wal_size else 0.0
    
    avg_wal_growth = sum([g for g in history_wal_growth if g > 0]) / len([g for g in history_wal_growth if g > 0]) if [g for g in history_wal_growth if g > 0] else 0.0
    peak_wal_growth = max(history_wal_growth) if history_wal_growth else 0.0

    summary_report = {
        "benchmark_meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "initial_backlog": initial_backlog,
            "duration_seconds": round(elapsed, 2)
        },
        "performance": {
            "avg_throughput_chk_s": round(avg_thr, 2),
            "peak_throughput_chk_s": round(peak_thr, 2),
            "min_throughput_chk_s": round(min_thr, 2),
            "smoothed_segments_30s": [round(s, 2) for s in history_smoothed_thr]
        },
        "latency_exec_seconds": {
            "avg": round(avg_exec, 6),
            "p95": round(p95_exec, 6),
            "p99": round(p99_exec, 6),
            "max_spike": round(max_spike, 6)
        },
        "sqlite_infrastructure": {
            "max_wal_size_mb": round(max_wal, 2),
            "avg_wal_growth_rate_mb": round(avg_wal_growth, 4),
            "peak_wal_growth_rate_mb": round(peak_wal_growth, 4),
            "wal_checkpoints_detected": wal_checkpoints_detected,
            "lock_spikes_5ms": lock_spikes_5ms,
            "lock_spikes_10ms": lock_spikes_10ms,
            "starvation_events_recorded": starvation_events_count
        },
        "fsm_integrity": {
            "zombies": orphans,
            "retries": max_retries,
            "err_perm": failed
        },
        "result": "PASS" if failed == 0 and orphans == 0 and starvation_events_count == 0 else "FAIL"
    }

    print("\n" + "=" * 50)
    print("=== BENCHMARK SUMMARY ===")
    print("=" * 50)
    print(f"Total Chunks Processed : {initial_backlog}")
    print(f"Avg / Peak Throughput  : {summary_report['performance']['avg_throughput_chk_s']} / {summary_report['performance']['peak_throughput_chk_s']} chk/s")
    print(f"Latency P95 / P99      : {summary_report['latency_exec_seconds']['p95']:.4f}s / {summary_report['latency_exec_seconds']['p99']:.4f}s")
    print(f"WAL Checkpoints        : {summary_report['sqlite_infrastructure']['wal_checkpoints_detected']}")
    print(f"WAL Avg Growth Rate    : {summary_report['sqlite_infrastructure']['avg_wal_growth_rate_mb']} MB/s")
    print(f"Starvation Events      : {summary_report['sqlite_infrastructure']['starvation_events_recorded']}")
    print(f"FSM Integrity Result   : {summary_report['result']}")
    print("=" * 50)

    print("=" * 50)

    with open(output_path, "w") as f:
        json.dump(summary_report, f, indent=2)
        
    # Remover dump incremental si el proceso cerró de forma nativa
    if os.path.exists(f"{output_path}.live"):
        os.remove(f"{output_path}.live")
        
    print(f"[OK] Historial del run persistido en: {output_path}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, default=os.getenv("QUEUE_DB_PATH", "./infra/db/queue.db"))
    parser.add_argument("--output", type=str, default="./benchmarks/snapshot_latest.json")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    start_telemetry(db_path=args.db, output_path=args.output, quiet=args.quiet)