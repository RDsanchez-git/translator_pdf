# PHASE_17BIS_FASE4_EXECUTION_PLAN v1.0.3
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.3
**Status:** ✅ FASE 4 COMPLETED (Gate 1 ✅, Gate 2 ✅, Gate 3 ✅)
**Date:** 2026-09-02
**Supersedes:** v1.0.2
**Derived From:** 2 NADRs FROZEN (NADR-F17BIS-18, NADR-F17BIS-19) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Fase 4 (Scientific Verification). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-DRAFT | 2026-08-30 | Emisión inicial. Secuenciación de 3 Gates / 8 Waves / 37 tareas atómicas. |
| 1.0.0-APPROVED | 2026-08-30 | Corrección de contadores: Gate 2 (25→22 reglas), Gate 3 (8→7 reglas), Total (55→51 reglas). Nota de Prerrequisitos para Fase 6 agregada. Verificación CriticalityAwareCostContext × ZhangShashaEngine en Gate 1 Exit Criteria. Documento APROBADO. |
| 1.0.1 | 2026-08-30 | **Gate 1 COMPLETED.** 12/12 tasks, 22/22 reglas NADR-18 implementadas. 10 archivos creados, 66 tests unitarios. Pyright 0 errors, pytest 508 passed. Zero-touch sobre infraestructura existente. |
| 1.0.2 | 2026-08-30 | **Gate 2 COMPLETED.** 17/17 tasks, 22/22 reglas NADR-19 (§5.1-§5.4, §5.6) implementadas. 12 archivos creados, 78 tests unitarios. Pyright 0 errors, pytest 586 passed. Zero-touch. 0 DF/GF durante implementación. Correcciones P0-1 (doble llamada evaluate) y P1 (overall_score fail-fast) aplicadas. |
| 1.0.3 | 2026-09-02 | **Gate 3 COMPLETED — FASE 4 OFICIALMENTE COMPLETADA.** 8/8 tasks, 7/7 reglas NADR-19 (§5.5, §5.7) implementadas. 4 archivos creados, 2 modificados (strategy.py type hint OCP, __init__.py exports), 38 tests agregados. Pyright 0 errors, pytest 624 passed. Zero-touch sobre infraestructura existente. 6 fixes de pyright aplicados inline (frozenset, protocolo TopologicalEvaluatorProtocol, assert isinstance SealedOracle, enum genérico, assert isinstance exit code, spec= en mock_strategy). 0 DF/GF durante implementación. |
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
**Gate Status:** ✅ COMPLETED
**NADRs afectados:** NADR-F17BIS-18 (22 reglas)

### 2.1 Wave 1.1 — NodeCriticality y CriticalityPolicy (NADR-18 §5.1, §5.2)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Crear enum `NodeCriticality` con exactamente tres niveles: `CRITICAL`, `WARNING`, `INFO`. Ubicación: `core/benchmark/topology/criticality/models.py`. Inmutable, `frozen=True`, con documentación de cada nivel. | NADR-18 §5.1 R2 | Low | — | DONE |
| **1.1.2** | Crear protocolo `CriticalityPolicy` (Protocol) con método `criticality_of(node_type: ContentNodeType) -> NodeCriticality`. Ubicación: `core/benchmark/topology/criticality/ports.py`. | NADR-18 §5.1 R1 | Low | 1.1.1 | DONE |
| **1.1.3** | Implementar `DefaultCriticalityPolicy` con el mapeo canónico inicial: CRITICAL → `DISPLAY_EQUATION`, `INLINE_EQUATION`, `TABLE_SIMPLE`, `TABLE_COMPLEX`; WARNING → `HEADING`, `PARAGRAPH`, `CODE`; INFO → `IMAGE`, `CAPTION`, `LIST`, `COMPOSITE_BLOCK`. Declarativo, centralizado, extensible. Ubicación: `core/benchmark/topology/criticality/policy.py`. | NADR-18 §5.1 R1, R3, R4, R5, R6, R7; §5.2 R8, R9 | Medium | 1.1.1, 1.1.2 | DONE |
| **1.1.4** | Tests unitarios de `NodeCriticality` y `DefaultCriticalityPolicy`: cobertura exhaustiva de los 11 `ContentNodeType`, fallo explícito ante tipo sin clasificación (extensibilidad), inmutabilidad. Ubicación: `tests/unit/test_criticality_policy.py`. | NADR-18 §5.1 R1, R2; §5.2 R9 | Low | 1.1.1, 1.1.2, 1.1.3 | DONE |

#### Notas de implementación — Task 1.1.1

> **Implementación completada 2026-08-30.**
> 
> Creado `NodeCriticality` como `StrEnum` con exactamente 3 niveles (CRITICAL, WARNING, INFO).
> 
> **Decisiones de diseño:**
> - Sin properties YAGNI (`is_critical`, etc.) conforme a ENGINEERING_PRINCIPLES §I
> - `StrEnum` para serialización determinista y comparaciones de valor
> - Documentación extensa en docstring de clase
> 
> **Archivo creado:** `core/benchmark/topology/criticality/models.py`
> **Regla implementada:** NADR-18 §5.1 R2

#### Notas de implementación — Task 1.1.2

> **Implementación completada 2026-08-30.**
> 
> Creado `CriticalityPolicy` como Protocol sin `@runtime_checkable` (overhead innecesario).
> 
> **Decisiones de diseño:**
> - Protocol puro para inyección de dependencias
> - Método `criticality_of(node_type: ContentNodeType) -> NodeCriticality`
> - Contrato de fail-fast documentado en docstring
> 
> **Archivo creado:** `core/benchmark/topology/criticality/ports.py`
> **Regla implementada:** NADR-18 §5.1 R1

#### Notas de implementación — Task 1.1.3

> **Implementación completada 2026-08-30.**
> 
> Creado `DefaultCriticalityPolicy` con mapeo canónico declarativo.
> 
> **Decisiones de diseño:**
> - `__slots__ = ()` para optimización de memoria
> - `_CRITICALITY_MAP` como dict de módulo (inmutable por convención)
> - `all_classified_types()` retorna `frozenset` para auditorías
> - Fail-fast con `raise ValueError(...) from None` para stack trace limpio
> 
> **Mapeo canónico:**
> - CRITICAL (4): DISPLAY_EQUATION, INLINE_EQUATION, TABLE_SIMPLE, TABLE_COMPLEX
> - WARNING (3): HEADING, PARAGRAPH, CODE
> - INFO (4): IMAGE, CAPTION, LIST, COMPOSITE_BLOCK
> 
> **Archivo creado:** `core/benchmark/topology/criticality/policy.py`
> **Reglas implementadas:** NADR-18 §5.1 R1, R3-R7; §5.2 R8, R9

#### Notas de implementación — Task 1.1.4

> **Implementación completada 2026-08-30.**
> 
> Creados 13 tests unitarios para `NodeCriticality` y `DefaultCriticalityPolicy`.
> 
> **Cobertura:**
> - Invariantes del enum: cardinalidad, valores, inmutabilidad, hashable
> - Cobertura exhaustiva: parametrizado sobre todos los ContentNodeType
> - Determinismo: misma entrada → misma salida
> - Taxonomía canónica: verificación por nivel
> - **Fail-fast: test de ValueError ante tipo sin clasificación (NADR-18 §5.2 R9)**
> - `all_classified_types()` retorna frozenset
> 
> **Archivo creado:** `tests/unit/test_criticality_policy.py`
> **Reglas verificadas:** NADR-18 §5.1 R1, R2; §5.2 R9

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.2 Wave 1.2 — CriticalityAwareCostContext (NADR-18 §5.3)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Crear `CriticalityAwareCostContext` que implementa el protocolo `TreeEditCostContext` existente (`core/benchmark/topology/ports.py`). Debe ponderar `deletion_cost`, `insertion_cost` y `substitution_cost` según la criticidad del nodo inyectada vía `CriticalityPolicy`. Configurable mediante pesos inyectados (no hardcodeados). Ubicación: `core/benchmark/topology/criticality/costs.py`. | NADR-18 §5.3 R11, R12, R13, R14, R15 | Medium | 1.1.1, 1.1.2, 1.1.3 | DONE |
| **1.2.2** | Definir pesos por defecto documentados como "propuesta inicial sujeta a validación empírica". Los pesos deben garantizar: `CRITICAL > WARNING > INFO` en penalización. Documentar que estos valores NO son definitivos. | NADR-18 §5.3 R12, R14 | Medium | 1.2.1 | DONE |
| **1.2.3** | Tests unitarios de `CriticalityAwareCostContext`: determinismo (mismos inputs → mismo costo), orden estricto CRITICAL > WARNING > INFO, configuración de pesos, integración con `ZhangShashaEngine` existente sin modificarlo. Ubicación: `tests/unit/test_criticality_costs.py`. | NADR-18 §5.3 R12, R15 | Medium | 1.2.1, 1.2.2 | DONE |

#### Notas de implementación — Task 1.2.1

> **Implementación completada 2026-08-30.**
> 
> Creado `CriticalityAwareCostContext` que implementa `TreeEditCostContext` del puerto canónico.
> 
> **Decisiones de diseño:**
> - **Importa `TreeEditCostContext` de `ports.py`** (NO redefine protocolo localmente)
> - `__slots__ = ("_policy", "_weights")` para optimización
> - Validación de cobertura completa de pesos en `__init__`
> - Properties `weights` y `policy` retornan copias defensivas
> 
> **Archivo creado:** `core/benchmark/topology/criticality/costs.py`
> **Reglas implementadas:** NADR-18 §5.3 R11, R12, R13, R14, R15

#### Notas de implementación — Task 1.2.2

> **Implementación completada 2026-08-30.**
> 
> Definidos pesos por defecto en `DEFAULT_CRITICALITY_WEIGHTS`:
> - `CRITICAL`: 5.0
> - `WARNING`: 2.0
> - `INFO`: 1.0
> 
> **Documentación:** Marcados como "propuesta inicial sujeta a validación empírica en Fase 5" (NADR-18 §5.3 R12, R14).
> 
> **Semántica de `substitution_cost`:**
> - Si mismo tipo Y contenido → 0.0 (consistente con `UnitCostContext`)
> - Si diferente → `max(peso_cand, peso_gt)` (conservador, semántica de pérdida)
> 
> **Reglas implementadas:** NADR-18 §5.3 R12, R14

#### Notas de implementación — Task 1.2.3

> **Implementación completada 2026-08-30.**
> 
> Creados 13 tests unitarios para `CriticalityAwareCostContext`.
> 
> **Cobertura:**
> - Determinismo: mismos inputs → mismo costo
> - Orden estricto: CRITICAL > WARNING > INFO en penalización
> - Sustitución idéntica: tipo Y contenido → costo 0.0
> - Sustitución diferente tipo mismo contenido → costo > 0.0
> - Sustitución con contenido diferente → max(criticidades)
> - Sustitución simétrica: costo(A,B) == costo(B,A)
> - Pesos customizados vía inyección
> - Pesos incompletos → ValueError
> - Property weights retorna copia defensiva
> - **Implementa TreeEditCostContext protocol (verificación con `isinstance`)**
> 
> **Archivo creado:** `tests/unit/test_criticality_costs.py`
> **Reglas verificadas:** NADR-18 §5.3 R12, R15

#### Notas de referencia cruzada (§1.4)

> NADR-18 §5.3 R12 aparece en Tasks 1.2.1, 1.2.2 y 1.2.3. Task 1.2.1 implementa la capacidad de configuración. Task 1.2.2 define los valores por defecto. Task 1.2.3 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.3 Wave 1.3 — Veredicto por Criticidad y Trazabilidad (NADR-18 §5.4, §5.5)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Implementar el mecanismo de detección de pérdida de nodo CRITICAL: dado un `ConfusionMatrix` o resultado de recall, si hay falsos negativos en nodos `CRITICAL`, emitir señal de fallo absoluto. Este mecanismo es independiente del NSS y tiene precedencia sobre él. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R16, R17 | High | 1.1.3, 1.2.1 | DONE |
| **1.3.2** | Implementar mecanismo de veredicto para nodos WARNING: si la pérdida de nodos WARNING supera un umbral configurable, emitir WARNING. Pérdida aislada de nodos WARNING MAY emitirse como veredicto de aprobación con observación. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R18 | Medium | 1.3.1 | DONE |
| **1.3.3** | Implementar mecanismo de veredicto para nodos INFO: la pérdida de nodos INFO MUST emitirse como veredicto de aprobación con observación. La pérdida de nodos INFO MUST NOT causar un veredicto de fallo. Ubicación: `core/benchmark/topology/criticality/verdict.py`. | NADR-18 §5.4 R19 | Low | 1.3.1 | DONE |
| **1.3.4** | Implementar trazabilidad de clasificación: toda evaluación topológica que use la taxonomía de criticidad MUST registrar la clasificación aplicada a cada nodo evaluado. Implementar evento de gobernanza para reclasificaciones. Ubicación: `core/benchmark/topology/criticality/traceability.py`. | NADR-18 §5.5 R20, R21, R22 | Medium | 1.1.3, 1.3.1 | DONE |
| **1.3.5** | Tests unitarios de veredicto por criticidad: pérdida CRITICAL → fallo absoluto independiente del NSS; pérdida WARNING → veredicto según umbral; pérdida INFO → PASS con observación. Tests de precedencia del mecanismo absoluto. Ubicación: `tests/unit/test_criticality_verdict.py`. | NADR-18 §5.4 R16, R17, R18, R19 | High | 1.3.1, 1.3.2, 1.3.3 | DONE |

#### Notas de implementación — Tasks 1.3.1-1.3.3

> **Completadas 2026-08-30.** `CriticalityVerdictEmitter` con input `RecallByNodeType` (integra con `EntityRecallEvaluator`). Stateless. Archivo: `criticality/verdict.py`.

#### Notas de implementación — Task 1.3.4

> **Completada 2026-08-30.** `ClassificationTracer` stateless + `ReclassificationEvent` con validaciones. `trace_types()` eliminado por YAGNI. Archivo: `criticality/traceability.py`.

#### Notas de implementación — Task 1.3.5

> **Completada 2026-08-30.** 40 tests unitarios (8 properties + 4 absolute_fail + 6 warning + 3 info + 5 no_loss + 8 tracer + 6 reclassification). Archivo: `test_criticality_verdict.py`.

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 12/12 |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ✅ 22/22 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ 0 hallazgos |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 508 passed |
| 7 | Notas de implementación completas | ✅ |
| 8 | Tests existentes ZhangShashaEngine en verde | ✅ Zero-touch |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-08-30

---

## 3. GATE 2 — REGRESIÓN TOPOLÓGICA GRADUADA Y ADAPTADOR BASELINE→EVALUACIÓN

**Objective:** Materializar la capacidad de emisión de veredictos graduados (PASS/WARNING/HARD_FAIL), el doble mecanismo de protección (NSS ponderado + regla absoluta CRITICAL), el adaptador que conecta el `SealedOracle` con la evaluación topológica, y la estrategia de evaluación de regresión. Al cierre de este Gate, el sistema puede evaluar el runtime contra el oráculo sellado con veredicto graduado.
**Execution Mode:** Secuencial
**Rollback Plan:** `git revert` de los commits del Gate 2; el sistema retorna al estado con `ParserEvaluationStrategy` únicamente.
**Gate Status:** ✅ COMPLETED
**NADRs afectados:** NADR-F17BIS-19 (§5.1-§5.4, §5.6)

### 3.1 Wave 2.1 — RegressionVerdict y RegressionThresholds (NADR-19 §5.1, §5.3)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Crear enum `RegressionVerdict` con exactamente tres niveles: `PASS`, `WARNING`, `HARD_FAIL`. Inmutable, `frozen=True`. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R1 | Low | Gate 1 | DONE |
| **2.1.2** | Crear `RegressionThresholds` como DTO configurable: `nss_hard_fail: float`, `nss_warning: float`. Valores por defecto documentados como "propuesta inicial sujeta a validación empírica". Inmutable. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R4, R5, R6, R7; §5.3 R12, R13, R14 | Medium | 2.1.1 | DONE |
| **2.1.3** | Implementar lógica de agregación por corpus: el veredicto por corpus MUST ser el peor veredicto de todos los documentos individuales. Si al menos un documento es HARD_FAIL, el corpus es HARD_FAIL. Si al menos un documento es WARNING y ninguno es HARD_FAIL, el corpus es WARNING. Solo si todos los documentos son PASS, el corpus es PASS. Ubicación: `core/benchmark/topology/regression/aggregation.py`. | NADR-19 §5.1 R2, R3 | Medium | 2.1.1 | DONE |
| **2.1.4** | Tests unitarios de `RegressionVerdict`, `RegressionThresholds` y agregación por corpus. Ubicación: `tests/unit/test_regression_models.py` y `tests/unit/test_regression_aggregation.py`. | NADR-19 §5.1 R1, R2, R3; §5.3 R12 | Low | 2.1.1, 2.1.2, 2.1.3 | DONE |

#### Notas de implementación — Task 2.1.1

> **Implementación completada 2026-08-30.**
>
> Creado `RegressionVerdict` como `StrEnum` con exactamente 3 niveles (PASS, WARNING, HARD_FAIL) y property `severity_rank` para agregación.
>
> Creado `RegressionCriticalitySignal` como enum tipado (`ABSOLUTE_FAIL`, `WARNING`, `PASS`) para evitar strings libres (ENGINEERING_PRINCIPLES §III).
>
> **Archivo creado:** `core/benchmark/topology/regression/models.py`
> **Regla implementada:** NADR-19 §5.1 R1

#### Notas de implementación — Task 2.1.2

> **Implementación completada 2026-08-30.**
>
> Creado `RegressionThresholds` con `nss_hard_fail=0.80`, `nss_warning=0.95` documentados como propuesta inicial no calibrada (NADR-19 §5.3 R12-R14).
>
> Invariante validada en `__post_init__`: `0.0 <= nss_hard_fail < nss_warning <= 1.0`.
>
> **Decisiones de diseño:**
> - `DEFAULT_REGRESSION_THRESHOLDS` como constante de módulo
> - Validación fail-fast en construcción
> - Inmutabilidad vía `frozen=True`
>
> **Reglas implementadas:** NADR-19 §5.1 R4-R7; §5.3 R12-R14

#### Notas de implementación — Task 2.1.3

> **Implementación completada 2026-08-30.**
>
> Creado `aggregate_corpus_verdicts()` que retorna `max(verdicts, key=severity_rank)`.
>
> Validación fail-fast: secuencia vacía → `ValueError`.
>
> Creado `RegressionEvaluationReport` con `overall_score` **obligatorio** (sin default) para fail-fast: no existe estado válido del dominio sin NSS. `nss_score` es property alias de `overall_score` (única fuente de verdad). Método `to_topological_report()` propaga NSS correctamente.
>
> **Archivo creado:** `core/benchmark/topology/regression/aggregation.py`
> **Reglas implementadas:** NADR-19 §5.1 R2, R3

#### Notas de implementación — Task 2.1.4

> **Implementación completada 2026-08-30.**
>
> Creados 30 tests unitarios (23 models + 7 aggregation).
>
> **Cobertura:**
> - Invariantes del enum: cardinalidad, valores, inmutabilidad, severity_rank
> - `RegressionCriticalitySignal`: enum tipado con 3 señales
> - Thresholds: invariante, defaults, custom, inmutabilidad
> - `RegressionEvaluationReport`: `overall_score` obligatorio, `nss_score` alias, `to_topological_report()` propaga NSS, veredicto se pierde en conversión
> - Agregación: todos los casos (all PASS, one WARNING, one HARD_FAIL, empty raises)
>
> **Archivos creados:** `tests/unit/test_regression_models.py`, `tests/unit/test_regression_aggregation.py`

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.2 Wave 2.2 — Doble Mecanismo de Protección (NADR-19 §5.2)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Implementar Mecanismo 1 (NSS ponderado por criticidad): calcular NSS utilizando `CriticalityAwareCostContext` (Gate 1) en lugar de `UnitCostContext`. Integrar con `TreeEditDistanceEvaluator` existente sin modificarlo (inyección de cost_context). | NADR-19 §5.2 R8 | High | Gate 1, 2.1.2 | DONE |
| **2.2.2** | Implementar Mecanismo 2 (Regla absoluta de pérdida CRITICAL): si hay pérdida de nodos CRITICAL, emitir HARD_FAIL independientemente del NSS. Este mecanismo tiene precedencia sobre el Mecanismo 1. Utilizar el componente de veredicto por criticidad del Gate 1 (Task 1.3.1). | NADR-19 §5.2 R9, R10 | High | Gate 1 (1.3.1), 2.2.1 | DONE |
| **2.2.3** | Implementar la complementariedad de ambos mecanismos: el veredicto final es el peor resultado de ambos. Documentar el ejemplo canónico: 1 nodo CRITICAL perdido en 1000 nodos → NSS alto pero HARD_FAIL. Ubicación: `core/benchmark/topology/regression/mechanism.py`. | NADR-19 §5.2 R8, R9, R10, R11 | High | 2.2.1, 2.2.2 | DONE |
| **2.2.4** | Tests unitarios del doble mecanismo: NSS ponderado, regla absoluta CRITICAL, precedencia, complementariedad, ejemplo canónico de 1 CRITICAL en 1000 nodos. Ubicación: `tests/unit/test_regression_mechanism.py`. | NADR-19 §5.2 R8, R9, R10, R11 | High | 2.2.1, 2.2.2, 2.2.3 | DONE |

#### Notas de implementación — Tasks 2.2.1-2.2.3

> **Implementación completada 2026-08-30.**
>
> Creado `DoubleProtectionMechanism` con `DoubleProtectionResult` inmutable.
>
> **Decisiones de diseño:**
> - **Precedencia total del Mecanismo 2:** si `criticality_verdict.has_critical_loss`, retorna `HARD_FAIL` inmediatamente sin evaluar NSS (NADR-19 §5.2 R9-R10).
> - **Complementariedad:** si no hay pérdida CRITICAL, el veredicto final es `max(nss_verdict, criticality_verdict_enum, key=severity_rank)` (NADR-19 §5.2 R11).
> - **Validación fail-fast de NSS:** `InvalidNSSScoreError` si `nss_score` no es finito o está fuera de `[0.0, 1.0]` (ENGINEERING_PRINCIPLES §IV, NADR-19 §5.2 R14).
> - **`RegressionCriticalitySignal`** enum tipado: la señal refleja el peor componente (ABSOLUTE_FAIL / WARNING / PASS).
> - Naming `DoubleProtectionMechanism` para trazabilidad directa con el ADR ("Doble Mecanismo de Protección").
>
> **Archivo creado:** `core/benchmark/topology/regression/mechanism.py`
> **Reglas implementadas:** NADR-19 §5.2 R8-R11

#### Notas de implementación — Task 2.2.4

> **Implementación completada 2026-08-30.**
>
> Creados 17 tests unitarios del doble mecanismo.
>
> **Cobertura:**
> - Ejemplo canónico: 1 CRITICAL en 1000 nodos → NSS 0.999 pero HARD_FAIL
> - Precedencia CRITICAL sobre NSS
> - NSS < hard_fail → HARD_FAIL; entre umbrales → WARNING; >= warning → PASS
> - Pérdida WARNING → WARNING; solo INFO → PASS
> - Complementariedad: peor resultado gana
> - Validación NSS: negativo, >1, NaN, inf → `InvalidNSSScoreError`
> - Boundaries: NSS=0.0 → HARD_FAIL, NSS=1.0 → PASS
> - Custom thresholds, inmutabilidad, determinismo
>
> **Archivo creado:** `tests/unit/test_regression_mechanism.py`

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.2 R8, R9, R10, R11 aparecen en Tasks 2.2.1, 2.2.2, 2.2.3 y 2.2.4. Tasks 2.2.1 y 2.2.2 implementan cada mecanismo por separado. Task 2.2.3 integra ambos. Task 2.2.4 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.3 Wave 2.3 — Adaptador Baseline→Evaluación (NADR-19 §5.4)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Crear `RegressionAdapter` que verifica la integridad criptográfica del oráculo mediante `OracleSemanticIdentityCalculator.calculate(oracle.nodes)` comparado contra el `oracle_hash` del manifiesto. Si no coincide, abortar con `OracleIntegrityError` (Fail-Fast). Ubicación: `core/benchmark/topology/regression/adapter.py`. | NADR-19 §5.4 R15, R18, R19 | High | Gate 1 | DONE |
| **2.3.2** | Implementar verificación de `ground_truth_state == SEALED` antes de evaluar. Si el estado no es SEALED, abortar con `OracleNotSealedError`. Utilizar el campo `ground_truth_state` de `CorpusDocumentMetadata` existente. | NADR-19 §5.4 R16, R18, R19 | Medium | 2.3.1 | DONE |
| **2.3.3** | Implementar verificación de completitud biyectiva mediante `BaselineCompletenessVerifier` antes de evaluar. Si la verificación falla, abortar con `IncompleteBaselineError`. | NADR-19 §5.4 R17, R18, R19 | Medium | 2.3.1 | DONE |
| **2.3.4** | Integrar las tres verificaciones (2.3.1, 2.3.2, 2.3.3) en secuencia Fail-Fast dentro del `RegressionAdapter`. El adaptador MUST reutilizar los evaluadores existentes sin modificarlos. | NADR-19 §5.4 R15, R16, R17, R18, R19 | High | 2.3.1, 2.3.2, 2.3.3 | DONE |
| **2.3.5** | Tests unitarios del adaptador: verificación de oracle_hash (match/mismatch), verificación de ground_truth_state (SEALED/no SEALED), verificación de completitud (completa/incompleta), Fail-Fast ante cualquier fallo. Ubicación: `tests/unit/test_regression_adapter.py`. | NADR-19 §5.4 R15, R16, R17, R18, R19 | High | 2.3.1, 2.3.2, 2.3.3, 2.3.4 | DONE |

#### Notas de implementación — Tasks 2.3.1-2.3.4

> **Implementación completada 2026-08-30.**
>
> Creado `RegressionAdapter` stateless con jerarquía de errores tipados en `core/benchmark/topology/regression/errors.py`.
>
> **Decisiones de diseño:**
> - **Orden de verificación Fail-Fast en `verify_all()`:** (1) Identidad documental → (2) Completitud biyectiva → (3) Estado SEALED → (4) Integridad criptográfica. Este orden minimiza el trabajo desperdiciado: los chequeos más baratos y más probables de fallar van primero.
> - **`verify_document_identity()` agregado:** detecta cruce de documentos (oráculo de `doc_A` con metadata de `doc_B`) antes de verificar integridad. Error tipado `OracleDocumentMismatchError`.
> - **`MissingOracleHashError`** para `metadata.oracle_hash is None` (fail-fast explícito, no `ValueError` genérico).
> - **`IncompleteBaselineError` reutilizado** desde `core/benchmark/ground_truth/errors.py` (Reuse Before Invent), lanzado con `"; ".join(errors)`.
> - **`GroundTruthState` es `Annotated[str, StringConstraints]`** (NO enum): se usa directamente como `str`, sin `.value`.
>
> **Archivos creados:** `core/benchmark/topology/regression/adapter.py`, `core/benchmark/topology/regression/errors.py`
> **Reglas implementadas:** NADR-19 §5.4 R15-R19

#### Notas de implementación — Task 2.3.5

> **Implementación completada 2026-08-30.**
>
> Creados 15 tests unitarios del adaptador.
>
> **Cobertura:**
> - `verify_document_identity`: IDs coinciden pasan; IDs divergentes → `OracleDocumentMismatchError`
> - `verify_oracle_integrity`: hash válido pasa; hash inválido → `OracleIntegrityError`; hash None → `MissingOracleHashError`
> - `verify_sealed_state`: `sealed` pasa; `draft` → `OracleNotSealedError`; `None` → `OracleNotSealedError`
> - `verify_completeness`: biyección completa pasa; faltante → `IncompleteBaselineError`; huérfano → `IncompleteBaselineError`
> - `verify_all`: orden Fail-Fast verificado con 3 tests explícitos (identidad primero, completitud antes de estado, estado antes de integridad)
>
> **Archivo creado:** `tests/unit/test_regression_adapter.py`

#### Notas de referencia cruzada (§1.4)

> NADR-19 §5.4 R15-R19 aparecen en Tasks 2.3.1 a 2.3.5. Tasks 2.3.1-2.3.3 implementan cada verificación por separado. Task 2.3.4 integra las tres. Task 2.3.5 verifica el comportamiento. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.4 Wave 2.4 — RegressionEvaluationStrategy (NADR-19 §5.1, §5.2, §5.6)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-30
**Fecha de cierre:** 2026-08-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.4.1** | Crear `RegressionEvaluationStrategy` que implementa el protocolo `EvaluationStrategy` existente (`core/benchmark/topology/ports.py`). Orquesta: (1) verificación de integridad, (2) evaluación TED ponderada, (3) evaluación Recall ponderada, (4) doble mecanismo de protección, (5) emisión de veredicto graduado. Ubicación: `core/benchmark/topology/regression/strategy.py`. | NADR-19 §5.1 R1, R2; §5.2 R8, R9, R10, R11 | High | 2.2.3, 2.3.4 | DONE |
| **2.4.2** | Implementar interacción con `EntityRecallEvaluator` ponderada por criticidad: un recall bajo de nodos CRITICAL se trata con mayor severidad que un recall bajo de nodos INFO. El recall se evalúa por tipo de nodo, ponderado por criticidad. | NADR-19 §5.6 R23, R24, R25 | Medium | 2.4.1 | DONE |
| **2.4.3** | Crear `RegressionEvaluationReport` que extiende `TopologicalEvaluationReport` existente con el campo `verdict: RegressionVerdict`. Inmutable. Ubicación: `core/benchmark/topology/regression/models.py`. | NADR-19 §5.1 R3 | Medium | 2.1.1, 2.4.1 | DONE |
| **2.4.4** | Tests unitarios de `RegressionEvaluationStrategy`: evaluación completa con oráculo válido, emisión de veredicto correcto, integración con `RegressionAdapter`, determinismo, interacción con recall ponderado. Ubicación: `tests/unit/test_regression_strategy.py`. | NADR-19 §5.1 R1, R2, R3; §5.6 R23, R24, R25 | High | 2.4.1, 2.4.2, 2.4.3 | DONE |

#### Notas de implementación — Tasks 2.4.1-2.4.3

> **Implementación completada 2026-08-30.**
>
> Creado `RegressionEvaluationStrategy` con dos métodos de evaluación:
> - `evaluate_run()` → retorna `TopologicalEvaluationReport` (cumple protocolo `EvaluationStrategy`; el veredicto se pierde en la conversión)
> - `evaluate_regression()` → retorna `RegressionEvaluationReport` (veredicto completo; usar en Gate 3)
>
> **Decisiones de diseño:**
> - **`_evaluate_recall_once()` (P0-1 corregido):** evalúa cada `EntityRecallEvaluator` **UNA sola vez**, retornando tanto `RecallByNodeType` (para veredicto) como `MetricScoreDTO` (para reporte). Elimina la doble llamada de la versión previa.
> - **`Dict[ContentNodeType, EntityRecallEvaluator]`** en vez de `Sequence`: el dict garantiza que cada evaluador está mapeado a su tipo sin parsing frágil de `metric_name`.
> - **Validación fail-fast:** `recall_evaluators` vacío → `ValueError` en `__init__`.
> - **`isinstance(dto.diagnostics, RecallDiagnostics)`** mantenido como defensa perimetral con comentario explicativo (protege contra cambios futuros en la jerarquía de evaluadores).
> - **`overall_score` obligatorio** en `RegressionEvaluationReport` (sin default): fail-fast, no existe estado válido sin NSS.
> - **`nss_score`** es property alias de `overall_score` (única fuente de verdad, sin divergencia posible).
>
> **Archivo creado:** `core/benchmark/topology/regression/strategy.py`
> **Reglas implementadas:** NADR-19 §5.1 R1-R3; §5.2 R8-R11; §5.6 R23-R25

#### Notas de implementación — Task 2.4.4

> **Implementación completada 2026-08-30.**
>
> Creados 16 tests unitarios de la strategy con mocks (`MagicMock(spec=...)`).
>
> **Cobertura:**
> - PASS con NSS alto y sin pérdidas; HARD_FAIL con pérdida CRITICAL; WARNING con NSS bajo o pérdida WARNING; PASS con solo pérdida INFO
> - `evaluate_run()` retorna `TopologicalEvaluationReport` y propaga NSS; el veredicto se pierde (verificado explícitamente)
> - **`test_recall_evaluators_called_exactly_once`**: verifica la corrección P0-1 (`call_count == 1` por evaluador)
> - **`test_empty_recall_evaluators_raises`**: validación fail-fast en `__init__`
> - Métricas incluyen TED y recall; determinismo; custom thresholds; custom verdict_emitter
> - **Mocks con `spec=EntityRecallEvaluator` y `spec=TreeEditDistanceEvaluator`** para que los tests fallen si la interfaz cambia
>
> **Archivo creado:** `tests/unit/test_regression_strategy.py`

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 17/17 |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ✅ 22/22 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ 0 hallazgos |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 586 passed |
| 7 | Notas de implementación completas | ✅ |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-08-30

---

## 4. GATE 3 — ENTRY POINT DE REGRESIÓN, REPORTE Y TESTS DE REGRESIÓN

**Objective:** Materializar el entry point de regresión que ejecuta la evaluación del runtime contra el oráculo sellado reutilizando el composition root del pipeline de producción, el reporte de regresión determinista y consumible por CI/CD, y los tests de regresión que certifican la implementación. Al cierre de este Gate, el sistema posee un mecanismo completo de regresión científica ejecutable.
**Execution Mode:** Secuencial
**Rollback Plan:** `git revert` de los commits del Gate 3; el sistema retorna al estado sin entry point de regresión.
**Gate Status:** ✅ COMPLETED
**NADRs afectados:** NADR-F17BIS-19 (§5.5, §5.7)

### 4.1 Wave 3.1 — Entry Point de Regresión (NADR-19 §5.5)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-02
**Fecha de cierre:** 2026-09-02

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Crear entry point CLI `tools/evaluation/run_regression.py` que orquesta la evaluación de regresión del runtime contra el oráculo sellado. MUST reutilizar `build_extraction_pipeline()` para generar el runtime AST. MUST NOT crear un pipeline de extracción separado. | NADR-19 §5.5 R20, R21 | High | Gate 2 | DONE |
| **3.1.2** | El entry point MUST ejecutar: (1) cargar manifiesto, (2) verificar completitud biyectiva, (3) para cada documento: verificar integridad, generar runtime AST, evaluar contra SealedOracle, emitir veredicto, (4) agregar veredictos por corpus. | NADR-19 §5.5 R20, R21, R22 | High | 3.1.1 | DONE |
| **3.1.3** | Implementar exit code diferenciado: `0` = PASS (todos los documentos PASS), `1` = WARNING (al menos un WARNING, ningún HARD_FAIL), `2` = HARD_FAIL (al menos un HARD_FAIL). | NADR-19 §5.5 R22 | Medium | 3.1.2 | DONE |
| **3.1.4** | Tests de integración del entry point: ejecución con corpus válido, emisión de veredictos correctos, exit codes correctos, determinismo, Fail-Fast ante oráculo no verificado. Ubicación: `tests/integration/test_regression_entry_point.py`. | NADR-19 §5.5 R20, R21, R22; §5.4 R18, R19 | High | 3.1.1, 3.1.2, 3.1.3 | DONE |

#### Notas de implementación — Tasks 3.1.1-3.1.3

> **Implementación completada 2026-09-02.**
>
> Creado `tools/evaluation/run_regression.py` con patrón CLI consistente con `run_benchmark.py` (argparse + `main()`).
>
> **Decisiones de diseño:**
> - **Functional Core / Imperative Shell:** Lógica de orquestación pura; I/O empujado a los bordes (file system, `sys.exit`).
> - **Reutilización estricta (R21):** `build_extraction_pipeline()` sin crear pipeline separado.
> - **Verificación de completitud una sola vez antes del loop** (Fail-Fast a nivel corpus).
> - **Verificaciones individuales por documento dentro del loop** (identidad, estado sellado, integridad) para evitar redundancia de `verify_completeness()`.
> - **`CriticalityAwareCostContext()` inyectado a `create_topology_evaluator()`** (NSS ponderado por criticidad, R8).
> - **11 `EntityRecallEvaluator`** (uno por `ContentNodeType`) para recall por tipo ponderado (R23-R25).
> - **`hydrate_ground_truth(state=SEALED)` + `assert isinstance(oracle, SealedOracle)`** para narrowing de pyright (contrato canónico NADR-F17BIS-12 §5.1 R3).
> - **Exit codes diferenciados:** 0=PASS, 1=WARNING, 2=HARD_FAIL (R22).
> - **`--inject-timestamp`** como flag opcional para R29 (determinismo estricto por defecto).
>
> **Argumentos CLI:**
> - `--corpus-dir` (requerido): directorio con `manifest.json` + `ground_truth/`
> - `--pdf-dir` (requerido): directorio con PDFs originales
> - `--output-dir` (opcional, default `reports/regression`)
> - `--inject-timestamp` (flag, default False)
>
> **Archivo creado:** `tools/evaluation/run_regression.py`
> **Reglas implementadas:** NADR-19 §5.5 R20, R21, R22

#### Notas de implementación — Task 3.1.4

> **Implementación completada 2026-09-02.**
>
> Creados 9 tests de integración con mocks `spec=` y fixtures en `tmp_path`.
>
> **Cobertura:**
> - **Exit codes (R22):** `test_exit_code_pass_when_all_pass` (exit 0), `test_exit_code_warning_when_any_warning` (exit 1), `test_exit_code_hard_fail_when_any_hard_fail` (exit 2).
> - **Fail-Fast (R18-R19):** `test_fail_fast_on_incomplete_baseline` (`IncompleteBaselineError` antes del loop).
> - **Reportes:** `test_report_files_created` (JSON + MD creados, JSON parseable), `test_deterministic_report` (2 ejecuciones → mismo JSON).
> - **CLI:** `test_required_args`, `test_inject_timestamp_flag`, `test_custom_output_dir`.
>
> **Robustez de mocks:**
> - Todos los mocks con `spec=` (`LocalFileSystemCorpusLoader`, `LocalFileSystemGroundTruthReader`, `LocalFileSystemGroundTruthArtifactAdapter`, `PdfParserAdapter`, `RegressionEvaluationStrategy`).
> - Helper `_run_entry_point()` centraliza setup de mocks.
> - `assert isinstance(code, int)` para narrowing de `SystemExit.code`.
> - `next(iter(ExtractionChallengeTrait))` para enum genérico (sin depender de miembro específico).
>
> **Archivo creado:** `tests/integration/test_regression_entry_point.py`
> **Reglas verificadas:** NADR-19 §5.5 R20, R21, R22; §5.4 R18, R19

#### Fixes de pyright aplicados inline (6 fixes)

> **Durante la implementación se detectaron 7 errores de pyright que se corrigieron inline sin generar DF/GF:**
>
> 1. **FIX 1 (run_regression.py:118):** `frozenset(artifact_adapter.list_artifact_ids())` — conversión `Tuple[str, ...]` → `FrozenSet[str]` para `verify_completeness()`.
> 2. **FIX 2 (strategy.py):** Type hint `ted_evaluator: TreeEditDistanceEvaluator` → `TopologicalEvaluatorProtocol`. OCP: dependencia de protocolo, no de implementación concreta. Sin cambio de comportamiento.
> 3. **FIX 3 (run_regression.py:149-156):** `assert isinstance(oracle, SealedOracle)` después de `hydrate_ground_truth(state=SEALED)` para narrowing de pyright.
> 4. **FIX 4 (test:95):** `next(iter(ExtractionChallengeTrait))` en vez de miembro específico del enum.
> 5. **FIX 5 (test:196, 213):** `assert isinstance(code, int)` para narrowing de `SystemExit.code`.
> 6. **FIX 6 (test:3 ubicaciones):** `MagicMock(spec=RegressionEvaluationStrategy)` para mock de instancia de strategy (consistencia con Gate 2).
>
> **Nota:** Los 6 fixes son correcciones de tipado estático, no defectos funcionales. No constituyen hallazgos diferibles porque se resolvieron inline dentro de la misma wave.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.2 Wave 3.2 — Reporte de Regresión (NADR-19 §5.7)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-02
**Fecha de cierre:** 2026-09-02

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Crear `RegressionReport` que incluye veredicto por documento y por corpus, NSS calculado, métricas ponderadas por criticidad, y detalle por documento. Formato JSON estructurado. Ubicación: `core/benchmark/topology/regression/report.py`. | NADR-19 §5.7 R26, R27 | Medium | Gate 2 | DONE |
| **3.2.2** | Implementar formato Markdown legible para humanos como salida secundaria. Reutilizar `MarkdownReportFormatter` existente en `tools/evaluation/infrastructure/formatters.py` si es compatible. | NADR-19 §5.7 R28 | Low | 3.2.1 | DONE |
| **3.2.3** | Garantizar determinismo del reporte: ausencia de marcas de tiempo físicas no inyectadas. Si se requiere marca temporal, MUST ser inyectada como parámetro externo. | NADR-19 §5.7 R29 | Low | 3.2.1 | DONE |
| **3.2.4** | Tests unitarios de reporting: determinismo, contenido correcto, formato JSON válido, ausencia de marcas de tiempo físicas. Ubicación: `tests/unit/test_regression_report.py`. | NADR-19 §5.7 R26, R27, R28, R29 | Medium | 3.2.1, 3.2.2, 3.2.3 | DONE |

#### Notas de implementación — Tasks 3.2.1-3.2.3

> **Implementación completada 2026-09-02.**
>
> Creado `core/benchmark/topology/regression/report.py` con diseño SOTA (combinación de propuestas tras análisis riguroso).
>
> **Decisiones de diseño (tras análisis comparativo):**
> - **`RegressionReport` como dataclass frozen** (sin wrapper YAGNI `DocumentRegressionResult`).
> - **`corpus_version: str`** para trazabilidad de versión del corpus evaluado.
> - **`corpus_nss: float`** (promedio de NSS por documento) para cumplir R27 ("NSS calculado").
> - **`generated_at: str | None = None`** inyectado externamente (R29 — determinismo total por defecto).
> - **Totales de false negatives por criticidad a nivel corpus** (`total_critical_false_negatives`, `total_warning_false_negatives`, `total_info_false_negatives`).
> - **`build_regression_report()` como función pura** (Functional Core, sin I/O).
> - **Formatters como Protocol + clases** (`RegressionReportFormatter`, `JsonRegressionReportFormatter`, `MarkdownRegressionReportFormatter`) para OCP. Consistente con `tools/evaluation/infrastructure/formatters.py`.
> - **`dict[str, object]`** en serialización (ENGINEERING_PRINCIPLES §III — Explicit over Implicit).
> - **`sort_keys=True`** en JSON para determinismo estricto.
> - **Sin `datetime.now()` en formatters** (R29).
>
> **Archivo creado:** `core/benchmark/topology/regression/report.py`
> **Reglas implementadas:** NADR-19 §5.7 R26, R27, R28, R29

#### Notas de implementación — Task 3.2.4

> **Implementación completada 2026-09-02.**
>
> Creados 29 tests unitarios.
>
> **Cobertura:**
> - **`TestBuildRegressionReport`** (12 tests): construcción, agregación de veredictos (peor gana), corpus_nss promedio, false negatives sumados, inmutabilidad, orden preservado, corpus_version, generated_at (default None + inyectado), determinismo.
> - **`TestJsonRegressionReportFormatter`** (9 tests): JSON válido, campos requeridos, corpus_nss, NSS por documento, determinismo, timestamp (ausente/injectado), serialización de diagnostics, veredicto HARD_FAIL.
> - **`TestMarkdownRegressionReportFormatter`** (8 tests): header, corpus_nss, verdict, tabla de documentos, criticality summary, determinismo, timestamp (ausente/injectado).
>
> **Archivo creado:** `tests/unit/test_regression_report.py`
> **Reglas verificadas:** NADR-19 §5.7 R26, R27, R28, R29

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.3 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-19 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- ✅ Entry point CLI `run_regression.py` existe y orquesta la evaluación de regresión.
- ✅ Entry point reutiliza `build_extraction_pipeline()` sin crear pipeline separado.
- ✅ Entry point verifica Fail-Fast ante oráculo no verificado.
- ✅ `RegressionReport` incluye veredicto por documento y por corpus.
- ✅ Formato JSON estructurado y formato Markdown legible.
- ✅ Reporte determinista: ausencia de marcas de tiempo físicas no inyectadas.
- ✅ Exit code diferenciado: 0 = PASS, 1 = WARNING, 2 = HARD_FAIL.
- ✅ Pyright: 0 errors, 0 warnings.
- ✅ Suite de tests completa en verde (incluyendo tests existentes de fases anteriores).

### 4.4 Gate 3 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 8/8 |
| 2 | Todas las reglas del Gate en estado DONE en §9 | ✅ 7/7 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ 0 hallazgos |
| 5 | Pyright: 0 errors, 0 warnings | ✅ (6 fixes aplicados inline) |
| 6 | Tests: suite completa en verde | ✅ 624 passed |
| 7 | Notas de implementación completas | ✅ |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-09-02

**Nota de cierre de Fase 4:** Con Gate 3 COMPLETED, la **Fase 4 (Scientific Verification)** se considera oficialmente COMPLETADA. Todas las 51 reglas de NADR-F17BIS-18 (22) y NADR-F17BIS-19 (29) están implementadas y verificadas.

---

## 5. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-08-30 | 22/22 | 12/12 | 0 | Taxonomía de criticidad y costos ponderados. Zero-touch. |
| Gate 2 | 2026-08-30 | 22/22 | 17/17 | 0 | Regresión topológica graduada y adaptador baseline→evaluación. Correcciones P0-1 y P1 aplicadas inline. Zero-touch. |
| Gate 3 | 2026-09-02 | 7/7 | 8/8 | 0 | Entry point CLI y reporte de regresión. 6 fixes de pyright aplicados inline. Zero-touch. **FASE 4 COMPLETADA.** |

---

## 6. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-4.1** | Verificar que `NodeCriticality` enum existe con tres niveles y mapea todos los `ContentNodeType` | Local | NADR-18 §5.1 R1, R2, R3 | Script de verificación | ✅ DONE |
| **MIG-4.2** | Verificar que `CriticalityAwareCostContext` implementa `TreeEditCostContext` con ponderación determinista | Local | NADR-18 §5.3 R11, R12, R15 | Script de verificación | ✅ DONE |
| **MIG-4.3** | Verificar que `RegressionAdapter` verifica oracle_hash, ground_truth_state, y completitud biyectiva antes de evaluar | Local | NADR-19 §5.4 R15, R16, R17, R18, R19 | Script de verificación | ✅ DONE |
| **MIG-4.4** | Verificar que `run_regression.py` ejecuta la evaluación de regresión del runtime contra el oráculo sellado | Local | NADR-19 §5.5 R20, R21, R22 | Script de verificación | ✅ DONE |
| **MIG-4.5** | Verificar que el reporte de regresión es determinista y consumible por CI/CD | Local/CI | NADR-19 §5.7 R26, R27, R28, R29 | Script de verificación | ✅ DONE |

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
| Gate 1 | 12 | 22 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 17 | 22 | 0 | 0 | ✅ COMPLETED |
| Gate 3 | 8 | 7 | 0 | 0 | ✅ COMPLETED |
| **TOTAL** | **37** | **51** | **0** | **0** | ✅ **FASE 4 COMPLETED** |

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

### 9.1 Gate 1 — Rules Audit Board (NADR-F17BIS-18) — ✅ COMPLETED

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-18 §5.1 R1 | DONE | Wave 1.1 / Task 1.1.2, 1.1.3, 1.1.4 | CriticalityPolicy + DefaultCriticalityPolicy + 13 tests |
| NADR-18 §5.1 R2 | DONE | Wave 1.1 / Task 1.1.1, 1.1.4 | NodeCriticality StrEnum + tests |
| NADR-18 §5.1 R3 | DONE | Wave 1.1 / Task 1.1.3 | Mapeo CRITICAL: 4 tipos |
| NADR-18 §5.1 R4 | DONE | Wave 1.1 / Task 1.1.3 | Mapeo WARNING: 3 tipos |
| NADR-18 §5.1 R5 | DONE | Wave 1.1 / Task 1.1.3 | Mapeo INFO: 4 tipos |
| NADR-18 §5.1 R6 | DONE | Wave 1.1 / Task 1.1.3 | Declarativa y centralizada |
| NADR-18 §5.1 R7 | DONE | Wave 1.1 / Task 1.1.3 | Clasificación por tipo, no por contenido |
| NADR-18 §5.2 R8 | DONE | Wave 1.1 / Task 1.1.3 | Extensible mediante composición |
| NADR-18 §5.2 R9 | DONE | Wave 1.1 / Task 1.1.3, 1.1.4 | Fail-fast ValueError + test |
| NADR-18 §5.2 R10 | DONE | Wave 1.3 / Task 1.3.4 | ReclassificationEvent + create_reclassification_event() |
| NADR-18 §5.3 R11 | DONE | Wave 1.2 / Task 1.2.1 | CriticalityAwareCostContext implementa TreeEditCostContext |
| NADR-18 §5.3 R12 | DONE | Wave 1.2 / Task 1.2.1, 1.2.2, 1.2.3 | Ponderación determinista + tests |
| NADR-18 §5.3 R13 | DONE | Wave 1.2 / Task 1.2.1 | Pesos configurables vía inyección |
| NADR-18 §5.3 R14 | DONE | Wave 1.2 / Task 1.2.2 | Pesos default documentados como propuesta inicial |
| NADR-18 §5.3 R15 | DONE | Wave 1.2 / Task 1.2.3 | Tests integración ZhangShashaEngine |
| NADR-18 §5.4 R16 | DONE | Wave 1.3 / Task 1.3.1, 1.3.5 | is_absolute_failure ante pérdida CRITICAL |
| NADR-18 §5.4 R17 | DONE | Wave 1.3 / Task 1.3.1, 1.3.5 | Precedencia CRITICAL > WARNING > INFO |
| NADR-18 §5.4 R18 | DONE | Wave 1.3 / Task 1.3.2, 1.3.5 | Umbral configurable >= 1 |
| NADR-18 §5.4 R19 | DONE | Wave 1.3 / Task 1.3.3, 1.3.5 | is_pass_with_observation para INFO |
| NADR-18 §5.5 R20 | DONE | Wave 1.3 / Task 1.3.4 | ClassificationTracer.trace_nodes() stateless |
| NADR-18 §5.5 R21 | DONE | Wave 1.3 / Task 1.3.4 | CRITICALITY_POLICY_VERSION |
| NADR-18 §5.5 R22 | DONE | Wave 1.3 / Task 1.3.4 | ReclassificationEvent + factory con validaciones |

### 9.2 Gate 2 — Rules Audit Board (NADR-F17BIS-19 §5.1-§5.4, §5.6) — ✅ COMPLETED

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-19 §5.1 R1 | DONE | Wave 2.1 / Task 2.1.1, 2.1.4 | RegressionVerdict StrEnum (3 niveles) + severity_rank + tests |
| NADR-19 §5.1 R2 | DONE | Wave 2.1 / Task 2.1.3, 2.1.4; Wave 2.4 / Task 2.4.1 | aggregate_corpus_verdicts + strategy |
| NADR-19 §5.1 R3 | DONE | Wave 2.1 / Task 2.1.3, 2.1.4; Wave 2.4 / Task 2.4.3 | RegressionEvaluationReport con verdict |
| NADR-19 §5.1 R4 | DONE | Wave 2.1 / Task 2.1.2 | RegressionThresholds configurable |
| NADR-19 §5.1 R5 | DONE | Wave 2.1 / Task 2.1.2 | RegressionThresholds configurable |
| NADR-19 §5.1 R6 | DONE | Wave 2.1 / Task 2.1.2 | RegressionThresholds configurable |
| NADR-19 §5.1 R7 | DONE | Wave 2.1 / Task 2.1.2 | RegressionThresholds configurable |
| NADR-19 §5.2 R8 | DONE | Wave 2.2 / Task 2.2.1, 2.2.3; Wave 2.4 / Task 2.4.1 | NSS ponderado vía CriticalityAwareCostContext |
| NADR-19 §5.2 R9 | DONE | Wave 2.2 / Task 2.2.2, 2.2.3; Wave 2.4 / Task 2.4.1 | Regla absoluta CRITICAL |
| NADR-19 §5.2 R10 | DONE | Wave 2.2 / Task 2.2.2, 2.2.3; Wave 2.4 / Task 2.4.1 | Precedencia Mecanismo 2 sobre Mecanismo 1 |
| NADR-19 §5.2 R11 | DONE | Wave 2.2 / Task 2.2.3; Wave 2.4 / Task 2.4.1 | Complementariedad: peor resultado gana |
| NADR-19 §5.3 R12 | DONE | Wave 2.1 / Task 2.1.2, 2.1.4 | Thresholds default documentados como propuesta inicial |
| NADR-19 §5.3 R13 | DONE | Wave 2.1 / Task 2.1.2 | Thresholds configurables vía inyección |
| NADR-19 §5.3 R14 | DONE | Wave 2.1 / Task 2.1.2; Wave 2.2 / Task 2.2.3 | Determinismo + InvalidNSSScoreError (finitud y rango) |
| NADR-19 §5.4 R15 | DONE | Wave 2.3 / Task 2.3.1, 2.3.4, 2.3.5 | verify_oracle_integrity con OracleSemanticIdentityCalculator |
| NADR-19 §5.4 R16 | DONE | Wave 2.3 / Task 2.3.2, 2.3.4, 2.3.5 | verify_sealed_state (GroundTruthState como str) |
| NADR-19 §5.4 R17 | DONE | Wave 2.3 / Task 2.3.3, 2.3.4, 2.3.5 | verify_completeness con BaselineCompletenessVerifier |
| NADR-19 §5.4 R18 | DONE | Wave 2.3 / Task 2.3.1-2.3.5; Wave 3.1 / Task 3.1.4 | Fail-Fast con errores tipados; verify_all ordenado |
| NADR-19 §5.4 R19 | DONE | Wave 2.3 / Task 2.3.1-2.3.5; Wave 3.1 / Task 3.1.4 | Errores explícitos tipados (5 clases en errors.py) |
| NADR-19 §5.6 R23 | DONE | Wave 2.4 / Task 2.4.2 | Recall por tipo ponderado por criticidad |
| NADR-19 §5.6 R24 | DONE | Wave 2.4 / Task 2.4.2 | Recall por tipo ponderado por criticidad |
| NADR-19 §5.6 R25 | DONE | Wave 2.4 / Task 2.4.2 | Recall por tipo ponderado por criticidad |

### 9.3 Gate 3 — Rules Audit Board (NADR-F17BIS-19 §5.5, §5.7) — ✅ COMPLETED

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-19 §5.5 R20 | DONE | Wave 3.1 / Task 3.1.1, 3.1.2, 3.1.4 | Entry point CLI reutiliza `build_extraction_pipeline()` |
| NADR-19 §5.5 R21 | DONE | Wave 3.1 / Task 3.1.1, 3.1.2, 3.1.4 | Orquestación completa (manifiesto → verificación → evaluación → veredicto) |
| NADR-19 §5.5 R22 | DONE | Wave 3.1 / Task 3.1.3, 3.1.4 | Exit codes diferenciados (0=PASS, 1=WARNING, 2=HARD_FAIL) |
| NADR-19 §5.7 R26 | DONE | Wave 3.2 / Task 3.2.1, 3.2.4 | `RegressionReport` con veredicto por documento y corpus |
| NADR-19 §5.7 R27 | DONE | Wave 3.2 / Task 3.2.1, 3.2.4 | `corpus_nss` + formato JSON estructurado (sort_keys) |
| NADR-19 §5.7 R28 | DONE | Wave 3.2 / Task 3.2.2, 3.2.4 | `MarkdownRegressionReportFormatter` legible |
| NADR-19 §5.7 R29 | DONE | Wave 3.2 / Task 3.2.3, 3.2.4 | `generated_at` inyectado externamente; sin timestamp por defecto |

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