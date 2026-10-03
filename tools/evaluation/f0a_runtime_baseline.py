#!/usr/bin/env python3
"""
F0-A Runtime Profile Baseline Measurement Script v3 (FINAL).
HITO_0.6 reconciliation + process-tree memory fix + refinements 1-2.

Refinamiento 1: peak_tree_ws (informativo) vs peak_single_process_ws (baseline).
Refinamiento 2: Diccionario acumulativo de picos por PID + child_pids_observed.

Platform note (HITO_0.7 mandatory):
  On this Windows venv, `sys.executable -m ...` ALWAYS spawns a child
  worker process. All future instruments (F0-D provider metrics,
  profiling, tracing) MUST use tree-monitoring. Single-process
  measurement is structurally invalid in this environment.
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
import subprocess
import tempfile
import psutil
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# WIN32 MEMORY CHANNEL (defined BEFORE sample_tree_memory)
# ═══════════════════════════════════════════════════════════════════
_WIN32_AVAILABLE = sys.platform == "win32"

if _WIN32_AVAILABLE:
    import ctypes
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _psapi = ctypes.WinDLL("psapi", use_last_error=True)

    class _PMC(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    def _sample_win32(pid: int) -> tuple[float, float]:
        """(WorkingSet MB, PeakWorkingSet MB) via Win32 GetProcessMemoryInfo.
        PeakWorkingSetSize is retroactive per-process: even if we attach
        late, the kernel-recorded peak is captured."""
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        h = _k32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
        )
        if not h:
            return 0.0, 0.0
        try:
            pmc = _PMC()
            pmc.cb = ctypes.sizeof(pmc)
            if _psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb):
                ws = pmc.WorkingSetSize / 1_048_576
                peak_ws = pmc.PeakWorkingSetSize / 1_048_576
                return ws, peak_ws
            return 0.0, 0.0
        finally:
            _k32.CloseHandle(h)


# ═══════════════════════════════════════════════════════════════════
# PROCESS TREE SAMPLING (Refinamiento 2: per-PID peak dict)
# ═══════════════════════════════════════════════════════════════════
def sample_tree_memory(
    root_proc,
) -> tuple[float, dict[int, float], float, float]:
    """
    Monitors the ENTIRE process tree (parent launcher + child worker).

    Returns:
        tree_ws_mb:        Sum of current WorkingSet across all processes
                           (INFORMATIVE: double-counts shared DLL pages).
        per_pid_peak:      Dict {pid: PeakWorkingSetSize MB} for this sample.
                           PeakWorkingSetSize is kernel-recorded, retroactive.
        total_cpu_user:    Sum of user CPU time across tree.
        total_cpu_system:  Sum of system CPU time across tree.

    Critical: venv python.exe on Windows spawns a child worker process.
    Monitoring only the parent gives ~3 MB instead of the real ~40 MB.
    """
    processes = [root_proc]
    try:
        processes += root_proc.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    tree_ws = 0.0
    per_pid_peak: dict[int, float] = {}
    total_cpu_user = 0.0
    total_cpu_system = 0.0

    for p in processes:
        try:
            pid = p.pid
            if _WIN32_AVAILABLE:
                ws, kernel_peak = _sample_win32(pid)
                tree_ws += ws
                per_pid_peak[pid] = kernel_peak
            else:
                mem = p.memory_info()
                ws = mem.rss / 1_048_576
                tree_ws += ws
                per_pid_peak[pid] = ws  # No kernel peak on non-Windows

            ct = p.cpu_times()
            total_cpu_user += ct.user
            total_cpu_system += ct.system
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return tree_ws, per_pid_peak, total_cpu_user, total_cpu_system


MEMORY_CHANNEL = (
    "win32_GetProcessMemoryInfo_process_tree"
    if _WIN32_AVAILABLE
    else "psutil_process_tree_UNVERIFIED"
)

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
CANONICAL_DIR = Path("tests/corpus/canonical")
CANONICAL_PDF_DIR = CANONICAL_DIR / "pdf"
CANONICAL_GT_DIR = CANONICAL_DIR / "ground_truth"
CANONICAL_MANIFEST = CANONICAL_DIR / "manifest.json"
OUTPUT_DIR = Path("reports/f0a_baseline")

NUM_REPETITIONS = 3
COLD_CACHE = True

# Exit codes that do NOT invalidate measurement (NADR-27 / DF-10)
# 0=PASS, 1=WARNING, 2=REGRESSION (HARD_FAIL basal expected)
VALID_EXIT_CODES = {0, 1, 2}

# Acceptance criteria for HITO_0.7
MIN_PEAK_WS_MB = 20.0
MAX_PEAK_WS_MB = 200.0
MIN_CPU_SEC = 0.1
MAX_CV_PCT = 20.0


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def get_hardware_envelope() -> dict:
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    cpu_count = psutil.cpu_count(logical=True)
    return {"ram_gb": ram_gb, "cpu_count": cpu_count}


def canonical_snapshot() -> str:
    """Pre/post mutation checksum (GAP-0.6-01)."""
    h = hashlib.sha256()
    for base in (CANONICAL_DIR, CANONICAL_PDF_DIR, CANONICAL_GT_DIR):
        if not base.exists():
            continue
        for p in sorted(base.glob("*")):
            if p.is_file():
                h.update(p.name.encode("utf-8"))
                file_hash = hashlib.sha256()
                with open(p, "rb") as f:
                    while chunk := f.read(8 * 1024 * 1024):
                        file_hash.update(chunk)
                h.update(file_hash.digest())
    return h.hexdigest()


def clean_cache() -> None:
    """Only cleans telemetry DB. Operational DBs isolated via env vars."""
    telemetry_db = Path("infra/telemetry/production.db")
    if telemetry_db.exists():
        telemetry_db.unlink()
    for ext in ["-wal", "-shm"]:
        wal = telemetry_db.with_suffix(telemetry_db.suffix + ext)
        if wal.exists():
            wal.unlink()


def clean_cv_reports(out_dir: Path) -> None:
    """Remove previous CV reports so read_cv_anchor reads the fresh one."""
    for f in out_dir.glob("regression_report_*.json"):
        f.unlink(missing_ok=True)
    for f in out_dir.glob("regression_report*.md"):
        f.unlink(missing_ok=True)


def read_cv_anchor(out_dir: Path) -> dict:
    """Anchor scientific evidence from CV report (Defecto 2 fix)."""
    reps = sorted(out_dir.glob("regression_report_*.json"))
    if not reps:
        return {}
    try:
        d = json.loads(reps[-1].read_text(encoding="utf-8"))
        rr = d.get("regression_report") or {}
        return {
            "coverage": d.get("coverage"),
            "corpus_verdict": rr.get("corpus_verdict"),
            "corpus_nss": rr.get("corpus_nss"),
            "report_file": reps[-1].name,
        }
    except Exception:
        return {}


def get_sqlite_stats(db_path: Path) -> dict:
    """SQLite stats on ephemeral DBs (Defecto 3 fix)."""
    if not db_path.exists():
        return {}
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.execute("PRAGMA wal_checkpoint;")
        checkpoint = cursor.fetchone()
        page_count = conn.execute("PRAGMA page_count;").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size;").fetchone()[0]
        conn.close()
        return {
            "wal_checkpoint": checkpoint,
            "page_count": page_count,
            "page_size": page_size,
        }
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════
# MEASUREMENT
# ═══════════════════════════════════════════════════════════════════
def run_measurement(repetition: int, env: dict) -> dict:
    print(f"\n  --- Repetition {repetition} of {NUM_REPETITIONS} ---")

    clean_cv_reports(OUTPUT_DIR)

    stderr_path = OUTPUT_DIR / f"rep{repetition}_stderr.log"
    stderr_file = open(stderr_path, "wb")

    cmd = [
        sys.executable, "-m", "tools.evaluation.run_regression",
        "--corpus-dir", str(CANONICAL_DIR),
        "--pdf-dir", str(CANONICAL_PDF_DIR),
        "--output-dir", str(OUTPUT_DIR),
        "--profile", "SMOKE",
    ]

    start_time = time.time()
    process = psutil.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=stderr_file,
        env=env,
    )

    # ── Refinamiento 2: acumulativo por PID ─────────────────────────
    kernel_peaks_by_pid: dict[int, float] = {}
    peak_tree_ws_mb = 0.0
    cpu_user_sec = 0.0
    cpu_system_sec = 0.0
    tree_ws_series: list[float] = []
    child_count_max = 0

    # CRITICAL: Wait for venv launcher to spawn the child worker
    time.sleep(0.3)

    try:
        while process.poll() is None:
            try:
                tree_ws, per_pid_peak, cu, cs = sample_tree_memory(process)

                if tree_ws > 0:
                    tree_ws_series.append(tree_ws)
                    if tree_ws > peak_tree_ws_mb:
                        peak_tree_ws_mb = tree_ws
                    cpu_user_sec = cu
                    cpu_system_sec = cs

                # Refinamiento 2: accumulate per-PID peaks (monotonic)
                for pid, kp in per_pid_peak.items():
                    if kp > kernel_peaks_by_pid.get(pid, 0.0):
                        kernel_peaks_by_pid[pid] = kp

                # Track child count
                try:
                    children = process.children(recursive=True)
                    if len(children) > child_count_max:
                        child_count_max = len(children)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                time.sleep(0.1)
            except psutil.NoSuchProcess:
                break
    except Exception as e:
        print(f"    Warning during monitoring: {e}")

    process.communicate()
    stderr_file.close()
    end_time = time.time()

    # Final tree read (children may still be alive briefly)
    try:
        _, final_peaks, cu, cs = sample_tree_memory(process)
        for pid, kp in final_peaks.items():
            if kp > kernel_peaks_by_pid.get(pid, 0.0):
                kernel_peaks_by_pid[pid] = kp
        cpu_user_sec = max(cpu_user_sec, cu)
        cpu_system_sec = max(cpu_system_sec, cs)
    except Exception:
        pass

    wall_time_sec = round(end_time - start_time, 3)
    total_cpu_sec = round(cpu_user_sec + cpu_system_sec, 3)

    # ── Refinamiento 1: métricas separadas ──────────────────────────
    # peak_single_process_ws = max kernel peak across all PIDs (BASELINE)
    # peak_tree_ws = max of tree sum (INFORMATIVE, double-counts shared)
    peak_single_process_ws = (
        max(kernel_peaks_by_pid.values()) if kernel_peaks_by_pid else 0.0
    )
    parent_pid = process.pid
    child_pids = sorted(
        pid for pid in kernel_peaks_by_pid if pid != parent_pid
    )

    cv_anchor = read_cv_anchor(OUTPUT_DIR)

    return {
        "repetition": repetition,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "wall_time_sec": wall_time_sec,
        "cpu_time_sec": total_cpu_sec,
        # ── Refinamiento 1: baseline metric ──
        "peak_working_set_mb": round(peak_single_process_ws, 2),
        "peak_single_process_ws_mb": round(peak_single_process_ws, 2),
        # ── Refinamiento 1: informative ──
        "peak_tree_ws_mb": round(peak_tree_ws_mb, 2),
        # ── Refinamiento 2: per-PID evidence ──
        "kernel_peaks_by_pid": {
            str(pid): round(ws, 2) for pid, ws in sorted(kernel_peaks_by_pid.items())
        },
        "parent_pid": parent_pid,
        "child_pids_observed": child_pids,
        "max_child_processes": child_count_max,
        # ── Series ──
        "tree_ws_series_samples": len(tree_ws_series),
        "tree_ws_series_max_mb": round(max(tree_ws_series), 2) if tree_ws_series else 0.0,
        "tree_ws_series_min_mb": round(min(tree_ws_series), 2) if tree_ws_series else 0.0,
        # ── Result ──
        "exit_code": process.returncode,
        "stderr_file": str(stderr_path),
        "cv_anchor": cv_anchor,
        "memory_channel": MEMORY_CHANNEL,
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
def main() -> None:
    print("=" * 80)
    print("F0-A Runtime Profile Baseline v3 FINAL")
    print("  Process-tree monitoring + per-PID kernel peaks")
    print("  HITO_0.6: Read-only over canonical corpus")
    print(f"  Memory channel: {MEMORY_CHANNEL}")
    print("=" * 80)

    if not CANONICAL_PDF_DIR.exists() or not CANONICAL_MANIFEST.exists():
        print("ERROR: Canonical corpus not found.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    hardware = get_hardware_envelope()
    print(f"Hardware: {hardware['ram_gb']}GB RAM, {hardware['cpu_count']} CPUs")
    print("Target: 16GB/4GB (NOT CONFORMANT - HITO_0.6 E-0.6-006)")
    print(f"Repetitions: {NUM_REPETITIONS}, Cold Cache: {COLD_CACHE}")
    print(f"Valid exit codes: {sorted(VALID_EXIT_CODES)}")
    print(f"Acceptance: peak_ws [{MIN_PEAK_WS_MB}, {MAX_PEAK_WS_MB}]MB, "
          f"cpu > {MIN_CPU_SEC}s, CV < {MAX_CV_PCT}%")

    # Read canonical manifest
    anchor_manifest_hash = "UNAVAILABLE"
    try:
        with open(CANONICAL_MANIFEST, "r", encoding="utf-8-sig") as f:
            manifest_data = json.load(f)
            anchor_manifest_hash = manifest_data.get("manifest_hash", "UNAVAILABLE")
    except Exception as e:
        print(f"Warning: could not read manifest: {e}")

    # DB isolation via env vars
    temp_db_dir = tempfile.mkdtemp(prefix="f0a_db_")
    env = os.environ.copy()
    env["FSM_DB_PATH"] = os.path.join(temp_db_dir, "fsm.db")
    env["QUEUE_DB_PATH"] = os.path.join(temp_db_dir, "queue.db")

    if COLD_CACHE:
        print("\n[1/6] Cleaning telemetry cache (operational DBs untouched)...")
        clean_cache()
        print("    Done")

    print("\n[2/6] Pre-mutation snapshot...")
    snapshot_pre = canonical_snapshot()
    print(f"    Pre: {snapshot_pre[:16]}...")

    print("\n[3/6] Executing measurements...")
    measurements = []
    for i in range(1, NUM_REPETITIONS + 1):
        m = run_measurement(i, env)
        measurements.append(m)
        print(
            f"    Rep {i}: Wall={m['wall_time_sec']}s, "
            f"PeakSingle={m['peak_single_process_ws_mb']}MB, "
            f"PeakTree={m['peak_tree_ws_mb']}MB, "
            f"CPU={m['cpu_time_sec']}s, "
            f"ChildPIDs={m['child_pids_observed']}, "
            f"Exit={m['exit_code']}"
        )
        if m["cv_anchor"]:
            print(
                f"      CV: verdict={m['cv_anchor'].get('corpus_verdict')}, "
                f"NSS={m['cv_anchor'].get('corpus_nss')}"
            )

    print("\n[4/6] Post-mutation snapshot...")
    snapshot_post = canonical_snapshot()
    print(f"    Post: {snapshot_post[:16]}...")

    canonical_mutated = snapshot_pre != snapshot_post
    if canonical_mutated:
        print("    CRITICAL: CANONICAL CORPUS MUTATED")
    else:
        print("    Canonical integrity verified (H-0.6-A CONFIRMED)")

    # SQLite stats on ephemeral DBs BEFORE cleanup
    print("\n[5/6] Collecting SQLite stats from ephemeral DBs...")
    sqlite_stats = {}
    for db_name in ["fsm.db", "queue.db"]:
        db_path = Path(temp_db_dir) / db_name
        stats = get_sqlite_stats(db_path)
        if stats:
            sqlite_stats[db_name] = stats
            print(f"    {db_name}: {stats.get('page_count', 0)} pages")
        else:
            print(f"    {db_name}: not created during execution")
    shutil.rmtree(temp_db_dir, ignore_errors=True)

    # ── Statistics ──────────────────────────────────────────────────
    wall_times = [m["wall_time_sec"] for m in measurements]
    avg_wall = sum(wall_times) / len(wall_times)
    variance = sum((x - avg_wall) ** 2 for x in wall_times) / len(wall_times)
    std_dev = variance ** 0.5
    coeff_var = (std_dev / avg_wall * 100) if avg_wall > 0 else 0

    peak_singles = [m["peak_single_process_ws_mb"] for m in measurements]
    cpu_times = [m["cpu_time_sec"] for m in measurements]

    print("\n[6/6] Statistics:")
    print(f"    Wall:     avg={avg_wall:.3f}s  std={std_dev:.3f}s  CV={coeff_var:.2f}%")
    print(f"    Peak WS:  avg={sum(peak_singles)/len(peak_singles):.1f}MB  "
          f"max={max(peak_singles):.1f}MB  min={min(peak_singles):.1f}MB")
    print(f"    CPU:      avg={sum(cpu_times)/len(cpu_times):.3f}s  "
          f"max={max(cpu_times):.3f}s")

    # ── Invalidation criteria (HITO_0.7 acceptance) ─────────────────
    invalidation_reasons = []

    # CV check
    if coeff_var > MAX_CV_PCT:
        invalidation_reasons.append(
            f"High variance: CV {coeff_var:.2f}% > {MAX_CV_PCT}%"
        )

    # Exit code check
    invalid_exits = [
        m for m in measurements if m["exit_code"] not in VALID_EXIT_CODES
    ]
    if invalid_exits:
        invalidation_reasons.append(
            f"{len(invalid_exits)} executions with invalid exit codes "
            f"(valid: {sorted(VALID_EXIT_CODES)}, "
            f"got: {[m['exit_code'] for m in invalid_exits]})"
        )

    # Canonical mutation check
    if canonical_mutated:
        invalidation_reasons.append("CANONICAL MUTATED during F0-A")

    # Memory sanity: peak_single_process_ws in [20, 200] MB
    max_peak = max(peak_singles)
    if max_peak < MIN_PEAK_WS_MB:
        invalidation_reasons.append(
            f"Memory too low: peak {max_peak:.1f}MB < {MIN_PEAK_WS_MB}MB "
            f"(measurement channel likely broken)"
        )
    elif max_peak > MAX_PEAK_WS_MB:
        invalidation_reasons.append(
            f"Memory too high: peak {max_peak:.1f}MB > {MAX_PEAK_WS_MB}MB "
            f"(unexpected for SMOKE profile)"
        )

    # CPU sanity
    max_cpu = max(cpu_times)
    if max_cpu < MIN_CPU_SEC:
        invalidation_reasons.append(
            f"CPU too low: max {max_cpu:.3f}s < {MIN_CPU_SEC}s "
            f"(measurement channel likely broken)"
        )

    # CV anchor check
    missing_anchors = [
        m for m in measurements if not m.get("cv_anchor") or not m["cv_anchor"].get("corpus_nss")
    ]
    if missing_anchors:
        invalidation_reasons.append(
            f"{len(missing_anchors)} repetitions missing CV anchor (NSS)"
        )

    is_valid = len(invalidation_reasons) == 0
    if not is_valid:
        print("\n    Baseline INVALIDATED:")
        for reason in invalidation_reasons:
            print(f"      - {reason}")
    else:
        print("\n    Baseline VALID - all acceptance criteria met")

    # ── Build report ────────────────────────────────────────────────
    report = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "script_version": "v3-final",
            "profile": "SMOKE",
            "num_repetitions": NUM_REPETITIONS,
            "cold_cache": COLD_CACHE,
            "hardware_envelope": hardware,
            "hardware_conformant": False,
            "hardware_limitation": (
                "Valid only as pre/post-F18 comparative anchor on same machine. "
                "No claims of 16GB/4GB envelope conformance."
            ),
            "anchor_manifest_hash": anchor_manifest_hash,
            "memory_channel": MEMORY_CHANNEL,
            "hito_0_6_reconciliation": (
                "Read-only over canonical per CI Phase 6 pattern"
            ),
            "platform_note": (
                "On this Windows venv, sys.executable -m ... ALWAYS spawns "
                "a child worker process. All future instruments MUST use "
                "tree-monitoring. Single-process measurement is structurally "
                "invalid in this environment."
            ),
            "valid_exit_codes": sorted(VALID_EXIT_CODES),
            "exit_code_semantics": {
                "0": "PASS",
                "1": "WARNING",
                "2": "REGRESSION (HARD_FAIL basal expected, DF-10) - VALID",
                "3": "BASELINE_INTEGRITY - INVALID measurement",
                "4": "EXECUTION_FAILURE - INVALID measurement",
            },
            "acceptance_criteria": {
                "peak_single_process_ws_mb": f"[{MIN_PEAK_WS_MB}, {MAX_PEAK_WS_MB}]",
                "cpu_time_sec": f"> {MIN_CPU_SEC}",
                "coeff_variation_pct": f"< {MAX_CV_PCT}",
                "canonical_mutated": "false",
                "exit_codes": f"in {sorted(VALID_EXIT_CODES)}",
                "cv_anchor": "present with NSS",
            },
        },
        "measurements": measurements,
        "statistics": {
            "avg_wall_time_sec": round(avg_wall, 3),
            "std_dev_wall_time_sec": round(std_dev, 3),
            "coeff_variation_pct": round(coeff_var, 2),
            "peak_single_process_ws_mb": {
                "avg": round(sum(peak_singles) / len(peak_singles), 2),
                "max": round(max(peak_singles), 2),
                "min": round(min(peak_singles), 2),
            },
            "cpu_time_sec": {
                "avg": round(sum(cpu_times) / len(cpu_times), 3),
                "max": round(max(cpu_times), 3),
                "min": round(min(cpu_times), 3),
            },
        },
        "canonical_integrity": {
            "snapshot_pre": snapshot_pre,
            "snapshot_post": snapshot_post,
            "mutated": canonical_mutated,
        },
        "sqlite_stats_ephemeral": sqlite_stats,
        "invalidation": {
            "is_valid": is_valid,
            "reasons": invalidation_reasons,
        },
        "deferred_questions": {
            "provider_metrics": (
                "NOT MEASURABLE: run_regression.py does not invoke providers. "
                "Provider latency, tokens, retries require GROQ_API_KEY and "
                "dispatcher. Destined to F0-D/F18."
            ),
        },
    }

    report_file = (
        OUTPUT_DIR
        / f"baseline_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved: {report_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()