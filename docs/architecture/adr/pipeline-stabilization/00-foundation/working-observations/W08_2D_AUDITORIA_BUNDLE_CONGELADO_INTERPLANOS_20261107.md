# W08-2d — Auditor de bundle congelado interplanos y runbook de corte (candidato)

**Fecha:** 2026-11-07 · **WORKING OBSERVATION / DRAFT / NO DEPLOY / NO MERGE.**

**Dependencias:** PR #40 (contexto OCR/G3) → #41 (recuperación de receipts legacy) → #42 (fence SQLite) → #43 (aprobación firmada ligada a queue.db) → este corte de auditoría de copias congeladas. Sigue siendo parte de la matriz §7 del documento candidato D-1/D-2; no reactiva las hojas de ruta generales.

## Fronteras efectivamente comprobadas

`audit_frozen_bundle(directory)` recibe un **directorio aislado existente** con copias cerradas y checkpointed de `queue.db`, `fsm.db`, `materialized.db` y `ast_cache/*.ast.json` por generación; `event.db` puede incluirse y, en tal caso, se valida su esquema e integridad SQLite. No hace backups de procesos vivos, ni toma snapshots de otras bases, ni abre conexiones a entornos reales, ni llama proveedores. Conexiones SQLite `mode=ro&immutable=1` y `PRAGMA query_only=ON`; si hay sidecars `-wal/-shm/-journal` se rechaza en lugar de asumir que el archivo principal incluye todas las transacciones.

El auditor verifica integridad física SQLite y tablas requeridas, correspondencia plan–AST por `ChunkPlan.from_json` y hash semántico de generación (distinto de la identidad del oráculo científico), cobertura completa de `chunk_tasks` por manifest, receipts ligados a tareas/execution_id y sha256 de respuestas, FSM por generación, existencia de publicación/materialización y cobertura de nodos. Rechaza `READY_FOR_ASSEMBLY` sin publicación, proyecciones sin publicación, AST ausente/cambiado y tareas sin plan. También rechaza receipts, publicaciones, proyecciones y snapshots **huérfanos de generación**, y verifica hashes de respuestas/materializaciones, correspondencia de nodos y metadatos de snapshots. Emite un DTO con digest SHA-256 ligado al **contenido de los archivos congelados**, cantidades de generaciones, estados inciertos, casos solo de receipts y publicaciones, sin imprimir texto ni identificadores de documentos.

**Una clasificación `receipt_only` del reporte NO equivale a permiso de recuperación:** el helper manual de #41 vuelve a verificar cada receipt y estado, y sigue prohibida la inferencia para `G3_EXTERNAL_UNKNOWN`. La auditoría no altera el estado ni repara datos.

## Runbook propuesto, NO ejecutado

1. **Autorización externa previa:** registrar change ticket, aprobación de operador en IAM/secrets externos y persona responsable de las llaves. No registrar claves privadas ni PDFs en Git/GitHub/CI.
2. **Congelar entrada y dispatch:** detener OCR Router, G3 Engine, reconciler, assembler y **todos** los procesos que puedan escribir en queue/FSM/materialized/event/AST. Confirmar físicamente ausencia de workers, leases, API calls/egress en vuelo y procesos antiguos. El mero hecho de `PROCESSING=0` no demuestra ausencia de efectos inciertos.
3. **Inventario/backup coordinados:** mientras se mantiene el bloqueo de escritores, crear **copias completas/checkpointed mediante backup de SQLite**, con archivo AST por generación y artefactos adicionales del runtime necesarios. Cerrar conexiones de copia; verificar que no existan WAL/journals pendientes. Este PR no incluye un script que copie las bases de producción ni automatiza el backup. Sellar fuera de GitHub rutas, checksums, hora, versión de proceso y chain-of-custody del bundle.
4. **Auditar las copias:** ejecutar el auditor sobre un directorio descartable aislado. Si falta una generación, coincide un hash solo parcialmente, hay receipts/proyecciones huérfanas o hay `G3_EXTERNAL_UNKNOWN`, registrar disposición y **no** reinterpretarlo como autorización de retry. Si hay discrepancias, abortar el despliegue y conservar el conjunto intacto.
5. **Verificar el estado actual y la firma:** obtener la huella de `queue.db` actual, emitir aprobación corta desde canal separado y revalidar bajo `BEGIN IMMEDIATE` al activar #42/#43. El inventario de copias **NO** puede sustituir esa revalidación de la base real: sus rutas/digests difieren por diseño.
6. **Activar solo en ventana aprobada:** con acceso restringido DDL y procesos antiguos detenidos, activar fence, verificar triggers y registro de autorización, arrancar exclusivamente ejecutores nuevos; comprobar logs y ausencia de accesos antiguos. No asumir que los triggers protegen `fsm.db`, `materialized.db`, eventos o archivos.
7. **Rollback con fail-closed:** tras activación, no reiniciar un binario antiguo contra la misma cola, retirar triggers ni restaurar `queue.db` aisladamente. Primero detener todos los servicios y analizar estado `G3_EXTERNAL_UNKNOWN` y publicaciones. Rollback únicamente mediante restauración **coherente del bundle interplanos** y reconciliación autorizada de efectos externos/receipts; la restitución de datos puede requerir decisiones humanas, no reintentos automáticos.

## Qué todavía NO está cubierto

- El bundle validado **no prueba simultaneidad de las copias**: depende del congelamiento y custodia del operador. Tampoco demuestra que una API externa no haya aplicado una llamada previa al corte.
- No implementa identificación/autorización de operador por IAM, bitácora append-only externa ni verificación automática de procesos de Windows/Docker; HMAC en #43 solo acredita conocimiento de clave.
- No integra una CLI de rollout, no firma ni cifra archivos de backup, no integra oráculos científicos ni certifica contenido PDF/AST vectorial.
- No modifica una ruta automática de recuperación legacy y no resuelve cache v2/replay W06.

**Gate de aceptación pendiente:** testigos offline y CI sobre head exacto; posteriormente revisión operativa verificable de stop-the-world, backup/restore, IAM/custodia y no reintento. PR #40–#43 y este corte deben continuar Draft hasta que esa evidencia exista.

## Endurecimiento de integridad (revisión adicional del mismo PR)

La revisión de código posterior a los primeros 12 PASS detectó que se comparaban hashes
locales sin aplicar las validaciones B2/B3 ya existentes de identidad de tareas, parser
de receipts, resultado materializado y versión de publicación. También faltaba exigir la
cobertura completa de snapshots para generaciones W08 modernas.

El auditor reutiliza ahora validadores de **solo lectura**: carga B2 de plan/tareas,
parser de respuestas G3, rehidratación de nodos y verificación B3 de publicación;
derivación pura de snapshots W08-2b. Diferencia generaciones legacy sin provenance CTX
de generaciones modernas, mantiene receipt_only como categoría no autorizante y
cubre todos los archivos aislados en la huella (incluyendo metadatos de custodia).
Las pruebas adversarias adicionales ejercitan publicados, completos, staged y
falsificaciones con checksum coherente. Ninguna garantía operativa externa nueva
se declara acreditada: DRAFT / NO MERGE / NO DEPLOY.


## Revisión de suficiencia operativa y gates de transición (2026-11-08)

**Estado:** WORKING OBSERVATION / PROCEDIMIENTO CANDIDATO / NO CERTIFICADO.
**Sujeto:** PR #44, código validado focalmente en e874445600f9ea8f7901338c4a3835784fdb069e; dependencias DRAFT #40→#43; base pipeline_stabilization en 3263b2c4a776e42012635a442846c4baed8940be.
**Autoridad:** D-1/D-2 §§7–8 CANDIDATE/NON-NORMATIVE; W06 y NADR FROZEN donde apliquen. Esta revisión NO ratifica G-1/G-2/G-3 ni aprueba merge, despliegue o trabajo en datos reales.

### Frontera exacta: auditoría no equivale a backup o restauración

- **Alcance del auditor #44:** lee copias cerradas de queue.db, fsm.db, materialized.db y ast_cache por generación; event.db opcional *solo para este auditor*. No acredita la simultaneidad de captura, el estado externo ni custodia.
- **Estado complementario de runtime:** el código de OCR/G5 usa documents.db (perfiles y repositorio documental); el ejecutor puede utilizar rate_limits.db (cuotas); data/ast_cache, data/inbox, data/archive, data/error, activos de imagen y output/ contienen datos de entrada, AST y PDFs. Su política de backup, retención y restauración debe fijarse en el manifiesto del despliegue realmente utilizado. No afirmar que #44 valida esos artefactos.
- **Topología de volúmenes no fijada:** docker-compose.yml monta sqlite_data en /app/infra/db, mientras docker-compose.runtime.yml emplea g3_runtime_state en /app/state, g3_runtime_data en /app/data y g3_runtime_output en /app/output. infra/db/connection.py resuelve rutas mediante SQLITE_STATE_DIR. No inferir el entorno activo del YAML: exigir rutas reales/volúmenes, configuración sin secretos y hashes.
- **Inventario de actividad mínimo:** db_bootstrap (DDL), ocr_router, llm_worker/Engine y sus heartbeats, reconciler, sweeper (WAL/FSM), assembler (G5/PDF), además de API/CLI/scripts/ingestores que tengan acceso a los mismos recursos. Controlar también las políticas de reinicio automático del Compose efectivo. Esta lista no sustituye la verificación real de procesos.
- **Falsador decisivo de protocolo:** verify_runtime_protocol() retorna sin error si todavía no existe la tabla g3_runtime_protocol_fence, por compatibilidad histórica. Por tanto, *preflight exitoso* no demuestra *fence activado*: exigir comprobación positiva de registro, protocolo, triggers y permisos antes de iniciar ejecutores nuevos.

### Matriz de aceptación y STOP (sin ejecución en este expediente)

| Gate | Testigo mínimo de aceptación | STOP / falsador | Estado |
|---|---|---|---|
| **O-0 Autoridad y sujeto** | Responsable de corte, owner/Board según §8, ticket, SHA de PR, decisión de integración diferenciada de permiso de despliegue, criterio de abort/rollback registrado. | Autoridad asumida por CI o candidatura D-1/D-2; ticket/owner/alcance ausentes. | PENDIENTE |
| **O-1 Inventario de despliegue** | Imagen/commit/procesos efectivos, Compose+overrides/env sin secretos, ruta real y volumen de cada SQLite (queue, FSM, materialized, event, documents, rate_limits cuando exista), AST, originales/activos y PDF; política de preservación por artefacto. | Ruta o volumen no reconocido; se omite una dependencia necesaria; mapeo entre fuente y copia no trazable. | PENDIENTE |
| **O-2 Parada física y egress** | Entrada bloqueada, reinicio automático controlado, escritores/legacy y heartbeats detenidos; evidencia de ausencia de llamadas externas en vuelo o disposición explícita para incertidumbre; observación antes y durante el backup. | Se usa solo PROCESSING=0/TTL de lease o el booleano drained_legacy_runtimes; subsiste writer, ingestión, reinicio o efecto externo sin disposición. | PENDIENTE |
| **O-3 Backup y custodia coordinados** | Copias completas/checkpointed obtenidas *mientras la exclusión se mantiene*, archivos AST, event.db si se usa, profiles/documents y activos/output necesarios; manifest de origen→copia, hashes, hora UTC, custodia/ACL y ausencia de sidecars en el paquete auditado. | Copias incoherentes o incompletas; WAL/archivo necesario omitido; DB vacía creada por ruta errónea; custodia imposible. | PENDIENTE |
| **O-4 Reconciliación y auditor** | audit_frozen_bundle PASS en copia aislada, hash y reporte privados; decisión por generación para pending/uncertain/receipt_only/published/orphan_fsm, leases y estados G5; G3_EXTERNAL_UNKNOWN permanece sin retry. La huella de copia NO reemplaza inventario de queue.db real. | Discrepancia entre planos o generaciones/artefactos, orfandad sin disposición, receipt_only usado como autorización, contradicción con FSM/G5. | Software offline 24 PASS; operación PENDIENTE |
| **O-5 Identidad y permisos externos** | IAM/secret store ajenos al repo, actor y aprobador verificables, segregación de claves, auditoría independiente append-only y ACL/DDL que impidan alterar el fence. | HMAC compartido tomado por identidad personal, secreto en Git/CI/logs, bitácora local tomada por inmutable, DDL sin restricción. | HMAC local probado; IAM PENDIENTE |
| **O-6 Activación explícita** | Con O-0…O-5 aprobados, inventario reciente de queue.db **real**, firma corta para esa ruta/huella, revalidación en BEGIN IMMEDIATE, cero PROCESSING/leases vivos; constancia POSITIVA de tabla/registro/triggers/protocolo antes de iniciar solo binarios nuevos. | Token vencido, cambio de inventario, escritura legacy, fence ausente aunque verify_runtime_protocol() no falle, ausencia de drenaje. | Fence+firma offline PASS; activación PENDIENTE |
| **O-7 Rollback y cierre** | Ensayo autorizado en medio descartable de restauración coherente de DBs + AST/perfiles/activos/output relevantes, sin proveedor; verificación de estado G5, PDFs y receipts, y procedimiento humano de disposición de efectos externos nuevos, con go/no-go registrado. | Downgrade en caliente, DROP TRIGGER como solución, restaurar solo queue.db, reintentar UNKNOWN o sobrescribir publicaciones/efectos posteriores no reconciliados. | PENDIENTE |

### Orden de decisión, preservación de evidencia y límite

1. **Para decidir integración secuencial #40→#44:** revisar el delta incremental, CI en SHA exacto, compatibilidad legacy y autoridad aprobada sobre el enfoque. Los controles científicos que ya fallaban se registran como FAIL reales; no se modifican oráculos. La integración del código y su activación en un entorno real son **actos distintos**.
2. **Antes de activar sobre estado real:** O-0…O-5 y un ensayo de restauración en entorno aislado deben tener recibos verificables y responsables identificados. Lo no ejecutado se informa NOT_REACHED/BLOCKED, no PASS. No ejecutar ningún paso de transición real por este documento.
3. **Durante una ventana que el operador autorice separadamente:** O-6 exige validación positiva del fence y del inventario vivo, no un simple booleano; O-7 gobierna el cierre/rollback sin romper W06.
4. **Custodia:** evidencias privadas de procesos, versiones, rutas resueltas, manifests, huellas, timestamps, aprobaciones y pruebas de restauración fuera de GitHub. No subir PDFs, DBs, textos, claves, IDs documentales en claro ni secretos.
5. **No se ha creado** CLI de rollout, IAM, sensor de egress, backup automatizado ni restaurador; #44 no certifica esos mecanismos ni habilita acciones Windows/Docker.

**Dictamen:** la capa software de #44 está validada focalmente, pero O-0…O-7 no tienen cierre operativo. Mantener PR #40→#44 en Draft y W08-2d operativo OPEN hasta actos separados de evidencia y gobierno.
