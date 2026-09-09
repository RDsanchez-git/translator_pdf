# FASE 5 — Wave 1.3 Curation Report

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_3_CURATION_REPORT.md`
**Fecha:** 2026-09-09
**Task:** 1.3.9 — Curaduría manual de Ground Truths
**Reglas:** NADR-21 §5.1 R5 (La curaduría ocurre ANTES del sealing, nunca después)

## Resumen Ejecutivo

- **Total de documentos curados:** 6
- **Documentos rechazados:** 0
- **Documentos aceptados:** 6 (3 sin observaciones, 3 con observaciones)
- **Extractor de producción evaluado:** `PyMuPDFProvider` (vía `build_extraction_pipeline()`)

**Veredicto General:** Todos los Ground Truths (GTs) han sido aceptados. Los ASTs representan fielmente la estructura y el contenido que el extractor de producción actual (`PyMuPDFProvider`) es capaz de producir. Las limitaciones observadas en la extracción de ecuaciones, tablas y gráficos se documentan formalmente como la "Baseline de Capacidades" contra la cual se medirán los futuros adaptadores (Marker, Docling, Nougat) en la Fase 17.

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

## Nota Metodológica: Sesgo del GT hacia el Extractor de Producción

**Advertencia:** Los Ground Truths de esta baseline fueron generados por el mismo extractor que será evaluado contra ellos (`PyMuPDFProvider` vía `build_extraction_pipeline()`).

Esto tiene dos implicaciones metodológicas:

1. **Tautología parcial:** La evaluación de PyMuPDF contra sus propios GTs mostrará métricas artificialmente altas, porque el GT refleja exactamente lo que PyMuPDF produce. El benchmark NO medirá fidelidad al documento fuente, sino coincidencia con el extractor de producción.

2. **Penalización de extractores superiores:** Un extractor que SÍ agrupe ecuaciones correctamente (Marker, Nougat) obtendrá un TED alto contra estos GTs, porque su salida diferirá de la salida fragmentada de PyMuPDF almacenada en el GT. El GT penaliza al extractor mejor, invirtiendo la señal del benchmark.

**Decisión:** Esta limitación es aceptada para la baseline actual (Fase 17-BIS) por restricciones prácticas. En una iteración futura, los GTs de doc_02_double, doc_05_graph y doc_07_pesaran deberían ser regenerados con un extractor de visión de mayor fidelidad, o curados manualmente por un experto humano, antes de usarse como referencia absoluta para el benchmark de extractores.

**Referencia normativa:** Este documento no invalida el Principio 6 (Golden Corpus Driven Development) del ROADMAP, pero documenta que la baseline actual es un *draft* del golden corpus, no el golden corpus definitivo. La certificación final (Gate 5) deberá considerar esta limitación.

## Limitaciones Documentadas de PyMuPDFProvider (Baseline de Capacidades)

Esta curaduría establece empíricamente las siguientes debilidades del extractor de producción actual, las cuales serán utilizadas como métricas de mejora en el Benchmark de la Fase 17:

1. **Fragmentación de Ecuaciones en Multi-Columna:** Incapacidad para agrupar tokens matemáticos contiguos en layouts de doble columna (evidenciado en `doc_02_double`).

2. **Ruido Estructural en Gráficos:** Extracción de etiquetas de ejes y datos de gráficos vectoriales como nodos de texto independientes, rompiendo la semántica del documento (evidenciado en `doc_05_graph`).

3. **Ceguera a Fuentes Type 3 / Sin ToUnicode:** Incapacidad para detectar tablas y ecuaciones en PDFs académicos antiguos que utilizan fuentes personalizadas sin mapas de decodificación estándar, degradando todo el contenido a texto plano (evidenciado en `doc_07_pesaran`).

## Hallazgos Derivados de esta Curaduría

| ID | Hallazgo | Clasificación | Destino |
|----|----------|---------------|---------|
| H-5.1-9 | doc_02_double: 52 nodos display_equation contienen fragmentos garbled (operadores/variables aislados). PyMuPDF no decodifica ecuaciones matemáticas de fuentes tipográficas. El GT NO es fiel al contenido matemático real. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos extraídos como paragraph individuales. Estructura del gráfico no capturada. | ACCEPTED_LIMITATION | Fase 6 / mejora de GT |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar la presencia y dejar placeholder para pegado manual. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4). | RECLASSIFIED_FUTURE_PHASE | Post Fase 17-BIS (ADR dedicado) |

## Próximos Pasos (Gate 2)

Con la curaduría completada y las limitaciones documentadas, los 6 Ground Truths están listos para avanzar en su ciclo de vida (`Draft` -> `Audited` -> `Validated`) y eventualmente alcanzar el estado `SEALED` en Gate 2, cumpliendo con la invariante de **Zero Partial Sealing** (NADR-21 §5.5) para los documentos que poseen GT.

*Nota: `doc_06_johnstone` permanece sin GT debido a su naturaleza `scanned_noise` y la ausencia de un pipeline de OCR configurado en el entorno actual. Se resolverá en el plan de adquisición de corpus.*
