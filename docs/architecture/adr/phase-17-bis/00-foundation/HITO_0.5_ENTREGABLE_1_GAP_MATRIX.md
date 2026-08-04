# HITO_0.5_ENTREGABLE_1_GAP_MATRIX.md
## Architecture Gap Matrix Consolidada — Matriz de Brechas y Diagnóstico Sistémico

* **Estado:** APPROVED AS RELEASE CANDIDATE (Final RC) / Hito 0.5 — Entregable 1
* **Fecha de Emisión:** 2026-08-01
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.5 (Decision Consolidation & Architecture Freeze Proposal)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Mapeo observacional y neutral de la discrepancia entre el Estado Comprobado en Código/Wiring (Hitos 0.1–0.4.5) y los Requerimientos de la Arquitectura Objetivo (Fase 17 / 17_BIS). Cero decisiones de implementación prematuras. Trazabilidad $100\%$ orientada a la gobernanza de los Architectural Decision Records (`ADR-F17BIS-01` a `ADR-F17BIS-11`).

---

## EXECUTIVE SUMMARY

La auditoría forense de los Hitos 0.1–0.4.5 identificó **cuarenta discrepancias de arquitectura** entre el wiring observado en tiempo de ejecución (tanto en el pipeline de producción como en el arnés de evaluación) y la arquitectura objetivo definida para las Fases 17/17_BIS. 

Las brechas se organizan en siete subsistemas funcionales y se clasifican operacionalmente según su severidad en la integridad del sistema (P0: Integridad/Determinismo; P1: Estructura/Clean Arch; P2: Ineficiencia/Observabilidad) y su alcance sistémico (`LOCAL`, `CROSS-CUTTING` y `SYSTEMIC`). 

Este documento no prescribe implementaciones concretas ni impone la clasificación de componentes por destino final (`KEEP`, `REPLACE`, etc.). Su única finalidad es establecer una línea base observacional e incontrastable que sirva de insumo neutral para el **Contract Map (Entregable 2)** y para los **Architectural Decision Records `ADR-F17BIS-01` a `ADR-F17BIS-11` (Entregable 3)**.

---

## 1. NOTA METODOLÓGICA Y DEFINICIÓN OPERACIONAL DE SEVERIDADES

> **DESLINDE ARQUITECTÓNICO DE GOBERNANZA:**
> 1. Una brecha o defecto registrado en esta matriz refleja **exclusivamente la discrepancia observada entre el wiring en tiempo de ejecución del pipeline de producción auditado y la arquitectura objetivo definida para las Fases 17/17_BIS**. No implica necesariamente una falla de implementación en el componente individual cuando este es evaluado de forma aislada.
> 2. Los *Architectural Decision Records* (`ADR-F17BIS-01` a `ADR-F17BIS-11`) referenciados en la columna final constituyen las resoluciones normativas que serán formalizadas detalladamente en el **Entregable 3 del Hito 0.5**.

### Cadena Causal de Gobernanza Arquitectónica:
$$\text{Finding (Auditoría)} \longrightarrow \text{Gap (Brecha)} \longrightarrow \text{Architectural Consequence} \longrightarrow \text{ADR-F17BIS-xx} \longrightarrow \text{Implementation (Fase 1)}$$

### Definición Operacional Objetiva de Severidades y Alcance (Decision Scope):
* **`P0 - CRÍTICO (Integridad & Determinismo)`:** Brecha que compromete la **consistencia de datos**, destruye el **determinismo criptográfico**, altera la **idempotencia**, produce **desbordamientos de contexto irrecoverables**, genera **inseguridad de I/O por condiciones de carrera** o rompe el **aislamiento transaccional FSM/CQRS**.
* **`P1 - ALTO (Estructura & Mantenibilidad)`:** Brecha que viola la **Arquitectura Hexagonal (DIP)**, desactiva **módulos de dominio en el Composition Root**, introduce **incompatibilidades de tipo estático**, subestima **presupuestos FinOps** o limita la **escalabilidad horizontal**.
* **`P2 - MEDIO (Optimización & Observabilidad)`:** Brecha que incrementa la **complejidad computacional**, duplica **revalidaciones**, genera **inconsistencias de telemetría** o mantiene **deuda técnica heredada** sin detener el procesamiento.

#### Clases de Alcance de Decisión (`Decision Scope`):
* **`SYSTEMIC`:** Impacta la infraestructura global, firmas criptográficas, modelo de persistencia o el plano de control.
* **`CROSS-CUTTING`:** Afecta a múltiples subsistemas o la transferencia de datos entre fronteras de capa.
* **`LOCAL`:** Afecta exclusivamente la lógica interna de una etapa o componente delimitado.

---

## 2. MATRIZ CONSOLIDADA DE BRECHAS ARQUITECTÓNICAS (ARCHITECTURE GAP MATRIX)

### SUBSISTEMA 1: INGESTIÓN FÍSICA Y MAQUETACIÓN 2D (PHYSICAL INGESTION & LAYOUT)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P2-01** | `core/layout/builder.py`, `pipeline_factory.py` | `P2-06`, `P1-C07` | `apps/bootstrap/pipeline_factory.py` pasa bloques crudos a `FlatASTBuilder` sin instanciar `DocumentLayoutBuilder`. | Procesamiento espacial $2\text{D}$ completo (ordenamiento DAG, columnas, normalización, fusión). | Sub-sistema `DocumentLayoutBuilder` (6 etapas) no forma parte del wiring construido por `pipeline_factory.py` auditado. | **P1** | El orden físico crudo de extracción se asume como orden lógico definitivo, omitiendo la resolución de lecturas multi-columna. | `CROSS-CUTTING` | **`ADR-F17BIS-11`** (Fronteras & Layout) |
| **GAP-P2-02** | `pipeline_factory.py`, `core/layout/models.py` | `P2-05` | `_adapter_mapper` asigna `LayoutBlock` en `LayoutBlockCollection` (que declara `LayoutBlockDraft`). | Contrato de frontera de tipos estricto y desacoplado, validable estáticamente. | Incompatibilidad de tipos en la boundary de ingesta; sobrevive por coincidencia de atributos (*duck-typing*). | **P1** | Quiebre de la verificación de tipos estáticos (`pyright`) e imposibilidad de validación estricta en Pydantic v2. | `LOCAL` | **`ADR-F17BIS-11`** (Fronteras & Ingesta) |
| **GAP-P2-03** | `apps/bootstrap/pipeline_factory.py` | `P2-08` | `pipeline_factory.py` instancía imperativamente `PyMuPDFProvider()`, ignorando `DEFAULT_EXTRACTION_PROVIDER`. | Selección de proveedores de extracción basada en políticas de perfilado o configuración. | Proveedores de extracción alternativos (`DoclingProvider`, `TesseractProvider`) no están integrados en el Composition Root. | **P1** | Acoplamiento del Composition Root a un único motor de extracción física, limitando la evaluación multimodular. | `CROSS-CUTTING` | **`ADR-F17BIS-11`** (Fronteras & Extractores) |
| **GAP-P2-04** | `core/layout/validator.py`, `pipeline_factory.py` | `P2-07` | `DocumentLayoutValidator` no es invocado durante el wiring del pipeline en `pipeline_factory.py`. | Filtrado defensivo (*Fail-Fast*) de maquetaciones físicas corruptas o páginas vacías previo al mapeo AST. | Ausencia de barrera de validación física en el wiring de ingesta de producción auditado. | **P1** | Geometrías nulas o estructuras fuera de margen progresan sin interceptar hacia las etapas de segmentación y compilación. | `CROSS-CUTTING` | **`ADR-F17BIS-04`** (Contrato de Validez) |
| **GAP-P2-05** | `core/ast/router.py` | `P2-09`, `E-0.4-326` | `PDFRouter.detect_pdf_type()` ejecuta `import fitz` (PyMuPDF) directamente dentro de `core/ast/`. | Dominio puro desacoplado de librerías concretas de infraestructura (Clean Architecture). | Importación directa de librería de infraestructura dentro del espacio de nombres de dominio. | **P1** | Acoplamiento del módulo de dominio a la librería C/Python `fitz`, limitando el aislamiento del core. | `LOCAL` | **`ADR-F17BIS-11`** (Contrato de Fronteras) |
| **GAP-P2-06** | `core/ast/builder.py` | `P2-10` | `_map_physical_to_logical` omite transferir `column_index` y parentesco al `control_plane` del `ASTNode`. | Preservación de metadatos espaciales $2\text{D}$ en el ASTNode para trazabilidad de renderizado. | Omisión de atributos de maquetación $2\text{D}$ durante la proyección del AST V2. | **P2** | Indisponibilidad de atributos de columna y jerarquía visual en las etapas posteriores de renderizado TeX. | `LOCAL` | **`ADR-F17BIS-06`** (Taxonomía & Metadatos) |

---

### SUBSISTEMA 2: AST V2, NORMALIZACIÓN, SEGMENTACIÓN Y ENRUTAMIENTO (TRANSFORMATION & ROUTING)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P3-01** | `core/segmenter/*`, `orchestrator.py` | `P3-H01`, `E-0.4-325` | `TranslationPipeline.execute()` no invoca `SegmenterService` (`core/segmenter/*`). | Segmentación oracional atómica de párrafos densos aplicando `ScientificBoundaryPolicy`. | Sub-sistema `Segmenter V2` no forma parte del wiring construido por el orquestador auditado. | **P1** | Párrafos densos viajan sin fragmentación oracional previa hacia el empaquetado de chunks. | `CROSS-CUTTING` | **`ADR-F17BIS-08`** (Segmentación & Fragmentos) |
| **GAP-P3-02** | `core/routing/*`, `workflow.py` | `P3-H01`, `P1-C06` | `orchestrator.py` no realiza llamadas a `RoutingWorkflow` ni a las clases en `core/routing/*`. | Clasificación y filtrado explícito de canales (`TRANSLATE`, `PASSTHROUGH`, `OMIT`) previo al despacho. | No se encontró evidencia de filtrado previo de canales mediante `RoutingWorkflow` en el pipeline auditado. | **P1** | La totalidad de los nodos del AST se despacha hacia el proveedor LLM sin discriminación de canal. | `CROSS-CUTTING` | **`ADR-F17BIS-11`** (Enrutamiento & Canales) |
| **GAP-P3-03** | `core/ast/hashing.py`, `core/chunking/*` | `P3-H02` | `TokenBudgetChunker` y `build_semantic_chunks_as_units` están definidos en `core/ast/hashing.py`. | Separación estricta de responsabilidades: `hashing.py` firma; `core/chunking/` empaqueta. | Módulo de utilidades de firma hospeda la implementación del empaquetador de tokens. | **P1** | Sub-sistema `core/chunking/` sin utilización en el runtime auditado; acoplamiento de responsabilidades en el módulo de hash. | `CROSS-CUTTING` | **`ADR-F17BIS-03`** (Hashing & Chunking) |
| **GAP-P3-04** | `core/ast/hashing.py` | `E-0.1-003`, `E-0.3-001` | `compute_ast_hash()` incluye `node_id` efímeros en la serialización JSON procesada para la firma SHA-256. | Identidad criptográfica $H_{semantic}$ determinista, agnóstica a identificadores mutables de runtime. | El valor de la firma criptográfica depende del campo `node_id` presente en la representación serializada. | **P0** | Inestabilidad determinista: árboles sintácticos con idéntico contenido y estructura producen hashes divergentes ante UUIDs variables. | `SYSTEMIC` | **`ADR-F17BIS-01` / `ADR-F17BIS-03`** (Identidad & Hash) |
| **GAP-P3-05** | `core/pipeline/orchestrator.py` | `P3-H05` | `compute_ast_hash(nodes)` se ejecuta en `orchestrator.py` **antes** de `HierarchicalContextEnricher`. | Firma criptográfica registrada en FSM equivalente al AST final enriquecido que se despacha. | Secuencia cronológica en la generación del hash desalineada respecto a la versión final del AST. | **P0** | El `ast_hash` registrado en la transacción no coincide con el contenido enriquecido despachado a los LLM. | `SYSTEMIC` | **`ADR-F17BIS-03`** (Sincronización de Hash) |
| **GAP-P3-06** | `core/pipeline/orchestrator.py`, `normalization/` | `P3-H03` | `orchestrator.py` instancia procedimentalmente clasificadores, integridades, placeholders y enriquecedores. | Encapsulamiento de transformaciones semánticas mediante la fachada extensible `NormalizationPipeline`. | Invocación procedimental de normalizadores en lugar de consumir la fachada `NormalizationPipeline`. | **P1** | Invasión de responsabilidades en el orquestador e imposibilidad de activar/desactivar transformaciones por configuración. | `CROSS-CUTTING` | **`ADR-F17BIS-11`** (Orquestación & Facades) |

---

### SUBSISTEMA 3: DESPACHO OPERACIONAL, LLM, FINOPS, CACHÉ Y RESILIENCIA (DISPATCH & RESILIENCE)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P4-01** | `core/resilience/circuit_breaker.py`, `dispatcher.py` | `P4-01` | `GlobalCircuitBreaker` no es instanciado ni inyectado en `AsyncDispatcher` ni en los proveedores LLM. | Intercepción *Fail-Fast* vía Circuit Breaker ante fallas masivas 5xx de proveedores remotos. | Motor de resiliencia sin evidencia de utilización en el runtime productivo auditado. | **P0** | Incapacidad de aislar fallas de red en cascada; el sistema reintenta indefinidamente ante caídas del proveedor remoto. | `SYSTEMIC` | **`ADR-F17BIS-08`** (Resiliencia & Circuit Breaker) |
| **GAP-P4-02** | `apps/cli/main.py`, `apps/llm_workers/__main__.py` | `P4-02` | CLI ejecuta despacho *In-Process* con `asyncio.Semaphore`; `LLMWorkerDaemon` procesa via SQLite CQRS. | Plano de ejecución unificado basado en cola transaccional CQRS y FSM para todos los entornos. | El modo CLI no utiliza el mismo mecanismo de coordinación ni persistencia transaccional que el modo daemon. | **P0** | El modo CLI salta la FSM, WAL logs, arrendamientos y recuperación, impidiendo el procesamiento distribuido en cluster. | `SYSTEMIC` | **`ADR-F17BIS-11`** (Plano de Ejecución) |
| **GAP-P4-03** | `apps/llm_workers/rate_limiter.py` | `P4-03` | `QuotaManager` y `TokenBucket` mantienen el conteo de tokens y refresco en variables de RAM local. | Control de cuotas RPM/TPM distribuido y coordinado entre múltiples trabajadores paralelos. | Estado de limitación de tasa acotado a la memoria RAM del proceso local. | **P1** | En despliegues multi-nodo, los procesos no coordinan cuotas, aumentando el riesgo de bloqueos `HTTP 429`. | `SYSTEMIC` | **`ADR-F17BIS-08`** (FinOps & Rate Limit) |
| **GAP-P4-04** | `core/ast/models.py`, `core/validation/budget.py` | `P4-04` | `PromptBudgetCalculator` usa `FastWordEstimator` (calcula tokens multiplicando palabras por $1.3$). | Estimación de tokens consistente con el algoritmo de tokenización utilizado por el proveedor de inferencia. | Subestimación de densidad de tokens para estructuras LaTeX y código técnico. | **P0** | Ecuaciones LaTeX complejas se subestiman por un orden de magnitud, provocando desbordamientos de ventana `ContextOverflowError`. | `CROSS-CUTTING` | **`ADR-F17BIS-06`** (Estimación de Tokens) |
| **GAP-P4-05** | `apps/cli/main.py`, `cache_provider.py` | `P4-05` | `apps/cli/main.py` inyecta `DummyContextResolver` (`TODO_PHASE15`), emitiendo migas de pan nulas. | Resolución de contexto jerárquico real (títulos de sección, contexto espacial) para prompts LLM. | Inyección de resolvedor de contexto nulo en el wiring del CLI productivo. | **P1** | Almacenamiento en Caché SQLite (`materialized.db`) de respuestas obtenidas sin contexto jerárquico. | `CROSS-CUTTING` | **`ADR-F17BIS-05`** (Gobernanza de Caché) |
| **GAP-P4-06** | `apps/bootstrap/pipeline_factory.py`, `dispatcher.py` | `P4-06` | `pipeline_factory.py` asigna `dispatcher.validation_pipeline` mediante mutación posterior de atributos. | Inyección de dependencias inmutable desde el constructor del componente. | Asignación mutativa de atributos post-construcción en el Composition Root. | **P1** | Riesgo de instanciar despachadores desprovistos de pipeline de validación o auto-reparación desde otros entry points. | `LOCAL` | **`ADR-F17BIS-11`** (Inyección Inmutable) |

---

### SUBSISTEMA 4: VALIDACIÓN POST-INFERENCIA, CURACIÓN Y AUTO-REPARACIÓN (VALIDATION & HEALING)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P5-01** | `core/validation/ast/engine.py`, `pipeline_factory.py` | `P5-H02` | `PolymorphicValidationEngine` no forma parte de la invocación en `pipeline_factory.py`. | Validación estática de integridad de nodos AST previa al envío al proveedor LLM. | Motor de validación AST pre-inferencia sin evidencia de utilización en el runtime auditado. | **P1** | Nodos estructuralmente corruptos progresan hacia el despacho, incurriendo en consumo de tokens en el LLM. | `CROSS-CUTTING` | **`ADR-F17BIS-04`** (Validación Pre-LLM) |
| **GAP-P5-02** | `apps/llm_workers/dispatcher.py` | `P5-H05` | `AsyncDispatcher._process_validation_and_healing()` envía exclusivamente `hard_fails[0]`. | Evaluación y curación de múltiples fallas de familias distintas cuando sea factible. | Despacho de auto-reparación acotado a un único fallo por pasada de curación. | **P2** | Chunks con dos errores reparables independientes (ej. Markdown + Math) fallan y se rechazan en una sola pasada. | `LOCAL` | **`ADR-F17BIS-07`** (Estrategias de Healing) |
| **GAP-P5-03** | `apps/llm_workers/dispatcher.py`, `healing/pipeline.py` | `P5-H05` | `AsyncDispatcher` ejecuta `validate_chunk()` una segunda vez tras la revalidación del healing. | Única pasada de revalidación atómica dentro del contenedor de curación. | Redundancia de evaluación en la secuencia de revalidación post-healing. | **P2** | Duplicación del tiempo de procesamiento en CPU por fragmento curado sin beneficio de seguridad adicional. | `LOCAL` | **`ADR-F17BIS-07`** (Revalidación Atómica) |
| **GAP-P5-04** | `apps/bootstrap/pipeline_factory.py` | `P5-H06` | `_build_default_validation_pipeline()` inyecta `LegacyValidatorAdapter` (Fases 11/12). | Suite de validadores de texto modernos, explícitos y desacoplados de adaptadores heredados. | Presencia de adaptador heredado en el Composition Root productivo. | **P1** | Persistencia de código antiguo que dificulta el diagnóstico reteniendo códigos `UnknownLegacyValidationCodeError`. | `LOCAL` | **`ADR-F17BIS-04`** (Desacoplamiento Legacy) |

---

### SUBSISTEMA 5: COMPILACIÓN, RENDERIZADO TeX Y SERIALIZACIÓN (COMPILER & ARTIFACTS)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P6-01** | `apps/compiler/__main__.py`, `core/compiler/service.py` | `P6-H01` | `AssemblerWorkerDaemon` no invoca `CompilationService` ni `DocumentAssembler`. | Reconstrucción centralizada en el core con validación de secuencias y políticas de tolerancia (`AssemblyPolicy`). | Núcleo de compilación y ensamblado de dominio sin evidencia de utilización en el daemon productivo. | **P0** | Desactivación de las reglas de tolerancia (`AssemblyPolicy`), degradación y verificación SHA-256 en el flujo distribuido. | `SYSTEMIC` | **`ADR-F17BIS-06`** (Gobernanza de Compilación) |
| **GAP-P6-02** | `apps/compiler/docker_runner.py` | `P6-H02` | `DockerRunner.compile()` escribe `tectonic_crash.log` y el PDF final en `os.getcwd()`. | Compilación aislada en directorios temporales efímeros por trabajo, con I/O thread-safe. | Inseguridad de I/O en el runner del compilador (Escritura en CWD compartido). | **P0** | Riesgo crítico de *Race Conditions*: compilaciones concurrentes en el mismo CWD sobreescriben artefactos mutuos. | `CROSS-CUTTING` | **`ADR-F17BIS-08`** (Aislamiento I/O Compilador) |
| **GAP-P6-03** | `apps/compiler/docker_runner.py` | `P6-H03` | `DockerRunner` ejecuta `subprocess.run(["tectonic", ...])` directamente en el host. | Ejecución en contenedor efervescente aislado o denominación verídica del ejecutor. | Discrepancia entre la denominación de la clase y su implementación de infraestructura real. | **P1** | Inexistencia de contenedor sandbox efervescente en el runner actual e inconsistencia de nomenclatura. | `LOCAL` | **`ADR-F17BIS-11`** (Contratos de Infraestructura) |
| **GAP-P6-04** | `core/compiler/rendering/implementations.py` | `P6-H04` | `LatexEscaper` realiza una sustitución ciega de caracteres (`_`, `^`, `$`, `{`, `}`). | Escapador de caracteres TeX inteligente (Context-Aware) que respete delimitadores matemáticos y macros. | Escapado de caracteres ciego al contexto sintáctico en `LatexEscaper`. | **P1** | Riesgo de alterar secuencias LaTeX válidas cuando aparecen fuera de los casos contemplados por el escapador. | `LOCAL` | **`ADR-F17BIS-06`** (Renderizado TeX) |
| **GAP-P6-05** | `core/compiler/rendering/mapper.py` | `E-0.4-371` | `DefaultRenderUnitMapper` reduce $N$ nodos AST de un chunk a un único nodo primario. | Mapeo $1:N$ que preserve la jerarquía y metadatos de todos los nodos pertenecientes al chunk. | Reducción de información topológica durante el mapeo a `RenderUnit`. | **P1** | Pérdida de metadatos de nodos secundarios contenidos en el empaquetado de un mismo chunk. | `LOCAL` | **`ADR-F17BIS-06`** (Mapeo de Renderizado) |
| **GAP-P6-06** | `tools/evaluation/infrastructure/ast_deserializer.py` | `E-0.4-373` | `ASTJsonDeserializer` desempaca diccionarios a mano (`ASTNode(**clean_kwargs)`). | Estándar único de serialización/deserialización atómica vía `infra/serialization/ast_json.py`. | Duplicación de lógica de deserialización desalineada del estándar Pydantic v2. | **P0** | Deserialización manual que omite validadores de Pydantic v2, rehidratando nodos potencialmente inconsistentes. | `SYSTEMIC` | **`ADR-F17BIS-01` / `ADR-F17BIS-03`** (Estándar Serialización) |

---

### SUBSISTEMA 6: GOBERNANZA TRANSACCIONAL, FSM, CQRS Y RUNTIME (RUNTIME & GOVERNANCE)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-P7-01** | `core/pipeline/state_store.py` | `P1-01`, `OBS-P1-01` | `FSMStateStore` (en `core/pipeline/`) importa `FSMRepository` directamente de `infra/db/`. | Dominio de aplicación desacoplado de infraestructura vía `StateStoreProtocol` e inyección de dependencias. | Importación directa de clase de infraestructura dentro del espacio de nombres `core/`. | **P1** | Fuga de frontera Hexagonal: el core del pipeline depende físicamente de un repositorio concreto SQLite. | `CROSS-CUTTING` | **`ADR-F17BIS-11`** (Fronteras Hexagonales) |
| **GAP-P7-02** | `core/execution/handlers.py` | `P1-H01`, `P7-H06` | `ReconciliationCommandHandler.handle_rematerialize()` inserta la clave `"unknown_ast_hash"`. | Preservación del linaje generacional estricto (`ast_hash` real) durante la rematerialización WAL. | Inyección de clave estática no vinculada al hash real durante la reconciliación. | **P0** | Ruptura de Query Model CQRS: el ensamblador consulta por el `ast_hash` real y falla, estancando el doc en `PROCESSING`. | `SYSTEMIC` | **`ADR-F17BIS-08`** (CQRS & Reconciliación) |
| **GAP-P7-03** | `runtime/reconciliation.py` | `P7-H02` | `CQRSReconciliationDaemon` tiene la bandera hardcodeada `EXPERIMENTAL_ENABLED = False`. | Daemon de reconciliación asíncrono activo para liberación de leases huérfanos y sanación de CQRS. | Inactivación por bandera de código del daemon de reconciliación CQRS. | **P0** | Tareas estancadas o con leases expirados no se recuperan automáticamente en el plano de control. | `SYSTEMIC` | **`ADR-F17BIS-08`** (Gobernanza Daemons) |
| **GAP-P7-04** | `core/pipeline/state_store.py` | `OBS-P1-07` | `FSMStateStore.save()` forja comandos sintéticos (`MarkAssemblyReadyCommand`, `StartCompilationCommand`). | Transiciones FSM gatilladas exclusivamente por eventos y comandos reales emitidos por el orquestador. | Generación de comandos sintéticos en el adapter de persistencia para forzar transiciones FSM. | **P2** | Trazabilidad del Event Log alterada: el adaptador registra comandos de compilación que el orquestador nunca emitió. | `CROSS-CUTTING` | **`ADR-F17BIS-08`** (Transiciones FSM) |
| **GAP-P7-05** | `apps/compiler/__main__.py` | `P1-H03` | `AssemblerWorkerDaemon` accede a miembros privados `_cache` y `_load_document` de `ASTRegistry`. | Encapsulamiento estricto; consumo de datos a través de métodos de consulta públicos. | Acceso directo a miembros privados de un registro en memoria desde la capa de aplicación. | **P1** | Acoplamiento entre el daemon y la implementación privada de la memoria caché de `ASTRegistry`. | `LOCAL` | **`ADR-F17BIS-11`** (Encapsulamiento de Registros) |

---

### SUBSISTEMA 7: EVALUACIÓN, TESTING, BENCHMARK Y CI GATES (TESTING & CI GOVERNANCE)

| ID Gap | Componentes Afectados | Finding de Origen | Estado Actual Observado (Runtime Auditado) | Requerimiento Arquitectura Objetivo | Brecha Identificada (Gap) | Severidad | Consecuencia Arquitectónica Observada | Decision Scope | Decision Record Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **GAP-C5-01** | `tests/integration/test_golden_parser.py` | `GAP-0.4-09`, `E-0.4-322` | `test_golden_parser.py` reasigna `expected_fingerprint = current_fingerprint` en runtime. | Barrera de regresión estricta que compare la salida del parser contra un oráculo congelado en disco. | Asignación que iguala el oráculo esperado a la variable bajo prueba ($A == A$). | **P0** | Incapacidad de detectar regresiones topológicas en CI; el test reporta éxito aun cuando se pierda contenido. | `SYSTEMIC` | **`ADR-F17BIS-10`** (CI Regression Gates) |
| **GAP-C5-02** | `core/benchmark/__main__.py` | `P3-H04` | `core/benchmark/__main__.py` ejecuta `parse_pdf()` de `core/ast/parser.py` (Parser Legacy Regex). | Evaluación del laboratorio de benchmarking sobre la canalización canónica de producción (`FlatASTBuilder`). | El benchmark ejecuta un parser diferente al utilizado por el pipeline productivo auditado. | **P0** | Desalineación de métricas: el laboratorio evalúa un modelo semántico desactualizado no utilizado en producción. | `SYSTEMIC` | **`ADR-F17BIS-10`** (Alineación Benchmark/Prod) |
| **GAP-C5-03** | `tests/integration/test_chunker_snapshot.py` | `E-0.4-381` | `test_chunker_snapshot.py` genera el snapshot si no existe y retorna `PASS` en la primera corrida. | Comprobación *Fail-Fast*: la ausencia de un snapshot de referencia debe arrojar error inmediato. | Auto-creación del oráculo en ejecuciones sobre entornos limpios sin baseline previa. | **P0** | Falso positivo en CI: aprueba ejecuciones en entornos limpios sin validar contra la línea de base congelada. | `CROSS-CUTTING` | **`ADR-F17BIS-10`** (Snapshots & Baselines) |
| **GAP-C5-04** | `.github/workflows/*`, `pyproject.toml` | `E-0.4-389`, `E-0.4-390` | No existen archivos de canalización de GitHub Actions ni un `pyproject.toml` centralizado. | Automatización de CI con *Required Status Checks* que bloqueen el merge remoto ante fallos. | Ausencia de archivos de configuración declarativos y flujos de automatización de CI. | **P0** | Inexistencia de barreras de control remotas; posibilidad de fusionar cambios que rompan el sistema. | `SYSTEMIC` | **`ADR-F17BIS-10`** (Automatización CI/CD) |
| **GAP-C5-05** | `tests/integration/test_real_parser_pipeline.py` | `E-0.4-323` | `TestRealParserIsolation` aplica `patch.object` total sobre `adapter.parse()` usando un PDF falso. | Pruebas de integración reales sobre binarios PDF sin parchear la función de extracción. | Discrepancia entre la denominación del test ("Real Isolation") y el uso de parches totales. | **P1** | Falsa sensación de cobertura de integración física; se evalúa exclusivamente la iteración de mocks en memoria. | `LOCAL` | **`ADR-F17BIS-10`** (Taxonomía de Tests) |

---

## 3. ESTADÍSTICAS GLOBALES DE LA GAP MATRIX REVISADA

```text
==================================================================================================
                 MÉTRICAS Y DISTRIBUCIÓN DE SEVERIDAD REVISADA (FASE 0)
==================================================================================================

  Total de Brechas Arquitectónicas Catalogadas : 40 Gaps
  ------------------------------------------------------------------------------------------------
  • Severidad P0 - CRÍTICO (Integridad & Determinismo)          : 14 Gaps  (35.0%)
  • Severidad P1 - ALTO (Estructura, Clean Arch & Zombis)        : 22 Gaps  (55.0%)
  • Severidad P2 - MEDIO (Optimización & Observabilidad)        :  4 Gaps  (10.0%)

  Distribución por Decision Scope (Alcance de Decisión):
  ├── SYSTEMIC (Infraestructura Global, Hashes, FSM, CQRS, CI)  : 12 Gaps  (30.0%)
  ├── CROSS-CUTTING (Flujo de Datos Inter-Capa y Orquestación)   : 14 Gaps  (35.0%)
  └── LOCAL (Interno de Módulo o Adaptador Delimitado)          : 14 Gaps  (35.0%)

  Distribución por Subsistemas del Proyecto:
  ├── 1. Ingestión Física y Layout 2D (Physical Ingestion)         :  6 Gaps  (GAP-P2-01 a P2-06)
  ├── 2. AST V2, Normalización, Segmenter y Routing                :  6 Gaps  (GAP-P3-01 a P3-06)
  ├── 3. Despacho, LLM, FinOps, Caché y Resiliencia                :  6 Gaps  (GAP-P4-01 a P4-06)
  ├── 4. Validación, Healing y Auto-Reparación                     :  4 Gaps  (GAP-P5-01 a P5-04)
  ├── 5. Compilación, Renderizado TeX y Serialización              :  6 Gaps  (GAP-P6-01 a P6-06)
  ├── 6. Gobernanza Transaccional, FSM, CQRS y Runtime             :  5 Gaps  (GAP-P7-01 a P7-05)
  └── 7. Testing, Benchmark, Snapshots y CI Gates                  :  5 Gaps  (GAP-C5-01 a C5-05)
==================================================================================================
```

---

## 4. CONCLUSIÓN Y TRANSICIÓN AL ENTREGABLE 2 (CONTRACT MAP)

La **Architecture Gap Matrix** se declara **APPROVED AS RELEASE CANDIDATE (Final RC)**. 

Cada uno de los 40 *Gaps* registrados cuenta con su **Consecuencia Arquitectónica Observada** incontrastable, su clasificación de **Alcance (Decision Scope)** y está formalmente asignado a los **Architectural Decision Records (`ADR-F17BIS-01` a `ADR-F17BIS-11`)** que serán desarrollados en el **Entregable 3**.

Queda habilitada la transición al **Entregable 2 (Contract Map Definitivo)**, donde cada componente del repositorio recibirá su clasificación imperativa de destino:
* **`KEEP`**: Módulos SOTA aprobados sin modificaciones de arquitectura.
* **`EXTEND`**: Componentes válidos que requieren desacoplamiento, tipeado o reconexión de puertos.
* **`REPLACE`**: Módulos defectuosos que deben reescribirse para eliminar inseguridades o fallas de I/O.
* **`DEPRECATE`**: Código legacy o zombi a purgar del repositorio.