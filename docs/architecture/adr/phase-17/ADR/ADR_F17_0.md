# ARCHITECTURE DECISION RECORD (ADR)
## Fase 17.0: Benchmark Corpus (Espacio Muestral y Taxonomía Estructural)

**Contexto y Problema:**
Tras la estabilización del núcleo del Traductor PDF (Fase 16), el cuello de botella arquitectónico se ha desplazado hacia el motor de extracción (Parser). Para ejecutar la Fase 17 (selección empírica entre motores de visión computacional), se requiere establecer un *Ground Truth* y medir métricas topológicas (ej. Tree Edit Distance). Sin embargo, un benchmark carece de validez científica si su espacio muestral no está formalmente definido y versionado. Evaluar parsers utilizando únicamente documentos limpios induce a un *overfitting* estructural. Actualmente, el proyecto carece de una colección estática, categorizada por atributos, y determinista de PDFs que sirva como activo científico y "pista de pruebas" universal.

**Objetivo:**
Definir, estructurar y congelar un espacio muestral representativo (el *Benchmark Corpus*) que sirva como base empírica inmutable para todos los experimentos del ciclo de vida del traductor, garantizando que las métricas estructurales posean significancia estadística, reproducibilidad absoluta y representen los desafíos topológicos reales del dominio.

Una vez publicada una versión del Benchmark Corpus, los documentos existentes no podrán modificarse ni eliminarse. Las nuevas incorporaciones requerirán una nueva versión del corpus o una política explícita de compatibilidad, preservando la reproducibilidad histórica de todos los experimentos.

**Decisiones Arquitectónicas:**

1. **Taxonomía Basada en Propiedades Estructurales (Traits):** La clasificación de los documentos se abstrae de su origen editorial (ej. IEEE, Springer). Se implementa un modelo de perfiles basado en propiedades combinables. Un documento podrá etiquetarse múltiplemente con rasgos como: `native_pdf`, `scanned`, `multi_column`, `heavy_equations`, `nested_tables`, `floating_figures`, etc. Esto garantiza una extensibilidad infinita del corpus.
2. **Inmutabilidad Experimental y Trazabilidad:** Todo experimento de *Benchmarking* debe ser estocásticamente reproducible. Se impone el versionado estricto del corpus. El `SequentialBenchmarkOrchestrator` deberá registrar en el `BenchmarkRunReport` el identificador de la versión del corpus, el Hash del manifiesto y los Hashes individuales de los documentos evaluados. 
3. **El "Corpus Manifest" como Entidad de Dominio:** El catálogo de documentos deja de ser tratado como un simple archivo auxiliar. Se instaura el `Corpus Manifest` como una entidad formal del Bounded Context de *Benchmark*. Su serialización física (JSON, YAML, Parquet) es un detalle de infraestructura, pero el dominio siempre interactuará con el contrato abstracto.
4. **Desacoplamiento de Almacenamiento Físico:** Se evita anclar el diseño a rutas locales efímeras (ej. `tests/corpus/`) o herramientas específicas de control de versiones. La arquitectura define un `Benchmark Corpus Repository` abstracto. La infraestructura subyacente deberá garantizar el almacenamiento eficiente y versionado de los artefactos binarios (BLOBs), independientemente de la tecnología elegida.
5. **Independencia del Ground Truth:** Esta etapa se limita exclusivamente a la definición taxonómica, selección y almacenamiento del *input* crudo (los PDFs). La generación de la salida ideal (el AST esperado) y las aserciones de calidad se delegan estrictamente a la Fase 17.1.

**No-Objetivos:**
* No se definen límites rígidos sobre la cantidad de documentos (el corpus será lo suficientemente pequeño para permitir iteración local rápida, pero estadísticamente diverso).
* No se generará el AST canónico (`Golden AST`) ni la representación de la verdad absoluta en este hito.
* No se impondrán decisiones de infraestructura (como Git LFS, S3 o DVC) en este documento.

---

# ROADMAP DE EJECUCIÓN (Hitos)

## Hito 1: Definición de Taxonomía Estructural
Diseño del modelo de perfiles y etiquetas para la curaduría documental.
* Definir el catálogo oficial de *Traits* (ej. `multi_column`, `heavy_math`, `scanned_noise`).
* Modelar la estructura de datos del `Corpus Manifest` (document_id, traits, sha256_hash).

## Hito 2: Curaduría Documental
Selección manual y preparación de los artefactos físicos basados en la taxonomía.
* Recopilar documentos científicos que cubran el espectro completo de *Traits* definidos.
* Saneamiento: Aislar fragmentos representativos (ej. extraer 3-5 páginas críticas de un libro extenso) para garantizar que los ciclos locales de benchmarking no incurran en tiempos de cómputo inasumibles.

## Hito 3: Estructuración del Repositorio y Manifiesto
Materialización de los artefactos y generación de la entidad de metadatos.
* Instanciar el `Benchmark Corpus Repository` (ubicación física a definir por infraestructura).
* Generar la primera serialización del `Corpus Manifest` con los hashes inmutables de los PDFs recopilados.

## Hito 4: Integración con el Dominio `core/benchmark`
Asegurar que el framework reconozca y valide la nueva entidad.
* Expandir `BenchmarkDataset` para hidratarse directamente desde el `Corpus Manifest`.
* Modificar `BenchmarkMetadata` para que herede y congele el Hash de la versión actual del corpus evaluado.

---

## TAXONOMÍA DE IMPACTO POR BOUNDED CONTEXT

Esta tabla delimita el impacto exacto de las decisiones de la Fase 17.0 sobre los módulos del sistema.

| Bounded Context / Módulo | Tipo de Impacto | Requisito / Modificación | Acción Correctiva (Fase 17.0) |
| :--- | :--- | :--- | :--- |
| `core/benchmark/models.py` | **Semántico / Dominio** | Modelado del `Corpus Manifest` y Taxonomía. | Añadir soporte para listas de *Traits* en `BenchmarkDocument` y registrar firmas de inmutabilidad en `BenchmarkMetadata`. |
| `core/benchmark/orchestrator.py`| **Lógico** | Trazabilidad del experimento. | Inyectar el Hash del manifiesto en el reporte final para asegurar reproducibilidad. |
| Infraestructura de Almacenamiento | **Físico / Persistencia** | Almacenamiento de BLOBs versionados. | Proveer la ruta física y el mecanismo (ej. submódulo, LFS o directorio local rastreado) para albergar el corpus sin degradar el repositorio de código. |

---


## RESULTADOS CONSOLIDADOS FASE 17.0 (Benchmark Corpus y Taxonomía Estructural)

### 1. Implementación del Subdominio: `core/benchmark/corpus/`
* **Causa Raíz:** Ausencia de un espacio muestral estático, indexado y versionado para la evaluación científica de parsers candidatos. Propensión a la obsesión por primitivos (*Primitive Obsession*) y acoplamiento de las entidades puras con metadatos y efectos secundarios de persistencia.
* **Correcciones Aplicadas:**
  * **`models.py` & `enums.py`:** Modelado inmutable del agregado `CorpusManifest` y sus entidades asociadas utilizando Pydantic Dataclasses nativas de V2. Se erradicó por completo el uso de la bandera permisiva `arbitrary_types_allowed=True`, garantizando la introspección y validación estricta del linter. Se inyectó validación implacable en el constructor del Value Object `DocumentFingerprint` para forzar hashes en minúsculas y lanzar excepciones directas ante malformaciones sintácticas.
  * **`dtos.py`:** Aislamiento perimetral de la morfología física del sumidero JSON mediante los DTOs inmutables rígidos `RawCorpusManifestDTO` y `RawDocumentEntryDTO`, purgando el flujo de diccionarios opacos (`Dict[str, Any]`) débiles para el análisis estático.
  * **`hasher.py` (`ManifestFingerprintCalculator`):** Servicio de dominio puro encargado del cálculo determinista de la firma global del manifiesto, aislando esta métrica de control fuera de las entidades de negocio mediante un ordenamiento alfabético estricto de identificadores y rasgos (*Traits*).
  * **`use_cases.py`:** Bifurcación ortogonal del flujo de aplicación en dos componentes especializados. `BootstrapCorpusManifestUseCase` encapsula el camino de escritura y reconciliación física contra el hardware, emitiendo un objeto rico `BootstrapCorpusResult`. `LoadCorpusManifestUseCase` habilita el camino rápido de lectura en runtime en tiempo constante O(1) RAM, evitando la reescritura innecesaria del archivo de catálogo en cada campaña de evaluación.
  * **`mapper.py` & `services.py`:** Introducción de `CorpusToBenchmarkDatasetMapper` y `DocumentComplexityClassifier` en la capa de aplicación. Traduce y adapta la taxonomía de propiedades del Corpus a la enumeración analítica del consumidor (`DocumentComplexity`), manteniendo el principio *Open/Closed* y erradicando la filtración de dependencias del contexto superior hacia el subdominio puro[cite: 1].
* **Métrica del Compilador:** `pyright core/benchmark/corpus/` $\rightarrow$ **0 errors, 0 warnings**.

---

### 2. Infraestructura e Inversión de Dependencias: `infra/` y `tools/`
* **Causa Raíz:** Acoplamiento hidráulico de librerías nativas compiladas de Computer Vision (`fitz` / PyMuPDF) dentro de la lógica de aplicación del benchmark y falta de contratos abstractos de inversión perimetral[cite: 1].
* **Correcciones Aplicadas:**
  * **`ports.py`:** Definición de los contratos formales `DocumentMetadataExtractorPort` (agnóstico al formato de entrada, devolviendo tipos primitivos hacia la aplicación) y `CorpusManifestLoaderPort` (abstracción de E/S desacoplada de la persistencia transaccional).
  * **`infra/adapters/document_metadata.py`:** Adaptador concreto `PyMuPdfDocumentMetadataExtractor` que encapsula herméticamente los efectos secundarios del sistema de archivos y el análisis binario en la periferia física del sistema.
  * **`infra/fs/corpus_repository.py` (`LocalFileSystemCorpusLoader`):** Adaptador de infraestructura encargado exclusivamente de la carga, persistencia y validación estructural del DTO del manifiesto en disco.
  * **`tools/evaluation/bootstrap_corpus.py`:** Entrypoint imperativo (*Imperative Shell*) purgado de lógica condicional, actuando únicamente como inyector de dependencias concretas para el disparo del caso de uso de sellado criptográfico.
* **Métrica de Integración:** Ejecución del orquestador vivo contra el `BenchmarkDataset` rehidratado por el Mapper $\rightarrow$ **Consistencia genética certificada, 0 regresiones detectadas**[cite: 2].