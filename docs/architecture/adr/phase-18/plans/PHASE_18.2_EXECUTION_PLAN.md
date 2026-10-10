# PHASE 18.2 EXECUTION PLAN v1.2.0

## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.2.0

**Status:** DRAFT

**Date:** 2026-10-11

**Supersedes:** v1.1.0

**Derived From:** 3 NADRs FROZEN (NADR-F18-03 v1.2.0, NADR-F18-04 v1.1.1, NADR-F18-05 v1.3.0) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0

**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Subfase 18.2. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

---

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-10 | Emisión inicial. 6 Gates, 12 Waves, 38 Tasks. |
| 1.1.0 | 2026-10-11 | Corrección de conteo de reglas: 55 reglas totales. |
| 1.2.0 | 2026-10-11 | **Correcciones de integridad estructural y gobernanza:** (1) Añadida R11 de NADR-F18-05 al Audit Board. (2) Corregida numeración contradictoria R8-R11 en Gate 3. (3) Eliminada R14 de Task 1.2.1 (doble autoridad). (4) Diferenciada implementación vs verificación de R9 en Tasks 2.2.1/2.2.2. (5) Corregidas dependencias de Gate 3 (depende de Gates 1 y 2). (6) Eliminada presuposición de feature flags en MIG-05. (7) Reformulada Task 4.2.1 para acotar condiciones de medición. (8) Reformuladas Tasks 5.1.2/5.1.4 para respetar tres disposiciones de diferimientos. (9) Añadida sección "Derivación del estado DONE" en §5. (10) Corregidos contadores: 6 Gates, 13 Waves, 39 Tasks. (11) Reformulado §9 para aclarar alcance de prescripción. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F18_MASTER (visión y capacidades)
↓
ADR_F18.2 v3.3.0 FROZEN (decisión de subfase)
↓
NADRs FROZEN (reglas constitucionales permanentes)
  - NADR-F18-03 v1.2.0: 23 reglas (autoridad y efectos inciertos)
  - NADR-F18-04 v1.1.1: 16 reglas (persistencia e idempotencia local)
  - NADR-F18-05 v1.3.0: 16 reglas (observabilidad de duplicación)
  - Total: 55 reglas
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_18.2_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_18.2_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
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

Ejemplos:
- `NADR-F18-03 §5.1 R1` → NADR-F18-03, sección 5.1, regla 1
- `NADR-F18-04 §5.2 R5` → NADR-F18-04, sección 5.2, regla 5
- `NADR-F18-05 §5.3 R8` → NADR-F18-05, sección 5.3, regla 8

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN**. Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_18.2_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

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

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §11. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

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

**Correcciones metodológicas aplicadas al template:**
- §9: Corregido "Este ADR" → "Este Execution Plan" (el template original contenía error editorial).
- §11.5: Corregida referencia de §10.3 → §11.3 (el template original contenía error de numeración).

---

## 2. GATES, WAVES & TASKS

### Gate 0 — Baseline & Contract Readiness

**Objective:** Establecer una baseline verificable del execution plane existente, auditar rutas reales de ejecución contra decisiones FROZEN, y cerrar la preparación contractual de implementación.

**Execution Mode:** Secuencial, con auditorías independientes en paralelo cuando corresponda.

**Rollback Plan:** Ninguna modificación funcional activada. Si falla el gate, se corrige la planificación, no se modifican NADRs congelados.

**Gate Status:** ⏳ PENDING

---

#### Wave 0.1 — Rule & Evidence Mapping (NADR-F18-03, NADR-F18-04, NADR-F18-05)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **0.1.1** | Extraer inventario exhaustivo de reglas de NADR-F18-03/04/05 y construir mapeo inicial Rule → Task, sin duplicar autoridades de implementación. Verificar que cada una de las 55 reglas tiene una task implementadora designada o una justificación explícita de cumplimiento preexistente. | Trazabilidad completa a 55 reglas | Low | — | TODO |
| **0.1.2** | Auditar rutas reales de ejecución (lease, reconciler, journal, proyecciones, telemetría, conexiones de almacenamiento) contra las decisiones FROZEN de ADR_F18.2 v3.3.0. Documentar brechas verificadas entre estado actual y contrato normativo. | — | Medium | Task 0.1.1 | TODO |

**Notas de implementación — Task 0.1.1**

> {Se actualiza al completar la Task. Documenta el inventario de reglas extraído, el mapeo Rule → Task construido, y la validación de completitud.}

**Notas de implementación — Task 0.1.2**

> {Se actualiza al completar la Task. Documenta las rutas auditadas, las brechas identificadas y la evidencia de verificación.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 0.2 — Operational Baseline (Todos los NADRs)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **0.2.1** | Ejecutar y registrar baseline funcional y estática: suite completa de tests (854 tests), Pyright (0 errors, 0 warnings), import-linter (4 contratos KEPT), escenarios de chaos existentes (game_day_1), estado de migraciones de esquema. Documentar evidencia reproducible pre-cambio. | — | Low | Task 0.1.2 | TODO |
| **0.2.2** | Establecer matrices de escenarios de fallo (terminación coordinada, SIGKILL, crash pre-efecto, crash post-efecto/pre-journal, crash post-journal/pre-proyección, pérdida de autoridad), responsabilidades de prueba, compatibilidad de datos y preflight de rollback/recovery. Aprobar contratos de validación. | — | Medium | Task 0.2.1 | TODO |

**Notas de implementación — Task 0.2.1**

> {Se actualiza al completar la Task. Documenta el baseline ejecutado: número de tests, resultados de Pyright, resultados de import-linter, estado de game_day_1, versión de esquemas SQLite.}

**Notas de implementación — Task 0.2.2**

> {Se actualiza al completar la Task. Documenta las matrices de escenarios establecidas, las responsabilidades de prueba asignadas y los contratos de validación aprobados.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 0 Exit Criteria

Este Gate no implementa reglas normativas. Sus criterios son de preparación:

- Corpus de 55 reglas FROZEN identificado sin omisiones ni identificadores inventados.
- Cada obligación nueva tiene una task implementadora designada o una justificación explícita de cumplimiento preexistente que se verificará en Gates posteriores.
- Baseline reproducible documentada (tests, Pyright, import-linter, game_day_1, esquemas), sin atribuir a los datos iniciales garantías que no demuestran.
- Inventario de dependencias y riesgos de migración aprobado.
- No hay conflicto abierto con las decisiones de DC-08 ni con los límites congelados de F18.1.
- Matrices de escenarios de fallo establecidas y contratos de validación aprobados.

#### Gate 0 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Inventario de 55 reglas completado y validado | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings (baseline preservada) | {✅/❌} |
| 6 | Tests: suite completa en verde (854 tests, baseline preservada) | {✅/❌} |
| 7 | Import-linter: 4 contratos KEPT / 0 BROKEN (baseline preservada) | {✅/❌} |
| 8 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

### Gate 1 — Execution Authority & Conservative Recovery

**Objective:** Materializar la autoridad pre-efecto y la recuperación de efectos inciertos gobernadas por NADR-F18-03. Garantizar que ningún efecto externo se inicie sin autoridad recuperable y que el reconciler no reejecute automáticamente operaciones con efecto externo incierto.

**Execution Mode:** Mixto; Wave 1.1 y Wave 1.2 pueden ejecutarse en paralelo, pero Wave 1.2 depende conceptualmente de los contratos establecidos en Wave 1.1.

**Rollback Plan:** Preservar el modelo de datos compatible y utilizar activación controlada. No restaurar un reconciler que vuelva a exponer operaciones inciertas a duplicación automática como estrategia de rollback de producción. Rollback de código no significa restaurar una condición operacional insegura.

**Gate Status:** ⏳ PENDING

---

#### Wave 1.1 — Pre-effect Authority (NADR-F18-03 §5.1, §5.2)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Verificar y completar la autoridad recuperable antes del efecto externo, reutilizando el lease existente en chunk_tasks. Implementar persistencia de lease antes de `execute()` y verificación de vigencia. | NADR-F18-03 §5.1 R1, R2, R4 | High | Gate 0 | TODO |
| **1.1.2** | Materializar el tratamiento de autoridades caducadas u obsoletas, con fencing local verificable. Implementar detección de pérdida/expiración de autoridad durante ejecución del efecto externo. | NADR-F18-03 §5.1 R3 | High | Task 1.1.1 | TODO |
| **1.1.3** | Materializar los contratos de clasificación semántica: resultado confirmado localmente, no inicio demostrablemente verificado, e incertidumbre sobre ejecución o resultado. Implementar distinción sin exigir enums físicos específicos. | NADR-F18-03 §5.2 R5, R6, R7, R8 | High | Task 1.1.1 | TODO |

**Notas de implementación — Task 1.1.1**

> {Se actualiza al completar la Task. Documenta cómo se implementó la persistencia de lease antes del efecto externo, los archivos creados/modificados, las decisiones técnicas tomadas, los tests agregados.}

**Notas de implementación — Task 1.1.2**

> {Se actualiza al completar la Task. Documenta cómo se implementó la detección de pérdida de autoridad, los mecanismos de fencing local, los tests de concurrencia y pérdida de lease.}

**Notas de implementación — Task 1.1.3**

> {Se actualiza al completar la Task. Documenta cómo se implementó la clasificación semántica, la representación de las tres categorías, los tests de clasificación y ausencia de inferencias indebidas.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 1.2 — Conservative Reconciliation (NADR-F18-03 §5.3, §5.4, §5.5, §5.6)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Corregir las rutas de reconciliación que puedan convertir una incertidumbre externa en reejecución automática. Implementar prohibición de reejecución automática de operaciones con resultado externo incierto. | NADR-F18-03 §5.3 R9, R12, R13, R15 | Critical | Task 1.1.3 | TODO |
| **1.2.2** | Materializar trazabilidad recuperable de incertidumbre: identificador del intento original, momento de primera detección de la incertidumbre, historial de sweeps de recuperación. Implementar mecanismo de escalamiento configurable que impida olvido silencioso. | NADR-F18-03 §5.3 R10, R11 | High | Task 1.2.1 | TODO |
| **1.2.3** | Integrar la disposición autorizada y las reejecuciones excepcionales con autorización explícita y riesgo aceptado. Implementar contabilización de reejecuciones excepcionales. No prometer resolución en tiempo finito. | NADR-F18-03 §5.3 R14, §5.6 R21, R22, R23 | High | Task 1.2.2 | TODO |
| **1.2.4** | Implementar resolución por evidencia externa verificable cuando exista. Prohibir usar ausencia de evidencia como fundamento para asumir que el efecto externo no ocurrió. No asumir capacidades del proveedor sin verificación previa. | NADR-F18-03 §5.4 R16, R17, R18 | Medium | Task 1.2.1 | TODO |
| **1.2.5** | Preservar la distinción entre identidad de intento (autoridad de ejecución) e identidad científica (contrato de identidad congelado). Implementar verificabilidad de la preservación de correlación cuando el contrato lo exija. | NADR-F18-03 §5.5 R19, R20 | Medium | Task 1.1.1 | TODO |

**Notas de implementación — Task 1.2.1**

> {Se actualiza al completar la Task. Documenta cómo se corrigieron las rutas de reconciliación, la prohibición de reejecución automática, los tests de no replay bajo incertidumbre.}

**Notas de implementación — Task 1.2.2**

> {Se actualiza al completar la Task. Documenta cómo se implementó la trazabilidad de incertidumbre, el mecanismo de escalamiento, los tests de recuperación y escalamiento.}

**Notas de implementación — Task 1.2.3**

> {Se actualiza al completar la Task. Documenta cómo se integró la disposición autorizada, la contabilización de excepciones, los tests de autorización y control de excepciones.}

**Notas de implementación — Task 1.2.4**

> {Se actualiza al completar la Task. Documenta cómo se implementó la resolución por evidencia externa, los tests de resolución con y sin evidencia.}

**Notas de implementación — Task 1.2.5**

> {Se actualiza al completar la Task. Documenta cómo se preservó la distinción de identidades, los tests de compatibilidad con identidad científica.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 1 Exit Criteria

Todas las reglas de NADR-F18-03 §5.1, §5.2, §5.3, §5.4, §5.5, §5.6 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- Ningún efecto externo se inicia sin la autoridad recuperable exigida (R1, R2, R4).
- La pérdida o expiración de autoridad durante una operación externa es detectable por el sistema (R3).
- La autoridad recuperable preserva el identificador del intento de ejecución como distinto de la identidad científica (R4).
- La recuperación distingue entre existencia de resultado local recuperable, ausencia demostrable de inicio del efecto externo e incertidumbre sobre su ejecución o resultado (R5).
- Una operación clasificada como incierta no se trata como equivalente a una operación cuyo no inicio está demostrablemente verificado (R6).
- La ausencia de resultado local registrado no se interpreta automáticamente como prueba de que el efecto externo no ocurrió (R7).
- Ante evidencia insuficiente, la clasificación conservadora como incierta es el comportamiento por defecto (R8).
- Una operación con resultado externo incierto no es reejecutada automáticamente por el mecanismo de recuperación (R9).
- Toda operación con resultado externo incierto conserva trazabilidad suficiente (R10) y dispone de mecanismo de escalamiento configurable (R11).
- El escalamiento de una operación incierta no se interpreta como evidencia de que la reejecución sea segura (R12).
- La reejecución de una operación con resultado externo incierto requiere autorización explícita (R13) y se contabiliza como excepción arquitectónicamente autorizada (R14).
- La autorización excepcional de reejecución requiere aceptación explícita del riesgo de duplicación (R15).
- Cuando existe evidencia externa verificable, el sistema resuelve el estado conforme a dicha evidencia (R16).
- La ausencia de evidencia externa verificable no se utiliza como fundamento para asumir que el efecto externo no ocurrió (R17).
- La capacidad del proveedor externo de proporcionar evidencia verificable no se asume sin verificación previa (R18).
- La identidad de intento utilizada para la autoridad de ejecución se preserva como distinta de la identidad científica (R19).
- La preservación de la correlación entre identidad de intento e identidad científica es verificable cuando el contrato congelado lo exija (R20).
- El sistema provee mecanismos para resolver operaciones inciertas, reconociendo el límite fundamental (R21).
- Cuando no es posible resolver una operación incierta mediante evidencia externa verificable, el sistema conserva una representación recuperable y distinguible de las operaciones elegibles para ejecución automática (R22).
- La política de resolución de operaciones inciertas puede configurar umbrales de escalamiento, pero dichos umbrales no se interpretan como garantías de seguridad de reejecución (R23).
- Las pruebas de frontera local no se presentan como pruebas de cancelación o fencing remoto.

#### Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas de NADR-F18-03 §5.1-§5.6 en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde | {✅/❌} |
| 7 | Import-linter: 4 contratos KEPT / 0 BROKEN | {✅/❌} |
| 8 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

### Gate 2 — Durable Local Apply & Recovery

**Objective:** Materializar NADR-F18-04, garantizando convergencia local idempotente bajo el modelo de fallos aprobado. Asegurar que toda autoridad de ejecución y todo resultado confirmado localmente persistan de forma recuperable, que la aplicación de resultados sea idempotente, y que exista coherencia entre autoridad, journal y proyecciones.

**Execution Mode:** Mixto, con secuencia estricta desde persistencia hacia reconstrucción. Wave 2.1 y Wave 2.2 pueden ejecutarse en paralelo, pero Wave 2.2 depende conceptualmente de los contratos de persistencia establecidos en Wave 2.1.

**Rollback Plan:** Las migraciones deben conservar compatibilidad con datos previamente persistidos. Las reversas destructivas de evidencia durable quedan prohibidas; cuando corresponda, se requerirá restauración verificada o una estrategia de forward recovery.

**Gate Status:** ⏳ PENDING

---

#### Wave 2.1 — Durability & Idempotent Apply (NADR-F18-04 §5.1, §5.2)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Verificar y completar el contrato de confirmación durable. Formalizar política de durabilidad SQLite WAL + synchronous=NORMAL + busy_timeout conforme a ADR_F18.2 §8.1. Documentar garantías para escenarios incluidos y exclusiones explícitas para escenarios no cubiertos (power loss, fallo físico). | NADR-F18-04 §5.1 R1, R2, R3, R4 | High | Gate 0 | TODO |
| **2.1.2** | Verificar y completar idempotencia local para journal (append_wal con ON CONFLICT DO NOTHING), comandos de reconciliación (processed_reconciliation_commands) y aplicación de resultados (upsert_projection con version check monotónico). Implementar property tests de repetición. | NADR-F18-04 §5.2 R5, R6 | High | Task 2.1.1 | TODO |
| **2.1.3** | Impedir sobrescrituras por autoridad obsoleta mediante mecanismos de control de concurrencia (bloqueo optimista con version check monotónico o CAS). Implementar pruebas de concurrencia y conflicto para una misma identidad y versión. | NADR-F18-04 §5.2 R7 | High | Task 2.1.2 | TODO |

**Notas de implementación — Task 2.1.1**

> {Se actualiza al completar la Task. Documenta cómo se formalizó la política de durabilidad, la configuración SQLite, las garantías documentadas para escenarios incluidos y las exclusiones explícitas.}

**Notas de implementación — Task 2.1.2**

> {Se actualiza al completar la Task. Documenta cómo se verificó y completó la idempotencia local, los property tests de repetición agregados.}

**Notas de implementación — Task 2.1.3**

> {Se actualiza al completar la Task. Documenta cómo se implementaron los mecanismos de control de concurrencia, las pruebas de sobrescritura por autoridad obsoleta.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 2.2 — Recovery Convergence (NADR-F18-04 §5.3, §5.4, §5.5)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Materializar recuperación de resultados confirmados durables cuya proyección o reconocimiento final quedó pendiente. Implementar convergencia idempotente post-fallo parcial: si el journal registra un resultado pero el proceso falla antes de actualizar la proyección, el sistema debe completar o reconstruir idempotentemente las transiciones locales derivadas pendientes sin requerir nueva ejecución externa. | NADR-F18-04 §5.3 R8, R10 | High | Task 2.1.3 | TODO |
| **2.2.2** | Verificar reconstruibilidad determinista de proyecciones desde fuentes autoritativas (principalmente event journal). Implementar coherencia entre control plane, event plane y materialized plane tras recuperación. | NADR-F18-04 §5.3 R9 (verificación) | High | Task 2.2.1 | TODO |
| **2.2.3** | Implementar separación explícita de propiedades: atomicidad, durabilidad, idempotencia y recuperabilidad deben declararse y verificarse por separado. Prohibir interpretar atomicidad como garantía de durabilidad, durabilidad como garantía de idempotencia, o idempotencia local como garantía de recuperación coherente entre planos. | NADR-F18-04 §5.4 R11, R12, R13, R14 | Medium | Task 2.2.1 | TODO |
| **2.2.4** | Implementar compatibilidad con NADR-F18-03: la recuperación del estado local debe respetar la clasificación semántica de resultados establecida en NADR-F18-03 §5.2. La ausencia de confirmación local de un resultado no debe interpretarse como prueba de ausencia de efecto externo (conforme a NADR-F18-03 R7). | NADR-F18-04 §5.5 R15, R16 | Medium | Task 2.2.1, Gate 1 | TODO |

**Notas de implementación — Task 2.2.1**

> {Se actualiza al completar la Task. Documenta cómo se implementó la recuperación de resultados confirmados durables con proyección pendiente, los tests de crash entre journal y proyección.}

**Notas de implementación — Task 2.2.2**

> {Se actualiza al completar la Task. Documenta cómo se verificó la reconstruibilidad determinista, los tests de reconstrucción y reconciliación.}

**Notas de implementación — Task 2.2.3**

> {Se actualiza al completar la Task. Documenta cómo se implementó la separación de propiedades, los tests de verificación independiente de cada propiedad.}

**Notas de implementación — Task 2.2.4**

> {Se actualiza al completar la Task. Documenta cómo se implementó la compatibilidad con NADR-F18-03, los tests de respeto a la clasificación semántica.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 2 Exit Criteria

Todas las reglas de NADR-F18-04 §5.1, §5.2, §5.3, §5.4, §5.5 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- Toda autoridad de ejecución y todo resultado confirmado localmente persisten en almacenamiento recuperable conforme al modelo de fallos aprobado en ADR_F18.2 §8.1 (R1).
- Un resultado local no se considera confirmado durablemente hasta que su fuente autoritativa haya completado satisfactoriamente el contrato de confirmación de persistencia aplicable (R2).
- La persistencia del execution plane respeta la política inicial SQLite WAL + synchronous=NORMAL + busy_timeout aprobada en ADR_F18.2 §3.1/§8.2 (R3).
- Las garantías de durabilidad aplican exclusivamente a los escenarios incluidos en el modelo de fallos aprobado y no se extienden implícitamente a escenarios excluidos (R4).
- La reaplicación de un mismo resultado confirmado es idempotente y no produce efectos locales duplicados o inconsistentes (R5).
- Para una misma identidad lógica y versión de resultado, la aplicación repetida preserva un estado equivalente. Una versión igual con contenido incompatible no sobrescribe silenciosamente un resultado previamente confirmado (R6).
- Las escrituras producidas por una autoridad obsoleta no sobrescriben resultados pertenecientes a una autoridad vigente (R7).
- Tras toda recuperación, la coherencia entre autoridad local, registro de eventos y proyecciones materializadas se verifica conforme a las reglas de reconciliación aprobadas (R8).
- Toda proyección materializada que represente resultados confirmados es reconstruible de forma determinista a partir de sus fuentes locales autoritativas recuperables (R9).
- Cuando un resultado haya alcanzado confirmación durable en su fuente local autoritativa, cualquier interrupción posterior permite completar o reconstruir idempotentemente las transiciones locales derivadas pendientes, sin requerir una nueva ejecución externa por la sola ausencia de materialización o reconocimiento final (R10).
- Las garantías de atomicidad, durabilidad, idempotencia y recuperabilidad se declaran y verifican por separado (R11).
- La atomicidad de una transición local no se interpreta como garantía de durabilidad ante fallos (R12).
- La durabilidad ante fallos no se interpreta como garantía de idempotencia de aplicación (R13).
- La idempotencia de aplicación local no se interpreta como garantía de recuperación coherente entre planos (R14).
- La recuperación del estado local respeta la clasificación semántica de resultados establecida en NADR-F18-03 §5.2 (R15).
- La ausencia de confirmación local de un resultado no se interpreta como prueba de ausencia de efecto externo, conforme a NADR-F18-03 R7 (R16).

#### Gate 2 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas de NADR-F18-04 §5.1-§5.5 en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde | {✅/❌} |
| 7 | Import-linter: 4 contratos KEPT / 0 BROKEN | {✅/❌} |
| 8 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

### Gate 3 — Exposure Observability & FinOps

**Objective:** Materializar DC-08c mediante NADR-F18-05, implementando capacidad de observabilidad estratificada para caracterizar exposición a duplicación sin crear una fuente de verdad paralela. Garantizar que toda ejecución de efecto externo disponga de trazabilidad observable que permita correlacionar intentos, resultados y decisiones de recuperación.

**Execution Mode:** Mixto; primero correlación y evidencia (Wave 3.1), después métricas derivadas (Wave 3.2).

**Rollback Plan:** Las señales derivadas pueden desactivarse si fallan, pero no deben perderse autorizaciones excepcionales, resultados locales confirmados ni evidencia necesaria para su auditoría.

**Gate Status:** ⏳ PENDING

---

#### Wave 3.1 — Correlation & Evidence (NADR-F18-05 §5.1, §5.2)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Materializar correlación estable entre operación lógica, intentos, resultados y decisiones excepcionales, reutilizando identidades existentes cuando sean suficientes. Implementar clave de correlación lógica estable que pueda derivarse de identidades existentes cuando resulte inequívoca, sin imponer un identificador físico adicional. | NADR-F18-05 §5.1 R1, R2, R3 | Medium | Gates 1, 2 | TODO |
| **3.1.2** | Materializar la distinción entre actividad cliente (intento inicial, reejecución, cantidad de intentos) y evidencia sobre duplicación externa (desconocida, inferida, confirmada). Conservar procedencia y evitar doble conteo. Implementar evolución de evidencia: un caso inferido puede pasar a confirmado sin doble conteo. | NADR-F18-05 §5.2 R4, R5, R6, R7, R8 | High | Task 3.1.1 | TODO |

**Notas de implementación — Task 3.1.1**

> {Se actualiza al completar la Task. Documenta cómo se implementó la correlación estable, la clave de correlación lógica, los tests de correlación multintento.}

**Notas de implementación — Task 3.1.2**

> {Se actualiza al completar la Task. Documenta cómo se implementó la distinción entre actividad cliente y evidencia de duplicación externa, los tests de taxonomía y evolución probatoria.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 3.2 — Measurement & Financial Exposure (NADR-F18-05 §5.3, §5.4, §5.5)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Instrumentar ventanas cliente (intervalo observable entre execute() y append_wal()), distinción de ventanas causales externas, denominadores, cobertura y límites de inferencia. Implementar identificación de cada duración como medida, estimada, acotada mediante evidencia validada o no observable. | NADR-F18-05 §5.3 R9, R10 | High | Task 3.1.2 | TODO |
| **3.2.2** | Materializar reportes de costes observados/facturados, estimados y exposición económica potencial no confirmada, con atribución a operaciones lógicas cuando sea posible. Prohibir presentar costes hipotéticos de benchmark como gasto real de producción. | NADR-F18-05 §5.4 R12, R13 | Medium | Task 3.2.1 | TODO |
| **3.2.3** | Asegurar recuperabilidad de evidencia auditable necesaria (conforme a NADR-F18-04) y declarar cobertura o pérdida de telemetría sin falsos ceros. Implementar distinción entre evidencia auditable durable (trazabilidad de decisiones excepcionales) y telemetría derivada (métricas de agregación que pueden ser efímeras). Implementar trazabilidad durable de reejecuciones excepcionales autorizadas bajo incertidumbre, conservando correlación observable con su decisión de autorización y aceptación de riesgo. | NADR-F18-05 §5.4 R11, §5.5 R14, R15, R16 | High | Task 3.2.1, Gates 1, 2 | TODO |

**Notas de implementación — Task 3.2.1**

> {Se actualiza al completar la Task. Documenta cómo se instrumentaron las ventanas cliente, la distinción de ventanas causales, los tests de métricas y evidencia temporal.}

**Notas de implementación — Task 3.2.2**

> {Se actualiza al completar la Task. Documenta cómo se implementaron los reportes de costes, la atribución a operaciones lógicas, los tests FinOps y reportes de exposición.}

**Notas de implementación — Task 3.2.3**

> {Se actualiza al completar la Task. Documenta cómo se aseguró la recuperabilidad de evidencia auditable, la distinción entre evidencia durable y telemetría efímera, la trazabilidad durable de decisiones excepcionales, los tests de crash, pérdida de señales y reconstrucción.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 3 Exit Criteria

Todas las reglas de NADR-F18-05 §5.1, §5.2, §5.3, §5.4, §5.5 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- Todo intento de efecto externo es correlacionable con su operación lógica original y su resultado local conocido (R1).
- La observabilidad no equipara, confluye ni sustituye la identidad de intento por la identidad científica definida en el contrato de identidad congelado (R2).
- Toda operación lógica dispone de una clave de correlación lógica estable que permite correlacionar sus múltiples intentos de ejecución (R3).
- La observabilidad distingue dos dimensiones conceptuales: actividad del cliente y evidencia de duplicación externa. Estas dimensiones no se modelan como estados mutuamente excluyentes (R4).
- Duplicación externa confirmada se define como evidencia verificable y suficientemente atribuible que acredita más de una aplicación externa de la misma operación lógica. La mera existencia de múltiples intentos del cliente, cargos agregados o señales indirectas no constituye por sí sola confirmación (R5).
- Toda tasa reportada declara explícitamente su numerador, denominador, unidad de observación, período de observación, cobertura de datos y limitaciones de comparabilidad (R6).
- La ausencia de evidencia externa verificable no se interpreta como evidencia de ausencia de duplicación (R7).
- Las ventanas temporales observables del cliente y las ventanas causales externas se distinguen conceptualmente y en todo reporte aplicable. Cada duración se identifica como medida, estimada, acotada mediante evidencia validada o no observable (R8).
- Una medición o estimación indirecta de ventana de exposición no se presenta como cota superior validada sin evidencia que demuestre la relación entre la medición indirecta y la cota causal (R9).
- La pérdida, insuficiencia o ceguera deliberada de observabilidad es identificable y reportada explícitamente; no se transforma silenciosamente en valores cero, suposiciones de éxito o inferencias no fundamentadas (R10).
- Toda reejecución excepcional autorizada bajo incertidumbre conserva una correlación observable y durable (conforme a las garantías de persistencia de NADR-F18-04) con su decisión de autorización, la aceptación explícita del riesgo asociado y la identidad de la autoridad que tomó la decisión (R11).
- Los costes derivados de efectos externos se distinguen explícitamente en tres categorías: coste observado o facturado, coste estimado, y exposición económica potencial no confirmada (R12).
- La observabilidad de exposición a duplicación expone datos accionables para los mecanismos de control de presupuesto y FinOps (R13).
- La atribución de reejecuciones a operaciones lógicas se preserva cuando sea posible (R14).
- La reconstrucción de evidencia de observabilidad respeta la jerarquía de autoridad y las garantías de persistencia gobernadas por NADR-F18-04 (R15).
- La trazabilidad de decisiones excepcionales se rige por las mismas garantías de persistencia durable que el estado local gobernado por NADR-F18-04 (R16).
- Una reejecución del cliente no se reporta automáticamente como duplicación confirmada del proveedor.
- Existe trazabilidad entre intentos y operaciones lógicas.
- La evolución inferido → confirmado no ocasiona doble conteo.
- Las ventanas cliente no se presentan como cotas externas sin validación.
- La ausencia de observabilidad se identifica como desconocimiento, no como cero.
- Los costes hipotéticos no se publican como gasto real.
- Los informes diferencian propiedades demostradas, inferidas y no observables.

#### Gate 3 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las reglas de NADR-F18-05 §5.1-§5.5 en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde | {✅/❌} |
| 7 | Import-linter: 4 contratos KEPT / 0 BROKEN | {✅/❌} |
| 8 | Notas de implementación completas para todas las Tasks | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

### Gate 4 — Integrated Empirical Validation

**Objective:** Validar empíricamente las garantías arquitectónicas bajo escenarios críticos de fallo. Ejecutar chaos harness ampliado, validar convergencia, medir ventanas directamente, verificar fencing de frontera externa y caracterizar durabilidad ante terminación abrupta real.

**Execution Mode:** Paralelo (Waves 4.1, 4.2, 4.3 independientes).

**Rollback Plan:** Se practica el procedimiento aprobado del Runbook (§4); no se presupone que deshacer una migración de esquema o restaurar un backup elimine efectos ya ejecutados en un proveedor.

**Gate Status:** ⏳ PENDING

---

#### Wave 4.1 — Chaos Harness & Convergence Validation (Todos los NADRs)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Ejecutar game_day_1 completo con todos los escenarios críticos del modelo de fallos aprobado (ADR_F18.2 §8.1): terminación coordinada (SIGTERM/SIGINT), SIGKILL, crash pre-efecto, crash post-efecto/pre-journal, crash post-journal/pre-proyección, pérdida de autoridad. Verificar que el sistema alcanza estado coherente y no hay duplicaciones no autorizadas. | Validación empírica de Gates 1-3 | Critical | Gates 1-3 | TODO |
| **4.1.2** | Validar convergencia bajo todos los escenarios del modelo de fallos. Verificar que las decisiones excepcionales se trazan correctamente y conservan correlación observable durable con su autorización y aceptación de riesgo. | NADR-F18-03 §5.3 R10, R11; NADR-F18-05 §5.5 R15 | Critical | Task 4.1.1 | TODO |
| **4.1.3** | Ejecutar regresión completa contra el corpus canónico (perfiles SMOKE y FULL). Validar que las capacidades de F18.1 y del pipeline científico siguen satisfechas. Verificar no regresión de invariantes INV-SCI-1, INV-OPS-1, INV-ASSEMBLY-ORDER, INV-NO-RESOURCE-SIGNAL. | Validación de no regresión científica | Critical | Task 4.1.1 | TODO |

**Notas de implementación — Task 4.1.1**

> {Se actualiza al completar la Task. Documenta los escenarios ejecutados, los resultados de convergencia, las duplicaciones observadas (si las hubo), la evidencia de validación.}

**Notas de implementación — Task 4.1.2**

> {Se actualiza al completar la Task. Documenta la validación de trazabilidad de decisiones excepcionales, la correlación observable durable, los tests de auditoría post-recuperación.}

**Notas de implementación — Task 4.1.3**

> {Se actualiza al completar la Task. Documenta los resultados de regresión contra el corpus canónico, la validación de no regresión de invariantes científicos.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 4.2 — Direct Measurement & External Fencing (NADR-F18-05, NADR-F18-03)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Caracterizar el intervalo cliente observable mediante medición directa en un entorno autorizado y reproducible (staging controlado o laboratorio), con identificación explícita de proveedor LLM, configuración de hardware, tamaño de muestra, carga de trabajo, presupuesto máximo de medición, condiciones de fallo a inyectar, y criterios de interpretación. Declarar explícitamente que esta medición es del intervalo cliente observable, no de la ventana causal externa. Documentar limitaciones de observación y comparabilidad. | NADR-F18-05 §5.3 R9, R10 | High | Gates 1-3 | TODO |
| **4.2.2** | Validar capacidad de medición de duplicación: verificar que las tres categorías (actividad cliente, duplicación inferida, duplicación confirmada) se miden correctamente y no se confluyen. Verificar que las tasas declaran numerador/denominador/unidad/período. Verificar que la incapacidad de medir se reporta explícitamente. | NADR-F18-05 §5.2 R4, R5, R6, R7 | High | Task 4.2.1 | TODO |
| **4.2.3** | Implementar y ejecutar test_fencing.py (actualmente vacío, 0 bytes). Validar fencing DB/SQL (worker zombi bloqueado por optimistic locking), fencing de reconciler (comandos obsoletos rechazados), fencing de frontera externa (mock LLM con registro durable que verifique que worker obsoleto no puede iniciar nuevas llamadas tras perder lease). Declarar explícitamente que las pruebas con mock demuestran el comportamiento de la aplicación bajo condiciones simuladas, no una garantía universal del proveedor. | NADR-F18-03 §5.1 R1, R2, R3; Validación empírica de fencing | Critical | Gates 1-3 | TODO |

**Notas de implementación — Task 4.2.1**

> {Se actualiza al completar la Task. Documenta el entorno de medición autorizado, el proveedor LLM utilizado, la configuración de hardware, el tamaño de muestra, la carga de trabajo, el presupuesto máximo, las condiciones de fallo inyectadas, los criterios de interpretación, la distribución caracterizada (P50, P95, P99), la declaración explícita de que es medición del intervalo cliente, las limitaciones de observación y comparabilidad.}

**Notas de implementación — Task 4.2.2**

> {Se actualiza al completar la Task. Documenta la validación de la capacidad de medición de duplicación, los tests de no confluencia de categorías, los tests de declaración de numerador/denominador.}

**Notas de implementación — Task 4.2.3**

> {Se actualiza al completar la Task. Documenta la implementación de test_fencing.py, los tests de fencing DB/SQL, fencing de reconciler, fencing de frontera externa con mock LLM, la declaración explícita de limitaciones de las pruebas con mock.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 4.3 — Durability & Power Loss Characterization (NADR-F18-04)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Validar durabilidad ante terminación abrupta real (SIGKILL) más allá de game_day_1. Ejecutar pruebas específicas de crash en diferentes puntos del flujo de persistencia (antes de journal, entre journal y proyección, entre proyección y acknowledge). Verificar que el sistema recupera estado coherente conforme a la jerarquía de verdad local (Event Journal como fuente de verdad primaria). | NADR-F18-04 §5.1 R1, R2, R3, R4; §5.3 R8, R9, R10 | High | Gates 1-3 | TODO |
| **4.3.2** | Documentar comportamiento ante power loss como limitación aceptada explícitamente (conforme a ADR_F18.2 §8.1, §8.2). No prometer durabilidad ante power loss sin evidencia. Registrar honestamente que synchronous=NORMAL no garantiza flush a disco ante pérdida de energía. | NADR-F18-04 §5.1 R4; Documentación de limitación aceptada | Medium | Task 4.3.1 | TODO |

**Notas de implementación — Task 4.3.1**

> {Se actualiza al completar la Task. Documenta las pruebas de durabilidad ante SIGKILL, los puntos de crash inyectados, la validación de recuperación coherente, la jerarquía de verdad local verificada.}

**Notas de implementación — Task 4.3.2**

> {Se actualiza al completar la Task. Documenta la caracterización del comportamiento ante power loss, la documentación de limitación aceptada, la declaración honesta de garantías.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 4 Exit Criteria

Todas las validaciones empíricas de Gates 1-3 deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- Chaos harness ejecutado con todos los escenarios críticos del modelo de fallos aprobado (terminación coordinada, SIGKILL, crash pre-efecto, crash post-efecto/pre-journal, crash post-journal/pre-proyección, pérdida de autoridad).
- Convergencia validada empíricamente: el sistema alcanza estado coherente bajo todos los escenarios del modelo de fallos.
- No hay duplicaciones no autorizadas observadas en los escenarios de validación.
- Las decisiones excepcionales se trazan correctamente y conservan correlación observable durable.
- Regresión completa contra el corpus canónico (perfiles SMOKE y FULL) pasada sin alteración de invariantes científicos.
- Intervalo cliente observable caracterizado mediante medición directa en entorno autorizado y reproducible, con declaración explícita de limitaciones.
- Capacidad de medición de duplicación validada: las tres categorías se miden correctamente y no se confluyen.
- test_fencing.py implementado y pasando: fencing DB/SQL, fencing de reconciler, fencing de frontera externa (con mock).
- Durabilidad ante SIGKILL validada más allá de game_day_1.
- Comportamiento ante power loss documentado honestamente como limitación aceptada.
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde.
- Import-linter: 4 contratos KEPT / 0 BROKEN.

#### Gate 4 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Todas las validaciones empíricas de Gates 1-3 en estado DONE en §7 | {✅/❌} |
| 3 | Gate Exit Criteria satisfechos | {✅/❌} |
| 4 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 5 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 6 | Tests: suite completa en verde | {✅/❌} |
| 7 | Import-linter: 4 contratos KEPT / 0 BROKEN | {✅/❌} |
| 8 | Notas de implementación completas para todas las Tasks | {✅/❌} |
| 9 | Evidencia de validación empírica documentada (reportes de chaos harness, mediciones, tests de fencing) | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

### Gate 5 — Phase Closure & Deferred Findings Resolution

**Objective:** Evaluar triggers de diferimientos condicionados (DF-24, DF-34), completar Deferred Findings Register, completar Exit Review Evidence Log, y cerrar la Subfase 18.2 con handoff a Fase 18.3.

**Execution Mode:** Secuencial.

**Rollback Plan:** No aplica. Este Gate es de cierre documental y evaluación de triggers, no de implementación funcional.

**Gate Status:** ⏳ PENDING

---

#### Wave 5.1 — Deferred Findings Evaluation (DF-24, DF-34)

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **5.1.1** | Ejecutar benchmark de coste de re-inferencia para ProfileStore (trigger DF-34). Medir coste de CPU de reconstrucción heurística, latencia de re-inferencia, estabilidad del resultado. Evaluar si el coste es operacionalmente aceptable. | Evaluación de trigger DF-34 | Medium | Gate 4 | TODO |
| **5.1.2** | Evaluar resultado del benchmark de DF-34 y determinar disposición conforme a gobernanza de diferimientos condicionados: (a) Si trigger no activado (coste no medible o inconcluso): mantener diferimiento con evidencia y condición de reevaluación. (b) Si trigger activado y decisión dentro de autoridad vigente: registrar disposición autorizada (ACCEPTED_LIMITATION o cambio operativo). (c) Si trigger activado requiere cambiar decisión FROZEN: elevar al Architecture Board y mantener bloqueada cualquier implementación incompatible hasta resolución formal. | Resolución de DF-34 | High | Task 5.1.1 | TODO |
| **5.1.3** | Medir impacto efectivo de warm-up de CircuitBreaker (trigger DF-24). Medir tiempo real de recuperación tras reinicio, número de llamadas fallidas durante warm-up, impacto FinOps. | Evaluación de trigger DF-24 | Medium | Gate 4 | TODO |
| **5.1.4** | Evaluar resultado de la medición de DF-24 y determinar disposición conforme a gobernanza de diferimientos condicionados: (a) Si trigger no activado (impacto no medible o inconcluso): mantener diferimiento con evidencia y condición de reevaluación. (b) Si trigger activado y decisión dentro de autoridad vigente: registrar disposición autorizada (ACCEPTED_LIMITATION o cambio operativo). (c) Si trigger activado requiere cambiar decisión FROZEN: elevar al Architecture Board y mantener bloqueada cualquier implementación incompatible hasta resolución formal. | Resolución de DF-24 | High | Task 5.1.3 | TODO |

**Notas de implementación — Task 5.1.1**

> {Se actualiza al completar la Task. Documenta el benchmark ejecutado, las métricas de coste de CPU, latencia, estabilidad, la evaluación de aceptabilidad operacional.}

**Notas de implementación — Task 5.1.2**

> {Se actualiza al completar la Task. Documenta la disposición tomada sobre DF-34 conforme a las tres opciones de gobernanza, la justificación basada en evidencia, si se requiere elevación al Architecture Board.}

**Notas de implementación — Task 5.1.3**

> {Se actualiza al completar la Task. Documenta la medición de impacto de warm-up, las métricas de tiempo de recuperación, llamadas fallidas, impacto FinOps.}

**Notas de implementación — Task 5.1.4**

> {Se actualiza al completar la Task. Documenta la disposición tomada sobre DF-24 conforme a las tres opciones de gobernanza, la justificación basada en evidencia, si se requiere elevación al Architecture Board.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Wave 5.2 — Documentation & Handoff

**Wave Status:** ⏳ PENDING

**Fecha de inicio:** TBD

**Fecha de cierre:** TBD

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **5.2.1** | Completar Deferred Findings Register (`reviews/FASE_18.2_DEFERRED_FINDINGS_REGISTER.md`). Clasificar todos los hallazgos identificados durante la implementación de Gates 0-4. Documentar resoluciones o diferimientos a fases futuras. Actualizar estado de todos los findings a RESOLVED, CLOSED (NAR), RECLASSIFIED_FUTURE_PHASE, o ACCEPTED_LIMITATION según corresponda. | Completitud del Findings Register | Medium | Gates 0-4 | TODO |
| **5.2.2** | Completar Exit Review Evidence Log (`reviews/FASE_18.2_EXIT_REVIEW_EVIDENCE_LOG.md`). Documentar evidencia forense de cada decisión tomada durante la implementación. Consolidar hallazgos de Gates 0-4. Congelar el documento como FROZEN. | Completitud del Evidence Log | Medium | Task 5.2.1 | TODO |
| **5.2.3** | Handoff a Fase 18.3. Documentar estado final de la Subfase 18.2. Identificar dependencias para Fase 18.3 (Resource Governance & Adaptive Scheduling). Actualizar ROADMAP si es necesario. | Handoff documental | Low | Task 5.2.2 | TODO |

**Notas de implementación — Task 5.2.1**

> {Se actualiza al completar la Task. Documenta el estado final del Deferred Findings Register, la clasificación de todos los hallazgos, las resoluciones o diferimientos.}

**Notas de implementación — Task 5.2.2**

> {Se actualiza al completar la Task. Documenta el estado final del Exit Review Evidence Log, la evidencia forense consolidada, el congelamiento del documento.}

**Notas de implementación — Task 5.2.3**

> {Se actualiza al completar la Task. Documenta el handoff a Fase 18.3, las dependencias identificadas, las actualizaciones al ROADMAP si aplican.}

**Hallazgos identificados en esta Wave**

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

---

#### Gate 5 Exit Criteria

Todas las tareas de cierre documental y evaluación de triggers deben alcanzar estado `DONE`. Específicamente:

- Trigger DF-34 evaluado con benchmark de coste de re-inferencia completado.
- Disposición sobre DF-34 documentada conforme a gobernanza de diferimientos condicionados (mantener diferimiento, ACCEPTED_LIMITATION, o elevación al Board).
- Trigger DF-24 evaluado con medición de impacto de warm-up completada.
- Disposición sobre DF-24 documentada conforme a gobernanza de diferimientos condicionados (mantener diferimiento, ACCEPTED_LIMITATION, o elevación al Board).
- Deferred Findings Register completo y actualizado con todos los hallazgos de Gates 0-4 clasificados.
- Exit Review Evidence Log FROZEN con evidencia forense consolidada de todas las decisiones.
- Handoff a Fase 18.3 completado con dependencias identificadas.
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde.
- Import-linter: 4 contratos KEPT / 0 BROKEN.

#### Gate 5 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | {✅/❌} |
| 2 | Gate Exit Criteria satisfechos | {✅/❌} |
| 3 | Hallazgos identificados derivados al Findings Register | {✅/❌} |
| 4 | Pyright: 0 errors, 0 warnings | {✅/❌} |
| 5 | Tests: suite completa en verde | {✅/❌} |
| 6 | Import-linter: 4 contratos KEPT / 0 BROKEN | {✅/❌} |
| 7 | Notas de implementación completas para todas las Tasks | {✅/❌} |
| 8 | Deferred Findings Register ARCHIVED | {✅/❌} |
| 9 | Exit Review Evidence Log FROZEN | {✅/❌} |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}

**Fecha de verificación:** {YYYY-MM-DD}

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 0 | {YYYY-MM-DD} | 0/0 (no implementa reglas, solo mapeo) | {A}/4 | {N} | {Observaciones} |
| Gate 1 | {YYYY-MM-DD} | {X}/23 (NADR-F18-03) | {A}/8 | {N} | {Observaciones} |
| Gate 2 | {YYYY-MM-DD} | {X}/16 (NADR-F18-04) | {A}/7 | {N} | {Observaciones} |
| Gate 3 | {YYYY-MM-DD} | {X}/16 (NADR-F18-05) | {A}/5 | {N} | {Observaciones} |
| Gate 4 | {YYYY-MM-DD} | 0/0 (validación empírica, no implementación de reglas nuevas) | {A}/8 | {N} | {Observaciones} |
| Gate 5 | {YYYY-MM-DD} | 0/0 (cierre documental, no implementación de reglas nuevas) | {A}/7 | {N} | {Observaciones} |
| **TOTAL** | **{YYYY-MM-DD}** | **55/55** | **{A}/39** | **{N}** | **Subfase 18.2 COMPLETADA** |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Captura de baseline y backup verificable de todas las bases de datos SQLite (queue.db, event.db, materialized.db, fsm.db, telemetry.db) | Local / Staging | NADR-F18-04 §5.1 R1, R2 | Backup verificable con hash SHA-256 | TODO |
| **MIG-02** | Verificación de versión y configuración SQLite: confirmar que todas las conexiones utilizan WAL + synchronous=NORMAL conforme a política aprobada. Documentar busy_timeout como parámetro operativo del plan (no como obligación literal del ADR). | Local / Staging / Prod | NADR-F18-04 §5.1 R3 | Reporte de configuración | TODO |
| **MIG-03** | Preflight de compatibilidad de esquemas: verificar que las migraciones de esquema (agregado de campos de trazabilidad, índices para clasificación semántica, etc.) son no destructivas y compatibles con datos previamente persistidos | Local / Staging | NADR-F18-04 §5.1 R1, R2 | Reporte de compatibilidad | TODO |
| **MIG-04** | Ensayo de migración no destructiva en entorno de staging: ejecutar migraciones, verificar integridad de datos, validar reversibilidad aplicable | Staging | NADR-F18-04 §5.1 R1, R2, R3 | Evidencia de ensayo exitoso | TODO |
| **MIG-05** | Activación controlada de contratos de ejecución: desplegar nueva versión con activación por configuración (sin feature flags) para habilitar autoridad pre-efecto, clasificación semántica, y observabilidad de duplicación | Staging / Prod | NADR-F18-03 §5.1, §5.2, §5.3; NADR-F18-05 §5.1, §5.2 | Reporte de activación | TODO |
| **MIG-06** | Verificación postactivación de lease, recuperación y evidencia: monitorear que la autoridad recuperable se persiste correctamente, que la clasificación semántica distingue los tres estados, que la observabilidad de duplicación reporta las tres categorías | Prod | NADR-F18-03 §5.1, §5.2; NADR-F18-04 §5.3; NADR-F18-05 §5.2 | Reporte de verificación | TODO |
| **MIG-07** | Procedimiento de contingencia y recuperación segura: definir procedimiento para rollback de configuración sin perder evidencia de efectos externos inciertos ni resultados confirmados. No restaurar base de datos antigua de forma automática mientras existan efectos remotos inciertos (podría retroceder conocimiento local sin revertir efecto externo). | Prod | NADR-F18-03 §5.3; NADR-F18-04 §5.3 | Procedimiento documentado | TODO |
| **MIG-08** | Registro de aceptación y evidencia operativa: documentar estado final auditable, decisiones de aceptación de riesgo, limitaciones aceptadas, y handoff a operación | Prod | Todos los NADRs | Reporte de aceptación | TODO |

---

## 5. GLOBAL DoD (Definition of Done)

La Subfase 18.2 se considera oficialmente completada cuando:

```text
{55 reglas en NADRs FROZEN (NADR-F18-03: 23 reglas, NADR-F18-04: 16 reglas, NADR-F18-05: 16 reglas)} − {Rules with DONE status in §7} = ∅
```

### 5.1 Derivación del estado DONE

El estado de una regla es **derivado** del estado de las tareas que la implementan y validan. Una regla alcanza estado `DONE` cuando se cumplen **simultáneamente** las tres condiciones siguientes:

1. **Implementation Evidence:** Existe al menos una tarea con estado `DONE` que implementa la regla (evidencia de implementación commiteada).
2. **Verification superado:** La implementación supera los mecanismos de verificación estática/mecánica aplicables (linter, type-check, property-test, import-linter).
3. **Validation superado:** La implementación supera los mecanismos de validación dinámica/comportamental aplicables (regression gate, chaos harness, golden corpus, pruebas de integración).

**Nota sobre tareas distribuidas:** Cuando una regla aparece en múltiples tareas (una implementa, otra verifica), el estado `DONE` se alcanza cuando **ambas** tareas están completas. La tarea implementadora provee Implementation Evidence; la tarea verificadora provee Verification/Validation.

**Nota sobre reglas no aplicables:** Si una regla no es aplicable al contexto de implementación (justificado explícitamente), puede marcarse como `N/A` con documentación de la justificación. Esto no cuenta como incumplimiento.

### 5.2 Verificación de completitud

Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / chaos harness / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

### 5.3 Criterios especializados para Subfase 18.2

- **Integridad normativa:** Cobertura total de las 55 reglas aplicables, sin duplicación de responsabilidades ni excepciones silenciosas.
- **Seguridad de efectos:** Ninguna recuperación incierta desencadena replay externo no autorizado (NADR-F18-03 §5.3 R9).
- **Recuperación local:** Una confirmación durable puede recuperarse idempotentemente tras fallos incluidos en el contrato (NADR-F18-04 §5.3 R10).
- **Compatibilidad:** No se alteran indebidamente las identidades científicas (NADR-F18-03 §5.5 R19, R20), los contratos de F18.1 (NADR-F18-02) ni las invariantes del pipeline (INV-SCI-1, INV-OPS-1, INV-ASSEMBLY-ORDER, INV-NO-RESOURCE-SIGNAL).
- **Observabilidad honesta:** La evidencia de duplicación no se confunde con actividad del cliente (NADR-F18-05 §5.2 R4, R5); lo inobservable permanece identificado como tal (NADR-F18-05 §5.3 R10).
- **Calidad:** Pyright 0 errors, 0 warnings; suite de tests completa en verde (baseline de 854 tests preservada o incrementada); import-linter 4 contratos KEPT / 0 BROKEN; propiedades concurrentes verificadas; regresiones contra corpus canónico (perfiles SMOKE y FULL) satisfechas.
- **Evidencia:** Cada escenario de aceptación identifica el artefacto, versión, commit, entorno, resultado y limitaciones relevantes.
- **Operación:** Migraciones, restauración y preflight están ensayados dentro del entorno aprobado (Runbook §4 ejecutado).
- **Gobernanza:** Los hallazgos bloqueantes están resueltos; las limitaciones aceptadas (DF-24, DF-34) conservan su clasificación formal; Deferred Findings Register ARCHIVED; Exit Review Evidence Log FROZEN.

**Sobre las reglas DEFERRED:**

Un hallazgo puede diferirse bajo la gobernanza correspondiente; una regla obligatoria aplicable no puede considerarse satisfecha por estar diferida. Si se difiere una obligación normativa indispensable, el cierre de la fase debe quedar bloqueado, salvo que exista una resolución formal de alcance o gobernanza que autorice otra disposición sin contradecir el corpus superior.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 0 | {A}/4 | 0/0 | 0 | 0 | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 1 | {A}/8 | {X}/23 | 0 | {Y} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 2 | {A}/7 | {X}/16 | 0 | {Y} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 3 | {A}/5 | {X}/16 | 0 | {Y} | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 4 | {A}/8 | 0/0 | 0 | 0 | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| Gate 5 | {A}/7 | 0/0 | 0 | 0 | {✅ COMPLETED / 🟡 IN PROGRESS / ⏳ PENDING} |
| **TOTAL** | **{A}/39** | **55/55** | **0** | **{Z}** | {Estado global} |

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

### 7.1 Gate 1 — Rules Audit Board (NADR-F18-03)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-03 §5.1 R1 | {DONE/PENDING} | Wave 1.1 / Task 1.1.1 | {Breve descripción de cómo se implementó} |
| NADR-F18-03 §5.1 R2 | {Status} | Wave 1.1 / Task 1.1.1 | {Notes} |
| NADR-F18-03 §5.1 R3 | {Status} | Wave 1.1 / Task 1.1.2 | {Notes} |
| NADR-F18-03 §5.1 R4 | {Status} | Wave 1.1 / Task 1.1.1 | {Notes} |
| NADR-F18-03 §5.2 R5 | {Status} | Wave 1.1 / Task 1.1.3 | {Notes} |
| NADR-F18-03 §5.2 R6 | {Status} | Wave 1.1 / Task 1.1.3 | {Notes} |
| NADR-F18-03 §5.2 R7 | {Status} | Wave 1.1 / Task 1.1.3 | {Notes} |
| NADR-F18-03 §5.2 R8 | {Status} | Wave 1.1 / Task 1.1.3 | {Notes} |
| NADR-F18-03 §5.3 R9 | {Status} | Wave 1.2 / Task 1.2.1 | {Notes} |
| NADR-F18-03 §5.3 R10 | {Status} | Wave 1.2 / Task 1.2.2 | {Notes} |
| NADR-F18-03 §5.3 R11 | {Status} | Wave 1.2 / Task 1.2.2 | {Notes} |
| NADR-F18-03 §5.3 R12 | {Status} | Wave 1.2 / Task 1.2.1 | {Notes} |
| NADR-F18-03 §5.3 R13 | {Status} | Wave 1.2 / Task 1.2.1 | {Notes} |
| NADR-F18-03 §5.3 R14 | {Status} | Wave 1.2 / Task 1.2.3 | {Notes} |
| NADR-F18-03 §5.3 R15 | {Status} | Wave 1.2 / Task 1.2.1 | {Notes} |
| NADR-F18-03 §5.4 R16 | {Status} | Wave 1.2 / Task 1.2.4 | {Notes} |
| NADR-F18-03 §5.4 R17 | {Status} | Wave 1.2 / Task 1.2.4 | {Notes} |
| NADR-F18-03 §5.4 R18 | {Status} | Wave 1.2 / Task 1.2.4 | {Notes} |
| NADR-F18-03 §5.5 R19 | {Status} | Wave 1.2 / Task 1.2.5 | {Notes} |
| NADR-F18-03 §5.5 R20 | {Status} | Wave 1.2 / Task 1.2.5 | {Notes} |
| NADR-F18-03 §5.6 R21 | {Status} | Wave 1.2 / Task 1.2.3 | {Notes} |
| NADR-F18-03 §5.6 R22 | {Status} | Wave 1.2 / Task 1.2.3 | {Notes} |
| NADR-F18-03 §5.6 R23 | {Status} | Wave 1.2 / Task 1.2.3 | {Notes} |

### 7.2 Gate 2 — Rules Audit Board (NADR-F18-04)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-04 §5.1 R1 | {DONE/PENDING} | Wave 2.1 / Task 2.1.1 | {Notes} |
| NADR-F18-04 §5.1 R2 | {Status} | Wave 2.1 / Task 2.1.1 | {Notes} |
| NADR-F18-04 §5.1 R3 | {Status} | Wave 2.1 / Task 2.1.1 | {Notes} |
| NADR-F18-04 §5.1 R4 | {Status} | Wave 2.1 / Task 2.1.1 | {Notes} |
| NADR-F18-04 §5.2 R5 | {Status} | Wave 2.1 / Task 2.1.2 | {Notes} |
| NADR-F18-04 §5.2 R6 | {Status} | Wave 2.1 / Task 2.1.3 | {Notes} |
| NADR-F18-04 §5.2 R7 | {Status} | Wave 2.1 / Task 2.1.3 | {Notes} |
| NADR-F18-04 §5.3 R8 | {Status} | Wave 2.2 / Task 2.2.1 | {Notes} |
| NADR-F18-04 §5.3 R9 | {Status} | Wave 2.2 / Task 2.2.1 (implementación), Task 2.2.2 (verificación) | {Notes} |
| NADR-F18-04 §5.3 R10 | {Status} | Wave 2.2 / Task 2.2.1 | {Notes} |
| NADR-F18-04 §5.4 R11 | {Status} | Wave 2.2 / Task 2.2.3 | {Notes} |
| NADR-F18-04 §5.4 R12 | {Status} | Wave 2.2 / Task 2.2.3 | {Notes} |
| NADR-F18-04 §5.4 R13 | {Status} | Wave 2.2 / Task 2.2.3 | {Notes} |
| NADR-F18-04 §5.4 R14 | {Status} | Wave 2.2 / Task 2.2.3 | {Notes} |
| NADR-F18-04 §5.5 R15 | {Status} | Wave 2.2 / Task 2.2.4 | {Notes} |
| NADR-F18-04 §5.5 R16 | {Status} | Wave 2.2 / Task 2.2.4 | {Notes} |

### 7.3 Gate 3 — Rules Audit Board (NADR-F18-05)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F18-05 §5.1 R1 | {DONE/PENDING} | Wave 3.1 / Task 3.1.1 | {Notes} |
| NADR-F18-05 §5.1 R2 | {Status} | Wave 3.1 / Task 3.1.1 | {Notes} |
| NADR-F18-05 §5.1 R3 | {Status} | Wave 3.1 / Task 3.1.1 | {Notes} |
| NADR-F18-05 §5.2 R4 | {Status} | Wave 3.1 / Task 3.1.2 | {Notes} |
| NADR-F18-05 §5.2 R5 | {Status} | Wave 3.1 / Task 3.1.2 | {Notes} |
| NADR-F18-05 §5.2 R6 | {Status} | Wave 3.1 / Task 3.1.2 | {Notes} |
| NADR-F18-05 §5.2 R7 | {Status} | Wave 3.1 / Task 3.1.2 | {Notes} |
| NADR-F18-05 §5.2 R8 | {Status} | Wave 3.1 / Task 3.1.2 | {Notes} |
| NADR-F18-05 §5.3 R9 | {Status} | Wave 3.2 / Task 3.2.1 | {Notes} |
| NADR-F18-05 §5.3 R10 | {Status} | Wave 3.2 / Task 3.2.1 | {Notes} |
| NADR-F18-05 §5.4 R11 | {Status} | Wave 3.2 / Task 3.2.3 | {Notes} |
| NADR-F18-05 §5.4 R12 | {Status} | Wave 3.2 / Task 3.2.2 | {Notes} |
| NADR-F18-05 §5.4 R13 | {Status} | Wave 3.2 / Task 3.2.2 | {Notes} |
| NADR-F18-05 §5.5 R14 | {Status} | Wave 3.2 / Task 3.2.3 | {Notes} |
| NADR-F18-05 §5.5 R15 | {Status} | Wave 3.2 / Task 3.2.3 | {Notes} |
| NADR-F18-05 §5.5 R16 | {Status} | Wave 3.2 / Task 3.2.3 | {Notes} |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-18/reviews/FASE_18.2_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.2.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (IMPLEMENTATION_REQUIRED / REVIEW_REQUIRED / CLOSED (NAR) / RECLASSIFIED_FUTURE_PHASE / ACCEPTED_LIMITATION)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este Execution Plan actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **El ADR_F18.2** define exclusivamente la visión arquitectónica de la Subfase 18.2 (el QUÉ y el POR QUÉ).
* **Los NADRs FROZEN** (NADR-F18-03, NADR-F18-04, NADR-F18-05) contienen las reglas técnicas obligatorias y las restricciones de diseño.
* **Este Execution Plan** define la secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos.
* **Los HITOs FROZEN** (HITO_18.2.0, HITO_18.2.1, HITO_18.2.2) proporcionan la evidencia forense que fundamenta las decisiones.
* **El Deferred Findings Register** registra los hallazgos identificados durante la implementación y su resolución.

Este documento **prescribe trabajo operativo dentro de las decisiones superiores** (tareas, secuencia, dependencias, validaciones), pero **no prescribe implementaciones tecnológicas específicas más allá de lo necesario para la trazabilidad normativa**. Los criterios de revisión de código y los detalles de implementación operativa se definen en los procedimientos de desarrollo.

Toda implementación que pretenda materializar las decisiones de ADR_F18.2 deberá demostrar trazabilidad explícita hacia este Execution Plan y hacia los NADRs FROZEN correspondientes.

**Criterio de cierre de la Subfase 18.2:**

La Subfase 18.2 se cierra cuando:

1. Las 55 reglas de NADR-F18-03/04/05 están en estado DONE en §7 (con Implementation Evidence, Verification y Validation completados conforme a §5.1).
2. Todos los Gates (0-5) están en estado COMPLETED.
3. El Deferred Findings Register está ARCHIVED.
4. El Exit Review Evidence Log está FROZEN.
5. El Global DoD (§5) está satisfecho.
6. Pyright: 0 errors, 0 warnings.
7. Tests: suite completa en verde (baseline de 854 tests preservada o incrementada).
8. Import-linter: 4 contratos KEPT / 0 BROKEN.
9. Runbook (§4) ejecutado exitosamente.
10. Handoff a Fase 18.3 completado.

---

## 10. FUTURE WORK

> Este Execution Plan cubre la Subfase 18.2 (Durable Execution & Recovery). Las siguientes subfases de Fase 18 (18.3 Resource Governance & Adaptive Scheduling, 18.4 Provider & Cache Runtime Semantics, 18.5 Runtime Verification & Promotion) tendrán sus propios Execution Plans.
>
> Mejoras futuras del proceso de trazabilidad podrían incluir:
> - Automatización del Traceability Appendix (§7) mediante scripts que extraigan el estado de las Tasks y recalculen los contadores del Status Dashboard (§6).
> - Integración con sistemas de CI/CD para actualización automática del estado de las Tasks basado en commits y PRs.
> - Herramientas de visualización del progreso de implementación y validación.
>
> Estas mejoras no son obligaciones del Execution Plan actual y quedan como trabajo futuro sujeto a priorización.

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
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§11.3)

### 11.6 Control de cambios del Execution Plan

El Execution Plan puede evolucionar durante la implementación, pero los cambios requieren:

1. **Versión incrementada:** Cada cambio significativo incrementa la versión del documento.
2. **Justificación documentada:** Todo cambio debe justificar por qué es necesario.
3. **Evaluación de impacto:** Analizar cómo el cambio afecta tareas pendientes, dependencias y criterios de salida.
4. **Aprobación:** Los cambios que modifican dependencias entre gates, eliminan tareas o alteran Exit Criteria requieren aprobación del Architecture Board.
5. **No modificar NADRs FROZEN:** El Execution Plan no puede modificar reglas normativas congeladas.

**Prohibiciones específicas:**
- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación de la Subfase 18.2. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN (55 reglas: 23 de NADR-F18-03, 16 de NADR-F18-04, 16 de NADR-F18-05), no este documento. El estado de cada regla es derivado del estado de la Task que la implementa (§5.1). Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.