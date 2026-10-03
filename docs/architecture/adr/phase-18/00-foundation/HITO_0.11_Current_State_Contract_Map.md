# HITO_0.11_Current_State_Contract_Map.md

**Estado:** FROZEN v1.0.1
**Fecha de emisión:** 2026-10-03
**Fecha de congelamiento:** 2026-10-03 (v1.0.1)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Consolidation Output
**Naturaleza:** Read-only. Consolida el estado actual de componentes, autoridades y contratos vigentes del execution plane, con clasificación reuse/extend/replace y mapeo de fronteras. Este documento no prescribe implementación ni arquitectura; su función es proporcionar un mapa unificado del estado actual para alimentar el ADR_F18_MASTER.
**Evidencia Forense Vinculante:** HITO_0.1 v1.2.0 (F0-B), HITO_0.2 v1.2.0 (F0-G), HITO_0.3 v1.3.0 (F0-F), HITO_0.4 v1.3.0 (F0-E), HITO_0.5 v1.2.0 (F0-A Protocol), HITO_0.6 v1.0.0 (Reconciliation), HITO_0.7 v1.1.0 (F0-A Baseline), HITO_0.8 v1.4.0 (F0-C), HITO_0.9 v1.4.0 (F0-D), HITO_0.10 v1.0.1 (Gap Matrix)
**Mandato (Charter §8):** Generar el output obligatorio "Current State & Contract Map" para ADR_F18_MASTER §7.
**Síntesis:** Se consolida el estado actual de 13 autoridades del execution plane (11 RETAIN, 2 REFACTOR), 1 capacidad faltante (Coordinated Shutdown), 1 superficie de refactor (benchmark/runners, violación de frontera), y 8 componentes de concurrencia. Se documentan 5 contratos de comparación científica (guard diferencial), 4 mecanismos de durabilidad observados, y 3 contratos de medición. Fronteras hexagonales respetadas en 12/13 superficies arquitectónicas auditadas; 1 violación documentada (imports cruzados core→apps). 25 GAPs abiertos con destino F18 (3 P0, 15 P1, 7 P2), consolidados en HITO_0.10 v1.0.1.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-03 | Emisión inicial. Consolidación de estado actual y contratos de HITOs 0.1-0.9. |
| 1.0.1-FROZEN | 2026-10-03 | **Reconciliación epistemológica y cuantitativa.** (1) Corregidos conteos de autoridades: 13 autoridades (11 RETAIN + 2 REFACTOR) + 1 capacidad missing + 1 refactor surface. (2) Alineado universo de GAPs con HITO_0.10 v1.0.1: 25 GAPs abiertos (3 P0 + 15 P1 + 7 P2). (3) Añadida tabla de versiones fuente consumidas. (4) Corregidas afirmaciones epistemológicas: "arquitectura hexagonal madura" → "estructura hexagonal observable en superficies auditadas"; "contratos implementados" → "mecanismos y contratos observados". (5) Corregido subset canónico de evidencia: "evidencia científica" → "evidencia de verificación/lineage". (6) Prerrequisitos del guard diferencial reformulados: "PREREQUISITE VERIFIED" → "Prerequisite implementation observed; completion-order invariance NO DEMOSTRADO". (7) GAP-0.5-02 degradado de P0 a P1 (alineado con HITO_0.10 v1.0.1). (8) DCs reformulados como decisiones, no implementación. (9) Añadida nota sobre RETAIN/REFACTOR/MISSING: clasificación de estado actual, no decisión de diseño. (10) Corregido denominador de fronteras hexagonales: "12/13 autoridades" → "12/13 superficies arquitectónicas auditadas". (11) Corregido cierre: "Contradicciones: Ninguna" → "No se identifican contradicciones materiales; existen refinamientos de clasificación y alcance documentados en la consolidación". |

---

## 1. RESUMEN EJECUTIVO

Se consolidó el estado actual de componentes, autoridades y contratos del execution plane a partir de la evidencia forense de los 9 HITOs de Fase 0. Este documento sirve como entrada directa para el ADR_F18_MASTER, proporcionando el mapa completo de lo que existe, lo que funciona, lo que requiere refactor y lo que falta.

**Hallazgo central:**

> El execution plane presenta una estructura hexagonal observable en las superficies auditadas, con una violación de frontera confirmada (imports cruzados core→apps) y varias capacidades aún pendientes de demostración o refactor. 13 autoridades están bien delimitadas (11 RETAIN, 2 REFACTOR), 1 capacidad reclamada por el Charter está ausente (Coordinated Shutdown), y 1 superficie requiere refactor (benchmark/runners). Los mecanismos de durabilidad (SQLite WAL, BEGIN IMMEDIATE, epoch fencing) están observados pero no todos validados empíricamente. Los contratos de comparación científica (guard diferencial) están definidos como prerrequisitos pero requieren implementación del mecanismo M0→M1→M2→M3.

**Distribución por clasificación:**

| Categoría | Cantidad | Detalle |
|---|---|---|
| **Autoridades RETAIN** | 11 | ControlPlane, EventPlane, MaterializedPlane, SystemPlane, FSM, Reconciler, RecoveryDaemon, RateLimiter, Cache, DocumentRepository, CommandHandlers |
| **Autoridades REFACTOR** | 2 | CircuitBreaker (in-memory), ProfileStore (in-memory) |
| **Capacidad MISSING** | 1 | Coordinated Shutdown |
| **Refactor surface** | 1 | benchmark/runners (imports cruzados core→apps) |
| **Componentes de concurrencia** | 8 | SyncProviderBridge, AsyncDispatcher, TaskLeaseHeartbeat, LLMWorkerDaemon, ReconcilerDaemon, RecoveryDaemon, TranslationPipeline, RoutingWorkflow |

**Nota sobre clasificación:** La clasificación RETAIN/REFACTOR/MISSING identifica el estado actual observado, no constituye decisión de diseño ni obliga a una estrategia de implementación. La decisión normativa corresponde al ADR/DC correspondiente.

**Contratos vigentes:**
- **5 contratos de comparación científica** (guard diferencial): hash AST por nodo, hash artefacto ensamblado, métricas científicas por documento, subset canónico de evidencia de verificación/lineage, tolerancia = exactitud con params congelados
- **4 mecanismos de durabilidad observados**: WAL + BEGIN IMMEDIATE + optimistic locking, epoch fencing, recovery automático (sweeper/resumer), recovery manual (OnDemandResumeManager)
- **3 contratos de medición**: baseline operacional (wall/CPU/RSS), baseline de waste ratio (parcial), baseline de durabilidad (matriz state→authority→storage→durability→recovery→loss window)

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO

### 2.1 Límite epistemológico
Este documento es una **consolidación** de evidencia ya producida en HITOs 0.1-0.9. No introduce nueva evidencia forense. No propone implementación. No decide diseño. Su función es proporcionar un mapa unificado del estado actual para alimentar el ADR_F18_MASTER.

### 2.2 Método de consolidación
1. Extraer inventario de autoridades de HITO_0.2 (F0-G)
2. Extraer componentes de concurrencia de HITO_0.1 (F0-B)
3. Extraer contratos de comparación de HITO_0.4 (F0-E)
4. Extraer mecanismos de durabilidad de HITO_0.8 (F0-C)
5. Extraer contratos de medición de HITO_0.7 (F0-A Baseline) y HITO_0.9 (F0-D)
6. Consolidar en matriz unificada con clasificación reuse/extend/replace
7. Mapear fronteras entre componentes
8. Trazar a Decision Candidates del Charter §7
9. Reconciliar versiones fuente consumidas (ver §4)

---

## 3. ALCANCE CONSOLIDADO

| Superficie | HITO origen | Estado |
|---|---|---|
| Autoridades del execution plane | HITO_0.2 (F0-G) | 13 autoridades inventariadas (11 RETAIN, 2 REFACTOR) |
| Capacidad faltante | HITO_0.8 (F0-C) | 1 MISSING (Coordinated Shutdown) |
| Refactor surface | HITO_0.2 (F0-G) | 1 (benchmark/runners, imports cruzados) |
| Componentes de concurrencia | HITO_0.1 (F0-B) | 8 componentes mapeados |
| Contratos de comparación científica | HITO_0.4 (F0-E) | 5 contratos definidos |
| Mecanismos de durabilidad | HITO_0.8 (F0-C) | 4 mecanismos observados |
| Contratos de medición | HITO_0.7, HITO_0.9 | 3 contratos establecidos |
| Fronteras hexagonales | HITO_0.2 (F0-G) | 12/13 superficies auditadas respetadas, 1 violación |

---

## 4. FUENTES DE EVIDENCIA Y VERSIONES CONSUMIDAS

### 4.1 Tabla de versiones fuente

| HITO fuente | Versión consumida | ¿Reconciliada? | Evidencia de reconciliación |
|---|---|---|---|
| HITO_0.1 (F0-B) | v1.2.0 | Sí | Changelog v1.2.0: correcciones epistemológicas |
| HITO_0.2 (F0-G) | v1.2.0 | Sí | Changelog v1.2.0: DF-24 reabierto, H-0.2-A rebajada |
| HITO_0.3 (F0-F) | v1.3.0 | Sí | Changelog v1.3.0: H-0.3-A/H-0.3-B rebajadas |
| HITO_0.4 (F0-E) | v1.3.0 | Sí | Changelog v1.3.0: prerrequisitos verificados, end-to-end pending M1 |
| HITO_0.5 (F0-A Protocol) | v1.2.0 | Sí | Changelog v1.2.0: reconciliación post-ejecución |
| HITO_0.6 (Reconciliation) | v1.0.0 | No | Versión única |
| HITO_0.7 (F0-A Baseline) | v1.1.0 | Sí | Changelog v1.1.0: tree-monitoring, per-PID peaks |
| HITO_0.8 (F0-C) | v1.4.0 | Sí | Changelog v1.4.0: reconciliación epistemológica, taxonomía de pérdida |
| HITO_0.9 (F0-D) | v1.4.0 | Sí | Changelog v1.4.0: alineación con Charter §6, Evidence Register |
| HITO_0.10 (Gap Matrix) | v1.0.1 | Sí | Changelog v1.0.1: GAP_CLASS, normalización, 25 GAPs |

### 4.2 Tipos de evidencia

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Charter | `FASE0_AUDIT_CHARTER.md` §5.3, §6, §9 | Mandato y restricciones |
| ADR Maestro | `ADR_F17_BIS_MASTER.md` §5 | Determinismo y Reproducibilidad |
| NADR | `NADR-F17BIS-09` | FSM/Event Log Integrity |
| NADR | `NADR-F17BIS-07` | Healing Atomic Rollback |
| NADR | `NADR-F17BIS-08` | Distributed Execution Plane CQRS |
| Principios | `ENGINEERING_PRINCIPLES.md` §IV | Cero Fallos Silenciosos |
| HITO previo | `HITO_0.1` v1.2.0 | Componentes de concurrencia |
| HITO previo | `HITO_0.2` v1.2.0 | Inventario de autoridades |
| HITO previo | `HITO_0.3` v1.3.0 | Workload corpus |
| HITO previo | `HITO_0.4` v1.3.0 | Contratos de comparación |
| HITO previo | `HITO_0.5` v1.2.0 | Protocolo de medición |
| HITO previo | `HITO_0.6` v1.0.0 | Reconciliación de perímetro |
| HITO previo | `HITO_0.7` v1.1.0 | Baseline operacional |
| HITO previo | `HITO_0.8` v1.4.0 | Matriz de durabilidad |
| HITO previo | `HITO_0.9` v1.4.0 | Baseline de waste |
| HITO previo | `HITO_0.10` v1.0.1 | Gap Matrix consolidada (25 GAPs) |

---

## 5. CURRENT STATE MAP — AUTORIDADES DEL EXECUTION PLANE

### 5.1 Inventario de autoridades (de HITO_0.2 F0-G)

| Autoridad | Representación | Estado que posee | Frontera | Clasificación |
|---|---|---|---|---|
| **Control Plane** | `core/execution/ports.py::ControlPlanePort` → `infra/db/control_repo.py::ControlPlaneRepository` | Leases, task state, execution_id, retry_count | Puerto Protocol en core; implementación SQLite en infra | **RETAIN** |
| **Event Plane** | `core/execution/ports.py::EventPlanePort` → `infra/db/event_repo.py::EventPlaneRepository` | WAL de eventos (chunk_events_log) | Puerto Protocol en core; implementación SQLite en infra | **RETAIN** |
| **Materialized Plane** | `core/execution/ports.py::MaterializedPlanePort` → `infra/db/materialized_repo.py::MaterializedPlaneRepository` | Proyecciones de chunks traducidos | Puerto Protocol en core; implementación SQLite en infra | **RETAIN** |
| **System Plane (Leadership)** | `infra/db/system_repo.py::SystemPlaneRepository` | Leadership leases, epoch | Sin puerto abstracto (acceso directo) | **RETAIN** |
| **FSM State** | `core/execution/state.py::DocumentState` + `core/pipeline/state_store.py::FSMStateStore` → `infra/db/fsm_repository.py::FSMRepository` | Estado del documento (CREATED→COMPLETED), transiciones, suspended_reason | Tabla de transiciones en core; persistencia en infra | **RETAIN** |
| **Reconciler** | `apps/daemons/reconciler.py::ReconcilerDaemon` | Convergencia CQRS, zombie recovery, FSM stall detection | Daemon en apps; consume SystemPlane + ControlPlane | **RETAIN** |
| **Recovery Sweeper** | `runtime/sweeper.py::RecoveryDaemon` | WAL checkpoint, purga de documentos STALLED (>3600s) | Daemon en runtime; consume FSMRepository | **RETAIN** |
| **Rate Limiter** | `apps/llm_workers/rate_limiter.py::QuotaManager` + `infra/resilience/sqlite_rate_limit_store.py::SQLiteRateLimitStore` | Token buckets (RPM/TPM), estado persistente | Lógica en apps; persistencia en infra | **RETAIN** |
| **Circuit Breaker** | `core/resilience/circuit_breaker.py::GlobalCircuitBreaker` + `CircuitBreakerRegistry` | Estado CB (CLOSED/OPEN/HALF_OPEN), métricas de fallos | In-memory en core; sin persistencia | **REFACTOR** |
| **Cache** | `apps/llm_workers/cache_provider.py::CachedLLMProvider` | Cache de respuestas LLM por prompt_hash | Autoridad de cache en apps; usa aiosqlite | **RETAIN** |
| **Profile Store** | `core/document_profile/ports.py::ProfileStore` → `infra/db/profile_store.py::InMemoryProfileStore` | Perfiles inferidos de documentos | Puerto Protocol en core; implementación in-memory en infra | **REFACTOR** |
| **Document Repository** | `infra/db/document_repository.py::SQLiteDocumentRepository` | Documentos persistidos | Implementación en infra | **RETAIN** |
| **Command Handlers** | `core/execution/handlers.py::DocumentCommandHandler` | Procesamiento de comandos FSM (Start, Fail, Cancel, Stall, RecoverZombie) | Core puro | **RETAIN** |

### 5.2 Capacidad MISSING (identificada en HITO_0.8 F0-C)

| Capacidad | Estado | Justificación |
|---|---|---|
| **Coordinated Shutdown** | **MISSING** | Charter §6 reclama "DaemonSupervisor/GracefulShutdown". Búsqueda recursiva en apps/, runtime/, core/ no encontró implementación. Shutdown distribuido sin coordinación centralizada observada. Implementación nominal no encontrada es evidencia secundaria; la capability podría existir mediante signal handlers, orchestration externa, context manager, lifecycle coordinator, process manager o supervisor externo. GAP-0.8-01 (P1). |

### 5.3 Refactor surface (violación de frontera, de HITO_0.2 F0-G)

| Superficie | Violación | Estado |
|---|---|---|
| **`core/benchmark/runners/*`** | Imports cruzados core→apps: `from apps.llm_workers.prompt_builder import PromptBuilder`, `from apps.bootstrap.provider_stack_factory import build_provider_stack`. Viola frontera hexagonal (ENGINEERING_PRINCIPLES §II). Confirma DF-06. GAP-0.2-03 (P1). | **REFACTOR** |

### 5.4 Resumen de clasificación

| Clasificación | Cantidad | Detalle |
|---|---|---|
| **Autoridades RETAIN** | 11 | ControlPlane, EventPlane, MaterializedPlane, SystemPlane, FSM, Reconciler, RecoveryDaemon, RateLimiter, Cache, DocumentRepository, CommandHandlers |
| **Autoridades REFACTOR** | 2 | CircuitBreaker (persistencia), ProfileStore (persistencia) |
| **Capacidad MISSING** | 1 | Coordinated Shutdown |
| **Refactor surface** | 1 | benchmark/runners (imports cruzados) |
| **Total autoridades** | 13 | 11 RETAIN + 2 REFACTOR |

---

## 6. CURRENT STATE MAP — COMPONENTES DE CONCURRENCIA

### 6.1 Inventario de componentes (de HITO_0.1 F0-B)

| Componente | Representación observada | Modelo | Participa en producción | Estado |
|---|---|---|---|---|
| `SyncProviderBridge` | `apps/llm_workers/sync_bridge.py::SyncProviderBridge` | Thread + asyncio loop dedicado | Sí (daemon + engine) | **CONFIRMADO** |
| `AsyncDispatcher` | `apps/llm_workers/dispatcher.py::AsyncDispatcher` | asyncio nativo (PriorityQueue, create_task) | Sí (CLI) / No (daemon) | **CONFIRMADO** |
| `TaskLeaseHeartbeat` | `apps/llm_workers/__main__.py::TaskLeaseHeartbeat` | threading.Thread + threading.Event | Sí (daemon) | **CONFIRMADO** |
| `LLMWorkerDaemon` | `apps/llm_workers/__main__.py::LLMWorkerDaemon` | Loop síncrono + threading.Event | Sí (daemon) | **CONFIRMADO** |
| `ReconcilerDaemon` | `apps/daemons/reconciler.py::ReconcilerDaemon` | Loop síncrono + threading.Thread (heartbeat) | Sí (daemon separado) | **CONFIRMADO** |
| `RecoveryDaemon` | `runtime/sweeper.py::RecoveryDaemon` | Loop síncrono + time.sleep | Sí (daemon separado) | **CONFIRMADO** |
| `TranslationPipeline` | `core/pipeline/orchestrator.py::TranslationPipeline` | async def execute() | Sí (CLI) | **CONFIRMADO** |
| `RoutingWorkflow` | `core/pipeline/workflow.py::RoutingWorkflow` | Síncrono (Iterator, yield) | Sí (pipeline interno) | **CONFIRMADO** |

### 6.2 Flujos observados

**FLUJO A — Traducción vía CLI (handle_translate):**
```
apps/cli/main.py::handle_translate()
  -> asyncio.run(handle_translate_async())           [OK] async nativo
  -> build_provider_stack()                          [OK] async
  -> build_pipeline()                                [OK] composition root
  -> pipeline.execute(job)                           [OK] async
  -> dispatcher.dispatch(units)                      [OK] AsyncDispatcher nativo
  -> asyncio.PriorityQueue + asyncio.create_task     [OK] concurrencia controlada
  -> provider.translate(envelope)                    [OK] async directo
```

**FLUJO B — Traducción vía Daemon de producción (LLMWorkerDaemon):**
```
apps/llm_workers/__main__.py::LLMWorkerDaemon.run()
  -> while not self._stop_event.is_set()             [OK] loop síncrono
  -> control_repo.pick_task()                        [OK] SQLite BEGIN IMMEDIATE
  -> SyncProviderBridge.execute(node)                [OBS] barrera síncrona: future.result(180s)
     -> asyncio.run_coroutine_threadsafe()           [OBS] cross-thread async
     -> provider.translate(envelope)                 [OK] async dentro del loop dedicado
     -> future.result(timeout=180.0)                 [OBS] bloquea hilo llamante
  -> TaskLeaseHeartbeat._beat()                      [OK] thread separado
     -> control_repo.renew_task_lease()              [OK] SQLite
  -> event_repo.append_wal()                         [OK] SQLite INSERT+commit
```

**Leyenda:**
- `[OK]` flujo sano observado
- `[OBS]` característica arquitectónica observada (impacto pendiente de F18)

---

## 7. CONTRACT MAP — CONTRATOS DE COMPARACIÓN CIENTÍFICA

### 7.1 Contratos del guard diferencial (de HITO_0.4 F0-E)

| Contrato | Descripción | Prerrequisito | Estado |
|---|---|---|---|
| **Hash AST por nodo** | `compute_ast_hash(node)` calcula SHA-256 sobre nodos AST (content, type, strategy, omitiendo sequence_id) | Determinismo de hashing | ✅ **Prerequisite implementation observed** (E-0.4-001) |
| **Hash artefacto ensamblado** | SHA-256 del documento científico ensamblado | Determinismo de ensamblado bajo mismas entradas | ✅ **Prerequisite implementation observed** (E-0.4-002); completion-order invariance NO DEMOSTRADO |
| **Métricas científicas por documento** | NSS (Normalized Structural Similarity) y Critical FN del `DoubleProtectionMechanism` | Determinismo de métricas bajo mismo AST | ✅ **Prerequisite implementation observed** (E-0.4-003) |
| **Subset canónico de evidencia de verificación/lineage** | Exit codes, identidad de ejecución, cobertura de perfil | Separación scientific/operational | ✅ **Prerequisite implementation observed** (E-0.4-004) |
| **Tolerancia = exactitud con params congelados** | Scientific equality (strict, tolerancia cero) vs operational evidence (puede diferir) | DC-02 resuelto | ⏳ **PENDIENTE** (GAP-0.4-03) |

### 7.2 Separación scientific equality / operational/lineage evidence

**Scientific equality (strict, tolerancia cero):**
- Hash del AST por nodo (representación científica)
- Hash del artefacto ensamblado (scientific artifact)
- Métricas científicas por documento (NSS, Critical FN)

**Operational/lineage evidence (not required, puede diferir):**
- Timestamps
- execution_id
- queue timings
- worker ID
- retry timing
- CPU time
- cache hit/miss
- scheduling order
- Exit codes
- Cobertura de perfil

**Nota:** La distinción entre scientific artifact y operational envelope debe resolverse en DC-02 antes de definir el contrato final del guard diferencial (GAP-0.4-03).

---

## 8. CONTRACT MAP — MECANISMOS DE DURABILIDAD OBSERVADOS

### 8.1 Mecanismos de durabilidad observados (de HITO_0.8 F0-C)

| Mecanismo | Descripción | Implementación | Validación empírica |
|---|---|---|---|
| **WAL + BEGIN IMMEDIATE + optimistic locking** | Transacciones atómicas con protección contra writes zombie | SQLite WAL, BEGIN IMMEDIATE, OptimisticLockError en 3 puntos | ✅ **OBSERVED** (E-0.8-001, E-0.8-005) |
| **Epoch fencing** | Comandos stale son descartados tras pérdida de liderazgo | lease_version como epoch, verificación en handlers | ⚠️ **NO DEMOSTRADO** empíricamente (GAP-0.8-06) |
| **Recovery automático** | Zombies y stalls son detectados y recuperados automáticamente | Reconciler sweep (25-35s), Sweeper (3600s → FAILED_FATAL) | ✅ **CONFIRMED** en escenario testeado (E-0.8-017) |
| **Recovery manual** | Documentos STALLED pueden ser rescatados manualmente | OnDemandResumeManager (STALLED → suspended_state via CAS) | ✅ **OBSERVED** (E-0.8-015) |

### 8.2 Matriz de durabilidad por activo (de HITO_0.8 §7.1)

| Activo | Persistence Mechanism | Recovery Mechanism | Recovery Convergence |
|---|---|---|---|
| Task Lease (chunk) | OBSERVED: BEGIN IMMEDIATE, TTL 300s, heartbeat 30s, OptimisticLockError | OBSERVED: reconciler sweep 25-35s; mark_zombie_recovered | **NO DEMOSTRADO** (GAP-0.8-07) |
| Leadership Epoch | OBSERVED: BEGIN IMMEDIATE, TTL 120s, heartbeat 36s | OBSERVED: epoch fencing en handlers | **NO DEMOSTRADO** (GAP-0.8-06) |
| Event WAL | OBSERVED: INSERT + commit inmediato | OBSERVED: economic replay por clave de dedup | **CONFIRMED estructural / PARTIAL bajo crash** (GAP-0.8-04) |
| Materialized Projections | OBSERVED: upsert con version check | OBSERVED: rematerialización vía reconciler | **CONFIRMED estructural** |
| Document FSM | OBSERVED: CAS + state_version | OBSERVED: watchdog, sweeper, resumer | **CONFIRMED en escenario testeado** (E-0.8-017) |
| Rate-limit buckets | OBSERVED: persist post-consumo, restore con refill | OBSERVED: refill por elapsed | **NO DEMOSTRADO** |
| Circuit Breaker | **NONE** (in-memory) | OBSERVED: cold start en CLOSED | **NO DEMOSTRADO**; STATE_LOSS TOTAL |
| Profile Store | **NONE** (in-memory) | OBSERVED: reconstrucción por otra vía no demostrada | **NO DEMOSTRADO**; STATE_LOSS TOTAL |
| Telemetry Gateway | OBSERVED: flush por lotes | OBSERVED: flush limpio solo en stop() ordenado | **NO DEMOSTRADO**; TELEMETRY_LOSS residual |

---

## 9. CONTRACT MAP — CONTRATOS DE MEDICIÓN

### 9.1 Baseline operacional (de HITO_0.7 F0-A)

| Métrica | Valor | Unidad | CV |
|---|---|---|---|
| Wall time (avg) | 1.659 | segundos | 0.41% |
| Peak single-process WS (avg) | 76.98 | MB | 0.07% |
| CPU time (avg) | 1.448 | segundos | 0.48% |
| Corpus NSS | 0.6385503611043202 | (adimensional) | — |
| Corpus verdict | HARD_FAIL | (estado basal esperado, DF-10) | — |

**Hardware envelope:** 31.83 GB RAM / 12 CPUs (NO conforme con target 16 GB / 4 GB VRAM)

### 9.2 Baseline de waste ratio (de HITO_0.9 F0-D)

| Canal Charter | Estado | Resultado |
|---|---|---|
| Duplicate execution | **DEFERRED** (W1) | No ejercitable: adapters/SDKs no exponen base_url override sin código productivo |
| Retry waste | **MEDIDO PARCIAL** (W3) | Quota contention bajo límites artificiales: 3/20 granted |
| Post-cancel work | **DEFERRED** (W5) | No ejercitable: misma limitación que W1 |
| Repeated provider calls | **DEFERRED** (W2) | No ejercitable: misma limitación que W1 |
| Failed persistence | **MEDIDO** (W7) | 1/1 zombie write interceptado (scope: lease-expired ack) |
| Baseline de waste ratio | **PARCIAL** | Solo canales ejercitables; 3/5 deferred |

### 9.3 Baseline de durabilidad (de HITO_0.8 F0-C)

Ver §8.2 (Matriz de durabilidad por activo).

---

## 10. MATRIZ DE FRONTERAS HEXAGONALES

### 10.1 Fronteras respetadas (12/13 superficies arquitectónicas auditadas)

| Superficie | Capa | Frontera | Estado |
|---|---|---|---|
| ControlPlanePort | Core (Protocol) → Infra (Implementation) | ✅ Respetada | Puerto abstracto en core, implementación SQLite en infra |
| EventPlanePort | Core (Protocol) → Infra (Implementation) | ✅ Respetada | Puerto abstracto en core, implementación SQLite en infra |
| MaterializedPlanePort | Core (Protocol) → Infra (Implementation) | ✅ Respetada | Puerto abstracto en core, implementación SQLite en infra |
| ProfileStore | Core (Protocol) → Infra (Implementation) | ✅ Respetada | Puerto abstracto en core, implementación in-memory en infra |
| FSM State | Core (Domain) → Infra (Persistence) | ✅ Respetada | Tabla de transiciones en core, persistencia en infra |
| DocumentCommandHandler | Core (Domain) | ✅ Respetada | Core puro, sin dependencias de infra |
| QuotaManager | Apps (Application) → Infra (Persistence) | ✅ Respetada | Lógica en apps, persistencia en infra |
| CachedLLMProvider | Apps (Application) | ✅ Respetada | Autoridad de cache en apps |
| ReconcilerDaemon | Apps (Application) | ✅ Respetada | Daemon en apps, consume puertos de core/infra |
| RecoveryDaemon | Runtime (Infrastructure) | ✅ Respetada | Daemon en runtime, consume repos de infra |
| SystemPlaneRepository | Infra (Persistence) | ✅ Respetada | Implementación en infra (sin puerto abstracto, pero funcional) |
| DocumentRepository | Infra (Persistence) | ✅ Respetada | Implementación en infra |

### 10.2 Frontera violada (1/13 superficies arquitectónicas auditadas)

| Superficie | Capa | Violación | Estado |
|---|---|---|---|
| `core/benchmark/runners/*` | Core → Apps | ❌ **VIOLADA** | Imports cruzados: `from apps.llm_workers.prompt_builder import PromptBuilder`, `from apps.bootstrap.provider_stack_factory import build_provider_stack`. Confirma DF-06. GAP-0.2-03 (P1). |

---

## 11. TRAZABILIDAD A DECISION CANDIDATES

### 11.1 Mapeo de autoridades a DCs

| DC | Autoridades relacionadas | Estado en Fase 0 | Acción requerida en F18 |
|---|---|---|---|
| **DC-01** (Fork de concurrencia) | SyncProviderBridge, AsyncDispatcher, TaskLeaseHeartbeat, LLMWorkerDaemon | Evidencia de flujos A/B disponible; barrera síncrona observada | Resolver fork de concurrencia (async single-process + executors vs multi-process) |
| **DC-02** (Parámetros de runtime en identity científica) | ProfileStore, DocumentRepository | Precondición no resuelta (GAP-0.4-03) | Resolver parámetros de runtime en identity científica vs metadata operacional |
| **DC-03** (Determinismo observable por proveedor) | Cache, RateLimiter | Capacidad confirmada, medición deferred | Resolver protocolo de caracterización de determinismo observable del proveedor |
| **DC-04** (Alcance de caches) | Cache | Evidencia de cache preexistente (E-0.2-008) | Resolver alcance de caches (pure-function 🟢 / LLM 🟡 / semantic+embedding 🔴) |
| **DC-07** (Tiers 8k/32k/1M o batch = f(budgets)) | RateLimiter, QuotaManager | Evidencia de entrada disponible | Resolver si la planificación se basa en tiers discretos, budgets continuos o combinación; valores concretos sujetos a caracterización empírica |
| **DC-08** (Write-policy SQLite + journal) | ControlPlane, EventPlane, MaterializedPlane, CircuitBreaker | Evidencia de gaps de durabilidad | Resolver write-policy SQLite + mecanismo de journal de INV-JOURNAL + persistencia de CB |
| **DC-11** (Semántica de admisión-diferida sin nuevo estado FSM) | FSM State | Riesgo identificado (GAP-0.4-02) | Resolver semántica de admisión-diferida sin nuevo estado FSM |
| **DC-12** (Contrato y promoción del guard diferencial) | Todos los contratos de comparación | Prerrequisitos verificados, end-to-end pending M1 | Resolver contrato, criterios de promoción y límites de equivalencia del differential guard |
| **DC-13** (Coordinated shutdown / daemon lifecycle) | **MISSING** | Capacidad NO DEMOSTRADA | Resolver coordinated shutdown / daemon lifecycle orchestration |
| **DF-06** (Imports cruzados core→apps) | `core/benchmark/runners/*` | Violación de frontera confirmada | Refactor de composición para respetar frontera hexagonal |
| **DF-24** (Persistencia de Circuit Breaker) | CircuitBreaker | Reabierto bajo DC-01/DC-08 | Resolver persistencia de Circuit Breaker |
| **DF-34** (Persistencia de ProfileStore) | ProfileStore | Existencia del store in-memory confirmada; coste agregado de re-inferencia tras restart aún no cuantificado | Resolver persistencia de ProfileStore |

**Nota sobre DC-13:** DC-13 contiene dos superficies conceptualmente distintas: lifecycle/shutdown orchestration (GAP-0.8-01) y telemetry durability (GAP-0.9-02). La separación normativa queda pendiente de resolución en HITO_0.12/ADR.

---

## 12. GAP MATRIX RESUMEN (de HITO_0.10 v1.0.1)

Ver HITO_0.10 v1.0.1 para detalle completo. Resumen:

| Severidad | Cantidad | GAPs |
|---|---|---|
| **P0** | 3 | GAP-0.3-01, GAP-0.4-01, GAP-0.4-03 |
| **P1** | 15 | GAP-0.1-01, GAP-0.2-01, GAP-0.2-02, GAP-0.2-03, GAP-0.2-04, GAP-0.3-02, GAP-0.3-03, GAP-0.4-02, GAP-0.5-02, GAP-0.7-01, GAP-0.7-02, GAP-0.8-01, GAP-0.8-06, GAP-0.8-07, GAP-0.9-01, GAP-0.9-02, GAP-0.9-04, GAP-0.9-05 |
| **P2** | 7 | GAP-0.1-02, GAP-0.1-03, GAP-0.8-05, GAP-0.9-03, y otros |
| **Total** | 25 | Todos con fase de resolución propuesta F18/F18+/F19+ |

---

## 13. VERIFICACIÓN DE CUMPLIMIENTO

| Regla | Fuente | Cumplimiento |
|---|---|---|
| Consolidación sin nueva evidencia | Charter §8 | ✅ Solo consolida HITOs 0.1-0.9 |
| Mapeo completo de autoridades | Charter §6 (F0-G) | ✅ 13 autoridades + 1 MISSING + 1 refactor surface |
| Mapeo completo de componentes de concurrencia | Charter §6 (F0-B) | ✅ 8 componentes |
| Contratos de comparación definidos | Charter §6 (F0-E) | ✅ 5 contratos |
| Mecanismos de durabilidad observados | Charter §6 (F0-C) | ✅ 4 mecanismos |
| Fronteras hexagonales mapeadas | ENGINEERING_PRINCIPLES §II | ✅ 12/13 superficies auditadas respetadas, 1 violación |
| Trazabilidad a DCs | Charter §7 | ✅ 12 DCs mapeados |
| Versiones fuente reconciliadas | Metodología | ✅ Tabla §4.1 |

---

## 14. CIERRE DEL HITO 0.11

**Estado del HITO:** FROZEN v1.0.1
**Condición de cierre cumplida:** Estado actual de 13 autoridades consolidado (11 RETAIN, 2 REFACTOR); 1 capacidad MISSING documentada; 1 refactor surface identificado; 8 componentes de concurrencia mapeados con flujos observados; 5 contratos de comparación científica definidos; 4 mecanismos de durabilidad observados; 3 contratos de medición establecidos; fronteras hexagonales mapeadas (12/13 superficies auditadas respetadas, 1 violación documentada); trazabilidad completa a 12 Decision Candidates; resumen de Gap Matrix (25 GAPs: 3 P0, 15 P1, 7 P2); versiones fuente reconciliadas; afirmaciones epistemológicas corregidas; subset canónico de evidencia de verificación/lineage separado de scientific equality; DCs reformulados como decisiones, no implementación; nota sobre RETAIN/REFACTOR/MISSING añadida.
**Verificación de cadena de gobernanza:** Charter §8 → HITOs 0.1-0.9 → HITO_0.10 v1.0.1 (Gap Matrix) → este documento → ADR_F18_MASTER §7.
**Refinamientos respecto a HITOs previos:** No se identifican contradicciones materiales adicionales respecto de la evidencia fuente; las diferencias de clasificación, versión y semántica de contratos quedan explícitamente reconciliadas en este documento (conteos corregidos, GAP-0.5-02 degradado, DCs reformulados, versiones reconciliadas).
**Siguiente paso recomendado:** Emitir HITO_0.12 (Evidence Register & DC Resolutions) para completar los outputs obligatorios de Charter §8.

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
| 0.8 F0-C State Durability & Recovery Map | FROZEN v1.4.0 | Matriz de durabilidad |
| 0.9 F0-D Waste/FinOps Map | FROZEN v1.4.0 | Baseline de waste |
| 0.10 Architecture Gap Matrix Consolidated | FROZEN v1.0.1 | Output obligatorio Charter §8 |
| **0.11 Current State & Contract Map** | **FROZEN v1.0.1** | **Output obligatorio Charter §8** |

**Fase 0 casi completa.** Falta 1 output obligatorio: Evidence Register & DC Resolutions.