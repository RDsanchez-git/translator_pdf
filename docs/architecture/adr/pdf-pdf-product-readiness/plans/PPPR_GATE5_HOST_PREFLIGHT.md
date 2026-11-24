# PPPR Gate 5 — Preflight de host y modalidad soportada

**Estado:** LIVING / no normativo; W5.1 COMPLETED/PASS (5.1.1 y 5.1.2 DONE), H-G5-01 RESUELTO / BOARD_ACCEPTED, ratificación comunicada por owner el 2026-11-24 sobre HEAD `5d336fdc86868c4172deb658a8ab9b0c9da5368d`, CI #45326107574 SUCCESS. G5 IN_PROGRESS; W5.2 NOT_RUN hasta CI del HEAD documental. No sustituye criterios del Execution Plan.

**Base:** `7ff8b84733a63efd3012adf14070db86cff051ad`, rama `pdf-pdf-product-readiness`. CI post-merge #45314286191 SUCCESS (3/3 jobs); CV #45314286115 FAIL/DEFERRED, BASELINE_INTEGRITY_FAILURE (15 PDF privados ausentes). G1–G4 COMPLETED/PASS en esta base histórica (20/30 DONE entonces); estado vigente 22/30 Tasks DONE (73,3%), G5 IN_PROGRESS, 14 GAP P1 OPEN, PRODUCT_READINESS=NOT_CERTIFIED.

## 1. Autoridad y frontera

- ADR Maestro DC-08: CLI dentro del contenedor de un nodo, D-1/D-2; no puente Windows→Docker ni modalidad distribuida.
- Execution Plan v0.5.32 §2.5.1: 5.1.1 host real soportado; 5.1.2 Compose, volúmenes, secretos, red, recuperación y permisos efectivos. No cerrar por inspección YAML o CI.
- HITO PPPR.0.7 FROZEN, especialmente E-0.7-004/007/009/016/017/021/025/035/038/039. GAP-0.7-01/02 candidatos no confirmados; GAP-0.5-03 histórico, no duplicar.
- Atlas AS-IMPLEMENTED y runbook histórico `docs/architecture/adr/pipeline-stabilization/handoff/LABORATORIO_Y_REPRODUCCION.md`: C2 positivo histórico, no prueba del host actual; no ejecutar receta C2 sin presupuesto, recursos e imagen acreditados.
- DC-03: sin proveedor, destino, datos, finalidad, retención/entrenamiento y presupuesto explícitamente autorizados, cero inferencia comercial. Este procedimiento no concede permisos.
- Un PR para G5 completo (W5.1 + W5.2 + Exit Review). No merge de Wave ni cambio a FROZEN. Actualización de los tres registros LIVING al checkpoint de cierre de Wave con evidencia.

## 2. Audit First — observaciones estáticas en la base

| Frontera | Evidencia estática | Acción necesaria |
|---|---|---|
| Entrada | `apps/cli/main.py::handle_translate`: admisión por SHA, `--inbox-dir`; foreground `--run` opt-in reutiliza OCR/G3/G5 | Comprobar un único namespace y modo operativo, no lanzar foreground junto a daemons sobre el mismo trabajo |
| Compose | Base trae chaos/fake Gemini y binds; runtime override mueve SQLite/datos/output a volúmenes comunes, benchmark 0, perfila lab | Inspeccionar composición efectiva; no iniciar base aislado ni confundir runtime con lab |
| Laboratorio | `apps/lab/convergence_compose_preflight.py` comprueba imagen histórica, red interna y clave dummy; C2 histórico | Reutilizar controles pertinentes sin importar topología histórica como autoridad productiva |
| SQLite | `infra/db/connection.py` resuelve solo infra/db/*.db bajo SQLITE_STATE_DIR; ATTACH fsm_db depende de identidad real | Comprobar paths y alias reales por conexión, persistencia entre contenedores |
| Secretos/red | Runtime no entrega GROQ_API_KEY; lab sí usa dummy; red interna solo acreditada declarativamente en lab | Sin claves reales en W5.1; comprobar aislamiento y entrega autorizada por frontera antes de 5.2.3 |
| Recuperación | Sweeper declarado; reconciler y leases existentes | Verificar GAP-0.5-03 en composición efectiva; no asumir seguridad por presencia del daemon |
| Imagen | Dockerfile fija Tectonic 0.15.0 pero no digest; instalación pip no fijada al lock | Identificar imagen/versión efectiva y recursos antes de elegir corrección de build; no descargar aún |

## 3. P0 — inventario del host real (solo lectura)

Ejecutar desde la raíz del checkout en PowerShell si sigue siendo el host Windows/Docker Desktop Linux histórico. Si cambió el host, indicar sistema y modalidad antes de adaptar. El entorno de asistencia no tiene daemon Docker ni acceso al nodo del owner.

```powershell
git rev-parse HEAD
git branch --show-current
"WORKTREE_DIRTY_COUNT=" + @(git status --porcelain).Count
docker context show
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose version
docker info --format 'os={{.OSType}} arch={{.Architecture}} cpus={{.NCPU}} memory_bytes={{.MemTotal}}'
Get-PSDrive -PSProvider FileSystem | Select-Object Name,Free,Used
docker ps --format 'running={{.Names}} image={{.Image}}'
```

No compartir nombres de contenedores ajenos o sensibles: basta indicar si existen proyectos activos del traductor y si se pueden aislar. No compartir endpoints remotos, paths personales, `.env`, secretos, tokens ni `docker inspect` completo. Confirmar explícitamente que el contexto corresponde al daemon local del nodo autorizado; el nombre de contexto no prueba localidad por sí solo.

Si no hay Docker, el daemon no responde, el host no es local o hay recursos insuficientes, detener antes de crear recursos. Compose debe entender `!override` (v2.24.4+ conforme HITO 0.7 E-035); no deducir compatibilidad solo del nombre Docker Desktop. Sin presupuesto host/disco/RAM autorizado, no ejecutar arranque.

## 4. P1 — preflight declarativo posterior a P0

Desde el checkout exacto de Gate5, sin iniciar contenedores:

```powershell
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config --quiet
if ($LASTEXITCODE -ne 0) { throw "STOP: compose runtime invalido" }
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config --services
```

No publicar `config` expandido: puede incluir secretos. El siguiente paso de implementación debe evaluar de forma saneada servicio/comando, perfiles, mounts, state/data/output, rutas SQLite, usuario, capacidades, secretos presentes/ausentes sin valores, red y aislamiento. Resultado declarativo NO equivale a runtime ni a 5.1.1/5.1.2 DONE.

## 5. P2 — procedimiento histórico y evidencia de laboratorio (EJECUTADO en alcance indicado)

Con autorización específica del nodo y presupuesto de recursos, y tras aprobar composición efectiva: usar proyecto nuevo aislado, fuente sintética, cero proveedor comercial; verificar identidad de imagen y contenedor, UID y escritura en volúmenes propios, admisión CLI interna en inbox compartido, visibilidad de mismo estado por conexiones independientes, SQLite WAL y alias, arranque/reinicio y recuperación sin borrar estado, exclusión de roots legacy/lab no autorizados, controles reales de red/secretos. El E2E fake completo y crash/replay pertenecen a W5.2 y no se declaran ejecutados aquí. Preservar artefactos y logs saneados. Si un preflight falla, STOP y RCA antes de reintentar.

**Prohibido en P0/P1:** build/pull, up/run, bootstrap, eliminación de contenedores/volúmenes, down -v, prune, llamadas externas, corpus privado, gasto. No adoptar el host histórico ni seleccionar proveedor por inferencia. Ningún PASS de host se deduce de este documento.


## 6. Evidencia efectivamente ejecutada por owner (no acceso directo del Staff al daemon)

- Host Windows/Docker Desktop Linux, Engine 28.5.1, Compose 2.40.3-desktop.1, x86_64, 4 CPU, RAM 12545732608 bytes. Imagen local `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`, UID/GID 10001, Python 3.11.17, SQLite 3.40.1, Tectonic 0.15.0.
- Worktree inicial `a55d03c9151439d462575d7b7d1ba37bceaa2b10`: imports 5/5, preflight estático C0, bootstrap cuatro planos, aislamiento seis volúmenes (parser Python tras incidencia ALL_PROXY/all_proxy de PowerShell 5.1). Admisión CLI interna sin --run, PDF sintético 867 bytes SHA `c04e85a19df4603540d0100573e8fc477d7b3e0881e5197b472f9327a6642d16`; persistencia independiente, quick_check ok y WAL. Marcadores PPPR_G5_CONTAINER_ADMISSION_PASS y PPPR_G5_CROSS_CONTAINER_PERSISTENCE_PASS.
- HEAD `db880511bb570c5d11f3ff32dc4a2be00869bdbd`, CI #45319396033 SUCCESS: 1681 PASS/6 skipped/20 E2E excluidos; 8/8 Tectonic. PPPR_G5_EFFECTIVE_WIRING_PASS: 6 identidades/secrets, 5 namespace/ATTACH, fake state RO. PPPR_G5_CONTROLLED_RESTART_PASS: 8/8 WAL checkpoints, huellas lógicas y PDF iguales, cero imágenes/volúmenes nuevos, daemons detenidos. Disco libre final 37037170688 bytes.
- Todos estos testigos físicos usaron convergence-lab sobre host real; NO se transfieren automáticamente a la composición local soportada. Board FAVORABLE CON CORRECCIÓN FOCAL: 5.1.1 aceptada para DONE, corrección sweeper aceptada, H-G5-01 pendiente. Contención WAL y recuperación integral 5.2.2. 14 GAP históricos OPEN.

## 7. H-G5-01 — composición local soportada (BOARD_ACCEPTED en alcance offline)

Usar exclusivamente base + runtime + `docker-compose.local.yml` para este nodo autorizado. El overlay histórico convergence-lab conserva su significado y autorización separada; no combinar los dos overlays. No se modifica Dockerfile ni se pretende acreditar una imagen reconstruida. El tag de la imagen existente se verifica contra su ID exacto antes de cualquier efecto. La configuración local es deliberadamente offline hasta autorización DC-03 y verificación 5.2.3. No iniciar llm_worker ni el pipeline para W5.1.

| Control | Local soportado (alcance aceptado) | Exclusivo del laboratorio |
|---|---|---|
| Imagen y código | mismo ID local, no build/pull, checkout RO | fake y sustituciones de proveedor |
| Usuario | workers 10001:10001, sin capacidades; bootstrap root transitorio, capacidades acotadas | token C0 separado |
| Inicialización | `infra/db/local_volume_bootstrap.py` opt-in propio, comparte preparación no recursiva de propietarios con wrapper C0, baja privilegios antes del bootstrap canónico | wrapper C0 sigue exclusivamente lab |
| Montajes | seis volúmenes propios nocopy y checkout RO | fake solo state RO |
| Red | bridge interno, sin puertos, proxies/credenciales enumeradas vacías | fake HTTP interno, dummy |
| Reinicio | no automático; operador controla arranque/reinicio | escenarios de caos |
| Servicios | seis existentes, sin dependencia fake ni chaos activo | g3_fake y perfiles históricos |

Preflight nuevo `tools/pppr_local_preflight.py` valida JSON efectivo con Python, conjunto exacto de servicios, comandos, permisos, imagen, dependencias, montajes, nombres de volumen, red, secretos enumerados y opt-in. No imprime valores. Falsadores unitarios de drift. Preflight no es evidencia física.

### P3 — procedimiento y condiciones originales (ejecutado: resultado definitivo §8)

Desde worktree limpio del HEAD correctivo, con contexto local desktop-linux y mínimo preventivo 30 GiB libres, sin .env ni perfiles activos:

```powershell
python -B tools/pppr_local_preflight.py --project tpdfppprg501 --context desktop-linux
if ($LASTEXITCODE -ne 0) { throw "STOP: local preflight" }
```

Esperar PPPR_G5_LOCAL_STATIC_PASS. Proyecto nuevo aislado para acreditar inicialización real de propietarios sin tocar los seis volúmenes históricos de laboratorio. Volúmenes vacíos nocopy; no sembrar cachés, no duplicar imágenes ni descargar dependencias. Antes de crear recursos comprobar ausencia de contenedores/volúmenes/red del proyecto y guardar inventario global de IDs. Ejecutar solo db_bootstrap con run --no-deps --pull never y nombre de testigo (sin --rm, preservar contenedor detenido), verificar bootstrap real bajo UID/GID 10001 mediante propiedad de archivos y permisos efectivos; inspeccionar cada worker con entrypoint Python sin iniciar daemons; verificar mounts, ausencia de secretos enumerados, WAL/alias, admisión sintética sin --run y persistencia independiente. Arrancar solo sweeper con up -d --no-deps --no-build --pull never, comprobar cuatro checkpoints, reiniciar mismo contenedor, comprobar cuatro checkpoints nuevos, detener en finally y comparar huellas lógicas y SHA. Conservar resultados saneados, medir disco y confirmar inventario sin nuevas imágenes, solo seis volúmenes nuevos del proyecto. No borrar ni migrar datos históricos. Procedimiento efectivamente ejecutado y marcadores finales en §8. No repetir sobre los proyectos acreditados; una eventual nueva ejecución requiere causa concreta y autorización. Si falla, STOP y RCA. No E2E, inferencia, crash/replay, egress ni merge.



### P3.1 — checkpoint histórico supersedido: RCA de preflight local (owner, HEAD e64633c5d5f037400c960e7e81cd233f67767d50)

CI #45323666567 SUCCESS (1692 PASS, 6 skipped, 20 deselected), pero preflight local **FAIL** antes de crear recursos. Diagnóstico saneado de los seis servicios: IMAGE_MATCH=True, BUILD_PRESENT=True, PULL_NEVER=True, siete mounts exactos sin duplicados, checkout correcto RO, CREATE_HOST_PATH=ABSENT. El reset de build heredado dentro del anchor no resultó efectivo; Compose v2.40.3 upstream usa compose-go/v2 v2.9.1 cuyo bool CreateHostPath se serializa con omitempty (https://github.com/compose-spec/compose-go/blob/v2.9.1/types/types.go). Corrección focal: reset directo por servicio y lista común de mounts sin tag de merge sobre el anchor; se conserva el control estricto de conjunto de targets, RO, nocopy, origen existente. El preflight calibra el parser instalado con dos binds long-form explícitos false/true: acepta ausencia del campo solo si el parser distingue inequívocamente false omitido de true explícito; rechaza ambigüedad y auto-create. Nueva regresión obligatoria de los tres YAML reales mediante docker compose config en CI, sin contenedores ni operaciones de imagen. Falsadores adicionales de calibración y auto-create. CI y repetición del preflight en host pendientes. **No ejecutar bloque B/bootstrap hasta PASS sobre HEAD correctivo exacto.** El owner confirmó que el bloque B no fue ejecutado; no se crearon recursos Docker por esta incidencia. H-G5-01 OPEN, W5.1 IN_PROGRESS; W5.2 NOT_RUN.


### P3.2 — checkpoint histórico supersedido: corrección de la frontera de serialización

CI #45325554935 FAILURE sobre `782031523fbabf1c7dec410394b8315eaa85dff9`: static SUCCESS, unit 358 PASS, integration falló en el primer test real por `ValueError: ambiguous bind serializer`; suite completa y Tectonic posteriores SKIPPED. No se acreditó el contrato efectivo. La calibración indirecta no es suficiente y se elimina, no se declara aceptable la ambigüedad. Compose upstream v2.40.3 (cmd/compose/config.go, runConfigNoInterpolate) permite obtener el modelo combinado como diccionario con `config --no-interpolate --format json`, antes de convertirlo al Project tipado. Se contrasta con `config --format json` de los mismos archivos: el modelo combinado debe declarar explícitamente false para create_host_path en el bind /workspace, de origen exacto y RO, y la representación efectiva no puede indicar true. Si ambas vistas no acreditan la condición, STOP. No sustituir todos los controles efectivos por el modelo no interpolado. Se conserva el test real obligatorio y se agrega override negativo efectivamente procesado por Compose, más matriz de casos unitarios. No se ha demostrado aún la compatibilidad de ambas vistas en el runner o host; nueva CI y preflight pendientes. Sin recursos Docker adicionales ni bootstrap. H-G5-01 OPEN.


## 8. P3 definitivo — testigos owner PASS y ratificación (2026-11-24)

**HEAD acreditado:** `5d336fdc86868c4172deb658a8ab9b0c9da5368d`. CI #45326107574 SUCCESS 3/3, parser real obligatorio y override negativo PASS; 362 unit, 113 integración/2 skipped, 1704 suite técnica PASS/6 skipped/20 E2E excluidos; Tectonic 8/8; Pyright 0/0/0, import-linter 4/4. Selecciones no acumulativas. P3.1/P3.2 son historia, no estados vigentes. Board FAVORABLE AL CIERRE DE WAVE 5.1 comunicado por owner: H-G5-01 RESUELTO / BOARD_ACCEPTED, ambas Tasks DONE en modalidad inicial local offline de un nodo. Plan v0.5.32, Register §2.5 v0.1.33, Evidence §3.5 v0.1.34, PR #94. CI documental pendiente al registrar.

### 8.1 Procedimiento reproducible y puntos de control ejecutados

Registro de la ejecución del owner en Windows PowerShell 5.1 con Python local, contexto desktop-linux, Engine 28.5.1, Compose 2.40.3-desktop.1. Usar exclusivamente base + runtime + local; no combinar con convergence-lab. Los comandos siguientes son referencia reproducible de lo ejecutado, NO instrucción para repetir ahora. Antes de cada nueva sesión autorizada: verificar HEAD exacto esperado y worktree limpio, disco C >=30 GiB, ausencia de .env/perfiles/overrides no autorizados, preflight exacto, ID de imagen, inventario y propiedad de recursos. En pruebas posteriores, actualizar el SHA esperado solo tras verificar CI del nuevo HEAD; no reutilizar un proyecto fresco como si fuera vacío.

```powershell
# Bloque A (ya ejecutado)
git rev-parse HEAD
git status --porcelain
Get-PSDrive C | Select-Object Name,Free,Used
python -B tools/pppr_local_preflight.py --project tpdfppprg501 --context desktop-linux
if ($LASTEXITCODE -ne 0) { throw "STOP: preflight local fallido" }

# Prefijo común de los comandos Docker, no usar Compose genérico.
$dc = @("--context","desktop-linux","compose","--project-name","tpdfppprg501",
    "-f","docker-compose.yml","-f","docker-compose.runtime.yml","-f","docker-compose.local.yml")

# Bloque B (ya ejecutado, solo una vez sobre proyecto inicialmente inexistente)
# Antes: inventario de imágenes IDs, volúmenes y nombres de contenedores/redes;
# exigir que no existan recursos del proyecto.
docker @dc run --no-deps --pull never --name tpdfppprg501-bootstrap-witness -T db_bootstrap
if ($LASTEXITCODE -ne 0) { throw "STOP: bootstrap local fallido; no repetir" }
```

Owner: LOCAL_FRESH_PROJECT_PASS, LOCAL_BOOTSTRAP_IDENTITY_PASS, LOCAL_BOOTSTRAP_CAPABILITIES_PASS, LOCAL_VOLUME_PASS 6/6, LOCAL_INTERNAL_NETWORK_PASS, EXACTLY_SIX_NEW_VOLUMES_PASS, NO_NEW_IMAGES_PASS, NO_RUNNING_DAEMONS_PASS, PPPR_G5_LOCAL_BOOTSTRAP_PASS. Verificaciones Python JSON de docker inspect: imagen exacta, comando local_volume_bootstrap.py, root inicial, exit 0/detenido, CapAdd CHOWN/DAC_OVERRIDE/SETGID/SETUID y ALL drop, restart no; mounts exactos y checkout RO, seis nombres de volumen con label del proyecto, driver local y sin opciones; red internal/bridge sin IPv6 ni publicación de puertos. No imprimir inspect completo ni secretos.

Bloque C (ya ejecutado): por servicio ocr_router, llm_worker, assembler, reconciler, sweeper, contenedor de inspección con `docker @dc run --no-deps --pull never --name tpdfppprg501-<servicio>-witness -T --entrypoint python <servicio> -B -` y script por stdin. El script del owner verificó:
- os.getuid/getgid/geteuid/getegid = 10001; /proc/self/status CapEff/CapPrm/CapBnd=0, NoNewPrivs=1.
- /proc/self/mountinfo /workspace ro, seis raíces rw; Path.stat uid/gid=10001:10001 y os.access R/W/X; state/db y cuatro archivos DB mismo owner, R/W. Ausencia de variables SECRETS de tools.pppr_local_preflight y opt-ins locales/LAB en workers; benchmark 0.
- infra.db.connection.resolve_sqlite_path("infra/db/"+name) = "/app/state/db/"+name, get_connection en closing, PRAGMA quick_check=("ok",), journal_mode=("wal",), synchronous=(1,); queue ATTACH alias fsm_db a fsm.db, COUNT document_fsm y chunk_tasks = 0.
- Solo ocr_router: crear PDF sintético con fitz.open(), new_page(), insert_text((72,72),"PPPR Gate 5 local host synthetic admission witness."), save("/app/data/g5_local_host_probe.pdf"); exigir fuente ausente antes. Ejecutar `python -B -m apps.cli.main translate /app/data/g5_local_host_probe.pdf --inbox-dir /app/data/inbox` sin --run. SHA-256 de fuente y copia iguales; otros cuatro contenedores observan ambas rutas y mismo SHA. No repetir admisión.
- Inspección independiente de cada contenedor detenido: imagen exacta, user 10001:10001, exit 0, CapDrop ALL/CapAdd ausente, no privileged, restart no, sin puertos, siete mounts exactos y volúmenes de proyecto.
- Inventario sin nuevos volúmenes ni imágenes; proyecto sin procesos activos.

Resultados: LOCAL_NONROOT_CAPABILITIES_PASS, LOCAL_VOLUME_OWNERSHIP_PASS, LOCAL_SECRET_SCOPE_PASS, LOCAL_SQLITE_OWNERSHIP_AND_NAMESPACE_PASS, LOCAL_SHARED_INBOX_PASS y LOCAL_CONTAINER_CONFIG_PASS 5/5; LOCAL_CLI_ADMISSION_PASS; PPPR_G5_LOCAL_EFFECTIVE_WIRING_PASS. Identidad sintética a4f1d5a91f260c11e1e346f733a46cf87fe3ac54b518565a334c884dd269d9b0. Warning fitz y mojibake de consola no invalidaron marcadores. Sin OCR, inferencia ni ensamblado.

Bloque D (ya ejecutado): snapshot previo y posterior en contenedores efímeros `docker @dc run --rm --no-deps --pull never -T --entrypoint python sweeper -B -`, código por stdin; para cada DB fsm/queue/event/materialized abrir sqlite3.connect(path.as_uri()+"?mode=ro", uri=True), verificar uid/gid, quick_check, journal_mode WAL y calcular sha256 de "\n".join(db.iterdump()).encode(); añadir SHA del PDF admitido y exigir igualdad exacta antes/después. No compara bytes físicos de WAL sino estado lógico.

```powershell
# Solo sweeper, tras snapshot previo y comprobación de recursos.
docker @dc up -d --no-deps --no-build --pull never sweeper
# Inspeccionar ID único activo, imagen, user, comando, mounts, red,
# restart no, capacidades y NoNewPrivileges; guardar StartedAt.
# docker logs --since <StartedAt> <ID> : esperar con límite 60 s
# startup SWEEPER_WAL_MAINTENANCE_ONLY y cuatro SWEEPER_WAL_CHECKPOINT_OK.
docker @dc restart --timeout 10 sweeper
# Exigir mismo ID, StartedAt nuevo y otros cuatro checkpoints.
# En el procedimiento Python ejecutado, stop se ejecutó en finally.
docker @dc stop --timeout 10 sweeper
# Snapshot posterior y comparación, inventario de imágenes/volúmenes,
# confirmar cero daemons activos; STOP si cualquier diferencia.
```

Resultados owner: LOCAL_RESTART_RESOURCES_PASS, LOCAL_INITIAL_STATE_SNAPSHOT_PASS, LOCAL_SWEEPER_CONTAINER_POLICY_PASS, LOCAL_WAL_CHECKPOINT_PASS (Event, Materialized, FSM, Queue) 8/8, LOCAL_SWEEPER_START_PASS, LOCAL_SWEEPER_RESTART_PASS, LOCAL_SQLITE_LOGICAL_STATE_UNCHANGED_PASS, LOCAL_PDF_IDENTITY_UNCHANGED_PASS, NO_NEW_IMAGES_PASS, NO_NEW_VOLUMES_PASS, NO_RUNNING_DAEMONS_PASS, PPPR_G5_LOCAL_CONTROLLED_RESTART_PASS. Se rechazaban marcadores SWEEPER_ABORTED, SWEEPER_PERMANENT_FAILURE, SWEEPER_WAL_CHECKPOINT_FAILED/INCOMPLETE y SWEEPER_WAL_PLANE_MISSING. Sin trabajo activo en FSM/queue durante el reinicio.

### 8.2 Disposición y conservación

Conservar **ambos** proyectos tpdfconvppprg501 y tpdfppprg501, sus doce volúmenes en total, contenedores testigo detenidos y PDF sintéticos; no limpiar recursos históricos, no down -v ni prune, no repetir bootstrap/admisión/testigos sin causa concreta. Disco libre final 37035110400 bytes (aprox. 34,49 GiB); cero imágenes nuevas, cero build/pull/descargas de modelos o dependencias en host. No sembrar cachés para cerrar W5.1. Las variaciones globales de disco no se atribuyen exclusivamente a Docker.

Observaciones Board no bloqueantes: ampliar cobertura negativa directa de prepare_owners cuando corresponda (propietario incompatible, symlink, mount ausente, sin modificación); identidad de imagen no acredita reproducibilidad del build ni barrera infalible; red interna y restart manual no prueban egress universal ni recuperación F18. Recuperación integral/contención WAL en 5.2.2; egress/autoridad de credenciales y proveedor en ámbito 5.2.3 antes de efecto. Sin nuevas Tasks ni diferimientos arbitrarios. GAP-0.5-03 aceptado en ámbito sweeper, 14 GAP P1 históricos OPEN globalmente. W5.2 NOT_RUN, G5 Exit Review NOT_RUN, CV científica FAIL/DEFERRED, PRODUCT_READINESS=NOT_CERTIFIED. No inferencia comercial, merge ni modificación FROZEN.
