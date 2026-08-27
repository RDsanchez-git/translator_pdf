# PHASE_17BIS_FASE3_EXECUTION_PLAN.md

## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.0  
**Status:** DRAFT  
**Date:** 2026-08-27  
**Supersedes:** N/A  
**Derived From:** 3 NADRs FROZEN (NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0  
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa de la Fase 3 (Identity & Trust Model) y el seguimiento de cumplimiento de las reglas de NADR-F17BIS-15 v2.0, NADR-F17BIS-16 y NADR-F17BIS-17. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-27 | Emisión inicial. Mapeo de reglas de 3 NADRs FROZEN a 2 Gates / 5 Waves / 13 tareas atómicas. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17-BIS_03 (visión y capacidades de Fase 3)
↓
NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17 (reglas constitucionales permanentes, FROZEN)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_FASE3_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_3_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-F17BIS-17 §5.1 R1` → NADR-F17BIS-17, sección 5.1, regla 1.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_3_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

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

### 1.7 Naturaleza de la Fase 3

La Fase 3 es una fase de **formalización y hardening**, no de construcción masiva. A diferencia de la Fase 2 (que construyó la ontología del oráculo con 4 Gates, 12 Waves, 37 Tasks), la Fase 3 se enfoca en:

1. **Formalizar** lo que ya existe (cerrar gaps normativos mediante documentación explícita).
2. **Agregar defensa en profundidad** (validaciones explícitas de dominio para campos criptográficos).
3. **Limpiar deuda técnica** (campos huérfanos, docstrings ambiguos).
4. **Preparar el terreno** para Fase 4 (Scientific Verification).

Por lo tanto, el Execution Plan es deliberadamente compacto: **2 Gates, 5 Waves, 13 Tasks**. Esto refleja la realidad de que la mayoría de la infraestructura ya existe (implementada en Fase 2) y solo requiere formalización y validación.

---

## 2. GATES DE LA FASE 3 — IDENTITY & TRUST MODEL

La Fase 3 se estructura en **2 Gates**, separando claramente "formalización documental" de "implementación de validaciones":

```text
Gate 1 (Formalización Normativa) ✅ PENDING
   └──► Gate 2 (Validación Explícita de Dominio) ✅ PENDING
```

Cada Gate actúa como compuerta conforme a METHODOLOGY §6.5: el Gate N+1 no inicia hasta que el Gate N pase su Exit Review.

---

## GATE 1 — FORMALIZACIÓN NORMATIVA

**Objective:** Documentar explícitamente los contratos de hashing semántico, justificar la inclusión de `ground_truth_state` en la identidad global, aclarar docstrings ambiguos y limpiar campos huérfanos que no participan en la identidad.

**NADRs afectados:** NADR-F17BIS-15 v2.0, NADR-F17BIS-16  
**Execution Mode:** Secuencial (Wave 1.1 → Wave 1.2)  
**Rollback Plan:** `git revert` de los cambios documentales; el sistema retorna al estado de Fase 2 sin documentación explícita.  
**Gate Status:** ⏳ PENDING

### 2.1 Wave 1.1 — Documentación de Semántica de Dimensiones (NADR-F17BIS-16)

**Wave Status:** ⏳ PENDING  
**Fecha de inicio:** {YYYY-MM-DD}  
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Documentar `OracleSemanticIdentityCalculator` como contrato canónico para linaje de baseline | NADR-F17BIS-16 §5.2 R5, R6, R7, R8 | Low | — | TODO |
| **1.1.2** | Documentar coexistencia de contratos de hashing semántico (`compute_ast_hash` vs `OracleSemanticIdentityCalculator`) | NADR-F17BIS-16 §5.2 R5, R6, R7 | Low | — | TODO |
| **1.1.3** | Justificar explícitamente la inclusión de `ground_truth_state` en `manifest_hash` | NADR-F17BIS-16 §5.3 R10 | Low | — | TODO |

#### Notas de implementación — Task 1.1.1

> {Se actualiza al completar la Task. Documentar el CÓMO se implementó: archivos modificados, docstrings agregados, validaciones ejecutadas. Ejemplo: "Docstring de `OracleSemanticIdentityCalculator` actualizado para especificar: propósito arquitectónico (linaje de baseline), dimensiones incluidas (node_id, node_type, strategy, payload), dimensiones excluidas (metadata física). 368 tests passed, 0 errors pyright."}

#### Notas de implementación — Task 1.1.2

> {Se actualiza al completar la Task. Documentar la coexistencia de contratos: `compute_ast_hash` (NADR-03) es para comparación de parsers (agnóstico a node_id), `OracleSemanticIdentityCalculator` (NADR-15) es para linaje de baseline (sensible a node_id). Ambos son deterministas y tienen propósitos distintos.}

#### Notas de implementación — Task 1.1.3

> {Se actualiza al completar la Task. Agregar docstring en `ManifestFingerprintCalculator` que justifique la inclusión de `ground_truth_state` citando las tres razones del ADR_F17-BIS_03 §3: (1) previene des-sellado silencioso, (2) protege integridad del proceso de certificación, (3) cualquier cambio de estado invalida el sello.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.2 Wave 1.2 — Limpieza de Deuda Técnica (DC-06, DC-08)

**Wave Status:** ⏳ PENDING  
**Fecha de inicio:** {YYYY-MM-DD}  
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Corregir docstring de `compute_ast_hash` para clarificar sensibilidad al orden (DC-06) | NADR-F17BIS-16 §5.2 R5, R6, R7 | Low | Wave 1.1 | TODO |
| **1.2.2** | Eliminar campos huérfanos `ground_truth_version` y `ground_truth_sha256` de `RawDocumentEntryDTO` (DC-08) | ENGINEERING_PRINCIPLES §I (YAGNI) | Medium | Wave 1.1 | TODO |

#### Notas de implementación — Task 1.2.1

> {Se actualiza al completar la Task. Corregir docstring de `compute_ast_hash` en `core/ast/hashing.py` para clarificar que la función es sensible al orden de la secuencia de nodos, eliminando la ambigüedad del docstring actual que dice "independientemente de su orden de procesamiento".}

#### Notas de implementación — Task 1.2.2

> {Se actualiza al completar la Task. Eliminar campos `ground_truth_version` y `ground_truth_sha256` de `RawDocumentEntryDTO` en `core/benchmark/corpus/dtos.py`. Actualizar todos los consumidores que referencian estos campos. Ejecutar suite completa de tests para verificar que no hay rupturas.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.3 Gate 1 Exit Criteria

Todas las reglas de NADR-F17BIS-15 v2.0 y NADR-F17BIS-16 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- `OracleSemanticIdentityCalculator` tiene documentación explícita de propósito arquitectónico, dimensiones incluidas/excluidas.
- La coexistencia de `compute_ast_hash` y `OracleSemanticIdentityCalculator` está documentada con justificación de propósitos distintos.
- La inclusión de `ground_truth_state` en `manifest_hash` está justificada explícitamente con las tres razones del ADR.
- El docstring de `compute_ast_hash` clarifica sensibilidad al orden de nodos.
- Campos huérfanos `ground_truth_version` y `ground_truth_sha256` han sido eliminados de `RawDocumentEntryDTO`.

### 2.4 Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas del Gate en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde (baseline 368 passed, 5 skipped) | {✅/❌} |
| 7 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}  
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 2 — VALIDACIÓN EXPLÍCITA DE DOMINIO

**Objective:** Implementar validación explícita de dominio para campos que participan en identidades criptográficas (`document_id`, `node_id`), agregar tests de propiedad para verificar inyectividad del encoding, y documentar el conjunto de sentinels y valores especiales.

**NADRs afectados:** NADR-F17BIS-17  
**Execution Mode:** Secuencial (Wave 2.1 → Wave 2.2 → Wave 2.3)  
**Rollback Plan:** `git revert` de las validaciones de dominio agregadas; el sistema retorna al estado post-Gate 1 sin validación explícita de dominio.  
**Gate Status:** ⏳ PENDING

### 2.5 Wave 2.1 — Validación de Dominio para `document_id` (NADR-F17BIS-17)

**Wave Status:** ⏳ PENDING  
**Fecha de inicio:** {YYYY-MM-DD}  
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Agregar validación de dominio en `CorpusDocumentMetadata.document_id` (excluir `:`) | NADR-F17BIS-17 §5.1 R1-R4 | Medium | Gate 1 | TODO |
| **2.1.2** | Agregar tests de fail-fast para `document_id` inválido | NADR-F17BIS-17 §5.1 R3-R4 | Low | 2.1.1 | TODO |
| **2.1.3** | Documentar contrato de dominio de `document_id` | NADR-F17BIS-17 §5.4 R13 | Low | 2.1.1 | TODO |

#### Notas de implementación — Task 2.1.1

> {Se actualiza al completar la Task. Agregar `pattern=r"^[^:]+$"` a `document_id` en `core/benchmark/corpus/models.py::CorpusDocumentMetadata`. Verificar que la validación se aplica en construcción del objeto (fail-fast).}

#### Notas de implementación — Task 2.1.2

> {Se actualiza al completar la Task. Agregar test unitario en `tests/unit/test_corpus_models.py` que verifique que `document_id` con `:` falla con `ValidationError`. Ejecutar suite completa de tests para verificar que no hay rupturas.}

#### Notas de implementación — Task 2.1.3

> {Se actualiza al completar la Task. Agregar docstring en `CorpusDocumentMetadata` que documente el contrato de dominio de `document_id`: caracteres permitidos, caracteres prohibidos (`:`), justificación (inyectividad del framing).}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.6 Wave 2.2 — Validación de Dominio para `node_id` (NADR-F17BIS-17)

**Wave Status:** ⏳ PENDING  
**Fecha de inicio:** {YYYY-MM-DD}  
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Agregar validación de dominio en `ASTNode.node_id` (excluir `:`) | NADR-F17BIS-17 §5.1 R1-R4 | Medium | Wave 2.1 | TODO |
| **2.2.2** | Agregar tests de fail-fast para `node_id` inválido | NADR-F17BIS-17 §5.1 R3-R4 | Low | 2.2.1 | TODO |
| **2.2.3** | Documentar contrato de dominio de `node_id` | NADR-F17BIS-17 §5.4 R13 | Low | 2.2.1 | TODO |

#### Notas de implementación — Task 2.2.1

> {Se actualiza al completar la Task. Agregar `pattern=r"^[^:]+$"` a `node_id` en `core/ast/models.py::ASTNode`. Verificar que la validación se aplica en construcción del objeto (fail-fast).}

#### Notas de implementación — Task 2.2.2

> {Se actualiza al completar la Task. Agregar test unitario en `tests/unit/test_ast_models.py` que verifique que `node_id` con `:` falla con `ValidationError`. Ejecutar suite completa de tests para verificar que no hay rupturas.}

#### Notas de implementación — Task 2.2.3

> {Se actualiza al completar la Task. Agregar docstring en `ASTNode` que documente el contrato de dominio de `node_id`: caracteres permitidos, caracteres prohibidos (`:`), justificación (inyectividad del framing).}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.7 Wave 2.3 — Tests de Inyectividad del Encoding (NADR-F17BIS-17)

**Wave Status:** ⏳ PENDING  
**Fecha de inicio:** {YYYY-MM-DD}  
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Agregar property-based testing para inyectividad de `manifest_hash` | NADR-F17BIS-17 §5.2 R5-R8 | Medium | Wave 2.2 | TODO |
| **2.3.2** | Agregar property-based testing para inyectividad de `oracle_hash` | NADR-F17BIS-17 §5.2 R5-R8 | Medium | Wave 2.2 | TODO |

#### Notas de implementación — Task 2.3.1

> {Se actualiza al completar la Task. Agregar property-based tests en `tests/unit/test_manifest_fingerprint.py` usando `hypothesis` library que verifiquen inyectividad del encoding: dos payloads distintos producen hashes distintos. Configurar estrategias conservadoras para `document_id`, `fingerprint.sha256`, `traits`, `page_count`, `oracle_hash`, `ground_truth_state`.}

#### Notas de implementación — Task 2.3.2

> {Se actualiza al completar la Task. Agregar property-based tests en `tests/unit/test_oracle_identity.py` usando `hypothesis` library que verifiquen inyectividad del encoding: dos tuplas de nodos distintas producen hashes distintos. Configurar estrategias conservadoras para `node_id`, `node_type`, `strategy`, `payload`.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.8 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-17 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- `document_id` tiene validación de dominio que excluye `:`.
- `node_id` tiene validación de dominio que excluye `:`.
- Tests de fail-fast verifican que valores inválidos son rechazados explícitamente.
- Contratos de dominio están documentados en docstrings.
- Tests de propiedad verifican inyectividad del encoding para `manifest_hash` y `oracle_hash`.
- Conjunto de sentinels está documentado.

### 2.9 Gate 2 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas del Gate en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde (baseline 368 passed, 5 skipped + nuevos tests de propiedad) | {✅/❌} |
| 7 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}  
**Fecha de verificación:** {YYYY-MM-DD}

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | {YYYY-MM-DD} | {X/Y} | {5/5} | {N} | {Observaciones} |
| Gate 2 | {YYYY-MM-DD} | {X/Y} | {8/8} | {N} | {Observaciones} |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Verificar que todos los `document_id` existentes en el corpus canónico cumplen con el nuevo patrón (sin `:`) | Local | NADR-F17BIS-17 §5.1 R1-R4 | Script de validación | TODO |
| **MIG-02** | Verificar que todos los `node_id` existentes en los oráculos cumplen con el nuevo patrón (sin `:`) | Local | NADR-F17BIS-17 §5.1 R1-R4 | Script de validación | TODO |
| **MIG-03** | Ejecutar suite completa de tests de regresión para verificar que no hay rupturas | Local/CI | Todas las reglas | pytest output | TODO |

---

## 5. GLOBAL DoD (Definition of Done)

La Fase 3 (Identity & Trust Model) se considera oficialmente completada cuando:

```text
{All rules in FROZEN NADRs NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17} − {Rules with DONE status in §7} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | {A} | {X} | {Y} | {Z} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 2 | {B} | {W} | {V} | {U} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| **TOTAL** | **{A+B}** | **{X+W}** | **{Y+V}** | **{Z+U}** | {Estado global} |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task (§2.{X}.{Y})
3. Se actualiza el `Derived Status` de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.{X}.4 o §2.{X}.9)

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 7.1 Gate 1 — Rules Audit Board


#### NADR-F17BIS-16

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-16 §5.1 R1-R3 | DONE | Wave 1.1 / Task 1.1.1 | Documentación de OracleSemanticIdentityCalculator como contrato canónico |
| NADR-F17BIS-16 §5.2 R4-R8 | DONE | Wave 1.1 / Task 1.1.2, Wave 1.2 / Task 1.2.1 | Documentación de coexistencia de contratos de hashing + aclaración de docstring |
| NADR-F17BIS-16 §5.3 R9-R12 | DONE | Wave 1.1 / Task 1.1.3 | Justificación de ground_truth_state en manifest_hash |
| NADR-F17BIS-16 §5.4 R13-R16 | DONE | Wave 1.1 / Task 1.1.1, 1.1.2, 1.1.3 | Verificación de documentación de composición de identidad global |

#### Limpieza de Deuda Técnica

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| DC-06 (aclarar docstring) | DONE | Wave 1.2 / Task 1.2.1 | Docstring de compute_ast_hash corregido |
| DC-08 (limpiar campos huérfanos) | DONE | Wave 1.2 / Task 1.2.2 | Campos ground_truth_version y ground_truth_sha256 eliminados |

### 7.2 Gate 2 — Rules Audit Board

#### NADR-F17BIS-17

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-17 §5.1 R1-R4 | DONE | Wave 2.1 / Task 2.1.1, Wave 2.2 / Task 2.2.1 | Validación de dominio para document_id y node_id |
| NADR-F17BIS-17 §5.1 R3-R4 | DONE | Wave 2.1 / Task 2.1.2, Wave 2.2 / Task 2.2.2 | Tests de fail-fast para valores inválidos |
| NADR-F17BIS-17 §5.2 R5-R8 | DONE | Wave 2.3 / Task 2.3.1, 2.3.2 | Tests de propiedad para inyectividad del encoding |
| NADR-F17BIS-17 §5.3 R9-R12 | DONE | Wave 2.1 / Task 2.1.3, Wave 2.2 / Task 2.2.3 | Documentación de sentinels y valores especiales |
| NADR-F17BIS-17 §5.4 R13-R15 | DONE | Wave 2.1 / Task 2.1.3, Wave 2.2 / Task 2.2.3, Wave 2.3 / Task 2.3.1, 2.3.2 | Verificación de inyectividad mediante tests automatizados |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_3_DEFERRED_FINDINGS_REGISTER.md
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

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase (NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17).
* La **secuencia operativa, tareas concretas y seguimiento de cumplimiento** se rigen por el Execution Plan (`PHASE_17BIS_FASE3_EXECUTION_PLAN.md`).
* Los **hallazgos identificados durante la implementación, su clasificación y resolución** se registran en el Deferred Findings Register (`FASE_3_DEFERRED_FINDINGS_REGISTER.md`).

Este documento **no prescribe implementaciones específicas, planificación operacional, criterios de revisión de código ni registro de hallazgos.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

---

## 10. FUTURE WORK

> El Traceability Appendix (§7) se escribe manualmente en esta versión. Versiones futuras **PODRÍAN** generar este appendix automáticamente desde metadatos de tareas, eliminando la sincronización manual. Esta nota evita asumir que el appendix debe mantenerse siempre a mano.
>
> La Fase 3 formaliza y valida la infraestructura de identidad. La materialización del corpus canónico en disco (Fase 5) y la integración en CI Gates (Fase 6) construirán sobre esta base sin modificarla.

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 11.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task (§2.{X}.{Y})
3. Actualizar el `Derived Status` de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§2.{X})
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 11.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§2.{X}.4 o §2.{X}.9)
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

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.