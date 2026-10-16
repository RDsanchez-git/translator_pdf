# L0 — Revisión de aislamiento físico, egress y elegibilidad (PF-08/PF-09)

**Estado:** `DRAFT — STATIC DESIGN REVIEW / NOT AUTHORIZED FOR EXECUTION`; revisión complementaria de configuración `base`/`base+golden`  
**Fecha de inspección:** 2026-10-15  
**Repositorio:** `RDsanchez-git/translator_pdf`  
**Commit documental verificado:** `4b9fc2c3c692ad87402855235d4dedd0e7d8db5f`  
**Documento operativo subordinado:** `docs/architecture/adr/pipeline-stabilization/00-foundation/E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md`, §4 PF-08/09, §§5, 9, 10, 13  
**Autoridad de prerregistro:** `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` v0.1.0 `DRAFT`, §6.1, **no aprobado**  
**Protocolo de observación:** Atlas v0.2.15, §9; `L1 NO EJECUTADO`, `execution_outcome=null`.

> Este anexo es un análisis estático auxiliar, no un nuevo gate normativo, una decisión del Board ni una propuesta de cambios funcionales. No ejecutar las configuraciones de ejemplo implícitas en esta revisión. No contiene claves ni instrucciones para contactar un proveedor real.

## 1. Resultado ejecutivo

**PF-08 — `NO ACREDITADO`:** Engine selecciona Groq (`GROQ_API_KEY` y `build_provider_stack` sin `provider_type`; default `groq`), pero la infraestructura declarada de control es un fake de Gemini mediante Toxiproxy. No existe prueba de sustitución compatible ni bloqueo de egress de Groq. El fake Gemini no equivale a un interceptor OpenAI/Groq; Toxiproxy es un proxy configurado para tráfico dirigido a él, no una política global de salida. El `GEMINI_API_URL` de Compose no demuestra controlar el SDK `AsyncGroq`.

**PF-09 — `NO ACREDITADO`:** el anchor Compose monta `./:/app` y un volumen `sqlite_data:/app/infra/db`. Aunque `infra/db` quede bajo el volumen anidado, `data/inbox`, `data/archive`, `data/error`, `data/ast_cache`, `output/`, rutas auxiliares y cualquier otra ruta escribible bajo `/app` siguen exponiendo el árbol del host. Un nombre de proyecto Compose distinto no elimina el riesgo de escritura del bind mount. **No lanzar el Compose vigente contra el árbol de trabajo del owner**.

**Hallazgo nuevo de seguridad instrumental:** los servicios `fake-gemini` y `toxiproxy` publican puertos de host (`8000:8000`, `8443:8443`, `8474:8474`), sin binding explícito a loopback en la configuración inspeccionada. `depends_on` comprueba orden/salud de procesos, **no** demuestra aislamiento de tráfico ni que el proveedor efectivamente llamado sea ese fake.

**Diferencia de estados:** `OBSERVED-STATIC` describe código y YAML versionados; la efectividad de aislamiento, build/imagen, firewall y una corrida `L1` es `UNKNOWN/NOT VERIFIED`. No hay resultado A/B/C, incidente observado, `GAP` formal ni severidad P0–P2 asignada.

## 2. Evidencia primaria por superficie

| Superficie | Referencia del commit | Observación estática | Límite de inferencia |
|---|---|---|---|
| Compose base | `docker-compose.yml` anchor `x-worker-base`, líneas 1–49 | `./:/app` y `sqlite_data:/app/infra/db`; `chaos_net` bridge | No acredita contenedores iniciados ni paths efectivos del host de una corrida |
| Servicios | `docker-compose.yml`, líneas 181–235 | Toxiproxy `8443`, API admin `8474`, fake `8000` publicados | Publicar puertos no demuestra explotación ni contacto real |
| Fake | `apps/daemons/fake_gemini.py` | `/v1beta/models/{model}:generateContent`; RNG sembrable, no obligatoriamente sembrado; respuesta sintética | No acredita compatibilidad de payload con parser Groq/OpenAI ni ciencia PDF |
| Proxy | `toxiproxy.json` | upstream `fake-gemini:8000`, escucha `:8443` | No aplica una denegación de salida general |
| Selector | `runtime/engine.py`, líneas ~73–110; `apps/bootstrap/provider_stack_factory.py`, líneas ~23–58 | Lee `GROQ_API_KEY`, pasa `api_key` sin tipo; valor predeterminado `groq` | Si la clave no llega al proceso, falla al llegar a la validación; no se observó orden cronológico real |
| Groq SDK | `apps/llm_workers/adapters.py`, líneas ~17–29 | Inicializa `AsyncGroq` sin `base_url` alternativo explícito | No inferir ausencia absoluta de configuraciones de SDK no inspeccionadas, pero no hay ruta controlada acreditada |
| OCR | `apps/ocr_router/__main__.py`, líneas ~40–62, ~74–193 | Crea `data/inbox`, `archive`, `error`; mueve físicamente los PDF procesados | Un PDF sellado no debe inyectarse desde su ubicación canónica |
| AST | `core/ast/registry.py`, líneas ~15–20 | Escribe `data/ast_cache` relativo a workspace | Proteger solo SQLite es insuficiente |
| Compilación | `apps/compiler/__main__.py`, líneas ~153–160 | `COMPILER_OUTPUT_DIR` default `output` y crea salida | Sin volumen/espacio de salida aislado, el bind puede escribir en el host |
| Bootstrap | `infra/db/bootstrap.py`, líneas ~13–57 | Crea/inicializa esquemas persistentes bajo `infra/db` | No ejecutarlo contra bases existentes |
| Golden | `docker-compose.golden.yml`, líneas ~33–46 | `IS_BENCHMARK=0`, API Gemini externa; fake/proxy del base no son eliminados por ello | No es sustituto del proveedor controlado ni cierre E2E |

**Nota:** las líneas son ubicaciones orientativas contra ese commit. Para cita formal, fijar enlaces inmutables y rangos exactos al formalizar evidencia. Ninguna frase equivale a una prueba de aislamiento efectiva.

## 3. Modelo mínimo de amenazas de ensayo

| Riesgo | Condición de exposición | Control que deberá demostrarse antes de L1 | Evidencia admisible |
|---|---|---|---|
| Modificación de corpus sellado | `./:/app` es escribible; corpus bajo árbol host | Corpus/GT fuera del workspace ejecutable o montado read-only; copia de PDF seleccionada como input | Mounts efectivos, prueba negativa de escritura **solo en sandbox**, hashes pre/post |
| Destrucción o contaminación de DB | `sqlite_data` persistente, alias/bind y scripts bootstrap | DB/volúmenes nuevos exclusivos de corrida, sin compartir nombre/path con datos del owner | Mapa de mounts, volúmenes y snapshots de estado inicial |
| Alteración del input | OCR usa `shutil.move` hacia archive/error | Solo usar copia reproducible del PDF de entrada; original intocable | Hash origen y copia, rutas pre/post, trazas OCR |
| Egress o coste real | Groq SDK sin sustitución de endpoint probada | Salida de red negada por mecanismo externo verificable y adapter controlado compatible, antes de conectar credenciales | Política de red efectiva, test negativo controlado, registro de destino real del socket en ensayo aprobado |
| Exposición de fake/admin | Publicación `8000`, `8443`, `8474` | Interfaces solo donde sean necesarias; no exponer admin a red no confiable | Config efectiva saneada, bindings de host, revisión de puertos |
| Resultados no comparables | Benchmark mode/ramas sintéticas por `doc_` | Sujetos y fingerprints distintos para Compose base, overlay, CLI y daemon | Manifest de flags y SHA, frontera `CP-03` AST real/sintético |
| Evidencia incompleta | DB WAL activo, logs sin correlación | Captura consistente; no sobrescribir ni editar datos capturados | Log con UTC/run ID y checksums; backup consistente o limitación `UNKNOWN` |

## 4. Criterios de aceptación instrumental (propuestos, subordinados al Charter)

**Para concluir PF-08 en una configuración concreta:** (1) adapter y endpoint real resueltos y registrados sin secretos; (2) respuesta determinista conforme al contrato esperado y al dialecto realmente invocado; (3) aislamiento efectivo de red demostrado, no inferido de `GEMINI_API_URL`; (4) la prueba de compatibilidad no altera el sujeto AS-IS sin registrar variante; (5) ninguna credencial real presente en el ensayo L1. Hasta entonces `NO ACREDITADO`.

**Para concluir PF-09 en una configuración concreta:** (1) tabla exhaustiva host→contenedor de mounts, para todos los servicios y overrides; (2) el directorio de trabajo original y los oráculos sellados quedan imposibles de escribir desde los procesos ensayados; (3) DB, AST cache, inbox, archive/error y output están en destinos descartables identificados; (4) los procesos no comparten volúmenes/estado previos; (5) logs, checkpoints y snapshots sobreviven a detener la corrida; (6) hay plan de restauración/detención ensayado fuera del repositorio. Hasta entonces `NO ACREDITADO`.

**Restricción epistemológica:** un test negativo aislado de egress o de escritura no demuestra ausencia universal de caminos alternos. El veredicto es por configuración y perímetro concretos.

## 5. Próxima adquisición estática permitida al owner (PowerShell)

Estos comandos únicamente proyectan campos de la configuración declarativa **sin interpolar `.env`** y no arrancan el daemon. Docker Compose CLI debe estar disponible, pero **no** necesita que el daemon Linux funcione para analizar archivos. Si falla el parseo, conservar el error saneado. Revisar la salida antes de enviarla.

```powershell
# Ejecutar desde raíz del repositorio. No modifica ningún archivo.
# --no-interpolate evita resolver variables desde .env.
$combos = @(
  @{ Label='base'; Files=@('docker-compose.yml') },
  @{ Label='base+golden'; Files=@('docker-compose.yml','docker-compose.golden.yml') }
)
foreach ($combo in $combos) {
  $argsCompose = @()
  foreach ($f in $combo.Files) { $argsCompose += @('-f',$f) }
  $json = & docker compose @argsCompose config --no-interpolate --format json
  if ($LASTEXITCODE -ne 0) { Write-Output "CONFIG_PARSE_FAILED $($combo.Label)"; continue }
  $cfg = $json | ConvertFrom-Json
  Write-Output "=== $($combo.Label) ==="
  $rows = @(foreach ($name in @($cfg.services.PSObject.Properties.Name | Sort-Object)) {
    $svc = $cfg.services.$name
    $envNames = @()
    if ($null -ne $svc.environment) { $envNames = @($svc.environment.PSObject.Properties.Name | Sort-Object) }
    $mounts = @($svc.volumes | ForEach-Object { "{0}:{1}:{2}" -f $_.type,$_.source,$_.target })
    $ports = @($svc.ports | ForEach-Object { "{0}/{1} host_ip={2}" -f $_.published,$_.target,$_.host_ip })
    [PSCustomObject]@{
      Subject=$combo.Label; Service=$name
      Command=($svc.command -join ' ')
      EnvNames=($envNames -join ',')
      MountTypesAndTargets=($mounts -join ';')
      PublishedPorts=($ports -join ';')
      NetworkNames=((@($svc.networks.PSObject.Properties.Name)) -join ',')
    }
  })
  $rows | Format-List
}
```

**Observación:** el resultado se mantiene exclusivamente en memoria y se filtran las propiedades antes de imprimir. **No publicar nunca la salida cruda de `docker compose config --format json`: podría contener secretos**. Este script imprime nombres de variables, no sus valores, pero muestra rutas y nombres de red/volumen que también merecen revisión antes de compartirse.

## 6. Resultados y decisión de avance

- `PF-02`: 21/21 PDF SHA-256 cotejados contra el manifiesto v3.9 (owner); no habilita elección de documento.
- `PF-06`: Dockerfile instala *si el build llega a completarse* Tectonic 0.15.0; imagen y binario no inspeccionados.
- `PF-07`: `INCOMPATIBLE-STATIC` en relación código/configuración declarada, efecto runtime condicional.
- `PF-08`: `NO ACREDITADO` para todas las rutas hoy inspeccionadas.
- `PF-09`: `NO ACREDITADO` para Compose actual. Riesgo de modificación del árbol host documentado.
- `R1/R2/R3`: ninguna variante hoy acreditada como elegible L1; elegibilidad debe ser evaluada individualmente y con autorización.
- `E2E-0/L1`: `NO EJECUTADO`, `execution_outcome=null`. El diagnóstico de aislamiento no es resultado C.

**Próximo paso:** obtener la proyección saneada de configuración y completar la tabla host→contenedor, sin iniciar ni compilar; después someter el diseño de aislamiento/egress y sujeto a autorización para L0 operativo, con separación explícita de una caracterización AS-IS y una variante instrumentada. Cualquier futura selección canónica/remediación sigue fuera de este anexo.

## 7. Referencias inmutables

- [Expediente L0 consolidado, commit `4b9fc2c3`](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md)
- [Atlas §9 v0.2.15, commit `4b9fc2c3`](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md)
- [Charter v0.1.0 DRAFT, mismo commit](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docs/architecture/adr/pipeline-stabilization/00-foundation/PIPELINE_STABILIZATION_AUDIT_CHARTER.md)
- [Compose base](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docker-compose.yml)
- [Compose golden overlay](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/docker-compose.golden.yml)
- [OCR router](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/ocr_router/__main__.py)
- [AST Registry](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/core/ast/registry.py)
- [Assembler](https://github.com/RDsanchez-git/translator_pdf/blob/4b9fc2c3c692ad87402855235d4dedd0e7d8db5f/apps/compiler/__main__.py)

---

## 8. Adenda — Valores proyectados de Compose base vs base+golden (L0, 2026-10-15)

**Origen:** transcripción PowerShell aportada por el owner, `docker compose -f … config --no-interpolate --format json`, selección local de variables de lista permitida. **Naturaleza:** `REPORTED-LOCAL-CONFIG` corroborable con Compose YAML versionado. El comando no inicia contenedores, no verifica variables efectivas dentro de procesos ni prueba tráfico. La salida no contiene valores de secretos; `GEMINI_API_KEY` fue deliberadamente excluida del volcado.

| Servicio | Propiedad | Base | Base + golden | Interpretación |
|---|---|---|---|---|
| `llm_worker` | `IS_BENCHMARK` | `1` | `0` | El overlay reemplaza el flag; todavía queda el disparador `document_id.startswith('doc_')` dentro de Engine. |
| `llm_worker` | `ENABLE_CHAOS_TEST` | `0` | `0` | No prueba que se eliminen servicios fake/proxy ni que exista red aislada. |
| `llm_worker` | `GEMINI_API_URL` | `http://toxiproxy:8443` | `https://generativelanguage.googleapis.com` | URL pública declarada en golden para clientes que la lean; no demuestra que Engine/Groq la utilice. |
| `llm_worker` | `MAX_CONCURRENT_CHUNKS`, `MAX_GLOBAL_LLM_CONCURRENCY` | `1`, `1` | `1`, `1` | Límites declarados sin ejecución. |
| `llm_worker` | `NODE_ID` | `llm_worker_alpha` | `llm_worker_alpha` | Identidad configurada. |
| `llm_worker` | `FSM_DB_PATH`, `QUEUE_DB_PATH` | `/app/infra/db/{fsm,queue}.db` | Igual | Destinos lógicos declarados, no estado SQLite aislado. |
| `assembler` | `ENABLE_CHAOS_TEST` | No declarado | `0` | El overlay añade variable a este servicio. |
| `assembler` | `FSM_DB_PATH`, `QUEUE_DB_PATH` | `/app/infra/db/{fsm,queue}.db` | Igual | No se demuestra acceso a bases aisladas. |

**Control cruzado de presencia, separado de valores:** el owner también proyectó las *claves* de `environment` y reportó `GROQ_API_KEY` ausente tanto en base como en base+golden para `llm_worker`; `GEMINI_API_KEY` presente en ambas. Esto acredita los valores configurados **en el modelo Compose inspeccionado**, no el entorno runtime que pudiera introducir otra fuente. En `engine.py`, el guard de `GROQ_API_KEY` está dentro de `run_pipeline()`, al cual llega el daemon después de consultar la cola en `__main__`; por tanto **no** es correcto afirmar que el proceso «siempre falla inmediatamente al iniciar» ni atribuir el primer error cronológico sin traza. Una conexión de cola y el scheduler pueden fallar o permanecer sin candidatos antes del guard.

**Conclusión revisada:** caracteriza de manera bastante completa **estos campos específicos** del Compose declarado. No constituye «100 % de L0», no satisface PF-01…PF-06 en todas sus dimensiones, no garantiza seguridad de ejecución y no es un resultado C. `L0 OBSERVACIONAL PARCIAL`; `L1 NO EJECUTADO`.

## 9. Evaluación de la propuesta recibida de «Audit Sandbox» — NO APROBADA

| Propuesta externa | Evaluación técnica y epistemológica | Precondición verificable antes de decidir |
|---|---|---|
| Overlay `docker-compose.audit.yml` | **Candidato razonable de instrumentación**, no una arquitectura aprobada. Compose fusiona volúmenes por destino y agrega/retiene otros ajustes; un override de `tests/corpus:ro` no vuelve `./:/app` inmutable ni elimina automáticamente puertos fake/proxy. | Renderizar configuración combinada saneada y verificar mounts completos de todos los servicios, `read_only`/submounts, puertos, redes y servicios residuales. Para sustituir listas enteras, estudiar `!override`/`!reset` según la versión Compose disponible, sin ejecutarlos todavía. |
| Red `internal: true` | **Defensa en profundidad**, no basta invocar el flag como prueba universal de firewall. Si existe otro enlace de red o acceso mediante puertos publicados, se rompe la premisa. Build/pull y runtime tienen necesidades de red diferentes. | Demostrar que cada proceso ensayado tiene exclusivamente la red prevista, que ningún contenedor ofrece un puente de salida, que los puertos administrativos no quedan publicados y que la denegación de egress se observa en prueba negativa *controlada*. |
| `GROQ_API_KEY=dummy` | Satisface condicionalmente el guard en `run_pipeline`; **no redirige por sí solo la API ni garantiza que se invoque el fake**. Un secreto real jamás se introduce en el expediente. | Endpoint exacto resuelto por el SDK, opciones de configuración, credenciales dummy y ausencia de salida externa; prueba del adapter en sandbox autorizada antes de L1. |
| `fake_groq` OpenAI-compatible | **Alternativa viable por estudiar**, no implementación obligatoria decidida. Debe hablar el protocolo concreto de Groq `chat.completions` y devolver `choices/message/usage` coherentes con `OpenAICompatibleDialect` y el `expected_output_key` de `PromptRenderer`. Un «Caesar shift» arbitrario no garantiza cumplir validación y preservación. | Test de contrato con respuesta golden fija, payload correspondiente a request real, headers de correlación, control de reintentos, registro de solicitudes y reproducibilidad; sin traducciones externas. |
| Conectar SDK Groq al fake sin cambiar `GroqProvider` | **Nueva vía potencial:** la documentación oficial de `groq-python` permite `GROQ_BASE_URL` como variable de entorno del cliente, además de `base_url=` en el constructor. El adaptador del repo crea `AsyncGroq(api_key=…, max_retries=…)` sin `base_url` explícita. Esto puede hacer posible un override *de configuración*, no un cambio de lógica productiva. | Confirmar la **versión instalada/lock del SDK**, que esa versión soporta `GROQ_BASE_URL` y la ruta `/openai/v1`; demostrar la URL efectivamente elegida y el protocolo de respuesta en una prueba negativa sin red pública. **No marcar SATISFECHO solo por documentación de una versión externa.** |
| Reutilizar corpus sellado | La integridad 21/21 está acreditada frente al manifiesto; **no** se autoriza ensayar desde la carpeta canónica ni tocar ground truths. | PDF específico aprobado y su copia con SHA-256; input temporal y rutas de lectura del parser auditadas; prohibición de escribir sobre originales y oráculos. |

**Punto de control importante de Compose:** las reglas oficiales de merge usan el destino dentro del contenedor como clave de unicidad de montajes. Para `ports` hay reglas de secuencia y no desaparecen por omitirlos del overlay. Un diseño «solo anexo un YAML» exige comprobar el modelo resultante, no inferirlo de la intención del autor. Documentación: https://docs.docker.com/reference/compose-file/merge/ ; https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/ . SDK Groq: https://github.com/groq/groq-python .

### Reglas de separación

- **Sujeto A — baseline AS-IS:** conservar fuente, YAML, defaults y disfunciones acreditadas; no ejecutarlo contra volúmenes host ni proveedor real sin autorización.
- **Sujeto B — variante instrumentada de observación:** podría usar endpoint Groq redirigido, clave dummy, red restringida, rootfs/código inmutable y volúmenes explícitos únicos. Esta variante recibe **otro fingerprint** y no reemplaza el resultado del sujeto A.
- **Sujeto C — remediación o arquitectura TO-BE:** corrección funcional, elección de ruta, sustitución estable de adaptadores, etc., fuera de la caracterización previa a decisiones.

No decidir que el Board *obligatoriamente* deba elegir entre `A/B/C` de implementación: el Charter D-1…D-7 sigue `DRAFT`; el owner/autoridad resuelve autorización de experimento y el Board los cambios de alcance arquitectónico según documentos rectores.

## 10. Secuencia de decisión y pruebas de aceptación de la instrumentación (propuesta)

**Etapa 0 — Diseño exclusivamente documental (AHORA):** aprobar únicamente la preparación de un diseño de configuración de auditoría en borrador, no desplegarlo. Incluye grafo de trust boundaries (host, build, runtime), matriz de mounts destino/origen/opciones por servicio, grafos de red, variables *solo nombres* salvo flags inocuos, adaptador y contrato de salida, política de captura/saneamiento y plan de limpieza. El diseño rechaza alternativas que monten el repo original en escritura o permitan inferencias pagadas.

**Etapa 1 — Fijación de sujeto y autoridad:** seleccionar por autoridad competente un PDF candidato del corpus con SHA verificable, variante/código/Compose, autorización de L0 operacional (si aplica), y aprobación aplicable del preregistro antes de L1. Mantener `Atlas IN_PROGRESS`, `Charter DRAFT` hasta acto formal.

**Etapa 2 — Prueba del arnés separada de L1:** *después* de autorización, construir o inspeccionar el entorno exclusivamente en workspace descartable; comprobar `tectonic --version` dentro de imagen si se pudo construir, resoluciones de URI del SDK Groq, contrato `chat.completions` contra fixture determinista; prueba negativa de egress y escritura solamente en sandbox; verificar fingerprints, parámetros efectivos y cero llaves reales. **No alimentar un PDF canónico en esta etapa.** Registrar su resultado como `HARNESS_VERIFICATION`, no `E2E-0 A/B/C`.

**Etapa 3 — Dictamen PF por variante:** solo declarar `ELIGIBLE` si PF-07/08/09 y las demás precondiciones requeridas están acreditadas para **esa configuración**. Si fallan, `NO ELEGIBLE — PRECONDICIÓN` y sin corrida L1; conservar traza. No implementar parches para enmascarar una primera ruptura.

**Etapa 4 — L1 autorizado:** ejecutar una corrida por cada ruta documental elegible, captura de `CP-00…CP-12`, hashes/cadena de custodia, `execution_outcome` exclusivamente A/B/C con justificación. Si la instrumentación modifica el sujeto, consignar diferencia y no presentarla como baseline intacto. Los testigos L2 son independientes y el proveedor real L3 sigue diferido.

### Gate de revisión documental del diseño (NO nuevo gate normativo)

Antes de aprobar el **diseño** del arnés, exigir evidencia revisable de: (a) merge real y seguro de Compose; (b) protección del árbol original y corpus; (c) volúmenes DB/cache/output aislados; (d) puertos/residuales eliminados o limitados; (e) SDK Groq configurable y fake con dialecto compatible; (f) bloqueo de red verificado antes de cualquier inferencia; (g) compatibilidad de build/depósitos en entorno elegido; (h) operador, autorización, rollback y expediente. Cada punto puede permanecer `UNKNOWN`; el documento no lo convierte en PASS.

**Resultado de la adenda:** `PF-07 INCOMPATIBLE-STATIC / PF-08 NOT DEMONSTRATED / PF-09 NOT DEMONSTRATED / L0 OBSERVACIONAL PARCIAL / L1 NO EJECUTADO`. **No hay aprobación de un overlay, fake, cambio funcional, commit ni ejecución.**
