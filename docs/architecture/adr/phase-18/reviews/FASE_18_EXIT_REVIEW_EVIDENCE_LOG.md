# FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** docs/architecture/adr/phase-18/reviews/FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md
**Versión:** 1.0.7
**Estado:** COMPLETED
**Fecha:** 2026-10-04
**Última actualización:** 2026-10-07
**Derivado de:** PHASE_18.1_EXECUTION_PLAN.md v1.0.7 — Subfase 18.1 (Execution Plane & Concurrency)
**Ámbito:** Subfase 18.1 — Execution Plane & Concurrency
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review de la Subfase 18.1. Cada finding incluye los archivos
auditados, el análisis, los gaps confirmados, la justificación normativa y la
clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial. Estructura abierta para incorporación dinámica de hallazgos. DF-06 pre-registrado con estructura de análisis preparada. Ningún Gate ejecutado todavía. |
| 1.0.1 | 2026-10-05 | Wave 1.1 completada. Evidencia forense agregada para DF-07 (RESOLVED), DF-08 (CLOSED (NAR)), GF-01 (IMPLEMENTATION_REQUIRED). Gate 1 parcialmente ejecutado (Wave 1.1 de 3). |
| 1.0.2 | 2026-10-05 | Wave 1.2 completada. Evidencia forense agregada para DF-09 (REVIEW_REQUIRED): resultado contraintuitivo del benchmark de SyncProviderBridge. La barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugiere; requiere reevaluación de DC-01. Gate 1 parcialmente ejecutado (Wave 1.1 y 1.2 de 3). |
| 1.0.3 | 2026-10-05 | Wave 1.3 completada sin nuevos hallazgos. Baselines FROZEN v1.0.0 (F18_BASELINE_CONCURRENCY.md, F18_BASELINE_METRICS_PER_STAGE.md) consolidan la evidencia de Waves 1.1 y 1.2 sin revelar gaps adicionales. Gate 1 ✅ COMPLETED (Waves 1.1, 1.2, 1.3 todas DONE; 4 hallazgos derivados). |
| 1.0.4 | 2026-10-05 | Wave 2.1 completada. Evidencia forense agregada para DF-13 (REVIEW_REQUIRED): `model_de_execution` ausente de `identity_chain`; INV-EXEC-IDENTIFIABILITY parcialmente satisfecha. Contrato F18_IDENTITY_BOUNDARY_CONTRACT.md FROZEN v1.0.1 (DC-02-A) emitido. Gate 2 🟡 Parcialmente ejecutado (Wave 2.1 de 3). Convención de numeración por fase y colisión DF-09 documentadas en Findings Register §1.6. |
| 1.0.5 | 2026-10-05 | **Gate 2 ✅ COMPLETED.** Wave 2.2 (DC-01): Mantener modelo híbrido actual (F18_DC01_DECISION.md). Wave 2.3 (DC-05): Specialized Contexts ratificados (F18_DC05_DECISION.md). DF-09 reclasificado a RESOLVED en Findings Register (la reevaluación exigida se materializó en la decisión DC-01). |
| 1.0.6 | 2026-10-06 | **Gate 3 ✅ COMPLETED.** Waves 3.1-3.5 todas DONE. Evidencia forense completada para los 3 hallazgos pendientes: DF-06 (§2.1, RESOLVED — MOVE — runners movidos a apps/benchmark/runners/, 2 ignore_import eliminados de pyproject.toml), GF-01 (§2.4, RESOLVED — DELETE — re-análisis reveló ambos NullTelemetryAdapter como código muerto, adapters.py eliminado), DF-13 (§2.6, RESOLVED — Opción B metadata operacional, identity_chain intacto). Gate 3 Exit Review agregado (§3.3). Cero hallazgos pendientes tras Gate 3. |
| 1.0.7 | 2026-10-07 | **Gate 4 ✅ COMPLETED. Subfase 18.1 ✅ COMPLETED.** Waves 4.1-4.3 todas DONE. Gate 4 no produjo hallazgos DF/GF nuevos (es un Gate de verificación/evaluación). Evidencia de verificación documentada en §3.4: verificación estática (pyright 0 errors, 42+43 tests), validación dinámica (bounded execution, neutralidad científica con 2 ejecuciones SMOKE → mismo execution_id/verdict, verification isolation, frontera mecanismo/política y shutdown/recovery), evaluación DC-06b (1 técnica CAE, 5 requieren evidencia adicional; F18_DC06b_EVALUATION_REPORT.md emitido). Corrección aplicada en Gate 4: F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1→v1.0.2 (fórmula execution_id alineada con código y NADR-F17BIS-28 §5.1 R6/§5.2 R13). Observaciones pre-existentes documentadas (HARD_FAIL basal según HITO_0.7 v1.1.0, handlers.py, runtime/engine.py) — no son hallazgos de 18.1. Criterios de cierre satisfechos; documento cerrado formalmente. |

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
- **INV-EXEC-IDENTIFIABILITY (ADR_F18_MASTER §5.1):** El modo/política de ejecución es identificable y reproducible, excluido de la identidad científica.

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
| RESOLVED | Implementado y cerrado |
| RESOLVED — DELETE | Código muerto eliminado |
| RESOLVED — MOVE | Código reubicado en capa correcta |
| RESOLVED — REFACTORED | Código refactorizado sin cambio funcional |
| RESOLVED — FACTORY EXTRACTION | Lógica extraída a factory canónica |
| CLOSED (NAR) | No Action Required — falso positivo o correcto por diseño |
| ACCEPTED_LIMITATION | Limitación conocida y documentada |
| RECLASSIFIED_FUTURE_PHASE | Movido a fase posterior con justificación |
| IMPLEMENTATION_REQUIRED | Requiere implementación (scope por definir o acotado) |
| REVIEW_REQUIRED | Requiere análisis adicional antes de decidir |
| PENDING_REVIEW | Pendiente de análisis en Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

    1. ¿Sigue siendo válido el hallazgo?
       → NO: CLOSED (NAR)
       → SÍ: continuar

    2. ¿Puede resolverse dentro del Gate actual?
       → SÍ: RESOLVED
       → NO: continuar

    3. ¿Es un problema técnico?
       → SÍ: RECLASIFICADO a Gate futuro
       → NO: continuar

    4. ¿Es un conflicto normativo?
       → SÍ: CONVERTIDO EN GF
       → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE

### 1.5 Relación con el Findings Register

Cada entrada de este Evidence Log tiene una referencia cruzada bidireccional con el FASE_18_DEFERRED_FINDINGS_REGISTER v1.0.7:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

---

## 2. ESTRUCTURA POR FINDING

{Estructura abierta. Se agrega una sub-sección por cada DF/GF analizado. Findings con evidencia forense completa: DF-06 (§2.1), DF-07 (§2.2), DF-08 (§2.3), GF-01 (§2.4), DF-09 (§2.5), DF-13 (§2.6). Gate 4 ejecutado sin producir hallazgos DF/GF nuevos; la evidencia de verificación de Gate 4 se documenta en §3.4 (Gate Exit Review Summary).}

### 2.1 DF-06 — Imports cruzados core→apps (frontera hexagonal)

| Campo | Valor |
|-------|-------|
| **ID** | DF-06 |
| **Tipo** | Deferred Finding |
| **Estado** | RESOLVED — MOVE |
| **Origen** | HITO_0.2 v1.2.0 (E-0.2-005); ADR_F18.1 §4; PHASE_18.1_EXECUTION_PLAN §2C.5 |
| **Gate destino original** | Gate 3 (Wave 3.5, Task 3.5.1) |
| **Gate de resolución** | Gate 3 (Wave 3.5, Tasks 3.5.1 y 3.5.2) |
| **Estado previo** | Pre-registrado (identificado en Fase 0) |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — la evaluación confirmó la violación; se ejecutó el refactor |
| **¿Bloquea la Subfase 18.1?** | No — fue evaluación/refactor paralelo, no bloqueó DC-01 ni DC-05 |

#### 2.1.1 Texto original del DF

> *"Imports cruzados de core/benchmark/runners/ hacia apps/llm_workers y apps/bootstrap violan la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II y dificultan la evaluación independiente del modelo de concurrencia."*

#### 2.1.2 Reformulación corregida

No requiere reformulación. El texto original es preciso y fue confirmado por la auditoría de Gate 3 (Task 3.5.1).

#### 2.1.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | core/benchmark/runners/gemini_runner.py | Importa `apps.llm_workers.prompt_builder.PromptBuilder`, `apps.llm_workers.dispatcher.AsyncDispatcher`, `apps.bootstrap.provider_stack_factory.build_provider_stack`, `apps.bootstrap.pipeline_factory.build_healing_pipeline`. **0 consumidores** (código muerto). |
| 2 | core/benchmark/runners/groq_runner.py | Mismos 4 imports cruzados hacia apps/. **1 consumidor**: core/benchmark/__main__.py (L14, L51, L52). |
| 3 | core/benchmark/__main__.py | Composition root ubicado en core/ que importa GroqBenchmarkRunner y apps.bootstrap.pipeline_factory (segundo ignore_import de DF-06). |
| 4 | pyproject.toml | 2 `ignore_import` de DF-06: Contrato 1 "Domain must not import from Infrastructure" y Contrato 3 "Domain modules must not import concrete OCR provider implementations". |
| 5 | apps/llm_workers/adapters.py | GroqProvider / GeminiProvider (production providers). Confirma que benchmark runners ≠ production providers (clases distintas). |
| 6 | tests/ (grep recursivo) | **Ningún test importa los runners** (grep vacío) — el refactor no rompe tests. |
| 7 | ENGINEERING_PRINCIPLES.md §II | Frontera hexagonal: "El dominio nunca depende de la infraestructura". |
| 8 | HITO_0.2 v1.2.0 §4.2 (E-0.2-005) | Evidencia forense original del hallazgo (Fase 0). |

#### 2.1.4 Análisis

- **¿La condición original existe?** Sí, confirmada. Los runners en core/benchmark/runners/ importan de apps.llm_workers y apps.bootstrap. Es una violación real, no un falso positivo.
- **¿Es una violación normativa o un comportamiento correcto por diseño?** Violación de ENGINEERING_PRINCIPLES §II. Los runners son adaptadores (componen providers LLM + dispatcher + pipeline) y no pueden vivir en core/.
- **¿Qué NADRs/ADRs aplican?** ENGINEERING_PRINCIPLES §II es la autoridad. NADR-F18-02 §8 referencia esta autoridad sin redefinirla.
- **¿Cuál es el impacto funcional real?** La violación era estructural (frontera), no funcional. El refactor (git mv) preserva el comportamiento sin cambio funcional.

**Decisión de destino (Task 3.5.2):** `apps/benchmark/runners/`, **NO** `infra/benchmarks/runners/`. Justificación: el Contrato 2 de import-linter ("Infrastructure must not import from Application layer") prohíbe infra→apps, y los runners importan de apps.llm_workers/apps.bootstrap. `apps/benchmark/runners/` es el único destino donde todos los imports son lícitos sin nuevos ignore_import.

#### 2.1.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Imports cruzados core→apps en ambos runners | grep de imports en gemini_runner.py y groq_runner.py | Alta |
| G2 | Composition root (__main__.py) en core/ importa de apps/ | core/benchmark/__main__.py L14 y apps.bootstrap.pipeline_factory | Alta |
| G3 | 2 ignore_import de DF-06 en pyproject.toml (deuda técnica) | pyproject.toml Contrato 1 y Contrato 3 | Media |

#### 2.1.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Benchmark runners = production providers | ❌ No es gap | Clases distintas: runners en apps/benchmark/, providers en apps/llm_workers/adapters.py |
| Tests rotos por el move | ❌ No es gap | Ningún test importa los runners (grep vacío) |
| GeminiBenchmarkRunner usado en producción | ❌ No es gap | 0 consumidores; código muerto (movido junto, eliminación es decisión aparte) |

#### 2.1.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Refactor de composición sin cambio funcional |
| Reproducibilidad | ❌ No | git mv preserva comportamiento |
| Corrección funcional | ❌ No | Sin cambio funcional |
| Bloquea DC-01 | ❌ No | DC-01 resuelto en Gate 2 |
| Bloquea DC-05 | ❌ No | DC-05 resuelto en Gate 2 |
| Bloquea Gate 4 | ❌ No | Refactor completado antes de Gate 4 |

#### 2.1.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-06-A | Evaluar imports cruzados core/benchmark/runners/ → apps/ | **Completado** (Task 3.5.1) | Benchmark |
| DF-06-B | Eliminar imports cruzados: git mv runners → apps/benchmark/runners/, git mv __main__.py → apps/benchmark/, actualizar import | **Completado** (Task 3.5.2) | Benchmark |
| DF-06-C | Limpiar pyproject.toml: eliminar 2 ignore_import de DF-06 (Contrato 1: 4→3; Contrato 3: 1→0) | **Completado** (Task 3.5.2) | Configuración |

#### 2.1.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí (confirmado en Task 3.5.1) |
| Es violación arquitectónica | ✅ Sí (ENGINEERING_PRINCIPLES §II) |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.1 | ✅ Sí (ADR_F18.1 §4) |
| Bloquea objetivo de 18.1 | ❌ No |
| Clasificación | **RESOLVED — MOVE** |
| Prioridad | Media |

**Verificación de cierre:** pyright 0 errors; lint-imports 4 contratos KEPT / 0 BROKEN; tests 6/6 passed. La deuda técnica fue eliminada, no movida.

#### 2.1.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> *"Separación estricta entre el Dominio (Lógica pura, AST, Modelos) y la Infraestructura (OCR, LLMs, File I/O). El dominio nunca depende de la infraestructura."*

Esta regla aplicó porque DF-06 identificó una dependencia real de core (dominio) hacia apps (capa de aplicación/adaptadores). La resolución movió los runners y el composition root fuera de core/, restaurando la frontera hexagonal y eliminando los 2 ignore_import que mitigaban la deuda. La autoridad de clasificación y cierre corresponde al FASE_18_DEFERRED_FINDINGS_REGISTER.

---

### 2.2 DF-07 — Ausencia de adaptador síncrono para TelemetryPort

| Campo | Valor |
|-------|-------|
| **ID** | DF-07 |
| **Tipo** | Deferred Finding |
| **Estado** | RESOLVED |
| **Origen** | Inspección forense Wave 1.1; PHASE_18.1_EXECUTION_PLAN §2.1 |
| **Gate destino original** | Gate 1 (Wave 1.1, Task 1.1.1) |
| **Estado previo** | Identificado durante inspección forense de Wave 1.1 |
| **Prioridad** | Alta — prerrequisito técnico de Task 1.1.1 |
| **¿Requiere implementación?** | Sí — crear adaptador síncrono de TelemetryPort |
| **¿Bloquea la Subfase 18.1?** | Sí — sin adaptador síncrono no se puede instrumentar run_regression.py |

#### 2.2.1 Texto original del DF

> *"Solo existe SQLiteTelemetryGateway (asíncrono, ProductionTelemetryEvent). No existe implementación síncrona de TelemetryPort.record_execution(StageExecutionRecord). Prerrequisito técnico de Task 1.1.1."*

#### 2.2.2 Reformulación corregida

No requiere reformulación. El texto original es preciso y fue identificado durante la inspección forense de Wave 1.1.

#### 2.2.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | core/telemetry/ports.py (líneas 19-27) | TelemetryPort definido como ABC con record_execution(StageExecutionRecord). NullTelemetryAdapter en línea 25 implementa correctamente la interfaz. |
| 2 | core/telemetry/adapters.py (líneas 1-10) | NullTelemetryAdapter duplicado con API incompatible (record_metric, record_event). No implementa TelemetryPort. (GF-01 identificado aquí.) |
| 3 | core/telemetry/gateway.py | SQLiteTelemetryGateway asíncrono para ProductionTelemetryEvent. No implementa TelemetryPort. |
| 4 | core/telemetry/models.py | ProductionTelemetryEvent y TelemetryEventType definidos. Modelo de producción, no de pipeline stages. |
| 5 | tools/evaluation/run_regression.py | Entry point síncrono. No usa telemetría. Necesita adaptador síncrono. |

#### 2.2.4 Análisis

- **¿La condición original existe?** Sí. No existe ningún adaptador síncrono que implemente TelemetryPort.record_execution(StageExecutionRecord).
- **¿Es una violación normativa o un comportamiento correcto por diseño?** Es un gap de implementación. TelemetryPort (contrato canónico) existe pero no tiene implementación síncrona. SQLiteTelemetryGateway es asíncrono y usa un modelo diferente (ProductionTelemetryEvent).
- **¿Qué NADRs/ADRs aplican?** NADR-F18-02 §5.7 R23-R26 (visibilidad operacional mínima). ENGINEERING_PRINCIPLES §VII (Reuse Before Invent): se reutiliza TelemetryPort existente, se crea adaptador síncrono porque no existe.
- **¿Cuál es el impacto funcional real?** Sin adaptador síncrono, no se puede instrumentar run_regression.py (que es síncrono) para capturar métricas por etapa. Bloquea Task 1.1.1 y GAP-0.5-02.

#### 2.2.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | No existe adaptador síncrono de TelemetryPort | Búsqueda exhaustiva en core/telemetry/ confirma ausencia | Alta |
| G2 | SQLiteTelemetryGateway usa modelo incompatible (ProductionTelemetryEvent vs StageExecutionRecord) | core/telemetry/gateway.py no implementa TelemetryPort | Media |

#### 2.2.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| TelemetryPort (contrato) | ✅ Correcto por diseño | Interface abstracta bien definida en ports.py |
| NullTelemetryAdapter en ports.py | ✅ Correcto por diseño | Implementa TelemetryPort correctamente |
| StageExecutionRecord (modelo) | ✅ Correcto por diseño | Modelo Pydantic completo con todos los campos necesarios |

#### 2.2.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Telemetría no afecta determinismo |
| Reproducibilidad | ❌ No | Telemetría no afecta reproducibilidad |
| Corrección funcional | ⚠️ Parcial | Sin telemetría, no se puede validar GAP-0.5-02 |
| Bloquea DC-01 | ⚠️ Sí (indirecto) | DC-01 requiere evidencia de Gate 1; sin telemetría no hay evidencia por etapa |
| Bloquea DC-05 | ❌ No | DC-05 es independiente de telemetría |
| Bloquea Gate 4 | ❌ No | Gate 4 requiere Gate 1-3 completados |

#### 2.2.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-07-A | Crear core/telemetry/regression_gateway.py con RegressionTelemetryGateway(TelemetryPort) | Completado | Telemetría |
| DF-07-B | Crear tests/telemetry/test_regression_gateway.py con 6 tests | Completado | Tests |
| DF-07-C | Integrar en run_regression.py | Completado | Entry point |

#### 2.2.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí (gap confirmado) |
| Es violación arquitectónica | ❌ No (gap de implementación, no violación) |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.1 | ✅ Sí (prerrequisito de Task 1.1.1) |
| Bloquea objetivo de 18.1 | ✅ Sí (bloquea GAP-0.5-02) |
| Clasificación | RESOLVED |
| Prioridad | Alta |

#### 2.2.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §VII (Reuse Before Invent):**
> *"Toda sustitución de autoridad existente exige evidencia de insuficiencia."*

Esta regla aplica porque se reutiliza TelemetryPort (contrato canónico existente) y se crea un adaptador síncrono nuevo solo porque no existe implementación síncrona. No se inventa un nuevo contrato ni un nuevo modelo de datos.

---

### 2.3 DF-08 — Variables no definidas en pipeline_factory.py

| Campo | Valor |
|-------|-------|
| **ID** | DF-08 |
| **Tipo** | Deferred Finding |
| **Estado** | CLOSED (NAR) |
| **Origen** | Inspección forense Wave 1.1 (código pegado truncado) |
| **Gate destino original** | Gate 1 (Wave 1.1) |
| **Estado previo** | Reportado como bug crítico durante inspección |
| **Prioridad** | Alta (reportado inicialmente) → N/A (falso positivo) |
| **¿Requiere implementación?** | No — falso positivo |
| **¿Bloquea la Subfase 18.1?** | No — no hay bug |

#### 2.3.1 Texto original del DF

> *"Variables no definidas en pipeline_factory.py: error_summary y draft en _adapter_mapper. Reportado como bug crítico de producción."*

#### 2.3.2 Reformulación corregida

No requiere reformulación. El hallazgo fue cerrado como falso positivo tras verificación forense.

#### 2.3.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | apps/bootstrap/pipeline_factory.py línea 202 | `error_summary = "; ".join(report.errors)` — variable definida correctamente |
| 2 | apps/bootstrap/pipeline_factory.py línea 210 | `draft = _layout_block_to_draft(block, page.page_number, reading_order)` — variable definida correctamente |
| 3 | Verificación Select-String | Comandos PowerShell confirmaron presencia de ambas líneas en el archivo real |
| 4 | HITO_0.7 v1.1.0 | Baseline operacional ejecutada exitosamente (wall=1.659s, CPU=1.448s), lo cual es inconsistente con un NameError en el pipeline |

#### 2.3.4 Análisis

- **¿La condición original existe?** No. El código pegado estaba truncado por encoding de PowerShell. Las líneas reales del archivo tienen las variables definidas correctamente.
- **¿Es una violación normativa o un comportamiento correcto por diseño?** No es violación ni gap. Es un falso positivo causado por truncamiento del pegado en la consola PowerShell.
- **¿Qué NADRs/ADRs aplican?** ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos): verificación forense antes de fixear. Un fix incorrecto podría introducir un fallo silencioso peor.
- **¿Cuál es el impacto funcional real?** Ninguno. El código real funciona correctamente. HITO_0.7 ejecutó el pipeline exitosamente.

#### 2.3.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| — | Ningún gap confirmado | Falso positivo | N/A |

#### 2.3.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| error_summary no definido | ❌ No es gap | Línea 202 tiene `error_summary = "; ".join(report.errors)` |
| draft no definido | ❌ No es gap | Línea 210 tiene `draft = _layout_block_to_draft(block, page.page_number, reading_order)` |
| _adapter_mapper roto | ❌ No es gap | Función completa y correcta en el archivo real |

#### 2.3.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | No hay bug |
| Reproducibilidad | ❌ No | No hay bug |
| Corrección funcional | ❌ No | No hay bug |
| Bloquea DC-01 | ❌ No | No hay bug |
| Bloquea DC-05 | ❌ No | No hay bug |
| Bloquea Gate 4 | ❌ No | No hay bug |

#### 2.3.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-08-A | Verificar código real con Select-String | Completado | Verificación |
| DF-08-B | Reclasificar como CLOSED (NAR) | Completado | Findings Register |

#### 2.3.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ❌ No (falso positivo) |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ❌ No |
| Pertenece a Subfase 18.1 | N/A |
| Bloquea objetivo de 18.1 | ❌ No |
| Clasificación | CLOSED (NAR) |
| Prioridad | N/A |

#### 2.3.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Todo fallo debe ser detectable, reportable y trazable."*

Esta regla aplica en sentido inverso: antes de fixear un supuesto bug, se verificó forensemente que el bug existe. La verificación confirmó que es un falso positivo. No se aplicó ningún fix, evitando así introducir un fallo silencioso real.

---

### 2.4 GF-01 — NullTelemetryAdapter duplicado con APIs incompatibles

| Campo | Valor |
|-------|-------|
| **ID** | GF-01 |
| **Tipo** | Governance Finding |
| **Estado** | RESOLVED — DELETE |
| **Origen** | Inspección forense Wave 1.1 |
| **Gate destino original** | Gate 3 (Wave 3.5, junto con refactor de composición) |
| **Gate de resolución** | Gate 3 (Wave 3.5, Task 3.5.3 — agregada en Execution Plan v1.0.6) |
| **Estado previo** | Identificado durante inspección forense de Wave 1.1 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — consolidar NullTelemetryAdapter en una única implementación |
| **¿Bloquea la Subfase 18.1?** | No — warning agregado, consolidación diferida a Gate 3 |

#### 2.4.1 Texto original del GF

> *"Dos clases con el mismo nombre NullTelemetryAdapter coexisten: core/telemetry/ports.py:25 (implementa TelemetryPort correctamente) y core/telemetry/adapters.py:4 (expone record_metric/record_event, API incompatible con TelemetryPort)."*

#### 2.4.2 Reformulación corregida

No requiere reformulación. El texto original es preciso.

#### 2.4.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | core/telemetry/ports.py líneas 19-27 | TelemetryPort (ABC) con record_execution(StageExecutionRecord). NullTelemetryAdapter en línea 25 implementa record_execution correctamente. |
| 2 | core/telemetry/adapters.py líneas 1-10 | NullTelemetryAdapter con record_metric(name, value, tags) y record_event(name, payload). NO implementa TelemetryPort. |
| 3 | core/telemetry/gateway.py | SQLiteTelemetryGateway usa ProductionTelemetryEvent, no TelemetryPort. |
| 4 | ENGINEERING_PRINCIPLES.md §III | "Explicit over Implicit — toda decisión arquitectónica debe ser explícita y trazable." |

#### 2.4.4 Análisis

- **¿La condición original existe?** Sí. Dos clases con el mismo nombre NullTelemetryAdapter coexisten con APIs incompatibles.
- **¿Es una violación normativa o un comportamiento correcto por diseño?** Es una violación de ENGINEERING_PRINCIPLES §III (Explicit over Implicit). La duplicación con APIs incompatibles crea confusión de contratos y riesgo de import incorrecto.
- **¿Qué NADRs/ADRs aplican?** ENGINEERING_PRINCIPLES §III (Explicit over Implicit). NADR-F18-02 §5.7 R25 (evidencia operacional separada): la consolidación debe mantener la separación entre telemetría de producción y telemetría de pipeline.
- **¿Cuál es el impacto funcional real?** Confusión de contratos. Riesgo de que un desarrollador importe el NullTelemetryAdapter incorrecto (de adapters.py en lugar de ports.py). No afecta funcionalidad actual porque el NullTelemetryAdapter de adapters.py no se usa en el flujo de regression.

#### 2.4.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | NullTelemetryAdapter duplicado con APIs incompatibles | ports.py:25 vs adapters.py:4 | Media |
| G2 | adapters.py NullTelemetryAdapter no implementa TelemetryPort | Inspección de código | Media |

#### 2.4.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| TelemetryPort en ports.py | ✅ Correcto por diseño | Interface abstracta bien definida |
| NullTelemetryAdapter en ports.py | ✅ Correcto por diseño | Implementa TelemetryPort correctamente |
| SQLiteTelemetryGateway en gateway.py | ✅ Correcto por diseño | Gateway de producción con modelo diferente |

#### 2.4.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | No afecta determinismo |
| Reproducibilidad | ❌ No | No afecta reproducibilidad |
| Corrección funcional | ❌ No | No afecta funcionalidad actual |
| Bloquea DC-01 | ❌ No | No bloquea DC-01 |
| Bloquea DC-05 | ❌ No | No bloquea DC-05 |
| Bloquea Gate 4 | ❌ No | No bloquea Gate 4 |

#### 2.4.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| GF-01-A | Agregar warning en core/telemetry/adapters.py | Completado | Inmediato |
| GF-01-B | Re-análisis forense previo a consolidación (verificar uso real de ambos NullTelemetryAdapter) | **Completado** (Task 3.5.3) | Gate 3 |
| GF-01-C | Eliminar NullTelemetryAdapter duplicado muerto (core/telemetry/adapters.py); conservar canónico de ports.py | **Completado** (Task 3.5.3) | Gate 3 |

**Nota de re-análisis (Task 3.5.3):** El grep recursivo confirmó que NINGUNO de los dos NullTelemetryAdapter es importado en todo el código, y que `record_metric`/`record_event` nunca se llaman. Ambos son código muerto. Esto cambió el diagnóstico original de "consolidar dos adaptadores en uso" a "eliminar duplicado muerto". La resolución fue eliminar `core/telemetry/adapters.py` por completo (RESOLVED — DELETE) y conservar el NullTelemetryAdapter canónico de `core/telemetry/ports.py` (implementa TelemetryPort.record_execution).

#### 2.4.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí (gap confirmado; re-análisis reveló que ambos son código muerto) |
| Es violación arquitectónica | ⚠️ Parcial (violación de Explicit over Implicit) |
| Es violación de gobernanza | ✅ Sí (conflicto de interfaces en el mismo módulo) |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.1 | ✅ Sí (resolución en Gate 3) |
| Bloquea objetivo de 18.1 | ❌ No |
| Clasificación | **RESOLVED — DELETE** |
| Prioridad | Media |

**Verificación de cierre:** pyright 0 errors; tests en verde; sin imports huérfanos.

#### 2.4.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §III (Explicit over Implicit):**
> *"Toda decisión arquitectónica debe ser explícita y trazable."*

Esta regla aplica porque la duplicación de NullTelemetryAdapter con APIs incompatibles viola el principio de explicitud. La consolidación debe hacer explícita cuál es la implementación canónica. El warning agregado en adapters.py documenta la inconsistencia hasta que se resuelva en Gate 3.

---

### 2.5 DF-09 — Resultado contraintuitivo del benchmark de SyncProviderBridge

| Campo | Valor |
|-------|-------|
| **ID** | DF-09 |
| **Tipo** | Deferred Finding |
| **Estado** | RESOLVED (reclasificado desde REVIEW_REQUIRED en Gate 2 Exit Review) |
| **Origen** | Benchmark de SyncProviderBridge, Wave 1.2 (Task 1.2.1, 1.2.2); reports/benchmark/sync_bridge_benchmark.json |
| **Gate destino original** | Gate 1 (Wave 1.2) → Gate 2 (Wave 2.2, reevaluación de DC-01) |
| **Estado previo** | Identificado durante ejecución del benchmark en Wave 1.2 |
| **Prioridad** | Alta — afecta la decisión DC-01 |
| **¿Requiere implementación?** | No — requiere reevaluación de DC-01 con la nueva evidencia |
| **¿Bloquea la Subfase 18.1?** | No directamente — pero cambia la priorización de DC-01 en Gate 2 |

#### 2.5.1 Texto original del DF

> *"Resultado contraintuitivo del benchmark de SyncProviderBridge: la barrera síncrona NO es el cuello de botella que GAP-0.1-01 sugiere. Overhead p95 pequeño (2-10ms), throughput idéntico (ratio 1.00x), backpressure idéntico, RSS despreciable (0.02 MB). La hipótesis original de HITO_0.1 E-0.1-001 (inferencia estática) es corregida por la primera medición cuantitativa. Requiere reevaluación de DC-01."*

#### 2.5.2 Reformulación corregida

No requiere reformulación. El texto original es preciso y está alineado con la evidencia cuantitativa del benchmark.

#### 2.5.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | tools/evaluation/benchmark_sync_bridge.py | Instrumento de medición efímero creado en Task 1.2.1. 4 experimentos sintéticos con MockLLMProvider y MockPromptBuilder. |
| 2 | reports/benchmark/sync_bridge_benchmark.json | Resultados cuantitativos del benchmark (timestamp, 4 experimentos, limitaciones documentadas). |
| 3 | apps/llm_workers/sync_bridge.py | SyncProviderBridge: barrera síncrona en execute() vía future.result(timeout=180.0), thread dedicado con event loop, shutdown con join(timeout=2.0). |
| 4 | apps/llm_workers/__main__.py | LLMWorkerDaemon: loop síncrono secuencial, backoff exponencial (base=1.0s, max=4.0s, factor=1.2), TaskLeaseHeartbeat en thread separado. |
| 5 | apps/llm_workers/dispatcher.py | AsyncDispatcher: async nativo con PriorityQueue, N workers (default 20), queue.join(), cancelación explícita. |
| 6 | HITO_0.1 v1.2.0 §10 (E-0.1-001) | Evidencia forense original: barrera síncrona identificada como hecho estructural; impacto cuantitativo pendiente de medición (GAP-0.1-01). |
| 7 | FASE0_AUDIT_CHARTER.md §9 | Criterio preregistrado: métrica latencia p95, dirección ↓, condición sin ↑RSS, calibración umbral = p95_baseline × (1 − δ). |

#### 2.5.4 Análisis

- **¿La condición original existe?** La barrera síncrona SÍ existe como hecho estructural (confirmado por HITO_0.1 E-0.1-001). Pero la HIPÓTESIS de que es un cuello de botella significativo NO se confirma. El benchmark cuantitativo revela que el impacto es pequeño o nulo.
- **¿Es una violación normativa o un comportamiento correcto por diseño?** No es violación ni gap. Es una corrección de hipótesis: la inferencia estática original (HITO_0.1) es corregida por la primera medición cuantitativa. Esto valida el proceso "Audit First, Design Later" y "Benchmark Before Optimization" (ADR_F18_MASTER §5.2).
- **¿Qué NADRs/ADRs aplican?** FASE0_AUDIT_CHARTER §9 (criterio preregistrado: la evidencia determina el resultado, no la intuición). ENGINEERING_PRINCIPLES §VII (Benchmark Before Optimization). ADR_F18_MASTER §5.2 (Audit First, Design Later). NADR-F18-02 §5.9 R31 (evidencia cuantitativa para DC-01).
- **¿Cuál es el impacto funcional real?** Cambia la priorización de DC-01. La elisión de SyncProviderBridge NO está justificada por la evidencia cuantitativa. Los modelos candidatos deben evaluarse contra las 32 reglas de NADR-F18-02, no contra la hipótesis de que la barrera es un cuello de botella.

#### 2.5.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | La hipótesis original (GAP-0.1-01) era una inferencia estática no verificada | HITO_0.1 E-0.1-001 identifica la estructura pero no mide el impacto | Media |
| G2 | El overhead de la barrera crece con la latencia del provider (2-10ms p95), no es constante | Exp 1: overhead p95 = 2.05ms (0.1s), 9.28ms (0.5s), 10.40ms (1.0s) | Media |

#### 2.5.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Throughput bajo carga | ❌ No es gap | Ratio async/bridge = 1.00x en N=1,2,5,10,20. Sin diferencia. |
| Backpressure bajo burst | ❌ No es gap | wall=20.08s idéntico ambos paths, peak_threads=5, completed=50. Sin diferencia. |
| Costo de memoria del thread dedicado | ❌ No es gap | RSS delta = 0.02 MB. Despreciable. |
| Existencia de la barrera síncrona | ❌ No es gap | Existe como hecho estructural, pero su impacto es pequeño o nulo. |

#### 2.5.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Telemetría y benchmark no afectan determinismo |
| Reproducibilidad | ❌ No | Telemetría y benchmark no afectan reproducibilidad |
| Corrección funcional | ❌ No | No hay bug; es corrección de hipótesis |
| Bloquea DC-01 | ⚠️ Sí (indirecto) | Cambia la priorización de DC-01 en Gate 2 (Wave 2.2); la elisión de SyncProviderBridge no es prioritaria |
| Bloquea DC-05 | ❌ No | DC-05 es independiente de la barrera síncrona |
| Bloquea Gate 4 | ❌ No | Gate 4 requiere Gate 1-3 completados |

#### 2.5.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-09-A | Ejecutar benchmark de SyncProviderBridge (4 experimentos sintéticos) | Completado | Wave 1.2 |
| DF-09-B | Documentar resultados cuantitativos y evaluar contra criterio preregistrado de Charter §9 | Completado | Wave 1.2 |
| DF-09-C | Reevaluar DC-01 en Gate 2 (Wave 2.2) con la nueva evidencia | **Completado** — materializado en F18_DC01_DECISION.md v1.0.0 (decisión: mantener modelo híbrido) | Gate 2 |
| DF-09-D | Documentar limitaciones del benchmark (mock provider, no replica daemon real, concurrencia N>1 no existe en producción) | Completado | Wave 1.2 |

#### 2.5.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcial (la barrera existe, pero el impacto es pequeño o nulo) |
| Es violación arquitectónica | ❌ No (corrección de hipótesis, no violación) |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí (requirió reevaluación de DC-01) |
| Pertenece a Subfase 18.1 | ✅ Sí (Gate 1 Wave 1.2 → Gate 2 Wave 2.2) |
| Bloquea objetivo de 18.1 | ❌ No (reevaluación completada, DC-01 resuelto) |
| Clasificación | **RESOLVED** (reclasificado desde REVIEW_REQUIRED en Gate 2 Exit Review; la reevaluación de DC-01 se materializó en F18_DC01_DECISION.md v1.0.0) |
| Prioridad | Alta |

#### 2.5.10 Regla aplicada

> **FASE0_AUDIT_CHARTER §9 (Pre-registro de reglas de decisión):**
> *"La forma de cada regla y la regla de calibración quedan congeladas con este charter. Los números concretos se instancian desde el baseline F0-A aplicando la regla de calibración preregistrada."*

Esta regla aplica porque el benchmark evaluó el impacto de la barrera síncrona contra el criterio preregistrado de Charter §9. El resultado muestra que el criterio NO se cumple claramente (overhead 2-10ms, throughput idéntico, RSS sin diferencia), por lo que la elisión de SyncProviderBridge NO está justificada por la evidencia cuantitativa. Esto valida el proceso de preregistro: la evidencia determina el resultado, no la intuición.

**Regla complementaria:**

> **ENGINEERING_PRINCIPLES §VII (Benchmark Before Optimization):**
> *"Toda sustitución de autoridad existente exige evidencia de insuficiencia."*

Esta regla aplica porque la elisión de SyncProviderBridge es una sustitución de autoridad existente. La evidencia del benchmark NO demuestra insuficiencia suficiente para justificar la sustitución.

---

### 2.6 DF-13 — `model_de_execution` ausente de `identity_chain`

| Campo | Valor |
|-------|-------|
| **ID** | DF-13 |
| **Tipo** | Deferred Finding |
| **Estado** | RESOLVED |
| **Origen** | Wave 2.1 (Task 2.1.1); F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 §2.2; core/benchmark/verification/identity_chain.py |
| **Gate destino original** | Gate 2 (Wave 2.1) → Gate 3 (Wave 3.4, Task 3.4.2) |
| **Gate de resolución** | Gate 3 (Wave 3.4, Task 3.4.2) — Opción B |
| **Estado previo** | Identificado durante emisión del contrato DC-02-A |
| **Prioridad** | Media — afecta trazabilidad de DC-12, no bloquea |
| **¿Requiere implementación?** | Condicional — evaluación de extensión de `build_identity_chain` en Gate 3 (Task 3.4.2) |
| **¿Bloquea la Subfase 18.1?** | No — debilita trazabilidad del modo de ejecución en evidencia de verificación, pero no invalida DC-12 |

#### 2.6.1 Texto original del DF

> *"`model_de_execution` (modo de ejecución) NO está incluido en `identity_chain` de `build_identity_chain()`. El testing diferencial (DC-12) no puede distinguir modos de ejecución por execution_id alone. INV-EXEC-IDENTIFIABILITY está parcialmente satisfecha: el modo es identificable en configuración del sistema, pero no presente en el identity_chain del reporte de verificación."*

#### 2.6.2 Reformulación corregida

No requiere reformulación. El texto original es preciso y está alineado con la inspección de `identity_chain.py` y el contrato §2.2.

#### 2.6.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | core/benchmark/verification/identity_chain.py | `build_identity_chain()` compone el IdentityChain completo (baseline_identity, subject_identity, configuration_identity, parameter_identity, profile_identity, result_identity). Internamente `build_execution_id()` calcula execution_id a partir de baseline + subject + config + parameter + profile (sin result). **No incluye campo de modo de ejecución.** |
| 2 | core/benchmark/verification/identity_chain.py (`build_execution_id`) | execution_id = hash determinista de `baseline + subject + config + parameter + profile` (NO incluye `result` — anti-circularidad; NADR-F17BIS-28 §5.1 R6/§5.2 R13). Derivado de scientific identity, **no discriminador de modo**. El contrato v1.0.1 decía "baseline + config + profile + result" (erróneo); corregido a v1.0.2 en Gate 4 Task 4.1.1. |
| 3 | core/benchmark/verification/report.py | `ContinuousVerificationReport` porta identity_chain; sin campo de modo de ejecución en el reporte. |
| 4 | F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 §2.2 | Clasifica `model_de_execution` como execution identity y documenta explícitamente su ausencia en identity_chain (nota DF-13). |
| 5 | NADR-F18-01 v1.0.3 §5.2 R6, R7 | Toda propiedad que determine el modo/política de ejecución MUST ser clasificada como execution identity y MUST ser identificable. |
| 6 | ADR_F18_MASTER §5.1 | INV-EXEC-IDENTIFIABILITY: el modo/política de ejecución es identificable y reproducible y habilita testing diferencial. |

#### 2.6.4 Análisis

- **¿La condición original existe?** Sí. `build_identity_chain()` no incluye `model_de_execution`. Dos ejecuciones con los mismos parámetros científicos producen el **mismo** execution_id independientemente del modo (secuencial vs concurrente) y del resultado, porque execution_id es hash de `baseline + subject + config + parameter + profile` (NO incluye `result` — anti-circularidad).
- **¿Es una violación normativa o un comportamiento correcto por diseño?** Es un gap parcial de materialización, no una violación directa. El contrato DC-02-A **clasifica** correctamente el modo como execution identity (cumple R6 en el plano normativo), pero el mecanismo existente (`identity_chain`) no lo **materializa** en el reporte de verificación (R7 e INV-EXEC-IDENTIFIABILITY quedan parcialmente satisfechos). El modo es identificable en configuración del sistema, pero no en la evidencia de verificación persistida.
- **¿Qué NADRs/ADRs aplican?** NADR-F18-01 §5.2 R6 (clasificación de execution identity), §5.2 R7 (execution identity identificable). INV-EXEC-IDENTIFIABILITY (ADR_F18_MASTER §5.1). NADR-F18-01 §5.2 R8 (el modo NO debe entrar en scientific identity — la extensión propuesta debe respetar esta exclusión).
- **¿Cuál es el impacto funcional real?** DC-12 M1 requiere comparar dos modos de ejecución. Sin el modo en el reporte, la distinción de modos debe hacerse por configuración externa al artefacto de verificación, no por identity_chain. Esto debilita la trazabilidad autocontenida del experimento M1 pero no lo invalida. También afecta Task 3.4.2 (trazabilidad de identidad por artefacto).

#### 2.6.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | `model_de_execution` ausente de `identity_chain` | Inspección de build_identity_chain() en identity_chain.py; contrato §2.2 | Media |
| G2 | `execution_id` no discrimina modo de ejecución | build_execution_id() = hash(baseline + subject + config + parameter + profile); mismos parámetros científicos ⇒ mismo execution_id en cualquier modo y con cualquier resultado | Media |

#### 2.6.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| execution_id determinista | ✅ Correcto por diseño | Identificabilidad de resultado derivado de scientific identity; no debe variar por modo (R8) |
| telemetry_execution_id separado | ✅ Correcto por diseño | Evidencia operacional uuid4, excluida de scientific identity (R8; Wave 1.1) |
| scientific identity sin propiedades de ejecución | ✅ Correcto por diseño | R3 y R8 cumplidos en contrato §2.1 |
| Clasificación normativa del modo | ✅ Correcto por diseño | Contrato §2.2 clasifica model_de_execution como execution identity (R6) |

#### 2.6.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | No afecta determinismo de hashing ni de métricas |
| Reproducibilidad | ❌ No | El modo es reproducible por configuración externa |
| Corrección funcional | ❌ No | No hay bug; es ausencia de campo de trazabilidad |
| Bloquea DC-01 | ❌ No | DC-01 evalúa modelos candidatos; el modo se conoce por configuración |
| Bloquea DC-12 | ⚠️ Parcial | Debilita trazabilidad autocontenida del modo en evidencia de verificación de M1; no invalida el experimento |
| Bloquea Gate 4 | ❌ No | Gate 4 verifica propiedades; la extensión corresponde a Gate 3 |

#### 2.6.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-13-A | Evaluar si `build_identity_chain()` debe extenderse con `model_de_execution` como campo de execution identity | **Completado — RECHAZADO** (Task 3.4.2). La extensión cambiaría la semántica de execution_id, requeriría aprobación del Architecture Board (DC-02-A §5.1) y rompería compatibilidad con reportes históricos. | Gate 3 |
| DF-13-B | Registrar el modo en metadata operacional de `ContinuousVerificationReport` (sin tocar identity_chain) | **Completado — ACEPTADO (Opción B)** (Task 3.4.2). Creado `core/benchmark/verification/execution_metadata.py` (ExecutionMetadata frozen); `report.py` y `run_regression.py` actualizados. | Gate 3 |
| DF-13-C | Verificar que la resolución respete NADR-F18-01 §5.2 R8 (el modo NO entra en scientific identity) y no altere execution_id de reportes históricos | **Completado** (Task 3.4.2). identity_chain y build_execution_id intactos; execution_id históricos sin alterar; backward-compatible. | Gate 3 |

**Verificación empírica (Task 3.4.2):** Regresión SMOKE generó JSON con `execution_metadata` presente: `model_de_execution: sequential_regression`, `execution_timestamp_iso8601` válido, `telemetry_execution_id: dc542da753d143bb`. Tests: 4/4 passed (test_execution_metadata.py).

#### 2.6.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí (gap confirmado) |
| Es violación arquitectónica | ⚠️ Parcial (limitación de mecanismo existente frente a R7 / INV-EXEC-IDENTIFIABILITY; clasificación normativa correcta) |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.1 | ✅ Sí (Gate 3, Task 3.4.2) |
| Bloquea objetivo de 18.1 | ❌ No (resuelto; trazabilidad del modo materializada) |
| Clasificación | **RESOLVED** (Opción B — metadata operacional) |
| Prioridad | Media |

#### 2.6.10 Regla aplicada

> **NADR-F18-01 §5.2 R6 y R7:**
> *"Toda propiedad que determine el modo/política de ejecución MUST ser clasificada como execution identity"* y *"la execution identity MUST ser identificable"*.

Esta regla aplica porque el modo de ejecución determina la política de ejecución y está correctamente clasificado en el contrato (R6), pero no es identificable **en el artefacto de verificación** (R7 parcial). La resolución debe materializar el modo en la evidencia sin violar R8.

**Regla complementaria:**

> **INV-EXEC-IDENTIFIABILITY (ADR_F18_MASTER §5.1):**
> *"El modo/política de ejecución es identificable y reproducible, excluido de la identidad científica."*

Esta regla aplica porque el testing diferencial (DC-12 M1) requiere distinguir modos de ejecución en la evidencia comparada. Sin el modo en identity_chain o en el reporte, la distinción depende de configuración externa, debilitando la autocontenibilidad de la evidencia de M1.

---

## 3. GATE EXIT REVIEW SUMMARY

{Estructura abierta. Se agrega una sub-sección por cada Gate Exit Review ejecutado. Gates completados: 1 (Waves 1.1-1.3), 2 (Waves 2.1-2.3), 3 (Waves 3.1-3.5), 4 (Waves 4.1-4.3). Subfase 18.1 CERRADA FORMALMENTE.}

### 3.0 Estado actual

| Gate | Estado | Fecha | Hallazgos analizados |
|------|--------|-------|---------------------|
| Gate 1 — Evidence & Measurement Baseline | ✅ COMPLETED (Waves 1.1, 1.2, 1.3 todas DONE) | 2026-10-05 | 4 (DF-07, DF-08, GF-01, DF-09) |
| Gate 2 — Architectural Decisions | ✅ COMPLETED (Waves 2.1, 2.2, 2.3 todas DONE) | 2026-10-05 | 2 (DF-09 reclasificado a RESOLVED; DF-13 identificado como REVIEW_REQUIRED) + 3 DCs resueltos (DC-02-A, DC-01, DC-05) |
| Gate 3 — Implementation | ✅ COMPLETED (Waves 3.1-3.5 todas DONE) | 2026-10-06 | 3 resueltos (DF-13, DF-06, GF-01) |
| Gate 4 — Verification & Technique Evaluation | ✅ COMPLETED (Waves 4.1-4.3 todas DONE) | 2026-10-07 | 0 hallazgos nuevos (Gate de verificación/evaluación) |

### 3.1 Gate 1 Exit Review — COMPLETO (Waves 1.1, 1.2, 1.3 completadas, 2026-10-05)

**Árbol de decisión aplicado:**

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-07 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | RegressionTelemetryGateway creado en Task 1.1.1 |
| DF-08 | ❌ No | N/A | N/A | CLOSED (NAR) | Falso positivo por truncamiento de pegado PowerShell |
| GF-01 | ✅ Sí | ❌ No (en Gate 1) | ✅ Sí | IMPLEMENTATION_REQUIRED | Consolidación diferida a Gate 3 |
| DF-09 | ✅ Sí | ❌ No (requiere reevaluación de DC-01) | ✅ Sí | REVIEW_REQUIRED | Resultado contraintuitivo del benchmark de SyncProviderBridge. Derivado a Gate 2 (Wave 2.2) para reevaluación de DC-01. |

**Resumen:**
- RESOLVED: 1 (DF-07)
- CLOSED (NAR): 1 (DF-08)
- IMPLEMENTATION_REQUIRED: 1 (GF-01)
- REVIEW_REQUIRED: 1 (DF-09)
- Nuevos hallazgos registrados: 4

**Nota de cierre de Gate 1 (Wave 1.3, 2026-10-05):** Wave 1.3 (Baseline Documentation) se completó sin identificar nuevos hallazgos. Los baselines FROZEN v1.0.0 (F18_BASELINE_CONCURRENCY.md y F18_BASELINE_METRICS_PER_STAGE.md) consolidan la evidencia de Waves 1.1 y 1.2 sin revelar gaps adicionales a los ya registrados. GAP-0.7-01 permanece parcialmente resuelto (telemetría Wave 1.1 cubre el pipeline de regression); GAP-0.7-02 y GAP-0.7-05 permanecen DEFERRED conforme a HITO_0.7 §14. Gate 1 queda COMPLETED con 4 hallazgos derivados y evidencia suficiente para Gate 2 (DC-01).

**Evidencia forense detallada:** Ver §2.2 (DF-07), §2.3 (DF-08), §2.4 (GF-01), §2.5 (DF-09).

### 3.2 Gate 2 Exit Review — COMPLETO (Waves 2.1, 2.2, 2.3 completadas, 2026-10-05)

**Árbol de decisión aplicado:**

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-09 | ✅ Sí | ✅ Sí (DC-01 resuelto con esta evidencia) | ✅ Sí | **RESOLVED** | La reevaluación de DC-01 exigida por DF-09 se materializó en F18_DC01_DECISION.md v1.0.0. El benchmark demostró que la elisión de SyncProviderBridge no produce beneficio medible; DC-01 resuelto: mantener modelo híbrido. |
| DF-13 | ✅ Sí | ❌ No (requiere cambio de código en identity_chain) | ✅ Sí | REVIEW_REQUIRED | `model_de_execution` ausente de `build_identity_chain()`. Evaluación de extensión diferida a Gate 3 (Task 3.4.2). |

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

**Evidencia forense detallada:** Ver §2.5 (DF-09), §2.6 (DF-13), y documentos de decisión F18_DC01_DECISION.md / F18_DC05_DECISION.md.

### 3.3 Gate 3 Exit Review — COMPLETO (Waves 3.1-3.5 completadas, 2026-10-06)

**Árbol de decisión aplicado:**

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-13 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED** | Opción B: `model_de_execution` registrado como metadata operacional (ExecutionMetadata) separada de identity_chain. R8 respetado, backward-compatible. Task 3.4.2. |
| DF-06 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED — MOVE** | Imports cruzados confirmados (Task 3.5.1); runners movidos a apps/benchmark/runners/, 2 ignore_import eliminados (Task 3.5.2). |
| GF-01 | ✅ Sí | ✅ Sí (en Gate 3) | ✅ Sí | **RESOLVED — DELETE** | Re-análisis: ambos NullTelemetryAdapter son código muerto. adapters.py eliminado; canónico de ports.py conservado. Task 3.5.3. |

**Resumen:**
- RESOLVED: 1 (DF-13)
- RESOLVED — MOVE: 1 (DF-06)
- RESOLVED — DELETE: 1 (GF-01)
- Nuevos hallazgos registrados: 0

**Nota de cierre de Gate 3:** Las cinco Waves de Gate 3 (3.1 Bounded Execution, 3.2 Admission/Backpressure, 3.3 Cancellation/Shutdown, 3.4 Visibility/Identity Traceability, 3.5 Composition Refactor) se completaron sin nuevos hallazgos DF/GF. Los tres hallazgos pendientes de Gates 1 y 2 fueron resueltos: DF-13 (Opción B metadata operacional), DF-06 (refactor de composición runners→apps), GF-01 (eliminación de duplicado muerto). Gate 3 queda COMPLETED con cero hallazgos pendientes. La verificación final de Gate 3 arrojó: pyright 0 errors, lint-imports 4 contratos KEPT / 0 BROKEN, suite tests en verde.

**Evidencia forense detallada:** Ver §2.1 (DF-06), §2.4 (GF-01), §2.6 (DF-13).

### 3.4 Gate 4 Exit Review — COMPLETO (Waves 4.1-4.3 completadas, 2026-10-07)

**Árbol de decisión aplicado:**

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | Sin hallazgos nuevos | Gate 4 es verificación/evaluación; no produjo hallazgos DF/GF nuevos |

**Resumen:**
- RESOLVED: 0
- CLOSED (NAR): 0
- Nuevos hallazgos registrados: 0

**Nota de cierre de Gate 4:** Las tres Waves de Gate 4 (4.1 Static Verification, 4.2 Dynamic Validation, 4.3 Technique Evaluation) se completaron sin identificar nuevos hallazgos DF/GF. Gate 4 es un Gate de verificación y evaluación; su función es confirmar que las propiedades implementadas en Gate 3 se sostienen bajo análisis estático y validación dinámica. Las observaciones documentadas durante Gate 4 NO son hallazgos de la Subfase 18.1: son condiciones pre-existentes documentadas en HITOs de Fase 0 o correcciones aplicadas dentro del Gate. Gate 4 queda COMPLETED con cero hallazgos nuevos y cero hallazgos pendientes. La Subfase 18.1 queda cerrada formalmente.

#### Evidencia de verificación por Wave

**Wave 4.1 — Static Verification:**

| Verificación | Resultado | Evidencia |
|--------------|-----------|-----------|
| NADR-F18-01 (20 reglas) verificadas estáticamente | ✅ DONE | pyright 0 errors sobre identity_chain.py, execution_metadata.py, report.py, outcome.py; 42 tests passed (test_identity_chain, test_execution_metadata, test_verification_report) |
| NADR-F18-02 (32 reglas) verificadas estáticamente | ✅ DONE | pyright 0 errors sobre 15 módulos de Gate 3 (core/execution/*, runtime/*, infra/os/resource_monitor.py); 43 tests passed (6 archivos de tests de Gate 3) |
| Contrato F18_IDENTITY_BOUNDARY_CONTRACT.md verificado | ✅ DONE | 3 dimensiones ortogonales, cláusula de invalidación, gobernanza de modificaciones |

**Acción correctiva aplicada en Task 4.1.1:** Discrepancia detectada entre F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.1 y el código. El contrato decía execution_id = hash(baseline + config + profile + result), pero build_execution_id() excluye result (NADR-F17BIS-28 §5.1 R6: Execution precede a Result en identity chain; §5.2 R13: result identity no sustituye entradas) e incluye subject y parameter (§5.1 R3, R5). **Resolución:** contrato actualizado a v1.0.2 con fórmula corregida: execution_id = hash(baseline + subject + config + parameter + profile). Scientific Identity (§2.1) no se toca; no requiere recalibración de DC-12. Esta corrección fue verificada con NADR-F17BIS-28 (texto completo de §5.1 y §5.2) y confirmada por el usuario.

**Observaciones pre-existentes documentadas en Task 4.1.2 (NO son hallazgos de 18.1):**

| # | Observación | Veredicto |
|---|-------------|-----------|
| 1 | core/execution/handlers.py:15 importa de infra.db.fsm_repository | Deuda pre-existente de Fase 17, ya en ignore_imports de pyproject.toml. NO introducida por Gate 3, NO parte de DF-06. Resolución corresponde a fase futura. |
| 2 | runtime/engine.py importa de apps/ (3 imports) | Pre-existente, no hay contrato de import-linter que prohíba runtime→apps. No es violación de ningún contrato vigente. |

**Wave 4.2 — Dynamic Validation:**

| Verificación | Resultado | Evidencia |
|--------------|-----------|-----------|
| Bounded execution bajo carga | ✅ DONE | 16 tests passed (test_recovery_flow, test_backpressure_mechanism, test_coordinated_shutdown, test_cancellation_mechanism); suite unitaria completa 854 passed |
| No deadlocks/livelocks (§5.5 R18) | ✅ DONE | Suite unitaria completa 854 passed, termina en 48s |
| Verification isolation (§5.8 R29) | ✅ DONE | run_regression.py no usa threading/asyncio (grep vacío) |
| Neutralidad científica (INV-SCI-1, §5.8 R27) | ✅ DONE | Dos ejecuciones SMOKE independientes (20:11:53 y 20:19:50 UTC del 7/10/2026) producen el mismo execution_id (0294be97...) y el mismo scientific_verdict (HARD_FAIL) |
| Operational state variable (INV-OPS-1, §5.8 R28) | ✅ DONE | execution_timestamp y telemetry_execution_id diferentes entre ejecuciones; execution_id y scientific_verdict estables |
| NADR-F18-01 §5.1 R4, §5.3 R11/R12, §5.4 R15 | ✅ DONE | Verificadas dinámicamente mediante las dos ejecuciones SMOKE comparadas |
| Frontera mecanismo/política (§5.2 R7, §5.3 R10) | ✅ DONE | AdmissionMechanismPort y BackpressureMechanismPort son puertos abstractos (Protocol) sin política embebida; docstrings referencian explícitamente que la política corresponde a Subfase 18.3 |
| Shutdown sin recovery (§5.4 R15) | ✅ DONE | CoordinatedShutdownMechanism NO implementa recuperación de estado persistente (sin leases, zombies, fencing); ShutdownReport sin campos de recovery |

**Observación documentada en Task 4.2.2 (NO es hallazgo de 18.1):**

scientific_verdict=HARD_FAIL (exit_code=2) en regresión SMOKE. Condición conocida y documentada del corpus canónico según HITO_0.7 v1.1.0 (estado basal legítimo, FASE_6_HANDOFF §2.2, DF-10). Es pre-existente a la Subfase 18.1 (reportes del 5/10/2026 ya muestran exit_code=2, antes de Gate 3 implementado el 6/10/2026). No fue introducida por el execution plane ni por Gate 3. La investigación del HARD_FAIL corresponde a Subfase 17-BIS (re-calibración del corpus) o Subfase 18.5 (DC-12), no a la Subfase 18.1. Se registró como observación en el Evidence Log, NO como DF formal, conforme a la decisión del usuario y la verificación de HITO_0.7 v1.1.0.

**Limitación documentada en Task 4.2.2:** DC-01 decidió MANTENER el modelo híbrido (un solo modo de ejecución), por lo que la comparación "mismo documento bajo distintos modos" se limita a verificar que el modo actual es científicamente neutro. La comparación multi-modo queda diferida a DC-12 (Subfase 18.5).

**Wave 4.3 — Technique Evaluation (DC-06b):**

| Verificación | Resultado | Evidencia |
|--------------|-----------|-----------|
| Evaluación de 6 técnicas candidatas | ✅ DONE | Matriz de evaluación por técnica contra criterio preregistrado de Charter §9 |
| DC-06b documentado para Board | ✅ DONE | F18_DC06b_EVALUATION_REPORT.md v1.0.0 emitido en docs/architecture/adr/phase-18/reports/ |

**Resultado de la evaluación DC-06b:**

| # | Técnica | Resultado | Justificación |
|---|---|---|---|
| 1 | SyncProviderBridge elision | **CAE** | DC-01 decidió mantener modelo híbrido; DF-09 demostró overhead negligible (2-10ms), throughput 1.00x |
| 2 | Process pools | Requiere evidencia adicional | GAP-0.7-01 OPEN — sin descomposición CPU por etapa |
| 3 | Object pools / zero-copy | Requiere evidencia adicional | Sin allocations ni hotspot medidos |
| 4 | Lazy loading | Requiere evidencia adicional | Sin datos por documento |
| 5 | LLM cache | Requiere evidencia adicional | GAP-0.7-02 OPEN — no medible vía run_regression; condicionada a DC-03/DC-04 (18.4) |
| 6 | Batching adaptativo | Requiere evidencia adicional | GAP-0.7-02 OPEN — no medible vía run_regression; condicionada a DC-07 (18.3) |

DC-06b NO resuelto en la Subfase 18.1. Es decisión de Board compartida entre Subfases 18.1-18.4. La resolución completa requiere las métricas por técnica de F0-D y las evaluaciones de las Subfases 18.3 y 18.4.

**Evidencia forense detallada:** No hay nuevos findings en §2 (Gate 4 no produjo hallazgos). La evidencia de verificación se documenta en esta sección.

---

## 4. TABLA CONSOLIDADA FINAL

{Tabla consolidada completa para Gates 1-4. Gate 4 no produjo hallazgos nuevos; la tabla permanece estable con los 6 hallazgos de Gates 1-3.}

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| CLOSED (NAR) | 1 | DF-08 |
| RESOLVED — DELETE | 1 | GF-01 |
| RESOLVED — MOVE | 1 | DF-06 |
| RESOLVED | 3 | DF-07, DF-09, DF-13 |
| IMPLEMENTATION_REQUIRED | 0 | — |
| RECLASSIFIED_FUTURE_PHASE | 0 | — |
| REVIEW_REQUIRED | 0 | — |
| ACCEPTED_LIMITATION | 0 | — |
| PENDING_REVIEW | 0 | — |

### 4.2 Tabla consolidada

| DF/GF | Estado | Decisión |
|----|--------|----------|
| DF-06 | **RESOLVED — MOVE** | Imports cruzados confirmados (Task 3.5.1) y resueltos (Task 3.5.2): runners movidos de core/benchmark/runners/ a apps/benchmark/runners/, __main__.py movido a apps/benchmark/, 2 ignore_import eliminados de pyproject.toml. Verificación: pyright 0 errors, lint-imports 4 KEPT/0 BROKEN, tests 6/6. Ver §2.1 para evidencia forense completa. |
| DF-07 | RESOLVED | RegressionTelemetryGateway creado en Wave 1.1 (Task 1.1.1). Ver §2.2 para evidencia forense completa. |
| DF-08 | CLOSED (NAR) | Falso positivo por truncamiento de pegado PowerShell. Ver §2.3 para evidencia forense completa. |
| GF-01 | **RESOLVED — DELETE** | Re-análisis en Task 3.5.3: ambos NullTelemetryAdapter son código muerto (ninguno importado; record_metric/record_event nunca llamados). core/telemetry/adapters.py eliminado; NullTelemetryAdapter canónico de ports.py conservado. Ver §2.4 para evidencia forense completa. |
| DF-09 (F18) | **RESOLVED** | Resultado contraintuitivo del benchmark de SyncProviderBridge (Wave 1.2). **Reclasificado en Gate 2 Exit Review:** la reevaluación de DC-01 exigida por DF-09 se materializó en F18_DC01_DECISION.md v1.0.0 (decisión: mantener modelo híbrido). La evidencia del benchmark fue consumida para resolver DC-01. **Nota de numeración:** DF-09 de F18 NO es el mismo hallazgo que DF-09 de Fase 17-BIS. |
| DF-13 | **RESOLVED** | Opción B (Task 3.4.2): `model_de_execution` registrado como metadata operacional (ExecutionMetadata) separada de identity_chain. R8 respetado, backward-compatible. Verificación: pyright 0 errors, tests 4/4, regresión SMOKE con execution_metadata presente en JSON. Ver §2.6 para evidencia forense completa. |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (FROZEN) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado PENDING_REVIEW
- [x] La tabla consolidada final está completa (Gates 1-4)
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [x] Los hallazgos RECLASSIFIED_FUTURE_PHASE tienen destino explícito (N/A — ninguno)
- [x] Los hallazgos REVIEW_REQUIRED tienen plan de reevaluación (N/A — ninguno)
- [x] Todos los Gates del PHASE_18.1_EXECUTION_PLAN v1.0.7 están COMPLETED
- [x] La Subfase 18.1 cumple el Global DoD definido en §5 del Execution Plan

**Estado:** Todos los criterios satisfechos. El Evidence Log queda formalmente cerrado para la Subfase 18.1.

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

**Referencias cruzadas Wave 1.1:**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-07 (RESOLVED) | §2.2 | Completo |
| DF-08 (CLOSED (NAR)) | §2.3 | Completo |
| GF-01 (RESOLVED — DELETE) | §2.4 | Completo — reclasificado en Gate 3 (Task 3.5.3) |

**Referencias cruzadas Hallazgos pre-registrados:**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-06 (RESOLVED — MOVE) | §2.1 | Completo — resuelto en Gate 3 (Task 3.5.2) |

**Referencias cruzadas Wave 1.2:**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-09 (RESOLVED) | §2.5 | Completo — reclasificado en Gate 2 (reevaluación de DC-01) |

**Referencias cruzadas Wave 2.1:**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-13 (RESOLVED) | §2.6 | Completo — resuelto en Gate 3 (Task 3.4.2, Opción B) |

**Referencias cruzadas Wave 2.2 y 2.3 (Decisiones Arquitectónicas):**

| Findings Register / DC | Evidence Log / Documento | Estado |
|---|---|---|
| DF-09 (RESOLVED) | §2.5 | Completo — reevaluación materializada en F18_DC01_DECISION.md v1.0.0 (DC-01) |
| DC-01 (RESOLVED) | F18_DC01_DECISION.md v1.0.0 | Decisión arquitectónica documentada con evidencia cuantitativa |
| DC-05 (RESOLVED) | F18_DC05_DECISION.md v1.0.0 | Decisión arquitectónica documentada (Specialized Contexts) |

**Referencias cruzadas Wave 3.4 (Identity Traceability):**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-13 (RESOLVED) | §2.6 | Completo — Opción B materializada en Task 3.4.2 (ExecutionMetadata) |

**Referencias cruzadas Wave 3.5 (Composition Refactor):**

| Findings Register | Evidence Log | Estado |
|---|---|---|
| DF-06 (RESOLVED — MOVE) | §2.1 | Completo — runners movidos a apps/benchmark/runners/, 2 ignore_import eliminados (Task 3.5.2) |
| GF-01 (RESOLVED — DELETE) | §2.4 | Completo — adapters.py eliminado tras re-análisis de código muerto (Task 3.5.3) |

**Referencias cruzadas Gate 4 (Verification & Technique Evaluation):**

| Verificación / Documento | Evidence Log | Estado |
|---|---|---|
| Static Verification NADR-F18-01 | §3.4 Wave 4.1 | Completo — pyright 0 errors, 42 tests, contrato v1.0.2 |
| Static Verification NADR-F18-02 | §3.4 Wave 4.1 | Completo — pyright 0 errors, 43 tests |
| Corrección contrato v1.0.1→v1.0.2 | §3.4 Wave 4.1 | Completo — fórmula execution_id alineada con código y NADR-F17BIS-28 |
| Dynamic Validation (bounded execution, neutralidad, isolation, frontera mecanismo/política, shutdown) | §3.4 Wave 4.2 | Completo — 854 tests, 2 ejecuciones SMOKE, grep verification isolation |
| Observación HARD_FAIL pre-existente | §3.4 Wave 4.2 | Documentada — HITO_0.7 v1.1.0, no es hallazgo de 18.1 |
| Technique Evaluation DC-06b | §3.4 Wave 4.3 | Completo — F18_DC06b_EVALUATION_REPORT.md emitido |

### 5.3 Protocolo de actualización dinámica

| Evento | Acción en este documento |
|--------|--------------------------|
| Nuevo hallazgo identificado en Execution Plan | Agregar sub-sección en §2 con estructura completa |
| Gate Exit Review ejecutado | Completar §2.{N} del finding + agregar §3.{N} |
| Finding reclasificado | Actualizar §2.{N}.9 (clasificación consolidada) + §4 |
| Batch de implementación completado | Referenciar evidencia de implementación en §2.{N}.3 |
| Fase cerrada | Estado del documento → FROZEN |

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review de la Subfase 18.1. No tiene autoridad normativa. No redefine
reglas de NADRs ni ADRs. Su único propósito es documentar la evidencia que
fundamenta cada clasificación del FASE_18_DEFERRED_FINDINGS_REGISTER, para
que futuras sesiones o fases no tengan que re-derivar conclusiones. La
autoridad de clasificación y cierre de hallazgos corresponde al Findings
Register; este documento proporciona la evidencia forense que justifica
cada clasificación.

**Cierre formal de la Subfase 18.1:** Con Gate 4 COMPLETED y todos los criterios
de cierre satisfechos, este Evidence Log pasa de IN_PROGRESS a COMPLETED. Los 6
hallazgos de Gates 1-3 tienen evidencia forense completa (§2.1-§2.6). Gate 4 no
produjo hallazgos nuevos; su evidencia de verificación se documenta en §3.4. Las
observaciones documentadas en Gate 4 que corresponden a fases futuras (HARD_FAIL
basal → 17-BIS/18.5; handlers.py → refactor futuro; DC-06b → Board 18.2-18.4)
quedan registradas aquí como trazabilidad de la Subfase 18.1, pero su resolución
corresponde a los ámbitos indicados. La Subfase 18.1 queda formalmente cerrada
con 52/52 reglas NADR DONE, 32/32 Tasks DONE, 4/4 Gates COMPLETED.