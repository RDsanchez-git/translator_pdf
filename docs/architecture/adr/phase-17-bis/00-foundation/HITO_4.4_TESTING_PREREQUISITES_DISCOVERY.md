# HITO_4.4_TESTING_PREREQUISITES_DISCOVERY.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-08-30
**Fecha de congelamiento:** 2026-08-30
**Fase:** 17-BIS — Fase 4 (Scientific Verification)
**Tipo de artefacto:** Forensic Discovery / Testing Architecture Prerequisites Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT (FROZEN), HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT (FROZEN), HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT (FROZEN), HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY (FROZEN), HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY (FROZEN), HITO_4.3_BASELINE_BENCHMARK_ADAPTER_ENTRY_POINT_DISCOVERY (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0-FROZEN.
**Mandato:** Auditar el estado actual de los tests de regresión, snapshots, fixtures, CI gates y precondiciones de prueba necesarias para que Fase 4 pueda implementar regresión científica contra oráculo sellado de forma confiable, no tautológica y de grado producción.
**Síntesis:** La infraestructura matemática de topología tiene tests unitarios SOTA, y existe un workflow de CI funcional con protección de oráculos inmutables. Existe también una capa de ~137 tests de Fase 3 que prueban contratos de identidad, framing, completitud y ciclo de vida, reutilizables como infraestructura de testing. Sin embargo, la capa de regresión integrada contra oráculo sellado no es confiable: el golden test es tautológico, los snapshots tienen autogeneración y sub-aserción, y el CI ejecuta tests potencialmente defectuosos. Antes de que la regresión graduada sea efectiva, Fase 4 debe construir una suite soberana basada en oráculos sellados, fixtures sellados, mutaciones negativas y contratos de salida verificables.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-08-30 | Emisión inicial y congelamiento formal. Discovery forense de prerequisitos de testing para Scientific Verification. Correcciones integradas: pyproject.toml reclasificado como EXISTENTE, CI workflow reclasificado como EXISTENTE con riesgo, tests de Fase 3 reconocidos como infraestructura reutilizable, distinción componente/integración explícita, conteo Zhang-Shasha explícito. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la evidencia disponible sobre la arquitectura de tests de regresión heredada de HITO_0.4.4, HITO_0.4.4_C5, HITO_4.1, HITO_4.2 y HITO_4.3. El objetivo fue determinar si la suite actual puede certificar, de forma SOTA y de grado producción, una regresión científica contra `SealedOracle`.

**Hallazgo central:**

> La infraestructura matemática de topología posee tests unitarios fuertes y conservables, especialmente `test_zhang_shasha.py` (15 funciones, 17 ejecuciones parametrizadas). Existe un workflow de CI funcional (`.github/workflows/ci.yml`) con protección de oráculos inmutables. Existe también una capa de ~137 tests de Fase 3 que prueban contratos de identidad, framing, completitud y ciclo de vida, reutilizables como infraestructura de testing. Sin embargo, la capa de regresión integrada contra oráculo sellado no es confiable: el golden test es tautológico, los snapshots tienen autogeneración y sub-aserción, no existen pruebas de precondiciones criptográficas en contexto de evaluación, no existen pruebas de veredicto graduado, y el CI ejecuta tests potencialmente defectuosos bajo el marker `regression`.

**Defectos dominantes confirmados:**

1. **Golden test tautológico (E-4.4-001):** `test_golden_parser.py` compara el fingerprint actual contra un valor derivado de la misma ejecución o permite skips ante ausencia de oráculo. No es una barrera de regresión.
2. **Snapshots con autogeneración y sub-aserción (E-4.4-002):** `test_chunker_snapshot.py` no garantiza oráculo independiente, inmutable y completo.
3. **CI workflow ejecuta tests potencialmente defectuosos (E-4.4-003):** El workflow `.github/workflows/ci.yml` existe y es funcional, con 4 jobs y protección de oráculos. Sin embargo, el job `regression-gates` ejecuta `pytest -m "regression"` que puede incluir tests tautológicos o con autogeneración. El CI no bloquea merges basándose en tests confiables.
4. **Ausencia de tests del adaptador SealedOracle→evaluación (E-4.4-005):** No existen pruebas que verifiquen carga de oráculo, `oracle_hash`, `ground_truth_state`, completitud y conexión con evaluadores en contexto de evaluación.
5. **Ausencia de tests de veredicto graduado (E-4.4-006):** No existen pruebas para `PASS`, `WARNING`, `HARD_FAIL`, pérdida de nodos críticos, umbrales NSS o exit codes.
6. **Ausencia de negative controls / mutation fixtures (E-4.4-007):** No hay fixtures diseñados para demostrar que la suite falla cuando se viola el contrato.

**Veredicto:** La construcción SOTA para Fase 4 no debe ser "un golden test más" ni una extensión de snapshots existentes. Debe ser una suite soberana de regresión científica con oráculos sellados, fixtures sellados, mutaciones negativas, precondiciones criptográficas obligatorias, pruebas de veredicto graduado, pruebas de entry point y CI gates confiables. La suite actual no alcanza grado producción sin remediación.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No implementa tests. No modifica fixtures. No introduce entry points. Su función es auditar prerequisitos, clasificar gaps y derivar evidencia para ADRs/NADRs y Execution Plans.

Este HITO no reaudita el motor Zhang-Shasha ni los evaluadores TED/Recall (cubiertos por HITO_4.1). No reaudita la taxonomía de criticidad ni las reglas de regresión (cubiertos por HITO_4.2). No reaudita el adaptador SealedOracle→evaluación (cubierto por HITO_4.3).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR_F17_BIS_MASTER, HITO_0.4.4, HITO_0.4.4_C5.
2. Cargar HITOs previos aplicables: HITO_4.1, HITO_4.2, HITO_4.3.
3. Inspeccionar el árbol de proyecto (`PROJECT_TREE.txt`) y el workspace (`ARCHITECTURE_WORKSPACE.md`).
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs E-4.4-NNN.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar TO BE VERIFIED cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Artefactos / Referencias | Estado |
|---|---|---|
| Tests de topología matemática | `tests/unit/test_zhang_shasha.py` (15 funciones, 17 ejecuciones parametrizadas), `tests/unit/test_structural_metric.py` | Referenciado desde HITO_4.1 |
| Tests de golden parser | `tests/integration/test_golden_parser.py` | Auditado por HITO_0.4.4 / C5 |
| Tests de snapshots de chunking | `tests/integration/test_chunker_snapshot.py` | Auditado por HITO_0.4.4 / C5 |
| Helpers de bootstrap de golden data | `tests/helpers/bootstrap_translation_golden.py` | Auditado por HITO_0.4.4 / C5 |
| CI workflows | `.github/workflows/ci.yml` | EXISTENTE y funcional (4 jobs) |
| Configuración centralizada de tooling | `pyproject.toml` | EXISTENTE y funcional |
| Adaptador SealedOracle→evaluación | No existe | Auditado por HITO_4.3 |
| RegressionEvaluationStrategy | No existe | Auditado por HITO_4.3 |
| RegressionVerdict / RegressionThresholds | No existe | Auditado por HITO_4.2 |
| CriticalityAwareCostContext | No existe | Auditado por HITO_4.2 |
| NormalizedNodeMatchingPolicy / framing seguro | No existe | Auditado por HITO_4.1 |
| Entry point de regresión | No existe | Auditado por HITO_4.3 |
| Tests de identidad y framing (Fase 3) | `test_framing_injectivity.py`, `test_corpus_models.py`, `test_ast_models.py`, `test_oracle_identity.py`, `test_manifest_fingerprint.py`, `test_ground_truth_completeness.py`, `test_ground_truth_lifecycle.py`, `test_ground_truth_sealing_atomicity.py`, `test_ground_truth_sealed_protection.py`, `test_ground_truth_validity.py` | EXISTENTES (~137 tests, reutilizables) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER | Fuente normativa: dimensiones de identidad, invariantes, hoja de ruta |
| HITO previo | HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT | Evidencia sobre tautologías, snapshots, mocks, límites de tests |
| HITO previo | HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT | Evidencia sobre golden tests, snapshots, estado de CI y pyproject |
| HITO previo | HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY | Evidencia sobre evaluadores topológicos reutilizables y gap de matching |
| HITO previo | HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY | Evidencia sobre ausencia de criticidad y veredicto graduado |
| HITO previo | HITO_4.3_BASELINE_BENCHMARK_ADAPTER_ENTRY_POINT_DISCOVERY | Evidencia sobre ausencia de adaptador, entry point y verificación de oracle_hash |
| Principio rector | HITO_0.4.4: "Un test no es evidencia..." | Criterio de validez de tests |
| Proyecto | PROJECT_TREE.txt, ARCHITECTURE_WORKSPACE.md | Estructura real del repositorio |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 | Estructura canónica del HITO |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Test de regresión científico requerido (AUSENTE)

```text
FLUJO A -- Regresion cientifica requerida (AUSENTE)

  Fixture de corpus canonico sellado [Debe existir]
    |
    +---> CorpusManifest con oracle_hash + ground_truth_state [Existe en dominio]
    |
    +---> SealedOracle fixture independiente [Debe cargarse]
    |
    +---> Verificacion de completitud biyectiva [Falta en contexto test/evaluacion]
    |
    +---> Verificacion ground_truth_state == SEALED [Falta]
    |
    +---> Verificacion oracle_hash [Falta]
    |
    +---> Runtime AST candidate fixture [Debe ser independiente]
    |
    +---> Evaluacion topologica [Infraestructura existe]
    |
    +---> RegressionVerdict PASS/WARNING/HARD_FAIL [Falta]
    |
    +---> Assert de reporte + exit code [Falta]
```

### FLUJO B — Golden test actual degradado

```text
FLUJO B -- Golden parser actual degradado

  test_golden_parser.py
    |
    +---> expected_fingerprint derivado o no independiente [GAP]
    |
    +---> current_fingerprint de la ejecucion actual [GAP]
    |
    +---> comparacion A == A o skip si falta oraculo [GAP]
    |
    +---> test pasa sin demostrar independencia [NO CERTIFICA]

Veredicto: No es barrera de regresion.
```

### FLUJO C — Snapshot actual degradado

```text
FLUJO C -- Snapshot de chunking actual degradado

  test_chunker_snapshot.py
    |
    +---> snapshot puede autogenerarse [GAP]
    |
    +---> campos parciales/sub-asercion [GAP]
    |
    +---> ausencia de garantia de inmutabilidad [GAP]
    |
    +---> test puede pasar con contrato incompleto [NO CERTIFICA]

Veredicto: No es oraculo soberano.
```

### FLUJO D — Tests topológicos unitarios sanos

```text
FLUJO D -- Tests matematicos topologicos sanos

  tests/unit/test_zhang_shasha.py (15 funciones, 17 ejecuciones parametrizadas)
    |
    +---> arboles vacios
    +---> nodos individuales
    +---> identidad
    +---> insercion / borrado / sustitucion atomica
    +---> isomorfismo
    +---> simetria
    +---> multi-raiz
    +---> profundidad / anchura
    +---> escalabilidad hasta 150 nodos

Veredicto: Test suite SOTA conservable.
```

### FLUJO E — CI workflow existente

```text
FLUJO E -- CI workflow existente

  .github/workflows/ci.yml
    |
    +---> Job: static-analysis (pyright + import-linter) [OK]
    |
    +---> Job: regression-gates (pytest -m "regression") [RIESGO]
    |         |
    |         +---> persist-credentials: false [OK]
    |         +---> CORPUS_READONLY: "true" [OK]
    |         +---> git diff --exit-code tests/fixtures/ [OK]
    |         +---> Ejecuta tests marcados como "regression" [RIESGO: puede incluir tests defectuosos]
    |
    +---> Job: unit-tests (pytest -m "unit") [OK]
    |
    +---> Job: integration-tests (pytest -m "integration and not regression") [OK]

Veredicto: Workflow funcional, pero ejecuta tests potencialmente defectuosos.
```

### FLUJO F — Tests de Fase 3 reutilizables

```text
FLUJO F -- Tests de Fase 3 reutilizables (~137 tests)

  test_framing_injectivity.py (17 tests)
    +---> Inyectividad del framing de manifest_hash
    +---> Inyectividad del framing de oracle_hash
    +---> Property-based con hypothesis

  test_corpus_models.py (~30 tests)
    +---> Contratos DocumentId, GroundTruthState
    +---> Invariantes CorpusDocumentMetadata, CorpusManifest

  test_ast_models.py (~27 tests)
    +---> Contratos NodeId, parent_node_id
    +---> Invariantes ASTNode, spawn_fragment

  test_oracle_identity.py (8 tests)
    +---> Identidad semantica del oraculo

  test_manifest_fingerprint.py (10 tests)
    +---> Fingerprint del manifiesto, sensibilidad a oracle_hash

  test_ground_truth_completeness.py (6 tests)
    +---> Completitud biyectiva (BaselineCompletenessVerifier)

  test_ground_truth_lifecycle.py (~22 tests)
    +---> Transiciones legales/ilegales, inmutabilidad

  test_ground_truth_sealing_atomicity.py (~7 tests)
    +---> Atomicidad del sellado, autoridad unica

  test_ground_truth_sealed_protection.py (~5 tests)
    +---> Proteccion contra sobrescritura

  test_ground_truth_validity.py (5 tests)
    +---> Validez estructural del oraculo

Veredicto: Infraestructura de testing reutilizable para Fase 4.
```

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| Tests unitarios de Zhang-Shasha | `test_zhang_shasha.py` (15 funciones, 17 ejecuciones parametrizadas) | Sí (TreeEditEngine, TreeEditCostContext) | Certificación matemática TED | CONFIRMADO SOTA |
| Tests de StructuralTopologyMetric | `test_structural_metric.py` | Sí (TopologyMetric) | Certificación de métrica APTED legacy/tools | CONFIRMADO |
| Golden parser test | `test_golden_parser.py` | No (tautológico) | Debería certificar parser contra oráculo independiente | CONFIRMADO DEFECTUOSO |
| Snapshot de chunking | `test_chunker_snapshot.py` | No (autogeneración, sub-aserción) | Debería certificar empaquetado/chunking contra snapshot soberano | CONFIRMADO DEFECTUOSO |
| Helper bootstrap golden | `bootstrap_translation_golden.py` | No (herramienta manual) | Generación manual de baselines | CONFIRMADO CON RIESGO |
| CI workflows | `.github/workflows/ci.yml` | Sí (4 jobs) | Dynamic merge gate | EXISTENTE (ejecuta tests potencialmente defectuosos) |
| Configuración de tooling | `pyproject.toml` | Sí (pytest, pyright, importlinter, coverage) | Configuración central de tooling | EXISTENTE |
| Tests de oracle_hash mismatch | No existen | No | Deben probar Fail-Fast ante oráculo mutado | MISSING |
| Tests de ground_truth_state no sellado | No existen | No | Deben probar Fail-Fast ante draft/no sealed | MISSING |
| Tests de completitud biyectiva en evaluación | No existen en contexto evaluación | No | Deben probar baseline incompleta antes de evaluar | MISSING (existen en contexto sellado) |
| Tests de `hydrate_ground_truth()` en regresión | No existen | No | Deben probar hidratación controlada por consumidor | MISSING |
| Tests de adaptador SealedOracle→evaluación | No existen | No | Deben probar conexión runtime AST vs SealedOracle.nodes | MISSING |
| Tests de RegressionEvaluationStrategy | No existen | No | Deben probar orquestación de regresión | MISSING |
| Tests de RegressionVerdict | No existen | No | Deben probar PASS/WARNING/HARD_FAIL | MISSING |
| Tests de criticidad | No existen | No | Deben probar pérdida de CRITICAL/WARNING/INFO | MISSING |
| Tests de NSS ponderado | No existen | No | Deben probar efecto de costos por criticidad | MISSING |
| Tests de NormalizedNodeMatchingPolicy | No existen | No | Deben probar stripping + Unicode NFC | MISSING |
| Tests de framing seguro de matching_key | No existen | No | Deben probar `text_content` con delimitador `:` | MISSING |
| Tests de CLI / exit code | No existen | No | Deben probar 0/1/2 o contrato final ADR | MISSING |
| Negative controls / mutation fixtures | No existen | No | Deben demostrar que la suite falla ante violaciones | MISSING |
| Tests de identidad y framing (Fase 3) | ~137 tests en `tests/unit/` | Sí | Contratos de identidad, framing, completitud, ciclo de vida | EXISTENTES (reutilizables) |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision / Evidencia previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Golden parser test | Tautológico o no soberano | Oráculo independiente e inmutable | HITO_0.4.4: GAP-0.4-09 | DISCREPANCY | E-4.4-001 |
| Snapshot chunking | Autogeneración y sub-aserción | Snapshot cerrado, completo y Fail-Fast si falta | HITO_0.4.4_C5: C5-R01, C5-R02 | DISCREPANCY | E-4.4-002 |
| CI workflows | Existente, ejecuta tests potencialmente defectuosos | Dynamic merge gate con tests confiables | HITO_0.4.4_C5 | PARCIAL | E-4.4-003 |
| pyproject/tooling | Existente y funcional | Configuración central reproducible | HITO_0.4.4_C5 | COMPLIANT | E-4.4-004 |
| Tests de oracle_hash | Ausentes | Fail-Fast ante mismatch | HITO_4.3 GAP-4.3-02 | DISCREPANCY | E-4.4-005 |
| Tests de adapter SealedOracle→evaluación | Ausentes | Cobertura del flujo baseline→benchmark | HITO_4.3 GAP-4.3-01 | DISCREPANCY | E-4.4-006 |
| Tests de veredicto graduado | Ausentes | PASS/WARNING/HARD_FAIL verificable | HITO_4.2 GAP-4.2-02 | DISCREPANCY | E-4.4-007 |
| Tests TED unitarios | Existentes y rigurosos (15 funciones, 17 ejecuciones parametrizadas) | Cobertura matemática determinista | HITO_4.1 E-4.1-017 | COMPLIANT | E-4.4-008 |
| Tests de normalización matching | Ausentes | Matching robusto | HITO_4.1 GAP-4.1-04 | DISCREPANCY | E-4.4-009 |
| Tests de framing matching_key | Ausentes | Delimitador protegido o encoding no ambiguo | HITO_4.1 GAP-4.1-07 | DISCREPANCY | E-4.4-010 |
| Tests de exit code | Ausentes | Contrato observable para CI | HITO_4.3 §16.2 | DISCREPANCY | E-4.4-011 |
| Tests de identidad y framing (Fase 3) | Existentes (~137 tests) | Infraestructura reutilizable | Fase 3 | COMPLIANT | E-4.4-012 |

---

## 8. MUTATION SEMANTICS MATRIX — TEST NEGATIVE CONTROLS

| Mutación / Violación | Test requerido | Resultado esperado | Observed actual | Gap |
|---|---|---|---|---|
| Mutar `SealedOracle.nodes` sin actualizar `oracle_hash` | Test de integridad criptográfica | Abort / Fail-Fast antes de evaluar | No existe | GAP-4.4-05 |
| `ground_truth_state != SEALED` | Test de lifecycle | Abort / Fail-Fast antes de evaluar | No existe | GAP-4.4-06 |
| Documento en manifiesto sin oráculo | Test de completitud biyectiva | Abort / Fail-Fast de corpus | Existe en sellado, no en evaluación | GAP-4.4-07 |
| Oráculo extra sin manifiesto | Test de biyección inversa | Abort / Fail-Fast de corpus | Existe en sellado, no en evaluación | GAP-4.4-07 |
| Pérdida de `DISPLAY_EQUATION` | Test de criticidad CRITICAL | HARD_FAIL | No existe | GAP-4.4-08 |
| Pérdida de `TABLE_COMPLEX` | Test de criticidad CRITICAL | HARD_FAIL | No existe | GAP-4.4-08 |
| Pérdida de `HEADING` | Test de criticidad WARNING | WARNING o veredicto ADR final | No existe | GAP-4.4-08 |
| Pérdida de `CAPTION` | Test de criticidad INFO | PASS con observación o veredicto ADR final | No existe | GAP-4.4-08 |
| NSS bajo umbral crítico | Test de threshold crítico | HARD_FAIL | No existe | GAP-4.4-09 |
| NSS entre umbrales | Test de threshold warning | WARNING | No existe | GAP-4.4-09 |
| `text_content` con espacios / Unicode desnormalizado | Test de NormalizedNodeMatchingPolicy | Matching estable | No existe | GAP-4.4-10 |
| `text_content` con `:` | Test de framing seguro | MatchingKey no ambiguo | No existe | GAP-4.4-11 |
| CLI con PASS | Test de exit code | Exit code 0 | No existe | GAP-4.4-12 |
| CLI con WARNING | Test de exit code | Exit code según ADR final, propuesto 1 | No existe | GAP-4.4-12 |
| CLI con HARD_FAIL | Test de exit code | Exit code según ADR final, propuesto 2 | No existe | GAP-4.4-12 |
| Falta snapshot/oráculo | Test de no-autogeneración | Fail-Fast; no crear baseline en CI | Actual degradado | GAP-4.4-02 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Para evidencia positiva, se usa N/A.

| ID | Sev | Evidencia | Hallazgo |
|---|---|---|---|
| **E-4.4-001** | P0 | HITO_0.4.4 / HITO_0.4.4_C5 → `tests/integration/test_golden_parser.py` | **Golden parser test degradado / tautológico.** El test carga la huella congelada en disco, pero inmediatamente ejecuta `expected_fingerprint = current_fingerprint`. La aserción se transforma en `current_fingerprint == current_fingerprint` (A == A). El test siempre pasa aunque el parser pierda ecuaciones, tablas o destruya la topología. |
| **E-4.4-002** | P0 | HITO_0.4.4_C5 → `tests/integration/test_chunker_snapshot.py` | **Snapshot de chunking degradado.** El test contiene lógica de autogeneración: `if not os.path.exists(self.snapshot_path): json.dump(actual_snapshot, ...)`. Si la prueba se ejecuta en un entorno limpio sin la fixture, genera el snapshot sobre la marcha y retorna PASS. Además, el bucle de validación solo compara 4 atributos de 11 serializados, dejando `chunk_fingerprint`, `source_sequence_range`, `node_count` y `estimated_tokens` sin verificar. |
| **E-4.4-003** | P1 | `.github/workflows/ci.yml` | **CI workflow existente pero ejecuta tests potencialmente defectuosos.** El workflow tiene 4 jobs (static-analysis, regression-gates, unit-tests, integration-tests), protección de oráculos inmutables (`persist-credentials: false`, `CORPUS_READONLY: "true"`, `git diff --exit-code tests/fixtures/`). Sin embargo, el job `regression-gates` ejecuta `pytest -m "regression"` que puede incluir tests tautológicos o con autogeneración. El CI no bloquea merges basándose en tests confiables. |
| **E-4.4-004** | N/A | `pyproject.toml` | **Configuración centralizada de tooling EXISTENTE y funcional.** El archivo contiene `[tool.pytest.ini_options]` con testpaths y markers, `[tool.pyright]` con configuración de type checking, `[tool.importlinter]` con contratos de frontera hexagonal, y `[tool.coverage.run]` / `[tool.coverage.report]`. No es un gap. |
| **E-4.4-005** | P0 | HITO_4.3 GAP-4.3-02 | **Tests de oracle_hash ausentes.** No existe prueba que demuestre Fail-Fast ante mismatch de `oracle_hash`. Ningún componente verifica la identidad semántica del oráculo antes de usarlo como referencia de evaluación en contexto de regresión. |
| **E-4.4-006** | P0 | HITO_4.3 GAP-4.3-01 / GAP-4.3-03 | **Tests de adaptador SealedOracle→evaluación ausentes.** No existe prueba del flujo `SealedOracle` → verificación → evaluador topológico. La conexión es arquitectónicamente simple (ambos operan sobre `Sequence[ASTNode]`), pero no está testeada. |
| **E-4.4-007** | P0 | HITO_4.2 GAP-4.2-02 | **Tests de RegressionVerdict ausentes.** No existen pruebas para PASS/WARNING/HARD_FAIL ni agregación por corpus. No existe `RegressionEvaluationStrategy` ni `RegressionThresholds`. |
| **E-4.4-008** | N/A | HITO_4.1 E-4.1-017 → `tests/unit/test_zhang_shasha.py` | **Suite Zhang-Shasha SOTA (15 funciones, 17 ejecuciones parametrizadas).** Cubre: árboles vacíos, nodos individuales, identidad, inserción/borrado/sustitución atómica, isomorfismo, simetría, violaciones de orden, multi-raíz, profundidad, anchura, escalabilidad hasta 150 nodos. Debe conservarse como baseline matemático. |
| **E-4.4-009** | P1 | HITO_4.1 GAP-4.1-04 | **Tests de normalización de matching ausentes.** No existen pruebas que cubran stripping + Unicode NFC para `NodeMatchingPolicy`. |
| **E-4.4-010** | P1 | HITO_4.1 GAP-4.1-07 | **Tests de framing seguro de matching_key ausentes.** No existe prueba para `text_content` con `:` u otros delimitadores ambiguos. |
| **E-4.4-011** | P1 | HITO_4.3 §16.2 | **Tests de exit code ausentes.** No existe entry point de regresión ni contrato de exit codes verificable por CI. |
| **E-4.4-012** | N/A | `tests/unit/` (Fase 3) | **Tests de identidad y framing de Fase 3 existentes (~137 tests).** `test_framing_injectivity.py` (17), `test_corpus_models.py` (~30), `test_ast_models.py` (~27), `test_oracle_identity.py` (8), `test_manifest_fingerprint.py` (10), `test_ground_truth_completeness.py` (6), `test_ground_truth_lifecycle.py` (~22), `test_ground_truth_sealing_atomicity.py` (~7), `test_ground_truth_sealed_protection.py` (~5), `test_ground_truth_validity.py` (5). Son infraestructura de testing reutilizable para Fase 4. |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-4.4-01 | La suite matemática topológica y la suite de regresión científica son capas distintas. Que `test_zhang_shasha.py` sea SOTA no implica que la regresión contra oráculo sellado esté certificada. | Alto | OPEN |
| OBS-4.4-02 | La regresión científica requiere negative controls. Una suite que solo prueba caminos felices no demuestra que detecta violaciones. | Alto | OPEN |
| OBS-4.4-03 | El bootstrap de golden data puede existir como herramienta manual, pero debe estar excluido del camino crítico de CI. | Alto | OPEN |
| OBS-4.4-04 | Los tests de adapter deben usar puertos fake/in-memory para comprobar contratos sin depender de I/O real, y tests de integración separados para filesystem real. | Medio | OPEN |
| OBS-4.4-05 | Los tests de CLI deben verificar no solo stdout o reporte, sino también exit code, artefacto de salida y comportamiento Fail-Fast. | Medio | OPEN |
| OBS-4.4-06 | Los umbrales NSS siguen siendo hipótesis de trabajo de HITO_4.2. Los tests deben expresar el contrato decidido por ADR/NADR, no fijar arbitrariamente valores no aprobados. | Alto | OPEN |
| OBS-4.4-07 | El CI workflow existe pero ejecuta tests potencialmente defectuosos bajo el marker `regression`. La remediación de los tests defectuosos es prerrequisito para que el CI sea un merge gate confiable. | Alto | OPEN |
| OBS-4.4-08 | La suite de Fase 4 debe distinguir regression fixtures de benchmark fixtures. Reusar `BenchmarkDocument` sin integridad criptográfica reproduciría el gap de HITO_4.3. | Medio | OPEN |
| OBS-4.4-09 | Los ~137 tests de Fase 3 son infraestructura de testing reutilizable. Prueban contratos de identidad, framing, completitud y ciclo de vida que son prerrequisitos para la regresión científica. | Medio | OPEN |
| OBS-4.4-10 | La distinción entre "test del componente X" y "test del componente X integrado en flujo Y" es crítica. `BaselineCompletenessVerifier` tiene tests en contexto de sellado (`test_ground_truth_completeness.py`), pero no tiene tests en contexto de evaluación (antes de evaluar runtime vs oráculo). | Alto | OPEN |

---

## 12. MATRIZ DE TRIAJE

| Artefacto / Componente | Clasificación | Justificación forense |
|---|---|---|
| `test_zhang_shasha.py` | RETAIN | Suite matemática rigurosa y SOTA (15 funciones, 17 ejecuciones parametrizadas). Debe conservarse. |
| `test_structural_metric.py` | RETAIN / TO BE VERIFIED | Útil para rama APTED legacy; su destino depende del benchmark comparativo de HITO_4.1. |
| `test_golden_parser.py` | REWRITE | Tautológico; no es evidencia de regresión. Debe reescribirse soberanamente. |
| `test_chunker_snapshot.py` | REWRITE | Autogeneración y sub-aserción; no es snapshot soberano. |
| `bootstrap_translation_golden.py` | QUARANTINE / MANUAL ONLY | Puede existir como herramienta manual, nunca como camino automático de CI. |
| `.github/workflows/ci.yml` | RETAIN + FIX TESTS | Workflow funcional con protección de oráculos. Debe retenerse pero los tests que ejecuta deben remediarse. |
| `pyproject.toml` | RETAIN | Configuración centralizada existente y funcional. |
| Tests de oracle_hash | CREATE | Bloqueantes para integridad científica. |
| Tests de ground_truth_state | CREATE | Bloqueantes para evitar evaluación contra draft. |
| Tests de completitud biyectiva en evaluación | CREATE | Bloqueantes para baseline completa. (Existen en contexto sellado; faltan en contexto evaluación.) |
| Tests de adapter SealedOracle→evaluación | CREATE | Bloqueantes para GAP-2.0-11. |
| Tests de RegressionVerdict | CREATE | Bloqueantes para DC-07. |
| Tests de criticidad | CREATE | Bloqueantes para DC-06. |
| Tests de NormalizedNodeMatchingPolicy | CREATE | Necesarios para cerrar GAP-4.1-04. |
| Tests de framing matching_key | CREATE | Necesarios para cerrar GAP-4.1-07. |
| Tests de CLI / exit code | CREATE | Necesarios para CI y operación de producción. |
| Tests de identidad y framing (Fase 3) | RETAIN / REUSE | ~137 tests reutilizables como infraestructura de testing. |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Oráculos soberanos e independientes

| Elemento | Estado | Evidencia |
|---|---|---|
| Golden parser soberano | FALTANTE / DEFECTUOSO | E-4.4-001 |
| Snapshot soberano sin autogeneración | FALTANTE / DEFECTUOSO | E-4.4-002 |
| Fixtures sellados con hash | FALTANTE | E-4.4-005 |
| Negative controls | FALTANTE | E-4.4-007 |

**Veredicto del pilar:** No apto para producción. Debe remediarse antes de certificar regresión científica.

### Pilar 2 — Precondiciones criptográficas y de ciclo de vida

| Elemento | Estado | Evidencia |
|---|---|---|
| Test de `oracle_hash` válido | FALTANTE | E-4.4-005 |
| Test de `oracle_hash` inválido | FALTANTE | E-4.4-005 |
| Test de `ground_truth_state == SEALED` | FALTANTE | E-4.4-006 |
| Test de draft/no sealed | FALTANTE | E-4.4-006 |
| Test de completitud biyectiva en evaluación | FALTANTE (existe en sellado) | E-4.4-007 |

**Veredicto del pilar:** Completamente ausente en contexto de evaluación. Bloquea Fase 4. Los tests de completitud existen en contexto de sellado (`test_ground_truth_completeness.py`) pero no en contexto de evaluación.

### Pilar 3 — Regresión graduada

| Elemento | Estado | Evidencia |
|---|---|---|
| Test PASS | FALTANTE | E-4.4-007 |
| Test WARNING | FALTANTE | E-4.4-007 |
| Test HARD_FAIL | FALTANTE | E-4.4-007 |
| Test pérdida CRITICAL | FALTANTE | E-4.4-014 |
| Test NSS thresholds | FALTANTE | E-4.4-007 |
| Test agregación por corpus | FALTANTE | E-4.4-007 |

**Veredicto del pilar:** Completamente ausente. Bloquea DC-07.

### Pilar 4 — Infraestructura topológica testeada

| Elemento | Estado | Evidencia |
|---|---|---|
| Zhang-Shasha unit tests | EXISTENTE SOTA (15 funciones, 17 ejecuciones parametrizadas) | E-4.4-008 |
| StructuralMetric tests | EXISTENTE | HITO_4.1 |
| Normalized matching tests | FALTANTE | E-4.4-009 |
| Framing matching_key tests | FALTANTE | E-4.4-010 |
| Criticality cost tests | FALTANTE | E-4.4-014 |

**Veredicto del pilar:** Base matemática sana; extensiones de Fase 4 no cubiertas.

### Pilar 5 — Entry point y CI gate

| Elemento | Estado | Evidencia |
|---|---|---|
| CLI de regresión | FALTANTE | HITO_4.3 / E-4.4-011 |
| Tests de exit code | FALTANTE | E-4.4-011 |
| CI workflow | EXISTENTE (ejecuta tests potencialmente defectuosos) | E-4.4-003 |
| Configuración centralizada | EXISTENTE | E-4.4-004 |
| Tests de identidad y framing (Fase 3) | EXISTENTE (~137 tests) | E-4.4-012 |

**Veredicto del pilar:** Parcialmente existente. El CI workflow funciona pero ejecuta tests potencialmente defectuosos. La remediación de tests es prerrequisito para que el CI sea confiable.

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-4.4-01** | Golden parser test tautológico/no soberano. No certifica regresión. | E-4.4-001 | Testing / HITO_0.4.4 GAP-0.4-09 | **Fase 4** | OPEN |
| **GAP-4.4-02** | Snapshot de chunking con autogeneración y sub-aserción. | E-4.4-002 | Testing / C5-R01, C5-R02 | **Fase 4** | OPEN |
| **GAP-4.4-03** | CI workflow ejecuta tests potencialmente defectuosos bajo marker `regression`. | E-4.4-003 | CI / DC-10 | **Fase 4** | OPEN |
| **GAP-4.4-05** | Tests de `oracle_hash` ausentes. | E-4.4-005 | Integrity / HITO_4.3 GAP-4.3-02 | **Fase 4** | OPEN |
| **GAP-4.4-06** | Tests de `ground_truth_state == SEALED` ausentes. | E-4.4-006 | Lifecycle / HITO_4.3 | **Fase 4** | OPEN |
| **GAP-4.4-07** | Tests de completitud biyectiva en evaluación ausentes. (Existen en contexto sellado.) | E-4.4-007 | Baseline completeness / HITO_4.3 GAP-4.3-05 | **Fase 4** | OPEN |
| **GAP-4.4-08** | Tests de criticidad por tipo de nodo ausentes. | E-4.4-014 | DC-06 / HITO_4.2 | **Fase 4** | OPEN |
| **GAP-4.4-09** | Tests de veredicto graduado y NSS thresholds ausentes. | E-4.4-007 | DC-07 / HITO_4.2 | **Fase 4** | OPEN |
| **GAP-4.4-10** | Tests de normalización de matching ausentes. | E-4.4-009 | HITO_4.1 GAP-4.1-04 | **Fase 4** | OPEN |
| **GAP-4.4-11** | Tests de framing seguro de matching_key ausentes. | E-4.4-010 | HITO_4.1 GAP-4.1-07 | **Fase 4** | OPEN |
| **GAP-4.4-12** | Tests de CLI / exit codes ausentes. | E-4.4-011 | HITO_4.3 / Entry point | **Fase 4** | OPEN |
| **GAP-4.4-13** | Negative controls / mutation fixtures ausentes. | E-4.4-007 | Testing SOTA | **Fase 4** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-4.4-A | La suite actual de regresión integrada es confiable para Fase 4. | RECHAZADA | E-4.4-001, E-4.4-002, E-4.4-003 | Debe remediarse antes de certificar Scientific Verification. |
| H-4.4-B | Los tests matemáticos topológicos existentes son reutilizables. | CONFIRMADA | E-4.4-008 | Deben conservarse como base SOTA. |
| H-4.4-C | Un golden test tautológico puede servir como evidencia de regresión si pasa establemente. | RECHAZADA | E-4.4-001, principio HITO_0.4.4 | Un test solo es evidencia si falla ante violación del contrato correcto. |
| H-4.4-D | La autogeneración de snapshots en CI es compatible con oráculos soberanos. | RECHAZADA | E-4.4-002 | Bootstrap debe ser manual y fuera de CI. |
| H-4.4-E | Fase 4 requiere negative controls / mutation fixtures. | CONFIRMADA | E-4.4-007, matriz de mutaciones | Sin negative controls no se demuestra sensibilidad de la suite. |
| H-4.4-F | Las pruebas de regresión pueden implementarse como extensión directa de `run_benchmark.py`. | RECHAZADA | HITO_4.3, E-4.4-011 | Benchmark y regresión deben mantenerse separados. |
| H-4.4-G | La ausencia de CI permite aún considerar producción si los tests locales pasan. | RECHAZADA | E-4.4-003 | El CI existe pero ejecuta tests potencialmente defectuosos. Sin tests confiables, el CI no es merge gate efectivo. |
| H-4.4-H | Los tests de Fase 4 deben fijar umbrales 0.80/0.95 inmediatamente. | RECHAZADA | HITO_4.2, OBS-4.4-06 | Los umbrales son hipótesis arbitrarias hasta ADR/NADR y validación empírica. |
| H-4.4-I | Los tests de Fase 3 son reutilizables como infraestructura de testing. | CONFIRMADA | E-4.4-012 | ~137 tests de identidad, framing, completitud y ciclo de vida pueden reutilizarse. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿La construcción de tests actual es SOTA?

**Estado actual verificado:**

1. `test_zhang_shasha.py` sí es SOTA para certificación matemática del motor TED (15 funciones, 17 ejecuciones parametrizadas).
2. `test_golden_parser.py` fue marcado como P0 por tautología.
3. `test_chunker_snapshot.py` fue marcado como P0 por autogeneración y sub-aserción.
4. `.github/workflows/ci.yml` existe y es funcional, con 4 jobs y protección de oráculos.
5. `pyproject.toml` existe y está configurado.
6. No existen tests de `oracle_hash`, `ground_truth_state`, completitud en evaluación, adaptador SealedOracle→evaluación, veredicto graduado ni exit codes.
7. Existen ~137 tests de Fase 3 reutilizables.

**Respuesta forense:**

No, la construcción actual no es SOTA a nivel de regresión científica. Solo la capa matemática unit-level puede considerarse SOTA. La capa de integración/regresión es insuficiente y contiene falsas garantías. El CI existe pero ejecuta tests potencialmente defectuosos.

**Implicación:**

Fase 4 no debe apoyarse en los golden/snapshot tests actuales como certificación. Debe construir una suite nueva de regresión científica basada en oráculos sellados, negative controls y verificación criptográfica. La remediación de tests defectuosos es prerrequisito para que el CI funcione como merge gate confiable.

### 16.2 ¿Cuál es la mejor alternativa real de grado producción?

**Respuesta forense:**

La mejor alternativa real es una suite de regresión científica separada en seis carriles:

| Carril | Objetivo | Criterio de producción |
|---|---|---|
| Unit math | Mantener certificación Zhang-Shasha | Determinismo algebraico y casos borde |
| Unit policy | Criticidad, thresholds, matching, framing | Fixtures mínimos y negativos |
| Contract adapter | SealedOracle→evaluación | Puertos fake/in-memory + Fail-Fast |
| Integration regression | Runtime AST vs SealedOracle | Corpus sellado independiente |
| CLI/entry point | Operabilidad | Reporte + exit code estable |
| CI gate | Bloqueo de merge | Workflow reproducible con tests confiables |

Esta alternativa es superior a un único test end-to-end porque aísla fallas, evita dependencia excesiva de I/O, conserva determinismo y permite negative controls por contrato.

### 16.3 ¿Qué tests son bloqueantes para Fase 4?

**Respuesta forense:**

Son bloqueantes:

1. Test de `oracle_hash` válido e inválido.
2. Test de `ground_truth_state == SEALED` y estado no sellado.
3. Test de completitud biyectiva manifest ↔ oráculos **en contexto de evaluación** (los tests en contexto de sellado ya existen).
4. Test de adaptador SealedOracle→evaluación.
5. Test de pérdida de nodo CRITICAL → HARD_FAIL.
6. Test de pérdida de nodo WARNING → WARNING o contrato final ADR.
7. Test de `RegressionVerdict` y agregación por documento/corpus.
8. Test de NormalizedNodeMatchingPolicy.
9. Test de framing seguro de `matching_key`.
10. Test de CLI / exit code.
11. Test Fail-Fast si falta oráculo/snapshot.
12. Remediación de tests defectuosos para que el CI sea merge gate confiable.

### 16.4 ¿Qué tests deben conservarse?

**Respuesta forense:**

Deben conservarse:

1. `test_zhang_shasha.py`: suite matemática SOTA (15 funciones, 17 ejecuciones parametrizadas).
2. `test_structural_metric.py`: conservar mientras la dualidad core/tools esté pendiente de benchmark comparativo.
3. Tests unitarios de validadores y componentes puros clasificados como excelentes por HITO_0.4.4.
4. Tests de identidad y framing de Fase 3 (~137 tests): infraestructura reutilizable.

### 16.5 ¿Qué tests deben reescribirse?

**Respuesta forense:**

Deben reescribirse:

1. `test_golden_parser.py`: por tautología y/o skip ante oráculo ausente.
2. `test_chunker_snapshot.py`: por autogeneración y sub-aserción.
3. Cualquier test de "real parser pipeline" que use mocks/stubs y se presente como E2E.
4. Cualquier test que derive expected y actual de la misma ejecución.

### 16.6 ¿Cómo debe tratarse el bootstrap de golden data?

**Respuesta forense:**

El bootstrap de golden data puede existir únicamente como herramienta manual, fuera del camino crítico de CI. En CI debe estar prohibida la creación automática de oráculos, snapshots o baselines.

**Regla forense:**

> Si falta el oráculo, el test falla. Si el oráculo cambia, el hash debe cambiar por revisión explícita. Si el test genera el oráculo que luego valida, el test no certifica regresión.

### 16.7 ¿Qué debe probarse respecto a HITO_4.3?

**Respuesta forense:**

Deben probarse todos los prerequisitos del adaptador baseline→benchmark:

1. El consumidor verifica `ground_truth_state == SEALED`.
2. El consumidor usa `hydrate_ground_truth()` solo después de verificar el estado.
3. El consumidor calcula `OracleSemanticIdentityCalculator.calculate(oracle.nodes)`.
4. El consumidor compara el resultado con `CorpusDocumentMetadata.oracle_hash`.
5. El consumidor aborta antes de evaluar si falla cualquier precondición.
6. El consumidor pasa `sealed_oracle.nodes` a los evaluadores existentes.
7. El reporte conserva trazabilidad por `document_id`.

---

## 18. MATRIZ DE TRAZABILIDAD DC / GAP

| DC / GAP | Tema | Evidencia HITO vinculada | Estado operativo | Fase destino |
|---|---|---|---|---|
| **DC-06** | Taxonomía de criticidad | HITO_4.2 GAP-4.2-01, E-4.4-014 | Tests ausentes | Fase 4 |
| **DC-07** | Reglas de regresión graduada | HITO_4.2 GAP-4.2-02, E-4.4-007 | Tests ausentes | Fase 4 |
| **DC-10** | CI / runner desacoplado | E-4.4-003, E-4.4-011, GAP-4.4-03, GAP-4.4-12 | CI existe, tests defectuosos | Fase 4 |
| **GAP-2.0-11** | Adaptador baseline→benchmark | HITO_4.3 E-4.3-001, GAP-4.4-05 a GAP-4.4-07 | Tests ausentes | Fase 4 |
| **GAP-0.4-09** | Golden test tautológico | E-4.4-001, GAP-4.4-01 | Persistente | Fase 4 |
| **C5-R01/C5-R02** | Snapshot autogenerado/sub-aserción | E-4.4-002, GAP-4.4-02 | Persistente | Fase 4 |
| **GAP-4.1-04** | Matching sin normalización | E-4.4-009, GAP-4.4-10 | Tests ausentes | Fase 4 |
| **GAP-4.1-07** | Framing matching_key | E-4.4-010, GAP-4.4-11 | Tests ausentes | Fase 4 |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Falsa confianza por tests tautológicos | Tests que pasan sin oráculo independiente pueden ocultar regresiones críticas. | Alto | E-4.4-001 |
| Oráculos autogenerados en CI | Si CI genera su propio expected, no existe regresión real. | Alto | E-4.4-002 |
| CI ejecuta tests defectuosos | El workflow existe pero puede reportar PASS falso si ejecuta tests tautológicos. | Alto | E-4.4-003 |
| Regresión sin negative controls | Sin mutaciones intencionales, no se sabe si la suite falla cuando debe fallar. | Alto | E-4.4-007 |
| Evaluación contra oráculo mutado | Sin test de hash mismatch, se puede evaluar contra baseline corrupta. | Alto | E-4.4-005 |
| Evaluación contra draft | Sin test de lifecycle, se puede evaluar contra ground truth no sellado. | Alto | E-4.4-006 |
| Umbrales prematuros | Tests que fijen 0.80/0.95 antes del ADR convertirían hipótesis arbitrarias en contrato accidental. | Medio | OBS-4.4-06 |
| Confusión benchmark/regresión | Reusar herramientas de benchmark como si fueran regression gates mezcla objetivos y degrada trazabilidad. | Medio | HITO_4.3 |
| Matching ambiguo no testeado | Sin test de `text_content` con `:`, puede persistir ambigüedad en matching_key. | Medio | E-4.4-010 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR / NADR

Con base en este Discovery, el ADR o NADR posterior deberá responder:

1. ¿Cuál es la taxonomía oficial de test lanes para Fase 4?
2. ¿Qué fixtures componen el corpus mínimo de regresión científica?
3. ¿Cuántos negative controls son obligatorios por contrato crítico?
4. ¿Debe existir un fixture mutado por cada nivel de criticidad?
5. ¿Cómo se almacenan y versionan los oráculos sellados de test?
6. ¿Cómo se impide la autogeneración de oráculos en CI?
7. ¿Cuál es el contrato exacto de exit codes del CLI de regresión?
8. ¿Los warnings bloquean merge o solo reportan degradación?
9. ¿Qué parte corresponde a Fase 4 y qué parte se difiere a Fase 6 CI Automation?
10. ¿Cómo se valida empíricamente que los umbrales NSS elegidos son adecuados?
11. ¿Qué cobertura mínima se exige para `oracle_hash`, `ground_truth_state` y completitud?
12. ¿El benchmark legacy (`run_benchmark.py`) queda fuera del regression gate?
13. ¿Cómo se revisa manualmente una actualización legítima de golden baseline?
14. ¿Qué formato de reporte es obligatorio para auditoría posterior: JSON, Markdown o ambos?
15. ¿Cómo se garantiza que los tests no dependan de network, LLMs, tiempo, orden del filesystem o estado global?
16. ¿Qué tests marcados como `regression` en el CI actual son confiables y cuáles deben remediarse?

---

## 21. CIERRE DEL HITO 4.4

Este HITO confirma que la suite actual no es suficiente para certificar Scientific Verification de grado producción. La base matemática topológica sí es sólida y debe conservarse (15 funciones, 17 ejecuciones parametrizadas). Existe un workflow de CI funcional con protección de oráculos inmutables. Existe también una capa de ~137 tests de Fase 3 reutilizables como infraestructura de testing. Sin embargo, la capa de regresión integrada presenta defectos bloqueantes: golden test tautológico, snapshots degradados, tests potencialmente defectuosos ejecutados por CI, ausencia de tests de integridad criptográfica en contexto de evaluación, ausencia de tests de adaptador SealedOracle→evaluación, ausencia de tests de veredicto graduado y ausencia de negative controls.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** 100% del alcance documental y de evidencia heredada aplicable fue auditado. Todas las evidencias tienen ID estable y severidad. Todos los gaps tienen evidencia vinculada y fase destino. Todas las hipótesis están cerradas como CONFIRMADA o RECHAZADA. Cero hipótesis abiertas sin destino. Las 5 correcciones han sido integradas: pyproject.toml reclasificado como EXISTENTE, CI workflow reclasificado como EXISTENTE con riesgo, tests de Fase 3 reconocidos como infraestructura reutilizable, distinción componente/integración explícita, conteo Zhang-Shasha explícito.
**Verificación de cadena de gobernanza:** ADR_F17_BIS_MASTER → HITO_0.4.4 → HITO_0.4.4_C5 → HITO_4.1 → HITO_4.2 → HITO_4.3 → HITO_4.4 (este documento). Cadena completa verificada.
**Contradicciones con HITOs previos:** Ninguna. Los hallazgos confirman y refinan GAP-0.4-09, C5-R01, C5-R02, GAP-2.0-11, GAP-4.1-04, GAP-4.1-07, GAP-4.2-01, GAP-4.2-02 y GAP-4.3-01.
**Decision Candidates generados:** Ninguno nuevo. Este HITO consolida evidencia para DC-06, DC-07 y DC-10.
**Siguiente paso recomendado:** Construir ADR_F17-BIS_04 (Scientific Verification) y los NADRs de Fase 4, usando HITO_4.1–4.4 como evidencia forense. El Execution Plan de Fase 4 debe materializar primero los prerequisitos de testing soberano antes de declarar cualquier regression gate como producción.