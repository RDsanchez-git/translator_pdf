# FASE 5 — WAVE 3.3: PROVENANCE & PARAMETER FREEZE RECORD

**Documento:** docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_3_PROVENANCE_RECORD.md
**Version:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-10
**Gate:** Gate 3 — Scientific Calibration & Experimental Provenance
**Wave:** 3.3 — Provenance & Parameter Freeze
**Derivado de:** NADR-F17BIS-23 §5.5, §5.6, §5.8 | FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md | FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md | PHASE_17BIS_FASE5_EXECUTION_PLAN v1.3.1
**MIG-08 ejecutado:** 2026-09-10

---

## 1. IDENTIDADES CRIPTOGRAFICAS MATERIALIZADAS

Las siguientes identidades son el resultado concreto del parameter freeze ejecutado por MIG-08. Se embeben aqui como evidencia inmutable; cualquier modificacion en los valores requeriria un nuevo documento de gobernanza (NADR-23 §5.6 R25).

| Identidad | Valor (SHA-256) | Derivacion |
|:---|:---|:---|
| corpus_identity | `0fda76909289fe8777b8413f4178e2117d2961689437b66e4454c1a7a07a4c34` | manifest_hash del corpus canonico sellado v1.0 |
| configuration_identity | `b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302` | ConfigurationFingerprintCalculator sobre CanonicalEngineConfiguration |
| parameter_identity | `6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5` | ParameterIdentityCalculator sobre FrozenParameters (solo parametros calibrables) |
| experiment_identity | `2c26f93fe375130a209cd2d0f3687bc02fe993b167cc1585709cf0a3fec74ddd` | ExperimentIdentityCalculator sin timestamp (R20) |
| result_identity (sanity) | `f97a3d43672dc5f74ff92a998505ecc92b5067999a4ecb631975e6436a8060ae` | SHA-256 de reports/sanity_validation/regression_report.json |

**Distincion semantica clave (R20, R25):** parameter_identity es intencionalmente distinta de configuration_identity. Un cambio de motor/politica/normalizacion sin tocar los parametros NO generaria nueva parameter identity ni nueva linea de certificacion de parametros. Solo cambios en los valores calibrables (nss_hard_fail, nss_warning, cost_weights, warning_threshold) generan nueva parameter identity.

---

## 2. PARAMETROS CONGELADOS (Task 3.3.2)

Conforme a NADR-23 §5.6 R23-R25:

| Parametro | Valor | Tipo | Origen |
|:---|:---:|:---|:---|
| nss_hard_fail | 0.80 | Threshold | Normativo (diseño arquitectonico) |
| nss_warning | 0.95 | Threshold | Normativo (diseño arquitectonico) |
| cost_weights | (5.0, 2.0, 1.0) | Pesos de criticidad (CRITICAL, WARNING, INFO) | Normativo (diseño arquitectonico) |
| warning_threshold | 1 | FNs WARNING minimos | Normativo (diseño arquitectonico) |

**Invariante de thresholds:** `0.0 <= nss_hard_fail < nss_warning <= 1.0` verificada en `FrozenParameters.__post_init__`.

**Regla de inmutabilidad (R25):** toda nueva configuracion de estos cuatro valores constituye una nueva parameter identity y requiere una nueva linea de certificacion. Enforcement operacional:
- `tests/integration/test_parameter_freeze.py::test_repo_freeze_artifact_matches_domain_defaults` recalcula parameter_identity desde los defaults del dominio y la compara con el artefacto en `reports/calibration/parameter_freeze.json`. Si alguien muta un default sin saberlo, el test falla.
- `tools/evaluation/freeze_parameters.py` retorna exit code 2 si se invoca con una parameter_identity distinta a la ya materializada (conflicto de freeze).

---

## 3. CALIBRATION PROVENANCE RECORD (Task 3.3.1)

Conforme a NADR-23 §5.5 R18-R22. Artefacto materializado: `reports/calibration/calibration_provenance_record.json`.

| Campo (R18) | Valor |
|:---|:---|
| corpus_identity | `0fda76909289fe8777b8413f4178e2117d2961689437b66e4454c1a7a07a4c34` |
| metric_configuration | `b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302` |
| parameters | `{nss_hard_fail: 0.8, nss_warning: 0.95, cost_weights: [5.0, 2.0, 1.0], warning_threshold: 1}` |
| result | `SANITY_VALIDATION: corpus_verdict=HARD_FAIL; corpus_nss=0.6535949846158722; pass=1; warning=0; hard_fail=5` |
| timestamp | (inyectado en la ejecucion de MIG-08; no participa en identidades, R20) |

| Campo adicional | Valor | Justificacion |
|:---|:---|:---|
| parameter_identity | `6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5` | R20(b) |
| experiment_identity | `2c26f93fe375130a209cd2d0f3687bc02fe993b167cc1585709cf0a3fec74ddd` | R20(a), sin timestamp |
| result_identity | `f97a3d43672dc5f74ff92a998505ecc92b5067999a4ecb631975e6436a8060ae` | R20(c) |
| protocol_identity | `FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md@1.0.0` | Referencia al protocolo aprobado (R19) |
| calibration_run | `NONE` | LOCAL_CALIBRATION_SET = ∅ (Wave 3.1, H-5.3-1) |
| parameters_origin | `NORMATIVE_DESIGN` | Distinguibilidad R28: normativos, no calibrados empiricamente |

**Condiciones de reproducibilidad (R19):** search_configuration = NONE, seed = NONE (algoritmos deterministas). Condiciones de ejecucion documentadas: H-5.3-1, H-5.3-2, H-5.3-3.

**Artifact provenance vs calibration-run provenance (R21, R22):** este record es calibration-run provenance (identidad del experimento). No duplica el artifact provenance del corpus (linaje de manifest y oráculos, Wave 1.2). No se prescribe infraestructura especifica (R22): la implementacion vive en el Execution Plan (MIG-08).

**Calibration validity (R26a):** no se ejecuto calibracion empirica. Los parametros son normativos por diseño, no calibrados. Calibration validity no aplica en esta instancia; se aplicara cuando el corpus alcance ≥20 documentos diversos y se ejecute el protocolo de Wave 3.2.

---

## 4. EVALUATION PROVENANCE RECORD (Task 3.3.3)

Conforme a NADR-23 §5.8 R29-R31. Artefacto materializado: `reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json`.

| Campo (R31) | Valor |
|:---|:---|
| corpus_identity | `0fda76909289fe8777b8413f4178e2117d2961689437b66e4454c1a7a07a4c34` |
| configuration_identity | `b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302` |
| frozen_parameters_identity | `6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5` |
| result | `SANITY_VALIDATION: corpus_verdict=HARD_FAIL; corpus_nss=0.6535949846158722; pass=1; warning=0; hard_fail=5` |
| timestamp | (inyectado; no participa en identidades, R20) |
| result_identity | `f97a3d43672dc5f74ff92a998505ecc92b5067999a4ecb631975e6436a8060ae` |

| Campo adicional | Valor | Justificacion |
|:---|:---|:---|
| evaluation_kind | `SANITY_VALIDATION` | Distincion obligatoria frente a FINAL_EVALUATION (R2, R17) |
| calibration_provenance_reference | `2c26f93fe375130a209cd2d0f3687bc02fe993b167cc1585709cf0a3fec74ddd` | Trazabilidad R31: apunta al experiment identity del Calibration Provenance Record |
| limitations | `["H-5.3-1", "H-5.3-2", "H-5.3-3"]` | Limitaciones conocidas del conjunto de validacion |

**Independencia del registro (R29):** el Evaluation Provenance Record es un artefacto separado del Calibration Provenance Record. Son trazables via `calibration_provenance_reference = experiment_identity`, pero no comparten archivo.

**Idempotencia por kind (R33):** el entry point `freeze_parameters.py` escribe el Evaluation Provenance Record con nombre acotado por kind (`evaluation_provenance_record_{kind}.json`). En Gate 5 (Task 5.2.2), la ejecucion con `--evaluation-kind FINAL_EVALUATION` sobre el mismo freeze existente no caera en no-op: emitira `evaluation_provenance_record_FINAL_EVALUATION.json` sin tocar el freeze ni el Calibration Provenance Record.

---

## 5. HALLAZGOS ASOCIADOS

Los tres hallazgos estan clasificados `ACCEPTED_LIMITATION` en FASE_5_DEFERRED_FINDINGS_REGISTER v0.12.0 (§3.3 y §9.2.7).

| ID | Clasificacion | Relacion con Wave 3.3 |
|:---|:---|:---|
| H-5.3-1 | ACCEPTED_LIMITATION | Calibracion estadistica no ejecutable con 6 documentos (N=6 < 20, NADR-23 R12). Justifica `calibration_run=NONE` y `parameters_origin=NORMATIVE_DESIGN`. |
| H-5.3-2 | ACCEPTED_LIMITATION | Divergencia masiva entre runtime de produccion y GTs curados: 5/6 HARD_FAIL, 106 Critical FN, corpus NSS 0.6536. Confirma que la divergencia es estructural (limitacion del extractor), no parametrica. Referenciado en limitations del Evaluation Provenance Record. |
| H-5.3-3 | ACCEPTED_LIMITATION | GT de doc_07_pesaran no editado en curaduria: es salida cruda del extractor; el unico PASS del sanity validation es tautologico (NSS=1.0000, global_ted=0.0). Curaduria real diferida con ampliacion de corpus. Referenciado en limitations del Evaluation Provenance Record. |

---

## 6. TRAZABILIDAD

| Task | Descripcion | Estado |
|:---|:---|:---:|
| 3.3.1 | Calibration Provenance Record con 5 campos minimos (R18) y 3 tipos de identidad (R20) | DONE |
| 3.3.2 | Parameter freeze con hash determinista (R24) e inmutabilidad verificada (R25) | DONE |
| 3.3.3 | Evaluation Provenance Record independiente (R29) pero trazable (R31) | DONE |

| Operacion | Estado |
|:---|:---:|
| MIG-08 (parameter freeze) | DONE |

---

## 7. ARTEFACTOS MATERIALIZADOS

| Ruta | Contenido | Reglas |
|:---|:---|:---|
| `core/benchmark/topology/regression/provenance.py` | Modulo de dominio: `FrozenParameters`, `ParameterIdentityCalculator`, `ExperimentIdentityCalculator`, `ResultIdentityCalculator`, `CalibrationProvenanceRecord`, `EvaluationProvenanceRecord` | NADR-23 §5.5 R18-R22, §5.6 R23-R25, §5.8 R29-R31 |
| `tools/evaluation/freeze_parameters.py` | Entry point CLI (Imperative Shell) con semantica de salida 0/1/2 | NADR-23 §5.6 R25, DF-18 |
| `reports/calibration/parameter_freeze.json` | Artefacto de freeze (parameter_identity + parametros + metadata) | NADR-23 §5.6 R23-R25 |
| `reports/calibration/calibration_provenance_record.json` | Calibration Provenance Record (run NONE, origen normativo) | NADR-23 §5.5 R18-R22 |
| `reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json` | Evaluation Provenance Record del sanity validation | NADR-23 §5.8 R29-R31 |
| `tests/unit/test_provenance_identities.py` | 19 tests unitarios: determinismo, sensibilidad, distincion de identidades, inmutabilidad | NADR-23 §5.5 R20, §5.6 R24 |
| `tests/integration/test_parameter_freeze.py` | 7 tests de integracion: materializacion, idempotencia, conflicto, FINAL_EVALUATION sobre freeze existente, enforcement sobre el artefacto del repo | NADR-23 §5.6 R25 |

---

**Nota de Gobernanza:** Este documento es el registro del parameter freeze y los provenance records de Gate 3. No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs. Su proposito es embeber las identidades criptograficas reales materializadas por MIG-08 y proveer trazabilidad completa a los artefactos en disco.
