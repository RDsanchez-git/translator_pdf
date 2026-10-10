# FASE_18.2_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-18/reviews/FASE_18.2_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 1.0.0
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-10-10
**Última actualización:** 2026-10-10
**Derivado de:** `PHASE_18.2_EXECUTION_PLAN.md` v1.2.1
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de la Subfase 18.2 (Durable Execution & Recovery), su clasificación,
resolución y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F18_MASTER v1.0.0 FROZEN
    ↓
ADR_F18.2 v3.3.0 FROZEN
    ↓
NADR-F18-03 v1.2.0 FROZEN | NADR-F18-04 v1.1.1 FROZEN | NADR-F18-05 v1.3.0 FROZEN
    ↓
PHASE_18.2_EXECUTION_PLAN v1.2.1
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que el execution plane garantice
> una ejecución durable con recuperación coherente bajo el modelo de fallos
> aprobado, manteniendo la separación entre autoridad de ejecución, efectos
> externos inciertos y confirmación local idempotente, sin atribuir al
> proveedor capacidades no verificadas ni prometer exactly-once no demostrado?"*

### 0.3 Reglas transversales aplicables

**De ADR_F18.2 v3.3.0 FROZEN:**
- DC-08: Separación entre intención durable pre-efecto y resolución de efectos inciertos
- DC-08a: Reutilización del lease existente como mecanismo principal de intención pre-efecto
- DC-08b: Política de no-reejecución automática bajo incertidumbre
- DC-08c: Taxonomía estratificada de duplicación (actividad cliente vs evidencia externa)
- DC-08d: Modelo de fallos acotado (WAL+NORMAL, exclusión de power loss)

**De NADR-F18-03 v1.2.0 FROZEN:**
- §5.1: Autoridad de ejecución pre-efecto recuperable
- §5.2: Clasificación semántica de resultados (confirmado/no iniciado/incierto)
- §5.3: Prohibición de reejecución automática bajo incertidumbre
- §5.5: Preservación de identidad científica vs identidad de intento

**De NADR-F18-04 v1.1.1 FROZEN:**
- §5.1: Durabilidad conforme al modelo de fallos aprobado
- §5.2: Idempotencia de aplicación local
- §5.3: Coherencia y recuperación entre planos
- §5.4: Separación explícita de propiedades (atomicidad/durabilidad/idempotencia/recuperabilidad)

**De NADR-F18-05 v1.3.0 FROZEN:**
- §5.2: Distinción entre actividad cliente y evidencia de duplicación externa
- §5.3: Límites epistemológicos de medición (ventana cliente vs ventana causal)
- §5.4: Separación de costes observados/estimados/exposición potencial
- §5.5: Integridad de evidencia sin crear fuentes de verdad paralelas

**De ENGINEERING_PRINCIPLES:**
- §I YAGNI: No sobreingeniería de mecanismos de recovery
- §II Hexagonal: Separación de puertos y adaptadores
- §VII Reuse Before Invent: Reutilización de maquinaria existente

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-18.2-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación de Subfase 18.2 |
| `GF-18.2-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-18.2-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

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
| `DEFERRED_CONDITIONAL` | Diferimiento condicionado con trigger pendiente (DF-24, DF-34) |
| `ESCALATED_TO_BOARD` | Requiere decisión del Architecture Board |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos/documentos auditados.
- Cada finding **DEBE** distinguir: (a) gap confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún finding se cierra sin evidencia de código o documental.
- No se implementa código durante el Exit Review. La implementación se agrupa en batches posteriores.
- Para hallazgos relacionados con efectos externos, **DEBE** declararse explícitamente si la evidencia es local (cliente) o requiere verificación del proveedor.

### 1.4 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Trigger de diferimiento activado (DF-24/DF-34) | Evaluar y documentar disposición conforme a gobernanza |
| Fase cerrada | Estado del documento → `ARCHIVED` |

---

## 2. GATE EXIT REVIEWS

{Se agregan dinámicamente conforme se ejecutan los gates.}

### 2.0 Gate 0 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 0 — Baseline & Contract Readiness**
- Wave 0.1: Rule & Evidence Mapping (Tasks 0.1.1, 0.1.2, 0.1.3)
- Wave 0.2: Operational Baseline (Tasks 0.2.1, 0.2.2)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 0

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

---

### 2.1 Gate 1 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 1 — Execution Authority & Conservative Recovery**
- Wave 1.1: Pre-effect Authority (Tasks 1.1.1, 1.1.2, 1.1.3)
- Wave 1.2: Conservative Reconciliation (Tasks 1.2.1, 1.2.2, 1.2.3, 1.2.4, 1.2.5)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 1

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

---

### 2.2 Gate 2 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 2 — Durable Local Apply & Recovery**
- Wave 2.1: Durability & Idempotent Apply (Tasks 2.1.1, 2.1.2, 2.1.3)
- Wave 2.2: Recovery Convergence (Tasks 2.2.1, 2.2.2, 2.2.3, 2.2.4)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 2

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

---

### 2.3 Gate 3 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 3 — Exposure Observability & FinOps**
- Wave 3.1: Correlation & Evidence (Tasks 3.1.1, 3.1.2)
- Wave 3.2: Measurement & Financial Exposure (Tasks 3.2.1, 3.2.2, 3.2.3)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 3

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

---

### 2.4 Gate 4 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 4 — Integrated Empirical Validation**
- Wave 4.1: Chaos Harness & Convergence Validation (Tasks 4.1.1, 4.1.2, 4.1.3)
- Wave 4.2: Direct Measurement & External Fencing (Tasks 4.2.1, 4.2.2, 4.2.3)
- Wave 4.3: Durability & Power Loss Characterization (Tasks 4.3.1, 4.3.2)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 4

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

---

### 2.5 Gate 5 Exit Review ({YYYY-MM-DD})

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

**Gate 5 — Phase Closure & Deferred Findings Resolution**
- Wave 5.1: Deferred Findings Evaluation (Tasks 5.1.1, 5.1.2, 5.1.3, 5.1.4)
- Wave 5.2: Documentation & Handoff (Tasks 5.2.1, 5.2.2, 5.2.3)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos aún |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate posterior: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Revisiones tardías documentadas: 0

#### Hallazgos identificados en Gate 5

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

#### Evaluación de diferimientos condicionados

**DF-24 (CircuitBreaker persistencia):**
- Trigger evaluado: {SÍ/NO/PARCIAL}
- Medición de impacto: {completada/pendiente/inconclusa}
- Disposición: {ACCEPTED_LIMITATION / ESCALATED_TO_BOARD / DEFERRED_CONDITIONAL}
- Justificación: {pendiente de completar}

**DF-34 (ProfileStore persistencia):**
- Trigger evaluado: {SÍ/NO/PARCIAL}
- Benchmark de coste: {completado/pendiente/inconcluso}
- Disposición: {ACCEPTED_LIMITATION / ESCALATED_TO_BOARD / DEFERRED_CONDITIONAL}
- Justificación: {pendiente de completar}

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED — MOVE` | 0 | — |
| `RESOLVED — REFACTORED` | 0 | — |
| `RESOLVED — FACTORY EXTRACTION` | 0 | — |
| `RESOLVED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |
| `DEFERRED_CONDITIONAL` | 0 | — |
| `ESCALATED_TO_BOARD` | 0 | — |

### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| — | — | Sin hallazgos aún |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Se agregan dinámicamente conforme se ejecutan los batches.}

### 4.1 BATCH 1 — {NOMBRE DEL BATCH} ({Completado/Pendiente})

**Fecha de ejecución:** {YYYY-MM-DD}
**Validación:** Pyright {N} errors | pytest {X} passed, {Y} skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| — | — | — | — | Sin batches aún |

#### Correcciones adicionales durante ejecución

- {pendiente de completar}

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | Sin hallazgos aún |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| — | — | {pendiente de completar} |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| — | — | {pendiente de completar} |

#### Métricas post-batch

| Métrica | Valor |
|---------|-------|
| Archivos creados | {N} |
| Archivos modificados | {N} |
| Archivos eliminados | {N} |
| Archivos movidos | {N} |
| Imports corregidos | {N} |
| Tests ejecutados | {X} passed, {Y} skipped |
| Errores de tipo estático | {N} |

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
| Hallazgos diferidos condicionados | 0 |
| Hallazgos escalados al Board | 0 |
| Batches completados | 0 |
| Archivos eliminados totales | 0 |
| Archivos movidos totales | 0 |
| Archivos creados totales | 0 |
| Tests finales | {baseline: 854 passed} |
| Pyright final | {baseline: 0 errors} |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| — | — | Sin diferimientos aún |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida o incrementada desde 854)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados
5. La evidencia de implementación se adjunta al DF correspondiente

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
5. Los hallazgos `DEFERRED_CONDITIONAL` (DF-24, DF-34) tienen disposición documentada
6. Los hallazgos `ESCALATED_TO_BOARD` tienen resolución formal del Architecture Board
7. Todos los Gates (0-5) están en estado COMPLETED
8. El Exit Review Evidence Log está FROZEN

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 0 |
| Hallazgos resueltos | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos diferidos condicionados | 0 |
| Hallazgos escalados al Board | 0 |
| Batches completados | 0/{Total} |
| Estado del Exit Review | ⏳ NOT STARTED |

---

## 9. DIFERIMIENTOS CONDICIONADOS (DF-24, DF-34)

### 9.1 DF-24: CircuitBreaker persistencia

**Trigger:** Medición de impacto efectivo de warm-up
**Autoridad de decisión:** Architecture Board
**Disposición actual:** `DEFERRED_CONDITIONAL`

| Aspecto | Estado |
|---------|--------|
| Trigger activado | {SÍ/NO/PARCIAL} |
| Medición completada | {pendiente} |
| Tiempo de recuperación medido | {pendiente} |
| Llamadas fallidas durante warm-up | {pendiente} |
| Impacto FinOps | {pendiente} |
| Disposición final | {ACCEPTED_LIMITATION / ESCALATED_TO_BOARD / DEFERRED_CONDITIONAL} |
| Justificación | {pendiente} |

### 9.2 DF-34: ProfileStore persistencia

**Trigger:** Benchmark de coste de re-inferencia
**Autoridad de decisión:** Architecture Board
**Disposición actual:** `DEFERRED_CONDITIONAL`

| Aspecto | Estado |
|---------|--------|
| Trigger activado | {SÍ/NO/PARCIAL} |
| Benchmark completado | {pendiente} |
| Coste de CPU medido | {pendiente} |
| Latencia de re-inferencia | {pendiente} |
| Estabilidad del resultado | {pendiente} |
| Aceptabilidad operacional | {pendiente} |
| Disposición final | {ACCEPTED_LIMITATION / ESCALATED_TO_BOARD / DEFERRED_CONDITIONAL} |
| Justificación | {pendiente} |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan de la Subfase 18.2 y su resolución. Las decisiones de
gobernanza (escalaciones al Board, diferimientos condicionados) se documentan
aquí pero se resuelven mediante los canales normativos correspondientes.