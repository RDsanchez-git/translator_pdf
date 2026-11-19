# HITO_PPPR.0.2_INGESTA_Y_EXTRACCION_PDF.md

**Estado:** IN_PROGRESS v1.0.1  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** N/A  
**Iniciativa:** PPPR — Fase 0, iniciativa transversal `pdf-pdf-product-readiness`  
**Tipo de artefacto:** Forensic Flow Audit  
**Naturaleza:** Auditoría read-only del producto; este documento no prescribe implementación, ADR ni NADR.  
**Baseline de código inspeccionado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`; referencia de gobernanza `pdf-pdf-product-readiness@0c8d1f569394e111fa727a5b375c49d4b4576f81`.  
**Fuentes vinculantes:** Metodologías general v1.3.0 y forense v1.2.0 FROZEN; PPPR.0.1 FROZEN v1.0.9; D-1/D-2 y Atlas de convergencia (corte histórico); `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, NADR-F17BIS-02; HITO 0.4.5-P2 F17-BIS como antecedente, no como evidencia del HEAD.  
**Mandato:** Determinar qué contenido del PDF físico representa, transforma o rechaza la ruta PyMuPDF conectada antes de G3, y qué evidencia falta para atribuirle fidelidad STEM.  
**Síntesis provisional:** La ruta productiva materializa texto y ciertos PNG/matemática visual, aplica rechazos fail-closed a glifos señalados, matemáticas mixtas y vectores, y no ofrece clasificación nativa de tablas ni orden multicolumna acreditado. Se detectaron dos desajustes de contrato estáticamente demostrables en el perfilado geométrico; la calidad física/científica global sigue NO VERIFICABLE.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura basada en lectura directa del SHA fijado; cadena de extracción, tipos físicos, cobertura/rechazos B02, mapeo AST, perfilado y testigos sintéticos. Dos gaps locales estáticos, fronteras y cuestiones diferidas. Sin tests ejecutados ni FROZEN. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Revisión §4.7–4.8: fichas extendidas P1, contratos y destinos formales, control de cobertura por frontera, límites de testigos B01/B02/B03, propagación del perfil geométrico y reconciliación normativa. Sin cambios de producción, tests nuevos ni FROZEN. |

## 1. RESUMEN EJECUTIVO

Este HITO profundiza **únicamente la frontera PDF físico → PyMuPDF → DocumentLayout → AST → perfilado/OCR**, ya delimitada en PPPR.0.1. La decisión D-1/D-2 permanece cerrada: CLI → OCR Router → G3 → G5. No se reabren R1/R2/R3 ni se evalúa instalar nuevos motores. El hecho de conservar un PNG o rechazar un vector demuestra una conducta concreta, no que se pueda traducir cualquier paper ni que un PDF resultante sea científicamente fiel.

**Hallazgo central:**

> La ruta PDF→AST conectada conserva ciertos contenidos y rechaza pérdidas visibles, pero su perfil geométrico consume atributos que el AST construido no expone; los alcances de extracción STEM siguen condicionados por testigos parciales.

El punto más sólido de la primera pasada es el desacople entre `NodeMetadata.pages` y `NodeGeometryAdapter.page_number`: el sampler de primeras páginas recibe `0` para los AST construidos por esta ruta. En la misma proyección, el denominador para x relativa es `612` por falta de `page_width` en `NodeMetadata`. Son bugs de contrato geométrico verificables por lectura de las expresiones; no se ha cuantificado su impacto en corpus ni salida PDF.

**Defectos dominantes confirmados:** `GAP-0.2-01` (E-0.2-011) y `GAP-0.2-02` (E-0.2-012), ambos P1 locales; no se demuestra tasa de error científica.

**Veredicto provisional:** cobertura física parcial y explícita; dos gaps locales de perfilado corroborados estáticamente; orden científico por columnas, recuperabilidad semántica de fórmulas y fidelidad de documentos reales pendientes de evidencia proporcionada al riesgo. El HITO sigue `IN_PROGRESS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **OBSERVADO:** lectura directa de archivos en `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42` por GitHub, con métodos y puntos de transición identificados. El baseline de gobernanza no cambia código respecto de `main` (PR #66 contiene únicamente dos Markdown en el momento de apertura).
- **REQUIRED:** `PROJECT_SCOPE.md` §§2/4 (AST/linaje, completitud topológica, conservación de material técnico); `ENGINEERING_PRINCIPLES.md` §§III–IV (explicitud, ausencia de fallos silenciosos, trazabilidad), NADR-F17BIS-02 §5.1–5.2 (borde hexagonal y política de proveedor), más contratos explícitos del sampler, extractor y adaptador.
- **DECISION:** D-1/D-2 es selección de ruta, no dictamen de calidad. `capabilities` declara varias restricciones del proveedor; no inferir soporte por el nombre de una clase. F17-BIS-P2 es antecedente de un commit distinto, con afirmaciones ya superadas.
- **NO VERIFICABLE:** desempeño de PDFs científicos privados/canónicos, fidelidad de glifos no marcados como U+FFFD, orden de doble columna real, precisión de tablas/formulaciones, salida final de G5, SLO y host. No se inspeccionó corpus ni se hizo egress.
- **EJECUTADO:** solo lectura de código, documentación y tests. **No** se ejecutaron pytest, PyMuPDF, CI, OCR, Docker, LLM, Tectonic ni ensayos científicos. Ningún test `PASS` se acredita por leer sus aserciones.

El análisis usa tests existentes como **testigos versionados**, no como resultados nuevos. Se omite deliberadamente un grafo/runner temporal: los grafos del owner son índices históricos, no evidencia causal.

## 3. ALCANCE AUDITADO

**AUDITADO (código fuente directo, baseline fijado):**
- `apps/bootstrap/{extraction_config,provider_factory,pipeline_factory}.py`; `apps/ocr_router/__main__.py`; `infra/adapters/{pdf_parser,ast_profiling}.py`.
- `core/extraction/provider.py`; `infra/extraction/providers/{pymupdf_provider,pymupdf_integrity,pymupdf_math_visual,pymupdf_image_assets}.py`.
- `core/domain/document.py`, `core/layout/{models,classification,validator}.py`, `core/ast/{builder,models,strategy,cross_page}.py`.
- `core/document_profile/{profiler,models,extractors,ports,scoring}.py`, `core/document_profile/detectors/{layout,semantic}.py`.

**AUDITADO como fuente de cobertura de tests, NO como ejecución:** `tests/unit/{test_pipeline_factory,test_pymupdf_integrity,test_b022_image_rendering,test_b023_raster_asset_contract,test_b024_explicit_math_spans,test_b025_math_visual}.py`; `tests/integration/{test_golden_parser,test_pymupdf_extraction_integrity,test_b022_image_staging,test_b023_raster_image_pipeline,test_b024_g3_g5_math_roundtrip,test_b025_math_visual_preservation,test_g3_b4_2_ocr_router_durable_plan,test_g3_b4_4_profile_projection_assembly,test_real_parser_pipeline}.py`; YAML CI/CV como evidencia de disparadores, no de ejecuciones.

**REFERENCIADO sin auditoría semántica profunda:** `core/normalization/` (máscaras y normalización del HITO 0.3/0.4); `core/chunking/`, `core/context/`, `runtime/engine.py` (0.3–0.5); ensamblador y Tectonic (0.6); despliegue/host (0.7); benchmark, CV/GT (0.8).

**FUERA DEL SCOPE:** comparación o integración de Docling/Tesseract, red/proveedor comercial, rediseño G3/G5, modificación de oráculos/corpus, cambios de runtime.


### 3.1 Control de cobertura por responsabilidad contractual (§4.5 y §8.1)

La palabra **AUDITADO** significa lectura directa del símbolo relevante del archivo del SHA, **no** ejecución del módulo ni garantía completa del paquete. Los caminos ajenos al mandato se señalan como REFERENCIADOS; no se generaliza la ausencia de consumidores a partir de búsquedas indexadas. Inventario agrupado para evitar una ficha por archivo:

| Superficie / módulos incluidos | Símbolos y propiedad inspeccionada | Estado forense / evidencia | Límite |
|---|---|---|---|
| `apps/bootstrap/{extraction_config,provider_factory,pipeline_factory}.py`, `apps/ocr_router/__main__.py` | IDs, factory, `build_extraction_pipeline`, `build_document_profiler`, `OCRRouterDaemon._process_document` | **AUDITADO** — E-0.2-001, 010–013 | Persistencia, CAS, retries y cola delegados a PPPR.0.5 |
| `core/extraction/provider.py`, `infra/extraction/providers/pymupdf_{provider,integrity,math_visual,image_assets}.py` | Puerto, `capabilities`, `extract/_build_page`, guard B02, imagen, math-font, activos SHA | **AUDITADO** — E-0.2-002–008, 018 | No acredita contenido PDF invisible a PyMuPDF ni cobertura científica del corpus |
| `infra/adapters/pdf_parser.py`, `core/layout/{models,classification,validator}.py`, `core/domain/document.py` | Layout físico, tipos, clasificador heurístico, validación previa al AST y bordes de datos | **AUDITADO** — E-0.2-003, 008–010 | No se ejecutó el subsistema alterno `DocumentLayoutBuilder`; no está seleccionado por la factory inspeccionada |
| `core/ast/{builder,models,strategy,cross_page}.py` | DTO explícito, `NodeMetadata`, nodos/estrategias, sutura adyacente entre páginas | **AUDITADO** — E-0.2-009–012 | Fidelidad de segmentación, hash y chunking se examina en PPPR.0.3 |
| `infra/adapters/ast_profiling.py`, `core/document_profile/{profiler,models,extractors,ports,scoring}.py`, `core/document_profile/detectors/{layout,semantic}.py` | Extracción de BBox/página, sampling, umbrales de layout y dependencia de tipología | **AUDITADO** — E-0.2-011–013, 017 | Perfil persistido y uso real por G5 referidos a PPPR.0.5/0.6 |
| Tests `test_golden_parser`, `test_real_parser_pipeline`, `test_pymupdf_extraction_integrity`, B02.2–B02.5, `test_g3_b4_2_ocr_router_durable_plan`, `test_g3_b4_4_profile_projection_assembly` y `test_pipeline_factory` | Lectura de fixtures/aserciones y sustituciones técnicas, sin ejecución | **AUDITADO como código de tests** — E-0.2-014 | `NOT_RUN` en este HITO. No hay evidencia nueva de CI, Ground Truth, PDF comercial ni caso multicolumna calibrado |

**REFERENCIADO:** G3/plan/normalización (PPPR.0.3–0.5), render y compilador G5 (0.6), configuración de host (0.7), corpus/oráculos y medición científica (0.8). **NO VERIFICABLE en esta etapa:** comportamientos de PDFs reales no inspeccionados, proveedor comercial, artefactos externos y ejecución host. La delimitación es por **propiedad**, no por exclusión total de un archivo que aparezca en más de un HITO.

### 3.2 Alcance causal de los testigos existentes

| Testigo versionado (solo inspeccionado) | Qué **podría** falsar si se ejecutara en aislamiento | Qué **no** acredita por sí solo |
|---|---|---|
| `tests/integration/test_golden_parser.py`, `test_real_parser_pipeline.py` | Texto conocido, IDs y estabilidad en PDFs temporales simples de una/dos páginas, mediante factory real | Orden de dos columnas, detección de matemática no textual, integridad de todo paper STEM |
| `tests/integration/test_pymupdf_extraction_integrity.py`, `tests/unit/test_pymupdf_integrity.py` | Admisión texto simple, imagen embebida y rechazo de dibujo vectorial/sentinelas | Cobertura de objetos PyMuPDF no observados o exactitud de glifos sin sentinela |
| `test_b023_raster_image_pipeline.py`, `test_b025_math_visual_preservation.py` | Ruta sintética PNG/math-font → AST → PRESERVE → staging de activos G5 | Semántica de ecuaciones, fuente Unicode reconstruida, Tectonic real o PDF científico final |
| `test_b024_explicit_math_spans.py`, `test_b024_g3_g5_math_roundtrip.py` | Máscaras de delimitadores LaTeX **ya presentes en texto** y render acotado | Detección universal de fórmulas extraídas de un PDF |
| `test_g3_b4_2_ocr_router_durable_plan.py`, `test_g3_b4_4_profile_projection_assembly.py`, `test_b03_foreground_pdf_product.py` | Contratos de estados/perfiles con dobles o SQLite descartable | Muestreo correcto por página, sensibilidad a ancho físico, exactitud STEM ni E2E de producción |
| `test_b022_image_staging.py`, `test_b022_image_rendering.py` | Validación de referencia/path de PNG y TeX generado; el runner externo es stub en staging | Compilación física o preservación visual resultante |

En los testigos revisados **no aparece una aserción focal del par `NodeMetadata.pages`→`FirstPagesSamplingPolicy` ni de clasificación de columnas con ancho físico variable**. Esta conclusión está limitada a los archivos inspeccionados, no a toda la suite. No ejecutar tests ni generar corpus forma parte de la limitación explícita de esta pasada.

## 4. FUENTES DE EVIDENCIA

**Primarias del SHA `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`:** rutas en §3, con anclas verificables de GitHub:
- [Composición y mapper](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/apps/bootstrap/pipeline_factory.py#L159-L229)
- [Extracción física PyMuPDF](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/infra/extraction/providers/pymupdf_provider.py#L43-L416)
- [Guardia B02](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/infra/extraction/providers/pymupdf_integrity.py#L18-L64)
- [Math visual](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/infra/extraction/providers/pymupdf_math_visual.py#L20-L80)
- [PNG content-addressed](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/infra/extraction/providers/pymupdf_image_assets.py#L17-L62)
- [AST materializado](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/core/ast/builder.py#L87-L175)
- [Metadata del AST](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/core/ast/models.py#L13-L24)
- [Geometría y sampler](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/infra/adapters/ast_profiling.py#L29-L110)
- [Detección geométrica](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/core/document_profile/detectors/layout.py#L6-L56)
- [OCR conectado](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/apps/ocr_router/__main__.py#L100-L106)

**Normativa:** metodologías FROZEN, NADR-F17BIS-02, principios/scope. **Anterior descriptiva:** Atlas D-1/D-2 y [HITO 0.4.5-P2 F17-BIS](https://github.com/RDsanchez-git/translator_pdf/blob/1d21cfe958cc1de8a33824fed748cd6fe9260f42/docs/architecture/adr/phase-17-bis/00-foundation/HITO_0.4.5_P2_PHYSICAL_INGESTION_AUDIT.md), contrastado expresamente con el código actual.


### 4.1 Clasificación de autoridad de las fuentes (§4.6)

| Naturaleza | Fuentes y uso |
|---|---|
| **Normativa de proceso** | Metodología general v1.3.0 y metodología HITOs v1.2.0, ambas FROZEN: estado `IN_PROGRESS`, formato extendido, gaps y cierre |
| **Objetivo y principios** | `PROJECT_SCOPE.md` §2/§4 y `ENGINEERING_PRINCIPLES.md` §§III–IV: propósito de perfilado/linaje y rechazo de pérdidas silenciosas. No sustituyen una especificación física ya aprobada |
| **NADR FROZEN aplicable con frontera** | `NADR-F17BIS-02` §5.1–5.2: política/puertos de ingesta; **no regula el cálculo `page_width` ni el sampler de páginas** |
| **Evidencia primaria del estado actual** | Archivos Python y YAML de `main@1d21cfe` indicados en §3, con símbolos citados en E-IDs |
| **Testigos técnicos declarativos** | Fuentes de tests B01/B02/B03/G3: se auditan aserciones y sustituciones; **sin ejecuciones nuevas** |
| **Forense heredada** | HITO PPPR.0.1 FROZEN y F17-BIS-P2, este último reconciliado contra el SHA actual |
| **Decisión histórica descriptiva** | D-1/D-2 + Atlas: autoridad de ruta operativa, no comprobante de fidelidad científica |

## 5. MAPA DE FLUJOS OBSERVADOS

```text
CLI/admisión (PPPR.0.1; referenciado)
    → data/inbox/*.pdf
    → OCRRouterDaemon._process_document
    → build_extraction_pipeline()
         → ExtractionProviderFactory.create(PYMUPDF)
         → PyMuPDFProvider.extract(pdf_path)
              → fitz.open / page.get_text("dict") / page.get_drawings()
              → guard B02 de bloques/glifos/vectores
              → bloques de texto, PNG de imagen, PNG matemática visual o RECHAZO
              → LayoutPage[LayoutBlock] / DocumentLayout
         → PdfParserAdapter.parse
              → DocumentLayoutValidator.validate
              → LayoutBlock → LayoutBlockDraft (proyección explícita)
              → FlatASTBuilder → CrossPageNormalizer → ASTNode[]
    → OCRRouter: HeuristicDocumentProfiler.profile(AST)
         → FirstPagesSamplingPolicy → NodeGeometryAdapter → layout detector
    → hash/plan/snapshots/estado para G3 (PPPR.0.3/0.5)
```

El orden es el de bloques nativos de `page.get_text("dict")`, luego el mismo orden en páginas y `FlatASTBuilder`; **no se observa** en esta cadena resolución explícita de lectura por columnas. No deducir de ello un contraejemplo dinámico específico que no fue ejecutado.

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev. | Observed (fuente concreta) | Required / Decision / límite | Estado |
|---|---|---|---|---|
| **E-0.2-001** | P2 | `provider_factory.py::create` acepta `PYMUPDF` y rechaza otros IDs; `pipeline_factory.py::build_extraction_pipeline` lo usa por defecto. | NADR-F17BIS-02 exige política explícita; D-1/D-2 no autorizan segunda ruta. No conectar otros motores por inferencia. | CONECTADO |
| **E-0.2-002** | P2 | `pymupdf_provider.py::_build_page` toma `get_text("dict")` y `get_drawings()`, llama guard antes de materializar bloques de la página. | Rechazo observable, no exhaustividad visual. | OBSERVADO |
| **E-0.2-003** | P2 | `_extract_physical_block` concatena texto de spans por línea; `_extract_dominant_typography` reduce tipografía al estilo predominante; `_extract_raw_content` preserva `original/normalized/cleaned` hasta Layout. | Alcance de linaje de spans y tipografía en AST se limita a metadata/payload que realmente cruza el mapper. | OBSERVADO |
| **E-0.2-004** | P2 | `validate_pymupdf_page_coverage` rechaza `type != 0` salvo IMAGE permitido, y spans con U+FFFD/U+FFFF. | Otros glifos equivocados o ausentes pueden no activar estas dos sentinelas; ciencia no acreditada. | OBSERVADO |
| **E-0.2-005** | P2 | `pymupdf_provider.py::_image_block_to_png` decodifica rásteres sin máscaras/canales incompatibles; `persist_png_asset` utiliza SHA-256 y enlace atómico, verificando byte a byte la existencia previa. | Imagen rastreable no equivale a fidelidad de figuras científicas ni transacción multiartefacto global. | OBSERVADO |
| **E-0.2-006** | P2 | `pymupdf_math_visual.py` identifica fuentes matemáticas dedicadas; `visual` se rasteriza a PNG; `mixed` y fallos de bbox/size se rechazan. | No recupera semántica/LaTeX. Es preservación visual limitada, no reconocimiento universal. | OBSERVADO |
| **E-0.2-007** | P2 | Cualquier `page.get_drawings()` no vacío produce `B02_UNREPRESENTED_VECTOR_DRAWING`; el proveedor convierte ese error a `LayoutRecoveryError`. | Rechazo fail-closed evita invisibilizar vectores; cobertura de PDFs con gráficas no está demostrada. | OBSERVADO |
| **E-0.2-008** | P2 | Capacidades del proveedor: `has_tables=False`, `supports_math=False`, `supports_multicolumn=False`, `supports_rotation=False`; classifier heurístico termina en `PARAGRAPH` sin detector general de ecuaciones/tablas. | Declaración restrictiva; no inferir clasificación STEM de una etiqueta de clase ni prometer compatibilidad. | LIMITACIÓN |
| **E-0.2-009** | P2 | `_build_layout_block` fija `column_index=0`, y `_adapter_mapper` transporta ese campo; `FlatASTBuilder._map_physical_to_logical` no lo incorpora a `NodeMetadata` (sí lleva bbox/page y `layout_reading_order`). | Ruta no acredita orden de lectura de dos columnas. Bboxes no son, por sí mismas, un resolvedor de orden. | LIMITACIÓN |
| **E-0.2-010** | P2 | `PdfParserAdapter.parse` rechaza layout vacío o AST vacío; `DocumentLayoutValidator` comprueba páginas, IDs y geometrías antes del AST. | Contrato de rechazo observable. **No** reeditar el P2-07 histórico como si siguiera sin validador. | OBSERVADO |
| **E-0.2-011** | **P1** | `NodeMetadata` define `pages: List[int]`, no `page_number`; `NodeGeometryAdapter.extract` lee `getattr(metadata,"page_number",0)`. `FirstPagesSamplingPolicy.sample` decide el límite por ese valor, y `build_document_profiler` lo conecta a OCR. | Contrato declarado de sampling acotado por primeras páginas y principio de trazabilidad explícita. | **GAP-0.2-01** |
| **E-0.2-012** | **P1** | `NodeMetadata` no define `page_width`, y `NodeGeometryAdapter` divide `bbox.center_x` entre `612.0` por fallback. Los BBox del proveedor son absolutos (`is_normalized=False`). `HeuristicLayoutDetector` clasifica por `relative_center_x`. | Coordenada relativa correcta depende del ancho físico real; el fallback no lo representa si página ≠ 612 pt. | **GAP-0.2-02** |
| **E-0.2-013** | P2 | `OCRRouterDaemon._process_document` llama `parser.parse`, luego `profiler.profile`, y solo después calcula hash/plan/estado. | Corrobora que el perfilado desajustado **sí** está en la ruta seleccionada. Autoridad de plan/estado se audita en 0.3/0.5. | CONECTADO |
| **E-0.2-014** | P2 | Tests B02.2–B02.5 verifican por código fixtures sintéticos, PNG/staging, rechazo vectorial y math-font; OCR/plan usa dobles; B03 prueba texto/IDs de dos páginas temporales. | Test definido ≠ test ejecutado; no hay resultados nuevos de pytest, Tectonic real, CI en este PR o corpus STEM. | ALCANCE TESTIGO |
| **E-0.2-015** | P2 | El HITO F17-BIS P2 anotaba ausencia de mapper tipado y validador de Layout. En `main` actual `_layout_block_to_draft` y `DocumentLayoutValidator` existen y se llaman. | Reconciliación temporal: no reabrir P2-05/P2-07 como gaps actuales, sin afirmar que todos los defectos históricos estén resueltos. | HISTÓRICO RECONCILIADO |
| **E-0.2-016** | P2 | `ci.yml` y `continuous-verification.yml` contemplan PR con base `main`/`pipeline_stabilization`, no `pdf-pdf-product-readiness`. | El PR interno documental no adquiere CI PASS automáticamente; revisión focal sin atribuir éxitos no ejecutados. | OBSERVADO |
| **E-0.2-017** | P2 | `HeuristicTypeDetector._apply_layout_context` toma `LayoutDetection` para ponderar `PAPER/REPORT/BOOK`; `HeuristicDocumentProfiler.profile` pasa primero el layout detectado al clasificador semántico. | El defecto de geometría puede influir también sobre el tipo de perfil persistido, **sin** demostración de clasificación incorrecta en corpus. | CONEXIÓN CAUSAL |
| **E-0.2-018** | P2 | `PyMuPDFProvider.extract/_build_page` inspecciona texto físico e imágenes vía PyMuPDF; `_image_block_to_png` conserva rásteres como imagen, **no** transcribe el texto dentro de una imagen. | No acreditar un OCR raster general del producto por el nombre `OCRRouterDaemon`; no se investigó ningún servicio OCR externo. | LÍMITE OBSERVADO |


### Evidencia E-0.2-011: desacople de identidad de página en muestreo del profiler

* **Archivo fuente primario:** `core/ast/models.py`; corroboraciones `core/ast/builder.py`, `infra/adapters/ast_profiling.py`, `apps/bootstrap/pipeline_factory.py`, `core/document_profile/profiler.py` y `apps/ocr_router/__main__.py`.
* **Símbolos auditados:** `NodeMetadata`, `FlatASTBuilder._map_physical_to_logical`, `NodeGeometryAdapter.extract`, `FirstPagesSamplingPolicy.sample`, `build_document_profiler`, `OCRRouterDaemon._process_document`.
* **Declaración observada** (fragmentos literales mínimos; fuente `main@1d21cfe`):

```python
# core/ast/models.py::NodeMetadata
pages: List[int] = Field(default_factory=lambda: [])

# core/ast/builder.py::FlatASTBuilder._map_physical_to_logical
pages=[block.page_index],

# infra/adapters/ast_profiling.py::NodeGeometryAdapter.extract
page_num = getattr(metadata, "page_number", 0)

# infra/adapters/ast_profiling.py::FirstPagesSamplingPolicy.sample
page_num = geom.page_number if geom else 0
if page_num not in seen_pages:
    if len(seen_pages) >= self._max_pages:
        break
    seen_pages.add(page_num)
sampled.append(node)
```

* **Observed:** la producción de AST tipado sitúa la página en `metadata.pages` (lista) y **no** crea `metadata.page_number`. El adaptador consulta el segundo atributo, ausente, y entrega `0` aun para nodos de páginas distintas que tienen bbox. El sampler cuenta `0` como única página: con `max_pages >= 1` **no corta por número real de páginas** en esta ruta. `build_document_profiler` lo inyecta y OCR llama `document_profiler.profile`; no se trata de una clase aislada o de un harness.
* **Required:** el contrato directo `ProfileSamplingPolicy.sample` y la semántica explícita de `FirstPagesSamplingPolicy(max_pages)` requieren un número de página distinguible para acotar las **primeras páginas**. `ENGINEERING_PRINCIPLES.md` §III (explicitud/tipos) y §IV (trazabilidad de índices físicos) demandan conservar esa identidad a través del borde. **No** se atribuye este requisito a NADR-F17BIS-02.
* **Decision:** D-1/D-2 seleccionaron OCR→G3→G5, sin aprobar semántica alternativa de muestreo. Los comentarios `Bounded Workload` del código son evidencia del contrato intencional, **no** un NADR adicional.
* **Hallazgo forense:** discrepancia tipada y causal `pages: List[int]`→lectura de `page_number`; `max_pages` no representa número real de páginas para los nodos AST producidos por este mapper.
* **Consecuencia arquitectónica demostrada:** el volumen que procesa el profiler deja de estar acotado por las primeras `N` páginas; depende de todos los nodos que atraviesan el sampler, y la muestra observada por clasificadores puede incluir páginas posteriores a `N`. **No** se ha medido consumo de CPU, coste, tasa de clasificación errónea ni un PDF final.
* **Severidad:** **P1 / LOCAL**, por violación estructural del contrato tipado y de trazabilidad en la frontera AST→perfilado, no por una medición de degradación científica.
* **Estado:** **OPEN** → `GAP-0.2-01`. Destino: gobernanza PPPR posterior a Fase 0, con testigo focal de verificación a delimitar (PPPR.0.8). Owner de implementación **no asignado** antes del Execution Plan.

### Evidencia E-0.2-012: escala física no preservada para geometría relativa

* **Archivo fuente primario:** `infra/adapters/ast_profiling.py`; corroboraciones `core/ast/models.py`, `core/ast/builder.py`, `core/domain/document.py`, `infra/extraction/providers/pymupdf_provider.py`, `core/document_profile/detectors/layout.py`, `core/document_profile/detectors/semantic.py`, `core/document_profile/profiler.py`.
* **Símbolos auditados:** `NodeGeometryAdapter.extract`, `NodeMetadata`, `FlatASTBuilder._map_physical_to_logical`, `PyMuPDFProvider._build_page/_build_bbox`, `HeuristicLayoutDetector.detect`, `HeuristicTypeDetector._apply_layout_context`.
* **Declaración observada** (fragmentos literales mínimos; `main@1d21cfe`):

```python
# infra/adapters/ast_profiling.py::NodeGeometryAdapter
_FALLBACK_PAGE_WIDTH = 612.0
page_width = getattr(metadata, "page_width", self._FALLBACK_PAGE_WIDTH)
if not page_width or page_width <= 0:
    page_width = self._FALLBACK_PAGE_WIDTH
relative_center_x=center_x / page_width,

# core/ast/models.py::NodeMetadata (campos geométricos)
bboxes: List[BoundingBox] = Field(default_factory=lambda: [])
pages: List[int] = Field(default_factory=lambda: [])

# core/ast/builder.py::_map_physical_to_logical
bboxes=[block.bbox],

# core/document_profile/detectors/layout.py
if geom.relative_center_x <= self._LEFT_CLUSTER_MAX:  # 0.40
    left_mass += 1
elif geom.relative_center_x >= self._RIGHT_CLUSTER_MIN:  # 0.60
    right_mass += 1
```

* **Observed:** PyMuPDF produce `PageDimensions.width` a partir de la página y bboxes absolutos (`is_normalized=False`); el mapper a AST transporta BBox, pero **no** ancho físico de página a `NodeMetadata`. El adaptador recupera sistemáticamente el valor fijo `612.0` para los AST tipados de esta ruta; el detector consume ese cociente como si fuera relativo al ancho real.
* **Required:** contrato matemático de `NodeGeometry.relative_center_x` y de umbrales de `HeuristicLayoutDetector`: una posición **relativa a la página fuente** requiere dividir por el ancho de esa página, o partir de una geometría realmente normalizada. `ENGINEERING_PRINCIPLES.md` §IV exige linaje físico intacto y §III, transformación explícita. **NADR-F17BIS-02 no establece una regla numérica de geometría.**
* **Decision:** el perfilado está conectado en OCR por la factory seleccionada (D-1/D-2); no existe decisión formal acreditada que autorice usar 612 puntos para toda dimensión de página.
* **Hallazgo forense:** se pierde el denominador físico al cruzar el borde Layout→AST→profiler. **Ejemplo aritmético, no test ejecutado:** en una página de ancho 300 pt y un bbox válido `x0=180, x1=240`, el centro está en 210 pt: valor verdadero `210/300 = 0.70` (región derecha `>= 0.60`), mientras el adapter emite `210/612 ≈ 0.343` (región izquierda `<= 0.40`). Este ejemplo demuestra que el error puede invertir la asignación de un nodo; no demuestra que un corpus concreto tenga ese caso.
* **Consecuencia arquitectónica demostrada:** el detector opera sobre masas laterales potencialmente mal asignadas; su `LayoutDetection` alimenta `HeuristicTypeDetector`, que pesa tipos `PAPER/REPORT/BOOK` en función de ese layout (E-0.2-017). El efecto sobre un documento o el render G5 sigue **NO VERIFICABLE** sin un falsador aislado y el HITO 0.6.
* **Severidad:** **P1 / LOCAL** en proyección geométrica y perfilado, respaldado por umbrales explícitos y ejemplo causal; no P0 ni certificación de defecto científico global.
* **Estado:** **OPEN** → `GAP-0.2-02`. Destino: gobernanza PPPR posterior a Fase 0, con verificación focal a delimitar en PPPR.0.8; sin owner operativo asignado hasta Execution Plan.

**Interpretación de severidad:** P1 en E-011/012 significa desajuste estructural verificable por flujo de datos, **no** que se haya medido una tasa de fallo científica. P2 describe decisiones conservadoras, alcance limitado o testigos parciales; no significa defecto.

## 14. GAPS CONSOLIDADOS (PROVISIONALES)

Se consolida aquí el **delta local** al contrato observado, no una Gap Matrix transversal (reservada a PPPR.0.9). El campo «Fase destino» identifica la **etapa futura PPPR después de cerrar Fase 0** y el gate documental que deberá valorar la obligación; **no** crea una nueva fase numerada ni una tarea de implementación ya aprobada.

| GAP | Descripción | Evidencia | Pilar / contrato afectado | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.2-01** | La identidad de página `NodeMetadata.pages` no llega a `NodeGeometryAdapter.page_number`; el muestreo no acota primeras páginas cuando `max_pages >= 1` | **E-0.2-011**; recorrido E-0.2-013 | `ProfileSamplingPolicy.sample` / `FirstPagesSamplingPolicy(max_pages)`; `ENGINEERING_PRINCIPLES.md` §§III–IV (índices físicos/tipado). **No** NADR-F17BIS-02 | **Iniciativa PPPR, etapa pos-Fase 0**: evaluar en ADR Maestro y reglas existentes; solo tras gobernanza aprobada, trazar tarea en Execution Plan. Falsador de alcance en HITO PPPR.0.8 | **OPEN (P1 / LOCAL)** |
| **GAP-0.2-02** | El adaptador divide centro de BBox absoluto por `612.0` al no recibir `page_width`, aunque el ancho real de página puede diferir | **E-0.2-012**; propagación E-0.2-017 | `NodeGeometry.relative_center_x` + umbrales de `HeuristicLayoutDetector`; `ENGINEERING_PRINCIPLES.md` §§III–IV (linaje geométrico). **No** NADR-F17BIS-02 | **Iniciativa PPPR, etapa pos-Fase 0**: evaluar alcance en ADR Maestro y regla aplicable existente antes de crear NADR. Execution Plan posterior; testigo en HITO PPPR.0.8, consumidor G5 en PPPR.0.6 | **OPEN (P1 / LOCAL)** |

**Responsable de implementación:** `NO ASIGNADO` hasta el Execution Plan aprobado. El HITO identifica el módulo responsable del comportamiento y la etapa de decisión, sin predefinir solución, wave, ownership operativo o merge. No se registran como gaps automáticamente: rechazo de vectores, falta de reconocimiento matemático universal, ausencia de OCR de rásteres, proveedor alternativo no conectado, multicolumna no soportada o resultados científicos no ejecutados. Son límites de producto/posibles decisiones de alcance, salvo que otra evidencia demuestre incumplimiento de una obligación exigible.

## 15. ESTADO DE HIPÓTESIS Y CUESTIONES DIFERIDAS

| ID | Pregunta falsable | Estado actual y razón | Destino |
|---|---|---|---|
| **H-0.2-A** | ¿Preserva un paper real de dos columnas la secuencia lógica de lectura nativa? | `NO VERIFICABLE` con lectura estática; código no reordena y no se ejecutó PDF con oráculo de lectura. | PPPR.0.8 (evidencia/corpus autorizado) y 0.3 (consumidor AST); no bloquea inventario de frontera. |
| **H-0.2-B** | ¿Existen glifos matemáticos erróneos sin sentinelas Unicode detectables? | `NO VERIFICABLE` sin fuente PDF/GT; guard vigila dos codepoints, no todas las sustituciones. | PPPR.0.8 |
| **H-0.2-C** | ¿Qué cobertura física logra la ruta ante tablas rasterizadas, trazos vectoriales y bloques mixtos STEM de papers reales? | `NO VERIFICABLE` sin corpus; hay rutas de rechazo/PNG, no benchmark científico. | PPPR.0.8, decisión de alcance en ADR PPPR |
| **H-0.2-D** | ¿La clasificación de layout incorrecta afecta efectivamente el PDF G5 final? | `NO VERIFICABLE`: falla de proyección estática confirmada, cadena downstream de layout/TeX no medida. | PPPR.0.6 y 0.8 |

Las hipótesis no declaran una nueva implementación ni un gap sin evidencia. Para FROZEN debe reconciliarse el cierre de todo `TO BE VERIFIED` según §8.2, revisar cobertura del perímetro y explicitar garantías.

## 16. RESPUESTAS PROVISIONALES AL MANDATO

1. **Representado:** texto PyMuPDF (por bloque/line/spans proyectados a texto y tipografía dominante), BBox absoluto y página en AST; imagen ráster decodificable y ciertos bloques matemáticos visuales como referencias SHA-256 a PNG, con `PRESERVE` al pasar por la estrategia tipada.
2. **Transformado:** bloques físicos → `LayoutBlock` → `LayoutBlockDraft` → `ASTNode`; colapsan señales tipográficas a predominantes y metadatos espaciales parcialmente; `CrossPageNormalizer` puede fusionar límites según heurística textual, sin test aquí de corrección científica.
3. **Rechazado:** vectores detectados, bloques de tipo no soportado, glifos sentinela, imágenes incompatibles, mixed math/prose identificada, geometrías inválidas, mapeo/límites vacíos. No extrapolar estos rechazos a exhaustividad física.
4. **No acreditado:** completitud matemática, lectura por columnas, reconocimiento de tablas, fidelidad de todas las figuras, eficiencia del sampler de páginas, calidad lingüística/física PDF→PDF, garantía host/egress.

## 21. CIERRE DEL HITO — ESTADO IN_PROGRESS

**NO FROZEN.** §4.7–4.8 revisados y fichas P1 formalizadas. Siguen pendientes: revisión de la suficiencia de cobertura contra el mandato completo, reconciliación de límites STEM con lo verificable sin corpus, comprobación del alcance de tests focales (solo si se autoriza ejecutar), validación de hipótesis `NO VERIFICABLE` como Deferred Questions no bloqueantes, y checklist §8.1–8.2 formal previo a cierre. No existe `PASS` científico o test nuevo. Ninguna decisión de diseño, código, ADR/NADR o Execution Plan fue aprobada por este HITO.

**Siguiente gate:** revisión forense del documento en PR interno a `pdf-pdf-product-readiness`; atender observaciones y resolver las hipótesis conforme a §8.2 antes de solicitar FROZEN. Mantener #66 Draft, sin merge a `main`; implementación solo tras gobernanza completa integrada.
