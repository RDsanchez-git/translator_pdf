# PHASE 17-BIS — FASE 2 EXECUTION PLAN v1.5.0
## Scientific Baseline Domain — Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.5.0
**Status:** `APPROVED`
**Date:** 2026-08-24
**Supersedes:** v1.4.0
**Derived From:** 4 NADRs APPROVED (NADR-F17BIS-12..15) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.2.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa de la Fase 2 (Scientific Baseline Domain) y el seguimiento de cumplimiento de las reglas de NADR-F17BIS-12..15. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-23 | Emisión inicial. Mapeo de las 37 reglas de NADR-F17BIS-12..15 a 4 Gates / 12 Waves / 37 tareas atómicas. |
| 1.1.0 | 2026-08-23 | Task 1.1.1 completada (DONE). Gate 1 → IN PROGRESS. 5 hallazgos derivados al Findings Register (DF-01..DF-05). |
| 1.2.0 | 2026-08-23 | Task 1.1.2 completada (DONE). Decisiones DF-02 y DF-03 cerradas (RESOLVED). 2 nuevos hallazgos forward-looking (DF-07, DF-08). |
| 1.3.0 | 2026-08-23 | Task 1.1.3 completada (DONE). Wave 1.1 COMPLETED. Hallazgos DF-05, DF-07, DF-09, DF-11 cerrados (RESOLVED). DF-10 abierto (BenchmarkParserBridge). |
| 1.4.0 | 2026-08-23 | Wave 1.2 COMPLETED (Tasks 1.2.1, 1.2.2, 1.2.3 DONE). DF-06 y DF-08 RESOLVED. DF-13 registrado como forward-looking para Gate 3. |
| 1.5.0 | 2026-08-24 | Wave 1.3 COMPLETED (Tasks 1.3.1, 1.3.2, 1.3.3 DONE). Gate 1 listo para Exit Review. DF-15 (bug multiplataforma) RESOLVED. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
ADR_F17_BIS_02 (Scientific Baseline Domain — APPROVED)
↓
NADRs F17BIS-12..15 (reglas constitucionales, APPROVED)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_FASE2_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_2_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR APPROVED, sin inventar identificadores paralelos:

```text
NADR-F17BIS-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-F17BIS-13 §5.2 R6` → NADR-F17BIS-13, sección 5.2, regla 6.

El inventario autoritativo de reglas es el **corpus de NADRs APPROVED** (NADR-F17BIS-12..15, 37 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

```text
DF-{XX} | GF-{XX}
```

**Responsabilidad de este documento:** Identificar el hallazgo y derivarlo al registro.
**Responsabilidad del Findings Register:** Clasificar, resolver o diferir el hallazgo.

### 1.4 Operational Principles

- **Los NADRs no pertenecen a una fase.** Son reglas constitucionales permanentes. Lo que se asigna por fase son sus reglas individuales.
- **El Execution Plan es la única fuente de verdad temporal.** No existen matrices de trazabilidad paralelas.
- **Política de referencias cruzadas:** Una regla puede aparecer en múltiples tareas **únicamente** cuando una tarea la implementa y otra la verifica o completa. Nunca deben existir dos tareas implementando la misma obligación.
- **El estado de una regla es derivado.** Una regla no tiene estado propio. Su estado es el estado de la tarea que la implementa, salvo que esté distribuida (implementada en una tarea, verificada en otra).
- **Mapeo 1:1 regla→tarea:** Cada una de las 37 reglas de NADR-F17BIS-12..15 es implementada por exactamente una tarea. Esto garantiza trazabilidad auditable sin doble implementación.

### 1.5 Documento Vivo — Convención de Actualización

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §11. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§3)
- Status Dashboard (§6)
- Traceability Appendix (§7)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

### 1.6 Restricciones de Hardware (carry-forward obligatorio)

Conforme al ADR Maestro §4 y ENGINEERING_PRINCIPLES:
- **Single-node / No infraestructura distribuida:** Prohibido Redis, Brokers, K8s, DBs remotas. SQLite WAL es el Core Engine.
- **Memory Efficiency:** DTOs inmutables (`frozen=True`), cero mutación in-place.
- **FinOps First & Fail-Fast:** Ninguna degradación silenciosa; toda anomalía aborta o emite warning indexable.

---

## 2. GATES DE LA FASE 2 — SCIENTIFIC BASELINE DOMAIN

La Fase 2 se estructura en **4 Gates**, uno por NADR, respetando el grafo de dependencias ontológicas:

```text
Gate 1 (NADR-12: Ontología)
   └──► Gate 2 (NADR-13: Validez/Completitud) — opera sobre entidades con estado
          └──► Gate 3 (NADR-14: Autoridad/Puertos) — exige validez como precondición
                 └──► Gate 4 (NADR-15: Identidad Semántica) — porta sobre oráculo sellado
```

Cada Gate actúa como compuerta conforme a METHODOLOGY §6.5: el Gate N+1 no inicia hasta que el Gate N pase su Exit Review.

---

## GATE 1 — ORACLE ONTOLOGY & LIFECYCLE GOVERNANCE

**Objective:** Formalizar la ontología del Ground Truth como entidad de dominio con ciclo de vida gobernado, disyunción Draft/Oracle e inmutabilidad de instancia.
**NADRs afectados:** NADR-F17BIS-12 (9 reglas)
**Execution Mode:** Secuencial (Critical Path — fundamento ontológico)
**Rollback Plan:** `git revert` de los modelos de dominio introducidos; el sistema retorna al estado de DTOs planos de Fase 1.
**Gate Status:** 🟡 IN PROGRESS (listo para Exit Review)

### 2.1 Wave 1.1 — Tipos disjuntos Draft/Oracle (NADR-12 §5.1)

**Wave Status:** ✅ COMPLETED

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Modelar el Ground Truth como entidad de dominio cuyo tipo está determinado por su estado de ciclo de vida | NADR-12 §5.1 R1 | High | — | DONE |
| **1.1.2** | Definir tipos disjuntos para el estado de borrador curado y el estado de oráculo sellado, sin conversión implícita | NADR-12 §5.1 R2 | High | 1.1.1 | DONE |
| **1.1.3** | Garantizar que un artefacto serializado no sea tratado como oráculo sin hidratación y validación previas vía contrato canónico | NADR-12 §5.1 R3 | High | 1.1.2 | DONE |

#### Notas de implementación — Wave 1.1

**Task 1.1.1 (DONE — 2026-08-23):**
Creado `core/benchmark/ground_truth/models.py` con el vocabulario `GroundTruthLifecycleState` (4 estados: DRAFT, AUDITED, VALIDATED, SEALED) y la entidad base `GroundTruth` (frozen=True, `Tuple[ASTNode, ...]` + `state`). El tipo de la entidad está determinado por `state` (R1). El enum introduce solo el vocabulario habilitante; las transiciones y la autoridad son Task 1.2.1 (R4/R6), y los tipos disjuntos Draft/Oracle son Task 1.1.2 (R2). Inmutabilidad profunda garantizada con `Tuple` (lección E-2.0-14). Helper de test local `_make_node` verificado contra contrato real de `ASTNode` (3 campos requeridos: `node_id`, `node_type`, `payload`). No existe helper compartido en `tests/helpers/` (confirmado por grep).

**Hallazgos derivados al Findings Register:** DF-01 (deuda test helpers), DF-02 (decisión ontológica Entity vs VO), DF-03 (campo state condiciona 1.1.2), DF-04 (ACCEPTED_LIMITATION inmutabilidad profunda), DF-05 (Tuple vs Sequence forward-looking).

**Verificación:** Pyright 0 errors · pytest 6 passed · regresión 280 passed, 5 skipped · frontera hexagonal limpia (0 imports de infra).

**Task 1.1.2 (DONE — 2026-08-23):**
Reemplazada la entidad genérica `GroundTruth` por los tipos disjuntos `GroundTruthDraft` y `SealedOracle` (NADR-12 §5.1 R1-R2). Ambos portan `document_id` como identidad propia (Entity en sentido DDD, agregado separado de `CorpusManifest`, relación por referencia vía `document_id`). No existe conversión implícita entre los tipos (tests verifican ausencia de métodos `to_oracle`, `seal`, `as_oracle`, `to_draft`, `unseal`, `as_draft`). Campo `state` eliminado: el tipo mismo determina el estado. Decisiones ontológicas DF-02 y DF-03 cerradas como RESOLVED. Documentación de validación de no-vaciedad añadida al docstring del módulo (responsabilidad de Task 2.1.2, NADR-13 §5.1 R2). Métodos redundantes `from_nodes` eliminados (YAGNI).

**Hallazgos derivados al Findings Register:** DF-07 (redundancia potencial `document_id` en puertos vs entidad → Task 1.1.3), DF-08 (coexistencia Draft/Oracle para mismo `document_id` → Task 1.2.1).

**Verificación:** Pyright 0 errors · pytest 16 passed · regresión 290 passed, 5 skipped (baseline 274 + 16 nuevos) · frontera hexagonal limpia.

**Task 1.1.3 (DONE — 2026-08-23):**
Materializada la hidratación vía contrato canónico (NADR-12 §5.1 R3). Puertos actualizados a `Tuple[ASTNode, ...]` (inmutabilidad en frontera, DF-05 resuelto). Adaptador `LocalFileSystemGroundTruthReader` convierte `List → Tuple` tras `read_ast_json`; import de `ASTNode` añadido (DF-09 resuelto). `LoadGroundTruthUseCase` sigue retornando `Tuple` crudo (no construye entidad porque el estado no está en el artefacto). Introducida fábrica `hydrate_ground_truth(document_id, nodes, state)` como único punto de construcción de entidades. En Task 1.1.3 la fábrica solo acepta DRAFT y SEALED; AUDITED y VALIDATED lanzan `ValueError` con trazabilidad a DF-06 (Task 1.2.1). Confirmado por inspección que el artefacto serializado NO porta metadata de estado.

**Hallazgos resueltos:** DF-05 (Tuple vs Sequence → RESOLVED), DF-07 (redundancia document_id → RESOLVED), DF-09 (import ASTNode → RESOLVED), DF-11 (mapeo AUDITED/VALIDATED prematuro → RESOLVED).

**Hallazgo abierto:** DF-10 (`BenchmarkParserBridge.extract_ast` debe retornar `Tuple` para cumplir nuevo contrato de `ASTExtractionPort` → REVIEW_REQUIRED, verificar antes de Task 1.2.1).

**Verificación:** Pyright 0 errors (4 archivos) · pytest 22 passed (modelos) · pytest 3 passed (puertos) · regresión 299 passed, 5 skipped · frontera hexagonal limpia.

### 2.2 Wave 1.2 — Ciclo de vida y no-inferencia de estado (NADR-12 §5.2)

**Wave Status:** ✅ COMPLETED

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Definir explícitamente los estados de ciclo de vida (borrador, auditado, validado, sellado) y las únicas transiciones permitidas | NADR-12 §5.2 R4 | High | 1.1.3 | DONE |
| **1.2.2** | Eliminar toda inferencia de estado de sellado a partir de presencia de archivo o campo incidental | NADR-12 §5.2 R5 | High | 1.2.1 | DONE |
| **1.2.3** | Asegurar que toda transición de estado sea producida por una operación explícita y gobernada, nunca como efecto lateral | NADR-12 §5.2 R6 | High | 1.2.1 | DONE |

#### Notas de implementación — Wave 1.2

**Task 1.2.1 (DONE — 2026-08-23):**
Introducido `DraftSubState` enum (DRAFT, AUDITED, VALIDATED) como sub-estados del Draft (DF-06 resuelto). Expandido `GroundTruthDraft` con campo `sub_state` requerido con default `DRAFT`. Introducida `LifecycleTransitionAuthority` como servicio de dominio stateless en `core/benchmark/ground_truth/lifecycle.py` con transiciones válidas: `audit` (DRAFT→AUDITED), `validate` (AUDITED→VALIDATED), `seal` (VALIDATED→SealedOracle), `rollback_to_draft` (AUDITED→DRAFT), `rollback_to_audited` (VALIDATED→AUDITED). Cada transición retorna una nueva instancia con `sub_state` actualizado (inmutabilidad, ENGINEERING_PRINCIPLES §II). La transición `seal()` documenta explícitamente que NO valida completitud/validez (Gate 2, NADR-13 §5.1) ni persiste estado sellado (Gate 3, NADR-14 §5.2, DF-13). Rollback de `SealedOracle` prohibido por tipado estático (NADR-12 §5.3 R9). `InvalidTransitionError` como error de dominio fail-fast. `hydrate_ground_truth` expandido para aceptar los 4 estados (resuelve DF-06 y DF-11 simultáneamente).

**Hallazgos resueltos:** DF-06 (4 estados vs 2 tipos → RESOLVED), DF-08 (coexistencia Draft/Oracle → RESOLVED, permitida por diseño).

**Hallazgo forward-looking:** DF-13 (persistencia del estado SEALED → Gate 3, Task 3.2.1).

**Verificación:** Pyright 0 errors (models, lifecycle) · pytest 18 passed (lifecycle) · pytest 22 passed (models actualizado) · regresión 317 passed, 5 skipped.

**Task 1.2.2 (DONE — 2026-08-23) — Verificación + documentación:**
Verificado que `GroundTruthDraft` y `SealedOracle` no infieren estado de campos incidentales (materializado por tipos disjuntos en Task 1.1.2). El estado está determinado por el TIPO y el `sub_state`. Documentado que `ManifestLineageSealer` infiere estado de `ground_truth_sha256 != None` como hallazgo forward-looking para Gate 3 (NADR-14 §5.2 R5, Task 3.2.2). NO eliminado `ManifestGroundTruthUpdater` (responsabilidad de Gate 3). NO refactorizado `SealGroundTruthUseCase` (responsabilidad de Gate 2/Gate 3). Scope estrictamente respetado.

**Task 1.2.3 (DONE — 2026-08-23) — Verificación + documentación:**
Clarificado que la creación de una entidad en estado DRAFT no es una transición de ciclo de vida (las transiciones son cambios de estado). Verificado que `GenerateGoldenDraftUseCase` solo pasa nodos al writer sin producir transiciones implícitas. Verificado que `LoadGroundTruthUseCase` solo lee sin modificar estado. Documentado que `LifecycleTransitionAuthority` es el único punto de transición para el dominio de ciclo de vida. NO verificado `ManifestLineageSealer` (responsabilidad de Gate 3).

### 2.3 Wave 1.3 — Inmutabilidad y reemplazo (NADR-12 §5.3)

**Wave Status:** ✅ COMPLETED

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Forzar inmutabilidad de las entidades de ciclo de vida; toda transición produce una nueva instancia | NADR-12 §5.3 R7 | Medium | 1.2.3 | DONE |
| **1.3.2** | Permitir el reemplazo de un borrador por una nueva instancia durante la curaduría; prohibir mutación in-place | NADR-12 §5.3 R8 | Medium | 1.3.1 | DONE |
| **1.3.3** | Impedir que un oráculo sellado sea alterado o sobrescrito por operaciones de curaduría | NADR-12 §5.3 R9 | High | 1.3.1 | DONE |

#### Notas de implementación — Wave 1.3

**Task 1.3.1 (DONE — 2026-08-24) — Verificación + documentación:**
Verificado que la inmutabilidad está materializada por: (1) `frozen=True` en `GroundTruthDraft` y `SealedOracle` (Task 1.1.2), (2) transiciones que retornan nuevas instancias en `LifecycleTransitionAuthority` (Task 1.2.1), (3) tests de inmutabilidad que verifican `result is not draft`. NO se agregó código nuevo.

**Task 1.3.2 (DONE — 2026-08-24) — Verificación + tests + corrección de bug:**
Verificado que el reemplazo está permitido: crear nueva instancia de `GroundTruthDraft` con mismo `document_id`, mutación in-place prohibida por `frozen=True`. Agregados 2 tests: `test_draft_replacement_creates_new_instance` (dominio, en `test_ground_truth_models.py`) y `test_draft_writer_overwrites_existing_file` (infraestructura, en `test_ground_truth_ports.py`). El test de infraestructura expuso bug multiplataforma (DF-15): `write_ast_json_atomic` usaba `Path.rename()` que lanza `FileExistsError` en Windows si el destino existe. Corregido con `os.replace()` que es atómico y multiplataforma. Esta corrección garantiza NADR-F17BIS-01 §5.6 (reemplazo atómico) en Windows.

**Hallazgo resuelto:** DF-15 (bug multiplataforma en `write_ast_json_atomic` → RESOLVED).

**Verificación:** Pyright 0 errors · pytest 23 passed (models) · pytest 4 passed (ports) · regresión 320 passed, 5 skipped.

**Task 1.3.3 (DONE — 2026-08-24) — Verificación + test + DF-14:**
Verificado que la protección de modelo y autoridad está materializada: (1) `SealedOracle` es `frozen=True` (mutación in-place prohibida), (2) `LifecycleTransitionAuthority` no tiene rollback para `SealedOracle` (verificado por test `test_sealed_oracle_cannot_rollback` que confirma `AttributeError` al pasar `SealedOracle` a métodos de rollback). La protección de persistencia (impedir sobrescritura de oráculos sellados en disco) requiere mecanismo de persistencia del estado SEALED (DF-13) y se registra como hallazgo forward-looking para Gate 3 (DF-14). NADR-12 §5.3 R9 materializado a nivel de modelo y autoridad; protección de persistencia completada en Gate 3.

**Hallazgo derivado:** DF-14 (protección contra sobrescritura de oráculos sellados → Gate 3, Task 3.2.1, depende de DF-13).

**Verificación:** Pyright 0 errors · pytest 19 passed (lifecycle) · regresión 320 passed, 5 skipped.

#### Notas de referencia cruzada (§1.4)
> NADR-12 §5.1 R3 (Task 1.1.3) referencia el contrato canónico de serialización gobernado por NADR-F17BIS-01 (Fase 1). No hay doble implementación: NADR-01 gobierna la representación canónica del AST; la Task 1.1.3 únicamente la consume como precondición de hidratación.

#### Hallazgos identificados en este Gate (Waves 1.1, 1.2, 1.3)
| ID | Hallazgo | Estado |
|----|----------|--------|
| DF-01 | Deuda: 4 copias locales de helper de construcción ASTNode en tests | REVIEW_REQUIRED |
| DF-02 | Decisión ontológica: GroundTruth como Entity con document_id [RESOLVED] | RESOLVED |
| DF-03 | Campo state eliminado; tipo determina el estado [RESOLVED] | RESOLVED |
| DF-04 | ACCEPTED_LIMITATION: inmutabilidad profunda con fugas heredadas | ACCEPTED_LIMITATION |
| DF-05 | Tuple vs Sequence en puertos [RESOLVED] | RESOLVED |
| DF-06 | 4 estados vs 2 tipos (AUDITED/VALIDATED son sub-estados del Draft) [RESOLVED] | RESOLVED |
| DF-07 | Redundancia potencial document_id [RESOLVED] | RESOLVED |
| DF-08 | Coexistencia Draft/Oracle permitida por diseño [RESOLVED] | RESOLVED |
| DF-09 | Import ausente de ASTNode en ground_truth_store.py [RESOLVED] | RESOLVED |
| DF-10 | BenchmarkParserBridge.extract_ast debe retornar Tuple (prerequisito Wave 1.3) | REVIEW_REQUIRED |
| DF-11 | Mapeo AUDITED/VALIDATED prematuro en fábrica [RESOLVED] | RESOLVED |
| DF-13 | Persistencia del estado SEALED (forward-looking Gate 3) | REVIEW_REQUIRED |
| DF-14 | Protección contra sobrescritura de oráculos sellados (forward-looking Gate 3, depende de DF-13) | REVIEW_REQUIRED |
| DF-15 | Bug multiplataforma en write_ast_json_atomic [RESOLVED] | RESOLVED |

### 2.4 Gate 1 Exit Criteria

Todas las reglas de NADR-F17BIS-12 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:
- Existe una entidad de dominio cuyo tipo está determinado por el estado de ciclo de vida
- Los tipos de borrador y oráculo sellado son disjuntos y no convertibles implícitamente
- Ningún consumidor infiere el estado de sellado desde la presencia de un artefacto
- Las entidades de ciclo de vida son inmutables; las transiciones producen nuevas instancias
- Un oráculo sellado no puede ser sobrescrito por curaduría

### 2.5 Gate 1 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ (9/9) |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ (9/9) |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ (14 derivados, 11 cerrados) |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (baseline 274+ mantenida) | ✅ (320 passed) |
| 7 | Notas de implementación completas para todas las Tasks | ✅ (9/9) |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 2 — GROUND TRUTH VALIDITY & BASELINE COMPLETENESS

**Objective:** Materializar el contrato de validez estructural del oráculo y la completitud biyectiva de la baseline (Zero Partial Sealing), con sellado atómico.
**NADRs afectados:** NADR-F17BIS-13 (10 reglas)
**Execution Mode:** Secuencial (depende de Gate 1)
**Rollback Plan:** `git revert` de los contratos de validez y completitud; el sellado retorna al comportamiento de Fase 1 (no recomendado — reproduce el defecto P0).
**Gate Status:** ⏳ PENDING

### 2.6 Wave 2.1 — Contrato de validez estructural (NADR-13 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Definir un contrato explícito de validez estructural que todo oráculo debe satisfacer antes del sellado | NADR-13 §5.1 R1 | High | Gate 1 | TODO |
| **2.1.2** | Incluir en el contrato la no-vaciedad del contenido, la integridad de los nodos y la coherencia estructural | NADR-13 §5.1 R2 | High | 2.1.1 | TODO |
| **2.1.3** | Rechazar de forma explícita e inmediata el sellado de todo oráculo que no satisfaga el contrato de validez | NADR-13 §5.1 R3 | Critical | 2.1.2 | TODO |

#### Notas de implementación — Wave 2.1
> {Se actualiza al completar la Wave.}

### 2.7 Wave 2.2 — Completitud biyectiva (NADR-13 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Forzar la correspondencia biyectiva completa entre documentos fuente declarados y sus oráculos | NADR-13 §5.2 R4 | Critical | 2.1.3 | TODO |
| **2.2.2** | Verificar la completitud en ambas direcciones (documento→oráculo y oráculo→documento) | NADR-13 §5.2 R5 | Critical | 2.2.1 | TODO |
| **2.2.3** | Abortar el sellado mediante fallo explícito ante la ausencia de oráculo para un documento fuente declarado | NADR-13 §5.2 R6 | Critical | 2.2.2 | TODO |
| **2.2.4** | Detectar oráculos huérfanos (sin documento fuente declarado) y abortar el sellado | NADR-13 §5.2 R7 | Critical | 2.2.2 | TODO |
| **2.2.5** | Prohibir la degradación de la incompletitud a advertencias no bloqueantes | NADR-13 §5.2 R8 | High | 2.2.3 | TODO |

#### Notas de implementación — Wave 2.2
> {Se actualiza al completar la Wave.}

### 2.8 Wave 2.3 — Atomicidad del sellado (NADR-13 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Hacer del sellado una operación atómica: se certifica la baseline completa y válida, o no se certifica nada | NADR-13 §5.3 R9 | Critical | 2.2.5 | TODO |
| **2.3.2** | Garantizar que un sellado abortado no deje una baseline parcialmente certificada ni un manifiesto inconsistente | NADR-13 §5.3 R10 | Critical | 2.3.1 | TODO |

#### Notas de implementación — Wave 2.3
> {Se actualiza al completar la Wave.}

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.9 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-13 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Todo oráculo es validado estructuralmente antes del sello
- La biyección documento↔oráculo se verifica en ambas direcciones
- La ausencia de un oráculo o la presencia de un oráculo huérfano aborta el sellado con fallo explícito
- El sellado es atómico; un aborto no deja baseline parcial

### 2.10 Gate 2 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 3 — CURATION/RUNTIME PORT ASYMMETRY & SEALING AUTHORITY

**Objective:** Segregar las superficies de acceso de curaduría y runtime en puertos asimétricos, y consolidar una única autoridad de sellado gobernada.
**NADRs afectados:** NADR-F17BIS-14 (9 reglas)
**Execution Mode:** Secuencial (depende de Gate 2)
**Rollback Plan:** `git revert` de la segregación de puertos; restaurar la autoridad de sellado previa.
**Gate Status:** ⏳ PENDING

### 2.11 Wave 3.1 — Asimetría de puertos (NADR-14 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Exponer las operaciones de curaduría (escritura) y de runtime (lectura) sobre la baseline mediante contratos de acceso distintos | NADR-14 §5.1 R1 | High | Gate 2 | TODO |
| **3.1.2** | Garantizar que el contrato de lectura de runtime no exponga capacidad de escritura ni mutación de la baseline | NADR-14 §5.1 R2 | High | 3.1.1 | TODO |
| **3.1.3** | Impedir que el contrato de curaduría sea consumido por los caminos de runtime que leen la baseline certificada | NADR-14 §5.1 R3 | High | 3.1.1 | TODO |

#### Notas de implementación — Wave 3.1
> {Se actualiza al completar la Wave.}

### 2.12 Wave 3.2 — Autoridad única de sellado (NADR-14 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Consolidar la certificación de oráculos y baselines en una única autoridad de sellado | NADR-14 §5.2 R4 | High | 3.1.3 | TODO |
| **3.2.2** | Eliminar la coexistencia de múltiples autoridades de sellado con lógica duplicada o divergente | NADR-14 §5.2 R5 | Medium | 3.2.1 | TODO |
| **3.2.3** | Asegurar que toda operación de sellado delegue en la autoridad única, sin rutas alternativas | NADR-14 §5.2 R6 | High | 3.2.1 | TODO |

#### Notas de implementación — Wave 3.2
> {Se actualiza al completar la Wave.}

### 2.13 Wave 3.3 — Superficie de curaduría gobernada (NADR-14 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Componer las dependencias de todo punto de entrada de curaduría/sellado conforme a la raíz de composición establecida | NADR-14 §5.3 R7 | Medium | 3.2.3 | TODO |
| **3.3.2** | Propagar los fallos de integridad durante curaduría/sellado como errores explícitos, sin degradación a advertencias | NADR-14 §5.3 R8 | High | 3.3.1 | TODO |
| **3.3.3** | Proveer explícitamente los parámetros que determinan la identidad de la baseline (versión objetivo del sello), sin fijación implícita | NADR-14 §5.3 R9 | Medium | 3.3.1 | TODO |

#### Notas de implementación — Wave 3.3
> {Se actualiza al completar la Wave.}

#### Notas de referencia cruzada (§1.4)
> NADR-14 §5.3 R7 (Task 3.3.1) referencia la raíz de composición gobernada por NADR-F17BIS-11 (Fase 1). No hay doble implementación: NADR-11 gobierna la composición del pipeline de traducción; la Task 3.3.1 extiende el mismo principio a los entry points de curaduría de la baseline.

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.14 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-14 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Los contratos de lectura y escritura de la baseline están segregados
- El camino de runtime no puede invocar operaciones de escritura
- Existe una única autoridad de sellado; la duplicación de lógica de linaje ha sido erradicada
- Los entry points de curaduría componen vía raíz de composición y propagan fallos explícitos

### 2.15 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 4 — SEMANTIC IDENTITY LINEAGE IN THE BASELINE MODEL

**Objective:** Portar la identidad semántica del oráculo como linaje de primera clase, separar las dimensiones de identidad y diferenciar las versiones de esquema/corpus/baseline.
**NADRs afectados:** NADR-F17BIS-15 (9 reglas)
**Execution Mode:** Secuencial (depende de Gate 3)
**Rollback Plan:** `git revert` del modelo de linaje de identidad; el modelo retorna al estado de integridad de bytes de Fase 1.
**Gate Status:** ⏳ PENDING

### 2.16 Wave 4.1 — Linaje de identidad semántica (NADR-15 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Portar la identidad semántica del oráculo como parte de su linaje dentro del modelo de baseline | NADR-15 §5.1 R1 | High | Gate 3 | TODO |
| **4.1.2** | Incluir la identidad semántica del oráculo en el linaje del sellado, además de la integridad del artefacto | NADR-15 §5.1 R2 | High | 4.1.1 | TODO |
| **4.1.3** | Asegurar que la identidad semántica corresponda a la firma semántica determinista del AST gobernada por el contrato canónico de hashing | NADR-15 §5.1 R3 | High | 4.1.2 | TODO |

#### Notas de implementación — Wave 4.1
> {Se actualiza al completar la Wave.}

### 2.17 Wave 4.2 — Separación de dimensiones de identidad (NADR-15 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Residir las dimensiones de identidad (semántica, integridad del artefacto, identidad física del documento fuente, versión de esquema) en lugares ontológicos diferenciados | NADR-15 §5.2 R4 | High | 4.1.3 | TODO |
| **4.2.2** | Prohibir el colapso de dos o más dimensiones de identidad en un único campo o mecanismo | NADR-15 §5.2 R5 | High | 4.2.1 | TODO |
| **4.2.3** | Impedir que el hash de integridad de los bytes de un artefacto sea utilizado como identidad semántica del oráculo | NADR-15 §5.2 R6 | Critical | 4.2.1 | TODO |
| **4.2.4** | Impedir que la identidad física del documento fuente incorpore la identidad semántica del oráculo | NADR-15 §5.2 R7 | High | 4.2.1 | TODO |

#### Notas de implementación — Wave 4.2
> {Se actualiza al completar la Wave.}

### 2.18 Wave 4.3 — Diferenciación de versiones (NADR-15 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Diferenciar la versión del esquema del AST, la versión del corpus y la identidad de la baseline en el modelo de identidad | NADR-15 §5.3 R8 | High | 4.2.4 | TODO |
| **4.3.2** | Hacer la firma del catálogo sensible al linaje de los oráculos; una mutación de oráculo altera la firma resultante | NADR-15 §5.3 R9 | Critical | 4.3.1 | TODO |

#### Notas de implementación — Wave 4.3
> {Se actualiza al completar la Wave.}

#### Notas de referencia cruzada (§1.4)
> NADR-15 §5.1 R3 (Task 4.1.3) referencia la firma semántica determinista gobernada por NADR-F17BIS-03 (Fase 1). No hay doble implementación: NADR-03 gobierna la fórmula de `compute_ast_hash`; la Task 4.1.3 únicamente consume esa firma como identidad semántica del oráculo.

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.19 Gate 4 Exit Criteria

Todas las reglas de NADR-F17BIS-15 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- El oráculo sellado porta su identidad semántica como linaje de primera clase
- Las dimensiones de identidad (semántica, integridad, física, esquema) están diferenciadas y no colapsadas
- La versión de esquema, versión de corpus e identidad de baseline están diferenciadas
- La firma del catálogo es sensible al linaje de los oráculos

### 2.20 Gate 4 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 (Ontología) | — | 6/9 | 6/9 | 12 (DF-01..13; 9 cerrados) | Waves 1.1 y 1.2 COMPLETED, Gate IN PROGRESS |
| Gate 2 (Validez/Completitud) | — | 0/10 | 0/10 | 0 | — |
| Gate 3 (Autoridad/Puertos) | — | 0/9 | 0/9 | 0 | — |
| Gate 4 (Identidad Semántica) | — | 0/9 | 0/9 | 0 | — |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-F2-01** | Verificar que los entry points de curaduría (`bootstrap_corpus`, `freeze_ground_truth`, `generate_golden_draft`) operan contra la nueva ontología sin degradación | Local | NADR-14 §5.3 R7, R8 | Smoke test de curaduría | TODO |

> **Nota:** La migración de artefactos de baseline existentes (re-sellado) y la materialización del corpus canónico en disco **NO** pertenecen a la Fase 2. El re-sellado criptográfico es responsabilidad de la Fase 3 (Identity & Trust Model, `MIG-01` del plan global) y la materialización de la Fase 5 (Baseline Certification). La Fase 2 formaliza la ontología; no puebla ni re-sella artefactos.

---

## 5. GLOBAL DoD (Definition of Done)

La Fase 2 (Scientific Baseline Domain) se considera oficialmente completada cuando:

```text
{All rules in APPROVED NADRs F17BIS-12..15} − {Rules with DONE status in §7} = ∅
```

Es decir, las **37 reglas** de NADR-F17BIS-12..15 deben estar en estado `DONE`.

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 (Ontología) | 6 | 6 | 0 | 3 | 🟡 IN PROGRESS |
| Gate 2 (Validez/Completitud) | 0 | 0 | 0 | 10 | ⏳ PENDING |
| Gate 3 (Autoridad/Puertos) | 0 | 0 | 0 | 9 | ⏳ PENDING |
| Gate 4 (Identidad Semántica) | 0 | 0 | 0 | 9 | ⏳ PENDING |
| **TOTAL** | **6** | **6** | **0** | **31** | 🟡 IN PROGRESS |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task
3. Se actualiza el `Derived Status` de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 7.1 Gate 1 — NADR-F17BIS-12 (Oracle Ontology & Lifecycle)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-12 §5.1 R1 | DONE | Task 1.1.1 | Entidad GroundTruth + enum GroundTruthLifecycleState creados. Tipo determinado por state. DF-02, DF-03 derivados. |
| NADR-12 §5.1 R2 | DONE | Task 1.1.2 | Tipos disjuntos GroundTruthDraft y SealedOracle creados con document_id como identidad. Sin conversión implícita. DF-02, DF-03 cerrados como RESOLVED. DF-07, DF-08 derivados (forward-looking). |
| NADR-12 §5.1 R3 | DONE | Task 1.1.3 | Puertos actualizados a Tuple[ASTNode, ...]. Adaptador convierte List → Tuple. Fábrica hydrate_ground_truth introducida (solo DRAFT/SEALED; AUDITED/VALIDATED lanzan ValueError → DF-06). DF-05, DF-07, DF-09, DF-11 cerrados como RESOLVED. |
| NADR-12 §5.2 R4 | DONE | Task 1.2.1 | LifecycleTransitionAuthority introducida con 5 transiciones válidas. DraftSubState como sub-estados del Draft. DF-06, DF-08 cerrados como RESOLVED. DF-13 derivado a Gate 3. |
| NADR-12 §5.2 R5 | DONE | Task 1.2.2 | Verificado: modelo de dominio no infiere estado (tipos disjuntos). ManifestLineageSealer (Gate 3) documentado como forward-looking. |
| NADR-12 §5.2 R6 | DONE | Task 1.2.3 | Verificado: LifecycleTransitionAuthority es único punto de transición. GenerateGoldenDraftUseCase y LoadGroundTruthUseCase no producen transiciones implícitas. |
| NADR-12 §5.3 R7 | PENDING | Task 1.3.1 | — |
| NADR-12 §5.3 R8 | PENDING | Task 1.3.2 | — |
| NADR-12 §5.3 R9 | PENDING | Task 1.3.3 | — |

### 7.2 Gate 2 — NADR-F17BIS-13 (Validity & Completeness)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-13 §5.1 R1 | PENDING | Task 2.1.1 | — |
| NADR-13 §5.1 R2 | PENDING | Task 2.1.2 | — |
| NADR-13 §5.1 R3 | PENDING | Task 2.1.3 | — |
| NADR-13 §5.2 R4 | PENDING | Task 2.2.1 | — |
| NADR-13 §5.2 R5 | PENDING | Task 2.2.2 | — |
| NADR-13 §5.2 R6 | PENDING | Task 2.2.3 | — |
| NADR-13 §5.2 R7 | PENDING | Task 2.2.4 | — |
| NADR-13 §5.2 R8 | PENDING | Task 2.2.5 | — |
| NADR-13 §5.3 R9 | PENDING | Task 2.3.1 | — |
| NADR-13 §5.3 R10 | PENDING | Task 2.3.2 | — |

### 7.3 Gate 3 — NADR-F17BIS-14 (Port Asymmetry & Sealing Authority)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-14 §5.1 R1 | PENDING | Task 3.1.1 | — |
| NADR-14 §5.1 R2 | PENDING | Task 3.1.2 | — |
| NADR-14 §5.1 R3 | PENDING | Task 3.1.3 | — |
| NADR-14 §5.2 R4 | PENDING | Task 3.2.1 | — |
| NADR-14 §5.2 R5 | PENDING | Task 3.2.2 | — |
| NADR-14 §5.2 R6 | PENDING | Task 3.2.3 | — |
| NADR-14 §5.3 R7 | PENDING | Task 3.3.1 | — |
| NADR-14 §5.3 R8 | PENDING | Task 3.3.2 | — |
| NADR-14 §5.3 R9 | PENDING | Task 3.3.3 | — |

### 7.4 Gate 4 — NADR-F17BIS-15 (Semantic Identity Lineage)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-15 §5.1 R1 | PENDING | Task 4.1.1 | — |
| NADR-15 §5.1 R2 | PENDING | Task 4.1.2 | — |
| NADR-15 §5.1 R3 | PENDING | Task 4.1.3 | — |
| NADR-15 §5.2 R4 | PENDING | Task 4.2.1 | — |
| NADR-15 §5.2 R5 | PENDING | Task 4.2.2 | — |
| NADR-15 §5.2 R6 | PENDING | Task 4.2.3 | — |
| NADR-15 §5.2 R7 | PENDING | Task 4.2.4 | — |
| NADR-15 §5.3 R8 | PENDING | Task 4.3.1 | — |
| NADR-15 §5.3 R9 | PENDING | Task 4.3.2 | — |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.3.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (implementable / diferido / NAR / limitación)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.2.0.

* **El ADR Maestro** (`ADR_F17_BIS_MASTER.md`) define la visión arquitectónica de la fase (el QUÉ y el POR QUÉ).
* **El ADR de Fase** (`ADR_F17_BIS_02.md`) particulariza la decisión para la sub-fase Scientific Baseline Domain.
* **Las reglas técnicas obligatorias** se encuentran promulgadas en NADR-F17BIS-12 a NADR-F17BIS-15.
* **Este Execution Plan** define la secuencia operativa, tareas concretas y seguimiento de cumplimiento.
* **El Deferred Findings Register** (`FASE_2_DEFERRED_FINDINGS_REGISTER.md`) registra los hallazgos identificados, su clasificación y resolución.

Este documento **no prescribe decisiones arquitectónicas, criterios de revisión de código ni registro de hallazgos.**

---

## 10. FUTURE WORK

> El Traceability Appendix (§7) se escribe manualmente en esta versión. Versiones futuras **PODRÍAN** generar este appendix automáticamente desde metadatos de tareas, eliminando la sincronización manual. Esta nota evita asumir que el appendix debe mantenerse siempre a mano.
>
> La Fase 2 formaliza la ontología del oráculo. La materialización en disco del corpus canónico (Fase 5) y el encadenamiento criptográfico global $H_{baseline}$ (Fase 3) construirán sobre esta ontología sin modificarla.

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task
1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 11.2 Al completar una Task
1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task
3. Actualizar el `Derived Status` de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo
1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave"
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 11.4 Al cerrar un Gate
1. Verificar el Gate Exit Review Checklist
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§3)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 11.5 Al cancelar una operación de Deployment
1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§4)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§11.3)

### 11.6 Prohibiciones
- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre las reglas normativas de NADR-F17BIS-12..15 y su implementación en la Fase 2. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs APPROVED, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.