# Matriz versionada de composición y disposición de archivos — convergencia PDF→PDF

**Versión:** v1.0.1 · **Fecha:** 2026-11-09 · **Estado:** inventario técnico prescriptivo, disposición **propuesta** / no borrado autorizado.  
**Sujeto:** `RDsanchez-git/translator_pdf` / `pipeline_stabilization` @ `6a5ee41886b935c2c0f3a107a42620d93de31efb` (#40 integrado).  
**Plan vinculante por referencia:** [PLAN_IMPLEMENTACION_CONVERGENCIA_OPERATIVA_UNICA_PDF_PDF_V1_20261109.md](PLAN_IMPLEMENTACION_CONVERGENCIA_OPERATIVA_UNICA_PDF_PDF_V1_20261109.md), v1.0.1.  
**Decisión de producto:** [D-1/D-2, cabecera vigente](DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md): una CLI, G3→G5, sin motores productivos rivales. Este inventario **no** equivale a ejecución, censo exhaustivo de consumidores externos o certificación científica.

## 1. Cómo se usa esta matriz

Cada fila establece una identidad de símbolo o path exacto (salvo las filas con `/*`, que son **grupos** declarados), origen histórico orientativo, rol, consumidor, **disposición TO-BE**, **evidencia AS-IS** y testigo del plan. `R1 compartido` y `R2+R1` señalan reutilización; el nombre de ruta **no** es una propiedad normativa del archivo. Las rutas de #41–#44 están **en ramas Draft, no en el HEAD**. No usar `NO_PRODUCTIVO` como sinónimo de borrar, ni `KEEP` como prueba de funcionamiento.

**Estados de disposición:** `KEEP` (sobrevive y participa), `KEEP_VERIFICAR` (sobrevive sujeto a ensayo), `ADAPT_CONDICIONAL` (solo mecanismo aislado ante brecha), `ADAPT_OPERACION` (root/config para corregir), `NO_PRODUCTIVO` (excluido de entrypoints soportados), `HISTORICO_COMPAT` (permanece por consumidores/tests hasta censo), `RETIRE_CANDIDATE` (posible futura retirada, no ejecutada), `KEEP_LAB` (laboratorio; nunca motor prod), `NO_ROOT`/`NO_ROOT_OFICIAL` (no seleccionado), `DEFER_PR` (no merge), `DEFER_EVALUACION_INDEPENDIENTE` (auditar propio delta).

**Los tests T01–T07 y deltas C0–C4 se definen en el plan; son checklists técnicos, no nuevos gates normativos.** `AS-IS` viene de inspección estática y evidencia histórica delimitada; no se ejecutó la composición multiproceso.

## 2. Inventario numerado v1.0.0 (94 filas)

| ID | Origen | Archivo / símbolo | Responsabilidad | Consumidor / salida | Disposición TO-BE | AS-IS | Condición de integración | Testigo | Reserva |
|---|---|---|---|---|---|---|---|---|---|
| E01 | R1 | apps/cli/main.py::handle_translate | Entrada | CLI→inbox; OCR | KEEP | ACTIVO | D1; SHA PDF; no G3 propio | T01,T02 | No eliminar archivo |
| E02 | R1 | apps/cli/main.py::handle_translate_async | Ejecutor R1 | TranslationPipeline | RETIRE_CANDIDATE | CODIGO_INACTIVO_CLI | No handler en parse_arguments; otros callers no censados | T06 | Retiro solo tras censo |
| E03 | R1 | apps/cli/main.py::parse_arguments | CLI | translate→handle_translate | KEEP | ACTIVO | --run opt-in; translate admisión | T01,T02,T07 | Única entrada declarada |
| E04 | Convergencia | apps/cli/pdf_inbox.py | Admisión por bytes | OCR inbox | KEEP | ACTIVO | SHA256, copia atómica; misma raíz que OCR | T02 | Host vs volumen Compose: probar |
| E05 | Convergencia | apps/cli/pdf_product.py | Foreground | OCR→G3→G5 | KEEP | ACTIVO_FOREGROUND | Usa implementaciones existentes; preflight workspace/DB/Tectonic | T07 | No certificar Compose con foreground |
| E06 | R1 compartido | apps/bootstrap/pipeline_factory.py::build_pipeline | Composition root R1 | AsyncDispatcher | NO_PRODUCTIVO | EXISTE_NO_INVOCADO_POR_CLI | No llamar desde translate ni Compose | T06 | Mantener pruebas/consumidores hasta censo |
| E07 | R1 compartido | apps/bootstrap/pipeline_factory.py::build_extraction_pipeline | Parser factory | OCRRouterDaemon | KEEP | ACTIVO | PyMuPDF→Layout→FlatAST | T02,T03 | Retener aunque se aísle build_pipeline |
| E08 | R1 compartido | apps/bootstrap/pipeline_factory.py::build_document_profiler | Profiler factory | OCRRouterDaemon | KEEP | ACTIVO | Inyecta perfilador | T02 | Mismo archivo root mixto |
| E09 | R1 | core/pipeline/orchestrator.py | TranslationPipeline R1 | build_pipeline | NO_PRODUCTIVO | EXISTE_SIN_ROOT_PRODUCTIVO_ACREDITADO | No convertir en wrapper de G3 | T06 | Censo consumidores |
| E10 | R1 | core/pipeline/job.py | Job R1 | TranslationPipeline | HISTORICO_COMPAT | NO_ROOT_PRODUCTIVO | Conservar por consumidores R1 y tests | T06 | Revisar antes de retiro |
| E11 | R1 | core/pipeline/workflow.py | Workflow R1 | TranslationPipeline | HISTORICO_COMPAT | NO_ROOT_PRODUCTIVO | No usar como segunda FSM G3 | T06 | Consumidores sin auditar |
| E12 | R1 | core/pipeline/state_store.py | FSM R1 adaptador | TranslationPipeline | HISTORICO_COMPAT | NO_ROOT_PRODUCTIVO | No introducir segunda fuente de autoridad | T06 | Preservar mientras haya consumidores |
| E13 | R1 | apps/llm_workers/dispatcher.py::AsyncDispatcher | Executor R1 | build_pipeline | NO_PRODUCTIVO | NO_EN_COMPOSE | No llamar LLM en paralelo a G3 | T06 | No borrar sin censo |
| E14 | R1/G3 | apps/llm_workers/prompt_builder.py | Prompt estructurado | SyncProviderBridge.execute_chunk | KEEP | ACTIVO_G3 | Prompt y budgets; identidad de contexto verificada por bridge | T03 | No confundir con segunda vía |
| E15 | R1→G3 | core/normalization/enrichers/context_enricher.py | Jerarquía/contexto | prepare_contextual_plan | KEEP | INTEGRADO_40 | Anota CTX; no cambia hash semántico | T02,T03 | Beneficio reutilizado |
| E16 | R1/G3 | core/context/snapshot_contract.py | DTO contexto | DurableContextPlanRepository / bridge | KEEP | ACTIVO_G3 | Snapshot durable de contexto | T03 | No fallback GLOBAL_ROOT |
| E17 | R1 | core/context/context_registry.py | Context registry legacy | build_pipeline R1 | HISTORICO_COMPAT | EXISTE | No usar como almacén runtime G3 | T06 | No borrar por nombre |
| E18 | R1 | core/context/dynamic_resolver.py | Resolver legacy | build_pipeline R1 | HISTORICO_COMPAT | EXISTE | G3 usa snapshots durables | T06 | Censo |
| E19 | R1 | core/validation/pipeline.py | Validación | R1 AsyncDispatcher | ADAPT_CONDICIONAL | NO_PROBADO_EN_G3 | Compatibilidad por miembro G3 debe demostrarse | T03 | No bloquear C0-C2 |
| E20 | R1 | core/validation/factory.py | Factory validación | R1 build_pipeline | ADAPT_CONDICIONAL | NO_PROBADO_EN_G3 | No integrar todo el pipeline por arrastre | T06 | Reutilizar pruebas específicas |
| E21 | R1 | core/healing/pipeline.py | Healing post-LLM | R1 AsyncDispatcher | ADAPT_CONDICIONAL | NO_PROBADO_EN_G3 | Nunca nuevo egress tras UNKNOWN | T03,T05 | Contrato G3 requiere adaptación |
| E22 | R1 | core/healing/strategies/* | Healing por estrategia | HealingPipeline | ADAPT_CONDICIONAL | EXISTE | Reutilizar sólo reglas apropiadas | T06 | Grupo, no archivo único |
| E23 | R1/G3 | core/prompting/* | Payload/canonicalizer | PromptBuilder | KEEP | USO_G3_INDIRECTO | No duplicar versión/hash ni inventar safe replay | T03 | Grupo dependencias |
| E24 | R2 | apps/ocr_router/__main__.py | OCR único | AST/Plan/queue/FSM | KEEP | COMPOSE+FOREGROUND | _process_document y daemon.run comparten implementación | T02 | Error move-to-error; diagnosticar primario |
| E25 | R2 | apps/bootstrap/extraction_config.py | Config extractor | ExtractionProviderFactory | KEEP | ACTIVO | Default PyMuPDF | T02 | Docling no seleccionado |
| E26 | R2 | apps/bootstrap/provider_factory.py | Extractor factory | build_extraction_pipeline | KEEP | ACTIVO | Solo PyMuPDF conectado | T02 | No elegir Docling por etiqueta |
| E27 | R2 | infra/adapters/pdf_parser.py | Layout→AST adapter | OCR parser | KEEP | ACTIVO | Producer→consumer de layout | T02 | Validación de coverage |
| E28 | R2 | infra/extraction/providers/pymupdf_provider.py | Extractor concreto | PdfParserAdapter | KEEP | ACTIVO | Produce layout e imágenes representadas | T02 | B02 fail-closed |
| E29 | R2 | infra/extraction/providers/pymupdf_integrity.py | Guard cobertura | PyMuPDF | KEEP | ACTIVO_FAIL_CLOSED | Vector sin representación falla explícito | T02 | No debilitar para forzar PASS |
| E30 | R2 | infra/extraction/providers/pymupdf_image_assets.py | Activos imagen | PyMuPDF/G5 | KEEP | ACTIVO_CONDICIONAL | Preservar assets trazables | T04 | No equivale a vectores |
| E31 | R2 | infra/extraction/providers/pymupdf_math_visual.py | Math visual | PyMuPDF | KEEP | ACTIVO_CONDICIONAL | Limitaciones científicas pendientes | T04 | No inferir fidelidad |
| E32 | Alternativa | infra/extraction/providers/docling_provider.py | Extractor alternativo | No factory productiva | NO_PRODUCTIVO | EXISTE_NO_SELECCIONADO | Conservar investigación/test | T06 | No reemplazar PyMuPDF sin W09 |
| E33 | R2 | core/ast/builder.py | FlatASTBuilder | build_extraction_pipeline | KEEP | ACTIVO | Un solo AST plano | T02 | No segundo AST |
| E34 | R2 | core/ast/models.py | DTO AST y units | OCR/G3/G5 | KEEP | ACTIVO | Identidad de miembros/nodos | T02,T03,T04 | No mutar DTOs por atajo |
| E35 | R2 | core/ast/hashing.py | Hash semántico | OCR/G3 | KEEP | ACTIVO | Excluye control_plane; no sustituye manifest | T02,T03 | Hash no prueba same inference |
| E36 | R2 | core/ast/registry.py | Persistencia AST | OCR/G3/G5 | KEEP | ACTIVO | Archivos data/ast_cache; otra instancia rehidrata | T02,T04 | Shared volume obligatorio |
| E37 | R2+R1 | core/chunking/contextual_plan.py | Plan contextual | OCR | KEEP | INTEGRADO_40 | Heading PRESERVE, grupos CTX | T02,T03 | No GLOBAL_ROOT |
| E38 | R2 | core/chunking/manifest_contract.py | ChunkPlan | OCR/G3 | KEEP | ACTIVO | Cobertura de AST representado y manifest digest | T03 | No prueba cobertura PDF |
| E39 | R2 | core/chunking/semantic_chunking.py | Chunker | contextual_plan | KEEP | ACTIVO | Units por contexto/token | T02 | Mantener estrategia |
| E40 | R2 | core/chunking/result_contract.py | Parse respuesta G3 | SyncProviderBridge | KEEP | ACTIVO | Cobertura exacta miembros | T03 | No aceptar raw echo como traducción |
| E41 | R2 | core/document_profile/profiler.py | Perfil documental | OCR | KEEP | ACTIVO | Almacena perfil en documents.db | T02 | Mismo namespace |
| E42 | R2 | infra/db/profile_store.py | SQLite ProfileStore | OCR/G5 | KEEP | ACTIVO | Tabla en documents.db, creada on demand | T02,T04 | No bootstrap 4DB como cobertura total |
| E43 | R2 | infra/db/context_snapshot_repo.py | Snapshot+Plan | OCR/G3 | KEEP | INTEGRADO_39_40 | enqueue_verified/load_verified | T02,T03 | Falldown en generations legacy |
| E44 | R2 | runtime/engine.py::run_pipeline | Ejecutor G3 | queue→receipt/publicación | KEEP | ACTIVO_COMPOSE | Control W06 y preflight plan/snapshots | T03,T05 | IS_BENCHMARK=0 indispensable |
| E45 | R2 | runtime/engine.py::__main__ | Polling G3 | G3 docs pendientes | KEEP | COMPOSE | Worker service llm_worker | T01,T03 | No reemplazar por R3 |
| E46 | R2 | apps/llm_workers/sync_bridge.py::execute_chunk | Bridge G3 | G3→provider | KEEP | ACTIVO | Snapshot CTX, respuesta JSON por miembro | T03 | execute(node) no productivo |
| E47 | Legacy compartido | apps/llm_workers/sync_bridge.py::execute | Bridge nodo legacy | Legacy consumers | HISTORICO_COMPAT | EXISTE_NO_G3 | Mantener aislado; no reintroducir fallback | T06 | Censo consumidores |
| E48 | R2 | apps/bootstrap/provider_stack_factory.py | Provider stack | runtime.engine | KEEP | ACTIVO_G3 | G3 llama cache_db_path=None | T03 | Default cache sigue riesgoso otros callers |
| E49 | R2 | apps/llm_workers/adapters.py | Groq provider | provider_stack_factory | KEEP | ACTIVO_G3 | Fake HTTP test; real solo con autorización | T03 | No credenciales en Git |
| E50 | R2 | apps/llm_workers/cache_provider.py | Cache v1 | Provider stack opcional | NO_G3_CACHE | DESACTIVADA_G3 | W08-3 abierto; no habilitar | T03 | No borrar esquema a ciegas |
| E51 | R2 | apps/llm_workers/rate_limiter.py | Cuotas | provider stack | KEEP | ACTIVO_G3 | SQLite quota state local | T03 | No saltear presupuesto |
| E52 | R2 | runtime/chunk_staging.py | Staging | G3→receipts | KEEP | ACTIVO | PRESERVE bypass / TRANSLATE | T03,T05 | No inferir ciencia |
| E53 | R2 | runtime/publication_pipeline.py | Publicación | G3→G5 | KEEP | ACTIVO | Publish→finalize→FSM | T03,T04 | No ACID cross SQLite |
| E54 | R2 | infra/db/staged_publication.py | Materialización idempotente | queue/materialized | KEEP | ACTIVO | Receipts/projections por miembros | T03,T04 | Verificar generación |
| E55 | R2 | infra/db/control_repo.py | Queue/leases/receipts | OCR/G3/recovery | KEEP | ACTIVO | Autoridad task+attempt, UNKNOWN | T03,T05 | No reutilizar recovery legacy |
| E56 | R2 | infra/db/fsm_repository.py | FSM | OCR/G3/G5 | KEEP | ACTIVO | Versiones CAS | T02,T05 | Sin falso COMPLETED |
| E57 | R2 | infra/db/materialized_repo.py | Proyecciones | G3/G5 | KEEP | ACTIVO | Sólo versión/generación vigente | T04 | No resultados de otra generación |
| E58 | R2 | infra/db/connection.py | SQLite path resolver | Todos | KEEP | ACTIVO | SQLITE_STATE_DIR redirecciona infra/db/*.db | T01 | Validar documents.db |
| E59 | R2 | infra/db/bootstrap.py | DB bootstrap | Todos | KEEP | ACTIVO_CON_PRECAUCION | Crea 4 DB base; perfil DB on demand | T01 | Solo disposable sin inventario real |
| E60 | R2 | infra/db/schema_*.sql | Esquemas por plano | bootstrap | KEEP | ACTIVO | No reescribir schema para converger | T01 | Grupo files |
| E61 | R2 | apps/compiler/__main__.py::AssemblerWorkerDaemon | Worker G5 | projections→PDF | KEEP | ACTIVO_COMPOSE | Fencing/heartbeat/compile/publish | T04,T05 | Mismo AST/queue |
| E62 | R2 | core/compiler/context_resolver.py | CQRS resolver | G5 | KEEP | ACTIVO | AST + proyecciones | T04 | No necesita breadcrumbs LLM |
| E63 | R2 | core/compiler/service.py | CompilationService | G5 | KEEP | ACTIVO | TeX+assets | T04 | No segundo renderer |
| E64 | R2 | core/compiler/assembler.py | Ensamblador lógico | G5 | KEEP | ACTIVO | Assembles context/payload | T04 | Tolerancia según oráculos |
| E65 | R2 | core/compiler/rendering/* | Render geometry/assets | G5 | KEEP | ACTIVO | Mapeo y assets actuales | T04 | Grupo |
| E66 | R2 | apps/compiler/tectonic_runner.py | Compilador físico | G5 | KEEP | ACTIVO | Tectonic real en testigo | T04 | No monkeypatch para test real |
| E67 | R2 | infra/db/assembly_recovery.py | AssemblyLeaseRepository | G5/reconciler | KEEP | ACTIVO | CAS/lease, promotion OS | T04,T05 | FS↔DB no ACID |
| E68 | R2 | apps/daemons/reconciler.py | Recuperación | queue/fsm/event | KEEP_VERIFICAR | COMPOSE | Distinguir G3 vs legacy en recovery | T05 | No retry UNKNOWN |
| E69 | R2 | runtime/sweeper.py | Sweeper/WAL | queue/fsm | KEEP_VERIFICAR | COMPOSE | TTL stalled y WAL | T05 | No restaurar G3 incierto |
| E70 | R2 | runtime/resumer.py | Resume manual | CLI resume | KEEP_VERIFICAR | CLI | Solo disposición autorizada | T05 | Cuidado STALLED/UNKNOWN |
| E71 | R3 | apps/llm_workers/__main__.py::LLMWorkerDaemon | Executor alternativo R3 | Legacy queue | NO_PRODUCTIVO | NO_EN_COMPOSE | No segundo motor | T06 | No borrar sin censo |
| E72 | R3 | apps/llm_workers/__main__.py::TaskLeaseHeartbeat | Heartbeat R3 | R3 daemon | ADAPT_CONDICIONAL | NO_EN_G3 | G3 y G5 tienen leases propios | T05 | No transplantar literal |
| E73 | R3 | runtime/admission_mechanism.py | RSS admission | R3 | ADAPT_CONDICIONAL | NO_EN_G3 | Secuencial pre-claim; G3 threadpool | T05 | Requerir brecha F18-02 |
| E74 | R3 | runtime/backpressure_mechanism.py | Wait backpressure | R3 | ADAPT_CONDICIONAL | NO_EN_G3 | Secuencial HOLD de pull | T05 | No presume equivalencia |
| E75 | R3 | runtime/coordinated_shutdown.py | Shutdown mechanism | R3 | ADAPT_CONDICIONAL | NO_EN_G3 | Adoptar solo con test necesidad | T05 | No cuarto daemon |
| E76 | R3 | runtime/operational_visibility.py | Observabilidad | R3 | ADAPT_CONDICIONAL | NO_EN_G3 | Logs adecuados para G3 si falta cobertura | T05 | No nuevo telemetry backend |
| E77 | R3 | core/execution/admission.py | Admisión contrato | R3 | LIBRERIA_COMPAT | EXISTE | Capacidad no ejecutor | T06 | Mantener protocolos |
| E78 | R3 | core/execution/cancellation.py | CancellationToken | R3 | LIBRERIA_COMPAT | EXISTE | No afirmar remote cancellation | T05 | No retry timeout |
| E79 | R3 | core/execution/coordination.py | Primitivos coordinación | R3 | LIBRERIA_COMPAT | EXISTE | Reuso condicionado | T06 | Sin daemon entero |
| E80 | Root | docker-compose.yml | Compose base | daemons | ADAPT_OPERACION | ACTUAL_BENCHMARK_1 | Selecciona G3 pero inválido solo para G3 real | T01 | Sin override STOP |
| E81 | Root | docker-compose.runtime.yml | Override runtime | daemons | KEEP_VERIFICAR | ACTUAL_BENCHMARK_0 | Mounts state/data/output; !override/!reset | T01,T02 | Necesita Compose compatible |
| E82 | Root | docker-compose.golden.yml | Override parcial histórico | llm_worker/assembler | NO_ROOT_OFICIAL | NO_ACREDITADO | No promover por nombre golden | T01 | No probado completo |
| E83 | Root | Dockerfile | Imagen runtime | Compose | KEEP_VERIFICAR | ACTUAL | Tectonic 0.15 pin release; instalación en build | T01,T04 | Digest de imagen y caches |
| E84 | Lab | apps/lab/offline_pdf_lab.py | Smoke foreground real | CLI --run | KEEP_LAB | HISTORICO_B03 | Real OCR, Tectonic, fake HTTP; image/zip pinned | T07 | No prueba multiproceso |
| E85 | Lab | apps/lab/g3_fake.py | Fake Groq controlado | G3 | KEEP_LAB | EXISTE | Loopback/private opt-in, DB manifest | T03 | No egress/costo real |
| E86 | Root | pyproject.toml | CLI packaging | apps.cli.main:main | KEEP | ACTIVO | Entry point translator-pdf | T01,T06 | Revisar scripts externos |
| E87 | Root | apps/api/server.py | API stub | — | NO_ROOT | STUB_1_LINE | No API productiva acreditada | T06 | No inventar servicio |
| E88 | Root | apps/ocr_workers/router.py | OCR legacy stub | — | NO_ROOT | STUB_1_LINE | No confundir con OCRRouterDaemon | T06 | No borrar sin censo |
| E89 | Bench | apps/benchmark/__main__.py | Benchmark | Harness | KEEP_LAB | NO_PRODUCTIVO | Fuera de whitelist operativa | T06 | No declarar ruta alternativa productiva |
| E90 | Bench | tools/evaluation/* | Regresión/oráculos | Test harness | KEEP_LAB | NO_PRODUCTIVO | Separado de operación | T06 | No alterar baselines |
| E91 | Draft | runtime/legacy_context_recovery.py (#41) | Recuperación legacy | No en base | DEFER_PR | DRAFT_UNMERGED | Solo si legacy real requiere recovery receipts | C3 | Nunca merge stack completo |
| E92 | Draft | infra/db/runtime_protocol_fence.py (#42) | Fencing de runtimes incompatibles | No en base | DEFER_PR | DRAFT_UNMERGED | Considerar downgrade/restart old writer sobre misma DB | C0/C3 | No equiparar preflight sin fence activada |
| E93 | Draft | infra/db/runtime_cutover_approval.py (#43) | HMAC gate de cutover | No en base | DEFER_PR | DRAFT_UNMERGED | Solo si #42 y ceremonia necesaria | C3 | Firma no IAM |
| E94 | Draft | infra/db/frozen_bundle_audit.py (#44) | Auditor offline interplanos | No en base | DEFER_EVALUACION_INDEPENDIENTE | DRAFT_UNMERGED | Puede servir sin #42/#43 para bundle real | C3 | No snapshot live consistente automático |

## 3. Responsabilidades exclusivas y anti-duplicación

| Hecho | Única autoridad lógica seleccionada | Producer | Consumidor | Lo que NO hacer |
|---|---|---|---|---|
| Identidad PDF | SHA256 bytes en admisión | `apps/cli/pdf_inbox.py` | OCR/FSM | `--job-id` alternativo |
| Extracción/AST y perfil | ASTRegistry + perfil en documents.db | `OCRRouterDaemon` + factory PyMuPDF | G3/G5 | Orquestador `TranslationPipeline` R1 duplicado |
| Plan+contexto+tareas | queue.db (`DurableContextPlanRepository`) | OCR | Engine | Generar otro plan desde CLI |
| Claim/efecto/receipt | queue.db / G3 claims y receipts | `runtime/engine.py` | materializer/recovery | `AsyncDispatcher` / `LLMWorkerDaemon` como escritor paralelo |
| Proyecciones | materialized.db con receipts G3 | publication_pipeline | CQRS G5 | Otro journal de resultado sin autoridad |
| Estado FSM | fsm.db + CAS | command handlers | OCR/G3/G5/sweeper | `COMPLETED` como ciencia |
| PDF | salida en volumen y publicación fenced G5 | G5/Tectonic | CLI/operador | PDF fake como traducción/ciencia |
| Incertidumbre | estado e historial causal persistentes | Engine/Reconciler según contrato | operador | retry automático de `G3_EXTERNAL_UNKNOWN` |

## 4. Composición mínima autoritativa

```text
PRODUCTO: apps.cli.main:main / translate
   ├─ apps.cli.pdf_inbox.submit_pdf_to_inbox
   └─ data/inbox compartido
       └─ apps.ocr_router.__main__:OCRRouterDaemon
          ├─ apps.bootstrap.pipeline_factory:build_extraction_pipeline
          ├─ core.normalization.enrichers.context_enricher
          ├─ core.chunking.contextual_plan:prepare_contextual_plan
          └─ ASTRegistry + DurableContextPlanRepository
             └─ runtime.engine:run_pipeline
                ├─ runtime.chunk_staging:stage_claimed_unit
                ├─ apps.llm_workers.sync_bridge:execute_chunk
                └─ runtime.publication_pipeline:advance_staged_document
                   └─ apps.compiler.__main__:AssemblerWorkerDaemon
                      └─ CQRSAssemblyContextResolver + CompilationService
                         └─ HostTectonicRunner + PDF publicado

TRANSVERSALES: apps.daemons.reconciler / runtime.sweeper
MODALIDAD CONTROLADA: apps.cli.pdf_product (llama las MISMAS clases)
NO PRODUCTIVOS: R1 AsyncDispatcher/TranslationPipeline y R3 LLMWorkerDaemon
```

## 5. Registro de consumidores que falta comprobar antes de retirar

Para `E02/E06/E09/E13/E47/E71`, inspeccionar importadores y lanzadores en todo el árbol (`apps`, `core`, `runtime`, `tests`, `tools`, `configs`, workflows, Docker y empaquetado), además de procesos externos si se conoce instalación viva. El hallazgo de una referencia **no** implica actividad: clasificarla como `ENTRYPOINT_PRODUCTIVO`, `LIBRERIA_TRANSITIVA`, `TEST/LAB`, `DOC`, `EXTERNO_DESCONOCIDO`.

```bash
rg -n 'AsyncDispatcher|LLMWorkerDaemon|handle_translate_async|build_pipeline\(|TranslationPipeline\(' apps core runtime tests tools configs .github pyproject.toml
rg -n 'apps/llm_workers/__main__|core/pipeline/orchestrator|runtime/engine.py|apps/compiler/__main__|apps/ocr_router/__main__' docker-compose*.yml Dockerfile .github apps
```

Las declaraciones `EXTERNO_DESCONOCIDO` o `NO_EN_COMPOSE` no autorizan borrar símbolos. Las filas de grupo `/*` no sustituyen al listado de cada archivo cuando se vaya a editar esa zona: antes de un PR, desplegar los módulos concretos y consumidores impactados.

## 6. Definición de cierre y política de revisión

Una fila `KEEP` solo cambia a `VERIFICADO_EN_TOPOLOGIA` con commit, proceso/servicio, env y paths efectivos, testigo que use productor/consumidor reales y evidencia publicada. Una fila `ADAPT_CONDICIONAL` **no** exige trabajo si no aparece el falsador especificado; evitar sobreingeniería. Una fila `NO_PRODUCTIVO` se considera cerrada para este hito solo cuando no figura en el root soportado y sus consumidores son conocidos o su incertidumbre está declarada sin despliegue compatible; eliminar código es fase distinta.

**Invariantes de cierre operativo:** CLI→OCR→G3→G5 multiproceso real sobre volúmenes aislados, mismo documento/generación, snapshots/receipts/proyecciones coherentes, Tectonic físico, recuperación safe/fail-closed, ausencia de ejecutor R1/R3 productivo. **No implica** validez científica, aceptación lingüística, W09 ni producto listo.

**Actualización:** la trazabilidad de avance se registra en el tablero **§8.1 del plan** (C0–C4 y T01–T07), sin agregar 94 columnas o duplicar un tablero en esta matriz. Solo al cambiar una fila se actualizan su disposición/estado y la evidencia concreta de un consumidor o testigo, con SHA y fecha. Esta versión mantiene honestamente sus estados históricos; no hay evidencia nueva de runtime. Correcciones documentales v1.0.x; cambio de disposición, contrato o alcance v1.x. Nunca declarar `RETIRE` definitivo sin censo y autorización puntual. Todos los enlaces a código tienen sujeto `6a5ee418…` y deben revisarse contra el HEAD antes de modificar.

## 6.1 Convención mínima de actualización de la matriz

**La fuente única de avance es el plan §8.1**: allí se actualizan `PENDIENTE / EN_CURSO / BLOQUEADO / COMPLETADO / NO_APLICA` para C0–C4 y T01–T07. **Esta matriz no copia esos estados en sus 94 filas**. La matriz expresa decisiones de composición por componente, no el estado de una campaña de tests. `KEEP` es una disposición, no `COMPLETADO`.

Cuando una ejecución, modificación o inventario cambie una fila de esta matriz:

1. Conservar su ID `E01…E94` y su path; actualizar exclusivamente la fila impactada (consumidor real, evidencia AS-IS, decisión TO-BE, testigo y motivo), con referencia verificable a **commit probado + testigo del plan + fecha**. Si el resultado revela un consumidor imprevisto, registrar esa evidencia antes de cambiar `NO_PRODUCTIVO`, `ADAPT_CONDICIONAL` o `RETIRE_CANDIDATE`.
2. No marcar `VERIFICADO_EN_TOPOLOGIA` sin ejecución real de su productor y consumidor sobre el root soportado. Un PASS de CI anterior, un import estático o una ejecución foreground simulada no prueban el modo Compose.
3. Nunca eliminar implementaciones por una disposición `NO_PRODUCTIVO`: la retirada física exige censo de referencias y autorización puntual. Un símbolo históricamente R1/R3 puede ser una librería compartida legítima.
4. Registrar el avance de C0–C4 y T01–T07 **solo en plan §8.1**; actualizar allí también el historial y el enlace a evidencia del mismo cambio. Si no cambia ninguna fila aquí, **no editar la matriz solo para incrementar porcentajes**.
5. Versiones: v1.0.x para precisión y evidencia nueva sin cambio de alcance; v1.x para cambio sustantivo de contratos, disposiciones o criterios. No modificar el identificador del archivo por una revisión menor. No editar oráculos FROZEN.

**Historial de esta matriz:**

| Fecha | Versión | Cambio | Evidencia |
|---|---|---|---|
| 2026-11-09 | v1.0.0 | Inventario inicial de 94 entradas basado en #40 integrado | `adbb61a88c179d3a11a31e78cd470b590024a4be` |
| 2026-11-09 | v1.0.1 | Formato Markdown corregido; convención ligera de disposición y enlace al tablero del plan | Commit documental; sin pruebas de ejecución nuevas |

**Límites documentales:** #41–#44 Draft no merged; #45 closed; `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md` del owner, D-1/D-2, Atlas y NADR FROZEN conservan primacía. No se modifican scripts, bases, oráculos, Compose, PRs ni despliegues al publicar esta matriz.
