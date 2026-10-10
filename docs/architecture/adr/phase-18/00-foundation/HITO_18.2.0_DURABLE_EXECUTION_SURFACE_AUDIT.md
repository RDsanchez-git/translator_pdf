# HITO_18.2.0_DURABLE_EXECUTION_SURFACE_AUDIT.md

**Estado:** FROZEN v1.3.0
**Fecha de emisión original:** 2026-10-09
**Fecha de enmienda v1.1.0:** 2026-10-09
**Fecha de enmienda v1.2.0:** 2026-10-09
**Fecha de enmienda v1.3.0:** 2026-10-09
**Fecha de congelamiento:** 2026-10-09
**Fase:** Fase 18 (Advanced Local Runtime) — Subfase 18.2 (Durable Execution & Recovery)
**Tipo de artefacto:** Forensic Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Supersede:** HITO_18.2.0 v1.2.0 FROZEN, v1.1.0 FROZEN y v1.0.0 FROZEN

**Advertencia epistemológica (obligatoria):** Este HITO es un reporte forense. Las afirmaciones sobre el estado del repositorio, los resultados del chaos harness y el commit de promoción de NADR-F18-02 son reportadas como observaciones, no certificadas independientemente. La verificación independiente corresponde al proceso de gobernanza (Paso -1) y a HITO_18.2.1. El cumplimiento completo de INV-JOURNAL NO está demostrado por este HITO.

**Evidencia Forense Vinculante:**

- ADR_F18_MASTER v1.0.0 FROZEN (§5.1 invariantes — especialmente INV-JOURNAL con cláusula de "ventana de duplicación acotada y medida", §6.2 subfases, §8.2 DC Log, §8.3 Deferred Findings)
- NADR-F18-01 v1.0.3 FROZEN (Execution Identity & Scientific Isolation)
- NADR-F18-02 v1.0.1 FROZEN (Bounded Concurrent Execution, §5.4 R15)
- ADR_F18.1 v1.0.2 FROZEN (Execution Plane & Concurrency)
- F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 FROZEN (DC-02-A)
- FASE_18.1_HANDOFF v1.0.0 (carry-forwards §5.2, prerequisites §6.1)
- HITO_0.8 v1.4.0 (State Durability & Recovery Map — evidencia heredada)
- METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 FROZEN (estructura canónica)
- METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES v1.3.0 FROZEN (jerarquía de gobernanza)
- ENGINEERING_PRINCIPLES (YAGNI §I, Hexagonal §II, Reuse Before Invent §VII)

**Código auditado:** apps/llm_workers/__main__.py, infra/db/control_repo.py, infra/db/event_repo.py, infra/db/materialized_repo.py, infra/db/system_repo.py, infra/db/fsm_repository.py, infra/db/schema_queue.sql, infra/db/profile_store.py, core/resilience/circuit_breaker.py, core/telemetry/gateway.py, core/document_profile/profiler.py, core/document_profile/models.py, runtime/recovery.py, runtime/sweeper.py, runtime/resumer.py, apps/daemons/reconciler.py, core/execution/handlers.py, core/execution/state.py, core/execution/coordination.py, core/execution/shutdown.py, core/execution/cancellation.py, core/execution/admission.py, core/execution/backpressure.py, apps/daemons/chaos_runner.py, tests/integration/test_recovery_flow.py, infra/db/bootstrap.py, infra/db/connection.py, apps/bootstrap/provider_stack_factory.py

**Mandato:** Auditar el surface durable existente del execution plane post-18.1 para determinar qué activos existen, qué garantías proporcionan realmente, qué gaps quedan frente a INV-JOURNAL y los requisitos de ADR_F18_MASTER §6.2, y qué activos pueden reutilizarse sin reinvención.

**Síntesis:** La maquinaria de recovery existente es sustancialmente más completa de lo documentado (6 daemons/handlers, fencing SQL activo, reconciler con 2 vectores, chaos harness funcional). El task lease (UPDATE a PROCESSING con lease_owner, lease_expires_at, execution_id de intento) constituye una intención durable previa al efecto externo. Ni la violación estructural de INV-JOURNAL ni su cumplimiento completo están demostrados: la ventana execute→append_wal existe (OBSERVADO), la acotación temporal no está demostrada, la medición de frecuencia de duplicación no está demostrada. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". ProfileStore y CircuitBreaker son in-memory; clasificación final requiere cuantificación (HITO_18.2.1). Convergencia de recovery y cobertura de fencing NO demostradas empíricamente. Write-policy synchronous=NORMAL suficiente para crash de proceso; durabilidad ante power loss no demostrada.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-09 | Emisión inicial. Auditoría forense del surface durable post-18.1. |
| 1.0.0-FROZEN | 2026-10-09 | Cierre formal inicial. |
| 1.1.0-FROZEN | 2026-10-09 | Versión sucesora. Correcciones tras revisión arquitectónica y re-verificación forense del task lease: GAP-18.2.0-01 reclasificado de P0 a P1; hipótesis H-18.2.0-A reformulada; inconsistencias internas DOC-01 a DOC-06 corregidas; separación de niveles epistemológicos; fechas cronológicas corregidas; cobertura declarada con precisión. |
| 1.2.0-FROZEN | 2026-10-09 | Versión superadora que incorpora lo mejor de la revisión externa manteniendo la clasificación de severidad correcta: (1) Incorporación explícita de la cláusula de "ventana de duplicación acotada y medida" del ADR Maestro como fundamento de la clasificación P1. (2) Adición de Matriz Observed/Required/Decision (§7). (3) Adopción de niveles epistemológicos OBSERVADO/DEMOSTRADO/GARANTIZADO. (4) Distinción prominente "efecto no iniciado" vs "efecto iniciado pero no registrado". (5) _process_task reclasificado de REFACTOR a TO BE VERIFIED. (6) Gap de power loss/write-policy mantenido. |
| 1.3.0-FROZEN | 2026-10-09 | Enmienda metodológica con 8 correcciones (C1-C8): (C1) Conclusión refinada: ni violación ni cumplimiento completo de INV-JOURNAL demostrados. (C2) Distinción explícita entre execution_id del contrato de identidad (hash determinista, F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2) y execution_id del intento (generado por pick_task). (C3) Idempotencia limitada a cada operación concreta observada; propiedad integral NO DEMOSTRADA. (C4) Estimación ~1-10ms clasificada como HIPÓTESIS no validada. (C5) Fencing reformulado: "no se identificó cobertura empírica suficiente en el alcance examinado". (C6) Mecanismos 18.1: "no modificar semántica ni contratos sin decisión y trazabilidad correspondientes". (C7) synchronous=NORMAL: separación de consistencia, durabilidad ante crash de proceso y durabilidad ante pérdida de energía. (C8) DF-24 subsumido en DC-08 (confirmado por ADR Maestro §8.3); DF-34 con trigger propio independiente. Precisión adicional: justificación de severidad P1 reformulada. |

---

## 1. RESUMEN EJECUTIVO

Se auditó el surface durable del execution plane local post-Subfase 18.1. La auditoría cubrió 10 superficies principales y verificó los contratos de ADR_F18_MASTER §5.1 (INV-JOURNAL, INV-SCI-1, INV-OPS-1, INV-UNITS, INV-VERIFICATION-ISOLATION), NADR-F18-02 §5.4 R15 (shutdown sin recovery) y ENGINEERING_PRINCIPLES §VII (Reuse Before Invent).

**Hallazgo central:**

> El execution plane posee una maquinaria de recovery funcional y sustancialmente más completa de lo que la documentación de fase sugiere (6 daemons/handlers, epoch fencing activo a nivel SQL, reconciler con 2 vectores de recuperación, chaos harness con game_day_1). El task lease persistido por `pick_task()` (task_state=PROCESSING, lease_owner, lease_expires_at, execution_id de intento) constituye una intención durable previa al efecto externo. **Ni la violación estructural de INV-JOURNAL ni su cumplimiento completo están demostrados.** La ventana execute→append_wal existe (OBSERVADO). La acotación temporal de la ventana NO está demostrada (la estimación ~1-10ms es HIPÓTESIS no validada). La medición de la frecuencia de duplicación NO está demostrada. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". La resolución requiere evidencia adicional (HITO_18.2.1).

**Defectos dominantes confirmados:**

1. **Gap de medición de la ventana de duplicación (E-18.2.0-004, P1):** El cumplimiento completo de INV-JOURNAL no está demostrado. La ventana execute→append_wal existe (OBSERVADO). La acotación temporal no está demostrada (HIPÓTESIS ~1-10ms). La medición de frecuencia de duplicación no está demostrada. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". Esto es un gap que requiere evidencia adicional (HITO_18.2.1), no una violación confirmada ni un cumplimiento certificado.

2. **ProfileStore completamente in-memory (E-18.2.0-001, P2):** `InMemoryProfileStore` pierde todo el estado en restart. Clasificación final pendiente de cuantificación de coste de re-inferencia (trigger DF-34 → HITO_18.2.1). DF-34 tiene trigger propio independiente (no subsumido en DC-08).

3. **CircuitBreaker completamente in-memory (E-18.2.0-002, P2):** `GlobalCircuitBreaker` pierde estado en restart. Clasificación final pendiente de evaluación de impacto (trigger DF-24 → HITO_18.2.1). DF-24 está explícitamente subsumido en DC-08 (ADR_F18_MASTER §8.3).

4. **Cobertura de tests de fencing (E-18.2.0-010, P1):** `tests/test_fencing.py` no existe. Fencing OBSERVADO a nivel de API y SQL. No se identificó cobertura empírica suficiente en el alcance examinado.

5. **Write-policy synchronous=NORMAL (E-18.2.0-009, P2):** Suficiente para durabilidad ante crash de proceso. Durabilidad ante pérdida de energía NO demostrada. Requiere decisión DC-08.

**Veredicto:** La Subfase 18.2 debe partir de la maquinaria existente (Reuse Before Invent). Los gaps identificados son candidatos de alcance para 18.2; su inclusión final y mecanismo de resolución deben reconciliarse con el ADR Master, las decisiones vigentes y la evidencia de HITO_18.2.1. Este HITO no certifica suficiencia de recovery ni cumplimiento completo de INV-JOURNAL; certifica existencia de activos reutilizables sustanciales y gaps que requieren evidencia adicional. Ningún gap es P0: no hay violación estructural de invariante constitucional demostrada.

**Estado de preparación para el siguiente documento:** HITO_18.2.0 v1.3.0 FROZEN. HITO_18.2.1 pendiente con contrato preciso de medición de propiedades (ventana temporal, frecuencia de duplicación, recuperación, coste FinOps, fencing, convergencia). ADR_F18.2 bloqueado hasta cierre de HITO_18.2.1.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

**Separación estricta de niveles epistemológicos:**

Este HITO distingue tres niveles que NO deben mezclarse:

| Nivel | Definición | Aplicación en este HITO |
|---|---|---|
| **OBSERVADO** | Lo que el código realmente hace hoy (inspección directa) | Fencing SQL existe; lease se escribe antes del efecto; WAL se escribe después del efecto; idempotencia de comandos |
| **DEMOSTRADO** | Lo que funciona correctamente bajo fallo verificado (tests, chaos harness) | Recovery de documentos STALLED (test_recovery_flow.py verde) |
| **GARANTIZADO** | Lo que funciona correctamente bajo todos los escenarios relevantes | Convergencia global de recovery (NO DEMOSTRADO); cobertura de fencing (NO DEMOSTRADO) |

Adicionalmente, este HITO distingue cuatro categorías de estado para cada hallazgo:

- **FACT:** Lo que el código hace observably (inspección directa).
- **INFERENCE:** Lo que puede deducirse razonablemente del código, pero no está demostrado bajo fallo.
- **HIPÓTESIS:** Estimación no validada que requiere medición o experimento.
- **NO DEMOSTRADO:** Lo que requiere validación empírica, ejecución o evidencia adicional.
- **DECISION PENDING:** Lo que requiere decisión arquitectónica o de Board.

Específicamente, este HITO:

- **Puede** afirmar qué código existe y qué hace (OBSERVADO).
- **Puede** afirmar qué exige la arquitectura vigente (Required).
- **Puede** afirmar qué decidió una fase previa (Decision).
- **No puede** certificar que un mecanismo funciona bajo todos los escenarios de fallo (requiere validación empírica).
- **No puede** cuantificar costes FinOps (requiere ejecución empírica → HITO_18.2.1).
- **No puede** medir la acotación temporal de la ventana de duplicación (requiere experimento → HITO_18.2.1).
- **No puede** medir la frecuencia de duplicación (requiere escenarios de fallo controlados → HITO_18.2.1).
- **No puede** decidir mecanismos de resolución de gaps (requiere ADR/NADR).
- **No puede** aceptar unilateralmente una limitación que contradiga un invariante congelado (requiere Board).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (ADR_F18_MASTER, NADR-F18-01, NADR-F18-02, ADR_F18.1, F18_IDENTITY_BOUNDARY_CONTRACT, ENGINEERING_PRINCIPLES, METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES).
2. Cargar HITOs previos aplicables (HITO_0.8 v1.4.0 como evidencia heredada).
3. Cargar handoff de fase previa (FASE_18.1_HANDOFF v1.0.0).
4. Inspeccionar código fuente mediante comandos PowerShell read-only.
5. Separar Observed / Required / Decision para cada hallazgo.
6. Registrar evidencia estable con IDs normalizados (E-18.2.0-XXX).
7. Consolidar gaps solo cuando exista discrepancia demostrada contra contrato vigente.
8. Declarar NO DEMOSTRADO cuando la evidencia sea insuficiente.
9. Clasificar como HIPÓTESIS las estimaciones no validadas.
10. Derivar Decision Candidates solo si la evidencia los exige.
11. Verificar estado del repositorio (git status, tests, pyright, import-linter) como sanity check.

---

## 3. ALCANCE AUDITADO

**Nota metodológica sobre cobertura:** La tabla siguiente declara el estado real de cada superficie. "100% auditado" significa inspección directa del código fuente en este HITO. "Referenciado" significa usado por evidencia previa sin re-auditoría. "No verificable" significa que requiere runtime, disco o ejecución no disponible en auditoría read-only.

| Superficie | Módulos | Estado real |
|---|---|---|
| ProfileStore | core/document_profile/ports.py, infra/db/profile_store.py | 100% auditado |
| CircuitBreaker | core/resilience/circuit_breaker.py, infra/resilience/sqlite_rate_limit_store.py | 100% auditado |
| Ventana post-effect/pre-journal | apps/llm_workers/__main__.py, apps/llm_workers/sync_bridge.py, infra/db/control_repo.py, infra/db/event_repo.py | 100% auditado |
| Telemetría | core/telemetry/gateway.py | 100% auditado |
| Fencing/Epochs/Leases | infra/db/system_repo.py, infra/db/control_repo.py, core/execution/handlers.py, infra/db/schema_queue.sql | 100% auditado |
| Recovery machinery | runtime/recovery.py, runtime/sweeper.py, runtime/resumer.py, apps/daemons/reconciler.py, core/execution/handlers.py, core/execution/state.py | 100% auditado |
| Chaos harness | apps/daemons/chaos_runner.py, tests/integration/test_recovery_flow.py, tests/test_fencing.py | Auditado (test_fencing.py confirmado inexistente) |
| Mecanismos 18.1 | core/execution/coordination.py, shutdown.py, cancellation.py, admission.py, backpressure.py + implementaciones runtime | 100% auditado |
| SQLite write-policy | infra/db/bootstrap.py, infra/db/connection.py | 100% auditado |
| Schema chunk_tasks | infra/db/schema_queue.sql | 100% auditado |
| Estado del repositorio | git status, pytest, pyright, import-linter | 100% auditado |
| core/telemetry/regression_gateway.py | Referenciado en handoff 18.1 | No verificable: archivo .py eliminado, .pyc huérfano presente |
| HITO_0.8 v1.4.0 | Evidencia heredada de durabilidad y recovery | Referenciado, no re-auditado |
| Convergencia de recovery bajo fallo | Comportamiento runtime del reconciler/watchdog | NO DEMOSTRADO (requiere ejecución de chaos harness) |
| Cobertura empírica de fencing | Comportamiento bajo worker obsoleto | NO DEMOSTRADO (no se identificó cobertura suficiente en el alcance examinado) |
| Acotación temporal de ventana de duplicación | Intervalo real entre execute() y append_wal() | HIPÓTESIS no validada (requiere medición → HITO_18.2.1) |
| Frecuencia de duplicación | Tasa de efectos externos repetidos tras crash | NO DEMOSTRADO (requiere escenarios de fallo controlados → HITO_18.2.1) |

**Nota sobre regresión SMOKE:** El corpus canónico produce scientific_verdict=HARD_FAIL (exit_code=2). Esta es una condición legítima y pre-existente documentada en HITO_0.7 v1.1.0 (FASE_6_HANDOFF §2.2, DF-10 de 17-BIS). No es regresión de 18.1 ni bug del execution plane. Este HITO la registra como condición de contexto, no como gap.

**Nota sobre baseline de tests:** 854 tests collected, pyright 0 errors, 0 warnings. Import-linter: 4 contratos KEPT / 0 BROKEN. Rama: fase18_subfase02_gate00. Este baseline no debe degradarse.

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Clasificación | Uso en el HITO |
|---|---|---|---|
| ADR Maestro | docs/architecture/adr/phase-18/ADR/ADR_F18_MASTER.md v1.0.0 FROZEN | Normativa | Invariantes §5.1 (especialmente INV-JOURNAL con cláusula de ventana de duplicación acotada y medida), subfases §6, DC Log §8.2, Deferred Findings §8.3 |
| NADR | docs/architecture/adr/phase-18/NADR/NADR-F18-01.md v1.0.3 FROZEN | Normativa | Frontera de identidad, scientific neutrality |
| NADR | docs/architecture/adr/phase-18/NADR/NADR-F18-02.md v1.0.1 FROZEN | Normativa | Bounded execution, shutdown §5.4 R15, recovery excluido |
| ADR de Fase | docs/architecture/adr/phase-18/ADR/ADR_F18_1.md v1.0.2 FROZEN | Normativa | DC-13 eliminado del registro canónico (changelog v1.0.1) |
| Contrato | docs/architecture/adr/phase-18/reports/F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.2 FROZEN | Normativa | execution_id = hash(baseline+subject+config+parameter+profile); distingue identidad de ejecución de identidad de intento |
| Handoff | docs/architecture/adr/phase-18/handoff/FASE_18.1_HANDOFF.md v1.0.0 | Histórica | Carry-forwards §5.2, prerequisites §6.1 |
| HITO previo | HITO_0.8 v1.4.0 | Forense heredada | Gaps históricos GAP-0.2-04, GAP-0.8-01, GAP-0.9-02, DC-13 |
| Metodología | docs/architecture/METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 FROZEN | Normativa | Estructura canónica de este HITO |
| Metodología | docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0 FROZEN | Normativa | Jerarquía de gobernanza, flujo de trabajo |
| Principios | docs/architecture/ENGINEERING_PRINCIPLES.md | Normativa | YAGNI §I, Hexagonal §II, Reuse Before Invent §VII |
| Código | apps/llm_workers/__main__.py | Runtime | Worker LLM, flujo _process_task, task lease heartbeat |
| Código | infra/db/control_repo.py | Runtime | pick_task (lease), acknowledge, abandon, mark_zombie_recovered |
| Código | infra/db/event_repo.py | Runtime | append_wal, get_replay, get_latest_event |
| Código | infra/db/materialized_repo.py | Runtime | upsert_projection idempotente |
| Código | infra/db/system_repo.py | Runtime | Leadership/epoch fencing |
| Código | infra/db/fsm_repository.py | Runtime | FSM transitions, find_stalled_documents |
| Schema | infra/db/schema_queue.sql | Schema | Tabla chunk_tasks con columnas de lease, system_leases |
| Código | infra/db/profile_store.py | Runtime | ProfileStore in-memory |
| Código | core/resilience/circuit_breaker.py | Runtime | CircuitBreaker in-memory |
| Código | core/telemetry/gateway.py | Runtime | Telemetría con buffer in-memory |
| Código | runtime/recovery.py, sweeper.py, resumer.py | Runtime | Recovery daemons |
| Código | apps/daemons/reconciler.py | Runtime | Reconciler con epoch fencing y 2 vectores |
| Código | core/execution/handlers.py | Runtime | Reconciliation command handlers |
| Código | core/execution/state.py | Runtime | FSM con 12 estados |
| Código | apps/daemons/chaos_runner.py | Runtime | Chaos harness |
| Test | tests/integration/test_recovery_flow.py | Verificación | Recovery end-to-end |
| Test | tests/test_fencing.py | Verificación | Confirmado inexistente |
| Código | core/execution/coordination.py, shutdown.py, cancellation.py, admission.py, backpressure.py + runtime/ | Runtime | Mecanismos 18.1 FROZEN |
| Código | infra/db/bootstrap.py, connection.py | Runtime | SQLite pragmas |
| Código | apps/bootstrap/provider_stack_factory.py | Runtime | Composition root del provider stack |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Worker LLM: secuencia crítica de lease, efecto externo y journal

```text
apps/llm_workers/__main__.py::LLMWorkerDaemon (run + _process_task)

  [PREVIO: pick_task() en engine.py / run loop]
    UPDATE chunk_tasks SET task_state='PROCESSING',
       lease_owner=?, lease_expires_at=?, execution_id=?       [OBSERVADO] INTENCIÓN DURABLE
       (execution_id de intento: exec_{timestamp}_{uuid})
    BEGIN IMMEDIATE ... RETURNING ... commit                    [OBSERVADO]

  -> _process_task(task)
      -> Checkpoint 1: raise_if_cancelled()                     [OBSERVADO]
      -> ast_registry.get_node()                                [OBSERVADO]
      -> materialized.get_projection_status()                   [OBSERVADO] early exit si CURRENT
      -> event.get_replay()                                     [OBSERVADO] replay económico si existe
      -> [si no hay replay]
          -> TaskLeaseHeartbeat.__enter__()                     [OBSERVADO] renovación periódica de lease
          -> Checkpoint 2: raise_if_cancelled()                 [OBSERVADO]
          -> processor.execute(node)                            [OBSERVADO] EFECTO EXTERNO (LLM call)
          -> heartbeat.lease_lost check                         [OBSERVADO]
          -> event.append_wal(...)                              [OBSERVADO] journal post-effecto
          -> Checkpoint 3: raise_if_cancelled()                 [OBSERVADO]
      -> TextNormalizer.normalize()                             [OBSERVADO]
      -> materialized.upsert_projection()                       [OBSERVADO] idempotente
      -> control.mark_task_completed()                          [OBSERVADO] acknowledge con CAS

Leyenda:
  [OBSERVADO]   código verificado presente
  [DEMOSTRADO]  verificado bajo fallo en tests
  [GARANTIZADO] verificado bajo todos los escenarios

GAP OBSERVADO (E-18.2.0-004, P1):
  Entre processor.execute() (efecto externo) y event.append_wal() (journal)
  existe una ventana. El lease (pick_task) es intención durable previa al efecto.
  La ventana existe (OBSERVADO). La acotación temporal NO está demostrada
  (estimación ~1-10ms es HIPÓTESIS no validada). La medición de frecuencia
  de duplicación NO está demostrada. El reconciler no distingue "efecto no
  iniciado" de "efecto iniciado pero no registrado".
```

### FLUJO B — Recovery: detección y reconciliación de zombies

```text
apps/daemons/reconciler.py::ReconcilerDaemon._sweep_tasks()

  SELECT task_id, document_id, node_id FROM chunk_tasks
  WHERE task_state = 'PROCESSING' AND lease_expires_at < now    [OBSERVADO]

  Para cada zombie:
    latest_event = event_repo.get_latest_event(node_id)         [OBSERVADO]

    SI latest_event.lifecycle == "GENERATED":
      -> RematerializeTaskCommand                               [OBSERVADO] Vector 2: CQRS desync
      (efecto ocurrió, WAL existe, rematerializar proyección)
    SINO:
      -> RecoverZombieTaskCommand                               [OBSERVADO] Vector 1: zombie puro
      (devolver a PENDING, re-ejecutar)
      [GAP] Vector 1 no distingue "efecto no iniciado" de
            "efecto iniciado pero no registrado"

core/execution/handlers.py::ReconciliationCommandHandler
  -> handle_rematerialize()
      -> get_current_epoch() vs cmd.reconciler_epoch            [OBSERVADO] fencing activo
      -> mat.upsert_projection()                                [OBSERVADO] rematerialización
      -> task.mark_cqrs_reconciled()                            [OBSERVADO] idempotencia
  -> handle_recover_zombie()
      -> get_current_epoch() vs cmd.reconciler_epoch            [OBSERVADO] fencing activo
      -> task.mark_zombie_recovered()                           [OBSERVADO] idempotencia

Leyenda:
  [OBSERVADO]   código verificado presente
  [DEMOSTRADO]  verificado bajo fallo en tests
  [GARANTIZADO] verificado bajo todos los escenarios

Veredicto: La maquinaria de recovery es funcional a nivel de API (OBSERVADO).
La suficiencia contractual y la convergencia bajo los escenarios de fallo
pertinentes permanecen NO DEMOSTRADAS (requiere chaos harness).
```

### FLUJO C — Fencing y ownership

```text
infra/db/system_repo.py::SystemPlaneRepository
  -> acquire_leadership()                                       [OBSERVADO] retorna lease_version como epoch
  -> renew_leadership()                                         [OBSERVADO] WHERE owner_id AND lease_expires_at >= now
  -> get_current_epoch()                                        [OBSERVADO] lectura de lease_version

infra/db/control_repo.py::ControlPlaneRepository
  -> pick_task()                                                [OBSERVADO] BEGIN IMMEDIATE + UPDATE RETURNING
  -> acknowledge_execution()                                    [OBSERVADO] WHERE lease_owner AND lease_expires_at >= now
  -> abandon_execution()                                        [OBSERVADO] WHERE lease_owner AND lease_expires_at >= now
  -> renew_task_lease()                                         [OBSERVADO] WHERE lease_owner AND task_state = PROCESSING
  -> mark_zombie_recovered()                                    [OBSERVADO] idempotencia vía processed_reconciliation_commands

core/execution/handlers.py::ReconciliationCommandHandler
  -> epoch verification: cmd.reconciler_epoch != current_epoch -> DROP  [OBSERVADO]

Leyenda:
  [OBSERVADO]   fencing observado a nivel SQL y API

Veredicto: Fencing OBSERVADO a nivel de API y SQL. No se identificó cobertura
empírica suficiente en el alcance examinado: tests/test_fencing.py no existe.
```

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| ProfileStore (puerto) | core/document_profile/ports.py::ProfileStore | Sí (DF-34) | Persistencia temporal de perfiles documentales | OBSERVADO |
| ProfileStore (implementación) | infra/db/profile_store.py::InMemoryProfileStore | Sí (DF-34) | dict in-memory, sin persistencia | OBSERVADO |
| CircuitBreaker | core/resilience/circuit_breaker.py::GlobalCircuitBreaker | Sí (DF-24) | Estado in-memory CLOSED/OPEN/HALF_OPEN | OBSERVADO |
| CircuitBreakerRegistry | core/resilience/circuit_breaker.py::CircuitBreakerRegistry | Parcial | Dict in-memory; existe pero no usado en producción | OBSERVADO |
| SQLiteRateLimitStore | infra/resilience/sqlite_rate_limit_store.py | No (precedente) | Persistencia de cuotas en SQLite WAL | OBSERVADO |
| SQLiteTelemetryGateway | core/telemetry/gateway.py | Sí (GAP-0.9-02) | Buffer asyncio.Queue + flush batch a SQLite | OBSERVADO |
| TaskLease (intención durable) | infra/db/control_repo.py::pick_task + schema chunk_tasks | Sí (INV-JOURNAL) | task_state=PROCESSING + lease_owner + execution_id de intento + lease_expires_at | OBSERVADO |
| execution_id de intento | infra/db/control_repo.py::pick_task → exec_{timestamp}_{uuid} | Sí (INV-JOURNAL) | Identifica un intento específico de ejecución; NO es el execution_id del contrato de identidad | OBSERVADO |
| TaskLeaseHeartbeat | apps/llm_workers/__main__.py::TaskLeaseHeartbeat | Sí (INV-JOURNAL) | Daemon thread de renovación de lease | OBSERVADO |
| SystemPlaneRepository | infra/db/system_repo.py | Sí (fencing) | Leadership + epoch via lease_version | OBSERVADO |
| ControlPlaneRepository | infra/db/control_repo.py | Sí (fencing) | Task leases + optimistic locking | OBSERVADO |
| EventPlaneRepository | infra/db/event_repo.py | Sí (journal) | append_wal idempotente, get_replay, get_latest_event | OBSERVADO |
| MaterializedPlaneRepository | infra/db/materialized_repo.py | Sí (projection) | upsert_projection idempotente con version check | OBSERVADO |
| AbandonedProcessWatchdog | runtime/recovery.py | Sí (recovery) | Detecta docs estancados > 3600s → STALLED | OBSERVADO |
| RecoveryDaemon (sweeper) | runtime/sweeper.py | Sí (recovery) | WAL checkpoint + purga STALLED > 1h | OBSERVADO |
| OnDemandResumeManager | runtime/resumer.py | Sí (recovery) | Rescate STALLED → suspended_state | OBSERVADO |
| ReconcilerDaemon | apps/daemons/reconciler.py | Sí (recovery) | Leadership + sweep zombies + FSM stalls | OBSERVADO |
| ReconciliationCommandHandler | core/execution/handlers.py | Sí (recovery) | Rematerialize + RecoverZombie con epoch check | OBSERVADO |
| DocumentCommandHandler | core/execution/handlers.py | Sí (recovery) | Transiciones FSM con CAS | OBSERVADO |
| DocumentState FSM | core/execution/state.py | Sí (recovery) | 12 estados incluyendo STALLED, FAILED_RETRYABLE, FAILED_FATAL | OBSERVADO |
| ChaosInjector | apps/daemons/chaos_runner.py | Sí (validación) | Docker kill + upstream mutation | OBSERVADO |
| SystemObserver | apps/daemons/chaos_runner.py | Sí (validación) | Inyección de carga + métricas de convergencia | OBSERVADO |
| game_day_1_crash_consistency | apps/daemons/chaos_runner.py | Sí (validación) | Kill SIGKILL + convergencia estricta | OBSERVADO |
| Mecanismos 18.1 | coordination.py, shutdown.py, cancellation.py, admission.py, backpressure.py + runtime | Sí (18.1 FROZEN) | Primitivos de ejecución bounded | OBSERVADO |
| test_fencing.py | tests/test_fencing.py | Sí (validación) | No existe | MISSING |
| regression_gateway.py | core/telemetry/regression_gateway.py | Referenciado | .py eliminado, .pyc huérfano (8095 bytes) | NO VERIFICABLE |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Intención durable pre-effecto | Task lease (PROCESSING + execution_id de intento + lease_owner + lease_expires_at) persistido ANTES del efecto externo | INV-JOURNAL (1ª parte): intención/lease/reserva recuperable tras crash | HITO_0.8 identificó GAP-0.2-04 | COMPLIANT | E-18.2.0-004, E-18.2.0-005 |
| Idempotent apply (operaciones concretas) | upsert_projection con version check; append_wal con ON CONFLICT DO NOTHING; reconciliation commands con processed_reconciliation_commands | INV-JOURNAL (2ª parte): aplicación idempotente del resultado | Ninguna | OBSERVADO por operación; propiedad integral NO DEMOSTRADA | E-18.2.0-004, E-18.2.0-006 |
| Ventana de duplicación acotada | Ventana execute→append_wal existe (OBSERVADO). Acotación temporal NO demostrada (~1-10ms es HIPÓTESIS). | INV-JOURNAL (3ª parte): ventana de duplicación acotada | Ninguna | NO DEMOSTRADO (acotación temporal) | E-18.2.0-004 |
| Ventana de duplicación medida | No hay telemetría que cuantifique frecuencia de duplicación ni verifique acotación | INV-JOURNAL (3ª parte): ventana de duplicación medida | Ninguna | NO DEMOSTRADO | E-18.2.0-004 |
| Distinción "efecto no iniciado" vs "efecto iniciado pero no registrado" | Reconciler Vector 1 trata ambos casos igual (devolver a PENDING) | Resolución segura de resultado ambiguo | Ninguna | NO DEMOSTRADO (gap de granularidad) | E-18.2.0-004 |
| ProfileStore persistencia | InMemoryProfileStore con dict | DF-34: cuantificar coste de re-inferencia | Ninguna | NO DEMOSTRADO (trigger no ejecutado) | E-18.2.0-001 |
| CircuitBreaker persistencia | GlobalCircuitBreaker con deque + CircuitState | DF-24: evaluar impacto de perder estado | Ninguna | NO DEMOSTRADO (trigger no ejecutado) | E-18.2.0-002 |
| Telemetría durabilidad | asyncio.Queue + batch de 50 | GAP-0.9-02: operacional vs durable | HITO_0.8 | DECISION REQUIRED (operational state candidato) | E-18.2.0-003 |
| Fencing empírico | SQL-level fencing + epoch verification | Validación de garantías | HITO_18.2.0 v1.0.0 | NO DEMOSTRADO (no se identificó cobertura suficiente en el alcance examinado) | E-18.2.0-005, E-18.2.0-010 |
| Convergencia de recovery | Maquinaria funcional a nivel API | Validación empírica | HITO_18.2.0 v1.0.0 | NO DEMOSTRADO | E-18.2.0-007, E-18.2.0-008 |
| Write-policy SQLite (crash de proceso) | WAL + NORMAL + busy_timeout=30s | DC-08: formalización | Ninguna | OBSERVADO (suficiente para crash de proceso) | E-18.2.0-009 |
| Write-policy SQLite (power loss) | synchronous=NORMAL no garantiza flush a disco | DC-08: formalización | Ninguna | NO DEMOSTRADO (power loss) | E-18.2.0-009 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación/viola invariante, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| E-18.2.0-001 | P2 | infra/db/profile_store.py::InMemoryProfileStore → self._store: dict[str, InferredDocumentProfile] = {} | ProfileStore completamente in-memory. FACT: el estado no sobrevive al reinicio. NO DEMOSTRADO: coste real de re-inferencia. DECISION PENDING: persistir, reconstruir o aceptar (trigger DF-34 → HITO_18.2.1). DF-34 tiene trigger propio independiente (no subsumido en DC-08). |
| E-18.2.0-002 | P2 | core/resilience/circuit_breaker.py::GlobalCircuitBreaker → self.failure_timestamps = deque(), self.state = CircuitState.CLOSED | CircuitBreaker completamente in-memory. FACT: el estado no sobrevive al reinicio. INFERENCE: posible tormenta de reintentos si provider caído. NO DEMOSTRADO: frecuencia e impacto económico real. DECISION PENDING (trigger DF-24 → HITO_18.2.1). DF-24 está subsumido en DC-08 (ADR_F18_MASTER §8.3). |
| E-18.2.0-003 | P2 | core/telemetry/gateway.py::SQLiteTelemetryGateway → self._queue: asyncio.Queue, batch de 50 | Telemetría con buffer in-memory. FACT: crash entre emit() y _write_batch() pierde eventos en queue. NO DEMOSTRADO: máximo real de pérdida. NO DEMOSTRADO: si la telemetría participa en garantías de recovery. DECISION PENDING (destino F20, pendiente revisión contractual). |
| E-18.2.0-004 | P1 | infra/db/control_repo.py::pick_task → UPDATE chunk_tasks SET task_state='PROCESSING', lease_owner, lease_expires_at, execution_id de intento; apps/llm_workers/__main__.py::_process_task → processor.execute(node) seguido de event.append_wal(...); apps/daemons/reconciler.py::_sweep_tasks → Vector 1 (RecoverZombieTaskCommand) cuando WAL no existe | Gap de medición de la ventana de duplicación. FACT: el lease (pick_task) es intención durable previa al efecto. FACT: la ventana execute→append_wal existe (OBSERVADO). HIPÓTESIS no validada: acotación temporal ~1-10ms. NO DEMOSTRADO: medición de frecuencia de duplicación. NO DEMOSTRADO: distinción "efecto no iniciado" vs "efecto iniciado pero no registrado". INV-JOURNAL: ni violación estructural ni cumplimiento completo demostrados. |
| E-18.2.0-005 | P2 | infra/db/system_repo.py::SystemPlaneRepository → acquire_leadership retorna lease_version como epoch; infra/db/control_repo.py::ControlPlaneRepository → acknowledge_execution con WHERE lease_owner AND lease_expires_at >= now | Fencing implementado a nivel SQL. FACT: optimistic locking + epoch verification existen. NO DEMOSTRADO: que un worker obsoleto no pueda producir efectos tras perder autoridad. No se identificó cobertura empírica suficiente en el alcance examinado. |
| E-18.2.0-006 | P2 | core/execution/handlers.py::ReconciliationCommandHandler → if cmd.reconciler_epoch != current_epoch: return; infra/db/control_repo.py → INSERT OR IGNORE INTO processed_reconciliation_commands | Idempotencia de reconciliation OBSERVADA. Epoch verification en handlers. processed_reconciliation_commands previene re-procesamiento de comandos. Nota: idempotencia de reconciliation ≠ idempotencia de efecto externo LLM. Son contratos distintos. |
| E-18.2.0-007 | P2 | runtime/recovery.py, runtime/sweeper.py, runtime/resumer.py, apps/daemons/reconciler.py, core/execution/handlers.py | Recovery machinery OBSERVADA: 6 componentes. Watchdog, Sweeper, Resumer, Reconciler, ReconciliationCommandHandler, DocumentCommandHandler. FSM con 12 estados. FACT: los mecanismos existen y sus APIs son correctas. NO DEMOSTRADO: convergencia global bajo todos los escenarios de fallo. |
| E-18.2.0-008 | P2 | apps/daemons/chaos_runner.py::game_day_1_crash_consistency | Chaos harness OBSERVADO. FACT: game_day_1 inyecta 5 docs, kill reconciler + worker con SIGKILL, verifica convergencia estricta. NO DEMOSTRADO: cobertura de todos los crash windows relevantes. Resultados de ejecución no auditados en este HITO. |
| E-18.2.0-009 | P2 | infra/db/bootstrap.py → PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA busy_timeout=30000; infra/db/connection.py → mismos pragmas | SQLite write-policy OBSERVADA. FACT: WAL + NORMAL + busy_timeout=30s. Separación de niveles de durabilidad: (1) Consistencia: OBSERVADA (WAL + transacciones). (2) Durabilidad ante crash de proceso: OBSERVADA (synchronous=NORMAL garantiza flush a WAL). (3) Durabilidad ante pérdida de energía: NO DEMOSTRADA (NORMAL no garantiza flush a disco). Nivel requerido y política de escritura quedan a DC-08. |
| E-18.2.0-010 | P1 | tests/test_fencing.py → archivo inexistente | Cobertura de tests de fencing. FACT: fencing OBSERVADO a nivel API/SQL. FACT: tests/test_fencing.py no existe. No se identificó cobertura empírica suficiente en el alcance examinado. El alcance de la búsqueda de cobertura equivalente en otros módulos no está documentado. |
| E-18.2.0-011 | P2 | core/telemetry/__pycache__/regression_gateway.cpython-311.pyc → 8095 bytes; core/telemetry/regression_gateway.py → PathNotFound | Artefacto .pyc huérfano. El archivo .py fue eliminado durante 18.1 (GF-01 resuelto) pero el bytecode no se limpió. Deuda técnica menor. |
| E-18.2.0-012 | P2 | ADR_F18_MASTER §8.2 → DC-13 ausente del DC Log canónico; ADR_F18.1 v1.0.1 changelog → "DC-13 eliminado por no existir en el registro canónico" | DC-13 referencia huérfana. Eliminado del registro canónico en ADR_F18.1 v1.0.1. Referencias residuales en documentos derivados constituyen deuda documental. |
| E-18.2.0-013 | P2 | core/execution/coordination.py::CoordinationPrimitives → frozen=True, stop_event, bridge_ready; core/execution/cancellation.py::CancellationToken → raise_if_cancelled | Mecanismos 18.1 como evidencia formal. CoordinationPrimitives, CancellationToken son FROZEN y funcionales. No modificar semántica ni contratos de 18.1 sin la decisión y trazabilidad correspondientes; los cambios de integración o correcciones necesarias requieren evidencia y aprobación. |

### Evidencia E-18.2.0-004: Gap de medición de la ventana de duplicación (P1)

* **Archivo Fuente Primario:** infra/db/control_repo.py, apps/llm_workers/__main__.py, apps/daemons/reconciler.py
* **Símbolos Auditados:** ControlPlaneRepository.pick_task, LLMWorkerDaemon._process_task, ReconcilerDaemon._sweep_tasks
* **Declaración Observada:**

```python
# pick_task() — INTENCIÓN DURABLE previa al efecto (control_repo.py)
execution_id = f"exec_{int(time.time()*1000):015d}_{uuid.uuid4().hex[:8]}"  # execution_id de INTENTO
UPDATE chunk_tasks
SET task_state = 'PROCESSING', lease_owner = ?, lease_expires_at = ?, execution_id = ?
WHERE task_id = (...)
# BEGIN IMMEDIATE ... RETURNING ... commit

# _process_task() — efecto externo y journal (__main__.py)
raw_response = self.processor.execute(node)   # EFECTO EXTERNO
# ... ventana (HIPÓTESIS: ~1-10ms, no validada) ...
self.event.append_wal(...)                     # JOURNAL

# _sweep_tasks() — reconciliación tras crash (reconciler.py)
latest_event = self.event_repo.get_latest_event(node_id)
if latest_event and latest_event.lifecycle == "GENERATED":
    cmd = RematerializeTaskCommand(...)        # Vector 2
else:
    cmd = RecoverZombieTaskCommand(...)        # Vector 1: zombie puro → PENDING
```

* **Observed:** (FACT) `pick_task()` persiste durablemente task_state=PROCESSING, lease_owner, lease_expires_at y execution_id de intento antes del efecto externo. (FACT) `processor.execute()` ocurre antes de `append_wal()`, con una ventana intermedia. (FACT) `upsert_projection` es idempotente (version check), `append_wal` es idempotente (ON CONFLICT DO NOTHING), reconciliation commands son idempotentes (processed_reconciliation_commands). (FACT) El reconciler, al encontrar una tarea PROCESSING con lease expirado y sin evento GENERATED, la clasifica como "zombie puro" (Vector 1) y la devuelve a PENDING. (FACT) No hay telemetría que cuantifique la frecuencia de duplicación en la ventana execute→append_wal. (HIPÓTESIS no validada) La acotación temporal de la ventana es ~1-10ms.
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "Ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash y una aplicación idempotente del resultado. El mecanismo concreto de persistencia y coordinación permanece abierto a DC-08. **La propiedad obligatoria es: idempotent apply y ventana de duplicación acotada y medida.**"
* **Decision:** HITO_0.8 v1.4.0 identificó este gap como GAP-0.2-04. FASE_18.1_HANDOFF §5.2 lo lista como carry-forward a 18.2. No fue resuelto en 18.1.
* **Hallazgo Forense:** Verificación de las tres propiedades obligatorias de INV-JOURNAL:

| Propiedad obligatoria | Estado | Evidencia |
|---|---|---|
| Intención/lease/reserva recuperable tras crash | OBSERVADO (satisfecha) | pick_task() persiste PROCESSING + lease_owner + execution_id de intento + lease_expires_at ANTES del efecto |
| Idempotent apply (operaciones concretas) | OBSERVADO por operación; propiedad integral NO DEMOSTRADA | upsert_projection (version check), append_wal (ON CONFLICT DO NOTHING), reconciliation commands (processed_reconciliation_commands). Faltan: claves de idempotencia, comportamiento ante resultados diferentes, atomicidad entre WAL/proyección/estado |
| Ventana de duplicación acotada | NO DEMOSTRADO (acotación temporal) | La ventana existe (OBSERVADO). Estimación ~1-10ms es HIPÓTESIS no validada. La ejecución del proveedor, la planificación del proceso y las operaciones intermedias pueden afectar el tiempo transcurrido |
| Ventana de duplicación medida | NO DEMOSTRADO | No hay telemetría que cuantifique frecuencia de duplicación ni verifique acotación. Medir latencia entre execute() y append_wal() no equivale a medir frecuencia de duplicación |

  **Conclusión:** Ni la violación estructural de INV-JOURNAL ni su cumplimiento completo están demostrados. La ventana existe (OBSERVADO). La acotación temporal NO está demostrada. La medición de frecuencia NO está demostrada. La distinción "efecto no iniciado" vs "efecto iniciado pero no registrado" NO está implementada en el reconciler. Esto es un gap que requiere evidencia adicional (HITO_18.2.1), no una violación confirmada ni un cumplimiento certificado.

  **Nota sobre execution_id dual:** Es crucial distinguir dos conceptos:
  - **execution_id del contrato de identidad** (F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2): hash determinista de baseline+subject+config+parameter+profile. Identifica una combinación de entradas. Es el mismo para múltiples intentos con las mismas entradas.
  - **execution_id de intento** (generado por pick_task): `exec_{timestamp}_{uuid}`. Identifica un intento específico de ejecución. Es diferente para cada intento.
  Estos son conceptos distintos y no deben confundirse. El execution_id de intento es el que participa en la intención durable previa al efecto.

* **Consecuencia Arquitectónica:** Duplicación ocasional de trabajo LLM (tokens) en caso de crash dentro de la ventana execute→append_wal, no cuantificada ni medida. Impacto FinOps no acotado. NO es violación confirmada de INV-JOURNAL. NO es cumplimiento certificado de INV-JOURNAL. La resolución (medición de la ventana, y opcionalmente distinción de escenarios) es una decisión arquitectónica que corresponde a DC-08 / ADR_F18.2, no a este HITO.
* **Estado:** OPEN — clasificado como gap de medición/observabilidad P1. Requiere decisión arquitectónica (DC-08) informada por HITO_18.2.1.

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-18.2.0-01 | regression_gateway.cpython-311.pyc huérfano (8095 bytes) en core/telemetry/__pycache__/. El .py fue eliminado durante 18.1 (GF-01 resuelto) pero el bytecode no se limpió. | Bajo | OPEN |
| OBS-18.2.0-02 | DC-13 aparece como carry-forward en FASE_18.1_HANDOFF §5.2 y §8.5 pese a haber sido eliminado del DC Log canónico en ADR_F18.1 v1.0.1. Deuda documental. | Bajo | OPEN |
| OBS-18.2.0-03 | El handoff de 18.1 declaraba NADR-F18-02 como DRAFT; el archivo físico dice FROZEN y existe commit de promoción (ee392e8). Este HITO registra el hecho reportado; la verificación independiente del commit corresponde al proceso de gobernanza (Paso -1). | Bajo | CLOSED (hecho reportado) |
| OBS-18.2.0-04 | La regresión SMOKE produce exit_code=2 (HARD_FAIL basal). Condición legítima y pre-existente del corpus canónico documentada en HITO_0.7 v1.1.0. No es regresión de 18.1 ni gap de 18.2. | Bajo | CLOSED (contexto) |
| OBS-18.2.0-05 | core/execution/handlers.py importa de infra.db.fsm_repository (deuda Fase 17, en ignore_imports de pyproject.toml). No es gap de 18.2. | Bajo | DEFERRED (refactor futuro) |
| OBS-18.2.0-06 | Una prueba de fencing sobre SQLite no demuestra que el proveedor LLM pueda impedir un efecto externo de un worker que perdió su lease. El efecto externo puede producirse antes de que el worker compruebe que perdió autoridad. Esta frontera debe quedar explícita en la matriz de escenarios de HITO_18.2.1. | Medio | OPEN (HITO_18.2.1) |

---

## 12. MATRIZ DE TRIAJE

**Nota metodológica:** La clasificación refleja el estado forense. TO BE VERIFIED indica que la clasificación final RETAIN/REFACTOR depende de evidencia adicional (HITO_18.2.1) o de decisión arquitectónica (DC-08). No se declara REFACTOR prematuramente cuando el trigger de cuantificación no se ha ejecutado o cuando la decisión de DC-08 está pendiente.

| Componente | Clasificación | Justificación forense |
|---|---|---|
| InMemoryProfileStore | TO BE VERIFIED | Trigger DF-34 (cuantificar coste de re-inferencia) no ejecutado. No se puede clasificar RETAIN/REFACTOR sin esa evidencia. DF-34 tiene trigger propio independiente. (E-18.2.0-001) |
| GlobalCircuitBreaker | TO BE VERIFIED | Trigger DF-24 (evaluar impacto de perder estado) no ejecutado. DF-24 está subsumido en DC-08. (E-18.2.0-002) |
| SQLiteTelemetryGateway | TO BE VERIFIED | Buffer in-memory observado. Clasificación ACCEPTED_LIMITATION vs. autoridad durable pendiente de revisión contractual (destino F20). (E-18.2.0-003) |
| LLMWorkerDaemon._process_task | TO BE VERIFIED | Gap de medición P1. Si DC-08 decide cerrar el gap con medición, puede no requerir modificación estructural. Si decide añadir distinción de escenarios, puede requerir modificación. La clasificación depende de la decisión de DC-08. (E-18.2.0-004) |
| SystemPlaneRepository | RETAIN | Fencing OBSERVADO y funcional a nivel API/SQL. Requiere validación empírica (test_fencing.py). (E-18.2.0-005) |
| ControlPlaneRepository (pick_task/lease) | RETAIN | Lease como intención durable, optimistic locking funcionales. (E-18.2.0-004, E-18.2.0-005) |
| EventPlaneRepository (append_wal) | RETAIN | Journal idempotente funcional. (E-18.2.0-004) |
| MaterializedPlaneRepository | RETAIN | Projection idempotente con version check. (E-18.2.0-004) |
| AbandonedProcessWatchdog | RETAIN | Recovery daemon OBSERVADO y funcional a nivel API. Requiere validación empírica de convergencia. (E-18.2.0-007) |
| RecoveryDaemon (sweeper) | RETAIN | WAL checkpoint + purga funcional. Requiere validación empírica. (E-18.2.0-007) |
| OnDemandResumeManager | RETAIN | Rescate de STALLED funcional. Requiere validación empírica. (E-18.2.0-007) |
| ReconcilerDaemon | RETAIN | Reconciler con epoch fencing y 2 vectores funcional. Vector 1 tiene gap de granularidad (no distingue escenarios). Requiere validación empírica. (E-18.2.0-004, E-18.2.0-007) |
| ReconciliationCommandHandler | RETAIN | Handlers con epoch check e idempotencia funcionales. Requiere validación empírica. (E-18.2.0-006) |
| DocumentCommandHandler | RETAIN | Transiciones FSM con CAS funcionales. Requiere validación empírica. (E-18.2.0-007) |
| DocumentState FSM | RETAIN | 12 estados incluyendo STALLED, FAILED_RETRYABLE, FAILED_FATAL. Requiere validación empírica. (E-18.2.0-007) |
| ChaosInjector | RETAIN | Chaos harness OBSERVADO y funcional. Puede requerir ampliación de escenarios en Gate 4. (E-18.2.0-008) |
| SystemObserver | RETAIN | Observabilidad out-of-band funcional. (E-18.2.0-008) |
| game_day_1_crash_consistency | RETAIN | Criterio de validación empírica. (E-18.2.0-008) |
| Mecanismos 18.1 (coordination, shutdown, cancellation, admission, backpressure) | RETAIN | FROZEN. No modificar semántica ni contratos de 18.1 sin la decisión y trazabilidad correspondientes; los cambios de integración o correcciones necesarias requieren evidencia y aprobación. (E-18.2.0-008, E-18.2.0-013) |
| tests/test_fencing.py | MISSING | Archivo inexistente. No se identificó cobertura empírica suficiente en el alcance examinado. Debe crearse en Gate 4. (E-18.2.0-010) |
| regression_gateway.cpython-311.pyc | DEPRECATE | Artefacto huérfano. Debe limpiarse. (E-18.2.0-011) |
| SQLiteRateLimitStore | RETAIN | Precedente de autoridad durable en SQLite. Referencia útil si DF-24/DF-34 deciden persistir. (E-18.2.0-009) |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Journal Semantics (INV-JOURNAL)

| Elemento | Estado | Evidencia |
|---|---|---|
| Intención/lease durable pre-effecto | OBSERVADO | E-18.2.0-004, E-18.2.0-005 |
| Idempotent apply (operaciones concretas) | OBSERVADO por operación | E-18.2.0-004, E-18.2.0-006 |
| Idempotent apply (propiedad integral) | NO DEMOSTRADO | E-18.2.0-004 |
| Ventana de duplicación acotada | NO DEMOSTRADO (acotación temporal) | E-18.2.0-004 |
| Ventana de duplicación medida | NO DEMOSTRADO | E-18.2.0-004 |
| Distinción "efecto no iniciado" vs "efecto iniciado pero no registrado" | NO DEMOSTRADO (gap de granularidad) | E-18.2.0-004 |

**Veredicto del pilar:** Ni la violación estructural de INV-JOURNAL ni su cumplimiento completo están demostrados. La intención durable existe (lease), idempotent apply está OBSERVADO por operación concreta, la ventana de duplicación existe pero su acotación temporal y medición NO están demostradas. La resolución corresponde a HITO_18.2.1 (medición) y DC-08 (decisión).

### Pilar 2 — Autoridades Operacionales (DF-24, DF-34)

| Elemento | Estado | Evidencia |
|---|---|---|
| ProfileStore persistencia | NO DEMOSTRADO (requiere cuantificación) | E-18.2.0-001 |
| CircuitBreaker persistencia | NO DEMOSTRADO (requiere evaluación) | E-18.2.0-002 |
| RateLimitStore persistencia (precedente) | OBSERVADO | E-18.2.0-009 |

**Veredicto del pilar:** FACT: ambas autoridades son in-memory y no sobreviven al reinicio. NO DEMOSTRADO: frecuencia e impacto económico reales. DECISION PENDING: persistir, reconstruir o aceptar, según contrato y evidencia (HITO_18.2.1). DF-24 está subsumido en DC-08 (ADR_F18_MASTER §8.3). DF-34 tiene trigger propio independiente (cuantificación de re-inferencia). No se declara "autoridad durable faltante" como obligación; se separa el hecho observado de la obligación normativa.

### Pilar 3 — Fencing & Ownership

| Elemento | Estado | Evidencia |
|---|---|---|
| Epoch fencing (lease_version) | OBSERVADO (API/SQL) | E-18.2.0-005 |
| Task lease con optimistic locking | OBSERVADO | E-18.2.0-005 |
| Epoch verification en handlers | OBSERVADO | E-18.2.0-006 |
| Seguridad empírica de fencing | NO DEMOSTRADO | E-18.2.0-010 |

**Veredicto del pilar:** Fencing OBSERVADO a nivel de API y SQL. No se identificó cobertura empírica suficiente en el alcance examinado. Requiere creación de test_fencing.py y validación empírica. Nota: una prueba de fencing sobre SQLite no demuestra que el proveedor LLM pueda impedir un efecto externo de un worker que perdió su lease (OBS-18.2.0-06).

### Pilar 4 — Recovery & Reconciliation

| Elemento | Estado | Evidencia |
|---|---|---|
| Detección de zombies (watchdog + reconciler) | OBSERVADO | E-18.2.0-007 |
| Aislamiento de zombies (STALLED state) | OBSERVADO | E-18.2.0-007 |
| Recuperación de zombies (RecoverZombieTaskCommand) | OBSERVADO | E-18.2.0-007 |
| Rematerialización CQRS (RematerializeTaskCommand) | OBSERVADO | E-18.2.0-007 |
| Forward progress (MarkAssemblyReadyCommand) | OBSERVADO | E-18.2.0-007 |
| Idempotencia de reconciliation | OBSERVADO | E-18.2.0-006 |
| Convergencia global de recovery | NO DEMOSTRADO | E-18.2.0-008 |

**Veredicto del pilar:** La maquinaria de recovery existe y es funcional a nivel de API. La suficiencia contractual y la convergencia bajo los escenarios de fallo pertinentes permanecen NO DEMOSTRADAS. Requiere validación con chaos harness ampliado.

### Pilar 5 — Mecanismos 18.1 (Intocables)

| Elemento | Estado | Evidencia |
|---|---|---|
| CoordinationPrimitives | OBSERVADO | E-18.2.0-008, E-18.2.0-013 |
| ShutdownMechanismPort + CoordinatedShutdownMechanism | OBSERVADO | E-18.2.0-008 |
| CancellationToken + TaskOutcome | OBSERVADO | E-18.2.0-008, E-18.2.0-013 |
| AdmissionMechanismPort + SequentialAdmissionMechanism | OBSERVADO | E-18.2.0-008 |
| BackpressureMechanismPort + SequentialBackpressureMechanism | OBSERVADO | E-18.2.0-008 |

**Veredicto del pilar:** COMPLETO. Todos los mecanismos de 18.1 están FROZEN y funcionales. 18.2 no debe modificar semántica ni contratos de 18.1 sin la decisión y trazabilidad correspondientes; los cambios de integración o correcciones necesarias requieren evidencia y aprobación (NADR-F18-02 §5.4 R15).

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| GAP-18.2.0-01 | Gap de medición de la ventana de duplicación: la ventana execute→append_wal existe (OBSERVADO), la acotación temporal NO está demostrada (HIPÓTESIS ~1-10ms), la medición de frecuencia NO está demostrada. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". Ni violación ni cumplimiento completo de INV-JOURNAL demostrados. | E-18.2.0-004 | INV-JOURNAL (medición) / DC-08 | 18.2 (decisión arquitectónica) | OPEN |
| GAP-18.2.0-02 | ProfileStore completamente in-memory. Coste de re-inferencia no cuantificado. DF-34 tiene trigger propio independiente. | E-18.2.0-001 | DF-34 | 18.2 (cuantificación en HITO_18.2.1) | OPEN |
| GAP-18.2.0-03 | CircuitBreaker completamente in-memory. Impacto de perder estado no evaluado. DF-24 está subsumido en DC-08. | E-18.2.0-002 | DF-24 / DC-08 | 18.2 (evaluación en HITO_18.2.1) | OPEN |
| GAP-18.2.0-04 | Telemetría con buffer in-memory. Máximo real de pérdida no demostrado; participación en garantías de recovery no verificada. | E-18.2.0-003 | GAP-0.9-02 | F20 (pendiente revisión contractual) | OPEN |
| GAP-18.2.0-05 | tests/test_fencing.py inexistente. No se identificó cobertura empírica suficiente en el alcance examinado. | E-18.2.0-010 | Validación empírica | 18.2 (Gate 4) | OPEN |
| GAP-18.2.0-06 | SQLite write-policy (WAL+NORMAL+busy_timeout) no formalizada. Durabilidad ante crash de proceso OBSERVADA. Durabilidad ante pérdida de energía NO demostrada. | E-18.2.0-009 | DC-08 | 18.2 (ADR_F18.2) | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-18.2.0-A | "Existen activos de recovery sustanciales reutilizables sin reinvención." | CONFIRMADA | E-18.2.0-005, E-18.2.0-006, E-18.2.0-007 | La hipótesis de reutilización está respaldada por la existencia de activos sustanciales. Su suficiencia para cerrar 18.2 aún debe evaluarse contra los crash windows, las unidades de recuperación y los criterios de aceptación (HITO_18.2.1). |
| H-18.2.0-B | "GAP-0.2-04 constituye una violación estructural de INV-JOURNAL." | RECHAZADA | E-18.2.0-004, ADR_F18_MASTER §5.1 | El task lease es una intención durable previa al efecto, idempotent apply está OBSERVADO por operación concreta. La cláusula del ADR Maestro "La propiedad obligatoria es: idempotent apply y ventana de duplicación acotada y medida" admite la ventana acotada. La violación estructural NO está demostrada. |
| H-18.2.0-B2 | "El cumplimiento completo de INV-JOURNAL está demostrado." | RECHAZADA | E-18.2.0-004 | La acotación temporal de la ventana NO está demostrada. La medición de frecuencia de duplicación NO está demostrada. La propiedad integral de idempotent apply NO está demostrada. El cumplimiento completo NO está demostrado. |
| H-18.2.0-C | "ProfileStore requiere persistencia obligatoria." | NO VERIFICABLE | E-18.2.0-001 | Requiere cuantificación de coste de re-inferencia (HITO_18.2.1). No se puede afirmar ni rechazar sin esa evidencia. |
| H-18.2.0-D | "CircuitBreaker requiere persistencia obligatoria." | NO VERIFICABLE | E-18.2.0-002 | Requiere evaluación de impacto de perder estado (HITO_18.2.1). |
| H-18.2.0-E | "La telemetría es operational state prescindible para recovery." | NO VERIFICABLE | E-18.2.0-003 | Requiere revisión contractual de si la telemetría participa en garantías de recovery o auditoría. Clasificación preliminar: operational state con destino F20, pendiente confirmación. |
| H-18.2.0-F | "La maquinaria de recovery converge en todos los escenarios de fallo." | NO VERIFICABLE | E-18.2.0-007, E-18.2.0-008 | Requiere validación empírica con chaos harness ampliado (HITO_18.2.1 / Gate 4). |
| H-18.2.0-G | "DC-13 existe como DC formal en el registro canónico." | RECHAZADA | E-18.2.0-012 | DC-13 fue eliminado del registro canónico en ADR_F18.1 v1.0.1. Referencias residuales son deuda documental. |
| H-18.2.0-H | "NADR-F18-02 está en DRAFT y debe promoverse antes de 18.2." | RESUELTA | Archivo físico dice FROZEN; commit de promoción ejecutado durante Paso -1 (ee392e8) | La contradicción handoff vs. archivo fue resuelta. NADR-F18-02 está FROZEN v1.0.1. (Hecho reportado; verificación independiente corresponde a Paso -1.) |
| H-18.2.0-I | "La acotación temporal de la ventana de duplicación es ~1-10ms." | HIPÓTESIS no validada | E-18.2.0-004 | El número de líneas entre dos llamadas no establece una cota temporal. La ejecución del proveedor, la planificación del proceso y las operaciones intermedias pueden afectar el tiempo transcurrido. Requiere medición (HITO_18.2.1). |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué superficie durable existe actualmente en el execution plane?

**Estado actual verificado (FACT):**

1. Task lease como intención durable: pick_task persiste PROCESSING + lease_owner + lease_expires_at + execution_id de intento antes del efecto.
2. Fencing/epochs: implementado a nivel SQL (SystemPlaneRepository + ControlPlaneRepository).
3. Recovery machinery: 6 componentes funcionales (watchdog, sweeper, resumer, reconciler, 2 handlers).
4. FSM: 12 estados incluyendo STALLED, FAILED_RETRYABLE, FAILED_FATAL.
5. Idempotencia: reconciliation_id + processed_reconciliation_commands; upsert_projection con version check; append_wal con ON CONFLICT DO NOTHING.
6. Chaos harness: game_day_1_crash_consistency funcional.
7. Mecanismos 18.1: coordination, shutdown, cancellation, admission, backpressure (FROZEN).
8. SQLite: WAL + NORMAL + busy_timeout=30s.

**Respuesta forense:**

La superficie durable existente es sustancialmente más completa de lo que la documentación de fase sugiere. El sistema ya tiene intención durable (lease), idempotent apply por operación concreta, ventana de duplicación existente, fencing, recovery, reconciliation idempotente y validación empírica.

**Implicación:**

18.2 no debe reinventar recovery. Debe cerrar gaps de medición y cuantificación, y validar empíricamente la maquinaria existente.

### 16.2 ¿Qué garantías proporciona realmente la maquinaria existente?

**Estado actual verificado:**

1. Intención durable: OBSERVADA (lease via pick_task).
2. Idempotent apply por operación concreta: OBSERVADO (upsert_projection, append_wal, reconciliation commands). Propiedad integral NO DEMOSTRADA.
3. Ventana de duplicación acotada: NO DEMOSTRADO (acotación temporal).
4. Ventana de duplicación medida: NO DEMOSTRADO.
5. Fencing: OBSERVADO a nivel API y SQL. No se identificó cobertura empírica suficiente en el alcance examinado.
6. Recovery: OBSERVADO a nivel API. Convergencia global NO DEMOSTRADA.

**Respuesta forense:**

Las garantías de intención durable e idempotent apply por operación concreta están OBSERVADAS. Las garantías de acotación y medición de la ventana de duplicación, propiedad integral de idempotent apply, seguridad empírica de fencing, y convergencia de recovery NO están DEMOSTRADAS.

**Implicación:**

HITO_18.2.1 debe caracterizar crash windows y cuantificar impactos. Gate 4 debe validar empíricamente convergencia y fencing.

### 16.3 ¿Qué gaps quedan frente a INV-JOURNAL y ADR_F18_MASTER §6.2?

**Estado actual verificado:**

1. INV-JOURNAL: Ni violación estructural ni cumplimiento completo demostrados. Gap de medición de la ventana de duplicación (P1).
2. DF-34: ProfileStore in-memory, coste de re-inferencia no cuantificado. Trigger propio independiente.
3. DF-24: CircuitBreaker in-memory, impacto no evaluado. Subsumido en DC-08.
4. GAP-0.9-02: telemetría con pérdida, clasificación pendiente revisión contractual.
5. DC-08: write-policy no formalizada, power loss no demostrado.
6. test_fencing.py: inexistente. No se identificó cobertura suficiente en el alcance examinado.

**Respuesta forense:**

Seis gaps consolidados. Dos son P1 (gap de medición del journal, cobertura de fencing). Cuatro son P2 (autoridades in-memory, telemetría, write-policy). Ninguno es P0: no hay violación estructural de invariante constitucional demostrada.

**Implicación:**

Los gaps son candidatos de alcance para 18.2. Su inclusión final y mecanismo de resolución deben reconciliarse con el ADR Master, las decisiones vigentes y la evidencia de HITO_18.2.1. ADR_F18.2 debe resolver DC-08 internamente, respetando la jerarquía normativa.

### 16.4 ¿Qué activos pueden reutilizarse sin reinvención?

**Estado actual verificado:**

La mayoría de los componentes auditados son RETAIN (recovery machinery, fencing, journal, projection, mecanismos 18.1). Cuatro componentes están TO BE VERIFIED (ProfileStore, CircuitBreaker, SQLiteTelemetryGateway, _process_task — su clasificación depende de evidencia o decisión adicional). Un componente es MISSING (test_fencing.py). Un artefacto es DEPRECATE (regression_gateway.pyc).

**Respuesta forense:**

La hipótesis de reutilización (Reuse Before Invent) está fuertemente respaldada. La proporción exacta RETAIN/total no se declara como métrica certificada porque el denominador agrupa componentes de distinta naturaleza; la clasificación cualitativa es suficiente para concluir que la reinvención no está justificada.

**Implicación:**

18.2 es una subfase de cierre de gaps y validación empírica, no de construcción. Reuse Before Invent aplica plenamente.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| DC-08 | Write-policy SQLite + mecanismo de journal de INV-JOURNAL | E-18.2.0-004, E-18.2.0-009, GAP-18.2.0-01, GAP-18.2.0-06 | Intención durable (lease) OBSERVADA; idempotent apply por operación concreta OBSERVADO; ventana de duplicación existe; acotación y medición NO demostradas; write-policy no formalizada | 18.2 (ADR_F18.2) |
| DF-24 | Persistencia de CircuitBreaker | E-18.2.0-002, GAP-18.2.0-03 | Ausente (in-memory) | 18.2 (subsumido en DC-08, ADR_F18_MASTER §8.3) |
| DF-34 | Persistencia de ProfileStore | E-18.2.0-001, GAP-18.2.0-02 | Ausente (in-memory) | 18.2 (trigger propio: cuantificación de re-inferencia; NO subsumido en DC-08) |
| DC-13 | Coordinated shutdown durable | E-18.2.0-012, OBS-18.2.0-02 | Eliminado del DC Log canónico (ADR_F18.1 v1.0.1) | N/A (referencia huérfana, limpiar) |

> **Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos. La trazabilidad del HITO no sustituye la autoridad del registro de decisiones.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Duplicación ocasional de llamadas LLM no cuantificada | Gap de medición en ventana execute→append_wal: la duplicación puede ocurrir pero no está medida | Medio (FinOps) | E-18.2.0-004 |
| Tormenta de reintentos tras restart | Si CircuitBreaker pierde estado OPEN y el proveedor sigue caído, el sistema puede reintentar hasta re-abrir | Medio (FinOps + disponibilidad) | E-18.2.0-002 |
| Pérdida de perfiles documentales | Crash antes de completar pipeline pierde perfiles inferidos | Bajo/Medio (depende de coste de re-inferencia, no cuantificado) | E-18.2.0-001 |
| Convergencia no demostrada | La maquinaria de recovery existe pero su convergencia global no está validada empíricamente | Medio (confiabilidad) | E-18.2.0-007, E-18.2.0-008 |
| Cobertura de fencing no demostrada | No se identificó cobertura empírica suficiente en el alcance examinado | Medio | E-18.2.0-010 |
| Sobreingeniería de recovery | Riesgo de construir un framework genérico cuando la maquinaria existente es suficiente | Medio (deuda técnica, YAGNI) | E-18.2.0-007 |
| Pérdida de WAL en power loss | synchronous=NORMAL no garantiza flush a disco tras pérdida de energía | Medio (durabilidad) | E-18.2.0-009 |
| Efecto externo tras pérdida de lease | El efecto externo puede producirse antes de que el worker compruebe que perdió autoridad | Medio (FinOps) | OBS-18.2.0-06 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR o NADR posterior deberá responder (previa evidencia de HITO_18.2.1):

1. ¿Qué mecanismo cierra el gap de medición de la ventana de duplicación (telemetría de duplicación, y opcionalmente distinción de escenarios "efecto no iniciado" vs "efecto iniciado pero no registrado")? (DC-08)
2. ¿ProfileStore requiere persistencia o reconstrucción determinista? (DF-34, requiere cuantificación)
3. ¿CircuitBreaker requiere persistencia o warm-up rápido es suficiente? (DF-24, requiere evaluación)
4. ¿La telemetría es operational state prescindible o autoridad durable? (GAP-0.9-02, requiere revisión contractual)
5. ¿Qué nivel de durabilidad se requiere para la write-policy SQLite: consistencia, durabilidad ante crash de proceso, o durabilidad ante pérdida de energía? (DC-08)
6. ¿Qué unidad de recuperación debe gobernar cada mecanismo: documento, chunk, batch-call, o execution? (INV-UNITS)
7. ¿Qué escenarios de crash debe cubrir el chaos harness para certificar convergencia de recovery, incluyendo la frontera entre proteger SQLite y proteger un proveedor externo? (Gate 4)

---

## 21. CIERRE DEL HITO 18.2.0

Este HITO confirma que el execution plane posee una maquinaria de recovery funcional y sustancialmente más completa de lo documentado. El task lease constituye una intención durable previa al efecto externo, idempotent apply está OBSERVADO por operación concreta, y la ventana de duplicación existe. **Ni la violación estructural de INV-JOURNAL ni su cumplimiento completo están demostrados.** La acotación temporal de la ventana NO está demostrada (HIPÓTESIS ~1-10ms). La medición de frecuencia de duplicación NO está demostrada. La propiedad integral de idempotent apply NO está demostrada. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". Se identifican seis gaps consolidados (dos P1, cuatro P2, ninguno P0): un gap de medición de la ventana de duplicación, dos autoridades in-memory pendientes de cuantificación, telemetría con pérdida pendiente de revisión contractual, cobertura de fencing no demostrada, y write-policy no formalizada (power loss). La convergencia de recovery y la seguridad empírica de fencing permanecen NO DEMOSTRADAS. Los gaps son candidatos de alcance para 18.2; su inclusión final y mecanismo de resolución requieren la evidencia de HITO_18.2.1 y las decisiones de ADR_F18.2.

**Estado del HITO:** FROZEN v1.3.0 (supersede v1.2.0, v1.1.0 y v1.0.0)

**Advertencia epistemológica de cierre:** Este HITO es un reporte forense. Las afirmaciones sobre el estado del repositorio, los resultados del chaos harness y el commit de promoción de NADR-F18-02 son reportadas como observaciones, no certificadas independientemente. El cumplimiento completo de INV-JOURNAL NO está demostrado por este HITO. La resolución requiere HITO_18.2.1 (medición de propiedades) y DC-08 (decisión arquitectónica).

**Condición de cierre cumplida:**

- [x] Metadata completa y consistente.
- [x] Changelog actualizado a la versión de cierre (v1.3.0 con registro de correcciones C1-C8).
- [x] Límite epistemológico declarado con niveles OBSERVADO/DEMOSTRADO/GARANTIZADO y categorías FACT/INFERENCE/HIPÓTESIS/NO DEMOSTRADO/DECISION PENDING.
- [x] Alcance auditado con estado real por superficie (sin porcentaje inflado).
- [x] Fuentes de evidencia listadas y clasificadas.
- [x] Matriz Observed/Required/Decision completa (§7).
- [x] Todas las evidencias tienen ID estable (E-18.2.0-001 a E-18.2.0-013).
- [x] Todas las evidencias tienen severidad clasificada.
- [x] Todas las evidencias relevantes separan Observed / Required / Decision.
- [x] Cláusula de "ventana de duplicación acotada y medida" del ADR Maestro incorporada explícitamente.
- [x] Distinción "efecto no iniciado" vs "efecto iniciado pero no registrado" prominente.
- [x] Distinción execution_id del contrato de identidad vs execution_id de intento explícita.
- [x] Idempotencia limitada a operaciones concretas; propiedad integral NO DEMOSTRADA.
- [x] Estimación ~1-10ms clasificada como HIPÓTESIS no validada.
- [x] Fencing reformulado: "no se identificó cobertura empírica suficiente en el alcance examinado".
- [x] Mecanismos 18.1: "no modificar semántica ni contratos sin decisión y trazabilidad correspondientes".
- [x] synchronous=NORMAL: separación de consistencia, durabilidad ante crash de proceso y durabilidad ante pérdida de energía.
- [x] DF-24 subsumido en DC-08 (confirmado por ADR Maestro §8.3); DF-34 con trigger propio independiente.
- [x] Justificación de severidad P1 reformulada: "El cumplimiento completo de INV-JOURNAL no está demostrado. La ventana existe, la acotación temporal no está demostrada, la medición de frecuencia no está demostrada. Esto es un gap que requiere evidencia adicional (HITO_18.2.1), no una violación confirmada ni un cumplimiento certificado."
- [x] Todos los gaps tienen evidencia vinculada (6 gaps).
- [x] Todos los gaps tienen fase destino explícita.
- [x] Todas las hipótesis están cerradas (10 hipótesis: 1 CONFIRMADA, 3 RECHAZADAS, 1 RESUELTA, 1 HIPÓTESIS no validada, 4 NO VERIFICABLE).
- [x] Cero hipótesis abiertas.
- [x] Contradicciones internas v1.0.0 documentadas y corregidas en v1.1.0, v1.2.0 y v1.3.0.
- [x] Todos los IDs E, GAP, OBS, H son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas y advertencia epistemológica.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.

**Verificación de cadena de gobernanza:**

ADR_F18_MASTER FROZEN → ADR_F18.1 FROZEN → NADR-F18-01 FROZEN → NADR-F18-02 FROZEN → HITO_0.8 v1.4.0 → FASE_18.1_HANDOFF v1.0.0 → HITO_18.2.0 v1.0.0 → HITO_18.2.0 v1.1.0 → HITO_18.2.0 v1.2.0 → **HITO_18.2.0 v1.3.0 FROZEN (supersede)** → HITO_18.2.1 (pendiente) → ADR_F18.2 (pendiente) → NADR-F18-03 (pendiente) → PHASE_18.2_EXECUTION_PLAN (pendiente)

**Contradicciones con HITOs previos y con versiones anteriores:**

- v1.0.0 clasificó GAP-18.2.0-01 como P0 (violación de INV-JOURNAL). v1.1.0 lo reclasificó como P1 (gap de observabilidad) tras re-verificación forense del task lease. v1.2.0 mantuvo P1 e incorporó explícitamente la cláusula de "ventana de duplicación acotada y medida". v1.3.0 refina la justificación: ni violación ni cumplimiento completo demostrados. No es contradicción con HITOs previos; es corrección interna documentada.
- v1.2.0 no distinguía execution_id del contrato de identidad de execution_id de intento. v1.3.0 incorpora la distinción (C2).
- v1.2.0 declaraba idempotencia de aplicación del resultado como OBSERVADA integralmente. v1.3.0 limita la afirmación a operaciones concretas; propiedad integral NO DEMOSTRADA (C3).
- v1.2.0 declaraba la acotación temporal ~1-10ms como OBSERVADA. v1.3.0 la clasifica como HIPÓTESIS no validada (C4).
- v1.2.0 decía "cobertura de fencing inexistente". v1.3.0 reformula: "no se identificó cobertura empírica suficiente en el alcance examinado" (C5).
- v1.2.0 decía "mecanismos 18.1 intocables". v1.3.0 reformula: "no modificar semántica ni contratos sin decisión y trazabilidad correspondientes" (C6).
- v1.2.0 no separaba niveles de durabilidad de synchronous=NORMAL. v1.3.0 separa consistencia, durabilidad ante crash de proceso y durabilidad ante pérdida de energía (C7).
- v1.2.0 no distinguía DF-24 (subsumido en DC-08) de DF-34 (trigger propio). v1.3.0 incorpora la distinción (C8).
- HITO_0.8 v1.4.0 identificó GAP-0.2-04, GAP-0.8-01, GAP-0.9-02 y DC-13. Este HITO confirma GAP-0.2-04 (reclasificado a gap de medición P1), GAP-0.9-02 (pendiente revisión contractual), y resuelve DC-13 como referencia huérfana. GAP-0.8-01 (coordinated shutdown) fue resuelto en 18.1.

**Decision Candidates generados:** Ninguno nuevo. DC-08, DF-24 y DF-34 son DCs existentes del ADR Maestro que este HITO confirma como abiertos. DC-13 confirmado como referencia huérfana (eliminar).

**Siguiente paso recomendado:** Emitir HITO_18.2.1_CRASH_WINDOW_FINOPS_ANALYSIS con contrato de medición de propiedades: (A) ventana temporal (distribución de tiempo entre efecto externo y persistencia del evento; condiciones del experimento y percentiles), (B) frecuencia de duplicación (inyecciones de crash en puntos controlados; número de efectos externos repetidos sobre intentos y ejecuciones totales), (C) recuperación (estado durable inicial, punto del fallo, estado tras reinicio y resultado final esperado/observado), (D) coste FinOps (llamadas repetidas, tokens o coste atribuible, metodología de cálculo y límites de extrapolación), (E) fencing (intento de escritura o efecto desde un worker obsoleto y evidencia de rechazo; incluir el límite entre proteger SQLite y proteger un proveedor externo), (F) convergencia (escenarios de crash definidos, invariantes comprobadas y criterios de aceptación por unidad de recuperación). El HITO_18.2.1 debe cerrar con matriz escenario → contrato esperado → mecanismo existente → evidencia observada → gap → decisión que requiere. No debe diseñar la solución ni prescribir arquitectura de journal.

---

**Nota de Gobernanza:** Este HITO es evidencia forense pura. No propone código de producción. No materializa decisiones de implementación. No acepta unilateralmente limitaciones que contradigan invariantes congelados. Su función es servir como insumo para HITO_18.2.1, ADR_F18.2, NADR-F18-03 y PHASE_18.2_EXECUTION_PLAN. La versión v1.3.0 supersede v1.2.0, v1.1.0 y v1.0.0 y constituye la referencia canónica para documentos posteriores.