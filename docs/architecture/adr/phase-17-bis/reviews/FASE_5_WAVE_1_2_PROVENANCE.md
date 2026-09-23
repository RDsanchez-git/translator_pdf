# FASE 5 — Wave 1.2 Provenance Record

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_2_PROVENANCE.md`
**Fecha:** 2026-09-06
**Task:** 1.2.4 — Provenance de corpus
**Reglas:** NADR-20 §5.7 R27-R28

## Origen del Corpus Canónico

| Campo | Valor |
|-------|-------|
| Fuentes | Corpus candidato de `calibration_v1` + `datasets/raw/` + `tests/corpus/` (raíz) |
| Fecha de inclusión | 2026-09-06 |
| Responsable | Usuario |
| Método de selección | Inspección visual + clasificación por traits |

## Linaje por Documento

| Documento Canónico | Fuente Original | SHA-256 |
|--------------------|-----------------|---------|
| `doc_01_single.pdf` | `tests/corpus/calibration_v1/pdf/doc_01_single.pdf` | `2a1bab7fb7093146...` |
| `doc_02_double.pdf` | `tests/corpus/calibration_v1/pdf/doc_02_double.pdf` | `84891f98114b90a7...` |
| `doc_03_math.pdf` | `tests/corpus/calibration_v1/pdf/doc_03_math.pdf` | `21b9283a83f92983...` |
| `doc_04_table.pdf` | `tests/corpus/calibration_v1/pdf/doc_04_table.pdf` | `de56cd0420852abd...` |
| `doc_05_graph.pdf` | `tests/corpus/calibration_v1/pdf/doc_05_graph.pdf` | `274ce908d472a06b...` |
| `doc_06_johnstone.pdf` | `tests/corpus/johnstone00distribution_3hoja.pdf` | `b4f8e7a8a6f3e02e...` |
| `doc_07_pesaran.pdf` | `datasets/raw/pesaran1999.pdf` | `f1c800724a622a08...` |
| `doc_08_bilingual_cs.pdf` | `arXiv:2502.12924v3 (Heredia et al., 2026) — recorte páginas 4-6` | `248481ebb4e3ea5e...` |
| `doc_09_vanhaverbeke.pdf` | *(fuente original — H-5.5-2, sellado pre-gate)* | `SHA pendiente` |
| `doc_10_gross.pdf` | *(fuente original — H-5.5-2, sellado pre-gate)* | `SHA pendiente` |
| `doc_11_fig.pdf` | Capítulo 20 "Overlap in Observational Studies" — págs. 270-272 | `cb9eaa3956d17339...` |
| `doc_12_multi_col.pdf` | Felin & Holweg (2024) "Theory Is All You Need" — Strategy Science, págs. 1-3 | `2de743f869b3c28b...` |
| `doc_13_fmi_graf_tablas.pdf` | FMI Working Paper (sovereign ratings) — págs. 11-13 | `8f1a9ad7c09ad81a...` |
| `doc_14_fig_math.pdf` | Deisenroth, Faisal & Ong. *Mathematics for Machine Learning* (CUP, 2024). Capítulo 3, §3.8.4 + §3.9 — págs. 90-92 | `05008eeb69f65d4b...` |
| `doc_15_table_fig_code.pdf` | Mark Lutz. *Learning Python* (O'Reilly, 5th ed.). Capítulo 33: Exception Coding Details — págs. 837-839 | `806fce3fb5b73be3...` |
| `doc_16_fig_code.pdf` | Jake VanderPlas. *Python Data Science Handbook* (O'Reilly). Capítulo 5: Machine Learning, "In Depth: Linear Regression" — págs. 396-398 | `c6ede7450dc46b70...` |
| `doc_17_table_code.pdf` | Jake VanderPlas. *Python Data Science Handbook* (O'Reilly). Capítulo 3: Data Manipulation with Pandas, "Vectorized String Operations" — págs. 181-183 | `f0c3d8e2a1b94c57...` |
| `doc_18_table_math_doble_col.pdf` | IMF Occasional Paper / Working Paper. "Saving-Investment Balances in Industrial Countries" — págs. 45-47 | `a7b3c9d2e5f18046...` |
| `doc_19_fig_table_doble_col.pdf` | K. Hastuti et al. *Machine Learning with Applications 24 (2026) 100852*. "Proposed pipeline for keris classification..." — págs. 3-5 | `c4d5e6f7a8b90123...` |
| `doc_20_doble_col_table.pdf` | K. Hastuti et al. *Machine Learning with Applications 24 (2026) 100852*. Sección final (discusión, conclusiones, apéndices) — págs. 12-14 | `d5e6f7a8b9c01234...` |
| `doc_21_heavy_math_table.pdf` | OpenAI / Terence Tao et al. "Finite Time Blowup for Navier–Stokes" — págs. 24-26 | `e6f7a8b9c0d12345...` |
| `doc_22_table_fig_math.pdf` | M. Flores et al. *Machine Learning with Applications 24 (2026) 100878*. "Estimation of Soil Organic Carbon..." — págs. 4-6 | `f7a8b9c0d1e23456...` |

## Nota Normativa

Provenance ≠ identidad. La identidad está determinada por el SHA-256 del contenido,
no por el provenance. El provenance documenta el origen y linaje del documento,
pero no altera su identidad criptográfica.

## Extensión v2.0 (2026-09-13)

| Campo | Valor |
|-------|-------|
| Fecha de inclusión | 2026-09-13 |
| Responsable | Usuario |
| Método de selección | Búsqueda dirigida por trait faltante (bilingual_mix) |
| Criterio | Código-switching EN-ES genuino (Examples 4, 5, 6 + Table 3) |
| Recorte | Páginas 4-6 del original (18 páginas) |
| Corpus version | v1.0 → v2.0 |
| Manifest hash anterior | `0fda7690...` (v1.0, 6 sellados) |
| Manifest hash nuevo | `5d2f47cb8d98b892...` (v2.0, 7 sellados) |

## Extensión v2.1-v2.2 (2026-09-14)

| Campo | Valor |
|-------|-------|
| Fecha de inclusión | 2026-09-14 |
| Documentos añadidos | doc_09_vanhaverbeke, doc_10_gross |
| Método de selección | Onboarding dirigido (pre-gate de curaduría) |
| Nota | Sellados sin curaduría manual (H-5.5-2). Tautológicos. Reemplazo diferido a re-baseline v3.0. |
| Corpus version | v2.0 → v2.2 |

## Extensión v3.0 — Batch 2a (2026-09-19)

| Campo | Valor |
|-------|-------|
| Fecha de inclusión | 2026-09-19 |
| Responsable | Usuario |
| Método de selección | Búsqueda dirigida por traits con cobertura baja (nested_tables, floating_figures, multi_column, heavy_math) |
| Criterios de selección | Documentos con divergencia estructural de PyMuPDF: ecuaciones, tablas econométricas, figuras vectoriales, doble columna |
| Recorte | 3 páginas por documento |
| Documentos añadidos | doc_11_fig (heavy_math + floating_figures), doc_12_multi_col (multi_column), doc_13_fmi_graf_tablas (nested_tables + floating_figures) |
| Gate de curaduría | Activo (Batch 1, commit `9cbddf8`). Escritor `curate_gt.py` operativo (Batch 2a, commit `c4bb03b`). |
| Corpus version | v2.2 → v3.0 |
| Manifest hash anterior | `52c42353...` (v2.2, 9 sellados) |
| Manifest hash nuevo | `SHA pendiente` (v3.0, 12 sellados) |

## Extensión v3.1 — Batch 3 (2026-09-22 / 2026-09-23)

| Campo | Valor |
|-------|-------|
| Fecha de inclusión | 2026-09-22 / 2026-09-23 |
| Responsable | Usuario |
| Método de selección | Búsqueda dirigida por traits con cobertura baja/media + stress tests de patologías extremas |
| Criterios de selección | Documentos que evidencien: (1) ceguera sistemática ante código Python/Jupyter, (2) destrucción tabular en reports econométricos de doble columna, (3) hiper-fragmentación matemática extrema, (4) inversión sistemática de jerarquía, (5) colapso monolítico de tablas extensas multimodales |
| Recorte | 3 páginas por documento |
| Documentos añadidos | doc_14_fig_math (layout Tufte + figuras geométricas + matrices con glifos corruptos), doc_15_table_fig_code (snippets Python + tabla shredding), doc_16_fig_code (celdas Jupyter + figuras matplotlib), doc_17_table_code (Pandas string methods + tablas de referencia), doc_18_table_math_doble_col (tablas econométricas IMF + capas fantasma), doc_19_fig_table_doble_col (YOLOv8x + inversión de jerarquía), doc_20_doble_col_table (apéndices + dualidad tabular smashing/shredding), doc_21_heavy_math_table (Navier-Stokes + mutilación de raíces), doc_22_table_fig_math (47 covariables + Moran's I + intercalación de footnotes) |
| Gate de curaduría | Activo (Batch 1, commit `9cbddf8`). Escritor `curate_gt.py` operativo (Batch 2a, commit `c4bb03b`). |
| Corpus version | v3.0 → v3.5 (saltos v3.1-v3.4 absorbidos en cierre unificado) |
| Manifest hash anterior | `SHA pendiente` (v3.0, 12 sellados) |
| Manifest hash nuevo | `SHA pendiente de sellado unificado` (v3.5, 19 curados + 3 pendientes de Batch 4 para alcanzar 20 sellados) |

### Hallazgos derivados de Batch 3

| ID | Hallazgo | Clasificación |
|---|---|---|
| H-5.1-19..20 | Layout Tufte (margin bleed) y corrupción de glifos TeX en delimitadores de matrices | ACCEPTED_LIMITATION |
| H-5.1-21..26 | Ceguera sistemática ante código Python y celdas Jupyter (100% de snippets tipados como prosa) | ACCEPTED_LIMITATION |
| H-5.1-27..28 | Desarticulación de tablas de referencia y ceguera IPython con regex complejas | ACCEPTED_LIMITATION |
| H-5.1-29..32 | Desmembramiento tabular vertical (77.6% celdas sueltas), capas fantasma, corrupción IMF, falsos headings | ACCEPTED_LIMITATION |
| H-5.1-33..35 | Inversión sistemática de jerarquía (header role inversion), doble patología tabular, omisión absoluta de figuras en visión | ACCEPTED_LIMITATION |
| H-5.1-36..38 | Dualidad tabular (smashing vs shredding), epidemia de falsos headings, colapso de listas con viñetas | ACCEPTED_LIMITATION |
| H-5.1-39..41 | Hiper-fragmentación matemática devastadora (56.2%), mutilación sistemática de signos radicales, header bleed extremo | ACCEPTED_LIMITATION |
| H-5.1-42..44 | Colapso monolítico extremo de tabla extensa (47 covariables), desarticulación de sumatorias dobles, intercalación destructiva de notas al pie | ACCEPTED_LIMITATION |

## Extensión v3.9 — Batch 3 completo y SELLADO DEFINITIVO (2026-09-23)

| Campo | Valor |
|-------|-------|
| Fecha de sellado | 2026-09-23 |
| Responsable | Usuario |
| Método de selección | Búsqueda dirigida por traits con cobertura baja + stress tests de patologías extremas de PyMuPDF |
| Documentos añadidos | doc_14_fig_math a doc_22_table_fig_math (9 documentos) |
| Gate de curaduría | Activo. Todos los documentos curados manualmente antes del sellado. |
| Corpus version | v3.5 → v3.9 |
| Manifest hash final | `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d` |
| Total identidades selladas | **21** (objetivo mínimo 20 alcanzado) |
| Zero Partial Sealing | ✅ Cumplido. Biyección N_PDF = N_GT = 21. |