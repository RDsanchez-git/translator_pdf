# W08-2b — Evidencia de snapshots de contexto durables (WORKING)

**Estado:** contrato candidato, solo revisión; no productor/consumidor productivos conectados.
**Dependencias:** [PR #38](https://github.com/RDsanchez-git/translator_pdf/pull/38) (DTO `ContextSnapshotV1`), [issue #36](https://github.com/RDsanchez-git/translator_pdf/issues/36), testigos estrictos [PR #37](https://github.com/RDsanchez-git/translator_pdf/pull/37).
**Rama:** `w08-2b-durable-context-boundary-review` en relación con `pipeline_stabilization`; no fusionar antes de #38.

## Corte atómico implementado

`derive_verified_plan_contexts(plan, ast)` reconstruye la generación de contextos desde el AST y verifica la pertenencia de miembros y unidades de inferencia. No acepta `GLOBAL_ROOT` como identidad válida de inferencia ni acepta mezclar miembros de contextos distintos en un chunk.

`DurableContextPlanRepository.enqueue_verified()` persiste dentro del mismo `chunk_plan_write_scope` de `queue.db` el plan, las tareas y las instantáneas contextuales. En reintento idéntico verifica filas existentes y no reinicia tareas; una generación anterior sin snapshots no puede ser adoptada de forma automática.

`load_verified()` reconstruye desde otra conexión, compara el plan, la generación AST, la cobertura de contextos y los checksums y contenido de los snapshots con lo derivado del AST. La ausencia de tabla, snapshot, el `manifest_sha256` divergente o una alteración del contexto abortan la carga. No usa RAM previa al reinicio ni migra historiales en secreto.

## Brecha detectada e intencionalmente NO corregida

`OCRRouterDaemon._process_document()` actualmente genera `ChunkPlan` con `raw_ast` sin enriquecer. El agrupador utiliza `structural_path` (a menudo ausente) y el fallback `GLOBAL_ROOT`, por lo que llamar a este adaptador desde el OCR Router actual **fallaría explícitamente**, que es preferible a guardar una mentira. El siguiente corte W08-2c debe corregir productor y consumidor con tests de traspaso real, sin crear otro orquestador.

El adaptador W08-2b **no** se invoca desde producción. No cambia `schema_queue.sql`, `runtime.engine`, `SyncProviderBridge`, la caché, los receipts, la política W06 ni la ciencia de baseline.

## Casos de aceptación

Pruebas offline SQLite descartable: rehidratación interproceso, idempotencia, rechazo de plan legacy sin contextos, corrupción de snapshot, cobertura faltante, ID `GLOBAL_ROOT`, profundidad inconsistente, AST de generación distinta, rollback tras error SQL y transacción externa. La CI ejecuta estos tests en un paso separado sin Docker ni proveedor.

**No cierre de W08-2b:** integración con productor real, contexto efectivo del prompt, modelo, caché v2 y replay siguen pendientes. El hash contextual no autoriza reintentos de efectos externos.
