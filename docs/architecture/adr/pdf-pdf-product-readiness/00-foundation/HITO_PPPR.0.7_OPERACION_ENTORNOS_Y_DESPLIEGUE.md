# HITO_PPPR.0.7_OPERACION_ENTORNOS_Y_DESPLIEGUE.md

**Estado:** FROZEN v1.0.5  
**Fecha de emisión:** 2026-11-20  
**Congelamiento:** 2026-11-20  
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
| 1.0.2-IN_PROGRESS | 2026-11-20 | Tercera pasada: confrontación con Docker Docs de `!override` (Compose 2.24.4+), transmisión explícita de secrets, preflight exclusivo LAB, privilegios/imagen y modalidad inside-container; 39 evidencias P2, 0 GAP P1 confirmado, 2 IDs candidatos NO CONFIRMADOS. Checklist final pendiente. NOT_RUN. |
| 1.0.3-IN_PROGRESS | 2026-11-20 | Cierre de hipótesis: 9 disposiciones terminales con propiedades observadas y restricciones físicas NO VERIFICABLE; 39 E-IDs P2, 5 DQ, 4 DC. Se prepara checklist formal de cierre; sin tests ni cambios productivos. |
| 1.0.4-FROZEN | 2026-11-20 | Checklist formal §§8.1–8.2, 9.2–9.4 y garantías: 39 E P2, 0 GAP propios OPEN, 2 IDs candidatos no confirmados, 9 hipótesis terminales, 5 DQ y 4 DC. Cierre de auditoría estática, NO operación comercial ni CI PASS. |
| 1.0.5-FROZEN | 2026-11-20 | Corrección documental puntual posterior a FROZEN según metodología §1.2: resumen ejecutivo alineado con severidades finales y cierre, eliminación de texto residual `NO FROZEN` tras §21.4 y continuidad del changelog histórico. **Sin cambios** a 39 E-IDs, hipótesis, GAP candidatos, DQ/DC, causalidad o garantías; NOT_RUN. |

## 1. RESUMEN EJECUTIVO

**Hecho de composición:** la opción seleccionada en el Atlas es CLI/admisión → OCR Router → `runtime/engine.py` (G3) → `apps/compiler/__main__.py` (G5) → PDF. `docker-compose.yml` es una base heredada que contiene fake/chaos y benchmark; `docker-compose.runtime.yml` sustituye montajes/estado y desactiva componentes de laboratorio por `profiles: [lab]`. `docker-compose.convergence-lab.yml` añade una composición controlada **solo para laboratorio offline con fake**, no un perfil productivo real. `docker-compose.golden.yml` presenta una intención histórica de calidad, pero no demuestra por sí solo que sea el launcher operativo aprobado.

**Credenciales de G3 — observación P2, candidato GAP-0.7-01 NO CONFIRMADO:** `runtime/engine.py::_create_chunk_processor` requiere `GROQ_API_KEY` cuando existe inferencia; `docker-compose.yml` + `docker-compose.runtime.yml` no declaran su inyección en `llm_worker`, mientras que el laboratorio emplea una clave *dummy*. Una variable en PowerShell o `.env` no llega automáticamente al contenedor sin un mecanismo de entrega explícito. **No hay proveedor/modelo comercial definitivo aprobado** (PPPR.0.4), ni consta una llamada real al proveedor: la decisión de backend y secretos permanece en DQ-0.7-01/DC-0.7-02.

**Admisión entre host y Docker — observación P2, candidato GAP-0.7-02 NO CONFIRMADO:** la CLI ejecutada desde el checkout host escribe por defecto en `<repo>/data/inbox`, mientras OCR en Compose utiliza `/app/data/inbox` en el volumen nombrado `g3_runtime_data`, sin bind automático del inbox host. **C2 acreditó históricamente la modalidad funcional de admisión mediante CLI dentro del contenedor**, con `--inbox-dir /app/data/inbox` y proveedor fake. No está aprobado el contrato de CLI Windows directa hacia ese daemon; permanece en DQ-0.7-02/DC-0.7-01, sin negar la continuidad demostrada en el laboratorio.

**Límites prioritarios:** `docker compose up` no fue ejecutado; no se inspeccionaron máquinas Windows ni volúmenes reales, configuraciones expandidas, permisos, certificados, versiones efectivas o secretos. No extrapolar evidencia de laboratorio C0–C4 con fake a egress/hosting comercial. El sweeper de Compose es un **GAP-0.5-03 preexistente**, no se abre uno duplicado aquí.

**Dictamen vigente:** auditoría estática **FROZEN v1.0.5**, **39 evidencias P2**, **cero GAP propios OPEN** y **dos identificadores candidatos NO CONFIRMADOS**. Nueve hipótesis terminales, cinco Deferred Questions y cuatro Decision Candidates con destino. El cierre no acredita un despliegue comercial, tests, CI, Docker activo, inferencia real ni certificación científica.

**Garantía limitada del cierre:** la configuración y los contratos observables quedaron inventariados con los límites de §§2, 15 y 21; no se acreditan proveedor/modelo, host Windows, Compose efectivo, accesibilidad física de cachés, seguridad operacional ni traducción EN→ES real.

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

## 10. REGISTRO DE EVIDENCIA — FINAL

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

| **E-0.7-035** | P2 | `docker-compose.runtime.yml` usa `volumes: !override`, `depends_on: !override` y `GEMINI_API_URL: !reset null`; Docker Docs exige Compose v2.24.4+ para `!override`. | Regla de parser oficial, **no** versión efectiva de Docker Desktop del propietario. El C0 histórico valida LAB, no producto. | H-F / DQ-03 |
| **E-0.7-036** | P2 | Según Docker Docs, variables de shell o `.env` sirven para interpolar; no se entregan a un contenedor sin `environment`, `env_file` u otra inyección explícita. Compose base+runtime carece de `GROQ_API_KEY`; el LAB sí pasa dummy. | Es ausencia declarativa, no prueba de inexistencia de configuración privada del operador o decisión de proveedor. | H-B / DQ-01 |
| **E-0.7-037** | P2 | `apps/lab/convergence_compose_preflight.py::inspect_topology/main` inspecciona TRES YAML y exige red interna, fake Groq, UID, `nocopy` y clave dummy, mostrando códigos saneados. | Preflight de C0 exclusivo LAB; no acredita Compose comercial ni host actual. Testigo NOT_RUN en este HITO. | H-F/I |
| **E-0.7-038** | P2 | `Dockerfile` no fija USER ni checksum de Tectonic descargado; `docker-compose.runtime.yml` no fija user/cap_drop. `apps/lab/convergence_db_bootstrap.py` fija UID10001 y declara explícitamente no ser para producto. | Riesgo contextual P2 de privilegios/imagen, sin prueba de explotación ni contrato de host; no importar controles LAB como garantía comercial. | H-E/H / DQ-04 |
| **E-0.7-039** | P2 | `apps/cli/main.py::handle_translate` soporta `--inbox-dir` y `--run` foreground; C2 histórico ejecutó admisión CLI dentro de contenedor con `/app/data/inbox`, y OCR inspecciona `workspace_dir/data/inbox`. | Continuidad del LAB histórico sin probar CLI Windows a daemon Docker; falta contrato de modalidad host. | H-A / DQ-02 |

**Severidad final §7.1:** E-0.7-001…039, **39 E-IDs estables, todos P2**. E-008/009 fueron reclasificadas sin reasignar sus IDs en v1.0.1. Los dos IDs GAP-0.7-01/02 son **CANDIDATOS NO CONFIRMADOS**, no GAP OPEN. El cero P1 nuevo no elimina el GAP-0.5-03 del sweeper ni los GAP de G3 en PPPR.0.4; tampoco acredita el despliegue comercial.

## 14. GAPs CANDIDATOS — NO CONFIRMADOS (0 GAP OPEN)

| ID provisional | Observación/cadena causal | Required y límite | Estado y destino preliminar |
|---|---|---|---|
| **GAP-0.7-01 (CANDIDATO, NO CONFIRMADO v1.0.1)** | G3 exige `GROQ_API_KEY` para inferencia pero Compose base+runtime no la inyecta; lab sí pasa dummy. | El proveedor/modelo comercial no está seleccionado (PPPR.0.4 DQ-04/DC-04). No se acreditaron launchers host externos ni secreto real. | **NO PROMOVIDO A P1**: E-008/029 P2; DQ-0.7-01 y DC-0.7-02. Reexaminar únicamente si se selecciona ese modo/proveedor |
| **GAP-0.7-02 (CANDIDATO, NO CONFIRMADO v1.0.1)** | CLI de Windows no conecta por defecto inbox local al volumen del OCR Compose; C2 admitió desde contenedor con volumen compartido. | D-1/D-2 requiere continuidad, no específicamente admisión host→Docker sin puente; Atlas ya documenta el riesgo y el modo host no fue aprobado como requisito separado. | **NO PROMOVIDO A P1**: E-009/027/028 P2; DQ-0.7-02 y DC-0.7-01. Mantener C2 acreditado históricamente |

**No duplicar:** GAP-0.5-03 sweeper, GAP-0.4-01 proveedor/modelo retirado, GAP-0.4-03 destino en→es, GAP-0.2-02 geometría/G5; no suponer que configuración potencialmente incorrecta ha producido daño comercial.

## 15. HIPÓTESIS — CLASIFICACIÓN TERMINAL Y CUESTIONES DIFERIDAS

| ID | Pregunta y falsador | Estado |
|---|---|---|
| **H-0.7-A** | ¿CLI host y OCR Docker comparten inbox? | **CONFIRMADA** diferencia de namespace para CLI host/Compose, E-002/009/039; **RESUELTA** continuidad C2 usando CLI dentro de contenedor E-027; modo Windows→daemon **NO VERIFICABLE** DQ-0.7-02 |
| **H-0.7-B** | ¿La clave Groq llega a G3 por Compose base+runtime? | **CONFIRMADA** ausencia declarativa E-008/029/036; backend futuro/operador **NO VERIFICABLE** DQ-0.7-01 y PPPR.0.4 |
| **H-0.7-C** | ¿Bootstrap y bases documents/cuotas convergen en SQLite? | **CONFIRMADA EN CÓDIGO** E-016/017/018/031 con SQLITE_STATE_DIR y lazy init; ACL/volumen **NO VERIFICABLE** DQ-0.7-03 |
| **H-0.7-D** | ¿Inbox, archive/error, assets y output están disponibles? | **CONFIRMADA** topología YAML y rutas por código E-006/019/020; accesibilidad física **NO VERIFICABLE** DQ-0.7-03 |
| **H-0.7-E** | ¿Tectonic, imagen y dependencias son reproducibles offline? | **NO VERIFICABLE** sin build/cache/host; riesgos de Dockerfile P2 E-021/033/038 y destino DQ-0.7-04 |
| **H-0.7-F** | ¿Runtime excluye chaos/benchmark y acepta tags Compose? | **CONFIRMADA** intención en YAML E-005/007/032/035/037; !override exige Compose >=2.24.4; config efectiva host **NO VERIFICABLE** DQ-0.7-03 |
| **H-0.7-G** | ¿Reconciler/sweeper son correctos en runtime? | **CONFIRMADA** declaración en Compose E-025/032; seguridad lógica **GAP-0.5-03** FROZEN, no duplicar; proceso vivo **NO VERIFICABLE** DQ-0.7-03 |
| **H-0.7-H** | ¿Red, privilegios, logs y secrets son aptos en el host comercial? | **NO VERIFICABLE** sin selección de despliegue ni acceso a host, E-029/032/033/038; DQ-0.7-04 / DC-0.7-03 |
| **H-0.7-I** | ¿CI y fake C2 constituyen PASS comercial y científico? | **RECHAZADA COMO GARANTÍA** E-011/012/023/026/034/037, NOT_RUN; DQ-0.7-05 |

### 15.1 Deferred Questions finales (§8.2: motivo, no-bloqueo y destino)

| ID | Motivo de NO VERIFICABLE y efecto sobre cierre estático | Destino |
|---|---|---|
| **DQ-0.7-01** | No están elegidos proveedor/modelo comercial ni mecanismo aprobado de suministro de secretos; no hay acceso a host/credenciales. **No bloquea** observar YAML/G3, sí impide acreditar inferencia real. | PPPR.0.4 DQ-04/DC-04, ADR Maestro/Execution Plan y testigo autorizado cuando proceda |
| **DQ-0.7-02** | No existe decisión de que la CLI directa en Windows deba alcanzar OCR en Docker sin transferencia; el C2 admitió desde contenedor. Launcher/volúmenes externos desconocidos. **No bloquea** demostrar C2 ni advertir el límite; impide declarar el modo host validado. | ADR Maestro (modalidad), Execution Plan (preflight de ingreso), PPPR.0.8 si se autoriza |
| **DQ-0.7-03** | La versión efectiva de Docker/Compose, las ACL/UID, mounts, estado real de SQLite y servicios de recuperación dependen de un host no inspeccionado. **No bloquea** el censo declarativo; no acredita arranque ni durabilidad física. | PPPR.0.8 y/o gate operacional aislado del Execution Plan |
| **DQ-0.7-04** | Los digest de build, cachés Tectonic, exposición de red, usuario real, logs y entrega de secrets no se verificaron en imagen/host productivo. **No bloquea** registrar riesgos acotados; sí impide garantía de seguridad/despliegue. | ADR Maestro/Execution Plan; testigo focal PPPR.0.8 si se autoriza |
| **DQ-0.7-05** | Los workflows no incluyen PR a la rama general y la suite de este HITO no se ejecutó; C2 es histórico con fake. **No bloquea** revisión de archivos, sí cualquier afirmación de CI/LLM real o ciencia PASS. | PPPR.0.8/0.9 y gobernanza futura de CI |

### 15.2 Decision Candidates finales (NO APROBADOS)

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
## 21. CIERRE PPPR.0.7 — FROZEN v1.0.5

### 21.1 Checklist §8.1–8.2: revisión formal de suficiencia

| Control | Resultado respaldado |
|---|---|
| Metadata, changelog, SHA y fecha | **CUMPLE**: versiones v1.0.0–v1.0.5 (corrección editorial post-FROZEN conforme metodología §1.2), baseline main/gobernanza y fecha de congelamiento |
| Perímetro y epistemología | **CUMPLE para auditoría estática**: §§2–5, distinción AUDITADO/REFERENCIADO/NO VERIFICABLE; Windows, Docker físico y proveedor comercial fuera de garantías |
| Fuentes, precedencia y §9.2 | **CUMPLE**: código, Compose, Dockerfile, Atlas descriptivo, runbook C0/C2 histórico, PPPR.0.1–0.6, Scope/principios, F18 y Docker Docs contextual. F17-BIS PROPOSED no es MUST |
| Evidencias, IDs y severidades | **CUMPLE**: 39 E-IDs consecutivos, 39 P2, 0 P0/P1; reclasificación de E-008/009 documentada |
| Fichas §4.7 para P0/P1 | **NO APLICA**: ninguno confirmado dentro del modo de despliegue decidido; no convertir riesgos de modalidades no aprobadas en defectos P1 |
| GAPs y destinos §4.8 | **CUMPLE**: 0 GAP propios OPEN; GAP-0.7-01/02 mantienen identificadores de **candidato NO CONFIRMADO**, evidencia y causas en §14, DQ/DC de destino, no son work items autorizados |
| Hipótesis y dudas §8.1–8.2 | **CUMPLE**: H-0.7-A…I terminales por propiedad; cinco DQ con motivo, no-bloqueo del mandato estático y destino; cuatro DC separadas sin decisiones prematuras |
| Reconciliación §9.3–9.4 | **CUMPLE**: §17 distingue C2 fake, Windows→Docker, Groq/config futura, GAP-0.5-03, PPPR.0.4 y PPPR.0.6; no retorna a topología F17-BIS |
| Garantías, gobernanza y siguiente paso | **CUMPLE**: §§21.2–21.4; FROZEN documental revisable en PR #72, general #66 Draft, ninguna implementación |
| Docker, Compose, tests, LLM, Tectonic real, host, SQLite privado o corpus GT | **NOT_RUN / NO REQUERIDOS para cerrar el mandato estático**, indispensables antes de certificar puesta en producción o fidelidad científica |

**Resolución §8.2:** las incertidumbres físicas NO VERIFICABLE no bloquean la descripción y clasificación de la configuración versionada; **sí** bloquean cualquier afirmación de disponibilidad comercial o de funcionamiento real de la variante host/Compose. Si se seleccionara exactamente el backend Groq actual sin inyección, faltaría entregar la clave; si se exigiera CLI Windows→daemon Docker, faltaría un puente definido. No se autoriza asumir que esos modos ya son productivos.

### 21.2 Veredicto y garantías positivas/negativas

**HITO FROZEN DOCUMENTAL v1.0.5 (2026-11-20)**: censo y análisis estático de operación, configuración, despliegue y aislamiento de la ruta D-1/D-2 en `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`. Solo se garantiza **lo observable en archivos y contratos**: separaciones entre YAML base/runtime/lab/golden, namespaces de CLI/volúmenes, redirección SQLite, claves esperadas por G3, preflight exclusivo LAB, caché Tectonic prevista, límites de la imagen y workflows existentes. El C2 original acredita históricamente la admisión dentro del contenedor con fake, no se reejecutó hoy.

**NO SE GARANTIZA**: Compose efectivo en Windows, credencial/producto comercial, modelo Groq vigente, EN→ES real, egress/FinOps, accesibilidad/permisos de volúmenes/DB, aislamiento externo, reproducción de imagen/cachés, Tectonic físico, recuperación crash, CI PASS ni fidelidad visual o científica. `PRODUCT_READINESS=PASS` sigue prohibido. Los tests, servicios, Docker Desktop, LLM, bases SQLite del propietario y corpus/oráculos no se tocaron.

**Hallazgos vivos:** GAP-0.7-01/02 son **IDs candidatos NO CONFIRMADOS**, no GAPs propios OPEN; la configuración sí tiene dos límites condicionados que deberán revisarse tras decisión de modalidad/backend. PPPR.0.5 conserva GAP-0.5-03 sobre sweeper y PPPR.0.4 conserva GAPs de proveedor/modelo/idioma, no duplicados aquí.

### 21.3 Cadena de gobernanza

Metodología ordenada v1.3.0 FROZEN → metodología forense v1.2.0 FROZEN → D-1/D-2 y Atlas AS-IMPLEMENTED descriptivo → PROJECT_SCOPE/principios y código actual, PPPR.0.1–0.6 FROZEN, F18 aplicable → **PPPR.0.7 FROZEN** → PPPR.0.8–0.9 → ADR Maestro / ADR-NADR estrictamente necesarios → Execution Plan aprobado → único PR general #66 aprobado e integrado en `main` → implementación por PR posteriores conforme a plan y tests.

### 21.4 Estado Git y siguiente gate

**HITO preparado para revisión/aprobación explícita en PR #72**, rama `pppr/hito-0.7` → `pdf-pdf-product-readiness`, un único Markdown. **FROZEN documental no equivale a aprobación externa ni CI PASS**. Tras aprobación y merge: verificar FROZEN en la rama general, eliminar la rama corta y abrir PPPR.0.8 desde el HEAD general actualizado. PR #66 sigue Draft hacia main, que permanece intacto. No activar Docker, cuentas reales, corpus o SQLite sin autorización/gate físico aislado.

> FROZEN documental ≠ despliegue comercial listo ≠ proveedor EN→ES verificado ≠ PASS CI ≠ certificación STEM.
