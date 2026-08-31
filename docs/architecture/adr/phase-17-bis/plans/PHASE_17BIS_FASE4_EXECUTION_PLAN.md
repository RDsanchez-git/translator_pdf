# PHASE_17BIS_FASE4_EXECUTION_PLAN v1.0.0
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.0
**Status:** APPROVED
**Date:** 2026-08-30
**Supersedes:** N/A
**Derived From:** 2 NADRs FROZEN (NADR-F17BIS-18, NADR-F17BIS-19) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Fase 4 (Scientific Verification). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-DRAFT | 2026-08-30 | Emisión inicial. Secuenciación de 3 Gates / 8 Waves / 37 tareas atómicas. |
| 1.0.0-APPROVED | 2026-08-30 | Corrección de contadores: Gate 2 (25→22 reglas), Gate 3 (8→7 reglas), Total (55→51 reglas). Nota de Prerrequisitos para Fase 6 agregada. Verificación CriticalityAwareCostContext × ZhangShashaEngine en Gate 1 Exit Criteria. Documento APROBADO. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
        │
        ▼
ADR_F17-BIS_04 (Scientific Verification — visión arquitectónica)
        │
        ▼
NADR-F17BIS-18 (Taxonomía de Criticidad — 22 reglas)
NADR-F17BIS-19 (Regresión Topológica Graduada — 29 reglas)
        │  Cada regla se identifica por: NADR-XX §sección Rregla
        ▼
PHASE_17BIS_FASE4_EXECUTION_PLAN (ESTE DOCUMENTO)
        │  Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
        ▼
FASE_4_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
        │  Mapea: Finding → Classification → Batch → Resolution → Status
        ▼
Implementación (commits, tests)
        │  Referencia reglas como Implementation Evidence
        ▼
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-18 §5.2 R3` → NADR-F17BIS-18, sección 5.2, regla 3.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (NADR-F17BIS-18 con 22 reglas y NADR-F17BIS-19 con 29 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_4_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

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

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §13. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2-§4)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§5)
- Status Dashboard (§8)
- Traceability Appendix (§9)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

### 1.6 Infraestructura Existente Reutilizable

Según HITO_4.1 y HITO_4.5, la siguiente infraestructura es reutilizable sin modificación:

| Componente | Ubicación | Fuente de Evidencia |
|---|---|---|
| `ZhangShashaEngine` | `core/benchmark/topology/engines/zhang_shasha/` | HITO_4.1 E-4.1-001 |
| `ForestDistanceCalculator` | `core/benchmark/topology/engines/zhang_shasha/forest.py` | HITO_4.1 E-4.1-001 |
| `PostorderIndexer` | `core/benchmark/topology/engines/zhang_shasha/indexer.py` | HITO_4.1 E-4.1-016 |
| `TreeEditDistanceEvaluator` | `core/benchmark/topology/evaluators/ted.py` | HITO_4.1 E-4.1-002 |
| `EntityRecallEvaluator` | `core/benchmark/topology/evaluators/recall.py` | HITO_4.1 E-4.1-003 |
| `LCSAnchorAlignmentStrategy` | `core/benchmark/topology/alignment/strategy.py` | HITO_4.1 E-4.1-012 |
| `HeadingAnchorPartitionStrategy` | `core/benchmark/topology/partitioning/heading.py` | HITO_4.1 E-4.1-013 |
| `MaxBoundNormalizationPolicy` | `core/benchmark/topology/policies/normalization.py` | HITO_4.1 E-4.1-014 |
| `WorstCaseOverflowStrategy` | `core/benchmark/topology/policies/overflow.py` | HITO_4.1 E-4.1-015 |
| `OracleSemanticIdentityCalculator` | `core/benchmark/ground_truth/identity.py` | HITO_4.3 E-4.3-012 |
| `BaselineCompletenessVerifier` | `core/benchmark/ground_truth/completeness.py` | HITO_4.3 E-4.3-011 |
| `SealedOracle` | `core/benchmark/ground_truth/models.py` | HITO_4.3 E-4.3-001 |
| `build_extraction_pipeline()` | `apps/bootstrap/pipeline_factory.py` | HITO_4.5 E-4.5-004 |
| `ContentNodeType` | `core/ast/enums.py` | HITO_4.2 E-4.2-008 |
| `UnitCostContext` | `core/benchmark/topology/costs/unit.py` | HITO_4.1 E-4.1-005 |
| `ParserEvaluationStrategy` | `core/benchmark/topology/strategies.py` | HITO_4.1 E-4.1-007 |
| `EvaluationStrategy` (Protocol) | `core/benchmark/topology/ports.py` | HITO_4.1 |
| `TreeEditCostContext` (Protocol) | `core/benchmark/topology/ports.py` | HITO_4.1 |
| `TopologicalEvaluationReport` | `core/benchmark/topology/models.py` | HITO_4.1 |
| `ConfusionMatrix` | `core/benchmark/topology/models.py` | HITO_4.1 |

---

## 2. GATE 1 — TAXONOMÍA DE CRITICIDAD Y COSTOS PONDERADOS

**Objective:** Materializar la capacidad de dominio de clasificación de nodos por criticidad científica (DC-06), implementando el enum `NodeCriticality`, la política de mapeo `CriticalityPolicy`, el contexto de costos ponderados `CriticalityAwareCostContext`, y el mecanismo de veredicto por criticidad. Al cierre de este Gate, el sistema posee la taxonomía completa y la ponderación de costos está operativa.
**Execution Mode:** Secuencial
**Rollback Plan:** `git revert` de los commits del Gate 1; el sistema retorna al estado con `UnitCostContext` uniforme.
**Gate Status:** ⏳ PENDING
**NADRs afectados:** NADR-F17BIS-18 (22 reglas)

### 2.1 Wave 1.1 — NodeCriticality y CriticalityPolicy (NADR-18 §5.1, §5.2)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Crear enum `NodeCriticality` con exactamente tres niveles: `CRITICAL`, `WARNING`, `INFO`. Ubicación: `core/benchmark/topology/criticality/models.py`. Inmutable, `frozen=True`, con documentación de cada nivel. | NADR-18 §5.1 R2 | Low | — | TODO |
| **1.1.2** | Crear protocolo `CriticalityPolicy` (Protocol) con método `criticality_of(node_type: ContentNodeType) -> NodeCriticality`. Ubicación: `core/benchmark/topology/criticality/ports.py`. | NADR-18 §5.1 R1 | Low | 1.1.1 | TODO |
| **1.1.3** | Implementar `DefaultCriticalityPolicy` con el mapeo canónico inicial: CRITICAL → `DISPLAY_EQUATION`, `INLINE_EQUATION`, `TABLE_SIMPLE`, `TABLE_COMPLEX`; WARNING → `HEADING`, `PARAGRAPH`, `CODE`; INFO → `IMAGE`, `CAPTION`, `LIST`, `COMPOSITE_BLOCK`. Declarativo, centralizado, extensible. Ubicación: `core/benchmark/topology/criticality/policy.py`. | NADR-18 §5.1 R1, R3, R4, R5, R6, R7; §5.2 R8, R9 | Medium | 1.1.1, 1.1.2 | TODO |
| **1.1.4** | Tests unitarios de `NodeCriticality` y `DefaultCriticalityPolicy`: cobertura exhaustiva de los 11 `ContentNodeType`, fallo explícito ante tipo sin clasificación (extensibilidad), inmutabilidad. Ubicación: `tests/unit/test_criticality_policy.py`. | NADR-18 §5.1 R1, R2; §5.2 R9 | Low | 1.1.1, 1.1.2, 1.1.3 | TODO |

#### Notas de implementación — Task 1.1.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.1.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.1.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.1.4

> {Se actualiza al completar la Task.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.2 Wave 1.2 — CriticalityAwareCostContext (NADR-18 §5.3)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Crear `CriticalityAwareCostContext` que implementa el protocolo `TreeEditCostContext` existente (`core/benchmark/topology/ports.py`). Debe ponderar `deletion_cost`, `insertion_cost` y `substitution_cost` según la criticidad del nodo inyectada vía `CriticalityPolicy`. Configurable mediante pesos inyectados (no hardcodeados). Ubicación: `core/benchmark/topology/criticality/costs.py`. | NADR-18 §5.3 R11, R12, R13, R14, R15 | Medium | 1.1.1, 1.1.2, 1.1.3 | TODO |
| **1.2.2** | Definir pesos por defecto documentados como "propuesta inicial sujeta a validación empírica". Los pesos deben garantizar: `CRITICAL > WARNING > INFO` en penalización. Documentar que estos valores NO son definitivos. | NADR-18 §5.3 R12, R14 | Medium | 1.2.1 | TODO |
| **1.2.3** | Tests unitarios de `CriticalityAwareCostContext`: determinismo (mismos inputs → mismo costo), orden estricto CRITICAL > WARNING > INFO, configuración de pesos, integración con `ZhangShashaEngine` existente sin modificarlo. Ubicación: `tests/unit/test_criticality_costs.py`. | NADR-18 §5.3 R12, R15 | Medium | 1.2.1, 1.2.2 | TODO |

#### Notas de implementación — Task 1.2.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.2.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.2.3

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-18 §5.3 R12 aparece en Tasks 1.2.1, 1.2.2 y 1.2.3. Task 1.2.1 implementa la capacidad de configuración. Task 1.2.2 define los valores por defecto. Task 1.2.3 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.3 Wave 1.3 — Veredicto por Criticidad y Trazabilidad (NADR-18 §5.4, §5.5)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Implementar el mecanismo de detección de pérdida de nodo CRITICAL: dado un `ConfusionMatrix` o resultado de recall, si hay falsos negativos en nodos `CRITICAL`, emitir señal de fallo absoluto. Este mecanismo es independiente del NSS y tiene precedencia sobre él. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R16, R17 | High | 1.1.3, 1.2.1 | TODO |
| **1.3.2** | Implementar mecanismo de veredicto para nodos WARNING: si la pérdida de nodos WARNING supera un umbral configurable, emitir WARNING. Pérdida aislada de nodos WARNING MAY emitirse como veredicto de aprobación con observación. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R18 | Medium | 1.3.1 | TODO |
| **1.3.3** | Implementar mecanismo de veredicto para nodos INFO: la pérdida de nodos INFO MUST emitirse como veredicto de aprobación con observación. La pérdida de nodos INFO MUST NOT causar un veredicto de fallo. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R19 | Low | 1.3.1 | TODO |
| **1.3.4** | Implementar trazabilidad de clasificación: toda evaluación topológica que use la taxonomía de criticidad MUST registrar la clasificación aplicada a cada nodo evaluado. Implementar evento de gobernanza para reclasificaciones. Ubicación: `core/benchmark/topology/criticality/traceability.py`. | NADR-18 §5.5 R20, R21, R22 | Medium | 1.1.3, 1.3.1 | TODO |
| **1.3.5** | Tests unitarios de veredicto por criticidad: pérdida CRITICAL → fallo absoluto independiente del NSS; pérdida WARNING → veredicto según umbral; pérdida INFO → PASS con observación. Tests de precedencia del mecanismo absoluto. Ubicación: `tests/unit/test_criticality_verdict.py`. | NADR-18 §5.4 R16, R17, R18, R19 | High | 1.3.1, 1.3.2, 1.3.3 | TODO |

#### Notas de implementación — Task 1.3.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.3.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.3.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.3.4

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 1.3.5

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-18 §5.4 R16, R17 aparecen en Tasks 1.3.1 y 1.3.5. Task 1.3.1 implementa el mecanismo. Task 1.3.5 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.4 Gate 1 Exit Criteria

Todas las reglas de NADR-F17BIS-18 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- `NodeCriticality` enum existe con exactamente tres niveles (`CRITICAL`, `WARNING`, `INFO`).
- `CriticalityPolicy` mapea todos los `ContentNodeType` existentes sin excepción.
- `CriticalityAwareCostContext` implementa `TreeEditCostContext` con ponderación determinista.
- Tests verifican que pérdida de nodo CRITICAL emite fallo absoluto independiente del NSS.
- Trazabilidad de clasificación registrada por cada nodo evaluado.
- **Verificar que `CriticalityAwareCostContext` no rompe los tests existentes de `ZhangShashaEngine` cuando se usa con `UnitCostContext` como fallback.** La suite `test_zhang_shasha.py` debe permanecer en verde sin modificación.
- Pyright: 0 errors, 0 warnings.
- Suite de tests completa en verde (incluyendo tests existentes de fases anteriores).

### 2.5 Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ❌ |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ❌ |
| 3 | Gate Exit Criteria satisfechos | ❌ |
| 4 | Hallazgos identificados derivados al Findings Register | ❌ |
| 5 | Pyright: 0 errors, 0 warnings | ❌ |
| 6 | Tests: suite completa en verde | ❌ |
| 7 | Notas de implementación completas para todas las Tasks | ❌ |
| 8 | Tests existentes de ZhangShashaEngine en verde con CriticalityAwareCostContext | ❌ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 3. GATE 2 — REGRESIÓN TOPOLÓGICA GRADUADA Y ADAPTADOR BASELINE→EVALUACIÓN

**Objective:** Materializar la capacidad de emisión de veredictos graduados (PASS/WARNING/HARD_FAIL), el doble mecanismo de protección (NSS ponderado + regla absoluta CRITICAL), el adaptador que conecta el `SealedOracle` con la evaluación topológica, y la estrategia de evaluación de regresión. Al cierre de este Gate, el sistema puede evaluar el runtime contra el oráculo sellado con veredicto graduado.
**Execution Mode:** Secuencial
**Rollback Plan:** `git revert` de los commits del Gate 2; el sistema retorna al estado con `ParserEvaluationStrategy` únicamente.
**Gate Status:** ⏳ PENDING
**NADRs afectados:** NADR-F17BIS-19 (§5.1-§5.4, §5.6)

### 3.1 Wave 2.1 — RegressionVerdict y RegressionThresholds (NADR-19 §5.1, §5.3)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Crear enum `RegressionVerdict` con exactamente tres niveles: `PASS`, `WARNING`, `HARD_FAIL`. Inmutable, `frozen=True`. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R1 | Low | Gate 1 | TODO |
| **2.1.2** | Crear `RegressionThresholds` como DTO configurable: `nss_hard_fail: float`, `nss_warning: float`. Valores por defecto documentados como "propuesta inicial sujeta a validación empírica". Inmutable. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R4, R5, R6, R7; §5.3 R12, R13, R14 | Medium | 2.1.1 | TODO |
| **2.1.3** | Implementar lógica de agregación por corpus: el veredicto por corpus MUST ser el peor veredicto de todos los documentos individuales. Si al menos un documento es HARD_FAIL, el corpus es HARD_FAIL. Si al menos un documento es WARNING y ninguno es HARD_FAIL, el corpus es WARNING. Solo si todos los documentos son PASS, el corpus es PASS. Ubicación: `core/benchmark/topology/regression/aggregation.py`. | NADR-19 §5.1 R2, R3 | Medium | 2.1.1 | TODO |
| **2.1.4** | Tests unitarios de `RegressionVerdict`, `RegressionThresholds` y agregación por corpus. Ubicación: `tests/unit/test_regression_verdict.py`. | NADR-19 §5.1 R1, R2, R3; §5.3 R12 | Low | 2.1.1, 2.1.2, 2.1.3 | TODO |

#### Notas de implementación — Task 2.1.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.1.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.1.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.1.4

> {Se actualiza al completar la Task.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.2 Wave 2.2 — Doble Mecanismo de Protección (NADR-19 §5.2)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Implementar Mecanismo 1 (NSS ponderado por criticidad): calcular NSS utilizando `CriticalityAwareCostContext` (Gate 1) en lugar de `UnitCostContext`. Integrar con `TreeEditDistanceEvaluator` existente sin modificarlo (inyección de cost_context). | NADR-19 §5.2 R8 | High | Gate 1, 2.1.2 | TODO |
| **2.2.2** | Implementar Mecanismo 2 (Regla absoluta de pérdida CRITICAL): si hay pérdida de nodos CRITICAL, emitir HARD_FAIL independientemente del NSS. Este mecanismo tiene precedencia sobre el Mecanismo 1. Utilizar el componente de veredicto por criticidad del Gate 1 (Task 1.3.1). | NADR-19 §5.2 R9, R10 | High | Gate 1 (1.3.1), 2.2.1 | TODO |
| **2.2.3** | Implementar la complementariedad de ambos mecanismos: el veredicto final es el peor resultado de ambos. Documentar el ejemplo canónico: 1 nodo CRITICAL perdido en 1000 nodos → NSS alto pero HARD_FAIL. Ubicación: `core/benchmark/topology/regression/mechanism.py`. | NADR-19 §5.2 R8, R9, R10, R11 | High | 2.2.1, 2.2.2 | TODO |
| **2.2.4** | Tests unitarios del doble mecanismo: NSS ponderado, regla absoluta CRITICAL, precedencia, complementariedad, ejemplo canónico de 1 CRITICAL en 1000 nodos. Ubicación: `tests/unit/test_regression_mechanism.py`. | NADR-19 §5.2 R8, R9, R10, R11 | High | 2.2.1, 2.2.2, 2.2.3 | TODO |

#### Notas de implementación — Task 2.2.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.2.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.2.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.2.4

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.2 R8, R9, R10, R11 aparecen en Tasks 2.2.1, 2.2.2, 2.2.3 y 2.2.4. Tasks 2.2.1 y 2.2.2 implementan cada mecanismo por separado. Task 2.2.3 integra ambos. Task 2.2.4 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.3 Wave 2.3 — Adaptador Baseline→Evaluación (NADR-19 §5.4)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Crear `RegressionAdapter` que verifica la integridad criptográfica del oráculo mediante `OracleSemanticIdentityCalculator.calculate(oracle.nodes)` comparado contra el `oracle_hash` del manifiesto. Si no coincide, abortar con `OracleIntegrityError` (Fail-Fast). Ubicación: `core/benchmark/topology/regression/adapter.py`. | NADR-19 §5.4 R15, R18, R19 | High | Gate 1 | TODO |
| **2.3.2** | Implementar verificación de `ground_truth_state == SEALED` antes de evaluar. Si el estado no es SEALED, abortar con `OracleNotSealedError`. Utilizar el campo `ground_truth_state` de `CorpusDocumentMetadata` existente. | NADR-19 §5.4 R16, R18, R19 | Medium | 2.3.1 | TODO |
| **2.3.3** | Implementar verificación de completitud biyectiva mediante `BaselineCompletenessVerifier` antes de evaluar. Si la verificación falla, abortar con `IncompleteBaselineError`. | NADR-19 §5.4 R17, R18, R19 | Medium | 2.3.1 | TODO |
| **2.3.4** | Integrar las tres verificaciones (2.3.1, 2.3.2, 2.3.3) en secuencia Fail-Fast dentro del `RegressionAdapter`. El adaptador MUST reutilizar los evaluadores existentes sin modificarlos. | NADR-19 §5.4 R15, R16, R17, R18, R19 | High | 2.3.1, 2.3.2, 2.3.3 | TODO |
| **2.3.5** | Tests unitarios del adaptador: verificación de oracle_hash (match/mismatch), verificación de ground_truth_state (SEALED/no SEALED), verificación de completitud (completa/incompleta), Fail-Fast ante cualquier fallo. Ubicación: `tests/unit/test_regression_adapter.py`. | NADR-19 §5.4 R15, R16, R17, R18, R19 | High | 2.3.1, 2.3.2, 2.3.3, 2.3.4 | TODO |

#### Notas de implementación — Task 2.3.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.3.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.3.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.3.4

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.3.5

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.4 R15-R19 aparecen en Tasks 2.3.1 a 2.3.5. Tasks 2.3.1-2.3.3 implementan cada verificación por separado. Task 2.3.4 integra las tres. Task 2.3.5 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.4 Wave 2.4 — RegressionEvaluationStrategy (NADR-19 §5.1, §5.2, §5.6)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.4.1** | Crear `RegressionEvaluationStrategy` que implementa el protocolo `EvaluationStrategy` existente (`core/benchmark/topology/ports.py`). Orquesta: (1) verificación de integridad, (2) evaluación TED ponderada, (3) evaluación Recall ponderada, (4) doble mecanismo de protección, (5) emisión de veredicto graduado. Ubicación: `core/benchmark/topology/regression/strategy.py`. | NADR-19 §5.1 R1, R2; §5.2 R8, R9, R10, R11 | High | 2.2.3, 2.3.4 | TODO |
| **2.4.2** | Implementar interacción con `EntityRecallEvaluator` ponderada por criticidad: un recall bajo de nodos CRITICAL se trata con mayor severidad que un recall bajo de nodos INFO. El recall se evalúa por tipo de nodo, ponderado por criticidad. | NADR-19 §5.6 R23, R24, R25 | Medium | 2.4.1 | TODO |
| **2.4.3** | Crear `RegressionEvaluationReport` que extiende `TopologicalEvaluationReport` existente con el campo `verdict: RegressionVerdict`. Inmutable. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R3 | Medium | 2.1.1, 2.4.1 | TODO |
| **2.4.4** | Tests unitarios de `RegressionEvaluationStrategy`: evaluación completa con oráculo válido, emisión de veredicto correcto, integración con `RegressionAdapter`, determinismo, interacción con recall ponderado. Ubicación: `tests/unit/test_regression_strategy.py`. | NADR-19 §5.1 R1, R2, R3; §5.6 R23, R24, R25 | High | 2.4.1, 2.4.2, 2.4.3 | TODO |

#### Notas de implementación — Task 2.4.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.4.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.4.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 2.4.4

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.1 R1, R2 aparecen en Tasks 2.4.1 y 2.4.4. Task 2.4.1 implementa la estrategia. Task 2.4.4 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.5 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-19 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- `RegressionVerdict` enum existe con exactamente tres niveles (`PASS`, `WARNING`, `HARD_FAIL`).
- `RegressionThresholds` tiene umbrales configurables con valores por defecto documentados.
- Doble mecanismo de protección implementado: NSS ponderado + regla absoluta CRITICAL.
- `RegressionAdapter` verifica oracle_hash, ground_truth_state == SEALED, y completitud biyectiva antes de evaluar.
- Fallo en cualquier verificación previa emite error explícito (Fail-Fast).
- `RegressionEvaluationStrategy` implementa `EvaluationStrategy` y orquesta la evaluación completa.
- Interacción con `EntityRecallEvaluator` ponderada por criticidad.
- Pyright: 0 errors, 0 warnings.
- Suite de tests completa en verde (incluyendo tests existentes de fases anteriores).

### 3.6 Gate 2 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ❌ |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ❌ |
| 3 | Gate Exit Criteria satisfechos | ❌ |
| 4 | Hallazgos identificados derivados al Findings Register | ❌ |
| 5 | Pyright: 0 errors, 0 warnings | ❌ |
| 6 | Tests: suite completa en verde | ❌ |
| 7 | Notas de implementación completas para todas las Tasks | ❌ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 4. GATE 3 — ENTRY POINT DE REGRESIÓN, REPORTE Y TESTS DE REGRESIÓN

**Objective:** Materializar el entry point de regresión que ejecuta la evaluación del runtime contra el oráculo sellado reutilizando el composition root del pipeline de producción, el reporte de regresión determinista y consumible por CI/CD, y los tests de regresión que certifican la implementación. Al cierre de este Gate, el sistema posee un mecanismo completo de regresión científica ejecutable.
**Execution Mode:** Secuencial
**Rollback Plan:** `git revert` de los commits del Gate 3; el sistema retorna al estado sin entry point de regresión.
**Gate Status:** ⏳ PENDING
**NADRs afectados:** NADR-F17BIS-19 (§5.5, §5.7)

### 4.1 Wave 3.1 — Entry Point de Regresión (NADR-19 §5.5)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Crear entry point CLI `tools/evaluation/run_regression.py` que orquesta la evaluación de regresión del runtime contra el oráculo sellado. MUST reutilizar `build_extraction_pipeline()` para generar el runtime AST. MUST NOT crear un pipeline de extracción separado. | NADR-19 §5.5 R20, R21 | High | Gate 2 | TODO |
| **3.1.2** | El entry point MUST ejecutar: (1) cargar manifiesto, (2) verificar completitud biyectiva, (3) para cada documento: verificar integridad, generar runtime AST, evaluar contra SealedOracle, emitir veredicto, (4) agregar veredictos por corpus. | NADR-19 §5.5 R20, R21, R22 | High | 3.1.1 | TODO |
| **3.1.3** | Implementar exit code diferenciado: `0` = PASS (todos los documentos PASS), `1` = WARNING (al menos un WARNING, ningún HARD_FAIL), `2` = HARD_FAIL (al menos un HARD_FAIL). | NADR-19 §5.5 R22 | Medium | 3.1.2 | TODO |
| **3.1.4** | Tests de integración del entry point: ejecución con corpus válido, emisión de veredictos correctos, exit codes correctos, determinismo, Fail-Fast ante oráculo no verificado. Ubicación: `tests/integration/test_regression_entry_point.py`. | NADR-19 §5.5 R20, R21, R22; §5.4 R18, R19 | High | 3.1.1, 3.1.2, 3.1.3 | TODO |

#### Notas de implementación — Task 3.1.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.1.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.1.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.1.4

> {Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.5 R20, R21, R22 aparecen en Tasks 3.1.1, 3.1.2, 3.1.3 y 3.1.4. Tasks 3.1.1-3.1.3 implementan el entry point. Task 3.1.4 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.2 Wave 3.2 — Reporte de Regresión (NADR-19 §5.7)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Crear `RegressionReport` que incluye veredicto por documento y por corpus, NSS calculado, métricas ponderadas por criticidad, y detalle por documento. Formato JSON estructurado. Ubicación: `core/benchmark/topology/regression/report.py`. | NADR-19 §5.7 R26, R27 | Medium | Gate 2 | TODO |
| **3.2.2** | Implementar formato Markdown legible para humanos como salida secundaria. Reutilizar `MarkdownReportFormatter` existente en `tools/evaluation/infrastructure/formatters.py` si es compatible. | NADR-19 §5.7 R28 | Low | 3.2.1 | TODO |
| **3.2.3** | Garantizar determinismo del reporte: ausencia de marcas de tiempo físicas no inyectadas. Si se requiere marca temporal, MUST ser inyectada como parámetro externo. | NADR-19 §5.7 R29 | Low | 3.2.1 | TODO |
| **3.2.4** | Tests unitarios de reporting: determinismo, contenido correcto, formato JSON válido, ausencia de marcas de tiempo físicas. Ubicación: `tests/unit/test_regression_report.py`. | NADR-19 §5.7 R26, R27, R28, R29 | Medium | 3.2.1, 3.2.2, 3.2.3 | TODO |

#### Notas de implementación — Task 3.2.1

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.2.2

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.2.3

> {Se actualiza al completar la Task.}

#### Notas de implementación — Task 3.2.4

> {Se actualiza al completar la Task.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.3 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-19 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- Entry point CLI `run_regression.py` existe y orquesta la evaluación de regresión.
- Entry point reutiliza `build_extraction_pipeline()` sin crear pipeline separado.
- Entry point verifica Fail-Fast ante oráculo no verificado.
- `RegressionReport` incluye veredicto por documento y por corpus.
- Formato JSON estructurado y formato Markdown legible.
- Reporte determinista: ausencia de marcas de tiempo físicas no inyectadas.
- Exit code diferenciado: 0 = PASS, 1 = WARNING, 2 = HARD_FAIL.
- Pyright: 0 errors, 0 warnings.
- Suite de tests completa en verde (incluyendo tests existentes de fases anteriores).

### 4.4 Gate 3 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ❌ |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ❌ |
| 3 | Gate Exit Criteria satisfechos | ❌ |
| 4 | Hallazgos identificados derivados al Findings Register | ❌ |
| 5 | Pyright: 0 errors, 0 warnings | ❌ |
| 6 | Tests: suite completa en verde | ❌ |
| 7 | Notas de implementación completas para todas las Tasks | ❌ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 5. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | — | —/22 | —/12 | — | Taxonomía de criticidad y costos ponderados |
| Gate 2 | — | —/22 | —/17 | — | Regresión topológica y adaptador |
| Gate 3 | — | —/7 | —/8 | — | Entry point, reporte y tests |

---

## 6. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-4.1** | Verificar que `NodeCriticality` enum existe con tres niveles y mapea todos los `ContentNodeType` | Local | NADR-18 §5.1 R1, R2, R3 | Script de verificación | TODO |
| **MIG-4.2** | Verificar que `CriticalityAwareCostContext` implementa `TreeEditCostContext` con ponderación determinista | Local | NADR-18 §5.3 R11, R12, R15 | Script de verificación | TODO |
| **MIG-4.3** | Verificar que `RegressionAdapter` verifica oracle_hash, ground_truth_state, y completitud biyectiva antes de evaluar | Local | NADR-19 §5.4 R15, R16, R17, R18, R19 | Script de verificación | TODO |
| **MIG-4.4** | Verificar que `run_regression.py` ejecuta la evaluación de regresión del runtime contra el oráculo sellado | Local | NADR-19 §5.5 R20, R21, R22 | Script de verificación | TODO |
| **MIG-4.5** | Verificar que el reporte de regresión es determinista y consumible por CI/CD | Local/CI | NADR-19 §5.7 R26, R27, R28, R29 | Script de verificación | TODO |

---

## 7. GLOBAL DoD (Definition of Done)

La Fase 4 (Scientific Verification) se considera oficialmente completada cuando:

```text
{All rules in NADR-F17BIS-18} ∪ {All rules in NADR-F17BIS-19} − {Rules with DONE status in §9} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 8. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§9), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 0 | 0 | 0 | 22 | ⏳ PENDING |
| Gate 2 | 0 | 0 | 0 | 22 | ⏳ PENDING |
| Gate 3 | 0 | 0 | 0 | 7 | ⏳ PENDING |
| **TOTAL** | **0** | **0** | **0** | **51** | ⏳ PENDING |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2-§4)
2. Se agregan las Notas de implementación de la Task (§2.{X}.{Y})
3. Se actualiza el `Derived Status` de sus reglas en §9
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.5, §3.6, §4.4)

---

## 9. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2-§4); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 9.1 Gate 1 — Rules Audit Board (NADR-F17BIS-18)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-18 §5.1 R1 | PENDING | Wave 1.1 / Task 1.1.2, 1.1.3, 1.1.4 | — |
| NADR-18 §5.1 R2 | PENDING | Wave 1.1 / Task 1.1.1, 1.1.4 | — |
| NADR-18 §5.1 R3 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.1 R4 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.1 R5 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.1 R6 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.1 R7 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.2 R8 | PENDING | Wave 1.1 / Task 1.1.3 | — |
| NADR-18 §5.2 R9 | PENDING | Wave 1.1 / Task 1.1.3, 1.1.4 | — |
| NADR-18 §5.2 R10 | PENDING | Wave 1.3 / Task 1.3.4 | — |
| NADR-18 §5.3 R11 | PENDING | Wave 1.2 / Task 1.2.1 | — |
| NADR-18 §5.3 R12 | PENDING | Wave 1.2 / Task 1.2.1, 1.2.2, 1.2.3 | — |
| NADR-18 §5.3 R13 | PENDING | Wave 1.2 / Task 1.2.1 | — |
| NADR-18 §5.3 R14 | PENDING | Wave 1.2 / Task 1.2.2 | — |
| NADR-18 §5.3 R15 | PENDING | Wave 1.2 / Task 1.2.3 | — |
| NADR-18 §5.4 R16 | PENDING | Wave 1.3 / Task 1.3.1, 1.3.5 | — |
| NADR-18 §5.4 R17 | PENDING | Wave 1.3 / Task 1.3.1, 1.3.5 | — |
| NADR-18 §5.4 R18 | PENDING | Wave 1.3 / Task 1.3.2, 1.3.5 | — |
| NADR-18 §5.4 R19 | PENDING | Wave 1.3 / Task 1.3.3, 1.3.5 | — |
| NADR-18 §5.5 R20 | PENDING | Wave 1.3 / Task 1.3.4 | — |
| NADR-18 §5.5 R21 | PENDING | Wave 1.3 / Task 1.3.4 | — |
| NADR-18 §5.5 R22 | PENDING | Wave 1.3 / Task 1.3.4 | — |

### 9.2 Gate 2 — Rules Audit Board (NADR-F17BIS-19 §5.1-§5.4, §5.6)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-19 §5.1 R1 | PENDING | Wave 2.1 / Task 2.1.1, 2.1.4 | — |
| NADR-19 §5.1 R2 | PENDING | Wave 2.1 / Task 2.1.3, 2.1.4; Wave 2.4 / Task 2.4.1 | — |
| NADR-19 §5.1 R3 | PENDING | Wave 2.1 / Task 2.1.3, 2.1.4; Wave 2.4 / Task 2.4.3 | — |
| NADR-19 §5.1 R4 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.1 R5 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.1 R6 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.1 R7 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.2 R8 | PENDING | Wave 2.2 / Task 2.2.1, 2.2.3; Wave 2.4 / Task 2.4.1 | — |
| NADR-19 §5.2 R9 | PENDING | Wave 2.2 / Task 2.2.2, 2.2.3; Wave 2.4 / Task 2.4.1 | — |
| NADR-19 §5.2 R10 | PENDING | Wave 2.2 / Task 2.2.2, 2.2.3; Wave 2.4 / Task 2.4.1 | — |
| NADR-19 §5.2 R11 | PENDING | Wave 2.2 / Task 2.2.3; Wave 2.4 / Task 2.4.1 | — |
| NADR-19 §5.3 R12 | PENDING | Wave 2.1 / Task 2.1.2, 2.1.4 | — |
| NADR-19 §5.3 R13 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.3 R14 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-19 §5.4 R15 | PENDING | Wave 2.3 / Task 2.3.1, 2.3.4, 2.3.5 | — |
| NADR-19 §5.4 R16 | PENDING | Wave 2.3 / Task 2.3.2, 2.3.4, 2.3.5 | — |
| NADR-19 §5.4 R17 | PENDING | Wave 2.3 / Task 2.3.3, 2.3.4, 2.3.5 | — |
| NADR-19 §5.4 R18 | PENDING | Wave 2.3 / Task 2.3.1, 2.3.2, 2.3.3, 2.3.4, 2.3.5; Wave 3.1 / Task 3.1.4 | — |
| NADR-19 §5.4 R19 | PENDING | Wave 2.3 / Task 2.3.1, 2.3.2, 2.3.3, 2.3.4, 2.3.5; Wave 3.1 / Task 3.1.4 | — |
| NADR-19 §5.6 R23 | PENDING | Wave 2.4 / Task 2.4.2 | — |
| NADR-19 §5.6 R24 | PENDING | Wave 2.4 / Task 2.4.2 | — |
| NADR-19 §5.6 R25 | PENDING | Wave 2.4 / Task 2.4.2 | — |

### 9.3 Gate 3 — Rules Audit Board (NADR-F17BIS-19 §5.5, §5.7)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-19 §5.5 R20 | PENDING | Wave 3.1 / Task 3.1.1, 3.1.2, 3.1.4 | — |
| NADR-19 §5.5 R21 | PENDING | Wave 3.1 / Task 3.1.1, 3.1.2, 3.1.4 | — |
| NADR-19 §5.5 R22 | PENDING | Wave 3.1 / Task 3.1.3, 3.1.4 | — |
| NADR-19 §5.7 R26 | PENDING | Wave 3.2 / Task 3.2.1, 3.2.4 | — |
| NADR-19 §5.7 R27 | PENDING | Wave 3.2 / Task 3.2.1, 3.2.4 | — |
| NADR-19 §5.7 R28 | PENDING | Wave 3.2 / Task 3.2.2, 3.2.4 | — |
| NADR-19 §5.7 R29 | PENDING | Wave 3.2 / Task 3.2.3, 3.2.4 | — |

---

## 10. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_4_DEFERRED_FINDINGS_REGISTER.md
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

## 11. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **Este Execution Plan** define exclusivamente la secuencia operativa de la Fase 4 (el CÓMO y el CUÁNDO).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta fase (NADR-F17BIS-18, NADR-F17BIS-19).
* La **visión arquitectónica** (el QUÉ y el POR QUÉ) se define en el ADR_F17-BIS_04.
* Los **hallazgos identificados durante la implementación, su clasificación y resolución** se registran en el Deferred Findings Register (`FASE_4_DEFERRED_FINDINGS_REGISTER.md`).

Este documento **no prescribe implementaciones específicas, criterios de revisión de código ni registro de hallazgos.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este Execution Plan mediante los NADRs y el ADR correspondientes.

---

## 12. FUTURE WORK

> Notas sobre mejoras futuras del proceso de trazabilidad, automatización del appendix, etc.
>
> - Automatización del cálculo de contadores del Status Dashboard (§8) mediante script que parsee el Traceability Appendix (§9).
> - Integración del regression gate en CI/CD (pertenece a Fase 6 — Continuous Verification).
> - Expansión del corpus de calibración de 5 a 20-30 documentos (pertenece a Fase 5 — Baseline Certification).
> - Validación empírica de los pesos de criticidad por defecto sobre un corpus más amplio (pertenece a Fase 5).
> - Remediación de tests tautológicos identificados en HITO_0.4.4_C5 (C5-R01, C5-R02, C5-R03) (pertenece a Fase 5/6).

### Nota de Prerrequisitos para Fase 6

> Los prerequisitos de testing y CI identificados en HITO_4.4 (remediación de tests tautológicos, verificación de `pyproject.toml`, verificación de `.github/workflows/ci.yml`, configuración de Required Status Checks) son responsabilidad de la **Fase 6 (Continuous Verification)** y deben ser secuenciados en el Execution Plan de la Fase 6, gobernados por NADR-10 (Regression Gates & CI Automation).
>
> La Fase 4 define la semántica de regresión graduada y el entry point ejecutable. La Fase 6 integra esa semántica en la infraestructura de CI/CD como compuerta de merge automatizada.

---

## 13. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 13.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2-§4)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 13.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2-§4)
2. Redactar las **Notas de implementación** de la Task (§2.{X}.{Y})
3. Actualizar el `Derived Status` de las reglas implementadas en §9
4. Recalcular los contadores del Status Dashboard (§8)
5. Verificar que las reglas implementadas no aparecen como PENDING en §9

### 13.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§2.{X}.{Z})
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 13.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§2.5, §3.6, §4.4)
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§5)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 13.5 Al cancelar una operación de Deployment

1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§6)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§13.3)

### 13.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.