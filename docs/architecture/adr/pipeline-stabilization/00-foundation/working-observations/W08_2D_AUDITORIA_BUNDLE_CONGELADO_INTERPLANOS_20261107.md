# W08-2d — Auditor de bundle congelado interplanos y runbook de corte (candidato)

**Fecha:** 2026-11-07 · **WORKING OBSERVATION / DRAFT / NO DEPLOY / NO MERGE.**

**Dependencias:** PR #40 (contexto OCR/G3) → #41 (recuperación de receipts legacy) → #42 (fence SQLite) → #43 (aprobación firmada ligada a queue.db) → este corte de auditoría de copias congeladas. Sigue siendo parte de la matriz §7 del documento candidato D-1/D-2; no reactiva las hojas de ruta generales.

## Fronteras efectivamente comprobadas

`audit_frozen_bundle(directory)` recibe un **directorio aislado existente** con copias cerradas y checkpointed de `queue.db`, `fsm.db`, `materialized.db` y `ast_cache/*.ast.json` por generación; `event.db` puede incluirse y, en tal caso, se valida su esquema e integridad SQLite. No hace backups de procesos vivos, ni toma snapshots de otras bases, ni abre conexiones a entornos reales, ni llama proveedores. Conexiones SQLite `mode=ro&immutable=1` y `PRAGMA query_only=ON`; si hay sidecars `-wal/-shm/-journal` se rechaza en lugar de asumir que el archivo principal incluye todas las transacciones.

El auditor verifica integridad física SQLite y tablas requeridas, correspondencia plan–AST por `ChunkPlan.from_json` y hash semántico de generación (distinto de la identidad del oráculo científico), cobertura completa de `chunk_tasks` por manifest, receipts ligados a tareas/execution_id y sha256 de respuestas, FSM por generación, existencia de publicación/materialización y cobertura de nodos. Rechaza `READY_FOR_ASSEMBLY` sin publicación, proyecciones sin publicación, AST ausente/cambiado y tareas sin plan. Emite un DTO con digest SHA-256 ligado al **contenido de los archivos congelados**, cantidades de generaciones, estados inciertos, casos solo de receipts y publicaciones, sin imprimir texto ni identificadores de documentos.

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
