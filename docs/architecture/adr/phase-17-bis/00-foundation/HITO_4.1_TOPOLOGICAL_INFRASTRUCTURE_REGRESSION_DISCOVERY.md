# HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY.md

**Estado:** IN_PROGRESS v1.0.0
**Fecha de emisión:** 2026-08-30
**Fecha de congelamiento:** N/A
**Fase:** 17-BIS — Fase 4 (Scientific Verification)
**Tipo de artefacto:** Forensic Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT (FROZEN), HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT (FROZEN), HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT (FROZEN), HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY (FROZEN v2.1.0), FASE_3_HANDOFF (FROZEN v1.0.0), METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0-FROZEN, módulos auditados en core/benchmark/topology/, bootstrap/topology.py, tools/evaluation/topology/, tests/unit/test_zhang_shasha.py, tests/unit/test_structural_metric.py.
**Mandato:** Auditar el estado actual de la infraestructura topológica post-Fases 1-3 para determinar qué componentes son reutilizables para Scientific Verification, qué componentes requieren extensión, y qué gaps bloquean la conexión runtime vs oráculo sellado.
**Síntesis:** La infraestructura matemática y de evaluación topológica es SOTA y reutilizable como componentes. La capa de orquestación requiere una nueva estrategia de evaluación orientada a regresión. La conexión con el oráculo sellado, la taxonomía de criticidad y las reglas de regresión graduada están ausentes.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-08-30 | Emisión inicial. Auditoría forense completa de la infraestructura topológica post-Fases 1-3. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la totalidad de la infraestructura topológica del repositorio: core/benchmark/topology/ (17 archivos), bootstrap/topology.py (composition root), tools/evaluation/topology/ (11 archivos), tools/evaluation/application/benchmark_service.py, y las suites de pruebas asociadas (tests/unit/test_zhang_shasha.py con 17 tests, tests/unit/test_structural_metric.py con 8 tests). Se verificaron los contratos de puertos, la pureza matemática del motor Zhang-Shasha, los evaluadores de dominio, las estrategias de alineamiento y particionado, las políticas de normalización y overflow, y la dualidad entre la rama nativa (core/) y la rama APTED (tools/).

**Hallazgo central:**

> La infraestructura matemática y de evaluación topológica es SOTA y reutilizable como componentes puros. Sin embargo, la capa de orquestación está diseñada para comparación de parsers (parser vs parser), no para regresión contra oráculo sellado (runtime vs SealedOracle). La conexión con el oráculo sellado, la taxonomía de criticidad y las reglas de regresión graduada están completamente ausentes.

**Defectos dominantes confirmados:**

1. **Ausencia de conexión SealedOracle → evaluación topológica (E-4.1-009, E-4.1-021):** Ningún componente de la infraestructura topológica consume SealedOracle ni verifica oracle_hash antes de evaluar. El GAP-2.0-11 heredado del HITO 2.0 permanece abierto.
2. **Ausencia de taxonomía de criticidad (E-4.1-010):** No existe ningún enum, política o contrato que mapee ContentNodeType a niveles de criticidad (CRITICAL, WARNING, INFO). DC-06 permanece sin materialización operativa.
3. **Ausencia de reglas de regresión graduada (E-4.1-011):** No existe ningún mecanismo de veredicto (PASS, WARNING, HARD_FAIL). DC-07 permanece sin materialización operativa.
4. **Framing del matching_key sin protección contra ambigüedad (E-4.1-022):** El matching_key usa ":" como delimitador sin proteger text_content, generando riesgo de ambigüedad en el alineamiento LCS.

**Veredicto:** La infraestructura topológica está lista para ser consumida por Fase 4 como componentes puros. La fase debe crear la capa de orquestación de regresión, la conexión con el oráculo sellado, la taxonomía de criticidad y las reglas de veredicto graduado. No se requiere reescribir el motor matemático ni los evaluadores existentes.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Este HITO no audita el pipeline de producción (core/pipeline/, apps/llm_workers/, apps/compiler/). Esa superficie fue auditada en los HITOs 0.4.5-P1 a P7 y en el HITO 0.4.4-D/E. Este HITO se limita exclusivamente a la infraestructura de evaluación topológica y su conexión (o ausencia de conexión) con la baseline sellada.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR_F17_BIS_MASTER, NADR-F17BIS-10, NADR-F17BIS-16, NADR-F17BIS-17.
2. Cargar HITOs previos aplicables: HITO_0.4.1, HITO_0.4.4_C1, HITO_0.4.4_C5, HITO_2.0.
3. Inspeccionar código fuente de todos los módulos del alcance.
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs E-4.1-NNN.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar TO BE VERIFIED cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| core/benchmark/topology/models.py | MatchingKey, RecallDiagnostics, NormalizationDiagnostics, NormalizationInput, NormalizationResult, TedDiagnostics, MetricScoreDTO, TopologicalEvaluationReport, ConfusionMatrix, AnchorCorrespondence, AlignmentResult, EvaluationForest, TEDEvaluationContext, EvaluationWindow, PostorderIndex | 100% auditado |
| core/benchmark/topology/ports.py | NodeCorrespondencePolicy, ContentSimilarityPolicy, EditCostPolicy, NodeMatchingPolicy, AnchorAlignmentStrategy, AnchorPartitionStrategy, TreeEditCostContext, TreeDistanceAlgorithm, TreeEditEngine, OverflowStrategy, NormalizationPolicy, TopologicalEvaluatorProtocol, ScoreAggregationPolicy, EvaluationStrategy, AnchorSequenceAlignmentEngine | 100% auditado |
| core/benchmark/topology/strategies.py | ParserEvaluationStrategy | 100% auditado |
| core/benchmark/topology/evaluators/ted.py | TreeEditDistanceEvaluator | 100% auditado |
| core/benchmark/topology/evaluators/recall.py | EntityRecallEvaluator | 100% auditado |
| core/benchmark/topology/engines/zhang_shasha/engine.py | ZhangShashaEngine | 100% auditado |
| core/benchmark/topology/engines/zhang_shasha/forest.py | ForestDistanceCalculator | 100% auditado |
| core/benchmark/topology/engines/zhang_shasha/indexer.py | PostorderIndexer, IndexConsistencyError, VIRTUAL_ROOT_ID | 100% auditado |
| core/benchmark/topology/engines/zhang_shasha/matrix.py | TreeDistanceTable | 100% auditado |
| core/benchmark/topology/engines/zhang_shasha/tree.py | ZhangShashaTreeDistanceCalculator | 100% auditado |
| core/benchmark/topology/engines/lcs_engine.py | LCSSequenceAlignmentEngine, PreferCandidateTieBreaker | 100% auditado |
| core/benchmark/topology/alignment/strategy.py | LCSAnchorAlignmentStrategy | 100% auditado |
| core/benchmark/topology/alignment/keys.py | AnchorExtractor, MatchingKeyMapper, IndexedAnchor | 100% auditado |
| core/benchmark/topology/alignment/mapper.py | AlignmentProjector | 100% auditado |
| core/benchmark/topology/alignment/metrics.py | AlignmentQualityPolicy | 100% auditado |
| core/benchmark/topology/alignment/tie_break.py | LCSTieBreakStrategy, PreferCandidateTieBreaker | 100% auditado |
| core/benchmark/topology/partitioning/heading.py | HeadingAnchorPartitionStrategy, PartitionBoundary | 100% auditado |
| core/benchmark/topology/policies/normalization.py | MaxBoundNormalizationPolicy | 100% auditado |
| core/benchmark/topology/policies/overflow.py | WorstCaseOverflowStrategy | 100% auditado |
| core/benchmark/topology/costs/unit.py | UnitCostContext | 100% auditado |
| bootstrap/topology.py | DefaultNodeMatchingPolicy, create_topology_evaluator | 100% auditado |
| tools/evaluation/topology/metrics/structural.py | StructuralTopologyMetric, CostMatrix, CustomAPTEDConfig | 100% auditado |
| tools/evaluation/topology/fingerprint.py | ASTFingerprintPolicy | 100% auditado |
| tools/evaluation/topology/models.py | MetricName, BenchmarkDocument, ConfusionMatrix, MetricResult, DocumentEvaluationResult, BenchmarkSummaryReport | 100% auditado |
| tools/evaluation/topology/ports.py | TopologyMetric, BenchmarkAggregationStrategy | 100% auditado |
| tools/evaluation/topology/strategies.py | DefaultBenchmarkAggregationStrategy | 100% auditado |
| tools/evaluation/topology/metrics/__init__.py | MetricRegistry, default_metrics, UnknownMetricProfileError | 100% auditado |
| tools/evaluation/application/benchmark_service.py | TopologyBenchmarkService | 100% auditado |
| tests/unit/test_zhang_shasha.py | 17 tests del motor Zhang-Shasha | 100% auditado |
| tests/unit/test_structural_metric.py | 8 tests de StructuralTopologyMetric | 100% auditado |
| core/benchmark/ground_truth/identity.py | OracleSemanticIdentityCalculator | Referenciado (auditado en HITO 3.1, Fase 3) |
| core/benchmark/ground_truth/models.py | SealedOracle, GroundTruthDraft | Referenciado (auditado en HITO 2.0, Fase 2) |
| core/benchmark/corpus/services.py | ManifestFingerprintCalculator | Referenciado (auditado en HITO 3.2, Fase 3) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md | Fuente normativa: dimensiones de identidad, invariantes, hoja de ruta |
| NADR | NADR-F17BIS-10 (Regression Gates & CI Automation) | Reglas normativas de regresión y CI |
| NADR | NADR-F17BIS-16 (Cryptographic Identity Semantics) | Diferenciación de contratos de hashing |
| NADR | NADR-F17BIS-17 (Identity Encoding Integrity) | Contratos de dominio para framing |
| HITO previo | HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT.md | Evidencia forense heredada: OBS-0.4.1-01 a OBS-0.4.1-04 |
| HITO previo | HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT.md | Evidencia forense heredada: estado del subsistema topológico |
| HITO previo | HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT.md | Contexto: estado de tests de regresión y CI (tautología en golden test, ausencia de CI workflow) |
| HITO previo | HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY.md | Evidencia forense heredada: GAP-2.0-11, ontología del oráculo |
| Handoff | FASE_3_HANDOFF.md | Estado de Fase 3, carry-forward obligatorio |
| Código | core/benchmark/topology/* (17 archivos) | Observación runtime/código |
| Código | bootstrap/topology.py | Observación runtime/código |
| Código | tools/evaluation/topology/* (11 archivos) | Observación runtime/código |
| Código | tools/evaluation/application/benchmark_service.py | Observación runtime/código |
| Test | tests/unit/test_zhang_shasha.py | Verificación comportamental |
| Test | tests/unit/test_structural_metric.py | Verificación comportamental |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 | Estructura canónica del HITO |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Pipeline TED actual (evaluación topológica)

```text
FLUJO A -- Pipeline TED actual (parser vs parser)

  create_topology_evaluator() [bootstrap/topology.py]
    -> ZhangShashaEngine(indexer, algorithm) [OK]
    -> LCSSequenceAlignmentEngine(PreferCandidateTieBreaker) [OK]
    -> LCSAnchorAlignmentStrategy(matching_policy, alignment_engine) [OK]
    -> HeadingAnchorPartitionStrategy() [OK]
    -> WorstCaseOverflowStrategy() [OK]
    -> MaxBoundNormalizationPolicy() [OK]
    -> UnitCostContext() [GAP: sin criticidad]
    -> TreeEditDistanceEvaluator(aligner, partitioner, engine, overflow, normalizer, costs) [OK]
    -> MetricScoreDTO [OK]

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado
```

### FLUJO B — Pipeline de Recall actual (evaluación por tipo)

```text
FLUJO B -- Pipeline de Recall actual

  EntityRecallEvaluator(target_type, matching_policy) [OK]
    -> Filtrado selectivo O(n) [OK]
    -> Indexacion por MatchingKey [GAP: sin normalizacion]
    -> Consumo de buckets [OK]
    -> ConfusionMatrix(TP, FP, FN) [OK]
    -> MetricScoreDTO(f1_score) [OK]

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado (OBS-0.4.1-01 heredado)
```

### FLUJO C — Conexión con oráculo sellado (AUSENTE)

```text
FLUJO C -- Conexion con oraculo sellado (AUSENTE)

  SealedOracle [Existe en core/benchmark/ground_truth/models.py]
    -> ??? [GAP: ningun componente consume SealedOracle]
    -> oracle_hash verification [GAP: no se verifica antes de evaluar]
    -> TopologicalEvaluatorProtocol.evaluate(candidate, ground_truth) [GAP: toma Sequence[ASTNode], no SealedOracle]
    -> RegressionVerdict [GAP: no existe]

Leyenda:
  [GAP] gap confirmado. Este flujo NO EXISTE actualmente.
```

### FLUJO D — Dualidad core/ vs tools/ (OBS-0.4.1-04)

```text
FLUJO D -- Dualidad core/ vs tools/

  Rama nativa (core/benchmark/topology/):
    ZhangShashaEngine [Python puro, O(M^2 N^2) amortiguado]
    -> Particionado escalable via LCS
    -> Costos flexibles via TreeEditCostContext
    -> Raiz virtual con costo 0.0

  Rama APTED (tools/evaluation/topology/metrics/structural.py):
    StructuralTopologyMetric [APTED, O(M^3 N)]
    -> Sin particionado (arbol completo)
    -> Costos fijos via CostMatrix
    -> Raiz artificial ("Document", "root")

  [GAP: OBS-0.4.1-04. Dualidad sin resolucion.]
```

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| Motor Zhang-Shasha | ZhangShashaEngine, ForestDistanceCalculator, ZhangShashaTreeDistanceCalculator | Sí (TreeEditEngine, TreeDistanceAlgorithm) | Motor matemático puro de Tree Edit Distance | CONFIRMADO |
| Indexador post-orden | PostorderIndexer, PostorderIndex | Sí (TreeEditCostContext) | Indexación O(N) con validación de sibling order y raíz virtual | CONFIRMADO |
| Evaluador TED | TreeEditDistanceEvaluator | Sí (TopologicalEvaluatorProtocol) | Application Service: Alignment → Partition → Engine → Normalize | CONFIRMADO |
| Evaluador Recall | EntityRecallEvaluator | Sí (TopologicalEvaluatorProtocol) | Recall por tipo de nodo con ConfusionMatrix | CONFIRMADO |
| Estrategia de alineamiento | LCSAnchorAlignmentStrategy | Sí (AnchorAlignmentStrategy) | Alineamiento LCS de anchors con matching policy inyectada | CONFIRMADO |
| Estrategia de particionado | HeadingAnchorPartitionStrategy | Sí (AnchorPartitionStrategy) | Particionado por headings en O(n) con intervalos semiabiertos | CONFIRMADO |
| Política de normalización | MaxBoundNormalizationPolicy | Sí (NormalizationPolicy) | Normalización acotada [0,1] con invariante geométrica | CONFIRMADO |
| Política de overflow | WorstCaseOverflowStrategy | Sí (OverflowStrategy) | Fallback lineal O(N) ante desbordamiento de ventanas | CONFIRMADO |
| Contexto de costos | UnitCostContext | Sí (TreeEditCostContext) | Costos unitarios simétricos (1.0) sin criticidad | CONFIRMADO (con gap) |
| Matching policy | DefaultNodeMatchingPolicy | Sí (NodeMatchingPolicy) | Igualdad textual directa sin normalización | CONFIRMADO (con gap) |
| Estrategia de evaluación | ParserEvaluationStrategy | Sí (EvaluationStrategy) | Orquestador de evaluadores para comparación de parsers | CONFIRMADO (con gap) |
| Métrica APTED | StructuralTopologyMetric | No (TopologyMetric en tools/) | TED vía APTED con costos fijos | CONFIRMADO (dualidad) |
| Fingerprint policy | ASTFingerprintPolicy | No (herramienta) | Fingerprint semántico e identitario de nodos | CONFIRMADO |
| Servicio de benchmark | TopologyBenchmarkService | No (herramienta) | Servicio de aplicación para evaluación de corpus | CONFIRMADO |
| Conexión SealedOracle | No existe | No | No existe ningún componente que consuma SealedOracle | MISSING |
| Taxonomía de criticidad | No existe | No | No existe mapeo ContentNodeType → CRITICAL/WARNING/INFO | MISSING |
| Reglas de regresión | No existe | No | No existe mecanismo de veredicto PASS/WARNING/HARD_FAIL | MISSING |
| RegressionEvaluationStrategy | No existe | No | No existe estrategia de evaluación runtime vs oráculo | MISSING |
| RegressionVerdict | No existe | No | No existe modelo de veredicto de regresión | MISSING |
| CriticalityAwareCostContext | No existe | No | No existe extensión de TreeEditCostContext con criticidad | MISSING |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision/Recomendación previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Motor Zhang-Shasha | Motor completo, puro, con tests rigurosos (17 tests) | Motor matemático determinista para TED | HITO 0.4.1 recomienda: consolidar sobre rama nativa | COMPLIANT | E-4.1-001, E-4.1-017 |
| Evaluador TED | Application Service puro, pipeline modular | Evaluador de topología con normalización [0,1] | HITO 0.4.1: componente SOTA | COMPLIANT | E-4.1-002, E-4.1-004 |
| Evaluador Recall | Recall por tipo con ConfusionMatrix | Recall semántico por categoría | HITO 0.4.1: componente SOTA | COMPLIANT | E-4.1-003 |
| Costos de edición | UnitCostContext: costos uniformes 1.0 | Costos ponderados por criticidad (DC-06) | ADR Maestro §8 DC-06: pendiente | DISCREPANCY | E-4.1-005, E-4.1-010 |
| Matching policy | Igualdad textual directa sin normalización | Matching robusto ante variaciones triviales | HITO 0.4.1 OBS-0.4.1-01: pendiente | DISCREPANCY | E-4.1-006 |
| Estrategia de evaluación | ParserEvaluationStrategy: parser vs parser | Regresión: runtime vs oráculo sellado | HITO 2.0 GAP-2.0-11: pendiente | DISCREPANCY | E-4.1-007, E-4.1-009 |
| Conexión SealedOracle | No existe | Consumo de SealedOracle con verificación de oracle_hash | HITO 2.0 GAP-2.0-11: pendiente | DISCREPANCY | E-4.1-009, E-4.1-021 |
| Criticidad | No existe | Taxonomía CRITICAL/WARNING/INFO mapeada a ContentNodeType | ADR Maestro §8 DC-06: pendiente | DISCREPANCY | E-4.1-010 |
| Regresión graduada | No existe | Veredicto PASS/WARNING/HARD_FAIL | ADR Maestro §8 DC-07: pendiente | DISCREPANCY | E-4.1-011 |
| Dualidad core/ vs tools/ | Dos motores TED coexisten | Consolidación sobre rama nativa | HITO 0.4.1 OBS-0.4.1-04: pendiente | DISCREPANCY | E-4.1-008 |
| Framing del matching_key | ":" como delimitador sin proteger text_content | Delimitador protegido o normalización | No existe decisión previa | DISCREPANCY | E-4.1-022 |
| Contratos de dominio | DocumentId, NodeId, GroundTruthState en core/shared/identity_contracts.py | Contratos de dominio para framing criptográfico | Fase 3 (Wave 2.1, 2.2, 2.4): implementado | COMPLIANT | FASE_3_HANDOFF |
| Identidad semántica | OracleSemanticIdentityCalculator (contrato canónico) | Identidad semántica del oráculo | Fase 3: implementado | COMPLIANT | FASE_3_HANDOFF |
| Suite Zhang-Shasha | 17 tests: vacíos, isomorfismo, simetría, multi-raíz, escalabilidad | Suite rigurosa del motor matemático | HITO 0.4.4_C1: componente SOTA | COMPLIANT | E-4.1-017 |
| Suite StructuralTopologyMetric | 8 tests: determinismo, aplanamiento, reordenamiento | Suite de la métrica APTED | HITO 0.4.4_C1: componente válido | COMPLIANT | E-4.1-018 |
| Tests de regresión y CI | Tautología en golden test, ausencia de CI workflow | Tests de regresión funcionales y CI activo | HITO 0.4.4_C5 GAP-0.4-09, C5-R01 a C5-R10: pendiente | DISCREPANCY | HITO 0.4.4_C5 |

---

## 8. MUTATION SEMANTICS MATRIX

| Mutación | NSS cambia? | Recall cambia? | Criticidad afecta? | Veredicto cambia? | Observed behavior | Required behavior | Evidencia | Gap |
|---|---|---|---|---|---|---|---|---|
| Pérdida de nodo DISPLAY_EQUATION | Sí | Sí | A DECIDIR (DC-06) | A DECIDIR (DC-07) | NSS baja; recall de ecuaciones baja; sin veredicto | NSS ponderado por criticidad; recall afectado; HARD_FAIL si CRITICAL | E-4.1-005, E-4.1-010, E-4.1-011 | GAP-4.1-02, GAP-4.1-03 |
| Pérdida de nodo PARAGRAPH | Sí | Sí | A DECIDIR (DC-06) | A DECIDIR (DC-07) | NSS baja; recall de párrafos baja; sin veredicto | NSS ponderado; recall afectado; WARNING si WARNING | E-4.1-005, E-4.1-010, E-4.1-011 | GAP-4.1-02, GAP-4.1-03 |
| Pérdida de nodo HEADING | Sí | No (no es target de recall) | A DECIDIR (DC-06) | A DECIDIR (DC-07) | NSS baja; sin veredicto | NSS ponderado; WARNING; desalineación de particionado | E-4.1-005, E-4.1-010, E-4.1-011 | GAP-4.1-02, GAP-4.1-03 |
| Cambio de contenido en nodo | Sí | Sí (si cambia matching key) | No | A DECIDIR (DC-07) | NSS baja; recall puede bajar; sin veredicto | NSS afectado; recall afectado; veredicto según umbral | E-4.1-005, E-4.1-011 | GAP-4.1-03 |
| Cambio de orden de nodos | Sí | No | No | A DECIDIR (DC-07) | NSS baja; sin veredicto | NSS afectado; veredicto según umbral | E-4.1-005, E-4.1-011 | GAP-4.1-03 |
| Aplanamiento jerárquico | Sí | No | No | A DECIDIR (DC-07) | NSS baja significativamente; sin veredicto | NSS afectado; veredicto según umbral | E-4.1-005, E-4.1-011 | GAP-4.1-03 |
| Espacio sobrante en texto | Sí (matching falla) | Sí (matching falla) | No | A DECIDIR | Matching falla por igualdad textual directa | Matching robusto con normalización | E-4.1-006 | GAP-4.1-04 |
| Cambio de node_id | Sí (oracle_hash cambia) | No | No | No | oracle_hash cambia; NSS no cambia (compute_ast_hash excluye node_id) | Correcto: compute_ast_hash para comparación, oracle_hash para identidad | FASE_3_HANDOFF | None |
| text_content con ":" en matching_key | Ambigüedad en LCS | Sí (falso negativo) | No | A DECIDIR | matching_key genera clave ambigua | Delimitador protegido o normalización | E-4.1-022 | GAP-4.1-07 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Para evidencia positiva (componentes SOTA confirmados), se usa N/A.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-4.1-001** | N/A | core/benchmark/topology/engines/zhang_shasha/engine.py::ZhangShashaEngine | **Motor Zhang-Shasha completo y funcional.** Adaptador de orquestación puro acoplado a contratos perimetrales (Ports). Se limita a indexar las colecciones y delegar la DP al algoritmo inyectado. |
| **E-4.1-002** | N/A | core/benchmark/topology/evaluators/ted.py::TreeEditDistanceEvaluator | **Evaluador TED como Application Service puro.** Coordina alineamiento, particionado, motor inyectado y normalización. No contiene lógica del algoritmo Zhang-Shasha ni manejo de matrices DP. |
| **E-4.1-003** | N/A | core/benchmark/topology/evaluators/recall.py::EntityRecallEvaluator | **Evaluador Recall con complejidad O(n).** Micro-juez de recuperación estructural. Filtrado selectivo, indexación por MatchingKey, consumo de buckets con protección de complejidad lineal. |
| **E-4.1-004** | N/A | core/benchmark/topology/evaluators/ted.py::TreeEditDistanceEvaluator.evaluate | **Pipeline TED modular.** Flujo unidireccional: Alignment (LCS) → Partition (Windows) → Engine (DP/Zhang-Shasha) → Normalization. Cada etapa acoplada a protocolo/puerto específico. |
| **E-4.1-005** | P1 | core/benchmark/topology/costs/unit.py::UnitCostContext | **Costos unitarios sin criticidad.** deletion_cost = 1.0, insertion_cost = 1.0, substitution_cost = 1.0 si difiere texto o tipo. No existe ponderación por ContentNodeType. |
| **E-4.1-006** | P1 | bootstrap/topology.py::DefaultNodeMatchingPolicy.match | **Matching con igualdad textual directa.** match() compara candidate.node_type == ground_truth.node_type and candidate.text_content == ground_truth.text_content. Sin stripping, sin normalización Unicode, sin lowercasing. |
| **E-4.1-007** | P1 | core/benchmark/topology/strategies.py::ParserEvaluationStrategy.evaluate_run | **Estrategia de evaluación para comparación de parsers.** evaluate_run(document_id, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]). Toma secuencias genéricas de ASTNode, no SealedOracle. |
| **E-4.1-008** | P1 | tools/evaluation/topology/metrics/structural.py::StructuralTopologyMetric | **Dualidad core/ vs tools/ (OBS-0.4.1-04 heredado).** StructuralTopologyMetric usa APTED con costos fijos (CostMatrix: delete=1.0, insert=1.0, rename_same_type=0.5, rename_diff_type=2.0). Sin particionado. Raíz artificial ("Document", "root"). |
| **E-4.1-009** | P0 | Ausencia total en todos los archivos auditados | **No existe conexión SealedOracle → evaluación topológica.** Ningún componente de core/benchmark/topology/ ni de tools/evaluation/topology/ consume SealedOracle ni verifica oracle_hash antes de evaluar. |
| **E-4.1-010** | P0 | Ausencia total en todos los archivos auditados | **No existe taxonomía de criticidad.** No existe ningún enum, política o contrato que mapee ContentNodeType a niveles de criticidad (CRITICAL, WARNING, INFO). DC-06 sin materialización operativa. |
| **E-4.1-011** | P0 | Ausencia total en todos los archivos auditados | **No existen reglas de regresión graduada.** No existe ningún mecanismo de veredicto (PASS, WARNING, HARD_FAIL). No existe RegressionVerdict ni ningún modelo de veredicto. DC-07 sin materialización operativa. |
| **E-4.1-012** | N/A | core/benchmark/topology/alignment/strategy.py::LCSAnchorAlignmentStrategy | **Alineamiento LCS con anchor_type configurable.** Constructor acepta matching_policy, alignment_engine y anchor_type (default: ContentNodeType.HEADING). Desacoplado mediante inversión de control. |
| **E-4.1-013** | N/A | core/benchmark/topology/partitioning/heading.py::HeadingAnchorPartitionStrategy | **Particionado por headings en O(n).** Segmentador topológico puro basado en intervalos secuenciales semiabiertos. Garantiza partición exhaustiva del AST en una única pasada lineal. |
| **E-4.1-014** | N/A | core/benchmark/topology/policies/normalization.py::MaxBoundNormalizationPolicy | **Normalización con invariante geométrica.** Escala de demeritación acotada estrictamente a [0.0, 1.0]. Valida que accumulated_distance no supere worst_case_bound. |
| **E-4.1-015** | N/A | core/benchmark/topology/policies/overflow.py::WorstCaseOverflowStrategy | **Fallback lineal ante overflow.** Penalización lineal O(N) ante desbordamientos de ventanas. Suma iterativa de costos atómicos del puerto. |
| **E-4.1-016** | N/A | core/benchmark/topology/engines/zhang_shasha/indexer.py::PostorderIndexer | **Indexador con validación estricta.** Construye vectores paralelos en O(N). Valida invariante de sibling order. Sintetiza raíz virtual neutra (VIRTUAL_ROOT_ID) para bosques multi-raíz con costo 0.0. |
| **E-4.1-017** | N/A | tests/unit/test_zhang_shasha.py | **Suite Zhang-Shasha rigurosa (17 tests).** Cubre: árboles vacíos, nodos individuales, identidad, inserción/borrado/sustitución atómica, isomorfismo, simetría, violaciones de orden, multi-raíz, profundidad, anchura, escalabilidad hasta 150 nodos. |
| **E-4.1-018** | N/A | tests/unit/test_structural_metric.py | **Suite StructuralTopologyMetric (8 tests).** Cubre: determinismo, árboles idénticos, árboles vacíos, isomorfismo por ID, aplanamiento jerárquico, reordenamiento de hijos, rename mismo/diferente tipo. |
| **E-4.1-019** | N/A | tools/evaluation/topology/fingerprint.py::ASTFingerprintPolicy | **Fingerprint ortogonal a compute_ast_hash.** semantic_fingerprint() retorna tupla (node_type, content) para matching nodo-a-nodo. identity_fingerprint() incluye node_id. No son redundantes (HITO 2.0 E-2.0-16). |
| **E-4.1-020** | N/A | tools/evaluation/application/benchmark_service.py::TopologyBenchmarkService | **Servicio de aplicación puro.** Opera exclusivamente en memoria sobre objetos DTO BenchmarkDocument. No realiza I/O. Evalúa documento individual y corpus completo. |
| **E-4.1-021** | P0 | Ausencia total en todos los archivos auditados | **No se verifica oracle_hash antes de evaluar.** Ningún componente verifica la identidad semántica del oráculo (OracleSemanticIdentityCalculator.calculate) antes de usarlo como referencia de evaluación. Riesgo de evaluar contra un oráculo mutado. |
| **E-4.1-022** | P1 | bootstrap/topology.py::DefaultNodeMatchingPolicy.matching_key | **Framing del matching_key sin protección contra ambigüedad.** matching_key() retorna MatchingKey(value=f"{node.node_type}:{node.text_content}"). Si text_content contiene ":", la clave generada es ambigua y puede producir falsos positivos o negativos en el alineamiento LCS. A diferencia de DocumentId, NodeId y GroundTruthState (Fase 3), text_content no tiene contrato de dominio que prohíba ":". |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-4.1-01 | LCSAnchorAlignmentStrategy usa anchor_type=ContentNodeType.HEADING por defecto. Si el runtime pierde headings, el alineamiento se degrada a una única ventana global. | Medio | OPEN |
| OBS-4.1-02 | TEDEvaluationContext.max_node_threshold tiene default de 150 en models.py pero create_topology_evaluator() lo sobreescribe a 2000. Existe inconsistencia de defaults. | Bajo | OPEN |
| OBS-4.1-03 | La duplicación de PreferCandidateTieBreaker existe en alignment/tie_break.py y engines/lcs_engine.py. Ambos definen la misma clase. | Bajo | OPEN |
| OBS-4.1-04 | EntityRecallEvaluator usa matching_key() que depende de DefaultNodeMatchingPolicy. Si se aplica normalización al matching, el recall se beneficia automáticamente. | Bajo | OPEN |
| OBS-4.1-05 | StructuralTopologyMetric en tools/ tiene su propia reconstrucción de jerarquía (_build_apted_tree) independiente de la infraestructura nativa. | Medio | OPEN |

---

## 12. MATRIZ DE TRIAJE

| Componente | Clasificación | Justificación forense |
|---|---|---|
| ZhangShashaEngine | RETAIN | Motor matemático puro, completo, con suite rigurosa de 17 tests. Reutilizable directamente. (E-4.1-001, E-4.1-017) |
| ForestDistanceCalculator | RETAIN | Ecuaciones de recurrencia stateless con raíz virtual de costo 0.0. (E-4.1-001) |
| PostorderIndexer | RETAIN | Indexación O(N) con validación estricta. (E-4.1-016) |
| ZhangShashaTreeDistanceCalculator | RETAIN | Implementación canónica con early exits. (E-4.1-001) |
| TreeDistanceTable | RETAIN | Estructura optimizada con __slots__. (E-4.1-001) |
| TreeEditDistanceEvaluator | RETAIN | Application Service puro con pipeline modular. (E-4.1-002, E-4.1-004) |
| EntityRecallEvaluator | RETAIN | Recall O(n) con ConfusionMatrix. (E-4.1-003) |
| LCSAnchorAlignmentStrategy | RETAIN | Alineamiento con anchor_type configurable. (E-4.1-012) |
| HeadingAnchorPartitionStrategy | RETAIN | Particionado O(n) con intervalos semiabiertos. (E-4.1-013) |
| MaxBoundNormalizationPolicy | RETAIN | Normalización con invariante geométrica. (E-4.1-014) |
| WorstCaseOverflowStrategy | RETAIN | Fallback lineal ante overflow. (E-4.1-015) |
| LCSSequenceAlignmentEngine | RETAIN | Motor LCS con tie-breaker inyectable. (E-4.1-012) |
| UnitCostContext | REFACTOR | Costos uniformes sin criticidad. Debe extenderse para soportar ponderación por ContentNodeType (DC-06). (E-4.1-005) |
| DefaultNodeMatchingPolicy | REFACTOR | Igualdad textual directa sin normalización. Debe agregarse stripping + Unicode NFC. (E-4.1-006, OBS-0.4.1-01 heredado) |
| ParserEvaluationStrategy | RETAIN | Válido para comparación de parsers. No debe modificarse; Fase 4 crea una estrategia nueva de regresión. (E-4.1-007) |
| StructuralTopologyMetric | TO BE VERIFIED | Dualidad con rama nativa. Requiere benchmark comparativo antes de decidir deprecación. (E-4.1-008, OBS-0.4.1-04 heredado) |
| ASTFingerprintPolicy | RETAIN | Mecanismo ortogonal a compute_ast_hash. (E-4.1-019, HITO 2.0 E-2.0-16) |
| TopologyBenchmarkService | RETAIN | Servicio de aplicación puro. (E-4.1-020) |
| DefaultBenchmarkAggregationStrategy | RETAIN | Agregación por promedio aritmético. (E-4.1-020) |
| MetricRegistry | RETAIN | Registro centralizado con composición perezosa. (E-4.1-020) |
| RegressionEvaluationStrategy | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-009) |
| CriticalityAwareCostContext | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-005, E-4.1-010) |
| NodeCriticality (enum) | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-010) |
| CriticalityPolicy | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-010) |
| RegressionVerdict | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-011) |
| RegressionThresholds | MISSING | No existe. Debe crearse en Fase 4. (E-4.1-011) |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Motor Matemático (TED)

| Elemento | Estado | Evidencia |
|---|---|---|
| ZhangShashaEngine | EXISTENTE | E-4.1-001 |
| ForestDistanceCalculator | EXISTENTE | E-4.1-001 |
| PostorderIndexer con raíz virtual | EXISTENTE | E-4.1-016 |
| Suite de tests (17 tests) | EXISTENTE | E-4.1-017 |

**Veredicto del pilar:** El motor matemático está completo, es puro y tiene tests rigurosos. Reutilizable directamente por Fase 4 sin modificación.

### Pilar 2 — Evaluadores de Dominio

| Elemento | Estado | Evidencia |
|---|---|---|
| TreeEditDistanceEvaluator | EXISTENTE | E-4.1-002 |
| EntityRecallEvaluator | EXISTENTE | E-4.1-003 |
| Pipeline modular (Alignment → Partition → Engine → Normalize) | EXISTENTE | E-4.1-004 |
| MaxBoundNormalizationPolicy | EXISTENTE | E-4.1-014 |
| WorstCaseOverflowStrategy | EXISTENTE | E-4.1-015 |

**Veredicto del pilar:** Los evaluadores están completos y son reutilizables. El pipeline es modular y cada etapa está desacoplada por protocolos.

### Pilar 3 — Estrategia de Orquestación

| Elemento | Estado | Evidencia |
|---|---|---|
| ParserEvaluationStrategy (parser vs parser) | EXISTENTE | E-4.1-007 |
| RegressionEvaluationStrategy (runtime vs oráculo) | FALTANTE | E-4.1-009 |
| create_topology_evaluator() (composition root) | EXISTENTE | E-4.1-001 |

**Veredicto del pilar:** La estrategia de orquestación existe para comparación de parsers. Fase 4 debe crear una nueva estrategia de regresión que consuma SealedOracle y produzca RegressionVerdict.

### Pilar 4 — Conexión con Baseline Sellada

| Elemento | Estado | Evidencia |
|---|---|---|
| Consumo de SealedOracle | FALTANTE | E-4.1-009 |
| Verificación de oracle_hash antes de evaluar | FALTANTE | E-4.1-021 |
| Verificación de completitud biyectiva | FALTANTE (en este contexto) | E-4.1-009 |

**Veredicto del pilar:** Completamente ausente. Este es el gap central de Fase 4 (GAP-2.0-11 heredado del HITO 2.0). Fase 4 debe crear el adaptador que conecte SealedOracle con la infraestructura topológica.

### Pilar 5 — Criticidad y Regresión Graduada

| Elemento | Estado | Evidencia |
|---|---|---|
| Taxonomía de criticidad (DC-06) | FALTANTE | E-4.1-010 |
| Reglas de regresión graduada (DC-07) | FALTANTE | E-4.1-011 |
| CriticalityAwareCostContext | FALTANTE | E-4.1-005 |
| RegressionVerdict | FALTANTE | E-4.1-011 |
| RegressionThresholds | FALTANTE | E-4.1-011 |

**Veredicto del pilar:** Completamente ausente. DC-06 y DC-07 son los Decision Candidates principales de Fase 4. Deben materializarse como NADRs y luego como contratos de dominio.

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-4.1-01** | No existe conexión entre SealedOracle y la infraestructura topológica. Ningún componente consume SealedOracle ni verifica oracle_hash antes de evaluar. (GAP-2.0-11 heredado) | E-4.1-009, E-4.1-021 | Pilar 4 / NADR-F17BIS-16 §5.2 | **Fase 4** | OPEN |
| **GAP-4.1-02** | No existe taxonomía de criticidad de nodos. No existe mapeo ContentNodeType → CRITICAL/WARNING/INFO. (DC-06) | E-4.1-010 | Pilar 5 / ADR Maestro §8 DC-06 | **Fase 4** | OPEN |
| **GAP-4.1-03** | No existen reglas de regresión graduada. No existe mecanismo de veredicto PASS/WARNING/HARD_FAIL. (DC-07) | E-4.1-011 | Pilar 5 / ADR Maestro §8 DC-07 | **Fase 4** | OPEN |
| **GAP-4.1-04** | DefaultNodeMatchingPolicy usa igualdad textual directa sin normalización. Un espacio sobrante o cambio de mayúscula invalida el matching. (OBS-0.4.1-01 heredado) | E-4.1-006 | Pilar 2 / HITO 0.4.1 | **Fase 4** | OPEN |
| **GAP-4.1-05** | Dualidad core/ vs tools/ sin resolución. Dos motores TED coexisten (ZhangShashaEngine vs StructuralTopologyMetric con APTED). (OBS-0.4.1-04 heredado) | E-4.1-008 | Pilar 1 / HITO 0.4.1 | **Fase 4** | OPEN |
| **GAP-4.1-06** | UnitCostContext aplica costos uniformes (1.0) sin ponderación por criticidad. Debe extenderse para soportar CriticalityAwareCostContext. | E-4.1-005 | Pilar 5 / ADR Maestro §8 DC-06 | **Fase 4** | OPEN |
| **GAP-4.1-07** | El matching_key usa ":" como delimitador sin proteger text_content. Si text_content contiene ":", la clave es ambigua. A diferencia de DocumentId/NodeId/GroundTruthState (Fase 3), text_content no tiene contrato de dominio. | E-4.1-022 | Pilar 2 / NADR-F17BIS-17 §5.1 | **Fase 4** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-4.1-A | La infraestructura matemática y de evaluación topológica es reutilizable directamente para Fase 4 sin modificación. | CONFIRMADA | E-4.1-001 a E-4.1-004, E-4.1-012 a E-4.1-015, E-4.1-017 | Fase 4 no necesita reescribir el motor matemático ni los evaluadores. |
| H-4.1-B | El DefaultNodeMatchingPolicy requiere normalización (stripping + Unicode NFC) para ser robusto ante variaciones triviales. | CONFIRMADA | E-4.1-006, OBS-0.4.1-01 | Fase 4 debe crear una NormalizedNodeMatchingPolicy o extender la existente. |
| H-4.1-C | La dualidad core/ vs tools/ (ZhangShashaEngine vs StructuralTopologyMetric) puede resolverse en Fase 4. | TO BE VERIFIED | E-4.1-008, OBS-0.4.1-04 | Requiere benchmark comparativo empírico antes de decidir deprecación. No puede resolverse por intuición. |
| H-4.1-D | El SealedOracle puede conectarse directamente a los evaluadores existentes (TreeEditDistanceEvaluator, EntityRecallEvaluator) sin modificar sus firmas. | CONFIRMADA (inferencia de tipos: Tuple[ASTNode, ...] es subtipo de Sequence[ASTNode]) | E-4.1-007, E-4.1-009 | Los evaluadores toman Sequence[ASTNode]. SealedOracle.nodes es Tuple[ASTNode, ...]. La conexión es directa: evaluar(candidate, sealed_oracle.nodes). Verificación empírica pendiente en implementación de Fase 4. |
| H-4.1-E | La verificación de oracle_hash debe ocurrir antes de la evaluación, no durante. | CONFIRMADA | E-4.1-021, ENGINEERING_PRINCIPLES §IV (Fail-Fast) | Si el oráculo fue mutado en disco, la evaluación debe abortar inmediatamente, no degradar silenciosamente. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué componentes son reutilizables directamente para Fase 4?

**Estado actual verificado:**

1. Motor Zhang-Shasha completo: ZhangShashaEngine, ForestDistanceCalculator, PostorderIndexer, ZhangShashaTreeDistanceCalculator, TreeDistanceTable.
2. Evaluadores: TreeEditDistanceEvaluator, EntityRecallEvaluator.
3. Pipeline: LCSAnchorAlignmentStrategy, HeadingAnchorPartitionStrategy, MaxBoundNormalizationPolicy, WorstCaseOverflowStrategy.
4. Motor LCS: LCSSequenceAlignmentEngine con PreferCandidateTieBreaker.
5. Composition root: create_topology_evaluator().
6. Servicio de benchmark: TopologyBenchmarkService, DefaultBenchmarkAggregationStrategy, MetricRegistry.
7. Fingerprint: ASTFingerprintPolicy.

**Respuesta forense:**

12 componentes son reutilizables directamente sin modificación. Todos son puros, stateless, desacoplados por protocolos, y tienen tests rigurosos. La infraestructura matemática y de evaluación está lista para ser consumida por Fase 4.

**Implicación:**

Fase 4 no necesita reescribir el motor matemático ni los evaluadores. Debe crear la capa de orquestación de regresión, la conexión con el oráculo sellado, la taxonomía de criticidad y las reglas de veredicto.

### 16.2 ¿Qué componentes requieren extensión para soportar regresión graduada?

**Estado actual verificado:**

1. UnitCostContext: costos uniformes sin criticidad. Debe extenderse para soportar ponderación por ContentNodeType.
2. DefaultNodeMatchingPolicy: igualdad textual directa. Debe agregarse normalización (stripping + Unicode NFC).

**Respuesta forense:**

2 componentes requieren extensión. UnitCostContext debe convertirse en CriticalityAwareCostContext. DefaultNodeMatchingPolicy debe convertirse en NormalizedNodeMatchingPolicy. Ambos cambios son aditivos y no rompen los contratos existentes.

**Implicación:**

Las extensiones deben implementarse como nuevas clases que implementen los protocolos existentes (TreeEditCostContext, NodeMatchingPolicy), sin modificar las clases originales. Esto preserva el principio Open/Closed.

### 16.3 ¿Cómo se conecta actualmente la infraestructura topológica con el oráculo sellado (SealedOracle)?

**Estado actual verificado:**

1. Ningún componente de core/benchmark/topology/ consume SealedOracle.
2. Ningún componente verifica oracle_hash antes de evaluar.
3. ParserEvaluationStrategy toma Sequence[ASTNode] genérico, no SealedOracle.
4. Los evaluadores (TreeEditDistanceEvaluator, EntityRecallEvaluator) toman Sequence[ASTNode] como parámetros.

**Respuesta forense:**

La conexión NO EXISTE. Este es el gap central de Fase 4 (GAP-2.0-11 heredado del HITO 2.0). Sin embargo, la conexión es arquitectónicamente simple: SealedOracle.nodes es Tuple[ASTNode, ...], y los evaluadores toman Sequence[ASTNode]. La conexión directa es evaluar(candidate_ast, sealed_oracle.nodes). No se requiere modificar las firmas de los evaluadores (verificación empírica pendiente, H-4.1-D).

Lo que SÍ debe crearse es:
- Un adaptador que cargue el SealedOracle desde disco.
- Una verificación de oracle_hash antes de evaluar (Fail-Fast).
- Una verificación de completitud biyectiva.
- Una estrategia de evaluación de regresión que orqueste el flujo completo.

**Implicación:**

Fase 4 debe crear un RegressionEvaluationStrategy que:
1. Cargue el SealedOracle.
2. Verifique oracle_hash (Fail-Fast).
3. Verifique completitud biyectiva.
4. Evalúe el runtime AST contra el oráculo usando los evaluadores existentes.
5. Produzca un RegressionVerdict.

### 16.4 ¿Qué gaps existen entre la infraestructura actual y los requisitos de Fase 4 (DC-06, DC-07)?

**Estado actual verificado:**

1. DC-06 (Taxonomía de Criticidad): No existe ningún enum, política o contrato que mapee ContentNodeType a niveles de criticidad.
2. DC-07 (Reglas de Regresión): No existe ningún mecanismo de veredicto (PASS, WARNING, HARD_FAIL).

**Respuesta forense:**

7 gaps consolidados separan la infraestructura actual de los requisitos de Fase 4:
- GAP-4.1-01: Conexión SealedOracle ausente.
- GAP-4.1-02: Taxonomía de criticidad ausente (DC-06).
- GAP-4.1-03: Reglas de regresión ausentes (DC-07).
- GAP-4.1-04: Matching sin normalización.
- GAP-4.1-05: Dualidad core/ vs tools/.
- GAP-4.1-06: Costos sin criticidad.
- GAP-4.1-07: Framing del matching_key sin protección contra ambigüedad.

**Implicación:**

Fase 4 debe resolver estos 7 gaps. Los gaps 4.1-01, 4.1-02, 4.1-03 y 4.1-06 son bloqueantes para la certificación científica. Los gaps 4.1-04, 4.1-05 y 4.1-07 son importantes pero no bloqueantes.

### 16.5 ¿Cuál es el estado de la dualidad core/ vs tools/ (OBS-0.4.1-04)?

**Estado actual verificado:**

1. Rama nativa (core/benchmark/topology/): ZhangShashaEngine, Python puro, O(M^2 N^2) amortiguado, particionado escalable, costos flexibles, raíz virtual con costo 0.0.
2. Rama APTED (tools/evaluation/topology/metrics/structural.py): StructuralTopologyMetric, APTED, O(M^3 N), sin particionado, costos fijos, raíz artificial.

**Respuesta forense:**

La dualidad persiste desde el HITO 0.4.1. El HITO 0.4.1 recomendó consolidar sobre la rama nativa. Sin embargo, la consolidación requiere evidencia empírica (benchmark comparativo) antes de decidir deprecación. No puede resolverse por intuición ni por preferencia estética.

**Implicación:**

Fase 4 debe ejecutar un benchmark comparativo entre ZhangShashaEngine y StructuralTopologyMetric sobre el corpus de calibración. Si los resultados son equivalentes, se depreca StructuralTopologyMetric. Si no, se documenta la razón y se mantiene la coexistencia.

### 16.6 ¿El DefaultNodeMatchingPolicy requiere normalización (OBS-0.4.1-01)?

**Estado actual verificado:**

1. match() compara candidate.node_type == ground_truth.node_type and candidate.text_content == ground_truth.text_content.
2. matching_key() retorna MatchingKey(value=f"{node.node_type}:{node.text_content}").
3. No se aplica stripping, normalización Unicode ni lowercasing.

**Respuesta forense:**

Sí, requiere normalización. Un espacio sobrante al inicio o final del texto, o un cambio de mayúscula, invalida el matching. Esto afecta tanto al alineamiento LCS (LCSAnchorAlignmentStrategy usa matching_key()) como al recall (EntityRecallEvaluator usa matching_key()).

La normalización recomendada es: stripping + Unicode NFC. NO lowercasing, porque puede cambiar la semántica en algunos contextos (ej. "DNA" vs "dna").

Adicionalmente, el framing del matching_key usa ":" como delimitador sin proteger text_content. Si text_content contiene ":", la clave es ambigua. Esto debe resolverse mediante normalización o escapado del delimitador.

**Implicación:**

Fase 4 debe crear una NormalizedNodeMatchingPolicy que implemente NodeMatchingPolicy con normalización. La política debe ser inyectable para preservar el principio Open/Closed. El framing del matching_key debe protegerse contra ambigüedad.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-06** | Taxonomía de Criticidad de Nodos | E-4.1-010, E-4.1-005, GAP-4.1-02 | Ausente. No existe ningún enum, política o contrato de criticidad. | **Fase 4** |
| **DC-07** | Reglas de Regresión Topológica | E-4.1-011, GAP-4.1-03 | Ausente. No existe ningún mecanismo de veredicto. | **Fase 4** |
| **DC-10** | Desacoplamiento del Runner de CI | E-4.1-009, GAP-4.1-01 | Ausente en el contexto de regresión. Existe para benchmark. | **Fase 4 / Fase 6** |

**Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos. DC-06 y DC-07 fueron resueltos normativamente en el ADR Maestro §8, pero no tienen materialización operativa.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Evaluación contra oráculo mutado | Si el oráculo es mutado en disco y no se verifica oracle_hash antes de evaluar, la evaluación produce resultados falsos. | Alto | E-4.1-021 |
| Matching frágil | Sin normalización, variaciones triviales (espacios, Unicode) invalidan el matching y degradan el alineamiento y el recall. | Medio | E-4.1-006 |
| Costos uniformes | Sin ponderación por criticidad, la pérdida de una ecuación tiene el mismo peso que la pérdida de un caption. | Alto | E-4.1-005 |
| Dualidad de motores | Dos motores TED pueden producir resultados diferentes. Sin benchmark comparativo, no hay evidencia de equivalencia. | Medio | E-4.1-008 |
| Degradación de alineamiento sin headings | Si el runtime pierde headings, el alineamiento LCS se degrada a una única ventana global, aumentando el costo computacional. | Medio | OBS-4.1-01 |
| Ambigüedad en matching_key | Si text_content contiene ":", la clave de matching es ambigua. Riesgo de falsos positivos/negativos en alineamiento LCS. | Medio | E-4.1-022 |
| Tests de regresión tautológicos y CI ausente | test_golden_parser.py tiene tautología (A == A) y no existe CI workflow. La regresión no puede detectarse actualmente. | Alto | HITO 0.4.4_C5 (GAP-0.4-09, C5-R01 a C5-R10) |

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
9. ¿Cómo se protege el framing del matching_key contra ambigüedad cuando text_content contiene ":"?

---

## 21. CIERRE DEL HITO 4.1

Este HITO confirma que la infraestructura matemática y de evaluación topológica es SOTA y reutilizable como componentes puros. La capa de orquestación está diseñada para comparación de parsers, no para regresión contra oráculo sellado. La conexión con el oráculo sellado, la taxonomía de criticidad y las reglas de regresión graduada están completamente ausentes.

**Estado del HITO:** IN_PROGRESS v1.0.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados. Todas las evidencias tienen ID estable y severidad. Todos los gaps tienen evidencia vinculada y fase destino. Todas las hipótesis están cerradas como CONFIRMADA, RESUELTA, RECHAZADA o TO BE VERIFIED. Cero hipótesis abiertas sin destino.
**Verificación de cadena de gobernanza:** ADR_F17_BIS_MASTER → HITO_0.4.1 → HITO_0.4.4_C1 → HITO_0.4.4_C5 → HITO_2.0 → FASE_3_HANDOFF → HITO_4.1 (este documento). Cadena completa verificada.
**Contradicciones con HITOs previos:** Ninguna. Todos los hallazgos son consistentes con los HITOs previos. Los gaps heredados (OBS-0.4.1-01, OBS-0.4.1-04, GAP-2.0-11) se confirman como persistentes. Se agrega GAP-4.1-07 (framing del matching_key) como hallazgo nuevo.
**Decision Candidates generados:** Ninguno nuevo. DC-06 y DC-07 ya existen en el ADR Maestro §8. Este HITO confirma su ausencia operativa.
**Siguiente paso recomendado:** Construir HITO_4.2 (Criticality and Regression Rules Discovery) usando este HITO como insumo, para auditar qué existe y proponer la taxonomía de criticidad y las reglas de regresión. Luego construir ADR_F17-BIS_04 (Scientific Verification) y los NADRs de Fase 4.