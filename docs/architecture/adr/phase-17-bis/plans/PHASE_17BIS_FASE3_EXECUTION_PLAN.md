# PHASE_17BIS_FASE3_EXECUTION_PLAN.md

## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.5.0  
**Status:** COMPLETED  
**Date:** 2026-08-29  
**Last Updated:** 2026-08-29  
**Supersedes:** v1.4.0   
**Derived From:** 3 NADRs FROZEN (NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0  
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa de la Fase 3 (Identity & Trust Model) y el seguimiento de cumplimiento de las reglas de NADR-F17BIS-15 v2.0, NADR-F17BIS-16 y NADR-F17BIS-17. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-27 | Emisión inicial. Mapeo de reglas de 3 NADRs FROZEN a 2 Gates / 5 Waves / 13 tareas atómicas. |
| 1.1.0 | 2026-08-27 | Gate 1 COMPLETED. Wave 1.1 y Wave 1.2 DONE (5/5 tasks). 0 hallazgos identificados. Gate 1 Exit Review: PASS. |
| 1.2.0 | 2026-08-28 | Wave 2.1 COMPLETED. Tasks 2.1.1-2.1.3 DONE (3/8 tasks de Gate 2). 24 tests nuevos, 392 passed total. 0 hallazgos. |
| 1.3.0 | 2026-08-28 | Wave 2.2 COMPLETED. Tasks 2.2.1-2.2.3 DONE (6/8 tasks de Gate 2). 27 tests de ASTNode, 419 passed total. Insight SOTA: spawn_fragment usa constructor completo para bypass de model_copy. 0 hallazgos. |
| 1.4.0 | 2026-08-29 | Wave 2.3 COMPLETED. Tasks 2.3.1-2.3.2 DONE. 17 property-based tests con hypothesis. Inyectividad del framing verificada empíricamente (~850 ejemplos aleatorios). Corrección de causa raíz en DocumentFingerprint.__post_init__ (eliminación de islower() redundante). Hallazgo DF-01 identificado y derivado al Findings Register. Gate 2 EXIT REVIEW: PASS CONDICIONADO (pendiente resolución de DF-01). 436 passed total. |
| 1.5.0 | 2026-08-29 | DF-01 RESOLVED en Batch 1 del Findings Register (METHODOLOGY §6.6). GroundTruthState type alias + aplicación en DTO/modelo + 6 tests. El Execution Plan mantiene su estructura original de 13 tasks. Gate 2 EXIT REVIEW FINAL: PASS. Fase 3 COMPLETADA. 442 passed total. |

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
Gate 1 (Formalización Normativa) ✅ COMPLETED
   └──► Gate 2 (Validación Explícita de Dominio) ✅ COMPLETED
```

Cada Gate actúa como compuerta conforme a METHODOLOGY §6.5: el Gate N+1 no inicia hasta que el Gate N pase su Exit Review.

---

## GATE 1 — FORMALIZACIÓN NORMATIVA

**Objective:** Documentar explícitamente los contratos de hashing semántico, justificar la inclusión de `ground_truth_state` en la identidad global, aclarar docstrings ambiguos y limpiar campos huérfanos que no participan en la identidad.

**NADRs afectados:** NADR-F17BIS-15 v2.0, NADR-F17BIS-16  
**Execution Mode:** Secuencial (Wave 1.1 → Wave 1.2)  
**Rollback Plan:** `git revert` de los cambios documentales; el sistema retorna al estado de Fase 2 sin documentación explícita.  
**Gate Status:** ✅ COMPLETED

### 2.1 Wave 1.1 — Documentación de Semántica de Dimensiones (NADR-F17BIS-16)

**Wave Status:** ✅ COMPLETED  
**Fecha de inicio:** 2026-08-27  
**Fecha de cierre:** 2026-08-27

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Documentar `OracleSemanticIdentityCalculator` como contrato canónico para linaje de baseline | NADR-F17BIS-16 §5.2 R5, R6, R7, R8 | Low | — | DONE |
| **1.1.2** | Documentar coexistencia de contratos de hashing semántico (`compute_ast_hash` vs `OracleSemanticIdentityCalculator`) | NADR-F17BIS-16 §5.2 R5, R6, R7 | Low | — | DONE |
| **1.1.3** | Justificar explícitamente la inclusión de `ground_truth_state` en `manifest_hash` | NADR-F17BIS-16 §5.3 R10 | Low | — | DONE |

#### Notas de implementación — Task 1.1.1

> Docstring del módulo `core/benchmark/ground_truth/identity.py` actualizado para declarar explícitamente `OracleSemanticIdentityCalculator` como CONTRATO CANÓNICO PARA LINAJE DE BASELINE (NADR-F17BIS-16 §5.2 R8). Se agregó diferenciación de contratos (DC-01 resuelto): este contrato incluye `node_id` porque la identidad del oráculo requiere distinguir nodos, mientras que `compute_ast_hash` lo excluye para comparación de parsers. Docstring de la clase actualizado con la misma declaración. 368 tests passed, 0 errors pyright.

#### Notas de implementación — Task 1.1.2

> Docstring del módulo `core/ast/hashing.py` actualizado para declarar explícitamente `compute_ast_hash` como CONTRATO ALTERNATIVO (no canónico para linaje). Se documentó la coexistencia con `OracleSemanticIdentityCalculator` y la justificación de propósitos distintos (NADR-F17BIS-16 §5.2 R4-R8). Referencias cruzadas agregadas a ambos contratos. 368 tests passed, 0 errors pyright.

#### Notas de implementación — Task 1.1.3

> Docstring de `ManifestFingerprintCalculator` en `core/benchmark/corpus/services.py` actualizado con la justificación explícita de la inclusión de `ground_truth_state` en el hash (NADR-F17BIS-16 §5.3 R10, DC-03 resuelto). Se documentaron las tres razones del ADR_F17-BIS_03 §3: (1) previene des-sellado silencioso, (2) protege integridad del proceso de certificación, (3) invalida sello ante cambios de estado. Se clarificó la semántica: `ground_truth_state` es estado operacional, `oracle_hash` es identidad científica. 368 tests passed, 0 errors pyright.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | Ningún hallazgo identificado | — |

### 2.2 Wave 1.2 — Limpieza de Deuda Técnica (DC-06, DC-08)

**Wave Status:** ✅ COMPLETED  
**Fecha de inicio:** 2026-08-27  
**Fecha de cierre:** 2026-08-27

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Corregir docstring de `compute_ast_hash` para clarificar sensibilidad al orden (DC-06) | NADR-F17BIS-16 §5.2 R5, R6, R7 | Low | Wave 1.1 | DONE |
| **1.2.2** | Eliminar campos huérfanos `ground_truth_version` y `ground_truth_sha256` de `RawDocumentEntryDTO` (DC-08) | ENGINEERING_PRINCIPLES §I (YAGNI) | Medium | Wave 1.1 | DONE |

#### Notas de implementación — Task 1.2.1

> Docstring de `compute_ast_hash` en `core/ast/hashing.py` corregido para clarificar sensibilidad al orden (DC-06 resuelto). Se eliminó la ambigüedad del docstring anterior que decía "independientemente de su orden de procesamiento". Se clarificó explícitamente: (a) el orden de los nodos en la secuencia SÍ afecta el hash, (b) el orden interno de procesamiento NO afecta el hash (gracias a `sort_keys=True`). 368 tests passed, 0 errors pyright.

#### Notas de implementación — Task 1.2.2

> Limpieza profunda de campos huérfanos `ground_truth_version` y `ground_truth_sha256` (DC-08 resuelto). Archivos modificados: `core/benchmark/corpus/dtos.py` (eliminación de campos), `core/benchmark/corpus/services.py` (eliminación de `detected_hashes` y `target_version` de `ManifestLineageSealer`), `core/benchmark/corpus/use_cases.py` (eliminación de propagación), `core/benchmark/ground_truth/use_cases.py` (eliminación de cálculo de `detected_hashes` y `target_version`), `tools/evaluation/freeze_ground_truth.py` (eliminación de `target_version`), tests y fixtures JSON actualizados.
>
> **Decisión de diseño clave:** Al eliminar `ground_truth_sha256`, el cálculo de `detected_hashes` (que hacía I/O de disco con `read_artifact_bytes`) quedó completamente huérfano y fue eliminado. Esto elimina una lectura de disco y un cálculo SHA-256 por documento durante el sellado, mejorando el rendimiento. Los parámetros `detected_hashes` y `target_version` fueron eliminados de las firmas de `ManifestLineageSealer.seal_manifest_with_ground_truth` y `SealGroundTruthUseCase.execute` para evitar código muerto. YAGNI. 368 tests passed, 0 errors pyright.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | Ningún hallazgo identificado | — |

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ (0 hallazgos) |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (baseline 368 passed, 5 skipped) | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** PASS  
**Fecha de verificación:** 2026-08-27

---

## GATE 2 — VALIDACIÓN EXPLÍCITA DE DOMINIO

**Objective:** Implementar validación explícita de dominio para campos que participan en identidades criptográficas (`document_id`, `node_id`), agregar tests de propiedad para verificar inyectividad del encoding, y documentar el conjunto de sentinels y valores especiales.

**NADRs afectados:** NADR-F17BIS-17  
**Execution Mode:** Secuencial (Wave 2.1 → Wave 2.2 → Wave 2.3)  
**Rollback Plan:** `git revert` de las validaciones de dominio agregadas; el sistema retorna al estado post-Gate 1 sin validación explícita de dominio.  
**Gate Status:** ✅ COMPLETED

### 2.5 Wave 2.1 — Validación de Dominio para `document_id` (NADR-F17BIS-17)

**Wave Status:** ✅ COMPLETED  
**Fecha de inicio:** 2026-08-28  
**Fecha de cierre:** 2026-08-28

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Agregar validación de dominio en `CorpusDocumentMetadata.document_id` (excluir `:`) | NADR-F17BIS-17 §5.1 R1-R4 | Medium | Gate 1 | DONE |
| **2.1.2** | Agregar tests de fail-fast para `document_id` inválido | NADR-F17BIS-17 §5.1 R3-R4 | Low | 2.1.1 | DONE |
| **2.1.3** | Documentar contrato de dominio de `document_id` | NADR-F17BIS-17 §5.4 R13 | Low | 2.1.1 | DONE |

#### Notas de implementación — Task 2.1.1

> Validación de dominio implementada mediante type alias centralizado `DocumentId` en `core/shared/identity_contracts.py` (nuevo módulo). Ubicación en `core/shared/` evita dependencias invertidas: tanto `core/benchmark/corpus` como `core/ast` (Wave 2.2) pueden importar sin violar boundaries. Mecanismo: `Annotated[str, StringConstraints(min_length=1, pattern=r"^[^:]+$")]` (Pydantic v2 idiomático). Aplicado en `CorpusDocumentMetadata.document_id` (modelo de dominio) y `RawDocumentEntryDTO.document_id` (DTO de frontera) para Fail-Fast en ambos puntos. 0 errors pyright.

#### Notas de implementación — Task 2.1.2

> Archivo `tests/unit/test_corpus_models.py` creado con 24 tests exhaustivos. Casos cubiertos: válidos (alfanuméricos, guiones, puntos, espacios, single-char), fail-fast para `:` (inicio, medio, final, solo `:`, múltiples `:`, vacío), inmutabilidad (`frozen=True`), invariantes de `DocumentFingerprint`, propagación de fail-fast en `CorpusManifest`. 24 passed, 0 errors pyright.

#### Notas de implementación — Task 2.1.3

> Docstrings de `CorpusDocumentMetadata` y `RawDocumentEntryDTO` actualizados con documentación completa del contrato de dominio: DOMINIO, PROHIBIDO, JUSTIFICACIÓN (inyectividad del framing criptográfico), VALIDACIÓN, SENTINEL. Incluye documentación consolidada de `oracle_hash` (sentinel "none") y `ground_truth_state` (estado operacional DF-13). 0 errors pyright.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | Ningún hallazgo identificado | — |


### 2.6 Wave 2.2 — Validación de Dominio para `node_id` (NADR-F17BIS-17)

**Wave Status:** ✅ COMPLETED  
**Fecha de inicio:** 2026-08-28  
**Fecha de cierre:** 2026-08-28

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Agregar validación de dominio en `ASTNode.node_id` (excluir `:`) | NADR-F17BIS-17 §5.1 R1-R4 | Medium | Wave 2.1 | DONE |
| **2.2.2** | Agregar tests de fail-fast para `node_id` inválido | NADR-F17BIS-17 §5.1 R3-R4 | Low | 2.2.1 | DONE |
| **2.2.3** | Documentar contrato de dominio de `node_id` | NADR-F17BIS-17 §5.4 R13 | Low | 2.2.1 | DONE |

#### Notas de implementación — Task 2.2.1

> Validación de dominio aplicada a `node_id` y `parent_node_id` en `ASTNode` usando el type alias `NodeId` de `core/shared/identity_contracts.py`. Ambos campos usan `NodeId` (y `Optional[NodeId]` respectivamente) para consistencia de dominio: ninguna referencia a un node_id puede contener el delimitador `:`. Insight SOTA: `spawn_fragment()` fue reescrito para usar el constructor completo de `ASTNode` en lugar de `model_copy(update={"node_id": ...})`, porque Pydantic v2 no revalida campos actualizados vía `model_copy`. Esto previene bypass del contrato de dominio. `with_strategy()` y `with_sequence_id()` mantienen `model_copy` porque no actualizan campos con contrato. 0 errors pyright.

#### Notas de implementación — Task 2.2.2

> Archivo `tests/unit/test_ast_models.py` creado con 27 tests exhaustivos. Clases de tests: `TestNodeIdDomainContract` (9 tests de fail-fast para `:`), `TestParentNodeIdDomainContract` (4 tests de consistencia de dominio), `TestASTNodeInvariants` (9 tests de inmutabilidad y propiedades), `TestASTNodeSpawnFragment` (4 tests incluyendo bypass prevention). 27 passed, 0 errors pyright.

#### Notas de implementación — Task 2.2.3

> Docstring de `ASTNode` actualizado con documentación completa del contrato de dominio de `node_id`: DOMINIO, PROHIBIDO (`:`), JUSTIFICACIÓN (inyectividad del framing `node_id:type:strategy:payload_hash` en `OracleSemanticIdentityCalculator`), VALIDACIÓN, SENTINEL. `parent_node_id` documentado con el mismo contrato para consistencia. Nota SOTA sobre `spawn_fragment` incluida. 0 errors pyright.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | Ningún hallazgo identificado | — |

### 2.7 Wave 2.3 — Tests de Inyectividad del Encoding (NADR-F17BIS-17)

**Wave Status:** ✅ COMPLETED  
**Fecha de inicio:** 2026-08-29  
**Fecha de cierre:** 2026-08-29

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Agregar property-based testing para inyectividad de `manifest_hash` | NADR-F17BIS-17 §5.2 R5-R8 | Medium | Wave 2.2 | DONE |
| **2.3.2** | Agregar property-based testing para inyectividad de `oracle_hash` | NADR-F17BIS-17 §5.2 R5-R8 | Medium | Wave 2.2 | DONE |

#### Notas de implementación — Task 2.3.1

> Archivo `tests/unit/test_framing_injectivity.py` creado con 9 property-based tests para `ManifestFingerprintCalculator` usando `hypothesis`. Estrategias conservadoras generan valores dentro del dominio válido (sin `:`, hex lowercase, enum values). Tests de sensibilidad: document_id, fingerprint.sha256, traits, page_count, oracle_hash, ground_truth_state, corpus_version. Test de insensibilidad: orden de documentos (ManifestFingerprintCalculator ordena internamente). ~450 ejemplos aleatorios generados. Corrección de causa raíz: `DocumentFingerprint.__post_init__` simplificado eliminando `islower()` (redundante con `all(c in "0123456789abcdef")`) que fallaba para hashes sin letras (ej: `"0"*64`). 9 tests passed.

#### Notas de implementación — Task 2.3.2

> 8 property-based tests para `OracleSemanticIdentityCalculator` en `tests/unit/test_framing_injectivity.py`. Tests de sensibilidad: node_id, content, node_type, strategy, order, cardinality (1 vs 2 nodos). Test de insensibilidad: sequence_id (metadata física no participa en framing). Estrategias con `blacklist_categories=("Cs",)` para excluir surrogates Unicode que Pydantic rechaza. ~400 ejemplos aleatorios generados. 8 tests passed.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-01 | `ground_truth_state` es `Optional[str]` sin validación explícita de `:`. En la práctica los valores vienen de `GroundTruthLifecycleState` enum (sin `:`), pero el contrato del DTO permite cualquier string. Riesgo bajo mientras el enum permanezca cerrado. | Findings Register §2.2 → IMPLEMENTATION_REQUIRED → Batch 1 → RESOLVED (2026-08-29) |

### 2.8 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-17 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- `document_id` tiene validación de dominio que excluye `:`. ✅
- `node_id` tiene validación de dominio que excluye `:`. ✅
- Tests de fail-fast verifican que valores inválidos son rechazados explícitamente. ✅
- Contratos de dominio están documentados en docstrings. ✅
- Tests de propiedad verifican inyectividad del encoding para `manifest_hash` y `oracle_hash`. ✅
- Conjunto de sentinels está documentado. ✅

### 2.9 Gate 2 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE (8 tasks) | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ (DF-01 → Batch 1 → RESOLVED) |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (442 passed, 5 skipped) | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** PASS  
**Fecha de verificación:** 2026-08-29

**Nota de resolución de DF-01 (post-Wave 2.3):**

Durante Wave 2.3 se identificó DF-01: `ground_truth_state` participa en el framing de `manifest_hash` pero carecía de contrato de dominio explícito (asimetría con `document_id` y `node_id`).

Siguiendo METHODOLOGY §6.6, el hallazgo se clasificó como `IMPLEMENTATION_REQUIRED` y se resolvió en **Batch 1** del Findings Register (no como Wave nueva del Execution Plan):

- `GroundTruthState` type alias en `core/shared/identity_contracts.py`
- Aplicación en `RawDocumentEntryDTO.ground_truth_state` y `CorpusDocumentMetadata.ground_truth_state`
- 6 tests de fail-fast en `tests/unit/test_corpus_models.py::TestGroundTruthStateDomainContract`
- Suite completa: 442 passed, 5 skipped
- Pyright: 0 errors

Esta resolución no modifica la estructura del Execution Plan (13 tasks originales) porque se ejecuta como Batch de resolución de findings, conforme a METHODOLOGY §6.6 punto 4.

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-08-27 | 17/17 | 5/5 | 0 | Formalización documental completa. Limpieza profunda de DC-08 eliminó I/O innecesario. |
| Gate 2 | 2026-08-29 | 15/15 | 8/8 | 1 (DF-01 → Batch 1 → RESOLVED) | Validación de dominio completa. Inyectividad del framing verificada con hypothesis. Corrección de causa raíz en DocumentFingerprint. DF-01 resuelto como Batch post-Wave 2.3. |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Verificar que todos los `document_id` existentes cumplen con el patrón (sin `:`) | Local | NADR-F17BIS-17 §5.1 R1-R4 | Grep PowerShell: 0 resultados | DONE |
| **MIG-02** | Verificar que todos los `node_id` existentes cumplen con el patrón (sin `:`) | Local | NADR-F17BIS-17 §5.1 R1-R4 | Grep PowerShell: 0 resultados | DONE |
| **MIG-03** | Ejecutar suite completa de tests de regresión | Local/CI | Todas las reglas | pytest: 442 passed, 5 skipped | DONE |

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
| Gate 1 | 5 | 17 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 8 | 15 | 0 | 0 | ✅ COMPLETED |
| **TOTAL** | **13** | **32** | **0** | **0** | ✅ COMPLETED |

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

#### NADR-F17BIS-15 v2.0

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-15 v2.0 §5.3 R10 | DONE | Wave 1.1 / Task 1.1.3 | Acoplamiento implícito de ASTSchemaVersion a CorpusVersion documentado y justificado en ManifestFingerprintCalculator |

#### NADR-F17BIS-16

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-16 §5.1 R1-R3 | DONE | Wave 1.1 / Task 1.1.1 | Documentación de OracleSemanticIdentityCalculator como contrato canónico |
| NADR-F17BIS-16 §5.2 R4-R8 | DONE | Wave 1.1 / Task 1.1.2, Wave 1.2 / Task 1.2.1 | Documentación de coexistencia de contratos de hashing + aclaración de docstring (DC-06) |
| NADR-F17BIS-16 §5.3 R9-R12 | DONE | Wave 1.1 / Task 1.1.3 | Justificación de ground_truth_state en manifest_hash (DC-03) |
| NADR-F17BIS-16 §5.4 R13-R16 | DONE | Wave 1.1 / Task 1.1.1, 1.1.2, 1.1.3 | Verificación de documentación de composición de identidad global |

#### Limpieza de Deuda Técnica

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| DC-06 (aclarar docstring) | DONE | Wave 1.2 / Task 1.2.1 | Docstring de compute_ast_hash corregido |
| DC-08 (limpiar campos huérfanos) | DONE | Wave 1.2 / Task 1.2.2 | Campos ground_truth_version y ground_truth_sha256 eliminados. Limpieza profunda de detected_hashes y target_version. |

### 7.2 Gate 2 — Rules Audit Board

#### NADR-F17BIS-17

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-17 §5.1 R1-R4 (document_id) | DONE | Wave 2.1 / Task 2.1.1, 2.1.2 | Validación con `DocumentId` type alias + 24 tests |
| NADR-F17BIS-17 §5.1 R1-R4 (node_id + parent_node_id) | DONE | Wave 2.2 / Task 2.2.1, 2.2.2 | Validación con `NodeId` type alias + 27 tests. spawn_fragment con constructor completo |
| NADR-F17BIS-17 §5.1 R1-R4 (ground_truth_state) | DONE | Batch 1 / DF-01 (post-Wave 2.3) | Validación con `GroundTruthState` type alias + 6 tests. Resuelto como Batch del Findings Register |
| NADR-F17BIS-17 §5.2 R5-R8 | DONE | Wave 2.3 / Task 2.3.1, 2.3.2 | 17 property-based tests con hypothesis. Inyectividad del framing verificada |
| NADR-F17BIS-17 §5.3 R9-R12 | DONE | Waves 2.1-2.3 + Batch 1 | Sentinels documentados. Contratos completos para los 4 campos del framing |
| NADR-F17BIS-17 §5.4 R13-R15 | DONE | Waves 2.1-2.3 + Batch 1 | Contratos documentados + verificación de inyectividad con property-based tests |

> **Nota de conteo:** Las reglas R1-R4 de NADR-F17BIS-17 §5.1 aparecen en múltiples filas porque fueron aplicadas a distintos campos (document_id, node_id + parent_node_id, ground_truth_state). Para el conteo del Status Dashboard y el Gate Completion Log, cada regla única se cuenta una sola vez. Total de reglas únicas de NADR-F17BIS-17: 15 (R1-R4 + R5-R8 + R9-R12 + R13-R15).

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