# HITO_0.1_F0-B_Concurrency_Blocking_Map.md

**Estado:** FROZEN v1.2.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** FASE0_AUDIT_CHARTER.md (preregistro FROZEN), FASE_6_HANDOFF.md v1.0.0, ADR_F17_BIS_MASTER.md, ENGINEERING_PRINCIPLES.md, METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0
**Mandato:** ¿Cuál es el mapa de concurrencia, bloqueo y coordinación del execution plane actual? ¿Qué fuentes de bloqueo existen y cómo impactan las capacidades C1, C3, C6 y C10 de Fase 18?
**Síntesis:** El execution plane opera bajo un modelo híbrido dual: asyncio nativo en el core del pipeline, con un adaptador síncrono (SyncProviderBridge) en el daemon de producción que introduce barreras síncronas cuyo impacto cuantitativo en C1/C3/C6/C10 debe medirse en F0-A.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-02 | Emisión inicial. Auditoría forense estática sobre 27 archivos del execution plane. |
| 1.1.0-FROZEN | 2026-10-02 | Adición de secciones 11, 18, 19 (completitud estructural). |
| 1.2.0-FROZEN | 2026-10-02 | Correcciones epistemológicas: separación estricta FACT/INFERENCE/RISK en E-0.1-001, E-0.1-002, E-0.1-004, E-0.1-006. Reemplazo de lenguaje evaluativo por observable. Rebaja de conclusiones adelantadas sobre SyncProviderBridge. |

---

## 1. RESUMEN EJECUTIVO

Se auditó el execution plane del Traductor PDF para mapear concurrencia, bloqueo y coordinación. La auditoría cubrió 27 archivos en `apps/llm_workers/`, `apps/cli/`, `apps/daemons/`, `core/pipeline/`, `core/execution/`, `runtime/` e `infra/db/`. Se verificaron contratos de puertos (`ControlPlanePort`, `EventPlanePort`), mecanismos de shutdown, y patrones de bloqueo.

**Hallazgo central:**

> El execution plane posee concurrencia asyncio nativa de calidad (AsyncDispatcher con PriorityQueue y cancelación), pero el daemon de producción utiliza un adaptador síncrono (SyncProviderBridge) que introduce barreras síncronas cuyo impacto cuantitativo en las capacidades C1, C3, C6 y C10 debe medirse en F0-A.

**Hechos observados confirmados:**

1. **Barrera síncrona en SyncProviderBridge (E-0.1-001):** `execute()` usa `future.result(timeout=180.0)`, bloqueando el thread del worker durante la duración de la llamada LLM.
2. **Coordinación multi-thread en el daemon (E-0.1-002):** El daemon coordina estado (lease heartbeat) y ejecución (bridge) a través de 3 threads independientes y 3 `threading.Event`.
3. **Shutdown con bounded join (E-0.1-004):** `SyncProviderBridge.shutdown()` usa `thread.join(timeout=2.0)` tras `future.cancel()`.

**Riesgos identificados (pendientes de F0-A/F0-C):**

1. **Riesgo de thread residual (E-0.1-004):** Si la librería HTTP subyacente no coopera con la cancelación asyncio, el thread del event loop podría quedar residual tras el shutdown.
2. **Limitación potencial de capacidad (E-0.1-001):** La barrera síncrona podría limitar la granularidad de coordinación y el backpressure, pero el impacto cuantitativo debe medirse.

**Veredicto:** El SyncProviderBridge emerge como superficie prioritaria de evaluación dentro de DC-01 y DC-06b; la evidencia actual no determina todavía si debe eliminarse, refactorizarse o conservarse. El impacto cuantitativo en C1/C3/C6/C10 debe medirse en F0-A.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia estática del código fuente. No ejecuta profiling de runtime (eso pertenece a F0-A / HITO_0.5). Las hipótesis sobre comportamiento runtime (ej. cooperación de librerías HTTP con cancelación asyncio) se marcan como `NO VERIFICABLE` desde este HITO.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (Charter F18, ADR Maestro 17-BIS, ENGINEERING_PRINCIPLES).
2. Cargar HITOs previos aplicables (FASE_6_HANDOFF como estado basal).
3. Inspeccionar código fuente mediante grep estructurado sobre 27 archivos (bloques [0]-[26] del script de auditoría).
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs normalizados.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar `TO BE VERIFIED` cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `apps/llm_workers/` | `sync_bridge.py`, `__main__.py`, `dispatcher.py`, `cache_provider.py`, `rate_limiter.py`, `circuit_breaker_provider.py` | 100% auditado |
| `apps/cli/` | `main.py` | 100% auditado |
| `apps/daemons/` | `reconciler.py` | 100% auditado |
| `core/pipeline/` | `orchestrator.py`, `workflow.py`, `state_store.py` | 100% auditado |
| `core/execution/` | `ports.py`, `state.py`, `handlers.py`, `models.py`, `constants.py` | 100% auditado |
| `core/resilience/` | `circuit_breaker.py` | 100% auditado |
| `runtime/` | `sweeper.py` | 100% auditado |
| `infra/db/` | `control_repo.py`, `event_repo.py`, `system_repo.py`, `profile_store.py`, `fsm_repository.py`, `materialized_repo.py` | 100% auditado |
| `infra/resilience/` | `sqlite_rate_limit_store.py` | 100% auditado |
| `core/benchmark/` | `runners/gemini_runner.py`, `runners/groq_runner.py` | Parcial (solo imports cruzados DF-06) |
| `core/document_profile/` | `ports.py` | Referenciado |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Charter | `docs/architecture/adr/phase-18/00-foundation/FASE0_AUDIT_CHARTER.md` | Fuente normativa: capacidades C1-C13, invariantes, reglas de Fase 0 |
| ADR | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` | Fuente normativa: jerarquía, carry-forwards |
| Handoff | `docs/architecture/adr/phase-17-bis/handoff/FASE_6_HANDOFF.md` | Estado basal del proyecto post-Fase 6 |
| Principios | `docs/architecture/ENGINEERING_PRINCIPLES.md` | Fuente normativa: principios inmutables |
| Código | 27 archivos `.py` (ver §3) | Observación forense primaria |
| Script | Bloques [0]-[26] del script PowerShell de auditoría | Evidencia cruda de grep estructurado |

---

## 5. MAPA DE FLUJOS OBSERVADOS

```text
FLUJO A -- Traducción vía CLI (handle_translate)

  apps/cli/main.py::handle_translate()
    -> asyncio.run(handle_translate_async())           [OK] async nativo
    -> build_provider_stack()                          [OK] async
    -> build_pipeline()                                [OK] composition root
    -> pipeline.execute(job)                           [OK] async
    -> dispatcher.dispatch(units)                      [OK] AsyncDispatcher nativo
    -> asyncio.PriorityQueue + asyncio.create_task     [OK] concurrencia controlada
    -> provider.translate(envelope)                    [OK] async directo

FLUJO B -- Traducción vía Daemon de producción (LLMWorkerDaemon)

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

Leyenda:
  [OK]   flujo sano observado
  [OBS]  característica arquitectónica observada (impacto pendiente de F0-A)
  [GAP]  gap confirmado
  [RISK] riesgo latente
  [TBD]  requiere verificación adicional
```

---

## 6. INVENTARIO DE COMPONENTES DE CONCURRENCIA

| Componente | Representación observada | Modelo | Participa en producción | Estado |
|---|---|---|---|---|
| `SyncProviderBridge` | `apps/llm_workers/sync_bridge.py::SyncProviderBridge` | Thread + asyncio loop dedicado | Sí (daemon + engine) | CONFIRMADO |
| `AsyncDispatcher` | `apps/llm_workers/dispatcher.py::AsyncDispatcher` | asyncio nativo (PriorityQueue, create_task) | Sí (CLI) / No (daemon) | CONFIRMADO |
| `TaskLeaseHeartbeat` | `apps/llm_workers/__main__.py::TaskLeaseHeartbeat` | threading.Thread + threading.Event | Sí (daemon) | CONFIRMADO |
| `LLMWorkerDaemon` | `apps/llm_workers/__main__.py::LLMWorkerDaemon` | Loop síncrono + threading.Event | Sí (daemon) | CONFIRMADO |
| `ReconcilerDaemon` | `apps/daemons/reconciler.py::ReconcilerDaemon` | Loop síncrono + threading.Thread (heartbeat) | Sí (daemon separado) | CONFIRMADO |
| `RecoveryDaemon` | `runtime/sweeper.py::RecoveryDaemon` | Loop síncrono + time.sleep | Sí (daemon separado) | CONFIRMADO |
| `TranslationPipeline` | `core/pipeline/orchestrator.py::TranslationPipeline` | async def execute() | Sí (CLI) | CONFIRMADO |
| `RoutingWorkflow` | `core/pipeline/workflow.py::RoutingWorkflow` | Síncrono (Iterator, yield) | Sí (pipeline interno) | CONFIRMADO |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-0.1-001** | P1 | `apps/llm_workers/sync_bridge.py::SyncProviderBridge.execute` → `future.result(timeout=self._timeout)` (L95) | **Barrera síncrona en el hilo llamante.** El método `execute()` bloquea el thread del worker con `future.result(timeout=180.0)`. El event loop asyncio corre en un `threading.Thread` separado (L25). Esto introduce una barrera síncrona cuyo impacto en C1 (Bounded Execution) y C3 (Backpressure) debe cuantificarse en F0-A. |
| **E-0.1-002** | P2 | `apps/llm_workers/__main__.py::LLMWorkerDaemon` → `_stop_event = threading.Event()` (L96), `TaskLeaseHeartbeat` → `stop_event = threading.Event()` (L43), `SyncProviderBridge` → `_ready_event = threading.Event()` (L26) | **Coordinación multi-thread observada.** El daemon de producción usa 3 threads independientes (main loop, heartbeat, bridge loop) y 3 `threading.Event` separados para coordinación. No existe un event loop unificado. Esta es una característica arquitectónica cuyo impacto potencial en C6 (Cancellation), C7 (Concurrency Safety) y C10 (Resource Efficiency) debe evaluarse en F0-A. |
| **E-0.1-003** | P2 | `apps/llm_workers/dispatcher.py::AsyncDispatcher.dispatch` → `asyncio.PriorityQueue()` (L233), `asyncio.create_task(self._worker(...))` (L285), `w.cancel()` (L291) | **Concurrencia nativa observada.** `AsyncDispatcher` implementa concurrencia asyncio con PriorityQueue (prioridades de costo), create_task y cancelación explícita. Sin embargo, el daemon de producción no lo usa directamente; pasa por `SyncProviderBridge`. |
| **E-0.1-004** | P2 | `apps/llm_workers/sync_bridge.py::SyncProviderBridge.shutdown` → `future.cancel()` (L99), `self._thread.join(timeout=2.0)` (L48) | **Shutdown con bounded join.** El shutdown cancela tareas pendientes y hace `join(timeout=2.0)` sobre el thread del event loop. **FACT:** El shutdown tiene un límite de tiempo acotado. **RISK:** Si `future.cancel()` no logra cancelar la coroutine subyacente (porque la librería HTTP no coopera con asyncio cancellation), el thread podría quedar residual. **NO DEMOSTRADO:** Que efectivamente existan threads huérfanos o impacto material de memoria/FD. |
| **E-0.1-005** | P2 | `apps/llm_workers/__main__.py` → `signal.signal(signal.SIGINT, shutdown_handler)` (L280), `signal.signal(signal.SIGTERM, shutdown_handler)` (L281) | **Shutdown por señal observado.** El daemon maneja SIGINT/SIGTERM configurando `_stop_event`. El handler llama `daemon.stop()` y luego `processor.shutdown()`. El orden es stop loop → shutdown bridge. |
| **E-0.1-006** | P2 | `apps/llm_workers/__main__.py::LLMWorkerDaemon.run` → `sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)` (L113) | **Backoff exponencial en polling.** El daemon usa backoff exponencial (base 1.0s, max 4.0s, factor 1.2) con jitter aleatorio para polling de tareas. **FACT:** El algoritmo puede introducir hasta ~4.5s de latencia adicional de polling bajo condición idle, según la implementación observada. **NO DEMOSTRADO:** Que esto tenga relevancia observable en el rendimiento del sistema bajo carga real. |
| **E-0.1-007** | P2 | `apps/llm_workers/dispatcher.py::AsyncDispatcher._worker` → `await queue.get()` (L134), `await self._provider.translate(envelope)` (L138), `queue.task_done()` (L219) | **Worker asíncrono observado.** El worker del dispatcher usa `await queue.get()` para backpressure, procesa la traducción asíncronamente, y marca `task_done()`. La estructura observada es compatible con bounded execution. |

### Evidencia E-0.1-001: Barrera síncrona en el hilo llamante

* **Archivo Fuente Primario:** `apps/llm_workers/sync_bridge.py`
* **Símbolo Auditado:** `SyncProviderBridge.execute`
* **Declaración Observada:**

```python
def execute(self, node: ASTNode) -> str:
    # ...
    future = asyncio.run_coroutine_threadsafe(self._provider.translate(envelope), self._loop)
    # ...
    result = future.result(timeout=self._timeout)  # L95: BLOQUEA el hilo llamante
```

* **Observed:** El método `execute()` es síncrono. Envía la coroutine al event loop del thread dedicado vía `run_coroutine_threadsafe` y bloquea el hilo llamante con `future.result(timeout=180.0)`.
* **Required:** C1 (Bounded Execution) y C3 (Backpressure) exigen que el execution plane pueda limitar la concurrencia y ejercer backpressure.
* **Decision:** No hay decisión previa documentada sobre este patrón. El bridge fue introducido como adaptador pragmático para conectar el pipeline async con el daemon síncrono.
* **Hallazgo Forense:** **FACT:** El patrón "async-en-thread" introduce una barrera síncrona en el hilo llamante. **INFERENCE:** Esta barrera podría limitar la granularidad de coordinación y el backpressure. **NO DEMOSTRADO:** El impacto cuantitativo en C1/C3 debe medirse en F0-A.
* **Consecuencia Arquitectónica:** DC-01 (fork de concurrencia) y DC-06b (supervivencia de técnicas del ROADMAP) deben evaluar el SyncProviderBridge como superficie prioritaria; la evidencia actual no determina si debe eliminarse, refactorizarse o conservarse.
* **Estado:** OPEN (impacto cuantitativo pendiente de F0-A)

### Evidencia E-0.1-004: Shutdown con bounded join

* **Archivo Fuente Primario:** `apps/llm_workers/sync_bridge.py`
* **Símbolo Auditado:** `SyncProviderBridge.shutdown`
* **Declaración Observada:**

```python
def shutdown(self) -> None:
    # ... cancelación de pending tasks ...
    self._thread.join(timeout=2.0)  # L48
```

* **Observed:** El shutdown cancela tareas pendientes y hace `join(timeout=2.0)` sobre el thread del event loop.
* **Required:** C6 (Cancellation) exige cancelación limpia sin fuga de recursos. C4 (Recovery) exige que el sistema pueda reiniciarse sin estado residual.
* **Decision:** No hay decisión previa documentada.
* **Hallazgo Forense:** **FACT:** El shutdown tiene un límite de tiempo acotado (2.0s). **FACT:** `future.cancel()` precede al join. **NO DEMOSTRADO:** Que la coroutine no coopere con cancelación. **NO DEMOSTRADO:** Que se produzca thread leak. **NO DEMOSTRADO:** Que exista impacto material de memoria/FD. **RISK:** Thread/event-loop residual si la cancelación no coopera.
* **Consecuencia Arquitectónica:** En un entorno de 16GB RAM, threads residuales con sockets abiertos podrían consumir memoria y file descriptors, agravando el riesgo de OOM. Esto debe verificarse en F0-C.
* **Estado:** TO BE VERIFIED (requiere F0-A/F0-C para confirmar comportamiento real)

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.1-01** | SyncProviderBridge introduce barrera síncrona en el hilo llamante; el impacto cuantitativo en C1/C3 debe medirse. | E-0.1-001 | C1, C3, INV-OPS-1 | **Fase 18** (DC-01, DC-06b) | OPEN |
| **GAP-0.1-02** | Coordinación multi-thread observada; el impacto potencial en C6/C7/C10 debe evaluarse. | E-0.1-002 | C6, C10 | **Fase 18** (DC-01) | OPEN |
| **GAP-0.1-03** | Riesgo de thread residual en shutdown; debe verificarse en F0-C. | E-0.1-004 | C4, C6 | **Fase 18** (DC-01) | TO BE VERIFIED |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.1-A | El AsyncDispatcher podría reemplazar al SyncProviderBridge en el daemon sin cambios en la semántica científica. | NO VERIFICABLE | E-0.1-003 confirma que AsyncDispatcher existe y es funcional; pero no se ha verificado que el daemon pueda operar completamente en asyncio sin afectar INV-SCI-1. | Si se confirma en F0-E, habilita la elisión del bridge (DC-06b). |
| H-0.1-B | Las librerías HTTP de los proveedores LLM (GROQ, Gemini) no cooperan con `asyncio.Task.cancel()` durante una request en vuelo. | NO VERIFICABLE | E-0.1-004 muestra el mecanismo de riesgo; la verificación requiere ejecución real (F0-A). | Si se confirma, el shutdown del bridge requiere un mecanismo de cancelación más robusto. |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-01** | Fork de concurrencia: async single-process + executors vs multi-process | E-0.1-001, E-0.1-002, E-0.1-003, E-0.1-004 | Parcial: asyncio nativo existe (AsyncDispatcher) pero no se usa en daemon | **Fase 18** |
| **DC-06b** | ¿Las técnicas prescritas del ROADMAP sobreviven? (elisión de SyncProviderBridge) | E-0.1-001, E-0.1-003 | Ausente: el bridge sigue activo en producción | **Fase 18** |

---

## 19. APÉNDICE NO NORMATIVO -- RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| OOM por threads residuales | Si el shutdown del bridge falla, threads con sockets abiertos podrían consumir RAM/VRAM en un sistema de 16GB/4GB. | Alto (potencial) | E-0.1-004 |
| Latencia de polling | El backoff exponencial (max 4.0s + jitter 0.5s) podría introducir hasta ~4.5s de latencia en la detección de nuevas tareas bajo condición idle. | Medio (potencial) | E-0.1-006 |
| Thundering herd post-crash | Si múltiples workers se reinician simultáneamente tras un crash, todos podrían intentar `pick_task` al mismo tiempo. Mitigado parcialmente por `BEGIN IMMEDIATE`. | Medio (potencial) | E-0.1-002 |

---

## 21. CIERRE DEL HITO 0.1

Este HITO confirma que el execution plane posee concurrencia asyncio nativa (AsyncDispatcher) pero opera en producción a través de un bridge síncrono que introduce barreras síncronas y coordinación multi-thread. El impacto cuantitativo en C1/C3/C6/C10 debe medirse en F0-A.

**Estado del HITO:** FROZEN v1.2.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados, todas las evidencias tienen ID estable y severidad, todos los gaps tienen fase destino explícita, todas las hipótesis cerradas (NO VERIFICABLE), separación estricta FACT/INFERENCE/RISK aplicada, lenguaje evaluativo reemplazado por observable.
**Verificación de cadena de gobernanza:** Charter F18 FROZEN → F0-B mandato → este HITO. Cadena verificada.
**Contradicciones con HITOs previos:** Ninguna (primer HITO de Fase 18).
**Decision Candidates generados:** DC-01 (evidencia de entrada), DC-06b (evidencia de entrada).
**Siguiente paso recomendado:** Completar HITO_0.2 (F0-G Authority Boundary Map) para tener la visión completa del execution plane antes de proceder a F0-F y F0-E.