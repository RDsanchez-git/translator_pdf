# Plan de implementación de la convergencia operativa única PDF→PDF — R1/R2/R3

**Versión:** v1.0.17 · **Fecha:** 2026-11-09 · **Estado:** especificación operativa versionada; **testigo funcional PDF→PDF acreditado en laboratorio el 2026-11-12, sin cierre global ni certificación**  
**Repositorio / rama de referencia:** `RDsanchez-git/translator_pdf` / `pipeline_stabilization`  
**Commit inspeccionado:** `6a5ee41886b935c2c0f3a107a42620d93de31efb` (#40 MERGED). Los caminos, configuraciones y tests descritos se refieren a **ese commit**, no a una instalación desplegada.  
**Documento rector:** [Decisión D-1/D-2, cabecera vigente, §§0, 2, 6–8](DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md). El nombre histórico `CANDIDATE` no revoca la **aprobación del owner del 2026-11-08**.  
**Matriz compañera obligatoria:** [MATRIZ_VERSIONADA_COMPOSICION_DISPOSICION_R1_R2_R3_V1_20261109.md](MATRIZ_VERSIONADA_COMPOSICION_DISPOSICION_R1_R2_R3_V1_20261109.md), v1.0.1.  
**Carácter de las decisiones de este plan:** recomendaciones de integración sobre código observado. Las disposiciones `RETIRE_CANDIDATE` **no** autorizan borrar archivos; las condiciones de despliegue son independientes. No se aprueba modificar NADR FROZEN ni ejecutar inferencia paga.

## 0. Decisión ejecutiva — el objetivo que NO debe desplazarse

**Máxima prioridad: CERRAR UNA SOLA RUTA OPERATIVA PDF→PDF** con el código existente. No se persigue en este hito que esa ruta traduzca satisfactoriamente toda clase de papers, que sea científica o lingüísticamente certificada, que esté lista para usuarios externos, ni que agote W08-3. Es posible obtener `CONVERGENCIA_OPERATIVA_ACREDITADA` y, a la vez, conservar `PRODUCT_READINESS=NOT_DEMONSTRATED`.

**D-1 vigente:** una CLI como adaptador de entrada, una cadena contractual PDF→PDF y ningún segundo motor productivo. `translate` admite al inbox; `translate --run` ejecuta en primer plano **los mismos componentes** para casos controlados.  
**D-2 vigente:** continuidad R2/OCR → G3 (`runtime/engine.py`) → publicación → G5/Tectonic. Se reutilizan componentes puntuales R1 (contexto, prompt, validación/healing cuando sea compatible) y R3 (controles operativos cuando la brecha esté acreditada); **no** se trasplantan `AsyncDispatcher`, `TranslationPipeline` o `LLMWorkerDaemon` como motores paralelos.

Tres afirmaciones diferentes, nunca intercambiables:
1. **Composición seleccionada en código**: los entrypoints actuales pueden llamar a un único G3/G5. Ya existe en parte.
2. **Convergencia operativa acreditada**: arranque reproducible, handoff real entre procesos, autoridad/linaje coherentes, recuperación segura y exclusión de rutas rivales. **Pendiente**.
3. **Traductor científico productivamente útil**: cobertura PDF/layout/math, política `PRESERVE` física, traducción fiel, calidad G5 y aceptación de corpus. **Trabajo posterior**; las pérdidas detectadas siguen fallando explícitamente.

La ruta debe **rechazar** documentos que no puede representar, no relajar B02 para obtener un PDF artificial. Los contratos F18/W06/W07/W08 no pueden vulnerarse para forzar un PASS operacional. Eso no los convierte automáticamente en subproyectos de certificación de producto.

## 1. Evidencia concreta que gobierna el plan

| ID | Hecho y alcance | Fuente |
|---|---|---|
| E01 | La cabecera de D-1/D-2 declara dirección aprobada; el resto del expediente conserva texto histórico de 2026-11-05. | Decisión rectora, primeras líneas |
| E02 | #38, #39 y #40 están integrados. #40 conectó contexto OCR→snapshots→G3 y una prueba CLI integrada con parser/HTTP/Tectonic controlados. No demostró Compose real. | [PR #40](https://github.com/RDsanchez-git/translator_pdf/pull/40); `tests/integration/test_w08_cli_foreground_single_generation_offline.py` |
| E03 | `handle_translate` es el destino de `translate`; `handle_translate_async` aún existe pero no es el handler del subcomando. | `apps/cli/main.py::parse_arguments` y `handle_translate` |
| E04 | El OCR daemon construye `prepare_contextual_plan`, escribe AST, snapshots/plan/tareas y mueve el PDF de inbox a archive/error; G3 valida `load_verified` antes del proveedor. | `apps/ocr_router/__main__.py`, `core/chunking/contextual_plan.py`, `infra/db/context_snapshot_repo.py`, `runtime/engine.py` |
| E05 | `docker-compose.yml` arranca `runtime/engine.py` pero le pasa `IS_BENCHMARK=1`; G3 lo rechaza. `docker-compose.runtime.yml` cambia ese valor a `0` y reubica SQLite/data/output. **La configuración efectiva no fue ejecutada aquí.** | Ambos Compose; `runtime/engine.py::run_pipeline` |
| E06 | `apps/lab/offline_pdf_lab.py` usa extractor real, SQLite real y Tectonic real en contenedor aislado, con HTTP LLM falso. B03 registra **testigo histórico reportado por el owner**, no reproducción nueva ni verificación de Compose multiproceso. El laboratorio exige imagen/caché histórica pinneada. | `apps/lab/offline_pdf_lab.py`; `working-observations/B03_20261106_CONVERGENCIA_FUNCIONAL_OFFLINE_NO_CIERRE_GOBIERNO.md` |
| E07 | G3 llama `execute_chunk` del bridge, no al `AsyncDispatcher` R1. El bridge `execute(node)` legacy sigue disponible pero no es el contrato G3. | `runtime/chunk_staging.py`; `apps/llm_workers/sync_bridge.py` |
| E08 | G3 deshabilita explícitamente la caché `prompt_hash` antigua con `cache_db_path=None`. El default de `build_provider_stack` aún permite esa caché en otros consumidores. W08-3 queda abierto. | `runtime/engine.py::_create_chunk_processor`, `apps/bootstrap/provider_stack_factory.py`; [issue #36](https://github.com/RDsanchez-git/translator_pdf/issues/36) |
| E09 | Compose no arranca `apps/llm_workers/__main__.py::LLMWorkerDaemon`; su existencia en Git no prueba actividad ni ausencia de consumidores externos. | Compose y módulo R3; no hay inventario de procesos host |
| E10 | B02 detecta contenido vectorial no representado y falla explícitamente antes de G3/G5; tres tests de integración histórica permanecen FAIL. | `infra/extraction/providers/pymupdf_integrity.py`; `tests/integration/test_verification_pipeline_connection.py` |
| E11 | #41–#44 son Draft apilados y divergidos del merge #40; #45 está cerrado sin merge. No forman parte de HEAD ni son prerrequisitos automáticos de esta convergencia. | [#41](https://github.com/RDsanchez-git/translator_pdf/pull/41), [#42](https://github.com/RDsanchez-git/translator_pdf/pull/42), [#43](https://github.com/RDsanchez-git/translator_pdf/pull/43), [#44](https://github.com/RDsanchez-git/translator_pdf/pull/44) |
| E12 | Ni Git/CI ni este documento prueban que no existan SQLite productivas, procesos viejos o política de rollback en otra instalación. | Límite explícito de evidencia; `working-observations/W08_2C_TRANSICION_GENERACIONES_LEGACY_20261107.md` |

**Prevalencia:** contrato FROZEN aplicable → D-1/D-2 aprobadas en la cabecera vigente → código HEAD y pruebas verificadas → observaciones históricas con sujeto y fecha → propuestas. La matriz de este plan **no reemplaza** el Atlas, Charter, NADR, corpus ni oráculos. Los estados de Board/G-1/G-2 en tablas históricas son históricos respecto de la dirección aprobada y no deben bloquearla artificialmente.

## 2. Grafo TO-BE de ejecución: un solo propietario por hecho

```text
 CLI: apps/cli/main.py / pdf_inbox.py
    | SHA256 PDF -> data/inbox (misma raíz de datos que el OCR)
    v
 OCR: apps/ocr_router/__main__.py
    | build_extraction_pipeline (PyMuPDF actual; B02 fail-closed)
    | Layout -> Flat AST -> perfil -> prepare_contextual_plan (contexto R1)
    | ASTRegistry archivo + documents.db perfil
    | queue.db: ChunkPlan + tareas + context snapshots (transacción local)
    | FSM: PROCESSING (transacciones separadas; recuperación explícita)
    v
 G3: runtime/engine.py (único claim/executor LLM)
    | load_verified(document_id, ast_hash, AST) ANTES de proveedor/claim
    | ThreadPoolExecutor + leases/attempt authority
    | stage_claimed_unit: PRESERVE local / TRANSLATE-PARTIAL -> bridge.execute_chunk
    | provider stack (caché antigua DESHABILITADA en este root)
    | queue.db: receipts/result staged
    v
 runtime/publication_pipeline.py + infra/db/staged_publication.py
    | queue.db -> materialized.db (commit y recuperación diferenciados)
    | FSM: READY_FOR_ASSEMBLY
    v
 G5: apps/compiler/__main__.py
    | CQRSAssemblyContextResolver(AST, proyecciones, perfil, activos)
    | CompilationService -> HostTectonicRunner
    | AssemblyLeaseRepository (fencing; publicación física)
    v
 output/translated_<document_id>.pdf + FSM COMPLETED

 Reconciler / Sweeper: recuperación transversal con semántica G3/G5;
 no despachan un segundo LLM ni reintentan automáticamente UNKNOWN.
```

**Autoridad física, no transacción imaginaria:** `document_id` = SHA-256 de bytes fuente; `ast_hash` representa la generación semántica según `core/ast/hashing.py`; `manifest_sha256`/`plan.digest` identifica plan; `chunk_id` identifica unidad G3; `node_id` miembro de AST/proyección; `execution_id`, lease y versión controlan intentos; `queue.db` gobierna tareas/receipts; `fsm.db` estados; `materialized.db` proyecciones; `documents.db` perfiles/payloads de apoyo; AST y PDF permanecen en filesystem. No afirmar atomicidad entre todos estos planos.

El **producer de la entrada** es la CLI; el **producer de AST/plan** es OCR; el **único ejecutor LLM** es G3; el **único assembler** es G5. Ni CLI ni R1 deben crear otra cola de resultados o otro journal autoritativo.

## 3. Lista blanca de procesos y modalidades

### 3.1 Daemons admitidos en la composición R2

| Rol | Comando declarado (código actual) | Entrada/efecto que debe tener | Condición |
|---|---|---|---|
| Bootstrap (one-shot) | `python infra/db/bootstrap.py` | Esquemas SQLite en volumen descartable; NO ejecutarlo a ciegas sobre estado vivo | Pasa y termina antes de workers |
| OCR Router | `python apps/ocr_router/__main__.py` | `data/inbox` → AST, plan/snapshots, FSM, archive/error | Único consumidor documental |
| G3 LLM worker | `python runtime/engine.py` | Selección de documentos G3, claims, staging/publicación | `IS_BENCHMARK=0`; nunca R3 |
| G5 Assembler | `python apps/compiler/__main__.py` | FSM `READY_FOR_ASSEMBLY` → Tectonic → PDF | Mismo AST, queue y materialized |
| Reconciler | `python apps/daemons/reconciler.py` | Recuperación fenced de leases; distinguir G3 de tareas legacy | Sin retry de efecto incierto |
| Sweeper | `python runtime/sweeper.py` | WAL y FSM; revisar su interacción con cuarentenas | No reabrir UNKNOWN |
| CLI one-shot | `python -m apps.cli.main translate <PDF>` | Copiar por SHA-256 a inbox compartido | No orquestar R1 |

`apps/cli/main.py::handle_translate_async`, `apps/bootstrap/pipeline_factory.py::build_pipeline`, `core/pipeline/orchestrator.py::TranslationPipeline`, `apps/llm_workers/dispatcher.py::AsyncDispatcher` y `apps/llm_workers/__main__.py::LLMWorkerDaemon` **no** son procesos/roots productivos de esta composición. Sus implementaciones se mantienen hasta completar el censo de consumidores. La factoría `pipeline_factory.py` también contiene las funciones de extracción/perfil **sí admitidas**: nunca eliminar el archivo completo.

### 3.2 Dos formas de operar la misma lógica

**Política de soporte durante el cierre:** el camino canónico a acreditar para operación es `translate` (solo admisión) + OCR Router + G3 + G5 como procesos independientes en la composición `docker-compose.yml` **con** `docker-compose.runtime.yml`. `translate --run` es, por ahora, **modalidad de laboratorio/diagnóstico aislada** sobre el mismo contrato y no un segundo root productivo certificado. No ejecutar ambas modalidades sobre la misma generación y las mismas bases mientras esa concurrencia no haya sido probada. Esta restricción de soporte **no deshabilita** el flag ni demuestra exclusión operativa por sí sola.


- **Canónica asíncrona / multiproceso:** `translate` solo admite al inbox; OCR, G3 y G5 corren en sus procesos independientes. Es la **prueba decisiva pendiente** para cerrar la convergencia desplegable.
- **Foreground controlado:** `translate --run` llama `OCRRouterDaemon._process_document`, `runtime.engine.run_pipeline` y `AssemblerWorkerDaemon._process_assembly_task` sobre los mismos contratos, con el preflight de `apps/cli/pdf_product.py`. El laboratorio B03 ya ejercitó esta modalidad con fake HTTP; no reemplaza la prueba entre procesos.

No ejecutar foreground **con daemons activos sobre el mismo documento/generación** durante los testigos: el plan exige aislarlos, no dar por demostrada una coexistencia que no fue ensayada.

## 4. Contrato de workspace, Compose y persistencia: primer delta obligatorio

### 4.1 Configuración que DEBE verificarse (no presuponer)

En `docker-compose.yml` el worker base monta checkout en `/app` y `sqlite_data:/app/infra/db`; el G3 tiene `IS_BENCHMARK: "1"`, lo que **bloquea** `run_pipeline`. El override `docker-compose.runtime.yml` usa `!override` para cambiar cada conjunto de mounts a volúmenes separados (`g3_runtime_state:/app/state`, `g3_runtime_data:/app/data`, `g3_runtime_output:/app/output`), define `SQLITE_STATE_DIR: /app/state/db`, `FSM_DB_PATH`, `QUEUE_DB_PATH`, `EVENT_DB_PATH` y `MAT_DB_PATH` bajo esa raíz, y pasa `IS_BENCHMARK: "0"`. Los perfiles `lab` delimitan `toxiproxy` y `fake-gemini` en el override.

**Contrato soportado a acreditar:** `docker compose -f docker-compose.yml -f docker-compose.runtime.yml config` produce una única composición coherente; no declarar `docker-compose.yml` solo como despliegue válido para G3. Requiere una versión de Compose compatible con las etiquetas `!override`/`!reset`; si no, STOP por prerrequisito. El `docker-compose.golden.yml` parcial no se promueve por el nombre `golden` a topología de producción.

**Rutas a inspeccionar dentro de cada servicio:** `APP_ROOT=/app`; `SQLITE_STATE_DIR=/app/state/db`; `/app/data/inbox`, `/app/data/archive`, `/app/data/error`, `/app/data/ast_cache`; `/app/output`; `/app/state/db/{fsm,queue,event,materialized,documents}.db` (comprobar resolución de `documents.db`, creada perezosamente por los repositorios, no enumerada en `infra/db/bootstrap.py`). Verificar `cwd=/app`, `ASTRegistry()`, `resolve_sqlite_path()`, el usuario y los permisos de volumen. Los archivos AST NO están en SQLite y deben sobrevivir un reinicio igual que los DB.

**Riesgo de entrada comprobable:** `handle_translate` sin `--run` usa por defecto la raíz del checkout que ejecuta la CLI. Una CLI ejecutada en **host** puede escribir en `<checkout>/data/inbox`, mientras Compose usa `g3_runtime_data:/app/data`: **no son necesariamente el mismo inbox**. No declarar handoff hasta demostrar bytes idénticos en ambos lados. Modalidad inicial de laboratorio: CLI one-shot dentro de la misma composición/mounts que OCR (con PDF fuente montado en lectura), o un mecanismo explícito equivalente de ingreso al volumen. No duplicar ingreso ni enlazar una instalación real como atajo.

**Contrato de red del testigo (todavía por implementar):** `apps/llm_workers/adapters.py::GroqProvider` crea `AsyncGroq` sin `base_url` explícita. El laboratorio foreground usa `GROQ_BASE_URL`; antes del test Compose debe probarse la resolución de esa variable por la **versión instalada del SDK**, no presumirla. En contenedores distintos, `127.0.0.1` del G3 **no** apunta al fake: el fake debe escuchar únicamente en una red Docker **interna sin salida externa**, usando sus opt-in `TPDF_OFFLINE_LAB=EXPLICIT_OFFLINE_TEST_ONLY`, `TPDF_FAKE_PRIVATE_DOCKER=EXPLICIT_INTERNAL_NETWORK_ONLY`, `TPDF_FAKE_BIND=0.0.0.0`, `TPDF_FAKE_QUEUE_DB` en la misma `queue.db` aislada y token dummy. `GROQ_API_KEY` del G3 debe coincidir con el dummy; ningún egress real ni puerto publicado hacia host en este test. El contrato de la red/servicio fake **no existe todavía como Compose de prueba validado** y por eso T03 sigue pendiente. El fake deberá contabilizar ≥1 POST de unidad `TRANSLATE`; un PDF sin inferencia no satisface T03. Probar explícitamente conexión/aislamiento antes del smoke; abortar si no es verificable.

**Proveedor controlado:** el servicio G3 necesita `GROQ_API_KEY` y `GROQ_BASE_URL` adecuados para el testigo; la configuración runtime le quita `GEMINI_API_URL` del benchmark, pero **no demuestra** provisión de credenciales ni un fake Groq compatible para Compose. El laboratorio `apps/lab/g3_fake.py` sí ofrece HTTP controlado con token dummy y validación contra `queue.db`; para el testigo Compose, disponerlo en **red privada, sin egress real**, configurado según sus opt-in y sus paths, sin habilitar servicios históricos indiscriminadamente. Credenciales reales solo en un acto posterior explícito; nunca grabarlas en Git ni en evidencia.

### 4.2 Orden seguro de exploración, sin mutaciones

```bash
git rev-parse HEAD
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config --services
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config
rg -n 'handle_translate_async|build_pipeline\(|AsyncDispatcher|LLMWorkerDaemon|TranslationPipeline\(' apps core runtime bootstrap
rg -n 'IS_BENCHMARK|SQLITE_STATE_DIR|APP_ROOT|GROQ_BASE_URL|GROQ_API_KEY|COMPILER_OUTPUT_DIR' docker-compose*.yml apps runtime infra
```

**Atención:** `docker compose config` podría mostrar valores interpolados sensibles en otros entornos: censurar cualquier secreto antes de conservar logs. No ejecutar `up`, `bootstrap`, `run` ni manipular un volumen vivo como parte de esta inspección estática. Revalidar SHA y diffs antes de proponer cambios.

### 4.3 Restricción operativa obligatoria: reutilización de imágenes y presupuesto de almacenamiento (2026-11-09)

**Prioridad absoluta para C0–C4: NO construir ni descargar imágenes/dependencias si el owner ya dispone de una imagen histórica compatible.** Antes de proponer o ejecutar `docker compose build`, `docker build`, `docker pull`, `apt-get`, `pip install` en contenedor o acciones que disparen esas operaciones, el operador/asistente **debe consultar primero** al owner su disponibilidad real de espacio, imágenes existentes y autorización explícita para cualquier descarga o reconstrucción. No se permite presumir disponibilidad de disco. Un `build:` heredado de Compose no habilita ejecutar `build` automáticamente.

**Inventario confirmado en host por el owner (2026-11-09, etiquetas/IDs abreviados, no evidencia de compatibilidad funcional):** `i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824` (`abe5b5dbbc65`, 17.7 GB); `g3-b4-10/translator-pdf-runtime:fbf166b-derived-r0` (`b476a8ceedb6`, 17.7 GB); `i0-1d/translator-pdf-audit:d1-01-01` (`95300da97b59`, 17.6 GB), además de imágenes `translator_pdf-*` de ~810 MB y `fake-gemini` de 225 MB. No eliminar ni recrear estas imágenes a partir de un nombre, tag o tamaño; cotejar ID completo/digest, dependencias, arquitectura y presencia de PyMuPDF/Tectonic. **No sumar tamaños de imágenes como si fueran uso exclusivo**: pueden compartir capas.

**Regla de implementación:** usar la imagen histórica seleccionada por ID/digest verificado con `image:` y `pull_policy: never`; quitar o neutralizar el `build:` heredado **en la composición efectiva del laboratorio**. Ejecutar el código **convergido actual** mediante un montaje explícito del checkout en solo lectura (según la variante B03.2), ajustando `PYTHONPATH`/comandos y separando rutas de escritura: SQLite, inbox, AST, cachés y PDF en volúmenes nuevos por RUN-ID. Verificar en modo de solo lectura que las dependencias instaladas son compatibles con HEAD; un desajuste se registra como `PRECONDITION_BLOCKED` y se propone la opción de menor consumo **antes** de pedir autorización, nunca como build reactivo. Reutilizar cachés históricas **solo** cuando se puedan montar en modo RO sin escrituras ni colisión; no duplicar cachés pesadas por defecto.

**Higiene/custodia del disco:** registrar antes de cualquier operación creadora `docker system df` y el inventario de objetos/espacio recuperable; estimar el incremento y el umbral libre autorizado por el owner. Un `build` interrumpido puede dejar caché BuildKit sin imagen etiquetada. Para recuperar espacio, inspeccionar `docker buildx du --verbose` y borrar **solo registros identificados** con filtro `id` y consentimiento explícito; no usar `docker system prune`, `docker builder prune -a`, `docker image prune -a`, `docker compose down -v`, borrados masivos o `docker volume prune` sobre un host con evidencia histórica. No atribuir automáticamente toda la caché al intento actual. Si no puede determinarse la procedencia de una capa, **preservar y solicitar identificación**, no barrer.

**Incidente de alcance:** se recomendó `docker compose ... build db_bootstrap` antes de consultar el almacenamiento; el owner detuvo esa ejecución después de descargas. **La recomendación fue incorrecta y queda expresamente prohibida sin inventario y autorización.** La inspección estática `C0_T01_STATIC_CANDIDATE_PASS` sí fue reportada por el owner (Compose v2.40.3 / Docker Engine 28.5.1, proyecto `tpdfconvconv0911a`, seis volúmenes y red con nombres libres); no acredita arranque, imagen runtime ni PDF físico.

### 4.4 Permisos de volúmenes Docker y primer bootstrap — observación C0/T01 (2026-11-12)

**Testigo local del owner sobre Draft #46 @ `146868e5aaa257d8aae78f1c3ec1787a16e863a9` (NO implica cierre de T01):** `python -m pytest tests/unit/test_convergence_compose_preflight.py -q` → **11 passed in 0.52s**; `python -m apps.lab.convergence_compose_preflight --run-id conv0911a --verify-local-image` → `C0_T01_STATIC_CANDIDATE_PASS`. Proyecto aislado `tpdfconvconv0911a`, imagen R2 local pinneada (`sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`), sin build/pull. El primer `docker compose ... run --rm --no-deps --pull never -T db_bootstrap` creó una red y seis volúmenes nombrados y falló `PermissionError` en `/app/state/db`: `uid=10001(audit)`, pero los seis volúmenes nuevos tenían raíz `uid=0,gid=0,mode=755`. La configuración `nocopy: true` es intencional para evitar replicación de datos de la imagen; no debe suprimirse para esconder el problema.

**Recuperación acotada comprobada:** el owner ejecutó **una sola vez** en ese proyecto `docker compose ... run --rm --no-deps --pull never -T --user 0:0 db_bootstrap sh -ec 'chown 10001:10001 /app/state /app/data /app/output /app/.cache/hf /app/.cache/torch /app/.cache/tectonic; mkdir -p /app/state/db; chown 10001:10001 /app/state/db'`, **sin `chown -R` ni bootstrap como root**. El bootstrap posterior con el usuario por defecto terminó **exit 0** e inicializó `/app/state/db/{fsm,queue,event,materialized}.db`, leyendo los cuatro SQL desde `/workspace/infra/db/`. El owner verificó después, desde **otro contenedor** y UID 10001, las cuatro SQLite vía URI `mode=ro`: `fsm.db` 1 tabla, `queue.db` 4, `event.db` 1, `materialized.db` 3, todas con `PRAGMA quick_check=ok`; `C0_T01_SQLITE_PERSISTENCE_PASS`, exit 0. **No** hay todavía handoff OCR/G3/G5 ni PDF multiproceso. Documentar una forma repetible y acotada de inicialización de permisos para un RUN-ID fresco sin crear servicio innecesario; evitar reutilización de volúmenes con nombre histórico.

**Cambio implementado y probado en Draft #46, RUN-ID fresco (2026-11-12):** `apps/lab/convergence_db_bootstrap.py` prepara solo las raíces de los seis mounts nombrados con `nocopy` bajo UID 0, comprueba opt-in expreso/mounts/owner y hace `setgroups([])` → `setgid(10001)` → `setuid(10001)` → `execv(..., /workspace/infra/db/bootstrap.py)`. El override del laboratorio limita `user: 0:0` a `db_bootstrap`; OCR/G3/G5 siguen como UID no privilegiado. Ningún cambio en Dockerfile o Compose de producto. **Evidencia del owner sobre `2b70ca1addf7e38c9119b9522be9b99536321b14`:** 18 tests PASS, 1 SKIP por ausencia de permiso para crear symlink en Windows; preflight `C0_T01_STATIC_CANDIDATE_PASS`. En proyecto nuevo `tpdfconvconv1211b`, `docker compose ... run --rm --no-deps --pull never -T db_bootstrap` creó seis volúmenes y red y terminó **exit 0** sin `chown` manual. Una segunda invocación a contenedor con UID 10001 accedió por URI SQLite `mode=ro` a `fsm.db`/`queue.db`/`event.db`/`materialized.db`, `quick_check=ok` y tablas **1/4/1/3**, `C0_T01_FRESH_VOLUME_PERSISTENCE_PASS`, **exit 0**. Estos resultados no demuestran por sí solos handoff CLI→OCR ni la cadena multiproceso. El uso de `docker compose run --rm` crea contenedores efímeros pero no borra volúmenes. No ejecutar `down -v`, prune, rebuild ni ensayos de OCR/G3/G5 con estado legado.

**Testigo de rutas reportado por owner (2026-11-12, sobre el Compose del laboratorio `tpdfconvconv1211b`):** con `ocr_router python -B -` (sin iniciar daemon), `uid=10001`, `cwd=/app`, `CLI_DEFAULT=/workspace/data/inbox`, `OCR_INBOX=/app/data/inbox`, `SHARED_DATA_EXISTS=True`, `SHARED_DATA_WRITABLE=True`, `SAME_INBOX=False`, exit 0. Las advertencias de `fitz`, `google.api_core` y `google.generativeai` son deprecaciones y **no** constituyen el fallo de esta sonda. `apps/cli/main.py::handle_translate` utiliza el checkout de la ubicación del archivo salvo que `--run` defina root; el CLI de admisión admite `--inbox-dir /app/data/inbox` para apuntar al volumen compartido **sin activar foreground**. Esta prueba es lectura/importación de rutas, no envío de PDF, ni recepción del OCR.

**Sonda de estado auxiliar reportada por owner (2026-11-12):** desde `ocr_router python -B -`, ejecutado con usuario UID 10001 y sin arrancar daemon, `APP_ROOT=/app`, `SQLITE_STATE_DIR=/app/state/db`, `resolve_sqlite_path("infra/db/documents.db")=/app/state/db/documents.db`, `DOCUMENTS_DB_CORRECT=True`, `AST_DIR=/app/data/ast_cache`, `AST_PARENT_WRITABLE=True`, `INBOX_PARENT_WRITABLE=True`, exit 0. Esto acredita solo **resolución y permisos de rutas**, no existencia ni esquema de `documents.db` ni persistencia de un AST real. Antes de iniciar el daemon debe probarse la inicialización/esquema efectiva del perfil de documentos, ya que el bootstrap base crea cuatro SQLite, no una quinta demostrada.

**Testigo de admisión C1/T02 — parcial PASS reportado por el owner (2026-11-12):** con la imagen histórica y los volúmenes ya existentes del proyecto `tpdfconvconv1211b`, un contenedor efímero `ocr_router python -B -` (UID 10001, sin levantar daemon) generó en un directorio temporal un PDF sintético mínimo con `pymupdf`, calculó SHA-256 de sus bytes, invocó la **CLI canónica** `python -B -m apps.cli.main translate <ruta-temporal> --inbox-dir /app/data/inbox` **sin `--run`**, y comparó el hash de los bytes publicados. Resultado: `C0_T01_CLI_ADMISSION_PASS`, exit **0**, `document_id=2a21f24dc0741da5c6c6cbb849c48375a224fd065aeaed548be3108d8ebd67f9`, destino `/app/data/inbox/2a21f24dc0741da5c6c6cbb849c48375a224fd065aeaed548be3108d8ebd67f9.pdf`. La CLI reportó `ENVIADO AL INBOX`. No se ejecutaron OCR, G3 o G5; el origen temporal se destruyó tras la prueba y el PDF del inbox **persiste** hasta su tratamiento o retención autorizada. Las advertencias `fitz/google` no invalidaron el resultado, pero serán deuda separada.

**Inspección de perfil documental (fuente de código):** `infra/db/bootstrap.py` inicializa expresamente solo las cuatro SQLite principales; `SQLiteProfileStore.__init__` crea la tabla `inferred_document_profiles` mediante `CREATE TABLE IF NOT EXISTS` sobre `get_connection("infra/db/documents.db")` al crear el OCR composition root. No inventar una quinta base preinicializada ni modificar bootstrap solo por su ausencia: comprobar este side effect y su esquema en una fase controlada cuando se inicie el OCR, con manejo fail-closed si falla.

**Lectura intercontenedor de inbox C1/T02 — parcial PASS (2026-11-12):** el owner abrió un **segundo contenedor temporal** UID `10001` sobre el proyecto `tpdfconvconv1211b` y, sin iniciar el daemon, verificó `PDF_COUNT=1`, `PDF_BYTES=869`, encabezado `%PDF-` y contenido SHA-256 idéntico al nombre `2a21f24dc0741da5c6c6cbb849c48375a224fd065aeaed548be3108d8ebd67f9` en `/app/data/inbox`. Resultado `C1_T02_INBOX_CROSS_CONTAINER_PASS`, exit **0**. Esto acredita el transporte de entrada entre la CLI y otro proceso que monta el mismo volumen; **NO** acredita que el OCR haya interpretado el documento, persistido AST/plan o avanzado la FSM.

**Preflight del parser seleccionado C1/T02 — PASS (2026-11-12):** desde un contenedor temporal UID 10001 sobre `tpdfconvconv1211b`, el owner verificó SHA-256 del PDF publicado y ejecutó `apps.bootstrap.pipeline_factory.build_extraction_pipeline().parse()` sin daemon ni escritura FSM/queue: `PARSER: PdfParserAdapter`, `AST_NODE_COUNT: 1`, `C1_T02_PARSER_PREFLIGHT_PASS`, exit **0**. Aviso `fitz` de deprecación, no fallo. Esta sonda acredita el parser básico **solamente**; no demuestra que el nodo supere `prepare_contextual_plan`, que el OCR archive el archivo ni que existan tareas persistidas.

**Precondición OCR one-shot — PASS (2026-11-12):** el owner ejecutó una sonda de solo lectura en un nuevo contenedor UID 10001 sobre `tpdfconvconv1211b`: PDF existente con SHA-256 coincidente, `fsm.db` y `queue.db` existentes y `SELECT ast_hash,current_state,state_version FROM document_fsm WHERE document_id=?` devolvió `PREEXISTING_FSM_ROWS: 0`. Resultado `C1_T02_OCR_ONE_SHOT_PRECONDITIONS_PASS`, exit **0**. Esto **no** inspeccionó aún filas previas de `queue.db`, ni ejecutó OCR.

**Siguiente falsador C1/T02:** antes de ejecutar por primera vez `OCRRouterDaemon._process_document` sobre el PDF actual, reconfirmar que hay exactamente un PDF en inbox, ningún estado de la generación en FSM ni plan/tareas previos en queue, y que el tokenizer esté disponible localmente (sin build/pull/egress). Ejecutar **una sola** recepción con los componentes reales del composition root y usuario UID 10001, sin iniciar G3/G5; el método captura excepciones y puede mover el archivo a `data/error`, por tanto **un exit 0 solo no demuestra PASS**. Comprobar después en segunda conexión la FSM, el AST, `documents.db`, `queue.db` y el archivo archivado; no resetear volúmenes ni asumir reintento seguro si falla. `C0/T01` y `C1/T02` siguen `EN_CURSO`.

## 5. Deltas implementables, mínimos y secuenciados

### C0 — Fijar root y contrato, antes de editar ejecutores

**Archivos a inspeccionar:** tres Compose, `Dockerfile`, `apps/cli/main.py`, `apps/cli/pdf_product.py`, `apps/cli/pdf_inbox.py`, `infra/db/connection.py`, `infra/db/bootstrap.py`, `core/ast/registry.py`.  
**Acción:** emitir evidencia de configuración efectiva (servicio→command/entrypoint→cwd→volumes→DB/env→consumidor) y el inventario global de arranques por `rg`/tree, según matriz compañera. Identificar consumidores externos como `UNKNOWN` si Git no los prueba. Prohibido concluir que un ejecutor corre solo porque tiene `if __name__ == "__main__"`.  
**Ajuste candidato:** documentar **una sola invocación soportada** de Compose con runtime override. Si el entorno puede usar solo el Compose base, corregir ese root/configuración antes de considerarlo soportado; no ocultar su `IS_BENCHMARK=1`.  
**PASS:** ningún servicio productivo declarativo invoca R1/R3; todas las rutas y bootstrap resuelven el mismo namespace; el contrato de entrada al inbox está definido.  
**STOP:** dos ejecuciones incompatibles sobre la misma `queue.db`, paths divergentes, mounts no compartidos, credencial real en el laboratorio o bootstrap destructivo sobre datos no descartables.

### C1 — Formalizar la entrada compartida y conexión CLI→OCR

**Propietario del cambio:** `apps/cli/main.py` / `apps/cli/pdf_inbox.py` como adaptadores; `OCRRouterDaemon` sigue siendo propietario del parseo y plan.  
**Acción mínima preferida:** **no cambiar código hasta probar** ingreso vía CLI one-shot dentro del mismo workspace de Compose. Para un PDF montado read-only, verificar que la CLI calcula `document_id=sha256(bytes)`, crea `/app/data/inbox/<id>.pdf` y el OCR recibe exactamente ese archivo. Si la necesidad operativa exige CLI host nativa, agregar **un adaptador explícito de transferencia de inbox** o un contrato de mounts, no una segunda ruta de parseo ni una copia opaca a DB.  
**No hacer:** convertir `handle_translate_async` en handler, llamar a `build_pipeline()`, escribir tareas desde CLI o usar `--run` como bypass de daemons para declarar Compose aprobado.  
**PASS:** el documento admitido aparece **una vez** en la misma cola de archivos, OCR lo procesa y deja AST/plan/contexto durable verificables con otra conexión/proceso.  
**STOP:** doble ingesta, root distinto, conflicto de hashes/manifest o error OCR silenciado.

### C2 — Acreditar OCR→G3→publicación→G5 entre procesos

**Conservar sin reescritura:** `build_extraction_pipeline`, `prepare_contextual_plan`, `DurableContextPlanRepository.enqueue_verified/load_verified`, `run_pipeline`, `stage_claimed_unit`, `advance_staged_document`, `AssemblerWorkerDaemon` y `HostTectonicRunner`.  
**Primera prueba física, SIN cambiar código de producto:** PDF sintético compatible y controlado (idealmente el smoke B03), PyMuPDF real, SQLite/AST reales descartables, fake HTTP G3 de protocolo válido, Tectonic real. Primero, si están disponibles sus artefactos fijados, reproducir `python -m apps.lab.offline_pdf_lab --preflight` y `--run-smoke` **para constatar el baseline foreground**. Luego configurar la prueba **multiproceso**, que B03 no acreditó. Si falta imagen o ZIP históricos, marcar `PRECONDITION_BLOCKED` y usar otro contenedor de prueba separado/pinneado, sin inventar PASS.  
**Orden:** bootstrap en volumen nuevo → iniciar OCR/G3/G5 y recuperadores compatibles → CLI one-shot solo-admisión → esperar resultado limitado por plazo del test (no polling infinito) → detener daemons → inspeccionar copias/snapshots descartables. El fake debe comprobar identidad de `document_id/ast_hash/manifest/chunk_id`; idealmente registrar solo hashes y conteos.  
**Fixture mínimo no trivial:** PDF sintético representable por PyMuPDF, con texto que produzca al menos una unidad `TRANSLATE` y un elemento `PRESERVE` cubierto por el productor actual; fixture y clasificación se inspeccionan antes del test. El fake HTTP debe recibir ≥1 solicitud de `TRANSLATE` y **cero** solicitudes por unidades `PRESERVE`, con conteo y binding de cada chunk. No basta generar un PDF ni `COMPLETED` si el fake nunca fue invocado. No introducir primitivas vectoriales todavía no representadas para obtener un PASS artificial; B02 conserva STOP.

**Oráculos de operación:** mismo `document_id`/generación; AST no vacío y `compute_ast_hash` consistente; plan + snapshots y cardinalidad de miembros; task states y receipts válidos; proyecciones por `node_id` y versión; `READY_FOR_ASSEMBLY` posterior a publicación; G5 compila de verdad, publica PDF con cabecera y lectura estructural mediante PyMuPDF, `FSM COMPLETED`. La salida **no** tiene por qué ser una traducción real porque el proveedor es controlado.  
**STOP:** `B02_UNREPRESENTED_*` explícito (testigo de cobertura no apto, NO modificar el guard), G3 lee otra SQLite, `W08_G3_UNVERIFIED_CONTEXT_BEFORE_PROVIDER`, `PDF_RUN_COMPLETED_WITHOUT_PUBLISHED_PDF`, missing receipt/proyección, doble publicación adversa o proveedor externo accidental.

### C3 — Recuperación y dos modalidades sin duplicar autoridad

**Sujetos focales, en datos aislados:** crash antes de que OCR termine de encolar; OCR tras AST file pero antes de persistir queue/FSM; reinicio G3 antes de egress, después de resultado staged, con `G3_EXTERNAL_UNKNOWN`; fallo G5 entre archivo privado, `os.replace()` y commit SQLite. Recorrer solo escenarios para los que existan testigos y un mecanismo autorizado, no crear una migración como requisito universal.  
**Módulos vigentes:** `apps/daemons/reconciler.py`, `runtime/sweeper.py`, `infra/db/control_repo.py`, `infra/db/assembly_recovery.py`, `runtime/publication_pipeline.py`, `runtime/resumer.py`.  
**Reglas irreductibles:** `UNKNOWN` no se reintenta sin disposición autorizada; un `PENDING` histórico no prueba no-inicio remoto; stale owner no publica; `RESULT_STAGED` con receipts válidos no repite LLM; `PRESERVE` nunca llama LLM; no falsificar atomicidad DB↔FS. Las recuperaciones de R1 para tareas legacy **no** autorizan recuperar una tarea G3 con otro protocolo.  
**Test de modalidad:** ejecutar foreground en otra workspace/generación aislada y demostrar el mismo contrato de documentos/planes/proyecciones/salida; no ejecutar daemons simultáneamente sobre esa generación hasta acreditar explícitamente la coordinación.  
**PASS:** recuperación segura o STOP explícito clasificable, con evidencia persistida reabierta desde proceso nuevo. No se exige que todo fallo se recupere automáticamente; sí que no corrompa o reintente incierto.

### C4 — Sellar la superficie productiva; disposición final de ejecutores

**Cambio de código solo si la búsqueda lo demanda:** aislar o eliminar import/call de `build_pipeline` **de los entrypoints productivos**, no de todos los tests; mantener `build_extraction_pipeline` y `build_document_profiler` en `apps/bootstrap/pipeline_factory.py` o separarlos solo si hay beneficio verificable. Identificar y bloquear cualquier proceso productivo invocando `apps/llm_workers/__main__.py` o `core/pipeline/orchestrator.py`. Confirmar que `SyncProviderBridge.execute(node)` legacy no es camino alternativo de `run_pipeline`; conservar `execute_chunk`.  
**Conservar como librerías o histórico:** R1 validación/healing, rutas de test; R3 admission/backpressure/shutdown/visibility, hasta medir garantía faltante en el modelo concurrente de G3. No injertar clases secuenciales R3 tal cual. No hacer `RETIRE` físico hasta confirmar consumidores, compatibilidad, tests y autorización puntual.  
**PASS:** único grafo de ejecución productivo verificable; los módulos alternativos pueden permanecer en el árbol sin ser activables por los entrypoints soportados. Documentar los consumidores `UNKNOWN` sin declararlos inexistentes.

## 6. Testigos mínimos de cierre (y falsadores)

| Testigo del plan | Sujeto real y herramientas existentes | Prueba positiva | Negativa / STOP | Alcance |
|---|---|---|---|---|
| T01 root/config | Compose base+runtime, `docker compose config` | G3 seleccionado, `IS_BENCHMARK=0`, DB/mounts coherentes | base sin override da G3 benchmark; ruta CLI host no compartida | Inspección; no operación |
| T02 CLI→OCR | CLI admission y `OCRRouterDaemon` en procesos diferentes | mismo SHA, un inbox/AST/plan/snapshots | drift, duplicación, error antes de FSM | Handoff real |
| T03 G3 controlado | Engine, provider fake privado, SQLite fresco | contexto validado, receipts/staging/publicación correctos | contexto inválido no llama provider; `PRESERVE` no egress | W08 / G3 focal |
| T04 G5 físico | G5 y Tectonic real | proyecciones+AST+PDF físico+FSM correlacionados | proyección faltante o lease obsoleto no publica | W10 operativo, NO ciencia |
| T05 reinicio/authority | Reconciler/Sweeper/G3/G5 | staged→publicado sin nuevo POST, fenced rollback | timeout incierto nunca retry; stale owner nunca publica | W06/W07 mínimos |
| T06 superficie única | entrypoints/Compose/CLI con import graph | cero arranques productivos de R1/R3 | referencia activa a ejecutor legacy con escritura | Exclusividad |
| T07 compatibilidad foreground | `apps.lab.offline_pdf_lab` o fixture equivalente | contratos iguales en generación **aislada** | discrepancias de plan/DB/PDF | No sustituye T02–T05 |

**Evidencia por testigo:** commit, `docker compose version`, digest de imagen, configuración efectiva saneada, comandos, hashes fuente/artefactos, paths de mounts sin credenciales, estados de FSM/queue/materialized, cantidad de requests del fake, tiempos/exit code, logs de STOP, documento/manifest/test IDs. Evidencia de CI antigua no se reetiqueta como ejecución sobre HEAD.

**Conexión con Atlas:** usar W06 (efecto incierto), W07 (fencing), W08 (identidad/replay), W09 (PRESERVE científico) y W10 (artefacto) **sin cambiar sus oráculos**. T01–T07 son **checklist de esta ejecución**, NO gates normativos nuevos, ni sustituyen preregistro/certificación científica. Para el cierre estrictamente operativo, W09 queda pendiente salvo el bypass local que ya obliga `PRESERVE`; no declarar fidelidad científica por esa prueba.

## 7. Riesgos, decisiones acotadas y tratamiento de Draft #41–#44

| Riesgo | Política mientras se converge | Condición que abriría trabajo mínimo |
|---|---|---|
| Estado legacy fuera del repo | Probar primero con **volúmenes nuevos y descartables**; no inferir ausencia de datos externos ni usar bootstrap sobre producción. Inventariar **solo antes de un cutover real**. | Si existe obligación de preservar generaciones antiguas, evaluar #41 aislado; si escritor incompatible puede reabrir la misma DB por reinicio/downgrade, evaluar barrera #42. |
| #43 HMAC | No fusionar por inercia. Prueba firma de aprobación para activación, no IAM real. | Solo si existe activación de fence #42 autorizada y necesidad de ceremonia de operador. |
| #44 auditor offline | Puede ser independiente de #41–#43; no arrastrar la pila Git. | Si hay bundle real para auditar, adaptar **su delta propio** y verificar integridad/read-only del snapshot consistente. |
| #45 | Cerrado sin merge; su cache barrier ya fue reimplantado en #40. | No revivir. |
| Cache/replay | G3 conserva `cache_db_path=None`; no reutilización insegura. | W08-3 posterior y separada, issue #36; no habilitar cache por configuración accidental. |
| Vector/PDF científico | Mantener B02 fail-closed. Usar smoke compatible para acreditar la ruta, no corpus científico bloqueado como falso fallo de cableado. | H04/W09 después del cierre de ruta única, con investigación fuente→Layout→AST→PRESERVE→G5. |
| Capacidad R3 | No desplegar daemon alternativo. | Medición F18-02 muestra brecha en admisión/pool/shutdown de G3; adaptar solo contrato faltante. |
| Validación/healing R1 | No alterar el protocolo G3 ni repetir llamadas inciertas. | Test positivo y negativo muestra necesidad de adaptar validadores por miembro post-respuesta bajo la misma authority. |
| PDF final / estado | `FSM COMPLETED` + cabecera PDF **no** prueba equivalencia científica. | W09/aceptación posterior usa corpus y oráculos existentes. |

La instalación ya aprobada del código #40 **no** es autorización automática de un rollout sobre SQLite legacy. La política documental `working-observations/W08_2C_TRANSICION_GENERACIONES_LEGACY_20261107.md` identifica ese problema; no lo convierte en requisito para probar un entorno limpio.

## 8. Secuencia de trabajo y Definition of Done de CONVERGENCIA, no de producto

**Orden de ejecución obligatorio por dependencia, no por la urgencia de otros backlogs:**
1. **C0 / T01 + censo de consumidores:** fijar configuración/entradas/volúmenes. No añadir un nuevo engine.
2. **C1 / T02:** ingreso real CLI→OCR con un mismo workspace.
3. **C2 / T03 + T04:** un PDF compatible atraviesa *daemons independientes* y Tectonic real.
4. **C3 / T05 + T07:** recuperaciones y equivalencia de modalidades sin competencia.
5. **C4 / T06:** sellar arranques y documentar `KEEP/ADAPT/NO_PRODUCTIVO/RETIRE_CANDIDATE` por consumidor real. Cambios pequeños y separados solo si los falsadores lo piden.

**Definition of Done — etiqueta interna `CONVERGENCIA_OPERATIVA_ACREDITADA`:**
- [ ] CLI única entrega PDF al inbox realmente compartido, identidad por bytes reproducida.
- [ ] OCR único construye AST, perfil y manifest/snapshots verificables.
- [ ] Un solo G3 consume y publica con identidad/receipt/fencing; cache antigua deshabilitada.
- [ ] Un solo G5 usa proyecciones y activos de la generación y publica PDF real.
- [ ] Testigo multiproceso en volúmenes nuevos, con parser/Tectonic reales y proveedor controlado.
- [ ] Reinicios/STOP focales no producen egress repetido incierto, stale writes ni falsa publicación.
- [ ] Compose efectivo y entrypoints no seleccionan ejecutores productivos R1/R3.
- [ ] Logs/artefactos pinneados y matriz actualizada con `AS-IS verificado` vs `TO-BE implementado`.
- [ ] No se alteraron oráculos STEM ni contratos FROZEN, ni se hizo despliegue/cutover silencioso.

**Resultado que NO se obtiene con este DoD:** `PRODUCT_READINESS=PASS`, traducción lingüística evaluada, equivalencia matemática W09, soporte de todos los PDFs, costos/proveedor real acreditados, política universal de rollback, eliminación total de código legacy, o aprobación de actividades fuera de D-1/D-2.

Si no puede cumplirse algún ítem: registrar **bloqueo específico y falsador** (`PATH_MISMATCH`, `UNSUPPORTED_COMPOSE`, `PRECONDITION_MISSING`, `CONTRACT_DRIFT`, `B02_FAIL_CLOSED`, `UNKNOWN_EFFECT`, etc.), no sumar infraestructura preventiva sin causalidad.

## 8.1 Seguimiento versionado del avance (obligatorio y mínimo)

Este documento es el **único tablero de avance de la convergencia operativa**. La matriz compañera identifica responsabilidades y disposiciones por archivo; **no** se exige editar sus 94 filas cada vez que se ejecuta una prueba. Los estados de aquí no son gates normativos nuevos ni sustituyen los oráculos FROZEN.

**Estados permitidos:** `PENDIENTE` (sin evidencia de cierre en el HEAD), `EN_CURSO` (se trabaja en ese delta, sin cierre), `BLOQUEADO` (impedimento reproducible con causa/evidencia), `COMPLETADO` (criterios PASS cubiertos y evidencia verificable) y `NO_APLICA` (solo para una prueba opcional, con justificación y sin eludir un invariante obligatorio). Un FAIL o PRECONDITION_BLOCKED **nunca** es `COMPLETADO`. No se deduce `COMPLETADO` de un documento, PR abierto, CI histórica, salida PDF fake ni ausencia de errores visibles.

**Registro de deltas — actualizado 2026-11-12 (PR #46, runtime @ `93a8f9021cbb95c92c9242d68fd6f1dfe9eb3d0f`, test adicional @ `21eb7da8baf1ac86a288916e112f9e67ca652494`):** **C0/T01, C1/T02 y C2/T03–T04 `COMPLETADO`**. C0 ratificado por el owner y respaldado por preflight Compose, bootstrap fresco UID10001, SQLite persistente, rutas, dependencia fake/worker y testigo multiproceso; el inventario de todos los consumidores y ejecutores R1/R3 es **C4/T06**, no precondición adicional de C0. C2 cerrado por cadena automática y falsadores negativos, con PDF Tectonic real y HTTP fake independiente. **T05 `COMPLETADO` por recuperación segura y falsadores W06/W07; C3 `EN_CURSO` hasta T07 foreground aislado, y C4/T06 `PENDIENTE`**; no se declara convergencia global ni readiness científica/productiva.

| Delta | Estado | Pruebas para cerrarlo | Evidencia PASS / bloqueo | Última revisión |
|---|---|---|---|---|
| C0 — Root/configuración | COMPLETADO | T01; Compose/root/imagen/bootstrap/DB/mounts/entrada efectivos | [Acta de corrección y ratificación](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6838189437): `C0_T01_STATIC_CANDIDATE_PASS` y tests del preflight; `C0_T01_FRESH_VOLUME_PERSISTENCE_PASS` (bootstrap UID10001, volúmenes `nocopy`, SQLite RO `quick_check=ok`); `C2_DAEMON_START_GUARD_PASS` y `C2_DAEMONS_RUNNING_SET_PASS`; `/workspace:ro`, working dir `/app`, `/app/state/db`, inbox `/app/data/inbox`, output `/app/output`, `chaos_net internal:true`, sin builds/pulls/puertos, imagen local `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`, `IS_BENCHMARK=0`, fake Groq privado, CLI compartida. Censo integral de ejecutores externos pertenece a C4/T06; no inventar ausencia de consumidores fuera de Git | 2026-11-12 |
| C1 — Entrada CLI→OCR | COMPLETADO | T02; inbox compartido, una generación | [Acta PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46): CLI `translate --inbox-dir /app/data/inbox` sin `--run` admitió SHA-256 `50a7305f…084ef9`; OCR one-shot en otro contenedor: 4 nodos AST, 2 tareas, 1 plan/snapshot, FSM `PROCESSING` v2, archive hash igual; `C2_T03_FRESH_OCR_ONE_SHOT_PASS` y `C2_T03_MIXED_PLAN_CROSS_CONTAINER_PASS`, exit 0 | 2026-11-12 |
| C2 — OCR→G3→G5 multiproceso | COMPLETADO | T03 + T04: positivo automático y negativos de contexto/lease/proyección | [Acta de cierre PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200) @ runtime `93a8f902` / tests `21eb7da8`: CLI única→OCR/G3/G5 daemons, FSM `COMPLETED` v7, 2 receipts, 1 publicación, 4 proyecciones, PDF Tectonic real 7050 bytes/1 pág. SHA-256 `71f209255c923daef84e44e1ae1bf642dfe5270e862eadedb0709b94ee62bfe3`; fake HTTP 1 intento/1 aceptado TRANSLATE/0 rechazado/0 PRESERVE; negativos W08/G5 19 PASS, test G5 de proyección ausente 14 PASS, ambos exit 0. Incertidumbre histórica preservada | 2026-11-12 |
| C3 — Recuperación/modalidades | EN_CURSO | T05 completo; T07 foreground aislado pendiente | [Acta T05](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840272805): recuperación G3 entre procesos @ `c146f0e`, 1 PASS/exit 0; W06 quarantine/UNKNOWN/reconciler y G5 fencing/rollback cubiertos por baterías focales previas, sin Docker nuevo; falta T07 | 2026-11-12 |
| C4 — Exclusividad productiva | PENDIENTE | T06; inventario de entrypoints/consumidores | — | 2026-11-09 |

**Registro de testigos — corte 2026-11-12:** **T02, T03 y T04 `COMPLETADO`** con ejecución automática real, persistencia y HTTP independientes, y negativos focales en código vigente. T01 tiene cierre propio de root/configuración; T05 se cierra por sus testigos de recuperación y STOP, mientras T07 sigue pendiente. El testigo anterior one-shot es antecedente, no sustituto.

| Testigo | Estado | Evidencia verificable o bloqueo |
|---|---|---|
| T01 — Root/config | COMPLETADO | [Acta C0](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6838189437): preflight Compose efectivo PASS, override de laboratorio fija imagen sin build/pull, root `/app` con código `/workspace:ro`, estado/AST/inbox/output compartidos, SQLite en volumen `/app/state/db`, bootstrap UID10001 con `nocopy`, Groq dummy y `IS_BENCHMARK=0`, `g3_fake` saludable sin puertos en red interna. Tres entrypoints OCR/G3/G5 reales arrancaron en conjunto y completaron PDF físico en este mismo proyecto. El inventario global de consumidores R1/R3 permanece como C4/T06 |
| T02 — CLI→OCR | COMPLETADO | Fixture mixto `50a7305f…084ef9` admitido por CLI; OCR one-shot en distinto contenedor persistió AST 4, plan 2 (`preserve`/`translate`), snapshot 1, perfil y FSM `PROCESSING` v2; lectura independiente de identidades/tareas `PENDING` y archivo archivado por SHA; exit 0 |
| T03 — G3 fake HTTP | COMPLETADO | [Acta de cierre](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200): generación SHA-256 `28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f`, AST SHA `b0b4cb12ea5e2a871a8789e5228e428b10eca04380e5a95503ff4f61c89f9c4a`, manifest SHA `7724718fd66aff7b570f70a1dad828b2d3391abd14c47ef32fd12fb4a487229d`; fake HTTP 1 POST total, 1 aceptación 200 para `chunk_0002_2_4_fdbea9ce` TRANSLATE, 0 intentos PRESERVE y 0 rechazos; 2 receipts (PRESERVE nulo), 1 publicación G3, 4 proyecciones. Negativos `test_w08_missing_context_fails_before_fake_provider` y `test_w08_context_from_other_generation_fails_before_fake` (provider.calls=0); batería W08 + G5 19 PASS exit 0 @ runtime `93a8f902` |
| T04 — G5 + Tectonic | COMPLETADO | [Acta de cierre](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200): G5 daemon independiente publicó PDF `%PDF-` de 7050 bytes, 1 página PyMuPDF/texto extraíble, SHA-256 `71f209255c923daef84e44e1ae1bf642dfe5270e862eadedb0709b94ee62bfe3`; FSM `COMPLETED` v7, 1 ASSEMBLER `COMPLETED`, 2 receipts y 4 proyecciones verificadas RO. Negativos `test_expired_lease_old_worker_cannot_publish_even_without_takeover` y fencing/rollback; `test_missing_projection_blocks_real_g5_worker_before_pdf` ejercita método G5 real sobre SQLite temporales, exige fallo autorizado sin Tectonic ni PDF. Tests focales 19 PASS + 14 PASS, ambos exit 0 @ `21eb7da8` |
| T05 — Reinicio/authority | COMPLETADO | [Acta T05](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840272805): `test_c3_t05_process_boundary.py` @ `c146f0e` 1 PASS/1,66 s/exit 0 (SQLite reabierta desde proceso independiente; staged→publicado/ready sin proveedor ni duplicación); W06 `G3_EXTERNAL_UNKNOWN` sin retry y reconciler con lease expirado/quarantine (batería 34 PASS/exit 0); G5 fenced lease, stale-owner, crash de promoción física y recuperación (19 PASS + 14 PASS/exit 0). Alcance mínimo §6: no reinicio exhaustivo de todos los daemons ni de OCR |
| T06 — Superficie única | PENDIENTE | — |
| T07 — Foreground aislado | PENDIENTE | B03 histórico es antecedente, no PASS de este HEAD |

**Reglas de actualización al terminar o bloquear algo:**

1. En el mismo cambio que entrega la prueba (o inmediatamente después de ejecutar el testigo sin cambiar código), editar **solo** la fila del delta y del testigo afectado: estado, fecha, resultado y enlace a evidencia. `EN_CURSO` puede llevar PR/commit de implementación, pero no un PASS anticipado.
2. Para pasar a `COMPLETADO` registrar **commit exacto** del producto probado, comando y Compose efectivo, versión/digest de imagen cuando aplique, fixture SHA-256, resultados/exit codes, enlace al run/log o acta de ejecución y verificaciones de identidad/FSM/receipts/PDF. No almacenar secretos, textos de papers privados, prompts ni datos sensibles en el documento. Cuando la evidencia sea local/privada, dejar referencia auditable sin volcarla a Git.
3. Para `BLOQUEADO`, registrar **fallo causal concreto**, dónde ocurrió, sujeto SHA, cómo reproducirlo sin efectos reales y qué evidencia demostraría que se resolvió. `NO_APLICA` requiere explicar por qué no compromete el DoD y no es aceptable para C0–C4 ni para los testigos obligatorios sin revisión explícita del contrato.
4. El delta pasa a `COMPLETADO` **solo** si todos sus testigos obligatorios están `COMPLETADO` y su criterio PASS se verificó sobre la misma composición y generación cuando corresponda. El cierre global `CONVERGENCIA_OPERATIVA_ACREDITADA` requiere C0–C4 en `COMPLETADO` más las casillas del DoD §8 satisfechas. Un documento marcado completo sin evidencia es un defecto del registro.
5. Cuando cambie un consumidor real, root o contrato, actualizar **solo las filas pertinentes** de la matriz (disposición y evidencia), citando el mismo SHA/testigo; nunca convertir `KEEP` automáticamente en PASS ni `NO_PRODUCTIVO` en permiso de borrado. Mantener sincronizadas ambas versiones.
6. Versionar v1.0.x para correcciones y avances que no alteran el alcance/criterios; v1.x para cambios justificados de alcance, disposición o criterio. Cada actualización debe incorporar una entrada breve en el historial inferior. No crear tableros paralelos.

**Historial del seguimiento:**

| Fecha | Versión | Cambio | Evidencia |
|---|---|---|---|
| 2026-11-09 | v1.0.0 | Primera especificación y matriz, sin prueba operativa nueva | `adbb61a88c179d3a11a31e78cd470b590024a4be` |
| 2026-11-09 | v1.0.1 | Convención de avance, registros iniciales, root canónico, requisitos del fake/fixture y Markdown corregido | Este commit documental; no ejecución nueva |
| 2026-11-09 | v1.0.2 | C0/T01 pasa a EN_CURSO; preparación del override y validación estática en Draft #46 | [PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46); no existe PASS de Compose ni del PDF multiproceso |

| 2026-11-09 | v1.0.3 | Restricción obligatoria de reutilizar imágenes históricas, ahorrar disco, pedir autorización antes de build/pull y limpieza selectiva de BuildKit; se registra C0 estático PASS (no cierre) | Inventario Docker y preflight enviados por el owner; Draft #46; no se ejecutaron contenedores nuevos en ese corte |
| 2026-11-12 | v1.0.4 | Evidencia local C0/T01: 11 tests PASS, preflight con digest PASS y bootstrap real de cuatro bases exit 0 tras resolver uid 10001 en volúmenes vacíos; mantiene EN_CURSO | PR #46 @ `146868e5`; acta del owner en conversación; pendiente testigo independiente/persistencia |
| 2026-11-12 | v1.0.5 | Evidencia de SQLite en otro contenedor (4 quick_check OK, tablas 1/4/1/3, exit 0) y candidato de inicialización efímera de permisos solo para C0/T01; sin atribuirle PASS de runtime aún | Conversación owner; Draft #46; wrapper pendiente de validación local en RUN-ID fresco |
| 2026-11-12 | v1.0.6 | Primer bootstrap automático en RUN-ID nuevo y lectura persistente entre contenedores PASS; no se infiere handoff PDF→PDF; siguientes pruebas: root/inbox compartido y consumidores | Owner sobre PR #46 @ `2b70ca1`; 18 PASS/1 SKIP y preflight PASS, proyecto `tpdfconvconv1211b` |
| 2026-11-12 | v1.0.7 | Sonda de rutas `UID10001` confirma inbox CLI por defecto diferente del OCR; CLI admite `--inbox-dir` explícito; queda abierta ubicación real de `documents.db`/AST antes de emitir testigo T02 | Salida local owner `SAME_INBOX=False`, exit 0; lectura de `apps/cli/main.py`, `apps/ocr_router/__main__.py` |
| 2026-11-12 | v1.0.8 | Sonda sin escrituras acredita resolución de documents.db en volumen estado y rutas AST/inbox escribibles; siguiente paso admisión PDF sintético sin daemons | Salida local owner `DOCUMENTS_DB_CORRECT=True`, `AST_PARENT_WRITABLE=True`, `INBOX_PARENT_WRITABLE=True`, exit 0 |
| 2026-11-12 | v1.0.9 | CLI one-shot sin `--run` publicó PDF sintético en inbox con SHA-256 verificado; C1/T02 pasa a EN_CURSO, sin inferir consumo OCR; esquema de perfil es lazy en SQLiteProfileStore | Salida local owner `C0_T01_CLI_ADMISSION_PASS` exit 0, `document_id=2a21f24d…d67f9` y revisión de código `infra/db/profile_store.py` |
| 2026-11-12 | v1.0.10 | Segundo contenedor UID10001 confirma un PDF sintético de 869 bytes con hash/header correcto; handoff de volumen probado, aún no OCR real | Salida local owner `C1_T02_INBOX_CROSS_CONTAINER_PASS`, exit 0; proyecto `tpdfconvconv1211b` |
| 2026-11-12 | v1.0.11 | Preflight del parser real sobre el PDF admitido: 1 nodo AST, exit 0; siguiente paso OCR one-shot y verificaciones independientes, sin G3/G5 | Salida local owner `C1_T02_PARSER_PREFLIGHT_PASS`; `PdfParserAdapter`, `AST_NODE_COUNT=1` |
| 2026-11-12 | v1.0.12 | Sonda read-only confirma PDF con hash válido, fsm/queue presentes y 0 filas FSM previas para la generación; autorización operativa de una única ingesta OCR con falsadores explícitos, sin atribuir PASS anticipado | Salida local owner `C1_T02_OCR_ONE_SHOT_PRECONDITIONS_PASS`, `PREEXISTING_FSM_ROWS: 0`, exit 0 |
| 2026-11-12 | v1.0.13 | Testigo CLI→OCR→G3(fake)→publicación→G5/Tectonic con verificación intercontenedor del PDF final; T02 `COMPLETADO`, T03/T04/C2 `EN_CURSO` por falsadores/contador HTTP pendientes. Incidente del doble prefijo Groq corregido; generación `G3_EXTERNAL_UNKNOWN` previa preservada sin reintento. No hubo despliegue productivo ni cierre del DoD | [PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46) @ `eb264aa531c7495887864ee5034404fab1c90f8e`; owner: `C2_T03_FRESH_OCR_ONE_SHOT_PASS`, `C2_T03_MIXED_PLAN_CROSS_CONTAINER_PASS`, `C2_T03_G3_DURABLE_CROSS_CONTAINER_PASS`, `C2_T03_G5_ONE_SHOT_PUBLISH_PASS`, `C2_T03_PDF_TO_PDF_CROSS_CONTAINER_PASS` (exit 0); PDF SHA-256 `cdaad9f…1c9fb` |

| 2026-11-12 | v1.0.14 | Primera ejecución totalmente automática CLI→OCR daemon→G3 daemon→G5 daemon con fake HTTP observado por POST y auditoría RO intercontenedor; C2/T03/T04 siguen `EN_CURSO` hasta ejecutar negativos focales actuales; selector `G3_EXTERNAL_UNKNOWN` corregido y probado | [Acta automática PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837649853) @ `93a8f902`; fuente SHA-256 `28a53af…158d0f`, PDF SHA-256 `71f20925…2bfe3`, HTTP 1/1/0, FSM v7 |

| 2026-11-12 | v1.0.15 | **C2/T03 y T04 COMPLETADO**: testigo automático PDF→PDF con auditoría intercontenedor y fake HTTP 1/1/0; negativos W08 y G5 de lease/ausencia de proyección verificados (19 PASS + 14 PASS). C0/T01 y C3/C4 continúan abiertos; PR Draft sin certificación | [Acta de cierre PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200); runtime `93a8f902`, test `21eb7da8`; PDF SHA-256 `71f20925…2bfe3` |

| 2026-11-12 | v1.0.16 | Corregida clasificación: **C0/T01 COMPLETADO** (ratificación owner y evidencias previas de root/Compose/bootstrap y arranque); el censo integral de consumidores pertenece a **C4/T06**. C1/C2 también completos; C3/C4 abiertos, PR Draft | [Acta C0](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6838189437); [C2 cerrado](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200) |

| 2026-11-12 | v1.0.17 | **T05 COMPLETADO**: testigo G3 en subprocess distintos y SQLite temporal 1 PASS/exit 0; W06 UNKNOWN/reconciler y G5 fencing/rollback reutilizados sin repetir pruebas ni tocar Docker. C3 EN_CURSO hasta T07; C4 pendiente, Draft | [Acta T05](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840272805); `c146f0e` |

## 9. Registro de cambios propuestos y disciplina de integración

Este documento y la matriz son **documentación exclusivamente**. No suponen cambios funcionales, despliegue, restauración de volúmenes, cierre de PRs ni borrado de rutas.

Cuando se implementen:
- Usar la base vigente de `pipeline_stabilization` y un delta por frontera; no arrastrar históricamente las ramas stacked #41–#44.
- Archivo modificado → motivo/falsador → consumidor exacto → test positivo/negativo → reversión segura. Priorizar `docker-compose.runtime.yml`/invocación CLI compartida antes de nuevas clases.
- Conservar builds, hashes de tests y STOPs; no cambiar el sentido de un FAIL conocido B02 ni adjudicar a esta integración el gate CV externo.
- Antes de retirar código R1/R3: `rg` global, import graph, dependencias de CLI/packaging (`pyproject.toml`), Compose, tests, consumidores fuera del repositorio **si se conocen**. Si estos últimos no pueden probarse, mantener `RETIRE_CANDIDATE`, no borrar.
- Para un deploy real, además de este cierre de laboratorio: inventario del estado instalado, operator/cutover/rollback autorizado y verificación de ausencia de escritores incompatibles. Este acto es distinto y **no bloquea** acreditar la composición nueva en un entorno desechable.

## 10. Fuentes y trazabilidad

- [Decisión D-1/D-2 vigente](DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md), en especial §§0, 2, 6, 7 y 8; su texto histórico no es voto posterior.
- [Matriz §7 B01–B03 (histórica)](working-observations/B01_B03_RECONCILIACION_MATRIZ_DELTA_MINIMO_SECCION7_20261106.md). Su diagnóstico de contexto y W06 de 2026-11-06 **precede** a #31/#38/#39/#40: se actualiza según HEAD, no se copia como estado vigente.
- [B03 observación offline (histórica)](working-observations/B03_20261106_CONVERGENCIA_FUNCIONAL_OFFLINE_NO_CIERRE_GOBIERNO.md); [política transición legacy, propuesta](working-observations/W08_2C_TRANSICION_GENERACIONES_LEGACY_20261107.md).
- [Atlas](PRODUCTION_PIPELINE_EXECUTION_ATLAS.md) y [Charter](PIPELINE_STABILIZATION_AUDIT_CHARTER.md) como fuentes de contratos/testigos históricos; NADR F18 aplicables permanecen FROZEN.
- [#40 integrado](https://github.com/RDsanchez-git/translator_pdf/pull/40), [#36 W08](https://github.com/RDsanchez-git/translator_pdf/issues/36), ramas Draft #41–#44 (no integradas).
- Fuentes de producto suministradas por el owner: `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md` (fuera del checkout). Prohíben pérdida silenciosa, duplicación de autoridad y sobreingeniería.
- Inspección estática de código y Compose en `6a5ee41886b935c2c0f3a107a42620d93de31efb`; **no** se ejecutaron Docker ni testigos dinámicos al redactar este plan.

**Actualización de versión:** incrementar v1.0.x para correcciones documentales sin cambio de alcance; v1.x si cambia una disposición o contrato operativo; nunca convertir un `TO-BE` no probado en `AS-IS PASS` sin commit, testigo y evidencia.