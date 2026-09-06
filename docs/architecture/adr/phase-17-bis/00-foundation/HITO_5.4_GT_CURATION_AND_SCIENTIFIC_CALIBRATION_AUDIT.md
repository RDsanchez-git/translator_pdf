# HITO_5.4_GT_CURATION_AND_SCIENTIFIC_CALIBRATION_AUDIT.md

**Estado:** FROZEN v1.0.3
**Fecha de emisión:** 2026-09-04
**Fecha de congelamiento:** 2026-09-04
**Fase:** 17-BIS — Fase 5 (Baseline Certification)
**Tipo de artefacto:** Ground Truth Curation & Scientific Calibration Infrastructure Audit
**Naturaleza:** Read-only forensic audit. No se propone código de producción. No se editan Ground Truths. No se calibran parámetros. No se implementa infraestructura nueva.

**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-12 (FROZEN), NADR-F17BIS-13 (FROZEN), NADR-F17BIS-14 (FROZEN), NADR-F17BIS-16 (FROZEN), NADR-F17BIS-17 (FROZEN), NADR-F17BIS-18 (FROZEN), NADR-F17BIS-19 (FROZEN), HITO_5.0 v1.0.2 (FROZEN), HITO_5.1 v1.1.2 (FROZEN), HITO_5.2 v1.1.0 (FROZEN), HITO_5.3 v1.1.3 (FROZEN), FASE_4_HANDOFF (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN), ENGINEERING_PRINCIPLES.md (FROZEN), PROJECT_TREE.txt, PROJECT_SCOPE.md, código fuente verificado directamente en `core/benchmark/ground_truth/`, `core/benchmark/topology/`, `tools/evaluation/`, `tests/corpus/`.

**Mandato:** Determinar, mediante evidencia forense reproducible, si los Ground Truths y la infraestructura de calibración del proyecto son científicamente confiables y suficientemente representativos para certificar la baseline canónica. Específicamente: (a) verificar que los Ground Truths pueden hidratarse bajo los contratos actuales y producen identidad criptográfica válida; (b) verificar que la cobertura observada del corpus coincide con la cobertura declarada; (c) auditar la infraestructura de calibración existente y determinar si permite calibración científica reproducible; (d) cerrar las hipótesis H-5.1-C, H-5.1-D y H-5.1-F heredadas de HITO 5.1.

**Síntesis:** Este HITO audita dos tracks ortogonales: TRACK A (Ground Truth Forensic Qualification) verifica la integridad, hidratación e identidad criptográfica de los Ground Truths existentes; TRACK B (Scientific Calibration Infrastructure Audit) audita la infraestructura existente de calibración y determina si permite calibración científica reproducible. **Clasificación final: NOT READY.** calibration_v1 es INELIGIBLE bajo el contrato actual por dos defectos contractuales/identitarios demostrados (manifest legacy DF-19, node_ids legacy que producen identidad criptográfica distinta). Un tercer aspecto (cobertura de traits) queda como indicio pendiente de curaduría humana. No existe infraestructura de partición de datasets, provenance de calibration runs, ni protocolo de calibración empírica ejecutable. La clasificación NOT READY es robusta frente a la incertidumbre epistemológica de traits: incluso si los traits fueran perfectos, los otros defectos bloquearían la certificación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-SKELETON | 2026-09-04 | Emisión inicial del esqueleto. |
| 1.0.1-SKELETON | 2026-09-04 | 6 correcciones estructurales. |
| 1.0.0-FROZEN | 2026-09-04 | Cierre inicial. TRACK A + TRACK B completados. |
| 1.0.1-FROZEN | 2026-09-04 | 5 correcciones menores (conteos, evidencias adicionales, riesgo .strip()). |
| 1.0.2-FROZEN | 2026-09-04 | Correcciones de rigor epistemológico: E-5.4-011 degradada, H-5.1-C cambiada a NO DEMOSTRADA, GAP-5.4-010 eliminado, R12 separada en A/B, columna Nature agregada. |
| 1.0.3-FROZEN | 2026-09-04 | **Correcciones forenses finales:** (1) Evidence Register reconciliado con inventario canónico explícito (18 evidencias: 6 P1, 4 P2, 8 VERIF); (2) H-5.1-F corregida de RECHAZADA a NO DEMOSTRADA (falta recomputación efectiva de hash); (3) Zero Partial Sealing reclasificado de FAIL a PASS/NOT YET EXERCISED (no hubo sellado parcial); (4) R12-B corregido de NON-COMPLIANT a PENDING EMPIRICAL VALIDATION; (5) Tabla de dimensiones de readiness introducida (Corpus Quality / GT Eligibility / Scientific GT Validity / Calibration Readiness / Empirical Calibration / Baseline Certification); (6) Checklist de superficies corregido; (7) Versión única v1.0.3; (8) GAP-5.4-002 reformulado como DISCREPANCIA DE IDENTIDAD / CONSECUENCIA CRIPTOGRÁFICA PENDIENTE DE VERIFICACIÓN. |

---

## NOTA DE HERENCIA

Este HITO recibe de:

**HITO 5.0:** Estado de contratos de dominio. Gaps operacionales (DF-18, rutas hardcoded).

**HITO 5.1:** Universo físico del corpus (7 identidades únicas candidatas). GAP-5.1-07: node_id serializado en representación no canónica. **Hipótesis pendientes:**
- H-5.1-C: Coverage Observada → **NO DEMOSTRADA** (indicio de subdeclaración, pendiente de curaduría humana)
- H-5.1-D: Compatibilidad de .ast.json legacy → **RECHAZADA** (E-5.4-008)
- H-5.1-F: Consecuencia de node_id no canónico sobre oracle_hash → **NO DEMOSTRADA** (falta recomputación efectiva)

**HITO 5.2:** Estado operacional del tooling (DF-18). Atomicidad física de persistencia verificada. **Restricción:** sanitize_ground_truth_types.py puede violar SealedOracle sin verificación de estado sellado (GAP-5.2-05). **Este HITO NO debe editar Ground Truths.**

**HITO 5.3:** Clasificación C — Comparable but Non-Equivalent. ZhangShasha y APTED no calculan la misma función de distancia bajo la configuración actual. **Implicación crítica para este HITO:** Los thresholds de NSS NO son transferibles entre motores. Si se usa ZhangShasha (canónico), los thresholds deben calibrarse para Σ TED(windows). Si se usa APTED, los thresholds deben calibrarse para TED(full tree). **Adicionalmente, HITO 5.3 detectó divergencia de normalización de texto: CriticalityAwareCostContext usa text_content SIN .strip(), mientras ASTFingerprintPolicy.semantic_fingerprint() usa text_content CON .strip() (E-5.3-002). Esto puede causar divergencias en benchmarks.**

**FASE_4_HANDOFF:** run_regression.py con exit codes 0/1/2. DF-04 como carry-forward. create_topology_evaluator() como composition root.

### Implicación de la clasificación C de HITO 5.3

HITO 5.3 concluyó que ZhangShasha y APTED son **Comparable but Non-Equivalent** (clasificación C). Las divergencias fundamentales son:

1. Modelo de costo diferente (UnitCostContext sub=1.0 vs CostMatrix rename=0.5/2.0).
2. Normalización de texto diferente (UnitCostContext sin `.strip()` vs `semantic_fingerprint` con `.strip()`).
3. Raíz virtual diferente (condicional vs siempre) con impacto en denominador de normalización.
4. Metodología diferente (Σ TED(windows) vs TED(full tree)).

**Implicación crítica para este HITO:**

- Los thresholds de NSS **NO son transferibles** entre motores.
- Si se usa ZhangShasha (canónico), los thresholds deben calibrarse para **Σ TED(windows)**.
- Si se usa APTED, los thresholds deben calibrarse para **TED(full tree)**.
- La calibración debe especificar explícitamente qué motor se está calibrando.
- La divergencia de `.strip()` puede causar resultados inconsistentes entre motores.

### Parámetros heredados y su clasificación

| Parámetro | Valor actual | Clasificación | Fuente |
|---|---|---|---|
| Pesos de criticidad | CRITICAL=5.0, WARNING=2.0, INFO=1.0 | Normativo/Heurístico | NADR-18 §5.3 R12: "Propuesta inicial sujeta a validación empírica" |
| Thresholds de NSS | 0.80/0.95 (FASE_4_HANDOFF) | Heurístico | No calibrados empíricamente |
| Normalización | MaxBoundNormalizationPolicy | Normativo | NADR-19 |
| Método de evaluación | DoubleProtectionMechanism | Normativo | NADR-19 |

**Observación:** Ninguno de estos parámetros ha sido calibrado empíricamente. Todos son normativos o heurísticos. Este HITO documenta esto explícitamente.

---

## NOTA DE DESVIACIÓN ESTRUCTURAL

Las secciones 5-9 de METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 no aplican a este tipo de HITO. Se reemplazan por secciones específicas de GT curation y calibración:

| Sección canónica | Sección reemplazo | Justificación |
|---|---|---|
| 5. Mapa de Flujos | 5. TRACK A — GT Forensic Qualification | Audita contenido de GTs, no flujos transaccionales |
| 6. Inventario Dimensiones | 5.1-5.7 | Inventario de GTs, traits, hidratación, identidad |
| 7. Matriz ORD | 7. Matriz Observed/Required/Decision | Aplica a GTs y calibración |
| 8. Mutation Semantics | N/A | No aplica: este HITO no muta GTs |
| 9. Canonicalization | 5.4 | Verificación de identidad criptográfica (oracle_hash) |

---

## 1. RESUMEN EJECUTIVO

Se ejecutó el análisis forense completo con **verificación directa de código fuente y contenido real de artefactos** (no solo PROJECT_TREE). La auditoría cubrió TRACK A (GT Forensic Qualification) y TRACK B (Calibration Infrastructure Audit). Se identificaron **18 evidencias forenses únicas** (6 P1, 4 P2, 8 verificaciones).

**Hallazgo central:**

> La infraestructura de calibración **NO está lista** para calibración científica reproducible. calibration_v1 es **INELIGIBLE** bajo el contrato actual por dos defectos contractuales/identitarios demostrados: (1) manifest en formato legacy (DF-19), incompatible con ManifestFingerprintCalculator actual; (2) node_ids no canónicos (`"value='p1_b0'"` en lugar de `"p1_b0"`) que producen una identidad criptográfica distinta bajo el algoritmo vigente (la incompatibilidad con el oracle_hash almacenado debe verificarse mediante recomputación efectiva). Un tercer aspecto (cobertura de traits) queda como **indicio pendiente de curaduría humana**. No existe infraestructura de partición de datasets, provenance de calibration runs, ni protocolo de calibración empírica ejecutable.

**Tabla de dimensiones de readiness:**

| Dimensión | Estado |
|---|---|
| Physical corpus discovery | COMPLETE |
| GT contractual eligibility | FAIL / PENDING |
| Scientific GT validity | NOT DEMONSTRATED |
| Calibration infrastructure readiness | NOT READY |
| Empirical parameter calibration | NOT PERFORMED |
| Baseline certification | BLOCKED |

**Nota epistemológica:** NOT READY para calibración NO significa que el corpus sea científicamente inválido. Significa que la infraestructura actual no permite calibración científica reproducible. La validez científica del contenido de GTs queda como NOT DEMONSTRATED, pendiente de curaduría humana experta.

**Clasificación final:**

> **NOT READY** — La infraestructura no permite calibración científica reproducible. Se requiere ADR_F17_BIS_05 para decidir: (a) política de curaduría de Ground Truths, (b) política de migración de .ast.json legacy, (c) adquisición de corpus adicional, (d) implementación de infraestructura de calibración, (e) protocolo de calibración empírica de parámetros. La clasificación NOT READY es robusta frente a la incertidumbre epistemológica de traits.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Lo que este HITO puede establecer

- Si los Ground Truths existentes pueden hidratarse bajo los contratos actuales (hydrate_ground_truth).
- Si los Ground Truths producen identidad criptográfica válida (OracleSemanticIdentityCalculator).
- Si los node_id legacy producen identidad válida bajo el algoritmo vigente (H-5.1-F queda como NO DEMOSTRADA por falta de recomputación efectiva).
- Si los .ast.json legacy son directamente compatibles con el AST actual (cierra H-5.1-D).
- Si existe indicio de discrepancia entre cobertura observada y declarada (H-5.1-C queda como NO DEMOSTRADA).
- Si calibration_v1 puede considerarse científicamente reutilizable bajo los contratos actuales.
- Qué infraestructura de calibración existe actualmente (inventario).
- Si existe separación adecuada entre calibración, validación y evaluación final.
- Si la infraestructura registra suficiente provenance para reproducir una calibration run.
- Si existe riesgo demostrable de leakage, duplicación o sobreajuste del corpus durante la calibración.

### 2.2 Lo que este HITO NO puede establecer

- La validez científica absoluta del contenido de los Ground Truths (requiere curaduría humana experta).
- La cobertura real de traits del corpus (requiere inspección visual de contenido).
- La calibración empírica de pesos y thresholds (pertenece al Execution Plan post-ADR).
- La implementación de infraestructura de calibración nueva.
- La edición o corrección de Ground Truths existentes.
- La selección de documentos adicionales para el corpus (pertenece a ADR_F17_BIS_05).
- La corrección matemática completa de cada algoritmo de evaluación (requiere pruebas contra oráculos matemáticos conocidos).
- La incompatibilidad efectiva de node_ids legacy con oracle_hash almacenado (requiere recomputación efectiva).

### 2.3 Restricciones operativas

- **Hardware:** 16GB RAM (ADR Maestro §4, ROADMAP §I).
- **Zhang-Shasha:** Complejidad O(n²) en espacio. Si se ejecutan benchmarks sobre árboles grandes (>1000 nodos), puede haber presión de memoria.
- **Corpus actual:** 7 identidades únicas candidatas (HITO 5.1). **Con 7 documentos, un esquema clásico train/validation/holdout no resulta estadísticamente robusto y requiere una política específica de validación.** La alternativa es leave-one-out cross-validation (7 folds), bootstrap, o adquisición de corpus adicional (DC-5.1-03 de HITO 5.1: 13-23 documentos faltantes).

### 2.4 Método forense

La auditoría sigue el método:

1. Cargar fuentes normativas (ADRs, NADRs, HITOs previos).
2. Inspeccionar contenido real de PDFs y Ground Truths (no solo manifest).
3. Verificar hidratación de GTs bajo contratos actuales.
4. Recomputar identidad criptográfica (oracle_hash) y comparar con almacenada.
5. Auditar infraestructura de calibración existente contra PROJECT_TREE y código directo.
6. Clasificar parámetros (normativos/empíricos/heurísticos/ajustados).
7. Determinar riesgos de leakage/duplicación.
8. Producir evidencia forense reproducible.

**Nota epistemológica:** Este HITO distingue explícitamente entre:
- **Evidencia demostrada:** Verificación directa de código, artefactos o contratos.
- **Indicio:** Señal que sugiere un fenómeno pero no lo demuestra (ej. nombres de archivos que sugieren traits).
- **Riesgo potencial:** Posibilidad de un fenómeno adverso, no incidente observado.
- **Consecuencia pendiente de verificación:** Fenómeno que se sigue lógicamente de la evidencia pero requiere recomputación/cálculo efectivo para confirmarse.

---

## 3. ALCANCE AUDITADO

### 3.1 Objetos de auditoría (verificados contra PROJECT_TREE y código directo)

**Ground Truth Domain (core/benchmark/ground_truth/) — VERIFICADO:**
- `models.py` → GroundTruthLifecycleState (4 estados), DraftSubState, GroundTruthDraft, SealedOracle, hydrate_ground_truth()
- `ports.py` → GroundTruthReaderPort, GroundTruthDraftWriterPort, ASTExtractionPort, GroundTruthArtifactPort
- `identity.py` → OracleSemanticIdentityCalculator (incluye node_id en hash)
- `lifecycle.py` → LifecycleTransitionAuthority (audit, validate, seal, rollback_to_draft, rollback_to_audited)
- `validity.py` → OracleValidityContract
- `completeness.py` → BaselineCompletenessVerifier
- `use_cases.py` → LoadGroundTruthUseCase, GenerateGoldenDraftUseCase, SealGroundTruthUseCase
- `errors.py` → GroundTruthError, EmptyGroundTruthDraftError, OracleValidityError, IncompleteBaselineError, OrphanOracleError, BaselineContractError, SealedOracleOverwriteError

**Corpus Domain (core/benchmark/corpus/):**
- `models.py` → DocumentFingerprint, CorpusVersion, CorpusDocumentMetadata, CorpusManifest
- `enums.py` → ExtractionChallengeTrait
- `ports.py` → DocumentMetadataExtractorPort, CorpusManifestReaderPort, CorpusManifestWriterPort
- `services.py` → ManifestFingerprintCalculator, ManifestLineageSealer
- `use_cases.py` → BootstrapCorpusManifestUseCase, LoadCorpusManifestUseCase
- `dtos.py` → RawDocumentEntryDTO, RawCorpusManifestDTO, BootstrapCorpusResult
- `mappers.py` → CorpusToBenchmarkDatasetMapper

**Infraestructura de persistencia (infra/fs/):**
- `ground_truth_store.py` → LocalFileSystemGroundTruthReader, LocalFileSystemGroundTruthDraftWriter, LocalFileSystemGroundTruthArtifactAdapter
- `corpus_repository.py` → LocalFileSystemCorpusLoader

**Serialización (infra/serialization/):**
- `ast_json.py` → serialize_ast_json(), deserialize_ast_json(), write_ast_json_atomic(), read_ast_json()

**Serialización experimental (experiments/loaders/):**
- `ast_json_loader.py` → load_ast_sequence_from_json()

**Infraestructura de calibración/benchmark (tools/evaluation/) — VERIFICADO:**
- `run_benchmark.py` → entry point de benchmark
- `application/benchmark_service.py` → TopologyBenchmarkService (NO tiene partición de datasets)
- `topology/metrics/` → NodeCountMetric, EntityRecallMetric, SequenceAlignmentMetric, StructuralTopologyMetric
- `topology/models.py` → MetricName, BenchmarkDocument, ConfusionMatrix, MetricResult, DocumentEvaluationResult, BenchmarkSummaryReport
- `topology/ports.py` → TopologyMetric, BenchmarkAggregationStrategy
- `topology/strategies.py` → DefaultBenchmarkAggregationStrategy
- `topology/metrics/__init__.py` → MetricRegistry, default_metrics() (4 métricas por defecto)
- `topology/fingerprint.py` → ASTFingerprintPolicy (semantic_fingerprint, identity_fingerprint)
- `infrastructure/corpus_repository.py` → LocalFileSystemCorpusRepository

**Infraestructura de regresión (core/benchmark/topology/regression/) — VERIFICADO:**
- `adapter.py` → RegressionAdapter (verify_document_identity, verify_oracle_integrity, verify_sealed_state, verify_completeness, verify_all)
- `mechanism.py` → DoubleProtectionMechanism (doble protección: NSS + regla absoluta CRITICAL)
- `strategy.py` → RegressionEvaluationStrategy
- `models.py` → RegressionVerdict, RegressionThresholds, RegressionEvaluationReport
- `aggregation.py` → aggregate_corpus_verdicts()
- `errors.py` → RegressionError, OracleIntegrityError, OracleNotSealedError, OracleDocumentMismatchError, MissingOracleHashError, InvalidNSSScoreError

**Taxonomía de criticidad (core/benchmark/topology/criticality/) — VERIFICADO:**
- `costs.py` → CriticalityAwareCostContext (CRITICAL=5.0, WARNING=2.0, INFO=1.0, sustitución usa text_content SIN .strip())
- `models.py` → NodeCriticality
- `policy.py` → DefaultCriticalityPolicy
- `verdict.py` → CriticalityVerdictEmitter
- `ports.py` → CriticalityPolicy
- `traceability.py` → ClassificationTracer, ClassificationRecord, ClassificationTrace, ReclassificationEvent

**Composition root (bootstrap/):**
- `topology.py` → DefaultNodeMatchingPolicy, create_topology_evaluator()

**Artefactos de corpus (tests/corpus/) — VERIFICADO:**
- `calibration_v1/manifest.json` → formato legacy (ground_truth_version, ground_truth_sha256 en lugar de oracle_hash, ground_truth_state)
- `calibration_v1/ground_truth/*.json` → 5 archivos (doc_01_single a doc_05_graph) con node_ids legacy (`value='p1_b0'`)
- `benchmark_v1/manifest.json` → vacío (documents: [])
- `*.ast.json` legacy → 2 archivos (johnstone00distribution, marchenko_pastur) con estructura no directamente compatible con AST V2

**Tests relevantes (tests/unit/):**
- `test_ground_truth_lifecycle.py`
- `test_ground_truth_models.py`
- `test_ground_truth_completeness.py`
- `test_ground_truth_validity.py`
- `test_ground_truth_ports.py`
- `test_ground_truth_sealed_protection.py`
- `test_ground_truth_sealing_atomicity.py`
- `test_oracle_identity.py`
- `test_framing_injectivity.py`
- `test_manifest_fingerprint.py`
- `test_corpus_models.py`
- `test_corpus_port_asymmetry.py`
- `test_criticality_costs.py`
- `test_criticality_policy.py`
- `test_criticality_verdict.py`
- `test_regression_adapter.py`
- `test_regression_mechanism.py`
- `test_regression_models.py`
- `test_regression_strategy.py`
- `test_zhang_shasha.py`
- `test_structural_metric.py`

### 3.2 Explícitamente excluido

- Modificar Ground Truths existentes.
- Implementar infraestructura de calibración nueva.
- Calibrar pesos o thresholds.
- Seleccionar documentos adicionales para el corpus.
- Optimizar algoritmos.
- Infraestructura distribuida (Redis, Message Brokers, Kubernetes).
- Motores de extracción de visión computacional (Fase 17).
- Optimizaciones de rendimiento, asincronía o memoria (Fase 18).
- **Inspección semántica/visual humana de PDFs** (requiere curaduría humana experta, fuera del alcance forense ejecutado).

---

## 4. FUENTES DE EVIDENCIA

**Fuentes inspeccionadas:**
- Contenido real de `tests/corpus/calibration_v1/manifest.json`
- Contenido real de `tests/corpus/calibration_v1/ground_truth/doc_01_single.json`
- Contenido real de `tests/corpus/benchmark_v1/manifest.json`
- Contenido real de `tests/corpus/johnstone00distribution_3hoja.pdf.ast.json`
- Inventario de `tests/corpus/calibration_v1/candidates/` (docling + pymupdf)
- Código fuente de `core/benchmark/ground_truth/models.py`
- Código fuente de `core/benchmark/ground_truth/identity.py`
- Código fuente de `core/benchmark/topology/criticality/costs.py`
- Código fuente de `core/benchmark/topology/regression/mechanism.py`
- Código fuente de `tools/evaluation/application/benchmark_service.py`
- Código fuente de `tools/evaluation/topology/metrics/__init__.py`

---

## 5. TRACK A — GROUND TRUTH FORENSIC QUALIFICATION

### 5.1 Inventario físico del corpus (7 identidades de HITO 5.1)

**Manifest de calibration_v1 (VERIFICADO):**

```json
{
  "corpus_version": "v1.0",
  "manifest_hash": "c64a74d7f483d9cebda323f5791b31afb450c139e5ac6d96e4c1786b227d37ea",
  "documents": [
    {
      "document_id": "doc_01_single",
      "sha256": "2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3",
      "traits": ["native_pdf"],
      "page_count": 3,
      "ground_truth_version": null,
      "ground_truth_sha256": null
    },
    {
      "document_id": "doc_02_double",
      "sha256": "84891f98114b90a7b8b80eee46d5de9990707046b8cea29affb3536da51a3123",
      "traits": ["native_pdf"],
      "page_count": 3,
      "ground_truth_version": null
    },
    {
      "document_id": "doc_03_math",
      "sha256": "21b9283a83f92983ebeb688d76a0d8c0de5068dc703129db42e7e2a2ea2a19fe",
      "traits": ["native_pdf"],
      "page_count": 3,
      "ground_truth_version": null,
      "ground_truth_sha256": null
    },
    {
      "document_id": "doc_04_table",
      "sha256": "de56cd0420852abdf1c13e4a4853e5977a6ecf8021811bb5cb70d75ccfa925ab",
      "traits": ["native_pdf"],
      "page_count": 3,
      "ground_truth_version": null,
      "ground_truth_sha256": null
    },
    {
      "document_id": "doc_05_graph",
      "sha256": "274ce908d472a06b6211e667861d5cf7bde2749d1412415447c7e1d3ce6df789",
      "traits": ["native_pdf"],
      "page_count": 3,
      "ground_truth_version": null,
      "ground_truth_sha256": null
    }
  ]
}
```

**Hallazgo E-5.4-001 (P1 — INCOMPATIBILIDAD):** El manifest usa campos **`ground_truth_version`** y **`ground_truth_sha256`** en lugar de **`oracle_hash`** y **`ground_truth_state`**. Esto confirma **DF-19** (HITO 5.1 GAP-5.1-01): el manifest es incompatible con el formato actual de `ManifestFingerprintCalculator.compute_hash()`.

**Hallazgo E-5.4-011 (P2 — OBSERVACIÓN/INDICIO):** Los 5 documentos declaran únicamente `traits: ["native_pdf"]`. Los nombres de archivos sugieren posible variedad:
- `doc_02_double` → podría sugerir MULTI_COLUMN
- `doc_03_math` → podría sugerir HEAVY_MATHEMATICS
- `doc_04_table` → podría sugerir COMPLEX_TABLES
- `doc_05_graph` → podría sugerir MIXED_CONTENT

**Nota epistemológica:** Los nombres de archivos son **indicios**, no evidencia suficiente para demostrar cobertura real. Este HITO no ejecutó inspección visual de contenido de PDFs. La cobertura real queda como **NO DEMOSTRADA**, pendiente de curaduría humana experta.

**Cierre de H-5.1-C:** **NO DEMOSTRADA.** Existe indicio de posible subdeclaración de traits, pero no se puede afirmar científicamente la cobertura real sin inspección de contenido.

**Completitud biyectiva a nivel de archivos:**
| PDF | GT | Estado |
|---|---|---|
| doc_01_single | doc_01_single.json (35647 bytes) | ✅ |
| doc_02_double | doc_02_double.json (103119 bytes) | ✅ |
| doc_03_math | doc_03_math.json (64820 bytes) | ✅ |
| doc_04_table | doc_04_table.json (56761 bytes) | ✅ |
| doc_05_graph | doc_05_graph.json (86992 bytes) | ✅ |

**E-5.4-003 (VERIF):** Completitud biyectiva 5 PDFs ↔ 5 GTs a nivel de archivos.

**Manifest de benchmark_v1:**
```json
{
  "corpus_version": "v1.0",
  "manifest_hash": "fa8b919c909d5eb9e373d090928170eb0e7936ac20ccf413332b96520903168e",
  "documents": []
}
```

**E-5.4-010 (VERIF):** benchmark_v1 está vacío (documents: []). Un corpus vacío con hash correcto es compatible con el contrato vigente.

### 5.2 Verificación de traits (Declared vs Observed)

**Enum verificado:**
- `core/benchmark/corpus/enums.py::ExtractionChallengeTrait` (NATIVE_PDF, MULTI_COLUMN, HEAVY_MATHEMATICS, COMPLEX_TABLES, DENSE_TYPOGRAPHY, MIXED_CONTENT, OCR_DEPENDENCY)

**Protocolo de búsqueda de evidencia:**

Para cada PDF, verificar físicamente la presencia de cada trait:

| Trait | Definición | Método de verificación |
|---|---|---|
| NATIVE_PDF | PDF nativo (no escaneado) | Inspección de metadata PDF |
| MULTI_COLUMN | Múltiples columnas | Inspección visual de páginas |
| HEAVY_MATHEMATICS | Alta densidad de ecuaciones | Inspección visual + conteo de payloads MathPayload |
| COMPLEX_TABLES | Tablas complejas/anidadas | Inspección visual + conteo de payloads TablePayload |
| DENSE_TYPOGRAPHY | Tipografía densa | Inspección visual |
| MIXED_CONTENT | Contenido mixto (texto + figuras + tablas) | Inspección visual |
| OCR_DEPENDENCY | Requiere OCR | Inspección de metadata PDF |

**Nota:** Este HITO no ejecuta inspección visual directa de PDFs. Se identifica un **indicio** de posible subdeclaración de traits basado en nombres de archivos, pero la cobertura real queda como NO DEMOSTRADA.

**Formato de evidencia esperado por trait (para futura curaduría):**

| Campo | Definición |
|---|---|
| document | Identidad del documento |
| trait | Trait verificado |
| observed | TRUE / FALSE |
| evidence | Páginas o ubicación de evidencia |
| confidence | HIGH / MEDIUM / LOW |
| method | MANUAL_FORENSIC_REVIEW |

### 5.3 Hidratación de Ground Truths (hydrate_ground_truth)

**Código verificado (`core/benchmark/ground_truth/models.py`):**

```python
class GroundTruthLifecycleState(str, Enum):
    DRAFT = "draft"
    AUDITED = "audited"
    VALIDATED = "validated"
    SEALED = "sealed"

class DraftSubState(str, Enum):
    DRAFT = "draft"
    AUDITED = "audited"
    VALIDATED = "validated"

class GroundTruthDraft(BaseModel):
    model_config = ConfigDict(frozen=True)
    document_id: str = Field(..., min_length=1)
    nodes: Tuple[ASTNode, ...] = Field(...)
    sub_state: DraftSubState = Field(default=DraftSubState.DRAFT)

class SealedOracle(BaseModel):
    model_config = ConfigDict(frozen=True)
    document_id: str = Field(..., min_length=1)
    nodes: Tuple[ASTNode, ...] = Field(...)

def hydrate_ground_truth(
    document_id: str,
    nodes: Tuple[ASTNode, ...],
    state: GroundTruthLifecycleState,
) -> GroundTruthDraft | SealedOracle:
    if state == GroundTruthLifecycleState.SEALED:
        return SealedOracle(document_id=document_id, nodes=nodes)
    if state == GroundTruthLifecycleState.DRAFT:
        return GroundTruthDraft(document_id=document_id, nodes=nodes, sub_state=DraftSubState.DRAFT)
    if state == GroundTruthLifecycleState.AUDITED:
        return GroundTruthDraft(document_id=document_id, nodes=nodes, sub_state=DraftSubState.AUDITED)
    if state == GroundTruthLifecycleState.VALIDATED:
        return GroundTruthDraft(document_id=document_id, nodes=nodes, sub_state=DraftSubState.VALIDATED)
    raise ValueError(f"Invariant failure: unknown lifecycle state '{state}' for document '{document_id}'.")
```

**E-5.4-013 (VERIF — PASS para implementación contractual):** La función de hidratación es compatible con los contratos de lifecycle según inspección estática:
- Retorna `SealedOracle` si `state=SEALED`
- Retorna `GroundTruthDraft` con sub_state apropiado para DRAFT/AUDITED/VALIDATED
- NO valida no-vaciedad (responsabilidad de `OracleValidityContract`)
- Requiere que el consumidor provea el estado explícitamente al cargar desde disco

**Nota epistemológica:** "La función de hidratación es compatible con los contratos de lifecycle" NO equivale a "todos los Ground Truth físicos pueden hidratarse correctamente". La hidratación exitosa de cada artefacto físico queda pendiente de verificación efectiva.

**Nota sobre estados efímeros:** DRAFT/AUDITED/VALIDATED son estados del proceso de curaduría. No se persisten en disco como metadata independiente. Esto es una característica de diseño del contrato de lifecycle, no un defecto.

### 5.4 Verificación de identidad criptográfica (oracle_hash)

**Código verificado (`core/benchmark/ground_truth/identity.py`):**

```python
class OracleSemanticIdentityCalculator:
    @staticmethod
    def calculate(nodes: Tuple[ASTNode, ...]) -> str:
        parts = []
        for node in nodes:
            payload_json = node.payload.model_dump_json()
            payload_hash = compute_sha256(payload_json.encode("utf-8"))
            node_identity = (
                f"{node.node_id}:"
                f"{node.node_type.value}:"
                f"{node.strategy.value}:"
                f"{payload_hash}"
            )
            parts.append(node_identity.encode("utf-8"))
        return compute_sha256(b"".join(parts))
```

**E-5.4-012 (VERIF — CRÍTICO para H-5.1-F):** OracleSemanticIdentityCalculator **INCLUYE node_id en el hash**. La identidad del nodo es:
```
node_id:node_type:strategy:payload_hash
```

Esto significa que si dos oráculos tienen el mismo contenido pero diferentes node_ids, producirán hashes diferentes. Esto es intencional para proteger la integridad del proceso de certificación.

**Implicación para H-5.1-F:** Si calibration_v1 tiene node_ids legacy (`"value='p1_b0'"` en lugar de `"p1_b0"`), el oracle_hash calculado será **diferente** al oracle_hash calculado con node_ids canónicos. **Sin embargo, la incompatibilidad efectiva con el oracle_hash almacenado debe verificarse mediante recomputación efectiva.**

### 5.5 Compatibilidad de .ast.json legacy

**Contenido verificado (`tests/corpus/johnstone00distribution_3hoja.pdf.ast.json`):**

```json
[
  {
    "node_id": "node_0",
    "type": "section",
    "content": "On the distribution of the largest principal component",
    "latex": null,
    "status": null,
    "metadata": {}
  },
  {
    "node_id": "node_1",
    "type": "paragraph",
    "content": "Iain M. Johnstone\\*",
    "latex": null,
    "status": null,
    "metadata": {}
  }
]
```

**E-5.4-008 (P1 — INCOMPATIBILIDAD):** La estructura de .ast.json legacy **no es directamente compatible** con el contrato AST V2 actual y requiere migración/adaptación estructural o re-extracción, decisión que corresponde al ADR:

| Aspecto | .ast.json legacy | AST V2 actual |
|---|---|---|
| Tipo de nodo | `"type": "section"` | `"node_type": "heading"` |
| Contenido | `"content": "..."` | `"payload": {"content": "..."}` |
| Latex | `"latex": null` | No existe (MathPayload tiene `content`) |
| Status | `"status": null` | No existe |
| Sequence ID | No existe | `"sequence_id": 1` |
| Strategy | No existe | `"strategy": "translate"` |
| Depth | No existe | `"depth": 0` |
| Parent node | No existe | `"parent_node_id": null` |
| Control plane | No existe | `"control_plane": {}` |
| Segment index | No existe | `"segment_index": 0` |
| Segment count | No existe | `"segment_count": 1` |
| Metadata | `"metadata": {}` | Metadata rica (bboxes, pages, confidence, etc.) |

**Cierre de H-5.1-D:** **RECHAZADA.** Los .ast.json legacy no son directamente compatibles con el contrato AST V2 actual. Requieren migración/adaptación estructural o re-extracción, decisión que corresponde al ADR.

**Inventario de .ast.json legacy:**
- `johnstone00distribution_3hoja.pdf.ast.json` (14013 bytes)
- `marchenko_pastur_1967_3hoja.pdf.ast.json` (13716 bytes)

**E-5.4-022 (P2):** Solo 2 de 7 identidades tienen .ast.json legacy. `[Amoretal_2023]_3hojas.pdf` NO tiene .ast.json legacy.

### 5.6 Node_id canónico vs legacy (H-5.1-F)

**Contenido verificado (`tests/corpus/calibration_v1/ground_truth/doc_01_single.json`):**

```json
[
  {
    "node_id": "value='p1_b0'",
    "sequence_id": 1,
    "node_type": "heading",
    "strategy": "translate",
    "metadata": {
      "bboxes": [
        {
          "x0": 209.6510009765625,
          "y0": 116.88343811035156,
          "x1": 402.4118957519531,
          "y1": 134.09884643554688,
          "is_normalized": false
        }
      ],
      "pages": [1],
      "provider_native_id": "0",
      "confidence": 1.0,
      "layout_reading_order": 0,
      "semantic_origin": "pdf_text"
    },
    "depth": 0,
    "payload": {
      "content": "Minimum Viable Scale"
    },
    "control_plane": {},
    "parent_node_id": null,
    "segment_index": 0,
    "segment_count": 1
  }
]
```

**E-5.4-004 (P1 — DISCREPANCIA DE IDENTIDAD):** El node_id contiene `"value='p1_b0'"` en lugar de `"p1_b0"`. Esto es una representación legacy no canónica.

**Lo demostrado:**
- node_id entra en el framing del hash (E-5.4-012)
- `"value='p1_b0'"` ≠ `"p1_b0"` (E-5.4-004)
- Por lo tanto, node_id legacy produce una identidad criptográfica distinta bajo el algoritmo vigente

**Lo NO demostrado (pendiente de recomputación efectiva):**
- stored oracle_hash ≠ recomputed oracle_hash
- Esto requiere cálculo efectivo y comparación

**Cierre de H-5.1-F:** **NO DEMOSTRADA.** Se demuestra que node_id legacy produce una identidad criptográfica distinta bajo el algoritmo vigente. La incompatibilidad efectiva con el oracle_hash almacenado debe verificarse mediante recomputación efectiva. Esta verificación corresponde a ADR_F17_BIS_05 o al Execution Plan posterior.

### 5.7 Verificación de completitud de baseline

**Función a verificar:**
- `core/benchmark/ground_truth/completeness.py::BaselineCompletenessVerifier.verify()`

**Contrato de validez:**
- `core/benchmark/ground_truth/validity.py::OracleValidityContract.validate()`

**Invariante de Zero Partial Sealing (ADR Maestro §5):**
- Un corpus NO puede entrar en estado SEALED si no existe correspondencia biyectiva completa entre PDFs declarados y sus oráculos AST auditados ($N_{PDF} = N_{GT}$).

**E-5.4-003 (VERIF):** Completitud biyectiva a nivel de archivos: 5 PDFs ↔ 5 GTs. Sin embargo, los GTs no son elegibles bajo el contrato actual (DF-19, node_ids legacy), por lo que la completitud biyectiva NO se cumple a nivel de contrato.

**Nota sobre Zero Partial Sealing:** La invariante de Zero Partial Sealing NO está violada. No hubo sellado parcial (0/5 sellados). El corpus es ineligible para sealing, pero eso no equivale a violación de la invariante de Zero Partial Sealing. La invariante se violaría si se sellara un corpus con $N_{PDF} \neq N_{GT}$.

---

## 6. TRACK B — SCIENTIFIC CALIBRATION INFRASTRUCTURE AUDIT

### 6.1 Inventario de infraestructura de calibración existente

**Verificación contra PROJECT_TREE y código directo:**

| Componente | Existe | Evidencia | Observación |
|---|:---:|---|---|
| TopologyBenchmarkService | ✅ | `tools/evaluation/application/benchmark_service.py` | Evalúa documentos contra métricas, NO tiene partición de datasets |
| MetricRegistry | ✅ | `tools/evaluation/topology/metrics/__init__.py` | 4 métricas por defecto: NodeCount, EntityRecall, SequenceAlignment, Structural |
| RegressionEvaluationStrategy | ✅ | `core/benchmark/topology/regression/strategy.py` | Estrategia de evaluación de regresión |
| DoubleProtectionMechanism | ✅ | `core/benchmark/topology/regression/mechanism.py` | Doble protección: NSS + regla absoluta CRITICAL |
| CriticalityAwareCostContext | ✅ | `core/benchmark/topology/criticality/costs.py` | CRITICAL=5.0, WARNING=2.0, INFO=1.0 |
| CriticalityVerdictEmitter | ✅ | `core/benchmark/topology/criticality/verdict.py` | Emite veredictos de criticidad |
| create_topology_evaluator() | ✅ | `bootstrap/topology.py` | Composition root con UnitCostContext por defecto |
| Partición de datasets (train/validation/holdout) | ❌ | No existe en PROJECT_TREE | TopologyBenchmarkService itera sobre todos los documentos |
| Calibration Provenance Record | ❌ | No existe en PROJECT_TREE | No hay sistema de tracking de calibration runs |
| Capacidad funcional de análisis estadístico reproducible | ❌ | Ausencia funcional demostrada | No existe mecanismo para el protocolo requerido |
| Protocolo de calibración empírica ejecutable | ❌ | No existe en PROJECT_TREE | No hay protocolo definido |

**E-5.4-018 (P1 — AUSENCIA DE INFRAESTRUCTURA):** Se demuestra la ausencia funcional de:
- Partición de datasets (train/validation/holdout)
- Provenance de calibration runs
- Capacidad funcional de análisis estadístico reproducible requerido por el protocolo
- Protocolo de calibración empírica ejecutable

**Nota:** La ausencia de un directorio/módulo llamado "calibration" no constituye por sí misma un defecto. La calibración podría implementarse como una aplicación sobre infraestructura benchmark existente. Lo que se demuestra es la ausencia de los componentes funcionales específicos requeridos para calibración científica reproducible.

### 6.2 Clasificación de parámetros (normativos/empíricos/heurísticos/ajustados)

**Clasificación verificada:**

| Clasificación | Definición | Ejemplo |
|---|---|---|
| Normativo | Derivado de decisión arquitectónica (ADR/NADR) | Pesos de criticidad (NADR-18 §5.3 R12) |
| Empírico | Derivado de observaciones sobre corpus | Threshold calibrado sobre datos |
| Heurístico | Elegido por criterio de diseño | Threshold 0.95 "porque parecía razonable" |
| Ajustado | Obtenido mediante optimización/calibración | argmin(parameter_loss) |

**Parámetros actuales:**

| Parámetro | Valor actual | Clasificación | Fuente |
|---|---|---|---|
| Pesos de criticidad | CRITICAL=5.0, WARNING=2.0, INFO=1.0 | Normativo/Heurístico | NADR-18 §5.3 R12: "Propuesta inicial sujeta a validación empírica" |
| Thresholds de NSS | 0.80/0.95 | Heurístico | FASE_4_HANDOFF, no calibrados empíricamente |
| Normalización | MaxBoundNormalizationPolicy | Normativo | NADR-19 |
| Método de evaluación | DoubleProtectionMechanism | Normativo | NADR-19 |

**E-5.4-019 (P1 — AUSENCIA DE CALIBRACIÓN EMPÍRICA):** Ninguno de los parámetros ha sido calibrado empíricamente. Todos son normativos o heurísticos. La validación empírica de pesos de criticidad (mencionada en NADR-18 §5.3 R12 como "propuesta inicial sujeta a validación empírica") está pendiente.

### 6.3 Separación de datasets (o ausencia de ella)

**Código verificado (`tools/evaluation/application/benchmark_service.py`):**

```python
class TopologyBenchmarkService:
    def evaluate_corpus(
        self,
        provider_name: str,
        documents: Sequence[BenchmarkDocument],
    ) -> BenchmarkSummaryReport:
        doc_results = [self.evaluate_document(doc) for doc in documents]
        return self._strategy.aggregate(
            provider_name=provider_name,
            results=doc_results,
        )
```

**E-5.4-016 (VERIF):** TopologyBenchmarkService **NO tiene partición de datasets**. Simplemente itera sobre todos los documentos y agrega resultados. No existe separación train/validation/holdout.

**E-5.4-020 (P2):** Con 7 identidades únicas (HITO 5.1), un esquema clásico train/validation/holdout **no resulta estadísticamente robusto y requiere una política específica de validación.** La alternativa es leave-one-out cross-validation (7 folds), bootstrap, o adquisición de corpus adicional.

### 6.4 Reproducibilidad y provenance (mínimo necesario)

**E-5.4-021 (P1 — AUSENCIA DE PROVENANCE DE CALIBRATION RUNS):** No existe sistema de provenance de calibration runs. No hay registro de:
- corpus_identity (SHA-256 del manifest)
- metric_configuration (hash de configuración)
- parameters (pesos/thresholds)
- result (scores)
- timestamp (fecha de ejecución)

**Nota epistemológica:** Esto se limita a calibration-run provenance, no a provenance del sistema en general. El proyecto sí tiene conceptos de identidad y trazabilidad de artefactos (manifest_hash, DocumentFingerprint.sha256, oracle_hash, CorpusVersion), pero eso no equivale a experiment provenance.

**Observación:** No se requiere Calibration Provenance Record de 18 campos (YAGNI). 5 campos mínimos serían suficientes para reproducibilidad, pero actualmente no existe ninguno.

### 6.5 calibration_v1 como caso de test

**Clasificación de calibration_v1:**

| Aspecto | Estado | Naturaleza | Justificación |
|---|---|---|---|
| PDFs científicamente adecuados | ⚠️ PENDIENTE | Curaduría | Requiere inspección visual de contenido |
| GTs hidratables | ✅ SÍ | Verificación de implementación contractual | hydrate_ground_truth funciona correctamente |
| ASTs semánticamente correctos | ⚠️ PENDIENTE | Curaduría | Requiere curaduría humana experta |
| Node_ids canónicos | ❌ NO | Discrepancia de identidad | E-5.4-004: `"value='p1_b0'"` en lugar de `"p1_b0"` |
| Oracle_hashes válidos | ⚠️ PENDIENTE DE VERIFICACIÓN | Consecuencia criptográfica | E-5.4-012 + E-5.4-004: node_id en hash → identidad distinta; incompatibilidad efectiva pendiente de recomputación |
| Manifest reconstruible | ❌ NO | Incompatibilidad contractual | E-5.4-001: formato legacy (DF-19) |
| Traits completos | ⚠️ PENDIENTE | Indicio | E-5.4-011: indicio de subdeclaración, no demostrado |

**Clasificación final:** **INELIGIBLE** — calibration_v1 NO es elegible para sealing/baseline bajo el contrato vigente. Esto NO equivale a "científicamente inválido". Significa que no es elegible como baseline canónica bajo el contrato vigente.

### 6.6 Inventario de candidates (docling vs pymupdf)

**Contenido verificado (`tests/corpus/calibration_v1/candidates/`):**

| Extractor | Archivos JSON | Archivos meta.json |
|---|:---:|:---:|
| docling | 5 | 5 |
| pymupdf | 5 | **0** |

**E-5.4-023 (P2):** Los candidates de pymupdf NO tienen archivos meta.json, mientras que los candidates de docling SÍ tienen meta.json. Esto representa una inconsistencia de metadata entre extractores. La pregunta para el ADR/Execution Plan es: ¿meta.json es parte del contrato científico del candidate o simplemente un artefacto auxiliar de un extractor?

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| # | Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|---|
| 1 | GTs hidratables | ✅ hydrate_ground_truth funciona (implementación contractual) | NADR-12 §5.1 R3 | HITO 5.1 | PASS — implementación contractual | E-5.4-013 |
| 2 | Identidad criptográfica válida | ⚠️ node_ids legacy producen identidad distinta; incompatibilidad efectiva pendiente de recomputación | NADR-16, NADR-17 | HITO 5.1 | PENDING VERIFICATION | E-5.4-004, E-5.4-012 |
| 3 | Cobertura observada = declarada | ⚠️ Indicio de subdeclaración (no demostrado) | ADR Maestro §6 | HITO 5.1 | NOT DEMONSTRATED | E-5.4-011 |
| 4 | Infraestructura de calibración | ❌ Ausencia funcional demostrada | NADR-18, NADR-19 | HITO 5.3 | FAIL | E-5.4-018, E-5.4-021 |
| 5 | Separación de datasets | ❌ No existe partición | ENGINEERING_PRINCIPLES §I | HITO 5.1 | FAIL | E-5.4-016, E-5.4-020 |
| 6 | Provenance suficiente | ❌ No existe sistema de tracking de calibration runs | ROADMAP §I Principio 6 | HITO 5.2 | FAIL | E-5.4-021 |
| 7 | Completitud biyectiva | ⚠️ A nivel de archivos SÍ, a nivel de contrato NO | NADR-13 §5.2 R4-R8 | HITO 5.1 | PARTIAL | E-5.4-003 |
| 8 | Zero Partial Sealing | ✅ No violado (0/5 sellados, no hubo sellado parcial) | ADR Maestro §5 | HITO 5.1 | PASS / NOT YET EXERCISED | E-5.4-003 |
| 9 | .ast.json legacy compatibles | ❌ No directamente compatibles, requieren migración/adaptación o re-extracción (decisión del ADR) | N/A | HITO 5.1 | FAIL | E-5.4-008 |
| 10 | Parámetros calibrados empíricamente | ❌ Todos normativos/heurísticos | NADR-18 §5.3 R12 (validación empírica) | N/A | PENDING EMPIRICAL VALIDATION | E-5.4-019 |

---

## 8. REGISTRO DE EVIDENCIA FORENSE — INVENTARIO CANÓNICO

**Conteo verificado:** COUNT(unique E-ID) = 18 = COUNT(P1: 6) + COUNT(P2: 4) + COUNT(VERIF: 8)

| ID | Sev | Tipo | Evidencia | Hallazgo |
|---|---|---|---|---|
| E-5.4-001 | **P1** | INCOMPATIBILIDAD | `calibration_v1/manifest.json` | Manifest en formato legacy (DF-19): `ground_truth_version`, `ground_truth_sha256` en lugar de `oracle_hash`, `ground_truth_state`. Incompatible con ManifestFingerprintCalculator actual |
| E-5.4-003 | VERIF | VERIFICACIÓN | Inventario de GTs | Completitud biyectiva a nivel de archivos: 5 PDFs ↔ 5 GTs |
| E-5.4-004 | **P1** | DISCREPANCIA DE IDENTIDAD | `doc_01_single.json` | node_id contiene `"value='p1_b0'"` en lugar de `"p1_b0"` (representación legacy no canónica). Produce identidad criptográfica distinta bajo el algoritmo vigente. Incompatibilidad efectiva con oracle_hash almacenado pendiente de recomputación efectiva |
| E-5.4-008 | **P1** | INCOMPATIBILIDAD | `johnstone00distribution_3hoja.pdf.ast.json` | Estructura no directamente compatible con AST V2. Requiere migración/adaptación estructural o re-extracción, decisión que corresponde al ADR |
| E-5.4-010 | VERIF | VERIFICACIÓN | `benchmark_v1/manifest.json` | benchmark_v1 está vacío (documents: []). Compatible con contrato vigente |
| E-5.4-011 | **P2** | OBSERVACIÓN/INDICIO | `calibration_v1/manifest.json` | Los 5 documentos declaran únicamente `traits: ["native_pdf"]`. Nombres de archivos sugieren posible variedad. **Nota:** Nombres de archivos son indicios, no evidencia suficiente. Cobertura real NO DEMOSTRADA, pendiente de curaduría humana |
| E-5.4-012 | VERIF | VERIFICACIÓN | `identity.py` | OracleSemanticIdentityCalculator INCLUYE node_id en el hash (crítico para H-5.1-F) |
| E-5.4-013 | VERIF | VERIFICACIÓN | `models.py` | hydrate_ground_truth funciona correctamente (implementación contractual). No demuestra hidratación exitosa de cada artefacto físico |
| E-5.4-014 | VERIF | VERIFICACIÓN | `criticality/costs.py` | CriticalityAwareCostContext implementa TreeEditCostContext, sustitución usa text_content SIN .strip() |
| E-5.4-015 | VERIF | VERIFICACIÓN | `regression/mechanism.py` | DoubleProtectionMechanism implementa doble protección: NSS + regla absoluta CRITICAL |
| E-5.4-016 | VERIF | VERIFICACIÓN | `benchmark_service.py` | TopologyBenchmarkService NO tiene partición de datasets, itera sobre todos los documentos |
| E-5.4-017 | VERIF | VERIFICACIÓN | `metrics/__init__.py` | MetricRegistry con 4 métricas por defecto: NodeCount, EntityRecall, SequenceAlignment, Structural |
| E-5.4-018 | **P1** | AUSENCIA DE INFRAESTRUCTURA | PROJECT_TREE + código | Ausencia funcional demostrada de: partición de datasets, provenance de calibration runs, capacidad funcional de análisis estadístico reproducible, protocolo de calibración empírica ejecutable |
| E-5.4-019 | **P1** | AUSENCIA DE CALIBRACIÓN | NADR-18 §5.3 R12 + código | Ningún parámetro calibrado empíricamente. Todos normativos/heurísticos. Validación empírica pendiente |
| E-5.4-020 | **P2** | OBSERVACIÓN | HITO 5.1 | Con 7 documentos, esquema clásico train/validation/holdout no resulta estadísticamente robusto. Requiere política específica de validación |
| E-5.4-021 | **P1** | AUSENCIA DE PROVENANCE | PROJECT_TREE + código | No existe sistema de provenance de calibration runs. Limitado a calibration-run provenance, no a provenance del sistema en general |
| E-5.4-022 | **P2** | OBSERVACIÓN | Inventario .ast.json | Solo 2 de 7 identidades tienen .ast.json legacy. `[Amoretal_2023]_3hojas.pdf` NO tiene .ast.json legacy |
| E-5.4-023 | **P2** | OBSERVACIÓN | Inventario candidates | pymupdf candidates NO tienen meta.json, docling candidates SÍ tienen meta.json. Inconsistencia de metadata entre extractores. Pregunta: ¿meta.json es parte del contrato científico del candidate? |

**Resumen de severidades:** 6 P1, 4 P2, 8 VERIF. Total: 18 evidencias únicas.

---

## 9. GAPS CONSOLIDADOS

| GAP | Sev | Nature | Descripción | Evidencia | Contract | Proven | Fase destino |
|---|---|---|---|---|---|---|---|
| **GAP-5.4-001** | **P1** | INCOMPATIBILIDAD | Manifest de calibration_v1 en formato legacy (DF-19), incompatible con ManifestFingerprintCalculator actual | E-5.4-001 | NADR-16 §5.4, DF-19 | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-002** | **P1** | DISCREPANCIA DE IDENTIDAD / CONSECUENCIA CRIPTOGRÁFICA PENDIENTE DE VERIFICACIÓN | node_ids legacy en calibration_v1 producen identidad criptográfica distinta bajo el algoritmo vigente. La incompatibilidad efectiva con el oracle_hash almacenado debe verificarse mediante recomputación efectiva | E-5.4-004, E-5.4-012 | NADR-16, NADR-17 | SÍ (divergencia), NO (consecuencia efectiva) | **ADR_F17_BIS_05** |
| **GAP-5.4-003** | **P2** | DC / OBSERVACIÓN | Indicio de subdeclaración de traits en calibration_v1. Nombres de archivos sugieren variedad, pero solo "native_pdf" declarado. **Nota:** Indicio, no demostración. Pendiente de curaduría humana | E-5.4-011 | ADR Maestro §6 | NO (indicio) | **ADR_F17_BIS_05 / Curaduría** |
| **GAP-5.4-004** | **P1** | INCOMPATIBILIDAD | .ast.json legacy no directamente compatibles con AST V2. Requieren migración/adaptación estructural o re-extracción, decisión que corresponde al ADR | E-5.4-008 | N/A | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-005** | **P1** | AUSENCIA DE INFRAESTRUCTURA | Ausencia funcional demostrada de: partición de datasets, provenance, capacidad de análisis estadístico reproducible, protocolo de calibración empírica | E-5.4-018, E-5.4-021 | NADR-18, NADR-19 | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-006** | **P1** | AUSENCIA DE CALIBRACIÓN | Ningún parámetro calibrado empíricamente. Todos normativos/heurísticos | E-5.4-019 | NADR-18 §5.3 R12 | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-007** | **P2** | OBSERVACIÓN | Con 7 documentos, esquema clásico train/validation/holdout no resulta estadísticamente robusto. Requiere política específica de validación | E-5.4-020 | ENGINEERING_PRINCIPLES §I | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-008** | **P2** | OBSERVACIÓN | `[Amoretal_2023]_3hojas.pdf` no tiene .ast.json legacy | E-5.4-022 | N/A | SÍ | **ADR_F17_BIS_05** |
| **GAP-5.4-009** | **P2** | OBSERVACIÓN | Inconsistencia de metadata entre extractores/candidates: pymupdf no materializa meta.json mientras docling sí. Pregunta: ¿meta.json es parte del contrato científico del candidate? | E-5.4-023 | N/A | SÍ | **Execution Plan** |

---

## 10. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| H-5.1-C | Cobertura Observada coincide con Cobertura Declarada | **NO DEMOSTRADA** | E-5.4-011: Indicio de subdeclaración basado en nombres de archivos. No se ejecutó inspección visual de contenido. Pendiente de curaduría humana experta |
| H-5.1-D | .ast.json legacy son directamente compatibles con AST actual | **RECHAZADA** | E-5.4-008: Estructura no directamente compatible (`type` vs `node_type`, `content` vs `payload.content`, sin `sequence_id`, `strategy`, `depth`, `parent_node_id`). Requiere migración/adaptación estructural o re-extracción, decisión que corresponde al ADR |
| H-5.1-F | node_id legacy produce identidad criptográfica válida | **NO DEMOSTRADA** | E-5.4-004 + E-5.4-012: Se demuestra que node_id legacy produce una identidad criptográfica distinta bajo el algoritmo vigente. La incompatibilidad efectiva con el oracle_hash almacenado debe verificarse mediante recomputación efectiva |

---

## 11. RESPUESTAS A PREGUNTAS FORENSES (Q1-Q10)

### Q1 — ¿La cobertura real del corpus coincide con la cobertura declarada?

**NO DEMOSTRADO.** Existe indicio de posible subdeclaración de traits basado en nombres de archivos:
- `doc_02_double` → podría sugerir MULTI_COLUMN
- `doc_03_math` → podría sugerir HEAVY_MATHEMATICS
- `doc_04_table` → podría sugerir COMPLEX_TABLES
- `doc_05_graph` → podría sugerir MIXED_CONTENT

Sin embargo, los nombres de archivos son **indicios**, no evidencia suficiente. Este HITO no ejecutó inspección visual de contenido de PDFs. La cobertura real queda como **NO DEMOSTRADA**, pendiente de curaduría humana experta.

**Evidencia:** E-5.4-011

### Q2 — ¿Cada Ground Truth representa efectivamente el contenido estructural del PDF correspondiente?

**PENDIENTE de curaduría humana experta.** Este HITO no ejecuta inspección visual directa de PDFs ni comparación semántica con GTs. Se identifica un indicio de discrepancia de traits, pero la validez semántica/estructural de GTs queda pendiente de curaduría.

### Q3 — ¿Los Ground Truths pueden hidratarse bajo los contratos actuales?

**SÍ — implementación contractual.** La función de hidratación es compatible con los contratos de lifecycle según inspección estática. **Nota epistemológica:** Esto NO equivale a "todos los Ground Truth físicos pueden hidratarse correctamente". La hidratación exitosa de cada artefacto físico queda pendiente de verificación efectiva.

**Evidencia:** E-5.4-013

**Funciones verificadas:**
- `hydrate_ground_truth()`
- `GroundTruthDraft`
- `SealedOracle`
- `GroundTruthLifecycleState`
- `DraftSubState`
- `LifecycleTransitionAuthority`

### Q4 — ¿Los node_id legacy producen una identidad criptográfica válida bajo el algoritmo vigente?

**NO — producen identidad distinta.** `OracleSemanticIdentityCalculator.calculate()` incluye `node_id` en el hash. Los GTs de calibration_v1 tienen node_ids legacy (`"value='p1_b0'"` en lugar de `"p1_b0"`), por lo que producen una identidad criptográfica distinta bajo el algoritmo vigente.

**Sin embargo, la incompatibilidad efectiva con el oracle_hash almacenado debe verificarse mediante recomputación efectiva.** Esto requiere cálculo efectivo y comparación de stored_hash vs recomputed_hash.

**Evidencia:** E-5.4-004, E-5.4-012

**Funciones verificadas:**
- `OracleSemanticIdentityCalculator.calculate()`

### Q5 — ¿Los .ast.json legacy son compatibles con el AST actual?

**NO son directamente compatibles con el contrato AST V2 actual y requieren migración/adaptación estructural o re-extracción, decisión que corresponde al ADR.**

La estructura es diferente:

| Aspecto | .ast.json legacy | AST V2 actual |
|---|---|---|
| Tipo de nodo | `"type": "section"` | `"node_type": "heading"` |
| Contenido | `"content": "..."` | `"payload": {"content": "..."}` |
| Sequence ID | No existe | `"sequence_id": 1` |
| Strategy | No existe | `"strategy": "translate"` |
| Depth | No existe | `"depth": 0` |
| Parent node | No existe | `"parent_node_id": null` |
| Metadata | `"metadata": {}` | Metadata rica (bboxes, pages, confidence, etc.) |

**Evidencia:** E-5.4-008

**Funciones verificadas:**
- `deserialize_ast_json()`
- `read_ast_json()`
- `load_ast_sequence_from_json()`

### Q6 — ¿calibration_v1 puede considerarse científicamente reutilizable bajo los contratos actuales?

**NO — INELIGIBLE bajo el contrato vigente.** Esto NO equivale a "científicamente inválido". Significa que no es elegible como baseline canónica bajo el contrato vigente. Los defectos contractuales/identitarios demostrados son suficientes para esta clasificación.

**Clasificación:** INELIGIBLE — requiere migración significativa para ser elegible.

### Q7 — ¿Qué infraestructura de calibración existe actualmente?

**AUSENCIA FUNCIONAL DEMOSTRADA.** Inventario:

| Componente | Existe | Observación |
|---|:---:|---|
| TopologyBenchmarkService | ✅ | Evalúa documentos, NO tiene partición |
| MetricRegistry | ✅ | 4 métricas por defecto |
| RegressionEvaluationStrategy | ✅ | Estrategia de evaluación |
| DoubleProtectionMechanism | ✅ | Doble protección NSS + CRITICAL |
| CriticalityAwareCostContext | ✅ | CRITICAL=5.0, WARNING=2.0, INFO=1.0 |
| Partición de datasets | ❌ | No existe |
| Provenance de calibration runs | ❌ | No existe |
| Capacidad funcional de análisis estadístico reproducible | ❌ | Ausencia funcional demostrada |
| Protocolo de calibración empírica | ❌ | No existe |

**Evidencia:** E-5.4-018

### Q8 — ¿Qué separación de datasets existe actualmente?

**NINGUNA.** `TopologyBenchmarkService.evaluate_corpus()` itera sobre todos los documentos sin partición. No existe separación train/validation/holdout. Con 7 documentos, un esquema clásico train/validation/holdout **no resulta estadísticamente robusto y requiere una política específica de validación.**

**Evidencia:** E-5.4-016, E-5.4-020

### Q9 — ¿Qué provenance se registra actualmente?

**NINGUNO para calibration runs.** No existe sistema de tracking de calibration runs. Limitado a calibration-run provenance, no a provenance del sistema en general. El proyecto sí tiene conceptos de identidad y trazabilidad de artefactos (manifest_hash, DocumentFingerprint.sha256, oracle_hash, CorpusVersion), pero eso no equivale a experiment provenance.

**Evidencia:** E-5.4-021

### Q10 — ¿Existe riesgo demostrable de leakage, duplicación o sobreajuste del corpus durante la calibración?

**SÍ, riesgo potencial.** HITO 5.1 detectó duplicados:
- G1: 4 copias (84891f98...)
- G2: 2 copias (21b9283a...)

Sin separación de datasets basada en content identity (SHA-256), existe riesgo potencial de leakage. Sin embargo, como no existe infraestructura de calibración, el riesgo es **teórico** en este momento. No se ha observado incidente de contaminación.

**Nota epistemológica:** Duplicados físicos no necesariamente significa leakage experimental. El leakage solo ocurre si esos contenidos terminan distribuidos entre conjuntos o usados de manera que contamine la calibración.

**Evidencia:** HITO 5.1 GAP-5.1-06

---

## 12. CLASIFICACIÓN FINAL (Calibration Readiness)

**Clasificación: NOT READY**

```text
                 ┌─────────────────────────┐
                 │  Scientific Truth       │
                 │  Qualification           │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Calibration Readiness   │
                 └────────────┬────────────┘
                              │
                              ▼
                         NOT READY
                              │
                              ▼
                     GAP / DC / ADR_F17_BIS_05
```

**Tabla de dimensiones de readiness:**

| Dimensión | Estado |
|---|---|
| Physical corpus discovery | COMPLETE |
| GT contractual eligibility | FAIL / PENDING |
| Scientific GT validity | NOT DEMONSTRATED |
| Calibration infrastructure readiness | NOT READY |
| Empirical parameter calibration | NOT PERFORMED |
| Baseline certification | BLOCKED |

**Justificación:**

**DEMOSTRADO:**
1. **calibration_v1 es INELIGIBLE** bajo el contrato actual:
   - Manifest en formato legacy (DF-19) — E-5.4-001 — incompatible con contrato actual
   - node_ids legacy producen identidad criptográfica distinta — E-5.4-004, E-5.4-012 — incompatibilidad efectiva pendiente de recomputación
2. **.ast.json legacy no directamente compatibles** con AST V2 — E-5.4-008 — requieren migración/adaptación o re-extracción
3. **Ausencia funcional de infraestructura de calibración:**
   - No existe partición de datasets — E-5.4-016
   - No existe sistema de provenance — E-5.4-021
   - No existe protocolo de calibración empírica — E-5.4-018
4. **Parámetros NO calibrados empíricamente:**
   - Pesos de criticidad: normativos/heurísticos — E-5.4-019
   - Thresholds de NSS: heurísticos — E-5.4-019

**NO DEMOSTRADO (pendiente de curaduría humana):**
- Cobertura real de traits del corpus
- Validez semántica/estructural de GTs
- Migración vs re-extracción de .ast.json legacy
- Protocolo de calibración
- Estrategia de validación de datasets
- Requisito de corpus adicional
- Normalización canónica de texto

**Nota epistemológica:** NOT READY para calibración NO significa que el corpus sea científicamente inválido. Significa que la infraestructura actual no permite calibración científica reproducible. La clasificación NOT READY es robusta frente a la incertidumbre epistemológica de traits.

**Pregunta central:** ¿Estamos en condiciones de calibrar científicamente la Baseline sin contaminar el experimento?

**Respuesta:** NO. La infraestructura actual no permite calibración científica reproducible.

---

## 13. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia | Fase destino |
|---|---|---|---|
| **DC-5.4-001** | Política de curaduría de Ground Truths | E-5.4-004, E-5.4-011, E-5.4-012 | **ADR_F17_BIS_05** |
| **DC-5.4-002** | Política de migración de .ast.json legacy | E-5.4-008 | **ADR_F17_BIS_05** |
| **DC-5.4-003** | Política de migración de manifest legacy | E-5.4-001 | **ADR_F17_BIS_05** |
| **DC-5.4-004** | Adquisición de corpus adicional | E-5.4-020, DC-5.1-03 | **ADR_F17_BIS_05** |
| **DC-5.4-005** | Implementación de infraestructura de calibración | E-5.4-018, E-5.4-021 | **ADR_F17_BIS_05** |
| **DC-5.4-006** | Protocolo de calibración empírica de parámetros | E-5.4-019 | **ADR_F17_BIS_05** |
| **DC-5.4-007** | Política de partición de datasets | E-5.4-016, E-5.4-020 | **ADR_F17_BIS_05** |

**Nota sobre DC-5.4-006:** El protocolo de calibración empírica debe comenzar definiendo el experimento (qué variable calibrar, qué ground truth observable, qué función objetivo, qué parámetros, qué restricciones, qué unidad de evaluación, qué independencia, qué criterio de aceptación). Solo después: grid search, LOOCV, bootstrap, Bayesian optimization, etc. El ADR no debería comenzar eligiendo algoritmo de búsqueda.

---

## 14. VERIFICACIÓN DE CUMPLIMIENTO NADR-18/NADR-19

| Regla | Estado | Justificación |
|---|---|---|
| NADR-18 §5.3 R11 (CriticalityAwareCostContext implementa TreeEditCostContext) | ✅ Cumple | CriticalityAwareCostContext implementa TreeEditCostContext (E-5.4-014) |
| NADR-18 §5.3 R12 — Condición A (Pesos deterministas) | ✅ Cumple | Pesos CRITICAL=5.0, WARNING=2.0, INFO=1.0 son deterministas |
| NADR-18 §5.3 R12 — Condición B (Validación empírica realizada) | ⚠️ PENDING EMPIRICAL VALIDATION | NADR-18 §5.3 R12 establece "Propuesta inicial sujeta a validación empírica". La validación empírica NO se ha realizado. Esto puede interpretarse como "el diseño permite/admite una futura validación" o como "la implementación actual incumple R12". La interpretación depende de si NADR-18 formula explícitamente la validación como precondición obligatoria para considerar el modelo conforme |
| NADR-18 §5.3 R13 (Pesos configurables) | ✅ Cumple | CriticalityAwareCostContext acepta weights por inyección |
| NADR-18 §5.3 R14 (CRITICAL > WARNING > INFO) | ✅ Cumple | 5.0 > 2.0 > 1.0 |
| NADR-19 §5.2 R8 (NSS ponderado) | ✅ Cumple | DoubleProtectionMechanism implementa Mecanismo 1 (E-5.4-015) |
| NADR-19 §5.2 R9 (Regla absoluta CRITICAL) | ✅ Cumple | DoubleProtectionMechanism implementa Mecanismo 2 (E-5.4-015) |
| NADR-19 §5.2 R10 (Precedencia Mecanismo 2) | ✅ Cumple | Mecanismo 2 tiene precedencia sobre Mecanismo 1 (E-5.4-015) |
| NADR-19 §5.2 R11 (Complementariedad) | ✅ Cumple | Veredicto final = peor resultado (E-5.4-015) |
| NADR-19 §5.5 R20 (Reutiliza build_extraction_pipeline) | N/A | **Justificación:** R20 es una regla de composición del benchmark que exige reutilizar el pipeline de producción. Este HITO audita infraestructura de calibración, no la composición del pipeline de extracción. La verificación de R20 pertenece al HITO que audite la composición del benchmark (HITO 5.3 lo verificó para StructuralTopologyMetric) |

---

## 15. APÉNDICE — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia |
|---|---|---|---|
| calibration_v1 INELIGIBLE | No es elegible para sealing/baseline bajo contrato actual | Alto | E-5.4-001, E-5.4-004, E-5.4-012 |
| .ast.json legacy requieren migración/adaptación o re-extracción | No directamente compatibles con AST V2 | Alto | E-5.4-008 |
| Infraestructura de calibración insuficiente | No permite calibración científica reproducible | Alto | E-5.4-018, E-5.4-021 |
| Parámetros no calibrados | Pesos y thresholds son heurísticos/normativos, no empíricos | Alto | E-5.4-019 |
| Corpus insuficiente para partición clásica | 7 documentos no resultan estadísticamente robustos para train/validation/holdout | Medio | E-5.4-020 |
| Leakage potencial | Sin separación de datasets basada en content identity. Riesgo teórico, no incidente observado | Medio | HITO 5.1 GAP-5.1-06 |
| Thresholds no transferibles | ZhangShasha vs APTED requieren calibración separada | Medio | HITO 5.3 Clasificación C |
| Divergencia de normalización de texto | CriticalityAwareCostContext usa text_content SIN .strip(), ASTFingerprintPolicy usa text_content CON .strip(). Puede causar divergencias en benchmarks | Medio | HITO 5.3 E-5.3-002 |
| Inconsistencia de metadata entre extractores | pymupdf candidates sin meta.json, docling con meta.json | Bajo | E-5.4-023 |

---

## 16. APÉNDICE — OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-5.4-001 | benchmark_v1 está vacío (documents: []). Compatible con contrato vigente | Bajo | OPEN |
| OBS-5.4-002 | `[Amoretal_2023]_3hojas.pdf` no tiene .ast.json legacy | Bajo | OPEN |
| OBS-5.4-003 | Inconsistencia en candidates: pymupdf sin meta.json, docling con meta.json | Bajo | OPEN |
| OBS-5.4-004 | El fragmento de código en mechanism.py presentado en la evidencia parece incompleto. La verificación estática del archivo fuente (pyright) no reproduce el defecto. | Bajo | CLOSED / NO REPRODUCED |
| OBS-5.4-005 | CriticalityAwareCostContext usa text_content SIN .strip() para sustitución | Medio | OPEN |
| OBS-5.4-006 | Los estados DRAFT/AUDITED/VALIDATED no tienen persistencia física independiente. Esto es una característica de diseño del contrato de lifecycle, no un defecto. El contrato de lifecycle sólo requiere persistencia del estado sealed. | Bajo | OPEN (característica de diseño) |

---

## 17. APÉNDICE — PREGUNTAS PARA ADR_F17_BIS_05

1. **DC-5.4-001:** ¿Cuál es la política de curaduría de Ground Truths? ¿Se requiere curaduría humana experta para validar contenido semántico?

2. **DC-5.4-002:** ¿Cuál es la política de migración de .ast.json legacy? ¿Migración programática o re-extracción completa?

3. **DC-5.4-003:** ¿Cuál es la política de migración de manifest legacy (DF-19)? ¿Migración automática o regeneración?

4. **DC-5.4-004:** ¿Se requiere adquisición de corpus adicional? ¿Cuántos documentos se necesitan para partición válida?

5. **DC-5.4-005:** ¿Cuál es el plan de implementación de infraestructura de calibración? ¿Módulo separado, partición de datasets, provenance, estadística?

6. **DC-5.4-006:** ¿Cuál es el protocolo de calibración empírica de parámetros? **Nota:** El protocolo debe comenzar definiendo el experimento (qué variable calibrar, qué ground truth observable, qué función objetivo, qué parámetros, qué restricciones, qué unidad de evaluación, qué independencia, qué criterio de aceptación). Solo después: grid search, LOOCV, bootstrap, Bayesian optimization, etc.

7. **DC-5.4-007:** ¿Cuál es la política de partición de datasets? ¿Leave-one-out (7 folds) con corpus actual? ¿Train/validation/holdout con corpus ampliado?

8. **Thresholds no transferibles (HITO 5.3):** Dado que ZhangShasha y APTED son Comparable but Non-Equivalent, ¿se calibra para ZhangShasha (canónico) o para ambos motores por separado?

9. **Traits incompletos:** ¿Se requiere inspección manual de PDFs para completar traits, o se acepta "native_pdf" como trait único?

10. **Validación empírica de pesos de criticidad (NADR-18 §5.3 R12 Condición B):** ¿Cuándo se realizará la validación empírica pendiente?

11. **Divergencia de .strip() (HITO 5.3 E-5.3-002):** ¿Se debe estandarizar la normalización de texto entre CriticalityAwareCostContext (sin .strip()) y ASTFingerprintPolicy (con .strip())?

---

## 18. REGLA DE ORO

> **No se calibra sobre los mismos datos con los que se evalúa. Calibration ≠ Tuning. Un script no es un protocolo científico. Un número elegido heurísticamente no es un número calibrado.**

> **No se editan Ground Truths en un HITO forense. Primero: AUDIT → EVIDENCE → CLASSIFICATION. Después: ADR → PLAN → CURATION.**

> **No se declara "científicamente calibrado" por tener un script. La calibración requiere protocolo previamente definido, datos independientes, y función objetivo explícita.**

> **Un indicio no es evidencia. Un nombre de archivo que sugiere un trait no demuestra la presencia de ese trait. La cobertura real requiere inspección de contenido.**

> **Una consecuencia lógica no demostrada efectivamente no equivale a una demostración. La incompatibilidad de node_id legacy con oracle_hash debe verificarse mediante recomputación efectiva.**

---

## 19. CIERRE DEL HITO

**Estado del HITO:** FROZEN v1.0.3

**Condición de cierre cumplida:**
- [x] Metadata completa y consistente
- [x] Changelog actualizado (6 versiones)
- [x] Límite epistemológico declarado
- [x] Nota de desviación estructural justificada
- [x] Todas las superficies técnicas incluidas en el alcance forense fueron inspeccionadas; la inspección semántica/visual humana de PDFs queda fuera del alcance ejecutado
- [x] Fuentes de evidencia listadas (código directo + artefactos reales)
- [x] Nota de herencia completa (incluye conexión con HITO 5.3)
- [x] TRACK A completado (GT Forensic Qualification)
- [x] TRACK B completado (Calibration Infrastructure Audit)
- [x] Matriz Observed/Required/Decision completada (10 items)
- [x] Registro de Evidencia Forense completado con inventario canónico explícito (18 evidencias: 6 P1, 4 P2, 8 VERIF)
- [x] Gaps Consolidados completados (9 gaps con columna Nature)
- [x] Estado de Hipótesis completado (H-5.1-C: NO DEMOSTRADA, H-5.1-D: RECHAZADA, H-5.1-F: NO DEMOSTRADA)
- [x] Respuestas a Preguntas Forenses completadas (Q1-Q10)
- [x] Clasificación Final completada: **NOT READY**
- [x] Tabla de dimensiones de readiness introducida
- [x] Matriz de Trazabilidad DC completada (7 DCs)
- [x] Verificación de Cumplimiento NADR-18/NADR-19 completada (R12-B: PENDING EMPIRICAL VALIDATION)
- [x] Apéndices completados (Riesgos, Observaciones, Preguntas ADR)
- [x] Regla de Oro incluida (con adiciones epistemológicas)
- [x] Zero Partial Sealing reclasificado a PASS / NOT YET EXERCISED
- [x] GAP-5.4-002 reformulado como DISCREPANCIA DE IDENTIDAD / CONSECUENCIA CRIPTOGRÁFICA PENDIENTE DE VERIFICACIÓN
- [x] Versión única v1.0.3 en todo el documento
- [x] Cadena de gobernanza verificada
- [x] Siguiente paso recomendado declarado

**Verificación de cadena de gobernanza:**
ADR_F17_BIS_MASTER → NADRs 12-19 → HITO 5.0 → HITO 5.1 → HITO 5.2 → HITO 5.3 → HITO 5.4 (este) → Gaps y DCs → ADR_F17_BIS_05 → Execution Plan.

**Siguiente paso recomendado:**
- **SYNTHESIS**: ADR_F17_BIS_05 con insumos de HITO 5.0, 5.1, 5.2, 5.3, 5.4.
- Después: NADRs de Fase 5 → Execution Plan → Implementation → Validation → Certification.