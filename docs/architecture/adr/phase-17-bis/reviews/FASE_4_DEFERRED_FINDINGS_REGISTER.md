# FASE_4_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_4_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.3.0
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-08-30
**Última actualización:** 2026-08-30
**Derivado de:** `PHASE_17BIS_FASE4_EXECUTION_PLAN.md` v1.0.1
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de la Fase 4 (Scientific Verification), su clasificación,
resolución y evidencia empírica de los batches.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0-DRAFT | 2026-08-30 | Creación del documento. Estructura inicial. |
| 0.2.0 | 2026-08-30 | Gate 1 COMPLETED. PRE-01 a PRE-04 formalizados como DF-01 a DF-04. |
| 0.3.0 | 2026-08-30 | Regeneración completa siguiendo plantilla canónica. Gate 1 Exit Review completo con árbol de decisión, tabla por DF, decisiones arquitectónicas y lecciones aprendidas. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17-BIS_04 > NADR-F17BIS-18 / NADR-F17BIS-19 > PHASE_17BIS_FASE4_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la regresión científica del
> runtime contra el oráculo sellado sea una evaluación determinista, graduada
> y reproducible, verificando la integridad criptográfica y el estado de
> ciclo de vida del oráculo antes de evaluar?"*

### 0.3 Reglas transversales aplicables

> - **Zero Partial Sealing** (ADR Maestro §5): Un corpus NO podrá entrar en
>   estado `SEALED` si no existe una correspondencia biyectiva completa entre
>   los PDFs declarados y sus oráculos AST auditados.
> - **Determinismo y Reproducibilidad** (ADR Maestro §5): Todo el pipeline de
>   evaluación, serialización y cálculo de firmas debe ser 100% determinista.
> - **Desacoplamiento de Identidades** (ADR Maestro §5): La arquitectura debe
>   mantener diferenciados los conceptos de AST Schema Version, Corpus Version
>   e Identity Hash.
> - **Separación de Identidades** (NADR-F17BIS-16 §5.3): `ground_truth_state`
>   es estado operacional del ciclo de vida, no identidad científica del
>   contenido. `oracle_hash` es identidad científica del contenido del oráculo.
> - **Principio de Reutilización del Composition Root** (ADR_F17-BIS_04):
>   El entry point de regresión reutiliza el composition root
>   `build_extraction_pipeline()` para generar el runtime AST.
> - **Principio de Verificación Previo** (ADR_F17-BIS_04): Antes de evaluar
>   el runtime contra el oráculo sellado, se debe verificar la integridad
>   criptográfica del oráculo mediante `oracle_hash` y la completitud
>   biyectiva mediante `BaselineCompletenessVerifier`.
> - **Principio de Veredicto Graduado** (ADR_F17-BIS_04): El veredicto de
>   regresión emite tres juicios diferenciados (`PASS`/`WARNING`/`HARD_FAIL`)
>   basados en la magnitud de la desviación topológica.
> - **Doble Mecanismo de Protección** (ADR_F17-BIS_04): El veredicto se basa
>   en el NSS ponderado por criticidad (protección gradual) Y la regla de
>   pérdida de nodo CRITICAL (protección absoluta). Ambos son complementarios.

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

### 2.1 Gate 1 Exit Review (2026-08-30)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble en Gate 1? | ¿Técnico? | Decisión | Motivo |
|----|----------|----------------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Fase 6 | Tests tautológicos no bloquean Fase 4; su remediación pertenece a Fase 6 (ADR Maestro §6) |
| DF-02 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Fase 6 | pyproject.toml y ci.yml ya existen; la verificación de cobertura pertenece a Fase 6 (NADR-10) |
| DF-03 | ✅ Sí | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Gate futuro | Deuda técnica de layout no bloquea Fase 4; pertenece a remediación de layout |
| DF-04 | ✅ Sí | ❌ No | ✅ Sí | REVIEW_REQUIRED | Dualidad ZhangShasha/APTED requiere benchmark comparativo antes de decidir |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Fase 6: 2 (DF-01, DF-02)
- RECLASIFICADO → Gate futuro: 1 (DF-03)
- CLOSED (NAR): 0
- REVIEW_REQUIRED: 1 (DF-04)
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados durante Gate 1: 0
- Revisiones tardías documentadas: 0

#### Decisiones arquitectónicas congeladas en Gate 1

| Decisión | Task | Justificación |
|----------|------|---------------|
| `CriticalityPolicy` como Protocol sin `@runtime_checkable` | 1.1.2 | ENGINEERING_PRINCIPLES §II (YAGNI): overhead innecesario sin consumidor actual de `isinstance()` |
| `DefaultCriticalityPolicy` con mapeo declarativo en dict de módulo | 1.1.3 | ENGINEERING_PRINCIPLES §III (Explicit over Implicit): sin magia, factoría explícita |
| `CriticalityAwareCostContext` importa `TreeEditCostContext` del puerto canónico | 1.2.1 | DRY: no redefinir protocolos existentes; NADR-18 §5.3 R11 |
| `substitution_cost` con `max(peso_cand, peso_gt)` | 1.2.2 | Semántica conservadora de pérdida: la sustitución de un nodo CRITICAL siempre tiene la mayor penalización |
| `CriticalityVerdictEmitter` con input `RecallByNodeType` | 1.3.1 | Integración con `EntityRecallEvaluator` existente; no duplicar lógica de matching |
| `ClassificationTracer` stateless | 1.3.4 | ENGINEERING_PRINCIPLES §II (Stateless Components): función pura, sin acumulación interna |
| `trace_types()` eliminado por YAGNI | 1.3.4 | ENGINEERING_PRINCIPLES §I (YAGNI): sin consumidor actual |

#### Lecciones aprendidas

- La integración con `EntityRecallEvaluator` vía `RecallByNodeType` es más limpia que recibir `Sequence[ASTNode]` directamente, porque no duplica la lógica de matching que ya vive en el evaluador.
- Los componentes stateless (`ClassificationTracer`, `CriticalityVerdictEmitter`) son más fáciles de testear y componer que los stateful.
- El umbral de WARNING con semántica `>=` (threshold o más FNs = WARNING) es más intuitivo que `>` (estrictamente mayor).

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
| `RECLASSIFIED_FUTURE_PHASE` | 3 | DF-01, DF-02, DF-03 |
| `REVIEW_REQUIRED` | 1 | DF-04 |
| `ACCEPTED_LIMITATION` | 0 | — |

### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RECLASSIFIED_FUTURE_PHASE` | Tests tautológicos → Fase 6 (ADR Maestro §6, NADR-10) |
| DF-02 | `RECLASSIFIED_FUTURE_PHASE` | CI workflows verification → Fase 6 (NADR-10) |
| DF-03 | `RECLASSIFIED_FUTURE_PHASE` | Deuda LayoutBlockDraft → Gate futuro (no bloquea) |
| DF-04 | `REVIEW_REQUIRED` | Dualidad ZhangShasha/APTED — pendiente benchmark Fase 5 |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{No se ejecutaron batches durante Gate 1 porque no se identificaron hallazgos
que requirieran implementación. Los 4 findings pre-identificados fueron
reclasificados a fases futuras sin necesidad de código nuevo.}

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 4 (DF-01, DF-02, DF-03, DF-04) |
| Hallazgos resueltos | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos reclasificados a fase futura | 3 (DF-01, DF-02, DF-03) |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 1 (DF-04) |
| Batches completados | 0 |
| Archivos eliminados totales | 0 |
| Archivos movidos totales | 0 |
| Archivos creados totales | 10 (7 código + 3 tests) |
| Tests finales | 66 (13 policy + 13 costs + 40 verdict) |
| Pyright final | 0 errors, 0 warnings, 0 informations |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| DF-01 | Fase 6 (Continuous Verification) | La remediación de tests tautológicos (`test_golden_parser.py`, `test_chunker_snapshot.py`) y la integración en CI pertenecen a Fase 6 según ADR Maestro §6. La Fase 4 define las reglas de regresión; la Fase 6 las ejecuta como compuertas de merge. |
| DF-02 | Fase 6 (Continuous Verification) | `pyproject.toml` y `.github/workflows/ci.yml` ya existen. La verificación de que cubren los nuevos tests de regresión y la configuración de Required Status Checks pertenecen a Fase 6, gobernadas por NADR-10. |
| DF-03 | Gate futuro (remediación de layout) | El mapper `_layout_block_to_draft()` funciona correctamente. La eliminación de `LayoutBlockDraft` y `LayoutBlockCollection` es una tarea de remediación de layout que no bloquea la Fase 4. Identificado en HITO_0.4.4_C3 (C3-FUTURE-07). |
| DF-04 | Pendiente de benchmark Fase 5 | La Fase 4 usa exclusivamente `ZhangShashaEngine` (NADR-19 §5.2 R8). La decisión de deprecación de `StructuralTopologyMetric` (APTED) requiere evidencia empírica (benchmark comparativo sobre el corpus de calibración). Sin evidencia, no se puede tomar una decisión arquitectónica fundamentada. Identificado en HITO_0.4.1 (OBS-0.4.1-04). |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida: 508 passed, 5 skipped)
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
| Total de hallazgos analizados | 4 |
| Hallazgos resueltos | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 1 (DF-04) |
| Hallazgos cerrados sin acción | 0 |
| Batches completados | 0 |
| Estado del Exit Review | 🟡 IN PROGRESS |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución.