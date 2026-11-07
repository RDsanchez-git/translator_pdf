# W08-2c — Política propuesta de transición de generaciones G3 sin contexto durable

**Fecha:** 2026-11-07. **Estado:** WORKING OBSERVATION / GATE OPERATIVO PENDIENTE / NO IMPLANTADO.
**Alcance:** despliegue de PR #40 (OCR contextual y preflight Engine), sobre PR #38 + #39 integrados.
**Autoridad:** W06-R1 para estados/efectos externos, `ChunkPlan` + AST de generación para linaje, y gobernanza explícita del operador.
**NO** convierte fallos de baseline CV/B02 en PASS ni ratifica decisiones D-1/D-2.

## Problema concreto

El Engine propuesto usa `DurableContextPlanRepository.load_verified` al inicio. Los `chunk_plans` y `chunk_tasks` que existían antes de W08-2c pueden carecer de `g3_context_snapshots`; la función falla cerrada, incluso si la única operación posterior sería completar publicación de resultados previamente staged. El OCR propuesto registra un AST anotado y nuevos snapshots; la cola antigua no puede asumir esta evidencia por equivalencia de hash semántico, dado que el hash excluye `control_plane`. Tampoco existe una transacción entre archivos AST, FSM y `queue.db`.

**Prohibido:** poblar las tablas con `GLOBAL_ROOT`, fabricar breadcrumbs vacías, reabrir una tarea `G3_EXTERNAL_UNKNOWN`, borrar receipts para forzar reintentos, inferir el estado `NOT_STARTED` del proveedor por ausencia de caché, o migrar un AST/manifest histórico en el mismo `execution_id` sin evidencia y decisión de autoridad.

## Protocolo de adopción propuesto — NO ejecutado ni automatizado

1. **Congelar ingreso y dispatch:** antes de sustituir código OCR/Engine, detener los consumidores antiguos y bloquear nuevos claims de G3; confirmar que no queda ningún proceso legacy capaz de procesar planes creados por W08-2c. No usar despliegue mixto ni rollback automático a un runtime que permita `breadcrumbs=()`. Un despliegue seguro requiere evidencia de barrera de versión/operación, hoy no implementada como gate.
2. **Inventariar por generación** `(document_id, ast_hash, manifest_sha256)` todas las filas `chunk_plans`, `chunk_tasks`, receipts, sus estados de FSM y presencia/cobertura de snapshots. Usar consultas de solo lectura y respaldos consistentes de `queue.db`, `fsm.db`, `materialized.db` y caché AST; conservar trazabilidad de los artefactos originales. Esta política no suministra scripts de mutación.
3. **Generaciones con snapshots completos,** del mismo AST y manifest y verificadas por `load_verified`: elegibles para código nuevo una vez aprobada la barrera de versión y la recuperación de arranques. La firma por sí sola no autoriza un retry ni publicación; siguen las validaciones W06 y CP-08.
4. **Generaciones legacy en `PENDING` sin efecto externo demostrado:** siguen bloqueadas en el nuevo Engine. Un operador puede autorizar, tras comprobar ausencia de efectos/leases y consistencia del archivo original, un flujo de **nueva generación/ingesta controlada** que vuelva a construir el contexto desde el AST fuente; no completar por backfill `context_id` al azar. Una semántica de reemplazo y de deduplicación debe diseñarse y probarse antes de ejecutarse, porque `ast_hash` semántico puede permanecer igual mientras el manifest contextual cambia.
5. **Generaciones con `PROCESSING`, expiradas, `RETRYABLE_ERROR`, `G3_EXTERNAL_UNKNOWN` o autoridad incierta:** mantener cuarentena y disposición del operador según W06. `PENDING` no garantiza inexistencia de un efecto si hubo una ventana de crash; exigir evidencia del historial, nunca deducir `NOT_STARTED` de un campo aislado. Ningún retry automático.
6. **Generaciones con resultados `RESULT_STAGED`/`COMPLETED` y receipts válidos:** preservar su evidencia. Definir una ruta de recuperación **sin proveedor** compatible con datos históricos y con CP-08 mediante una revisión separada; el Engine W08-2c, tal cual, falla al preflight y no acredita esa ruta legacy. No permitir que una reparación contextual borre materialización o vuelva a inferir.
7. **Rollback / corte:** las filas creadas por W08-2c no pueden exponerse automáticamente al código anterior, porque la ruta antigua omite el preflight contextual y puede construir prompts distintos. Exigir stop-the-world o un gate de capacidad/versiones antes de activar; restaurar datos desde respaldos solo con protocolo de recovery aprobado, preservando receipts/UNKNOWN y sin cruzar SQLite sin reconciliación.

## Condiciones para desplegar #40 — todavía ABIERTAS

- Demostrar inventario reproducible y tratamiento por estado (con especial énfasis en `RESULT_STAGED`, `COMPLETED` y `G3_EXTERNAL_UNKNOWN`) sobre copias descartables de DBs, **sin** reescritura de oráculos ni ingestión de corpus privado.
- Acreditar un mecanismo de barrera de versión/arranque o una ventana operativa excluyente que impida que código legacy procese nuevos planes; prueba negativa de un rollback inseguro.
- Acreditar que el OCR Router se detiene/falla antes de una transición FSM peligrosa si la persistencia contextual falla; distinguir recuperación de AST/archivos vs transacciones `queue.db`.
- Verificar la integración exacta contra `pipeline_stabilization` tras #38/#39: análisis estático, tests W06/B03/W08-2b/W08-2c y fallo conocido CV/B02 sin reinterpretación.
- Mantener `#40` **DRAFT / NO MERGE / NO DEPLOY** hasta que el responsable apruebe el enfoque de transición o se divida en un PR de despliegue explícitamente condicionado y compatible con W06.

## Fuera de alcance

No es un diseño implementado de migraciones SQLite, ni un switch seguro de caché v1→v2, ni autorización de replay. La identidad de reutilización `InferenceReuseIdentityV1` **no** sustituye estado de intento, lease, fencing o receipt.
