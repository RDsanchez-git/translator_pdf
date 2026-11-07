# W08-2a — Contrato candidato de contexto e identidad reutilizable

**Corte:** 2026-11-07.
**Estado:** WORKING OBSERVATION / NON-NORMATIVE / REVIEW ONLY / NOT MERGED / NOT PRODUCTION CERTIFIED.
**Issue rector:** #36. **Testigos de caracterización:** PR #37 (3 PASS / 4 STRICT XFAIL).
**Base:** `pipeline_stabilization` @ `6edd24a5b5324cf1834aef1e2af40d50d4d9f81c`.

## 1. Delimitación

**No** se altera F17-BIS NADR-05 FROZEN, F18 scientific identity ni la autoridad de intento W06-R1. Esta nota especifica una representación que puede probarse antes de decidir dónde persistirla. No sustituye D-1/D-2 pendientes de ratificación. No autoriza usar un hash local como clave de idempotencia del proveedor.

Se observaron las siguientes brechas en la ruta productiva:
- `HierarchicalContextEnricher` construye mapeos `CTX_<blake2b>` a secuencias de objetos `{level,title}`.
- `ChunkPlan` conserva `context_id`, pero no una instantánea contextual autosuficiente.
- `SyncProviderBridge.execute_chunk()` crea `ResolvedContext(..., breadcrumbs=())`, sin hidratar contenido del documento.
- El stack productivo conecta `CachedLLMProvider` a `infra/db/materialized.db` por defecto; la clave del almacén legado es solo `prompt_hash`, lectura tolera fallos convirtiéndolos a MISS y puede rebautizar el chunk de un resultado guardado.
- La autoridad de intento W06-R1 reside en `queue.db`, sus estados/fences/receipts, no en la caché.

## 2. Contratos puros versionados candidatos

`ContextSnapshotV1` encapsula `document_id`, `ast_hash`, `context_id`, breadcrumbs estructuradas `{level:int,title:str}`, serialización JSON canónica y `snapshot_sha256`. Verifica consistencia **interna** y detecta corrupción del contenido serializado, pero **no prueba procedencia** ni permite afirmar que `context_id` se calculó a partir de esas breadcrumbs. La comparación con el productor real y la pertenencia de cada unidad al plan son controles separados. `GLOBAL_ROOT` se rechaza como contexto no resuelto; el contexto raíz legítimo debe resolverse por un `CTX_...` del enriquecedor, con frame explícito `[ROOT_DOCUMENT_CONTEXT]`.

`InferenceReuseIdentityV1` ata generación, `manifest_sha256`, `chunk_id`, `context_snapshot_sha256`, `prompt_hash`, `provider_id`, `model_name`, `prompt_version`, `target_language` y `effective_config_sha256`. Su `reuse_sha256` proviene de JSON canónico versionado. El `effective_config_sha256` **debe** ser producido desde opciones reales (routing/dialect, temperatura, límites y demás parámetros con efecto semántico) en el composition root; no se inventa un valor de configuración ni se confía en metadatos del cliente. El `prompt_hash` se calcula sobre el esquema efectivo **después** del pruning por presupuesto y de la preparación de payload, no sobre un prompt ideal.

`execution_id`, worker/lease/fencing, resultado y estado de caché quedan fuera del hash de reutilización; siguen siendo responsables de autoridad, progresión y observabilidad. Las pruebas solo acreditan determinismo y sensibilidad a dimensiones explícitas.

## 3. Trabajo todavía necesario para W08-2b (NO implementado)

1. **Fuente autoritativa:** elegir y probar la transacción de persistencia de snapshots de contexto verificados bajo `(document_id, ast_hash, context_id)`, vinculados al mismo `ChunkPlan`/manifest que produce el enriquecedor. Un hash de un dict arbitrario no basta. Probar reinicio desde proceso nuevo y lectura después de commit; sin fallback a estado en RAM ni `GLOBAL_ROOT` inventado.
2. **Proveniencia y tipado:** comprobar que los títulos/niveles y `context_id` proceden de la misma generación AST. Declarar y comprobar el algoritmo de identificación versionado del productor o referenciar directamente su evidencia. Resolver la frontera `list[dict{level,title}]` hacia `ResolvedContext.breadcrumbs: tuple[str,...]` sin `str(dict)` ni pérdida silenciosa del nivel.
3. **Composición G3:** hidratar bajo autoridad del plan antes de permitir provider I/O; verificar que el `prompt_hash` represente el prompt efectivamente enviado, incluida selección del modelo/fallback y parámetros reales.
4. **Caché v2:** almacenar/releer identidad completa; consulta y retorno deben rechazar mismatches de identidad de generación, contexto, prompt, modelo, versión, chunk y proveedor. **No servir silenciosamente entradas antiguas** cuya identidad no puede demostrarse. Elegir migración explícita o nuevo espacio de claves, no un `COALESCE` que asuma compatibilidad de v1.
5. **Fallo de caché y W06:** contrastar el test actual `test_cache_fault_tolerance`, que acepta I/O fail→miss→provider, con los requisitos fail-closed. Un fallo de lectura no prueba que una llamada externa anterior no ocurrió. Cualquier retry/replay debe pasar por la autoridad G3 de W06; un cache hit no es un receipt ni concede permiso autónomo de publicación.
6. **Receipts:** enlazar identidad de inferencia, snapshot de contexto, intento y resultado validado en una fuente durable única por hecho, sin duplicar `event.db` y `chunk_result_receipts` por reflejo. Evaluar compatibilidad de tablas existentes y ventanas de crash de forma explícita.

## 4. Criterio de esta revisión

- Contratos puros versionados, objetos inmutables y hashes deterministas.
- Variar cualquier dimensión semántica declarada cambia `reuse_sha256`.
- `GLOBAL_ROOT` no resuelto, frames malformados, hashes faltantes y serializaciones manipuladas fallan explícitamente.
- Batería offline sin DB, Docker, PDF privado, red, SDK o tokens reales.
- Pyright/Import Linter y tests en el head de revisión: **pendiente de CI**.
- Los 4 XFAIL de PR #37 permanecen abiertos; este PR **no** los convierte en PASS.

**No cierre:** `W08-2a=CONTRACT PROPOSED`; `W08-2b=PENDING`; `W08-INTEGRAL=NOT CERTIFIED`; `F18/W06 AUTHORITY=UNCHANGED`.
