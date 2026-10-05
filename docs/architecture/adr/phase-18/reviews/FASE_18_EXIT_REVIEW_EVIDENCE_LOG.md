# FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** docs/architecture/adr/phase-18/reviews/FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md
**Versión:** 1.0.1
**Estado:** IN_PROGRESS
**Fecha:** 2026-10-04
**Última actualización:** 2026-10-05
**Derivado de:** PHASE_18.1_EXECUTION_PLAN.md v1.0.1 — Subfase 18.1 (Execution Plane & Concurrency)
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

Cada entrada de este Evidence Log tiene una referencia cruzada bidireccional con el FASE_18_DEFERRED_FINDINGS_REGISTER v1.0.1:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

---

## 2. ESTRUCTURA POR FINDING

{Estructura abierta. Se agregará una sub-sección por cada DF/GF analizado. A continuación se incluye DF-06 como hallazgo pre-registrado con estructura de análisis preparada.}

### 2.1 DF-06 — Imports cruzados core→apps (frontera hexagonal)

| Campo | Valor |
|-------|-------|
| **ID** | DF-06 |
| **Tipo** | Deferred Finding |
| **Estado** | PENDING_REVIEW |
| **Origen** | HITO_0.2 v1.2.0 (E-0.2-005); ADR_F18.1 §4; PHASE_18.1_EXECUTION_PLAN §2C.5 |
| **Gate destino original** | Gate 3 (Wave 3.5, Task 3.5.1) |
| **Estado previo** | Pre-registrado (identificado en Fase 0) |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Condicional — solo si la evaluación confirma la dependencia arquitectónica |
| **¿Bloquea la Subfase 18.1?** | No — es evaluación paralela, no bloquea DC-01 ni DC-05 |

#### 2.1.1 Texto original del DF

> *"Imports cruzados de core/benchmark/runners/ hacia apps/llm_workers y apps/bootstrap violan la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II y dificultan la evaluación independiente del modelo de concurrencia."*

#### 2.1.2 Reformulación corregida

No requiere reformulación. El texto original es preciso y está alineado con la evidencia forense de HITO_0.2 v1.2.0 (E-0.2-005).

#### 2.1.3 Archivos y documentos auditados

{Se completará durante la ejecución de Task 3.5.1. Estructura preparada:}

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | core/benchmark/runners/gemini_runner.py | Pendiente de auditoría |
| 2 | core/benchmark/runners/groq_runner.py | Pendiente de auditoría |
| 3 | apps/llm_workers/ (módulos importados) | Pendiente de auditoría |
| 4 | apps/bootstrap/ (módulos importados) | Pendiente de auditoría |
| 5 | ENGINEERING_PRINCIPLES.md §II | Frontera hexagonal: "El dominio nunca depende de la infraestructura" |
| 6 | HITO_0.2 v1.2.0 §4.2 (E-0.2-005) | Evidencia forense original del hallazgo |
| 7 | PROJECT_TREE.txt | Estructura de directorios para verificar ubicación de módulos |

#### 2.1.4 Análisis

{Se completará durante la ejecución de Task 3.5.1. Preguntas a responder:}

- ¿La condición original existe? (imports cruzados core→apps)
- ¿Es una violación normativa de ENGINEERING_PRINCIPLES §II o un comportamiento correcto por diseño?
- ¿Qué NADRs/ADRs aplican? (ENGINEERING_PRINCIPLES §II; NADR-F18-02 no es la autoridad)
- ¿Cuál es el impacto funcional real en la evaluación del modelo de concurrencia?

**Nota normativa:** La autoridad de la frontera hexagonal es ENGINEERING_PRINCIPLES §II, no NADR-F18-02. NADR-F18-02 §8 referencia esta autoridad sin redefinirla. DF-06 es una manifestación concreta que debe ser evaluada contra la autoridad correcta.

#### 2.1.5 Gaps objetivos confirmados

{Se completará durante la ejecución de Task 3.5.1.}

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Pendiente de auditoría | — | — |

#### 2.1.6 Lo que NO es un gap

{Se completará durante la ejecución de Task 3.5.1.}

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Pendiente de auditoría | — | — |

#### 2.1.7 Impacto en la Subfase 18.1

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ⏳ Pendiente | Pendiente de auditoría |
| Reproducibilidad | ⏳ Pendiente | Pendiente de auditoría |
| Corrección funcional | ⏳ Pendiente | Pendiente de auditoría |
| Bloquea DC-01 | ❌ No | DF-06 es evaluación paralela, no bloquea DC-01 |
| Bloquea DC-05 | ❌ No | DF-06 es evaluación paralela, no bloquea DC-05 |
| Bloquea Gate 4 | ⚠️ Condicional | Solo si la evaluación revela dependencia crítica |

#### 2.1.8 Sub-acciones identificadas

{Se completará durante la ejecución de Task 3.5.1.}

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-06-A | Evaluar imports cruzados core/benchmark/runners/ → apps/ | Pendiente | Benchmark |
| DF-06-B | Si se confirma: eliminar imports cruzados respetando frontera hexagonal | Pendiente | Benchmark |

#### 2.1.9 Clasificación consolidada

{Se completará durante el Gate 3 Exit Review.}

| Campo | Valor |
|-------|-------|
| Condición original existe | ⏳ Pendiente de auditoría |
| Es violación arquitectónica | ⏳ Pendiente de auditoría |
| Es violación de gobernanza | ⏳ Pendiente de auditoría |
| Es problema técnico | ⏳ Pendiente de auditoría |
| Pertenece a Subfase 18.1 | ✅ Sí (ADR_F18.1 §4, condicional) |
| Bloquea objetivo de 18.1 | ❌ No |
| Clasificación | PENDING_REVIEW |
| Prioridad | Media |

#### 2.1.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> *"Separación estricta entre el Dominio (Lógica pura, AST, Modelos) y la Infraestructura (OCR, LLMs, File I/O). El dominio nunca depende de la infraestructura."*

Esta regla aplica porque DF-06 identifica una posible dependencia de core (dominio) hacia apps (infraestructura/adaptadores). Si se confirma, la resolución implica eliminar la dependencia para restaurar la frontera hexagonal. La autoridad de clasificación y cierre corresponde al FASE_18_DEFERRED_FINDINGS_REGISTER, no a este documento.

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
| **Estado** | IMPLEMENTATION_REQUIRED |
| **Origen** | Inspección forense Wave 1.1 |
| **Gate destino original** | Gate 3 (Wave 3.5, junto con refactor de composición) |
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
| GF-01-B | Consolidar NullTelemetryAdapter en Gate 3 (Wave 3.5) | Pendiente | Gate 3 |

#### 2.4.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí (gap confirmado) |
| Es violación arquitectónica | ⚠️ Parcial (violación de Explicit over Implicit) |
| Es violación de gobernanza | ✅ Sí (conflicto de interfaces en el mismo módulo) |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.1 | ✅ Sí (consolidación en Gate 3) |
| Bloquea objetivo de 18.1 | ❌ No |
| Clasificación | IMPLEMENTATION_REQUIRED |
| Prioridad | Media |

#### 2.4.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §III (Explicit over Implicit):**
> *"Toda decisión arquitectónica debe ser explícita y trazable."*

Esta regla aplica porque la duplicación de NullTelemetryAdapter con APIs incompatibles viola el principio de explicitud. La consolidación debe hacer explícita cuál es la implementación canónica. El warning agregado en adapters.py documenta la inconsistencia hasta que se resuelva en Gate 3.

---

## 3. GATE EXIT REVIEW SUMMARY

{Estructura abierta. Se agregará una sub-sección por cada Gate Exit Review ejecutado. Ningún Gate ha sido ejecutado todavía.}

### 3.0 Estado actual

| Gate | Estado | Fecha | Hallazgos analizados |
|------|--------|-------|---------------------|
| Gate 1 — Evidence & Measurement Baseline | 🟡 Parcialmente ejecutado (Wave 1.1 de 3 completada) | 2026-10-05 | 3 (DF-07, DF-08, GF-01) |
| Gate 2 — Architectural Decisions | ⏳ No ejecutado | — | 0 |
| Gate 3 — Implementation | ⏳ No ejecutado | — | 0 (DF-06 pre-registrado, GF-01 diferido) |
| Gate 4 — Verification & Technique Evaluation | ⏳ No ejecutado | — | 0 |

### 3.1 Gate 1 Exit Review — PARCIAL (Wave 1.1 completada, 2026-10-05)

**Árbol de decisión aplicado:**

| DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-07 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | RegressionTelemetryGateway creado en Task 1.1.1 |
| DF-08 | ❌ No | N/A | N/A | CLOSED (NAR) | Falso positivo por truncamiento de pegado PowerShell |
| GF-01 | ✅ Sí | ❌ No (en Gate 1) | ✅ Sí | IMPLEMENTATION_REQUIRED | Consolidación diferida a Gate 3 |

**Resumen:**
- RESOLVED: 1 (DF-07)
- CLOSED (NAR): 1 (DF-08)
- IMPLEMENTATION_REQUIRED: 1 (GF-01)
- Nuevos hallazgos registrados: 3

**Evidencia forense detallada:** Ver §2.2 (DF-07), §2.3 (DF-08), §2.4 (GF-01).

---

## 4. TABLA CONSOLIDADA FINAL

{Se completará al cierre del último Gate Exit Review.}

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| CLOSED (NAR) | 1 | DF-08 |
| RESOLVED — DELETE | 0 | — |
| RESOLVED | 1 | DF-07 |
| IMPLEMENTATION_REQUIRED | 1 | GF-01 |
| RECLASSIFIED_FUTURE_PHASE | 0 | — |
| REVIEW_REQUIRED | 0 | — |
| ACCEPTED_LIMITATION | 0 | — |
| PENDING_REVIEW | 1 | DF-06 |

### 4.2 Tabla consolidada

| DF/GF | Estado | Decisión |
|----|--------|----------|
| DF-06 | PENDING_REVIEW | Pendiente de evaluación en Gate 3 (Task 3.5.1) |
| DF-07 | RESOLVED | RegressionTelemetryGateway creado en Wave 1.1 (Task 1.1.1). Ver §2.2 para evidencia forense completa. |
| DF-08 | CLOSED (NAR) | Falso positivo por truncamiento de pegado PowerShell. Ver §2.3 para evidencia forense completa. |
| GF-01 | IMPLEMENTATION_REQUIRED | Consolidar NullTelemetryAdapter en Gate 3 (Wave 3.5). Ver §2.4 para evidencia forense completa. |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (FROZEN) cuando:

- [ ] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [ ] Ningún hallazgo está en estado PENDING_REVIEW
- [ ] La tabla consolidada final está completa
- [ ] Cada clasificación tiene al menos una regla normativa aplicada
- [ ] Los hallazgos RECLASSIFIED_FUTURE_PHASE tienen destino explícito
- [ ] Los hallazgos REVIEW_REQUIRED tienen plan de reevaluación
- [ ] Todos los Gates del PHASE_18.1_EXECUTION_PLAN v1.0.1 están COMPLETED
- [ ] La Subfase 18.1 cumple el Global DoD definido en §5 del Execution Plan

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
| GF-01 (IMPLEMENTATION_REQUIRED) | §2.4 | Completo |
| DF-06 (PENDING_REVIEW) | §2.1 | Pendiente (Gate 3) |

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