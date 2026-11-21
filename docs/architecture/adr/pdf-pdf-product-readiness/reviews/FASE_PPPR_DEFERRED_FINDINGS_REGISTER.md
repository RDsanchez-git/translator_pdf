# FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/pdf-pdf-product-readiness/reviews/FASE_PPPR_DEFERRED_FINDINGS_REGISTER.md`  
**Versión:** 0.1.1  
**Estado:** IN_PROGRESS — estructura preparada, **sin ejecución iniciada ni hallazgos registrados**; se archivará al cierre formal de PPPR.  
**Fecha de creación:** 2026-11-21  
**Última actualización:** 2026-11-21  
**Derivado de:** `PHASE_PPPR_EXECUTION_PLAN.md` v0.5.0 APPROVED / LIVING / NOT_STARTED, rama `pdf-pdf-product-readiness`.  
**Ámbito:** PPPR (iniciativa transversal PDF→PDF; no fase histórica numerada).  
**Propósito:** Registro único y auditable de hallazgos `DF`/`GF` **que surjan durante la ejecución y los Exit Reviews** del Execution Plan: identificación, clasificación, decisión, resolución, batch y evidencia de implementación.

**Estado empírico inicial:** Gates 1–6 `PENDING/NOT_RUN`, 30 Tasks `TODO`, sin Exit Review ni batches ejecutados. **No hay DF/GF nuevos registrados en este documento**; esto no implica ausencia de defectos. Los 14 `GAP-ID` P1 OPEN de PPPR.0.9 siguen siendo la baseline forense del Execution Plan y **no** se copian como hallazgos nuevos.

**Decisión específica del owner y dictamen ajustado favorable del Architecture Board (2026-11-21):** para **PPPR exclusivamente**, se autoriza publicar este esqueleto `IN_PROGRESS` en GitHub **antes del cierre** y actualizarlo de manera incremental cada vez que se identifique, clasifique o resuelva un hallazgo, se complete una Task relacionada o se realice un Exit Review/batch. El owner autorizó explícitamente el merge documental del PR #81 únicamente hacia `pdf-pdf-product-readiness`; el Board expresó dictamen ajustado **favorable a esa integración**. Esto constituye una **autorización particular de calendario y versionado operativo** frente al momento general de commiteo indicado en `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §6.7: **no reforma el texto general, no concede excepciones a otras fases** ni altera los requisitos de evidencia. `ARCHIVED` solo al cierre formal de PPPR. El documento `IN_PROGRESS` **no implica** G1 iniciado, permisos de código, pruebas, materiales privados, egress ni certificación.

---

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-11-21 | Esqueleto inicial sin DF/GF ni Exit Reviews. |
| 0.1.1 | 2026-11-21 | Registra autorización puntual del owner y dictamen ajustado favorable del Board para publicación/actualización incremental PPPR, sin modificar §6.7 ni el cierre ARCHIVED. |

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

**Estado inicial:** **ningún Gate Exit Review realizado**. El plan tiene seis Gates, todos `PENDING/NOT_RUN`. Los apartados `2.N` se agregan **solo** cuando se ejecute una revisión real; no se crean actas ficticias.

| Gate previsto | Exit Review | Hallazgos registrados por esta revisión |
|---|---|---|
| G1 — Baseline, autoridad y preparación | NOT_RUN | Sin entradas |
| G2 — Ingesta física e identidad | NOT_RUN | Sin entradas |
| G3 — Seguridad de efectos e inferencia G3 | NOT_RUN | Sin entradas |
| G4 — Reconstrucción G5 y PDF | NOT_RUN | Sin entradas |
| G5 — Integración y operación real | NOT_RUN | Sin entradas |
| G6 — Conformidad científica y cierre | NOT_RUN | Sin entradas |

**Estructura a completar para cada Gate N (NO es un review ejecutado):**

- Encabezado `### 2.N Gate N Exit Review (fecha efectiva)`; HEAD/SHAs, tareas/rules y veredicto del Gate en el Execution Plan.
- Árbol de decisión: validez → resolubilidad dentro del Gate → naturaleza técnica/normativa → `RESOLVED / CLOSED (NAR) / RECLASSIFIED_FUTURE_PHASE / GF`, con autoridad.
- Tabla `DF/GF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo | Evidencia Log §N`.
- Resumen por clasificación, nuevos hallazgos, revisiones tardías, decisiones arquitectónicas autorizadas y lecciones aprendidas.
- **Las decisiones de implementación no se ejecutan durante el Exit Review**.

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
| Gates revisados | NOT_RUN (G1–G6 pendientes) |
| Hallazgos PPPR registrados nuevos | Sin entradas a la fecha de creación |
| Hallazgos analizados/resueltos/diferidos | NOT_RUN |
| Batches ejecutados | NOT_RUN |
| Estado de los Exit Reviews | **NO_INICIADOS** |
| Estado operativo del Register | **IN_PROGRESS (esqueleto), sin trabajo ejecutado** |
| Cierre de fase | **PENDIENTE / NO ARCHIVED** |

---

**Nota de Gobernanza:** este documento registra **hallazgos → clasificación → decisión → batch → commit** y **no** contiene la evidencia forense detallada ni constituye una autoridad normativa. La evidencia por DF/GF se conserva en `FASE_PPPR_EXIT_REVIEW_EVIDENCE_LOG.md`, de manera incremental e inmutable una vez registrada. Ninguna entrada ni Gate Exit Review se presume ejecutado por crear este esqueleto.`