# PHASE_PPPR_EXECUTION_PLAN.md — PDF→PDF Product Readiness
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 0.4.0
**Status:** DRAFT — NO APPROVED / NO FROZEN
**Date:** 2026-11-21
**Supersedes:** DRAFT v0.3.0 — revisión focal del Architecture Board sobre HEAD `9c73652dd64c1115a064b9454ee2d7051d0bdc2e`; no sustituye normas FROZEN
**Derived From:** ADR_PPPR_MASTER.md FROZEN; NADR-FPPPR-01/02/03/04 FROZEN; metodología general v1.3.0 FROZEN; `5_METH_EXECUTION_PLAN.md`; HITOs PPPR.0.1–0.9 FROZEN.
**Governance Bridge:** Única fuente de verdad temporal de reglas → Tasks → Waves → Gates → evidencia de implementación. Los NADR conservan autoridad constitucional; ninguna Task aquí autoriza por sí sola código, corpus, egress, pagos, evaluación científica ni merge a `main`.
**Estado de autoridad:** el Architecture Board mantuvo favorable la cascada 6/12/30, **sin aprobación integral**. Su dictamen sobre DRAFT v0.3.0 exige cerrar G3 sin reglas pendientes hasta G5 ni excepción a `5_METH_EXECUTION_PLAN.md`, y sustentar por sujeto y falsador la clasificación histórica F17-BIS/F18. Se preservan las correcciones de G1, DC-04, HEADING físico y candidato científico G6. **No** se autoriza FROZEN, merge, ejecución, corpus privado, egress comercial ni integración a `main`.
**Baseline documental de contraste:** `pdf-pdf-product-readiness@e759a55c18a2c96aa7dc8473d4afd7c48ee7adc2`; `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42` (código auditado por HITOs). Revalidar ambos HEAD antes del PR y antes de ejecutar; no tratar la referencia histórica como checkout activo.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0-DRAFT | 2026-11-21 | Primer plan candidato: 6 Gates, 12 Waves, 30 Tasks; dos reservas del Board; trazabilidad primaria de reglas PPPR, GAP y falsadores; sin implementación ni ensayos. |
| 0.2.0-DRAFT | 2026-11-21 | Corrige G1 sin excepción autoatribuida, individualiza reglas históricas aplicables y excluidas, distingue G3 offline/G5 real, separa evaluación de Product Readiness en G6, reescribe runbook como operaciones de release, minimiza dependencias y separa responsabilidades HEADING; mantiene 6/12/30 y las 40 reglas PPPR intactas. |
| 0.3.0-DRAFT | 2026-11-21 | Revisión focal Board: censo histórico individual 104 (80 A/0 B/24 C), distinción G1 documental/ejecutado, derivación G3/G5, jerarquía PDF físico y candidato científico de G6; pendiente de ratificación. |
| 0.4.0-DRAFT | 2026-11-21 | Dictamen focal Board: G3 solo cierra con reglas propias DONE por falsadores offline suficientes; G5 mantiene prueba comercial separada. Clasificación histórica respaldada por consumidores y falsadores, sin resultados inventados. Estructura y protocolo de documento vivo preservados. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Regla de precedencia y cascada

```text
ROADMAP / PROJECT_SCOPE / ENGINEERING_PRINCIPLES
    ↓
ADR Maestro PPPR FROZEN (DC-01…12)
    ↓
NADR-FPPPR-01…04 FROZEN + contratos F17-BIS/F18 compatibles
    ↓
PHASE_PPPR_EXECUTION_PLAN (ESTE DOCUMENTO — DRAFT)
    ↓
G1 baseline/autoridad → G2 datos/identidades → G3 inferencia/efectos
    ↓
G4 G5/PDF → G5 host/E2E → G6 ciencia/readiness
    ↓
PRs productivos + tests + Exit Review Evidence Log / Findings Register
```

**Hipótesis de granularidad para revisión:** 6 Gates, 12 Waves y 30 Tasks. No deriva mecánicamente de cuatro NADR ni de 13 causas; las dependencias pueden conducir a reajuste antes de aprobación integral del plan. Son unidades de trabajo, **no 30 PR ni 30 commits obligatorios**.
**Gates secuenciales:** ningún Gate N+1 se ejecuta ni se declara aprobado antes del cierre **satisfactorio y autorizado** del gate bloqueante N. Un Gate Exit Review puede quedar realizado con veredicto `FAIL` o `BLOCKED` sin abrir el siguiente gate. Las gestiones externas independientes (custodia, permisos, host, evaluación de proveedor) pueden prepararse en paralelo, sin conceder autoridad operativa, anticipar Tasks bloqueadas ni ocultar restricciones.

**Distinción de actos:** para aprobar integralmente **el documento** basta una ruta de desbloqueo de G1 gobernada, con alternativas legítimas, autoridad y consecuencia `BLOCKED`; **no** se exige haber ejecutado `1.2.1`, materializado físicamente el corpus ni obtenido CI verde. La ejecución y el cierre de G1 requieren esas evidencias **después de la autorización de ejecución**. Aprobación documental, FROZEN, merge, ejecución y permisos comerciales/científicos son actos separados; `main` y PR #66 quedan fuera.

### 1.2 Convenciones de referencias y propiedad

- Identificador canónico: `NADR-FPPPR-XX §5.Y Rn`; no se inventan IDs de reglas. El corpus de NADR FROZEN es su fuente de texto autoritativa; este plan solo asigna responsabilidades y estados.
- Cada regla PPPR tiene exactamente una **Task principal de materialización** en §2; una Task diferente puede verificarla cuando resulte necesario, identificando esa relación como verification, no doble implementación.
- Las reglas históricas se cotejan **individualmente por §5.Y Rn**: §1.6 identifica consumidor, precondición y frontera; §2 asigna Task principal; §7.H fija falsador y evidencia por regla. `A` es aplicable y requiere verificación, no equivale a defecto; `C` excluye por sujeto, no por ausencia de GAP. Cada Gate solo obtiene PASS cuando **todas las reglas con Task principal allí están DONE**, sin obligación pendiente en gate posterior.
- Un identificador PPPR mantiene un único dueño; las verificaciones posteriores, la adecuación de consumidores y los testigos G5/G6 se referencian como **verificación complementaria**, sin segunda implementación de la misma regla.
- Se preservan los **14 GAP-ID P1 OPEN** de PPPR.0.9 §14, con **13 núcleos causales preliminares**; `GAP-0.1-01` y `GAP-0.4-02` comparten causa pero mantienen sus IDs. No son tasks ni findings nuevos.
- `DF-XX` y `GF-XX` solo nacen durante ejecución y se clasifican en el Deferred Findings Register; no crear un segundo registro en este plan.

### 1.3 Dos reservas del Board (vinculantes para este borrador)

**R1 — DC-04 / consumidor real:** la suficiencia normativa **no acredita** la conformidad actual de `compute_ast_hash`, `ChunkPlan`, `ASTRegistry`, snapshots, persistencia, replay ni una caché eventualmente seleccionada. Las Tasks `2.2.1–2.2.3` deben demostrar, antes de adoptar/reutilizar o persistir un resultado, la suficiencia de **cada identidad realmente consumida** para jerarquía H1/H2, contenido Unicode STEM, contexto, idioma, parámetros/versiones y contrato; separar intento operacional y generación. No sustituir por una firma universal ni incorporar caché no conectada por presunción.

**R2 — NADR-FPPPR-01 / ciencia:** las reglas de legitimidad **no aprueban** política concreta de oráculos, modelo de confianza ni umbrales. Su constitución, autoría, independencia y criterios exigen decisión previa de la autoridad competente, externa a este plan. La provisión histórica de 15 PDF (issue #34) no equivale a GT EN→ES. G6 queda BLOCKED donde falten criterios, permisos o corpus; tests exploratorios no certifican. **Una evaluación completa puede producir un resultado científicamente desfavorable:** completar la Task de evaluación no equivale a `PRODUCT_READINESS=PASS`.

### 1.4 Estados, riesgos y pruebas

- Estados de Tasks: `TODO`, `IN_PROGRESS`, `DONE`, `BLOCKED` o `ELIMINADO` con justificación y revisión. Un status textual no es evidencia de una ejecución.
- **Estado de reglas derivado y precedencia:** para `DONE` se exige Task principal `DONE` y evidencia suficiente de verification/validation del **Gate propietario**. Un testigo posterior no puede quedar programado como verificación normativa pendiente de una regla de Gate cerrado. Si una obligación no se puede acreditar en su Gate, este queda `BLOCKED` hasta modificación formal de frontera o decisión metodológica **superior** previa; no se permite PASS parcial. G5 añade pruebas de funcionamiento real y puede detectar regresión que obligue a reabrir un gate anterior, sin fingir que G3 ya probó ese resultado físico.
- Riesgo: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, como priorización del plan **propuesta**, sin reclasificar P1 forenses ni severidades de NADR.
- **Estado global inicial:** TODO / NOT_RUN, Gate 1 PENDING, Gates 2–6 PENDING, ninguna salida PASS. `PRODUCT_READINESS=NOT_CERTIFIED` hasta que exista evaluación válida y decisión competente; **no** equivale a evaluación negativa realizada. No se han ejecutado Pyright, CI, tests, Docker, proveedor, Tectonic, corpus ni benchmarks en esta redacción.
- **Triple separación de resultados:** `Task=DONE` acredita trabajo y evidencia de esa tarea; `Gate Exit Review=REALIZADO` acredita que hubo revisión aun cuando concluya `FAIL`/`BLOCKED`; `PRODUCT_READINESS=PASS` solo procede ante conformidad científica **positiva** en todas las dimensiones exigidas, junto con la satisfacción técnica, permisos y criterios aprobados. Ninguna de las tres etiquetas sustituye otra.

### 1.5 Fuentes y límites

La secuencia productiva auditada es CLI→OCR→G3→G5→PDF en nodo único, no los programas F17/F17-BIS/18 anteriores a convergencia. `NADR-F17BIS-06` PROPOSED no constituye obligación FROZEN; `NADR-F17BIS-04` APPROVED pendiente de formalización editorial tampoco se convierte por reflejo en norma nueva de PPPR. El subconjunto de normas F18 aplicado a autoridad, incertidumbre, durabilidad y observabilidad se justifica por código conectado PPPR.0.5 y DC-07, no por importar una rama antigua.
Las decisiones del ADR Maestro DC-03/08/09/10/12 permanecen invariantes: EN→ES inicial; no egress ni gasto sin permisos; modalidad local CLI en contenedor y un nodo; aceptación científica del PDF final; `DEGRADED` no conforme; custodia del corpus bajo owner.

### 1.6 Clasificación individual de reglas históricas por sujeto y frontera — propuesta

**Criterio:** la falta de un GAP independiente no justifica excluir una regla de un contrato aplicable. Se confrontan el estado FROZEN, el sujeto y la frontera real D-1/D-2. Las cláusulas condicionales siguen condicionadas; no se presume permiso de egress, reintento, gasto ni un defecto nuevo.

**Categorías:** **A:** aplicable, con implementación o verificación por acreditar; **B:** aplicable ya satisfecha, exige evidencia directa de consumidor y pruebas efectivas; **C:** no aplicable al sujeto PPPR, excluida con justificación de frontera. Ninguna B se acredita desde una auditoría documental de código sin tests ejecutados. Las reglas A pueden resultar ya implementadas y no implican ochenta reparaciones.

**Censo para decisión del Board:** 104 reglas examinadas individualmente; **80 A, 0 B, 24 C**. Clasificación propuesta, no ratificación integral ni importación indiscriminada de arquitectura histórica. `1.1.2` debe comprobar aplicabilidad y evidencias de cumplimiento en el HEAD ejecutado.

| Regla histórica FROZEN | Categoría | Task principal si aplicable | Justificación |
|---|---|---|---|
| `NADR-F17BIS-03 §5.1 R1` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.1 R2` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.1 R3` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.1 R4` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.1 R5` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.2 R6` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.2 R7` | A — aplicable, evidencia pendiente | `2.2.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.3 R8` | A — aplicable, evidencia pendiente | `2.2.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.3 R9` | A — aplicable, evidencia pendiente | `2.2.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.4 R10` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.4 R11` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.4 R12` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-03 §5.4 R13` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-16 §5.1 R1` | C — no aplicable a PPPR | — | Identidad del oráculo histórico |
| `NADR-F17BIS-16 §5.1 R2` | C — no aplicable a PPPR | — | Identidad del oráculo histórico |
| `NADR-F17BIS-16 §5.1 R3` | C — no aplicable a PPPR | — | Identidad del oráculo histórico |
| `NADR-F17BIS-16 §5.2 R4` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-16 §5.2 R5` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-16 §5.2 R6` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-16 §5.2 R7` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F17BIS-16 §5.2 R8` | C — no aplicable a PPPR | — | Hash de baseline con identidad de nodo |
| `NADR-F17BIS-16 §5.3 R9` | C — no aplicable a PPPR | — | Estado y sellado de oráculo histórico |
| `NADR-F17BIS-16 §5.3 R10` | C — no aplicable a PPPR | — | Estado y sellado de oráculo histórico |
| `NADR-F17BIS-16 §5.3 R11` | C — no aplicable a PPPR | — | Estado y sellado de oráculo histórico |
| `NADR-F17BIS-16 §5.3 R12` | C — no aplicable a PPPR | — | Estado y sellado de oráculo histórico |
| `NADR-F17BIS-16 §5.4 R13` | C — no aplicable a PPPR | — | Identidad global de baseline científica histórica |
| `NADR-F17BIS-16 §5.4 R14` | C — no aplicable a PPPR | — | Identidad global de baseline científica histórica |
| `NADR-F17BIS-16 §5.4 R15` | C — no aplicable a PPPR | — | Identidad global de baseline científica histórica |
| `NADR-F17BIS-16 §5.4 R16` | C — no aplicable a PPPR | — | Identidad global de baseline científica histórica |
| `NADR-F18-01 §5.1 R1` | C — no aplicable a PPPR | — | Composición de scientific baseline histórica |
| `NADR-F18-01 §5.1 R2` | C — no aplicable a PPPR | — | Composición de scientific baseline histórica |
| `NADR-F18-01 §5.1 R3` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.1 R4` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.1 R5` | C — no aplicable a PPPR | — | Composición de scientific baseline histórica |
| `NADR-F18-01 §5.2 R6` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.2 R7` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.2 R8` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.2 R9` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.3 R10` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.3 R11` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.3 R12` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.3 R13` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.4 R14` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.4 R15` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.4 R16` | A — aplicable, evidencia pendiente | `2.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-01 §5.4 R17` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.4 R18` | C — no aplicable a PPPR | — | Guard/comparación diferencial de modos F18 no adoptados |
| `NADR-F18-01 §5.5 R19` | C — no aplicable a PPPR | — | Identidad científica y de ejecución impuesta a artefactos históricos F18; no equivale a generación EN→ES |
| `NADR-F18-01 §5.5 R20` | C — no aplicable a PPPR | — | Identidad científica y de ejecución impuesta a artefactos históricos F18; no equivale a generación EN→ES |
| `NADR-F18-03 §5.1 R1` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.1 R2` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.1 R3` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.1 R4` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.2 R5` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.2 R6` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.2 R7` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.2 R8` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R9` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R10` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R11` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R12` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R13` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R14` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.3 R15` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.4 R16` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.4 R17` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.4 R18` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.5 R19` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.5 R20` | A — aplicable, evidencia pendiente | `3.1.1` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.6 R21` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.6 R22` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-03 §5.6 R23` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.1 R1` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.1 R2` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.1 R3` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.1 R4` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.2 R5` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.2 R6` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.2 R7` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.3 R8` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.3 R9` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.3 R10` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.4 R11` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.4 R12` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.4 R13` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.4 R14` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.5 R15` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-04 §5.5 R16` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.1 R1` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.1 R2` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.1 R3` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.2 R4` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.2 R5` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.2 R6` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.2 R7` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.3 R8` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.3 R9` | A — aplicable, evidencia pendiente | `5.2.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.3 R10` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.4 R11` | A — aplicable, evidencia pendiente | `3.1.2` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.4 R12` | A — aplicable, evidencia pendiente | `5.2.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.5 R13` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.5 R14` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.5 R15` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |
| `NADR-F18-05 §5.5 R16` | A — aplicable, evidencia pendiente | `3.1.3` | Sujeto compatible con D-1/D-2; verificación/corrección pendiente según condición de la regla |

**Límites específicos:** F17BIS-16 R8 es baseline/oráculo y no impone `node_id` en la generación traducida. F18-01 se aprovecha solo por sus restricciones compatibles de separación conceptual, no por su baseline sellada ni su guard diferencial. F18-03/04/05 aplican a las responsabilidades operacionales cubiertas por DC-07 y a las condiciones efectivamente materializadas; sin activar por presunción mecanismos excepcionales. Las exclusiones conservan íntegra la autoridad histórica.

## 2. GATES, WAVES & TASKS (única secuencia temporal autorizable)

### 2.1 Gate 1 — Baseline, autoridad y preparación

**Objective:** Baseline, autoridad y preparación.
**Execution Mode:** Secuencial para la definición; gestiones externas autónomas pueden avanzar en paralelo.
**Rollback Plan (propuesto):** Solo artefactos documentales hasta aprobación del plan; descartar branch corta sin tocar main.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.1.1 Wave 1.1 — Baseline y trazabilidad

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **1.1.1** | Fijar baseline de producto y gobernanza | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.1/0.9; D-1/D-2 | MEDIUM | — | TODO |
| **1.1.2** | Trazabilidad canónica y frontera de normas | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.9 §14; ADR Maestro §8.1 | HIGH | 1.1.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **1.1.1:** Fijar main de producto, HEAD de la rama PPPR, D-1/D-2 y el alcance CLI→OCR→G3→G5→PDF; dejar delimitado el PR documental #66 sin merge a main. **Falsador / evidencia de salida:** Registro reproducible de SHAs, rutas y diferencia entre gobierno y código; ninguna tarea posterior sobre baseline incierta.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **1.1.2:** Vincular en este único plan las reglas FPPPR FROZEN, reglas históricas estrictamente compatibles, 14 GAP-ID y autoridad del ADR Maestro; identificar implementador único y verificadores. **Falsador / evidencia de salida:** Auditoría de cobertura 40/40 sin doble propiedad, 14 GAP-ID con destino y ningún NADR histórico importado por analogía.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.1.2 Wave 1.2 — Preparación y autorizaciones

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **1.2.1** | Habilitar controles reproducibles | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.8; issue #34 | HIGH | 1.1.1 | TODO |
| **1.2.2** | Registrar autorizaciones y dependencias externas | — (preparación, control o verification; no regla PPPR nueva) | ADR Maestro DC-03/08/10; PPPR-01 §5.2 | CRITICAL | 1.1.2 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **1.2.1:** Caracterizar CI, Pyright, suite exigida y falsadores offline, y **determinar si la ausencia de 15 PDF del issue #34 bloquea realmente el conjunto requerido**. Vía predeterminada: tramitar con el owner/custodio el aprovisionamiento legítimo, con licencias y verificaciones de integridad, para ejecutar la suite completa sin alterar los oráculos. Vía excepcional **solo si la anterior es imposible o no procede**: elevar a la autoridad metodológica/Board una solicitud de alcance inicial verificable y de las pruebas que quedarían pendientes; **el Execution Plan no concede esa excepción**. **Falsador / evidencia de salida:** Suite requerida satisfactoria bajo alcance formal vigente; si faltan corpus o decisión de autoridad, Gate 1 `BLOCKED`, no PASS de una suite parcial. El diagnóstico inicial puede realizarse sin afirmar que CI está verde.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **1.2.2:** Registrar cada dependencia externa con **rol solicitante, autoridad decisora, evidencia exigida y Task/Gate consumidor** (tabla siguiente). Se puede tramitar desde G1 sin requerir que **todas** las autorizaciones de G5/G6 estén concedidas para cerrar G1. **Falsador / evidencia de salida:** estado solicitado/otorgado/denegado/no iniciado atribuible; ninguna solicitud equivale a aprobación, ninguna aprobación se infiere de configuración y el gate consumidor queda `BLOCKED` cuando el permiso efectivo falte.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Registro de desbloqueos de `1.2.2` (estatus inicial: PENDIENTE; ningún permiso otorgado por este plan):**

| Dependencia | Rol que la solicita/gestiona | Autoridad que debe concederla | Evidencia y condición de desbloqueo | Consumidor |
|---|---|---|---|---|
| 15 PDF históricos / suite CI | Staff Engineering / custodia técnica, por canal del owner | Owner/custodio legítimo; autoridad metodológica/Board solo para cualquier excepción de alcance | Disponibilidad e integridad/licencia verificables **o** acto formal de alcance inicial, sin sustituir test omitido por PASS integral | `1.2.1`, G1 y sucesivos |
| Datos y corpus EN→ES científico | Staff Engineering / evaluación, con owner | Owner/custodios de derechos y autoridad científica competente | Uso permitido, origen, oráculos EN→ES elegibles e independencia aprobada | `6.1.1–6.1.3` |
| Proveedor/egress/tratamiento/retención/training | Staff Engineering / G3 y owner | Owner con autoridad sobre datos y destino, conforme DC-03 | Autorización expresa y atribuible por proveedor, finalidad y material | `5.2.3` |
| Presupuesto/coste y modelo permitido | Staff Engineering / G3 y owner | Owner / autoridad presupuestaria delegada acreditable | Límite monetario, condiciones y backend efectivo aprobados | `5.2.3` |
| Host, red, secretos, volúmenes | Staff Engineering / operación, con owner | Owner/autoridad operacional aplicable | Modalidad de nodo único, permisos y controles de entorno acreditados | `5.1.1–5.1.2` |
| Política de autoridad, confianza, criterios científicos | Staff Engineering / evaluación, con owner | Autoridad científica/Board competente, **no** Execution Plan | Política aprobada, independencia, umbrales/criterios y versiones **anteriores** a evaluación certificante | `6.1.1–6.2.2` |

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.1.3 Gate 1 — Exit Criteria (fijos antes de ejecución)

1. Baseline `main` del producto y `pdf-pdf-product-readiness` documentados con SHAs verificables; ruta única ratificada, y ninguna escritura de código en esta etapa.
2. Cobertura normativa trazada sin reglas nuevas: cada obligación PPPR tiene exactamente una Task implementadora y los 14 GAP-ID conservan su identidad y destino; normas F17-BIS/F18 sometidas a compatibilidad real.
3. **Camino predeterminado:** suite y controles de CI/Pyright exigidos completos y en verde tras aprovisionar legítimamente lo necesario para el corpus del issue #34. **Camino excepcional:** solo si la autoridad metodológica/Board decide expresamente **antes del cierre** qué control inicial es exigible y qué queda pendiente, su alcance y efecto sobre gates siguientes; se exige PASS de ese alcance expresamente autorizado y registro visible de toda prueba excluida, **sin llamarlo PASS de suite integral**. Si ninguna de las dos vías produce el cumplimiento verificable exigido: `BLOCKED` y G2 no inicia. El plan no puede elegir por sí mismo una reducción de cobertura.
4. Dependencias externas de custodia, egress, coste, host y autoridad científica registradas con solicitante, autoridad decisora, estado y evidencia/condición de desbloqueo. Se permite tramitación temprana, **no** aprobación inferida ni ejecución anticipada. Las pendientes bloquean exclusivamente los gates que realmente las consumen, salvo el corpus/CI necesario para el propio G1.

#### 2.1.4 Gate 1 — Exit Review

El cierre exige todas las Tasks del Gate `DONE`, reglas implementadas/verificadas con evidencia enlazada en §7, criterios anteriores acreditados, Findings Register y Evidence Log actualizados según metodología. Ninguna dependencia externa pendiente puede sustituirse por fake ni por un CONDITIONAL PASS informal.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate en DONE | NOT_RUN |
| Reglas asociadas implementadas y verificadas | NOT_RUN |
| Gate Exit Criteria satisfechos y evidencia física/lógica | NOT_RUN |
| Hallazgos derivados al register + Exit Review Evidence Log | NOT_RUN |
| Pyright: 0 errors / 0 warnings | NOT_RUN |
| Suite completa exigible por metodología, y regresiones en verde | NOT_RUN |
| Notas y pruebas por Task completas | NOT_RUN |

**Veredicto:** PENDING / NOT_RUN (futuro PASS, CONDITIONAL PASS solo con decisión formal de alcance si procede, o FAIL; nunca de manera retroactiva).
**Fecha de verificación:** —

---

### 2.2 Gate 2 — Ingesta física e identidad

**Objective:** Ingesta física e identidad.
**Execution Mode:** Cascada G2 tras cierre formal de G1; waves 2.1 y 2.2 sucesivas.
**Rollback Plan (propuesto):** Revertir adaptadores/cambios de identidad por PR; mantener compatibilidad/invalidez explícita de claves durables sin migración silenciosa.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.2.1 Wave 2.1 — Procedencia y geometría

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **2.1.1** | Procedencia página–región | NADR-FPPPR-04 §5.1 R1; NADR-FPPPR-04 §5.1 R2; NADR-FPPPR-04 §5.1 R3 | GAP-0.2-01/02; E-0.2-011/012 | HIGH | 1.1.2,1.2.1 | TODO |
| **2.1.2** | Geometría y transformación acreditada | NADR-FPPPR-04 §5.2 R4; NADR-FPPPR-04 §5.2 R5; NADR-FPPPR-04 §5.2 R6; NADR-FPPPR-04 §5.4 R10 | GAP-0.2-02; E-0.2-012/020 | HIGH | 2.1.1 | TODO |
| **2.1.3** | Muestreo estricto e incertidumbre | NADR-FPPPR-04 §5.3 R7; NADR-FPPPR-04 §5.3 R8; NADR-FPPPR-04 §5.4 R9 | GAP-0.2-01; E-0.2-011 | HIGH | 2.1.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **2.1.1:** Garantizar vínculo verificable documento/página/región para nodos simples y multipágina; resolver ambigüedad sin inferir asociación por posición de listas. **Falsador / evidencia de salida:** Nodos multipágina conservan procedencia y un BBox ambiguo se declara indeterminado; ninguna página 0 ficticia acreditada.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **2.1.2:** Hacer coherentes espacios de coordenadas, dimensiones físicas reales, geometrías parciales/representativas y trazabilidad de transformaciones hasta el perfilado; no imponer formato AST nuevo por defecto. **Falsador / evidencia de salida:** Caso 300 pt y X 210 pt=0.70, tamaños mixtos, coordenadas ya relativas y geometría parcial reconocida; 612 no se acepta como valor real universal.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **2.1.3:** Asegurar límite real por primeras N páginas y tratamiento explícito de nodos fronterizos, cobertura parcial y datos no acreditados. **Falsador / evidencia de salida:** Sobrecobertura nunca PASS estricto; descarte de contenido incluido no implica cobertura completa; fallar localmente sin rechazo global arbitrario.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.2.2 Wave 2.2 — Identidad y consumidores

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **2.2.1** | Firma semántica y canonización STEM | NADR-F17BIS-03 §5.1 R1; NADR-F17BIS-03 §5.1 R4; NADR-F17BIS-03 §5.2 R6 | GAP-0.3-01; GAP-0.3-02; E-0.3-010/020 | HIGH | 1.1.2,1.2.1 | TODO |
| **2.2.2** | Identidad de generación frente a intento | NADR-F17BIS-16 §5.2 R4; NADR-F17BIS-16 §5.2 R5; NADR-F17BIS-16 §5.2 R6; NADR-F17BIS-16 §5.2 R7; NADR-F18-01 §5.1 R3; NADR-F18-01 §5.2 R8 | GAP-0.3-01; GAP-0.3-02; DQ-0.9-01 | HIGH | 2.2.1 | TODO |
| **2.2.3** | Verificar y corregir consumidores durables y reutilización | NADR-F17BIS-03 §5.3 R8; NADR-F17BIS-03 §5.3 R9 | E-0.9-027/028; issue #36 como antecedente | CRITICAL | 2.2.1,2.2.2 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **2.2.1:** Resolver sensibilidad a jerarquía y equivalencias Unicode científicamente seguras en la frontera AST→identidad; acordar contrato por propósito sin NFKC indiscriminado. **Falsador / evidencia de salida:** H1/H2 cambia firma si afecta semántica; variantes Unicode admisibles son deterministas; no se alteran símbolos STEM por una equivalencia supuesta. **Testigo de cadena física (HITO PPPR.0.3, E-0.3-019):** PDF fuente con H1/H2/H3 acreditados → extracción / `LayoutBlockDraft` → AST; rechazar un falso PASS si se pierde el nivel antes del AST o se sustituye silenciosamente `UNKNOWN` por H1. Una fuente sin evidencia suficiente de nivel se declara limitada, no se obliga a OCR universal.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F17BIS-03 §5.1 R1`; `NADR-F17BIS-03 §5.1 R2`; `NADR-F17BIS-03 §5.1 R3`; `NADR-F17BIS-03 §5.1 R4`; `NADR-F17BIS-03 §5.2 R6`; `NADR-F17BIS-03 §5.2 R7`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **2.2.2:** Definir proyección técnica de DC-04 sobre generación EN→ES (fuente, idioma, contrato, parámetros/versiones relevantes) y separar intento operacional, oráculo y condiciones incidentales. El contrato alternativo del AST y la baseline histórica no sustituyen esta composición por propósito (F17BIS-16 R4–R7; F18-01 R3/R8). **Falsador / evidencia de salida:** Cambio relevante crea identidad distinta; timeout/reintento no altera por sí solo identidad científica; ningún hash universal obligatorio.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F17BIS-03 §5.1 R5`; `NADR-F17BIS-03 §5.4 R10`; `NADR-F17BIS-03 §5.4 R11`; `NADR-F17BIS-03 §5.4 R12`; `NADR-F17BIS-03 §5.4 R13`; `NADR-F17BIS-16 §5.2 R4`; `NADR-F17BIS-16 §5.2 R5`; `NADR-F17BIS-16 §5.2 R6`; `NADR-F17BIS-16 §5.2 R7`; `NADR-F18-01 §5.1 R3`; `NADR-F18-01 §5.1 R4`; `NADR-F18-01 §5.2 R8`; `NADR-F18-01 §5.4 R16`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **2.2.3:** Implementar la verificación de identidad y corregir **solo donde el consumidor actual demuestre insuficiencia** las claves efectivamente usadas por `ChunkPlan`, `ASTRegistry`, snapshots, persistencia/replay y caché **solo si conectada**; preservar linaje cronológico de firma (F17BIS-03 R8/R9). No activar `CachedLLMProvider` por su existencia. **Falsador / evidencia de salida:** Claves insuficientes no se aceptan como identidad fuerte; falsadores de contexto, idioma, jerarquía, contrato/modelo/versión, storage y replay. Una firma alternativa solo puede servir a un consumidor cuya suficiencia esté probada. No se infiere defecto de caché no seleccionada.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F17BIS-03 §5.3 R8`; `NADR-F17BIS-03 §5.3 R9`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.2.3 Gate 2 — Exit Criteria (fijos antes de ejecución)

1. Procedencia página–región y geometría relativa verificadas en nodos multipágina, dimensiones variables y espacios de coordenadas compatibles; sampler no acepta sobrecobertura como estrictamente conforme.
2. Falsadores `GAP-0.2-01/02` y `GAP-0.3-01; GAP-0.3-02` superados; jerarquía y normalización Unicode STEM segura tienen identidad semántica exigible.
3. Antes de aprobar persistencia/replay/reutilización, identidad **real** por consumidor suficiente para cambios de jerarquía, contexto, idioma, versión y contrato; no se importa firma única ni cache no adoptada.
4. Pyright 0 errors/0 warnings y controles de regresión requeridos en verde; sin cambiar GT ni reducir cobertura para declarar PASS.

#### 2.2.4 Gate 2 — Exit Review

El cierre exige todas las Tasks del Gate `DONE`, reglas implementadas/verificadas con evidencia enlazada en §7, criterios anteriores acreditados, Findings Register y Evidence Log actualizados según metodología. Ninguna dependencia externa pendiente puede sustituirse por fake ni por un CONDITIONAL PASS informal.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate en DONE | NOT_RUN |
| Reglas asociadas implementadas y verificadas | NOT_RUN |
| Gate Exit Criteria satisfechos y evidencia física/lógica | NOT_RUN |
| Hallazgos derivados al register + Exit Review Evidence Log | NOT_RUN |
| Pyright: 0 errors / 0 warnings | NOT_RUN |
| Suite completa exigible por metodología, y regresiones en verde | NOT_RUN |
| Notas y pruebas por Task completas | NOT_RUN |

**Veredicto:** PENDING / NOT_RUN (futuro PASS, CONDITIONAL PASS solo con decisión formal de alcance si procede, o FAIL; nunca de manera retroactiva).
**Fecha de verificación:** —

---

### 2.3 Gate 3 — Inferencia EN→ES y seguridad de efectos

**Objective:** Inferencia EN→ES y seguridad de efectos.
**Execution Mode:** Waves 3.1→3.2, contratos y falsadores **offline** sin efecto comercial. PASS de G3 exige cierre de todas las reglas propias con prueba suficiente; G5 comprueba adicionalmente funcionamiento/disponibilidad efectiva y costes reales, pero **no** es un requisito de cierre diferido de una regla G3. Si falta documentación atribuible de modelo/compatibilidad para la admisión que se pretende, G3 BLOCKED: no se suple por un identificador de modelo ni por una simulación.
**Rollback Plan (propuesto):** Rollback mediante cambios revisados conservando receipts/UNKNOWN; nunca reejecutar un efecto incierto para compensar fallo.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.3.1 Wave 3.1 — Seguridad de efectos F18

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **3.1.1** | Autoridad vigente al efecto externo | NADR-F18-03 §5.1 R1; NADR-F18-03 §5.1 R2 | GAP-0.5-02; E-0.5-020/021 | CRITICAL | 2.2.2,2.2.3 | TODO |
| **3.1.2** | Escalamiento de UNKNOWN | NADR-F18-03 §5.2 R5; NADR-F18-03 §5.2 R7; NADR-F18-03 §5.2 R8; NADR-F18-03 §5.3 R9; NADR-F18-03 §5.3 R10; NADR-F18-03 §5.3 R11; NADR-F18-03 §5.6 R22 | GAP-0.5-01; E-0.5-019/022/026 | HIGH | 3.1.1 | TODO |
| **3.1.3** | Coherencia de sweeper y planos F18 | NADR-F18-04 §5.1 R2; NADR-F18-04 §5.2 R5; NADR-F18-04 §5.2 R7; NADR-F18-04 §5.3 R8; NADR-F18-04 §5.3 R10; NADR-F18-04 §5.5 R15; NADR-F18-04 §5.5 R16; NADR-F18-05 §5.1 R1; NADR-F18-05 §5.1 R2; NADR-F18-05 §5.1 R3; NADR-F18-05 §5.3 R10; NADR-F18-05 §5.5 R13 | GAP-0.5-03; E-0.5-023/032 | HIGH | 3.1.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **3.1.1:** Corregir el chequeo de lease/authority entre espera del semáforo y comienzo del provider I/O, respetando la recuperación ante efecto incierto. **Falsador / evidencia de salida:** Caducidad durante espera impide inicio no autorizado; no se proclama reversibilidad de efecto ya iniciado.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F18-01 §5.3 R10`; `NADR-F18-01 §5.3 R11`; `NADR-F18-01 §5.3 R12`; `NADR-F18-01 §5.3 R13`; `NADR-F18-03 §5.1 R1`; `NADR-F18-03 §5.1 R2`; `NADR-F18-03 §5.1 R3`; `NADR-F18-03 §5.1 R4`; `NADR-F18-03 §5.5 R19`; `NADR-F18-03 §5.5 R20`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **3.1.2:** Conectar escalamiento configurable y evidencia recuperable para estados externos inciertos sin autorizar segundo efecto ciego. **Falsador / evidencia de salida:** UNKNOWN persiste y se expone para revisión; no se reconvierte en retry automático.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F18-03 §5.2 R5`; `NADR-F18-03 §5.2 R6`; `NADR-F18-03 §5.2 R7`; `NADR-F18-03 §5.2 R8`; `NADR-F18-03 §5.3 R9`; `NADR-F18-03 §5.3 R10`; `NADR-F18-03 §5.3 R11`; `NADR-F18-03 §5.3 R12`; `NADR-F18-03 §5.3 R13`; `NADR-F18-03 §5.3 R14`; `NADR-F18-03 §5.3 R15`; `NADR-F18-03 §5.4 R16`; `NADR-F18-03 §5.4 R17`; `NADR-F18-03 §5.4 R18`; `NADR-F18-03 §5.6 R21`; `NADR-F18-03 §5.6 R22`; `NADR-F18-03 §5.6 R23`; `NADR-F18-05 §5.4 R11`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **3.1.3:** Alinear selectores, transiciones, receipts y reporting del sweeper efectivo y recuperación idempotente dentro de las fuentes autoritativas. **Falsador / evidencia de salida:** Estado consultado/transicionado/reportado coincide; crash/restart no inventa resultado ni efecto confirmado.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F18-04 §5.1 R1`; `NADR-F18-04 §5.1 R2`; `NADR-F18-04 §5.1 R3`; `NADR-F18-04 §5.1 R4`; `NADR-F18-04 §5.2 R5`; `NADR-F18-04 §5.2 R6`; `NADR-F18-04 §5.2 R7`; `NADR-F18-04 §5.3 R8`; `NADR-F18-04 §5.3 R9`; `NADR-F18-04 §5.3 R10`; `NADR-F18-04 §5.4 R11`; `NADR-F18-04 §5.4 R12`; `NADR-F18-04 §5.4 R13`; `NADR-F18-04 §5.4 R14`; `NADR-F18-04 §5.5 R15`; `NADR-F18-04 §5.5 R16`; `NADR-F18-05 §5.1 R1`; `NADR-F18-05 §5.1 R2`; `NADR-F18-05 §5.1 R3`; `NADR-F18-05 §5.3 R10`; `NADR-F18-05 §5.5 R13`; `NADR-F18-05 §5.5 R14`; `NADR-F18-05 §5.5 R15`; `NADR-F18-05 §5.5 R16`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.3.2 Wave 3.2 — Contrato G3 EN→ES

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **3.2.1** | Intención lingüística hasta petición real | NADR-FPPPR-03 §5.1 R1; NADR-FPPPR-03 §5.1 R2 | GAP-0.4-03; E-0.4-003/011/012 | HIGH | 2.2.2,3.1.1 | TODO |
| **3.2.2** | Backend vigente y fallback efectivo | NADR-FPPPR-03 §5.2 R3; NADR-FPPPR-03 §5.2 R4 | GAP-0.4-01; GAP-0.4-02; GAP-0.1-01 (estos dos últimos comparten causa) | HIGH | 3.2.1 | TODO |
| **3.2.3** | Admisión integral, presupuesto y rechazo seguro | NADR-FPPPR-03 §5.3 R5; NADR-FPPPR-03 §5.3 R6; NADR-FPPPR-03 §5.3 R7; NADR-FPPPR-03 §5.3 R8; NADR-FPPPR-03 §5.4 R9; NADR-FPPPR-03 §5.4 R10 | GAP-0.4-04; GAP-0.1-01; GAP-0.4-02 (verificación de admisión) | CRITICAL | 3.1.3,3.2.2,1.2.2 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **3.2.1:** Propagar y acreditar origen EN y destino ES desde generación hasta solicitud efectiva sin confiar en configuración o prompt supuesto. **Falsador / evidencia de salida:** Petición efectiva demuestra EN→ES; ausencia de intención requerida produce rechazo antes de I/O.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **3.2.2:** Comprobar **documentalmente** vigencia y capacidades declaradas del backend/modelo candidato y materializar selección/fallback coherentes con el **request construido offline**; si la evidencia documental es insuficiente, el backend es inadmisible. No declarar comprobada la disponibilidad efectiva, aceptación del provider ni el coste real hasta `5.2.3`. **Falsador / evidencia de salida:** `SWITCH_MODEL` modifica modelo, capacidades, límites y autorización en el **request serializado capturado por spy pre-efecto**, o falla antes del envío. Para R3, documento de proveedor fechado y atribuible debe acreditar vigencia, disponibilidad declarada *aplicable* y capacidad de cualquier backend declarado admisible; si no existe, G3 queda BLOCKED para esa admisión. Ninguna llamada comercial, aceptación del proveedor o uptime se atribuye a G3.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **3.2.3:** Implementar y probar **offline** la política de admisión por límites de entrada/salida/ventana total, estimación, credenciales/permisos/precondiciones y presupuesto, con trazabilidad de petición construida, rechazo antes del efecto y frontera de incertidumbre F18. Se prueban negativos con spy/mock sin permitir I/O externo; el permiso real, los cargos y el comportamiento del proveedor se acreditan después en `5.2.3`. **Falsador / evidencia de salida:** contexto+instrucciones+reserva exceden ventana ⇒ `NO DISPATCH`; sin autorización efectiva ⇒ `NO DISPATCH`; un intento posiblemente iniciado no equivale a rechazo. Una simulación favorable no constituye autorización de egress ni presupuesto.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.3.3 Gate 3 — Exit Criteria (fijos antes de ejecución)

1. Todas las Tasks `3.1.1–3.2.3` y **todas las reglas PPPR e históricas cuyo propietario está en Gate 3** deben alcanzar `DONE` con verificación/validación suficiente **antes** de declarar `G3=PASS`; ninguna regla puede quedar PENDING hasta G5.
2. Autoridad vigente al iniciar efecto; UNKNOWN y escalamiento/recuperación sin retry ciego; coherencia de sweeper, FSM, receipts y fuentes locales. Probar offline recuperación y persistencia SQLite bajo modelo de fallos F18: una prueba única de sweeper no acredita las demás reglas de durabilidad, versionado ni observabilidad.
3. Petición efectiva EN→ES capturada antes del despacho con transporte espía; fallback coherente con modelo y límites del request; evidencia documental **auténtica y temporalmente aplicable** de vigencia, disponibilidad declarada y capacidades para admisión; presupuesto, egress y estimaciones verificados. Las precondiciones ausentes provocan `NO DISPATCH`. **Las diez reglas `NADR-FPPPR-03` tienen falsador propio en §2.3.5 y ninguna pasa por declaración.**
4. Pyright 0 errors/0 warnings; suite aplicable, falsadores de G3, Evidence Log y Findings Register completos. G5 requiere luego prueba comercial **distinta** (`5.2.3`) con permiso efectivo, modelo, respuesta, disponibilidad observada y coste, sin sustituir ni postergar el cierre normativo de G3.

#### 2.3.4 Gate 3 — Exit Review

El Gate 3 solo recibe `PASS` si **todas** sus Tasks están `DONE`, y todas sus reglas PPPR e históricas asignadas están `DONE` en §7 tras superar los falsadores de su sujeto. El review registra evidencia contractual/offline con SHA y alcance, **no** disponibilidad ni costes reales. Si falta una evidencia exigible en G3, permanece `BLOCKED`; se solicita cambio formal de frontera o decisión metodológica superior antes de G4, nunca un «cierre por alcance» autoatribuido. Una contradicción posterior en G5 genera finding y exige volver a verificar el contrato afectado, no usar un PASS anterior para ocultarla.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate 3 DONE | ❌ NOT_RUN |
| Reglas con Task principal en Gate 3 todas DONE en §7 | ❌ NOT_RUN |
| Falsadores individuales y criterios G3 completos | ❌ NOT_RUN |
| Hallazgos/Evidence Log y notas con SHAs | ❌ NOT_RUN |
| Pyright 0 errors/0 warnings y suite exigible PASS | ❌ NOT_RUN |
| Exit Review con veredicto real | ❌ NOT_RUN |

**Veredicto:** PENDING / NOT_RUN. **No** se autoriza PASS parcial ni se trasladan reglas G3 pendientes a G5.

#### 2.3.5 Falsadores normativos individuales de NADR-FPPPR-03 para Gate 3

Se examina el **contrato pre-efecto** sobre el request realmente serializado (spy/mock sin red) y su relación con generación, admisión y políticas. Un test negativo sin evidencia positiva suficiente para declarar backend admisible no autoriza una admisión. G5 verifica físicamente el proveedor, egress y coste, como un **sujeto de integración adicional**.

| Regla | Task | Falsador obligatorio para DONE en G3 | Afirmación excluida |
|---|---|---|---|
| `NADR-FPPPR-03 §5.1 R1` | `3.2.1` | Cambiar/omitir origen EN o destino ES en generación invalida la intención o causa rechazo antes de I/O | No acredita calidad lingüística |
| `NADR-FPPPR-03 §5.1 R2` | `3.2.1` | Espiar request efectivo: indica EN→ES igual a generación; configuración `es` no propagada ⇒ rechazo | No equivale a respuesta real |
| `NADR-FPPPR-03 §5.2 R3` | `3.2.2` | Documento fuente de proveedor, fecha, modelo, disponibilidad aplicable y capacidad; invalidarlo ⇒ no declararlo admisible | No demuestra uptime real |
| `NADR-FPPPR-03 §5.2 R4` | `3.2.2` | Forzar fallback: modelo físico capturado y límites, presupuesto y egress reevaluados; alternativa no acreditada ⇒ rechazo | No demuestra ejecución comercial |
| `NADR-FPPPR-03 §5.3 R5` | `3.2.3` | Probar exceso independiente de entrada, salida, ventana total y request agregado ⇒ NO DISPATCH | No infiere límites del provider real |
| `NADR-FPPPR-03 §5.3 R6` | `3.2.3` | Medición/estimación conservadora cubre request serializado y modelo efectivo; discordancia no cubierta ⇒ rechazo | No impone tokenizador universal |
| `NADR-FPPPR-03 §5.3 R7` | `3.2.3` | Autorización ausente/incompatible de destino, datos, fin, retención o training ⇒ pre-efecto bloqueado | No concede egress real |
| `NADR-FPPPR-03 §5.3 R8` | `3.2.3` | Falta autorización monetaria ⇒ NO DISPATCH aun si hay cuota/tokens; fallback exige reevaluación | No acredita cargos ni presupuesto aprobado |
| `NADR-FPPPR-03 §5.4 R9` | `3.2.3` | Admisión vinculada a generación, modelo, idioma, estimador, permisos y request; ruptura de vínculo ⇒ rechazo atribuible | No confunde intento con generación |
| `NADR-FPPPR-03 §5.4 R10` | `3.2.3` | Cada precondición inválida falla antes de envío con causa; efecto incierto sigue UNKNOWN/F18 y nunca «no inicio» | No declara seguro el retry incierto |


### 2.4 Gate 4 — Reconstrucción G5 y PDF

**Objective:** Reconstrucción G5 y PDF.
**Execution Mode:** Waves 4.1→4.2; dependencia de la intención EN→ES y geometría acreditada.
**Rollback Plan (propuesto):** Revertir plantilla/adaptador G5 a contrato previo sin publicar un PDF parcial como conforme.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.4.1 Wave 4.1 — Protección de contenido G5

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **4.1.1** | Proteger CODE/TABLE literal | NADR-FPPPR-02 §5.1 R1; NADR-FPPPR-02 §5.1 R2 | GAP-0.6-01; E-0.6-025 | HIGH | 1.1.2 | TODO |
| **4.1.2** | Preservar TeX legítimo y regiones mixtas | NADR-FPPPR-02 §5.1 R3; NADR-FPPPR-02 §5.1 R4 | GAP-0.6-01; E-0.6-025/032 | HIGH | 4.1.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **4.1.1:** Conservar significado y caracteres significativos de CODE/TABLE evitando que TeX/LaTeX activo interprete caracteres literales. **Falsador / evidencia de salida:** Casos sintéticos con %, _, \, $, &, \textbackslash y texto literal conservan semántica sin activación accidental.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **4.1.2:** Distinguir expresiones científicas TeX legítimas de texto con apariencia de macro y respetar regiones mixtas sin presuponer reconocedor universal. **Falsador / evidencia de salida:** Macro legítima reconocida sigue activa; literal parecido a macro no se activa; mezclas preservan fronteras.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.4.2 Wave 4.2 — Jerarquía y reconstrucción

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **4.2.1** | Traducción de HEADING y jerarquía | NADR-FPPPR-02 §5.2 R5; NADR-FPPPR-02 §5.2 R6; NADR-FPPPR-02 §5.2 R7 | GAP-0.6-02; E-0.3-013/018; E-0.6-026 | HIGH | 2.2.1,3.2.3 | TODO |
| **4.2.2** | Representación espacial, pérdidas y PDF físico sintético | NADR-FPPPR-02 §5.3 R8; NADR-FPPPR-02 §5.3 R9 | GAP-0.2-02 (propagación G5); GAP-0.6-01/02 | HIGH | 2.1.2,4.1.2,4.2.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **4.2.1:** **Dos comprobaciones diferentes dentro de la misma Task integradora. (A) Productor upstream:** los HEADING de lenguaje natural seleccionados para traducción obtienen contenido EN→ES según el contrato de generación, sin dejar texto original por una política `PRESERVE` no autorizada; esta prueba no transfiere a G5 la tarea de traducir. **(B) Consumidor G5:** el texto recibido se preserva sin sustitución silenciosa y se representa con nivel H1/H2/H3 y función jerárquica acreditados; desconocidos no se inventan. **Falsadores / evidencia de salida:** (A) entrada heading EN seleccionada produce texto de salida ES atribuible; (B) G5 conserva exactamente texto recibido y niveles distintos; una prueba G5 no acredita fidelidad lingüística ni certifica el encabezado; **(C) E2E físico** con origen H1/H2/H3 verificable: PDF fuente→extracción→AST→selección/generación EN→ES→G5 conserva niveles; pruebas aisladas con AST preparado/G5 tipado no sustituyen esta cadena. Si la jerarquía fuente no es acreditable, registrar límite, no inventar nivel.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **4.2.2:** Verificar en G5 la obligación de geometría parcial/acreditada materializada en G2 (PPPR-04 R6), la trazabilidad origen→reconstrucción, el reporte de pérdidas y la compilación PDF sintética. **Falsador / evidencia de salida:** Proyección parcial no aparenta totalidad; pérdidas no pasan por producto conforme; PDF sintético validado sin alegar ciencia.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.4.3 Gate 4 — Exit Criteria (fijos antes de ejecución)

1. CODE/TABLE literal resiste TeX accidental y TeX científico legítimo mantiene interpretación válida; regiones mixtas respetan clasificación.
2. Evidencias **separadas** para HEADING: (a) productor upstream selecciona y genera el contenido EN→ES requerido; (b) G5 respeta el contenido efectivamente recibido, función y niveles H1/H2/H3 sin inventarlos; **(c) falsador físico PDF→AST→generación→G5** que detecta pérdida H1/H2/H3 en la extracción (`E-0.3-019`), solo con jerarquía de origen acreditada. G5 no se evalúa como motor de traducción ni oráculo lingüístico.
3. Geometría agregada y pérdidas tienen atribución; PDF sintético compila bajo contratos físicos permitidos, **sin certificación científica**.
4. Falsadores de `GAP-0.6-01/02` y propagación `GAP-0.2-02` con Pyright/suite exigida y Gate Exit Review satisfactorios.

#### 2.4.4 Gate 4 — Exit Review

El cierre exige todas las Tasks del Gate `DONE`, reglas implementadas/verificadas con evidencia enlazada en §7, criterios anteriores acreditados, Findings Register y Evidence Log actualizados según metodología. Ninguna dependencia externa pendiente puede sustituirse por fake ni por un CONDITIONAL PASS informal.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate en DONE | NOT_RUN |
| Reglas asociadas implementadas y verificadas | NOT_RUN |
| Gate Exit Criteria satisfechos y evidencia física/lógica | NOT_RUN |
| Hallazgos derivados al register + Exit Review Evidence Log | NOT_RUN |
| Pyright: 0 errors / 0 warnings | NOT_RUN |
| Suite completa exigible por metodología, y regresiones en verde | NOT_RUN |
| Notas y pruebas por Task completas | NOT_RUN |

**Veredicto:** PENDING / NOT_RUN (futuro PASS, CONDITIONAL PASS solo con decisión formal de alcance si procede, o FAIL; nunca de manera retroactiva).
**Fecha de verificación:** —

---

### 2.5 Gate 5 — Integración y operación real

**Objective:** Integración y operación real.
**Execution Mode:** Waves 5.1→5.2; permisos y modalidad host preceden I/O real.
**Rollback Plan (propuesto):** Revertir despliegue/configuración del nodo, preservar evidencia local y no borrar intentos externos inciertos.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.5.1 Wave 5.1 — Host y modalidad soportada

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **5.1.1** | Contrato de host local soportado | — (preparación, control o verification; no regla PPPR nueva) | ADR Maestro DC-08; PPPR.0.7 | HIGH | 3.2.3,4.2.2,1.2.2 | TODO |
| **5.1.2** | Compose, secretos, persistencia y permisos | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.7; GAP-0.5-03 (verification) | HIGH | 5.1.1,3.1.3 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **5.1.1:** Materializar y verificar la modalidad inicial autorizada CLI dentro del contenedor de un nodo; separar laboratorio de host real. **Falsador / evidencia de salida:** Host real soportado o gate bloqueado; no se presume interfaz Windows→Docker ni modo distribuido.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **5.1.2:** Verificar wiring de Compose, volumen/secretos, red, recuperación y controles efectivos contra el modo aprobado, sin inferirlos del YAML. **Falsador / evidencia de salida:** Preflight y reinicio con condiciones reales autorizadas; no exponer credenciales ni simular permisos como concedidos.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.5.2 Wave 5.2 — Integración completa

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **5.2.1** | E2E sintético de la ruta única | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.1/0.6/0.8 | HIGH | 5.1.2 | TODO |
| **5.2.2** | Falsadores de crash, replay e integración | — (preparación, control o verification; no regla PPPR nueva) | GAP-0.5-01; GAP-0.5-02; GAP-0.5-03; issue #36 (antecedente) | HIGH | 5.2.1,2.2.3 | TODO |
| **5.2.3** | Inferencia real acotada y autorizada | — (preparación, control o verification; no regla PPPR nueva) | ADR Maestro DC-03; PPPR.0.4/0.7 | CRITICAL | 5.2.2,3.2.3,1.2.2 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **5.2.1:** Ejecutar prueba técnica CLI→OCR→G3(fake)→G5→PDF y evidencias tipadas, sin confundir %PDF-/COMPLETED con ciencia. **Falsador / evidencia de salida:** Rutas y estados verificables con fake y PDF físico; NOT_CERTIFIED, no conformidad científica automática.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **5.2.2:** Validar reinicio, lease, UNKNOWN, manifest/receipts y reuso de identidades tras fallos en composición seleccionada. **Falsador / evidencia de salida:** Ningún segundo efecto ciego; replay de misma generación no se confunde con nueva generación; integridad local recuperable.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F18-05 §5.2 R4`; `NADR-F18-05 §5.2 R5`; `NADR-F18-05 §5.2 R6`; `NADR-F18-05 §5.2 R7`; `NADR-F18-05 §5.3 R8`; `NADR-F18-05 §5.3 R9`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **5.2.3:** **Solo con permisos previos efectivos** de proveedor, datos, finalidad, tratamiento/retención/entrenamiento, presupuesto y host, ejecutar un testigo comercial **no certificante**: comprobar disponibilidad física/response del backend, correspondencia del modelo real y fallback, límites efectivos, consumo/coste atribuible y rechazo de alternativas no autorizadas. Si falta cualquier autorización, `BLOCKED` sin petición. **Falsador / evidencia de salida:** Documento/decisión y evidencia anterior al primer token; modelo efectivo y request correlacionables; no equiparar documentación G3 ni fake con disponibilidad real; no certificar calidad EN→ES con un mero resultado de proveedor.
  - **Normas históricas con propiedad principal en esta Task (clasificación A propuesta, no PASS):** `NADR-F18-05 §5.4 R12`. Si no existe trabajo nuevo, se exige igualmente verificar su aplicación por sujeto y evidencia, y conservar complementos de §7.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.5.3 Gate 5 — Exit Criteria (fijos antes de ejecución)

1. CLI dentro de contenedor en un nodo real autorizado verificado; Compose, mounts, secrets, red, fuentes SQLite y restart/rollback con evidencia reproducible.
2. E2E fake y fallos de recuperación pasan sin confundir técnica con conformidad; reporte correcto de ausencia de prueba científica.
3. **Testigo real del proveedor** (`5.2.3`) con modelo efectivo, capacidad/disponibilidad, respuesta y coste observados, solo después de autorizaciones explícitas de destino, finalidad, retención, posible entrenamiento, datos, presupuesto y host; sin ellas, Gate **BLOCKED**, no un PASS por contrato offline. Las condiciones técnicas verificadas en G3 no se describen como prueba comercial ejecutada.
4. Pyright 0 errors/0 warnings, controles y suite aprobada completos, logs y Gate Exit Review verificados.

#### 2.5.4 Gate 5 — Exit Review

El cierre exige todas las Tasks del Gate `DONE`, reglas implementadas/verificadas con evidencia enlazada en §7, criterios anteriores acreditados, Findings Register y Evidence Log actualizados según metodología. Ninguna dependencia externa pendiente puede sustituirse por fake ni por un CONDITIONAL PASS informal.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate en DONE | NOT_RUN |
| Reglas asociadas implementadas y verificadas | NOT_RUN |
| Gate Exit Criteria satisfechos y evidencia física/lógica | NOT_RUN |
| Hallazgos derivados al register + Exit Review Evidence Log | NOT_RUN |
| Pyright: 0 errors / 0 warnings | NOT_RUN |
| Suite completa exigible por metodología, y regresiones en verde | NOT_RUN |
| Notas y pruebas por Task completas | NOT_RUN |

**Veredicto:** PENDING / NOT_RUN (futuro PASS, CONDITIONAL PASS solo con decisión formal de alcance si procede, o FAIL; nunca de manera retroactiva).
**Fecha de verificación:** —

---

### 2.6 Gate 6 — Validación científica y cierre

**Objective:** Validación científica y cierre.
**Execution Mode:** Wave 6.1 crea evidencia sobre referencia aprobada; 6.2 produce dictamen atribuible.
**Rollback Plan (propuesto):** No reescribir resultados/oráculos ni declarar conforme artefactos previamente marcados no certificados; conservar evidencia para recalificación futura.
**Gate Status:** PENDING · NOT_RUN
**Inicio/Cierre:** pendiente; definir en ejecución autorizada.

#### 2.6.1 Wave 6.1 — Evidencia científica

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **6.1.1** | Comprobar autoridad científica y criterios previos | NADR-FPPPR-01 §5.2 R4; NADR-FPPPR-01 §5.2 R5; NADR-FPPPR-01 §5.2 R6 | ADR Maestro DC-09/10; PPPR.0.8 | CRITICAL | 1.2.2 | TODO |
| **6.1.2** | Disponibilidad y elegibilidad de referencias | — (preparación, control o verification; no regla PPPR nueva) | Issue #34; PPPR.0.8; NADR-01 R4/5 (verification) | CRITICAL | 6.1.1 | TODO |
| **6.1.3** | Evaluación de las tres dimensiones del PDF final | NADR-FPPPR-01 §5.1 R2; NADR-FPPPR-01 §5.1 R3; NADR-FPPPR-01 §5.4 R10 | PPPR.0.8; ADR Maestro DC-09 | CRITICAL | 6.1.2,5.2.3,4.2.2 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **6.1.1:** Registrar aprobación competente de política de autoridad, modelo de independencia, criterios y versiones ANTES de evaluación certificante; aplicar controles de rechazo si faltan. El plan no los aprueba unilateralmente. **Falsador / evidencia de salida:** Aprobaciones atribuibles y anteriores a evaluación; cualquier vacío de autoridad bloquea certificación.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **6.1.2:** Preparar materiales científicamente pertinentes y GT EN→ES independientes, con custodia/licencia/identidad acreditadas. Los 15 PDF históricos no son por sí oráculos bilingües. **Falsador / evidencia de salida:** Corpus y referencias elegibles con custodia; sin material ⇒ BLOCKED, sin bajar oráculos históricos.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **6.1.3:** Ejecutar evaluación **válida y atribuible** del PDF final EN→ES sobre fidelidad lingüística, integridad STEM y estructura/visual con referencias y criterios autorizados **previos**; conservar su veredicto científico por dimensión aunque resulte **desfavorable**. **Falsador / evidencia de salida:** **Antes de evaluar**, demostrar un **candidato legítimo al dictamen científico**: PDF final EN→ES de la ruta productiva autorizada o seleccionado por autoridad competente, fuente, generación, versiones de contrato/modelo/parámetros relevantes, condiciones de corpus/datos/proveedor/host, permisos efectivos, referencias independientes y criterios vigentes aprobados *antes* de evaluar. **El testigo técnico/comercial no certificante `5.2.3` no se reutiliza automáticamente**. Sin candidato atribuible `BLOCKED / NOT_CERTIFIED`. `Task 6.1.3=DONE` puede coexistir con dimensión `FAIL` y `PRODUCT_READINESS=FAIL`; fake o `%PDF-` no sustituyen evaluación.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.6.2 Wave 6.2 — Dictamen y cierre

**Wave Status:** PENDING · NOT_RUN · sin autorización de inicio.
**Fechas:** pendiente / pendiente.

| Task | Description | Rules Implemented / frontera | GAP / evidencia | Risk | Deps | Status |
|---|---|---|---|---|---|---|
| **6.2.1** | Atribución, vigencia y resultado de conformidad | NADR-FPPPR-01 §5.1 R1; NADR-FPPPR-01 §5.3 R7; NADR-FPPPR-01 §5.3 R8; NADR-FPPPR-01 §5.3 R9; NADR-FPPPR-01 §5.4 R11 | PPPR.0.8; ADR Maestro DC-12 | CRITICAL | 6.1.3 | TODO |
| **6.2.2** | Exit Review integral, readiness y handoff | — (preparación, control o verification; no regla PPPR nueva) | PPPR.0.9; metodología general §6.5–6.7 | CRITICAL | 6.2.1 | TODO |

**Condiciones de verificación por Task — obligatorias cuando se ejecute:**

- **6.2.1:** Relacionar documentalmente fuente, generación, PDF concreto, criterios/versiones, referencias, **resultado por dimensión** y vigencia; distinguir rechazo científico válido, evaluación incompleta/no certificada y conformidad positiva. Gestionar PDFs DEGRADED como no conformes. **Falsador / evidencia de salida:** una evaluación negativa válida se conserva sin convertirse en readiness positiva; el cambio de criterios no reescribe evidencia; parcial/DEGRADED ≠ conforme.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.
- **6.2.2:** Ejecutar Gate Exit Review integral y reconciliar 40 reglas PPPR, subconjunto F17-BIS/F18 aplicable, 14 GAP-ID, findings, CI/tests, runbook y permisos; elevar **dos resultados distintos**: (i) `GATE_EXIT_REVIEW` realizado con su veredicto operacional y (ii) `PRODUCT_READINESS` científicamente fundamentado. Un resultado científico negativo obliga a `PRODUCT_READINESS=FAIL`, aunque la evaluación haya sido completada correctamente. **Falsador / evidencia de salida:** ninguna Task `DONE`, Exit Review administrativo ni suite verde cambia un resultado científico desfavorable a positivo; decisión final de autoridad competente y sin merge automático a `main`.
  - Notas de implementación: PENDIENTE; registrar rutas, SHAs, pruebas y resultados reales al pasar a DONE; ninguna prueba declarada ejecutada.

**Notas de referencia cruzada y hallazgos:** las referencias a reglas usadas por otros gates como comprobación son **verification**; aquí no se duplica su implementación. No hay DF/GF identificados en este borrador. Toda observación futura se deriva al único Findings Register conforme a §8.

#### 2.6.3 Gate 6 — Exit Criteria (fijos antes de ejecución)

1. Modelo de autoridad de oráculos, independencia y criterios/umbrales científicos concretos aprobados **antes** de evaluación certificante, por autoridad competente distinta del plan; de lo contrario, **BLOCKED**.
2. Corpus EN→ES independiente, licenciado y suficiente para las tres dimensiones; los 15 PDF de issue #34 son históricos y no constituyen oráculos bilingües automáticamente.
3. **Candidato científico evaluable previamente acreditado**, vinculado a la fuente, generación, PDF final de la ruta PPPR, modelo/contrato/versiones, custodia de datos, permisos y criterios/oráculos independientes autorizados. No se adopta automáticamente el testigo no certificante G5. Evaluaciones **válidas** del PDF final EN→ES con resultado separado por dimensión; `6.1.3=DONE` acredita **ejecución evaluativa**, no conformidad positiva. Un resultado científicamente desfavorable válido produce dictamen negativo; evidencia/autoridad insuficiente produce `NOT_CERTIFIED / BLOCKED` (no un rechazo científico artificial).
4. Dictamen atribuible a documento/generación/PDF/versiones; 14 GAP-ID con disposición real, findings, pruebas, Pyright, reglas históricas aplicables, status dashboard y runbook reconciliados. **Condición necesaria para `G6 PASS` con cierre positivo del producto:** conformidad científica `PASS` **en las tres dimensiones** (lingüística, STEM, estructural/visual) bajo autoridad y criterios aprobados **más** cumplimiento técnico/operacional y permisos. La mera realización del Exit Review nunca satisface esa condición. Ante resultado científico negativo: registrar `PRODUCT_READINESS=FAIL`, `G6` sin `PASS` positivo y disponer remediación; ante falta de autoridad/evidencia: `BLOCKED / NOT_CERTIFIED`.

#### 2.6.4 Gate 6 — Exit Review

El cierre exige todas las Tasks del Gate `DONE`, reglas implementadas/verificadas con evidencia enlazada en §7, criterios anteriores acreditados, Findings Register y Evidence Log actualizados según metodología. Ninguna dependencia externa pendiente puede sustituirse por fake ni por un CONDITIONAL PASS informal.

| Control canónico | Estado inicial |
|---|---|
| Tasks del Gate en DONE | NOT_RUN |
| Reglas asociadas implementadas y verificadas | NOT_RUN |
| Gate Exit Criteria satisfechos y evidencia física/lógica | NOT_RUN |
| Hallazgos derivados al register + Exit Review Evidence Log | NOT_RUN |
| Pyright: 0 errors / 0 warnings | NOT_RUN |
| Suite completa exigible por metodología, y regresiones en verde | NOT_RUN |
| Notas y pruebas por Task completas | NOT_RUN |

**Veredicto:** PENDING / NOT_RUN (futuro PASS, CONDITIONAL PASS solo con decisión formal de alcance si procede, o FAIL; nunca de manera retroactiva).
**Fecha de verificación:** —

**Separación obligatoria en G6:** el *Exit Review* debe documentar si se realizó y su veredicto (`PASS / FAIL / BLOCKED`); el **dictamen `PRODUCT_READINESS` es independiente** (`PASS / FAIL / NOT_CERTIFIED / BLOCKED`). `PRODUCT_READINESS=PASS` solo con las tres dimensiones científicas conformes, el conjunto normativo técnico acreditado y las autorizaciones válidas. Un Exit Review realizado con resultado negativo no habilita cierre positivo ni G6 `PASS`.

---

## 3. GATE COMPLETION LOG (Living Document)

Se completa solo después de un Exit Review real, con referencias al Evidence Log/Findings Register y al HEAD evaluado. **Registro de realización del review ≠ aprobación del Gate**. Un Gate con `FAIL`/`BLOCKED` conserva la revisión realizada, pero no se marca COMPLETED satisfactoriamente ni habilita el siguiente. Para G6 se registra además, en evidencia separada, `PRODUCT_READINESS` con su fundamento científico.

| Gate | Fecha cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|---|---|---|---|---|---|
| G1 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |
| G2 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |
| G3 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |
| G4 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |
| G5 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |
| G6 | — | Derivar de §7 | Derivar de §2 | — | PENDING · NOT_RUN |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK (operaciones de release; NO ejecutado)

Este runbook contiene **operaciones de release, preflight, migración autorizada, activación, verificación post-despliegue y rollback**. No desplaza el diseño/codificación de identidad (`2.2.x`), las pruebas E2E/fake (`5.2.1–5.2.2`) ni la evaluación científica (`6.1.x`) desde sus Tasks. Queda fijado antes de iniciar ejecución, bajo permisos de host/datos/proveedor, y no se reescribe durante la fase salvo cancelación justificada por autoridad. **MIG ≠ Task, no altera las 30 unidades ni crea una validación certificante por sí misma.**

| Step | Operación de release (no desarrollo) | Entorno | Reglas / Tasks enlazadas | Evidencia operativa exigida | Estado inicial |
|---|---|---|---|---|---|
| MIG-01 | Preflight de release: comprobar HEAD aprobado, artefactos versionados y ausencia de modificaciones no autorizadas antes de desplegar. | Git/CI | `1.1.1–1.1.2`; gobernanza general | Manifiesto de artefactos, revisión, SHAs, autorización de cambio | TODO / NOT_RUN |
| MIG-02 | Preflight de seguridad y custodia: comprobar permisos efectivos, secretos inyectados sin exposición, mounts, entorno y datos permitidos. | Host autorizado | `1.2.2`, `5.1.1–5.1.2`; PPPR-03 R7/R8 | Evidencia de autorización previa, superficie de datos y rechazo pre-efecto cuando falte | BLOCKED hasta autorización pertinente |
| MIG-03 | Aplicar **solo si está autorizada y resulta necesaria** la migración o invalidación de identidades persistidas establecida y probada en `2.2.1–2.2.3`, con respaldo/restore y guardas contra claves antiguas. | Almacenamiento local | `2.2.1–2.2.3`; DC-04, F17BIS-03/16 aplicables | Acta de cambio, compatibilidad/invalidez, respaldo y rollback reproducible | TODO / NOT_RUN |
| MIG-04 | Resguardar estado recuperable antes de activar versión: backups/snapshots coherentes, receipts, plan/autoridad y comprobación de restauración autorizada. | Host nodo único | `3.1.1–3.1.3`, `5.1.2`; F18-04 aplicable | Evidencia de fuentes autoritativas y restauración sin reejecución externa ciega | TODO / NOT_RUN |
| MIG-05 | Desplegar y activar **en la modalidad aprobada** la versión seleccionada CLI/contenedor/Compose, manteniendo cerrado egress no autorizado. | Host nodo único | `5.1.1–5.1.2`, `5.2.1`; DC-08 | Versión efectiva, health/preflight, configuración permitida, prueba de no egress involuntario | BLOCKED hasta aprobación de host |
| MIG-06 | Habilitar proveedor externo **únicamente** si la activación fue autorizada por destino, datos, fin, retención, entrenamiento y presupuesto; si falta alguna aprobación, mantener deshabilitado. | Host/proveedor autorizado | `5.2.3`, `3.2.3`; PPPR-03 R3–R10 | Referencia al permiso previo y al testigo `5.2.3`; no se ejecuta aquí una segunda evaluación | BLOCKED hasta autorizaciones efectivas |
| MIG-07 | Verificación **post-activación** de artefacto desplegado, identidades/recuperación locales, logs y condiciones de rollback; sin convertir healthchecks en ciencia. | Host autorizado | `5.1.2`, `5.2.1–5.2.2`, `6.2.2` | Concordancia de versión, estados observables, trazabilidad y limitaciones | TODO / NOT_RUN |
| MIG-08 | Disponer rollback/roll-forward de release por autoridad competente ante falla, preservando UNKNOWN, receipts, dictámenes previos y evidencias; entrega operativa solo tras autorización separada. | Host/gobernanza | `3.1.x`, `5.2.2`, `6.2.2`; F18-03/04/05 aplicables | Orden de rollback, integridad de datos, correlación post-rollback, autorización de release | TODO / NOT_RUN |

**Actividades expresamente fuera del runbook:** *planificar* hashes o preparar matrices (Tasks `1.1.x`/`2.2.x`), *ejecutar* pruebas fake o recuperación (Tasks `5.2.1–5.2.2`), ejecutar el testigo comercial como actividad de desarrollo/validación (`5.2.3`) y constituir/evaluar oráculos científicos (`6.1.x`). Las operaciones MIG se limitan a desplegar, comprobar, migrar o revertir **lo ya aprobado y validado**; no autorizan por su cuenta ningún egress, prueba, certificado ni merge.


## 5. GLOBAL DoD (Definition of Done)

El producto no podrá declararse completo por el número de commits, tests unitarios aislados, un PDF con encabezado válido o estados FSM terminales. El cierre de obligaciones se rige por:

```text
Reglas PPPR FROZEN aplicables − reglas implementadas Y verificadas Y validadas = ∅
```

Para cada obligación: (1) una Task principal con implementación commiteada, salvo obligaciones de autoridad externa donde se exige acto aprobatorio verificable; (2) verification técnica superada; (3) validation comportamental superada según sujeto; (4) rastreo a falsador/commit/resultado; (5) sin findings críticos abiertos u ocultos. **Las 40 reglas PPPR y las 80 históricas clase A propuestas** se auditan individualmente, sin contar exclusiones como pendientes ni ampliar sujetos por analogía. Las referencias históricas quedan subordinadas a su cierre de compatibilidad por el Board.

**DoD técnico / documental del programa:** G1–G6 con sus Exit Reviews y salidas acreditadas, Pyright 0 errors/0 warnings, suite requerida aprobada por alcance competente (sin presentar alcance parcial como suite integral), reglas PPPR e históricas compatibles verificadas, permisos aplicables y Findings Register/Evidence Log consistentes. La realización de una evaluación **con resultado desfavorable** puede cerrar correctamente su Task de evaluación, pero **no** satisface un Gate 6 positivo ni Product Readiness.

**DoD de Product Readiness positivo — condición adicional y no sustituible:** `PRODUCT_READINESS=PASS` **si y solo si** existe (a) conformidad científica **positiva en las tres dimensiones** requerida por ADR Maestro DC-09/NADR-FPPPR-01 R2, conforme a políticas, oráculos, independencia y criterios previamente aprobados; (b) conformidad técnica/operativa y reglas requeridas verificadas; (c) permisos de datos, proveedor, presupuesto y host acreditados; (d) dictamen atribuible al **PDF final efectivamente evaluado** y vigente; y (e) decisión competente de cierre. Resultado negativo válido ⇒ `PRODUCT_READINESS=FAIL` (sin reescribir evidencia); ausencia de autoridad, material o evidencia ⇒ `NOT_CERTIFIED`/`BLOCKED`, nunca `PASS` ni `FAIL` científico fabricado. El Gate Exit Review realizado es un acto **distinto** de ese resultado.

Ningún Gate ni este DoD autorizan por sí solos el merge del PR #66 a `main`, la certificación científica, la ejecución comercial o la obtención de corpus privado.

---

## 6. STATUS DASHBOARD (Living Document)

**No hay contadores `DONE` hardcodeados.** El dashboard es una **vista derivada** por consulta al estado de Tasks (§2), propiedad primaria de reglas (§7), pruebas requeridas y veredictos de Gate (§2). Las filas siguientes especifican la consulta a implementar, no una medición ejecutada:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| G1 | `COUNT(task.status == DONE ∧ gate=G1)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| G2 | `COUNT(task.status == DONE ∧ gate=G2)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| G3 | `COUNT(task.status == DONE ∧ gate=G3)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| G4 | `COUNT(task.status == DONE ∧ gate=G4)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| G5 | `COUNT(task.status == DONE ∧ gate=G5)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| G6 | `COUNT(task.status == DONE ∧ gate=G6)` | `COUNT(regla única: owner DONE ∧ verificaciones obligatorias acreditadas, incluidas las de G5)` | `COUNT(regla diferida con autoridad)` | `COUNT(regla sin cierre: owner pendiente ∨ verificación obligatoria pendiente)` | PENDING / NOT_RUN |
| **TOTAL** | `SUM(tasks DONE únicas)` | `COUNT(reglas únicas verificadas)` | `COUNT(reglas formalmente diferidas)` | `COUNT(reglas pendientes)` | PENDING / NOT_RUN |

Actualización solo tras cambios verificables de Tasks: regla derivada de Task principal, sin duplicar recuentos por verification cruzada. Los filtros computan **por separado** las 40 reglas PPPR y las 80 reglas históricas clase A **propuestas** en §1.6/§7; no hacen doble conteo, ni cuentan reglas excluidas como `DEFERRED`. El dashboard representa cierre normativo **solo cuando** Task principal y todas las verificaciones obligatorias constan como acreditadas: en particular, FPPPR-03 R1–R10 no se contabilizan DONE desde G3 si `5.2.3` conserva evidencia requerida pendiente. Es cumplimiento normativo/operativo, **no** indicador de Product Readiness. `PRODUCT_READINESS` se informa separadamente según §5/§2.6.3 y no se deriva de Tasks `DONE`. Un `BLOCKED` de autoridad científica no se reemplaza por `DONE` para conseguir dashboard verde.

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

Este es el **único apéndice de regla → Task principal**; las tablas de §2 constituyen el mapeo de Task→reglas. No replica el texto normativo ni constituye un registro forense paralelo. Estado inicial `PENDING/NOT_RUN`, incluso si el antecedente documental es FROZEN.

| Rule (NADR FROZEN) | Derived Status | Implementation Evidence / Primary Task | Implementation Notes |
|---|---|---|---|
| **NADR-FPPPR-01** | | | |
| `NADR-FPPPR-01 §5.1 R1` | PENDING / NOT_RUN | Task `6.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.1 R2` | PENDING / NOT_RUN | Task `6.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.1 R3` | PENDING / NOT_RUN | Task `6.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.2 R4` | PENDING / NOT_RUN | Task `6.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.2 R5` | PENDING / NOT_RUN | Task `6.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.2 R6` | PENDING / NOT_RUN | Task `6.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.3 R7` | PENDING / NOT_RUN | Task `6.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.3 R8` | PENDING / NOT_RUN | Task `6.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.3 R9` | PENDING / NOT_RUN | Task `6.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.4 R10` | PENDING / NOT_RUN | Task `6.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-01 §5.4 R11` | PENDING / NOT_RUN | Task `6.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| **NADR-FPPPR-02** | | | |
| `NADR-FPPPR-02 §5.1 R1` | PENDING / NOT_RUN | Task `4.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.1 R2` | PENDING / NOT_RUN | Task `4.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.1 R3` | PENDING / NOT_RUN | Task `4.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.1 R4` | PENDING / NOT_RUN | Task `4.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.2 R5` | PENDING / NOT_RUN | Task `4.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.2 R6` | PENDING / NOT_RUN | Task `4.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.2 R7` | PENDING / NOT_RUN | Task `4.2.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.3 R8` | PENDING / NOT_RUN | Task `4.2.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-02 §5.3 R9` | PENDING / NOT_RUN | Task `4.2.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| **NADR-FPPPR-03** | | | |
| `NADR-FPPPR-03 §5.1 R1` | PENDING / NOT_RUN | Task `3.2.1` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.1 R2` | PENDING / NOT_RUN | Task `3.2.1` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.2 R3` | PENDING / NOT_RUN | Task `3.2.2` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.2 R4` | PENDING / NOT_RUN | Task `3.2.2` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.3 R5` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.3 R6` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.3 R7` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.3 R8` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.4 R9` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| `NADR-FPPPR-03 §5.4 R10` | PENDING / NOT_RUN | Task `3.2.3` — evidencia no disponible | G3 Task principal y pruebas offline; **verificación complementaria obligatoria `5.2.3`** para propiedades efectivas requeridas de proveedor/request/permiso/coste. `PENDING` hasta ambas evidencias. |
| **NADR-FPPPR-04** | | | |
| `NADR-FPPPR-04 §5.1 R1` | PENDING / NOT_RUN | Task `2.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.1 R2` | PENDING / NOT_RUN | Task `2.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.1 R3` | PENDING / NOT_RUN | Task `2.1.1` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.2 R4` | PENDING / NOT_RUN | Task `2.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.2 R5` | PENDING / NOT_RUN | Task `2.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.2 R6` | PENDING / NOT_RUN | Task `2.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.3 R7` | PENDING / NOT_RUN | Task `2.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.3 R8` | PENDING / NOT_RUN | Task `2.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.4 R9` | PENDING / NOT_RUN | Task `2.1.3` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |
| `NADR-FPPPR-04 §5.4 R10` | PENDING / NOT_RUN | Task `2.1.2` — evidencia no disponible | Sin cambios implementados; falsadores en §2 |

### 7.H Trazabilidad individual de reglas históricas aplicables (clase A; pendiente)

**Correspondencia §1.6↔§2↔§7:** las 80 reglas A se trazan individualmente aquí y en las notas de Task §2. Las 24 reglas C no son obligaciones PPPR ni aparecen como PENDING; B=0 hasta que exista evidencia verificable del consumidor real. `PENDING/NOT_RUN` no implica un nuevo GAP ni incumplimiento presumido.

| Regla FROZEN aplicable | Derived Status | Task principal | Verificación complementaria exigida | Límite de evidencia |
|---|---|---|---|---|
| `NADR-F17BIS-03 §5.1 R1` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.1 R2` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.1 R3` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.1 R4` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.1 R5` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.2 R6` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.2 R7` | PENDING / NOT_RUN | `2.2.1` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.3 R8` | PENDING / NOT_RUN | `2.2.3` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.3 R9` | PENDING / NOT_RUN | `2.2.3` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.4 R10` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.4 R11` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.4 R12` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-03 §5.4 R13` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/G2; 5.2.2 en replay si procede · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-16 §5.2 R4` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3; 5.2.2 sobre reuso durable · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-16 §5.2 R5` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3; 5.2.2 sobre reuso durable · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-16 §5.2 R6` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3; 5.2.2 sobre reuso durable · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F17BIS-16 §5.2 R7` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3; 5.2.2 sobre reuso durable · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.1 R3` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.1 R4` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.2 R8` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.3 R10` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.3 R11` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.3 R12` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.3 R13` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-01 §5.4 R16` | PENDING / NOT_RUN | `2.2.2` — evidencia NO disponible | 2.2.3/5.2.2: identidad versus intento · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.1 R1` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.1 R2` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.1 R3` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.1 R4` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.2 R5` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.2 R6` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.2 R7` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.2 R8` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R9` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R10` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R11` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R12` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R13` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R14` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.3 R15` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.4 R16` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.4 R17` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.4 R18` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.5 R19` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.5 R20` | PENDING / NOT_RUN | `3.1.1` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.6 R21` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.6 R22` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-03 §5.6 R23` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.2.2: UNKNOWN/crash/autoridad; excepción solo si autorizada · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.1 R1` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.1 R2` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.1 R3` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.1 R4` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.2 R5` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.2 R6` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.2 R7` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.3 R8` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.3 R9` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.3 R10` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.4 R11` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.4 R12` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.4 R13` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.4 R14` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.5 R15` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-04 §5.5 R16` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2 y 5.2.2: estado recuperable y proyecciones · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.1 R1` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.1 R2` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.1 R3` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.2 R4` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.2 R5` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.2 R6` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.2 R7` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.3 R8` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.3 R9` | PENDING / NOT_RUN | `5.2.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.3 R10` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.4 R11` | PENDING / NOT_RUN | `3.1.2` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.4 R12` | PENDING / NOT_RUN | `5.2.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.5 R13` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.5 R14` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.5 R15` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |
| `NADR-F18-05 §5.5 R16` | PENDING / NOT_RUN | `3.1.3` — evidencia NO disponible | 5.1.2/5.2.2; 5.2.3 solo cuando su sujeto requiera proveedor/métricas · NOT_RUN | Aplicabilidad por sujeto; falsador conforme a precondición real, sin inferir fallo observado |

**Estado derivado:** regla DONE únicamente cuando la Task principal y sus verificaciones de consumidor pertinentes estén acreditadas. Si la condición de la norma no se materializa, registrar la justificación verificable; la mera ausencia de un GAP no permite excluirla. No se ejecutarán efectos externos para simular obligaciones condicionales sin permiso.

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos que **surjan de la implementación** se derivarán, cuando comience esa etapa, a un único register propio de PPPR en `docs/architecture/adr/pdf-pdf-product-readiness/reviews/` con nomenclatura excepcional PPPR que apruebe la autoridad aplicable conforme a metodología general §§3.5/6.5–6.7. No se crea ahora para rellenar plantillas. El *Exit Review Evidence Log* se construirá incrementalmente por Gate y se congelará al cierre; los resultados/batches operativos irán al Deferred Findings Register.

Este plan registra únicamente referencias a `DF-XX`/`GF-XX` cuando existan, nunca clasificación, remediación ni historial duplicados. La ausencia actual de findings nuevos significa **NOT_RUN**, no cero defectos.

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

- `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN fija Audit First, secuencia ADR→NADR→Execution Plan→código→Verification/Validation y gates de revisión.
- `docs/architecture/5_METH_EXECUTION_PLAN.md` establece secciones 1–11, Rule-Centric Traceability, gate criteria inmutables una vez iniciados, runbook, Dashboard derivado, Evidence Log y Findings Register.
- `ADR_PPPR_MASTER.md` FROZEN fija decisiones DC-01…12, entre ellas DC-04 identidad por propósito, DC-09 autoridad científica y DC-03 datos/egress.
- `NADR-FPPPR-01/02/03/04` FROZEN gobiernan obligaciones permanentes sin pertenecer a Gates o Waves; este plan es su única proyección temporal, no un nuevo NADR ni una autorización de cambiarlos.
- HITOs PPPR.0.1–0.9 FROZEN son evidencia forense; 14 GAP-ID P1 OPEN no quedan resueltos por la redacción del plan.
- El Architecture Board ratificó **suficiencia normativa para planificar** con las reservas DC-04 y científica; no hay autorización de implementación, inferencia comercial, pruebas sobre corpus privado, certificación ni integración PR #66 a `main`.

---

## 10. FUTURE WORK (no nuevas obligaciones)

**Antes de aprobación documental del DRAFT:** (a) revisar contra HEAD las 30 Tasks, las 40 reglas PPPR y la clasificación histórica individual; (b) **aprobar una ruta de desbloqueo gobernada de G1**, con aprovisionamiento autorizado como predeterminado o solicitud a autoridad metodológica de excepción formal, definiendo autoridad, dependencias y efecto `BLOCKED`; **no exigir la ejecución previa de `1.2.1`, el corpus materializado ni CI en verde**; (c) aprobar el alcance offline de G3 y los complementos efectivos de G5; (d) validar falsador físico de HEADING y procedencia del candidato científico; (e) verificar criterios y runbook. **Durante la ejecución posterior de G1**, deberá completarse realmente la vía autorizada, pasar pruebas exigibles y documentar su evidencia; si no, `BLOCKED`. Ninguna de estas rutas autoautoriza excepción, implementación ni evaluación científica. Cualquier decisión arquitectónica genuinamente nueva retorna al Board, no se introduce como Task silenciosa. Tras aprobación integral, PR del plan y autorización de merge interno siguen siendo actos separados; cualquier código requiere autorización posterior conforme a la cadena aprobada.

---

## 11. DYNAMIC UPDATE PROTOCOL

### 11.1 Inicio de una Task
Cambiar `TODO→IN_PROGRESS` en §2 solo cuando Execution Plan esté aprobado, dependencias cubiertas y trabajo autorizado; anotar HEAD, dueño y referencia normativa sin editar criterios de Gate.

### 11.2 Completar una Task
Con commit/PR comprobado, registrar archivos y mecanismos en notas §2, verification/validation (incluida Pyright/suite), derivar estado de reglas §7 y recalcular Dashboard §6 desde la misma fuente temporal.

### 11.3 Nuevo finding
Identificar `DF-XX`/`GF-XX`, referenciarlo en la Wave, registrar evidencia inmediatamente en Exit Review Evidence Log y derivar decisión/classificación al Deferred Findings Register. Si bloquea, Task `BLOCKED`.

### 11.4 Cerrar Gate
Registrar Exit Review con fecha/SHAs, Findings Register/Evidence Log y su **veredicto real**. Actualizar Gate `COMPLETED` y habilitar Gate sucesor solo si se acreditan todos sus criterios de cierre bajo el alcance vigente; un review realizado con `FAIL`/`BLOCKED` queda registrado pero no libera el gate. En G6 registrar **además** `PRODUCT_READINESS` por separado, que exige ciencia positiva en las tres dimensiones. `CONDITIONAL PASS` solo bajo decisión competente expresa de alcance y nunca reemplaza un criterio científico, permiso o requisito de producto.

### 11.5 Cancelar una migración
Marcar `ELIMINADO` en §4 solo con causa/autoridad registradas; si afecta una regla, abrir finding y decisión formal, sin eliminar retrospectivamente trazabilidad.

### 11.6 Prohibiciones
- No modificar Gate Exit Criteria después de comenzar el Gate.
- No añadir reglas sin NADR FROZEN ni reescribir el corpus normativo.
- No inventar estados PASS, métricas, reviews, credenciales, oráculos, criterio científico o autorizaciones.
- No borrar Tasks: si devienen innecesarias, registrar cancelación y su efecto sobre la propiedad de reglas antes de avanzar.
- No registrar en este documento clasificación ni resolución de findings que pertenezcan al Register.
- No fusionar PR #66 a `main` ni iniciar pruebas/operaciones comerciales sin gates y permisos específicos.

---

**Nota final de gobernanza:** `DRAFT v0.3.0`, **no aprobado integralmente** ni autorizado para ejecución, FROZEN o merge. Se conserva la hipótesis 6/12/30 tras la revisión focal del Board. Las reservas DC-04 y científica, la vía legítima de G1, las reglas históricas por consumidor, la frontera offline G3/real G5 y la prohibición de equiparar evaluación realizada con Product Readiness positiva son condiciones explícitas. Ningún informe técnico/fake será presentado como conformidad científica del PDF final EN→ES.