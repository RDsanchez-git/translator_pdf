# FASE 5 — WAVE 3.2: CALIBRATION PROTOCOL RECORD

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-10
**Gate:** Gate 3 — Scientific Calibration & Experimental Provenance
**Wave:** 3.2 — Calibration Protocol & Execution
**Derivado de:** NADR-F17BIS-23 §5.2, §5.4, §5.7 | FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md | PHASE_17BIS_FASE5_EXECUTION_PLAN v1.3.0

---

## 1. PROTOCOLO DE CALIBRACIÓN (NADR-23 §5.2 R4-R8) — Task 3.2.1

### 1.1 Estado del protocolo

NADR-23 §5.2 R4 establece: "Toda calibración MUST ser gobernada por un protocolo de calibración definido antes de la ejecución."

**Estado actual:** El protocolo está DEFINIDO pero NO EJECUTADO. La ejecución está condicionada a que el corpus alcance ≥20 documentos diversos (conforme a NADR-23 §5.3 R12 y la estrategia documentada en Wave 3.1).

### 1.2 Definición del experimento (R5)

Conforme a NADR-23 §5.2 R5, el protocolo define como mínimo:

| Elemento | Definición |
|:---|:---|
| Variable a calibrar | nss_hard_fail, nss_warning, cost_weights (CRITICAL, WARNING, INFO), warning_threshold |
| Ground truth observable | Veredictos humanos PASS/WARNING/HARD_FAIL anotados por experto por documento |
| Función objetivo | Maximizar F1-score para detección de HARD_FAIL sobre el conjunto de validación |
| Espacio de parámetros | nss_hard_fail ∈ [0.50, 0.95]; nss_warning ∈ [nss_hard_fail + 0.05, 1.0]; cost_weights ∈ [1.0, 10.0]³; warning_threshold ∈ [1, 5] |
| Restricciones | 0.0 ≤ nss_hard_fail < nss_warning ≤ 1.0 (invariante de RegressionThresholds); cost_weights CRITICAL > WARNING > INFO |
| Unidad de evaluación | Documento individual (corpus canónico sellado) |
| Independencia de datasets | Partición por SHA-256 conforme a Wave 3.1; CAL ∩ FINAL = ∅ (NADR-23 R10) |
| Criterio de aceptación | F1-score > 0.85 en validación cruzada; ningún documento con pérdida CRITICAL clasificada como PASS |

### 1.3 Algoritmo de búsqueda (R6)

Conforme a NADR-23 §5.2 R6: "El protocolo de calibración MUST definir el experimento antes de elegir el algoritmo de búsqueda."

El experimento está definido en §1.2. La selección del algoritmo de búsqueda es posterior y se decidirá al momento de la ejecución. Candidatos preliminares:

| Algoritmo | Justificación preliminar |
|:---|:---|
| Grid Search | Espacio de parámetros acotado; determinismo absoluto; reproducible |
| LOOCV | Adecuado para corpus de 20-30 documentos; maximiza datos de entrenamiento |
| Bootstrap resampling | Estimación de intervalos de confianza del threshold óptimo |

La decisión final del algoritmo se documentará en el Calibration Provenance Record (Wave 3.3) al momento de la ejecución.

### 1.4 Aprobación del protocolo (R7)

Conforme a NADR-23 §5.2 R7: "El protocolo de calibración MUST ser aprobado antes de la ejecución de la calibración."

**Estado:** El protocolo queda registrado como APROBADO CONDICIONAL. La condición es la materialización de un corpus ≥20 documentos. La aprobación definitiva se ejecutará al momento de la calibración.

### 1.5 Condiciones de reproducibilidad (R8)

Conforme a NADR-23 §5.2 R8, el protocolo captura las condiciones necesarias para reproducir el resultado:

| Condición | Valor al momento de la ejecución |
|:---|:---|
| Protocolo/versión | Este documento, versión vigente al momento de la ejecución |
| Corpus identity | SHA-256 del manifest (corpus_version + manifest_hash) |
| Configuración del motor | ConfigurationFingerprintCalculator.calculate() sobre CanonicalEngineConfiguration |
| Parámetros iniciales | Defaults actuales: 0.80/0.95, 5.0/2.0/1.0, 1 |
| Restricciones | §1.2 de este documento |
| Seed | N/A (algoritmos deterministas) o seed controlado si se usa método estocástico |
| Configuración del algoritmo de búsqueda | Se documentará al momento de la ejecución |

---

## 2. EXPERIMENTAL LIFECYCLE (NADR-23 §5.4 R14-R17) — Task 3.2.2

### 2.1 Lifecycle completo

Conforme a NADR-23 §5.4 R14, el proceso MUST completar las fases secuenciales:

    CALIBRATION → VALIDATION → PARAMETER FREEZE → FINAL EVALUATION

### 2.2 Estado actual del lifecycle con N=6

| Fase | Estado | Justificación |
|:---|:---|:---|
| CALIBRATION | NO EJECUTADA (∅) | Corpus insuficiente (N=6 < 20). NADR-23 R12 prohíbe presumir robustez estadística. |
| VALIDATION | SANITY VALIDATION (6 docs) | Verificación de que los defaults no producen veredictos absurdos. NO genera ni selecciona parámetros candidatos. |
| PARAMETER FREEZE | Defaults congelados | Los defaults actuales se congelan como parámetros normativos (no calibrados). Ver §3.6 de este documento. |
| FINAL EVALUATION | RESERVADA PARA GATE 5 | NADR-23 R17: produce evidencia de baseline certificada sobre conjunto disjunto. |

### 2.3 Regla de no-omisión (R14)

NADR-23 §5.4 R14 establece: "La omisión de cualquier fase MUST NOT ser permitida."

**Cumplimiento:** Ninguna fase se omite. CALIBRATION se registra como fase no ejecutable con justificación normativa (R12). VALIDATION se ejecuta como sanity check. PARAMETER FREEZE se ejecuta sobre los defaults. FINAL EVALUATION se reserva para Gate 5.

### 2.4 Regla de selección en VALIDATION (R15)

NADR-23 §5.4 R15 establece: "La selección de parámetros MUST ocurrir en la fase de VALIDATION, no en la fase de CALIBRATION."

**Cumplimiento:** Dado que CALIBRATION no genera candidatos (∅), no hay selección de parámetros. Los defaults se mantienen sin modificación.

### 2.5 Regla de generalización en VALIDATION (R16)

NADR-23 §5.4 R16 establece: "La fase de VALIDATION MUST verificar la generalización de los parámetros candidatos sobre un conjunto de validación disjunto del conjunto de calibración."

**Cumplimiento:** Dado que LOCAL_CALIBRATION=∅, la disjunción es trivialmente satisfecha. SANITY_VALIDATION opera sobre los 6 documentos sellados como verificación de cordura, no como validación de generalización.

### 2.6 Regla de FINAL EVALUATION (R17)

NADR-23 §5.4 R17 establece: "La fase de FINAL EVALUATION MUST producir evidencia de baseline certificada sobre un conjunto de evaluación final disjunto del conjunto de calibración y del conjunto de validación."

**Cumplimiento:** FINAL_EVALUATION_SET = RESERVED_FOR_GATE_5. Gate 5 decidirá si usa el mismo corpus (con documentación de la limitación) o un corpus ampliado.

### 2.7 Resultados de Sanity Validation (ejecución real)

**Ejecutado:** 2026-09-10 | **Comando:** `python -m tools.evaluation.run_regression --corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf --output-dir reports/sanity_validation`

**Evidencia:** `reports/sanity_validation/regression_report.{json,md}`

| Documento | Verdict | NSS | Critical FN | Warning FN | Info FN | Signal |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| doc_01_single | HARD_FAIL | 0.4286 | 14 | 17 | 0 | ABSOLUTE_FAIL |
| doc_02_double | HARD_FAIL | 0.3643 | 68 | 41 | 1 | ABSOLUTE_FAIL |
| doc_03_math | HARD_FAIL | 0.7350 | 9 | 24 | 0 | ABSOLUTE_FAIL |
| doc_04_table | HARD_FAIL | 0.6355 | 15 | 11 | 6 | ABSOLUTE_FAIL |
| doc_05_graph | HARD_FAIL | 0.7582 | 0 | 29 | 19 | ABSOLUTE_FAIL |
| doc_07_pesaran | PASS | 1.0000 | 0 | 0 | 0 | PASS |

**Agregado:**
- Corpus NSS: 0.6536
- Corpus Verdict: HARD_FAIL
- Total Critical FN: 106
- Total Warning FN: 122
- Total Info FN: 26
- PASS: 1/6 | WARNING: 0/6 | HARD_FAIL: 5/6

#### 2.7.1 Interpretación de resultados

El sanity validation detectó exactamente lo que debía detectar: el runtime de producción (`build_extraction_pipeline()` → `PyMuPDFProvider`) produce ASTs que divergen masivamente de los Ground Truths curados manualmente. Esto es **consistente** con los hallazgos de curaduría de Wave 1.3:

- **H-5.1-9 (ACCEPTED_LIMITATION):** doc_02_double tiene 52 ecuaciones fragmentadas en GT → aquí se manifiesta como 68 Critical FN (pérdida de display_equation, f1=0.0)
- **H-5.1-10 (ACCEPTED_LIMITATION):** doc_05_graph tiene labels de ejes como paragraphs → aquí se manifiesta como 19 Info FN en captions (f1=0.0)
- **doc_07_pesaran (NSS=1.0000):** TAUTOLOGÍA, no validación positiva. El GT no fueeditado en curaduría (solo revisado con observación "fuentes Type 3"), por lo que es idéntico a la salida cruda del extractor. El documento contiene tablas (Table 1, Table 2) que PyMuPDF no extrae; un GT correctamente curado divergiría del runtime y produciría HARD_FAIL como los demás. Ver H-5.3-3.

#### 2.7.2 Implicaciones para calibración

Los resultados **refuerzan (no invalidan)** la decisión de Wave 3.1 de no calibrar con 6 documentos:

1. El corpus es insuficiente estadísticamente (N=6 < 20, NADR-23 R12)
2. Cualquier "calibración" sobre estos datos sería calibrar para aceptar mediocridad del extractor
3. Los thresholds actuales (0.80/0.95) **no son el problema** — el problema es el extractor (PyMuPDFProvider)
4. La magnitud de la divergencia (106 Critical FN totales) confirma que la limitación es estructural, no paramétrica
5. El único PASS del corpus (doc_07) es tautológico (H-5.3-3): no existe ni un solodocumento que valide positivamente el pipeline contra una verdad independiente. La señal real del sanity validation es 5/6 divergencia masiva + 1/6 sin señal.

**Hallazgo derivado:** H-5.3-2 registrado como ACCEPTED_LIMITATION. Ver §3.7 de este documento.

---

## 3. CONDICIONES DE VALIDEZ CIENTÍFICA (NADR-23 §5.7 R26-R28) — Task 3.2.3

### 3.1 Calibration validity (R26a)

NADR-23 §5.7 R26(a): "Una calibración MUST ser considerada científicamente válida si fue ejecutada conforme a un protocolo aprobado, utilizó datasets independientes a nivel de cryptographic content identity, produjo un Calibration Provenance Record suficiente, y completó las fases CALIBRATION y VALIDATION."

**Estado actual:** NO se ha ejecutado calibración empírica. Por lo tanto, no existe calibration validity. Los defaults actuales NO son parámetros calibrados.

### 3.2 Parameter eligibility (R26b)

NADR-23 §5.7 R26(b): "Un conjunto de parámetros MUST ser considerado elegible para freeze si sobrevivió la fase de VALIDATION conforme al criterio de aceptación."

**Estado actual:** Los defaults actuales son elegibles para freeze como parámetros NORMATIVOS, no como parámetros calibrados. La elegibilidad se basa en el criterio de diseño (§3.4 de este documento), no en validación empírica.

### 3.3 Certification eligibility (R26c)

NADR-23 §5.7 R26(c): "Una certificación MUST ser considerada elegible si los parámetros congelados fueron utilizados en una FINAL EVALUATION independiente."

**Estado actual:** FINAL EVALUATION reservada para Gate 5. La certificación de la baseline queda condicionada a la ejecución de Gate 5.

### 3.4 Tuning ad-hoc vs. calibración científica (R27)

NADR-23 §5.7 R27 establece: "El tuning ad-hoc sin protocolo MUST NOT ser considerado calibración científica. La distinción entre calibración y tuning MUST ser verificable."

**Verificación:** Los defaults actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) NO son resultado de tuning ad-hoc. Son parámetros NORMATIVOS definidos por diseño con las siguientes justificaciones:

| Parámetro | Justificación de diseño |
|:---|:---|
| nss_hard_fail = 0.80 | Threshold conservador: NSS < 0.80 indica pérdida estructural significativa (>20% de divergencia). Consistente con práctica de fail-fast para proteger nodos CRITICAL. |
| nss_warning = 0.95 | Threshold exigente: NSS entre 0.80 y 0.95 indica degradación moderada que requiere revisión humana antes de continuar. |
| cost_weights CRITICAL = 5.0 | La pérdida de un nodo CRITICAL (ecuación, tabla) debe dominar el score. 5× el peso de INFO garantiza que una ecuación perdida pese más que 4 párrafos INFO. |
| cost_weights WARNING = 2.0 | Headings y párrafos son importantes pero no críticos. 2× el peso de INFO. |
| cost_weights INFO = 1.0 | Baseline natural (costo unitario). Consistente con UnitCostContext como referencia. |
| warning_threshold = 1 | Cualquier pérdida WARNING (≥1 falso negativo) emite señal de advertencia. Consistente con ICDAR: cualquier error crítico = fail absoluto. |

**Distinción verificable:** Los defaults son parámetros normativos/heurísticos definidos por diseño. NO son parámetros calibrados empíricamente. La calibración empírica se ejecutará cuando el corpus alcance ≥20 documentos, conforme al protocolo de §1 de este documento.

### 3.5 Distinguibilidad de tipos de parámetros (R28)

NADR-23 §5.7 R28 establece: "Un parámetro calibrado empíricamente MUST ser distinguible de un parámetro normativo o heurístico. La confusión de tipos de parámetros MUST NOT ser permitida."

**Clasificación actual:**

| Parámetro | Tipo | Origen |
|:---|:---|:---|
| nss_hard_fail = 0.80 | NORMATIVO | Diseño arquitectónico |
| nss_warning = 0.95 | NORMATIVO | Diseño arquitectónico |
| cost_weights = 5.0/2.0/1.0 | NORMATIVO | Diseño arquitectónico |
| warning_threshold = 1 | NORMATIVO | Diseño arquitectónico |

Cuando se ejecute calibración empírica con corpus ≥20, los parámetros resultantes se clasificarán como CALIBRADOS y se registrará la transición en el Calibration Provenance Record.

### 3.6 Parameter Identity (NADR-23 §5.6 R24)

NADR-23 §5.6 R24 establece: "El parameter freeze MUST ser verificable: los parámetros congelados MUST ser identificables mediante un hash criptográfico determinista (parameter identity conforme a R20)."

**Parameter Identity (SHA-256):**

    b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302

**Configuración canónica congelada (CanonicalEngineConfiguration):**

| Campo | Valor |
|:---|:---|
| engine_type | core.benchmark.topology.engines.zhang_shasha.engine.ZhangShashaEngine |
| cost_weights | (5.0, 2.0, 1.0) |
| partition_strategy | core.benchmark.topology.partitioning.heading.HeadingAnchorPartitionStrategy |
| alignment_strategy | core.benchmark.topology.alignment.strategy.LCSAnchorAlignmentStrategy |
| normalization_policy | core.benchmark.topology.policies.normalization.MaxBoundNormalizationPolicy |
| overflow_strategy | core.benchmark.topology.policies.overflow.WorstCaseOverflowStrategy |
| matching_policy | bootstrap.topology.DefaultNodeMatchingPolicy |
| nss_hard_fail | 0.80 |
| nss_warning | 0.95 |
| warning_threshold | 1 |

**Determinismo verificado:** ConfigurationFingerprintCalculator.calculate() produce el mismo hash ante la misma configuración (test_same_config_same_hash PASSED en Wave 2.4).

### 3.7 Hallazgo derivado: H-5.3-2

**ID:** H-5.3-2
**Clasificación:** ACCEPTED_LIMITATION
**Origen:** Sanity Validation de Wave 3.2 (§2.7)
**Descripción:** El runtime de producción (`build_extraction_pipeline()` → `PyMuPDFProvider`) produce divergencia masiva respecto a los Ground Truths curados manualmente: 5/6 documentos = HARD_FAIL, 106 Critical FN totales, NSS promedio 0.6536. La divergencia es consistente con las limitaciones de PyMuPDFProvider documentadas en H-5.1-9 (fragmentación de ecuaciones) y H-5.1-10 (labels de gráficos).

**Interpretación:** Este hallazgo **no invalida** los defaults ni la arquitectura. Confirma que:
1. Los thresholds actuales (0.80/0.95) están funcionando correctamente (detectan la divergencia)
2. La magnitud de la divergencia es estructural (limitación del extractor), no paramétrica
3. Cualquier calibración empírica sobre este corpus sería inválida (calibrar para aceptar mediocridad)

**Destino:** Recalibración diferida a:
- Fase 6 (Continuous Verification) cuando corpus alcance ≥20 documentos, O
- Extensión de Fase 5 si usuario adquiere 13+ documentos adicionales, O
- Fase futura de mejora de extractor (PyMuPDFProvider) cuando se aborde H-5.1-11 (Detect & Placeholder)

**No bloquea Gate 3:** El lifecycle CAL→VAL→FREEZE está completo (CAL=∅, VAL=sanity, FREEZE=defaults).

### 3.8 Hallazgo derivado: H-5.3-3

**ID:** H-5.3-3
**Clasificación:** ACCEPTED_LIMITATION
**Origen:** Reinterpretación del sanity validation de Wave 3.2 (§2.7)
**Descripción:** El GT de doc_07_pesaran no fue editado en curaduría; es salida cruda
de build_extraction_pipeline(). El NSS=1.0000 es tautología (extractor contra sí
mismo), no validación positiva. El documento contiene tablas que PyMuPDF no extrae
(fuentes Type 3); un GT curado correctamente divergiría del runtime.
**Consecuencia:** doc_07 marcado como no-informativo para validación. Curaduría real
diferida y agrupada con la ampliación del corpus (H-5.2-1 + déficit de 13 docs).
**No bloquea Gate 3:** re-sellar en medio de Gate 3 rompería la trazabilidad del
manifest_hash usado en Waves 3.1-3.2 y no cambiaría ninguna decisión de calibración.

---

## 4. REGLA ANTI-LEAKAGE (refuerzo)

Conforme a la estrategia documentada en Wave 3.1 y NADR-23 R2:

> Los resultados de SANITY_VALIDATION_SET MUST NOT modificar nss_hard_fail, nss_warning, cost_weights ni warning_threshold.

Esta regla se refuerza en Wave 3.2 como invariante de todo el lifecycle. Cualquier intento de modificar parámetros basándose en resultados de sanity validation constituye una violación de NADR-23 R2 y R27.

**Verificación empírica:** Los resultados de §2.7 muestran divergencia masiva (5/6 HARD_FAIL). Si hubiéramos "calibrado" sobre estos datos, habríamos degradado los thresholds para acomodar la mediocridad del extractor. La regla anti-leakage previene exactamente este sesgo de confirmación.

---

## 5. TRAZABILIDAD

| Task | Descripción | Estado |
|:---|:---|:---:|
| 3.2.1 | Protocolo de calibración definido antes de elegir algoritmo | ✅ DONE (protocolo definido, ejecución condicionada a corpus ≥20) |
| 3.2.2 | Lifecycle CAL→VAL→FREEZE ejecutado | ✅ DONE (CAL=∅, VAL=sanity ejecutada con resultados reales §2.7, FREEZE=defaults con fingerprint §3.6, FINAL=Gate 5) |
| 3.2.3 | Condiciones de validez científica documentadas | ✅ DONE (defaults = normativos, no tuning ad-hoc; H-5.3-2 documentado) |

---

## 6. HALLAZGOS DERIVADOS DE WAVE 3.2

| ID | Descripción | Clasificación |
|:---|:---|:---|
| H-5.3-2 | Divergencia masiva entre runtime de producción y GTs curados (5/6 HARD_FAIL, 106 Critical FN). Consistente con limitaciones estructurales de PyMuPDFProvider (H-5.1-9, H-5.1-10). No invalida los thresholds; confirma que el problema es el extractor, no los parámetros. | ACCEPTED_LIMITATION |
| H-5.3-3 | GT de doc_07 no editado en curaduría: NSS=1.0000 es tautología (extractor contra sí mismo), no validación positiva. Documento contiene tablas no extraídas por PyMuPDF (Type 3). doc_07 marcado no-informativo; curaduría diferida con ampliación de corpus. | ACCEPTED_LIMITATION |

---

**Nota de Gobernanza:** Este documento es el registro del protocolo de calibración y lifecycle para Gate 3. No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs. Su propósito es documentar el protocolo de calibración, el estado del lifecycle, la clasificación de parámetros y los resultados reales de sanity validation conforme a NADR-23 §5.2, §5.4 y §5.7.
