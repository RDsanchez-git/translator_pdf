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
| Identidades cualificadas | 7 |
| Manifest hash | `62f0df16c6faecd6bac7662438f24c0a407e4c46f3271f894933456cc39bc0f1` |
| Corpus version | `v1.0` |

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

## Cobertura del Catálogo Vigente (ExtractionChallengeTrait)

| Trait | Documentos | Cobertura |
|-------|------------|:---------:|
| `native_pdf` | doc_01, doc_02, doc_04, doc_05, doc_07 | 5/7 |
| `scanned_noise` | doc_03, doc_06 | 2/7 |
| `multi_column` | doc_02, doc_05 | 2/7 |
| `heavy_math` | doc_01, doc_02, doc_03, doc_04, doc_06, doc_07 | 6/7 |
| `nested_tables` | doc_04, doc_07 | 2/7 |
| `floating_figures` | doc_04, doc_05 | 2/7 |
| `bilingual_mix` | — | **0/7** ⚠️ |

## Déficit de Corpus

- **Identidades actuales:** 7
- **Objetivo mínimo (NADR-20 §5.5 R20):** 20
- **Déficit:** 13 documentos
- **Trait no cubierto:** `bilingual_mix`
- **Estado:** Certificación bloqueada hasta alcanzar ≥20 identidades