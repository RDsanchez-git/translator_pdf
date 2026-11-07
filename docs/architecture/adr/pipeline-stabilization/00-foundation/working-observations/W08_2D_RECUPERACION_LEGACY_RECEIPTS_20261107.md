# W08-2d — Propuesta de recuperación legacy exclusivamente por receipts

**2026-11-07 · WORKING OBSERVATION · CANDIDATE · NO DEPLOY / NO MERGE AUTOMÁTICO**

**Dependencia de revisión:** [PR #40](https://github.com/RDsanchez-git/translator_pdf/pull/40) (OCR→G3 con contexto versionado). La rama W08-2d parte de ese head; el alcance propio es recuperar resultados legacy ya persistidos, sin nueva inferencia y sin migrar el estado previo.

## Hechos que motivan el corte

El Engine de W08-2c realiza `DurableContextPlanRepository.load_verified()` antes de inspeccionar el estado FSM o las tareas. Eso aborta ante planes previos sin `g3_context_snapshots` incluso si *todas* las tareas están `RESULT_STAGED`/`COMPLETED` con receipts íntegros. En cambio, `runtime/publication_pipeline.py::advance_staged_document()` ya implementa publicación, verificación, finalización y CAS de FSM sin proveedor externo. Reaprovechar esta rutina es menor delta y menor riesgo que inventar un sistema paralelo de publicaciones.

## Delimitación del contrato

1. `preflight_g3_context(..., allow_receipt_only_legacy=False)` mantiene el rechazo por defecto. Un contexto moderno con snapshots exige `load_verified`; uno moderno que haya perdido snapshots no se reinterpreta silenciosamente como legacy.
2. Una excepción manual `allow_receipt_only_legacy=True` es **solo** aplicable a un plan histórico sin AST enriquecido ni identidades `CTX_...`, con todas sus tareas homogéneas `RESULT_STAGED` o `COMPLETED`. Se ejecuta la validación ya existente `load_staged_chunk_responses(..., allow_completed=...)` sobre todas las unidades, receipts, `execution_id`, miembros y hashes.
3. `recover_legacy_staged_document(..., approved_by_operator: bool, owner_id)` es entrada de **recuperación separada del Engine automático**, no una opción de crear tareas. Verifica estado FSM `PROCESSING`, ejecuta el preflight y delega exclusivamente a `advance_staged_document()`. No tiene referencia a LLM, `SyncProviderBridge`, proveedor, scheduler, caché, migraciones ni nuevo `claim`.
4. La autorización booleana representa **una precondición explícita en la API, NO autenticación, autorización de usuario ni decisión registrada**. Requiere una barrera operativa externa, identidad auditada, respaldo consistente y exclusión de consumidores legacy. No se crea CLI/daemon ejecutable para usar esta ruta en producción en este PR.
5. Planes incompletos, `G3_EXTERNAL_UNKNOWN`, `RETRYABLE_ERROR`, tareas parciales, receipts corruptos, ausencia de aprobación y generaciones de contexto moderno sin snapshot se rechazan antes de publicar, sin modificar sus estados. No se fabrica `GLOBAL_ROOT`, no se reinicia un `execution_id`, no se altera la autoridad W06.
6. La transacción física sigue dividida entre `queue.db`, `materialized.db` y `fsm.db`. La rutina existente ofrece idempotencia y validación de las ventanas de crash cubiertas por B4/3b, **no atomicidad cross-DB** ni garantía de exactly-once externo.

## Gates que todavía bloquean despliegue de #40

- **Barrera de versión/arranque y despliegue:** impedir que un ejecutor anterior reciba planes contextualizados o que haya dos runtimes con interpretaciones distintas; acreditar exclusión y rollback seguro, con testigos negativos. Este PR **no implementa ese gate**.
- **Inventario local:** contar estados reales de `queue.db`/`fsm.db`/receipts de generaciones anteriores, sin leer/alterar los documentos canónicos ni exponer DBs privadas. No se hizo.
- **Disponibilidad del AST histórico:** la recuperación manual necesita el AST original de la generación y comprueba su hash semántico. Ausencia/corrupción bloquea. No hay reconstrucción de contexto o plan a partir de un PDF externo.
- **Capacidades de operador:** mecanismo de aprobación autenticado y auditado de cada generación, protección de exclusividad/lease y ventana de congelamiento; no basta pasar `approved_by_operator=True`. No se conecta ninguna ruta automática al helper de recuperación.
- **Compatibilidad de schema y clasificación:** verificar mediante pruebas de DB descartables los estados legacy y las ventanas B4/3b. Concluir sobre garantías observables sin relajar oráculos NADR FROZEN ni convertir resultados de CI científicos FAIL en PASS.

**Veredicto:** W08-2d puede caracterizar un *subconjunto* de recuperación legacy terminada; no certifica el despliegue ni resuelve automáticamente las generaciones incompletas. W08-2c (#40) sigue DRAFT hasta resolver los gates de rollout y tener evidencia focal de seguridad.
