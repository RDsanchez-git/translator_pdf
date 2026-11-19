# HITO_0.1_RUTA_OPERATIVA_Y_PERIMETRO.md

**Estado:** IN_PROGRESS v1.0.8  
**Fecha de emisión:** 2026-11-18  
**Fecha de congelamiento:** N/A  
**Fase:** Fase 0 — Auditoría forense de la iniciativa `pdf-pdf-product-readiness` (la designación de fase numerada del roadmap aún requiere resolución de gobernanza).  
**Tipo de artefacto:** Flow Audit  
**Naturaleza:** Read-only. No prescribe código, diseño, cambios de arquitectura ni implementación.  
**Baseline de inspección:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`. Las observaciones posteriores deben citar su SHA de fuente.  
**Evidencia Forense Vinculante:** `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN; Atlas, handoff y evidencia C0–C4 D-1/D-2; ADR/NADR F18 vigentes y `PHASE_18.2_EXECUTION_PLAN.md` sin alterar sus estados; TST-STAB; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; código en `main@1d21cfe`.  
**Mandato:** Determinar la ruta ejecutable real, sus fronteras y dependencias, la cobertura necesaria de auditoría y las incertidumbres que impiden planificar por evidencia una traducción PDF→PDF STEM utilizable.  
**Síntesis:** Inventario estático de roots, contratos y componentes en curso; el grafo v2 cubre los 579 módulos Python del SHA base y permite diferenciar enlaces estáticos, inferidos y no resueltos. Persisten fronteras inyectadas y consumidores externos no verificables; **el HITO no está cerrado**.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-18 | Apertura del HITO, mandato, baseline, método, evidencias iniciales y condiciones de cierre; sin declarar una auditoría completada. |
| 1.0.1-IN_PROGRESS | 2026-11-18 | Primera reconciliación estática: Atlas histórico versus main y grafo de productores/consumidores de la ruta D-1/D-2. La auditoría sigue abierta. |
| 1.0.2-IN_PROGRESS | 2026-11-18 | Segundo barrido estático: censo de rutas ejecutables y consumidoras fuera del Atlas, factories, benchmark/CV, stubs y alcance real de testigos T06/W08; conserva límites no verificados. |
| 1.0.3-IN_PROGRESS | 2026-11-18 | Mapa de contratos entre fronteras y dependencia por capacidad, matriz de responsabilidad de los HITOs 0.2–0.9 y verificación focal de mecanismos B02/W08/G3/F18/G5/CI. Sin cierre de auditoría ni gap nuevo. |
| 1.0.4-IN_PROGRESS | 2026-11-18 | Control de cobertura y roots adicionales sobre SHA fijo; reconciliación literal con metodología HITOs v1.2.0; severidad conforme consecuencias, desarrollo P1 y GAP local fundamentado. Cierre aún no autorizado. |
| 1.0.5-IN_PROGRESS | 2026-11-18 | Primera pasada integral sobre grafo aportado por el owner (20.615 líneas), contraste focal contra rutas y llamadas asíncronas de main, límites de un grafo de llamadas sin imports ni destinos enlazados. Ninguna brecha nueva de producto. |
| 1.0.6-IN_PROGRESS | 2026-11-19 | Contrastado grafo v2 enlazado con el SHA base y los 579 Python versionados, revisión de 6.399 edges y 7.384 unresolved por categorías, fronteras de puertos inyectados OCR/G3/G5 verificadas focalmente. Sin nueva brecha ni cierre prematuro. |
| 1.0.7-IN_PROGRESS | 2026-11-19 | Triaje de unresolved/dynamic por riesgo y lectura del binding DI en OCR/G3/G5, reconciler y legacy; pre-checklist de cierre según §8 HITOs. Sin ejecución ni nuevos GAP. |
| 1.0.8-IN_PROGRESS | 2026-11-19 | Revisión contra §§3, 8, 9 y 11.1 de metodología HITOs; fuentes HITO 17-BIS/F18 heredadas, estados de hipótesis tipados, diferidos justificados y checklist reubicado en §21. Detectados gates de gobernanza del nombre de etapa e integración Git, sin congelar. |

## 1. RESUMEN EJECUTIVO

El objetivo es observar la composición PDF→PDF desde admisión hasta PDF publicado y los componentes que realmente pueden influir en ese recorrido, incluida la herencia legacy y las obligaciones FROZEN aplicables.

**Hallazgo central de apertura:**

> La convergencia operativa sobre fake está documentada, pero el contrato real de inferencia, los controles de gasto, la identidad de la generación y la fidelidad STEM todavía requieren reconciliación causal contra el código y la evidencia de ejecución. No corresponde fijar tareas ni seleccionar nuevas abstracciones antes de la Fase 0.

**Observaciones iniciales reconciliadas:** el constructor G3 usa modelo/ventana primarios literales; el builder acepta `SWITCH_MODEL` conservando `model_name`; el adaptador envía ese modelo; y el foreground devuelve el PDF de una generación `COMPLETED`. También se comprobó estáticamente el grafo de composición y consumidores críticos del Atlas sobre el corte de `main`. **La inspección estática NO acredita ejecución física, traducción real ni ausencia de otros consumidores.**

**Defecto estructural confirmado en la composición inspeccionada:** una decisión `SWITCH_MODEL` puede formar un envelope `BuildSuccess` sin cambiar el modelo efectivamente enviado a Groq (**E-0.1-002**); se registra como discrepancia contractual local sin prescribir solución (**GAP-0.1-01**). La hipótesis sobre generación/idioma permanece por verificar, no se eleva a defecto confirmado.

**Veredicto forense:** mapa estático de raíces y dependencias utilizables, con límites físicos y dinámicos expresos. `IN_PROGRESS`; no acredita auditoría integral de capacidades, ADR/NADR, plan ni implementación.

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

### Control de cobertura del HITO 0.1 — SHA `1d21cfe`

Se enumeró el árbol Git completo (**1.094 blobs versionados; `truncated=false`**) y se contrastaron los **roots seleccionados por configuración versionada** con los símbolos invocados. El número del árbol no es un censo de métodos ni una declaración de lectura profunda del 100 % de archivos. Se delimita el HITO 0.1 a **selección de roots, conexiones entre fronteras y consumidores relevantes conocidos**; la semántica de los módulos especializados pertenece a los HITOs 0.2–0.8.

| Superficie delimitada de 0.1 | Código/configuración leída directamente | Cobertura y límite |
|---|---|---|
| Producto seleccionado | `pyproject.toml`, `apps/cli/{main,pdf_inbox,pdf_product}.py`, `apps/ocr_router/__main__.py`, `runtime/engine.py`, `apps/compiler/__main__.py` | **AUDITADO ESTÁTICO**; no hubo E2E nuevo |
| Composición/dependencias | `apps/bootstrap/{pipeline_factory,provider_factory,provider_stack_factory,extraction_config}.py`, factories y contratos fronterizos citados en §5–6 | **AUDITADO FOCAL**; implementaciones internas corresponden a otros HITOs |
| Estado y auxiliares | `infra/db/{connection,control_repo,fsm_repository,context_snapshot_repo,staged_publication,assembly_recovery}.py`, `apps/daemons/reconciler.py`, `runtime/{publication_pipeline,recovery,resumer,sweeper,settings}.py` | **AUDITADO FOCAL**; revisión normativa y fallos F18 en 0.5 |
| Lanzadores/entornos | `Dockerfile`, `Dockerfile.fake`, `docker-compose.yml`, `docker-compose.runtime.yml`, `docker-compose.convergence-lab.yml`, `docker-compose.golden.yml`, `apps/lab/{offline_pdf_lab,convergence_compose_preflight,convergence_db_bootstrap,g3_fake}.py` | **AUDITADO ESTÁTICO**; `docker compose config`, Docker/host/egress no ejecutados |
| Alternativas e instrumentales | `apps/cli/legacy_translate_async.py`, `apps/llm_workers/__main__.py`, `apps/benchmark/__main__.py`, `apps/benchmark/runners/{groq,gemini}_runner.py`, `apps/compiler/sandbox/server.py`, `core/routing/router.py`, `bootstrap/topology.py` | **AUDITADO FOCAL** como roots o consumidores, no seleccionados como segunda ruta productiva |
| Testigos y CV | `tests/unit/test_c4_t06_supported_roots.py`, `tests/integration/{test_verification_pipeline_connection,test_w08_cli_foreground_single_generation_offline}.py`, `.github/workflows/{ci,continuous-verification}.yml`, `tools/evaluation/run_regression.py` | **AUDITADO ESTÁTICO**; tests no reejecutados, alcance de oráculos a 0.8 |
| Contratos profundos | `core/ast/`, `core/chunking/`, `core/normalization/`, `core/compiler/`, `infra/extraction/`, `core/benchmark/`, `tools/evaluation/` completos | **REFERENCIADOS, NO RE-AUDITADOS** exhaustivamente aquí; destinos 0.2/0.3/0.4/0.6/0.8 |
| Externo/no observable en Git | Procesos iniciados por terceros, Compose efectivo en host, estado físico SQLite/volúmenes, secretos/proveedor comercial, corpus sellado | **NO VERIFICABLE** en este HITO; causas: no hay acceso/permiso/atestación física. Destinos 0.5, 0.7 y 0.8, según propiedad |

**Hallazgos que evitan falsas ausencias:** `ExtractionProviderId` enumera `PYMUPDF/DOCLING/TESSERACT`; existen `DoclingProvider` y `TesseractProvider`, pero la factory conectada solo acepta `PYMUPDF`. `StrategyRouter` y `TranslationStrategyRouter` existen con responsabilidades distintas; no constituyen, por su nombre, routing multimodelo activo de G3. `apps/compiler/sandbox/server.py` expone una ruta HTTP `/compile` separada del G5 seleccionado; no inventar un servicio productivo a partir del archivo. `docker-compose.golden.yml` declara variables `GEMINI_*`, **sin prueba de Compose efectivo ni compatibilidad con el G3 Groq actual**. `runtime/settings.py` declara flags F18 con defaults conservadores; la activación real requiere otro HITO.

**Límite de completitud:** cobertura de rutas/configuración *versionadas* que se identificaron y leyeron, no demostración de ausencia universal de consumidores. La búsqueda indexada de símbolos devolvió falsos vacíos para símbolos presentes; se descartó como prueba negativa. Un scan reproducible de todos los imports/callers de cada archivo Python, el análisis de importación dinámica y los lanzadores externos no están acreditados; una afirmación universal sobre ellos sería falsa. **Esta limitación se conserva explícita hasta revisión de cierre**, y su riesgo se difiere por superficie sin duplicar inspecciones profundas.

### Insumo adicional: grafo de funciones recibido del owner (primera pasada, read-only)

Se inspeccionó el archivo aportado `PIPELINE_GRAPH.rar` (SHA-256 `dd37803735a01ab119d6cb15aa6d5bfd75db76df33b708358d68fb0ca39e971b`), que contiene **un único** `PIPELINE_GRAPH.md` (SHA-256 `f935b90b97246f3ca61f89a80d402be16faa0dd7bfe7525dad1cfd2a9e393c53`). Se procesaron todas sus **20.615 líneas**, que representan **544 subgrafos de archivo, 983 clases, 1.011 funciones y 13.061 aristas**. El archivo no indica SHA de repositorio/fecha de generación verificables. **Es un índice contextual externo, no fuente vinculante versionada ni sustituto del Atlas.** Ninguna conclusión de comportamiento se toma solo de él.

**Límite estructural del grafo:** 11.185 aristas apuntan a nodos genéricos `call_*` (nombre de llamada sin resolver destino), y 1.876 conectan clase→método dentro de archivo; **ninguna arista identifica directamente un destino resuelto en otro archivo del repositorio**. No representa imports ni resolución de puertos/protocolos, fábricas inyectadas, registros por configuración, procesos Compose, runtime HTTP/SQLite ni consumidores externos. Las clases/métodos asíncronos pueden quedar omitidos.

**Contraste focal con el SHA fijo de main:**

| Consulta de completitud | En grafo recibido | En código versionado `main@1d21cfe` | Interpretación |
|---|---|---|---|
| G3 productivo `runtime/engine.py` | **AUSENTE** como subgrafo | **PRESENTE**; `run_pipeline` y `_create_chunk_processor` ejecutan G3 seleccionado | El grafo NO cubre todos los archivos críticos; `call_run_pipeline` es referencia sin binding |
| Provider factory asíncrona | Archivo presente, **sin `build_provider_stack` ni aristas internas** | `async def build_provider_stack` compone `GroqProvider`/Gemini según selector | El generador pierde funciones asíncronas; no inferir factory desconectada |
| Adaptador Groq | Figura constructor, **no `async def translate`** | `GroqProvider.translate` envía `envelope.model_name` | La ausencia de método en grafo no acredita ausencia de efecto |
| CLI `getattr(args, 'run', False)` | Nodo genérico `call_getattr` | Acceso a atributo `argparse`; imports locales explícitos para la rama `--run` | No constituye carga dinámica de servicio |
| G5 `getattr(node.metadata, ...)` | Nodos genéricos `call_getattr` | Accesores de geometría y activos en adaptadores | No constituye plugin ni raíz alternativa |
| Ficheros sueltos `extraer_benchmark.py`, `generate_workspace.py` | Presentes | No figuran entre blobs del árbol Git fijo | Fecha/procedencia del grafo no coincide con árbol exacto |

**Resultado:** el grafo es valioso para inspeccionar el **inventario positivo de símbolos** y dirigir el análisis selectivo, pero es **inapropiado para una prueba negativa de ausencia de consumidores dinámicos**. Antes de certificar completitud de esos consumidores se necesita un censo de imports/callers de código versionado, configuración y servicios externos documentados; la ausencia física de un servicio ajeno al repositorio es `NO VERIFICABLE` sin evidencia del host. No fabricar un segundo Atlas, ni persistir el archivo externo sin justificación y autorización.

### Insumo adicional: grafo enlazado v2 del owner, inspeccionado y contrastado

El owner entregó `translator_pdf_graph.rar` (SHA-256 `65b119239afd9a2e99b3a0a8a36d28582acf655e65e535656470a7c73e5ab72b`), con los **seis** artefactos `graph_inventory.json`, `graph_edges.csv`, `graph_unresolved.csv`, `graph_dynamic.csv`, `graph_resolved.mmd`, `graph_summary.md`. Se abrieron y analizaron; el inventario declara `commit_sha=1d21cfe958cc1de8a33824fed748cd6fe9260f42` y **una modificación del árbol de trabajo: borrado de PDF versionado**, no código Python. La comparación con el árbol Git recursivo `truncated=false` confirma **579/579 archivos `.py` versionados contabilizados**; `0` fallos de parseo. La procedencia es más fuerte que la del grafo v1, pero el artefacto todavía es **contextual, no una ejecución ni un resultado normativo**.

| Indicador del v2 | Resultado | Interpretación admisible |
|---|---:|---|
| Módulos analizados / archivos `.py` de main | 579 / 579 | Censo de módulos versionados completo; no garantiza todas las ramas operativas |
| Definiciones indexadas | 4.743 | Incluye funciones y métodos asíncronos ausentes en v1 |
| Aristas enlazadas | 6.399 | 5.875 `static`, 524 `inferred`; **3.625** entre módulos |
| Llamadas no resueltas | 7.384 | 5.304 atributos externos/dinámicos, 1.188 externos/no resueltos, 892 `self` sin tipo inferible; **no son 7.384 problemas** |
| Sitios dinámicos o de efecto | 1.064 | 954 expresiones compuestas y 110 `dispatch_o_efecto_dinamico`; **no son 1.064 plugins** |
| Núcleo focal (`apps/cli`, `apps/ocr_router`, `runtime`, `apps/llm_workers`, `apps/bootstrap`, `apps/compiler`, `infra/db`) | 499 edges, 995 unresolved, 107 sitios señalados | De los 107, 90 son expresiones compuestas y 17 `getattr`/`subprocess.run`; requieren lectura semántica selectiva |

**Enlaces positivos verificados sobre código y grafo del mismo SHA:**

| Frontera | Enlace/resolución v2 | Confirmación en código |
|---|---|---|
| CLI → G3 | `apps.cli.pdf_product._run_g3` → `runtime.engine.run_pipeline`, `import_explicito/static`, línea 113 | Import local + llamada directa |
| G3 → composition root | `runtime.engine._create_chunk_processor` → `apps.bootstrap.provider_stack_factory.build_provider_stack`, `import_explicito/static`, línea 87 | Factory asíncrona compone Groq/Gemini condicional; `cache_db_path=None` en G3 |
| Foreground → OCR | `_ingest` → `OCRRouterDaemon._process_document`, `metodo_instancia_inferido/inferred`, línea 108 | Construcción del daemon explícita en `apps/cli/pdf_product.py` |
| Foreground → G5 | `_run_g5` → `AssemblerWorkerDaemon._process_assembly_task`, `metodo_instancia_inferido/inferred`, línea 162 | Construcción de runner, resolver y compilation service explícita |
| OCR → plan | `OCRRouterDaemon._process_document` → `prepare_contextual_plan`, `import_explicito/static`, línea 121 | Import y uso en OCR |

**Fronteras inyectadas que el grafo v2 marca correctamente `unresolved`, y su tratamiento:**

- `apps/ocr_router/__main__.py`: `self.parser.parse`, `self.document_profiler.profile`, `self.ast_registry.register_ast` se enlazan **por constructor**, verificado focalmente en `apps/bootstrap/pipeline_factory.py`, `apps/cli/pdf_product.py` y OCR; su semántica específica corresponde a 0.2/0.3.
- `runtime/chunk_staging.py::stage_claimed_unit`: `processor.execute_chunk` y `repo.stage_chunk_result` se verifican por firma/protocolo y composición de G3; **no** se equipara una invocación al éxito del proveedor. Dueños 0.4/0.5.
- `apps/llm_workers/sync_bridge.py::SyncProviderBridge.execute_chunk`: `self._builder.build` y `self._provider.translate` se configuran en el constructor; la segunda atraviesa el stack CB/RateLimit/Groq, y el POST real queda **NO VERIFICABLE** aquí. Dueño 0.4.
- `apps/compiler/__main__.py::_process_assembly_task`: `self.context_resolver.resolve`, `self.compilation_service.compile_document_with_assets` y `self.runner.compile` son puertos inyectados por la composición G5; `HostTectonicRunner.compile` ejecuta `subprocess.run` con Tectonic, sin ensayo físico nuevo. Dueños 0.6/0.7.
- `Graph_dynamic.csv` registra `getattr` de datos geométricos/CLI y `subprocess.run`; no se deben contar como loaders de clases. No se ha acreditado que los consumidores fuera de Git estén ausentes.

**Delimitación de salida:** se completó el **censo estático de archivos Python y de enlaces que el analizador es capaz de resolver**. Falta comprobar exhaustividad semántica de las llamadas `unresolved` de alto impacto, los sitios configurados condicionalmente, Compose efectivo y los procesos del host; estos últimos no se pueden cerrar solo con otro grafo. El inventario v2 permite **priorizar** esa inspección sin convertir cada llamada al stdlib/SQLite en un nuevo HITO o gap. El grafo `.mmd` recorta la vista a un máximo de 350 aristas; las tablas CSV/JSON, no el dibujo, son la base de cobertura.

### Triaje focal de consumidores indirectos y sitios dinámicos (HITO 0.1, mismo SHA)

Se inspeccionaron los CSV y el inventario v2 por **raíz y tipo de expresión**, para no tratar `7.384` unresolved como `7.384` consumidores o defects. En el subconjunto `apps/cli/`, `apps/ocr_router/`, `runtime/`, `apps/llm_workers/`, `apps/bootstrap/`, `apps/compiler/`, `apps/daemons/`, `infra/db/`, `infra/adapters/` e `infra/extraction/` hay **1.239 llamadas unresolved** (conteo de filas, no destinos únicos) y **133 sitios dinámicos/de efecto**: 99 expresiones compuestas y 34 `getattr`/`subprocess.run`. Se contrastaron selectivamente los casos que pueden cambiar composición, inferencia, autoridad o publicación.

| Frontera de interés | Unresolved o disparador del v2 | Binding comprobado en código | Veredicto / dueño de análisis profundo |
|---|---|---|---|
| OCR y generación de AST | `self.parser.parse`, `self.document_profiler.profile`, `self.profile_store.save`, `self.ast_registry.register_ast` | `OCRRouterDaemon.__init__` recibe `ParserProtocol`, profiler, store y registry. Root OCR y foreground inyectan `build_extraction_pipeline()`/profiler y repositorios concretos | **Inyección estática localizada**, no plugin desconocido; 0.2/0.3 para semántica |
| G3 y efectos | `processor.execute_chunk`, `repo.stage_chunk_result`, `self._builder.build`, `self._provider.translate` | `run_pipeline` crea `SyncProviderBridge` solo cuando hay unidades traducibles; `stage_claimed_unit` usa lease y `PRESERVE` evita POST; bridge recibe stack construido por `build_provider_stack` | **Binding estático localizado**, ejecución HTTP **NO VERIFICABLE**; 0.4/0.5 |
| Stack de proveedor | `underlying.translate` por wrappers/protocolo; selección condicional `provider_type` | Factory elige `GroqProvider` por default o `GeminiProvider` por rama explícita; orden CB → Cache opcional → RateLimit → proveedor; G3 pasa `cache_db_path=None` | No hay loader `importlib` detectado en la factory; fallback/multimodelo **no acreditado**, 0.4 |
| G5 | `self.context_resolver.resolve`, `self.compilation_service.compile_document_with_assets`, `self.runner.compile` | Roots G5 foreground/daemon inyectan `CQRSAssemblyContextResolver`, `CompilationService` y `HostTectonicRunner`; último ejecuta `subprocess.run(["tectonic", "--untrusted", "doc.tex"], ...)` | **Binding localizado**; compilación física de este corte **NO VERIFICADA**; 0.6/0.7 |
| Reconciler, FSM y leases | `self.system.acquire_leadership`, `self.recon_cmd_handler.handle`, `self.task_repo.*`, `self.cmd_handler.handle` | `apps/daemons/reconciler.py` construye repositorios/handlers explícitamente; G5 construye `AssemblyLeaseRepository` sobre queue y conexión de heartbeat separada | No es un segundo motor; garantías transaccionales y F18 siguen a 0.5 |
| Dispatch histórico | `self.parser.parse`, `self.dispatcher.dispatch` en `core/pipeline/orchestrator.py`, `getattr` en `apps/llm_workers/dispatcher.py` | `TranslationPipeline` recibe puertos en constructor y `build_pipeline` conserva consumidor legacy; el `getattr` revisado obtiene datos de unidad/healing | **Legacy con consumidores**, no root productivo; preservación de compatibilidad a 0.1/0.7 y semántica a 0.4 |
| `__import__`, `setattr` y subprocess | El conjunto completo del CSV señala 3 `__import__`, 7 `setattr` y 21 `subprocess.run` | Los 3 `__import__` están en `audit/build/tests/test_i0_1.py`; los 7 `setattr` en tests; en `apps/compiler/` hay dos subprocess Tectonic, solo uno en el G5 seleccionado | No constituyen 31 plugins productivos. Otros subprocess son laboratorio, CI/evaluación/test; 0.7/0.8 según root |
| Selección desde infraestructura | `Dockerfile`, cuatro Compose, `pyproject.toml` y workflows indexados | CLI `translator-pdf` y Compose base seleccionan OCR/`runtime.engine`/G5; override runtime modifica servicios/volúmenes/dependencias con `!override`/`!reset`; `docker-compose.golden.yml` usa vars Gemini sin probar G3 real | **Textual/versionado**; el Compose efectivo y procesos externos son **NO VERIFICABLES** con análisis estático, 0.7 |

**Lectura de certeza:**

- `CONFIRMADO POR COMPOSICIÓN ESTÁTICA`: destino de las interfaces identificado en constructores y roots seleccionados para el SHA, **sin prueba de que se esté ejecutando en host**.
- `REFERENCIADO`: implementación de biblioteca/instrumento con consumidores versionados, sin seleccionar como root productivo.
- `NO VERIFICABLE`: consumidor fuera de Git, selección dinámica por entorno externo, credenciales, red, efectos HTTP, subprocess/Compose real y estado físico. Se requieren atestaciones/ensayos autorizados en HITOs 0.4/0.5/0.7/0.8, no inventar cobertura.
- `FUERA DE SCOPE DE 0.1`: validez STEM de AST/TeX y semántica detallada de cada prueba. Se transfiere a 0.2/0.3/0.6/0.8 con los módulos de origen ya identificados.

**Resultado del triaje:** el riesgo residual de 0.1 no es «miles de consumidores dinámicos sin identificar», sino **(a)** límites de interfaces con tipos seleccionados en runtime, **(b)** configuración/roots externos al repositorio, y **(c)** comportamiento físico que no se infiere de un grafo. Ninguno de esos límites debe generar un servicio, script permanente o GAP nuevo solo por ser `unresolved`.




**Fuera de alcance en Fase 0:** cambio de código, migración de datos, purga, traducción comercial, campaña de benchmark científico, carga de PDF de terceros y nuevos despliegues.

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Rol |
|---|---|---|
| Normativa | `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` | Secuencia, plantilla, criterio de evidencia y cierres |
| Normativa | `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, ADR/NADR aplicables | Propósito del producto e invariantes |
| Forense/documentación vigente | `docs/architecture/adr/pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` (corte `6818e86`, §§1–6 y 10) | Mapa histórico de entrypoints, datos, consumidores y pruebas de impacto; insumo a contrastar, no certificación de `main` |
| Histórico y diff | [Comparación 6818e86…1d21cfe](https://github.com/RDsanchez-git/translator_pdf/compare/6818e86e21b14e77a606f0c863e9c199b4627601...1d21cfe958cc1de8a33824fed748cd6fe9260f42) | Cambio de superficies entre Atlas y baseline de la auditoría |
| Contextual externo, no vinculante | Archivo del owner `PIPELINE_GRAPH.rar` / `PIPELINE_GRAPH.md`, SHA-256 documentados en §3 | Índice de funciones y llamadas para descubrimiento; falta procedencia Git y resolución entre módulos |
| Contextual externo, con baseline atribuible | Archivo del owner `translator_pdf_graph.rar`, SHA-256 y seis artefactos en §3 | Grafo estático de los 579 `.py` sobre el SHA declarado; código y aristas corroboradas selectivamente; no prueba ejecución |
| Forense/documentación vigente | `docs/architecture/adr/pipeline-stabilization/handoff/README.md` y `EVIDENCIA_Y_CIERRE.md` | Decisión D-1/D-2, límites fake y actas históricas |
| Normativa aplicable | `docs/architecture/adr/phase-18/ADR/ADR_F18_MASTER.md`, `docs/architecture/adr/phase-18/NADR/NADR-F18-03.md` y NADR F18 restantes | Autoridad y efectos inciertos; revisión completa de cumplimiento en HITO 0.5 |
| Plan histórico | `docs/architecture/adr/phase-18/plans/PHASE_18.2_EXECUTION_PLAN.md` | Estado histórico de gates/tareas; no crear plan competidor |
| Alcance del proyecto | `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md` | Prohibición de fallos silenciosos, identidad y calidad; reglas no inventadas |
| Forense/documentación histórica | `docs/architecture/adr/tests_stabilization/`; `docs/architecture/adr/phase-18/` | Alcances de tests, mecanismos, decisiones y obligaciones existentes |
| HITO histórico (evidencia heredada) | `docs/architecture/adr/phase-17-bis/00-foundation/HITO_0.4.5_P1_PRODUCTION_COMPOSITION_AUDIT.md` | Composición R1/histórica; no extrapolar su root al corte D-1/D-2 |
| HITO previo FROZEN | `docs/architecture/adr/phase-17-bis/00-foundation/HITO_6.4_DEPENDENCY_GRAPH_AND_READINESS_ASSESSMENT.md` | Dependencias CV/CI históricas; no re-auditar su corpus ni su baseline aquí |
| HITO previo FROZEN | `docs/architecture/adr/phase-18/00-foundation/HITO_0.11_Current_State_Contract_Map.md` | Autoridades y contratos heredados, anterior a las decisiones de convergencia |
| HITO previo FROZEN | `docs/architecture/adr/phase-18/00-foundation/HITO_18.2.0_DURABLE_EXECUTION_SURFACE_AUDIT.md` | Riesgos e invariantes F18; cotejo contractual profundo reservado a 0.5 |
| Código observado | `runtime/engine.py`, `core/validation/budget.py`, `apps/llm_workers/prompt_builder.py`, `apps/llm_workers/adapters.py`, `apps/cli/pdf_product.py` | Primeros testigos concretos; falta verificar consumidores completos |
| Fuente de restricción | [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34) | Evaluación científica/corpus diferidos y custodia |
| Evidencia pendiente | Host Windows, APIs y proveedores reales, archivos de corpus privados | No verificada por la auditoría de apertura |

**Reutilización y no-regresión (§9.2–9.4 de la metodología):** se reabrieron los cuatro HITOs históricos anteriores. `HITO_0.4.5_P1` describe la composición previa de `TranslationPipeline`/R1; **el handoff D-1/D-2 posterior** selecciona OCR → `runtime/engine.py` → G5 en los launchers soportados. Su evidencia histórica no se elimina ni se convierte en reporte del estado actual. `HITO_6.4` constató límites de CV/CI en su corte 2026-09; los workflows de `main@1d21cfe` se examinaron focalmente, pero su diferencia de fecha/composición **requiere reconciliación por SHA en HITO 0.8** si afecta una garantía, sin declarar hoy contradicción irreconciliable. `HITO_0.11` y `HITO_18.2.0` ofrecen el inventario previo de autoridad/durabilidad; el status posterior del plan F18.2 y el wiring actual deben confrontarse en HITO 0.5. **No se repiten** las matrices históricas ni se asume que sus defectos continuaron o fueron corregidos sin evidencia.

**Hallazgos diferidos heredados:** las limitaciones de CV/CI y los DC/DF de F18 ya tienen sus propias fuentes y registros. Se los referencia sin crear ID de finding nuevo; la eventual reconciliación y trazabilidad de resolución pertenece a las autoridades documentales de las fases originarias o a los HITOs 0.5/0.8 de esta auditoría, según propiedad.

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

### 6.1 Contratos entre fronteras — fuente única de este inventario

La matriz registra **productor → consumidor y valor de identidad/autoridad**. Las columnas «HITO» asignan investigación, **no** decisiones de implementación. El estado `CONFIRMADO ESTÁTICO` no significa probado dinámicamente.

| Frontera contractual | Productor → consumidor constatable | Datos / invariantes que atraviesan | HITO primario | Estado / límite |
|---|---|---|---|---|
| Admisión → OCR | `apps/cli/pdf_inbox.py::submit_pdf_to_inbox` → `OCRRouterDaemon._process_document` | `document_id` = SHA-256 bytes, mismo inbox/raíz; duplicación y estados anteriores | 0.1 raíces; 0.2 contenido; 0.7 workspace | CONFIRMADO ESTÁTICO; montaje real/OS no verificado |
| PDF físico → Layout/AST | `ExtractionProviderFactory` → `PyMuPDFProvider` → `PdfParserAdapter` → `FlatASTBuilder` | Texto, glyphs, página, imagen, bbox, clasificación y `B02_UNREPRESENTED_VECTOR_DRAWING` | **0.2** | EXTRACCIÓN CONECTADA; amplitud STEM por auditar |
| AST → Contexto/ChunkPlan | `prepare_contextual_plan` → `HierarchicalContextEnricher`, `TokenBudgetChunker`, `ChunkPlan.build` | `ast_hash` invariante, `chunk_id`/miembros, orden/segmentos, `manifest_sha256` | **0.3** | CONTRATO EXISTENTE; exhaustividad y cambio semántico por auditar |
| Plan/contexto → G3 | `DurableContextPlanRepository.enqueue_verified/load_verified` → `runtime.engine.run_pipeline` | `document_id`, `ast_hash`, `manifest_sha256`, `snapshot_sha256`; fallar antes de proveedor ante drift | **0.3** (datos), **0.5** (durabilidad) | W08 CONECTADO PARA SNAPSHOTS; no equivale a reuse/caché |
| G3 → proveedor | `SyncProviderBridge.execute_chunk` → `PromptBuilder` → `build_provider_stack` → `GroqProvider` | Prompt físico, idioma, modelo/ventana, reserva, cuota, JSON y máscaras de matemática | **0.4** | CONEXIÓN ESTÁTICA; fallback y egress reales sin acreditación |
| Claim → efecto → staging/publicación | `ControlPlaneRepository.pick_task` → `stage_claimed_unit` → `advance_staged_document` → `materialized` y FSM | `task_id`, `execution_id`, lease, `state_version`, receipt, `G3_EXTERNAL_UNKNOWN` | **0.5** (autoridad), 0.4 (efecto/transport) | RECOVERY PARCIAL OBSERVADO; prohibición de retry incierto |
| Proyecciones/AST → G5 | `CQRSAssemblyContextResolver` → `DocumentAssembler` → `CompilationService` y mapper | `node_id`, `sequence_id`, `projection_version`, activos, payload fallback y perfil | **0.6** | RUTA CONECTADA; degradación ≠ fidelidad |
| TeX/assets → archivo publicado | `HostTectonicRunner` → PDF staged → `AssemblyLeaseRepository.publish` | Caché/TeX/assets, lease, `os.replace`, FS/SQLite no atómicos entre sí | **0.6** (render), **0.5** (fencing), 0.7 (host) | PUBLICACIÓN ESTÁTICA; compilación física nueva no ejecutada |
| Artefactos → verificación | `build_extraction_pipeline` → `tools.evaluation.run_regression`; tests B02/G3/G5/W08 y workflows | Oráculo, fixture, SHA, evidencia fake/real, custodia de corpus | **0.8** | EVIDENCIA HEREDADA ACOTADA; ciencia PDF→PDF no acreditada |

### 6.2 Fronteras especializadas de los HITOs restantes

Esta es una **partición del alcance forense**, no el Execution Plan de implementación ni una declaración de HITOs ya aprobados. Un mismo archivo puede tener dos responsabilidades: se audita cada **propiedad contractual** una sola vez, y los demás HITOs remiten a ella.

| HITO propuesto | Pregunta delimitadora, módulos y evidencias a investigar | Excluye / remite a |
|---|---|---|
| **0.2 — Ingesta y extracción PDF** | Cobertura del origen físico: `infra/extraction/providers/pymupdf_provider.py`, `pymupdf_integrity.py`, `pymupdf_math_visual.py`, `pymupdf_image_assets.py`; `infra/adapters/pdf_parser.py`; clasificadores, perfiles y tests `test_pymupdf_extraction_integrity`, B02.2–B02.5. Constatar lo representado/rechazado, gráficos, fórmulas, columnas y casos sintéticos | No decidir identidad del `ChunkPlan` (0.3) ni calidad del PDF ensamblado (0.6) |
| **0.3 — AST, normalización, contexto y chunking** | `core/ast/`, `core/layout/`, `core/normalization/`, `core/segmenter/`, `core/chunking/`, `core/context/`; `compute_ast_hash`, `validate_chunk_coverage`, `ContextSnapshotV1`, identidad W08 y uso efectivo; testigos W08/G3-B2 | El proveedor físico y tokens de salida pertenecen a 0.4; estado transaccional/leases a 0.5. Identidad `inference-reuse` ≠ generación autorizada |
| **0.4 — Inferencia, prompting y proveedor** | `runtime/engine.py::_create_chunk_processor`, `apps/llm_workers/{sync_bridge,prompt_builder,adapters,rate_limiter,cache_provider,routing}.py`, `core/prompting/`, `core/validation/budget.py`, `core/finops/`; modelo, target language, medición vs payload real, `SWITCH_MODEL`, token/respuesta/cuota/gasto, máscaras, error/egress | No diseñar router adicional ni transferir a 0.4 la semántica de recuperación F18 (0.5) |
| **0.5 — Estado, persistencia, autoridad y recuperación** | `infra/db/`, `core/execution/`, `runtime/{publication_pipeline,chunk_staging,recovery,resumer,sweeper}.py`, `apps/daemons/reconciler.py`; SQLite/ATTACH, CAS/epoch, leases, receipts, W06, `UNKNOWN`; confrontar con ADR/NADR F18 y `PHASE_18.2_EXECUTION_PLAN` **ya existente** | No duplicar el plan ni la autoridad de F18. No atribuir idempotencia HTTP remota por idempotencia de receipt local |
| **0.6 — Ensamblado y fidelidad física del PDF** | `apps/compiler/`, `core/compiler/`, `infra/db/assembly_recovery.py` solo para la frontera física; assets, `TextRenderStrategy`, matemática explícita, `AdaptiveFloatStrategy`, política `DEGRADED`, multicolumna y `HostTectonicRunner` | No volver a auditar totalidad de CAS/leases (0.5) ni declarar que el PDF conserva un elemento que B02 no extrajo (0.2) |
| **0.7 — Operación reproducible y entornos** | `apps/cli/`, `pyproject.toml`, `Dockerfile`, tres Compose operativos/instrumentales, `apps/lab/`, `infra/db/bootstrap.py`, host Windows, secretos, cwd/volúmenes, rutas, red, caches y límites de ejecución | No modificar `--network none` del laboratorio certificado ni afirmar egress autorizada sin control físico |
| **0.8 — Verificación técnica y científica** | `tests/`, `.github/workflows/`, `core/benchmark/`, `tools/evaluation/`, TST-STAB, CV, fixtures y corpus; garantías causales de testigos, cobertura de modos STEM, falsadores, skips/NOT_RUN, custodia y issue #34 | No rehacer 1.476 pruebas históricas; no modificar GT/sellos ni convertir fake/CI técnico en PASS científico |
| **0.9 — Consolidación y reconciliación** | Matriz de brechas **dentro de este HITO**, con fuentes `E-0.x` de los precedentes, contradicciones resueltas, incertidumbres irreductibles y Decision Candidates | No introducir nuevas decisiones, reglas NADR, tareas o matriz temporal que compita con Execution Plan |

**Orden lógico de dependencias, no waves de implementación:** 0.1 delimita las fronteras → 0.2 identifica el observable fuente → 0.3 valida representación/plan → 0.4 investiga inferencia, 0.5 autoridad y 0.6 reconstrucción (las tres con contratos compartidos pero preguntas distintas) → 0.7 demuestra condiciones de entorno → 0.8 delimita alcance de pruebas científicas → 0.9 reconcilia resultados. No se prohíbe realizar investigación read-only independiente antes de terminar otra, pero **no se emite veredicto sobre una frontera no inspeccionada**.

### 6.3 Capacidades reutilizables y límites — evitar rediseños prematuros

- **Extracción ya contiene mecanismos concretos:** factory de `PyMuPDFProvider`, guard `validate_pymupdf_page_coverage` con rechazo de vectores no representados, bloque visual matemático identificado, y PNG content-addressed. La clasificación del contenido científico *no está resuelta universalmente* por esos mecanismos. Verificación profunda: 0.2.
- **Representación/contexto ya contiene garantías:** `FlatASTBuilder`, `compute_ast_hash`, `TokenBudgetChunker`, `validate_chunk_coverage`, `DurableContextPlanRepository`. No diseñar nuevo AST/chunker antes de comprobar alcance: 0.3.
- **Inferencia ya contiene un stack de proveedores y quotas:** `CircuitBreakerProvider` → `CachedLLMProvider` (condicional) → `RateLimitedProvider` → `GroqProvider`; G3 pasa `cache_db_path=None`. Eso no prueba techo monetario ni ruteo efectivo del fallback: 0.4.
- **Durabilidad/autoridad ya contiene mecanismos separados:** `ControlPlaneRepository`, `FSMRepository`, `AssemblyLeaseRepository`, staging/materialized, reconciler y sweeper. F18.2 está en `DRAFT` con Gate 1 Wave 1.1 implementada y tareas pendientes; distinguir lectura normativa de completitud runtime: 0.5.
- **G5 ya contiene renderizado matemático explícito y activos:** `TextRenderStrategy`, `AdaptiveFloatStrategy`, `CompilationService.compile_document_with_assets`, `HostTectonicRunner`. No prometer recuperación de ecuaciones que no salieron de B02 ni interpretar `DEGRADED` como conservación: 0.6.
- **Tests ya contienen testigos útiles de alcance delimitado:** B02 sintéticos, W08 foreground con parser/proveedor/Tectonic reemplazados, F18 fencing, TST-STAB. Reusar el SUT y los falsadores; trabajo adicional se justifica por garantía faltante concreta: 0.8.

**Condición de cierre pendiente de 0.1:** completar censo versionado de dependencias bajo búsqueda fiable de imports/refs, contrastar configuración dinámica y plugin/runner externos conocidos sin ejecutar efectos; comprobar que todos los contratos relevantes tienen HITO primario o exclusión motivada. La tabla actual demuestra una **partición provisional suficiente para organizar investigación**, no exhaustividad del grafo ni ausencia global de scripts.


## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Selección productiva | CLI y Compose soportados usan OCR → `runtime/engine.py` → G5; R1/R3 conservan consumidores propios | Una sola ruta efectiva, sin inventar otra | D-1/D-2, Atlas de convergencia | CONFIRMADO ESTÁTICO | E-0.1-011, E-0.1-014, E-0.1-015 |
| Modelo / presupuesto G3 | `SWITCH_MODEL` se acepta pero adaptador recibe el modelo primario | `ENGINEERING_PRINCIPLES.md` §§III–IV; contrato físico explícito | Sin fallback físico aprobado demostrado | DISCREPANCIA CONFIRMADA EN CÓDIGO | E-0.1-002, E-0.1-023 |
| Identidad y reutilización | `COMPLETED` puede devolver PDF previo; W08 tiene DTO de identidad, caché legacy no usada en G3 | Identidad y linaje válidos por generación | W08, Atlas; reejecución externa incierta no automática | TO BE VERIFIED (HITO 0.3/0.5) | E-0.1-003, E-0.1-004 |
| OCR / STEM y G5 | Parser PyMuPDF y guards de vector, math visual/PNG; renderer matemático/figuras existentes | Conservación técnica y trazabilidad de `PROJECT_SCOPE.md` | D-1/D-2 no equivalen a certificación STEM | SOLO COMPONENTES IDENTIFICADOS | E-0.1-021, E-0.1-026, E-0.1-029 |
| Calidad/ciencia | Tests fake/integración y CV extracción cubren contratos distintos | Evaluación física/científica separada, custodia | TST-STAB e issue #34 | LIMITADO, no PASS científico | E-0.1-020, E-0.1-027 |
| Runtime y autoridad | F18 define reglas y plan histórico; la composición física no está ejecutada aquí | NADR F18 aplicables sin duplicación normativa | F18.2 FROZEN NADR y plan propio | AUDITORÍA PROFUNDA DELEGADA A 0.5/0.7 | E-0.1-024, E-0.1-025, E-0.1-030 |

**La matriz es forense, no una aprobación de arquitectura ni de implementación.**

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev | Evidencia (archivo → símbolo) | Observed / alcance |
|---|---|---|---|
| **E-0.1-001** | P2 | `runtime/engine.py::_create_chunk_processor` | `model_name="llama3-70b-8192"`, `primary_window_limit=8192`, `fallback_window_limit=1048576`. Disponibilidad real del modelo y capacidades de la cuenta NO verificadas aquí. |
| **E-0.1-002** | P1 | `core/validation/budget.py::PromptBudgetCalculator.calculate`; `apps/llm_workers/prompt_builder.py::PromptBuilder.build`; `apps/llm_workers/adapters.py::GroqProvider.translate` | `SWITCH_MODEL` puede ser tratado como éxito por builder, pero el envío usa `envelope.model_name`. No se acredita conmutación física de modelo; efecto operacional de una llamada real NO ensayado. |
| **E-0.1-003** | P2 | `apps/cli/pdf_product.py::run_admitted_pdf` | `COMPLETED` devuelve un PDF existente verificado por header, sin volver a ejecutar G3. Falta auditar si la generación guardada distingue configuración/idioma efectivo. |
| **E-0.1-004** | P2 | `runtime/engine.py::_create_chunk_processor`; `core/prompting/inference_identity.py::InferenceReuseIdentityV1` | Caché legacy G3 deshabilitada; identidad W08 candidata incluye idioma y config, pero no constituye autoridad de ejecución. Conexión efectiva a generación por verificar. |
| **E-0.1-005** | P2 | `apps/llm_workers/sync_bridge.py::execute_chunk`; `apps/llm_workers/adapters.py::GroqProvider.translate` | Instrucción menciona un idioma «configurado»; configuración de idioma explícita no fue acreditada en las firmas inspeccionadas. Se debe inspeccionar el resto de la ruta antes de concluir ausencia. |
| **E-0.1-006** | P2 | `apps/cli/pdf_product.py::preflight_product_run`; `docker-compose.runtime.yml`; handoff de laboratorio | Foreground exige Tectonic en PATH; runtime Docker con override documentado; no se ha demostrado un mismo entorno con Tectonic, acceso autenticado y corrida autorizada real. |
| **E-0.1-007** | P2 | `apps/cli/main.py::handle_translate/parse_arguments`, `apps/cli/pdf_product.py::run_admitted_pdf` | Admisión sin inferencia por defecto; `--run` opt-in. La rama `COMPLETED` devuelve PDF verificado sin repetir OCR/G3/G5; no se observó selección de idioma en los argumentos `translate`. |
| **E-0.1-008** | P2 | `apps/ocr_router/__main__.py::_process_document`; `infra/db/context_snapshot_repo.py::enqueue_verified` | OCR produce perfil, AST, plan contextual y snapshots; AST/queue/FSM se persisten en fronteras separadas. No se acredita atomicidad entre archivos físicos/SQLite. |
| **E-0.1-009** | P2 | `runtime/engine.py::run_pipeline`; `runtime/chunk_staging.py::stage_claimed_unit` | AST/plan/snapshots se verifican antes de inicializar proveedor; `PRESERVE` evita POST; se observó ruta `RESULT_STAGED`/completada sin inferencia y `G3_EXTERNAL_UNKNOWN` fuera de runnable. |
| **E-0.1-010** | P2 | `apps/compiler/__main__.py::_process_assembly_task`; `infra/db/assembly_recovery.py::AssemblyLeaseRepository.publish` | G5 usa lease y validación de autoridad para publicar PDF; no equivale a certificación de layout o fidelidad. |
| **E-0.1-011** | P2 | `docker-compose.yml::llm_worker/assembler`; `docker-compose.runtime.yml::llm_worker` | Servicio `llm_worker` ejecuta `runtime/engine.py`, no el R3 legacy; base mantiene `IS_BENCHMARK=1` y override declara `0`. Composición efectiva y runtime comercial siguen NO VERIFICADOS. |
| **E-0.1-012** | P2 | [Comparación Git del corte Atlas con main](https://github.com/RDsanchez-git/translator_pdf/compare/6818e86e21b14e77a606f0c863e9c199b4627601...1d21cfe958cc1de8a33824fed748cd6fe9260f42) y `runtime/recovery.py`/`runtime/resumer.py` | Únicos dos archivos modificados dentro de `apps/core/infra/runtime` y los Compose desde el corte pinneado; agregan cierre de conexión SQLite. No se deduce ejecución física actual. |
| **E-0.1-013** | P2 | `apps/bootstrap/pipeline_factory.py::build_pipeline/build_extraction_pipeline`; `apps/llm_workers/__main__.py::LLMWorkerDaemon` | Hay composición legacy y worker R3 existentes sin selección como G3 productivo en Compose; consumidores de tests, herramientas y sistemas externos aún por inventariar. |
| **E-0.1-014** | P2 | `pyproject.toml::project.scripts`, `apps/cli/main.py::parse_arguments/handle_translate_async`, `tests/unit/test_c4_t06_supported_roots.py` | El entrypoint empaquetado es la CLI canónica; T06 inspecciona estáticamente CLI/Compose/Docker y constata el rechazo R1, sin cubrir lanzadores externos ni comportamiento físico. |
| **E-0.1-015** | P2 | `apps/cli/legacy_translate_async.py::handle_translate_async`, `apps/bootstrap/pipeline_factory.py::build_pipeline`, `apps/llm_workers/__main__.py::LLMWorkerDaemon` | R1 conserva consumidor versionado distinto de CLI productiva; R3 conserva ejecución propia, admission/backpressure/shutdown. No autoriza purga ni adopción del daemon alterno. |
| **E-0.1-016** | P2 | `apps/benchmark/__main__.py::main`, `apps/benchmark/runners/{groq,gemini}_runner.py`, `tools/evaluation/run_regression.py::_run_evaluation` | La extracción productiva sirve también a benchmark y CV; bench usa modelo/proveedor externo, CV compara AST y baseline. Son consumidores con semánticas y permisos diferentes. |
| **E-0.1-017** | P2 | `apps/bootstrap/provider_factory.py::ExtractionProviderFactory.create`, `apps/bootstrap/pipeline_factory.py::build_extraction_pipeline`; `apps/api/server.py`, `apps/ocr_workers/router.py`, `configs/*.yaml` | PyMuPDF está conectado mediante factory; archivos API/worker/config nombrados existen pero están vacíos en este commit. No deben contarse como capacidades implementadas. |
| **E-0.1-018** | P2 | `apps/lab/offline_pdf_lab.py`, `apps/lab/convergence_compose_preflight.py`, `tests/integration/test_w08_cli_foreground_single_generation_offline.py` | Los testigos de laboratorio limitan red/transporte; W08 sustituye parser, transporte HTTP y compilación Tectonic. Son pruebas contractuales parciales, no ejecución científica real. |
| **E-0.1-019** | P2 | `apps/benchmark/__main__.py::main` y `GroqBenchmarkRunner.warmup` | Un root manual abre PDF físico (`[Amoretal_2023]_3hojas.pdf`) y tiene camino de inferencia Groq. Posible egress al ejecutarlo: exige permiso/privacidad; no se afirma que haya sido ejecutado. |
| **E-0.1-020** | P2 | `.github/workflows/ci.yml`, `.github/workflows/continuous-verification.yml`, `pyproject.toml::tool.pytest.ini_options` | Suite por defecto usa `-m not e2e`; workflow CV invoca `run_regression`. No inferir aptitud de producto de CI técnico PASS ni convertir CV sin corpus en PASS. |
| **E-0.1-021** | P2 | `apps/bootstrap/provider_factory.py::ExtractionProviderFactory.create`, `infra/extraction/providers/pymupdf_{provider,integrity,math_visual,image_assets}.py`, `apps/bootstrap/pipeline_factory.py::build_extraction_pipeline` | La ruta B02 materializa texto/PNG matemático cuando es identificable y rechaza vectores sin representación; capacidades ya existentes, cobertura física y matemática restante por auditar en 0.2. |
| **E-0.1-022** | P2 | `core/chunking/contextual_plan.py::prepare_contextual_plan`, `core/chunking/manifest_contract.py::validate_chunk_coverage`, `infra/db/context_snapshot_repo.py::enqueue_verified/load_verified` | AST hash, cobertura, manifest y snapshots tienen contratos diferenciados; existencia no demuestra identidad completa de una nueva generación o traducción. Dueño 0.3 y 0.5. |
| **E-0.1-023** | P2 | `apps/llm_workers/prompt_builder.py::PromptBuilder.build`, `core/validation/budget.py::calculate`, `apps/llm_workers/adapters.py::GroqProvider.translate`, `core/prompting/measurement_adapter.py` | El stack físico usa `envelope.model_name`; `SWITCH_MODEL` se acepta como envelope sin cambio de modelo. Medición/logical payload, renderizado físico y límites del proveedor deben reconciliarse en 0.4. |
| **E-0.1-024** | P2 | `infra/db/control_repo.py::pick_task/stage_chunk_result/mark_g3_external_unknown`, `infra/db/staged_publication.py`, `runtime/publication_pipeline.py`, `infra/db/assembly_recovery.py::publish` | Contratos de claim, receipt, materializado, FSM y publicación física separados; los commits no componen una transacción universal con HTTP/filesystem. Dueño 0.5. |
| **E-0.1-025** | P2 | `docs/architecture/adr/phase-18/NADR/NADR-F18-03.md`, `docs/architecture/adr/phase-18/plans/PHASE_18.2_EXECUTION_PLAN.md` | Obligaciones F18.2 de efectos inciertos ya gobiernan esta superficie y el plan existente declara Wave 1.1 DONE con trabajo posterior pendiente. Referir a 0.5 sin duplicar gobernanza. |
| **E-0.1-026** | P2 | `core/compiler/rendering/implementations.py::TextRenderStrategy/AdaptiveFloatStrategy`, `core/compiler/service.py::CompilationService`, `apps/compiler/tectonic_runner.py::HostTectonicRunner` | Hay manejo de matemática explícita, floats y PNG que llega al runner físico; la calidad del PDF no está probada por observar esas clases. Dueño 0.6. |
| **E-0.1-027** | P2 | `tests/integration/test_verification_pipeline_connection.py`, `test_w08_cli_foreground_single_generation_offline.py`, `docs/architecture/adr/tests_stabilization/PLAN_REMEDIACION_TESTS_PIPELINE.md` | Extracción sintética y W08 fake verifican propiedades distintas; TST-STAB clasifica límites y no ejecutó una falsación particular. No extrapolar a certificación científica: 0.8. |
| **E-0.1-028** | P2 | `.github/workflows/{ci,continuous-verification}.yml`, `apps/lab/offline_pdf_lab.py`, `docker-compose.runtime.yml` | Infraestructura de test separa aislamiento fake, CI técnico y CV de corpus. El override de runtime no certifica que una composición con proveedor real/TeX funcione. Investigación en 0.7/0.8. |
| **E-0.1-029** | P2 | `apps/bootstrap/extraction_config.py::ExtractionProviderId`, `apps/bootstrap/provider_factory.py::ExtractionProviderFactory.create`, `infra/extraction/providers/{docling_provider,tesseract_provider}.py` | Existen clases/IDs alternativos para extracción; la factory conectada únicamente construye PyMuPDF y rechaza otros IDs. No proponer nuevos proveedores sin investigación 0.2. |
| **E-0.1-030** | P2 | `docker-compose.golden.yml::services.llm_worker`, `Dockerfile::CMD`, `apps/compiler/sandbox/server.py::compile_chunk` | Compose golden declara variables Gemini; Dockerfile selecciona `runtime/engine.py` cuyo proveedor configurado es Groq; la ruta HTTP `/compile` existe como endpoint separado de G5. No hay evidencia de despliegue funcional ni de consumidor productivo de ese endpoint. |
| **E-0.1-031** | P2 | `core/routing/router.py::StrategyRouter.route`, `apps/llm_workers/routing.py::TranslationStrategyRouter.route`, `runtime/settings.py::RuntimeSettings` | Hay routers de estrategia existentes y flags F18; su presencia no prueba fallback físico de proveedor ni activación real de garantías. |
| **E-0.1-032** | P2 | Árbol Git recursivo del corte `main@1d21cfe`; `Dockerfile.fake`, `apps/daemons/{chaos_runner,fake_gemini}.py`, `apps/lab/g3_fake.py`, `infra/redis/queues.py` | Censo de roots/versionado separa herramientas fake/chaos y stubs de procesos seleccionados; imposible inferir invocadores externos ni datos de runtime de un árbol de archivos. |
| **E-0.1-033** | P2 | `PIPELINE_GRAPH.rar` / `PIPELINE_GRAPH.md` aportados por owner; formato Mermaid, estadísticas y hashes §3 | Fuente **contextual no versionada**: 544 archivos, 13.061 aristas sin binding cross-file; falta SHA de generación. No implica ejecución, consumidores reales o completitud dinámica. |
| **E-0.1-034** | P2 | Grafo recibido vs `runtime/engine.py::run_pipeline/_create_chunk_processor` y `apps/bootstrap/provider_stack_factory.py::build_provider_stack` en main | El grafo **omite el archivo G3 seleccionado** y la definición `async def` de factory, aunque ambos existen en el código. Se prohíbe usar ausencia de arista como ausencia de consumidor. |
| **E-0.1-035** | P2 | Grafo `call_getattr` vs `apps/cli/main.py::handle_translate`, `apps/compiler/__main__.py::RenderGeometryAdapter/RenderAssetAdapter` | Las llamadas `getattr` focales acceden a atributos de argumentos/AST y no constituyen descubrimiento de providers mediante reflexión. En otros módulos aún puede existir dispatch dinámico; no se afirma ausencia general. |
| **E-0.1-036** | P2 | Grafo vs `apps/llm_workers/adapters.py::GroqProvider.translate`, `apps/bootstrap/provider_stack_factory.py::build_provider_stack`, `apps/cli/pdf_product.py::_run_g3` | Las definiciones asíncronas del adaptador y factory no están representadas; `_run_g3` sí produce `call_run_pipeline` pero el grafo no resuelve su destino G3. Un análisis exhaustivo requiere imports, contratos y composición, no solo `call_*`. |
| **E-0.1-037** | P2 | `translator_pdf_graph.rar::graph_inventory.json/graph_summary.md`; Git tree `main@1d21cfe` | **Cobertura v2 comprobada:** 579 Python versionados y parseados, 0 fallos, 6.399 edges; 524 inferidos se distinguen de 5.875 estáticos. Una eliminación local de PDF no es código, pero impide interpretar la salida como solo un checkout limpio por SHA. |
| **E-0.1-038** | P2 | `graph_edges.csv` + `apps/cli/pdf_product.py::_ingest/_run_g3/_run_g5`, `runtime/engine.py::_create_chunk_processor` | Se corroboraron los enlaces CLI→G3, G3→factory, foreground→OCR y foreground→G5, con distinción de confianza `static`/`inferred`; prueba de composición estática, no E2E. |
| **E-0.1-039** | P2 | `graph_unresolved.csv` + `apps/ocr_router/__main__.py::_process_document`, `runtime/chunk_staging.py::stage_claimed_unit`, `apps/llm_workers/sync_bridge.py::execute_chunk` | Persisten llamadas a puertos/atributos inyectados sin tipo resuelto por analizador; se rastrearon constructores y contratos en código. `unresolved` no equivale a plugin ni ausencia de consumidor. |
| **E-0.1-040** | P2 | `graph_dynamic.csv`, `apps/compiler/__main__.py::_process_assembly_task`, `apps/compiler/tectonic_runner.py::HostTectonicRunner.compile` | Los sitios dinámicos combinan `getattr` de datos, expresiones compuestas y `subprocess.run` real del compilador; no son evidencia de 1.064 puntos de extensión desconocidos. El servicio del host sigue no verificado. |
| **E-0.1-041** | P2 | `graph_unresolved.csv/graph_dynamic.csv` por roots; `apps/ocr_router/__main__.py::OCRRouterDaemon.__init__`, `apps/cli/pdf_product.py::_ingest` | Subconjunto operacional extendido: 1.239 unresolved y 133 sitios dinámicos/de efecto; principales puertos OCR se inyectan por constructor desde roots versionados. El número de filas no representa consumidores distintos. |
| **E-0.1-042** | P2 | `runtime/engine.py::run_pipeline/_create_chunk_processor`, `runtime/chunk_staging.py::stage_claimed_unit`, `apps/llm_workers/sync_bridge.py::SyncProviderBridge.execute_chunk`, `apps/bootstrap/provider_stack_factory.py::build_provider_stack`, `apps/llm_workers/circuit_breaker_provider.py::CircuitBreakerProvider.translate` | Destino de proveedor y wrappers CB/RateLimit se compone explícitamente por factory; llamada vía protocolo inyectado y POST real no están probados dinámicamente. No se confirma fallback multimodelo. |
| **E-0.1-043** | P2 | `apps/compiler/__main__.py::__main__/_process_assembly_task`, `apps/cli/pdf_product.py::_run_g5`, `apps/compiler/tectonic_runner.py::HostTectonicRunner.compile`, `graph_dynamic.csv` | Ambos roots G5 inyectan servicio/resolver/runner; `subprocess.run` ejecutaría Tectonic, pero no fue corrido. El endpoint `apps/compiler/sandbox/server.py::compile_chunk` es raíz alternativa identificada, no seleccionada en Compose. |
| **E-0.1-044** | P2 | `graph_dynamic.csv`, `audit/build/tests/test_i0_1.py`, `tests/integration/test_g5_assembler_worker_integration.py`, `tools/evaluation/execution/process_runner.py`, `apps/daemons/reconciler.py::__main__` | Los tres `__import__` están en tests, los siete `setattr` en tests y `subprocess.run` tiene consumidores de laboratorio/evaluación/compilación; el reconciler construye handlers y repositorios explícitos. Persisten configuraciones y procesos externos no observables. |

**Criterio de severidad aplicado (§7.1):** solo `E-0.1-002` es **P1 por incumplimiento estructural demostrado** de la decisión de presupuesto frente al request físico. Los demás E-IDs se mantienen **P2 como evidencia contextual o de riesgo latente**, sin declarar defecto no comprobado. La ausencia de una demostración en esta pasada no es un P1 automático; ningún E-ID implica PASS de ciencia.

### Evidencia E-0.1-002: conmutación de modelo no materializada en el request G3

* **Archivo fuente primario:** `apps/llm_workers/prompt_builder.py`; corroboración `core/validation/budget.py`, `apps/llm_workers/adapters.py`, `runtime/engine.py`.
* **Símbolos auditados:** `PromptBudgetCalculator.calculate`, `PromptBuilder.build`, `GroqProvider.translate`, `_create_chunk_processor`.
* **Declaración observada (fragmentos mínimos del SHA auditado):**

```python
# core/validation/budget.py
status=BudgetDecisionType.SWITCH_MODEL,

# apps/llm_workers/prompt_builder.py
if decision.status in (BudgetDecisionType.VALID, BudgetDecisionType.SWITCH_MODEL):
    ...
model_name=self.model_name,
target_provider="fallback_large_window" if decision.status == BudgetDecisionType.SWITCH_MODEL else "primary"

# apps/llm_workers/adapters.py
response = await self._client.chat.completions.create(
    model=envelope.model_name, temperature=1e-5, stream=False, **kwargs
)
```

* **Observed:** el budget puede emitir `SWITCH_MODEL`, el builder lo acepta como `BuildSuccess` con `target_provider=fallback_large_window` **sin modificar el nombre del modelo**, y el adaptador Groq envía `envelope.model_name`, no `target_provider`. El G3 seleccionado fija el modelo por constructor; no se ha ejecutado una llamada al proveedor real.
* **Required:** `ENGINEERING_PRINCIPLES.md` §III (`Explicit over Implicit`) y §IV (`Cero Fallos Silenciosos`) exigen no representar una ruta admitida como efectiva si la capacidad física solicitada no está materializada; el contrato tipado `BudgetDecisionType.SWITCH_MODEL` debe reconciliarse con la construcción física.
* **Decision:** D-1/D-2 mantienen una sola ruta operativa PDF→PDF. No existe decisión demostrada en esta auditoría que autorice interpretar `target_provider` como conmutación real al margen del proveedor.
* **Hallazgo forense:** discrepancia reproducible por lectura de código entre `BudgetDecisionType.SWITCH_MODEL` y el modelo efectivamente seleccionado por el adaptador.
* **Consecuencia arquitectónica:** un request considerado admisible bajo la ventana de fallback puede intentar usar el modelo primario; la aceptación lógica no demuestra capacidad de contexto física. **No** se cuantifica aquí el impacto económico ni se afirma un resultado HTTP determinado.
* **Severidad:** **P1**, debido a la incompatibilidad tipada en el recorrido seleccionado; no por presunción de gasto real.
* **Estado:** OPEN; destinado a investigación 0.4 y decisión posterior por la cadena de gobernanza; sin prescripción de implementación.

Los IDs existentes no se reasignan. `E-0.1-023` complementa `E-0.1-002` con la frontera de medición/serialización; no constituye un segundo GAP. No hubo tests ejecutados, egress real ni certificación científica.

## 14. GAPS CONSOLIDADOS

**GAP local de Flow Audit:** solo se consolida una discrepancia demostrada. No se emite una Gap Matrix global ni se predetermina la solución; la consolidación transversal sigue siendo propiedad de HITO 0.9.

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.1-01** | El builder admite `SWITCH_MODEL` pero el adaptador no materializa esa conmutación en el modelo físico enviado | **E-0.1-002** (corroboración E-0.1-023) | `ENGINEERING_PRINCIPLES.md` §§III–IV; presupuesto G3 | Etapa `pdf-pdf-product-readiness` — investigación HITO 0.4, posterior ADR/NADR/plan | OPEN |

**Ninguna otra observación se transforma en GAP sin contraste `Observed/Required/Decision` y evidencia suficiente.** Pendientes sobre idioma, generación, efectos y STEM permanecen hipótesis, no decisiones de remediación.

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto actual | Evidencia | Implicación / destino |
|---|---|---|---|---|
| H-0.1-A | El fallback `SWITCH_MODEL` no conmuta físicamente el modelo en la ruta seleccionada | CONFIRMADA ESTÁTICAMENTE | E-0.1-002 | GAP-0.1-01; HITO 0.4 |
| H-0.1-B | Cambiar idioma/modelo del mismo PDF devuelve la generación `COMPLETED` anterior | NO VERIFICABLE EN 0.1 | E-0.1-003, E-0.1-004 | DQ-0.1-01: configuración/identidad por generación sin prueba física; 0.3/0.5. No impide identificar root y consumidor |
| H-0.1-C | F18 y legacy contienen capacidades útiles que no selecciona la CLI | CONFIRMADA COMO EXISTENCIA, no como aptitud | E-0.1-015, E-0.1-025 | Evaluar uso y cumplimiento sin reimplementar; 0.5 |
| H-0.1-D | B02/G5 rechazan o degradan casos STEM todavía no certificados | CONFIRMADA (mecanismos existentes, no cobertura universal) | E-0.1-021, E-0.1-026 | Rechazo/estrategias observadas; alcance físico y científico pendiente en 0.2/0.6/0.8 |
| H-0.1-E | Restricciones FinOps/egress impiden por sí mismas prueba comercial controlada | NO VERIFICABLE EN 0.1 | E-0.1-006, E-0.1-028 | DQ-0.1-02: faltan permiso de egress, credenciales y ensayo físico; 0.4/0.7. No condiciona inventario estático |
| H-0.1-F | Roots soportados corresponden al mapa positivo del Atlas | CONFIRMADA ESTÁTICAMENTE | E-0.1-011, E-0.1-014 | No extrapolar a despliegues externos |
| H-0.1-G | Implementación de producción cambió sustancialmente desde el corte del Atlas | RECHAZADA en los roots comparados | E-0.1-012 | Recuperación cambió en dos archivos; profundizar 0.5 |
| H-0.1-H | Solo existe un consumidor de cada factory/dispatcher legacy | RECHAZADA para los casos rastreados | E-0.1-015, E-0.1-016 | Inventario dinámico/external no verificable aquí; 0.7 |
| H-0.1-I | Benchmark y CV acreditan el mismo E2E PDF→PDF que la ruta productiva | RECHAZADA | E-0.1-016, E-0.1-027 | CV extraccion y fake no sustituyen ciencia; 0.8 |
| H-0.1-J | No existen consumidores fuera del repositorio de R1/R3 | NO VERIFICABLE | E-0.1-014, E-0.1-032 | Falta inventario externo/host, no hay autoridad de observarlo; 0.7 |
| H-0.1-K | Cada frontera relevante puede tener un HITO investigador primario sin duplicación | CONFIRMADA PARA LAS FRONTERAS INVENTARIADAS | §6.1–6.2, E-0.1-022 | Matriz asigna responsable principal a cada frontera conocida; DQ-0.1-04 pide validar suficiencia/ajustes, no prueba de exhaustividad universal |
| H-0.1-L | No existen mecanismos concretos de preservación STEM en la ruta | RECHAZADA COMO AUSENCIA GENERAL | E-0.1-021, E-0.1-026 | Alcance científico por verificar en 0.2/0.6 |
| H-0.1-M | El grafo proporcionado cubre todas las rutas y prueba ausencia de consumidores dinámicos | RECHAZADA | E-0.1-033, E-0.1-034, E-0.1-036 | No cerrar HITO basándose en ese negativo; censo estático adicional y externos NO VERIFICABLE |
| H-0.1-N | Todos los `getattr` que figuran en el grafo corresponden a carga de servicios | RECHAZADA para casos focales, generalidad no verificada | E-0.1-035 | Distinguir atributo de dato, dispatch por protocolo y reflexión de importación |
| H-0.1-O | El grafo mejorado aún omite `runtime.engine` y funciones `async` | RECHAZADA para v2 | E-0.1-037, E-0.1-038 | Los 579 Python y enlaces estáticos se indexan; confirmar consumidores indirectos mediante puertos |
| H-0.1-P | Toda llamada `unresolved` implica un consumidor desconocido productivo | RECHAZADA como generalización | E-0.1-039, E-0.1-040 | Priorizar solo puertos, configuración y efectos relevantes por HITO 0.2–0.8 |
| H-0.1-Q | Los puertos inyectados de OCR/G3/G5 carecen de consumidores concretos en roots soportados | RECHAZADA para las composiciones auditadas | E-0.1-041..043 | La operación real sigue NO VERIFICABLE: 0.2/0.4/0.6/0.7 |
| H-0.1-R | `__import__`/`setattr` encontrados por el v2 revelan un loader productivo oculto | RECHAZADA en las apariciones del CSV | E-0.1-044 | Las llamadas identificadas residen en tests; runtime con plugins externos no es observable: 0.7 |

**Disposición tipada (§8.1–8.2):** todas las H-0.1-A..R tienen ahora un prefijo terminal `CONFIRMADA`, `RECHAZADA` o `NO VERIFICABLE` dentro del alcance declarado. H-0.1-B/E/J no se declaran refutadas ni probadas: sus razones, no-bloqueo del mandato de *mapear la ruta estática* y destinos están en DQ-0.1-01..03. La aprobación de perímetro H-0.1-K sigue siendo un gate de cierre; la hipótesis se confirma **solo para el conjunto de fronteras actualmente inventariado**, no para cada uso futuro.

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

- **¿Hay una ruta PDF→PDF soportada?** Sí, según handoff integrado; éxito con fake no demuestra producto real.
- **¿Está auditado su grafo completo y sus capacidades?** No; ya se contrastaron las aristas estáticas centrales del Atlas y la composición seleccionada contra `main`, pero faltan consumidores secundarios/dinámicos, las garantías de cada frontera y evidencia física.
- **¿Se autorizan cambios por los hallazgos de apertura?** No; falta cerrar la auditoría, derivar decisiones normativas y aprobar el plan.
- **¿Debe la nueva etapa inventar soluciones?** No por defecto: se exige búsqueda y clasificación de capacidades y consumidores antes de afirmar ausencia.

## 21. CIERRE DEL HITO 0.1

### 21.1 Pre-checklist canónico — `IN_PROGRESS`

Evaluación previa a la revisión del owner, usando `1.2_METH_FOR_FORENSIC_HITOs.md` §§8.1–8.2; **no** es certificación FROZEN.

| Gate de cierre | Estado | Evidencia / condición restante |
|---|---|---|
| Metadata, changelog, límite epistemológico y método | CONFORME EN BORRADOR | §§1–2 y changelog; falta versión de congelamiento |
| Alcance + fuentes y módulos | CONFORME PARCIAL | §3 tiene censo 579/579 de módulos Python versionados en grafo, pero la auditoría propia es focal por fronteras; conservar `REFERENCIADO`/`NO VERIFICABLE` por módulo, no declarar 579 semánticamente auditados |
| Evidencias con ID, severidad y Observed/Required/Decision | CONFORME EN BORRADOR | E-0.1-001..044; E-0.1-002 extendida (P1). No promover riesgos P2 a defectos sin causalidad |
| GAP trazado a evidencia, contrato y destino | CONFORME EN BORRADOR | GAP-0.1-01 → E-0.1-002 → 0.4/gobernanza, sin decidir solución |
| Hipótesis cerradas o diferidas según §8.2 | CONFORME EN BORRADOR | H-0.1-B/E/J tipadas como `NO VERIFICABLE` y diferidas con causa, destino y no-bloqueo del mandato; K confirmada solo para fronteras inventariadas. Requiere verificación owner del perímetro |
| Contradicciones y antecedentes FROZEN | CONFORME PARCIAL | §4 ya reutiliza HITOs 17-BIS/F18; diferencia histórica en CV/CI con HITO_6.4 se remite a 0.8, sin declararse contradicción del mismo SHA |
| Veredicto, declaración de garantías y siguiente paso | **PENDIENTE DE REVISIÓN** | El veredicto está limitado a la ruta estática; falta validación owner, versión/fecha FROZEN y declaración de garantías final |
| Gobernanza de incorporación Git y denominación | **PENDIENTE** | Metodología general §3.5.1 exige `phase-{fase}` y §6.7 sitúa commit de HITOs al finalizar Fase 0; nombre de iniciativa y PR Draft deben reconciliarse antes de merge |

### 21.2 Deferred Questions (sin resolución inventada)

| ID | Pregunta / razón por la que no se concluye ahora | Destino / criterio |
|---|---|---|
| DQ-0.1-01 | ¿Una nueva configuración de idioma/modelo crea o reutiliza correctamente generación cuando el mismo `document_id` está `COMPLETED`? El grafo y la CLI no prueban el comportamiento físico | HITO 0.3 (identidad) y 0.5 (autoridad), reproducción aislada autorizada |
| DQ-0.1-02 | ¿Cuota, credenciales, modelo y proveedor permiten una ejecución pagada controlada? No se probó red real ni se autorizó egress | HITO 0.4 (provider/FinOps) y 0.7 (entorno); no transmitir PDF privado |
| DQ-0.1-03 | ¿Existen launchers/consumidores de R1/R3 fuera de Git? El árbol no inspecciona instalaciones ni procesos del host | HITO 0.7; inventario operativo del owner si resulta necesario, de otro modo `NO VERIFICABLE` |
| DQ-0.1-04 | ¿El reparto de fronteras 0.2–0.9 es suficiente y evita doble auditoría? Existe matriz de dueños primarios para las fronteras conocidas, pero la suficiencia del perímetro no está refrendada formalmente | Revisión del owner sobre §6.2 antes de declarar FROZEN; no es plan de implementación |
| DQ-0.1-05 | ¿Cómo reconciliar `pdf-pdf-product-readiness` (nombre de iniciativa acordado) con la convención de carpeta `phase-{fase}`, y cuándo integrar HITOs en main según §6.7 general? Una respuesta no se infiere de la especialización | Governance/owner antes de merge o cierre de Fase 0; mantener Draft PR #66 sin merge, sin reinterpretar ni editar metodología FROZEN |

**Criterio de finitud:** 0.1 puede concluir *el mapa versionado y los límites de consumidores de la ruta* sin haber ensayado todas las propiedades profundas de 0.2–0.8. Si una incógnita sí impide reconocer una raíz o consumidor primario, debe resolverse antes del cierre; si no, debe cumplir las cuatro condiciones de §8.2. No basta un `TO BE VERIFIED` sin causa ni destino.

### 21.3 Estado y declaración de cierre pendiente

**Estado del HITO:** IN_PROGRESS v1.0.8; **NO FROZEN**.  
**Condición de cierre:** pendiente. Requiere inventario completo de entrypoints y consumidores relevantes (incluidos imports/configuración dinámica y herramientas), reconciliación de obligaciones con su versión vigente, referencias de evidencia y límites por superficie, clasificación de hipótesis, contradicciones resueltas o declaradas, y criterios verificables de transferencia a otros HITOs. Ya existe contraste estático inicial del Atlas, selección de roots, consumidores versionados focales, mapa de fronteras y dueño primario por HITO (§6.1–6.3). **No** equivale a censo global exhaustivo. El índice textual no permitió descartar consumidores por ausencia de resultados; quedan rutas dinámicas/externas, trazabilidad de dependencias relevantes y contraste de alcance por normativa. No se atribuye a 0.1 la revisión profunda de cada propiedad que está correctamente delegada a otro HITO. La inspección del grafo v1 (E-0.1-033..036) reveló omisiones importantes; el grafo v2 (E-0.1-037..040) **sí cubre los 579 Python versionados** e identifica 6.399 enlaces estáticos/inferidos, con fronteras OCR/G3/G5 comprobadas por lectura focal. **No** autoriza certificar resolución universal de 7.384 llamadas o 1.064 sitios potencialmente dinámicos: muchos son efectos externos/atributos, y los puertos inyectados necesitan análisis de composición. Consumidores host ajenos a Git permanecen `NO VERIFICABLE`, con destino 0.7; contratos internos profundos se asignan a 0.2–0.8. El triaje focal §3 (E-0.1-041..044) localizó bindings de OCR/G3/G5 y separó tests/reflexión de efectos físicos; quedan por resolver o diferir conforme a §8.2 las DQ-0.1-01..04 y obtener validación de cierre del owner. La evaluación preliminar §21.1 **no** equivale a checklist completado. El registro de fuentes §4 ya declara HITOs previos y el triaje de hipótesis está acotado por §21.2. La denominación de carpeta, el instante de integración del PR y la suficiencia formal del perímetro permanecen abiertos como **gates de gobernanza**, no como brechas de código.  
**Verificación de cadena de gobernanza:** metodología general v1.3.0 (prevalece) > metodología HITOs v1.2.0 FROZEN (especializada) > ADR/NADR vigentes y decisiones D-1/D-2 > Atlas/handoffs descriptivos y HITOs 17-BIS/F18 previos > evidencia actual del HITO > futuro ADR/NADR/Execution Plan. No hay ADR/NADR ni Execution Plan aprobados de esta iniciativa. El plan F18.2 conserva su propia autoridad. **Contradicciones con HITOs previos:** no se acreditó una contradicción sobre el mismo SHA; la diferencia temporal entre HITO_6.4 y workflow CV actual se documenta para reconciliación en 0.8. **Conflictos de nomenclatura/commit:** DQ-0.1-05 pendiente de autoridad owner. **Revisión de cierre:** no aprobada.  
**Decision Candidates generados:** ninguno aprobado; DQ-0.1-01..05 conservan las decisiones/evidencias pendientes, con sus destinatarios. GAP-0.1-01 no prescribe solución.  
**Siguiente paso recomendado:** validar por owner la suficiencia de la matriz §6.2 y resolver DQ-0.1-05 de nomenclatura/merge según metodología superior; después, aplicar checklist §21.1 y emitir declaración FROZEN solo si todos los gates se satisfacen. Mantener PR #66 Draft y sin merge. Auditar HITO 0.2 sin ejecutar código de producción.

> No usar esta versión `IN_PROGRESS` como prueba de que la auditoría de Fase 0 esté completa.
