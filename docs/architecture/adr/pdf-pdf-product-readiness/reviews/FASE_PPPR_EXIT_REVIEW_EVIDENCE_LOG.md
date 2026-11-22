# FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/pdf-pdf-product-readiness/reviews/FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md`  
**Versión:** 0.1.11  
**Estado:** IN_PROGRESS — Gate 1 Exit Review REALIZADO/PASS; G2/W2.1 integrada, Wave 2.2 / PR #86 con falsadores y CI técnica [CI #44972570392](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44972570392) SUCCESS sobre `a6ce8eb88e2c9bf50114cba26d0ecb7a80e0a865`. Test interprocesos, CI final, Board y merge todavía pendientes. G2 Exit Review NOT_RUN, 14 GAP P1 OPEN, `PRODUCT_READINESS=NOT_CERTIFIED`; no se certifica ciencia ni egress.
**Fecha:** 2026-11-21  
**Última actualización:** 2026-11-21  
**Derivado de:** `PHASE_PPPR_EXECUTION_PLAN.md` v0.5.9 APPROVED/LIVING — G1 PASS, G2 IN_PROGRESS; W2.1 MERGED, W2.2 evidencia CI verde del código y aceptación pendiente; Gate 2 Exit Review NOT_RUN.
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

**Estado del Gate 1 (2026-11-21):** Exit Review REALIZADO y, luego del complemento de CI del SHA evaluado en SUCCESS, **G1 PASS/COMPLETED**. La constatación inicial `BLOCKED_PENDING_CI_HEAD` permanece como evidencia temporal en §3.1, sin alteración retroactiva. G2–G6 `NOT_RUN`. **0 hallazgos DF/GF nuevos** y ningún certificado científico; el registro por finding §2 permanece vacío.

| Gate del Execution Plan | Revisión real | Evidencia por DF/GF | Decisión/veredicto |
|---|---|---|---|
| G1 — Baseline y autoridad | **REALIZADO 2026-11-21 + addendum de CI posterior**; 4/4 Tasks DONE | **0 DF/GF nuevos**, sin §2 ficticio. Referencias de criterios en Plan §2.1.4 y CI/CV en §3.1 | **G1 PASS/COMPLETED**; CI del HEAD SUCCESS, CV científica FAIL/DEFERRED |
| G2 — Procedencia e identidad | NOT_RUN (G2 IN_PROGRESS; W2.1 integrada, W2.2 técnicamente implementada, Board/merge pendientes) | Sin entradas DF/GF nuevas inventadas; 14 GAP históricos OPEN | PENDING — sin veredicto de Gate |
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