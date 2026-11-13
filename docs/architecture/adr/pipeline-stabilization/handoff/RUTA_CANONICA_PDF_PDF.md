# Ruta canónica PDF→PDF implementada

**Sujeto:** código fusionado a pipeline_stabilization por PR #46 (merge commit 6818e86e21b14e77a606f0c863e9c199b4627601). **Alcance:** topología y control del laboratorio con fake; no producción certificada.

## Responsabilidades únicas

| Frontera | Entrada/ejecutor autorizado | Resultado |
|---|---|---|
| Admisión | apps.cli.main:main, comando translate, apps.cli.pdf_inbox | SHA-256 de bytes fuente; inbox compartido |
| OCR | apps/ocr_router/__main__.py | PyMuPDF, ASTRegistry, perfil, activos, ChunkPlan contextual y snapshots |
| G3 | runtime/engine.py | claim/lease, PRESERVE sin POST, TRANSLATE mediante SyncProviderBridge.execute_chunk, receipts y publicación |
| Materialización | runtime/publication_pipeline.py | proyecciones por node_id/version e idempotencia |
| G5 | apps/compiler/__main__.py | CQRSAssemblyContextResolver, Tectonic, PDF y transición fenced a COMPLETED |
| Recuperación | apps/daemons/reconciler.py y runtime/sweeper.py | recovery y cuarentena seguras, sin reintento ciego del efecto incierto |

**Camino oficial:** CLI translate (solo admisión) → data/inbox → OCR Router → G3 → G5 → PDF físico. Los daemons independientes se declaran en docker-compose.yml + docker-compose.runtime.yml. El override docker-compose.convergence-lab.yml es **exclusivo de pruebas** y no sustituye esa composición de producto.

**Modo foreground:** translate --run usa las mismas clases a través de apps/cli/pdf_product.py, solo en un workspace y generación separados. No ejecutarlo concurrentemente con los daemons sobre la misma generación/SQLite. Es herramienta controlada de diagnóstico, no un segundo motor productivo.

## Identidades y persistencia

- document_id: SHA-256 de los bytes del PDF.
- ast_hash: generación AST; manifest_sha256: identidad del plan; chunk_id: unidad G3; node_id: miembro AST/proyección.
- queue.db: tasks, claims, execution_id, recibos; fsm.db: estado/CAS; materialized.db: proyecciones; documents.db: perfil auxiliar; filesystem: AST, activos y PDF.
- No se afirma transacción común entre proveedor, filesystem y SQLite. RESULT_STAGED se puede recuperar sin reinferencia; old-owner no puede publicar. G3_EXTERNAL_UNKNOWN no autoriza segundo POST ni reconciliación automática.
- El G3 canónico mantiene cache_db_path=None para evitar replay de caché legacy insuficientemente identificada.

## Código que NO es root productivo

El símbolo handle_translate_async en apps/cli/main.py falla con C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED. La implementación histórica R1 fue separada a apps/cli/legacy_translate_async.py. AsyncDispatcher y TranslationPipeline sirven a compatibilidad/tests y benchmark. LLMWorkerDaemon R3 conserva un main ejecutable manualmente, pero no lo eligen los roots soportados en Git. Posibles lanzadores externos siguen UNKNOWN: no declarar retirada total.

## Límites de aceptación

Un HTTP 200 del fake, un PDF de una página y FSM COMPLETED no certifican traducción auténtica, cobertura vectorial, matemática, fidelidad STEM, costes de proveedor real ni readiness de producción. B02_UNREPRESENTED_VECTOR_DRAWING es rechazo seguro cuando no se puede representar una región; no deshabilitarlo para conseguir un PASS. Los NADR FROZEN y oráculos científicos conservan precedencia.

Véanse [el runbook del laboratorio](LABORATORIO_Y_REPRODUCCION.md) y [las actas del cierre](EVIDENCIA_Y_CIERRE.md).
