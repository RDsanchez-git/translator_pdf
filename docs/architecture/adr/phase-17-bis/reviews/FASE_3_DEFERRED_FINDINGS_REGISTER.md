# FASE_3_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_3_DEFERRED_FINDINGS_REGISTER.md`  
**Versión:** 1.0.0-COMPLETED  
**Estado:** COMPLETED  
**Fecha de creación:** 2026-08-27  
**Última actualización:** 2026-08-29  
**Derivado de:** `PHASE_17BIS_FASE3_EXECUTION_PLAN.md` v1.1.0  
**Propósito:** Registro auditable de hallazgos identificados durante la implementación del Execution Plan de Fase 3 (Identity & Trust Model), su clasificación, resolución y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17-BIS_03 > NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17 > PHASE_17BIS_FASE3_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Fase 3 logre su objetivo de formalizar el encadenamiento criptográfico global, garantizar la inyectividad del encoding y establecer la semántica de las dimensiones de identidad de manera determinista y reproducible?"*

### 0.3 Reglas transversales aplicables

> **Separación de Identidades (ADR Maestro §3):** Integridad ≠ Identidad ≠ Regresión. Las dimensiones de identidad no se colapsan.

> **Determinismo y Reproducibilidad (ADR Maestro §5):** Todo hash debe ser 100% determinista.

> **Explicit over Implicit (ENGINEERING_PRINCIPLES §III):** Cero "magia" en el código. Validación explícita de dominio.

> **Fail-Fast (ROADMAP §I):** Rechazo explícito en construcción, no advertencias silenciosas.

> **YAGNI (ENGINEERING_PRINCIPLES §I):** No se implementa lógica sin necesidad demostrada.

> **Inmutabilidad (ENGINEERING_PRINCIPLES §II):** Toda transición de estado retorna una copia nueva. Cero mutación in-place.

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
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
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

### 2.1 Gate 1 Exit Review — Formalización Normativa (2026-08-27)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual?
   → SÍ: ¿Requiere implementación de código?
      → SÍ: IMPLEMENTATION_REQUIRED → Batch (METHODOLOGY §6.6) → RESOLVED
      → NO: RESOLVED (resolución documental)
   → NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Ningún hallazgo identificado en Gate 1 |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate 2: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0

**Nota:** La Wave 1.1 (documentación) y Wave 1.2 (limpieza de deuda técnica) se ejecutaron sin identificar hallazgos. La limpieza profunda de DC-08 (eliminación de campos huérfanos, `detected_hashes` y `target_version`) se completó sin generar efectos colaterales. Pyright 0 errors, pytest 368 passed, 5 skipped.

#### Decisiones arquitectónicas congeladas en Gate 1

| Decisión | Task | Justificación |
|----------|------|---------------|
| Eliminación de `detected_hashes` y `target_version` de `ManifestLineageSealer` y `SealGroundTruthUseCase` | 1.2.2 | YAGNI: al eliminar `ground_truth_sha256`, estos parámetros quedaron huérfanos. Eliminarlos evita código muerto y mejora rendimiento (menos I/O). |

#### Lecciones aprendidas

- La limpieza de campos huérfanos puede desbloquear limpiezas más profundas de código muerto (parámetros, cálculos de I/O) que no eran evidentes inicialmente.

---

### 2.2 Gate 2 Exit Review — Validación Explícita de Dominio (2026-08-29)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ✅ Sí (~30 líneas) | ✅ Sí (hardening de dominio) | IMPLEMENTATION_REQUIRED → Batch 1 | Asimetría defensiva con document_id y node_id |

**Resumen:**
- IMPLEMENTATION_REQUIRED: 1 (DF-01)
- CLOSED (NAR): 0
- RECLASSIFIED_FUTURE_PHASE: 0
- Nuevos hallazgos registrados: 1 → resuelto en Batch 1

#### Decisiones arquitectónicas congeladas en Gate 2

| Decisión | Task/Batch | Justificación |
|----------|------|---------------|
| Corrección de causa raíz en DocumentFingerprint.__post_init__ | 2.3.1 | Eliminar islower() redundante que fallaba para hashes sin letras (ej: "0"*64). |
| spawn_fragment con constructor completo | 2.2.1 | Pydantic v2 model_copy(update=...) no revalida campos. Previene bypass del contrato NodeId. |
| parent_node_id: Optional[NodeId] | 2.2.1 | Consistencia de dominio: referencias a node_id deben tener el mismo contrato. |
| GroundTruthState type alias | Batch 1 (DF-01) | Cierre de asimetría defensiva. ground_truth_state participa en framing de manifest_hash al igual que document_id. |

#### Lecciones aprendidas

- `str.islower()` en Python retorna False para strings sin caracteres alfabéticos. Los invariantes deben verificar el contrato real, no propiedades incidentales.
- Pydantic v2 `model_copy(update=...)` no revalida campos actualizados. Métodos factory que modifican campos con contratos deben usar constructor completo.
- `hypothesis` con `st.characters()` incluye surrogates Unicode por defecto. Usar `blacklist_categories=("Cs",)`.
- Los hallazgos `IMPLEMENTATION_REQUIRED` se resuelven como Batches del Findings Register (METHODOLOGY §6.6), no como Waves nuevas del Execution Plan. Esto preserva la estructura original del plan y mantiene la trazabilidad findings → batches → commits.

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 1 | DF-01 (Batch 1) |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |


### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RESOLVED` | Resuelto en Batch 1 mediante GroundTruthState type alias aplicado en DTO y modelo de dominio + 6 tests de fail-fast. Asimetría defensiva cerrada. |
---


## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

### 4.1 BATCH 1 — Resolución de DF-01 (2026-08-29)

**Fecha de ejecución:** 2026-08-29  
**Validación:** Pyright 0 errors | pytest 442 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-01** | `RESOLVED` | GroundTruthState type alias + aplicación en DTO/modelo + 6 tests fail-fast | core/shared/identity_contracts.py, core/benchmark/corpus/dtos.py, core/benchmark/corpus/models.py, tests/unit/test_corpus_models.py | ✅ 442 passed |

#### Correcciones adicionales durante ejecución

- Ninguna. El cambio fue aditivo y de riesgo cero (verificado con grep previo: 0 fixtures con ground_truth_state, 0 asignaciones con ':').

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | Ninguno | — | — |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| NADR-F17BIS-17 | §5.1 R1-R4 | ground_truth_state ahora tiene contrato de dominio explícito (GroundTruthState) con validación fail-fast en construcción |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| GroundTruthState = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^:]+$")] | Mismo patrón que DocumentId y NodeId. Consistencia de dominio. | Enum acoplado al DTO (violación de Problema B), diferir a Fase 4/5 (deuda técnica deliberada) |
| Resolver en Batch 1 (no diferir) | ENGINEERING_PRINCIPLES §I (Cero Deuda Técnica Deliberada). El cambio es trivial (~30 líneas) y cierra asimetría defensiva. | RECLASSIFIED_FUTURE_PHASE a Fase 4 (destino incorrecto, Fase 4 es Scientific Verification) |

#### Métricas post-batch

| Métrica | Valor |
|---------|-------|
| Archivos creados | 0 |
| Archivos modificados | 4 |
| Archivos eliminados | 0 |
| Tests ejecutados | 442 passed, 5 skipped |
| Errores de tipo estático | 0 |

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 1 |
| Hallazgos resueltos | 1 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos reclasificados a fase futura | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Batches completados | 1 |
| Archivos eliminados totales | 0 |
| Archivos creados totales (Fase 3) | 4 (identity_contracts.py, test_corpus_models.py, test_ast_models.py, test_framing_injectivity.py) |
| Archivos modificados totales (Fase 3) | 15 (identity.py, hashing.py, services.py, dtos.py, use_cases.py ×2, freeze_ground_truth.py, models.py ×2, models_ast.py, pyproject.toml, test_corpus_models.py, manifest.json, test_ground_truth_sealing_atomicity.py, test_manifest_fingerprint.py, test_corpus_port_asymmetry.py) |
| Archivos modificados en Batch 1 | 4 (corpus/dtos.py, corpus/models.py, test_corpus_models.py, identity_contracts.py) |
| Tests finales | 442 passed, 5 skipped |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| — | — | Sin hallazgos diferidos. DF-01 fue resuelto en Batch 1 de la misma fase. |

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
| Total de hallazgos analizados | 1 |
| Hallazgos resueltos | 1 (DF-01 → Batch 1) |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Batches completados | 1/1 |
| Estado del Exit Review | ✅ CERRADO (Gate 1 PASS, Gate 2 PASS con DF-01 RESOLVED en Batch 1) |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad findings → clasificación → resolución → commit. No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la evidencia empírica de los hallazgos identificados durante la implementación del Execution Plan de Fase 3 y su resolución.