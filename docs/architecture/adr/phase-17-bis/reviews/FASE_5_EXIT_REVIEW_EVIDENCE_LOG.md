# FASE_5_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 0.8.0
**Estado:** IN_PROGRESS
**Fecha:** 2026-09-05
**Última actualización:** 2026-09-10
**Derivado de:** `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.2.2 — Gates 1-5 Exit Reviews
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante los Gate Exit Reviews de Fase 5 (Baseline Certification). Cada finding
incluye los archivos auditados, el análisis, los gaps confirmados, la justificación
normativa y la clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-09-05 | Emisión inicial del esqueleto dinámico. Documento vacío, listo para recibir evidencia forense durante la ejecución de los Gate Exit Reviews. |
| 0.2.0 | 2026-09-06 | Wave 1.1 completada: 4 hallazgos derivados identificados (H-5.1-1 a H-5.1-4) y registrados como referencia de trazabilidad en §5.2. La evidencia forense formal se registrará en §2 durante el Gate 1 Exit Review. |
| 0.3.0 | 2026-09-06 | **Wave 1.2 completada:** (1) H-5.1-4 reclasificado de PENDING_REVIEW a RESOLVED — traits reclasificados con nombres correctos del catálogo vigente (scanned_noise, heavy_math, nested_tables, floating_figures); (2) H-5.1-5 registrado y RESOLVED — discrepancia de nombres de traits (DENSE_TYPOGRAPHY y MIXED_CONTENT no existen en catálogo; HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise); (3) H-5.1-6 registrado y CLOSED (NAR) — contrato del manifest verificado como 6D plano en RawDocumentEntryDTO; (4) Manifest canónico generado y verificado con BootstrapCorpusManifestUseCase (hash 62f0df16). |
| 0.4.0 | 2026-09-09 | **Wave 1.3 completada:** (1) H-5.1-2 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — archivo temporal tmptu237h6p eliminado en Task 1.3.1; (2) H-5.1-3 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — AST legacy reemplazado por re-extracción post-recorte en Task 1.3.8; (3) H-5.1-7 registrado y RESOLVED — parent_node_id=None consistente con Flat Design, verificado en curaduría; (4) H-5.1-8 registrado y CLOSED (NAR) — ManifestFingerprintCalculator incluye page_count (verificado en source code); (5) H-5.1-9 registrado como ACCEPTED_LIMITATION — doc_02_double: fragmentación de ecuaciones por PyMuPDF en doble columna; (6) H-5.1-10 registrado como ACCEPTED_LIMITATION — doc_05_graph: labels de ejes como paragraphs; (7) H-5.1-11 registrado como RECLASSIFIED_FUTURE_PHASE — patrón Detect & Placeholder, fuera del scope de Fase 17-BIS (ADR §4); (8) Curation Report generado en reviews/. |
| 0.5.0 | 2026-09-09 | **Wave 2.1 completada:** (1) H-5.2-1 registrado como IMPLEMENTATION_REQUIRED — doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6 (Zero Partial Sealing), requiere re-incorporación con pipeline OCR; (2) H-5.2-2 registrado y CLOSED (NAR) — GroundTruthLifecycleState tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED), diseño type-state confirmado por tests; (3) GAP-5.2-05 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — sanitize_ground_truth_types.py protegido con SealedOracleOverwriteError (fail-hard), 3 tests nuevos; (4) Gate 2 Exit Review estado actualizado a IN_PROGRESS; (5) Baseline tests: 627 passed, 5 skipped. |
| 0.6.0 | 2026-09-09 | **Wave 2.2 completada:** (1) H-5.2-3 registrado y RESOLVED — canonicalization_lineage.json movido de ground_truth/ a canonical/ raíz (separación de concerns, ground_truth/ solo contiene GTs); (2) H-5.2-4 registrado y RESOLVED — freeze_ground_truth.py path corregido de benchmark_v1 a canonical; (3) H-5.2-5 registrado y CLOSED (NAR) — log duplicado eliminado de freeze_ground_truth.py; (4) DF-19 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — manifest en formato 6D sellado con oracle_hash y ground_truth_state; (5) Sellado ejecutado: manifest_hash 0fda7690, 6/6 GTs sellados, MIG-02 y MIG-06 ejecutados; (6) Corrección de inconsistencia: header Última actualización 2026-09-05 → 2026-09-09. |
| 0.7.0 | 2026-09-09 | **Wave 2.3 completada:** (1) H-5.2-6 registrado como ACCEPTED_LIMITATION — ASTFingerprintPolicy.semantic_fingerprint() e identity_fingerprint() aplican .strip() violando NADR-22 §5.3 R10-R12, pero la divergencia está confinada al tooling experimental (tools/evaluation/topology/); la ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no usa ASTFingerprintPolicy ni aplica .strip(); (2) Task 2.3.1 completada por construcción: ZhangShashaEngine en composition root, APTED aislado en tools/ como experimental; (3) Task 2.3.2 completada por construcción: DEFAULT_CRITICALITY_WEIGHTS = CRITICAL 5.0, WARNING 2.0, INFO 1.0; run_regression.py pasa CriticalityAwareCostContext explícitamente; decisión: default del composition root permanece UnitCostContext (Explicit over Implicit + YAGNI); (4) Gate 2 Exit Review actualizado: 10/17 Tasks DONE. |
| 0.8.0 | 2026-09-10 | **Wave 2.4 completada, Gate 2 COMPLETED:** (1) DF-04 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — benchmark ejecutado con run_df04_benchmark.py sobre 6 documentos del corpus canónico sellado; divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double); 4 causas raíz documentadas (cost model diferente, normalización diferente, fingerprint diferente H-5.2-6, estructura de árbol diferente); APTED queda como experimental no-normativo (NADR-22 §5.1 R3); evidencia forense en reports/df04/df04_benchmark.{json,md}; (2) Task 2.4.3 implementada: ConfigurationFingerprintCalculator con module.qualname, 12 tests nuevos; (3) Task 2.4.5 implementada: configuration_fingerprint propagado en RegressionReport y run_regression.py; (4) Task 2.4.6 completada: 6 tests de determinismo PASSED; (5) Tasks 2.4.1, 2.4.2, 2.4.4 completadas por construcción; (6) Gate 2 → COMPLETED (17/17 Tasks, 43/43 rules). |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_05 > NADR-F17BIS-20..24 > PHASE_17BIS_FASE5_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Scientific Baseline sea una
> representación determinista, reproducible y arquitectónicamente fiel del
> pipeline productivo que vamos a certificar?"*

### 0.3 Reglas transversales aplicables

- **Zero Partial Sealing** — `ADR_F17_BIS_MASTER §5`
- **Determinismo y Reproducibilidad** — `ADR_F17_BIS_MASTER §5`
- **Desacoplamiento de Identidades** — `ADR_F17_BIS_MASTER §5`
- **Cero Fallos Silenciosos** — `ENGINEERING_PRINCIPLES §IV`
- **Trazabilidad Absoluta** — `ENGINEERING_PRINCIPLES §IV`
- **Inmutabilidad de Sealed** — `NADR-F17BIS-21 §5.4 R19`, `NADR-F17BIS-24 §5.6 R25`
- **Calibration ≠ Evaluation** — `NADR-F17BIS-23 §5.1 R2`

### 0.4 Corolario forense

> *Un finding solo es válido si puede demostrarse mediante evidencia de código,
> artefacto, test, reporte o documento congelado. Un indicio —nombre de archivo,
> comentario, convención informal o sospecha— no constituye evidencia suficiente
> para clasificar un finding como gap confirmado.*

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-5.{N}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF en Fase 5 |
| `GAP-5.{N}-{XX}` | Gap heredado de HITO | Gap pre-identificado durante auditorías/hitos previos de Fase 5 |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `RESOLVED — MIGRATION` | Artefacto migrado a formato vigente |
| `RESOLVED — CONFIGURATION` | Configuración explícita implementada |
| `RESOLVED — FAILURE SEMANTICS` | Semántica de fallo/exit codes corregida |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida y documentada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

```text
1. ¿Sigue siendo válido el hallazgo?
   → NO: CLOSED (NAR)
   → SÍ: continuar

2. ¿Existe evidencia suficiente?
   → NO: REVIEW_REQUIRED
   → SÍ: continuar

3. ¿Puede resolverse dentro del Gate actual?
   → SÍ: RESOLVED
   → NO: continuar

4. ¿Es un problema técnico?
   → SÍ: RECLASIFICADO a Gate futuro / IMPLEMENTATION_REQUIRED
   → NO: continuar

5. ¿Es un conflicto normativo?
   → SÍ: CONVERTIDO EN GF
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. ESTRUCTURA POR FINDING

{Se agregan dinámicamente conforme se ejecutan los Gate Exit Reviews.
Cada finding analizado recibe una sub-sección con la siguiente estructura.}

---

## 3. GATE EXIT REVIEW SUMMARY

{Se agregan dinámicamente conforme se ejecutan los Gates del Execution Plan.}

### 3.1 Gate 1 Exit Review — Canonical Corpus & GT Qualification

**Estado:** 🟡 IN PROGRESS — Waves 1.1, 1.2 y 1.3 completadas (17/18 Tasks DONE). Task 1.1.5 pendiente (déficit de 13 documentos bloquea Exit Criteria).
**Fecha:** 2026-09-06 (inicio)

### 3.2 Gate 2 Exit Review — GT Sealing & Canonical Evaluation Configuration

**Estado:** ✅ COMPLETED — Waves 2.1, 2.2, 2.3 y 2.4 completadas (17/17 Tasks DONE). Gate 2 cerrado el 2026-09-10.
**Fecha:** 2026-09-09 (inicio), 2026-09-10 (cierre)

### 3.3 Gate 3 Exit Review — Scientific Calibration & Experimental Provenance

**Estado:** ⏳ PENDING — Gate 3 no ha iniciado.
**Fecha:** —

### 3.4 Gate 4 Exit Review — Certification Tooling & Execution Safety

**Estado:** ⏳ PENDING — Gate 4 no ha iniciado.
**Fecha:** —

### 3.5 Gate 5 Exit Review — End-to-End Certification & Baseline Freeze

**Estado:** ⏳ PENDING — Gate 5 no ha iniciado.
**Fecha:** —

---

## 4. TABLA CONSOLIDADA FINAL

{Se completa al cierre del último Gate Exit Review.}

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| — | — | — |

---

## 5. HALLAZGOS PRE-IDENTIFICADOS (REFERENCIA DE TRAZABILIDAD)

Los siguientes hallazgos fueron identificados en HITOs anteriores y/o en el
Execution Plan. Se registran aquí **únicamente como referencia de trazabilidad**.
La evidencia forense que justifica su clasificación se construirá durante los
Gate Exit Reviews correspondientes, aplicando el árbol de decisión de §1.4.

> **Nota:** La existencia de estos hallazgos como carry-forward no implica que
> su evidencia forense esté completa. El análisis detallado (archivos auditados,
> gaps confirmados, sub-acciones, regla aplicada) se registra en §2 cuando se
> ejecute el Gate Exit Review correspondiente.

### 5.1 Carry-forwards de Fase 4 — no bloquean Fase 5

| ID | Descripción | Estado preliminar | Destino | Fuente |
|----|-------------|-------------------|---------|--------|
| DF-01 | Tests tautológicos | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 | FASE_4_HANDOFF |
| DF-02 | Verificación ci.yml/pyproject.toml | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 | FASE_4_HANDOFF |
| DF-03 | Deuda LayoutBlockDraft | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Gate futuro | FASE_4_HANDOFF |

### 5.2 Hallazgos activos de Fase 5 — pendientes de evidencia forense

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo ejecutado con run_df04_benchmark.py sobre 6 documentos del corpus canónico sellado. Divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double). Desglose: doc_01_single (12.14%), doc_02_double (22.63%), doc_03_math (0.62%), doc_04_table (13.08%), doc_05_graph (2.88%), doc_07_pesaran (0.00%). Cuatro causas raíz identificadas: (1) cost model diferente (APTED penaliza sustituciones diff-type 2× más: 2.0 vs 1.0), (2) normalización diferente (MaxBound vs del×|GT|+ins×|Cand|), (3) fingerprint diferente (H-5.2-6: APTED usa .strip()), (4) estructura de árbol diferente (APTED reconstruye jerarquía vía parent_node_id). Patrón 1: APTED consistentemente más severo en 4/6 documentos. Patrón 2: divergencia alta en docs con estructura compleja. Patrón 3: coincidencia perfecta en casos triviales (doc_07_pesaran 0.00%, score 1.0 en ambos) valida correctitud de ambos motores. Decisión: APTED queda como experimental no-normativo conforme a NADR-22 §5.1 R3. Evidencia forense en reports/df04/df04_benchmark.{json,md}. | `RESOLVED` | Gate 2 W2.4 (investigación), Gate 5 W5.3 (cierre administrativo) | FASE_4_HANDOFF §5.2 → Resolución Wave 2.4 |
| DF-18 | Semántica de fallo heterogénea | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 4 W4.2 | HITO 5.2 |
| DF-19 | Manifest legacy 4D→6D. Tasks 1.2.3 (contrato) y 1.3.1 (ejecución de migración) completadas. Manifest sellado en formato 6D con oracle_hash y ground_truth_state='sealed' para los 6 documentos. | `RESOLVED` | Gate 1 W1.2 W1.3 (implementación); Gate 2 W2.2 (sellado) | HITO 5.1 → Resolución Wave 1.3 → Sellado Wave 2.2 |
| GAP-5.0-03 | Configuración implícita del corpus | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 4 W4.1 | HITO 5.0 |
| GAP-5.2-05 | Certification Boundary Integrity violation. Remediado en Task 2.1.2: sanitize_ground_truth_types.py protegido con SealedOracleOverwriteError (fail-hard). | `RESOLVED` | Gate 2 W2.1 T2.1.2 (remediación primaria); Gate 4 W4.3 T4.3.2 (verificación de boundary) | HITO 5.2 → Resolución Wave 2.1 |


### 5.2.1 Hallazgos derivados de Wave 1.1 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 1.1
(Corpus Discovery & Identity). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 1 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.1-1 | Discrepancia 7 vs 6 identidades (HITO 5.1). pesaran1999.pdf encontrado en datasets/raw/ e incluido como doc_07_pesaran.pdf (SHA-256: f1c80072). | `RESOLVED` | Gate 1 W1.1 T1.1.1 | Auditoría Wave 1.1 |
| H-5.1-2 | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en tests/corpus/calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | `RESOLVED` | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.1 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-3 | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy). Resuelto por re-extracción: PDF recortado a 3 páginas, GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente). | `RESOLVED` | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.8 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-4 | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Clasificación corregida en manifest canónico con nombres del catálogo vigente. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Inspección visual Wave 1.1 → Reclasificación Wave 1.2 |

> **Nota:** H-5.1-1 se marca como `RESOLVED` porque la identidad faltante fue
> encontrada e incluida en el corpus canónico durante Wave 1.1. La evidencia
> forense formal (SHA-256 verificado, archivos auditados) se registrará en §2
> durante el Gate 1 Exit Review.
>
> H-5.1-2 se marca como `RESOLVED` porque el archivo temporal fue eliminado
> durante Wave 1.3 (Task 1.3.1). La evidencia forense formal se registrará en §2
> durante el Gate 1 Exit Review.
>
> H-5.1-3 se marca como `RESOLVED` porque el AST legacy fue reemplazado por
> re-extracción durante Wave 1.3 (Task 1.3.8): PDF recortado a 3 páginas,
> GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente AST V2).
> La evidencia forense formal se registrará en §2 durante el Gate 1 Exit Review.
>
> H-5.1-4 se marca como `RESOLVED` porque la clasificación de traits fue corregida
> durante Wave 1.2 (Task 1.2.1) con los nombres correctos del catálogo vigente
> (ExtractionChallengeTrait). La evidencia forense formal se registrará en §2
> durante el Gate 1 Exit Review.


### 5.2.2 Hallazgos derivados de Wave 1.2 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 1.2
(Corpus Qualification & Manifest). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 1 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.1-5 | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). Nombres inexistentes: DENSE_TYPOGRAPHY, MIXED_CONTENT. Nombres corregidos: HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise. Reclasificación completada. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Auditoría Wave 1.2 |
| H-5.1-6 | Contrato del manifest verificado como 6D plano en RawDocumentEntryDTO (document_id, sha256, traits, page_count, ground_truth_state, oracle_hash). El sha256 está encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en el DTO de serialización. El contrato 6D es correcto. | `CLOSED (NAR)` | Gate 1 W1.2 T1.2.3 | Auditoría Wave 1.2 |

> **Nota:** H-5.1-5 se marca como `RESOLVED` porque la discrepancia fue identificada
> y corregida durante la misma Task (1.2.1). La reclasificación se completó contra
> el catálogo vigente (ExtractionChallengeTrait). La evidencia forense formal se
> registrará en §2 durante el Gate 1 Exit Review.
>
> H-5.1-6 se marca como `CLOSED (NAR)` porque la hipótesis (contrato NO es 6D plano)
> fue refutada: RawDocumentEntryDTO SÍ es 6D plano. El sha256 está encapsulado en
> DocumentFingerprint a nivel de dominio pero aplanado en el DTO de serialización.
> La evidencia forense formal se registrará en §2 durante el Gate 1 Exit Review.


### 5.2.3 Hallazgos derivados de Wave 1.3 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 1.3
(GT Migration & Eligibility). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 1 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.1-7 | Todos los parent_node_id son None en los 5 GTs canonicalizados. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II: secuencias lineales enriquecidas con metadatos topológicos). Verificado en curaduría manual. | `RESOLVED` | Gate 1 W1.3 T1.3.4 → T1.3.9 | Auditoría Wave 1.3 |
| H-5.1-8 | ManifestFingerprintCalculator.compute_hash() incluye page_count en el payload (verificado en source code: `f"{doc.page_count}:"`). Hash anterior coincidió por valor por defecto de Pydantic que igualó el valor real. | `CLOSED (NAR)` | Gate 1 W1.3 T1.3.1 | Auditoría Wave 1.3 |
| H-5.1-9 | doc_02_double: 52 nodos display_equation contienen fragmentos garbled (operadores/variables aislados: "+", "= = =", "p", "i t i i"). PyMuPDF no agrupa tokens matemáticos en layout de doble columna. GT fiel al extractor, no al documento fuente. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos vectoriales extraídos como paragraph individuales (ej. "–20", "0", "15"). Estructura del gráfico no capturada. Comportamiento esperado de PyMuPDF frente a gráficos vectoriales. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar la presencia y dejar placeholder para pegado manual. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4: no modificar extractores). | `RECLASSIFIED_FUTURE_PHASE` | Post Fase 17-BIS | Curaduría Wave 1.3 |

> **Nota:** H-5.1-7 se marca como `RESOLVED` porque la observación (parent_node_id=None)
> es consistente con el Flat Design definido en ENGINEERING_PRINCIPLES §II. La curaduría
> manual (Task 1.3.9) confirmó que los ASTs representan fielmente la estructura del
> documento fuente dentro de las capacidades del extractor. La evidencia forense formal
> se registrará en §2 durante el Gate 1 Exit Review.
>
> H-5.1-8 se marca como `CLOSED (NAR)` porque la inspección del source code de
> ManifestFingerprintCalculator.compute_hash() confirmó que page_count SÍ está incluido
> en el payload del hash. El hash anterior coincidió porque Pydantic asignó un valor
> por defecto que igualó el valor real (todos los documentos tenían page_count=3).
> La evidencia forense formal se registrará en §2 durante el Gate 1 Exit Review.
>
> H-5.1-9 y H-5.1-10 se marcan como `ACCEPTED_LIMITATION` porque documentan limitaciones
> conocidas de PyMuPDFProvider (fragmentación de ecuaciones en doble columna y ruido
> estructural en gráficos vectoriales). Los GTs son fieles a la salida del extractor
> de producción actual, aunque no al contenido real del documento fuente. Documentado
> en FASE_5_WAVE_1_3_CURATION_REPORT.md. La evidencia forense formal se registrará en §2
> durante el Gate 1 Exit Review.
>
> H-5.1-11 se marca como `RECLASSIFIED_FUTURE_PHASE` porque la implementación del patrón
> Detect & Placeholder requiere modificación de PyMuPDFProvider y nuevos tipos de nodo
> (placeholder), lo cual está fuera del scope de Fase 17-BIS según ADR F17_BIS_MASTER §4.
> Se documenta como candidato a decisión para una fase futura con ADR dedicado.
> La evidencia forense formal se registrará en §2 durante el Gate 1 Exit Review.


### 5.2.4 Hallazgos derivados de Wave 2.1 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 2.1
(GT Validation & Structural Integrity). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 2 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.2-1 | doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6 (Zero Partial Sealing). El documento tiene trait scanned_noise y requiere pipeline OCR no disponible. PDF físico preservado en canonical/pdf/ como evidencia (quarantine). Manifest hash recalculado: 39cc80bd → fae41bb5. Re-incorporación planificada junto con déficit de 13 documentos. | `IMPLEMENTATION_REQUIRED` | Gate 2 W2.1 (pre-requisito biyección) | Auditoría Wave 2.1 |
| H-5.2-2 | GroundTruthLifecycleState muestra 3 estados en inspección runtime pero tests esperan 4. Verificación: enum SÍ tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED). Tests test_four_states_with_canonical_values y test_exactly_four_states PASSED. Diseño type-state: SEALED se representa como tipo SealedOracle (no GroundTruthDraft con estado). | `CLOSED (NAR)` | Gate 2 W2.1 T2.1.1 | Auditoría Wave 2.1 |

> **Nota:** H-5.2-1 se marca como `IMPLEMENTATION_REQUIRED` porque la exclusión de
> doc_06_johnstone es una medida temporal para restaurar la biyección exigida por
> Zero Partial Sealing (ADR F17_BIS_MASTER §5). El documento debe ser re-incorporado
> cuando se disponga de un pipeline OCR funcional, junto con los 13 documentos del
> déficit. La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.
>
> H-5.2-2 se marca como `CLOSED (NAR)` porque la inspección inicial mostró 3 estados
> en runtime, pero los tests confirmaron que el enum SÍ tiene 4 estados. La discrepancia
> fue un artefacto de la inspección (el script iteró sobre el enum pero no mostró SEALED
> por razones de visualización). Los tests test_four_states_with_canonical_values y
> test_exactly_four_states PASSED confirman el diseño type-state correcto.
> La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.


### 5.2.5 Hallazgos derivados de Wave 2.2 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 2.2
(Zero Partial Sealing & Oracle Identity). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 2 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.2-3 | canonicalization_lineage.json estaba en ground_truth/ contaminando BaselineCompletenessVerifier como oráculo huérfano (el verificador detectó "Orphan oracle (not in manifest): canonicalization_lineage"). Movido a canonical/ raíz. Separación de concerns: ground_truth/ debe contener exclusivamente GTs (uno por documento). | `RESOLVED` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |
| H-5.2-4 | freeze_ground_truth.py apuntaba a tests/corpus/benchmark_v1/ en lugar de tests/corpus/canonical/. El entry point habría sellado un corpus inexistente o incorrecto. Path corregido a canonical/. | `RESOLVED` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |
| H-5.2-5 | Log duplicado en freeze_ground_truth.py (línea logger.info "Cryptographic lock complete..." repetida). Eliminado. No afecta funcionalidad ni integridad del sellado. | `CLOSED (NAR)` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |

> **Nota:** H-5.2-3 se marca como `RESOLVED` porque el archivo de trazabilidad
> (canonicalization_lineage.json, creado en Wave 1.3 Task 1.3.2) fue movido fuera
> del directorio ground_truth/ para restaurar la separación de concerns. El
> BaselineCompletenessVerifier detectó correctamente el oráculo huérfano, lo que
> confirma que el mecanismo de protección funciona. La evidencia forense formal
> se registrará en §2 durante el Gate 2 Exit Review.
>
> H-5.2-4 se marca como `RESOLVED` porque el path del entry point fue corregido
> de benchmark_v1 a canonical. Sin este fix, el sellado habría fallado con
> FileNotFoundError o habría operado sobre un corpus inexistente. La evidencia
> forense formal se registrará en §2 durante el Gate 2 Exit Review.
>
> H-5.2-5 se marca como `CLOSED (NAR)` porque el log duplicado no afectaba la
> funcionalidad del sellado ni la integridad de los datos. Es un hallazgo cosmético.
> La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.


### 5.2.6 Hallazgos derivados de Wave 2.3 — referencia de trazabilidad

Los siguientes hallazgos fueron identificados durante la ejecución de Wave 2.3
(Canonical Engine Composition). Se registran aquí como referencia de trazabilidad.
La evidencia forense formal (archivos auditados, análisis, gaps confirmados,
regla aplicada) se registrará en §2 durante el Gate 2 Exit Review.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| H-5.2-6 | ASTFingerprintPolicy.semantic_fingerprint() aplica node.text_content.strip() e identity_fingerprint() aplica str(content).strip(), violando NADR-22 §5.3 R10-R12 (normalización sin .strip(), sin fingerprint). Sin embargo, la divergencia está confinada al tooling experimental (tools/evaluation/topology/). La ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no usa ASTFingerprintPolicy. El dominio canónico (DefaultNodeMatchingPolicy, CriticalityAwareCostContext) no aplica .strip(). | `ACCEPTED_LIMITATION` | Gate 2 W2.3 T2.3.3 | AUDIT Wave 2.3 |

> **Nota:** H-5.2-6 se marca como `ACCEPTED_LIMITATION` porque:
> (1) ASTFingerprintPolicy está en tools/evaluation/topology/fingerprint.py (tooling experimental);
> (2) los únicos usuarios son EntityRecallMetric, SequenceAlignmentMetric y StructuralTopologyMetric, todos en tools/evaluation/topology/metrics/;
> (3) la ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no importa ni usa ASTFingerprintPolicy;
> (4) el dominio canónico (DefaultNodeMatchingPolicy.match(), CriticalityAwareCostContext.substitution_cost()) usa comparación exacta de text_content sin normalización destructiva;
> (5) modificar ASTFingerprintPolicy podría romper tests del tooling experimental sin beneficio para la certificación.
> Se documenta como deuda técnica para Fase 6 (mejora del tooling de evaluación).
> La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.

### 5.2.7 Hallazgos derivados de Wave 2.4 — referencia de trazabilidad

Wave 2.4 (Engine Configuration Freeze & Verification) no generó nuevos hallazgos derivados (H-5.2-X). El hallazgo pre-identificado DF-04 fue resuelto con evidencia empírica completa.

| ID | Descripción | Estado preliminar | Gate destino | Fuente |
|----|-------------|-------------------|--------------|--------|
| DF-04 | Benchmark comparativo ZhangShasha vs APTED ejecutado sobre 6 documentos del corpus canónico sellado. Divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double). Cuatro causas raíz identificadas y documentadas: (1) cost model diferente (APTED penaliza sustituciones diff-type 2× más), (2) normalización diferente, (3) fingerprint diferente (H-5.2-6), (4) estructura de árbol diferente. APTED queda como experimental no-normativo (NADR-22 §5.1 R3). Evidencia forense en reports/df04/df04_benchmark.{json,md}. | `RESOLVED` | Gate 2 W2.4 T2.4.7 (investigación), Gate 5 W5.3 T5.3.3 (cierre administrativo) | Benchmark DF-04 Wave 2.4 |

> **Nota:** DF-04 se marca como `RESOLVED` porque el benchmark fue ejecutado,
> las cuatro causas raíz fueron identificadas y documentadas, y la decisión
> normativa (APTED como experimental no-normativo) fue aplicada conforme a
> NADR-22 §5.1 R3. La evidencia forense completa está en reports/df04/df04_benchmark.{json,md}.
> El criterio DF-04 fue aplicado correctamente: divergencia ≥ 1%, causa raíz investigada y documentada.
> Cierre administrativo pendiente en Gate 5 Task 5.3.3 (documentación final).

---

## 6. CRITERIOS DE CIERRE

### 6.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [ ] Todos los hallazgos del Execution Plan tienen evidencia forense registrada en §2
- [ ] Ningún hallazgo está en estado `PENDING_REVIEW`
- [ ] La tabla consolidada final (§4) está completa
- [ ] Cada clasificación tiene al menos una regla normativa aplicada
- [ ] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [ ] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación
- [ ] Los 5 Gate Exit Reviews (§3) están ejecutados y documentados
- [ ] No hay hallazgos bloqueantes abiertos en Gate 5

### 6.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

## 7. PLANTILLA PARA NUEVOS FINDINGS

Cuando se identifique un hallazgo durante un Gate Exit Review, se agrega una
sub-sección en §2 con la siguiente estructura:

```text
### {N} {DF/GF}-{XX} — {Título corto del hallazgo}

| Campo | Valor |
|-------|-------|
| ID | {DF/GF}-{XX} |
| Tipo | {Deferred Finding / Governance Finding / Hallazgo derivado} |
| Estado | {Clasificación final} |
| Origen | {Wave/Task/Gate donde se identificó} |
| Gate destino original | {Gate original} |
| Estado previo | {Estado anterior si fue reclasificado} |
| Prioridad | {Baja / Media / Alta / Critical / N/A} |
| ¿Requiere implementación? | {Sí/No — con alcance si aplica} |
| ¿Bloquea la certificación? | {Sí/No/Condicional} |

#### {N}.1 Texto original del DF
> {Texto exacto del hallazgo tal como fue registrado}

#### {N}.2 Reformulación corregida (si aplica)
{Reformulación o "No requiere reformulación"}

#### {N}.3 Archivos y documentos auditados
| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | {ruta} | {Evidencia} |

#### {N}.4 Análisis
{Análisis detallado}

#### {N}.5 Gaps objetivos confirmados (si aplica)
| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | {Gap} | {Evidencia} | {Severidad} |

#### {N}.6 Lo que NO es un gap
| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| {Aspecto} | {Veredicto} | {Justificación} |

#### {N}.7 Impacto en la certificación
| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | {Sí/No/Parcial} | {Justificación} |
| Reproducibilidad | {Sí/No/Parcial} | {Justificación} |
| Corrección funcional | {Sí/No/Parcial} | {Justificación} |
| Bloquea la certificación | {Sí/No/Condicional} | {Justificación} |

#### {N}.8 Sub-acciones identificadas (si aplica)
| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| {DF}-{XX}-A | {Descripción} | {Estado} | {Scope} |

#### {N}.9 Clasificación consolidada
| Campo | Valor |
|-------|-------|
| Condición original existe | {Sí/No/Parcialmente} |
| Es violación arquitectónica | {Sí/No} |
| Es violación de gobernanza | {Sí/No} |
| Es problema técnico | {Sí/No} |
| Pertenece a Fase 5 | {Sí/No} |
| Bloquea la certificación | {Sí/No/Condicional} |
| Clasificación | {ESTADO_FINAL} |
| Prioridad | {Baja/Media/Alta/Critical} |

#### {N}.10 Regla aplicada
> {NADR/ADR/ENGINEERING_PRINCIPLES} §{N} ({Nombre}):
> "{Cita textual de la regla}"
{Explicación de cómo la regla aplica al caso concreto.}
```

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones. La evidencia se construye durante los
Gate Exit Reviews, no antes.