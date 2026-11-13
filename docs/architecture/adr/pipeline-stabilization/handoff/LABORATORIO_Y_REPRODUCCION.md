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

**Antes del primer comando con escritura:** comprobar también que ningún objeto Docker tiene nombres calculados iguales pero carece de las etiquetas de Compose; reservar espacio y memoria efectivos, identificar fuente ZIP y cache, y registrar SHA de git e imagen. **Lecturas PowerShell útiles de presupuesto (sin modificar recursos):**

~~~powershell
Get-PSDrive -Name C | Select-Object Name,Used,Free
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory
docker info --format '{{.MemTotal}}'
docker system df
~~~

Las magnitudes deben interpretarse en sus unidades: RAM WMI en KiB, RAM Docker en bytes y espacio PowerShell en bytes. **No** ejecutar nuevas pruebas si el presupuesto de Docker Desktop es insuficiente para los límites del Compose. `docker compose config --quiet` no inicia contenedores; el preflight es **solo estático**. No publicar una salida completa de `config` con secretos.

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

**[RECETA NUEVA, ESCRITURA EN LOS NUEVOS VOLUMENES].** Docker Compose `run` no expone la opción `--no-build`: se usa `--no-deps --pull never`; en los tres YAML el preflight verifica que el servicio seleccionado tiene `build` eliminado e imagen local con `pull_policy: never`. La opción `--no-build` sí es válida en `compose up`. El override define `nocopy:true`, de modo que Tectonic/tiktoken no se copiarán solos. Se utiliza un contenedor efímero basado en `ocr_router` con su **comando reemplazado** (no inicia el daemon), con mount adicional **RO** del seed y usuario 10001. Rechazar destinos ya poblados.

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
& docker @dc run --rm --no-deps --pull never -T --user 10001:10001 -v "$($SeedDir):/lab_seed:ro" ocr_router python -B -c $copyCode
if ($LASTEXITCODE -ne 0) { throw "STOP: cache no sembrada" }
~~~

Si la copia falla (montaje Windows, permisos, disco), **STOP**: no activar red, no sobrescribir. `--no-deps` evita volver a iniciar `db_bootstrap`; la imagen es la pinneada por Compose y no se permite build/pull.

### C.5. Fixture mixta históricamente probada (PRESERVE + TRANSLATE)

**[GENERADOR PROBADO EL 2026-11-12, adaptado a un proyecto futuro].** La conversación y el [acta original](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837448665) contienen el generador del testigo automático, su `C2_AUTO_FIXTURE_PREFLIGHT_PASS` y exit 0. Produjo 4 nodos AST, 1 unidad PRESERVE, 1 TRANSLATE, 1544 bytes y SHA `28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f`. **El mismo escenario ya se probó** y luego recorrió los tres daemons hasta el PDF.

El código siguiente recupera el mismo diseño de PDF y las **mismas verificaciones de parser y plan** del testigo. Solo adapta el nombre del fichero a `/app/data/lab_fixtures/smoke_<RunId>.pdf` (referido en C.7–C.9). El nonce se genera nuevo, de modo que **no** se esperan los SHA históricos. El criterio de esta fase es **al menos un PRESERVE y un TRANSLATE/PARTIAL_TRANSLATE, comprobados con el parser real ANTES de admitir**. El generador `_smoke_source` queda para B03, no sustituye este falsador mixto C2. La variante de nombre futura no se ha ejecutado en otro RUN-ID.

~~~powershell
$fixtureCode = @'
from pathlib import Path
import hashlib, secrets, sqlite3, sys
import pymupdf
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.hashing import compute_ast_hash
from core.chunking.contextual_plan import prepare_contextual_plan
from core.validation.estimators import ExactBPEEstimator

runid = sys.argv[1]
inbox = Path("/app/data/inbox")
path = Path("/app/data/lab_fixtures") / ("smoke_" + runid + ".pdf")
fsm = Path("/app/state/db/fsm.db")
def check(value, reason):
    if not value:
        raise SystemExit("C2_AUTO_FIXTURE_BLOCKED:" + reason)
check(inbox.is_dir() and not list(inbox.glob("*.pdf")), "INBOX_NOT_EMPTY")
check(fsm.is_file(), "FSM_MISSING")
check(not path.parent.is_symlink(), "FIXTURE_DIR_SYMLINK")
path.parent.mkdir(parents=True, exist_ok=True)
check(not path.exists() and not path.is_symlink(), "SOURCE_ALREADY_EXISTS")
nonce = secrets.token_hex(12)
with pymupdf.open() as pdf:
    page = pdf.new_page(width=595, height=842)
    page.insert_text((147, 145), "Automatic Pipeline Witness", fontsize=20)
    page.insert_text((62, 210), "Scientific observations require careful and repeatable analysis.", fontsize=11)
    page.insert_text((62, 255), "Researchers examine evidence before reporting their conclusions.", fontsize=11)
    page.insert_text((62, 300), "This controlled laboratory fixture contains identifier " + nonce + ".", fontsize=11)
    pdf.save(str(path))

data = path.read_bytes()
check(data.startswith(b"%PDF-") and not path.is_symlink(), "INVALID_SOURCE")
document_id = hashlib.sha256(data).hexdigest()
with sqlite3.connect(fsm.as_uri() + "?mode=ro", uri=True) as db:
    db.execute("PRAGMA query_only=ON")
    previous = db.execute("SELECT COUNT(*) FROM document_fsm WHERE document_id=?", (document_id,)).fetchone()[0]
check(previous == 0, "PREEXISTING_FSM")
ast = build_extraction_pipeline().parse(str(path))
check(len(ast) >= 2, "INSUFFICIENT_AST")
plan = prepare_contextual_plan(document_id=document_id, raw_ast=ast, estimator=ExactBPEEstimator()).plan
ast_hash = compute_ast_hash(ast)
check(plan.ast_hash == ast_hash, "AST_HASH_DRIFT")
types = [getattr(u.chunk_type, "value", str(u.chunk_type)).lower() for u in plan.units]
preserve = sum(t == "preserve" for t in types)
translate = sum(t in ("translate", "partial_translate") for t in types)
print("SOURCE_PATH:", path)
print("DOCUMENT_ID:", document_id)
print("AST_HASH:", ast_hash)
print("PDF_BYTES:", len(data))
print("AST_NODES:", len(ast))
print("UNIT_TYPES:", types)
print("PRESERVE_UNITS:", preserve)
print("TRANSLATE_UNITS:", translate)
print("PREEXISTING_FSM_ROWS:", previous)
check(preserve >= 1, "NO_PRESERVE_UNIT")
check(translate >= 1, "NO_TRANSLATE_UNIT")
check(not list(inbox.glob("*.pdf")), "INBOX_CHANGED")
print("C2_AUTO_FIXTURE_PREFLIGHT_PASS")
'@
$fixtureCode | & docker @dc run --rm --no-deps --pull never -T --user 10001:10001 ocr_router python -B - $RunId
if ($LASTEXITCODE -ne 0) { throw "STOP: parser no acreditó fixture mixta; NO admitir" }
$InsidePdf = "/app/data/lab_fixtures/smoke_$RunId.pdf"
~~~

Este comando solo deja una fuente en `lab_fixtures`, fuera del inbox; no inicia OCR, G3 o G5 ni hace POST. **Ante un fallo no admitir ni sustituir silenciosamente por un PDF distinto.**

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

### C.7. Guardia obligatoria antes de admitir un PDF

**Este bloque debe ejecutarse después de C.6 y antes de C.8, ANTES de la primera admisión.** Comprueba identidad, ausencia de generación anterior, inbox vacío y SQLite ya inicializado, desde un **proceso RO separado**. El RUN-ID nuevo no basta por sí solo para demostrar que la fuente no tiene una fila previa.

~~~powershell
$guardCode = @'
from pathlib import Path
from hashlib import sha256
from contextlib import closing
import sqlite3
import sys
source = Path("/app/data/lab_fixtures") / ("smoke_" + sys.argv[1] + ".pdf")
if not source.is_file():
    raise SystemExit("STOP_FIXTURE_ABSENT")
document_id = sha256(source.read_bytes()).hexdigest()
inbox = Path("/app/data/inbox")
if not inbox.is_dir() or list(inbox.iterdir()):
    raise SystemExit("STOP_INBOX_NOT_EMPTY")
for name, query in (
    ("fsm.db", "SELECT COUNT(*) FROM document_fsm WHERE document_id=?"),
    ("queue.db", "SELECT COUNT(*) FROM chunk_plans WHERE document_id=?"),
):
    db = Path("/app/state/db") / name
    if not db.is_file():
        raise SystemExit("STOP_DB_MISSING:" + name)
    with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)) as conn:
        conn.execute("PRAGMA query_only=ON")
        count = conn.execute(query, (document_id,)).fetchone()[0]
        if count != 0:
            raise SystemExit("STOP_SOURCE_ALREADY_PRESENT_IN_" + name)
print("C2_PRE_ADMISSION_FRESH_GENERATION_PASS:", document_id)
'@
& docker @dc run --rm --no-deps --pull never -T --user 10001:10001 ocr_router python -B -c $guardCode $RunId
if ($LASTEXITCODE -ne 0) { throw "STOP: no se permite la admisión de C.8" }
~~~

**Interpretación:** este guard **no** crea ni modifica generación; solo verifica condiciones previas. Si falla, no enviar el PDF ni reactivar un proyecto con estado desconocido.

### C.8. Única admisión CLI, sin foreground ni repetición

**[PATRÓN EJECUTADO POR OWNER EN C2].** La CLI debe ejecutarse **en el contenedor OCR ya iniciado**, compartiendo realmente `/app/data/inbox` con los daemons. `--run` está prohibido para esta modalidad.

~~~powershell
& docker @dc exec -T ocr_router python -B -m apps.cli.main translate $InsidePdf --inbox-dir /app/data/inbox
if ($LASTEXITCODE -ne 0) { throw "STOP: admisión fallida, NO repetir" }
Write-Output "C2_CLI_ADMISSION_RETURNED (no significa COMPLETED)"
~~~

OCR sondea el inbox y archiva o envía a `error`; G3 procesa el `ChunkPlan` y G5 compila a PDF. **No repetir admisión** para forzar progreso. Leer FSM/receipts/logs del proyecto nuevo con los próximos bloques. Un HTTP 422 o `G3_EXTERNAL_UNKNOWN` obliga STOP sin segundo POST.

### C.9. Auditoría durable SQLite + PDF desde contenedor separado (RO)

**[AUDITOR PROPUESTO, NUEVO].** Reusar exactamente `$dc` y `$RunId` de C.1; ejecutarlo **sin volver a admitir**. Imprime FSM, plan, tareas, receipts, publicación/proyecciones y PDF. Si aún está procesando, devuelve `NOT_YET_COMPLETED_NO_REINGEST`: esperar dentro de un plazo acotado y **repetir únicamente esta lectura**. Una excepción, un PDF corrupto o `UNKNOWN` no son permiso para arrancar otra vez.

~~~powershell
$auditCode = @'
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import json
import sqlite3
import sys
import pymupdf

source = Path("/app/data/lab_fixtures") / ("smoke_" + sys.argv[1] + ".pdf")
if not source.is_file():
    raise SystemExit("STOP_SOURCE_MISSING")
document_id = sha256(source.read_bytes()).hexdigest()

def ro(name):
    p = Path("/app/state/db") / name
    if not p.is_file() or p.is_symlink():
        raise SystemExit("STOP_DB_MISSING:" + name)
    conn = sqlite3.connect(p.as_uri() + "?mode=ro", uri=True, timeout=8)
    conn.execute("PRAGMA query_only=ON")
    return conn

with closing(ro("fsm.db")) as fsm, closing(ro("queue.db")) as queue, closing(ro("materialized.db")) as mat:
    rows = fsm.execute(
        "SELECT ast_hash,current_state,state_version FROM document_fsm WHERE document_id=?",
        (document_id,),
    ).fetchall()
    print("FSM:", rows)
    if not rows:
        raise SystemExit("NOT_YET_COMPLETED_NO_REINGEST")
    if len(rows) != 1:
        raise SystemExit("STOP_GENERATION_AMBIGUOUS")
    ast_hash, state, version = rows[0]
    if state in ("FAILED_FATAL", "FAILED_RETRYABLE", "STALLED", "CANCELLED"):
        raise SystemExit("STOP_DOCUMENT_STATE_" + state)
    plans = queue.execute(
        "SELECT manifest_json,manifest_sha256 FROM chunk_plans WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchall()
    if not plans:
        raise SystemExit("NOT_YET_COMPLETED_NO_REINGEST")
    if len(plans) != 1:
        raise SystemExit("STOP_PLAN_AMBIGUOUS")
    plan = json.loads(plans[0][0])
    units = {u["chunk_id"]: u["chunk_type"] for u in plan["units"]}
    if len(units) != len(plan["units"]):
        raise SystemExit("STOP_CHUNK_ID_COLLISION")
    tasks = queue.execute(
        "SELECT worker_type,node_id,task_state FROM chunk_tasks WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchall()
    receipts = queue.execute(
        "SELECT chunk_id,raw_response IS NULL FROM chunk_result_receipts WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchall()
    publication = mat.execute(
        "SELECT manifest_sha256,projection_version FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchall()
    projections = mat.execute(
        "SELECT COUNT(*) FROM valid_chunks_cache WHERE document_id=? AND ast_hash=?",
        (document_id, ast_hash),
    ).fetchone()[0]
    print("IDENTITY:", document_id, ast_hash, plans[0][1])
    print("UNITS:", units)
    print("TASKS:", sorted(tasks))
    print("RECEIPTS (chunk, raw_response_is_null):", sorted(receipts))
    print("PUBLICATIONS:", publication)
    print("PROJECTIONS:", projections)
    if any(t[2] == "G3_EXTERNAL_UNKNOWN" for t in tasks):
        raise SystemExit("STOP_G3_EXTERNAL_UNKNOWN_NO_RETRY")
    if state != "COMPLETED":
        raise SystemExit("NOT_YET_COMPLETED_NO_REINGEST")

pdf_path = Path("/app/output") / ("translated_" + document_id + ".pdf")
if not pdf_path.is_file() or pdf_path.is_symlink():
    raise SystemExit("STOP_OUTPUT_MISSING")
pdf_bytes = pdf_path.read_bytes()
if not pdf_bytes.startswith(b"%PDF-"):
    raise SystemExit("STOP_INVALID_PDF_HEADER")
with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
    pages = len(pdf)
    has_text = any(isinstance(t, str) and bool(t.strip()) for t in (p.get_text() for p in pdf))
if pages < 1 or not has_text:
    raise SystemExit("STOP_PDF_STRUCTURE")
if not tasks or any(t[2] != "COMPLETED" for t in tasks):
    raise SystemExit("STOP_TASKS_NOT_COMPLETED")
if len(receipts) != len(units) or len(publication) != 1 or projections < 1:
    raise SystemExit("STOP_G3_DURABILITY_NOT_COMPLETE")
if publication[0][0] != plans[0][1]:
    raise SystemExit("STOP_PUBLICATION_MANIFEST_DRIFT")
print("PDF:", pdf_path, "bytes:", len(pdf_bytes), "pages:", pages,
      "text:", has_text, "sha256:", sha256(pdf_bytes).hexdigest())
print("C2_NEW_GENERATION_SQLITE_AND_PDF_AUDIT_PASS")
'@
& docker @dc run --rm --no-deps --pull never -T --user 10001:10001 ocr_router python -B -c $auditCode $RunId
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Auditoría NO PASS: clasificar FSM, tasks y logs antes de decidir"
}
~~~

### C.9 bis. Oráculo exacto por identidades, además del auditor C.9

**[COMPLEMENTO ESTÁTICO DERIVADO DEL CONTRATO ACTUAL].** Se ejecuta **solo después de un C.9 exitoso**: comprueba que los receipts correspondan exactamente a los `chunk_id` del plan, que las tareas incluyan una LLM por chunk y una ASSEMBLER, y que el conjunto de `node_id` de `valid_chunks_cache` coincida con los miembros del plan. Es una consulta RO y no vuelve a admitir ni llamar a G3.

~~~powershell
$coverageCode = @'
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import json, sqlite3, sys

source = Path("/app/data/lab_fixtures") / ("smoke_" + sys.argv[1] + ".pdf")
if not source.is_file(): raise SystemExit("STOP_SOURCE_MISSING")
doc = sha256(source.read_bytes()).hexdigest()
def ro(name):
    p = Path("/app/state/db") / name
    c = sqlite3.connect(p.as_uri() + "?mode=ro", uri=True, timeout=8)
    c.execute("PRAGMA query_only=ON")
    return c
with closing(ro("fsm.db")) as fsm, closing(ro("queue.db")) as q, closing(ro("materialized.db")) as mat:
    rows = fsm.execute("SELECT ast_hash,current_state FROM document_fsm WHERE document_id=?", (doc,)).fetchall()
    if len(rows) != 1 or rows[0][1] != "COMPLETED": raise SystemExit("STOP_NOT_COMPLETED")
    ast = rows[0][0]
    plans = q.execute("SELECT manifest_json,manifest_sha256 FROM chunk_plans WHERE document_id=? AND ast_hash=?", (doc,ast)).fetchall()
    if len(plans) != 1: raise SystemExit("STOP_PLAN_NOT_UNIQUE")
    plan = json.loads(plans[0][0])
    body = {k:v for k,v in plan.items() if k != "manifest_sha256"}
    digest = sha256(json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
    if digest != plans[0][1] or digest != plan.get("manifest_sha256"): raise SystemExit("STOP_PLAN_HASH")
    units = plan["units"]
    chunks = [u["chunk_id"] for u in units]
    nodes = {m["node_id"] for u in units for m in u["members"]}
    if not chunks or len(chunks) != len(set(chunks)) or not nodes: raise SystemExit("STOP_PLAN_COVERAGE")
    kinds = {u["chunk_id"]:u["chunk_type"] for u in units}
    receipts = q.execute("SELECT chunk_id,raw_response IS NULL FROM chunk_result_receipts WHERE document_id=? AND ast_hash=?", (doc,ast)).fetchall()
    tasks = q.execute("SELECT worker_type,node_id,task_state FROM chunk_tasks WHERE document_id=? AND ast_hash=?", (doc,ast)).fetchall()
    pubs = mat.execute("SELECT manifest_sha256,result_sha256,projection_version FROM g3_plan_publications WHERE document_id=? AND ast_hash=?", (doc,ast)).fetchall()
    projections = mat.execute("SELECT node_id,content_hash,normalized_response,normalized_hash,projection_version FROM valid_chunks_cache WHERE document_id=? AND ast_hash=?", (doc,ast)).fetchall()
    if len(receipts) != len(chunks) or {x[0] for x in receipts} != set(chunks): raise SystemExit("STOP_RECEIPT_COVERAGE")
    for chunk,raw_null in receipts:
        if bool(raw_null) != (kinds[chunk] == "preserve"): raise SystemExit("STOP_RECEIPT_POLICY")
    expected_tasks = {("LLM",chunk,"COMPLETED") for chunk in chunks} | {("ASSEMBLER","ROOT_ASSEMBLY","COMPLETED")}
    if len(tasks) != len(expected_tasks) or set(tasks) != expected_tasks: raise SystemExit("STOP_TASK_COVERAGE")
    if len(pubs) != 1 or pubs[0][0] != digest or pubs[0][2] != 1: raise SystemExit("STOP_PUBLICATION_IDENTITY")
    if len(projections) != len(nodes) or {p[0] for p in projections} != nodes: raise SystemExit("STOP_NODE_COVERAGE")
    for node,source_hash,content,normalized_hash,version in projections:
        if (version != 1 or not isinstance(source_hash,str) or len(source_hash) != 64
                or normalized_hash != sha256(content.encode("utf-8")).hexdigest()):
            raise SystemExit("STOP_PROJECTION_HASH_VERSION")
    print("C2_EXACT_COVERAGE_PASS", "chunks",len(chunks),"nodes",len(nodes))
'@
$coverageCode | & docker @dc run --rm --no-deps --pull never -T --user 10001:10001 ocr_router python -B - $RunId
if ($LASTEXITCODE -ne 0) { throw "STOP: cobertura por identidad no coincide" }
~~~

**Alcance:** verifica conjuntos de identidades, versión v1 y SHA de contenido normalizado, pero **no** reconstruye el `result_sha256` de publicación con el AST completo ni prueba semántica lingüística. Esa diferencia frente a una auditoría completa del protocolo queda explícita. `PRESERVE` con respuesta nula se verifica aquí y la ausencia de POST para esa unidad se prueba por separado con el fake en C.10.

**Alcance del oráculo:** validación estructural y durable, no cobertura científica. `COMPLETED`, receipt y PDF real pueden coexistir con traducción fake. El testigo C2 histórico tenía 4 nodos, 2 unidades y 4 proyecciones; **no** exigir esos números a una fixture distinta. Para una prueba mixta deberá añadirse además una aserción por `chunk_id`: `PRESERVE` con `raw_response NULL` y **cero POST** asociado.

### C.10. Conteo HTTP fake independiente de SQLite

**[CÓDIGO / OBSERVADO EN C2]:** el fake escribe una línea JSON compacta para cada `G3_FAKE_POST_ATTEMPT`, `G3_FAKE_REQUEST_ACCEPTED` o `G3_FAKE_REQUEST_REJECTED`. El recuento de POST **no se infiere de receipts ni de un `logs --tail`**. El siguiente comando inspecciona los **logs completos del fake de este proyecto nuevo**; no imprimir el cuerpo del prompt ni env.

~~~powershell
$fakeLogs = @(& docker @dc logs --no-color g3_fake 2>&1 | ForEach-Object { $_.ToString() })
if ($LASTEXITCODE -ne 0) { throw "STOP: logs fake inaccesibles" }
$attempts = @($fakeLogs | Select-String -SimpleMatch '"event":"G3_FAKE_POST_ATTEMPT"').Count
$accepted = @($fakeLogs | Select-String -SimpleMatch '"event":"G3_FAKE_REQUEST_ACCEPTED"').Count
$rejected = @($fakeLogs | Select-String -SimpleMatch '"event":"G3_FAKE_REQUEST_REJECTED"').Count
Write-Output "C2_HTTP_ATTEMPTS=$attempts; ACCEPTED=$accepted; REJECTED=$rejected"
$fakeLogs | Select-String -SimpleMatch '"event":"G3_FAKE_REQUEST_ACCEPTED"'
if ($rejected -ne 0) { throw "STOP: fake rechazó algún POST" }
~~~

Para una ejecución **fresca con fake no reiniciado**, la cardinalidad esperada de HTTP aceptados se obtiene de las unidades `translate`/`partial_translate` del plan **no de la cantidad de receipts** (PRESERVE no hace POST). `attempts != accepted`, varios POST para la misma unidad, ausencia de aceptación con unidades TRANSLATE, o identidad inesperada de `document_id`/`ast_hash`/`manifest_sha256`/`chunk_id` = **STOP y auditoría, sin reingesta**. Este bloque **no** presume que la nueva fixture contenga dos tipos de unidades.

**Referencia original C2, NO ORÁCULO DE NUEVA FIXTURE:** fuente 1544 bytes SHA `28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f`; AST `b0b4cb12ea5e2a871a8789e5228e428b10eca04380e5a95503ff4f61c89f9c4a`, manifiesto `7724718fd66aff7b570f70a1dad828b2d3391abd14c47ef32fd12fb4a487229d`; una PRESERVE + una TRANSLATE, un POST 200, dos receipts, una publicación, 4 proyecciones, FSM COMPLETED v7 y PDF 7050 bytes SHA `71f209255c923daef84e44e1ae1bf642dfe5270e862eadedb0709b94ee62bfe3`. [Acta íntegra C2](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200).

### C.11. Detener, preservar y limpiar solo recursos nuevos

Después del PASS o de cualquier STOP, **no lanzar otra admisión**. Guardar primero resultados, IDs, stdout, logs saneados, timestamp UTC, SHA de la fuente/AST/plan/PDF, estados/receipts y presupuesto usado. Para una snapshot SQLite con `-wal`/`-shm`, **no copiar un .db aislado mientras hay escritores**; usar mecanismo consistente autorizado.

~~~powershell
# Solo el proyecto $Project de ESTA corrida. No incluir proyectos históricos.
& docker @dc stop ocr_router llm_worker assembler g3_fake
if ($LASTEXITCODE -ne 0) { throw "STOP: comprobar escritores antes de limpiar" }
& docker @dc ps -a
~~~

**Dos opciones de custodia distintas:**

- **Preservar** (predeterminado): dejar los volúmenes con su RUN-ID; no volver a usar ese RUN-ID.
- **Retirar SOLO la nueva corrida con aprobación expresa:** después de archivar evidencia y confirmar que no aloja otra generación, `docker compose down` **sin `-v`** puede retirar contenedores/red del proyecto **dejando volúmenes**. Para eliminar cada uno de esos seis volúmenes haría falta validación de pertenencia, lista explícita y aprobación; **este runbook no proporciona un borrado general de volúmenes**. No tocar `tpdfconvconv1211b`, laboratorio R2/C-L1 ni `G3_EXTERNAL_UNKNOWN` histórico. `$SeedDir` puede eliminarse únicamente tras confirmar que su contenido ya no es evidencia necesaria.

**El host `%TEMP%` del launcher B03 es un mecanismo diferente:** `--run-smoke` retiene workspace y PDF exportado; T07 elimina su scratch al salir normalmente. No aplicar la misma limpieza a los tres laboratorios.

## 7. D — Comparación foreground T07 frente al C2 original

**T07 NO es un runner reutilizable para nuevos RUN-ID:** `apps/lab/t07_foreground_compare.py` tiene fijados por código el proyecto `tpdfconvconv1211b`, la fixture `/app/data/c2_auto_fixtures/c2_auto_7bde7a829408de26521dc0d5.pdf` y sus SHA. Exige **exactamente cuatro servicios** en funcionamiento: `assembler`, `g3_fake`, `llm_worker` y `ocr_router`, y que OCR aún conserve esa fixture. No recrear el proyecto histórico para satisfacerlo.

~~~powershell
# Solo para el sujeto histórico intacto con sus precondiciones presentes:
python -B -m apps.lab.t07_foreground_compare
if ($LASTEXITCODE -ne 0) { throw "STOP: consultar T07_STOP; no reconstruir C2 antiguo" }
~~~

**[OBSERVADO 2026-11-12, owner Windows]:** `T07_FOREGROUND_CONTRACT_EQUIVALENCE_PASS`, `T07_TEMP_WORKSPACE_CLEANUP_PASS` y `C3_T07_FOREGROUND_ISOLATED_PASS`, exit 0; un contenedor `docker run --rm --pull never --network none`, sin nuevos volúmenes Docker, fake de loopback y checkout RO. Copió la fuente 1544 bytes de C2, recuperó el mismo AST/manifest, receipts y proyecciones, un POST TRANSLATE y un PDF físico de 7050 bytes SHA `9f70c22525358f7134020ad1ef511067037eca35cfe6636acd2494178a5325b4`. Diferente al hash de C2 (convergen **contratos**, no bytes idénticos). El workspace temporal T07 se elimina cuando termina normalmente; no atribuirle la retención de B03.

Para nueva prueba foreground usar **`offline_pdf_lab --run-smoke` o `--run-pdf`** en un workspace nuevo según `5`. No añadir un falso parámetro de RUN-ID a T07: su script **no lo soporta**.

## 8. E — Falsadores de recuperación/G5, sin ejecutar otro laboratorio

La misma arquitectura incluye `ReconcilerDaemon` y `RecoveryDaemon`, pero **no** formaron parte de los cuatro servicios del C2 positivo. Sus pruebas deben hacerse con SQLite de test y recursos acotados, no con SIGKILL sobre contenedores históricos.

**G3 y efecto remoto incierto:** la unidad `PRESERVE` genera receipt sin `raw_response` ni POST. Una unidad `TRANSLATE` exige plan/contexto verificados antes de llamar al proveedor. `RESULT_STAGED` puede publicarse/reconciliarse desde otro proceso **sin segundo efecto externo**; `G3_EXTERNAL_UNKNOWN` se mantiene en cuarentena y no es runnable. El test T05 provocó `os._exit(73)` en un subprocess y comprobó reapertura/finalización desde otro, no reinicios exhaustivos de OCR y todos los daemons.

**G5 y crash entre archivos/DB:** `AssemblyLeaseRepository.publish` toma autoridad fenced, compila un PDF a ruta privada `.assembly_<uuid>.pdf` y hace `os.replace` antes del COMMIT SQLite (con FSM adjunta). Si el proceso muere en esa ventana, el fichero físico podría existir mientras FSM no está `COMPLETED`. El G5/2 anterior acreditó dos SIGKILL y recuperación sobre **otra imagen y fixtures sintéticas**, no todas las ventanas del C2 actual. No importar su imagen/TAR grande ni ejecutar sus scripts one-shot sobre volúmenes vigentes. Ante `FAILED_RETRYABLE`/task `FAILED` por error normal, **no** asumir reintento automático universal; clasificar y requerir autoridad.

**Tests focales — ejecutar solo los necesarios**, desde raíz del repo y sin Docker, con venv compatible:

~~~powershell
# Configuración C0, volumen nuevo y bootstrap
python -B -m pytest -q tests/unit/test_convergence_compose_preflight.py tests/unit/test_convergence_db_bootstrap.py -p no:cacheprovider

# Foreground, aislamiento y fake
python -B -m pytest -q tests/unit/test_b032_offline_pdf_lab.py -p no:cacheprovider

# Recuperación G3 entre procesos
python -B -m pytest -q tests/integration/test_c3_t05_process_boundary.py -p no:cacheprovider

# G3 externo incierto y publicación desde staging
python -B -m pytest -q tests/integration/test_w06_g3_uncertain_effect_offline.py tests/integration/test_g3_b4_3b_publication_recovery.py -p no:cacheprovider

# G5 lease/rollback, contexto OCR→G3
python -B -m pytest -q tests/integration/test_g5_assembler_lease_recovery.py tests/integration/test_w08_ocr_g3_context_wiring.py -p no:cacheprovider

# Rutas productivas y CLI
python -B -m pytest -q tests/unit/test_c4_t06_supported_roots.py tests/integration/test_cli_router.py -p no:cacheprovider
~~~

Estos son comandos de test, **no afirmaciones de PASS del nuevo HEAD**. Un test que cambie por contrato debe revisarse junto al [Atlas](ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) y los NADR FROZEN. No correr el CI científico completo ni modificar B02/corpus para una prueba de composición.

## 9. Diagnóstico rápido y política STOP

| Síntoma | Causa o riesgo probable | Acción permitida |
|---|---|---|
| `C0_T01_BLOCKED/FAIL` | Compose, imagen, mounts, red o credenciales no cumplen el contrato | STOP sin iniciar recursos; revisar reason code |
| Imagen local o ZIP no coinciden | El sujeto offline de referencia cambió | STOP; no descargar ni usar TAR G5 como sustituto |
| `db_bootstrap` no termina `exited 0` | Inicialización, ownership, DDL, mount, permisos | Preservar logs/DB; NO repetir bootstrap |
| No se puede sembrar cache | Volumen no vacío, ownership, Docker Desktop bind, falta ZIP | STOP; no sobrescribir/no habilitar egress |
| `g3_fake` no healthy | queue.db ausente, opt-in, mount RO o servicio errado | NO arrancar G3 |
| OCR ignora PDF | Inbox diferente, poll, deduplicación, parser B02, error de perfil | Inspeccionar `data/archive`, `data/error`, queue/FSM y logs sin reingesta |
| `B02_UNREPRESENTED_VECTOR_DRAWING` | Región vectorial no representable con seguridad | Rechazo correcto; no silenciar extractor |
| Fake 422 / intentos duplicados | URL/protocolo/plan/manifest equivocados o efecto incierto | STOP, preservar logs; no repetir POST |
| `G3_EXTERNAL_UNKNOWN` | Se desconoce resultado externo y está cuarentenado | STOP definitivo sin disposición autorizada |
| `READY_FOR_ASSEMBLY` sin PDF | Worker G5, cache, lease, proyección o payload | Inspeccionar tarea/estado/caché; no segundo ensamblador competitivo |
| PDF existe, FSM no COMPLETED | Posible ventana `os.replace` ↔ COMMIT SQLite | No declarar PASS, conservar PDF y DB/WAL |
| FSM COMPLETED pero PDF incorrecto | Estado lógico no garantiza estructura/calidad | FAIL material; revisar PDF sin tocar FROZEN |
| `B032_EXPORT_ALREADY_EXISTS` | Launcher protege PDF exportado de sobrescritura | Nuevo destino autorizado; no borrar evidencia |
| Disco/RAM insuficientes | Riesgo de degradar Docker Desktop o volúmenes | STOP; no `prune` ni reconstrucciones automáticas |

## 10. Registro obligatorio y mantenimiento futuro del laboratorio

**Una corrida nueva se considera observada, no «automáticamente acreditada» por leer este manual.** Capturar en el acta propia:

| Campo | Debe registrarse |
|---|---|
| Sujeto | SHA de código, hora UTC, Windows/Docker/Compose/Python, imagen ID exacta |
| Aislamiento | RUN-ID nuevo, proyecto, red interna, volúmenes, mounts RO/nocopy, ausencia de puertos |
| Recursos | Disco y RAM antes/después; presupuesto, creaciones y desvíos |
| Cache | ZIP SHA, archivos Tectonic/tiktoken, rutas, ownership; sin restauración de SQLite histórico |
| Entrada | PDF autorizado, tamaño/SHA, `document_id`, `ast_hash`, `manifest_sha256` y unidades |
| Procesos | exit code bootstrap, fake health, OCR/G3/G5 ejecutándose por separado |
| Persistencia | FSM+versiones, tareas, receipts, publicación, proyecciones, fencing |
| HTTP | Todos los POST del fake (intentos, aceptados, rechazados), identidad exacta y **cero PRESERVE** |
| PDF | Path, cabecera, páginas, texto extraíble, bytes y SHA; correlación con FSM |
| Fallos | Código STOP, no reingesta, registros preservados, limpieza/acceso a volúmenes |
| Alcance | Diferenciar PASS de topología con fake de traducción real/W09/product readiness |

**Qué sabemos del ensayo original [OBSERVADO 2026-11-12]:** C0–C4 y DoD 9/9 acreditados con fake, OCR/G3/G5 independientes, un POST de `TRANSLATE` aceptado, cero a `PRESERVE`, PDF físico Tectonic, recuperación focal T05 y comparación T07. Ver [actas del PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46) y [evidencia final](EVIDENCIA_Y_CIERRE.md).

**Qué NO sabemos todavía para la receta nueva de `6`:** no se ha ejecutado aquí su orquestación completa sobre **un RUN-ID fresco** (incluidos bind Windows, extracción, ownership, contenedores, auditor/HTTP). Por eso **no** se publica `C2_REPRODUCIBLE_FROM_ZERO_PASS` ni se promete que una modificación futura se pruebe sin nuevos ajustes. La receta sí contiene las precondiciones, comandos derivados del código y criterios STOP/PASS necesarios para que no haya que redescubrir la arquitectura. Si el owner la valida una vez en entorno descartable, registrar exactamente el HEAD, los comandos ejecutados, el tiempo/espacio y las correcciones realizadas antes de elevarla a procedimiento acreditado.

**Política de mantenimiento:** este mismo runbook se actualiza con cada cambio de Compose, bootstrap, proveedor fake, fixture o evidencia; no restaurar manuales R2/C-L1/G5 antiguos ni crear documentos de sandbox paralelos. El Atlas sigue siendo la autoridad descriptiva de la ruta y el cierre sigue siendo el documento de evidencia de la convergencia.

**Fin del procedimiento.**
