# HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-09-24
**Fecha de congelamiento:** 2026-09-24
**Fase:** 17-BIS — Fase 6 (Continuous Verification)
**Tipo de artefacto:** Forensic Flow Audit / Dimension Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- ADR_F17_BIS_MASTER.md (FROZEN) §3, §5
- ADR_F17_BIS_05.md (FROZEN) §3 D3, §5, §7
- ENGINEERING_PRINCIPLES.md (FROZEN) §II, §IV
- HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md v1.0.0 (FROZEN)
- HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md v1.0.0 (FROZEN)
- METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN)
- FASE_5_DEFERRED_FINDINGS_REGISTER.md v0.21.0 (ARCHIVED) — O-5.0-1, H-5.2-1
- FASE_5_HANDOFF.md v1.0.1 (FROZEN)
- `tools/evaluation/run_regression.py`
- `infra/fs/corpus_repository.py`
- `infra/fs/ground_truth_store.py`
- `core/benchmark/topology/regression/adapter.py`
- `core/benchmark/topology/regression/errors.py`
- `core/benchmark/ground_truth/errors.py`
- `core/benchmark/ground_truth/models.py`
- `core/benchmark/ground_truth/identity.py`
- `core/benchmark/corpus/services.py`
- `tests/corpus/canonical/manifest.json`
- `tests/corpus/canonical/` (estructura completa)
- `.gitignore`
- `.github/workflows/ci.yml`
**Mandato:** ¿Existe una forma reproducible, íntegra, identificable y compatible con el modelo de confianza de F17-BIS para que el mecanismo de Continuous Verification consuma exactamente la baseline canónica sellada y sus artefactos físicos de referencia?
**Síntesis:** La baseline sellada de Fase 5 (21 identidades, manifest v3.9) existe localmente con contratos de integridad e identidad completos. Sin embargo, 14 de 21 PDFs no están trackeados en git, no existe mecanismo de materialización en CI, y el Imperative Shell de regresión no verifica la existencia de PDFs antes de la extracción ni traduce errores de infraestructura a exit codes tipados. El consumo de la baseline es posible localmente pero NO es reproducible en un entorno de ejecución externo (CI).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-24 | Emisión inicial. |
| 1.0.0-FROZEN | 2026-09-24 | Cierre formal del HITO con evidencia completa. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la disponibilidad, materialización, identidad e integridad de la baseline canónica sellada por Fase 5, vista desde el punto de vista de su consumo operativo por Continuous Verification. La auditoría cubrió: el contrato del Imperative Shell de regresión (`run_regression.py`), los adaptadores de infraestructura (`LocalFileSystemCorpusLoader`, `LocalFileSystemGroundTruthReader`, `LocalFileSystemGroundTruthArtifactAdapter`), el contrato de verificación (`RegressionAdapter`), los contratos de identidad (`ManifestFingerprintCalculator`, `OracleSemanticIdentityCalculator`), el contrato de inmutabilidad (`SealedOracle`), la estructura física del corpus canónico, el comportamiento ante condiciones de error, y la jerarquía de errores del dominio.

**Hallazgo central:**

> La baseline sellada de Fase 5 existe localmente con contratos de integridad e identidad completos y verificables. El Imperative Shell de regresión (`run_regression.py`) consume correctamente el manifest, los Ground Truths y los PDFs, y verifica identidad, estado sellado e integridad criptográfica antes de evaluar. Sin embargo, el consumo NO es reproducible en un entorno de ejecución externo (CI) porque: (1) 14 de 21 PDFs no están trackeados en git, (2) no existe mecanismo de materialización, (3) la ausencia de PDFs produce un crash no tipado de PyMuPDF en vez de un error de dominio, y (4) el entry point no usa `run_entry(main)` por lo que los crashes producen exit code 1 ambiguo (indistinguible de WARNING).

**Defectos dominantes confirmados:**

1. **PDFs no trackeados (E-6.2-001):** 14 de 21 PDFs del corpus canónico están excluidos de git por `.gitignore`. Un clone fresco no puede ejecutar `run_regression.py` contra el corpus completo.
2. **Ausencia de materialización (E-6.2-002):** No existe ningún mecanismo (script, artifact download, object storage, cache) para obtener los PDFs en un entorno de ejecución externo.
3. **Crash no tipado ante PDF ausente (E-6.2-003):** La ausencia de un PDF produce `pymupdf.FileNotFoundError` (crash de librería), no un error de dominio con mensaje indexable.
4. **Exit code ambiguo (E-6.2-004):** `run_regression.py` no usa `run_entry(main)`. Los crashes producen exit code 1 (default de Python), indistinguible de `EXIT_WARNING = 1` (NADR-19 §5.5 R22).
5. **PDF huérfano (E-6.2-005):** `doc_06_johnstone.pdf` existe físicamente (563435 bytes) pero NO está en el manifest ni tiene Ground Truth. Es un artefacto de quarantine (H-5.2-1).

**Hallazgo positivo confirmado:**

6. **Contratos de integridad e identidad completos (E-6.2-006, E-6.2-007, E-6.2-008):** El `RegressionAdapter` verifica identidad documental, completitud biyectiva, estado sellado e integridad criptográfica (oracle_hash) antes de evaluar. Los contratos de identidad (`ManifestFingerprintCalculator`, `OracleSemanticIdentityCalculator`) son deterministas y sensibles a mutaciones relevantes.

**Veredicto:** La baseline es consumible localmente con garantías de integridad e identidad. NO es consumible en CI sin un mecanismo de materialización de PDFs. El gap es operacional (materialización + error handling), no arquitectónico (los contratos existen y son correctos).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código.

Específicamente, este HITO:
- **NO** decide cómo materializar los PDFs en CI (S3, artifacts, self-hosted, etc.).
- **NO** decide si los PDFs deben entrar en git.
- **NO** resuelve el problema de copyright/distribución.
- **NO** propone un nuevo formato de manifest.
- **NO** modifica el contrato de `SealedOracle`.
- **NO** re-sella la baseline.
- **NO** decide la taxonomía de estados operacionales (pertenece a DC-6.4 / HITO 6.3).
- **NO** diseña el CI adapter (pertenece a HITO 6.3).

Este HITO **SÍ**:
- Demuestra qué artefactos físicos necesita el verification subject.
- Demuestra dónde están actualmente esos artefactos.
- Demuestra qué identidad canónica tienen.
- Demuestra qué mecanismos de integridad existen.
- Demuestra qué significa `SEALED` para cada artefacto consumido.
- Demuestra que NO existe mecanismo reproducible de materialización.
- Demuestra el comportamiento ante artefacto ausente/corrupto/incompatible.
- Demuestra la distinción entre canonical corpus y fixtures/legacy.
- Identifica gaps y Decision Candidates.

### 2.2 Método forense

1. Cargar fuentes normativas (ADR Master §3, §5; ADR_05 §3 D3, §5; ENGINEERING_PRINCIPLES §II, §IV).
2. Cargar HITOs previos como insumo (6.0: Regression Gate Illusion; 6.1: sujeto de verificación).
3. Cargar evidencia heredada de Fase 5 (O-5.0-1: copyright; H-5.2-1: doc_06 quarantine).
4. Inspeccionar contratos del Imperative Shell (`run_regression.py`).
5. Inspeccionar adaptadores de infraestructura (`corpus_repository.py`, `ground_truth_store.py`).
6. Inspeccionar contrato de verificación (`RegressionAdapter`).
7. Inspeccionar contenido real del corpus canónico (`manifest.json`, estructura de archivos, GT ejemplo).
8. Ejecutar `run_regression.py` con condiciones de error controladas (PDF ausente, corpus ausente, corpus incompleto). Estas ejecuciones son read-only: no modifican código, no modifican artefactos sellados, solo observan la respuesta del sistema ante condiciones de fallo.
9. Inspeccionar contratos de identidad (`ManifestFingerprintCalculator`, `OracleSemanticIdentityCalculator`).
10. Inspeccionar contrato de inmutabilidad (`SealedOracle`, `GroundTruthLifecycleState`).
11. Inspeccionar jerarquía de errores del dominio (regression, ground_truth).
12. Consolidar gaps solo con evidencia demostrada.

### 2.3 Axioma de entrada

> **La baseline de Fase 5 no se vuelve a construir, recalibrar ni modificar como parte de HITO 6.2.** La baseline sellada (corpus v3.9, manifest `727782fe...`, 21 oráculos) es tratada como referencia read-only. Cualquier deficiencia de consumo se registra como gap/DC, no se ejecuta.

### 2.4 Relación con HITOs previos

| HITO | Qué demostró | Qué hereda 6.2 |
|---|---|---|
| HITO 6.0 | Regression Gate Illusion: CI tiene job nominal que no ejecuta verificación. PDFs en `.gitignore`. No materialización. | E-6.0-004, E-6.0-005, E-6.0-006 como evidencia de contexto. 6.2 profundiza en las consecuencias. |
| HITO 6.1 | Sujeto de verificación existe: `run_regression.py` invoca `build_extraction_pipeline()`. Correspondencia production ↔ verification completa. | E-6.1-001, E-6.1-002, E-6.1-007 como insumo. 6.2 audita si los artefactos que el sujeto necesita están disponibles. |
| Fase 5 (Findings Register) | O-5.0-1: PDFs no trackeados por copyright. H-5.2-1: doc_06 excluido por OCR. | Evidencia heredada. 6.2 no re-descubre, cita y profundiza consecuencias. |

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos / Archivos | Estado |
|---|---|---|
| Imperative Shell de regresión | `tools/evaluation/run_regression.py` (`parse_args()`, `main()`) | 100% auditado |
| Adaptador de corpus (lectura) | `infra/fs/corpus_repository.py` (`LocalFileSystemCorpusLoader`) | 100% auditado |
| Adaptador de GT (lectura) | `infra/fs/ground_truth_store.py` (`LocalFileSystemGroundTruthReader`, `LocalFileSystemGroundTruthArtifactAdapter`) | 100% auditado |
| Contrato de verificación | `core/benchmark/topology/regression/adapter.py` (`RegressionAdapter`) | 100% auditado |
| Contrato de identidad (manifest) | `core/benchmark/corpus/services.py` (`ManifestFingerprintCalculator.compute_hash()`) | 100% auditado |
| Contrato de identidad (oracle) | `core/benchmark/ground_truth/identity.py` (`OracleSemanticIdentityCalculator.calculate()`) | 100% auditado |
| Contrato de inmutabilidad | `core/benchmark/ground_truth/models.py` (`SealedOracle`, `GroundTruthLifecycleState`, `GroundTruthDraft`) | 100% auditado |
| Jerarquía de errores (regression) | `core/benchmark/topology/regression/errors.py` | 100% auditado |
| Jerarquía de errores (ground_truth) | `core/benchmark/ground_truth/errors.py` | 100% auditado |
| Manifest canónico real | `tests/corpus/canonical/manifest.json` | 100% auditado |
| Estructura física del corpus | `tests/corpus/canonical/` (recursivo) | 100% auditado |
| Ground Truth ejemplo | `tests/corpus/canonical/ground_truth/doc_01_single.json` | Parcial (primeros 50 líneas) |
| Comportamiento ante error | Ejecuciones controladas de `run_regression.py` | 100% auditado (3 condiciones) |
| CI workflow | `.github/workflows/ci.yml` | Referenciado (auditoría completa en HITO 6.0) |
| `.gitignore` | Reglas de exclusión | Referenciado (auditoría completa en HITO 6.0) |
| Production pipeline | `apps/bootstrap/pipeline_factory.py` | Referenciado (auditoría completa en HITO 6.1) |

**Fuera de scope:**
- Mecanismo interno de `PyMuPDFProvider.extract()` (HITO 6.1 referenciado)
- Mecanismo interno de `DoubleProtectionMechanism.evaluate()` (HITO 6.3)
- Semántica de exit codes en CI (HITO 6.3)
- Infraestructura CI (HITO 6.3)
- Performance de ejecución (HITO 6.4)
- Contenido completo de los 21 Ground Truths (solo estructura verificada)
- Contenido de `curation_checklist.json` (no relevante para consumo)

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §3 | Separación Integridad / Identidad / Regresión |
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §5 | Invariantes: Zero Partial Sealing, Determinismo, Desacoplamiento de Identidades |
| ADR (normativa) | `ADR_F17_BIS_05.md` §3 D3 | Identidad, Sealing y Autoridad Única |
| ADR (normativa) | `ADR_F17_BIS_05.md` §5 | Cláusula de relación Fase 5 → Fase 6 |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §II | Functional Core / Imperative Shell, Inmutabilidad |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §IV | Cero Fallos Silenciosos, Trazabilidad Absoluta |
| HITO previo (forense) | `HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md` | Regression Gate Illusion, PDFs en .gitignore |
| HITO previo (forense) | `HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md` | Sujeto de verificación, correspondencia |
| Findings Register (heredado) | `FASE_5_DEFERRED_FINDINGS_REGISTER.md` v0.21.0, O-5.0-1 | Decisión de ownership: PDFs no trackeados por copyright |
| Findings Register (heredado) | `FASE_5_DEFERRED_FINDINGS_REGISTER.md` v0.21.0, H-5.2-1 | doc_06 excluido por OCR, preservado como quarantine |
| Handoff (heredado) | `FASE_5_HANDOFF.md` v1.0.1 | Estado de cierre Fase 5, carry-forwards |
| Código (runtime) | `tools/evaluation/run_regression.py` | Imperative Shell: qué lee, cómo verifica, cómo ejecuta |
| Código (runtime) | `infra/fs/corpus_repository.py` | Adaptador de corpus: fail-fast, atomicidad |
| Código (runtime) | `infra/fs/ground_truth_store.py` | Adaptador de GT: lectura, listado |
| Código (runtime) | `core/benchmark/topology/regression/adapter.py` | Contrato de verificación: 4 verificaciones |
| Código (runtime) | `core/benchmark/corpus/services.py` | Identidad del manifest: framing |
| Código (runtime) | `core/benchmark/ground_truth/identity.py` | Identidad del oracle: framing |
| Código (runtime) | `core/benchmark/ground_truth/models.py` | Inmutabilidad: SealedOracle frozen |
| Código (runtime) | `core/benchmark/topology/regression/errors.py` | Jerarquía de errores de regresión |
| Código (runtime) | `core/benchmark/ground_truth/errors.py` | Jerarquía de errores de ground truth |
| Artefacto (runtime) | `tests/corpus/canonical/manifest.json` | Contenido real: v3.9, 21 docs, hashes |
| Artefacto (runtime) | `tests/corpus/canonical/` (estructura) | Archivos físicos: 22 PDFs, 21 GTs, lineage |
| Artefacto (runtime) | `tests/corpus/canonical/ground_truth/doc_01_single.json` | Estructura de un GT sellado |
| Ejecución (forense) | `run_regression.py` con 3 condiciones de error | Comportamiento ante fallo |
| Configuración (runtime) | `.gitignore` | Reglas de exclusión de corpus |
| CI (runtime) | `.github/workflows/ci.yml` | Job regression-gates (referenciado de HITO 6.0) |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Baseline Sealing → Physical Artifacts (qué produce Fase 5)

```text
Fase 5 (SealGroundTruthUseCase)
    │
    ├── Para cada documento:
    │       │
    │       ├── OracleValidityContract.validate()
    │       ├── BaselineCompletenessVerifier.verify()
    │       ├── OracleSemanticIdentityCalculator.calculate(nodes)
    │       │       ▼
    │       │   oracle_hash (SHA-256 determinista)
    │       │
    │       ├── ManifestLineageSealer.seal_manifest_with_ground_truth()
    │       │       ▼
    │       │   manifest con ground_truth_state="sealed" + oracle_hash
    │       │
    │       └── write_ast_json_atomic()
    │               ▼
    │           ground_truth/{doc_id}.json (artefacto físico)
    │
    ├── ManifestFingerprintCalculator.compute_hash()
    │       ▼
    │   manifest_hash (SHA-256 determinista)
    │
    └── save_manifest_dto() (tempfile + fsync + os.replace)
            ▼
        manifest.json (artefacto físico)

Artefactos físicos producidos:
    tests/corpus/canonical/manifest.json
    tests/corpus/canonical/ground_truth/{doc_id}.json  (×21)
    tests/corpus/canonical/canonicalization_lineage.json
    tests/corpus/canonical/{doc_id}_canonicalization_lineage.json  (×16)
    tests/corpus/canonical/curation_checklist.json
    tests/corpus/canonical/pdf/{doc_id}.pdf  (×22, incluye doc_06 huérfano)

Leyenda:
  [OK] artefacto existente confirmado
  [ORPHAN] artefacto físico sin entrada en manifest
```

**Estado:** [OK] para 21 identidades. [ORPHAN] para doc_06_johnstone.pdf.

### FLUJO B — Artifact → Materialization (cómo se obtienen)

```text
Entorno local (workspace del desarrollador):
    │
    ├── tests/corpus/canonical/manifest.json       [OK: trackeado en git]
    ├── tests/corpus/canonical/ground_truth/*.json  [OK: trackeados en git]
    ├── tests/corpus/canonical/pdf/doc_01-07.pdf    [OK: trackeados en git]
    └── tests/corpus/canonical/pdf/doc_08-22.pdf    [GAP: NO trackeados]
            │
            └── .gitignore: "tests/corpus/canonical/pdf/"
                → 14 PDFs ausentes en clone fresco

Entorno CI (GitHub Actions):
    │
    ├── actions/checkout@v4
    │       ▼
    │   Clone del repositorio
    │       ├── manifest.json          [OK]
    │       ├── ground_truth/*.json    [OK]
    │       ├── pdf/doc_01-07.pdf      [OK]
    │       └── pdf/doc_08-22.pdf      [MISSING]
    │
    ├── ¿Mecanismo de materialización?
    │       ├── artifact download      [NO EXISTE]
    │       ├── object storage         [NO EXISTE]
    │       ├── cache específico       [NO EXISTE]
    │       ├── wget/curl              [NO EXISTE]
    │       ├── self-hosted runner     [NO EXISTE]
    │       └── script de provisioning [NO EXISTE]
    │
    └── run_regression.py --pdf-dir tests/corpus/canonical/pdf
            │
            ├── doc_01: PDF existe → procesa OK
            ├── ...
            ├── doc_07: PDF existe → procesa OK
            ├── doc_08: PDF NO existe → pymupdf.FileNotFoundError [CRASH]
            └── (no llega a doc_09-22)

Leyenda:
  [OK] disponible en clone fresco
  [MISSING] ausente en clone fresco
  [GAP] gap confirmado
  [CRASH] error no tipado
```

**Estado:** [GAP] — 14 de 21 PDFs no están disponibles en un clone fresco. No existe mecanismo de materialización. La ejecución en CI fallaría en doc_08 con crash no tipado.

### FLUJO C — Materialization → Verification Subject (cómo se consumen)

```text
run_regression.py main()
    │
    ├── Paso 1: Cargar manifest
    │   LocalFileSystemCorpusLoader(base_path=corpus_dir)
    │       → load_raw_manifest()
    │       → fail-fast: FileNotFoundError si manifest.json no existe
    │       → RawCorpusManifestDTO.model_validate(data)
    │       ▼
    │   CorpusManifest (21 documentos, v3.9)
    │
    ├── Paso 2: Verificar completitud biyectiva
    │   LocalFileSystemGroundTruthArtifactAdapter(base_path=corpus_dir)
    │       → list_artifact_ids() → sorted stems de ground_truth/*.json
    │   RegressionAdapter.verify_completeness(manifest_ids, artifact_ids)
    │       → BaselineCompletenessVerifier.verify()
    │       → IncompleteBaselineError si falla
    │       ▼
    │   Completitud verificada (21 == 21)
    │
    ├── Paso 3: Construir pipeline de evaluación
    │   build_canonical_engine_configuration()
    │   create_topology_evaluator()
    │   build_extraction_pipeline()          ← SUT NORMATIVO (HITO 6.1)
    │   LocalFileSystemGroundTruthReader(base_path=corpus_dir)
    │   LoadGroundTruthUseCase(reader=gt_reader)
    │
    ├── Paso 4: Para cada documento (loop):
    │   │
    │   ├── 4a. Cargar oráculo
    │   │   load_gt_uc.execute(doc_id)
    │   │       → LocalFileSystemGroundTruthReader.load_ground_truth()
    │   │       → fail-fast: FileNotFoundError si GT no existe
    │   │       → tuple(read_ast_json(target_path))
    │   │   hydrate_ground_truth(document_id, nodes, state=SEALED)
    │   │       ▼
    │   │   SealedOracle (frozen=True)
    │   │
    │   ├── 4b. Verificaciones por documento (Fail-Fast)
    │   │   adapter.verify_document_identity(oracle, metadata)
    │   │       → OracleDocumentMismatchError si IDs no coinciden
    │   │   adapter.verify_sealed_state(metadata)
    │   │       → OracleNotSealedError si state != "sealed"
    │   │   adapter.verify_oracle_integrity(oracle, metadata)
    │   │       → MissingOracleHashError si oracle_hash is None
    │   │       → OracleIntegrityError si hash no coincide
    │   │
    │   ├── 4c. Generar runtime AST
    │   │   pdf_path = pdf_dir / f"{doc_id}.pdf"
    │   │   runtime_ast = extraction_pipeline.parse(str(pdf_path))
    │   │       → PyMuPDFProvider.extract(file_path)
    │   │       → fitz.open(pdf_path)
    │   │       → [CRASH: pymupdf.FileNotFoundError si PDF no existe]
    │   │       → [NO HAY VERIFICACIÓN PREVIA DE EXISTENCIA]
    │   │
    │   └── 4d. Evaluar
    │       strategy.evaluate_regression(doc_id, candidate_ast, gt_nodes)
    │           → DoubleProtectionMechanism.evaluate()
    │           ▼
    │       RegressionEvaluationReport
    │
    ├── Paso 5: Construir reporte de corpus
    │   build_regression_report()
    │       ▼
    │   RegressionReport (corpus_verdict, corpus_nss, documents)
    │
    ├── Paso 6: Escribir reportes
    │   JsonRegressionReportFormatter / MarkdownRegressionReportFormatter
    │       ▼
    │   regression_report.json / regression_report.md
    │
    └── Paso 7: Exit code
        sys.exit(0/1/2)
        [NOTE: NO usa run_entry(main). Crash → exit 1 ambiguo]

Leyenda:
  [OK] verificación existente
  [CRASH] error no tipado
  [NOTE] observación
```

**Estado:** [OK] para verificaciones de GT (identidad, estado, integridad). [CRASH] para PDF ausente (no hay verificación previa). [NOTE] para exit code ambiguo.

### FLUJO D — Error Paths (qué ocurre ante condiciones de fallo)

```text
Condición 1: --corpus-dir inexistente
    │
    ├── LocalFileSystemCorpusLoader.load_raw_manifest()
    │   → FileNotFoundError("Manifest not found: ...")
    │   → Traceback crudo → exit code 1
    │   → [NO es atrapado por run_entry]
    │   → [Exit code 1 == EXIT_WARNING: AMBIGUO]
    │
    └── Observación: El mensaje es descriptivo pero no indexable.
        No hay código [CORPUS-001] o similar.

Condición 2: --pdf-dir inexistente (corpus OK)
    │
    ├── Pasos 1-3: OK (manifest, completitud, pipeline)
    ├── Paso 4a: OK (GT cargado, SealedOracle hidratado)
    ├── Paso 4b: OK (verificaciones de GT pasan)
    ├── Paso 4c: extraction_pipeline.parse(pdf_path)
    │   → PyMuPDFProvider.extract(file_path)
    │   → fitz.open(pdf_path)
    │   → pymupdf.FileNotFoundError("no such file: '...'")
    │   → Traceback crudo → exit code 1
    │   → [NO es un error de dominio]
    │   → [NO hay verificación previa de existencia de PDF]
    │   → [Exit code 1 == EXIT_WARNING: AMBIGUO]
    │
    └── Observación: La verificación de GT pasa pero la extracción
        falla. El error es de infraestructura (PyMuPDF), no de dominio.
        No se distingue de un WARNING científico.

Condición 3: --pdf-dir parcial (solo doc_01)
    │
    ├── Pasos 1-3: OK
    ├── Paso 4 doc_01: OK (PDF existe, extrae, evalúa)
    ├── Paso 4 doc_02: extraction_pipeline.parse(pdf_path)
    │   → pymupdf.FileNotFoundError("no such file: '...doc_02_double.pdf'")
    │   → Traceback crudo → exit code 1
    │   → [Falla en el primer PDF ausente]
    │   → [No hay verificación previa de completitud de PDFs]
    │
    └── Observación: La completitud verifica GTs (21 == 21) pero
        NO verifica PDFs. El fallo ocurre en la extracción, no en
        la verificación de completitud.

Leyenda:
  [OK] paso exitoso
  [CRASH] error no tipado
  [AMBIGUO] exit code indistinguible
```

**Estado:** Los tres error paths producen exit code 1 con traceback crudo. Ninguno produce un error de dominio tipado con mensaje indexable. Ninguno distingue entre "baseline integrity failure" y "execution failure".

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

### 6.1 Artifact Inventory Matrix

| Artefacto | Ubicación | Tracking git | Identidad | Integridad | Estado |
|---|---|---|---|---|---|
| `manifest.json` | `tests/corpus/canonical/manifest.json` | ✅ Trackeado | `manifest_hash: 727782fe...` | SHA-256 recomputable vía `ManifestFingerprintCalculator` | CONFIRMADO |
| Ground Truths (×21) | `tests/corpus/canonical/ground_truth/{doc_id}.json` | ✅ Trackeados | `oracle_hash` por documento | SHA-256 recomputable vía `OracleSemanticIdentityCalculator` | CONFIRMADO |
| PDFs doc_01-07 (×7) | `tests/corpus/canonical/pdf/{doc_id}.pdf` | ✅ Trackeados | `sha256` en manifest | Verificable contra manifest | CONFIRMADO |
| PDFs doc_08-22 (×14) | `tests/corpus/canonical/pdf/{doc_id}.pdf` | ❌ NO trackeados (.gitignore) | `sha256` en manifest | Verificable contra manifest (si se materializan) | GAP |
| PDF doc_06 (×1) | `tests/corpus/canonical/pdf/doc_06_johnstone.pdf` | ❌ NO trackeado | NO en manifest | NO verificable | ORPHAN |
| `curation_checklist.json` | `tests/corpus/canonical/curation_checklist.json` | ❌ NO trackeado (.gitignore) | N/A | N/A | OUT-OF-SCOPE (no consumido por run_regression) |
| `canonicalization_lineage.json` | `tests/corpus/canonical/canonicalization_lineage.json` | ✅ Trackeado | N/A | N/A | CONFIRMADO (trazabilidad) |
| Lineage por documento (×16) | `tests/corpus/canonical/{doc_id}_canonicalization_lineage.json` | ✅ Trackeados | N/A | N/A | CONFIRMADO (trazabilidad) |

### 6.2 Identity Chain Matrix

| Identidad | Qué incluye | Qué NO incluye | Calculador | Determinista | Sensible a mutación |
|---|---|---|---|---|---|
| `manifest_hash` | corpus_version, document_id, sha256, traits (ordenados), page_count, oracle_hash, ground_truth_state | Contenido de GTs, contenido de PDFs | `ManifestFingerprintCalculator.compute_hash()` | ✅ Sí (documentos ordenados por document_id) | ✅ Sí: cualquier cambio en los 7 campos produce hash diferente |
| `oracle_hash` | node_id, node_type, strategy, payload (serializado determinista) | sequence_id, depth, parent_node_id, metadata (bboxes, pages, confidence), control_plane, segment_index, segment_count | `OracleSemanticIdentityCalculator.calculate()` | ✅ Sí (tupla ordenada) | ✅ Sí: cambio en node_id, type, strategy o payload produce hash diferente. Insensible a metadata física. |
| `sha256` (PDF) | Contenido binario del PDF | N/A | `compute_sha256()` | ✅ Sí | ✅ Sí: cualquier cambio en el PDF produce hash diferente |
| `corpus_version` | Versión semántica del corpus | N/A | Manual (string) | ✅ Sí | ✅ Sí: cambio de versión produce manifest_hash diferente |

### 6.3 Sealed Contract Matrix

| Artefacto | Estado | Mutabilidad | Verificación antes de uso | Excepción ante violación |
|---|---|---|---|---|
| `SealedOracle` (modelo) | `frozen=True` (Pydantic) | Inmutable por contrato de modelo | `hydrate_ground_truth(state=SEALED)` retorna `SealedOracle` | `ValidationError` si se intenta mutar |
| Ground Truth JSON (disco) | `ground_truth_state: "sealed"` en manifest | Mutable en disco (filesystem) | `RegressionAdapter.verify_sealed_state()` verifica estado | `OracleNotSealedError` si state != "sealed" |
| Ground Truth JSON (disco) | Integridad criptográfica | Mutable en disco (filesystem) | `RegressionAdapter.verify_oracle_integrity()` recalcula oracle_hash | `OracleIntegrityError` si hash no coincide |
| Manifest JSON (disco) | `manifest_hash` en el propio archivo | Mutable en disco (filesystem) | NO hay verificación de manifest_hash en `run_regression.py` | N/A (no se verifica) |
| PDF (disco) | `sha256` en manifest | Mutable en disco (filesystem) | NO hay verificación de sha256 del PDF en `run_regression.py` | N/A (no se verifica) |
| Escritura de GT | Protegida por `SealedOracleOverwriteError` | Inmutable por use case | `GenerateGoldenDraftUseCase` verifica estado antes de escribir | `SealedOracleOverwriteError` |
| Escritura de manifest | Atómica (tempfile + fsync + os.replace) | N/A | N/A | N/A |

**Observación crítica:** `run_regression.py` verifica la integridad del GT (oracle_hash) pero NO verifica:
1. El `manifest_hash` contra el manifest recalculado.
2. El `sha256` del PDF contra el valor en el manifest.
3. La existencia del PDF antes de intentar la extracción.

Esto significa que un PDF sustituido (mismo nombre, diferente contenido) no sería detectado por el entry point de regresión. La integridad del PDF se verifica implícitamente solo si el GT fue generado a partir de ese PDF, pero no hay verificación directa.

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-6.2-001** | P0 | `.gitignore` → `tests/corpus/canonical/pdf/`; `git ls-files tests/corpus/canonical/` → solo doc_01-07 en pdf/ | **14 de 21 PDFs no trackeados en git.** La regla `.gitignore` excluye el directorio completo. Solo 7 PDFs (agregados antes de la regla) están trackeados. Un clone fresco no tiene doc_08-22. |
| **E-6.2-002** | P0 | `.github/workflows/ci.yml` → búsqueda de download/artifact/cache/wget/curl/rclone/self-hosted → 0 resultados; HITO 6.0 E-6.0-004 | **No existe mecanismo de materialización.** Ningún step del CI descarga, cachea o materializa PDFs. No hay script de provisioning. No hay object storage. |
| **E-6.2-003** | P1 | Ejecución forense: `run_regression.py --pdf-dir /tmp/nonexistent_pdfs` → `pymupdf.FileNotFoundError: no such file: '\tmp\nonexistent_pdfs\doc_01_single.pdf'` → exit code 1 | **Crash no tipado ante PDF ausente.** La ausencia de un PDF produce un error de PyMuPDF (librería de infraestructura), no un error de dominio con mensaje indexable. No hay verificación previa de existencia. |
| **E-6.2-004** | P1 | `tools/evaluation/run_regression.py` línea 215: `if __name__ == "__main__": main()` (sin `run_entry`); exit code observado: 1 ante crash | **Exit code ambiguo.** `run_regression.py` define `EXIT_WARNING = 1` (NADR-19 §5.5 R22) pero no usa `run_entry(main)`. Un crash produce exit code 1 (default de Python), indistinguible de WARNING científico. |
| **E-6.2-005** | P2 | `tests/corpus/canonical/pdf/doc_06_johnstone.pdf` (563435 bytes) existe; `manifest.json` NO contiene doc_06; `ground_truth/` NO contiene doc_06 | **PDF huérfano.** `doc_06_johnstone.pdf` existe físicamente pero no está en el manifest ni tiene GT. Es un artefacto de quarantine (H-5.2-1: excluido por requerir OCR). No participa en la baseline pero ocupa espacio en el directorio. |
| **E-6.2-006** | P2 | `core/benchmark/topology/regression/adapter.py` → `verify_document_identity()`, `verify_sealed_state()`, `verify_oracle_integrity()`, `verify_completeness()` | **Verificaciones de GT completas.** El RegressionAdapter verifica identidad documental, estado sellado, integridad criptográfica (oracle_hash) y completitud biyectiva antes de evaluar. Orden Fail-Fast: identity → completeness → sealed → integrity. |
| **E-6.2-007** | P2 | `core/benchmark/corpus/services.py` → `ManifestFingerprintCalculator.compute_hash()`: framing con 7 campos por documento, ordenados por document_id | **Identidad del manifest determinista y sensible.** El hash incluye corpus_version, document_id, sha256, traits, page_count, oracle_hash, ground_truth_state. Cualquier mutación en estos campos produce hash diferente. |
| **E-6.2-008** | P2 | `core/benchmark/ground_truth/identity.py` → `OracleSemanticIdentityCalculator.calculate()`: framing con node_id, node_type, strategy, payload_hash | **Identidad del oracle determinista y sensible.** El hash captura contenido semántico (qué dice el oráculo) y NO metadata física (dónde está en el PDF). Insensible a sequence_id, depth, parent_node_id, metadata, control_plane. |
| **E-6.2-009** | P2 | `core/benchmark/ground_truth/models.py` → `class SealedOracle(BaseModel)`: `frozen=True`; tipo disjunto de `GroundTruthDraft`; sin conversión implícita | **Inmutabilidad de SealedOracle por contrato de modelo.** `frozen=True` impide mutación de instancia. Tipo disjunto impide conversión implícita desde Draft. Gobernado por autoridad de sellado. |
| **E-6.2-010** | P2 | `tests/corpus/canonical/manifest.json` → 21 documentos, todos con `ground_truth_state: "sealed"`, todos con `oracle_hash` no-nulo | **Baseline v3.9 completamente sellada.** Los 21 documentos tienen estado "sealed" y oracle_hash calculado. El manifest_hash es `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`. |
| **E-6.2-011** | P2 | Ejecución forense: `run_regression.py --corpus-dir /tmp/nonexistent_corpus` → `FileNotFoundError: Manifest not found: \tmp\nonexistent_corpus\manifest.json` → exit code 1 | **Manifest ausente produce FileNotFoundError del adaptador.** El mensaje es descriptivo pero no indexable. No hay código `[CORPUS-001]` o similar. Exit code 1 ambiguo. |
| **E-6.2-012** | P2 | Ejecución forense: `run_regression.py` con pdf_dir parcial (solo doc_01) → `pymupdf.FileNotFoundError` en doc_02 → exit code 1 | **Completitud NO verifica PDFs.** `verify_completeness()` compara manifest_doc_ids vs artifact_doc_ids (GTs), NO vs PDFs. La ausencia de PDFs solo se detecta en la extracción, no en la verificación de completitud. |
| **E-6.2-013** | P2 | `core/benchmark/topology/regression/errors.py` → jerarquía: RegressionError → OracleIntegrityError, OracleNotSealedError, OracleDocumentMismatchError, MissingOracleHashError, InvalidNSSScoreError. `core/benchmark/ground_truth/errors.py` → GroundTruthError → EmptyGroundTruthDraftError, OracleValidityError, IncompleteBaselineError → OrphanOracleError, BaselineContractError, SealedOracleOverwriteError | **Jerarquía de errores no cubre PDF ausente.** Ningún error de dominio representa "PDF físico faltante" o "artefacto de entrada ausente". Los errores cubren integridad del oráculo (GT), no del PDF. |
| **E-6.2-014** | P2 | `tests/corpus/canonical/ground_truth/doc_01_single.json` → estructura: array de nodos con node_id, sequence_id, node_type, strategy, metadata (bboxes, pages, provider_native_id, confidence, layout_reading_order, semantic_origin), depth, payload, control_plane, parent_node_id, segment_count | **Estructura de GT confirmada.** Cada GT es un array JSON de nodos AST V2. La estructura incluye metadata física (bboxes, pages) que NO afecta el oracle_hash (insensible por diseño). |

### Evidencia E-6.2-001: 14 de 21 PDFs no trackeados en git

* **Archivo Fuente Primario:** `.gitignore`, `git ls-files tests/corpus/canonical/`
* **Símbolo Auditado:** Regla de exclusión y tracking real
* **Declaración Observada:**

```text
.gitignore línea: tests/corpus/canonical/pdf/

git ls-files tests/corpus/canonical/pdf/:
  doc_01_single.pdf
  doc_02_double.pdf
  doc_03_math.pdf
  doc_04_table.pdf
  doc_05_graph.pdf
  doc_06_johnstone.pdf
  doc_07_pesaran.pdf

NO trackeados (14):
  doc_08_bilingual_cs.pdf, doc_09_vanhaverbeke.pdf, doc_10_gross.pdf,
  doc_11_fig.pdf, doc_12_multi_col.pdf, doc_13_fmi_graf_tablas.pdf,
  doc_14_fig_math.pdf, doc_15_table_fig_code.pdf, doc_16_fig_code.pdf,
  doc_17_table_code.pdf, doc_18_table_math_doble_col.pdf,
  doc_19_fig_table_doble_col.pdf, doc_20_doble_col_table.pdf,
  doc_21_heavy_math_table.pdf, doc_22_table_fig_math.pdf
```

* **Observed:** La regla `.gitignore` excluye `tests/corpus/canonical/pdf/` completo. Solo 7 PDFs (agregados antes de la regla) están trackeados. 14 PDFs no están disponibles en un clone fresco.
* **Required:** ADR Master §5: "Determinismo y Reproducibilidad: Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser 100% determinista." ADR_05 §5: "La Fase 6 integra estos artefactos en el pipeline de CI/CD." ROADMAP: "Regression Gates: Aserción estricta en CI."
* **Decision:** Fase 5 decidió no trackear PDFs por copyright (O-5.0-1, Findings Register v0.21.0). Esta decisión fue operacional, no normativa.
* **Hallazgo Forense:** La decisión de copyright (O-5.0-1) tiene una consecuencia no anticipada: impide la reproducibilidad de la regresión en CI. La baseline es consumible localmente pero no en un entorno de ejecución externo.
* **Consecuencia Arquitectónica:** Sin un mecanismo de materialización, el Regression Gate no puede ejecutarse en CI contra el corpus completo. Esto bloquea el DoD Level B del ADR Master ("Compuertas de CI Activas").
* **Estado:** OPEN

### Evidencia E-6.2-003: Crash no tipado ante PDF ausente

* **Archivo Fuente Primario:** Ejecución forense de `run_regression.py`
* **Símbolo Auditado:** `main()` → `extraction_pipeline.parse(str(pdf_path))` → `PyMuPDFProvider.extract()` → `fitz.open()`
* **Declaración Observada:**

```text
$ python tools/evaluation/run_regression.py --corpus-dir tests/corpus/canonical --pdf-dir /tmp/nonexistent_pdfs --output-dir /tmp/test_output

Traceback (most recent call last):
  File "tools/evaluation/run_regression.py", line 171, in main
    runtime_ast = extraction_pipeline.parse(str(pdf_path))
  File "infra/adapters/pdf_parser.py", line 26, in parse
    document_layout = self._provider.extract(file_path)
  File "infra/extraction/providers/pymupdf_provider.py", line 69, in extract
    with fitz.open(pdf_path) as doc:
  File "venv/Lib/site-packages/pymupdf/__init__.py", line 2992, in __init__
    raise FileNotFoundError(f"no such file: '{filename}'")
pymupdf.FileNotFoundError: no such file: '\tmp\nonexistent_pdfs\doc_01_single.pdf'
Exit code: 1
```

* **Observed:** La ausencia de un PDF produce `pymupdf.FileNotFoundError` (error de librería de infraestructura). El traceback es crudo, sin mensaje indexable. El exit code es 1 (default de Python para excepciones no capturadas).
* **Required:** ENGINEERING_PRINCIPLES §IV: "Cero Fallos Silenciosos: Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un Warning indexable explícito (ej. [AST-001]) o fallar duro (Raise Exception)." NADR-24 §5.4 R15-R19: semántica de fallo uniforme con exit codes diferenciados.
* **Decision:** `run_regression.py` no fue incluido en la remediación DF-18 (Wave 4.2). GF-01 estableció separación de scope: `run_regression` conserva taxonomía NADR-19 (0/1/2 = PASS/WARNING/HARD_FAIL).
* **Hallazgo Forense:** El error de PDF ausente no es un error de dominio. Es un crash de infraestructura que propaga como traceback crudo. No hay verificación previa de existencia de PDFs. No hay error tipado con mensaje indexable. El exit code 1 es ambiguo (indistinguible de WARNING científico).
* **Consecuencia Arquitectónica:** Un consumidor CI no puede distinguir entre "el pipeline tiene una regresión científica (WARNING)" y "el PDF no existe (EXECUTION_FAILURE)". Esto viola el principio de Cero Fallos Silenciosos en el sentido de que el fallo no es indexable ni tipado.
* **Estado:** OPEN

### Evidencia E-6.2-012: Completitud NO verifica PDFs

* **Archivo Fuente Primario:** `core/benchmark/topology/regression/adapter.py` → `verify_completeness()`; `core/benchmark/ground_truth/completeness.py` → `BaselineCompletenessVerifier.verify()`
* **Símbolo Auditado:** `verify_completeness(manifest_doc_ids, artifact_doc_ids)`
* **Declaración Observada:**

```python
def verify_completeness(
    self,
    manifest_doc_ids: FrozenSet[str],
    artifact_doc_ids: FrozenSet[str],
) -> None:
    errors = BaselineCompletenessVerifier.verify(
        manifest_doc_ids=manifest_doc_ids,
        artifact_doc_ids=artifact_doc_ids,
    )
    if errors:
        raise IncompleteBaselineError("; ".join(errors))
```

* **Observed:** `verify_completeness()` compara `manifest_doc_ids` (del manifest.json) contra `artifact_doc_ids` (de `ground_truth/*.json`). NO compara contra PDFs. La completitud es sobre GTs, no sobre PDFs.
* **Required:** ADR Master §5: "Invariante de Sellado Estricto (Zero Partial Sealing): Un corpus NO podrá entrar en estado SEALED si no existe una correspondencia biyectiva completa entre los PDFs declarados y sus oráculos AST auditados ($N_{PDF} = N_{GT}$)."
* **Decision:** La completitud fue diseñada para verificar la biyección manifest ↔ GTs, no manifest ↔ PDFs. Esto es correcto para el sellado (Fase 5 verifica ambas biyecciones), pero el entry point de regresión solo verifica una.
* **Hallazgo Forense:** La verificación de completitud en `run_regression.py` es parcial: verifica manifest ↔ GTs pero no manifiesto ↔ PDFs. La ausencia de PDFs solo se detecta cuando se intenta la extracción (paso 4c), no en la verificación de completitud (paso 2). Esto es consistente con el diseño (la regresión evalúa GTs, no PDFs), pero significa que un corpus con PDFs ausentes pasa la verificación de completitud y falla en la extracción.
* **Consecuencia Arquitectónica:** El Zero Partial Sealing ($N_{PDF} = N_{GT}$) se verifica en el sellado (Fase 5) pero no se re-verifica en el consumo (run_regression.py). Si un PDF se elimina después del sellado, la regresión no lo detecta hasta intentar la extracción.
* **Estado:** OPEN

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-6.2-01 | `LocalFileSystemCorpusLoader` acepta `base_path` como archivo o directorio. Si es archivo o termina en `.json`, usa directamente. Si no, usa `base_path / "manifest.json"`. Esto permite flexibilidad pero no está documentado en el CLI de `run_regression.py`. | Bajo | OPEN |
| OBS-6.2-02 | `LocalFileSystemGroundTruthReader.load_ground_truth()` retorna `tuple(read_ast_json(target_path))`. La conversión a tuple garantiza inmutabilidad de la colección (ENGINEERING_PRINCIPLES §II). | Bajo | OPEN |
| OBS-6.2-03 | `LocalFileSystemGroundTruthArtifactAdapter.list_artifact_ids()` retorna stems ordenados (`sorted`). Esto garantiza determinismo en el listado de artefactos. | Bajo | OPEN |
| OBS-6.2-04 | `LocalFileSystemCorpusLoader.save_manifest_dto()` usa escritura atómica (tempfile + fsync + os.replace). Esto es consistente con NADR-F17BIS-01 §5.6 y DF-15. La lectura (`load_raw_manifest()`) no es atómica pero es read-only. | Bajo | OPEN |
| OBS-6.2-05 | El `manifest_hash` está contenido en el propio `manifest.json`. No hay verificación de que el `manifest_hash` sea correcto al cargar el manifest. `run_regression.py` no recalcula el manifest_hash ni lo compara. | Medio | OPEN |
| OBS-6.2-06 | El `sha256` del PDF está en el manifest pero `run_regression.py` no lo verifica contra el archivo físico. Un PDF sustituido (mismo nombre, diferente contenido) no sería detectado. | Medio | OPEN |
| OBS-6.2-07 | `doc_06_johnstone.pdf` (563435 bytes) existe en `pdf/` pero no en el manifest ni en `ground_truth/`. Es un artefacto de quarantine (H-5.2-1). Si se ejecutara `run_regression.py` con un `--pdf-dir` que incluya doc_06, no habría problema porque el loop itera sobre el manifest (21 docs), no sobre los archivos del directorio. | Bajo | OPEN |
| OBS-6.2-08 | La estructura de un GT incluye `metadata.bboxes`, `metadata.pages`, `metadata.provider_native_id`, `metadata.confidence`, `metadata.layout_reading_order`, `metadata.semantic_origin`. Estos campos NO afectan el `oracle_hash` (insensible por diseño de `OracleSemanticIdentityCalculator`). Esto significa que un GT puede tener metadata diferente pero mismo oracle_hash. | Bajo | OPEN |
| OBS-6.2-09 | El `--inject-timestamp` flag de `run_regression.py` "rompe determinismo estricto" según el docstring. En CI, este flag debería ser False (default) para garantizar determinismo. | Bajo | OPEN |
| OBS-6.2-10 | La variable `CORPUS_READONLY: "true"` en el CI workflow no tiene consumidor demostrado en el código (OBS-6.0-01 de HITO 6.0). Es decorativa. | Bajo | OPEN |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-6.2-01** | 14 de 21 PDFs del corpus canónico no están trackeados en git. Un clone fresco no puede ejecutar `run_regression.py` contra el corpus completo. Esto bloquea la reproducibilidad de la regresión en CI. | E-6.2-001, HITO 6.0 E-6.0-005 | Pilar: Materialización / ADR Master §5 (Determinismo y Reproducibilidad) | **Fase 6** | BLOCKING |
| **GAP-6.2-02** | No existe mecanismo de materialización de PDFs en CI. Ningún step del workflow descarga, cachea o provisiona los PDFs. No hay script de provisioning, object storage, ni self-hosted runner. | E-6.2-002, HITO 6.0 E-6.0-004 | Pilar: Materialización / ADR_05 §5 (Fase 6 integra en CI/CD) | **Fase 6** | BLOCKING |
| **GAP-6.2-03** | La ausencia de un PDF produce `pymupdf.FileNotFoundError` (crash de librería), no un error de dominio con mensaje indexable. No hay verificación previa de existencia de PDFs antes de la extracción. | E-6.2-003, E-6.2-012 | Pilar: Error Handling / ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos) | **Fase 6** | OPEN |
| **GAP-6.2-04** | `run_regression.py` no usa `run_entry(main)`. Los crashes producen exit code 1 (default de Python), indistinguible de `EXIT_WARNING = 1` (NADR-19 §5.5 R22). Un consumidor CI no puede distinguir WARNING científico de EXECUTION_FAILURE. | E-6.2-004, E-6.2-003, E-6.2-011 | Pilar: Error Handling / NADR-24 §5.4 R15-R19 (semántica de fallo uniforme) | **Fase 6 (DC)** | OPEN |
| **GAP-6.2-05** | La jerarquía de errores del dominio no tiene un error para "PDF físico faltante" o "artefacto de entrada ausente". Los errores de regresión cubren integridad del oráculo (GT), no del PDF. | E-6.2-013 | Pilar: Error Handling / DC-6.4 (taxonomía de estados) | **Fase 6 (DC)** | OPEN |
| **GAP-6.2-06** | `run_regression.py` no verifica el `manifest_hash` contra el manifest recalculado. Un manifest mutado en disco no sería detectado por el entry point de regresión. | OBS-6.2-05 | Pilar: Integridad / ADR Master §3 (Integridad ≠ Identidad) | **Fase 6** | OPEN |
| **GAP-6.2-07** | `run_regression.py` no verifica el `sha256` del PDF contra el valor en el manifest. Un PDF sustituido (mismo nombre, diferente contenido) no sería detectado. | OBS-6.2-06 | Pilar: Integridad / ADR Master §3 (Integridad) | **Fase 6** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-6.2-A | El verification subject necesita exactamente: manifest.json + ground_truth/*.json + pdf/*.pdf. | CONFIRMADA | E-6.2-006, E-6.2-010. `run_regression.py` lee manifest (paso 1), GTs (paso 4a), PDFs (paso 4c). No lee otros artefactos (curation_checklist, lineage). | El conjunto mínimo de artefactos para CV es: 1 manifest + 21 GTs + 21 PDFs. |
| H-6.2-B | La baseline es consumible localmente con garantías de integridad. | CONFIRMADA | E-6.2-006, E-6.2-007, E-6.2-008, E-6.2-009, E-6.2-010. Las verificaciones de identidad, estado sellado e integridad criptográfica pasan para los 21 GTs. | Localmente, la baseline es consumible y verificable. |
| H-6.2-C | La baseline es consumible en CI. | RECHAZADA | E-6.2-001, E-6.2-002. 14 PDFs no trackeados, no hay materialización. | La baseline NO es consumible en CI sin un mecanismo de materialización. |
| H-6.2-D | La ausencia de un PDF produce un error de dominio tipado. | RECHAZADA | E-6.2-003. Produce `pymupdf.FileNotFoundError` (crash de librería), no error de dominio. | El error handling de PDFs ausentes es un gap. |
| H-6.2-E | La completitud verifica tanto GTs como PDFs. | RECHAZADA | E-6.2-012. `verify_completeness()` solo verifica manifest ↔ GTs, no manifest ↔ PDFs. | La completitud es parcial. La ausencia de PDFs se detecta en la extracción, no en la verificación. |
| H-6.2-F | El `manifest_hash` se verifica al cargar el manifest. | RECHAZADA | OBS-6.2-05. `run_regression.py` no recalcula ni compara el manifest_hash. | Un manifest mutado no sería detectado por el entry point. |
| H-6.2-G | El `sha256` del PDF se verifica contra el manifest. | RECHAZADA | OBS-6.2-06. `run_regression.py` no verifica el sha256 del PDF. | Un PDF sustituido no sería detectado. |
| H-6.2-H | `doc_06_johnstone.pdf` interfiere con la ejecución de `run_regression.py`. | RECHAZADA | OBS-6.2-07. El loop itera sobre el manifest (21 docs), no sobre los archivos del directorio. doc_06 no está en el manifest, por lo que no se procesa. | El PDF huérfano no interfiere con la ejecución, pero ocupa espacio y puede causar confusión. |
| H-6.2-I | Existe un mecanismo externo (fuera del repo) para materializar los PDFs. | NO VERIFICABLE | La búsqueda en el repo no encontró evidencia. No se puede verificar infraestructura externa desde el repositorio. | Destino: DC-6.2. Requiere decisión arquitectónica. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué artefactos físicos necesita realmente el verification subject identificado en HITO 6.1?

**Estado actual verificado:**

1. `run_regression.py` requiere `--corpus-dir` y `--pdf-dir` (E-6.1-007 de HITO 6.1).
2. De `--corpus-dir` lee: `manifest.json` (paso 1), `ground_truth/*.json` (paso 4a).
3. De `--pdf-dir` lee: `{doc_id}.pdf` para cada documento del manifest (paso 4c).
4. No lee: `curation_checklist.json`, `canonicalization_lineage.json`, `{doc_id}_canonicalization_lineage.json`.

**Respuesta forense:**

El verification subject necesita exactamente:

```text
--corpus-dir:
    manifest.json                          (1 archivo, 8363 bytes)
    ground_truth/{doc_id}.json             (21 archivos, ~1.2 MB total)

--pdf-dir:
    {doc_id}.pdf                           (21 archivos, ~22 MB total)
```

Total: 1 manifest + 21 GTs + 21 PDFs = 43 artefactos.

**Implicación:** Los artefactos de trazabilidad (lineage, curation_checklist) NO son necesarios para la ejecución de la regresión. Son artefactos de gobernanza, no de consumo.

### 16.2 ¿Dónde están actualmente esos artefactos?

**Estado actual verificado:**

1. `manifest.json`: `tests/corpus/canonical/manifest.json` — trackeado en git.
2. `ground_truth/*.json`: `tests/corpus/canonical/ground_truth/` — 21 archivos trackeados en git.
3. `pdf/doc_01-07.pdf`: `tests/corpus/canonical/pdf/` — 7 archivos trackeados en git.
4. `pdf/doc_08-22.pdf`: `tests/corpus/canonical/pdf/` — 14 archivos NO trackeados (.gitignore).
5. `pdf/doc_06_johnstone.pdf`: `tests/corpus/canonical/pdf/` — NO trackeado, NO en manifest (huérfano).

**Respuesta forense:**

| Artefacto | Ubicación local | Tracking git | Disponible en clone fresco |
|---|---|---|---|
| manifest.json | `tests/corpus/canonical/manifest.json` | ✅ | ✅ |
| ground_truth/*.json (×21) | `tests/corpus/canonical/ground_truth/` | ✅ | ✅ |
| pdf/doc_01-07.pdf (×7) | `tests/corpus/canonical/pdf/` | ✅ | ✅ |
| pdf/doc_08-22.pdf (×14) | `tests/corpus/canonical/pdf/` | ❌ (.gitignore) | ❌ |

**Implicación:** Un clone fresco tiene 22 de 43 artefactos necesarios (manifest + 21 GTs). Faltan 14 PDFs. La regresión solo puede ejecutarse contra 7 de 21 documentos en un clone fresco.

### 16.3 ¿Cuál es su identidad canónica?

**Estado actual verificado:**

1. `manifest_hash`: `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d` (v3.9).
2. `oracle_hash` por documento: SHA-256 determinista calculado por `OracleSemanticIdentityCalculator`.
3. `sha256` por PDF: SHA-256 del contenido binario.
4. `corpus_version`: `v3.9`.

**Respuesta forense:**

La identidad canónica de la baseline está completamente definida:

```text
Baseline Identity:
    corpus_version: v3.9
    manifest_hash: 727782fe0df26d9d...
    documents: 21 × (document_id, sha256, traits, page_count, oracle_hash, ground_truth_state)
```

Cada documento tiene una cadena de identidad:
```text
document_id → sha256 (PDF) → oracle_hash (GT) → ground_truth_state ("sealed")
```

El `manifest_hash` es un hash compuesto que incluye todos los campos de todos los documentos, ordenados por `document_id`. Cualquier mutación en cualquier campo produce un `manifest_hash` diferente.

**Implicación:** La identidad canónica está completamente definida y es verificable. El gap no es de identidad sino de materialización.

### 16.4 ¿Qué mecanismos de integridad existen?

**Estado actual verificado:**

1. `RegressionAdapter.verify_document_identity()`: compara `oracle.document_id` vs `metadata.document_id`.
2. `RegressionAdapter.verify_sealed_state()`: verifica `metadata.ground_truth_state == "sealed"`.
3. `RegressionAdapter.verify_oracle_integrity()`: recalcula `oracle_hash` y compara con `metadata.oracle_hash`.
4. `RegressionAdapter.verify_completeness()`: verifica biyección manifest_doc_ids ↔ artifact_doc_ids.

**Respuesta forense:**

Existen 4 mecanismos de integridad para GTs:

| Verificación | Qué detecta | Excepción |
|---|---|---|
| `verify_document_identity` | Cruce de documentos (GT de doc_A usado para doc_B) | `OracleDocumentMismatchError` |
| `verify_sealed_state` | GT no sellado | `OracleNotSealedError` |
| `verify_oracle_integrity` | GT mutado en disco | `OracleIntegrityError` |
| `verify_completeness` | GT faltante o huérfano | `IncompleteBaselineError` |

NO existen mecanismos de integridad para:

| Verificación ausente | Qué detectaría | Estado |
|---|---|---|
| Verificación de `manifest_hash` | Manifest mutado en disco | AUSENTE (OBS-6.2-05) |
| Verificación de `sha256` del PDF | PDF sustituido | AUSENTE (OBS-6.2-06) |
| Verificación de existencia de PDF | PDF ausente | AUSENTE (E-6.2-003) |
| Verificación de completitud de PDFs | PDFs faltantes | AUSENTE (E-6.2-012) |

**Implicación:** La integridad del GT está completamente protegida. La integridad del PDF y del manifest NO está verificada por el entry point de regresión. Esto es un gap de integridad parcial.

### 16.5 ¿Qué significa `SEALED` para cada artefacto consumido?

**Estado actual verificado:**

1. `SealedOracle` (modelo): `frozen=True`, tipo disjunto de `GroundTruthDraft`, sin conversión implícita.
2. `ground_truth_state: "sealed"` (manifest): estado lógico que indica que el GT fue sellado.
3. `oracle_hash` (manifest): hash criptográfico del contenido semántico del GT.
4. `SealedOracleOverwriteError`: protección contra sobrescritura de GT sellado.

**Respuesta forense:**

`SEALED` significa:

```text
Para el modelo (SealedOracle):
    - frozen=True: no se puede mutar la instancia
    - Tipo disjunto: no se puede convertir desde GroundTruthDraft
    - Gobernado por autoridad de sellado (SealGroundTruthUseCase)

Para el artefacto en disco (ground_truth/{doc_id}.json):
    - ground_truth_state = "sealed" en el manifest
    - oracle_hash calculado y almacenado en el manifest
    - Protegido contra sobrescritura por SealedOracleOverwriteError
    - Verificado por RegressionAdapter antes de cada evaluación

Para el consumidor (run_regression.py):
    - Verifica estado sellado antes de evaluar
    - Verifica integridad criptográfica antes de evaluar
    - No puede mutar el GT (read-only por diseño)
```

**Lo que SEALED NO garantiza:**
- No garantiza que el PDF correspondiente exista.
- No garantiza que el PDF no haya sido sustituido.
- No garantiza que el manifest no haya sido mutado.

**Implicación:** `SEALED` protege el GT pero no el PDF ni el manifest. La protección del GT es completa; la del PDF y manifest es parcial.

### 16.6 ¿Existe actualmente un mecanismo reproducible de materialización?

**Estado actual verificado:**

1. Búsqueda en `.github/workflows/ci.yml`: 0 mecanismos de materialización.
2. Búsqueda en `pyproject.toml`: 0 referencias a corpus/artifact/download.
3. Búsqueda en scripts de tooling: 0 scripts de provisioning.
4. HITO 6.0 E-6.0-004: confirmado que no existe materialización.

**Respuesta forense:**

NO. No existe ningún mecanismo reproducible de materialización de PDFs en CI. La búsqueda exhaustiva en el repositorio y el workflow CI no encontró:
- Artifact download (GitHub Actions, GitLab CI)
- Object storage (S3, GCS, Azure)
- Cache específico de corpus
- wget/curl/rclone
- Self-hosted runner
- Script de provisioning

**Implicación:** La materialización es un gap bloqueante (GAP-6.2-01, GAP-6.2-02). Sin un mecanismo de materialización, la regresión no puede ejecutarse en CI contra el corpus completo.

### 16.7 ¿Ese mecanismo preserva identidad e integridad?

**Respuesta forense:**

No aplica. No existe mecanismo de materialización (16.6). La pregunta queda abierta para cuando se diseñe un mecanismo (DC-6.2).

### 16.8 ¿Existe provenance suficiente para reconstruir el origen del baseline consumido?

**Estado actual verificado:**

1. `manifest.json` contiene: corpus_version, manifest_hash, documentos con sha256, traits, page_count, oracle_hash, ground_truth_state.
2. `canonicalization_lineage.json` + 16 archivos de lineage por documento: trazabilidad de canonicalización de node_ids.
3. `curation_checklist.json`: registro de curaduría (no trackeado en git).
4. FASE_5_HANDOFF.md v1.0.1: estado de cierre de Fase 5.
5. FASE_5_DEFERRED_FINDINGS_REGISTER.md v0.21.0: decisiones de ownership (O-5.0-1), quarantine (H-5.2-1).

**Respuesta forense:**

La provenance de la baseline es suficiente para reconstruir:
- **Qué** se selló: 21 documentos con identidad criptográfica completa.
- **Cuándo**: Fase 5, corpus v3.9, manifest_hash `727782fe...`.
- **Cómo**: SealGroundTruthUseCase con verificaciones de completitud y validez.
- **Quién**: documentado en FASE_5_HANDOFF.md.

La provenance NO es suficiente para reconstruir:
- **De dónde** se obtuvieron los PDFs originales (fuentes de adquisición no documentadas en el manifest).
- **Por qué** doc_06 fue excluido (documentado en H-5.2-1 pero no en el manifest).

**Implicación:** La provenance es suficiente para verificar la identidad e integridad de la baseline. No es suficiente para reconstruir la cadena de adquisición de los PDFs originales, pero esto no es necesario para Continuous Verification.

### 16.9 ¿Qué diferencia existe entre canonical corpus y fixtures/legacy corpus?

**Estado actual verificado:**

1. `tests/corpus/canonical/`: corpus canónico sellado (21 docs, manifest v3.9).
2. `tests/fixtures/`: fixtures de tests (sample_3_pages.pdf, caches, unit_cost_context.py).
3. HITO 6.0 E-6.0-006: CI verifica inmutabilidad de `tests/fixtures/`, no de `tests/corpus/canonical/`.
4. HITO 6.0 E-6.0-012: `tests/fixtures/` contiene basura de tests (~40 archivos *_cache_*.db).

**Respuesta forense:**

| Recurso | Rol | Identidad | ¿Canonical? |
|---|---|---|---|
| `tests/corpus/canonical/manifest.json` | Baseline canónica sellada | manifest_hash: 727782fe... | ✅ Sí |
| `tests/corpus/canonical/ground_truth/*.json` | Oráculos sellados | oracle_hash por documento | ✅ Sí |
| `tests/corpus/canonical/pdf/*.pdf` | PDFs de referencia | sha256 en manifest | ✅ Sí (21 de 22) |
| `tests/fixtures/sample_3_pages.pdf` | Fixture de test genérico | No tiene identidad canónica | ❌ No |
| `tests/fixtures/*_cache_*.db` | Basura de tests | No tiene identidad | ❌ No |
| `tests/fixtures/unit_cost_context.py` | Fixture de test | No tiene identidad canónica | ❌ No |

**Implicación:** `tests/fixtures/` y `tests/corpus/canonical/` NO son intercambiables. El CI actualmente verifica la inmutabilidad de `tests/fixtures/` (ruta incorrecta), no de `tests/corpus/canonical/` (ruta correcta). Esto es un gap de protección (HITO 6.0 GAP-6.0-03).

### 16.10 ¿Qué restricciones de distribución afectan a los artefactos?

**Estado actual verificado (evidencia heredada):**

1. FASE_5_DEFERRED_FINDINGS_REGISTER.md v0.21.0, O-5.0-1: "FASE_4_HANDOFF queda como artefacto histórico externo por decisión de ownership."
2. FASE_5_HANDOFF.md v1.0.1: "Los PDFs del corpus NO se trackean en git por copyright."
3. `.gitignore`: `tests/corpus/canonical/pdf/` excluido.

**Respuesta forense:**

La restricción documentada es:
- **Qué**: Los PDFs del corpus canónico no se trackean en git.
- **Por qué**: Restricciones de distribución/copyright (decisión de ownership O-5.0-1).
- **A qué aplica**: Solo a los PDFs. Los GTs (JSON) y el manifest SÍ se trackean.
- **Impacto**: Un clone fresco no tiene 14 de 21 PDFs.

**Lo que NO está documentado:**
- Si la restricción impide solo git o cualquier distribución (CI artifacts, object storage, etc.).
- Si existe una política de almacenamiento/distribución alternativa.
- Si los PDFs pueden distribuirse en un entorno privado/organizacion.

**Implicación:** La restricción de copyright es un FACT heredado de Fase 5. HITO 6.2 no la re-descubre ni la resuelve. La consecuencia operativa (imposibilidad de materialización en CI) se registra como gap (GAP-6.2-01, GAP-6.2-02) y se alimenta como Decision Candidate (DC-6.2).

### 16.11 ¿Qué ocurre actualmente ante artefacto ausente, corrupto, sustituido o con identidad incompatible?

**Estado actual verificado (ejecuciones forenses):**

| Condición | Comportamiento observado | Exit code | Error tipado |
|---|---|---|---|
| Manifest ausente | `FileNotFoundError: Manifest not found: ...` | 1 | ❌ No (FileNotFoundError genérico) |
| PDF ausente | `pymupdf.FileNotFoundError: no such file: ...` | 1 | ❌ No (error de PyMuPDF) |
| PDFs parciales | `pymupdf.FileNotFoundError` en primer PDF faltante | 1 | ❌ No |
| GT ausente | `FileNotFoundError: Oracle consistency error: Ground Truth for '{doc_id}' not found.` | 1 | ❌ No (FileNotFoundError genérico) |
| GT corrupto (JSON inválido) | No verificado directamente. `read_ast_json()` probablemente lanza `json.JSONDecodeError`. | 1 (inferido) | ❌ No |
| GT mutado (oracle_hash no coincide) | `OracleIntegrityError` | 2 (inferido) | ✅ Sí |
| GT no sellado | `OracleNotSealedError` | 2 (inferido) | ✅ Sí |
| GT con document_id incorrecto | `OracleDocumentMismatchError` | 2 (inferido) | ✅ Sí |
| Manifest con oracle_hash None | `MissingOracleHashError` | 2 (inferido) | ✅ Sí |
| Manifest incompleto (GT huérfano) | `IncompleteBaselineError` | 2 (inferido) | ✅ Sí |
| PDF sustituido (mismo nombre, diferente contenido) | NO DETECTADO. El sha256 no se verifica. | N/A | ❌ No |
| Manifest mutado (manifest_hash incorrecto) | NO DETECTADO. El manifest_hash no se verifica. | N/A | ❌ No |

**Respuesta forense:**

El comportamiento ante condiciones de fallo es **parcial**:
- **Errores de GT**: tipados y detectados (OracleIntegrityError, OracleNotSealedError, etc.).
- **Errores de PDF**: NO tipados. Producen crashes de PyMuPDF con exit code 1 ambiguo.
- **Errores de manifest**: NO verificados. El manifest_hash y el sha256 del PDF no se verifican.

**Implicación:** La taxonomía de errores cubre la integridad del GT pero no la del PDF ni del manifest. Esto alimenta DC-6.4 (taxonomía de estados operacionales) y DC-6.5 (verificación de integridad completa).

### 16.12 ¿Qué cuestiones quedan necesariamente abiertas para 6.3/6.4?

**Respuesta forense:**

| Cuestión | HITO destino | DC |
|---|---|---|
| Cómo materializar PDFs en CI | 6.3 / DC-6.2 | DC-6.2 |
| Cómo conectar `run_regression.py` a CI (adapter, invocación directa, wrapper) | 6.3 / DC-6.3 | DC-6.3 |
| Semántica de conformance vs regression vs baseline de divergencia | 6.3 / DC-6.1 | DC-6.1 |
| Taxonomía de estados operacionales (BASELINE_INTEGRITY_FAILURE vs EXECUTION_FAILURE) | 6.3 / DC-6.4 | DC-6.4 |
| Perfil de ejecución por evento (PR, merge, release, nightly) | 6.3 / DC-6.5 | DC-6.5 |
| Si `run_regression.py` debe usar `run_entry(main)` | 6.3 | DC-6.9 (nuevo) |
| Si debe existir verificación previa de PDFs | 6.3 | DC-6.10 (nuevo) |
| Si debe verificarse manifest_hash y sha256 del PDF | 6.3 / 6.4 | DC-6.11 (nuevo) |
| Grafo de dependencias y readiness | 6.4 | N/A |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-6.2** | Materialización del corpus canónico en CI | E-6.2-001, E-6.2-002, GAP-6.2-01, GAP-6.2-02 | Ausente | **Fase 6** |
| **DC-6.4** | Taxonomía de estados operacionales (BASELINE_INTEGRITY_FAILURE vs EXECUTION_FAILURE) | E-6.2-003, E-6.2-004, E-6.2-013, GAP-6.2-04, GAP-6.2-05 | Ausente (solo PASS/WARNING/HARD_FAIL) | **Fase 6** |
| **DC-6.9** | ¿Debe `run_regression.py` usar `run_entry(main)` para traducir crashes a exit code 2? | E-6.2-004, GAP-6.2-04 | Ausente (usa `main()` directo) | **Fase 6** |
| **DC-6.10** | ¿Debe existir verificación previa de existencia de PDFs antes de la extracción? | E-6.2-003, E-6.2-012, GAP-6.2-03 | Ausente | **Fase 6** |
| **DC-6.11** | ¿Debe `run_regression.py` verificar `manifest_hash` y `sha256` del PDF? | OBS-6.2-05, OBS-6.2-06, GAP-6.2-06, GAP-6.2-07 | Ausente | **Fase 6** |

> **Nota de gobernanza:** DC-6.9, DC-6.10 y DC-6.11 son nuevos, generados por este HITO. No resuelven nada; identifican decisiones que el ADR/NADR de Fase 6 deberá tomar.

---

## 21. CIERRE DEL HITO 6.2

Este HITO confirma que **la baseline sellada de Fase 5 existe con contratos de integridad e identidad completos y verificables**, pero **NO es consumible en un entorno de ejecución externo (CI)** sin un mecanismo de materialización de PDFs.

La baseline es:
- **Localmente consumible**: manifest + 21 GTs + 21 PDFs están disponibles en el workspace del desarrollador. Las verificaciones de identidad, estado sellado e integridad criptográfica pasan.
- **NO consumible en CI**: 14 de 21 PDFs no están trackeados en git. No existe mecanismo de materialización. Un clone fresco solo tiene 7 de 21 PDFs.
- **Parcialmente protegida**: La integridad del GT está completamente protegida (4 verificaciones). La integridad del PDF y del manifest NO está verificada por el entry point de regresión.
- **Con error handling parcial**: Los errores de GT son tipados y detectados. Los errores de PDF son crashes no tipados con exit code ambiguo.

El gap NO es arquitectónico (los contratos existen y son correctos) sino operacional:
1. Materialización de PDFs en CI (GAP-6.2-01, GAP-6.2-02) — BLOCKING.
2. Error handling de PDFs ausentes (GAP-6.2-03) — OPEN.
3. Exit code ambiguo (GAP-6.2-04) — OPEN.
4. Verificación de integridad de PDF y manifest (GAP-6.2-06, GAP-6.2-07) — OPEN.
5. Taxonomía de errores incompleta (GAP-6.2-05) — OPEN.

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
- [x] Todas las hipótesis están cerradas como `CONFIRMADA`, `RESUELTA`, `RECHAZADA` o `NO VERIFICABLE` (con destino explícito).
- [x] Cero hipótesis abiertas sin destino.
- [x] Cero contradicciones no documentadas con HITOs previos.
- [x] Todos los IDs `E`, `GAP`, `OBS`, `H` son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.
**Verificación de cadena de gobernanza:** ADR Master §3, §5 → ADR_05 §3 D3, §5 → NADR-19 §5.5 R20 → HITO 6.0 → HITO 6.1 → HITO 6.2 → (futuro) HITO 6.3, 6.4 → ADR_06 / NADRs → Execution Plan.
**Contradicciones con HITOs previos:** Ninguna. HITO 6.0 identificó la Regression Gate Illusion a nivel de CI. HITO 6.1 confirmó que el sujeto de verificación existe. HITO 6.2 confirma que la baseline es consumible localmente pero no en CI. Esto es consistente y complementario.
**Decision Candidates generados:** DC-6.9 (run_entry), DC-6.10 (verificación previa de PDFs), DC-6.11 (verificación de manifest_hash y sha256). DC-6.2 y DC-6.4 alimentados con evidencia adicional.
**Siguiente paso recomendado:** Redactar HITO 6.3 (CI Regression Gate & Operational Semantics) para auditar la infraestructura CI, la semántica operacional, y resolver la frontera CI ↔ dominio. Posteriormente, HITO 6.4 (Dependency Graph & Readiness Assessment) para consolidar findings y Decision Candidates.