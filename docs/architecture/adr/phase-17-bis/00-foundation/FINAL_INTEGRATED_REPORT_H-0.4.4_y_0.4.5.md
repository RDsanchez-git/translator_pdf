# HITO_0.4.5_FINAL_INTEGRATED_REPORT.md
## Production Pipeline & Runtime Boundary Audit — Reporte Forense Integrado

* **Estado:** FROZEN / CONGELADO (Cierre de Fase 0 / Hito 0.4.5)[cite: 5]
* **Fecha de Emisión:** 2026-07-30[cite: 5]
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)[cite: 5]
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate)[cite: 5]
* **ADR de Gobernanza:** `ADR_F17-BIS_0`[cite: 5]
* **Límite Epistemológico:** Reconstrucción definitiva de la arquitectura en tiempo de ejecución (*runtime*) fundamentada en la evidencia forense de los bloques P1 a P7 y C1 a C5, desestimando inferencias sin sustento directo en código[cite: 5].

---

## SECCIÓN 1 — PRODUCTION PIPELINE FORENSIC REPORT (0.4.5-1)

El análisis forense del código fuente ha demostrado un cisma epistemológico en el sistema: el pipeline teórico declarado en las especificaciones de diseño y en los ADRs diverge de manera crítica de la canalización física que procesa los documentos en tiempo de ejecución[cite: 5]. La ejecución real sufre de múltiples cortocircuitos procedimentales (*bypasses*), módulos zombis (código existente pero inalcanzable), duplicación de motores y contaminación de responsabilidades[cite: 5].

A continuación, se presenta la reconstrucción anatómica paso a paso de la trazabilidad real vs. teórica del documento ($\text{PDF} \rightarrow \dots \rightarrow \text{Artefacto}$), con referencia a las aristas de código y la causa raíz de cada desvío detectado[cite: 5].

---

### DIAGRAMA DE FLUJO FÍSICO REAL VS. CANALIZACIÓN TEÓRICA

```
==================================================================================================
                 CANALIZACIÓN TEÓRICA DECLARADA EN ARQUITECTURA (FALSADA)
==================================================================================================

  [PDF] ──► [ExtractionProvider] ──► [LayoutBuilder (6 Stages)] ──► [LayoutValidator]
                                                                          │
  [TranslationUnit] ◄── [PolicyChunker] ◄── [RoutingWorkflow] ◄── [FlatASTBuilder]
         │
         ├──► [AsyncDispatcher] ──► [QuotaManager] ──► [CircuitBreaker] ──► [LLM Provider]
         │                                                                       │
         ▼                                                                       ▼
  [PDF] ◄── [Tectonic] ◄── [CompilationService] ◄── [DocumentAssembler] ◄── [Healing] ◄── [Validation]

==================================================================================================
                   CANALIZACIÓN FÍSICA OBSERVADA EN RUNTIME (EVIDENCIA DURA)
==================================================================================================

  [PDF Input]
       │
       ▼
  [PyMuPDFProvider.extract()] ──► DocumentLayout (LayoutBlock)[cite: 5]
       │
       ├─────────────────────────────────────────┐
       │ [BYPASS ✗] DocumentLayoutBuilder        │ [BYPASS ✗] DocumentLayoutValidator
       │ (6 Stages Zombis)[cite: 5]             │ (Completamente Omitido)[cite: 5]
       ▼                                         │
  [_adapter_mapper()] ◄──────────────────────────┘ (Fuga: Duck-Typing accidental)[cite: 5]
       │
       ▼
  [FlatASTBuilder.build()] ──► CrossPageNormalizer.execute()[cite: 5]
       │
       ▼
  [TranslationPipeline.execute()] (orchestrator.py)
       ├── 1. compute_ast_hash() [¡Prematuro! Incluye node_id efímero][cite: 5]
       ├── 2. Invocación in-line: SemanticNodeClassifier, StructuralAssetPlaceholder,
       │      ASTIntegrityValidator, HierarchicalContextEnricher[cite: 5]
       │
       ├── [BYPASS ✗] NormalizationPipeline (Bypasseado a favor de llamadas manuales)[cite: 5]
       ├── [BYPASS ✗] Segmenter V2 (core/segmenter/* es ZOMBI 100%)[cite: 5]
       └── [BYPASS ✗] RoutingWorkflow (core/routing/* es ZOMBI 100%)[cite: 5]
       │
       ▼
  [ChunkerProtocolAdapter] ──► core/ast/hashing.py (build_semantic_chunks_as_units)[cite: 5]
       │                         (Contaminación: TokenBudgetChunker vive en hashing.py)[cite: 5]
       ▼
  [BIPOLARIDAD OPERACIONAL]
       ├──────► RUTA A (CLI In-Process): AsyncDispatcher[cite: 5]
       │           ├── DummyContextResolver (¡Contexto nulo hardcodeado!)[cite: 5]
       │           ├── PromptBuilder (FastWordEstimator -> Subestima LaTeX)[cite: 5]
       │           ├── QuotaManager (Estado solo en RAM local)[cite: 5]
       │           └── [BYPASS ✗] GlobalCircuitBreaker (OMITIDO / ZOMBI 100%)[cite: 5]
       │
       └──────► RUTA B (Distributed Daemon): runtime/engine.py[cite: 5]
                   ├── ThreadPoolExecutor directo a bases SQLite[cite: 5]
                   └── [BYPASS ✗] Bypassea TranslationPipeline y Validation[cite: 5]
       │
       ▼
  [Validation & Healing]
       ├── [BYPASS ✗] PolymorphicValidationEngine (Pre-LLM es ZOMBI 100%)[cite: 5]
       ├── ValidationPipeline.validate_chunk() (Post-LLM)[cite: 5]
       └── HealingPipeline.heal_and_revalidate() (SOTA: Rollback atómico verificado)[cite: 5]
       │
       ▼
  [AssemblerWorkerDaemon] (apps/compiler/__main__.py)[cite: 5]
       │
       ├── [BYPASS ✗] CompilationService (core/compiler/service.py ZOMBI)[cite: 5]
       ├── [BYPASS ✗] DocumentAssembler / AssemblyPolicy (ZOMBI EN DAEMON)[cite: 5]
       │
       ├── Recolección ad-hoc manual de proyecciones desde SQLite[cite: 5]
       ├── TexBuilder.build() (LatexEscaper ciego al contexto)[cite: 5]
       └── DockerRunner.compile() (Falso Docker -> Tectonic local; Race condition)[cite: 5]
       │
       ▼
  [FSM & CQRS Persistence]
       ├── FSMRepository.transition_to() (SOTA: Compare-And-Swap con state_version)[cite: 5]
       ├── FSMStateStore.save() (Forja comandos de compilación fantasma)[cite: 5]
       ├── [EXPERIMENTAL_ENABLED = False] (CQRSReconciliationDaemon APAGADO)[cite: 5]
       └── Bug CQRS: Rematerialización inyecta "unknown_ast_hash" ahorcando el flujo[cite: 5]
```

---

### ESTRATIFICACIÓN DETALLADA DE LA CANALIZACIÓN REAL (ETAPAS 1 A 7)

#### FASE 1: Ingestión Física y Maquetación 2D (Physical Ingestion & Layout)
* **Entrada:** Archivo binario PDF[cite: 5].
* **Canalización Teórica:** $\text{PDF} \rightarrow \text{ExtractionProvider} \rightarrow \text{DocumentLayoutBuilder} \rightarrow \text{DocumentLayoutValidator} \rightarrow \text{FlatASTBuilder} \rightarrow \text{AST V2}$[cite: 5].
* **Flujo Físico Observado:**
  1. `PyMuPDFProvider.extract()` procesa el binario y emite un Aggregate `core.domain.document.DocumentLayout` compuesto por instancias de `LayoutBlock`[cite: 5].
  2. En `apps/bootstrap/pipeline_factory.py`, la función interna `_adapter_mapper` extrae los bloques crudos y los asigna a `LayoutBlockCollection`[cite: 5].
  3. `FlatASTBuilder.build()` procesa la colección e invoca a `_map_physical_to_logical`[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[BYPASS P0 - CRÍTICO] Bypassing Completo de `DocumentLayoutBuilder`:** El paquete `core/layout/builder.py` aloja un orquestador $2\text{D}$ estructurado en 6 etapas (`CoordinateNormalizer`, `SpatialAnalyzer`, `BlockIdentityGenerator`, `ReadingOrderResolver`, `LogicalClassifier`, `SpatialMerger`)[cite: 5]. El pipeline productivo **jamás instancía este builder**[cite: 5]. Todo el análisis espacial de columnas y grafos de lectura (DAG) es código $100\%$ zombi[cite: 5].
  * **[BYPASS P1 - ALTO] Omisión de `DocumentLayoutValidator`:** `pipeline_factory.py` no ejecuta la validación física (`core/layout/validator.py`)[cite: 5]. BoundingBoxes nulos o páginas fuera de rango ingresan al sistema sin filtrado *Fail-Fast*[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Incompatibilidad de Tipos por Duck-Typing:** `_adapter_mapper` inyecta instancias de `core.domain.document.LayoutBlock` en `LayoutBlockCollection`, cuya firma exige `core.layout.models.LayoutBlockDraft`[cite: 5]. La integración sobrevive accidentalmente en Python porque ambas clases comparten los nombres de atributos `content` y `bbox`, pero destruye el análisis de tipo estático (`pyright`) y colapsa ante validaciones de Pydantic v2[cite: 5].
  * **[DESACOPLAMIENTO P1 - ALTO] Hardcoding de Proveedor:** `pipeline_factory.py` fuerza `provider = PyMuPDFProvider()`, dejando inalcanzables en producción a `DoclingProvider` y `TesseractProvider`[cite: 5].

---

#### FASE 2: Materialización AST V2, Normalización, Segmentación y Enrutamiento
* **Entrada:** `LayoutBlockCollection`[cite: 5].
* **Canalización Teórica:** $\text{FlatASTBuilder} \rightarrow \text{CrossPageNormalizer} \rightarrow \text{NormalizationPipeline} \rightarrow \text{Segmenter V2} \rightarrow \text{RoutingWorkflow}$[cite: 5].
* **Flujo Físico Observado:**
  1. `FlatASTBuilder.build()` ejecuta la proyección y aplica de forma activa `CrossPageNormalizer.execute()`[cite: 5].
  2. `TranslationPipeline.execute()` (`core/pipeline/orchestrator.py`) recibe la secuencia de nodos[cite: 5].
  3. Realiza llamadas procedurales directas a clasificadores y enriquecedores[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[DEFECTO P1 - ALTO] Firma Criptográfica Prematura e Inestable:** `TranslationPipeline.execute()` invoca `compute_ast_hash(nodes)` **antes** de ejecutar `HierarchicalContextEnricher`[cite: 5]. El hash del trabajo (`job.ast_hash`) no captura la estructura enriquecida con tokens de contexto[cite: 5]. Además, `compute_ast_hash` (en `core/ast/hashing.py`) incluye el `node_id` efímero en la serialización JSON, haciendo que dos árboles con idéntico contenido tengan firmas distintas si cambian los IDs[cite: 5].
  * **[BYPASS P1 - ALTO] Cortocircuito del `NormalizationPipeline`:** `orchestrator.py` no utiliza la fachada `NormalizationPipeline` de `core/normalization/pipeline.py`[cite: 5]. Instancia in-line `SemanticNodeClassifier`, `StructuralAssetPlaceholder`, `ASTIntegrityValidator` y `HierarchicalContextEnricher`, rompiendo el patrón Facade y el principio OCP[cite: 5].
  * **[BYPASS P0 - CRÍTICO] Sub-sistema `Segmenter V2` 100% Zombi:** Todo el paquete `core/segmenter/*` (`SegmenterService`, `AtomicSegmenter`, `ParagraphSegmenter`, `ScientificBoundaryPolicy`) carece de importaciones en la orquestación[cite: 5]. Párrafos densos viajan completos sin dividirse en oraciones atómicas[cite: 5].
  * **[BYPASS P0 - CRÍTICO] Sub-sistema `RoutingWorkflow` 100% Zombi:** Las clases en `core/routing/*` y `core/pipeline/workflow.py` no son invocadas[cite: 5]. No existe filtrado de canales (`TRANSLATE`, `PASSTHROUGH`, `OMIT`), enviando todo el volumen directamente a los LLM[cite: 5].

---

#### FASE 3: Empaquetado de Tokens (Chunking)
* **Entrada:** Lista plana de `ASTNode` pre-segmentados[cite: 5].
* **Canalización Teórica:** $\text{ASTNode Sequence} \rightarrow \text{PolicyDrivenStreamingChunker}$[cite: 5].
* **Flujo Físico Observado:**
  1. `TranslationPipeline.execute()` invoca `self.chunker.chunk(nodes)`[cite: 5].
  2. En runtime, `self.chunker` es el `ChunkerProtocolAdapter` inyectado por `apps/cli/main.py`[cite: 5].
  3. El adaptador delega en la función `build_semantic_chunks_as_units()` en `core/ast/hashing.py`[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[BYPASS P0 - CRÍTICO] Sub-sistema `core/chunking/` 100% Zombi:** El motor formal de chunking orientado a objetos (`PolicyDrivenStreamingChunker` y `StructuralNodeAtomicityPolicy`) está completamente descalificado[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Contaminación Ontológica en `core/ast/hashing.py`:** La lógica de negocio de partición de texto, presupuestos de tokens (`ChunkPolicy`), división por oraciones (`_split_by_sentence`) e instanciación de `TranslationUnit` vive dentro de `hashing.py`[cite: 5]. Se secuestra un módulo de utilidades criptográficas para alojar la lógica de dominio principal[cite: 5].

---

#### FASE 4: Despacho Operacional, FinOps, Caché y Resiliencia
* **Entrada:** `TranslationUnit` Sequence[cite: 5].
* **Canalización Teórica:** $\text{TranslationUnit} \rightarrow \text{AsyncDispatcher} \rightarrow \text{ContextResolver} \rightarrow \text{PromptBuilder} \rightarrow \text{CachedLLMProvider} \rightarrow \text{RateLimitedProvider} \rightarrow \text{GlobalCircuitBreaker} \rightarrow \text{LLM Provider}$[cite: 5].
* **Flujo Físico Observado:**
  1. `AsyncDispatcher.dispatch()` orquesta las tareas asíncronamente[cite: 5].
  2. Enruta el prompt a través de `CachedLLMProvider` y `RateLimitedProvider`[cite: 5].
  3. Envía la solicitud HTTP a las APIs de Groq o Gemini[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[BYPASS P0 - CRÍTICO] Motor de Resiliencia `GlobalCircuitBreaker` 100% Zombi:** `core/resilience/circuit_breaker.py` no se instancía ni se inyecta en el despachador ni en los proveedores[cite: 5]. Si el proveedor remoto emite errores `500` masivos, el sistema no abre el circuito y continúa saturando la red con reintentos[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Bipolaridad del Plano de Ejecución:** `apps/cli/main.py` ejecuta el despacho *In-Process* en memoria mediante `asyncio.Semaphore`[cite: 5]. Paralelamente, `apps/llm_workers/__main__.py` opera el `LLMWorkerDaemon` en modo distribuido consultando la cola SQLite (`ControlPlaneRepository`)[cite: 5]. El modo CLI no pasa por CQRS ni por la FSM[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Invalidez de `QuotaManager` para Multi-Proceso:** `TokenBucket` almacena el contador de tokens y el tiempo de refresco en variables locales de memoria RAM (`self.tokens`)[cite: 5]. En un despliegue multi-nodo, los procesos no comparten cuotas, multiplicando el tráfico a las APIs y gatillando bloqueos `HTTP 429`[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Subestimación FinOps en Ecuaciones LaTeX:** `PromptBuilder` e `InferenceMeasurementService` emplean `FastWordEstimator`, el cual calcula tokens multiplicando palabras por $1.3$ (`split()`)[cite: 5]. Una ecuación LaTeX compleja de 1 palabra física equivale a 20+ tokens BPE reales[cite: 5]. La subestimación de un orden de magnitud causa desbordamientos de ventana `ContextOverflowError` en la API[cite: 5].
  * **[DEFECTO P1 - ALTO] Envenenamiento de Caché por `DummyContextResolver`:** `apps/cli/main.py` inyecta `DummyContextResolver` (`TODO_PHASE15`), el cual emite migas de pan nulas[cite: 5]. Se guardan en la caché SQLite (`materialized.db`) traducciones desprovistas de contexto jerárquico real[cite: 5].
  * **[DEFECTO P1 - ALTO] Inyección Mutativa Posterior:** `pipeline_factory.py` asigna los pipelines de validación y curación mediante mutación de atributos post-construcción (`dispatcher.validation_pipeline = ...`), violando el encapsulamiento inmutable[cite: 5].

---

#### FASE 5: Control de Calidad Post-Inferencia (Validación y Auto-Reparación)
* **Entrada:** Texto traducido emitido por el LLM (`InferenceResult`)[cite: 5].
* **Canalización Teórica:** $\text{LLM Output} \rightarrow \text{ValidationPipeline} \rightarrow (\text{Si HARD\_FAIL}) \rightarrow \text{HealingPipeline} \rightarrow \text{Revalidación Atómica}$[cite: 5].
* **Flujo Físico Observado:**
  1. `AsyncDispatcher._process_validation_and_healing()` recibe el resultado[cite: 5].
  2. Ejecuta `ValidationPipeline.validate_chunk(ctx)`[cite: 5].
  3. Si hay `HARD_FAIL`, invoca `HealingPipeline.heal_and_revalidate()`[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[DEMOSTRACIÓN POSITIVA SOTA] Rollback Atómico y Aborto Estricto:** Se constató que si el *healing* no logra corregir el error o revalida con un nuevo `HARD_FAIL`, se ejecuta un *rollback* atómico al texto original y `AsyncDispatcher` asigna `FailureReason.VALIDATION_FAILURE` al `ChunkOutcome`[cite: 5]. Dado que `VALIDATION_FAILURE` no es degradable en `AssemblyPolicy`, el `DocumentAssembler` **aborta el ensamblado del documento de forma correcta**[cite: 5].
  * **[FALSACIÓN DE HIPÓTESIS] Pureza de `ValidationPipeline`:** Se demostró que `ValidationPipeline` es un contenedor puro de texto (`StructuralValidator`, `PreservationValidator`, `PerimeterValidator`, `SemanticValidator`, `VolumetricValidator`)[cite: 5]. No ejecuta validadores del AST[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] `PolymorphicValidationEngine` Zombi:** El motor de validación estática de AST pre-inferencia (`core/validation/ast/engine.py`) no se invoca en el pipeline[cite: 5].
  * **[DEFECTO P2 - MEDIO] Disparo Monofoco y Doble Revalidación Redundante:** `AsyncDispatcher` solo envía el primer error (`hard_fails[0]`) al `HealingPipeline`[cite: 5]. Además, tras recibir la revalidación exitosa del *healing*, `AsyncDispatcher` ejecuta una segunda llamada redundante a `validate_chunk()`[cite: 5].
  * **[DEUDA P1 - ALTO] Inyección de `LegacyValidatorAdapter`:** La fábrica sigue inyectando el adaptador de las Fases 11 y 12 en el pipeline moderno[cite: 5].

---

#### FASE 6: Reconstrucción, Renderizado TeX y Compilación
* **Entrada:** Proyecciones almacenadas en el plano materializado[cite: 5].
* **Canalización Teórica:** $\text{DispatchResult} \rightarrow \text{CompilationService} \rightarrow \text{DocumentAssembler} \rightarrow \text{RenderUnitMapper} \rightarrow \text{TexBuilder} \rightarrow \text{DockerRunner} \rightarrow \text{PDF}$[cite: 5].
* **Flujo Físico Observado:**
  1. `AssemblerWorkerDaemon` (`apps/compiler/__main__.py`) despierta al detectar estado `READY_FOR_ASSEMBLY` en la FSM[cite: 5].
  2. Extrae las proyecciones desde `MaterializedPlaneRepository`[cite: 5].
  3. Invocación directa a `TexBuilder.build()` y `DockerRunner.compile()`[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[BYPASS P0 - CRÍTICO] Bypassing del Core de Compilación (`CompilationService` y `DocumentAssembler` Zombis):** `AssemblerWorkerDaemon` **jamás invoca a `CompilationService` ni a `DocumentAssembler`**[cite: 5]. Reconstruye los fragmentos manualmente en un bucle `for` directo desde la base de datos[cite: 5]. Las políticas de tolerancia a fallos (`AssemblyPolicy`), las reglas de degradación y la verificación de hashes SHA-256 quedan totalmente desactivadas en producción[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Inseguridad Concurrente y Race Conditions en `DockerRunner`:** `DockerRunner.compile()` (en `apps/compiler/docker_runner.py`) escribe los logs de choque `tectonic_crash.log` y el PDF compilado directamente en el directorio de trabajo actual (`os.getcwd()`)[cite: 5]. Trabajos concurrentes sobreescriben mutuamente sus archivos, corrompiendo la salida final[cite: 5].
  * **[DEFECTO P1 - ALTO] Falso "DockerRunner":** La clase no utiliza contenedores Docker; ejecuta el binario local `tectonic` mediante `subprocess.run` en the host[cite: 5].
  * **[DEFECTO P1 - ALTO] Escapador TeX Ciego al Contexto:** `LatexEscaper` realiza una traducción ciega de caracteres (`_`, `^`, `$`, `{`, `}`), corrompiendo comandos y fórmulas LaTeX legítimas dentro del texto[cite: 5].
  * **[DEFECTO P1 - ALTO] Pérdida de Semántica $N:1$:** `RenderUnitMapper` reduce $N$ nodos AST de un chunk a un único nodo primario, destruyendo la jerarquía de los elementos restantes[cite: 5].

---

#### FASE 7: Gobernanza Transaccional, FSM y Reconciliación CQRS
* **Entrada:** Comandos de estado de ejecución (`DocumentCommand`)[cite: 5].
* **Canalización Teórica:** $\text{StateStore} \rightarrow \text{DocumentCommandHandler} \rightarrow \text{FSMRepository} \rightarrow \text{EventPlane} \rightarrow \text{Reconciler}$[cite: 5].
* **Flujo Físico Observado:**
  1. `FSMStateStore.save()` traduce pasos del pipeline a comandos FSM[cite: 5].
  2. `DocumentCommandHandler.handle()` valida la transición vía `FSMValidator`[cite: 5].
  3. `FSMRepository.transition_to()` ejecuta la mutación atómica[cite: 5].
* **Análisis Forense de Bypasses y Fallas:**
  * **[DEMOSTRACIÓN POSITIVA SOTA] Exclusión Mutua Optimista (CAS) en FSM:** `FSMRepository.transition_to` utiliza Compare-And-Swap estricto apoyado en `state_version`[cite: 5]. Si dos trabajadores intentan modificar el estado simultáneamente, `rowcount == 0` dispara `OptimisticLockError`, garantizando aislamiento perfecto[cite: 5].
  * **[DEFECTO P2 - MEDIO] Transiciones Ocultas en `FSMStateStore`:** Para cubrir la falta de coincidencia entre los pasos del Job y la FSM, `FSMStateStore.save()` emite comandos sintéticos de "compilaciones fantasma" (`MarkAssemblyReadyCommand`, `StartCompilationCommand`) que el orquestador nunca ordenó, falseando la bitácora[cite: 5].
  * **[BYPASS P0 - CRÍTICO] Daemon de Reconciliación CQRS Desactivado:** `runtime/reconciliation.py` tiene la bandera hardcodeada `EXPERIMENTAL_ENABLED = False`[cite: 5]. El proceso de liberación de leases huérfanos y sanación de proyecciones está **$100\%$ inactivo**[cite: 5].
  * **[DEFECTO P0 - CRÍTICO] Bug de Inyección de Hash Desconocido en Re-materialización:** En `ReconciliationCommandHandler.handle_rematerialize()`, al rescatar un evento del WAL, inserta la proyección con el string literal `"unknown_ast_hash"`[cite: 5]. Cuando el ensamblador consulta la base con el `ast_hash` real, la lectura falla (*MISS*) y el documento queda ahorcado en estado `PROCESSING` para siempre[cite: 5].

---

## SECCIÓN 2 — PRODUCTION COMPOSITION MAP (0.4.5-2)

La mapa de composición revela que la arquitectura sufre de una **Raíz de Composición Dividida (*Split Composition Root*)**, violaciones de la Arquitectura Hexagonal por importaciones inversas desde `core/` hacia `infra/`, y la coexistencia de un orquestador sincrónico junto a un motor de runtime multihilo paralelo[cite: 5].

```text
[ CAPA DE ENTRADA / ENTRY POINTS ]
  ├── apps/cli/main.py (CLI interactivo / In-process Async)[cite: 5]
  ├── apps/compiler/__main__.py (Assembler Worker Daemon)[cite: 5]
  ├── apps/llm_workers/__main__.py (Distributed LLM Worker Daemon)[cite: 5]
  └── runtime/engine.py (Motor Monolítico Paralelo / Subproceso independiente)[cite: 5]
           │
           ▼
[ RAÍZ DE COMPOSICIÓN / COMPOSITION ROOT ]
  apps/bootstrap/pipeline_factory.py
  (Fallas: Tipado laxo 'dispatcher: Any'; Muta pipelines internamente post-instanciación;
   Rutas de conexión SQLite hardcodeadas "infra/db/...")[cite: 5]
           │
           ├───────────────────────────────────────────┐
           │ (Inyección de Interfaces / Protocols)     │ (Inyección de Adaptadores)
           ▼                                           ▼
[ SERVICIOS DE APLICACIÓN ]                   [ ADAPTADORES DE INFRAESTRUCTURA ]
  core/pipeline/orchestrator.py                 ├── infra/adapters/pdf_parser.py[cite: 5]
  (TranslationPipeline)                         ├── infra/db/document_repository.py[cite: 5]
  (Falla Hexagonal: Instancia in-line           ├── infra/db/fsm_repository.py[cite: 5]
   SemanticNodeClassifier,                      └── core/pipeline/state_store.py
   HierarchicalContextEnricher, etc.)[cite: 5]        (VIOLACIÓN HEXAGONAL DIRECTA:
                                                         Clase FSMStateStore en core/
                                                         importa FSMRepository de infra/)[cite: 5]
           │
           ▼
[ DOMINIO PURO / COMPONENTES ISOLADOS (ZOMBIS) ]
  ├── core/layout/builder.py (DocumentLayoutBuilder ZOMBI)[cite: 5]
  ├── core/segmenter/* (Segmenter V2 ZOMBI)[cite: 5]
  ├── core/routing/* & workflow.py (RoutingWorkflow ZOMBI)[cite: 5]
  ├── core/chunking/* (POO Chunker ZOMBI)[cite: 5]
  ├── core/resilience/circuit_breaker.py (GlobalCircuitBreaker ZOMBI)[cite: 5]
  ├── core/validation/ast/engine.py (PolymorphicValidationEngine ZOMBI)[cite: 5]
  └── core/compiler/service.py & assembler.py (Compilation Core ZOMBI en Daemon)[cite: 5]
```

---

## SECCIÓN 3 — PRODUCTION EVIDENCE MATRIX (0.4.5-3)

La siguiente matriz establece el estado de certificación real del sistema[cite: 5]. Se diferencia categóricamente entre la existencia de código fuente, la presencia de pruebas unitarias/integración y la **verificación empírica de ejecución en la canalización física de producción**[cite: 5].

| Capacidad Arquitectónica | Código Fuente Existente | Cobertura en Suite Test | Ejecución Real en Runtime | Veredicto de Certificación |
| :--- | :---: | :---: | :---: | :--- |
| **Physical Extraction** | `PyMuPDFProvider`[cite: 5] | `test_real_paper.py`[cite: 5] | **SÍ (PyMuPDF)**[cite: 5] | 🟢 **CERTIFICADO** (Motor hardcodeado)[cite: 5] |
| **Spatial 2D Layout** | `DocumentLayoutBuilder`[cite: 5] | `test_layout_validator.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO (Zombi 100%)**[cite: 5] |
| **AST V2 Materialization** | `FlatASTBuilder`[cite: 5] | `test_golden_parser.py`[cite: 5] | **SÍ (FlatAST)**[cite: 5] | 🟡 **ACEPTADO CON RESERVAS** (Duck-typing)[cite: 5] |
| **AST Cross-Page Normalization** | `CrossPageNormalizer`[cite: 5] | `test_ast.py`[cite: 5] | **SÍ**[cite: 5] | 🟢 **CERTIFICADO (SOTA)**[cite: 5] |
| **Sentence Segmentation** | `Segmenter V2` (`core/segmenter`)[cite: 5] | `test_ast.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO (Zombi 100%)**[cite: 5] |
| **Channel Routing** | `RoutingWorkflow` (`core/routing`)[cite: 5] | `test_routing.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO (Zombi 100%)**[cite: 5] |
| **POO Policy Chunking** | `PolicyDrivenStreamingChunker`[cite: 5] | `test_chunker_snapshot.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO** (Lógica en `hashing.py`)[cite: 5] |
| **LLM Dispatching** | `AsyncDispatcher`[cite: 5] | `test_dispatcher.py`[cite: 5] | **SÍ (Bipolar)**[cite: 5] | 🟡 **ACEPTADO CON RESERVAS** (Dualidad CLI/Daemon)[cite: 5] |
| **FinOps / Token Budgeting** | `PromptBudgetCalculator`[cite: 5] | `test_pricing_engine.py`[cite: 5] | **NO (INEXACTO)**[cite: 5] | 🔴 **NO CERTIFICADO** (Subestima LaTeX)[cite: 5] |
| **Rate Limiting** | `QuotaManager` / `TokenBucket`[cite: 5] | `test_rate_limiter.py`[cite: 5] | **SÍ (Local RAM)**[cite: 5] | 🔴 **NO CERTIFICADO** (Inviable en cluster)[cite: 5] |
| **Circuit Breaker Resilience** | `GlobalCircuitBreaker`[cite: 5] | `test_circuit_breaker.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO (Zombi 100%)**[cite: 5] |
| **Pre-LLM AST Validation** | `PolymorphicValidationEngine`[cite: 5] | `test_validation_pipeline.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO (Zombi 100%)**[cite: 5] |
| **Post-LLM Text Validation** | `ValidationPipeline`[cite: 5] | `test_validation_integration`[cite: 5] | **SÍ**[cite: 5] | 🟢 **CERTIFICADO** (Bloquea `HARD_FAILS`)[cite: 5] |
| **Auto-Healing & Rollback** | `HealingPipeline`[cite: 5] | `test_structural_healing.py`[cite: 5] | **SÍ (SOTA)**[cite: 5] | 🟢 **CERTIFICADO (SOTA)**[cite: 5] |
| **Document Assembly** | `DocumentAssembler`[cite: 5] | `test_assembler.py`[cite: 5] | **NO (BYPASSED)**[cite: 5] | 🔴 **NO CERTIFICADO** (Daemon arma ad-hoc)[cite: 5] |
| **TeX Rendering** | `TexBuilder` / `RenderContext`[cite: 5] | `test_assembler.py`[cite: 5] | **SÍ**[cite: 5] | 🟡 **ACEPTADO CON RESERVAS** (Escaper ciego)[cite: 5] |
| **PDF Compilation** | `DockerRunner` (Tectonic)[cite: 5] | `test_pipeline.py`[cite: 5] | **SÍ (Local Host)**[cite: 5] | 🔴 **NO CERTIFICADO** (Race condition I/O)[cite: 5] |
| **Atomic Serialization** | `infra/serialization/ast_json.py`[cite: 5] | `test_chunker_snapshot.py`[cite: 5] | **SÍ (SOTA)**[cite: 5] | 🟢 **CERTIFICADO (SOTA SRE)**[cite: 5] |
| **FSM State Locking (CAS)** | `FSMRepository.transition_to`[cite: 5] | `test_recovery_flow.py`[cite: 5] | **SÍ (SOTA)**[cite: 5] | 🟢 **CERTIFICADO (SOTA CAS)**[cite: 5] |
| **CQRS Reconciliation** | `CQRSReconciliationDaemon`[cite: 5] | `test_recovery_flow.py`[cite: 5] | **NO (DISABLED)**[cite: 5] | 🔴 **NO CERTIFICADO** (Bandera OFF / Bug Hash)[cite: 5] |

---

## SECCIÓN 4 — BENCHMARK VS. PRODUCTION BOUNDARY MAP (0.4.5-4)

La auditoría forense destapó el origen del malentendido metodológico inicial: **el laboratorio de evaluación (Benchmark) estaba midiendo un pipeline distinto al que corre en producción**[cite: 5].

```text
               ┌────────────────────────────────────────────────────────┐
               │                PRODUCTION PIPELINE                     │
               │ (Canalización transaccional real para documentos PDF)   │
               └───────┬────────────────────────────────────────┬───────┘
                       │                                        │
           (El pipeline pierde la                    (El chunker inyecta UUIDs
            geometría 2D por el bypass                efímeros alterando firmas
            de DocumentLayoutBuilder)[cite: 5]          en compute_ast_hash)[cite: 5]
                       │                                        │
                       ▼                                        ▼
               ┌───────────────┐                        ┌───────────────┐
               │ FlatASTBuilder│                        │  hashing.py   │
               └───────┬───────┘                        └───────┬───────┘
                       │                                        │
             (AST V2)  │    ┌───────────────────────────┐       │ (TranslationUnits)
                       ├────┤ BOUNDARY DE DESCONEXIÓN   ├───────┤
                       │    └───────────────────────────┘       │
                       ▼                                        ▼
               ┌────────────────────────────────────────────────────────┐
               │               BENCHMARK MINI-PIPELINE                  │
               │ (El entorno aséptico de evaluación topológica - F17)   │
               └───────┬───────────────────────────────┬────────────────┘
                       │                               │
            (Utiliza core/ast/parser.py           (Utiliza ASTFingerprintPolicy
             legacy con Regex Markdown,            que ignora node_id, esquivando 
             viciando la calibración)[cite: 5]   la fragilidad criptográfica)[cite: 5]
                       │                               │
                       ▼                               ▼
               ┌────────────────┐               ┌────────────────┐
               │    Metrics     │               │  Leaderboard   │
               └────────────────┘               └────────────────┘
```

---

### DIAGNÓSTICO DE LA FRONTERA BENCHMARK VS. PRODUCCIÓN
1. **Ruta Paralela Tóxica en Benchmark:** `core/benchmark/__main__.py` ejecuta `parse_pdf()` de `core/ast/parser.py`, el cual corta el texto mediante el parser legacy de expresiones regulares de Markdown (`MarkdownSegmenter`)[cite: 5]. El Benchmark no evaluaba el AST V2 de producción (`PdfParserAdapter` $\rightarrow$ `DocumentLayout` $\rightarrow$ `FlatASTBuilder`)[cite: 5]. Las métricas históricas publicadas por el laboratorio sobre precisión topológica y densidad eran académicamente inválidas para el runtime real[cite: 5].
2. **Esquiva de Fragilidad Criptográfica:** El benchmark de `tools/evaluation/` utilizaba `ASTFingerprintPolicy.semantic_fingerprint()`, comparando únicamente `(node_type, content)` y omitiendo el `node_id`[cite: 5]. Esto permitió que el benchmark funcionara limpiamente, ocultando el bug de `compute_ast_hash()` (en `hashing.py`), el cual acopla `node_id` efímeros rompiendo el determinismo en el orquestador real[cite: 5].
3. **Mandato de Remediación:** Para el Hito 0.5, se exige que el Benchmark se alimente exclusivamente de la salida de `PdfParserAdapter` y `FlatASTBuilder`, eliminando por completo `core/ast/parser.py`[cite: 5].

---

## CONCLUYENTE FINAL Y DISPOSICIÓN PARA HITO 0.5

El **Hito 0.4.5 (Production Pipeline & Runtime Boundary Audit)** queda oficialmente **CERRADO Y CONGELADO (`FROZEN`)**[cite: 5].

El sistema ha sido desnudado analíticamente. Se han identificado sus componentes excepcionales SOTA (Sutura trans-página, Auto-healing con rollback, Serialización atómica SRE y FSM con CAS)[cite: 5] y se ha confeccionado el backlog ineludible de remediación para saneamiento de zombis, bypasses y race conditions[cite: 5].

El proyecto está formalmente habilitado para avanzar al **Hito 0.5: Decision Consolidation & Architecture Freeze Proposal**, donde se consolidarán las decisiones arquitectónicas definitivas (`KEEP`, `EXTEND`, `REPLACE`, `DEPRECATE`) para la firma del **ADR_F17-BIS (Maestro)**[cite: 5].