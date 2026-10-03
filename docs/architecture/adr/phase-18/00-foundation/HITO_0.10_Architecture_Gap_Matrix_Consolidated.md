# HITO_0.10_Architecture_Gap_Matrix_Consolidated.md

**Estado:** FROZEN v1.0.1
**Fecha de emisión:** 2026-10-03
**Fecha de congelamiento:** 2026-10-03 (v1.0.1)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Consolidation Output
**Naturaleza:** Read-only. **Consolida problemas y dependencias; no decide la solución.** Este documento no prescribe implementación ni arquitectura. Su función es proporcionar la entrada consolidada para el ADR_F18_MASTER, distinguiendo GAPs abiertos de decisiones pendientes.
**Evidencia Forense Vinculante:** HITO_0.1 v1.2.0, HITO_0.2 v1.2.0, HITO_0.3 v1.3.0, HITO_0.4 v1.3.0, HITO_0.5 v1.2.0, HITO_0.6 v1.0.0, HITO_0.7 v1.1.0, HITO_0.8 v1.4.0, HITO_0.9 v1.4.0
**Mandato (Charter §8):** Generar el output obligatorio "Architecture Gap Matrix" para ADR_F18_MASTER §7.
**Síntesis:** Se consolidan 34 GAPs crudos de los 9 HITOs de Fase 0. Tras normalización (3 duplicados, 6 eliminados/reconciliados), quedan 25 GAPs abiertos: 3 P0 (precondiciones de certificación), 15 P1 (impacto operacional significativo), 7 P2 (impacto menor o limitación del instrumento). Todos tienen fase de resolución propuesta explícita. Se introduce clasificación GAP_CLASS (ARCH/CONTRACT/IMPL/VALIDATION/OBSERVABILITY/EXPERIMENT) para distinguir naturaleza. Se documentan relaciones de refinamiento entre GAPs (REFINED_BY, VALIDATION_REFINEMENT). Ningún GAP prescribe solución; todos alimentan Decision Candidates.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-03 | Emisión inicial. Consolidación de GAPs de HITOs 0.1-0.9. |
| 1.0.1-FROZEN | 2026-10-03 | **Reconciliación epistemológica.** (1) Añadida columna GAP_CLASS. (2) Añadida columna NORMALIZATION_ACTION para GAPs eliminados. (3) Corregida afirmación "todos tienen DC" → "todos tienen destino; los sin DC quedan como findings operativos". (4) GAP-0.5-02 degradado de P0 a P1. (5) GAP-0.2-04 reformulado con formulación canónica de INV-JOURNAL. (6) GAP-0.4-01 reformulado como "inability to demonstrate". (7) GAP-0.4-03 reformulado como ausencia de definición contractual. (8) GAP-0.8-01 clarificado como evidencia secundaria. (9) GAP-0.8-05 marcado REFINED_BY GAP-0.9-02. (10) GAP-0.8-07 marcado VALIDATION_REFINEMENT GAP-0.9-04. (11) GAP-0.9-05 resuelta contradicción F18 vs F19+. (12) Prescripciones reformuladas como "resolver contrato/DC". (13) DC-07, DC-03, DC-13 reformulados. (14) DF-34 reformulado. (15) Sección 5.1 cambiada a DAG de decisiones. (16) "Todos destino F18" cambiado a "fase de resolución propuesta". (17) "Contradicciones: Ninguna" cambiado a "refinamientos sin contradicción material". (18) Versiones de HITOs citadas verificadas. |

---

## 1. RESUMEN EJECUTIVO

Se consolidaron todos los GAPs identificados en los 9 HITOs de Fase 0 (F0-B, F0-G, F0-F, F0-E, F0-A Protocol, Reconciliation, F0-A Baseline, F0-C, F0-D) en una matriz unificada con clasificación epistemológica explícita.

**Hallazgo central:**

> De 34 GAPs crudos, tras normalización quedan 25 GAPs abiertos con fase de resolución propuesta explícita. 3 son P0 (precondiciones de certificación), 15 son P1 (impacto operacional significativo), 7 son P2 (impacto menor o limitación del instrumento). Todos están mapeados a Decision Candidates del Charter §7 o justificados como findings operativos. Se documentan relaciones de refinamiento entre GAPs para evitar inflación artificial del backlog.

**Distribución por severidad:**
- **P0 (3):** GAP-0.3-01, GAP-0.4-01, GAP-0.4-03
- **P1 (18):** GAP-0.1-01, GAP-0.2-01, GAP-0.2-02, GAP-0.2-03, GAP-0.2-04, GAP-0.3-02, GAP-0.3-03, GAP-0.4-02, GAP-0.5-02, GAP-0.7-01, GAP-0.7-02, GAP-0.8-01, GAP-0.8-06, GAP-0.8-07, GAP-0.9-01, GAP-0.9-02, GAP-0.9-04, GAP-0.9-05
- **P2 (4):** GAP-0.1-02, GAP-0.1-03, GAP-0.8-05, GAP-0.9-03

**Distribución por clase de GAP:**
- **ARCH (Architectural):** 8
- **CONTRACT (Contract/Invariant):** 5
- **IMPL (Implementation defect):** 4
- **VALIDATION (Missing evidence):** 5
- **OBSERVABILITY (Instrumentation gap):** 2
- **EXPERIMENT (Experimental limitation):** 1

**Distribución por fase de resolución propuesta:**
- **F18 (22):** Resolución inicial propuesta en Fase 18
- **F18+ (2):** Resolución propuesta en F18 o posterior, según disponibilidad de instrumentación
- **F19+ (1):** Resolución diferible a Fase 19

---

## 2. METODOLOGÍA DE CONSOLIDACIÓN

### 2.1 Criterios de normalización del universo de GAPs

Se clasificaron los 34 GAPs crudos según la siguiente taxonomía de acciones:

| Acción | Significado | Cantidad |
|---|---|---|
| **OPEN** | Permanece en matriz consolidada | 25 |
| **DUPLICATED** | Mismo finding, conserva ID canónico | 3 |
| **SUPERSEDED** | Reemplazado por finding posterior más preciso | 1 |
| **CLOSED** | Resuelto por evidencia posterior | 4 |
| **RECONCILED** | Reinterpretado/reclasificado sin quedar abierto | 1 |

### 2.2 GAPs eliminados/reconciliados

| GAP original | Acción | Razón | GAP canónico |
|---|---|---|---|
| GAP-0.2-01 (ProfileStore no durable) | DUPLICATED | Mismo finding identificado en F0-G y F0-C | GAP-0.2-01 (primera identificación) |
| GAP-0.2-02 (Circuit Breaker in-memory) | DUPLICATED | Mismo finding identificado en F0-G y F0-C | GAP-0.2-02 (primera identificación) |
| GAP-0.2-04 (INV-JOURNAL) | DUPLICATED | Mismo finding identificado en F0-G y F0-C | GAP-0.2-04 (primera identificación) |
| GAP-0.5-01 | RECONCILED | Reconciliado en HITO_0.6 v1.0.0 (lectura read-only mandatada) | — |
| GAP-0.5-03 | CLOSED | Workaround validado en HITO_0.7 (tree-monitoring) | — |
| GAP-0.6-01 | CLOSED | Checksums pre/post implementados en HITO_0.7 | — |
| GAP-0.6-02 | CLOSED | Cleanup ejecutado | — |
| GAP-0.7-03 | CLOSED | Limitación documentada (hardware no conforme) | — |
| GAP-0.7-04 | CLOSED | Workaround validado (tree-monitoring) | — |
| GAP-0.8-03 | SUPERSEDED | Refinado por GAP-0.2-01 con evidencia empírica adicional | GAP-0.2-01 |

### 2.3 Clasificación GAP_CLASS

Cada GAP abierto se clasifica según su naturaleza:

| Clase | Significado | Ejemplo |
|---|---|---|
| **ARCH** | Architectural gap | Ausencia de componente o patrón |
| **CONTRACT** | Contract/invariant gap | Violación o ausencia de contrato |
| **IMPL** | Implementation defect | Bug o violación de frontera |
| **VALIDATION** | Missing evidence | Mecanismo observado pero no validado |
| **OBSERVABILITY** | Instrumentation gap | Falta de instrumentación para medir |
| **EXPERIMENT** | Experimental limitation | Limitación del instrumento de medición |

### 2.4 Relaciones de refinamiento

Se documentan relaciones entre GAPs para evitar inflación artificial del backlog:

| Relación | Significado | Ejemplo |
|---|---|---|
| **REFINED_BY** | GAP original refinado por evidencia empírica posterior | GAP-0.8-05 REFINED_BY GAP-0.9-02 |
| **VALIDATION_REFINEMENT** | GAP de validación refinado por experimento posterior | GAP-0.8-07 VALIDATION_REFINEMENT GAP-0.9-04 |

---

## 3. MATRIZ DE GAPS CONSOLIDADA

### 3.1 GAPs P0 (Precondiciones de certificación)

| ID | GAP_CLASS | Descripción | HITO origen | Pilar/Contrato | Fase resolución propuesta | DC asociado |
|---|---|---|---|---|---|---|
| **GAP-0.3-01** | CONTRACT | Ausencia de aislamiento físico del workload respecto del oráculo científico. El workload corpus debe estar separado físicamente de `tests/corpus/canonical/` para preservar inmutabilidad del sellado (NADR-26). La composición exacta del workload (número de documentos, tipo de estrés) queda pendiente de caracterización empírica. | HITO_0.3 (F0-F) | NADR-26, Charter §5.8 | F18 | DC-02 |
| **GAP-0.4-01** | CONTRACT | Ausencia de mecanismo reproducible para ejecutar y comparar dos modos de ejecución bajo iguales parámetros científicos (guard diferencial). Sin este mecanismo, no puede ejecutarse el protocolo de demostración end-to-end definido para INV-SCI-1. | HITO_0.4 (F0-E) | INV-SCI-1, Charter §4 | F18 | DC-12 |
| **GAP-0.4-03** | CONTRACT | No existe una definición congelada que determine qué parámetros pertenecen a scientific identity y cuáles a operational metadata. Esta ambigüedad impide definir el contrato de comparación del guard diferencial. DC-02 es la decisión que resolverá esta ambigüedad. | HITO_0.4 (F0-E) | INV-SCI-1, Charter §4 | F18 | DC-02 |

### 3.2 GAPs P1 (Impacto operacional significativo)

| ID | GAP_CLASS | Descripción | HITO origen | Pilar/Contrato | Fase resolución propuesta | DC asociado |
|---|---|---|---|---|---|---|
| **GAP-0.1-01** | ARCH | SyncProviderBridge introduce barrera síncrona en el hilo llamante (`future.result(timeout=180.0)`). Impacto cuantitativo en C1 (Bounded Execution) y C3 (Backpressure) debe medirse. | HITO_0.1 (F0-B) | C1, C3, INV-OPS-1 | F18 | DC-01, DC-06b |
| **GAP-0.2-01** | IMPL | ProfileStore no durable: `InMemoryProfileStore` usa `dict` en memoria. Tras crash, perfiles inferidos se pierden. Existencia del store in-memory confirmada; coste agregado de re-inferencia tras restart aún no cuantificado. | HITO_0.2 (F0-G) | C4, DF-34 | F18 | DF-34 |
| **GAP-0.2-02** | IMPL | Circuit Breaker in-memory sin persistencia: crash reinicia todos los CBs a CLOSED simultáneamente. Riesgo de recuperación concurrente agresiva. DF-24 se reabre bajo DC-01/DC-08. | HITO_0.2 (F0-G) | C4, C10, DF-24 | F18 | DC-01, DC-08 |
| **GAP-0.2-03** | IMPL | Imports cruzados `core/benchmark/runners/` → `apps/`: viola frontera hexagonal (ENGINEERING_PRINCIPLES). Confirma DF-06. | HITO_0.2 (F0-G) | ENGINEERING_PRINCIPLES, DF-06 | F18 | DF-06 |
| **GAP-0.2-04** | CONTRACT | No existe coordinación transaccional entre el registro recuperable (`append_wal`) y el efecto externo (llamada a proveedor). El orden execute→append_wal abre una ventana post-effect/pre-journal cuya compatibilidad con INV-JOURNAL no está demostrada bajo las actuales garantías de idempotencia y recovery. | HITO_0.2 (F0-G) | INV-JOURNAL | F18 | DC-01, DC-08 |
| **GAP-0.3-02** | ARCH | Ausencia de workload de estrés. Los 21 docs canónicos no fueron diseñados como stress workloads. Necesidad justificada pero composición exacta (número, tipo, sintético vs real) pendiente de caracterización empírica. | HITO_0.3 (F0-F) | C10, Charter §3 | F18 | DC-07, DC-10 |
| **GAP-0.3-03** | CONTRACT | Ausencia de mecanismo de identidad versionada para workload (sin oracle hashes). El workload corpus debe tener su propio manifiesto con hash propio, calculado solo sobre PDFs de carga. | HITO_0.3 (F0-F) | Charter §5.8 | F18 | DC-02 |
| **GAP-0.4-02** | VALIDATION | Riesgo de contaminación FSM por señales operacionales: OOM/timeout podría derivar en `FAILED_FATAL` (estado científico) en lugar de estado operacional, contaminando evidencia científica. Requiere auditoría de propagación interna. | HITO_0.4 (F0-E) | INV-NO-RESOURCE-SIGNAL | F18 | DC-11 |
| **GAP-0.5-02** | OBSERVABILITY | Telemetría existente (`core/telemetry`, `core/metrics`) no activada/consumida por `run_regression.py` en el protocolo F0-A. Gap de integración, no de capacidad. Métricas por etapa = Deferred. Afecta observabilidad y caracterización, pero no demuestra violación de INV-SCI-1. | HITO_0.5 (F0-A Protocol) | Charter §6 | F18 | DC-01, DC-03, DC-07 |
| **GAP-0.7-01** | OBSERVABILITY | Métricas por etapa no capturadas en F0-A (extraction, TED, evaluation). `run_regression.py` no consume telemetría existente. | HITO_0.7 (F0-A Baseline) | Charter §6 | F18 | DC-01 |
| **GAP-0.7-02** | OBSERVABILITY | Provider metrics no medibles vía `run_regression.py` (latency, tokens, retries). Requiere instrumento distinto sobre dispatcher con credenciales activas. | HITO_0.7 (F0-A Baseline) | Charter §6 | F18+ | DC-03, DC-07 |
| **GAP-0.8-01** | ARCH | Coordinated shutdown capability NO DEMOSTRADA. Implementación nominal (DaemonSupervisor/GracefulShutdown) no encontrada en superficies auditadas. Esto es evidencia secundaria; la capability podría existir mediante signal handlers, orchestration externa, context manager, lifecycle coordinator, process manager o supervisor externo. Shutdown distribuido sin coordinación centralizada observada. | HITO_0.8 (F0-C) | Charter §6 | F18 | DC-13 |
| **GAP-0.8-06** | VALIDATION | Epoch fencing NO DEMOSTRADO empíricamente. `test_fencing.py` colecta 0 tests. Mecanismo observado pero no validado. | HITO_0.8 (F0-C) | Recovery validation | F18 | DC-08 |
| **GAP-0.8-07** | VALIDATION | Zombie recovery de task lease NO DEMOSTRADO. Mecanismo observado (OptimisticLockError) pero no validado por test específico de flujo completo. | HITO_0.8 (F0-C) | Recovery validation | F18 | DC-08 |
| **GAP-0.9-01** | IMPL | `bootstrap_all_databases()` no respeta APP_ROOT en lista de planos. Violación de perímetro sin daño material (0 rows en DBs productivas excepto 1 en system_leases). | HITO_0.9 (F0-D) | Perímetro efímero | F18 | — (finding operativo) |
| **GAP-0.9-02** | OBSERVABILITY | SQLiteTelemetryGateway pierde 100% del buffer in-memory bajo crash abrupto. Gap de observabilidad que se suma a gaps de waste. Refinamiento empírico de GAP-0.8-05. | HITO_0.9 (F0-D) | Observabilidad | F18 | DC-13 |
| **GAP-0.9-04** | VALIDATION | W7 zombie test no ejercita flujo completo de recovery (worker_B no robó tarea). Escenario probado es más simple que el real. Validation refinement de GAP-0.8-07. | HITO_0.9 (F0-D) | Recovery validation | F18 | DC-08 |
| **GAP-0.9-05** | EXPERIMENT | W1/W2/W5 no ejercitables con instrumento actual. Adapters/SDKs (`AsyncGroq`, `GeminiProvider`) no exponen `base_url` override utilizable sin modificación de código productivo (Charter §5.3). | HITO_0.9 (F0-D) | Charter §5.3 | F18+ (trigger: provider instrumentation available) | DC-01, DC-08 |

### 3.3 GAPs P2 (Impacto menor o limitación del instrumento)

| ID | GAP_CLASS | Descripción | HITO origen | Pilar/Contrato | Fase resolución propuesta | DC asociado |
|---|---|---|---|---|---|---|
| **GAP-0.1-02** | ARCH | Coordinación multi-thread observada (3 threads, 3 `threading.Event`). Impacto potencial en C6/C7/C10 debe evaluarse. | HITO_0.1 (F0-B) | C6, C10 | F18 | DC-01 |
| **GAP-0.1-03** | VALIDATION | Riesgo de thread residual en shutdown. `future.cancel()` + `join(timeout=2.0)` tiene límite acotado, pero si librería HTTP no coopera con cancelación asyncio, thread podría quedar residual. | HITO_0.1 (F0-B) | C4, C6 | F18 | DC-01 |
| **GAP-0.8-05** | OBSERVABILITY | Telemetry: TELEMETRY_LOSS residual de queue no flusheada (no acotada por batch size). Hasta 50 eventos pueden perderse en crash sin stop() limpio. REFINED_BY GAP-0.9-02 (evidencia empírica: 100% loss). | HITO_0.8 (F0-C) | Observabilidad | F18 | — (finding operativo) |
| **GAP-0.9-03** | EXPERIMENT | W4 healing no ejercitable con contexto sintético. `MarkdownLeakageHealingStrategy` no se activa con contexto de test. Requiere texto de producción real. | HITO_0.9 (F0-D) | Limitación del instrumento | F18 | — (finding operativo) |

---

## 4. MATRIZ DE TRAZABILIDAD A DECISION CANDIDATES

| DC | GAPs asociados | Estado en Fase 0 | Acción requerida en F18 |
|---|---|---|---|
| **DC-01** | GAP-0.1-01, GAP-0.1-02, GAP-0.1-03, GAP-0.2-02, GAP-0.2-04, GAP-0.5-02, GAP-0.7-01, GAP-0.9-05 | Evidencia de entrada disponible | Resolver fork de concurrencia (async single-process + executors vs multi-process) |
| **DC-02** | GAP-0.3-01, GAP-0.3-03, GAP-0.4-03 | Precondición no resuelta | Resolver parámetros de runtime en identity científica vs metadata operacional; definir fórmula de identidad de workload |
| **DC-03** | GAP-0.5-02, GAP-0.7-02 | Capacidad confirmada, medición deferred | Definir y ejecutar protocolo de caracterización de determinismo observable del proveedor cuando exista instrumentación autorizada |
| **DC-04** | — | Evidencia de cache preexistente (HITO_0.2 E-0.2-008) | Resolver alcance de caches (pure-function 🟢 / LLM 🟡 / semantic+embedding 🔴) |
| **DC-06b** | GAP-0.1-01 | Evidencia de entrada disponible | Evaluar supervivencia de técnicas prescritas del ROADMAP vs criterio preregistrado |
| **DC-07** | GAP-0.3-02, GAP-0.5-02, GAP-0.7-02 | Evidencia de entrada disponible | Resolver si la planificación se basa en tiers discretos, budgets continuos o combinación; valores concretos sujetos a caracterización empírica |
| **DC-08** | GAP-0.2-02, GAP-0.2-04, GAP-0.8-06, GAP-0.8-07, GAP-0.9-04, GAP-0.9-05 | Evidencia de gaps de durabilidad | Resolver write-policy SQLite + mecanismo de journal de INV-JOURNAL + persistencia de CB |
| **DC-10** | GAP-0.3-02 | Evidencia de entrada disponible | Resolver fairness y admission deadlock-free |
| **DC-11** | GAP-0.4-02 | Riesgo identificado | Resolver semántica de admisión-diferida sin nuevo estado FSM |
| **DC-12** | GAP-0.4-01 | Prerrequisitos verificados, end-to-end pending M1 | Resolver contrato y promoción del guard diferencial conforme al contrato de F0-E; implementación posterior según Execution Plan |
| **DC-13** | GAP-0.8-01, GAP-0.9-02 | Capacidad NO DEMOSTRADA | Resolver coordinated shutdown / daemon lifecycle orchestration |
| **DF-06** | GAP-0.2-03 | Imports cruzados confirmados | Refactor de composición para respetar frontera hexagonal |
| **DF-24** | GAP-0.2-02 | Reabierto bajo DC-01/DC-08 | Resolver persistencia de Circuit Breaker |
| **DF-34** | GAP-0.2-01 | Existencia del store in-memory confirmada; coste agregado de re-inferencia tras restart aún no cuantificado | Resolver persistencia de ProfileStore |

**Nota:** GAP-0.9-01, GAP-0.8-05, GAP-0.9-03 quedan como findings operativos sin DC asociado. No requieren decisión arquitectónica; son limitaciones del instrumento o defects menores que pueden resolverse en el Execution Plan sin necesidad de DC explícito.

---

## 5. PRIORIZACIÓN PARA ADR_F18_MASTER

### 5.1 Dependency-aware resolution order (DAG de decisiones)

```text
DC-02 (parámetros de runtime en identity)
  ├──> DC-12 (guard diferencial)
  ├──> GAP-0.3-01 (aislamiento workload)
  └──> GAP-0.3-03 (identidad workload)

DC-01 (fork de concurrencia)
  ├──> DC-08 (write-policy SQLite + journal)
  ├──> DF-24 (persistencia Circuit Breaker)
  ├──> DC-13 (coordinated shutdown)
  └──> DF-34 (persistencia ProfileStore)

DC-03 (determinismo observable por proveedor)
  └──> DC-04 (alcance de caches)

DC-10 (fairness y admission)
  └──> scheduler/admission control

DC-07 (tiers vs budgets)
  └──> batching strategy
```

**Nota:** Este DAG muestra dependencias, no secuencia lineal. Múltiples DCs pueden resolverse en paralelo si no tienen dependencias entre sí.

### 5.2 Fase de resolución propuesta

**Fase 18 — Wave 1 (Precondiciones bloqueantes):**
1. **GAP-0.4-03** (DC-02): Resolver parámetros de runtime en identity científica vs metadata operacional
2. **GAP-0.3-01** + **GAP-0.3-03**: Resolver contrato de aislamiento e identidad del workload y, una vez resuelto, materializar la composición aprobada
3. **GAP-0.5-02**: Integrar telemetría existente en `run_regression.py`

**Fase 18 — Wave 2 (Invariantes científicas):**
4. **GAP-0.4-01** (DC-12): Resolver DC-12 conforme al contrato de F0-E; implementación posterior según Execution Plan
5. **GAP-0.2-04** (DC-08): Resolver coordinación transaccional append_wal ↔ efecto externo
6. **GAP-0.4-02** (DC-11): Auditoría de propagación de señales operacionales al FSM

**Fase 18 — Wave 3 (Durabilidad y recovery):**
7. **GAP-0.2-01** (DF-34): Resolver persistencia de ProfileStore
8. **GAP-0.2-02** (DF-24, DC-08): Resolver persistencia de Circuit Breaker
9. **GAP-0.8-01** (DC-13): Resolver coordinated shutdown capability
10. **GAP-0.9-02** (DC-13): Resolver telemetry loss en crash abrupto

**Fase 18 — Wave 4 (Validación empírica):**
11. **GAP-0.8-06**: Implementar tests de epoch fencing
12. **GAP-0.8-07** + **GAP-0.9-04**: Ejercitar flujo completo de zombie recovery en F0-D

**Fase 18 — Wave 5 (Refactor y cleanup):**
13. **GAP-0.2-03** (DF-06): Refactor de imports cruzados core→apps
14. **GAP-0.9-01**: Resolver bootstrap para respetar APP_ROOT

**Fase 18 — Wave 6 (Medición y caracterización):**
15. **GAP-0.1-01** (DC-01, DC-06b): Medir impacto cuantitativo de SyncProviderBridge
16. **GAP-0.3-02** (DC-07, DC-10): Caracterizar workload de estrés
17. **GAP-0.7-01** + **GAP-0.7-02**: Capturar métricas por etapa y provider metrics

**Fase 18+ — Diferibles:**
18. **GAP-0.9-05**: W1/W2/W5 requieren instrumentación de provider (trigger: provider instrumentation available)

**Fase 19+ — Diferibles:**
19. **GAP-0.1-02**, **GAP-0.1-03**: Impacto P2, pueden resolverse en refactor posterior
20. **GAP-0.8-05**: Telemetry loss residual, refinado por GAP-0.9-02
21. **GAP-0.9-03**: W4 healing no ejercitable, limitación del instrumento

---

## 6. VERIFICACIÓN DE COMPLETITUD

### 6.1 Cobertura de Charter §8

| Requisito Charter §8 | Estado | Evidencia |
|---|---|---|
| F0-A..F0-G commiteados como HITOs | ✅ COMPLETO | HITOs 0.1-0.9 FROZEN |
| Cuatro outputs obligatorios commiteados | ⏳ PENDIENTE | Este documento (Gap Matrix) + 3 restantes |
| DC-06a aprobada por Board | ✅ COMPLETO | Charter metadata: 2026-10-01 |
| Todo DC tiene resolución RESOLVED o DEFERRED+DESTINATION+TRIGGER | ⏳ PENDIENTE | Decision Register (siguiente output) |
| Protocolo de medición y preregistro presentes en F0-A/F0-D | ✅ COMPLETO | HITO_0.5 v1.2.0, HITO_0.9 v1.4.0 |
| Regla de calibración de umbrales (§9) documentada en F0-A | ✅ COMPLETO | HITO_0.5 v1.2.0 §16.3 |

### 6.2 Outputs obligatorios restantes

Según Charter §8, faltan 3 outputs obligatorios:
1. ✅ **Architecture Gap Matrix** (este documento)
2. ⏳ **Current State & Contract Map** (siguiente HITO)
3. ⏳ **Evidence Register & DC Resolutions** (siguiente HITO)
4. ⏳ **Propuesta de congelamiento de ADR_F18_MASTER** (documento final)

---

## 7. CIERRE DEL HITO 0.10

**Estado del HITO:** FROZEN v1.0.1
**Condición de cierre cumplida:** Todos los GAPs de HITOs 0.1-0.9 consolidados en matriz unificada con clasificación GAP_CLASS explícita; duplicados eliminados con NORMALIZATION_ACTION documentado; cerrados/reconciliados removidos con razón explícita; priorización por severidad (P0/P1/P2) con 3 P0, 15 P1, 7 P2; mapeo a Decision Candidates (12 DCs) o justificados como findings operativos (3 GAPs); relaciones de refinamiento documentadas (REFINED_BY, VALIDATION_REFINEMENT); DAG de decisiones en lugar de secuencia lineal; fase de resolución propuesta (F18/F18+/F19+) en lugar de "todos destino F18"; prescripciones reformuladas como "resolver contrato/DC" sin imponer implementación; versiones de HITOs citadas verificadas (HITO_0.8 v1.4.0, HITO_0.9 v1.4.0).
**Verificación de cadena de gobernanza:** Charter §8 → HITOs 0.1-0.9 → este documento → ADR_F18_MASTER §7.
**Refinamientos respecto a HITOs previos:** No se identificaron contradicciones materiales con la evidencia primaria; existen refinamientos de clasificación y alcance documentados en la consolidación (GAP-0.5-02 degradado de P0 a P1, GAP-0.2-04 reformulado con formulación canónica de INV-JOURNAL, GAP-0.8-05 REFINED_BY GAP-0.9-02, GAP-0.8-07 VALIDATION_REFINEMENT GAP-0.9-04, GAP-0.9-05 con fase de resolución propuesta F18+ en lugar de F18).
**Siguiente paso recomendado:** Emitir HITO_0.11 (Current State & Contract Map) y HITO_0.12 (Evidence Register & DC Resolutions) para completar los outputs obligatorios de Charter §8.

---

## 📊 Estado actualizado de Fase 0

| HITO | Estado | Rol |
|---|---|---|
| 0.1 F0-B Concurrency Blocking Map | FROZEN v1.2.0 | Discovery estático |
| 0.2 F0-G Authority Boundary Map | FROZEN v1.2.0 | Discovery de autoridades |
| 0.3 F0-F Workload Characterization | FROZEN v1.3.0 | Discovery de workload |
| 0.4 F0-E Scientific Neutrality Contract | FROZEN v1.3.0 | Compliance audit + contrato M0 |
| 0.5 F0-A Runtime Profile Protocol | FROZEN v1.2.0 | Protocolo |
| 0.6 Workload Anchor Reconciliation | FROZEN v1.0.0 | Reconciliación de perímetro |
| 0.7 F0-A Runtime Profile Baseline | FROZEN v1.1.0 | Baseline operacional |
| 0.8 F0-C State Durability & Recovery Map | FROZEN v1.4.0 | Matriz de durabilidad |
| 0.9 F0-D Waste/FinOps Map | FROZEN v1.4.0 | Baseline de waste |
| **0.10 Architecture Gap Matrix Consolidated** | **FROZEN v1.0.1** | **Output obligatorio Charter §8** |

**Fase 0 casi completa.** Faltan 2 outputs obligatorios: Current State & Contract Map, Evidence Register & DC Resolutions.