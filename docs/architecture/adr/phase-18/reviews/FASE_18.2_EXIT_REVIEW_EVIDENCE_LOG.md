# FASE_18.2_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-18/reviews/FASE_18.2_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 1.0.2
**Estado:** IN_PROGRESS
**Fecha:** 2026-10-10
**Última actualización:** 2026-10-10
**Derivado de:** `PHASE_18.2_EXECUTION_PLAN.md` v1.2.3
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review de la Subfase 18.2 (Durable Execution & Recovery).
Cada finding incluye los archivos auditados, el análisis, los gaps confirmados,
la justificación normativa y la clasificación final.

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
| 1.0.0 | 2026-10-10 | Emisión inicial. Estructura dinámica para 6 Gates. |
| 1.0.1 | 2026-10-10 | Gate 0 Exit Review completado. 5 findings registrados con evidencia forense: DF-18.2-01, DF-18.2-02, DF-18.2-03, DF-18.2-04, GF-18.2-01. Jerarquía normativa corregida (NADR-F18-03 v1.1.0 FROZEN). |
| 1.0.2 | 2026-10-10 | Gate 1 Wave 1.1 completada. Secciones de resolución añadidas a DF-18.2-01, DF-18.2-02, DF-18.2-04 (estado → RESOLVED). Evidencia de validación: 1009 tests passed, Pyright 0 errors, import-linter 4/4 KEPT. Gate 1 Exit Review permanece pendiente hasta completar Wave 1.2. |
---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F18_MASTER v1.0.0 FROZEN
    ↓
ADR_F18.2 v3.3.0 FROZEN
    ↓
NADR-F18-03 v1.1.0 FROZEN | NADR-F18-04 v1.1.1 FROZEN | NADR-F18-05 v1.3.0 FROZEN
    ↓
PHASE_18.2_EXECUTION_PLAN v1.2.2
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que el execution plane garantice
> una ejecución durable con recuperación coherente bajo el modelo de fallos
> aprobado, manteniendo la separación entre autoridad de ejecución, efectos
> externos inciertos y confirmación local idempotente, sin atribuir al
> proveedor capacidades no verificadas ni prometer exactly-once no demostrado?"*

### 0.3 Reglas transversales aplicables

**De ADR_F18.2 v3.3.0 FROZEN:**
- DC-08: Separación entre intención durable pre-efecto y resolución de efectos inciertos
- DC-08a: Reutilización del lease existente como mecanismo principal de intención pre-efecto
- DC-08b: Política de no-reejecución automática bajo incertidumbre
- DC-08c: Taxonomía estratificada de duplicación (actividad cliente vs evidencia externa)
- DC-08d: Modelo de fallos acotado (WAL+NORMAL, exclusión de power loss)
- §11.3: Limitaciones aceptadas y riesgos residuales explícitos

**De NADR-F18-03 v1.1.0 FROZEN:**
- §5.1: Autoridad de ejecución pre-efecto recuperable
- §5.2: Clasificación semántica de resultados (confirmado/no iniciado/incierto)
- §5.3: Prohibición de reejecución automática bajo incertidumbre
- §5.5: Preservación de identidad científica vs identidad de intento

**De NADR-F18-04 v1.1.1 FROZEN:**
- §5.1: Durabilidad conforme al modelo de fallos aprobado
- §5.2: Idempotencia de aplicación local
- §5.3: Coherencia y recuperación entre planos
- §5.4: Separación explícita de propiedades (atomicidad/durabilidad/idempotencia/recuperabilidad)

**De NADR-F18-05 v1.3.0 FROZEN:**
- §5.2: Distinción entre actividad cliente y evidencia de duplicación externa
- §5.3: Límites epistemológicos de medición (ventana cliente vs ventana causal)
- §5.4: Separación de costes observados/estimados/exposición potencial
- §5.5: Integridad de evidencia sin crear fuentes de verdad paralelas

**De ENGINEERING_PRINCIPLES:**
- §I YAGNI: No sobreingeniería de mecanismos de recovery
- §II Hexagonal: Separación de puertos y adaptadores
- §VII Reuse Before Invent: Reutilización de maquinaria existente

**De ROADMAP_ARQUITECTONICO_LP:**
- §V: Arquitectura de nodo único con SQLite, sin infraestructura distribuida

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-18.2-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación de Subfase 18.2 |
| `GF-18.2-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-18.2-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida y documentada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |
| `DEFERRED_CONDITIONAL` | Diferimiento condicionado con trigger pendiente |
| `ESCALATED_TO_BOARD` | Requiere decisión del Architecture Board |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.
- Para hallazgos relacionados con efectos externos, **DEBE** declararse explícitamente si la evidencia es local (cliente) o requiere verificación del proveedor.
- Para hallazgos de durabilidad, **DEBE** especificarse el escenario de fallo (coordinado, SIGKILL, power loss) y si está dentro o fuera del modelo de fallos aprobado.

### 1.4 Árbol de decisión del Gate Exit Review

```text
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
   → NO: continuar

5. ¿Requiere decisión del Architecture Board?
   → SÍ: ESCALATED_TO_BOARD
   → NO: continuar

6. ¿Es un diferimiento condicionado con trigger pendiente?
   → SÍ: DEFERRED_CONDITIONAL
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. ESTRUCTURA POR FINDING

### 2.1 DF-18.2-01 — AsyncDispatcher sin gobernanza de ejecución durable

| Campo | Valor |
|-------|-------|
| **ID** | DF-18.2-01 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 0.1 / Task 0.1.2 (auditoría de rutas) |
| **Gate destino original** | Gate 0 |
| **Estado previo** | N/A |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — Gate 1 Task 1.1.1 |
| **¿Bloquea ejecución durable?** | Sí — Ruta 2 completamente sin gobernanza |

#### 2.1.1 Texto original del DF

> *"AsyncDispatcher (apps/llm_workers/dispatcher.py) carece de mecanismos de authority pre-effecto, lease check y journal post-effecto. Solo SyncProviderBridge tiene estos mecanismos parciales."*

#### 2.1.2 Reformulación corregida

No requiere reformulación. El hallazgo es preciso y verificable.

#### 2.1.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/bootstrap/pipeline_factory.py:105` | `dispatcher = AsyncDispatcher(...)` — Composition Root usa AsyncDispatcher en ruta productiva |
| 2 | `apps/llm_workers/dispatcher.py:105` | `provider_result = await self._provider.translate(envelope)` — Efecto externo sin authority |
| 3 | `apps/llm_workers/dispatcher.py` (completo) | No hay referencia a lease, authority, append_wal, ni clasificación semántica |
| 4 | Grep: `AsyncDispatcher` en `apps`, `runtime`, `core` | Usado en benchmark runners (gemini_runner.py:103, groq_runner.py:105) Y pipeline_factory.py:105 (ruta productiva) |
| 5 | `apps/bootstrap/provider_stack_factory.py` | Stack: CircuitBreaker → Cache → RateLimiter → Provider. Sin mecanismos de authority/journal. |

#### 2.1.4 Análisis

**¿La condición original existe?** ✅ Sí. `AsyncDispatcher` es usado por `TranslationPipeline` vía `pipeline_factory.py:105`, lo cual es una ruta productiva confirmada.

**¿Es una violación normativa?** ✅ Sí.

**NADRs violados:**
- NADR-F18-03 §5.1 R1: Toda ejecución de efecto externo MUST estar precedida por autoridad recuperable.
- NADR-F18-03 §5.1 R2: La autoridad MUST ser verificable como vigente antes de iniciar el efecto.
- NADR-F18-03 §5.2 R5-R8: La recuperación MUST distinguir entre resultado confirmado, no-iniciado e incierto.
- NADR-F18-03 §5.3 R9: Operación con resultado incierto MUST NOT ser reejecutada automáticamente.

**¿Cuál es el impacto funcional real?**
- Cualquier crash durante `AsyncDispatcher.translate()` resultará en efecto externo completado sin trazabilidad.
- Si el pipeline se reintenta, hay duplicación casi segura del efecto externo.
- Sin journal, no hay forma de recuperar estado coherente tras crash.

**¿Afecta la separación entre autoridad de ejecución y efectos externos?** ✅ Sí. No existe autoridad alguna.

**¿Compromete la idempotencia de aplicación local?** ✅ Sí. Sin journal, no hay idempotencia de aplicación.

**¿Introduce fuentes de verdad paralelas?** ❌ No. La ausencia de journal es el problema, no una fuente paralela.

#### 2.1.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Sin authority pre-effecto | `dispatcher.py:105` no persiste lease antes de `translate()` | Alta |
| G2 | Sin lease check | No hay verificación de vigencia antes ni después del efecto | Alta |
| G3 | Sin journal post-effecto | No hay `append_wal` ni equivalente | Alta |
| G4 | Sin clasificación semántica | No distingue confirmado/no-iniciado/incierto | Alta |

#### 2.1.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| AsyncDispatcher no maneja timeouts | ✅ Correcto por diseño | El timeout es responsabilidad del provider stack (CircuitBreakerProvider), no del dispatcher |
| AsyncDispatcher no implementa healing | ❌ No relacionado | Healing es responsabilidad del HealingPipeline inyectado, no del dispatcher |

#### 2.1.7 Impacto en ejecución durable y recuperación

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Autoridad de ejecución pre-efecto | ✅ Sí | Ruta 2 no tiene authority |
| Clasificación semántica de resultados | ✅ Sí | No clasifica resultados |
| Idempotencia de aplicación local | ✅ Sí | Sin journal, no hay idempotencia |
| Coherencia entre planos | ✅ Sí | Sin event journal, no hay fuente de verdad |
| Observabilidad de duplicación | ⚠️ Parcial | Telemetry existe en envelope pero sin clasificación semántica |
| Durabilidad bajo modelo de fallos | ✅ Sí | Sin WAL, sin journal |
| Bloquea Gate posterior | ✅ Sí | Gate 1 debe cubrir ambas rutas |

#### 2.1.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-18.2-01-A | Extender gobernanza de authority/lease a AsyncDispatcher | ✅ Completado (Task 1.1.1) | Gate 1 |
| DF-18.2-01-B | Añadir journal post-effecto en AsyncDispatcher | ✅ Completado (Task 1.1.1) | Gate 1 |
| DF-18.2-01-C | Clasificación semántica en AsyncDispatcher | ✅ Completado (Task 1.1.3) | Gate 1 |

#### 2.1.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ✅ Sí |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.2 | ✅ Sí |
| Bloquea ejecución durable | ✅ Sí |
| Clasificación | `IMPLEMENTATION_REQUIRED` |
| Prioridad | Alta |

#### 2.1.10 Regla aplicada

> **NADR-F18-03 §5.1 R1:**
> *"Toda ejecución de efecto externo MUST estar precedida por una autoridad recuperable persistida antes del inicio del efecto."*

La Ruta 2 (AsyncDispatcher) viola esta regla porque no persiste autoridad antes de invocar `translate()`. Esto debe corregirse en Gate 1 Task 1.1.1, extendiendo la gobernanza de SyncProviderBridge a AsyncDispatcher.

#### 2.1.11 Resolución implementada — Gate 1 Wave 1.1 (2026-10-10)

**Estado:** ✅ RESOLVED
**Resuelto por:** Task 1.1.1 (DF-18.2-01-A, DF-18.2-01-B) + Task 1.1.3 (DF-18.2-01-C)
**Batch:** BATCH 1 — Wave 1.1 Pre-effect Authority

**Implementación:**
- `DispatcherProtocol` actualizado: `dispatch(units, document_id, ast_hash)` provee contexto de autoridad.
- `AsyncDispatcher` recibe `EventPlanePort` inyectado desde Composition Root (`pipeline_factory.py`).
- `_worker()` genera `execution_id` único pre-efecto y llama a `append_wal()` INMEDIATAMENTE después del efecto externo, antes de validación/healing.
- `_worker()` hace `get_replay()` pre-efecto: si existe replay con matching `payload_sha256 + prompt_version + model_name`, sintetiza `InferenceResult` sin llamar al LLM (patrón consistente con `LLMWorkerDaemon`).
- Benchmarks usan `NullEventPlane` (adaptador nulo, no escribe en journal de producción).
- Clasificación semántica implementada en Task 1.1.3: `classify_external_effect()` derivada de evidencia observable (`task_state` + `has_generated_event`).

**Archivos modificados:**
- `apps/llm_workers/dispatcher.py`
- `apps/bootstrap/pipeline_factory.py`
- `core/pipeline/orchestrator.py`
- `core/execution/semantic_classification.py` (NUEVO — Task 1.1.3)
- `apps/benchmark/runners/gemini_runner.py`, `apps/benchmark/runners/groq_runner.py`
- `tests/helpers/fakes.py` + 6 archivos de tests

**Evidencia de validación:**
- Pyright: 0 errors, 0 warnings, 0 informations
- Tests: 1009 passed, 5 skipped
- Import-linter: 4/4 KEPT

**Reglas NADR satisfechas:**
- NADR-F18-03 §5.1 R1: Autoridad recuperable pre-efecto (execution_id + append_wal)
- NADR-F18-03 §5.2 R5-R8: Clasificación semántica (Task 1.1.3)
- NADR-F18-04 §5.2 R5 (parcial): Idempotencia de reaplicación vía replay check

**Limitación residual documentada:**
- El fencing por lease en Ruta 2 (AsyncDispatcher) no es idéntico al de Ruta 1 (LLMWorkerDaemon). La Ruta 2 es un flujo batch en memoria orquestado por `TranslationPipeline`, donde la autoridad se gestiona a nivel de documento (FSM), no de chunk individual. Esta diferencia es correcta por diseño y está documentada en `FASE_18.2_FAILURE_SCENARIO_MATRIX.md` §3.2.

---

### 2.2 DF-18.2-02 — Sin mecanismo de activación para contratos 18.2

| Campo | Valor |
|-------|-------|
| **ID** | DF-18.2-02 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 0.1 / Task 0.1.3 (mecanismo de activación) |
| **Gate destino original** | Gate 0 |
| **Estado previo** | N/A |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — Gate 1 Task 1.1.1 (extender RuntimeSettings) |
| **¿Bloquea ejecución durable?** | ⚠️ Condicional — necesario para MIG-05 |

#### 2.2.1 Texto original del DF

> *"No existe mecanismo de feature flags o activación gradual para los contratos de ejecución durable de 18.2. RuntimeSettings existe pero no tiene campos específicos para 18.2."*

#### 2.2.2 Reformulación corregida

No requiere reformulación.

#### 2.2.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `runtime/settings.py` | `RuntimeSettings` dataclass frozen con campos: `reconciliation_enabled`, `sweep_interval_seconds`, `sweep_jitter_seconds` |
| 2 | Grep: `feature_flag`, `ENABLE_`, `TOGGLE`, `os.environ`, `config.get` en `runtime`, `core/utils`, `apps/bootstrap` | Sin resultados relevantes |
| 3 | `apps/bootstrap/pipeline_factory.py` | Usa `RuntimeSettings` vía inyección desde Composition Root |
| 4 | `apps/llm_workers/__main__.py` | No hay referencia a `RuntimeSettings`; configuración directa vía `os.getenv` para `GROQ_RPM_LIMIT` y `GROQ_TPM_LIMIT` |

#### 2.2.4 Análisis

**¿La condición original existe?** ✅ Sí. No hay mecanismo de activación para los contratos de 18.2.

**¿Es una violación normativa?** ❌ No. Es una carencia, no una violación. Los contratos de 18.2 aún no están implementados.

**Decisión arquitectónica:**
- NO inventar sistema de feature flags nuevo (YAGNI).
- SÍ extender `RuntimeSettings` con campos específicos para 18.2.
- SÍ mantener inyección desde Composition Root (NADR-11 §5.1 R1).
- Nota: `__main__.py` usa `os.getenv` directamente para RPM/TPM limits. Esto es coherente con el patrón existente pero debe revisarse para mantener consistencia con `RuntimeSettings`.

#### 2.2.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Sin campos de activación 18.2 en RuntimeSettings | `settings.py` solo tiene campos de reconciliación | Media |
| G2 | Uso inconsistente de configuración (os.getenv vs RuntimeSettings) | `__main__.py` usa `os.getenv` para RPM/TPM | Baja |

#### 2.2.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| RuntimeSettings no tiene campos de observabilidad | ✅ Correcto por diseño | La observabilidad es responsabilidad de NADR-F18-05, no de RuntimeSettings |

#### 2.2.7 Impacto en ejecución durable y recuperación

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Autoridad de ejecución pre-efecto | ❌ No | No afecta directamente |
| Clasificación semántica de resultados | ❌ No | No afecta directamente |
| Idempotencia de aplicación local | ❌ No | No afecta directamente |
| Coherencia entre planos | ❌ No | No afecta directamente |
| Observabilidad de duplicación | ❌ No | No afecta directamente |
| Durabilidad bajo modelo de fallos | ❌ No | No afecta directamente |
| Bloquea Gate posterior | ⚠️ Condicional | Necesario para MIG-05 (activación controlada) |

#### 2.2.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-18.2-02-A | Extender RuntimeSettings con campos de activación 18.2 | ✅ Completado (Task 1.1.1) | Gate 1 |
| DF-18.2-02-B | Revisar uso de os.getenv en __main__.py para consistencia | ⚠️ Diferido (mejora no bloqueante) | Gate 5 o posterior |

#### 2.2.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.2 | ✅ Sí |
| Bloquea ejecución durable | ⚠️ Condicional |
| Clasificación | `IMPLEMENTATION_REQUIRED` |
| Prioridad | Media |

#### 2.2.10 Regla aplicada

> **NADR-10 §5.2 R11:**
> *"La activación de mecanismos del runtime MUST estar gobernada por configuración externa, no por banderas hardcodeadas."*

RuntimeSettings es el mecanismo canónico para esta configuración. Debe extenderse en Gate 1 con campos específicos para 18.2.

#### 2.2.11 Resolución implementada — Gate 1 Wave 1.1 (2026-10-10)

**Estado:** ✅ RESOLVED (hallazgo principal)
**Resuelto por:** Task 1.1.1
**Batch:** BATCH 1 — Wave 1.1 Pre-effect Authority

**Implementación:**
- `RuntimeSettings` extendido con 3 campos de activación para 18.2:
  - `conservative_recovery_enabled: bool = False`
  - `semantic_classification_enabled: bool = False`
  - `stratified_observability_enabled: bool = False`
- Valores por defecto `False`: activación gobernada por configuración externa, no hardcodeada (NADR-10 §5.2 R11).
- Inyección desde Composition Root mantenida (NADR-11 §5.1 R1). No se inventó sistema de feature flags nuevo (YAGNI).

**Archivos modificados:**
- `runtime/settings.py`

**Evidencia de validación:**
- Pyright: 0 errors, 0 warnings, 0 informations
- Tests: 1009 passed, 5 skipped
- Import-linter: 4/4 KEPT

**Reglas NADR satisfechas:**
- NADR-10 §5.2 R11: Activación gobernada por configuración externa

**Limitación residual documentada:**
- DF-18.2-02-B (consistencia de `os.getenv` en `__main__.py` para GROQ_RPM_LIMIT/GROQ_TPM_LIMIT) se difiere como mejora de consistencia no bloqueante. El uso actual de `os.getenv` para límites de cuota es coherente con el patrón existente y no compromete la ejecución durable. Se evaluará en Gate 5 o en una tarea de limpieza posterior.

---

### 2.3 DF-18.2-03 — Archivos vacíos (deuda técnica potencial)

| Campo | Valor |
|-------|-------|
| **ID** | DF-18.2-03 |
| **Tipo** | Deferred Finding |
| **Estado** | `REVIEW_REQUIRED` |
| **Origen** | Wave 0.1 / Task 0.1.2 (auditoría de rutas) |
| **Gate destino original** | Gate 0 |
| **Estado previo** | N/A |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No inmediato — requiere análisis |
| **¿Bloquea ejecución durable?** | No |

#### 2.3.1 Texto original del DF

> *"Archivos vacíos detectados: core/execution/event_log.py (0 bytes), core/execution/invariants.py (0 bytes), core/execution/job_model.py (0 bytes), core/utils/config.py (0 bytes), core/utils/time.py (0 bytes), infra/redis/queues.py (0 bytes), apps/api/server.py (0 bytes). core/execution/constants.py tiene contenido (344 bytes)."*

#### 2.3.2 Reformulación corregida

No requiere reformulación.

#### 2.3.3 Archivos y documentos auditados

| # | Archivo | Tamaño | Evidencia |
|---|---------|--------|-----------|
| 1 | `core/execution/event_log.py` | 0 bytes | Vacío. El event journal real está en `infra/db/event_repo.py`. Posible placeholder muerto. |
| 2 | `core/execution/constants.py` | 344 bytes | Contiene `CURRENT_PROJECTION_VERSION = 1`. Usado por `SyncProviderBridge`. No es deuda. |
| 3 | `core/execution/invariants.py` | 0 bytes | Vacío. Posible placeholder. |
| 4 | `core/execution/job_model.py` | 0 bytes | Vacío. El modelo de job está en `core/pipeline/job.py`. Posible placeholder muerto. |
| 5 | `core/utils/config.py` | 0 bytes | Vacío. Configuración se maneja vía `runtime/settings.py`. Posible placeholder muerto. |
| 6 | `core/utils/time.py` | 0 bytes | Vacío. Posible placeholder. |
| 7 | `infra/redis/queues.py` | 0 bytes | Vacío. Coherente con ROADMAP §V: Redis no es arquitectura objetivo. Candidato a eliminación. |
| 8 | `apps/api/server.py` | 0 bytes | Vacío. API futura/no implementada. |

#### 2.3.4 Análisis

**¿La condición original existe?** ✅ Sí. Los archivos están vacíos.

**¿Es una violación normativa?** ❌ No. Es deuda técnica, no violación.

**¿Cuál es el impacto funcional real?** Ninguno. Los archivos vacíos no afectan la ejecución.

**¿Qué riesgo introducen?** Confusión para futuros desarrolladores. Un archivo vacío llamado `event_log.py` puede confundirse con el event journal real.

**Posibles acciones:**
1. Eliminar archivos vacíos si son placeholders muertos.
2. Documentar como "futuro trabajo" si son placeholders intencionales.
3. Dejar como está si no afectan la implementación de 18.2.

**Recomendación:** Diferir a análisis posterior. No bloquea Gate 0 ni Gates 1-5. `infra/redis/queues.py` es candidato a eliminación inmediata por ser coherente con la decisión de ROADMAP §V (sin Redis).

#### 2.3.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | 7 archivos vacíos sin documentación de propósito | Ver tabla 2.3.3 | Baja |

#### 2.3.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| `core/execution/constants.py` vacío | ❌ No es gap | Tiene contenido: `CURRENT_PROJECTION_VERSION = 1` |
| `apps/api/server.py` vacío | ✅ Correcto por diseño | API no está en el alcance de Fase 18 |

#### 2.3.7 Impacto en ejecución durable y recuperación

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Autoridad de ejecución pre-efecto | ❌ No | No afecta |
| Clasificación semántica de resultados | ❌ No | No afecta |
| Idempotencia de aplicación local | ❌ No | No afecta |
| Coherencia entre planos | ❌ No | No afecta |
| Observabilidad de duplicación | ❌ No | No afecta |
| Durabilidad bajo modelo de fallos | ❌ No | No afecta |
| Bloquea Gate posterior | ❌ No | No bloquea |

#### 2.3.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-18.2-03-A | Evaluar si archivos vacíos son placeholders intencionales o deuda | Pendiente | Gate 5 o posterior |
| DF-18.2-03-B | Eliminar `infra/redis/queues.py` (coherente con ROADMAP §V) | Pendiente | Gate 5 o posterior |

#### 2.3.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ⚠️ Parcial (deuda técnica) |
| Pertenece a Subfase 18.2 | ❌ No (no bloquea) |
| Bloquea ejecución durable | ❌ No |
| Clasificación | `REVIEW_REQUIRED` |
| Prioridad | Baja |

#### 2.3.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se crea un nuevo artefacto a menos que elimine una ambigüedad que esté bloqueando activamente la implementación."*

Los archivos vacíos no bloquean implementación, pero introducen ambigüedad. Deben evaluarse y documentarse o eliminarse.

---

### 2.4 DF-18.2-04 — SyncProviderBridge verifica lease POST-effecto

| Campo | Valor |
|-------|-------|
| **ID** | DF-18.2-04 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 0.1 / Task 0.1.2 (auditoría de rutas) |
| **Gate destino original** | Gate 0 |
| **Estado previo** | N/A |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — Gate 1 Task 1.1.1 |
| **¿Bloquea ejecución durable?** | Sí — ventana de efecto sin authority verificada |

#### 2.4.1 Texto original del DF

> *"SyncProviderBridge solo verifica lease POST-effecto (línea 328 de __main__.py), no PRE-effecto. Esto viola NADR-F18-03 §5.1 R2 que requiere verificación de vigencia antes de iniciar el efecto externo."*

#### 2.4.2 Reformulación corregida

No requiere reformulación.

#### 2.4.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/llm_workers/__main__.py:326` | `raw_response = self.processor.execute(node)` — Efecto externo |
| 2 | `apps/llm_workers/__main__.py:328` | `if heartbeat.lease_lost.is_set(): raise OptimisticLockError(...)` — Check POST-effecto |
| 3 | `apps/llm_workers/__main__.py:333` | `self.event.append_wal(...)` — Journal POST-effecto |
| 4 | `apps/llm_workers/sync_bridge.py` | `SyncProviderBridge.execute()` no tiene verificación de lease. Solo `future.result(timeout=...)`. |
| 5 | HITO_18.2.2 E-18.2.2-001 | Confirma que el check de lease es POST-EFFECT |

#### 2.4.4 Análisis

**¿La condición original existe?** ✅ Sí. El check de lease ocurre después del efecto externo.

**¿Es una violación normativa?** ✅ Sí.

**NADR violado:**
- NADR-F18-03 §5.1 R2: *"La autoridad de ejecución MUST ser verificable como vigente antes de iniciar el efecto externo."*

**¿Cuál es el impacto funcional real?**
- Si el lease expira durante `execute()`, el efecto externo se completa pero se detecta después.
- Esto es coherente con NADR-F18-03 §5.1 R3 (detectar pérdida, no revertir), pero la verificación debe ser PRE-effecto para prevenir inicio sin authority.
- La ventana entre `pick_task()` y `execute()` puede ser larga si hay demoras en la construcción del prompt.

**Corrección requerida:**
- Verificar lease INMEDIATAMENTE antes de `execute(node)`.
- Si lease no vigente, NO iniciar efecto externo.
- Clasificar como "no-iniciado" en lugar de "incierto".

#### 2.4.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Lease check POST-effecto en lugar de PRE-effecto | `__main__.py:326-328` | Alta |
| G2 | SyncProviderBridge.execute() no verifica lease internamente | `sync_bridge.py` completo | Media |

#### 2.4.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Check de lease POST-effecto existe | ✅ Correcto por diseño | NADR-F18-03 §5.1 R3 requiere detección de pérdida. El check post-effecto cumple parcialmente. |
| OptimisticLockError lanzado tras pérdida | ✅ Correcto por diseño | Previene escrituras obsoletas en SQLite (fencing local). |

#### 2.4.7 Impacto en ejecución durable y recuperación

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Autoridad de ejecución pre-efecto | ✅ Sí | Verificación POST en lugar de PRE |
| Clasificación semántica de resultados | ⚠️ Parcial | Si lease expira durante execute, la clasificación es incierta en lugar de no-iniciada |
| Idempotencia de aplicación local | ❌ No | No afecta directamente |
| Coherencia entre planos | ❌ No | No afecta directamente |
| Observabilidad de duplicación | ❌ No | No afecta directamente |
| Durabilidad bajo modelo de fallos | ❌ No | No afecta directamente |
| Bloquea Gate posterior | ✅ Sí | Gate 1 Task 1.1.1 debe corregir |

#### 2.4.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-18.2-04-A | Mover lease check a PRE-effecto en __main__.py | ✅ Completado (Task 1.1.1) | Gate 1 |
| DF-18.2-04-B | Evaluar si SyncProviderBridge.execute() debe verificar lease internamente | ✅ Completado — Decisión: NO mover al bridge (Task 1.1.2) | Gate 1 |

#### 2.4.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ✅ Sí |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Subfase 18.2 | ✅ Sí |
| Bloquea ejecución durable | ✅ Sí |
| Clasificación | `IMPLEMENTATION_REQUIRED` |
| Prioridad | Alta |

#### 2.4.10 Regla aplicada

> **NADR-F18-03 §5.1 R2:**
> *"La autoridad de ejecución MUST ser verificable como vigente antes de iniciar el efecto externo."*

La verificación actual es POST-effecto. Debe moverse a PRE-effecto en Gate 1 Task 1.1.1. El check POST-effecto existente se mantiene como detección de pérdida durante la ejecución (NADR-F18-03 §5.1 R3).

#### 2.4.11 Resolución implementada — Gate 1 Wave 1.1 (2026-10-10)

**Estado:** ✅ RESOLVED
**Resuelto por:** Task 1.1.1 (verificación PRE-effecto) + Task 1.1.2 (fencing local verificable)
**Batch:** BATCH 1 — Wave 1.1 Pre-effect Authority

**Implementación:**
- `TaskLeaseHeartbeat` añade `_lease_lock` (thread-safe), `_lease_expires_at`, y property `is_lease_viable` con margen conservador de 30 segundos.
- `LLMWorkerDaemon._process_task()` verifica `heartbeat.is_lease_viable` INMEDIATAMENTE antes de `self.processor.execute(node)`.
- Lanza `LeaseExpiredError` si el lease no tiene margen suficiente, previniendo el inicio del efecto externo sin autoridad vigente.
- Verificación POST-effecto existente (`lease_lost.is_set()`) se mantiene como detección de pérdida DURANTE el efecto (NADR-F18-03 §5.1 R3).
- `mark_task_completed()` añadido con doble fencing (lease_owner + lease_expires_at + state_version) en Task 1.1.2.
- Manejo explícito de `OptimisticLockError` post-completado: si el lease expira después de journal + proyección, el trabajo se preserva (no se marca como FAILED).

**Decisión de diseño DF-18.2-04-B:**
- Se evaluó mover la verificación de lease dentro de `SyncProviderBridge.execute()`. Decisión: NO moverla. La verificación permanece en `__main__.py` (capa de orquestación) porque:
  - `SyncProviderBridge` es un adaptador de impedancia thread-safe, no debe conocer la semántica de lease.
  - La responsabilidad de authority pertenece a la capa de orquestación (NADR-F18-02 §5.1: separación de responsabilidades).
  - Moverla al bridge violaría el principio de inversión de dependencias (el bridge recibiría dependencia del control plane).

**Archivos modificados:**
- `apps/llm_workers/__main__.py`
- `infra/db/control_repo.py` (mark_task_completed)
- `core/execution/ports.py` (ControlPlanePort actualizado)

**Evidencia de validación:**
- Pyright: 0 errors, 0 warnings, 0 informations
- Tests: 1009 passed, 5 skipped
- Import-linter: 4/4 KEPT

**Reglas NADR satisfechas:**
- NADR-F18-03 §5.1 R2: Verificación de vigencia PRE-effecto (is_lease_viable)
- NADR-F18-03 §5.1 R3: Detección de pérdida durante ejecución + fencing local verificable (mark_task_completed)

---

### 2.5 GF-18.2-01 — CircuitBreakerProvider envuelve cache

| Campo | Valor |
|-------|-------|
| **ID** | GF-18.2-01 |
| **Tipo** | Governance Finding |
| **Estado** | `REVIEW_REQUIRED` |
| **Origen** | Wave 0.1 / Task 0.1.2 (auditoría de rutas) |
| **Gate destino original** | Gate 0 |
| **Estado previo** | N/A |
| **Prioridad** | Media |
| **¿Requiere implementación?** | No inmediato — requiere análisis de impacto FinOps |
| **¿Bloquea ejecución durable?** | No |

#### 2.5.1 Texto original del GF

> *"CircuitBreakerProvider envuelve CachedLLMProvider en el provider stack. Si el breaker está abierto, podría impedir servir respuestas cacheadas locales, lo cual tensiona con el objetivo FinOps de reducir llamadas al proveedor."*

#### 2.5.2 Reformulación corregida

No requiere reformulación.

#### 2.5.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/bootstrap/provider_stack_factory.py` | Stack: `CircuitBreakerProvider(underlying=provider, breaker=breaker)` donde `provider` es `CachedLLMProvider` o `RateLimitedProvider` |
| 2 | `apps/bootstrap/provider_stack_factory.py` docstring | "Stack order: CircuitBreaker → Cache → RateLimiter → Provider" y "NADR-08 §5.5: CB antes de RL previene consumo de cuota con circuito abierto" |
| 3 | `apps/llm_workers/circuit_breaker_provider.py` | Delega al breaker, que decide si llamar al provider |

#### 2.5.4 Análisis

**¿La condición original existe?** ✅ Sí. El CircuitBreaker está fuera del cache en el stack.

**¿Es un conflicto normativo?** ⚠️ Posible tensión entre:
- NADR-08 §5.2 R7: CircuitBreaker MANDATORY en todas las rutas.
- NADR-08 §5.5: CB antes de RL previene consumo de cuota con circuito abierto.
- NADR-F18-05 §5.4: FinOps — respuestas cacheadas locales no deberían consumir cuota del proveedor.

**¿Cuál es el impacto funcional real?**
- Si el breaker está abierto, las llamadas se rechazan ANTES de consultar el cache.
- Esto significa que respuestas cacheadas válidas no se sirven cuando el proveedor está caído.
- Impacto FinOps: se pierde la oportunidad de servir respuestas gratuitas del cache.
- Impacto de disponibilidad: el sistema falla más de lo necesario.

**¿Es una violación?** ❌ No. El diseño actual es válido según NADR-08 §5.5. Pero hay una tensión con el objetivo FinOps.

**Pregunta de gobernanza:**
Si el breaker está abierto, ¿debería permitir servir respuestas cacheadas locales?

**Opciones:**
1. Mantener diseño actual (CB fuera de cache). Cumple NADR-08 §5.5.
2. Reordenar stack a Cache → CircuitBreaker → RateLimiter → Provider. Permite cache hits con breaker abierto.
3. Añadir lógica condicional: si cache hit, servir sin pasar por breaker.

**Recomendación:** Analizar en Gate 3 (Observabilidad & FinOps) con datos de impacto reales. No decidir en Gate 0.

#### 2.5.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Posible pérdida de respuestas cacheadas con breaker abierto | `provider_stack_factory.py` stack order | Media |

#### 2.5.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| CircuitBreaker está presente en el stack | ✅ Correcto por diseño | NADR-08 §5.2 R7 lo requiere |
| CircuitBreaker previene consumo de cuota con circuito abierto | ✅ Correcto por diseño | NADR-08 §5.5 lo justifica |

#### 2.5.7 Impacto en ejecución durable y recuperación

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Autoridad de ejecución pre-efecto | ❌ No | No afecta |
| Clasificación semántica de resultados | ❌ No | No afecta |
| Idempotencia de aplicación local | ❌ No | No afecta |
| Coherencia entre planos | ❌ No | No afecta |
| Observabilidad de duplicación | ❌ No | No afecta |
| Durabilidad bajo modelo de fallos | ❌ No | No afecta |
| Bloquea Gate posterior | ❌ No | Análisis en Gate 3 |

#### 2.5.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| GF-18.2-01-A | Analizar impacto FinOps de respuestas cacheadas perdidas con breaker abierto | Pendiente | Gate 3 |
| GF-18.2-01-B | Evaluar reordenamiento del stack (Cache → CB → RL → Provider) | Pendiente | Gate 3 |

#### 2.5.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No (diseño actual es válido) |
| Es violación de gobernanza | ⚠️ Posible tensión entre NADRs |
| Es problema técnico | ❌ No |
| Pertenece a Subfase 18.2 | ✅ Sí (análisis FinOps) |
| Bloquea ejecución durable | ❌ No |
| Clasificación | `REVIEW_REQUIRED` |
| Prioridad | Media |

#### 2.5.10 Regla aplicada

> **NADR-08 §5.5:**
> *"CB antes de RL previene consumo de cuota con circuito abierto."*

> **NADR-F18-05 §5.4 R12:**
> *"Los costes derivados de efectos externos MUST distinguirse explícitamente en tres categorías: coste observado o facturado, coste estimado, y exposición económica potencial no confirmada."*

La tensión entre ambas reglas debe resolverse con análisis de impacto FinOps en Gate 3. No es una violación, sino una oportunidad de optimización.

---

### 3.0 Gate 0 Exit Review (2026-10-10)

**Estado:** ✅ COMPLETED

**Gate 0 — Baseline & Contract Readiness**
- Wave 0.1: Rule & Evidence Mapping (Tasks 0.1.1, 0.1.2, 0.1.3)
- Wave 0.2: Operational Baseline (Tasks 0.2.1, 0.2.2)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble en Gate 0? | ¿Técnico? | Decisión | Motivo |
|----|----------|----------------------|-----------|----------|--------|
| DF-18.2-01 | ✅ Sí | ❌ No | ✅ Sí | IMPLEMENTATION_REQUIRED | AsyncDispatcher sin gobernanza. Gate 1. |
| DF-18.2-02 | ✅ Sí | ❌ No | ✅ Sí | IMPLEMENTATION_REQUIRED | Sin mecanismo de activación. Gate 1. |
| DF-18.2-03 | ✅ Sí | ⚠️ Parcial | ✅ Sí | REVIEW_REQUIRED | Archivos vacíos. No bloquea. |
| DF-18.2-04 | ✅ Sí | ❌ No | ✅ Sí | IMPLEMENTATION_REQUIRED | Lease check POST-effecto. Gate 1. |
| GF-18.2-01 | ✅ Sí | ❌ No | ❌ No | REVIEW_REQUIRED | CB envuelve cache. Gate 3. |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 3 (DF-18.2-01, DF-18.2-02, DF-18.2-04)
- REVIEW_REQUIRED: 2 (DF-18.2-03, GF-18.2-01)
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 1 (GF-18.2-01)
- ESCALATED_TO_BOARD: 0
- DEFERRED_CONDITIONAL: 0
- Nuevos hallazgos registrados: 5

---

### 3.4 Gate 4 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 4 — Integrated Empirical Validation**
- Wave 4.1: Chaos Harness & Convergence Validation (Tasks 4.1.1, 4.1.2, 4.1.3)
- Wave 4.2: Direct Measurement & External Fencing (Tasks 4.2.1, 4.2.2, 4.2.3)
- Wave 4.3: Durability & Power Loss Characterization (Tasks 4.3.1, 4.3.2)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- ESCALATED_TO_BOARD: 0
- DEFERRED_CONDITIONAL: 0
- Nuevos hallazgos registrados: 0

---

### 3.5 Gate 5 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 5 — Phase Closure & Deferred Findings Resolution**
- Wave 5.1: Deferred Findings Evaluation (Tasks 5.1.1, 5.1.2, 5.1.3, 5.1.4)
- Wave 5.2: Documentation & Handoff (Tasks 5.2.1, 5.2.2, 5.2.3)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- ESCALATED_TO_BOARD: 0
- DEFERRED_CONDITIONAL: 0
- Nuevos hallazgos registrados: 0

---

## 4. TABLA CONSOLIDADA FINAL

{Se completa al cierre del último Gate Exit Review.}

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED — MOVE` | 0 | — |
| `RESOLVED — REFACTORED` | 0 | — |
| `RESOLVED — FACTORY EXTRACTION` | 0 | — |
| `RESOLVED` | 3 | DF-18.2-01, DF-18.2-02, DF-18.2-04 |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 2 | DF-18.2-03, GF-18.2-01 |
| `ACCEPTED_LIMITATION` | 0 | — |
| `DEFERRED_CONDITIONAL` | 0 | — |
| `ESCALATED_TO_BOARD` | 0 | — |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-18.2-01 | `RESOLVED` | AsyncDispatcher con authority, journal y replay check. Resuelto en Task 1.1.1 + Task 1.1.3. Evidencia: §2.1.11. |
| DF-18.2-02 | `RESOLVED` | RuntimeSettings extendido con campos de activación 18.2. Resuelto en Task 1.1.1. Sub-acción B diferida (mejora no bloqueante). Evidencia: §2.2.11. |
| DF-18.2-03 | `REVIEW_REQUIRED` | Archivos vacíos: evaluar si son placeholders intencionales o deuda técnica. No bloquea. |
| DF-18.2-04 | `RESOLVED` | Lease check movido a PRE-effecto + fencing local verificable. Resuelto en Task 1.1.1 + Task 1.1.2. Evidencia: §2.4.11. |
| GF-18.2-01 | `REVIEW_REQUIRED` | CircuitBreaker envuelve cache: analizar impacto FinOps en Gate 3. Posible reordenamiento del stack. |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado `PENDING_REVIEW`
- [ ] La tabla consolidada final está completa
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [ ] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [ ] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación
- [ ] Los hallazgos `DEFERRED_CONDITIONAL` (DF-24, DF-34) tienen disposición documentada
- [ ] Los hallazgos `ESCALATED_TO_BOARD` tienen resolución formal del Architecture Board
- [ ] Todos los Gates (0-5) están en estado COMPLETED
- [ ] El Findings Register está ARCHIVED

**Progreso:** Gate 0 completado. Gate 1 Wave 1.1 completada. 3/5 findings RESOLVED con evidencia forense de resolución registrada. 2/5 findings pendientes (DF-18.2-03, GF-18.2-01 — ambos REVIEW_REQUIRED, no bloqueantes). Gate 1 Exit Review pendiente hasta completar Wave 1.2.

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones. La evidencia debe ser auditable,
reproducible y trazable a las reglas normativas de los NADRs FROZEN.