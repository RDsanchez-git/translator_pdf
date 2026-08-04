# ADR F17.3: Capa de Integración Canónica de Extracción y Aislamiento de Runtime

## 1. Objetivo y Contexto
La Fase 17.2 consolidó el motor de evaluación topológica y estableció la línea base física de PyMuPDF ($0.8190$). Para evaluar e integrar extractores del Estado del Arte (SOTA) como Marker, Docling y Nougat, el sistema requiere una infraestructura de integración que resuelva dos problemas fundamentales:
1. **Incompatibilidad de Runtime:** Dependencias masivas de Deep Learning (PyTorch, CUDA, Transformers) que provocan colisiones de versiones (*Dependency Hell*) con el núcleo ligero del sistema.
2. **Heterogeneidad de Formatos:** Cada herramienta emite estructuras propietarias (Markdown, JSON propietario, diccionarios nativos).

La Fase 17.3 establece la **Capa de Integración Canónica de Extracción**, permitiendo conectar cualquier motor mediante procesos aislados y convertir sus salidas a la representación de dominio `DocumentLayout` sin contaminar el entorno ni alterar la canalización de construcción del AST.

---

## 2. Decisiones Arquitectónicas

### 2.1 Reutilización del Contrato Unificado (`ExtractionProvider`)
No se crearán protocolos paralelos de adaptación ni namespaces superfluos (`core/extraction/adapters/`). Todo proveedor de extracción (PyMuPDF, Marker, Docling) implementará **única y exclusivamente** la interfaz canónica existente en `core/extraction/provider.py`: `ExtractionProvider` con el método `extract(pdf_path: str) -> DocumentLayout`[cite: 1]. Hacia el dominio principal, Marker y Docling son simplemente otros *Providers* de extracción.

### 2.2 Principio de Intercambiabilidad y Representación Canónica
Todo motor de extracción debe ser sustituible por otro sin modificar una sola línea del pipeline posterior. Queda strictly prohibido que un proveedor produzca un Árbol de Sintaxis Abstracta (`ASTNode`) de forma directa. La única frontera pública válida es el *Aggregate Root* `DocumentLayout`. La construcción del AST V2 se delega de forma universal y determinista al `FlatASTBuilder` existente[cite: 1].

Flujo del pipeline de extracción:
1. **Documento PDF** es enviado al **MarkerProvider**.
2. **MarkerProvider** invoca la CLI aislada vía **ExternalProcessRunner** para producir `.md` / `.json` crudo.
3. El parseador interno convierte dicho resultado a **DocumentLayout**.
4. **DocumentLayoutValidator** valida las invariantes de maquetación.
5. **FlatASTBuilder** construye de forma determinista el **AST V2**.

### 2.3 Orquestación Encapsulada y Ubicación de Infraestructura (`ExternalProcessRunner`)
Para garantizar la cohesión del contrato `extract(pdf_path: str)`, el `ExtractionProvider` de un motor externo orquestará internamente el proceso completo de punta a punta (invocación del proceso aislado + traducción de la salida cruda). 
El componente encargado de ejecutar CLI de bajo nivel (`ExternalProcessRunner`) es **infraestructura genérica**, no perteneciente ni al dominio principal ni exclusivamente al benchmark. Se ubicará en `infra/execution/process_runner.py` para poder ser reutilizado en producción por otros componentes del sistema (p. ej. `tectonic`, `latexmk`, `pandoc`)[cite: 1].

### 2.4 Validación Rigurosa de Invariantes (`DocumentLayoutValidator`)
No se confiará únicamente en la validación de tipos de Pydantic. Antes de pasar un `DocumentLayout` al `FlatASTBuilder`, se ejecutará un paso explícito de validación de invariantes de maquetación:
* Bounding boxes válidos dentro de márgenes físicos.
* Índices de página coherentes ($\ge 1$).
* Unicidad de `block_id`.
* Grafo de orden de lectura (*Reading Order*) acíclico.

### 2.5 Determinismo y Neutralidad Absoluta del Provider
Todo proveedor debe ser $100\%$ determinista. Queda prohibida la inclusión de heurísticas variables, inferencias probabilísticas o postprocesamiento dinámico en la capa de adaptación. El proveedor debe mapear con absoluta fidelidad la salida del parser original. Si el parser no emite coordenadas espaciales, la ausencia se representará explícitamente como `None`. Queda prohibida la invención de coordenadas ficticias.

### 2.6 Metadata de Doble Capa y Trazabilidad Criptográfica
Todo candidato generado registrará obligatoriamente los siguientes metadatos de trazabilidad:
* `input_pdf_sha256`: Hash criptográfico del documento fuente.
* `parser_name`: Identificador del motor (ej. `marker`).
* `parser_version`: Versión exacta de la CLI/paquete aislado (ej. `marker-pdf==0.9.1`).
* `adapter_version`: Versión del traductor interno a `DocumentLayout` (ej. `v1.0.0`).
* `model_name`: Modelo o pesos utilizados.
* `commit_hash`: Estado del código del repositorio.
* `execution_timestamp`: Marca temporal UTC de generación.

### 2.7 Generación CLI Unificada y Offline Benchmark Execution
Se erradica la creación de scripts aislados por cada parser (`generate_marker_candidate.py`, `generate_docling_candidate.py`). Se implementará una herramienta CLI parametrizada e integrada `tools/evaluation/generate_candidates.py --provider <name>` que ejecutará el *UseCase* canónico de generación. La evaluación topológica consumirá únicamente artefactos estáticos persistidos en `candidates/<parser_name>/<doc_id>.json`.

---

## 3. Plan de Ejecución (Hitos)

### Hito 1: Infraestructura de Ejecución e Integración Base
* **Objetivo:** Implementar el motor de subprocesos aislados `ExternalProcessRunner` en infraestructura y la herramienta unificada de candidatos.
* **Entregables:**
  * Implementación de `ExternalProcessRunner` en `infra/execution/process_runner.py` con gestión de *timeouts*, aislamiento CLI y logs de auditoría[cite: 1].
  * Implementación de `DocumentLayoutValidator` para asegurar el cumplimiento de invariantes físicas antes del `FlatASTBuilder`[cite: 1].
  * Unificación del script CLI `tools/evaluation/generate_candidates.py` soportando el flag `--provider`.
  * Validación de la canalización de referencia con `PyMuPDFProvider`[cite: 1].

### Hito 2: Validación de la Capacidad Multi-Provider y Baseline de Referencia

#### Hito 2A: Consolidación de Arquitectura Multi-Provider y Reference Provider (Baseline)
* **Objetivo:** Consolidar `PyMuPDFProvider` como el *Reference Provider (Baseline)* para desarrollo, pruebas automatizadas y benchmarking debido a su bajo costo computacional, comportamiento determinista y compatibilidad con el entorno de desarrollo actual. Validar la capacidad de la plataforma para orquestar candidatos AST V2 sin acoplamiento a motores OCR específicos ni fricción de hardware.
* **Entregables:**
  * **Adopción del Reference Provider (Baseline):** Adoptar `PyMuPDFProvider` como estándar de contraste inicial sin restringir la integración futura de extractores especializados (Marker, MinerU, Docling).
  * **Generación Canónica de Baseline:** Ejecución y depósito de candidatos (`.json` y `.meta.json`) en `candidates/pymupdf/` mediante `python -m tools.evaluation.generate_candidates --provider pymupdf` sobre el corpus `calibration_v1`.
  * **Verificación de Contrato End-to-End:** Confirmación del flujo desacoplado entre capas:
    `ExtractionProvider` → `DocumentLayout` → `DocumentLayoutValidator` → `FlatASTBuilder` → `AST V2`.

#### Hito 2B: Integración de Proveedores Alternativos (Diferida / Bajo Demanda)
* **Objetivo:** Incorporar adaptadores de extracción secundarios únicamente ante una necesidad funcional demostrada (ej. PDFs escaneados) o disponibilidad de hardware con mayor VRAM.
* **Entregables:**
  * **Spike de Viabilidad Técnica:** Evaluación previa de impacto en CPU, RAM y VRAM antes de introducir dependencias adicionales.
  * **Adaptador de Extracción Dedicado:** Construcción del nuevo `ExtractionProvider` (ej. `DoclingProvider` o `MarkerProvider`) respetando la interfaz pura.
  * **Evaluación Comparativa en Benchmark:** Generación de candidatos paralela para medición de métricas (TED, preservación de fórmulas, tablas y orden de lectura) frente al Baseline.

### Hito 3: Motor Algorítmico de Similaridad Estructural (PR 2B)
* **Objetivo:** Implementar la métrica de Tree Edit Distance (TED / APTED) para evaluar formalmente la fidelidad de la jerarquía y estructura del árbol AST V2 candidato frente al Ground Truth de calibración.
* **Entregables:**
  * **ADR de Evaluación Estructural:** Formalización del algoritmo seleccionado (ej. APTED), matriz de costos de operaciones de edición (inserción, supresión, reemplazo) y normalización escalar $[0, 1]$.
  * **Implementación de `StructuralTopologyMetric`:** Desarrollo del algoritmo en `tools/evaluation/topology/metrics/structural.py` e integración directa a `default_metrics()`.
  * **Suite de Pruebas y Calibración:** Tests unitarios sobre árboles sintéticos con deformaciones conocidas y validación sobre la suite `calibration_v1`.

### Hito 4: Integración de Proveedores Secundarios (Spike & Multi-Provider)
* **Objetivo:** Incorporar adaptadores de extracción secundarios especializados (ej. Docling, Marker o MinerU) sobre la infraestructura de aislamiento para habilitar la comparación multi-proveedor.
* **Entregables:**
  * **Spike de Viabilidad Técnica:** Evaluación de consumo de recursos (RAM/VRAM), tiempo de inferencia y dependencias antes de la integración.
  * **Adaptador de Extracción Secundario:** Construcción de `DoclingProvider` (o equivalente) en `core/extraction/ocr_providers/` respetando el contrato puro `ExtractionProvider`.
  * **Generación Canónica de Candidatos:** Ejecución del pipeline y depósito de candidatos AST V2 en `candidates/docling/` para el corpus `calibration_v1`.

### Hito 5: Torneo de Extractores y Reporte de Significancia Científica (Torneo SOTA)
* **Objetivo:** Someter a todos los proveedores (Baseline PyMuPDF vs Proveedores Secundarios) al evaluador topológico completo para seleccionar empíricamente al motor de extracción definitivo del pipeline.
* **Entregables:**
  * **Ejecución del Benchmark Multi-Provider:** Ejecución del CLI `run_benchmark.py` sobre todos los proveedores de la suite `calibration_v1`.
  * **Emisión del `ScientificSignificanceReport`:** Generación de los reportes consolidados (Markdown/JSON) con evidencia cuantitativa (NodeCount, Recall, SequenceAlignment, TED) que determine al extractor oficial del sistema.



## RESULTADOS CONSOLIDADOS FASE 17.3 

### 1. Implementación de la Infraestructura y Contratos del Subdominio: `tools/evaluation/` y `core/layout/` (Hito 1)
* **Causa Raíz:** Riesgo de acoplamiento aferente inverso al obligar al orquestador y al benchmark a conocer los detalles de ejecución CLI de motores de extracción externos. Propensión al acoplamiento de infraestructura por mezcla de serialización JSON dentro de servicios de aplicación, mutabilidad de DTOs y falta de un validador de invariantes físicas previa a la construcción del AST V2.
* **Correcciones Aplicadas:**
  * **`tools/evaluation/execution/` (PR 1):** Despliegue de `ExternalProcessRunner` para la invocación aislada de procesos secundarios CLI. Captura inmutable de artefactos (`tuple[Path, ...]`), manejo de timeouts, captura de STDERR/STDOUT y lanzamiento de excepciones de dominio tipadas (`ProcessTimeoutError`, `ProcessExecutionError`).
  * **Auditoría de Contratos (PR 2):** Verificación formal y congelamiento de contratos de extracción (`ExtractionProvider`) y construcción AST (`FlatASTBuilder`) sin sobreingeniería (YAGNI).
  * **`core/layout/validator.py` (PR 3):** Implementación de `DocumentLayoutValidator` para la auditoría de invariantes de maquetación (páginas vacías, secuencias no monótonas, colisión de `BlockId` y BoundingBoxes inválidos). Respeto al principio de neutralidad (`bbox=None` es válido) y emisión inmutable de `LayoutValidationReport` sin lanzar excepciones en el flujo principal.
  * **`tools/evaluation/services/` y `generate_candidates.py` (PR 4):** Arquitectura Hexagonal pura (CLI → Application Service → Domain). `CandidateGenerationService` orquesta el pipeline entregando `tuple[ASTNode, ...]` puras, mientras que el CLI asume la responsabilidad de serialización e I/O, incorporando métricas operacionales (`processed`, `accepted`, `rejected`) y registro local de proveedores.
  * **`core/domain/document.py`:** Ajuste del tipo `bbox` en `LayoutBlock` a `Optional[BoundingBox]` para permitir proveedores neutrales sin coordenadas espaciales.
* **Métrica del Compilador:** `pyright tools/evaluation/services/candidate_generator.py tools/evaluation/generate_candidates.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/test_layout_validator.py` → **8/8 PASSED**.


### 2. Consolidación de Arquitectura Multi-Provider y Baseline de Referencia (Hito 2)
* **Causa Raíz:** Riesgo de acoplamiento prematuro a motores de extracción de Deep Learning pesados (Marker, MinerU) sin considerar las restricciones físicas del hardware de desarrollo (16 GB RAM / 4 GB VRAM), lo que habría introducido complejidad operativa masiva, dependencias pesadas de PyTorch/CUDA y fricción en CI sin aportar valor al contrato del dominio (`DocumentLayout`).
* **Correcciones Aplicadas:**
  * **Redefinición Estratégica del Hito (Hito 2A / Hito 2B):** Reestructuración del hito para priorizar la validación de la capacidad multi-proveedor del pipeline y del contrato de abstracción sobre la selección de un motor OCR específico, aplicando de forma estricta el principio YAGNI.
  * **Adopción del Reference Provider (Baseline - Hito 2A):** Formalización de `PyMuPDFProvider` como el proveedor de referencia canónico para desarrollo, ejecución local, pruebas automatizadas y benchmarking debido a su comportamiento determinista, costo computacional nulo y velocidad de ejecución sub-segundo.
  * **Generación y Depósito Canónico de Candidatos:** Ejecución e integración fluida del pipeline sobre la suite de calibración `calibration_v1` (`doc_01_single` a `doc_05_graph`), generando los artefactos AST V2 (`.json`) y su telemetría sidecar (`.meta.json`) en `candidates/pymupdf/`.
  * **Diferimiento de Proveedores Secundarios (Hito 2B):** Aplazamiento bajo demanda de la integración de adaptadores pesados (Marker, MinerU, Docling) hasta que exista un caso de uso funcional justificado (ej. PDFs escaneados) o disponibilidad de hardware dedicado con mayor VRAM, manteniendo la neutralidad del dominio.
* **Métrica del Compilador:** `pyright tools/evaluation/services/candidate_generator.py tools/evaluation/generate_candidates.py` → **0 errors, 0 warnings**.
* **Métrica de Cobertura de Corpus:** `generate_candidates --provider pymupdf` → **5/5 candidatos generados y validados (0 rechazados)** sobre `calibration_v1`.

### 2A. Consolidación de Arquitectura Multi-Provider y Reference Provider (Hito 2A)
* **Causa Raíz:** Riesgo de acoplamiento prematuro a motores de extracción de Deep Learning pesados (Marker, MinerU, Docling) sin considerar las restricciones físicas del hardware de desarrollo (16 GB RAM / 4 GB VRAM), lo que habría introducido complejidad operativa masiva, dependencias pesadas de PyTorch/CUDA y fricción en CI sin aportar valor al contrato del dominio (`DocumentLayout`).
* **Correcciones Aplicadas:**
  * **Adopción del Reference Provider (Baseline):** Formalización de `PyMuPDFProvider` como el proveedor de referencia canónico para desarrollo, ejecución local, pruebas automatizadas y benchmarking debido a su comportamiento determinista, costo computacional nulo y velocidad de ejecución sub-segundo.
  * **Generación y Depósito Canónico de Candidatos:** Ejecución e integración fluida del pipeline sobre la suite de calibración `calibration_v1` (`doc_01_single` a `doc_05_graph`), generando y depositando los artefactos AST V2 (`.json`) y su telemetría sidecar (`.meta.json`) en `candidates/pymupdf/`.
  * **Verificación de Contrato End-to-End:** Validación experimental y confirmación del flujo completamente desacoplado entre capas:
    `ExtractionProvider` → `DocumentLayout` → `DocumentLayoutValidator` → `FlatASTBuilder` → `AST V2`.
* **Métrica del Compilador:** `pyright tools/evaluation/services/candidate_generator.py tools/evaluation/generate_candidates.py` → **0 errors, 0 warnings**.
* **Métrica de Cobertura de Corpus:** `generate_candidates --provider pymupdf` → **5/5 candidatos generados y validados (0 rechazados)** sobre `calibration_v1`.


### 2B. Integración de Proveedores Alternativos (Hito 2B)
* **Causa Raíz:** Riesgo de sobreingeniería, acoplamiento prematuro y degradación del entorno local por la introducción de adaptadores de extracción basados en modelos pesados de Deep Learning (Marker, MinerU, Docling), con alto consumo de VRAM (> 4 GB) y dependencias complejas de PyTorch/CUDA sin justificación funcional en el baseline.
* **Correcciones Aplicadas:**
  * **Diferimiento Estratégico Bajo Demanda:** Formalización del aplazamiento de adaptadores secundarios hasta contar con casos de uso críticos (ej. PDFs escaneados) o disponibilidad de hardware dedicado, aplicando de forma estricta el principio YAGNI.
  * **Preservación de la Interfaz Pura:** Garantía de que el contrato `ExtractionProvider` permanece totalmente desacoplado, permitiendo la adición futura de nuevos adaptadores sin modificar el dominio ni la infraestructura existente.
  * **Protocolo de Spike de Viabilidad:** Definición de métricas de viabilidad técnica (consumo de RAM/VRAM, aislamiento de proceso y latencia sub-segunda) como prerrequisito obligatorio antes de cualquier integración en la suite principal.
* **Métrica de Arquitectura:** Contrato `ExtractionProvider` desacoplado al **100%** de motores OCR específicos.
* **Estado del Módulo:** **Diferido / Listo para integración bajo demanda** (sin impacto en la velocidad del baseline de producción).

---

### 3. Motor Algorítmico de Similaridad Estructural - PR 2B (Hito 3)
* **Causa Raíz:** Incapacidad de las métricas lineales (`EntityRecall` y `SequenceAlignment`) para evaluar formalmente la fidelidad de la jerarquía profunda y las relaciones padre-hijo del árbol AST V2 candidato frente al Ground Truth.
* **Correcciones Aplicadas:**
  * **Implementación de `StructuralTopologyMetric` y APTED:** Desarrollo de la métrica topológica basada en Tree Edit Distance (TED) en `tools/evaluation/topology/metrics/structural.py`, integrando `CustomAPTEDConfig` alineado inmutablemente con la matriz de costos del **ADR 0017** (`delete=1.0`, `insert=1.0`, `rename_same_type=0.5`, `rename_diff_type=2.0`).
  * **Fingerprint Semántico Estricto:** Integración de `ASTFingerprintPolicy.semantic_fingerprint()` para extraer explícitamente la tupla `(node_type, text_content)`, garantizando la penalización diferencial de renombres según tipo y contenido.
  * **Construcción Eficiente del Árbol ($O(N)$):** Reconstrucción del mapa de adyacencia indexando `parent_node_id` y envolviendo los subárboles en una raíz virtual `Document`, asegurando el desempaquetado de argumentos posicionales (`*children_trees`) para la librería `apted`.
  * **Robustez de Infraestructura y Deserialización:** Corrección de la serialización atómica en Windows mediante `Path.replace()` en `infra/serialization/ast_json.py` y manejo polimórfico `dict`/`list` en `ASTJsonDeserializer`.
  * **Integración Global y Verificación Empírica:** Registro explícito en `default_metrics()` y verificación matemática en el benchmark sobre `calibration_v1`, confirmando que la paridad exacta de score con `sequence` (`0.6380`) responde con precisión a la topología plana del Ground Truth actual (`parent_node_id: {None}`).
* **Métrica de Tests Unitarios:** `python -m pytest tests/unit/test_structural_metric.py` → **7/7 passed in 0.21s**.
* **Métrica del Benchmark de Calibración:** `python -m tools.evaluation.run_benchmark --provider pymupdf --corpus calibration_v1` → **5/5 documentos evaluados exitosamente** (`node_count: 1.0000`, `recall: 0.6380`, `sequence: 0.6380`, `structural: 0.6380`).

### 4. Integración de Proveedores Secundarios - Docling Extraction Adapter (Hito 4)
* **Causa Raíz:** Necesidad de integrar motores de extracción SOTA alternativos (ej. Docling) capaces de reconocer layouts complejos, tablas y expresiones matemáticas, manteniendo la arquitectura hexagonal y sin acoplar el dominio AST V2.
* **Correcciones Aplicadas:**
  * **Implementación de `DoclingProvider`:** Desarrollo del adaptador inmutable en `core/extraction/ocr_providers/docling_provider.py` cumpliendo con el contrato `ExtractionProvider` y declarando explícitamente sus capacidades físicas `ExtractionCapabilities`.
  * **Mapeo Lógico de Etiquetas Docling:** Implementación de `_LABEL_MAPPING` para la traducción de enums `DocItemLabel` nativas hacia `LayoutBlockType` (títulos, listas, tablas, fórmulas, notas al pie, encabezados).
  * **Manejo de Proveniencia y Geometría:** Extracción de coordenadas bounding box y páginas desde los metadatos `prov` de Docling con saneamiento de dimensiones y límites (`x1 > x0`, `y1 > y0`).
  * **Generación Canónica de Candidatos:** Despliegue de la herramienta `generate_candidates.py` para procesar y depositar candidatos AST V2 y metadatos sidecar en `tests/corpus/calibration_v1/candidates/docling/`.
  * **Registro de Deuda Técnica (Known Mapping Gaps / AST Fallbacks):** Documentación explícita de etiquetas no mapeadas en la capa de adaptador (`picture`, `chart`, `marker`) y de los fallbacks semánticos hacia `ParagraphPayload` mediante la regla `[AST-004]` del `FlatASTBuilder` (`DISPLAY_EQUATION`, `TABLE_SIMPLE`, `SECTION`, `LIST_ITEM`, `CAPTION`, `FOOTNOTE`).
* **Métrica de Tests Unitarios:** `python -m pytest tests/unit/test_docling_provider.py` → **3/3 passed in 7.05s**.
* **Métrica de Generación de Candidatos:** `python -m tools.evaluation.generate_candidates --provider docling --corpus tests/corpus/calibration_v1/pdf` → **5/5 documentos procesados exitosamente** (`Procesados=5 | Aceptados=5 | Rechazados=0`).

### 5. Torneo de Extractores y Reporte Comparativo Multi-Proveedor (Hito 5)
* **Causa Raíz:** Ausencia de un entorno de laboratorio para comparar empíricamente la fidelidad topológica ($TED$) y rendimiento operacional entre múltiples proveedores (`PyMuPDF` vs `Docling`) sobre la suite `calibration_v1`.
* **Correcciones Aplicadas:**
  * **Despliegue del Runner Comparativo Experimental:** Utilización del runner desacoplado `tools/evaluation/run_experimental_benchmark.py` que consume exclusivamente candidatos pre-generados en `candidates/` contra el Ground Truth, garantizando cero costo de re-extracción física durante la evaluación.
  * **Consolidación del Leaderboard Topológico:** Evaluación cruzada sobre los 5 documentos del corpus `calibration_v1`, registrando scores promedios de similaridad estructural ($TED$/APTED): `PyMuPDF` = **0.8190**, `Docling` = **0.3271**.
  * **Validación del Aislamiento Hexagonal:** Demostración empírica de que el pipeline de evaluación (`TopologyBenchmarkService`) es completamente agnóstico al motor físico subyacente y sensible a la preservación de estructura end-to-end.
  * **Análisis Descriptivo de Latencia y Sensibilidad de Pipeline:** Registro descriptivo de latencias promedio de evaluación (`PyMuPDF`: 48.12 ms vs `Docling`: 20.56 ms) e identificación de la causa principal en la diferencia de puntuaciones: los fallbacks semánticos a `PARAGRAPH` y variaciones de granularidad de segmentación.
  * **Consolidación de Evidencia en ADR 0017:** Actualización formal de la Sección 7 del ADR 0017 integrando la tabla comparativa multi-proveedor, el registro de deudas de mapeo y la preservación del histórico de calibración.
* **Métrica del Benchmark Multi-Proveedor:** `python -m tools.evaluation.run_experimental_benchmark --corpus tests/corpus/calibration_v1` → **5/5 documentos evaluados y comparados exitosamente** (`PyMuPDF Avg Score: 0.8190`, `Docling Avg Score: 0.3271`).