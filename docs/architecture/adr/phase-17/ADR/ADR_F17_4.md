# ADR F17.4: Generalización del SequentialBenchmarkOrchestrator y Unificación del Framework de Benchmarking

- **Estado:** Propuesto (Aprobado para Ejecución)
- **Fecha:** 2026-07-24
- **Autores:** Staff Architecture Team
- **Subdominio:** `core/benchmark` (Fase 17.4)
- **Dependencias:**
  - ADR 0016: Modelo de Dominio AST V2
  - ADR 0017: Familia de Algoritmos Tree Edit Distance (TED), Invariantes y Normalización
  - ADR F17.3: Capa de Integración Canónica de Extracción y Aislamiento de Runtime

---

## 1. Objetivo y Contexto

Las Fases 17.2 y 17.3 consolidaron el motor de evaluación topológica ($TED$/APTED, *Recall*, *Sequence Alignment*) y la capa de integración de extractores de maquetación (`PyMuPDFProvider`, `DoclingProvider`). Sin embargo, el subsistema principal de orquestación en `core/benchmark/` (`SequentialBenchmarkOrchestrator`) fue diseñado originalmente con un sesgo hacia la evaluación de modelos de lenguaje (LLMs), presuponiendo atributos hardcodeados de inferencia ($TPS$, conteo de tokens de entrada/salida, temperatura y costos en USD).

La Fase 17.4 establece la **Generalización de la Infraestructura de Benchmarking**, transformando a `core/benchmark/` en un marco de laboratorio agnóstico, polimórfico y extensible, capaz de orquestar y evaluar cualquier dominio del sistema (Parsers de maquetación, LLMs, Segmentadores, Traductores o Compiladores). Se persigue este objetivo sin introducir bibliotecas externas, sin duplicar componentes de infraestructura y manteniendo un control estricto de la complejidad del repositorio.

---

## 2. Decisiones Arquitectónicas

### 2.1 Orquestador Único y Agnóstico (`SequentialBenchmarkOrchestrator`)
Se prohíbe la creación de orquestadores especializados o duplicados (`ParserBenchmarkOrchestrator`, `EvaluationSession`, `BenchmarkCoordinator` o `BenchmarkEngine`). Existirá **un único orquestador** (`SequentialBenchmarkOrchestrator`) en `core/benchmark/orchestrator.py`. Su responsabilidad se limita a coordinar el ciclo de vida neutro de evaluación:

$$\text{CandidateProvider} \longrightarrow \text{Runner} \longrightarrow \text{Evaluator[]} \longrightarrow \text{PersistenceGateway} \longrightarrow \text{Reporter}$$

### 2.2 Inversión de Dependencias Estricta (DIP) y Registro de Proveedores
El orquestador interactuará **exclusivamente con contratos abstractos** definidos en `core/benchmark/ports.py`:
* `BenchmarkCandidateProvider`: Contrato para la entrega de artefactos/candidatos de evaluación.
* `BenchmarkEvaluatorProtocol`: Contrato para la ejecución de métricas de cualquier tipo.

Queda **estrictamente prohibido** que el orquestador importe o reconozca bibliotecas concretas de OCR o LLMs (`docling`, `fitz`, `google-generativeai`, `groq`). La resolución del proveedor concreto se realiza exclusivamente en la capa de fachada CLI mediante inyección de dependencias o fábricas (`ProviderRegistry`).

### 2.3 Generalización de Modelos y Colección Neutra de Métricas
Se refactorizan los DTOs de `core/benchmark/models.py` (`ProviderDescriptor`, `RunnerExecutionResult`, `BenchmarkRunReport`) eliminando cualquier supuesto estático de inferencia LLM (tokens, TPS, costo, prompts).
* Para evitar acoplamientos por dominio o proliferación de clases (`TopologyMetricsPayload`, `InferenceMetricsPayload`), las métricas se transportarán mediante un modelo neutro extensible de colección: `dict[str, MetricResult]` o mapeos equivalentes de pares clave-valor (`dict[str, Any]`). El orquestador operará sobre métricas de forma 100% transparente y agnóstica.

### 2.4 Registro Dinámico e Inyección de Métricas
El `SequentialBenchmarkOrchestrator` no conocerá ni importará las métricas por defecto (`default_metrics()`). Las métricas a evaluar serán construidas e inyectadas dinámicamente desde la fachada CLI hacia el orquestador como una lista de evaluadores (`list[BenchmarkEvaluatorProtocol]`). El orquestador se limitará a iterar sobre los evaluadores inyectados:

$$\forall e \in \text{Evaluators}: \quad \text{metrics}[e.\text{name}] = e.\text{evaluate}(\text{candidate}, \text{ground\_truth})$$

### 2.5 Reutilización de Infraestructura Existente y Persistencia
No se crearán gateways ni repositorios de persistencia secundarios. El `BenchmarkPersistenceGateway` en `core/benchmark/persistence.py` se reutiliza de forma integral para almacenar los reportes y registros de ejecución de cualquier dominio, manteniendo la compatibilidad con el esquema SQLite/JSON actual.

### 2.6 Unificación de Entrypoints y Unificación CLI
Se erradica la dualidad de scripts de ejecución experimental (`run_experimental_benchmark.py`). Toda la suite de evaluación topológica se canaliza a través del comando CLI unificado en `tools/evaluation/run_benchmark.py`, el cual actúa como una fachada ligera sobre el `SequentialBenchmarkOrchestrator`.

### 2.7 Aislamiento Absoluto del Dominio Validado y Cero Nuevas Dependencias
No se agregará **ninguna dependencia externa nueva** a `pyproject.toml` o `requirements.txt`. El refactor se realizará exclusivamente mediante patrones de diseño de la librería estándar de Python (`typing.Protocol`, `dataclasses`, `abc`).
Queda estrictamente congelado y protegido de cualquier modificación el código de dominio validado en las Fases 17.2 y 17.3: `FlatASTBuilder`, `DocumentLayout`, `ASTNode`, `StructuralTopologyMetric`, `EntityRecallMetric` y `SequenceAlignmentMetric`.

### 2.8 Garantía de Retrocompatibilidad (LLM Benchmarking)
La generalización del marco de benchmarking no debe alterar ni romper los flujos de evaluación preexistentes para modelos de lenguaje (`GeminiBenchmarkRunner`, `GroqBenchmarkRunner`). Ambos dominios (Inferencia LLM y Estructura documental) deben coexistir sobre la misma infraestructura de orquestación.

---

## 3. Plan de Ejecución (Hitos)

### Hito 1: Desacoplamiento del Orchestrator y Puertos
* **Objetivo:** Auditar y refactorizar `core/benchmark/ports.py` para definir los contratos abstractos puros `BenchmarkCandidateProvider` y `BenchmarkEvaluatorProtocol`.
* **Entregables:**
  * Declaración de interfaces abstractas desacopladas de cualquier motor de inferencia o parser físico en `core/benchmark/ports.py`.
  * Eliminación de acoplamientos a librerías de OCR/LLM concretas en el contrato de orquestación.

### Hito 2: Generalización de los Modelos de Benchmark
* **Objetivo:** Refactorizar `BenchmarkRunReport`, `ProviderDescriptor` y `RunnerExecutionResult` eliminando cualquier supuesto específico de inferencia LLM y permitiendo el almacenamiento agnóstico de resultados mediante colecciones de métricas.
* **Entregables:**
  * Eliminación de atributos específicos de LLM (tokens, temperatura, costo, TPS) del modelo común base.
  * Consolidación de un modelo de métricas genérico e inmutable (`dict[str, MetricResult]` o `dict[str, Any]`).
  * Compatibilidad simultánea con benchmarks topológicos y benchmarks de inferencia sin crear DTOs específicos por dominio.

### Hito 3: Pipeline Unificado y Fachadas CLI
* **Objetivo:** Unificar la ejecución del benchmark sobre una única canalización centralizada y eliminar scripts paralelos.
* **Entregables:**
  * Refactorización de `tools/evaluation/run_benchmark.py` y `generate_candidates.py` como fachadas ligeras sobre el orquestador unificado.
  * Inyección dinámica de métricas (`MetricRegistry` / `Evaluator[]`) desde el CLI al orquestador.
  * Depreciación y eliminación definitiva de `tools/evaluation/run_experimental_benchmark.py`.

### Hito 4: Persistencia y Reportes Agnósticos
* **Objetivo:** Conectar `BenchmarkPersistenceGateway` y la capa de reportería al pipeline de evaluación unificado.
* **Entregables:**
  * Persistencia de resultados mediante `BenchmarkPersistenceGateway` en `core/benchmark/persistence.py`.
  * Generación de reportes Markdown y JSON estructurados respetando las especificaciones del **ADR 0017**.

### Hito 5: Prueba de Arquitectura y Compatibilidad Total
* **Objetivo:** Demostrar la extensibilidad y robustez del orquestador mediante pruebas de integración sin modificar su código.
* **Entregables:**
  * Ejecución exitosa del benchmark comparativo de parsers (`PyMuPDF` vs `Docling`) sobre `calibration_v1` utilizando el `SequentialBenchmarkOrchestrator` refactorizado.
  * Verificación del Principio Open/Closed: la incorporación de un nuevo proveedor no requiere alterar una sola línea del orquestador.
  * Prueba de humo sobre el benchmark de LLMs para garantizar la retrocompatibilidad completa del framework.


## RESULTADOS CONSOLIDADOS FASE 17.4

### 1. Desacoplamiento del Orchestrator y Definición de Puertos Agnósticos (Hito 1)
* **Causa Raíz:** Acoplamiento aferente de la infraestructura de benchmarking (`core/benchmark/`) a conceptos exclusivos de inferencia LLM. Ausencia de interfaces abstractas puras para la provisión desacoplada de candidatos y la evaluación agnóstica de métricas, lo que forzaba al marco de evaluación a depender de implementaciones concretas o importar DTOs periféricos desde la capa de herramientas (`tools/`).
* **Correcciones Aplicadas:**
  * **`core/benchmark/models.py`:** Adición del Value Object agnóstico e inmutable `MetricResult` (`metric_name: str`, `value: float`, `details: dict[str, Any]`), garantizando que el núcleo en `core/` no dependa de DTOs o `Enum`s específicos provenientes de `tools/evaluation/topology/` y respetando la Regla de Dependencia Hexagonal.
  * **`core/benchmark/ports.py` (DIP & Protocols):**
    * Implementación de `BenchmarkCandidateProvider(Protocol)` con el método neutro `provide(document_id: str) -> Any` para desacoplar la entrega de candidatos respecto a motores físicos OCR o APIs de inferencia.
    * Implementación de `BenchmarkEvaluatorProtocol(Protocol)` con el contrato `evaluate(candidate: Any, ground_truth: Any) -> MetricResult` para estandarizar la evaluación de métricas en cualquier dominio ($TED$, *Recall*, $BLEU$, etc.).
  * **Garantía de Retrocompatibilidad:** Preservación intacta de `RunnerExecutionResult` y `BenchmarkRunnerProtocol` (`warmup`, `teardown`, `execute_dataset`), asegurando la compatibilidad absoluta con los ejecutores preexistentes (`GeminiBenchmarkRunner`, `GroqBenchmarkRunner`).
* **Métrica del Compilador:** `pyright core/benchmark/ports.py core/benchmark/models.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/` → **ALL PASSED**.

### 2. Generalización y Desacoplamiento de Modelos de Benchmark (Hito 2)
* **Causa Raíz:** Mezcla de responsabilidades por ubicación de DTOs de infraestructura en la capa de puertos (`ports.py`), riesgo de dependencias circulares entre módulos y opacidad en los tipos de retorno de los artefactos producidos por los proveedores.
* **Correcciones Aplicadas:**
  * **Aislamiento de Abstracciones Base (`core/benchmark/types.py`):** Creación del módulo neutro `types.py` que aloja `ProviderKind` (Enum funcional) y `BenchmarkArtifact` (Protocol marcador), eliminando la dependencia circular entre `models.py` y `ports.py`.
  * **Tipado Estricto de Artefactos:** Reemplazo de `Any` por `Optional[BenchmarkArtifact]` tanto en `RunnerExecutionResult` como en `BenchmarkExecution`, e inmutabilidad de metadatos en `ProviderDescriptor.capabilities` mediante `Mapping[str, Any]`.
  * **Unidad Atómica de Benchmark (`BenchmarkExecution`):** Consolidación del Value Object `BenchmarkExecution` como contenedor universal desacoplado de ejecuciones individuales, estructurando el orden lógico de atributos (contexto de ejecución primero, artefactos y métricas al final).
  * **Migración Hexagonal Límite:** Reubicación de `RunnerExecutionResult` dentro de `models.py` manteniendo intacta la colección `List[ChunkBenchmarkRecord]` para preservar compatibilidad con runners de LLM preexistentes.
  * **Aislamiento de Alcance:** Congelamiento de `BenchmarkRunReport` y `ProviderBenchmarkMetrics` sin modificaciones, postergando la agregación de reportes al Hito 3.
* **Métrica del Compilador:** `pyright core/benchmark/types.py core/benchmark/models.py core/benchmark/ports.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/` → **ALL PASSED**.

## RESULTADOS CONSOLIDADOS FASE 17.4

### 3. Fachadas CLI Unificadas y Registro Extensible de Métricas (Hito 3)
* **Causa Raíz:** Evaluación ansiosa (eager) de instancias en el registro de métricas, mutabilidad expuesta en la colección de perfiles y mantenimiento de lógica duplicada en scripts deprecados.
* **Correcciones Aplicadas:**
  * **Creación Perezosa y Encapsulamiento (`MetricRegistry`):** Refactorización de `MetricRegistry` en `tools/evaluation/topology/metrics/__init__.py` utilizando fábricas perezosas (`Callable[[], Sequence[TopologyMetric]]`) y ocultando la mutabilidad del registro mediante `.register()`.
  * **Estandarización de Inmutabilidad:** Ajuste de `MetricResult.details` a `Mapping[str, Any]` en los DTOs de dominio.
  * **Delegación Pura de Depreciación:** Reemplazo de la lógica duplicada en `tools/evaluation/run_experimental_benchmark.py` por una delegación directa hacia `run_benchmark.main()` acompañada de `DeprecationWarning`.
* **Métrica del Compilador:** `pyright tools/evaluation/topology/metrics/__init__.py tools/evaluation/run_benchmark.py tools/evaluation/generate_candidates.py tools/evaluation/run_experimental_benchmark.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/` → **ALL PASSED**.


### 4. Persistencia y Reportes Agnósticos (Hito 4)
* **Causa Raíz:** Acoplamiento de la infraestructura de persistencia a tipos de archivo y formatos específicos (Markdown/JSON).
* **Correcciones Aplicadas:**
  * **API de Persistencia Agnóstica (`core/benchmark/persistence.py`):** Reemplazo de métodos especializados por `save_artifact(filename, content)`, permitiendo que la infraestructura persista cualquier artefacto de texto sin conocer su formato ni su dominio.
  * **Delegación Pura en CLI (`tools/evaluation/run_benchmark.py`):** Invocación de `persistence.save_artifact(...)` desde la fachada para cada archivo de salida, aislando completamente las operaciones de I/O de la interfaz de usuario.
  * **Documentación de Invariantes (`tools/evaluation/topology/metrics/__init__.py`):** Explicitación del contrato de `MetricRegistry.register(...)` restringiendo su uso exclusivamente a la etapa de bootstrap.
* **Métrica del Compilador:** `pyright core/benchmark/persistence.py tools/evaluation/topology/metrics/__init__.py tools/evaluation/run_benchmark.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/` → **ALL PASSED**.


### 5. Prueba de Arquitectura y Compatibilidad Total (Hito 5)
* **Ajustes de Calidad:**
  * **Eliminación de Acoplamiento Temporal:** Remoción de `assert exec_time > 0.0` para evitar intermitencias por velocidad de CPU o resolución del reloj del SO.
  * **Aserciones por Interfaz:** Sustitución de la validación sobre cadenas internas de texto por `isinstance(artifact, BenchmarkArtifact)`, validando el contrato abstracto y no la implementación del mock.
  * **Persistencia Estricta:** Reemplazo de `.called` por `mock_persistence.save_final_report.assert_called_once()`.
* **Métrica del Compilador:** `pyright tests/integration/test_benchmark_orchestration_integration.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/integration/test_benchmark_orchestration_integration.py` → **2 PASSED**.