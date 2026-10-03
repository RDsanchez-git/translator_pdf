# HITO_0.8_F0-C_State_Durability_Recovery_Map.md

**Estado:** FROZEN v1.4.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Discovery (State Durability & Recovery Map)
**Naturaleza:** Read-only + Evidence Validation. Mapea durabilidad y comportamiento de recovery de activos del execution plane; valida recovery mechanisms con tests de integración ejecutados. No cuantifica costo económico (eso es F0-D).
**Evidencia Forense Vinculante:** `FASE0_AUDIT_CHARTER.md` §4 (INV-JOURNAL), §6 (Etapa 3); `HITO_0.1` v1.2.0; `HITO_0.2` v1.2.0; `HITO_0.4` v1.3.0 (DC-02 vigente); `NADR-F17BIS-09` (FSM/Event Log Integrity); `NADR-F17BIS-07` (Healing Atomic Rollback); `NADR-F17BIS-08` (Distributed Execution Plane CQRS); `ENGINEERING_PRINCIPLES.md` §IV (Cero Fallos Silenciosos); `ADR_F17_BIS_MASTER.md` §5 (Determinismo y Reproducibilidad).
**Mandato:** Responder "qué sobrevive, qué se pierde y cómo intenta recuperarse" por activo del execution plane; verificar durabilidad/convergencia de activos reclamados por Charter §6 (FSM, reconciler, chaos_runner, supervisor); cerrar hipótesis abiertas de HITO_0.1/0.2 con destino F0-C. La frontera con F0-D es explícita: F0-C no cuantifica costo; F0-D responde "cuánto cuesta operacional y económicamente este comportamiento bajo workload".
**Síntesis:** Durabilidad heterogénea y estratificada. Varios activos del data plane poseen persistencia estructural SQLite WAL con mecanismos de recovery implementados; algunos escenarios de recovery están validados empíricamente (test_recovery_flow PASSED); la convergencia por activo permanece heterogénea y no demostrada globalmente. El resilience plane (Circuit Breaker, Profile Store) es in-memory con pérdida total de estado operacional en restart. El orden execute() → append_wal() viola INV-JOURNAL estructuralmente; su consecuencia económica es una inferencia trazada, no una medición. Coordinated shutdown como capacidad permanece NO DEMOSTRADA (implementación nominal no encontrada). Epoch fencing NO DEMOSTRADO (test_fencing colecta 0 tests).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-02 | Emisión inicial. Matriz de durabilidad completa; H-0.2-B rechazada (INV-JOURNAL violado); activos in-memory identificados; DaemonSupervisor MISSING. |
| 1.1.0-FROZEN | 2026-10-02 | Fusión de dos auditorías independientes. 16 evidencias, 5 gaps, 6 DCs, 8 hipótesis. |
| 1.2.0-FROZEN | 2026-10-02 | Reconciliación post-análisis crítico + evidencia empírica (tests ejecutados). Determinismo degradado a NO DEMOSTRADO; loss window separado en 5 categorías; recovery convergence CONFIRMED por test; CQRS lineage CONFIRMED con caveat; epoch fencing NO DEMOSTRADO; journal-first eliminado como mitigación; SQLite "óptima" eliminado; severidad semántica corregida. |
| 1.3.0-FROZEN | 2026-10-02 | Unificación v1.2.0 + draft v1.2.0-alt. Absorbe: GAP-0.8-06, columna Recovery Convergence, naturaleza Evidence Validation, E-0.8-018 severidad P1. Corrige: DC-02 restaurado, H-0.8-D restaurada como inferencia estructural, CQRS lineage matizado, caveat execution_id re-redactado. |
| 1.4.0-FROZEN | 2026-10-02 | **Versión unificada definitiva.** (1) Correcciones semánticas: recovery convergence des-generalizado; GAP-0.8-01 bajado a P1 con justificación; taxonomía formal de pérdida; telemetry loss = residuo no acotado; STALLED = Escalation Threshold; TOTAL calificado como estado operacional; H-0.8-B = mecanismo presente; H-0.8-D acotada a condiciones observadas; destinos sin prescribir solución; frontera F0-C/F0-D explícita; §16.7 "Qué NO afirma este HITO". (2) Estructura forense explícita recuperada en §10 (campos Observed/Required/Hallazgo/Severidad separados). (3) H-0.8-A restaurada a OBSERVADA (regresión semántica corregida). (4) E-0.8-016 severidad P1 restaurada. (5) DC-08 documentado como DC compuesto con nota de posible subdivisión en ADR Master. |

---

## 1. RESUMEN EJECUTIVO

Se auditó estáticamente el execution plane y se ejecutaron tests de integración existentes para mapear durabilidad y recovery de todos los activos con estado, conforme al mandato de Charter §6 (Etapa 3, F0-C).

**Hallazgo central:**

> La durabilidad es heterogénea y estratificada. Varios activos del data plane (leases, FSM, event WAL, materialized projections, rate-limit buckets) poseen persistencia estructural SQLite WAL con mecanismos de recovery implementados; el escenario test_complete_crash_recovery_and_resume_lifecycle pasó, validando empíricamente un flujo de recovery concreto. La convergencia de recovery por activo permanece heterogénea: CONFIRMED para FSM en el escenario testeado, NO DEMOSTRADO para zombie recovery de leases, epoch fencing, rate limits y telemetry. El resilience plane (Circuit Breaker, Profile Store) es in-memory: pérdida total de estado operacional en restart. El orden execute() → append_wal() viola INV-JOURNAL estructuralmente.

**Hechos observados (CONFIRMED / OBSERVED):**

1. **Task Lease y Leadership Epoch (E-0.8-001, E-0.8-002):** Persistencia estructural con BEGIN IMMEDIATE, TTLs (300s/120s), heartbeats (30s/36s); mecanismos de recovery implementados (reconciler con epoch fencing). Convergencia de zombie recovery y fencing NO DEMOSTRADA (GAP-0.8-06, GAP-0.8-07).
2. **Event WAL y Materialized Projections (E-0.8-003, E-0.8-004):** Persistencia de writes observada; orden invertido respecto a INV-JOURNAL; lineage estructural CQRS CONFIRMED; integridad bajo crash PARTIAL (GAP-0.8-04).
3. **Document FSM (E-0.8-005, E-0.8-016):** CAS versionado, cuarentena STALLED con Escalation Threshold 3600s, recovery dual automático/manual; convergencia CONFIRMADA en el escenario testeado (E-0.8-017); no global.
4. **Rate-limit buckets (E-0.8-006):** Persistencia post-consumo y restore con refill; correctitud temporal bajo clock perturbation NO DEMOSTRADA.
5. **Circuit Breaker y Profile Store (E-0.8-007, E-0.8-008):** In-memory; STATE_LOSS TOTAL de estado operacional en restart.
6. **Coordinated shutdown (E-0.8-009):** Implementación nominal (DaemonSupervisor/GracefulShutdown) no encontrada; capacidad NO DEMOSTRADA (GAP-0.8-01, P1).
7. **PRAGMAs SQLite (E-0.8-014):** Configuración observada (WAL + NORMAL + busy_timeout); optimalidad NO DEMOSTRADA.
8. **Economic replay (E-0.8-020):** Mecanismo presente con clave de dedup intencional (content_hash + prompt_v + model_v); no cubre crash-before-journal en primera ejecución.

**Veredicto:** F0-C establece el mapa de durabilidad y recovery con fronteras epistémicas correctas. No demuestra convergencia global de recovery, no cuantifica waste (F0-D), y no decide mecanismos de cierre (DC-08, DC-13). Siete gaps abiertos (GAP-0.8-01 a GAP-0.8-07) con destino a decisión de arquitectura en Fase 18 y cuantificación en F0-D.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Mapa estático + validación limitada: un test de integración ejecutado y pasado. Las loss windows derivan de TTLs e intervalos configurados en código, no de medición de crash real. Ningún claim de convergencia global, costo económico o determinismo científico.

### 2.2 Frontera F0-C / F0-D
- **F0-C responde:** qué sobrevive, qué se pierde y cómo intenta recuperarse.
- **F0-D responde:** cuánto cuesta operacional y económicamente ese comportamiento bajo workload, incluyendo el impacto de las ventanas de recovery (en particular execute() → append_wal()).

### 2.3 Método forense
1. Inspeccionar repositorios y daemons para backend, transacciones, atomicidad y recovery behavior.
2. Verificar presencia de activos reclamados por Charter §6.
3. Ejecutar tests de integración existentes (test_recovery_flow, test_fencing) sin mutar estado normativo.
4. Clasificar: FACT / OBSERVED / CONFIRMED / INFERENCE / NO DEMOSTRADO / MISSING.
5. Aplicar taxonomía de pérdida (§7.3) a cada ventana.
6. Cerrar hipótesis de HITO_0.1/0.2 con destino explícito.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `apps/llm_workers/__main__.py` | Worker, TaskLeaseHeartbeat, shutdown, _process_task | 100% auditado |
| `apps/compiler/__main__.py` | AssemblerWorkerDaemon, _fail_document_safely | 100% auditado |
| `apps/llm_workers/adapters.py` | GroqProvider, GeminiProvider, timeouts | 100% auditado |
| `apps/daemons/reconciler.py` | ReconcilerDaemon, sweep_tasks, sweep_fsm_stalls, leadership | 100% auditado |
| `apps/daemons/chaos_runner.py` | SystemObserver, ChaosInjector, game_day_1_crash_consistency | 100% auditado (chaos sin ejecutar) |
| `runtime/sweeper.py` | RecoveryDaemon, WAL checkpoint, stalled docs | 100% auditado |
| `runtime/recovery.py` | AbandonedProcessWatchdog | 100% auditado |
| `runtime/resumer.py` | OnDemandResumeManager | 100% auditado |
| `runtime/settings.py` | RuntimeSettings | 100% auditado |
| `infra/db/control_repo.py` | ControlPlaneRepository, leases, zombie recovery | 100% auditado |
| `infra/db/system_repo.py` | SystemPlaneRepository, leadership, epoch | 100% auditado |
| `infra/db/fsm_repository.py` | FSMRepository, transitions, stalled docs | 100% auditado |
| `infra/db/event_repo.py` | EventPlaneRepository, WAL append, replay | 100% auditado |
| `infra/db/materialized_repo.py` | MaterializedPlaneRepository, upsert_projection | 100% auditado |
| `infra/db/bootstrap.py`, `connection.py` | PRAGMAs, connection config | 100% auditado |
| `core/resilience/circuit_breaker.py` | GlobalCircuitBreaker, state in-memory | 100% auditado |
| `infra/db/profile_store.py` | InMemoryProfileStore | 100% auditado |
| `core/telemetry/gateway.py` | SQLiteTelemetryGateway, queue in-memory | 100% auditado |
| `apps/llm_workers/rate_limiter.py` | QuotaManager, persist/restore buckets | 100% auditado |
| `infra/resilience/sqlite_rate_limit_store.py` | SQLiteRateLimitStore | 100% auditado |
| `core/execution/state.py`, `handlers.py` | DocumentState, commands, handlers | 100% auditado |
| `core/pipeline/state_store.py` | FSMStateStore, dispatch, versionado | 100% auditado |
| `tests/integration/test_recovery_flow.py` | Recovery lifecycle test | **EJECUTADO, PASSED** |
| `tests/test_fencing.py` | Epoch fencing tests | **EJECUTADO, 0 TESTS COLLECTED** |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Charter | `FASE0_AUDIT_CHARTER.md` §4, §6 | Mandato: INV-JOURNAL, matriz state→authority→storage→durability→recovery→loss window; activos reclamados |
| ADR | `ADR_F17_BIS_MASTER.md` §5 | Determinismo y Reproducibilidad; frontera de determinismo |
| NADR | `NADR-F17BIS-09` | FSM/Event Log Integrity |
| NADR | `NADR-F17BIS-07` | Healing Atomic Rollback |
| NADR | `NADR-F17BIS-08` | Distributed Execution Plane CQRS |
| Principios | `ENGINEERING_PRINCIPLES.md` §IV | Cero Fallos Silenciosos |
| HITO previo | `HITO_0.1` v1.2.0 | H-0.1-B, GAP-0.1-03 abiertos con destino F0-C |
| HITO previo | `HITO_0.2` v1.2.0 | H-0.2-B, GAP-0.2-04, DF-34 abiertos con destino F0-C |
| HITO previo | `HITO_0.4` v1.3.0 | DC-02 vigente (parámetros de runtime en identidad científica) |
| Código | 20 superficies (§3) | Evidencia forense primaria |
| Tests | `test_recovery_flow.py` | **EJECUTADO, PASSED** — Recovery convergence en escenario concreto |
| Tests | `test_fencing.py` | **EJECUTADO, 0 TESTS COLLECTED** — Epoch fencing NO DEMOSTRADO |
| Chaos | `chaos_runner.py` | Evidencia reutilizable (no ejecutada) |

---

## 7. MATRIZ DE DURABILIDAD Y RECOVERY

### 7.1 Matriz estructural con convergencia por activo

| Activo | Authority | Storage | Persistence Mechanism | Recovery Mechanism | Recovery Convergence |
|---|---|---|---|---|---|
| Task Lease (chunk) | ControlPlaneRepository | queue.db (WAL) | OBSERVED: BEGIN IMMEDIATE, TTL 300s, heartbeat 30s, OptimisticLockError | OBSERVED: reconciler sweep 25-35s; mark_zombie_recovered | **NO DEMOSTRADO** (GAP-0.8-07) |
| Leadership Epoch | SystemPlaneRepository | system.db (WAL) | OBSERVED: BEGIN IMMEDIATE, TTL 120s, heartbeat 36s | OBSERVED: epoch fencing en handlers | **NO DEMOSTRADO** (GAP-0.8-06) |
| Event WAL | EventPlaneRepository | event.db (WAL) | OBSERVED: INSERT + commit inmediato | OBSERVED: economic replay por clave de dedup | **CONFIRMED estructural / PARTIAL bajo crash** (E-0.8-019, GAP-0.8-04) |
| Materialized Projections | MaterializedPlaneRepository | materialized.db (WAL) | OBSERVED: upsert con version check | OBSERVED: rematerialización vía reconciler | **CONFIRMED estructural** |
| Document FSM | FSMRepository + DocumentCommandHandler | fsm.db (WAL) | OBSERVED: CAS + state_version | OBSERVED: watchdog, sweeper, resumer | **CONFIRMED en escenario testeado** (E-0.8-017); no global |
| Rate-limit buckets | QuotaManager + SQLiteRateLimitStore | rate_limits.db (WAL) | OBSERVED: persist post-consumo, restore con refill | OBSERVED: refill por elapsed | **NO DEMOSTRADO** |
| Circuit Breaker | GlobalCircuitBreaker + Registry | **IN-MEMORY** | **NONE** | OBSERVED: cold start en CLOSED | **NO DEMOSTRADO**; STATE_LOSS TOTAL (estado operacional) |
| Profile Store | InMemoryProfileStore | **IN-MEMORY** | **NONE** | OBSERVED: reconstrucción por otra vía no demostrada | **NO DEMOSTRADO**; STATE_LOSS TOTAL (estado operacional) |
| Telemetry Gateway | SQLiteTelemetryGateway | production.db (WAL) + asyncio.Queue | OBSERVED: flush por lotes | OBSERVED: flush limpio solo en stop() ordenado | **NO DEMOSTRADO**; TELEMETRY_LOSS residual |
| WAL Checkpoint | RecoveryDaemon | Todos los DBs | OBSERVED: wal_checkpoint(TRUNCATE) por ciclo | N/A (performance, no datos) | N/A |

### 7.2 Ventanas temporales (nomenclatura corregida)

| Activo | Persistence Window | Detection Interval | Recovery / Escalation Threshold | Potential Data-Loss | Potential Duplicate-Effect |
|---|---|---|---|---|---|
| Task lease | Immediate (WAL commit) | 25-35s (sweep) | 300s (stale ownership máximo) | NO DEMOSTRADO | Ventana execute→append_wal (INV-JOURNAL) |
| Leadership | Immediate | 36s (heartbeat) | 120s (TTL) | NO DEMOSTRADO | Mitigado por fencing (NO DEMOSTRADO empíricamente) |
| STALLED quarantine | Immediate | 30-35s (sweeper) | 3600s = **Escalation Threshold** a FAILED_FATAL (no es recovery) | NO DEMOSTRADO | N/A |
| Telemetry | Batch (50 o queue vacía) | N/A | N/A | TELEMETRY_LOSS = residuo de queue no flusheado (no acotado por batch size) | N/A |
| Circuit Breaker | **NONE** | N/A | N/A | STATE_LOSS TOTAL (estado operacional) | Reintentos post-restart (NO CUANTIFICADO) |
| Profile Store | **NONE** | N/A | N/A | STATE_LOSS TOTAL (estado operacional) | Re-inferencia (NO CUANTIFICADO) |

### 7.3 Taxonomía formal de pérdida

| Categoría | Definición | Activos afectados |
|---|---|---|
| DATA_LOSS | Pérdida de datos científicos o de documento | Ninguno demostrado |
| STATE_LOSS | Pérdida de estado operacional persistente | Circuit Breaker, Profile Store (TOTAL); telemetry (parcial) |
| WORK_LOSS | Trabajo completado que debe rehacerse | Potencial en ventana execute→append_wal (NO CUANTIFICADO) |
| DUPLICATE_EFFECT | Efecto externo ejecutado más de una vez | Potencial en ventana execute→append_wal (H-0.8-D, inferencia) |
| ECONOMIC_WASTE | Costo financiero de WORK_LOSS o DUPLICATE_EFFECT | NO CUANTIFICADO (F0-D) |
| TELEMETRY_LOSS | Pérdida de eventos observacionales | Telemetry gateway (residual de queue) |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.8-001: Task lease: persistencia y zombie write prevention observadas
* **Archivo:** `infra/db/control_repo.py:36-176`; `apps/llm_workers/__main__.py:31-77`
* **Observed:**
  - `pick_task` usa `BEGIN IMMEDIATE` (control_repo.py:42), TTL 300s (control_repo.py:39), retorna TaskLease con lease_expires_at.
  - `TaskLeaseHeartbeat` corre en daemon thread, renueva lease cada TTL×0.25 = 30s (main.py:41, 57-59).
  - `acknowledge_execution`, `abandon_execution`, `release_task_untouched` usan `WHERE lease_owner = ? AND lease_expires_at >= ?` para proteger writes zombie (control_repo.py:77, 94, 121); lanzan OptimisticLockError si lease expiró.
  - Reconciler corre cada 25-35s (reconciler.py:102, 120), detecta zombies y los recupera (reconciler.py:129-196).
* **Hallazgo:** Mechanism exists OBSERVED. Recovery convergence NO DEMOSTRADO (no hay tests específicos para zombie recovery).
* **Severidad:** N/A (fortaleza observada, no gap)

### Evidencia E-0.8-002: Leadership epoch con fencing implementado
* **Archivo:** `infra/db/system_repo.py:8-51`; `apps/daemons/reconciler.py:76-127`; `core/execution/handlers.py:128-196`
* **Observed:**
  - `acquire_leadership` usa `BEGIN IMMEDIATE` (system_repo.py:11), TTL 120s, retorna epoch (lease_version autoincrementa, system_repo.py:15).
  - `_leadership_heartbeat` renueva cada TTL×0.3 = 36s (reconciler.py:27, 80); si falla, log LEADERSHIP_LOST y resetea epoch a 0 (reconciler.py:82-85).
  - Epoch fencing: `ReconciliationCommandHandler.handle_rematerialize` y `handle_recover_zombie` verifican `cmd.reconciler_epoch == current_epoch`; si mismatch, `STALE_RECONCILER_COMMAND_DROPPED` + métrica (handlers.py:132-134, 180-182).
* **Hallazgo:** Mechanism exists OBSERVED. Epoch fencing NO DEMOSTRADO empíricamente (test_fencing.py colecta 0 tests, GAP-0.8-06).
* **Severidad:** N/A (fortaleza observada, validación pendiente)

### Evidencia E-0.8-003: Event WAL: persistencia confirmada, orden INV-JOURNAL violado
* **Archivo:** `apps/llm_workers/__main__.py:137-199`; `infra/db/event_repo.py:41-53`
* **Observed:**
  - Worker ejecuta: `raw_response = self.processor.execute(node)` (main.py:173, **efecto externo: llamada a proveedor**), luego `self.event.append_wal(...)` (main.py:178-182, **journal**).
  - `append_wal` hace `INSERT INTO chunk_events_log` con commit inmediato (event_repo.py:53).
  - `get_replay` permite replay económico si content_hash + prompt_v + model_v coinciden (event_repo.py:28-38).
  - Entre L175 (`heartbeat.lease_lost` check) y L178 (`append_wal`) existe una ventana donde el I/O al LLM se ejecutó pero no se journaleó.
* **Required:** Charter §4 INV-JOURNAL: "ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash y una aplicación idempotente del resultado."
* **Hallazgo:** **H-0.2-B RECHAZADA.** El orden es efecto externo → journal, no journal → efecto externo. Si crash DESPUÉS de `execute()` pero ANTES de `append_wal()`, el proveedor ya fue llamado (costo incurrido) pero no hay registro. Re-ejecución duplica el trabajo. Esto viola INV-JOURNAL: el journal debe preceder al efecto externo, o el efecto debe ser idempotente (pero llamadas a LLM no lo son). **GAP-0.8-04**. Consecuencia económica NO cuantificada (F0-D).
* **Severidad:** P1

### Evidencia E-0.8-004: Materialized projections con idempotencia
* **Archivo:** `apps/llm_workers/__main__.py:192-195`; `infra/db/materialized_repo.py:28-40`
* **Observed:**
  - `upsert_projection` con commit (main.py:192-195).
  - Idempotencia por content_hash + projection_v: si proyección ya existe con mismo hash, no se sobreescribe.
  - Query con `WHERE projection_version >= valid_chunks_cache.projection_version` permite updates solo si la versión es mayor o igual.
* **Hallazgo:** Mechanism exists OBSERVED. CQRS lineage estructural CONFIRMED (ciclo Event Plane → Materialized Plane verificado, E-0.8-019).
* **Severidad:** N/A (fortaleza observada)

### Evidencia E-0.8-005: Document FSM con CAS versionado
* **Archivo:** `infra/db/fsm_repository.py:21-125`; `core/execution/handlers.py:28-109`; `core/pipeline/state_store.py:29-59`; `core/execution/state.py`
* **Observed:**
  - `transition_to` usa CAS: `WHERE document_id = ? AND ast_hash = ? AND current_state = ?` (fsm_repository.py:37-40), versionado con state_version.
  - `FSMStateStore.dispatch()` delega a `DocumentCommandHandler.handle()` que valida transición vía `FSMValidator.validate()` antes de ejecutar.
  - Terminal states: COMPLETED, FAILED_FATAL, CANCELLED (state.py:50-52).
  - STALLED es estado de cuarentena, no terminal; transiciones válidas: STALLED → {PARSING, PROCESSING, ..., CANCELLED} (state.py:36-39).
* **Hallazgo:** Mechanism exists OBSERVED. Recovery convergence CONFIRMED en escenario testeado (E-0.8-017); no global.
* **Severidad:** N/A (fortaleza observada)

### Evidencia E-0.8-006: Rate-limit buckets: mecanismo observado, correctitud temporal no demostrada
* **Archivo:** `apps/llm_workers/rate_limiter.py:125-186`; `infra/resilience/sqlite_rate_limit_store.py:27-61`
* **Observed:**
  - `_persist_bucket_state` después de cada consumo exitoso (rate_limiter.py:186): INSERT ON CONFLICT DO UPDATE en rate_limits.db.
  - `_restore_bucket_state` en startup (rate_limiter.py:127-128, 144-151): carga estado previo, aplica refill por tiempo transcurrido (`elapsed * refill_rate`), actualiza bucket.
  - **Caveat técnico:** La conversión epoch → monotonic depende de `time.time()` (rate_limiter.py:148), que puede tener drift en sistemas con NTP adjust. El refill compensa parcialmente, pero un ajuste de reloj hacia atrás podría producir refill negativo (mitigado por `max(0.0, ...)` en L148).
* **Hallazgo:** Mechanism exists OBSERVED. Recovery convergence NO DEMOSTRADO (no hay tests específicos). Correctitud bajo clock perturbation NO DEMOSTRADA.
* **Severidad:** N/A (fortaleza observada, validación pendiente)

### Evidencia E-0.8-007: Circuit Breaker in-memory sin persistencia
* **Archivo:** `core/resilience/circuit_breaker.py:17-127`
* **Observed:**
  - `GlobalCircuitBreaker.__init__` inicializa `self.state = CircuitState.CLOSED`, `self.failure_timestamps = deque()`, `self.last_failure_time = 0.0` (circuit_breaker.py:19-25).
  - No hay método `save()` ni `restore()`; no hay store inyectado.
  - `CircuitBreakerRegistry` es singleton in-memory con `threading.Lock` para creación estática (circuit_breaker.py:119-127).
* **Hallazgo:** **GAP-0.8-02.** STATE_LOSS TOTAL de estado operacional en restart. CB empieza CLOSED en cada restart; si el proveedor estaba caído, el primer request falla y reabre el circuito, pero hay ventana de vulnerabilidad donde requests fallidos pueden reintentarse innecesariamente. Impacto operacional NO CUANTIFICADO (F0-D).
* **Severidad:** P1

### Evidencia E-0.8-008: Profile Store in-memory (DF-34)
* **Archivo:** `infra/db/profile_store.py:4-15`
* **Observed:**
  - `InMemoryProfileStore.__init__` inicializa `self._store: dict[str, InferredDocumentProfile] = {}` (profile_store.py:9).
  - `save()` y `get()` operan sobre el dict in-memory (profile_store.py:11-15).
  - No hay backend persistente.
* **Hallazgo:** **DF-34 CONFIRMADO en nivel FACT. GAP-0.8-03.** FACT: el estado no sobrevive restart. INFERENCE: requiere reconstrucción por otra vía. NO DEMOSTRADO: que cada restart provoque necesariamente re-inferencia completa de todos los perfiles. Costo → F0-D.
* **Severidad:** P1

### Evidencia E-0.8-009: Coordinated shutdown capability NO DEMOSTRADA
* **Archivo:** Búsqueda recursiva en `apps/`, `runtime/`, `core/`, `infra/`
* **Observed:** No existe clase `DaemonSupervisor`, `GracefulShutdown`, ni función `graceful_shutdown` o `supervise` en las superficies auditadas.
* **Shutdown distribuido actual:** Cada daemon (Worker, Reconciler, Sweeper) maneja su propio shutdown vía `signal.signal(SIGINT/SIGTERM)` + `_stop_event` (main.py:280-281, reconciler.py:127).
* **Required:** Charter §6 lista "DaemonSupervisor/GracefulShutdown" como activo reclamado. HITO_0.2_F0-G lo menciona.
* **Hallazgo:** **GAP-0.8-01.** FACT: implementación nominal no encontrada en superficies auditadas. INFERENCE: coordinated shutdown no garantizado. La capacidad podría existir por otra composición no observada, por lo que permanece NO DEMOSTRADA, no imposible. Severidad P1: activo reclamado por Charter §6; impacto inmediato mitigado por leases/TTL/reconciler; P0 reservado a violación de invariante científica o bloqueo de certificación.
* **Severidad:** P1 (MISSING)

### Evidencia E-0.8-010: Telemetry gateway: pérdida residual de queue
* **Archivo:** `core/telemetry/gateway.py:10-84`
* **Observed:**
  - `SQLiteTelemetryGateway` usa `asyncio.Queue` in-memory (gateway.py:16).
  - `_flush_worker` consume de la queue, hace batch de hasta 50 eventos, escribe en production.db (gateway.py:58-84).
  - `stop()` envía poison pill (`None`) para cerrado limpio (gateway.py:45-47).
* **Hallazgo:** TELEMETRY_LOSS = eventos residentes en queue no flusheados al momento del crash. El batch size 50 NO acota el máximo absoluto de pérdida (depende de acumulación en queue, frecuencia de flush, y momento exacto del crash). GAP-0.8-05.
* **Severidad:** P2

### Evidencia E-0.8-011: Chaos runner y recovery tests: existencia, no resultado global
* **Archivo:** `apps/daemons/chaos_runner.py:19-220`; `tests/integration/test_recovery_flow.py`; `tests/test_fencing.py`
* **Observed:**
  - `SystemObserver`: `inject_load()`, `get_convergence_metrics()`, `wait_for_convergence(target_docs, timeout_sec=300)`.
  - `ChaosInjector`: `kill_service(service_name, signal="SIGKILL")`, `mutate_upstream(payload)`.
  - `game_day_1_crash_consistency()`: test de crash consistency que inyecta carga, mata reconciler y worker, y espera convergencia.
  - `test_complete_crash_recovery_and_resume_lifecycle`: test de recovery lifecycle completo. **EJECUTADO, PASSED** (E-0.8-017).
  - `test_fencing.py`: archivo existe pero **0 TESTS COLLECTED** (E-0.8-018).
* **Hallazgo:** Infraestructura de chaos testing y recovery tests existe. Ejecutabilidad/pasado/convergencia global NO DEMOSTRADOS. Solo test_recovery_flow validado empíricamente en esta auditoría.
* **Severidad:** N/A (evidencia reutilizable)

### Evidencia E-0.8-012: Ventana duplicate-effect: detalle técnico
* **Archivo:** `apps/llm_workers/__main__.py:173-178`
* **Observed:**
  ```
  L173: raw_response = self.processor.execute(node)   # I/O al LLM
  L175: if heartbeat.lease_lost.is_set():             # check
  L176:     raise OptimisticLockError(...)            # split-brain prevention
  L178: self.event.append_wal(...)                    # journal
  ```
* **Hallazgo:** Si el proceso crash entre L176 y L178, el I/O al LLM se ejecutó (y se pagó) pero no se journaleó. El reconciler, al ver el lease expirado, lo rematerializará (doble cobro). El economic replay (E-0.8-003, `get_replay`) mitiga parcialmente: si el mismo content_hash + prompt_v + model_v ya fue journaleado en una ejecución previa, no se repaga. Pero en la primera ejecución, la ventana existe.
* **Mitigación:** NO se prescribe. journal-first es una técnica candidata que por sí sola NO establece exactly-once external effects. **DC-08** debe decidir entre: (a) idempotency key del proveedor, (b) deduplicación externa, (c) semántica at-least-once explícita, (d) recuperación basada en replay, (e) aceptar explícitamente duplicación potencial, (f) mecanismo de confirmación del proveedor.
* **Severidad:** P1

### Evidencia E-0.8-013: Parámetros temporales explícitos
* **Archivos:** `__main__.py`, `reconciler.py`, `control_repo.py`, `fsm_repository.py`, `sweeper.py`
* **Observed:**
  - Task lease TTL inicial: `now + 300` (5 min) — `control_repo.py` L39
  - Task lease renewal: `additional_ttl_sec = 300` default — `control_repo.py` L102
  - Heartbeat interval (worker): `ttl_sec * 0.25 = 30s` — `__main__.py` L41
  - Heartbeat interval (reconciler): `ttl_sec * 0.3 = 36s` — `reconciler.py` L27
  - Leadership TTL: `120s` — `reconciler.py` L17
  - STALLED quarantine: `threshold_sec=3600` → FAILED_FATAL — `fsm_repository.py` L69, `sweeper.py` L60
  - Reconciler sweep sleep: `random.uniform(25.0, 35.0)` — `reconciler.py` L102, L120
  - Worker backoff: `base_sleep=1.0`, `max_sleep=4.0`, `1.2^consecutive_idle` — `__main__.py` L93-94, L113
  - PRAGMA busy_timeout: `30000` (30s) consistente en todos los entry points
* **Hallazgo:** Todos los parámetros temporales están explícitos y parametrizados. Insumo directo para experimentos de F0-D.
* **Severidad:** N/A (informativo)

### Evidencia E-0.8-014: PRAGMAs SQLite: configuración observada
* **Archivos:** `infra/db/bootstrap.py:43-55`; `infra/db/connection.py:59-61`
* **Observed:**
  - `PRAGMA journal_mode=WAL` (todos los DBs) — bootstrap.py:44, connection.py:59
  - `PRAGMA synchronous=NORMAL` (todos los DBs) — bootstrap.py:45, connection.py:60
  - `PRAGMA busy_timeout=30000` (30s) — bootstrap.py:46, connection.py:61
  - `PRAGMA wal_checkpoint(TRUNCATE)` al bootstrap — bootstrap.py:55
  - Worker aplica `PRAGMA busy_timeout=30000` a queue/evt/mat — main.py:216
  - Sweeper aplica `PRAGMA busy_timeout=15000` a fsm/queue — sweeper.py:51-52
* **Hallazgo:** Configuración OBSERVED: WAL + NORMAL + busy_timeout. **Optimalidad para workload objetivo NO DEMOSTRADA** (requiere benchmark comparativo; Benchmark Before Optimization).
* **Severidad:** N/A (informativo)

### Evidencia E-0.8-015: STALLED quarantine con recovery dual y Escalation Threshold
* **Archivos:** `core/execution/state.py` L21, L36-39; `runtime/recovery.py:12-59`; `runtime/sweeper.py:59-77`; `runtime/resumer.py:10-49`
* **Observed:**
  - `DocumentState.STALLED` con transiciones válidas a cualquier estado no-terminal.
  - `StallDocumentCommand` guarda `suspended_state` original (handlers.py:79).
  - **Recovery automático:** `AbandonedProcessWatchdog.execute_sweep(threshold_sec=3600)` detecta docs en estados activos con updated_at < now - 3600s y los mueve a STALLED (recovery.py:19-45).
  - **Escalation terminal:** Sweeper mueve docs STALLED > 3600s a FAILED_FATAL (sweeper.py:60-75). Esto es **escalation threshold**, no recovery: FAILED_FATAL es terminalización.
  - **Recovery manual:** `OnDemandResumeManager.rescue_stalled_document` transiciona STALLED → `suspended_state` via CAS (resumer.py:17-49). Valida que `current_state == "STALLED"` antes de reanudar.
* **Hallazgo:** Mechanism exists OBSERVED. Recovery convergence CONFIRMED en escenario testeado (E-0.8-017).
* **Severidad:** N/A (fortaleza observada)

### Evidencia E-0.8-016: Orden completo de _process_task y ventanas de crash
* **Archivo:** `apps/llm_workers/__main__.py:137-198`
* **Observed:** Orden de ejecución completo:
  1. L148: `ast_registry.get_node` (in-memory)
  2. L158: `materialized.get_projection_status` (skip si CURRENT)
  3. L165: `event.get_replay` (economic replay check)
  4. Si no replay:
     - L171: `TaskLeaseHeartbeat` context manager
     - L173: `processor.execute(node)` ← **I/O EXTERNO (LLM)**
     - L175: check `heartbeat.lease_lost`
     - L178: `event.append_wal` ← journal
     - L188: normalización (TextNormalizer o equation skip)
     - L192: `materialized.upsert_projection` ← materialized plane
     - L197: `control.mark_task_completed` ← control plane ack
* **Hallazgo:** Mapa de ventanas de crash CONFIRMED: (a) execute→append_wal (DUPLICATE_EFFECT), (b) append_wal→upsert (rematerialización), (c) upsert→ack (re-reconciliación idempotente).
* **Severidad:** P1

### Evidencia E-0.8-017: Recovery convergence validada en un escenario concreto
* **Archivo:** `tests/integration/test_recovery_flow.py`
* **Executed:**
  ```
  python -m pytest tests/integration/test_recovery_flow.py::TestRecoveryAndResumeEndToEnd::test_complete_crash_recovery_and_resume_lifecycle -v
  ```
* **Result:**
  ```
  test_complete_crash_recovery_and_resume_lifecycle PASSED [100%]
  1 passed in 1.23s
  ```
* **Hallazgo:** FACT: el escenario concreto pasó. NO DEMOSTRADO: que todo el data plane converja tras cualquier crash relevante. Alcance: FSM + flujo de resume en el escenario testeado.
* **Severidad:** N/A (fortaleza confirmada en alcance limitado)

### Evidencia E-0.8-018: Epoch fencing NO DEMOSTRADO
* **Archivo:** `tests/test_fencing.py`
* **Executed:**
  ```
  python -m pytest tests/test_fencing.py -v
  ```
* **Result:**
  ```
  collected 0 items
  no tests ran in 0.35s
  ```
* **Hallazgo:** El archivo `tests/test_fencing.py` existe pero no tiene tests ejecutables (collected 0 items). Epoch fencing permanece como NO DEMOSTRADO porque no hay tests que lo validen. **GAP-0.8-06**.
* **Severidad:** P1 (gap de validación)

### Evidencia E-0.8-019: CQRS lineage estructural CONFIRMADO; integridad bajo crash PARTIAL
* **Archivo:** `infra/db/event_repo.py:28-53`; `infra/db/materialized_repo.py:28-40`
* **Observed:**
  - Event Plane: `append_wal(execution_id, document_id, node_id, content_hash, raw_response, prompt_v, model_v, projection_v, lifecycle)` → INSERT + commit
  - Materialized Plane: `upsert_projection(document_id, ast_hash, node_id, content_hash, normalized_text, normalized_hash, projection_v)` → upsert con version check
  - Ciclo completo: Event Plane escribe → Worker normaliza → Materialized Plane upsertea → Assembler lee
* **Hallazgo:** Presencia y lineage estructural CONFIRMED (ciclo Event Plane → Materialized Plane verificado). Integridad bajo crash PARTIAL (GAP-0.8-04: ventana execute→append_wal viola INV-JOURNAL; crash en esa ventana produce efecto externo sin journal).
* **Severidad:** N/A (fortaleza estructural confirmada, gap de integridad bajo crash documentado)

### Evidencia E-0.8-020: Economic replay: mecanismo presente con clave de dedup intencional
* **Archivo:** `infra/db/event_repo.py:28-38`
* **Observed:**
  - `get_replay(content_hash, prompt_v, model_v)` busca por `content_hash + prompt_version + model_version`.
  - La clave de dedup es **intencional**: deduplicación económica por contenido y versiones de prompt/modelo.
  - El contexto está capturado en `prompt_v`/`model_v`; si el contexto cambia, cambia la versión de prompt y el replay no aplica.
  - Que dos tasks con mismo contenido y mismas versiones compartan replay es **el comportamiento deseado** (misma entrada ⇒ misma salida esperada bajo determinismo).
* **Hallazgo:** Mecanismo de economic replay CONFIRMADO (presente y funcional). Límite operativo: no cubre crash-before-journal en primera ejecución (no hay registro previo compatible). Este límite ya está documentado en E-0.8-003/E-0.8-012.
* **Severidad:** N/A (informativo, límite documentado)

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-0.8-01 | Reconciler usa jitter 25-35s contra thundering herd | Bajo | DOCUMENTADA |
| OBS-0.8-02 | Worker usa backoff exponencial con jitter | Bajo | DOCUMENTADA |
| OBS-0.8-03 | busy_timeout consistente por entry point | Bajo | OBSERVADA |
| OBS-0.8-04 | Assembler con _fail_document_safely como fallback | Medio | OBSERVADA |
| OBS-0.8-05 | test_recovery_flow pasa; test_fencing sin tests ejecutables | Medio | DOCUMENTADA |
| OBS-0.8-06 | Rate limiter mitiga refill negativo con max(0.0, ...) | Bajo | DOCUMENTADA |
| OBS-0.8-07 | TaskLeaseHeartbeat con conexión SQLite dedicada (self-lock) | Bajo | OBSERVADA |
| OBS-0.8-08 | Clave de replay intencional; límite = crash-before-journal | Bajo | DOCUMENTADA |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.8-01** (P1) | Coordinated shutdown capability NO DEMOSTRADA; implementación nominal no encontrada. Activo reclamado por Charter §6. | E-0.8-009 | Charter §6 | Fase 18: decisión de arquitectura DC-13; sin solución prescrita | OPEN |
| **GAP-0.8-02** (P1) | Circuit Breaker sin persistencia: STATE_LOSS TOTAL de estado operacional en restart. | E-0.8-007 | Resiliencia | Fase 18: DC-08 decide mecanismo; F0-D cuantifica impacto | OPEN |
| **GAP-0.8-03** (P1) | Profile Store sin persistencia (DF-34): STATE_LOSS TOTAL; reconstrucción no demostrada. | E-0.8-008 | Recovery | Fase 18: decisión de arquitectura bajo modelo de concurrencia elegido; F0-D cuantifica | OPEN |
| **GAP-0.8-04** (P1) | INV-JOURNAL violado estructuralmente: efecto externo antes que journal; DUPLICATE_EFFECT y ECONOMIC_WASTE potenciales no cuantificados. | E-0.8-003, E-0.8-012 | Charter §4 | Fase 18: DC-08 decide mecanismo post-F0-D | OPEN |
| **GAP-0.8-05** (P2) | Telemetry: TELEMETRY_LOSS residual de queue no flusheada (no acotada por batch size). | E-0.8-010 | Observabilidad | Fase 18: decisión de arquitectura; sin solución prescrita | OPEN |
| **GAP-0.8-06** (P1) | Epoch fencing NO DEMOSTRADO: test_fencing colecta 0 tests. | E-0.8-018 | Recovery validation | Fase 18: instrumentación de tests / F0-D experimentos | OPEN |
| **GAP-0.8-07** (P1) | Zombie recovery de task lease NO DEMOSTRADO: mecanismo observado sin test específico. | E-0.8-001 | Recovery validation | Fase 18: instrumentación de tests / F0-D experimentos | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.1-B | Cliente HTTP coopera con asyncio.cancel() | **NO VERIFICABLE** | adapters.py sin timeouts/CancelledError visibles | F0-D ejecución controlada |
| H-0.2-B | Journal precede al efecto externo | **RECHAZADA** | E-0.8-003 | GAP-0.8-04 |
| H-0.8-A | Control Plane posee zombie write prevention | **OBSERVADA (mecanismo presente)**; convergencia NO DEMOSTRADA | E-0.8-001 (OptimisticLockError en 3 puntos) | GAP-0.8-07: falta validación empírica de convergencia |
| H-0.8-B | Event Plane posee mecanismo de economic replay | **CONFIRMADA (mecanismo presente)** | E-0.8-003, E-0.8-020 | No cubre crash-before-journal en primera ejecución |
| H-0.8-C | Recovery tests existen y son reutilizables | **CONFIRMADA (existencia + un escenario pasado)** | E-0.8-011, E-0.8-017 | Convergencia global NO DEMOSTRADA |
| H-0.8-D | Tras crash en la ventana execute→append_wal, el reconciler re-ejecuta el efecto externo bajo las condiciones de recuperación observadas (sweep → mark_zombie_recovered → PENDING → replay-miss → execute) | **CONFIRMADA como inferencia estructural trazada** | E-0.8-003, E-0.8-012, E-0.8-016, control_repo.py:153-176 | Frecuencia y ECONOMIC_WASTE NO DEMOSTRADOS → F0-D |
| H-0.8-E | Epoch fencing funciona correctamente | **NO DEMOSTRADO** | E-0.8-018 | GAP-0.8-06 |
| GAP-0.1-03 | Threads residuales post-shutdown | **NO VERIFICABLE** | join(timeout=2.0) sin verificación total | F0-D |
| GAP-0.2-04 | Coordinación transaccional append_wal vs efecto externo | **RECHAZADA (orden inverso demostrado)** | E-0.8-003 | Se cierra como GAP-0.8-04 |
| DF-34 | ProfileStore in-memory con costo real de recovery | **CONFIRMADA en nivel FACT** | E-0.8-008 | GAP-0.8-03; costo → F0-D |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué sobrevive, qué se pierde y cómo intenta recuperarse?
Sobrevive: todo lo persistido en SQLite WAL (leases, FSM, event WAL, proyecciones, buckets). Se pierde: estado operacional in-memory (CB, Profile Store) y telemetría residual de queue. Intenta recuperarse: reconciler (zombies, rematerialización), sweeper (escalation), resumer (manual), economic replay (dedup). Convergencia: validada solo en el escenario testeado.

### 16.2 ¿Qué activos reclamados por Charter §6 están presentes?
- **FSM:** PRESENTE con convergencia validada en un escenario.
- **Reconciler:** PRESENTE con fencing NO DEMOSTRADO.
- **Chaos runner:** PRESENTE sin ejecutar.
- **Supervisor:** Implementación nominal NO ENCONTRADA; capacidad NO DEMOSTRADA (GAP-0.8-01).

### 16.3 ¿Qué hipótesis de HITO_0.1/0.2 se cierran?
- **H-0.2-B:** RECHAZADA (INV-JOURNAL violado, GAP-0.8-04).
- **GAP-0.2-04:** Cerrada como GAP-0.8-04.
- **DF-34:** Confirmada en nivel FACT.
- **H-0.1-B y GAP-0.1-03:** NO VERIFICABLE con destino F0-D.

### 16.4 ¿Qué taxonomía de pérdida se aplica?
§7.3: DATA_LOSS (ninguno demostrado), STATE_LOSS (CB, ProfileStore, telemetry), WORK_LOSS y DUPLICATE_EFFECT (potenciales en ventana INV-JOURNAL), ECONOMIC_WASTE (NO CUANTIFICADO, F0-D), TELEMETRY_LOSS (residual).

### 16.5 ¿Qué evidencia es reutilizable en F0-D?
chaos_runner (game_day_1), test_recovery_flow (pasado), test_fencing (a instrumentar), parámetros temporales de E-0.8-013, y la cadena causal de H-0.8-D como sujeto de cuantificación económica.

### 16.6 ¿Qué decisiones quedan separadas y dónde?
- **DC-08:** Write-policy SQLite + mecanismo de cierre de INV-JOURNAL + persistencia de CB.
- **DC-13:** Coordinated shutdown / daemon lifecycle orchestration.
- **DC-01:** Fork de concurrencia (recibe evidencia de durabilidad).
- **DC-02:** Mantiene su significado vigente (HITO_0.4).
- **DF-34:** Carry-forward de ProfileStore.
Ninguna se resuelve en F0-C.

### 16.7 ¿Qué NO afirma este HITO?
Convergencia global de recovery; costo económico de ventanas; determinismo científico; optimalidad de configuración SQLite; efectividad universal de economic replay; existencia o imposibilidad de coordinated shutdown por otra composición no auditada.

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO ADR/NADR

| Regla | Fuente | Required | Observed | Estado | Evidencia |
|---|---|---|---|---|---|
| FSM durabilidad | NADR-09 | Transiciones atómicas | SQLite + CAS + WAL | OBSERVED | E-0.8-005 |
| Event Log integridad | NADR-09 | Append-only | append_wal con commit | OBSERVED | E-0.8-003 |
| Fail fast | ENGINEERING §IV | Errores explícitos | OptimisticLockError en 3 puntos | OBSERVED | E-0.8-001 |
| Atomicidad healing | NADR-07 | Sin mutación no verificada | Ventana execute→append_wal sin journal | PARTIAL | E-0.8-012 |
| CQRS linaje | NADR-08 | Coordinación durable | Tres planos con lineage alineado | Lineage estructural CONFIRMED; integridad bajo crash PARTIAL (GAP-0.8-04) | E-0.8-019 |
| Determinismo científico | ADR Maestro §5 / INV-SCI-1 | Invariancia bajo schedule/concurrencia/cache | No variada ni medida | NO DEMOSTRADO (M1, HITO_0.4) | E-0.8-014 |
| INV-JOURNAL | Charter §4 | Intención recuperable previa al efecto externo | Orden inverso demostrado | FAIL (estructural) | E-0.8-003 |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia | Estado | Fase destino |
|---|---|---|---|---|
| **DC-01** | Fork de concurrencia | E-0.8-001, E-0.8-002 | Durabilidad observada; concurrencia no medida | Fase 18 |
| **DC-02** | Parámetros de runtime en identidad científica (vigente HITO_0.4) | E-0.8-019 | Lineage estructural CONFIRMED | Fase 18 |
| **DC-08** | Write-policy SQLite + cierre INV-JOURNAL + persistencia CB *(DC compuesto heredado de HITO_0.2 v1.2.0; podría requerir subdivisión en ADR_F18_MASTER si las decisiones divergen)* | E-0.8-003, E-0.8-007, E-0.8-012, E-0.8-014 | Alternativas enumeradas sin decisión | Fase 18 post-F0-D |
| **DC-13** | Coordinated shutdown / daemon lifecycle | E-0.8-009 | Capacidad NO DEMOSTRADA | Fase 18 |
| **DF-34** | ProfileStore durable (carry-forward) | E-0.8-008 | FACT confirmado; costo → F0-D | Fase 18 |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Categoría de pérdida | Impacto | Evidencia |
|---|---|---|---|
| Duplicate-effect post-crash en ventana execute→append_wal | DUPLICATE_EFFECT / ECONOMIC_WASTE | Alto (NO CUANTIFICADO) | E-0.8-003, E-0.8-012, H-0.8-D |
| Reintentos post-restart con CB en CLOSED | ECONOMIC_WASTE | Medio (NO CUANTIFICADO) | E-0.8-007 |
| Re-inferencia de perfiles tras restart | WORK_LOSS / ECONOMIC_WASTE | Medio (NO CUANTIFICADO) | E-0.8-008 |
| Shutdown descoordinado entre daemons | WORK_LOSS potencial | Medio | E-0.8-009 |
| Telemetría residual perdida | TELEMETRY_LOSS | Bajo | E-0.8-010 |
| Fencing y zombie recovery sin validación | Riesgo de convergencia no probada | Medio | E-0.8-001, E-0.8-018 |

---

## 21. CIERRE DEL HITO 0.8

**Estado del HITO:** FROZEN v1.4.0
**Condición de cierre cumplida:** Matriz estructural y de ventanas con convergencia por activo y taxonomía formal de pérdida; 20 evidencias con estructura forense explícita (Observed/Required/Hallazgo/Severidad); 7 gaps con destino de decisión (sin solución prescrita); 10 hipótesis cerradas o con destino explícito; decisiones separadas en DC-08 y DC-13 sin reasignar IDs congelados; DC-08 documentado como DC compuesto; severidades alineadas a taxonomía (P0 reservado a invariantes/certificación); frontera F0-C/F0-D explícita; cierre sin adjudicar convergencia global, costo económico ni determinismo científico.
**Verificación de cadena de gobernanza:** Charter §4 y §6 → HITO_0.1 v1.2.0 → HITO_0.2 v1.2.0 → HITO_0.4 v1.3.0 → este HITO v1.4.0 → F0-D → DC-08/DC-13 → ADR_F18_MASTER.
**Contradicciones con HITOs previos:** Ninguna; se restauran y respetan significados vigentes de DC-02/DC-08/DC-13.
**Siguiente paso recomendado:** F0-D (Waste/FinOps Map): cuantificar ECONOMIC_WASTE de la ventana execute→append_wal (H-0.8-D), costo de STATE_LOSS en CB/ProfileStore, y TELEMETRY_LOSS; ejecutar experimentos controlados de convergencia (zombie recovery, fencing) reutilizando chaos_runner; alimentar DC-08 y DC-13 con datos antes de decidir.

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
| **0.8 F0-C State Durability & Recovery Map** | **FROZEN v1.4.0** | **Matriz de durabilidad (unificada definitiva)** |

**Etapa 3 parcialmente cerrada (F0-C completo).** Falta **F0-D (Waste/FinOps Map)** para cerrar la Etapa 3 antes del ADR Master.