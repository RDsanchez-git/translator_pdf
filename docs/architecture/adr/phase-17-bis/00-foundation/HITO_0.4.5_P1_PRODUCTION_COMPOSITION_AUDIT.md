# HITO_0.4.5_P1_PRODUCTION_COMPOSITION_AUDIT.md
## Control Plane, Orchestration Core & Production Pipeline Boundaries — Reporte Consolidado Bloque P1

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P1)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P1)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en el análisis AST del código fuente de producción y el Grafo Estático de Dependencias (`PIPELINE_P1_GRAPH.md`). Cero mutaciones en código productivo. Disposición y acciones diferidas al Hito 0.5.

---

## 1. MARCO EPISTEMOLÓGICO Y DESACOPLAMIENTO BENCHMARK VS. PRODUCCIÓN

El análisis del Grafo Estático de Dependencias del Bloque P1 (`PIPELINE_P1_GRAPH.md`) y la inspección directa del código fuente han establecido una distinción arquitectónica fundamental que reorienta el cierre de la Fase 0: **el subsistema de Benchmark no es el Pipeline de Producción.**

* **El Subsistema de Benchmark (`core/benchmark/`, `tools/evaluation/`):** Constituye un arnés de evaluación y calibración exógeno. Su función es construir un *mini-pipeline* sintético que ingiere PDFs de prueba, ejecuta proveedores candidatos (PyMuPDF, Docling, Marker), genera un AST borrador y lo compara mediante métricas topológicas (Distancia de Edición de Árboles Zhang-Shasha y Recall de Entidades) contra el *Ground Truth* para emitir reportes de significancia estadística y construir el Leaderboard de la Fase 17.
* **El Pipeline de Producción (`core/pipeline/`, `apps/bootstrap/`, `apps/cli/`, `runtime/`, `core/execution/`):** Constituye la canalización transaccional real del producto. Ingiere el binario PDF, construye el `DocumentLayout`, materializa el AST V2, aplica normalizaciones, segmenta oracionalmente, ejecuta el enrutamiento de estrategias, empaqueta en presupuestos de tokens, despacha asíncronamente a los trabajadores LLM con control de cuotas (FinOps), valida la sintaxis LaTeX post-traducción, ejecuta auto-reparaciones (*healing*) con *rollback*, ensambla fragmentos, compila con Tectonic y persiste eventos en un almacén CQRS gobernado por una Máquina de Estados Finita (FSM).

> **Conclusión Epistemológica del Bloque P1:** La auditoría de los bloques C1 a C5 certificó la validez del arnés de evaluación. Este Bloque P1 inaugura el escrutinio sobre la verdad operacional: el *Control Plane*, la raíz de composición (*Composition Root*) y las fronteras de ejecución que procesan los documentos científicos de los usuarios.

---

## 2. INVENTARIO FORENSE Y ANÁLISIS DE EVIDENCIA DURA (HALLAZGOS P1-01 A P1-18)

La auditoría forense del Bloque P1 ha revelado grietas de diseño, acoplamientos prohibidos y violaciones de Clean Architecture en la capa de composición y orquestación de producción. A continuación se detallan exhaustivamente todos los hallazgos registrados:

### 2.1. Ingesta, Composición y Doble Composition Root

#### OBS-P1-01 / P1-C01 (Inversión de Frontera y Acoplamiento Directo en `FSMStateStore`)
* **Ubicación:** `core/pipeline/state_store.py`
* **Mecanismo Causal:** El módulo declara la interfaz `StateStoreProtocol(Protocol)`. En el mismo archivo, la clase `FSMStateStore` implementa dicho protocolo, pero realiza la siguiente importación explicita de infraestructura:
  ```python
  from infra.db.fsm_repository import FSMRepository
  from core.execution.handlers import DocumentCommandHandler
  ```
* **Impacto Arquitectónico:** Viola la Arquitectura Hexagonal (*Ports & Adapters*). Un puerto/adaptador ubicado dentro del espacio de nombres `core/` importa directamente un repositorio concreto de `infra/`. El núcleo del dominio de aplicación se acopla físicamente a la implementación de persistencia SQLite, anulando la abstracción.

#### OBS-P1-02 (Raíz de Composición Dividida)
* **Ubicación:** `apps/bootstrap/pipeline_factory.py` vs. `apps/cli/main.py`
* **Mecanismo Causal:** `pipeline_factory.py` se presenta como the *Composition Root* central (`build_pipeline()`). Sin embargo, no construye el sistema de forma integral. `apps/cli/main.py` (el punto de entrada CLI) asume manualmente la instanciación e interconexión de la infraestructura de LLMs, FinOps y concurrencia:
  ```python
  groq_provider = GroqProvider(api_key=api_key, dialect=dialect)
  quota_manager = QuotaManager(rpm_limit=rpm_limit, tpm_limit=tpm_limit)
  rate_provider = RateLimitedProvider(underlying=groq_provider, quota_manager=quota_manager)
  cached_provider = CachedLLMProvider(underlying=rate_provider, db_path="infra/db/materialized.db")
  dispatcher = AsyncDispatcher(context_resolver=..., prompt_builder=..., provider_stack=cached_provider)
  ```
* **Impacto Arquitectónico:** No existe un único punto de verdad para la composición. Si se invoca el pipeline desde un Daemon o una API Web (`apps/api/`), se corre el riesgo de instanciar un pipeline incompleto o desalineado respecto al comportamiento del CLI.

#### OBS-P1-03 (Debilitamiento de Contratos con `Any` en the Factory)
* **Ubicación:** `apps/bootstrap/pipeline_factory.py`
* **Mecanismo Causal:** Mientras `core/pipeline/orchestrator.py` exige que el despachador cumpla con `DispatcherProtocol(Protocol)`, la función de fábrica relaja el tipo:
  ```python
  def build_pipeline(chunker: ChunkerProtocol, dispatcher: Any, ...) -> TranslationPipeline:
  ```
* **Impacto Arquitectónico:** Contradice la política de "composición con tipado estricto libre de *duck-typing*". El Type Checker de Python (`pyright` / `mypy`) es incapaz de validar la interfaz del `dispatcher` en la frontera de inyección.

#### OBS-P1-04 (Mocks y Adapters Provisionales en Runtime)
* **Ubicación:** `apps/cli/main.py`
* **Mecanismo Causal:** El CLI inyecta componentes temporales directamente en el pipeline productivo:
  * `DummyContextResolver`: Mock etiquetado como `TODO_PHASE15` que emite resoluciones de contexto nulas (`resolve_many() -> {}`).
  * `ChunkerProtocolAdapter`: Adaptador local que envuelve la función procedural `build_semantic_chunks_as_units`.
* **Impacto Arquitectónico:** El camino de ejecución de producción depende de conectores temporales que devuelven estructuras vacías, impidiendo la resolución real de contextos jerárquicos.

#### OBS-P1-05 (Monkey-Patching de la Entidad de Dominio para UX)
* **Ubicación:** `apps/cli/main.py` (`handle_translate_async`)
* **Mecanismo Causal:** Para actualizar la interfaz visual basada en la librería `rich`, el CLI intercepta y reasigna dinámicamente el método de la entidad de trabajo en runtime:
  ```python
  original_enter_step = job.enter_step
  def proxy_enter_step(step: PipelineStep):
      original_enter_step(step)
      update_ux_boundary()
  job.enter_step = proxy_enter_step
  ```
* **Impacto Arquitectónico:** Violación de encapsulamiento. La capa de presentación modifica imperativamente la instancia de un objeto de dominio (`TranslationJob`) para inyectar *side-effects* de renderizado en consola.

---

### 2.2. Orquestación, Inlining y Módulos Huérfanos

#### P1-C01 / OBS-P1-13 (Instanciación In-line e Invasión de Responsabilidades en `TranslationPipeline`)
* **Ubicación:** `core/pipeline/orchestrator.py` (`execute`)
* **Mecanismo Causal:** `TranslationPipeline` viola el principio de Inversión de Dependencias (DIP) y la Arquitectura Limpia. En lugar de recibir procesadores especializados inyectados, los instancian internamente durante la ejecución del método `execute()`:
  * `classifier = SemanticNodeClassifier()`
  * `placeholder_fixer = StructuralAssetPlaceholder()`
  * `validator = ASTIntegrityValidator()`
  * `context_enricher = HierarchicalContextEnricher()`
  * Compila expresiones regulares hardcodeadas en su constructor: `self._exotic_bullets = re.compile(r'^\s*([•▪‣◦■♦○]|[-‑‒–—-]>\s*)\s*')`.
* **Impacto Arquitectónico:** El orquestador de aplicación asume lógica de negocio de bajo nivel (modificación de viñetas, reemplazo de *placeholders* de tablas/figuras y clasificación semántica de nodos), impidiendo probar el orquestador de forma aislada sin instanciar todo el dominio de normalización.

#### P1-C06 / OBS-P1-14 (Orfandad del Módulo de Enrutamiento `RoutingWorkflow`)
* **Ubicación:** `core/pipeline/workflow.py` vs. `core/pipeline/orchestrator.py`
* **Mecanismo Causal:** `core/pipeline/workflow.py` define `RoutingWorkflow.stream_translate_channel()`, el cual implementa la bifurcación del AST en canales (`TRANSLATE`, `PASSTHROUGH`, `OMIT`) apoyándose en `NodeRouter` y `PassthroughSink`. El Grafo Estático AST demuestra que `TranslationPipeline` **jamás importa ni invoca a `RoutingWorkflow`**.
* **Impacto Arquitectónico:** La infraestructura de enrutamiento desarrollada en la Fase 16.4 está completamente huérfana en el runtime de producción. Todo el AST es enviado ciegamente al chunker sin filtrar los nodos omitibles o de paso directo.

#### P1-C07 (Divergencia entre `DocumentLayoutBuilder` y `FlatASTBuilder`)
* **Ubicación:** `core/layout/builder.py` vs. `apps/bootstrap/pipeline_factory.py`
* **Mecanismo Causal:** La capa de layout define la etapa `DocumentLayoutBuilder` para procesar maquetación bidimensional mediante una tubería de `LayoutStage`. No obstante, `pipeline_factory.py` pasa directamente los bloques de `DocumentLayout` al `FlatASTBuilder` mediante una función interna `_adapter_mapper`:
  ```python
  def _adapter_mapper(document_layout: DocumentLayout) -> list[ASTNode]:
      flat_blocks = []
      for page in document_layout.pages:
          flat_blocks.extend(page.blocks)
      collection = LayoutBlockCollection(blocks=flat_blocks)
      return mapper.build(collection)
  ```
* **Impacto Arquitectónico:** `DocumentLayoutBuilder` (con sus etapas de normalización espacial, detección de columnas y fusión) no se ejecuta en la ingesta productiva oficial, constituyendo un "pipeline paralelo" o código zombi en `core/layout/`.

---

### 2.3. Identidad, Hash Criptográfico y FSM

#### OBS-P1-05 (Colisión Semántica entre Job ID y Document ID)
* **Ubicación:** `core/pipeline/orchestrator.py`
* **Mecanismo Causal:** En `TranslationPipeline.execute()`, se impone la asignación:
  ```python
  job.document_id = job.job_id
  ```
* **Impacto Arquitectónico:** Confunde la identidad de la transacción de ejecución (`job_id`) con la identidad del documento físico (`document_id`). Si un mismo documento PDF es reintentado en múltiples ejecuciones independientes, cada *Job* forzará un nuevo `document_id`, imposibilitando el seguimiento histórico del documento en la FSM.

#### P1-C03 / OBS-P1-12 (Calculo Prematuro del Hash AST)
* **Ubicación:** `core/pipeline/orchestrator.py`
* **Mecanismo Causal:** El pipeline ejecuta la siguiente secuencia lineal de operaciones:
  1. Classify batch
  2. Asset placeholder normalization
  3. **`current_ast_hash = compute_ast_hash(nodes)`**
  4. AST Integrity Validation
  5. **`nodes, structured_registry, ... = context_enricher.enrich_document(nodes)`**
  6. Persistence & Chunking with `nodes`
* **Impacto Arquitectónico:** El hash criptográfico registrado en el `TranslationJob` y enviado a la FSM se calcula sobre los nodos **antes** de que `HierarchicalContextEnricher` modifique la estructura agregando los metadatos y tokens de contexto jerárquico. El hash almacenado no corresponde con el AST que realmente se traduce y ensambla.

#### OBS-P1-07 (Doble FSM y Transiciones Ocultas en `FSMStateStore`)
* **Ubicación:** `core/pipeline/state_store.py` (`save`)
* **Mecanismo Causal:** Existe una desalineación entre el autómata de pasos de aplicación (`PipelineStep`) y el autómata de estados durables (`DocumentState`). Para cubrir esta falta de correspondencia, `FSMStateStore.save()` forja transiciones ocultas que el orquestador jamás emitió:
  ```python
  # Intercepción 1: Promoción oculta a Assembly Ready
  if status.current_state == "PROCESSING" and cmd_class == StartAssemblyCommand:
      cmd_ready = MarkAssemblyReadyCommand(...)
      expected_version = self.handler.handle(cmd_ready)

  # Intercepción 2: Auto-promoción en ráfaga de la fase de compilación
  if status.current_state == "ASSEMBLING" and cmd_class == CompleteDocumentCommand:
      cmd_ready_comp = MarkCompilationReadyCommand(...)
      expected_version = self.handler.handle(cmd_ready_comp)
      cmd_start_comp = StartCompilationCommand(...)
      expected_version = self.handler.handle(cmd_start_comp)
  ```
* **Impacto Arquitectónico:** El adaptador de persistencia falsea el historial de eventos CQRS. Forja comandos de "compilaciones fantasma" (`StartCompilationCommand`) que el pipeline nunca coordinó, violando la trazabilidad del Event Log.

#### OBS-P1-08 (Inexistencia de Transición Persistida para `AUDITING`)
* **Ubicación:** `core/pipeline/state_store.py`
* **Mecanismo Causal:** `TranslationJob` entra formalmente al paso `PipelineStep.AUDITING`. Sin embargo, `STEP_TO_COMMAND_CLASS` omite dicho paso en su diccionario de mapeo.
* **Impacto Arquitectónico:** La etapa de auditoría existe en la memoria del runtime, pero es completamente invisible para la base de datos de la FSM.

#### OBS-P1-06 (Discrepancia Semántica en el Mecanismo de Reanudación "Resume")
* **Ubicación:** `core/pipeline/orchestrator.py`
* **Mecanismo Causal:** Cuando el pipeline detecta un trabajo previo con el mismo `ast_hash` (`is_valid_resume = True`), la única etapa que omite re-ejecutar es la persistencia de `PipelineStep.PARSING`.
* **Impacto Arquitectónico:** El sistema no realiza un *checkpoint-resume* granular (no salta a la fase donde ocurrió el fallo). Ejecuta un **macro-replay**: vuelve a clasificar, enriquecer contexto, empaquetar chunks, despachar a LLMs (apoyándose en la caché) y ensamblar.

---

### 2.4. CQRS, Encapsulamiento y Asincronía en Workers

#### P1-H01 (Ruptura Generacional en Reconciliación CQRS)
* **Ubicación:** `core/execution/handlers.py` (`ReconciliationCommandHandler.handle_rematerialize`)
* **Mecanismo Causal:** Al rematerializar una tarea desde el Event Log hacia la vista proyectada, el manejador ejecuta:
  ```python
  self.mat.upsert_projection(
      cmd.document_id,
      "unknown_ast_hash",
      cmd.node_id,
      ...
  )
  ```
* **Impacto Arquitectónico:** Destruye la barrera de seguridad generacional. Inyecta proyecciones en el `MaterializedPlaneRepository` asociadas al string literal `"unknown_ast_hash"`, contaminando el plano de lectura con datos no vinculados al hash real del documento.

#### P1-H02 (Desacoplamiento de Hash en `RematerializeTaskCommand`)
* **Ubicación:** `core/execution/handlers.py`
* **Mecanismo Causal:** El comando `RematerializeTaskCommand` transporta el atributo `content_hash`. No obstante, el manejador busca el evento más reciente en WAL (`get_latest_event(cmd.node_id)`) y utiliza `latest_event.content_hash` sin validar si coincide con el hash solicitado en el comando.
* **Impacto Arquitectónico:** Riesgo de inconsistencia temporal en CQRS. Se proyecta un estado distinto al solicitado si ocurrieron eventos posteriores en el WAL.

#### P1-H03 (Perforación de Encapsulamiento en `ASTRegistry`)
* **Ubicación:** `apps/compiler/__main__.py` (`AssemblerWorkerDaemon`)
* **Mecanismo Causal:** El daemon que escucha tareas de ensamblado e invoca la compilación accede directamente a atributos y métodos privados del registro en memoria:
  ```python
  if cache_key not in self.ast_registry._cache:
      self.ast_registry._load_document(doc_id, ast_hash)
  doc_nodes = self.ast_registry._cache.get(cache_key, {})
  ```
* **Impacto Arquitectónico:** Acoplamiento severo entre la infraestructura de workers y la implementación interna de `ASTRegistry`. Viola el principio de ocultamiento de información.

#### P1-H07 (Duplicación e Instanciación Impura en Worker Compiler)
* **Ubicación:** `apps/compiler/__main__.py`
* **Mecanismo Causal:** El archivo de entrada del worker de compilación contiene la siguiente duplicación literal de código:
  ```python
  tex_builder = TexBuilder(context=render_context)
  tex_builder = TexBuilder(context=render_context)
  ```
  Además, construye `RenderUnit` manualmente iterando sobre las proyecciones materializadas de SQLite en lugar de consumir el `DocumentAssembler` y el `RenderUnitMapper` del core.

---

## 3. GRAFO Y FLUJO OPERACIONAL REAL DE PRODUCCIÓN (RUNTIME VS. TEORÍA)

El análisis forense permite contrastar el diagrama conceptual frente a la ejecución física observada en el código:

```text
==================================================================================================
                              FLUJO TEÓRICO DE PRODUCCIÓN (CLEAN ARCH)
==================================================================================================

  CLI EntryPoint ──► Composition Root ──► TranslationPipeline ──► RoutingWorkflow ──► Chunker
                            (Factory)                                (Translate/Pass)     │
                                                                                          ▼
  PDF Artifact ◄── Compiler ◄── Assembler ◄── Validation & Healing ◄── AsyncDispatcher ◄──┘

==================================================================================================
                             FLUJO REAL EN TIEMPO DE EJECUCIÓN (OBSERVADO)
==================================================================================================

  apps/cli/main.py 
     ├── Instancia DummyContextResolver (Mock temporal)
     ├── Instancia ChunkerProtocolAdapter (Wrapper local de hashing)
     ├── Configura LLM Stack (Groq -> RateLimit -> Cache -> AsyncDispatcher)
     ├── Monkey-Patch: job.enter_step = proxy_enter_step (Mutación UX)
     │
     ▼
  apps/bootstrap/pipeline_factory.py (Composition Root Parcial)
     ├── Instancia PyMuPDFProvider + PdfParserAdapter
     ├── Inyecta SQLite Connections ("infra/db/documents.db", "fsm.db")
     ├── Mutación posterior: dispatcher.validation_pipeline = ...
     │
     ▼
  core/pipeline/orchestrator.py (TranslationPipeline.execute)
     ├── 1. Parser.parse() -> PdfParserAdapter -> FlatASTBuilder
     ├── 2. SemanticNodeClassifier() (In-line)
     ├── 3. StructuralAssetPlaceholder() (In-line)
     ├── 4. compute_ast_hash() (¡Calculado prematuramente!)
     ├── 5. ASTIntegrityValidator() (In-line)
     ├── 6. HierarchicalContextEnricher() (In-line -> Modifica nodos)
     ├── 7. FSMStateStore.save() (Sincroniza FSM - State PARSING)
     ├── 8. BYPASS: Ignora completamente RoutingWorkflow (Código Huérfano)
     ├── 9. Chunker.chunk() -> TokenBudgetChunker
     ├── 10. SQLiteDocumentRepository.save_batch()
     ├── 11. AsyncDispatcher.dispatch() -> LLM Worker -> Validation -> Healing
     ├── 12. FSMStateStore.save() (Sincroniza FSM - State ASSEMBLING)
     ├── 13. DocumentAssembler.assemble()
     ├── 14. SummaryBuilder.build()
     └── 15. FSMStateStore.save() (Paso FINISHED -> Dispara comandos de compilación ocultos)
```

---

## 4. MATRIZ TAXONÓMICA DE RIESGO Y DISPOSICIÓN ARQUITECTÓNICA (HITO 0.5)

| Componente / Módulo | Estado ArquITECTÓNICO | Severidad | Hallazgo Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `core/pipeline/state_store.py` | Boundary Violation | **P0 (Crítico)** | `FSMStateStore` importa `FSMRepository` de `infra/db/`. | **REUBICAR A INFRA / ADAPTER** |
| `core/pipeline/orchestrator.py` | In-line Invasión | **P0 (Crítico)** | Instanciación in-line de clasificadores; omite `RoutingWorkflow`. | **REFACTORIZAR OBLIGATORIO** |
| `core/pipeline/workflow.py` | Code Huérfano | **P0 (Crítico)** | `RoutingWorkflow` no es invocado por el pipeline principal. | **INTEGRAR EN TRANSLATION_PIPELINE** |
| `core/execution/handlers.py` | Generational Loss | **P0 (Crítico)** | Reconciliador usa `"unknown_ast_hash"` en proyecciones. | **REFACTORIZAR OBLIGATORIO** |
| `apps/bootstrap/pipeline_factory.py` | Split Root | **P1 (Alto)** | Mutación posterior de atributos en `dispatcher`. Rutas hardcodeadas. | **CONSOLIDAR FACTORY** |
| `apps/cli/main.py` | Entry Point Impuro | **P1 (Alto)** | Monkey-patching sobre `TranslationJob`, uso de `DummyContextResolver`. | **REFACTORIZAR CLI** |
| `apps/compiler/__main__.py` | Encapsulation Leak | **P1 (Alto)** | Accede a `._cache` y `._load_document` de `ASTRegistry`. Duplicación TeX. | **CREAR PUERTO PÚBLICO** |
| `core/pipeline/job.py` | Domain Entity | **P2 (Medio)** | Entidad sólida; `pipeline_metadata` requiere esquema tipado. | **CONSERVAR / REFINAR TIPO** |
| `core/pipeline/protocols.py` | Interfaces | **Cero** | Interfaces puras usando `typing.Protocol`. | **CONSERVAR** |

---

## 5. MARCO NORMATIVO Y REGISTRO DE REGLAS DE REMEDIACIÓN (P1-R01 A P1-R11)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes reglas constituyen el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P1-R01 (Inversión Hexagonal en StateStore - P0):** Mover `FSMStateStore` fuera del paquete `core/pipeline/` y reubicarlo como un adaptador concreto en `infra/adapters/` o `infra/db/`. El `core/` debe interactuar únicamente con la interfaz `StateStoreProtocol`.
* **P1-R02 (Restauración de Barrera Generacional CQRS - P0):** Eliminar el valor por defecto `"unknown_ast_hash"` en `ReconciliationCommandHandler`. Extender `RematerializeTaskCommand` para transportar el `ast_hash` real y exigir su presencia antes de escribir en el `MaterializedPlaneRepository`.
* **P1-R03 (Sincronización Cronológica del Hash AST - P0):** Reordenar la ejecución en `TranslationPipeline.execute()` para invocar a `compute_ast_hash(nodes)` **estrictamente después** del `HierarchicalContextEnricher` y de cualquier mutación de normalización pre-FSM.
* **P1-R04 (Integración del Enrutador de Canales - P0):** Conectar `RoutingWorkflow` en `TranslationPipeline` para filtrar y clasificar los nodos en `TRANSLATE`, `PASSTHROUGH` y `OMIT` antes de entregarlos al `TokenBudgetChunker`.
* **P1-R05 (Unificación de the Composition Root):** Centralizar la instanciación de dependencias en `pipeline_factory.py`. Eliminar la creación manual de proveedores LLM, Rate Limiters, Caché y Dispatchers en `apps/cli/main.py`. Reemplazar `DummyContextResolver` por el resolvedor real de producción.
* **P1-R06 (Eliminación de Transiciones Ocultas en FSM):** Sincronizar los pasos de `PipelineStep` con los comandos de `DocumentState`. Prohibir que `FSMStateStore.save()` autopromocione comandos de compilación no ordenados explícitamente por el pipeline.
* **P1-R07 (Protección de Encapsulamiento en Registros):** Diseñar un método público `get_document_nodes(document_id, ast_hash)` en `ASTRegistry`. Prohibir que `AssemblerWorkerDaemon` acceda a miembros privados (`._cache`, `._load_document`).
* **P1-R08 (Prohibición de Monkey-Patching y Mutación Posterior):** Eliminar la reasignación de métodos en runtime (`job.enter_step = proxy_enter_step`) en el CLI y la inyección mutativa posterior en la fábrica (`dispatcher.validation_pipeline = ...`). Pasar todas las dependencias como inmutables en los constructores.
* **P1-R09 (Inyección Limpia de Procesadores de Dominio):** Eliminar la instanciación in-line de `SemanticNodeClassifier`, `StructuralAssetPlaceholder`, `ASTIntegrityValidator` y `HierarchicalContextEnricher` dentro de `TranslationPipeline`. Inyectar un pipeline de normalización de entrada compuesto.
* **P1-R10 (Externalización de Configuración de Infraestructura):** Retirar las cadenas de conexión SQLite hardcodeadas (`"infra/db/documents.db"`, `"infra/db/fsm.db"`, `"infra/db/materialized.db"`) de los módulos de bootstrap y CLI, moviéndolas a variables de entorno o a un DTO `PipelineConfig`.
* **P1-R11 (Aclaración de Pipeline de Layout Zombi):** Resolver en el Hito 0.5 si `DocumentLayoutBuilder` (`core/layout/builder.py`) debe integrarse formalmente en el flujo de ingesta de producción o si debe ser deprecado en favor de `PdfParserAdapter` + `FlatASTBuilder`.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Modelado y Arquitectura Conceptual:** **SÓLIDO Y SOTA.** La separación CQRS, el diseño de la FSM, la presencia de comandos inmutables con *epoch fencing* y los contratos de `protocols.py` demuestran un diseño intencionalmente robusto.
2. **Ejecución de Runtime y Orquestación:** **DISCONTINUO / REQUIERE REMEDIACIÓN CRÍTICA.** Se observan fugas de infraestructura hacia el core, el bypass del sistema de enrutamiento, transiciones de estado fantasma y errores de orden en el cálculo de la identidad criptográfica del AST.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P1

The audit for **Block P1 (Control Plane, Orchestration Core & Production Pipeline Boundaries)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P1
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (El runtime incumple restricciones Clean Arch)
  Remediation Backlog      | OPEN (Reglas P1-R01 a P1-R11 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque P1. Se confirmó la vital distinción epistemológica entre el framework de Benchmark y el Pipeline de Producción. La arquitectura transaccional de producción está bien delineada teóricamente, pero la implementación actual sufre de fugas de infraestructura (FSMStateStore), orfandad de enrutamiento, ruptura generacional en CQRS ("unknown_ast_hash") y error cronológico en el cálculo de firmas. Queda estrictamente prohibido mutar código. Todo hallazgo se documenta en el backlog de remediación, despejando la vía para proceder a auditar el Bloque P2 (Physical Ingestion $\rightarrow$ Layout $\rightarrow$ AST)."*