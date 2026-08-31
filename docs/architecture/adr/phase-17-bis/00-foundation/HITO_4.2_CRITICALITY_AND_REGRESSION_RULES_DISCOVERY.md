# HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-08-30
**Fecha de congelamiento:** 2026-08-30
**Fase:** 17-BIS — Fase 4 (Scientific Verification)
**Tipo de artefacto:** Forensic Discovery / Dimension & Mutation Semantics Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT (FROZEN), HITO_0.4.2_AST_ONTOLOGY_AUDIT (FROZEN), HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT (FROZEN), HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT (FROZEN), HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY (FROZEN v2.1.0), FASE_3_HANDOFF (FROZEN v1.0.0), HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0-FROZEN.
**Mandato:** Auditar el estado actual de la taxonomía de criticidad de nodos (DC-06) y las reglas de regresión topológica (DC-07), identificar qué existe, qué falta, y proponer la estructura normativa que Fase 4 debe materializar.
**Síntesis:** No existe ninguna taxonomía de criticidad ni reglas de regresión graduada en el repositorio. DC-06 y DC-07 están completamente ausentes a nivel operativo. Se propone una taxonomía de 3 niveles (CRITICAL / WARNING / INFO) mapeada a ContentNodeType, y reglas de veredicto basadas en NSS ponderado y pérdida de nodos críticos.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-08-30 | Emisión inicial. Discovery forense de criticidad y reglas de regresión. |
| 1.0.0-FROZEN | 2026-08-30 | Aplicación de 5 correcciones de forma. Congelamiento formal del HITO. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la totalidad del repositorio en busca de componentes, contratos, enums, políticas o reglas que materialicen la taxonomía de criticidad de nodos (DC-06) y las reglas de regresión topológica graduada (DC-07). Se inspeccionaron `core/ast/enums.py`, `core/validation/ast/models.py`, `core/validation/models.py`, `core/benchmark/topology/costs/unit.py`, `core/benchmark/topology/ports.py`, `core/benchmark/topology/strategies.py`, `tools/evaluation/topology/models.py`, y las suites de tests asociadas.

**Hallazgo central:**

> No existe ninguna taxonomía de criticidad de nodos ni reglas de regresión graduada en el repositorio. DC-06 y DC-07 están completamente ausentes a nivel operativo. Los costos de edición son uniformes (1.0), no existe ningún enum de criticidad, y no existe ningún mecanismo de veredicto (PASS / WARNING / HARD_FAIL). La regresión actual se limita a comparaciones binarias de snapshots o a la tautología del golden test (GAP-0.4-09).

**Defectos dominantes confirmados:**

1. **Ausencia total de taxonomía de criticidad (E-4.2-001):** No existe ningún enum, política o contrato que mapee `ContentNodeType` a niveles de criticidad. DC-06 sin materialización operativa.
2. **Ausencia total de reglas de regresión graduada (E-4.2-002):** No existe ningún mecanismo de veredicto (PASS / WARNING / HARD_FAIL). DC-07 sin materialización operativa.
3. **Costos de edición uniformes sin ponderación (E-4.2-003):** `UnitCostContext` aplica costos simétricos de 1.0 sin distinción de tipo de nodo. La pérdida de una ecuación tiene el mismo peso que la pérdida de un caption.
4. **Regresión actual limitada a snapshots binarios o tautologías (E-4.2-004):** La suite de tests actual no implementa regresión graduada. El golden test es tautológico (GAP-0.4-09) y los snapshots de chunking comparan campos parciales.

**Veredicto:** Fase 4 debe crear desde cero la taxonomía de criticidad, las reglas de regresión graduada, el contexto de costos ponderados y el mecanismo de veredicto. No existe nada reutilizable para estos componentes específicos.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Este HITO no audita el motor matemático Zhang-Shasha ni los evaluadores TED/Recall (eso fue cubierto por HITO_4.1). Este HITO se limita exclusivamente a la taxonomía de criticidad (DC-06) y las reglas de regresión graduada (DC-07).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR_F17_BIS_MASTER §8 (DC-06, DC-07), HITO_0.4.2 (OBS-0.4.2-04), HITO_0.4.1 (recomendación DC-06).
2. Cargar HITOs previos aplicables: HITO_0.4.4, HITO_0.4.4_C5, HITO_2.0, FASE_3_HANDOFF.
3. Inspeccionar código fuente de todos los módulos del alcance.
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs E-4.2-NNN.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar TO BE VERIFIED cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/ast/enums.py` | ContentNodeType, TranslationStrategy, HeadingLevel, SemanticOrigin | 100% auditado |
| `core/validation/ast/models.py` | ValidationSeverity (INFO, SOFT_FAIL, HARD_FAIL) | 100% auditado |
| `core/validation/models.py` | Severity, Scope, ValidationContext, ValidationResult | 100% auditado |
| `core/validation/ast/validators/strategy.py` | PassthroughIntegrityValidator | 100% auditado |
| `core/validation/ast/validators/structural.py` | StructuralEquationValidator | 100% auditado |
| `core/benchmark/topology/costs/unit.py` | UnitCostContext | 100% auditado |
| `core/benchmark/topology/ports.py` | TreeEditCostContext, EditCostPolicy, TopologicalEvaluatorProtocol, EvaluationStrategy | 100% auditado |
| `core/benchmark/topology/strategies.py` | ParserEvaluationStrategy | 100% auditado |
| `core/benchmark/topology/models.py` | MetricScoreDTO, TopologicalEvaluationReport, ConfusionMatrix | 100% auditado |
| `tools/evaluation/topology/models.py` | MetricName, MetricResult, DocumentEvaluationResult, BenchmarkSummaryReport | 100% auditado |
| `tools/evaluation/topology/strategies.py` | DefaultBenchmarkAggregationStrategy | 100% auditado |
| `tests/integration/test_golden_parser.py` | TestGoldenParser | 100% auditado |
| `tests/integration/test_chunker_snapshot.py` | TestChunkerSnapshot | 100% auditado |
| `tests/unit/test_zhang_shasha.py` | Suite Zhang-Shasha (17 tests) | Referenciado (auditado en HITO_4.1) |
| `tests/unit/test_structural_metric.py` | Suite StructuralTopologyMetric (8 tests) | Referenciado (auditado en HITO_4.1) |
| `core/benchmark/topology/evaluators/ted.py` | TreeEditDistanceEvaluator | Referenciado (auditado en HITO_4.1) |
| `core/benchmark/topology/evaluators/recall.py` | EntityRecallEvaluator | Referenciado (auditado en HITO_4.1) |
| `core/benchmark/ground_truth/models.py` | SealedOracle, GroundTruthDraft | Referenciado (auditado en HITO_2.0, Fase 2) |
| `core/benchmark/ground_truth/identity.py` | OracleSemanticIdentityCalculator | Referenciado (auditado en HITO_3.1, Fase 3) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER §8 (DC-06, DC-07), §3 (Dimensión REGRESIÓN) | Fuente normativa: definición de DC-06 y DC-07 |
| HITO previo | HITO_0.4.2_AST_ONTOLOGY_AUDIT (OBS-0.4.2-04) | Evidencia forense heredada: ContentNodeType carece de criticidad |
| HITO previo | HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT | Evidencia forense heredada: UnitCostContext sin ponderación |
| HITO previo | HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT | Evidencia forense heredada: tautología en golden test |
| HITO previo | HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT | Evidencia forense heredada: ausencia de CI workflows |
| HITO previo | HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY | Evidencia forense heredada: GAP-2.0-11 |
| Handoff | FASE_3_HANDOFF v1.0.0 | Estado de Fase 3, carry-forward obligatorio |
| HITO previo | HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY | Evidencia forense: estado de la infraestructura topológica |
| Código | core/ast/enums.py, core/validation/ast/models.py, core/benchmark/topology/costs/unit.py | Observación runtime/código |
| Test | tests/integration/test_golden_parser.py, tests/integration/test_chunker_snapshot.py | Verificación comportamental |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 | Estructura canónica del HITO |

> **Nota sobre secciones condicionales:** Las secciones 5 (Mapa de Flujos Observados), 9 (Canonicalization / Determinism Audit), 12 (Matriz de Triaje) y 17 (Verificación de Cumplimiento ADR/NADR) no aplican a este HITO. Este HITO es un Dimension & Mutation Semantics Audit, no un Flow Audit, Canonicalization Audit, Discovery puro ni Compliance Audit.

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| Taxonomía de criticidad de nodos | No existe | No | No existe mapeo ContentNodeType → CRITICAL/WARNING/INFO | MISSING |
| Reglas de regresión graduada | No existe | No | No existe mecanismo de veredicto PASS/WARNING/HARD_FAIL | MISSING |
| Contexto de costos ponderados | No existe | No | No existe extensión de TreeEditCostContext con criticidad | MISSING |
| RegressionVerdict | No existe | No | No existe modelo de veredicto de regresión | MISSING |
| RegressionThresholds | No existe | No | No existe configuración de umbrales de regresión | MISSING |
| ContentNodeType | `core/ast/enums.py` (11 miembros) | Sí (AST V2) | Ontología de tipos semánticos del AST | CONFIRMADO |
| ValidationSeverity | `core/validation/ast/models.py` (INFO, SOFT_FAIL, HARD_FAIL) | Sí (validación pre-LLM) | Severidad de validación AST (no es criticidad de regresión) | CONFIRMADO (uso diferente) |
| Severity | `core/validation/models.py` | Sí (validación post-LLM) | Severidad de validación de chunks (no es criticidad de regresión) | CONFIRMADO (uso diferente) |
| UnitCostContext | `core/benchmark/topology/costs/unit.py` | Sí (TreeEditCostContext) | Costos unitarios simétricos (1.0) sin criticidad | CONFIRMADO (con gap) |
| TreeEditCostContext | `core/benchmark/topology/ports.py` | Sí (Protocol) | Puerto de costos de edición | CONFIRMADO |
| EditCostPolicy | `core/benchmark/topology/ports.py` | Sí (Protocol) | Puerto de política de costos por tipo | CONFIRMADO (no implementado) |
| ParserEvaluationStrategy | `core/benchmark/topology/strategies.py` | Sí (EvaluationStrategy) | Orquestador de evaluación de parsers (no regresión) | CONFIRMADO (uso diferente) |
| MetricScoreDTO | `core/benchmark/topology/models.py` | Sí | Contenedor de resultado de evaluación | CONFIRMADO |
| TopologicalEvaluationReport | `core/benchmark/topology/models.py` | Sí | Reporte de evaluación topológica por documento | CONFIRMADO |
| ConfusionMatrix | `core/benchmark/topology/models.py` | Sí | Matriz de confusión (TP, FP, FN) | CONFIRMADO |
| DefaultBenchmarkAggregationStrategy | `tools/evaluation/topology/strategies.py` | Sí (BenchmarkAggregationStrategy) | Agregación por promedio aritmético | CONFIRMADO |
| Golden test | `tests/integration/test_golden_parser.py` | No (tautológico) | Tautología A == A (GAP-0.4-09) | CONFIRMADO (defectuoso) |
| Snapshot de chunking | `tests/integration/test_chunker_snapshot.py` | Parcial | Snapshot con auto-generación y sub-aserción | CONFIRMADO (defectuoso) |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Taxonomía de criticidad (DC-06) | No existe ningún enum, política o contrato de criticidad | ADR Maestro §8 DC-06: mapeo ContentNodeType → CRITICAL/WARNING/INFO | HITO 0.4.2 OBS-0.4.2-04: "ContentNodeType carece de métodos o clasificadores de criticidad semántica" | DISCREPANCY | E-4.2-001 |
| Reglas de regresión graduada (DC-07) | No existe ningún mecanismo de veredicto PASS/WARNING/HARD_FAIL | ADR Maestro §8 DC-07: condiciones para HARD_FAIL vs WARNING | ADR Maestro §3: "Regresión no es Coincidencia Binaria (Snapshotting)" | DISCREPANCY | E-4.2-002 |
| Costos de edición ponderados | UnitCostContext aplica costos uniformes 1.0 | Costos diferenciados por criticidad de nodo | HITO 0.4.1: "Extender TreeEditCostContext para asignar penalizaciones diferenciadas según la severidad del nodo" | DISCREPANCY | E-4.2-003 |
| Regresión actual | Golden test tautológico (A == A), snapshots con auto-generación | Regresión graduada con veredicto explícito | HITO 0.4.4 GAP-0.4-09, C5-R01 a C5-R10 | DISCREPANCY | E-4.2-004 |
| ValidationSeverity vs criticidad de regresión | ValidationSeverity (INFO, SOFT_FAIL, HARD_FAIL) existe en validación pre-LLM | No debe confundirse con criticidad de regresión | No existe decisión previa | TO BE VERIFIED | E-4.2-005 |
| EditCostPolicy | Protocol existe en ports.py pero no tiene implementación | Debe implementarse para soportar costos ponderados | No existe decisión previa | DISCREPANCY | E-4.2-006 |
| Conexión SealedOracle → evaluación | No existe (GAP-2.0-11 heredado) | Adaptador que conecte SealedOracle con evaluación topológica | HITO 2.0 GAP-2.0-11, HITO 4.1 GAP-4.1-01 | DISCREPANCY | E-4.2-007 |

---

## 8. MUTATION SEMANTICS MATRIX

| Mutación | Criticidad afectada | NSS cambia? | Recall cambia? | Veredicto esperado | Observed behavior | Required behavior | Evidencia | Gap |
|---|---|---|---|---|---|---|---|---|
| Pérdida de DISPLAY_EQUATION | CRITICAL (propuesto) | Sí | Sí | HARD_FAIL | NSS baja uniformemente; sin veredicto | NSS ponderado; HARD_FAIL | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de INLINE_EQUATION | CRITICAL (propuesto) | Sí | Sí | HARD_FAIL | NSS baja uniformemente; sin veredicto | NSS ponderado; HARD_FAIL | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de TABLE_SIMPLE | CRITICAL (propuesto) | Sí | Sí | HARD_FAIL | NSS baja uniformemente; sin veredicto | NSS ponderado; HARD_FAIL | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de TABLE_COMPLEX | CRITICAL (propuesto) | Sí | Sí | HARD_FAIL | NSS baja uniformemente; sin veredicto | NSS ponderado; HARD_FAIL | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de HEADING | WARNING (propuesto) | Sí | No | WARNING | NSS baja uniformemente; sin veredicto | NSS ponderado; WARNING | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de PARAGRAPH | WARNING (propuesto) | Sí | Sí | WARNING | NSS baja uniformemente; sin veredicto | NSS ponderado; WARNING | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de CODE | WARNING (propuesto) | Sí | Sí | WARNING | NSS baja uniformemente; sin veredicto | NSS ponderado; WARNING | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de IMAGE | INFO (propuesto) | Sí | No | PASS (con observación) | NSS baja uniformemente; sin veredicto | NSS ponderado; PASS con observación | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de CAPTION | INFO (propuesto) | Sí | No | PASS (con observación) | NSS baja uniformemente; sin veredicto | NSS ponderado; PASS con observación | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de LIST | INFO (propuesto) | Sí | No | PASS (con observación) | NSS baja uniformemente; sin veredicto | NSS ponderado; PASS con observación | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Pérdida de COMPOSITE_BLOCK | INFO (propuesto) | Sí | No | PASS (con observación) | NSS baja uniformemente; sin veredicto | NSS ponderado; PASS con observación | E-4.2-001, E-4.2-002, E-4.2-003 | GAP-4.2-01, GAP-4.2-02 |
| Cambio de contenido en nodo | Depende del tipo | Sí | Sí | Depende del umbral | NSS baja; sin veredicto | NSS ponderado; veredicto según umbral | E-4.2-002, E-4.2-003 | GAP-4.2-02 |
| Cambio de orden de nodos | No aplica | Sí | No | Depende del umbral | NSS baja; sin veredicto | NSS ponderado; veredicto según umbral | E-4.2-002 | GAP-4.2-02 |
| Aplanamiento jerárquico | No aplica | Sí | No | Depende del umbral | NSS baja significativamente; sin veredicto | NSS ponderado; veredicto según umbral | E-4.2-002 | GAP-4.2-02 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Para evidencia positiva (componentes SOTA confirmados), se usa N/A.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-4.2-001** | P0 | Ausencia total en todos los archivos auditados | **Ausencia total de taxonomía de criticidad.** No existe ningún enum, política o contrato que mapee `ContentNodeType` a niveles de criticidad (CRITICAL, WARNING, INFO). DC-06 sin materialización operativa. |
| **E-4.2-002** | P0 | Ausencia total en todos los archivos auditados | **Ausencia total de reglas de regresión graduada.** No existe ningún mecanismo de veredicto (PASS, WARNING, HARD_FAIL). No existe RegressionVerdict ni ningún modelo de veredicto. DC-07 sin materialización operativa. |
| **E-4.2-003** | P1 | `core/benchmark/topology/costs/unit.py::UnitCostContext` | **Costos de edición uniformes sin ponderación.** `deletion_cost = 1.0`, `insertion_cost = 1.0`, `substitution_cost = 1.0` si difiere texto o tipo. No existe ponderación por criticidad de nodo. La pérdida de una ecuación tiene el mismo peso que la pérdida de un caption. |
| **E-4.2-004** | P0 | `tests/integration/test_golden_parser.py`, `tests/integration/test_chunker_snapshot.py` | **Regresión actual limitada a snapshots binarios o tautologías.** El golden test es tautológico (GAP-0.4-09: `expected_fingerprint = current_fingerprint`). El snapshot de chunking tiene auto-generación silenciosa (C5-R01) y sub-aserción de campos (C5-R02). |
| **E-4.2-005** | P2 | `core/validation/ast/models.py::ValidationSeverity` | **ValidationSeverity vs criticidad de regresión.** `ValidationSeverity` (INFO, SOFT_FAIL, HARD_FAIL) existe en validación pre-LLM. No debe confundirse con criticidad de regresión. Son conceptos ortogonales: ValidationSeverity gobierna la validación de nodos AST antes de la inferencia LLM; la criticidad de regresión gobierna la evaluación de desviaciones topológicas contra el oráculo sellado. |
| **E-4.2-006** | P1 | `core/benchmark/topology/ports.py::EditCostPolicy` | **EditCostPolicy sin implementación.** El Protocol `EditCostPolicy` existe en `ports.py` con métodos `insertion_cost(node_type)`, `deletion_cost(node_type)`, `mismatch_cost(type_candidate, type_ground_truth)`, `substitution_weight(node_type)`. Sin embargo, no existe ninguna implementación concreta de este Protocol en el repositorio. |
| **E-4.2-007** | P0 | Ausencia total en todos los archivos auditados | **Conexión SealedOracle → evaluación ausente (GAP-2.0-11 heredado).** No existe ningún componente que conecte `SealedOracle` con la evaluación topológica. GAP-2.0-11 heredado del HITO 2.0, confirmado en HITO 4.1 como GAP-4.1-01. |
| **E-4.2-008** | N/A | `core/ast/enums.py::ContentNodeType` | **ContentNodeType confirmado (11 miembros).** COMPOSITE_BLOCK, HEADING, PARAGRAPH, DISPLAY_EQUATION, INLINE_EQUATION, TABLE_SIMPLE, TABLE_COMPLEX, IMAGE, CAPTION, CODE, LIST. Ontología establecida en Fase 16.2. |
| **E-4.2-009** | N/A | `core/benchmark/topology/ports.py::TreeEditCostContext` | **TreeEditCostContext confirmado (Protocol).** Puerto de costos de edición con métodos `deletion_cost(node)`, `insertion_cost(node)`, `substitution_cost(candidate, ground_truth)`. Implementado por `UnitCostContext`. |
| **E-4.2-010** | N/A | `core/benchmark/topology/models.py::MetricScoreDTO` | **MetricScoreDTO confirmado.** Contenedor universal inmutable para resultados de evaluación. Campos: `metric_name`, `primary_score`, `diagnostics`. |
| **E-4.2-011** | N/A | `core/benchmark/topology/models.py::TopologicalEvaluationReport` | **TopologicalEvaluationReport confirmado.** Reporte de evaluación topológica por documento. Campos: `document_id`, `metrics`, `overall_score`. |
| **E-4.2-012** | N/A | `core/benchmark/topology/models.py::ConfusionMatrix` | **ConfusionMatrix confirmado.** Matriz de confusión con propiedades `precision`, `recall`, `f1_score`. |
| **E-4.2-013** | N/A | `tools/evaluation/topology/strategies.py::DefaultBenchmarkAggregationStrategy` | **DefaultBenchmarkAggregationStrategy confirmado.** Agregación por promedio aritmético simple por métrica. |
| **E-4.2-014** | P2 | `core/validation/ast/validators/strategy.py::PassthroughIntegrityValidator` | **PassthroughIntegrityValidator usa severity HARD_FAIL.** Este validador de estrategia para nodos estructurales usa `ValidationSeverity.HARD_FAIL`. Confirma que el concepto de severidad existe en validación pre-LLM, pero no es criticidad de regresión. |
| **E-4.2-015** | P2 | `core/validation/ast/validators/structural.py::StructuralEquationValidator` | **StructuralEquationValidator usa severity SOFT_FAIL.** Este validador estructural de ecuaciones usa `ValidationSeverity.SOFT_FAIL`. Confirma que el concepto de severidad existe en validación pre-LLM, pero no es criticidad de regresión. |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-4.2-01 | `ValidationSeverity` (INFO, SOFT_FAIL, HARD_FAIL) y la criticidad de regresión propuesta (CRITICAL, WARNING, INFO) son conceptos ortogonales. No deben unificarse ni confundirse. ValidationSeverity gobierna la validación de nodos AST antes de la inferencia LLM. La criticidad de regresión gobierna la evaluación de desviaciones topológicas contra el oráculo sellado. | Medio | OPEN |
| OBS-4.2-02 | `EditCostPolicy` (Protocol) y `TreeEditCostContext` (Protocol) son puertos diferentes. `EditCostPolicy` opera por `node_type` (ContentNodeType), mientras que `TreeEditCostContext` opera por `ASTNode`. La implementación de costos ponderados por criticidad debe decidir cuál puerto implementar o si se necesita un nuevo puerto. | Medio | OPEN |
| OBS-4.2-03 | `DefaultBenchmarkAggregationStrategy` agrega por promedio aritmético simple. Para regresión graduada, puede ser necesario un agregador ponderado por criticidad o un agregador que produzca un veredicto discreto (PASS/WARNING/HARD_FAIL) en lugar de un score continuo. | Medio | OPEN |
| OBS-4.2-04 | `TopologicalEvaluationReport` tiene un campo `overall_score: float | None`. Para regresión graduada, puede ser necesario extender este reporte con un campo de veredicto discreto (`verdict: RegressionVerdict`). | Medio | OPEN |
| OBS-4.2-05 | La taxonomía de criticidad propuesta debe ser extensible. Si se agregan nuevos tipos de nodo a `ContentNodeType` en el futuro, la taxonomía de criticidad debe poder mapearlos sin modificar el código existente (Open/Closed Principle). | Bajo | OPEN |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Taxonomía de Criticidad (DC-06)

| Elemento | Estado | Evidencia |
|---|---|---|
| Enum de criticidad (NodeCriticality) | FALTANTE | E-4.2-001 |
| Política de mapeo ContentNodeType → NodeCriticality | FALTANTE | E-4.2-001 |
| Contexto de costos ponderados (CriticalityAwareCostContext) | FALTANTE | E-4.2-003, E-4.2-006 |
| Extensibilidad de la taxonomía | FALTANTE | E-4.2-001 |

**Veredicto del pilar:** Completamente ausente. DC-06 debe materializarse desde cero en Fase 4.

### Pilar 2 — Reglas de Regresión Graduada (DC-07)

| Elemento | Estado | Evidencia |
|---|---|---|
| Modelo de veredicto (RegressionVerdict) | FALTANTE | E-4.2-002 |
| Configuración de umbrales (RegressionThresholds) | FALTANTE | E-4.2-002 |
| Estrategia de evaluación de regresión (RegressionEvaluationStrategy) | FALTANTE | E-4.2-002, E-4.2-007 |
| Agregador de veredicto | FALTANTE | E-4.2-002, OBS-4.2-03 |
| Extensión de TopologicalEvaluationReport con veredicto | FALTANTE | E-4.2-002, OBS-4.2-04 |

**Veredicto del pilar:** Completamente ausente. DC-07 debe materializarse desde cero en Fase 4.

### Pilar 3 — Conexión con Baseline Sellada

| Elemento | Estado | Evidencia |
|---|---|---|
| Adaptador SealedOracle → evaluación | FALTANTE | E-4.2-007 |
| Verificación de oracle_hash antes de evaluar | FALTANTE | E-4.2-007, HITO 4.1 E-4.1-021 |
| Verificación de completitud biyectiva | FALTANTE | E-4.2-007 |

**Veredicto del pilar:** Completamente ausente. GAP-2.0-11 heredado. Debe materializarse en Fase 4.

### Pilar 4 — Regresión Actual (Estado Actual)

| Elemento | Estado | Evidencia |
|---|---|---|
| Golden test | DEFECTUOSO (tautológico) | E-4.2-004, GAP-0.4-09 |
| Snapshot de chunking | DEFECTUOSO (auto-generación, sub-aserción) | E-4.2-004, C5-R01, C5-R02 |
| CI workflows | AUSENTE | HITO 0.4.4_C5 GAP-C5-05 |
| pyproject.toml | AUSENTE | HITO 0.4.4_C5 GAP-C5-04 |

**Veredicto del pilar:** La regresión actual no es confiable. Debe ser remediada antes de que la regresión graduada pueda ser efectiva.

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-4.2-01** | No existe taxonomía de criticidad de nodos. No existe mapeo ContentNodeType → CRITICAL/WARNING/INFO. (DC-06) | E-4.2-001 | Pilar 1 / ADR Maestro §8 DC-06 | **Fase 4** | OPEN |
| **GAP-4.2-02** | No existen reglas de regresión graduada. No existe mecanismo de veredicto PASS/WARNING/HARD_FAIL. (DC-07) | E-4.2-002 | Pilar 2 / ADR Maestro §8 DC-07 | **Fase 4** | OPEN |
| **GAP-4.2-03** | UnitCostContext aplica costos uniformes sin ponderación por criticidad. Debe extenderse para soportar CriticalityAwareCostContext. | E-4.2-003, E-4.2-006 | Pilar 1 / HITO 0.4.1 recomendación DC-06 | **Fase 4** | OPEN |
| **GAP-4.2-04** | Regresión actual limitada a snapshots binarios o tautologías. Golden test tautológico (GAP-0.4-09), snapshot con auto-generación (C5-R01) y sub-aserción (C5-R02). | E-4.2-004 | Pilar 4 / HITO 0.4.4 GAP-0.4-09, C5-R01, C5-R02 | **Fase 4** | OPEN |
| **GAP-4.2-05** | Conexión SealedOracle → evaluación ausente. (GAP-2.0-11 heredado, GAP-4.1-01) | E-4.2-007 | Pilar 3 / HITO 2.0 GAP-2.0-11, HITO 4.1 GAP-4.1-01 | **Fase 4** | OPEN |
| **GAP-4.2-06** | EditCostPolicy (Protocol) sin implementación concreta. | E-4.2-006 | Pilar 1 / core/benchmark/topology/ports.py | **Fase 4** | OPEN |
| **GAP-4.2-07** | CI workflows ausentes. pyproject.toml ausente. | HITO 0.4.4_C5 GAP-C5-04, GAP-C5-05 | Pilar 4 / HITO 0.4.4_C5 | **Fase 4 / Fase 6** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-4.2-A | Existe alguna taxonomía de criticidad en el repositorio. | RECHAZADA | E-4.2-001 | No existe ningún enum, política o contrato de criticidad. DC-06 debe materializarse desde cero. |
| H-4.2-B | Existen reglas de regresión graduada en el repositorio. | RECHAZADA | E-4.2-002 | No existe ningún mecanismo de veredicto. DC-07 debe materializarse desde cero. |
| H-4.2-C | UnitCostContext puede extenderse para soportar costos ponderados sin romper el contrato existente. | CONFIRMADA | E-4.2-003, E-4.2-009 | UnitCostContext implementa TreeEditCostContext. Una nueva implementación (CriticalityAwareCostContext) puede implementar el mismo Protocol sin modificar UnitCostContext. |
| H-4.2-D | ValidationSeverity puede reutilizarse como criticidad de regresión. | RECHAZADA | E-4.2-005, OBS-4.2-01 | ValidationSeverity gobierna validación pre-LLM, no criticidad de regresión. Son conceptos ortogonales. No deben unificarse. |
| H-4.2-E | La regresión actual (golden test, snapshots) es confiable. | RECHAZADA | E-4.2-004, GAP-0.4-09, C5-R01, C5-R02 | La regresión actual no es confiable. Debe ser remediada antes de que la regresión graduada pueda ser efectiva. |
| H-4.2-F | EditCostPolicy tiene implementación concreta. | RECHAZADA | E-4.2-006 | EditCostPolicy es un Protocol sin implementación. Debe implementarse para soportar costos ponderados. |
| H-4.2-G | La conexión SealedOracle → evaluación existe. | RECHAZADA | E-4.2-007 | No existe ningún componente que conecte SealedOracle con evaluación. GAP-2.0-11 heredado. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué existe actualmente para la taxonomía de criticidad (DC-06)?

**Estado actual verificado:**

1. No existe ningún enum de criticidad (NodeCriticality) en el repositorio.
2. No existe ninguna política de mapeo ContentNodeType → criticidad.
3. No existe ningún contexto de costos ponderados (CriticalityAwareCostContext).
4. `EditCostPolicy` (Protocol) existe en `core/benchmark/topology/ports.py` pero no tiene implementación concreta.
5. `UnitCostContext` implementa `TreeEditCostContext` con costos uniformes (1.0).
6. `ValidationSeverity` (INFO, SOFT_FAIL, HARD_FAIL) existe en validación pre-LLM pero no es criticidad de regresión.

**Respuesta forense:**

No existe nada reutilizable para DC-06. La taxonomía de criticidad debe crearse desde cero en Fase 4.

**Implicación:**

Fase 4 debe crear:
- Un enum `NodeCriticality` con valores CRITICAL, WARNING, INFO.
- Una política `CriticalityPolicy` que mapee `ContentNodeType` → `NodeCriticality`.
- Un contexto de costos `CriticalityAwareCostContext` que implemente `TreeEditCostContext` con costos ponderados por criticidad.

### 16.2 ¿Qué existe actualmente para las reglas de regresión graduada (DC-07)?

**Estado actual verificado:**

1. No existe ningún modelo de veredicto (RegressionVerdict) en el repositorio.
2. No existe ninguna configuración de umbrales (RegressionThresholds).
3. No existe ninguna estrategia de evaluación de regresión (RegressionEvaluationStrategy).
4. `ParserEvaluationStrategy` existe pero es para comparación de parsers, no para regresión.
5. `TopologicalEvaluationReport` tiene `overall_score: float | None` pero no tiene campo de veredicto discreto.
6. La regresión actual se limita a snapshots binarios o tautologías.

**Respuesta forense:**

No existe nada reutilizable para DC-07. Las reglas de regresión graduada deben crearse desde cero en Fase 4.

**Implicación:**

Fase 4 debe crear:
- Un modelo `RegressionVerdict` con valores PASS, WARNING, HARD_FAIL.
- Una configuración `RegressionThresholds` con umbrales de NSS.
- Una estrategia `RegressionEvaluationStrategy` que evalúe runtime vs oráculo sellado y produzca un veredicto.
- Una extensión de `TopologicalEvaluationReport` con campo de veredicto discreto.

### 16.3 ¿Qué taxonomía de criticidad se propone?

> **NOTA: HIPÓTESIS DE TRABAJO. Lo siguiente es una hipótesis de trabajo derivada de la evidencia forense. No es una decisión fijada. La validación empírica y la fijación normativa corresponden al ADR_F17-BIS_04 y los NADRs de Fase 4.**

**Estado actual verificado:**

1. `ContentNodeType` tiene 11 miembros: COMPOSITE_BLOCK, HEADING, PARAGRAPH, DISPLAY_EQUATION, INLINE_EQUATION, TABLE_SIMPLE, TABLE_COMPLEX, IMAGE, CAPTION, CODE, LIST.
2. HITO 0.4.2 OBS-0.4.2-04: "ContentNodeType carece de métodos o clasificadores de criticidad semántica".
3. HITO 0.4.1 recomienda: "Extender TreeEditCostContext para asignar penalizaciones diferenciadas según la severidad del nodo (HEADING > PARAGRAPH)".

**Respuesta forense:**

Se propone la siguiente taxonomía de criticidad basada en el impacto de la pérdida de cada tipo de nodo en el contenido científico del documento:

| ContentNodeType | Criticidad propuesta | Justificación |
|---|---|---|
| DISPLAY_EQUATION | CRITICAL | La pérdida de una ecuación en bloque destruye contenido científico primario. Es irrecuperable. |
| INLINE_EQUATION | CRITICAL | La pérdida de una ecuación inline destruye contenido científico primario. Es irrecuperable. |
| TABLE_SIMPLE | CRITICAL | La pérdida de una tabla destruye datos estructurados científicos. Es irrecuperable. |
| TABLE_COMPLEX | CRITICAL | La pérdida de una tabla compleja destruye datos estructurados científicos. Es irrecuperable. |
| HEADING | WARNING | La pérdida de un heading degrada la topología del documento pero el contenido textual sobrevive. La estructura puede reconstruirse por contexto. El NSS ya captura el impacto topológico. |
| PARAGRAPH | WARNING | La pérdida de un párrafo es significativa pero el documento puede seguir siendo comprensible. |
| CODE | WARNING | La pérdida de código degrada pero no destruye la prosa. |
| IMAGE | INFO | La pérdida de una imagen degrada pero no destruye el texto. En un contexto de traducción, la imagen se preserva como referencia (AssetReference). |
| CAPTION | INFO | Los captions son elementos auxiliares. |
| LIST | INFO | Las listas son elementos auxiliares. |
| COMPOSITE_BLOCK | INFO | Los bloques compuestos son elementos auxiliares. |

**Justificación de HEADING → WARNING (no CRITICAL):**

En el debate arquitectónico se consideró elevar HEADING a CRITICAL porque los headings son los anchors del particionado (`HeadingAnchorPartitionStrategy`). Sin embargo, se descartó por las siguientes razones:

1. El NSS (Normalized Structural Score) ya captura el impacto de la pérdida de un heading en la topología del documento.
2. No necesitamos elevar HEADING a CRITICAL para capturar ese impacto; el NSS ponderado ya lo hace.
3. La regla de HARD_FAIL por pérdida de nodo CRITICAL es una protección absoluta. Si la aplicamos a HEADING, cualquier pérdida de heading sería HARD_FAIL, lo cual es excesivo: un heading perdido no destruye el contenido científico primario.
4. El contenido textual de la sección sobrevive. La estructura puede reconstruirse por contexto (el siguiente heading, el contenido de la sección).

**Implicación:**

Esta taxonomía debe ser validada empíricamente antes de ser fijada. Los valores de costos ponderados deben ser configurables vía política inyectada, con valores por defecto documentados como "propuesta inicial pendiente de validación empírica".

### 16.4 ¿Qué reglas de regresión graduada se proponen?

> **NOTA: HIPÓTESIS DE TRABAJO. Lo siguiente es una hipótesis de trabajo derivada de la evidencia forense. No es una decisión fijada. La validación empírica y la fijación normativa corresponden al ADR_F17-BIS_04 y los NADRs de Fase 4.**
>
> **NOTA SOBRE UMBRALES: Los valores numéricos de NSS propuestos (0.80 y 0.95) son completamente ARBITRARIOS y carecen de justificación empírica. Son placeholders para la validación empírica que debe realizarse en Fase 4 antes de fijarlos normativamente. No deben usarse en producción hasta ser validados.**

**Estado actual verificado:**

1. No existe ningún mecanismo de veredicto en el repositorio.
2. ADR Maestro §3: "Regresión no es Coincidencia Binaria (Snapshotting)".
3. ADR Maestro §8 DC-07: "¿Bajo qué condiciones específicas de desalineación topológica o divergencia de contenido la suite de integración emite un HARD FAIL vs. un WARNING?"

**Respuesta forense:**

Se proponen las siguientes reglas de regresión graduada:

| Condición | Veredicto | Justificación |
|---|---|---|
| Pérdida de nodos CRITICAL (ecuaciones, tablas) | HARD_FAIL | Contenido científico primario destruido. Irrecuperable. |
| NSS < umbral crítico (default propuesto: 0.80) | HARD_FAIL | Desviación estructural severa. |
| Pérdida de nodos WARNING (headings, párrafos, código) | WARNING | Estructura degradada pero no destruida. |
| NSS entre umbral crítico y umbral de advertencia (default propuesto: 0.95) | WARNING | Desviación estructural moderada. |
| Pérdida de nodos INFO (imágenes, captions, listas) | PASS (con observación) | Elementos auxiliares. |
| NSS > umbral de advertencia (default propuesto: 0.95) | PASS | Sin desviación significativa. |

**Doble mecanismo de protección:**

La taxonomía de criticidad afecta dos mecanismos distintos y complementarios:

1. **NSS ponderado por criticidad (protección gradual):** Los costos de edición en el TED se ponderan por criticidad. Un nodo CRITICAL tiene costo de borrado mayor que un nodo INFO. El NSS resultante refleja la criticidad.
2. **Regla de pérdida de nodo CRITICAL (protección absoluta):** Si se pierde un nodo CRITICAL, HARD_FAIL independiente del NSS.

Ambos mecanismos son necesarios y complementarios. El NSS ponderado solo captura el impacto gradual. Si se pierde 1 nodo CRITICAL de 1000, el NSS puede seguir alto (> 0.95) y el veredicto sería PASS. Esto es incorrecto: la pérdida de una ecuación es irrecuperable. La regla de pérdida de nodo CRITICAL captura el impacto absoluto.

**Implicación:**

Los umbrales de NSS deben ser configurables vía política inyectada, con valores por defecto documentados como "propuesta inicial pendiente de validación empírica". No deben fijarse como constantes hasta que haya evidencia empírica.

### 16.5 ¿Qué componentes deben crearse en Fase 4?

**Estado actual verificado:**

1. No existe ningún componente de criticidad ni de regresión graduada en el repositorio.
2. Los puertos `TreeEditCostContext` y `EditCostPolicy` existen pero no tienen implementación ponderada.
3. `TopologicalEvaluationReport` existe pero no tiene campo de veredicto discreto.
4. `ParserEvaluationStrategy` existe pero es para comparación de parsers, no para regresión.

**Respuesta forense:**

Fase 4 debe crear los siguientes componentes:

| Componente | Propósito | Puerto / Contrato |
|---|---|---|
| `NodeCriticality` (enum) | Taxonomía de criticidad: CRITICAL, WARNING, INFO | Nuevo enum en `core/benchmark/topology/` |
| `CriticalityPolicy` | Mapeo ContentNodeType → NodeCriticality | Nueva política en `core/benchmark/topology/` |
| `CriticalityAwareCostContext` | Costos de edición ponderados por criticidad | Implementa `TreeEditCostContext` |
| `RegressionVerdict` (enum) | Veredicto de regresión: PASS, WARNING, HARD_FAIL | Nuevo enum en `core/benchmark/topology/` |
| `RegressionThresholds` | Configuración de umbrales de NSS | Nuevo modelo en `core/benchmark/topology/` |
| `RegressionEvaluationStrategy` | Estrategia de evaluación runtime vs oráculo | Implementa `EvaluationStrategy` |
| Extensión de `TopologicalEvaluationReport` | Campo de veredicto discreto | Extensión del modelo existente |
| Adaptador SealedOracle → evaluación | Conexión con baseline sellada | Nuevo adaptador en `core/benchmark/topology/` |

**Implicación:**

Todos los componentes deben ser creados en `core/benchmark/topology/` (dominio puro), siguiendo la arquitectura hexagonal. No deben introducirse dependencias de infraestructura en el dominio.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-06** | Taxonomía de Criticidad de Nodos | E-4.2-001, E-4.2-003, E-4.2-006, GAP-4.2-01, GAP-4.2-03, GAP-4.2-06 | Ausente. No existe ningún enum, política o contrato de criticidad. | **Fase 4** |
| **DC-07** | Reglas de Regresión Topológica | E-4.2-002, E-4.2-004, GAP-4.2-02, GAP-4.2-04 | Ausente. No existe ningún mecanismo de veredicto. | **Fase 4** |
| **DC-10** | Desacoplamiento del Runner de CI | HITO 0.4.4_C5 GAP-C5-04, GAP-C5-05, GAP-4.2-07 | Ausente en el contexto de regresión. Existe para benchmark. | **Fase 4 / Fase 6** |

**Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos. DC-06 y DC-07 fueron resueltos normativamente en el ADR Maestro §8, pero no tienen materialización operativa.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Taxonomía de criticidad sin validación empírica | La taxonomía propuesta es una hipótesis basada en el impacto semántico de cada tipo de nodo. Debe ser validada empíricamente antes de ser fijada. | Alto | E-4.2-001, GAP-4.2-01 |
| Umbrales de NSS sin validación empírica | Los umbrales propuestos (0.80, 0.95) son completamente arbitrarios. Deben ser validados empíricamente antes de ser fijados. | Alto | E-4.2-002, GAP-4.2-02 |
| Confusión entre ValidationSeverity y criticidad de regresión | ValidationSeverity (INFO, SOFT_FAIL, HARD_FAIL) y la criticidad de regresión (CRITICAL, WARNING, INFO) son conceptos ortogonales. Existe el riesgo de que se confundan o se unifiquen incorrectamente. | Medio | E-4.2-005, OBS-4.2-01 |
| Regresión actual no confiable | La regresión actual (golden test tautológico, snapshots con auto-generación) no es confiable. Debe ser remediada antes de que la regresión graduada pueda ser efectiva. | Alto | E-4.2-004, GAP-0.4-09, C5-R01, C5-R02 |
| Ausencia de CI workflows | Sin CI workflows, las reglas de regresión no pueden ser aplicadas automáticamente. | Alto | HITO 0.4.4_C5 GAP-C5-05 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR o NADR posterior deberá responder:

1. ¿Cuál es la taxonomía de criticidad exacta? ¿Qué ContentNodeType se mapea a CRITICAL, WARNING e INFO? ¿Cuál es la justificación de cada mapeo?
2. ¿Cuáles son las reglas exactas de regresión? ¿Bajo qué condiciones se emite HARD_FAIL vs WARNING vs PASS?
3. ¿Los umbrales de NSS son fijos o configurables? Si son configurables, ¿cuáles son los defaults?
4. ¿La verificación de oracle_hash es obligatoria antes de toda evaluación? ¿Qué error se emite si falla?
5. ¿La NormalizedNodeMatchingPolicy reemplaza a DefaultNodeMatchingPolicy o coexiste con ella?
6. ¿Se depreca StructuralTopologyMetric en Fase 4 o se mantiene hasta que haya evidencia de equivalencia?
7. ¿El CriticalityAwareCostContext extiende UnitCostContext o es una implementación independiente de TreeEditCostContext?
8. ¿El RegressionVerdict es un enum simple o un modelo con métricas detalladas?
9. ¿Cómo se protege el framing del matching_key contra ambigüedad cuando text_content contiene ":"? *(Heredada de HITO_4.1 GAP-4.1-07. Incluida aquí para trazabilidad.)*
10. ¿Cómo se valida empíricamente la taxonomía de criticidad antes de fijarla?
11. ¿Cómo se validan empíricamente los umbrales de NSS antes de fijarlos?
12. ¿Cómo se remedia la regresión actual (golden test tautológico, snapshots con auto-generación) antes de que la regresión graduada pueda ser efectiva?

---

## 21. CIERRE DEL HITO 4.2

Este HITO confirma que no existe ninguna taxonomía de criticidad ni reglas de regresión graduada en el repositorio. DC-06 y DC-07 están completamente ausentes a nivel operativo. Se propone una taxonomía de 3 niveles (CRITICAL / WARNING / INFO) mapeada a ContentNodeType, y reglas de veredicto basadas en NSS ponderado y pérdida de nodos críticos.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados. Todas las evidencias tienen ID estable y severidad. Todos los gaps tienen evidencia vinculada y fase destino. Todas las hipótesis están cerradas como CONFIRMADA, RESUELTA, RECHAZADA o TO BE VERIFIED. Cero hipótesis abiertas sin destino. Las 5 correcciones de forma han sido aplicadas.
**Verificación de cadena de gobernanza:** ADR_F17_BIS_MASTER → HITO_0.4.2 → HITO_0.4.1 → HITO_0.4.4 → HITO_0.4.4_C5 → HITO_2.0 → FASE_3_HANDOFF → HITO_4.1 → HITO_4.2 (este documento). Cadena completa verificada.
**Contradicciones con HITOs previos:** Ninguna. Todos los hallazgos son consistentes con los HITOs previos. Los gaps heredados (GAP-0.4-09, GAP-2.0-11, C5-R01, C5-R02) se confirman como persistentes.
**Decision Candidates generados:** Ninguno nuevo. DC-06 y DC-07 ya existen en el ADR Maestro §8. Este HITO confirma su ausencia operativa y propone la estructura normativa que Fase 4 debe materializar.
**Siguiente paso recomendado:** Construir HITO_4.3 (Baseline→Benchmark Adapter and Entry Point Discovery) usando este HITO como insumo, para auditar cómo conectar SealedOracle con la evaluación topológica y definir el entry point de regresión. Luego construir ADR_F17-BIS_04 (Scientific Verification) y los NADRs de Fase 4.