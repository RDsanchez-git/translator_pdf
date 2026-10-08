# FASE_18_DEFERRED_FINDINGS_REGISTER.md

**Documento:** docs/architecture/adr/phase-18/reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md
**Versión:** 1.0.7
**Estado:** COMPLETED
**Fecha de creación:** 2026-10-04
**Última actualización:** 2026-10-07
**Derivado de:** PHASE_18.1_EXECUTION_PLAN.md v1.0.7
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

Este registro recibe hallazgos derivados de las siguientes fuentes del PHASE_18.1_EXECUTION_PLAN v1.0.7:

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
| Wave 3.5 — Composition Refactor (DF-06 + GF-01) | §2C.5 | Hallazgos de frontera hexagonal (DF-06) y consolidación de código muerto (GF-01) |
| Wave 4.1 — Static Verification | §2D.1 | Hallazgos de verificación |
| Wave 4.2 — Dynamic Validation | §2D.2 | Hallazgos de validación |
| Wave 4.3 — Technique Evaluation (DC-06b) | §2D.3 | Hallazgos de evaluación |

### 1.6 Convención de numeración por fase

La numeración de DF/GF **se reinicia en cada fase**. No existe numeración global
entre fases. Los IDs de fases anteriores que se **trasladaron o migraron** a la
fase actual conservan su numeración original y permanecen **ocupados**: no se
reutilizan en la numeración corriente de la fase en ejecución.

**IDs ocupados en Fase 18 por traslado o colisión histórica:**

| ID | Origen | Estado en F18 |
|----|--------|---------------|
| DF-06 | Trasladado de Fase 0 / HITO_0.2 (E-0.2-005) | RESOLVED — MOVE en F18 (Gate 3, Task 3.5.2) |
| DF-10 | Ocupado por Fase 17-BIS (HARD_FAIL basal NSS) | No reutilizable en F18 |
| DF-11 | Ocupado por Fase 17-BIS (manifest corrupto → exit 3) | No reutilizable en F18 |
| DF-12 | Ocupado por Fase 17-BIS (LayoutBlockDraft legacy zombi) | No reutilizable en F18 |
| DF-19, DF-24, DF-34 | Ocupados por Fase 17-BIS / HITO_0.2 / HITO_0.8 | No reutilizables en F18 |

**Colisión documentada — DF-09:** DF-09 de Fase 18 (resultado contraintuitivo
del benchmark de SyncProviderBridge, REVIEW_REQUIRED) **NO es el mismo
hallazgo** que DF-09 de Fase 17-BIS (enforcement CV diferido,
ACCEPTED_LIMITATION, cláusula 6.1). DF-09 fue asignado en F18 antes de
verificar colisión con el histórico de Fase 17-BIS. Ambos hallazgos son
independientes y pertenecen a fases distintas. Esta colisión se documenta aquí
para evitar ambigüedad en referencias cruzadas inter-fase. El siguiente ID
libre en F18 tras DF-09 es **DF-13**.

**Regla operativa:** Al asignar un ID nuevo en F18, verificar contra la tabla de
IDs ocupados de esta sección. Si el ID candidato está ocupado por una fase
anterior, tomar el siguiente libre.

---

## 2. GATE EXIT REVIEWS

{Estructura abierta. Se agrega una sub-sección por cada Gate ejecutado. Gates completados: 1 (Wave 1.1-1.3), 2 (Wave 2.1-2.3), 3 (Wave 3.1-3.5), 4 (Wave 4.1-4.3). Todos los Gates de la Subfase 18.1 completados.}

### 2.0 Hallazgos pre-registrados (previos a la implementación)

Los siguientes hallazgos fueron identificados durante la Fase 0 y/o el diseño del Execution Plan y se pre-registran aquí para su clasificación formal en el Gate Exit Review correspondiente.

| DF | Descripción | Origen | Estado | Gate esperado |
|----|-------------|--------|--------|---------------|
| DF-06 | Imports cruzados de core/benchmark/runners/ hacia apps/llm_workers y apps/bootstrap. Violan la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II. | HITO_0.2 v1.2.0 (E-0.2-005); ADR_F18.1 §4; PHASE_18.1_EXECUTION_PLAN §2C.5 | **RESOLVED — MOVE** (Gate 3, Task 3.5.2) | Gate 3 |

**Nota sobre DF-06:** La autoridad normativa de la frontera hexagonal es ENGINEERING_PRINCIPLES §II, no NADR-F18-02. DF-06 fue evaluado en Task 3.5.1 (CONFIRMADO) e implementado en Task 3.5.2 (RESOLVED — MOVE: runners movidos a apps/benchmark/runners/). La clasificación y cierre formal quedan registrados en §2.3 y §3.2.

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

### 2.2 Gate 2 Exit Review — COMPLETO (Waves 2.1, 2.2, 2.3 completadas, 2026-10-05)

**Árbol de decisión aplicado:**

    1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
    2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
    3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
    4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-09 | ✅ Sí | ✅ Sí (DC-01 resuelto con esta evidencia) | ✅ Sí | **RESOLVED** | La reevaluación de DC-01 exigida por DF-09 se materializó en F18_DC01_DECISION.md v1.0.0. El benchmark demostró que la elisión de SyncProviderBridge no produce beneficio medible; DC-01 resuelto: mantener modelo híbrido. |
| DF-13 | ✅ Sí | ❌ No (requiere cambio de código en identity_chain) | ✅ Sí | REVIEW_REQUIRED | `model_de_execution` ausente de `build_identity_chain()`. Evaluación de extensión diferida a Gate 3 (Task 3.4.2, trazabilidad de identidad). |

**Resumen:**
- RESOLVED: 1 (DF-09, reclasificado desde REVIEW_REQUIRED)
- REVIEW_REQUIRED: 1 (DF-13)
- Nuevos hallazgos registrados: 0 (DC-01 y DC-05 son decisiones, no hallazgos)

**Decisiones de Gate 2 (no son hallazgos, se documentan para trazabilidad):**

| DC | Decisión | Evidencia | Documento |
|----|----------|-----------|-----------|
| DC-02-A | Contrato provisional de identidad definido | F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 | Wave 2.1 |
| DC-01 | Mantener modelo híbrido actual | Benchmark Wave 1.2 (overhead 2-10ms, throughput 1.00x) | F18_DC01_DECISION.md v1.0.0, Wave 2.2 |
| DC-05 | Specialized Contexts (ratificación) | God-Object Test: 6 contextos sin solapamiento | F18_DC05_DECISION.md v1.0.0, Wave 2.3 |

**Nota de cierre de Gate 2:** Las tres Waves de Gate 2 completadas sin nuevos hallazgos DF/GF. DF-09 reclasificado a RESOLVED porque la reevaluación de DC-01 que exigía se materializó en F18_DC01_DECISION.md v1.0.0. DF-13 permanece REVIEW_REQUIRED (diferido a Gate 3, Task 3.4.2). Gate 2 queda COMPLETED con 3 DCs resueltos y 1 hallazgo pendiente de revisión.

#### Evidencia forense por hallazgo

**DF-13 — `model_de_execution` ausente de `identity_chain`:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | Wave 2.1 (Task 2.1.1); F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 §2.2; core/benchmark/verification/identity_chain.py |
| **Estado** | `REVIEW_REQUIRED` |
| **Gate** | Gate 2 (Wave 2.1) → Gate 3 (Wave 3.4, Task 3.4.2) |
| **Descripción** | `model_de_execution` (modo de ejecución: secuencial vs concurrente vs híbrido) NO está incluido en `identity_chain` de `build_identity_chain()`. El `execution_id` es un hash determinista derivado de `baseline + subject + config + parameter + profile` (NO incluye `result` — anti-circularidad; NADR-F17BIS-28 §5.1 R6/§5.2 R13). La fórmula real del código `build_execution_id()` siempre fue esta; el contrato v1.0.1 estaba desactualizado (decía "baseline + config + profile + result") y fue corregido a v1.0.2 en Gate 4 Task 4.1.1. Dos ejecuciones con los mismos parámetros científicos producen el MISMO execution_id independientemente del modo de ejecución y del resultado. El testing diferencial (DC-12) no puede distinguir modos de ejecución por execution_id alone. INV-EXEC-IDENTIFIABILITY está parcialmente satisfecha: el modo es identificable en la configuración del sistema, pero no está presente en el identity_chain del reporte de verificación. |
| **Archivos auditados** | core/benchmark/verification/identity_chain.py (build_identity_chain, build_execution_id), core/benchmark/verification/report.py (ContinuousVerificationReport), F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 §2.2 (corregido a v1.0.2 en Gate 4) |
| **Gap confirmado** | (a) gap confirmado: ausencia de discriminador de modo de ejecución en identity_chain |
| **Implicación para DC-12** | El guard diferencial (M1) requiere comparar dos modos de ejecución. Sin `model_de_execution` en el reporte, la distinción de modos debe hacerse por configuración externa al reporte, no por identity_chain. Esto no invalida DC-12 pero debilita la trazabilidad del modo en la evidencia de verificación. |
| **Acción requerida** | Evaluar en Gate 3 (Task 3.4.2) si `build_identity_chain()` debe extenderse con `model_de_execution` como campo de execution identity, o si el modo debe registrarse en metadata operacional del ContinuousVerificationReport. La decisión requiere evaluar impacto en NADR-F18-01 §5.2 R6-R9 y en la estabilidad de identity_chain existente. |
| **Regla aplicada** | NADR-F18-01 §5.2 R6 (toda propiedad que determine el modo/política de ejecución MUST ser clasificada como execution identity); §5.2 R7 (execution identity identificable). INV-EXEC-IDENTIFIABILITY (ADR_F18_MASTER §5.1): el modo de ejecución habilita testing diferencial. |

### 2.3 Gate 3 Exit Review — COMPLETO (Waves 3.1-3.5 completadas, 2026-10-06)

**Árbol de decisión aplicado:**

    1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
    2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
    3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
    4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-13 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED** | Opción B: `model_de_execution` registrado como metadata operacional (ExecutionMetadata) separada de identity_chain. R8 respetado, backward-compatible. Task 3.4.2. |
| DF-06 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED — MOVE** | Imports cruzados confirmados (Task 3.5.1); runners movidos de core/ a apps/benchmark/runners/, 2 ignore_import eliminados de pyproject.toml (Task 3.5.2). |
| GF-01 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED — DELETE** | Re-análisis: ambos NullTelemetryAdapter son código muerto (ninguno importado). adapters.py eliminado; canónico de ports.py conservado. Task 3.5.3. |

**Resumen:**
- RESOLVED: 1 (DF-13)
- RESOLVED — MOVE: 1 (DF-06)
- RESOLVED — DELETE: 1 (GF-01)
- Nuevos hallazgos registrados: 0

**Nota de cierre de Gate 3:** Las cinco Waves de Gate 3 completadas sin nuevos hallazgos DF/GF. Los tres hallazgos pendientes al inicio del Gate fueron resueltos: DF-13 (heredado de Gate 2 como REVIEW_REQUIRED, resuelto vía Opción B metadata operacional en Task 3.4.2), DF-06 (pre-registrado en §2.0, resuelto como RESOLVED — MOVE en Task 3.5.2), GF-01 (heredado de Gate 1 como IMPLEMENTATION_REQUIRED, resuelto como RESOLVED — DELETE en Task 3.5.3). Gate 3 queda COMPLETED con cero hallazgos pendientes de resolución. Restante Gate 4 (verificación) no tiene hallazgos asociados hasta su ejecución.

#### Evidencia forense por hallazgo

**DF-13 — `model_de_execution` ausente de `identity_chain`:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | Wave 2.1 (Task 2.1.1); diferido a Gate 3 Task 3.4.2 |
| **Estado** | `RESOLVED` |
| **Gate** | Gate 3 (Wave 3.4, Task 3.4.2) |
| **Decisión adoptada** | **Opción B — metadata operacional.** `model_de_execution` se registra como metadata operacional separada, NO se extiende `build_identity_chain()`. Alternativas evaluadas: (A) extender identity_chain — rechazada por cambiar semántica de execution_id, requerir aprobación del Board y romper compatibilidad histórica; (B) metadata operacional — aceptada. |
| **Resolución** | Creado `core/benchmark/verification/execution_metadata.py` (ExecutionMetadata frozen: model_de_execution, execution_timestamp_iso8601, telemetry_execution_id). Modificado `core/benchmark/verification/report.py` (campo opcional execution_metadata en ContinuousVerificationReport + serialización JSON) y `tools/evaluation/run_regression.py` (inyecta model_de_execution="sequential_regression" + telemetry_execution_id existente de Task 1.1.1). |
| **Verificación empírica** | Regresión SMOKE generó JSON con execution_metadata presente: `model_de_execution: sequential_regression`, `telemetry_execution_id: dc542da753d143bb`. |
| **Regla aplicada** | NADR-F18-01 §5.2 R7/R9 (execution identity identificable/registrable), §5.2 R8 (execution identity NO contamina scientific identity — identity_chain intacto). INV-EXEC-IDENTIFIABILITY satisfecha: el modo es registrable y trazable en el reporte. |

**DF-06 — Imports cruzados core/benchmark/runners → apps/:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Deferred Finding |
| **Origen** | HITO_0.2 v1.2.0 (E-0.2-005); pre-registrado en §2.0 |
| **Estado** | `RESOLVED — MOVE` |
| **Gate** | Gate 3 (Wave 3.5, Tasks 3.5.1 y 3.5.2) |
| **Task 3.5.1 — Evaluación** | CONFIRMADO. Evidencia forense: (1) gemini_runner.py y groq_runner.py en core/benchmark/runners/ importan de apps.llm_workers (PromptBuilder, AsyncDispatcher) y apps.bootstrap (build_provider_stack, build_healing_pipeline); (2) GroqBenchmarkRunner tiene 1 consumidor (core/benchmark/__main__.py), GeminiBenchmarkRunner tiene 0 (código muerto); (3) benchmark runners ≠ production providers (apps/llm_workers/adapters.py); (4) ningún test importa los runners; (5) pyproject.toml tiene 2 ignore_import de DF-06 (Contrato 1 y Contrato 3). |
| **Task 3.5.2 — Resolución** | Destino elegido: `apps/benchmark/runners/` (NO infra/) porque el Contrato 2 de import-linter prohíbe infra→apps y los runners importan de apps.llm_workers/apps.bootstrap; apps/benchmark/runners/ es el único destino sin violaciones ni nuevos ignore_import. Ejecución: git mv de ambos runners + __main__.py a apps/benchmark/; import actualizado (core.benchmark.runners → apps.benchmark.runners); pyproject.toml: 2 ignore_import eliminados (Contrato 1: 4→3; Contrato 3: 1→0). |
| **Verificación** | pyright 0 errors; lint-imports 4 KEPT / 0 BROKEN; tests 6/6 passed. La deuda técnica fue eliminada, no movida. |
| **Regla aplicada** | ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal): el dominio (core/) no depende de la infraestructura/capa de aplicación (apps/). |

**GF-01 — NullTelemetryAdapter duplicado con APIs incompatibles:**

| Campo | Valor |
|-------|-------|
| **Tipo** | Governance Finding |
| **Origen** | Wave 1.1; destino Gate 3 (Wave 3.5) |
| **Estado** | `RESOLVED — DELETE` |
| **Gate** | Gate 3 (Wave 3.5, Task 3.5.3 — agregada en Execution Plan v1.0.6) |
| **Re-análisis** | El diagnóstico original ("consolidar dos adaptadores en uso") cambió con evidencia nueva: grep confirmó que NINGUNO de los dos NullTelemetryAdapter es importado en todo el código, y record_metric/record_event nunca se llaman. Ambos son código muerto. El hallazgo pasó de "consolidación" a "eliminación de duplicado muerto". |
| **Resolución** | `core/telemetry/adapters.py` eliminado (contenía NullTelemetryAdapter con API incompatible record_metric/record_event). NullTelemetryAdapter canónico de `core/telemetry/ports.py` (implementa TelemetryPort.record_execution) conservado. |
| **Verificación** | pyright 0 errors; tests en verde. Sin imports huérfanos. |
| **Regla aplicada** | ENGINEERING_PRINCIPLES §III (Explicit over Implicit): una única implementación canónica explícita. YAGNI: código muerto eliminado sin conservarlo "por si acaso". |

### 2.4 Gate 4 Exit Review — COMPLETO (Waves 4.1-4.3 completadas, 2026-10-07)

**Árbol de decisión aplicado:**

    1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
    2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
    3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
    4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | Sin hallazgos nuevos | Gate 4 es verificación/validación; no produjo hallazgos DF/GF nuevos |

**Resumen:**
- RESOLVED: 0
- CLOSED (NAR): 0
- Nuevos hallazgos registrados: 0

**Nota de cierre de Gate 4:** Las tres Waves de Gate 4 (4.1 Static Verification, 4.2 Dynamic Validation, 4.3 Technique Evaluation) se completaron sin identificar nuevos hallazgos DF/GF. Gate 4 es un Gate de verificación y evaluación, no de implementación; su función es confirmar que las propiedades implementadas en Gate 3 se sostienen bajo análisis estático y validación dinámica. Las observaciones documentadas durante Gate 4 (detalladas abajo) NO son hallazgos de la Subfase 18.1: son condiciones pre-existentes documentadas en HITOs de Fase 0 o correcciones aplicadas dentro del Gate. Gate 4 queda COMPLETED con cero hallazgos nuevos y cero hallazgos pendientes. La Subfase 18.1 queda cerrada formalmente.

#### Observaciones documentadas en Gate 4 (NO son hallazgos de 18.1)

| # | Observación | Wave | Disposición |
|---|-------------|------|-------------|
| 1 | Discrepancia entre F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 y el código: el contrato decía execution_id = hash(baseline + config + profile + result), pero build_execution_id() excluye result (NADR-F17BIS-28 §5.1 R6/§5.2 R13) e incluye subject y parameter (§5.1 R3/R5). | 4.1 (Task 4.1.1) | **Corregida:** contrato actualizado a v1.0.2 con fórmula alineada al código. Scientific Identity (§2.1) no se toca; no requiere recalibración de DC-12. |
| 2 | core/execution/handlers.py:15 importa de infra.db.fsm_repository. Deuda pre-existente de Fase 17, ya en ignore_imports de pyproject.toml. NO introducida por Gate 3, NO parte de DF-06. | 4.1 (Task 4.1.2) | **Documentada como observación pre-existente.** No es hallazgo de 18.1. Resolución corresponde a fase futura (refactor de handlers). |
| 3 | runtime/engine.py importa de apps/ (3 imports). Pre-existente, no hay contrato de import-linter que prohíba runtime→apps. | 4.1 (Task 4.1.2) | **Documentada como observación pre-existente.** No es hallazgo de 18.1. |
| 4 | scientific_verdict=HARD_FAIL (exit_code=2) en regresión SMOKE. Condición conocida y documentada del corpus canónico según HITO_0.7 v1.1.0 (estado basal legítimo, FASE_6_HANDOFF §2.2, DF-10). Pre-existente a la Subfase 18.1. | 4.2 (Task 4.2.2) | **Documentada como observación pre-existente.** No es hallazgo de 18.1. La investigación del HARD_FAIL corresponde a Subfase 17-BIS (re-calibración del corpus) o Subfase 18.5 (DC-12). |
| 5 | DC-01 decidió MANTENER el modelo híbrido (un solo modo de ejecución), por lo que la comparación "mismo documento bajo distintos modos" se limita a verificar que el modo actual es científicamente neutro. La comparación multi-modo queda diferida a DC-12 (Subfase 18.5). | 4.2 (Task 4.2.2) | **Limitación documentada.** No es hallazgo; es consecuencia de la decisión DC-01. |
| 6 | DC-06b NO resuelto en la Subfase 18.1. Es decisión de Board compartida entre Subfases 18.1-18.4. F18_DC06b_EVALUATION_REPORT.md v1.0.0 emitido con recomendación para el Board. | 4.3 (Task 4.3.2) | **Documentado para el Board.** No es hallazgo; es una decisión pendiente de Board con evidencia consolidada. |

#### Verificación de propiedades (evidencia de Gate 4)

| Propiedad | Método | Evidencia |
|-----------|--------|-----------|
| NADR-F18-01 (20 reglas) verificadas estáticamente | pyright + tests de contrato | 42 tests passed; contrato v1.0.2 |
| NADR-F18-02 (32 reglas) verificadas estáticamente | pyright + tests de contrato | 43 tests passed |
| Bounded execution bajo carga | Tests de integración + suite unitaria | 854 passed; SMOKE ejecuta sin crash |
| No deadlocks/livelocks | Suite unitaria completa | 854 passed en 48s |
| Verification isolation | Grep de threading/asyncio en run_regression.py | Grep vacío (sin threading/asyncio) |
| Neutralidad científica (INV-SCI-1) | Dos ejecuciones SMOKE independientes | Mismo execution_id, mismo scientific_verdict |
| Operational state variable (INV-OPS-1) | Dos ejecuciones SMOKE independientes | Timestamps/telemetry_ids diferentes, resultado estable |
| Frontera mecanismo/política | Inspección de puertos y mecanismos | Puertos abstractos sin política embebida |
| Shutdown sin recovery | Inspección de CoordinatedShutdownMechanism | Sin leases/zombies/fencing/recovery |
| DC-06b evaluado | Matriz de evaluación por técnica | 1 técnica CAE, 5 requieren evidencia adicional |

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | IDs |
|--------------|----------|-----|
| CLOSED (NAR) | 1 | DF-08 |
| RESOLVED — DELETE | 1 | GF-01 |
| RESOLVED — MOVE | 1 | DF-06 |
| RESOLVED | 3 | DF-07, DF-09 (F18), DF-13 |
| IMPLEMENTATION_REQUIRED | 0 | — |
| RECLASSIFIED_FUTURE_PHASE | 0 | — |
| REVIEW_REQUIRED | 0 | — |
| ACCEPTED_LIMITATION | 0 | — |
| PENDING_REVIEW | 0 | — |

> **Nota de prefijos:** La columna "IDs" lista identificadores con su prefijo correspondiente (DF- para Deferred Findings, GF- para Governance Findings). El conteo total de 6 hallazgos analizados incluye 5 DFs + 1 GF.

### 3.2 Tabla consolidada

| DF/GF | Estado | Decisión |
|----|--------|----------|
| DF-06 | **RESOLVED — MOVE** | Imports cruzados confirmados (Task 3.5.1) y resueltos (Task 3.5.2): runners movidos de core/benchmark/runners/ a apps/benchmark/runners/, __main__.py movido a apps/benchmark/, import actualizado, 2 ignore_import eliminados de pyproject.toml (Contrato 1: 4→3; Contrato 3: 1→0). Verificación: pyright 0 errors, lint-imports 4 KEPT/0 BROKEN, tests 6/6. Ver §2.3 para evidencia forense completa. |
| DF-07 | RESOLVED | RegressionTelemetryGateway creado en Wave 1.1 (Task 1.1.1). Adaptador síncrono SQLite WAL con context manager. Pyright: 0 errors. Tests: 6/6 passed. |
| DF-08 | CLOSED (NAR) | Falso positivo. Verificación forense (Select-String) confirmó que pipeline_factory.py:210 tiene `draft = _layout_block_to_draft(block, page.page_number, reading_order)` y pipeline_factory.py:202 tiene `error_summary = "; ".join(report.errors)`. El código pegado estaba truncado por encoding de PowerShell. |
| GF-01 | **RESOLVED — DELETE** | Re-análisis en Task 3.5.3: ambos NullTelemetryAdapter son código muerto (ninguno importado; record_metric/record_event nunca llamados). core/telemetry/adapters.py eliminado; NullTelemetryAdapter canónico de ports.py conservado. Verificación: pyright 0 errors, tests verde, sin imports huérfanos. Ver §2.3 para evidencia forense completa. |
| DF-09 (F18) | **RESOLVED** | Resultado contraintuitivo del benchmark de SyncProviderBridge (Wave 1.2). La barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugería. **Reclasificado en Gate 2 Exit Review:** la reevaluación de DC-01 exigida por DF-09 se materializó en F18_DC01_DECISION.md v1.0.0 (decisión: mantener modelo híbrido). La evidencia del benchmark fue consumida para resolver DC-01. **Nota de numeración (§1.6):** DF-09 de F18 NO es el mismo hallazgo que DF-09 de Fase 17-BIS (enforcement CV diferido, ACCEPTED_LIMITATION). |
| DF-13 | **RESOLVED** | Opción B (Task 3.4.2): `model_de_execution` registrado como metadata operacional (ExecutionMetadata) separada de identity_chain. Creado execution_metadata.py; report.py y run_regression.py actualizados. R8 respetado (identity_chain intacto, execution_id históricos sin alterar), backward-compatible. Verificación: pyright 0 errors, tests 4/4, regresión SMOKE con execution_metadata presente en JSON. Ver §2.3 para evidencia forense completa. |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Estructura abierta. Se agregará una sub-sección por cada batch ejecutado. Ningún batch ha sido ejecutado todavía.}

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 6 |
| Hallazgos resueltos | 5 |
| Hallazgos cerrados sin acción | 1 |
| Hallazgos reclasificados a fase futura | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Waves de implementación completadas (Gate 3) | 5 (3.1, 3.2, 3.3, 3.4, 3.5) |
| Waves de verificación completadas (Gate 4) | 3 (4.1, 4.2, 4.3) |
| Archivos eliminados totales | 1 (core/telemetry/adapters.py) |
| Archivos reubicados totales (DF-06) | 3 (groq_runner.py, gemini_runner.py, __main__.py → apps/benchmark/) |
| Documentos de verificación emitidos (Gate 4) | 1 (F18_DC06b_EVALUATION_REPORT.md v1.0.0) |
| Contratos corregidos (Gate 4) | 1 (F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 → v1.0.2) |
| Tests finales | Suite completa verde (854 passed, 1 warning cosmético no relacionado) |
| Pyright final | 0 errors |
| lint-imports final | 4 contratos KEPT / 0 BROKEN |
| Observaciones documentadas (Gate 4, no son hallazgos) | 6 (ver §2.4) |

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
1. No hay hallazgos en estado IMPLEMENTATION_REQUIRED sin batch asignado ✅
2. No hay hallazgos en estado REVIEW_REQUIRED sin decisión ✅
3. Todos los batches planificados están completados ✅
4. Los hallazgos RECLASSIFIED_FUTURE_PHASE tienen destino explícito ✅ (ninguno)
5. Todos los Gates del PHASE_18.1_EXECUTION_PLAN v1.0.7 están COMPLETED ✅
6. La Subfase 18.1 cumple el Global DoD definido en §5 del Execution Plan ✅

**Estado:** Todos los criterios satisfechos. El Findings Register queda formalmente cerrado para la Subfase 18.1.

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 6 |
| Hallazgos resueltos | 5 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 1 |
| Gates completados | 4/4 (Gate 1, 2, 3, 4) |
| Estado del Exit Review | ✅ COMPLETED (Subfase 18.1 cerrada formalmente) |

**Veredicto final:** Todos los hallazgos identificados durante la Subfase 18.1 fueron clasificados y resueltos (5 RESOLVED, 1 CLOSED NAR). Gate 4 no produjo hallazgos nuevos. Las observaciones documentadas en Gate 4 son condiciones pre-existentes o consecuencias de decisiones previas, no hallazgos de la Subfase 18.1. La Subfase 18.1 queda formalmente cerrada con cero hallazgos pendientes.

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit de la Subfase 18.1. No tiene
autoridad normativa. No redefine reglas de NADRs ni ADRs. Su único propósito
es documentar la evidencia empírica de los hallazgos identificados durante la
implementación del PHASE_18.1_EXECUTION_PLAN v1.0.7 y su resolución. La
autoridad de clasificación y cierre de hallazgos corresponde exclusivamente a
este documento, conforme a METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.3.

**Cierre formal de la Subfase 18.1:** Con Gate 4 COMPLETED y todos los criterios
de cierre satisfechos, este Findings Register pasa de IN_PROGRESS a COMPLETED.
Los hallazgos que requieran seguimiento en subfases posteriores (18.2-18.5)
deberán registrarse en los Findings Registers correspondientes de esas subfases,
conforme a la convención de numeración por fase (§1.6). Las observaciones
documentadas en Gate 4 (§2.4) que corresponden a fases futuras (HARD_FAIL basal
→ 17-BIS/18.5; handlers.py → refactor futuro; DC-06b → Board 18.2-18.4) quedan
registradas aquí como trazabilidad de la Subfase 18.1, pero su resolución
corresponde a los ámbitos indicados.