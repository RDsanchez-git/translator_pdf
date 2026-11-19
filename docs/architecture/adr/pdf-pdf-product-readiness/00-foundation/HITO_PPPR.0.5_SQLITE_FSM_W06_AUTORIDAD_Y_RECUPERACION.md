# HITO_PPPR.0.5_SQLITE_FSM_W06_AUTORIDAD_Y_RECUPERACION.md

**Estado:** FROZEN v1.0.3  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** 2026-11-19  
**Fase:** PPPR — Fase 0 transversal de `pdf-pdf-product-readiness`, no una fase nueva del roadmap.  
**Tipo de artefacto:** Forensic Flow Audit (autoridad, persistencia, estados, W06 y recovery).  
**Naturaleza:** Read-only; no modifica producción, datos reales, corpus, tests ni decisiones de diseño.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@1e4c767eb60d46f37e733c3af85a28dfe76f7f38`, con PPPR.0.1–0.4 FROZEN.  
**Evidencia Forense Vinculante:** Metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y Atlas; NADR-F18-01 (identidades), NADR-F18-02 (ejecución acotada), NADR-F18-03 (autoridad/efectos inciertos), NADR-F18-04 (durabilidad/idempotencia), NADR-F18-05 (exposición y observabilidad), ADR-F18.2 FROZEN; los HITOs PPPR.0.1–0.4 congelados.  
**Mandato:** auditar **la ruta soportada** OCR→G3→G5 en cuanto a propietarios de estado, `FSMRepository`, SQLite `fsm.db/queue.db/event.db/materialized.db/rate_limits.db`, identidad del intento, leases y epochs, pre-efecto/pos-efecto W06, receipt/manifest, recuperación, proyecciones y transición FSM; distinguir implementación actual, evidencia de testigos y obligaciones F18, sin volver a ejecutar el antiguo pipeline.  
**Síntesis:** El G3 usa receipts y leases durables en `queue.db`, publicación por commits locales y cuarentena W06 sin retry ciego. Tres GAP P1 locales OPEN: UNKNOWN sin escalamiento configurable, lease no revalidado tras semáforo y sweeper configurado en Compose con selección/transición de FSM contradictorias. Sin pruebas comerciales ni certificación.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura desde merge del PR #69 con inspección directa de root G3, SQL/repositories, reconciler, staged publication, F18 NADR-03/04 y testigos W06/B3/B4. 18 E-IDs iniciales, 8 hipótesis por cerrar; NO tests ejecutados, NO FROZEN ni GAP prematuro. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Segunda pasada: 26 E-IDs, 2 P1 locales y fichas §4.7; consumidores UNKNOWN y CLI, lease→semáforo→provider, reconcilers y sweeper. NADR-F18-03/04 y ADR-F18.2 reconciliados con ruta vigente. NOT_RUN, no FROZEN. |
| 1.0.2-IN_PROGRESS | 2026-11-19 | Tercera pasada: 34 E-IDs, tercer GAP P1 relativo a sweeper Compose, clasificación de ventanas W1–W8 y reconciliación de testigos. Sin ejecución ni FROZEN; pendientes hipótesis terminales y DQ/DC. |
| 1.0.3-FROZEN | 2026-11-19 | Cierre conforme §8.1–8.2: 34 E-IDs, 3 fichas P1, 3 GAP P1 locales OPEN, H-0.5-A…I terminales, 4 DQ, 3 DC, ventanas W1–W8 y no-regresión F18/HITOs previos; sin tests, producción ni PASS. |

## 1. RESUMEN EJECUTIVO

Se completó la auditoría forense de propiedad de estado de la ruta seleccionada. El OCR almacena un AST y un `ChunkPlan` con context snapshots; G3 recupera la generación validada, reclama tareas en `queue.db` con leases, llama al proveedor únicamente para `TRANSLATE/PARTIAL`, guarda un resultado estructurado en receipt durable y publica los nodos por una secuencia local `queue.db → materialized.db → queue.db → fsm.db`.

**Hallazgo central:**

> En el G3 vigente, los receipts verificados y los estados de cuarentena sustituyen la antigua inferencia «sin evento, entonces no hubo efecto»; la coherencia de publicación se recupera mediante pasos locales, **no** una transacción distribuida ni una garantía de no duplicación comercial.

**Defectos dominantes P1 LOCAL:** **GAP-0.5-01** (E-019/022/026: UNKNOWN sin escalamiento, NADR-F18-03 R11); **GAP-0.5-02** (E-020/021: lease no revalidado al inicio del efecto, R2); **GAP-0.5-03** (E-023/032: sweeper declarado en Compose inspecciona estados no STALLED y transiciona a FAILED_RETRYABLE sin corroborar receipts, NADR-F18-04 R8). No se acredita duplicación de efectos ni daño real.

**Veredicto de cierre:** 34 evidencias, 3 GAP P1 OPEN y garantías locales de receipts, W06, replay y FSM delimitadas. El sweeper tiene conectividad declarada en Compose, sin ejecución comprobada del contenedor. **FROZEN documental**, no certificación del producto ni aprobación de implementación.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **Observed:** lectura directa de `main@1d21cfe`, separando código activo, contratos de pruebas offline y antecedentes F18. No se ha accedido a ninguna base del usuario.
- **Required:** F18-NADR-03 §5.1–5.6 (autoridad, incertidumbre y recuperación), F18-NADR-04 §5.1–5.5 (durabilidad/confirmación/idempotencia), F18-NADR-01 (identidades) y reglas de gobierno FROZEN. Se contrastarán consumidores antes de declarar incumplimientos.
- **Decision:** D-1/D-2 fijaron CLI→OCR Router→`runtime/engine.py`→G5. Esta elección no ordena volver a la ruta CQRS anterior ni crear una segunda FSM.
- **Garantía limitada:** `PRAGMA journal_mode=WAL; synchronous=NORMAL` se ha observado, pero NO demuestra inmunidad a power loss/fallo físico. CAS SQL ≠ cancelación de una llamada comercial ya iniciada. No se declara atomicidad entre archivos SQLite separados.
- **NOT_RUN:** tests, Docker, crash injection, SDK del LLM, compilador, SQLite de producción y corpus/GT. Los tests se examinan como evidencia de **intención/cobertura**, no se les atribuye PASS actual.
- **Perímetros ajenos:** G3 modelo/prompt/tokens (PPPR.0.4), G5 y salida física (PPPR.0.6), hosting/secretos/volúmenes (PPPR.0.7), prueba científica (PPPR.0.8).

## 3. ALCANCE AUDITADO — PERÍMETRO FINAL

| Frontera | Código primario y propiedad | Estado de esta pasada |
|---|---|---|
| Admission/OCR→G3 | `apps/ocr_router/__main__.py::_process_document`, `infra/db/context_snapshot_repo.py::enqueue_verified` | **AUDITADO focal**: atomicidad local de plan + tasks + snapshots; otro HITO cubre extracción |
| G3 root y workers | `runtime/engine.py::run_pipeline`; `runtime/chunk_staging.py::stage_claimed_unit`; `apps/llm_workers/sync_bridge.py::execute_chunk` | **AUDITADO**: semáforo y frontera pre-I/O, E-020/021 |
| Autoridad de tarea | `infra/db/control_repo.py::{pick_task,stage_chunk_result,mark_g3_external_unknown,recover_expired_g3_task}` | **AUDITADO focal**: lease, CAS, UNKNOWN y fencing |
| FSM documento | `infra/db/fsm_repository.py`, `core/execution/handlers.py` | **AUDITADO focal**: CAS versionado, límites de transacción |
| Recuperación/reconciliador | `apps/daemons/reconciler.py`, `infra/db/system_repo.py`, `runtime/{recovery,resumer,sweeper}.py`, `docker-compose{,.runtime}.yml` | **AUDITADO focal**: UNKNOWN, reconciler y sweeper de runtime configurado; distinto de CLI foreground |
| Publicación | `infra/db/staged_publication.py`, `runtime/publication_pipeline.py` | **AUDITADO**: staged→materialized→queue→FSM, replay local |
| SQLite/WAL y cuota | `infra/db/{connection,schema_queue,schema_fsm,schema_event,context_snapshot_repo}.py/sql`, `infra/resilience/thread_owned_sqlite_rate_limit_store.py` | **AUDITADO focal**; escritura real y power-loss NO VERIFICABLE |
| Event plane histórico | `infra/db/{event_repo,materialized_repo}.py`, rutas legadas del reconciler | **AUDITADO para desambiguar consumidor**, no sustituye G3 vigente |
| Tests versionados | W06, B3 receipts/publication, B4 recovery/fencing, SQLite ownership/factory | **LEÍDOS · NOT_RUN**; algunos fakes/SQLite temporal |
| Normativa previa | NADR-F18-01…05, ADR-F18.2 y corte histórico de F18.2 | **RECONCILIADO POR DELTA** (§17); no transferir GAP histórico por homonimia |
| G5/output y costeo de I/O | Otros HITOs PPPR | **REFERENCIADO**; sin certificación física ni económica |

**Perímetro suficiente para el mandato estático:** root OCR→G3, control/queue, FSM, reconciler, sweeper declarado en Compose, publicación y testigos auditados por código; G5 físico, host, LLM, facturación y corpus explícitamente referenciados o NO VERIFICABLE con destinos (§15). No se introducen matrices externas ni se presume exhaustividad de consumidores privados.

## 4. FUENTES DE EVIDENCIA

**Código primario:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`: `runtime/{engine,chunk_staging,publication_pipeline,recovery,resumer,sweeper,operational_visibility}.py`, `apps/daemons/reconciler.py`, `apps/llm_workers/sync_bridge.py`, `apps/cli/{main,pdf_product}.py`, `core/execution/{state,handlers,visibility}.py`, `infra/db/{control_repo,fsm_repository,system_repo,staged_publication,context_snapshot_repo,connection,event_repo,materialized_repo}.py`. **Composición:** `docker-compose.yml` y `docker-compose.runtime.yml` declaran sweeper; la CLI foreground no lo instancia. No se verificó un host vivo.

**Normas:** `docs/architecture/adr/phase-18/NADR/NADR-F18-01.md` (identidades), `NADR-F18-02.md` (concurrencia), `NADR-F18-03.md` §5 R1–R23 (autoridad e incertidumbre), `NADR-F18-04.md` §5 R1–R16 (persistencia recuperable), `NADR-F18-05.md` (observabilidad), y F18 ADR Maestro/ADR_F18_2 FROZEN. **Histórico como testigo, no estado actual:** `HITO_0.8_F0-C_State_Durability_Recovery_Map.md` y `HITO_18.2.1_CRASH_WINDOW_FINOPS_ANALYSIS.md`, con distintos cortes de código.

**Tests solo leídos:** `tests/integration/{test_w06_g3_uncertain_effect_offline,test_g3_b4_3b_publication_recovery,test_g3_b4_9_reconciler_fencing,test_g3_b3_3a_staged_publication,test_g3_b3_3b_finalization,test_g3_wal_stage_write_scope,test_pdf_pdf_fsm_transaction_ownership,test_pdf_pdf_sqlite_contracts,test_g3_b4_7b_sqlite_quota_thread_owner}.py`. Sin ejecución, sin CI acreditada y sin proveedor real.

## 5. MAPA DE FLUJOS OBSERVADOS — COMPOSICIÓN SELECCIONADA

```text
CLI → OCR Router (_process_document)                           [PPPR.0.1/0.2]
  → ASTRegistry + DurableContextPlanRepository.enqueue_verified
     queue.db: plan + tasks + context snapshots en transacción local
  → document_fsm (fsm.db)                          [CAS propio, DB distinta]
  → G3 runtime/engine.py::run_pipeline
     → load_verified(AST, plan, context) antes de paid provider
     → seleccionar tareas runnable PENDING/RETRYABLE_ERROR
     → ControlPlaneRepository.pick_task:
        BEGIN IMMEDIATE, PROCESSING + lease_owner + execution_id + TTL 300s
     → stage_claimed_unit:
        lease snapshot válido antes de inferir
        PRESERVE: sin LLM | TRANSLATE/PARTIAL: SyncProviderBridge
        → stage_chunk_result: response binding, checksum y receipt durable
           + task_state RESULT_STAGED bajo transacción local queue.db
        ERRORES de inferencia inciertos → mark_g3_external_unknown (no retry)
     → si todas RESULT_STAGED:
        publish_staged_plan → materialized.db (todas proyecciones juntas)
        finalize_published_plan → queue.db (COMPLETED en una transacción)
        DocumentCommandHandler/MarkAssemblyReady → fsm.db (CAS)
     → si todas COMPLETED: verificar publicación y avanzar FSM sin paid provider
  → G5 (PPPR.0.6)

apps/daemons/reconciler.py:
  → lease líder global, epoch, snapshot CAS
  → expired G3 + sin receipt:
       PRESERVE probado → PENDING, seguro sin efecto comercial
       INFERENCE/ambiguo → G3_EXTERNAL_UNKNOWN, sin reintento automático
  → solo tareas legacy sin ChunkPlan consultan event.db por generación/WAL
```

**Semántica central:** hay *confirmaciones recuperables locales* y puntos de corte entre DBs; **no existe una transacción atómica global** que combine queue, materialized y FSM. El contrato actual busca converger sin volver a pagar por la sola ausencia de una proyección local. No confundir esa propiedad lógica con protección demostrada ante pérdida física de energía.

## 10. REGISTRO DE EVIDENCIA FORENSE — FINAL

| E-ID | Severidad | Observed (archivo::símbolo) | Required/Decision/límite | Estado |
|---|---|---|---|---|
| **E-0.5-001** | P2 | `context_snapshot_repo.py::enqueue_verified` escribe plan, tasks y context snapshots en una única transacción `queue.db`; `load_verified` compara generación/manifest al reabrir. | Atomicidad **local**; no equivale a commit de `fsm.db`. | OBSERVADO |
| **E-0.5-002** | P2 | `engine.py::run_pipeline` verifica AST, hash, manifest y snapshots antes de crear proveedor pago; rechaza falta/drift. | Fallar antes de I/O ante identidad divergente; capacidades GT/fidelidad no probadas. | OBSERVADO |
| **E-0.5-003** | P2 | `control_repo.py::pick_task` usa `BEGIN IMMEDIATE`, estado PROCESSING, `lease_owner`, `execution_id` y expiración de ~300 s confirmados antes de retornar. | NADR-F18-03 §5.1: autoridad recuperable pre-efecto. No acredita detener proveedor en vuelo. | OBSERVADO |
| **E-0.5-004** | P2 | `chunk_staging.py::stage_claimed_unit` coteja unidad/task/lease antes del proveedor y controla `PRESERVE`; invoca `stage_chunk_result` después de inferencia. | Guardias SQL y de protocolo; ventana entre efecto y receipt **no es cerrable por CAS retroactivo**. | OBSERVADO |
| **E-0.5-005** | P2 | `control_repo.py::stage_chunk_result` valida response manifest, checksum, lease-owner, execution-id y version CAS; inserta receipt y marca RESULT_STAGED en la misma transacción. | NADR-F18-04 §5.1/5.2: fuente autoritativa recuperable; no implica sync entre DBs. | OBSERVADO |
| **E-0.5-006** | P2 | `engine.py::chunk_worker_thread` marca `G3_EXTERNAL_UNKNOWN` ante fallos de inferencia no demostrablemente pre-red; `CircuitOpenError` libera tarea pre-provider. | NADR-F18-03 §5.2–5.3: no equiparar desconocido a no iniciado ni reintentar silenciosamente. | OBSERVADO |
| **E-0.5-007** | P2 | `control_repo.py::mark_g3_external_unknown` escribe `error_log` tipado con primer momento/attempt `execution_id`; no requiere TTL vigente y utiliza CAS de owner/attempt. | Representación durable de incertidumbre; **escalamiento automático configurable** aún no demostrado. | OBSERVADO / ABIERTO |
| **E-0.5-008** | P2 | `control_repo.py::find_documents_with_pending_chunks/find_documents_ready_for_g3_recovery` excluye generaciones con UNKNOWN de selección automática. | NADR-F18-03 R9: no retry de resultado incierto. Mecanismo de disposición/alerta todavía por rastrear. | OBSERVADO |
| **E-0.5-009** | P2 | `reconciler.py::_sweep_tasks` envía G3 a `recover_expired_g3_task`; este usa snapshot de lease, epoch líder y FSM PROCESSING; sin receipt, solo PRESERVE se libera y LLM va a UNKNOWN. | NADR-F18-03 R5/R8/R9; recuperar sin inventar que no hubo efecto. | OBSERVADO |
| **E-0.5-010** | P2 | `reconciler.py` usa `EventPlaneRepository` para CQRS legacy; para tareas G3 hace `continue` antes del bloque `get_latest_event`. | No heredar defectos de journal legacy como comportamiento de la ruta actual; cotejar obligación F18 por equivalencia de contrato. | RECONCILIACIÓN |
| **E-0.5-011** | P2 | `staged_publication.py::{publish_staged_plan,finalize_published_plan}` verifica receipts y aplica proyecciones `materialized.db` antes de completar `queue.db`; replay idéntico permitido. | NADR-F18-04 §5.2/5.3, publicación idempotente **local** sin 2PC. | OBSERVADO |
| **E-0.5-012** | P2 | `publication_pipeline.py::advance_staged_document` exige estado homogéneo RESULT_STAGED o COMPLETED y luego hace FSM CAS hacia READY_FOR_ASSEMBLY. | No tratar estados parciales como publicación; commit entre planos separado. | OBSERVADO |
| **E-0.5-013** | P2 | `engine.py::run_pipeline` admite recuperación de documento completamente staged/completed sin inicializar proveedor pago. | Compatibilidad post-crash dentro de ventana lógica; no demuestra power-loss. | OBSERVADO |
| **E-0.5-014** | P2 | `connection.py::get_connection` configura `WAL + synchronous=NORMAL + busy_timeout`, `check_same_thread=True`; `fsm_repository.py` opera con SAVEPOINT y CAS. | NADR-F18-04 R3/R4: política aprobada, no garantía de power-loss. | CONTRATO CONFIRMADO |
| **E-0.5-015** | P2 | `context_snapshot_repo.py` y `staged_publication.py` distinguen transacción local y transacción del caller; `fsm_repository.py::_write_scope` respeta SAVEPOINT anidado. | Atomicidad local, idempotencia y recuperabilidad no son sinónimos. | OBSERVADO |
| **E-0.5-016** | P2 | W06 offline cubre respuesta perdida→UNKNOWN, no segundo llamado, restart y expiración sin receipt; usa fakes y SQLite descartable. | Contrato visible en tests; `NOT_RUN` y no prueba de Groq ni fallos de energía. | TESTIGO |
| **E-0.5-017** | P2 | Tests B3/B4 versionan replay tras crash entre publicación y finalización, fencing de reconciler y rechazo de proyección corrupta/missing receipt. | Cobertura de mecanismos testados por intención; no se heredan resultados CI aquí. | TESTIGO |
| **E-0.5-018** | P2 | `infra/resilience/thread_owned_sqlite_rate_limit_store.py` y test B4/7b aíslan estado de cuotas en hilo owner, distinto de la connection factory compartida. | No confundir cuotas durables con confirmación de cobro externo, ni atribuir thread safety de DB por nombre. | REFERENCIADO |

| **E-0.5-019** | **P1** | `control_repo.py` persiste UNKNOWN y lo excluye de los selectores; `reconciler.py::_sweep_tasks` solo consulta PROCESSING expirado; `engine.py` emite log una vez y la CLI status/resume no dispone UNKNOWN. No hay escalamiento configurable ni revisión recurrente conectados en las interfaces auditadas. | NADR-F18-03 §5.3 **R11** (escalamiento configurable contra olvido silencioso), ADR-F18.2 DC-08b. | **GAP-0.5-01 OPEN** |
| **E-0.5-020** | **P1** | `chunk_staging.py::stage_claimed_unit` compara el timestamp del lease **antes** de `with llm_semaphore:`; tras adquirir el semáforo ejecuta `processor.execute_chunk` sin revalidación durable del owner/attempt; `SyncProviderBridge.execute_chunk` envía al provider sin check adicional. | NADR-F18-03 §5.1 **R2**: autoridad verificable y vigente antes de comenzar efecto externo. Fencing SQL posterior no evita llamada iniciada por lease expirado. | **GAP-0.5-02 OPEN** |
| **E-0.5-021** | P2 | `pick_task` asigna TTL ≈300s; `GLOBAL_LLM_SEMAPHORE` puede esperar si `MAX_CONCURRENT_CHUNKS` excede capacidad global. No se observó un `renew_task_lease` conectado al worker G3. | Interleaving posible, no latencia real ni error proveedor medidos. Contexto E-020. | CONTROL TEMPORAL |
| **E-0.5-022** | P2 | `apps/cli/main.py::handle_status` consulta `document_fsm`, no `chunk_tasks`; `handle_resume` solo reanuda STALLED; `pdf_product.py` exige READY_FOR_ASSEMBLY después de G3. | Un operador puede recibir FSM PROCESSING sin disponer desde la CLI soportada de la causa/acción para UNKNOWN; no se presupone un comando concreto. | CORROBORA GAP-0.5-01 |
| **E-0.5-023** | P2 | `runtime/sweeper.py` declara limpiar STALLED pero `FSMRepository.find_stalled_documents` filtra PARSING/PROCESSING/READY_FOR_ASSEMBLY, nunca STALLED; el `FailDocumentCommand` del handler mapea a FAILED_RETRYABLE, distinto del FAILED_FATAL del log. | Contradicción local en ejecutor auxiliar; conectividad con la ruta producto y obligación a confirmar antes de abrir GAP. | H-0.5-I, NO PROMOVIDO |
| **E-0.5-024** | P2 | Testigos W06/B4 versionados cubren bloqueo de UNKNOWN/restart, CAS, recovered receipts; no incluyen en esos archivos escalamiento configurable ni expiración de lease mientras espera el semáforo hasta iniciar provider. | Testigos offline leídos `NOT_RUN`; ausencia de prueba en estas fuentes no equivale a incidencia comercial. | LÍMITE DE TEST |
| **E-0.5-025** | P2 | `ADR_F18_2.md` v3.3.0 DC-08a/b reutiliza lease como autoridad y acepta incertidumbre conservadora; no obliga a event INTENT ni a disponibilidad de resolución automática del proveedor. `reconciler.py` evita consulta de `event.db` en rama G3. | Evitar falsas reaperturas del journal legacy y una solución innecesaria de transacción distribuida. | RECONCILIADO |
| **E-0.5-026** | P2 | `test_g3_b4_3b_publication_recovery.py::test_g3_scheduler_excludes_unknown_generation` exige selectores vacíos y FSM PROCESSING para una generación con UNKNOWN, incluso si quedan tareas normales. | El bloqueo es una protección correcta contra segundo efecto; su duración indefinida sin escalamiento es el riesgo de GAP-01. Testigo NOT_RUN. | CORROBORA GAP-0.5-01 |
| **E-0.5-027** | P2 | `stage_chunk_result` guarda receipt y RESULT_STAGED en una misma transacción queue.db, con manifest, hash, CAS de lease y rollback ante fallo. | NADR-F18-04 R1–R2/R5: confirmación durable local, no transacción con el LLM. | CONFIRMACIÓN LOCAL |
| **E-0.5-028** | P2 | Sin receipt después de inferencia, `recover_expired_g3_task` separa PRESERVE probado→PENDING de TRANSLATE/PARTIAL→G3_EXTERNAL_UNKNOWN, con epoch/lease/estado FSM. | NADR-F18-03 R5–R9: ausencia de resultado no prueba ausencia de efecto. | W06 CONSERVADOR |
| **E-0.5-029** | P2 | `publish_staged_plan` reconstruye nodos desde receipts, aplica proyecciones y publicación en una transacción materialized.db; replay idéntico se verifica y la divergencia se rechaza. | NADR-F18-04 R5/6/9/10, sin 2PC. | PUBLICACIÓN LOCAL |
| **E-0.5-030** | P2 | `finalize_published_plan` verifica publicación committed y receipts, completa todas las tareas en una transacción queue.db con CAS; rechaza planes mixed o corruptos. | NADR-F18-04 R8/R10–R14; ACK separado de publicación. | FINALIZACIÓN LOCAL |
| **E-0.5-031** | P2 | `advance_staged_document` hace materialized→queue→FSM CAS por commits distintos; `engine.py` detecta todos RESULT_STAGED o COMPLETED antes de inicializar proveedor pago. | Replay de resultados confirmados sin re-inferencia, no atomicidad inter-DB. | CONVERGENCIA ESTÁTICA |
| **E-0.5-032** | **P1** | `docker-compose.yml` habilita `sweeper` y `docker-compose.runtime.yml` lo conserva. `run_sweep_cycle` anuncia purga STALLED; `find_stalled_documents` consulta PARSING/PROCESSING/READY_FOR_ASSEMBLY, no STALLED; `FailDocumentCommand` produce FAILED_RETRYABLE, no el FAILED_FATAL registrado, sin comparar leases ni receipts. | NADR-F18-04 §5.3 R8 exige coherencia en recuperación; ENGINEERING_PRINCIPLES §IV impide informar estados falsos. Host real NO VERIFICABLE. | **GAP-0.5-03 OPEN** |
| **E-0.5-033** | P2 | Tests B3/B4 de crash entre publicación/ACK/FSM y corrupción/mixed/rollback, y W06 con provider fake, versionan las barreras pero están NOT_RUN. | Testigo escrito ≠ ejecución física, SIGKILL, power loss o garantía remota. | TESTIGOS |
| **E-0.5-034** | P2 | `ThreadOwnedSQLiteRateLimitStore` posee DB de cuotas en un hilo; `InferenceMeasurementService` estima tokens, mientras `WorkUnitObservation` es telemetría de estado, sin evidencia de reporte durable de excepción/costo real. | NADR-F18-05 R4–R15 separa actividad cliente, duplicación y costo. Conformidad real de excepción NO VERIFICABLE. | DQ-0.5-04 |

**Severidad final §7.1:** E-0.5-001…034 retienen sus IDs; E-019, E-020 y E-032 son P1 LOCAL por consecuencia contractual, las otras 31 P2 por hechos o límites. E-023 se conserva P2; E-032 acredita conectividad declarativa, no servicio ejecutado. Ningún P0, doble cobro o explotación demostrada.

### Fichas extendidas P1 (§4.7)

#### E-0.5-019 — cuarentena UNKNOWN sin seguimiento configurable conectado

- **Fuente/símbolos:** `infra/db/control_repo.py::{mark_g3_external_unknown,find_documents_with_pending_chunks,find_documents_ready_for_g3_recovery}`; `apps/daemons/reconciler.py::_sweep_tasks`; `runtime/engine.py::run_pipeline`; `apps/cli/main.py::{handle_status,handle_resume}`.
- **Declaración observada:**

```python
# El selector G3 descarta las generaciones con UNKNOWN.
AND NOT EXISTS (
    SELECT 1 FROM chunk_tasks uncertain
    WHERE uncertain.task_state = 'G3_EXTERNAL_UNKNOWN'
)
# El reconciler solo inspecciona PROCESSING expirado.
WHERE task_state = 'PROCESSING'
  AND lease_expires_at < ?
# El G3 registra un log puntual, sin mecanismo de escalamiento.
logger.error("G3_W06_EXTERNAL_UNKNOWN_REQUIRES_OPERATOR: %s", unknown)
```

- **Observed:** `mark_g3_external_unknown` guarda `execution_id`, causa y `first_detected_at` de forma recuperable. Scheduler, recovery normal y CLI inspeccionados no presentan al operador una vía conectada de alarma parametrizable, reapertura informada ni disposición autorizada para esa cuarentena. El reconciler filtra PROCESSING (no UNKNOWN), mientras status/resume operan solo sobre FSM; los logs puntuales no son seguimiento configurable. **Alcance negativo:** solo consumidores/versiones inspeccionados, no procesos externos desconocidos.
- **Required:** NADR-F18-03 §5.3 **R11** impone mecanismo de escalamiento configurable contra olvido silencioso; R9 prohíbe retry automático y R10 preserva trazabilidad. ADR-F18.2 DC-08b no exige progreso automático imposible sin proveedor cooperante, pero sí seguimiento/escalamiento.
- **Decision:** D-1/D-2 define ruta; ADR-F18.2 deja los umbrales a planificación, sin aprobar un umbral fijo ni una infraestructura nueva.
- **Consecuencia:** un documento con UNKNOWN puede permanecer bloqueado indefinidamente y sin seguimiento programado por la composición soportada; protección de no-retry correcta, pero progresión operativa no gobernada. No se atribuye cobro duplicado observado.
- **Severidad/estado:** **P1 LOCAL · OPEN → GAP-0.5-01**. Destino: ADR Maestro/Execution Plan PPPR; reutilizar mecanismos antes de inventar infraestructura.

#### E-0.5-020 — verificación de lease anterior a la espera del semáforo

- **Fuente/símbolos:** `runtime/chunk_staging.py::stage_claimed_unit`, `infra/db/control_repo.py::{pick_task,renew_task_lease,stage_chunk_result}`, `runtime/engine.py::chunk_worker_thread`, `apps/llm_workers/sync_bridge.py::execute_chunk`.
- **Declaración observada:**

```python
if lease.lease_expires_at <= time.time():
    raise ValueError("G3_B4_3A_EXPIRED_LEASE")
# ...
with llm_semaphore:
    raw_response = processor.execute_chunk(plan, unit)
# El bridge luego despacha un future de provider sin revalidación SQL.
```

- **Observed:** el guard compara el snapshot original del `TaskLease` antes del bloqueo del semáforo; el worker no renueva ese lease en esta ruta y no hay otra verificación durable de `owner/execution_id/lease_expires_at` justo al iniciar el efecto. `stage_chunk_result` valida SQL **después** del I/O, sin poder impedir un envío previo.
- **Contrajemplo causal NO ejecutado:** lease válido al llegar al guard; el semáforo permanece ocupado hasta que el lease vence o cambia de owner; al liberarse, el código inicia el provider con autoridad caducada y el CAS posterior puede rechazar el resultado. Es posible sin alegar latencia observada ni doble factura.
- **Required:** NADR-F18-03 §5.1 **R1–R3**, en especial **R2** (autoridad recuperable vigente verificable *antes* del efecto). La pérdida durante un efecto ya comenzado no equivale a cancelación del proveedor.
- **Decision:** ADR-F18.2 ratifica reutilizar lease durable como autoridad; no obliga a un segundo journal ni especifica una implementación nueva.
- **Consecuencia:** la corrección del receipt local no acredita el *external-effect fencing* previo. El modo de concurrencia configurado puede abrir la ventana, aunque los testigos SQL pasen.
- **Severidad/estado:** **P1 LOCAL · OPEN → GAP-0.5-02**. Destino: ADR Maestro/Execution Plan PPPR; testigo offline focal de expiración durante espera si se autoriza.


#### E-0.5-032 — sweeper de Compose y FSM contradictoria (P1)

- **Fuentes/símbolos:** `docker-compose.yml::services.sweeper`, `docker-compose.runtime.yml`, `runtime/sweeper.py::RecoveryDaemon.run_sweep_cycle`, `infra/db/fsm_repository.py::find_stalled_documents`, `core/execution/handlers.py::_get_target_state`.
- **Declaración observada:**

```python
# find_stalled_documents filtra:
WHERE current_state IN ('PARSING','PROCESSING','READY_FOR_ASSEMBLY')
# No incluye STALLED
# sweeper envía FailDocumentCommand y anuncia FAILED_FATAL.
# handler mapea FailDocumentCommand -> FAILED_RETRYABLE.
```

- **Observed:** el servicio está en Compose y su overlay runtime; no está invocado por CLI foreground. Selecciona por antigüedad FSM sin cotejar leases/receipts en queue y no procesa STALLED. El handler mueve a FAILED_RETRYABLE mientras el log informa FAILED_FATAL. No hubo ejecución del contenedor.
- **Required:** NADR-F18-04 §5.3 R8 requiere coherencia entre autoridad y proyecciones tras recuperación; NADR-F18-05 §5.3 R10 impide ocultar insuficiencia observacional; ENGINEERING_PRINCIPLES §IV exige cero fallos silenciosos y trazabilidad, sin regla textual específica sobre nombres de estado.
- **Decision:** F18 adopta convergencia local sin 2PC. Presencia en Compose no demuestra stack activo.
- **Consecuencia:** un documento PROCESSING antiguo puede cambiar a FAILED_RETRYABLE sin corroborar evidencia de queue; un STALLED verdadero no es seleccionado por esa purga. No se observaron cargos, daño ni retries pagados.
- **Severidad:** **P1 LOCAL · OPEN → GAP-0.5-03**; destino ADR Maestro/Execution Plan y verificación de composición PPPR.0.7.

## 11. MATRIZ DE CRASH Y RECUPERACIÓN (NOT_RUN)

| Ventana | Estado al corte | Comportamiento observado/esperable en código |
|---|---|---|
| W1 Claim antes de paid I/O | PROCESSING sin receipt | Expirado: LLM→UNKNOWN; PRESERVE verificable→PENDING; lease no prueba llamada |
| W2 LLM iniciado sin receipt | Resultado externo desconocido | W06 bloquea retry automático; cobro NO VERIFICABLE |
| W3 Receipts parciales | Algunas tareas RESULT_STAGED | La publicación incompleta se rechaza |
| W4 Todos RESULT_STAGED | queue confirmada, materialized pendiente | Se reconstruye desde receipt sin proveedor |
| W5 materialized committed | queue RESULT_STAGED | Replay idempotente de publicación, finalización queue |
| W6 queue COMPLETED | FSM PROCESSING | Revalidación y CAS a READY_FOR_ASSEMBLY sin LLM |
| W7 Mixed/alteración | Plan, hashes o receipts incoherentes | Fail-closed, sin progreso falso |
| W8 Power loss/proveedor remoto | Fuera del testigo estático | WAL+NORMAL aprobado para fallos locales F18, sin exactly-once externo |

**Separación de garantías:** recepción externa, receipt durable, proyección, ACK queue y FSM no son una única transacción. Tests B3/B4/W06 versionados: **NOT_RUN**; no se extrapola SIGKILL o power loss.

## 14. GAPS CONSOLIDADOS — FINAL

| GAP | Defecto observado | Evidencia | Contrato | Destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.5-01** | UNKNOWN bloquea retry pero carece de escalamiento configurable en la composición auditada | **E-0.5-019**, E-022/026 | NADR-F18-03 R11; ADR-F18.2 DC-08b | ADR Maestro PPPR → Execution Plan | **P1 LOCAL · OPEN** |
| **GAP-0.5-02** | Lease verificado antes, no después del semáforo inmediatamente antes de efecto externo | **E-0.5-020**, E-021 | NADR-F18-03 R2; ADR-F18.2 DC-08a | ADR Maestro PPPR → Execution Plan; testigo focal | **P1 LOCAL · OPEN** |
| **GAP-0.5-03** | Sweeper de Compose selecciona estados equivocados, omite receipts/leases y declara FAILED_FATAL cuando realmente mueve a FAILED_RETRYABLE | **E-0.5-032**, E-023 | NADR-F18-04 R8; NADR-F18-05 R10; principios SRE IV | ADR Maestro PPPR → Execution Plan; entorno PPPR.0.7 | **P1 LOCAL · OPEN** |

**No son GAPs de esta ruta:** ausencia de INTENT en el journal legado, falta de 2PC, bloqueo seguro de UNKNOWN o no usar `synchronous=FULL` (F18 aprobó WAL+NORMAL para su modelo de fallos). E-023 mantiene su identidad: E-032 demuestra la conectividad declarativa del sweeper en Compose, sin probar su actividad física. No se crean tareas de implementación prematuras.

## 15. HIPÓTESIS TERMINALES, DQ Y DC (§8.1–8.2)

| ID | Veredicto con frontera de evidencia |
|---|---|
| H-0.5-A | **CONFIRMADA brecha local** UNKNOWN sin escalamiento → GAP-01 |
| H-0.5-B | **RECHAZADA garantía universal** de lease al inicio externo → GAP-02 |
| H-0.5-C | **CONFIRMADA por código** cuarentena W06 sin reintento automático; NOT_RUN |
| H-0.5-D | **CONFIRMADA por código** replay post-receipt sin reinferencia; NOT_RUN |
| H-0.5-E | **CONFIRMADA** separación de commits locales, sin 2PC |
| H-0.5-F | **CONFIRMADA en la ruta inspeccionada** CAS, owner, execution_id y epoch en escrituras; no equivale a fencing físico pre-I/O |
| H-0.5-G | **CONFIRMADA como política F18**, WAL+NORMAL, power loss NO VERIFICABLE → DQ-02 |
| H-0.5-H | **NO VERIFICABLE integralmente**, FinOps/cobro/duplicación/telemetría → DQ-04 |
| H-0.5-I | **CONFIRMADA en Compose** sweeper contradictorio, host no ejecutado → GAP-03 |

### 15.1 Deferred Questions (§8.2)

| ID | Motivo explícito y por qué no bloquea inventario estático | Destino |
|---|---|---|
| DQ-0.5-01 | Duración y efecto real de esperar semáforo con lease caducado: defecto de flujo ya demostrado, impacto no medido | ADR/Execution Plan, test focal offline posterior |
| DQ-0.5-02 | SIGKILL, durabilidad física y power loss no ensayados; F18 excluye power loss como garantía | PPPR.0.7/0.8 |
| DQ-0.5-03 | Compose versionado no prueba contenedores activos ni configuración exacta del host | PPPR.0.7 |
| DQ-0.5-04 | Correlación de excepciones, factura real y duplicación remota requieren cuenta/proveedor y autorización | ADR Maestro, PPPR.0.7/0.8, NADR-F18-05 |

### 15.2 Decision Candidates

| ID | Elección no aprobada | Destino |
|---|---|---|
| DC-0.5-01 | Seguimiento configurable y disposición autorizada de UNKNOWN sin retry ciego | ADR Maestro/Execution Plan |
| DC-0.5-02 | Vigencia del lease justo antes de efecto, incluidos semáforos y expiración | ADR Maestro/Execution Plan |
| DC-0.5-03 | Rol del sweeper, reconciliación queue/FSM y reporting confiable | ADR Maestro/Execution Plan |

**Disposición terminal §8.1–8.2:** H-0.5-A…I tienen veredictos; H-0.5-H es NO VERIFICABLE integralmente y las limitaciones empíricas de H-G/I están en DQ-0.5-02/03. Las DQ registran motivo, no-bloqueo del cierre estático y destino. Ningún diseño ni operación pagada resulta aprobada.

## 16. RESPUESTAS AL MANDATO — FINAL

La cadena seleccionada **no** usa el `EventPlaneRepository.get_latest_event` para decidir si reintenta un chunk G3. La autoridad para aplicar resultados vive en un plan/lease/receipt de `queue.db`, y el estado local se mueve entre planos con verificación e idempotencia por etapa. Un intento de proveedor incierto permanece representado por `G3_EXTERNAL_UNKNOWN`, lo que cumple la prohibición de retry ciego, **pero no acredita escalamiento configurable** (GAP-0.5-01). La comprobación de lease antes del semáforo no valida inicio de efecto (GAP-02). El sweeper declarado en Compose no coteja receipts al mutar FSM y informa un estado diferente del real (GAP-03). La recuperación de resultados locales se limita al modelo de fallos aprobado; no implica exactly-once remoto.

## 17. NO-REGRESIÓN Y RECONCILIACIÓN F18 / PPPR (§9.2–9.4)

| Fuente y frontera | Observed en el HEAD auditado | Required/Decision y conclusión |
|---|---|---|
| PPPR.0.1 FROZEN | CLI→OCR→G3→G5 soportados; Compose también declara daemons | No reabrir D-1/D-2 ni confundir CLI foreground con despliegue Compose (E-032) |
| PPPR.0.2 FROZEN | Plan/tasks/context snapshot guardados en queue y FSM en otro archivo | Extracción no re-auditada; frontera SQLite del ingreso E-001/002 aquí |
| PPPR.0.3 FROZEN | Verificación del hash recibido y plan antes de inferir | GAP-0.3-01/02 siguen OPEN; validar un hash no repara campos omitidos de su pre-image |
| PPPR.0.4 FROZEN | Modelo/presupuesto/prompt Groq y error post-effect llegan al worker G3 | GAP-0.4-01…04 siguen OPEN; W06/receipt tratados aquí, no viabilidad comercial |
| ADR-F18.2, NADR-F18-03 | Lease como intención durable, UNKNOWN sin retry, epoch y CAS del reconciler | Respetar no-retry; GAP-01 (R11) y GAP-02 (R2) son discrepancias nuevas de composición, no reinicio del EventPlane legado |
| NADR-F18-04 | Receipt local queue, proyección materialized, finalización queue y FSM CAS; no 2PC | Recuperación desde fuentes locales, sin nuevo journal; GAP-03 concierne al sweeper de Compose, no a publicación del foreground |
| NADR-F18-05, principios SRE | Quotas y observabilidad local no prueban gastos/duplicación real; log sweeper contradice FSM | DQ-04 limita FinOps; no inferir dato externo, error silencioso ni estado efectivo desde el mensaje de log |

**Contradicciones reconciliadas:** (a) la descripción histórica F18 del journal CQRS no describe el G3 actual basado en receipts; (b) la descripción del sweeper no coincide con los estados consultados; (c) el mensaje FAILED_FATAL no coincide con FAILED_RETRYABLE. E-023 sigue P2 y E-032 conecta el servicio configurado, sin reasignar IDs o afirmar que Docker esté activo. Los hallazgos anteriores del producto siguen abiertos en sus HITOs.

## 21. CIERRE DEL HITO PPPR.0.5 — FROZEN v1.0.3

### 21.1 Checklist obligatorio (§8.1–8.2)

| Control | Resultado y evidencia |
|---|---|
| Metadata, tipo, estado, fecha y changelog | **CUMPLE** — encabezado y versiones 1.0.0–1.0.3 |
| Método read-only, límite epistemológico | **CUMPLE** — §2: Observed/Required/Decision, NOT_RUN y no certificación |
| 100% del perímetro declarado auditado o explicitado como NO VERIFICABLE | **CUMPLE** — §3: ingestión/FSM/queue/G3/reconciler/sweeper/publicación/cuotas; G5/host/LLM/GT diferidos |
| Fuentes obligatorias y estado histórico | **CUMPLE** — §4/17: SHA main, F18 y PPPR.0.1–0.4 FROZEN |
| Flujo completo, bifurcaciones y persistencia | **CUMPLE** — §5/11: G3 vigente vs CQRS legacy; ocho ventanas W1–W8 |
| E-IDs estables y severidad | **CUMPLE** — §10: 34 E-IDs, 3 P1, 31 P2; sin reasignación |
| Fichas extendidas P1 (Observed/Required/Decision) | **CUMPLE** — E-0.5-019/020/032 con causalidad, consecuencia, estado y destino |
| GAPs trazables, contrato, destino, estado | **CUMPLE** — §14, GAP-0.5-01…03 P1 LOCAL OPEN |
| Hipótesis clasificadas, ninguna abierta | **CUMPLE** — §15, H-0.5-A…I |
| Deferred Questions según §8.2 | **CUMPLE** — DQ-0.5-01…04 con motivo, no-bloqueo y destino |
| Decision Candidates separados de decisiones vigentes | **CUMPLE** — DC-0.5-01…03, sin tecnología prescrita |
| No-regresión con HITOs y reconciliación F18 | **CUMPLE** — §17, histórico vs G3 actual y sweeper Compose |
| Garantías explícitas, cadena de gobierno y siguiente paso | **CUMPLE** — §§21.2–21.4 |
| Tests, Docker, CI, proveedor comercial, corpus y GT | **NOT_RUN / NO REQUERIDO** para cierre estático; no se acredita PASS |

**Regla §8.2:** los datos empíricos no obtenidos no bloquean este mandato de lectura estática porque tienen razón específica y destino. Sí impiden certificar el producto, probar gestión externa de efectos o cerrar los tres GAPs.

### 21.2 Declaración de cierre y garantías positivas/negativas

**Estado: FROZEN v1.0.3 — 2026-11-19.** Se cierra únicamente el Flow Audit documental de SQLite, FSM, W06, autoridad, publicación y recuperación de la ruta versionada main@1d21cfe958cc1de8a33824fed748cd6fe9260f42.

**Positivo por código:** lease/attempt durables y CAS local, receipt + RESULT_STAGED atómicos en queue.db, UNKNOWN conservador que bloquea retry automático, proyección materialized verificable e idempotente, finalización de cola y CAS FSM recuperables por etapas. El reconciler distingue tareas G3 del CQRS legacy y verifica epoch/owner. Las garantías dependen de contratos locales y del modelo de fallos F18; tests versionados se leyeron, no ejecutaron.

**GAPs aún P1 LOCAL / OPEN:** GAP-0.5-01 (UNKNOWN sin escalamiento conectado), GAP-0.5-02 (lease no revalidado al inicio del I/O), GAP-0.5-03 (sweeper Compose con consultas/transiciones/reporting incompatibles). FROZEN no subsana ni acepta estas discrepancias.

**NO GARANTIZADO:** proveedor real, cuenta o cargo, ausencia de efectos externos duplicados, vigencia universal del lease al despachar, recuperación física SIGKILL/power loss, exactly-once, cobertura real de host/Compose, G5 final, fidelidad STEM, oráculos/GT ni PRODUCT_READINESS=PASS. No se ejecutaron tests, SQLite real, CI, Docker, API LLM, corpus ni remediación.

### 21.3 Cadena de gobernanza y no-regresión

Metodología general v1.3.0 FROZEN → metodología forense v1.2.0 FROZEN → PROJECT_SCOPE / ENGINEERING_PRINCIPLES → D-1/D-2, Atlas → PPPR.0.1–0.4 FROZEN y ADR-F18.2/NADR-F18-01…05 FROZEN → PPPR.0.5 FROZEN → PPPR.0.6–0.9 → ADR Maestro PPPR, ADR/NADR estrictamente necesarios → Execution Plan aprobado e integrado a main → implementación futura por PRs distintos.

No se autoriza restablecer retries ciegos, crear journal paralelo, imponer 2PC o cambiar a synchronous=FULL por reflejo. Las soluciones se evaluarán exclusivamente después de la gobernanza correspondiente.

### 21.4 Próximo gate e integración Git

Documento preparado para revisión y aprobación explícita del PR interno #70, aún Draft, hacia pdf-pdf-product-readiness. FROZEN documental no implica aprobación del propietario ni merge.

Después de aprobar e integrar #70: verificar el HITO en la rama general; eliminar pppr/hito-0.5; abrir pppr/hito-0.6 desde el HEAD actualizado. El PR general #66 debe seguir Draft, con main intacto, hasta concluir Fase 0, ADR Maestro, ADR/NADR y Execution Plan aprobados. No se implementa producción antes.

> FROZEN documental ≠ GAPs resueltos ≠ prueba de durabilidad física ≠ certificación científica ≠ autorización de implementación.
