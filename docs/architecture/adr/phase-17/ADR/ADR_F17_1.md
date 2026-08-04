# ARCHITECTURE DECISION RECORD (ADR)
## Fase 17.1: Scientific Ground Truth (Golden AST Definición y Alineación Canónica)

**Contexto y Problema:**
Con el espacio muestral (`Benchmark Corpus`) consolidado, el sistema requiere una referencia de verdad absoluta para medir de forma empírica y matemática la precisión de los parsers candidatos. El diseño inicial adolecía de fugas de abstracción: consideraba al formato físico (JSON) como un modelo de dominio en sí mismo, creaba una familia de DTOs paralela redundante, incrustaba lógicas dinámicas de tolerancia geométrica en los datos estáticos y supeditaba la generación del borrador a una única librería. Adicionalmente, acumular reglas de canonicidad científica STEM dentro del propio registro arquitectónico amenazaba con hipertrofiar el documento, diluyendo las decisiones de diseño en detalles de prosa editorial.

**Objetivo:**
Establecer la ontología canónica, la segregación modular del espacio de la verdad absoluta y la política de extensión de metadatos para el Ground Truth, garantizando la reutilización del modelo `AST V2` nativo y abstrayendo los mecanismos de serialización y generación inicial en componentes periféricos intercambiables.

**Decisiones Arquitectónicas:**

1. **Pureza del Dominio (Reutilización de AST V2):** El Ground Truth no se define como un formato o estructura de datos independiente. El Golden AST es una colección viva de instancias puras de los modelos inmutables de `ASTNode` de la Fase 16. Los detalles de transformación física se delegan a la capa de infraestructura genérica mediante un serializador especializado (`infra/serialization/ast_json.py`), quedando el core libre de nociones de formato (JSON, CBOR, Protobuf).
2. **Segregación de Subdominios (Corpus vs. Ground Truth):** Se rechaza la inclusión del Ground Truth dentro del espacio lógico del Corpus. Se establece el submódulo dedicado `core/benchmark/ground_truth/`. El Corpus responde exclusivamente a la pregunta *"¿Qué documentos existen?"*, mientras que el Ground Truth responde *"¿Cuál es la representación canónica estructural de cada documento?"*.
3. **Unificación y Trazabilidad del Manifiesto:** Se prohíbe la creación de catálogos o archivos de control paralelos. La trazabilidad y el linaje de la verdad absoluta se centralizan expandiendo el `RawCorpusManifestDTO` existente en el archivo `manifest.json` único. Cada documento incorporará dos nuevas propiedades obligatorias: `ground_truth_version` (para gobernar la evolución secuencial de las anotaciones humanas ante correcciones editoriales) y `ground_truth_sha256` (para validación genética pre-vuelo).
4. **Purismo Geométrico Absoluto:** El Golden AST registrará únicamente las coordenadas espaciales absolutas de los elementos físicos (`BoundingBox` con x, y, w, h). Se prohíbe inyectar umbrales, márgenes o porcentajes de tolerancia dentro de las estructuras de datos. La flexibilidad ante variaciones posicionales es responsabilidad exclusiva de los jueces comparadores y las políticas dinámicas de IoU (`BoundingBoxComparator` / `TolerancePolicy`) que se diseñarán en la Fase 17.2.
5. **Principio de Intercambiabilidad del Bootstrap:** El mecanismo de generación inicial de borradores constituye un detalle de infraestructura efímero y sustituible. No forma parte del contrato arquitectónico del Ground Truth. El pipeline puede alternar entre Marker, Docling, Nougat o ensembles de modelos visuales sin alterar los contratos del caso de uso.
6. **Gobernanza Normativa Exterior (`GROUND_TRUTH_SPEC.md`):** Las reglas específicas de canonicidad, normalización matemática (LaTeX balanceado en bloques `DISPLAY_EQUATION`) y continuidad léxica trans-página se extirpan de este ADR. Se consolidan en un documento normativo independiente denominado `GROUND_TRUTH_SPEC.md`, el cual actuará como la especificación funcional y el manual de auditoría para el revisor humano.

**No-Objetivos:**
* No se desarrollan los componentes de cálculo de distancias de grafos o métricas de similitud estructural.
* No se implementan los motores de tolerancia geométrica ni los algoritmos comparadores de cajas de colisión.

---

# ROADMAP DE EJECUCIÓN (Hitos)

## Hito 1: Infraestructura de Serialización y Extensión Contractual
Ampliación de los esquemas base de metadatos e implementación del sumidero genérico.
* Modificar `RawDocumentEntryDTO` e `infra/fs/corpus_repository.py` para soportar de forma tipada las propiedades `ground_truth_version` y `ground_truth_sha256`.
* Desarrollar el adaptador puro de infraestructura `infra/serialization/ast_json.py` para gestionar la deshidratación y rehidratación de colecciones de `ASTNode`.

## Hito 2: Creación del Bounded Context y Caso de Uso de Carga
Aislamiento del oráculo semántico y conexión de lectura.
* Instanciar el submódulo `core/benchmark/ground_truth/` e incorporar el caso de uso `LoadGroundTruthUseCase` acoplado al puerto del lector.
* Desarrollar `core/benchmark/ground_truth/ports.py` definiendo el contrato abstracto de provisión del Ground Truth.

## Hito 3: Herramienta de Drafting e Inyección de la Especificación
Materialización del entorno operativo de asistencia y documentación de reglas.
* Redactar `docs/GROUND_TRUTH_SPEC.md` detallando las políticas obligatorias de balanceo TeX y fusión de párrafos continuos.
* Desarrollar el script de automatización periférica `tools/evaluation/generate_golden_draft.py` configurado por inversión para volcar las colecciones iniciales de nodos en `tests/corpus/benchmark_v1/ground_truth/`.

## Hito 4: Sellado Criptográfico del Repositorio de Verdad
Cierre del ciclo del hito con validación estricta de consistencia.
* Ejecutar la curaduría humana sobre los primeros 5 documentos de estrés estructural seleccionados del corpus.
* Desarrollar `tools/evaluation/freeze_ground_truth.py` para calcular el hash de los archivos ordenados, inyectar las versiones y firmas correspondientes en el `manifest.json` y congelar la línea de base.