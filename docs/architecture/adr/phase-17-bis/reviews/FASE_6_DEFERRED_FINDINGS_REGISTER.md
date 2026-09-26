# FASE_6_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.2.0
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-09-25
**Última actualización:** 2026-09-26
**Derivado de:** `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.3
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de Fase 6 (Continuous Verification), su clasificación, resolución
y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_06 v1.2.0 > NADR-F17BIS-25..30 > PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.3
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que Continuous Verification sea
> un control operativo efectivo, reproducible y arquitectónicamente fiel
> sobre el pipeline productivo, con enforcement demostrable sobre la
> integración de cambios?"*

### 0.3 Reglas transversales aplicables

- **ENGINEERING_PRINCIPLES §I (Reuse Before Invent):** Ningún finding puede justificar la creación de un mecanismo paralelo si existe capacidad normativa que lo resuelve.
- **ENGINEERING_PRINCIPLES §II (Functional Core / Imperative Shell):** Los hallazgos deben respetar la separación entre lógica de dominio e infraestructura.
- **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):** Ningún finding puede cerrarse como NAR si existe un fallo no indexable asociado. Todo fallo debe ser explícito o derivar en implementación.
- **NADR-F17BIS-27 §5.1 R1-R5:** La semántica de resultados distingue evaluación científica de estado operacional. Un finding sobre ambigüedad semántica no puede cerrarse como NAR.
- **NADR-F17BIS-30 §5.5 R14-R16:** NO DEMOSTRADO no es una forma alternativa de DONE. Un finding sobre enforcement sin evidencia externa no puede cerrarse como RESOLVED sin evidencia server-side.
- **ADR_F17_BIS_MASTER §5 (Determinismo y Reproducibilidad):** Todo hallazgo que afecte la reproducibilidad de la verificación debe clasificarse como IMPLEMENTATION_REQUIRED o ACCEPTED_LIMITATION con justificación explícita.
- **ADR_F17_BIS_06 v1.2.0 D1 (Integración, No Creación):** Ningún finding puede justificar la creación de un segundo mecanismo de verificación.
- **PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.3 §8 (Global DoD):** Un finding que afecta una regla normativa solo se cierra cuando es trazable a una implementación commiteada, un mecanismo de verification superado y un mecanismo de validation superado.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Diferido a fase futura con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `DEFERRED — FASE {X}` | Diferido a fase específica con ADR pendiente |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos/documentos auditados.
- Cada finding **DEBE** distinguir: (a) gap confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún finding se cierra sin evidencia de código o documental.
- No se implementa código durante el Exit Review. La implementación se agrupa en batches posteriores.

### 1.4 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Fase cerrada | Estado del documento → `ARCHIVED` |

### 1.5 Relación con el Execution Plan

Este registro es la **autoridad única** para el ciclo de vida de hallazgos. El Execution Plan (`PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.3) referencia hallazgos por ID pero no los clasifica ni los resuelve.

```text
Execution Plan (Task)
    ↓ identifica hallazgo
Deferred Findings Register (este documento)
    ↓ clasifica y resuelve
Findings Register (autoridad)
    ↓ registra batches
Commits / Tests (evidencia)
```

---

## 2. GATE EXIT REVIEWS

{Una sub-sección por cada Gate ejecutado. Se agregan dinámicamente conforme avanza la implementación.}

### 2.1 Gate 1 Exit Review — Verification Foundation ({YYYY-MM-DD})

**Gate:** Gate 1 — Verification Foundation
**NADRs:** NADR-F17BIS-25 (13 reglas), NADR-F17BIS-26 (28 reglas)
**Tasks:** 1.1.1, 1.1.2, 1.1.3, 1.2.1, 1.2.2, 1.2.3, 1.2.4

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | {Pendiente de ejecución} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})
- Revisiones tardías documentadas: {N} ({DF-XX})

#### Decisiones arquitectónicas congeladas en Gate 1 (si aplica)

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | {Pendiente de ejecución} |

#### Lecciones aprendidas (si aplica)

- {Pendiente de ejecución}

---

### 2.2 Gate 2 Exit Review — Verification Contract ({YYYY-MM-DD})

**Gate:** Gate 2 — Verification Contract
**NADRs:** NADR-F17BIS-27 (35 reglas), NADR-F17BIS-28 (34 reglas)
**Tasks:** 2.1.1, 2.1.2, 2.1.3, 2.2.1, 2.2.2, 2.2.3

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | {Pendiente de ejecución} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})
- Revisiones tardías documentadas: {N} ({DF-XX})

#### Decisiones arquitectónicas congeladas en Gate 2 (si aplica)

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | {Pendiente de ejecución} |

#### Lecciones aprendidas (si aplica)

- {Pendiente de ejecución}

---

### 2.3 Gate 3 Exit Review — Continuous Verification Integration ({YYYY-MM-DD})

**Gate:** Gate 3 — Continuous Verification Integration
**NADRs:** NADR-F17BIS-29 (35 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-29
**Tasks:** 3.1.1, 3.1.2, 3.1.3, 3.2.1, 3.2.2, 3.2.3, 3.3.1, 3.3.2, 3.3.3

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | {Pendiente de ejecución} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})
- Revisiones tardías documentadas: {N} ({DF-XX})

#### Decisiones arquitectónicas congeladas en Gate 3 (si aplica)

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | {Pendiente de ejecución} |

#### Lecciones aprendidas (si aplica)

- {Pendiente de ejecución}

---

### 2.4 Gate 4 Exit Review — Enforcement & Phase Closure ({YYYY-MM-DD})

**Gate:** Gate 4 — Enforcement & Phase Closure
**NADRs:** NADR-F17BIS-30 (22 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-30
**Tasks:** 4.1.1, 4.1.2, 4.1.3, 4.2.1, 4.2.2, 4.2.3, 4.3.1, 4.3.2, 4.3.3

**Nota específica de Gate 4:** Este Gate incluye Tasks con precondiciones externas:
- **Task 4.1.3:** Evidencia server-side de branch protection. Si no se puede obtener, el finding se clasifica como `ACCEPTED_LIMITATION` o `RECLASSIFIED_FUTURE_PHASE` con justificación explícita. NO DEMOSTRADO no es RESOLVED.
- **Task 4.2.1:** PASS path end-to-end. Si no existe un escenario PASS legítimo, el finding se clasifica como `ACCEPTED_LIMITATION` o `IMPLEMENTATION_REQUIRED` según corresponda. No se fabrica un PASS para cerrar el gate.

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
5. ¿Es una limitación externa al perímetro del repositorio? → SÍ: ACCEPTED_LIMITATION con evidencia
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | {Pendiente de ejecución} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- ACCEPTED_LIMITATION: {N} ({DF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})
- Revisiones tardías documentadas: {N} ({DF-XX})

#### Decisiones arquitectónicas congeladas en Gate 4 (si aplica)

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | {Pendiente de ejecución} |

#### Lecciones aprendidas (si aplica)

- {Pendiente de ejecución}

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |

### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| — | — | {Pendiente de ejecución} |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Una sub-sección por cada batch ejecutado. Se agregan dinámicamente conforme avanza la implementación.}

### 4.1 BATCH 1 — {NOMBRE DEL BATCH} ({Completado/Pendiente})

**Fecha de ejecución:** {YYYY-MM-DD}
**Validación:** Pyright {N} errors | pytest {X} passed, {Y} skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| — | — | {Pendiente de ejecución} | — | — |

#### Correcciones adicionales durante ejecución

- {Pendiente de ejecución}

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | {Pendiente de ejecución} |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| — | — | {Pendiente de ejecución} |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| — | — | {Pendiente de ejecución} |

#### Métricas post-batch

| Métrica | Valor |
|---------|-------|
| Archivos creados | 0 |
| Archivos modificados | 0 |
| Archivos eliminados | 0 |
| Archivos movidos | 0 |
| Imports corregidos | 0 |
| Tests ejecutados | 0 passed, 0 skipped |
| Errores de tipo estático | 0 |

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 0 |
| Hallazgos resueltos | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos reclasificados a fase futura | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Batches completados | 0 |
| Archivos eliminados totales | 0 |
| Archivos movidos totales | 0 |
| Archivos creados totales | 0 |
| Tests finales | 0 passed, 0 skipped |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| — | — | {Pendiente de ejecución} |

### 6.1 Candidatos pre-identificados (no constituyen hallazgos registrados)

Los siguientes son escenarios anticipados por el Execution Plan v1.0.3 que **podrían** generar hallazgos diferidos. No se registran como hallazgos hasta que se materialicen durante la implementación:

| Escenario anticipado | Posible destino | Condición de activación |
|---------------------|-----------------|------------------------|
| Evidencia server-side de branch protection no obtenible (Task 4.1.3) | ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE | Si la configuración server-side no es accesible desde el perímetro del repositorio |
| PASS path no demostrable (Task 4.2.1) | ACCEPTED_LIMITATION o IMPLEMENTATION_REQUIRED | Si no existe una ejecución legítima del verification subject que produzca PASS contra la baseline sellada |
| Mecanismo de materialización de PDFs requiere infraestructura externa (Task 1.2.1, MIG-02) | RECLASSIFIED_FUTURE_PHASE o ACCEPTED_LIMITATION | Si la materialización requiere recursos fuera del alcance de Fase 6 |
| Recalibración de thresholds para operatividad del gate | DEFERRED — post Fase 17-BIS | Si la operatividad del gate requiere ajuste de thresholds (DC-6.6, fuera de scope de Fase 6) |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito

### 7.3 Criterio específico de Fase 6

Adicionalmente, para Fase 6:
5. Los hallazgos relacionados con enforcement (NADR-F17BIS-30) tienen evidencia server-side o están documentados como NO DEMOSTRADO con justificación explícita.
6. Los hallazgos relacionados con el PASS path (Task 4.2.1) tienen evidencia de ejecución legítima o están documentados como ACCEPTED_LIMITATION.
7. Ningún hallazgo se cierra como RESOLVED si afecta una regla normativa sin cumplir los criterios de trazabilidad del Global DoD (PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.3 §8).

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 0 |
| Hallazgos resueltos | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Batches completados | 0/{Total} |
| Estado del Exit Review | 🟡 IN PROGRESS |

### 8.1 Progreso por Gate

| Gate | Estado | Hallazgos | Batches |
|------|--------|-----------|---------|
| Gate 1 — Verification Foundation | ⏳ PENDING | 0 | 0 |
| Gate 2 — Verification Contract | ⏳ PENDING | 0 | 0 |
| Gate 3 — Continuous Verification Integration | ⏳ PENDING | 0 | 0 |
| Gate 4 — Enforcement & Phase Closure | ⏳ PENDING | 0 | 0 |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan de Fase 6 y su resolución.