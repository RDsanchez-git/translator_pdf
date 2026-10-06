# PHASE 18.1 EXECUTION PLAN v1.0.3
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.4
**Status:** IN_PROGRESS
**Date:** 2026-10-05
**Aprobación Architecture Board:** — (pendiente)
**Supersedes:** v1.0.0
**Derived From:** 2 NADRs FROZEN (NADR-F18-01 v1.0.3, NADR-F18-02 v1.0.1) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Subfase 18.1 (Execution Plane & Concurrency). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial. 4 Gates, 14 Waves, 32 Tasks. Mapeo completo de 52 reglas. |
| 1.0.1 | 2026-10-04 | Corrección de consistencia (11 cambios): (1) Conteo corregido a 31 Tasks. (2) Gate 3 corregido a 11 Tasks. (3) DF-06 desvinculado de NADR-F18-02 §5.8 R27; autoridad correcta es ENGINEERING_PRINCIPLES §II. (4) Task 3.5.2: cierre de DF-06 derivado al Findings Register, no resuelto por la Task. (5) Semántica de "Rules Implemented" aclarada para Tasks de verificación. (6) §7: DONE alcanzable por combinación implementación+verificación. (7) Gate 4.1: "propiedades estructurales y contractuales verificables mediante análisis estático". (8) DC-02-A reformulado como DC-02 (descomposición operativa: definición provisional). (9) Global DoD: evidencia decisional/probatoria permitida para reglas no implementables como código. (10) MIG-01: "backup" sustituido por "snapshot/retención operacional". (11) Gate 1 explicitado como evidence materialization. |
| 1.0.2 | 2026-10-05 | Wave 1.2 COMPLETED (Tasks 1.2.1, 1.2.2). Benchmark de SyncProviderBridge ejecutado: overhead p95 2-10ms, throughput ratio 1.00x (sin diferencia), backpressure idéntico, RSS delta 0.02 MB. Resultado contraintuitivo: la barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugería. Derivado DF-09 (REVIEW_REQUIRED) — requiere reevaluación de DC-01. NADR-F18-02 §5.9 R32 → DONE. |
| 1.0.3 | 2026-10-05 | Wave 1.3 COMPLETED (Tasks 1.3.1, 1.3.2). Baselines FROZEN v1.0.0: F18_BASELINE_CONCURRENCY.md (modelo dual, 3 threads, barrera, backoff, shutdown) y F18_BASELINE_METRICS_PER_STAGE.md (HITO_0.7 + telemetría Wave 1.1 + benchmark Wave 1.2 + estado calibración 1/6 técnicas). Gate 1 ✅ COMPLETED (Waves 1.1, 1.2, 1.3 todas DONE). NADR-F18-02 §5.9 R31 → DONE. Correcciones de consistencia: (I1) Tasks 1.1.1, 1.1.2 Status TODO → DONE (ya estaban completadas según notas de implementación); (I2) Task 1.2.2 nota de implementación completada. |
| 1.0.4 | 2026-10-05 | Wave 2.1 COMPLETED (Tasks 2.1.1, 2.1.2, 2.1.3). Contrato F18_IDENTITY_BOUNDARY_CONTRACT.md FROZEN v1.0.1 (DC-02-A) emitido en decisions/: 3 dimensiones ortogonales (Scientific Identity, Execution Identity, Operational State) + Workload Identity (GAP-0.3-03 documentado), reglas de no-colapso, cláusula de invalidación con 3 condiciones + escalación (R17), gobernanza de modificaciones (R16), matriz regla-por-regla de las 10 reglas de Wave 2.1. 10 reglas NADR-F18-01 → DONE. Derivado DF-13 (model_de_execution ausente de identity_chain; INV-EXEC-IDENTIFIABILITY parcial). Nota de colisión de numeración DF-09 (F18 vs F17-BIS) documentada en contrato §10. Gate 2 🟡 IN PROGRESS. |


---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

    ADR_F18_MASTER FROZEN (visión y capacidades de Fase 18)
    |
    v
    ADR_F18.1 v1.0.2 FROZEN (visión de Subfase 18.1)
    |
    v
    NADR-F18-01 v1.0.3 FROZEN (Execution Identity & Scientific Isolation, 20 reglas)
    NADR-F18-02 v1.0.1 FROZEN (Bounded Concurrent Execution, 32 reglas)
    | Cada regla se identifica por: NADR-XX §sección Rregla
    v
    PHASE_18.1_EXECUTION_PLAN (ESTE DOCUMENTO)
    | Mapea: Task -> Rules -> Gate/Wave -> Status -> Implementation Evidence
    v
    FASE_18_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
    | Mapea: Finding -> Classification -> Batch -> Resolution -> Status
    v
    Implementación (commits, tests)
    | Referencia reglas como Implementation Evidence
    v
    Verificación (CI gates, regression tests)

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

    NADR-{XX} §{sección} R{regla}

Ejemplo: NADR-F18-02 §5.1 R1 → NADR-F18-02, sección 5.1, regla 1.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (NADR-F18-01 + NADR-F18-02 = 52 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md), no en este documento. Este plan los identifica y los deriva al registro por ID:

    DF-{XX} | GF-{XX}

**Responsabilidad de este documento:** Identificar el hallazgo y derivarlo al registro.
**Responsabilidad del Findings Register:** Clasificar, resolver o diferir el hallazgo.

### 1.4 Operational Principles

- **Los NADRs no pertenecen a una fase.** Son reglas constitucionales permanentes. Lo que se asigna por subfase son sus reglas individuales.
- **El Execution Plan es la única fuente de verdad temporal.** No existen matrices de trazabilidad paralelas.
- **Política de referencias cruzadas:** Una regla puede aparecer en múltiples tareas **únicamente** cuando una tarea la implementa y otra la verifica o completa. Nunca deben existir dos tareas implementando la misma obligación.
- **Semántica de "Rules Implemented" en Tasks de verificación:** En Tasks cuyo objetivo sea exclusivamente Verification/Validation (Gate 4), la referencia a una regla en la columna "Rules Implemented" se interpreta como **regla cubierta/verificada por la Task**, no como una segunda implementación de la obligación. La implementación normativa permanece atribuida a la Task de materialización correspondiente (Gate 3).
- **El estado de una regla es derivado.** Una regla no tiene estado propio. Su estado es el estado de la tarea que la implementa, salvo que esté distribuida (implementada en una tarea, verificada en otra). El estado DONE de una regla exige que ambas responsabilidades —implementación y verificación, cuando correspondan— estén satisfechas.
- **Medición antes de decisión:** DC-01 no se resuelve sin evidencia cuantitativa previa (GAP-0.5-02, GAP-0.1-01). DC-02 (descomposición operativa: definición provisional) puede avanzar en paralelo con la medición al no existir dependencia entre ellos (ADR_F18.1 §3).
- **Técnicas subordinadas a evidencia:** Ninguna técnica candidata (pure async, object pools, zero-copy, lazy loading, batching) se implementa sin evidencia cuantitativa de beneficio conforme a Charter §9 (DC-06b).

### 1.5 Documento Vivo — Convención de Actualización

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §11. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§3)
- Status Dashboard (§6)
- Traceability Appendix (§7)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

### 1.6 Estructura de la Subfase 18.1

| Dimensión | Valor |
|---|---|
| Gates | 4 |
| Waves | 14 |
| Tasks | 31 |
| Reglas NADR-F18-01 | 20 |
| Reglas NADR-F18-02 | 32 |
| Total reglas a trazar | 52 |
| DCs a resolver | DC-01, DC-02 (descomposición operativa: definición provisional), DC-05, DC-06b (evaluación), DF-06 (condicional) |

---

## 2. GATE 1 — Evidence & Measurement Baseline

**Objective:** Reunir la evidencia cuantitativa requerida para la resolución de DC-01 (fork de concurrencia). Resolver GAP-0.5-02 (telemetría por etapa) y GAP-0.1-01 (impacto de SyncProviderBridge). Sin este Gate, DC-01 no puede resolverse conforme a NADR-F18-02 §5.9 R31. **Este Gate es evidence materialization, no implementación de comportamiento del execution plane.**
**Execution Mode:** Secuencial (Wave 1.1 → 1.2 → 1.3)
**Rollback Plan:** Si la medición revela que el instrumento es inadecuado, se rediseña el protocolo de medición sin modificar código productivo. Los datos de medición son efímeros y no afectan estado normativo.
**Gate Status:** ✅ COMPLETED

### 2.1 Wave 1.1 — Telemetry Integration (GAP-0.5-02)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-10-05
**Fecha de cierre:** 2026-10-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Integrar la infraestructura de telemetría existente (SQLiteTelemetryGateway, ProductionTelemetryEvent) en el entry point de medición (run_regression.py) para capturar métricas por etapa del pipeline | NADR-F18-02 §5.9 R31 | Medium | — | DONE |
| **1.1.2** | Validar que el pipeline de recolección de telemetría produce datos completos y consistentes por etapa (extraction, normalización, segmentación, chunking, traducción, validación, ensamblado, TED, hashing, serialización, SQLite) | NADR-F18-02 §5.9 R31 | Low | 1.1.1 | DONE |

#### Notas de implementación — Task 1.1.1

> Completada 2026-10-05. Creado `core/telemetry/regression_gateway.py` con
> `RegressionTelemetryGateway(TelemetryPort)`: adaptador síncrono SQLite WAL
> con context manager, fail-safe (catch sqlite3.Error + TypeError + ValueError),
> schema creation en `__enter__`. Modificado `tools/evaluation/run_regression.py`:
> imports agregados, `telemetry_execution_id` (uuid4) generado en `main()`
> separado de `identity_chain.execution_id` (NADR-F18-01 §5.2 R8),
> `_run_evaluation()` instrumentado con 3 stages: EXTRACTION (stage_index=0),
> TOPOLOGY_EVALUATION (stage_index=1), REPORT_ASSEMBLY (stage_index=2).
> Telemetría persiste en `output_dir/telemetry.db` como evidencia operacional
> separada (NADR-F18-02 §5.7 R25).
> Pyright: 0 errors, 0 warnings. Tests: 6/6 passed.
> DF-07 resuelto. DF-08 reclasificado como CLOSED (NAR) — falso positivo
> por truncamiento de pegado PowerShell; verificación forense confirmó que
> `draft = _layout_block_to_draft(...)` y `error_summary = "; ".join(report.errors)`
> existen en el código real (pipeline_factory.py:210, pipeline_factory.py:202).

#### Notas de implementación — Task 1.1.2

> Completada 2026-10-05. Validación de completitud ejecutada contra
> `reports/regression_test/telemetry.db` (regresión SMOKE, 5 documentos).
> Resultados: 1 execution_id único, 0 NULLs en 8 campos requeridos,
> 11/11 timestamps ISO 8601 válidos, 10/10 stages con document_id en metadata,
> latencias consistentes (EXTRACTION avg=0.0592s, TOPOLOGY_EVALUATION avg=0.0550s,
> REPORT_ASSEMBLY <0.0001s). Veredicto: PASS — datos completos y consistentes.
> NADR-F18-02 §5.9 R31 satisfecho para Wave 1.1.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-07 | Ausencia de adaptador síncrono para TelemetryPort. Solo existe SQLiteTelemetryGateway (asíncrono, ProductionTelemetryEvent). Prerrequisito técnico de Task 1.1.1. | Findings Register — RESOLVED en Task 1.1.1 |
| DF-08 | Variables no definidas en pipeline_factory.py (`error_summary`, `draft`). Reportado como bug crítico durante inspección forense. | Findings Register — CLOSED (NAR), falso positivo por truncamiento de pegado PowerShell |
| GF-01 | NullTelemetryAdapter duplicado en core/telemetry/ports.py y core/telemetry/adapters.py con APIs incompatibles. | Findings Register — IMPLEMENTATION_REQUIRED, consolidación diferida a Gate 3 |

### 2.2 Wave 1.2 — SyncProviderBridge Impact Measurement (GAP-0.1-01)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-10-05
**Fecha de cierre:** 2026-10-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Diseñar y ejecutar el protocolo de medición del impacto cuantitativo de la barrera síncrona (SyncProviderBridge) sobre bounded execution (C1) y backpressure (C3) bajo carga, conforme al criterio preregistrado de Charter §9 | NADR-F18-02 §5.9 R31 | Medium | 1.1.2 | DONE |
| **1.2.2** | Documentar los resultados cuantitativos de la medición: latencia p95 por etapa I/O, impacto en concurrencia efectiva, comportamiento de backpressure bajo carga | NADR-F18-02 §5.9 R31, R32 | Low | 1.2.1 | DONE |

#### Notas de implementación — Task 1.2.1

> Completada 2026-10-05. Creado `tools/evaluation/benchmark_sync_bridge.py`:
> instrumento de medición efímero conforme a ADR_F18_MASTER §7.1 (medición
> externa, sin mutación de código productivo). 4 experimentos sintéticos:
> (1) overhead por llamada con MockLLMProvider de latencia fija (0.1s/0.5s/1.0s),
> (2) throughput bajo carga con N=1,2,5,10,20 workers,
> (3) backpressure ante burst de 50 unidades con concurrency=5,
> (4) RSS delta del thread dedicado del bridge.
> Mocks deterministas: MockLLMProvider (asyncio.sleep), MockPromptBuilder
> (envelopes fijos que aíslan la variable: solo la barrera cambia entre
> Path A bridge y Path B async directo).
> Verificaciones forenses de imports previas a la ejecución:
> PromptBudget es @dataclass(frozen=True, slots=True) con campos
> system_tokens/context_tokens/payload_tokens/reserved_tokens/window_limit;
> NodeId es Annotated[str, StringConstraints(pattern=r"^[^:]+$")];
> control_plane existe en ASTNode (línea 122); PromptIntent.TRANSLATE y
> PromptConstraints() con defaults. Un falso positivo sobre PromptBudget
> (decorador no capturado por Select-String -Context 0,20) fue descartado
> con verificación de línea previa (línea 28), mismo patrón que DF-08.
> Limitaciones documentadas en el JSON: Exp 2 usa asyncio.Semaphore como
> aproximación de AsyncDispatcher (sin PriorityQueue ni validation/healing);
> Exp 1-4 no incluyen TaskLeaseHeartbeat ni backoff exponencial; el daemon
> real es SECUENCIAL (N=1), los experimentos de concurrencia miden el
> overhead de la barrera, no el comportamiento actual del daemon.
> Pyright: 0 errors. Sin tests de unidad (instrumento de medición efímero).

#### Notas de implementación — Task 1.2.2

> Completada 2026-10-05. Resultados cuantitativos del benchmark documentados:
>
> **Exp 1 — Overhead por llamada:** p95 = 2.05ms (0.1s), 9.28ms (0.5s),
> 10.40ms (1.0s). El overhead CRECE con la latencia del provider (no es
> constante; sugiere contention en run_coroutine_threadsafe o overhead del
> event loop dedicado proporcional al tiempo de espera).
>
> **Exp 2 — Throughput bajo carga:** ratio async/bridge = 1.00x en N=1,2,
> 5,10,20. SIN DIFERENCIA de throughput. ThreadPoolExecutor con bridge es
> tan eficiente como asyncio.Semaphore para este workload I/O-bound.
>
> **Exp 3 — Backpressure bajo burst:** wall=20.08s idéntico ambos paths,
> peak_threads=5, completed=50. SIN DIFERENCIA.
>
> **Exp 4 — RSS delta:** 0.02 MB. Costo de memoria del thread dedicado
> prácticamente cero.
>
> **Evaluación contra criterio preregistrado (Charter §9):**
> - Métrica: latencia p95 por etapa I/O → overhead 2-10ms (pequeño)
> - Dirección esperada si se elide: ↓ → margen marginal (2-10ms)
> - Condición sin ↑RSS: ✅ se cumple (0.02 MB)
> - Throughput: sin mejora si se elide (ratio 1.00x)
>
> **Veredicto:** El criterio NO se cumple claramente; la elisión de
> SyncProviderBridge NO está justificada por la evidencia cuantitativa.
> La hipótesis original de GAP-0.1-01 (inferencia estática de HITO_0.1
> E-0.1-001) es corregida por la primera medición cuantitativa. Derivado
> DF-09 (REVIEW_REQUIRED) al Findings Register. NADR-F18-02 §5.9 R31
> satisfecho para Wave 1.2. R32 satisfecho: el benchmark documenta sin
> prescribir modelo de concurrencia.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-09 | Resultado contraintuitivo: la barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugiere. Overhead p95 pequeño (2-10ms), throughput idéntico (ratio 1.00x), backpressure idéntico, RSS despreciable (0.02 MB). La hipótesis original de HITO_0.1 E-0.1-001 (inferencia estática) es corregida por la primera medición cuantitativa. Implica reevaluación de DC-01: la elisión de SyncProviderBridge no está justificada por la evidencia. | Findings Register — REVIEW_REQUIRED (reevaluación de DC-01) |

### 2.3 Wave 1.3 — Baseline Documentation

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-10-05
**Fecha de cierre:** 2026-10-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Documentar el baseline de concurrencia actual: modelo híbrido dual, 3 threads independientes, barrera síncrona, backoff exponencial, shutdown con bounded join | NADR-F18-02 §5.9 R31 | Low | 1.2.2 | DONE |
| **1.3.2** | Documentar el baseline de métricas por etapa del pipeline conforme a HITO_0.7 v1.1.0 (wall, CPU, peak RSS, allocations, I/O wait) | NADR-F18-02 §5.9 R31 | Low | 1.1.2 | DONE |

#### Notas de implementación — Task 1.3.1

> Completada 2026-10-05. Creado `docs/baselines/F18_BASELINE_CONCURRENCY.md`
> (FROZEN v1.0.0). Integra evidencia de HITO_0.1 v1.2.0 (forense),
> benchmark Wave 1.2 (cuantitativa) e inspección de código de producción.
> Documenta: modelo híbrido dual (SyncProviderBridge + AsyncDispatcher),
> 3 threads independientes (main loop, heartbeat, bridge event loop),
> barrera síncrona con overhead 2-10ms y timeout 180s, backoff exponencial
> (base=1.0s, max=4.0s, factor=1.2, jitter=±0.5s), shutdown con bounded
> join (timeout=2.0s). Incluye sección de trazabilidad DC-01 (alimenta
> Gate 2 Wave 2.2 sin resolver DC-01 prematuramente), limitaciones del
> benchmark (L1-L5), gaps residuales (GAP-0.1-02, GAP-0.1-03), y
> verificación NADR. DC-01 NO se resuelve en Gate 1 (evidence
> materialization); se resuelve en Gate 2 Wave 2.2 conforme a
> NADR-F18-02 §5.9 R30.

#### Notas de implementación — Task 1.3.2

> Completada 2026-10-05. Creado `docs/baselines/F18_BASELINE_METRICS_PER_STAGE.md`
> (FROZEN v1.0.0). Integra evidencia de 3 fuentes: HITO_0.7 v1.1.0
> (métricas agregadas: wall 1.659s CV 0.41%, CPU 1.448s CV 0.48%, peak
> WS single-process 76.98 MB CV 0.07%), telemetría Wave 1.1 (métricas por
> etapa de regression: EXTRACTION avg 0.0592s, TOPOLOGY_EVALUATION avg
> 0.0550s, REPORT_ASSEMBLY <0.0001s), benchmark Wave 1.2 (overhead,
> throughput, RSS). Incluye tabla de estado de calibración Charter §9:
> 1/6 técnicas evaluadas (SyncProviderBridge elision → rechazada, overhead
> negligible y throughput idéntico), 5/6 pendientes de métricas específicas.
> GAP-0.7-01 parcialmente resuelto (regression sí, daemon producción no).
> GAP-0.7-02 y GAP-0.7-05 documentados como DEFERRED. NADR-F18-02 §5.9
> R31 satisfecho para Wave 1.3.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | Sin hallazgos nuevos en Wave 1.3. Baselines documentados sin identificar gaps adicionales a los ya registrados. GAP-0.7-01 parcialmente resuelto (telemetría Wave 1.1 cubre el pipeline de regression); GAP-0.7-02 y GAP-0.7-05 permanecen DEFERRED conforme a HITO_0.7 §14. | — |

### 2.4 Gate 1 Exit Criteria

Todas las reglas de NADR-F18-02 §5.9 R31 referenciadas en este Gate deben alcanzar estado DONE. Específicamente:

- GAP-0.5-02 resuelto: telemetría integrada en el entry point de medición con datos por etapa ✅
- GAP-0.1-01 resuelto: impacto cuantitativo de SyncProviderBridge medido y documentado ✅
- Baseline de concurrencia actual documentado: F18_BASELINE_CONCURRENCY.md FROZEN v1.0.0 ✅
- Baseline de métricas por etapa documentado: F18_BASELINE_METRICS_PER_STAGE.md FROZEN v1.0.0 ✅
- Evidencia suficiente para evaluar DC-01 conforme a NADR-F18-02 §5.9 R31 ✅

### 2.5 Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 6/6 (1.1.1, 1.1.2, 1.2.1, 1.2.2, 1.3.1, 1.3.2) |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ R31 DONE, R32 DONE (2/2) |
| 3 | Gate Exit Criteria satisfechos | ✅ 5/5 criterios |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ 4 hallazgos (DF-07 RESOLVED, DF-08 CLOSED (NAR), GF-01 IMPLEMENTATION_REQUIRED, DF-09 REVIEW_REQUIRED) |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 6/6 passed |
| 7 | Notas de implementación completas para todas las Tasks | ✅ 6/6 |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-10-05

---

## 2B. GATE 2 — Architectural Decisions

**Objective:** Resolver DC-01 (modelo de concurrencia), DC-02 (descomposición operativa: definición provisional de frontera de identidad) y DC-05 (estructura de contextos de ejecución). DC-02 (definición provisional) puede avanzar en paralelo con Gate 1 al no existir dependencia (ADR_F18.1 §3). DC-01 requiere Gate 1 completado. DC-05 requiere DC-01 resuelto.
**Execution Mode:** Mixto (Wave 2.1 en paralelo con Gate 1; Wave 2.2 secuencial post-Gate 1; Wave 2.3 secuencial post-Wave 2.2)
**Rollback Plan:** Si DC-01 revela que ningún modelo candidato satisface las reglas de NADR-F18-02, se escala al Architecture Board para reevaluación del criterio preregistrado. No se fuerza una decisión sin evidencia.
**Gate Status:** 🟡 IN PROGRESS

### 2B.1 Wave 2.1 — Identity Boundary Definition (DC-02, descomposición operativa: definición provisional) [PARALELO con Gate 1]

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-10-05
**Fecha de cierre:** 2026-10-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Definir la frontera provisional entre scientific identity, execution identity y operational state conforme a NADR-F18-01 §5.1-§5.3. Establecer el piso constitucional mínimo (baseline sellada + parámetros científicos congelados + representación estructural canónica) | NADR-F18-01 §5.1 R1, R2, R3, R5; §5.2 R6, R8; §5.3 R10 | High | — | DONE |
| **2.1.2** | Validar que la frontera provisional es compatible con DC-12 (guard diferencial, Subfase 18.5): las dimensiones relevantes para comparación quedan explícitamente fijadas y la cláusula de invalidación está documentada | NADR-F18-01 §5.4 R17, R18 | Medium | 2.1.1 | DONE |
| **2.1.3** | Documentar el contrato de frontera de identidad: dimensiones incluidas, dimensiones excluidas, versión, gobernanza de modificaciones | NADR-F18-01 §5.4 R16 | Medium | 2.1.1, 2.1.2 | DONE |

#### Notas de implementación — Task 2.1.1

> Completada 2026-10-05. Emitido `docs/architecture/adr/phase-18/decisions/
> F18_IDENTITY_BOUNDARY_CONTRACT.md` FROZEN v1.0.1 (DC-02-A). Frontera
> provisional definida en 3 dimensiones ortogonales + Workload Identity:
> (1) Scientific Identity (tolerancia cero): baseline_identity (manifest
> sellado), configuration_identity (matching_policy + cost_context +
> engine_configuration), profile_identity, result_identity — mapeados
> directamente a `build_identity_chain()`; piso constitucional mínimo
> satisfecho (R2). (2) Execution Identity: execution_id (identificador de
> resultado derivado, NO discriminador de modo), subject_identity,
> model_de_execution, telemetry_execution_id — explícitamente excluidos de
> scientific identity (R8). (3) Operational State: 8 componentes (timestamps,
> scheduling order, resource utilization, retry timing, cache hit/miss,
> provider latency, worker ID, queue timings) — nunca contaminan scientific
> identity (R10). (4) Workload Identity: parcialmente cubierta por
> profile_identity; GAP-0.3-03 documentado como limitación de DC-02-A,
> resolución en DC-02-B. Reglas de no-colapso explícitas por dimensión.
> 7 reglas de Task 2.1.1 verificadas en matriz §7 del contrato.

#### Notas de implementación — Task 2.1.2

> Completada 2026-10-05. Compatibilidad con DC-12 validada en contrato §4:
> (a) prerrequisitos de HITO_0.4 v1.3.0 verificados (E-0.4-001 hashing AST
> determinista, E-0.4-002 ensamblado por identidad/lineage, E-0.4-003 métricas
> NSS/Critical FN reproducibles, E-0.4-004 exit codes 0-4 en boundary);
> (b) propiedades end-to-end pendientes de M1 explícitamente declaradas
> (neutralidad científica, INV-ASSEMBLY-ORDER, INV-NO-RESOURCE-SIGNAL parcial);
> (c) cláusula de invalidación (R17) con 3 condiciones concretas: M1 revela
> dimensión operational afectando scientific equality; técnica de DC-06b
> introduce variación científica no anticipada; INV-SCI-1 no se cumple bajo
> clasificación provisional — más proceso de escalación al Architecture Board
> con hallazgo P0 y suspensión de DC-12 hasta recalibración;
> (d) estabilidad durante comparación (R18) garantizada por restricciones de
> modificación (§5.4 del contrato). Contrato de comparación (§3) define
> scientific equality bit-exact, operational evidence no comparada, y subset
> canónico de verificación/lineage (exit codes, coverage, corpus_verdict,
> corpus_nss).

#### Notas de implementación — Task 2.1.3

> Completada 2026-10-05. Contrato documentado, versionado y gobernado (R16):
> dimensiones incluidas (§2.1-§2.4) y excluidas (§3.2) explícitas; versión
> FROZEN v1.0.1 con changelog (v1.0.0 emisión inicial, v1.0.1 correcciones
> C1-C6); gobernanza de modificaciones (§5) con autoridad por nivel
> (Scientific Identity y Workload Identity: Architecture Board; Execution
> Identity: Board/Staff Engineering; Operational State: Staff Engineering),
> proceso de 5 pasos (propuesta con evidencia → evaluación de impacto →
> aprobación → emisión → recalibración de DC-12 si aplica), versionado
> incremental y 4 restricciones duras. Documento ubicado en `decisions/`
> (artefacto de decisión, no plan operativo). Matriz de verificación
> regla-por-regla de las 10 reglas de Wave 2.1 en §7 del contrato.
> Nota de colisión de numeración DF-09 (F18 vs F17-BIS) documentada en §10.

#### Notas de referencia cruzada (§1.4)

> DC-02 se resuelve mediante una descomposición operativa interna (definición provisional → DC-12 → consolidación definitiva). Esta descomposición NO crea nuevos Decision Candidates ni nuevos niveles de autoridad, conforme a ADR_F18.1 §3. La Task 2.1.1 implementa la definición provisional; la consolidación definitiva se realizará en Subfase 18.5 post-DC-12.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-13 | `model_de_execution` (modo de ejecución) NO está incluido en `identity_chain` de `build_identity_chain()`. El testing diferencial (DC-12) no puede distinguir modos de ejecución por execution_id alone, porque execution_id es un hash determinista derivado de scientific identity + result, no un discriminador de modo. INV-EXEC-IDENTIFIABILITY parcialmente satisfecha: el modo es identificable en configuración del sistema pero no presente en el identity_chain del reporte de verificación. | Findings Register — REVIEW_REQUIRED; evaluación de extensión de `build_identity_chain` en Gate 3 (Task 3.4.2) |

#### Nota de numeración (Wave 2.1)

> DF-09 de Fase 18 (resultado contraintuitivo del benchmark de
> SyncProviderBridge) **NO es el mismo hallazgo** que DF-09 de Fase 17-BIS
> (enforcement CV diferido, ACCEPTED_LIMITATION). La numeración se reinicia
> por fase; los IDs de fases anteriores trasladados permanecen ocupados y no
> se reutilizan. DF-09 de F18 fue asignado antes de verificar colisión con el
> histórico; la colisión se documenta en el contrato §10 y en el Findings
> Register para evitar ambigüedad en referencias cruzadas. El siguiente ID
> libre en F18 es DF-13 (DF-06, DF-10, DF-11, DF-12, DF-19, DF-24, DF-34
> ocupados por fases anteriores o por F18).

### 2B.2 Wave 2.2 — Concurrency Model Decision (DC-01)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Analizar la evidencia de Gate 1 (GAP-0.5-02, GAP-0.1-01) y evaluar los modelos candidatos (async single-process + executors, multi-process, híbrido) contra las 32 reglas de NADR-F18-02 | NADR-F18-02 §5.9 R30, R32 | High | Gate 1 COMPLETED | TODO |
| **2.2.2** | Documentar la decisión DC-01 con evidencia cuantitativa: modelo seleccionado, justificación contra reglas NADR, impacto en C1/C3/C6/C10, y criterios de validación | NADR-F18-02 §5.9 R30, R31 | High | 2.2.1 | TODO |

#### Notas de implementación — Task 2.2.1

> Pendiente de implementación.

#### Notas de implementación — Task 2.2.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2B.3 Wave 2.3 — Execution Context Structure (DC-05)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Evaluar la estructura de contextos de ejecución: unificado vs especializado. Ejecutar test de god-object: qué boundary protege cada contexto | NADR-F18-02 §5.6 R21 | Medium | 2.2.2 (DC-01 resuelto) | TODO |
| **2.3.2** | Documentar la decisión DC-05 con boundaries explícitos: estructura seleccionada, fronteras de cada contexto, justificación contra NADR-F18-02 §5.6 R20-R22 | NADR-F18-02 §5.6 R20, R22 | Medium | 2.3.1 | TODO |

#### Notas de implementación — Task 2.3.1

> Pendiente de implementación.

#### Notas de implementación — Task 2.3.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2B.4 Gate 2 Exit Criteria

- DC-02 (definición provisional) resuelto: frontera provisional de identidad definida, validada contra DC-12, documentada y versionada
- DC-01 resuelto: modelo de concurrencia seleccionado con evidencia cuantitativa
- DC-05 resuelto: estructura de contextos de ejecución definida con boundaries explícitos
- Todas las reglas de NADR-F18-01 §5.1-§5.4 y NADR-F18-02 §5.6, §5.9 referenciadas en este Gate en estado DONE

### 2B.5 Gate 2 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | DC-01 documentado con evidencia cuantitativa | ⏳ |
| 6 | DC-02 (definición provisional) documentado con cláusula de invalidación | ⏳ |
| 7 | DC-05 documentado con boundaries explícitos | ⏳ |
| 8 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 2C. GATE 3 — Implementation

**Objective:** Materializar las decisiones arquitectónicas de Gate 2. Implementar bounded execution, admission/backpressure mechanism, cancellation/shutdown mechanism, operational visibility, identity traceability y composition refactor (DF-06).
**Execution Mode:** Mixto (Waves 3.1-3.4 pueden tener paralelismo parcial; Wave 3.5 secuencial)
**Rollback Plan:** Cada Wave tiene rollback independiente. Si una implementación viola INV-SCI-1 (NADR-F18-01 §5.1 R4), se revierte inmediatamente y se registra como hallazgo crítico. El estado científico canónico no se modifica en ningún caso.
**Gate Status:** ⏳ PENDING

### 2C.1 Wave 3.1 — Bounded Execution & Concurrency Safety

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Implementar el mecanismo de bounded execution conforme al modelo seleccionado en DC-01: respeto al resource envelope, límites explícitos y configurables, outcome operacional identificable ante agotamiento | NADR-F18-02 §5.1 R1, R3, R4 | High | Gate 2 COMPLETED | TODO |
| **3.1.2** | Implementar los primitivos de coordinación concurrente: explícitos, verificables, sin data races, sin deadlocks/livelocks dentro del operational envelope | NADR-F18-02 §5.5 R16, R17, R19 | High | 3.1.1 | TODO |
| **3.1.3** | Implementar la estructura de contextos de ejecución conforme a DC-05: boundaries explícitos, sin god-object | NADR-F18-02 §5.6 R20, R21, R22 | Medium | 3.1.1 | TODO |

#### Notas de implementación — Task 3.1.1

> Pendiente de implementación.

#### Notas de implementación — Task 3.1.2

> Pendiente de implementación.

#### Notas de implementación — Task 3.1.3

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2C.2 Wave 3.2 — Admission & Backpressure Mechanism

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Implementar el mecanismo de admisión: determinación de aceptación de trabajo, sin retención de recursos para trabajo rechazado, distinguible de la política de admisión (18.3) | NADR-F18-02 §5.1 R2; §5.2 R5, R6, R7 | Medium | 3.1.1 | TODO |
| **3.2.2** | Implementar el mecanismo de backpressure: propagación de presión consumidores→productores, bounded buffering o mecanismo equivalente, distinguible de la política de backpressure (18.3) | NADR-F18-02 §5.3 R8, R9, R10 | Medium | 3.1.1 | TODO |

#### Notas de implementación — Task 3.2.1

> Pendiente de implementación.

#### Notas de implementación — Task 3.2.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2C.3 Wave 3.3 — Cancellation & Shutdown

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Implementar el mecanismo de cancelación cooperativa: cancelable, libera recursos, verificable (completada/cancelada/fallida), sin comprometer evidencia científica canónica | NADR-F18-02 §5.4 R11, R12, R13, R14 | High | 3.1.2 | TODO |
| **3.3.2** | Implementar el mecanismo de terminación ordenada (shutdown): cancela trabajo en vuelo antes de terminar. La semántica de recuperación de estado persistente tras shutdown corresponde a Subfase 18.2 y NO se implementa aquí | NADR-F18-02 §5.4 R15 | Medium | 3.3.1 | TODO |

#### Notas de implementación — Task 3.3.1

> Pendiente de implementación.

#### Notas de implementación — Task 3.3.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2C.4 Wave 3.4 — Operational Visibility & Identity Traceability

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.4.1** | Implementar la visibilidad operacional mínima: propiedad observable para distinguir estado de unidad de trabajo, registrada como evidencia operacional separada de la científica. Sin observabilidad profunda (F20) | NADR-F18-02 §5.7 R23, R24, R25, R26 | Medium | 3.1.1 | TODO |
| **3.4.2** | Implementar la trazabilidad de identidad: todo artefacto lleva identidad científica e identidad de ejecución distinguibles; la evidencia operacional es trazable a la ejecución que la produjo | NADR-F18-01 §5.2 R7, R9; §5.3 R13; §5.4 R14; §5.5 R19, R20 | Medium | 2.1.3 (frontera de identidad) | TODO |

#### Notas de implementación — Task 3.4.1

> Pendiente de implementación.

#### Notas de implementación — Task 3.4.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2C.5 Wave 3.5 — Composition Refactor (DF-06)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.5.1** | Evaluar los imports cruzados core→apps identificados en DF-06 (core/benchmark/runners/ hacia apps/llm_workers y apps/bootstrap). Determinar si la dependencia arquitectónica se confirma conforme a ENGINEERING_PRINCIPLES §II (frontera hexagonal) | ENGINEERING_PRINCIPLES §II (frontera hexagonal); DF-06 (evaluación, no regla NADR) | Low | — | TODO |
| **3.5.2** | Si DF-06 se confirma: eliminar los imports cruzados respetando la frontera hexagonal establecida por ENGINEERING_PRINCIPLES §II. Si no se confirma: documentar la evaluación y derivar la evidencia al Findings Register para su clasificación/cierre | ENGINEERING_PRINCIPLES §II (frontera hexagonal); DF-06 | Medium | 3.5.1 | TODO |

#### Notas de implementación — Task 3.5.1

> Pendiente de implementación.

#### Notas de implementación — Task 3.5.2

> Pendiente de implementación.

#### Notas de referencia cruzada (§1.4)

> DF-06 no genera un nuevo dominio normativo. La frontera hexagonal ya está establecida en ENGINEERING_PRINCIPLES §II. NADR-F18-02 §8 referencia esta autoridad sin redefinirla. La Task 3.5.1 evalúa la manifestación concreta; la Task 3.5.2 la resuelve si se confirma. La autoridad de clasificación y cierre de DF-06 corresponde al Findings Register, no a esta Task.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2C.6 Gate 3 Exit Criteria

- Bounded execution implementado y respetando resource envelope
- Admission mechanism implementado y distinguible de política (18.3)
- Backpressure mechanism implementado con bounded buffering
- Cancellation cooperativa implementada sin comprometer evidencia canónica
- Shutdown ordenado implementado (sin semántica de recovery de 18.2)
- Operational visibility mínima implementada como propiedad observable
- Identity traceability implementada (identidad científica + ejecución por artefacto)
- DF-06 evaluado y evidencia derivada al Findings Register
- Pyright: 0 errors, 0 warnings
- Tests: suite completa en verde

### 2C.7 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |
| 8 | Verificación de que la implementación no altera INV-SCI-1 | ⏳ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 2D. GATE 4 — Verification & Technique Evaluation

**Objective:** Verificar todas las propiedades de NADR-F18-01 y NADR-F18-02. Validar el comportamiento del execution plane bajo carga. Evaluar técnicas candidatas conforme a Charter §9 (DC-06b). Cerrar la Subfase 18.1.
**Execution Mode:** Secuencial (Wave 4.1 → 4.2 → 4.3)
**Rollback Plan:** Si la verificación revela violación de INV-SCI-1, se detiene la subfase y se escala al Architecture Board. No se procede con DC-06b hasta que la neutralidad científica esté verificada.
**Gate Status:** ⏳ PENDING

### 2D.1 Wave 4.1 — Static Verification

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Verificar estáticamente las propiedades estructurales y contractuales de NADR-F18-01 verificables mediante análisis estático: clasificación de identidad, frontera documentada y versionada, trazabilidad de identidad por artefacto | NADR-F18-01 §5.1 R1-R5; §5.2 R6-R9; §5.3 R10-R13; §5.4 R14-R18; §5.5 R19-R20 | Medium | Gate 3 COMPLETED | TODO |
| **4.1.2** | Verificar estáticamente las propiedades estructurales y contractuales de NADR-F18-02 verificables mediante análisis estático: bounded execution, admission/backpressure mechanism, cancellation, concurrency safety, execution context, operational visibility, scientific neutrality | NADR-F18-02 §5.1 R1-R4; §5.2 R5-R7; §5.3 R8-R10; §5.4 R11-R15; §5.5 R16-R19; §5.6 R20-R22; §5.7 R23-R26; §5.8 R27-R29 | Medium | Gate 3 COMPLETED | TODO |

#### Notas de implementación — Task 4.1.1

> Pendiente de implementación.

#### Notas de implementación — Task 4.1.2

> Pendiente de implementación.

#### Notas de referencia cruzada (§1.4)

> Las referencias a reglas en esta Wave se interpretan como **reglas cubiertas/verificadas**, no como segunda implementación. La implementación normativa permanece atribuida a las Tasks de Gate 3. Conforme a §1.4, el estado DONE de una regla puede alcanzarse mediante la combinación de su Task de implementación (Gate 3) y su Task de verificación (Gate 4).

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2D.2 Wave 4.2 — Dynamic Validation

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Validar bounded execution bajo carga, backpressure, cancellation, shutdown ordenado y concurrency safety dentro del operational envelope declarado | NADR-F18-02 §5.1 R1, R4; §5.3 R9; §5.4 R11, R13; §5.5 R18 | High | 4.1.2 | TODO |
| **4.2.2** | Validar la neutralidad científica del execution plane: mismo documento bajo distintos modos de ejecución produce evidencia científica canónica idéntica. Validar verification isolation (sin scheduler/concurrencia por defecto) | NADR-F18-01 §5.1 R4; §5.3 R11, R12; §5.4 R15; NADR-F18-02 §5.8 R27, R28, R29 | Critical | 4.2.1 | TODO |
| **4.2.3** | Validar la frontera mecanismo/política: el mecanismo de admisión y backpressure opera independientemente de la política de recursos (18.3). Validar que el shutdown no invade semántica de recovery (18.2) | NADR-F18-02 §5.2 R7; §5.3 R10; §5.4 R15 | Medium | 4.2.1 | TODO |

#### Notas de implementación — Task 4.2.1

> Pendiente de implementación.

#### Notas de implementación — Task 4.2.2

> Pendiente de implementación.

#### Notas de implementación — Task 4.2.3

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2D.3 Wave 4.3 — Technique Evaluation (DC-06b)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Evaluar las técnicas candidatas del ROADMAP (pure async, elisión de SyncProviderBridge, threads/process pools, object pools, zero-copy, lazy loading, batching adaptativo) contra el criterio preregistrado de Charter §9 y la evidencia de Gate 1 | NADR-F18-02 §5.9 R30, R32 | Medium | 4.2.2 | TODO |
| **4.3.2** | Documentar los resultados de evaluación de DC-06b para decisión del Architecture Board: técnicas que sobreviven, técnicas que caen, técnicas que requieren evidencia adicional. DC-06b es evaluación compartida con Subfases 18.2-18.4 | NADR-F18-02 §5.9 R32 | Medium | 4.3.1 | TODO |

#### Notas de implementación — Task 4.3.1

> Pendiente de implementación.

#### Notas de implementación — Task 4.3.2

> Pendiente de implementación.

#### Notas de referencia cruzada (§1.4)

> DC-06b es una decisión de Board compartida entre Subfases 18.1 a 18.4. La Subfase 18.1 aporta la evaluación de técnicas relacionadas con el modelo de concurrencia y la barrera síncrona. Las técnicas relacionadas con resource budgets (18.3), provider/cache (18.4) se evalúan en sus subfases respectivas. Este Execution Plan no resuelve DC-06b; documenta la evaluación para el Board.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2D.4 Gate 4 Exit Criteria

- Todas las propiedades de NADR-F18-01 (20 reglas) verificadas
- Todas las propiedades de NADR-F18-02 (32 reglas) verificadas
- Neutralidad científica validada: mismo documento, distinto modo de ejecución, misma evidencia canónica
- Verification isolation validada
- Frontera mecanismo/política validada (18.1/18.3)
- Frontera shutdown/recovery validada (18.1/18.2)
- DC-06b evaluado y documentado para decisión del Board
- Pyright: 0 errors, 0 warnings
- Tests: suite completa en verde
- Golden corpus: sin regresión científica

### 2D.5 Gate 4 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Golden corpus: sin regresión científica | ⏳ |
| 8 | Notas de implementación completas para todas las Tasks | ⏳ |
| 9 | DC-06b documentado para Board | ⏳ |
| 10 | INV-SCI-1 verificada bajo variación operacional | ⏳ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-10-05 | 2/2 | 6/6 | 4 (DF-07 RESOLVED, DF-08 CLOSED (NAR), GF-01 IMPLEMENTATION_REQUIRED, DF-09 REVIEW_REQUIRED) | Evidence & Measurement Baseline (evidence materialization). ✅ COMPLETED. Wave 1.1: telemetría por etapa integrada. Wave 1.2: benchmark SyncProviderBridge (resultado contraintuitivo; DF-09 derivado). Wave 1.3: baselines FROZEN (concurrencia + métricas por etapa; calibración 1/6 técnicas). Evidencia suficiente para Gate 2 (DC-01). |
| Gate 2 | — | 0/14 | 0/7 | 0 | Architectural Decisions |
| Gate 3 | — | 0/32 | 0/11 | 0 | Implementation |
| Gate 4 | — | 0/8 | 0/7 | 0 | Verification & Technique Evaluation |

> **Nota de referencias cruzadas:** El total de 56 filas en el Traceability Appendix incluye 4 referencias cruzadas legítimas conforme a §1.4 (NADR-F18-02 §5.6 R20-R22 en Gate 2/3, NADR-F18-02 §5.8 R27 en Gate 3/4). Las reglas únicas a trazar son 52 (20 NADR-F18-01 + 32 NADR-F18-02).

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Snapshot/retención operacional del estado actual del execution plane (configuración, DBs efímeras, logs) antes de cualquier modificación | Local | NADR-F18-01 §5.1 R4 | Snapshot documentado | TODO |
| **MIG-02** | Verificar que el golden corpus produce el mismo resultado científico antes y después de la migración del modelo de ejecución | Local | NADR-F18-01 §5.4 R15; NADR-F18-02 §5.8 R27 | Golden corpus comparison | TODO |
| **MIG-03** | Si MIG-02 falla: rollback inmediato al modelo de ejecución anterior. El estado científico canónico no se modifica en ningún caso | Local | NADR-F18-01 §5.1 R4 | Rollback ejecutado + evidencia | TODO |
| **MIG-04** | Verificar verification isolation post-migración: el verification subject se ejecuta sin scheduler ni concurrencia por defecto | Local | NADR-F18-02 §5.8 R29 | Test de verification isolation | TODO |
| **MIG-05** | Actualizar el baseline operacional post-migración conforme a HITO_0.7 v1.1.0 (wall, CPU, peak RSS) para comparación futura | Local | NADR-F18-02 §5.9 R31 | Baseline documentado | TODO |

---

## 5. GLOBAL DoD (Definition of Done)

La Subfase 18.1 se considera oficialmente completada cuando:

    {All 52 rules in NADR-F18-01 + NADR-F18-02} − {Rules with DONE status in §7} = ∅

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

**Excepción para reglas de naturaleza decisional o probatoria:** Para reglas cuya materialización sea normativa, decisional o probatoria y no constituya comportamiento implementable como código (ej. NADR-F18-02 §5.9 R31: producir evidencia cuantitativa para DC-01), el Implementation Evidence puede ser el artefacto de evidencia/decisión correspondiente (documento de medición, registro de decisión, baseline documentado), en lugar de un commit de código.

**Condiciones adicionales de cierre:**
- DC-01 RESOLVED con evidencia cuantitativa
- DC-02 (definición provisional) RESOLVED (frontera provisional de identidad)
- DC-05 RESOLVED (estructura de contextos)
- DC-06b evaluado y documentado para Board
- DF-06 evaluado y evidencia derivada al Findings Register
- GAP-0.5-02 y GAP-0.1-01 resueltos
- Golden corpus: sin regresión científica
- Pyright: 0 errors, 0 warnings
- Tests: suite completa en verde

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 6 | 2 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 3 | 10 | 0 | 4 | 🟡 IN PROGRESS |
| Gate 3 | 0 | 0 | 0 | 32 | ⏳ PENDING |
| Gate 4 | 0 | 0 | 0 | 8 | ⏳ PENDING |
| **TOTAL** | **9** | **12** | **0** | **44 (40 únicas + 4 referencias cruzadas)** | 🟡 IN PROGRESS |

**Regla de actualización:** Cada vez que una Task pase a DONE:
1. Se actualiza el Status de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task (§2.{X}.{Y})
3. Se actualiza el Derived Status de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.{Z})

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Convención de estado DONE:** El estado DONE de una regla puede alcanzarse mediante la combinación de su Task de implementación (Gate 3) y su Task de verificación/validación (Gate 4). No se requiere que todas las reglas reaparezcan en cada Gate; las referencias adicionales en Gate 4 demuestran cobertura de verificación, no segunda implementación.

**Formato:** Rule | Derived Status | Evidence | Implementation Notes

### 7.1 Gate 1 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-02 §5.9 R31 | DONE | Wave 1.1 / Task 1.1.1, 1.1.2 ✅; Wave 1.2 / Task 1.2.1, 1.2.2 ✅; Wave 1.3 / Task 1.3.1, 1.3.2 ✅ | Evidencia cuantitativa para DC-01 (evidence materialization). 3 Waves completadas: telemetría por etapa (Wave 1.1), benchmark SyncProviderBridge con resultado contraintuitivo (Wave 1.2, DF-09), baselines FROZEN de concurrencia y métricas por etapa (Wave 1.3). Evidencia suficiente para Gate 2 (Wave 2.2) evaluar DC-01 contra las 32 reglas de NADR-F18-02. |
| NADR-F18-02 §5.9 R32 | DONE | Wave 1.2 / Task 1.2.2 ✅; Wave 1.3 / Task 1.3.1, 1.3.2 ✅ | No prescripción de modelo. Los baselines documentan el estado actual sin prescribir modelo de concurrencia. DC-01 se resuelve en Gate 2 (Wave 2.2) conforme a §5.9 R30. |

### 7.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-01 §5.1 R1 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Composición de scientific identity: 4 componentes mapeados a build_identity_chain() (contrato §2.1) |
| NADR-F18-01 §5.1 R2 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Piso constitucional mínimo: baseline sellada + params congelados + representación estructural (contrato §2.1, §3.1) |
| NADR-F18-01 §5.1 R3 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Exclusión de propiedades de ejecución: mecanismo/scheduling/concurrencia/resources clasificados en Execution Identity u Operational State (contrato §2.2, §2.3) |
| NADR-F18-01 §5.1 R5 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Variación requiere re-baseline: gobernanza de modificaciones exige nueva versión del contrato (contrato §5.2, §5.3) |
| NADR-F18-01 §5.2 R6 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Clasificación execution identity: execution_id, subject_identity, model_de_execution, telemetry_execution_id (contrato §2.2) |
| NADR-F18-01 §5.2 R8 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Exclusión de scientific identity: regla de no-colapso explícita (contrato §2.1, §2.2) |
| NADR-F18-01 §5.3 R10 | DONE | Wave 2.1 / Task 2.1.1 ✅ | Clasificación operational state: 8 componentes que pueden diferir libremente (contrato §2.3) |
| NADR-F18-01 §5.4 R16 | DONE | Wave 2.1 / Task 2.1.3 ✅ | Frontera documentada, versionada y gobernada: contrato FROZEN v1.0.1 + §5 Gobernanza de Modificaciones |
| NADR-F18-01 §5.4 R17 | DONE | Wave 2.1 / Task 2.1.2 ✅ | Cláusula de invalidación DC-12: 3 condiciones concretas + proceso de escalación al Board (contrato §4.3) |
| NADR-F18-01 §5.4 R18 | DONE | Wave 2.1 / Task 2.1.2 ✅ | Estabilidad durante comparación: restricciones de modificación + FROZEN hasta DC-02-B (contrato §4.3, §5.4) |
| NADR-F18-02 §5.6 R20 | PENDING | Wave 2.3 / Task 2.3.2 | Context boundaries explícitos |
| NADR-F18-02 §5.6 R21 | PENDING | Wave 2.3 / Task 2.3.1 | No god-object |
| NADR-F18-02 §5.6 R22 | PENDING | Wave 2.3 / Task 2.3.2 | Condicionado a DC-01/DC-05 |
| NADR-F18-02 §5.9 R30 | PENDING | Wave 2.2 / Task 2.2.1, 2.2.2 | DC-01 con evidencia |

### 7.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-02 §5.1 R1 | PENDING | Wave 3.1 / Task 3.1.1 | Resource envelope |
| NADR-F18-02 §5.1 R2 | PENDING | Wave 3.2 / Task 3.2.1 | Admission grant |
| NADR-F18-02 §5.1 R3 | PENDING | Wave 3.1 / Task 3.1.1 | Límites explícitos |
| NADR-F18-02 §5.1 R4 | PENDING | Wave 3.1 / Task 3.1.1 | Outcome operacional |
| NADR-F18-02 §5.2 R5 | PENDING | Wave 3.2 / Task 3.2.1 | Admission mechanism |
| NADR-F18-02 §5.2 R6 | PENDING | Wave 3.2 / Task 3.2.1 | No retención recursos rechazados |
| NADR-F18-02 §5.2 R7 | PENDING | Wave 3.2 / Task 3.2.1 | Mecanismo/política separados |
| NADR-F18-02 §5.3 R8 | PENDING | Wave 3.2 / Task 3.2.2 | Backpressure mechanism |
| NADR-F18-02 §5.3 R9 | PENDING | Wave 3.2 / Task 3.2.2 | Bounded buffering |
| NADR-F18-02 §5.3 R10 | PENDING | Wave 3.2 / Task 3.2.2 | Mecanismo/política separados |
| NADR-F18-02 §5.4 R11 | PENDING | Wave 3.3 / Task 3.3.1 | Cancelación cooperativa |
| NADR-F18-02 §5.4 R12 | PENDING | Wave 3.3 / Task 3.3.1 | No evidencia canónica incompleta |
| NADR-F18-02 §5.4 R13 | PENDING | Wave 3.3 / Task 3.3.1 | Liberación de recursos |
| NADR-F18-02 §5.4 R14 | PENDING | Wave 3.3 / Task 3.3.1 | Cancelación verificable |
| NADR-F18-02 §5.4 R15 | PENDING | Wave 3.3 / Task 3.3.2 | Shutdown ordenado |
| NADR-F18-02 §5.5 R16 | PENDING | Wave 3.1 / Task 3.1.2 | No data races |
| NADR-F18-02 §5.5 R17 | PENDING | Wave 3.1 / Task 3.1.2 | Primitivos explícitos |
| NADR-F18-02 §5.5 R19 | PENDING | Wave 3.1 / Task 3.1.2 | Superficie identificable |
| NADR-F18-02 §5.6 R20 | PENDING | Wave 3.1 / Task 3.1.3 | Context boundaries |
| NADR-F18-02 §5.6 R21 | PENDING | Wave 3.1 / Task 3.1.3 | No god-object |
| NADR-F18-02 §5.6 R22 | PENDING | Wave 3.1 / Task 3.1.3 | Estructura DC-05 |
| NADR-F18-02 §5.7 R23 | PENDING | Wave 3.4 / Task 3.4.1 | Visibility mínima |
| NADR-F18-02 §5.7 R24 | PENDING | Wave 3.4 / Task 3.4.1 | Propiedad observable |
| NADR-F18-02 §5.7 R25 | PENDING | Wave 3.4 / Task 3.4.1 | Evidencia operacional separada |
| NADR-F18-02 §5.7 R26 | PENDING | Wave 3.4 / Task 3.4.1 | No observabilidad profunda |
| NADR-F18-01 §5.2 R7 | PENDING | Wave 3.4 / Task 3.4.2 | Execution identity identificable |
| NADR-F18-01 §5.2 R9 | PENDING | Wave 3.4 / Task 3.4.2 | Execution identity registrable |
| NADR-F18-01 §5.3 R13 | PENDING | Wave 3.4 / Task 3.4.2 | Operational state registrable |
| NADR-F18-01 §5.4 R14 | PENDING | Wave 3.4 / Task 3.4.2 | Ejecución unívocamente identificable |
| NADR-F18-01 §5.5 R19 | PENDING | Wave 3.4 / Task 3.4.2 | Artefacto con ambas identidades |
| NADR-F18-01 §5.5 R20 | PENDING | Wave 3.4 / Task 3.4.2 | Evidencia operacional trazable |
| ENGINEERING_PRINCIPLES §II | PENDING | Wave 3.5 / Task 3.5.1, 3.5.2 | Frontera hexagonal (DF-06, evaluación; no es regla NADR) |

### 7.4 Gate 4 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-01 §5.1 R4 | PENDING | Wave 4.2 / Task 4.2.2 | No alteración por ejecución (verificación) |
| NADR-F18-01 §5.3 R11 | PENDING | Wave 4.2 / Task 4.2.2 | Operational state no altera identity (verificación) |
| NADR-F18-01 §5.3 R12 | PENDING | Wave 4.2 / Task 4.2.2 | No falsificación de evidencia (verificación) |
| NADR-F18-01 §5.4 R15 | PENDING | Wave 4.2 / Task 4.2.2 | Misma identity → misma evidencia (verificación) |
| NADR-F18-02 §5.5 R18 | PENDING | Wave 4.2 / Task 4.2.1 | No deadlocks/livelocks (verificación) |
| NADR-F18-02 §5.8 R27 | PENDING | Wave 4.2 / Task 4.2.2 | No alteración identidad científica (verificación) |
| NADR-F18-02 §5.8 R28 | PENDING | Wave 4.2 / Task 4.2.2 | Evidencia operacional separada (verificación) |
| NADR-F18-02 §5.8 R29 | PENDING | Wave 4.2 / Task 4.2.2 | Verification isolation (verificación) |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

    docs/architecture/adr/phase-18/reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.2.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (implementable / diferido / NAR / limitación)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0.

* **ADR_F18_MASTER** define la visión y capacidades de Fase 18 (el QUÉ y el POR QUÉ a nivel de fase).
* **ADR_F18.1** define la visión de la Subfase 18.1 (el QUÉ y el POR QUÉ a nivel de subfase).
* **NADR-F18-01 y NADR-F18-02** definen las reglas constitucionales permanentes (el QUÉ debe ser verdadero).
* **Este Execution Plan** define la secuencia operativa, tareas concretas y seguimiento de cumplimiento (el CÓMO y el CUÁNDO).
* **El Deferred Findings Register** registra los hallazgos identificados durante la implementación, su clasificación y resolución.

Este documento **no prescribe implementaciones específicas ni criterios de revisión de código.** No redefine reglas NADR. No registra hallazgos (se derivan al Findings Register).

Toda implementación que pretenda materializar las reglas de NADR-F18-01 y NADR-F18-02 deberá demostrar trazabilidad explícita hacia este Execution Plan mediante el Traceability Appendix (§7).

---

## 10. FUTURE WORK

- Automatización del Traceability Appendix (§7): generar el audit board automáticamente a partir del estado de las Tasks.
- Integración con CI: verificar propiedades NADR automáticamente en cada PR que toque el execution plane.
- Extensión del protocolo de medición a Subfases 18.2-18.5 conforme se emitan sus Execution Plans.
- Evaluación de DC-06b en Subfases 18.2-18.4 para técnicas no relacionadas con concurrencia.

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task

1. Actualizar el Status de la Task a IN_PROGRESS en la tabla de Wave (§2)
2. Actualizar el Gate Status a 🟡 IN PROGRESS si era ⏳ PENDING

### 11.2 Al completar una Task

1. Actualizar el Status de la Task a DONE en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task (§2.{X}.{Y})
3. Actualizar el Derived Status de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§2.{X}.{Z})
2. Asignar ID único (DF-{XX} o GF-{XX})
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el Status a BLOCKED

### 11.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§2.{Z})
2. Actualizar el Gate Status a ✅ COMPLETED
3. Registrar en el Gate Completion Log (§3)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 11.5 Al cancelar una operación de Deployment

1. Actualizar el Status a ELIMINADO en la tabla de Deployment (§4)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§11.3)

### 11.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como ELIMINADO con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento
- ❌ No resolver DC-01 sin evidencia cuantitativa de Gate 1
- ❌ No implementar técnicas candidatas sin evidencia conforme a Charter §9

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación de la Subfase 18.1. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN (NADR-F18-01 + NADR-F18-02 = 52 reglas), no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.