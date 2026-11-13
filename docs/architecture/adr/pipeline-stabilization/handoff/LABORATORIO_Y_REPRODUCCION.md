# Laboratorio y reproducción — ruta única PDF→PDF

**Edición:** v2.0 · **corte del repositorio:** 2026-11-13 · **rama destino:** `pipeline_stabilization`  
**Sujeto de código:** merge [`02edd83cc77fd8c7b106b087bedd3bc83743f9f5`](https://github.com/RDsanchez-git/translator_pdf/commit/02edd83cc77fd8c7b106b087bedd3bc83743f9f5). La corrida multiproceso original C2 fue ejecutada sobre `93a8f9021cbb95c92c9242d68fd6f1dfe9eb3d0f` (PR #46).  
**Objetivo:** preparar, inspeccionar, ejecutar, auditar y detener pruebas sobre la **única** ruta admitida CLI → OCR Router → G3 (`runtime/engine.py`) → G5 (`apps/compiler/__main__.py`) → PDF. El fake devuelve eco controlado, **no traducción lingüística**. Ninguna receta activa proveedor real ni autoriza producción/cutover.

**Leyenda de procedencia:** **[OBSERVADO]** = resultado real reportado por el owner en 2026-11-12; **[CÓDIGO]** = comportamiento verificado en scripts/Compose vigentes; **[RECETA NUEVA / SIN E2E]** = secuencia íntegra derivada de ellos que todavía no fue reejecutada desde cero sobre volúmenes nuevos. No extrapolar PASS históricos a futuros commits.

## 0. Elegir la prueba adecuada

| Objetivo | Modalidad | Costo/resultado |
|---|---|---|
| Verificar que Compose sea válido y que la imagen esté presente | **A. Preflight C0** | Solo lectura; no arranca recursos, NO prueba PDF |
| Traducir un PDF sintético mediante parser + G3 fake + Tectonic rápidamente | **B. Foreground B03.2** | Un contenedor `--rm --network none`, workspace host temporal, **evidencia retenida** |
| Verificar **los tres daemons independientes**, sus bases compartidas y un PDF completo | **C. Multiproceso C2** | Seis volúmenes nuevos, bootstrap, fake, OCR/G3/G5, verificación de HTTP/SQLite/PDF |
| Repetir específicamente la comparación con el C2 antiguo | **D. T07** | Requiere **el contenedor C2 histórico vivo** y la fixture histórica exacta; no apto para nuevo RUN-ID |
| Verificar recuperación, estado incierto o G5 fencing sin Docker | **E. Tests focales** | SQLite efímeras/pytest; falsadores acotados |

**Camino rápido:** usar A y B para un ensayo cotidiano. Usar C cuando cambie la topología, la admisión, la frontera entre procesos, los recibos o el ensamblado. No reabrir C0–C4 solo para probar B.

## 1. Archivos de la implementación que debes reconocer

| Archivo | Papel |
|---|---|
| `docker-compose.yml` | Base heredada (incluye build, puertos/chaos y `IS_BENCHMARK=1`); **no ejecutar sola** |
| `docker-compose.runtime.yml` | Override: bases/volúmenes compartidos, inbox/output, `IS_BENCHMARK=0` |
| `docker-compose.convergence-lab.yml` | Override **solo laboratorio**: imagen local fija, `/workspace:ro`, `nocopy`, `g3_fake` interno, sin build/pull |
| `apps/lab/convergence_compose_preflight.py` | Inspección estática segura y, opcionalmente, ID de imagen local |
| `apps/lab/convergence_db_bootstrap.py` | Ownership de seis volúmenes nuevos; desciende a UID10001 antes de `infra/db/bootstrap.py` |
| `apps/lab/g3_fake.py` | Fake privado: lee plan desde `queue.db` con SQLite RO, HTTP JSON auditado |
| `apps/cli/main.py`, `apps/cli/pdf_inbox.py` | `translate` sin `--run` = admisión por SHA-256 al inbox realmente compartido |
| `apps/ocr_router/__main__.py` | Parser, AST, perfil, `ChunkPlan` contextual, queue/FSM/archivado |
| `runtime/engine.py` / `runtime/chunk_staging.py` / `runtime/publication_pipeline.py` | G3 real: claims, `PRESERVE` sin POST, `TRANSLATE` vía fake, receipts, publicación, avance FSM |
| `apps/compiler/__main__.py` / `infra/db/assembly_recovery.py` | G5 real: lease, CQRS, Tectonic y publicación PDF fenced |
| `apps/daemons/reconciler.py` / `runtime/sweeper.py` | Recuperación y mantenimiento (NO reintentan `G3_EXTERNAL_UNKNOWN`) |
| `apps/lab/offline_pdf_lab.py` | Launcher B03 y **extractor seguro de cachés**/fixture de texto |
| `apps/lab/t07_foreground_compare.py` | Comparación histórica T07, no launcher genérico de C2 nuevo |

**Vínculo técnico:** [Atlas de la ruta única](ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md); [evidencia y DoD C0–C4](EVIDENCIA_Y_CIERRE.md).

## 2. Condiciones de seguridad y presupuesto

**Entorno observado:** Windows / PowerShell 5.1, venv Python, Docker Desktop Linux con contexto `desktop-linux` y Compose v2 compatible con `!override`/`!reset`. La imagen ya debe existir; código del checkout se monta **RO** en `/workspace` mientras `/app` permanece escribible para bases y outputs.

- **Prohibidos sin autorización distinta:** `docker build`, `docker pull`, `docker save`, `docker system prune`, `docker volume prune`, `docker compose down -v`, eliminar volúmenes históricos, importar el TAR del laboratorio G5/2, usar secretos reales o proveedores externos. Nunca ejecutar `docker compose up` sin indicar servicios.
- **Proyecto nuevo para cada C2:** RUN-ID `[a-z0-9]{8,16}` no usado; nombre Docker Compose `tpdfconv<run-id>`. No usar de nuevo `tpdfconvconv1211b`, `i0l19cf15cac6b12`, ni los proyectos G5.
- **Solo red fake:** `chaos_net internal:true`, IPv6 deshabilitado, ningún puerto publicado para los servicios seleccionados; `g3_fake` escucha en `:8080` **solo dentro** de esa red. Ningún `toxiproxy` o `fake-gemini` habilitado por perfiles del Compose base.
- **Solo seis volúmenes aislados, `nocopy:true`:** `g3_runtime_state`, `g3_runtime_data`, `g3_runtime_output`, `hf_models_cache`, `torch_cache`, `tectonic_cache`. No contienen las cachés heredadas de la imagen: **sembrarlas** antes de los daemons.
- **Cuidado del bootstrap:** `db_bootstrap` root **solo durante preparación de volúmenes nuevos**, wrapper valida mounts, toma ownership de sus raíces y baja a `10001:10001`. No ejecutarlo de nuevo en bases existentes.
- **Cuidado de la inferencia:** `G3_EXTERNAL_UNKNOWN` = cuarentena: no reiniciar el POST ni reingresar sin disposición. No ejecutar `translate --run` y los daemons sobre la misma generación.
- No publicar `.env`, configuración efectiva con tokens, `docker inspect` entero, texto del PDF, prompts ni credenciales. Usar `config --quiet` y logs saneados.
- **Recursos:** el Compose original declara OCR con límite `10g`, G3 `6g`, G5 `2g`; Docker Desktop necesita margen suficiente para la ejecución, sin asumir que esos límites sean el consumo real. La regla antigua R2/C-L1 de **21 GiB libres antes de escribir / STOP debajo de 20 GiB** era **política local histórica**, no un mínimo contractual de este C2. Antes de crear volúmenes, registrar RAM y disco efectivos y fijar el presupuesto de la corrida. B03.2 exige **2 GiB libres** en su código.
- Si falla imagen/ZIP/seguridad, STOP. No «arreglar» automáticamente cambiando imagen, egress o eliminando datos.

**Dato recuperado del G5/2 anterior aplicable al G5 actual:** Tectonic requiere caché offline, y `os.replace` del PDF físico ocurre antes del COMMIT SQLite. Puede existir PDF materializado sin FSM `COMPLETED` después de un crash. **No** usar como kit actual el TAR histórico G5 (~7 GiB), su imagen diferente `sha256:b476a8…` o sus comandos SIGKILL sobre volúmenes nuevos.

## 3. Identidades exactas, red y rutas del sandbox C2

**Imagen C0–C2 [CÓDIGO/OBSERVADO]:**  
`i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824`  
SHA **`sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`**. No descargar/sustituir si falta.

**ZIP histórico reutilizable **solo para las cachés** [CÓDIGO/OBSERVADO]:**  
`Downloads/PAQUETE_HISTORICO_G4_B03_PDF_A_PDF_FBF166B_R1.zip`  
SHA-256 **`ac0300bc0a2a6ac8117f8fb34af000ba91747f2761e5562ba5bb4ae14fccf76d`**. El extractor `offline_pdf_lab._seed_caches` permite **294 ficheros Tectonic (~43,35 MB) y un tiktoken**, no AST, PDFs, WAL ni bases antiguas.

| Volumen | Montaje | Datos |
|---|---|---|
| `g3_runtime_state` | `/app/state` | `/app/state/db/{queue,fsm,materialized,event,documents}.db` |
| `g3_runtime_data` | `/app/data` | `inbox`, `archive`, `error`, fixtures |
| `g3_runtime_output` | `/app/output` | `translated_<document_id>.pdf` |
| `hf_models_cache` | `/app/.cache/hf` | cache HF nueva |
| `torch_cache` | `/app/.cache/torch` | cache Torch nueva |
| `tectonic_cache` | `/app/.cache/tectonic` | 294 ficheros offline |
| Bind RO | `<checkout>:/workspace:ro` | código actual, sin escrituras en checkout |

`g3_fake` **solo** monta `/workspace:ro` y `/app/state:ro`; no tiene montajes de inbox/PDF/output. `IS_BENCHMARK=0`, `PYTHONPATH=/workspace`, `SQLITE_STATE_DIR=/app/state/db`, `QUEUE_DB_PATH=/app/state/db/queue.db`, `FSM_DB_PATH=/app/state/db/fsm.db`, `MAT_DB_PATH=/app/state/db/materialized.db`, `GROQ_BASE_URL=http://g3_fake:8080`, `GROQ_API_KEY` dummy; `GEMINI_API_KEY` vacío y proxies HTTP vacíos. El SDK llama a `/openai/v1/chat/completions`; no duplicar el prefijo en `GROQ_BASE_URL`.

## 4. A — Preflight seguro sin crear recursos

Desde la raíz del repositorio con tu venv activado. **Leer primero** el HEAD y el contexto; no usar `COMPOSE_PROFILES`.

~~~powershell
git rev-parse HEAD
git status --short
docker context show
docker compose version
docker image inspect i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824 --format '{{.Id}}'

# RUN-ID solo de inspección, sin crear contenedores:
python -B -m apps.lab.convergence_compose_preflight --run-id soloins01 --verify-local-image
if ($LASTEXITCODE -ne 0) { throw "STOP: preflight Compose/imagen" }

# Inventario de solo lectura:
docker ps -a --format '{{.Names}} {{.Status}}'
docker volume ls --format '{{.Name}}'
docker network ls --format '{{.Name}}'
docker system df
~~~

Esperado: `C0_T01_STATIC_CANDIDATE_PASS: no containers started; runtime still unverified`. Cualquier `C0_T01_BLOCKED`/`C0_T01_FAIL` obliga STOP. Este preflight analiza comandos, UID, montajes, red, fake, estado y proyecto, **no** acredita egress físico ni PDF. No volcar `docker compose config` completo con credenciales en logs.

## 5. B — Foreground rápido sin Compose [LAUNCHER SOPORTADO]

El lanzador verifica imagen y ZIP exactos; utiliza `docker run --rm --pull never --network none` y fake loopback. Usa el parser, G3 y G5 reales del checkout con `--run`, pero NO daemons independientes.

~~~powershell
python -B -m apps.lab.offline_pdf_lab --preflight
if ($LASTEXITCODE -ne 0) { throw "STOP: ZIP/imagen/Docker" }

# Solo si está autorizada la escritura. Genera fixture PDF sintética:
python -B -m apps.lab.offline_pdf_lab --run-smoke
if ($LASTEXITCODE -ne 0) { throw "STOP: revisar B032_STOP y conservar evidencias" }

# Alternativa con otro PDF permitido:
# python -B -m apps.lab.offline_pdf_lab --run-pdf "C:\RUTA\documento.pdf"
~~~

**Efectos y salida:** `--preflight` no crea contenedores. `--run-smoke`/`--run-pdf` crean carpeta `%TEMP%\translator_pdf_b032_*` y **LA RETIENEN**, además de exportar PDF bajo `Downloads/translator_pdf_offline` sin sobrescribir. Se valida `%PDF-` y FSM `COMPLETED`. El fake hace eco: no certifica calidad científica/lingüística ni el C2 multiproceso. No limpiar esos temporales sin constatar titularidad.


## 6. C — Procedimiento C2 multiproceso sobre proyecto nuevo

**[RECETA NUEVA: todavía SIN E2E acreditado en un RUN-ID nuevo].** Se basa en los comandos de arranque observados en el [acta C2](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837358365), el [testigo físico](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837649853) y los scripts/Compose reales. La siembra y fixture que siguen son una composición **nueva**, no una reejecución certificada. Cada fallo implica **STOP sin repetir bootstrap, admisión ni POST**. Esta sección escribe nuevas carpetas, volúmenes, SQLite, logs y PDF; requiere autorización y presupuesto de disco/RAM antes de comenzar.

### C.1. Preparar un RUN-ID nuevo y verificar aislamiento sin escritura

Ejecutar en PowerShell desde la raíz del checkout. Cambiar `ensayoa01` por un RUN-ID **nunca usado** (8–16 letras minúsculas/números). El prefijo `tpdfconv` lo genera el preflight y debe coincidir con el proyecto Compose. No aceptar recursos de otras ejecuciones.

~~~powershell
$ErrorActionPreference = "Stop"
$RunId = "ensayoa01"  # CAMBIAR por uno propio nuevo
$Project = "tpdfconv$RunId"
$dc = @("compose", "-p", $Project,
    "-f", "docker-compose.yml",
    "-f", "docker-compose.runtime.yml",
    "-f", "docker-compose.convergence-lab.yml")
if ($env:COMPOSE_PROFILES) { throw "STOP: COMPOSE_PROFILES activo" }
python -B -m apps.lab.convergence_compose_preflight --run-id $RunId --verify-local-image
if ($LASTEXITCODE -ne 0) { throw "STOP: preflight de Compose/imagen" }
& docker @dc config --quiet
if ($LASTEXITCODE -ne 0) { throw "STOP: Compose inválido" }

$existingContainers = @(docker ps -a --filter "label=com.docker.compose.project=$Project" --format '{{.ID}}' | Where-Object { $_ })
$existingVolumes = @(docker volume ls --filter "label=com.docker.compose.project=$Project" --format '{{.Name}}' | Where-Object { $_ })
$existingNetworks = @(docker network ls --filter "label=com.docker.compose.project=$Project" --format '{{.Name}}' | Where-Object { $_ })
if ($existingContainers.Count -or $existingVolumes.Count -or $existingNetworks.Count) {
    throw "STOP: colisión de proyecto/RUN-ID"
}
Write-Output "C2_NEW_PROJECT_COLLISION_GUARD_PASS: $Project"
~~~

**Antes del primer comando con escritura:** comprobar también que ningún objeto Docker tiene nombres calculados iguales pero carece de las etiquetas de Compose; reservar espacio y memoria efectivos, identificar fuente ZIP y cache, y registrar SHA de git e imagen. `docker compose config --quiet` no inicia contenedores; el preflight es **solo estático**. No publicar una salida completa de `config` con secretos.

### C.2. Extraer solo caches desde ZIP autorizado a una carpeta host nueva

El extractor del código actual `offline_pdf_lab._check_history` confirma SHA-256, y `_seed_caches` extrae únicamente 294 archivos Tectonic y uno tiktoken. **Sí escribe** en `%TEMP%`; no restaura DB/AST/PDF/receipts del ZIP anterior.

~~~powershell
$Zip = Join-Path $HOME "Downloads\PAQUETE_HISTORICO_G4_B03_PDF_A_PDF_FBF166B_R1.zip"
$SeedDir = Join-Path $env:TEMP ("tpdf_seed_" + $RunId)
if (Test-Path -LiteralPath $SeedDir) { throw "STOP: semilla ya existe" }
New-Item -ItemType Directory -Path $SeedDir -ErrorAction Stop | Out-Null

$seedCode = @'
from pathlib import Path
import sys
from apps.lab.offline_pdf_lab import _check_history, _seed_caches
archive, workspace = map(Path, sys.argv[1:3])
_check_history(archive)
counts = _seed_caches(archive, workspace)
if counts != (294, 1):
    raise SystemExit("STOP_CACHE_COUNT_MISMATCH")
print("C2_HOST_CACHE_SEED_PASS", counts)
'@
python -B -c $seedCode $Zip $SeedDir
if ($LASTEXITCODE -ne 0) { throw "STOP: cache no verificada" }
~~~

**Esperado:** `C2_HOST_CACHE_SEED_PASS (294, 1)`; `$SeedDir\cache` contiene Tectonic y `$SeedDir\data\tiktoken-cache` contiene tiktoken. Reutiliza el extractor verificado por B03 pero **aún no se ha validado este procedimiento conjunto C2**.

### C.3. Crear seis volúmenes nuevos y realizar bootstrap UNA sola vez

**[ESCRITURA DOCKER].** Solo con presupuesto/autorización. El wrapper valida montajes, toma ownership de raíces de los seis volúmenes y **baja a UID10001** antes de aplicar el esquema SQLite. El servicio ha de salir `exited 0`; ante fallo, **no repetir sobre esos volúmenes**.

~~~powershell
& docker @dc up -d --no-deps --no-build --pull never db_bootstrap
if ($LASTEXITCODE -ne 0) { throw "STOP: bootstrap no inició" }
$boot = (& docker @dc ps -a -q db_bootstrap | Select-Object -First 1)
if (-not $boot) { throw "STOP: bootstrap container no localizado" }
$bootState = ""
for ($i = 0; $i -lt 60; $i++) {
    $bootState = (& docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' $boot).Trim()
    if ($bootState.StartsWith("exited")) { break }
    Start-Sleep -Seconds 1
}
if ($bootState -ne "exited 0") { throw "STOP: bootstrap no exit 0: $bootState" }
& docker @dc logs --tail 40 db_bootstrap
Write-Output "C2_FRESH_BOOTSTRAP_EXIT0"
~~~

### C.4. Transferir solo caches a los volúmenes frescos

**[RECETA NUEVA, ESCRITURA EN LOS NUEVOS VOLUMENES].** El override define `nocopy:true`, de modo que Tectonic/tiktoken no se copiarán solos. Se utiliza un contenedor efímero basado en `ocr_router` con su **comando reemplazado** (no inicia el daemon), con mount adicional **RO** del seed y usuario 10001. Rechazar destinos ya poblados.

~~~powershell
$copyCode = @'
from pathlib import Path
import shutil
root = Path("/lab_seed")
pairs = (
    (root / "cache", Path("/app/.cache/tectonic"), 294),
    (root / "data" / "tiktoken-cache", Path("/app/data/tiktoken-cache"), 1),
)
for src, dst, expected in pairs:
    if not src.is_dir():
        raise SystemExit("STOP_CACHE_SOURCE_MISSING")
    files = sorted(p for p in src.rglob("*") if p.is_file() and not p.is_symlink())
    if len(files) != expected:
        raise SystemExit("STOP_CACHE_SOURCE_COUNT")
    if dst.exists() and any(dst.rglob("*")):
        raise SystemExit("STOP_CACHE_TARGET_ALREADY_POPULATED")
    dst.mkdir(parents=True, exist_ok=True)
    for item in files:
        target = dst / item.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        with item.open("rb") as source, target.open("xb") as output:
            shutil.copyfileobj(source, output)
print("C2_CONTAINER_CACHE_SEED_PASS: tectonic=294 tiktoken=1")
'@
& docker @dc run --rm --no-deps --no-build --pull never -T --user 10001:10001 -v "$($SeedDir):/lab_seed:ro" ocr_router python -B -c $copyCode
if ($LASTEXITCODE -ne 0) { throw "STOP: cache no sembrada" }
~~~

Si la copia falla (montaje Windows, permisos, disco), **STOP**: no activar red, no sobrescribir. `--no-deps` evita volver a iniciar `db_bootstrap`; la imagen es la pinneada por Compose y no se permite build/pull.

### C.5. Generar fixture sintética nueva fuera de inbox

El generador `offline_pdf_lab._smoke_source` es código existente; se reutiliza en el nuevo volumen `data`. **Esta fixture puede no tener dos unidades PRESERVE/TRANSLATE como el C2 histórico**; no aplicar sus contadores como PASS obligatorio para este PDF.

~~~powershell
$fixtureCode = @'
from pathlib import Path
from hashlib import sha256
import sys
from apps.lab.offline_pdf_lab import _smoke_source
runid = sys.argv[1]
path = Path("/app/data/lab_fixtures") / ("smoke_" + runid + ".pdf")
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    raise SystemExit("STOP_FIXTURE_ALREADY_EXISTS")
_smoke_source(path)
data = path.read_bytes()
if not data.startswith(b"%PDF-"):
    raise SystemExit("STOP_FIXTURE_HEADER")
print("C2_FIXTURE_PATH:", path)
print("C2_FIXTURE_BYTES:", len(data))
print("C2_DOCUMENT_ID:", sha256(data).hexdigest())
'@
& docker @dc run --rm --no-deps --no-build --pull never -T --user 10001:10001 ocr_router python -B -c $fixtureCode $RunId
if ($LASTEXITCODE -ne 0) { throw "STOP: fixture no creada" }
$InsidePdf = "/app/data/lab_fixtures/smoke_$RunId.pdf"
~~~

**STOP si** no está vacío `/app/data/inbox` o si ya hay FSM con ese `document_id`. El OCR no debe reabrir generaciones completadas/incertidumbres para «probar otra vez»; ver bloque de auditoría RO en C.7 antes de tomar una decisión de reingesta.

### C.6. Arrancar fake y tres daemons de la ruta oficial

**[ARRANQUE OBSERVADO EN C2]:** fake healthy → OCR Router + G3 + G5. Reconciler/sweeper no se iniciaron en el positivo C2; son sujetos de pruebas focales de recovery.

~~~powershell
& docker @dc up -d --no-deps --no-build --pull never g3_fake
if ($LASTEXITCODE -ne 0) { throw "STOP: fake no iniciado" }
$fake = (& docker @dc ps -q g3_fake | Select-Object -First 1)
if (-not $fake) { throw "STOP: fake no localizado" }
$health = ""
for ($i = 0; $i -lt 30; $i++) {
    $health = (& docker inspect --format '{{.State.Health.Status}}' $fake).Trim()
    if ($health -eq "healthy") { break }
    Start-Sleep -Seconds 2
}
if ($health -ne "healthy") { throw "STOP: fake no saludable" }
& docker @dc up -d --no-deps --no-build --pull never ocr_router llm_worker assembler
if ($LASTEXITCODE -ne 0) { throw "STOP: daemons no iniciados" }
$running = @(& docker @dc ps --status running --services | Where-Object { $_ })
$expected = @("assembler", "g3_fake", "llm_worker", "ocr_router")
if (($running | Sort-Object) -join "," -ne ($expected | Sort-Object) -join ",") {
    throw "STOP: conjunto real de servicios no coincide con C2"
}
Write-Output "C2_DAEMONS_RUNNING_SET_PASS"
~~~

Para lectura de estados y logs acotados (sin imprimir env):

~~~powershell
& docker @dc ps -a
& docker @dc logs --tail 30 g3_fake ocr_router llm_worker assembler
~~~

**Cuatro servicios `running` no prueban resultado PDF.** No levantar `toxiproxy`/`fake-gemini` ni publicar puertos.

### C.7. Única admisión CLI, sin foreground ni repetición

**[PATRÓN EJECUTADO POR OWNER EN C2].** La CLI debe ejecutarse **en el contenedor OCR ya iniciado**, compartiendo realmente `/app/data/inbox` con los daemons. `--run` está prohibido para esta modalidad.

~~~powershell
& docker @dc exec -T ocr_router python -B -m apps.cli.main translate $InsidePdf --inbox-dir /app/data/inbox
if ($LASTEXITCODE -ne 0) { throw "STOP: admisión fallida, NO repetir" }
Write-Output "C2_CLI_ADMISSION_RETURNED (no significa COMPLETED)"
~~~

OCR sondea el inbox y archiva o envía a `error`; G3 procesa el `ChunkPlan` y G5 compila a PDF. **No repetir admisión** para forzar progreso. Leer FSM/receipts/logs del proyecto nuevo con los próximos bloques. Un HTTP 422 o `G3_EXTERNAL_UNKNOWN` obliga STOP sin segundo POST.
