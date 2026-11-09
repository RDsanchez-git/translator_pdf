# W08-2c — OCR/G3: fronteras de contexto verificado (corte de revisión)

**Estado:** DRAFT / NO MERGE / NO CERTIFICACIÓN INTEGRAL / NO REPLAY.  
**Dependencias:** issue #36 → PR #38 (W08-2a, DTO) → PR #39 (W08-2b, transacción SQLite) → PR #40 (W08-2c, enlace OCR/Engine).  
**Base de producción estable:** `pipeline_stabilization` @ `6edd24a5`; ningún artefacto F17-BIS FROZEN cambia.

## Cambio exacto

1. OCR usa `prepare_contextual_plan` antes de persistir AST y plan. El enriquecedor asigna `CTX_<BLAKE2B>` a nodos no encabezado; cada secuencia de inferencia se agrupa por ID de contexto y no por `structural_path` ausente. Los encabezados quedan aislados como PRESERVE, no se solicita una inferencia para encabezados ni se acepta `GLOBAL_ROOT` como permiso de inferir.
2. El contrato `compute_ast_hash` semántico existente excluye `control_plane`. El productor verifica que el hash permanezca idéntico tras agregar metadatos; la referencia de generación de AST y el manifest no mutan su semántica. Se **persiste el AST anotado** para que una rehidratación desde disco conserve la misma evidencia de contexto, no una instancia efímera.
3. La nueva frontera OCR → `DurableContextPlanRepository.enqueue_verified` mantiene una transacción local de `queue.db` para plan/tareas/snapshots. El archivo AST y FSM siguen teniendo sus propios commits separados; no se inventa atomicidad inter-DB ni archivos.
4. Engine llama `load_verified` antes de reclamar tareas o construir un proveedor; el plan previamente persistido sin snapshots no se adopta ni se rellena con contexto vacío. El trabajo de recuperación de resultados ya staged continúa exigiendo la evidencia contextual, pero no inicializa proveedor.
5. El `SyncProviderBridge.execute_chunk` requiere snapshot correspondiente al documento, generación, `context_id` y profundidad de la unidad. Formatea los frames como breadcrumbs legibles de tipo `H1: Methods`; si falta o diverge, emite `W08_G3_UNVERIFIED_CONTEXT_BEFORE_PROVIDER` **antes del POST**. El modo `execute(node)` legacy no se promueve como entrada productiva de G3.

## Invariantes de validación

- Ruta sintética OCR → plan → SQLite → nueva conexión → bridge fake transporta los encabezados correctos y no mezcla secciones homónimas por coincidencia textual.
- Contexto ausente, de otra generación, contexto `GLOBAL_ROOT` o una generación con AST/manifest divergentes falla explícitamente, sin servicio externo.
- Los tests de W06 se adaptaron a planes enriquecidos: timeout con respuesta perdida permanece `G3_EXTERNAL_UNKNOWN`; no se permite segundo efecto automático.
- PRESERVE mantiene capacidad de ejecución sin montar un proveedor; no cambia la publicación/receipt.
- Integración en CI: Pyright, Import Linter, unitarios, B03, W06, W08-2b, W08-2c, suite general. Sólo pueden considerarse demostrados los veredictos efectivamente observados sobre el head.
- El Regression Gate conserva su fallo histórico por corpus privado no materializado. Los tres fallos de extracción vectorial en tests generales B02 no se convierten en PASS.
- **No se modifica** `CachedLLMProvider`: `prompt_hash` sigue siendo insuficiente como identidad semántica por sí solo. Los cuatro XFAIL de PR #37 no se resuelven integralmente con una prueba de contexto real. F18 identidad científica y W06 autoridad de intento permanecen separados.

## Limitaciones y siguiente frontera

**No hay upgrade silencioso de generaciones existentes** en `queue.db`. La política de migración de trabajos en curso y la verificación de seguridad del repliegue/recovery requieren diseño específico antes de desplegar: el fail-closed local puede frenar una generación legacy, pero no puede inventarse retrospectivamente su contexto. La compatibilidad del `ASTRegistry` con nodos anotados y el efecto de encabezados multi-nivel se prueban de manera explícita.

**W08-3 pendiente:** ligar `InferenceReuseIdentityV1` con el proveedor, configuración efectiva, prompt post-compression, base de caché y recibos. La caché v1 actual **no se considera segura para reutilización entre contextos/modelos**; no activar replay/retry de efectos inciertos por un cache hit. Aún falta el contrato de error de cache con autoridad W06.

**Veredicto del corte:** Implementación candidata en PR #40; no autoriza merge por sí sola hasta CI y revisión de fixtures heredadas. No certificar fidelidad científica ni PDF→PDF integral.
