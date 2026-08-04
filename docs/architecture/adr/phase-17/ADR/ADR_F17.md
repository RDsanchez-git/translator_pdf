# HOJA DE RUTA DE ARQUITECTURA (ADRs) - FASE 17
**Iniciativa:** Evaluation Framework & Parser Selection
**Objetivo:** Adaptar el framework de benchmarking existente para evaluar, medir y seleccionar científicamente el motor SOTA de extracción documental (Computer Vision / OCR) que alimentará el `AST V2`.

---

### ADR F17.0: Benchmark Corpus (Selección Documental)
* **Objetivo:** Definir el espacio muestral estático, determinista y representativo que servirá como base empírica para todos los experimentos del ciclo de vida del traductor.
* **Entregables:**
  * Taxonomía del corpus: Selección de PDFs categorizados por desafío estructural (papers a doble columna, libros de Springer, artículos de econometría/física con alta densidad de `DISPLAY_EQUATION`, documentos con `TABLE_COMPLEX`).
  * Estructura de almacenamiento en el repositorio (ej. `tests/corpus/benchmark_v1/`).
* **Desafío Arquitectónico:** Evitar el sobreajuste (*overfitting*). El corpus debe incluir documentos limpios nativos digitales y documentos ruidosos (scans).

### ADR F17.1: Scientific Ground Truth (Golden AST)
* **Objetivo:** Definir el esquema canónico de "la verdad absoluta" contra la cual se calcularán las distancias y los deltas de pérdida de los parsers candidatos.
* **Entregables:**
  * Estructura de representación del `Golden AST Schema Version` (JSON serializado de la topología ideal), por ejemplo golden_ast/v1, golden_ast/v2. Porque el AST V2 del proyecto seguirá evolucionando y para no invalidar todo el benchmark cuando aparezca un AST V3.
  * Metodología de *Bootstrapping*: Herramienta CLI o *script* para generar el primer borrador del AST y facilitar la corrección/auditoría manual antes de congelarlo.
* **Desafío Arquitectónico:** Aislar el *Ground Truth* de la varianza estocástica del OCR (BBoxes flotantes). La aserción debe basarse en la jerarquía, el `ContentNodeType` y la semántica, no en coordenadas exactas en milímetros.

### ADR F17.2: Métricas Topológicas y Evaluadores (Los Jueces)
* **Objetivo:** Definir la matemática pura de la evaluación estructural, migrando el foco del framework actual (diseñado para evaluar texto generativo de LLMs) hacia la geometría y la fidelidad del árbol documental.
* **Entregables:**
  * Implementación de métricas de recuperación: `EquationRecall`, `TableRecall`.
  * Implementación de métricas de distancia: *Tree Edit Distance* (TED) utilizando algoritmos polinómicos ($O(n^3)$ como Zhang-Shasha/APTED), aplicando partición por subgrafos (ej. comparar página por página) para evitar la explosión de tiempo de cómputo en documentos largos.
* **Desafío Arquitectónico:** Diseñar evaluadores puros, desacoplados del orquestador, que implementen una interfaz estándar consumible por el `SequentialBenchmarkOrchestrator`.

### ADR F17.3: Benchmark Extraction Adapters & Aislamiento de Dependencias
* **Objetivo:** Establecer el contrato `BenchmarkExtractionAdapter` (que unifica Extracción $\rightarrow$ Layout $\rightarrow$ AST V2) y definir la política de aislamiento para evitar el *Dependency Hell* de librerías de IA.
* **Entregables:**
  * Contrato `BenchmarkCandidateProvider`.
  * Diseño de los adaptadores para los candidatos (Marker, Docling, Nougat, PyMuPDF).
  * Política de aislamiento de *Runtime*: Envolturas de ejecución (*wrappers* CLI, subprocesos tipo `subprocess.Popen` o contenedores Docker efímeros) para impedir colisiones de dependencias masivas (PyTorch, CUDA) en el entorno `core`.
* **Desafío Arquitectónico:** Asegurar que el benchmark mida el motor de extracción y su capacidad de mapeo al `AST V2`, sin acoplar el núcleo del traductor a librerías desechables.

### ADR F17.4: Adaptación del SequentialBenchmarkOrchestrator
* **Objetivo:** Refactorizar y generalizar el orquestador de métricas (actualmente sesgado a evaluación de LLMs y presupuestos de tokens) para soportar *pipelines* de extracción física.
* **Entregables:**
  * Adaptación de las clases de `core/benchmark` (`BenchmarkRunReport`, `ProviderDescriptor`).
  * Cableado de flujo: `Runner` (instancia un *Adapter*) $\rightarrow$ procesa el `BenchmarkDocument` $\rightarrow$ genera `AST` candidato $\rightarrow$ invoca a los Evaluadores Topológicos (contra el `Golden AST`).
* **Desafío Arquitectónico:** Reutilizar el sistema de persistencia (`BenchmarkPersistenceGateway`) y el motor estadístico sin romper la compatibilidad con los futuros benchmarks de LLMs.

### ADR F17.5: Leaderboard Estadístico y Selección del Parser
* **Objetivo:** Definir los criterios de victoria utilizando el rigor estadístico preexistente en el proyecto para seleccionar el parser definitivo.
* **Entregables:**
  * Reglas de ponderación multicriterio (ej. 50% *Equation Recall*, 30% *Tree Edit Distance*, 20% Latencia de Ingesta).
  * Aplicación del `StatisticalComparator` (Cliff's Delta, Holm-Bonferroni) para asegurar que la diferencia entre parsers no sea un artefacto de varianza aleatoria.
  * Reporte final de la *Fase 17* y declaración en código del motor por defecto que alimentará al sistema de aquí en adelante.
* **Desafío Arquitectónico:** Evitar sesgos empíricos. La selección debe ser 100% auditable y reproducible por cualquier *runner* que clone el repositorio.