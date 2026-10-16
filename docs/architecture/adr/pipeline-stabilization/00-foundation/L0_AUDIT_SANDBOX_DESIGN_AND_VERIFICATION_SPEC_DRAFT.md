# L0 — Audit Sandbox: especificación de aislamiento, proveedor controlado y verificación

**Estado:** `DRAFT — DESIGN ONLY / SIN IMPLEMENTACIÓN NI AUTORIZACIÓN DE EJECUCIÓN`  
**Corte documental:** 2026-10-15  
**Proyecto:** `RDsanchez-git/translator_pdf`, rama objetivo `pipeline_stabilization`  
**Fuente de código y configuración cotejada:** commit `4b9fc2c3c692ad87402855235d4dedd0e7d8db5f`  
**Atlas rector:** `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` v0.2.15, §9, `IN_PROGRESS`  
**Charter rector:** `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` v0.1.0 `DRAFT`, §6.1; decisiones D-1…D-7 pendientes  
**Instrumentos subordinados:** `E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md` y `L0_PF08_PF09_ISOLATION_EGRESS_REVIEW_DRAFT.md` (anexo aceptado por el owner para orientar el diseño)  
**L1:** `NO EJECUTADO` · `execution_outcome=null` · sin PDF designado, presupuesto ni proveedor real autorizado.

> **Objeto de esta entrega.** Diseño auditable del arnés, no un cambio a la arquitectura del producto. Su aceptación para revisión **no constituye aprobación del Charter, autorización para desarrollar servicios, permiso de ejecutar contenedores, ni decisión de ruta canónica**. Ninguna variante instrumentada reemplazará una observación AS-IS; se registrarán fingerprints diferentes.

## 1. Resultado y decisión de diseño propuesta

**DECISIÓN DE DISEÑO PROPUESTA — PENDIENTE DE VALIDACIÓN TÉCNICA Y AUTORIZACIÓN DE IMPLEMENTACIÓN:** preparar una **copia de trabajo de auditoría segregada** del repositorio y una composición de ejecución específica, verificable *antes de iniciarse*. Preferencia técnica: **manifest completo de servicios de auditoría generado o curado explícitamente** a partir de la configuración AS-IS, en lugar de confiar en sobrescrituras parciales no inspeccionadas. Un overlay `docker-compose.audit.yml` es admisible **solo si el modelo efectivo** demuestra que eliminó/reemplazó todos los mounts, puertos, redes y dependencias incompatibles; la forma YAML por sí sola no demuestra seguridad.

El sandbox mantendrá **idéntico código funcional de referencia** y reproducirá las dependencias efectivas de la ruta bajo prueba, salvo las modificaciones *instrumentales* autorizadas, expresamente identificadas: directorios de datos temporales, política de red, endpoint de prueba Groq, credencial ficticia y medidas de seguridad. Estas diferencias son observables en el manifest de la variante y nunca se describen como comportamiento idéntico del despliegue AS-IS original.

### 1.1 Tres sujetos diferenciados

| Sujeto | Identidad | Qué admite afirmar | Qué prohíbe afirmar |
|---|---|---|---|
| **A — AS-IS documental** | Commit de código, Compose base o base+golden, flags y configuración original. | Contratos, incongruencias y conexiones declaradas en las fuentes. | Que pasó o falló dinámicamente sin arranque observado; que es seguro ejecutarlo en el host. |
| **B — Harness Verification** | Misma fuente funcional más perímetro instrumental con fingerprint y expediente propios. | Que un **arnés concreto** protege archivos, controla egress y satisface contrato de proveedor. | Que la aplicación realizó PDF→PDF, o que A se comportó igual. |
| **C — E2E-0/L1 autorizado** | Route+PDF SHA256+commit+variante aprobada+RUN-ID. | Clasificación A/B/C **solo después de una corrida** atribuible con checkpoints. | Que A significa cumplimiento de FROZEN/scientific verdict; que los testigos L2 cuentan como checkpoints L1. |

## 2. Alcance y límites de evidencia

**Delimitación positiva:** diseño estático de PF-06/07/08/09/10/12; controles comparables de configuración, build, red y archivos; contrato del simulador Groq; procedimiento de verificación negativa previo a L1; matriz de auditoría y responsabilidades.

**Fuera de alcance:** implementar/remediar el motor, reintroducir Gemini como proveedor productivo, cambiar modelos, solventar doble `ATTACH`, corregir la relación `chunk_id ↔ node_id`, elevar hallazgos a severidad oficial, cambiar corpus/oráculos, aprobar D-1…D-7, probar Groq real, correr `docker build/up`, ejecutar `pytest`, `E2E-0` o L2, declarar `FROZEN`.

**Estados de evidencia:** `OBSERVED-STATIC` para código/configuración; `REPORTED-LOCAL` para transcripciones de PowerShell; `REQUIRED` únicamente si hay regla efectivamente FROZEN aplicable; `PROPOSED-CONTROL` para este instrumento; `NOT VERIFIED` para controles no probados; `DECISION REQUIRED` para actos pendientes.

## 3. Hechos de partida auditados y hallazgos acotados

| ID instrumental | Hecho y fuente | Implicación técnica | Límite de inferencia |
|---|---|---|---|
| `AS-01` | Compose base arranca `llm_worker` con `python runtime/engine.py`; `IS_BENCHMARK=1`. | La configuración base **no puede usarse como prueba PDF→PDF productiva** por sí misma. | No acredita corrida. |
| `AS-02` | Golden cambia `IS_BENCHMARK=0`, pero no cambia el entry point; Engine también deriva nodos sintéticos si `document_id.startswith('doc_')`. | Requiere registrar el ID efectivo; *no* simular como entrada OCR un ID `doc_` sin verificar la semántica. | La entrada PDF por OCR deriva `document_id=SHA256(bytes)`, no el nombre del archivo. |
| `AS-03` | `engine.py` lee `GROQ_API_KEY`; la factory selecciona `groq` por defecto; ambas variantes Compose declaran claves de Gemini pero no `GROQ_API_KEY` para `llm_worker` en el modelo inspeccionado. | `INCOMPATIBLE-STATIC` para el wiring declarado; el entorno runtime real aún no fue ejecutado. | El guard de clave está en `run_pipeline`, **después** del sondeo de cola; no afirmar fallo inmediato al iniciar. |
| `AS-04` | `GroqProvider` construye `AsyncGroq(api_key=...,max_retries=...)` y llama `chat.completions.create(...)`. | Se precisa fake **Groq/OpenAI-compatible**, no API `generateContent` Gemini. | El SDK documenta `GROQ_BASE_URL` en versiones publicadas; la versión local y su precedencia requieren verificación. |
| `AS-05` | Compose base declara `./:/app`, volumen `sqlite_data:/app/infra/db`, `chaos_net` bridge; fake/proxy publican puertos 8000, 8443, 8474. | Perímetro actual no es descartable ni restringe egress Groq por diseño. | La ausencia de ejecución no acredita accesibilidad efectiva ni compromiso. |
| `AS-06` | OCR mueve PDFs de `data/inbox` a `data/archive/error`; ASTRegistry escribe `data/ast_cache`; Assembler escribe bajo `output` por defecto. | Las bases aisladas **no bastan**: archivos y carpetas de aplicación deben segregarse. | Los paths finales dependen de CWD/APP_ROOT y montajes efectivos. |
| `AS-07` | Corpus manifest `v3.9`: owner comparó SHA-256 de 21/21 PDFs con sus entradas; `FASE_5_BENCHMARK_METHODOLOGY` documenta corpus sellado. | Usar copia del PDF elegido; originales y oráculos separados y preservados. | Integridad de PDFs contra manifest ≠ elección de PDF para E2E-0 ≠ veredicto científico. |
| `AS-08` | `Dockerfile` contiene `COPY requirements.txt .` y descarga Tectonic 0.15.0 sin hash anclado visible. | Antes de build, comprobar disponibilidad reproducible de requirements y artefacto Tectonic. | `requirements.txt` **no figuró** en el listado raíz versionado ni respondió la lectura de GitHub del commit consultado: no demuestra si existe localmente/generado, ni que el build falle. |
| `AS-09` | `.dockerignore` consultado no contiene exclusión explícita de `.env`; `Dockerfile` termina `COPY . /app/`. | El contexto de build puede incluir secretos si se construye desde un árbol con `.env`; copiar código y archivos con `.env` a una imagen **no es aceptable para el arnés**. | No se realizó build ni se encontró ningún secreto en imagen. |
| `AS-10` | Docker Compose CLI `2.40.3`: el owner comparó modelo base y base+golden sin interpolación, con claves y flags inocuos. | Ya están probadas las diferencias **de los campos inspeccionados** y que ambos contienen 8 servicios. | No implica validación de todos los campos, red ni runtime. |

## 4. Arquitectura instrumental propuesta — fronteras de confianza

```text
HOST DEL OWNER — FUERA DEL ENSAYO
  checkout original (git / .env / corpus / oráculos / DB históricos)
  └─ SIN MONTAR COMO ESCRIBIBLE EN NINGÚN SERVICIO DE PRUEBA

ÁREA EXTERNA DESCARTABLE — RUN-ID Y PATHS CONTROLADOS
  source_snapshot/       código del commit elegido (sin .git/.env/credenciales)
  evidence/              logs saneados, hashes, manifest y snapshots
  runtime_data/
    inbox/                SOLO COPIA de PDF preregistrado
    archive/ error/ ast_cache/ output/
  volumes/               datos SQLite y caches exclusivos
  audit_config/          Compose efectivo inspeccionado + reglas declaradas

RED DE ENSAYO EXCLUSIVA (internal; sin red pública ni publicaciones)
  ocr_router ── queue/FSM ── engine ── materialized ── assembler
                               │
                               └── fake Groq (API chat.completions)
                                      ↑
                               GROQ_BASE_URL candidata;
                               requiere comprobación del SDK

EVIDENCIA → capturada fuera de directorios de escritura del pipeline
```

**Perímetro host:** `source_snapshot` procede de un commit fijo y se monta solo lectura si el layout funcional lo permite; si se utiliza un snapshot de código **escribible en el sandbox**, se registra expresamente ese menor aislamiento y nunca se utiliza el checkout original. `evidence/` no se monta read-write en procesos innecesarios. No montar el socket Docker, carpetas personales, `.env` real, claves, volumen de producción ni corpus/oráculos canónicos dentro del contenedor.

**Perímetro de build:** compilación de la imagen, descarga Tectonic y paquetes Python son una etapa separada de runtime y podrán requerir internet tras autorización explícita; **no confundir** acceso de red en build con acceso de red del contenedor en L1. Build a partir de un contexto mínimo saneado, sin `.env`, `.git`, PDFs del corpus completo, bases de datos existentes, evidencias ni ficheros sensibles. Evitar filtrar secretos por capas o logs. Capturar hash/digest de la imagen y procedimiento reproducible; un `FROM python:3.11-slim` mutable y binarios sin checksum no constituyen build hermético.

**Perímetro runtime:** la única red permitida a los servicios ensayados debe ser la interna dedicada; `internal: true` por sí solo no suprime otras redes o rutas y se debe verificar la membresía real. `network_mode: host`, servicios puente con red externa y publicaciones de puertos son motivos de rechazo salvo excepción aprobada y justificada. Control negativo de egreso se hace **después** de levantar un harness vacío/autorizado, con destino inocuo y sin corpus ni credencial real.

## 5. Matriz de rutas de escritura — cobertura mínima

| Consumidor | Destino en contenedor | Naturaleza | Política propuesta | Evidencia de verificación |
|---|---|---|---|---|
| OCR | `/app/data/inbox` | Input consumible/movible | Solo copia temporal de PDF; jamás archivo original | Hash copia pre/post y logs de movimiento |
| OCR | `/app/data/archive`, `/app/data/error` | Resultados de ingesta | Directorios descartables de corrida | Snapshot y hashes, sin tocar árbol original |
| OCR/Engine/Assembler | `/app/data/ast_cache` | AST persistente | Área de datos compartida entre procesos de esa corrida, descartable | AST recuperable desde proceso nuevo |
| Bootstrap/daemons | `/app/infra/db` | FSM/queue/event/materialized/documents/rate-limit/cache potencial | Volumen nuevo de la corrida, exclusivo; verificar DB completas y rutas absolutas/reales | Paths efectivos, `PRAGMA database_list`, snapshots coherentes |
| Assembler | `/app/output` o `COMPILER_OUTPUT_DIR` | PDF final | Salida única para RUN-ID; no compartir con repo original | Archivo, validez y hash o ausencia acreditada |
| Tectonic/modelos | `/app/.cache/tectonic`, `.cache/hf`, `.cache/torch`, `/tmp` | Cachés/temporales | Separar por build/harness, evitar caches productivas; `/tmp` apto para escrituras | `mount inspect`, flags, permisos |
| Código | `/app/apps`, `/app/core`, `/app/infra` (excepto DB), `/app/runtime` | Fuente | Código de commit fijo e idealmente solo lectura | Resolución de source mount y test negativo en sandbox |
| Corpus/oráculos | `/app/tests/corpus` (si es necesario) | Datos sellados | Preferentemente NO montar; excepcionalmente RO en sandbox. Jamás host original writable | Inventario de mounts y hashes pre/post |
| Expediente | Fuera del espacio manipulable del pipeline | Custodia | Captura separada y saneada, con acceso controlado | Manifest SHA-256 y correlación a RUN-ID |

**Regla de submontajes:** los mounts se fusionan por destino según Compose. Agregar una línea `tests/corpus:ro` **no neutraliza** automáticamente el `./:/app` original. Proponer reemplazo total de `volumes` para cada servicio (p. ej., `!override` compatible con Compose >=2.24.4) y comprobar que ningún bind apunta a la raíz original. La protección debe medirse sobre **configuración efectiva**, no leyendo fragmentos YAML. Si se exige rootfs read-only, enumerar `/tmp` y demás rutas imprescindibles antes de activarlo; no introducir errores instrumentales silenciosos que luego parezcan defectos del producto.

## 6. Política de red y servicios del arnés

| Elemento | Diseño propuesto | Condición comprobable |
|---|---|---|
| Red de traducción | Bridge dedicada `internal: true`, solo servicios de prueba | Única red conectada por servicio; sin `network_mode=host`; `network inspect` en harness |
| Fake Groq | Servicio interno sin publicación de puerto host | El SDK Groq recibe exclusivamente peticiones previstas; request counters/correlación |
| Toxiproxy/fake Gemini heredados | Excluirlos del runtime **si la variante no los requiere**; no basta omitirlos del overlay | Ausencia en modelo efectivo/servicios iniciados, o inactivos y sin puertos/salida si su presencia resultara inevitable |
| Puertos `8000/8443/8474` | Ningún puerto público en variante aislada | `ports=[]` por servicio; `docker ps/inspect` sin host publish |
| Salida pública | Denegada para cada contenedor de runtime | Control negativo de DNS/socket/HTTP inocuo; no se permite excepción “temporal” para Groq real |
| SDK endpoint | `GROQ_BASE_URL` **hipótesis documentada**, con versión local comprobada | URL resuelta de runtime apunta a fake interno y nunca a `api.groq.com`; si SDK no lo admite, `NO ELEGIBLE` hasta decisión de instrumentación distinta |
| Credenciales | `GROQ_API_KEY` ficticia solo en harness | No hay credenciales reales en entorno, imagen, `docker inspect`, logs o comandos compartidos |
| Dependencias | Imagen y fake construidos antes de cerrar la red | Se distinguen claramente stages build y runtime; no hay pull en medio de L1 |

**Precaución:** utilizar una clave ficticia sin redirección y sin bloqueo efectivo **no es seguro**: el SDK podría enviar datos a un endpoint externo. Nunca “probar primero para ver si falla” usando red abierta.

## 7. Contrato exacto del proveedor Groq controlado

### 7.1 Base de código inspeccionada

- `GroqProvider.translate()` usa `AsyncGroq.chat.completions.create(model=envelope.model_name, temperature=1e-5, stream=False, **kwargs)`.
- `OpenAICompatibleDialect.build_request_kwargs()` construye `messages=[system,user]` y `response_format={"type":"json_object"}`.
- `PromptRenderer.render()` exige que el modelo responda únicamente JSON con la clave raíz `content`.
- `OpenAICompatibleDialect.parse_response()` lee `choices[0].message.content`, decodifica JSON, busca `content`, y lee `usage.prompt_tokens`, `usage.completion_tokens`, `choices[0].finish_reason`.

### 7.2 Contrato de integración propuesto (NO fake implementado)

| Dimensión | Comportamiento exigible en prueba de contrato | Falso positivo que evita |
|---|---|---|
| Endpoint | Ruta de SDK **realmente emitida** al endpoint fake; prever `/openai/v1/chat/completions` según SDK, verificar por log/trace. | Endpoint aparente configurado pero no utilizado. |
| Método | `POST`, cuerpo JSON con `model`, `messages`, `response_format.type=json_object`, `stream=false`. | Fake responde bien a un HTTP que el adapter no invoca. |
| Formato | `choices[0].message.content` es **string que contiene JSON válido**, por ejemplo `{"content":"texto controlado"}`; `finish_reason="stop"`. | Respuesta Gemini `candidates[]` aceptada indebidamente como Groq. |
| Usage | `usage.prompt_tokens` y `usage.completion_tokens` numéricos coherentes con contrato; tiempos del adapter observados. | `InferenceResult` parcialmente inventado. |
| Determinismo | Fixtures fijos o función determinista sobre ID/payload normalizado; mismo input/config produce mismo resultado; casos de error explícitos separados. | Semilla aleatoria tratada como garantía de determinismo de traducción. |
| Semántica | El fixture conserva, cuando corresponda, restricciones de estructura matemáticas/código/PRESERVE; evita traductor Caesar arbitrario. | Un falso PASS por respuesta que vulnera validadores o ciencia. |
| Correlación | Registrar `RUN-ID`, document_id/chunk_id y request ID cuando sean transmitidos; nunca inventar un ID ausente. | Contabilizar intentos repetidos como uno solo. |
| Fallos | Casos 429/500, timeout, malformed *solo* en harness verification/L2 autorizado. L1 normal sin fault injection. | Contaminación de L1 por prueba de caos. |

**Fixture de forma ilustrativa, no oráculo científico ni implementación:**

```json
{
  "id": "chatcmpl-audit-fixture-001",
  "object": "chat.completion",
  "created": 0,
  "model": "fixture-model-id",
  "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\"content\":\"TEXTO_CONTROLADO\"}"}, "finish_reason": "stop"}],
  "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
}
```

**No afirmar conformidad SDK por la forma ilustrativa:** versionado de SDK y compatibilidad efectiva con campos obligatorios aún se verifican. Un harness que devuelve siempre `TEXTO_CONTROLADO` puede demostrar transporte, pero no validación semántica ni completitud PDF→PDF. Las respuestas del ensayo deben preregistrarse sin ajustarlas post hoc al resultado.

## 8. Riesgos de fidelidad experimental

1. **Instrumentar sin remediar:** cambiar `GROQ_BASE_URL` y red no modifica lógica de Engine, pero sí la configuración de I/O; fingerprint de variante obligatorio.
2. **Ruta sintética:** `IS_BENCHMARK=1` o `document_id.startswith('doc_')` mantiene falsas terminalidades. No borrar este comportamiento histórico; clasificar baseline y variante por separado.
3. **Primer error:** doble `ATTACH fsm_db` observado en inspección estática puede anteceder al guard Groq; `chunk_id/node_id` puede impedir ejecutar inferencia. No anticipar qué fallo cronológico observará L1.
4. **Errores de arnés:** si la imagen carece de `requirements.txt`, la red bloquea dependencias inevitables o el filesystem no tiene rutas de escritura, clasificarlos como `HARNESS_FAILURE / NO ELEGIBLE — PRECONDICIÓN`, no como defecto nuevo de producto.
5. **Continuidad:** un fixture Groq válido y un Engine que complete un task no prueban AST real, ensamblado, perfil persistente o PDF atribuible.
6. **No sobreleer el golden:** solo cambia variables específicas; fake/proxy podrían seguir declarados y el Engine sigue seleccionando Groq. Nunca iniciar golden como modo de auditoría seguro.

## 9. Matriz de verificación del arnés — criterios falsables propuestos

Estos son **controles instrumentales**, no un nuevo gate normativo del Charter. **Todos están `NOT VERIFIED` hoy.** Un resultado negativo produce evidencia y suspende L1; no se corrige silenciosamente dentro de la misma corrida.

| Control | Evidencia requerida para PASS de harness | Resultado que bloquea L1 |
|---|---|---|
| `HV-01` Código | Commit completo y diff del snapshot; origen sin contaminación; imagen identificada por digest. | No se puede reconciliar código/copia/imagen. |
| `HV-02` Build | `requirements.txt` y demás insumos resueltos en checkout reproducible; Tectonic realmente ejecutable en imagen; procedimiento/digest. | Falla de build o binario ausente, desconocido. |
| `HV-03` Secretos | `.env` original fuera del build context, imagen, contenedores; solo dummy en harness. | Cualquier ruta o valor real expuesto. |
| `HV-04` Mounts | Inventario *de todos los servicios*, con source absoluto y `read_only`; ninguna escritura posible en checkout/corpus originales. | Fuente original visible writable o ruta desconocida. |
| `HV-05` Bases y rutas | DB/AST/inbox/archive/output/temp resueltos a destinos nuevos del RUN-ID. | Uso de datos, paths o volúmenes compartidos no autorizados. |
| `HV-06` Red | Única red interna efectiva por contenedor; sin puertos publicados ni bridge externa. | Interfaz adicional, puerto administrativo o acceso al host no previsto. |
| `HV-07` Egress | Prueba negativa inocua hacia dominio público en runtime sin corpus/credencial real; registro de resultado. | Tráfico externo exitoso o resultado ambiguo sin demostración complementaria. |
| `HV-08` SDK | Versión y precedencia de `GROQ_BASE_URL` inspeccionadas; endpoint efectivo interno y headers/cuerpo correlacionados. | SDK apunta fuera o URL no acreditada. |
| `HV-09` Fake | Request/response compatible con SDK, Dialect y Renderer; repetición determinista. | 404, parsing errors del fake, respuesta aleatoria u oracle ajustado. |
| `HV-10` Inmutabilidad | Prueba negativa de escritura contra copia de referencia RO **dentro del sandbox**, hashes original pre/post idénticos. | Escritura permitida o test ejecutado contra checkout del owner. |
| `HV-11` Reversibilidad | Parada/limpieza solo por recursos etiquetados de RUN-ID; evidencia queda fuera de volúmenes temporales. | Destrucción de otros proyectos o expediente. |
| `HV-12` Procedencia | Config saneada, hashes, UTC, autor, comandos, desviaciones; sin A/B/C. | Evidencia sin correlación o divulgación de secretos. |
| `HV-13` Cobertura real | Servicio `ocr_router`, `llm_worker`, `assembler`, reconciler, bootstrap y auxiliares elegidos justificados; ausencia de residuos no deseados. | Toxiproxy/fake Gemini activos por herencia sin justificación o servicios requeridos omitidos. |
| `HV-14` Comparabilidad | Tabla AS-IS→harness de cada delta; `IS_BENCHMARK`, ID documental y ruta definidos. | Resultado atribuido falsamente a configuración AS-IS intacta. |
| `HV-15` Snapshot DB | Método coherente SQLite (backup API/pausa coordinada o evidencia de WAL), accesibilidad desde nueva conexión. | Copia inconsistente o atribución de durabilidad no observada. |
| `HV-16` Permisos | Owner/autoridad de ensayo y límites de acciones autorizadas documentados; Charter/L1 aprobados antes de ensayo. | Autorización no disponible. |

### 9.1 Verificación de config sin daemon (cuando exista una implementación revisada)

Sin desplegar contenedores, inspeccionar `docker compose -f ... config --no-interpolate --format json` y proyectar **nombres y flags inocuos**, nunca valores secretos. Si el tipo de `environment` cambia a arreglo, normalizarlo: el owner ya encontró que leer `.PSObject.Properties.Name` de un `Object[]` produce `Count/Length/...` y no variables reales. Verificar especialmente `services[*].volumes`, `.networks`, `.ports`, `network_mode`, `.privileged`, `extra_hosts`, `environment` (nombres), `env_file`, `secrets`, `build`, `depends_on`, y `networks[*].internal`.

Para overrides de Compose, usar `!override` o `!reset` **solo después de verificación en versión local** y resolver rutas relativas según el primer archivo Compose. No inferir que `!reset` de puertos remueve `expose` o que eliminar `depends_on` elimina el servicio. **Si el overlay no puede acreditar el grafo entero con confianza, preferir composición dedicada explícita.**

## 10. Secuencia operativa propuesta (SIN EJECUTAR AHORA)

| Fase | Salida | Autoridad / condición |
|---|---|---|
| **D0** — Diseño actual | Esta especificación; trazabilidad de requisitos, amenazas y controles, preguntas abiertas. | Aprobación del diseño ≠ aprobación de desarrollo/ejecución. |
| **D1** — Cierre del diseño | Elegir *overlay verificado* o *manifest explícito*; aprobar esquema de fixtures Groq, selección de servicios, mounts/red y repositorios de insumos. | Owner técnico confirma alcance instrumental, sin elegir ruta canónica. |
| **I0** — Construcción de arnés | Código de fake/Compose **fuera del núcleo funcional**, con tests de contrato y linter; commit propio y diff trazable. | Autorización expresa antes de crear o cambiar archivos del repo. |
| **HV** — Harness Verification | Ejecutar `HV-01…HV-16` en entorno descartable con logs y evidencias. | Aprobación de L0 operacional; sin PDF canónico ni proveedor real. |
| **P0** — Elegibilidad L0 | `ELIGIBLE / NO ELEGIBLE — PRECONDICIÓN / UNKNOWN` por ruta/variante. | Criterios de Atlas §9 y Charter aplicable. |
| **L1** — E2E-0 | Una corrida por ruta elegible con PDF+SHA autorizado, CP-00…CP-12, outcome A/B/C. | Aprobación Charter/autoridad, proveedor controlado compatible, aislamiento probado. |
| **POST** — Reconciliación | Evidencia en Atlas §§8–12 y decisión posterior del Board. | No retroeditar AS-IS ni emitir GAP formal sin unidad gobernada. |

### 10.1 Prueba de separación de fases

- **D0/D1:** prohibido ejecutar código de producto o construir imágenes; solo lectura, verificación documental y planificación.
- **I0:** permite crear instrumentos **solo si hay autorización adicional expresa**; no cambiar rama AS-IS ni fixtures del corpus.
- **HV:** permite pruebas de harness sin PDF del corpus; ni éxito ni fracaso se traslada a A/B/C.
- **L1:** única etapa que puede producir outcome A/B/C; todo `NO ELEGIBLE` y `NO EJECUTADO` mantiene `execution_outcome=null`.

## 11. Preguntas todavía abiertas — no resolver por suposición

| Pregunta | Por qué importa | Siguiente evidencia segura |
|---|---|---|
| ¿`requirements.txt` está en el checkout local y cómo se genera desde `pyproject.toml`? | El Dockerfile intenta copiar ese archivo. | `git ls-files --error-unmatch requirements.txt` y `Test-Path` sin mostrar contenido. |
| ¿Qué versión local del paquete `groq` se usa y admite `GROQ_BASE_URL`? | Permitiría redirección de endpoint sin editar `GroqProvider`. | `importlib.metadata.version('groq')`; código fuente SDK local sin secretos. |
| ¿Se dispone de un mecanismo de build reproducible aprobado? | Descarga de Tectonic/paquetes y tagged base mutable no demuestran cadena reproducible. | Inspección de lock/constraints, requisitos versionados, políticas de hashes; sin construir. |
| ¿Qué fichero/servicios deben integrarse para cada ruta L1, especialmente R1 fuera de Compose y R3 fuera del base? | Evitar falsos resultados por excluir un productor/consumidor. | Mapa explícito de dependencias y autoridad de ensayo por ruta. |
| ¿Qué exacto PDF se autoriza entre los del corpus y cómo se copia sin tocar el original? | Preregistro comparativo por ruta. | Decisión owner/Board; manifest y hash local ya comparados 21/21. |
| ¿Qué aprobación rige el desarrollo del arnés y su ejecución? | Evitar convertir un draft en mandato de cambios funcionales. | Acta owner/Board según Charter y metodología, con scope, operador, límites y fecha. |

## 12. Primeras verificaciones locales seguras (opcional, D1 documental)

El owner puede inspeccionar **solo dos incertidumbres**, sin Docker daemon, sin abrir `.env`, sin llamadas externas y sin escribir archivos:

```powershell
# Desde la raíz del repositorio. No ejecuta el producto ni instala paquetes.
Write-Output '=== INPUT DE BUILD ==='
[pscustomobject]@{
  RequirementsPresent = Test-Path -LiteralPath 'requirements.txt' -PathType Leaf
  RequirementsTracked = (@(git ls-files -- 'requirements.txt').Count -gt 0)
  PyprojectPresent = Test-Path -LiteralPath 'pyproject.toml' -PathType Leaf
}

Write-Output '=== GROQ SDK INSTALADO EN VENV ==='
@'
from importlib import metadata
try:
    print('groq_version=' + metadata.version('groq'))
except metadata.PackageNotFoundError:
    print('groq_version=NOT_INSTALLED')
'@ | python -
```

Si falla el descubrimiento de paquete por plataforma, registrar el error y usar `python -m pip show groq` mostrando solo nombre/versión (no listar credenciales). La versión del SDK es **metadato**, no test de URL ni prueba de integración. No inspeccionar o compartir valores de variables del host.

## 13. Criterio de salida de esta especificación

Este documento puede declararse `DESIGN REVIEWED` cuando:

- [ ] Hay aprobación de su alcance por el owner técnico, **sin reclamar autoridad del Charter**.
- [ ] Se decidió la forma concreta de composición y se adjuntó un diff completo y verificable del despliegue AS-IS.
- [ ] Se confirmó viabilidad documental de construir desde commit fijo con insumos presentes y sin secretos.
- [ ] Se aprobó contrato de fake Groq con fixtures preregistradas.
- [ ] Se aprobó mapa de mounts/red y control negativo de protección del checkout original.
- [ ] Existe lista de responsables, permisos, secuencia de HV y plan de parada/reversibilidad.
- [ ] Se mantiene una separación explícita de D1, I0, HV y L1.

**Aunque esta lista se satisfaga, PF-08/PF-09 NO pasan a `SATISFECHO` hasta las verificaciones físicas posteriores.** Ningún resultado A/B/C se asigna antes de L1.

## 14. Referencias (por identidad inmutable)

**Fuentes de repositorio — commit `4b9fc2c3c692ad87402855235d4dedd0e7d8db5f`:**

- [Atlas, §9](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md)
- [Charter, §6.1](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/PIPELINE_STABILIZATION_AUDIT_CHARTER.md)
- [Expediente E2E-0 publicado](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md)
- [Compose base](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docker-compose.yml); [golden overlay](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docker-compose.golden.yml); [Dockerfile](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/Dockerfile); [`.dockerignore`](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/.dockerignore)
- [Engine](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/runtime/engine.py); [factory de proveedores](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/bootstrap/provider_stack_factory.py); [adaptadores](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/llm_workers/adapters.py)
- [Groq dialect](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/core/prompting/dialects/openai_compatible.py); [renderer](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/core/prompting/renderer.py); [OCR](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/ocr_router/__main__.py); [ASTRegistry](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/core/ast/registry.py); [Assembler](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/compiler/__main__.py)
- [Benchmark methodology F17-BIS v1.2.0](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/phase-17-bis/reviews/FASE_5_BENCHMARK_METHODOLOGY.md)

**Referencias externas de comportamiento instrumental (no autoridad del proyecto):**

- [SDK Groq Python — configuración `GROQ_BASE_URL`](https://github.com/groq/groq-python)
- [Docker Compose — Merge](https://docs.docker.com/reference/compose-file/merge/)
- [Docker Compose — Networks/internal](https://docs.docker.com/reference/compose-file/networks/)
- [Docker Compose — Port publishing](https://docs.docker.com/engine/network/port-publishing/)

---

**Veredicto:** `DOCUMENTAL DESIGN PREPARED / IMPLEMENTATION NOT AUTHORIZED / HARNESS NOT VERIFIED / L0 PARTIAL / L1 NOT EXECUTED / OUTCOME null`.
