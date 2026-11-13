# Runbook del sandbox PDF→PDF de convergencia

**Alcance:** reproducibilidad acotada de C0–C4 sobre código de pipeline_stabilization (PR #46). No es un procedimiento de despliegue, migración ni cutover. El testigo C2 original ya fue acreditado: **no repetirlo para acreditar de nuevo el mismo cierre**.

## 1. Requisitos y seguridad

Host original: Windows PowerShell 5.1, Docker Desktop/Linux, Python 3.11/venv; disco limitado. Imagen **histórica ya presente localmente**, tag i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824, ID sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd. Sin build, pull, imágenes, volúmenes ni proyectos nuevos salvo autorización explícita para un nuevo ensayo. Código del checkout montado /workspace:ro; runtime en /app. Fake con token dummy, sin egress público ni puertos host.

**STOP:** nunca ejecutar Docker prune, compose down -v, borrar volúmenes, bootstrap sobre datos existentes, reabrir G3_EXTERNAL_UNKNOWN, mezclar foreground y daemons en la misma generación o ejecutar un proveedor real para repetir esta prueba. Los documentos y actas contienen hashes y límites; los artefactos históricos siguen custodiados fuera de Git.

## 2. Preflight sin iniciar contenedores

Desde la raíz del repositorio, con Compose v2 que soporte !override/!reset y COMPOSE_PROFILES sin establecer:

~~~powershell
python -B -m apps.lab.convergence_compose_preflight --run-id conv0911a
$LASTEXITCODE

# Opcional: solo inspecciona la imagen local existente
python -B -m apps.lab.convergence_compose_preflight --run-id conv0911a --verify-local-image
$LASTEXITCODE
~~~

C0_T01_STATIC_CANDIDATE_PASS significa **solo inspección del Compose efectivo**; no comprueba runtime, egress físico ni PDF. Ante cualquier C0_T01_BLOCKED/FAIL, detener el procedimiento y registrar causa; no instalar ni levantar nada en automático.

## 3. Topología multiproceso C0–C2

La combinación histórica acreditada fue docker-compose.yml + docker-compose.runtime.yml + docker-compose.convergence-lab.yml, proyecto tpdfconvconv1211b. En ese **laboratorio**: db_bootstrap one-shot (solo volúmenes nuevos, UID root transitorio y drop a 10001), ocr_router, llm_worker (runtime/engine.py), assembler y g3_fake; reconciler/sweeper disponibles. Workspace /app, DB compartidas /app/state/db, inbox /app/data/inbox, output /app/output, red chaos_net internal:true, cachés pinneadas, fake g3_fake:8080 sin exposición exterior.

**Inspección de servicios existentes (sin iniciar ni modificar):**

~~~powershell
docker compose -p tpdfconvconv1211b `
  -f docker-compose.yml `
  -f docker-compose.runtime.yml `
  -f docker-compose.convergence-lab.yml `
  ps --status running --services
~~~

**Límite de reproducción:** la prueba real automática CLI (admisión sin --run) → OCR daemon → G3 daemon/fake → G5/Tectonic fue realizada una vez por el owner con comprobaciones independientes de SQLite, HTTP y PDF. **No existe en el repositorio un único comando validado que reconstruya ese ensayo multiproceso desde cero**; no presentar un comando compose up hipotético como receta probada. La prueba está descrita en la [acta C2](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200). Para un nuevo C2 haría falta un plan autorizado y volúmenes nuevos, no reutilizar la generación histórica.

**Resultado acreditado:** fuente 1544 bytes SHA 28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f; AST b0b4cb12ea5e2a871a8789e5228e428b10eca04380e5a95503ff4f61c89f9c4a; manifiesto 7724718fd66aff7b570f70a1dad828b2d3391abd14c47ef32fd12fb4a487229d; un POST a TRANSLATE, ninguno a PRESERVE, 2 receipts, 1 publicación, 4 proyecciones, FSM COMPLETED v7; PDF 7050 bytes SHA 71f209255c923daef84e44e1ae1bf642dfe5270e862eadedb0709b94ee62bfe3.

## 4. Foreground B03.2 y equivalencia T07

El lanzador apps.lab.offline_pdf_lab utiliza un contenedor Docker --rm --pull never --network none y un fake en loopback, código en /workspace:ro, bases nuevas en directorio host temporal. Necesita archivo histórico local Downloads/PAQUETE_HISTORICO_G4_B03_PDF_A_PDF_FBF166B_R1.zip, SHA-256 ac0300bc0a2a6ac8117f8fb34af000ba91747f2761e5562ba5bb4ae14fccf76d. Extrae exclusivamente cachés Tectonic/tiktoken y **nunca** restaura bases/PDF antiguos del ZIP.

~~~powershell
# Preflight: verifica imagen/ZIP, no ejecuta PDF
python -B -m apps.lab.offline_pdf_lab --preflight
$LASTEXITCODE

# Ensayo opcional real: CREA carpeta temporal y RETIENE evidencia;
# no repetir sin necesidad/disco suficiente.
python -B -m apps.lab.offline_pdf_lab --run-smoke
$LASTEXITCODE
~~~

Importante: offline_pdf_lab --run-smoke **conserva** su carpeta de ensayo y exporta un PDF, no limpia automáticamente.

La comparación T07 (ya acreditada) usa **otro lanzador** y necesita que el contenedor OCR del viejo proyecto C2 esté corriendo y contenga la fixture original. Copia la fuente en solo lectura, verifica identidad, receipts, plan, HTTP y PDF; usa TemporalDirectory con limpieza al terminar:

~~~powershell
python -B -m apps.lab.t07_foreground_compare
$LASTEXITCODE
~~~

Si el contenedor C2 no existe o faltan el ZIP o la imagen pinneada, **STOP**: no reconstruir el laboratorio histórico solo para ejecutar T07. T07 obtuvo PDF 7050 bytes SHA 9f70c22525358f7134020ad1ef511067037eca35cfe6636acd2494178a5325b4; igualdad **contractual**, no binaria, con C2. [Acta T07](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840717576).

## 5. Tests de verificación mínimos sin Docker

~~~powershell
python -B -m pytest -q tests/integration/test_c3_t05_process_boundary.py -p no:cacheprovider
python -B -m pytest -q tests/unit/test_c4_t06_supported_roots.py tests/integration/test_cli_router.py -p no:cacheprovider
~~~

En el entorno del owner: T05 1 PASS/exit 0; T06 6 PASS/exit 0. Son tests de contrato y recuperación, **no** una ejecución integral equivalente a C2. Evitar correrlos de nuevo si solo se quiere consultar la acreditación.

## 6. Cuidado de artefactos

No aplicar limpieza general de contenedores o rutas de Windows. Mantener los hashes y actas en [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md). Los logs brutos y PDF binarios no fueron incorporados a Git; no afirmar que se dispone de una reconstrucción íntegra forense fuera del host histórico. El CI CV falla por 15 PDF canónicos ausentes (issue #34) y los tres tests B02 históricos; eso es trabajo independiente.
