# HITO_0.2_F0-G_Authority_Boundary_Map.md

**Estado:** FROZEN v1.2.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** FASE0_AUDIT_CHARTER.md (preregistro FROZEN), FASE_6_HANDOFF.md v1.0.0, ADR_F17_BIS_MASTER.md, ENGINEERING_PRINCIPLES.md, METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0, HITO_0.1_F0-B_Concurrency_Blocking_Map.md
**Mandato:** ¿Cuáles son las autoridades existentes en el execution plane, qué estado poseen, dónde están sus fronteras, y cuáles son candidates a reuse/extend/replace en Fase 18?
**Síntesis:** La arquitectura hexagonal posee autoridades maduras en control (leases), liderazgo (fencing epoch), eventos (WAL), resiliencia (rate limiter persistente) y recovery (sweeper con WAL checkpoint). Se confirman tres gaps: ProfileStore no durable (DF-34), Circuit Breaker in-memory sin persistencia, e imports cruzados core→apps (DF-06). DF-24 se reabre bajo DC-01/DC-08.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-02 | Emisión inicial. Inventario forense de 15 autoridades en el execution plane. |
| 1.1.0-FROZEN | 2026-10-02 | Adición de secciones 11, 18, 19 (completitud estructural). |
| 1.2.0-FROZEN | 2026-10-02 | Correcciones epistemológicas: E-0.2-006 (no afirmar thundering herd), DF-24 reabierto bajo DC-01/DC-08, H-0.2-A rebajada de CONFIRMADA a HYPOTHESIS, E-0.2-004 (ProfileStore: cuantificar impacto), lenguaje evaluativo reemplazado por observable. |

---

## 1. RESUMEN EJECUTIVO

Se auditó el execution plane para inventariar autoridades existentes, sus fronteras, el estado que poseen y su clasificación reuse/extend/replace. La auditoría cubrió 15 componentes en `core/execution/`, `core/resilience/`, `infra/db/`, `infra/resilience/`, `apps/daemons/`, `apps/llm_workers/` y `runtime/`. Se verificaron contratos de puertos, mecanismos de persistencia y fronteras hexagonales.

**Hallazgo central:**

> La arquitectura posee autoridades bien delimitadas para control, liderazgo, eventos y resiliencia, con mecanismos de leasing, fencing epoch y persistencia SQLite ya implementados. Sin embargo, dos componentes carecen de durabilidad observada (ProfileStore in-memory, Circuit Breaker in-memory), lo que podría comprometer la recuperación ante crashes en un entorno de 16GB RAM; el impacto operacional debe cuantificarse.

**Hechos observados confirmados:**

1. **ProfileStore no durable (E-0.2-004):** `InMemoryProfileStore` usa un `dict` en memoria. Tras un crash, el perfil inferido del documento se pierde.
2. **Circuit Breaker in-memory sin persistencia (E-0.2-006):** `GlobalCircuitBreaker` mantiene estado (CLOSED/OPEN/HALF_OPEN) y métricas exclusivamente en memoria con `asyncio.Lock()`.
3. **Imports cruzados core→apps (E-0.2-005):** `core/benchmark/runners/` importa directamente de `apps.llm_workers` y `apps.bootstrap`, violando la frontera hexagonal.

**Riesgos identificados (pendientes de F0-A/F0-C):**

1. **Riesgo de recuperación agresiva post-crash (E-0.2-006):** Un crash reinicia todos los CBs a CLOSED simultáneamente, lo que podría permitir una recuperación concurrente agresiva.
2. **Costo potencial de recálculo de perfiles (E-0.2-004):** Tras crash, el sistema podría verse forzado a reconstruir perfiles; el costo y necesidad para recovery deben cuantificarse.

**Veredicto:** La base de autoridades es sólida y reutilizable. Los tres gaps identificados son de severidad P1 y deben resolverse en Fase 18 (DF-34, DF-06) o documentarse como Decision Candidates (persistencia de Circuit Breaker → DC-01/DC-08, DF-24 reabierto).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es inventariar y clasificar autoridades existentes. La clasificación reuse/extend/replace es provisional y se valida contra los DCs del Charter. No se audita la durabilidad real de los mecanismos de persistencia (eso pertenece a F0-C / HITO_0.6).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (Charter F18, ADR Maestro, ENGINEERING_PRINCIPLES).
2. Cargar HITO_0.1 (F0-B) como insumo de contexto.
3. Inspeccionar código fuente mediante grep estructurado sobre 15 componentes de autoridad.
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs normalizados.
6. Clasificar cada autoridad como RETAIN/REFACTOR/RELOCATE/MISSING.
7. Consolidar gaps con fase destino explícita.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/execution/` | `ports.py`, `state.py`, `handlers.py` | 100% auditado |
| `core/resilience/` | `circuit_breaker.py` | 100% auditado |
| `core/document_profile/` | `ports.py` | 100% auditado |
| `infra/db/` | `control_repo.py`, `event_repo.py`, `system_repo.py`, `profile_store.py`, `fsm_repository.py`, `materialized_repo.py`, `document_repository.py` | 100% auditado |
| `infra/resilience/` | `sqlite_rate_limit_store.py` | 100% auditado |
| `apps/daemons/` | `reconciler.py` | 100% auditado |
| `apps/llm_workers/` | `rate_limiter.py`, `circuit_breaker_provider.py`, `cache_provider.py` | 100% auditado |
| `runtime/` | `sweeper.py` | 100% auditado |
| `core/benchmark/runners/` | `gemini_runner.py`, `groq_runner.py` | Parcial (solo imports cruzados) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Charter | `FASE0_AUDIT_CHARTER.md` | Capacidades C1-C13, invariantes, DCs |
| ADR | `ADR_F17_BIS_MASTER.md` | Jerarquía normativa, carry-forwards |
| Handoff | `FASE_6_HANDOFF.md` | Estado basal, DF-06, DF-34 |
| HITO previo | `HITO_0.1_F0-B_Concurrency_Blocking_Map.md` | Contexto de concurrencia |
| Código | 15+ archivos `.py` (ver §3) | Observación forense primaria |

---

## 6. INVENTARIO DE AUTORIDADES

| Autoridad | Representación | Estado que posee | Frontera | Clasificación |
|---|---|---|---|---|
| Control Plane | `core/execution/ports.py::ControlPlanePort` → `infra/db/control_repo.py::ControlPlaneRepository` | Leases, task state, execution_id, retry_count | Puerto Protocol en core; implementación SQLite en infra | RETAIN |
| Event Plane | `core/execution/ports.py::EventPlanePort` → `infra/db/event_repo.py::EventPlaneRepository` | WAL de eventos (chunk_events_log) | Puerto Protocol en core; implementación SQLite en infra | RETAIN |
| Materialized Plane | `core/execution/ports.py::MaterializedPlanePort` → `infra/db/materialized_repo.py::MaterializedPlaneRepository` | Proyecciones de chunks traducidos | Puerto Protocol en core; implementación SQLite en infra | RETAIN |
| System Plane (Leadership) | `infra/db/system_repo.py::SystemPlaneRepository` | Leadership leases, epoch | Sin puerto abstracto (acceso directo) | RETAIN |
| FSM State | `core/execution/state.py::DocumentState` + `core/pipeline/state_store.py::FSMStateStore` → `infra/db/fsm_repository.py::FSMRepository` | Estado del documento (CREATED→COMPLETED), transiciones, suspended_reason | Tabla de transiciones en core; persistencia en infra | RETAIN |
| Reconciler | `apps/daemons/reconciler.py::ReconcilerDaemon` | Convergencia CQRS, zombie recovery, FSM stall detection | Daemon en apps; consume SystemPlane + ControlPlane | RETAIN |
| Recovery Sweeper | `runtime/sweeper.py::RecoveryDaemon` | WAL checkpoint, purga de documentos STALLED (>3600s) | Daemon en runtime; consume FSMRepository | RETAIN |
| Rate Limiter | `apps/llm_workers/rate_limiter.py::QuotaManager` + `infra/resilience/sqlite_rate_limit_store.py::SQLiteRateLimitStore` | Token buckets (RPM/TPM), estado persistente | Lógica en apps; persistencia en infra | RETAIN |
| Circuit Breaker | `core/resilience/circuit_breaker.py::GlobalCircuitBreaker` + `CircuitBreakerRegistry` | Estado CB (CLOSED/OPEN/HALF_OPEN), métricas de fallos | In-memory en core; sin persistencia | REFACTOR |
| Cache | `apps/llm_workers/cache_provider.py::CachedLLMProvider` | Cache de respuestas LLM por prompt_hash | Autoridad de cache en apps; usa aiosqlite | RETAIN |
| Profile Store | `core/document_profile/ports.py::ProfileStore` → `infra/db/profile_store.py::InMemoryProfileStore` | Perfiles inferidos de documentos | Puerto Protocol en core; implementación in-memory en infra | REFACTOR |
| Document Repository | `infra/db/document_repository.py::SQLiteDocumentRepository` | Documentos persistidos | Implementación en infra | RETAIN |
| Command Handlers | `core/execution/handlers.py::DocumentCommandHandler` | Procesamiento de comandos FSM (Start, Fail, Cancel, Stall, RecoverZombie) | Core puro | RETAIN |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-0.2-001** | P2 | `infra/db/control_repo.py::ControlPlaneRepository.pick_task` → `self.conn.execute("BEGIN IMMEDIATE")` (L42), `WHERE lease_owner IS NULL OR lease_expires_at < ?` (L51) | **Admisión con optimistic locking observada.** `pick_task` usa `BEGIN IMMEDIATE` y filtra por lease expirado o nulo, previniendo doble asignación. El lease tiene TTL de 300s (L39). La estructura observada es compatible con C2 y C5. |
| **E-0.2-002** | P2 | `apps/daemons/reconciler.py::ReconcilerDaemon.run` → `epoch = self.system.acquire_leadership(...)` (L99), `if epoch == 0:` (L100), fencing check en sweep (L147) | **Liderazgo con fencing epoch observado.** El reconciler adquiere liderazgo y verifica el epoch en cada iteración. Si pierde liderazgo (epoch=0), degrada a follower sin matar el proceso (L83). La estructura observada es compatible con C7. |
| **E-0.2-003** | P1 | `infra/db/event_repo.py::EventPlaneRepository.append_wal` → `INSERT INTO chunk_events_log ...` (L45), `self.conn.commit()` (L53) | **WAL sin coordinación transaccional con efecto externo observada.** El repositorio expone `append_wal` como operación atómica de DB. Sin embargo, no hay evidencia de que el Orchestrator/Dispatcher coordine esta llamada con el efecto externo (llamada LLM) en un patrón de intent/lease. El gap está a nivel de caso de uso, no de repositorio. |
| **E-0.2-004** | P1 | `infra/db/profile_store.py::InMemoryProfileStore` → `self._store: dict[str, InferredDocumentProfile] = {}` (L9) | **ProfileStore no durable observado.** La implementación activa es un wrapper de `dict`. Tras un crash, el perfil inferido se pierde. **FACT:** El estado no sobrevive al crash. **NO DEMOSTRADO:** Que el perfil sea necesario para recovery, que se utilice durante recovery, o que recalcularlo tenga costo material. Confirma DF-34. |
| **E-0.2-005** | P1 | `core/benchmark/runners/gemini_runner.py` → `from apps.llm_workers.prompt_builder import PromptBuilder` (L15), `from apps.bootstrap.provider_stack_factory import build_provider_stack` (L17) | **Imports cruzados core→apps observados.** Módulos en `core/benchmark` importan directamente de `apps.llm_workers` y `apps.bootstrap`. Viola la frontera hexagonal. Confirma DF-06. |
| **E-0.2-006** | P1 | `core/resilience/circuit_breaker.py::GlobalCircuitBreaker` → `self._lock = asyncio.Lock()` (L29), `self.failure_timestamps` (deque in-memory), `self.state = CircuitState.CLOSED` (L19) | **Circuit Breaker in-memory sin persistencia observado.** El estado del CB (CLOSED/OPEN/HALF_OPEN) y las métricas de fallos viven exclusivamente en memoria. No hay store de persistencia. **FACT:** Un crash reinicia todos los CBs a CLOSED simultáneamente. **RISK:** Esto podría eliminar el conocimiento de un estado OPEN previamente establecido y permitir una recuperación concurrente agresiva. **NO DEMOSTRADO:** Que produzca efectivamente un thundering herd bajo carga real. |
| **E-0.2-007** | P2 | `apps/llm_workers/rate_limiter.py::QuotaManager` → `_persist_bucket_state()` (L153), `_restore_bucket_state()` (L130), `infra/resilience/sqlite_rate_limit_store.py::SQLiteRateLimitStore` → `INSERT ... ON CONFLICT DO UPDATE` (L54-58) | **Rate limiter con persistencia funcional observada.** QuotaManager mantiene TokenBucket en memoria pero implementa hooks de persistencia/restauración conectados a SQLiteRateLimitStore. El patrón UPSERT proporciona idempotencia. |
| **E-0.2-008** | P2 | `apps/llm_workers/cache_provider.py::CachedLLMProvider` → `async with aiosqlite.connect(self._db_path)` (L30, L47, L68), `self._locks` (L128) | **Cache LLM con persistencia y lock por clave observada.** CachedLLMProvider usa aiosqlite para persistencia y mantiene locks asyncio por `prompt_hash` para prevenir thundering herd en cache misses. Autoridad de cache preexistente (DC-04: LLM Cache 🟡). |
| **E-0.2-009** | P2 | `runtime/sweeper.py::RecoveryDaemon.run_sweep_cycle` → `conn_fsm.execute("PRAGMA busy_timeout=15000")` (L51), `_force_wal_checkpoint()` (L25) | **Sweeper con conciencia de durabilidad observada.** Fuerza `busy_timeout=15000` y ejecuta `wal_checkpoint` en cada ciclo. Demuestra gestión proactiva de la durabilidad de SQLite. |

### Evidencia E-0.2-006: Circuit Breaker in-memory sin persistencia

* **Archivo Fuente Primario:** `core/resilience/circuit_breaker.py`
* **Símbolo Auditado:** `GlobalCircuitBreaker`
* **Declaración Observada:**

```python
class GlobalCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, window_sec: float = 60.0, recovery_timeout: float = 30.0):
        self.state = CircuitState.CLOSED          # L19: in-memory
        self._lock = asyncio.Lock()               # L29: asyncio lock
        self.failure_timestamps = deque()          # in-memory
```

* **Observed:** El estado del CB (`CLOSED`, `OPEN`, `HALF_OPEN`), las métricas de fallos (`failure_timestamps`) y el lock (`asyncio.Lock()`) viven exclusivamente en memoria. `CircuitBreakerRegistry` mantiene un `Dict[str, GlobalCircuitBreaker]` como singleton de clase (L120). No hay ningún hook de persistencia ni store asociado.
* **Required:** C4 (Recovery) exige que el sistema pueda recuperarse de un crash sin pérdida de estado crítico. En un entorno de 16GB RAM, un OOM es un escenario real. C10 (Resource Efficiency) exige que la recuperación no agrave la presión de recursos.
* **Decision:** DF-24 (`CircuitBreakerStore` persistente) fue diferido a Fase 18 "solo si se demuestra necesidad multi-proceso". Este HITO demuestra pérdida de estado ante crash, pero **no demuestra automáticamente necesidad de persistencia multi-proceso**. DF-24 se reabre bajo DC-01/DC-08.
* **Hallazgo Forense:** **FACT:** El estado del CB no sobrevive al crash del proceso. **INFERENCE:** Esto podría eliminar el conocimiento de un estado OPEN previamente establecido. **RISK:** Podría permitir una recuperación concurrente agresiva. **NO DEMOSTRADO:** Que produzca efectivamente un thundering herd bajo carga real.
* **Consecuencia Arquitectónica:** DC-01 y DC-08 deben considerar la persistencia del estado del CB como parte del modelo de durabilidad del execution plane. DF-24 se reabre bajo DC-01/DC-08.
* **Estado:** OPEN (DF-24 reabierto)

---

## 12. MATRIZ DE TRIAJE

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `ControlPlaneRepository` | RETAIN | Leases con `BEGIN IMMEDIATE` y optimistic locking. Semántica completa de admisión. E-0.2-001. |
| `EventPlaneRepository` | RETAIN | WAL atómico. El gap de coordinación transaccional es del caso de uso, no del repositorio. E-0.2-003. |
| `MaterializedPlaneRepository` | RETAIN | Proyecciones con versionado. Sin hallazgos negativos. |
| `SystemPlaneRepository` | RETAIN | Leadership con epoch. Sin puerto abstracto pero funcional. E-0.2-002. |
| `FSMRepository` + `DocumentState` | RETAIN | Tabla de transiciones completa (10 estados, transiciones explícitas). E-0.2-009. |
| `ReconcilerDaemon` | RETAIN | Fencing epoch, anti-entropía CQRS, zombie recovery. E-0.2-002. |
| `RecoveryDaemon` | RETAIN | WAL checkpoint, purga de STALLED. E-0.2-009. |
| `QuotaManager` + `SQLiteRateLimitStore` | RETAIN | TokenBucket con persistencia funcional. E-0.2-007. |
| `GlobalCircuitBreaker` | REFACTOR | Estado in-memory sin persistencia. Requiere evaluación bajo DC-01/DC-08. E-0.2-006. |
| `CachedLLMProvider` | RETAIN | Cache con aiosqlite y locks por clave. Autoridad preexistente para DC-04. E-0.2-008. |
| `InMemoryProfileStore` | REFACTOR | `dict` en memoria. Requiere evaluación de impacto operacional. E-0.2-004. |
| `core/benchmark/runners/*` | RELOCATE | Imports cruzados core→apps violan frontera hexagonal. E-0.2-005. |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.2-01** | ProfileStore no durable: `InMemoryProfileStore` pierde perfiles tras crash; el costo y necesidad para recovery deben cuantificarse. | E-0.2-004 | C4, DF-34 | **Fase 18** | OPEN |
| **GAP-0.2-02** | Circuit Breaker in-memory sin persistencia: crash reinicia todos los CBs a CLOSED; el riesgo de recuperación agresiva debe evaluarse. DF-24 se reabre bajo DC-01/DC-08. | E-0.2-006 | C4, C10, DF-24 | **Fase 18** (DC-01, DC-08) | OPEN |
| **GAP-0.2-03** | Imports cruzados `core/benchmark` → `apps/`: viola frontera hexagonal. | E-0.2-005 | ENGINEERING_PRINCIPLES, DF-06 | **Fase 18** (sinergia con refactor de composición) | OPEN |
| **GAP-0.2-04** | Event Plane: `append_wal` es atómico a nivel de DB, pero no hay evidencia de coordinación transaccional con el efecto externo a nivel de caso de uso (INV-JOURNAL). | E-0.2-003 | INV-JOURNAL | **Fase 18** (DC-01, DC-08) | TO BE VERIFIED |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.2-A | `SQLiteRateLimitStore` puede servir como patrón para persistir el estado del Circuit Breaker. | HYPOTHESIS | E-0.2-007 muestra que el patrón UPSERT en SQLite ya funciona para estado de buckets. Sin embargo, CB puede tener necesidades distintas (ventana temporal, half-open ownership, fencing, clock semantics). | Si se confirma en DC-01/DC-08, reduce el costo de implementar persistencia de CB. |
| H-0.2-B | La coordinación transaccional entre `append_wal` y el efecto externo existe en el Orchestrator pero no es visible desde el repositorio. | NO VERIFICABLE | E-0.2-003 muestra que el repositorio no la posee; la verificación requiere auditar `orchestrator.py` y `dispatcher.py` en profundidad (F0-C). | Si se confirma, GAP-0.2-04 se cierra como RESUELTA. Si se rechaza, se promueve a GAP bloqueante para DC-08. |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-01** | Fork de concurrencia | E-0.2-001, E-0.2-006 | Parcial: control plane sólido; CB sin persistencia | **Fase 18** |
| **DC-03** | Determinismo observable por proveedor | E-0.2-008 | Parcial: cache existe pero determinismo del proveedor no medido | **Fase 18** (F0-A) |
| **DC-04** | Alcance de caches | E-0.2-008 | Implementado: LLM cache con aiosqlite | **Fase 18** |
| **DC-08** | Write-policy SQLite + journal | E-0.2-003, E-0.2-006, E-0.2-009 | Parcial: BEGIN IMMEDIATE en control; sin persistencia de CB | **Fase 18** |

---

## 19. APÉNDICE NO NORMATIVO -- RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Recuperación agresiva post-crash | Crash reinicia todos los CBs a CLOSED. Al reiniciar, todos los workers podrían enviar requests simultáneamente a proveedores LLM, agravando la presión. | Alto (potencial) | E-0.2-006 |
| Recálculo costoso de perfiles | Tras crash, `InMemoryProfileStore` pierde perfiles. El sistema podría verse forzado a re-inferir perfiles de documentos ya procesados. | Medio (potencial) | E-0.2-004 |
| Divergencia journal/estado | Si el proceso crashea entre `append_wal` y la actualización del materialized plane, el journal y el estado materializado podrían divergir. | Alto (potencial) | E-0.2-003 |

---

## 21. CIERRE DEL HITO 0.2

Este HITO confirma que la arquitectura de autoridades del execution plane es sólida y reutilizable, con mecanismos de leasing, fencing, persistencia de cuotas y cache LLM. Se identifican tres gaps P1 (ProfileStore in-memory, Circuit Breaker in-memory, imports cruzados) y un gap TO BE VERIFIED (coordinación transaccional del journal). DF-24 se reabre bajo DC-01/DC-08.

**Estado del HITO:** FROZEN v1.2.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados, todas las evidencias tienen ID estable y severidad, todos los gaps tienen fase destino explícita, todas las hipótesis cerradas (HYPOTHESIS / NO VERIFICABLE), separación estricta FACT/INFERENCE/RISK aplicada, lenguaje evaluativo reemplazado por observable, DF-24 reabierto bajo DC-01/DC-08.
**Verificación de cadena de gobernanza:** Charter F18 FROZEN → HITO_0.1 FROZEN (insumo) → F0-G mandato → este HITO. Cadena verificada.
**Contradicciones con HITOs previos:** Ninguna con HITO_0.1. Los hallazgos son complementarios.
**Decision Candidates generados:** DC-01 (evidencia adicional), DC-04 (evidencia de cache preexistente), DC-08 (evidencia de gaps de durabilidad, DF-24 reabierto).
**Siguiente paso recomendado:** Proceder con HITO_0.3 (F0-F Workload Characterization) y HITO_0.4 (F0-E Scientific Neutrality Contract) para completar la Etapa de Auditoría 1.