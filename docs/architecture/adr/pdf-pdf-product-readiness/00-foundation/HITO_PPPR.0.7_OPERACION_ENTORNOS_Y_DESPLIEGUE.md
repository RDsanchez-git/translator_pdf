# HITO_PPPR.0.7_OPERACION_ENTORNOS_Y_DESPLIEGUE.md

**Estado:** IN_PROGRESS v1.0.1  
**Fecha de emisión:** 2026-11-20  
**Congelamiento:** N/A  
**Tipo de artefacto:** Forensic Flow Audit — operación y entornos de la ruta única PDF→PDF  
**Iniciativa:** PPPR, Fase 0 documental transversal (no fase numerada del roadmap)  
**Baseline productivo inspeccionado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@c5841f79b26b3cd1e734817f1a11cc298507f43b` (HITOs 0.1–0.6 FROZEN)  
**Metodología:** `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN (superior), `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN (§4.7/§4.8, §7.1, §8.1–8.2, §9.2, §11.1); `docs/architecture/PROJECT_SCOPE.md`, `docs/architecture/ENGINEERING_PRINCIPLES.md`.  
**Ruta seleccionada:** D-1/D-2; Atlas `docs/architecture/adr/pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` v1.0.2 como mapa **DESCRIPTIVO AS-IMPLEMENTED** (corte `6818e86`), comprobado con código actual; **no** NADR vinculante.  
**Mandato:** auditar la **composición efectivamente versionada** de CLI, host Windows, Docker/Compose, configuración, secrets, rutas compartidas, estado SQLite, volúmenes y permisos, bootstrap, dependencias/cachés/Tectonic, redes/egress, arranque/recovery y testigos de entorno. Distinguir uso productivo, entorno de laboratorio fake, documentos históricos y host externo NO VERIFICABLE.  
**Naturaleza:** exclusivamente lectura de repositorio y testigos, **NOT_RUN**; no Docker/Windows/PowerShell ejecutado, no secretos inspeccionados, no SQLite del usuario, no egress/LLM, no corpus, ni código productivo modificado.

### Changelog

| Versión | Fecha | Alcance |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-20 | Apertura desde merge #71: censo de tres variantes Compose y root CLI; 26 E-IDs, dos candidatos P1 con causalidad de configuración, 9 hipótesis y límites de host; contraste con runbook C0–C4 y PPPR.0.4/0.5. Sin FROZEN ni pruebas nuevas. |
| 1.0.1-IN_PROGRESS | 2026-11-20 | Segunda pasada: 34 E-IDs todos P2; dos IDs candidatos sin GAP confirmado, nueve hipótesis parcialmente clasificadas, C2 con admisión intra-contenedor comprobada documentalmente, y PPPR.0.4 con proveedor pendiente. DQ/DC se incorporan al cierre de esta pasada. No tests ni FROZEN. |

## 1. RESUMEN EJECUTIVO

**Hecho de composición:** la opción seleccionada en el Atlas es CLI/admisión → OCR Router → `runtime/engine.py` (G3) → `apps/compiler/__main__.py` (G5) → PDF. `docker-compose.yml` es una base heredada que contiene fake/chaos y benchmark; `docker-compose.runtime.yml` sustituye montajes/estado y desactiva componentes de laboratorio por `profiles: [lab]`. `docker-compose.convergence-lab.yml` añade una composición controlada **solo para laboratorio offline con fake**, no un perfil productivo real. `docker-compose.golden.yml` presenta una intención histórica de calidad, pero no demuestra por sí solo que sea el launcher operativo aprobado.

**Primera tensión operacional observada:** un proceso G3 con traducciones a inferir exige `GROQ_API_KEY` en `runtime.engine._create_chunk_processor`, pero la composición `docker-compose.yml` + `docker-compose.runtime.yml` **no** declara ese secreto en el ambiente del servicio `llm_worker`; el host puede poseer una variable o archivo `.env` y Docker Compose **no la transmite automáticamente al contenedor salvo declaración explícita u otra inyección**. El laboratorio sí suministra una credencial *dummy*. **GAP-0.7-01 provisional P1 LOCAL**: arranque declarado sin wiring de credencial requerido para inferencia real, si no hay inyección externa no versionada; no se afirma que se haya intentado un POST real.

**Segunda tensión operacional observada:** la CLI por defecto deposita el PDF en `<repo>/data/inbox` del host; la composición runtime reconfigura OCR para observar `/app/data/inbox` dentro del volumen nombrado `g3_runtime_data` y **no** monta la carpeta de inbox del host. Por tanto, **la invocación CLI desde el checkout host no alcanza automáticamente el OCR de Compose**, salvo uso de una admisión dentro del namespace del contenedor u otra transferencia/configuración host no acreditada. **GAP-0.7-02 provisional P1 LOCAL**, limitado a la combinación *CLI host + stack runtime*; no decir que el laboratorio C2 falló (tuvo inbox compartido) ni que todo uso de CLI está bloqueado.

**Límites prioritarios:** `docker compose up` no fue ejecutado; no se inspeccionaron máquinas Windows ni volúmenes reales, configuraciones expandidas, permisos, certificados, versiones efectivas o secretos. No extrapolar evidencia de laboratorio C0–C4 con fake a egress/hosting comercial. El sweeper de Compose es un **GAP-0.5-03 preexistente**, no se abre uno duplicado aquí.

**Veredicto:** **IN_PROGRESS**. Se requiere completar causalidad de los dos GAPs candidatos, compatibilidad efectiva de Compose, inventario de fuentes de configuración/credenciales/archivos, falsadores y checklist final §8.1–8.2 antes de FROZEN.

## 2. LÍMITE EPISTEMOLÓGICO Y REGLAS DE INSPECCIÓN

- **OBSERVED en SHA:** YAML, Dockerfile, entrypoints, tests/runbook y código de resolución de rutas. Un `environment:` declarado no prueba variable efectiva en contenedor; un `volumes:` nombrado describe acceso previsto, no que host lo comparta físicamente.
- **REQUIRED:** preservar una única ruta admitida, configuración explícita, privacidad de corpus/credenciales, fail-closed y trazabilidad, SRE, sin falso `PASS`; los detalles de proveedor/modelo y de W06 se gobiernan respectivamente en PPPR.0.4/0.5.
- **DECISION existente:** D-1/D-2 y Atlas con el mismo stack; C0–C4 lograron evidencia de laboratorio **con fake** en otro corte, no aprobación de despliegue comercial.
- **HISTÓRICO:** Docker/Compose originales, `docker-compose.golden.yml`, P6/F17-BIS, imágenes y cachés fechadas, reportes C0–C4; no usar NADR PROPOSED como obligación vigente ni reactivar R1/R3.
- **NO VERIFICABLE:** Docker Desktop real, shells externos, variables/launchers host, presencia de `.env`, discos/volúmenes, red/NAT/egress, Tectonic físico, facturas, permisos y corpus. `NOT_RUN` para todos los tests versionados en este HITO.
- **Prohibiciones:** no imprimir variables secretas, ejecutar `docker compose config` que exponga credenciales, iniciar contenedores, descargar imágenes, tocar SQLite, borrar Docker volumes ni modificar el checkout Windows del propietario sin mandato y aislamiento específicos.

## 3. INVENTARIO DEL PERÍMETRO OPERATIVO

| Superficie | Ruta/configuración observada | Estado en primera pasada |
|---|---|---|
| CLI/admisión foreground | `apps/cli/{main,pdf_inbox,pdf_product}.py`, `pyproject.toml` | **AUDITADO** (E-001/002/003) |
| Compose base heredada | `docker-compose.yml` | **AUDITADO** (E-004/005/006) |
| Override del runtime compartido | `docker-compose.runtime.yml` | **AUDITADO** (E-007/008/009) |
| Composición offline convergente | `docker-compose.convergence-lab.yml`, `apps/lab/convergence_compose_preflight.py` | **AUDITADO** (E-010/011/012) |
| Config alternativo Golden | `docker-compose.golden.yml` | **REFERENCIADO**, no launcher seleccionado (E-013) |
| G3/credenciales/modelo/env | `runtime/engine.py`, `apps/bootstrap/provider_stack_factory.py`, `apps/llm_workers/adapters.py` | **AUDITADO focal** (E-014/015); semántica del modelo PPPR.0.4 |
| SQLite estado/creación/ATTACH | `infra/db/{bootstrap,connection,profile_store,document_repository}.py` | **AUDITADO** (E-016/017/018) |
| OCR/directorios y assets G5 | `apps/ocr_router/__main__.py`, `apps/compiler/{__main__,tectonic_runner}.py` | **AUDITADO focal** (E-019/020) |
| Imagen, dependencias y supply chain | `Dockerfile`, `.dockerignore`, `pyproject.toml` | **AUDITADO inicial**, verificación de proveniencia futura (E-021/022) |
| CI/CV, testigos/host | `.github/workflows/{ci,continuous-verification}.yml`, tests C0/B03, handoff `LABORATORIO_Y_REPRODUCCION.md` | **LEÍDOS, NOT_RUN** (E-023/024/025/026) |
| Entorno Windows/Docker físico, variables/secretos externos, discos/certificados | No acceso seguro disponible | **NO VERIFICABLE**; DQ a precisar |
| Reconciler/Sweeper | `apps/daemons/reconciler.py`, `runtime/sweeper.py` | **REFERENCIADO** — GAP-0.5-03, sin duplicar auditoría de estado |

## 4. FUENTES DE EVIDENCIA Y PRECEDENCIA

**Código productivo pinneado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`. Source roots `apps/cli/main.py`, `apps/cli/pdf_inbox.py`, `apps/cli/pdf_product.py`, `apps/ocr_router/__main__.py`, `runtime/{engine,settings,sweeper}.py`, `apps/compiler/{__main__,tectonic_runner}.py`, `infra/db/{bootstrap,connection,profile_store,document_repository}.py`, `apps/bootstrap/provider_stack_factory.py`; Compose/YAML/Build/CI indicados en §3.

**Fuentes de convergencia:** Atlas de ruta única v1.0.2 (DESCRIPTIVO AS-IMPLEMENTED de `6818e86`), `docs/architecture/adr/pipeline-stabilization/handoff/{EVIDENCIA_Y_CIERRE,LABORATORIO_Y_REPRODUCCION}.md` (C0–C4 con fake, comandos históricos, precauciones de Windows/volúmenes). Los tests `tests/unit/{test_convergence_compose_preflight,test_b032_offline_pdf_lab,test_tectonic_runner}.py`, `tests/integration/{test_b03_foreground_pdf_product,test_pdf_pdf_sqlite_contracts}.py` fueron **LEÍDOS, NOT_RUN**.

**Gobernanza vigente:** metodologías FROZEN superior/especializada, `PROJECT_SCOPE`, `ENGINEERING_PRINCIPLES`, D-1/D-2, PPPR.0.1–0.6 FROZEN y ADR/NADR F18 relevantes. No importar requisitos F17-BIS PROPOSED como autoridad.

## 5. MAPA DE COMPOSICIÓN OBSERVADO

```text
Host / PowerShell (NO INSPECCIONADO)
  ├─ translator-pdf / python -m apps.cli.main translate paper.pdf
  │     └─ inbox por defecto: <repo_root_host>/data/inbox/<sha256>.pdf
  │          (admisión SHA, no ejecuta OCR si no --run)
  │
  ├─ Docker Compose: docker-compose.yml + docker-compose.runtime.yml
  │    ├─ db_bootstrap → state/db/{fsm,queue,event,materialized}.db
  │    ├─ ocr_router → /app/data/inbox (g3_runtime_data VOLUME)
  │    ├─ llm_worker → runtime/engine.py
  │    │     └─ G3 necesita GROQ_API_KEY para unidades TRANSLATE/PARTIAL
  │    │          (NO declarada en environment del Compose runtime)
  │    ├─ assembler → HostTectonicRunner, /app/output VOLUME
  │    ├─ reconciler → autoridad SQLite
  │    └─ sweeper → GAP-0.5-03 ya identificado
  │
  └─ Laboratorio D-1/D-2: + docker-compose.convergence-lab.yml
       ├─ /workspace:ro (código actual) y /app writable
       ├─ G3 fake interno + dummy key + red interna
       └─ preflight C0; C2 histórico ejecutó OCR/G3/G5 y Tectonic con fake

  No equivaler host inbox ↔ named volume sin transferencia explícita.
  No equiparar fake lab ↔ proveedor/modelo comercial válido.
```

## 10. REGISTRO DE EVIDENCIA — PRIMERA PASADA

| E-ID | Severidad provisional | OBSERVED (archivo::símbolo) | REQUIRED / DECISION / límite | Disposición |
|---|---|---|---|---|
| **E-0.7-001** | P2 | `pyproject.toml::project.scripts` expone `translator-pdf=apps.cli.main:main`; CLI `translate` admite PDF por SHA sin invocar R1. | D-1 seleccionó CLI; no es sinónimo de LLM ejecutado. | OBS |
| **E-0.7-002** | P2 | `apps/cli/main.py::handle_translate` selecciona `repo_root/data/inbox` salvo `--inbox-dir`; `--run` usa `preflight_product_run` y exige cwd/inbox canon. | Ruta host y namespace Docker no son automáticamente la misma ubicación. | H-0.7-A |
| **E-0.7-003** | P2 | `apps/cli/pdf_inbox.py::submit_pdf_to_inbox` escribe archivo temporal en inbox, hace flush/fsync, hash SHA de bytes, y publica con `os.link`/verifica re-admisión. | Publicación local de admisión segura; no equivale a visibilidad desde OCR remoto ni PDF final. | OBS |
| **E-0.7-004** | P2 | `docker-compose.yml` define worker-base con `./:/app`, `sqlite_data:/app/infra/db`, caches, red chaos, restart y `build`. | Archivo base heredado, no confundir con overlay de runtime ni su testabilidad aislada. | OBS |
| **E-0.7-005** | P2 | En Compose base, `llm_worker` apunta a `runtime/engine.py`, pero porta `IS_BENCHMARK=1`, `GEMINI_API_KEY` dummy y dependencia de Toxiproxy; fake Gemini publica puertos. | **No** llamar productivo al compose base sin override; censo de roots no implica la opción seleccionada real. | CONFIG HISTÓRICA |
| **E-0.7-006** | P2 | `docker-compose.runtime.yml` hace `volumes: !override` para servicios OCR/G3/G5/auxiliares, expone mismos `g3_runtime_{state,data,output}`, reconfigura paths SQLite y `IS_BENCHMARK=0`. | Topología local de estado común prevista; no hay verificación de volúmenes físicos ni de egress. | OBS |
| **E-0.7-007** | P2 | Compose runtime declara `toxiproxy/fake-gemini: profiles: [lab]` y restablece `depends_on` G3 solo a db_bootstrap; red restante de stack base sigue `chaos_net`. | Sin perfil activo, los servicios heredados de chaos quedan excluidos; no prometer aislamiento de red del stack comercial. | OBS |
| **E-0.7-008** | P2 (reclasificada v1.0.1) | `docker-compose.yml` y `.runtime.yml` no inyectan `GROQ_API_KEY`; `runtime/engine.py::_create_chunk_processor` la exige para inferencia; laboratorio sí agrega clave dummy. | El proveedor/modelo comercial no fue elegido (PPPR.0.4 DQ-04/DC-04); un archivo `.env` host no se transmite automáticamente al contenedor. Launcher externo NO VERIFICABLE. | **OBS P2 / GAP-0.7-01 candidato NO CONFIRMADO** |
| **E-0.7-009** | P2 (reclasificada v1.0.1) | CLI host escribe `data/inbox` local; OCR Compose lee `/app/data/inbox` en volumen nombrado; falta bind host en YAML base+runtime. | C2 histórico del owner admitió desde contenedor efímero con `--inbox-dir /app/data/inbox`. No hay contrato aprobado de CLI Windows directa a daemon Docker sin puente. | **OBS P2 / GAP-0.7-02 candidato NO CONFIRMADO** |
| **E-0.7-010** | P2 | `docker-compose.convergence-lab.yml` usa imagen local fija sin build/pull, `/workspace:ro`, seis volúmenes `nocopy`, dummy Groq y `g3_fake` interno en red `internal:true`. | Perfil controlado C0–C4; no demostrar despliegue comercial con esa topología. | LAB |
| **E-0.7-011** | P2 | `apps/lab/convergence_compose_preflight.py::inspect_topology` valida composición lab declarativa sin mostrar secretos; exige imagen/volúmenes/DB/puertos/perfiles/fake y rechaza drift. | Preflight **específico del laboratorio**, no validador universal del runtime comercial. | TESTIGO NOT_RUN |
| **E-0.7-012** | P2 | `tests/unit/test_convergence_compose_preflight.py` y `test_b032_offline_pdf_lab.py` prueban configuraciones/fakes y rutas de ejecución sintéticas, en este turno solo **leídos**. | Ningún PASS, Docker o CI de PPPR.0.7 acreditado. | TESTIGO NOT_RUN |
| **E-0.7-013** | P2 | `docker-compose.golden.yml` define solo variantes de G3/G5 con endpoint/clave Gemini y documentación "producción/calidad"; no es la combinación D-1/D-2 seleccionada por el Atlas. | No importar `GEMINI_API_URL` o `fake-gemini` a G3 Groq por nombre de "Golden". | HISTÓRICO |
| **E-0.7-014** | P2 | `runtime/engine.py::_create_chunk_processor` lee `GROQ_API_KEY`, inicializa proveedor solo cuando corresponde inferencia, configura quotas SQLite y mantiene `llama3-70b-8192` literal. | Clave/configuración y modelo son frentes distintos; modelo retirado y fallback pertenecen a **PPPR.0.4**, no duplicar GAP. | H-0.7-B |
| **E-0.7-015** | P2 | `apps/bootstrap/provider_stack_factory.py::build_provider_stack` selecciona Groq por defecto e inyecta api_key; otro proveedor no se selecciona por presencia de `GEMINI_API_KEY` heredada. | No afirmar que fake Gemini sea proveedor comercial de la ruta actual ni publicar credenciales. | OBS |
| **E-0.7-016** | P2 | `infra/db/bootstrap.py::bootstrap_all_databases` crea fsm/queue/event/materialized bajo `SQLITE_STATE_DIR`, aplica DDL y pragmas WAL/NORMAL; no crea `documents.db` al iniciar. | `documents.db` puede ser creado luego por `SQLiteProfileStore`/repositorio; no declarar ausencia automáticamente GAP. | H-0.7-C |
| **E-0.7-017** | P2 | `infra/db/connection.py::resolve_sqlite_path` redirige SOLO `infra/db/*.db` a `SQLITE_STATE_DIR`, mientras `APP_ROOT` y paths absolutos controlan la raíz. `ensure_fsm_database_attached` verifica destino del alias. | Contrato de estado por namespace; comprobar combinaciones de argv/env sin inferir DOBLE base desde nombres. | H-0.7-C |
| **E-0.7-018** | P2 | OCR y assembler abren `infra/db/documents.db` tras bootstrap y construyen allí tablas necesarias; conexión SQLite `check_same_thread` por defecto y `get_connection` con WAL/NORMAL. | Capacidad de creación condicional, no prueba de arranque/ACL/volúmenes compartidos en Windows. | OBS |
| **E-0.7-019** | P2 | `OCRRouterDaemon` vigila `workspace_dir/data/inbox`, mueve exitosos a archive y fallidos a error con motivo JSON; opera desde cwd del daemon. | Datos / errores / archivo requieren persistencia compartida y permisos; el host no se inspeccionó. | H-0.7-D |
| **E-0.7-020** | P2 | G5 usa `COMPILER_OUTPUT_DIR` (default `output`) y `HostTectonicRunner` con `TemporaryDirectory` y copia de assets desde `APP_ROOT` o cwd, más SHA/canonical path. | Estado/salida/configuración deben coincidir con volumen y root; validación de PDF físico queda PPPR.0.8. | OBS |
| **E-0.7-021** | P2 | `Dockerfile` instala Python 3.11 y dependencias nativas, descarga Tectonic 0.15.0 con `curl`, sin SHA/digest verificado en la instrucción; `pip install .` resuelve dependencias generales no bloqueadas. | Riesgo de reproducibilidad/supply-chain; **sin requisito firmado/host ni build real**, no asignar P1 por mera ausencia de lock. | H-0.7-E |
| **E-0.7-022** | P2 | `.dockerignore` excluye `.env`, DB y PDF raíz; `pyproject.toml` incluye dependencias `pytesseract`/`docling` aunque la factory no los selecciona en la ruta PyMuPDF. | Dependencia declarada ≠ motor activo. No proponer instalación/refactor por intuición. | OBS |
| **E-0.7-023** | P2 | `.github/workflows/ci.yml` dispara PR hacia main/pipeline_stabilization y `continuous-verification.yml` lo mismo; no incluye branch `pdf-pdf-product-readiness` en esos triggers. | PRs documentales internos no equivalen a CI PASS; cualquier ejecución requiere run/SHA verificable. | TESTIGO / LÍMITE |
| **E-0.7-024** | P2 | `docs/.../handoff/LABORATORIO_Y_REPRODUCCION.md` registra Windows PowerShell 5.1, Docker Desktop Linux, override de runtime y lab, caches offline y recursos C2; distingue recetas no reejecutadas y pruebas anteriores del owner. | Evidencia histórica válida con fecha/corte, sin asumir máquina actual, RAM libre, imagen local o passwords. | HOST NO VERIFICABLE |
| **E-0.7-025** | P2 | `docker-compose.yml` mantiene `sweeper` y override runtime no lo desactiva; los hosts/servicios efectivos no se inspeccionaron. | **Propagación de GAP-0.5-03** previamente probado por composición; no abrir segundo GAP. | GAP HEREDADO |
| **E-0.7-026** | P2 | El laboratorio C0 con config y testigos C2 con fake comprueban solo topología limitada, Tectonic sintético/real según corrida y código de aquel SHA; no acreditan variables secretas reales, egress, facturación ni recuperación global en 2026-11-20. | Separar fake, preflight estático, testigo histórico del owner y seguridad de producción. | NO VERIFICABLE |

| **E-0.7-027** | P2 | `LABORATORIO_Y_REPRODUCCION.md` tabla C2: admisión CLI desde contenedor efímero de Compose con `--inbox-dir /app/data/inbox`, exit 0, mismo namespace de OCR. | Falsador de que CLI→OCR siempre está desconectada; no prueba CLI Windows ni modelo real. Evidencia histórica del owner, NOT_RUN hoy. | C2 HISTÓRICO RECONCILIADO |
| **E-0.7-028** | P2 | Atlas v1.0.2 §1 advierte expresamente el desajuste potencial entre inbox CLI host y volumen OCR; `apps/cli/pdf_product.py::preflight_product_run` exige cwd/inbox canónico en `--run`. | Precondición ya documentada; foreground reutiliza módulos en otro modo, no implementa puente hacia daemon Docker. | MODALIDAD DELIMITADA |
| **E-0.7-029** | P2 | Los YAML base+runtime mantienen `GEMINI_API_KEY` dummy y limpian `GEMINI_API_URL`, pero no pasan `GROQ_API_KEY`; solo el lab la inyecta con fake. `provider_stack_factory` usa Groq por defecto. | PPPR.0.4 GAP-01 y DQ-04/DC-04 ya gobiernan proveedor/modelo comercial pendiente; no proponer versionar secretos. | CONFIG COMERCIAL NO APROBADA |
| **E-0.7-030** | P2 | Árbol de `main` con 1094 blobs: 4 archivos Compose YAML; ningún launcher `.ps1`, `.sh`, `.bat` o `.cmd` versionado. `docker-compose.golden.yml` declara overlay Gemini y no está seleccionado por Atlas. | Lanzadores host externos siguen UNKNOWN. No afirmar que un archivo llamado golden sea el deployment vigente. | CENSO DE ROOTS |
| **E-0.7-031** | P2 | `infra/db/bootstrap.py` crea fsm/queue/event/materialized bajo `SQLITE_STATE_DIR`; `connection.resolve_sqlite_path` redirige `infra/db/*.db` (incluye documents/rate_limits al abrirse) y `SQLiteProfileStore` crea perfil bajo conexión docs. | La ausencia de `documents.db` en bootstrap no prueba falla: creación lazy. Permisos/ownership del volumen siguen NO VERIFICABLE. | SQLITE POR COMPOSICIÓN |
| **E-0.7-032** | P2 | `.runtime.yml` ubica Toxiproxy/fake Gemini bajo perfiles lab, sustituye `depends_on` de G3 y pone `IS_BENCHMARK=0`; `.convergence-lab.yml` agrega fake Groq y red `internal:true` ausente en base. | Red sin egress pertenece al laboratorio; no atribuir la misma garantía a Compose runtime comercial ni afirmar stack efectivo ejecutado. | TOPOLOGÍAS DISTINTAS |
| **E-0.7-033** | P2 | `Dockerfile` usa imagen Python 3.11 flotante, descarga Tectonic 0.15.0 sin checksum explícito, instala dependencias sin lock y no fija `USER`; overlay runtime no declara `user` ni `cap_drop`. | Riesgos de build/supply-chain y privilegios si se construye esa imagen; C2 usa otra imagen histórica. Sin host/contrato de despliegue no convertir a P1. | RIESGO P2 |
| **E-0.7-034** | P2 | `.github/workflows/{ci,continuous-verification}.yml` disparan PR hacia main/pipeline_stabilization, no hacia rama general PPPR; tests de preflight son lab/fake y de HostTectonicRunner usan mock. | No inferir CI PASS o test físico desde código versionado o PR Draft #72. | CI NOT_RUN |

**Segunda pasada §7.1:** E-0.7-001…034, **34 E-IDs estables y todos P2**; E-008/009 pasan de P1 candidato a P2 por falta de contrato de despliegue comercial/host aprobado. Las observaciones permanecen; GAP-0.7-01/02 solo son IDs **CANDIDATOS NO CONFIRMADOS**, no OPEN ni implementables. Sin P0/P1 confirmados ni PASS físico.

## 14. GAPs CANDIDATOS — NO CONFIRMADOS (0 GAP OPEN)

| ID provisional | Observación/cadena causal | Required y límite | Estado y destino preliminar |
|---|---|---|---|
| **GAP-0.7-01 (CANDIDATO, NO CONFIRMADO v1.0.1)** | G3 exige `GROQ_API_KEY` para inferencia pero Compose base+runtime no la inyecta; lab sí pasa dummy. | El proveedor/modelo comercial no está seleccionado (PPPR.0.4 DQ-04/DC-04). No se acreditaron launchers host externos ni secreto real. | **NO PROMOVIDO A P1**: E-008/029 P2; DQ-0.7-01 y DC-0.7-02. Reexaminar únicamente si se selecciona ese modo/proveedor |
| **GAP-0.7-02 (CANDIDATO, NO CONFIRMADO v1.0.1)** | CLI de Windows no conecta por defecto inbox local al volumen del OCR Compose; C2 admitió desde contenedor con volumen compartido. | D-1/D-2 requiere continuidad, no específicamente admisión host→Docker sin puente; Atlas ya documenta el riesgo y el modo host no fue aprobado como requisito separado. | **NO PROMOVIDO A P1**: E-009/027/028 P2; DQ-0.7-02 y DC-0.7-01. Mantener C2 acreditado históricamente |

**No duplicar:** GAP-0.5-03 sweeper, GAP-0.4-01 proveedor/modelo retirado, GAP-0.4-03 destino en→es, GAP-0.2-02 geometría/G5; no suponer que configuración potencialmente incorrecta ha producido daño comercial.

## 15. HIPÓTESIS EN SEGUNDA PASADA Y CUESTIONES DIFERIDAS

| ID | Pregunta y falsador | Estado |
|---|---|---|
| **H-0.7-A** | ¿CLI host y OCR Docker comparten inbox? | **CONFIRMADA diferencia estática** E-002/009; **RESUELTA para C2** por admisión dentro del contenedor E-027/028; **NO VERIFICABLE** el soporte de CLI Windows→Compose → DQ-0.7-02 |
| **H-0.7-B** | ¿La credencial llega al proveedor comercial elegido? | **CONFIRMADA ausencia Groq en Compose base+runtime** E-008/029; backend comercial y launcher externos **NO VERIFICABLE** → DQ-0.7-01, PPPR.0.4 |
| **H-0.7-C** | ¿Bootstrap y apertura de documents/quotas usan namespace correcto? | **CONFIRMADA POR CÓDIGO** E-016/017/018/031: rutas `infra/db/*.db` redirigidas por `SQLITE_STATE_DIR`, documents.db creada al usarse; permisos reales **NO VERIFICABLE** → DQ-0.7-03 |
| **H-0.7-D** | ¿Inbox, archive, error, assets y output están disponibles? | **CONFIRMADA TOPOLOGÍA DECLARATIVA** E-006/019/020; lectura y escritura física en host/volúmenes **NO VERIFICABLE** → DQ-0.7-03 |
| **H-0.7-E** | ¿Tectonic, imagen y dependencias se reproducen en entorno real sin egress? | **CONFIRMADO riesgo de build sin digest/lock** E-021/033; Tectonic real/host **NO VERIFICABLE** → DQ-0.7-04 |
| **H-0.7-F** | ¿El Compose runtime excluye chaos y benchmark? | **CONFIRMADA CONFIGURACIÓN YAML** E-005/007/032: profiles lab y `IS_BENCHMARK=0`; configuración efectiva host **NO VERIFICABLE** → DQ-0.7-03 |
| **H-0.7-G** | ¿Reconciler/sweeper están declarados y operan seguros? | **CONFIRMADA DECLARACIÓN** E-025/032; no duplicar **GAP-0.5-03**; contenedores activos no observados → DQ-0.7-03 |
| **H-0.7-H** | ¿Secrets, red, privilegios y logs son adecuados para producción? | **RIESGOS P2 OBS** E-029/032/033; host y configuración secreta **NO VERIFICABLE** → DQ-0.7-04 |
| **H-0.7-I** | ¿CI y fake acreditan despliegue o ciencia? | **RECHAZADA COMO GARANTÍA** E-011/012/023/026/034; tests NOT_RUN, C2 histórico fake → DQ-0.7-05 |

### 15.1 Deferred Questions de segunda pasada (§8.2; no cerradas como garantía)

| ID | Motivo de NO VERIFICABLE y efecto sobre cierre estático | Destino |
|---|---|---|
| **DQ-0.7-01** | No están elegidos proveedor/modelo comercial ni mecanismo aprobado de suministro de secretos; no hay acceso a host/credenciales. **No bloquea** observar YAML/G3, sí impide acreditar inferencia real. | PPPR.0.4 DQ-04/DC-04, ADR Maestro/Execution Plan y testigo autorizado cuando proceda |
| **DQ-0.7-02** | No existe decisión de que la CLI directa en Windows deba alcanzar OCR en Docker sin transferencia; el C2 admitió desde contenedor. Launcher/volúmenes externos desconocidos. **No bloquea** demostrar C2 ni advertir el límite; impide declarar el modo host validado. | ADR Maestro (modalidad), Execution Plan (preflight de ingreso), PPPR.0.8 si se autoriza |
| **DQ-0.7-03** | La versión efectiva de Docker/Compose, las ACL/UID, mounts, estado real de SQLite y servicios de recuperación dependen de un host no inspeccionado. **No bloquea** el censo declarativo; no acredita arranque ni durabilidad física. | PPPR.0.8 y/o gate operacional aislado del Execution Plan |
| **DQ-0.7-04** | Los digest de build, cachés Tectonic, exposición de red, usuario real, logs y entrega de secrets no se verificaron en imagen/host productivo. **No bloquea** registrar riesgos acotados; sí impide garantía de seguridad/despliegue. | ADR Maestro/Execution Plan; testigo focal PPPR.0.8 si se autoriza |
| **DQ-0.7-05** | Los workflows no incluyen PR a la rama general y la suite de este HITO no se ejecutó; C2 es histórico con fake. **No bloquea** revisión de archivos, sí cualquier afirmación de CI/LLM real o ciencia PASS. | PPPR.0.8/0.9 y gobernanza futura de CI |

### 15.2 Decision Candidates (NO APROBADOS)

| ID | Pregunta estrictamente pendiente | Destino |
|---|---|---|
| **DC-0.7-01** | ¿Modalidad inicial soportada: CLI dentro del contenedor, CLI host con puente o foreground? No construir nuevo servicio por anticipación. | ADR Maestro / Execution Plan |
| **DC-0.7-02** | Tras elegir el backend en PPPR.0.4, ¿cómo inyectar secrets sin versionarlos ni exponerlos? | ADR Maestro / Execution Plan |
| **DC-0.7-03** | ¿Qué controles mínimos de identidad/imagen/red/caché/recursos aplican al despliegue aprobado, sin convertir el laboratorio en producción? | ADR Maestro; NADR solo si es necesario; Execution Plan |
| **DC-0.7-04** | ¿Cuál es el preflight no destructivo mínimo de modalidad, mounts, Compose efectivo y configuración sin divulgar secretos? | Execution Plan una vez aprobada la modalidad |
## 16. RESPUESTAS A LA SEGUNDA PASADA

El Compose compartido permite que OCR/G3/G5 accedan a volúmenes comunes. C2 acreditó **admisión CLI dentro del contenedor** con fake y volumen compartido; una CLI directa de Windows necesita puente/launcher no documentado como modalidad aprobada. G3 carece de credencial Groq inyectada por el Compose base+runtime, pero la decisión de proveedor comercial permanece abierta en PPPR.0.4. Los dos candidatos observados son **P2 NO CONFIRMADOS**, no P1 ni GAPs abiertos.

Se verificó por código la redirección `SQLITE_STATE_DIR` y creación lazy de `documents.db`; el overlay runtime desactiva benchmark y perfila fake/chaos como laboratorio. Host y Compose efectivo, identidad/ACL, imágenes reales, secrets y Tectonic físico son **NO VERIFICABLE**. Sweeper sigue siendo GAP-0.5-03, no se duplica. No hay PASS de producto.

## 17. RECONCILIACIÓN DE MODALIDADES Y NO-REGRESIÓN

| Fuente/contrato | Estado exacto | Disposición |
|---|---|---|
| D-1/D-2 y Atlas v1.0.2 | Ruta única; Atlas descriptivo, advierte separación host/Docker | No inventar una segunda arquitectura por la entrada |
| C2 histórico del propietario | CLI dentro de contenedor efímero, `--inbox-dir /app/data/inbox`, fake interno, PDF real de laboratorio | Acredita continuidad en ese corte/modalidad; no producción ni Windows CLI externa |
| CLI directa Windows + Docker daemon | Checkout host distinto de volumen Compose, sin bridge en YAML | DQ-0.7-02/DC-0.7-01, no fallo general de ruta |
| G3 comercial | `GROQ_API_KEY` exigida, no entregada en Compose runtime; modelo/proveedor sustituto no aprobados | Observación P2; PPPR.0.4 DQ-04/DC-04, no duplicar modelo/idioma |
| PPPR.0.5 FROZEN | Sweeper Compose GAP-0.5-03 P1 OPEN | Se conserva su dueño, no duplicar en 0.7 |
| PPPR.0.6 FROZEN | G5 Tectonic/asset/publish auditados por código | No fabricar fallo físico sin testigo |
| F17-BIS | P6 histórico multirruta y NADR-F17BIS-06 PROPOSED | No norma principal ni obligaciones MUST aplicables automáticamente |

**Riesgos condicionados, no incidentes probados:** si se elige Groq y se lanza sin secret, G3 falla cerrado al necesitar inferencia; si se exige CLI host frente a OCR Docker sin transferencia, el PDF quedará en otro inbox. Debe decidirse primero modalidad y backend. El laboratorio fake no convierte esos escenarios en un PASS comercial ni autoriza ejecutar servicios.
## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN — v1.0.1.** 34 E-IDs (34 P2, 0 P1), 2 GAP candidatos **NO CONFIRMADOS**, 9 hipótesis parcialmente clasificadas, 5 Deferred Questions con razón/no-bloqueo/destino y 4 Decision Candidates sin aprobación. Resta checklist §8.1–8.2 y verificaciones finales de alcance/contraejemplos; host/Compose físico NO VERIFICABLE. Sin tests, CI, Docker, API, SQLite/corpus ni implementación.

**Gate Git:** PR interno Draft con **solo este HITO**, `pppr/hito-0.7` → `pdf-pdf-product-readiness`; PR general #66 sigue Draft hacia `main`. No FROZEN, no merge y no cambios de código de producción. Luego de cierre y autorización: integrar, verificar en general, eliminar rama corta antes de abrir PPPR.0.8.
