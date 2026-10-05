# F18_BASELINE_METRICS_PER_STAGE.md

**Estado:** FROZEN v1.0.0
**Fecha:** 2026-10-05
**Tipo:** Baseline de métricas por etapa del pipeline
**Naturaleza:** Read-only. Consolida métricas disponibles de 3 fuentes.
**Evidencia:** HITO_0.7 v1.1.0 (baseline agregado); Telemetría Task 1.1.1; Benchmark Task 1.2.1.
**Mandato:** Task 1.3.2 del PHASE_18.1_EXECUTION_PLAN v1.0.2 — Documentar baseline de métricas por etapa.

---

## 1. MÉTRICAS AGREGADAS (HITO_0.7 v1.1.0)

| Métrica | Rep 1 | Rep 2 | Rep 3 | Avg | CV |
|---|---|---|---|---|---|
| Wall time (s) | 1.669 | 1.654 | 1.655 | 1.659 | 0.41% |
| CPU time (s) | 1.453 | 1.453 | 1.438 | 1.448 | 0.48% |
| Peak WS single-process (MB) | 76.91 | 77.04 | 77.00 | 76.98 | 0.07% |
| Peak WS tree (MB) | 87.86 | 80.40 | 77.52 | 81.93 | 5.55% |

**Condiciones:** Perfil SMOKE (5 docs), cold cache, 3 repeticiones.
**Hardware:** 31.83GB RAM / 12 CPUs (no conforme con target 16GB).
**Exit code:** 2 (HARD_FAIL basal, DF-10). NSS: 0.6385503611043202.

---

## 2. MÉTRICAS POR ETAPA — PIPELINE DE REGRESIÓN (Telemetría Task 1.1.1)

| Stage | Count | Min (s) | Max (s) | Avg (s) |
|---|---|---|---|---|
| EXTRACTION | 5 | 0.0408 | 0.0823 | 0.0592 |
| TOPOLOGY_EVALUATION | 5 | 0.0061 | 0.1923 | 0.0550 |
| REPORT_ASSEMBLY | 1 | 0.0000 | 0.0000 | 0.0000 |

**Fuente:** reports/regression_test/telemetry.db
**Nota:** Métricas del pipeline de REGRESIÓN (run_regression.py), no del pipeline de PRODUCCIÓN. No incluye traducción LLM, chunking ni FSM.

---

## 3. MÉTRICAS DE BARRERA SÍNCRONA (Benchmark Task 1.2.1)

| Métrica | Valor |
|---|---|
| Overhead p95 (provider 100ms) | 2.05ms |
| Overhead p95 (provider 500ms) | 9.28ms |
| Overhead p95 (provider 1000ms) | 10.40ms |
| Throughput ratio async/bridge | 1.00x (todas las configuraciones) |
| RSS delta del thread dedicado | 0.02 MB |

---

## 4. ESTADO DE CALIBRACIÓN (Charter §9)

| Técnica | Métrica requerida | Disponibilidad | Estado |
|---|---|---|---|
| SyncProviderBridge elision | latencia p95 por etapa I/O | ✅ Disponible | **CALIBRADA: técnica rechazada** (overhead negligible, sin mejora de throughput) |
| Process pools | CPU-time TED/extraction | ❌ Ausente | NO CALIBRADA |
| Object pools / zero-copy | allocations y peak RSS en hotspot | ❌ Ausente | NO CALIBRADA |
| Lazy loading | peak RSS por doc grande + wall p95 | ❌ Ausente | NO CALIBRADA |
| LLM cache | hit-rate + costo evitado | ❌ Ausente | NO CALIBRADA |
| Batching adaptativo | tokens por padding | ❌ Ausente | NO CALIBRADA |

**Resultado:** 1/6 técnicas evaluadas (SyncProviderBridge elision → rechazada). 5/6 pendientes.

---

## 5. MÉTRICAS NO DISPONIBLES (DEFERRED)

| Métrica | GAP | Razón | Destino |
|---|---|---|---|
| CPU time por etapa | GAP-0.7-01 | Requiere profiling por etapa | Gate 2 o F0-D |
| Allocations por etapa | GAP-0.7-01 | Requiere tracemalloc | Gate 2 o F0-D |
| I/O wait por etapa | GAP-0.7-01 | Requiere instrumentación I/O | Gate 2 o F0-D |
| Provider latency/tokens | GAP-0.7-02 | run_regression no invoca providers | F0-D |
| Peak RSS por documento | GAP-0.7-05 | Requiere medición por documento | Gate 2 |

---

## 6. VERIFICACIÓN NADR

| Regla | Required | Observed | Estado |
|---|---|---|---|
| NADR-F18-02 §5.9 R31 | Evidencia cuantitativa para DC-01 | 3 fuentes integradas | ✅ PASS |
| NADR-F18-02 §5.9 R32 | No prescripción de modelo | Baseline documenta sin prescribir | ✅ PASS |
| NADR-F18-02 §5.7 R25 | Evidencia operacional separada | telemetry.db separado de regression_report.json | ✅ PASS |
| NADR-F18-01 §5.1 R4 | No mutación del oráculo | Baseline read-only | ✅ PASS |

---

## 7. TRAZABILIDAD

| Artefacto | Relación |
|---|---|
| HITO_0.7 v1.1.0 | Baseline agregado |
| Telemetría Task 1.1.1 | Latencia por etapa de regresión |
| Benchmark Task 1.2.1 | Overhead de barrera |
| FASE0_AUDIT_CHARTER §6 | Requisito de métricas por etapa |
| FASE0_AUDIT_CHARTER §9 | Regla de calibración de técnicas |