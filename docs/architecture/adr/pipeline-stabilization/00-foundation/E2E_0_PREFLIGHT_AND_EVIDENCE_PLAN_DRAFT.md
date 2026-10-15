# E2E-0 — Expediente de preejecución y adquisición de evidencia (DRAFT)

**Proyecto:** `RDsanchez-git/translator_pdf` · rama objetivo `pipeline_stabilization`  
**Documento rector operativo:** `docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md`, §9, versión declarada `0.2.15`  
**Corte de referencia documental publicada:** Atlas v0.2.15 en commit `362fc032ac01b29ff1264b77b15019dce612a197`, blob `d4bf9b79f9e2ea1169c1089519e1a04650fe42ac`  
**HEAD local comunicado por el owner para inspección L0:** `456700e2001cd8a8fef15cb75982f2faceb7bcdf` (`pipeline_stabilization`; la diferencia de historia y el estado del árbol se registran por separado)  
**Corte de adquisición L0:** 2026-10-15; resultados comunicados por el owner y cotejo estático selectivo de archivos versionados en GitHub  
**Prerregistro:** `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` v0.1.0 `DRAFT`, §6.1 (NO aprobado)  
**Método:** `1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 `FROZEN`  
**Estado del expediente:** `DRAFT — L0 OBSERVACIONAL PARCIAL / L0 FORMAL SIN ACTA / L1 E2E-0 NO EJECUTADO`  
**Alcance:** consolidación de verificaciones locales no destructivas reportadas por el owner, contraste de fuentes y preparación de evidencia. No es una nueva norma, un nuevo gate de aceptación, un plan de remediación ni una autorización de ejecución.

**Control de cambios de este auxiliar:** revisión L0 del 2026-10-15: actualiza los PF y la elegibilidad preliminar por ruta, integra el corpus sellado v3.9 de F17-BIS, separa build previsto de build demostrado y formula condicionalmente el desacople Groq/Gemini. No afecta Charter, metodología, Atlas ni código.

**Contexto aportado por el owner:** Groq fue elegido deliberadamente como proveedor de traducción por restricciones de tokens gratuitos de Gemini. En consecuencia, **no** proponer restaurar Gemini en el producto por conveniencia del test; el fake Gemini es un instrumento histórico separado, y cualquier nueva modalidad controlada exige evaluación de equivalencia y autorización.

> **Regla de precedencia:** ante divergencias, aplicar Charter, metodología y contratos `FROZEN` en su ámbito de autoridad; el Atlas §9 organiza la adquisición. Este documento es un instrumento auxiliar subordinado. Las decisiones D-1…D-7, identidad de unidad/HITO, selección del PDF, control del proveedor y autorizaciones siguen pendientes.

## 1. Objetivo y criterio de éxito de esta fase

**Objetivo de la preparación:** producir una ficha de sujeto verificable por ruta, identificar prerequisitos PF-01…PF-12, documentar las autorizaciones pendientes y disponer de una plantilla de acta L1 sin alterar el repositorio ni el corpus. **Éxito de preparación ≠ éxito de E2E-0 ≠ certificación de producto.**

**Salidas previstas:** (a) inventario de versiones, rutas, flags y dependencias; (b) manifiesto de entradas candidatas sin elegir PDF; (c) matriz de compatibilidad entre adapter, proveedor controlado y egress; (d) matriz de aislamiento de archivos/volúmenes; (e) elegibilidad por ruta con fundamento; (f) plantilla de acta L1 y plan de custodia. Ninguna salida implica ejecutar servicios.

## 2. Invariantes de seguridad y cadena de custodia

1. **No ejecutar L1 ni levantar Docker** hasta contar con autorización explícita, PDF preregistrado y provider determinista que se haya demostrado compatible con el adapter realmente invocado. No invocar APIs de proveedor real para “comprobar”.
2. **No ejecutar `docker compose up`, `docker build`, `pytest`, CLI de traducción ni daemons** durante esta primera ronda documental. `docker compose config --services` es inspección declarativa; puede fallar por variables ausentes, lo cual se registra.
3. **No imprimir secretos.** Prohibido compartir `.env`, credenciales, tokens, URLs con parámetros secretos o salida completa de `docker compose config` sin revisión. Las comprobaciones de variables registrarán exclusivamente `PRESENT`/`ABSENT` (nunca valores).
4. **No escribir en DB, inbox, archive, output, corpus u oráculos del owner.** Una ejecución futura usará copias inmutables del input y volúmenes/DB descartables, sin compartir estado con producción.
5. **Separar las identidades:** commit del Atlas publicado, commit de código efectivamente ejecutado, árbol local (incluidas modificaciones no confirmadas), configuración, PDF SHA-256, `RUN-ID` y fecha/hora UTC. No asumir que el commit documental es el baseline funcional del Atlas.
6. **No corregir fallos durante L1.** Si se cambia código, flags, provider o volúmenes, crear un sujeto/variante y expediente diferentes; preservar la observación AS-IS previa.
7. **No colapsar resultados:** `ELIGIBLE / NO ELEGIBLE — PRECONDICIÓN / UNKNOWN` es estado L0; `A/B/C` corresponde solo a L1 ejecutado; `NO EJECUTADO` y `NO ELEGIBLE` implican `execution_outcome: null`.
8. **Snapshots SQLite coherentes:** para DB activas, no copiar el archivo `.db` omitiendo WAL/SHM. Diseñar captura consistente o registrar `UNKNOWN` y limitación. No tomar snapshots en esta fase.
9. **No asignar IDs formales E-/GAP- ni severidad P0–P2** antes de existir unidad/autoridad. `PF`, `CP`, `W`, `RUN-ID` son etiquetas instrumentales locales.
10. **No seleccionar ruta canónica** por ser la que aparece en Compose; R3 no se considera ruta elegible solo por existir código.

## 3. Sujeto, variantes y controles de comparabilidad

| Candidato | Entry point / composición según Atlas §2 | Pregunta de elegibilidad (NO resultado) | Riesgo de interpretación |
|---|---|---|---|
| **R1 — CLI** | `apps/cli/main.py` → `TranslationPipeline` / `AsyncDispatcher`; ensamblado delegado | ¿Existe arranque reproducible, input PDF autorizado, adapter controlado y handoff a PDF verificable? | `PipelineResult(document=None)` no es PDF final ni defecto por sí mismo; falta continuidad material demostrada. |
| **R2 — OCR → Engine → Assembler** | `apps/ocr_router` → queue/FSM/AST → `runtime/engine.py` → `apps/compiler` | ¿Puede aislarse el Compose efectivo y acreditarse proveedor compatible sin tocar el AS-IS? | Compose base fija `IS_BENCHMARK=1`; terminalidad sintética ≠ PDF. Scheduler puede duplicar `ATTACH`; chunk_id ≠ node_id. |
| **R3 — OCR → LLMWorkerDaemon → Assembler** | Worker alternativo `apps/llm_workers/__main__.py`, no seleccionado por Compose base | ¿Existe una variante ejecutable autorizada y un contrato de claim compatible? | Método `claim_next_pending_task` no encontrado en repo instanciado según inspección; no declararlo RETIRE. |

**Regla de muestreo:** Charter §6.1 solicita un ensayo por cada ruta *elegible con entrada documental*, no necesariamente cada script/daemon aislado. Registrar explícitamente los candidatos excluidos y su fundamento. Variantes de benchmark, AST real, proveedor y Compose base+golden tienen fingerprints diferentes; no mezclar resultados.

## 4. Matriz PF-01…PF-12 — estado observacional al 2026-10-15

**Convenciones:** `VERIFICADO-LOCAL` = salida de comandos locales aportada por el owner; `OBSERVED-STATIC` = contenido del repo cotejado por lectura; `PARCIAL` = hay evidencia útil pero falta el criterio completo; `NO ACREDITADO` = no se ha demostrado una precondición; `UNKNOWN` = se desconoce un hecho material. `SATISFECHO` se restringe al **subcriterio acreditado**, sin elevarlo automáticamente a elegibilidad L1. En especial, **presencia de binario Docker ≠ motor operativo; instrucción Dockerfile ≠ imagen construida**.

| PF | Observación, fuente y delimitación | Estado de control |
|---|---|---|
| **PF-01 Código/Atlas** | Rama `pipeline_stabilization`, HEAD local `456700e2…`, Atlas `v0.2.15`; `git status --short` registra Atlas modificado y este documento nuevo no trackeado. `git diff --check` no mostró errores. SHA de código y estado se volverán a fijar antes de correr. | `PARCIAL — IDENTIFICADO, WORKTREE DIRTY` |
| **PF-02 Corpus** | Manifiesto `tests/corpus/canonical/manifest.json` `v3.9`, `manifest_hash=727782fe…`; **21 de 21 PDFs presentes y con SHA-256 local igual al campo `documents[].sha256`**. No se ha recalculado la semántica de `manifest_hash` ni verificado oráculos aquí; PDF E2E-0 no seleccionado. | `SATISFECHO — INTEGRIDAD DE PDFs VS MANIFEST`; designación `PENDING` |
| **PF-03 Herramientas** | Python 3.11.9, Docker CLI 28.5.1, Compose v2.40.3, Pyright 1.1.411, pytest 9.0.3. Tectonic no encontrado en PATH Windows. `docker images` produjo error de conexión a `dockerDesktopLinuxEngine`; no prueba engine ni imágenes. | `PARCIAL — DOCKER ENGINE NO DISPONIBLE EN ESA SESIÓN` |
| **PF-04 Compose base** | `docker compose -f docker-compose.yml config --services` enumeró 8 servicios; código Compose declara `llm_worker → runtime/engine.py`, `IS_BENCHMARK=1` y recursos persistentes. No se han iniciado contenedores ni cotejado interpolación segura de configuración efectiva. | `PARCIAL — TOPOLOGÍA DECLARADA` |
| **PF-05 Golden** | `base + golden` enumera los mismos 8 servicios; overlay cambia `IS_BENCHMARK=0` y apunta `GEMINI_API_URL` a endpoint público, sin seleccionar Groq ni acreditar supresión de fake/chaos. No confundir servicio listado con equivalencia de despliegue. | `PARCIAL — OVERLAY ESTÁTICO` |
| **PF-06 Build/Tectonic** | `Dockerfile` declara descarga de Tectonic `0.15.0`, `COPY requirements.txt` y `pip install`. **No se construyó ni inspeccionó una imagen**; no se confirmó `tectonic --version` en contenedor, dependencias ni digest de binario. | `PARCIAL — INTENCIÓN DE BUILD; INSTALACIÓN NO DEMOSTRADA` |
| **PF-07 Proveedor** | `engine.py`/CLI/daemon leen `GROQ_API_KEY`; sus invocaciones inspeccionadas a `build_provider_stack()` omiten `provider_type` y el default de factory es `groq`. Compose base/overlay declaran Gemini, no pasan explícitamente `GROQ_API_KEY` al contenedor `llm_worker`. La sesión PowerShell no listó variable host `GROQ_API_KEY`. **Si el proceso no recibe la clave por otra vía, `engine.py` aborta cuando alcanza ese guard**; si la recibe, construye Groq, no el fake Gemini. No se observó arranque. | `INCOMPATIBLE-STATIC — CONFIGURACIÓN DECLARADA VS SELECCIÓN DE ADAPTER`; efecto en run `NO OBSERVADO` |
| **PF-08 Fake/egress** | `fake_gemini.py` expone API Gemini, semilla configurable y fallos; `toxiproxy.json` dirige `gemini_proxy` a `fake-gemini:8000`. `GroqProvider` usa `AsyncGroq` sin endpoint alternativo en la factory inspeccionada; el proxy Gemini **no intercepta Groq ni actúa como firewall**. Salida de red denegada no probada. | `NO ACREDITADO — CONTROL DETERMINISTA COMPATIBLE / EGRESS` |
| **PF-09 Aislamiento** | Compose monta `./:/app` y el volumen persistente `sqlite_data:/app/infra/db`; los puertos del fake/proxy están publicados. No hay entorno descartable validado ni protección técnica verificada para corpus, GT y DB existentes. | `NO ACREDITADO — AISLAMIENTO DE ENSAYO` |
| **PF-10 Benchmark** | `IS_BENCHMARK=1` en base y `0` en overlay; `engine.py` también utiliza rama sintética para `document_id.startswith('doc_')`. Una ejecución benchmark completada no acredita PDF. No se ejecutó ninguna variante. | `OBSERVED-STATIC — FLAGS / BRANCHES IDENTIFICADOS` |
| **PF-11 CI/typing** | Versiones de Pyright/pytest conocidas; disponibilidad de ejecutables y configuración `pyproject.toml` reconocida. No se midió gate real ni corrida Pyright/pytest actual; warning de actualización no es anomalía funcional. | `PARCIAL — HERRAMIENTAS IDENTIFICADAS` |
| **PF-12 Custodia** | Existe diseño de acta, hashes, aislamiento y snapshots. No se aprobó ni ensayó reversibilidad; no hay operador, PDF, autorización ni `RUN-ID` de L1. | `DRAFT — NO VALIDADO OPERACIONALMENTE` |

**Estado global:** `L0 OBSERVACIONAL PARCIAL`; `L1 NO EJECUTADO`; `execution_outcome = null`; `PRODUCT READINESS NOT DEMONSTRATED`. No trasladar `PF-07` a severidad P0/P1/P2, incidente en producción o resultado `C` de E2E-0. El rótulo `INCOMPATIBLE-STATIC` es una clasificación local de relación **código/configuración**, no una decisión de arquitectura.

## 5. Puertas de autorización y dependencias (sin inventar decisiones)

| Asunto | Requerido para | Estado al redactar | Quién debe resolver |
|---|---|---|---|
| Charter §6.1 y marco de autoridad | Preregistro vinculante de L1 | `DRAFT / PENDING` | Owner/Board competente |
| Unidad/HITO, identidad formal, nomenclatura (DOC-01) | Folios y cierre forense | `DECISION REQUIRED` | Board/autoridad competente |
| PDF exacto y SHA-256 del manifest | Ensayo comparable | `PENDING` | Board/owner según Charter |
| Rutas y variantes que serán evaluadas | Matriz de elegibilidad | `UNKNOWN` hasta L0 | Owner/Board según autoridad |
| Provider determinista compatible con Groq (elección funcional actual del owner) o variante explícitamente autorizada | L1 sin egress real | `NOT DEMONSTRATED`; fake actual es Gemini y stack invocado elige Groq | Owner técnico + autoridad de ensayo; no asumir que toda instrumentación exige D-1…D-7 |
| Denegación verificable de egress real y credenciales protegidas | L1 seguro | `NOT VERIFIED`; Toxiproxy no es cortafuegos general | Owner técnico |
| Entorno/DB/volúmenes aislados y reversibles | L1 no contaminante | `NOT VERIFIED`; Compose monta repo y estado persistente | Owner técnico |
| E2E con proveedor real y presupuesto | L3, no L1 | `DEFERRED / NOT AUTHORIZED` | Owner/Board |
| Decisiones D-1…D-7 | Convergencia, gobernanza | `PENDING` | Board/owner |

**No transformar la tabla en nuevas exigencias normativas:** detalla cómo demostrar los prerrequisitos ya presentes en el Charter y Atlas. Si alguna aprobación de la unidad puede ser posterior a L0, documentar su dependencia sin asumir autoridad. **La elección deliberada de Groq es un hecho de intención del owner; no es una aprobación de proveedor real para L1.** La autoridad deberá distinguir (i) caracterización AS-IS sin arreglar el sujeto, (ii) instrumentación de ensayo explícitamente autorizada y separada, y (iii) cambios funcionales posteriores que pertenezcan a remediación/TO-BE. **No imponer una opción A/B/C de implementación como requisito normativo nuevo.**

## 6. Comandos de la primera ronda L0 — registro de referencia (no hace falta repetir)

Bloque de referencia usado para orientar la **primera ronda ya reportada** por el owner. Solo repetir de forma deliberada si es necesario actualizar el corte; ejecutar **desde la raíz del repositorio** en PowerShell. Los comandos no hacen `git add`, `git commit`, `git push`, build, arranque de servicios ni escrituras de aplicación. **Revisar manualmente la salida antes de compartirla**, especialmente si los paths locales contienen datos personales.

```powershell
# A. Identidad y limpieza del sujeto documental
$atlas = 'docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md'
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check
git log -1 --format='%H%n%s%n%cI'
Select-String -Path $atlas -Pattern '^\*\*Versión:\*\*', '^## 0\.4 Progreso', '^\*\*Integración documental:\*\*'

# B. Herramientas disponibles (NO instala nada)
python --version
Get-Command python, docker, tectonic, pyright, pytest -ErrorAction SilentlyContinue | Select-Object Name, Source
if (Get-Command docker -ErrorAction SilentlyContinue) { docker --version; docker compose version }

# C. Descubrimiento declarativo del Compose (NO crea contenedores)
Get-ChildItem -File -Name 'docker-compose*.yml', 'docker-compose*.yaml', 'compose*.yml', 'compose*.yaml' -ErrorAction SilentlyContinue
if ((Get-Command docker -ErrorAction SilentlyContinue) -and (Test-Path 'docker-compose.yml')) {
  docker compose -f docker-compose.yml config --services
}

# D. Inventario de PDFs y manifiestos (NO elegir PDF ni abrir su contenido)
Get-ChildItem 'tests/corpus/canonical/pdf' -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Extension -eq '.pdf' -or $_.Name -match 'manifest' } |
  Select-Object Name, Length
```

**No pegar** la salida de `docker compose config` sin `--services`; puede interpolar secretos. No pegar contenido de `.env`, tokens, variables de entorno completas, ni `pip freeze` si incluyera rutas privadas. Si un comando falla, conservar el mensaje y continuar; un fallo de herramienta no demuestra fallo del pipeline.

**Rondas posteriores ya recibidas:** inventario y comparación de 21/21 PDFs, servicios de Compose, Dockerfile, factory, adaptadores y fake Gemini. Conservar las salidas aportadas como evidencia observacional no formalizada; no volver a ejecutarlas por rutina. El siguiente control pendiente es diseñar aislamiento/egress y formalizar el sujeto autorizado, no repetir hashes ni iniciar el pipeline.

## 7. Plantilla de ficha de elegibilidad por ruta

```yaml
route_id: R1|R2|R3
route_variant_id: PENDING
subject_code_sha: 456700e2001cd8a8fef15cb75982f2faceb7bcdf  # HEAD local reportado; no SHA ejecutado
atlas_version: '0.2.15'
atlas_blob_sha: d4bf9b79f9e2ea1169c1089519e1a04650fe42ac
charter_version: '0.1.0 DRAFT'
operator: PENDING
utc_recorded_at: PENDING
entrypoint: UNKNOWN
input_pdf: PENDING_BOARD_OWNER
input_sha256: PENDING_BOARD_OWNER
provider_adapter: UNKNOWN
deterministic_provider_compatibility: UNKNOWN
real_provider_egress_blocked: UNKNOWN
compose_files_order: UNKNOWN
is_benchmark: UNKNOWN
isolation_plan: UNKNOWN
PF_01_to_12: SEE_SECTION_4_L0_PARTIAL
L0_eligibility: UNKNOWN  # ELIGIBLE | NO ELEGIBLE — PRECONDICIÓN | UNKNOWN
eligibility_rationale: PENDING
L1_authorization: PENDING
L1_execution_status: NO_EJECUTADO
execution_outcome: null
```

Los valores son marcadores de plantilla, **no observaciones reales**. El estado `L0_eligibility` se decide por variante y configuración, no globalmente para todo el repositorio.

## 8. Acta L1 futura — estructura mínima, no ejecución

```yaml
run_id: NOT_ASSIGNED
route_id: UNKNOWN
variant_fingerprint: UNKNOWN
operator: PENDING
start_utc: null
end_utc: null
charter_authorization_reference: PENDING
code_commit_sha: UNKNOWN
working_tree_delta: UNKNOWN
atlas_version: '0.2.15'
input_pdf_name: PENDING
input_pdf_sha256: PENDING
adapter: UNKNOWN
provider_control_mechanism: UNKNOWN
egress_policy: UNKNOWN
build_runtime: UNKNOWN
compose_files_and_order: UNKNOWN
flags_and_resource_bounds: UNKNOWN
isolated_data_paths: UNKNOWN
pre_run_manifest_sha256: UNKNOWN
command_invoked: NONE
exit_code: null
PF_01_to_12: SEE_SECTION_4_L0_PARTIAL
checkpoints:
  CP_00: NOT_OBSERVED
  CP_01: NOT_OBSERVED
  CP_02: NOT_OBSERVED
  CP_03: NOT_OBSERVED
  CP_04: NOT_OBSERVED
  CP_05: NOT_OBSERVED
  CP_06: NOT_OBSERVED
  CP_07: NOT_OBSERVED
  CP_08: NOT_OBSERVED
  CP_09: NOT_OBSERVED
  CP_10: NOT_OBSERVED
  CP_11: NOT_OBSERVED
  CP_12: NOT_OBSERVED
first_observed_break: UNKNOWN
execution_status: NO_EJECUTADO
execution_outcome: null  # SOLO A | B | C tras L1 ejecutado y acreditado
contract_verdict: NO_EVALUABLE
scientific_verdict: NO_EVALUABLE
logs_hashes: NONE
sqlite_snapshot_hashes: NONE
pdf_output_sha256: null
post_run_manifest_sha256: UNKNOWN
deviations: NONE_RECORDED
reviewer: PENDING
review_utc: null
```

**Semántica de CP:** en una corrida efectivamente iniciada, usar `REACHED`, `FAILED_OBSERVED`, `NOT_REACHED` o `UNKNOWN`; antes de ejecutar, `NOT_OBSERVED (NO EJECUTADO)`. La primera ruptura debe respaldarse por trazas, sin inferir orden cronológico global entre procesos independientes. Un PDF final atribuible puede sustentar A, pero no certifica automáticamente contratos FROZEN o integridad científica. Los resultados B/C deben conservarse íntegramente.

## 9. Paquete de evidencia y control de integridad (diseño para cuando L1 sea autorizado)

**Ubicación:** carpeta externa al corpus y al árbol versionado; ruta acordada con el owner. Propuesta de estructura lógica, no crear aún:

```text
RUN-ID/
  00_authorization_and_subject.md
  01_preflight_PF01_PF12.md
  02_input_manifest.json
  03_environment_fingerprint.md
  04_commands_and_timestamps.log
  05_logs_redacted/
  06_sqlite_consistent_snapshots/
  07_output_artifacts/
  08_checkpoint_matrix.md
  09_outcome_and_limitations.md
  10_hash_manifest.sha256
  11_review.md
```

**Control de calidad del paquete:** verificar nombres, hash SHA-256 de bytes, integridad de snapshots, relación `RUN-ID`→config→PDF→salida y distinción de observado/no observado. No usar el éxito de un validador de formato como aprobación funcional o contractual. Minimizar datos sensibles y preservar, cuando sea necesario, copia original bajo acceso restringido y copia saneada para revisión.

## 10. Matriz de riesgos e incertidumbres priorizados antes de L1

| Cuestión | Lo verificado hasta ahora | Qué impide afirmar | Próxima evidencia autorizable |
|---|---|---|---|
| **PF-07 Groq vs Gemini** | Factory admite ambos, default Groq; las entry points usan `GROQ_API_KEY` y omiten `provider_type`; Compose configura fake Gemini sin clave Groq explícita. | Que *todo* Compose falla por este motivo o que `engine.py` llega al guard antes de cualquier otra ruptura; tampoco sabemos las variables reales del proceso. | Fingerprint seguro de configuración **sin valores secretos** y evaluación de mecanismo compatible con Groq; no usar clave real en L1. |
| **PF-08 Fake, determinismo y salida** | Toxiproxy upstream es `fake-gemini:8000`; fake con RNG sin semilla obligatoria y salida sintética; `GroqProvider` usa SDK Groq. | Que la cadena se intercambia por configuración o bloquea tráfico de otras APIs; que la respuesta feliz satisface el dialecto esperado. | Verificación de protocolo, respuesta/campo esperado y restricción efectiva de salida, diseñada sin modificar AS-IS ejecutado. |
| **PF-06 Tectonic/build** | Dockerfile instala condicionalmente binario al construirse; Docker Desktop Linux Engine no accesible en comprobación local. | Imagen construida, `tectonic --version`, reproducibilidad efectiva. | Tras autorización de L0 operacional, build/inspección aislada y registro de artefacto, sin ejecutar L1. |
| **PF-09 Persistencia y corpus** | `./:/app`, volumen SQLite, puertos publicados y corpus v3.9 sellado. | Que el corpus/GT o DB estén protegidos contra escritura o que el entorno sea descartable. | Diseño de mounts de solo lectura + copia de trabajo y proyecto/volúmenes únicos, revisado antes de ejecutarse. |
| **PF-10 Benchmark vs producto** | Base `IS_BENCHMARK=1`, golden `0`; rama sintética por prefijo `doc_`; F17-BIS certifica extracción/regresión, no PDF→PDF. | Terminalidad sintética como PDF real o resultados históricos como E2E-0. | Sujetos separados y huellas de configuración, corpus/ground truth sin mutaciones. |
| **R2 scheduler e identidad** | Doble `ATTACH fsm_db` condicional y `chunk_id` vs `node_id` documentados estáticamente en Atlas. | Orden de primera excepción observada en ejecución. | L1 autorizada o testigo L2 independiente, con traza y conservación de precondiciones. |
| **R1 handoff/R3 API** | CLI no acredita AST/proyección física; R3 invoca `claim_next_pending_task` no encontrado en repositorio instanciado. | Qué rutas completas funcionarían y cuál debe ser canónica. | Matriz por ruta, L1 por ruta elegible y decisiones posteriores, sin elegirlas aquí. |

**Tratamiento de propuestas recibidas de terceros:** las opciones de adaptar entry points para Gemini, crear un fake Groq, o usar proveedor real **no son conclusiones ni acciones aprobadas**. Cambiar `os.getenv('GROQ_API_KEY')` a `'GEMINI_API_KEY'` **no** seleccionaría por sí mismo Gemini porque la factory conserva `provider_type='groq'`. Agregar una clave de Groq permitiría superar un guard condicional, pero **no** demostraría control determinista; introducir una credencial real/egress viola las precondiciones de L1 del Charter tal como está planteado. Cualquier variante instrumentada debe tener autorización, fingerprint y reporte distinto del AS-IS, sin reescribir los criterios preregistrados.

## 11. Criterios de revisión de este documento auxiliar

- [ ] Se confirmó que el Atlas publicado/ejecutado corresponde a la versión y blob registrados.
- [x] Se recibieron varias rondas de inspección local, sin compartir valores de secretos.
- [x] Se registró **estado parcial** PF-01…PF-12 con fuente y limitación; **no** significa que los 12 PF estén satisfechos.
- [x] Se inventariaron las rutas principales y se distinguieron sus impedimentos estáticos; la elegibilidad definitiva sigue pendiente.
- [ ] Se definió mecanismo verificable de proveedor controlado y denegación de egress.
- [ ] Se documentaron rutas de datos aisladas y estrategia de snapshots coherentes.
- [ ] Se identificó el PDF designado y su SHA-256, cuando el Board/owner lo apruebe.
- [ ] Se registró la autorización que habilita cada acción futura.
- [ ] Se acordó el formato de expediente y el operador/revisor.
- [ ] Se mantuvo `L1 NO EJECUTADO` y `execution_outcome: null` hasta una corrida real.

**Dictamen actual:** `DRAFT / L0 OBSERVACIONAL PARCIAL / PF-07 INCOMPATIBLE-STATIC (SUJETO COMPOSE DECLARADO) / PF-08 Y PF-09 NO ACREDITADOS / L1 NO EJECUTADO / OUTCOME null`. No modifica Charter, Atlas, código ni estado `IN_PROGRESS`.

## 12. Referencias y procedencia

- [Atlas v0.2.15, §9 y §§2, 8, 12 — commit 362fc032](https://github.com/RDsanchez-git/translator_pdf/blob/362fc032ac01b29ff1264b77b15019dce612a197/docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md)
- [Charter v0.1.0 DRAFT, §6.1–6.5 — mismo commit](https://github.com/RDsanchez-git/translator_pdf/blob/362fc032ac01b29ff1264b77b15019dce612a197/docs/architecture/adr/pipeline-stabilization/00-foundation/PIPELINE_STABILIZATION_AUDIT_CHARTER.md)
- [Metodología forense v1.2.0 FROZEN — mismo commit](https://github.com/RDsanchez-git/translator_pdf/blob/362fc032ac01b29ff1264b77b15019dce612a197/docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md)

**Nota de consistencia documental:** en el commit de Atlas `362fc032…` el encabezado §0.4 aún decía `v0.2.14`; el owner mostró en su árbol local la corrección `v0.2.15 — corte documental 2026-10-15`. La modificación **no se confunde** con la versión publicada hasta contar con su commit. La fecha del corte puede conservarse.


### 12.1 Fuentes primarias adicionales — repositorio inspeccionado, HEAD local comunicado `456700e2…`

- [Factory Groq/Gemini y default](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/apps/bootstrap/provider_stack_factory.py): acepta `provider_type=groq|gemini`, default `groq`; soporte disponible no equivale a selección por entry point.
- [Engine y guard Groq](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/runtime/engine.py): lectura de `GROQ_API_KEY`, stack sin `provider_type`, rama benchmark/sintética y scheduler.
- [Adaptadores de inferencia](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/apps/llm_workers/adapters.py): `AsyncGroq` y `GeminiProvider` con semánticas propias.
- [Compose base](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/docker-compose.yml) y [overlay golden](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/docker-compose.golden.yml): flags, fake, montajes, endpoints, servicios.
- [Dockerfile](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/Dockerfile): instrucción de instalación de Tectonic v0.15.0; sin evidencia de imagen funcional.
- [Fake Gemini](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/apps/daemons/fake_gemini.py) y [Toxiproxy](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/toxiproxy.json): contrato de mock y proxy, no egress guard global.
- [Manifest canónico v3.9](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/tests/corpus/canonical/manifest.json): `21` entradas; cotejo SHA-256 local reportado 21/21.
- [Metodología de benchmark F17-BIS](https://github.com/RDsanchez-git/translator_pdf/blob/456700e2001cd8a8fef15cb75982f2faceb7bcdf/docs/architecture/adr/phase-17-bis/reviews/FASE_5_BENCHMARK_METHODOLOGY.md) v1.2.0, y registros `FASE_5_WAVE_*` del mismo directorio. **No trasladar identidades de corpus previos o veredictos de regresión a E2E-0.**
- `tests/integration/test_real_e2e.py` contiene `patch.object(self.pipeline, 'execute', ...)` con `MagicMock`; el nombre del test no constituye prueba de PDF→PDF.

**Alcance del cotejo:** lectura estática de fuentes de GitHub y transcripciones de inspección PowerShell del owner; **no** acceso al runtime Windows, imagen Docker, variables de proceso de un contenedor, archivos `.env`, credenciales ni logs E2E. Los resultados observacionales locales no están formalizados aún como paquete L0 con RUN-ID y custodia completa.

## 13. Matriz de elegibilidad preliminar por sujeto — no confundir con A/B/C

| Sujeto | Condición observada | Estado de preflight | Qué permitiría revisarlo |
|---|---|---|---|
| **R1 CLI, Groq seleccionado** | Requiere `GROQ_API_KEY` y proveedor controlado aún no disponible; handoff material a PDF no acreditado. | `UNKNOWN / NO ELEGIBLE PARA L1 BAJO LAS PRECONDICIONES HOY ACREDITADAS` | Autoridad de ensayo, PDF designado, provider controlado compatible, aislamiento y configuración de ruta. |
| **R2 Compose base OCR→Engine→Assembler** | Selecciona `IS_BENCHMARK=1`; Engine espera Groq y Compose publica variables Gemini; fake Gemini no es interceptor Groq. Persistencia compartida sin aislamiento demostrado. | `NO ELEGIBLE — PRECONDICIONES PF-07/08/09; OBSERVED-STATIC` | Cerrar elegibilidad, separar configuración AS-IS de variante controlada autorizada y conservar baseline original. |
| **R2 base + golden** | `IS_BENCHMARK=0`, pero la rama sintética también puede activarse por `doc_`; `GEMINI_API_URL` externa, selección Groq en Engine no cambia. | `NO ELEGIBLE — PRECONDICIONES PF-07/08/09; OBSERVED-STATIC` | Evaluación estática y control efectivo de proveedor/egress, aislamiento y sujeto elegible. |
| **R3 daemon alternativo** | No está seleccionado en Compose base; API `claim_next_pending_task` ausente del repo instanciado, además de proveedor no controlado. | `UNKNOWN / STATIC API BLOCKER; L1 NO HABILITADO` | Aclarar ruta/elegibilidad por autoridad y contrato de acceso a tareas sin remediación tácita. |

**Autoridad y alcance de la palabra “bloqueado”:** significa que **no existe actualmente un paquete de elegibilidad L1 acreditado** para la variante descrita. No demuestra que todos los servicios Compose fallen, que ninguna instalación posible arranque, ni que todos los defectos funcionales sean conocidos. Tampoco declara una severidad formal `CRITICAL/P0`: esa clasificación exige la metodología y autoridad correspondientes.

### 13.1 Prueba lógica de la incompatibilidad PF-07 — observación vs inferencia

1. **OBSERVED-STATIC:** el servicio `llm_worker` de Compose base ejecuta `runtime/engine.py`.
2. **OBSERVED-STATIC:** en el archivo Compose auditado el servicio configura `GEMINI_API_KEY`, `GEMINI_API_URL` y `IS_BENCHMARK`, pero no declara transmisión explícita de `GROQ_API_KEY`.
3. **OBSERVED-STATIC:** Engine lee `GROQ_API_KEY` y, **si no está presente en el proceso cuando ejecuta ese bloque**, lanza `RuntimeError`. La fábrica utiliza Groq por omisión.
4. **CONDICIONAL, NO OBSERVADO DINÁMICAMENTE:** bajo un entorno efectivo sin la clave Groq, ese guard impide construir el proveedor; **no** atribuir sin traza el primer fallo cronológico, porque el scheduler u otros prerrequisitos pueden fallar antes.
5. **SI SE SUPERA ESE GUARD:** la opción por defecto sigue siendo Groq, que no usa el proxy del fake Gemini. No introducir una credencial real para comprobarlo durante L1.

**Consecuencia precisa:** incompatibilidad estática de la instrumentación Compose/Gemini respecto al stack Groq invocado y ausencia de control determinista acreditado. La ausencia de una declaración YAML no es prueba universal de ausencia de variable en *todo* entorno posible; la salida del proceso y sus variables reales no se inspeccionaron.

## 14. Próximo acto legítimo y control de publicación

1. **Revisión del expediente por el owner:** verificar los hechos, contexto de elección deliberada de Groq y estados PF, sin forzar opciones TO-BE.
2. **Publicación documental opcional:** mantener nombre `E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md`, estado `DRAFT`, y commitear **solo este auxiliar** cuando se acepte. El Atlas con corrección local §0.4 puede ir en commit distinto; no incluirlo accidentalmente.
3. **Continuar L0 observacional:** elaborar controles comprobables de egress/volúmenes y equivalencia del fake, sin exponer claves ni modificar corpus/GT/DB.
4. **Separar decisiones de elegibilidad y remediación:** elevar al owner/Board las autorizaciones de L1 y las variantes de prueba; la selección de ruta canónica y los cambios de implementación pertenecen al cauce posterior, no al documento auxiliar.
5. **L1 sigue prohibido por falta de elegibilidad/autorización:** no ejecutar Docker Compose, traducciones, proveedor real o suites que escriban DB como sustituto de E2E-0.

**Cierre de esta revisión:** `PREFLIGHT DOCUMENTAL CONSOLIDADO — DRAFT; L0 PARTIAL; L1 NOT EXECUTED; A/B/C NOT ASSIGNED`. Este expediente **no declara** el Atlas `FROZEN` ni propone cambiar Groq por Gemini.
