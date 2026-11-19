# HITO_0.1_RUTA_OPERATIVA_Y_PERIMETRO.md

**Estado:** IN_PROGRESS v1.0.2  
**Fecha de emisión:** 2026-11-18  
**Fecha de congelamiento:** N/A  
**Etapa:** PDF→PDF Product Readiness — Fase 0 (auditoría forense). La numeración formal de fase, si corresponde, queda sujeta a gobernanza metodológica.  
**Tipo de artefacto:** Forensic Discovery / Flow Audit  
**Naturaleza:** Read-only. No prescribe código, diseño, cambios de arquitectura ni implementación.  
**Baseline de inspección:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`. Las observaciones posteriores deben citar su SHA de fuente.  
**Evidencia forense vinculante:** handoff de convergencia PDF→PDF, metodología general, metodología HITOs, ADR/NADR FROZEN aplicables, informes TST-STAB y código de `main`.  
**Mandato:** Determinar la ruta ejecutable real, sus fronteras y dependencias, la cobertura necesaria de auditoría y las incertidumbres que impiden planificar por evidencia una traducción PDF→PDF STEM utilizable.  
**Síntesis:** Inicio documentado de la auditoría. Se han identificado contratos y acoplamientos concretos en G3 y CLI, pero **aún no existe inventario exhaustivo, matriz consolidada ni cierre forense**.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-18 | Apertura del HITO, mandato, baseline, método, evidencias iniciales y condiciones de cierre; sin declarar una auditoría completada. |
| 1.0.1-IN_PROGRESS | 2026-11-18 | Primera reconciliación estática: Atlas histórico versus main y grafo de productores/consumidores de la ruta D-1/D-2. La auditoría sigue abierta. |
| 1.0.2-IN_PROGRESS | 2026-11-18 | Segundo barrido estático: censo de rutas ejecutables y consumidoras fuera del Atlas, factories, benchmark/CV, stubs y alcance real de testigos T06/W08; conserva límites no verificados. |

## 1. RESUMEN EJECUTIVO

El objetivo es observar la composición PDF→PDF desde admisión hasta PDF publicado y los componentes que realmente pueden influir en ese recorrido, incluida la herencia legacy y las obligaciones FROZEN aplicables.

**Hallazgo central de apertura:**

> La convergencia operativa sobre fake está documentada, pero el contrato real de inferencia, los controles de gasto, la identidad de la generación y la fidelidad STEM todavía requieren reconciliación causal contra el código y la evidencia de ejecución. No corresponde fijar tareas ni seleccionar nuevas abstracciones antes de la Fase 0.

**Observaciones iniciales reconciliadas:** el constructor G3 usa modelo/ventana primarios literales; el builder acepta `SWITCH_MODEL` conservando `model_name`; el adaptador envía ese modelo; y el foreground devuelve el PDF de una generación `COMPLETED`. También se comprobó estáticamente el grafo de composición y consumidores críticos del Atlas sobre el corte de `main`. **La inspección estática NO acredita ejecución física, traducción real ni ausencia de otros consumidores.**

**Veredicto actual:** `IN_PROGRESS`; no habilita ADR, NADR, plan ni PR de implementación.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

- **Observed:** comportamiento constatado por lectura del código, estructura y, cuando exista, pruebas bajo un SHA identificado.
- **Required:** obligación atribuible a fuente normativa vigente, explicitada con regla/alcance; no deducida de preferencia de diseño.
- **Decision:** acuerdo o conclusión histórica con autoridad y alcance comprobables; `FROZEN` no significa que todo esté implementado.
- No convertir test con fake, CI verde o PDF con cabecera válida en prueba de traducción real o fidelidad científica.
- No inferir `NO IMPLEMENTADO` de una búsqueda incompleta ni `RESUELTO` de la existencia de una clase.
- Ningún HITO accede al corpus privado ni altera sellos, GT, SQLite de uso o efectos de proveedor. Evidencia de runtime no disponible se clasifica `NO VERIFICABLE`.
- Este HITO es un arranque documental, **no** una auditoría declarada como realizada de todo el árbol.

### 2.2 Método forense y finitud

1. Congelar el SHA base y leer metodología, decisiones y handoffs relevantes. **El Atlas de convergencia es el mapa inicial, no una fuente de verdad automática para HEAD**: comparar su corte `6818e86` con `main@1d21cfe` y seguir rutas/símbolos reales.
2. Delimitar el grafo operativo `CLI → OCR → plan/AST → G3 → materialización → G5 → PDF` y las fronteras de error/reanudación.
3. Enumerar composición y consumidores mediante entrypoints, imports, factories, configuración, repositorios, tests y referencias dinámicas conocidas; declarar límites de búsqueda.
4. Inventariar capacidades por frontera: `CONECTADO`, `IMPLEMENTADO_NO_CONECTADO`, `LEGACY_CON_CONSUMIDOR`, `SOLO_TEST`, `NO_VERIFICADO` o `AUSENCIA_CONFIRMADA_EN_PERIMETRO`. Una clasificación no decide su destino.
5. Contrastar contratos y decisiones de W06/W08, F18, G3/G5, TST-STAB y el handoff existente con las implementaciones y tests actuales; registrar `Observed/Required/Decision`.
6. Documentar escenarios no verificables sin fingir pruebas físicas ni ejecutar proveedor/corpus en esta fase.
7. Emitir evidencias estables y gaps únicamente ante discrepancias fundamentadas; transferir aspectos de otras superficies a HITOs específicos cuando corresponda.
8. Cerrar cuando el perímetro y sus consumidores relevantes estén enumerados y las incertidumbres y límites explícitos sean suficientes para que los HITOs siguientes y la gobernanza no reinventen soluciones existentes.

**Control de alcance:** se inspeccionará todo componente *relevante para el recorrido y sus contratos*, no cada archivo incidental del repositorio con el mismo nivel de profundidad. Los hallazgos fuera de perímetro se derivan, no se absorben sin límite. **Limitación de búsqueda:** en este barrido la consulta indexada de símbolos conocidos no devolvió resultados aun para símbolos presentes en archivos leídos; por tanto, no se usa ese mecanismo para afirmar ausencia de consumidores. La evidencia positiva proviene de archivos individuales y el árbol Git; los consumidores dinámicos/extras todavía están por cerrar.

## 3. ALCANCE AUDITADO

| Superficie | Archivos/entrada inicial | Cobertura en esta apertura |
|---|---|---|
| CLI/foreground | `apps/cli/main.py`, `apps/cli/pdf_product.py` | AUDITADO FOCAL, no exhaustivo |
| G3/prompt/proveedor | `runtime/engine.py`, `core/validation/budget.py`, `apps/llm_workers/prompt_builder.py`, `apps/llm_workers/adapters.py`, `apps/llm_workers/sync_bridge.py`, `apps/bootstrap/provider_stack_factory.py` | AUDITADO FOCAL, no exhaustivo |
| Plan y contrato de reutilización | `core/chunking/manifest_contract.py`, `core/prompting/inference_identity.py` | REFERENCIADO / inspección parcial |
| OCR, B02, normalización, AST, clasificadores | `apps/ocr_router/`, `apps/bootstrap/pipeline_factory.py`, `core/ast/` y dependencias | POR AUDITAR |
| G5 y recursos científicos | `apps/compiler/`, `core/compiler/`, perfiles, renderer y activos | POR AUDITAR |
| Estado y recuperación | `infra/db/`, `runtime/recovery.py`, `runtime/resumer.py`, `runtime/sweeper.py`, reconciler, W06 | POR AUDITAR |
| Entornos | `docker-compose.yml`, `docker-compose.runtime.yml`, bootstrap, host Windows, Tectonic/cachés | REFERENCIADO; runtime físico no verificado |
| Oráculos y suites | `tests/`, `.github/workflows/`, `reports/certification/`, issue #34 | REFERENCIADO; evidencia científica real no re-ejecutada |
| Legacy | R1/R3, CLI histórica, `build_pipeline`, benchmarks y consumidores potenciales | AUDITADO FOCAL: roots y algunos consumidores; búsqueda global incompleta |
| Roots complementarios | `pyproject.toml`, `apps/benchmark/`, `apps/api/`, `apps/ocr_workers/`, `tools/evaluation/`, `apps/lab/`, `.github/workflows/` | AUDITADO FOCAL: entradas y alcance, no invocaciones externas |

**Primera reconciliación del perímetro con el Atlas (inspección estática, 2026-11-18):**

- Fuente descriptiva: `ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` v1.0.2, corte `6818e86e21b14e77a606f0c863e9c199b4627601`. Su tabla §3 y grafo §1 sirvieron para seleccionar símbolos concretos, **sin reemplazar su lectura en main**.
- Comparación Git `6818e86...1d21cfe`: 78 rutas cambiadas globalmente; de las superficies de código `apps/`, `core/`, `infra/`, `runtime/` y los cuatro `docker-compose*.yml`, **solo** se modificaron `runtime/recovery.py` y `runtime/resumer.py`. Ambas incorporan `contextlib.closing` para conexiones de SQLite (PR #65). No equivale a probar las rutas en el SO actual.
- Se inspeccionaron directamente los entrypoints/productores/consumidores listados en §6; se distingue `AUDITADO FOCAL` de `POR AUDITAR` aunque la ruta esté nombrada en el Atlas.
- **No se constató runtime real, disponibilidad de Tectonic o modelos comerciales, contenido de bases privadas, ni invocaciones externas al repositorio.**

**Segunda reconciliación — raíces auxiliares y consumidores compartidos (estática, mismo SHA de main):**

- El árbol Git contiene **1.094 archivos versionados**. El inventario de rutas no equivale a auditar semánticamente cada archivo. En la inspección focal se leyeron composición, CLI, servicio OCR, stack de proveedor, ejecutables legacy, benchmark, CV, laboratorio y testigos T06/W08.
- `pyproject.toml` registra `translator-pdf = "apps.cli.main:main"`. La CLI soportada solo registra `translate/sweep/resume/status`, y `handle_translate_async` lanza el error `C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED`.
- `apps/cli/legacy_translate_async.py::handle_translate_async` **sí** llama `build_pipeline`; por tanto, el factory histórico `apps/bootstrap/pipeline_factory.py::build_pipeline` tiene al menos un consumidor versionado, aunque no el comando productivo soportado. No se concluye si hay callers externos.
- `apps/llm_workers/__main__.py::LLMWorkerDaemon` conserva un root R3 directamente ejecutable y mecanismos de admission/backpressure/shutdown, diferentes de la composición del G3 seleccionado. El test T06 verifica los launchers versionados y no demuestra ausencia global de consumidores externos.
- `apps/benchmark/__main__.py` inicia un experimento Groq y llama el `build_extraction_pipeline` de producción; los runners Groq/Gemini consumen `AsyncDispatcher` y `build_provider_stack`. El benchmark **no** es una ruta productiva seleccionada. Su carga de un PDF físico y su posible egress externo requieren autorización propia; ningún experimento fue ejecutado en esta auditoría.
- `tools/evaluation/run_regression.py` también usa `build_extraction_pipeline()` para comparar AST contra oráculos: valida extracción/topología, **no** prueba que una traducción G3→G5 sea fiel. El CI científico invoca ese runner y el pytest predeterminado excluye `e2e`.
- `apps/bootstrap/provider_factory.py::ExtractionProviderFactory` resuelve PyMuPDF en la composición de extracción; existe al menos esa implementación reutilizable. `apps/api/server.py`, `apps/ocr_workers/router.py`, `configs/llm.yaml` y `configs/pipeline.yaml` están vacíos en este corte: su nombre no constituye una API/worker/configuración operativa.
- `apps/lab/offline_pdf_lab.py` exige `--network none` y fake local; `apps/lab/convergence_compose_preflight.py` analiza topología/seguridad de laboratorio, no ejecuta E2E; `docker-compose.runtime.yml` es un override que **todavía debe** validarse como Compose efectivo. No transformar un test offline en prueba comercial.

**Evidencia de alcance:** los testigos `tests/unit/test_c4_t06_supported_roots.py` y `tests/integration/test_w08_cli_foreground_single_generation_offline.py` se inspeccionaron como **código de prueba**, no se ejecutaron en esta pasada. T06 declara expresamente que solo prueba selección estática en launchers soportados; W08 reemplaza parser, transporte LLM y Tectonic aunque conserva la composición y SQLite reales.

**Fuera de alcance en Fase 0:** cambio de código, migración de datos, purga, traducción comercial, campaña de benchmark científico, carga de PDF de terceros y nuevos despliegues.

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Rol |
|---|---|---|
| Normativa | `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` | Secuencia, plantilla, criterio de evidencia y cierres |
| Normativa | `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, ADR/NADR aplicables | Propósito del producto e invariantes |
| Forense/documentación vigente | `docs/architecture/adr/pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` (corte `6818e86`, §§1–6 y 10) | Mapa histórico de entrypoints, datos, consumidores y pruebas de impacto; insumo a contrastar, no certificación de `main` |
| Histórico y diff | [Comparación 6818e86…1d21cfe](https://github.com/RDsanchez-git/translator_pdf/compare/6818e86e21b14e77a606f0c863e9c199b4627601...1d21cfe958cc1de8a33824fed748cd6fe9260f42) | Cambio de superficies entre Atlas y baseline de la auditoría |
| Forense/documentación vigente | `docs/architecture/adr/pipeline-stabilization/handoff/README.md` y `EVIDENCIA_Y_CIERRE.md` | Decisión D-1/D-2, límites fake y actas históricas |
| Forense/documentación histórica | `docs/architecture/adr/tests_stabilization/`; `docs/architecture/adr/phase-18/` | Alcances de tests, mecanismos, decisiones y obligaciones existentes |
| Código observado | `runtime/engine.py`, `core/validation/budget.py`, `apps/llm_workers/prompt_builder.py`, `apps/llm_workers/adapters.py`, `apps/cli/pdf_product.py` | Primeros testigos concretos; falta verificar consumidores completos |
| Fuente de restricción | [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34) | Evaluación científica/corpus diferidos y custodia |
| Evidencia pendiente | Host Windows, APIs y proveedores reales, archivos de corpus privados | No verificada por la auditoría de apertura |

## 5. MAPA DE FLUJOS OBSERVADOS

**Topología tomada del Atlas y contrastada en código estático; pendiente de auditoría completa de consumidores y estado:**

```text
CLI/admisión
  → OCR + perfil → AST + ChunkPlan + snapshots durables
  → G3 runtime.engine → claims/leases → SyncProviderBridge
  → proveedor / PRESERVE → recibos y proyecciones
  → FSM READY_FOR_ASSEMBLY → G5/renderer/Tectonic → PDF
```

**Primer contraste de aristas entre productores y consumidores en main (no es ejecución):**

| Tramo | Productor observado → consumidor | Archivo/símbolo leído |
|---|---|---|
| Entrada admitida | `handle_translate` → `submit_pdf_to_inbox`; `--run` → `run_admitted_pdf` | `apps/cli/main.py`, `apps/cli/pdf_inbox.py`, `apps/cli/pdf_product.py` |
| Foreground compartido | `_ingest` → `OCRRouterDaemon._process_document`; `_run_g3` → `runtime.engine.run_pipeline`; `_run_g5` → G5 compartido | `apps/cli/pdf_product.py` |
| OCR → planes | `build_extraction_pipeline`/perfil → `prepare_contextual_plan` → `ASTRegistry.register_ast` + `DurableContextPlanRepository.enqueue_verified` | `apps/ocr_router/__main__.py`, `apps/bootstrap/pipeline_factory.py`, `core/chunking/contextual_plan.py`, `infra/db/context_snapshot_repo.py` |
| Plan → G3 | `ASTRegistry.get_document_ast` + `DurableContextPlanRepository.load_verified` antes del proveedor; `stage_claimed_unit` sobre unidades `PRESERVE` o traducibles | `runtime/engine.py`, `runtime/chunk_staging.py` |
| G3 → proveedor | `SyncProviderBridge.execute_chunk` construye/valida protocolo; `build_provider_stack` compone proveedor; G3 no usa caché legacy | `apps/llm_workers/sync_bridge.py`, `apps/bootstrap/provider_stack_factory.py`, `runtime/engine.py` |
| G3 → publicación | `advance_staged_document` → `publish_staged_plan` y `finalize_published_plan` → transición de FSM | `runtime/publication_pipeline.py`, `infra/db/staged_publication.py` |
| G5 → PDF | `AssemblerWorkerDaemon` → `AssemblyLeaseRepository`, `CQRSAssemblyContextResolver`, `CompilationService`, `HostTectonicRunner` | `apps/compiler/__main__.py`, `infra/db/assembly_recovery.py`, `core/compiler/`, `apps/compiler/tectonic_runner.py` |

**Ramas cuyo efecto debe observarse:** rechazo B02; integridad de plan y contexto; unidades `PRESERVE`; `G3_EXTERNAL_UNKNOWN`; reanudación `RESULT_STAGED`; FSM `COMPLETED` y posible reutilización de una salida previa; lease G5; rechazo de PDF inexistente/inválido. Estas aristas **no atribuyen éxito E2E físico**.

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

La tabla de §3 es **un índice de superficies**, no un inventario terminado de implementaciones. Los HITOs posteriores o la expansión del presente deben acreditar sus dueños, entradas, consumidores, contratos y efectos. `NO_VERIFICADO` es una salida válida; ausencia solo después de buscar consumidores concretos.

**Roots y composición comprobados estáticamente en main:**

| Root/componente | Selección real | Evidencia / límite |
|---|---|---|
| CLI `translate` | Por defecto **solo admite**; `--run` opt-in ejecuta los componentes OCR/G3/G5 en foreground | `apps/cli/main.py::handle_translate`; no implica inferencia si la generación ya está publicada |
| OCR daemon | `apps/ocr_router/__main__.py` ejecuta `OCRRouterDaemon` | Ruta normal del contenedor y foreground enlazados a OCR |
| G3 daemon | `docker-compose.yml` servicio `llm_worker` ejecuta `runtime/engine.py` | Nombre de servicio no igual a `apps/llm_workers/__main__.py` |
| G5 daemon | `docker-compose.yml` `assembler` ejecuta `apps/compiler/__main__.py` | Fencing sobre PDF físico; calidad STEM por investigar en HITO 0.6 |
| Composición de runtime | `docker-compose.runtime.yml` fija `IS_BENCHMARK=0` y raíces SQLite/volúmenes para worker | Base declara `IS_BENCHMARK=1`; no ejecutar base sola ni atribuir integración real a la composición no ensayada |
| R1 y R3 | `build_pipeline` y `LLMWorkerDaemon` existen; R1 no se ofrece en la CLI canónica y R3 no es el comando del `llm_worker` soportado | **No equivalen a código muerto**: comprobar consumidores de tests/benchmarks y externos desconocidos antes de decidir sobre legacy |

**Matriz de consumidores observados fuera de la ruta positiva (no autoriza eliminación):**

| Capacidad / raíz | Consumidor positivo constatado | Clasificación observada | Límite |
|---|---|---|---|
| `build_pipeline` / `TranslationPipeline` | `apps/cli/legacy_translate_async.py` | `LEGACY_CON_CONSUMIDOR` | El símbolo de compatibilidad en `apps/cli/main.py` rechaza, pero no se auditó todo launcher externo |
| `AsyncDispatcher` | `apps/benchmark/runners/groq_runner.py`, `gemini_runner.py`; composición R1 | `CONSUMIDOR_BENCHMARK/LEGACY` | No equivale a worker G3 seleccionado |
| `LLMWorkerDaemon` R3 | Root propio `apps/llm_workers/__main__.py` | `EJECUTABLE_NO_SELECCIONADO_EN_ROOTS_SOPORTADOS` | Proceso manual/external launch `UNKNOWN` |
| `build_extraction_pipeline` | OCR y foreground, además de benchmark y Continuous Verification | `COMPARTIDO_PRODUCTO_Y_EVALUACION` | Modificar el parser afecta la evaluación; se profundiza HITO 0.2/0.8 |
| `build_provider_stack` | G3, R3 y runners benchmark | `COMPARTIDO_CON_POLITICAS_DISTINTAS` | Default de caché no determina la composición G3 (`cache_db_path=None`) |
| `apps.api.server`, `apps.ocr_workers.router`, `configs/*.yaml` | Archivos vacíos | `STUB_OBSERVADO` | No inferir inexistencia de otros endpoints/configuraciones |
| `tools.evaluation.run_regression` | Workflow de CV y ejecución CLI manual | `ROOT_DE_VERIFICACION_DE_EXTRACCION` | No es pipeline PDF→PDF traducido |

**Puntos de autoridad confirmados como referencias, sin sustitución de la auditoría 0.5:** `FSMRepository.transition_to`; `ControlPlaneRepository.pick_task/stage_chunk_result/mark_g3_external_unknown`; `DurableContextPlanRepository.load_verified`; `AssemblyLeaseRepository.claim/renew/publish/recover_expired`. `runtime/recovery.py` y `runtime/resumer.py` cambiaron desde el Atlas; se observó cierre explícito con `closing(get_connection(...))` y se delega su comportamiento de recuperación a HITO 0.5.

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Dimensión | Observed (código/handoff) | Required (a reconciliar) | Decision previa |
|---|---|---|---|
| Ruta | Un foreground usa `runtime.engine` y el ensamblador existente | Ruta coherente y conservación STEM según scope/contratos | D-1/D-2 aprobadas; no segundo motor productivo |
| G3 budget | Una decisión `SWITCH_MODEL` puede terminar en `model_name` sin cambio de proveedor | No aceptar una capacidad que la petición física no satisface; norma específica aún por mapear | No se acredita un fallback multimodelo |
| Reutilización | G3 deshabilita caché legacy; `COMPLETED` puede devolver PDF existente | Identidad completa y no confundir la fuente con la generación | W08 define identidad candidata de reutilización; no autorización de replay |
| Ciencia | Fake y PDF publicado no demuestran traducción/fidelidad | `PROJECT_SCOPE` exige conservación técnica y rastreabilidad | Evaluación canónica permanece diferida según #34 |
| Selección de roots / legacy | CLI, Compose y empaquetado seleccionan G3; R1/R3/benchmarks mantienen entrypoints propios | No confundir inactividad en roots soportados con ausencia de consumidores | D-1/D-2 autorizan una sola ruta productiva sin eliminar bibliotecas históricas |
| Reutilización de parser | Benchmark y CV consumen el factory de extracción productivo | Evitar doble extracción y preservar comparabilidad/oráculos; norma particular por reconciliar | Handoff prohíbe nuevo motor productivo; CV sigue independiente de G3→G5 |

**Esta matriz es inicial y no declara cumplimiento normativo exhaustivo.**

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev preliminar | Fuente/código | Observación y límite |
|---|---|---|---|
| **E-0.1-001** | P1 | `runtime/engine.py::_create_chunk_processor` | `model_name="llama3-70b-8192"`, `primary_window_limit=8192`, `fallback_window_limit=1048576`. Disponibilidad real del modelo y capacidades de la cuenta NO verificadas aquí. |
| **E-0.1-002** | P1 | `core/validation/budget.py::PromptBudgetCalculator.calculate`; `apps/llm_workers/prompt_builder.py::PromptBuilder.build`; `apps/llm_workers/adapters.py::GroqProvider.translate` | `SWITCH_MODEL` puede ser tratado como éxito por builder, pero el envío usa `envelope.model_name`. No se acredita conmutación física de modelo; efecto operacional de una llamada real NO ensayado. |
| **E-0.1-003** | P1 | `apps/cli/pdf_product.py::run_admitted_pdf` | `COMPLETED` devuelve un PDF existente verificado por header, sin volver a ejecutar G3. Falta auditar si la generación guardada distingue configuración/idioma efectivo. |
| **E-0.1-004** | P1 | `runtime/engine.py::_create_chunk_processor`; `core/prompting/inference_identity.py::InferenceReuseIdentityV1` | Caché legacy G3 deshabilitada; identidad W08 candidata incluye idioma y config, pero no constituye autoridad de ejecución. Conexión efectiva a generación por verificar. |
| **E-0.1-005** | P1 | `apps/llm_workers/sync_bridge.py::execute_chunk`; `apps/llm_workers/adapters.py::GroqProvider.translate` | Instrucción menciona un idioma «configurado»; configuración de idioma explícita no fue acreditada en las firmas inspeccionadas. Se debe inspeccionar el resto de la ruta antes de concluir ausencia. |
| **E-0.1-006** | P1 | `apps/cli/pdf_product.py::preflight_product_run`; `docker-compose.runtime.yml`; handoff de laboratorio | Foreground exige Tectonic en PATH; runtime Docker con override documentado; no se ha demostrado un mismo entorno con Tectonic, acceso autenticado y corrida autorizada real. |
| **E-0.1-007** | P1 | `apps/cli/main.py::handle_translate/parse_arguments`, `apps/cli/pdf_product.py::run_admitted_pdf` | Admisión sin inferencia por defecto; `--run` opt-in. La rama `COMPLETED` devuelve PDF verificado sin repetir OCR/G3/G5; no se observó selección de idioma en los argumentos `translate`. |
| **E-0.1-008** | P1 | `apps/ocr_router/__main__.py::_process_document`; `infra/db/context_snapshot_repo.py::enqueue_verified` | OCR produce perfil, AST, plan contextual y snapshots; AST/queue/FSM se persisten en fronteras separadas. No se acredita atomicidad entre archivos físicos/SQLite. |
| **E-0.1-009** | P1 | `runtime/engine.py::run_pipeline`; `runtime/chunk_staging.py::stage_claimed_unit` | AST/plan/snapshots se verifican antes de inicializar proveedor; `PRESERVE` evita POST; se observó ruta `RESULT_STAGED`/completada sin inferencia y `G3_EXTERNAL_UNKNOWN` fuera de runnable. |
| **E-0.1-010** | P1 | `apps/compiler/__main__.py::_process_assembly_task`; `infra/db/assembly_recovery.py::AssemblyLeaseRepository.publish` | G5 usa lease y validación de autoridad para publicar PDF; no equivale a certificación de layout o fidelidad. |
| **E-0.1-011** | P1 | `docker-compose.yml::llm_worker/assembler`; `docker-compose.runtime.yml::llm_worker` | Servicio `llm_worker` ejecuta `runtime/engine.py`, no el R3 legacy; base mantiene `IS_BENCHMARK=1` y override declara `0`. Composición efectiva y runtime comercial siguen NO VERIFICADOS. |
| **E-0.1-012** | P2 | [Comparación Git del corte Atlas con main](https://github.com/RDsanchez-git/translator_pdf/compare/6818e86e21b14e77a606f0c863e9c199b4627601...1d21cfe958cc1de8a33824fed748cd6fe9260f42) y `runtime/recovery.py`/`runtime/resumer.py` | Únicos dos archivos modificados dentro de `apps/core/infra/runtime` y los Compose desde el corte pinneado; agregan cierre de conexión SQLite. No se deduce ejecución física actual. |
| **E-0.1-013** | P2 | `apps/bootstrap/pipeline_factory.py::build_pipeline/build_extraction_pipeline`; `apps/llm_workers/__main__.py::LLMWorkerDaemon` | Hay composición legacy y worker R3 existentes sin selección como G3 productivo en Compose; consumidores de tests, herramientas y sistemas externos aún por inventariar. |
| **E-0.1-014** | P2 | `pyproject.toml::project.scripts`, `apps/cli/main.py::parse_arguments/handle_translate_async`, `tests/unit/test_c4_t06_supported_roots.py` | El entrypoint empaquetado es la CLI canónica; T06 inspecciona estáticamente CLI/Compose/Docker y constata el rechazo R1, sin cubrir lanzadores externos ni comportamiento físico. |
| **E-0.1-015** | P2 | `apps/cli/legacy_translate_async.py::handle_translate_async`, `apps/bootstrap/pipeline_factory.py::build_pipeline`, `apps/llm_workers/__main__.py::LLMWorkerDaemon` | R1 conserva consumidor versionado distinto de CLI productiva; R3 conserva ejecución propia, admission/backpressure/shutdown. No autoriza purga ni adopción del daemon alterno. |
| **E-0.1-016** | P2 | `apps/benchmark/__main__.py::main`, `apps/benchmark/runners/{groq,gemini}_runner.py`, `tools/evaluation/run_regression.py::_run_evaluation` | La extracción productiva sirve también a benchmark y CV; bench usa modelo/proveedor externo, CV compara AST y baseline. Son consumidores con semánticas y permisos diferentes. |
| **E-0.1-017** | P2 | `apps/bootstrap/provider_factory.py::ExtractionProviderFactory.create`, `apps/bootstrap/pipeline_factory.py::build_extraction_pipeline`; `apps/api/server.py`, `apps/ocr_workers/router.py`, `configs/*.yaml` | PyMuPDF está conectado mediante factory; archivos API/worker/config nombrados existen pero están vacíos en este commit. No deben contarse como capacidades implementadas. |
| **E-0.1-018** | P2 | `apps/lab/offline_pdf_lab.py`, `apps/lab/convergence_compose_preflight.py`, `tests/integration/test_w08_cli_foreground_single_generation_offline.py` | Los testigos de laboratorio limitan red/transporte; W08 sustituye parser, transporte HTTP y compilación Tectonic. Son pruebas contractuales parciales, no ejecución científica real. |
| **E-0.1-019** | P2 | `apps/benchmark/__main__.py::main` y `GroqBenchmarkRunner.warmup` | Un root manual abre PDF físico (`[Amoretal_2023]_3hojas.pdf`) y tiene camino de inferencia Groq. Posible egress al ejecutarlo: exige permiso/privacidad; no se afirma que haya sido ejecutado. |
| **E-0.1-020** | P2 | `.github/workflows/ci.yml`, `.github/workflows/continuous-verification.yml`, `pyproject.toml::tool.pytest.ini_options` | Suite por defecto usa `-m not e2e`; workflow CV invoca `run_regression`. No inferir aptitud de producto de CI técnico PASS ni convertir CV sin corpus en PASS. |

Los IDs se reservan y no se reasignan; estos testigos son **lectura de fuentes**, no falsación ejecutada ni certificación de comportamiento real. La clasificación de severidad y cumplimiento se revalidará antes de cierre; un P1 preliminar no es una conclusión normativa.

## 14. GAPS CONSOLIDADOS

**Estado: NO CERRADO.** En la apertura no se emite una Gap Matrix global ni se determina un destino de implementación sin reconciliar consumidores y autoridad normativa. Las E-0.1-001..020 son insumos para investigación, no equivalen automáticamente a GAP confirmado o a tarea aprobada.

| Gap | Evidencia | Contrato/autoridad | Destino | Estado |
|---|---|---|---|---|
| Sin gaps formalmente consolidados en este corte | E-0.1-001..020 | Por reconciliar con normas vigentes | Por resolver tras investigación | TO BE VERIFIED |

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis a falsar | Estado |
|---|---|---|
| H-0.1-A | El fallback lógico G3 carece de ruta física de respaldo para el proveedor seleccionado | OBSERVADO en la composición inspeccionada; falta verificar consumidores alternos |
| H-0.1-B | Cambiar idioma/modelo sobre el mismo documento puede devolver una generación anterior marcada `COMPLETED` | PLAUSIBLE; requiere inspección integral de persistencia e identidad |
| H-0.1-C | El estado real de F18 y componentes legacy contiene reutilización útil no visible desde la CLI | TO BE VERIFIED |
| H-0.1-D | Extracción/ensamblado omite o rechaza casos STEM representativos más allá de los tests focales | PARCIALMENTE DOCUMENTADO; requiere auditar fronteras y evidencia |
| H-0.1-E | La ruta real tiene restricciones de gasto/egress que pueden impedir una prueba comercial controlada | TO BE VERIFIED |
| H-0.1-F | Los consumidores seleccionados por la CLI y los tres servicios Compose corresponden al grafo positivo del Atlas en el corte de main | CONFIRMADO ESTÁTICAMENTE en símbolos leídos; no E2E |
| H-0.1-G | La implementación productiva relevante cambió después del Atlas de forma sustantiva | REFUTADO para `apps/core/infra` y Compose en comparación Git; cambios focales en recuperación pendientes de HITO 0.5 |
| H-0.1-H | Solo hay un consumidor relevante de `build_pipeline`, `AsyncDispatcher` o factory de proveedores | REFUTADO PARCIALMENTE por CLI legacy y runners benchmark; censo global pendiente |
| H-0.1-I | Los scripts de benchmark y evaluación ejercen la misma garantía PDF→PDF de G3→G5 | REFUTADO por invocación de parser/dispatcher y CV extracción-only; falta observar todas las variantes de evaluación |
| H-0.1-J | No existe otro sistema externo que invoque R1/R3 o módulos de prueba | NO VERIFICABLE con archivos Git; requiere inventario de despliegues y permiso del owner |

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

- **¿Hay una ruta PDF→PDF soportada?** Sí, según handoff integrado; éxito con fake no demuestra producto real.
- **¿Está auditado su grafo completo y sus capacidades?** No; ya se contrastaron las aristas estáticas centrales del Atlas y la composición seleccionada contra `main`, pero faltan consumidores secundarios/dinámicos, las garantías de cada frontera y evidencia física.
- **¿Se autorizan cambios por los hallazgos de apertura?** No; falta cerrar la auditoría, derivar decisiones normativas y aprobar el plan.
- **¿Debe la nueva etapa inventar soluciones?** No por defecto: se exige búsqueda y clasificación de capacidades y consumidores antes de afirmar ausencia.

## 21. CIERRE DEL HITO 0.1

**Estado del HITO:** IN_PROGRESS v1.0.2; **NO FROZEN**.  
**Condición de cierre:** pendiente. Requiere inventario completo de entrypoints y consumidores relevantes (incluidos imports/configuración dinámica y herramientas), reconciliación de obligaciones con su versión vigente, referencias de evidencia y límites por superficie, clasificación de hipótesis, contradicciones resueltas o declaradas, y criterios verificables de transferencia a otros HITOs. Ya existe contraste estático inicial del Atlas, selección de roots y consumidores versionados focales, **no** un censo global exhaustivo. El índice textual no permitió descartar consumidores por ausencia de resultados; quedan rutas dinámicas/externas, trazabilidad de dependencias relevantes y segregación precisa para los HITOs siguientes.  
**Verificación de cadena de gobernanza:** metodología revisada; aún no existe ADR/NADR/Execution Plan de esta iniciativa.  
**Decision Candidates generados:** ninguno aprobado; posibles preguntas permanecen en `TO BE VERIFIED`.  
**Siguiente paso:** continuar auditoría read-only y ampliar/emitir HITOs necesarios, con base fija y cierre formal antes de decisiones de diseño.

> No usar esta versión `IN_PROGRESS` como prueba de que la auditoría de Fase 0 esté completa.
