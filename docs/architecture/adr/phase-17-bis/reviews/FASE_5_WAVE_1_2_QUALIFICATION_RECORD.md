# FASE 5 — Wave 1.2 Qualification Record

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_2_QUALIFICATION_RECORD.md`
**Fecha:** 2026-09-06
**Task:** 1.2.2 — Proceso de cualificación formal con registro auditable
**Reglas:** NADR-20 §5.4 R14-R18

## Metadatos de Cualificación

| Campo | Valor |
|-------|-------|
| Fecha de cualificación | 2026-09-06 |
| Responsable | Usuario (curaduría humana experta) |
| Método de verificación | Inspección visual de contenido + clasificación por traits |
| Corpus canónico | `tests/corpus/canonical/pdf/` |
| Identidades cualificadas | 7 (6 sellados v1.0 + doc_08 v2.0; doc_06 en quarantine) |
| Manifest hash | `5d2f47cb8d98b892...` |
| Corpus version | `v2.0` |

## Clasificación de Traits por Documento

| Documento | Traits (catálogo vigente) | Justificación |
|-----------|---------------------------|---------------|
| doc_01_single | `native_pdf`, `heavy_math` | Paper económico, 4 ecuaciones, texto nativo |
| doc_02_double | `native_pdf`, `multi_column`, `heavy_math` | Doble columna, ecuaciones |
| doc_03_math | `scanned_noise`, `heavy_math` | PDF escaneado (no nativo), matemáticas densas |
| doc_04_table | `native_pdf`, `nested_tables`, `heavy_math`, `floating_figures` | Tablas complejas, figuras, 1 ecuación |
| doc_05_graph | `native_pdf`, `multi_column`, `floating_figures` | Doble columna, figuras |
| doc_06_johnstone | `scanned_noise`, `heavy_math` | Escaneado, matemático denso |
| doc_07_pesaran | `native_pdf`, `heavy_math`, `nested_tables` | Econometría pura, 41 páginas, tablas |
| doc_08_bilingual_cs | `native_pdf`, `multi_column`, `bilingual_mix` | Paper ACL doble columna, code-switching EN-ES genuino en Examples 4/5/6 y Table 3 |

## Cobertura del Catálogo Vigente (ExtractionChallengeTrait)

| Trait | Documentos | Cobertura |
|-------|------------|:---------:|
| `native_pdf` | doc_01, doc_02, doc_04, doc_05, doc_07 | 6/7 |
| `scanned_noise` | doc_03 | 1/7 | (doc_06 en quarantine) |
| `multi_column` | doc_02, doc_05, doc_08 | 3/7 |
| `heavy_math` | doc_01, doc_02, doc_03, doc_04, doc_07 | 5/7 |
| `nested_tables` | doc_04, doc_07 | 2/7 |
| `floating_figures` | doc_04, doc_05 | 2/7 |
| `bilingual_mix` | — | doc_08 | 1/7 | 

## Déficit de Corpus

- **Identidades selladas actuales:** 7
- **Objetivo mínimo (NADR-20 §5.5 R20):** 20
- **Déficit:** 13 documentos
- **Trait cubierto:** `bilingual_mix` ✅ (doc_08)
- **Estado:** Certificación bloqueada hasta alcanzar ≥20 identidades