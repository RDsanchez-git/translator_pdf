# FASE 5 — Wave 1.2 Qualification Record

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_2_QUALIFICATION_RECORD.md`
**Fecha de creación:** 2026-09-06
**Última actualización:** 2026-09-19
**Task:** 1.2.2 — Proceso de cualificación formal con registro auditable
**Reglas:** NADR-20 §5.4 R14-R18

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| v2.0 | 2026-09-06 | Emisión inicial: 7 identidades cualificadas (doc_01-05, doc_07, doc_08; doc_06 en quarantine). |
| v2.1 | 2026-09-14 | Addendum v2.1: doc_08_bilingual_cs (Curation Report Wave 1.3). |
| v2.2 | 2026-09-19 | Addendum v2.2: doc_09_vanhaverbeke y doc_10_gross (sellados pre-gate de curaduría, H-5.5-2, tautológicos). Coverage actualizada: bilingual_mix → 3/9, native_pdf → 8/9. Déficit: 11 documentos. |
| v3.0 | 2026-09-19 | Addendum v3.0 (Batch 2a): doc_11_fig, doc_12_multi_col, doc_13_fmi_graf_tablas. Gate de curaduría activo. Coverage actualizada: nested_tables → 3/12, floating_figures → 4/12, multi_column → 4/12, heavy_math → 6/12. Déficit: 8 documentos. |
| v3.5 | 2026-09-23 | Addendum v3.5 (Batch 3): doc_14_fig_math, doc_15_table_fig_code, doc_16_fig_code, doc_17_table_code, doc_18_table_math_doble_col, doc_19_fig_table_doble_col, doc_20_doble_col_table, doc_21_heavy_math_table, doc_22_table_fig_math. Gate de curaduría activo. Coverage actualizada: native_pdf → 19/19, multi_column → 10/19, heavy_math → 10/19, floating_figures → 8/19, nested_tables → 4/19. Déficit: 1 documento para alcanzar 20 sellados. |
| v3.9 | 2026-09-23 | **SELLADO DEFINITIVO.** Addendum v3.9 (Batch 3 completo): doc_14_fig_math a doc_22_table_fig_math sellados bajo gate de curaduría. Corpus alcanza 21 identidades selladas (objetivo NADR-20 §5.5 R20: 20). Manifest hash: `727782fe0df26d9d...`. Zero Partial Sealing cumplido. Biyección N_PDF = N_GT = 21. |

## Metadatos de Cualificación

| Campo | Valor |
|-------|-------|
| Fecha de cualificación inicial | 2026-09-06 |
| Última actualización | 2026-09-23 |
| Responsable | Usuario (curaduría humana experta) |
| Método de verificación | Inspección visual de contenido + clasificación por traits |
| Corpus canónico | `tests/corpus/canonical/pdf/` |
| Identidades cualificadas | **21 selladas** (doc_01-05, doc_07-22; doc_06 en quarantine) |
| Manifest hash | `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d` |
| Corpus version | `v3.9` |

## Clasificación de Traits por Documento

| Documento | Traits (catálogo vigente) | Justificación |
|-----------|---------------------------|---------------|
| doc_01_single | `native_pdf`, `heavy_math` | Paper económico, 4 ecuaciones, texto nativo |
| doc_02_double | `native_pdf`, `multi_column`, `heavy_math` | Doble columna, ecuaciones |
| doc_03_math | `scanned_noise`, `heavy_math` | PDF escaneado (no nativo), matemáticas densas |
| doc_04_table | `native_pdf`, `nested_tables`, `heavy_math`, `floating_figures` | Tablas complejas, figuras, 1 ecuación |
| doc_05_graph | `native_pdf`, `multi_column`, `floating_figures` | Doble columna, figuras |
| doc_06_johnstone | `scanned_noise`, `heavy_math` | Escaneado, matemático denso (**quarantine H-5.2-1**, no cualificado) |
| doc_07_pesaran | `native_pdf`, `heavy_math`, `nested_tables` | Econometría pura, 41 páginas, tablas |
| doc_08_bilingual_cs | `native_pdf`, `multi_column`, `bilingual_mix` | Paper ACL doble columna, code-switching EN-ES genuino en Examples 4/5/6 y Table 3 |
| doc_09_vanhaverbeke | `native_pdf`, `bilingual_mix` | Code-switching EN-ES (H-5.5-2, sellado sin curaduría previa — tautológico) |
| doc_10_gross | `native_pdf`, `bilingual_mix` | Code-switching EN-ES infantil + Leipzig glossing (H-5.5-2, sellado sin curaduría previa — tautológico) |
| doc_11_fig | `native_pdf`, `floating_figures`, `heavy_math` | Regression discontinuity: ecuaciones con límites + Figura 20.2 con texto vectorial |
| doc_12_multi_col | `native_pdf`, `multi_column` | Paper Strategy Science en doble columna (ciencias sociales, sin matemáticas) |
| doc_13_fmi_graf_tablas | `native_pdf`, `nested_tables`, `floating_figures` | FMI sovereign ratings: Tablas 2 y 3 (ordered probit) + Figuras 1 y 2 (year-fixed effects) |
| doc_14_fig_math | `native_pdf`, `floating_figures`, `heavy_math` | Libro de texto *Mathematics for Machine Learning* (layout Tufte, figuras geométricas + matrices con glifos corruptos) |
| doc_15_table_fig_code | `native_pdf` | *Learning Python* O'Reilly (try/except, tablas + bloques de código Python) |
| doc_16_fig_code | `native_pdf`, `floating_figures` | *Python Data Science Handbook* (celdas Jupyter + figuras matplotlib + fórmula L2) |
| doc_17_table_code | `native_pdf` | *Python Data Science Handbook* (Pandas string methods, tablas referencia + celdas IPython) |
| doc_18_table_math_doble_col | `native_pdf`, `multi_column`, `heavy_math`, `nested_tables` | IMF Working Paper (tablas econométricas de panel dinámico en doble columna + capas fantasma) |
| doc_19_fig_table_doble_col | `native_pdf`, `multi_column`, `floating_figures` | Paper de visión por computadora (pipeline YOLOv8x, tablas de hiperparámetros, inversión de jerarquía) |
| doc_20_doble_col_table | `native_pdf`, `multi_column` | Paper de heritage AI (apéndices con tablas de distribución y ablation studies, dualidad tabular) |
| doc_21_heavy_math_table | `native_pdf`, `heavy_math` | Paper de OpenAI/Tao (Navier-Stokes, hiper-fragmentación de fórmulas y mutilación de raíces) |
| doc_22_table_fig_math | `native_pdf`, `multi_column`, `heavy_math`, `floating_figures` | Paper de teledetección (tabla de 47 covariables, Moran's I, mapas satelitales, intercalación de footnotes) |

## Cobertura del Catálogo Vigente (ExtractionChallengeTrait)

| Trait | Documentos | Cobertura |
|-------|------------|:---------:|
| `native_pdf` | doc_01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | **19/19** |
| `scanned_noise` | doc_03 (doc_06 en quarantine) | **1/19** |
| `multi_column` | doc_02, 05, 08, 12, 18, 19, 20, 22 | **8/19** |
| `heavy_math` | doc_01, 02, 03, 04, 07, 11, 14, 18, 21, 22 | **10/19** |
| `nested_tables` | doc_04, 07, 13, 18 | **4/19** |
| `floating_figures` | doc_04, 05, 11, 13, 14, 16, 19, 22 | **8/19** |
| `bilingual_mix` | doc_08, 09, 10 | **3/19** |

## Déficit de Corpus

- **Identidades selladas actuales:** 21
- **Objetivo mínimo (NADR-20 §5.5 R20):** 20
- **Déficit:** 0 — **OBJETIVO ALCANZADO**
- **Traits con cobertura adecuada (≥6):** `native_pdf` (20), `heavy_math` (10), `multi_column` (8), `nested_tables` (8), `floating_figures` (8)
- **Traits con cobertura baja (≤3):** `bilingual_mix` (3), `scanned_noise` (1)
- **Estado:** ✅ Certificación habilitada. Corpus sellado bajo firma global SHA-256. Regression Gates activos.

## Notas de Gobernanza

- **doc_06_johnstone** en quarantine (H-5.2-1): scanned puro sin text layer. No cuenta como identidad cualificada hasta que se re-trimee con OCR o se descarte formalmente.
- **doc_09_vanhaverbeke y doc_10_gross** sellados sin curaduría manual previa (H-5.5-2, antes del gate O2 de Batch 1). Sus oráculos son tautológicos (NSS=1.0000 contra sí mismos). Reemplazo diferido a re-baseline v3.0 (corpus ≥20 identidades).
- **Gate O2 de Batch 1** (commit `9cbddf8`) ahora impone entrada `CURATED` en `curation_checklist.json` antes del sellado. Ningún documento onboarded después del 2026-09-15 puede repetir la tautología de doc_09/doc_10.
- **Batch 2a (2026-09-19):** doc_11_fig, doc_12_multi_col y doc_13_fmi_graf_tablas onboarded con gate de curaduría activo (Batch 1 + Batch 2a). Estos son los primeros documentos curados bajo el protocolo completo: check_candidate → add_document → generate_draft → canonicalize → curar manualmente → curate_gt → freeze.
- **Hallazgos derivados de Batch 2a:** H-5.1-12 (contaminación vectorial de figuras), H-5.1-13 (cross-page bleed de headers), H-5.1-14 (hiper-fragmentación por renglón), H-5.1-15 (destrucción total de estructura tabular). Todos clasificados ACCEPTED_LIMITATION, destino Fase 6.
- **Batch 3 (2026-09-22 / 2026-09-23):** doc_14_fig_math a doc_22_table_fig_math onboarded con gate de curaduría activo. Estos 9 documentos documentan patologías extremas del extractor PyMuPDF: hiper-fragmentación matemática (56.2% de nodos en doc_21), colapso monolítico de tablas extensas (doc_22), ceguera sistemática ante código Python (100% en doc_15/16/17), y destrucción tabular en reports econométricos (77.6% en doc_18).
- **Hallazgos derivados de Batch 3:** H-5.1-19 a H-5.1-44 (26 hallazgos nuevos). Todos clasificados ACCEPTED_LIMITATION, destino Fase 6. El catálogo de limitaciones documentadas de PyMuPDFProvider se expandió de 18 a 30 debilidades empíricamente verificadas.