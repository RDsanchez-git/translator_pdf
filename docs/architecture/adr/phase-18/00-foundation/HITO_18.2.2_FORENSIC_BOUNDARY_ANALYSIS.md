# HITO_18.2.2_FORENSIC_BOUNDARY_ANALYSIS.md

**Estado:** FROZEN
**Versión:** v1.4.1
**Fecha de emisión original:** 2026-10-10
**Fecha de enmienda v1.1.0:** 2026-10-10
**Fecha de enmienda v1.2.0:** 2026-10-10
**Fecha de enmienda v1.3.0:** 2026-10-10
**Fecha de enmienda v1.3.1:** 2026-10-10
**Fecha de enmienda v1.4.0:** 2026-10-10
**Fecha de enmienda v1.4.1:** 2026-10-10
**Fecha de congelamiento:** 2026-10-10
**Fase:** Fase 18 (Advanced Local Runtime) — Subfase 18.2 (Durable Execution & Recovery)
**Tipo de artefacto:** Forensic Discovery (código fuente)
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación. No prescribe soluciones de diseño; identifica problemas, alternativas y límites de la evidencia disponible.
**Supersede:** HITO_18.2.2 v1.4.0 DRAFT

**Advertencia epistemológica obligatoria:** Este HITO es auditoría forense de código fuente. Clasifica cada hallazgo en FACT (código verificado), INFERENCE (conclusión derivada con razonamiento explícito), NO DEMOSTRADO (requiere ejecución o evidencia adicional), y DECISION CANDIDATE (alternativa arquitectónica pendiente de Board). NO certifica garantías integrales; proporciona evidencia para decisiones acotadas. Este documento NO prescribe soluciones de diseño; identifica problemas, alternativas y límites de la evidencia disponible. La ausencia de un mecanismo en el código auditado no demuestra que un proveedor externo carezca de esa capacidad; la verificación de capacidades externas requiere acceso al contrato/API del proveedor.

**Convención de IDs:** Todos los IDs de evidencia usan el formato canónico `E-18.2.2-NNN`. Las referencias cortas `E-NNN` que aparecen en este documento son abreviaturas internas equivalentes a `E-18.2.2-NNN` y no constituyen IDs alternativos.

**Nota de numeración editorial:** Las secciones §8, §9 y §17 no aparecen explícitamente en este documento. Esto se debe a que la estructura canónica de METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 FROZEN incluye secciones que, para el caso específico de Forensic Discovery de execution plane, quedan incorporadas en las secciones existentes (§7 Matriz Observed/Required/Decision absorbe §8; §10 Registro de Evidencia Forense absorbe §9; §18 Matriz de Trazabilidad DC absorbe §17). Esta omisión es editorial y no afecta la integridad del contenido.

**Evidencia Forense Vinculante:**
- HITO_18.2.0 v1.3.0 FROZEN
- HITO_18.2.1 v1.2.0 FROZEN
- ADR_F18_MASTER v1.0.0 FROZEN (§5.1 invariantes, §6.2 subfases, §8.2 DC Log)
- ADR_F18.1 v1.0.2 FROZEN
- NADR-F18-02 v1.0.1 FROZEN
- F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 FROZEN
- Código fuente auditado: 2026-10-10 (rama `fase18_subfase02_gate00`, commit `9ea2627`)

**Mandato:** Caracterizar empíricamente las garantías reales de ejecución durable, recovery y fencing externo en el execution plane actual, identificando brechas entre lo implementado y lo requerido por INV-JOURNAL (ADR_F18_MASTER §5.1).

**Síntesis:** El execution plane tiene fencing DB/SQL y epoch fencing DEMOSTRADOS, fencing external-effect PARCIAL, y una brecha principal: ausencia de resolución de efectos externos inciertos en recuperación. Se identifican 5 gaps (2 P1, 3 P2).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-DRAFT | 2026-10-10 | Emisión inicial. 8 líneas de investigación auditadas. |
| 1.1.0-DRAFT | 2026-10-10 | Reestructuración completa bajo METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 FROZEN. |
| 1.2.0-DRAFT | 2026-10-10 | Enmienda tras revisión arquitectónica externa. Reformulación de afirmaciones absolutas. Taxonomía de fencing. Separación de intención durable en control plane vs event journal. |
| 1.3.0-DRAFT | 2026-10-10 | Enmienda de compliance metodológico. Formato extendido para evidencias P1. Reclasificación E-002/E-005 a P2. |
| 1.3.1-DRAFT | 2026-10-10 | Enmienda de compliance metodológico. Nota de descomposición DC-08. Síntesis condensada. |
| 1.4.0-DRAFT | 2026-10-10 | Enmienda tras auditoría externa v2. Versionado normalizado. Tabla de gaps con columna Severidad. Ventana ~1ms como ESTIMACIÓN INDIRECTA HEREDADA. Consistencia de taxonomía. |
| 1.4.1-DRAFT | 2026-10-10 | Enmienda tras auditoría externa v3. SIGKILL delimitado. E-004/E-013 unificados a P2. Consecuencias condicionales. INV-JOURNAL reformulado. Justificación normativa de severidades. Telemetría descompuesta. GAP-03 como incertidumbre. Conclusiones como INFERENCE/RECOMMENDATION. |
| **1.4.1-FROZEN** | **2026-10-10** | **Congelamiento tras auditoría final. Correcciones REV-01, REV-02, REV-03 aplicadas. Ajustes editoriales de numeración y fraseo de hipótesis. Documento listo como insumo para ADR_F18.2.** |

---

## 1. RESUMEN EJECUTIVO

Se ejecutó auditoría forense de código sobre las 8 líneas de investigación (D-01 a D-08) del execution plane, completando la evidencia iniciada en HITO_18.2.0 v1.3.0 y HITO_18.2.1 v1.2.0. La auditoría cubrió los módulos principales del worker LLM, reconciler, handlers, repositorios de persistencia, mecanismos de recovery y telemetría, verificando los contratos de INV-JOURNAL, INV-OPS-1 y INV-SCI-1 definidos en ADR_F18_MASTER §5.1.

**Hallazgo central:**

> El execution plane posee un mecanismo de intención persistida vía task lease en `chunk_tasks` (PROCESSING + execution_id + lease_owner + lease_expires_at) que se escribe antes del efecto externo. La intención persistida está OBSERVADA; la recuperabilidad estructural bajo crash NO está demostrada empíricamente. La brecha principal es la ausencia de un mecanismo para resolver el caso de efecto externo incierto durante la recuperación: el reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado en el journal", lo cual permite un escenario de duplicación de efectos externos cuando el proveedor completa la operación y el proceso cae antes de registrar el resultado. El código cliente auditado no implementa idempotencia en la frontera LLM; las capacidades de deduplicación y consulta del proveedor externo están pendientes de verificación.

**Defectos dominantes confirmados:**

1. **Ausencia de resolución de efectos inciertos en recuperación (E-18.2.2-007, E-18.2.2-008):** El reconciler no distingue "sin INTENT/lease" de "con INTENT/lease sin GENERATED". No existe lógica de verificación con el proveedor ni estado de cuarentena para efectos inciertos.
2. **Código cliente sin idempotencia en frontera LLM (E-18.2.2-013):** Búsqueda exhaustiva de mecanismos de idempotencia en el código cliente → 0 resultados. Capacidades del proveedor externo NO DEMOSTRADAS. Una reejecución puede generar una segunda operación y un coste adicional, salvo que el proveedor aplique deduplicación efectiva; esta capacidad no ha sido verificada.
3. **Telemetría sin distinción de re-ejecución (E-18.2.2-033):** `ProductionTelemetryEvent` no tiene campos para distinguir primera ejecución de re-ejecución accidental.
4. **test_fencing.py vacío (E-18.2.2-036):** Archivo existe pero tiene 0 bytes. Es un placeholder sin implementar.
5. **Durabilidad ante terminación abrupta real:** Comportamiento ante SIGKILL demostrado únicamente para el escenario cubierto por `game_day_1` (harness operativo); no demostrado para el crash entre efecto externo completado y registro en journal ni para power loss.

**Veredicto:** El lease en chunk_tasks constituye un mecanismo observado de intención durable; su recuperabilidad estructural bajo crash y su suficiencia para INV-JOURNAL no están demostradas empíricamente. La segunda cláusula (aplicación idempotente del resultado) está satisfecha para operaciones locales (append_wal, upsert_projection, reconciliation commands, FSM transitions) pero NO está garantizada para el efecto externo LLM. La propiedad obligatoria de "ventana de duplicación acotada y medida" no está completamente satisfecha: la ventana es una ESTIMACIÓN INDIRECTA HEREDADA (~1ms por resta de latencia mock, HITO_18.2.1) y la duración real NO está DEMOSTRADA; además no está medida con telemetría. Se identifican cinco gaps consolidados (dos P1, tres P2). El gap de resolución de efectos inciertos es el problema arquitectónico central que debe resolverse en DC-08b.

**Estado de preparación para el siguiente documento:** HITO_18.2.2 FROZEN v1.4.1. Sirve como insumo para decisiones de DC-08a, DC-08b, DC-08c y DC-08d en ADR_F18.2.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Este HITO separa rigurosamente seis niveles epistemológicos:

| Nivel | Definición | Aplicación en este HITO |
|---|---|---|
| **OBSERVADO** (Observed) | Lo que el código realmente hace hoy (inspección directa) | Configuración de PRAGMAs, enum EventLifecycle, vectores del reconciler, búsqueda de términos en código |
| **EVIDENCIA DOCUMENTAL** | Lo que la documentación oficial de un componente afirma | Semántica de WAL+NORMAL según documentación de SQLite |
| **DEMOSTRADO** | Comportamiento verificado empíricamente mediante ejecución | Fencing SQL (HITO_18.2.1). SIGKILL ejecutado en game_day_1 para escenario específico. |
| **NO DEMOSTRADO** | Requiere ejecución o evidencia adicional | Fencing frontera externa, durabilidad ante crash post-efecto/pre-journal, capacidades del proveedor LLM, convergencia global, power loss |
| **DECISION CANDIDATE** | Alternativa arquitectónica pendiente de Board | DC-08a, DC-08b, DC-08c, DC-08d |
| **ESTIMACIÓN INDIRECTA** | Valor derivado de cálculo sobre mediciones existentes, no medido directamente | Ventana ~1ms (HITO_18.2.1, resta de latencia mock de 25ms a medición total de ~26ms) |

Específicamente, este HITO:

- **Puede** afirmar qué código existe y qué hace (OBSERVADO).
- **Puede** afirmar qué exige la arquitectura vigente (REQUERIDO por ADR_F18_MASTER).
- **Puede** afirmar qué decidió una fase previa (DECIDIDO en HITOs anteriores).
- **Puede** afirmar qué dice la documentación oficial de SQLite sobre WAL+NORMAL (EVIDENCIA DOCUMENTAL).
- **No puede** certificar que un mecanismo funciona bajo todos los escenarios de fallo (requiere validación empírica).
- **No puede** afirmar qué capacidades ofrece un proveedor externo (requiere verificación del contrato/API del proveedor).
- **No puede** cuantificar costes FinOps de duplicación natural (requiere telemetría de producción).
- **No puede** decidir mecanismos de resolución de gaps (requiere ADR/NADR).

**Nota sobre SIGKILL:** El harness operativo game_day_1_crash_consistency ejecuta SIGKILL real vía Docker y verifica convergencia para ese escenario específico. Esto constituye evidencia DEMOSTRADA para ese escenario. Sin embargo, NO constituye demostración de: (a) durabilidad general del execution plane ante SIGKILL en todos los escenarios, (b) crash post-efecto/pre-journal con efecto externo realmente ocurrido, (c) power loss.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (ADR_F18_MASTER, NADR-F18-02, ENGINEERING_PRINCIPLES).
2. Cargar HITOs previos aplicables (HITO_18.2.0 v1.3.0, HITO_18.2.1 v1.2.0).
3. Ejecutar 8 bloques de auditoría PowerShell read-only (D-01 a D-08).
4. Inspeccionar código fuente completo donde fue necesario.
5. Separar Observed / Required / Decision para cada hallazgo.
6. Registrar evidencia estable con IDs normalizados (E-18.2.2-NNN).
7. Consolidar gaps solo cuando exista discrepancia demostrada contra contrato vigente.
8. Declarar NO DEMOSTRADO cuando la evidencia sea insuficiente.
9. Derivar Decision Candidates solo si la evidencia los exige.
10. Verificar estado del repositorio (git status, tests, pyright, import-linter) como sanity check.

---

## 3. ALCANCE AUDITADO

**Nota metodológica sobre cobertura:** La tabla siguiente declara el estado real de cada superficie. "100% auditado" significa inspección directa del código fuente en este HITO. "Referenciado" significa usado por evidencia previa sin re-auditoría. "No verificable" significa que requiere runtime, disco, ejecución no disponible, o acceso a documentación externa del proveedor.

| Superficie | Módulos | Estado real |
|---|---|---|
| Worker LLM (flujo crítico) | apps/llm_workers/__main__.py | 100% auditado |
| Adaptadores LLM | apps/llm_workers/adapters.py | 100% auditado |
| Reconciler (vectores de recovery) | apps/daemons/reconciler.py | 100% auditado |
| Handlers de reconciliación | core/execution/handlers.py | 100% auditado |
| Repositorio de eventos | infra/db/event_repo.py | 100% auditado |
| Repositorio de proyecciones | infra/db/materialized_repo.py | 100% auditado |
| Repositorio de control | infra/db/control_repo.py | 100% auditado |
| Repositorio FSM | infra/db/fsm_repository.py | 100% auditado |
| Bootstrap SQLite | infra/db/bootstrap.py | 100% auditado |
| Connection factory | infra/db/connection.py | 100% auditado |
| CoordinatedShutdown | runtime/coordinated_shutdown.py | 100% auditado |
| Watchdog | runtime/recovery.py | 100% auditado |
| Sweeper | runtime/sweeper.py | 100% auditado |
| Resumer | runtime/resumer.py | 100% auditado |
| Telemetry gateway | core/telemetry/gateway.py | 100% auditado |
| Chaos harness | apps/daemons/chaos_runner.py | 100% auditado |
| Excepciones del dominio | core/execution/exceptions.py | 100% auditado |
| CircuitBreaker | core/resilience/circuit_breaker.py | 100% auditado |
| FSM states | core/execution/state.py | 100% auditado |
| ProfileStore | infra/db/profile_store.py | 100% auditado |
| Profiler | core/document_profile/profiler.py | 100% auditado |
| Tests de recovery | tests/integration/test_recovery_flow.py, tests/unit/test_recovery_determinability.py | 100% auditado |
| Tests de fencing | tests/test_fencing.py | 100% auditado (confirmado vacío, 0 bytes) |
| Convergencia global bajo múltiples escenarios | Comportamiento runtime | NO DEMOSTRADO (requiere ejecución de game_day_1 ampliado) |
| Durabilidad ante SIGKILL | Comportamiento runtime | DEMOSTRADO para escenario game_day_1; NO DEMOSTRADO para crash post-efecto/pre-journal ni power loss |
| Durabilidad ante power loss | Comportamiento hardware | NO DEMOSTRADO (requiere experimento físico) |
| Fencing frontera externa | Comportamiento proveedor LLM | NO DEMOSTRADO (requiere verificación de API del proveedor) |
| Capacidades de idempotencia del proveedor LLM | Contrato/API externo | NO VERIFICABLE desde el repositorio (requiere documentación del proveedor) |

**Nota sobre baseline de tests:** 854 tests collected, pyright 0 errors, 0 warnings. Import-linter: 4 contratos KEPT / 0 BROKEN. Rama: fase18_subfase02_gate00. Este baseline no debe degradarse.

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Clasificación | Uso en el HITO |
|---|---|---|---|
| ADR Maestro | docs/architecture/adr/phase-18/ADR/ADR_F18_MASTER.md v1.0.0 FROZEN | Normativa | INV-JOURNAL §5.1, INV-OPS-1, INV-SCI-1, DC-08, DF-24, DF-34 |
| NADR | docs/architecture/adr/phase-18/NADR/NADR-F18-02.md v1.0.1 FROZEN | Normativa | Bounded execution, shutdown §5.4 R15 |
| Contrato | docs/architecture/adr/phase-18/reports/F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.2 FROZEN | Normativa | Frontera de identidad |
| Principios | docs/architecture/ENGINEERING_PRINCIPLES.md | Normativa | Forensic First, Evidence-based, Anti-Spekulation |
| HITO previo | HITO_18.2.0 v1.3.0 FROZEN | Forense heredada | Superficie durable, gaps, clasificación P1 de GAP-18.2.0-01 |
| HITO previo | HITO_18.2.1 v1.2.0 FROZEN | Forense heredada | Ventana temporal estimada ~1ms (estimación indirecta), tasa de duplicación bajo inyección, fencing SQL DEMOSTRADO |
| Código | apps/llm_workers/__main__.py | Runtime | Flujo crítico _process_task, ventana execute→append_wal |
| Código | apps/daemons/reconciler.py | Runtime | Vectores de recuperación, epoch fencing |
| Código | core/execution/handlers.py | Runtime | Handlers de reconciliación, epoch verification |
| Código | infra/db/event_repo.py | Runtime | append_wal idempotente |
| Código | infra/db/materialized_repo.py | Runtime | upsert_projection idempotente |
| Código | infra/db/control_repo.py | Runtime | Task leases, optimistic locking, pick_task |
| Código | infra/db/fsm_repository.py | Runtime | FSM transitions con CAS |
| Código | infra/db/bootstrap.py, connection.py | Runtime | SQLite pragmas |
| Código | runtime/coordinated_shutdown.py | Runtime | Shutdown ordenado |
| Código | runtime/recovery.py, sweeper.py, resumer.py | Runtime | Recovery daemons |
| Código | core/telemetry/gateway.py | Runtime | Telemetry buffer in-memory |
| Código | apps/daemons/chaos_runner.py | Runtime | Chaos harness game_day_1 |
| Código | core/execution/exceptions.py | Runtime | Jerarquía de excepciones |
| Código | core/resilience/circuit_breaker.py | Runtime | CircuitBreaker in-memory |
| Test | tests/integration/test_recovery_flow.py | Verificación | Recovery end-to-end |
| Test | tests/unit/test_recovery_determinability.py | Verificación | Recovery determinable |
| Test | tests/test_fencing.py | Verificación | Confirmado vacío (0 bytes) |
| Documentación | Documentación oficial SQLite sobre WAL+NORMAL | Evidencia documental | Semántica de durabilidad esperada |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Worker LLM: secuencia crítica de lease, efecto externo y journal

~~~text
apps/llm_workers/__main__.py::LLMWorkerDaemon (run + _process_task)

  [PREVIO: pick_task() en engine.py / run loop]
    UPDATE chunk_tasks SET task_state='PROCESSING',
       lease_owner=?, lease_expires_at=?, execution_id=?       [OK] INTENCIÓN DURABLE
       (execution_id de intento: exec_{timestamp}_{uuid})         (control plane)
    BEGIN IMMEDIATE ... RETURNING ... commit                    [OK]

  -> _process_task(task)
      -> Checkpoint 1: raise_if_cancelled()                     [OK]
      -> ast_registry.get_node()                                [OK]
      -> materialized.get_projection_status()                   [OK] early exit si CURRENT
      -> event.get_replay()                                     [OK] replay económico si existe
      -> [si no hay replay]
          -> TaskLeaseHeartbeat.__enter__()                     [OK] renovación periódica de lease
          -> Checkpoint 2: raise_if_cancelled()                 [OK]
          -> processor.execute(node)                            [OK] EFECTO EXTERNO (LLM call)
          -> heartbeat.lease_lost check                         [OK] DB/SQL fencing parcial
          -> event.append_wal(...)                              [GAP] journal post-effecto
          -> Checkpoint 3: raise_if_cancelled()                 [OK]
      -> TextNormalizer.normalize()                             [OK]
      -> materialized.upsert_projection()                       [OK] idempotente
      -> control.mark_task_completed()                          [OK] acknowledge con CAS

Leyenda:
  [OK]   flujo sano observado
  [GAP]  gap confirmado (GAP-18.2.2-01)
  [RISK] riesgo latente
  [TBD]  requiere verificación adicional

GAP OBSERVADO (GAP-18.2.2-01, P1):
  Entre processor.execute() (efecto externo) y event.append_wal() (journal)
  existe una ventana. El check de heartbeat.lease_lost (E-18.2.2-002) previene
  escrituras obsoletas en SQLite (DB/SQL fencing) pero NO previene el efecto
  externo ya ocurrido. El reconciler no distingue "efecto no iniciado" de
  "efecto iniciado pero no registrado" (E-18.2.2-007, E-18.2.2-008).

  La secuencia observada permite un escenario de duplicación de efectos
  externos cuando el proveedor completa la operación y el proceso cae antes
  de registrar el resultado. La frecuencia, las condiciones exactas y la
  posibilidad de recuperación alternativa requieren validación empírica.

  NOTA: La ventana ~1ms es una ESTIMACIÓN INDIRECTA HEREDADA (HITO_18.2.1,
  obtenida por resta de latencia mock de 25ms a una medición total de ~26ms).
  La duración real de la ventana execute→append_wal NO está DEMOSTRADA.
~~~

### FLUJO B — Recovery: detección y reconciliación de zombies

~~~text
apps/daemons/reconciler.py::ReconcilerDaemon._sweep_tasks()

  SELECT task_id, document_id, node_id FROM chunk_tasks
  WHERE task_state = 'PROCESSING' AND lease_expires_at < now    [OK]

  Para cada zombie:
    latest_event = event_repo.get_latest_event(node_id)         [OK]

    SI latest_event.lifecycle == "GENERATED":
      -> RematerializeTaskCommand                               [OK] Vector 2: CQRS desync
      (efecto ocurrió, WAL existe, rematerializar proyección)
    SINO:
      -> RecoverZombieTaskCommand                               [GAP] Vector 1: zombie puro
      (devolver a PENDING, re-ejecutar)
      [GAP] Vector 1 no distingue "efecto no iniciado" de
            "efecto iniciado pero no registrado"

core/execution/handlers.py::ReconciliationCommandHandler
  -> handle_rematerialize()
      -> get_current_epoch() vs cmd.reconciler_epoch            [OK] epoch fencing
      -> mat.upsert_projection()                                [OK] rematerialización
      -> task.mark_cqrs_reconciled()                            [OK] idempotencia
  -> handle_recover_zombie()
      -> get_current_epoch() vs cmd.reconciler_epoch            [OK] epoch fencing
      -> task.mark_zombie_recovered()                           [OK] idempotencia

Leyenda:
  [OK]   flujo sano observado
  [GAP]  gap confirmado (GAP-18.2.2-01)

Veredicto: La maquinaria de recovery es funcional a nivel de API pero NO maneja
el escenario de efecto externo incierto (INTENT/lease sin GENERATED). Requiere
decisión arquitectónica sobre política de resolución (DC-08b).
~~~

### FLUJO C — Taxonomía de fencing observada

~~~text
TIPO 1: DB/SQL Fencing (protección de operaciones de persistencia local)
  -> pick_task: BEGIN IMMEDIATE + UPDATE RETURNING              [DEMOSTRADO]
  -> acknowledge_execution: WHERE lease_owner AND lease_expires_at >= now  [DEMOSTRADO]
  -> renew_task_lease: WHERE lease_owner AND task_state = PROCESSING       [DEMOSTRADO]
  -> mark_zombie_recovered: WHERE lease_owner                              [DEMOSTRADO]
  Evidencia: HITO_18.2.1 v1.2.0 (fencing SQL PASS)

TIPO 2: Reconciler Epoch Fencing (rechazo de comandos obsoletos)
  -> get_current_epoch() vs cmd.reconciler_epoch                [DEMOSTRADO]
  -> STALE_RECONCILER_COMMAND_DROPPED                           [DEMOSTRADO]
  Evidencia: core/execution/handlers.py:137-141

TIPO 3: External-Effect Fencing (impedir efecto externo obsoleto)
  -> heartbeat.lease_lost check POST-execute()                  [PARCIAL]
  -> Check ocurre DESPUÉS de processor.execute()                [OBSERVADO]
  -> No previene efecto ya ocurrido                             [OBSERVADO]
  -> No hay check PRE-execute()                                 [OBSERVADO]
  Evidencia: E-18.2.2-001, E-18.2.2-002

TIPO 4: Duplicate-Effect Prevention (impedir efectos duplicados)
  -> Idempotencia en proveedor LLM                              [NO DEMOSTRADO]
  -> Idempotency keys en código cliente                         [AUSENTE]
  -> Mecanismo de verificación con proveedor                    [AUSENTE]
  Evidencia: E-18.2.2-013, E-18.2.2-008

Leyenda:
  [DEMOSTRADO]  verificado empíricamente
  [OBSERVADO]   código inspeccionado
  [PARCIAL]     protección incompleta
  [AUSENTE]     no existe en el código auditado
  [NO DEMOSTRADO] requiere verificación externa

Veredicto: DB/SQL fencing y Reconciler epoch fencing están DEMOSTRADOS.
External-effect fencing es PARCIAL (check post-execute). Duplicate-effect
prevention está NO DEMOSTRADO (código cliente sin idempotencia; capacidades
del proveedor pendientes de verificación).
~~~

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| ProfileStore (implementación) | infra/db/profile_store.py::InMemoryProfileStore | Sí (DF-34) | dict in-memory, sin persistencia | CONFIRMADO |
| CircuitBreaker | core/resilience/circuit_breaker.py::GlobalCircuitBreaker | Sí (DF-24) | Estado in-memory CLOSED/OPEN/HALF_OPEN | CONFIRMADO |
| SQLiteRateLimitStore | infra/resilience/sqlite_rate_limit_store.py | No (precedente) | Persistencia de cuotas en SQLite WAL | CONFIRMADO |
| SQLiteTelemetryGateway | core/telemetry/gateway.py | Sí (GAP-0.9-02) | Buffer asyncio.Queue + flush batch a SQLite | CONFIRMADO |
| Task lease en chunk_tasks | infra/db/control_repo.py::pick_task | Sí (INV-JOURNAL) | task_state=PROCESSING + lease_owner + execution_id + lease_expires_at | CONFIRMADO (mecanismo observado; recuperabilidad bajo crash NO DEMOSTRADA) |
| TaskLeaseHeartbeat | apps/llm_workers/__main__.py::TaskLeaseHeartbeat | Sí (INV-JOURNAL) | Daemon thread de renovación de lease | CONFIRMADO |
| SystemPlaneRepository | infra/db/system_repo.py | Sí (fencing) | Leadership + epoch via lease_version | CONFIRMADO |
| ControlPlaneRepository | infra/db/control_repo.py | Sí (fencing) | Task leases + optimistic locking | CONFIRMADO |
| EventPlaneRepository | infra/db/event_repo.py | Sí (journal) | append_wal idempotente, get_replay, get_latest_event | CONFIRMADO |
| MaterializedPlaneRepository | infra/db/materialized_repo.py | Sí (projection) | upsert_projection idempotente con version check | CONFIRMADO |
| AbandonedProcessWatchdog | runtime/recovery.py | Sí (recovery) | Detecta docs estancados > 3600s → STALLED | CONFIRMADO |
| RecoveryDaemon (sweeper) | runtime/sweeper.py | Sí (recovery) | WAL checkpoint + purga STALLED > 1h | CONFIRMADO |
| OnDemandResumeManager | runtime/resumer.py | Sí (recovery) | Rescate STALLED → suspended_state | CONFIRMADO |
| ReconcilerDaemon | apps/daemons/reconciler.py | Sí (recovery) | Leadership + sweep zombies + FSM stalls | CONFIRMADO |
| ReconciliationCommandHandler | core/execution/handlers.py | Sí (recovery) | Rematerialize + RecoverZombie con epoch check | CONFIRMADO |
| DocumentCommandHandler | core/execution/handlers.py | Sí (recovery) | Transiciones FSM con CAS | CONFIRMADO |
| DocumentState FSM | core/execution/state.py | Sí (recovery) | 12 estados incluyendo STALLED, FAILED_RETRYABLE, FAILED_FATAL | CONFIRMADO |
| EventLifecycle enum | core/execution/ports.py | Sí (journal) | GENERATED, REMATERIALIZED, VALIDATED, REJECTED, RECONCILED. No incluye estados pre-effecto. | PARCIAL |
| ChaosInjector | apps/daemons/chaos_runner.py | Sí (validación) | Docker kill + upstream mutation | CONFIRMADO |
| game_day_1_crash_consistency | apps/daemons/chaos_runner.py | Sí (validación) | Kill SIGKILL + convergencia estricta | CONFIRMADO |
| CoordinatedShutdownMechanism | runtime/coordinated_shutdown.py | Sí (shutdown) | Secuencia ordenada signal_stop → processor_shutdown → close_connections | CONFIRMADO |
| Mecanismos 18.1 | coordination.py, shutdown.py, cancellation.py, admission.py, backpressure.py + runtime | Sí (18.1 FROZEN) | Primitivos de ejecución bounded | CONFIRMADO |
| test_fencing.py | tests/test_fencing.py | Sí (validación) | Existe pero VACÍO (0 bytes). Placeholder sin implementar. | PRESENT — EMPTY PLACEHOLDER |
| Idempotencia en código cliente LLM | apps/llm_workers/adapters.py, providers/ | Sí (INV-JOURNAL) | Búsqueda exhaustiva → 0 resultados | ABSENT IN AUDITED SCOPE |
| Capacidades de idempotencia del proveedor LLM | Contrato/API externo | Sí (INV-JOURNAL) | No verificable desde el repositorio | NOT EMPIRICALLY VALIDATED |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Intención/lease durable pre-effecto | Lease persistido en chunk_tasks (PROCESSING + execution_id + lease_owner + lease_expires_at) | INV-JOURNAL: "intención/lease/reserva recuperable tras crash" | HITO_18.2.0 identificó GAP-18.2.0-01 | MECANISMO OBSERVADO; RECUPERABILIDAD NO DEMOSTRADA | E-18.2.2-001, E-18.2.2-002 |
| Estado pre-effecto en event journal | EventLifecycle sin estados pre-effecto | INV-JOURNAL: recuperación tras crash | Ninguna | PARTIAL | E-18.2.2-007 |
| Idempotent apply (operaciones locales) | ON CONFLICT DO NOTHING en append_wal; version check en upsert_projection; INSERT OR IGNORE en reconciliation | INV-JOURNAL: "aplicación idempotente del resultado" | Ninguna | OBSERVADO | E-18.2.2-009 a E-18.2.2-012 |
| Idempotencia de efecto externo | Búsqueda de idempotency keys en cliente → 0 resultados | INV-JOURNAL: "aplicación idempotente del resultado" | DC-08: mecanismo abierto | NOT EMPIRICALLY VALIDATED | E-18.2.2-013 |
| Ventana de duplicación acotada | ESTIMACIÓN INDIRECTA HEREDADA (~1ms por resta) | INV-JOURNAL: "ventana de duplicación acotada y medida" | HITO_18.2.1 estimó ~1ms | NO DEMOSTRADO (duración real) | HITO_18.2.1 v1.2.0 |
| Ventana de duplicación medida | Sin instrumentación entre execute() y append_wal(); sin campos retry en telemetría | INV-JOURNAL: "ventana de duplicación medida" | Ninguna | NOT EMPIRICALLY VALIDATED | E-18.2.2-030, E-18.2.2-033 |
| Lógica de verificación con proveedor | Búsqueda → 0 resultados | Resolución de efectos inciertos | Ninguna | ABSENT IN AUDITED SCOPE | E-18.2.2-008 |
| Resolución de efectos inciertos | Reconciler Vector 1 trata todos los zombies igual | INV-JOURNAL: idempotent apply | Ninguna | ABSENT IN AUDITED SCOPE | E-18.2.2-007, E-18.2.2-008 |
| DB/SQL fencing | Optimistic locking + epoch verification | Fencing de persistencia local | HITO_18.2.1 demostró | DEMOSTRADO | HITO_18.2.1, E-18.2.2-003 |
| External-effect fencing | Check post-execute de lease_lost | Fencing de efecto externo | Ninguna | PARCIAL | E-18.2.2-001, E-18.2.2-002 |
| Durabilidad ante crash de proceso | WAL + NORMAL configurado | INV-JOURNAL: "recuperable tras crash" | Ninguna | EVIDENCIA DOCUMENTAL (semántica); COMPORTAMIENTO NO DEMOSTRADO | E-18.2.2-014, E-18.2.2-015 |
| Durabilidad ante SIGKILL | game_day_1 ejecuta SIGKILL real | INV-JOURNAL: "recuperable tras crash" | Ninguna | DEMOSTRADO para escenario game_day_1; NO DEMOSTRADO para crash post-efecto/pre-journal | E-18.2.2-028 |
| Durabilidad ante power loss | Sin pruebas | INV-JOURNAL: "recuperable tras crash" | Ninguna | NOT EMPIRICALLY VALIDATED | E-18.2.2-016, E-18.2.2-021 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Formato canónico: `E-18.2.2-NNN`. Severidad: P0 = bloquea certificación/viola invariante, P1 = defecto estructural, P2 = riesgo latente.

**Criterio de severidad aplicado:** P1 se asigna cuando el gap impide demostrar una propiedad obligatoria de INV-JOURNAL (idempotent apply del resultado externo, o ventana de duplicación medida). P2 se asigna cuando el gap es un hecho observado cuya adecuación al contrato depende de decisiones abiertas (DC-08) o cuando la evidencia no demuestra una violación sino una incertidumbre.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| E-18.2.2-001 | P2 | apps/llm_workers/__main__.py:326-329 → `raw_response = self.processor.execute(node)` seguido de `if heartbeat.lease_lost.is_set(): raise OptimisticLockError(...)` | Verificación de lease POST-EFFECT. El worker verifica el lease DESPUÉS de que el efecto externo ya ocurrió. Si el lease se pierde DURANTE execute(), el efecto externo ya se produjo antes de la verificación. |
| E-18.2.2-002 | P2 | apps/llm_workers/__main__.py:95-98 → TaskLeaseHeartbeat: `success = control_repo.renew_task_lease(...); if not success: self.lease_lost.set()` | Heartbeat asíncrono no detiene ejecución. El heartbeat corre en un thread separado. Si el lease expira durante execute(), el flag se setea pero la ejecución del LLM continúa hasta completion. NOTA: Esto es una decisión de diseño observada, no una violación de autoridad congelada. El Maestro no prescribe el comportamiento del heartbeat durante I/O externo. Relevante para DC-08b. |
| E-18.2.2-003 | P2 | core/execution/handlers.py:137-141 → `current_epoch = self.system.get_current_epoch("global_reconciler"); if cmd.reconciler_epoch != current_epoch: return` | Epoch fencing solo en reconciler. El epoch fencing protege al RECONCILER de ejecutar comandos obsoletos (Reconciler Epoch Fencing), pero NO protege al worker LLM de ejecutar efectos externos tras perder autoridad (External-Effect Fencing). |
| E-18.2.2-004 | P2 | apps/llm_workers/adapters.py + providers/ → Búsqueda exhaustiva de `fence`, `authority_check`, `idempotency`, `request.id` → 0 resultados | Código cliente sin mecanismos de external-effect fencing ni idempotencia. Búsqueda exhaustiva en código cliente → 0 resultados. Capacidades del proveedor externo NO DEMOSTRADAS. NOTA: Esta evidencia demuestra que el código cliente auditado no implementa estos mecanismos. NO demuestra que el proveedor externo carezca de estas capacidades; esa verificación requiere acceso al contrato/API del proveedor. |
| E-18.2.2-005 | P2 | apps/llm_workers/__main__.py:326-336 → `raw_response = self.processor.execute(node)` ... `self.event.append_wal(...)` | Ventana execute→append_wal sin transacción. Dos operaciones separadas sin coordinación transaccional. Si crash entre ambas, el efecto externo ocurrió pero no hay rastro en el journal. NOTA: El Maestro dice "El mecanismo concreto de persistencia y coordinación permanece abierto a DC-08." La ausencia de transacción es una decisión de diseño abierta, no un incumplimiento de autoridad congelada. Evidencia de soporte para GAP-18.2.2-01. |
| E-18.2.2-006 | P2 | apps/daemons/reconciler.py:159-177 → `latest_event = self.event_repo.get_latest_event(node_id); if latest_event and latest_event.lifecycle == "GENERATED": cmd = RematerializeTaskCommand(...) else: cmd = RecoverZombieTaskCommand(...)` | Reconciler distingue Vector 1 vs Vector 2. Vector 1: zombie puro (sin GENERATED) → PENDING. Vector 2: CQRS desync (GENERATED existe) → rematerializar. |
| E-18.2.2-007 | P1 | core/execution/ports.py:23-28 → `class EventLifecycle(Enum): GENERATED, REMATERIALIZED, VALIDATED, REJECTED, RECONCILED` | Event journal sin estados pre-effecto. El enum EventLifecycle solo tiene estados post-effecto. No hay estados INTENT, UNCERTAIN, PENDING_EXECUTION, ni similar en el journal de eventos. NOTA: El lease en chunk_tasks (PROCESSING + execution_id) es una forma de intención durable en el control plane. La ausencia de estado INTENT en el event journal no equivale a ausencia de intención durable. La brecha está en que el reconciler no puede distinguir "efecto no iniciado" de "efecto iniciado pero no registrado" durante la recuperación. |
| E-18.2.2-008 | P1 | apps/ + core/ + runtime/ → Búsqueda exhaustiva de `verify.*provider`, `check.*result`, `query.*status`, `confirm.*execution` → 0 resultados relevantes | NO hay lógica en el código auditado para verificar con proveedor si efecto externo ocurrió. Si crash en ventana execute→append_wal, el reconciler no puede consultar al proveedor para resolver la ambigüedad. NOTA: Esta evidencia demuestra ausencia en el código auditado. NO demuestra que el proveedor carezca de mecanismos de consulta; esa verificación requiere acceso al contrato/API del proveedor. |
| E-18.2.2-009 | P2 | infra/db/event_repo.py:42-51 → `INSERT INTO chunk_events_log ... ON CONFLICT(execution_id, node_id) DO NOTHING` | append_wal idempotente con ON CONFLICT DO NOTHING. Previene duplicación en el journal si el mismo execution_id+node_id se reintenta. NOTA: Idempotencia de persistencia local, NO idempotencia del efecto externo. |
| E-18.2.2-010 | P2 | infra/db/materialized_repo.py → `INSERT INTO valid_chunks_cache ... ON CONFLICT(document_id, ast_hash, node_id) DO UPDATE SET ... WHERE excluded.projection_version >= valid_chunks_cache.projection_version` | upsert_projection idempotente con version check monotónico. Solo actualiza si la nueva versión es mayor o igual. NOTA: Idempotencia de persistencia local, NO idempotencia del efecto externo. |
| E-18.2.2-011 | P2 | infra/db/control_repo.py::mark_cqrs_reconciled, mark_zombie_recovered → `INSERT OR IGNORE INTO processed_reconciliation_commands (reconciliation_id, processed_at) VALUES (?, ?)` | Reconciliation commands idempotentes por reconciliation_id. INSERT OR IGNORE previene reprocesamiento. |
| E-18.2.2-012 | P2 | infra/db/fsm_repository.py::transition_to → `UPDATE document_fsm SET current_state = ?, state_version = state_version + 1, ... WHERE document_id = ? AND ast_hash = ? AND current_state = ? AND state_version = ?` | FSM transitions con CAS (Compare-And-Swap). Si state_version no coincide, lanza OptimisticLockError. |
| E-18.2.2-013 | P2 | apps/llm_workers/ + core/prompting/ + infra/llm/ → Búsqueda exhaustiva de `idempotency`, `idempotent`, `dedup`, `cache_key`, `request_id`, `trace_id`, `Idempotency-Key`, `X-Request-ID`, `x-idempotency`, `client-side.dedup` → 0 resultados | Código cliente sin mecanismos de idempotencia en frontera LLM. Búsqueda exhaustiva en código cliente → 0 resultados. NOTA: Esta evidencia demuestra que el código cliente auditado no implementa ni utiliza idempotencia. NO demuestra que el proveedor externo carezca de capacidades de idempotencia; esa verificación requiere acceso al contrato/API del proveedor. El Maestro deja el mecanismo abierto a DC-08; la ausencia es hecho observado, no incumplimiento de autoridad congelada. |
| E-18.2.2-014 | P2 | infra/db/bootstrap.py:44-46 → `conn.execute("PRAGMA journal_mode=WAL;"); conn.execute("PRAGMA synchronous=NORMAL;"); conn.execute("PRAGMA busy_timeout=30000;")` | WAL + NORMAL + busy_timeout=30000 en bootstrap. Configuración aplicada en inicialización de BDs. |
| E-18.2.2-015 | P2 | infra/db/connection.py:59-61 → `conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA synchronous=NORMAL"); conn.execute(f"PRAGMA busy_timeout={timeout * 1000}")` | Mismos PRAGMAs en connection factory. Todas las conexiones usan WAL + NORMAL + busy_timeout. |
| E-18.2.2-016 | P2 | infra/ + apps/ + core/ + runtime/ → Búsqueda exhaustiva de `synchronous.*FULL`, `PRAGMA synchronous` → Solo NORMAL encontrado | synchronous=FULL ausente en el código auditado. NORMAL es universal en todo el código del execution plane. NOTA: La semántica de WAL+NORMAL según documentación oficial de SQLite es EVIDENCIA DOCUMENTAL. La durabilidad ante cada escenario de fallo requiere DEMOSTRACIÓN EMPÍRICA. El Maestro NO menciona fsync ni synchronous=FULL; la elección depende del modelo de fallos que DC-08d decida. |
| E-18.2.2-017 | P2 | runtime/sweeper.py:25-45 → `cursor = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")` ejecutado en EVENT_DB_PATH, MAT_DB_PATH, FSM_DB_PATH, QUEUE_DB_PATH | WAL checkpoint TRUNCATE en sweeper. Mantenimiento cíclico en los 4 planos de ejecución. |
| E-18.2.2-018 | P2 | runtime/coordinated_shutdown.py:16-91 → class CoordinatedShutdownMechanism: execute(reason) → signal_stop() → processor_shutdown() → close_connections() | CoordinatedShutdownMechanism existe. Secuencia garantizada best-effort con reporte de errores en ShutdownReport. |
| E-18.2.2-019 | P2 | apps/llm_workers/__main__.py:489-490 → `signal.signal(signal.SIGINT, shutdown_handler); signal.signal(signal.SIGTERM, shutdown_handler)` | Signal handlers para SIGINT/SIGTERM. Shutdown ordenado vía CoordinatedShutdownMechanism. |
| E-18.2.2-020 | P2 | apps/ + runtime/ + core/ → Búsqueda exhaustiva de `signal.SIGKILL` → 0 resultados | NO hay handler para SIGKILL en el código auditado. Imposible por diseño del SO: SIGKILL no es interceptable. NOTA: El harness operativo game_day_1_crash_consistency SÍ ejecuta kill real vía Docker (E-18.2.2-028). La ausencia se refiere a handlers en el código de producción, no a pruebas en el harness. |
| E-18.2.2-021 | P2 | infra/db/ + core/ + runtime/ → Búsqueda de `fsync` → Solo en corpus_repository.py:59 y ast_json.py:39 | fsync solo para corpus/AST, no para execution plane. Los 4 planos de ejecución (Event, Materialized, FSM, Queue) NO usan fsync explícito. NOTA: SQLite puede realizar operaciones de sincronización internamente según su configuración. La ausencia de fsync explícito en Python no demuestra ausencia de sincronización en el motor. |
| E-18.2.2-022 | P2 | apps/daemons/reconciler.py:164-181 → RecoverZombieTaskCommand (Vector 1) y RematerializeTaskCommand (Vector 2) | ReconcilerDaemon con Vector 1 y Vector 2. Vector 3 (_sweep_fsm_stalls) opera sobre documentos FSM, no sobre tasks. |
| E-18.2.2-023 | P2 | runtime/recovery.py:12-59 → class AbandonedProcessWatchdog: execute_sweep(threshold_sec=3600) | AbandonedProcessWatchdog con threshold 3600s. Detecta documentos estancados y los promueve a STALLED. |
| E-18.2.2-024 | P2 | runtime/sweeper.py:21-91 → class RecoveryDaemon: _force_wal_checkpoint() + run_sweep_cycle() | RecoveryDaemon (sweeper) con WAL checkpoint + abort de documentos STALLED tras TTL de cuarentena. |
| E-18.2.2-025 | P2 | runtime/resumer.py → class OnDemandResumeManager: rescue_stalled_document(document_id, ast_hash) | OnDemandResumeManager para rescate manual. Transiciona STALLED → suspended_state via CAS. |
| E-18.2.2-026 | P2 | runtime/ + apps/daemons/ → Búsqueda de orquestador coordinando watchdog, sweeper, resumer, reconciler → 0 resultados | 4 componentes NO coordinan explícitamente. Solo comparten DB, no hay orquestador que los sincronice. NOTA: Compartir una base de datos no demuestra por sí solo que haya una carrera efectiva. Hace falta identificar las operaciones concurrentes, sus intercalaciones y el efecto observable. |
| E-18.2.2-027 | P2 | apps/daemons/ + tests/ → Búsqueda de `game_day_2`, `game_day_3`, `chaos_scenario`, `fault_injection` → 0 resultados | Solo UN escenario de chaos: game_day_1. No hay escenarios adicionales para múltiples workers, pérdida de lease durante efecto externo, efectos inciertos. |
| E-18.2.2-028 | P2 | apps/daemons/chaos_runner.py:178-220 → game_day_1_crash_consistency: 5 docs, kill reconciler + worker-a con SIGKILL, espera convergencia 120s | game_day_1 prueba: 5 docs, kill reconciler + worker-a. Criterio de convergencia estricto: docs_completed == target AND chunks_pending == 0 AND chunks_processing == 0 AND chunks_orphaned == 0. NOTA: Este es un harness operativo en apps/daemons/chaos_runner.py, NO un test automatizado en tests/. Constituye evidencia DEMOSTRADA para ese escenario específico. |
| E-18.2.2-029 | P2 | apps/llm_workers/__main__.py:279, 380 → `start_node = time.perf_counter()` ... `metrics.observe("node_latency", time.perf_counter() - start_node)` | Timing solo con perf_counter para node_latency. Mide latencia total del nodo, NO la ventana execute→append_wal específicamente. |
| E-18.2.2-030 | P1 | apps/llm_workers/__main__.py:326-336 → Entre execute() y append_wal() solo hay check de lease_lost y comentarios | NO hay instrumentación entre execute() y append_wal(). No hay métricas intermedias, logs de timing, ni telemetría específica de la ventana. NOTA: Esto impide medir el intervalo observable cliente execute()→append_wal() directamente. |
| E-18.2.2-031 | P2 | core/telemetry/gateway.py:21-60 → class SQLiteTelemetryGateway: _queue: asyncio.Queue, _flush_worker() batch de 50 | Telemetry gateway async con queue. Fire-and-forget con flush batch de 50 eventos. Crash abrupto pierde eventos en cola. |
| E-18.2.2-032 | P2 | apps/daemons/chaos_runner.py:180-217 → game_day_1_crash_consistency existe y ejecuta kill real | Chaos harness existe. game_day_1 ejecuta kill real (SIGKILL vía Docker) y verifica convergencia. NOTA: Esto constituye evidencia DEMOSTRADA para ese escenario específico, NO para todos los escenarios de fallo. |
| E-18.2.2-033 | P1 | core/telemetry/models.py → class ProductionTelemetryEvent: execution_id, chunk_id, provider, event_type, selection_reason, latency_ms, quota_wait_ms, input_tokens, output_tokens | NO hay telemetría para distinguir primera ejecución de re-ejecución. ProductionTelemetryEvent no tiene campos retry_count, attempt_number, is_replay, ni similar. NOTA: Esto impide identificar intentos y reejecuciones en producción. |
| E-18.2.2-034 | P2 | tests/integration/test_recovery_flow.py (5902 bytes) → test_complete_crash_recovery_and_resume_lifecycle | test_recovery_flow.py EXISTE. Test end-to-end de watchdog + resumer + pipeline. |
| E-18.2.2-035 | P2 | tests/unit/test_recovery_determinability.py (2304 bytes) | test_recovery_determinability.py EXISTE. Tests de recovery determinable post-fallo. |
| E-18.2.2-036 | P2 | tests/test_fencing.py → `ls -la` muestra 0 bytes | test_fencing.py VACÍO (0 bytes). Es un placeholder sin implementar. NOTA: Se refiere a tests/ (pruebas automatizadas). El harness operativo game_day_1 en apps/daemons/chaos_runner.py SÍ ejecuta kill real (E-18.2.2-028). |
| E-18.2.2-037 | P2 | tests/ → Búsqueda de tests de power_loss, SIGKILL, fencing de frontera externa → 0 resultados | NO hay tests automatizados en tests/ para power loss, SIGKILL, o fencing de frontera externa. NOTA: El harness operativo game_day_1 SÍ usa SIGKILL (E-18.2.2-028), pero no existe una prueba automatizada dedicada al escenario de efecto externo completado antes del crash y no registrado en el journal. |
| E-18.2.2-038 | P2 | apps/llm_workers/__main__.py:328-329 → `if heartbeat.lease_lost.is_set(): raise OptimisticLockError(...)` | OptimisticLockError manejada. Previene escrituras obsoletas en SQLite si lease fue revocado durante I/O (DB/SQL fencing parcial). |
| E-18.2.2-039 | P2 | apps/llm_workers/__main__.py:360-366 → `except TaskCancelledError as e: self.control.abandon_execution(task_id, reason=f"CANCELLED:{e.reason}")` | TaskCancelledError → abandon_execution. Libera recursos (lease) para retry por otro worker. |
| E-18.2.2-040 | P2 | apps/llm_workers/__main__.py:247-251 → `except (TransientAPIError, CircuitOpenError, TimeoutError): task_id_err = task["task_id"][:8] if task else "UNKNOWN"; logger.warning(...)` | TransientAPIError/CircuitOpenError → abandonar tarea. Self-healing reasignará vía reconciler. |
| E-18.2.2-041 | P2 | apps/llm_workers/__main__.py:240-245 → `except ResourceExhaustedError as e: logger.critical(...); self._exited_due_to_resource = True; self._coord.signal_stop()` | ResourceExhaustedError → fail-fast. INV-NO-RESOURCE-SIGNAL: agotamiento de recursos produce EXECUTION_FAILURE, nunca REGRESSION/PASS. |
| E-18.2.2-042 | P2 | core/resilience/circuit_breaker.py → class GlobalCircuitBreaker: failure_threshold=5, window_sec=60, recovery_timeout=30, estados CLOSED/OPEN/HALF_OPEN | CircuitBreaker con CLOSED/OPEN/HALF_OPEN. Parámetros concretos observados. La configuración establece `recovery_timeout=30s`. El tiempo efectivo de recuperación depende de la ejecución y del resultado de la sonda; no fue medido empíricamente. |
| E-18.2.2-043 | P2 | core/execution/state.py → DocumentState: CREATED, PARSING, PROCESSING, READY_FOR_ASSEMBLY, ASSEMBLING, READY_FOR_COMPILATION, COMPILING, COMPLETED, FAILED_RETRYABLE, FAILED_FATAL, STALLED, CANCELLED | FSM con FAILED_RETRYABLE/FAILED_FATAL/STALLED. Transiciones legales definidas en LEGAL_TRANSITIONS. |
| E-18.2.2-044 | P2 | infra/db/profile_store.py → class InMemoryProfileStore: _store: dict[str, InferredDocumentProfile] = {} | ProfileStore in-memory. dict sin persistencia. Pierde todo el estado en restart. |
| E-18.2.2-045 | P2 | core/document_profile/profiler.py → class HeuristicDocumentProfiler: usa LayoutDetector + DocumentTypeDetector + ProfileSamplingPolicy | HeuristicDocumentProfiler heurístico. Sin llamadas LLM. Bounded workload via ProfileSamplingPolicy. |

### Evidencia E-18.2.2-007: Event journal sin estados pre-effecto (P1)

* **Archivo Fuente Primario:** core/execution/ports.py
* **Símbolo Auditado:** EventLifecycle (Enum)
* **Declaración Observada:**

~~~python
class EventLifecycle(Enum):
    GENERATED = "GENERATED"
    REMATERIALIZED = "REMATERIALIZED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    RECONCILED = "RECONCILED"
~~~

* **Observed:** El enum EventLifecycle solo tiene 5 estados, todos post-effecto. No hay estados INTENT, UNCERTAIN, PENDING_EXECUTION, ni similar en el journal de eventos.
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "Ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash". La cláusula menciona explícitamente "intención/lease/reserva" como alternativas válidas. El lease en chunk_tasks (PROCESSING + execution_id + lease_owner + lease_expires_at) es una forma de intención durable en el control plane.
* **Decision:** HITO_18.2.0 v1.3.0 identificó GAP-18.2.0-01 (ventana post-effect/pre-journal) como P1. ADR_F18.2 v2.2.1 propone DC-08a (Intent-First Journal) como alternativa, pero aún no está implementado.
* **Hallazgo Forense:** La ausencia de estado INTENT en el event journal NO equivale a ausencia de intención durable. El lease en chunk_tasks satisface la primera cláusula de INV-JOURNAL ("intención/lease/reserva recuperable tras crash") como mecanismo observado; la recuperabilidad bajo crash NO está demostrada empíricamente. La brecha está en que el reconciler no puede distinguir "efecto no iniciado" de "efecto iniciado pero no registrado" durante la recuperación, porque no hay un registro en el event journal que capture la intención antes del efecto.
* **Consecuencia Arquitectónica:** La recuperación no puede resolver el caso de efecto externo incierto. Si crash ocurre entre execute() y append_wal(), el reconciler trata la tarea como zombie puro (Vector 1) y la devuelve a PENDING, permitiendo un escenario de duplicación del efecto externo.
* **Estado:** OPEN — clasificado como GAP-18.2.2-01 (P1). Requiere decisión de DC-08b sobre política de resolución de efectos inciertos.

### Evidencia E-18.2.2-008: NO hay lógica para verificar con proveedor si efecto externo ocurrió (P1)

* **Archivo Fuente Primario:** apps/ + core/ + runtime/ (búsqueda global)
* **Símbolo Auditado:** Búsqueda exhaustiva de `verify.*provider`, `check.*result`, `query.*status`, `confirm.*execution`
* **Declaración Observada:**

~~~text
Búsqueda global en apps/, core/, runtime/:
- verify.*provider → 0 resultados relevantes
- check.*result → 0 resultados relevantes
- query.*status → 0 resultados relevantes
- confirm.*execution → 0 resultados relevantes
(Solo falsos positivos en preservation.py: validación DOI/URL, no verificación con proveedor LLM)
~~~

* **Observed:** No existe código en el repositorio auditado que consulte al proveedor LLM para verificar si una llamada previa se completó.
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "aplicación idempotente del resultado". Para resolver el caso de efecto incierto (INTENT/lease sin GENERATED), se requiere un mecanismo que permita determinar si el efecto externo ocurrió.
* **Decision:** HITO_18.2.1 v1.2.0 identificó esta limitación. ADR_F18.2 v2.2.1 §10.1 (F-ADR-18.2-01) reconoce que Intent-First Journal NO elimina por sí solo la duplicación sin mecanismos adicionales.
* **Hallazgo Forense:** La ausencia de lógica de verificación con proveedor significa que el reconciler no puede resolver la ambigüedad del efecto incierto. Si crash ocurre entre execute() y append_wal(), el reconciler trata la tarea como zombie puro (Vector 1) y la devuelve a PENDING, permitiendo un escenario de duplicación del efecto externo.
* **Consecuencia Arquitectónica:** La recuperación no puede resolver el caso de efecto externo incierto sin un mecanismo adicional (verificación con proveedor, cuarentena, o aceptación explícita de duplicación).
* **Estado:** OPEN — clasificado como GAP-18.2.2-01 (P1). Requiere decisión de DC-08b sobre política de resolución de efectos inciertos.

### Evidencia E-18.2.2-013: Código cliente sin idempotencia en frontera LLM (P2)

* **Archivo Fuente Primario:** apps/llm_workers/adapters.py, providers/
* **Símbolo Auditado:** Búsqueda exhaustiva de mecanismos de idempotencia
* **Declaración Observada:**

~~~text
Búsqueda global en apps/llm_workers/, core/prompting/, infra/llm/:
- idempotency → 0 resultados
- idempotent → 0 resultados
- dedup → 0 resultados
- cache_key → 0 resultados
- request_id → 0 resultados
- trace_id → 0 resultados
- Idempotency-Key → 0 resultados
- X-Request-ID → 0 resultados
- x-idempotency → 0 resultados
- client-side.dedup → 0 resultados
~~~

* **Observed:** El código cliente auditado no implementa ni utiliza mecanismos de idempotencia, request IDs, ni deduplicación en las llamadas al proveedor LLM.
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "aplicación idempotente del resultado". Para que el resultado sea idempotente en la frontera externa, se requiere un mecanismo de idempotencia en el proveedor o en el cliente.
* **Decision:** HITO_18.2.1 v1.2.0 ya identificó esta limitación. ADR_F18.2 v2.2.1 §10.1 (F-ADR-18.2-01) reconoce que Intent-First Journal NO elimina por sí solo la duplicación sin mecanismos adicionales.
* **Hallazgo Forense:** El código cliente auditado no implementa idempotencia. NOTA IMPORTANTE: Esta evidencia demuestra que el **código cliente** no implementa idempotencia. NO demuestra que el **proveedor externo** carezca de capacidades de idempotencia. La verificación de capacidades del proveedor requiere acceso al contrato/API del proveedor vigente (Groq actualmente) y está pendiente de verificación externa.
* **Consecuencia Arquitectónica:** Una reejecución puede generar una segunda operación y un coste adicional, salvo que el proveedor aplique deduplicación efectiva; esta capacidad no ha sido verificada. La decisión de DC-08b debe considerar si el proveedor ofrece idempotencia y si el cliente debe utilizarla.
* **Estado:** OPEN — clasificado como GAP-18.2.2-02 (P2). Requiere verificación de capacidades del proveedor y decisión de DC-08b.

### Evidencia E-18.2.2-030: NO hay instrumentación entre execute() y append_wal() (P1)

* **Archivo Fuente Primario:** apps/llm_workers/__main__.py
* **Símbolo Auditado:** LLMWorkerDaemon._process_task (líneas 326-336)
* **Declaración Observada:**

~~~python
raw_response = self.processor.execute(node)  # línea ~326

if heartbeat.lease_lost.is_set():
    raise OptimisticLockError(...)

# Guardar en WAL ANTES del checkpoint 3 (preservar resultado del LLM)
# Si se cancela después, el resultado está en WAL para replay económico
self.event.append_wal(                       # línea ~333
    exec_id, doc_id, node_id, content_hash,
    raw_response, self.processor.prompt_v, self.processor.model_v,
    self.processor.projection_v, EventLifecycle.GENERATED
)
~~~

* **Observed:** Entre `processor.execute()` y `event.append_wal()` solo hay un check de `heartbeat.lease_lost` y comentarios. No hay métricas intermedias, logs de timing, ni telemetría específica de la ventana.
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "ventana de duplicación acotada y **medida**". Para medir la ventana, se requiere instrumentación que capture el timing entre el efecto externo y el registro en el journal.
* **Decision:** HITO_18.2.1 v1.2.0 estimó la ventana en ~1ms por resta de latencia mock (estimación indirecta, no medición directa). No existe instrumentación dedicada.
* **Hallazgo Forense:** La ausencia de instrumentación entre execute() y append_wal() impide medir directamente la duración de la ventana de duplicación y la frecuencia de crashes en esa ventana. La estimación de ~1ms es indirecta y no constituye una medición empírica directa.
* **Consecuencia Arquitectónica:** No se puede demostrar que la ventana de duplicación está "medida" como exige INV-JOURNAL. Se requiere instrumentación dedicada (DC-08c) para satisfacer esta propiedad.
* **Estado:** OPEN — clasificado como GAP-18.2.2-04 (P1). Requiere decisión de DC-08c sobre mecanismo de telemetría.

### Evidencia E-18.2.2-033: ProductionTelemetryEvent sin campos de re-ejecución (P1)

* **Archivo Fuente Primario:** core/telemetry/models.py
* **Símbolo Auditado:** ProductionTelemetryEvent (dataclass)
* **Declaración Observada:**

~~~python
class ProductionTelemetryEvent:
    execution_id: str
    chunk_id: str
    provider: str
    event_type: TelemetryEventType
    selection_reason: ProviderSelectionReason
    latency_ms: float
    quota_wait_ms: float
    input_tokens: int
    output_tokens: int
    # NO hay campos: retry_count, attempt_number, is_replay, is_reexecution
~~~

* **Observed:** ProductionTelemetryEvent tiene campos para ejecución, proveedor, latencia, quota y tokens. NO tiene campos para distinguir primera ejecución de re-ejecución accidental (retry_count, attempt_number, is_replay, is_reexecution, ni similar).
* **Required:** INV-JOURNAL (ADR_F18_MASTER §5.1): "ventana de duplicación acotada y **medida**". Para medir la tasa de duplicación en producción, se requiere telemetría que distinga primera ejecución de re-ejecución.
* **Decision:** HITO_18.2.1 v1.2.0 identificó esta limitación. HITO_18.2.0 v1.3.0 clasificó GAP-0.9-02 (telemetría) como P2.
* **Hallazgo Forense:** La ausencia de campos de re-ejecución en ProductionTelemetryEvent impide medir la tasa natural de duplicación en producción. No se puede distinguir si una llamada LLM es primera ejecución o re-ejecución por recovery.
* **Consecuencia Arquitectónica:** No se puede demostrar que la ventana de duplicación está "medida" como exige INV-JOURNAL. Se requiere extensión de ProductionTelemetryEvent (DC-08c) para satisfacer esta propiedad.
* **Estado:** OPEN — clasificado como GAP-18.2.2-04 (P1). Requiere decisión de DC-08c sobre mecanismo de telemetría.

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-18.2.2-01 | test_fencing.py existe pero está vacío (0 bytes). Es un placeholder sin implementar. Se refiere a tests/ (pruebas automatizadas). El harness operativo game_day_1 en apps/daemons/chaos_runner.py SÍ ejecuta kill real. | Medio | OPEN |
| OBS-18.2.2-02 | La configuración de CircuitBreaker establece `recovery_timeout=30s`. La estimación previa de ~60s en HITO_18.2.1 no queda sustentada por la configuración observada. El tiempo efectivo de recuperación depende de la ejecución y del resultado de la sonda; no fue medido empíricamente. | Bajo | CLOSED (corrección documental) |
| OBS-18.2.2-03 | Vector 3 del reconciler (_sweep_fsm_stalls) opera sobre documentos FSM, no sobre tasks. No es un tercer vector para efectos inciertos. | Bajo | CLOSED (aclaración documentada) |
| OBS-18.2.2-04 | Los 4 componentes de recovery (watchdog, sweeper, resumer, reconciler) son daemons independientes sin coordinación explícita. Compartir una base de datos no demuestra por sí solo que haya una carrera efectiva. Hace falta identificar las operaciones concurrentes, sus intercalaciones y el efecto observable. | Medio | OPEN (hipótesis, no finding) |
| OBS-18.2.2-05 | fsync solo se usa en corpus_repository.py y ast_json.py (módulos de corpus/AST), no en el execution plane. SQLite puede realizar operaciones de sincronización internamente según su configuración. | Bajo | CLOSED (documentado en E-18.2.2-021) |

---

## 12. MATRIZ DE TRIAJE

**Nota metodológica:** La clasificación refleja el estado forense observado. No prescribe soluciones de diseño. Las categorías son descriptivas del estado actual, no prescriptivas de cambios futuros.

| Componente | Clasificación | Justificación forense |
|---|---|---|
| InMemoryProfileStore | TO BE VERIFIED | Trigger DF-34 (cuantificar coste de re-inferencia) no ejecutado. Sin benchmark de CPU. (E-18.2.2-044) |
| GlobalCircuitBreaker | TO BE VERIFIED | Trigger DF-24 (evaluar impacto de perder estado) no ejecutado. Warm-up no medido; configuración observada con recovery_timeout=30s. (E-18.2.2-042) |
| SQLiteTelemetryGateway | TO BE VERIFIED | Buffer in-memory observado. Clasificación ACCEPTED_LIMITATION vs. autoridad durable pendiente de revisión contractual (destino F20). (E-18.2.2-031) |
| LLMWorkerDaemon._process_task | PARTIAL — contract coverage incomplete | Flujo funcional observado. Ventana execute→append_wal sin instrumentación. Check de lease post-execute. (E-18.2.2-001, E-18.2.2-005, E-18.2.2-030) |
| SystemPlaneRepository | PRESENT — behavior observed | Fencing OBSERVADO y funcional a nivel API/SQL. Requiere validación empírica (test_fencing.py). (E-18.2.2-003) |
| ControlPlaneRepository (pick_task/lease) | PRESENT — behavior observed | Lease como intención durable, optimistic locking funcionales. (E-18.2.2-001, E-18.2.2-002) |
| EventPlaneRepository (append_wal) | PRESENT — behavior observed | Journal idempotente funcional. Enum EventLifecycle no incluye estados pre-effecto. (E-18.2.2-007, E-18.2.2-009) |
| MaterializedPlaneRepository | PRESENT — behavior observed | Projection idempotente con version check. (E-18.2.2-010) |
| AbandonedProcessWatchdog | PRESENT — behavior observed | Recovery daemon OBSERVADO y funcional a nivel API. Requiere validación empírica de convergencia. (E-18.2.2-023) |
| RecoveryDaemon (sweeper) | PRESENT — behavior observed | WAL checkpoint + purga funcional. Requiere validación empírica. (E-18.2.2-024) |
| OnDemandResumeManager | PRESENT — behavior observed | Rescate de STALLED funcional. Requiere validación empírica. (E-18.2.2-025) |
| ReconcilerDaemon | PARTIAL — contract coverage incomplete | Vector 1 y Vector 2 funcionales. NO maneja escenario de efecto incierto (INTENT/lease sin GENERATED). (E-18.2.2-006, E-18.2.2-022) |
| ReconciliationCommandHandler | PRESENT — behavior observed | Handlers con epoch check e idempotencia funcionales. Requiere validación empírica. (E-18.2.2-003) |
| DocumentCommandHandler | PRESENT — behavior observed | Transiciones FSM con CAS funcionales. Requiere validación empírica. (E-18.2.2-012) |
| DocumentState FSM | PRESENT — behavior observed | 12 estados incluyendo STALLED, FAILED_RETRYABLE, FAILED_FATAL. Requiere validación empírica. (E-18.2.2-043) |
| EventLifecycle enum | PARTIAL — contract coverage incomplete | 5 estados post-effecto. No incluye estados pre-effecto. La brecha puede resolverse de múltiples formas (no necesariamente extendiendo este enum). (E-18.2.2-007) |
| ChaosInjector | PRESENT — behavior observed | Chaos harness OBSERVADO y funcional. No prueba escenario de efecto incierto. (E-18.2.2-032) |
| game_day_1_crash_consistency | PRESENT — behavior observed | Harness operativo con kill real. No es un test automatizado en tests/. No prueba escenario de efecto incierto. (E-18.2.2-028) |
| CoordinatedShutdownMechanism | PRESENT — behavior observed | Shutdown ordenado funcional. FROZEN en 18.1. (E-18.2.2-018) |
| Mecanismos 18.1 (coordination, shutdown, cancellation, admission, backpressure) | PRESENT — behavior observed | FROZEN. No deben modificarse. NADR-F18-02 §5.4 R15. (E-18.2.2-018, E-18.2.2-019) |
| tests/test_fencing.py | PRESENT — EMPTY PLACEHOLDER | Archivo existe con 0 bytes. Placeholder sin implementar. No es ausencia en el alcance; es presencia sin contenido. (E-18.2.2-036) |
| Idempotencia en código cliente LLM | ABSENT IN AUDITED SCOPE | Búsqueda exhaustiva → 0 resultados. (E-18.2.2-013) |
| Capacidades de idempotencia del proveedor LLM | NOT EMPIRICALLY VALIDATED | No verificable desde el repositorio. Requiere documentación del proveedor. (E-18.2.2-013) |
| SQLiteRateLimitStore | PRESENT — behavior observed | Precedente de autoridad durable en SQLite. (E-18.2.2-014) |
| ProductionTelemetryEvent | PARTIAL — contract coverage incomplete | Carece de campos retry_count, attempt_number, is_replay. Brecha de observabilidad. (E-18.2.2-033) |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Journal Semantics (INV-JOURNAL)

| Elemento | Estado | Evidencia |
|---|---|---|
| Intención/lease durable pre-effecto | MECANISMO OBSERVADO (lease en chunk_tasks); RECUPERABILIDAD ESTRUCTURAL NO DEMOSTRADA EMPÍRICAMENTE | E-18.2.2-001, E-18.2.2-002 |
| Estado pre-effecto en event journal | PARTIAL (ausente en EventLifecycle) | E-18.2.2-007 |
| Idempotent apply (operaciones locales) | OBSERVADO | E-18.2.2-009, E-18.2.2-010, E-18.2.2-011, E-18.2.2-012 |
| Idempotencia de efecto externo (proveedor) | NOT EMPIRICALLY VALIDATED | E-18.2.2-013 |
| Ventana de duplicación acotada | ESTIMACIÓN INDIRECTA HEREDADA (~1ms por resta de latencia mock, HITO_18.2.1); duración real NO DEMOSTRADA | HITO_18.2.1 v1.2.0 |
| Ventana de duplicación medida | NOT EMPIRICALLY VALIDATED | E-18.2.2-030, E-18.2.2-033 |
| Lógica de verificación con proveedor | ABSENT IN AUDITED SCOPE | E-18.2.2-008 |
| Resolución de efectos inciertos en recuperación | ABSENT IN AUDITED SCOPE | E-18.2.2-007, E-18.2.2-008 |

**Veredicto del pilar:** PARCIALMENTE CUMPLIDO. El lease en chunk_tasks constituye un mecanismo observado de intención durable; su recuperabilidad estructural bajo crash y su suficiencia para INV-JOURNAL no están demostradas empíricamente. La segunda cláusula ("aplicación idempotente del resultado") está satisfecha para operaciones locales pero NO está garantizada para el efecto externo LLM. La propiedad obligatoria de "ventana de duplicación acotada y medida" no está completamente satisfecha: la ventana es una ESTIMACIÓN INDIRECTA HEREDADA (~1ms por resta de latencia mock) y la duración real NO está DEMOSTRADA; además no está medida con telemetría. El gap principal es la ausencia de resolución de efectos inciertos en la recuperación.

### Pilar 2 — Autoridades Operacionales (DF-24, DF-34)

| Elemento | Estado | Evidencia |
|---|---|---|
| ProfileStore persistencia | ABSENT IN AUDITED SCOPE (in-memory) | E-18.2.2-044 |
| CircuitBreaker persistencia | ABSENT IN AUDITED SCOPE (in-memory) | E-18.2.2-042 |
| RateLimitStore persistencia (precedente) | PRESENT — behavior observed | E-18.2.2-014 |

**Veredicto del pilar:** FACT: ambas autoridades son in-memory y no sobreviven al reinicio. NO DEMOSTRADO: frecuencia e impacto económico reales. DECISION PENDING: persistir, reconstruir o aceptar, según contrato y evidencia (Gate 4). DF-24 está subsumido en DC-08 (ADR_F18_MASTER §8.3). DF-34 tiene trigger propio independiente (cuantificación de re-inferencia).

### Pilar 3 — Fencing & Ownership

| Elemento | Estado | Evidencia |
|---|---|---|
| DB/SQL fencing (protección de persistencia local) | DEMOSTRADO | HITO_18.2.1 v1.2.0, E-18.2.2-003 |
| Reconciler epoch fencing (rechazo de comandos obsoletos) | DEMOSTRADO | E-18.2.2-003 |
| External-effect fencing (impedir efecto externo obsoleto) | PARTIAL (check post-execute) | E-18.2.2-001, E-18.2.2-002 |
| Duplicate-effect prevention (impedir efectos duplicados) | NOT EMPIRICALLY VALIDATED | E-18.2.2-013, E-18.2.2-008 |
| Seguridad empírica de fencing | NOT EMPIRICALLY VALIDATED | E-18.2.2-036 |

**Veredicto del pilar:** DB/SQL fencing y Reconciler epoch fencing están DEMOSTRADOS. External-effect fencing es PARCIAL (check post-execute). Duplicate-effect prevention está NOT EMPIRICALLY VALIDATED (código cliente sin idempotencia; capacidades del proveedor pendientes de verificación). Seguridad empírica NOT EMPIRICALLY VALIDATED (test_fencing.py vacío).

### Pilar 4 — Recovery & Reconciliation

| Elemento | Estado | Evidencia |
|---|---|---|
| Detección de zombies (watchdog + reconciler) | PRESENT — behavior observed | E-18.2.2-022, E-18.2.2-023 |
| Aislamiento de zombies (STALLED state) | PRESENT — behavior observed | E-18.2.2-043 |
| Recuperación de zombies (Vector 1) | PRESENT — behavior observed | E-18.2.2-006, E-18.2.2-022 |
| Rematerialización CQRS (Vector 2) | PRESENT — behavior observed | E-18.2.2-006, E-18.2.2-022 |
| Barrido FSM documental (Vector 3) | PRESENT — behavior observed | E-18.2.2-022 |
| Vector para efectos inciertos (INTENT/lease sin GENERATED) | ABSENT IN AUDITED SCOPE | E-18.2.2-007, E-18.2.2-008 |
| Coordinación entre 4 componentes | NOT EMPIRICALLY VALIDATED | E-18.2.2-026 |
| Idempotencia de reconciliation | PRESENT — behavior observed | E-18.2.2-011 |
| Convergencia global de recovery | NOT EMPIRICALLY VALIDATED | E-18.2.2-027, E-18.2.2-028 |

**Veredicto del pilar:** El ReconcilerDaemon dispone de dos vectores de recuperación relacionados con tareas y materialización (Vector 1 y Vector 2), además de un mecanismo separado de barrido de estados FSM documentales (Vector 3). Ninguno resuelve el escenario de efecto externo incierto. Los 4 componentes operan sin coordinación explícita (hipótesis de condiciones de carrera, no finding). La convergencia global NO está DEMOSTRADA (solo game_day_1 existe, no prueba efecto incierto).

### Pilar 5 — Mecanismos 18.1 (Intocables)

| Elemento | Estado | Evidencia |
|---|---|---|
| CoordinationPrimitives | PRESENT — behavior observed | E-18.2.2-018, E-18.2.2-019 |
| ShutdownMechanismPort + CoordinatedShutdownMechanism | PRESENT — behavior observed | E-18.2.2-018 |
| CancellationToken + TaskOutcome | PRESENT — behavior observed | E-18.2.2-039 |
| AdmissionMechanismPort + SequentialAdmissionMechanism | PRESENT — behavior observed | HITO_18.2.0 v1.3.0 |
| BackpressureMechanismPort + SequentialBackpressureMechanism | PRESENT — behavior observed | HITO_18.2.0 v1.3.0 |

**Veredicto del pilar:** CONTRATOS Y MECANISMOS CON ESTADO FROZEN EN 18.1; NO SE REABREN EN ESTE HITO. La presencia y el congelamiento previo de estos mecanismos no constituyen una nueva certificación funcional en este HITO. 18.2 no debe modificar semántica ni contratos de 18.1 sin la decisión y trazabilidad correspondientes (NADR-F18-02 §5.4 R15).

### Pilar 6 — Durabilidad & Write-Policy (DC-08)

| Elemento | Estado | Evidencia |
|---|---|---|
| SQLite WAL + NORMAL (configuración) | OBSERVADO | E-18.2.2-014, E-18.2.2-015 |
| synchronous=FULL | ABSENT IN AUDITED SCOPE | E-18.2.2-016 |
| fsync en execution plane | ABSENT IN AUDITED SCOPE | E-18.2.2-021 |
| WAL checkpoint TRUNCATE | PRESENT — behavior observed | E-18.2.2-017 |
| Durabilidad ante crash de proceso (semántica documentada) | EVIDENCIA DOCUMENTAL | Documentación oficial SQLite |
| Durabilidad ante crash de proceso (comportamiento empírico) | NOT EMPIRICALLY VALIDATED | E-18.2.2-020, E-18.2.2-037 |
| Durabilidad ante SIGKILL | DEMOSTRADO para escenario game_day_1 (harness operativo); NO DEMOSTRADO para crash post-efecto/pre-journal ni power loss. No hay prueba automatizada dedicada en tests/ | E-18.2.2-020, E-18.2.2-028, E-18.2.2-037 |
| Durabilidad ante power loss | NOT EMPIRICALLY VALIDATED | E-18.2.2-016, E-18.2.2-021 |
| Signal handlers (SIGINT, SIGTERM) | PRESENT — behavior observed | E-18.2.2-019 |
| Signal handler (SIGKILL) | ABSENT (imposible por diseño de SO) | E-18.2.2-020 |

**Veredicto del pilar:** Write-policy OBSERVADA (WAL + NORMAL + busy_timeout). Semántica de durabilidad según documentación oficial SQLite es EVIDENCIA DOCUMENTAL. Comportamiento empírico ante cada escenario de fallo NOT EMPIRICALLY VALIDATED. La elección entre NORMAL y FULL debe partir del modelo de fallos requerido por la arquitectura, no de la idea de que "más sincronización siempre es mejor". El Maestro NO menciona fsync ni synchronous=FULL; la elección depende del modelo de fallos que DC-08d decida. La ausencia de fsync explícito o synchronous=FULL NO constituye por sí misma una violación contractual demostrada; es una incertidumbre de durabilidad frente al modelo de fallos requerido.

---

## 14. GAPS CONSOLIDADOS

**Criterio de severidad aplicado:** P1 se asigna cuando el gap impide demostrar una propiedad obligatoria de INV-JOURNAL (idempotent apply del resultado externo, o ventana de duplicación medida). P2 se asigna cuando el gap es un hecho observado cuya adecuación al contrato depende de decisiones abiertas (DC-08) o cuando la evidencia no demuestra una violación sino una incertidumbre.

| GAP | Severidad | Categoría | Descripción | Evidencia primaria | Evidencia de soporte | Autoridad normativa | Cadena de trazabilidad | Fase destino | Estado |
|---|---|---|---|---|---|---|---|---|---|
| GAP-18.2.2-01 | P1 | Garantía requerida no demostrada | Resolución de efectos externos inciertos en recuperación. El reconciler no distingue "efecto no iniciado" de "efecto iniciado pero no registrado". La secuencia observada permite un escenario de duplicación de efectos externos cuando el proveedor completa la operación y el proceso cae antes de registrar el resultado. La frecuencia, las condiciones exactas y la posibilidad de recuperación alternativa requieren validación empírica. | E-18.2.2-007, E-18.2.2-008 | E-18.2.2-005 | INV-JOURNAL (ADR_F18_MASTER §5.1): "idempotent apply y ventana de duplicación acotada y medida" | E-007/008 → INV-JOURNAL §5.1 → reconciler no distingue efecto incierto → re-ejecución ciega → idempotent apply del resultado externo no demostrado → P1 | 18.2 (DC-08b, Board decision) | OPEN |
| GAP-18.2.2-02 | P2 | Hecho observado, decisión abierta | Código cliente sin mecanismos de idempotencia en frontera LLM. Búsqueda exhaustiva en código cliente → 0 resultados. Capacidades de deduplicación y consulta del proveedor externo pendientes de verificación. Una reejecución puede generar una segunda operación y un coste adicional, salvo que el proveedor aplique deduplicación efectiva; esta capacidad no ha sido verificada. | E-18.2.2-004, E-18.2.2-013 | — | INV-JOURNAL §5.1: "El mecanismo concreto permanece abierto a DC-08" | E-013 → mecanismo abierto a DC-08 → hecho observado, no incumplimiento → P2 | 18.2 (DC-08b, Board decision) | OPEN |
| GAP-18.2.2-03 | P2 | Incertidumbre de durabilidad | Incertidumbre de durabilidad frente al modelo de fallos requerido. La configuración observada es WAL + synchronous=NORMAL. No se encontró synchronous=FULL ni llamadas explícitas a fsync en el execution plane. La semántica documentada de SQLite es EVIDENCIA DOCUMENTAL. El comportamiento empírico ante power loss NO está DEMOSTRADO. El Maestro no menciona fsync ni synchronous=FULL; la elección depende del modelo de fallos que DC-08d decida. | E-18.2.2-016, E-18.2.2-021 | — | INV-JOURNAL §5.1: "recuperable tras crash". DC-08 §8.2: criterio es "Decisión documentada" | E-016/021 → configuración observada → modelo de fallos abierto a DC-08d → incertidumbre, no incumplimiento → P2 | 18.2 (DC-08d, Board decision) | OPEN |
| GAP-18.2.2-04 | P1 | Garantía requerida no demostrada | Telemetría sin capacidad de medición de duplicación. Se descompone en 4 aspectos: (1) Medición del intervalo observable cliente execute()→append_wal(): sin instrumentación (E-030). (2) Identificación de intentos y reejecuciones: sin campos retry/attempt/replay en ProductionTelemetryEvent (E-033). (3) Observabilidad del resultado del proveedor: no verificable desde el repositorio. (4) Tasa de duplicación observada: no medible sin los 3 anteriores. | E-18.2.2-030, E-18.2.2-033 | — | INV-JOURNAL §5.1: "ventana de duplicación acotada y medida" | E-030/033 → INV-JOURNAL "ventana medida" → sin instrumentación ni campos retry → no se puede medir → P1 | 18.2 (DC-08c, Board decision) | OPEN |
| GAP-18.2.2-05 | P2 | Cobertura de validación insuficiente | Cobertura de validación incompleta. game_day_1 ejecuta kill real (SIGKILL vía Docker) pero NO prueba el caso crítico de crash post-effect/pre-journal con efecto realmente ocurrido. test_fencing.py vacío (0 bytes). | E-18.2.2-027, E-18.2.2-028, E-18.2.2-036, E-18.2.2-037 | — | Validación empírica (Gate 4) | E-027/028/036/037 → game_day_1 no prueba efecto incierto → test_fencing.py vacío → cobertura insuficiente → P2 | 18.2 (Gate 4) | OPEN |

**Resumen de severidades:** 2 P1 (GAP-18.2.2-01, GAP-18.2.2-04) + 3 P2 (GAP-18.2.2-02, GAP-18.2.2-03, GAP-18.2.2-05).

**Nota sobre E-004 y E-013:** Ambos describen la ausencia de mecanismos en el código cliente auditado. E-004 (búsqueda de fencing externo) y E-013 (búsqueda de idempotencia) son hechos observados de ausencia en el alcance auditado, no incumplimientos de autoridad congelada (el Maestro deja el mecanismo abierto a DC-08). Ambos se clasifican P2 y respaldan GAP-18.2.2-02.

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-18.2.2-A | "El execution plane tiene fencing completo que previene split-brain y duplicación." | RECHAZADA | E-18.2.2-001, E-18.2.2-002, E-18.2.2-004 | DB/SQL fencing y epoch fencing DEMOSTRADOS. External-effect fencing PARCIAL. Duplicate-effect prevention NOT EMPIRICALLY VALIDATED. |
| H-18.2.2-B | "El reconciler maneja todos los escenarios de recovery." | RECHAZADA | E-18.2.2-006, E-18.2.2-007, E-18.2.2-008 | Reconciler maneja Vector 1 (zombie puro) y Vector 2 (CQRS desync), pero NO maneja escenario de efecto incierto (INTENT/lease sin GENERATED). |
| H-18.2.2-C | "El código cliente implementa idempotencia en frontera LLM." | RECHAZADA | E-18.2.2-013 | Búsqueda exhaustiva en código cliente → 0 resultados. Capacidades del proveedor externo NO DEMOSTRADAS. |
| H-18.2.2-D | "El execution plane usa synchronous=FULL o fsync para garantizar durabilidad." | RECHAZADA | E-18.2.2-016, E-18.2.2-021 | synchronous=FULL NO existe en el código auditado. fsync solo se usa en corpus/AST, no en execution plane. NOTA: El Maestro no exige FULL; la elección depende del modelo de fallos que DC-08d decida. |
| H-18.2.2-E | "La telemetría permite medir la tasa de duplicación en producción." | RECHAZADA | E-18.2.2-033 | ProductionTelemetryEvent carece de campos retry_count, attempt_number, is_replay. No se puede distinguir primera ejecución de re-ejecución. |
| H-18.2.2-F | "game_day_1 valida convergencia global bajo todos los escenarios de fallo." | RECHAZADA | E-18.2.2-027, E-18.2.2-028 | game_day_1 existe y ejecuta kill real, pero NO prueba el caso crítico de crash post-effect/pre-journal con efecto realmente ocurrido. |
| H-18.2.2-G | "test_fencing.py existe y valida fencing empíricamente." | RECHAZADA | E-18.2.2-036 | test_fencing.py existe pero está VACÍO (0 bytes). Es un placeholder sin implementar. |
| H-18.2.2-H | "Los 4 componentes de recovery coordinan entre sí." | NO DEMOSTRADA | E-18.2.2-026 | Los 4 componentes son daemons independientes sin coordinación explícita. La ausencia de un coordinador explícito no prueba ni descarta coordinación efectiva ni demuestra una condición de carrera. Requiere identificación de operaciones concurrentes, intercalaciones y efecto observable. |
| H-18.2.2-I | "INV-JOURNAL está completamente satisfecho." | RECHAZADA | E-18.2.2-007, E-18.2.2-008, E-18.2.2-013 | INV-JOURNAL NO está completamente satisfecho. El lease constituye un mecanismo observado de intención durable; su recuperabilidad estructural bajo crash no está demostrada empíricamente. La segunda cláusula (aplicación idempotente del resultado) no está garantizada para el efecto externo. La ventana de duplicación no está formalmente acotada ni medida. |
| H-18.2.2-J | "CircuitBreaker warm-up es ~60s como estimaba HITO_18.2.1." | RECHAZADA | E-18.2.2-042 | La configuración observada establece `recovery_timeout=30s`. El tiempo efectivo de recuperación depende de la ejecución y del resultado de la sonda; no fue medido empíricamente. Por tanto, la estimación previa de ~60s no queda sustentada por la configuración observada. |
| H-18.2.2-K | "Vector 3 del reconciler maneja efectos inciertos." | RECHAZADA | E-18.2.2-022 | Vector 3 (_sweep_fsm_stalls) opera sobre documentos FSM, no sobre tasks. No es un tercer vector para efectos inciertos. |

**Hipótesis abiertas registradas en OBS (no en matriz H):**

| ID | Hipótesis | Estado | Evidencia | Implicación |
|---|---|---|---|---|
| OBS-18.2.2-04 | "Los 4 componentes de recovery pueden generar condiciones de carrera." | OPEN (hipótesis, no finding) | E-18.2.2-026 | Compartir una base de datos no demuestra por sí solo que haya una carrera efectiva. Hace falta identificar las operaciones concurrentes, sus intercalaciones y el efecto observable. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué garantías reales de ejecución durable existen en el execution plane?

**Estado actual verificado:**

1. Mecanismo de intención persistida via task lease en chunk_tasks (PROCESSING + execution_id + lease_owner + lease_expires_at) OBSERVADO (E-18.2.2-001, E-18.2.2-002). La intención persistida está OBSERVADA; la recuperabilidad estructural bajo crash NO está demostrada empíricamente.
2. Idempotencia por operación concreta OBSERVADA en append_wal, upsert_projection, reconciliation commands, FSM transitions (E-18.2.2-009 a E-18.2.2-012). NOTA: Idempotencia de persistencia local, NO idempotencia del efecto externo.
3. DB/SQL fencing DEMOSTRADO (epoch verification + optimistic locking) (E-18.2.2-003, HITO_18.2.1).
4. Reconciler epoch fencing DEMOSTRADO (rechazo de comandos obsoletos) (E-18.2.2-003).
5. External-effect fencing PARCIAL (check post-execute) (E-18.2.2-001, E-18.2.2-002).
6. Duplicate-effect prevention NOT EMPIRICALLY VALIDATED (código cliente sin idempotencia; capacidades del proveedor pendientes) (E-18.2.2-004, E-18.2.2-013).
7. Estado pre-effecto en event journal PARTIAL (ausente en EventLifecycle) (E-18.2.2-007).
8. Lógica de verificación con proveedor ABSENT IN AUDITED SCOPE (E-18.2.2-008).
9. Write-policy OBSERVADA (WAL + NORMAL + busy_timeout) (E-18.2.2-014, E-18.2.2-015).
10. synchronous=FULL ABSENT IN AUDITED SCOPE (E-18.2.2-016). NOTA: El Maestro no exige FULL; la elección depende del modelo de fallos que DC-08d decida.
11. Durabilidad ante crash de proceso: EVIDENCIA DOCUMENTAL (documentación SQLite). Comportamiento empírico NOT EMPIRICALLY VALIDATED.
12. Durabilidad ante SIGKILL: DEMOSTRADO para escenario game_day_1; NO DEMOSTRADO para crash post-efecto/pre-journal ni power loss.

**Respuesta forense:**

El execution plane tiene garantías parciales de ejecución durable. El lease en chunk_tasks constituye un mecanismo observado de intención durable; su recuperabilidad estructural bajo crash y su suficiencia para INV-JOURNAL no están demostradas empíricamente. La idempotencia existe por operación concreta, pero el efecto externo (LLM call) NO tiene idempotencia garantizada. El DB/SQL fencing y el reconciler epoch fencing están DEMOSTRADOS. El external-effect fencing es PARCIAL. El duplicate-effect prevention está NOT EMPIRICALLY VALIDATED. La write-policy es WAL+NORMAL, pero el comportamiento empírico ante cada escenario de fallo requiere validación.

**Implicación:**

INV-JOURNAL NO está completamente satisfecho. La brecha principal es la ausencia de resolución de efectos inciertos en la recuperación. DC-08b requiere decisión del Board; el HITO proporciona evidencia para esa decisión. DC-08a, DC-08c y DC-08d son aspectos complementarios de DC-08 que pueden resolverse en el mismo ADR o diferirse según su complejidad.

### 16.2 ¿Qué gaps quedan frente a INV-JOURNAL?

**Estado actual verificado:**

1. GAP-18.2.2-01 (P1): Resolución de efectos externos inciertos en recuperación.
2. GAP-18.2.2-02 (P2): Código cliente sin mecanismos de idempotencia en frontera LLM.
3. GAP-18.2.2-03 (P2): Incertidumbre de durabilidad frente al modelo de fallos requerido.
4. GAP-18.2.2-04 (P1): Telemetría sin capacidad de medición de duplicación.
5. GAP-18.2.2-05 (P2): Cobertura de validación incompleta.

**Respuesta forense:**

Cinco gaps consolidados. Dos son P1 (GAP-18.2.2-01, GAP-18.2.2-04), tres son P2 (GAP-18.2.2-02, GAP-18.2.2-03, GAP-18.2.2-05). El gap de resolución de efectos inciertos (GAP-18.2.2-01) es el problema arquitectónico central que debe resolverse en DC-08b.

**Implicación:**

DC-08b (política de efectos inciertos) requiere decisión del Board con la evidencia de este HITO. DC-08c (telemetría) requiere decisión del Board. DC-08d (durabilidad) requiere decisión del Board. El gap P2 de validación requiere Gate 4.

### 16.3 ¿Qué activos pueden reutilizarse sin reinvención?

**Estado actual verificado:**

La mayoría de los componentes auditados son PRESENT — behavior observed (recovery machinery, fencing SQL, journal, projection, mecanismos 18.1). Cuatro componentes están PARTIAL — contract coverage incomplete (LLMWorkerDaemon._process_task, ReconcilerDaemon, EventLifecycle enum, ProductionTelemetryEvent). Dos componentes son ABSENT IN AUDITED SCOPE (idempotencia en código cliente). Uno es NOT EMPIRICALLY VALIDATED (capacidades del proveedor). Tres componentes están TO BE VERIFIED (ProfileStore, CircuitBreaker, SQLiteTelemetryGateway). test_fencing.py es PRESENT — EMPTY PLACEHOLDER.

**Respuesta forense (INFERENCE):**

INFERENCE: La evidencia observada sugiere que la mayoría de los componentes existentes son funcionales a nivel de API y podrían reutilizarse sin reinvención completa. Los componentes PARTIAL podrían requerir extensiones o mejoras puntuales.

**Recomendación (RECOMMENDATION):**

RECOMMENDATION: Basado en la evidencia observada, se recomienda aplicar Reuse Before Invent y extender los componentes existentes en lugar de reinventar. Sin embargo, el alcance exacto de las extensiones requeridas dependerá de las decisiones de DC-08b, DC-08c y DC-08d.

**Implicación:**

18.2 podría ser una subfase de cierre de gaps y validación empírica, no de construcción. Las decisiones finales sobre el alcance de las extensiones corresponden al ADR_F18.2.

### 16.4 ¿Qué mecanismos de recovery existen y cuáles faltan?

**Estado actual verificado:**

1. Vector 1 (zombie puro → PENDING): PRESENT (E-18.2.2-006, E-18.2.2-022).
2. Vector 2 (CQRS desync → rematerializar): PRESENT (E-18.2.2-006, E-18.2.2-022).
3. Vector 3 (barrido FSM documental): PRESENT (E-18.2.2-022).
4. Vector para efectos inciertos (INTENT/lease sin GENERATED): ABSENT IN AUDITED SCOPE (E-18.2.2-007, E-18.2.2-008).
5. Coordinación entre 4 componentes: NOT EMPIRICALLY VALIDATED (E-18.2.2-026).

**Respuesta forense:**

El ReconcilerDaemon dispone de dos vectores de recuperación relacionados con tareas y materialización (Vector 1 y Vector 2), además de un mecanismo separado de barrido de estados FSM documentales (Vector 3). Ninguno resuelve el escenario de efecto externo incierto. Los 4 componentes de recovery operan sin coordinación explícita (hipótesis de condiciones de carrera, no finding).

**Implicación:**

DC-08b debe decidir la política de resolución de efectos inciertos. Las alternativas incluyen (no excluyentes): (A) registro de intención en event journal con vector de recuperación, (B) cuarentena para efectos inciertos, (C) verificación con proveedor si disponible, (D) aceptación explícita de ventana residual como ACCEPTED_LIMITATION, (E) combinación de las anteriores.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| DC-08a | Intent-First Journal (registro de intención en event journal) | E-18.2.2-007, GAP-18.2.2-01 | Registro de intención pre-effecto en EventLifecycle no implementado. Existe lease durable en control plane. Necesidad de journal adicional pendiente de DC-08. | 18.2 (alternativa a investigar) |
| DC-08b | Política de efectos inciertos | E-18.2.2-007, E-18.2.2-008, E-18.2.2-013, GAP-18.2.2-01, GAP-18.2.2-02 | Ausente (reconciler sin vector para efectos inciertos) | 18.2 (Board decision) |
| DC-08c | Telemetría de duplicación | E-18.2.2-030, E-18.2.2-033, GAP-18.2.2-04 | Ausente (ProductionTelemetryEvent sin campos de retry) | 18.2 (Board decision) |
| DC-08d | Durabilidad ante power loss | E-18.2.2-016, E-18.2.2-021, GAP-18.2.2-03 | Configuración observada WAL + NORMAL. FULL no configurado. Adecuación al modelo de fallos pendiente de decisión. | 18.2 (Board decision) |
| DF-24 | Persistencia de CircuitBreaker | E-18.2.2-042, OBS-18.2.2-02 | Ausente (in-memory, configuración con recovery_timeout=30s, tiempo efectivo no medido) | 18.2 (subsumido en DC-08, Board decision) |
| DF-34 | Persistencia de ProfileStore | E-18.2.2-044 | Ausente (in-memory, sin benchmark de CPU) | 18.2 (trigger propio: cuantificación de re-inferencia) |

> **Nota de descomposición de DC-08:** DC-08a, DC-08b, DC-08c y DC-08d son una descomposición propuesta del DC-08 único definido en ADR_F18_MASTER §8.2 ("Write-policy SQLite + mecanismo de journal de INV-JOURNAL"), para facilitar la decisión del ADR_F18.2. No son DCs independientes en el registro canónico del Maestro. El ADR_F18.2 debe resolver DC-08 como un todo, pudiendo adoptar decisiones diferenciadas para cada aspecto de la descomposición.

> **Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos. Un mecanismo candidato no implementado no equivale a una garantía normativa incumplida; la adecuación al contrato depende de la decisión del Board.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Escenario de duplicación de efectos externos | Crash post-effect/pre-journal permite re-ejecución por reconciler Vector 1 cuando el proveedor completó la operación | Alto (FinOps) | E-18.2.2-007, E-18.2.2-008, E-18.2.2-013, GAP-18.2.2-01, GAP-18.2.2-02 |
| Tormenta de reintentos tras restart | Si CircuitBreaker pierde estado OPEN y el proveedor sigue caído, el sistema reintentará hasta re-abrir | Medio (FinOps + disponibilidad) | E-18.2.2-042, OBS-18.2.2-02 |
| Pérdida de perfiles documentales | Crash antes de completar pipeline pierde perfiles inferidos | Bajo/Medio (depende de coste de re-inferencia, no cuantificado) | E-18.2.2-044 |
| Convergencia no demostrada | La maquinaria de recovery existe pero su convergencia global no está validada empíricamente | Medio (confiabilidad) | E-18.2.2-027, E-18.2.2-028, GAP-18.2.2-05 |
| Cobertura de fencing no demostrada | test_fencing.py vacío. Seguridad empírica de fencing no validada | Medio | E-18.2.2-036, GAP-18.2.2-05 |
| Condiciones de carrera entre 4 componentes de recovery | Los 4 componentes operan sin coordinación explícita (hipótesis, no finding) | Medio (confiabilidad) | E-18.2.2-026, OBS-18.2.2-04 |
| Pérdida de WAL en power loss | synchronous=NORMAL no garantiza flush a disco tras pérdida de energía (EVIDENCIA DOCUMENTAL) | Medio (durabilidad) | E-18.2.2-016, E-18.2.2-021, GAP-18.2.2-03 |
| Efecto externo tras pérdida de lease | El efecto externo puede producirse antes de que el worker compruebe que perdió autoridad | Medio (FinOps) | E-18.2.2-001, E-18.2.2-002, E-18.2.2-004 |
| Sobreingeniería de recovery | Riesgo de construir un framework genérico cuando la maquinaria existente es suficiente | Medio (deuda técnica, YAGNI) | E-18.2.2-022 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR_F18.2 deberá responder:

1. **¿Qué política de resolución de efectos inciertos adoptar?** (DC-08b, Board decision)
   - Alternativas NO EXCLUYENTES:
     - (A) Registro de intención en event journal con vector de recuperación (alternativa a investigar; la brecha puede resolverse sin extender EventLifecycle)
     - (B) Cuarentena para efectos inciertos
     - (C) Verificación con proveedor si disponible
     - (D) Aceptación explícita de ventana residual como ACCEPTED_LIMITATION
     - (E) Combinación de las anteriores
   - La combinación apropiada depende de las garantías exigidas y de las capacidades verificadas del proveedor.

2. **¿Qué mecanismo de telemetría implementar para medir tasa de duplicación?** (DC-08c)
   - Aspectos a resolver por separado:
     - Medición del intervalo observable cliente execute()→append_wal()
     - Identificación de intentos y reejecuciones (campos retry/attempt/replay)
     - Observabilidad del resultado del proveedor, cuando la interfaz lo permita
     - Tasa de duplicación observada, con denominador, ventana temporal y limitaciones

3. **¿Qué nivel de durabilidad requerir para power loss?** (DC-08d)
   - Alternativas:
     - (A) Aceptar ventana de power loss como ACCEPTED_LIMITATION
     - (B) Cambiar a synchronous=FULL con medición de impacto de latencia
     - (C) Requerir hardware con battery-backed write cache
   - La elección debe partir del modelo de fallos requerido por la arquitectura, no de la idea de que "más sincronización siempre es mejor".

4. **¿Qué escenarios de crash debe cubrir el chaos harness ampliado en Gate 4?** (GAP-18.2.2-05)
   - Escenarios mínimos:
     - Crash post-effect/pre-journal con efecto realmente ocurrido en proveedor
     - Múltiples workers compitiendo por tareas
     - Pérdida de lease durante efecto externo
     - Efectos inciertos (INTENT/lease sin GENERATED)
   - Cada escenario debe especificar: qué se mata, cuándo se mata, qué se verifica tras reinicio, y qué constituye convergencia.

5. **¿Cómo implementar test_fencing.py para validar fencing empíricamente?** (GAP-18.2.2-05)
   - Tests mínimos:
     - DB/SQL fencing: worker zombi bloqueado por optimistic locking
     - Reconciler epoch fencing: comandos obsoletos rechazados
     - External-effect fencing: verificar comportamiento con mock
   - NOTA: Una prueba con mock demuestra el comportamiento de la aplicación bajo las condiciones simuladas; no demuestra una garantía universal del proveedor externo.

6. **¿Cómo coordinar los 4 componentes de recovery para evitar condiciones de carrera?** (OBS-18.2.2-04)
   - Alternativas:
     - (A) Mantener independencia (aceptar riesgo de condiciones de carrera)
     - (B) Añadir orquestador explícito
     - (C) Documentar contratos de no-interferencia
   - NOTA: Compartir una base de datos no demuestra por sí solo que haya una carrera efectiva. Hace falta identificar las operaciones concurrentes, sus intercalaciones y el efecto observable.

---

## 21. CIERRE DEL HITO 18.2.2

Este HITO confirma que el execution plane tiene garantías parciales de ejecución durable. El DB/SQL fencing y el reconciler epoch fencing están DEMOSTRADOS. El lease en chunk_tasks constituye un mecanismo observado de intención durable; su recuperabilidad estructural bajo crash y su suficiencia para INV-JOURNAL no están demostradas empíricamente. La idempotencia existe por operación concreta, pero el efecto externo (LLM call) NO tiene idempotencia garantizada. La brecha principal es la ausencia de resolución de efectos inciertos en la recuperación, lo cual permite un escenario de duplicación de efectos externos. Se identifican cinco gaps consolidados (dos P1, tres P2). El gap de resolución de efectos inciertos es el problema arquitectónico central que debe resolverse en DC-08b.

**Estado del HITO:** FROZEN v1.4.1

**Condición de cierre cumplida:**

- [x] Metadata completa y consistente.
- [x] Changelog actualizado a la versión v1.4.1.
- [x] Versión única v1.4.1 en todo el documento (portada, resumen, changelog, cierre, cadena de gobernanza).
- [x] Límite epistemológico declarado con seis niveles (OBSERVADO, EVIDENCIA DOCUMENTAL, DEMOSTRADO, NO DEMOSTRADO, DECISION CANDIDATE, ESTIMACIÓN INDIRECTA).
- [x] Nota sobre SIGKILL delimitado por escenario.
- [x] Convención de IDs normalizados declarada (E-18.2.2-NNN).
- [x] Alcance auditado con estado real por superficie (sin porcentaje inflado).
- [x] Fuentes de evidencia listadas y clasificadas.
- [x] Mapa de flujos observados (Flujo A, B, C).
- [x] Inventario de dimensiones/componentes completo (26 componentes).
- [x] Taxonomía de fencing en cuatro categorías (DB/SQL, Reconciler Epoch, External-Effect, Duplicate-Effect Prevention).
- [x] Separación de intención durable en control plane (lease) vs event journal (EventLifecycle).
- [x] Sección 7 (Matriz Observed/Required/Decision) presente.
- [x] Todas las evidencias tienen ID estable (E-18.2.2-001 a E-18.2.2-045).
- [x] Todas las evidencias tienen severidad clasificada.
- [x] E-004 y E-013 unificados a P2 con justificación normativa.
- [x] Consecuencias condicionales aplicadas (E-013: "puede generar coste adicional salvo que el proveedor aplique deduplicación efectiva").
- [x] INV-JOURNAL reformulado como mecanismo observado sin recuperabilidad demostrada.
- [x] Criterio de severidad explícito en §14 (P1 = garantía requerida no demostrada; P2 = hecho observado o incertidumbre).
- [x] Telemetría descompuesta en 4 aspectos separados (GAP-18.2.2-04).
- [x] GAP-18.2.2-03 reformulado como incertidumbre de durabilidad, no incumplimiento.
- [x] Conclusiones de reutilización etiquetadas como INFERENCE/RECOMMENDATION.
- [x] Observaciones complementarias documentadas (5 OBS).
- [x] Matriz de triaje completa (26 componentes clasificados con categorías descriptivas, no prescriptivas).
- [x] Matriz de pilares completa (6 pilares).
- [x] Todos los gaps tienen evidencia vinculada (5 gaps).
- [x] Todos los gaps tienen fase destino explícita.
- [x] 11 hipótesis evaluadas en matriz H: 10 rechazadas y 1 no demostrada (H-18.2.2-H).
- [x] Hipótesis abiertas registradas en OBS (1 hipótesis: OBS-18.2.2-04).
- [x] Respuestas a preguntas del mandato completas (4 preguntas).
- [x] Matriz de trazabilidad DC completa (6 DCs).
- [x] Apéndice de riesgos completo (9 riesgos).
- [x] Preguntas para ADR completas (6 preguntas, con alternativas NO EXCLUYENTES para DC-08b).
- [x] Contradicciones con HITOs previos documentadas y corregidas.
- [x] Todos los IDs E, GAP, OBS, H son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.
- [x] Correcciones REV-01, REV-02, REV-03 aplicadas tras auditoría final.
- [x] Ajustes editoriales de numeración (§8, §9, §17) documentados.
- [x] Frase de hipótesis ajustada a "10 rechazadas y 1 no demostrada".
- [x] Vector 3 reformulado como mecanismo separado de barrido FSM documental.
- [x] Matriz DC reformulada: mecanismo candidato no implementado ≠ garantía normativa incumplida.
- [x] CircuitBreaker warm-up reformulado como configuración observada, no duración empírica.

**Nota editorial sobre numeración:** Las secciones §8, §9 y §17 no aparecen explícitamente en este documento. Para Forensic Discovery de execution plane, su contenido queda incorporado en §7 (Matriz Observed/Required/Decision absorbe §8), §10 (Registro de Evidencia Forense absorbe §9) y §18 (Matriz de Trazabilidad DC absorbe §17). Esta omisión es editorial y no afecta la integridad del contenido ni la trazabilidad normativa.

**Verificación de cadena de gobernanza:**

ADR_F18_MASTER FROZEN → ADR_F18.1 FROZEN → NADR-F18-01 FROZEN → NADR-F18-02 FROZEN → HITO_18.2.0 v1.3.0 FROZEN → HITO_18.2.1 v1.2.0 FROZEN → **HITO_18.2.2 v1.4.1 FROZEN** → ADR_F18.2 v3.0.0 → NADR-F18-03 → PHASE_18.2_EXECUTION_PLAN

**Contradicciones con HITOs previos:**

- HITO_18.2.1 v1.2.0 estimaba warm-up de CircuitBreaker en ~60s. Este HITO corrige: la configuración observada establece `recovery_timeout=30s`; el tiempo efectivo de recuperación depende de la ejecución y del resultado de la sonda, no fue medido empíricamente (OBS-18.2.2-02). No es contradicción; es refinamiento con evidencia más precisa.
- HITO_18.2.1 v1.2.0 afirmaba que test_fencing.py no existe. Este HITO corrige: test_fencing.py existe pero está VACÍO (0 bytes). No es contradicción; es corrección de hecho observable.
- HITO_18.2.0 v1.3.0 identificó GAP-18.2.0-01 como P1. Este HITO lo reclasifica como GAP-18.2.2-01 P1 tras auditoría forense completa que confirma el escenario de duplicación de efectos externos. No es contradicción; es refinamiento con evidencia más profunda.
- HITO_18.2.1 v1.2.0 clasificó durabilidad ante crash de proceso como "OBSERVADO (esperado según documentación SQLite)". Este HITO corrige: la configuración es OBSERVADA; la semántica documentada es EVIDENCIA DOCUMENTAL; el comportamiento empírico es NOT EMPIRICALLY VALIDATED. No es contradicción; es refinamiento epistemológico.
- HITO_18.2.1 v1.2.0 clasificó ventana ~1ms como OBSERVADO. Este HITO corrige: es ESTIMACIÓN INDIRECTA HEREDADA (resta de latencia mock), NO medición directa. No es contradicción; es refinamiento epistemológico.

**Decision Candidates generados:**

- DC-08a: Intent-First Journal (registro de intención en event journal) — alternativa a investigar
- DC-08b: Política de efectos inciertos (Board decision) — alternativas NO EXCLUYENTES
- DC-08c: Telemetría de duplicación (Board decision)
- DC-08d: Durabilidad ante power loss (Board decision)

**Siguiente paso recomendado:**

1. ~~Auditoría externa~~ (completada, correcciones aplicadas).
2. ~~Congelar como FROZEN~~ (este documento es v1.4.1 FROZEN).
3. Decidir DC-08a, DC-08b, DC-08c, DC-08d en ADR_F18.2 v3.0.0 con evidencia de este HITO.
4. Congelar ADR_F18.2 v3.0.0 FROZEN.
5. Proceder con NADR-F18-03 y PHASE_18.2_EXECUTION_PLAN.

---

**Nota de Gobernanza:** Este HITO es evidencia forense pura. No propone código de producción. No materializa decisiones de implementación. No prescribe soluciones de diseño. No acepta unilateralmente limitaciones que contradigan invariantes congelados. Su función es servir como insumo para ADR_F18.2, NADR-F18-03 y PHASE_18.2_EXECUTION_PLAN. La versión v1.4.1 está FROZEN y lista para consumo por el Architecture Board.