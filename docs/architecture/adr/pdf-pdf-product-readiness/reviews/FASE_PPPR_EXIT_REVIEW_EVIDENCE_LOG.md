# FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/pdf-pdf-product-readiness/reviews/FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md`  
**Versión:** 0.1.21  
**Estado:** G1/G2 Exit Reviews PASS; PR90 W3.1 IN_PROGRESS con CI #45105007281 SUCCESS, H1/H3 resueltos, R10 F18-05 PARCIAL (alcance Board pendiente). Cuatro reglas F18-05 acreditables en alcance y 16 F18-04 contrastadas individualmente, NO DONE global; W3.2/G3 Exit Review NOT_RUN, 14 GAP P1 OPEN; `PRODUCT_READINESS=NOT_CERTIFIED`.  
**Fecha:** 2026-11-21  
**Última actualización:** 2026-11-22  
**Derivado de:** `PHASE_PPPR_EXECUTION_PLAN.md` v0.5.19 APPROVED/LIVING; CI #45105007281 SUCCESS sobre a49cd952…; R10/otras normas aún pendientes Board, no Gate3 Exit Review.
**Ámbito:** PPPR, ruta única `CLI → OCR → G3 → G5 → PDF`.  
**Propósito:** Registro forense incremental, por Gate Exit Review, que conserva los fundamentos empíricos, los archivos examinados, los límites de evidencia y las reglas que justifican la clasificación de **cada hallazgo nuevo DF/GF** del Deferred Findings Register.

> **Este documento SÍ es:** evidencia por DF/GF y resumen de Gate Exit Reviews efectivamente realizados.
>
> **Este documento NO es:** el Execution Plan, el Findings Register, un repositorio de resultados por batch, un NADR, un nuevo HITO forense ni una certificación del PDF final EN→ES.

**Baseline inicial del esqueleto (conservada):** 30 Tasks TODO y G1–G6 PENDING, sin Exit Review ni pruebas. **Checkpoint Wave 1.1 (2026-11-21):** Tasks 1.1.1/1.1.2 verificadas documentalmente sobre los HEAD y blobs citados en el Execution Plan §2.1.1; **no se detectó DF/GF nuevo dentro de esa revisión estática acotada**. No constituye hallazgo clasificado ni Gate Exit Review; Pyright, pytest, CI, OCR, E2E, corpus privado e inferencia NOT_RUN. Los 14 GAP-ID P1 forenses continúan OPEN y `PRODUCT_READINESS=NOT_CERTIFIED`.

**Gate 1 Exit Review registrado (2026-11-21):** revisión efectiva de criterios §2.1.3(1–4) y control §2.1.4 del Execution Plan, HEAD `718a81a7816ef91710b3a86b00cc4326b0b18262`. Baseline/trazabilidad/dependencias documentales verificadas; excepción ratificada en issue #34. La CI técnica del HEAD actual [#44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) **estaba IN_PROGRESS** al fijar el veredicto, con análisis estático SUCCESS y pruebas restantes todavía pendientes; CV [#44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) **FAIL** por 15 PDF faltantes, **no considerada PASS**. El Review se realizó, **G1 BLOCKED/PENDING_CI_HEAD**, no se habilita G2. No se identificó DF/GF nuevo en este ámbito: **ninguna entrada forense §2.N**, sin fabricar `CLOSED (NAR)` ni alterar hallazgos preexistentes.

**Complemento cronológico de evidencia y decisión (2026-11-21):** la [CI del HEAD evaluado #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) finalizó en **completed/SUCCESS**, atribuido a `718a81a7816ef91710b3a86b00cc4326b0b18262`. Jobs **Static Analysis (Pyright + import-linter), Unit Test Suite, Integration Test Suite**, incluido `Run complete technical pytest suite (excluding scientific E2E)`, finalizaron `success`. La resolución aprobada `PPPR-G1-CI-SCOPE-01` autoriza ese alcance solo para G1 §2.1.3(3); con los criterios (1), (2) y (4) ya acreditados, el **veredicto posterior de Gate 1 es PASS/COMPLETED**. El estado inicial BLOCKED queda conservado en §3.1, no se sustituye retroactivamente. La [CV científica #44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) sigue **FAIL/DEFERRED**, sin veredicto científico ni autorización de corpus; issue #34 preexistente. **0 DF/GF nuevos, G2 aún no iniciado**.

**Checkpoint histórico de G2/Wave 2.1 (2026-11-21; pre-corrección Board, NO Gate2 Exit Review):** el commit `2542d6aed46d044d5384b7004070cb3bb1c8deb7` del [PR #85](https://github.com/RDsanchez-git/translator_pdf/pull/85) contiene la implementación de Tasks `2.1.1`/`2.1.2`/`2.1.3`, con la preservación de `PhysicalRegion`, referencia de página física, manejo de dimensiones no acreditadas, normalización geométrica por página, incertidumbre `geometry_reasons`, sampler estricto primeras N páginas y detección de columnas por página. Falsadores unitarios `tests/unit/test_pppr_g2_physical_provenance.py`, integración de PDF sintético temporal `tests/integration/test_pppr_g2_physical_ingestion.py`; sin corpus privado, GT científico ni uso de proveedor comercial. [CI #44955114310](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44955114310): **completed/SUCCESS**, Static Analysis (Pyright + import-linter) SUCCESS con **0 errors / 0 warnings / 0 informations**, Unit Test Suite SUCCESS (**248 PASS**, 1254 deselected), Integration Test Suite SUCCESS, suite `pytest -m "not e2e"` **1478 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings pytest**. Esos 248 unitarios pertenecen a ejecución separada y **no** se suman a 1478. Los 10 requisitos FPPPR-04 tienen falsadores propios registrados en el Execution Plan §2.2.1 y su trazabilidad §7; no se marca Gate2 PASS antes de Wave2.2 y su Exit Review. Los defectos previstos en `GAP-0.2-01/02` siguen como antecedentes P1 OPEN hasta cierre formal; **ningún nuevo DF/GF fuera de scope fue identificado en la Wave**. Esta nota guarda evidencia de Tasks, **NO crea un finding ni acta de Exit Review**.

**Addendum correctivo del Architecture Board (2026-11-21; PR #85, mismo scope W2.1):** Dictamen FAVORABLE CON CORRECCIONES; NO autoriza merge. La inspección del HEAD anterior `c7bf6725974e77396b7bed51be29952583c14ca6` acreditó CI técnica [#44955971217](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44955971217) SUCCESS, pero reveló que OCR perdía los diagnósticos de perfil en SQLite y el consumidor podía promover layout sin conservar la incertidumbre. El commit correctivo `1ef307dae8a7009d6a7f35a6cdf28038c7a120b4` en el MISMO PR #85 adjunta `ProfileDiagnostics` al perfil, lo persiste con hash vinculado al documento y migración legada sin falsas garantías, emite telemetría acotada por ID, y exige cobertura STRICT_SCOPE y geometría sin limitaciones antes de activar el layout de doble columna. Se agregan falsadores de OCR Router real con nodo válido + nodo indeterminado, reinicio SQLite, replay, manipulación, documentos mezclados y regiones inmutables. La CI correctiva [#44960950403](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44960950403) queda **PENDING_FINAL_REVALIDATION** al redactar este addendum. La prueba exitosa del HEAD anterior NO se transfiere al nuevo HEAD: 10/10 reglas FPPPR-04, en particular R9/R10, no se reclaman nuevamente VERIFIED sin CI final y aceptación Board.

**Límites explícitos:** `ExtractionProviderFactory` conecta únicamente PyMuPDF. Los falsadores de la ruta de producto NO acreditan Docling histórico (`provs[0]`, fallback `page_no=1`, BBox `+0.01`), ni se incorpora un proveedor alternativo. `PhysicalRegion.source_document` puede conservar rutas locales en el AST persistido; evaluar minimización/redacción y privacidad antes de habilitar egress externo, que aquí NO está autorizado. El historial de 14 GAP P1 continúa OPEN; CV científica FAIL/DEFERRED, Wave 2.2 PENDING, Gate 2 Exit Review NOT_RUN y `PRODUCT_READINESS=NOT_CERTIFIED`. Ninguna Task, NADR, Gate, criterio fijo, DF/GF ficticio ni PR adicional.

**Falsadores adicionales del addendum (NOT_VERIFIED hasta CI nuevo HEAD):** `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py` recorre OCR con nodo válido e indeterminado hasta SQLite y reinicio; `tests/integration/test_g3_b4_4_profile_projection_assembly.py` comprueba lectura, hash, replay y render conservador; `tests/unit/test_pppr_g2_physical_provenance.py` añade mezcla de fuentes e inmutabilidad. Son sintéticos/offline, sin PDFs privados, proveedor comercial ni CV científica. No hay Exit Review G2.

**Addendum de revalidación técnica del HEAD correctivo (2026-11-21; no es Gate 2 Exit Review):** [CI técnica #44961625659](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44961625659) completó **SUCCESS** sobre SHA `0dc091fa7f1b3a3bbd38f9841ba4c8805061475b` con tres jobs SUCCESS (Static Analysis, Unit Test Suite, Integration Test Suite); Pyright **0 errors/0 warnings/0 informations**, import-linter PASS, unitarios **250 PASS / 1257 deselected / 3 warnings**; suite completa `pytest -m "not e2e"` **1483 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar la selección de 250 tests al resultado de 1483. Los falsadores correctivos OCR/SQLite/consumidor y el caso mixto están en el HEAD evaluado. La evidencia técnica para FPPPR-04 R9/R10 y los diez requisitos queda **CI_VERIFIED / BOARD_ACCEPTANCE_PENDING**: el Board debe revisar la corrección y el owner conserva autoridad exclusiva de merge. **PR #85 OPEN/Draft sin merge, Wave 2.2 PENDING, G2 Exit Review NOT_RUN, 14 GAP P1 OPEN, CV científica FAIL/DEFERRED, PRODUCT_READINESS NOT_CERTIFIED.**

**Checkpoint definitivo para integración W2.1 (2026-11-21; no es Gate 2 Exit Review):** el Architecture Board realizó una segunda revisión **FAVORABLE A LA INTEGRACIÓN** del PR #85 sobre el HEAD `2535860a23236a9325d56c2cb582c1c5d404265f`. [CI final de la revisión Board #44962322464](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44962322464) confirmó **completed/SUCCESS para exactamente ese SHA**, con tres jobs SUCCESS (Static Analysis, Unit Test Suite, Integration Test Suite), Pyright **0 errores / 0 advertencias / 0 informaciones**, import-linter **4/4 contratos conformes**, unitarios **250 PASS / 1257 deselected / 3 advertencias**, y suite completa `pytest -m "not e2e"` **1483 PASS / 4 SKIPPED / 20 E2E deselected / 3 advertencias**. No sumar ejecuciones separadas. La conformidad de los diez falsadores `NADR-FPPPR-04` es **CI_VERIFIED** y el dictamen del Board es **FAVORABLE_A_INTEGRACION**, limitado a la ruta conectada **PyMuPDF**, NO a Docling histórico. El owner **autoriza expresamente el merge del PR #85 tras esta sincronización documental y una CI SUCCESS del HEAD final**. Se trata de autoridad expresada en la conversación, no de un review APPROVED emitido por la API de GitHub. Los checkpoints anteriores (`#44961625659`, `0dc091fa…`) se mantienen como historial, no como evidencia del HEAD `2535860…`. Esta nota se fija **antes de ejecutar el merge**, que se verificará en GitHub después; G2 IN_PROGRESS, Wave 2.2 PENDING, Gate 2 Exit Review NOT_RUN, 14 GAP P1 OPEN, CV científica FAIL/DEFERRED, `PRODUCT_READINESS=NOT_CERTIFIED`, sin permiso de egress.

**Checkpoint técnico Wave 2.2 / PR #86 (2026-11-21; NO Gate 2 Exit Review):** implementación y falsadores de Tasks 2.2.1–2.2.3 integrados en la rama del PR #86, **sin merge**; [CI #44972570392](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44972570392) **completed/SUCCESS** sobre SHA exacto `a6ce8eb88e2c9bf50114cba26d0ecb7a80e0a865`, 3/3 jobs SUCCESS, Pyright 0 errors/0 warnings/0 informations, import-linter PASS; unitarios **287 PASS / 1273 deselected / 3 warnings** y suite `pytest -m "not e2e"` **1536 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar ejecuciones separadas. Se añadió después el falsador de reproducibilidad entre procesos/PYTHONHASHSEED en `tests/unit/test_pppr_g2_semantic_identity.py`, commit `9ab965622fcd65f7a300522598a8c696943bf79a`; su CI [#44974172865](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44974172865) **IN_PROGRESS al registrar este checkpoint**, NO certificada por el run del SHA anterior.

**2.2.1 — Identidad semántica / incertidumbre:** `core/ast/hashing.py` define `AST_SEMANTIC_PRODUCT_V2`, sensible a texto, orden, nivel H1/H2/H3 y profundidad y ajeno a IDs operacionales/geometría. Canonización Unicode NFC conservadora sin colapsar símbolos STEM. `core/layout/models.py` y `core/ast/builder.py` transportan nivel explícito y admiten evidencia de encabezados numerados (`1`, `1.2`, `1.2.3`) probada con PDF temporal en `tests/integration/test_pppr_g2_semantic_pdf_chain.py`; los encabezados no numerados permanecen `UNKNOWN` y `core/chunking/contextual_plan.py` los conserva como `PRESERVE` sin inventar H1 ni abortar OCR, con falsador en `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py`. No se certifica reconocimiento jerárquico universal de PDFs.

**2.2.2 — Propósito de generación EN→ES:** `core/prompting/inference_identity.py` define `PPPRGenerationIdentityV1` basada en el candidato W08 `InferenceReuseIdentityV1`, separando identidad semántica, identidad de generación y autoridad de intento W06. Incluye documento/AST, manifest, chunk, snapshot de contexto, prompt efectivo, idioma fuente/destino, proveedor/modelo, versión de prompt, contrato de salida y configuración efectiva/ruta de presupuesto. `apps/llm_workers/sync_bridge.py` materializa la identidad y `runtime/chunk_staging.py` la pasa al recibo durable en `infra/db/control_repo.py`, con migración SQLite aditiva y falsadores de variación de dimensiones en `tests/unit/test_pppr_g2_generation_identity.py`; no presume que dos generaciones tengan resultados científicos idénticos.

**2.2.3 — Consumidores reales e integridad:** `ASTRegistry.get_verified_document_ast` relee el JSON persistido y acredita hash semántico V2 más `artifact_sha256` separado para `node_id`, `strategy`, metadatos y demás campos durables; `core/compiler/context_resolver.py` y el runtime productivo usan lectura verificada. La huella local detecta drift accidental, **no es firma de autenticidad criptográfica frente a un actor que controle archivo y hash**. `ChunkPlan`, snapshots, contexto, receipts G3, publicación/ensamblado y replay conservan sus controles específicos; `runtime/engine.py` exige la `root_config_sha256` activa en recuperación productiva y `infra/db/control_repo.py` rechaza recibos de otra configuración, corruptos o legados no atestados. Falsadores de AST manipulado, reinicio, estrategias, jerarquía, idempotencia, cambio de generación, migración SQLite y recorrido CLI offline. La caché `CachedLLMProvider` no seleccionada permanece desactivada y el worker heredado no se presenta como conformidad del producto.

**Gobernanza y frontera:** alcance offline sintético y proveedor de extracción productivo PyMuPDF. `G2 IN_PROGRESS`, Wave 2.2 **TECHNICAL_CI_VERIFIED_PRE_BOARD** sobre SHA `a6ce8eb88e2c9bf50114cba26d0ecb7a80e0a865`, falsador entre procesos y CI del HEAD posterior **pendientes**, 3 Tasks implementadas **sin convertir revisión/merge pendiente en DoD final**. Los 14 GAP-ID P1 permanecen OPEN; no se inventan DF/GF, batches ni Gate 2 Exit Review; CV científica FAIL/DEFERRED (15 PDF privados ausentes, excepción G1 no extensible); sin egress, gasto, evaluación científica, G3, `main` ni PR #66. `PRODUCT_READINESS=NOT_CERTIFIED`. El Board revisará el HEAD documental final después de CI verde y el owner decide el merge.

**Addendum correctivo Architecture Board / Wave 2.2 (2026-11-21; PR #86; NO Gate 2 Exit Review):** segundo dictamen **FAVORABLE CON UNA RESERVA DE INTEGRIDAD**, sobre HEAD documental `9a69c70a700fa55f9370c41651c7e694896bfcac`; autorización de merge **NO emitida**. El Board identificó una colisión legítima entre identidad semántica V2 y contenido durable distinto: `register_ast()` podía sustituir silenciosamente archivos con igual `document_id`/`ast_hash`, pero distinta identidad de nodo, estrategia o procedencia física. **Corrección:** `core/ast/registry.py` comprueba la firma semántica al registrar, escribe un temporal completo y publica mediante `os.link` sin sobrescritura atómica; reintento con contenido idéntico = idempotente; archivo preexistente diferente/corrupto = rechazo y sin mutación de caché. `tests/integration/test_pppr_g2_semantic_registry.py` falsifica conflicto con hash semántico igual, idempotencia y carreras de dos escritores independientes, además de rechazo de artefacto inválido.

**Suficiencia real del recibo de generación:** `infra/db/control_repo.py` y `infra/db/schema_queue.sql` agregan `generation_binding_sha256` a recibos nuevos y migración SQLite aditiva; la vinculación local combina documento, AST, manifiesto, unidad, tarea, ejecución, checksum de respuesta, `generation_sha256` y `root_config_sha256`. El consumidor recalcula esa vinculación en replay productivo: cambio **solo** de `generation_sha256` manteniendo idéntica la configuración raíz y la respuesta ⇒ `PPPR_G2_GENERATION_RECEIPT_BINDING_DRIFT`; recibo sin vinculación bajo validación productiva ⇒ `PPPR_G2_REPLAY_GENERATION_UNVERIFIED`. Falsadores `tests/integration/test_g3_b4_1_worker_coexistence.py` y CLI offline. **Límite de autoridad:** el consumidor comprueba coherencia durable local y configuración raíz, **NO recalcula la preimagen efectiva de prompt/modelo/contexto del productor** ni acredita una firma de autenticidad de tercero; `SyncProviderBridge` sigue siendo el productor de la identidad por propósito. No se convierte el hash semántico en hash universal, no se habilita caché LLM ni se reclaman garantías científicas.

**Evidencia técnica correctiva:** [CI técnica #44975050240](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44975050240) **completed/SUCCESS** para HEAD exacto `69d56ef349fef9443e6dc1fe9390027401c219f9`, jobs Static Analysis, Unit Test Suite e Integration Test Suite **3/3 SUCCESS**, Pyright **0 errores / 0 advertencias / 0 informaciones**, import-linter PASS, unitarios **288 PASS / 1277 deselected / 3 warnings**, integración focal **95 PASS / 1470 deselected**, suite `pytest -m "not e2e"` **1541 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar ejecuciones separadas. Este resultado acredita **código y falsadores del SHA citado**, no la CI posterior del commit exclusivamente documental. Wave 2.2 **TECHNICAL_CI_VERIFIED_PRE_BOARD**, 3/3 Tasks implementadas pero `IN_PROGRESS/BOARD_PENDING` hasta aceptación formal y autorización de integración. G2 `IN_PROGRESS`, Exit Review `NOT_RUN`, 14 GAP P1 históricos `OPEN`, sin nuevos DF/GF ficticios ni certificación científica, `PRODUCT_READINESS=NOT_CERTIFIED`; sin egress, gastos, host, G3, main ni PR #66.

**Checkpoint W1.2 (2026-11-21):** los resultados de la verificación de Tasks se conservan en Execution Plan §2.1.2 y [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34). Sobre el mismo HEAD `67affe9ffa9d68b09788c5cc6fdff6dc3467b546`: [GitHub CI #44935045055](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44935045055) `SUCCESS`, Pyright 0 errores/0 advertencias, import-linter PASS, `not e2e` 1454 PASS, 4 SKIPPED, 20 E2E deselected; [CV #44935045265](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44935045265) `FAIL / BASELINE_INTEGRITY_FAILURE (exit 3)` por 15 PDF faltantes. [Resolución excepcional G1 ratificada por owner, comentario 7069421655](https://github.com/RDsanchez-git/translator_pdf/issues/34#issuecomment-7069421655) **solo** para §2.1.3(3). El fallo CV es previo y queda visible; la revisión W1.2 no creó nuevo DF/GF ni reclasificó el issue #34. **Esta nota NO es una entrada forense de DF/GF ni un Gate Exit Review realizado.**

**Decisión específica del owner y dictamen ajustado favorable del Architecture Board (2026-11-21):** para **PPPR exclusivamente**, se autoriza integrar este esqueleto `IN_PROGRESS` **antes de cerrar la fase** y versionar incrementalmente su evidencia **desde el descubrimiento de cada DF/GF y durante las Tasks/Gate Exit Reviews**, conforme a §1.3. El owner autorizó explícitamente el merge documental del PR #81 a `pdf-pdf-product-readiness`, y el Board emitió dictamen ajustado **favorable a esa integración**. Es una **autorización puntual de calendario de publicación** frente a `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §6.7, **sin modificar su regla general ni extenderla a otras fases**. Cada entrada validada sigue inmutable; el documento entero será `FROZEN` **solo al cierre formal de PPPR**. La publicación temprana no afirma revisión ejecutada, resultado científico ni autoriza comenzar G1.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-11-21 | Esqueleto metodológico PPPR; 0 entradas forenses, 6 Gates NOT_RUN; preparado para construcción incremental sin publicar evidencia ficticia. |
| 0.1.1 | 2026-11-21 | Precisión editorial del Board: captura temprana de observaciones al detectar DF/GF y consolidación forense inmutable durante Gate Exit Review. |
| 0.1.2 | 2026-11-21 | Formaliza autorización particular del owner y dictamen ajustado favorable del Board para publicación/versionado incremental temprano de PPPR, sin alterar §6.7, inmutabilidad ni FROZEN final. |
| 0.1.3 | 2026-11-21 | Checkpoint W1.1: baseline y trazabilidad comprobados en Execution Plan §2.1.1; sin DF/GF ni Exit Review nuevos; no se inventan entradas forenses. |
| 0.1.4 | 2026-11-21 | Checkpoint W1.2: CI técnica y CV científica con veredictos reales separados, ratificación acotada del owner y dependencias pendientes. Sin nuevo DF/GF ni Exit Review; la prueba de Tasks sigue en Execution Plan. |
| 0.1.5 | 2026-11-21 | Primer Gate Exit Review real: G1 revisado con 4 Tasks DONE y criterios documentales satisfechos; CI del HEAD 718a81a aún IN_PROGRESS durante revisión, por tanto G1 BLOCKED/PENDING_CI. CV FAIL/DEFERRED visible, 0 DF/GF nuevos. Sin análisis forense de findings inexistentes ni FROZEN. |
| 0.1.6 | 2026-11-21 | Addendum del Exit Review G1: CI técnica #44951655134 SUCCESS para HEAD evaluado, levantando bloqueo transitorio; PASS G1 acreditado. CV científica continúa FAIL/DEFERRED; no se generan hallazgos DF/GF nuevos ni certificación. |
| 0.1.7 | 2026-11-21 | Checkpoint de Wave2.1: procedencia física, geometría y muestreo verificados en GitHub CI #44955114310 y falsadores sintéticos; sin Exit Review G2 ni DF/GF nuevos fuera de GAP-0.2-01/02 históricos, sin certificación científica. Se actualiza con código/tests en el mismo PR #85. |

| 0.1.8 | 2026-11-21 | Addendum Board sobre PR #85 y falsadores OCR/SQLite, persistencia y consumidor conservador; CI del nuevo HEAD pendiente, R9/R10 NO nuevamente VERIFIED. Sin Gate2 Exit Review, cierre GAP ni certificación científica. |
| 0.1.9 | 2026-11-21 | Revalidación técnica CI #44961625659 SUCCESS en commit `0dc091fa7f1b`, nuevos falsadores OCR persistencia y consumidor PASS. Diez reglas CI_VERIFIED, aceptación Board pendiente; sin Gate2 Exit Review ni CV científica certificada. |
| 0.1.10 | 2026-11-21 | Dictamen Board favorable a integración con CI #44962322464 SUCCESS en HEAD `2535860…`, owner autoriza merge condicionado a sincronización de los tres documentos y CI del nuevo HEAD. Nada de Gate2 Exit Review ni CV científica PASS. |
| 0.1.11 | 2026-11-21 | Checkpoint técnico W2.2/PR #86: AST semántico V2, generación EN→ES y consumidores/replay. CI #44972570392 SUCCESS sobre `a6ce8eb8…`, test interprocesos y nuevo HEAD aún pendientes; sin Board/merge, G2 Exit Review ni validación científica. |
| 0.1.12 | 2026-11-21 | Addendum Board PR #86: no-clobber AST y vínculo local de integridad del recibo, con falsadores de concurrencia, reinicio y alteración de generación. CI #44975050240 SUCCESS sobre `69d56ef3…`, 3 jobs verdes, 288 unit y 1541 suite; Board/merge pendientes; sin Exit Review G2 ni certificación científica. |
| 0.1.13 | 2026-11-21 | Gate2 Exit Review REALIZADO en código SHA `ac156be2…`, CI #44977644736 SUCCESS (3/3 jobs, 289 unit PASS, 1542 suite técnica PASS); Board tercera revisión FAVORABLE, 6 Tasks y 30 reglas G2 con evidencia, 4/4 criterios técnicos PASS. Owner autoriza merge PR86 tras este registro; integración pendiente. 14 GAP P1 OPEN, CV sin certificar, G3 NOT_RUN. |

| 0.1.14 | 2026-11-22 | Post-merge PR86: commit `7842bb3c69c2baf792cb9cb3acca088462445d54`, CI pre-merge #44978406678 y post-merge #44979093690 SUCCESS; G2 COMPLETED/PASS, 6/6 Tasks, 30/30 reglas y 4/4 Exit Criteria. Acta pre-merge inalterada; 14 GAP P1 OPEN, CV FAIL/DEFERRED, Product Readiness no certificado, G3 NOT_RUN. |
| 0.1.15 | 2026-11-22 | Checkpoint W3.1 PR90: base `6ab1800…` tras merges PR88/PR89, CI técnica base #45090693364 SUCCESS; tests offline de autoridad, UNKNOWN y alarma introducidos pero aún NO verificados en CI del PR90. Sin G3 Exit Review ni cierre de reglas/Tasks. |
| 0.1.16 | 2026-11-22 | Board sobre PR90 3c5e366… FAVORABLE CON CORRECCIONES/NO MERGE, observaciones H1 alta, H2 alta, H3 media; correcciones de cuota NO_START, alarma independiente, nueva prueba PRAGMA y matriz de 24 reglas F18-04/05 como candidatos con gaps. CI del SHA final y segunda revisión Board pendientes, sin reglas/Tasks G3 DONE. |
| 0.1.17 | 2026-11-22 | Evidencia ejecutada [CI #45100465237](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45100465237) SUCCESS sobre `4340538…`: Pyright 0/0/0, 4/4 import-linter, 289 unit PASS, suite técnica 1558 PASS/4 skipped/20 E2E excluidos (2 warnings pytest). H2 §7.H.1 mapea 24 normas sin acreditar todos sus falsadores; nuevos tests de reconstrucción derivada y auditoría UNKNOWN ausente en `0d528b1…` CI_PENDING. Ningún nuevo Exit Review/Task G3 DONE. |
| 0.1.18 | 2026-11-22 | Board segunda revisión PR90 verifica [CI #45101231199](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45101231199) SUCCESS sobre `6e83816…`: Pyright 0/0, import-linter 4/4, 289 unit, 95 integración focal, suite técnica 1560 PASS /4 skipped/20 excluidos. H1/H3 resueltos. H2 pide fallo negativo de ruta de retry excepcional; test añadido `ff531d23…` CI final pendiente y dictamen normativo condicional Board pendiente, sin G3 Exit Review. |
| 0.1.19 | 2026-11-22 | [CI #45102292492](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45102292492) completed SUCCESS sobre HEAD `9ea325f752e0a30fdf66469a9bde60456a702cb9` (3/3 jobs; Pyright 0/0/0, import-linter 4/4, 289 unit, 95 integración focal y `not e2e` 1561 PASS /4 skipped/20 excluidos, 2 warnings). Falsador de inalcanzabilidad por APIs locales incluido y ejecutado. H2 parcial, su dictamen condicional aún pendiente de Board; no Tasks G3 DONE ni merge. |
| 0.1.20 | 2026-11-23 | Board ratifica [CI #45103595023](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45103595023) SUCCESS `68dec1f…`, H1/H3 cerrados y aplicabilidad de F18-03/F18-05 condicional en rutas locales. F18-05 R1/R2/R10/R13/R15 siguen PARCIAL. Dos falsadores adicionales en `518e2a0…` verifican formatter+filtro reales y reemisión UNKNOWN desde SQLite tras pérdida de logs; CI nuevo HEAD pendiente, sin Tasks/Gate Exit Review DONE. |
| 0.1.21 | 2026-11-23 | [CI #45105007281](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45105007281) final SUCCESS en `a49cd95285ae874dddeaea26011f391e741fa3b1`: Pyright 0/0/0, import-linter 4/4, unit 289, integración focal 95, `not e2e` 1563 PASS/4 skipped/20 E2E excluidos, dos warnings. Cuatro reglas F18-05 Board acreditables localmente; R10 detección local sí, pérdida de entrega externa no. F18-04 R1–R16 testigos revisados sin auto-PASS. Propuesta scope R10 a Board; no código, no DONE ni merge. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_PPPR_MASTER.md FROZEN
    ↓
NADR-FPPPR-01/02/03/04 FROZEN
    + reglas F17-BIS/F18 ratificadas solo por estado, sujeto y frontera
    ↓
PHASE_PPPR_EXECUTION_PLAN.md v0.5.0 APPROVED / LIVING
    ↓
ESTE EVIDENCE LOG (evidencia, no norma)
```

Rigen `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §§3.5.2, 6.5–6.7 y `6_METH_EXIT_REVIEW_EVIDENCE_LOG_FASE_{X}.md`. La autoridad de un NADR no se reescribe mediante un finding.

### 0.2 Principio rector del Exit Review PPPR

> ¿La evidencia concreta del código, documentos y comportamiento de la ruta única PDF→PDF demuestra que el hallazgo viola una obligación vigente de este Gate, que es una hipótesis sin acreditar o que está fuera de alcance y requiere una decisión de derivación, **sin desviar la implementación del Execution Plan aprobado**?

Distinguir siempre `OBSERVADO / NO VERIFICADO / NO-GAP / DECISIÓN COMPETENTE`. Los falsadores con estado `NOT_RUN` nunca son PASS.

### 0.3 Reglas transversales aplicables

- Evidencia forense por **Gate y DF/GF**; referenciar fuente, ruta, líneas pertinentes y SHA/fecha de la observación.
- `NADR-FPPPR-01` gobierna autoridad científica; PPPR-02 representación G5; PPPR-03 inferencia G3; PPPR-04 procedencia física. DC-04 identidad por consumidor, DC-07 autoridad y recuperación; F17-BIS/F18 únicamente para reglas ratificadas del sujeto PPPR.
- Un testigo técnico con fake, un estado `DONE` o un PDF con cabecera `%PDF-` no demuestra certificación científica ni un resultado real de proveedor.
- Cada finding debe distinguir: (a) gap objetivo confirmado, (b) hipótesis pendiente, (c) comportamiento correcto/no-gap. **No inventar nuevos GAP-ID P1** ni tratar los históricos como findings nuevos por defecto.
- El análisis y clasificación con decisiones, batches y resultados vive **en el Findings Register**; aquí se conserva únicamente la **evidencia que fundamenta cada clasificación**.
- El Gate Exit Review realizado puede concluir `FAIL/BLOCKED`. Un dictamen `PRODUCT_READINESS=PASS` necesita autoridad, referencias y criterios científicos aprobados y resultados positivos en las tres dimensiones; no se deriva de la mera revisión.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Identificador | Uso |
|---|---|
| `DF-{XX}` | Finding técnico nuevo, asignado en el registro único PPPR |
| `GF-{XX}` | Finding de gobernanza que requiere autoridad competente |
| `H-{XX}-{X}` | Hallazgo derivado de otro DF |
| `GAP-0.x-XX` | Referencia a la baseline histórica PPPR.0.9; no crear DF automático |
| `E-0.x-XXX` | Referencia histórica a evidencia forense de HITOs; no nueva prueba |

El **mismo ID** se utiliza en la Wave del Execution Plan, la entrada forense de este Log y la clasificación/resolución del Findings Register.

### 1.2 Estados de clasificación

| Estado canónico | Significado en la evaluación |
|---|---|
| `PENDING_REVIEW` | Hallazgo aún no analizado en Exit Review |
| `REVIEW_REQUIRED` | Insuficiencia de evidencia para decisión final |
| `IMPLEMENTATION_REQUIRED` | Defecto demostrado que requiere trabajo autorizado |
| `RESOLVED` y variantes | Corrección acreditada con implementación y validación |
| `CLOSED (NAR)` | No-gap o hipótesis descartada con justificación verificable |
| `ACCEPTED_LIMITATION` | Limitación aceptada por autoridad correspondiente |
| `RECLASSIFIED_FUTURE_PHASE` | Derivación con alcance, destino y decisión explícita |

Las variantes de `RESOLVED`, `DEFERRED — FASE {X}` y otros estados admisibles se encuentran en `6_METH_DEFERRED_FINDINGS_REGISTER_FASE_{X}.md`. La clasificación final operativa se registra **en el Findings Register**, no se duplica como una segunda fuente de verdad.

### 1.3 Reglas de evidencia

Para cada entrada futura, registrar como mínimo: origen Gate/Wave/Task, texto exacto del hallazgo y cambios de formulación, código/documentos inspeccionados con SHAs y referencias, hecho observado, hipótesis, condiciones negativas verificadas, impacto sobre PPPR, regla aplicable, alcance/gap/no-gap, autoridad que clasifica, límites del resultado y vínculo al Findings Register. No inventar números de tests, hechos de proveedor, autorizaciones o permisos.

**Momento 1 — descubrimiento del hallazgo (captura inmediata, todavía no validada en Exit Review).** Cuando se detecta un DF/GF durante una Task, asignar su ID estable en el Findings Register, registrar allí su estado `PENDING_REVIEW` y **capturar de inmediato en este Log** la observación original, fecha, Gate/Wave/Task, archivos y SHAs, testigos disponibles, condiciones de reproducción y límites de verificación. Distinguir expresamente `OBSERVADO`, `HIPÓTESIS` y `NO_VERIFICADO`. Esta captura inicial no equivale a una clasificación final, evidencia completa, Gate Exit Review ejecutado ni autorización de trabajo nuevo.

**Momento 2 — Gate Exit Review (validación y cierre de la entrada forense).** Durante la revisión real del Gate, completar y contrastar los apartados §2.N, determinar gap/no-gap/limitación y regla aplicable, vincular la **decisión** al Findings Register y registrar HEAD/fecha/autoridad de la revisión. **A partir de su validación, la entrada forense queda inmutable** frente a los batches de resolución. Si aparece información posterior, conservar la evidencia previa y añadir **complemento fechado y vinculado al mismo ID**, mientras que la reclasificación y sus resultados se documentan en el Findings Register. **No posponer la captura inicial hasta el cierre del Gate**.

### 1.4 Árbol de decisión del Gate Exit Review

```text
¿Existe el hallazgo? ─ NO ─► CLOSED (NAR) con prueba
           │
           SÍ
           ▼
¿Se puede resolver dentro del Gate? ─ SÍ ─► registrar evidencia;
           │                              resolución solo por batch autorizado
           NO
           ▼
¿Es técnico y pertenece al programa? ─ SÍ ─► registrar dependencia/derivación
           │
           NO
           ▼
¿Es conflicto normativo? ─ SÍ ─► GF y escalar a autoridad competente
           │
           NO
           ▼
ACCEPTED_LIMITATION / RECLASSIFIED_FUTURE_PHASE
solo con justificación, destino y autoridad; Gate BLOCKED si aplica
```

No implementar correcciones durante el Exit Review. Las decisiones de código pertenecen a Tasks/batches posteriores autorizados.

---

## 2. ESTRUCTURA POR FINDING

**Estado:** **SIN ENTRADAS DF/GF, NOT_RUN**. La verificación W1.1 documental y W1.2 técnica/autoridades está documentada por Task en Execution Plan §§2.1.1–2.1.2, con enlaces a los runs y decisión externa. La ausencia de hallazgos nuevos en ese alcance **no constituye entrada forense, `CLOSED (NAR)` ni resultado científico artificial**. Esta sección solo se amplía cuando exista un hallazgo nuevo real. No se crean apartados `2.1 DF-01` ficticios.

**Plantilla operativa de cada entrada futura (no es evidencia registrada):**

### 2.N — {DF/GF-ID} — {Título sustentado en evidencia}

| Campo | Valor a completar sobre el hallazgo real |
|---|---|
| ID | {DF/GF-XX} |
| Tipo | {Deferred / Governance / Derivado} |
| Estado durante revisión | {PENDING_REVIEW / clasificación fundamentada} |
| Origen | {Gate, Wave, Task, fecha, revisión real} |
| Gate de destino original | {Gate N} |
| Estado previo | {Estado anterior o no aplica} |
| Prioridad | {Baja / Media / Alta / Critical / N/A} |
| ¿Requiere implementación? | {Sí / No / pendiente de análisis} |
| ¿Bloquea el Exit Criteria de PPPR? | {Sí / No / condicional; por qué} |
| Reference al Register | {Entrada DF/GF con decisión y autoridad} |

#### 2.N.1 Texto original del DF/GF
Conservar literalmente la observación original registrada en la Wave/Task; si no está disponible, indicarlo como limitación, **no inventar una cita**.

#### 2.N.2 Reformulación corregida (si aplica)
Documentar qué se corrigió conceptualmente, con versión/fecha y sin borrar el texto original.

#### 2.N.3 Archivos y documentos auditados

| Archivo/documento/contrato | SHA y rango | Evidencia extraída o ausencia comprobada | Estado de verificación |
|---|---|---|---|
| {Fuente real, no placeholder como evidencia} | {SHA/rango} | {Hecho observable} | {CONFIRMADO / NO_VERIFICADO} |

#### 2.N.4 Análisis
Indicar existencia, implicaciones funcionales, consumidor concreto, regla exacta, reproducción, límite de observación y diferencia entre fallo normativo, brecha técnica e hipótesis.

#### 2.N.5 Gaps objetivos confirmados (si aplica)

| Hecho/gap | Evidencia localizable | Impacto real | Relación con GAP-ID histórico |
|---|---|---|---|
| {Solo tras acreditación} | {Archivo/PR/testigo} | {Acreditado} | {Vínculo opcional; no duplicar ID} |

#### 2.N.6 Lo que NO es un gap
Registrar comportamientos correctos por diseño, escenarios fuera de alcance o hipótesis descartadas, **solo si se contrastaron**.

#### 2.N.7 Impacto en la meta PPPR

| Dimensión | Afectación acreditada | Justificación |
|---|---|---|
| Identidad/procedencia | {Sí/No/Indeterminada} | {Evidencia} |
| Seguridad del efecto/recuperación | {Sí/No/Indeterminada} | {Evidencia} |
| Reconstrucción/estructura/STEM | {Sí/No/Indeterminada} | {Evidencia} |
| Conformidad científica PDF final | {Sí/No/Indeterminada} | {Sujeto/oráculo/permisos; no presumir ciencia} |
| Gate/Task/Readiness | {PASS/FAIL/BLOCKED/NOT_RUN según corresponda} | {Criterio exacto} |

#### 2.N.8 Sub-acciones identificadas (si aplica)
Registrar propuestas de corrección o tests específicos como posibles componentes de un batch, **sin considerarlas automáticamente Tasks nuevas ni trabajo autorizado**.

#### 2.N.9 Clasificación consolidada
Registrar hechos confirmados, si existe conflicto normativo o técnico y la **referencia a la decisión clasificada en el Findings Register**. No replicar allí una segunda decisión incompatible.

#### 2.N.10 Regla aplicada
Referencia exacta `NADR/ADR/ENGINEERING_PRINCIPLES §/Rn` y explicación de su correspondencia con el sujeto observado; si requiere una nueva autoridad, crear/escalar GF antes de introducir obligación.

**Protocolo de inmutabilidad:** una entrada 2.N firmada por un Gate Exit Review con SHA/fecha **no se corrige silenciosamente**. Información nueva se agrega como apartado de seguimiento vinculado al mismo ID, sin falsificar el resultado anterior.

---

## 3. GATE EXIT REVIEW SUMMARY

**Checkpoint W3.1/PR90 2026-11-22, NO Gate3 Exit Review:** se modifica la autoridad previa al I/O externo tras espera del semáforo, se separa CAS de no-inicio acreditado de UNKNOWN persistente y se agrega alarma de reconciliación configurable sobre SQLite. Falsadores offline de expiración, cambio de owner, corrupción de audit, TTL, reinicio y no-retry introducidos en la rama. **CI final/Board pendientes**; ninguna Task o regla G3 DONE y no se afirma certificación científica ni se habilitan efectos comerciales.

**Estado del Gate 1 (2026-11-21):** Exit Review REALIZADO y, luego del complemento de CI del SHA evaluado en SUCCESS, **G1 PASS/COMPLETED**. La constatación inicial `BLOCKED_PENDING_CI_HEAD` permanece como evidencia temporal en §3.1, sin alteración retroactiva. G2–G6 `NOT_RUN`. **0 hallazgos DF/GF nuevos** y ningún certificado científico; el registro por finding §2 permanece vacío.

| Gate del Execution Plan | Revisión real | Evidencia por DF/GF | Decisión/veredicto |
|---|---|---|---|
| G1 — Baseline y autoridad | **REALIZADO 2026-11-21 + addendum de CI posterior**; 4/4 Tasks DONE | **0 DF/GF nuevos**, sin §2 ficticio. Referencias de criterios en Plan §2.1.4 y CI/CV en §3.1 | **G1 PASS/COMPLETED**; CI del HEAD SUCCESS, CV científica FAIL/DEFERRED |
| G2 — Procedencia e identidad | **Exit Review REALIZADO 2026-11-21**, 6 Tasks, 30 reglas G2, CI #44977644736 SUCCESS; **PR86 MERGED 2026-11-22**, CI post-merge SUCCESS | **0 DF/GF nuevos en alcance**; H1/H2 resueltos, 14 GAP P1 históricos OPEN | **4/4 Exit Criteria PASS y G2 COMPLETED/PASS tras verificación de integración** |
| G3 — Seguridad de efectos e inferencia | NOT_RUN | No registrada | PENDING |
| G4 — Reconstrucción G5/PDF | NOT_RUN | No registrada | PENDING |
| G5 — Host e integración E2E | NOT_RUN | No registrada | PENDING |
| G6 — Ciencia y cierre | NOT_RUN | No registrada | PENDING |

### 3.1 Gate 1 Exit Review (2026-11-21) — REVISIÓN REALIZADA, SIN PASS

**Baseline del review:** `pdf-pdf-product-readiness@718a81a7816ef91710b3a86b00cc4326b0b18262`. CI técnica de referencia anterior `67affe9ffa9d68b09788c5cc6fdff6dc3467b546`, diferenciada del HEAD sujeto al review. **Objeto real:** conformidad de las Tasks 1.1.1–1.2.2 y de los cuatro Exit Criteria de G1, sin pretensión de validar G2–G6 o ciencia EN→ES.

**Evidencia y límites observados:**

| Criterio/control | Evidencia verificable | Alcance y decisión |
|---|---|---|
| G1 §2.1.3(1) | `main@1d21cfe9…`; gobernanza `718a81a…`; PR #82 y PR #83 documentales; raíz CLI/OCR/G3/G5 en fuentes versionadas (§2.1.1 del plan) | **PASS documental**, no E2E ni código nuevo |
| G1 §2.1.3(2) | 40/40 reglas PPPR con responsable único; clasificación histórica 104 = 79 A/25 C; 14/14 GAP-ID P1 de HITO PPPR.0.9 conservados | **PASS de trazabilidad**, no reparación de los GAP |
| G1 §2.1.3(3) | [Ratificación del owner `PPPR-G1-CI-SCOPE-01`](https://github.com/RDsanchez-git/translator_pdf/issues/34#issuecomment-7069421655); [CI #44935045055](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44935045055) anterior SUCCESS; [CI del HEAD #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) **IN_PROGRESS** al revisar (análisis estático SUCCESS, suite aún no terminada) | **PENDING_CI_HEAD**, no atribuir PASS de ejecución anterior al HEAD actual |
| CV científica separada | [CV #44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) **FAIL**, 15 PDFs no disponibles; ámbito de excepción ratificada por owner solo G1 | **FAIL/DEFERRED, nunca PASS científico** |
| G1 §2.1.3(4) | Matriz §2.1.2 del plan, solicitante/autoridad/condición/consumidor; permisos externos no concedidos | **PASS documental**; cada Gate consumidor queda condicionado |
| Nuevos DF/GF | No apareció observación nueva susceptible de clasificar en este scope; issue #34 y 14 GAP P1 se mantienen como antecedentes | **0 DF/GF nuevos**, no inventar `CLOSED (NAR)` ni un falso positivo |
| Gate resultante | 4/4 Tasks DONE; CI de HEAD sin veredicto final al momento de revisión | **REVIEW_REALIZADO / GATE BLOCKED_PENDING_CI**, G2 `PENDING` |

**Matriz de hallazgos del Exit Review:** sin filas DF/GF nuevos porque **ninguno fue identificado en el alcance revisado**. No se emite una clasificación `CLOSED (NAR)` para un hallazgo inexistente ni un GF por el diferimiento históricamente autorizado. El Findings Register §2.1 contiene **la decisión operativa y el resumen**, mientras este apartado conserva alcance y referencias de evidencia. Si la CI actual concluye con fallo nuevo, capturar inmediatamente el hallazgo, asignar ID y agregar su evidencia §2.N antes de clasificar.

**Dictamen fechado:** Gate 1 Exit Review **realizado** el 2026-11-21. **G1 permanece IN_PROGRESS / BLOCKED_PENDING_CI_HEAD, sin PASS**. Al recibir CI íntegra del HEAD actual, nueva evaluación fechada del control pendiente, sin borrar este testigo ni inferir certificación científica.

**Addendum posterior al dictamen inicial (2026-11-21, resultado definitivo):** [GitHub CI #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) del HEAD exacto `718a81a7816ef91710b3a86b00cc4326b0b18262` resultó **SUCCESS**, los tres jobs de análisis estático/units/integration completaron `success`, incluyendo suite completa técnica sin E2E científico. Con [resolución metodológica limitada G1](https://github.com/RDsanchez-git/translator_pdf/issues/34#issuecomment-7069421655), quedan acreditados los cuatro Exit Criteria de G1. **Veredicto posterior: G1=PASS/COMPLETED, el 2026-11-21**. La evidencia previa de CI en progreso y bloqueo queda arriba, íntegra. CV científica [#44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) sigue **FAIL/DEFERRED** por corpus ausente y no constituye PASS ni certificación. **Nuevos DF/GF 0**, issue #34 y los 14 GAP P1 siguen preexistentes, G2 no iniciado.

**Estructura de revisiones de otros Gates:** al ejecutar un Gate posterior, agregar `### 3.N Gate N Exit Review (fecha, HEAD, sujeto, veredicto)` y las referencias individuales §2.N de cualquier DF/GF efectivamente identificado. Una revisión realizada sin PASS no equivale a cierre del Gate.

---

### 3.2 Gate 2 Exit Review (2026-11-21) — REALIZADO / CRITERIOS PASS

**Objeto acreditado:** Gate2/Wave2.1 PR #85 [integrado](https://github.com/RDsanchez-git/translator_pdf/pull/85), ten rules `NADR-FPPPR-04` para procedencia física, geometría y muestreo; Gate2/Wave2.2 PR #86, 20 reglas históricas clase A con dueño G2 verificadas por falsadores concretos (Execution Plan §7.H), `AST_SEMANTIC_PRODUCT_V2`, `PPPRGenerationIdentityV1` y consumidores durables.

**Revisión Board y correcciones:** tercera revisión favorable sobre `0d42ad7f30a9576fa6bec05d0fe336a95de16cc7` con [CI #44975791556](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44975791556) SUCCESS (288 PASS unitarios/1541 suite). H1: `core/ast/registry.py` no sustituye el artefacto bajo misma clave semántica, falsadores de reintento/concurrencia/corrupción en `tests/integration/test_pppr_g2_semantic_registry.py`. H2: `infra/db/control_repo.py` conserva y comprueba `generation_binding_sha256`, falsador de generación alterada con `root_config_sha256` constante en `tests/integration/test_g3_b4_1_worker_coexistence.py`. **Límite:** integrity local no equivale a recalcular el prompt/modelo/contexto del productor ni a acreditar autenticidad externa.

**Revalidación complementaria de reglas históricas (solo tests):** `tests/unit/test_pppr_g2_semantic_identity.py` prueba que IDs de chunk/trace no contaminan hash semántico; `tests/unit/test_pppr_g2_generation_identity.py` verifica la identidad EN→ES en procesos Python independientes bajo distinto `PYTHONHASHSEED`. [CI #44977644736](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44977644736) **completed/SUCCESS** sobre `ac156be223d2db952e968352bc1ea38c3531186e`: static analysis Pyright **0 errors/0 warnings/0 informations**, import-linter 4/4, **289 unit PASS / 1277 deselected**, integración focal **95 PASS / 1471 deselected**, suite completa `not e2e` **1542 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar estas ejecuciones independientes.

| Exit Criterion fijo §2.2.3 | Evidencia y veredicto |
|---|---|
| (1) Procedencia física, geometría y sampler | **PASS:** `PhysicalRegion`, dimensiones acreditadas y unidad página–región; PDF sintético PyMuPDF, muestras mixtas y límites sin sobrecobertura; PR85 CI y regresión PR86 |
| (2) Falsadores GAP previstos; jerarquía y Unicode STEM | **PASS técnico:** GAP-0.2-01/02 y GAP-0.3-01/02 falsadores ejecutados; H1/H2/H3/UNKNOWN, NFC conservador, símbolos STEM, dos procesos Python; no declarar cierre de los GAP P1 |
| (3) Identidad real por consumidor | **PASS en ruta conectada:** ChunkPlan, ASTRegistry no-clobber, snapshots, OCR/SQLite, recibos G3, replay y ensamblado; identidad semántica, generación, artefacto y autoridad operacional separadas |
| (4) Pyright/regresión | **PASS:** [CI #44977644736](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44977644736) 3/3 jobs SUCCESS, Pyright 0/0, import-linter 4/4, 1542 PASS suite técnica; CV científica permanece FAIL/DEFERRED |

**Acta de cierre de la revisión:** `REVIEW_REALIZADO / G2_EXIT_CRITERIA_PASS_4_OF_4 / AUTHORIZED_MERGE_PENDING`. Seis Tasks del Gate con implementación/pruebas acreditadas y favorables al Board. El owner autorizó específicamente el merge PR #86 **después de actualizar esta acta**; al instante de esta anotación la integración/HEAD de la rama destino aún no están verificados. `G2 COMPLETED` se declarará solo tras esa comprobación. **0 hallazgos nuevos DF/GF sustentados dentro del ámbito de revisión**: las observaciones técnicas del Board se corrigieron antes de merge y no se duplican como IDs ficticios. Los **14 GAP P1 históricos siguen OPEN** y requieren sus decisiones forenses propias. CV científica FAIL/DEFERRED (15 PDFs privados no presentes), `PRODUCT_READINESS=NOT_CERTIFIED`; alcance PyMuPDF/offline, NO Docling, egress, gasto, host o `main`. La excepción G1 no se extiende a G2 ni se inventa evidencia del corpus. G3 NOT_RUN hasta completar publicación y DoR.

**CI del HEAD documental posterior:** verificación adicional pendiente; no extrapolar el run `ac156be223d2db952e968352bc1ea38c3531186e` al commit de documentación.

**Addendum forense post-merge (2026-11-22; NO sustituye el Exit Review original):** el acta de 2026-11-21 registra correctamente que el merge todavía estaba pendiente. Después, [PR #86](https://github.com/RDsanchez-git/translator_pdf/pull/86) fue MERGED 2026-11-22 03:06:19 UTC; la rama `pdf-pdf-product-readiness` quedó en `7842bb3c69c2baf792cb9cb3acca088462445d54`. El SHA pre-merge `807dd45358dd407d3e0a07682a4088c935b9a96f` superó [CI #44978406678](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44978406678); el merge superó [CI #44979093690](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44979093690) SUCCESS sobre `7842bb3c69c2baf792cb9cb3acca088462445d54` (3/3 jobs, Pyright 0/0/0, import-linter 4/4, 289 unitarios PASS, 95 integración focal PASS y suite `not e2e` 1542 PASS / 4 SKIPPED / 20 E2E excluidos; no sumar suites). Los tres documentos fueron los únicos archivos modificados después del SHA de código revisado `ac156be2…`. Con esa evidencia **G2 COMPLETED/PASS** (sin segunda revisión ni nuevas reglas). [CV #44979093692](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44979093692) terminó FAIL/DEFERRED por `BASELINE_INTEGRITY_FAILURE` y 15 PDFs canónicos ausentes en runner; no es evaluación científica positiva ni negativa. `PRODUCT_READINESS=NOT_CERTIFIED`; 14 GAP P1 OPEN; G3–G6 NOT_RUN; ningún permiso nuevo de egress, proveedor o gasto.

**Board PR #90 — revisión 2026-11-22 sobre `3c5e366e6b948c20f37d82334787826b4c4fb456`: FAVORABLE CON CORRECCIONES / NO MERGE.** H1 HIGH: `PermanentQuotaRejection` / `QuotaTimeoutError` provenían del rate limiter antes de `_underlying.translate` y caían en UNKNOWN genérico; el PR añade catch específico en `runtime/engine.py` y CAS `mark_g3_proven_no_start(permanent=True/False)`, con pruebas de cero I/O y reintento acotado. H3 MEDIUM: sweeps previos ya no bloquean la alarma; `_run_sweep_cycle` aísla excepciones y deduplica por `(task_id,execution_id)` durante TTL en memoria, conservando SQLite como autoridad. H2 HIGH: matriz individual de 24 reglas propietarias de Task 3.1.3, sin presumir cobertura universal. **Estado: CODE_PROPOSED / CI DEL SHA FINAL PENDIENTE, BOARD_REVIEW_PENDING, ningún DONE nuevo**.

**Fuente de evidencia por regla:** Execution Plan §7.H.1; los testigos listados allí se examinaron como candidatos y no se infiere `CI_VERIFIED` por la mera presencia de pruebas. El nuevo test `test_pppr_g3_effective_sqlite_wal_normal_busy_timeout` verifica PRAGMAs efectivos únicamente cuando la CI del HEAD que lo contiene pase. La tolerancia metodológica de G1 NO se aplica a G3. La CV científica continúa FAIL/DEFERRED y no está cubierta por estos tests offline.

**Checkpoint CI y límites adicionales H2 (2026-11-22; NO es Gate3 Exit Review):** [CI #45100465237](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45100465237) completó SUCCESS para código y documentos en `4340538aa78438c4c61b636d15c872dbaa4daee0`: 3/3 jobs; Pyright 0 errores/0 advertencias/0 informaciones; import-linter 4/4; unit 289 PASS y suite `not e2e` 1558 PASS /4 SKIPPED /20 E2E deselected /2 warnings. La suite focal de 95 integración PASS es un subconjunto y NO se suma. El SHA posterior `0d528b1…` agrega **dos falsadores nuevos offline**: reconstrucción del conjunto de proyecciones derivadas tras borrar proyecciones y marcador, usando receipts y plan inalterados, y reexposición de UNKNOWN aun cuando su audit metadata falta, con persistencia del estado tras reinicio del objeto daemon. No garantiza reparación automática de proyección corrupta, durabilidad ante pérdida eléctrica ni telemetría global completa; la **CI del SHA posterior queda pendiente**. No se atribuye PASS a reglas F18-05 condicionales de retry excepcional sin ese camino autorizado. Sin nuevos DF/GF inventados ni cierre Wave 3.1.

**Dictamen de aplicabilidad propuesto para segunda decisión del Board — PR90 / H2 (2026-11-22; no cambia NADR FROZEN):**
- **PROHIBITED PATH / prueba negativa en alcance:** `NADR-F18-03 §5.3 R13` y `R15` (ninguna vía productiva autorizada de retry de `G3_EXTERNAL_UNKNOWN`); test `test_pppr_g3_unknown_blocks_all_authorized_local_retry_and_legacy_recovery` invoca selección, API de no-inicio, renovación, abandono, liberación, reconocimiento y reconciliación legada sobre el mismo attempt después de UNKNOWN y tras reapertura SQLite. El test prueba rechazo en **interfaces locales existentes**, no integridad frente a escrituras SQL privilegiadas arbitrarias ni una capacidad de aprobación/rematerialización comercial inexistente. Estado **TEST_EXECUTED_CI_SUCCESS / BOARD_DISPOSITION_PENDING**, no `DONE`.
- **CONDITION NOT TRIGGERED (a ratificar):** `NADR-F18-03 §5.3 R14`, `NADR-F18-05 §5.4 R11`, `NADR-F18-05 §5.5 R14` y porción de `R15` referida a decisiones excepcionales. Sin camino productivo de autorización, aceptación de riesgo, decisión o retry excepcional, no existe una decisión cuya contabilización o durabilidad pueda falsarse. Este dato no prueba cumplimiento positivo ni permite `DONE` automático. La obligación queda vinculante si se habilita esa capacidad posteriormente; su habilitación exige decisión normativa y tests de autorización, identidad, durabilidad y auditabilidad, sin excepción metodológica implícita.
- **Obligación actual independiente de condición:** `NADR-F18-05 §5.5 R15` también obliga a separar evidencia autoritativa de métricas derivadas aun sin reejecuciones excepcionales; los tests de UNKNOWN con auditoría ausente, reinicio y alertas volátiles aportan evidencia focal pero **no acreditan universalmente** todo observability-plane. `NADR-F18-04 §5.3 R9` reconstruye el **conjunto derivado ausente** desde receipts locales recuperables; no implica reparación automática de fila corrupta aislada ni supervivencia de fuentes destruidas.
- **Criterio para cierre:** confirmar en Board la suficiencia de falsadores individuales y la aplicabilidad/inalcanzabilidad **sin reclasificar automáticamente una regla con `CONDITION NOT TRIGGERED` como `DONE`**. Toda brecha que siga aplicable y sin evidencia permanece `PENDING`; no agregar proveedores, colas, oráculos o infraestructura de monitoreo artificiales.

**Board — decisión de aplicabilidad recibida (2026-11-23; sin nuevo Exit Review):** H1 y H3 RESUELTOS; `VERIFIED — PROHIBITED PATH` para NADR-F18-03 §5.3 R13 limitado a APIs locales examinadas; `CONDITION NOT TRIGGERED` para F18-03 §5.3 R14/R15 y F18-05 §5.4 R11/§5.5 R14, sin declarar PASS ficticio ni eliminar obligación futura; F18-05 §5.5 R15 **PARCIAL**. Board mantiene **NO MERGE / W3.1 IN_PROGRESS**, demanda cotejo focal de F18-05 §5.1 R1/R2, §5.3 R10 y §5.5 R13/R15 en productores/consumidores realmente conectados. No se autorizan reintentos excepcionales ni telemetría nueva.

**Auditoría focal de emisores realmente conectados (2026-11-23):** `runtime/engine.py` pone `ctx_execution_id` (identidad de intento), `ctx_task_id` (tarea lógica) y `ctx_node_id` (chunk), mientras `core/utils/telemetry.py` (`DistributedContextFilter`+`JSONFormatter`) los serializa; `apps/daemons/reconciler.py` reconstruye alarmas desde `ControlPlaneRepository.list_due_g3_unknown` (SQLite), incluyendo `document_id`, `ast_hash`, `chunk_id`, `task_id`, `execution_id`, `audit_valid`, `first_detected_at` y disposición manual. `core/metrics/metrics.py`, `core/metrics/summary.py` y sus exportadores son agregados heredados de Dispatch/FinOps; **no son lectores/autoridad de UNKNOWN en la ruta G3 inspeccionada**, ni emiten una tasa de duplicación externa en el alcance probado. Se agregan **solo dos falsadores offline** en `tests/integration/test_w06_g3_uncertain_effect_offline.py`: `test_pppr_g3_unknown_worker_json_log_correlates_attempt_to_durable_operation` y `test_pppr_g3_unknown_alarm_recovered_after_ephemeral_json_log_loss`. El primero prueba el formatter+filtro reales y la distinción `trace_id=execution_id` de identidades lógicas/científicas; el segundo descarta el buffer de logs, reinicia el daemon, verifica alarma nuevamente desde SQLite y demuestra que no cambia el attempt ni se habilita retry. **CI de estos dos tests PENDING**. Límites: no pruebas de sinks externos, reporting global, modificaciones SQL privilegiadas, gastos comerciales ni decisiones excepcionales inexistentes.

**Architecture Board — tercera revisión recibida (2026-11-23; sin review formal GitHub):** [CI #45105007281](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45105007281) SUCCESS sobre `a49cd95285ae874dddeaea26011f391e741fa3b1`: Pyright 0 errores/0 warnings/0 informations; import-linter 4/4; 289 unit PASS, 95 integración focal PASS, `not e2e` **1563 PASS, 4 SKIPPED, 20 E2E excluidos, 2 warnings pytest**. Board considera F18-05 §5.1 **R1/R2** y §5.5 **R13/R15 (porción activa)** **ACREDITABLE EN ALCANCE** en emisores/lectores locales reales, con la parte excepcional de R15 `CONDITION NOT TRIGGERED`. **R10 PARCIAL**: faltaba distinguir recuperación de UNKNOWN de detección de pérdida de entrega a un sink. Ninguna de las cuatro acreditaciones acotadas autoriza reclasificar las otras 20 normas a PASS; 3.1.3 no DONE.

**Dictamen propuesto de alcance F18-05 §5.3 R10 (Architecture Board, a ratificar; 2026-11-23):** R10 aplica efectivamente a los **datos de auditoría local conectados a G3** (SQLite `chunk_tasks.error_log`), a su consumidor `ControlPlaneRepository.list_due_g3_unknown` y al emisor de alarma `ReconcilerDaemon`. Una auditoría ausente/corrupta se identifica explícitamente como `PPPR_G3_UNKNOWN_AUDIT_CORRUPT_REQUIRES_OPERATOR`; **jamás se interpreta como cero, éxito o permiso de nuevo intento**. Ante pérdida de la salida JSON efímera, el estado UNKNOWN persiste, es recuperable y genera una nueva alarma al reiniciar el reconciliador. **No hay detección de pérdida de entrega del propio buffer/stream**: la eliminación de ese buffer fue inducida en el test, no detectada por el producto. `JSONFormatter`+`StreamHandler` publican registros, pero ningún contrato de entrega confirmada a un colector externo, ACK ni lector de logs capaz de cambiar el estado G3 aparece conectado a esta ruta examinada. **Propuesta:** `R10 LOCAL_AUDIT_GAP_DETECTION_VERIFIED / EXTERNAL_LOG_DELIVERY_UNVERIFIED / SCOPE_BOARD_PENDING`; fuera del alcance de W3.1 se sitúa la detección de caídas silenciosas aguas abajo de cualquier sink externo no conectado, **sin afirmar que R10 global esté cumplida**. Si una entrega confirmada de logs deviene funcionalmente necesaria, requiere una decisión de alcance y prueba previa en el Gate correspondiente; no es permiso para habilitar actualmente una plataforma de logging ni excepción a los NADR FROZEN.

**Reconciliación individual de testigos históricos F18-04 (2026-11-23; sin nueva implementación):** se inspeccionaron las aserciones de `test_stage_reopen_replay_and_recompose_two_nodes`, `test_identical_retry_is_no_op_and_conflicting_retry_is_rejected`, `test_reopen_uses_durable_queue_receipt_for_idempotent_publication`, `test_failure_on_publication_insert_rolls_back_all_nodes`, `test_crash_after_publication_replays_without_reinference`, `test_crash_after_queue_completion_replays_to_fsm`, `test_completed_without_receipt_never_advances_fsm`, `test_engine_recovery_never_initializes_provider`, `test_fenced_recovery_rejects_stale_authority` y falsadores W06. **R1** reapertura desde fuente local; **R2** sin receipt no hay confirmación; **R3** PRAGMAs efectivos verificados por test; **R4** exclusión de power-loss documentada; **R5/R6** replay idempotente y rechazo de contenido en conflicto; **R7** fencing ante autoridad obsoleta; **R8** coherencia queue→publicación→FSM acreditable en el camino comprobado, **pero la aplicabilidad del event journal legada a G3 debe ratificarse**; **R9** reconstrucción de proyección derivada desde receipts recuperables (Board favorable en alcance), **no** reparación universal; **R10** recuperación poscommit sin reinferencia; **R11** atomicidad, reabertura, idempotencia y recuperación con falsadores separados; **R12** rollback no es garantía eléctrica; **R13** durabilidad no sustituye prueba de idempotencia; **R14** idempotencia no sustituye reconciliación de FSM; **R15/R16** clasificación UNKNOWN/no-inicio sin deducir ausencia de efecto externo. Los testigos existen y la suite [CI #45105007281](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45105007281) está en verde, pero su **acreditación integral por regla continúa sujeta a ratificación Board**, especialmente R8, R11 y límites de modelo de fallos. No se suponen consumidores nuevos, journal autoritativo universal ni Power Loss.

**CI exacta del falsador negativo (2026-11-22):** [CI #45102292492](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45102292492) terminó SUCCESS sobre `9ea325f752e0a30fdf66469a9bde60456a702cb9`; la ejecución demuestra comportamiento de interfaces locales existentes y reinicio SQLite en el alcance del test, sin implicar autorización excepcional, auditoría de decisiones inexistentes o resiliencia ante SQL arbitrario. H2 precisa dictamen del Board por regla; no se marca DONE por condición no disparada.

**Límite de la prueba negativa añadida:** `test_pppr_g3_unknown_blocks_all_authorized_local_retry_and_legacy_recovery` verifica el rechazo de `mark_g3_proven_no_start`, `renew_task_lease`, `release_task_untouched`, `abandon_execution`, `acknowledge_execution`, `mark_zombie_recovered`, `mark_cqrs_reconciled` y la selección `pick_task` tras abrir otra conexión, conservando el attempt y la primera llamada proveedor simulada. No ensaya modificaciones arbitrarias del archivo SQLite por un administrador y no atribuye inexistentes autorizaciones excepcionales. **CI del test del nuevo SHA pendiente; ninguna regla aún cambia automáticamente a DONE.**

## 4. TABLA CONSOLIDADA FINAL

**Estado:** `NO_ELABORADA`. Esta sección se completa al finalizar el **último Gate Exit Review**, sin declarar que no hubo findings simplemente porque aún no se revisó.

### 4.1 Resumen por clasificación

| Clasificación | Cantidad acreditada | Referencias |
|---|---|---|
| `CLOSED (NAR)` | NO_CALCULADO | — |
| `RESOLVED` y variantes | NO_CALCULADO | — |
| `IMPLEMENTATION_REQUIRED` | NO_CALCULADO | — |
| `RECLASSIFIED_FUTURE_PHASE` | NO_CALCULADO | — |
| `REVIEW_REQUIRED` | NO_CALCULADO | — |
| `ACCEPTED_LIMITATION` | NO_CALCULADO | — |

### 4.2 Tabla consolidada

| DF/GF | Clasificación fundamentada | Regla aplicada | Evidencia §2.N | Register |
|---|---|---|---|---|
| _Sin entradas; todavía no se ejecutaron Exit Reviews_ | — | — | — | — |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Cierre del Evidence Log

El documento solo alcanza `FROZEN` al cierre formal de PPPR, cuando:

- [ ] Se ha ejecutado el Exit Review de cada Gate exigible; todos los findings identificados tienen entrada forense individual.
- [ ] No quedan findings `PENDING_REVIEW` sin análisis o disposición.
- [ ] La tabla consolidada final está elaborada con IDs y evidencia verificable.
- [ ] Cada clasificación está fundamentada por una regla/autoridad real y datos concretos, sin normas inventadas.
- [ ] Todos los `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito y los `REVIEW_REQUIRED` un plan autorizado de reevaluación.
- [ ] Cada finding referenciado en el Findings Register remite a la evidencia forense de esta pieza; IDs reconciliados, sin duplicación.
- [ ] La inmutabilidad de entradas anteriores y las ampliaciones fechadas está comprobada.
- [ ] Los Gates y el estado de Product Readiness se informan con sus veredictos reales, sin deducir PASS de una revisión realizada.

### 5.2 Relación con el Findings Register

| Documento | Es fuente de verdad de | Momento de actualización |
|---|---|---|
| **Este Evidence Log** | Evidencia forense/observaciones y fundamentos de cada DF/GF | Incremental en el Exit Review de cada Gate; entradas inmutables |
| **FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md** | Clasificación, decisión de autoridad, plan/batch y resolución | Durante Exit Reviews y ejecución de batches |
| **PHASE_PPPR_EXECUTION_PLAN.md** | Tasks, secuencia, estados derivados, Gates y trazabilidad temporal | Durante ejecución autorizada de cada Task y Gate |

Una **clasificación operativa** se cambia **en el Register** por decisión documentada; la evidencia original de este Log se conserva y se puede complementar, sin reemplazarla.

---

**Nota de Gobernanza:** Evidence Log de PPPR, de naturaleza forense y **sin autoridad normativa**. Esqueleto publicado anticipadamente por decisión específica del owner con dictamen ajustado favorable del Board; autorización particular de calendario PPPR registrada en el encabezado, sin reforma general de §6.7. `IN_PROGRESS` significa *documento habilitado para construcción*, **NO** que haya empezado G1 o que existan revisiones completadas. Se congelará solo cuando concluyan la fase, las revisiones y la reconciliación forense.`