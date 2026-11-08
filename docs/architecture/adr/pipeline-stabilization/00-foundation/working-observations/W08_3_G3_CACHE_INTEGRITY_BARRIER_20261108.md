# W08-3 / H02 — Barrera mínima de caché legacy en G3

**Estado:** WORKING OBSERVATION · DRAFT · NO NORMATIVO · NO MERGE · NO DEPLOY
**Dependencia:** stack PR #40→#44, sobre #44 en 175f3ea76fe8b849b3398cc848849ec1b816f2bc.
**Marco:** convergencia PDF→PDF R1/R2/R3, candidato D-1/D-2 §§7–8, expediente H01/H02 v0.3, issue #36.

## H01: continuidad técnica, decisión formal pendiente

- Dirección candidata: una CLI adaptadora, G3→G5 como referencia condicional, transferencia selectiva de capacidades R1/R3 y sin ejecución duplicada.
- W08-2a/b (#38/#39) ya están integrados; #40→#44 continúan Draft con pruebas focales. Una aprobación formal G-1/G-2/G-3 no se presume.
- El trabajo aquí no forma parte de otra fase, no altera corpus/oráculos y no habilita despliegue ni merge.

## H02: hallazgo y alcance exacto del delta

`runtime/engine.py::_create_chunk_processor` llamaba `build_provider_stack()` omitiendo `cache_db_path`. La factory habilita por defecto `CachedLLMProvider`. Esa caché lee filas heredadas solo por `prompt_hash` y tolera errores de lectura como MISS; no consume todavía `InferenceReuseIdentityV1`.

**Cambio aplicado:** G3 pasa `cache_db_path=None` explícitamente; conserva el provider Groq, rate limiter y circuit breaker; se impide que el camino G3 lea o escriba una fila `llm_translation_cache` sin identidad completa. Testigos unitarios offline verifican el opt-out en el Engine y la ausencia de construcción de `CachedLLMProvider` en la factory.

**Este cambio no implementa W08-3 completo ni desactiva de manera universal cualquier consumidor externo de `CachedLLMProvider`.** El resto de H02 sigue abierto: derivación verdadera de configuración/idioma/modelo efectivos, huella del prompt post-compresión, validación de identidad en lectura, rechazo de filas históricas no verificables, fallo cerrado de lectura y pruebas adversarias por contexto/generación más reinicios. La decisión de volver a habilitar cache debe tener testigos y autoridad; un cache hit nunca concede reintento de un efecto incierto W06.

## Evidencia y falsadores

- **POSITIVO requerido:** `_create_chunk_processor` configura `cache_db_path=None` y el proveedor se construye sin decorator `CachedLLMProvider`, preservando wrappers requeridos.
- **NEGATIVO/STOP:** un refactor retira el opt-out; una instancia G3 accede a `llm_translation_cache`; un error se interpreta como MISS que autoriza una llamada no gobernada; una generación `G3_EXTERNAL_UNKNOWN` vuelve a ser ejecutable.
- Solo pruebas sintéticas; sin PDF real, volumen, proveedor externo, consumo de cuota ni estado productivo. El verdict se registrará con CI en el commit exacto.
