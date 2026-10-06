# F18_DC01_DECISION.md

**Documento:** `docs/architecture/adr/phase-18/reports/F18_DC01_DECISION.md`
**Estado:** FROZEN v1.0.0
**Fecha:** 2026-10-05
**Tipo:** Decisión arquitectónica (DC-01)
**Naturaleza:** Resolución del fork de concurrencia con evidencia cuantitativa.
**Evidencia vinculante:** 
  - Benchmark Task 1.2.1 (reports/benchmark/sync_bridge_benchmark.json)
  - Telemetría Task 1.1.1 (reports/regression_test/telemetry.db)
  - F18_BASELINE_CONCURRENCY.md v1.0.0
  - F18_BASELINE_METRICS_PER_STAGE.md v1.0.0
  - HITO_0.1 v1.2.0 (E-0.1-001 a E-0.1-007)
  - HITO_0.12 v1.0.1 (§5.2 DC-01)
  - ADR_F18_MASTER §5.1 (invariantes), §5.2 (reglas de gobernanza)
**Mandato:** Resolver DC-01 (fork de concurrencia) con evidencia cuantitativa
  de impacto en C1 (bounded execution), C3 (backpressure), C6 (cancellation),
  C10 (resource efficiency).
**Decisión:** MANTENER modelo híbrido actual (daemon secuencial + SyncProviderBridge).

---

## 1. RESUMEN EJECUTIVO

Se evaluaron tres opciones para el modelo de concurrencia del execution plane:

| Opción | Descripción | Evidencia | Decisión |
|---|---|---|---|
| **A** | Mantener modelo híbrido actual | Overhead negligible (~1%), throughput idéntico (1.00x), RSS delta 0.02 MB | ✅ **ACEPTADA** |
| **B** | Async single-process ± executors (elisión de SyncProviderBridge) | Sin beneficio medible vs Opción A; executors no aportan en I/O-bound | ❌ Rechazada |
| **C** | Multi-process | Sin evidencia de beneficio; overhead IPC no cuantificado | ❌ Rechazada |

**Decisión DC-01:** Mantener modelo híbrido actual (daemon secuencial +
SyncProviderBridge con thread dedicado + event loop + future.result bloqueante).

**Justificación normativa:**
- ENGINEERING_PRINCIPLES §VII (Reuse Before Invent): sin evidencia de
  insuficiencia, no sustituir autoridad existente.
- ADR_F18_MASTER §5.2 (Benchmark Before Optimization): técnica candidata
  sin evidencia empírica de beneficio no se implementa.
- ADR_F18_MASTER §5.2 (Evidence-driven technique selection): técnica
  "Asincronía pura top-to-bottom" del ROADMAP §IV Fase 18 es refutada
  por evidencia del benchmark.

---

## 2. EVIDENCIA DISPONIBLE (Gate 1)

### 2.1 Benchmark Task 1.2.1 (overhead de SyncProviderBridge)

| Experimento | Métrica | Resultado | Interpretación |
|---|---|---|---|
| Overhead por llamada | p95 overhead | 2.05ms (provider 100ms) / 9.28ms (500ms) / 10.40ms (1000ms) | Overhead constante ~2-10ms, despreciable vs latencia LLM real (500-3000ms) |
| Throughput bajo carga | Ratio async/bridge | 1.00x en todas las configuraciones (N=1,2,5,10,20) | Sin diferencia de throughput entre modelos |
| Backpressure | Wall time (50 calls, 2s latency, 5 concurrent) | 20.08s ambos | Comportamiento idéntico bajo carga |
| RSS delta | Delta de memoria | 0.02 MB | Costo de memoria negligible |

**Fuente:** `reports/benchmark/sync_bridge_benchmark.json`

### 2.2 Telemetría Task 1.1.1 (pipeline de regresión)

| Stage | Count | Min (s) | Max (s) | Avg (s) |
|---|---|---|---|---|
| EXTRACTION | 5 | 0.0408 | 0.0823 | 0.0592 |
| TOPOLOGY_EVALUATION | 5 | 0.0061 | 0.1923 | 0.0550 |
| REPORT_ASSEMBLY | 1 | 0.0000 | 0.0000 | 0.0000 |

**Fuente:** `reports/regression_test/telemetry.db`

**Nota:** Estas métricas son del pipeline de REGRESIÓN (run_regression.py),
no del pipeline de PRODUCCIÓN (LLMWorkerDaemon). El pipeline de regresión
no incluye etapas de traducción LLM, chunking, ni FSM persistence.

### 2.3 Baseline operacional (HITO_0.7 v1.1.0)

| Métrica | Valor | CV |
|---|---|---|
| Wall time | 1.659s avg | 0.41% |
| CPU time | 1.448s avg | 0.48% |
| Peak WS single-process | 76.98 MB avg | 0.07% |
| Corpus NSS | 0.6385503611043202 | — |

**Fuente:** F18_BASELINE_METRICS_PER_STAGE.md §1

### 2.4 Modelo de concurrencia actual (HITO_0.1 v1.2.0)

| Componente | Descripción | Evidencia |
|---|---|---|
| SyncProviderBridge | Thread dedicado + event loop + future.result(timeout=180.0) | E-0.1-001 |
| LLMWorkerDaemon | Loop síncrono secuencial (1 task a la vez) | E-0.1-006 |
| TaskLeaseHeartbeat | Thread separado para renovación de lease | E-0.1-002 |
| AsyncDispatcher | asyncio nativo con PriorityQueue (usado por CLI, no por daemon) | E-0.1-003, E-0.1-007 |
| Shutdown | Bounded join (thread.join(timeout=2.0)) + future.cancel() | E-0.1-004 |
| Backoff | Exponencial (base=1.0s, max=4.0s, factor=1.2, jitter ±0.5s) | E-0.1-006 |

**Fuente:** F18_BASELINE_CONCURRENCY.md §1

### 2.5 Evidencia estructural de C6 (Cancellation)

| Evidencia | Descripción | Relevancia para C6 |
|---|---|---|
| E-0.1-004 | Shutdown con bounded join (`join(timeout=2.0)`) | Mecanismo de cancelación bounded observado |
| E-0.1-005 | Shutdown por señal (SIGINT/SIGTERM handlers) | Mecanismo de cancelación externa observado |

**Nota:** Esta evidencia es **estructural** (observación del mecanismo), no
cuantitativa (no hay medición de latency de cancelación). El modelo actual
tiene mecanismos de cancellation bounded; las opciones B y C carecen de
evidencia estructural equivalente.

---

## 3. EVALUACIÓN DE OPCIONES

### 3.1 Opción A: Mantener modelo híbrido actual

**Descripción:** Daemon secuencial + SyncProviderBridge (thread dedicado +
event loop + future.result bloqueante).

**Evidencia a favor:**
- Overhead de barrera: 2-10ms p95 (~1% de latencia LLM real)
- Throughput ratio async/bridge: 1.00x (sin diferencia)
- RSS delta: 0.02 MB (negligible)
- Daemon es secuencial (1 task a la vez), por lo que no hay concurrencia
  que bounded
- Código existente funciona correctamente
- Mecanismos de cancellation bounded observados (E-0.1-004, E-0.1-005)

**Evidencia en contra:**
- Arquitectura híbrida (sync + async) es conceptualmente impura
- DF-13: `model_de_execution` no está en identity_chain (limitación parcial
  de INV-EXEC-IDENTIFIABILITY)

**Cumplimiento de invariantes:**

| Invariante | Cumplimiento | Justificación |
|---|---|---|
| INV-SCI-1 | ⏳ No evaluable | Requiere M1 (ejecutar dos modos y comparar scientific output) |
| INV-OPS-1 | ⚠️ Parcial | Prerrequisitos verificados (E-0.4-001/002/003); end-to-end pendiente M1 |
| INV-EXEC-IDENTIFIABILITY | ⚠️ Parcial | SyncProviderBridge es identificable; DF-13 documenta limitación |
| INV-NO-RESOURCE-SIGNAL | ⏳ No evaluable | Requiere evaluación de propagación de señales operacionales |

### 3.2 Opción B: Async single-process ± executors

**Descripción:** Reemplazar SyncProviderBridge con async directo, convertir
daemon a async nativo. Incluye la variante con ThreadPoolExecutor/
ProcessPoolExecutor para trabajo bloqueante.

**Evidencia a favor:**
- Arquitectura conceptualmente más pura (async top-to-bottom)
- Elimina thread dedicado del bridge
- ROADMAP §IV Fase 18 lista esta técnica como candidata

**Evidencia en contra:**
- Benchmark muestra overhead negligible de la barrera (2-10ms p95)
- Throughput ratio 1.00x: async puro NO produce mejora medible
- RSS delta 0.02 MB: costo de memoria del thread es negligible
- Requiere reescritura significativa de LLMWorkerDaemon
- Sin evidencia de beneficio medible
- **Executors no aportan en workload I/O-bound:** El workload del daemon
  es predominantemente I/O-bound (llamadas LLM con latencia 500-3000ms).
  ThreadPoolExecutor/ProcessPoolExecutor están diseñados para trabajo
  CPU-bound que bloquea el event loop. En I/O-bound, el event loop ya
  maneja la concurrencia eficientemente vía `asyncio.sleep()` durante
  las llamadas de red. El overhead de thread/process management no se
  compensa con ganancia de throughput.

**Cumplimiento de invariantes:**

| Invariante | Cumplimiento | Justificación |
|---|---|---|
| INV-SCI-1 | ⏳ No evaluable | Requiere M1 |
| INV-OPS-1 | ⚠️ Parcial | Mismo desempeño que Opción A |
| INV-EXEC-IDENTIFIABILITY | ⚠️ Parcial | Mismo problema que Opción A (DF-13) |
| INV-NO-RESOURCE-SIGNAL | ⏳ No evaluable | Requiere evaluación |

**Violaciones normativas:**
- ❌ ENGINEERING_PRINCIPLES §VII (Reuse Before Invent): sin evidencia de
  insuficiencia, no sustituir autoridad existente
- ❌ ADR_F18_MASTER §5.2 (Benchmark Before Optimization): técnica candidata
  sin evidencia empírica de beneficio
- ❌ ADR_F18_MASTER §5.2 (Evidence-driven technique selection): técnica
  refutada por evidencia del benchmark

### 3.3 Opción C: Multi-process

**Descripción:** Reemplazar threading con multiprocessing.

**Evidencia a favor:**
- Ninguna identificada en la evidencia disponible

**Evidencia en contra:**
- Sin evidencia de beneficio en Gate 1
- Daemon es secuencial (1 task a la vez), por lo que no hay carga que
  paralelizar
- Overhead de IPC (inter-process communication) típicamente mayor que
  thread switch
- Complejidad arquitectónica significativa
- Sin evidencia estructural de mecanismos de cancellation

**Cumplimiento de invariantes:**

| Invariante | Cumplimiento | Justificación |
|---|---|---|
| INV-SCI-1 | ⏳ No evaluable | Sin evidencia |
| INV-OPS-1 | ❓ Desconocido | Overhead IPC no cuantificado |
| INV-EXEC-IDENTIFIABILITY | ❓ Desconocido | Sin evaluación |
| INV-NO-RESOURCE-SIGNAL | ❓ Desconocido | Sin evaluación |

**Violaciones normativas:**
- ❌ ENGINEERING_PRINCIPLES §VII (Reuse Before Invent): sin evidencia de
  insuficiencia
- ❌ ADR_F18_MASTER §5.2 (Benchmark Before Optimization): sin evidencia
  empírica
- ❌ ADR_F18_MASTER §5.2 (Evidence-driven technique selection): sin
  evidencia de beneficio

---

## 4. DECISIÓN

**DC-01 queda resuelto: MANTENER modelo híbrido actual (Opción A).**

El execution plane continúa usando:
- **LLMWorkerDaemon:** loop síncrono secuencial (1 task a la vez)
- **SyncProviderBridge:** thread dedicado + event loop + future.result(timeout=180.0)
- **TaskLeaseHeartbeat:** thread separado para renovación de lease
- **AsyncDispatcher:** asyncio nativo (usado por CLI, no por daemon)

---

## 5. JUSTIFICACIÓN NORMATIVA

### 5.1 ENGINEERING_PRINCIPLES §VII (Reuse Before Invent)

> "Toda sustitución de autoridad existente exige evidencia de insuficiencia."

El benchmark Task 1.2.1 demuestra que SyncProviderBridge tiene:
- Overhead negligible (2-10ms p95, ~1% de latencia LLM real)
- Throughput idéntico al async puro (ratio 1.00x)
- RSS delta mínimo (0.02 MB)

**No hay evidencia de insuficiencia.** Por lo tanto, no se sustituye la
autoridad existente.

### 5.2 ADR_F18_MASTER §5.2 (Benchmark Before Optimization)

> "Ninguna técnica candidata se implementa sin evidencia empírica de beneficio."

La técnica "Asincronía pura top-to-bottom (elisión de SyncProviderBridge)"
del ROADMAP §IV Fase 18 es una técnica candidata. El benchmark Task 1.2.1
proporciona evidencia empírica de que esta técnica **NO produce beneficio
medible** en:
- Bounded execution (C1): throughput idéntico
- Backpressure (C3): comportamiento idéntico
- Resource efficiency (C10): RSS delta negligible

La técnica es **refutada** por la evidencia y no se implementa.

### 5.3 ADR_F18_MASTER §5.2 (Evidence-driven technique selection)

> "Las técnicas candidatas sobreviven o caen según evidencia del baseline
> y criterio preregistrado en FASE0_AUDIT_CHARTER.md §9."

El criterio preregistrado (Charter §9) exige:
- Métrica: latencia p95 por etapa I/O
- Dirección esperada si se elide: ↓ (disminución)
- Condición: sin ↑RSS (sin aumento de memoria)

La evidencia del benchmark muestra:
- Latencia p95 de la barrera: 2-10ms (overhead, no latencia de etapa I/O)
- Dirección: no hay disminución medible (throughput ratio 1.00x)
- RSS: sin aumento significativo (delta 0.02 MB)

La técnica no cumple el criterio preregistrado y es rechazada.

### 5.4 HITO_0.12 §5.2 (DC-01 acceptance criterion)

> "Decisión documentada: async single-process + executors vs multi-process,
> con evidencia de impacto en C1/C3/C6/C10."

Este documento proporciona:
- ✅ Decisión documentada (Opción A)
- ✅ Evidencia de impacto en C1 (bounded execution): throughput ratio 1.00x
- ✅ Evidencia de impacto en C3 (backpressure): comportamiento idéntico
- ⚠️ Evidencia de impacto en C6 (cancellation): **estructural** (E-0.1-004/005),
  no cuantitativa. El modelo actual tiene mecanismos de cancellation bounded;
  las opciones B y C carecen de evidencia estructural equivalente.
- ✅ Evidencia de impacto en C10 (resource efficiency): RSS delta 0.02 MB

**Declaración de desviación:** El acceptance criterion exige evidencia de
impacto en C1/C3/C6/C10. C6 (cancellation) no fue evaluado cuantitativamente
(no hay medición de latency de cancelación). La evidencia disponible es
estructural (observación de mecanismos), no cuantitativa. Esta desviación
parcial del acceptance criterion se documenta explícitamente. La evaluación
cuantitativa de C6 queda como evidencia complementaria para Gate 3 (Task 3.1.2,
implementación de cancellation conforme a NADR-F18-02 §5.4 R11-R15).

---

## 6. IMPLICACIONES

### 6.1 Para el execution plane

1. **DC-01 selecciona el modelo híbrido como base arquitectónica.**
2. **El cumplimiento de NADR-F18-02 §5.1-§5.7 se materializa en Gate 3
   sobre este modelo.** "Mantener" no implica ausencia de modificaciones
   en Gate 3. Gate 3 implementa bounded execution, admission/backpressure,
   cancellation y operational visibility conforme a NADR-F18-02.
3. **SyncProviderBridge se mantiene** como componente del execution plane.
4. **LLMWorkerDaemon continúa** como loop síncrono secuencial.
5. **AsyncDispatcher se mantiene** para uso del CLI (no del daemon).
6. **No hay reescritura** del daemon como async puro o multi-process.

### 6.2 Para el ROADMAP

La técnica "Asincronía pura top-to-bottom (elisión de SyncProviderBridge)"
del ROADMAP §IV Fase 18 queda **rechazada** conforme al criterio
preregistrado. El ROADMAP puede enmendarse en v3.1 para reflejar esta
decisión basada en evidencia.

### 6.3 Para DC-12 (guard diferencial)

DC-12 requiere comparar dos modos de ejecución bajo iguales parámetros
científicos. Con DC-01 resuelto (mantener modelo actual), DC-12 se enfoca
en:
- Demostrar INV-SCI-1 bajo variación operacional (scheduling order, retry
  timing, cache hit/miss)
- NO en comparar modelo híbrido vs async puro (esa comparación ya fue
  evaluada y rechazada)

### 6.4 Para DF-13 (model_de_execution ausente de identity_chain)

DF-13 se mantiene como hallazgo abierto para Gate 3 (Task 3.4.2, trazabilidad
de identidad). La decisión de DC-01 no resuelve DF-13; simplemente establece
que el modelo actual es adecuado para el caso de uso actual.

---

## 7. HALLAZGOS RELACIONADOS

### DF-09: Resultado contraintuitivo del benchmark de SyncProviderBridge

**Referencia:** Ver `FASE_18_DEFERRED_FINDINGS_REGISTER.md` para descripción
completa y estado de gobernanza de DF-09.

**Relación con esta decisión:** La reevaluación exigida por DF-09 se
materializa en esta decisión DC-01. La evidencia del benchmark Task 1.2.1
proporciona la base empírica para resolver DC-01 (mantener modelo híbrido).
La reclasificación de DF-09 en el Findings Register ocurre en el Gate 2
Exit Review, no en este documento.

**Evidencia de apoyo:** reports/benchmark/sync_bridge_benchmark.json

---

## 8. TRAZABILIDAD NORMATIVA

| Fuente | Regla/Sección | Cumplimiento |
|---|---|---|
| ENGINEERING_PRINCIPLES §VII | Reuse Before Invent | ✅ Sin evidencia de insuficiencia, no se sustituye autoridad existente |
| ADR_F18_MASTER §5.1 INV-SCI-1 | Misma baseline + mismos params ⇒ misma salida científica | ⏳ No evaluable (requiere M1) |
| ADR_F18_MASTER §5.1 INV-OPS-1 | Diferencias operacional no alteran resultado científico | ⚠️ Parcial (prerrequisitos verificados; end-to-end pendiente M1) |
| ADR_F18_MASTER §5.1 INV-EXEC-IDENTIFIABILITY | Modo de ejecución identificable y reproducible | ⚠️ Parcial (DF-13 documenta limitación) |
| ADR_F18_MASTER §5.2 | Benchmark Before Optimization | ✅ Técnica candidata sin beneficio medible es rechazada |
| ADR_F18_MASTER §5.2 | Evidence-driven technique selection | ✅ Técnica refutada por evidencia del benchmark |
| ADR_F18_MASTER §8.2 DC-01 | Fork de concurrencia | ✅ Decisión documentada con evidencia de impacto en C1/C3/C10; C6 estructural |
| HITO_0.12 §5.2 | DC-01 acceptance criterion | ⚠️ Satisfecho con desviación parcial en C6 (documentada en §5.4) |
| ROADMAP §IV Fase 18 | Asincronía pura top-to-bottom | ❌ Técnica rechazada por evidencia |

---

## 9. MATRIZ DE TRAZABILIDAD DC

| DC | Relación con DC-01 | Estado |
|---|---|---|
| **DC-01** | Este documento resuelve DC-01 | ✅ RESUELTO |
| **DC-02** | Contrato de identidad (resuelto en F18_IDENTITY_BOUNDARY_CONTRACT.md) | ✅ RESUELTO (DC-02-A) |
| **DC-05** | Contextos especializados vs unificados (depende de DC-01) | ⏳ PENDIENTE (Wave 2.3) |
| **DC-08** | Write-policy SQLite (depende de DC-01) | ⏳ PENDIENTE (Subfase 18.2) |
| **DC-10** | Fairness y admission (depende de DC-01) | ⏳ PENDIENTE (Subfase 18.3) |
| **DC-11** | Semántica de admisión-diferida (depende de DC-01) | ⏳ PENDIENTE (Subfase 18.3) |
| **DC-12** | Guard diferencial (usa DC-02-A) | ⏳ PENDIENTE (Subfase 18.5) |
| **DC-13** | Coordinated shutdown (depende de DC-01) | ⏳ PENDIENTE (Subfase 18.2) |

---

## 10. CIERRE

**Estado:** FROZEN v1.0.0
**Condición de cierre:** DC-01 resuelto con evidencia cuantitativa de impacto
en C1/C3/C10 y evidencia estructural en C6; tres opciones evaluadas; decisión
documentada con justificación normativa; técnica del ROADMAP rechazada conforme
a criterio preregistrado; desviación parcial del acceptance criterion en C6
documentada explícitamente; aclaración de que Gate 3 implementa mecanismos
NADR-F18-02 sobre el modelo elegido; trazabilidad normativa completa.
**Próximo paso:** Wave 2.3 (DC-05, contextos especializados vs unificados)
depende de DC-01 y puede proceder. Gate 3 implementa bounded execution,
admission/backpressure, cancellation y operational visibility sobre el modelo
seleccionado.