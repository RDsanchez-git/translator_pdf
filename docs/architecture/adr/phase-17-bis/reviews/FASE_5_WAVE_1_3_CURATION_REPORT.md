# FASE 5 — Wave 1.3 Curation Report

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_3_CURATION_REPORT.md`
**Fecha original:** 2026-09-09
**Última actualización:** 2026-09-13 (adición de doc_08_bilingual_cs)
**Task:** 1.3.9 — Curaduría manual de Ground Truths
**Reglas:** NADR-21 §5.1 R5 (La curaduría ocurre ANTES del sealing, nunca después)

---

## Resumen Ejecutivo

- **Total de documentos curados:** 7
- **Documentos rechazados:** 0
- **Documentos aceptados:** 7 (3 sin observaciones, 4 con observaciones)
- **Extractor de producción evaluado:** `PyMuPDFProvider` (vía `build_extraction_pipeline()`)

**Veredicto General:** Todos los Ground Truths (GTs) han sido aceptados. Los ASTs representan fielmente la estructura y el contenido que el extractor de producción actual (`PyMuPDFProvider`) es capaz de producir. Las limitaciones observadas en la extracción de ecuaciones, tablas, gráficos, code-switching y node_ids se documentan formalmente como la "Baseline de Capacidades" contra la cual se medirán los futuros adaptadores (Marker, Docling, Nougat) en la Fase 17 y fases futuras.

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

---

## Hallazgos Derivados de esta Curaduría

| ID | Hallazgo | Clasificación | Destino |
|----|----------|---------------|---------|
| H-5.1-9 | doc_02_double: 52 nodos display_equation contienen fragmentos garbled (operadores/variables aislados). PyMuPDF no decodifica ecuaciones matemáticas de fuentes tipográficas. El GT NO es fiel al contenido matemático real. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos extraídos como paragraph individuales. Estructura del gráfico no capturada. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar la presencia y dejar placeholder para pegado manual. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4). | RECLASSIFIED_FUTURE_PHASE | Post Fase 17-BIS (ADR dedicado) |
| DF-06 | Pipeline de extracción genera node_ids en formato legacy `value='pX_bY'` para todos los documentos. Requiere canonicalización manual post-extracción. Causa raíz: `BenchmarkParserBridge.extract_ast()` serializa `BlockId` con `str()` en vez de `.value`. | CARRY_FORWARD | Fase 6 (fix del pipeline de extracción) |
| O-5.3-1 | NodeMetadata no soporta campo `note` para clasificación de footnotes. Footnotes presentes en contenido pero sin metadata estructural. | OBSERVATION | Fase 6 (extensión de schema si se requiere) |

---

## Próximos Pasos

### Estado actual post-curación (2026-09-13)

Los 7 Ground Truths están curados y listos. El corpus v2.0 fue sellado exitosamente:

- **Corpus version:** v2.0
- **Manifest hash:** `5d2f47cb8d98b892...`
- **Biyección:** N_PDF = N_GT = 7 ✅
- **Estado:** 7/7 sellados

### Cobertura de traits actualizada

| Trait | Documentos | Cobertura |
|-------|------------|:---------:|
| `native_pdf` | doc_01, doc_02, doc_04, doc_05, doc_07, doc_08 | 6/7 |
| `scanned_noise` | doc_03 | 1/7 |
| `multi_column` | doc_02, doc_05, doc_08 | 3/7 |
| `heavy_math` | doc_01, doc_02, doc_03, doc_04, doc_07 | 5/7 |
| `nested_tables` | doc_04, doc_07 | 2/7 |
| `floating_figures` | doc_04, doc_05 | 2/7 |
| `bilingual_mix` | doc_08 | **1/7** ✅ |

### Déficit de corpus

- **Identidades selladas:** 7
- **Objetivo mínimo (NADR-20 §5.5 R20):** 20
- **Déficit:** 13 documentos
- **Estado:** Certificación final (Gate 5) bloqueada hasta alcanzar ≥20 identidades

### Carry-forwards acumulados de esta Wave

| ID | Descripción | Fase destino |
|----|-------------|-------------|
| H-5.1-9 | Regenerar GTs de doc_02 con extractor de mayor fidelidad | Fase 6 |
| H-5.1-10 | Regenerar GTs de doc_05 con extractor de mayor fidelidad | Fase 6 |
| H-5.1-11 | Implementar patrón Detect & Placeholder | Post Fase 17-BIS |
| DF-06 | Fix del pipeline de extracción para generar node_ids canónicos | Fase 6 |
| O-5.3-1 | Evaluar extensión de NodeMetadata para footnotes | Fase 6 |

*Nota: `doc_06_johnstone` permanece sin GT debido a su naturaleza `scanned_noise` y la ausencia de un pipeline de OCR configurado en el entorno actual. Se resolverá en el plan de adquisición de corpus.*