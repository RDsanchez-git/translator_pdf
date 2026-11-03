# Sandbox de auditoría PDF→PDF — Gobernanza y guía operativa

**Versión de esta guía:** 0.1.0 (2026-11-03)  
**Estado:** `DRAFT — RUNBOOK DE REFERENCIA / REVISIÓN DEL OWNER PENDIENTE`  
**Ámbito:** `RDsanchez-git/translator_pdf`, rama `pipeline_stabilization`, investigación `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` `IN_PROGRESS`.  
**Sujeto probado:** R2, variante **C/L1 escalonada**, `RUN-ID=9cf15cac6b12`, proyecto `i0l19cf15cac6b12`, imagen local histórica R2.  
**Sujetos NO acreditados por esta guía:** R1 y R3, R2 concurrente AS-IS, segunda máquina, proveedor real, recuperación/fencing bajo fallo.  
**Carácter:** documento operativo descriptivo y de control de cambios. **No** modifica ni aprueba el Charter v0.1.0 `DRAFT`, los NADR `FROZEN`, D-1…D-7, el Atlas ni los criterios de un ensayo ya ejecutado. No autoriza por sí solo una nueva corrida.

> **Regla esencial.** El **sandbox** es la infraestructura y el protocolo seguro para examinar rutas; **no** es una ruta PDF→PDF adicional, una implementación nueva del traductor ni la futura arquitectura canónica. Se reutiliza el perímetro demostrado, y se verifican las diferencias indispensables de cada ruta. **No se crean tres sandboxes por haber tres rutas.**

## 0. Cómo utilizar esta guía y qué tan completa es

**Dos niveles de reproducibilidad.** Esta guía describe íntegramente **el estado conocido, la configuración del C/L1 ejecutado, los controles y las operaciones permitidas/prohibidas**. Un operador puede auditar ese estado y reconocer qué artefactos debe exigir antes de cualquier lanzamiento. Sin embargo, **no es un paquete universal autocontenido listo para ejecutar**: el manifest exacto y el fake se conservan en el ZIP local C/L1; los scripts P0–P5 son históricos y llevan codificados RUN-ID, hashes y precondiciones de la corrida finalizada. **No deben volver a ejecutarse** ni servir directamente para R1/R3. El apartado 14 registra esta deuda de *empaquetado*, sin proponer nuevos servicios ni una refactorización del producto.

**Fuente de verdad por tipo:** contrato normativo `FROZEN` vigente, si aplica → Charter/Atlas indicando su estado exacto → commit e imagen/verificación del código → manifests y scripts identificados por bytes → recibos y PDF/SQLite de la corrida → actas acotadas e inferencias explícitas. Un `DRAFT` no se convierte en `FROZEN` por estar citado. Las instantáneas antiguas conservan su fecha y no se reescriben retrospectivamente.

**Audiencia:** owner/operador Windows PowerShell, investigador de rutas, revisor de evidencia y Architecture Board cuando corresponda. **No ejecuta nada al abrirse.**

### 0.1 Decisión rápida

| Pregunta | Respuesta válida hoy |
|---|---|
| ¿Existe un perímetro seguro ya probado en esta PC? | **Sí, dentro del alcance C/L1 R2 escalonado** y de las sondas focales D1. |
| ¿Hay un sandbox único genérico listo para R1, R2 y R3 con un solo comando? | **No acreditado.** Falta revisar diferencias de entrypoints, dependencias y composición de R1/R3. |
| ¿Hay que repetir P0–P5 para demostrar que el sandbox existió? | **No.** La evidencia histórica está custodiada; no reiniciar el producto. |
| ¿El éxito físico A prueba el mejor traductor o fidelidad matemática? | **No.** R2 tuvo `scientific_verdict=FAIL`. |
| ¿Debe ampliarse la infraestructura ahora? | **No**, salvo bloqueo preciso, justificado y autorizado. |
| ¿Puede alguien ejecutar un nuevo ensayo leyendo solo este MD? | Puede completar inspecciones y preparar un protocolo; **no debe arrancar** sin manifest exacto, runner revisado para un RUN-ID fresco, evidencias previas y autorización específica. |

## 1. Propósito, límites y separación de sujetos

El propósito de L0/HV es disponer de un **perímetro de pruebas aislado y medible** que impida contaminar el checkout, corpus, artefactos históricos, volúmenes ajenos o credenciales reales. L1/E2E-0 **caracteriza** una ruta PDF→PDF existente. L2 discrimina causas de fallos; la posterior convergencia arquitectónica decide una sola ruta de producto. **Son fases con objetivos diferentes.**

| Sujeto | Naturaleza | Evidencia permitida | Prohibición de inferencia |
|---|---|---|---|
| A / AS-IS | Código + Compose/CLI original; fingerprint propio. | Mapa estático y, si existe, observación dinámica de A. | Equiparar C escalonado a concurrencia o configuración AS-IS. |
| B / D1 HV | Arnés de verificación `i0hv49cde367de`, sin PDF real; objetos `created`, seis volúmenes de nombre **literal**. | Seguridad limitada, SDK/fake, permisos, composición inspeccionada, WAL sintético. | Usarlo como segundo proyecto L1: los nombres de volúmenes pueden colisionar. |
| C / L1 R2 | Arnés con recursos **por RUN-ID**, seed offline y fases P0–P5. | Testigo real PDF→PDF escalonado y custodia, dentro de su configuración. | Presentarlo como R1, R3, R2 concurrente o garantía universal. |

**La política de reutilización es *reuse-first*:** una imagen existente, una familia de controles de aislamiento, y diferencias documentadas por ruta. **YAGNI:** no implementar fake nuevo, backend, proxy, microservicio, Kubernetes, Redis, nueva imagen, caché duplicada o arreglo funcional para mejorar el resultado durante la caracterización.

## 2. Estado histórico y línea base congelada

| Objeto | Identidad acreditada en el ensayo R2 |
|---|---|
| Código funcional ejecutado | Commit `d4cda2c379c0efd93a70e795d31c37a0ede7a192` ; tree `f2a635ef8822780698066a288e46607c8b671938`. |
| Rama del repositorio al publicar esta guía | `pipeline_stabilization`; posteriores commits **documentales** no alteran retrospectivamente el código de R2. Comparar trees antes de atribuir igualdad. |
| Imagen R2 local | `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`. |
| Tag local de esa imagen | `i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824`. El **ID**, no solo el tag, es la autoridad. |
| Plataforma | Docker Desktop Linux, contexto `desktop-linux`, Linux/amd64; cliente de operaciones Windows PowerShell y Python local. |
| D1/HV | Proyecto `i0hv49cde367de`; **conservar intacto**, composición con seis nombres globales fijos. |
| C/L1 | Proyecto `i0l19cf15cac6b12`; RUN-ID `9cf15cac6b12`; red `i0l19cf15cac6b12_internal`; cinco contenedores de producto detenidos tras las fases. |
| PDF canónico probado | `tests/corpus/canonical/pdf/doc_01_single.pdf`; `531778` bytes; SHA-256 `2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3`; 3 páginas. |
| PDF final R2 | `translated_2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3.pdf`; `20900` bytes; 4 páginas; SHA-256 `8c9f81dfcc2cfc200211894bad65a46bdd82fa45c36a9bfee1a1d454ce2d6c47`. |
| ZIP P5 custodiado | `P5_C_L1_R2_9cf15cac6b12_EVIDENCE_RO.zip`, `596525` bytes, SHA-256 `b1fe0603732493cdacc749c116c9694be53061eef5d40fa9d1315cfafd1bb65f`. No subir el corpus ni SQLite completos automáticamente. |

**Resultados:** P0–P4 `PASS` por fase, P5 V3 `PASS_EXPORT_ONLY`, `execution_outcome=A` (PDF físico válido), `scientific_verdict=FAIL` (pérdida matemática), `contract_verdict` integral `UNKNOWN`, `product_readiness=NOT_DEMONSTRATED`. El fake devolvió 59/59 fragmentos `translate` **idénticos** a la fuente; no acredita traducción lingüística. `event.chunk_events_log=0` y `queue.chunk_result_receipts=5`: **CP-08 del journal permanece `UNKNOWN`**.

## 3. Artefactos técnicos y su procedencia

### 3.1 Composición y fake histórico: fuente exacta

**Paquete existente del owner:** `L0_C_L1_R2_STATIC_CANDIDATE_REVIEW_ONLY_20261102.zip`; SHA-256 `cac669746a31fda07ce7b0f3f5862993292db20b108455ac5521181fdc7fb527`. Contiene:

| Miembro ZIP | SHA-256 del contenido | Rol |
|---|---|---|
| `compose.c.L1_REVIEW_ONLY.yaml` | `055034fa86aebaf7c147992e11d0e69ce18afb4fc39ba7648143a130a2b3d0c4` | Manifest completo R2 de cinco servicios, red y seis volúmenes. |
| `G3C_CONTRACT_GATE_FBF166B_R0.py` | `6d003daf9a44a36b8c12e2b7ad4f33edd3a8470221e42c38bae4e97fdc0b53a5` | Fake Groq determinista. |
| `C_L1_REVIEW_AND_HOLD.md` | `a504951ca2e3cfe9d78bf1e105e04f642cdf32d51e57115c80873a4829522854` | Revisión estática y limitaciones previas a la corrida. |
| `C_L1_STATIC_REVIEW_REPORT.json` | `d37392e929f94dc692f3376c579dd0fb7e837882b256fd6e33ef91b4f13a32ab` | Inventario estático del candidato. |
| `SHA256SUMS.txt` | `3a63592e24c83c8122b4b0bccb74a40546efd6d73a6867c29491d808dd55856e` | Sumas de los miembros del paquete. |

**NOTA DE SEGURIDAD:** en la fuente histórica aparece el perfil `l1-hold` y etiquetas `CANDIDATE_HOLD_NOT_AUTHORIZED`. El perfil es un obstáculo accidental de arranque, **no un permiso de seguridad**. No convertir `--profile l1-hold` en autorización. La ejecución C/L1 posterior tuvo autorizaciones P0–P5 expresas, pero el YAML histórico no se convierte por ello en una receta futura universal.

### 3.2 Ejecutores históricos: identificados y no reutilizables directamente

| Fase | Ejecutable usado | SHA-256 |
|---|---|---|
| P0 | `P0_C_L1_R2_APROVISIONAMIENTO_OFFLINE_CONTROLADO_20261103.py` | `59c84d7a5f3a39cf5d15150957c9593f186b663c264d900d6497d45fe1f44b86` |
| P1 | `P1_C_L1_R2_BOOTSTRAP_UNA_SOLA_EJECUCION_20261103.py` | `83eded4446465cbe326411a9207864a95f812b4508e958e0121388cdb786c4c2` |
| P2 | `P2_C_L1_R2_OCR_RECUPERACION_PRECHECK_V2_20261103.py` | `89167f82e4e3bd8add4c9e7a916b7a7f3f56e8fdfbde85a08aad457c9e1a88f9` |
| P3 | `P3_C_L1_R2_ENGINE_FAKE_EJECUCION_UNICA_20261103.py` | `0281b0241755b6bac534273a444dd6d4d4d27c62b7eaf35c454e6ceda5e9d84b` |
| P4 | `P4_C_L1_R2_ASSEMBLER_UNICO_CONTROLADO_20261103.py` | `0db5f0968b96707bc5072ff816dcf8ca6640ee5be3c65111b527f0da8cad91bf` |
| P5 | `P5_C_L1_R2_CUSTODIA_EXPORT_RO_V3_20261103.py` | `eaa4c9d3936e3bb71ec64451d63a69dadf4cb6cbd68f5e016f1fcfdae13e9964` |

V1 de P2 fue detenido en preflight por la comprobación SQLite, **sin iniciar OCR**; V1/V2 de P5 tuvieron STOP instrumentales antes de la exportación correcta. No reescribir los incidentes; no reintentar los scripts históricos ni `--apply` sobre el mismo RUN-ID. **Cualquier ensayo nuevo necesita una instancia/hashes/recibos distintos y un instrumento de operación revisado antes de ejecutarlo.** Guardar sus fuentes por SHA bajo custodia del owner o incorporarlas como **referencias históricas inertes** bajo una PR separada, no como `latest_runner.py` reutilizable.

### 3.3 Semillas offline históricas

Paquete G4 `PAQUETE_HISTORICO_G4_B03_PDF_A_PDF_FBF166B_R1.zip`: SHA-256 `ac0300bc0a2a6ac8117f8fb34af000ba91747f2761e5562ba5bb4ae14fccf76d`.

| Semilla | Lugar de destino dentro del volumen nuevo | Cuenta/huella |
|---|---|---|
| Copia del PDF seleccionado | `data/inbox/doc_01_single.pdf` | 1 PDF, `531778` bytes, SHA arriba. |
| tiktoken | `data/tiktoken-cache/` | 1 archivo, `1681126` bytes; SHA de árbol `903a473c4b3d0b1057ebce939489d3e18b52e6afa85ecfe9d0c3f9b3c7e9255b`. |
| Tectonic | `tectonic_cache/` | 294 archivos, 185 directorios, `43350180` bytes; SHA de árbol `213cda977206ecb584c8f83bd4f59ee1d7f748ce8b05daa15b5d2bedaa207660`. |

**Carga útil 45.563.084 bytes**; no es tope de crecimiento del Docker filesystem. No sembrar desde G4 AST, archive histórico, DB, sidecars WAL, PDF de salida, `sqlite_backups` ni `CAPTURE_REPORT.json`. No extraer TAR completo a C:. Los cuatro otros volúmenes (`state`, `output`, `hf_cache`, `torch_cache`) empiezan vacíos. Estos hashes **son de la muestra R2**, no oráculos universales para R1/R3 u otros PDF.

## 4. Arquitectura del perímetro demostrado

### 4.1 Host y red

- Host probado: Windows, PowerShell, Docker Desktop con contenedores Linux, contexto `desktop-linux`.
- Imagen: la ID local indicada; `pull_policy: never` en los cinco servicios; **sin `build` ni `ports`** en el manifest C/L1.
- Red del RUN-ID: `bridge` privado con `internal: true`, `enable_ipv6: false`; sin port publishing ni red bridge externa adjunta en los cinco servicios inspeccionados. La comunicación funcional `llm_worker`→`groq_fake_g3:8080` ocurrió dentro de ella.
- Sondas en D1 y C/L1 denegaron TCP público IPv4/IPv6. **No** demuestran denegación de todos los protocolos, rutas, procesos o eventos posteriores a un cambio de topología. Si se agrega otro endpoint o interfaz, hay que repetir la prueba relevante.
- No adjuntar red `host`, socket Docker, interfaces externas, `extra_hosts` de host, proxy real ni servicios de port-forwarding. Una necesidad nueva requiere justificación y revisión previa, no un arreglo silencioso.

### 4.2 Proyecto, identidad y recursos

Patrón del candidato R2: variable obligatoria `AUDIT_RUN_ID` (sin valor por defecto); proyecto `i0l1${AUDIT_RUN_ID}`; red `i0l1${AUDIT_RUN_ID}_internal`. **El RUN-ID real de un ensayo nuevo debe ser único y previamente inexistente**: verificar no colisión de proyecto, contenedores, red y *cada uno* de los seis nombres físicos de volúmenes. Un `docker compose -p` distinto **no protege** de volúmenes nombrados globalmente. No usar los recursos de D1 ni el `RUN-ID=9cf15cac6b12` como destino de un ensayo nuevo. No usar `staticaud01` fuera de una proyección `config` estática.

| Volumen lógico Compose | Nombre físico en C/L1 histórico | Montaje en los servicios de producto |
|---|---|---|
| `g3_runtime_data` | `i0l19cf15cac6b12_data` | `/app/data` |
| `g3_runtime_output` | `i0l19cf15cac6b12_output` | `/app/output` |
| `g3_runtime_state` | `i0l19cf15cac6b12_state` | `/app/state` |
| `hf_models_cache` | `i0l19cf15cac6b12_hf_cache` | `/app/.cache/hf` |
| `tectonic_cache` | `i0l19cf15cac6b12_tectonic_cache` | `/app/.cache/tectonic` |
| `torch_cache` | `i0l19cf15cac6b12_torch_cache` | `/app/.cache/torch` |

Las monturas `volume` usan `nocopy: true`. El fake tiene acceso al estado en **solo lectura** y un único bind de archivo `./G3C_CONTRACT_GATE_FBF166B_R0.py` → `/app/g3c_contract_fake.py`, `read_only: true`, `bind.create_host_path: false`. Los cuatro servicios funcionales tienen rootfs **escribible**; solo el fake declara `read_only: true`. No hay checkout/corpus montado directamente en modo escritura en C/L1. La comprobación negativa del bind R/O fue focal, no un ensayo de inmutabilidad del sistema entero.

### 4.3 Servicios y límites del Compose ejecutado

| Servicio | Rol/entrypoint o comando | UID:GID | Memoria y swap de contenedor | Dependencias declaradas |
|---|---|---|---|---|
| `db_bootstrap` | `python -B -c <bootstrap G3/G4 instrumentado>`; valida seeds, crea SQLite y baja privilegios | `0:0` al iniciar; baja a `10001:10001` | `256 MiB / 256 MiB` | ninguna |
| `ocr_router` | `python apps/ocr_router/__main__.py` | `10001:10001` | `10 GiB / 10 GiB` | bootstrap completado |
| `groq_fake_g3` | `python -B /app/g3c_contract_fake.py --serve` | `10001:10001` | `256 MiB / 256 MiB` | bootstrap completado |
| `llm_worker` | `python runtime/engine.py` | `10001:10001` | `6 GiB / 6 GiB` | bootstrap completado y fake saludable |
| `assembler` | `python apps/compiler/__main__.py` | `10001:10001` | `2 GiB / 2 GiB` | bootstrap completado |

Políticas del manifest: `restart: no`, `pull_policy: never`, `init: true`, `pids_limit: 256` excepto fake 64, y logging `json-file` con `max-size=2m`, `max-file=2`. Fake: `cap_drop: [ALL]`, `no-new-privileges`, `tmpfs /tmp` `16m`, healthcheck privado `http://127.0.0.1:8080/health`. No se extrapola a los otros cuatro servicios el `cap_drop` o rootfs R/O del fake. **`depends_on` no es orquestador de checkpoints ni hace seguro `docker compose up` indiscriminado.**

**Memoria física durante la serie histórica:** 31,83 GiB RAM host, 11,68 GiB asignados a Docker Desktop; no son mínimos normativos universales. **No arrancar los cinco simultáneamente** en esta PC: OCR tiene límite 10 GiB, con margen nominal pequeño dentro de Docker. Los picos observados P3 fueron Engine ~0,053 GiB y fake ~0,031 GiB, P4 Assembler ~0,192 GiB; cifras puntuales del testigo, no dimensionamiento de otros PDFs.

### 4.4 Variables de entorno y seguridad de credenciales

**Rutas comunes de estado** del manifest:

```text
APP_ROOT=/app
PYTHONPATH=/app
SQLITE_STATE_DIR=/app/state/db
FSM_DB_PATH=/app/state/db/fsm.db
QUEUE_DB_PATH=/app/state/db/queue.db
EVENT_DB_PATH=/app/state/db/event.db
MAT_DB_PATH=/app/state/db/materialized.db
```

**Diferencias por servicio:** `ocr_router`/`llm_worker`: `TIKTOKEN_CACHE_DIR=/app/data/tiktoken-cache`; `assembler`: `COMPILER_OUTPUT_DIR=/app/output`, `TECTONIC_CACHE_DIR=/app/.cache/tectonic`, `XDG_CACHE_HOME=/app/.cache/tectonic`, `XDG_CONFIG_HOME=/tmp/.config`, `HOME=/tmp`; los nombres de `NODE_ID` incluyen el RUN-ID y sufijo de servicio. `llm_worker`: `IS_BENCHMARK=0`, `MAX_CONCURRENT_CHUNKS=1`, `MAX_GLOBAL_LLM_CONCURRENCY=1`, `GROQ_TPM_LIMIT=200000`, `GROQ_BASE_URL=http://groq_fake_g3:8080`, `GROQ_API_KEY=<VALOR_FICTICIO>`; fake: `G3C_MAX_ACCEPTED=3`, `G3C_ENABLE_STANDALONE_TEST_SERVER=EXPLICIT_PRIVATE_LAB_ONLY`, `GROQ_API_KEY=<MISMO_VALOR_FICTICIO>`, `HTTP_PROXY=`, `HTTPS_PROXY=`, `ALL_PROXY=`, `NO_PROXY=groq_fake_g3,localhost,127.0.0.1`, `PYTHONDONTWRITEBYTECODE=1`. El Engine usa el proveedor simulado; no se debe configurar `api.groq.com` ni un token verdadero.

**Reglas:** verificar **nombres y presencia** de variables sensibles, origen efectivo, URL y coincidencia del valor ficticio **sin imprimir tokens**; no mostrar `.env`, `docker inspect` entero o `docker compose config` completo en logs públicos. El `G3C_MAX_ACCEPTED=3` corresponde al fixture histórico R2 (3 unidades `translate`); **no cambiarlo después de ver la salida OCR** de otro sujeto. Si una ruta requiere otra cardinalidad, se preregistra la incompatibilidad o nuevo fixture ANTES del ensayo, nunca se arregla ad hoc para obtener PASS.

## 5. Recursos, presupuesto y umbrales operativos

**Política histórica del operador, no del Charter:** antes de escribir, exigir al menos **21 GiB libres** en C:; STOP si el espacio cae por debajo de **20 GiB**. Presupuesto incremental máximo preventivo **1 GiB por fase**, monitorizado; no es una cuota garantizada de volúmenes ni del VHDX de Docker. Medir Windows C:, memoria Docker y capacidad del daemon **justo antes de cada fase**. Si la demanda futura supera el límite, detener y pedir nueva decisión con presupuesto concreto, no llenar el disco y limpiar después. Última medición P5: `28,83 GiB` libres; **no es una medición actual**.

**Prohibiciones constantes sin acto independiente:** `docker build`, `docker pull`, `docker save`/TAR de imagen, Docker Scout, copia masiva de wheelhouse/cache, reinstalaciones de dependencias, `docker system prune`, `docker compose down -v`, `docker volume rm`/limpieza de laboratorios históricos, borrado de recibos, checkout o corpus escribible, uso de APIs o claves reales y autoescalado a múltiples servicios. Evitar `docker exec` interactivo sin perímetro/autorización, y no montar `/var/run/docker.sock` en el runtime. No habilitar swap para simular RAM no disponible.

**Presupuesto inicial probado:** seeds ~45,56 MB decimales, cinco contenedores basados en la imagen existente, seis volúmenes nuevos y red. **No estimar el crecimiento global solamente a partir de los seeds.** Las métricas se registran antes/después por fase; logs acotados. No copiar imágenes, wheelhouse ni SQLite entero cuando un snapshot coherente y un SHA son suficientes.

## 6. Procedimiento de operador — etapas y gates

**Principio:** preflight de solo lectura → decisión de elegibilidad de **esa variante** → autorización de una fase → operación única → verificación de barrera durable → STOP/HOLD antes de la siguiente fase. No adelantar un gate por éxito de una fase distinta, ni confundir la política de sandbox con el éxito científico del traductor.

### 6.1 A. Inspección estática segura (PowerShell, sin iniciar Docker)

Ejecutar desde el checkout de GitHub; solo lectura, salvo operaciones internas que el cliente Docker eventualmente realice para consultar el daemon. **No** imprimir secretos. Si algo difiere, registrar y detener, no «arreglar» por intuición.

```powershell
# Inspección de estado, NO inicia ni borra servicios.
git branch --show-current
git rev-parse HEAD
git status --short
docker context show
docker version --format '{{.Server.Os}}/{{.Server.Arch}}'
docker image inspect --format '{{.Id}}' 'i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824'
(Get-PSDrive C).Free / 1GB
# Objetos históricos: inspección limitada a nombres y estados.
docker ps -a --filter 'label=com.docker.compose.project=i0l19cf15cac6b12' --format '{{.Names}} {{.Status}}'
docker volume ls --filter 'label=com.docker.compose.project=i0l19cf15cac6b12' --format '{{.Name}}'
```

**Verificar** contexto `desktop-linux`, ID de imagen exacto y su presencia, no estados inesperados de contenedores. Si Git contiene commits documentales posteriores, distinguir **HEAD de Git** de **commit del código dentro de la imagen**: jamás declarar igualdad de código sin reconciliar. El checkout del owner no es carpeta de ejecución escribible para un sandbox.

### 6.2 B. Validación de la fuente y del Compose, sin arranque

1. Ubicar el ZIP C/L1 de §3.1 y verificar su hash; extraerlo **en carpeta independiente**, no sobre el repositorio ni el proyecto D1. Verificar hashes de los dos archivos que se montarían en el runtime.
2. Resolver un RUN-ID **ficticio de inspección**, por ejemplo `staticaud01`, **solo** para `docker compose config --quiet`. La validación no crea contenedores, no otorga permiso para ejecutar y el ID de muestra jamás se usa para escribir.
3. Comprobar manualmente el modelo efectivo: servicios cinco, `build` ausente, `pull_policy=never`, redes `internal`, puertos no publicados, mounts sin binds RW ni paths heredados, variables fake y token ficticio, UID, límites RAM/swap, todos los seis volúmenes aislables.

```powershell
# Cambiar $compose por la ruta REAL del YAML extraído.
$compose = 'C:\RUTA_A_LA_COPIA\compose.c.L1_REVIEW_ONLY.yaml'
$env:AUDIT_RUN_ID = 'staticaud01' # SOLO PROYECCIÓN ESTÁTICA; NO ES RUN-ID OPERATIVO.
if ((Get-FileHash -Algorithm SHA256 $compose).Hash.ToLower() -ne '055034fa86aebaf7c147992e11d0e69ce18afb4fc39ba7648143a130a2b3d0c4') {
    throw 'STOP_COMPOSE_SOURCE_DRIFT'
}
docker compose --profile l1-hold -f $compose config --quiet
if ($LASTEXITCODE -ne 0) { throw 'STOP_COMPOSE_CONFIG' }
Remove-Item Env:AUDIT_RUN_ID # SOLO la variable temporal de ESTA consola.
```

`Remove-Item Env:` **no borra un archivo ni un recurso Docker**. Para validar pertenencia y reglas avanzadas puede inspeccionarse `config --format json` dentro de un verificador que **no publique secretos**. **No ejecutar** `docker compose up`, `start`, `create` ni `run` desde esta sección.

### 6.3 C. Revisión de las diferencias AS-IS→arnés→ruta

Antes de ejecutar R1/R2/R3 documentar en una tabla por ruta: commit/tree funcional, imagen ID/arquitectura, comando de entrada, servicios imprescindibles, variables, perfiles, mount de código/datos, DB, fake, seed, red, duración, momento de escritura, clase de PDF, fingerprints y estado `ELIGIBLE`, `NO ELEGIBLE — PRECONDICIÓN` o `UNKNOWN`. Verificar los 16 HV **solo donde el delta afecta su evidencia**; no repetir sondas de configuración que permanecen idénticas. La cobertura en C/L1 del camino nominal no incluye reconciler/sweeper ni garantiza recovery. **El diseño de R1/R3 aún no se ha verificado** y no se inventa su receta aquí.

### 6.4 D. Reserva, autorización y preparación de un RUN-ID **nuevo**

**Sección procedimental; NO comando de lanzamiento autorizado.** Antes de cualquier escritura:

1. Obtener decisión específica del owner: ruta, código, variante (concurrente/escenificada), PDF autorizado y SHA, fixture/determinismo fake, egress, umbrales y qué se considera `STOP`.
2. Asignar un RUN-ID único no reciclado; comprobar que proyecto/red/servicios/volúmenes no existen. Proteger D1 `i0hv49cde367de`, C/L1 `i0l19cf15cac6b12` y G4. No usar manifiestos D1 de volúmenes globales fijos.
3. Revisar que la **composición efectiva** tenga etiquetas de propiedad `org.traductor.audit.run-id`, red interna, fake-only, bind RO, sin `build/pull`, y que las rutas de datos apunten a volúmenes **frescos** del nuevo RUN-ID.
4. Verificar disponibilidad real de datos/cache, RAM y disco; si la variante requiere recursos nuevos, presupuestarlos y autorizarlos ANTES de crear contenedores o volúmenes.
5. Preparar un ejecutor de fase específico del nuevo ensayo **revisado como fuente**, con SHA, gates y reanudación definida. Los instrumentos históricos P0–P5 **no son plantillas que admitan simplemente cambiar un parámetro**: incluyen identidades y expectativas congeladas, y sus preflights rechazan drift.

**No se autoriza generar automáticamente varios nuevos volúmenes «por si acaso».** Solo los imprescindibles. La no colisión se demuestra, no se supone.

### 6.5 E. Ejecución histórica R2 P0–P5 — referencia de orquestación

**No ejecutar los comandos de esta tabla sobre el RUN-ID finalizado.** La tabla describe el comportamiento acreditado y las barreras que un nuevo procedimiento debe preservar. P0–P4 usaron primero preflight de solo lectura y `--apply` solo tras autorización de fase; P5 V3 usó `--export` en fase de custodia.

| Fase | Servicios permitidos | Precondición y primera barrera verificable | Resultado histórico |
|---|---|---|---|
| **P0** | Ninguno del producto; helper efímero `--network none` y recursos limitados para preparar semillas | Seis volúmenes NUEVOS, fichero PDF y cachés verificados, UID/GID y montajes, red/proyecto; no iniciar bootstrap. | `P0_PASS_L1_HOLD`. |
| **P1** | Solo `db_bootstrap` | Cuatro planos SQLite inicializados desde cero y WAL disponible; nunca reiniciar bootstrap una segunda vez. | `P1_PASS_L1_HOLD`. |
| **P2** | Solo `ocr_router` | PDF archivado, AST real 61 nodos, perfil/manifiesto 5 unidades, FSM `PROCESSING`, OCR detenido limpiamente. | `PASS_OCR_ONLY` con instrumento V2. |
| **P3** | Solo `groq_fake_g3` + `llm_worker` | 5 tareas completadas, 5 recibos, 61 proyecciones, barrera `READY_FOR_ASSEMBLY`, ambos detenidos. | `PASS_ENGINE_FAKE_ONLY`. |
| **P4** | Solo `assembler` | Publicación atómica de PDF, FSM `COMPLETED`, seis tareas terminadas; las otras cuatro funciones no reiniciadas. | `PASS_ASSEMBLER_ONLY`. |
| **P5** | **Ningún servicio del producto**; helper efímero sin red y volúmenes RO | Cinco snapshots SQLite por backup API, hash original/final, AST/manifiesto, ZIP y recibo; sin reinicios. | `PASS_EXPORT_ONLY` V3. |

**Precauciones:** no usar `docker compose up` indiscriminadamente; `depends_on` podría reiniciar `db_bootstrap`. Los ejecutores históricos controlaban el `start` individual y supervisaban estados; **la tabla no reemplaza ese código**. No matar un escritor en mitad de una transacción por un timeout arbitrario; detener preventivamente con procedimiento acotado y capturar STOP. Un PDF parcial, un log `COMPLETED` o un buen hash de SQLite no autorizan por sí solos otra fase.

### 6.6 F. Observabilidad y gates por fase

Antes y después de **cada** fase medir: espacio real C:, memoria total/asignada y pico observado por contenedor, bytes agregados a volúmenes del RUN-ID (sin sumar históricos), estados `running/exited/OOMKilled`, arrancados recientemente, logs acotados (con secretos ocultos), documentos/tablas y barrera de FSM. Obtener UTC de comienzo/fin y SHA del ejecutor/recebo. Si alguno de estos datos falla o difiere: `STOP/HOLD`, preservar registro, no repetir ni limpiar automáticamente.

**Condiciones de STOP obligatorias:** secreto no ficticio, destino externo o proxy no autorizado; contexto/image ID/volumen/red/mount fuera de allowlist; RUN-ID repetido; entrada/caché SHA distinto; writer vivo al hacer snapshot; libre C: <20 GiB o consumo >1 GiB no autorizado; OOM/pressure real; falta de barrera durable; estado de contenedor inesperado; ZIP corrupto; hash drift; fuente del instrumento no revisada. Un fallo del instrumento se registra por separado del fallo del producto.

## 7. Verificación L0/HV — matriz de controles, evidencia y límites

**Importante:** `PASS_LIMITED`/`ACOTADO` es un resultado **válido con su frontera**, no un truco para no completar un trabajo. La **habilitación operativa** de C/L1 R2 escalonado se obtuvo en esa variante y el ensayo pasó; la **certificación universal de todos los HV** no se atribuye a los otros modos o rutas.

| HV | Inspección de seguridad/operación | Evidencia histórica C/L1 o D1 | Límite para otra variante |
|---|---|---|---|
| HV-01 Código/imagen | Commit, tree, imagen ID y diff del ejecutor | IDs R2 fijados y comprobados | Si cambia entrypoint/código/imagen, reconciliar. |
| HV-02 Build/binarios | Ejecutables presentes, Tectonic y dependencias resueltas | R2 ejecutó Tectonic real; imagen existente | Dos cold builds/reproducibilidad son asunto de suministro, no equivalen a uso nominal. |
| HV-03 Secretos | Variables efectivas, origen, dummy sin imprimir valores | Dummy y URL fake inspeccionados | No es escaneo exhaustivo de host/capas; revisar cuando cambia la composición. |
| HV-04 Mounts | Todos los mounts, bind RO, ausencia de checkout/corpus RW | 5 servicios y 6 volúmenes examinados; fake RO | Otros entrypoints pueden escribir rutas diferentes. |
| HV-05 Estado fresco | Seis volúmenes/run-ID, rutas/DB/AST/output nuevos | C/L1 corrigió el defecto D1 de nombres fijos | Necesita RUN-ID y nuevos volúmenes para cada corrida; no reutilizar B/C. |
| HV-06 Red/puertos | Red `internal`, IPv6 desactivado, puertos ausentes | C/L1 interna y sin puertos publicados | Nuevos servicios o redes requieren nuevo contraste. |
| HV-07 Egress | Sondas inocuas hacia IPv4/IPv6 públicos | Denegado en D1 y C/L1 para TCP probado | No prueba otros protocolos ni la seguridad de otra red. |
| HV-08 SDK/endpoint | SDK Groq, precedencia y URL interna | Groq 1.4.0 en D1, Engine→fake en C/L1 | Revalidar si hay SDK/proveedor/código diferente. |
| HV-09 Fake/fixture | Contrato, salud, determinismo y límites del oráculo | 3 unidades `translate` atendidas | No cambiar fixture post hoc; eco no mide calidad de traducción. |
| HV-10 Referencia RO | Prueba de escritura en copia referencia RO, hashes | Negativa D1 y ausencia de checkout RW en C/L1 | No equivale a rootfs RO global. |
| HV-11 Reversibilidad | Pertenencia por RUN-ID y plan selectivo sin tocar históricos | Recursos identificados; **no** limpiados por decisión de custodia | Antes de eliminar, prueba/autorización separada; no exigir limpieza de historia para ensayar. |
| HV-12 Procedencia | UTC, fingerprints, comandos/recibos, desvíos | P0–P5, hashes PDFs/ZIP, snapshots | Integrar nuevo RUN-ID y archivo de recibos; folios formales pendientes. |
| HV-13 Cobertura | Servicios exigidos por la ruta y faltantes justificados | Cinco servicios R2 nominal | Reconciler/sweeper excluidos; recovery/concurrencia no acreditados. |
| HV-14 Comparabilidad | Tabla de deltas AS-IS→D1→C/variante, flags y fuente | C/L1 `IS_BENCHMARK=0`; ejecución escalonada declarada | No atribuir resultados a R2 AS-IS concurrente. |
| HV-15 SQLite snapshots | Backup API, WAL y lectura de otra conexión | 5/5 DB íntegros en P5 | No es recovery multi-proceso ante fallo activo. |
| HV-16 Autoridad | Consentimiento owner por fase, límites y Charter/Board | Permisos P0–P5 documentados | Charter sigue DRAFT: no inventar aprobación formal ni permiso para otras rutas. |

**Cómo completar un gate para una ruta:** demostrar los controles indispensables para el **perímetro y las operaciones propuestas**, adjudicar `ELIGIBLE / NO ELEGIBLE — PRECONDICIÓN / UNKNOWN` y describir qué no se ensayó. No condicionar L0 de R1 a 2 cold builds, ni presentar HV universal en PASS por una corrida nominal de R2. Las decisiones del Board pendientes se mantienen como dependencia de gobernanza separada, sin apropiarse de su autoridad.

## 8. Evidencia L1: CP-00…CP-12 y veredictos independientes

| CP | Verificación mínima, referida a la variante observada |
|---|---|
| CP-00 | Fingerprint Compose/código/imagen, flags/endpoint fake, rutas, recursos. |
| CP-01 | Bootstrap de bases nuevas y WAL. |
| CP-02 | Ingreso de **copia** PDF, SHA y archivado. |
| CP-03 | AST real y `ast_hash` persistidos. |
| CP-04 | Perfil, manifiesto, tipos y topología chunk/nodo. |
| CP-05 | FSM/cola por documento y generación coherentes. |
| CP-06 | Claim/lease, `execution_id`, autoridad/attach según evidencia. |
| CP-07 | I/O fake observado, autorización externa diferenciada. |
| CP-08 | Respuesta y journal/durabilidad precisos; **en R2 histórico `UNKNOWN` para `event.db`**, aunque hay 5 recibos G3 en cola. |
| CP-09 | Publicación/materialización por nodo, versiones/hash. |
| CP-10 | Barrera `READY_FOR_ASSEMBLY` y handoff real. |
| CP-11 | TeX/Tectonic, publicación física nueva del artefacto. |
| CP-12 | PDF final legible, hash, vínculo document_id, FSM terminal. |

**Outcome del Atlas §9.2.3:** `A` = PDF final válido de la ruta y atribuible a la corrida; `B` = producto parcial, última etapa y etapa de fallo identificadas; `C` = fallo con causa observada, traza y frontera. `NO EJECUTADO/NO ELEGIBLE` ⇒ `execution_outcome=null`, no cuarto outcome. Registrar en **campos distintos**: `execution_outcome`, `contract_verdict`, `scientific_verdict` y, para fake eco, `linguistic_translation_verdict=NOT_EVALUABLE_FAKE_ECHO`. No alterar criterios después de observar resultados.

**Fidelidad matemática:** cotejar PDF renderizado con original, ecuaciones, código, símbolos, tablas y figuras; `PRESERVE` en un manifiesto o PDF válido no bastan. En R2 real se observó pérdida en ecuaciones (1.1)/(1.2), desigualdad Bellman y AST sin tipos ecuación; **no se identificó aún una única función causal**. E2-02 sigue en investigación; no reparar durante el testigo E2E-0.

## 9. Custodia, evidencia histórica y protección de SQLite

**Material de una corrida** (crear bajo carpeta o almacén de evidencia **fuera de los volúmenes temporales y fuera de checkout escribible**):

```text
EVIDENCE/<RUN-ID>/
  manifest.json                 # run-id, ruta, código/tree, imagen, compose/fake/script SHA, UTC
  authorization.md              # quien autoriza, alcance, límites, gates y exclusiones
  env-sanitized.json            # nombres de variables, URL fake, no secretos
  l0-hv-status.md               # HV-01..16, prueba y alcance
  phases/                       # pequeños recibos P0..Pn, estados, STOP, códigos de retorno
  e2e0-cp-status.md             # CP-00..12, observado/desconocido, trazas
  pdf-and-sqlite/               # copias SOLO si fueron autorizadas y son indispensables
  sha256sums.txt                # hashes, tamaño y procedencia verificables
  review.md                     # A/B/C, contratos, científico, límites, incertidumbres
```

No crear esta estructura en los volúmenes de producto ni copiar automáticamente gigabytes. La evidencia P5 R2 ya exportada incluye PDF original/final, AST, manifiesto y **cinco snapshots** (`documents`, `fsm`, `queue`, `materialized`, `event`); ZIP de 14 miembros y hashes 13/13 coherentes. El `integrity_check=ok` se aplicó a copias estables. Si SQLite está en WAL o hay escritores activos, **no** copiar en caliente solo el `.db`; realizar backup por API en el procedimiento autorizado, comprobar lectura independiente, cerrar conexiones explícitamente en Windows antes de eliminar temporales y no tomar snapshots globales como transaccionalmente atómicos sin prueba de coordinación. Los recibos originales y ZIP P5 son inmutables; publicar al repositorio solo un **índice de evidencia** con hashes si no hay política que autorice almacenar binarios.

**Incidentes a conservar:** P2 V1 `STOP` de precheck; P2 V2 primer OCR real; P5 V1 `OperationalError`, V2 `PermissionError` por verificación temporal en Windows, V3 exportación válida con conexiones cerradas y traceback. Ninguno de esos dos STOP de P5 demuestra fallo del traductor. Separar siempre `instrument_failure` y `product_failure`.

## 10. Procedimiento ante incidentes, STOP y recuperación

1. **STOP antes de efectos nuevos:** no ejecutar inmediatamente la misma instrucción con `--apply/--export`; no modificar criterios, no borrar datos, no reinstalar ni reconstruir imagen por reacción.
2. Conservar salida textual con UTC, fase, ejecutor y SHA, `run_id`, recursos afectados, estado (`created/running/exited`), escrituras potenciales y recibos previos. **No imprimir** `docker inspect`/`env` completo si puede contener secretos.
3. Si existe un servicio **running**, evaluar únicamente el mecanismo de parada supervisada de la fase y riesgo de escritura activa; no usar kill abrupto sobre SQLite por defecto. Si el estado no se conoce: `STOP_REVIEW`, inspección puntual con el owner.
4. Distinguir precheck fallido **antes de iniciar** un servicio, fallo del instrumento **después de crear temporales** y fallo del producto **durante su procesamiento**. Para cualquier recuperación crear una revisión con nombre/hash nuevo, cambios mínimos, causalidad comprobable y autorización específica; nunca sobrescribir el script/recibo histórico.
5. Reanudar **solo** donde haya barrera durable probada; no reiniciar bootstrap/OCR/Engine/Assembler de un RUN-ID terminado. La observación posterior puede requerir solo lectura o una copia de DB, no reprocesar el PDF.
6. No `docker system prune`, no `compose down -v`, no renombrar ni eliminar volúmenes o archivos históricos para «limpiar» un STOP.

## 11. Retención, inventario y eventual retiro selectivo

El sandbox **no implica que todos los recursos deban quedar corriendo**: D1 y C/L1 terminan con los servicios detenidos. Mantener separados: `logs/receipts` pequeños permanentes, ZIP/PDF con hashes bajo custodia, recursos temporales etiquetados y recurso histórico inmutable. Una futura limpieza **se solicita como tarea diferente**, con inventario por `org.traductor.audit.run-id`, confirmación de que no hay escrituras activas, export/validación de evidencia **previos**, presupuesto y autorización explícita del owner. Documentar qué se eliminó y qué se conservó. **Esta guía no contiene ni autoriza comandos de borrado**, para no facilitar eliminación accidental de D1/G4/C/L1.

## 12. Admisión de R1 y R3 sin inflar implementaciones

**Contrato de admisión común (en orden):** (1) mapear entrypoint original y productor/consumidor documental, (2) demostrar que funciona o existe dentro de la imagen R2 sin instalar paquetes, (3) identificar archivos/DB y requisitos de escritura, (4) comprobar fake y modelo de proveedor sin modificar `core`, (5) proyectar Compose/CLI efectivo con red, UID y seis volúmenes por RUN-ID, (6) elaborar tabla delta y matriz HV aplicable, (7) determinar **elegibilidad L0**; (8) solo entonces pedir autorización/ensayo y registrar CP de L1. Si falta una interfaz, eso es un resultado `NO ELEGIBLE — PRECONDICIÓN` o `UNKNOWN` motivado, **no** una orden de reparar la ruta antes de caracterizarla.

| Ruta | Estado actual respecto de este sandbox | Qué validar primero | Qué no hacer |
|---|---|---|---|
| **R1 (CLI)** | **No evaluada dinámicamente aquí.** | Entry point CLI, extracción, validación/healing, estrategia de proveedor y handoff a compilación/publicación, rutas y procesos reales. | Suponer que CLI comparte semántica de R2 o instalar otro stack por anticipación. |
| **R2 (OCR→Engine→Assembler)** | **Probada por fases** con fake y PDF; preservar el testigo. | Si se ensayara AS-IS concurrente, nueva configuración/autoridad y gestión de recursos; no inferir equivalencia. | Repetir C/L1 para «mejorar» resultado o reparar E2-02 durante caracterización. |
| **R3 (daemon alternativo)** | **No evaluada dinámicamente aquí.** | Compatibilidad exacta de interfaces, colas/IDs, productores/consumidores y deps; registrar primera ruptura. | Agregar adaptadores funcionales para forzar un PASS del sujeto original. |

El **sandbox base** se reutiliza como política y recursos instrumentales **en la medida de compatibilidad verificada**. No crear imágenes por ruta, ni una implementación de «sandbox universal» con abstracciones antes de observar una necesidad real. Un caso de incumplimiento es evidencia útil para la decisión de convergencia.

## 13. Gobernanza: quién decide qué y cómo se cambia esta guía

| Decisión | Autoridad/registro requerido | No implica |
|---|---|---|
| Editar una **guía documental** | PR normal, revisión técnica, changelog, mantener `DRAFT` hasta adopción. | Aprobación de Charter/Atlas/HITO o permiso para ejecutar. |
| Nueva fase **read-only** | Plan con límites/fuentes, aprobación operativa según tipo de acción. | Permiso para escribir en volúmenes. |
| Crear/sembrar contenedores y volúmenes | Consentimiento owner específico a ruta, RUN-ID, recursos, presupuesto y ejecutor verificado. | Derecho a arrancar el pipeline. |
| Arrancar P1/P2/P3/P4 o R1/R3 | Permiso de **fase**, gates y STOP determinados, evidencia de preflight. | Permiso para ejecutar fases posteriores, provider real o remedios. |
| Probar proveedor real / crear builds / modificar código | Autoridad y presupuesto separados; contrato/seguridad apropiados. | Parte automática del ensayo fake. |
| Cambiar Charter DRAFT, decisiones D-1…D-7, NADR o cerrar Atlas | Architecture Board/autoridad correspondiente y método formal. | Efecto de una PR de instrucciones de sandbox. |
| Retirar laboratorios | Verificación de propiedad y custodia + consentimiento explícito. | `prune` global ni `down -v` sobre históricos. |

**Mantenimiento:** versión nueva del runbook ante cambios de imagen, host, Docker, Compose, fake, nombres de red/volumen, permisos, estrategia de snapshot, límites de recursos o nuevos sujetos. Mantener changelog, diferencia entre `historical fact` y `proposed change`, SHA de cada artefacto, y tabla AS-IS→arnés. No modificar retroactivamente recibos y outcomes; añadir adendas fechadas. Los umbrales 21/20 GiB y 1 GiB no son criterios normativos inmutables: actualizarlos solo con aprobación explícita y medición suficiente.

## 14. Qué falta para que un tercero pueda ejecutarlo sin ayuda del chat

Esta es la **lista cerrada de brechas de empaquetado operativo**, no una orden para implementar infraestructura nueva:

1. **Ubicación versionada** del YAML C/L1 y fake exactos identificados en §3.1, actualmente bajo custodia en el ZIP local. Publicarlos como **referencia instrumental congelada**, no como servicio nuevo ni manifest «production-ready».
2. **Custodia accesible de los ejecutores históricos** P0–P5 o su índice firmado/hash (son *artefactos de una sola corrida*). Para un RUN-ID futuro, preparar únicamente la **adaptación mínima y revisada de los gates**; no copiar y ejecutar scripts con IDs, recibos o conteos anteriores.
3. **Ficha de admisión por nueva ruta** (R1/R3): no exige otro sandbox, pero sí definir entrada/comandos/dependencias y parámetros que aún no se probaron.
4. **Permiso/autoridad de la nueva operación**: el Charter sigue DRAFT, el Atlas `IN_PROGRESS`; esta guía no tiene capacidad de aprobar pruebas futuras.
5. **Acceso a los artefactos offline autorizados**, con SHA y política de custodia. El Git remoto no debe convertirse en almacén de PDFs del corpus, ZIP gigantes, Docker TAR o bases privadas por conveniencia.

**Dictamen de operabilidad:** `REFERENCE_PERIMETER_R2_STAGED = DEMONSTRATED`; `RUNBOOK_CURRENT_STATE = DOCUMENTED`; `GENERIC_R1_R3_EXECUTOR = NOT_VERIFIED`; `UNIVERSAL_SANDBOX_CERTIFICATION = NOT_CLAIMED`. Estas etiquetas describen el alcance; no reemplazan los outcomes A/B/C de E2E-0.

## 15. Índice de fuentes y trazabilidad

**En el repositorio**, bajo `docs/architecture/adr/pipeline-stabilization/00-foundation/`:

- `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` v0.2.16, §§0–13; resultados de R2 y pendientes globales.
- `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` v0.1.0 `DRAFT`, §6 (caracterización y criterios de saneamiento distintos).
- `L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md` (§§9–10: HV-01…HV-16 y sujetos A/B/C).
- `L0_HV_D1_R2_DICTAMEN_CONSOLIDADO_POST_HV15_20261102.md` (fotografía D1 del 02/11, `HOLD/UNKNOWN` de ese día).
- `I0-1D_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_2026-10-31.md`, `I0-1E_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_20261101.md`, `I0-1F_ACTA_CONSOLIDADA_CIERRE_TECNICO_ACOTADO_20261102.md` (alcances técnicos históricos, no cierre del Atlas).
- `working-observations/L0_HV_R2_D1_C_L1_AVANCE_20261103.md` (reconciliación HV tras C/L1).
- `working-observations/E2E0_R2_ESCALONADO_AVANCE_20261103.md` (P0–P5, CP-00…12, outcome, contratos, ciencia).

**Fuera del Git actual, bajo custodia local del owner**: ZIP C/L1, ZIP G4, instrumentos P0–P5 y recibos originales, ZIP P5, dictamen científico y comparaciones visuales. Esta separación es intencional; el acceso a ellos debe resolverse antes de que un tercero quiera reejecutar un ensayo.

**Regla de integridad editorial:** si alguna fuente falta, ha cambiado o no está disponible, indicarlo como `UNKNOWN / PRECONDITION` y detener la nueva operación. **No completar por imaginación** configuración, permisos, UID, rutas, fake o artefactos de otra ruta.

---

**Fin de la guía v0.1.0 — `DRAFT`. El sandbox está acreditado como perímetro de referencia para R2 escalonado, no como producto ni traductor canónico. El Atlas sigue abierto.**
