# FASE_18_DEFERRED_FINDINGS_REGISTER.md

**Documento:** docs/architecture/adr/phase-18/reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md
**Versión:** 1.0.3
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-10-04
**Última actualización:** 2026-10-05
**Derivado de:** PHASE_18.1_EXECUTION_PLAN.md v1.0.3
**Ámbito:** Subfase 18.1 — Execution Plane & Concurrency
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de la Subfase 18.1, su clasificación, resolución y evidencia
empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

    ADR_F18_MASTER > ADR_F18.1 > NADR-F18-01, NADR-F18-02 > PHASE_18.1_EXECUTION_PLAN

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que el execution plane local
> opere de forma concurrente, acotada por recursos, cancelable y
> científicamente neutra, respetando la frontera entre scientific
> identity, execution identity y operational state establecida por
> NADR-F18-01 y las reglas de bounded execution establecidas por
> NADR-F18-02?"*

### 0.3 Reglas transversales aplicables

- **NADR-F18-01 §5.1 R4:** Ninguna modificación del mecanismo de ejecución debe alterar la scientific identity ni la evidencia científica canónica.
- **NADR-F18-01 §5.3 R12:** Las diferencias en operational state no deben falsificar la evidencia científica ni ser interpretadas como regresión científica.
- **NADR-F18-02 §5.1 R1:** El execution plane debe respetar el resource envelope vigente asignado por la política de recursos.
- **NADR-F18-02 §5.4 R12:** La cancelación no debe comprometer o publicar evidencia científica incompleta como evidencia canónica.
- **NADR-F18-02 §5.8 R27:** El modelo de ejecución concurrente no debe alterar la identidad científica ni la evidencia científica canónica.
- **ENGINEERING_PRINCIPLES §II:** Arquitectura Hexagonal — separación estricta entre Dominio e Infraestructura. El dominio nunca depende de la infraestructura.
- **ENGINEERING_PRINCIPLES §III:** Explicit over Implicit — toda decisión arquitectónica debe ser explícita y trazable.
- **ENGINEERING_PRINCIPLES §IV:** Cero Fallos Silenciosos — todo fallo debe ser detectable, reportable y trazable.
- **ENGINEERING_PRINCIPLES §VII:** Reuse Before Invent — toda sustitución de autoridad existente exige evidencia de insuficiencia.
- **INV-SCI-1 (ADR_F18_MASTER §5.1):** Misma baseline sellada + mismos parámetros científicos congelados ⇒ misma salida científica, independiente de schedule, concurrencia, budgets y cache.
- **INV-OPS-1 (ADR_F18_MASTER §5.1):** Las diferencias operacionales no alteran el resultado científico ni falsifican la evidencia científica.
- **INV-VERIFICATION-ISOLATION (ADR_F18_MASTER §5.1):** El verification subject corre sin scheduler ni concurrencia por defecto.
- **INV-NO-RESOURCE-SIGNAL (ADR_F18_MASTER §5.1):** Agotamiento de budget ⇒ EXECUTION_FAILURE con evidencia persistida; nunca REGRESSION/PASS.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| DF-{XX} | Deferred Finding | Hallazgo técnico identificado durante implementación |
| GF-{XX} | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| H-{XX}-{X} | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| RESOLVED | Implementado y cerrado con evidencia |
| RESOLVED — DELETE | Código muerto eliminado |
| RESOLVED — MOVE | Código reubicado en capa correcta |
| RESOLVED — REFACTORED | Código refactorizado sin cambio funcional |
| RESOLVED — FACTORY EXTRACTION | Lógica extraída a factory canónica |
| CLOSED (NAR) | No Action Required — falso positivo o correcto por diseño |
| ACCEPTED_LIMITATION | Limitación conocida, documentada y aceptada |
| RECLASSIFIED_FUTURE_PHASE | Diferido a fase futura con justificación |
| IMPLEMENTATION_REQUIRED | Requiere implementación (scope por definir o acotado) |
| REVIEW_REQUIRED | Requiere análisis adicional antes de decidir |
| DEFERRED — FASE {X} | Diferido a fase específica con ADR pendiente |
| PENDING_REVIEW | Hallazgo registrado, pendiente de clasificación en Gate Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos/documentos auditados.
- Cada finding **DEBE** distinguir: (a) gap confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún finding se cierra sin evidencia de código o documental.
- No se implementa código durante el Exit Review. La implementación se agrupa en batches posteriores.

### 1.4 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado PENDING_REVIEW |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Fase cerrada | Estado del documento → ARCHIVED |

### 1.5 Relación con el Execution Plan

Este registro recibe hallazgos derivados de las siguientes fuentes del PHASE_18.1_EXECUTION_PLAN v1.0.3:

| Fuente en Execution Plan | Sección | Tipo de hallazgo esperado |
|---|---|---|
| Wave 1.1 — Telemetry Integration | §2.1 | Hallazgos de instrumentación |
| Wave 1.2 — SyncProviderBridge Measurement | §2.2 | Hallazgos de medición |
| Wave 1.3 — Baseline Documentation | §2.3 | Hallazgos de documentación |
| Wave 2.1 — Identity Boundary Definition | §2B.1 | Hallazgos de frontera de identidad |
| Wave 2.2 — Concurrency Model Decision | §2B.2 | Hallazgos de DC-01 |
| Wave 2.3 — Execution Context Structure | §2B.3 | Hallazgos de DC-05 |
| Wave 3.1 — Bounded Execution & Concurrency Safety | §2C.1 | Hallazgos de implementación |
| Wave 3.2 — Admission & Backpressure Mechanism | §2C.2 | Hallazgos de implementación |
| Wave 3.3 — Cancellation & Shutdown | §2C.3 | Hallazgos de implementación |
| Wave 3.4 — Operational Visibility & Identity Traceability | §2C.4 | Hallazgos de implementación |
| Wave 3.5 — Composition Refactor (DF-06) | §2C.5 | Hallazgos de frontera hexagonal |
| Wave 4.1 — Static Verification | §2D.1 | Hallazgos de verificación |
| Wave 4.2 — Dynamic Validation | §2D.2 | Hallazgos de validación |
| Wave 4.3 — Technique Evaluation (DC-06b) | §2D.3 | Hallazgos de evaluación |

---

## 2. GATE EXIT REVIEWS

{Estructura abierta. Se agregará una sub-sección por cada Gate ejecutado. Ningún Gate ha sido ejecutado todavía.}

### 2.0 Hallazgos pre-registrados (previos a la implementación)

Los siguientes hallazgos fueron identificados durante la Fase 0 y/o el diseño del Execution Plan y se pre-registran aquí para su clasificación formal en el Gate Exit Review correspondiente.

| DF | Descripción | Origen | Estado | Gate esperado |
|----|-------------|--------|--------|---------------|
| DF-06 | Imports cruzados de core/benchmark/runners/ hacia apps/llm_workers y apps/bootstrap. Violan la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II. | HITO_0.2 v1.2.0 (E-0.2-005); ADR_F18.1 §4; PHASE_18.1_EXECUTION_PLAN §2C.5 | PENDING_REVIEW | Gate 3 |

**Nota sobre DF-06:** La autoridad normativa de la frontera hexagonal es ENGINEERING_PRINCIPLES §II, no NADR-F18-02. DF-06 es una manifestación concreta que debe ser evaluada. Si se confirma, la resolución implica eliminar los imports cruzados. Si no se confirma, la evidencia se deriva a este registro para clasificación/cierre como NAR. La Task 3.5.1 evalúa; la Task 3.5.2 implementa si se confirma. La clasificación y cierre formal corresponden a este registro.

### 2.1 Gate 1 Exit Review — COMPLETO (Waves 1.1, 1.2, 1.3 completadas, 2026-10-05)

**Árbol de decisión aplicado:**

    1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
    2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
    3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
    4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-07 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | RegressionTelemetryGateway creado en Task 1.1.1. Adaptador síncrono SQLite WAL con context manager. |
| DF-08 | ❌ No | N/A | N/A | CLOSED (NAR) | Falso positivo. Verificación forense (Select-String) confirmó que el código real tiene las variables definidas. El pegado estaba truncado por encoding de PowerShell. |
| GF-01 | ✅ Sí | ❌ No (en Gate 1) | ✅ Sí | IMPLEMENTATION_REQUIRED | NullTelemetryAdapter duplicado con APIs incompatibles. Consolidación diferida a Gate 3 (Wave 3.5). Warning agregado en adapters.py. |
| DF-09 | ✅ Sí | ❌ No (requiere reevaluación de DC-01) | ✅ Sí | REVIEW_REQUIRED | Resultado contraintuitivo del benchmark de SyncProviderBridge. La barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugiere. Requiere reevaluación de DC-01 en Gate 2 (Wave 2.2). |

**Resumen:**
- RESOLVED: 1 (DF-07)
- CLOSED (NAR): 1 (DF-08)
- IMPLEMENTATION_REQUIRED: 1 (GF-01)
- REVIEW_REQUIRED: 1 (DF-09)
- Nuevos hallazgos registrados: 4 (DF-07, DF-08, GF-01, DF-09)

**Nota de cierre de Gate 1 (Wave 1.3, 2026-10-05):** Wave 1.3 (Baseline Documentation) se completó sin identificar nuevos hallazgos. Los baselines FROZEN v1.0.0 (F18_BASELINE_CONCURRENCY.md y F18_BASELINE_METRICS_PER_STAGE.md) consolidan la evidencia de las Waves 1.1 y 1.2 sin revelar gaps adicionales a los ya registrados. GAP-0.7-01 permanece parcialmente resuelto (telemetría Wave 1.1 cubre el pipeline de regression); GAP-0.7-02 y GAP-0.7-05 permanecen DEFERRED conforme a HITO_0.7 §14. Gate 1 queda COMPLETED con 4 hallazgos derivados y evidencia suficiente para Gate 2 (DC-01).

#### Evidencia forense por hallazgo

**DF-07 — Ausencia de adaptador síncrono para TelemetryPort:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | Inspección forense Wave 1.1; PHASE_18.1_EXECUTION_PLAN §2.1 |
| **Estado** | `RESOLVED` |
| **Gate** | Gate 1 (Wave 1.1, Task 1.1.1) |
| **Descripción** | Solo existe SQLiteTelemetryGateway (asíncrono, ProductionTelemetryEvent). No existe implementación síncrona de TelemetryPort.record_execution(StageExecutionRecord). Prerrequisito técnico de Task 1.1.1. |
| **Archivos auditados** | core/telemetry/ports.py, core/telemetry/adapters.py, core/telemetry/gateway.py |
| **Gap confirmado** | (a) gap confirmado: no existe adaptador síncrono |
| **Resolución** | Creado core/telemetry/regression_gateway.py con RegressionTelemetryGateway(TelemetryPort). Pyright: 0 errors. Tests: 6/6 passed. |
| **Regla aplicada** | ENGINEERING_PRINCIPLES §VII (Reuse Before Invent): se reutiliza TelemetryPort existente, se crea adaptador síncrono porque no existe |

**DF-08 — Variables no definidas en pipeline_factory.py:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | Inspección forense Wave 1.1 (código pegado truncado) |
| **Estado** | `CLOSED (NAR)` |
| **Gate** | Gate 1 (Wave 1.1) |
| **Descripción** | Se reportó que `_adapter_mapper` en apps/bootstrap/pipeline_factory.py referencia `error_summary` y `draft` no definidos. Reportado como bug crítico de producción. |
| **Archivos auditados** | apps/bootstrap/pipeline_factory.py (líneas 200-215) |
| **Veredicto** | (c) no-gap: falso positivo por truncamiento de pegado PowerShell |
| **Evidencia de cierre** | Select-String confirmó: línea 210 tiene `draft = _layout_block_to_draft(block, page.page_number, reading_order)`; línea 202 tiene `error_summary = "; ".join(report.errors)`. El código real está correcto. |
| **Regla aplicada** | ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos): verificación forense antes de fixear. Un fix incorrecto podría introducir un fallo silencioso peor. |

**GF-01 — NullTelemetryAdapter duplicado con APIs incompatibles:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Governance Finding |
| **Origen** | Inspección forense Wave 1.1 |
| **Estado** | `IMPLEMENTATION_REQUIRED` |
| **Gate destino** | Gate 3 (Wave 3.5, junto con refactor de composición) |
| **Descripción** | Dos clases con el mismo nombre `NullTelemetryAdapter` coexisten: core/telemetry/ports.py:25 (implementa TelemetryPort correctamente) y core/telemetry/adapters.py:4 (expone record_metric/record_event, API incompatible con TelemetryPort). |
| **Archivos auditados** | core/telemetry/ports.py (líneas 19-27), core/telemetry/adapters.py (líneas 1-10) |
| **Gap confirmado** | (a) gap confirmado: conflicto de interfaces en el mismo módulo |
| **Impacto** | Confusión de contratos, riesgo de import incorrecto, viola ENGINEERING_PRINCIPLES §III (Explicit over Implicit) |
| **Acción inmediata** | Warning agregado en core/telemetry/adapters.py: "GF-01: Esta clase tiene API incompatible con TelemetryPort (core/telemetry/ports.py). La implementación canónica de NullTelemetryAdapter está en ports.py. Consolidación pendiente de resolución en Findings Register." |
| **Regla aplicada** | ENGINEERING_PRINCIPLES §III (Explicit over Implicit): la consolidación debe hacer explícita la implementación canónica |

**DF-09 — Resultado contraintuitivo del benchmark de SyncProviderBridge:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | Benchmark de SyncProviderBridge, Wave 1.2 (Task 1.2.1, 1.2.2); reports/benchmark/sync_bridge_benchmark.json |
| **Estado** | `REVIEW_REQUIRED` |
| **Gate** | Gate 1 (Wave 1.2) → Gate 2 (Wave 2.2, reevaluación de DC-01) |
| **Descripción** | El benchmark cuantitativo de SyncProviderBridge produce resultados contraintuitivos respecto a la hipótesis original de GAP-0.1-01 (HITO_0.1 E-0.1-001). La barrera síncrona existe como hecho estructural, pero su impacto en bounded execution (C1) y backpressure (C3) es pequeño o nulo: overhead p95 = 2-10ms, throughput ratio async/bridge = 1.00x (sin diferencia en N=1 a N=20), backpressure idéntico bajo burst, RSS delta = 0.02 MB (despreciable). La hipótesis original era una inferencia estática no verificada; la primera medición cuantitativa la corrige. |
| **Archivos auditados** | tools/evaluation/benchmark_sync_bridge.py, reports/benchmark/sync_bridge_benchmark.json, apps/llm_workers/sync_bridge.py, apps/llm_workers/__main__.py, apps/llm_workers/dispatcher.py |
| **Veredicto** | (b) hipótesis corregida: la hipótesis "la barrera síncrona es un cuello de botella significativo" NO se confirma. El overhead es pequeño (2-10ms p95) y el throughput es idéntico (ratio 1.00x). |
| **Evidencia cuantitativa** | Exp 1: overhead p95 = 2.05ms (latencia 0.1s), 9.28ms (0.5s), 10.40ms (1.0s). Exp 2: throughput ratio async/bridge = 1.00x en N=1,2,5,10,20. Exp 3: wall = 20.08s idéntico ambos paths, peak_threads=5, completed=50. Exp 4: RSS delta = 0.02 MB. |
| **Evaluación contra criterio preregistrado (Charter §9)** | Métrica: latencia p95 por etapa I/O → overhead 2-10ms (pequeño). Dirección esperada si se elide: ↓ → margen marginal (2-10ms). Condición sin ↑RSS: ✅ se cumple (0.02 MB). Throughput: sin mejora si se elide (ratio 1.00x). Veredicto: el criterio NO se cumple claramente; la elisión de SyncProviderBridge NO está justificada por la evidencia cuantitativa. |
| **Implicación para DC-01** | DC-01 (fork de concurrencia) requiere reevaluación en Gate 2 (Wave 2.2) con la nueva evidencia. La elisión de SyncProviderBridge no es una optimización prioritaria. Los modelos candidatos deben evaluarse contra las 32 reglas de NADR-F18-02, no contra la hipótesis de que la barrera es un cuello de botella. |
| **Limitaciones del benchmark** | (1) MockLLMProvider usa asyncio.sleep(), no I/O real de red. (2) No replica el daemon real (secuencial, heartbeat, backoff, SQLite). (3) Concurrencia N>1 no existe en producción (el daemon es secuencial). (4) MockPromptBuilder evita el costo real del PromptBuilder. Estas limitaciones podrían subestimar el impacto en producción, pero el resultado es claro para el escenario medido. |
| **Regla aplicada** | FASE0_AUDIT_CHARTER §9 (criterio preregistrado: la evidencia determina el resultado, no la intuición). ENGINEERING_PRINCIPLES §VII (Benchmark Before Optimization). ADR_F18_MASTER §5.2 (Audit First, Design Later). |

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| CLOSED (NAR) | 1 | DF-08 |
| RESOLVED — DELETE | 0 | — |
| RESOLVED | 1 | DF-07 |
| IMPLEMENTATION_REQUIRED | 1 | GF-01 |
| RECLASSIFIED_FUTURE_PHASE | 0 | — |
| REVIEW_REQUIRED | 1 | DF-09 |
| ACCEPTED_LIMITATION | 0 | — |
| PENDING_REVIEW | 1 | DF-06 |

### 3.2 Tabla consolidada

| DF/GF | Estado | Decisión |
|----|--------|----------|
| DF-06 | PENDING_REVIEW | Pendiente de evaluación en Gate 3 (Task 3.5.1) |
| DF-07 | RESOLVED | RegressionTelemetryGateway creado en Wave 1.1 (Task 1.1.1). Adaptador síncrono SQLite WAL con context manager. Pyright: 0 errors. Tests: 6/6 passed. |
| DF-08 | CLOSED (NAR) | Falso positivo. Verificación forense (Select-String) confirmó que pipeline_factory.py:210 tiene `draft = _layout_block_to_draft(block, page.page_number, reading_order)` y pipeline_factory.py:202 tiene `error_summary = "; ".join(report.errors)`. El código pegado estaba truncado por encoding de PowerShell. |
| GF-01 | IMPLEMENTATION_REQUIRED | Consolidar NullTelemetryAdapter en Gate 3 (Wave 3.5). Warning agregado en adapters.py. APIs incompatibles: ports.py implementa TelemetryPort; adapters.py expone record_metric/record_event. |
| DF-09 | REVIEW_REQUIRED | Resultado contraintuitivo del benchmark de SyncProviderBridge (Wave 1.2). La barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugiere: overhead p95 2-10ms, throughput ratio 1.00x, backpressure idéntico, RSS 0.02 MB. Requiere reevaluación de DC-01 en Gate 2 (Wave 2.2). La elisión de SyncProviderBridge NO está justificada por la evidencia cuantitativa conforme a Charter §9. |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Estructura abierta. Se agregará una sub-sección por cada batch ejecutado. Ningún batch ha sido ejecutado todavía.}

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 4 |
| Hallazgos resueltos | 1 |
| Hallazgos cerrados sin acción | 1 |
| Hallazgos reclasificados a fase futura | 0 |
| Hallazgos pendientes de implementación | 1 |
| Hallazgos pendientes de revisión | 2 |
| Batches completados | 0 |
| Archivos eliminados totales | 0 |
| Archivos movidos totales | 0 |
| Archivos creados totales | 5 |
| Tests finales | 6 passed, 0 skipped |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| — | — | — |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (ARCHIVED) cuando:
1. No hay hallazgos en estado IMPLEMENTATION_REQUIRED sin batch asignado
2. No hay hallazgos en estado REVIEW_REQUIRED sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos RECLASSIFIED_FUTURE_PHASE tienen destino explícito
5. Todos los Gates del PHASE_18.1_EXECUTION_PLAN v1.0.3 están COMPLETED
6. La Subfase 18.1 cumple el Global DoD definido en §5 del Execution Plan

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 4 |
| Hallazgos resueltos | 1 |
| Hallazgos pendientes de implementación | 1 |
| Hallazgos pendientes de revisión | 2 |
| Hallazgos cerrados sin acción | 1 |
| Batches completados | 0/0 |
| Estado del Exit Review | 🟡 IN PROGRESS |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit de la Subfase 18.1. No tiene
autoridad normativa. No redefine reglas de NADRs ni ADRs. Su único propósito
es documentar la evidencia empírica de los hallazgos identificados durante la
implementación del PHASE_18.1_EXECUTION_PLAN v1.0.3 y su resolución. La
autoridad de clasificación y cierre de hallazgos corresponde exclusivamente a
este documento, conforme a METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.3.