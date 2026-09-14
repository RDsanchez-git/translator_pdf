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