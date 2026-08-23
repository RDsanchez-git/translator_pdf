# PHASE {FASE} EXECUTION PLAN v{X.Y.Z}
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** {X.Y.Z}
**Status:** {DRAFT | APPROVED | FROZEN}
**Date:** {YYYY-MM-DD}
**Supersedes:** {versión anterior, si aplica}
**Derived From:** {N} NADRs FROZEN + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| {X.Y.Z} | {YYYY-MM-DD} | {Descripción del cambio} |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_{FASE}_MASTER (visión y capacidades)
↓
NADRs {XX}-{YY} (reglas constitucionales permanentes, FROZEN)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_{FASE}_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_{X}_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-08 §5.2 R3` → NADR-08, sección 5.2, regla 3.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN**. Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_{X}_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

```text
DF-{XX} | GF-{XX}
```

**Responsabilidad de este documento:** Identificar el hallazgo y derivarlo al registro.
**Responsabilidad del Findings Register:** Clasificar, resolver o diferir el hallazgo.

### 1.4 Operational Principles

- **Los NADRs no pertenecen a una fase.** Son reglas constitucionales permanentes. Lo que se asigna por fase son sus reglas individuales.
- **El Execution Plan es la única fuente de verdad temporal.** No existen matrices de trazabilidad paralelas.
- **Política de referencias cruzadas:** Una regla puede aparecer en múltiples tareas **únicamente** cuando una tarea la implementa y otra la verifica o completa. Nunca deben existir dos tareas implementando la misma obligación.
- **El estado de una regla es derivado.** Una regla no tiene estado propio. Su estado es el estado de la tarea que la implementa, salvo que esté distribuida (implementada en una tarea, verificada en otra).

### 1.5 Documento Vivo — Convención de Actualización

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §10. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§3)
- Status Dashboard (§6)
- Traceability Appendix (§7)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

---

## 2. GATE {N} — {NOMBRE DEL GATE}

**Objective:** {Qué logra este gate en términos arquitectónicos}
**Execution Mode:** {Secuencial | Paralelo | Mixto}
**Rollback Plan:** {Cómo revertir si algo sale mal}
**Gate Status:** {⏳ PENDING | 🟡 IN PROGRESS | ✅ COMPLETED}

### 2.{X} Wave {N.X} — {NOMBRE DE LA WAVE} ({NADRs afectados})

**Wave Status:** {⏳ PENDING | 🟡 IN PROGRESS | ✅ COMPLETED}
**Fecha de inicio:** {YYYY-MM-DD}
**Fecha de cierre:** {YYYY-MM-DD}

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **{N.X.1}** | {Descripción} | {NADR-XX §Y.Z R1, R2} | {Low/Medium/High/Critical} | {— / Task ID / Gate} | {TODO/IN_PROGRESS/DONE/BLOCKED} |
| **{N.X.2}** | {Descripción} | {NADR-XX §Y.Z R3} | {Risk} | {Deps} | {Status} |

#### Notas de implementación — Task {N.X.1}

> {Se actualiza al completar la Task. Documenta el CÓMO se implementó:
> archivos creados/modificados, decisiones técnicas tomadas,
> tests agregados, validaciones ejecutadas.
> Ejemplo: "FSMStateStore convertido a adaptador pasivo (initialize,
> dispatch, load, get_current_version). TranslationPipeline emite
> comandos explícitos. 274 tests passed, 0 errors pyright."}

#### Notas de implementación — Task {N.X.2}

> {Mismo formato. Se actualiza al completar la Task.}

#### Notas de referencia cruzada (§1.4)

> {Se registra cuando una regla aparece en múltiples Tasks,
> explicando que NO hay doble implementación sino
> preparación/completación.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| {DF-XX} | {Descripción breve} | Findings Register §{N} |

### 2.{Y} Gate {N} Exit Criteria

Todas las reglas de {NADRs} referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- {Criterio de salida 1}
- {Criterio de salida 2}
- {Criterio de salida N}

### 2.{Z} Gate {N} Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas del Gate en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde | {✅/❌} |
| 7 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate {N} | {YYYY-MM-DD} | {X/Y} | {A/B} | {N} | {Observaciones} |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-{XX}** | {Operación} | {Local/Staging/Prod/CI} | {NADR-XX §Y.Z R1} | {Evidencia} | {TODO/DONE/ELIMINADO} |

---

## 5. GLOBAL DoD (Definition of Done)

La Fase {FASE} se considera oficialmente completada cuando:

```text
{All rules in FROZEN NADRs} − {Rules with DONE status in §7} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate {N} | {A} | {X} | {Y} | {Z} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| **TOTAL** | **{A}** | **{X}** | **{Y}** | **{Z}** | {Estado global} |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task (§2.{X}.{Y})
3. Se actualiza el `Derived Status` de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.{Z})

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 7.{N} Gate {N} — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| {NADR-XX §Y.Z R1} | {DONE/DEFERRED/PENDING} | {Wave N.X / Task N.X.Y} | {Breve descripción de cómo se implementó} |
| {NADR-XX §Y.Z R2} | {Status} | {Evidence} | {Notes} |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-{fase}/reviews/FASE_{X}_DEFERRED_FINDINGS_REGISTER.md | Registra los hallazgos identificados durante la durante la implementación de este ADR | ✅ |
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.2.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (implementable / diferido / NAR / limitación)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v{versión}.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas y seguimiento de cumplimiento** se rigen por el Execution Plan (`PHASE_{FASE}_EXECUTION_PLAN.md`).
* Los **hallazgos identificados durante la implementación, su clasificación y resolución** se registran en el Deferred Findings Register (`FASE_{X}_DEFERRED_FINDINGS_REGISTER.md`).

Este documento **no prescribe implementaciones específicas, planificación operacional, criterios de revisión de código ni registro de hallazgos.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

## 10. FUTURE WORK

> {Notas sobre mejoras futuras del proceso de trazabilidad, automatización del appendix, etc.}

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 11.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task (§2.{X}.{Y})
3. Actualizar el `Derived Status` de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§2.{X}.{Z})
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 11.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§2.{Z})
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§3)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 11.5 Al cancelar una operación de Deployment

1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§4)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§10.3)

### 11.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.