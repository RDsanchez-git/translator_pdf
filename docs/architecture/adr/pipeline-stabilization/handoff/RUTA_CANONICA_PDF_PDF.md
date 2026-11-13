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

## Contrato de handoff y autoridades — lectura desde proceso nuevo

| Límite | Producido y persistido por | Verificación antes de consumir |
|---|---|---|
| CLI → OCR | Admisión content-addressed, PDF físico en inbox compartido | document_id corresponde al SHA-256 de **bytes**; la CLI por defecto fuera de Docker puede apuntar a otro inbox |
| OCR → G3 | AST y ast_hash en registro/FS, perfil, plan/manifest, miembros node_id y snapshots contextuales durables | Misma generación, mismo plan digest y contexto válido antes de llamar al proveedor; no usar datos de una generación distinta |
| G3 → publicación | Claim/lease/execution_id, respuesta staged, receipt por unidad, finalización de tarea y proyección por node_id | Fencing vigente, receipt/plan completos, publicación idempotente; preservar la barrera READY_FOR_ASSEMBLY hasta materializar |
| Publicación → G5 | AST/perfil/activos + proyecciones de la generación; tarea ASSEMBLER bajo lease | Resolver CQRS rechaza proyección ausente o identidad desajustada, old-owner no publica; PDF físico no equivale a fidelidad científica |
| Fallo → recuperación | Reconciler, Sweeper y repositorios con CAS/lease | G3_EXTERNAL_UNKNOWN permanece en cuarentena sin segundo POST automático; staged durable puede publicarse sin inferencia repetida; G5 reconcilia archivo/SQLite sin prometer transacción distribuida |

El modelo de persistencia utiliza SQLite **separadas** (queue, fsm, materialized y auxiliares), filesystem y proveedor externo. Ni el resultado remoto ni el rename del PDF comparten una transacción atómica con todos los commits SQLite. Un restart debe reabrir los datos durables y verificar fencing, no inferir autoridad del mero estado de un fichero. Los mecanismos positivos/negativos se acreditaron por sujeto en [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md), **no** como garantía universal.

## Selección de ejecución y compatibilidad

- **Multiproceso canónico:** translate solo admite el PDF; los workers OCR/G3/G5 continúan de forma independiente. Compose de producto declarado: docker-compose.yml **más** docker-compose.runtime.yml; no se demostró despliegue/cutover de esa composición sobre bases legacy productivas.
- **Composición de laboratorio:** añade docker-compose.convergence-lab.yml con imagen local fijada, proveedor fake privado y volúmenes nuevos. Es una prueba de la **misma ruta lógica**, no un entrypoint de producción alternativo.
- **Foreground aislado:** translate --run recorre los mismos contratos con la misma lógica; la equivalencia T07 se acreditó sobre un workspace separado, no coexistencia sobre las mismas DB/lease.
- **Legacy:** handle_translate_async bloqueado con C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED en apps/cli/main.py; implementación R1 conservada en apps/cli/legacy_translate_async.py; TranslationPipeline y AsyncDispatcher conservados para tests/benchmarks/compatibilidad. LLMWorkerDaemon R3 puede invocarse manualmente, pero no es seleccionado por roots soportados. No se afirma ausencia de consumidores fuera de Git ni autorización de borrado.

**Prevalencia:** NADR FROZEN aplicables → D-1/D-2 aprobadas (dirección) → implementación integrada y pruebas sobre SHA específico → plan cerrado y expediente forense histórico. La documentación de handoff explica el estado actual; no sustituye decisiones normativas ni inventa garantías nuevas.

## Límite de soporte y próximos cambios

La acreditación del PR #46 corresponde al **laboratorio con fake**, con PDF sintético representable, inferencia TRANSLATE simulada y PRESERVE sin POST. Quedan pendientes traducción lingüística evaluable, preservación matemática/vectorial W09, cobertura del corpus, coste y comportamiento del proveedor real, compatibilidad con generaciones legacy y autorización de producción. La protección B02 sigue fail-closed ante contenido vectorial que no puede conservarse en Layout/AST.

Si se modifica un productor o consumidor, volver a acreditar **esa frontera** con identidad y oráculos propios sobre el nuevo commit; no extender por inferencia el PASS de C2. Para diagnóstico y futuro ensayo consultar [LABORATORIO_Y_REPRODUCCION.md](LABORATORIO_Y_REPRODUCCION.md); para autoridad y testigos, [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md).
