# ROADMAP_FASE_16.md

# FASE 16 — ESTRUCTURA DOCUMENTAL SOTA

## Objetivo Principal
Transformar el pipeline de un procesador de texto plano heurístico a un procesador de documentos estructurados matemáticamente predecible y tipado.

## Reglas de la Fase
* **No benchmark:** La prioridad es la exactitud topológica, no la velocidad.
* **No optimización prematura:** El diseño prima sobre micro-optimizaciones.
* **Cero ML nativo en el core:** Las decisiones estructurales se toman con heurísticas de estado finito u $O(1)$.
* **Inmutabilidad estricta:** Los DTOs no mutan; se transicionan a nuevos estados copiando la instancia.

---

## El Pipeline Definitivo (Flujo de Datos)
`PDF -> ExtractionProvider -> LayoutDocument -> AST V2 (Plano) -> Segmenter V2 -> Atomic Chunking -> Passthrough Router -> Validation -> Translation -> Layout Compiler -> PDF Final`

---

## Desglose de Fases

### FASE 16.0 — Parser Abstraction Layer [COMPLETADA]
* **Objetivo:** Desacoplar el core del motor de extracción subyacente.
* **Mecanismo:** Inyección de un `ExtractionProvider` (ej. PyMuPDF, Marker, Docling) que estandariza la salida física hacia un `LayoutDocument`.

### FASE 16.1 — Layout Recovery [COMPLETADA]
* **Objetivo:** Retener la geometría física antes de la interpretación semántica.
* **Mecanismo:** Pipeline de 5 etapas (Normalizer, Classifier, Merger, Detector, Reading Order) que opera sobre `LayoutBlock`.
* **Invariante:** Proveer obligatoriamente `bbox`, `page_index` y `semantic_origin`.

### FASE 16.2 — AST V2 (Flat AST & Orchestration) [COMPLETADA]
* **Objetivo:** Transmutación de coordenadas físicas a una secuencia lógica semántica unidimensional $O(n)$.
* **Componentes SOTA:**
  * **PayloadRegistry:** Instanciación OCP-compliant de DTOs polimórficos (`ParagraphPayload`, `MathPayload`, etc.).
  * **CrossPageNormalizer:** Sutura determinística de fragmentos partidos por saltos de página con *de-hyphenation* conservador.
  * **StrategyResolver:** Función pura $O(1)$ que mapea la topología a un `TranslationStrategy` (`TRANSLATE`, `PASSTHROUGH`, `OMIT`).
  * **FlatASTBuilder:** Ensamblador basado en Pila Topológica para el cálculo del `depth` sin generar anidamiento de árboles.

### FASE 16.3 — Segmenter V2 (Desambiguación Oracional) [EN PROCESO]
* **Objetivo:** Refinamiento granular de nodos masivos a oraciones lógicas sin romper referencias espaciales.
* **Mecanismo:** Arquitectura Hexagonal basada en `Protocols`. El AST es evaluado por un `SegmentDispatcher` que aplica `ScientificBoundaryPolicy` estrictamente sobre nodos textuales.
* **Regla de Oro:** Cero destrucción de estructuras atómicas (`DISPLAY_EQUATION`, `CODE`, `TABLE_COMPLEX`).

### FASE 16.4 — Passthrough Router
* **Objetivo:** FinOps y preservación de formato crudo. No gastar tokens en inferencias inútiles.
* **Mecanismo:** Intercepción en `core/pipeline/orchestrator.py`. Si `strategy == PASSTHROUGH`, el nodo evade la llamada a la red (Groq/Gemini/OpenAI) y se inyecta directamente al Repositorio como `COMPLETED`.

### FASE 16.5 — Atomic Chunking
* **Objetivo:** Optimización de I/O de red empaquetando el contexto sin corromper la semántica.
* **Mecanismo:** Algoritmo $N \to 1$. Agrupa fragmentos respetando el umbral de tokens. Si un nodo es atómico (ej. bloque de código gigante), jamás se corta, garantizando su integridad estructural para el compilador final.

### FASE 16.6 — Validation Polymorphism
* **Objetivo:** Auditoría de calidad asimétrica.
* **Mecanismo:** Un `Paragraph` pasa por un `SemanticValidator`; una `Equation` por un `EquationValidator`; un `PASSTHROUGH` se somete a validación de hash de integridad.

### FASE 16.7 — Document Profile
* **Objetivo:** Extracción de metadatos geométricos globales para la reconstrucción.
* **Mecanismo:** Detección de `single_column` vs `double_column`, orientación y tipo de documento (paper, book) para gobernar las decisiones del ensamblador final.

### FASE 16.8 — Layout Compiler
* **Objetivo:** Ensamblado tipográfico de alta fidelidad.
* **Mecanismo:** Transformación del AST traducido de vuelta a un formato visualizable usando el `DocumentProfile` para mantener la coherencia espacial de tablas y figuras.

### FASE 16.9 — Prompt System SOTA
* **Objetivo:** Comunicación determinista con LLMs.
* **Mecanismo:** Eliminación de prompts en *string*. Inyección de payloads estructurados JSON (`constraints`, `context`, `payload`) validados bidireccionalmente por Pydantic (Structured Outputs).