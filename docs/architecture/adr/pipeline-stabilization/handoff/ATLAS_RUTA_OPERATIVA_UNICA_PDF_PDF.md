# Atlas de la Ruta Operativa Única PDF→PDF — arquitectura implementada

**Versión:** 1.0.1 (revisión estática de contratos y diagramas) · **corte técnico:** 2026-11-13 · **estado:** CURRENT IMPLEMENTED ROUTE / DOCUMENTACIÓN DESCRIPTIVA  
**Código anclado:** [PR #46 fusionado, commit `6818e86e21b14e77a606f0c863e9c199b4627601`](https://github.com/RDsanchez-git/translator_pdf/commit/6818e86e21b14e77a606f0c863e9c199b4627601), rama `pipeline_stabilization`. **Alcance de esta revisión:** correspondencia estática entre código pinneado, diagramas, contratos y Compose; sin reejecución de C2/T07.  
**Dirección:** D-1/D-2 aprobada por el owner el 2026-11-08; ejecución C0–C4 y DoD §8 (9/9) acreditados en laboratorio con fake.  
**Clase:** mapa AS-IMPLEMENTED de composición, código, flujos, fronteras y riesgos para mantenimiento. **No** es NADR, nuevo plan, autorización de despliegue ni certificación científica.

> **Cómo leer este Atlas.** «Código verificado» = comportamiento que puede seguirse en el commit pinneado. «Observado por owner» = salida local atribuible a una corrida C0–C4 y conservada en actas. «No demostrado» = propiedad que los ensayos/código no permiten afirmar. Si el código evoluciona, este Atlas no certifica automáticamente el nuevo HEAD. Los paths y símbolos son una instantánea, no un mecanismo universal de descubrimiento de servicios externos.

## 0. Qué es el producto y dónde termina la acreditación

**Contrato operativo:** admitir un PDF identificado por SHA-256 de sus bytes, convertirlo en AST y plan contextual durables, resolver unidades `PRESERVE`/`TRANSLATE`/`PARTIAL` en G3, materializar proyecciones por nodo y entregar el PDF ensamblado por G5 mediante una única línea de ejecución soportada.

**No acreditado:** fidelidad matemática, integridad del corpus científico, traducción lingüística real, proveedor de pago, toda figura/tablas/vector, coste/SLO productivo, despliegue/cutover, actualización segura de cualquier generación anterior ni ejecución en otra máquina. El rechazo `B02_UNREPRESENTED_VECTOR_DRAWING` es una barrera válida, no motivo para falsear el AST.

**Jerarquía:** contratos/NADR FROZEN aplicables → decisión D-1/D-2 aprobada → código y ensayos con commit identificable → [plan C0–C4 ejecutado](../00-foundation/PLAN_IMPLEMENTACION_CONVERGENCIA_OPERATIVA_UNICA_PDF_PDF_V1_20261109.md) → observaciones históricas. El [Atlas forense anterior](../00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md) sigue archivado como historia AS-IS de rutas competidoras; **este** Atlas documenta la ruta integrada. Para repetir ensayos consultar el [runbook separado](LABORATORIO_Y_REPRODUCCION.md); para sus pruebas e identidades consultar [acta final](EVIDENCIA_Y_CIERRE.md). No duplicar esos documentos aquí.

## 1. Mapa estructural y fronteras de proceso

~~~mermaid
flowchart TD
    OP["CLI translate<br/>admisión por SHA de bytes"] --> IN["data/inbox/&lt;document_id&gt;.pdf"]
    IN --> OCR["OCR Router<br/>poll + parser + contexto"]
    OCR --> AST["data/ast_cache<br/>AST versionado + activos"]
    OCR --> DOC["documents.db<br/>perfil/payloads"]
    OCR --> Q["queue.db<br/>plan, snapshots, tasks, receipts"]
    OCR --> FSM["fsm.db<br/>generación, estado, CAS"]
    Q --> G3["G3 runtime/engine.py<br/>claim y staging"]
    AST --> G3
    G3 --> Q
    G3 -- "SOLO TRANSLATE / PARTIAL" --> PROVIDER["SyncProviderBridge<br/>proveedor externo o fake"]
    PROVIDER --> G3
    G3 --> MAT["materialized.db<br/>publicación por node_id"]
    G3 --> FSM
    MAT --> G5["G5 Assembler<br/>resolver, TeX, Tectonic, lease"]
    AST --> G5
    DOC --> G5
    FSM --> G5
    Q --> G5
    G5 --> Q
    G5 --> OUT["output/translated_&lt;document_id&gt;.pdf"]
    G5 --> FSM
    REC["Reconciler / Sweeper<br/>servicios auxiliares"] -. "recuperación / mantenimiento" .-> Q
    REC -.-> FSM
    classDef data fill:#edf5fc,stroke:#597f9a,color:#243846
    class IN,AST,DOC,Q,FSM,MAT,OUT data
~~~

La topología anterior es **lógica**: la misma SQLite puede recibir escrituras de varios procesos bajo CAS/fencing, pero no existe transacción global con filesystem y proveedor. Las flechas representan **lectura/escritura o dependencia**, no una llamada RPC implícita. En Compose OCR, G3, G5 y auxiliares se declaran como procesos independientes; el positivo C2 observó efectivamente OCR, G3, G5 y fake, **no** acredita que Reconciler/Sweeper estuvieran corriendo en ese mismo positivo. La CLI normal **solo admite y vuelve**: no confirma procesamiento ni éxito científico. Para que OCR vea el PDF, **inbox de CLI y daemon deben resolver al mismo volumen real**: la ruta local por defecto de la CLI fuera de Docker puede no compartir el volumen del contenedor; usar `--inbox-dir` solo después de verificar la ruta efectiva y el workspace, sin duplicar documentos.

### 1.1 Secuencia de contratos realmente relevantes

~~~mermaid
sequenceDiagram
    participant CLI as CLI
    participant IN as Inbox
    participant OCR as OCR Router
    participant FS as AST/activos
    participant Q as queue.db
    participant F as fsm.db
    participant G3 as G3
    participant P as Proveedor
    participant M as materialized.db
    participant G5 as G5/Tectonic
    participant OUT as PDF output
    CLI->>IN: Temporal + fsync + hard link por document_id
    Note over CLI,OCR: La CLI retorna; OCR sondea el inbox compartido
    IN-->>OCR: Detecta PDF nuevo
    OCR->>FS: Parser + registro AST contextual
    OCR->>F: Initialize CREATED; PARSING por CAS
    OCR->>Q: Plan + tasks + snapshots (commit local)
    OCR->>F: PROCESSING (CAS separado)
    G3->>FS: Reabre/verifica AST de la generacion
    G3->>Q: Verifica plan + snapshots durables
    loop Por unidad reclamable
        G3->>Q: pick_task + execution_id + lease
        alt PRESERVE
            G3->>Q: stage_chunk_result(receipt NULL, fenced)
        else TRANSLATE/PARTIAL
            G3->>P: SyncProviderBridge.execute_chunk(plan, unit)
            P-->>G3: Respuesta G3 validada
            G3->>Q: stage_chunk_result(receipt, fenced)
        end
    end
    G3->>M: publish_staged_plan (commit materialized)
    G3->>Q: finalize_published_plan (commit queue)
    G3->>F: MarkAssemblyReadyCommand (CAS)
    G5->>Q: Claim assembler (FSM ATTACH, lease/fencing)
    G5->>FS: Reabre AST/activos
    G5->>M: Lee proyecciones; aplica politica de faltantes
    G5->>OUT: Tectonic escribe .assembly_<uuid>.pdf
    G5->>Q: BEGIN + CAS queue y FSM adjunta
    G5->>OUT: os.replace(temporal, final)
    G5->>Q: COMMIT queue y FSM adjunta
~~~

**Lectura de la secuencia:** resume el **camino positivo completo**, no el orden cronológico de todos los commits intermedios en cada error/restart; si hay recuperación de un plan `RESULT_STAGED`/`COMPLETED`, G3 puede saltar la rama del proveedor y reanudar la publicación desde datos durables. Si aparece `G3_EXTERNAL_UNKNOWN`, el flujo se detiene para esa generación y **no** ejecuta una segunda inferencia. OCR también guarda el perfil en `documents.db` antes del plan, omitido solo del diagrama de secuencia por legibilidad (sí figura en el estructural). G5 utiliza `queue.db` con `fsm_db` ATTACH: la transacción contiene sus UPDATE de queue/FSM, y hace `os.replace` **antes** del COMMIT; la promoción física no es parte de una transacción distribuida atómica. Ante crash, hacen falta pruebas de autoridad y recuperación, no una promesa universal de exactly-once.

## 2. Mapa de entrypoints y selección de topología

| Superficie | Entrada real | Admisión/ejecución | Condición de uso |
|---|---|---|---|
| CLI paquete | `apps.cli.main:main` / `python -m apps.cli.main translate` | Admite PDF por SHA, sin inferir | Root seleccionado por `pyproject.toml` |
| CLI foreground | `translate <pdf> --run` → `apps/cli/pdf_product.py::run_admitted_pdf` | OCR/G3/G5 reutilizados en **mismo proceso de control**, secuencialmente | Workspace y SQLite **aislados**, preflight obligatorio |
| OCR daemon | `python apps/ocr_router/__main__.py` | Escanea inbox, crea AST/plan y FSM | Worker en Compose |
| G3 daemon | `python runtime/engine.py` | Selección de planes, claims/staging/publicación | Único engine G3 seleccionado |
| G5 daemon | `python apps/compiler/__main__.py` | Lee READY_FOR_ASSEMBLY, lease, compila/publica | Único assembler G5 seleccionado |
| Reconciler | `python apps/daemons/reconciler.py` | Resuelve estados/recovery permitido | No autoriza egress incierto |
| Sweeper | `python runtime/sweeper.py` | Mantenimiento y transiciones acotadas | No suplanta el reconciler |
| Legacy R1 | `apps/cli/main.py::handle_translate_async` | **Falla cerradamente** con `C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED` | No handler registrado en CLI |
| R1 biblioteca | `apps/cli/legacy_translate_async.py`, `apps/bootstrap/pipeline_factory.py::build_pipeline`, `TranslationPipeline` y `AsyncDispatcher` | Históricos/benchmarks/tests, no root PDF→PDF | No borrar por inferencia |
| R3 | `apps/llm_workers/__main__.py::LLMWorkerDaemon` | Ejecutable manualmente, no seleccionado por Compose/CLI soportados | Posibles lanzadores externos UNKNOWN |

### 2.1 Los tres Compose NO son equivalentes

- `docker-compose.yml`: composición base, contiene dependencias y servicios históricos de laboratorio/chaos; incluye `IS_BENCHMARK=1` para `llm_worker`, puertos publicados de servicios fake/chaos y un `build` heredado. **No es por sí solo un lanzamiento canónico G3 verificado ni un despliegue productivo validado**.
- `docker-compose.runtime.yml`: override del root de estado compartido (`g3_runtime_state`, `g3_runtime_data`, `g3_runtime_output`), entorno de SQLite y selección de G3 con `IS_BENCHMARK=0`; reemplaza dependencias del `llm_worker` y pone fake-gemini/toxiproxy bajo perfil `lab`. Sus `!override`/`!reset` necesitan versión de Compose compatible. **Inspeccionar el Compose efectivo** antes de asumir que un servicio fue desactivado.
- `docker-compose.convergence-lab.yml`: **override instrumental de C0–C2**, con imagen local pinneada, fuentes actuales en `/workspace:ro`, red `chaos_net internal:true`, `g3_fake` interno, UID10001 y volúmenes aislados. Nunca confundirlo con instalación productiva.

El servicio que en Compose se llama `llm_worker` ejecuta **`runtime/engine.py`** y **NO** `apps/llm_workers/__main__.py`. Tampoco se autoriza usar `docker-compose.golden.yml` como raíz productiva. [Runbook seguro](LABORATORIO_Y_REPRODUCCION.md).

## 3. Inventario ejecutable: archivo → símbolo → consumidor

**Convención:** todas las rutas siguientes se verificaron frente al código fusionado en `6818e86`. Ruta en columna = archivo a inspeccionar antes de editar el contrato; funciones = puntos de unión relevantes, no un catálogo exhaustivo de 94 filas. El inventario histórico ampliado se conserva en la [matriz R1/R2/R3](../00-foundation/MATRIZ_VERSIONADA_COMPOSICION_DISPOSICION_R1_R2_R3_V1_20261109.md).

### 3.1 Admisión y parser

| Archivo | Rol o símbolo decisivo | Quién depende |
|---|---|---|
| `apps/cli/main.py` | `handle_translate`, `parse_arguments`, `--run` y rechazador R1 | operador/packaging, tests CLI |
| `apps/cli/pdf_inbox.py` | `submit_pdf_to_inbox`, `PDFInboxSubmission` | CLI → OCR inbox |
| `apps/cli/pdf_product.py` | `preflight_product_run`, `run_admitted_pdf`, `_ingest/_run_g3/_run_g5` | foreground exclusivo |
| `apps/ocr_router/__main__.py` | `OCRRouterDaemon._process_document` | inbox → AST/FSM/plan |
| `apps/bootstrap/pipeline_factory.py` | `build_extraction_pipeline` y `build_document_profiler`, **NO** `build_pipeline` R1 | OCR/foreground |
| `core/ast/registry.py` | `ASTRegistry.register_ast/get_document_ast` | OCR → G3 y G5 |
| `core/ast/hashing.py` | `compute_ast_hash` | identidad de generación |
| `infra/db/profile_store.py` | `SQLiteProfileStore` | OCR/G5 y documentos |

**Detalle de frontera:** `pdf_inbox.py` copia a un temporal, hace `fsync` y publica mediante hard link del temporal al archivo final por SHA. Si el destino existe, **verifica el hash existente**; si el filesystem no permite hard links, falla en lugar de sobrescribir. El mensaje de «admisión» **no** confirma OCR ni un PDF compilado. `OCRRouterDaemon` reconsulta FSM antes de ingerir: un documento ya activo/completado se archiva como duplicado en lugar de reiniciarse a ciegas; una generación fallida requiere intervención.

### 3.2 Plan, contexto y proveedor

| Archivo | Rol / frontera |
|---|---|
| `core/chunking/contextual_plan.py::prepare_contextual_plan` | enriquecimiento contextual, agrupación y `ChunkPlan`, conservando hash semántico AST |
| `core/chunking/manifest_contract.py::ChunkPlan` | cobertura, miembros, serialización canónica, `manifest_sha256` |
| `infra/db/context_snapshot_repo.py::DurableContextPlanRepository` | `enqueue_verified/load_verified`: snapshots y plan persistidos/verificados en nuevas conexiones |
| `core/context/snapshot_contract.py::ContextSnapshotV1` | esquema de contexto persistido y digest |
| `runtime/engine.py::run_pipeline` | validador de AST/plan/contexto previo a proveedor; despachador G3 |
| `runtime/chunk_staging.py::stage_claimed_unit` | rama `PRESERVE` vs `TRANSLATE/PARTIAL` y staging fenced |
| `apps/llm_workers/sync_bridge.py::SyncProviderBridge.execute_chunk` | prompt y respuesta estructurada con identidad, máscara matemática y contexto verificado |
| `apps/llm_workers/prompt_builder.py` | construcción de prompts para G3 |
| `apps/bootstrap/provider_stack_factory.py` | selección del stack de proveedor; no se inicializa antes de validar plan en G3 |
| `core/validation/budget.py` y `core/finops/measurement.py` | política de presupuesto/medición; no suponer validación de coste real por el fake |

`prepare_contextual_plan` rechaza alteración del hash semántico de AST por el enriquecimiento, contextos faltantes y agrupación incompatible. `DurableContextPlanRepository.enqueue_verified` conserva `ChunkPlan`, tareas y snapshots en una **transacción local en queue.db**; un plan legacy sin snapshots no se adopta silenciosamente. `load_verified` rechaza deriva del manifest, cobertura o snapshot antes de inferencia.

`SyncProviderBridge.execute_chunk` construye `G3_CHUNK_RESPONSE_V1`; valida binding de `document_id`/`ast_hash`/`manifest_sha256`/`chunk_id`, miembros y máscaras `__MATH_N__` sin cruzar segmentos. **Esto es control de formato y estructura, no prueba de fidelidad científica**. El antiguo `SyncProviderBridge.execute(node)` pertenece a ruta legacy y no debe reaparecer como fallback G3.

### 3.3 Persistencia, publicación, recuperación y ensamblado

| Archivo | Rol / frontera |
|---|---|
| `infra/db/connection.py::get_connection` / `resolve_sqlite_path` | conexión thread-confined; SQLite WAL; opt-in `SQLITE_STATE_DIR`; `fsm_db` ATTACH seguro |
| `infra/db/control_repo.py::ControlPlaneRepository` | `enqueue_chunk_plan`, `pick_task`, `stage_chunk_result`, `mark_g3_external_unknown`, selectores de recuperación |
| `infra/db/fsm_repository.py::FSMRepository` | `initialize_document`, `transition_to` CAS y selectores de estado |
| `infra/db/staged_publication.py` | `publish_staged_plan`, `finalize_published_plan` y verificaciones |
| `runtime/publication_pipeline.py::advance_staged_document` | publish → finalize → `READY_FOR_ASSEMBLY`, sin provider |
| `infra/db/materialized_repo.py::MaterializedPlaneRepository` | proyecciones de nodos por versión |
| `core/execution/state.py` / `core/execution/handlers.py` | grafo FSM legal, comandos y validación |
| `apps/daemons/reconciler.py::ReconcilerDaemon` | reparación de tareas/estado y control de liderazgo |
| `runtime/sweeper.py::RecoveryDaemon` | mantenimiento/fallos acotados |
| `apps/compiler/__main__.py::AssemblerWorkerDaemon` | selección por FSM, claim G5, compile, publicación fenced |
| `infra/db/assembly_recovery.py::AssemblyLeaseRepository` | claim, renew, advance, publish, fail_authorized y recover_expired |
| `core/compiler/context_resolver.py::CQRSAssemblyContextResolver` | valida topología AST, filtra OMIT, busca proyecciones de generación/versión |
| `core/compiler/service.py::CompilationService` | render de contexto y activos a TeX |
| `apps/compiler/tectonic_runner.py::HostTectonicRunner` | compilación física PDF por Tectonic |
| `core/compiler/assembler.py` / `core/compiler/rendering/*` | geometría, activos y ensamblado documental |

**Política G5 real (importante al cambiar el assembler):** `CQRSAssemblyContextResolver.resolve` verifica AST, unicidad, continuidad de `sequence_id` **antes** de filtrar `OMIT`, y obtiene las proyecciones requeridas por versión. Si faltan, **las registra**, pero no decide el rechazo. En la composición de `apps/compiler/__main__.py` y del foreground `apps/cli/pdf_product.py`, `DocumentAssembler` tiene `AssemblyPolicy(tolerance_ratio=0.05, allow_fallback=True, degradable_failures=frozenset())`: **si falta más del 5 % de nodos ensamblables, rechaza; si falta hasta el 5 %, puede aceptar como `DEGRADED`**, pero `CompilationService` debe obtener el payload de fallback con integridad por `chunk_id`/`payload_sha256` y aún puede fallar. **No afirmar** que cualquier falta de proyección causa rechazo inmediato ni que la tolerancia permite reconstruir información arbitraria. No se acreditó calidad científica en casos degradados.

## 4. Mapa de datos, IDs y autoridad

### 4.1 Identidades que nunca deben confundirse

| Identificador | Cómo se obtiene | Por qué importa |
|---|---|---|
| `document_id` | SHA-256 de los **bytes fuente** al ingresar | deduplicación de admisión; no identificador aleatorio de job |
| `ast_hash` | `compute_ast_hash` de AST semántico | generación lógica; no tomar nodos de otra |
| `manifest_sha256` | digest canónico de `ChunkPlan` | vincula unidades, orden, miembros y contexto |
| `context_id` / `snapshot_sha256` | contexto enriquecido y snapshot verificable | replay contextual seguro |
| `chunk_id` | unidad semántica G3, columna legacy `chunk_tasks.node_id` | NO igualar automáticamente a `AST.node_id` |
| `node_id` / `segment_index` | miembro de AST/plan; índice de segmento | proyección física por nodo y reconstrucción |
| `task_id` / `execution_id` / `lease_owner` | claim persistido en queue | autoridad para staging, ack y publicación |
| `state_version` / `projection_version` | CAS de FSM y versión de materialización | impide usar estados/proyecciones incompatibles |

La clave de un resultado legítimo está ligada a una **generación** y a su identidad completa. Reutilizar texto por `prompt_hash` sin modelo/contexto suficientemente vinculados está bloqueado: `runtime/engine.py` usa `cache_db_path=None` para la caché legacy.

### 4.2 Propiedad de SQLite y filesystem

| Plano | Archivo/ubicación configurada | Escritura/lectura y límite |
|---|---|---|
| FSM | `fsm.db` / `FSM_DB_PATH` | estado/versiones, CAS por generación; no mover progreso solo por ver el PDF |
| Queue/control | `queue.db` / `QUEUE_DB_PATH` | plans, `chunk_tasks`, `g3_context_snapshots`, `chunk_result_receipts`, claims y autorización |
| Materialized | `materialized.db` / `MAT_DB_PATH` | proyecciones por `node_id` y versión; publicación G3 verificada |
| Documentos/perfil | `documents.db` y perfil | perfil generado en OCR; datos auxiliares para G5 |
| Event/system | `event.db` y plano de sistema | eventos, conciliación y autoridad auxiliar; no es fuente única del documento |
| AST/activos | `data/ast_cache/<document_id>.<ast_hash>.ast.json` + recursos de render | `ASTRegistry.register_ast` usa temporal + `os.replace` y una caché RAM por proceso; G3/G5 reabren desde archivo por identidad. El registro AST no comparte commit con `queue.db`/`fsm.db` |
| PDF | `COMPILER_OUTPUT_DIR` → `translated_<document_id>.pdf` | publicación física G5 fenced, no certificado de fidelidad |

`infra/db/connection.py` redirige **solo** archivos `infra/db/*.db` cuando está declarado `SQLITE_STATE_DIR`; fuera de opt-in resuelve contra `APP_ROOT` o el root de código. **No** asumir que una variable del host configura automáticamente todos los servicios: revisar Compose efectivo. `get_connection` usa SQLite WAL, `synchronous=NORMAL`, busy timeout y conexiones restringidas por hilo. Para queue, `fsm_db` se adjunta si existe; una consulta de autoridad debe verificar el alias y no crear la FSM silenciosamente.

En el laboratorio Compose de C2, el root de estado está en `/app/state/db`, inbox `/app/data/inbox`, salida `/app/output` y fuentes `/workspace:ro`. Estos paths describen **ese sandbox**, no toda instalación posible de producción.

## 5. Estados y barreras que definen la ruta

~~~mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> PARSING
    PARSING --> PROCESSING
    PROCESSING --> READY_FOR_ASSEMBLY: plan G3 publicado + FSM CAS
    READY_FOR_ASSEMBLY --> ASSEMBLING
    ASSEMBLING --> READY_FOR_COMPILATION
    READY_FOR_COMPILATION --> COMPILING
    COMPILING --> COMPLETED: PDF fenced
    COMPLETED --> [*]
~~~

La figura muestra **solo el camino positivo de la FSM documental**; no es el estado de las unidades G3 ni de las tareas ASSEMBLER. El grafo legal con `FAILED_RETRYABLE`, `FAILED_FATAL`, `STALLED` y `CANCELLED` se define en `core/execution/state.py::LEGAL_TRANSITIONS` para el validador de comandos. **G5 también cambia estados mediante SQL fenced directamente en `AssemblyLeaseRepository`**, bajo CAS/lease y `fsm_db` ATTACH: si cambia el grafo legal, hay que comprobar **ambos mecanismos**, no asumir que todo pasa por `DocumentCommandHandler`.

**Máquina de tareas G3 (simplificada):** `PENDING/RETRYABLE_ERROR` → claim `PROCESSING` con `execution_id` → `RESULT_STAGED` con receipt → `COMPLETED`, después de publicación verificada. En error de efecto remoto incierto: `G3_EXTERNAL_UNKNOWN` **no runnable**, requiere disposición humana; no equivale a retry seguro. En G5 las fases de ensamblado se protegen con lease y `state_version`, y un worker anterior no puede publicar ni marcar FAILED al nuevo propietario.

### 5.1 Las tres fronteras no atómicas más peligrosas

1. **OCR AST → queue → FSM.** El AST se registra antes de commits SQLite; FSM/queue son transacciones separadas. Reingesta parcial solo con mismo `ast_hash` y validación de estado. Nunca crear «todo atómico» por comentario.
2. **Proveedor → receipt/staging → materialized → FSM.** La inferencia remota no participa en SQLite; primero se persiste el efecto/receipt de una unidad, después se publican proyecciones y se finaliza la cola, por último se avanza FSM. `RESULT_STAGED` puede recuperarse **sin repetir POST**. Un efecto remoto ambiguo no se vuelve a enviar automáticamente.
3. **Tectonic → archivo privado → promoción de PDF → commit de queue/FSM.** El PDF se compila a un nombre `.assembly_<uuid>.pdf`; `AssemblyLeaseRepository.publish` valida ruta/cabecera, lease y versión, ejecuta `os.replace` y commit bajo el writer lock. Si el proceso cae alrededor del rename, se necesita reconciliación o nueva compilación **autorizada**, no aceptar como prueba el archivo que quedó en disco.

## 6. Grafo de riesgo: cambios de código y tests mínimos pertinentes

| Si modificás... | Frontera vulnerable y pregunta a resolver | Testigos/versiones a revisar |
|---|---|---|
| CLI, argumento de inbox, deduplicación | ¿Sigue el mismo SHA bytes y la publicación atómica sin sobrescritura? | `tests/integration/test_pdf_inbox_submission.py`; `tests/integration/test_cli_router.py` |
| PyMuPDF, mapper o AST hashing | ¿Cambio semántico o cosmético? ¿Permanecen `node_id`/hash/activos representables? | `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py`; `tests/integration/test_w08_ocr_g3_context_wiring.py`; B02 científicos aparte |
| Enriquecimiento/contexto/plan | ¿Snapshot, manifest y cobertura tienen misma generación? | `tests/integration/test_w08_durable_context_boundary.py`; `tests/integration/test_g3_b2_sqlite_plan_contract.py` |
| Scheduler, claims, quotas, provider | ¿Existe una ruta que haga POST sin receipt/lease? ¿Bajo incertidumbre se repite? | `tests/integration/test_w06_g3_uncertain_effect_offline.py`; `tests/integration/test_g3_b4_3a_engine_staging.py`; `tests/integration/test_g3_b3_2_fenced_receipts.py` |
| Staging y publish G3 | ¿Se puede reabrir la publicación sin reenvío y sin duplicar proyecciones? | `tests/integration/test_g3_b4_3b_publication_recovery.py`; `tests/integration/test_c3_t05_process_boundary.py` |
| Resolver materializado, G5, Tectonic | ¿El G5 lee misma generación y nunca promueve el PDF de un lease viejo? | `tests/integration/test_g3_b4_4_profile_projection_assembly.py`; `tests/integration/test_g5_assembler_lease_recovery.py` |
| Reconciler, Sweeper, FSM | ¿Se preserva cuarentena UNKNOWN; CAS y transición legal? | `tests/integration/test_g3_b4_9_reconciler_fencing.py`; `tests/integration/test_w06_g3_uncertain_effect_offline.py` |
| Compose, imagen, mounts, fake | ¿La config efectiva sigue aislada; bootstrap solo volumen nuevo; no hay R3? | `apps/lab/convergence_compose_preflight.py`; `tests/unit/test_c4_t06_supported_roots.py` |
| Modalidad foreground | ¿Mismas clases/contratos con entorno aislado? | `tests/integration/test_w08_cli_foreground_single_generation_offline.py`; T07 [acta](EVIDENCIA_Y_CIERRE.md) |

La tabla es un **mapa de impacto**, no una obligación de ejecutar todas las pruebas ante cualquier cambio. Preferir tests focales y lectura del contrato afectado; reservar un nuevo E2E real para cambios que lo justifiquen y cuenten con recursos y autorización. No reinterpretar el DoD 9/9 del commit del PR #46 como evidencia de un HEAD futuro.

## 7. Observabilidad y diagnóstico con correlación

**Eje de correlación recomendado al inspeccionar salidas:** `document_id` + `ast_hash` + `manifest_sha256` + `chunk_id`/`node_id` + `task_id`/`execution_id` + `lease_owner` y `state_version`; usar un subconjunto según el proceso. Estos identificadores son más fiables para reconciliar eventos que la hora impresa de dos procesos distintos. No imprimir claves de proveedor, prompt ni texto sensible del PDF.

| Señal / marcador | Punto de observación | Interpretación segura |
|---|---|---|
| `PDF_INBOX_*` | CLI | falló admisión/destino; no se lanzó OCR |
| `W08_OCR_*` y `G3_B4_2_*` | OCR y snapshot | generación/contexto inválidos; evitar inferir |
| `G3_B4_3A_*`, `G3_B4_3B_*` | G3 staging/publication | falló claim/staging o hay plan incompleto |
| `G3_W06_EXTERNAL_UNKNOWN_REQUIRES_OPERATOR` | runtime G3 | STOP y cuarentena; **no** realizar POST adicional |
| `G5_ASSEMBLER_*` | G5 y lease | autoridad perdida, PDF inválido o publicación fenced |
| `C0_T01_STATIC_CANDIDATE_PASS` | preflight Compose | solo topología estática, NO runtime |
| `C3_T07_FOREGROUND_ISOLATED_PASS` | script T07 | equivalencia operacional aislada sobre fixture acreditada |
| FSM `COMPLETED` + PDF físico | verificación durable | resultado operacional del PDF, NO certificación científica |

Para aislar un problema se recomienda **primero** inspeccionar sin cambios: commit/imagen, rutas DB reales, estado FSM y tareas, receipts, snapshots, proyecciones, lease y PDF físico. Si el fallo es `G3_EXTERNAL_UNKNOWN`, no abrir un nuevo worker ni disparar reintentos; preservar bytes, logs y metadata para disposición posterior. Los comandos Docker, lecturas seguras y restricciones de limpieza están en el [runbook](LABORATORIO_Y_REPRODUCCION.md).

## 8. Topología de laboratorio y qué testificó

**Composición C2:** procesos independientes OCR Router, G3, G5 + fake interno; checkout montado read-only, imagen histórica con ID fijo, volúmenes separados en proyecto `tpdfconvconv1211b`, UID10001 y red interna. **Owner observó** un POST `TRANSLATE` aceptado, cero `PRESERVE`, receipts y proyecciones completas, FSM `COMPLETED` y PDF Tectonic real de 7050 bytes. El fixture y SHA están en [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md).

**Recuperación T05:** subprocess 1 persistió y murió deliberadamente; subprocess 2 reabrió y publicó lo staged sin provider; tercer lector verificó persistencia. Cobertura focal, no reinicio universal de cualquier daemon o tipo de fallo.

**Foreground T07:** mismo fuente/AST/manifest y contratos en workspace aislado con fake loopback. PDF de igual longitud y distinto SHA; equivalencia contractual, no determinismo byte a byte. **Su launcher requiere el contenedor OCR C2 original**; no es un reproductor independiente desde cero si ese recurso histórico desapareció.

**C4/T06:** entrada CLI R1 bloqueada, roots versionados no seleccionan R3, benchmarks siguen siendo consumidores legítimos del dispatcher legacy. Se inspeccionaron solo los entrypoints que Git permite observar; procesos externos quedan `UNKNOWN`.

## 9. Trazabilidad, regresiones heredadas y estado de integración

[Acta de DoD 9/9](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6841545770) y [decisión de merge](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6842521268). En el CI del último HEAD del PR #46, `static-analysis` y unitarios PASS, pero CV/integración FAIL por problemas previos **idénticos en la base**: 15 PDFs canónicos `doc_08…doc_22` ausentes ([issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34)) y 3 pruebas que chocan con el rechazo B02. Esos dos FAIL fueron **aceptados documentalmente como informativos para ese merge**, no convertidos en PASS ni resueltos. Este Atlas no reabre ese trabajo separado.

La evidencia operativa fue reportada por el owner; no existen logs brutos completos o PDFs binarios anexados al PR. **No afirmar que una futura instalación podrá reconstruir C2 automáticamente**: no hay un lanzador multiproceso integral probado desde cero. Consultar el [runbook](LABORATORIO_Y_REPRODUCCION.md) antes de cualquier nuevo sandbox.

## 10. Regla editorial para el próximo cambio arquitectónico

1. Identificar commit exacto, archivo y **productor/consumidor** afectados en las secciones 3 y 6.
2. Revisar D-1/D-2 y NADR FROZEN aplicables; un Atlas descriptivo no habilita alterar normas.
3. Demostrar con código y test focal que la identidad, autoridad y barreras de la sección 5 siguen válidas; una desviación debe clasificarse, no esconderse.
4. Actualizar **este Atlas en el mismo PR de cambio de ruta**: diff de nodos/edges, interfaces, estado, evidencia y cobertura. No abrir una segunda guía de arquitectura competidora.
5. Registrar fecha, commit testificado, prueba y límites; si no hubo test dinámico, escribir `INSPECCIÓN ESTÁTICA`, nunca `ACREDITADO`.
6. Mantener el runbook de Docker separado para comandos; conservar el expediente forense anterior sin reescribir observaciones históricas.

### Fuentes primarias de lectura obligada

- [CLI y admisión](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/apps/cli/main.py), [PDF inbox](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/apps/cli/pdf_inbox.py) y [foreground](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/apps/cli/pdf_product.py).
- [OCR Router](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/apps/ocr_router/__main__.py), [plan contextual](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/core/chunking/contextual_plan.py), [snapshots](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/infra/db/context_snapshot_repo.py).
- [G3](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/runtime/engine.py), [staging](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/runtime/chunk_staging.py), [publicación](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/runtime/publication_pipeline.py), [control repo](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/infra/db/control_repo.py).
- [G5](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/apps/compiler/__main__.py), [lease/publish](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/infra/db/assembly_recovery.py), [resolver](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/core/compiler/context_resolver.py), [SQLite paths](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/infra/db/connection.py).
- [Compose base](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/docker-compose.yml), [runtime](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/docker-compose.runtime.yml), [override laboratorio](https://github.com/RDsanchez-git/translator_pdf/blob/6818e86e21b14e77a606f0c863e9c199b4627601/docker-compose.convergence-lab.yml); [evidencias PR #46](EVIDENCIA_Y_CIERRE.md).

**Decisión de mantenimiento:** **un Atlas vivo**, un runbook operativo, una acta de evidencia. El viejo Atlas queda como fuente de historia, no otra SSOT de rutas actuales.
