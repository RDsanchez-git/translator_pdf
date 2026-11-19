# HITO_PPPR.0.5_SQLITE_FSM_W06_AUTORIDAD_Y_RECUPERACION.md

**Estado:** IN_PROGRESS v1.0.0  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** N/A  
**Fase:** PPPR — Fase 0 transversal de `pdf-pdf-product-readiness`, no una fase nueva del roadmap.  
**Tipo de artefacto:** Forensic Flow Audit (autoridad, persistencia, estados, W06 y recovery).  
**Naturaleza:** Read-only; no modifica producción, datos reales, corpus, tests ni decisiones de diseño.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@1e4c767eb60d46f37e733c3af85a28dfe76f7f38`, con PPPR.0.1–0.4 FROZEN.  
**Evidencia Forense Vinculante:** Metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y Atlas; NADR-F18-01 (identidades), NADR-F18-02 (ejecución acotada), NADR-F18-03 (autoridad/efectos inciertos), NADR-F18-04 (durabilidad/idempotencia), NADR-F18-05 (exposición y observabilidad), ADR-F18.2 FROZEN; los HITOs PPPR.0.1–0.4 congelados.  
**Mandato:** auditar **la ruta soportada** OCR→G3→G5 en cuanto a propietarios de estado, `FSMRepository`, SQLite `fsm.db/queue.db/event.db/materialized.db/rate_limits.db`, identidad del intento, leases y epochs, pre-efecto/pos-efecto W06, receipt/manifest, recuperación, proyecciones y transición FSM; distinguir implementación actual, evidencia de testigos y obligaciones F18, sin volver a ejecutar el antiguo pipeline.  
**Síntesis:** La ruta G3 actual utiliza `queue.db` como fuente local recuperable de plan/intent/receipt y materializa por etapas; `event.db` permanece en la ruta CQRS legada. Ante incertidumbre, los chunks de inferencia entran en cuarentena `G3_EXTERNAL_UNKNOWN` en vez de reintentarse automáticamente. Hay contratos positivos de fencing/idempotencia; falta examinar cobertura total, mecanismos de resolución de UNKNOWN y ventanas de fallo antes de congelar o abrir GAPs.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura desde merge del PR #69 con inspección directa de root G3, SQL/repositories, reconciler, staged publication, F18 NADR-03/04 y testigos W06/B3/B4. 18 E-IDs iniciales, 8 hipótesis por cerrar; NO tests ejecutados, NO FROZEN ni GAP prematuro. |

## 1. RESUMEN EJECUTIVO

Se inició la auditoría forense de propiedad de estado de la ruta seleccionada. El OCR almacena un AST y un `ChunkPlan` con context snapshots; G3 recupera la generación validada, reclama tareas en `queue.db` con leases, llama al proveedor únicamente para `TRANSLATE/PARTIAL`, guarda un resultado estructurado en receipt durable y publica los nodos por una secuencia local `queue.db → materialized.db → queue.db → fsm.db`.

**Hallazgo central:**

> En el G3 vigente, los receipts verificados y los estados de cuarentena sustituyen la antigua inferencia «sin evento, entonces no hubo efecto»; la coherencia de publicación se recupera mediante pasos locales, **no** una transacción distribuida ni una garantía de no duplicación comercial.

**Defectos dominantes:** ninguno clasificado definitivamente en esta apertura. La suficiencia del escalamiento de `G3_EXTERNAL_UNKNOWN`, la autoridad cerca del instante de I/O y la recuperación bajo fallos abruptos son **hipótesis a falsar**, no defectos ya probados.

**Veredicto inicial:** flujo principal parcialmente verificado; reconciliación F18↔código en curso. **IN_PROGRESS**; no `PRODUCT_READINESS=PASS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **Observed:** lectura directa de `main@1d21cfe`, separando código activo, contratos de pruebas offline y antecedentes F18. No se ha accedido a ninguna base del usuario.
- **Required:** F18-NADR-03 §5.1–5.6 (autoridad, incertidumbre y recuperación), F18-NADR-04 §5.1–5.5 (durabilidad/confirmación/idempotencia), F18-NADR-01 (identidades) y reglas de gobierno FROZEN. Se contrastarán consumidores antes de declarar incumplimientos.
- **Decision:** D-1/D-2 fijaron CLI→OCR Router→`runtime/engine.py`→G5. Esta elección no ordena volver a la ruta CQRS anterior ni crear una segunda FSM.
- **Garantía limitada:** `PRAGMA journal_mode=WAL; synchronous=NORMAL` se ha observado, pero NO demuestra inmunidad a power loss/fallo físico. CAS SQL ≠ cancelación de una llamada comercial ya iniciada. No se declara atomicidad entre archivos SQLite separados.
- **NOT_RUN:** tests, Docker, crash injection, SDK del LLM, compilador, SQLite de producción y corpus/GT. Los tests se examinan como evidencia de **intención/cobertura**, no se les atribuye PASS actual.
- **Perímetros ajenos:** G3 modelo/prompt/tokens (PPPR.0.4), G5 y salida física (PPPR.0.6), hosting/secretos/volúmenes (PPPR.0.7), prueba científica (PPPR.0.8).

## 3. ALCANCE AUDITADO — PRIMERA PASADA

| Frontera | Código primario y propiedad | Estado de esta pasada |
|---|---|---|
| Admission/OCR→G3 | `apps/ocr_router/__main__.py::_process_document`, `infra/db/context_snapshot_repo.py::enqueue_verified` | **AUDITADO focal**: atomicidad local de plan + tasks + snapshots; otro HITO cubre extracción |
| G3 root y workers | `runtime/engine.py::run_pipeline`; `runtime/chunk_staging.py::stage_claimed_unit` | **AUDITADO**: validación pre-provider, threading, estados, receipt |
| Autoridad de tarea | `infra/db/control_repo.py::{pick_task,stage_chunk_result,mark_g3_external_unknown,recover_expired_g3_task}` | **AUDITADO focal**: lease, CAS, UNKNOWN y fencing |
| FSM documento | `infra/db/fsm_repository.py`, `core/execution/handlers.py` | **AUDITADO focal**: CAS versionado, límites de transacción |
| Recuperación/reconciliador | `apps/daemons/reconciler.py`, `infra/db/system_repo.py`, `runtime/{recovery,resumer,sweeper}.py` | **AUDITADO focal**; semántica/activación de todos los mecanismos pendiente |
| Publicación | `infra/db/staged_publication.py`, `runtime/publication_pipeline.py` | **AUDITADO**: staged→materialized→queue→FSM, replay local |
| SQLite/WAL y cuota | `infra/db/{connection,schema_queue,schema_fsm,schema_event,context_snapshot_repo}.py/sql`, `infra/resilience/thread_owned_sqlite_rate_limit_store.py` | **AUDITADO focal**; escritura real y power-loss NO VERIFICABLE |
| Event plane histórico | `infra/db/{event_repo,materialized_repo}.py`, rutas legadas del reconciler | **AUDITADO para desambiguar consumidor**, no sustituye G3 vigente |
| Tests versionados | W06, B3 receipts/publication, B4 recovery/fencing, SQLite ownership/factory | **LEÍDOS · NOT_RUN**; algunos fakes/SQLite temporal |
| Normativa previa | NADR-F18-01…05, ADR-F18.2 y corte histórico de F18.2 | **CONTRASTE INICIADO**; no transferir un GAP histórico sin comprobar HEAD |
| G5/output y costeo de I/O | Otros HITOs PPPR | **REFERENCIADO**; sin certificación física ni económica |

No se considera completo aún el checklist §8.1. No se introducen expedientes suplementarios ni matrices auxiliares fuera de este HITO.

## 4. FUENTES DE EVIDENCIA

**Código primario:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`: `runtime/{engine,chunk_staging,publication_pipeline,recovery,resumer,sweeper}.py`, `apps/daemons/reconciler.py`, `infra/db/{control_repo,fsm_repository,staged_publication,context_snapshot_repo,connection,event_repo,materialized_repo}.py`.

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

## 10. REGISTRO INICIAL DE EVIDENCIA FORENSE

| E-ID | Sev. provisional | Observed (archivo::símbolo) | Required/Decision/límite | Estado |
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

**Severidad inicial P2 = hecho/limitación observable.** Antes de emitir P1/P0 se comprobarán los consumidores que podrían refutarlo; no se declara `PASS` científico ni se reabre una deuda histórica como defecto actual por mera similitud.

## 14. GAPS CONSOLIDADOS — APERTURA

**Ningún GAP formalizado aún.** Candidatos bajo investigación: escalamiento configurable de UNKNOWN conforme NADR-F18-03 R11; autoridad vigente inmediatamente antes de iniciar I/O y tratamiento de expiration/TTL en llamada en vuelo; coherencia de estados entre `queue.db` y `fsm.db` cuando se producen interrupciones. Requieren demostrar el incumplimiento normativo/consumidor y documentar consecuencia antes de asignar severidad.

## 15. HIPÓTESIS FALSABLES — IN_PROGRESS

| ID | Pregunta | Estado/destino de la investigación |
|---|---|---|
| **H-0.5-A** | ¿El escalamiento de `G3_EXTERNAL_UNKNOWN` dispone de umbrales/alarma operativa configurables y disposición segura según NADR-F18-03 R10–R15? | **TO BE VERIFIED**, rastrear CLI, reconciler, telemetry y operator workflow |
| **H-0.5-B** | ¿Toda operación G3 valida autoridad **vigente** inmediatamente antes del efecto, incluso con pérdida de lease entre guard y SDK? | **TO BE VERIFIED**, comparar NADR-F18-03 R1–R3 con `stage_claimed_unit` y provider bridge |
| **H-0.5-C** | ¿Crash tras paid effect y antes de receipt se convierte en UNKNOWN sin reintento automático? | **CONFIRMADA por lectura** en recuperación de expiración; testigo W06 `NOT_RUN` |
| **H-0.5-D** | ¿Crash después de RESULT_STAGED o tras materialized publication reinicia sin volver a llamar al modelo? | **CONFIRMADA como mecanismo** en código y tests; ejecución post-crash `NOT_RUN` |
| **H-0.5-E** | ¿Existe transacción distribuida queue/materialized/FSM, o solo convergencia por commits locales? | **CONFIRMADA la separación**; evaluar modelo de fallos F18 para no inventar necesidad de 2PC |
| **H-0.5-F** | ¿Las escrituras obsoletas están cercadas por identidad de ejecución, epoch y CAS en todas las rutas G3? | **PARCIAL**, revisar paths de finalización y handlers legacy |
| **H-0.5-G** | ¿El estado `WAL+NORMAL` es suficiente bajo el modelo de fallos realmente aprobado? | **CONFIRMADA como política estática**, garantías power-loss fuera de modelo; no medir aquí |
| **H-0.5-H** | ¿El estado durable de cuotas, circuit breaker y telemetría satisface reglas F18 sin contaminar identidad científica? | **TO BE VERIFIED**; controlar owner del estado y destino 0.7/ADR cuando aplique |

## 16. RESPUESTAS INICIALES AL MANDATO

La cadena seleccionada **no** usa el `EventPlaneRepository.get_latest_event` para decidir si reintenta un chunk G3. La autoridad para aplicar resultados vive en un plan/lease/receipt de `queue.db`, y el estado local se mueve entre planos con verificación e idempotencia por etapa. Un intento de proveedor incierto permanece representado por `G3_EXTERNAL_UNKNOWN`; eso es una protección importante, **no** prueba de que exista resolución, escalamiento, costo contabilizado o recuperación científica final.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN.** Apertura con 18 evidencias iniciales, ocho hipótesis y ninguna severidad P1 adjudicada por inercia histórica. Pendiente: inventario exhaustivo de consumidores de UNKNOWN y ejecutores/reconciliadores, contradicciones con F18, ventanas antes/después de I/O, guarantees bajo crash, resultados de tests `NOT_RUN` y checklist §8.1–8.2. No hubo tests, CI, proveedor comercial, corpus, cambios de código, SQLite ni otras mutaciones productivas.

**Git:** abrir PR interno Draft solo de este Markdown desde `pppr/hito-0.5` hacia `pdf-pdf-product-readiness`; mantener el PR general #66 Draft hacia `main`. Cuando PPPR.0.5 se congele, revise y apruebe, integrar internamente, verificar, eliminar rama corta y solo entonces comenzar PPPR.0.6. No implementar antes de ADR/NADR y Execution Plan aprobados.
