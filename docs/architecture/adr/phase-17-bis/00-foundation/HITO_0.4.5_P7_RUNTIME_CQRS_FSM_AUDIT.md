# HITO_0.4.5_P7_RUNTIME_CQRS_FSM_AUDIT.md
## Runtime Engine, CQRS Repositories, FSM Governance & Operational Recovery Boundary — Reporte de Auditoría Forense Integral Bloque P7

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P7)
* **Fecha de Emisión:** 2026-07-29
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P7)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta basada en el examen directo del código fuente operacional (`apps/daemons/reconciler.py`, `core/execution/handlers.py`, `core/pipeline/state_store.py`, `infra/db/control_repo.py`, `infra/db/fsm_repository.py`, `runtime/engine.py`, `runtime/reconciliation.py`, `runtime/recovery.py` y `runtime/resumer.py`)[cite: 4], aplicando el protocolo de investigación de 15 capas. Cero suposiciones. Cero mutaciones en código productivo.

---

## 1. MARCO EPISTEMOLÓGICO Y DIAGNÓSTICO DE RUNTIME

Sometiendo el Bloque P7 al protocolo de investigación de 15 capas (Capa 1: Evidencia vs. Interpretación; Capa 7: Detección de Contaminación; Capa 11: Falsación Sistemática; Capa 14: Invariantes del Sistema), el análisis del código fuente **ha demostrado la coexistencia de un núcleo FSM/CAS excepcionalmente robusto junto con una severa dualidad de motores de ejecución y componentes de resiliencia desactivados por banderas de entorno**.

Respondiendo a la pregunta central de la auditoría:
> *¿El runtime operacional realmente gobierna el pipeline de producción, o existe un pipeline paralelo que lo evita?*

**Demostración:** El sistema no posee un único camino de ejecución. Coexisten dos motores de ejecución desconectados:
1. **La ruta por Objetos / Orquestador (`core/pipeline/orchestrator.py`):** Utilizada en invocaciones sincrónicas y tests, gobernada por `FSMStateStore`.
2. **El motor distribuido de Runtime (`runtime/engine.py`):** Un script standalone multihilo (`ThreadPoolExecutor`) que realiza lecturas y escrituras directas sobre las tablas SQLite de CQRS (`fsm.db`, `queue.db`, `event.db`, `materialized.db`) bypassando `TranslationPipeline`.

```text
==================================================================================================
                 FLUJO TEÓRICO DECLARADO PARA EL BLOQUE P7 (FALSADO)
==================================================================================================

  [API / CLI] ──► [TranslationPipeline] ──► [FSMStateStore] ──► [DocumentCommandHandler]
                                                                        │
                                                                        ▼
  [CQRS Reconciler] ◄── [Control/Event/Materialized Planes] ◄── [FSMRepository]

==================================================================================================
                 FLUJO REAL OBSERVADO EN RUNTIME (DEMOSTRADO POR CÓDIGO)
==================================================================================================

               ┌─────────────────────────────────────────────────────────┐
               │ RUTA A: Orquestador Objetos (core/pipeline/orchestrator)│
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                                   [FSMStateStore] (Auto-promoción oculta)
                                            │
                                            ▼
                               [DocumentCommandHandler]
                                            │
                                            ▼
                                     [FSMRepository] (CAS Lock con state_version)
                                            ▲
               ┌────────────────────────────┴────────────────────────────┐
               │ RUTA B: Motor Distribuido Paranclelo (runtime/engine.py)│
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ├──► ThreadPoolExecutor + Pick Tasks Directo
                                            ├──► Invocación directa GroqProvider / MathProtector
                                            └──► Upsert manual en CQRS + WAL Log
                                            
  [DAEMONS DESCONECTADOS / EN RIESGO]:
  ├── runtime/reconciliation.py ──► [EXPERIMENTAL_ENABLED = False] (Bypass 100% inactivo)
  └── ReconciliationCommandHandler ──► Inserta "unknown_ast_hash" (Ruptura de Query Model)
```

---

## 2. REGISTRO EXHAUSTIVO DE HALLAZGOS FORENSES (P7-H01 A P7-H06)

### P7-H01: Dinarismo de Ejecución (Dualidad entre `orchestrator.py` y `runtime/engine.py`) [DEMOSTRADO]
* **Ubicación:** `runtime/engine.py` vs. `core/pipeline/orchestrator.py`
* **Demostración por Código Fuente:**
  In `runtime/engine.py` (`run_pipeline()`), se implementa un bucle `while True` con un `ThreadPoolExecutor(max_workers=max_threads)` que abre conexiones SQLite directas a `queue.db`, `event.db` y `materialized.db`. Dentro de cada hilo, extrae tareas con `th_task_repo.pick_task()`, aplica la máscara `InlineMathProtector.mask()`, invoca al LLM mediante `SyncProviderBridge`, escribe en la WAL (`append_wal`), actualiza la proyección (`upsert_projection`) y marca la tarea como completada.
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. Duplicación completa de responsabilidades. Se mantiene un motor entero de ejecución fuera de `core/pipeline/orchestrator.py` que no utiliza `TranslationPipeline` ni las políticas de validaciones de `ValidationPipeline` (Bloque P5).

---

### P7-H02: Inactivación Absoluta del Daemon de Reconciliación CQRS (`EXPERIMENTAL_ENABLED = False`) [DEMOSTRADO]
* **Ubicación:** `runtime/reconciliation.py`
* **Demostración por Código Fuente:**
  In `CQRSReconciliationDaemon.run_reconciliation_cycle()`:
  ```python
  EXPERIMENTAL_ENABLED = False

  class CQRSReconciliationDaemon:
      def run_reconciliation_cycle(self) -> None:
          if not EXPERIMENTAL_ENABLED:
              logger.info("CQRS_RECONCILER_BYPASS: El componente se encuentra en estado EXPERIMENTAL (Desactivado).")
              return
  ```
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. La sanación de proyecciones y la liberación de tareas huérfanas en el `ControlPlaneRepository` a través del daemon `runtime/reconciliation.py` está **$100\%$ inactiva en tiempo de ejecución**. Si este proceso se ejecuta como servicio, retorna inmediatamente en el primer `if` sin procesar ninguna tarea expirada.

---

### P7-H03: Certificación de Excelencia en el Núcleo FSM (Control de Concurrencia Optimista CAS) [DEMOSTRADO]
* **Ubicación:** `infra/db/fsm_repository.py` & `core/execution/handlers.py`
* **Demostración por Código Fuente:**
  En `FSMRepository.transition_to()`:
  ```python
  cursor = self.db.execute(
      """UPDATE document_fsm
         SET current_state = ?, state_version = state_version + 1, ...
         WHERE document_id = ? AND ast_hash = ? AND current_state = ?
           AND state_version = ?""",
      (...)
  )
  if cursor.rowcount == 0:
      raise OptimisticLockError(...)
  ```
  Adicionalmente, `DocumentCommandHandler.handle()` exige validación estricta de grafo de estados vía `FSMValidator.validate(current_state, target_state)` previo al `UPDATE`.
* **Veredicto Metodológico:** **SOTA / APROBADO**. El núcleo de la máquina de estados finitos es uno de los componentes más sólidos del sistema. Garantiza exclusión mutua mediante Compare-And-Swap (CAS) inmutable con `state_version`.

---

### P7-H04: Contaminación de Capas por Comandos SQL `ATTACH DATABASE` en Repositorios [DEMOSTRADO]
* **Ubicación:** `infra/db/control_repo.py` (`find_documents_with_pending_chunks()`) & `apps/daemons/reconciler.py`
* **Demostración por Código Fuente:**
  In `ControlPlaneRepository`:
  ```python
  def find_documents_with_pending_chunks(self, sample_size: int = 10):
      import os
      fsm_path = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
      self.conn.execute(f"ATTACH DATABASE '{fsm_path}' AS fsm_db")
      ...
  ```
* **Impacto Arquitectónico:** **[P1 - ALTO]**. Fuga de abstracción de infraestructura. Un repositorio del dominio de control ejecuta sentencias DDL/DML de adjunción de bases de datos de SQLite (`ATTACH DATABASE`) con rutas relativas por defecto en disco, acoplando la lógica de consulta a la topología física de archivos SQLite en lugar de encapsular la lectura en un puerto unificado.

---

### P7-H05: Auto-Promoción Oculta de Estados en `FSMStateStore` [DEMOSTRADO]
* **Ubicación:** `core/pipeline/state_store.py` (`FSMStateStore.save()`)
* **Demostración por Código Fuente:**
  In `FSMStateStore.save()`:
  ```python
  if status.current_state == "PROCESSING" and cmd_class == StartAssemblyCommand:
      cmd_ready = MarkAssemblyReadyCommand(...)
      expected_version = self.handler.handle(cmd_ready)

  if status.current_state == "ASSEMBLING" and cmd_class == CompleteDocumentCommand:
      cmd_ready_comp = MarkCompilationReadyCommand(...)
      expected_version = self.handler.handle(cmd_ready_comp)
      cmd_start_comp = StartCompilationCommand(...)
      expected_version = self.handler.handle(cmd_start_comp)
  ```
* **Impacto Arquitectónico:** **[P2 - MEDIO]**. El adaptador de estado oculta la desconexión de granularidad entre el `TranslationJob` (pasos macro: `PARSING`, `CHUNKING`, `ASSEMBLING`, `FINISHED`) y la FSM Fina (`READY_FOR_ASSEMBLY`, `ASSEMBLING`, `READY_FOR_COMPILATION`, `COMPILING`). `FSMStateStore` intercepta los saltos y emite comandos sintéticos intermedios en cadena para no violar la FSM.

---

### P7-H06: Corrupción de Linaje Topológico por `"unknown_ast_hash"` en Re-materialización CQRS [DEMOSTRADO]
* **Ubicación:** `core/execution/handlers.py` (`ReconciliationCommandHandler.handle_rematerialize()`)
* **Demostración por Código Fuente:**
  In `ReconciliationCommandHandler.handle_rematerialize()`:
  ```python
  self.mat.upsert_projection(
      cmd.document_id, "unknown_ast_hash", cmd.node_id, latest_event.content_hash, 
      normalized, normalized_hash, latest_event.projection_version
  )
  ```
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. Bug de consistencia en el Query Model. Cuando el reconciliador rescata un evento del WAL y re-materializa la proyección, inyecta la cadena `"unknown_ast_hash"` porque `RematerializeTaskCommand` carece del atributo `ast_hash`. Posteriormente, cuando `MaterializedPlaneRepository.get_assemblable_chunks()` busca los fragmentos listos usando el `ast_hash` real del documento, la proyección re-materializada **jamás coincide**, dejando el documento estancado indefinidamente.

---

## 3. TRAZABILIDAD Y FLUJO DE DATOS OPERACIONAL (FSM & CQRS)

```text
==================================================================================================
                 TRAZABILIDAD FSM / CAS Y CQRS EN RUNTIME (CÓDIGO VERIFICADO)
==================================================================================================

  [DocumentCommand] (ej. StartAssemblyCommand)
         │
         ▼
  [DocumentCommandHandler.handle()]
         │
         ├──► (1) FSMRepository.get_status() ──► DocumentStatusDTO(state_version)
         ├──► (2) FSMValidator.validate(old_state, new_state)
         │
         ▼
  [FSMRepository.transition_to()]
         │
         ├── UPDATE document_fsm ... WHERE state_version = expected_version
         │
         ├── (Exito)  ──► state_version + 1 (Retorna a Handler)
         └── (Fallo)  ──► cursor.rowcount == 0 ──► raise OptimisticLockError
                                                         │
                                                         ▼
                                             [Trabajo capturado por otro worker]

==================================================================================================
                 RUTA DE CORRUPCIÓN EN RE-MATERIALIZACIÓN CQRS (P7-H06)
==================================================================================================

  [WAL Event Log] ──► (lifecycle: GENERATED)
                            │
                            ▼
  [ReconciliationCommandHandler.handle_rematerialize()]
                            │
                            ▼
  [MaterializedPlaneRepository.upsert_projection()]
  (Parámetro ast_hash hardcodeado: "unknown_ast_hash")
                            │
                            ▼
  [Materialized DB] (Projection guardada con ast_hash="unknown_ast_hash")
                            │
                            ▼
  [MaterializedPlaneRepository.get_assemblable_chunks(doc_id, REAL_AST_HASH)]
                            │
                            ▼
           [MISS ✗] Projection no encontrada ──► Documento colgado eternamente
```

---

## 4. TAXONOMÍA Y MATRIZ DE COMPONENTES DEL BLOQUE P7

| Componente / Módulo | Categoría Arquitectónica | Severidad | Diagnóstico Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `infra/db/fsm_repository.py` | Persistence Core | **Cero** | Núcleo FSM con gobernanza CAS (`state_version`) impecable. | **CONSERVAR** |
| `core/execution/handlers.py` | Command Handler | **P0 (Crítico)** | Re-materialización inyecta `"unknown_ast_hash"` rompiendo el Query Model. | **REPARAR COMANDO/HANDLER** |
| `runtime/engine.py` | Runtime Parallel | **P0 (Crítico)** | Motor de ejecución paralelo que duplica y salta `orchestrator.py`. | **UNIFICAR EN ORQUESTADOR** |
| `runtime/reconciliation.py` | CQRS Daemon | **P0 (Crítico)** | Inactivo en runtime por bandera `EXPERIMENTAL_ENABLED = False`. | **ACTIVAR Y ESTABILIZAR** |
| `core/pipeline/state_store.py` | State Adapter | **P2 (Medio)** | Promoción implícita en cadena de comandos intermedios de la FSM. | **TRANSPARENTAR ESTADOS** |
| `infra/db/control_repo.py` | Persistence Core | **P1 (Alto)** | Inyección de SQL `ATTACH DATABASE` con rutas relativas por defecto. | **ENCAPSULAR CONSULTAS** |
| `runtime/recovery.py` | Watchdog | **Cero** | Escaneo y aislamiento de procesos zombi (`StallDocumentCommand`). | **CONSERVAR** |
| `runtime/resumer.py` | On-Demand Resumer | **Cero** | Rescate limpio de documentos en `STALLED` vía comandos CAS. | **CONSERVAR** |

---

## 5. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P7-R01 A P7-R05)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P7-R01 (Reparación de Contrato en Rematerialización CQRS - P0):** Extender `RematerializeTaskCommand` en `core/execution/state.py` para incluir obligatoriamente el atributo `ast_hash`. Modificar `ReconciliationCommandHandler.handle_rematerialize()` para utilizar el `ast_hash` real al invocar `upsert_projection()`, eliminando el valor estático `"unknown_ast_hash"`.
* **P7-R02 (Unificación de Motor de Ejecución en Runtime - P0):** Deprecar el bucle manual de parancleo en `runtime/engine.py` y hacer que utilice la abstracción oficial `TranslationPipeline` inyectada desde `pipeline_factory.py`, evitando la duplicación de lógica de dispatch, enrutamiento y sanitización.
* **P7-R03 (Activación de Reconciliación CQRS - P0):** Modificar la bandera `EXPERIMENTAL_ENABLED` en `runtime/reconciliation.py` o parametrizarla mediante variables de entorno de producción para que `CQRSReconciliationDaemon` ejecute la sanación activa de leases expirados.
* **P7-R04 (Desacoplamiento de Sentencias ATTACH en Repositorios - P1):** Eliminar la ejecución directa de `ATTACH DATABASE` con concatenación de cadenas dentro de los métodos de consulta de `ControlPlaneRepository`. La vinculación de bases de datos adjuntas debe gestionarse de forma transparente en el módulo de conexión `infra/db/connection.py`.
* **P7-R05 (Sincronización de Granularidad FSM y StateStore - P2):** Exponer los estados intermedios de compilación y ensamblado en `PipelineStep` (`READY_FOR_ASSEMBLY`, `READY_FOR_COMPILATION`) para que las llamadas a `FSMStateStore.save()` reflejen exactamente el paso en ejecución sin requerir auto-promociones sintéticas en cadena.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Núcleo de Transición y FSM:** **SÓLIDO Y SOTA.** El repositorio FSM y los manejadores de comandos protegen al sistema de manera efectiva contra escrituras zombi y conflictos de concurrencia mediante exclusión mutua optimista (CAS).
2. **Coherencia del Runtime y CQRS:** **GRAVEMENTE FRACTURADO.** La existencia de dos vías de ejecución (`orchestrator.py` vs. `runtime/engine.py`), la desactivación por código del daemon de reconciliación y el bug del hash desconocido en la re-materialización impiden certificar la gobernanza operacional del sistema.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P7

The audit for **Block P7 (Runtime / CQRS / FSM / Recovery / Operational Boundary)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P7
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada por Código Fuente)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Dualidad de Runtime, Reconciliador Inactivo y Bug en CQRS)
  Remediation Backlog      | OPEN (Reglas P7-R01 a P7-R05 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría forense del Bloque P7. Se certifica la excelencia técnica del núcleo FSM y sus bloqueos de concurrencia optimista (CAS). No obstante, se rechaza la certificación del runtime operacional debido a: (1) la dualidad entre TranslationPipeline y runtime/engine.py, (2) la inactivación por bandera de código de CQRSReconciliationDaemon (EXPERIMENTAL_ENABLED=False), y (3) el bug crítico en ReconciliationCommandHandler que inyecta 'unknown_ast_hash' corrompiendo las consultas del MaterializedPlaneRepository. Queda estrictamente prohibido mutar código durante la Fase 0. Las normativas P7-R01 a P7-R05 quedan congeladas en el backlog de remediación del Hito 0.5."*
```