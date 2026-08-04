# HITO_0.4.5_P3_TRANSFORMATION_SEGMENTATION_CHUNKING_AUDIT.md
## AST Transformations, Normalization, Segmenter V2 Isolation, Routing Channels & Chunking Boundaries — Reporte de Auditoría Forense Integral Bloque P3

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P3)
* **Fecha de Emisión:** 2026-07-29
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P3)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en la inspección del código fuente de producción (`core/ast/builder.py`, `core/ast/hashing.py`, `core/ast/parser.py`, `core/benchmark/__main__.py` y `core/pipeline/orchestrator.py`), aplicando el protocolo de investigación de 15 capas. Cero suposiciones. Cero mutaciones en código productivo.

---

## 1. MARCO EPISTEMOLÓGICO Y DIAGNÓSTICO DE RUNTIME

Sometiendo el sistema al protocolo de investigación de 15 capas (Capa 1: Evidencia vs. Interpretación; Capa 11: Falsación Sistemática; Capa 12: Clasificación Epistemológica), la lectura directa del código fuente de producción **ha confirmado empíricamente las desconexiones estructurales detectadas en el grafo estático y ha revelado nuevas anomalías críticas de diseño**.

El flujo teórico declarado en la Fase 16 ($\text{AST} \rightarrow \text{NormalizationPipeline} \rightarrow \text{Segmenter V2} \rightarrow \text{RoutingWorkflow} \rightarrow \text{PolicyChunker}$) **ha sido refutado en runtime**. En su lugar, la ejecución real salta el sub-sistema de segmentación V2, cortocircuita el enrutador de traducción, ignora la fachada del pipeline de normalización y delega el empaquetado de fragmentos a clases alojadas por contaminación dentro de un módulo de infraestructura algorítmica (`core/ast/hashing.py`).

```text
==================================================================================================
                 FLUJO TEÓRICO DECLARADO PARA EL BLOQUE P3 (FALSADO)
==================================================================================================

  [FlatASTBuilder] ──► [NormalizationPipeline] ──► [Segmenter V2] ──► [RoutingWorkflow] ──► [PolicyChunker]

==================================================================================================
                 FLUJO REAL OBSERVADO EN RUNTIME (DEMOSTRADO POR CÓDIGO)
==================================================================================================

  [FlatASTBuilder.build()]
         │
         ├──► CrossPageNormalizer.execute()  <--- [DEMOSTRADO ACTIVO]
         │
         ▼
  [TranslationPipeline.execute()] (core/pipeline/orchestrator.py)
         │
         ├──► (Bypass de NormalizationPipeline)
         ├──► Invocación procedimental directa:
         │      ├── SemanticNodeClassifier().classify_batch()
         │      ├── StructuralAssetPlaceholder().normalize()
         │      ├── ASTIntegrityValidator().validate_ast()
         │      └── HierarchicalContextEnricher().enrich_document()
         │
         ├──► [BYPASS ✗] ──► Segmenter V2 (core/segmenter/*) [UNREACHABLE / ZOMBI 100%]
         ├──► [BYPASS ✗] ──► RoutingWorkflow (core/routing/*) [UNREACHABLE / ZOMBI 100%]
         │
         ▼
  [self.chunker.chunk(nodes)] (vía ChunkerProtocolAdapter / CLI)
         │
         ├──► [BYPASS ✗] ──► POO Chunker (core/chunking/chunker.py) [UNREACHABLE / ZOMBI 100%]
         │
         ▼
  [core/ast/hashing.py] <--- [CONTAMINACIÓN ONTOLÓGICA DE DOMINIO]
         │
         ├──► build_semantic_chunks_as_units()
         ├──► ContextAwareSemanticGrouper.group()
         └──► TokenBudgetChunker.chunk_group()
                     │
                     ▼
             [TranslationUnit]
```

---

## 2. RESPUESTAS FORENSES DIRECTAS DEMOSTRADAS POR CÓDIGO FUENTE

A partir del escrutinio minucioso del código fuente provisto, se responde de forma categórica a cada pregunta de investigación:

* **1. ¿Se ejecuta realmente `CrossPageNormalizer`?**
  * **Respuesta:** **SÍ [DEMOSTRADO EN CÓDIGO].**
  * **Evidencia:** En `core/ast/builder.py` (`FlatASTBuilder.build()`), el Paso 2 ejecuta explícitamente:
    `merged_nodes = CrossPageNormalizer.execute(raw_nodes)`.
    Ocurre dentro del pipeline funcional de construcción del AST V2 antes de calcular la topología.
* **2. ¿Se ejecuta realmente `Segmenter V2` (`core/segmenter/*`)?**
  * **Respuesta:** **NO [DEMOSTRADO EN CÓDIGO - ZOMBI 100%].**
  * **Evidencia:** En `core/pipeline/orchestrator.py` (`TranslationPipeline.execute()`), la lista de `nodes` generada por el parser se envía directamente a `self.chunker.chunk(nodes)`. Ninguna clase de `core/segmenter/*` (`SegmenterService`, `AtomicSegmenter`, `ParagraphSegmenter`, `ScientificBoundaryPolicy`) es importada ni invocada en la orquestación.
* **3. ¿Dónde ocurre el routing (`TRANSLATE`, `PASSTHROUGH`, `OMIT`)?**
  * **Respuesta:** **DESCONECTADO DE LA CAPA FORMAL DE ROUTING [DEMOSTRADO EN CÓDIGO].**
  * **Evidencia:** Ni `orchestrator.py` ni `pipeline_factory.py` importan `core.routing` ni `RoutingWorkflow`. El etiquetado de tareas (`TRANSLATE`, `PARTIAL`, `PRESERVE`) se realiza de forma heurística e incrustada dentro de `TokenBudgetChunker.chunk_group()` en `core/ast/hashing.py`, evaluando directamente si `node.node_type in self.protected_types`. La capa formal `core/routing/` está totalmente inactiva.
* **4. ¿Chunker recibe AST pre o post segmentación?**
  * **Respuesta:** **PRE-SEGMENTACIÓN [DEMOSTRADO EN CÓDIGO].**
  * **Evidencia:** Dado que la capa de segmentación V2 es omitida por completo, `self.chunker.chunk(nodes)` recibe la lista plana de `ASTNode`s tal como fue emitida por el parser/builder original.
* **5. ¿El chunking usa la identidad canónica y dónde reside la implementación?**
  * **Respuesta:** **RESIDE POR CONTAMINACIÓN EN `hashing.py` [DEMOSTRADO EN CÓDIGO].**
  * **Evidencia:** El chunker en runtime no es `PolicyDrivenStreamingChunker` (`core/chunking/chunker.py`), sino `TokenBudgetChunker` definido dentro de `core/ast/hashing.py`. La función `build_semantic_chunks_as_units()` en `hashing.py` llama a `ContextAwareSemanticGrouper.group(ast)` y construye `TranslationUnit` asignando el hash determinístico `det_chunk_id = f"chunk_{chunk_index:04d}_{first_seq}_{last_seq}_{short_hash}"`.
* **6. ¿Existen rutas paralelas antiguas?**
  * **Respuesta:** **SÍ, RUTA PARALELA TÓXICA ACTIVA EN EL BENCHMARK [DEMOSTRADO EN CÓDIGO].**
  * **Evidencia:** En `core/benchmark/__main__.py`, el arnés de evaluación importa y ejecuta explícitamente:
    `from core.ast.parser import parse_pdf`
    `ast_nodes = parse_pdf(str(pdf_target_path))`
    Revisando `core/ast/parser.py`, se observa que `parse_pdf()` importa `from core.ast.segmenter import MarkdownSegmenter` y procesa el texto mediante expresiones regulares de Markdown (`#`, `\begin{equation}`). El benchmark no está evaluando la ingesta canónica de producción (`PdfParserAdapter` $\rightarrow$ `PyMuPDFProvider` $\rightarrow$ `DocumentLayout` $\rightarrow$ `FlatASTBuilder`), sino un parser legacy desalineado de la Fase 11.

---

## 3. REGISTRO EXHAUSTIVO DE HALLAZGOS FORENSES (P3-H01 A P3-H05)

### P3-H01: Desconexión Total de `Segmenter V2` y `RoutingWorkflow` [DEMOSTRADO]
* **Ubicación:** `core/segmenter/*` y `core/routing/*` vs. `core/pipeline/orchestrator.py`
* **Mecanismo Causal:** El orquestador de producción pasa la secuencia de nodos AST directamente al adaptador de chunking sin subdividir párrafos densos ni enrutarlos a través de `RoutingWorkflow`.
* **Impacto ArquITECTÓNICO:** **[P0 - CRÍTICO]**. Párrafos extensos que contienen múltiples oraciones con fórmulas matemáticas no se segmentan atómicamente. Si un solo elemento dentro de un párrafo largo falla la validación en el Bloque P5, todo el bloque se rechaza, impidiendo que el motor de *Healing* actúe a nivel de oración.

---

### P3-H02: Contaminación Ontológica de Dominio en `core/ast/hashing.py` [DEMOSTRADO]
* **Ubicación:** `core/ast/hashing.py` vs. `core/chunking/chunker.py`
* **Mecanismo Causal:** 
  El sub-sistema formal de chunking orientado a objetos (`core/chunking/` con `PolicyDrivenStreamingChunker` y `StructuralNodeAtomicityPolicy`) está completamente zombi. En su lugar, la lógica de negocio de partición de texto, límites de tokens (`ChunkPolicy`), manejo de desbordamiento por oraciones (`_split_by_sentence`) e instanciación de `TranslationUnit` vive dentro de `core/ast/hashing.py`.
* **Impacto ArquITECTÓNICO:** **[P0 - CRÍTICO]**. Violación severa del Principio de Responsabilidad Única (SRP). Un módulo cuyo nombre y propósito es calcular firmas criptográficas (`compute_ast_hash`) actúa como el motor principal de empaquetado de unidades para la inferencia LLM.

---

### P3-H03: Bypass Procedimental de `NormalizationPipeline` en the Orchestrator [DEMOSTRADO]
* **Ubicación:** `core/pipeline/orchestrator.py` (`TranslationPipeline.execute()`)
* **Mecanismo Causal:** 
  `orchestrator.py` no inyecta ni invoca la fachada `NormalizationPipeline` (definida en `core/normalization/pipeline.py`). En su lugar, importa e invoca manualmente en secuencia:
  1. `SemanticNodeClassifier.classify_batch()`
  2. `StructuralAssetPlaceholder.normalize()`
  3. `ASTIntegrityValidator.validate_ast()`
  4. `HierarchicalContextEnricher.enrich_document()`
* **Impacto Arquitectónico:** **[P1 - ALTO]**. Ruptura del patrón Facade/Pipeline. El orquestador acopla de forma procedimental las etapas de normalización individual en lugar de delegar en el registro extensible de políticas (`NormalizationPolicyRegistry`), impidiendo habilitar o deshabilitar normalizadores dinámicamente.

---

### P3-H04: Viciación de Métricas en Benchmark por Uso de Parser Legacy (`parse_pdf`) [DEMOSTRADO]
* **Ubicación:** `core/benchmark/__main__.py` vs. `core/ast/parser.py`
* **Mecanismo Causal:** 
  `core/benchmark/__main__.py` ejecuta `parse_pdf()` de `core/ast/parser.py` para ingestar documentos en los experimentos de laboratorio. `parse_pdf()` utiliza `MarkdownSegmenter` para trocear el texto basándose en sintaxis de Markdown y expresiones regulares.
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. Ceguera de gobernanza. El laboratorio de evaluación científica no mide el comportamiento del pipeline real de producción (el cual ingesta mediante `PyMuPDFProvider` y `FlatASTBuilder`). Las métricas de TPS, recall topológico y densidad de tokens publicadas por el benchmark están viciadas al medir un modelo semántico obsoleto.

---

### P3-H05: Identidad Canónica Prematura por Cortocircuito de Pipeline [DEMOSTRADO]
* **Ubicación:** `core/pipeline/orchestrator.py` (Línea `current_ast_hash = compute_ast_hash(nodes)`)
* **Mecanismo Causal:** 
  `compute_ast_hash()` se invoca sobre los nodos justo después de aplicar la sustitución de placeholders de assets, pero *antes* de que el contexto sea enriquecido e hidratado en `HierarchicalContextEnricher` y antes de la fase de chunking.
* **Impacto ArquITECTÓNICO:** **[P1 - ALTO]**. Desalineación de linaje. El hash del AST sellado en el trabajo (`job.ast_hash`) no captura la estructura enriquecida de context tokens (`context_id`) ni la fragmentación de unidades que finalmente se envía al plano de control (`ControlPlaneRepository`).

---

## 4. TRAZABILIDAD Y FLUJO DE DATOS OPERACIONAL (RUNTIME VS. TEORÍA)

```text
==================================================================================================
                 TRAZABILIDAD DE TRANSFORMACIÓN SEMÁNTICA (CÓDIGO VERIFICADO)
==================================================================================================

  LayoutBlockCollection
            │
            ▼
  [FlatASTBuilder.build()]
            │
            ├──► Step 1: _map_physical_to_logical()
            ├──► Step 2: CrossPageNormalizer.execute()  <--- [EJECUCIÓN CONFIRMADA]
            └──► Step 3: _apply_topology_and_policies()
            │
            ▼
  [ASTNode Sequence (Flujo Producción)]           [pdf_target_path (Flujo Benchmark)]
            │                                                      │
            ▼                                                      ▼
  [TranslationPipeline.execute()]                         [parse_pdf() (core/ast/parser.py)]
            │                                                      │
            ├──► SemanticNodeClassifier                            ├──► MarkdownSegmenter (Regex)
            ├──► StructuralAssetPlaceholder                        └──► Nodos AST Legacy
            ├──► ASTIntegrityValidator                                     │
            └──► HierarchicalContextEnricher                               ▼
            │                                             [BENCHMARK VICIADO / NO CANÓNICO]
            ├──► [BYPASS ✗] Segmenter V2
            └──► [BYPASS ✗] RoutingWorkflow
            │
            ▼
  [self.chunker.chunk(nodes)]
            │
            ▼
  [core/ast/hashing.py :: build_semantic_chunks_as_units()] <--- [HACK EN MÓDULO DE HASHING]
            │
            ├──► ContextAwareSemanticGrouper.group()
            └──► TokenBudgetChunker.chunk_group()
                     │
                     ▼
             [TranslationUnit Sequence]
```

---

## 5. MATRIZ TAXONÓMICA DE RIESGO Y DISPOSICIÓN PARA EL HITO 0.5

| Componente / Módulo | Categoría Arquitectónica | Severidad | Diagnóstico Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `core/ast/builder.py` | AST Construction | **Cero** | Invoca limpiamente `CrossPageNormalizer` y calcula topología. | **CONSERVAR** |
| `core/segmenter/*` | Segmenter V2 | **P0 (Crítico)** | $100\%$ zombi. Omitido en `orchestrator.py` y `pipeline_factory.py`. | **ENLAZAR EN PIPELINE** |
| `core/routing/*` | Routing Engine | **P0 (Crítico)** | $100\%$ zombi. Sin filtrado de canales (`PASSTHROUGH`/`OMIT`). | **ENLAZAR EN PIPELINE** |
| `core/chunking/*` | POO Chunker | **P0 (Crítico)** | $100\%$ zombi. Bypasseado a favor de funciones en `hashing.py`. | **RESTAURAR Y USAR** |
| `core/ast/hashing.py` | Hash Utils | **P0 (Crítico)** | Contaminado con lógica de dominio (`TokenBudgetChunker`). | **PURGAR LÓGICA CHUNKER** |
| `core/ast/parser.py` | Legacy Parser | **P0 (Crítico)** | Utilizado por `core/benchmark/__main__.py` viciando métricas. | **DEPRECAR / ELIMINAR** |
| `core/pipeline/orchestrator.py` | Orchestration | **P1 (Alto)** | Bypassea `NormalizationPipeline` invocando clases a mano. | **REFACTORIZAR A FACADE** |

---

## 6. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P3-R01 A P3-R05)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P3-R01 (Conexión Mandatoria de `Segmenter V2` - P0):** Modificar `TranslationPipeline.execute()` en `core/pipeline/orchestrator.py` para intercalar `SegmenterService` entre la normalización y el chunking, garantizando la partición oracional de párrafos densos mediante `ScientificBoundaryPolicy`.
* **P3-R02 (Purgado de Contaminación en `core/ast/hashing.py` - P0):** Eliminar la clase `TokenBudgetChunker`, la configuración `ChunkPolicy` y la función `build_semantic_chunks_as_units()` de `core/ast/hashing.py`. Reubicar esta responsabilidad exclusivamente dentro de `core/chunking/` respetando el contrato `ASTChunker`.
* **P3-R03 (Sanación de Ingesta en Benchmark - P0):** Refactorizar `core/benchmark/__main__.py` para eliminar la llamada a `parse_pdf()` de `core/ast/parser.py`. El benchmark debe instanciar `PdfParserAdapter` con `PyMuPDFProvider` y `FlatASTBuilder` para garantizar que las mediciones evalúen el pipeline de producción real.
* **P3-R04 (Activación de Canales de `RoutingWorkflow` - P1):** Conectar `RoutingWorkflow` (`core/pipeline/workflow.py`) en el orquestador para filtrar los nodos con estrategia `PASSTHROUGH` u `OMIT` antes de enviarlos a la cola de despacho LLM (Bloque P4).
* **P3-R05 (Encapsulamiento en `NormalizationPipeline` - P1):** Agrupar las invocaciones procedimentales de `SemanticNodeClassifier`, `StructuralAssetPlaceholder` y `HierarchicalContextEnricher` dentro del contenedor `NormalizationPipeline`, eliminando la manipulación directa de nodos dentro de `TranslationPipeline.execute()`.

---

## 7. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 7.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Materialización del AST V2:** **EXCEPCIONAL Y CORRECTA.** `FlatASTBuilder.build()` integra adecuadamente la sutura trans-página (`CrossPageNormalizer`) y el cálculo topológico $O(N)$.
2. **Transformación Semántica y Segmentación:** **GRAVEMENTE FRACTURADA.** El pipeline real omite la segmentación, ignora el enrutamiento, hospeda el chunker dentro del módulo de hashing criptográfico y evalúa el benchmark sobre una ruta legacy desalineada de producción.

---

### 7.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P3

The audit for **Block P3 (AST Transformations, Normalization, Segmenter V2, Routing & Chunking)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P3 (RECTIFICADO)
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Confirmada por Código Fuente)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Segmenter V2, Router y POO Chunker zombis; Benchmark viciado)
  Remediation Backlog      | OPEN (Reglas P3-R01 a P3-R05 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría forense rectificada del Bloque P3 tras la verificación directa del código fuente. Se demostró que CrossPageNormalizer está activo en FlatASTBuilder. Sin embargo, se confirma la orfandad total del Segmenter V2, del RoutingWorkflow y del sub-sistema formal core/chunking. La lógica de empaquetado de unidades vive por contaminación en core/ast/hashing.py. Se constató además la presencia de una ruta tóxica activa en el Benchmark (core/benchmark/__main__.py usando core/ast/parser.py), lo que invalida las mediciones del laboratorio respecto al comportamiento de producción. Queda estrictamente prohibido mutar código. Todas las reglas de remediación quedan congeladas para el Hito 0.5."*