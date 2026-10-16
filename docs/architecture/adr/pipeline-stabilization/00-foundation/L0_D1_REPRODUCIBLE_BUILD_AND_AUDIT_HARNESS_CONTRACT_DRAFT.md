# D1 — Contrato de build reproducible y arnés de auditoría Groq (propuesta de implementación)

**Estado:** `DRAFT — DESIGN REVIEW / NO BUILD / NO DEPLOY / NO L1`  
**Fecha de corte:** 2026-10-15  
**Repositorio:** `RDsanchez-git/translator_pdf` · `pipeline_stabilization`  
**Código y documentación examinados:** `4b9fc2c3c692ad87402855235d4dedd0e7d8db5f` (**no** es por sí mismo identidad de un futuro ejecutable)  
**Jerarquía:** Atlas v0.2.15 §9 → Charter §6.1 v0.1.0 DRAFT → expediente E2E-0 DRAFT → `L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md` → este contrato auxiliar.  
**Origen de datos:** contenido estático de archivos versionados, comprobaciones PowerShell comunicadas por el owner y pruebas locales sin red del SDK Groq 1.4.0. No hay build, imagen o runtime observado.

> **Objeto:** especificar los insumos, fronteras, verificaciones y secuencia que permiten construir un arnés forense **sin cambiar el producto AS-IS** ni crear un falso PASS. Su aprobación de diseño no eleva Charter/Board, no autoriza remediaciones funcionales, ni habilita ejecutar E2E-0. Los controles de esta propuesta son instrumentales; se evalúan como `PASS / FAIL / NOT_RUN / UNKNOWN`, no como criterios normativos nuevos del proyecto.

## 1. Decisión de diseño D1 propuesta

1. **Sujeto A: AS-IS, inmutable para la auditoría.** Capturar commit, tree y configuración `base` / `base+golden` sin modificarlos. No ejecutar Compose base contra el checkout del owner. Diferenciar cualquier instrumentación como sujeto B con fingerprint propio.
2. **Sujeto B: arnés dedicado y explícito.** Elegir como diseño de referencia un **Compose autónomo**, no un overlay aplicado ciegamente al Compose base. Conservar únicamente los servicios requeridos para la ruta autorizada y sus comandos originales, indicando cada omisión/delta. Una composición autónoma elimina la herencia accidental de `./:/app`, `ports`, fake Gemini, Toxiproxy y redes ajenas. Antes de aprobar I0 se hará el diff semántico completo A→B.
3. **Construcción en dos fronteras:** (i) adquisición de artefactos de dependencias controlada y aprobada, posiblemente conectada a red; (ii) construcción de la imagen de ensayo usando solo artefactos verificados, **sin red**, desde un contexto creado mediante lista positiva. No usar el `.env` ni el checkout original como contexto.
4. **Runtime aislado:** una red exclusiva `internal: true`, cero puertos publicados, identificador de proyecto por RUN-ID, credenciales ficticias, código sin host bind al checkout original, estado nuevo y descartable; observabilidad y evidencia en un área separada.
5. **Proveedor:** conservar `GroqProvider` y `OpenAICompatibleDialect` de la fuente original. Usar `GROQ_API_KEY` de ensayo y `GROQ_BASE_URL` hacia un fake HTTP **Groq/OpenAI-compatible**, no hacia el fake Gemini. Ninguna credencial ni solicitud de Groq real está autorizada para L1.
6. **Aislamiento primero:** las pruebas de contrato/red/filesystem se realizan con un documento artificial del harness o sin documento, según el control; nunca con un PDF canónico antes de la autorización específica de L1.

## 2. Evidencia que fija el diseño y límites

| ID local | Observación contrastada | Estado / límite |
|---|---|---|
| `D1-E01` | `requirements.txt` no existe localmente ni está trackeado; `pyproject.toml` sí existe. | `REPORTED-LOCAL`; un checkout limpio con Dockerfile actual (`COPY requirements.txt .`) **no satisface** ese input y no puede construir **tal cual**. No hay fallo dinámico observado. |
| `D1-E02` | `pyproject.toml` declara `requires-python >=3.11`, dependencias de producción (`groq`, `docling`, `pymupdf`, `tiktoken`, etc.) **sin pins exactos**; opcionales dev diferenciados; paquetes internos bajo `apps/core/infra/runtime`. | `OBSERVED-STATIC`; no constituye lock, no permite resolver versiones/digests de imagen. |
| `D1-E03` | El Dockerfile usa `FROM python:3.11-slim`, descarga Tectonic `0.15.0` por URL y termina con `COPY . /app/`. | `OBSERVED-STATIC`; etiqueta mutable, Tectonic sin SHA visible y contexto potencialmente sensible. |
| `D1-E04` | `.dockerignore` no excluye explícitamente `.env`; checkout local contiene `.env`. En la raíz versionada hay PDFs y otros artefactos, por lo que `COPY .` amplía innecesariamente la superficie de datos. | `OBSERVED-STATIC` + `REPORTED-LOCAL`; **riesgo de exposición**, no filtración constatada. |
| `D1-E05` | El `venv` contiene `groq 1.4.0`. El constructor local admite `base_url`, lee `GROQ_BASE_URL`; cliente construido con entorno parcheado resolvió `http://127.0.0.1:18765/openai/v1/`. | `REPORTED-LOCAL — SDK URL OVERRIDE VERIFIED`; no demuestra build en Linux, comunicación HTTP, ni aislamiento. |
| `D1-E06` | `GroqProvider.translate()` llama `AsyncGroq.chat.completions.create(...)`; `OpenAICompatibleDialect` solicita JSON y decodifica `choices[0].message.content` con clave raíz `content`. | `OBSERVED-STATIC`; el fake debe ajustarse a este contrato, no devolver una cadena simple o `candidates[]` Gemini. |
| `D1-E07` | OCR escribe/mueve bajo `data/`; `ASTRegistry` escribe `data/ast_cache`; Assembler escribe `output`; SQLite bajo `/app/infra/db`. | `OBSERVED-STATIC`; aislar solo `sqlite_data` no basta. |
| `D1-E08` | El modelo Compose `base+golden` conserva 8 servicios y cambia `IS_BENCHMARK: 1 → 0`, `GEMINI_API_URL` interna → pública; no declara `GROQ_API_KEY` en worker. | `REPORTED-LOCAL — CONFIG PARSE`; no prueba comportamiento dinámico. |

**Corrección importante:** `groq==1.4.0` es una **versión observada del venv**, no un pin ya autorizado para producción. Como baseline de equivalencia del arnés se propone fijar exactamente esa versión en el lock de prueba, **sujeto a comprobación de compatibilidad de Python/Linux, aprobación y resolución completa del lock**. No hacer upgrade silencioso ni inferir que cualquier versión del SDK se comporta igual.

## 3. Contrato de entradas — build hermético respecto de red

### 3.1 Artefactos obligatorios, todos por identidad de contenido

| Artefacto | Forma esperada | Condición de aceptación |
|---|---|---|
| Código | Git commit SHA completo + tree SHA + exportación allowlist; `git archive` desde ese SHA, no working tree. | Snapshot coincide byte por byte con la fuente versionada; lista de archivos archivados revisada; ninguna mutación de código del producto. |
| Descriptor Python | `pyproject.toml` del commit y metadatos de packaging necesarios. | Se preserva su contenido original; no se reemplaza por `pip freeze` local. |
| Lock runtime | Archivo versionado p. ej. `audit/requirements-linux-py311.lock` generado desde `pyproject.toml` con pins de transitivas y hashes de distribución. | Todas las dependencias necesarias para runtime se identifican por versión y hash; Python/OS/arquitectura declarados; código y herramientas de generación registrados; reproducible por procedimiento auditado. |
| Lock tooling/build | Herramientas de creación de ruedas (`pip`, `setuptools`, `wheel` y resolver usado) identificadas de forma independiente. | Bootstrap de tooling no introduce componentes mutables/ocultos. |
| Wheelhouse | Conjunto exacto de wheels aprobados y sumas SHA-256, almacenados fuera del checkout original. | Instalación offline; hashes contra lock; sin paquetes extra ni sdist compilados ad hoc sin aprobación. |
| Imagen base | `python:3.11-slim@sha256:<DIGEST_APROBADO>` + plataforma `linux/amd64` o la acordada. | Digest real fijado, fuente y fecha registradas; ninguna etiqueta mutable a secas en el build final. |
| Tectonic | Binario/paquete versión `0.15.0` para plataforma de la imagen, con SHA256 externo obtenido y aprobado antes de usar. | Hash verificado antes de copiar al contenedor; `tectonic --version` comprobado *después* en HV; posibilidad de assets/font cache offline evaluada. |
| Paquetes del SO | Base digest con dependencias resueltas en imagen base controlada, o repositorios APT con snapshot y pinning verificable. | `apt-get update` contra repositorios cambiantes **no** se califica como build hermético; se decide y registra una estrategia concreta. |
| Fake Groq | Código fuente e imagen de harness propios, hash/digest y fixtures versionados. | Nunca empaquetado como proveedor productivo ni instalado en `apps/llm_workers`; estrictamente instrumental. |
| Manifest B | Compose autónomo del arnés y política de seguridad referidos por hash. | Config completa verificada por parser y guard estático/dinámico; no usar `docker compose up` hasta HV autorizado. |

**Nota de rigor:** con `pyproject.toml` sin pins, **no existe actualmente un lock reproducible**. D1 fija el **procedimiento** para producirlo, no inventa pins, hashes, digests ni compatibilidades no observados. Un lock generado en Windows no se eleva automáticamente a lock ejecutable de Linux. La resolución debe verificarse para la plataforma y ABI del contenedor.

### 3.2 Estrategia de resolución y adquisición (plan de I0, NO ejecutar todavía)

1. Elegir plataforma soportada y versión exacta Python 3.11.x; registrar imagen base por digest. No inferir arquitectura del host por Tectonic `x86_64`.
2. Congelar el conjunto de dependencias de `[project].dependencies` para **runtime**; documentar extras `dev` por separado. Preferir un resolver reproducible (pip-tools/uv, versión propia fijada) con pins transitivos y hashes para Linux/Python 3.11. **Fijar `groq==1.4.0` solo como hipótesis aprobable de baseline**, no como cambio de requisitos del producto.
3. Obtener las distribuciones en un entorno de adquisición segregado; verificar sha256 de cada wheel, soporte de plataforma, licencias según política y vulnerabilidades conforme al corte temporal de revisión. Dependencias sin wheel: **STOP**, evaluar build aislado de sdist con procedencia documentada; nunca compilar a escondidas en la imagen final.
4. Crear `wheelhouse/` completo; generar manifest `{name, version, filename, sha256, source, platform_tag}`; conservar hashes de lock y herramientas.
5. Exportar fuente exclusivamente de paths autorizados del commit; agregar **solo** lock/wheels/Tectonic verificados y Dockerfile de auditoría desde el arnés. Prohibir `.git`, `.env*`, archivos de secretos, `tests/corpus`, `data`, `reports`, `output`, `*.pdf`, `*.db*`, `*.sqlite*`, claves y artifacts ajenos. La lista positiva requiere revisión de imports/recursos hasta acreditar cierre del conjunto de runtime; si falta un recurso indispensable, añadirlo explícitamente y documentar el delta.
6. Construir desde ese contexto sin acceso a internet (`build --network=none` **tras** preparar imágenes base y artefactos). Instalar únicamente desde wheelhouse con verificación de hashes; instalar paquete local sin volver a resolver dependencias; nunca `COPY . /app` sobre un checkout que contiene secretos.
7. Obtener digest de imagen resultante, SBOM y procedencia; comparar la imagen contra policy de archivos sensibles. Ejecutar `python -c ...`, `groq` metadata, `tectonic --version` y smoke de importación **solo en HV autorizado**; preregistrar cualquier fallo como `HARNESS_FAILURE`.

**Criterio de no-reproducibilidad:** una imagen no es reproducible solo porque el Dockerfile compile una vez. Se exige insumo y verificación por contenido, posibilidad de rebuild contra artefactos retenidos y diff de SBOM/digest o explicación de bytes no reproducibles (timestamps, metadata, etc.). Si dos builds no producen digest idéntico, declarar `REPRODUCIBILITY_NOT_DEMONSTRATED` sin ocultarlo.

### 3.3 Contexto de build mínimo: política positiva

**Paths candidatos permitidos desde git** (sujetos a cierre de imports y recursos en I0): `apps/`, `core/`, `infra/`, `runtime/`, `configs/`, `pyproject.toml`, `README.md`. Solo archivos que el commit incluya y que resulten necesarios. No copiar archivos con extensión `.pdf`, contenido sensible o archivos de pruebas/oráculos.

**Importante:** una lista positiva de carpetas **no garantiza** por sí misma ausencia de archivos sensibles dentro de ellas. Requerir inventario de cada ruta, revisión por tipo de archivo y política de rechazo (symlinks que escapen, credenciales, binarios no aprobados, PDF/DB/llaves). No imprimir ni almacenar valores de secretos durante los controles. Evitar que el hash manifieste datos personales en ruta de host: paths relativos, no absolutos.

## 4. Dockerfile de auditoría — contrato estructural (NO archivo ejecutable listo)

El Dockerfile de arnés debe:

- Usar **base por digest** y plataforma registrada.
- Requerir como entradas wheelhouse y lock verificables; instalación offline sin fuente remota y sin resolución implícita; separar tooling de runtime.
- Incorporar Tectonic desde artefacto local con SHA comprobado, no `curl` a un release durante el build; verificar bit de ejecución/ABI y recursos requeridos en HV.
- Instalar/copy únicamente la lista positiva de código; usuario no root salvo excepción documentada; `PYTHONPATH=/app`; fijar directorio de trabajo `/app`.
- No contener secretos en `ARG`, `ENV` real, `RUN`, metadatos de imagen, logs de build o capas.
- Preservar rutas exigidas por la app (`/app/infra/db`, `/app/data/{inbox,archive,error,ast_cache}`, `/app/output`) en **montajes de runtime**, no como archivos heredados de checkout.
- Evitar ejecución automática de la traducción al construir la imagen. El comando real del Engine/OCR/Assembler pertenece al manifest de runtime con identidad separada.

**No usar este documento como un Dockerfile de implementación.** La sintaxis concreta, paquetes nativos, versión de tooling y wheelhouse se implementan y revisan en I0 mediante PR instrumental propio. No completar placeholders con valores adivinados.

## 5. Manifest Compose B: modelo explícito, sin herencia peligrosa

### 5.1 Selección de servicios

Partir del inventario A, pero **no** copiar todos por inercia. Para la primera variante R2 candidata, inspeccionar si hacen falta `db_bootstrap`, `ocr_router`, `llm_worker` (`runtime/engine.py`), `assembler`, `reconciler` y `sweeper`, justificando inclusión/exclusión. Agregar `fake-groq` como dependencia de ensayo. No arrastrar `fake-gemini` ni `toxiproxy` si la variante Groq no los requiere. `R1` CLI y `R3` daemon alternativo quedan sujetos a matrices propias, no se infieren de R2.

### 5.2 Propiedades obligatorias del arnés

| Dimensión | Contrato del manifest B |
|---|---|
| Imágenes | Tags locales **más digest/id registrado**; nunca pull/build implícito al iniciar L1. |
| Redes | Única red `audit_internal` con `internal: true` en todos los servicios; sin `host`, redes ajenas, `extra_hosts` o rutas de salida no declaradas. Verificar red real tras levantar HV vacío. |
| Puertos | `ports` ausente o `[]` para **todos** los servicios; fake puede usar `expose` interno. Cero API admin expuesta. |
| Seguridad | `privileged: false`; sin `cap_add`, `devices`, socket Docker, montajes del home, secretos reales. Usuario no root cuando sea viable; `no-new-privileges`, capabilities mínimas, límites CPU/RAM/PIDs y logging acotado. |
| Código | Se ejecuta desde **imagen del commit**; sin montar checkout original en `/app`, y sin `build: .` sobre el proyecto original. Preferir rootfs `read_only: true` después de demostrar que caches/temp tienen soporte de escritura, para no generar falsos fallos. |
| Datos | `infra/db` de corrida con FSM/queue/event/materialized/documents/rate_limits/cache; `data/{inbox,archive,error,ast_cache}`, `output` y `/tmp` en montajes de corrida; sin volúmenes de otras corridas. |
| Credenciales | `GROQ_API_KEY` ficticia y `GROQ_BASE_URL` de fake; **no** importar `.env` del repo ni `env_file` real. Comprobar environment final por nombres y destinos permitidos sin exponer valores reales. |
| Flags | `IS_BENCHMARK=0` en variante orientada a PDF real; documentar que el prefijo sintético `doc_` sigue existiendo; OCR calcula document ID a partir de SHA. `ENABLE_CHAOS_TEST=0`. |
| Evidencias | Logs/capturas por RUN-ID fuera de volúmenes efímeros; no exponer credenciales ni payloads de origen en artefactos compartidos. |
| Reversibilidad | Prefijo de proyecto audit aislado, etiquetas `audit.run_id`, inventario de resources antes/después. Limpieza **solo** del proyecto/RUN-ID validado; no usar comandos destructivos globales (`docker system prune`, `volume prune`, `down -v` sobre proyecto ajeno). |

### 5.3 Interacciones con datos y falsos positivos a evitar

- El contenedor debe poder **mover la copia** del PDF desde `/app/data/inbox` hacia `archive`/`error`; un bind read-only de inbox bloquearía legítimamente ese movimiento y generaría un error del arnés.
- `ASTRegistry` crea/rehidrata archivos bajo `data/ast_cache`; OCR, Engine y Assembler requieren el mismo contenido según contrato real; comprobar visibilidad entre procesos en HV.
- `Sqlite` usa rutas absolutas/relativas de `/app/infra/db`, con attachment FSM y WAL. Verificar `PRAGMA database_list` y backups consistentes; un simple hash del `.db` con WAL abierto no prueba integridad.
- `COMPILER_OUTPUT_DIR` por defecto `output` relativo a CWD `/app`; cualquier override se registra. `Tectonic` puede necesitar `/tmp` y caché; testear antes de activar rootfs RO estricto.
- `GROQ_BASE_URL` no sustituye una política de red: exigir **fail-closed** si está vacía/ausente/externa, antes de crear un worker conectado. Validación de la URL final, membresía de redes, egress negativo.

## 6. Fake Groq: contrato de integración y límite científico

**Endpoint propuesto:** `POST /openai/v1/chat/completions`; comprobar ruta efectiva del SDK 1.4.0 con un cliente instanciado en el arnés, sin tocar proveedores reales.

**Request exigida:** `model`, `messages[system,user]`, `response_format.type="json_object"`, `temperature`, `stream=false`; validación de esquema y rechazo duro ante entradas inesperadas. No aceptar `generateContent` ni simular semántica de Gemini.

**Respuesta mínima compatible:** campo `choices[0].message.content` que contenga **JSON serializado** con raíz `content`; `usage.prompt_tokens/completion_tokens`, `finish_reason=stop`, `model`, `id`, campos adicionales exigidos por el SDK; forma final fijada por test de contrato (no por ejemplo informal).

**Determinismo:** fixtures versionados por hash de prompt normalizado y ruta/documento; mismo input+config+versión → mismo resultado byte-equivalente. Incluir contraejemplos intencionales en HV (schema inválido, request sin clave, 429/500 si autorizado) **fuera de L1**. No ajustar fixtures para obtener PASS tras observar fallos de producto; registrar error de fixture como `HARNESS_FAILURE`.

**Ciencia:** respuestas prefijadas o artificiales sirven para probar transporte/control, **no** para acreditar fidelidad de traducción, preservación científica, políticas de validación o healing. Para L1, preregistrar expectativas compatibles con los invariantes aplicables y declarar el alcance limitado del fake.

**No alterar `apps/llm_workers/adapters.py`, `runtime/engine.py`, `apps/cli/main.py` ni código de dominio para hacer funcionar el fake.** Un cambio de esos archivos origina sujeto de auditoría distinto y requiere proceso de remediación.

## 7. Verificación negativa, cadena de custodia y criterios de rechazo

| Control | Prueba requerida en HV (posterior, autorizada) | Condición de `STOP` |
|---|---|---|
| `HV-01` | Confirmación commit/tree/image, diff completo y manifest relativo de archivos. | Imposibilidad de ligar imagen a fuente. |
| `HV-02` | Build offline desde contexto mínimo con lock y SHA, `groq.version`, Tectonic y smoke imports. | Descarga implícita, dependency drift o instalación fallida. |
| `HV-03` | Escaneo de contexto/imagen por nombres de secretos y archivos prohibidos; verificar sin imprimir valores. | `.env`, key, PDF/DB original, trazas privadas dentro del artefacto. |
| `HV-04` | `docker compose config` filtrado; `docker inspect` de montajes para todos los procesos. | Bind al checkout original o mount RW de corpus/oráculo. |
| `HV-05` | DB/cache/inbox/AST/output observados sobre resources dedicados, aislamiento interservicios donde procede. | Acceso a DB existentes o rutas no identificadas. |
| `HV-06` | Redes, puertos, capabilities, privileged, `extra_hosts`, rootfs. | Exposición externa o privilegio adicional injustificado. |
| `HV-07` | Test de egress negativo **sin documentos ni credenciales reales**; verificación de ruta interna a fake. | Cualquier salida pública exitosa o resultado inconcluso. |
| `HV-08` | `groq==1.4.0` efectivo dentro de imagen; endpoint del cliente solo fake. | SDK drift o `api.groq.com` seleccionado. |
| `HV-09` | Request real de SDK→fake con `OpenAICompatibleDialect` y parser de app; fixtures repetibles. | API shape/determinismo incompatibles. |
| `HV-10` | Intento de escribir archivo testigo exclusivamente en **copia RO del sandbox**, nunca fuente original. | Escritura posible. |
| `HV-11` | Desmontaje/limpieza de resources SOLO del RUN-ID, conservación de expediente. | Se afecta resource ajeno. |
| `HV-12` | Hashes, timestamps UTC, comandos, operador, logs saneados, evidencia vinculada. | Evidencia incompleta o con secretos. |
| `HV-13` | Topología y `depends_on` del manifest B justificados frente a A. | Dependencia crítica omitida o servicio extraño. |
| `HV-14` | A→B delta explícito; flags e identidad documental fijados. | Variante simulada reportada como AS-IS. |
| `HV-15` | Captura SQLite consistente; WAL/backup verificados. | Copia incoherente o durabilidad no demostrada. |
| `HV-16` | Aprobación de actividades de ejecución y L1 registrada. | No hay autorización identificable. |

**No ejecutar comandos de verificación destructivos sobre el host.** Antes de HV, el paquete debe pasar revisiones estáticas de seguridad, permisos y SOP de limpieza. Las comprobaciones negativas se harán únicamente sobre recursos `audit_*` nuevos, con un plan de reversión previamente aprobado.

## 8. Plan de implementación separado por cambios y entregables (no ejecutar ahora)

| PR/entregable instrumental | Contenido acotado | Criterio de revisión previo al siguiente |
|---|---|---|
| **I0-1 — Build inputs** | `audit/build/` con Dockerfile específico, locking para Python/Linux, manifest de wheelhouse/Tectonic, allowlist del contexto y pruebas del generador. | Supply chain documentada; sin credenciales/datos originales; inspección reproducible; fail closed ante hash faltante. |
| **I0-2 — Fake provider** | `audit/fake_groq/` con API compatible y fixtures versionados; tests de `chat.completions` + parser original. | Contratos válidos contra SDK fijado; determinismo repetible; no fallbacks silenciosos. |
| **I0-3 — Runtime sandbox** | `audit/compose/compose.audit.yml` **autónomo**; perfiles por ruta solo si necesarios; volúmenes/red interna/namespacing. | `docker compose config` sin puertos, mounts host externos, URLs públicas, claves reales; tests negativos estáticos. |
| **I0-4 — HV orchestration** | Invocación segura de verificaciones preflight, informe estructurado `HV-01…HV-16`, política de cleanup por RUN-ID. | Traces y estados verificables; fallar cerrado; jamás transformar HV en E2E-0. |

**Recomendación:** un único PR pequeño de diseño D1 primero; dividir implementación en PR(s) instrumentales que faciliten la revisión. No incorporar los resultados en el Atlas todavía salvo cross-reference del expediente a la especificación. El Atlas sigue `IN_PROGRESS` y el Charter `DRAFT`.

## 9. Matriz de decisiones pendientes — y autoridad

| Decisión | Alternativas válidas | Responsable | Estado |
|---|---|---|---|
| Baseline funcional que se usará para build | Commit actual verificado u otro fijado para una futura corrida. | Owner/Board según Charter | `PENDING` |
| Plataforma/arquitectura y digest de imagen base | Imagen compatible con PyMuPDF/Docling/Tectonic; digest exacto. | Owner técnico + revisión | `PENDING` |
| Lock/dependency resolver y repositorio de artefactos | `pip-tools`/`uv`/otro método trazable con hashes; wheelhouse y política de conservación. | Owner técnico | `PENDING` |
| Tectonic y dependencias Linux | SHA real aprobado; base con dependencias o APT snapshot, política offline. | Owner técnico | `PENDING` |
| Fixture Groq y semántica permitida | Respuestas deterministas compatibles con formato de la aplicación y contratos científicos aplicables. | Owner técnico + quien autoriza ensayo | `PENDING` |
| Servicios de R2, mounts y mapa de datos | Inventario final A→B y lectura de rutas efectivas; R1/R3 en controles propios. | Auditor + owner técnico | `PENDING` |
| Aprobación de implementación I0 y de verificación HV | Alcance y límites sin tocar producto/corpus; distinto de autorización L1. | Owner/Board correspondiente | `PENDING` |
| PDF/caso oficial E2E-0 y Charter §6.1 | PDF elegido, su hash, mecanismo de provider, criterios preregistrados. | Owner/Board según autoridad | `PENDING` |

## 10. Protocolo de promoción de estados

- **Ahora:** `D1 DESIGN SPEC PREPARED`, SDK redirect `VERIFIED LOCAL`, build reproducible `NOT VERIFIED`, PF-06 `PRECONDITION UNSATISFIED`, PF-08/09 `NO ACREDITADOS`, L0 `PARCIAL`, L1 `NO EJECUTADO`, `execution_outcome: null`.
- **Tras revisión del diseño:** `D1 REVIEWED`, siempre sin ejecución. Si un insumo no está decidido: `D1 REVIEWED WITH OPEN DECISIONS`.
- **Tras I0:** `I0 IMPLEMENTED / NOT YET VERIFIED` (no cambiar PF-08/09).
- **Tras HV:** controles `HV-01…HV-16` de una variante identificada con `PASS/FAIL/UNKNOWN`; cerrar L0 por ruta **solo** si las precondiciones aplicables se satisfacen.
- **Tras L1 ejecutado:** único momento para outcomes A/B/C y checkpoints CP-00…CP-12. `NOT EXECUTED` o `NOT ELIGIBLE` mantienen `execution_outcome=null`.

## 11. Evidencia y fuentes

**Repositorio fijo:** `https://github.com/RDsanchez-git/translator_pdf/tree/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f`

- `pyproject.toml` (`[project].dependencies` no pinned, metadatos de packaging), `Dockerfile` (`COPY requirements.txt`, Tectonic, `COPY .`), `.dockerignore` (ausencia de `.env`), inventario raíz versionado con PDFs, `docker-compose.yml`, `docker-compose.golden.yml`.
- `runtime/engine.py`; `apps/bootstrap/provider_stack_factory.py`; `apps/llm_workers/adapters.py`; `core/prompting/dialects/openai_compatible.py`; `core/prompting/renderer.py`; `apps/ocr_router/__main__.py`; `core/ast/registry.py`; `apps/compiler/__main__.py`.
- Owner PowerShell: `RequirementsPresent=False`, `RequirementsTracked=False`, `PyprojectPresent=True`, `groq_version=1.4.0`; introspección del SDK (`base_url=True`, `GROQ_BASE_URL=True`) y prueba local `BASE_URL_OVERRIDE_EFFECTIVE=True`, `DEFAULT_PUBLIC_ENDPOINT_BYPASSED=True` para URL ficticia; modelo Compose base+golden, sin arranque.
- `L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md`, `L0_PF08_PF09_ISOLATION_EGRESS_REVIEW_DRAFT.md`, `E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md`, Atlas §9 y Charter §6.1.

---

**Veredicto actual:** `D1 DESIGN PROPOSED (IMPLEMENTABLE CONTRACT) / NO LOCK OR IMAGE PRODUCED / SDK OVERRIDE VERIFIED IN HOST VENV / PF-06 NOT SATISFIED / PF-08-PF-09 NOT VERIFIED / L0 PARTIAL / L1 NOT EXECUTED / OUTCOME null`.
