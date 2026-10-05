"""
tools/evaluation/benchmark_sync_bridge.py

Benchmark de SyncProviderBridge vs async directo.

Task 1.2.1 — GAP-0.1-01: Medición del impacto cuantitativo de la barrera
síncrona sobre bounded execution (C1) y backpressure (C3).

Diseño:
- MockLLMProvider: latencia configurable, determinista (asyncio.sleep).
- MockPromptBuilder: misma interfaz que PromptBuilder, devuelve envelopes
  fijos. Aísla la variable: la única diferencia entre Path A (bridge) y
  Path B (async directo) es la barrera síncrona.
- 4 experimentos sintéticos: overhead por llamada, throughput bajo carga,
  backpressure, RSS delta.
- Resultados persistidos en reports/benchmark/sync_bridge_benchmark.json.

NO modifica código de producción. Es un instrumento de medición efímero
conforme a ADR_F18_MASTER §7.1 (medición externa).

Criterio preregistrado (FASE0_AUDIT_CHARTER §9):
- Métrica: latencia p95 por etapa I/O
- Dirección esperada si se elide: ↓
- Condición: sin ↑RSS

Limitaciones documentadas:
- Exp 2 usa asyncio.Semaphore como aproximación de AsyncDispatcher.
  No incluye PriorityQueue, sequence_counter, ni validation/healing pipelines.
- Exp 1-4 no incluyen TaskLeaseHeartbeat ni backoff exponencial.
  Estos factores son capturados en Exp 5 (daemon observacional, Task 1.2.2).
- El daemon real es SECUENCIAL (1 task a la vez). Los experimentos de
  concurrencia miden el overhead de la barrera, no el comportamiento
  actual del daemon en producción.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from apps.llm_workers.prompt_builder import BuildSuccess, PromptEnvelope
from apps.llm_workers.sync_bridge import SyncProviderBridge
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload
from core.prompting.inference_result import InferenceResult
from core.prompting.models import (
    PromptConstraints,
    PromptContext,
    PromptIntent,
    PromptPayload,
    PromptSchema,
)
from core.validation.budget import PromptBudget

from typing import cast
from apps.llm_workers.prompt_builder import PromptBuilder as _PromptBuilderConcrete
from core.ast.models import TranslationTaskType

# =============================================================================
# Fixtures de medición (Functional Core)
# =============================================================================

def make_mock_envelope(chunk_id: str) -> PromptEnvelope:
    """Construye un PromptEnvelope mínimo y determinista para el benchmark.

    Usa los campos reales confirmados por verificación forense:
    - PromptIntent.TRANSLATE (Enum, no acepta None)
    - PromptConstraints() (BaseModel con defaults, no acepta None)
    - PromptBudget con campos reales (system_tokens, context_tokens, etc.)
    """
    schema = PromptSchema(
        intent=PromptIntent.TRANSLATE,
        context=PromptContext(
            chunk_index=0,
            depth=0,
            breadcrumbs=[],
            is_pruned=False,
        ),
        constraints=PromptConstraints(),
        payload=PromptPayload(content="benchmark payload"),
    )
    budget = PromptBudget(
        system_tokens=50,
        context_tokens=30,
        payload_tokens=100,
        reserved_tokens=50,
        window_limit=8192,
    )
    return PromptEnvelope(
        prompt_id=f"bench_{chunk_id[:8]}",
        chunk_id=chunk_id,
        chunk_type=TranslationTaskType.TRANSLATE,
        model_name="mock-model",
        prompt_version="v0.0-bench",
        prompt_hash="bench_hash_" + chunk_id[:8],
        schema=schema,
        estimated_tokens=150,
        budget_stats=budget,
        telemetry={},
        target_provider="primary",
    )


def make_mock_node(node_id: str) -> ASTNode:
    """Construye un ASTNode mínimo con los campos que SyncProviderBridge espera.

    Usa los campos reales confirmados por verificación forense:
    - node_id: NodeId (Annotated[str, pattern=r"^[^:]+$"]). Cualquier string
      sin ':' es válido.
    - control_plane: Dict[str, Any] con default_factory=dict. SÍ existe.
    - payload: ParagraphPayload (subtipo de ASTPayload).
    """
    return ASTNode(
        node_id=node_id,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(
            content="Benchmark paragraph content for sync bridge measurement."
        ),
        control_plane={
            "chunk_index": 0,
            "chunk_fingerprint": f"fp_{node_id[:12]}",
            "context_depth": 0,
        },
    )


class MockLLMProvider:
    """Provider con latencia fija configurable. Determinista.

    Implementa el Protocol LLMProvider:
        async def translate(self, envelope: PromptEnvelope) -> InferenceResult
    """

    def __init__(self, latency_sec: float) -> None:
        self._latency_sec = latency_sec
        self.call_count = 0

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        self.call_count += 1
        await asyncio.sleep(self._latency_sec)
        return InferenceResult(
            chunk_id=envelope.chunk_id,
            content="translated benchmark content",
            input_tokens=100,
            output_tokens=50,
            latency_ms=self._latency_sec * 1000.0,
            finish_reason="stop",
        )


class MockPromptBuilder:
    """Misma interfaz que PromptBuilder para SyncProviderBridge.

    Devuelve BuildSuccess con envelope fijo. Aísla la variable de medición:
    la única diferencia entre Path A (bridge) y Path B (async directo)
    es la barrera síncrona.
    """

    def __init__(self) -> None:
        self.prompt_version = "v0.0-bench"
        self.model_name = "mock-model"

    def build(
        self,
        unit: Any,
        resolved_context: Any,
        target_lang_expansion: float = 1.2,
    ) -> BuildSuccess:
        envelope = make_mock_envelope(unit.chunk_id)
        return BuildSuccess(status="success", envelope=envelope)


# =============================================================================
# Experimentos sintéticos (Imperative Shell)
# =============================================================================

def _percentiles(samples: List[float]) -> Dict[str, float]:
    """Calcula p50, p95, p99 de una lista de muestras."""
    if not samples:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}
    sorted_s = sorted(samples)
    n = len(sorted_s)
    return {
        "p50": sorted_s[int(n * 0.50)],
        "p95": sorted_s[min(int(n * 0.95), n - 1)],
        "p99": sorted_s[min(int(n * 0.99), n - 1)],
        "mean": statistics.mean(sorted_s),
    }


def experiment_1_overhead_per_call(
    latency_sec: float, repetitions: int
) -> Dict[str, Any]:
    """Experimento 1: Overhead de la barrera síncrona por llamada individual.

    Path A: SyncProviderBridge.execute() (bloqueante)
    Path B: await provider.translate() directo (async nativo)

    overhead_ms = bridge_latency - async_latency
    """
    provider = MockLLMProvider(latency_sec=latency_sec)
    builder = MockPromptBuilder()
    bridge = SyncProviderBridge(
        async_provider=provider,
        prompt_builder=cast(_PromptBuilderConcrete, builder),
        timeout_sec=30.0,
    )

    # Path A: mediciones vía bridge (síncrono)
    bridge_latencies: List[float] = []
    for i in range(repetitions):
        node = make_mock_node(f"bench_a_{i:04d}")
        t0 = time.perf_counter()
        bridge.execute(node)
        bridge_latencies.append(time.perf_counter() - t0)

    # Path B: mediciones async directo
    async def _measure_async_direct(n: int) -> List[float]:
        latencies: List[float] = []
        for i in range(n):
            envelope = make_mock_envelope(f"bench_b_{i:04d}")
            t0 = time.perf_counter()
            await provider.translate(envelope)
            latencies.append(time.perf_counter() - t0)
        return latencies

    async_latencies = asyncio.run(_measure_async_direct(repetitions))

    bridge.shutdown()

    overhead_samples = [b - a for b, a in zip(bridge_latencies, async_latencies)]

    return {
        "experiment": "overhead_per_call",
        "provider_latency_sec": latency_sec,
        "repetitions": repetitions,
        "bridge_latency": _percentiles(bridge_latencies),
        "async_latency": _percentiles(async_latencies),
        "overhead": _percentiles(overhead_samples),
    }


def experiment_2_throughput_under_load(
    latency_sec: float, worker_counts: List[int], units_per_config: int
) -> Dict[str, Any]:
    """Experimento 2: Throughput efectivo con N workers concurrentes.

    Path A: N threads x SyncProviderBridge.execute() (simula ThreadPoolExecutor)
    Path B: asyncio.Semaphore(N) como aproximación de AsyncDispatcher

    LIMITACIÓN DOCUMENTADA: Path B usa Semaphore como aproximación de
    AsyncDispatcher. No incluye PriorityQueue, sequence_counter, ni
    validation/healing pipelines.

    throughput_ratio = B / A
    """
    provider = MockLLMProvider(latency_sec=latency_sec)
    builder = MockPromptBuilder()
    bridge = SyncProviderBridge(
        async_provider=provider,
        prompt_builder=cast(_PromptBuilderConcrete, builder),
        timeout_sec=60.0,
    )

    results: Dict[str, Any] = {
        "experiment": "throughput_under_load",
        "provider_latency_sec": latency_sec,
        "units_per_config": units_per_config,
        "limitation": (
            "Path B usa asyncio.Semaphore como aproximación de AsyncDispatcher. "
            "No incluye PriorityQueue, sequence_counter, ni validation/healing."
        ),
        "configurations": [],
    }

    for n_workers in worker_counts:
        # Path A: threads x bridge
        def _bridge_call(idx: int) -> float:
            node = make_mock_node(f"load_a_{idx:04d}")
            t0 = time.perf_counter()
            bridge.execute(node)
            return time.perf_counter() - t0

        t_a_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            list(pool.map(_bridge_call, range(units_per_config)))
        wall_a = time.perf_counter() - t_a_start
        throughput_a = units_per_config / wall_a if wall_a > 0 else 0.0

        # Path B: async nativo con Semaphore (aproximación de AsyncDispatcher)
        async def _async_batch(n: int, total: int) -> float:
            sem = asyncio.Semaphore(n)

            async def _one(idx: int) -> None:
                async with sem:
                    envelope = make_mock_envelope(f"load_b_{idx:04d}")
                    await provider.translate(envelope)

            t0 = time.perf_counter()
            await asyncio.gather(*[_one(i) for i in range(total)])
            return time.perf_counter() - t0

        wall_b = asyncio.run(_async_batch(n_workers, units_per_config))
        throughput_b = units_per_config / wall_b if wall_b > 0 else 0.0

        results["configurations"].append({
            "workers": n_workers,
            "bridge_wall_sec": wall_a,
            "bridge_throughput_per_sec": throughput_a,
            "async_wall_sec": wall_b,
            "async_throughput_per_sec": throughput_b,
            "throughput_ratio_async_over_bridge": (
                throughput_b / throughput_a if throughput_a > 0 else float("inf")
            ),
        })

    bridge.shutdown()
    return results


def experiment_3_backpressure_behavior(
    latency_sec: float, burst_size: int, concurrency: int
) -> Dict[str, Any]:
    """Experimento 3: Comportamiento ante carga superior a la capacidad.

    Path A: SyncProviderBridge — no tiene backpressure; cada execute() bloquea.
            Se inyecta burst vía ThreadPoolExecutor(concurrency).
    Path B: asyncio.Semaphore — backpressure natural.

    Métricas: peak threads activos, wall time total.
    """
    import threading

    provider = MockLLMProvider(latency_sec=latency_sec)
    builder = MockPromptBuilder()
    bridge = SyncProviderBridge(
        async_provider=provider,
        prompt_builder=cast(_PromptBuilderConcrete, builder),
        timeout_sec=60.0,
    )

    # Path A: burst vía threads
    active_threads_peak = 0
    lock = threading.Lock()
    active = [0]

    def _bridge_burst(idx: int) -> None:
        nonlocal active_threads_peak
        with lock:
            active[0] += 1
            active_threads_peak = max(active_threads_peak, active[0])
        try:
            node = make_mock_node(f"burst_a_{idx:04d}")
            bridge.execute(node)
        finally:
            with lock:
                active[0] -= 1

    t_a_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(_bridge_burst, range(burst_size)))
    wall_a = time.perf_counter() - t_a_start

    # Path B: async con semaphore (backpressure natural)
    async def _async_burst(total: int, n: int) -> Dict[str, Any]:
        sem = asyncio.Semaphore(n)
        completed = 0

        async def _one(idx: int) -> None:
            nonlocal completed
            async with sem:
                envelope = make_mock_envelope(f"burst_b_{idx:04d}")
                await provider.translate(envelope)
                completed += 1

        t0 = time.perf_counter()
        await asyncio.gather(*[_one(i) for i in range(total)])
        wall = time.perf_counter() - t0
        return {"wall_sec": wall, "completed": completed}

    async_result = asyncio.run(_async_burst(burst_size, concurrency))

    bridge.shutdown()

    return {
        "experiment": "backpressure_behavior",
        "provider_latency_sec": latency_sec,
        "burst_size": burst_size,
        "concurrency": concurrency,
        "bridge": {
            "wall_sec": wall_a,
            "peak_active_threads": active_threads_peak,
            "mechanism": "ThreadPoolExecutor (no backpressure; cada execute bloquea)",
        },
        "async": {
            "wall_sec": async_result["wall_sec"],
            "completed": async_result["completed"],
            "mechanism": "asyncio.Semaphore (backpressure natural)",
        },
    }


def experiment_4_rss_delta() -> Dict[str, Any]:
    """Experimento 4: Costo en memoria del thread dedicado del bridge.

    Mide RSS antes y después de crear una instancia de SyncProviderBridge.
    Usa múltiples muestras para estabilidad.
    """
    try:
        import psutil
    except ImportError:
        return {
            "experiment": "rss_delta",
            "error": "psutil no disponible; medición de RSS omitida",
        }

    process = psutil.Process()

    # RSS antes (múltiples muestras)
    rss_before_samples = []
    for _ in range(5):
        time.sleep(0.05)
        rss_before_samples.append(process.memory_info().rss / (1024 * 1024))
    rss_before_mb = statistics.mean(rss_before_samples)

    provider = MockLLMProvider(latency_sec=0.01)
    builder = MockPromptBuilder()
    bridge = SyncProviderBridge(
        async_provider=provider,
        prompt_builder=cast(_PromptBuilderConcrete, builder),
        timeout_sec=30.0,
    )

    # RSS con bridge (múltiples muestras)
    rss_with_samples = []
    for _ in range(5):
        time.sleep(0.05)
        rss_with_samples.append(process.memory_info().rss / (1024 * 1024))
    rss_with_mb = statistics.mean(rss_with_samples)

    bridge.shutdown()

    # RSS después de shutdown (múltiples muestras)
    rss_after_samples = []
    for _ in range(5):
        time.sleep(0.05)
        rss_after_samples.append(process.memory_info().rss / (1024 * 1024))
    rss_after_mb = statistics.mean(rss_after_samples)

    return {
        "experiment": "rss_delta",
        "rss_before_mb": rss_before_mb,
        "rss_with_bridge_mb": rss_with_mb,
        "rss_after_shutdown_mb": rss_after_mb,
        "rss_delta_mb": rss_with_mb - rss_before_mb,
        "note": "Thread dedicado + event loop objects. Múltiples muestras promediadas.",
    }


# =============================================================================
# Entry point (Imperative Shell)
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark SyncProviderBridge vs async directo (GAP-0.1-01)"
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=100,
        help="Repeticiones por configuración en Exp 1 (default: 100)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("BENCHMARK: SyncProviderBridge vs async directo")
    print("Task 1.2.1 — GAP-0.1-01")
    print("=" * 70)

    results: Dict[str, Any] = {
        "benchmark": "sync_bridge_impact",
        "task": "1.2.1",
        "gap": "GAP-0.1-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "experiments": [],
        "limitations": [
            "Exp 2 Path B usa asyncio.Semaphore como aproximación de AsyncDispatcher.",
            "Exp 1-4 no incluyen TaskLeaseHeartbeat ni backoff exponencial.",
            "El daemon real es SECUENCIAL (1 task a la vez). Los experimentos de",
            "  concurrencia miden el overhead de la barrera, no el comportamiento",
            "  actual del daemon en producción.",
        ],
    }

    # Experimento 1: overhead por llamada (3 latencias x N reps)
    print(f"\n[1/4] Overhead por llamada (reps={args.repetitions})...")
    for latency in [0.1, 0.5, 1.0]:
        print(f"  latencia={latency}s...", end=" ", flush=True)
        exp1 = experiment_1_overhead_per_call(
            latency_sec=latency, repetitions=args.repetitions
        )
        results["experiments"].append(exp1)
        print(f"overhead p95={exp1['overhead']['p95']*1000:.2f}ms")

    # Experimento 2: throughput bajo carga
    print("\n[2/4] Throughput bajo carga...")
    exp2 = experiment_2_throughput_under_load(
        latency_sec=0.5,
        worker_counts=[1, 2, 5, 10, 20],
        units_per_config=20,
    )
    results["experiments"].append(exp2)
    for cfg in exp2["configurations"]:
        print(
            f"  N={cfg['workers']}: bridge={cfg['bridge_throughput_per_sec']:.2f}/s "
            f"async={cfg['async_throughput_per_sec']:.2f}/s "
            f"ratio={cfg['throughput_ratio_async_over_bridge']:.2f}x"
        )

    # Experimento 3: backpressure
    print("\n[3/4] Backpressure behavior...")
    exp3 = experiment_3_backpressure_behavior(
        latency_sec=2.0, burst_size=50, concurrency=5
    )
    results["experiments"].append(exp3)
    print(
        f"  bridge: wall={exp3['bridge']['wall_sec']:.2f}s "
        f"peak_threads={exp3['bridge']['peak_active_threads']}"
    )
    print(
        f"  async:  wall={exp3['async']['wall_sec']:.2f}s "
        f"completed={exp3['async']['completed']}"
    )

    # Experimento 4: RSS delta
    print("\n[4/4] RSS delta...")
    exp4 = experiment_4_rss_delta()
    results["experiments"].append(exp4)
    if "error" not in exp4:
        print(f"  RSS delta: {exp4['rss_delta_mb']:.2f} MB")
    else:
        print(f"  {exp4['error']}")

    # Persistir resultados
    output_dir = Path("reports/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "sync_bridge_benchmark.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\nResultados persistidos en: {output_path}")
    print("=" * 70)
    print("BENCHMARK COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    main()