# F18_BASELINE_CONCURRENCY.md

**Estado:** FROZEN v1.0.0
**Fecha:** 2026-10-05
**Tipo:** Baseline de concurrencia del execution plane
**Naturaleza:** Read-only. Documenta el estado actual del modelo de concurrencia sin modificar código de producción.
**Evidencia:** HITO_0.1 v1.2.0 (E-0.1-001 a E-0.1-007); benchmark_sync_bridge Task 1.2.1 (reports/benchmark/sync_bridge_benchmark.json); ADR_F18.1 v1.0.2 FROZEN; NADR-F18-02 v1.0.1 FROZEN.
**Mandato:** Task 1.3.1 del PHASE_18.1_EXECUTION_PLAN v1.0.2 — Documentar el baseline de concurrencia actual.

---

## 1. MODELO DE CONCURRENCIA ACTUAL

### 1.1 Arquitectura dual

| Flujo | Mecanismo | Concurrencia | Backpressure |
|---|---|---|---|
| CLI (run_regression.py) | Secuencial síncrono | 1 task a la vez | N/A |
| Daemon producción (LLMWorkerDaemon) | Secuencial síncrono + SyncProviderBridge | 1 task a la vez | N/A |
| AsyncDispatcher (interno) | asyncio nativo, PriorityQueue, N workers | N concurrentes (default 20) | queue.join() + task_done() |

**Nota:** El daemon de producción usa SyncProviderBridge como processor. El AsyncDispatcher se usa en el pipeline de traducción completo (build_pipeline) pero NO en el daemon ni en regression.

### 1.2 Threads del daemon de producción

| Thread | Función | Mecanismo de coordinación |
|---|---|---|
| Main loop | claim → process → mark completed | `_stop_event` (threading.Event) |
| TaskLeaseHeartbeat | Renovación lease cada ttl×0.25 | `stop_event` + `lease_lost` (threading.Event) |
| SyncProviderBridge loop | Event loop asyncio dedicado | `_ready_event` (threading.Event) |

### 1.3 Barrera síncrona (SyncProviderBridge)

- **Ubicación:** `SyncProviderBridge.execute()` → `future.result(timeout=180.0)`
- **Mecanismo:** `asyncio.run_coroutine_threadsafe()` + `future.result()` bloqueante
- **Timeout:** 180s por defecto
- **Cancelación:** `future.cancel()` en timeout y excepción
- **Shutdown:** `loop.call_soon_threadsafe(loop.stop)` + `thread.join(timeout=2.0)`

### 1.4 Backoff exponencial (idle)

- Base: 1.0s, Max: 4.0s, Factor: 1.2, Jitter: ±0.5s (random.uniform)

---

## 2. EVIDENCIA CUANTITATIVA (Benchmark Task 1.2.1)

### 2.1 Overhead de la barrera síncrona

| Latencia provider | Overhead p95 | % de overhead |
|---|---|---|
| 100ms | 2.05ms | 2.05% |
| 500ms | 9.28ms | 1.86% |
| 1000ms | 10.40ms | 1.04% |

**Interpretación:** Overhead despreciable comparado con latencias LLM reales (500-3000ms). Crece con la latencia del provider (no es constante).

### 2.2 Throughput bajo carga

| Workers | Bridge (calls/s) | Async (calls/s) | Ratio |
|---|---|---|---|
| 1 | 1.96 | 1.95 | 1.00x |
| 2 | 3.92 | 3.94 | 1.00x |
| 5 | 9.75 | 9.84 | 1.01x |
| 10 | 19.56 | 19.48 | 1.00x |
| 20 | 39.12 | 39.16 | 1.00x |

**Interpretación:** Sin diferencia de throughput. La barrera síncrona no limita throughput.

### 2.3 Backpressure y RSS

| Métrica | Bridge | Async | Diferencia |
|---|---|---|---|
| Wall time (50 calls, 2s latency, 5 concurrent) | 20.08s | 20.08s | 0 |
| RSS delta del thread dedicado | — | — | 0.02 MB (negligible) |

---

## 3. TRAZABILIDAD DC-01 (alimenta Gate 2)

Este baseline **NO resuelve DC-01**. Proporciona la evidencia cuantitativa para que Gate 2 (Wave 2.2, Task 2.2.1) evalúe los modelos candidatos contra las 32 reglas de NADR-F18-02.

| Evidencia | Implicación para DC-01 |
|---|---|
| Modelo híbrido dual (§1.1) | DC-01 debe evaluar si este modelo satisface las 32 reglas NADR |
| Barrera con overhead pequeño (§2.1, DF-09) | La elisión de SyncProviderBridge NO es optimización prioritaria |
| Throughput idéntico (§2.2) | ThreadPoolExecutor con bridge es tan eficiente como asyncio para I/O-bound |
| Daemon secuencial (§1.2) | Modelos candidatos deben evaluar si la concurrencia es necesaria |
| Shutdown con bounded join (§1.3) | Modelos candidatos deben garantizar cancellation limpia (NADR-F18-02 §5.4) |

---

## 4. LIMITACIONES DEL BENCHMARK

| # | Limitación | Impacto |
|---|---|---|
| L1 | MockLLMProvider usa asyncio.sleep(), no I/O real | No replica overhead de red |
| L2 | No replica daemon real (heartbeat, backoff, SQLite) | Contexto de producción diferente |
| L3 | Concurrencia N>1 no existe en producción | Escenario hipotético, no actual |
| L4 | MockPromptBuilder evita costo real del build | Overhead subestimado |
| L5 | Host hardware no conforme (31.83GB vs 16GB target) | Limitación de HITO_0.7 |

---

## 5. GAPS RESIDUALES

| GAP | Descripción | Estado | Destino |
|---|---|---|---|
| GAP-0.1-01 | Impacto cuantitativo de barrera síncrona | ✅ RESOLVED | — |
| GAP-0.1-02 | Impacto de coordinación multi-thread | ⚠️ PARCIAL | Gate 3 |
| GAP-0.1-03 | Riesgo de thread residual en shutdown | ⚠️ PARCIAL | Gate 3 |

---

## 6. VERIFICACIÓN NADR

| Regla | Required | Observed | Estado |
|---|---|---|---|
| NADR-F18-02 §5.9 R31 | Evidencia cuantitativa para DC-01 | Benchmark + inspección forense | ✅ PASS |
| NADR-F18-02 §5.9 R32 | No prescripción de modelo | Baseline documenta sin prescribir | ✅ PASS |
| NADR-F18-02 §5.8 R27 | No alteración identidad científica | Baseline read-only, sin mutación | ✅ PASS |

---

## 7. TRAZABILIDAD

| Artefacto | Relación |
|---|---|
| HITO_0.1 v1.2.0 | Evidencia forense (E-0.1-001 a E-0.1-007) |
| Benchmark Task 1.2.1 | Evidencia cuantitativa |
| ADR_F18.1 v1.0.2 | DC-01 gobernado por Subfase 18.1 |
| NADR-F18-02 v1.0.1 | §5.9 R30-R32 |
| FASE0_AUDIT_CHARTER §9 | Criterio preregistrado de calibración |