# HITO_6.3_CI_REGRESSION_GATE_AND_OPERATIONAL_SEMANTICS.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-09-25
**Fecha de congelamiento:** 2026-09-25
**Fase:** 17-BIS — Fase 6 (Continuous Verification)
**Tipo de artefacto:** Forensic Flow Audit / Operational Semantics Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- ADR_F17_BIS_MASTER.md (FROZEN) §6, §10
- ADR_F17_BIS_05.md (FROZEN) §5, §7
- ENGINEERING_PRINCIPLES.md (FROZEN) §II, §IV
- ROADMAP_ARQUITECTONICO_LP.md (FROZEN) — Fase 17_BIS
- HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md v1.0.0 (FROZEN)
- HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md v1.0.0 (FROZEN)
- HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md v1.0.0 (FROZEN)
- METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN)
- `.github/workflows/ci.yml`
- `tools/evaluation/run_regression.py`
- `core/benchmark/topology/regression/report.py`
- `infra/extraction/providers/pymupdf_provider.py`
- Reportes generados: `/tmp/regression_timing/regression_report.json`, `/tmp/regression_exit/regression_report.json`
**Mandato:** ¿Existe actualmente un camino de CI reproducible y operacionalmente definido que ejecute la Continuous Verification sobre la production pipeline y la baseline canónica, y cuyo resultado tenga una semántica de éxito/fallo inequívoca y pueda actuar como gate real?
**Síntesis:** El CI ejecuta un workflow que invoca un entry point de regresión que consume el production pipeline y la baseline sellada, produce un veredicto científico (HARD_FAIL confirmado) con exit code 2 correcto, y propaga ese fallo sin neutralización. Sin embargo: (1) el entry point invocado por CI (`pytest -m regression`) selecciona 0 tests (no invoca el entry point real), (2) el reporte no incluye el configuration_fingerprint (rompe reproducibilidad), (3) el enforcement a nivel de merge es NO DEMOSTRADO desde el repositorio, (4) no existen perfiles diferenciados (PR vs full vs nightly), (5) no existe protección de integridad sobre `tests/corpus/canonical/` (solo sobre `tests/fixtures/`).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-25 | Emisión inicial. |
| 1.0.0-FROZEN | 2026-09-25 | Cierre formal del HITO con evidencia completa. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la infraestructura de CI, la semántica operacional del Regression Gate, la propagación de fallo desde el dominio hasta el enforcement, la reproducibilidad y los perfiles de ejecución. La auditoría cubrió: el workflow CI completo (`.github/workflows/ci.yml`), el entry point de regresión (`run_regression.py`), la ejecución real del corpus completo (21 documentos), el reporte generado, las dependencias del pipeline de extracción, y la protección de integridad en CI.

**Hallazgo central:**

> El CI tiene un job `regression-gates` que ejecuta `pytest -m "regression"`, pero este comando selecciona **0 tests** (exit code 5). El entry point real (`run_regression.py`) que conecta el production pipeline con la baseline sellada **NO es invocado por CI**. Cuando se ejecuta manualmente, `run_regression.py` produce un veredicto científico correcto (HARD_FAIL, exit code 2) en 3.74 segundos para los 21 documentos del corpus, sin dependencias externas, y con propagación limpia del fallo (sin `continue-on-error`, `|| true`, `exit 0`). Sin embargo, el reporte generado **no incluye el `configuration_fingerprint`** (a pesar de calcularlo), lo que rompe la reproducibilidad. El enforcement a nivel de merge es **NO DEMOSTRADO** desde el repositorio (branch protection es configuración del servidor GitHub, no del código).

**Defectos dominantes confirmados:**

1. **CI no invoca el entry point real (E-6.3-001):** El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests. El entry point `run_regression.py` (que conecta production pipeline + baseline sellada) no es invocado por CI.
2. **Reporte sin configuration_fingerprint (E-6.3-002):** `run_regression.py` calcula `configuration_fingerprint` pero no lo persiste en el reporte JSON. Esto rompe la reproducibilidad: no se puede reconstruir qué configuración produjo un verdict específico.
3. **Sin protección de integridad sobre baseline canónica (E-6.3-003):** CI verifica inmutabilidad de `tests/fixtures/` (ruta legacy) pero no de `tests/corpus/canonical/` (ruta canónica). Mutaciones a la baseline no serían detectadas.
4. **Enforcement NO DEMOSTRADO (E-6.3-004):** Branch protection y required status checks son configuración del servidor GitHub, no del repositorio. No hay evidencia de que el job `regression-gates` bloquee merges.
5. **Sin perfiles diferenciados (E-6.3-005):** Un único workflow con triggers `push [main, develop]` y `pull_request [main]`. Sin schedules, sin workflow_dispatch, sin paths filter. El corpus completo (3.74s) se ejecuta en todo push, incluso cambios irrelevantes.

**Hallazgo positivo confirmado:**

6. **Propagación de fallo sin neutralización (E-6.3-006):** No hay `continue-on-error`, `|| true`, `exit 0`, `set +e` ni condiciones `if:` en el workflow. Un fallo en el job propaga directamente como fallo del workflow.
7. **Ejecución factible en CI (E-6.3-007):** 3.74 segundos para 21 documentos. ~28.8 MB de corpus. Sin dependencias externas (PyMuPDF es puramente local). Ejecutable en `ubuntu-latest` sin timeout issues.
8. **Exit code correcto (E-6.3-008):** HARD_FAIL → exit code 2 (confirmado). La taxonomía NADR-19 §5.5 R22 funciona correctamente cuando el entry point se ejecuta.

**Veredicto:** El CI tiene la infraestructura nominal para un Regression Gate pero no la conexión funcional. El entry point real existe y es operacionalmente ejecutable (3.74s, exit code correcto, sin dependencias externas). El gap es de **conexión** (CI no invoca el entry point correcto) y de **reproducibilidad** (reporte sin configuration_fingerprint) y de **enforcement** (branch protection no demostrable). La "Regression Gate Illusion" identificada en HITO 6.0 se confirma operacionalmente: el job existe, el entry point existe, pero no están conectados.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código.

Específicamente, este HITO:
- **NO** diseña el workflow futuro de CI.
- **NO** implementa un nuevo gate ni adapter.
- **NO** crea pytest markers ni modifica los existentes.
- **NO** decide si CI debe invocar `pytest` o `run_regression.py` directamente (pertenece a DC-6.12).
- **NO** decide nuevos exit codes ni modifica NADR-19.
- **NO** modifica `DoubleProtectionMechanism`.
- **NO** introduce `BASELINE_INTEGRITY_FAILURE` (pertenece a DC-6.4).
- **NO** elige perfiles de ejecución (PR/full/nightly) (pertenece a DC-6.5).
- **NO** configura branch protection.
- **NO** materializa PDFs (pertenece a DC-6.2 / HITO 6.2).
- **NO** optimiza performance.
- **NO** crea nuevos NADRs.

Este HITO **SÍ**:
- Demuestra qué eventos disparan el CI.
- Demuestra qué entry point se invoca.
- Demuestra si ese entry point ejecuta el production pipeline y consume la baseline.
- Demuestra cómo se propaga el fallo desde el dominio hasta el job CI.
- Demuestra qué evidencia se genera y si es reproducible.
- Demuestra qué superficie está protegida por CI.
- Identifica gaps y Decision Candidates.

### 2.2 Método forense

1. Cargar fuentes normativas (ADR Master §6, §10; ADR_05 §5, §7; ROADMAP; ENGINEERING_PRINCIPLES §II, §IV).
2. Cargar HITOs previos como insumo (6.0: Regression Gate Illusion; 6.1: sujeto de verificación; 6.2: baseline y materialización).
3. Inspeccionar workflow CI (`.github/workflows/ci.yml`) completo.
4. Verificar propagación de fallo (continue-on-error, || true, exit 0, if:).
5. Verificar triggers y perfiles de ejecución.
6. Verificar permisos del workflow (persist-credentials, permissions).
7. Ejecutar `run_regression.py` con el corpus completo y medir tiempo de ejecución.
8. Inspeccionar reporte JSON generado (estructura, campos, reproducibilidad).
9. Verificar dependencias externas del pipeline de extracción.
10. Verificar protección de integridad en CI.
11. Separar hechos de NO DEMOSTRADO (branch protection).
12. Consolidar gaps solo con evidencia demostrada.

### 2.3 Axioma de entrada

> **HITO 6.1 (sujeto) y HITO 6.2 (baseline) están FROZEN.** HITO 6.3 no re-audita el production pipeline ni la baseline. Asume que el sujeto (E-6.1-001, E-6.1-002) y la baseline (E-6.2-001 a E-6.2-014) existen como fue demostrado. HITO 6.3 audita la **conexión operativa** entre CI, el sujeto y la baseline.

### 2.4 Relación con HITOs previos

| HITO | Qué demostró | Qué hereda 6.3 |
|---|---|---|
| HITO 6.0 | Regression Gate Illusion: CI job nominal sin tests. PDFs en `.gitignore`. No materialización. Verificación sobre ruta incorrecta (`tests/fixtures/`). | E-6.0-001 a E-6.0-012 como evidencia de contexto. 6.3 profundiza en la cadena de propagación y enforcement. |
| HITO 6.1 | Sujeto de verificación existe: `run_regression.py` invoca `build_extraction_pipeline()`. Correspondencia production ↔ verification completa. | E-6.1-001, E-6.1-002, E-6.1-007 como insumo. 6.3 verifica si CI invoca este entry point. |
| HITO 6.2 | Baseline sellada existe. 14 de 21 PDFs no trackeados. No materialización. Crash no tipado ante PDF ausente. Exit code ambiguo. | E-6.2-001 a E-6.2-014 como insumo. 6.3 verifica si CI preserva integridad de la baseline y propaga correctamente el exit code. |

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos / Archivos | Estado |
|---|---|---|
| Workflow CI | `.github/workflows/ci.yml` (3541 bytes) | 100% auditado |
| Otros workflows | `.github/workflows/` (solo `ci.yml`) | 100% auditado |
| Entry point de regresión | `tools/evaluation/run_regression.py` | Referenciado (auditoría completa en HITO 6.1) |
| Reporte de regresión | `/tmp/regression_timing/regression_report.json` | 100% auditado (estructura) |
| Pipeline de extracción | `infra/extraction/providers/pymupdf_provider.py` | 100% auditado (dependencias externas) |
| Corpus canónico | `tests/corpus/canonical/` | Referenciado (auditoría completa en HITO 6.2) |
| Ejecución real | `run_regression.py` con corpus completo | 100% auditado (tiempo, exit code, reporte) |
| Protección de integridad | `git diff tests/fixtures/` en workflow | 100% auditado |
| Branch protection | Configuración del servidor GitHub | **NO DEMOSTRADO** (no accesible desde repositorio) |
| Required status checks | Configuración del servidor GitHub | **NO DEMOSTRADO** (no accesible desde repositorio) |
| Historial de ejecuciones CI | Dashboard de GitHub Actions | **NO DEMOSTRADO** (no accesible desde repositorio) |

**Fuera de scope:**
- Contenido de `run_regression.py` (auditoría completa en HITO 6.1)
- Contratos de identidad e integridad de la baseline (auditoría completa en HITO 6.2)
- Mecanismo interno de `DoubleProtectionMechanism` (auditoría completa en HITO 6.1)
- Materialización de PDFs (auditoría completa en HITO 6.2)
- Performance optimization (no es benchmark)
- Branch protection real (no accesible desde repositorio)

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §6 | Fase 6: Continuous Verification (Integración definitiva en CI Gates) |
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §10 | DoD Level B: Compuertas de CI Activas |
| ADR (normativa) | `ADR_F17_BIS_05.md` §5 | Cláusula de relación Fase 5 → Fase 6 |
| ADR (normativa) | `ADR_F17_BIS_05.md` §7 | Target State: CONTINUOUS VERIFICATION (Fase 6) |
| Roadmap (normativa) | `ROADMAP_ARQUITECTONICO_LP.md` Fase 17_BIS | "Regression Gates: Aserción estricta en CI" |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §II | Functional Core / Imperative Shell |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §IV | Cero Fallos Silenciosos |
| HITO previo (forense) | `HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md` | Regression Gate Illusion, gaps de CI |
| HITO previo (forense) | `HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md` | Sujeto de verificación, entry point |
| HITO previo (forense) | `HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md` | Baseline sellada, materialización, error handling |
| CI (runtime) | `.github/workflows/ci.yml` | Workflow completo, jobs, triggers, propagation |
| CI (runtime) | `.github/workflows/` (directorios) | Verificación de workflows adicionales |
| Código (runtime) | `tools/evaluation/run_regression.py` | Entry point (referenciado de HITO 6.1) |
| Código (runtime) | `infra/extraction/providers/pymupdf_provider.py` | Dependencias externas del pipeline |
| Artefacto (runtime) | `/tmp/regression_timing/regression_report.json` | Reporte generado (estructura, reproducibilidad) |
| Artefacto (runtime) | `/tmp/regression_exit/regression_report.json` | Reporte generado (exit code) |
| Ejecución (forense) | `run_regression.py` con corpus completo | Tiempo de ejecución (3.74s), exit code (2) |
| Ejecución (forense) | Búsqueda de continue-on-error, \|\| true, exit 0 | Propagación de fallo |
| Ejecución (forense) | Búsqueda de schedules, workflow_dispatch, paths | Perfiles de ejecución |
| Ejecución (forense) | Búsqueda de persist-credentials, permissions | Seguridad de la frontera |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — CI Trigger → Job (lo que existe)

```text
GitHub event
    │
    ├── push [main, develop]
    │       │
    │       ▼
    │   workflow: ci.yml
    │       │
    │       ├── job: static-analysis
    │       │       └── pyright + lint-imports
    │       │
    │       ├── job: regression-gates (needs: static-analysis)
    │       │       ├── checkout (persist-credentials: false)
    │       │       ├── setup-python (3.11)
    │       │       ├── pip install .[dev]
    │       │       ├── pytest -m "regression" -v --tb=short --no-header
    │       │       │       ▼
    │       │       │   [GAP: 0 tests collected]
    │       │       │       ▼
    │       │       │   exit code 5 (no tests collected)
    │       │       │       ▼
    │       │       │   [GAP: job falla si se ejecuta]
    │       │       │
    │       │       └── git diff --exit-code tests/fixtures/
    │       │               ▼
    │       │           [GAP: ruta incorrecta, no protege baseline]
    │       │
    │       ├── job: unit-tests (needs: static-analysis)
    │       │       └── pytest -m "unit" -v --tb=short --no-header -x
    │       │
    │       └── job: integration-tests (needs: [regression-gates, unit-tests])
    │               └── pytest -m "integration and not regression"
    │
    └── pull_request [main]
            │
            ▼
        (mismo workflow, mismos jobs)

Leyenda:
  [OK] componente existente
  [GAP] gap confirmado
  [NO DEMOSTRADO] no verificable desde el repositorio
```

**Estado:** [GAP] — El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests. No invoca `run_regression.py`.

### FLUJO B — Entry Point Real (lo que debería invocar CI)

```text
run_regression.py main()
    │
    ├── parse_args()
    │       --corpus-dir tests/corpus/canonical
    │       --pdf-dir tests/corpus/canonical/pdf
    │       --output-dir /tmp/regression_timing
    │
    ├── LoadCorpusManifestUseCase
    │       ▼
    │   CorpusManifest (v3.9, 21 docs)
    │
    ├── RegressionAdapter.verify_completeness()
    │       ▼
    │   [OK] 21 == 21
    │
    ├── build_canonical_engine_configuration()
    │       ▼
    │   ConfigurationFingerprint (calculado)
    │
    ├── build_extraction_pipeline()            ← SUT NORMATIVO (HITO 6.1)
    │       ▼
    │   PdfParserAdapter (PyMuPDFProvider)
    │
    ├── PARA CADA DOCUMENTO (21 docs):
    │       ├── load_gt_uc.execute(doc_id) → SealedOracle
    │       ├── adapter.verify_*() → [OK]
    │       ├── extraction_pipeline.parse(pdf_path)
    │       │       ▼
    │       │   [OK] PyMuPDF (local, sin red/GPU)
    │       │       ▼
    │       │   Candidate AST
    │       ├── strategy.evaluate_regression()
    │       │       ▼
    │       │   DoubleProtectionMechanism.evaluate()
    │       │       ▼
    │       │   HARD_FAIL (163 Critical FN)
    │       └── RegressionEvaluationReport
    │
    ├── build_regression_report()
    │       ▼
    │   RegressionReport (corpus_nss: 0.7208, verdict: HARD_FAIL)
    │       │
    │       ├── corpus_nss: ✅ incluido
    │       ├── corpus_verdict: ✅ incluido (HARD_FAIL)
    │       ├── corpus_version: ✅ incluido (v3.9)
    │       ├── documents: ✅ incluido (21 docs con métricas)
    │       ├── generated_at: ✅ incluido
    │       ├── total_critical_false_negatives: ✅ incluido
    │       └── configuration_fingerprint: ❌ NO INCLUIDO
    │
    ├── JsonRegressionReportFormatter.format()
    │       ▼
    │   regression_report.json
    │
    └── sys.exit(EXIT_HARD_FAIL)
            ▼
        exit code 2

Leyenda:
  [OK] componente existente
  [GAP] campo no incluido en reporte
```

**Estado:** [OK] para ejecución real. [GAP] para `configuration_fingerprint` (calculado pero no persistido).

### FLUJO C — Propagación de Fallo (CI → enforcement)

```text
Job: regression-gates
    │
    ├── pytest -m "regression"
    │       ▼
    │   exit code 5 (no tests collected)
    │       │
    │       ├── continue-on-error: ❌ NO existe
    │       ├── || true: ❌ NO existe
    │       ├── exit 0: ❌ NO existe
    │       ├── set +e: ❌ NO existe
    │       └── if: condition: ❌ NO existe
    │
    ├── job failed
    │       ▼
    │   workflow failed
    │       │
    │       ├── Required status check: [NO DEMOSTRADO]
    │       │       └── branch protection configuration
    │       │           (no accesible desde el repositorio)
    │       │
    │       └── Merge blocked: [NO DEMOSTRADO]
    │               └── depende de branch protection

Leyenda:
  [OK] propagación correcta
  [NO DEMOSTRADO] no verificable desde el repositorio
```

**Estado:** [OK] para propagación dentro del workflow (sin neutralización). [NO DEMOSTRADO] para enforcement a nivel de merge.

### FLUJO D — Ejecución Real (manual, no CI)

```text
python tools/evaluation/run_regression.py \
    --corpus-dir tests/corpus/canonical \
    --pdf-dir tests/corpus/canonical/pdf \
    --output-dir /tmp/regression_timing
    │
    ├── Tiempo de ejecución: 3.74 segundos
    ├── Exit code: 2 (HARD_FAIL)
    ├── Corpus: 21 documentos
    ├── Tamaño: ~28.8 MB (61 archivos)
    ├── Dependencias: PyMuPDF (local, sin red/GPU)
    ├── Reporte: regression_report.json + regression_report.md
    │       ├── corpus_nss: 0.7208
    │       ├── corpus_verdict: HARD_FAIL
    │       ├── corpus_version: v3.9
    │       ├── total_critical_false_negatives: 163
    │       └── configuration_fingerprint: ❌ NO incluido
    │
    └── Observabilidad:
        ├── Metrics por ContentNodeType: ✅
        ├── Diagnostics (global_ted, normalization): ✅
        ├── False negatives/positives por tipo: ✅
        └── Identity chain (manifest_hash, parameter_identity): ❌ NO incluidos

Leyenda:
  [OK] componente existente
  [GAP] componente ausente
```

**Estado:** [OK] para ejecución real. [GAP] para reproducibilidad completa.

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

### 6.1 CI Workflow Inventory

| Componente | Valor observado | Estado |
|---|---|---|
| Workflows totales | 1 (`ci.yml`) | CONFIRMADO |
| Triggers | `push [main, develop]`, `pull_request [main]` | CONFIRMADO |
| Schedules | ❌ No existen | CONFIRMADO (ausencia) |
| workflow_dispatch | ❌ No existe | CONFIRMADO (ausencia) |
| Paths filter | ❌ No existe | CONFIRMADO (ausencia) |
| Concurrency | `${{ github.workflow }}-${{ github.ref }}` + `cancel-in-progress: true` | CONFIRMADO |
| Python version | 3.11 | CONFIRMADO |
| Jobs | 4 (static-analysis, regression-gates, unit-tests, integration-tests) | CONFIRMADO |

### 6.2 Entry Points Inventory

| Entry Point | Invocado por CI | Ejecuta production pipeline | Consume baseline sellada | Estado |
|---|---|---|---|---|
| `pytest -m "regression"` | ✅ Sí (job regression-gates) | ❌ No (0 tests) | ❌ No | GAP |
| `run_regression.py` | ❌ No | ✅ Sí (E-6.1-001) | ✅ Sí (E-6.2-006) | GAP (no invocado por CI) |
| `pytest -m "unit"` | ✅ Sí (job unit-tests) | ❌ No (unit tests) | ❌ No | OK (no es regression) |
| `pytest -m "integration and not regression"` | ✅ Sí (job integration-tests) | ✅ Parcial (6 tests usan build_extraction_pipeline) | ❌ No (no comparan contra baseline) | OK (no es regression) |

### 6.3 Exit Semantics Matrix

| Domain Verdict | Process Exit Code | CI Interpretation | Propagation | Estado |
|---|---|---|---|---|
| PASS | 0 (`EXIT_PASS`) | Job success | Directa | OK |
| WARNING | 1 (`EXIT_WARNING`) | Job failure (sin neutralización) | Directa | OK |
| HARD_FAIL | 2 (`EXIT_HARD_FAIL`) | Job failure (sin neutralización) | Directa | OK |
| Execution failure (crash) | 1 (default Python) | Job failure (indistinguible de WARNING) | Ambigua | GAP (E-6.2-004) |
| Baseline integrity failure | 1 (default Python) | Job failure (indistinguible de WARNING) | Ambigua | GAP (E-6.2-004) |
| No tests collected | 5 (pytest) | Job failure | Directa | OK (pero no es regression) |

### 6.4 Report Observability Matrix

| Campo | Incluido en reporte | Determinista | Reproducible | Estado |
|---|---|---|---|---|
| `corpus_nss` | ✅ | ✅ | ✅ | OK |
| `corpus_verdict` | ✅ | ✅ | ✅ | OK |
| `corpus_version` | ✅ | ✅ | ✅ | OK |
| `documents` (21 docs con métricas) | ✅ | ✅ | ✅ | OK |
| `generated_at` | ✅ | ❌ (timestamp UTC) | ❌ | GAP (si inject_timestamp=True) |
| `total_critical_false_negatives` | ✅ | ✅ | ✅ | OK |
| `total_warning_false_negatives` | ✅ | ✅ | ✅ | OK |
| `total_info_false_negatives` | ✅ | ✅ | ✅ | OK |
| `hard_fail_count` | ✅ | ✅ | ✅ | OK |
| `warning_count` | ✅ | ✅ | ✅ | OK |
| `pass_count` | ✅ | ✅ | ✅ | OK |
| `total_documents` | ✅ | ✅ | ✅ | OK |
| `configuration_fingerprint` | ❌ | N/A | ❌ | GAP |
| `manifest_hash` | ❌ | N/A | ❌ | GAP |
| `parameter_identity` | ❌ | N/A | ❌ | GAP |
| `result_identity` | ❌ | N/A | ❌ | GAP |
| `commit_sha` | ❌ | N/A | ❌ | GAP |
| `schema_version` | ❌ | N/A | ❌ | GAP |

### 6.5 Failure Propagation Matrix

| Failure Origin | Propagation Path | Neutralization | Job Result | Estado |
|---|---|---|---|---|
| Regression detected (HARD_FAIL) | exit 2 → job fails → workflow fails | None (no continue-on-error) | Job failed | OK |
| Regression warning | exit 1 → job fails → workflow fails | None | Job failed (indistinguible de crash) | GAP |
| Baseline missing | FileNotFoundError → exit 1 → job fails | None | Job failed (indistinguible de WARNING) | GAP |
| Baseline integrity failure | OracleIntegrityError → exit 1 → job fails | None | Job failed (indistinguible de WARNING) | GAP |
| No regression tests | exit 5 → job fails → workflow fails | None | Job failed | OK (pero no es regression) |
| Python crash | traceback → exit 1 → job fails | None | Job failed (indistinguible de WARNING) | GAP |

### 6.6 CI Protection Surface

| Superficie protegida | Mecanismo | Estado |
|---|---|---|
| `tests/fixtures/` | `git diff --exit-code tests/fixtures/` | OK (pero ruta incorrecta) |
| `tests/corpus/canonical/` | ❌ No protegida | GAP |
| `tests/corpus/canonical/pdf/` | ❌ No protegida | GAP |
| `tests/corpus/canonical/ground_truth/` | ❌ No protegida | GAP |
| `tests/corpus/canonical/manifest.json` | ❌ No protegida | GAP |
| Branch protection | NO DEMOSTRADO | NO DEMOSTRADO |
| Required status checks | NO DEMOSTRADO | NO DEMOSTRADO |

### 6.7 Execution Profiles

| Perfil | Trigger | Regression | Corpus | Enforcement | Evidencia |
|---|---|---|---|---|---|
| PR (main) | pull_request | ❌ (0 tests) | N/A | NO DEMOSTRADO | CONFIRMADO (ausencia) |
| push main | push | ❌ (0 tests) | N/A | NO DEMOSTRADO | CONFIRMADO (ausencia) |
| push develop | push | ❌ (0 tests) | N/A | NO DEMOSTRADO | CONFIRMADO (ausencia) |
| nightly | ❌ No existe | N/A | N/A | N/A | CONFIRMADO (ausencia) |
| manual dispatch | ❌ No existe | N/A | N/A | N/A | CONFIRMADO (ausencia) |

### 6.8 Operational Constraints

| Dimensión | Valor observado | Estado |
|---|---|---|
| Tiempo de ejecución (corpus completo) | 3.74 segundos | OK |
| Tamaño del corpus | ~28.8 MB (61 archivos) | OK |
| Dependencias externas | ❌ Ninguna (PyMuPDF es local) | OK |
| GPU requerida | ❌ No | OK |
| Red requerida | ❌ No | OK |
| API keys requeridas | ❌ No | OK |
| Runner compatible | ubuntu-latest | OK |
| Timeout issues | ❌ No | OK |
| Paralelismo | ❌ No (secuencial) | OK |
| Determinismo | Parcial (generated_at rompe si inject_timestamp=True) | GAP |

---

## 7. MATRIZ OBSERVED / REQUIRED / STATUS

| Tema | Observed | Required | Status | Evidencia |
|---|---|---|---|---|
| CI invoca entry point de regresión | `pytest -m "regression"` → 0 tests | ADR Master §6: "Integración definitiva en CI Gates" | DISCREPANCY | E-6.3-001 |
| Entry point ejecuta production pipeline | `run_regression.py` sí lo ejecuta (E-6.1-001), pero CI no lo invoca | ADR Master §2.1: baseline evalúa pipeline de producción | DISCREPANCY | E-6.3-001, E-6.1-001 |
| Entry point consume baseline sellada | `run_regression.py` sí la consume (E-6.2-006), pero CI no lo invoca | ADR_05 §5: Fase 6 integra Regression Gates en CI/CD | DISCREPANCY | E-6.3-001, E-6.2-006 |
| Reporte incluye configuration_fingerprint | Calculado pero no persistido | ENGINEERING_PRINCIPLES §IV: Reproducibilidad | DISCREPANCY | E-6.3-002 |
| Reporte incluye manifest_hash | No incluido | ADR Master §3: Identidad de baseline | DISCREPANCY | E-6.3-002 |
| Propagación de fallo sin neutralización | No hay continue-on-error, \|\| true, exit 0 | ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos | COMPLIANT | E-6.3-006 |
| Exit code para HARD_FAIL | 2 (EXIT_HARD_FAIL) | NADR-19 §5.5 R22 | COMPLIANT | E-6.3-008 |
| Branch protection bloquea merges | NO DEMOSTRADO | ADR Master §10 DoD Level B: Compuertas de CI Activas | NO DEMOSTRADO | E-6.3-004 |
| Superficie protegida incluye baseline canónica | Solo protege `tests/fixtures/` (ruta legacy) | NADR-21 §5.4 R19: inmutabilidad de Sealed | DISCREPANCY | E-6.3-003 |
| Perfiles diferenciados (PR/full/nightly) | Un único perfil | ROADMAP: "Regression Gates: Aserción estricta en CI" | DISCREPANCY | E-6.3-005 |
| Ejecución factible en CI | 3.74s, ~28.8 MB, sin dependencias externas | Implícito en factibilidad operacional | COMPLIANT | E-6.3-007 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-6.3-001** | P0 | `.github/workflows/ci.yml` línea 67: `python -m pytest -m "regression" -v --tb=short --no-header`; HITO 6.0 E-6.0-002, E-6.0-003 | **CI no invoca el entry point real.** El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests (exit code 5). El entry point `run_regression.py` (que conecta production pipeline + baseline sellada) no es invocado por CI. |
| **E-6.3-002** | P1 | Ejecución forense: `run_regression.py` con corpus completo → reporte JSON sin `configuration_fingerprint`; `tools/evaluation/run_regression.py` línea ~160: `config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)` (calculado pero no persistido) | **Reporte sin configuration_fingerprint.** El entry point calcula el fingerprint de configuración pero no lo incluye en el reporte JSON. Esto rompe la reproducibilidad: no se puede reconstruir qué configuración produjo un verdict específico. |
| **E-6.3-003** | P1 | `.github/workflows/ci.yml` línea 70-75: `git diff --exit-code tests/fixtures/`; HITO 6.0 E-6.0-006, E-6.0-012 | **Sin protección de integridad sobre baseline canónica.** CI verifica inmutabilidad de `tests/fixtures/` (ruta legacy con caches y fixtures sintéticos) pero no de `tests/corpus/canonical/` (ruta canónica con baseline sellada). Mutaciones a la baseline no serían detectadas por CI. |
| **E-6.3-004** | P1 | Búsqueda en `.github/`: no hay archivos de configuración de branch protection; configuración del servidor GitHub no accesible desde el repositorio | **Enforcement NO DEMOSTRADO.** Branch protection y required status checks son configuración del servidor GitHub, no del repositorio. No hay evidencia de que el job `regression-gates` bloquee merges a main. |
| **E-6.3-005** | P2 | `.github/workflows/ci.yml` líneas 3-7: triggers `push [main, develop]`, `pull_request [main]`; búsqueda de `schedule`, `workflow_dispatch`, `paths:` → 0 resultados | **Sin perfiles diferenciados.** Un único workflow con triggers push/PR. Sin schedules (no hay perfil nightly), sin workflow_dispatch (no hay perfil manual), sin paths filter (se ejecuta en todo push, incluso cambios irrelevantes). |
| **E-6.3-006** | P2 | `.github/workflows/ci.yml` → búsqueda de `continue-on-error`, `\|\| true`, `exit 0`, `set +e`, `if:` → 0 resultados | **Propagación de fallo sin neutralización.** No hay mecanismos que conviertan un fallo en warning o que absorban el exit code. Un fallo en el job propaga directamente como fallo del workflow. |
| **E-6.3-007** | P2 | Ejecución forense: `Measure-Command { python tools/evaluation/run_regression.py ... }` → TotalSeconds: 3.74; `Get-ChildItem tests/corpus/canonical -Recurse` → 61 archivos, ~28.8 MB; `pymupdf_provider.py` → sin imports de requests, http, api, gpu, cuda, torch | **Ejecución factible en CI.** 3.74 segundos para 21 documentos. ~28.8 MB de corpus. Sin dependencias externas (PyMuPDF es puramente local). Ejecutable en `ubuntu-latest` sin timeout issues. |
| **E-6.3-008** | P2 | Ejecución forense: `python tools/evaluation/run_regression.py ...` → exit code 2; reporte JSON: `"corpus_verdict": "HARD_FAIL"` | **Exit code correcto para HARD_FAIL.** Exit code 2 (EXIT_HARD_FAIL) confirmado. La taxonomía NADR-19 §5.5 R22 funciona correctamente cuando el entry point se ejecuta. |
| **E-6.3-009** | P2 | `.github/workflows/ci.yml` línea 50: `persist-credentials: false` en job regression-gates | **Checkout sin credenciales de push.** El checkout del job `regression-gates` no puede pushear al repositorio. Protección parcial contra mutación de la baseline. |
| **E-6.3-010** | P2 | `.github/workflows/ci.yml` → búsqueda de `permissions:`, `token:` → 0 resultados explícitos | **Permisos implícitos.** No hay declaración explícita de `permissions` ni `token` en el workflow. Se usan permisos por defecto de GitHub Actions. |
| **E-6.3-011** | P2 | `.github/workflows/` → solo `ci.yml` (3541 bytes) | **Un único workflow.** No hay workflows adicionales (nightly, release, manual). |
| **E-6.3-012** | P2 | Reporte JSON generado → keys: `corpus_nss`, `corpus_verdict`, `corpus_version`, `documents`, `generated_at`, `hard_fail_count`, `pass_count`, `total_critical_false_negatives`, `total_documents`, `total_info_false_negatives`, `total_warning_false_negatives`, `warning_count` | **Reporte con métricas completas pero sin identity chain.** El reporte incluye NSS, verdict, versión, documentos con métricas detalladas, y contadores. NO incluye: `configuration_fingerprint`, `manifest_hash`, `parameter_identity`, `result_identity`, `commit_sha`, `schema_version`. |
| **E-6.3-013** | P2 | Reporte JSON generado → `generated_at` presente; `tools/evaluation/run_regression.py`: `--inject-timestamp` default=False | **generated_at presente sin flag.** El campo `generated_at` aparece en el reporte a pesar de que el flag `--inject-timestamp` no fue usado (default=False). Posible bug en el formateador o en el test previo que generó el reporte. |

### Evidencia E-6.3-001: CI no invoca el entry point real

* **Archivo Fuente Primario:** `.github/workflows/ci.yml`
* **Símbolo Auditado:** Job `regression-gates`, step "Run regression gates (pytest marker)"
* **Declaración Observada:**

```yaml
- name: Run regression gates (pytest marker)
  run: |
    python -m pytest -m "regression" -v --tb=short --no-header
  env:
    CORPUS_READONLY: "true"
```

* **Observed:** El CI ejecuta `pytest -m "regression"` que selecciona 0 tests (HITO 6.0 E-6.0-002, E-6.0-003). El entry point `run_regression.py` no es invocado.
* **Required:** ADR Master §6: "Continuous Verification (Integración definitiva en CI Gates)." ADR_05 §5: "La Fase 6 integra estos artefactos en el pipeline de CI/CD." ROADMAP: "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos."
* **Decision:** Fase 5 difirió la integración CI a Fase 6 (HITO 6.1 E-6.1-007).
* **Hallazgo Forense:** El job `regression-gates` tiene la apariencia de un Regression Gate pero no ejecuta la verificación real. Es exactamente la "Regression Gate Illusion" identificada en HITO 6.0, confirmada operacionalmente: el job existe, el entry point existe, pero no están conectados.
* **Consecuencia Arquitectónica:** Sin invocar `run_regression.py`, el CI no ejecuta el production pipeline contra la baseline sellada. El DoD Level B del ADR Master ("Compuertas de CI Activas") no está satisfecho.
* **Estado:** OPEN

### Evidencia E-6.3-002: Reporte sin configuration_fingerprint

* **Archivo Fuente Primario:** `/tmp/regression_timing/regression_report.json`, `tools/evaluation/run_regression.py`
* **Símbolo Auditado:** `main()` → `config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)`; reporte JSON → keys
* **Declaración Observada:**

```python
# tools/evaluation/run_regression.py (línea ~160)
config = build_canonical_engine_configuration(
    matching_policy=matching_policy,
    cost_context=cost_context,
)
config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)
# ...
regression_report = build_regression_report(
    corpus_version=manifest.corpus_version.value,
    evaluation_reports=document_reports,
    generated_at=generated_at,
    configuration_fingerprint=config_fingerprint,  # pasado como argumento
)
```

```json
// /tmp/regression_timing/regression_report.json (keys)
{
  "corpus_nss": 0.7208478616924202,
  "corpus_verdict": "HARD_FAIL",
  "corpus_version": "v3.9",
  "documents": [...],
  "generated_at": "...",
  "hard_fail_count": 21,
  "pass_count": 0,
  "total_critical_false_negatives": 163,
  "total_documents": 21,
  "total_info_false_negatives": 0,
  "total_warning_false_negatives": 0,
  "warning_count": 0
}
// configuration_fingerprint: ❌ NO incluido
```

* **Observed:** El entry point calcula `configuration_fingerprint` y lo pasa a `build_regression_report()`, pero el campo NO aparece en el reporte JSON generado. El fingerprint se calcula pero no se persiste.
* **Required:** ENGINEERING_PRINCIPLES §IV: "Reproducibilidad y Determinismo: Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser 100% determinista." ADR Master §3: "Identidad (Baseline & Schema Identity): Mecanismo: Hash compuesto / encadenado determinista global."
* **Decision:** No existe decisión previa que excluya el `configuration_fingerprint` del reporte.
* **Hallazgo Forense:** El reporte de regresión no incluye la identidad de la configuración usada. Esto rompe la reproducibilidad: si un verdict cambia entre ejecuciones, no se puede determinar si fue por un cambio en el código, en la configuración, o en la baseline. El fingerprint se calcula pero se pierde.
* **Consecuencia Arquitectónica:** Sin `configuration_fingerprint` en el reporte, no se puede reconstruir qué configuración produjo un verdict específico. Esto es especialmente crítico para Fase 6 porque el gate debe ser reproducible.
* **Estado:** OPEN

### Evidencia E-6.3-003: Sin protección de integridad sobre baseline canónica

* **Archivo Fuente Primario:** `.github/workflows/ci.yml`
* **Símbolo Auditado:** Job `regression-gates`, step "Verify oracles were not mutated"
* **Declaración Observada:**

```yaml
- name: Verify oracles were not mutated
  run: |
    git diff --exit-code tests/fixtures/ || {
      echo "ERROR: Los oráculos de regresión fueron modificados durante la ejecución."
      echo "Esto viola NADR-10 §5.1 R2. Los oráculos son inmutables."
      exit 1
    }
```

* **Observed:** El CI verifica inmutabilidad de `tests/fixtures/` (ruta legacy que contiene caches y fixtures sintéticos, HITO 6.0 E-6.0-012) pero NO verifica `tests/corpus/canonical/` (ruta canónica que contiene la baseline sellada).
* **Required:** NADR-21 §5.4 R19: "Inmutabilidad de SealedOracle: Un oráculo sellado no puede ser alterado ni sobrescrito." ADR Master §5: "Invariante de Sellado Estricto (Zero Partial Sealing)."
* **Decision:** La verificación de `tests/fixtures/` fue probablemente creada en una fase anterior, antes de la construcción del corpus canónico.
* **Hallazgo Forense:** La protección de integridad del CI apunta a la ruta incorrecta. Mutaciones a la baseline canónica (`tests/corpus/canonical/ground_truth/*.json`, `tests/corpus/canonical/manifest.json`) no serían detectadas por CI. La verificación de `tests/fixtures/` es efectivamente decorativa porque esa ruta contiene caches generados por tests.
* **Consecuencia Arquitectónica:** La baseline sellada no está protegida por CI. Un desarrollador podría modificar un oráculo sellado sin que CI lo detecte. Esto viola la invariante de inmutabilidad de SealedOracle a nivel de CI.
* **Estado:** OPEN

### Evidencia E-6.3-004: Enforcement NO DEMOSTRADO

* **Archivo Fuente Primario:** `.github/` (directorios), configuración del servidor GitHub
* **Símbolo Auditado:** Branch protection, required status checks
* **Declaración Observada:**

```text
.github/
├── workflows/
│   └── ci.yml
```

No hay archivos de configuración de branch protection. La configuración de branch protection es parte del servidor GitHub, no del repositorio.

* **Observed:** No hay evidencia en el repositorio de que el job `regression-gates` esté configurado como required status check. La configuración de branch protection no es accesible desde el código.
* **Required:** ADR Master §10 DoD Level B: "Compuertas de CI Activas: Pipeline en integración continua ejecutándose de forma exitosa contra los Regression Gates."
* **Decision:** No existe decisión previa documentada sobre branch protection.
* **Hallazgo Forense:** El enforcement a nivel de merge es **NO DEMOSTRADO** desde el repositorio. No se puede afirmar que el job `regression-gates` bloquee merges a main. Es posible que sí lo haga (configuración del servidor), pero no hay evidencia en el código.
* **Consecuencia Arquitectónica:** Sin evidencia de enforcement, no se puede afirmar que la "Ilusión del Regression Gate" tenga impacto real en el desarrollo. Si branch protection no está configurado, el job puede fallar sin bloquear merges.
* **Estado:** OPEN (NO DEMOSTRADO)

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-6.3-01 | La variable `CORPUS_READONLY: "true"` en el job `regression-gates` no tiene consumidor demostrado en el código (OBS-6.0-01 de HITO 6.0, OBS-6.2-10 de HITO 6.2). Es decorativa. | Bajo | OPEN |
| OBS-6.3-02 | El comentario en el workflow dice "El corpus es Read-Only: los tests no pueden mutar los oráculos" y usa `persist-credentials: false`. Esto es correcto como protección parcial, pero no reemplaza la verificación de integridad sobre `tests/corpus/canonical/`. | Medio | OPEN |
| OBS-6.3-03 | `persist-credentials: false` solo se usa en el job `regression-gates`. Los otros jobs (static-analysis, unit-tests, integration-tests) no lo declaran explícitamente. | Bajo | OPEN |
| OBS-6.3-04 | El job `integration-tests` tiene `needs: [regression-gates, unit-tests]`, lo que significa que depende del éxito de `regression-gates`. Si `regression-gates` falla (por exit code 5), `integration-tests` no se ejecuta. | Medio | OPEN |
| OBS-6.3-05 | El reporte JSON incluye `generated_at` a pesar de que `--inject-timestamp` no fue usado. Esto podría ser un bug en el formateador JSON o en la función `build_regression_report()`. | Bajo | OPEN |
| OBS-6.3-06 | El reporte JSON incluye métricas detalladas por ContentNodeType (composite_block, heading, paragraph, display_equation, inline_equation) con diagnostics completos (global_ted, normalization, overflow_triggered, false_negatives/positives, precision, recall). | Bajo | OPEN |
| OBS-6.3-07 | El tiempo de ejecución (3.74s para 21 documentos) es sorprendentemente rápido. Esto sugiere que el corpus es pequeño o que PyMuPDF es muy eficiente. En cualquier caso, es operacionalmente factible para CI. | Bajo | OPEN |
| OBS-6.3-08 | El corpus completo tiene 61 archivos y ~28.8 MB. Esto es factible para GitHub Actions (típicamente 14 GB de disco disponible). | Bajo | OPEN |
| OBS-6.3-09 | No hay paths filter en el workflow. Esto significa que la regresión se ejecuta en todo push a main/develop, incluso cambios que no tocan el pipeline de extracción (por ejemplo, cambios en documentación o en tests unitarios). | Medio | OPEN |
| OBS-6.3-10 | El job `regression-gates` tiene `needs: static-analysis`, lo que significa que solo se ejecuta si `static-analysis` pasa. Esto es correcto como dependencia. | Bajo | OPEN |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-6.3-01** | CI no invoca el entry point real (`run_regression.py`). El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests. El entry point que conecta production pipeline + baseline sellada no es invocado. | E-6.3-001, HITO 6.0 E-6.0-001, E-6.0-002, E-6.0-003 | Pilar: CI Gate / ADR Master §6, §10 DoD Level B | **Fase 6** | BLOCKING |
| **GAP-6.3-02** | El reporte de regresión no incluye `configuration_fingerprint`. El entry point lo calcula pero no lo persiste. Esto rompe la reproducibilidad: no se puede reconstruir qué configuración produjo un verdict específico. | E-6.3-002 | Pilar: Reproducibilidad / ENGINEERING_PRINCIPLES §IV | **Fase 6** | OPEN |
| **GAP-6.3-03** | CI verifica inmutabilidad de `tests/fixtures/` (ruta legacy) pero no de `tests/corpus/canonical/` (ruta canónica). Mutaciones a la baseline sellada no serían detectadas por CI. | E-6.3-003, HITO 6.0 E-6.0-006, E-6.0-012 | Pilar: Integridad / NADR-21 §5.4 R19 | **Fase 6** | OPEN |
| **GAP-6.3-04** | Branch protection y required status checks son NO DEMOSTRADOS desde el repositorio. No hay evidencia de que el job `regression-gates` bloquee merges a main. | E-6.3-004 | Pilar: Enforcement / ADR Master §10 DoD Level B | **Fase 6** | NO DEMOSTRADO |
| **GAP-6.3-05** | No existen perfiles diferenciados de ejecución (PR smoke, full merge, nightly). Un único workflow con triggers push/PR. Sin schedules, sin workflow_dispatch, sin paths filter. | E-6.3-005, E-6.3-011 | Pilar: Perfiles / ROADMAP | **Fase 6 (DC)** | OPEN |
| **GAP-6.3-06** | El reporte de regresión no incluye la identity chain completa: falta `manifest_hash`, `parameter_identity`, `result_identity`, `commit_sha`, `schema_version`. Solo incluye `corpus_version` y `configuration_fingerprint` (que tampoco está). | E-6.3-002, E-6.3-012 | Pilar: Reproducibilidad / ADR Master §3 | **Fase 6** | OPEN |
| **GAP-6.3-07** | Exit code 1 es ambiguo: puede significar WARNING (veredicto científico) o crash (fallo de ejecución) o baseline integrity failure. Un consumidor CI no puede distinguirlos. | HITO 6.2 E-6.2-004, E-6.3-008 | Pilar: Error Handling / NADR-24 §5.4 R15-R19 | **Fase 6 (DC)** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-6.3-A | El job `regression-gates` invoca `run_regression.py`. | RECHAZADA | E-6.3-001. El job ejecuta `pytest -m "regression"` que selecciona 0 tests. | La "Regression Gate Illusion" es real: el job existe pero no ejecuta la verificación. |
| H-6.3-B | El reporte de regresión incluye toda la identity chain necesaria para reproducibilidad. | RECHAZADA | E-6.3-002, E-6.3-012. Faltan `configuration_fingerprint`, `manifest_hash`, `parameter_identity`, `result_identity`, `commit_sha`, `schema_version`. | La reproducibilidad está incompleta. |
| H-6.3-C | CI protege la integridad de la baseline canónica. | RECHAZADA | E-6.3-003. CI protege `tests/fixtures/`, no `tests/corpus/canonical/`. | Mutaciones a la baseline no serían detectadas. |
| H-6.3-D | Branch protection está configurado y bloquea merges. | NO VERIFICABLE | E-6.3-004. Configuración del servidor GitHub, no accesible desde el repositorio. | Destino: NO DEMOSTRADO. Requiere acceso al servidor para verificar. |
| H-6.3-E | La ejecución del corpus completo es factible en CI. | CONFIRMADA | E-6.3-007. 3.74 segundos, ~28.8 MB, sin dependencias externas. | El corpus puede ejecutarse en cada push/PR sin timeout issues. |
| H-6.3-F | La propagación de fallo no tiene neutralización. | CONFIRMADA | E-6.3-006. No hay continue-on-error, \|\| true, exit 0, set +e, if:. | Un fallo en el job propaga correctamente como fallo del workflow. |
| H-6.3-G | Exit code 2 (HARD_FAIL) se propaga correctamente. | CONFIRMADA | E-6.3-008. Exit code 2 confirmado en ejecución real. | La taxonomía NADR-19 funciona correctamente cuando el entry point se ejecuta. |
| H-6.3-H | Existe un workflow nightly para ejecución completa del corpus. | RECHAZADA | E-6.3-005, E-6.3-011. Solo `ci.yml` existe. Sin schedules. | No hay perfil nightly. |
| H-6.3-I | El pipeline de extracción tiene dependencias externas (red, GPU, API). | RECHAZADA | E-6.3-007. PyMuPDF es puramente local, sin imports de requests, http, api, gpu, cuda, torch. | CI puede ejecutar sin infraestructura externa. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué eventos de CI ejecutan actualmente alguna forma de Continuous Verification?

**Estado actual verificado:**

1. Triggers: `push [main, develop]`, `pull_request [main]` (E-6.3-005).
2. Sin schedules, sin workflow_dispatch, sin paths filter.
3. Un único workflow (`ci.yml`).
4. Job `regression-gates` se ejecuta en estos triggers.

**Respuesta forense:**

Los eventos que disparan el job `regression-gates` son:
- Push a main
- Push a develop
- Pull request a main

Sin embargo, el job ejecuta `pytest -m "regression"` que selecciona 0 tests. Por lo tanto, **ningún evento ejecuta realmente Continuous Verification**. Los eventos disparan un job nominal que no ejecuta la verificación.

**Implicación:**

La "Regression Gate Illusion" se ejecuta en cada push/PR pero no verifica nada. Para que haya Continuous Verification real, se necesita:
1. Conectar el job al entry point correcto (`run_regression.py`), O
2. Agregar tests con marker `regression` que invoquen el production pipeline + baseline sellada.

### 16.2 ¿Cuál es el entry point exacto utilizado por CI?

**Estado actual verificado:**

1. Job `regression-gates` ejecuta: `python -m pytest -m "regression" -v --tb=short --no-header` (E-6.3-001).
2. `pytest -m "regression"` selecciona 0 tests (HITO 6.0 E-6.0-002, E-6.0-003).

**Respuesta forense:**

El entry point utilizado por CI es `pytest -m "regression"`. Este comando selecciona 0 tests y retorna exit code 5 (no tests collected).

**Implicación:**

El entry point de CI no ejecuta ninguna verificación. Es un entry point vacío.

### 16.3 ¿Ese entry point ejecuta realmente el production pipeline identificado en HITO 6.1?

**Respuesta forense:**

NO. El entry point de CI (`pytest -m "regression"`) selecciona 0 tests, por lo que no ejecuta nada. El production pipeline (`build_extraction_pipeline()`) no es invocado.

**Implicación:**

Para que el entry point de CI ejecute el production pipeline, se necesita:
1. Agregar tests con marker `regression` que invoquen `run_regression.py`, O
2. Cambiar el entry point de CI a `python tools/evaluation/run_regression.py ...`.

### 16.4 ¿Consume realmente la baseline identificada en HITO 6.2?

**Respuesta forense:**

NO. El entry point de CI (`pytest -m "regression"`) selecciona 0 tests, por lo que no consume nada. La baseline sellada (manifest v3.9, 21 oráculos) no es consumida.

**Implicación:**

Para que el entry point de CI consuma la baseline, se necesita:
1. Materializar los 14 PDFs no trackeados (HITO 6.2 GAP-6.2-01, GAP-6.2-02), Y
2. Invocar `run_regression.py` con `--corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf`.

### 16.5 ¿Ejecuta realmente `DoubleProtectionMechanism`?

**Respuesta forense:**

NO desde CI (porque el entry point selecciona 0 tests). SÍ cuando se ejecuta manualmente `run_regression.py` (E-6.1-011, E-6.1-012, HITO 6.1).

**Implicación:**

`DoubleProtectionMechanism` existe y funciona correctamente cuando se invoca, pero CI no lo invoca.

### 16.6 ¿Cómo se transforma el resultado del mecanismo en un resultado de proceso?

**Estado actual verificado:**

1. `DoubleProtectionMechanism.evaluate()` retorna `DoubleProtectionResult` con `verdict` (PASS/WARNING/HARD_FAIL) (E-6.1-012).
2. `build_regression_report()` agrega los verdicts por documento y calcula `corpus_verdict`.
3. `run_regression.py` mapea `corpus_verdict` a exit code: `sys.exit(EXIT_PASS)` / `sys.exit(EXIT_WARNING)` / `sys.exit(EXIT_HARD_FAIL)`.

**Respuesta forense:**

La transformación es:
```text
DoubleProtectionResult.verdict (por documento)
    → corpus_verdict (agregado)
    → sys.exit(0/1/2)
```

**Implicación:**

La transformación es correcta cuando `run_regression.py` se ejecuta. El gap es que CI no invoca `run_regression.py`.

### 16.7 ¿Cuáles son los exit codes reales para cada clase de resultado?

**Estado actual verificado:**

1. `EXIT_PASS = 0` (NADR-19 §5.5 R22).
2. `EXIT_WARNING = 1` (NADR-19 §5.5 R22).
3. `EXIT_HARD_FAIL = 2` (NADR-19 §5.5 R22).
4. Crash (Python default) → exit code 1.
5. No tests collected (pytest) → exit code 5.

**Respuesta forense:**

| Resultado | Exit code | Ambigüedad |
|---|---|---|
| PASS | 0 | Ninguna |
| WARNING | 1 | Indistinguible de crash |
| HARD_FAIL | 2 | Ninguna |
| Crash | 1 | Indistinguible de WARNING |
| Baseline integrity failure | 1 | Indistinguible de WARNING |
| No tests collected | 5 | Ninguna (pero no es regression) |

**Implicación:**

Exit code 1 es ambiguo. Un consumidor CI no puede distinguir WARNING (veredicto científico) de crash (fallo de ejecución). Esto alimenta DC-6.4 (taxonomía de estados operacionales).

### 16.8 ¿Existe propagación inequívoca de fallo desde dominio → proceso → job?

**Estado actual verificado:**

1. Dominio → proceso: exit code 0/1/2 (E-6.3-008).
2. Proceso → job: sin neutralización (E-6.3-006).
3. Job → workflow: sin neutralización (E-6.3-006).

**Respuesta forense:**

SÍ, la propagación es inequívoca **dentro del workflow**. No hay `continue-on-error`, `|| true`, `exit 0`, `set +e` ni condiciones `if:`. Un exit code distinto de 0 propaga como fallo del job y del workflow.

**Implicación:**

La propagación dentro del workflow es correcta. El gap es:
1. CI no invoca el entry point correcto (GAP-6.3-01).
2. Branch protection no está demostrado (GAP-6.3-04).

### 16.9 ¿Existe `continue-on-error`, excepciones absorbidas, `exit 0` o equivalentes que puedan neutralizar un fallo?

**Estado actual verificado:**

1. Búsqueda en `.github/workflows/ci.yml`: 0 resultados para `continue-on-error`, `|| true`, `exit 0`, `set +e`, `if:` (E-6.3-006).

**Respuesta forense:**

NO. No hay mecanismos de neutralización de fallo en el workflow.

**Implicación:**

La propagación de fallo es limpia. Esto es un hallazgo positivo.

### 16.10 ¿Qué superficie queda realmente protegida por el CI actual?

**Estado actual verificado:**

1. `tests/fixtures/` protegida por `git diff --exit-code` (E-6.3-003).
2. `tests/corpus/canonical/` NO protegida (E-6.3-003).
3. Branch protection NO DEMOSTRADO (E-6.3-004).

**Respuesta forense:**

La única superficie protegida es `tests/fixtures/`, que es la ruta legacy (caches y fixtures sintéticos, HITO 6.0 E-6.0-012). La baseline canónica (`tests/corpus/canonical/`) NO está protegida.

**Implicación:**

Mutaciones a la baseline sellada no serían detectadas por CI. Esto viola la invariante de inmutabilidad de SealedOracle a nivel de CI.

### 16.11 ¿Existe enforcement real sobre merge/branch, o eso está NO DEMOSTRADO?

**Estado actual verificado:**

1. Branch protection: configuración del servidor GitHub, no accesible desde el repositorio (E-6.3-004).
2. Required status checks: configuración del servidor GitHub, no accesible desde el repositorio (E-6.3-004).
3. No hay archivos de configuración de branch protection en `.github/`.

**Respuesta forense:**

NO DEMOSTRADO. No hay evidencia en el repositorio de que branch protection esté configurado ni de que el job `regression-gates` sea un required status check. Es posible que sí lo esté (configuración del servidor), pero no hay evidencia en el código.

**Implicación:**

Sin evidencia de enforcement, no se puede afirmar que la "Ilusión del Regression Gate" tenga impacto real en el desarrollo. Si branch protection no está configurado, el job puede fallar sin bloquear merges.

### 16.12 ¿Qué evidencia queda disponible para reconstruir una ejecución?

**Estado actual verificado:**

1. Reporte JSON: `corpus_nss`, `corpus_verdict`, `corpus_version`, `documents` (con métricas detalladas), `generated_at`, contadores (E-6.3-012).
2. Reporte Markdown: mismo contenido en formato legible.
3. NO incluidos: `configuration_fingerprint`, `manifest_hash`, `parameter_identity`, `result_identity`, `commit_sha`, `schema_version` (E-6.3-002, E-6.3-012).

**Respuesta forense:**

La evidencia disponible es **parcial**:
- ✅ Incluído: corpus_nss, corpus_verdict, corpus_version, documents (con métricas), generated_at, contadores.
- ❌ NO incluído: configuration_fingerprint, manifest_hash, parameter_identity, result_identity, commit_sha, schema_version.

**Implicación:**

La reproducibilidad es incompleta. Si un verdict cambia entre ejecuciones, no se puede determinar si fue por un cambio en el código, en la configuración, o en la baseline. Esto alimenta GAP-6.3-02 y GAP-6.3-06.

### 16.13 ¿La ejecución CI es reproducible respecto de baseline, configuración, parámetros e identidad?

**Estado actual verificado:**

1. Baseline: corpus_version incluida en reporte. manifest_hash NO incluido.
2. Configuración: configuration_fingerprint NO incluido (E-6.3-002).
3. Parámetros: parameter_identity NO incluido.
4. Identidad: result_identity NO incluido. commit_sha NO incluido.

**Respuesta forense:**

NO. La ejecución CI no es completamente reproducible. La identity chain está incompleta en el reporte.

**Implicación:**

Sin la identity chain completa, no se puede afirmar que dos ejecuciones con el mismo verdict fueron producidas por la misma configuración. Esto es crítico para Fase 6 porque el gate debe ser reproducible.

### 16.14 ¿Qué perfiles de ejecución existen actualmente?

**Estado actual verificado:**

1. Un único workflow (`ci.yml`) (E-6.3-011).
2. Triggers: push [main, develop], pull_request [main] (E-6.3-005).
3. Sin schedules, sin workflow_dispatch, sin paths filter.

**Respuesta forense:**

Un único perfil:
- **PR/push profile**: se ejecuta en cada push a main/develop y en cada PR a main. Ejecuta el corpus completo (si el entry point fuera correcto).

Sin perfiles diferenciados:
- ❌ No hay perfil PR smoke (corpus reducido).
- ❌ No hay perfil nightly (ejecución programada).
- ❌ No hay perfil manual (workflow_dispatch).

**Implicación:**

El corpus completo (3.74s) se ejecuta en todo push/PR, incluso cambios irrelevantes. Esto es factible por el tiempo de ejecución, pero no es óptimo. Esto alimenta DC-6.5 (perfiles de ejecución).

### 16.15 ¿Qué limitaciones operacionales existen para ejecutar Continuous Verification en CI?

**Estado actual verificado:**

1. Tiempo de ejecución: 3.74 segundos para 21 documentos (E-6.3-007).
2. Tamaño del corpus: ~28.8 MB (61 archivos) (E-6.3-007).
3. Dependencias externas: ninguna (PyMuPDF es local) (E-6.3-007).
4. GPU requerida: no (E-6.3-007).
5. Red requerida: no (E-6.3-007).
6. API keys requeridas: no (E-6.3-007).
7. Runner compatible: ubuntu-latest (E-6.3-007).
8. Materialización de PDFs: 14 de 21 no trackeados (HITO 6.2 GAP-6.2-01, GAP-6.2-02).

**Respuesta forense:**

Las limitaciones operacionales son:
- ✅ **Tiempo**: 3.74 segundos (sin limitación).
- ✅ **Tamaño**: ~28.8 MB (sin limitación).
- ✅ **Dependencias**: ninguna (sin limitación).
- ✅ **GPU/red/API**: no requeridas (sin limitación).
- ❌ **Materialización**: 14 de 21 PDFs no trackeados (limitación bloqueante).

**Implicación:**

La ejecución es factible en CI desde el punto de vista operacional (tiempo, tamaño, dependencias). La única limitación es la materialización de PDFs, que es un gap de HITO 6.2 (GAP-6.2-01, GAP-6.2-02).

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-6.3** | Frontera CI ↔ dominio: pytest marker vs invocación directa vs wrapper | HITO 6.0 E-6.0-001, E-6.0-002; HITO 6.1 E-6.1-001, E-6.1-007; HITO 6.3 E-6.3-001, GAP-6.3-01 | Ausente (CI usa pytest marker que selecciona 0 tests) | **Fase 6** |
| **DC-6.5** | Perfil de ejecución por evento (PR smoke vs merge full vs nightly) | HITO 6.3 E-6.3-005, E-6.3-011, GAP-6.3-05 | Ausente (un único perfil) | **Fase 6** |
| **DC-6.12** | ¿Cómo conectar el job `regression-gates` al entry point `run_regression.py`? | E-6.3-001, GAP-6.3-01 | Ausente | **Fase 6** |
| **DC-6.13** | ¿Qué campos de la identity chain deben incluirse en el reporte de regresión? | E-6.3-002, E-6.3-012, GAP-6.3-02, GAP-6.3-06 | Ausente (solo corpus_version incluido) | **Fase 6** |
| **DC-6.14** | ¿Debe CI verificar la integridad de `tests/corpus/canonical/` además de `tests/fixtures/`? | E-6.3-003, GAP-6.3-03 | Ausente (solo tests/fixtures/ verificado) | **Fase 6** |
| **DC-6.15** | ¿Cómo verificar branch protection si no es accesible desde el repositorio? | E-6.3-004, GAP-6.3-04 | NO DEMOSTRADO | **Fase 6** |

> **Nota de gobernanza:** DC-6.12 a DC-6.15 son nuevos, generados por este HITO. No resuelven nada; identifican decisiones que el ADR/NADR de Fase 6 deberá tomar.

---

## 21. CIERRE DEL HITO 6.3

Este HITO confirma que **la "Regression Gate Illusion" identificada en HITO 6.0 es operacionalmente real**: el job `regression-gates` existe, el entry point `run_regression.py` existe, pero no están conectados. CI ejecuta `pytest -m "regression"` que selecciona 0 tests. El entry point real no es invocado.

**Hallazgos positivos confirmados:**
- La propagación de fallo es limpia (sin neutralización).
- El exit code 2 (HARD_FAIL) funciona correctamente cuando el entry point se ejecuta.
- La ejecución es factible en CI (3.74s, ~28.8 MB, sin dependencias externas).

**Gaps confirmados:**
1. CI no invoca el entry point real (BLOCKING).
2. Reporte sin configuration_fingerprint (rompe reproducibilidad).
3. Sin protección de integridad sobre baseline canónica.
4. Enforcement NO DEMOSTRADO (branch protection no accesible desde repositorio).
5. Sin perfiles diferenciados (un único workflow push/PR).
6. Identity chain incompleta en reporte.
7. Exit code 1 ambiguo (WARNING vs crash).

El gap NO es de factibilidad operacional (el corpus se ejecuta en 3.74s sin dependencias externas) sino de **conexión** (CI no invoca el entry point correcto) y de **reproducibilidad** (reporte sin identity chain completa) y de **enforcement** (branch protection no demostrable).

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** Todas las condiciones de METHODOLOGY_FOR_FORENSIC_HITOs.md §8.1 verificadas:
- [x] Metadata completa y consistente.
- [x] Changelog actualizado a la versión de cierre.
- [x] Límite epistemológico declarado.
- [x] Alcance auditado completo.
- [x] Fuentes de evidencia listadas.
- [x] 100% de módulos del alcance auditados o explícitamente marcados como `NO DEMOSTRADO`.
- [x] Todas las evidencias tienen ID estable.
- [x] Todas las evidencias tienen severidad clasificada.
- [x] Todas las evidencias relevantes separan `Observed / Required / Decision`.
- [x] Todos los gaps tienen evidencia vinculada.
- [x] Todos los gaps tienen fase destino explícita.
- [x] Todas las hipótesis están cerradas como `CONFIRMADA`, `RESUELTA`, `RECHAZADA` o `NO VERIFICABLE` (con destino explícito).
- [x] Cero hipótesis abiertas sin destino.
- [x] Cero contradicciones no documentadas con HITOs previos.
- [x] Todos los IDs `E`, `GAP`, `OBS`, `H` son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.
**Verificación de cadena de gobernanza:** ADR Master §6, §10 → ADR_05 §5, §7 → NADR-19 §5.5 R22 → HITO 6.0 → HITO 6.1 → HITO 6.2 → HITO 6.3 → (futuro) HITO 6.4 → ADR_06 / NADRs → Execution Plan.
**Contradicciones con HITOs previos:** Ninguna. HITO 6.0 identificó la Regression Gate Illusion. HITO 6.1 confirmó el sujeto. HITO 6.2 confirmó la baseline. HITO 6.3 confirma operacionalmente que CI no invoca el sujeto contra la baseline. Esto es consistente y complementario.
**Decision Candidates generados:** DC-6.12 (conexión CI ↔ entry point), DC-6.13 (identity chain en reporte), DC-6.14 (protección de integridad de baseline), DC-6.15 (verificación de branch protection). DC-6.3 y DC-6.5 alimentados con evidencia adicional.
**Siguiente paso recomendado:** Redactar HITO 6.4 (Dependency Graph & Readiness Assessment) para consolidar findings de HITOs 6.0-6.3, construir el grafo de dependencias, y determinar qué Decision Candidates son bloqueantes y cuáles son paralelizables. Con HITO 6.4 completo, evaluar si se requiere ADR_F17_BIS_06 como ADR de Fase o si bastan NADRs de extensión.