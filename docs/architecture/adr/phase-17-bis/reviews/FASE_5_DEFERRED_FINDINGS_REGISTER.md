# FASE_5_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.6.0
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-09-05
**Última actualización:** 2026-09-05
**Derivado de:** `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.2.2
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de Fase 5 (Baseline Certification), su clasificación, resolución y
evidencia empírica de los batches.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-09-05 | Emisión inicial. Esqueleto con hallazgos pre-registrados. |
| 0.2.0 | 2026-09-05 | Hardening documental: expansión de marco normativo, estados de evidencia, árbol de decisión, mapeo Finding→Task, plantillas. |
| 0.3.0 | 2026-09-05 | **Conversión a esqueleto dinámico de descubrimiento.** Se eliminan análisis detallados pre-escritos. Las secciones dinámicas (§2, §3, §4) quedan vacías, listas para recibir evidencia durante los Gate Exit Reviews. Los hallazgos pre-identificados (§9) se conservan únicamente como referencia de trazabilidad. |
| 0.4.0 | 2026-09-06 | **Wave 1.1 completada:** 4 hallazgos derivados registrados (H-5.1-1 a H-5.1-4). H-5.1-1 RESOLVED (pesaran1999.pdf encontrado e incluido como doc_07). H-5.1-2, H-5.1-3 IMPLEMENTATION_REQUIRED. H-5.1-4 PENDING_REVIEW. Métricas actualizadas. |
| 0.5.0 | 2026-09-06 | **Wave 1.2 completada:** (1) H-5.1-4 reclasificado de PENDING_REVIEW a RESOLVED — traits reclasificados con nombres correctos del catálogo vigente (scanned_noise, heavy_math, nested_tables, floating_figures); (2) H-5.1-5 registrado y RESOLVED — discrepancia de nombres de traits (DENSE_TYPOGRAPHY y MIXED_CONTENT no existen; HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise); (3) H-5.1-6 registrado y CLOSED (NAR) — contrato del manifest verificado como 6D plano en RawDocumentEntryDTO; (4) Manifest canónico generado y verificado (hash 62f0df16); (5) Métricas y estado actualizados. |
| 0.6.0 | 2026-09-09 | **Wave 1.3 completada:** (1) H-5.1-2 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — archivo temporal tmptu237h6p eliminado en Task 1.3.1; (2) H-5.1-3 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — AST legacy reemplazado por re-extracción en Task 1.3.8; (3) H-5.1-7 registrado y RESOLVED — parent_node_id=None en todos los GTs, consistente con Flat Design, verificado en curaduría; (4) H-5.1-8 registrado y CLOSED (NAR) — ManifestFingerprintCalculator.compute_hash() incluye page_count (verificado en source code); (5) H-5.1-9 registrado como ACCEPTED_LIMITATION — doc_02_double: fragmentación de ecuaciones por PyMuPDF en doble columna; (6) H-5.1-10 registrado como ACCEPTED_LIMITATION — doc_05_graph: labels de ejes como paragraphs; (7) H-5.1-11 registrado como RECLASSIFIED_FUTURE_PHASE — patrón Detect & Placeholder, fuera del scope de Fase 17-BIS (ADR §4); (8) Métricas y estado actualizados. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_05 > NADR-F17BIS-20..24 > PHASE_17BIS_FASE5_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

Este registro no tiene autoridad normativa. Su función es operacional:
documentar hallazgos, clasificaciones, resoluciones, batches y evidencia.

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Scientific Baseline sea una
> representación determinista, reproducible y arquitectónicamente fiel del
> pipeline productivo que vamos a certificar?"*

Sub-preguntas aplicables durante la revisión:

- ¿El finding compromete la inmutabilidad de un Ground Truth sellado?
- ¿El finding compromete la biyección PDF↔oráculo exigida por Zero Partial Sealing?
- ¿El finding compromete el determinismo de serialización, evaluación o hashing?
- ¿El finding permite un fallo silencioso, un falso PASS o un exit code incorrecto?
- ¿El finding mezcla identidades que deben permanecer desacopladas?
- ¿El finding mezcla datos de calibración con datos de evaluación final?
- ¿El finding impide auditar el linaje del corpus, oráculo, configuración o parámetros?
- ¿El finding contradice una decisión congelada en ADR/NADR?

### 0.3 Reglas transversales aplicables

- **Zero Partial Sealing** — `ADR_F17_BIS_MASTER §5`: Un corpus NO podrá entrar en estado `SEALED` si no existe una correspondencia biyectiva completa entre los PDFs declarados y sus oráculos AST auditados ($N_{\text{PDF}} = N_{\text{GT}}$).
- **Determinismo y Reproducibilidad** — `ADR_F17_BIS_MASTER §5`: Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser determinista.
- **Desacoplamiento de Identidades** — `ADR_F17_BIS_MASTER §5`: La arquitectura debe mantener diferenciados los conceptos de AST Schema Version, Corpus Version, Identity Hash, Oracle Hash, Baseline Hash, Parameter Identity y Evaluation Configuration Identity.
- **Cero Fallos Silenciosos** — `ENGINEERING_PRINCIPLES §IV`: Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un warning indexable explícito o fallar duro.
- **Trazabilidad Absoluta** — `ENGINEERING_PRINCIPLES §IV`: El linaje del dato debe propagarse intacto a través de todas las transformaciones del pipeline.
- **Calidad sobre Velocidad** — `ENGINEERING_PRINCIPLES`: No se acepta deuda técnica deliberada en dominio core.
- **Cero Sesgo de Confirmación** — `ENGINEERING_PRINCIPLES`: Las decisiones de clasificación deben basarse en evidencia, invariantes comprobables y métricas.
- **Inmutabilidad de Sealed** — `NADR-F17BIS-21 §5.4 R19`, `NADR-F17BIS-24 §5.6 R25`: Un Ground Truth en estado `SEALED` no debe modificarse, sobrescribirse ni eliminarse. No existe rollback mutativo post-sealing.
- **Calibration ≠ Evaluation** — `NADR-F17BIS-23 §5.1 R2`: Los resultados de FINAL EVALUATION no deben participar en la selección, ajuste o justificación de parámetros.

### 0.4 Corolario forense

> *Un finding solo es válido si puede demostrarse mediante evidencia de código,
> artefacto, test, reporte o documento congelado. Un indicio —nombre de archivo,
> comentario, convención informal o sospecha— no constituye evidencia suficiente
> para clasificar un finding como gap confirmado.*

Implicaciones:

- Todo finding debe clasificar explícitamente su estado de evidencia: `gap confirmado`, `hipótesis pendiente`, `no-gap`.
- Ningún finding puede cerrarse como `RESOLVED` sin evidencia empírica.
- Ningún finding puede convertirse en `GF` sin citar la contradicción normativa exacta entre niveles de gobernanza.
- Ningún finding puede justificar mutación in-place de un artefacto sellado.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-5.{N}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF en Fase 5 |
| `GAP-5.{N}-{XX}` | Gap heredado de HITO | Gap pre-identificado durante auditorías/hitos previos de Fase 5 |

Notas:

- Los `DF-01`, `DF-02` y `DF-03` son carry-forwards de Fase 4 y no bloquean Fase 5.
- Los hallazgos activos que afectan Fase 5 son: `DF-04`, `DF-18`, `DF-19`, `GAP-5.0-03`, `GAP-5.2-05`.
- Los IDs nuevos generados durante Fase 5 deben asignarse secuencialmente a partir del siguiente identificador disponible.

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `PENDING_REVIEW` | Identificado, pendiente de clasificación |
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `RESOLVED — MIGRATION` | Artefacto migrado a formato vigente |
| `RESOLVED — CONFIGURATION` | Configuración explícita implementada |
| `RESOLVED — FAILURE SEMANTICS` | Semántica de fallo/exit codes corregida |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Diferido a fase futura con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación dentro del scope de Fase 5 |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `CONVERTED_TO_GF` | Convertido en Governance Finding |
| `DEFERRED — FASE {X}` | Diferido a fase específica con ADR pendiente |

### 1.3 Estados de evidencia

| Estado | Significado |
|--------|-------------|
| `GAP_CONFIRMED` | Gap confirmado con evidencia |
| `HYPOTHESIS_PENDING` | Hipótesis plausible, pendiente de evidencia |
| `NO_GAP` | No hay gap; correcto por diseño o falso positivo |
| `PARTIAL_GAP` | Gap parcialmente confirmado o acotado |
| `GOVERNANCE_CONFLICT` | Conflicto entre niveles normativos |

### 1.4 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos, tests, documentos o artefactos auditados.
- Cada finding **DEBE** distinguir: gap confirmado, hipótesis pendiente, no-gap, limitación aceptada.
- Ningún finding se cierra sin evidencia de código, test, artefacto o documento.
- No se implementa código durante el Gate Exit Review. La implementación se agrupa en batches posteriores.
- Todo finding que involucre un oráculo sellado **DEBE** verificar que no se propone mutación in-place.
- Todo finding que implique cambios normativos **DEBE** convertirse en `GF`.
- Todo finding diferido a fase futura **DEBE** tener destino explícito y justificación.

### 1.5 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Hallazgo validado | Actualizar Evidence Status (`GAP_CONFIRMED`, `NO_GAP`, etc.) |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación planificado | Asociar findings a batch |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Hallazgo convertido en GF | Crear entrada `GF-{XX}` y referenciar DF original |
| Fase cerrada | Estado del documento → `ARCHIVED` |

---

## 2. GATE EXIT REVIEWS

Los Gate Exit Reviews se agregan dinámicamente conforme se ejecutan los Gates del
Execution Plan. Cada Exit Review aplica el árbol de decisión estándar y registra
las decisiones tomadas sobre los hallazgos pre-identificados y los nuevos
hallazgos descubiertos durante la implementación.

### Árbol de decisión estándar

```text
1. ¿Sigue siendo válido el hallazgo?
   ├── NO  → CLOSED (NAR)
   └── SÍ  → continuar

2. ¿Existe evidencia suficiente?
   ├── NO  → REVIEW_REQUIRED
   └── SÍ  → continuar

3. ¿Es un problema técnico resoluble dentro del scope del Gate/Fase?
   ├── SÍ  → IMPLEMENTATION_REQUIRED / RESOLVED
   └── NO  → continuar

4. ¿Es un conflicto normativo entre niveles de gobernanza?
   ├── SÍ  → CONVERTED_TO_GF
   └── NO  → continuar

5. ¿Debe diferirse a fase futura?
   ├── SÍ  → RECLASSIFIED_FUTURE_PHASE / DEFERRED — FASE {X}
   └── NO  → ACCEPTED_LIMITATION o REVIEW_REQUIRED
```

### 2.1 Gate 1 Exit Review — Canonical Corpus & Ground Truth Qualification

**Estado:** ⏳ PENDING — Gate 1 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 1 / Waves 1.1, 1.2, 1.3
**Hallazgos pre-asignados:** DF-19

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 1 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 1

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

### 2.2 Gate 2 Exit Review — GT Sealing & Canonical Evaluation Configuration

**Estado:** ⏳ PENDING — Gate 2 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 2 / Waves 2.1, 2.2, 2.3, 2.4
**Hallazgos pre-asignados:** GAP-5.2-05, DF-04

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 2 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 2

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

### 2.3 Gate 3 Exit Review — Scientific Calibration & Experimental Provenance

**Estado:** ⏳ PENDING — Gate 3 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 3 / Waves 3.1, 3.2, 3.3
**Hallazgos pre-asignados:** —

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 3 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 3

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

### 2.4 Gate 4 Exit Review — Certification Tooling & Execution Safety

**Estado:** ⏳ PENDING — Gate 4 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 4 / Waves 4.1, 4.2, 4.3, 4.4
**Hallazgos pre-asignados:** GAP-5.0-03, DF-18, GAP-5.2-05

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 4 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 4

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

### 2.5 Gate 5 Exit Review — End-to-End Certification & Baseline Freeze

**Estado:** ⏳ PENDING — Gate 5 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 5 / Waves 5.1, 5.2, 5.3
**Hallazgos pre-asignados:** DF-04 (cierre administrativo)

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 5 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 5

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs/GAPs |
|--------------|----------|----------|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED` (cualquier subtipo) | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |
| `CONVERTED_TO_GF` | 0 | — |

### 3.2 Tabla consolidada

| ID | Estado | Evidence Status | Decisión |
|----|--------|-----------------|----------|
| — | — | — | Pendiente de cierre de los Gate Exit Reviews |

### 3.3 Hallazgos identificados durante implementación

| ID | Estado | Evidence Status | Descripción | Gate/Wave/Task | Fecha |
|----|--------|-----------------|-------------|----------------|-------|
| H-5.1-1 | RESOLVED | GAP_CONFIRMED | Discrepancia 7 vs 6 identidades (HITO 5.1). La identidad faltante (pesaran1999.pdf) estaba en datasets/raw/, fuera de tests/corpus/. Encontrada e incluida como doc_07_pesaran.pdf. SHA-256: f1c80072. | Gate 1 W1.1 T1.1.1 | 2026-09-06 |
| H-5.1-2 | RESOLVED | GAP_CONFIRMED | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en tests/corpus/calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.1 | 2026-09-09 |
| H-5.1-3 | RESOLVED | GAP_CONFIRMED | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy, content en lugar de payload.content). Resuelto por re-extracción en Task 1.3.8: PDF recortado a 3 páginas, GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente). | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.8 | 2026-09-09 |
| H-5.1-4 | RESOLVED | GAP_CONFIRMED | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Inspección visual confirmó PDFs escaneados. Clasificación corregida en manifest canónico con nombres del catálogo vigente. | Gate 1 W1.1 T1.1.1 → W1.2 T1.2.1 | 2026-09-06 |
| H-5.1-5 | RESOLVED | GAP_CONFIRMED | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). Nombres inexistentes: DENSE_TYPOGRAPHY, MIXED_CONTENT. Nombres corregidos: HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise. Reclasificación completada. | Gate 1 W1.2 T1.2.1 | 2026-09-06 |
| H-5.1-6 | CLOSED (NAR) | NO_GAP | Hipótesis: contrato del manifest NO es 6 campos planos. Verificación: RawDocumentEntryDTO SÍ es 6D plano (document_id, sha256, traits, page_count, ground_truth_state, oracle_hash). El sha256 está encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en el DTO de serialización. El contrato 6D es correcto. | Gate 1 W1.2 T1.2.3 | 2026-09-06 |
| H-5.1-7 | RESOLVED | GAP_CONFIRMED | Todos los parent_node_id son None en los 5 GTs canonicalizados. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II: secuencias lineales enriquecidas con metadatos topológicos). Verificado en curaduría manual (Task 1.3.9). | Gate 1 W1.3 T1.3.4 → T1.3.9 | 2026-09-09 |
| H-5.1-8 | CLOSED (NAR) | NO_GAP | Hipótesis: ManifestFingerprintCalculator.compute_hash() no incluye page_count. Verificación en source code: el payload SÍ incluye page_count (f"{doc.page_count}:"). El hash anterior coincidió por valor por defecto de Pydantic que igualó el valor real. | Gate 1 W1.3 T1.3.1 | 2026-09-09 |
| H-5.1-9 | ACCEPTED_LIMITATION | GAP_CONFIRMED | doc_02_double: 52 nodos display_equation contienen fragmentos garbled (operadores/variables aislados: "+", "= = =", "p", "i t i i"). PyMuPDF no agrupa tokens matemáticos en layout de doble columna. El GT es fiel a la salida del extractor pero NO al contenido matemático real. Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |
| H-5.1-10 | ACCEPTED_LIMITATION | GAP_CONFIRMED | doc_05_graph: 56 labels de ejes de gráficos vectoriales extraídos como paragraph individuales (ej. "–20", "0", "15"). Estructura del gráfico no capturada. Comportamiento esperado de PyMuPDF frente a gráficos vectoriales. Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |
| H-5.1-11 | RECLASSIFIED_FUTURE_PHASE | PARTIAL_GAP | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar la presencia y dejar placeholder para pegado manual. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4: no modificar extractores). Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

Las secciones de batch se agregan dinámicamente conforme se ejecuten las remediaciones.

### 4.1 BATCH 1 — Pendiente

**Fecha de ejecución:** —
**Validación:** Pyright — errors | pytest — passed, — skipped
**Estado:** ⏳ PENDING

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| — | — | — | — | — |

#### Correcciones adicionales durante ejecución

- —

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | — |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| — | — | — |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|-------------------------|
| — | — | — |

#### Métricas post-batch

| Métrica | Valor |
|---------|-------|
| Archivos creados | — |
| Archivos modificados | — |
| Archivos eliminados | — |
| Archivos movidos | — |
| Imports corregidos | — |
| Tests ejecutados | — |
| Errores de tipo estático | — |

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 16 |
| Hallazgos activos de Fase 5 | 5 (pre-identificados) + 11 (derivados de Wave 1.1, 1.2 y 1.3) |
| Hallazgos resueltos | 6 (H-5.1-1, H-5.1-2, H-5.1-3, H-5.1-4, H-5.1-5, H-5.1-7) |
| Hallazgos cerrados sin acción | 2 (H-5.1-6, H-5.1-8) |
| Hallazgos reclasificados a fase futura | 1 (H-5.1-11) |
| Hallazgos aceptados como limitación | 2 (H-5.1-9, H-5.1-10) |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Governance Findings abiertos | 0 |
| Batches completados | 0 |
| Archivos eliminados totales | 1 (tmptu237h6p) |
| Archivos movidos totales | 0 |
| Archivos creados totales | 9 (7 PDFs en canonical/pdf/, manifest.json, 6 GTs en canonical/ground_truth/, canonicalization_lineage.json, FASE_5_WAVE_1_3_CURATION_REPORT.md) |
| Tests finales | 624 passed, 5 skipped (baseline) |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

Los hallazgos diferidos a fases futuras se registran aquí con destino explícito y justificación.

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| H-5.1-11 | Post Fase 17-BIS (requiere ADR dedicado) | ADR F17_BIS_MASTER §4: la modificación de extractores de producción está fuera del scope de Fase 17-BIS. El patrón Detect & Placeholder requiere diseño de nuevos tipos de nodo (placeholder) y modificación de PyMuPDFProvider. Se recomienda evaluar en Fase 18 (Advanced Local Runtime) o en una fase dedicada de mejora de extracción. |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:

1. Todos los tests pasan:
   ```text
   pytest → baseline 624 passed, 5 skipped mantenida o mejorada
   ```
2. Pyright reporta:
   ```text
   0 errors
   ```
3. No se detectan imports huérfanos.
4. Los cambios están commiteados o registrados como Implementation Evidence.
5. Ningún oráculo sellado fue mutado in-place.
6. La evidencia del batch referencia explícitamente los DF/GF cerrados.
7. Si el batch toca contratos o artefactos de baseline, se registra hash/identidad antes y después.

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:

1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado.
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión.
3. Todos los batches planificados están completados.
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito.
5. DF-04 está cerrado con resolución documentada:
   - divergencia `< 1%` TED normalizado → APTED experimental sin acción adicional
   - divergencia `≥ 1%` TED normalizado → causa raíz investigada y documentada
6. DF-18 está resuelto:
   - semántica de fallo uniforme en entry points afectados
   - cero caminos críticos con exit code de éxito indebido
7. DF-19 está resuelto:
   - manifest migrado a formato 6D
   - hash recomputable
   - formato legacy eliminado o marcado como no canónico
8. GAP-5.0-03 está remediado:
   - configuración explícita de corpus
   - sin fallback silencioso a rutas hardcoded
9. GAP-5.2-05 está remediado:
   - protección de SealedOracle
   - no mutación in-place de artefactos sellados
10. El Gate 5 Exit Review no contiene findings bloqueantes abiertos.
11. El documento pasa a estado `ARCHIVED`.

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 16 |
| Hallazgos activos de Fase 5 (pre-identificados) | 5 |
| Hallazgos derivados de Wave 1.1, 1.2 y 1.3 | 11 |
| Hallazgos resueltos | 6 (H-5.1-1, H-5.1-2, H-5.1-3, H-5.1-4, H-5.1-5, H-5.1-7) |
| Hallazgos cerrados sin acción | 2 (H-5.1-6, H-5.1-8) |
| Hallazgos aceptados como limitación | 2 (H-5.1-9, H-5.1-10) |
| Hallazgos reclasificados a fase futura | 1 (H-5.1-11) |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Governance Findings abiertos | 0 |
| Batches completados | 0/— |
| Estado del Exit Review | 🟡 IN PROGRESS (Gate 1 en ejecución, Wave 1.3 completada) |

---

## 9. REGISTRO DE HALLAZGOS PRE-IDENTIFICADOS (REFERENCIA DE TRAZABILIDAD)

Los siguientes hallazgos fueron identificados en HITOs anteriores y/o en el
Execution Plan. Se registran aquí **únicamente como referencia de trazabilidad**.
La clasificación formal, evidencia forense y decisión arquitectónica se construirán
durante los Gate Exit Reviews correspondientes, aplicando el árbol de decisión de §1.

> **Nota:** La existencia de estos hallazgos como carry-forward o pre-identificación
> no implica que su evidencia forense esté completa. El análisis detallado (archivos
> auditados, gaps confirmados, sub-acciones, regla aplicada) se registra en §2
> cuando se ejecute el Gate Exit Review correspondiente.

### 9.1 Carry-forwards de Fase 4 — no bloquean Fase 5

| ID | Descripción | Estado preliminar | Destino | Fuente |
|----|-------------|-------------------|---------|--------|
| DF-01 | Tests tautológicos en `test_golden_parser.py` y `test_chunker_snapshot.py` | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 (Continuous Verification) | FASE_4_HANDOFF §5.2 |
| DF-02 | Verificación de `ci.yml` y `pyproject.toml` para tests de regresión | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 (Continuous Verification) | FASE_4_HANDOFF §5.2 |
| DF-03 | Deuda técnica `LayoutBlockDraft` / mapper transicional | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Gate futuro de remediación de layout | FASE_4_HANDOFF §5.2 |

### 9.2 Hallazgos activos de Fase 5 — pendientes de análisis formal

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo. Criterio (respaldado por FASE_4_HANDOFF §5.2): divergencia `< 1%` TED normalizado → APTED queda experimental sin acción adicional; divergencia `≥ 1%` → investigar causa raíz y documentar. | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 2 W2.4 Task 2.4.7 (implementación/investigación); Gate 5 W5.3 Task 5.3.3 (cierre administrativo) | FASE_4_HANDOFF §5.2 |
| DF-18 | Semántica de fallo heterogénea en 4 entry points (`freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`). Múltiples caminos de error pueden terminar en exit 0. | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 4 W4.2 Task 4.2.3 | HITO 5.2 |
| DF-19 | Manifest en formato legacy (4 dimensiones) incompatible con formato vigente (6 dimensiones). Hash almacenado ≠ hash calculado. | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 1 W1.2 Task 1.2.3 (contrato); Gate 1 W1.3 Task 1.3.1 (ejecución de migración) | HITO 5.1 |
| GAP-5.0-03 | Configuración implícita del corpus. 6 de 8 entry points tienen rutas hardcoded sin argumentos CLI configurables. | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 4 W4.1 Task 4.1.3 | HITO 5.0 |
| GAP-5.2-05 | Certification Boundary Integrity violation. `sanitize_ground_truth_types.py` puede sobrescribir Ground Truths sellados sin verificar estado de sellado. | `IMPLEMENTATION_REQUIRED` (preliminar) | Gate 2 W2.1 Task 2.1.2 (remediación primaria); Gate 4 W4.3 Task 4.3.2 (verificación de boundary) | HITO 5.2 |


### 9.2.1 Hallazgos derivados de Wave 1.1 y 1.2 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.1-1 | Discrepancia 7 vs 6 identidades (HITO 5.1). pesaran1999.pdf encontrado en datasets/raw/ e incluido como doc_07_pesaran.pdf (SHA-256: f1c80072). | `RESOLVED` | Gate 1 W1.1 T1.1.1 | Auditoría Wave 1.1 |
| H-5.1-2 | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en tests/corpus/calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | `RESOLVED` | Gate 1 W1.3 T1.3.1 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-3 | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy). Resuelto por re-extracción: PDF recortado a 3 páginas, GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente). | `RESOLVED` | Gate 1 W1.3 T1.3.8 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-4 | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Clasificación corregida en manifest canónico con nombres del catálogo vigente. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Inspección visual Wave 1.1 → Reclasificación Wave 1.2 |
| H-5.1-5 | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). DENSE_TYPOGRAPHY y MIXED_CONTENT no existen. Reclasificación completada. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Auditoría Wave 1.2 |
| H-5.1-6 | Contrato del manifest verificado como 6D plano en RawDocumentEntryDTO. El sha256 está encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en el DTO. El contrato 6D es correcto. | `CLOSED (NAR)` | Gate 1 W1.2 T1.2.3 | Auditoría Wave 1.2 |


### 9.2.2 Hallazgos derivados de Wave 1.3 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.1-7 | Todos los parent_node_id son None en los 5 GTs canonicalizados. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II). Verificado en curaduría manual. | `RESOLVED` | Gate 1 W1.3 T1.3.4 → T1.3.9 | Auditoría Wave 1.3 |
| H-5.1-8 | ManifestFingerprintCalculator.compute_hash() incluye page_count en el payload (verificado en source code). Hash anterior coincidió por valor por defecto de Pydantic. | `CLOSED (NAR)` | Gate 1 W1.3 T1.3.1 | Auditoría Wave 1.3 |
| H-5.1-9 | doc_02_double: 52 nodos display_equation con fragmentos garbled. PyMuPDF no agrupa ecuaciones en doble columna. GT fiel al extractor, no al documento fuente. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos como paragraphs. Estructura de gráficos no capturada por PyMuPDF. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder" para extracción de tablas/figuras/ecuaciones. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4). | `RECLASSIFIED_FUTURE_PHASE` | Post Fase 17-BIS | Curaduría Wave 1.3 |

### 9.3 Mapeo Finding → Task (referencia cruzada con Execution Plan)

| Finding | Task primaria | Tipo de relación | Nota |
|---------|---------------|------------------|------|
| DF-19 | 1.2.3 | Contrato | Define contrato de manifest canónico 6D (DONE) |
| DF-19 | 1.3.1 | Implementación / migración | Ejecuta migración del artefacto legacy (TODO) |
| H-5.1-1 | 1.1.1 | Resolución | pesaran1999.pdf incluido como doc_07 (RESOLVED) |
| H-5.1-2 | 1.3.1 | Limpieza | Archivo temporal huérfano eliminado (RESOLVED) |
| H-5.1-3 | 1.3.8 | Re-extracción | AST legacy reemplazado por re-extracción post-recorte (RESOLVED) |
| H-5.1-4 | 1.2.1 | Documentación | doc_03/doc_06 son scanned_noise, documentado en manifest (RESOLVED) |
| H-5.1-5 | 1.2.1 | Reclasificación | Nombres de traits corregidos contra catálogo vigente (RESOLVED) |
| H-5.1-6 | 1.2.3 | Verificación | Contrato 6D verificado como correcto (CLOSED NAR) |
| H-5.1-7 | 1.3.9 | Verificación | parent_node_id=None consistente con Flat Design (RESOLVED) |
| H-5.1-8 | 1.3.1 | Verificación | page_count incluido en hash (CLOSED NAR) |
| H-5.1-9 | 1.3.9 | Documentación | Limitación de PyMuPDF con ecuaciones en doble columna (ACCEPTED_LIMITATION) |
| H-5.1-10 | 1.3.9 | Documentación | Limitación de PyMuPDF con gráficos vectoriales (ACCEPTED_LIMITATION) |
| H-5.1-11 | 1.3.9 | Propuesta | Patrón Detect & Placeholder diferido a fase futura (RECLASSIFIED_FUTURE_PHASE) |
| GAP-5.2-05 | 2.1.2 | Remediación primaria | Protección de SealedOracle en tooling de GT |
| DF-04 | 2.4.7 | Investigación empírica | Benchmark ZhangShasha vs APTED |
| GAP-5.0-03 | 4.1.3 | Remediación primaria | Configuración explícita de corpus |
| DF-18 | 4.2.3 | Remediación primaria | Semántica de fallo uniforme |
| GAP-5.2-05 | 4.3.2 | Verificación de boundary | Validación de frontera de certificación |
| DF-04 | 5.3.3 | Cierre administrativo | Documentación final del finding |

---

## 10. RELACIÓN CON EL EXECUTION PLAN

| Gate | Waves | Tasks | Hallazgos pre-asignados |
|------|-------|-------|-------------------------|
| Gate 1 — Canonical Corpus & GT Qualification | W1.1, W1.2, W1.3 | 18 | DF-19 |
| Gate 2 — GT Sealing & Canonical Evaluation Configuration | W2.1, W2.2, W2.3, W2.4 | 17 | GAP-5.2-05, DF-04 |
| Gate 3 — Scientific Calibration & Experimental Provenance | W3.1, W3.2, W3.3 | 10 | — |
| Gate 4 — Certification Tooling & Execution Safety | W4.1, W4.2, W4.3, W4.4 | 13 | GAP-5.0-03, DF-18, GAP-5.2-05 |
| Gate 5 — End-to-End Certification & Baseline Freeze | W5.1, W5.2, W5.3 | 10 | DF-04 (cierre administrativo) |

---

## 11. REGISTRO DE GOVERNANCE FINDINGS

Los Governance Findings se registran únicamente cuando un hallazgo evidencia una
contradicción entre niveles de gobernanza. Se agregan dinámicamente durante los
Gate Exit Reviews.

| GF | DF origen | Estado | Conflicto normativo | Decisión |
|----|-----------|--------|---------------------|----------|
| — | — | — | Pendiente de identificación durante Gate Exit Reviews | — |

---

## 12. APÉNDICE — PLANTILLAS PARA NUEVOS HALLAZGOS

Cuando se identifique un hallazgo durante la implementación o un Gate Exit Review,
se agrega una entrada en §2 y/o §3.3 con la siguiente estructura mínima:

### 12.1 Plantilla para entrada en tabla de Gate Exit Review

| Campo | Valor |
|-------|-------|
| DF/GF | {ID} |
| ¿Válido? | {✅ Sí / ❌ No / ⚠️ Parcial} |
| Evidencia | {Breve descripción de la evidencia o "pendiente"} |
| ¿Resoluble en Gate? | {✅ Sí / ❌ No} |
| ¿Técnico? | {✅ Sí / ❌ No} |
| Decisión | {Estado final de clasificación} |
| Motivo | {Justificación breve con referencia normativa} |

### 12.2 Plantilla para hallazgo nuevo en §3.3

| Campo | Valor |
|-------|-------|
| ID | {DF/GF/H-5.N-X} |
| Estado | {Estado de clasificación} |
| Evidence Status | {GAP_CONFIRMED / HYPOTHESIS_PENDING / NO_GAP / PARTIAL_GAP / GOVERNANCE_CONFLICT} |
| Descripción | {Descripción breve} |
| Gate/Wave/Task | {Ubicación donde se identificó} |
| Fecha | {YYYY-MM-DD} |

### 12.3 Plantilla para entrada en batch (§4)

| Campo | Valor |
|-------|-------|
| DF ID | {ID} |
| Estado Final | {RESOLVED — acción / CLOSED (NAR) / etc.} |
| Acción Ejecutada | {Descripción de la acción} |
| Archivos Afectados | {Lista de archivos} |
| Validación | {✅ Evidencia de validación} |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → evidencia. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución. Los hallazgos que comprometan la
inmutabilidad de un oráculo sellado, la biyección PDF↔oráculo, el determinismo
de la evaluación, la independencia entre calibración y evaluación final, o la
semántica de fallo uniforme son bloqueantes hasta que se resuelvan o se
reclasifiquen formalmente con evidencia durante los Gate Exit Reviews.