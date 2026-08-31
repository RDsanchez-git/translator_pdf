# FASE_4_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_4_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.1.0-DRAFT
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-08-30
**Última actualización:** 2026-08-30
**Derivado de:** `PHASE_17BIS_FASE4_EXECUTION_PLAN.md` v1.0.0
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de la Fase 4 (Scientific Verification), su clasificación,
resolución y evidencia empírica de los batches.

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

## 2. HALLAZGOS PRE-IDENTIFICADOS DURANTE FASE 0 DE FASE 4 (REFERENCIA)

> **Nota metodológica:** Esta sección es una referencia cruzada a hallazgos
> identificados durante los HITOs 4.1-4.5 que tienen destino fuera de la Fase 4.
> Estos hallazgos NO se clasifican aquí; su clasificación formal ocurre durante
> el Gate Exit Review correspondiente. Esta sección existe únicamente para
> trazabilidad y para evitar que se pierdan durante la implementación.

| ID Ref | Hallazgo | Origen | Destino preliminar | Nota |
|--------|----------|--------|-------------------|------|
| PRE-01 | Tests tautológicos (`test_golden_parser.py`: tautología A==A; `test_chunker_snapshot.py`: autogeneración + sub-aserción) | HITO_0.4.4 (GAP-0.4-09, C5-R01, C5-R02, C5-R03), HITO_4.4 | Fase 6 (Continuous Verification) | La remediación de tests y la integración en CI pertenecen a Fase 6 según ADR Maestro §6. La Fase 4 define las reglas; la Fase 6 las ejecuta como compuertas de merge. |
| PRE-02 | Verificación de completitud de `pyproject.toml` y `.github/workflows/ci.yml` para los nuevos tests de regresión de Fase 4 | HITO_4.4 | Fase 6 (Continuous Verification) | Ambos archivos ya existen. La verificación de que cubren los nuevos tests de regresión y la configuración de Required Status Checks pertenecen a Fase 6, gobernadas por NADR-10. |
| PRE-03 | Deuda técnica de `LayoutBlockDraft` (mapper transicional `_layout_block_to_draft()` en `pipeline_factory.py`) | HITO_0.4.4-C3 (C3-FUTURE-07), HITO_4.5 | Gate 3 futuro (remediación de layout) | El mapper funciona correctamente. La eliminación de `LayoutBlockDraft` es una tarea de remediación de layout que no bloquea la Fase 4. |
| PRE-04 | Dualidad `core/benchmark/topology/` (ZhangShashaEngine) vs `tools/evaluation/topology/metrics/structural.py` (StructuralTopologyMetric con APTED) | HITO_0.4.1 (OBS-0.4.1-04), HITO_4.5 | Pendiente de benchmark comparativo | La Fase 4 usa exclusivamente ZhangShashaEngine (NADR-19 §5.2 R8). La decisión de deprecación requiere evidencia empírica (benchmark comparativo sobre el corpus de calibración). Sin evidencia, no se puede tomar una decisión arquitectónica fundamentada. |

> **Nota:** Los IDs `PRE-XX` son identificadores de referencia temporal.
> Durante el Gate Exit Review correspondiente, estos hallazgos se clasifican
> formalmente con IDs `DF-XX` o `GF-XX` según el árbol de decisión (§2.x).

---

## 3. GATE EXIT REVIEWS

{Una sub-sección por cada Gate ejecutado. Se agregan dinámicamente durante la implementación.}

<!-- Gate 1 Exit Review se agregará aquí cuando se ejecute -->
<!-- Gate 2 Exit Review se agregará aquí cuando se ejecute -->
<!-- Gate 3 Exit Review se agregará aquí cuando se ejecute -->

---

## 4. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| — | — | — |

---

## 5. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Una sub-sección por cada batch ejecutado. Se agregan dinámicamente durante la implementación.}

<!-- BATCH 1 se agregará aquí cuando se ejecute -->
<!-- BATCH 2 se agregará aquí cuando se ejecute -->
<!-- BATCH N se agregará aquí cuando se ejecute -->

---

## 6. MÉTRICAS ACUMULADAS DE LA FASE

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
| Tests finales | — |
| Pyright final | — |

---

## 7. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| — | — | — |

---

## 8. CRITERIOS DE CIERRE

### 8.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida: 442 passed, 5 skipped)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 8.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito

---

## 9. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 0 |
| Hallazgos resueltos | 0 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Batches completados | 0/3 |
| Estado del Exit Review | 🟡 IN PROGRESS |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución.