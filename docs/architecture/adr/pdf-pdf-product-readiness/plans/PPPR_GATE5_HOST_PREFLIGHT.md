# PPPR Gate 5 — Preflight de host y modalidad soportada

**Estado:** procedimiento operativo LIVING / no normativo; Task 5.1.1 BOARD_ACCEPTED para DONE; 5.1.2 IN_PROGRESS por H-G5-01; W5.2 NOT_RUN. Reconciliación formal de los tres documentos vivos al cierre de Wave. No sustituye al Execution Plan ni modifica criterios de aceptación.

**Base:** `7ff8b84733a63efd3012adf14070db86cff051ad`, rama `pdf-pdf-product-readiness`. CI post-merge #45314286191 SUCCESS (3/3 jobs); CV #45314286115 FAIL/DEFERRED, BASELINE_INTEGRITY_FAILURE (15 PDF privados ausentes). G1–G4 COMPLETED/PASS; 20/30 Tasks DONE, 14 GAP P1 OPEN, PRODUCT_READINESS=NOT_CERTIFIED.

## 1. Autoridad y frontera

- ADR Maestro DC-08: CLI dentro del contenedor de un nodo, D-1/D-2; no puente Windows→Docker ni modalidad distribuida.
- Execution Plan v0.5.31 §2.5.1: 5.1.1 host real soportado; 5.1.2 Compose, volúmenes, secretos, red, recuperación y permisos efectivos. No cerrar por inspección YAML o CI.
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

## 7. H-G5-01 — composición local soportada candidata

Usar exclusivamente base + runtime + `docker-compose.local.yml` para este nodo autorizado. El overlay histórico convergence-lab conserva su significado y autorización separada; no combinar los dos overlays. No se modifica Dockerfile ni se pretende acreditar una imagen reconstruida. El tag de la imagen existente se verifica contra su ID exacto antes de cualquier efecto. La configuración local es deliberadamente offline hasta autorización DC-03 y verificación 5.2.3. No iniciar llm_worker ni el pipeline para W5.1.

| Control | Local soportado candidato | Exclusivo del laboratorio |
|---|---|---|
| Imagen y código | mismo ID local, no build/pull, checkout RO | fake y sustituciones de proveedor |
| Usuario | workers 10001:10001, sin capacidades; bootstrap root transitorio, capacidades acotadas | token C0 separado |
| Inicialización | `infra/db/local_volume_bootstrap.py` opt-in propio, comparte preparación no recursiva de propietarios con wrapper C0, baja privilegios antes del bootstrap canónico | wrapper C0 sigue exclusivamente lab |
| Montajes | seis volúmenes propios nocopy y checkout RO | fake solo state RO |
| Red | bridge interno, sin puertos, proxies/credenciales enumeradas vacías | fake HTTP interno, dummy |
| Reinicio | no automático; operador controla arranque/reinicio | escenarios de caos |
| Servicios | seis existentes, sin dependencia fake ni chaos activo | g3_fake y perfiles históricos |

Preflight nuevo `tools/pppr_local_preflight.py` valida JSON efectivo con Python, conjunto exacto de servicios, comandos, permisos, imagen, dependencias, montajes, nombres de volumen, red, secretos enumerados y opt-in. No imprime valores. Falsadores unitarios de drift. Preflight no es evidencia física.

### P3 — ejecución pendiente (tras CI exacta SUCCESS)

Desde worktree limpio del HEAD correctivo, con contexto local desktop-linux y mínimo preventivo 30 GiB libres, sin .env ni perfiles activos:

```powershell
python -B tools/pppr_local_preflight.py --project tpdfppprg501 --context desktop-linux
if ($LASTEXITCODE -ne 0) { throw "STOP: local preflight" }
```

Esperar PPPR_G5_LOCAL_STATIC_PASS. Proyecto nuevo aislado para acreditar inicialización real de propietarios sin tocar los seis volúmenes históricos de laboratorio. Volúmenes vacíos nocopy; no sembrar cachés, no duplicar imágenes ni descargar dependencias. Antes de crear recursos comprobar ausencia de contenedores/volúmenes/red del proyecto y guardar inventario global de IDs. Ejecutar solo db_bootstrap con run --rm --no-deps --pull never, verificar bootstrap real bajo UID/GID 10001 mediante propiedad de archivos y permisos efectivos; inspeccionar cada worker con entrypoint Python sin iniciar daemons; verificar mounts, ausencia de secretos enumerados, WAL/alias, admisión sintética sin --run y persistencia independiente. Arrancar solo sweeper con up -d --no-deps --no-build --pull never, comprobar cuatro checkpoints, reiniciar mismo contenedor, comprobar cuatro checkpoints nuevos, detener en finally y comparar huellas lógicas y SHA. Conservar resultados saneados, medir disco y confirmar inventario sin nuevas imágenes, solo seis volúmenes nuevos del proyecto. No borrar ni migrar datos históricos. Procedimiento detallado de ejecución física se entrega después de CI; no afirmar P3 PASS hasta salida real del owner. Si falla, STOP y RCA. No E2E, inferencia, crash/replay, egress ni merge.



### P3.1 — RCA de preflight local (owner, HEAD e64633c5d5f037400c960e7e81cd233f67767d50)

CI #45323666567 SUCCESS (1692 PASS, 6 skipped, 20 deselected), pero preflight local **FAIL** antes de crear recursos. Diagnóstico saneado de los seis servicios: IMAGE_MATCH=True, BUILD_PRESENT=True, PULL_NEVER=True, siete mounts exactos sin duplicados, checkout correcto RO, CREATE_HOST_PATH=ABSENT. El reset de build heredado dentro del anchor no resultó efectivo; Compose v2.40.3 upstream usa compose-go/v2 v2.9.1 cuyo bool CreateHostPath se serializa con omitempty (https://github.com/compose-spec/compose-go/blob/v2.9.1/types/types.go). Corrección focal: reset directo por servicio y lista común de mounts sin tag de merge sobre el anchor; se conserva el control estricto de conjunto de targets, RO, nocopy, origen existente. El preflight calibra el parser instalado con dos binds long-form explícitos false/true: acepta ausencia del campo solo si el parser distingue inequívocamente false omitido de true explícito; rechaza ambigüedad y auto-create. Nueva regresión obligatoria de los tres YAML reales mediante docker compose config en CI, sin contenedores ni operaciones de imagen. Falsadores adicionales de calibración y auto-create. CI y repetición del preflight en host pendientes. **No ejecutar bloque B/bootstrap hasta PASS sobre HEAD correctivo exacto.** El owner confirmó que el bloque B no fue ejecutado; no se crearon recursos Docker por esta incidencia. H-G5-01 OPEN, W5.1 IN_PROGRESS; W5.2 NOT_RUN.


### P3.2 — corrección de la frontera de serialización

CI #45325554935 FAILURE sobre `782031523fbabf1c7dec410394b8315eaa85dff9`: static SUCCESS, unit 358 PASS, integration falló en el primer test real por `ValueError: ambiguous bind serializer`; suite completa y Tectonic posteriores SKIPPED. No se acreditó el contrato efectivo. La calibración indirecta no es suficiente y se elimina, no se declara aceptable la ambigüedad. Compose upstream v2.40.3 (cmd/compose/config.go, runConfigNoInterpolate) permite obtener el modelo combinado como diccionario con `config --no-interpolate --format json`, antes de convertirlo al Project tipado. Se contrasta con `config --format json` de los mismos archivos: el modelo combinado debe declarar explícitamente false para create_host_path en el bind /workspace, de origen exacto y RO, y la representación efectiva no puede indicar true. Si ambas vistas no acreditan la condición, STOP. No sustituir todos los controles efectivos por el modelo no interpolado. Se conserva el test real obligatorio y se agrega override negativo efectivamente procesado por Compose, más matriz de casos unitarios. No se ha demostrado aún la compatibilidad de ambas vistas en el runner o host; nueva CI y preflight pendientes. Sin recursos Docker adicionales ni bootstrap. H-G5-01 OPEN.
