# FASE 5 — WAVE 3.1: DATASET INDEPENDENCE RECORD

**Documento:** docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-10
**Gate:** Gate 3 — Scientific Calibration & Experimental Provenance
**Wave:** 3.1 — Dataset Independence & Partition
**Derivado de:** NADR-F17BIS-23 §5.1, §5.3, §5.7 | ADR_F17_BIS_MASTER §5 | PHASE_17BIS_FASE5_EXECUTION_PLAN v1.2.5

---

## 1. DECLARACIÓN DE FASES (NADR-23 §5.1 R1-R3)

La arquitectura distingue tres conceptos operacionalmente distintos:

| Fase | Rol | Estado en Gate 3 |
|:---|:---|:---|
| CALIBRATION | Genera y evalúa parámetros candidatos conforme al espacio de búsqueda | NO EJECUTADA — corpus insuficiente (N=6 < 20) |
| VALIDATION | Determina la elegibilidad y selección de candidatos conforme al criterio predefinido | NO EJECUTADA — no hay candidatos generados |
| FINAL EVALUATION | Produce evidencia de baseline certificada con parámetros congelados | RESERVADA PARA GATE 5 |

### Regla de secuencialidad (R3)

CALIBRATION, VALIDATION y FINAL EVALUATION MUST ser ejecutadas como fases secuenciales distintas. La ejecución simultánea o la mezcla de fases MUST NOT ser permitida.

**Cumplimiento:** En Gate 3, CALIBRATION no se ejecuta. No hay mezcla de fases.

### Regla de no-contaminación (R2)

Los resultados de FINAL EVALUATION MUST NOT participar en la selección de parámetros. La contaminación de la evaluación final por el proceso de calibración MUST NOT ser permitida.

**Cumplimiento:** FINAL EVALUATION está reservada para Gate 5. No se ejecuta en Gate 3.

---

## 2. CONTENT IDENTITIES (NADR-23 §5.3 R9)

La separación de datasets MUST basarse en cryptographic content identity (SHA-256), no en filename ni en document_id.

### Corpus canónico sellado — v1.0

**Manifest hash global:** 0fda76909289fe8777b8413f4178e2117d2961689437b66e4454c1a7a07a4c34
**Corpus version:** v1.0
**Total documentos:** 6

| document_id | SHA-256 | traits | page_count | ground_truth_state | oracle_hash |
|:---|:---|:---|:---:|:---:|:---|
| doc_01_single | 2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3 | native_pdf, heavy_math | 3 | sealed | fe0f8409dbbdd512... |
| doc_02_double | 84891f98114b90a7b8b80eee46d5de9990707046b8cea29affb3536da51a3123 | native_pdf, multi_column, heavy_math | 3 | sealed | 51d651de79d4e336... |
| doc_03_math | 21b9283a83f92983ebeb688d76a0d8c0de5068dc703129db42e7e2a2ea2a19fe | scanned_noise, heavy_math | 3 | sealed | 679e9443f25e09c9... |
| doc_04_table | de56cd0420852abdf1c13e4a4853e5977a6ecf8021811bb5cb70d75ccfa925ab | native_pdf, nested_tables, heavy_math, floating_figures | 3 | sealed | c71a4d4cb9e3e88a... |
| doc_05_graph | 274ce908d472a06b6211e667861d5cf7bde2749d1412415447c7e1d3ce6df789 | native_pdf, multi_column, floating_figures | 3 | sealed | f81575ba9b462f51... |
| doc_07_pesaran | 166bf27184067614ec7408ce9bea0d016a9acd4b55688ff8699956880f1eec60 | native_pdf, heavy_math, nested_tables | 3 | sealed | 8f361fb556b2d5c0... |

### Verificación de unicidad

Los 6 SHA-256 son únicos. No hay documentos duplicados a nivel de content identity.

---

## 3. ESTRATEGIA DE PARTICIÓN (NADR-23 §5.3 R11-R13)

### 3.1 Decisión de partición

Con N=6 documentos (< 20 identidades únicas), NADR-23 §5.3 R12 establece:

> "Con un corpus inferior a 20 identidades únicas, una partición clásica train/validation/holdout MUST NOT ser presumida estadísticamente robusta únicamente en virtud de la partición."

**Decisión:** No se ejecuta partición clásica CAL/VAL/FINAL. La estrategia es:

    LOCAL_CALIBRATION_SET  = (vacío)
    SANITY_VALIDATION_SET  = {6 documentos sellados}
    FINAL_EVALUATION_SET   = RESERVED_FOR_GATE_5

### 3.2 Justificación

| Aspecto | Justificación |
|:---|:---|
| Corpus insuficiente | N=6 < 20. NADR-23 R12 prohíbe presumir robustez estadística. |
| No hay calibración empírica | LOCAL_CALIBRATION_SET es vacío. No se generan parámetros candidatos. |
| Defaults de diseño | Los parámetros actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) son de diseño, no calibrados empíricamente. |
| Distinguibilidad de parámetros (R28) | Los defaults son normativos/heurísticos, NO calibrados empíricamente. NADR-23 §5.7 R28 exige esta distinguibilidad: "Un parámetro calibrado empíricamente MUST ser distinguible de un parámetro normativo o heurístico." |
| Sanity validation | SANITY_VALIDATION_SET valida que los defaults no producen veredictos absurdos. NO modifica parámetros. |
| Final evaluation reservada | FINAL_EVALUATION_SET se reserva para Gate 5, donde se decidirá si usa el mismo corpus o uno ampliado. |

### 3.3 Regla anti-leakage (NADR-23 R2)

> Los resultados de SANITY_VALIDATION_SET MUST NOT modificar nss_hard_fail, nss_warning, cost_weights ni warning_threshold. Solo validan que los defaults producen veredictos razonables.

**Cumplimiento:** Esta regla se registra como invariante de Gate 3. Cualquier intento de modificar parámetros basándose en SANITY_VALIDATION_SET constituye una violación de NADR-23 R2.

### 3.4 Disjunción (NADR-23 R10)

> El conjunto de calibración (calibration dataset) MUST ser disjunto del conjunto de evaluación final (final evaluation dataset) a nivel de cryptographic content identity.

**Cumplimiento:** LOCAL_CALIBRATION_SET es vacío. La intersección de vacío con FINAL_EVALUATION_SET es vacía. Trivialmente satisfecha.

---

## 4. LIMITACIONES CONOCIDAS Y VINCULACIÓN CON HALLAZGOS PREVIOS

| Hallazgo | Relación con Wave 3.1 |
|:---|:---|
| H-5.2-1 (doc_06_johnstone excluido) | El corpus de 6 docs es el resultado de la exclusión de doc_06. Si se re-incorpora con OCR, el corpus sería 7 docs, aún < 20. La recalibración local sigue siendo necesaria. |
| H-5.1-9, H-5.1-10 (limitaciones de PyMuPDF) | Los GTs sellados reflejan las limitaciones del extractor (fragmentación de ecuaciones, labels de gráficos). La calibración futura debe considerar estas limitaciones como factores conocidos. |
| H-5.2-6 (ASTFingerprintPolicy .strip()) | El tooling experimental aplica .strip(). El dominio canónico no. La calibración futura debe usar exclusivamente el dominio canónico (DefaultNodeMatchingPolicy, CriticalityAwareCostContext). |
| DF-04 (divergencia ZhangShasha vs APTED) | Divergencia 8.56% documentada. APTED queda como experimental no-normativo. La calibración futura usa exclusivamente ZhangShashaEngine como motor canónico (NADR-22 §5.1 R3). |

---

## 5. PROTOCOLO FUTURO (cuando el corpus sea ≥ 20)

Cuando el corpus canónico alcance 20 o más documentos diversos, se ejecutará el protocolo de calibración empírica conforme a NADR-23 §5.2:

### 5.1 Metodología

1. Curva Precision-Recall: para cada threshold t en [0, 1], calcular precision(t) y recall(t). Identificar el threshold que maximiza F1-score o el trade-off deseado.
2. Bootstrap confidence intervals: resampling con reemplazo para estimar intervalos de confianza del threshold óptimo.
3. Human verdicts: anotación experta de PASS/WARNING/HARD_FAIL por documento como ground truth observable.
4. Learning curves: entrenar con subconjuntos crecientes y medir mejora (metodología prescrita por GROBID: "Use learning curves").

### 5.2 Requisitos

- Corpus con 20 o más documentos diversos (papers IEEE, doble columna, libros, tablas, figuras, ecuaciones, código)
- Ground truths sellados para todos los documentos
- Múltiples ejecuciones del pipeline con variaciones controladas
- Protocolo aprobado antes de la ejecución (NADR-23 R4-R7)

### 5.3 Parámetros a calibrar

| Parámetro | Default actual | Tipo |
|:---|:---:|:---|
| nss_hard_fail | 0.80 | Threshold de NSS |
| nss_warning | 0.95 | Threshold de NSS |
| cost_weights CRITICAL | 5.0 | Peso de criticidad |
| cost_weights WARNING | 2.0 | Peso de criticidad |
| cost_weights INFO | 1.0 | Peso de criticidad |
| warning_threshold | 1 | FNs WARNING mínimos |

---

## 6. HALLAZGO ASOCIADO

**H-5.3-1** (ACCEPTED_LIMITATION): Calibración estadística no ejecutable con 6 documentos.

Ver Findings Register para clasificación completa.

---

## 7. TRAZABILIDAD

| Task | Descripción | Estado |
|:---|:---|:---:|
| 3.1.1 | Definición de CAL/VAL/FINAL como fases secuenciales | DONE |
| 3.1.2 | Partición por content identity (SHA-256) | DONE |
| 3.1.3 | Verificación de disjunción Calibration ∩ Final = ∅ | DONE |
| 3.1.4 | Estrategia de independencia estadística documentada | DONE |

---

**Nota de Gobernanza:** Este documento es el registro de la estrategia de partición de datasets para Gate 3. No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs. Su propósito es documentar la decisión de partición y la justificación normativa conforme a NADR-23 §5.3 R12 y §5.7 R28.
