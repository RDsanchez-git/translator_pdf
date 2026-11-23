# FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/pdf-pdf-product-readiness/reviews/FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md`  
**Versión:** 0.1.28  
**Estado:** G3 COMPLETED/PASS (Exit Review REALIZADO 2026-11-23, §2.3.3 4/4 PASS). 6/6 G3 Tasks DONE; 52/52 historic W3.1 rules (44 CI_VERIFIED/SCOPE_REVIEWED, 5 CONDITION_NOT_TRIGGERED/BOARD_SCOPE_ACCEPTED, 2 MODEL_SCOPE_LIMIT_ACCEPTED, 1 ACTIVE_SCOPE_CI_VERIFIED/EXCEPTION_CONDITION_NOT_TRIGGERED) plus 10/10 FPPPR-03 rules W3.2 (R1–R10 disposition per row). CI #45260540282 SUCCESS (3/3 jobs, Pyright 0 errors/0 warnings, import-linter 4/4) on exact integrated SHA 9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81. 0 DF/GF new in reviewed scope; 14 GAP P1 OPEN; CV #45260540192 FAIL/DEFERRED (BASELINE_INTEGRITY_FAILURE, exit 3; 15 private canonical PDFs absent); PRODUCT_READINESS=NOT_CERTIFIED. G4–G6 NOT_RUN.
**Fecha de creación:** 2026-11-21  
**Última actualización:** 2026-11-23  
**Derivado de:** Execution Plan v0.5.27, Evidence Log v0.1.29; Gate3 Exit Review over pdf-pdf-product-readiness@9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81.
**Ámbito:** PPPR (iniciativa transversal PDF→PDF; no fase histórica numerada).  
**Propósito:** Registro único y auditable de hallazgos `DF`/`GF` **que surjan durante la ejecución y los Exit Reviews** del Execution Plan: identificación, clasificación, decisión, resolución, batch y evidencia de implementación.

**Baseline al crear el esqueleto:** G1–G6 PENDING, 30 Tasks TODO, sin hallazgos ni Exit Reviews. **Checkpoint tras W1.1 (2026-11-21):** G1 IN_PROGRESS, dos Tasks de baseline/trazabilidad DONE por verificación documental; W1.2 pendiente, G1 Exit Review NOT_RUN. La auditoría estática acotada **no originó DF/GF nuevo**; no demuestra ausencia general de defectos. Los 14 `GAP-ID` P1 OPEN de PPPR.0.9 continúan como referencias históricas, no nuevos findings.

**Checkpoint al completar Wave 1.2 (2026-11-21):** `1.2.1` y `1.2.2` DONE por verificación GitHub CI/CV y registro explícito de dependencias/autoridades, no por ejecución científica ni por inferencia del plan. [CI técnica #44935045055](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44935045055) **SUCCESS**: Pyright 0 errores/0 advertencias, import-linter PASS, 1454 PASS/4 SKIPPED/20 E2E deselected; [CV #44935045265](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44935045265) **FAIL / BASELINE_INTEGRITY_FAILURE (exit 3)** por 15 PDF ausentes. Owner **ratificó** `PPPR-G1-CI-SCOPE-01` solo para G1 §2.1.3(3), [issue #34 comentario 7069421655](https://github.com/RDsanchez-git/translator_pdf/issues/34#issuecomment-7069421655). El déficit de corpus y diferimiento del benchmark son **preexistentes** y siguen OPEN/DEFERRED; no se les asigna un DF nuevo ni se atribuye resolución. No surgió DF/GF nuevo distinto durante W1.2 dentro del alcance auditado. **G1 sin Exit Review ni PASS**; permisos G5/G6 pendientes.

**Registro post Gate 1 Exit Review (2026-11-21, realizado, pero NO Gate PASS):** los cuatro Exit Criteria se examinaron con las evidencias del Execution Plan §2.1.4. Baseline, trazabilidad normativa y matriz de autoridades **acreditados documentalmente**; la excepción G1 `PPPR-G1-CI-SCOPE-01` está ratificada. La [CI #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) sobre `718a81a…` **estaba IN_PROGRESS durante el review** (Static Analysis SUCCESS, suite restante sin resultado final), por lo que se dejó el **Gate BLOCKED/PENDING_CI**; la [CV #44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) permanece **FAIL**, ciencia NO CERTIFICADA. La revisión de G1 **no identificó hallazgos nuevos DF/GF**: no se crean registros `DF-01/GF-01` de relleno ni `CLOSED (NAR)` para ausencias de findings. Issue #34 y HITO PPPR.0.9 conservan sus identidades y autoridad.

**Complemento de cierre G1 (2026-11-21; posterior al review inicial, no lo reemplaza):** GitHub Actions [CI #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) finalizó **completed/SUCCESS**, HEAD `718a81a7816ef91710b3a86b00cc4326b0b18262`; Static Analysis (Pyright + import-linter), Unit Test Suite e Integration Test Suite completaron **SUCCESS**, incluido el paso técnico `not e2e`. Con la excepción `PPPR-G1-CI-SCOPE-01` ratificada específicamente para §2.1.3(3), **los cuatro Exit Criteria de G1 quedaron acreditados y G1=PASS/COMPLETED** tras la reevaluación. La [CV #44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) continúa **FAIL/DEFERRED**, sin test científico PASS, por el corpus histórico ausente. **0 DF/GF nuevos** y 14 GAP P1 OPEN. G2 habilitado por precedencia, todavía sin iniciar.

**Checkpoint histórico de Wave 2.1 (2026-11-21; revisado por Board; NO Gate 2 Exit Review):** las Tasks `2.1.1`, `2.1.2` y `2.1.3` implementaron los diez falsadores de NADR-FPPPR-04 FROZEN en la ruta física y el perfilado, sin importar contratos nuevos ni alterar NADR. [CI GitHub #44955114310](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44955114310) **completed/SUCCESS** del commit `2542d6aed46d044d5384b7004070cb3bb1c8deb7`: Pyright 0 errores/0 advertencias, import-linter PASS, 248 unitarios PASS y suite técnica `not e2e` 1478 PASS, 4 SKIPPED y 20 E2E deselected. La actualización de gobernanza ocurre **en el mismo PR #85** después del resultado. Se corrigieron en alcance los problemas conocidos `GAP-0.2-01/02` (sampler/geometry) **sin declararlos cerrados formalmente**, pendientes de evaluación global en Gate2; no surgió un `DF` o `GF` nuevo **fuera de lo planificado**. Los hallazgos P1 existentes siguen identificados en HITO PPPR.0.9; el informe de CI técnico no certifica ciencia ni habilita W2.2 retroactivamente.

**Addendum correctivo del Architecture Board (2026-11-21; PR #85, mismo scope W2.1):** Dictamen FAVORABLE CON CORRECCIONES; NO autoriza merge. La inspección del HEAD anterior `c7bf6725974e77396b7bed51be29952583c14ca6` acreditó CI técnica [#44955971217](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44955971217) SUCCESS, pero reveló que OCR perdía los diagnósticos de perfil en SQLite y el consumidor podía promover layout sin conservar la incertidumbre. El commit correctivo `1ef307dae8a7009d6a7f35a6cdf28038c7a120b4` en el MISMO PR #85 adjunta `ProfileDiagnostics` al perfil, lo persiste con hash vinculado al documento y migración legada sin falsas garantías, emite telemetría acotada por ID, y exige cobertura STRICT_SCOPE y geometría sin limitaciones antes de activar el layout de doble columna. Se agregan falsadores de OCR Router real con nodo válido + nodo indeterminado, reinicio SQLite, replay, manipulación, documentos mezclados y regiones inmutables. La CI correctiva [#44960950403](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44960950403) queda **PENDING_FINAL_REVALIDATION** al redactar este addendum. La prueba exitosa del HEAD anterior NO se transfiere al nuevo HEAD: 10/10 reglas FPPPR-04, en particular R9/R10, no se reclaman nuevamente VERIFIED sin CI final y aceptación Board.

**Límites explícitos:** `ExtractionProviderFactory` conecta únicamente PyMuPDF. Los falsadores de la ruta de producto NO acreditan Docling histórico (`provs[0]`, fallback `page_no=1`, BBox `+0.01`), ni se incorpora un proveedor alternativo. `PhysicalRegion.source_document` puede conservar rutas locales en el AST persistido; evaluar minimización/redacción y privacidad antes de habilitar egress externo, que aquí NO está autorizado. El historial de 14 GAP P1 continúa OPEN; CV científica FAIL/DEFERRED, Wave 2.2 PENDING, Gate 2 Exit Review NOT_RUN y `PRODUCT_READINESS=NOT_CERTIFIED`. Ninguna Task, NADR, Gate, criterio fijo, DF/GF ficticio ni PR adicional.

**Interpretación del register:** la corrección requerida está dentro de GAP-0.2-01/02; no se inventa DF/GF por observación de revisión ni se adelanta cierre forense del Gate 2. CI técnica correctiva SUCCESS; revisión final del Board/merge pendientes.

**Addendum de revalidación técnica del HEAD correctivo (2026-11-21; no es Gate 2 Exit Review):** [CI técnica #44961625659](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44961625659) completó **SUCCESS** sobre SHA `0dc091fa7f1b3a3bbd38f9841ba4c8805061475b` con tres jobs SUCCESS (Static Analysis, Unit Test Suite, Integration Test Suite); Pyright **0 errors/0 warnings/0 informations**, import-linter PASS, unitarios **250 PASS / 1257 deselected / 3 warnings**; suite completa `pytest -m "not e2e"` **1483 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar la selección de 250 tests al resultado de 1483. Los falsadores correctivos OCR/SQLite/consumidor y el caso mixto están en el HEAD evaluado. La evidencia técnica para FPPPR-04 R9/R10 y los diez requisitos queda **CI_VERIFIED / BOARD_ACCEPTANCE_PENDING**: el Board debe revisar la corrección y el owner conserva autoridad exclusiva de merge. **PR #85 OPEN/Draft sin merge, Wave 2.2 PENDING, G2 Exit Review NOT_RUN, 14 GAP P1 OPEN, CV científica FAIL/DEFERRED, PRODUCT_READINESS NOT_CERTIFIED.**

**Checkpoint definitivo para integración W2.1 (2026-11-21; no es Gate 2 Exit Review):** el Architecture Board realizó una segunda revisión **FAVORABLE A LA INTEGRACIÓN** del PR #85 sobre el HEAD `2535860a23236a9325d56c2cb582c1c5d404265f`. [CI final de la revisión Board #44962322464](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44962322464) confirmó **completed/SUCCESS para exactamente ese SHA**, con tres jobs SUCCESS (Static Analysis, Unit Test Suite, Integration Test Suite), Pyright **0 errores / 0 advertencias / 0 informaciones**, import-linter **4/4 contratos conformes**, unitarios **250 PASS / 1257 deselected / 3 advertencias**, y suite completa `pytest -m "not e2e"` **1483 PASS / 4 SKIPPED / 20 E2E deselected / 3 advertencias**. No sumar ejecuciones separadas. La conformidad de los diez falsadores `NADR-FPPPR-04` es **CI_VERIFIED** y el dictamen del Board es **FAVORABLE_A_INTEGRACION**, limitado a la ruta conectada **PyMuPDF**, NO a Docling histórico. El owner **autoriza expresamente el merge del PR #85 tras esta sincronización documental y una CI SUCCESS del HEAD final**. Se trata de autoridad expresada en la conversación, no de un review APPROVED emitido por la API de GitHub. Los checkpoints anteriores (`#44961625659`, `0dc091fa…`) se mantienen como historial, no como evidencia del HEAD `2535860…`. Esta nota se fija **antes de ejecutar el merge**, que se verificará en GitHub después; G2 IN_PROGRESS, Wave 2.2 PENDING, Gate 2 Exit Review NOT_RUN, 14 GAP P1 OPEN, CV científica FAIL/DEFERRED, `PRODUCT_READINESS=NOT_CERTIFIED`, sin permiso de egress.

**Decisión específica del owner y dictamen ajustado favorable del Architecture Board (2026-11-21):** para **PPPR exclusivamente**, se autoriza publicar este esqueleto `IN_PROGRESS` en GitHub **antes del cierre** y actualizarlo de manera incremental cada vez que se identifique, clasifique o resuelva un hallazgo, se complete una Task relacionada o se realice un Exit Review/batch. El owner autorizó explícitamente el merge documental del PR #81 únicamente hacia `pdf-pdf-product-readiness`; el Board expresó dictamen ajustado **favorable a esa integración**. Esto constituye una **autorización particular de calendario y versionado operativo** frente al momento general de commiteo indicado en `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §6.7: **no reforma el texto general, no concede excepciones a otras fases** ni altera los requisitos de evidencia. `ARCHIVED` solo al cierre formal de PPPR. El documento `IN_PROGRESS` **no implica** G1 iniciado, permisos de código, pruebas, materiales privados, egress ni certificación.

---

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-11-21 | Esqueleto inicial sin DF/GF ni Exit Reviews. |
| 0.1.1 | 2026-11-21 | Registra autorización puntual del owner y dictamen ajustado favorable del Board para publicación/actualización incremental PPPR, sin modificar §6.7 ni el cierre ARCHIVED. |
| 0.1.2 | 2026-11-21 | Checkpoint posterior a W1.1: no nuevos DF/GF detectados en auditoría documental; G1 IN_PROGRESS, 1.1.1/1.1.2 DONE, W1.2 pendiente, Exit Review y batches NOT_RUN. |
| 0.1.3 | 2026-11-21 | Checkpoint al cierre de W1.2: CI técnica SUCCESS, CV científica FAIL/DEFERRED visible, resolución G1 ratificada por owner, permisos consumidores pendientes; no nuevos DF/GF ni Gate Exit Review. |
| 0.1.4 | 2026-11-21 | Gate 1 Exit Review realizado: 4/4 Tasks verificadas, sin nuevos DF/GF, issue #34 histórico no duplicado. Gate BLOCKED/PENDING_CI del HEAD 718a81a; CI previo PASS, CI del HEAD aún IN_PROGRESS; CV científica FAIL/DEFERRED. Sin batches ni Gate PASS. |
| 0.1.5 | 2026-11-21 | Complemento posterior: CI #44951655134 SUCCESS en HEAD evaluado; G1 Exit Review pasa de bloqueo transitorio documentado a PASS/COMPLETED. CV científica permanece FAIL/DEFERRED, sin DF/GF nuevos, sin batches; G2 habilitado pero no iniciado. |
| 0.1.6 | 2026-11-21 | G2/Wave 2.1 implementada y verificada con CI #44955114310 (Pyright 0/0, suite técnica 1478 PASS, 4 SKIPPED, 20 E2E deselected). Correcciones in-scope GAP-0.2-01/02 sin atribuir cierre forense previo a Exit Review. Sin DF/GF nuevo fuera del alcance, sin batches ni revisión de G2. Misma PR #85 que código/pruebas y Evidence Log. |

| 0.1.7 | 2026-11-21 | Addendum Board PR #85, R9/R10 OCR/SQLite corregidos a nivel código, CI correctiva pendiente; mantiene 14 GAP OPEN, sin DF/GF inventados ni Gate2 Exit Review. |
| 0.1.8 | 2026-11-21 | CI técnica correctiva #44961625659 SUCCESS, 10 reglas CI_VERIFIED/Board pendiente, sin declarar nuevo DF/GF ni cerrar 14 GAP P1. PR #85 permanece Draft; G2 Exit Review NOT_RUN. |
| 0.1.9 | 2026-11-21 | Board segunda revisión favorable a integración PR #85, CI final auditada #44962322464 SUCCESS sobre `2535860…`, owner habilita merge tras sincronización y revalidación. Sin nuevo DF/GF ni cierre anticipado de GAP/G2. |
| 0.1.10 | 2026-11-21 | Checkpoint técnico W2.2 / PR #86: 3 Tasks implementadas, código CI #44972570392 SUCCESS (287 unit, 1536 suite técnica PASS); test posterior interprocesos PENDING, Board/merge pendientes, Gate2 Exit Review NOT_RUN y 14 GAP P1 OPEN; sin DF/GF inventados. |
| 0.1.11 | 2026-11-21 | Segundo dictamen Board PR #86 FAVORABLE CON RESERVA, mitigación de sobrescritura AST y prueba de coherencia durable del recibo. CI correctiva #44975050240 SUCCESS en `69d56ef3…`; no nuevos DF/GF inventados ni cierre de GAP, Board/merge pendientes, Gate2 Exit Review NOT_RUN. |
| 0.1.12 | 2026-11-21 | Gate2 Exit Review realmente ejecutado: 6/6 Tasks, 30 reglas propias G2 verificadas; CI #44977644736 SUCCESS sobre `ac156be2…` (289 unit PASS, 1542 suite técnica PASS), Board tercera revisión FAVORABLE y owner autoriza merge posterior a este registro. Criterios 4/4 PASS, 14 GAP P1 OPEN, sin DF/GF nuevos detectados ni CV científica certificada, G3 pendiente. |

| 0.1.13 | 2026-11-22 | Reconciliación post-merge de PR86 `7842bb3c69c2baf792cb9cb3acca088462445d54`, CI #44978406678 y #44979093690 SUCCESS; G2 COMPLETED/PASS, 6/6 Tasks y 30/30 reglas. Sin segundo Exit Review, nuevos DF/GF, cierre forense de 14 GAP P1 ni certificación científica; G3 NOT_RUN. |
| 0.1.14 | 2026-11-22 | W3.1 PR90 autorizada e implementándose offline: autoridad pos-semáforo, no-inicio CAS, UNKNOWN recuperable y alarma configurable. CI y dictamen Board pendientes; 3 Tasks IN_PROGRESS, 0 DONE nuevas; ningún DF/GF nuevo ni Gate3 Exit Review. 14 GAP P1 históricos OPEN. |
| 0.1.15 | 2026-11-22 | Board PR90 FAVORABLE CON CORRECCIONES / NO MERGE. H1 HIGH (no-inicio cuota mal clasificado) y H3 MEDIUM (alarma UNKNOWN dependiente de sweeps) mitigados en código y falsadores propuestos CI_PENDING; H2 HIGH exige trazabilidad 24 normas F18-04/05, tabla en Execution Plan §7.H.1 con evidencia parcial/gaps declarados. No se abren DF/GF formales diferidos por observaciones in-scope aún no resueltas; 14 GAP P1 históricos OPEN. |
| 0.1.16 | 2026-11-22 | Revalidación técnica H1/H3 tras [CI #45100465237](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45100465237) SUCCESS en `4340538…`; nuevos falsadores H2 de reconstrucción derivada desde receipts y exposición de UNKNOWN aun sin auditoría (SHA `0d528b1…`, CI pendiente). No se convierten observaciones in-scope en DF/GF inventados; permanecen reglas parciales F18-05 R14/R15 sin prueba aplicable y Task 3.1.3 no DONE. |
| 0.1.17 | 2026-11-22 | Board segunda revisión PR90: H1/H3 RESUELTOS, H2 PARCIAL y aplicabilidad de retry excepcional condicionada; [CI #45101231199](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45101231199) SUCCESS sobre `6e83816…`. Falsador adicional de rutas autorizadas de retry UNKNOWN (sin decisión excepcional ficticia) en `ff531d23…`, CI_PENDING. No se abre DF/GF diferido ni se presume normatividad DONE; 14 GAP P1 históricos OPEN. |
| 0.1.18 | 2026-11-22 | [CI #45102292492](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45102292492) SUCCESS en HEAD `9ea325f752e0a30fdf66469a9bde60456a702cb9` (3/3 jobs, 289 unitarios, 95 integración focal, 1561 suite `not e2e` PASS, 4 skipped/20 E2E excluidos). Falsador de prohibición de UNKNOWN vía APIs locales ejecutado; H2 pendiente de dictamen por regla y aplicabilidad condicional, sin nueva DF/GF formal ni cambio de 14 GAP P1. 3 Tasks NO DONE / PR90 NO MERGE. |
| 0.1.19 | 2026-11-23 | Board acepta PROHIBITED PATH local y CONDITION NOT TRIGGERED sin auto-DONE; H1/H3 RESUELTOS, H2 F18-05 R1/R2/R10/R13/R15 PARCIAL. [CI #45103595023](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45103595023) SUCCESS en `68dec1f…`. Auditoría focal de emisores JSON y reconciliador SQLite con dos nuevos tests de formato y alarma sin sink en `518e2a0…` CI_PENDING. Sin DF/GF diferidos nuevos; 14 GAP históricos OPEN, W3.1 NO DONE. |
| 0.1.20 | 2026-11-23 | [CI #45105007281](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45105007281) SUCCESS sobre `a49cd95285ae874dddeaea26011f391e741fa3b1` (289 unit, 95 integración focal, 1563 `not e2e` PASS/4 skipped/20 excluidos). Board R1/R2/R13/R15 F18-05 acreditables en alcance; R10 PARCIAL por ausencia de detección de pérdida de entrega al sink, propuesta de delimitación pendiente. Auditoría individual de testigos F18-04 R1–R16 en plan §7.H.1, R8/R11 aún a ratificar. Sin cambios runtime, findings nuevos ni Task DONE. |
| 0.1.21 | 2026-11-23 | Cierre técnico W3.1 3/3 Tasks DONE tras revisión de 52 reglas históricas 10+18+24 (ver Plan v0.5.20 §7.H/§7.H.1), [CI #45106195219](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45106195219) SUCCESS sobre `c2490e037d203c2fa291f7b3c046bb4fce5b80fb`. Board favorable a R8/R10/R11 con límites, H1/H3 resueltos y prohibición de retry UNKNOWN probada por APIs locales; condiciones de autorización excepcional no disparadas, R16 evidencia externa no presente, sin tests positivos inventados. CI final del nuevo HEAD documental pendiente; owner autoriza merge PR90 tras SUCCESS. G3 Exit Review NOT_RUN; 14 GAP P1 históricos siguen OPEN, 0 DF/GF diferidos nuevos. |
| 0.1.22 | 2026-11-23 | W3.1 PR90 MERGED `67c12e70…`, [CI #45108175696](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45108175696) SUCCESS y [CV SMOKE #45108175690](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45108175690) FAIL corpus privado ausente. W3.2 offline iniciada: Task3.2.1 IN_PROGRESS con falsadores EN→ES/request físico, CI_PENDING; otras dos Tasks TODO. Sin nuevos DF/GF acreditados, 14 GAP históricos OPEN y Exit Review G3 NOT_RUN. |
| 0.1.23 | 2026-11-23 | [CI #45109251169](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45109251169) SUCCESS 3/3, EN→ES en request real+sin llamada para idioma incompatible. Groq retiro modelo productivo (2025-08-30) y catálogo potencial consultados 2026-11-23; fallback sin selección física permanece inadmisible. Guardias fail-closed con fake 0 llamadas en commit `33b81e79…`, CI_PENDING. 3.2.1 y 3.2.2 IN_PROGRESS, 3.2.3 TODO, sin DF/GF nuevos ni Gate3 Exit Review. |
| 0.1.24 | 2026-11-23 | [CI #45111804056](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45111804056) SUCCESS `7b87810a…`; incidentes CI por fakes sin `target_provider` revisados y corregidos. Task 3.2.3 implementa política de admisión positiva solo sintética y bloqueo productivo por falta de autorización, request físico/reserva de salida, límites independientes/estimación/egress/coste; [CI #45113284911](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45113284911) pendiente. Sin DF/GF nuevos ratificados, 14 GAP P1 históricos OPEN, W3.2 NO DONE/NO MERGE. |
| 0.1.25 | 2026-11-23 | Board H1/R9, H2/estimador no-inicio, H3/Decimal no-finito; parches acotados en PR91 commit `fb74ce96…` con auditoría durable por intento y testigos offline. CI anterior [CI #45114218248](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45114218248) SUCCESS, CI código nuevo [CI #45237767800](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45237767800) y CI documental pendientes. H1-H3 todavía no CLOSE sin re-review, sin DF/GF diferido nuevo por conjetura. 14 GAP históricos OPEN. |
| 0.1.26 | 2026-11-23 | [CI #45237767800](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45237767800) SUCCESS en `fb74ce96…`: 1608 pruebas técnicas PASS/4 skipped; H1/H2/H3 con falsadores de auditoría, falla local y Decimal no-finito. Cierre formal Board pendiente, no se reclasifica automáticamente como DONE, no se crean DF/GF diferidos sin autoridad. CI del checkpoint documental pendiente. |
| 0.1.27 | 2026-11-23 | [CI #45255747256](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45255747256) SUCCESS en 32603508a38df9b08571b97b60796f2f07fac5cc (3/3 jobs; Pyright 0 errors/0 warnings, import-linter 4/4, 289 unit PASS, 95 integración focal PASS, 1610 `not e2e` PASS/4 skipped/20 E2E excluidos; selecciones no sumables). Board favorable a H1–H4 y al cierre normativo offline; owner autoriza integrar PR91 sólo tras SUCCESS del HEAD documental final. W3.2 3/3 Tasks DONE offline, R1–R10 en Plan §7, H1–H4 aceptados, 14 GAP P1 históricos OPEN, sin DF/GF nuevos ni Gate3 Exit Review. |
| 0.1.28 | 2026-11-23 | G3 COMPLETED/PASS (Exit Review REALIZADO 2026-11-23, §2.3.3 4/4 PASS); 6/6 G3 Tasks DONE; 52/52 historic W3.1 rules (44 CI_VERIFIED/SCOPE_REVIEWED, 5 CONDITION_NOT_TRIGGERED/BOARD_SCOPE_ACCEPTED, 2 MODEL_SCOPE_LIMIT_ACCEPTED, 1 ACTIVE_SCOPE_CI_VERIFIED/EXCEPTION_CONDITION_NOT_TRIGGERED) plus 10/10 FPPPR-03 rules W3.2 (R1–R10 disposition per row); CI #45260540282 SUCCESS (3/3 jobs, Pyright 0 errors/0 warnings, import-linter 4/4) on exact integrated SHA 9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81; no new DF/GF in scope. CV #45260540192 FAIL/DEFERRED (BASELINE_INTEGRITY_FAILURE, exit 3; 15 private canonical PDFs absent); PRODUCT_READINESS=NOT_CERTIFIED. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_PPPR_MASTER.md (FROZEN)
    ↓
NADR-FPPPR-01/02/03/04 (FROZEN)
    + reglas F17-BIS/F18 únicamente por sujeto, estado y frontera ratificados
    ↓
PHASE_PPPR_EXECUTION_PLAN.md (APPROVED / LIVING / NOT_STARTED)
    ↓
ESTE REGISTER (operativo, no normativo)
```

Prevalecen `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §§3.5.3, 6.5–6.7 y `6_METH_DEFERRED_FINDINGS_REGISTER_FASE_{X}.md`. Ninguna clasificación del Register modifica reglas de un NADR ni obligaciones del plan.

### 0.2 Principio rector del Exit Review PPPR

> ¿El hallazgo demostrado impide cumplir una obligación vigente o un Gate Exit Criterion de la ruta única `CLI → OCR → G3 → G5 → PDF`, o corresponde a una superficie ajena a esta etapa que debe clasificarse y derivarse mediante decisión competente, **sin desviarnos de las Tasks autorizadas**?

Un hallazgo dentro del alcance y bloqueante **no** se difiere automáticamente. Las limitaciones, los permisos y las decisiones de arquitectura/ciencia se elevan a su autoridad; este registro no crea autorizaciones.

### 0.3 Reglas transversales aplicables

- Evidencia observada ≠ obligación normativa ≠ decisión de clasificación. No inventar ejecuciones, nuevas violaciones o métricas.
- `DF-XX` y `GF-XX` nacen al identificar un hallazgo **nuevo de implementación/revisión**, con ID estable por orden de registro y referencia a Gate/Wave/Task.
- Los 14 GAP-ID de PPPR.0.9 **no se renumeran ni se duplican**; una relación futura se registra como vínculo, no como hallazgo nuevo sin evidencia.
- `NADR-FPPPR-01` gobierna legitimidad de la certificación científica; `NADR-FPPPR-03` admisión G3; `NADR-FPPPR-04` geometría; ADR Maestro DC-04 identidad; F18 compatible, seguridad de efectos. No resolver discrepancias normativas unilateralmente.
- Exit Review ≠ ejecución de batch. El análisis forense detallado de cada finding se conserva en el **Exit Review Evidence Log** y la clasificación/resultados viven **solo aquí**.
- Clasificación `RECLASSIFIED_FUTURE_PHASE` exige destino, justificación, autoridad, impacto sobre Gate y vínculo a evidencia. No autoriza pasar un Gate con obligación propia incumplida.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen y exclusividad |
|---|---|---|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico nuevo durante implementación/Exit Review PPPR |
| `GF-{XX}` | Governance Finding | Conflicto de autoridad o aplicabilidad normativa pendiente de decisión competente |
| `H-{XX}-{X}` | Hallazgo derivado | Hallazgo identificado al examinar un DF ya existente |
| `GAP-0.x-XX` | GAP forense preexistente | **Solo referencia cruzada** a HITO PPPR; no se consume como DF |
| `E-0.x-XXX` | Evidencia forense histórica | Referencia; no prueba nueva ni resultado de una Task |

**Regla de unicidad:** los IDs DF/GF no se reutilizan ni se borran por reclasificación. Se asignarán al primer hallazgo real, sin reservar entradas ficticias en este esqueleto.

### 1.2 Estados de clasificación (canónicos)

| Estado | Significado |
|---|---|
| `PENDING_REVIEW` | Hallazgo nuevo, pendiente de Exit Review |
| `REVIEW_REQUIRED` | Análisis adicional exigible antes de decidir |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación, con scope por delimitar/aprobar |
| `RESOLVED` | Implementado y cerrado con evidencia suficiente |
| `RESOLVED — DELETE` | Código muerto eliminado y acreditado |
| `RESOLVED — MOVE` | Código reubicado y validado |
| `RESOLVED — REFACTORED` | Código refactorizado y validado |
| `RESOLVED — FACTORY EXTRACTION` | Lógica separada en factory, con pruebas |
| `CLOSED (NAR)` | No Action Required: no-gap o comportamiento correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida aceptada por autoridad competente |
| `RECLASSIFIED_FUTURE_PHASE` | Derivado con fase/etapa de destino y justificación |
| `DEFERRED — FASE {X}` | Diferimiento específico con autoridad y ADR pendientes, cuando corresponda |

Los estados reflejan decisiones fundadas, **no** etiquetas preventivas para permitir el avance de un Gate.

### 1.3 Reglas de evidencia

Cada DF/GF exigirá: texto original, fecha/origen Gate/Wave/Task, rutas/SHAs de archivos/documentos auditados, distinción `CONFIRMADO / HIPÓTESIS / NO-GAP`, norma/regla aplicable, evidencia en `FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md` y decisión/autoridad identificables. Al resolver: PR/commit, verificación/validación real y alcance del resultado.

**No** se implementa durante el Exit Review; las correcciones se programan en batches posteriores autorizados. No se inventa batch para un finding que aún no existe. Un `GF` se eleva a la autoridad que corresponda antes de ejecutar decisiones fuera del plan.

### 1.4 Protocolo de actualización dinámica

| Evento real | Actualización del Register |
|---|---|
| Nuevo DF/GF | ID estable, origen, `PENDING_REVIEW`, referencia a evidencia disponible; no cerrar prematuramente |
| Gate Exit Review | Agregar sección por Gate ejecutado; clasificaciones/decisiones vinculadas al Evidence Log |
| Clasificación posterior | Conservar ID, estado anterior, decisión, fecha, motivo y autoridad; no reescribir forense |
| Batch autorizado y terminado | Agregar resultado de implementación y pruebas reales, con SHAs |
| Diferimiento fuera de PPPR | Registrar justificación, destino y responsable, y someter efecto sobre Gate a autoridad |
| Cierre de PPPR | Reconciliar consolidado, batches, decisiones y evidencias; `ARCHIVED` solo tras cierre formal |

---

## 2. GATE EXIT REVIEWS

**Estado del Gate 1 Exit Review (2026-11-21, histórico y complemento):** inicialmente **REVIEW_REALIZADO / BLOCKED_PENDING_CI_HEAD** porque la suite del SHA todavía se ejecutaba; luego **CI SUCCESS / G1 PASS/COMPLETED** en addendum fechado, sin reescribir el estado inicial. **0 DF/GF nuevos** observados en este alcance. G2–G6 PENDING/NOT_RUN.

| Gate previsto | Exit Review | Hallazgos registrados por esta revisión |
|---|---|---|
| G1 — Baseline, autoridad y preparación | **REALIZADO 2026-11-21; reevaluación CI final → G1 PASS/COMPLETED** | **0 DF/GF nuevos**; issue #34 y GAP P1 históricos no duplicados |
| G2 — Ingesta física e identidad | **Exit Review 2026-11-21 4/4 PASS; PR86 MERGED 2026-11-22 `7842bb3c69c2…`, CI posterior SUCCESS; G2 COMPLETED/PASS** | **0 DF/GF nuevos acreditados en alcance**, observaciones H1/H2 resueltas antes de integración; 14 GAP P1 históricos OPEN |
| G3 — Seguridad de efectos e inferencia G3 | **REVIEW_REALIZADO/PASS, 4/4 on 2026-11-23** | 0 new DF/GF in review; 14 GAP P1 historical OPEN; scientific CV FAIL/DEFERRED |
| G4 — Reconstrucción G5 y PDF | NOT_RUN | Sin entradas |
| G5 — Integración y operación real | NOT_RUN | Sin entradas |
| G6 — Conformidad científica y cierre | NOT_RUN | Sin entradas |

### 2.1 Gate 1 Exit Review (2026-11-21) — REALIZADO / BLOQUEADO POR CI ACTUAL

**Sujeto revisado:** G1/W1.1–W1.2, 4/4 Tasks `DONE`, referencia normativa §2.1.3(1–4) y Review §2.1.4 del Execution Plan. **HEAD:** `pdf-pdf-product-readiness@718a81a7816ef91710b3a86b00cc4326b0b18262`. No se inspeccionó código nuevo en G1: PR #82 y #83 alteraron exclusivamente tres Markdown.

| DF/GF nuevo | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión de clasificación | Motivo y evidencia |
|---|---|---|---|---|---|
| **Sin hallazgos nuevos identificados en el alcance G1** | N/A | N/A | N/A | **NO SE ABRE DF/GF; sin estado CLOSED (NAR) inventado** | Inspección de SHAs, plan §2.1.4, [CI #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134), [CV #44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082), issue #34 |

**Árbol de decisión aplicado:** no existe un **hallazgo nuevo** que someter a clasificación de implementación, NAR, diferimiento o GF. El bloqueo actual es la ausencia de un resultado final de CI del **SHA efectivo**, no la aparición de un defecto probado adicional ni un desacuerdo normativo nuevo. La CV histórica **FAIL/DEFERRED** conserva su referencia al issue #34 y la resolución de alcance exclusiva G1; no cambia a PASS. Si el run actual falla por un defecto nuevo, corresponde capturar su evidencia inmediatamente y abrir el DF/GF que proceda.

**Resultados de criterios de G1:** 1 baseline **PASS**; 2 matriz reglas/GAP **PASS documental**; 3 excepción aprobada + CI anterior SUCCESS pero CI de HEAD vigente **PENDING**, por tanto **sin PASS final**; 4 dependencias externas registradas por autoridad/consumidor **PASS documental**. Las autorizaciones futuras no concedidas permanecen PENDING en su Gate consumidor.

**Resumen de clasificación:** nuevos DF = **0 observados**; nuevos GF = **0 observados**; implementaciones de findings = **0**; batches = **0**; derivaciones futuras = **0 nuevas**. Estos números se refieren solo a este review, **no** a ausencia global de defectos ni al censo histórico P1.

**Veredicto:** **GATE_REVIEW_REALIZADO; G1 BLOCKED/PENDING_CI_HEAD, NO PASS, G2 NO HABILITADO.** Gate Completion Log §3 del plan no indica fecha de cierre satisfactorio. Evidencia operativa en Execution Plan §2.1.4; referencia en Evidence Log §3.1. Una actualización posterior de un run CI debe quedar fechada y ligada al SHA correspondiente, sin reescribir silenciosamente este review.

**Addendum (2026-11-21, verificación posterior):** [CI #44951655134](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655134) concluyó **SUCCESS** en el SHA `718a81a…`, y sus tres jobs técnicos (Static Analysis, Unit Tests, Integration Tests) pasaron. **Veredicto final de G1: PASS/COMPLETED** conforme a §2.1.3(1–4) y a la resolución de alcance `PPPR-G1-CI-SCOPE-01` aprobada solo para el punto 3. Se conserva arriba el bloqueo transitorio observado al realizar el review. CV [#44951655082](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44951655082) **FAIL/DEFERRED**, ninguna certificación científica. **0 nuevos DF/GF, 0 batches, G2 no iniciado**.

**Estructura para próximos Gates N (NO son revisiones ejecutadas):**

- Encabezado `### 2.N Gate N Exit Review (fecha efectiva)`; HEAD/SHAs, tareas/reglas, veredicto del Gate en Execution Plan.
- Árbol de decisión, tabla `DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo | Evidence Log`.
- Clasificación con autoridad y evidencia de cada finding nuevo; sin repetir oráculos ni implementar dentro del Exit Review.
- Si el criterio requerido no se cumple, registrar `BLOCKED` aunque el review se haya realizado.

---

**Checkpoint técnico Wave 2.2 / PR #86 (2026-11-21; NO Gate 2 Exit Review):** implementación y falsadores de Tasks 2.2.1–2.2.3 integrados en la rama del PR #86, **sin merge**; [CI #44972570392](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44972570392) **completed/SUCCESS** sobre SHA exacto `a6ce8eb88e2c9bf50114cba26d0ecb7a80e0a865`, 3/3 jobs SUCCESS, Pyright 0 errors/0 warnings/0 informations, import-linter PASS; unitarios **287 PASS / 1273 deselected / 3 warnings** y suite `pytest -m "not e2e"` **1536 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar ejecuciones separadas. Se añadió después el falsador de reproducibilidad entre procesos/PYTHONHASHSEED en `tests/unit/test_pppr_g2_semantic_identity.py`, commit `9ab965622fcd65f7a300522598a8c696943bf79a`; su CI [#44974172865](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44974172865) **IN_PROGRESS al registrar este checkpoint**, NO certificada por el run del SHA anterior.

**2.2.1 — Identidad semántica / incertidumbre:** `core/ast/hashing.py` define `AST_SEMANTIC_PRODUCT_V2`, sensible a texto, orden, nivel H1/H2/H3 y profundidad y ajeno a IDs operacionales/geometría. Canonización Unicode NFC conservadora sin colapsar símbolos STEM. `core/layout/models.py` y `core/ast/builder.py` transportan nivel explícito y admiten evidencia de encabezados numerados (`1`, `1.2`, `1.2.3`) probada con PDF temporal en `tests/integration/test_pppr_g2_semantic_pdf_chain.py`; los encabezados no numerados permanecen `UNKNOWN` y `core/chunking/contextual_plan.py` los conserva como `PRESERVE` sin inventar H1 ni abortar OCR, con falsador en `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py`. No se certifica reconocimiento jerárquico universal de PDFs.

**2.2.2 — Propósito de generación EN→ES:** `core/prompting/inference_identity.py` define `PPPRGenerationIdentityV1` basada en el candidato W08 `InferenceReuseIdentityV1`, separando identidad semántica, identidad de generación y autoridad de intento W06. Incluye documento/AST, manifest, chunk, snapshot de contexto, prompt efectivo, idioma fuente/destino, proveedor/modelo, versión de prompt, contrato de salida y configuración efectiva/ruta de presupuesto. `apps/llm_workers/sync_bridge.py` materializa la identidad y `runtime/chunk_staging.py` la pasa al recibo durable en `infra/db/control_repo.py`, con migración SQLite aditiva y falsadores de variación de dimensiones en `tests/unit/test_pppr_g2_generation_identity.py`; no presume que dos generaciones tengan resultados científicos idénticos.

**2.2.3 — Consumidores reales e integridad:** `ASTRegistry.get_verified_document_ast` relee el JSON persistido y acredita hash semántico V2 más `artifact_sha256` separado para `node_id`, `strategy`, metadatos y demás campos durables; `core/compiler/context_resolver.py` y el runtime productivo usan lectura verificada. La huella local detecta drift accidental, **no es firma de autenticidad criptográfica frente a un actor que controle archivo y hash**. `ChunkPlan`, snapshots, contexto, receipts G3, publicación/ensamblado y replay conservan sus controles específicos; `runtime/engine.py` exige la `root_config_sha256` activa en recuperación productiva y `infra/db/control_repo.py` rechaza recibos de otra configuración, corruptos o legados no atestados. Falsadores de AST manipulado, reinicio, estrategias, jerarquía, idempotencia, cambio de generación, migración SQLite y recorrido CLI offline. La caché `CachedLLMProvider` no seleccionada permanece desactivada y el worker heredado no se presenta como conformidad del producto.

**Gobernanza y frontera:** alcance offline sintético y proveedor de extracción productivo PyMuPDF. `G2 IN_PROGRESS`, Wave 2.2 **TECHNICAL_CI_VERIFIED_PRE_BOARD** sobre SHA `a6ce8eb88e2c9bf50114cba26d0ecb7a80e0a865`, falsador entre procesos y CI del HEAD posterior **pendientes**, 3 Tasks implementadas **sin convertir revisión/merge pendiente en DoD final**. Los 14 GAP-ID P1 permanecen OPEN; no se inventan DF/GF, batches ni Gate 2 Exit Review; CV científica FAIL/DEFERRED (15 PDF privados ausentes, excepción G1 no extensible); sin egress, gasto, evaluación científica, G3, `main` ni PR #66. `PRODUCT_READINESS=NOT_CERTIFIED`. El Board revisará el HEAD documental final después de CI verde y el owner decide el merge.

**Addendum correctivo Architecture Board / Wave 2.2 (2026-11-21; PR #86; NO Gate 2 Exit Review):** segundo dictamen **FAVORABLE CON UNA RESERVA DE INTEGRIDAD**, sobre HEAD documental `9a69c70a700fa55f9370c41651c7e694896bfcac`; autorización de merge **NO emitida**. El Board identificó una colisión legítima entre identidad semántica V2 y contenido durable distinto: `register_ast()` podía sustituir silenciosamente archivos con igual `document_id`/`ast_hash`, pero distinta identidad de nodo, estrategia o procedencia física. **Corrección:** `core/ast/registry.py` comprueba la firma semántica al registrar, escribe un temporal completo y publica mediante `os.link` sin sobrescritura atómica; reintento con contenido idéntico = idempotente; archivo preexistente diferente/corrupto = rechazo y sin mutación de caché. `tests/integration/test_pppr_g2_semantic_registry.py` falsifica conflicto con hash semántico igual, idempotencia y carreras de dos escritores independientes, además de rechazo de artefacto inválido.

**Suficiencia real del recibo de generación:** `infra/db/control_repo.py` y `infra/db/schema_queue.sql` agregan `generation_binding_sha256` a recibos nuevos y migración SQLite aditiva; la vinculación local combina documento, AST, manifiesto, unidad, tarea, ejecución, checksum de respuesta, `generation_sha256` y `root_config_sha256`. El consumidor recalcula esa vinculación en replay productivo: cambio **solo** de `generation_sha256` manteniendo idéntica la configuración raíz y la respuesta ⇒ `PPPR_G2_GENERATION_RECEIPT_BINDING_DRIFT`; recibo sin vinculación bajo validación productiva ⇒ `PPPR_G2_REPLAY_GENERATION_UNVERIFIED`. Falsadores `tests/integration/test_g3_b4_1_worker_coexistence.py` y CLI offline. **Límite de autoridad:** el consumidor comprueba coherencia durable local y configuración raíz, **NO recalcula la preimagen efectiva de prompt/modelo/contexto del productor** ni acredita una firma de autenticidad de tercero; `SyncProviderBridge` sigue siendo el productor de la identidad por propósito. No se convierte el hash semántico en hash universal, no se habilita caché LLM ni se reclaman garantías científicas.

**Evidencia técnica correctiva:** [CI técnica #44975050240](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44975050240) **completed/SUCCESS** para HEAD exacto `69d56ef349fef9443e6dc1fe9390027401c219f9`, jobs Static Analysis, Unit Test Suite e Integration Test Suite **3/3 SUCCESS**, Pyright **0 errores / 0 advertencias / 0 informaciones**, import-linter PASS, unitarios **288 PASS / 1277 deselected / 3 warnings**, integración focal **95 PASS / 1470 deselected**, suite `pytest -m "not e2e"` **1541 PASS / 4 SKIPPED / 20 E2E deselected / 3 warnings**. No sumar ejecuciones separadas. Este resultado acredita **código y falsadores del SHA citado**, no la CI posterior del commit exclusivamente documental. Wave 2.2 **TECHNICAL_CI_VERIFIED_PRE_BOARD**, 3/3 Tasks implementadas pero `IN_PROGRESS/BOARD_PENDING` hasta aceptación formal y autorización de integración. G2 `IN_PROGRESS`, Exit Review `NOT_RUN`, 14 GAP P1 históricos `OPEN`, sin nuevos DF/GF ficticios ni certificación científica, `PRODUCT_READINESS=NOT_CERTIFIED`; sin egress, gastos, host, G3, main ni PR #66.

### 2.2 Gate 2 Exit Review (2026-11-21) — REALIZADO / CRITERIOS PASS

**Sujeto de la revisión:** G2/Wave2.1 integrada por PR #85 (`pdf-pdf-product-readiness@2c42628d…`) y G2/Wave2.2 en PR #86. Tercera revisión Architecture Board **FAVORABLE A LA INTEGRACIÓN**, SHA `0d42ad7f30a9576fa6bec05d0fe336a95de16cc7` y [CI #44975791556](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44975791556) SUCCESS, H1 (no-clobber AST) y H2 (binding local recibos) corregidas. Dos falsadores unitarios normativos finales sin alteración productiva validados en [CI #44977644736](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44977644736) **completed/SUCCESS** sobre `ac156be223d2db952e968352bc1ea38c3531186e`: 3/3 jobs, Pyright 0/0, import-linter 4/4, 289 PASS unitarios y 1542 PASS suite técnica `not e2e`, 4 SKIPPED, 20 E2E excluidos. No sumar selecciones.

**Control forense:** seis Tasks G2 implementadas y aceptadas técnicamente (2.1.1–2.2.3), diez reglas propias FPPPR-04 y veinte reglas históricas de propiedad G2 con falsadores en Execution Plan §7.H. Exit Criteria §2.2.3 **(1)–(4) PASS**: procedencia y muestreo físicos PyMuPDF, falsadores de GAP previstos, jerarquía/Unicode STEM, suficiencia de consumidor durable, CI y regresiones técnicas. Sin nuevo DF/GF sustentado en un defecto abierto identificado por esta revisión acotada; H1/H2 son observaciones correctivas resueltas **antes** de la integración, no se inventan IDs ni `CLOSED (NAR)`. Los **14 GAP P1 históricos permanecen OPEN**: superar un falsador técnico de Gate no significa una decisión forense de cierre.

**Dictamen/autoridad:** owner autoriza expresamente merge del PR #86 **una vez actualizado este Gate2 Exit Review**. El Exit Review está REALIZADO y los cuatro criterios PASS; la ejecución y verificación del merge/HEAD destino se harán después del registro. La aprobación Board llegó por la conversación transmitida por el owner, **no es una review APPROVED de la API de GitHub**. `G2 COMPLETED` y DoR de G3 solo se habilitan luego de verificar integración. La CV científica sigue FAIL/DEFERRED por 15 PDFs privados ausentes; `PRODUCT_READINESS=NOT_CERTIFIED`; ni Docling ni egress/proveedor comercial/host/`main`/PR66 incluidos.

**Addendum post-merge (2026-11-22; NO es nuevo Exit Review/DF/GF):** [PR #86](https://github.com/RDsanchez-git/translator_pdf/pull/86) MERGED luego de autorización y acta, `pdf-pdf-product-readiness` HEAD `7842bb3c69c2baf792cb9cb3acca088462445d54`. [CI #44978406678](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44978406678) y [CI #44979093690](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44979093690) SUCCESS. El estado previo «merge por verificar» se conserva cronológicamente, pero **G2 está ahora COMPLETED/PASS**. [CV #44979093692](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44979093692) FAIL/DEFERRED por `BASELINE_INTEGRITY_FAILURE` (15 PDFs canónicos ausentes en runner); los 14 GAP P1 siguen OPEN, `PRODUCT_READINESS=NOT_CERTIFIED`. G3 NOT_RUN y sin autorización de inicio.

**Board PR #90 — revisión 2026-11-22 sobre `3c5e366e6b948c20f37d82334787826b4c4fb456`: FAVORABLE CON CORRECCIONES / NO MERGE.** H1 HIGH: `PermanentQuotaRejection` / `QuotaTimeoutError` provenían del rate limiter antes de `_underlying.translate` y caían en UNKNOWN genérico; el PR añade catch específico en `runtime/engine.py` y CAS `mark_g3_proven_no_start(permanent=True/False)`, con pruebas de cero I/O y reintento acotado. H3 MEDIUM: sweeps previos ya no bloquean la alarma; `_run_sweep_cycle` aísla excepciones y deduplica por `(task_id,execution_id)` durante TTL en memoria, conservando SQLite como autoridad. H2 HIGH: matriz individual de 24 reglas propietarias de Task 3.1.3, sin presumir cobertura universal. **Estado: CODE_PROPOSED / CI DEL SHA FINAL PENDIENTE, BOARD_REVIEW_PENDING, ningún DONE nuevo**.

**Tratamiento del Register:** H1–H3 son observaciones de revisión del PR90 con remediación en el mismo PR. No constituyen DF/GF diferidos ni están cerradas; si resultara un defecto irresoluble dentro de la Wave se evaluará entonces la apertura formal siguiendo §1. Los 14 GAP P1 históricos no cambian.

**Dictamen de aplicabilidad propuesto para segunda decisión del Board — PR90 / H2 (2026-11-22; no cambia NADR FROZEN):**
- **PROHIBITED PATH / prueba negativa en alcance:** `NADR-F18-03 §5.3 R13` y `R15` (ninguna vía productiva autorizada de retry de `G3_EXTERNAL_UNKNOWN`); test `test_pppr_g3_unknown_blocks_all_authorized_local_retry_and_legacy_recovery` invoca selección, API de no-inicio, renovación, abandono, liberación, reconocimiento y reconciliación legada sobre el mismo attempt después de UNKNOWN y tras reapertura SQLite. El test prueba rechazo en **interfaces locales existentes**, no integridad frente a escrituras SQL privilegiadas arbitrarias ni una capacidad de aprobación/rematerialización comercial inexistente. Estado **TEST_EXECUTED_CI_SUCCESS / BOARD_DISPOSITION_PENDING**, no `DONE`.
- **CONDITION NOT TRIGGERED (a ratificar):** `NADR-F18-03 §5.3 R14`, `NADR-F18-05 §5.4 R11`, `NADR-F18-05 §5.5 R14` y porción de `R15` referida a decisiones excepcionales. Sin camino productivo de autorización, aceptación de riesgo, decisión o retry excepcional, no existe una decisión cuya contabilización o durabilidad pueda falsarse. Este dato no prueba cumplimiento positivo ni permite `DONE` automático. La obligación queda vinculante si se habilita esa capacidad posteriormente; su habilitación exige decisión normativa y tests de autorización, identidad, durabilidad y auditabilidad, sin excepción metodológica implícita.
- **Obligación actual independiente de condición:** `NADR-F18-05 §5.5 R15` también obliga a separar evidencia autoritativa de métricas derivadas aun sin reejecuciones excepcionales; los tests de UNKNOWN con auditoría ausente, reinicio y alertas volátiles aportan evidencia focal pero **no acreditan universalmente** todo observability-plane. `NADR-F18-04 §5.3 R9` reconstruye el **conjunto derivado ausente** desde receipts locales recuperables; no implica reparación automática de fila corrupta aislada ni supervivencia de fuentes destruidas.
- **Criterio para cierre:** confirmar en Board la suficiencia de falsadores individuales y la aplicabilidad/inalcanzabilidad **sin reclasificar automáticamente una regla con `CONDITION NOT TRIGGERED` como `DONE`**. Toda brecha que siga aplicable y sin evidencia permanece `PENDING`; no agregar proveedores, colas, oráculos o infraestructura de monitoreo artificiales.

**Checkpoint CI final para segunda revisión (2026-11-22):** [CI #45102292492](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45102292492) SUCCESS sobre `9ea325f752e0a30fdf66469a9bde60456a702cb9` valida H1/H3 y falsador negativo de retry UNKNOWN en interfaces examinadas. La condición de autorización/reintento excepcional no ocurrió ni existe capacidad productiva implementada; la aplicación normativa debe ratificarse sin marcar automáticamente una regla DONE. No se abre finding diferido por este debate dentro del mismo PR.

**Board — decisión de aplicabilidad recibida (2026-11-23; sin nuevo Exit Review):** H1 y H3 RESUELTOS; `VERIFIED — PROHIBITED PATH` para NADR-F18-03 §5.3 R13 limitado a APIs locales examinadas; `CONDITION NOT TRIGGERED` para F18-03 §5.3 R14/R15 y F18-05 §5.4 R11/§5.5 R14, sin declarar PASS ficticio ni eliminar obligación futura; F18-05 §5.5 R15 **PARCIAL**. Board mantiene **NO MERGE / W3.1 IN_PROGRESS**, demanda cotejo focal de F18-05 §5.1 R1/R2, §5.3 R10 y §5.5 R13/R15 en productores/consumidores realmente conectados. No se autorizan reintentos excepcionales ni telemetría nueva.

**Auditoría focal de emisores realmente conectados (2026-11-23):** `runtime/engine.py` pone `ctx_execution_id` (identidad de intento), `ctx_task_id` (tarea lógica) y `ctx_node_id` (chunk), mientras `core/utils/telemetry.py` (`DistributedContextFilter`+`JSONFormatter`) los serializa; `apps/daemons/reconciler.py` reconstruye alarmas desde `ControlPlaneRepository.list_due_g3_unknown` (SQLite), incluyendo `document_id`, `ast_hash`, `chunk_id`, `task_id`, `execution_id`, `audit_valid`, `first_detected_at` y disposición manual. `core/metrics/metrics.py`, `core/metrics/summary.py` y sus exportadores son agregados heredados de Dispatch/FinOps; **no son lectores/autoridad de UNKNOWN en la ruta G3 inspeccionada**, ni emiten una tasa de duplicación externa en el alcance probado. Se agregan **solo dos falsadores offline** en `tests/integration/test_w06_g3_uncertain_effect_offline.py`: `test_pppr_g3_unknown_worker_json_log_correlates_attempt_to_durable_operation` y `test_pppr_g3_unknown_alarm_recovered_after_ephemeral_json_log_loss`. El primero prueba el formatter+filtro reales y la distinción `trace_id=execution_id` de identidades lógicas/científicas; el segundo descarta el buffer de logs, reinicia el daemon, verifica alarma nuevamente desde SQLite y demuestra que no cambia el attempt ni se habilita retry. **CI de estos dos tests PENDING**. Límites: no pruebas de sinks externos, reporting global, modificaciones SQL privilegiadas, gastos comerciales ni decisiones excepcionales inexistentes.

**Architecture Board — tercera revisión recibida (2026-11-23; sin review formal GitHub):** [CI #45105007281](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45105007281) SUCCESS sobre `a49cd95285ae874dddeaea26011f391e741fa3b1`: Pyright 0 errores/0 warnings/0 informations; import-linter 4/4; 289 unit PASS, 95 integración focal PASS, `not e2e` **1563 PASS, 4 SKIPPED, 20 E2E excluidos, 2 warnings pytest**. Board considera F18-05 §5.1 **R1/R2** y §5.5 **R13/R15 (porción activa)** **ACREDITABLE EN ALCANCE** en emisores/lectores locales reales, con la parte excepcional de R15 `CONDITION NOT TRIGGERED`. **R10 PARCIAL**: faltaba distinguir recuperación de UNKNOWN de detección de pérdida de entrega a un sink. Ninguna de las cuatro acreditaciones acotadas autoriza reclasificar las otras 20 normas a PASS; 3.1.3 no DONE.

**Dictamen propuesto de alcance F18-05 §5.3 R10 (Architecture Board, a ratificar; 2026-11-23):** R10 aplica efectivamente a los **datos de auditoría local conectados a G3** (SQLite `chunk_tasks.error_log`), a su consumidor `ControlPlaneRepository.list_due_g3_unknown` y al emisor de alarma `ReconcilerDaemon`. Una auditoría ausente/corrupta se identifica explícitamente como `PPPR_G3_UNKNOWN_AUDIT_CORRUPT_REQUIRES_OPERATOR`; **jamás se interpreta como cero, éxito o permiso de nuevo intento**. Ante pérdida de la salida JSON efímera, el estado UNKNOWN persiste, es recuperable y genera una nueva alarma al reiniciar el reconciliador. **No hay detección de pérdida de entrega del propio buffer/stream**: la eliminación de ese buffer fue inducida en el test, no detectada por el producto. `JSONFormatter`+`StreamHandler` publican registros, pero ningún contrato de entrega confirmada a un colector externo, ACK ni lector de logs capaz de cambiar el estado G3 aparece conectado a esta ruta examinada. **Propuesta:** `R10 LOCAL_AUDIT_GAP_DETECTION_VERIFIED / EXTERNAL_LOG_DELIVERY_UNVERIFIED / SCOPE_BOARD_PENDING`; fuera del alcance de W3.1 se sitúa la detección de caídas silenciosas aguas abajo de cualquier sink externo no conectado, **sin afirmar que R10 global esté cumplida**. Si una entrega confirmada de logs deviene funcionalmente necesaria, requiere una decisión de alcance y prueba previa en el Gate correspondiente; no es permiso para habilitar actualmente una plataforma de logging ni excepción a los NADR FROZEN.

**Tratamiento de la observación R10:** brecha de acreditación in-scope mientras el Board no acepte explícitamente su delimitación; no se registra como defecto diferido nuevo ni se oculta mediante `CONDITION NOT TRIGGERED`. Si el Board determina que la entrega a un sink externo es parte del alcance operativo exigible, habrá que tramitar la corrección/falsador respectivo dentro de la Wave o cambiar el alcance por proceso formal.

**Wave 3.1 — CIERRE TÉCNICO/NORMATIVO PRE-MERGE (2026-11-23; NO Gate 3 Exit Review):** Architecture Board FAVORABLE a la implementación y a los alcances R10 (F18-05), R8/R11 (F18-04); H1/H3 resueltos y prohibición de retry UNKNOWN comprobada en APIs locales. Se efectuó cotejo individual de **52 reglas propietarias** (§7.H: 10/18/24 de Tasks 3.1.1/3.1.2/3.1.3), con testigo y límite propios por fila. **CI del código y documentos previos [CI #45106195219](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45106195219) SUCCESS** en `c2490e037d203c2fa291f7b3c046bb4fce5b80fb`, 3/3 jobs, Pyright 0/0/0, import-linter 4/4, 289 unitarios PASS, 95 integración focal PASS y `not e2e` 1563 PASS /4 skipped/20 E2E excluidos/2 warnings (no sumar selecciones). **La CI del HEAD documental de este checkpoint todavía requiere comprobarse antes de merge**. No hubo código ni tests nuevos para el cierre. Los supuestos excepcionales inexistentes constan `CONDITION_NOT_TRIGGERED / BOARD_SCOPE_ACCEPTED`; no se falsea un test positivo de excepciones ni se habilita retry. La ausencia de evidencias externas verificables para F18-03 R16 tampoco justifica inventar resolución. La frontera R10 limita detección de auditoría local; **no** demuestra entrega garantizada ni detección de pérdida a sink externo. F18-04 R8 usa los planos G3 existentes (receipts→proyección→FSM), no requiere event journal legacy adicional; R11 separa cuatro falsadores. F18-04 R4/R12 no amplían durabilidad a power-loss. **Las tres Tasks 3.1.x cierran como DONE técnico por cumplimiento dentro del alcance; Wave3.2/Gate3 Exit Review NO iniciados, G3 continúa IN_PROGRESS.** 14 GAP P1 históricos OPEN; `PRODUCT_READINESS=NOT_CERTIFIED`. El owner autoriza el merge #90 solo después de registrar estos estados y verificar CI exacta del HEAD final. No se presume una review APPROVE emitida por GitHub.

**Tratamiento del Register:** las observaciones H1/H2/H3 del Board fueron remediadas y verificadas en el PR; las limitaciones aceptadas de alcance no se clasifican artificialmente como DF/GF nuevos ni cierran los 14 GAP P1 históricos. `CONDITION_NOT_TRIGGERED` tampoco crea un permiso ni una excepción. Los criterios del Gate3 completo se revisarán tras Wave 3.2; no se simula ahora Gate Exit Review.

**Estado del Register:** las observaciones del Board sobre este PR son correcciones *in-scope*, no findings diferidos; ninguna aprobación o excepción fue creada y no se reduce el conjunto histórico de 14 GAP P1.

**Wave 3.2 / checkpoint inicial (2026-11-23):** [PR #90](https://github.com/RDsanchez-git/translator_pdf/pull/90) MERGED en `pdf-pdf-product-readiness@67c12e7020d76ab0c471fbf1179687c4d89f1783`; [CI #45108175696](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45108175696) SUCCESS técnica 3/3 sobre ese merge, [CV SMOKE #45108175690](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45108175690) FAIL `BASELINE_INTEGRITY_FAILURE` porque faltan 15 PDF privados en Actions. No atribuir CV PASS, no trasladar excepción G1 a G3. El owner autorizó iniciar **W3.2 offline**, nueva rama `pppr/g3-wave-3-2-contract-admission`, solo tres Tasks existentes y un PR de Wave. `3.2.1` IN_PROGRESS: en `apps/llm_workers/sync_bridge.py` se bloquea idioma ausente o distinto EN→ES antes de I/O, se explicita `language_intent` en el protocolo serializado y `tests/integration/test_g3_b4_3a_engine_staging.py` agrega falsadores de petición efectiva con renderer/dialecto reales, y proveedor espía con cero llamadas para idiomas inválidos. **CI del código nuevo pendiente; R1/R2 NADR-FPPPR-03 siguen PENDING**. `3.2.2` y `3.2.3` permanecen TODO: la auditoría histórica identifica el modelo `llama3-70b-8192` retirado, fallback lógico `SWITCH_MODEL` sin selección física coherente y faltan permisos de egress/presupuesto; no se declaran admitidos ni se ejecutan llamadas reales. 13/30 Tasks DONE, 17 pendientes; G3 IN_PROGRESS, G3 Exit Review NOT_RUN, 14 GAP P1 históricos OPEN y `PRODUCT_READINESS=NOT_CERTIFIED`. Sin cambios a FROZEN, baseline, corpus, egress, claves, gastos ni `main`.

**Checkpoint W3.2 / Hito técnico (2026-11-23):** [CI #45109251169](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45109251169) **SUCCESS sobre `20bc0490a66867844e3dfb626ffdefbdfb4cb341`** (3/3 jobs; Pyright 0 errors/0 warnings/0 informations, import-linter 4/4, 289 unit PASS, 95 integración focal PASS, suite `not e2e` **1569 PASS /4 SKIPPED /20 E2E excluidos /2 warnings**, selecciones no sumables). EN→ES explícito en protocolo G3, request dialect/renderer observado y cero provider fake calls para idiomas ausentes/incompatibles, sin declarar R1/R2 DONE hasta revisión. **Siguiente cambio focal de 3.2.2 en `33b81e79…`, CI_PENDING:** se bloquea pre-provider el modelo productivo `llama3-70b-8192` retirado y la ruta `SWITCH_MODEL` sin fallback físico acreditado; tests espía de 0 llamadas. Fuentes oficiales consultadas el 2026-11-23: [Groq deprecations](https://console.groq.com/docs/deprecations) (shutdown `llama3-70b-8192` 2025-08-30); [Groq Supported Models](https://console.groq.com/docs/models) y [GPT OSS 120B](https://console.groq.com/docs/model/openai/gpt-oss-120b) (candidato documental `openai/gpt-oss-120b`, 131072 context tokens, 65536 max completion); **candidato no seleccionado ni autorizado**. Sin prueba autenticada de compatibilidad efectiva por organización, cuota, autorización de egress ni presupuesto comercial; no se configura fallback ni se promete disponibilidad. **3.2.1 y 3.2.2 IN_PROGRESS, 3.2.3 TODO, Gate3 Exit Review NOT_RUN, W3.2 NO DONE**. La clasificación de `G3_EXTERNAL_UNKNOWN` de W3.1 permanece separada de los rechazos locales previos al efecto, sin reintentos ciegos; CV SMOKE sigue FAIL por corpus privado ausente, `PRODUCT_READINESS=NOT_CERTIFIED`. No se agregan DF/GF por causas históricas conocidas, no se cambia NADR FROZEN, no egress, gastos, corpus ni `main`.

**W3.2 / checkpoint de admisión pre-efecto (2026-11-23):** [CI #45111804056](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45111804056) **SUCCESS sobre `7b87810a640bd15fcfe3c6357a1d1fa9b4bd60e1`**, 3/3 jobs, Pyright 0/0/0, import-linter 4/4, 289 unit PASS, 95 integración focal PASS, suite `not e2e` **1571 PASS /4 SKIPPED /20 E2E excluidos/2 warnings**. Los dos fallos CI anteriores sobre `c7534d38…` y `519dab97…` se rastrearon a dobles sin `target_provider`; se revisaron los consumidores de `SyncProviderBridge` y ajustaron W06, W08 y cuota SQLite sin relajar el control productivo. **Nueva implementación de Task 3.2.3 en `b2bcb8b…`, CI nueva [CI #45113284911](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45113284911) PENDING:** `apps/llm_workers/g3_admission.py` crea una decisión pre-efecto explícita, atada a provider/modelo/root config/request físico; comparte con `GroqProvider` la construcción real de solicitud e incluye `max_completion_tokens`. Verifica de forma independiente entrada, reserva de salida y ventana, estimación, egress (destino/datos/finalidad/retención/training) y presupuesto con cota por tokens y precio; si falta cualquier evidencia, **NO DISPATCH** mediante `G3ExternalEffectNotStartedError`. La ruta productiva **no inyecta autorización alguna**, así que está **bloqueada por defecto**, sin llamadas comerciales, egress ni presupuesto implícito. Los testigos positivos nuevos usan políticas **sintéticas de proveedor fake offline**, no permisos reales; negativos con espía para cada límite/precondición y cero llamadas. Test CLI W08 con identidad atestiguada recibe únicamente la autorización sintética pertinente; se preservan contratos de W06/legacy. **Tasks 3.2.1/3.2.2/3.2.3 IN_PROGRESS / BOARD_PENDING**, ninguna DONE sin CI final y Board. No se acredita disponibilidad real del candidato documental, contabilidad comercial ni exactitud de tokenizador no documentada; se exige revisión del alcance de prueba de estimador y cobertura. Global 13/30 Tasks DONE; Gate3 Exit Review NOT_RUN, 14 GAP P1 históricos OPEN, `PRODUCT_READINESS=NOT_CERTIFIED`.

**Checkpoint Architecture Board W3.2 (2026-11-23, H1/H2/H3 — correcciones en PR91; CI final NO ACREDITADA):** El Board examinó `b2425f56dc6ea19e4843c875652bfe2481aa94de` y confirmó [CI #45114218248](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45114218248) **SUCCESS** (3/3; Pyright 0/0/0, import-linter 4/4, 289 unit, 95 focal, 1591 `not e2e` PASS, 4 skipped, 20 E2E excluidos). Dictamen **FAVORABLE CON CORRECCIONES / NO MERGE**. **H1 / FPPPR-03 R9:** el SHA del wire no prueba autorizaciones; en código nuevo `fb74ce968cfaf7a501e8c837ee512a9e4f93b1f4`, `G3AdmissionDecision` separa `request_sha256` del JSON de auditoría (referencias, capacidades, conteo, precios, cota) y `ControlPlaneRepository.record_g3_admission_decision` persiste un registro inmutable por `task_id/execution_id` con CAS de autoridad *antes del dispatch*, en SQLite de control, separado de la identidad científica; sin nuevo journal. **H2 / R10-F18:** la excepción del estimador se tipa como `G3ExternalEffectNotStartedError` antes de I/O y conserva CAS + estados durables; falla determinista `permanent=True`, falla transitoria usa presupuesto acotado. Test del motor real con SQLite descartable comprueba denegación duradera, 0 proveedor y no UNKNOWN. **H3 / R8:** precio y techo monetario deben ser `Decimal` finitos no negativos; el cálculo resultante también finito, con 12 falsadores de infinito/NaN pre-efecto. Tests adicionales de atestación, persistencia, reopen, identidad separada y falta de writer. **Evidencia CI:** [CI #45237767800](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45237767800) se inició sobre SHA de código `fb74ce9…`; **no se atribuye PASS hasta constatar resultado del HEAD exacto**. En este checkpoint documental se ejecutará CI propia. R3/R4 admiten solo evaluación offline **fail-closed sin backend comercial acreditado**, sujeto a disposición explícita futura Board; no se declara cuenta, autorización real o catálogo efectivamente disponible. **3.2.1/3.2.2/3.2.3 IN_PROGRESS / BOARD_REVIEW_PENDING**, las diez reglas R1–R10 siguen sin DONE formal; 13/30 Tasks DONE global, 14 GAP P1 históricos OPEN, `PRODUCT_READINESS=NOT_CERTIFIED`, Gate3 Exit Review NOT_RUN, PR91 OPEN/Draft, NO MERGE ni egress/corpus/gasto.

**Verificación de CI de correcciones H1/H2/H3 (2026-11-23):** [CI #45237767800](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45237767800) **SUCCESS** sobre SHA exacto de código `fb74ce968cfaf7a501e8c837ee512a9e4f93b1f4`, 3/3 jobs: Pyright 0 errores/0 warnings/0 informations, import-linter 4/4 contratos, 289 unitarios PASS, integración focal 95 PASS y suite `not e2e` **1608 PASS, 4 SKIPPED, 20 E2E excluidos, 2 warnings**. Los falsadores nuevos cubren el registro CAS durable y recuperación tras reapertura de SQLite, atestaciones diferentes para idéntico request, ausencia de writer, fallo inyectado del estimador en el motor real sin UNKNOWN ni dispatch, política permanente versus retry acotado y rechazos de `NaN`/`Infinity` en los tres importes. **R3/R4 siguen sujetos a la aceptación normativa del Board de fail-closed sin backend comercial admisible; R1–R10 permanecen sin cierre individual formal y las tres Tasks W3.2 IN_PROGRESS.** Esta CI corresponde al SHA de código anterior al checkpoint documental, cuya CI final debe verificarse separadamente. PR91 OPEN/Draft, NO MERGE, Gate3 Exit Review NOT_RUN, 13/30 Tasks DONE, `PRODUCT_READINESS=NOT_CERTIFIED`.


**W3.2 cierre documental de findings (2026-11-23, NO Gate3 Exit Review):** Board favorable a H1–H4 y al cierre normativo offline; owner autoriza integrar PR91 sólo tras SUCCESS del HEAD documental final. [CI #45255747256](https://github.com/RDsanchez-git/translator_pdf/actions/runs/45255747256) SUCCESS en 32603508a38df9b08571b97b60796f2f07fac5cc (3/3 jobs; Pyright 0 errors/0 warnings, import-linter 4/4, 289 unit PASS, 95 integración focal PASS, 1610 `not e2e` PASS/4 skipped/20 E2E excluidos; selecciones no sumables). H1 auditoría SQLite CAS, H2 estimador admisión pre-I/O, H3 Decimal finito y H4 prompt build/medición lógica pre-I/O fueron corregidos con falsadores; H4 motor real, SQLite durable, 0 proveedor/recibos/UNKNOWN. R1–R10 en Plan §7 con evidencia y límites; R3/R4: rechazo del modelo retirado/fallback lógico sin acreditación, NO modelo comercial admisible; R6: fail-closed sin estimador conservador comercial verificado; R7/R8: sin autorizaciones reales de egress ni gasto. No se crean DF/GF ficticios por correcciones del mismo scope, ni se cierran los 14 GAP P1 históricos. G3 Exit Review NOT_RUN, 16/30 Tasks DONE, 14 restantes, PRODUCT_READINESS=NOT_CERTIFIED, CI documental/merge pendientes.

### 2.3 Gate 3 Exit Review (2026-11-23) — REALIZADO / 4/4 PASS

**Baseline:** pdf-pdf-product-readiness@9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81. CI #45260540282 SUCCESS (3/3 jobs, Pyright 0 errors/0 warnings, import-linter 4/4) on exact integrated SHA 9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81. See Execution Plan §2.3.4 and Evidence Log §3.3 for separate evaluation of all four Exit Criteria.

| Exit Criterion | Decision |
|---|---|
| 1. Tasks/rules G3 | **PASS:** 6/6 G3 Tasks DONE; 52/52 historic W3.1 rules (44 CI_VERIFIED/SCOPE_REVIEWED, 5 CONDITION_NOT_TRIGGERED/BOARD_SCOPE_ACCEPTED, 2 MODEL_SCOPE_LIMIT_ACCEPTED, 1 ACTIVE_SCOPE_CI_VERIFIED/EXCEPTION_CONDITION_NOT_TRIGGERED) plus 10/10 FPPPR-03 rules W3.2 (R1–R10 disposition per row). |
| 2. Authority/UNKNOWN/recovery | **PASS:** W06/CAS/SQLite receipts/reopen/alarms, H2/H4 proven pre-effect no-start; uncertain effect retains F18 UNKNOWN. |
| 3. EN→ES and admission | **PASS offline only:** EN→ES request with spy, retired backend/fallback blocked, capability/estimation/egress/budget fail-closed. offline only: retired Groq model and logical SWITCH_MODEL without attested physical fallback are NO_DISPATCH; no commercial-model availability, verified conservative commercial estimator, egress, authorized budget or spending; UNKNOWN/F18 remains for possibly started effects. |
| 4. CI, tests and documents | **PASS:** CI #45260540282 SUCCESS (3/3 jobs, Pyright 0 errors/0 warnings, import-linter 4/4) on exact integrated SHA 9023ecbe267e2c7a45ce2e52e691e2c1e7a56b81; Plan v0.5.27, Findings v0.1.28, Evidence v0.1.29. |

**Findings:** 0 new DF/GF identified in this review: H1–H4 corrected in merged PR91, not invented as new deferred findings. 14 historical GAP P1 OPEN; CV #45260540192 FAIL/DEFERRED (BASELINE_INTEGRITY_FAILURE, exit 3; 15 private canonical PDFs absent); PRODUCT_READINESS=NOT_CERTIFIED. G4–G6 NOT_RUN. This documentary PR requires its own CI before any merge.

## 3. TABLA CONSOLIDADA FINAL

**Estado:** `NO_ELABORADA / NOT_RUN`. Se consolidará al cierre del último Gate Exit Review; no se presume que habrá cero hallazgos.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad acreditada | IDs |
|---|---|---|
| `CLOSED (NAR)` | NO_CALCULADO | — |
| `RESOLVED` y variantes | NO_CALCULADO | — |
| `IMPLEMENTATION_REQUIRED` | NO_CALCULADO | — |
| `RECLASSIFIED_FUTURE_PHASE` | NO_CALCULADO | — |
| `REVIEW_REQUIRED` | NO_CALCULADO | — |
| `ACCEPTED_LIMITATION` | NO_CALCULADO | — |

### 3.2 Tabla consolidada

| DF/GF | Estado final | Decisión / autoridad | Evidence Log |
|---|---|---|---|
| _Sin entradas: consolidado aún no elaborado_ | — | — | — |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

**Estado:** no se planificaron ni ejecutaron batches de resolución de findings nuevos. **No confundir batches de hallazgos con las 30 Tasks aprobadas en el Execution Plan.**

Al ejecutar un batch autorizado, agregar `### 4.N BATCH N — Nombre (fecha/estado)` con:

- DF/GF incluidos, autorización, Task/Gate relacionados, fecha, HEAD y commit/PR.
- Tabla `DF | Estado final | Acción ejecutada | Archivos afectados | Pyright/pytest/validación`.
- Correcciones adicionales, nuevos hallazgos derivados `H-XX-X`, reglas **ya existentes** aplicadas, decisiones de diseño justificadas y alternativas.
- Métricas *observadas*, cobertura/limitaciones, regresiones y evidencia verificable; no atribuir tests no ejecutados.

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualizan **al cierre de cada batch real**, derivados de las entradas de este Register y de los resultados acreditados; no se cargan valores a mano para simular progreso.

| Métrica canónica | Valor actual |
|---|---|
| Hallazgos analizados/resueltos/NAR | NOT_RUN / NO_CALCULADO |
| Reclasificados a fase futura | NOT_RUN / NO_CALCULADO |
| Pendientes de implementación/revisión | NOT_RUN / NO_CALCULADO |
| Batches completados | NOT_RUN |
| Archivos creados/modificados/eliminados/movidos por batches | NOT_RUN |
| Imports corregidos | NOT_RUN |
| Pyright final | NOT_RUN |
| Pytest final (passed/skipped) | NOT_RUN |

**Advertencia:** este estado se refiere **solo a los hallazgos registrados durante ejecución**. No rebaja los 14 GAP-ID P1 de PPPR.0.9 ni contabiliza sus remediaciones como DF sin una entrada real.

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino autorizado | Motivo técnico/normativo | Autoridad/fecha | Efecto sobre Gate y seguimiento |
|---|---|---|---|---|
| _Sin entradas registradas_ | — | — | — | — |

Un diferimiento no equivale a cancelar una Task requerida del plan ni un criterio de salida. Si el finding es bloqueante para un Gate, se conserva `BLOCKED` hasta resolución o decisión formal de alcance emitida por autoridad competente.

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

- [ ] Todas las correcciones autorizadas del batch commiteadas y vinculadas con DF/GF.
- [ ] `pytest` con baseline/suite exigible en verde; no ocultar skips ni alterar oráculos.
- [ ] `pyright` sin errores y sin incumplir el umbral del Execution Plan (0 errors / 0 warnings cuando exigido).
- [ ] Sin imports huérfanos; resultado observado y alcance documentados.
- [ ] Evidencia de verificación y validación asociada al mismo commit/HEAD.
- [ ] Findings reclasificados o cerrados solo mediante decisión sustentada en Evidence Log y autoridad.

### 7.2 Criterio de cierre del Findings Register

El documento se declara `ARCHIVED` **solo** tras cierre formal de PPPR, verificando que:

- [ ] Ningún `IMPLEMENTATION_REQUIRED` carece de batch o disposición formal.
- [ ] Ningún `REVIEW_REQUIRED` carece de decisión documentada.
- [ ] Batches planificados terminados y validados.
- [ ] Todos los `RECLASSIFIED_FUTURE_PHASE` tienen destino, dueño y justificación.
- [ ] Todas las entradas enlazan evidencia y decisiones del Exit Review Evidence Log.
- [ ] El cierre no encubre Gates `FAIL/BLOCKED` ni `PRODUCT_READINESS=NOT_CERTIFIED`.

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Estado actual |
|---|---|
| Gates revisados | **3 actual Gate Exit Reviews:** G1 PASS, G2 PASS, G3 PASS 4/4; G4–G6 NOT_RUN |
| Hallazgos PPPR registrados nuevos | **0 DF/GF nuevos fuera del alcance planificado** en G1 y W2.1; GAP-0.2-01/02 preexistentes no duplicados; no inferir ausencia global de defectos |
| Hallazgos analizados/resueltos/diferidos | **0 nuevos en Gate 1; clasificación N/A** (no inventar NAR) |
| Batches ejecutados | NOT_RUN |
| Estado de los Exit Reviews | G1/G2/G3 REVIEW_REALIZADO/PASS, G3 4/4 with #45260540282 on integrated baseline; CV científica separate FAIL/DEFERRED; G4–G6 NOT_RUN |
| Estado operativo del Register | IN_PROGRESS — G1/G2/G3 COMPLETED/PASS, 16/30 Tasks DONE, 14 GAP P1 historical OPEN, G4–G6 NOT_RUN, PRODUCT_READINESS=NOT_CERTIFIED |
| Cierre de fase | **PENDIENTE / NO ARCHIVED** |

---

**Nota de Gobernanza:** este documento registra **hallazgos → clasificación → decisión → batch → commit** y **no** contiene la evidencia forense detallada ni constituye una autoridad normativa. La evidencia por DF/GF se conserva en `FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md`, de manera incremental e inmutable una vez registrada. Ninguna entrada ni Gate Exit Review se presume ejecutado por crear este esqueleto.`