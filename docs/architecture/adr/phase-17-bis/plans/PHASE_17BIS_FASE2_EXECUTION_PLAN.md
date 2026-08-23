# PHASE 17-BIS — FASE 2 EXECUTION PLAN v1.0.0
## Scientific Baseline Domain — Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.0
**Status:** `APPROVED`
**Date:** 2026-08-23
**Supersedes:** N/A (primer Execution Plan de la Fase 2)
**Derived From:** 4 NADRs APPROVED (NADR-F17BIS-12..15) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.2.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa de la Fase 2 (Scientific Baseline Domain) y el seguimiento de cumplimiento de las reglas de NADR-F17BIS-12..15. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-23 | Emisión inicial. Mapeo de las 37 reglas de NADR-F17BIS-12..15 a 4 Gates / 12 Waves / 37 tareas atómicas. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
ADR_F17_BIS_02 (Scientific Baseline Domain — APPROVED)
↓
NADRs F17BIS-12..15 (reglas constitucionales, APPROVED)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_FASE2_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_2_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR APPROVED, sin inventar identificadores paralelos:

```text
NADR-F17BIS-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-F17BIS-13 §5.2 R6` → NADR-F17BIS-13, sección 5.2, regla 6.

El inventario autoritativo de reglas es el **corpus de NADRs APPROVED** (NADR-F17BIS-12..15, 37 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

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
- **Mapeo 1:1 regla→tarea:** Cada una de las 37 reglas de NADR-F17BIS-12..15 es implementada por exactamente una tarea. Esto garantiza trazabilidad auditable sin doble implementación.

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

### 1.6 Restricciones de Hardware (carry-forward obligatorio)

Conforme al ADR Maestro §4 y ENGINEERING_PRINCIPLES:
- **Single-node / No infraestructura distribuida:** Prohibido Redis, Brokers, K8s, DBs remotas. SQLite WAL es el Core Engine.
- **Memory Efficiency:** DTOs inmutables (`frozen=True`), cero mutación in-place.
- **FinOps First & Fail-Fast:** Ninguna degradación silenciosa; toda anomalía aborta o emite warning indexable.

---

## 2. GATES DE LA FASE 2 — SCIENTIFIC BASELINE DOMAIN

La Fase 2 se estructura en **4 Gates**, uno por NADR, respetando el grafo de dependencias ontológicas:

```text
Gate 1 (NADR-12: Ontología)
   └──► Gate 2 (NADR-13: Validez/Completitud) — opera sobre entidades con estado
          └──► Gate 3 (NADR-14: Autoridad/Puertos) — exige validez como precondición
                 └──► Gate 4 (NADR-15: Identidad Semántica) — porta sobre oráculo sellado
```

Cada Gate actúa como compuerta conforme a METHODOLOGY §6.5: el Gate N+1 no inicia hasta que el Gate N pase su Exit Review.

---

## GATE 1 — ORACLE ONTOLOGY & LIFECYCLE GOVERNANCE

**Objective:** Formalizar la ontología del Ground Truth como entidad de dominio con ciclo de vida gobernado, disyunción Draft/Oracle e inmutabilidad de instancia.
**NADRs afectados:** NADR-F17BIS-12 (9 reglas)
**Execution Mode:** Secuencial (Critical Path — fundamento ontológico)
**Rollback Plan:** `git revert` de los modelos de dominio introducidos; el sistema retorna al estado de DTOs planos de Fase 1.
**Gate Status:** ⏳ PENDING

### 2.1 Wave 1.1 — Tipos disjuntos Draft/Oracle (NADR-12 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Modelar el Ground Truth como entidad de dominio cuyo tipo está determinado por su estado de ciclo de vida | NADR-12 §5.1 R1 | High | — | TODO |
| **1.1.2** | Definir tipos disjuntos para el estado de borrador curado y el estado de oráculo sellado, sin conversión implícita | NADR-12 §5.1 R2 | High | 1.1.1 | TODO |
| **1.1.3** | Garantizar que un artefacto serializado no sea tratado como oráculo sin hidratación y validación previas vía contrato canónico | NADR-12 §5.1 R3 | High | 1.1.2 | TODO |

#### Notas de implementación — Wave 1.1
> {Se actualiza al completar la Wave.}

### 2.2 Wave 1.2 — Ciclo de vida y no-inferencia de estado (NADR-12 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Definir explícitamente los estados de ciclo de vida (borrador, auditado, validado, sellado) y las únicas transiciones permitidas | NADR-12 §5.2 R4 | High | 1.1.3 | TODO |
| **1.2.2** | Eliminar toda inferencia de estado de sellado a partir de presencia de archivo o campo incidental | NADR-12 §5.2 R5 | High | 1.2.1 | TODO |
| **1.2.3** | Asegurar que toda transición de estado sea producida por una operación explícita y gobernada, nunca como efecto lateral | NADR-12 §5.2 R6 | High | 1.2.1 | TODO |

#### Notas de implementación — Wave 1.2
> {Se actualiza al completar la Wave.}

### 2.3 Wave 1.3 — Inmutabilidad y reemplazo (NADR-12 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Forzar inmutabilidad de las entidades de ciclo de vida; toda transición produce una nueva instancia | NADR-12 §5.3 R7 | Medium | 1.2.3 | TODO |
| **1.3.2** | Permitir el reemplazo de un borrador por una nueva instancia durante la curaduría; prohibir mutación in-place | NADR-12 §5.3 R8 | Medium | 1.3.1 | TODO |
| **1.3.3** | Impedir que un oráculo sellado sea alterado o sobrescrito por operaciones de curaduría | NADR-12 §5.3 R9 | High | 1.3.1 | TODO |

#### Notas de implementación — Wave 1.3
> {Se actualiza al completar la Wave.}

#### Notas de referencia cruzada (§1.4)
> NADR-12 §5.1 R3 (Task 1.1.3) referencia el contrato canónico de serialización gobernado por NADR-F17BIS-01 (Fase 1). No hay doble implementación: NADR-01 gobierna la representación canónica del AST; la Task 1.1.3 únicamente la consume como precondición de hidratación.

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.4 Gate 1 Exit Criteria

Todas las reglas de NADR-F17BIS-12 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:
- Existe una entidad de dominio cuyo tipo está determinado por el estado de ciclo de vida
- Los tipos de borrador y oráculo sellado son disjuntos y no convertibles implícitamente
- Ningún consumidor infiere el estado de sellado desde la presencia de un artefacto
- Las entidades de ciclo de vida son inmutables; las transiciones producen nuevas instancias
- Un oráculo sellado no puede ser sobrescrito por curaduría

### 2.5 Gate 1 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde (baseline 274+ mantenida) | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 2 — GROUND TRUTH VALIDITY & BASELINE COMPLETENESS

**Objective:** Materializar el contrato de validez estructural del oráculo y la completitud biyectiva de la baseline (Zero Partial Sealing), con sellado atómico.
**NADRs afectados:** NADR-F17BIS-13 (10 reglas)
**Execution Mode:** Secuencial (depende de Gate 1)
**Rollback Plan:** `git revert` de los contratos de validez y completitud; el sellado retorna al comportamiento de Fase 1 (no recomendado — reproduce el defecto P0).
**Gate Status:** ⏳ PENDING

### 2.6 Wave 2.1 — Contrato de validez estructural (NADR-13 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Definir un contrato explícito de validez estructural que todo oráculo debe satisfacer antes del sellado | NADR-13 §5.1 R1 | High | Gate 1 | TODO |
| **2.1.2** | Incluir en el contrato la no-vaciedad del contenido, la integridad de los nodos y la coherencia estructural | NADR-13 §5.1 R2 | High | 2.1.1 | TODO |
| **2.1.3** | Rechazar de forma explícita e inmediata el sellado de todo oráculo que no satisfaga el contrato de validez | NADR-13 §5.1 R3 | Critical | 2.1.2 | TODO |

#### Notas de implementación — Wave 2.1
> {Se actualiza al completar la Wave.}

### 2.7 Wave 2.2 — Completitud biyectiva (NADR-13 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Forzar la correspondencia biyectiva completa entre documentos fuente declarados y sus oráculos | NADR-13 §5.2 R4 | Critical | 2.1.3 | TODO |
| **2.2.2** | Verificar la completitud en ambas direcciones (documento→oráculo y oráculo→documento) | NADR-13 §5.2 R5 | Critical | 2.2.1 | TODO |
| **2.2.3** | Abortar el sellado mediante fallo explícito ante la ausencia de oráculo para un documento fuente declarado | NADR-13 §5.2 R6 | Critical | 2.2.2 | TODO |
| **2.2.4** | Detectar oráculos huérfanos (sin documento fuente declarado) y abortar el sellado | NADR-13 §5.2 R7 | Critical | 2.2.2 | TODO |
| **2.2.5** | Prohibir la degradación de la incompletitud a advertencias no bloqueantes | NADR-13 §5.2 R8 | High | 2.2.3 | TODO |

#### Notas de implementación — Wave 2.2
> {Se actualiza al completar la Wave.}

### 2.8 Wave 2.3 — Atomicidad del sellado (NADR-13 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Hacer del sellado una operación atómica: se certifica la baseline completa y válida, o no se certifica nada | NADR-13 §5.3 R9 | Critical | 2.2.5 | TODO |
| **2.3.2** | Garantizar que un sellado abortado no deje una baseline parcialmente certificada ni un manifiesto inconsistente | NADR-13 §5.3 R10 | Critical | 2.3.1 | TODO |

#### Notas de implementación — Wave 2.3
> {Se actualiza al completar la Wave.}

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.9 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-13 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Todo oráculo es validado estructuralmente antes del sello
- La biyección documento↔oráculo se verifica en ambas direcciones
- La ausencia de un oráculo o la presencia de un oráculo huérfano aborta el sellado con fallo explícito
- El sellado es atómico; un aborto no deja baseline parcial

### 2.10 Gate 2 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 3 — CURATION/RUNTIME PORT ASYMMETRY & SEALING AUTHORITY

**Objective:** Segregar las superficies de acceso de curaduría y runtime en puertos asimétricos, y consolidar una única autoridad de sellado gobernada.
**NADRs afectados:** NADR-F17BIS-14 (9 reglas)
**Execution Mode:** Secuencial (depende de Gate 2)
**Rollback Plan:** `git revert` de la segregación de puertos; restaurar la autoridad de sellado previa.
**Gate Status:** ⏳ PENDING

### 2.11 Wave 3.1 — Asimetría de puertos (NADR-14 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Exponer las operaciones de curaduría (escritura) y de runtime (lectura) sobre la baseline mediante contratos de acceso distintos | NADR-14 §5.1 R1 | High | Gate 2 | TODO |
| **3.1.2** | Garantizar que el contrato de lectura de runtime no exponga capacidad de escritura ni mutación de la baseline | NADR-14 §5.1 R2 | High | 3.1.1 | TODO |
| **3.1.3** | Impedir que el contrato de curaduría sea consumido por los caminos de runtime que leen la baseline certificada | NADR-14 §5.1 R3 | High | 3.1.1 | TODO |

#### Notas de implementación — Wave 3.1
> {Se actualiza al completar la Wave.}

### 2.12 Wave 3.2 — Autoridad única de sellado (NADR-14 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Consolidar la certificación de oráculos y baselines en una única autoridad de sellado | NADR-14 §5.2 R4 | High | 3.1.3 | TODO |
| **3.2.2** | Eliminar la coexistencia de múltiples autoridades de sellado con lógica duplicada o divergente | NADR-14 §5.2 R5 | Medium | 3.2.1 | TODO |
| **3.2.3** | Asegurar que toda operación de sellado delegue en la autoridad única, sin rutas alternativas | NADR-14 §5.2 R6 | High | 3.2.1 | TODO |

#### Notas de implementación — Wave 3.2
> {Se actualiza al completar la Wave.}

### 2.13 Wave 3.3 — Superficie de curaduría gobernada (NADR-14 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Componer las dependencias de todo punto de entrada de curaduría/sellado conforme a la raíz de composición establecida | NADR-14 §5.3 R7 | Medium | 3.2.3 | TODO |
| **3.3.2** | Propagar los fallos de integridad durante curaduría/sellado como errores explícitos, sin degradación a advertencias | NADR-14 §5.3 R8 | High | 3.3.1 | TODO |
| **3.3.3** | Proveer explícitamente los parámetros que determinan la identidad de la baseline (versión objetivo del sello), sin fijación implícita | NADR-14 §5.3 R9 | Medium | 3.3.1 | TODO |

#### Notas de implementación — Wave 3.3
> {Se actualiza al completar la Wave.}

#### Notas de referencia cruzada (§1.4)
> NADR-14 §5.3 R7 (Task 3.3.1) referencia la raíz de composición gobernada por NADR-F17BIS-11 (Fase 1). No hay doble implementación: NADR-11 gobierna la composición del pipeline de traducción; la Task 3.3.1 extiende el mismo principio a los entry points de curaduría de la baseline.

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.14 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-14 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Los contratos de lectura y escritura de la baseline están segregados
- El camino de runtime no puede invocar operaciones de escritura
- Existe una única autoridad de sellado; la duplicación de lógica de linaje ha sido erradicada
- Los entry points de curaduría componen vía raíz de composición y propagan fallos explícitos

### 2.15 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## GATE 4 — SEMANTIC IDENTITY LINEAGE IN THE BASELINE MODEL

**Objective:** Portar la identidad semántica del oráculo como linaje de primera clase, separar las dimensiones de identidad y diferenciar las versiones de esquema/corpus/baseline.
**NADRs afectados:** NADR-F17BIS-15 (9 reglas)
**Execution Mode:** Secuencial (depende de Gate 3)
**Rollback Plan:** `git revert` del modelo de linaje de identidad; el modelo retorna al estado de integridad de bytes de Fase 1.
**Gate Status:** ⏳ PENDING

### 2.16 Wave 4.1 — Linaje de identidad semántica (NADR-15 §5.1)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Portar la identidad semántica del oráculo como parte de su linaje dentro del modelo de baseline | NADR-15 §5.1 R1 | High | Gate 3 | TODO |
| **4.1.2** | Incluir la identidad semántica del oráculo en el linaje del sellado, además de la integridad del artefacto | NADR-15 §5.1 R2 | High | 4.1.1 | TODO |
| **4.1.3** | Asegurar que la identidad semántica corresponda a la firma semántica determinista del AST gobernada por el contrato canónico de hashing | NADR-15 §5.1 R3 | High | 4.1.2 | TODO |

#### Notas de implementación — Wave 4.1
> {Se actualiza al completar la Wave.}

### 2.17 Wave 4.2 — Separación de dimensiones de identidad (NADR-15 §5.2)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Residir las dimensiones de identidad (semántica, integridad del artefacto, identidad física del documento fuente, versión de esquema) en lugares ontológicos diferenciados | NADR-15 §5.2 R4 | High | 4.1.3 | TODO |
| **4.2.2** | Prohibir el colapso de dos o más dimensiones de identidad en un único campo o mecanismo | NADR-15 §5.2 R5 | High | 4.2.1 | TODO |
| **4.2.3** | Impedir que el hash de integridad de los bytes de un artefacto sea utilizado como identidad semántica del oráculo | NADR-15 §5.2 R6 | Critical | 4.2.1 | TODO |
| **4.2.4** | Impedir que la identidad física del documento fuente incorpore la identidad semántica del oráculo | NADR-15 §5.2 R7 | High | 4.2.1 | TODO |

#### Notas de implementación — Wave 4.2
> {Se actualiza al completar la Wave.}

### 2.18 Wave 4.3 — Diferenciación de versiones (NADR-15 §5.3)

**Wave Status:** ⏳ PENDING

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Diferenciar la versión del esquema del AST, la versión del corpus y la identidad de la baseline en el modelo de identidad | NADR-15 §5.3 R8 | High | 4.2.4 | TODO |
| **4.3.2** | Hacer la firma del catálogo sensible al linaje de los oráculos; una mutación de oráculo altera la firma resultante | NADR-15 §5.3 R9 | Critical | 4.3.1 | TODO |

#### Notas de implementación — Wave 4.3
> {Se actualiza al completar la Wave.}

#### Notas de referencia cruzada (§1.4)
> NADR-15 §5.1 R3 (Task 4.1.3) referencia la firma semántica determinista gobernada por NADR-F17BIS-03 (Fase 1). No hay doble implementación: NADR-03 gobierna la fórmula de `compute_ast_hash`; la Task 4.1.3 únicamente consume esa firma como identidad semántica del oráculo.

#### Hallazgos identificados en esta Wave
| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | {Se registra durante la implementación} | Findings Register |

### 2.19 Gate 4 Exit Criteria

Todas las reglas de NADR-F17BIS-15 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- El oráculo sellado porta su identidad semántica como linaje de primera clase
- Las dimensiones de identidad (semántica, integridad, física, esquema) están diferenciadas y no colapsadas
- La versión de esquema, versión de corpus e identidad de baseline están diferenciadas
- La firma del catálogo es sensible al linaje de los oráculos

### 2.20 Gate 4 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** {YYYY-MM-DD}

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 (Ontología) | — | 0/9 | 0/9 | 0 | — |
| Gate 2 (Validez/Completitud) | — | 0/10 | 0/10 | 0 | — |
| Gate 3 (Autoridad/Puertos) | — | 0/9 | 0/9 | 0 | — |
| Gate 4 (Identidad Semántica) | — | 0/9 | 0/9 | 0 | — |

---

## 4. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-F2-01** | Verificar que los entry points de curaduría (`bootstrap_corpus`, `freeze_ground_truth`, `generate_golden_draft`) operan contra la nueva ontología sin degradación | Local | NADR-14 §5.3 R7, R8 | Smoke test de curaduría | TODO |

> **Nota:** La migración de artefactos de baseline existentes (re-sellado) y la materialización del corpus canónico en disco **NO** pertenecen a la Fase 2. El re-sellado criptográfico es responsabilidad de la Fase 3 (Identity & Trust Model, `MIG-01` del plan global) y la materialización de la Fase 5 (Baseline Certification). La Fase 2 formaliza la ontología; no puebla ni re-sella artefactos.

---

## 5. GLOBAL DoD (Definition of Done)

La Fase 2 (Scientific Baseline Domain) se considera oficialmente completada cuando:

```text
{All rules in APPROVED NADRs F17BIS-12..15} − {Rules with DONE status in §7} = ∅
```

Es decir, las **37 reglas** de NADR-F17BIS-12..15 deben estar en estado `DONE`.

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 (Ontología) | 0 | 0 | 0 | 9 | ⏳ PENDING |
| Gate 2 (Validez/Completitud) | 0 | 0 | 0 | 10 | ⏳ PENDING |
| Gate 3 (Autoridad/Puertos) | 0 | 0 | 0 | 9 | ⏳ PENDING |
| Gate 4 (Identidad Semántica) | 0 | 0 | 0 | 9 | ⏳ PENDING |
| **TOTAL** | **0** | **0** | **0** | **37** | ⏳ PENDING |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task
3. Se actualiza el `Derived Status` de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 7.1 Gate 1 — NADR-F17BIS-12 (Oracle Ontology & Lifecycle)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-12 §5.1 R1 | PENDING | Task 1.1.1 | — |
| NADR-12 §5.1 R2 | PENDING | Task 1.1.2 | — |
| NADR-12 §5.1 R3 | PENDING | Task 1.1.3 | — |
| NADR-12 §5.2 R4 | PENDING | Task 1.2.1 | — |
| NADR-12 §5.2 R5 | PENDING | Task 1.2.2 | — |
| NADR-12 §5.2 R6 | PENDING | Task 1.2.3 | — |
| NADR-12 §5.3 R7 | PENDING | Task 1.3.1 | — |
| NADR-12 §5.3 R8 | PENDING | Task 1.3.2 | — |
| NADR-12 §5.3 R9 | PENDING | Task 1.3.3 | — |

### 7.2 Gate 2 — NADR-F17BIS-13 (Validity & Completeness)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-13 §5.1 R1 | PENDING | Task 2.1.1 | — |
| NADR-13 §5.1 R2 | PENDING | Task 2.1.2 | — |
| NADR-13 §5.1 R3 | PENDING | Task 2.1.3 | — |
| NADR-13 §5.2 R4 | PENDING | Task 2.2.1 | — |
| NADR-13 §5.2 R5 | PENDING | Task 2.2.2 | — |
| NADR-13 §5.2 R6 | PENDING | Task 2.2.3 | — |
| NADR-13 §5.2 R7 | PENDING | Task 2.2.4 | — |
| NADR-13 §5.2 R8 | PENDING | Task 2.2.5 | — |
| NADR-13 §5.3 R9 | PENDING | Task 2.3.1 | — |
| NADR-13 §5.3 R10 | PENDING | Task 2.3.2 | — |

### 7.3 Gate 3 — NADR-F17BIS-14 (Port Asymmetry & Sealing Authority)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-14 §5.1 R1 | PENDING | Task 3.1.1 | — |
| NADR-14 §5.1 R2 | PENDING | Task 3.1.2 | — |
| NADR-14 §5.1 R3 | PENDING | Task 3.1.3 | — |
| NADR-14 §5.2 R4 | PENDING | Task 3.2.1 | — |
| NADR-14 §5.2 R5 | PENDING | Task 3.2.2 | — |
| NADR-14 §5.2 R6 | PENDING | Task 3.2.3 | — |
| NADR-14 §5.3 R7 | PENDING | Task 3.3.1 | — |
| NADR-14 §5.3 R8 | PENDING | Task 3.3.2 | — |
| NADR-14 §5.3 R9 | PENDING | Task 3.3.3 | — |

### 7.4 Gate 4 — NADR-F17BIS-15 (Semantic Identity Lineage)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-15 §5.1 R1 | PENDING | Task 4.1.1 | — |
| NADR-15 §5.1 R2 | PENDING | Task 4.1.2 | — |
| NADR-15 §5.1 R3 | PENDING | Task 4.1.3 | — |
| NADR-15 §5.2 R4 | PENDING | Task 4.2.1 | — |
| NADR-15 §5.2 R5 | PENDING | Task 4.2.2 | — |
| NADR-15 §5.2 R6 | PENDING | Task 4.2.3 | — |
| NADR-15 §5.2 R7 | PENDING | Task 4.2.4 | — |
| NADR-15 §5.3 R8 | PENDING | Task 4.3.1 | — |
| NADR-15 §5.3 R9 | PENDING | Task 4.3.2 | — |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.3.

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

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.2.0.

* **El ADR Maestro** (`ADR_F17_BIS_MASTER.md`) define la visión arquitectónica de la fase (el QUÉ y el POR QUÉ).
* **El ADR de Fase** (`ADR_F17_BIS_02.md`) particulariza la decisión para la sub-fase Scientific Baseline Domain.
* **Las reglas técnicas obligatorias** se encuentran promulgadas en NADR-F17BIS-12 a NADR-F17BIS-15.
* **Este Execution Plan** define la secuencia operativa, tareas concretas y seguimiento de cumplimiento.
* **El Deferred Findings Register** (`FASE_2_DEFERRED_FINDINGS_REGISTER.md`) registra los hallazgos identificados, su clasificación y resolución.

Este documento **no prescribe decisiones arquitectónicas, criterios de revisión de código ni registro de hallazgos.**

---

## 10. FUTURE WORK

> El Traceability Appendix (§7) se escribe manualmente en esta versión. Versiones futuras **PODRÍAN** generar este appendix automáticamente desde metadatos de tareas, eliminando la sincronización manual. Esta nota evita asumir que el appendix debe mantenerse siempre a mano.
>
> La Fase 2 formaliza la ontología del oráculo. La materialización en disco del corpus canónico (Fase 5) y el encadenamiento criptográfico global $H_{baseline}$ (Fase 3) construirán sobre esta ontología sin modificarla.

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task
1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 11.2 Al completar una Task
1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task
3. Actualizar el `Derived Status` de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo
1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave"
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 11.4 Al cerrar un Gate
1. Verificar el Gate Exit Review Checklist
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§3)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 11.5 Al cancelar una operación de Deployment
1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§4)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§11.3)

### 11.6 Prohibiciones
- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre las reglas normativas de NADR-F17BIS-12..15 y su implementación en la Fase 2. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs APPROVED, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.