# FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/pdf-pdf-product-readiness/reviews/FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md`  
**Versión:** 0.1.9  
**Estado:** IN_PROGRESS — G1 COMPLETED/PASS; G2/Wave 2.1 3/3 Tasks DONE, diez reglas FPPPR-04 CI_VERIFIED y Board FAVORABLE_A_INTEGRACION (PR #85, sincronización documental previa a merge). Wave2.2 PENDING, Gate2 Exit Review NOT_RUN, 14 GAP P1 OPEN, sin nuevo DF/GF ficticio ni certificación científica. ARCHIVED solo al cierre PPPR.
**Fecha de creación:** 2026-11-21  
**Última actualización:** 2026-11-21  
**Derivado de:** `PHASE_PPPR_EXECUTION_PLAN.md` v0.5.8 APPROVED/LIVING; G1 PASS, G2/W2.1 3/3 DONE y diez reglas CI_VERIFIED; HEAD auditado por Board `2535860a23236a9325d56c2cb582c1c5d404265f`, CI #44962322464 SUCCESS; PR #85 pendiente de integración al documentar.
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
| G2 — Ingesta física e identidad | NOT_RUN (Wave 2.1 3/3 Tasks DONE, Wave 2.2 pendiente) | Sin nuevo DF/GF fuera de GAP-0.2-01/02 ya previstos; sin Exit Review |
| G3 — Seguridad de efectos e inferencia G3 | NOT_RUN | Sin entradas |
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
| Gates revisados | **1 realizado: G1 PASS/COMPLETED**; G2 IN_PROGRESS/Wave2.1 completa, Exit Review G2 NOT_RUN; G3–G6 NOT_RUN |
| Hallazgos PPPR registrados nuevos | **0 DF/GF nuevos fuera del alcance planificado** en G1 y W2.1; GAP-0.2-01/02 preexistentes no duplicados; no inferir ausencia global de defectos |
| Hallazgos analizados/resueltos/diferidos | **0 nuevos en Gate 1; clasificación N/A** (no inventar NAR) |
| Batches ejecutados | NOT_RUN |
| Estado de los Exit Reviews | **G1 REVIEW_REALIZADO / CI posterior SUCCESS → PASS/COMPLETED; G2–G6 NOT_RUN** |
| Estado operativo del Register | **IN_PROGRESS — checkpoint W2.1 tras CI real, sin batch de findings ni Gate 2 Exit Review** |
| Cierre de fase | **PENDIENTE / NO ARCHIVED** |

---

**Nota de Gobernanza:** este documento registra **hallazgos → clasificación → decisión → batch → commit** y **no** contiene la evidencia forense detallada ni constituye una autoridad normativa. La evidencia por DF/GF se conserva en `FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md`, de manera incremental e inmutable una vez registrada. Ninguna entrada ni Gate Exit Review se presume ejecutado por crear este esqueleto.`