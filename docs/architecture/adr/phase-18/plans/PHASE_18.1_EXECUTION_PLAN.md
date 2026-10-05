# PHASE 18.1 EXECUTION PLAN v1.0.1
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.1
**Status:** IN_PROGRESS
**Date:** 2026-10-04
**Aprobación Architecture Board:** — (pendiente)
**Supersedes:** v1.0.0
**Derived From:** 2 NADRs FROZEN (NADR-F18-01 v1.0.3, NADR-F18-02 v1.0.1) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Subfase 18.1 (Execution Plane & Concurrency). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial. 4 Gates, 14 Waves, 32 Tasks. Mapeo completo de 52 reglas. |
| 1.0.1 | 2026-10-04 | Corrección de consistencia (11 cambios): (1) Conteo corregido a 31 Tasks. (2) Gate 3 corregido a 11 Tasks. (3) DF-06 desvinculado de NADR-F18-02 §5.8 R27; autoridad correcta es ENGINEERING_PRINCIPLES §II. (4) Task 3.5.2: cierre de DF-06 derivado al Findings Register, no resuelto por la Task. (5) Semántica de "Rules Implemented" aclarada para Tasks de verificación. (6) §7: DONE alcanzable por combinación implementación+verificación. (7) Gate 4.1: "propiedades estructurales y contractuales verificables mediante análisis estático". (8) DC-02-A reformulado como DC-02 (descomposición operativa: definición provisional). (9) Global DoD: evidencia decisional/probatoria permitida para reglas no implementables como código. (10) MIG-01: "backup" sustituido por "snapshot/retención operacional". (11) Gate 1 explicitado como evidence materialization. |

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
**Gate Status:** ⏳ PENDING

### 2.1 Wave 1.1 — Telemetry Integration (GAP-0.5-02)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Integrar la infraestructura de telemetría existente (SQLiteTelemetryGateway, ProductionTelemetryEvent) en el entry point de medición (run_regression.py) para capturar métricas por etapa del pipeline | NADR-F18-02 §5.9 R31 | Medium | — | TODO |
| **1.1.2** | Validar que el pipeline de recolección de telemetría produce datos completos y consistentes por etapa (extraction, normalización, segmentación, chunking, traducción, validación, ensamblado, TED, hashing, serialización, SQLite) | NADR-F18-02 §5.9 R31 | Low | 1.1.1 | TODO |

#### Notas de implementación — Task 1.1.1

> Pendiente de implementación.

#### Notas de implementación — Task 1.1.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.2 Wave 1.2 — SyncProviderBridge Impact Measurement (GAP-0.1-01)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Diseñar y ejecutar el protocolo de medición del impacto cuantitativo de la barrera síncrona (SyncProviderBridge) sobre bounded execution (C1) y backpressure (C3) bajo carga, conforme al criterio preregistrado de Charter §9 | NADR-F18-02 §5.9 R31 | Medium | 1.1.2 | TODO |
| **1.2.2** | Documentar los resultados cuantitativos de la medición: latencia p95 por etapa I/O, impacto en concurrencia efectiva, comportamiento de backpressure bajo carga | NADR-F18-02 §5.9 R31, R32 | Low | 1.2.1 | TODO |

#### Notas de implementación — Task 1.2.1

> Pendiente de implementación.

#### Notas de implementación — Task 1.2.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.3 Wave 1.3 — Baseline Documentation

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Documentar el baseline de concurrencia actual: modelo híbrido dual, 3 threads independientes, barrera síncrona, backoff exponencial, shutdown con bounded join | NADR-F18-02 §5.9 R31 | Low | 1.2.2 | TODO |
| **1.3.2** | Documentar el baseline de métricas por etapa del pipeline conforme a HITO_0.7 v1.1.0 (wall, CPU, peak RSS, allocations, I/O wait) | NADR-F18-02 §5.9 R31 | Low | 1.1.2 | TODO |

#### Notas de implementación — Task 1.3.1

> Pendiente de implementación.

#### Notas de implementación — Task 1.3.2

> Pendiente de implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.4 Gate 1 Exit Criteria

Todas las reglas de NADR-F18-02 §5.9 R31 referenciadas en este Gate deben alcanzar estado DONE. Específicamente:

- GAP-0.5-02 resuelto: telemetría integrada en el entry point de medición con datos por etapa
- GAP-0.1-01 resuelto: impacto cuantitativo de SyncProviderBridge medido y documentado
- Baseline de concurrencia actual documentado
- Baseline de métricas por etapa documentado
- Evidencia suficiente para evaluar DC-01 conforme a NADR-F18-02 §5.9 R31

### 2.5 Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

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

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 2B. GATE 2 — Architectural Decisions

**Objective:** Resolver DC-01 (modelo de concurrencia), DC-02 (descomposición operativa: definición provisional de frontera de identidad) y DC-05 (estructura de contextos de ejecución). DC-02 (definición provisional) puede avanzar en paralelo con Gate 1 al no existir dependencia (ADR_F18.1 §3). DC-01 requiere Gate 1 completado. DC-05 requiere DC-01 resuelto.
**Execution Mode:** Mixto (Wave 2.1 en paralelo con Gate 1; Wave 2.2 secuencial post-Gate 1; Wave 2.3 secuencial post-Wave 2.2)
**Rollback Plan:** Si DC-01 revela que ningún modelo candidato satisface las reglas de NADR-F18-02, se escala al Architecture Board para reevaluación del criterio preregistrado. No se fuerza una decisión sin evidencia.
**Gate Status:** ⏳ PENDING

### 2B.1 Wave 2.1 — Identity Boundary Definition (DC-02, descomposición operativa: definición provisional) [PARALELO con Gate 1]

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Definir la frontera provisional entre scientific identity, execution identity y operational state conforme a NADR-F18-01 §5.1-§5.3. Establecer el piso constitucional mínimo (baseline sellada + parámetros científicos congelados + representación estructural canónica) | NADR-F18-01 §5.1 R1, R2, R3, R5; §5.2 R6, R8; §5.3 R10 | High | — | TODO |
| **2.1.2** | Validar que la frontera provisional es compatible con DC-12 (guard diferencial, Subfase 18.5): las dimensiones relevantes para comparación quedan explícitamente fijadas y la cláusula de invalidación está documentada | NADR-F18-01 §5.4 R17, R18 | Medium | 2.1.1 | TODO |
| **2.1.3** | Documentar el contrato de frontera de identidad: dimensiones incluidas, dimensiones excluidas, versión, gobernanza de modificaciones | NADR-F18-01 §5.4 R16 | Medium | 2.1.1, 2.1.2 | TODO |

#### Notas de implementación — Task 2.1.1

> Pendiente de implementación.

#### Notas de implementación — Task 2.1.2

> Pendiente de implementación.

#### Notas de implementación — Task 2.1.3

> Pendiente de implementación.

#### Notas de referencia cruzada (§1.4)

> DC-02 se resuelve mediante una descomposición operativa interna (definición provisional → DC-12 → consolidación definitiva). Esta descomposición NO crea nuevos Decision Candidates ni nuevos niveles de autoridad, conforme a ADR_F18.1 §3. La Task 2.1.1 implementa la definición provisional; la consolidación definitiva se realizará en Subfase 18.5 post-DC-12.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

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
| Gate 1 | — | 0/2 | 0/6 | 0 | Evidence & Measurement Baseline (evidence materialization) |
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
| Gate 1 | 0 | 0 | 0 | 2 | ⏳ PENDING |
| Gate 2 | 0 | 0 | 0 | 14 | ⏳ PENDING |
| Gate 3 | 0 | 0 | 0 | 32 | ⏳ PENDING |
| Gate 4 | 0 | 0 | 0 | 8 | ⏳ PENDING |
| **TOTAL** | **0** | **0** | **0** | **56 (52 únicas + 4 referencias cruzadas)** | ⏳ PENDING |

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
| NADR-F18-02 §5.9 R31 | PENDING | Wave 1.1 / Task 1.1.1, 1.1.2; Wave 1.2 / Task 1.2.1, 1.2.2; Wave 1.3 / Task 1.3.1, 1.3.2 | Evidencia cuantitativa para DC-01 (evidence materialization) |
| NADR-F18-02 §5.9 R32 | PENDING | Wave 1.2 / Task 1.2.2 | No prescripción de modelo |

### 7.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-01 §5.1 R1 | PENDING | Wave 2.1 / Task 2.1.1 | Composición de scientific identity |
| NADR-F18-01 §5.1 R2 | PENDING | Wave 2.1 / Task 2.1.1 | Piso constitucional mínimo |
| NADR-F18-01 §5.1 R3 | PENDING | Wave 2.1 / Task 2.1.1 | Exclusión de propiedades de ejecución |
| NADR-F18-01 §5.1 R5 | PENDING | Wave 2.1 / Task 2.1.1 | Variación requiere re-baseline |
| NADR-F18-01 §5.2 R6 | PENDING | Wave 2.1 / Task 2.1.1 | Clasificación execution identity |
| NADR-F18-01 §5.2 R8 | PENDING | Wave 2.1 / Task 2.1.1 | Exclusión de scientific identity |
| NADR-F18-01 §5.3 R10 | PENDING | Wave 2.1 / Task 2.1.1 | Clasificación operational state |
| NADR-F18-01 §5.4 R16 | PENDING | Wave 2.1 / Task 2.1.3 | Frontera documentada y versionada |
| NADR-F18-01 §5.4 R17 | PENDING | Wave 2.1 / Task 2.1.2 | Cláusula de invalidación DC-12 |
| NADR-F18-01 §5.4 R18 | PENDING | Wave 2.1 / Task 2.1.2 | Estabilidad durante comparación |
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