#!/usr/bin/env python3
"""
HITO_0.9 F0-D — T1-LOCAL Waste Measurement (v1.4.0)
==================================================
Todas las firmas verificadas por probe_firmas.py. Cero adivinación.
W3, W4, W6, W7, W8 medibles. W1/W2/W5 deferred a F18.
"""
import asyncio
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports" / "waste_t1"
SCHEMA_DIR = PROJECT_ROOT / "infra" / "db"
SMOKE_PDF_DIR = PROJECT_ROOT / "tests" / "corpus" / "workload" / "pdf"
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# DAMAGE CHECK — read-only sobre DBs productivas
# ============================================================================

def damage_check() -> dict:
    report: dict = {}
    for plane in ("queue", "fsm", "event", "materialized", "rate_limits"):
        db_path = PROJECT_ROOT / "infra" / "db" / f"{plane}.db"
        if not db_path.exists():
            report[plane] = {"exists": False}
            continue
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            counts: dict = {}
            for t in tables:
                try:
                    counts[t] = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
                except Exception as e:
                    counts[t] = f"err:{e}"
            try:
                mtime = os.path.getmtime(db_path)
            except OSError:
                mtime = None
            report[plane] = {
                "exists": True,
                "tables": tables,
                "row_counts": counts,
                "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime)) if mtime else None,
            }
            conn.close()
        except Exception as e:
            report[plane] = {"exists": True, "error": repr(e)}
    return report


# ============================================================================
# DB EFÍMERA
# ============================================================================

def ephemeral_db(plane: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix=f"waste_t1_{plane}_"))
    db_path = tmp / f"{plane}.db"
    schema_file = SCHEMA_DIR / f"schema_{plane}.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema no encontrado: {schema_file}")
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema_file.read_text(encoding="utf-8"))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.commit()
    conn.close()
    return db_path


# ============================================================================
# W3: QUOTA CONTENTION
# Firma verificada: QuotaManager(rpm_limit, tpm_limit, clock, store)
#                   reserve(estimated_tokens, estimated_requests=1)
# ============================================================================

def measure_w3() -> dict:
    try:
        from apps.llm_workers.rate_limiter import QuotaManager
        from core.execution.exceptions import QuotaTimeoutError, PermanentQuotaRejection
        from infra.resilience.sqlite_rate_limit_store import SQLiteRateLimitStore

        # Schema inline (no existe schema_rate_limits.sql)
        tmp = Path(tempfile.mkdtemp(prefix="waste_t1_rate_limits_"))
        db_path = tmp / "rate_limits.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_buckets (
                bucket_id   TEXT PRIMARY KEY,
                tokens      REAL NOT NULL,
                last_update REAL NOT NULL
            )
        """)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.commit()

        store = SQLiteRateLimitStore(conn)

        class FakeClock:
            def __init__(self) -> None:
                self.t = 1_700_000_000.0
            def now(self) -> float:
                self.t += 0.1
                return self.t

        qm = QuotaManager(rpm_limit=3, tpm_limit=100, clock=FakeClock(), store=store)

        async def drive() -> tuple[int, int, int, list[float]]:
            granted = 0
            timeouts = 0
            permanent = 0
            waits: list[float] = []
            for _ in range(20):
                t0 = time.monotonic()
                try:
                    r = await qm.reserve(estimated_tokens=20, estimated_requests=1)
                    waits.append((time.monotonic() - t0) * 1000)
                    reason = getattr(r, "rejection_reason", None)
                    if reason is not None:
                        reason_val = getattr(reason, "value", str(reason))
                        if reason_val in ("none", "NONE", "None"):
                            granted += 1
                        else:
                            permanent += 1
                    else:
                        granted += 1
                except QuotaTimeoutError:
                    timeouts += 1
                    waits.append(5000.0)
                except PermanentQuotaRejection:
                    permanent += 1
            return granted, timeouts, permanent, waits

        granted, timeouts, permanent, waits = asyncio.run(drive())
        conn.close()
        shutil.rmtree(tmp, ignore_errors=True)

        waits_sorted = sorted(waits) if waits else [0.0]
        p95_idx = min(int(len(waits_sorted) * 0.95), len(waits_sorted) - 1)
        return {
            "status": "MEASURED",
            "w3_total_calls": granted + timeouts + permanent,
            "w3_granted": granted,
            "w3_timeouts": timeouts,
            "w3_permanent_rejections": permanent,
            "w3_mean_wait_ms": round(sum(waits) / len(waits), 2) if waits else 0.0,
            "w3_p95_wait_ms": round(waits_sorted[p95_idx], 2),
        }
    except Exception as e:
        return {"status": "NOT_MEASURABLE", "reason": f"{type(e).__name__}: {e}"}


# ============================================================================
# W4: HEALING ROLLBACK
# Firmas verificadas:
#   HealingPipeline(validation_pipeline, strategies, registry=None)
#   heal_and_revalidate(context: HealingContext) -> HealingResult
#   make_test_healing_context(text, family, invariant_id, severity)
#   ValidationPipeline() sin args
#   MarkdownLeakageHealingStrategy() sin args
# ============================================================================

def measure_w4() -> dict:
    try:
        from core.healing.pipeline import HealingPipeline
        from core.healing.telemetry import HealingTelemetryRegistry
        from core.healing.testing_factories import make_test_healing_context
        from core.healing.strategies.markdown_leakage import MarkdownLeakageHealingStrategy
        from core.validation.pipeline import ValidationPipeline
        from core.validation.models import Severity

        registry = HealingTelemetryRegistry()
        validation_pipeline = ValidationPipeline()  # sin args, verificado
        strategy = MarkdownLeakageHealingStrategy()  # sin args, verificado

        pipeline = HealingPipeline(
            validation_pipeline=validation_pipeline,
            strategies=[strategy],
            registry=registry,
        )

        # make_test_healing_context(text, family, invariant_id, severity)
        # severity default = Severity.HARD_FAIL
        ctx = make_test_healing_context(
            text="This is a **test** with [markdown](http://example.com) leakage",
            family="markdown_leakage",
            invariant_id="INV-MD-001",
            severity=Severity.HARD_FAIL,
        )

        n_attempts = 10
        for _ in range(n_attempts):
            try:
                pipeline.heal_and_revalidate(ctx)
            except Exception:
                pass  # esperado: algunos pueden fallar

        events = registry.get_events()
        total = len(events)
        rollbacks = sum(1 for e in events if e.outcome == "ROLLBACK")
        successes = sum(1 for e in events if e.outcome == "SUCCESS")
        failures = sum(1 for e in events if e.outcome == "FAILURE")
        not_applicable = sum(1 for e in events if e.outcome == "NOT_APPLICABLE")

        return {
            "status": "MEASURED",
            "w4_healing_attempts": total,
            "w4_rollbacks": rollbacks,
            "w4_successes": successes,
            "w4_failures": failures,
            "w4_not_applicable": not_applicable,
            "w4_rollback_rate": round(rollbacks / total, 4) if total > 0 else 0.0,
        }
    except Exception as e:
        return {"status": "NOT_MEASURABLE", "reason": f"{type(e).__name__}: {e}"}


# ============================================================================
# W6: TELEMETRY LOSS (graceful vs abrupt)
# Firmas verificadas:
#   ProductionTelemetryEvent(execution_id, chunk_id, provider, event_type,
#                            selection_reason=None, latency_ms=0.0,
#                            quota_wait_ms=0.0, input_tokens=0, output_tokens=0)
#   SQLiteTelemetryGateway(db_path) con start()/stop() SÍNCRONOS
# ============================================================================

def measure_w6() -> dict:
    try:
        from core.telemetry.gateway import SQLiteTelemetryGateway
        from core.telemetry.models import ProductionTelemetryEvent, TelemetryEventType

        event_type_value = list(TelemetryEventType)[0]

        def make_event(exec_id: str, chunk_id: str) -> ProductionTelemetryEvent:
            return ProductionTelemetryEvent(
                execution_id=exec_id,
                chunk_id=chunk_id,
                provider="fake",
                event_type=event_type_value,
                latency_ms=50.0,
                quota_wait_ms=10.0,
                input_tokens=100,
                output_tokens=50,
            )

        def count_events(db_path: Path) -> int:
            if not db_path.exists():
                return 0
            try:
                conn = sqlite3.connect(str(db_path))
                count = conn.execute("SELECT COUNT(*) FROM telemetry_events").fetchone()[0]
                conn.close()
                return int(count)
            except sqlite3.OperationalError:
                return 0

        # --- Run G: graceful ---
        tmp_g = Path(tempfile.mkdtemp(prefix="waste_t1_tel_g_"))
        db_g = tmp_g / "production.db"
        # NO usar ephemeral_db: el gateway crea su propio schema en _init_db()

        async def graceful_run() -> None:
            gw = SQLiteTelemetryGateway(db_path=str(db_g))
            await gw.start()
            for i in range(200):
                gw.emit(make_event(f"exec_g_{i:04d}", f"chunk_{i}"))
            await gw.stop()

        asyncio.run(graceful_run())
        time.sleep(1.0)
        persisted_g = count_events(db_g)

        # --- Run K: abrupto ---
        tmp_k = Path(tempfile.mkdtemp(prefix="waste_t1_tel_k_"))
        db_k = tmp_k / "production.db"

        probe_code = (
            "import sys, os, asyncio\n"
            f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
            "from core.telemetry.gateway import SQLiteTelemetryGateway\n"
            "from core.telemetry.models import ProductionTelemetryEvent, TelemetryEventType\n"
            "\n"
            "async def run():\n"
            f"    gw = SQLiteTelemetryGateway(db_path={str(db_k)!r})\n"
            "    await gw.start()\n"
            "    et = list(TelemetryEventType)[0]\n"
            "    for i in range(200):\n"
            "        evt = ProductionTelemetryEvent(\n"
            '            execution_id=f"exec_k_{i:04d}", chunk_id=f"chunk_{i}",\n'
            '            provider="fake", event_type=et,\n'
            "            latency_ms=50.0, quota_wait_ms=10.0,\n"
            "            input_tokens=100, output_tokens=50)\n"
            "        gw.emit(evt)\n"
            "    os._exit(0)\n"
            "\n"
            "asyncio.run(run())\n"
        )
        subprocess.run(
            [sys.executable, "-c", probe_code],
            cwd=str(PROJECT_ROOT), capture_output=True, timeout=30,
        )
        time.sleep(1.0)
        persisted_k = count_events(db_k)

        shutil.rmtree(tmp_g, ignore_errors=True)
        shutil.rmtree(tmp_k, ignore_errors=True)

        lost = max(0, persisted_g - persisted_k)
        return {
            "status": "MEASURED",
            "w6_events_emitted": 200,
            "w6_persisted_graceful": persisted_g,
            "w6_persisted_abrupt": persisted_k,
            "w6_lost_events": lost,
            "w6_telemetry_loss_ratio": round(lost / persisted_g, 4) if persisted_g > 0 else 0.0,
        }
    except Exception as e:
        return {"status": "NOT_MEASURABLE", "reason": f"{type(e).__name__}: {e}"}


# ============================================================================
# W7: FAILED PERSISTENCE (zombie writes)
# Firmas verificadas:
#   ControlPlaneRepository(conn)
#   enqueue_tasks(document_id, ast_hash, nodes: List[str])
#   pick_task(worker_id, document_id, ast_hash) -> Optional[TaskLease]
#   acknowledge_execution(task_id, worker_id)
# ============================================================================

def measure_w7() -> dict:
    try:
        from infra.db.control_repo import ControlPlaneRepository
        from core.execution.exceptions import OptimisticLockError

        db_path = ephemeral_db("queue")
        conn = sqlite3.connect(str(db_path))
        repo = ControlPlaneRepository(conn)

        # Descubrir tabla de tareas dinámicamente
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        task_table = next((t for t in tables if "task" in t.lower()), None)
        if task_table is None:
            conn.close()
            return {"status": "NOT_MEASURABLE",
                    "reason": f"Tabla de tareas no encontrada. Tablas: {tables}"}

        # Encolar y reclamar
        repo.enqueue_tasks("doc_zombie", "hash_zombie", ["node_z_1"])
        lease = repo.pick_task("worker_A", "doc_zombie", "hash_zombie")
        if lease is None:
            conn.close()
            return {"status": "NOT_MEASURABLE", "reason": "pick_task no otorgó lease"}

        # Expirar lease al pasado
        past = time.time() - 600
        cols = [c[1] for c in conn.execute(f"PRAGMA table_info([{task_table}])").fetchall()]
        expires_col = next((c for c in cols if "expire" in c.lower()), None)
        if expires_col is None:
            conn.close()
            return {"status": "NOT_MEASURABLE",
                    "reason": f"Columna de expiración no encontrada. Cols: {cols}"}

        conn.execute(
            f"UPDATE [{task_table}] SET {expires_col}=? WHERE task_id=?",
            (past, lease.task_id),
        )
        conn.commit()

        # Worker B roba la tarea
        lease_b = repo.pick_task("worker_B", "doc_zombie", "hash_zombie")

        # Worker A (expirado) intenta ack → debe fallar con OptimisticLockError
        intercepted = 0
        attempts = 1
        try:
            repo.acknowledge_execution(lease.task_id, "worker_A")
        except OptimisticLockError:
            intercepted += 1
        except Exception:
            pass

        conn.close()
        shutil.rmtree(db_path.parent, ignore_errors=True)

        return {
            "status": "MEASURED",
            "w7_task_table": task_table,
            "w7_expires_column": expires_col,
            "w7_zombie_attempts": attempts,
            "w7_intercepted": intercepted,
            "w7_interception_rate": round(intercepted / attempts, 4) if attempts > 0 else 0.0,
            "w7_task_stolen_by_worker_b": lease_b is not None,
        }
    except Exception as e:
        return {"status": "NOT_MEASURABLE", "reason": f"{type(e).__name__}: {e}"}


# ============================================================================
# W8: PROFILE RE-INFERENCE
# Firmas verificadas:
#   build_document_profiler() -> HeuristicDocumentProfiler
#   profiler.profile(input_data: ProfileInput) -> ProfilingResult
#   ProfileInput(nodes: Sequence[ASTNode])
# ============================================================================

def measure_w8() -> dict:
    try:
        from apps.bootstrap.pipeline_factory import build_document_profiler, build_extraction_pipeline
        from core.document_profile.models import ProfileInput

        pdfs = sorted(SMOKE_PDF_DIR.glob("*.pdf"))
        if not pdfs:
            return {"status": "NOT_MEASURABLE",
                    "reason": f"SMOKE vacío en {SMOKE_PDF_DIR}"}

        # Extraer AST real del primer PDF SMOKE
        pipeline = build_extraction_pipeline()
        ast_nodes = pipeline.parse(str(pdfs[0]))
        if not ast_nodes:
            return {"status": "NOT_MEASURABLE", "reason": "pipeline.parse devolvió vacío"}

        input_data = ProfileInput(nodes=ast_nodes)

        # Run A: profiler cold (instancia nueva)
        profiler_a = build_document_profiler()
        t0 = time.perf_counter()
        for _ in range(3):
            profiler_a.profile(input_data)
        cold_ms = (time.perf_counter() - t0) * 1000

        # Run B: profiler warm (mismo objeto, segunda tanda)
        t0 = time.perf_counter()
        for _ in range(3):
            profiler_a.profile(input_data)
        warm_ms = (time.perf_counter() - t0) * 1000

        # Run C: nuevo profiler frío (simula STATE_LOSS de ProfileStore)
        profiler_c = build_document_profiler()
        t0 = time.perf_counter()
        for _ in range(3):
            profiler_c.profile(input_data)
        new_cold_ms = (time.perf_counter() - t0) * 1000

        return {
            "status": "MEASURED",
            "w8_pdf_used": pdfs[0].name,
            "w8_ast_node_count": len(ast_nodes),
            "w8_cold_ms": round(cold_ms, 2),
            "w8_warm_ms": round(warm_ms, 2),
            "w8_new_cold_ms": round(new_cold_ms, 2),
            "w8_reinference_ms": round(new_cold_ms - warm_ms, 2),
        }
    except Exception as e:
        return {"status": "NOT_MEASURABLE", "reason": f"{type(e).__name__}: {e}"}


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("HITO_0.9 F0-D — T1-LOCAL Waste Measurement v1.4.0")
    print("=" * 70)

    print("\n[DAMAGE CHECK] DBs productivas (read-only):")
    damage = damage_check()
    for plane, info in damage.items():
        if info.get("exists"):
            counts = info.get("row_counts", {})
            total = sum(v for v in counts.values() if isinstance(v, int))
            ntables = len(info.get("tables", []))
            print(f"  {plane:15s} tables={ntables:2d}  total_rows={total:6d}  mtime={info.get('mtime_iso')}")
        else:
            print(f"  {plane:15s} NOT FOUND")

    print("\n[MEDICIONES] Ejecutando canales...")
    results: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "wrapper_version": "1.4.0",
        "scope": "T1-LOCAL",
        "deferred_to_F18": ["W1_duplicate_effect", "W2_cb_post_restart", "W5_post_cancel_io"],
        "deferred_reason": (
            "Sin override de base_url en SDKs reales; redirigir worker a fake "
            "provider exigiría código productivo nuevo (Charter §5.3)"
        ),
        "damage_check": damage,
        "channels": {},
    }

    channels = [
        ("W3_quota", measure_w3),
        ("W4_healing", measure_w4),
        ("W6_telemetry", measure_w6),
        ("W7_persistence", measure_w7),
        ("W8_profile", measure_w8),
    ]

    for name, fn in channels:
        print(f"\n  [{name}] ...")
        result = fn()
        results["channels"][name] = result
        print(f"  [{name}] -> {result['status']}")

    ts = results["timestamp"].replace(":", "-")
    out = REPORTS_DIR / f"baseline_t1_local_{ts}.json"
    out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\n[SAVE] {out}")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()