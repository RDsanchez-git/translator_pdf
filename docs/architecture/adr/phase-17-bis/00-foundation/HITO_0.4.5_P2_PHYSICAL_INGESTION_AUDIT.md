# HITO_0.4.5_P2_PHYSICAL_INGESTION_AUDIT.md
## Physical Ingestion, Layout Subsystem, Boundary Projections & AST V2 Materialization — Reporte Consolidado Bloque P2

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P2)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P2)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en el análisis AST del código fuente de producción y el Grafo de Ingestión Física de Dependencias (`P2_PHYSICAL_INGESTION_GRAPH.md`). Cero mutaciones en código productivo. Disposición y acciones diferidas al Hito 0.5.

---

## 1. MARCO EPISTEMOLÓGICO Y RESPUESTAS A PREGUNTAS FORENSES CLAVE

El escrutinio forense del Bloque P2 sobre la frontera de ingesta física, maquetación $2\text{D}$ y materialización del AST V2 ha resuelto la paradoja de tipos identificada en el análisis del grafo estático. La evidencia demuestra que existen **tres fronteras de datos distintas que no deben confundirse**:

```text
  [PDF Físico Input]
       │
       ▼  (Boundary 1: Ingesta Física ──► Dominio Físico de Producción)
  [DocumentLayout / LayoutBlock] (core.domain.document)
       │
       ├──────────────────────────────────────────┐
       │                                          │
       ▼ (Camino de Producción Real)              ▼ (Proyección del Harness de Benchmark)
  [_adapter_mapper()]                        [_pipeline_layout_to_ast()]
       │                                          │
       ▼                                          ▼ (Boundary 2: Dominio ──► DTO Benchmark)
  [LayoutBlockCollection]                    [LayoutBlockDraft]
       │                                          │
       ▼ (Boundary 3: Layout ──► AST V2)           ▼
  [FlatASTBuilder.build()]                   [LayoutBlockCollection]
       │                                          │
       ▼                                          ▼
  [ASTNode Sequence]                         [FlatASTBuilder.build()] ──► [Golden Draft]
```

### 1.1. Respuestas Directas a las Preguntas Forenses de Ingesta

1. **¿El flujo PDF $\rightarrow$ ExtractionProvider $\rightarrow$ DocumentLayout $\rightarrow$ Layout $\rightarrow$ FlatASTBuilder $\rightarrow$ AST es realmente así?**
   **Sí.** El grafo lo respalda y no aparece ninguna ruta directa desde los proveedores hacia el AST. `ExtractionProvider` emite exclusivamente `DocumentLayout`[cite: 1].
2. **¿Hay rutas alternativas?**
   **Sí, pero únicamente en la etapa de extracción física:** `ExtractionProvider` posee implementaciones para `PyMuPDFProvider`[cite: 1], `DoclingProvider`[cite: 1] y `TesseractProvider`[cite: 1]. A partir de `DocumentLayout`[cite: 1], el flujo converge en el mismo pipeline.
3. **¿El `PdfParserAdapter` pertenece al pipeline real o es histórico/test?**
   **Pertenece al pipeline real.** `build_pipeline()` en `apps/bootstrap/pipeline_factory.py` instancía explícitamente `PdfParserAdapter`[cite: 1]. El framework de benchmark lo reutiliza mediante `BenchmarkParserBridge`[cite: 1]; no es un componente legado ni exclusivo de pruebas.
4. **¿Dónde se hace realmente el boundary crossing?**
   El boundary de producción está en la **transición Layout $\rightarrow$ AST**, materializada por `FlatASTBuilder`[cite: 1] (precedido por la preparación de `LayoutBlockCollection`[cite: 1]). El boundary `LayoutBlock` $\rightarrow$ `LayoutBlockDraft` pertenece exclusivamente al harness de calibración/benchmark y no forma parte del pipeline productivo real[cite: 1].

---

## 2. REGISTRO EXHAUSTIVO DE EVIDENCIA FORENSE Y HALLAZGOS TÉCNICOS

### 2.1. Confirmaciones Positivas de Arquitectura

* **Hallazgos P2-01 (Separación Limpia Extraction vs. AST):** Ningún proveedor físico (`PyMuPDFProvider`[cite: 1], `DoclingProvider`[cite: 1], `TesseractProvider`[cite: 1]) conoce la estructura del AST V2[cite: 1]. Retornan exclusivamente Aggregate `DocumentLayout`[cite: 1].
* **Hallazgos P2-02 (Intercambiabilidad Polimórfica de Proveedores):** Los tres proveedores heredan e implementan el contrato `ExtractionProvider`[cite: 1]. El pipeline depende del puerto y no de un proveedor concreto.
* **Hallazgos P2-03 (Reutilización de Infraestructura por el Benchmark):** `BenchmarkParserBridge`[cite: 1] delega directamente en `PdfParserAdapter`[cite: 1]. El benchmark reutiliza el pipeline de extracción de producción sin clonar ni modificar la lógica de ingesta física.
* **Hallazgos P2-04 (Posición Correcta de `CrossPageNormalizer`):** `FlatASTBuilder.build()`[cite: 1] invoca `CrossPageNormalizer`[cite: 1] inmediatamente después de la proyección inicial a `ASTNode`[cite: 1]. Se confirma que la resolución de guiones y unión de párrafos divididos opera correctamente sobre la secuencia lógica del AST pre-segmentación[cite: 1].

---

### 2.2. Defectos Críticos y Brechas de Integración en Producción

#### P2-05 (Duck-Typing e Incompatibilidad de Tipos en `_adapter_mapper`) [P0 - CRÍTICO]
* **Ubicación:** `apps/bootstrap/pipeline_factory.py` (`_adapter_mapper`)[cite: 1] vs. `core/ast/builder.py` (`FlatASTBuilder`)[cite: 1]
* **Mecanismo Causal:** `PyMuPDFProvider.extract()`[cite: 1] retorna instancias de `core.domain.document.LayoutBlock`. En `pipeline_factory.py`[cite: 1], `_adapter_mapper` alana los bloques:
  ```python
  def _adapter_mapper(document_layout: DocumentLayout) -> list[ASTNode]:
      flat_blocks = []
      for page in document_layout.pages:
          flat_blocks.extend(page.blocks)  # Inyecta LayoutBlock (core.domain.document)
      collection = LayoutBlockCollection(blocks=flat_blocks)  # ¡Exige LayoutBlockDraft!
      return mapper.build(collection)
  ```
  `LayoutBlockCollection` (en `core/layout/models.py`[cite: 1]) declara `blocks: List[LayoutBlockDraft]`. `FlatASTBuilder.build()`[cite: 1] itera sobre la colección llamando a `_map_physical_to_logical(block)`[cite: 1], accediendo a atributos compartidos (`block.content`, `block.bbox`).
* **Impacto Arquitectónico:** La integración en runtime se sostiene **únicamente por duck-typing accidental** en Python. Dado que `LayoutBlock` y `LayoutBlockDraft` comparten nombres de atributos comunes, la aplicación no colapsa en ejecución simple, pero destruye la validación estática de tipos (`pyright` / `mypy`) y causa fallas al intentar re-validar el objeto con Pydantic v2.

#### P2-06 (Bypassing Completo del Sub-sistema `DocumentLayoutBuilder`) [P0 - CRÍTICO]
* **Ubicación:** `core/layout/builder.py`[cite: 1] vs. `apps/bootstrap/pipeline_factory.py`[cite: 1]
* **Mecanismo Causal:** El paquete `core/layout/`[cite: 1] aloja un orquestador de maquetación $2\text{D}$ (`DocumentLayoutBuilder`)[cite: 1] estructurado en seis etapas (*stages*) independientes:
  1. `CoordinateNormalizer`: Escala BoundingBoxes al espacio normalizado $[0.0, 1.0]$[cite: 1].
  2. `SpatialAnalyzer`: Detecta canales (*gutters*) y columnas físicas[cite: 1].
  3. `BlockIdentityGenerator`: Asigna IDs deterministas content-addressed[cite: 1].
  4. `ReadingOrderResolver`: Construye el grafo acíclico directed (DAG) para determinar el orden de lectura topológico[cite: 1].
  5. `LogicalClassifier`: Clasifica heurísticamente títulos, código, tablas y fórmulas[cite: 1].
  6. `SpatialMerger`: Fusiona bloques adyacentes pertenecientes al mismo flujo textual[cite: 1].
* **Evidencia del Grafo AST:** `pipeline_factory.py`[cite: 1] **jamás instancía ni ejecuta `DocumentLayoutBuilder`**[cite: 1]. Los bloques extraídos por `PyMuPDFProvider`[cite: 1] saltan directamente a `FlatASTBuilder`[cite: 1].
* **Impacto Arquitectónico:** Todo el motor de procesamiento espacial $2\text{D}$ de `core/layout/`[cite: 1] es **código zombi / inalcanzable** en el pipeline real de producción. El sistema traduce el PDF asumiendo que el orden físico crudo entregado por PyMuPDF[cite: 1] es el orden lógico definitivo, sin resolver lecturas multi-columna ni corregir geometrías.

#### P2-07 (Omisión del `DocumentLayoutValidator` en Production Factory) [P1 - ALTO]
* **Ubicación:** `core/layout/validator.py` (`DocumentLayoutValidator`)[cite: 1]
* **Mecanismo Causal:** `DocumentLayoutValidator.validate()`[cite: 1] certifica que el `DocumentLayout`[cite: 1] extraído no contenga páginas vacías, números de página duplicados o BoundingBoxes fuera de rango[cite: 1].
* **Impacto ArquITECTÓNICO:** `pipeline_factory.py`[cite: 1] no invoca este validador. Si el extractor físico entrega una página sin bloques o un BoundingBox corrupto (`bbox = None`), el fallo no se detiene de forma *Fail-Fast* en la ingesta, sino que se propaga aguas abajo hasta el chunker o el compilador LaTeX.

#### P2-08 (Hardcoding de Extractor e Inoperancia de `DEFAULT_EXTRACTION_PROVIDER`) [P1 - ALTO]
* **Ubicación:** `apps/bootstrap/pipeline_factory.py`[cite: 1]
* **Mecanismo Causal:** Aunque el módulo declara la constante `DEFAULT_EXTRACTION_PROVIDER: ProviderKind = ProviderKind.OCR_PARSER`[cite: 1], la función `build_pipeline()`[cite: 1] fija imperativamente:
  ```python
  provider = PyMuPDFProvider()
  ```
* **Impacto ArquITECTÓNICO:** `DoclingProvider` (`core/extraction/ocr_providers/docling_provider.py`)[cite: 1] y `TesseractProvider` (`core/extraction/ocr_providers/tesseract_provider.py`)[cite: 1] están desconectados del pipeline productivo. No existe un mecanismo en the Composition Root para conmutar dinámicamente de motor según el perfil del documento.

#### P2-09 (Invasión de Infraestructura en Dominio: Leak de PyMuPDF en `PDFRouter`) [P1 - ALTO]
* **Ubicación:** `core/ast/router.py` (`PDFRouter`)[cite: 1]
* **Mecanismo Causal:** El módulo de dominio `PDFRouter.detect_pdf_type()`[cite: 1] realiza una importación directa de la librería C/Python `fitz` (PyMuPDF) para analizar el árbol de objetos del PDF.
* **Impacto ArquITECTÓNICO:** Violación directa de Clean Architecture. El dominio de enrutamiento depende físicamente de una librería de infraestructura en lugar de interrogar las capacidades expuestas por el puerto `ExtractionProvider.capabilities()`[cite: 1].

#### P2-10 (Destrucción de Metadatos Espaciales $2\text{D}$ en `FlatASTBuilder`) [P1 - ALTO]
* **Ubicación:** `core/ast/builder.py` (`_map_physical_to_logical`)[cite: 1]
* **Mecanismo Causal:** Durante el mapeo de `LayoutBlockDraft` a `ASTNode`, el constructor copia la BoundingBox y el contenido, pero omite transferir `column_index` y los identificadores de parentesco jerárquico hacia el `control_plane` del nodo.
* **Impacto ArquITECTÓNICO:** Se pierde la información de maquetación $2\text{D}$ (distribución multi-columna y jerarquía espacial) en el momento exacto en que el documento se convierte en el vector lineal del AST V2.

---

## 3. GRAFO Y TRAZABILIDAD DEL FLUJO FÍSICO REAL VS. BENCHMARK HARNESS

El Grafo de Ingestión Física (`P2_PHYSICAL_INGESTION_GRAPH.md`) expone la separación real de caminos entre la ejecución productiva y la suite de calibración:

```text
==================================================================================================
                             FLUJO REAL DE PRODUCCIÓN (OBSERVADO EN P2)
==================================================================================================

  PDF Input ──► PyMuPDFProvider.extract()
                     │
                     ▼
              DocumentLayout (Domain: LayoutBlock)
                     │
                     ├──────────────┐
                     │ (BYPASS ✗)   │  [Bypassea DocumentLayoutBuilder y sus 6 stages]
                     │              │  [Bypassea DocumentLayoutValidator]
                     ▼              │
        _adapter_mapper() ◄─────────┘  (Mezcla incompatible: asigna LayoutBlock a
                     │                  LayoutBlockCollection expecting LayoutBlockDraft)
                     ▼
           LayoutBlockCollection
                     │
                     ▼
           FlatASTBuilder.build() ──► CrossPageNormalizer ──► list[ASTNode] (AST V2)

==================================================================================================
                           PROYECCIÓN DEL HARNESS DE BENCHMARK / CALIBRACIÓN
==================================================================================================

  DocumentLayout (Domain: LayoutBlock)
         │
         ▼
  run_calibration_v1.py / generate_golden_draft.py
         │
         ├── Proyección explícita: LayoutBlock ──► LayoutBlockDraft
         ├── Empaquetamiento: LayoutBlockCollection(blocks=draft_blocks)
         ├── Invocación: FlatASTBuilder.build(collection)
         └── Generación: Golden Draft AST (.ast.json)
```

---

## 4. TAXONOMÍA Y MATRIZ DE COMPONENTES DEL BLOQUE P2

| Componente / Módulo | Categoría | Severidad del Defecto | Hallazgo Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `core/extraction/provider.py` | Port Contract | **Cero** | Contrato `ExtractionProvider` puro usando `Protocol`[cite: 1]. | **CONSERVAR** |
| `ocr_providers/pymupdf_provider.py` | Concrete Adapter | **P1 (Alto)** | Genera `DocumentLayout` válido[cite: 1]; acoplado rígidamente en fábrica[cite: 1]. | **CONSERVAR / DESACOPLAR** |
| `ocr_providers/docling_provider.py` | Concrete Adapter | **P1 (Alto)** | Funcional[cite: 1]; inalcanzable en fábrica de producción. | **CONECTAR EN FACTORY** |
| `ocr_providers/tesseract_provider.py`| Concrete Adapter | **P1 (Alto)** | Inalcanzable en el pipeline de producción[cite: 1]. | **CONECTAR EN FACTORY** |
| `core/layout/builder.py` | Layout Subsystem | **P0 (Crítico)** | `DocumentLayoutBuilder` no se ejecuta (Pipeline Zombi)[cite: 1]. | **INTEGRAR O DEPRECAR** |
| `core/layout/models.py` | Layout DTOs | **P0 (Crítico)** | Duck-typing entre `LayoutBlock` y `LayoutBlockDraft`[cite: 1]. | **SANEAR TIPOS / MAPPER** |
| `core/layout/validator.py` | Validation | **P1 (Alto)** | `DocumentLayoutValidator` omitido en fábrica productiva[cite: 1]. | **INTEGRAR EN FACTORY** |
| `infra/adapters/pdf_parser.py` | Application Bridge| **P1 (Alto)** | `PdfParserAdapter` delega el mapeo a lambda interna[cite: 1]. | **REFACTORIZAR MAPPER** |
| `core/ast/builder.py` | AST Materializer | **P1 (Alto)** | `FlatASTBuilder` asume `LayoutBlockDraft` y pierde metadatos $2\text{D}$[cite: 1]. | **REFACTORIZAR MAPPER** |
| `core/ast/router.py` | Domain Router | **P1 (Alto)** | Importa `fitz` (PyMuPDF) directamente en el dominio[cite: 1]. | **MOVER FITZ A INFRA** |

---

## 5. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P2-R01 A P2-R08)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P2-R01 (Saneamiento de Tipos en the Boundary - P0):** Eliminar el acoplamiento por *duck-typing* en `_adapter_mapper`. Definir una función de transformación explícita que convierta `core.domain.document.LayoutBlock` a `core.layout.models.LayoutBlockDraft` antes de instanciar `LayoutBlockCollection`, o refactorizar `FlatASTBuilder` para que acepte directamente el Aggregate `DocumentLayout`.
* **P2-R02 (Gobernanza sobre `DocumentLayoutBuilder` - P0):** Decidir formalmente en el Hito 0.5 si `DocumentLayoutBuilder` (y sus 6 etapas de ordenamiento de lectura, detección de columnas y fusión geométrica) se integra activamente en el pipeline de producción de la Fase 17, o si se depreca oficialmente en favor del aplanado directo.
* **P2-R03 (Factoría Dinámica de Extracción - P0):** Refactorizar `apps/bootstrap/pipeline_factory.py` para instanciar dinámicamente `PyMuPDFProvider`, `DoclingProvider` o `TesseractProvider` leyendo el parámetro de configuración `DEFAULT_EXTRACTION_PROVIDER` o variables de entorno.
* **P2-R04 (Integración del Validador de Maquetación):** Inyectar `DocumentLayoutValidator` dentro del flujo de `PdfParserAdapter` o en `pipeline_factory.py`, garantizando que cualquier documento con geometrías nulas o páginas corruptas sea rechazado de forma *Fail-Fast*.
* **P2-R05 (Limpieza de Invasión de Infraestructura en Dominio):** Eliminar la importación de PyMuPDF (`import fitz`) en `core/ast/router.py`. La inspección de capacidades del PDF debe realizarse a través del puerto `ExtractionProvider.capabilities()`.
* **P2-R06 (Preservación de Metadatos $2\text{D}$ en el AST):** Modificar `FlatASTBuilder._map_physical_to_logical` para preservar el `column_index`, el BoundingBox normalizado y las referencias jerárquicas en el `control_plane` de cada `ASTNode` generado.
* **P2-R07 (Aislamiento de Mappers en Adapters):** Extraer la función `_adapter_mapper` fuera del cuerpo de `build_pipeline()` en `pipeline_factory.py`, convirtiéndola en un componente nombrado, testeable y reutilizable dentro de `infra/adapters/`.
* **P2-R08 (Contrato Estricto de BoundingBox Normalizado):** Exigir que todo proveedor de extracción entregue coordenadas normalizadas en escala $[0.0, 1.0]$ dentro de `DocumentLayout`, rechazando coordenadas absolutas en puntos tipográficos que no hayan sido convertidas previa entrega.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Modelado Físico y Abstracción de Proveedores:** **SÓLIDO Y BIEN CONCEBIDO.** Las interfaces `ExtractionProvider`, `DocumentLayout` y `ASTNode` están conceptualmente alineadas con DDD y Arquitectura Hexagonal. `ExtractionProvider` produce exclusivamente `DocumentLayout` (no AST), `PdfParserAdapter` pertenece formalmente al wiring real, los proveedores son polimórficamente intercambiables y el benchmark reutiliza la infraestructura de producción sin contaminar el runtime.
2. **Integración en Runtime y Transformación de Entrada:** **CRÍTICAMENTE DEFECTUOSA.** Se detectaron compatibilidades de tipo accidentales por *duck-typing*, el abandono del sub-sistema de maquetación $2\text{D}$ (`DocumentLayoutBuilder`) en el pipeline productivo y la imposibilidad de seleccionar proveedores de extracción en tiempo de ejecución.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P2

The audit for **Block P2 (Physical Ingestion $\rightarrow$ Layout $\rightarrow$ AST)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P2
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Relajamiento de tipos y layout bypass)
  Remediation Backlog      | OPEN (Reglas P2-R01 a P2-R08 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque P2. Se certificó la validez contractual de ExtractionProvider, PdfParserAdapter y la reutilización limpia por parte del Benchmark. No obstante, se constató que la ingesta física de producción sufre de un desacoplamiento de tipos entre LayoutBlock y LayoutBlockDraft en la función _adapter_mapper, que el sub-sistema DocumentLayoutBuilder está completamente omitido en el runtime real y que la selección de proveedores de extracción está hardcodeada. Queda strictly prohibido mutar código. Todos los hallazgos se registran en el backlog de remediación, habilitando la apertura de la auditoría del Bloque P3 (AST $\rightarrow$ Normalization $\rightarrow$ Segmenter $\rightarrow$ Router $\rightarrow$ Chunking)."*