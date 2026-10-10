# HITO_18.2.1_CRASH_WINDOW_FINOPS_ANALYSIS.md

**Estado:** FROZEN v1.2.0
**Fecha de emisión original:** 2026-10-09
**Fecha de enmienda v1.1.0:** 2026-10-09
**Fecha de enmienda v1.2.0:** 2026-10-09
**Fecha de congelamiento:** 2026-10-09
**Fase:** Fase 18 (Advanced Local Runtime) — Subfase 18.2 (Durable Execution & Recovery)
**Tipo de artefacto:** Forensic Discovery + Experimental Characterization
**Naturaleza:** Read-only + evidencia experimental preregistrada
**Supersede:** HITO_18.2.1 v1.1.0 FROZEN y v1.0.0 FROZEN

**Advertencia epistemológica:** Este HITO combina observación forense de código con evidencia experimental de un harness controlado (`prueba_18.py`). Las mediciones están acotadas por las condiciones del experimento (mock LLM 25ms, inyección artificial de crash, SQLite local). La extrapolación a producción requiere supuestos explícitos declarados en cada sección. Este documento NO certifica el cumplimiento integral de INV-JOURNAL; proporciona evidencia para decisiones acotadas.

**Evidencia Forense Vinculante:**
- HITO_18.2.0 v1.3.0 FROZEN (superficie durable auditada, clasificación P1 de GAP-18.2.0-01)
- ADR_F18_MASTER v1.0.0 FROZEN (§5.1 invariantes, §6.2 subfases, §8.2 DC Log, §8.3 Deferred Findings)
- NADR-F18-01 v1.0.3 FROZEN, NADR-F18-02 v1.0.1 FROZEN
- F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 FROZEN
- Experimento `prueba_18.py` ejecutado 2026-10-09 (resultados en `harness_report.json`)
- Auditoría A.1-A.7 ejecutada 2026-10-09 (resultados en este documento)

**Código auditado:** infra/db/event_repo.py, infra/db/materialized_repo.py, infra/db/control_repo.py, infra/db/fsm_repository.py, core/document_profile/profiler.py, core/document_profile/models.py, core/document_profile/service.py, apps/llm_workers/circuit_breaker_provider.py, apps/bootstrap/provider_stack_factory.py, apps/daemons/reconciler.py, apps/daemons/chaos_runner.py, runtime/recovery.py, runtime/resumer.py, core/pipeline/engine.py, infra/db/bootstrap.py, infra/db/connection.py, infra/db/sqlite_rate_limit_store.py, apps/llm_workers/rate_limiter.py, apps/compiler/tectonic_runner.py, infra/extraction/providers/, core/benchmark/profiles.py, tools/evaluation/run_regression.py, core/telemetry/gateway.py, tests/integration/test_recovery_flow.py, tests/test_resilient_provider.py, tests/test_recovery_determinability.py, tests/test_pipeline_fsm_emission.py

**Mandato:** Caracterizar experimentalmente las crash windows del execution plane y cuantificar el impacto FinOps de la ventana post-effect/pre-journal. Responder las 7 preguntas abiertas de HITO_18.2.0 v1.3.0 §20 con evidencia experimental.

**Síntesis:** El experimento demuestra que: (1) la duración total execute→append_wal observada es ~26ms (incluye latencia LLM mock); la ventana pura post-effect/pre-journal es inferida como ~1ms por resta, pero no medida directamente; (2) bajo inyección artificial de crash, la tasa de duplicación es 50% (10/20 tareas re-ejecutadas); (3) fencing por optimistic locking es EFECTIVO para operaciones SQL (worker zombi bloqueado, legítimo funciona); frontera externa NO DEMOSTRADA; (4) coste FinOps: $1,312.50/mes con 1000 tareas/día al 50% de tasa de crash artificial (corregido de v1.1.0). ProfileStore: re-inferencia sin coste de tokens LLM; coste de CPU no cuantificado. CircuitBreaker: warm-up estimado en ~60s basado en configuración, no medido experimentalmente. Telemetría: operational state (no participa en recovery). SQLite NORMAL: durabilidad ante crash de proceso OBSERVADA, power loss NO DEMOSTRADO. Recovery end-to-end y convergencia global: NO DEMOSTRADAS en este hito (requieren Gate 4).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-09 | Emisión inicial. Auditoría forense sin experimento. |
| 1.0.0-FROZEN | 2026-10-09 | Cierre formal. Basado en HITO_18.2.0 v1.0.0 (obsoleta). |
| 1.1.0-FROZEN | 2026-10-09 | Enmienda mayor: incorporación de evidencia experimental real, auditoría A.1-A.7, corrección P0→P1. |
| 1.2.0-FROZEN | 2026-10-09 | **Enmienda de corrección material:** (1) Corrección de error aritmético FinOps: $131.25/mes → $1,312.50/mes (factor 10). (2) Reformulación de ventana temporal: "duración observada" en lugar de "acotada y estable"; ventana pura ~1ms reclasificada como inferencia, no medición directa. (3) Eliminación de afirmación "idempotencia integral DEMOSTRADA"; mantenida como "idempotencia por operación OBSERVADA". (4) Acotación de veredicto fencing: "fencing SQL demostrado; frontera externa no demostrada". (5) Declaración explícita de C_recovery y F_convergencia como NO DEMOSTRADAS en este hito. (6) Reclasificación de estimaciones: ProfileStore "sin coste de tokens LLM; coste de CPU no cuantificado"; CircuitBreaker "~60s estimado basado en configuración, no medido". (7) Corrección de cierre de hipótesis: reclasificación de hipótesis abiertas y pendientes de decisión. |

---

## 1. RESUMEN EJECUTIVO

Se completó la caracterización experimental parcial de crash windows, idempotencia por operación, fencing SQL, y cuantificación FinOps. La auditoría combinó observación forense de código (A.1-A.7) con experimento controlado (`prueba_18.py`, 50 muestras por escenario, mock LLM 25ms).

**Hallazgo central:**

> La duración total execute→append_wal observada bajo condiciones del experimento es ~26ms (P50=25.97ms, P99=26.63ms, incluye latencia LLM mock). La ventana pura post-effect/pre-journal es **inferida** como ~1ms por resta (26ms - 25ms mock), pero **no medida directamente**. Bajo inyección artificial de crash post-effect, la tasa de duplicación observada es 50% (10/20 tareas). **Fencing por optimistic locking es EFECTIVO para operaciones SQL** (worker zombi bloqueado, legítimo funciona); frontera externa (prevención de llamadas LLM post-loss) **NO DEMOSTRADA**. Coste FinOps: $1,312.50/mes a 1000 tareas/día con tasa de crash artificial del 50% (corregido de v1.1.0). **Ni la violación estructural de INV-JOURNAL ni su cumplimiento integral están demostrados**: la ventana existe, la idempotencia existe por operación, pero la idempotencia integral del flujo completo y la medición de frecuencia natural de duplicación quedan pendientes.

**Defectos dominantes confirmados con evidencia:**

1. **Ventana post-effect/pre-journal (GAP-18.2.0-01, P1):** Duración total observada P50=25.97ms (incluye LLM mock). Ventana pura inferida ~1ms, no medida directamente. Idempotencia de `append_wal` OBSERVADA por operación. Tasa de duplicación bajo crash artificial: 50%. Coste FinOps: $0.0875/llamada duplicada. Requiere Board decision sobre mecanismo (Intent-First Journal) vs aceptación formal.

2. **ProfileStore in-memory (GAP-18.2.0-02, P2→RECOMENDACIÓN):** Re-inferencia heurística sin coste de tokens LLM. Coste de CPU no cuantificado (sin benchmark). Reconstrucción determinista OBSERVADA en código. Clasificación final: ACCEPTED_LIMITATION (recomendación, no decisión tomada).

3. **CircuitBreaker in-memory (GAP-18.2.0-03, P2):** Warm-up estimado en ~60s basado en configuración (5 fallos × ventana de 60s), no medido experimentalmente. Board decision pendiente.

4. **Fencing por optimistic locking (GAP-18.2.0-05, P1→PARCIALMENTE RESUELTO):** DEMOSTRADO para operaciones SQL (worker zombi bloqueado, legítimo funciona). NO DEMOSTRADO para frontera de proveedor externo (worker obsoleto que llama LLM tras perder lease). Cobertura en tests: test_recovery_flow.py, test_recovery_determinability.py, test_resilient_provider.py, test_pipeline_fsm_emission.py, game_day_1_crash_consistency (observado en chaos_runner.py). test_fencing.py NO existe pero hay cobertura equivalente parcial.

5. **Write-policy SQLite (GAP-18.2.0-06, P2):** Durabilidad ante crash de proceso OBSERVADA. Durabilidad ante power loss NO DEMOSTRADA (cero tests en A.6).

6. **Recovery end-to-end y convergencia global (GAP-18.2.1-02, GAP-18.2.1-03, P2):** NO DEMOSTRADAS en este hito. Campos C_recovery y F_convergencia vacíos en reporte experimental. Requieren Gate 4 del Execution Plan (game_day_1 completo).

**Veredicto:** Este HITO proporciona evidencia experimental **parcial** suficiente para que ADR_F18.2 tome decisiones informadas sobre DC-08, DF-24 y DF-34, con la advertencia explícita de que recovery end-to-end, convergencia global, fencing frontera externa y power loss permanecen NO DEMOSTRADAS. Ningún destino arquitectónico se declara resuelto por el HITO; las decisiones corresponden al Board. ADR_F18.2 puede emitirse con HITO_18.2.0 v1.3.0 y HITO_18.2.1 v1.2.0 como insumos, declarando explícitamente las condiciones de validación pendientes.

**Estado de preparación:** HITO_18.2.1 v1.2.0 FROZEN. ADR_F18.2 puede emitirse con condiciones de validación explícitas. Gate 4 del Execution Plan debe ejecutar experimentos adicionales (game_day_1 completo, fencing de frontera externa, power loss, medición directa de ventana pura).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO

### 2.1 Límite epistemológico

Este HITO combina dos tipos de evidencia:

| Tipo | Definición | Aplicación |
|---|---|---|
| **OBSERVADO** (código) | Inspección directa del fuente | Idempotencia por operación, fencing SQL, granularidad, ProfileStore sin LLM |
| **DEMOSTRADO** (experimental) | Evidencia reproducible bajo condiciones declaradas | Duración total ~26ms, fencing SQL, tasa duplicación bajo inyección |
| **INFERIDO** | Deducción razonable pero no medida directamente | Ventana pura ~1ms (por resta), warm-up ~60s (por configuración) |
| **NO DEMOSTRADO** | Evidencia insuficiente o fuera de alcance | Fencing frontera externa, power loss, frecuencia natural de crash, idempotencia integral, recovery end-to-end, convergencia global |
| **DECISION PENDING** | Requiere Board decision | DC-08, DF-24, aceptación de ventana |

**Lo que este HITO PUEDE afirmar:**
- La duración total execute→append_wal observada es ~26ms bajo condiciones del experimento
- La ventana pura post-effect/pre-journal es inferida como ~1ms (no medida directamente)
- La idempotencia existe por operación (append_wal con ON CONFLICT DO NOTHING)
- Fencing optimistic locking es efectivo para operaciones SQL (DEMOSTRADO experimentalmente)
- ProfileStore no usa llamadas LLM para re-inferencia (OBSERVADO en código)
- La tasa de duplicación BAJO INYECCIÓN ARTIFICIAL es 50%
- El coste unitario de duplicación es $0.0875/llamada (proyección con supuestos)

**Lo que este HITO NO PUEDE afirmar:**
- Que la ventana pura sea exactamente ~1ms (es inferencia por resta, no medición directa)
- Que la ventana esté "acotada" en el sentido contractual de tener un máximo garantizado (50 muestras no garantizan máximo)
- Que la idempotencia integral del flujo completo esté demostrada (las duplicaciones demuestran lo contrario en la ventana)
- Que la tasa natural de crash sea 50% (el experimento inyectó crashes artificialmente)
- Que fencing funcione contra proveedores externos (frontera no probada)
- Que SQLite NORMAL sea suficiente para power loss (no hay tests)
- Que recovery end-to-end converja bajo todos los escenarios (C_recovery vacío en reporte)
- Que la convergencia global esté demostrada (F_convergencia vacío en reporte)

### 2.2 Método

1. Cargar HITO_18.2.0 v1.3.0 FROZEN como insumo
2. Ejecutar auditoría A.1-A.7 (cobertura real de tests)
3. Ejecutar experimento `prueba_18.py` (50 muestras por escenario, mock LLM 25ms)
4. Separar OBSERVADO / DEMOSTRADO / INFERIDO / NO DEMOSTRADO / DECISION PENDING
5. No declarar destinos arquitectónicos como "resueltos"
6. Documentar supuestos explícitos para extrapolaciones
7. Distinguir medición directa de inferencia por resta

---

## 3. AUDITORÍA DE COBERTURA REAL (A.1-A.7)

### A.1 Cobertura de fencing en tests

**Resultado:** Búsqueda vacía para `(epoch|fencing|lease|stale_worker|obsolete_worker|lost_authority|lease_expired|LeaseExpiredError)` en tests/.

**Interpretación:** No hay tests unitarios con nombres o patterns que prueben explícitamente epoch fencing o loss of authority. La cobertura, si existe, está en otros patterns.

### A.2 Cobertura de recovery/crash

**Resultado parcial:** Se identificaron los siguientes archivos relevantes:
- `test_recovery_flow.py`: test end-to-end de crash recovery + resume (contenido completo en A.4)
- `test_recovery_determinability.py`: tests de recovery determinable post-fallo
- `test_resilient_provider.py`: test de CircuitBreaker con `GlobalCircuitBreaker(failure_threshold=2, recovery_timeout=10.0)`
- `test_pipeline_fsm_emission.py`: tests de resume desde PROCESSING y READY_FOR_ASSEMBLY
- `test_tectonic_runner.py`: tests de `tectonic_crash.log`
- `test_execution_failure_exit_code.py`: simulación de pipeline crash
- `chaos_runner.py`: contiene `game_day_1_crash_consistency` (observado)

**Interpretación:** Existe cobertura parcial de recovery en tests de integración. No es "inexistente" como afirmaba v1.0.0; es **cobertura parcial enfocada en recovery determinable y FSM transitions**. Cobertura específica de fencing por epoch: NO DEMOSTRADA en tests unitarios.

### A.3 game_day_1_crash_consistency

**Resultado:** Función observada en `chaos_runner.py` línea 178. No se ejecutó en este HITO (pertenece a Gate 4 del Execution Plan).

**Interpretación:** Recovery end-to-end y convergencia global NO DEMOSTRADAS en este hito. Requieren ejecución en Gate 4.

### A.4 test_recovery_flow.py (contenido completo)

**Resultado:** Test `test_complete_crash_recovery_and_resume_lifecycle` que:
1. Crea documento en PROCESSING con timestamp pasado
2. Ejecuta `AbandonedProcessWatchdog` → transiciona a STALLED
3. Ejecuta `OnDemandResumeManager` → rescata a PROCESSING
4. Ejecuta pipeline completo → COMPLETED

**Interpretación:** Recovery end-to-end OBSERVADO bajo condiciones controladas en test de integración. Demuestra watchdog + resumer + FSM transitions. No prueba reconciler ni epoch fencing.

### A.5 Timing/telemetría en _process_task

**Resultado:** Solo `time.perf_counter()` para métrica `node_latency`. **NO hay instrumentación específica** entre `execute()` y `append_wal()`.

**Interpretación:** La ventana execute→append_wal no está instrumentada en producción. La medición experimental (prueba_18.py) es la única evidencia de su tamaño, pero incluye latencia LLM mock. La ventana pura es inferida por resta, no medida directamente.

### A.6 Tests de durabilidad/power loss

**Resultado:** Búsqueda vacía para `(fsync|power_loss|sync_full|synchronous|WAL_checkpoint|durability)` en tests/.

**Interpretación:** CERO tests de durabilidad ante power loss. GAP-18.2.1-01 permanece NO DEMOSTRADO.

### A.7 Sanity check

**Resultado:** 854 tests collected. Baseline preservado. Rama: fase18_subfase02_gate00.

---

## 4. EVIDENCIA EXPERIMENTAL (prueba_18.py)

### Condiciones del experimento

| Parámetro | Valor |
|---|---|
| Muestras por escenario | 50 |
| Latencia LLM mock | 25ms (time.sleep) |
| BD | SQLite local temporal (temp_harness.sqlite) |
| Inyección de crash | Controlada, post-effect/pre-journal |
| Fecha ejecución | 2026-10-09T01:34:58 |
| Python | 3.11.9 |

### 4.1 Duración temporal execute→append_wal

| Métrica | Valor |
|---|---|
| samples | 50 |
| min_ms | 25.555 |
| max_ms | 26.626 |
| mean_ms | 26.02 |
| **P50** | **25.975** |
| **P95** | **26.566** |
| **P99** | **26.626** |

**Nota crítica sobre interpretación:** Esta medición INCLUYE la latencia LLM simulada (25ms via time.sleep) + log_external_effect + append_wal(). La ventana PURA post-effect/pre-journal (entre retorno de execute() y inicio de append_wal()) es **inferida** como aproximadamente P50=0.975ms, P99=1.626ms por resta de los 25ms del mock. Sin embargo, esta resta asume que time.sleep toma exactamente 25ms (en realidad tiene overhead de scheduling del sistema operativo) y que log_external_effect + append_wal son las únicas operaciones entre sleep y fin de medición. Por tanto:

- **DEMOSTRADO:** La duración total observada bajo condiciones del experimento es ~26ms (P50-P99).
- **INFERIDO:** La ventana pura post-effect/pre-journal es ~1ms (por resta).
- **NO DEMOSTRADO:** Que la ventana pura sea exactamente ~1ms (requiere medición directa sin mock).
- **NO DEMOSTRADO:** Que la ventana esté "acotada" en el sentido contractual de tener un máximo garantizado (50 muestras no garantizan máximo; el máximo observado fue 26.626ms pero no se puede afirmar que sea un límite superior).

**Recomendación:** Medir directamente la ventana pura instrumentando el código de producción entre execute() y append_wal() en Gate 4 del Execution Plan.

### 4.2 Tasa de duplicación bajo crash inyectado

| Métrica | Valor |
|---|---|
| total_tasks | 20 |
| crashes_inyectados | 10 |
| re_ejecuciones_por_reconciler | 10 |
| total_efectos_externos | 30 |
| **tasa_duplicacion_pct** | **50.0** |
| llamadas_duplicadas_absolutas | 10 |

**Interpretación:** La tasa del 50% es **artificial** porque el experimento inyectó crashes en exactamente el 50% de las tareas. NO representa la tasa natural de crash en producción. Representa: "si el proceso crashea en la ventana, el reconciler re-ejecuta".

**Clasificación:** Tasa bajo inyección artificial DEMOSTRADA. Tasa natural de crash NO DEMOSTRADA (requiere telemetría de producción).

### 4.3 Fencing por optimistic locking

| Test | Resultado |
|---|---|
| worker_zombi_bloqueado | **true** |
| worker_legitimo_funciona | **true** |
| veredicto | **PASS** (para operaciones SQL) |
| mecanismo | Optimistic locking vía WHERE lease_owner = ? AND lease_expires_at >= ? |

**Interpretación:** Fencing por optimistic locking **DEMOSTRADO** experimentalmente para operaciones SQL. Worker que perdió lease es bloqueado al intentar UPDATE en chunk_tasks. Worker legítimo funciona correctamente.

**Frontera NO probada:** Este test prueba solo la frontera SQLite (worker intenta UPDATE en BD). NO prueba la frontera del proveedor externo (worker obsoleto llama al LLM tras perder lease). La OBS-18.2.0-06 de v1.3.0 permanece abierta y NO DEMOSTRADA.

**Recomendación:** Diseñar experimento adicional en Gate 4 que pruebe la frontera externa: mock LLM que registre llamadas y verifique que worker zombi no pueda iniciar nuevas llamadas tras perder lease.

### 4.4 Coste FinOps (proyección corregida)

| Concepto | Valor |
|---|---|
| llamadas_duplicadas_obs | 10 |
| tokens_por_llamada (input/output) | 1500 / 500 |
| costo_unitario_usd | **0.0875** |
| **Escenario 1000 tareas/día, 50% tasa artificial:** | |
| duplicadas_estimadas | 500.0 |
| costo_diario_usd | 43.75 |
| **costo_mensual_usd** | **1,312.50** |

**Corrección de v1.1.0:** La versión anterior reportaba $131.25/mes, lo cual correspondía a una tasa del 5% (50 duplicadas/día), no del 50% (500 duplicadas/día). El cálculo correcto es:
```
1000 tareas/día × 50% = 500 duplicadas/día
500 × $0.0875 = $43.75/día
$43.75 × 30 días = $1,312.50/mes
```

**Nota sobre proyección:** Este cálculo usa la tasa artificial del 50%. El coste real depende de la tasa natural de crash, que NO está medida. Proyecciones con tasas realistas:

| Tasa de crash natural | Duplicadas/día | Coste mensual |
|---|---|---|
| 50% (artificial, arnés) | 500 | $1,312.50 |
| 5% (alto) | 50 | $131.25 |
| 1% (conservador) | 10 | $26.25 |
| 0.1% (realista) | 1 | $2.63 |
| 0.01% (optimista) | 0.1 | $0.26 |

La cuantificación del coste real requiere telemetría de crash en producción (Gate 4).

---

## 5. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Estado | Evidencia |
|---|---|---|---|---|
| Duración total execute→append_wal | P50=25.97ms (P99=26.63ms) bajo condiciones experimentales | INV-JOURNAL: ventana medida | **DEMOSTRADO** (duración observada) | E-18.2.1-001 (experimental) |
| Ventana pura post-effect/pre-journal | Inferida ~1ms por resta (26ms - 25ms mock) | INV-JOURNAL: ventana medida | **INFERIDO** (no medido directamente) | E-18.2.1-001 (experimental, inferencia) |
| Ventana acotada (máximo garantizado) | NO DEMOSTRADO (50 muestras no garantizan máximo) | INV-JOURNAL: ventana acotada | **NO DEMOSTRADO** | Requiere medición directa + análisis de worst-case |
| Idempotencia de append_wal | ON CONFLICT(execution_id, node_id) DO NOTHING | INV-JOURNAL: idempotent apply | **OBSERVADO** por operación | E-18.2.1-004 |
| Idempotencia integral del flujo | NO DEMOSTRADO (duplicaciones ocurren en ventana) | INV-JOURNAL: idempotent apply integral | **NO DEMOSTRADO** | Las 10 duplicaciones demuestran que el flujo completo no es idempotente en la ventana |
| Fencing optimistic locking (SQL) | Worker zombi bloqueado, legítimo funciona | INV-JOURNAL: ownership | **DEMOSTRADO** para operaciones SQL | E-18.2.0-005, experimental E |
| Fencing frontera externa | NO probado | INV-JOURNAL: prevención efecto externo post-loss | **NO DEMOSTRADO** | OBS-18.2.0-06 |
| Tasa natural de duplicación | NO medida (solo bajo inyección 50%) | INV-JOURNAL: ventana medida | **NO DEMOSTRADO** | requiere telemetría producción |
| ProfileStore persistencia | Re-inferencia sin coste de tokens LLM; coste de CPU no cuantificado | DF-34: cuantificar coste | **OBSERVADO** (recomendación: ACCEPTED_LIMITATION) | E-18.2.1-006 |
| CircuitBreaker persistencia | Warm-up ~60s estimado basado en configuración, no medido | DF-24: evaluar impacto | **INFERIDO** (DECISION PENDING) | E-18.2.1-007 |
| Telemetría durabilidad | Buffer in-memory, pérdida ~50 eventos | GAP-0.9-02: operational vs durable | **OBSERVADO** (no participa en recovery) | E-18.2.0-003 |
| SQLite crash de proceso | WAL + NORMAL + busy_timeout=30s | DC-08: durabilidad | **OBSERVADO** (suficiente) | E-18.2.1-002 |
| SQLite power loss | Cero tests (A.6 vacío) | DC-08: durabilidad | **NO DEMOSTRADO** | A.6 |
| Recovery end-to-end | test_recovery_flow.py OBSERVADO; game_day_1 no ejecutado | INV-OPS-1: recovery funcional | **PARCIALMENTE OBSERVADO** (test de integración existe; chaos harness no ejecutado) | A.4, A.3 |
| Convergencia global | NO medida (F_convergencia vacío en reporte) | INV-OPS-1: convergencia | **NO DEMOSTRADO** en este hito | Requiere Gate 4 |

---

## 6. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia | Hallazgo |
|---|---|---|---|
| E-18.2.1-001 | P1 | prueba_18.py resultado A | Duración total execute→append_wal observada P50=25.97ms (P99=26.63ms) incluye latencia LLM mock 25ms. Ventana pura inferida ~1ms por resta, no medida directamente. Ventana no demostrada como "acotada" en sentido contractual (máximo garantizado). Tasa duplicación bajo inyección: 50%. Coste unitario: $0.0875/llamada. |
| E-18.2.1-002 | P2 | infra/db/bootstrap.py, connection.py, A.6 | SQLite WAL + NORMAL + busy_timeout=30s. Suficiente para crash de proceso. NO DEMOSTRADO para power loss (cero tests en A.6). |
| E-18.2.1-003 | P2 | fsm_repository.py, reconciler.py, recovery.py, engine.py | Unidad de recuperación mixta: document (FSM), chunk (reconciler), execution (replay). |
| E-18.2.1-004 | — | event_repo.py::append_wal | Idempotencia de journal por operación: ON CONFLICT(execution_id, node_id) DO NOTHING. |
| E-18.2.1-005 | — | materialized_repo.py::upsert_projection | Idempotencia con version check monotonic. |
| E-18.2.1-006 | — | profiler.py::HeuristicDocumentProfiler | ProfileStore: re-inferencia heurística sin coste de tokens LLM. Coste de CPU no cuantificado (sin benchmark). |
| E-18.2.1-007 | — | provider_stack_factory.py, circuit_breaker_provider.py | CircuitBreaker global in-memory. Warm-up ~60s estimado basado en configuración (5 fallos × ventana de 60s), no medido experimentalmente. |
| E-18.2.1-008 | — | fsm_repository.py::initialize_document | Idempotencia FSM initialization: INSERT OR IGNORE. |
| E-18.2.1-009 | — | control_repo.py::mark_cqrs_reconciled | Idempotencia reconciliation: processed_reconciliation_commands. |
| E-18.2.1-010 | — | infra/extraction/providers/ | Extraction providers (docling, pymupdf, tesseract): idempotentes, sin side effects externos. |
| E-18.2.1-011 | — | profiles.py, run_regression.py | Perfiles SMOKE/FULL definidos. |
| E-18.2.1-012 | — | prueba_18.py resultado E | Fencing optimistic locking DEMOSTRADO experimentalmente para operaciones SQL: worker zombi bloqueado, legítimo funciona. Frontera externa NO DEMOSTRADA. |
| E-18.2.1-013 | — | A.1-A.7 auditoría | Cobertura parcial de recovery: test_recovery_flow.py, test_recovery_determinability.py, test_resilient_provider.py, test_pipeline_fsm_emission.py, game_day_1_crash_consistency (chaos_runner.py). test_fencing.py NO existe. Cobertura fencing en tests unitarios: CERO (A.1 vacío). Cobertura power loss: CERO (A.6 vacío). Recovery end-to-end OBSERVADO en test de integración; convergencia global NO DEMOSTRADA en este hito. |

---

## 7. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Estado | Fase destino |
|---|---|---|---|---|
| GAP-18.2.0-01 | Ventana execute→append_wal. Duración total observada ~26ms (incluye LLM mock). Ventana pura inferida ~1ms, no medida directamente. Ventana no demostrada como "acotada" (máximo garantizado). Idempotencia por operación OBSERVADA. Idempotencia integral NO DEMOSTRADA. Tasa duplicación bajo inyección 50%. Fencing SQLite DEMOSTRADO. Fencing frontera externa NO DEMOSTRADO. Coste FinOps $0.0875/llamada. | E-18.2.1-001, E-18.2.1-012, OBS-18.2.0-06 | **P1** (ni violación ni cumplimiento integrales demostrados; requiere Board decision sobre mecanismo vs aceptación) | 18.2 (DC-08) |
| GAP-18.2.0-02 | ProfileStore in-memory. Re-inferencia sin coste de tokens LLM OBSERVADA. Coste de CPU no cuantificado. | E-18.2.1-006 | **P2→RECOMENDACIÓN ACCEPTED_LIMITATION** (Board decide si acepta) | 18.2 (DF-34) |
| GAP-18.2.0-03 | CircuitBreaker in-memory. Warm-up ~60s estimado basado en configuración, no medido. | E-18.2.1-007 | **P2** (Board decision) | 18.2 (DF-24) |
| GAP-18.2.0-04 | Telemetría buffer in-memory. | E-18.2.0-003 | **P2→RECOMENDACIÓN ACCEPTED_LIMITATION** | F20 |
| GAP-18.2.0-05 | Fencing cobertura en tests. Cobertura parcial recovery existe. test_fencing.py NO existe. Fencing SQLite DEMOSTRADO. Frontera externa NO DEMOSTRADA. | E-18.2.1-012, E-18.2.1-013 | **P1→PARCIALMENTE RESUELTO** (fencing SQLite DEMOSTRADO; frontera externa NO DEMOSTRADA) | 18.2 (Gate 4) |
| GAP-18.2.0-06 | SQLite power loss. Cero tests. | E-18.2.1-002, A.6 | **P2** (NO DEMOSTRADO) | 18.2 (DC-08) |
| GAP-18.2.1-02 | Recovery end-to-end. test_recovery_flow.py OBSERVADO. game_day_1 no ejecutado en este hito. | E-18.2.1-013, A.3, A.4 | **P2** (PARCIALMENTE OBSERVADO; requiere Gate 4) | 18.2 (Gate 4) |
| GAP-18.2.1-03 | Convergencia global. F_convergencia vacío en reporte experimental. | E-18.2.1-013, A.3 | **P2** (NO DEMOSTRADO en este hito; requiere Gate 4) | 18.2 (Gate 4) |

---

## 8. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Estado |
|---|---|---|---|---|
| H-18.2.1-A | "Idempotencia existe por operación" | **CONFIRMADA** (en alcance acotado) | E-18.2.1-004, E-18.2.1-005, E-18.2.1-008, E-18.2.1-009 | Cerrada |
| H-18.2.1-B | "ProfileStore requiere persistencia" | **RECHAZADA** (recomendación ACCEPTED_LIMITATION) | E-18.2.1-006 | Cerrada |
| H-18.2.1-C | "CircuitBreaker requiere persistencia" | **PARCIAL** (warm-up estimado suficiente si provider operativo; no medido) | E-18.2.1-007 | Pendiente de decisión |
| H-18.2.1-D | "SQLite NORMAL suficiente para INV-JOURNAL" | **PARCIAL** (crash proceso SÍ, power loss NO DEMOSTRADO) | E-18.2.1-002, A.6 | Pendiente de decisión |
| H-18.2.1-E | "Recovery opera a un solo nivel" | **RECHAZADA** (mixta: document/chunk/execution) | E-18.2.1-003 | Cerrada |
| H-18.2.1-F | "Todos los efectos externos requieren journal" | **PARCIAL** (solo LLM calls) | E-18.2.1-001, E-18.2.1-010 | Cerrada |
| H-18.2.1-G | "Ventana pura execute→append_wal es ~1ms" | **INFERIDA** (por resta; no medida directamente) | E-18.2.1-001 | Abierta (requiere medición directa) |
| H-18.2.1-H | "Fencing optimistic locking es efectivo" | **PARCIALMENTE CONFIRMADA** (DEMOSTRADO para SQL; frontera externa NO DEMOSTRADA) | E-18.2.1-012 | Abierta (frontera externa pendiente) |
| H-18.2.1-I | "Cobertura de fencing en tests es inexistente" | **RECHAZADA** (cobertura parcial existe; test_fencing.py no existe pero hay tests equivalentes) | E-18.2.1-013, A.2 | Cerrada |
| H-18.2.1-J | "La ventana post-effect viola INV-JOURNAL" | **RECHAZADA** (consistente con HITO_18.2.0 v1.3.0: ni violación ni cumplimiento integrales demostrados) | E-18.2.1-001, HITO_18.2.0 v1.3.0 | Cerrada |
| H-18.2.1-K | "Idempotencia integral del flujo está demostrada" | **RECHAZADA** (duplicaciones demuestran que no es idempotente en ventana) | E-18.2.1-001 | Cerrada |
| H-18.2.1-L | "Recovery end-to-end converge bajo todos los escenarios" | **NO DEMOSTRADA** en este hito (C_recovery vacío; game_day_1 no ejecutado) | E-18.2.1-013, A.3 | Abierta (requiere Gate 4) |
| H-18.2.1-M | "Convergencia global está demostrada" | **NO DEMOSTRADA** en este hito (F_convergencia vacío) | E-18.2.1-013, A.3 | Abierta (requiere Gate 4) |
| H-18.2.1-N | "Frecuencia natural de crash es conocida" | **NO DEMOSTRADA** (solo tasa bajo inyección artificial) | E-18.2.1-001 | Abierta (requiere telemetría producción) |
| H-18.2.1-O | "Fencing frontera externa es efectivo" | **NO DEMOSTRADA** (solo frontera SQL probada) | E-18.2.1-012, OBS-18.2.0-06 | Abierta (requiere experimento adicional) |

---

## 9. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué mecanismo de journal cierra la ventana? (DC-08)

**Evidencia experimental:** Duración total observada ~26ms (incluye LLM mock). Ventana pura inferida ~1ms, no medida directamente. Idempotencia por operación existe. Fencing SQLite DEMOSTRADO. Idempotencia integral NO DEMOSTRADA.

**Opciones para Board decision:**
- **Opción A (Intent-First Journal):** Escribir INTENT antes de execute(). Agrega 1 write por llamada LLM. Coste adicional: estimado ~0.1ms latencia (no medido). Elimina duplicación.
- **Opción B (Aceptación formal):** Aceptar ventana con tasa natural de crash (a medir en producción). Coste: depende de tasa natural (proyección: $2.63-$1,312.50/mes para 1000 tareas/día).

**Advertencia:** La Opción B no certifica el cumplimiento integral de INV-JOURNAL; acepta una ventana de duplicación como riesgo residual.

### 16.2 ¿ProfileStore persistencia o reconstrucción? (DF-34)

**Evidencia:** Re-inferencia heurística sin coste de tokens LLM. Coste de CPU no cuantificado (sin benchmark).

**Recomendación:** ACCEPTED_LIMITATION (reconstrucción determinista preferible). Board decide.

### 16.3 ¿CircuitBreaker persistencia o warm-up? (DF-24)

**Evidencia:** Warm-up ~60s estimado basado en configuración (5 fallos × ventana de 60s), no medido experimentalmente.

**Opciones para Board decision:**
- **Opción A (Persistencia SQLite):** Agrega complejidad, elimina tormenta.
- **Opción B (Aceptación formal):** Aceptar warm-up como ACCEPTED_LIMITATION.

### 16.4 ¿Telemetría durable o ACCEPTED_LIMITATION? (GAP-0.9-02)

**Evidencia:** Buffer in-memory, no participa en recovery.

**Recomendación:** ACCEPTED_LIMITATION. Destino: F20.

### 16.5 ¿SQLite NORMAL suficiente? (DC-08)

**Evidencia:** Suficiente para crash de proceso. NO DEMOSTRADO para power loss (A.6 vacío).

**Opciones para Board decision:**
- Aceptar ventana de power loss (hardware moderno tiene battery-backed write cache frecuentemente).
- Usar synchronous=FULL (más costoso).
- Hardware battery-backed (más costoso).

### 16.6 ¿Unidad de recuperación? (INV-UNITS)

**Evidencia:** Mixta. Document (FSM), chunk (reconciler), execution (replay).

**Recomendación:** Documentar contractualmente la granularidad mixta. No requiere cambio.

### 16.7 ¿Qué efectos externos requieren journal?

**Evidencia:** Solo LLM calls (consume tokens, no idempotente). Rate limiter (estado interno, DF-27 resuelto). File I/O (idempotente). Extraction providers (idempotentes).

---

## 10. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia | Estado | Fase destino |
|---|---|---|---|---|
| DC-08 | Write-policy + journal | E-18.2.1-001, E-18.2.1-002, E-18.2.1-012, A.6 | Duración total observada; ventana pura inferida; idempotencia por operación OBSERVADA; idempotencia integral NO DEMOSTRADA; fencing SQLite DEMOSTRADO; frontera externa NO DEMOSTRADA; power loss NO DEMOSTRADO | 18.2 (Board decision) |
| DF-24 | CircuitBreaker | E-18.2.1-007 | Warm-up ~60s estimado basado en configuración, no medido | 18.2 (Board decision, subsumido en DC-08) |
| DF-34 | ProfileStore | E-18.2.1-006 | Re-inferencia sin coste de tokens LLM; coste de CPU no cuantificado | 18.2 (RECOMENDACIÓN ACCEPTED_LIMITATION) |
| GAP-0.9-02 | Telemetría | E-18.2.0-003 | Operational state | F20 (RECOMENDACIÓN ACCEPTED_LIMITATION) |

---

## 11. CIERRE DEL HITO 18.2.1

Este HITO demuestra experimentalmente que:
1. La duración total execute→append_wal observada es ~26ms (incluye LLM mock). Ventana pura inferida ~1ms, no medida directamente.
2. **Fencing optimistic locking es EFECTIVO para operaciones SQL** (DEMOSTRADO experimentalmente). Frontera externa NO DEMOSTRADA.
3. La tasa de duplicación bajo inyección artificial es 50%, con coste $0.0875/llamada duplicada. Coste mensual proyectado: $1,312.50/mes a tasa artificial 50% (corregido de v1.1.0).
4. ProfileStore: re-inferencia sin coste de tokens LLM; coste de CPU no cuantificado (recomendación ACCEPTED_LIMITATION).
5. CircuitBreaker: warm-up ~60s estimado basado en configuración, no medido.
6. SQLite NORMAL: suficiente para crash de proceso, NO DEMOSTRADO para power loss.
7. Cobertura de recovery en tests existe parcialmente (test_recovery_flow.py, test_recovery_determinability.py, game_day_1). Cobertura fencing en tests unitarios: CERO.
8. Recovery end-to-end OBSERVADO en test de integración. Convergencia global NO DEMOSTRADA en este hito.
9. **Idempotencia integral del flujo NO DEMOSTRADA** (las duplicaciones demuestran que no es idempotente en la ventana).
10. **Ni la violación estructural de INV-JOURNAL ni su cumplimiento integral están demostrados.**

**Estado del HITO:** FROZEN v1.2.0 (supersede v1.1.0 y v1.0.0)

**Condición de cierre cumplida:**
- [x] Metadata completa y consistente.
- [x] Changelog actualizado a v1.2.0 con 7 correcciones materiales.
- [x] Límite epistemológico declarado con separación OBSERVADO/DEMOSTRADO/INFERIDO/NO DEMOSTRADO/DECISION PENDING.
- [x] Auditoría A.1-A.7 completa y documentada.
- [x] Evidencia experimental (prueba_18.py) incorporada con supuestos explícitos.
- [x] Referencia actualizada a HITO_18.2.0 v1.3.0 FROZEN.
- [x] Clasificación GAP-18.2.0-01 mantenida como P1 (consistente con v1.3.0).
- [x] Eliminación de declaraciones "RESUELTO" para destinos arquitectónicos.
- [x] Frontera SQLite vs proveedor externo declarada (OBS-18.2.0-06).
- [x] **Corrección de error aritmético FinOps (factor 10).**
- [x] **Reformulación de ventana temporal: "duración observada" en lugar de "acotada y estable".**
- [x] **Eliminación de afirmación "idempotencia integral DEMOSTRADA".**
- [x] **Acotación de veredicto fencing: "fencing SQL demostrado; frontera externa no demostrada".**
- [x] **Declaración explícita de C_recovery y F_convergencia como NO DEMOSTRADAS.**
- [x] **Reclasificación de estimaciones: ProfileStore, CircuitBreaker, latencia journal.**
- [x] **Corrección de cierre de hipótesis: hipótesis abiertas y pendientes declaradas explícitamente.**
- [x] Todas las evidencias tienen ID estable.
- [x] Todos los gaps tienen evidencia vinculada.
- [x] Hipótesis abiertas y pendientes declaradas explícitamente (H-18.2.1-G, H-18.2.1-H, H-18.2.1-L, H-18.2.1-M, H-18.2.1-N, H-18.2.1-O).
- [x] Cero contradicciones con HITO_18.2.0 v1.3.0.
- [x] Siguiente paso recomendado declarado.

**Verificación de cadena de gobernanza:**
ADR_F18_MASTER FROZEN → HITO_18.2.0 v1.3.0 FROZEN → **HITO_18.2.1 v1.2.0 FROZEN** → ADR_F18.2 (pendiente) → NADR_F18-03 (pendiente) → PHASE_18.2_EXECUTION_PLAN (pendiente).

**Contradicciones con HITOs previos:**
- v1.0.0 clasificó GAP-18.2.0-01 como P0. v1.1.0 lo reclasificó como P1. v1.2.0 mantiene P1 (consistente con HITO_18.2.0 v1.3.0 FROZEN).
- v1.0.0 declaró "cobertura de fencing inexistente". v1.1.0 la corrigió: "cobertura parcial existe en tests de integración, cero en tests unitarios específicos". v1.2.0 mantiene esta corrección.
- v1.1.0 reportó $131.25/mes. v1.2.0 corrige a $1,312.50/mes (error de factor 10).
- v1.1.0 declaró "idempotencia integral DEMOSTRADA". v1.2.0 corrige a "idempotencia por operación OBSERVADA; idempotencia integral NO DEMOSTRADA".
- v1.1.0 declaró "ventana acotada y estable". v1.2.0 corrige a "duración observada bajo condiciones del experimento; ventana pura inferida, no medida directamente".

**Decision Candidates generados:** Ninguno nuevo. DC-08, DF-24, DF-34 son DCs existentes del ADR Maestro.

**Condiciones de validación pendientes (para ADR_F18.2):**
1. Medición directa de ventana pura post-effect/pre-journal (sin mock LLM).
2. Ejecución de game_day_1_crash_consistency completo (recovery end-to-end y convergencia global).
3. Experimento de fencing frontera externa (worker obsoleto intentando llamada LLM tras perder lease).
4. Telemetría de tasa natural de crash en producción.
5. Tests de durabilidad ante power loss.

**Siguiente paso recomendado:** Emitir ADR_F18.2 con HITO_18.2.0 v1.3.0 y HITO_18.2.1 v1.2.0 como insumos, declarando explícitamente las condiciones de validación pendientes. El ADR debe:
1. Resolver DC-08: Intent-First Journal vs aceptación formal (con tasa natural a medir en Gate 4). Advertencia: la aceptación formal no certifica cumplimiento integral de INV-JOURNAL.
2. Resolver DF-24: persistencia vs warm-up (basado en estimación, no medición).
3. Ratificar ACCEPTED_LIMITATION para DF-34 (ProfileStore) y GAP-0.9-02 (telemetría).
4. Aceptar ventana de power loss o requerir synchronous=FULL.
5. Requerir Gate 4 del Execution Plan: (a) medir tasa natural de crash en producción, (b) ejecutar game_day_1 completo, (c) test de fencing frontera externa, (d) test de power loss, (e) medición directa de ventana pura.

---

**Nota de Gobernanza:** Este HITO es evidencia experimental pura con correcciones materiales aplicadas en v1.2.0. No propone código de producción. No materializa decisiones de implementación. No certifica el cumplimiento integral de INV-JOURNAL. Su función es servir como insumo para ADR_F18.2, NADR_F18-03 y PHASE_18.2_EXECUTION_PLAN, con condiciones de validación explícitas. La versión v1.2.0 supersede v1.1.0 y v1.0.0 y constituye la referencia canónica para decisiones arquitectónicas posteriores.