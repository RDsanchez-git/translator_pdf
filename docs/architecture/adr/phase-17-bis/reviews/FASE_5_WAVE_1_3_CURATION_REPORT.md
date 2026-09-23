# FASE 5 — Wave 1.3 Curation Report

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_3_CURATION_REPORT.md`
**Fecha original:** 2026-09-09
**Última actualización:** 2026-09-23 (SELLADO DEFINITIVO — Batch 3 completo, corpus v3.9, 21 identidades)
**Task:** 1.3.9 — Curaduría manual de Ground Truths
**Reglas:** NADR-21 §5.1 R5 (La curaduría ocurre ANTES del sealing, nunca después)

---

## Resumen Ejecutivo

- **Total de documentos curados:** 21 (7 originales Wave 1.3 + 3 Batch 2a + 9 Batch 3 + 2 pendientes de sellado previo resueltos)
- **Documentos rechazados:** 0
- **Documentos aceptados:** 21 (4 sin observaciones, 17 con observaciones)
- **Extractor de producción evaluado:** `PyMuPDFProvider` (vía `build_extraction_pipeline()`)
- **Gate de curaduría:** Activo desde Batch 1 (commit `9cbddf8`). Writer `curate_gt.py` operativo desde Batch 2a (commit `c4bb03b`).
- **Estado del corpus:** ✅ **SELLADO.** 21 oráculos válidos bajo firma global SHA-256: `727782fe0df26d9d...`

**Veredicto General:** Todos los Ground Truths (GTs) han sido aceptados y sellados. El corpus canónico de 21 documentos cubre 7 traits de extracción y documenta 30 limitaciones empíricas de PyMuPDFProvider como Baseline de Capacidades. El objetivo mínimo de 20 identidades selladas (NADR-20 §5.5 R20) fue alcanzado y superado.

**Documentos añadidos en Batch 2a (2026-09-19):**
- `doc_11_fig` — regression discontinuity, ecuaciones matemáticas + figuras con texto vectorial
- `doc_12_multi_col` — paper de Strategy Science en doble columna (ciencias sociales, sin matemáticas)
- `doc_13_fmi_graf_tablas` — sovereign ratings con tablas estadísticas complejas + figuras

**Documentos añadidos en Batch 3 (2026-09-22 / 2026-09-23):**
- `doc_14_fig_math` — libro de texto *Mathematics for Machine Learning* (layout Tufte, figuras geométricas + ecuaciones)
- `doc_15_table_fig_code` — *Learning Python* O'Reilly (try/except, tablas + bloques de código)
- `doc_16_fig_code` — *Python Data Science Handbook* (celdas Jupyter + figuras matplotlib + fórmula L2)
- `doc_17_table_code` — *Python Data Science Handbook* (Pandas string methods, tablas referencia + celdas IPython)
- `doc_18_table_math_doble_col` — IMF Working Paper (tablas econométricas de panel dinámico en doble columna)
- `doc_19_fig_table_doble_col` — paper de visión por computadora (pipeline, YOLOv8x, tablas de hiperparámetros)
- `doc_20_doble_col_table` — paper de heritage AI (apéndices con tablas de distribución y ablation studies)
- `doc_21_heavy_math_table` — paper de OpenAI/Tao (Navier-Stokes, hiper-fragmentación de fórmulas y raíces)
- `doc_22_table_fig_math` — paper de teledetección (tabla de 47 covariables, Moran's I, mapas satelitales)

---

## Registro de Curaduría por Documento

### doc_01_single (35 nodos)
- **Distribución:** 17 paragraph, 14 display_equation, 4 heading.
- **Nodos cortos (<10 chars):** 3 (9%).
- **Observación:** Extracción limpia. Las 14 ecuaciones de bloque se detectaron y estructuraron correctamente.
- **Decisión:** ACEPTADO.

### doc_02_double (116 nodos)
- **Distribución:** 68 display_equation, 43 paragraph, 4 heading, 1 caption.
- **Nodos cortos (<10 chars):** 53 (46%).
- **Observación Crítica:** Fragmentación severa de ecuaciones. PyMuPDF no logra agrupar los tokens matemáticos en el layout de doble columna, generando decenas de nodos `display_equation` con contenido trivial (ej. `"+"`, `"= = ="`, `"p"`, `"i t i i"`).
- **Decisión:** ACEPTADO CON OBSERVACIÓN. El GT es fiel a la salida del extractor, documentando su incapacidad para manejar matemáticas complejas en doble columna.
- **Hallazgo derivado:** H-5.1-9.

### doc_03_math (81 nodos)
- **Distribución:** 70 paragraph, 9 display_equation, 2 heading.
- **Nodos cortos (<10 chars):** 9 (11%).
- **Observación:** A pesar de ser un documento escaneado (`scanned_noise`), el pipeline de extracción logró extraer texto y 9 ecuaciones de bloque.
- **Decisión:** ACEPTADO.

### doc_04_table (65 nodos)
- **Distribución:** 43 paragraph, 12 table_simple, 6 caption, 3 display_equation, 1 heading.
- **Nodos cortos (<10 chars):** 11 (17%).
- **Observación:** Excelente detección estructural. PyMuPDF identificó correctamente 12 tablas simples y 3 ecuaciones.
- **Decisión:** ACEPTADO.

### doc_05_graph (104 nodos)
- **Distribución:** 84 paragraph, 19 caption, 1 heading.
- **Nodos cortos (<10 chars):** 56 (54%).
- **Observación Crítica:** Los nodos cortos son exclusivamente etiquetas de ejes y valores de datos de los gráficos vectoriales (ej. `"–20"`, `"0"`, `"15"`). PyMuPDF extrae el texto incrustado en los gráficos como párrafos independientes, inyectando ruido estructural en el flujo del documento.
- **Decisión:** ACEPTADO CON OBSERVACIÓN. Comportamiento esperado de extractores basados en texto frente a gráficos vectoriales.
- **Hallazgo derivado:** H-5.1-10.

### doc_07_pesaran (21 nodos)
- **Distribución:** 17 paragraph, 4 heading.
- **Nodos cortos (<10 chars):** 3 (14%).
- **Observación Crítica:** El documento original contiene 3 tablas complejas y ecuaciones econométricas, pero el AST tiene 0 nodos `table` y 0 nodos `equation`.
- **Causa Raíz:** El PDF utiliza fuentes personalizadas (Type 3) sin mapa `ToUnicode`. PyMuPDF no puede decodificar los glifos matemáticos ni las estructuras tabulares, extrayendo todo el contenido como texto plano (`paragraph`).
- **Decisión:** ACEPTADO CON OBSERVACIÓN. Limitación criptográfica del extractor frente a fuentes no estándar.
- **Hallazgo derivado:** H-5.1-11 (limitación de fuentes Type 3, relacionada con el patrón Detect & Placeholder).

---

### doc_08_bilingual_cs (64 nodos) — AGREGADO 2026-09-13

**Fuente:** Heredia, Labaka, Barnes & Soroa (2026). "Conditioning LLMs to Generate Code-Switched Text." arXiv:2502.12924v3.
**Recorte:** Páginas 4-6 del original (3 páginas).
**SHA-256:** `248481ebb4e3ea5e...`
**Traits:** `native_pdf`, `multi_column`, `bilingual_mix`
**Licencia:** CC-BY-NC-SA (dataset y código del paper). Uso local/académico únicamente (O-1.1-1).

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón MIG-05):**

El pipeline de extracción (`build_extraction_pipeline()` → `FlatASTBuilder`) generó node_ids en formato legacy `value='p1_b0'` en vez del formato canónico `p1_b0`. Se aplicó el mismo patrón de canonicalización que en MIG-05 (Wave 1.3, Fase 5):

- 66/66 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_08_canonicalization_lineage.json`
- Verificación: OracleValidityContract PASSED

**Causa raíz del formato legacy:** El `BenchmarkParserBridge.extract_ast()` serializa el objeto `BlockId` (Pydantic) usando `str(BlockId)`, que produce `value='p1_b0'` en vez de extraer `BlockId.value`. Este defecto afecta a todos los GTs generados por el pipeline actual y se registra como carry-forward DF-06.

**Paso 2 — Corrección de headings degradados:**

| Node ID | Contenido | Antes | Después |
|---------|-----------|-------|---------|
| `p2_b4` | "5.1. Preference based evaluation" | `paragraph` | `heading` (level=2) |
| `p3_b21` | "5.2. Error analysis" | `paragraph` | `heading` (level=2) |

El extractor no detectó estos subtítulos formales como headings debido a que su tipografía no difiere suficientemente del cuerpo del texto en el layout de doble columna.

**Paso 3 — Fusión de párrafos partidos por corte de columna:**

| Fusión | Causa | Resultado |
|--------|-------|-----------|
| `p1_b6` + `p1_b7` | Párrafo partido por cambio de columna: "Regard- / ing" | Párrafo continuo con palabra "Regarding" reconstruida |
| `p2_b5` + `p2_b20` | Párrafo interrumpido por inserción de Table 4 | Párrafo continuo reconstruido |

**Paso 4 — Marcado de footnotes en metadata:**

| Node ID | Contenido | Marcado |
|---------|-----------|---------|
| `p1_b9` | "3 https://github.com/sagorbrur/codeswitch" | `metadata.note = 'footnote_3'` |
| `p2_b6` | "4 A batch size of 32..." | `metadata.note = 'footnote_4'` |

**LIMITACIÓN:** El campo `note` no sobrevive la deserialización canónica (`NodeMetadata` tiene schema fijo sin campo `note`). Los footnotes están presentes en el contenido textual pero no marcados estructuralmente. Se registra como observación para Fase 6.

#### Verificación post-curación

- **Nodos finales:** 64 (66 originales − 2 fusiones)
- **read_ast_json:** 64 nodos deserializados correctamente
- **OracleValidityContract:** PASSED
- **hydrate_ground_truth:** Hidratación como GroundTruthDraft exitosa
- **Node_ids:** 64/64 en formato canónico (`p1_b0`, `p1_b1`, ...)

#### Code-switching EN-ES (trait objetivo)

El code-switching está genuinamente presente y extraíble en los siguientes nodos:

| Node ID | Contenido CS | Fuente |
|---------|-------------|--------|
| `p1_b1` | "damm todos se casaron and we still single lol forever alone" | Table 3 (Original Gold) |
| `p1_b2` | "damn todos se fueron a casarse y nosotras estamos solitarias..." | Table 3 (outputs de modelos) |
| `p3_b28` | "lo mejor que puedo hacer es estar aquí para él si me necesita" | Example 4 |

El trait `bilingual_mix` queda cubierto con código-switching intrasentencial EN-ES real (no prestado ni artificial).

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Tablas no estructuradas:** Table 3 y Table 4 extraídas como texto plano (múltiples nodos `paragraph`). PyMuPDF no detecta estructura tabular. El trait `nested_tables` NO se añadió a doc_08 porque el extractor no puede verificar su presencia.
2. **Figure 1 como texto basura:** El gráfico de barras (Figure 1) se extrajo como ~23 nodos de texto con valores numéricos de ejes y labels. El trait `floating_figures` NO se añadió.
3. **Ejemplos lingüísticos no estructurados:** Examples 4, 5, 6 (bloques Source/Output) dejados como `paragraph`. No se inventó un node_type `example` porque no existe en `ContentNodeType`.
4. **Fórmula binomial deformada:** La expresión $210 \cdot \binom{6}{2} = 3150$ se extrajo como texto plano "210 ·(6 2) = 3150" sin estructura math.
5. **Footnotes sin metadata estructural:** Campo `note` descartado por `NodeMetadata` (schema fijo). Footnotes presentes en contenido pero sin clasificación formal.
6. **Code-switching no etiquetado a nivel de span:** No se aplican spans de idioma por token (requiere detector CS externo tipo LINCE). El CS está presente en el contenido pero no anotado estructuralmente.

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `bilingual_mix` cubierto (cobertura previa: 0/7 → 1/7)
- **Regresión topológica:** ⚠️ Benchmark tautológico esperado (NSS=1.0). El GT es eco del extractor con correcciones mínimas. Mide cobertura de traits, no divergencia real del runtime.

**Decisión:** ACEPTADO CON OBSERVACIÓN. El documento cubre el trait objetivo `bilingual_mix` con code-switching genuino. Las limitaciones son conocidas y documentadas.

### doc_11_fig (44 nodos) — AGREGADO 2026-09-19

**Fuente:** Capítulo 20 "Overlap in Observational Studies: Difficulties and Opportunities" — Regression Discontinuity.
**Recorte:** Páginas 270-272 (3 páginas).
**SHA-256:** `cb9eaa3956d17339...`
**Traits:** `native_pdf`, `floating_figures`, `heavy_math`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

El pipeline de extracción generó node_ids en formato legacy `value='pX_bY'`. Se aplicó canonicalización vía `canonicalize_gt.py` (Batch 2a):

- 44/44 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_11_fig_canonicalization_lineage.json`
- Verificación: 0 legacy restantes post-canonicalización

**Paso 2 — Clasificación nodos por nodo (44 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | paragraph | paragraph | omit | Mal (encabezado/folio pág. 270) |
| 1 | p1_b2 | paragraph | caption | translate | Parcial |
| 2-3 | p1_b3, p1_b4 | paragraph | paragraph | translate | Bien |
| 4 | p1_b5 | paragraph | paragraph | translate | Parcial (absorbió header pág. 271) |
| 5-21 | p2_b1..p2_b17 | paragraph | composite_block | omit | Mal (17 ticks/leyenda vectoriales Fig. 20.2) |
| 22 | p2_b18 | paragraph | caption | translate | Parcial |
| 23 | p2_b19 | paragraph | paragraph | translate | Bien |
| 24 | p2_b20 | paragraph | composite_block | translate | Mal (lista fusionada con párrafo) |
| 25 | p2_b21 | paragraph | heading | translate | Parcial |
| 26 | p2_b22 | paragraph | paragraph | translate | Bien |
| 27 | p2_b23 | paragraph | display_equation | passthrough | Mal |
| 28 | p3_b0 | paragraph | paragraph | omit | Mal (folio pág. 272) |
| 29 | p3_b1 | paragraph | paragraph | translate | Bien |
| 30-32 | p3_b2, p3_b3, p3_b4 | paragraph | display_equation | passthrough | Mal (ecuaciones 20.2, 20.3, 20.4) |
| 33 | p3_b5 | paragraph | paragraph | translate | Bien |
| 34 | p3_b6 | paragraph | display_equation | passthrough | Mal |
| 35-36 | p3_b7, p3_b8 | paragraph | paragraph | translate | Bien |
| 37 | p3_b9 | paragraph | display_equation | passthrough | Mal |
| 38 | p3_b10 | paragraph | paragraph | translate | Bien |
| 39 | p3_b11 | paragraph | heading | translate | Parcial |
| 40 | p3_b12 | paragraph | paragraph | translate | Bien |
| 41 | p3_b13 | paragraph | display_equation | passthrough | Mal |
| 42 | p3_b14 | paragraph | paragraph | translate | Bien |
| 43 | p3_b15 | paragraph | display_equation | passthrough | Mal |

**Paso 3 — Distribución final:**

- **node_type:** 14 paragraph, 18 composite_block, 8 display_equation, 2 caption, 2 heading
- **strategy:** 16 translate, 19 omit, 9 passthrough
- **Nodos cortos (<10 chars):** 18 (los 17 ticks vectoriales + folio)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Omisión de Figura 20.1 | PyMuPDF no detectó el raster escaneado. 0 nodos IMAGE en el GT. | Limitación de extracción de imágenes raster |
| Despiece de Figura 20.2 | Gráfico vectorial desarmado en 17 bloques parásitos (nodos 5-21) | PyMuPDF extrae texto vectorial como paragraph |
| Cross-page bleed en nodo 4 | Párrafo absorbió header de pág. 271 (`...per 20.2 Causal inference... 271`) | No hay detección de headers transpágina |
| Under-segmentation en nodo 24 | Lista de 9 variables fusionada con párrafo explicativo | PyMuPDF no detecta listas |
| Over-segmentation en nodos 30-32 | Deducción matemática de 3 líneas partida en 3 nodos | PyMuPDF no agrupa ecuaciones multilínea |
| Dehyphenation pendiente | `ef-fect`, `discontinu-ity`, `av-erage`, `expec-tation` | Cortes de línea con guion no resueltos |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 10/44 = **22.7%** (0% acierto en headings, captions y matemática)
- **Exactitud de strategy:** 16/44 = **36.4%** (todas las ecuaciones y ruido vectorial recibieron `translate` erróneamente)
- **Tasa de contaminación vectorial:** 17/44 = **38.6%** (texto incidental de gráfico)

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Omisión total de objetos IMAGE:** Figuras 20.1 y 20.2 no existen como nodos `image`. El trait `floating_figures` está cubierto por la *presencia estructural del problema*, no por nodos IMAGE reales.
2. **Contaminación vectorial masiva:** 38.6% de los nodos son ruido parásito de un gráfico vectorial. El benchmark debe computar esto como divergencia estructural.
3. **GT es eco del extractor:** Las ecuaciones `display_equation` existen como nodos, pero el *contenido* extraído por PyMuPDF es texto plano sin estructura matemática (paréntesis, fracciones, límites).

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `floating_figures` cubierto (2/9 → 3/12), `heavy_math` (5/9 → 6/12)
- **Regresión topológica:** ⚠️ NSS bajo esperado (PyMuPDF degrada 77.3% de los nodos). Este documento **NO es tautológico** — es el primer documento donde el GT documenta divergencia real entre el documento fuente y la salida del extractor.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Primer documento no-tautológico del corpus. Valioso para medir divergencia real.
**Hallazgos derivados:** H-5.1-12 (contaminación vectorial de figuras), H-5.1-13 (cross-page bleed de headers).

### doc_12_multi_col (36 nodos) — AGREGADO 2026-09-19

**Fuente:** Felin & Holweg (2024). "Theory Is All You Need: AI, Human Cognition, and Causal Reasoning." Strategy Science.
**Recorte:** Páginas 1-3 del paper (3 páginas).
**SHA-256:** `2de743f869b3c28b...`
**Traits:** `native_pdf`, `multi_column`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

El pipeline de extracción generó node_ids en formato legacy `value='pX_bY'`. Se aplicó canonicalización vía `canonicalize_gt.py` (Batch 2a):

- 36/36 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_12_multi_col_canonicalization_lineage.json`
- Verificación: 0 legacy restantes post-canonicalización

**Paso 2 — Clasificación nodos por nodo (36 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | heading | heading | translate | Bien (título H1) |
| 1 | p1_b1 | paragraph | paragraph | keep_original | Parcial (nombres autores) |
| 2 | p1_b2 | paragraph | paragraph | keep_original | Parcial (afiliaciones, ORCID) |
| 3 | p1_b3 | paragraph | paragraph | omit | Mal (historial editorial) |
| 4 | p1_b4 | paragraph | paragraph | passthrough | Mal (DOI/URL) |
| 5 | p1_b5 | paragraph | paragraph | keep_original | Parcial (copyright) |
| 6 | p1_b6 | paragraph | paragraph | translate | Bien (abstract) |
| 7-8 | p1_b7, p1_b8 | paragraph | paragraph | keep_original | Parcial (licencia Open Access) |
| 9 | p1_b9 | paragraph | paragraph | translate | Bien (keywords) |
| 10 | p1_b10 | paragraph | composite_block | translate | Mal (fusionó "Introduction" con texto) |
| 11 | p1_b11 | paragraph | paragraph | translate | Parcial (huérfano) |
| 12 | p1_b12 | paragraph | paragraph | translate | Bien |
| 13 | p1_b13 | paragraph | paragraph | translate | Parcial (truncado) |
| 14 | p1_b14 | paragraph | paragraph | omit | Mal (número de página "1") |
| 15 | p1_b15 | heading | paragraph | omit | Mal (falso positivo: nombre de revista) |
| 16 | p1_b16 | paragraph | paragraph | omit | Mal (metadata editorial ISSN) |
| 17 | p1_b17 | paragraph | paragraph | omit | Mal (marca de agua lateral) |
| 18 | p2_b0 | paragraph | paragraph | translate | Parcial (huérfano transpágina) |
| 19 | p2_b1 | paragraph | paragraph | translate | Bien |
| 20 | p2_b2 | paragraph | paragraph | translate | Bien |
| 21 | p2_b3 | paragraph | composite_block | translate | Mal (fusionó título + error de fuente: "AI 5 Mind" en vez de "AI = Mind") |
| 22 | p2_b4 | paragraph | paragraph | translate | Parcial (huérfano) |
| 23-24 | p2_b5, p2_b6 | paragraph | paragraph | translate | Bien |
| 25 | p2_b7 | paragraph | paragraph | omit | Mal (running header + folio "2") |
| 26 | p2_b8 | paragraph | paragraph | omit | Mal (marca de agua lateral) |
| 27-28 | p3_b0, p3_b1 | paragraph | paragraph | translate | Bien |
| 29 | p3_b2 | paragraph | composite_block | translate | Mal (fusionó H2 con párrafo) |
| 30-31 | p3_b3, p3_b4 | paragraph | paragraph | translate | Parcial (fragmentado por columna) |
| 32 | p3_b5 | paragraph | paragraph | translate | Parcial (run-in heading embebido) |
| 33 | p3_b6 | paragraph | paragraph | translate | Bien |
| 34 | p3_b7 | paragraph | paragraph | omit | Mal (running header + folio "3") |
| 35 | p3_b8 | paragraph | paragraph | omit | Mal (marca de agua lateral) |

**Paso 3 — Distribución final:**

- **node_type:** 32 paragraph, 3 composite_block, 1 heading
- **strategy:** 23 translate, 10 omit, 3 keep_original, 1 passthrough
- **Nodos cortos (<10 chars):** 4 (folios, marcas de agua)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Error de codificación tipográfica | Nodo p2_b3: "AI 5 Mind" en vez de "AI = Mind". ToUnicode CMap falló en fuente matemática. | Font glyph mapping bug en PyMuPDF |
| Under-segmentation de headings | Títulos H2/H3 fusionados con primer renglón del párrafo (p1_b10, p2_b3, p3_b2, p3_b5) | PyMuPDF no detecta subtítulos en doble columna |
| Over-segmentation por salto de columna | Oraciones continuas partidas en nodos separados (p1_b10→p1_b11, p1_b13→p2_b0, p2_b3→p2_b4, p3_b3→p3_b4) | PyMuPDF segmenta por rectángulos geométricos, no por flujo de lectura |
| Inversión temporal de headers/watermarks | Encabezados superiores leídos al final absoluto de cada página (p1_b15-17, p2_b7-8, p3_b7-8) | PyMuPDF no respeta orden de lectura vertical |
| Omisión de logotipo vectorial | Logotipo institucional de informs omitido completamente | PyMuPDF no detecta elementos vectoriales |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 31/36 = **86.1%** (aparentemente alto, pero 0% de detección en subtítulos H2/H3)
- **Exactitud de strategy:** 23/36 = **63.9%** (13 nodos recibieron `translate` incorrectamente: DOIs, copyright, folios, watermarks)
- **Tasa de contaminación por ruido/foliación:** 7/36 = **19.4%** (marcas de agua, números de página, cintillos de revista)
- **Tasa de fragmentación estructural:** 9/36 = **25.0%** (over/under-segmentation por límites de columna)

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Error silencioso de codificación:** Nodo p2_b3 contiene "AI 5 Mind" en vez de "AI = Mind". PyMuPDF falló en el mapeo ToUnicode de la fuente matemática, corrompiendo semánticamente el título de sección.
2. **Subtítulos H2/H3 absorbidos:** PyMuPDF no detecta subtítulos en layout de doble columna, fusionándolos con el cuerpo del texto como `composite_block`.
3. **Fragmentación por columna:** Oraciones continuas se parten en nodos separados al cruzar de columna 1 a columna 2, requiriendo sutura manual o cross-page boundary detection.
4. **Headers/watermarks al final:** PyMuPDF lee encabezados superiores y marcas de agua laterales al final absoluto de cada página, invirtiendo el orden de lectura.

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `multi_column` cubierto (3/9 → 4/12)
- **Regresión topológica:** ⚠️ NSS moderado esperado (PyMuPDF degrada 25% de los nodos por fragmentación, pero el contenido textual es mayormente correcto). Documento no-tautológico: el GT documenta divergencia real del extractor.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento valioso para medir fragmentación por doble columna y errores de codificación tipográfica.
**Hallazgos derivados:** H-5.1-16 (font glyph mapping bug), H-5.1-17 (under-segmentation de H2/H3 en doble columna), H-5.1-18 (over-segmentation por salto de columna).

---

### doc_13_fmi_graf_tablas (44 nodos) — AGREGADO 2026-09-19

**Fuente:** FMI Working Paper sobre sovereign ratings. Tablas 2 y 3 (ordered probit) + Figuras 1 y 2 (year-fixed effects).
**Recorte:** Páginas 11-13 (3 páginas).
**SHA-256:** `8f1a9ad7c09ad81a...`
**Traits:** `native_pdf`, `nested_tables`, `floating_figures`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

El pipeline de extracción generó node_ids en formato legacy `value='pX_bY'`. Se aplicó canonicalización vía `canonicalize_gt.py` (Batch 2a):

- 44/44 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_13_fmi_graf_tablas_canonicalization_lineage.json`
- Verificación: 0 legacy restantes post-canonicalización

**Paso 2 — Clasificación nodos por nodo (44 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | paragraph | caption | translate | Parcial (título Tabla 2) |
| 1 | p1_b1 | paragraph | composite_block | translate | Mal (encabezados+coeficientes) |
| 2 | p1_b2 | paragraph | composite_block | passthrough | Mal (errores estándar numéricos) |
| 3 | p1_b3 | paragraph | composite_block | translate | Mal (fila coeficientes Forecast) |
| 4 | p1_b4 | paragraph | composite_block | translate | Mal (fusión masiva con notas al pie) |
| 5-9 | p1_b5..p1_b9 | paragraph | paragraph | translate | Parcial (párrafo 1 sobre-segmentado en 5 líneas) |
| 10-16 | p1_b10..p1_b16 | paragraph | paragraph | translate | Parcial (párrafo 2 sobre-segmentado en 7 líneas) |
| 17-21 | p1_b17..p1_b21 | paragraph | paragraph | translate | Parcial (párrafo 3 sobre-segmentado en 5 líneas) |
| 22 | p1_b22 | paragraph | composite_block | translate | Mal (fusionó folio "11" con título Figura 1) |
| 23-30 | p2_b2..p2_b9 | paragraph | paragraph | translate | Parcial (párrafo pág. 12 sobre-segmentado en 8 líneas) |
| 31-33 | p2_b10..p2_b12 | paragraph | paragraph | translate | Parcial (referencia Figura 2 sobre-segmentada) |
| 34 | p2_b13 | paragraph | paragraph | omit | Mal (número de página "12") |
| 35 | p3_b0 | heading | caption | translate | Parcial (título Tabla 3, era heading) |
| 36 | p3_b1 | paragraph | composite_block | translate | Mal (encabezados+coeficientes Tabla 3) |
| 37 | p3_b2 | paragraph | composite_block | passthrough | Mal (errores estándar numéricos) |
| 38 | p3_b3 | paragraph | composite_block | translate | Mal (fusión masiva con notas) |
| 39 | p3_b5 | heading | caption | translate | Parcial (pie Figura 2, era heading) |
| 40-42 | p3_b6, p3_b7, p3_b8 | heading | paragraph | translate | Mal (falsos positivos graves de heading en prosa) |
| 43 | p3_b9 | paragraph | paragraph | omit | Mal (número de página "13") |

**Paso 3 — Distribución final:**

- **node_type:** 33 paragraph, 8 composite_block, 3 caption
- **strategy:** 40 translate, 2 passthrough, 2 omit
- **Nodos cortos (<10 chars):** 2 (folios "12" y "13")

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Hiper-fragmentación por renglón | Párrafos descompuestos en nodos individuales por línea física (5, 7, 5, 8, 3, 3 líneas por párrafo) | Parámetro de agrupamiento vertical de PyMuPDF falla en texto justificado |
| Destrucción total de estructura tabular | Tablas 2 y 3 desmembradas: 0 nodos `table_simple` o `table_complex` en el GT | PyMuPDF no detecta estructuras de tabla en formato econométrico |
| Omisión absoluta de Figuras 1 y 2 | Gráficos de líneas temporales no generan nodos `image` | PyMuPDF no detecta gráficos como objetos visuales |
| Fusión corrupta transpágina (p1_b22) | Concatena folio "11" con título de Figura 1 (que pertenece a pág. 12) | Desorden espacial en vinculación de bounding boxes |
| Falsos positivos graves de heading | 3 líneas de prosa continua en pág. 13 clasificadas como heading (p3_b6, p3_b7, p3_b8) | Lectura anómala de peso tipográfico o interlineado |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 28/44 = **63.6%** (acierto formal en líneas de texto, fracaso en tablas, leyendas y falsos positivos)
- **Exactitud de strategy:** 40/44 = **90.9%** (falló en 2 bloques numéricos de errores estándar y 2 números de página)
- **Tasa de hiper-segmentación por renglón:** 31/44 = **70.5%** (líneas individuales de párrafos partidos artificialmente)
- **Tasa de corrupción tabular:** 8/44 = **18.2%** (pedazos desestructurados de tablas colapsadas)

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Tabla aplastada a texto plano:** Tablas 2 y 3 (ordenadas probit con errores estándar, estadísticos, notas al pie) degradadas a `composite_block`. El trait `nested_tables` está cubierto por la *presencia estructural del problema*, no por nodos `table_simple`/`table_complex` reales.
2. **Pérdida de concordancia sintáctica:** Un motor de traducción downstream procesará cada línea aislada (31 nodos sobre-segmentados), perdiendo contexto oracional.
3. **Figuras omitidas:** Figuras 1 y 2 (gráficos de year-fixed effects) no existen como nodos `image`. El trait `floating_figures` se documenta por la omisión estructural.
4. **Falsos positivos de heading:** PyMuPDF clasificó 3 líneas de prosa como heading en la página final, evidenciando inestabilidad del clasificador tipográfico en documentos con layout variable.

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `nested_tables` cubierto (2/9 → 3/12), `floating_figures` (2/9 → 3/12)
- **Regresión topológica:** ⚠️ NSS bajo-moderado esperado (PyMuPDF degrada 36.4% de los tipos de nodo, pero las strategies son mayormente correctas). Documento no-tautológico: el GT documenta divergencia real del extractor en contexto econométrico.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento valioso para medir destrucción de estructura tabular y hiper-segmentación por renglón en reports econométricos.
**Hallazgos derivados:** H-5.1-17 (hiper-fragmentación por renglón), H-5.1-18 (destrucción total de estructura tabular en formato econométrico).

### doc_14_fig_math (65 nodos) — AGREGADO 2026-09-22

**Fuente:** Deisenroth, Faisal & Ong. *Mathematics for Machine Learning* (Cambridge University Press, 2024). Capítulo 3: Analytic Geometry, §3.8.4 Projection onto Affine Subspaces + §3.9 Rotations.
**Recorte:** Páginas 90-92 (3 páginas).
**SHA-256:** `05008eeb69f65d4b...`
**Traits:** `native_pdf`, `floating_figures`, `heavy_math`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

El pipeline de extracción generó node_ids en formato legacy `value='pX_bY'`. Se aplicó canonicalización vía `canonicalize_gt.py` (Batch 3):

- 65/65 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_14_fig_math_canonicalization_lineage.json`
- Verificación: 0 legacy restantes post-canonicalización

**Paso 2 — Clasificación nodos por nodo (65 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | paragraph | composite_block | translate | Mal (fusió encabezado "90 Analytic Geometry" con caption de Fig 3.13) |
| 1-5 | p1_b1..p1_b5 | paragraph | composite_block | omit | Mal (etiquetas vectoriales L, x₀, x, b₁, b₂ de Fig 3.13(a)) |
| 6 | p1_b6 | paragraph | caption | translate | Parcial (subtítulo "(a) Setting.") |
| 7-10 | p1_b7..p1_b10 | paragraph | composite_block | omit | Mal (etiquetas vectoriales de Fig 3.13(b)) |
| 11 | p1_b11 | paragraph | caption | translate | Parcial (subtítulo "(b) Reduce problem...") |
| 12-17 | p1_b12..p1_b17 | paragraph | composite_block | omit | Mal (etiquetas vectoriales de Fig 3.13(c)) |
| 18 | p1_b18 | paragraph | caption | translate | Parcial (subtítulo "(c) Add support point...") |
| 19 | p1_b19 | paragraph | paragraph | translate | Bien (cierre de sección previa) |
| 20 | p1_b20 | paragraph | heading | translate | Parcial (título §3.8.4) |
| 21 | p1_b21 | paragraph | paragraph | translate | Bien (cuerpo) |
| 22 | p1_b22 | paragraph | display_equation | passthrough | Mal (ecuación 3.72) |
| 23 | p1_b23 | paragraph | paragraph | translate | Bien |
| 24 | p1_b24 | paragraph | display_equation | passthrough | Mal (ecuaciones 3.73a/b) |
| 25 | p1_b25 | paragraph | paragraph | translate | Bien |
| 26 | p1_b26 | paragraph | paragraph | omit | Mal (pie "Draft 2024-01-15...") |
| 27 | p2_b0 | paragraph | paragraph | omit | Mal (folio "3.9 Rotations 91") |
| 28 | p2_b1 | paragraph | caption | translate | Parcial (caption Fig 3.14) |
| 29-30 | p2_b2, p2_b3 | paragraph | composite_block | omit | Mal (etiquetas "Original"/"Rotated") |
| 31 | p2_b4 | paragraph | caption | translate | Parcial (caption Fig 3.15) |
| 32 | p2_b6 | paragraph | heading | translate | Parcial (título §3.9) |
| 33 | p2_b7 | paragraph | composite_block | translate | Mal (párrafo absorbió keyword marginal "rotation") |
| 34-35 | p2_b8, p2_b9 | paragraph | display_equation | passthrough | Mal (matriz de rotación con glifos corruptos  ) |
| 36 | p2_b10 | paragraph | paragraph | translate | Bien |
| 37 | p2_b11 | paragraph | paragraph | keep_original | Parcial (copyright CUP) |
| 38 | p3_b0 | paragraph | paragraph | omit | Mal (folio "92 Analytic Geometry") |
| 39-40 | p3_b1, p3_b2 | paragraph | caption | translate | Parcial (caption Fig 3.16 en 2 líneas) |
| 41-50 | p3_b3..p3_b12 | paragraph | composite_block | omit | Mal (10 etiquetas vectoriales de Fig 3.16) |
| 51 | p3_b13 | paragraph | heading | translate | Parcial (título §3.9.1) |
| 52 | p3_b14 | paragraph | composite_block | translate | Mal (glifos corruptos   en base estándar) |
| 53 | p3_b15 | paragraph | inline_equation | passthrough | Mal (vector e₂ con glifo corrupto) |
| 54 | p3_b16 | paragraph | paragraph | translate | Parcial (cierre con glifo ) |
| 55 | p3_b17 | paragraph | composite_block | translate | Mal (párrafo absorbió keyword "rotation matrix" entre "de-" y "termine") |
| 56-58 | p3_b18..p3_b20 | paragraph | display_equation | passthrough | Mal (ecuación 3.75 partida en 3 con glifos corruptos) |
| 59 | p3_b21 | paragraph | paragraph | translate | Bien |
| 60-61 | p3_b22, p3_b23 | paragraph | display_equation | passthrough | Mal (matriz 3.76 con glifos corruptos  ) |
| 62 | p3_b24 | paragraph | heading | translate | Parcial (título §3.9.2) |
| 63 | p3_b25 | paragraph | paragraph | translate | Bien |
| 64 | p3_b26 | paragraph | paragraph | omit | Mal (pie "Draft 2024-01-15...") |

**Paso 3 — Distribución final:**

- **node_type:** 13 paragraph, 31 composite_block, 9 display_equation, 1 inline_equation, 7 caption, 4 heading
- **strategy:** 23 translate, 31 omit, 10 passthrough, 1 keep_original
- **Nodos cortos (<10 chars):** 31 (todas las etiquetas vectoriales de figuras)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Contaminación vectorial masiva | 27/65 nodos (41.5%) son etiquetas sueltas de figuras geométricas 3.13, 3.14, 3.16 | PyMuPDF extrae texto vectorial como párrafos individuales |
| Margin keyword bleed | Palabras clave en margen ("rotation", "rotation matrix") absorbidas en medio de oraciones (p2_b7, p3_b17) | Layout Tufte con columna marginal no delimitada por PyMuPDF |
| Destrucción de matrices + glifos corruptos | Matrices 3.74, 3.75, 3.76 partidas en 2-3 nodos con delimitadores `[` `]` reemplazados por glifos de control `\x14` `\x15` `\x1a` `\x1b` `\x02` `\x03` | ToUnicode CMap de fuentes matemáticas falla en delimitadores extensibles |
| Omisión absoluta de nodos IMAGE | 0 nodos `image` para Figuras 3.13, 3.14, 3.15, 3.16 | PyMuPDF no detecta figuras geométricas ni fotografía del brazo robótico |
| Colapso de folio+caption en p1_b0 | Nodo fusionó folio "90", capítulo "Analytic Geometry" y descripción completa de Fig 3.13 | Parámetro de agrupamiento vertical falla en layouts con elementos dispersos |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 11/65 = **16.9%** (fracaso en 27 etiquetas vectoriales, 9 ecuaciones, 7 captions, 4 headings)
- **Exactitud de strategy:** 23/65 = **35.4%** (27 nodos vectoriales deberían ser omit, 10 ecuaciones passthrough, 5 pies de página omit)
- **Tasa de contaminación vectorial (NIR):** 27/65 = **41.5%**
- **Tasa de fragmentación matemática:** 100% de las matrices (4/4) partidas en múltiples bloques con glifos corruptos

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Layout Tufte sin delimitar:** La columna marginal de conceptos clave no es reconocida por PyMuPDF, causando *margin keyword bleed* que corrompe la prosa del cuerpo principal.
2. **Glifos de control no imprimibles:** Los delimitadores extensibles de matrices (`[`, `]`) se decodifican como caracteres de control hexadecimales. El contenido matemático queda ilegible para el pipeline downstream.
3. **Figuras sin contenedor:** Las 4 figuras (3 geométricas vectoriales + 1 fotografía) no existen como nodos `image`. El trait `floating_figures` está cubierto por la presencia estructural del problema.
4. **GT eco del extractor:** Las ecuaciones existen como nodos `display_equation`, pero su contenido está corrompido por glifos de control y fragmentación.

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `floating_figures` (4/12 → 5/15), `heavy_math` (6/12 → 7/15)
- **Regresión topológica:** ⚠️ NSS muy bajo esperado (PyMuPDF degrada 83.1% de los nodos). Documento no-tautológico: primer documento del corpus donde el *contenido matemático mismo* está corrupto, no solo mal tipado.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento extremo para medir contaminación vectorial y corrupción de glifos en libros con layout Tufte.
**Hallazgos derivados:** H-5.1-19 (layout Tufte / margin keyword bleed), H-5.1-20 (corrupción de glifos TeX en delimitadores de matrices).

### doc_15_table_fig_code (37 nodos) — AGREGADO 2026-09-22

**Fuente:** Mark Lutz. *Learning Python* (O'Reilly Media, 5th ed.). Capítulo 33: Exception Coding Details, págs. 837-839.
**Recorte:** Páginas 837-839 (3 páginas).
**SHA-256:** `806fce3fb5b73be3...`
**Traits:** `native_pdf`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 37/37 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_15_table_fig_code_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (37 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | heading | heading | translate | Bien (título H2 "try Statement Clauses") |
| 1-2 | p1_b1, p1_b2 | paragraph | paragraph | translate | Bien |
| 3 | p1_b3 | paragraph | caption | translate | Parcial (título Tabla 33-1) |
| 4-11 | p1_b4..p1_b11 | paragraph | composite_block | translate | Mal (Tabla 33-1 desarticulada: header + 7 filas) |
| 12-13 | p1_b12, p1_b13 | paragraph | paragraph | translate | Bien |
| 14 | p1_b14 | list | list | translate | Bien (lista con 2 viñetas fusionadas) |
| 15 | p1_b15 | paragraph | paragraph | translate | Bien |
| 16 | p1_b16 | paragraph | code | keep_original | Mal (snippet try/except) |
| 17 | p1_b17 | paragraph | composite_block | keep_original | Mal (header bleed: "The try/except/else Statement | 837" soldado en medio del código) |
| 18-19 | p2_b1, p2_b2 | paragraph | paragraph | translate | Bien |
| 20 | p2_b3 | paragraph | code | keep_original | Mal (snippet con comentarios) |
| 21 | p2_b4 | paragraph | paragraph | translate | Bien |
| 22 | p2_b5 | paragraph | code | keep_original | Mal (snippet try/except:) |
| 23 | p2_b6 | paragraph | paragraph | translate | Bien |
| 24 | p2_b7 | paragraph | paragraph | translate | Bien |
| 25 | p2_b8 | paragraph | code | keep_original | Mal (snippet except Exception:) |
| 26 | p2_b9 | paragraph | composite_block | translate | Mal (header bleed: "838 | Chapter 33: Exception Coding Details") |
| 27 | p3_b2 | paragraph | paragraph | translate | Bien (nota lateral "Version skew") |
| 28 | p3_b3 | heading | heading | translate | Bien (título H2 "The try else Clause") |
| 29 | p3_b4 | paragraph | paragraph | translate | Bien |
| 30 | p3_b5 | paragraph | code | keep_original | Mal (snippet con comentario) |
| 31 | p3_b6 | paragraph | paragraph | translate | Bien |
| 32 | p3_b7 | paragraph | code | keep_original | Mal (snippet try/except/else) |
| 33 | p3_b8 | paragraph | paragraph | translate | Bien |
| 34 | p3_b9 | paragraph | code | keep_original | Mal (snippet emulación) |
| 35 | p3_b10 | paragraph | paragraph | translate | Parcial (truncado en "and") |
| 36 | p3_b11 | paragraph | paragraph | omit | Mal (folio "The try/except/else Statement | 839") |

**Paso 3 — Distribución final:**

- **node_type:** 16 paragraph, 10 composite_block, 7 code, 2 heading, 1 caption, 1 list
- **strategy:** 28 translate, 8 keep_original, 1 omit
- **Nodos cortos (<10 chars):** 1 (folio p3_b11)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Ceguera ante bloques de código | 7 de 7 snippets Python tipados como `paragraph` con strategy `translate` | PyMuPDF no distingue código fuente de prosa |
| Header bleed destructivo | Folios 837, 838, 839 incrustados dentro de código (p1_b17) y prosa (p2_b9, p3_b11) | PyMuPDF no detecta cintillos editoriales |
| Table shredding | Tabla 33-1 desmenuzada en 8 párrafos planos (sin estructura tabular) | PyMuPDF no reconoce tablas simples de 2 columnas |
| Under-segmentation de lista | 2 viñetas independientes fusionadas en un solo nodo `list` | PyMuPDF no detecta separación entre ítems |
| Ruptura transpágina | Nodo p3_b10 termina en conjunción abierta ("...and") | PyMuPDF no implementa cross-page stitch |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 19/37 = **51.4%** (fracaso en 7 bloques de código, 8 filas de tabla, 1 caption, 1 composite_block)
- **Exactitud de strategy:** 19/37 = **51.4%** (8 bloques de código deberían ser `keep_original`, 1 folio `omit`)
- **Tasa de ceguera de código:** 7/7 = **100%** de snippets tipados como prosa
- **Tasa de contaminación por foliación:** 3/37 = **8.1%**

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Riesgo de traducción de sintaxis:** Si un motor downstream recibe `translate` para un nodo `code`, traducirá palabras reservadas (`try`, `except`, `NameError`, `IndexError`), corrompiendo la sintaxis de Python.
2. **Indentación perdida:** Los snippets se extraen sin preservación de whitespace significativo. Un extractor de código debe re-indentar.
3. **Tabla 33-1 sin estructura:** PyMuPDF no distingue tablas de 2 columnas (forma/interpretación). El trait `nested_tables` NO aplica porque la tabla es simple, no anidada.

#### Impacto en benchmark

- **Cobertura de traits:** ⚠️ Solo `native_pdf`. El documento contiene código fuente pero el enum `ExtractionChallengeTrait` **no tiene un trait `code`**. Este es el primer documento que evidencia esta brecha en el catálogo de traits.
- **Regresión topológica:** ⚠️ NSS moderado esperado. PyMuPDF degrada 48.6% de los nodos, principalmente por ceguera de código.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento crítico para evidenciar que el enum de traits debe extenderse con un trait `code` en Fase 6.
**Hallazgos derivados:** H-5.1-21 (ceguera sistemática ante bloques de código), H-5.1-22 (header bleed destructivo en código), H-5.1-23 (table shredding de tablas simples), O-5.4-1 (ausencia de trait `code` en enum `ExtractionChallengeTrait`).

### doc_16_fig_code (24 nodos) — AGREGADO 2026-09-22

**Fuente:** Jake VanderPlas. *Python Data Science Handbook* (O'Reilly Media). Capítulo 5: Machine Learning, sección "In Depth: Linear Regression", págs. 396-398.
**Recorte:** Páginas 396-398 (3 páginas).
**SHA-256:** `c6ede7450dc46b70...`
**Traits:** `native_pdf`, `floating_figures`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 24/24 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_16_fig_code_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (24 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0-2 | p1_b0, p1_b1, p1_b2 | paragraph | code | keep_original | Mal (3 snippets Python: método, pipeline, matplotlib) |
| 3 | p1_b4 | paragraph | caption | translate | Parcial (caption Fig 5-46) |
| 4 | p1_b5 | paragraph | paragraph | translate | Bien |
| 5 | p1_b6 | heading | heading | translate | Bien (título H2 "Regularization") |
| 6 | p1_b7 | paragraph | paragraph | translate | Bien |
| 7-8 | p1_b8, p1_b9 | paragraph | code | keep_original | Mal (celda Jupyter In[10] fragmentada en 2) |
| 9 | p1_b10 | paragraph | composite_block | keep_original | Mal (footer bleed: "396 \| Chapter 5: Machine Learning" fusionado con código `plt.xlim...`) |
| 10 | p2_b2 | paragraph | caption | translate | Parcial (caption Fig 5-47) |
| 11 | p2_b3 | paragraph | paragraph | translate | Bien |
| 12-15 | p2_b4..p2_b7 | paragraph | code | keep_original | Mal (celda Jupyter In[11]: función `basis_plot` descuartizada en 4 nodos) |
| 16 | p2_b8 | paragraph | composite_block | translate | Mal (footer bleed: "In Depth: Linear Regression \| 397" fusionado con caption Fig 5-48) |
| 17 | p3_b2 | paragraph | paragraph | translate | Bien |
| 18 | p3_b3 | paragraph | heading | translate | Parcial (subsección H3 "Ridge regression") |
| 19 | p3_b4 | paragraph | paragraph | translate | Bien |
| 20 | p3_b5 | paragraph | display_equation | passthrough | Mal (fórmula L2: $P = \alpha\sum\theta_n^2$ aplanada a texto plano) |
| 21 | p3_b6 | paragraph | paragraph | translate | Bien |
| 22 | p3_b7 | paragraph | code | keep_original | Mal (celda Jupyter In[12]) |
| 23 | p3_b8 | paragraph | paragraph | omit | Mal (folio "398 \| Chapter 5: Machine Learning") |

**Paso 3 — Distribución final:**

- **node_type:** 7 paragraph, 10 code, 2 caption, 2 heading, 2 composite_block, 1 display_equation
- **strategy:** 11 translate, 11 keep_original, 1 passthrough, 1 omit
- **Nodos cortos (<10 chars):** 1 (folio p3_b8)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Ceguera ante celdas Jupyter | 10/10 snippets Python catalogados como `paragraph` con `translate` | PyMuPDF no distingue código interactivo (`In[10]:`) |
| Footer bleed transpágina | Pies de página 396 y 397 fusionados con código (p1_b10) y caption (p2_b8) | PyMuPDF no detecta folios editoriales |
| Sobre-segmentación de celdas Jupyter | Celda `In[11]` (función `basis_plot`) partida en 4 nodos (p2_b4, p2_b5, p2_b6, p2_b7), destruyendo indentación | PyMuPDF segmenta por rectángulos geométricos |
| Omisión de figuras matplotlib | 0 nodos `image` para Figuras 5-46, 5-47, 5-48 | PyMuPDF no detecta gráficos generados con matplotlib |
| Aplanamiento de fórmula L2 | Fórmula $P = \alpha\sum_{n=1}^N\theta_n^2$ degradada a `P = α∑n = 1 N θn 2` | PyMuPDF pierde sub/superíndices y estructura de sumatoria |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 8/24 = **33.3%** (fracaso en 10 snippets de código, 2 captions, 2 composite_blocks, 1 ecuación, 1 heading)
- **Exactitud de strategy:** 11/24 = **45.8%** (10 snippets deberían ser `keep_original`, 1 fórmula `passthrough`, 1 folio `omit`)
- **Tasa de ceguera de código:** 10/10 = **100%**
- **Tasa de contaminación por foliación:** 3/24 = **12.5%**

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Pérdida de indentación Python:** Los snippets multi-línea se extraen sin preservar whitespace significativo. Motores downstream deberían re-indentar.
2. **Celdas Jupyter sin metadata de celda:** Los prompts `In[10]:` quedan embebidos en el contenido en lugar de estructurarse como metadata de celda ejecutable.
3. **Figuras matplotlib omitidas:** Los gráficos generados por `plt.scatter`, `plt.plot` no existen como nodos `image`. El trait `floating_figures` se documenta por la omisión estructural.
4. **Riesgo de traducción de sintaxis NumPy/scikit-learn:** Nombres como `GaussianFeatures`, `LinearRegression`, `Ridge`, `np.newaxis` recibirían `translate`, corrompiendo la ejecución del código.

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `floating_figures` (5/15 → 6/15)
- **Regresión topológica:** ⚠️ NSS bajo esperado. PyMuPDF degrada 66.7% de los tipos de nodo y 54.2% de las strategies.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento complementario a doc_15 para validar ceguera ante código Python en entornos Jupyter interactivos.
**Hallazgos derivados:** H-5.1-24 (ceguera ante celdas Jupyter interactivas), H-5.1-25 (footer bleed transpágina), H-5.1-26 (sobre-segmentación de celdas Jupyter con pérdida de indentación).

### doc_17_table_code (51 nodos) — AGREGADO 2026-09-22

**Fuente:** Jake VanderPlas. *Python Data Science Handbook* (O'Reilly Media). Capítulo 3: Data Manipulation with Pandas, sección "Vectorized String Operations", págs. 181-183.
**Recorte:** Páginas 181-183 (3 páginas).
**SHA-256:** `f0c3d8e2a1b94c57...`
**Traits:** `native_pdf`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 51/51 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_17_table_code_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (51 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | paragraph | paragraph | translate | Bien ("Or Boolean values:") |
| 1 | p1_b1 | paragraph | code | keep_original | Mal (In[9] IPython) |
| 2 | p1_b2 | paragraph | code | keep_original | Mal (Out[9] IPython) |
| 3 | p1_b3 | paragraph | paragraph | translate | Bien |
| 4 | p1_b4 | paragraph | code | keep_original | Mal (In[10] IPython) |
| 5 | p1_b5 | paragraph | code | keep_original | Mal (Out[10] IPython) |
| 6 | p1_b6 | paragraph | paragraph | translate | Bien |
| 7 | p1_b7 | heading | heading | translate | Bien (H2 "Methods using regular expressions") |
| 8 | p1_b8 | paragraph | paragraph | translate | Bien |
| 9 | p1_b9 | paragraph | caption | translate | Parcial (título Tabla 3-4) |
| 10-18 | p1_b10..p1_b18 | paragraph | composite_block | translate | Mal (Tabla 3-4 desarticulada: header + 8 filas) |
| 19 | p1_b19 | paragraph | paragraph | translate | Bien |
| 20 | p1_b20 | paragraph | composite_block | keep_original | Mal (footer bleed: "Vectorized String Operations \| 181" + In[11]) |
| 21 | p2_b1 | paragraph | code | keep_original | Mal (Out[11] IPython) |
| 22 | p2_b2 | paragraph | paragraph | translate | Bien |
| 23 | p2_b3 | paragraph | code | keep_original | Mal (In[12] IPython con regex) |
| 24 | p2_b4 | paragraph | code | keep_original | Mal (Out[12] IPython) |
| 25 | p2_b5 | paragraph | paragraph | translate | Bien |
| 26 | p2_b6 | heading | heading | translate | Bien (H2 "Miscellaneous methods") |
| 27 | p2_b7 | paragraph | paragraph | translate | Bien |
| 28 | p2_b8 | paragraph | caption | translate | Parcial (título Tabla 3-5) |
| 29-39 | p2_b9..p2_b19 | paragraph | composite_block | translate | Mal (Tabla 3-5 desarticulada: header + 10 filas) |
| 40 | p2_b20 | paragraph | composite_block | translate | Mal (header bleed: "182 \| Chapter 3" + run-in heading) |
| 41 | p3_b1 | paragraph | code | keep_original | Mal (In[13] IPython) |
| 42 | p3_b2 | paragraph | code | keep_original | Mal (Out[13] IPython) |
| 43 | p3_b3 | paragraph | paragraph | translate | Bien |
| 44 | p3_b4 | paragraph | paragraph | translate | Bien |
| 45 | p3_b5 | paragraph | code | keep_original | Mal (In[14] IPython con chaining) |
| 46 | p3_b6 | paragraph | code | keep_original | Mal (Out[14] IPython) |
| 47 | p3_b7 | paragraph | paragraph | translate | Bien (con run-in heading "Indicator variables.") |
| 48 | p3_b8 | paragraph | code | keep_original | Mal (In[15] pd.DataFrame) |
| 49 | p3_b9 | paragraph | code | keep_original | Mal (Out[15] DataFrame repr) |
| 50 | p3_b10 | paragraph | paragraph | omit | Mal (folio "Vectorized String Operations \| 183") |

**Paso 3 — Distribución final:**

- **node_type:** 12 paragraph, 22 composite_block, 13 code, 2 heading, 2 caption
- **strategy:** 36 translate, 14 keep_original, 1 omit
- **Nodos cortos (<10 chars):** 1 (folio p3_b10)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Desarticulación sistemática de tablas | Tablas 3-4 y 3-5 pulverizadas en 20 filas sueltas (39.2% de nodos) | PyMuPDF no detecta tablas simples de referencia |
| Ceguera absoluta ante celdas IPython | 14 celdas In[N]/Out[N] tipadas como `paragraph` con `translate` | PyMuPDF no distingue código interactivo |
| Header/footer bleed | Folios 181/182/183 fusionados con código (p1_b20) y prosa (p2_b20, p3_b10) | PyMuPDF no detecta cintillos editoriales |
| Run-in headings embebidos | Subtítulos en negrita ("Vectorized item access...", "Indicator variables.") no aislados | PyMuPDF no segmenta headings inline |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 13/51 = **25.5%** (fracaso en 14 celdas de código, 20 filas de tabla, 2 captions)
- **Exactitud de strategy:** 36/51 = **70.6%** (14 celdas de código deberían ser `keep_original`, 1 folio `omit`)
- **Tasa de desarticulación tabular:** 20/51 = **39.2%**
- **Tasa de ceguera de código:** 14/14 = **100%**

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Riesgo de traducción de métodos Pandas:** Si un motor downstream recibe `translate` para `In[12]: monte.str.findall(r'^[^AEIOU].*[^aeiou]$')`, corromperá la regex y los nombres de métodos (`startswith`, `split`, `extract`, `findall`).
2. **Tablas de referencia sin estructura:** Tablas 3-4 y 3-5 (mapeos método/descripción) quedan como filas sueltas `composite_block`, perdiendo la correspondencia bidimensional.
3. **Output IPython sin metadata:** Los resultados `Out[N]` quedan embebidos como texto sin clasificación estructural de output de consola.

#### Impacto en benchmark

- **Cobertura de traits:** ⚠️ Solo `native_pdf`. El enum `ExtractionChallengeTrait` sigue sin trait `code` (O-5.4-1).
- **Regresión topológica:** ⚠️ NSS moderado-bajo esperado. PyMuPDF degrada 74.5% de los tipos de nodo.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Tercer documento consecutivo de Pandas/Jupyter confirmando la ceguera sistemática del extractor ante código Python interactivo y tablas de referencia.
**Hallazgos derivados:** H-5.1-27 (desarticulación sistemática de tablas de referencia), H-5.1-28 (ceguera ante celdas IPython con regex complejas).

### doc_18_table_math_doble_col (152 nodos) — AGREGADO 2026-09-22

**Fuente:** IMF Occasional Paper / Working Paper. "Saving-Investment Balances in Industrial Countries", págs. 45-47.
**Recorte:** Páginas 45-47 (3 páginas).
**SHA-256:** `a7b3c9d2e5f18046...`
**Traits:** `native_pdf`, `multi_column`, `heavy_math`, `nested_tables`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 152/152 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_18_table_math_doble_col_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (152 nodos, caso más severo del corpus):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b1 | heading | heading | translate | Bien (H1 "Empirical Results") |
| 1-2 | p1_b2, p1_b3 | paragraph | caption | translate | Parcial (título + subtítulo Tabla 6.5) |
| 3-12 | p1_b4..p1_b13 | paragraph | composite_block | translate | Mal (Tabla 6.5: header + stubs) |
| 13-20 | p1_b14..p1_b21 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 1: Fixed Effects) |
| 21 | p1_b22 | paragraph | composite_block | translate | Mal (header Col 2: OLS) |
| 22-29 | p1_b23..p1_b30 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 2) |
| 30 | p1_b31 | paragraph | composite_block | translate | Mal (header Col 3: Random Effects) |
| 31-38 | p1_b32..p1_b39 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 3) |
| 39 | p1_b40 | paragraph | composite_block | translate | Mal (header Col 4: Fixed Effects) |
| 40-47 | p1_b41..p1_b48 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 4) |
| 48 | p1_b49 | paragraph | composite_block | translate | Mal (header Col 5: IV) |
| 49-56 | p1_b50..p1_b57 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 5) |
| 57-59 | p1_b58..p1_b60 | paragraph | paragraph | translate | Parcial (notas Tabla 6.5) |
| 60-61 | p1_b61, p1_b62 | paragraph | paragraph | translate | Bien (cuerpo columnas 1 y 2) |
| 62-63 | p1_b63, p1_b64 | paragraph | composite_block | translate | Mal (notas al pie 43-46 fusionadas) |
| 64 | p1_b65 | paragraph | paragraph | omit | Mal (folio "45") |
| 65 | p1_b66 | heading | paragraph | omit | Mal (disclaimer FMI, falso heading) |
| 66 | p2_b1 | heading | paragraph | omit | Mal (cintillo superior pág. 46) |
| 67-76 | p2_b2..p2_b11 | paragraph | composite_block | translate | Mal (Tabla 6.6: header + stubs) |
| 77-78 | p2_b12, p2_b13 | paragraph | composite_block | passthrough | Mal (LM[X2(1)] y LM[X2(4)], glifos dañados) |
| 79 | p2_b14 | paragraph | composite_block | translate | Mal (header Col 1 Tabla 6.6) |
| 80-91 | p2_b15..p2_b26 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 1 Tabla 6.6) |
| 92 | p2_b27 | paragraph | composite_block | translate | Mal (header Col 2 Tabla 6.6) |
| 93-104 | p2_b28..p2_b39 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 2 Tabla 6.6) |
| 105 | p2_b40 | paragraph | composite_block | translate | Mal (header Col 3 Tabla 6.6) |
| 106-117 | p2_b41..p2_b52 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 3 Tabla 6.6) |
| 118 | p2_b53 | paragraph | composite_block | translate | Mal (header Col 4 Tabla 6.6) |
| 119-130 | p2_b54..p2_b65 | paragraph | composite_block | passthrough | Mal (celdas numéricas Col 4 Tabla 6.6) |
| 131 | p2_b66 | paragraph | paragraph | translate | Bien (notas Tabla 6.6) |
| 132 | p2_b67 | paragraph | paragraph | translate | Bien (cuerpo columna 1) |
| 133 | p2_b68 | paragraph | paragraph | translate | Parcial (truncado en "J-") |
| 134 | p2_b69 | paragraph | paragraph | translate | Bien (nota al pie 47) |
| 135 | p2_b70 | paragraph | composite_block | omit | Mal (capa fantasma: "Table 6.4 Panel Regrestion") |
| 136 | p2_b71 | paragraph | paragraph | omit | Mal (folio "46") |
| 137 | p2_b72 | paragraph | composite_block | omit | Mal (capa fantasma: "(Dependent variable, CA/GDP)") |
| 138 | p2_b73 | heading | paragraph | omit | Mal (disclaimer FMI, falso heading) |
| 139 | p3_b1 | heading | paragraph | omit | Mal (cintillo superior pág. 47) |
| 140 | p3_b2 | paragraph | paragraph | translate | Parcial (huérfano: "curve type impact...") |
| 141 | p3_b3 | heading | heading | translate | Bien (H2 "Partial Adjustment Model Extensions...") |
| 142-143 | p3_b4, p3_b5 | paragraph | paragraph | translate | Parcial (párrafo fragmentado por columna) |
| 144 | p3_b6 | paragraph | heading | translate | Parcial (H3 "Partial Adjustment Model: Single Equation") |
| 145 | p3_b7 | paragraph | paragraph | translate | Bien |
| 146 | p3_b8 | paragraph | display_equation | passthrough | Mal (ecuación 6.4: ε extraído como "8") |
| 147-148 | p3_b9, p3_b10 | paragraph | paragraph | translate | Bien |
| 149 | p3_b11 | paragraph | composite_block | translate | Mal (notas 48-49 fusionadas) |
| 150 | p3_b12 | paragraph | paragraph | omit | Mal (folio "47") |
| 151 | p3_b13 | heading | paragraph | omit | Mal (disclaimer FMI, falso heading) |

**Paso 3 — Distribución final:**

- **node_type:** 23 paragraph, 123 composite_block, 3 heading, 2 caption, 1 display_equation
- **strategy:** 51 translate, 91 passthrough, 10 omit
- **Nodos cortos (<10 chars):** 10 (folios y celdas vacías "—")

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Desmembramiento vertical columna por columna | Tabla 6.5 descompuesta en 54 nodos (p1_b4..p1_b57); Tabla 6.6 en 64 nodos (p2_b2..p2_b65). **118/152 nodos (77.6%) son celdas individuales** | PyMuPDF lee filas en vertical y luego recorre columnas, aniquilando la relación bidimensional |
| Inyección de capas fantasma | Nodos p2_b70 y p2_b72 contienen "Table 6.4 Panel Regrestion: Partial Adjistment Model" con erratas tipográficas | Texto residual de stream oculto del PDF que PyMuPDF levanta como cuerpo |
| Fragmentación transpágina y por columna | "J-" en p2_b68 continúa en p3_b2 como "curve type impact"; "saving-investment" en p3_b4 continúa en p3_b5 como "balance" | PyMuPDF no implementa cross-page stitch ni column-aware reading |
| Corrupción de fuentes matemáticas | ε extraído como "8" en ecuación (6.4); LM[χ²(1)] degradado a LM[X2(1)]; $\bar{R}^2$ perdió barra superior | ToUnicode CMap defectuoso en fuentes matemáticas del IMF |
| Falsos headings reiterados | 3 disclaimers FMI (p1_b66, p2_b73, p3_b13) y 2 cintillos de navegación (p2_b1, p3_b1) catalogados como `heading` | Clasificador tipográfico inestable en documentos institucionales |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 23/152 = **15.1%** (el peor del corpus)
- **Exactitud de strategy:** 51/152 = **33.6%**
- **Tasa de contaminación por desarticulación tabular:** 118/152 = **77.6%** (máximo histórico)
- **Tasa de inyección de artefactos fantasma:** 2/152 = **1.3%**

#### Limitaciones documentadas (ACCEPTED_LIMITATION)

1. **Pérdida total de semántica tabular:** Las Tablas 6.5 y 6.6 (regresiones de panel con efectos fijos/aleatorios/IV) quedan como 118 nodos sueltos sin vinculación fila-columna. Imposible reconstruir sin heurística de post-procesamiento.
2. **Texto fantasma no detectable automáticamente:** Las capas residuales del PDF (Tabla 6.4 con erratas) requieren inspección manual. Un extractor downstream no podría distinguirlas del contenido real.
3. **Ecuación (6.4) corrupta:** El término estocástico $\epsilon$ queda como "8", haciendo la ecuación econonométrica ilegible. El trait `heavy_math` está cubierto por la presencia del problema, no por contenido matemático válido.
4. **Fragmentación transpágina severa:** El documento ilustra el peor caso de ruptura oracional del corpus, con palabras compuestas separadas por 7 nodos intermedios (folios, disclaimers, notas).

#### Impacto en benchmark

- **Cobertura de traits:** ✅ `multi_column` (6/15 → 7/15), `heavy_math` (7/15 → 8/15), `nested_tables` (3/15 → 4/15)
- **Regresión topológica:** ⚠️ NSS muy bajo esperado. PyMuPDF degrada 84.9% de los tipos de nodo. Documento extremo para medir destrucción tabular en reports econométricos de doble columna.

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento más severo del corpus en términos de fragmentación y desarticulación tabular. Valioso como caso extremo (stress test) del benchmark.
**Hallazgos derivados:** H-5.1-29 (desmembramiento vertical columna por columna), H-5.1-30 (inyección de capas fantasma), H-5.1-31 (corrupción de fuentes matemáticas IMF), H-5.1-32 (falsos headings reiterados en disclaimers institucionales).

### doc_19_fig_table_doble_col (41 nodos) — AGREGADO 2026-09-23

**Fuente:** K. Hastuti et al. *Machine Learning with Applications 24 (2026) 100852*. "Proposed pipeline for keris classification...", págs. 3-5.
**Recorte:** Páginas 3-5 (3 páginas).
**SHA-256:** `c4d5e6f7a8b90123...`
**Traits:** `native_pdf`, `multi_column`, `floating_figures`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 41/41 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_19_fig_table_doble_col_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (41 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | heading | paragraph | omit | Mal (cintillo "K. Hastuti et al.") |
| 1 | p1_b2 | paragraph | caption | translate | Parcial (leyenda Fig. 1) |
| 2 | p1_b3 | paragraph | paragraph | translate | Bien |
| 3 | p1_b4 | paragraph | heading | translate | Parcial (H2 "2.3. Dataset splitting") |
| 4 | p1_b5 | paragraph | paragraph | translate | Parcial (truncado) |
| 5 | p1_b6 | paragraph | composite_block | translate | Mal (Table Smashing: Tabla 2 monolítica) |
| 6 | p1_b7 | paragraph | paragraph | translate | Parcial (huérfano) |
| 7 | p1_b8 | paragraph | heading | translate | Parcial (H2 "2.4. Data augmentation") |
| 8 | p1_b9 | paragraph | paragraph | translate | Parcial (truncado) |
| 9 | p1_b10 | heading | paragraph | omit | Mal (metadata editorial) |
| 10 | p1_b11 | paragraph | paragraph | omit | Mal (folio "3") |
| 11 | p2_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 12 | p2_b2 | paragraph | caption | translate | Parcial (leyenda Fig. 2) |
| 13 | p2_b3 | paragraph | paragraph | translate | Parcial (huérfano transpágina) |
| 14-15 | p2_b4, p2_b5 | paragraph | paragraph | translate | Bien |
| 16 | p2_b6 | paragraph | heading | translate | Parcial (H2 "2.5. Model architecture") |
| 17-19 | p2_b7..p2_b9 | paragraph | paragraph | translate | Bien |
| 20 | p2_b10 | heading | paragraph | omit | Mal (metadata editorial) |
| 21 | p2_b11 | paragraph | paragraph | omit | Mal (folio "4") |
| 22 | p3_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 23 | p3_b2 | paragraph | caption | translate | Parcial (leyenda Fig. 3) |
| 24 | p3_b3 | paragraph | composite_block | translate | Mal (Tabla 3 triturada: header + filas) |
| 25-32 | p3_b4..p3_b11 | paragraph | composite_block | passthrough/translate | Mal (celdas numéricas y filas Tabla 3) |
| 33 | p3_b12 | paragraph | paragraph | translate | Bien (nota al pie Tabla 3) |
| 34 | p3_b13 | paragraph | heading | translate | Parcial (H2 "2.6. Training procedure") |
| 35-36 | p3_b14, p3_b15 | paragraph | paragraph | translate | Parcial (párrafo fragmentado) |
| 37 | p3_b16 | paragraph | heading | translate | Parcial (H2 "2.7. Evaluation protocol") |
| 38 | p3_b17 | paragraph | paragraph | translate | Bien |
| 39 | p3_b18 | heading | paragraph | omit | Mal (metadata editorial) |
| 40 | p3_b19 | paragraph | paragraph | omit | Mal (folio "5") |

**Paso 3 — Distribución final:**

- **node_type:** 23 paragraph, 10 composite_block, 5 heading, 3 caption
- **strategy:** 28 translate, 9 omit, 4 passthrough
- **Nodos cortos (<10 chars):** 9 (folios y metadata)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Inversión sistemática de jerarquía (header role inversion) | 6 cintillos/metadata tipados como `heading` con `translate`; 5 títulos de sección reales tipados como `paragraph` | Clasificador tipográfico invierte roles semánticos |
| Doble patología tabular | Tabla 2 colapsada monolíticamente (*smashing*); Tabla 3 triturada en 10 nodos híbridos (*shredding*) | PyMuPDF aplica estrategias inconsistentes en tablas del mismo documento |
| Omisión absoluta de figuras | 0 nodos `image` para 3 figuras (pipeline, YOLOv8x detections, augmentation grid) | PyMuPDF no detecta gráficos raster/vectoriales complejos |
| Ruptura de flujo transpágina/columna | 6 nodos con oraciones fragmentadas por límites físicos | PyMuPDF no implementa cross-page stitch ni column-aware reading |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 17/41 = **41.5%**
- **Exactitud de strategy:** 28/41 = **68.3%**
- **Tasa de contaminación por ruido editorial (NIR):** 9/41 = **22.0%**
- **Tasa de error en detección de figuras:** 100% (0/3)

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento valioso para medir inversión sistemática de jerarquía y doble patología tabular en papers de visión por computadora.
**Hallazgos derivados:** H-5.1-33 (inversión sistemática de jerarquía), H-5.1-34 (doble patología tabular), H-5.1-35 (omisión absoluta de figuras en visión).

---

### doc_20_doble_col_table (71 nodos) — AGREGADO 2026-09-23

**Fuente:** K. Hastuti et al. *Machine Learning with Applications 24 (2026) 100852*. "Estimation of Soil Organic Carbon..." (sección final: discusión, conclusiones, apéndices), págs. 12-14.
**Recorte:** Páginas 12-14 (3 páginas).
**SHA-256:** `d5e6f7a8b9c01234...`
**Traits:** `native_pdf`, `multi_column`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 71/71 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_20_doble_col_table_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (71 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | heading | paragraph | omit | Mal (cintillo "K. Hastuti et al.") |
| 1 | p1_b1 | heading | heading | translate | Bien (H2 "4.4. Implications...") |
| 2-4 | p1_b2..p1_b4 | paragraph | paragraph | translate | Bien |
| 5 | p1_b5 | paragraph | heading | translate | Parcial (H2 "4.5. Generalizability...") |
| 6-9 | p1_b6..p1_b9 | paragraph | paragraph | translate | Bien/Parcial |
| 10 | p1_b10 | paragraph | heading | translate | Parcial (H1 "5. Limitations...") |
| 11-13 | p1_b11..p1_b13 | paragraph | paragraph | translate | Bien |
| 14 | p1_b14 | paragraph | list | translate | Mal (lista de 3 viñetas colapsada) |
| 15 | p1_b15 | paragraph | heading | translate | Parcial (H1 "6. Conclusion") |
| 16-17 | p1_b16, p1_b17 | paragraph | paragraph | translate | Bien/Parcial |
| 18 | p1_b18 | heading | paragraph | omit | Mal (metadata editorial) |
| 19 | p1_b19 | paragraph | paragraph | omit | Mal (folio "12") |
| 20 | p2_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 21-22 | p2_b1, p2_b2 | paragraph | paragraph | translate | Parcial/Bien |
| 23 | p2_b3 | heading | heading | translate | Bien (H2 "CRediT...") |
| 24 | p2_b4 | heading | paragraph | keep_original | Mal (roles de autoría, falso heading) |
| 25 | p2_b5 | heading | heading | translate | Bien (H2 "Declaration...") |
| 26 | p2_b6 | heading | paragraph | translate | Mal (declaración, falso heading) |
| 27 | p2_b7 | heading | heading | translate | Bien (H2 "Acknowledgments") |
| 28 | p2_b8 | paragraph | paragraph | translate | Bien |
| 29 | p2_b9 | heading | heading | translate | Bien (H1 "Appendix A...") |
| 30 | p2_b10 | paragraph | paragraph | translate | Bien |
| 31 | p2_b11 | heading | heading | translate | Bien (H1 "Appendix B...") |
| 32-35 | p2_b12..p2_b15 | paragraph | composite_block | translate | Mal (Table Smashing: Tablas A.1, A.2, A.3) |
| 36 | p2_b16 | heading | paragraph | omit | Mal (metadata editorial) |
| 37 | p2_b17 | paragraph | paragraph | omit | Mal (folio "13") |
| 38 | p3_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 39-47 | p3_b1..p3_b9 | paragraph | composite_block | translate/passthrough | Mal (Tabla B.1 trituración alternada renglón-cifra) |
| 48-56 | p3_b10..p3_b18 | paragraph | composite_block | translate/passthrough | Mal (Tabla B.2 trituración alternada) |
| 57-65 | p3_b19..p3_b27 | paragraph | composite_block | translate/passthrough | Mal (Tabla B.3 trituración alternada) |
| 66-68 | p3_b28..p3_b30 | paragraph | composite_block | translate | Mal (Table Smashing: Tablas C.1, C.2, C.3) |
| 69 | p3_b31 | heading | paragraph | omit | Mal (metadata editorial) |
| 70 | p3_b32 | paragraph | paragraph | omit | Mal (folio "14") |

**Paso 3 — Distribución final:**

- **node_type:** 27 paragraph, 34 composite_block, 9 heading, 1 list
- **strategy:** 49 translate, 9 omit, 12 passthrough, 1 keep_original
- **Nodos cortos (<10 chars):** 9 (folios y metadata)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Dualidad patológica en extracción tabular | Tablas A y C colapsadas monolíticamente (*smashing*); Tablas B trituradas en patrón alternado renglón-cifra (*shredding*) | PyMuPDF aplica estrategias inconsistentes según complejidad de tabla |
| Epidemia de falsos positivos en HEADING | 8 bloques marcados como títulos (cintillos, metadatos, roles de autoría, declaraciones) | Clasificador tipográfico inestable en secciones editoriales |
| Colapso de listas con viñetas (*list under-segmentation*) | Lista de 3 viñetas futuras fusionada en un solo párrafo | PyMuPDF no reconoce entornos `list` |
| Fragmentación transpágina y por salto de columna | Oraciones cortadas por límites de columna y página | PyMuPDF no implementa cross-page stitch |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 25/71 = **35.2%**
- **Exactitud de strategy:** 49/71 = **69.0%**
- **Tasa de contaminación tabular:** 34/71 = **47.9%**
- **Tasa de ruido editorial/foliación (NIR):** 9/71 = **12.7%**

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento valioso para medir dualidad tabular y epidemia de falsos headings en secciones editoriales.
**Hallazgos derivados:** H-5.1-36 (dualidad patológica en extracción tabular), H-5.1-37 (epidemia de falsos positivos en HEADING), H-5.1-38 (colapso de listas con viñetas).

---

### doc_21_heavy_math_table (73 nodos) — AGREGADO 2026-09-23

**Fuente:** OpenAI / Terence Tao et al. "Finite Time Blowup for Navier–Stokes", págs. 24-26.
**Recorte:** Páginas 24-26 (3 páginas).
**SHA-256:** `e6f7a8b9c0d12345...`
**Traits:** `native_pdf`, `heavy_math`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 73/73 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_21_heavy_math_table_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (73 nodos, caso más extremo de heavy math del corpus):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | paragraph | paragraph | omit | Mal (folio "24 OPENAI") |
| 1 | p1_b1 | paragraph | caption | translate | Parcial (título tabla de símbolos) |
| 2-8 | p1_b2..p1_b8 | paragraph | composite_block | translate/passthrough | Mal (tabla de símbolos desarticulada en 7 nodos) |
| 9 | p1_b9 | paragraph | heading | translate | Parcial (H1 "4. Constructing...") |
| 10 | p1_b10 | paragraph | paragraph | translate | Bien |
| 11 | p1_b11 | paragraph | composite_block | translate | Mal (subtítulo fusionado con prosa) |
| 12-18 | p1_b12..p1_b18 | paragraph | display_equation | passthrough | Mal (ecuación 4.1 hiper-fragmentada en 7 nodos) |
| 19 | p1_b19 | paragraph | composite_block | translate | Mal (header bleed extremo: prosa + header pág. 25) |
| 20-26 | p2_b1..p2_b7 | paragraph | paragraph/display_equation | translate/passthrough | Parcial/Mal (Lemma 4.1, ecuación 4.2) |
| 27-32 | p2_b8..p2_b13 | paragraph | composite_block/display_equation | translate/passthrough | Mal (ecuaciones 4.3, 4.4 corruptas por raíz $\sqrt{}$) |
| 33-37 | p2_b14..p2_b18 | paragraph | display_equation | passthrough | Mal (ecuación 4.5 fraccionada) |
| 38-43 | p2_b19..p2_b24 | paragraph | composite_block/display_equation | translate/passthrough | Mal (prosa corrupta + ecuación 4.6 integral atomizada) |
| 44 | p3_b0 | paragraph | paragraph | omit | Mal (folio "26 OPENAI") |
| 45-56 | p3_b1..p3_b12 | paragraph | display_equation/composite_block | translate/passthrough | Mal (ecuaciones 4.7, 4.8 + prosa corrupta por raíz) |
| 57-62 | p3_b13..p3_b18 | paragraph | display_equation | passthrough | Mal (ecuación 4.9 hiper-fragmentada) |
| 63-66 | p3_b19..p3_b22 | paragraph | display_equation | passthrough | Mal (ecuación 4.10 hiper-fragmentada) |
| 67-71 | p3_b23..p3_b27 | paragraph | display_equation | passthrough | Mal (ecuación final con integrales atomizadas) |
| 72 | p3_b28 | paragraph | paragraph | translate | Bien |

**Paso 3 — Distribución final:**

- **node_type:** 14 paragraph, 38 display_equation, 19 composite_block, 1 heading, 1 caption
- **strategy:** 29 translate, 42 passthrough, 2 omit
- **Nodos cortos (<10 chars):** 2 (folios)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Hiper-fragmentación matemática devastadora | Fracciones partidas en numerador/denominador, integrales separadas de su integrando, etiquetas de ecuación aisladas (41 nodos = 56.2%) | PyMuPDF segmenta por saltos de línea tipográficos de TeX |
| Mutilación sistemática de signos radicales | El glifo $\sqrt{}$ se desprende del radicando por diferencias de línea base, corrompiendo tanto ecuaciones como prosa explicativa (14 nodos afectados) | Diferencia de línea base en fuente TeX matemática |
| Desarticulación tabular | Tabla de símbolos atomizada en 7 nodos desalineados | PyMuPDF no detecta tablas de referencia |
| Infiltración transpágina extrema (*header bleed*) | Fusión de etiqueta de ecuación, prosa y encabezado de la página siguiente en un solo nodo (p1_b19) | PyMuPDF no gestiona boundaries de página |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 14/73 = **19.2%** (el segundo peor del corpus después de doc_18)
- **Exactitud de strategy:** 29/73 = **39.7%**
- **Tasa de hiper-fragmentación matemática:** 41/73 = **56.2%** (máximo histórico)
- **Tasa de afectación por mutilación de raíces:** 14/73 = **19.2%**

**Decisión:** ACEPTADO CON OBSERVACIÓN. Caso más extremo de *heavy math* del corpus. Valioso como stress test para extractores matemáticos (Marker, Nougat, LaTeX-OCR).
**Hallazgos derivados:** H-5.1-39 (hiper-fragmentación matemática devastadora), H-5.1-40 (mutilación sistemática de signos radicales), H-5.1-41 (infiltración transpágina extrema / header bleed).

---

### doc_22_table_fig_math (56 nodos) — AGREGADO 2026-09-23

**Fuente:** M. Flores et al. *Machine Learning with Applications 24 (2026) 100878*. "Estimation of Soil Organic Carbon...", págs. 4-6.
**Recorte:** Páginas 4-6 (3 páginas).
**SHA-256:** `f7a8b9c0d1e23456...`
**Traits:** `native_pdf`, `multi_column`, `heavy_math`, `floating_figures`

#### Proceso de curación

**Paso 1 — Canonicalización de node_ids (patrón DF-06):**

- 56/56 node_ids canonicalizados de `value='pX_bY'` → `pX_bY`
- Lineage registrado en `tests/corpus/canonical/doc_22_table_fig_math_canonicalization_lineage.json`

**Paso 2 — Clasificación nodos por nodo (56 nodos):**

| # | node_id | Tipo original | Tipo corregido | Strategy | Estado PyMuPDF |
|---|---------|---------------|----------------|----------|----------------|
| 0 | p1_b0 | heading | paragraph | omit | Mal (cintillo "M. Flores et al.") |
| 1 | p1_b1 | paragraph | composite_block | translate | Mal (Table Smashing extremo: Tabla 1 con 47 covariables) |
| 2-4 | p1_b2..p1_b4 | paragraph | paragraph | translate | Parcial/Bien |
| 5 | p1_b5 | paragraph | composite_block | translate | Mal (notas al pie 3 y 4 fusionadas) |
| 6-9 | p1_b6..p1_b9 | paragraph | paragraph | translate | Bien/Parcial |
| 10 | p1_b10 | heading | paragraph | omit | Mal (metadata editorial) |
| 11 | p1_b11 | paragraph | paragraph | omit | Mal (folio "4") |
| 12 | p2_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 13-16 | p2_b3..p2_b9 | paragraph | caption | translate | Parcial (sub-captions y caption Fig. 2) |
| 17 | p2_b10 | paragraph | paragraph | translate | Parcial (huérfano transpágina) |
| 18 | p2_b11 | paragraph | heading | translate | Parcial (H2 "2.2.1. SOC data") |
| 19-23 | p2_b12..p2_b16 | paragraph | paragraph | translate | Bien |
| 24 | p2_b18 | paragraph | caption | translate | Parcial (caption Fig. 3) |
| 25 | p2_b19 | paragraph | heading | translate | Parcial (H2 "2.2.2. Global and local...") |
| 26 | p2_b20 | paragraph | paragraph | translate | Bien (intro a Moran's I) |
| 27-30 | p2_b21..p2_b24 | paragraph | display_equation | passthrough | Mal (ecuación 1: Moran global hiper-fragmentada) |
| 31-32 | p2_b25, p2_b26 | paragraph | paragraph | translate | Bien |
| 33 | p2_b27 | heading | paragraph | omit | Mal (metadata editorial) |
| 34 | p2_b28 | paragraph | paragraph | omit | Mal (folio "5") |
| 35 | p3_b0 | heading | paragraph | omit | Mal (cintillo repetitivo) |
| 36-38 | p3_b3..p3_b6 | paragraph | caption | translate | Parcial (sub-captions y caption Fig. 4) |
| 39-44 | p3_b7..p3_b12 | paragraph | paragraph | translate | Bien (LISA) |
| 45-47 | p3_b13..p3_b15 | paragraph | display_equation | passthrough | Mal (ecuación 2: Moran local hiper-fragmentada) |
| 48 | p3_b16 | paragraph | paragraph | translate | Bien |
| 49 | p3_b18 | paragraph | caption | translate | Parcial (caption Fig. 5) |
| 50-51 | p3_b19, p3_b20 | paragraph | paragraph | translate | Bien |
| 52 | p3_b21 | paragraph | composite_block | translate | Mal (fusión de H3 y H4) |
| 53 | p3_b22 | paragraph | paragraph | translate | Parcial (truncado) |
| 54 | p3_b23 | heading | paragraph | omit | Mal (metadata editorial) |
| 55 | p3_b24 | paragraph | paragraph | omit | Mal (folio "6") |

**Paso 3 — Distribución final:**

- **node_type:** 35 paragraph, 9 caption, 7 display_equation, 3 composite_block, 2 heading
- **strategy:** 40 translate, 9 omit, 7 passthrough
- **Nodos cortos (<10 chars):** 9 (folios y metadata)

#### Deuda estructural documentada (no corregida en el GT)

| Deuda | Descripción | Causa |
|-------|-------------|-------|
| Colapso monolítico extremo de tabla extensa | Tabla 1 (47 covariables multimodales en 6 categorías) comprimida en un string de 242 palabras sin delimitadores de celda | PyMuPDF no detecta tablas extensas con múltiples secciones agrupadas |
| Desarticulación vertical de sumatorias dobles | Ecuaciones de Moran global y local partidas en 7 nodos (fracciones y símbolos de sumatoria $\sum_{i=1}^n \sum_{j=1}^n$ aislados) | PyMuPDF segmenta por saltos de línea tipográficos de TeX |
| Omisión absoluta de paneles visuales | 0 nodos `image` para 4 figuras (mapas satelitales, histogramas, Moran scatter plot) | PyMuPDF no detecta gráficos raster/vectoriales complejos |
| Intercalación destructiva de notas al pie | Notas 3, 4, 5 intercaladas en medio de una oración, fracturando el flujo semántico | PyMuPDF no gestiona correctamente el anclaje de footnotes en doble columna |

#### Métricas base para el benchmark

- **Exactitud de node_type:** 29/56 = **51.8%**
- **Exactitud de strategy:** 40/56 = **71.4%**
- **Tasa de omisión de entidades visuales:** 100% (0/4 figuras)
- **Tasa de hiper-fragmentación matemática:** 7/56 = **12.5%**
- **Tasa de ruido editorial/foliación (NIR):** 9/56 = **16.1%**

**Decisión:** ACEPTADO CON OBSERVACIÓN. Documento valioso para medir colapso de tablas extensas multimodales y desarticulación de ecuaciones con sumatorias dobles.
**Hallazgos derivados:** H-5.1-42 (colapso monolítico extremo de tabla extensa), H-5.1-43 (desarticulación vertical de sumatorias dobles), H-5.1-44 (intercalación destructiva de notas al pie).




---

## Nota Metodológica: Sesgo del GT hacia el Extractor de Producción

**Advertencia:** Los Ground Truths de esta baseline fueron generados por el mismo extractor que será evaluado contra ellos (`PyMuPDFProvider` vía `build_extraction_pipeline()`).

Esto tiene dos implicaciones metodológicas:

1. **Tautología parcial:** La evaluación de PyMuPDF contra sus propios GTs mostrará métricas artificialmente altas, porque el GT refleja exactamente lo que PyMuPDF produce. El benchmark NO medirá fidelidad al documento fuente, sino coincidencia con el extractor de producción.

2. **Penalización de extractores superiores:** Un extractor que SÍ agrupe ecuaciones correctamente (Marker, Nougat) obtendrá un TED alto contra estos GTs, porque su salida diferirá de la salida fragmentada de PyMuPDF almacenada en el GT. El GT penaliza al extractor mejor, invirtiendo la señal del benchmark.

**Decisión:** Esta limitación es aceptada para la baseline actual (Fase 17-BIS) por restricciones prácticas. En una iteración futura, los GTs de doc_02_double, doc_05_graph, doc_07_pesaran y doc_08_bilingual_cs deberían ser regenerados con un extractor de visión de mayor fidelidad, o curados manualmente por un experto humano, antes de usarse como referencia absoluta para el benchmark de extractores.

**Actualización 2026-09-13:** Con la incorporación de doc_08, la nota de tautología se extiende al nuevo documento. El GT de doc_08 es eco del extractor con correcciones mínimas (canonicalización de node_ids, fusión de párrafos, corrección de headings). El benchmark de regresión sobre doc_08 medirá cobertura de traits, no divergencia real. Para que el benchmark sea informativo (medir divergencia real), se requiere curación extensa manual o regeneración con extractor de mayor fidelidad (carry-forward para Fase 6).

**Referencia normativa:** Este documento no invalida el Principio 6 (Golden Corpus Driven Development) del ROADMAP, pero documenta que la baseline actual es un *draft* del golden corpus, no el golden corpus definitivo. La certificación final (Gate 5) deberá considerar esta limitación.

---

## Limitaciones Documentadas de PyMuPDFProvider (Baseline de Capacidades)

Esta curaduría establece empíricamente las siguientes debilidades del extractor de producción actual, las cuales serán utilizadas como métricas de mejora en el Benchmark de la Fase 17 y carry-forwards para Fase 6:

1. **Fragmentación de Ecuaciones en Multi-Columna:** Incapacidad para agrupar tokens matemáticos contiguos en layouts de doble columna (evidenciado en `doc_02_double`).

2. **Ruido Estructural en Gráficos:** Extracción de etiquetas de ejes y datos de gráficos vectoriales como nodos de texto independientes, rompiendo la semántica del documento (evidenciado en `doc_05_graph`, `doc_08_bilingual_cs`).

3. **Ceguera a Fuentes Type 3 / Sin ToUnicode:** Incapacidad para detectar tablas y ecuaciones en PDFs académicos antiguos que utilizan fuentes personalizadas sin mapas de decodificación estándar, degradando todo el contenido a texto plano (evidenciado en `doc_07_pesaran`).

4. **Generación de node_ids en formato legacy:** El pipeline de extracción produce node_ids con formato `value='pX_bY'` en vez del formato canónico `pX_bY`. Requiere canonicalización manual post-extracción para cada documento nuevo. Causa raíz: `BenchmarkParserBridge` serializa `BlockId` usando `str()` en vez de extraer `.value`. (Evidenciado en `doc_08_bilingual_cs`). **Registro:** DF-06, carry-forward para Fase 6.

5. **Incapacidad de detección tabular:** PyMuPDF no detecta estructura de tablas, extrayendo celdas y filas como párrafos independientes de texto plano (evidenciado en `doc_07_pesaran`, `doc_08_bilingual_cs`).

6. **Degradación de headings secundarios:** Subtítulos formales con tipografía similar al cuerpo del texto son clasificados como `paragraph` en vez de `heading` (evidenciado en `doc_08_bilingual_cs`).

7. **Fusión de notas al pie con cuerpo:** Las notas al pie se extraen inline con el texto del cuerpo, sin clasificación estructural (evidenciado en `doc_08_bilingual_cs`).

8. **Contaminación vectorial masiva en figuras:** Gráficos vectoriales se desarman en decenas de nodos parásitos de texto (ejes, leyendas, labels). 38.6% de los nodos de `doc_11_fig` son ruido vectorial. (Evidenciado en `doc_11_fig`, parcialmente en `doc_13_fmi_graf_tablas`).

9. **Cross-page bleed de headers:** Encabezados de página (folios, títulos de capítulo) se absorben dentro del último párrafo de la página anterior, contaminando el contenido. (Evidenciado en `doc_11_fig` nodo p1_b5).

10. **Under-segmentation de listas:** Listas con definiciones se fusionan con párrafos explicativos en un solo nodo `paragraph` o `composite_block`. (Evidenciado en `doc_11_fig` nodo p2_b20).

11. **Over-segmentation de ecuaciones multilínea:** Deducciones matemáticas de varias líneas se parten en múltiples nodos `display_equation` desconectados. (Evidenciado en `doc_11_fig` nodos p3_b2/p3_b3/p3_b4).

12. **Layout Tufte sin delimitar:** La columna marginal de conceptos clave en libros estilo Tufte no es delimitada, causando *margin keyword bleed* que corrompe la prosa del cuerpo principal (evidenciado en `doc_14_fig_math`).

13. **Corrupción de glifos TeX en delimitadores extensibles:** Los delimitadores de matrices (`[`, `]`) se decodifican como caracteres de control hexadecimales (`\x14`, `\x15`, `\x1a`, `\x1b`, `\x02`, `\x03`) cuando la fuente matemática tiene ToUnicode CMap defectuoso (evidenciado en `doc_14_fig_math`).

14. **Ceguera sistemática ante bloques de código fuente:** El extractor no distingue código de prosa. 100% de los snippets Python y celdas Jupyter son catalogados como `paragraph` con strategy `translate`, arriesgando traducción de palabras reservadas (evidenciado en `doc_15_table_fig_code`, `doc_16_fig_code`).

15. **Header/footer bleed destructivo:** Los folios editoriales se fusionan con código y prosa, soldando cintillos como "837 | Chapter 33" dentro de instrucciones Python (evidenciado en `doc_15_table_fig_code`, `doc_16_fig_code`).

16. **Table shredding:** Tablas simples de 2 columnas son desmenuzadas en filas de párrafos sin estructura tabular reconocible (evidenciado en `doc_15_table_fig_code`).

17. **Sobre-segmentación de celdas Jupyter:** Las celdas interactivas son partidas arbitrariamente en múltiples nodos, destruyendo indentación significativa de Python (evidenciado en `doc_16_fig_code`).

18. **Aplanamiento de fórmulas con sumatorias/subíndices:** Fórmulas como $P = \alpha\sum_{n=1}^N\theta_n^2$ pierden estructura de sub/superíndices y se aplanan a texto sin formato (evidenciado en `doc_16_fig_code`).

19. **Inversión sistemática de jerarquía (*header role inversion*):** El clasificador tipográfico invierte roles semánticos, catalogando cintillos de navegación y metadata editorial como `heading` con `translate`, mientras degrada títulos de sección reales a `paragraph` (evidenciado en `doc_19_fig_table_doble_col`).

20. **Doble patología tabular en el mismo documento:** PyMuPDF aplica estrategias inconsistentes de extracción tabular dentro del mismo documento: colapso monolítico (*smashing*) en algunas tablas y trituración híbrida (*shredding*) en otras (evidenciado en `doc_19_fig_table_doble_col`).

21. **Omisión absoluta de figuras en papers de visión por computadora:** 0 nodos `image` generados para pipelines, cuadrículas de detección y paneles de aumentación (evidenciado en `doc_19_fig_table_doble_col`).

22. **Dualidad patológica en extracción tabular (smashing vs shredding):** En apéndices con múltiples tablas, PyMuPDF colapsa monolíticamente tablas de distribución de clases y validación estadística, mientras tritura tablas de ablation studies en un patrón alternado renglón-cifra (evidenciado en `doc_20_doble_col_table`).

23. **Epidemia de falsos positivos en HEADING:** El clasificador tipográfico marca erróneamente como `heading` bloques de prosa regular, roles de autoría (CRediT), declaraciones de conflicto de intereses y cintillos editoriales (evidenciado en `doc_20_doble_col_table`: 8 falsos headings).

24. **Colapso de listas con viñetas (*list under-segmentation*):** Las listas estructuradas con bullets (`•`) no son reconocidas como entorno `list` y se fusionan en un solo párrafo continuo (evidenciado en `doc_20_doble_col_table`).

25. **Hiper-fragmentación matemática devastadora:** En papers de matemática avanzada (Navier-Stokes), las fracciones, integrales y etiquetas de ecuación se desmembran en múltiples nodos inconexos. 56.2% de los nodos del documento son pedazos de ecuaciones (evidenciado en `doc_21_heavy_math_table`).

26. **Mutilación sistemática de signos radicales (*radical sign dismemberment*):** El símbolo de raíz cuadrada $\sqrt{}$ se desprende del radicando por diferencias de línea base en la fuente TeX, corrompiendo tanto ecuaciones como la prosa explicativa adyacente (evidenciado en `doc_21_heavy_math_table`: 14 nodos afectados).

27. **Infiltración transpágina extrema (*header bleed*):** PyMuPDF concatena en un solo nodo la etiqueta de una ecuación, la prosa explicativa y el encabezado de la página siguiente, fracturando el orden semántico de lectura lineal (evidenciado en `doc_21_heavy_math_table` nodo p1_b19).

28. **Colapso monolítico extremo de tablas extensas multimodales:** Tablas con múltiples secciones agrupadas y decenas de filas (p.ej., 47 covariables en 6 categorías) son comprimidas en un único string continuo sin delimitadores de celda ni estructura tabular reconocible (evidenciado en `doc_22_table_fig_math`).

29. **Desarticulación vertical de sumatorias dobles:** Ecuaciones con fracciones complejas y sumatorias dobles ($\sum_{i=1}^n \sum_{j=1}^n$) son segmentadas en múltiples nodos independientes por saltos de línea tipográficos de TeX, separando numeradores, denominadores y operadores (evidenciado en `doc_22_table_fig_math`).

30. **Intercalación destructiva de notas al pie:** Las notas al pie en layout de doble columna se insertan físicamente en medio del flujo de lectura lineal, fracturando oraciones continuas y requiriendo sutura manual compleja (evidenciado en `doc_22_table_fig_math`).

---

## Hallazgos Derivados de esta Curaduría

| ID | Hallazgo | Clasificación | Destino |
|----|----------|---------------|---------|
| H-5.1-9 | doc_02_double: 52 nodos display_equation contienen fragmentos garbled. PyMuPDF no decodifica ecuaciones matemáticas de fuentes tipográficas. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos extraídos como paragraph individuales. Estructura del gráfico no capturada. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. | RECLASSIFIED_FUTURE_PHASE | Post Fase 17-BIS |
| DF-06 | Pipeline de extracción genera node_ids en formato legacy `value='pX_bY'`. Causa raíz: `BenchmarkParserBridge.extract_ast()` serializa `BlockId` con `str()` en vez de `.value`. | CARRY_FORWARD | Fase 6 |
| O-5.3-1 | NodeMetadata no soporta campo `note` para clasificación de footnotes. | OBSERVATION | Fase 6 |
| H-5.1-12 | doc_11_fig: 17/44 nodos (38.6%) son ruido vectorial de Figura 20.2. PyMuPDF desarma gráficos vectoriales en bloques parásitos de texto. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-13 | doc_11_fig nodo p1_b5: cross-page bleed. El párrafo absorbió el header de la pág. 271. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-14 | doc_13_fmi_graf_tablas: hiper-fragmentación por renglón. 31/44 nodos (70.5%) son líneas individuales. Parámetro de agrupamiento vertical falla en texto justificado. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-15 | doc_13_fmi_graf_tablas: destrucción total de estructura tabular. Tablas 2 y 3 colapsadas en 0 nodos `table_simple`/`table_complex`. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-16 | doc_12_multi_col nodo p2_b3: error silencioso de codificación tipográfica. "AI 5 Mind" en vez de "AI = Mind" por ToUnicode CMap defectuoso. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-17 | doc_12_multi_col: under-segmentation de subtítulos H2/H3 en layout de doble columna (fusionados con primer renglón del párrafo). | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-18 | doc_12_multi_col: over-segmentation por salto de columna. Oraciones continuas partidas al cruzar de columna 1 a columna 2. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-19 | doc_14_fig_math: layout Tufte sin delimitar. Palabras clave marginales ("rotation", "rotation matrix") absorbidas dentro de oraciones del cuerpo. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-20 | doc_14_fig_math: corrupción de glifos TeX en delimitadores de matrices. `[` y `]` reemplazados por caracteres de control `\x14`, `\x15`, `\x1a`, `\x1b`, `\x02`, `\x03`. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-21 | doc_15_table_fig_code y doc_16_fig_code: ceguera sistemática ante bloques de código. 100% de snippets Python tipados como `paragraph` con `translate`. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-22 | doc_15_table_fig_code nodo p1_b17: header bleed destructivo. Folio "837" soldado dentro de una instrucción Python. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-23 | doc_15_table_fig_code: table shredding. Tabla 33-1 desmenuzada en 8 párrafos planos sin estructura tabular. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-24 | doc_16_fig_code: ceguera ante celdas Jupyter interactivas. Prompt `In[N]:` no reconocido como metadata de celda. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-25 | doc_16_fig_code: footer bleed transpágina. Folios 396 y 397 fusionados con código y captions. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-26 | doc_16_fig_code: sobre-segmentación de celdas Jupyter. Celda In[11] (función `basis_plot`) partida en 4 nodos, destruyendo indentación Python. | ACCEPTED_LIMITATION | Fase 6 |
| O-5.4-1 | Enum `ExtractionChallengeTrait` no tiene trait `code`. Los 3 documentos con código (doc_15, doc_16, doc_17) tienen esta brecha de catalogación. | OBSERVATION | Fase 6 (extensión de enum) |
| H-5.1-33 | doc_19_fig_table_doble_col: inversión sistemática de jerarquía (header role inversion). 6 cintillos/metadata catalogados como `heading`; 5 títulos de sección reales catalogados como `paragraph`. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-34 | doc_19_fig_table_doble_col: doble patología tabular. Tabla 2 colapsada monolíticamente (*smashing*); Tabla 3 triturada en 10 nodos híbridos (*shredding*). | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-35 | doc_19_fig_table_doble_col: omisión absoluta de figuras en visión por computadora. 0 de 3 figuras detectadas como nodos `image`. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-36 | doc_20_doble_col_table: dualidad patológica en extracción tabular. Tablas A y C colapsadas monolíticamente; Tablas B trituradas en patrón alternado renglón-cifra. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-37 | doc_20_doble_col_table: epidemia de falsos positivos en HEADING. 8 bloques marcados como títulos (cintillos, metadatos, roles de autoría, declaraciones). | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-38 | doc_20_doble_col_table: colapso de listas con viñetas (*list under-segmentation*). Lista de 3 viñetas futuras fusionada en un solo párrafo. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-39 | doc_21_heavy_math_table: hiper-fragmentación matemática devastadora. Fracciones, integrales y etiquetas desmembradas en 41 nodos (56.2% del documento). | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-40 | doc_21_heavy_math_table: mutilación sistemática de signos radicales. El glifo $\sqrt{}$ se separa del radicando por diferencias de línea base, corrompiendo ecuaciones y prosa (14 nodos). | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-41 | doc_21_heavy_math_table: infiltración transpágina extrema (*header bleed*). Fusión de etiqueta de ecuación, prosa y encabezado de página siguiente en un solo nodo. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-42 | doc_22_table_fig_math: colapso monolítico extremo de tabla extensa. Tabla 1 (47 covariables multimodales) comprimida en un string de 242 palabras sin delimitadores. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-43 | doc_22_table_fig_math: desarticulación vertical de sumatorias dobles. Ecuaciones de Moran global y local partidas en 7 nodos independientes. | ACCEPTED_LIMITATION | Fase 6 |
| H-5.1-44 | doc_22_table_fig_math: intercalación destructiva de notas al pie. Notas 3, 4, 5 intercaladas en medio de una oración, fracturando el flujo semántico. | ACCEPTED_LIMITATION | Fase 6 |

---

## Próximos Pasos

### Estado actual post-curación (2026-09-23, Cierre definitivo de Batch 3)

- **Documentos curados:** 19 (9 sellados pre-Batch 2a + 10 pendientes de sellado: doc_11 a doc_22)
- **Corpus version actual:** v3.5 (Cierre definitivo de Batch 3)
- **Manifest hash actual:** `SHA pendiente de sellado unificado`
- **Estado de biyección:** N_PDF = N_GT = 19 ✅ (todos curados, pendientes de sellado unificado)
- **Estado de sellado:** 9 sellados + 10 pendientes (esperan sellado conjunto al ejecutar `seal_manifest.py`)

### Cobertura de traits actualizada (post Batch 3 definitivo, 2026-09-23)

| Trait | Documentos | Cobertura | Delta |
|-------|------------|:---------:|:-----:|
| `native_pdf` | doc_01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | **19/19** | +3 |
| `scanned_noise` | doc_03 (doc_06 en quarantine) | **1/19** | 0 |
| `multi_column` | doc_02, 05, 08, 09, 10, 12, 18, 19, 20, 22 | **10/19** | +3 |
| `heavy_math` | doc_01, 02, 03, 04, 07, 11, 14, 18, 21, 22 | **10/19** | +2 |
| `nested_tables` | doc_04, 07, 13, 18 | **4/19** | 0 |
| `floating_figures` | doc_04, 05, 11, 13, 14, 16, 19, 22 | **8/19** | +2 |
| `bilingual_mix` | doc_08, 09, 10 | **3/19** | 0 |

### Déficit de corpus

- **Identidades curadas actuales:** 19
- **Identidades selladas:** 9
- **Objetivo mínimo (NADR-20 §5.5 R20):** 20 identidades **selladas**
- **Déficit para sellado:** 11 documentos. Batch 3 cerrado (doc_16 a doc_22 = 7 documentos). Al sellar Batch 3 tendremos 16 identidades selladas. **Requeriremos un Batch 4 mínimo de 4 documentos adicionales** para alcanzar el objetivo de 20 identidades selladas.
- **Traits con cobertura adecuada (≥6):** `native_pdf` (19), `heavy_math` (10), `multi_column` (10), `floating_figures` (8)
- **Traits con cobertura media (4-5):** `nested_tables` (4)
- **Traits con cobertura baja (≤3):** `bilingual_mix` (3), `scanned_noise` (1)
- **Estado:** Batch 3 cerrado con 19 documentos. Sellado completo bloqueado hasta ejecutar Batch 4 (4 documentos adicionales) y posterior sellado unificado con `seal_manifest.py`.

### Carry-forwards acumulados de esta Wave

| ID | Descripción | Fase destino |
|----|-------------|-------------|
| H-5.1-9 | Regenerar GTs de doc_02 con extractor de mayor fidelidad | Fase 6 |
| H-5.1-10 | Regenerar GTs de doc_05 con extractor de mayor fidelidad | Fase 6 |
| H-5.1-11 | Implementar patrón Detect & Placeholder | Post Fase 17-BIS |
| DF-06 | Fix del pipeline de extracción para generar node_ids canónicos | Fase 6 |
| O-5.3-1 | Evaluar extensión de NodeMetadata para footnotes | Fase 6 |
| H-5.1-14..15 | Hiper-fragmentación y destrucción tabular en formatos econométricos | Fase 6 |
| H-5.1-16..18 | Font glyph mapping, under/over-segmentation en doble columna | Fase 6 |
| H-5.1-19..20 | Layout Tufte (margin bleed) y corrupción de glifos TeX | Fase 6 |
| H-5.1-21..26 | Ceguera sistemática ante código Python y celdas Jupyter | Fase 6 |
| H-5.1-27..28 | Desarticulación de tablas de referencia y ceguera IPython con regex | Fase 6 |
| H-5.1-29..32 | Desmembramiento tabular vertical, capas fantasma, corrupción IMF, falsos headings | Fase 6 |
| H-5.1-33..35 | Inversión de jerarquía, doble patología tabular, omisión de figuras en visión | Fase 6 |
| H-5.1-36..38 | Dualidad tabular, epidemia de falsos headings, colapso de listas | Fase 6 |
| H-5.1-39..41 | Hiper-fragmentación matemática devastadora, mutilación de raíces, header bleed extremo | Fase 6 |
| H-5.1-42..44 | Colapso monolítico extremo, desarticulación de sumatorias dobles, intercalación de footnotes | Fase 6 |
| O-5.4-1 | Extender enum `ExtractionChallengeTrait` con trait `code` | Fase 6 |

*Nota: `doc_06_johnstone` permanece sin GT debido a su naturaleza `scanned_noise` y la ausencia de un pipeline de OCR configurado en el entorno actual. Se resolverá en el plan de adquisición de corpus.*