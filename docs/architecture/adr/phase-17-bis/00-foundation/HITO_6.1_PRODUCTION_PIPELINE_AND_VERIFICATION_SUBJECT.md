# HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-09-24
**Fecha de congelamiento:** 2026-09-24
**Fase:** 17-BIS — Fase 6 (Continuous Verification)
**Tipo de artefacto:** Forensic Flow Audit / Dimension Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- ADR_F17_BIS_MASTER.md (FROZEN) §2.1, §6, §10
- ADR_F17_BIS_05.md (FROZEN) §3 D4, §5, §7
- ENGINEERING_PRINCIPLES.md (FROZEN) §II, §IV
- ROADMAP_ARQUITECTONICO_LP.md (FROZEN) — Fase 17_BIS
- HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md v1.0.0 (FROZEN)
- METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN)
- `apps/bootstrap/pipeline_factory.py`
- `apps/bootstrap/provider_factory.py`
- `infra/extraction/providers/pymupdf_provider.py`
- `infra/adapters/pdf_parser.py`
- `core/ast/builder.py`
- `core/pipeline/orchestrator.py`
- `tools/evaluation/run_regression.py`
- `core/benchmark/topology/regression/` (mechanism, strategy, adapter, report)
- `bootstrap/topology.py`
- `tests/integration/test_regression_entry_point.py`
- `tests/integration/test_chunker_snapshot.py`
- `tests/integration/test_golden_parser.py`
- `tests/integration/test_pipeline_orchestration.py`
- `tests/integration/test_real_e2e.py`
- `tests/integration/test_real_paper.py`
- `tests/integration/test_real_parser_pipeline.py`
**Mandato:** ¿Existe hoy un camino de ejecución que atraviese el production pipeline normativo (`build_extraction_pipeline()`) y compare el resultado contra la baseline sellada mediante el mecanismo de regresión topológica (`DoubleProtectionMechanism`)?
**Síntesis:** El Imperative Shell de regresión (`run_regression.py`) SÍ invoca el production pipeline normativo. La correspondencia production ↔ verification es completa en el plano de extracción. La desconexión NO está en el sujeto de verificación sino en la ausencia de invocación efectiva desde CI/tests contra el corpus sellado.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-24 | Emisión inicial. |
| 1.0.0-FROZEN | 2026-09-24 | Cierre formal del HITO. Corrección aplicada: GAP-6.1-05 agregado (delta-regression como capacidad identificada necesaria por DC-6.1). |

---

## 1. RESUMEN EJECUTIVO

Se auditó el sujeto de verificación de Continuous Verification: el production pipeline normativo, el Imperative Shell de regresión, y la correspondencia entre ambos. La auditoría cubrió la composition root de extracción (`build_extraction_pipeline()`), el entry point de regresión (`run_regression.py`), el Functional Core de regresión (`core/benchmark/topology/regression/`), los 6 tests de integración que usan el production pipeline, y el test del entry point de regresión (`test_regression_entry_point.py`).

**Hallazgo central:**

> El Imperative Shell de regresión (`run_regression.py`) SÍ invoca el production pipeline normativo (`build_extraction_pipeline()`) y SÍ ejecuta la extracción real sobre PDFs del corpus canónico. La correspondencia entre production path y verification path es COMPLETA en el plano de extracción. La desconexión identificada en HITO 6.0 (Regression Gate Illusion) NO reside en el sujeto de verificación sino en la ausencia de invocación efectiva: ningún test con marker `regression` invoca `run_regression.py` contra el corpus sellado, y el único test del entry point (`test_regression_entry_point.py`) mockea el production pipeline.

**Defectos dominantes confirmados:**

1. **Test del entry point mockea el SUT (E-6.1-003):** `test_regression_entry_point.py` reemplaza `build_extraction_pipeline()` con un `MagicMock`, por lo que no constituye evidencia de que el production pipeline sea sometido a verificación.
2. **Tests de integración desconectados de la baseline (E-6.1-004):** 6 tests usan `build_extraction_pipeline()` pero ninguno compara contra la baseline sellada ni tiene marker `regression`.
3. **Ausencia de verification boundary explícito (E-6.1-010):** No existe un contrato que defina qué constituye una "ejecución de Continuous Verification" vs un test de integración local.
4. **Ausencia de delta-regression (GAP-6.1-05):** El mecanismo actual implementa solo conformance absoluta. No existe capacidad de delta-regression ni baseline de divergencia, requerida por DC-6.1 para que Continuous Verification sea operativa con el estado actual de Fase 5.

**Hallazgo positivo confirmado:**

5. **Correspondencia production ↔ verification completa (E-6.1-001, E-6.1-002):** `run_regression.py` importa y ejecuta `build_extraction_pipeline()` para cada documento del corpus, cumpliendo NADR-19 §5.5 R20. El sujeto de verificación existe y está correctamente conectado.

**Veredicto:** El sujeto de verificación (production pipeline + baseline sellada + mecanismo topológico) EXISTE y está correctamente ensamblado en `run_regression.py`. El gap NO es arquitectónico (el camino existe) sino operacional (nadie lo invoca efectivamente desde CI). Esto reduce significativamente el scope de Fase 6: no se necesita construir un nuevo sujeto de verificación, sino conectar el existente a la infraestructura CI.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código.

Específicamente, este HITO:
- **NO** decide cómo conectar `run_regression.py` a CI (pertenece a HITO 6.3 / DC-6.3).
- **NO** propone crear un adapter pytest, un wrapper, ni un nuevo entry point.
- **NO** decide si los 6 tests de integración deben ser re-marcados como `regression`.
- **NO** resuelve la materialización de corpus en CI (pertenece a HITO 6.2 / DC-6.2).
- **NO** resuelve la semántica de conformance vs regression (pertenece a DC-6.1).

Este HITO **SÍ**:
- Demuestra que `run_regression.py` invoca `build_extraction_pipeline()`.
- Demuestra qué componentes del production pipeline son atravesados.
- Demuestra que `test_regression_entry_point.py` NO atraviesa el production pipeline.
- Demuestra que los 6 tests de integración NO verifican contra la baseline sellada.
- Produce la matriz de correspondencia production ↔ verification.
- Identifica el verification boundary como gap.
- Identifica la ausencia de delta-regression como gap (GAP-6.1-05).

### 2.2 Método forense

1. Cargar fuentes normativas (ADR Master §2.1, ADR_05 §3 D4, ENGINEERING_PRINCIPLES §II/§IV).
2. Cargar HITO 6.0 como insumo (evidencia de Regression Gate Illusion).
3. Inspeccionar `apps/bootstrap/pipeline_factory.py` para identificar la composition root.
4. Inspeccionar `tools/evaluation/run_regression.py` para verificar invocación del pipeline.
5. Inspeccionar `tests/integration/test_regression_entry_point.py` para verificar uso de mocks.
6. Inspeccionar los 6 tests de integración para verificar relación con la baseline.
7. Separar Observed / Required / Decision.
8. Producir matriz de correspondencia.
9. Consolidar gaps solo con evidencia demostrada.

### 2.3 Axioma de entrada

> **Fase 6 no tiene permiso para "arreglar" silenciosamente aquello que Fase 5 materializó y selló.** El sujeto de verificación construido en Fase 5 (`run_regression.py` + corpus sellado + DoubleProtectionMechanism) es un artefacto certificado operacionalmente. Fase 6 debe conectarlo a CI, no reconstruirlo.

### 2.4 Relación con HITO 6.0

HITO 6.0 demostró la **Regression Gate Illusion**: el CI tiene un job nominal que no ejecuta ninguna verificación. Este HITO determina **si el sujeto que debería ser verificado existe y está correctamente ensamblado**. La respuesta es SÍ: el sujeto existe. El gap está en la invocación, no en el sujeto.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| Composition root de extracción | `apps/bootstrap/pipeline_factory.py` (`build_extraction_pipeline()`, `build_pipeline()`, `build_healing_pipeline()`, `build_document_profiler()`, `_build_context_stack()`) | 100% auditado (estructura) |
| Provider factory | `apps/bootstrap/provider_factory.py` (`ExtractionProviderFactory.create()`) | 100% auditado (estructura) |
| Provider concreto | `infra/extraction/providers/pymupdf_provider.py` (`PyMuPDFProvider`) | Referenciado (auditoría completa en HITO 6.2 si aplica) |
| Parser adapter | `infra/adapters/pdf_parser.py` (`PdfParserAdapter.parse()`) | 100% auditado (estructura) |
| AST builder | `core/ast/builder.py` (`FlatASTBuilder.build()`) | Referenciado |
| Pipeline orchestrator | `core/pipeline/orchestrator.py` (`TranslationPipeline`, `ParserProtocol.parse()`) | Referenciado |
| Regression Imperative Shell | `tools/evaluation/run_regression.py` (`parse_args()`, `main()`) | 100% auditado |
| Regression Functional Core | `core/benchmark/topology/regression/` (mechanism, strategy, adapter, report, models, errors, aggregation) | 100% auditado (estructura) |
| Topology composition root | `bootstrap/topology.py` (`build_canonical_engine_configuration()`, `create_topology_evaluator()`, `DefaultNodeMatchingPolicy`) | 100% auditado (estructura) |
| Regression entry point test | `tests/integration/test_regression_entry_point.py` | 100% auditado |
| Integration tests con production pipeline | `test_chunker_snapshot.py`, `test_golden_parser.py`, `test_pipeline_orchestration.py`, `test_real_e2e.py`, `test_real_paper.py`, `test_real_parser_pipeline.py` | 100% auditado |
| Corpus canónico | `tests/corpus/canonical/` | Referenciado (auditoría completa en HITO 6.2) |
| CI workflow | `.github/workflows/ci.yml` | Referenciado (auditoría completa en HITO 6.0) |

**Fuera de scope:**
- Contenido interno de `PyMuPDFProvider.extract()` (HITO 6.2 si aplica)
- Mecanismo interno de `DoubleProtectionMechanism.evaluate()` (HITO 6.3)
- Semántica de exit codes en detalle (HITO 6.3)
- Materialización de corpus en CI (HITO 6.2)
- Infraestructura CI (HITO 6.3)
- Performance de ejecución (HITO 6.4)

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §2.1 | La baseline evalúa el pipeline de producción, no una ruta aislada |
| ADR (normativa) | `ADR_F17_BIS_05.md` §3 D4, §5, §7 | Motor canónico, frontera Fase 5→6, Target State |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §II, §IV | Functional Core / Imperative Shell, Cero Fallos Silenciosos |
| Roadmap (normativa) | `ROADMAP_ARQUITECTONICO_LP.md` Fase 17_BIS | "Regression Gates: Aserción estricta en CI" |
| HITO previo (forense) | `HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md` | Regression Gate Illusion, gaps de CI |
| Código (runtime) | `apps/bootstrap/pipeline_factory.py` | Composition root de extracción |
| Código (runtime) | `tools/evaluation/run_regression.py` | Imperative Shell de regresión |
| Código (runtime) | `core/benchmark/topology/regression/` | Functional Core de regresión |
| Código (runtime) | `bootstrap/topology.py` | Composition root topológica |
| Test (runtime) | `tests/integration/test_regression_entry_point.py` | Test del entry point (usa mocks) |
| Tests (runtime) | 6 tests de integración con `build_extraction_pipeline()` | Tests que usan el production pipeline |
| PROJECT_TREE (estructura) | `PROJECT_TREE.txt` | Inventario de módulos y símbolos |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Production Execution Path (normativo)

```text
PDF (input físico)
    │
    ▼
build_extraction_pipeline()                    [apps/bootstrap/pipeline_factory.py]
    │
    ├── ExtractionProviderFactory.create()     [apps/bootstrap/provider_factory.py]
    │       │
    │       ▼
    │   PyMuPDFProvider.extract()              [infra/extraction/providers/pymupdf_provider.py]
    │       │
    │       ▼
    │   LayoutBlockCollection                  [core/layout/models.py]
    │
    ├── PdfParserAdapter.parse()               [infra/adapters/pdf_parser.py]
    │       │
    │       ▼
    │   FlatASTBuilder.build()                 [core/ast/builder.py]
    │       │
    │       ▼
    │   ASTNode[] (Flat AST)                   [core/ast/models.py]
    │
    ▼
Candidate AST (artefacto verificable)

Leyenda:
  [OK] componente existente confirmado en PROJECT_TREE
```

**Estado:** [OK] — Todos los componentes existen y están confirmados en el PROJECT_TREE. La composition root `build_extraction_pipeline()` es la única factory de extracción productiva.

### FLUJO B — Regression Verification Path (Imperative Shell)

```text
run_regression.py main()                       [tools/evaluation/run_regression.py]
    │
    ├── parse_args()
    │       --corpus-dir (required)
    │       --pdf-dir (required)
    │       --output-dir
    │       --inject-timestamp
    │
    ├── LoadCorpusManifestUseCase              [core/benchmark/corpus/use_cases.py]
    │       │
    │       ▼
    │   CorpusManifest
    │
    ├── RegressionAdapter.verify_completeness() [core/benchmark/topology/regression/adapter.py]
    │
    ├── build_canonical_engine_configuration()  [bootstrap/topology.py]
    │       │
    │       ▼
    │   ConfigurationFingerprint
    │
    ├── create_topology_evaluator()             [bootstrap/topology.py]
    │       │
    │       ▼
    │   ZhangShashaEngine + CriticalityAwareCostContext
    │
    ├── build_extraction_pipeline()             [apps/bootstrap/pipeline_factory.py] ← SUT NORMATIVO
    │       │
    │       ▼
    │   PdfParserAdapter (production pipeline)
    │
    ├── LocalFileSystemGroundTruthReader        [infra/fs/ground_truth_store.py]
    │
    ├── LoadGroundTruthUseCase                  [core/benchmark/ground_truth/use_cases.py]
    │
    ├── PARA CADA DOCUMENTO:
    │       │
    │       ├── load_gt_uc.execute(doc_id)
    │       │       ▼
    │       │   GroundTruthDraft / SealedOracle
    │       │
    │       ├── hydrate_ground_truth(state=SEALED)
    │       │       ▼
    │       │   SealedOracle
    │       │
    │       ├── adapter.verify_document_identity()
    │       ├── adapter.verify_sealed_state()
    │       ├── adapter.verify_oracle_integrity()
    │       │
    │       ├── extraction_pipeline.parse(pdf_path)  ← EJECUTA PRODUCTION PIPELINE
    │       │       ▼
    │       │   Candidate AST
    │       │
    │       ├── strategy.evaluate_regression()       [core/benchmark/topology/regression/strategy.py]
    │       │       │
    │       │       ├── TreeEditDistanceEvaluator
    │       │       ├── EntityRecallEvaluator (por ContentNodeType)
    │       │       ├── CriticalityVerdictEmitter
    │       │       └── DoubleProtectionMechanism.evaluate()
    │       │               ▼
    │       │           DoubleProtectionResult (PASS / WARNING / HARD_FAIL)
    │       │
    │       └── RegressionEvaluationReport
    │
    ├── build_regression_report()               [core/benchmark/topology/regression/report.py]
    │       ▼
    │   RegressionReport (corpus_verdict, corpus_nss, documents)
    │
    ├── JsonRegressionReportFormatter.format()
    ├── MarkdownRegressionReportFormatter.format()
    │       ▼
    │   regression_report.json / regression_report.md
    │
    └── sys.exit(exit_code)                     [0=PASS, 1=WARNING, 2=HARD_FAIL]

Leyenda:
  [OK] componente existente confirmado
  [SUT] Subject Under Test normativo
```

**Estado:** [OK] — El Imperative Shell de regresión está completamente ensamblado. Invoca `build_extraction_pipeline()` (SUT normativo), ejecuta la extracción real sobre PDFs, verifica la integridad del oráculo sellado, y evalúa mediante el mecanismo topológico canónico.

### FLUJO C — Test del Entry Point (mockeado)

```text
test_regression_entry_point.py                 [tests/integration/test_regression_entry_point.py]
    │
    ├── _make_node()                           → ASTNode sintético
    ├── _make_eval_report()                    → RegressionEvaluationReport sintético
    ├── _make_manifest()                       → CorpusManifest sintético
    ├── _setup_dirs()                          → directorios temporales
    │
    ├── _run_entry_point()
    │       │
    │       ├── patch("...LocalFileSystemCorpusLoader")     → MagicMock
    │       ├── patch("...LoadCorpusManifestUseCase")       → MagicMock
    │       ├── patch("...LocalFileSystemGroundTruthArtifactAdapter") → MagicMock
    │       ├── patch("...LocalFileSystemGroundTruthReader") → MagicMock
    │       ├── patch("...LoadGroundTruthUseCase")          → MagicMock
    │       ├── patch("...build_extraction_pipeline")       → MagicMock ← SUT MOCKEADO
    │       ├── patch("...RegressionEvaluationStrategy")    → MagicMock (opcional)
    │       │
    │       ├── monkeypatch.setattr(sys, "argv", [...])
    │       │
    │       ├── from tools.evaluation.run_regression import main
    │       ├── main()
    │       └── pytest.raises(SystemExit) → exit_code
    │
    └── TestExitCodes / TestFailFast / TestReportFiles / TestParseArgs

Leyenda:
  [MOCK] componente reemplazado por MagicMock
  [SHELL] se verifica el Imperative Shell (CLI, exit codes, reportes)
  [NOT-SUT] el production pipeline NO es ejecutado
```

**Estado:** [SHELL] — El test verifica el Imperative Shell (argument parsing, exit codes, generación de reportes, fail-fast ante baseline incompleta). NO verifica el production pipeline ni la baseline sellada.

### FLUJO D — Tests de integración con production pipeline (sin baseline)

```text
test_chunker_snapshot.py                       → build_extraction_pipeline() → chunking snapshot
test_golden_parser.py                          → build_extraction_pipeline() → fingerprint comparison
test_pipeline_orchestration.py                 → build_extraction_pipeline() → orchestration
test_real_e2e.py                               → build_extraction_pipeline() → E2E con LLM fake
test_real_paper.py                             → build_extraction_pipeline() → parsing + validation
test_real_parser_pipeline.py                   → build_extraction_pipeline() → structural presence

Leyenda:
  [OK] usa production pipeline
  [NO-BASELINE] no compara contra corpus canónico sellado
  [NO-REGRESSION] no tiene marker "regression"
  [NO-TOPOLOGY] no usa DoubleProtectionMechanism
```

**Estado:** [NO-BASELINE] — Estos tests ejercen el production pipeline pero NO lo comparan contra la baseline sellada. Son tests de integración funcional, no de Continuous Verification.

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

### 6.1 Production Path Matrix

| Componente | Implementación observada | Archivo | Símbolo | Estado |
|---|---|---|---|---|
| Composition root de extracción | `build_extraction_pipeline()` | `apps/bootstrap/pipeline_factory.py` | `build_extraction_pipeline` | CONFIRMADO |
| Provider factory | `ExtractionProviderFactory` | `apps/bootstrap/provider_factory.py` | `ExtractionProviderFactory.create()` | CONFIRMADO |
| Provider concreto | `PyMuPDFProvider` | `infra/extraction/providers/pymupdf_provider.py` | `PyMuPDFProvider.extract()` | CONFIRMADO |
| Parser adapter | `PdfParserAdapter` | `infra/adapters/pdf_parser.py` | `PdfParserAdapter.parse()` | CONFIRMADO |
| AST builder | `FlatASTBuilder` | `core/ast/builder.py` | `FlatASTBuilder.build()` | CONFIRMADO |
| Pipeline orchestrator | `TranslationPipeline` | `core/pipeline/orchestrator.py` | `TranslationPipeline` | CONFIRMADO |
| Parser protocol | `ParserProtocol` | `core/pipeline/orchestrator.py` | `ParserProtocol.parse()` | CONFIRMADO |
| AST model | `ASTNode` | `core/ast/models.py` | `ASTNode` | CONFIRMADO |
| Content types | `ContentNodeType` | `core/ast/enums.py` | `ContentNodeType` | CONFIRMADO |
| Translation strategy | `TranslationStrategy` | `core/ast/enums.py` | `TranslationStrategy` | CONFIRMADO |

### 6.2 Verification Path Matrix

| Componente | Implementación observada | Archivo | Símbolo | Estado |
|---|---|---|---|---|
| Regression Imperative Shell | `run_regression.py` | `tools/evaluation/run_regression.py` | `main()` | CONFIRMADO |
| Regression strategy | `RegressionEvaluationStrategy` | `core/benchmark/topology/regression/strategy.py` | `evaluate_regression()` | CONFIRMADO |
| Double protection mechanism | `DoubleProtectionMechanism` | `core/benchmark/topology/regression/mechanism.py` | `evaluate()` | CONFIRMADO |
| Regression adapter | `RegressionAdapter` | `core/benchmark/topology/regression/adapter.py` | `verify_all()` | CONFIRMADO |
| Regression report | `RegressionReport` | `core/benchmark/topology/regression/report.py` | `build_regression_report()` | CONFIRMADO |
| Topology composition root | `build_canonical_engine_configuration()` | `bootstrap/topology.py` | `build_canonical_engine_configuration` | CONFIRMADO |
| Topology evaluator factory | `create_topology_evaluator()` | `bootstrap/topology.py` | `create_topology_evaluator` | CONFIRMADO |
| Tree edit engine | `ZhangShashaEngine` | `core/benchmark/topology/engines/zhang_shasha/engine.py` | `ZhangShashaEngine.compute()` | CONFIRMADO |
| Criticality cost context | `CriticalityAwareCostContext` | `core/benchmark/topology/criticality/costs.py` | `CriticalityAwareCostContext` | CONFIRMADO |
| Criticality verdict emitter | `CriticalityVerdictEmitter` | `core/benchmark/topology/criticality/verdict.py` | `CriticalityVerdictEmitter.evaluate()` | CONFIRMADO |
| TED evaluator | `TreeEditDistanceEvaluator` | `core/benchmark/topology/evaluators/ted.py` | `TreeEditDistanceEvaluator.evaluate()` | CONFIRMADO |
| Entity recall evaluator | `EntityRecallEvaluator` | `core/benchmark/topology/evaluators/recall.py` | `EntityRecallEvaluator.evaluate()` | CONFIRMADO |
| Node matching policy | `DefaultNodeMatchingPolicy` | `bootstrap/topology.py` | `DefaultNodeMatchingPolicy` | CONFIRMADO |
| Corpus manifest loader | `LoadCorpusManifestUseCase` | `core/benchmark/corpus/use_cases.py` | `execute()` | CONFIRMADO |
| Ground truth loader | `LoadGroundTruthUseCase` | `core/benchmark/ground_truth/use_cases.py` | `execute()` | CONFIRMADO |
| Ground truth reader | `LocalFileSystemGroundTruthReader` | `infra/fs/ground_truth_store.py` | `load_ground_truth()` | CONFIRMADO |
| Corpus loader | `LocalFileSystemCorpusLoader` | `infra/fs/corpus_repository.py` | `load_raw_manifest()` | CONFIRMADO |
| Ground truth hydration | `hydrate_ground_truth()` | `core/benchmark/ground_truth/models.py` | `hydrate_ground_truth` | CONFIRMADO |
| Sealed oracle type | `SealedOracle` | `core/benchmark/ground_truth/models.py` | `SealedOracle` | CONFIRMADO |

### 6.3 Verification Correspondence Matrix

| Boundary | Production | Verification (run_regression.py) | Correspondencia | Evidencia |
|---|---|---|---|---|
| Input PDF | PDF físico | PDF desde `--pdf-dir` | ✅ IDÉNTICO | E-6.1-002 |
| Pipeline factory | `build_extraction_pipeline()` | `build_extraction_pipeline()` | ✅ IDÉNTICO | E-6.1-001 |
| Provider factory | `ExtractionProviderFactory.create()` | Vía `build_extraction_pipeline()` | ✅ IDÉNTICO | E-6.1-001 |
| Provider concreto | `PyMuPDFProvider` | Vía factory | ✅ IDÉNTICO | E-6.1-001 |
| Parser adapter | `PdfParserAdapter.parse()` | Vía pipeline | ✅ IDÉNTICO | E-6.1-002 |
| AST builder | `FlatASTBuilder.build()` | Vía pipeline | ✅ IDÉNTICO | E-6.1-002 |
| Output AST | `ASTNode[]` | `ASTNode[]` (candidate) | ✅ IDÉNTICO | E-6.1-002 |
| Oracle | N/A (producción no tiene oracle) | `SealedOracle` desde GT | ⚠️ SOLO VERIFICATION | E-6.1-005 |
| Topology evaluation | N/A (producción no evalúa) | `DoubleProtectionMechanism` | ⚠️ SOLO VERIFICATION | E-6.1-005 |
| Criticality | N/A | `CriticalityAwareCostContext` | ⚠️ SOLO VERIFICATION | E-6.1-005 |
| Configuration | N/A | `build_canonical_engine_configuration()` | ⚠️ SOLO VERIFICATION | E-6.1-006 |
| Report | N/A | `regression_report.json/md` | ⚠️ SOLO VERIFICATION | E-6.1-006 |
| Exit code | N/A | `sys.exit(0/1/2)` | ⚠️ SOLO VERIFICATION | E-6.1-006 |
| Delta-regression | N/A | N/A (no existe) | ❌ AUSENTE EN AMBOS | GAP-6.1-05 |

**Conclusión de la matriz:** La correspondencia en el plano de extracción (PDF → pipeline → AST) es COMPLETA. Los componentes adicionales del verification path (oracle, topology, criticality, report) son propios de la verificación y no tienen contraparte en producción. Esto es correcto por diseño: producción extrae, verificación compara. La capacidad de delta-regression está ausente en ambos planos y requiere decisión arquitectónica (DC-6.1).

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| `run_regression.py` invoca `build_extraction_pipeline()` | `from apps.bootstrap.pipeline_factory import build_extraction_pipeline`; `extraction_pipeline = build_extraction_pipeline()` | NADR-19 §5.5 R20: "Reutiliza build_extraction_pipeline() para generar runtime AST" | Fase 4 implementó el Imperative Shell con esta invocación | COMPLIANT | E-6.1-001 |
| `run_regression.py` ejecuta extracción real sobre PDFs | `runtime_ast = extraction_pipeline.parse(str(pdf_path))` | ADR Master §2.1: la baseline evalúa el pipeline de producción | Fase 4 implementó la ejecución por documento | COMPLIANT | E-6.1-002 |
| `run_regression.py` verifica integridad del oráculo | `adapter.verify_document_identity()`, `verify_sealed_state()`, `verify_oracle_integrity()` | NADR-21 §5.4 R19: inmutabilidad de Sealed | Fase 5 implementó las verificaciones | COMPLIANT | E-6.1-005 |
| `run_regression.py` usa motor canónico | `build_canonical_engine_configuration()`, `create_topology_evaluator()` | ADR_05 §3 D4: ZhangShasha + CriticalityAwareCostContext | Fase 4 implementó la composición canónica | COMPLIANT | E-6.1-006 |
| `test_regression_entry_point.py` ejecuta production pipeline | Mockea `build_extraction_pipeline()` con `MagicMock` | El test del verification subject debería ejecutar el SUT real | El test fue diseñado para verificar el Imperative Shell (CLI, exit codes), no el SUT | DISCREPANCY (parcial) | E-6.1-003 |
| Tests de integración verifican contra baseline sellada | 6 tests usan `build_extraction_pipeline()` pero no comparan contra corpus sellado | ROADMAP: "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos" | Estos tests fueron creados para verificación funcional, no para regresión topológica | DISCREPANCY | E-6.1-004 |
| Existe verification boundary explícito | No existe un contrato que defina "ejecución de Continuous Verification" | Implícito en ADR Master §6 y ADR_05 §5 | No decidido previamente | MISSING | E-6.1-010 |
| `run_regression.py` es invocable desde CI | El entry point existe y es funcional, pero CI no lo invoca | ADR_05 §5: "La Fase 6 integra estos artefactos en el pipeline de CI/CD" | Fase 5 difirió la integración a Fase 6 | COMPLIANT (Fase 5) / PENDING (Fase 6) | E-6.1-007 |
| Existe capacidad de delta-regression | No existe en el código. Solo conformance absoluta (candidate ↔ oracle). | DC-6.1 identificará si es necesaria | No decidido previamente | MISSING | GAP-6.1-05 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-6.1-001** | P2 | `tools/evaluation/run_regression.py` → `from apps.bootstrap.pipeline_factory import build_extraction_pipeline`; `extraction_pipeline = build_extraction_pipeline()` | **run_regression.py invoca el SUT normativo.** El Imperative Shell importa y ejecuta `build_extraction_pipeline()`, cumpliendo NADR-19 §5.5 R20. |
| **E-6.1-002** | P2 | `tools/evaluation/run_regression.py` → `runtime_ast = extraction_pipeline.parse(str(pdf_path))` | **Ejecución real del production pipeline.** Para cada documento del corpus, el Imperative Shell ejecuta la extracción real sobre el PDF correspondiente. |
| **E-6.1-003** | P1 | `tests/integration/test_regression_entry_point.py` → `patch("tools.evaluation.run_regression.build_extraction_pipeline", return_value=mock_pipeline)` | **Test del entry point mockea el SUT.** El único test de `run_regression.py` reemplaza `build_extraction_pipeline()` con un `MagicMock`. Verifica el Imperative Shell (CLI, exit codes, reportes) pero NO el production pipeline. |
| **E-6.1-004** | P1 | `tests/integration/test_chunker_snapshot.py`, `test_golden_parser.py`, `test_pipeline_orchestration.py`, `test_real_e2e.py`, `test_real_paper.py`, `test_real_parser_pipeline.py` → `build_extraction_pipeline()` sin marker `regression` | **Tests de integración desconectados de la baseline.** 6 tests usan el production pipeline pero ninguno compara contra la baseline sellada ni tiene marker `regression`. |
| **E-6.1-005** | P2 | `tools/evaluation/run_regression.py` → `adapter.verify_document_identity(oracle, doc_metadata)`; `adapter.verify_sealed_state(doc_metadata)`; `adapter.verify_oracle_integrity(oracle, doc_metadata)` | **Verificación de integridad del oráculo.** El Imperative Shell verifica identidad, estado sellado e integridad de cada oráculo antes de evaluar. |
| **E-6.1-006** | P2 | `tools/evaluation/run_regression.py` → `config = build_canonical_engine_configuration(matching_policy=matching_policy, cost_context=cost_context)`; `config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)` | **Composición canónica verificada.** El Imperative Shell construye la configuración canónica del motor topológico y calcula su fingerprint. |
| **E-6.1-007** | P2 | `tools/evaluation/run_regression.py` → `parse_args()` con `--corpus-dir` (required), `--pdf-dir` (required) | **Entry point funcional con configuración explícita.** El Imperative Shell requiere configuración explícita del corpus y los PDFs (GAP-5.0-03 resuelto). |
| **E-6.1-008** | P2 | `apps/bootstrap/pipeline_factory.py` → `build_extraction_pipeline()` | **Única composition root de extracción.** No existe otra factory de extracción productiva. `build_extraction_pipeline()` es el único punto de composición. |
| **E-6.1-009** | P2 | `infra/adapters/pdf_parser.py` → `PdfParserAdapter.parse()` | **Parser adapter como interfaz del pipeline.** `PdfParserAdapter.parse()` es el método de entrada del pipeline de extracción. |
| **E-6.1-010** | P1 | Búsqueda exhaustiva en `core/`, `tools/`, `tests/` → no existe contrato de "verification subject" | **Verification boundary ausente.** No existe un contrato explícito que defina qué constituye una "ejecución de Continuous Verification" vs un test de integración local. |
| **E-6.1-011** | P2 | `core/benchmark/topology/regression/strategy.py` → `RegressionEvaluationStrategy.evaluate_regression(document_id, candidate_ast, ground_truth_ast)` | **Estrategia de regresión con firma explícita.** La estrategia recibe candidate AST y ground truth AST como argumentos separados, confirmando la separación production/verification. |
| **E-6.1-012** | P2 | `core/benchmark/topology/regression/mechanism.py` → `DoubleProtectionMechanism.evaluate(nss_score, criticality_verdict)` | **Mecanismo de doble protección con firma explícita.** El mecanismo recibe NSS y veredicto de criticidad, confirmando que opera sobre resultados de evaluación, no sobre el pipeline directamente. |

### Evidencia E-6.1-001: run_regression.py invoca el SUT normativo

* **Archivo Fuente Primario:** `tools/evaluation/run_regression.py`
* **Símbolo Auditado:** `main()` — importación y uso de `build_extraction_pipeline`
* **Declaración Observada:**

```python
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
# ...
extraction_pipeline = build_extraction_pipeline()
# ...
runtime_ast = extraction_pipeline.parse(str(pdf_path))
```

* **Observed:** El Imperative Shell de regresión importa `build_extraction_pipeline` de la composition root productiva y lo ejecuta para cada documento del corpus.
* **Required:** NADR-19 §5.5 R20: "Reutiliza build_extraction_pipeline() para generar runtime AST." ADR Master §2.1: "La Scientific Baseline se convierte en la referencia canónica contra la cual se evalúa el comportamiento funcional y estructural del pipeline de producción."
* **Decision:** Fase 4 implementó el Imperative Shell con esta invocación. No existe decisión previa que contradiga esta implementación.
* **Hallazgo Forense:** El sujeto de verificación está correctamente conectado. `run_regression.py` NO usa un parser aislado, un provider directo, ni una ruta legacy. Usa la composition root productiva normativa.
* **Consecuencia Arquitectónica:** La "Ilusión del Benchmark" de Fase 0 NO se repite en el Imperative Shell de regresión. El camino de verificación atraviesa el mismo pipeline que producción.
* **Estado:** OPEN (confirmado como COMPLIANT)

### Evidencia E-6.1-003: Test del entry point mockea el SUT

* **Archivo Fuente Primario:** `tests/integration/test_regression_entry_point.py`
* **Símbolo Auditado:** `_run_entry_point()` — patch de `build_extraction_pipeline`
* **Declaración Observada:**

```python
mock_pipeline = MagicMock(spec=PdfParserAdapter)
mock_pipeline.parse.return_value = list(nodes)

patches = [
    # ...
    patch(
        "tools.evaluation.run_regression.build_extraction_pipeline",
        return_value=mock_pipeline,
    ),
]
```

* **Observed:** El test reemplaza `build_extraction_pipeline()` con un `MagicMock` que retorna `nodes` sintéticos. El production pipeline real NO es ejecutado.
* **Required:** Si este test pretende representar el verification subject, debería ejecutar el production pipeline real contra la baseline sellada.
* **Decision:** El test fue diseñado para verificar el Imperative Shell (CLI parsing, exit codes, generación de reportes, fail-fast ante baseline incompleta). No fue diseñado para verificar el production pipeline.
* **Hallazgo Forense:** `test_regression_entry_point.py` es un test del **Imperative Shell**, no del **verification subject**. Esto es válido como test de CLI, pero NO constituye evidencia de Continuous Verification. El problema no es "usar mocks" sino interpretar este test como prueba de que el production pipeline está siendo verificado.
* **Consecuencia Arquitectónica:** Si el CI ejecutara este test como "regression gate", estaría verificando el shell pero no el pipeline. Esto es una variante de la Regression Gate Illusion a nivel de test.
* **Estado:** OPEN

### Evidencia E-6.1-010: Verification boundary ausente

* **Archivo Fuente Primario:** Búsqueda exhaustiva en `core/`, `tools/`, `tests/`
* **Símbolo Auditado:** Ningún contrato, protocolo, o tipo que defina "verification subject" o "continuous verification execution"
* **Declaración Observada:** No existe en el codebase un contrato que distinga:
  - Una ejecución de Continuous Verification (production pipeline + baseline sellada + mecanismo topológico + evidencia)
  - Un test de integración que usa el production pipeline para otro propósito
  - Un test del Imperative Shell que mockea el pipeline
* **Observed:** La distinción entre estos tres tipos de ejecución es implícita y depende de la convención del desarrollador.
* **Required:** ADR Master §6: "Continuous Verification (Integración definitiva en CI Gates)." ROADMAP: "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos." Ambos implican que debe existir una definición clara de qué constituye una ejecución de Continuous Verification.
* **Decision:** No existe decisión previa que defina este boundary.
* **Hallazgo Forense:** El verification boundary es un gap arquitectónico. Sin un contrato explícito, es posible que tests que no verifican la baseline sean interpretados como regression gates, o que tests que sí la verifican no sean reconocidos como tales.
* **Consecuencia Arquitectónica:** Este gap alimenta la Regression Gate Illusion (HITO 6.0). Sin un boundary explícito, el marker `regression` puede ser aplicado a tests que no verifican la baseline, creando una falsa sensación de protección.
* **Estado:** OPEN

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-6.1-01 | `run_regression.py` tiene un flag `--inject-timestamp` que "rompe determinismo estricto" (según docstring). Este flag es usado en la ejecución de FINAL EVALUATION de Fase 5. En CI, el determinismo estricto podría ser preferible. | Bajo | OPEN |
| OBS-6.1-02 | Los 6 tests de integración que usan `build_extraction_pipeline()` fueron creados en fases anteriores (Fase 4, integración) con propósitos funcionales. No fueron diseñados como regression gates. Re-marcarlos como `regression` sin verificar que comparan contra la baseline sería incorrecto. | Medio | OPEN |
| OBS-6.1-03 | `test_regression_entry_point.py` tiene 4 clases de tests: `TestExitCodes`, `TestFailFast`, `TestReportFiles`, `TestParseArgs`. Todas verifican el Imperative Shell. Ninguna verifica el production pipeline. Esto es consistente con el diseño de test de CLI. | Bajo | OPEN |
| OBS-6.1-04 | `PdfParserAdapter` está en `infra/adapters/` y tiene método `parse()`. El `ParserProtocol` en `core/pipeline/orchestrator.py` define `parse()` como interfaz. La correspondencia entre ambos está confirmada por el PROJECT_TREE pero no se inspeccionó el código de `PdfParserAdapter.parse()` en detalle. | Bajo | OPEN |
| OBS-6.1-05 | `build_extraction_pipeline()` es una de 5 funciones en `pipeline_factory.py`. Las otras son `build_healing_pipeline()`, `build_pipeline()`, `build_document_profiler()`, `_build_context_stack()`. Solo `build_extraction_pipeline()` es relevante para Continuous Verification de extracción. | Bajo | OPEN |
| OBS-6.1-06 | `core/pipeline/orchestrator.py` contiene `TranslationPipeline` que orquesta parser + chunker + dispatcher. Para Continuous Verification de extracción, solo el parser es relevante. El chunker y dispatcher son etapas posteriores del pipeline de traducción. | Bajo | OPEN |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-6.1-01** | El Imperative Shell de regresión está correctamente conectado al production pipeline, pero NO existe ningún test con marker `regression` que lo invoque contra el corpus sellado. El sujeto existe pero nadie lo ejecuta en CI. | E-6.1-001, E-6.1-002, E-6.1-004, HITO 6.0 E-6.0-001 | Pilar: Verification Subject / NADR-19 §5.5 R20 | **Fase 6** | BLOCKING |
| **GAP-6.1-02** | `test_regression_entry_point.py` mockea el production pipeline. Es un test válido del Imperative Shell pero NO constituye evidencia de Continuous Verification. Si se interpreta como regression gate, crea una variante de la Regression Gate Illusion a nivel de test. | E-6.1-003 | Pilar: Verification Subject / ADR Master §2.1 | **Fase 6** | OPEN |
| **GAP-6.1-03** | Los 6 tests de integración que usan `build_extraction_pipeline()` no comparan contra la baseline sellada. Son tests funcionales, no regression gates. Re-marcarlos como `regression` sin verificación sería incorrecto. | E-6.1-004 | Pilar: Verification Subject / ROADMAP | **Fase 6** | OPEN |
| **GAP-6.1-04** | No existe un verification boundary explícito: ningún contrato define qué constituye una "ejecución de Continuous Verification" vs un test de integración local vs un test del Imperative Shell. | E-6.1-010 | Pilar: Verification Boundary / ADR Master §6 | **Fase 6 (DC)** | OPEN |
| **GAP-6.1-05** | El mecanismo actual implementa solo conformance absoluta (candidate ↔ oracle). No existe capacidad de delta-regression ni baseline de divergencia. Esta capacidad es identificada como necesaria por DC-6.1 para que Continuous Verification sea operativa con el estado actual de Fase 5 (163 Critical FN, NSS 0.7208 < 0.80). Sin delta-regression, el mecanismo siempre emitirá HARD_FAIL. | E-6.1-011, E-6.1-012, HITO 6.0 E-6.0-009 | Pilar: Semántica Operacional / DC-6.1 | **Fase 6 (DC)** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-6.1-A | `run_regression.py` es el único Imperative Shell que conecta production pipeline con baseline sellada. | CONFIRMADA | E-6.1-001, E-6.1-002, E-6.1-005, E-6.1-006. No existe otro entry point que combine `build_extraction_pipeline()` + corpus sellado + DoubleProtectionMechanism. | El sujeto de verificación ya existe. Fase 6 no necesita construir un nuevo sujeto, sino conectar el existente a CI. |
| H-6.1-B | Los 6 tests de integración podrían ser adaptados como regression tests. | TO BE VERIFIED | E-6.1-004. Los tests usan el production pipeline pero no comparan contra la baseline. Para adaptarlos, necesitarían: (a) comparar contra corpus sellado, (b) usar DoubleProtectionMechanism, (c) generar evidencia. Esto podría ser más trabajo que invocar `run_regression.py` directamente. Destino: HITO 6.3 / DC-6.3. | No se puede asumir que re-marcar tests existentes es suficiente. Puede ser más simple invocar el Imperative Shell existente. |
| H-6.1-C | `test_regression_entry_point.py` es un test del Imperative Shell, no del verification subject. | CONFIRMADA | E-6.1-003. El test mockea `build_extraction_pipeline()` y verifica CLI parsing, exit codes, reportes. No ejecuta el production pipeline. | El test es válido para lo que fue diseñado (test de CLI). No debe ser interpretado como evidencia de Continuous Verification. |
| H-6.1-D | La correspondencia production ↔ verification es completa en el plano de extracción. | CONFIRMADA | E-6.1-001, E-6.1-002, E-6.1-008, E-6.1-009. `run_regression.py` usa la misma composition root, el mismo provider, el mismo parser, el mismo AST builder que producción. | No hay divergencia entre el pipeline productivo y el pipeline de verificación. La "Ilusión del Benchmark" de Fase 0 no se repite aquí. |
| H-6.1-E | Existe un componente intermedio entre `build_extraction_pipeline()` y el AST que podría quedar fuera de la verificación. | RECHAZADA | E-6.1-002. `extraction_pipeline.parse(str(pdf_path))` retorna directamente el AST. No hay transformación intermedia observable en el código del Imperative Shell. | El camino PDF → pipeline → AST es directo. No hay etapas ocultas. |
| H-6.1-F | El verification boundary podría definirse como un protocolo/tipo en el dominio. | TO BE VERIFIED | E-6.1-010. No existe actualmente. Definirlo requeriría una decisión arquitectónica (DC). Destino: DC-6.7 / ADR_F17_BIS_06. | No se puede implementar sin decisión normativa previa. |
| H-6.1-G | La ausencia de delta-regression impide que Continuous Verification sea operativa con el estado actual de Fase 5. | TO BE VERIFIED | GAP-6.1-05. Con 163 Critical FN y precedencia CRITICAL, el mecanismo siempre emite HARD_FAIL. Sin delta-regression, el gate sería inoperativo. Destino: DC-6.1 / HITO 6.3. | DC-6.1 debe determinar si la solución es delta-regression, recalibración, re-baseline, u otra. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Existe hoy un camino de ejecución que atraviese el production pipeline normativo y compare contra la baseline sellada?

**Estado actual verificado:**

1. `run_regression.py` importa y ejecuta `build_extraction_pipeline()` (E-6.1-001).
2. Para cada documento del corpus, ejecuta `extraction_pipeline.parse(str(pdf_path))` (E-6.1-002).
3. Verifica identidad, estado sellado e integridad del oráculo (E-6.1-005).
4. Usa `build_canonical_engine_configuration()` y `create_topology_evaluator()` (E-6.1-006).
5. Evalúa mediante `RegressionEvaluationStrategy.evaluate_regression()` que usa `DoubleProtectionMechanism` (E-6.1-011, E-6.1-012).
6. Genera `regression_report.json/md` y retorna exit code 0/1/2 (E-6.1-007).

**Respuesta forense:**

SÍ. El camino existe y está completamente ensamblado:

```text
run_regression.py --corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf
    → build_extraction_pipeline()          [production pipeline normativo]
    → extraction_pipeline.parse(pdf)       [extracción real]
    → SealedOracle (desde GT sellado)      [baseline sellada]
    → DoubleProtectionMechanism.evaluate() [mecanismo topológico canónico]
    → RegressionReport                     [evidencia]
    → exit code 0/1/2                      [semántica de fallo]
```

Este camino fue construido en Fase 4 y verificado en Fase 5. Es el sujeto de verificación de Continuous Verification.

**Implicación:**

Fase 6 NO necesita construir un nuevo sujeto de verificación. El sujeto existe. Lo que Fase 6 debe hacer es:
1. Conectar este sujeto a la infraestructura CI (DC-6.3).
2. Resolver la materialización del corpus en CI (DC-6.2).
3. Definir el verification boundary explícito (DC-6.7).
4. Determinar la semántica de regresión (DC-6.1).
5. Determinar si se requiere delta-regression para operatividad (DC-6.1 / GAP-6.1-05).

### 16.2 ¿El Imperative Shell de regresión (`run_regression.py`) invoca el production pipeline normativo?

**Estado actual verificado:**

1. `from apps.bootstrap.pipeline_factory import build_extraction_pipeline` (E-6.1-001).
2. `extraction_pipeline = build_extraction_pipeline()` (E-6.1-001).
3. `runtime_ast = extraction_pipeline.parse(str(pdf_path))` (E-6.1-002).

**Respuesta forense:**

SÍ. `run_regression.py` invoca `build_extraction_pipeline()` directamente. No usa un parser aislado, un provider directo, ni una ruta legacy. Cumple NADR-19 §5.5 R20.

**Implicación:**

La correspondencia production ↔ verification es completa en el plano de extracción. La "Ilusión del Benchmark" de Fase 0 (donde el benchmark medía una ruta legacy aislada) NO se repite en el Imperative Shell de regresión.

### 16.3 ¿`test_regression_entry_point.py` verifica el production pipeline?

**Estado actual verificado:**

1. El test mockea `build_extraction_pipeline()` con `MagicMock(spec=PdfParserAdapter)` (E-6.1-003).
2. El test verifica CLI parsing, exit codes, generación de reportes, fail-fast (E-6.1-003).
3. El test NO ejecuta el production pipeline real.

**Respuesta forense:**

NO. `test_regression_entry_point.py` es un test del **Imperative Shell** (CLI, exit codes, reportes), no del **verification subject**. Es un test válido para lo que fue diseñado, pero NO constituye evidencia de que el production pipeline esté siendo sometido a Continuous Verification.

**Implicación:**

Si el CI ejecutara este test como "regression gate", estaría verificando el shell pero no el pipeline. Esto es una variante de la Regression Gate Illusion a nivel de test. El marker `regression` no debería aplicarse a este test como sustituto de una verificación real.

### 16.4 ¿Los 6 tests de integración que usan `build_extraction_pipeline()` verifican contra la baseline sellada?

**Estado actual verificado:**

1. Los 6 tests usan `build_extraction_pipeline()` (E-6.1-004).
2. Ninguno compara contra el corpus canónico sellado (E-6.1-004).
3. Ninguno usa `DoubleProtectionMechanism` (E-6.1-004).
4. Ninguno tiene marker `regression` (HITO 6.0 E-6.0-003).

**Respuesta forense:**

NO. Los 6 tests son tests de integración funcional que ejercen el production pipeline para propósitos específicos (chunking snapshot, golden parser fingerprint, orchestration, E2E con LLM fake, parsing + validation, structural presence). No son regression gates.

**Implicación:**

Re-marcar estos tests como `regression` sin verificar que comparan contra la baseline sería incorrecto y crearía una falsa sensación de protección. Si se desea que estos tests participen en Continuous Verification, necesitarían ser modificados para comparar contra la baseline sellada, o se necesitaría crear tests nuevos que invoquen `run_regression.py` contra el corpus sellado.

### 16.5 ¿Qué componente produce el artefacto que se compara contra el Ground Truth?

**Estado actual verificado:**

1. `build_extraction_pipeline()` retorna un `PdfParserAdapter` (E-6.1-008, E-6.1-009).
2. `PdfParserAdapter.parse(pdf_path)` retorna el AST (E-6.1-009).
3. El AST es el artefacto que se compara contra el Ground Truth (E-6.1-011).

**Respuesta forense:**

El artefacto verificable es el **AST** (secuencia de `ASTNode[]`), producido por `PdfParserAdapter.parse()` que internamente usa `PyMuPDFProvider.extract()` y `FlatASTBuilder.build()`. Este AST es el "candidate" que se compara contra el "SealedOracle" (Ground Truth sellado).

**Implicación:**

El boundary de verificación es: **PDF → AST (candidate) vs SealedOracle (ground truth)**. Todo lo que está antes del AST (provider, parser, builder) es parte del sujeto de verificación. Todo lo que está después del AST (chunking, translation, assembly, compilation) está fuera del scope de Continuous Verification de extracción.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-6.1** | Semántica de Continuous Verification: conformance vs regression vs baseline de divergencia vs ambas | HITO 6.0 E-6.0-009, GAP-6.0-05; HITO 6.1 E-6.1-011, E-6.1-012, GAP-6.1-05 | Ausente (solo conformance absoluta existe) | **Fase 6** |
| **DC-6.3** | Frontera CI ↔ dominio: pytest marker vs invocación directa vs wrapper | HITO 6.0 E-6.0-001, E-6.0-002; HITO 6.1 E-6.1-001, E-6.1-007, GAP-6.1-01 | Ausente | **Fase 6** |
| **DC-6.7** | Verification boundary: ¿debe existir un contrato explícito que defina "ejecución de Continuous Verification"? | E-6.1-010, GAP-6.1-04 | Ausente | **Fase 6** |
| **DC-6.8** | ¿Debe existir un test de integración que ejecute `run_regression.py` contra el corpus sellado como smoke test? | E-6.1-003, E-6.1-004, GAP-6.1-01, GAP-6.1-02, GAP-6.1-03 | Ausente | **Fase 6** |

> **Nota de gobernanza:** DC-6.7 y DC-6.8 son nuevos, generados por este HITO. No resuelven nada; identifican decisiones que el ADR/NADR de Fase 6 deberá tomar.

---

## 21. CIERRE DEL HITO 6.1

Este HITO confirma que **el sujeto de verificación de Continuous Verification EXISTE y está correctamente ensamblado**. El Imperative Shell de regresión (`run_regression.py`) invoca el production pipeline normativo (`build_extraction_pipeline()`), ejecuta la extracción real sobre PDFs del corpus canónico, verifica la integridad de los oráculos sellados, evalúa mediante el mecanismo topológico canónico (`DoubleProtectionMechanism`), y produce evidencia con semántica de fallo diferenciada.

La correspondencia production ↔ verification es COMPLETA en el plano de extracción. La "Ilusión del Benchmark" de Fase 0 NO se repite en el Imperative Shell de regresión.

El gap NO es arquitectónico (el camino existe) sino operacional:
1. Ningún test con marker `regression` invoca el Imperative Shell contra el corpus sellado (GAP-6.1-01).
2. El único test del entry point mockea el production pipeline (GAP-6.1-02).
3. Los 6 tests de integración que usan el production pipeline no verifican contra la baseline (GAP-6.1-03).
4. No existe un verification boundary explícito (GAP-6.1-04).
5. No existe capacidad de delta-regression, requerida por DC-6.1 para operatividad con el estado actual de Fase 5 (GAP-6.1-05).

Esto reduce significativamente el scope de Fase 6: no se necesita construir un nuevo sujeto de verificación, sino conectar el existente a la infraestructura CI y definir el boundary explícito.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** Todas las condiciones de METHODOLOGY_FOR_FORENSIC_HITOs.md §8.1 verificadas:
- [x] Metadata completa y consistente.
- [x] Changelog actualizado a la versión de cierre.
- [x] Límite epistemológico declarado.
- [x] Alcance auditado completo.
- [x] Fuentes de evidencia listadas.
- [x] 100% de módulos del alcance auditados o explícitamente marcados como `No verificable`.
- [x] Todas las evidencias tienen ID estable.
- [x] Todas las evidencias tienen severidad clasificada.
- [x] Todas las evidencias relevantes separan `Observed / Required / Decision`.
- [x] Todos los gaps tienen evidencia vinculada.
- [x] Todos los gaps tienen fase destino explícita.
- [x] Todas las hipótesis están cerradas como `CONFIRMADA`, `RESUELTA`, `RECHAZADA` o `TO BE VERIFIED` (con destino explícito).
- [x] Cero hipótesis abiertas sin destino.
- [x] Cero contradicciones no documentadas con HITOs previos.
- [x] Todos los IDs `E`, `GAP`, `OBS`, `H` son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.
**Verificación de cadena de gobernanza:** ADR Master §2.1 → ADR_05 §3 D4, §5 → NADR-19 §5.5 R20 → HITO 6.0 → HITO 6.1 → (futuro) HITO 6.2, 6.3, 6.4 → ADR_06 / NADRs → Execution Plan.
**Contradicciones con HITOs previos:** Ninguna. HITO 6.0 identificó la Regression Gate Illusion a nivel de CI. HITO 6.1 confirma que el sujeto de verificación existe y que la ilusión está en la invocación, no en el sujeto. Esto es consistente y complementario.
**Decision Candidates generados:** DC-6.7 (verification boundary), DC-6.8 (smoke test de regresión). DC-6.1 y DC-6.3 alimentados con evidencia adicional.
**Siguiente paso recomendado:** Redactar HITO 6.2 (Canonical Baseline Consumption & Corpus Materialization) para auditar cómo se consume físicamente la baseline sellada y cómo llega el corpus canónico al entorno de ejecución. Posteriormente, HITO 6.3 (CI Regression Gate & Operational Semantics) para auditar la infraestructura CI y la semántica operacional. Finalmente, HITO 6.4 (Dependency Graph & Readiness Assessment) para consolidar findings y Decision Candidates.