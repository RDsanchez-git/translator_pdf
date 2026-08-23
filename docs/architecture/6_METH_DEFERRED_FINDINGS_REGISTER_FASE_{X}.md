# FASE_{X}_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-{fase}/reviews/FASE_{X}_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** {X.Y.Z}
**Estado:** {IN_PROGRESS | ARCHIVED}
**Fecha de creación:** {YYYY-MM-DD}
**Última actualización:** {YYYY-MM-DD}
**Derivado de:** `PHASE_{FASE}_EXECUTION_PLAN.md` v{versión}
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan, su clasificación, resolución y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_{FASE}_MASTER > ADR_{FASE}_{XX} > NADR-{XX}..{YY} > PHASE_{FASE}_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"{Pregunta rectora específica de la fase. Ejemplo: ¿La existencia de
> este finding impide que la Scientific Baseline sea una representación
> determinista, reproducible y arquitectónicamente fiel del pipeline
> productivo que vamos a certificar?}"*

### 0.3 Reglas transversales aplicables

> {Citar reglas transversales que aplican al análisis de hallazgos.
> Ejemplo: Corolario forense P2, Separación de identidades, etc.}

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

---

## 2. GATE EXIT REVIEWS

{Una sub-sección por cada Gate ejecutado. Se agregan dinámicamente.}

### 2.{N} Gate {N} Exit Review ({YYYY-MM-DD})

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-{XX} | {✅ Sí / ❌ No / ⚠️ Parcial} | {✅ Sí / ❌ No} | {✅ Sí / ❌ No} | {Decisión} | {Motivo} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})
- Revisiones tardías documentadas: {N} ({DF-XX})

#### Decisiones arquitectónicas congeladas en Gate {N} (si aplica)

| Decisión | Task | Justificación |
|----------|------|---------------|
| {Decisión} | {Task ID} | {NADR/Principio que la respalda} |

#### Lecciones aprendidas (si aplica)

- {Lección 1}
- {Lección 2}

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | {N} | {DF-XX, DF-YY} |
| `RESOLVED — DELETE` | {N} | {DF-XX} |
| `RESOLVED` | {N} | {DF-XX} |
| `IMPLEMENTATION_REQUIRED` | {N} | {DF-XX} |
| `RECLASSIFIED_FUTURE_PHASE` | {N} | {DF-XX} |
| `REVIEW_REQUIRED` | {N} | {DF-XX} |
| `ACCEPTED_LIMITATION` | {N} | {DF-XX} |

### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| {DF/GF-XX} | `{Estado final}` | {Descripción breve} |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Una sub-sección por cada batch ejecutado. Se agregan dinámicamente.}

### 4.{N} BATCH {N} — {NOMBRE DEL BATCH} ({Completado/Pendiente})

**Fecha de ejecución:** {YYYY-MM-DD}
**Validación:** Pyright {N} errors | pytest {X} passed, {Y} skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-{XX}** | `{RESOLVED — ACCIÓN}` | {Acción} | {Lista de archivos} | ✅ {Evidencia} |

#### Correcciones adicionales durante ejecución

- {Corrección 1}
- {Corrección 2}

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| {H-XX-X} | {Descripción} | {REVIEW_REQUIRED / etc.} | {Acción} |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| NADR-{XX} | §{Y.Z} R{N} | {Evidencia de cumplimiento} |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| {Decisión} | {NADR/Principio} | {Qué se rechazó y por qué} |

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
| Total de hallazgos analizados | {N} |
| Hallazgos resueltos | {N} |
| Hallazgos cerrados sin acción | {N} |
| Hallazgos reclasificados a fase futura | {N} |
| Hallazgos pendientes de implementación | {N} |
| Hallazgos pendientes de revisión | {N} |
| Batches completados | {N} |
| Archivos eliminados totales | {N} |
| Archivos movidos totales | {N} |
| Archivos creados totales | {N} |
| Tests finales | {X} passed, {Y} skipped |
| Pyright final | {N} errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| DF-{XX} | {Fase destino} | {Razón por la que se difiere} |

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

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | {N} |
| Hallazgos resueltos | {N} |
| Hallazgos pendientes de implementación | {N} |
| Hallazgos pendientes de revisión | {N} |
| Hallazgos cerrados sin acción | {N} |
| Batches completados | {N}/{Total} |
| Estado del Exit Review | {🟡 IN PROGRESS / ✅ CERRADO} |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución.