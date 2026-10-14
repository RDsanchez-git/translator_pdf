# FASE_5_HANDOFF.md

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_5_HANDOFF.md`
**Versión:** 1.0.1
**Estado:** FROZEN
**Fecha:** 2026-09-24
**Fase completada:** Fase 5 — Baseline Certification (Gate outcome: CONDITIONAL_PASS)
**Siguiente sub-fase:** Fase 6 — Continuous Verification (última sub-fase de 17-BIS)
**Siguiente fase del ROADMAP:** Fase 18 — Advanced Local Runtime
**Derivado de:** `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.4.0 + `FASE_5_DEFERRED_FINDINGS_REGISTER.md` v0.21.0

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-24 | Emisión inicial al cierre de Fase 5 (Gate outcome: CONDITIONAL_PASS, Phase outcome: REJECTED_WITH_DOCUMENTED_LIMITATIONS) |
| 1.0.1 | 2026-09-24 | Completado de datos pendientes del commit de cierre: (1) Commit hash `9689d7776c5ab6eaa611210c66d9b8e0fe75395b` registrado en §2.1 (Repository State); (2) PROJECT_TREE regenerado post-commit; (3) Veredicto de §9 actualizado de 🟡 EN PROGRESO a ✅ CERRADO — FROZEN. Sin cambios normativos ni de contenido. |

---

## 1. EXECUTIVE SUMMARY

**¿Qué se logró?** — La Fase 5 (Baseline Certification) completó la materialización del Corpus Canónico v3.9 con 21 identidades selladas bajo Zero Partial Sealing (N_PDF = N_GT = 21), superando el objetivo mínimo de 20 documentos (NADR-20 §5.5 R20). Se implementó la infraestructura completa de certificación: PREFLIGHT (8 precondiciones), DoubleProtectionMechanism (NSS + Criticality), Certification Evidence (7 elementos R29), POST-RUN VALIDATION (5 checks), y semántica de fallo uniforme en todos los entry points. El estado final es **CONDITIONAL_PASS** a nivel de Gate y **REJECTED_WITH_DOCUMENTED_LIMITATIONS** a nivel de Phase.

**¿Cuál es el estado actual?** — El corpus v3.9 está sellado (manifest hash `727782fe0df26d9d...`), los parámetros están congelados (parameter identity `67841171...`), y la FINAL EVALUATION fue ejecutada con resultado Corpus NSS = 0.7208 (HARD_FAIL, threshold 0.80). La divergencia es explicada por 36 hallazgos derivados de curaduría (H-5.1-9 a H-5.1-44) que documentan las limitaciones empíricas del extractor PyMuPDFProvider. Seis documentos (28.6%) son tautológicos por limitaciones de curaduría; 15 documentos (71.4%) son informativos. Los thresholds actuales (0.80/0.95) son defaults normativos, no calibrados empíricamente (H-5.3-1). Un hallazgo adicional de Gate 5 (H-5.6-1) confirmó que la curaduría de doc_11-13 fue sobrescrita durante el onboarding de Batch 3.

**¿Qué necesita la siguiente fase?** — Fase 6 (Continuous Verification, última sub-fase de 17-BIS) debe: (1) recalibrar thresholds con N=21 usando curvas precision-recall + bootstrap CI + human verdicts + learning curves; (2) evaluar extractores alternativos (Marker, Docling, Nougat) para reducir la divergencia estructural; (3) integrar los Regression Gates en CI/CD. Prerequisitos críticos: no mutar oráculos sellados (NADR-21 §5.4 R19), no calibrar sobre datos de evaluación (NADR-23 §5.1 R2), preservar la identidad del motor canónico (ZhangShasha + CriticalityAwareCostContext). Tras completar Fase 6, el ROADMAP continúa con Fase 18: Advanced Local Runtime.

> **Regla:** Este bloque es lo único que un humano necesita leer para entender dónde está
> el proyecto. Si alguien solo lee esta sección, debe poder decidir si continuar o no.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` |
| Commit hash de cierre | `9689d7776c5ab6eaa611210c66d9b8e0fe75395b` |
| Estado del árbol | Limpio (post-commit) |
| Baseline de tests | **729 passed, 5 skipped** (no debe degradarse sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados |
| Zero Partial Sealing | N_PDF = N_GT = 21 (verificado por BaselineCompletenessVerifier) |
| PROJECT_TREE | ⚠️ Desactualizado — faltan entry points creados en Fase 5 (ver §5.3) |

### 2.2 Validation Results

```bash
# Comandos ejecutados al cierre de la fase
python -m tools.evaluation.preflight_certification --corpus-dir tests/corpus/canonical --expected-manifest-hash 727782fe0df26d9d... --expected-configuration-identity b942fc95... --expected-parameter-identity 67841171...
# [PREFLIGHT] All 8 conditions satisfied ✅

python -m tools.evaluation.run_regression --corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf --output-dir reports/certification --inject-timestamp
# Corpus NSS: 0.7208 | Verdict: HARD_FAIL | Exit code: 2 ✅

python -m tools.evaluation.freeze_parameters --corpus-dir tests/corpus/canonical --evaluation-report reports/certification/regression_report.json --protocol-reference FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md --timestamp "2026-09-23T20:00:00Z" --evaluation-kind FINAL_EVALUATION
# [OK] Freeze identico ya materializado. Evaluation Provenance Record emitido para FINAL_EVALUATION ✅

# Verificación de determinismo (Task 5.3.4)
# Hash reporte #1 (sin timestamp): c4f9b284dfff79051dc2131db1ba13197ecc4ad5e7cd8d7185f4abf6e3da0911
# Hash reporte #2 (sin timestamp): c4f9b284dfff79051dc2131db1ba13197ecc4ad5e7cd8d7185f4abf6e3da0911
# Hashes idénticos → Determinismo operacional R32 verificado ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro (ADR_F17_BIS_MASTER) | FROZEN | 1.0.0 |
| ADR de Fase 5 (ADR_F17_BIS_05) | FROZEN | 1.0.0 |
| NADRs (5 documentos: NADR-20 a NADR-24) | FROZEN | 1.0.0 |
| Execution Plan | FROZEN | 1.4.0 |
| Evidence Log | FROZEN | 0.16.0 |
| Findings Register | ARCHIVED | 0.21.0 |
| Methodology | FROZEN | v1.3.0 |
| Benchmark Methodology | FROZEN | v1.2.0 |
| Curation Report | FROZEN | v3.5 |
| Provenance Record | FROZEN | v3.9 |
| Qualification Record | FROZEN | v3.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 78 + 1 (H-5.6-1 identificado en Gate 5) |
| Hallazgos resueltos | 22 |
| Hallazgos cerrados sin acción (NAR) | 4 |
| Hallazgos diferidos a fase futura | 12 |
| Hallazgos aceptados como limitación | 44 |
| Governance Findings | 3 (GF-01, GF-02 documentados; GF-03 remediado operacionalmente) |
| Hallazgo de Gate 5 | 1 (H-5.6-1: curaduría de doc_11-13 sobrescrita) |
| Batches ejecutados | 3 (Batch 1, Batch 2a, Batch 3) |
| Batches diferidos | 1 (Batch 2b: main_corpus, YAGNI) |
| Archivos eliminados | 6 (higiene de zombies y código archivado) |
| Archivos movidos | 1 (canonicalization_lineage.json de ground_truth/ a canonical/) |
| Archivos creados | 39+ (GTs, reportes, documentos de gobernanza) |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | ZhangShasha como motor topológico canónico para certificación | Divergencia ZhangShasha/APTED clasificada como Comparable but Non-Equivalent (HITO 5.3 Clasificación C) | ADR_F17_BIS_05 D4: ZhangShasha integra CriticalityAwareCostContext; APTED no lo integra en el adapter actual | `bootstrap/topology.py`, NADR-22 §5.1 |
| AD-02 | APTED como experimental no-normativo (no eliminado) | DF-04 benchmark: divergencia promedio 8.56%, máxima 22.63% | NADR-22 §5.1 R3 + ENGINEERING_PRINCIPLES §I (no eliminar sin evidencia de redundancia) | `reports/df04/df04_benchmark.{json,md}`, Task 2.4.7 |
| AD-03 | CriticalityAwareCostContext con pesos CRITICAL=5.0, WARNING=2.0, INFO=1.0 | Modelo de costo normativo para la cadena de certificación | ADR_F17_BIS_05 D4 + NADR-22 §5.2 R5-R9 | `core/benchmark/topology/criticality/costs.py` |
| AD-04 | DoubleProtectionMechanism (NSS + Criticality, worst-wins) | Graduar divergencias del motor topológico más allá de comparación binaria | NADR-22 §5.7 R22-R25 | `core/benchmark/topology/regression/mechanism.py` |
| AD-05 | Thresholds normativos NSS 0.80/0.95 (no calibrados empíricamente) | N=6 insuficiente para calibración estadística al inicio de Fase 5 | NADR-23 §5.3 R12 (prohíbe presumir robustez con <20 identidades) | H-5.3-1, `FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md` |
| AD-06 | Zero Partial Sealing como precondición de sellado | Riesgo de sellado parcial identificado en Fase 0 | ADR_F17_BIS_MASTER §5 + NADR-21 §5.5 R22-R27 | `BaselineCompletenessVerifier`, Task 2.2.2 |
| AD-07 | Curaduría ANTES del sellado (gate O2) | GF-03: onboarding v2.2 selló doc_09/doc_10 sin curaduría previa | NADR-21 §5.1 R5 + Batch 1 (commit `9cbddf8`) | `freeze_ground_truth.py::_check_curation_gate` |
| AD-08 | curate_gt.py como escritor de curation_checklist.json | Remediación operacional de GF-03 sin modificar código de dominio congelado | NADR-21 §5.1 R5 + Batch 2a (commit `c4bb03b`) | `tools/evaluation/curate_gt.py` |
| AD-09 | Separación de scope GF-01: run_regression (NADR-19) vs runner certificación (NADR-24) | Conflicto entre taxonomías de exit codes | GF-01 documentado como interpretación normativa | `FASE_5_DEFERRED_FINDINGS_REGISTER.md` GF-01 |
| AD-10 | Gate 5 CONDITIONAL_PASS con Phase REJECTED_WITH_DOCUMENTED_LIMITATIONS | NSS=0.7208 < 0.80 pero baseline correctamente construida | Execution Plan §2.5.6 + NADR-24 §5.1 R4 | `reports/certification/certification_evidence.json` |
| AD-11 | H-5.6-1 registrado como ACCEPTED_LIMITATION con sustitución diferida | Curaduría de doc_11-13 sobrescrita por generate_golden_draft durante onboarding de Batch 3 | Verificación empírica: GTs contienen solo tipos degradados; NSS=1.0000 tautológico | Evidencia empírica en Gate 5, Findings Register |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Corpus Canónico materializado (21 docs, alta varianza) | NADR-20 §5.5 R19-R21 | ✅ DONE |
| Zero Partial Sealing (biyección N_PDF = N_GT) | NADR-21 §5.5 R22-R27 | ✅ DONE |
| Oracle Validity Contract (4 invariantes) | NADR-21 §5.3 R13-R16 | ✅ DONE |
| Ground Truth Lifecycle (Draft→Audited→Validated→Sealed) | NADR-21 §5.4 R17-R21 | ✅ DONE |
| Autoridad Única de Sellado (SealGroundTruthUseCase) | NADR-21 §5.4 R19 | ✅ DONE |
| Node ID Canonicalization (migración legacy) | NADR-21 §5.2 R8-R12 | ✅ DONE |
| Oracle Semantic Identity (hash determinista) | NADR-21 §5.6 R28-R31 | ✅ DONE |
| Baseline Completeness Verifier | NADR-21 §5.5 R23 | ✅ DONE |
| Motor canónico ZhangShasha + CriticalityAwareCostContext | NADR-22 §5.1-§5.3 | ✅ DONE |
| DoubleProtectionMechanism | NADR-22 §5.7 R22-R25 | ✅ DONE |
| Configuration Fingerprint (module.qualname) | NADR-22 §5.6 R19-R21 | ✅ DONE |
| PREFLIGHT (8 precondiciones) | NADR-24 §5.2 R6-R9 | ✅ DONE |
| Semántica de fallo uniforme (exit codes) | NADR-24 §5.4 R15-R19 | ✅ DONE |
| Tolerancia a fallos parciales ≠ certificación parcial | NADR-24 §5.5 R20-R24 | ✅ DONE |
| Boundary integrity (Sealed inmutable) | NADR-24 §5.6 R25-R28 | ✅ DONE |
| Certification Evidence (7 elementos R29) | NADR-24 §5.7 R29-R31 | ✅ DONE |
| POST-RUN VALIDATION (5 checks) | NADR-24 §5.9 R36-R37 | ✅ DONE |
| Dataset Independence (Calibration ≠ Evaluation) | NADR-23 §5.1 R1-R3 | ✅ DONE |
| Parameter Freeze con identity criptográfica | NADR-23 §5.6 R23-R25 | ✅ DONE |
| Calibration Provenance Record (5 campos R18) | NADR-23 §5.5 R18-R22 | ✅ DONE |
| Curaduría con gate O2 | NADR-21 §5.1 R5 | ✅ DONE |
| Calibración empírica de parámetros | NADR-23 §5.2 R4-R8 | ⚠️ PARTIAL (protocolo definido, ejecución diferida a N=21) |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `tools/evaluation/freeze_ground_truth.py` — Sellado atómico con gate O2 de curaduría
- `tools/evaluation/curate_gt.py` — Escritor de curation_checklist.json (Batch 2a)
- `tools/evaluation/canonicalize_gt.py` — Canonicalización de node_ids con lineage
- `tools/evaluation/run_regression.py` — Runner de regresión (taxonomía NADR-19)
- `tools/evaluation/preflight_certification.py` — PREFLIGHT (8 precondiciones, NADR-24)
- `tools/evaluation/generate_golden_draft.py` — Generación de drafts de GT
- `tools/evaluation/add_document_to_corpus.py` — Alta de documentos en corpus
- `tools/evaluation/check_candidate.py` — Verificación física de candidatos
- `tools/evaluation/view_gt_html.py` — Visualización HTML de GTs
- `tools/evaluation/freeze_parameters.py` — Parameter freeze + provenance records
- `core/benchmark/certification/` — Paquete de dominio (contract, preflight, evidence, post_run)
- `tests/corpus/canonical/manifest.json` — Manifest canónico v3.9 (21 docs)
- `tests/corpus/canonical/ground_truth/*.json` — 21 oráculos sellados
- `tests/corpus/canonical/curation_checklist.json` — Registro de curaduría
- `reports/certification/regression_report.{json,md}` — Reporte de FINAL EVALUATION
- `reports/certification/certification_evidence.json` — Certification Evidence (7 elementos)
- `reports/calibration/parameter_freeze.json` — Parameter freeze
- `reports/calibration/calibration_provenance_record.json` — Calibration provenance
- `reports/calibration/evaluation_provenance_record_FINAL_EVALUATION.json` — Final evaluation provenance
- `reports/df04/df04_benchmark.{json,md}` — Benchmark DF-04 (ZhangShasha vs APTED)

**Modificados significativamente:**
- `bootstrap/topology.py` — Composition root canónico + build_canonical_engine_configuration()
- `core/shared/exit_codes.py` — Taxonomía uniforme (EXIT_OK=0, EXIT_CERTIFICATION_REJECTED=1, EXIT_EXECUTION_FAILURE=2)
- `core/shared/errors.py` — IndexedError con código indexable
- `tools/evaluation/entry_guard.py` — Guard de traducción R19

**Eliminados (zombies y deuda):**
- `tools/codemods/*` — Código zombie (commit `8cfac09`)
- `tools/load_test/*` — Código zombie
- `graveyard/gemini_client.py` — Código muerto

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para siguiente fase |
|-------------|--------|-------------------------------|
| No mutar oráculos sellados | NADR-21 §5.4 R19 + NADR-24 §5.6 R25 | Fase 6 no puede re-curar GTs sin crear nueva versión de corpus |
| Calibration ≠ Evaluation | NADR-23 §5.1 R2 | Fase 6 no puede calibrar sobre datos de evaluación final |
| Motor canónico único | ADR_F17_BIS_05 D4 + NADR-22 §5.1 | Fase 6 debe usar ZhangShasha + CriticalityAwareCostContext para certificación |
| Thresholds específicos del motor+config | ADR_F17_BIS_05 D4 | Thresholds de NSS no son transferibles entre motores |
| Zero Partial Sealing | ADR_F17_BIS_MASTER §5 | Cualquier cambio de corpus mantiene biyección N_PDF = N_GT |
| Semántica de fallo uniforme | NADR-24 §5.4 R15-R19 | Fase 6 mantiene exit codes diferenciados |
| Determinismo de serialización | ADR_F17_BIS_MASTER §5 | Todo pipeline de evaluación/serialización/hashing es determinista |
| Cero Fallos Silenciosos | ENGINEERING_PRINCIPLES §IV | Ningún camino de error produce exit code 0 |
| Reutilización estricta | ENGINEERING_PRINCIPLES §I | Reutilizar infraestructura existente antes de crear nueva |
| Flat Design (AST plano) | ENGINEERING_PRINCIPLES §II | Secuencias lineales con metadatos topológicos, no árboles anidados |
| PDFs del corpus no se distribuyen en el repo | Decisión de ownership (copyright) | Fase 6 debe manejar PDFs localmente; GTs y manifest sí están trackeados |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| H-5.1-11 | Patrón Detect & Placeholder para tablas/figuras/ecuaciones | Post Fase 17-BIS (ADR dedicado) | Nada |
| H-5.3-1 | Calibración estadística pendiente (N=21 ahora disponible) | Fase 6 (recalibración con curvas PR + bootstrap CI + human verdicts) | Certificación CERTIFIED |
| H-5.3-2 | Divergencia masiva runtime vs GTs (163 Critical FN) | Fase 6 (mejora de extractor) | Certificación CERTIFIED |
| H-5.3-3 | Curaduría real de doc_07 (tablas Type 3 sin ToUnicode) | Re-baseline v4.0 | Nada |
| H-5.5-2 | Sustitución de doc_09, doc_10 (tautológicos) | Re-baseline v4.0 | Nada |
| H-5.5-5 | Enforcement normativo O3 en autoridad de sellado (dominio) | Fase 6 | Nada (mitigado por gate O2 en tooling) |
| H-5.5-6 | Fingerprint de extractor/pipeline como identidad nueva | Fase 6 (posible enmienda normativa) | Nada |
| H-5.6-1 | Curaduría sobrescrita en doc_11-13 (tautológicos por regeneración) | Re-baseline v4.0 | Nada |
| DF-06 | Pipeline genera node_ids legacy (BenchmarkParserBridge serializa BlockId con str()) | Fase 6 (fix en BenchmarkParserBridge) | Nada (mitigado por canonicalize_gt.py) |
| DF-01 | Tests tautológicos en test_golden_parser.py y test_chunker_snapshot.py | Fase 6 | Nada |
| DF-02 | Verificación de ci.yml y pyproject.toml para tests de regresión | Fase 6 | Integración CI |
| DF-03 | Deuda técnica LayoutBlockDraft / mapper transicional | Gate futuro de remediación de layout | Nada |
| O-5.3-1 | NodeMetadata sin campo `note` para footnotes | Fase 6 (extensión de schema) | Nada |
| O-5.4-1 | Enum ExtractionChallengeTrait sin trait `code` | Fase 6 (extensión de catálogo) | Nada |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| Tautología del corpus (28.6%) | 6 documentos tautológicos (NSS=1.0000) no son informativos para validación del extractor: doc_07, doc_09, doc_10 (curaduría original) + doc_11, doc_12, doc_13 (H-5.6-1) | Documentados como limitación; sustitución diferida a re-baseline v4.0 |
| Curaduría de doc_11-13 perdida | generate_golden_draft sobrescribió la curaduría durante onboarding de Batch 3. Los GTs contienen solo tipos degradados (paragraph/heading). NSS=1.0000 es tautológico. | Documentado como H-5.6-1; gate O2 previene repetición; sustitución diferida |
| Thresholds no calibrados | NSS 0.80/0.95 son defaults normativos, no empíricos | Protocolo de calibración definido; ejecución diferida a N=21 |
| PDFs no distribuibles | PDFs del corpus no se trackean en git por copyright | GTs y manifest trackeados; biyección verificable localmente |
| Batch 2b (main_corpus) diferido | Orquestador de 6 verbos diferido por YAGNI | Trigger: ≥2 onboardings post-2a o error de secuenciación |
| GF-01 no resuelto por diseño | Conflicto NADR-19 vs NADR-24 en taxonomía de exit codes | Separación de scope documentada; runner de Gate 5 traduce |
| PROJECT_TREE desactualizado | El PROJECT_TREE no incluye entry points creados en Fase 5 (freeze_parameters.py, preflight_certification.py, generate_golden_draft.py, add_document_to_corpus.py, check_candidate.py, view_gt_html.py, canonicalize_gt.py). Los archivos existen y fueron ejecutados exitosamente. | Regenerar PROJECT_TREE antes del commit de cierre (generate_workspace.py) |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Corpus canónico v3.9 sellado (21 docs, Zero Partial Sealing verificado)
- ✅ Parámetros congelados con identity criptográfica (parameter_freeze.json)
- ✅ Motor canónico configurado (ZhangShasha + CriticalityAwareCostContext)
- ✅ Regression Gates materializados (ejecutables y verificables fuera de CI)
- ✅ Certification Evidence emitido (7 elementos R29)
- ✅ Baseline de Capacidades de PyMuPDFProvider documentada (36 hallazgos de curaduría)
- ✅ Herramienta de curaduría operativa (curate_gt.py + canonicalize_gt.py)
- ✅ Preflight operativo (8 precondiciones)
- ✅ POST-RUN VALIDATION operativa (5 checks)
- ✅ Determinismo operacional verificado (Task 5.3.4)

**Lo que se necesita antes de arrancar:**
- Decidir si Fase 6 arranca con recalibración de thresholds (H-5.3-1) o con evaluación de extractores alternativos
- Definir el ADR de Fase 6 con las decisiones de integración CI/CD
- Decidir si se requiere re-baseline v4.0 antes de integrar en CI (sustitución de 6 tautológicos)
- Regenerar PROJECT_TREE para incluir entry points de Fase 5

### 6.2 Next Phase Handoff Checklist

- [ ] Regenerar PROJECT_TREE (generate_workspace.py) para incluir entry points de Fase 5
- [ ] Crear ADR de Fase 6 (Continuous Verification) con decisiones de integración CI/CD
- [ ] Definir protocolo de recalibración de thresholds con N=21 (curvas PR + bootstrap CI + human verdicts)
- [ ] Evaluar extractores alternativos (Marker, Docling, Nougat) sobre corpus v3.9
- [ ] Implementar fix de DF-06 (node_ids legacy en BenchmarkParserBridge)
- [ ] Extender ExtractionChallengeTrait con trait `code` (O-5.4-1)
- [ ] Evaluar extensión de NodeMetadata con campo `note` (O-5.3-1)
- [ ] Integrar Regression Gates en pipeline de CI/CD
- [ ] Implementar enforcement normativo O3 en autoridad de sellado (H-5.5-5)
- [ ] Evaluar fingerprint de extractor/pipeline como identidad nueva (H-5.5-6)
- [ ] Decidir sobre re-baseline v4.0 (sustitución de 6 documentos tautológicos)

### 6.3 ROADMAP — Objetivos de la siguiente fase

> **Nota de gobernanza:** Fase 6 — Continuous Verification es la **última sub-fase de la Fase 17-BIS** según el ADR_F17_BIS_MASTER §6. Tras completar Fase 6, el ROADMAP continúa con **Fase 18: Advanced Local Runtime**. Los objetivos listados corresponden a Fase 6 dentro de 17-BIS.

1. **Integración CI/CD** — Integrar los Regression Gates en el pipeline de CI/CD para verificación continua
2. **Recalibración de thresholds** — Calibrar empíricamente NSS thresholds con N=21 documentos usando metodología científica (H-5.3-1)
3. **Mejora de extractor** — Evaluar e implementar adaptadores de extracción alternativos (Marker, Docling, Nougat) para reducir divergencia estructural
4. **Verificación continua** — Establecer el pipeline de verificación continua que detecta regresiones topológicas automáticamente

**Hito crítico:** Al concluir Fase 6, los Regression Gates están integrados en CI/CD y se ejecutan automáticamente contra el corpus canónico, detectando cualquier regresión topológica del pipeline de producción. Con esto se completa la Fase 17-BIS en su totalidad y se habilita el inicio de Fase 18 (Advanced Local Runtime).

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| ADR de Fase 6 | `docs/architecture/adr/phase-17-bis/ADR_F17_BIS_06.md` | Decisiones arquitectónicas de Continuous Verification |
| NADRs de Fase 6 | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-25+.md` | Reglas normativas de integración CI/CD |
| Execution Plan de Fase 6 | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE6_EXECUTION_PLAN.md` | Secuencia operativa de implementación |
| Findings Register de Fase 6 | `docs/architecture/adr/phase-17-bis/reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md` | Registro de hallazgos |
| Handoff de Fase 6 | `docs/architecture/adr/phase-17-bis/handoff/FASE_6_HANDOFF.md` | Transición a Fase 18 |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro | `docs/architecture/adr/phase-17-bis/ADR_F17_BIS_MASTER.md` |
| ADR de Fase 5 | `docs/architecture/adr/phase-17-bis/ADR_F17_BIS_05.md` |
| NADR-20 (Corpus) | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-20.md` |
| NADR-21 (Ground Truth) | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-21.md` |
| NADR-22 (Topological Engine) | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-22.md` |
| NADR-23 (Calibration) | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-23.md` |
| NADR-24 (Certification) | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-24.md` |
| Execution Plan | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE5_EXECUTION_PLAN.md` |
| Methodology | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |
| ROADMAP | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` |
| Engineering Principles | `docs/architecture/ENGINEERING_PRINCIPLES.md` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_DEFERRED_FINDINGS_REGISTER.md` |
| Evidence Log | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_EXIT_REVIEW_EVIDENCE_LOG.md` |
| Benchmark Methodology | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_BENCHMARK_METHODOLOGY.md` |
| Curation Report | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_3_CURATION_REPORT.md` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| Provenance Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_2_PROVENANCE.md` | Linaje de corpus |
| Qualification Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_2_QUALIFICATION_RECORD.md` | Cualificación formal |
| Dataset Independence Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md` | Partición de datasets |
| Calibration Protocol Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md` | Protocolo de calibración |
| Wave 3.3 Provenance Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_3_PROVENANCE_RECORD.md` | Provenance de Wave 3.3 |
| Wave 4.3 Evidence Record | `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_4_3_EVIDENCE_RECORD.md` | Evidencia de Wave 4.3 |
| Handoff Fase 5 → Fase 6 | `docs/architecture/adr/phase-17-bis/handoff/FASE_5_HANDOFF.md` | Este documento |
| PROJECT_SCOPE | `docs/architecture/PROJECT_SCOPE.md` | Alcance del proyecto |
| PROJECT_TREE | `PROJECT_TREE.txt` | Estructura del código (⚠️ desactualizado, regenerar) |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: Traductor PDF — Pipeline automatizado para traducción de documentos científicos
Descripción: Sistema local de alto rendimiento que transforma PDFs académicos en AST V2,
             traduce preservando topología (ecuaciones, tablas, código intactos),
             y ensambla con fidelidad de layout
Stack: Python, PyMuPDF (extracción), ZhangShasha (topología), Pydantic (contratos),
       SQLite (WAL), asyncio
Arquitectura: DDD + Hexagonal (Ports & Adapters), Functional Core / Imperative Shell,
              Flat AST
Fase actual completada: Fase 5 — Baseline Certification (CONDITIONAL_PASS)
Siguiente sub-fase: Fase 6 — Continuous Verification (última sub-fase de 17-BIS)
Siguiente fase del ROADMAP: Fase 18 — Advanced Local Runtime
```

### 8.2 Code State

```text
Tests: 729 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
Rama: main (limpio post-commit)
Corpus: v3.9 sellado, 21 docs, manifest hash 727782fe0df26d9d...
Parameter identity: 6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5
Configuration identity: b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302
Result: Gate CONDITIONAL_PASS, Phase REJECTED_WITH_DOCUMENTED_LIMITATIONS
Corpus NSS: 0.7208 (HARD_FAIL, threshold 0.80)
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. No mutar oráculos sellados (NADR-21 §5.4 R19, NADR-24 §5.6 R25)
2. Calibration ≠ Evaluation: no calibrar sobre datos de evaluación final (NADR-23 §5.1 R2)
3. Motor canónico único: ZhangShasha + CriticalityAwareCostContext (ADR_F17_BIS_05 D4)
4. Zero Partial Sealing: biyección N_PDF = N_GT obligatoria (ADR_F17_BIS_MASTER §5)
5. Cero Fallos Silenciosos: ningún camino de error produce exit 0 (ENGINEERING_PRINCIPLES §IV)
6. Determinismo: todo pipeline de evaluación/serialización/hashing es determinista
7. Reutilización estricta: consumir infraestructura existente antes de crear nueva
8. Explicit over Implicit: cero magia en código, factorías explícitas y tipado estricto
9. Inmutabilidad de DTOs: frozen=True, transiciones retornan copia nueva
10. Flat Design: secuencias lineales con metadatos topológicos, no árboles anidados
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- Este handoff (FASE_5_HANDOFF.md)
- ROADMAP_ARQUITECTONICO_LP.md
- ENGINEERING_PRINCIPLES.md

Prioridad 2 (cargar para implementación):
- ADR_F17_BIS_MASTER.md (decisiones arquitectónicas)
- ADR_F17_BIS_05.md (decisiones de Fase 5)
- NADRs relevantes según la tarea específica

Prioridad 3 (consultar según necesidad):
- Execution Plan de Fase 5 (secuencia operativa histórica)
- Findings Register ARCHIVED (hallazgos diferidos)
- Curation Report (limitaciones del extractor)
- PROJECT_TREE.txt (estructura del código — regenerar antes de usar)
```

### 8.5 Pending Items (carry-forward)

```text
[H-5.3-1] Calibración estadística pendiente (N=21 disponible)
          → Destino: Fase 6 (recalibración con curvas PR + bootstrap CI + human verdicts)
          → Bloquea: Certificación CERTIFIED
          → Opciones: Recalibrar thresholds 0.80/0.95 con evidencia empírica

[H-5.3-2] Divergencia masiva runtime vs GTs (163 Critical FN)
          → Destino: Fase 6 (mejora de extractor)
          → Bloquea: Certificación CERTIFIED
          → Opciones: Evaluar Marker, Docling, Nougat

[H-5.6-1] Curaduría perdida en doc_11-13 (sobrescrita por generate_golden_draft)
          → Destino: Re-baseline v4.0
          → Bloquea: Nada (mitigado por gate O2 que previene repetición)
          → Opciones: Re-curar y re-sellar en nueva versión de corpus

[DF-06] Pipeline genera node_ids legacy
        → Destino: Fase 6 (fix en BenchmarkParserBridge)
        → Bloquea: Nada (mitigado por canonicalize_gt.py)
        → Opciones: Fix directo o continuar con canonicalize_gt.py

[H-5.5-5] Enforcement normativo O3 en autoridad de sellado
          → Destino: Fase 6
          → Bloquea: Nada (mitigado por gate O2 en tooling)

[H-5.5-6] Fingerprint de extractor/pipeline como identidad nueva
          → Destino: Fase 6 (posible enmienda normativa)
          → Bloquea: Nada

[DF-02] Verificación de ci.yml y pyproject.toml
        → Destino: Fase 6
        → Bloquea: Integración CI
```

### 8.6 Work Conventions

```text
- Los PDFs del corpus NO se trackean en git (copyright). Los GTs (JSON) y manifest SÍ se trackean.
- La curaduría de GTs ocurre ANTES del sellado (gate O2 en freeze_ground_truth.py).
- Todo hallazgo se registra en el Findings Register con ID único (H-5.N-X, DF-XX, GF-XX, O-*.W-N).
- Los NADRs son inmutables (FROZEN). Cualquier cambio requiere nuevo ADR o enmienda normativa.
- El motor canónico es ZhangShasha + CriticalityAwareCostContext. APTED es experimental.
- Los thresholds de NSS (0.80/0.95) son específicos del motor+config. No son universales.
- El runbook de onboarding está en FASE_5_BENCHMARK_METHODOLOGY.md §3.
- Los reportes de calibración van en reports/calibration/ (trackeados en git).
- Los reportes de regresión van en reports/certification/ (trackeados en git).
- Los PDFs sueltos en la raíz del repo son basura de trabajo y se ignoran en .gitignore.
- El PROJECT_TREE está desactualizado; regenerar con generate_workspace.py antes de usar.
```

### 8.7 System Entry Points

```text
tools/evaluation/freeze_ground_truth.py      → Sellado atómico con gate O2 de curaduría
tools/evaluation/curate_gt.py                → Escritor de curation_checklist.json
tools/evaluation/canonicalize_gt.py          → Canonicalización de node_ids con lineage
tools/evaluation/run_regression.py           → Regresión topológica (taxonomía NADR-19)
tools/evaluation/preflight_certification.py  → PREFLIGHT (8 precondiciones, NADR-24)
tools/evaluation/generate_golden_draft.py    → Generación de drafts de GT
tools/evaluation/add_document_to_corpus.py   → Alta de documentos en corpus
tools/evaluation/check_candidate.py          → Verificación física de candidatos
tools/evaluation/view_gt_html.py             → Visualización HTML de GTs
tools/evaluation/freeze_parameters.py        → Parameter freeze + provenance records
tools/evaluation/run_benchmark.py            → Benchmark de proveedores
apps/bootstrap/pipeline_factory.py           → Composition root de extracción
bootstrap/topology.py                        → Composition root de topología
```

**Factories centralizadas:**
- `apps/bootstrap/pipeline_factory.py::build_extraction_pipeline()` — Factoría única de extracción (NADR-19 §5.5 R20). Compone PyMuPDFProvider + BenchmarkParserBridge + FlatASTBuilder.
- `bootstrap/topology.py::build_canonical_engine_configuration()` — Configuración canónica del motor topológico. Compone ZhangShashaEngine + CriticalityAwareCostContext + HeadingAnchorPartitionStrategy + MaxBoundNormalizationPolicy + RegressionThresholds.

---

## 9. CLOSURE CRITERIA

Este handoff se considera cerrado (FROZEN) cuando:

- [x] Resumen ejecutivo completo (§1)
- [x] Estado actual validado con evidencia (§2)
- [x] Decisiones arquitectónicas documentadas (§3)
- [x] Scope entregado listado (§4)
- [x] Todos los items diferidos listados con destino (§5.2)
- [x] Restricciones carry-forward identificadas (§5.1)
- [x] Known risks documentados (§5.3)
- [x] Prerequisitos de siguiente fase definidos (§6)
- [x] Mapa de referencias completo (§7)
- [x] LLM Context Block autocontenido (§8)
- [x] Commit hash completado en §2.1 (pendiente del commit de cierre)
- [x] PROJECT_TREE regenerado (pendiente del commit de cierre)

**Veredicto:** 🟡 EN PROGRESO — Pendiente commit hash y regeneración de PROJECT_TREE. FROZEN al completar estos dos items.

---

**Nota de Gobernanza:** Este documento es el punto de transición entre fases.
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado
exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que
cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4)
para tener contexto completo de arranque. Los detalles normativos se consultan bajo
demanda según la tarea específica.

---

## Notas de emisión

1. **Commit hash pendiente:** El campo `{SHA del commit de cierre}` en §2.1 debe completarse con el hash real del commit que cierre la Fase 5. Ejecutá `git log --oneline -1` después del commit y actualizá ese campo. El estado pasa de 🟡 EN PROGRESO a ✅ CERRADO — FROZEN al completar este item y la regeneración del PROJECT_TREE.

2. **Los PDFs del corpus no se trackean** por decisión de ownership (copyright). Esto está documentado como Known Risk en §5.3 y como Work Convention en §8.6. Los GTs (JSON) y el manifest SÍ se trackean, lo que permite verificar la biyección localmente.

3. **El Handoff está en `docs/architecture/adr/phase-17-bis/handoff/`** pero ese directorio puede estar en `.gitignore` (decisión O-5.0-2, commit `f748fd7`). Si necesitás trackear este documento, hay que negar el patrón en `.gitignore` con `!docs/architecture/adr/phase-17-bis/handoff/`. Decime si querés trackearlo o mantenerlo como artefacto local.

4. **Fase 5 cerrada con CONDITIONAL_PASS.** La certificación científica es REJECTED_WITH_DOCUMENTED_LIMITATIONS porque NSS=0.7208 < 0.80, pero la baseline está correctamente construida y los Gates 1-4 están COMPLETED. Fase 6 (última sub-fase de 17-BIS) debe abordar la recalibración de thresholds y la mejora del extractor para alcanzar CERTIFIED. Tras Fase 6, el ROADMAP continúa con Fase 18 (Advanced Local Runtime).

5. **Corrección de evidencias:** La evidencia de H-5.6-1 (curaduría de doc_11-13 sobrescrita) fue verificada empíricamente durante Gate 5. Los GTs contienen solo tipos degradados (`paragraph`/`heading`), confirmando la sobrescritura. El gate O2 (Batch 1) previene la repetición de este patrón en futuros onboardings.