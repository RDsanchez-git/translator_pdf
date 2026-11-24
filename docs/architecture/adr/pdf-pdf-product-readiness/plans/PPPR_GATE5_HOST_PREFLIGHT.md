# PPPR Gate 5 — Preflight de host y modalidad soportada

**Estado:** procedimiento operativo LIVING / no normativo; Task 5.1.1 IN_PROGRESS, evidencia host NOT_RUN; 5.1.2 y W5.2 TODO. No sustituye al Execution Plan ni modifica criterios de aceptación.

**Base:** `7ff8b84733a63efd3012adf14070db86cff051ad`, rama `pdf-pdf-product-readiness`. CI post-merge #45314286191 SUCCESS (3/3 jobs); CV #45314286115 FAIL/DEFERRED, BASELINE_INTEGRITY_FAILURE (15 PDF privados ausentes). G1–G4 COMPLETED/PASS; 20/30 Tasks DONE, 14 GAP P1 OPEN, PRODUCT_READINESS=NOT_CERTIFIED.

## 1. Autoridad y frontera

- ADR Maestro DC-08: CLI dentro del contenedor de un nodo, D-1/D-2; no puente Windows→Docker ni modalidad distribuida.
- Execution Plan v0.5.31 §2.5.1: 5.1.1 host real soportado; 5.1.2 Compose, volúmenes, secretos, red, recuperación y permisos efectivos. No cerrar por inspección YAML o CI.
- HITO PPPR.0.7 FROZEN, especialmente E-0.7-004/007/009/016/017/021/025/035/038/039. GAP-0.7-01/02 candidatos no confirmados; GAP-0.5-03 histórico, no duplicar.
- Atlas AS-IMPLEMENTED y runbook histórico `docs/architecture/adr/pipeline-stabilization/handoff/LABORATORIO_Y_REPRODUCCION.md`: C2 positivo histórico, no prueba del host actual; no ejecutar receta C2 sin presupuesto, recursos e imagen acreditados.
- DC-03: sin proveedor, destino, datos, finalidad, retención/entrenamiento y presupuesto explícitamente autorizados, cero inferencia comercial. Este procedimiento no concede permisos.
- Un PR para G5 completo (W5.1 + W5.2 + Exit Review). No merge de Wave ni cambio a FROZEN. Actualización de los tres registros LIVING al checkpoint de cierre de Wave con evidencia.

## 2. Audit First — observaciones estáticas en la base

| Frontera | Evidencia estática | Acción necesaria |
|---|---|---|
| Entrada | `apps/cli/main.py::handle_translate`: admisión por SHA, `--inbox-dir`; foreground `--run` opt-in reutiliza OCR/G3/G5 | Comprobar un único namespace y modo operativo, no lanzar foreground junto a daemons sobre el mismo trabajo |
| Compose | Base trae chaos/fake Gemini y binds; runtime override mueve SQLite/datos/output a volúmenes comunes, benchmark 0, perfila lab | Inspeccionar composición efectiva; no iniciar base aislado ni confundir runtime con lab |
| Laboratorio | `apps/lab/convergence_compose_preflight.py` comprueba imagen histórica, red interna y clave dummy; C2 histórico | Reutilizar controles pertinentes sin importar topología histórica como autoridad productiva |
| SQLite | `infra/db/connection.py` resuelve solo infra/db/*.db bajo SQLITE_STATE_DIR; ATTACH fsm_db depende de identidad real | Comprobar paths y alias reales por conexión, persistencia entre contenedores |
| Secretos/red | Runtime no entrega GROQ_API_KEY; lab sí usa dummy; red interna solo acreditada declarativamente en lab | Sin claves reales en W5.1; comprobar aislamiento y entrega autorizada por frontera antes de 5.2.3 |
| Recuperación | Sweeper declarado; reconciler y leases existentes | Verificar GAP-0.5-03 en composición efectiva; no asumir seguridad por presencia del daemon |
| Imagen | Dockerfile fija Tectonic 0.15.0 pero no digest; instalación pip no fijada al lock | Identificar imagen/versión efectiva y recursos antes de elegir corrección de build; no descargar aún |

## 3. P0 — inventario del host real (solo lectura)

Ejecutar desde la raíz del checkout en PowerShell si sigue siendo el host Windows/Docker Desktop Linux histórico. Si cambió el host, indicar sistema y modalidad antes de adaptar. El entorno de asistencia no tiene daemon Docker ni acceso al nodo del owner.

```powershell
git rev-parse HEAD
git branch --show-current
"WORKTREE_DIRTY_COUNT=" + @(git status --porcelain).Count
docker context show
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose version
docker info --format 'os={{.OSType}} arch={{.Architecture}} cpus={{.NCPU}} memory_bytes={{.MemTotal}}'
Get-PSDrive -PSProvider FileSystem | Select-Object Name,Free,Used
docker ps --format 'running={{.Names}} image={{.Image}}'
```

No compartir nombres de contenedores ajenos o sensibles: basta indicar si existen proyectos activos del traductor y si se pueden aislar. No compartir endpoints remotos, paths personales, `.env`, secretos, tokens ni `docker inspect` completo. Confirmar explícitamente que el contexto corresponde al daemon local del nodo autorizado; el nombre de contexto no prueba localidad por sí solo.

Si no hay Docker, el daemon no responde, el host no es local o hay recursos insuficientes, detener antes de crear recursos. Compose debe entender `!override` (v2.24.4+ conforme HITO 0.7 E-035); no deducir compatibilidad solo del nombre Docker Desktop. Sin presupuesto host/disco/RAM autorizado, no ejecutar arranque.

## 4. P1 — preflight declarativo posterior a P0

Desde el checkout exacto de Gate5, sin iniciar contenedores:

```powershell
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config --quiet
if ($LASTEXITCODE -ne 0) { throw "STOP: compose runtime invalido" }
docker compose -f docker-compose.yml -f docker-compose.runtime.yml config --services
```

No publicar `config` expandido: puede incluir secretos. El siguiente paso de implementación debe evaluar de forma saneada servicio/comando, perfiles, mounts, state/data/output, rutas SQLite, usuario, capacidades, secretos presentes/ausentes sin valores, red y aislamiento. Resultado declarativo NO equivale a runtime ni a 5.1.1/5.1.2 DONE.

## 5. P2 — evidencia exigida antes de cerrar W5.1 (NOT_RUN)

Con autorización específica del nodo y presupuesto de recursos, y tras aprobar composición efectiva: usar proyecto nuevo aislado, fuente sintética, cero proveedor comercial; verificar identidad de imagen y contenedor, UID y escritura en volúmenes propios, admisión CLI interna en inbox compartido, visibilidad de mismo estado por conexiones independientes, SQLite WAL y alias, arranque/reinicio y recuperación sin borrar estado, exclusión de roots legacy/lab no autorizados, controles reales de red/secretos. El E2E fake completo y crash/replay pertenecen a W5.2 y no se declaran ejecutados aquí. Preservar artefactos y logs saneados. Si un preflight falla, STOP y RCA antes de reintentar.

**Prohibido en P0/P1:** build/pull, up/run, bootstrap, eliminación de contenedores/volúmenes, down -v, prune, llamadas externas, corpus privado, gasto. No adoptar el host histórico ni seleccionar proveedor por inferencia. Ningún PASS de host se deduce de este documento.
