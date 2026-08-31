# HITO_4.3_BASELINE_BENCHMARK_ADAPTER_ENTRY_POINT_DISCOVERY.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-08-30
**Fecha de congelamiento:** 2026-08-30
**Fase:** 17-BIS — Fase 4 (Scientific Verification)
**Tipo de artefacto:** Forensic Discovery / Compliance-oriented Infrastructure Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT (FROZEN), HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT (FROZEN), HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY (FROZEN v2.1.0), FASE_3_HANDOFF (FROZEN v1.0.0), HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY (FROZEN), HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0-FROZEN.
**Mandato:** Auditar cómo el `SealedOracle` se conecta (o deja de conectarse) con la infraestructura de evaluación topológica, identificar los gaps en el entry point de regresión, determinar qué debe crearse para que Fase 4 pueda evaluar el runtime contra el oráculo sellado, y verificar la presencia o ausencia de verificación de `oracle_hash` antes de la evaluación.
**Síntesis:** No existe ningún componente que conecte el `SealedOracle` con la evaluación topológica, verifique su integridad criptográfica antes de evaluar, ni produzca un veredicto de regresión. El protocolo `EvaluationStrategy` es arquitectónicamente compatible con `SealedOracle.nodes`, pero la capa de orquestación, verificación y entry point están completamente ausentes. GAP-2.0-11 heredado del HITO 2.0 se confirma como el gap central de Fase 4.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-08-30 | Emisión inicial. Discovery forense del adaptador baseline→benchmark y entry point de regresión. |
| 1.0.0-FROZEN | 2026-08-30 | Aplicación de 4 correcciones de forma: (1) estado FROZEN, (2) evidencia E-4.3-015 hydrate_ground_truth(), (3) evidencia E-4.3-016 LoadGroundTruthUseCase, (4) H-4.3-C marcada como inferencia de tipos. Referencias a tests de regresión y framing del matching_key. Congelamiento formal. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la totalidad de la superficie de conexión entre la baseline sellada (`SealedOracle`, `CorpusManifest`, `oracle_hash`) y la infraestructura de evaluación topológica (`EvaluationStrategy`, `TreeEditDistanceEvaluator`, `EntityRecallEvaluator`, `TopologyBenchmarkService`). Se inspeccionaron los puertos de lectura del Ground Truth (`GroundTruthReaderPort`, `LocalFileSystemGroundTruthReader`), la fábrica de hidratación (`hydrate_ground_truth()`), el caso de uso de carga (`LoadGroundTruthUseCase`), el composition root topológico (`create_topology_evaluator()`), la estrategia de evaluación existente (`ParserEvaluationStrategy`), el servicio de benchmark (`TopologyBenchmarkService`), y el entry point CLI (`run_benchmark.py`).

**Hallazgo central:**

> No existe ningún componente en el repositorio que cargue un `SealedOracle`, verifique su `oracle_hash` mediante `OracleSemanticIdentityCalculator`, lo conecte con los evaluadores topológicos existentes, y produzca un veredicto de regresión graduado. El protocolo `EvaluationStrategy` es arquitectónicamente compatible con `SealedOracle.nodes` (ambos operan sobre `Sequence[ASTNode]`), pero la capa de orquestación de regresión, la verificación de integridad criptográfica y el entry point de ejecución están completamente ausentes. GAP-2.0-11 heredado del HITO 2.0 se confirma como el gap central de Fase 4.

**Defectos dominantes confirmados:**

1. **Ausencia total de conexión SealedOracle → evaluación (E-4.3-001, E-4.3-002):** Ningún componente de `core/benchmark/topology/` ni de `tools/evaluation/` consume `SealedOracle` ni verifica `oracle_hash` antes de evaluar. GAP-2.0-11 heredado del HITO 2.0, confirmado en HITO 4.1 como GAP-4.1-01.
2. **Ausencia de estrategia de evaluación de regresión (E-4.3-003, E-4.3-004):** `ParserEvaluationStrategy` está diseñada para comparación de parsers (parser A vs parser B), no para regresión contra oráculo sellado (runtime vs SealedOracle). No existe `RegressionEvaluationStrategy`.
3. **Ausencia de verificación de integridad criptográfica antes de evaluar (E-4.3-005, E-4.3-006):** Ningún componente verifica `oracle_hash` mediante `OracleSemanticIdentityCalculator.calculate()` antes de usar el oráculo como referencia de evaluación. Riesgo de evaluar contra un oráculo mutado en disco.
4. **Ausencia de entry point de regresión (E-4.3-007, E-4.3-008):** No existe ningún CLI tool ni script que ejecute la evaluación de regresión del runtime contra el oráculo sellado. `run_benchmark.py` es para benchmark de extractores, no para regresión.

**Veredicto:** Fase 4 debe crear desde cero el adaptador SealedOracle→evaluación, la estrategia de evaluación de regresión, la verificación de integridad criptográfica y el entry point de ejecución. La infraestructura matemática y los evaluadores existentes son reutilizables sin modificación.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Este HITO no audita el motor matemático Zhang-Shasha ni los evaluadores TED/Recall (cubiertos por HITO_4.1). No audita la taxonomía de criticidad ni las reglas de regresión (cubiertos por HITO_4.2). Este HITO se limita exclusivamente a la capa de conexión entre la baseline sellada y la evaluación topológica, la verificación de integridad criptográfica, y el entry point de ejecución.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR_F17_BIS_MASTER §3 (Dimensión REGRESIÓN), §5 (Invariantes), HITO_2.0 (GAP-2.0-11), HITO_4.1 (GAP-4.1-01), HITO_4.2 (GAP-4.2-05).
2. Cargar HITOs previos aplicables: HITO_0.4.1, HITO_0.4.4_C1, HITO_2.0, FASE_3_HANDOFF.
3. Inspeccionar código fuente de todos los módulos del alcance.
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs E-4.3-NNN.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar TO BE VERIFIED cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/benchmark/topology/ports.py` | `EvaluationStrategy`, `TopologicalEvaluatorProtocol`, `ScoreAggregationPolicy`, `TreeEditCostContext`, `NodeMatchingPolicy` | 100% auditado |
| `core/benchmark/topology/strategies.py` | `ParserEvaluationStrategy` | 100% auditado |
| `core/benchmark/topology/models.py` | `TopologicalEvaluationReport`, `MetricScoreDTO` | 100% auditado |
| `core/benchmark/ground_truth/models.py` | `SealedOracle`, `GroundTruthDraft`, `GroundTruthLifecycleState`, `hydrate_ground_truth()` | 100% auditado |
| `core/benchmark/ground_truth/identity.py` | `OracleSemanticIdentityCalculator` | 100% auditado |
| `core/benchmark/ground_truth/ports.py` | `GroundTruthReaderPort`, `GroundTruthDraftWriterPort`, `ASTExtractionPort`, `GroundTruthArtifactPort` | 100% auditado |
| `core/benchmark/ground_truth/completeness.py` | `BaselineCompletenessVerifier` | 100% auditado |
| `core/benchmark/ground_truth/use_cases.py` | `LoadGroundTruthUseCase`, `SealGroundTruthUseCase` | 100% auditado |
| `core/benchmark/corpus/models.py` | `CorpusManifest`, `CorpusDocumentMetadata` (campos `oracle_hash`, `ground_truth_state`) | 100% auditado |
| `core/benchmark/corpus/ports.py` | `CorpusManifestReaderPort`, `CorpusManifestWriterPort` | 100% auditado |
| `core/benchmark/corpus/services.py` | `ManifestFingerprintCalculator`, `ManifestLineageSealer` | 100% auditado |
| `infra/fs/ground_truth_store.py` | `LocalFileSystemGroundTruthReader`, `LocalFileSystemGroundTruthDraftWriter`, `LocalFileSystemGroundTruthArtifactAdapter` | 100% auditado |
| `infra/fs/corpus_repository.py` | `LocalFileSystemCorpusLoader` | 100% auditado |
| `bootstrap/topology.py` | `DefaultNodeMatchingPolicy`, `create_topology_evaluator()` | 100% auditado |
| `tools/evaluation/application/benchmark_service.py` | `TopologyBenchmarkService` | 100% auditado |
| `tools/evaluation/run_benchmark.py` | Entry point CLI de benchmark | 100% auditado |
| `tools/evaluation/topology/models.py` | `BenchmarkDocument`, `DocumentEvaluationResult`, `BenchmarkSummaryReport` | 100% auditado |
| `tools/evaluation/topology/ports.py` | `TopologyMetric`, `BenchmarkAggregationStrategy` | 100% auditado |
| `tools/evaluation/infrastructure/corpus_repository.py` | `LocalFileSystemCorpusRepository` | 100% auditado |
| `core/shared/identity_contracts.py` | `DocumentId`, `NodeId`, `GroundTruthState` | Referenciado (auditado en HITO 4.1, Fase 3) |
| `core/ast/models.py` | `ASTNode` (campos `node_id`, `parent_node_id`) | Referenciado (auditado en HITO 4.1, Fase 3) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER §3 (Dimensión REGRESIÓN), §5 (Invariantes) | Fuente normativa: definición de regresión y Zero Partial Sealing |
| HITO previo | HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY (GAP-2.0-11) | Evidencia forense heredada: adaptador baseline→benchmark ausente |
| HITO previo | HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY (GAP-4.1-01, GAP-4.1-07) | Evidencia forense: conexión SealedOracle→evaluación ausente, framing del matching_key sin protección |
| HITO previo | HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY (GAP-4.2-05, GAP-4.2-04) | Evidencia forense: conexión SealedOracle→evaluación ausente, tests de regresión no confiables |
| HITO previo | HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT | Evidencia forense heredada: estado de la infraestructura topológica |
| HITO previo | HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT | Evidencia forense heredada: circuito canónico de evaluación |
| HITO previo | HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT | Contexto: estado de tests de regresión y CI (tautología en golden test, ausencia de CI workflow) |
| Handoff | FASE_3_HANDOFF v1.0.0 | Estado de Fase 3, carry-forward obligatorio |
| Código | core/benchmark/topology/*, core/benchmark/ground_truth/*, core/benchmark/corpus/* | Observación runtime/código |
| Código | infra/fs/ground_truth_store.py, infra/fs/corpus_repository.py | Observación runtime/código |
| Código | bootstrap/topology.py, tools/evaluation/* | Observación runtime/código |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 | Estructura canónica del HITO |

> **Nota sobre secciones condicionales:** Las secciones 7 (Matriz Observed / Required / Decision), 8 (Mutation Semantics Matrix), 9 (Canonicalization / Determinism Audit) y 17 (Verificación de Cumplimiento ADR/NADR) no aplican a este HITO. Este HITO es un Forensic Discovery / Compliance-oriented Infrastructure Audit centrado en la capa de conexión y entry point, no en la semántica de mutación ni en la canonicalización.

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Conexión SealedOracle → Evaluación Topológica (AUSENTE)

```text
FLUJO A -- Conexion SealedOracle -> Evaluacion Topologica (AUSENTE)

  SealedOracle [Existe en core/benchmark/ground_truth/models.py]
    |
    +---> ??? [GAP: ningun componente carga SealedOracle para evaluacion]
    |
    +---> oracle_hash verification [GAP: no se verifica antes de evaluar]
    |         OracleSemanticIdentityCalculator.calculate(oracle.nodes) == oracle_hash
    |
    +---> BaselineCompletenessVerifier.verify() [GAP: no se verifica en contexto de evaluacion]
    |
    +---> EvaluationStrategy.evaluate_run(document_id, runtime_ast, oracle.nodes)
    |         [GAP: no existe RegressionEvaluationStrategy]
    |
    +---> RegressionVerdict [GAP: no existe]

Leyenda:
  [GAP] gap confirmado. Este flujo NO EXISTE actualmente.
```

### FLUJO B — Flujo actual de evaluación de parsers (EXISTENTE, NO APLICABLE A REGRESIÓN)

```text
FLUJO B -- Flujo actual de evaluacion de parsers (EXISTENTE)

  run_benchmark.py [tools/evaluation/run_benchmark.py]
    |
    +---> LocalFileSystemCorpusRepository.load_corpus_documents() [OK]
    |         Carga BenchmarkDocument con candidate y ground_truth como Sequence[ASTNode]
    |
    +---> TopologyBenchmarkService.evaluate_document(doc) [OK]
    |         Itera sobre metrics: Sequence[TopologyMetric]
    |         Cada metric.evaluate(candidate, ground_truth) -> MetricResult
    |
    +---> DefaultBenchmarkAggregationStrategy.aggregate() [OK]
    |         Promedio aritmetico simple por metrica
    |
    +---> BenchmarkSummaryReport [OK]

  NOTA: Este flujo es para benchmark de extractores (parser A vs parser B).
        NO es para regresion contra oraculo sellado (runtime vs SealedOracle).
        NO verifica oracle_hash. NO verifica completitud biyectiva.
        NO produce veredicto de regresion (PASS/WARNING/HARD_FAIL).

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado
```

### FLUJO C — Flujo actual de sellado de Ground Truth (EXISTENTE, CONTEXTO DE FASE 2/3)

```text
FLUJO C -- Flujo actual de sellado de Ground Truth (EXISTENTE)

  SealGroundTruthUseCase.execute(validated_drafts) [OK]
    |
    +---> BaselineCompletenessVerifier.verify() [OK]
    |         Verifica biyeccion manifest <-> oraculos
    |
    +---> OracleValidityContract.validate() [OK]
    |         Verifica validez estructural del oraculo
    |
    +---> LifecycleTransitionAuthority.seal(draft) -> SealedOracle [OK]
    |
    +---> OracleSemanticIdentityCalculator.calculate(oracle.nodes) -> oracle_hash [OK]
    |
    +---> ManifestLineageSealer.seal_manifest_with_ground_truth() [OK]
    |         Persiste oracle_hash y ground_truth_state en el manifiesto
    |
    +---> ManifestFingerprintCalculator.compute_hash() -> manifest_hash [OK]

  NOTA: Este flujo calcula oracle_hash durante el sellado.
        Pero NINGUN componente de evaluacion verifica oracle_hash antes de evaluar.
        El oracle_hash se calcula pero NUNCA se verifica en contexto de evaluacion.

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado
```

### FLUJO D — Flujo actual de carga de Ground Truth en runtime (EXISTENTE, SIN VERIFICACIÓN)

```text
FLUJO D -- Flujo actual de carga de Ground Truth en runtime (EXISTENTE)

  LoadGroundTruthUseCase.execute(document_id) [OK]
    |
    +---> GroundTruthReaderPort.load_ground_truth(document_id) [OK]
    |         Retorna Tuple[ASTNode, ...]
    |
    +---> LocalFileSystemGroundTruthReader.load_ground_truth() [OK]
    |         read_ast_json() -> Tuple[ASTNode, ...]
    |         NO verifica oracle_hash
    |         NO verifica ground_truth_state
    |         NO retorna SealedOracle (retorna Tuple[ASTNode, ...])
    |         NO usa hydrate_ground_truth()

  NOTA: El puerto de lectura retorna la secuencia de nodos cruda.
        NO retorna la entidad SealedOracle.
        NO verifica la integridad criptografica del oraculo.
        NO verifica el estado de ciclo de vida (SEALED vs DRAFT).
        NO usa la fabrica de hidratacion hydrate_ground_truth().

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado
```

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| `SealedOracle` | `core/benchmark/ground_truth/models.py` | Sí (entidad de dominio) | Oráculo sellado, verdad científica inmutable | CONFIRMADO |
| `SealedOracle.nodes` | `Tuple[ASTNode, ...]` | Sí (campo de la entidad) | Secuencia inmutable de nodos AST del oráculo | CONFIRMADO |
| `SealedOracle.document_id` | `str` (min_length=1) | Sí (identidad de la entidad) | Referencia al CorpusDocumentMetadata | CONFIRMADO |
| `hydrate_ground_truth()` | `core/benchmark/ground_truth/models.py` | Sí (fábrica de hidratación) | Convierte Tuple[ASTNode, ...] en SealedOracle o GroundTruthDraft según estado | CONFIRMADO (no usado en evaluación) |
| `OracleSemanticIdentityCalculator` | `core/benchmark/ground_truth/identity.py` | Sí (servicio de dominio) | Calcula oracle_hash (identidad semántica) | CONFIRMADO |
| `oracle_hash` (en manifiesto) | `CorpusDocumentMetadata.oracle_hash: Optional[str]` | Sí (campo del manifiesto) | Identidad semántica del oráculo sellado | CONFIRMADO |
| `ground_truth_state` (en manifiesto) | `CorpusDocumentMetadata.ground_truth_state: Optional[GroundTruthState]` | Sí (campo del manifiesto) | Estado operacional del ciclo de vida | CONFIRMADO |
| `GroundTruthReaderPort` | `core/benchmark/ground_truth/ports.py` | Sí (Protocol) | Puerto de lectura del oráculo en runtime | CONFIRMADO |
| `GroundTruthReaderPort.load_ground_truth()` | Retorna `Tuple[ASTNode, ...]` | Sí (método del Protocol) | Carga la secuencia de nodos del oráculo | CONFIRMADO (con gap) |
| `LocalFileSystemGroundTruthReader` | `infra/fs/ground_truth_store.py` | Sí (adaptador) | Implementación del puerto de lectura | CONFIRMADO |
| `LoadGroundTruthUseCase` | `core/benchmark/ground_truth/use_cases.py` | Sí (caso de uso) | Punto de entrada para cargar Ground Truth en runtime | CONFIRMADO (con gap) |
| `BaselineCompletenessVerifier` | `core/benchmark/ground_truth/completeness.py` | Sí (servicio de dominio) | Verifica biyección manifest ↔ oráculos | CONFIRMADO (no usado en evaluación) |
| `EvaluationStrategy` (Protocol) | `core/benchmark/topology/ports.py` | Sí (Protocol) | `evaluate_run(document_id, candidate_ast, ground_truth_ast)` | CONFIRMADO |
| `ParserEvaluationStrategy` | `core/benchmark/topology/strategies.py` | Sí (implementación) | Orquestador de evaluación de parsers | CONFIRMADO (uso diferente) |
| `TopologicalEvaluatorProtocol` | `core/benchmark/topology/ports.py` | Sí (Protocol) | `evaluate(candidate_ast, ground_truth_ast) -> MetricScoreDTO` | CONFIRMADO |
| `TreeEditDistanceEvaluator` | `core/benchmark/topology/evaluators/ted.py` | Sí (implementación) | Evaluador TED | CONFIRMADO |
| `EntityRecallEvaluator` | `core/benchmark/topology/evaluators/recall.py` | Sí (implementación) | Evaluador de recall por tipo | CONFIRMADO |
| `TopologyBenchmarkService` | `tools/evaluation/application/benchmark_service.py` | Sí (servicio de aplicación) | Orquestador de benchmark de extractores | CONFIRMADO (uso diferente) |
| `BenchmarkDocument` | `tools/evaluation/topology/models.py` | Sí (DTO) | Par candidate/ground_truth para benchmark | CONFIRMADO (uso diferente) |
| `run_benchmark.py` | `tools/evaluation/run_benchmark.py` | Sí (entry point CLI) | CLI de benchmark de extractores | CONFIRMADO (uso diferente) |
| `create_topology_evaluator()` | `bootstrap/topology.py` | Sí (composition root) | Ensambla el pipeline TED | CONFIRMADO |
| `RegressionEvaluationStrategy` | No existe | No | No existe estrategia de evaluación de regresión | MISSING |
| `RegressionVerdict` | No existe | No | No existe modelo de veredicto de regresión | MISSING |
| `RegressionThresholds` | No existe | No | No existe configuración de umbrales de regresión | MISSING |
| Adaptador SealedOracle→evaluación | No existe | No | No existe componente que conecte SealedOracle con evaluación | MISSING |
| Verificación de oracle_hash antes de evaluar | No existe | No | No existe verificación de integridad criptográfica antes de evaluar | MISSING |
| Entry point de regresión | No existe | No | No existe CLI tool para ejecutar regresión | MISSING |
| Verificación de completitud en evaluación | No existe | No | No existe verificación de biyección en contexto de evaluación | MISSING |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Para evidencia positiva (componentes SOTA confirmados), se usa N/A.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-4.3-001** | P0 | Ausencia total en todos los archivos auditados | **Ausencia total de conexión SealedOracle → evaluación.** Ningún componente de `core/benchmark/topology/` ni de `tools/evaluation/` consume `SealedOracle` ni lo conecta con los evaluadores topológicos. GAP-2.0-11 heredado del HITO 2.0, confirmado en HITO 4.1 como GAP-4.1-01. |
| **E-4.3-002** | P0 | Ausencia total en todos los archivos auditados | **Ausencia total de verificación de oracle_hash antes de evaluar.** Ningún componente verifica `oracle_hash` mediante `OracleSemanticIdentityCalculator.calculate()` antes de usar el oráculo como referencia de evaluación. Riesgo de evaluar contra un oráculo mutado en disco. |
| **E-4.3-003** | P0 | Ausencia total en todos los archivos auditados | **Ausencia de RegressionEvaluationStrategy.** No existe ninguna implementación de `EvaluationStrategy` orientada a regresión contra oráculo sellado. `ParserEvaluationStrategy` es la única implementación existente y está diseñada para comparación de parsers. |
| **E-4.3-004** | N/A | `core/benchmark/topology/strategies.py::ParserEvaluationStrategy` | **ParserEvaluationStrategy confirmada como evaluación de parsers.** `evaluate_run(document_id, candidate_ast, ground_truth_ast)` toma dos secuencias genéricas de `ASTNode` y las evalúa con una colección de `TopologicalEvaluatorProtocol`. No verifica `oracle_hash`, no verifica completitud, no produce veredicto de regresión. |
| **E-4.3-005** | N/A | `core/benchmark/topology/ports.py::EvaluationStrategy` | **Protocolo EvaluationStrategy confirmado.** `evaluate_run(document_id: str, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> TopologicalEvaluationReport`. El protocolo es arquitectónicamente compatible con `SealedOracle.nodes` (ambos operan sobre `Sequence[ASTNode]`). |
| **E-4.3-006** | P1 | `core/benchmark/ground_truth/ports.py::GroundTruthReaderPort` | **GroundTruthReaderPort retorna Tuple[ASTNode, ...], no SealedOracle.** El puerto de lectura retorna la secuencia de nodos cruda, no la entidad de dominio `SealedOracle`. No verifica `oracle_hash`, no verifica `ground_truth_state`, no retorna información de integridad criptográfica. |
| **E-4.3-007** | P0 | Ausencia total en todos los archivos auditados | **Ausencia de entry point de regresión.** No existe ningún CLI tool ni script que ejecute la evaluación de regresión del runtime contra el oráculo sellado. `run_benchmark.py` es para benchmark de extractores, no para regresión. |
| **E-4.3-008** | N/A | `tools/evaluation/application/benchmark_service.py::TopologyBenchmarkService` | **TopologyBenchmarkService confirmada como benchmark de extractores.** `evaluate_document(doc: BenchmarkDocument)` itera sobre `metrics: Sequence[TopologyMetric]` y evalúa `candidate` vs `ground_truth`. No verifica `oracle_hash`, no verifica completitud, no produce veredicto de regresión. |
| **E-4.3-009** | N/A | `core/benchmark/corpus/models.py::CorpusDocumentMetadata` | **CorpusDocumentMetadata confirmada con oracle_hash y ground_truth_state.** El manifiesto contiene `oracle_hash: Optional[str]` y `ground_truth_state: Optional[GroundTruthState]` por documento. Estos campos se calculan durante el sellado pero NUNCA se verifican en contexto de evaluación. |
| **E-4.3-010** | N/A | `bootstrap/topology.py::create_topology_evaluator()` | **create_topology_evaluator() confirmada como composition root topológico.** Ensambla `ZhangShashaEngine`, `LCSAnchorAlignmentStrategy`, `HeadingAnchorPartitionStrategy`, `WorstCaseOverflowStrategy`, `MaxBoundNormalizationPolicy`, `UnitCostContext`. No acepta `SealedOracle`, no verifica `oracle_hash`, no produce veredicto de regresión. |
| **E-4.3-011** | N/A | `core/benchmark/ground_truth/completeness.py::BaselineCompletenessVerifier` | **BaselineCompletenessVerifier confirmada.** `verify(manifest_doc_ids, artifact_doc_ids) -> List[str]`. Verifica biyección entre manifiesto y oráculos. Se usa durante el sellado (`SealGroundTruthUseCase`) pero NO se usa en contexto de evaluación. |
| **E-4.3-012** | N/A | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator` | **OracleSemanticIdentityCalculator confirmada.** `calculate(nodes: Tuple[ASTNode, ...]) -> str`. Calcula la identidad semántica del oráculo. Se usa durante el sellado para calcular `oracle_hash` pero NUNCA se usa para verificar la integridad del oráculo antes de evaluar. |
| **E-4.3-013** | P1 | `infra/fs/ground_truth_store.py::LocalFileSystemGroundTruthReader` | **LocalFileSystemGroundTruthReader confirmada sin verificación de integridad.** `load_ground_truth(document_id) -> Tuple[ASTNode, ...]` carga el archivo JSON mediante `read_ast_json()` y retorna la secuencia de nodos. No verifica `oracle_hash`, no verifica `ground_truth_state`, no retorna `SealedOracle`. |
| **E-4.3-014** | P2 | `tools/evaluation/topology/models.py::BenchmarkDocument` | **BenchmarkDocument confirmada como DTO de benchmark.** Contiene `candidate: Sequence[ASTNode]` y `ground_truth: Sequence[ASTNode]`. No contiene `oracle_hash`, no contiene `ground_truth_state`, no contiene información de integridad criptográfica. |
| **E-4.3-015** | N/A | `core/benchmark/ground_truth/models.py::hydrate_ground_truth()` | **Fábrica de hidratación confirmada.** `hydrate_ground_truth(document_id, nodes, state) -> GroundTruthDraft | SealedOracle`. Convierte `Tuple[ASTNode, ...]` en `SealedOracle` (si `state == SEALED`) o `GroundTruthDraft` (si `state != SEALED`). Es la función que debe usarse para cargar el `SealedOracle` desde disco en contexto de regresión. Nota: esta fábrica confía en el estado provisto por el consumidor (operación trust-based, según docstring). La verificación del estado SEALED es responsabilidad del consumidor, no de la fábrica. |
| **E-4.3-016** | P1 | `core/benchmark/ground_truth/use_cases.py::LoadGroundTruthUseCase` | **LoadGroundTruthUseCase confirmada sin verificación de integridad.** `execute(document_id) -> Tuple[ASTNode, ...]` retorna la secuencia de nodos mediante `GroundTruthReaderPort`. No verifica `oracle_hash`, no verifica `ground_truth_state`, no retorna `SealedOracle`, no usa `hydrate_ground_truth()`. Para regresión, se necesita un caso de uso diferente que retorne la entidad completa con verificación de integridad. |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-4.3-01 | `GroundTruthReaderPort.load_ground_truth()` retorna `Tuple[ASTNode, ...]` en lugar de `SealedOracle`. Esto significa que la información de identidad (`document_id`) y la entidad de dominio se pierden en la frontera de lectura. Para regresión, se necesita la entidad completa para verificar `oracle_hash` y `ground_truth_state`. | Alto | OPEN |
| OBS-4.3-02 | `OracleSemanticIdentityCalculator.calculate()` se usa durante el sellado para calcular `oracle_hash`, pero nunca se usa para verificar la integridad del oráculo antes de evaluar. Esto crea una asimetría: el hash se calcula pero nunca se verifica en contexto de evaluación. | Alto | OPEN |
| OBS-4.3-03 | `BaselineCompletenessVerifier.verify()` se usa durante el sellado para verificar la biyección manifest ↔ oráculos, pero nunca se usa en contexto de evaluación. Esto crea una asimetría: la completitud se verifica durante el sellado pero nunca se verifica antes de evaluar. | Medio | OPEN |
| OBS-4.3-04 | `TopologyBenchmarkService` opera sobre `BenchmarkDocument` que contiene `candidate` y `ground_truth` como `Sequence[ASTNode]` genéricas. No contiene información de integridad criptográfica ni de estado de ciclo de vida. Para regresión, se necesita un modelo diferente que contenga `oracle_hash` y `ground_truth_state`. | Medio | OPEN |
| OBS-4.3-05 | `create_topology_evaluator()` no acepta `SealedOracle` ni `oracle_hash`. Para regresión, se necesita un composition root diferente que acepte el oráculo sellado y verifique su integridad antes de ensamblar el pipeline de evaluación. | Medio | OPEN |
| OBS-4.3-06 | La compatibilidad arquitectónica entre `EvaluationStrategy` y `SealedOracle.nodes` es directa: ambos operan sobre `Sequence[ASTNode]`. No se requiere modificar las firmas de los evaluadores existentes para conectarlos con el oráculo sellado. La conexión es arquitectónicamente simple; lo que falta es la capa de orquestación y verificación. | Bajo | OPEN |
| OBS-4.3-07 | `hydrate_ground_truth()` es una fábrica trust-based: confía en el estado provisto por el consumidor. La verificación del estado SEALED es responsabilidad del consumidor, no de la fábrica. Para regresión, el consumidor (entry point o estrategia de regresión) debe verificar `ground_truth_state == "sealed"` antes de llamar a `hydrate_ground_truth()`. | Medio | OPEN |
| OBS-4.3-08 | Los tests de regresión actuales (golden test, snapshots de chunking) no son confiables. El golden test es tautológico (GAP-0.4-09) y los snapshots tienen auto-generación silenciosa (C5-R01) y sub-aserción de campos (C5-R02). Esto se auditará en detalle en HITO_4.4. *(Referencia: HITO_4.2 GAP-4.2-04, HITO_0.4.4_C5)* | Alto | OPEN |
| OBS-4.3-09 | El framing del `matching_key` usa `":"` como delimitador sin proteger `text_content`. Si `text_content` contiene `":"`, la clave es ambigua. Esto se auditará en detalle en HITO_4.4 o se resolverá en el ADR/NADR de Fase 4. *(Heredado de HITO_4.1 GAP-4.1-07)* | Medio | OPEN |

---

## 12. MATRIZ DE TRIAJE

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `EvaluationStrategy` (Protocol) | RETAIN | Protocolo arquitectónicamente compatible con `SealedOracle.nodes`. Reutilizable sin modificación. (E-4.3-005) |
| `TopologicalEvaluatorProtocol` | RETAIN | Protocolo de evaluador compatible con `Sequence[ASTNode]`. Reutilizable sin modificación. (E-4.3-005) |
| `TreeEditDistanceEvaluator` | RETAIN | Evaluador TED reutilizable sin modificación. (HITO 4.1 E-4.1-002) |
| `EntityRecallEvaluator` | RETAIN | Evaluador de recall reutilizable sin modificación. (HITO 4.1 E-4.1-003) |
| `OracleSemanticIdentityCalculator` | RETAIN | Servicio de dominio para calcular oracle_hash. Reutilizable para verificación de integridad. (E-4.3-012) |
| `BaselineCompletenessVerifier` | RETAIN | Servicio de dominio para verificar biyección. Reutilizable para verificación de completitud en evaluación. (E-4.3-011) |
| `SealedOracle` | RETAIN | Entidad de dominio del oráculo sellado. Reutilizable como referencia de evaluación. (E-4.3-001) |
| `hydrate_ground_truth()` | RETAIN | Fábrica de hidratación reutilizable para cargar SealedOracle desde disco. (E-4.3-015) |
| `CorpusDocumentMetadata` | RETAIN | Modelo de dominio con `oracle_hash` y `ground_truth_state`. Reutilizable para verificación de integridad. (E-4.3-009) |
| `ParserEvaluationStrategy` | RETAIN | Válida para comparación de parsers. No debe modificarse; Fase 4 crea una estrategia nueva de regresión. (E-4.3-004) |
| `TopologyBenchmarkService` | RETAIN | Válida para benchmark de extractores. No debe modificarse; Fase 4 crea un servicio nuevo de regresión. (E-4.3-008) |
| `GroundTruthReaderPort` | REFACTOR | Retorna `Tuple[ASTNode, ...]` en lugar de `SealedOracle`. Para regresión, se necesita la entidad completa con información de integridad. (E-4.3-006, OBS-4.3-01) |
| `LocalFileSystemGroundTruthReader` | REFACTOR | No verifica `oracle_hash` ni `ground_truth_state`. Para regresión, se necesita verificación de integridad. (E-4.3-013) |
| `LoadGroundTruthUseCase` | REFACTOR | No verifica `oracle_hash`, no verifica `ground_truth_state`, no retorna `SealedOracle`. Para regresión, se necesita un caso de uso diferente. (E-4.3-016) |
| `create_topology_evaluator()` | RETAIN | Composition root topológico reutilizable. Fase 4 puede crear un composition root adicional para regresión. (E-4.3-010) |
| `RegressionEvaluationStrategy` | MISSING | No existe. Debe crearse en Fase 4. (E-4.3-003) |
| `RegressionVerdict` | MISSING | No existe. Debe crearse en Fase 4. (HITO 4.2) |
| `RegressionThresholds` | MISSING | No existe. Debe crearse en Fase 4. (HITO 4.2) |
| Adaptador SealedOracle→evaluación | MISSING | No existe. Debe crearse en Fase 4. (E-4.3-001) |
| Verificación de oracle_hash antes de evaluar | MISSING | No existe. Debe crearse en Fase 4. (E-4.3-002) |
| Entry point de regresión | MISSING | No existe. Debe crearse en Fase 4. (E-4.3-007) |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Conexión SealedOracle → Evaluación

| Elemento | Estado | Evidencia |
|---|---|---|
| Adaptador SealedOracle→evaluación | FALTANTE | E-4.3-001 |
| Verificación de oracle_hash antes de evaluar | FALTANTE | E-4.3-002 |
| Verificación de completitud biyectiva en evaluación | FALTANTE | E-4.3-011, OBS-4.3-03 |
| Carga de SealedOracle desde disco (con entidad completa) | FALTANTE | E-4.3-006, E-4.3-013, E-4.3-015, E-4.3-016 |

**Veredicto del pilar:** Completamente ausente. GAP-2.0-11 heredado del HITO 2.0. Debe materializarse en Fase 4.

### Pilar 2 — Estrategia de Evaluación de Regresión

| Elemento | Estado | Evidencia |
|---|---|---|
| RegressionEvaluationStrategy | FALTANTE | E-4.3-003 |
| RegressionVerdict | FALTANTE | HITO 4.2 |
| RegressionThresholds | FALTANTE | HITO 4.2 |
| Extensión de TopologicalEvaluationReport con veredicto | FALTANTE | HITO 4.2, OBS-4.2-04 |

**Veredicto del pilar:** Completamente ausente. Debe materializarse en Fase 4.

### Pilar 3 — Entry Point de Regresión

| Elemento | Estado | Evidencia |
|---|---|---|
| CLI tool de regresión | FALTANTE | E-4.3-007 |
| Composition root de regresión | FALTANTE | OBS-4.3-05 |
| Modelo de entrada de regresión (con oracle_hash y ground_truth_state) | FALTANTE | OBS-4.3-04 |

**Veredicto del pilar:** Completamente ausente. Debe materializarse en Fase 4.

### Pilar 4 — Infraestructura Reutilizable

| Elemento | Estado | Evidencia |
|---|---|---|
| EvaluationStrategy (Protocol) | EXISTENTE | E-4.3-005 |
| TopologicalEvaluatorProtocol | EXISTENTE | E-4.3-005 |
| TreeEditDistanceEvaluator | EXISTENTE | HITO 4.1 E-4.1-002 |
| EntityRecallEvaluator | EXISTENTE | HITO 4.1 E-4.1-003 |
| OracleSemanticIdentityCalculator | EXISTENTE | E-4.3-012 |
| BaselineCompletenessVerifier | EXISTENTE | E-4.3-011 |
| SealedOracle | EXISTENTE | E-4.3-001 |
| hydrate_ground_truth() | EXISTENTE | E-4.3-015 |
| CorpusDocumentMetadata (con oracle_hash) | EXISTENTE | E-4.3-009 |

**Veredicto del pilar:** La infraestructura matemática, los evaluadores, los servicios de dominio, la fábrica de hidratación y las entidades de dominio están completos y son reutilizables sin modificación. La capa de orquestación, verificación y entry point están completamente ausentes.

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-4.3-01** | No existe conexión entre SealedOracle y la evaluación topológica. Ningún componente carga SealedOracle, verifica oracle_hash, ni lo conecta con los evaluadores. (GAP-2.0-11 heredado, GAP-4.1-01) | E-4.3-001, E-4.3-002 | Pilar 1 / HITO 2.0 GAP-2.0-11, HITO 4.1 GAP-4.1-01 | **Fase 4** | OPEN |
| **GAP-4.3-02** | No existe verificación de oracle_hash antes de evaluar. Riesgo de evaluar contra un oráculo mutado en disco. | E-4.3-002, E-4.3-012, OBS-4.3-02 | Pilar 1 / ENGINEERING_PRINCIPLES §IV (Fail-Fast) | **Fase 4** | OPEN |
| **GAP-4.3-03** | No existe RegressionEvaluationStrategy. ParserEvaluationStrategy es para comparación de parsers, no para regresión. | E-4.3-003, E-4.3-004 | Pilar 2 / ADR Maestro §3 (Dimensión REGRESIÓN) | **Fase 4** | OPEN |
| **GAP-4.3-04** | No existe entry point de regresión. No existe CLI tool para ejecutar regresión del runtime contra el oráculo sellado. | E-4.3-007 | Pilar 3 / ADR Maestro §3 (Dimensión REGRESIÓN) | **Fase 4** | OPEN |
| **GAP-4.3-05** | No existe verificación de completitud biyectiva en contexto de evaluación. BaselineCompletenessVerifier se usa durante el sellado pero no durante la evaluación. | E-4.3-011, OBS-4.3-03 | Pilar 1 / ADR Maestro §5 (Zero Partial Sealing) | **Fase 4** | OPEN |
| **GAP-4.3-06** | GroundTruthReaderPort retorna Tuple[ASTNode, ...] en lugar de SealedOracle. La información de identidad y la entidad de dominio se pierden en la frontera de lectura. | E-4.3-006, E-4.3-013, OBS-4.3-01 | Pilar 1 / NADR-F17BIS-12 §5.1 R1 (entidad de dominio) | **Fase 4** | OPEN |
| **GAP-4.3-07** | LoadGroundTruthUseCase no verifica oracle_hash, no verifica ground_truth_state, no retorna SealedOracle, no usa hydrate_ground_truth(). | E-4.3-016 | Pilar 1 / ENGINEERING_PRINCIPLES §IV (Fail-Fast) | **Fase 4** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-4.3-A | `SealedOracle.nodes` puede pasarse directamente a los evaluadores existentes sin modificar sus firmas. | CONFIRMADA | E-4.3-005, E-4.3-006 | `SealedOracle.nodes` es `Tuple[ASTNode, ...]` que es subtipo de `Sequence[ASTNode]`. Los evaluadores toman `Sequence[ASTNode]`. La conexión es directa. No se requiere modificar las firmas de los evaluadores. |
| H-4.3-B | La verificación de `oracle_hash` puede realizarse antes de la evaluación sin modificar las firmas de los evaluadores. | CONFIRMADA | E-4.3-012, OBS-4.3-02 | `OracleSemanticIdentityCalculator.calculate(oracle.nodes)` puede ejecutarse antes de llamar a los evaluadores. La verificación es una operación independiente que no requiere modificar las firmas de los evaluadores. |
| H-4.3-C | Una nueva `RegressionEvaluationStrategy` puede implementar el protocolo `EvaluationStrategy` existente sin modificar el protocolo. | CONFIRMADA (inferencia de tipos) | E-4.3-005 | El protocolo `EvaluationStrategy` tiene la firma `evaluate_run(document_id, candidate_ast, ground_truth_ast) -> TopologicalEvaluationReport`. Una nueva implementación puede cargar el `SealedOracle`, verificar `oracle_hash`, y pasar `oracle.nodes` como `ground_truth_ast`. No se requiere modificar el protocolo. Verificación empírica pendiente en implementación de Fase 4. |
| H-4.3-D | El entry point de regresión puede reutilizar `create_topology_evaluator()` para ensamblar el pipeline de evaluación. | CONFIRMADA | E-4.3-010, OBS-4.3-05 | `create_topology_evaluator()` ensambla el pipeline TED con los evaluadores existentes. El entry point de regresión puede llamar a esta función para obtener el evaluador y luego ejecutar la evaluación contra el oráculo sellado. |
| H-4.3-E | La verificación de completitud biyectiva puede reutilizar `BaselineCompletenessVerifier` en contexto de evaluación. | CONFIRMADA | E-4.3-011, OBS-4.3-03 | `BaselineCompletenessVerifier.verify(manifest_doc_ids, artifact_doc_ids)` puede ejecutarse antes de la evaluación para verificar que todos los documentos del manifiesto tienen oráculo sellado. No se requiere modificar el servicio. |
| H-4.3-F | `hydrate_ground_truth()` puede usarse para cargar el `SealedOracle` desde disco en contexto de regresión. | CONFIRMADA | E-4.3-015, OBS-4.3-07 | `hydrate_ground_truth(document_id, nodes, state)` retorna `SealedOracle` si `state == SEALED`. La fábrica es trust-based: confía en el estado provisto por el consumidor. El consumidor debe verificar `ground_truth_state == "sealed"` antes de llamar a la fábrica. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cómo se conecta actualmente el SealedOracle con la evaluación topológica?

**Estado actual verificado:**

1. No existe ningún componente que conecte `SealedOracle` con la evaluación topológica.
2. `GroundTruthReaderPort.load_ground_truth()` retorna `Tuple[ASTNode, ...]`, no `SealedOracle`.
3. `LoadGroundTruthUseCase.execute()` retorna `Tuple[ASTNode, ...]`, no `SealedOracle`, no usa `hydrate_ground_truth()`.
4. Ningún componente verifica `oracle_hash` antes de evaluar.
5. Ningún componente verifica `ground_truth_state` antes de evaluar.
6. `TopologyBenchmarkService` opera sobre `BenchmarkDocument` con `candidate` y `ground_truth` genéricos, sin información de integridad criptográfica.

**Respuesta forense:**

La conexión NO EXISTE. Este es el gap central de Fase 4 (GAP-2.0-11 heredado del HITO 2.0, confirmado en HITO 4.1 como GAP-4.1-01). Sin embargo, la conexión es arquitectónicamente simple: `SealedOracle.nodes` es `Tuple[ASTNode, ...]` que es subtipo de `Sequence[ASTNode]`, y los evaluadores toman `Sequence[ASTNode]`. La conexión directa es `evaluator.evaluate(runtime_ast, sealed_oracle.nodes)`. No se requiere modificar las firmas de los evaluadores.

Lo que SÍ debe crearse es:
- Un adaptador que cargue el `SealedOracle` desde disco y retorne la entidad completa (usando `hydrate_ground_truth()`).
- Una verificación de `oracle_hash` mediante `OracleSemanticIdentityCalculator.calculate()` antes de evaluar.
- Una verificación de completitud biyectiva mediante `BaselineCompletenessVerifier.verify()`.
- Una verificación de `ground_truth_state == "sealed"` antes de evaluar.
- Una estrategia de evaluación de regresión que orqueste el flujo completo.

**Implicación:**

Fase 4 debe crear un adaptador SealedOracle→evaluación que:
1. Cargue el `CorpusManifest` mediante `CorpusManifestReaderPort`.
2. Verifique la completitud biyectiva mediante `BaselineCompletenessVerifier`.
3. Para cada documento, cargue los nodos del oráculo mediante `GroundTruthReaderPort`.
4. Verifique `ground_truth_state == "sealed"` en el manifiesto.
5. Hidrate el `SealedOracle` mediante `hydrate_ground_truth(document_id, nodes, SEALED)`.
6. Verifique `oracle_hash` mediante `OracleSemanticIdentityCalculator.calculate(oracle.nodes) == oracle_hash`.
7. Evalúe el runtime AST contra `oracle.nodes` usando los evaluadores existentes.
8. Produzca un `RegressionVerdict`.

### 16.2 ¿Qué debe crearse para el entry point de regresión?

**Estado actual verificado:**

1. No existe ningún CLI tool para ejecutar regresión.
2. `run_benchmark.py` es para benchmark de extractores, no para regresión.
3. `create_topology_evaluator()` ensambla el pipeline TED pero no acepta `SealedOracle`.

**Respuesta forense:**

Fase 4 debe crear un entry point de regresión que:
1. Acepte como entrada el path del corpus canónico y el path del runtime AST.
2. Cargue el `CorpusManifest` y verifique la completitud biyectiva.
3. Para cada documento, cargue el `SealedOracle` y verifique `oracle_hash`.
4. Ensamble el pipeline de evaluación mediante `create_topology_evaluator()`.
5. Ejecute la evaluación de regresión mediante `RegressionEvaluationStrategy`.
6. Produzca un reporte de regresión con veredictos por documento y por corpus.
7. Retorne un exit code diferenciado (0 = PASS, 1 = WARNING, 2 = HARD_FAIL).

**Implicación:**

El entry point de regresión debe ser un CLI tool separado de `run_benchmark.py`. No debe modificarse `run_benchmark.py` para agregar funcionalidad de regresión. La separación de responsabilidades entre benchmark de extractores y regresión contra oráculo sellado debe mantenerse.

### 16.3 ¿Qué debe verificarse antes de evaluar?

**Estado actual verificado:**

1. `oracle_hash` se calcula durante el sellado pero NUNCA se verifica en contexto de evaluación.
2. `ground_truth_state` se persiste en el manifiesto pero NUNCA se verifica en contexto de evaluación.
3. `BaselineCompletenessVerifier` se usa durante el sellado pero NUNCA se usa en contexto de evaluación.
4. `hydrate_ground_truth()` es trust-based y confía en el estado provisto por el consumidor.

**Respuesta forense:**

Antes de evaluar, se deben verificar:
1. **Completitud biyectiva:** Todos los documentos del manifiesto tienen oráculo sellado. (`BaselineCompletenessVerifier.verify()`)
2. **Estado de ciclo de vida:** El `ground_truth_state` del documento es `"sealed"`. (Verificación directa del campo en el manifiesto)
3. **Integridad criptográfica:** El `oracle_hash` del manifiesto coincide con el hash calculado del oráculo. (`OracleSemanticIdentityCalculator.calculate(oracle.nodes) == oracle_hash`)
4. **Validez estructural:** El oráculo cumple las invariantes de validez. (`OracleValidityContract.validate()`)

Si cualquiera de estas verificaciones falla, la evaluación debe abortar inmediatamente (Fail-Fast, ENGINEERING_PRINCIPLES §IV). No se debe degradar silenciosamente ni evaluar contra un oráculo no verificado.

**Implicación:**

La verificación de integridad criptográfica es una operación independiente que debe ejecutarse antes de la evaluación. No se requiere modificar las firmas de los evaluadores. La verificación puede implementarse como un paso previo en la estrategia de evaluación de regresión.

### 16.4 ¿Qué componentes son reutilizables sin modificación?

**Estado actual verificado:**

1. `EvaluationStrategy` (Protocol): compatible con `SealedOracle.nodes`.
2. `TopologicalEvaluatorProtocol`: compatible con `Sequence[ASTNode]`.
3. `TreeEditDistanceEvaluator`: reutilizable sin modificación.
4. `EntityRecallEvaluator`: reutilizable sin modificación.
5. `OracleSemanticIdentityCalculator`: reutilizable para verificación de integridad.
6. `BaselineCompletenessVerifier`: reutilizable para verificación de completitud.
7. `SealedOracle`: reutilizable como referencia de evaluación.
8. `hydrate_ground_truth()`: reutilizable para cargar SealedOracle desde disco.
9. `CorpusDocumentMetadata` (con `oracle_hash` y `ground_truth_state`): reutilizable para verificación de integridad.
10. `create_topology_evaluator()`: reutilizable para ensamblar el pipeline de evaluación.

**Respuesta forense:**

La infraestructura matemática, los evaluadores, los servicios de dominio, la fábrica de hidratación y las entidades de dominio están completos y son reutilizables sin modificación. La capa de orquestación, verificación y entry point están completamente ausentes y deben crearse en Fase 4.

**Implicación:**

Fase 4 no necesita reescribir el motor matemático ni los evaluadores. Debe crear la capa de orquestación de regresión, la verificación de integridad criptográfica, y el entry point de ejecución. La infraestructura existente es reutilizable sin modificación.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-06** | Taxonomía de Criticidad de Nodos | HITO 4.2 GAP-4.2-01 | Ausente. No existe ningún enum, política o contrato de criticidad. | **Fase 4** |
| **DC-07** | Reglas de Regresión Topológica | HITO 4.2 GAP-4.2-02 | Ausente. No existe ningún mecanismo de veredicto. | **Fase 4** |
| **GAP-2.0-11** | Adaptador baseline→benchmark | E-4.3-001, E-4.3-002, GAP-4.3-01 | Ausente. No existe conexión SealedOracle→evaluación. | **Fase 4** |

**Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos. DC-06 y DC-07 fueron resueltos normativamente en el ADR Maestro §8, pero no tienen materialización operativa. GAP-2.0-11 fue identificado en el HITO 2.0 y confirmado en HITO 4.1 y HITO 4.3 como el gap central de Fase 4.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Evaluación contra oráculo mutado | Si el oráculo es mutado en disco y no se verifica oracle_hash antes de evaluar, la evaluación produce resultados falsos. | Alto | E-4.3-002, OBS-4.3-02 |
| Evaluación contra oráculo no sellado | Si el ground_truth_state no es "sealed" y no se verifica antes de evaluar, la evaluación se ejecuta contra un borrador no validado. | Alto | E-4.3-009, OBS-4.3-01 |
| Evaluación con baseline incompleta | Si la completitud biyectiva no se verifica antes de evaluar, la evaluación se ejecuta contra una baseline incompleta. | Medio | E-4.3-011, OBS-4.3-03 |
| Confusión entre benchmark y regresión | Si el entry point de regresión se implementa como extensión de run_benchmark.py, se confunden las responsabilidades de benchmark de extractores y regresión contra oráculo sellado. | Medio | E-4.3-007, E-4.3-008 |
| Pérdida de información de identidad en la frontera de lectura | Si GroundTruthReaderPort retorna Tuple[ASTNode, ...] en lugar de SealedOracle, la información de identidad y la entidad de dominio se pierden en la frontera de lectura. | Medio | E-4.3-006, OBS-4.3-01 |
| Fábrica trust-based sin verificación del consumidor | hydrate_ground_truth() confía en el estado provisto por el consumidor. Si el consumidor no verifica ground_truth_state antes de llamar a la fábrica, puede hidratar un GroundTruthDraft como si fuera SealedOracle. | Medio | E-4.3-015, OBS-4.3-07 |
| Tests de regresión no confiables | Los tests de regresión actuales (golden test tautológico, snapshots con auto-generación) no son confiables. Deben ser remediados antes de que la regresión graduada pueda ser efectiva. | Alto | OBS-4.3-08, HITO_4.2 GAP-4.2-04 |
| Framing del matching_key sin protección | El framing del matching_key usa ":" como delimitador sin proteger text_content. Riesgo de ambigüedad en el alineamiento LCS. | Medio | OBS-4.3-09, HITO_4.1 GAP-4.1-07 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR o NADR posterior deberá responder:

1. ¿El adaptador SealedOracle→evaluación debe ser un nuevo puerto hexagonal o una extensión del puerto existente `GroundTruthReaderPort`?
2. ¿La verificación de `oracle_hash` debe ser obligatoria antes de toda evaluación, o debe ser configurable?
3. ¿La verificación de completitud biyectiva debe ejecutarse antes de cada evaluación, o solo una vez por corpus?
4. ¿El entry point de regresión debe ser un CLI tool separado de `run_benchmark.py`, o debe ser una extensión del entry point existente?
5. ¿El `RegressionEvaluationStrategy` debe implementar el protocolo `EvaluationStrategy` existente, o debe definir un protocolo nuevo?
6. ¿El modelo de entrada de regresión debe contener `oracle_hash` y `ground_truth_state`, o debe cargarlos dinámicamente desde el manifiesto?
7. ¿La verificación de `ground_truth_state == "sealed"` debe ser obligatoria antes de toda evaluación, o debe ser configurable?
8. ¿El exit code del entry point de regresión debe ser diferenciado (0 = PASS, 1 = WARNING, 2 = HARD_FAIL), o debe ser binario (0 = PASS, 1 = FAIL)?
9. ¿Cómo se protege el framing del matching_key contra ambigüedad cuando text_content contiene ":"? *(Heredada de HITO_4.1 GAP-4.1-07. Incluida aquí para trazabilidad.)*
10. ¿`hydrate_ground_truth()` debe modificarse para verificar el estado antes de hidratar, o la verificación debe ser responsabilidad del consumidor?

---

## 21. CIERRE DEL HITO 4.3

Este HITO confirma que no existe ningún componente que conecte el `SealedOracle` con la evaluación topológica, verifique su integridad criptográfica antes de evaluar, ni produzca un veredicto de regresión. El protocolo `EvaluationStrategy` es arquitectónicamente compatible con `SealedOracle.nodes`, pero la capa de orquestación, verificación y entry point están completamente ausentes. GAP-2.0-11 heredado del HITO 2.0 se confirma como el gap central de Fase 4.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados. Todas las evidencias tienen ID estable y severidad. Todos los gaps tienen evidencia vinculada y fase destino. Todas las hipótesis están cerradas como CONFIRMADA, RESUELTA, RECHAZADA o TO BE VERIFIED. Cero hipótesis abiertas sin destino. Las 4 correcciones de forma han sido aplicadas. Referencias a tests de regresión y framing del matching_key incluidas.
**Verificación de cadena de gobernanza:** ADR_F17_BIS_MASTER → HITO_2.0 (GAP-2.0-11) → HITO_4.1 (GAP-4.1-01) → HITO_4.2 (GAP-4.2-05) → HITO_4.3 (este documento). Cadena completa verificada.
**Contradicciones con HITOs previos:** Ninguna. Todos los hallazgos son consistentes con los HITOs previos. GAP-2.0-11 heredado del HITO 2.0 se confirma como persistente y se consolida como GAP-4.3-01.
**Decision Candidates generados:** Ninguno nuevo. GAP-2.0-11 ya existe en el HITO 2.0. Este HITO confirma su ausencia operativa y consolida la evidencia forense para Fase 4.
**Siguiente paso recomendado:** Construir HITO_4.4 (Testing Prerequisites Discovery) usando este HITO como insumo, para auditar el estado actual de los tests de regresión y determinar qué debe remediarse antes de que la regresión graduada pueda ser efectiva. Luego construir ADR_F17-BIS_04 (Scientific Verification) y los NADRs de Fase 4.