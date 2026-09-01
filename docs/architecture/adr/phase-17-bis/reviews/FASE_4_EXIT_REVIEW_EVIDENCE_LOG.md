# FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 0.4.0
**Estado:** IN_PROGRESS
**Fecha:** 2026-08-30
**Última actualización:** 2026-08-30
**Derivado de:** `PHASE_17BIS_FASE4_EXECUTION_PLAN.md` v1.0.2 — Gate 1 y Gate 2 Exit Review
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review de la Fase 4 (Scientific Verification). Cada finding
incluye los archivos auditados, el análisis, los gaps confirmados, la justificación
normativa y la clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0-DRAFT | 2026-08-30 | Creación del documento. Estructura inicial. |
| 0.2.0 | 2026-08-30 | Gate 1 COMPLETED. Evidencia forense de PRE-01 a PRE-04 reclasificados como DF-01 a DF-04. |
| 0.3.0 | 2026-08-30 | Regeneración completa siguiendo plantilla canónica. Estructura por finding completa para DF-01 a DF-04 con las 10 subsecciones. |
| 0.4.0 | 2026-08-30 | **Gate 2 COMPLETED.** Gate 2 Exit Review Summary agregado. 0 nuevos hallazgos durante implementación. Evidencia forense de Gate 2 registrada. |

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
| `RESOLVED` | Implementado y cerrado |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

```text
1. ¿Sigue siendo válido el hallazgo?
   → NO: CLOSED (NAR)
   → SÍ: continuar

2. ¿Puede resolverse dentro del Gate actual?
   → SÍ: RESOLVED
   → NO: continuar

3. ¿Es un problema técnico?
   → SÍ: RECLASIFICADO a Gate futuro o fase futura
   → NO: continuar

4. ¿Es un conflicto normativo?
   → SÍ: CONVERTIDO EN GF
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. ESTRUCTURA POR FINDING

### 1 DF-01 — Tests tautológicos en integración

| Campo | Valor |
|-------|-------|
| **ID** | DF-01 (anteriormente PRE-01) |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | HITO_0.4.4 (GAP-0.4-09), HITO_4.4 |
| **Gate destino original** | Gate 4 (propuesta original) |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — pero en Fase 6, no en Fase 4 |
| **¿Bloquea la regresión científica graduada?** | No — la Fase 4 define las reglas; la Fase 6 las integra en CI |

#### 1.1 Texto original del DF

> *"Tests tautológicos (`test_golden_parser.py`: tautología A==A; `test_chunker_snapshot.py`: autogeneración + sub-aserción)"*

#### 1.2 Reformulación corregida

No requiere reformulación.

#### 1.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `tests/integration/test_golden_parser.py` | Tautología: `expected_fingerprint = current_fingerprint`. El test siempre pasa porque compara el valor actual consigo mismo. |
| 2 | `tests/integration/test_chunker_snapshot.py` | Autogeneración silenciosa de baseline: `if not os.path.exists(snapshot_path): json.dump(...)`. Sub-aserción: solo compara 4 de 11 campos serializados. |
| 3 | HITO_0.4.4_C5 (GAP-0.4-09) | Confirma P0 (Crítico). Dictamina REESCRIBIR para golden test y REFACTORIZAR para snapshot. |
| 4 | ADR_F17_BIS_MASTER §6 | Fase 6 = Continuous Verification (Integración definitiva en CI Gates). |

#### 1.4 Análisis

- **¿La condición original existe?** ✅ Sí. Los tests tautológicos existen en el repositorio.
- **¿Es una violación normativa?** No es una violación de NADRs de Fase 4. Es un defecto de testing que pertenece a Fase 6.
- **¿Qué NADRs/ADRs aplican?** ADR_F17_BIS_MASTER §6 (Fase 6), NADR-10 (Regression Gates & CI Automation).
- **¿Cuál es el impacto funcional real?** Bajo para Fase 4. Los tests tautológicos no afectan la implementación de la taxonomía de criticidad ni del mecanismo de veredicto. Afectan la confianza en la suite de tests de integración, pero eso es responsabilidad de Fase 6.

#### 1.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Golden test tautológico (A==A) | `test_golden_parser.py`: `expected_fingerprint = current_fingerprint` | Alta |
| G2 | Snapshot con autogeneración silenciosa | `test_chunker_snapshot.py`: `if not os.path.exists(...)` | Alta |
| G3 | Snapshot con sub-aserción (4 de 11 campos) | `test_chunker_snapshot.py`: solo compara campos parciales | Media |

#### 1.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Tests unitarios de Fase 4 | ✅ Correcto por diseño | 66 tests unitarios de Gate 1 cubren la taxonomía y el veredict. |
| `pyproject.toml` y `ci.yml` | ✅ Correcto por diseño | Ambos archivos existen y tienen configuración básica. La verificación de cobertura es Fase 6. |

#### 1.7 Impacto en la regresión científica graduada

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No afecta | La taxonomía y el veredicto son deterministas independientemente de los tests tautológicos. |
| Reproducibilidad | ❌ No afecta | Los componentes de Fase 4 son reproducibles sin depender de los tests de integración. |
| Corrección funcional | ❌ No afecta | La corrección funcional de Fase 4 está verificada por los 66 tests unitarios. |
| Bloquea Fase 5 | ❌ No | La Fase 5 (Baseline Certification) no depende de los tests tautológicos. |

#### 1.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-01-A | Reescribir `test_golden_parser.py` sin tautología | Pendiente | Fase 6 |
| DF-01-B | Remediar `test_chunker_snapshot.py` sin autogeneración | Pendiente | Fase 6 |

#### 1.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a la Fase 4 | ❌ No (pertenece a Fase 6) |
| Bloquea la regresión científica graduada | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Prioridad | Alta |

#### 1.10 Regla aplicada

> **ADR_F17_BIS_MASTER §6 (Sub-fases de la Fase 17-BIS):**
> *"FASE 6 — Continuous Verification (Integración definitiva en CI Gates)"*

La remediación de tests tautológicos y la integración en CI pertenecen a Fase 6 según el ADR Maestro. La Fase 4 define las reglas de regresión; la Fase 6 las ejecuta como compuertas de merge.

---

### 2 DF-02 — Verificación de CI workflows

| Campo | Valor |
|-------|-------|
| **ID** | DF-02 (anteriormente PRE-02) |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | HITO_4.4 |
| **Gate destino original** | Gate 4 (propuesta original) |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — pero en Fase 6, no en Fase 4 |
| **¿Bloquea la regresión científica graduada?** | No |

#### 2.1 Texto original del DF

> *"Verificación de completitud de `pyproject.toml` y `.github/workflows/ci.yml` para los nuevos tests de regresión de Fase 4"*

#### 2.2 Reformulación corregida

No requiere reformulación.

#### 2.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `pyproject.toml` | EXISTE. Contiene `[tool.pytest.ini_options]` con markers (regression, integration, unit, smoke), `[tool.pyright]`, `[tool.importlinter]`, `[tool.coverage.run]`. |
| 2 | `.github/workflows/ci.yml` | EXISTE. Contiene 4 jobs: static-analysis, regression-gates, unit-tests, integration-tests. Incluye `git diff --exit-code tests/fixtures/` para protección de oráculos. |
| 3 | HITO_4.4 | Confirma que ambos archivos existen pero no están verificados para los nuevos tests de regresión de Fase 4. |
| 4 | NADR-10 (Regression Gates & CI Automation) | La integración de regression gates en CI pertenece a Fase 6. |

#### 2.4 Análisis

- **¿La condición original existe?** ⚠️ Parcialmente. Los archivos existen pero no están verificados para los nuevos tests de regresión.
- **¿Es una violación normativa?** No. Es una tarea de verificación que pertenece a Fase 6.
- **¿Qué NADRs/ADRs aplican?** NADR-10 (Regression Gates & CI Automation), ADR_F17_BIS_MASTER §6.
- **¿Cuál es el impacto funcional real?** Bajo para Fase 4. La evaluación de regresión puede ejecutarse localmente sin CI. La integración en CI es responsabilidad de Fase 6.

#### 2.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | No verificado si `ci.yml` cubre los nuevos tests de regresión de Fase 4 | `.github/workflows/ci.yml` no menciona `test_criticality_*.py` | Baja |

#### 2.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Existencia de `pyproject.toml` | ✅ Correcto por diseño | El archivo existe y tiene configuración completa. |
| Existencia de `ci.yml` | ✅ Correcto por diseño | El archivo existe y tiene 4 jobs funcionales. |

#### 2.7 Impacto en la regresión científica graduada

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No afecta | La evaluación de regresión es determinista sin CI. |
| Reproducibilidad | ❌ No afecta | La evaluación puede ejecutarse localmente. |
| Corrección funcional | ❌ No afecta | Los 66 tests unitarios verifican la corrección funcional. |
| Bloquea Fase 5 | ❌ No | La Fase 5 no depende de la integración en CI. |

#### 2.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-02-A | Verificar que `ci.yml` cubre los nuevos tests de regresión | Pendiente | Fase 6 |
| DF-02-B | Configurar Required Status Checks | Pendiente | Fase 6 |

#### 2.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a la Fase 4 | ❌ No (pertenece a Fase 6) |
| Bloquea la regresión científica graduada | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Prioridad | Media |

#### 2.10 Regla aplicada

> **NADR-10 (Regression Gates & CI Automation):**
> La integración de regression gates en CI pertenece a Fase 6. La Fase 4 define las reglas; la Fase 6 las ejecuta como compuertas de merge.

---

### 3 DF-03 — Deuda técnica LayoutBlockDraft

| Campo | Valor |
|-------|-------|
| **ID** | DF-03 (anteriormente PRE-03) |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | HITO_0.4.4_C3 (C3-FUTURE-07), HITO_4.5 |
| **Gate destino original** | N/A (deuda técnica preexistente) |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — pero en Gate futuro, no en Fase 4 |
| **¿Bloquea la regresión científica graduada?** | No |

#### 3.1 Texto original del DF

> *"Deuda técnica de `LayoutBlockDraft` (mapper transicional `_layout_block_to_draft()` en `pipeline_factory.py`)"*

#### 3.2 Reformulación corregida

No requiere reformulación.

#### 3.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/layout/models.py` | Contiene `LayoutBlockDraft` y `LayoutBlockCollection` como DTOs legacy. |
| 2 | `apps/bootstrap/pipeline_factory.py` | Contiene `_layout_block_to_draft()` con nota DF-12: "LayoutBlockDraft pertenece al legacy DocumentLayoutBuilder (zombi). Este mapper es transicional." |
| 3 | HITO_0.4.4_C3 (C3-FUTURE-07) | "En Gate 3, FlatASTBuilder debe consumir LayoutBlock directamente, eliminando LayoutBlockDraft y LayoutBlockCollection." |
| 4 | HITO_4.5 E-4.5-003 | Confirma que el mapper transicional no es bloqueante para la regresión. |

#### 3.4 Análisis

- **¿La condición original existe?** ✅ Sí. `LayoutBlockDraft` existe como DTO legacy.
- **¿Es una violación normativa?** No. Es deuda técnica documentada que no bloquea la Fase 4.
- **¿Qué NADRs/ADRs aplican?** HITO_0.4.4_C3 (C3-FUTURE-07).
- **¿Cuál es el impacto funcional real?** Nulo para Fase 4. El mapper funciona correctamente y produce el AST esperado.

#### 3.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | `LayoutBlockDraft` es legacy zombi | `core/layout/models.py`, nota DF-12 en `pipeline_factory.py` | Baja |

#### 3.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Funcionalidad del mapper | ✅ Correcto por diseño | El mapper `_layout_block_to_draft()` funciona correctamente y produce el AST esperado. |
| Impacto en la regresión | ✅ Correcto por diseño | La regresión evalúa el AST resultante, no el mecanismo interno de construcción. |

#### 3.7 Impacto en la regresión científica graduada

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No afecta | El mapper es determinista. |
| Reproducibilidad | ❌ No afecta | El mapper es reproducible. |
| Corrección funcional | ❌ No afecta | El mapper produce el AST correcto. |
| Bloquea Fase 5 | ❌ No | La Fase 5 no depende de la eliminación de LayoutBlockDraft. |

#### 3.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-03-A | Eliminar `LayoutBlockDraft` y `LayoutBlockCollection` | Pendiente | Gate futuro (remediación de layout) |
| DF-03-B | `FlatASTBuilder` debe consumir `LayoutBlock` directamente | Pendiente | Gate futuro (remediación de layout) |

#### 3.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí (deuda técnica documentada) |
| Pertenece a la Fase 4 | ❌ No (pertenece a Gate futuro) |
| Bloquea la regresión científica graduada | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Prioridad | Baja |

#### 3.10 Regla aplicada

> **HITO_0.4.4_C3 (C3-FUTURE-07):**
> *"En Gate 3, FlatASTBuilder debe consumir LayoutBlock directamente, eliminando LayoutBlockDraft y LayoutBlockCollection."*

La eliminación de `LayoutBlockDraft` es una tarea de remediación de layout identificada en Fase 0. No bloquea la Fase 4 porque el mapper funciona correctamente.

---

### 4 DF-04 — Dualidad ZhangShasha/APTED

| Campo | Valor |
|-------|-------|
| **ID** | DF-04 (anteriormente PRE-04) |
| **Tipo** | Deferred Finding |
| **Estado** | `REVIEW_REQUIRED` |
| **Origen** | HITO_0.4.1 (OBS-0.4.1-04), HITO_4.5 |
| **Gate destino original** | N/A |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Pendiente de benchmark comparativo |
| **¿Bloquea la regresión científica graduada?** | No — la Fase 4 usa exclusivamente ZhangShashaEngine |

#### 4.1 Texto original del DF

> *"Dualidad `core/benchmark/topology/` (ZhangShashaEngine) vs `tools/evaluation/topology/metrics/structural.py` (StructuralTopologyMetric con APTED)"*

#### 4.2 Reformulación corregida

No requiere reformulación.

#### 4.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/benchmark/topology/engines/zhang_shasha/` | Motor TED nativo: Python puro, O(M²N²) amortiguado, particionado escalable, raíz virtual con costo 0.0. |
| 2 | `tools/evaluation/topology/metrics/structural.py` | Motor TED legacy: APTED (gema externa), O(M³N), sin particionado, costos fijos (CostMatrix). |
| 3 | HITO_0.4.1 (OBS-0.4.1-04) | "Dualidad core/ vs tools/ sin resolución. Se recomienda consolidar sobre la rama nativa." |
| 4 | HITO_4.5 | Confirma que la Fase 4 usa exclusivamente `ZhangShashaEngine` (NADR-19 §5.2 R8). |
| 5 | ENGINEERING_PRINCIPLES §I | "Benchmark Before Optimization: Ningún componente estructural se reemplaza sin evidencia estadística empírica." |

#### 4.4 Análisis

- **¿La condición original existe?** ✅ Sí. Ambos motores coexisten en el repositorio.
- **¿Es una violación normativa?** No. No existe un NADR que prohíba la coexistencia de motores TED.
- **¿Qué NADRs/ADRs aplican?** ENGINEERING_PRINCIPLES §I (Benchmark Before Optimization), NADR-19 §5.2 R8.
- **¿Cuál es el impacto funcional real?** Bajo para Fase 4. La Fase 4 usa exclusivamente `ZhangShashaEngine`. La dualidad no afecta la implementación de la regresión.

#### 4.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Dos implementaciones TED coexisten sin evidencia de equivalencia | `core/benchmark/topology/engines/zhang_shasha/` vs `tools/evaluation/topology/metrics/structural.py` | Media |

#### 4.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Funcionalidad de ZhangShashaEngine | ✅ Correcto por diseño | 17 tests unitarios verifican la correctitud del motor. |
| Uso de StructuralTopologyMetric en Fase 4 | ✅ Correcto por diseño | La Fase 4 usa exclusivamente ZhangShashaEngine (NADR-19 §5.2 R8). |

#### 4.7 Impacto en la regresión científica graduada

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No afecta | ZhangShashaEngine es determinista. |
| Reproducibilidad | ❌ No afecta | ZhangShashaEngine es reproducible. |
| Corrección funcional | ❌ No afecta | La Fase 4 usa exclusivamente ZhangShashaEngine. |
| Bloquea Fase 5 | ❌ No | La Fase 5 no depende de la decisión de deprecación. |

#### 4.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-04-A | Ejecutar benchmark comparativo ZhangShasha vs APTED sobre corpus de calibración | Pendiente | Fase 5 |
| DF-04-B | Decidir deprecación de StructuralTopologyMetric con evidencia empírica | Pendiente | Post-benchmark |

#### 4.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí (dualidad sin resolución) |
| Pertenece a la Fase 4 | ❌ No (la Fase 4 usa exclusivamente ZhangShashaEngine) |
| Bloquea la regresión científica graduada | ❌ No |
| Clasificación | `REVIEW_REQUIRED` |
| Prioridad | Media |

#### 4.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (Benchmark Before Optimization):**
> *"Ningún componente estructural se reemplaza sin evidencia estadística empírica."*

La decisión de deprecación de `StructuralTopologyMetric` requiere un benchmark comparativo sobre el corpus de calibración. Sin evidencia empírica, no se puede tomar una decisión arquitectónica fundamentada.

---

## 3. GATE EXIT REVIEW SUMMARY

### 3.1 Gate 1 Exit Review (2026-08-30)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble en Gate 1? | ¿Técnico? | Decisión | Motivo |
|----|----------|----------------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Fase 6 | ADR Maestro §6 |
| DF-02 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Fase 6 | NADR-10 |
| DF-03 | ✅ Sí | ❌ No | ✅ Sí | RECLASSIFIED_FUTURE_PHASE → Gate futuro | Deuda técnica layout |
| DF-04 | ✅ Sí | ❌ No | ✅ Sí | REVIEW_REQUIRED | Pendiente benchmark |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Fase 6: 2 (DF-01, DF-02)
- RECLASIFICADO → Gate futuro: 1 (DF-03)
- CLOSED (NAR): 0
- REVIEW_REQUIRED: 1 (DF-04)
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados durante Gate 1: 0

**Verificación empírica:**
- Pyright: 0 errors, 0 warnings, 0 informations
- Pytest: 508 passed, 5 skipped, 0 failures, 1 warning (no relacionado — FutureWarning de google.generativeai)
- Zero-touch: 0 archivos existentes modificados
- Componentes stateless: `CriticalityVerdictEmitter`, `ClassificationTracer` (ENGINEERING_PRINCIPLES §II)
- Determinismo: verificado en tests `test_deterministic_same_input_same_output` y `test_trace_is_deterministic`

---

### 3.2 Gate 2 Exit Review (2026-08-30)

**Árbol de decisión aplicado:**

No se identificaron nuevos hallazgos (DF/GF) durante la implementación de Gate 2. No hay entradas nuevas en la Estructura por Finding (§2) para este Gate.

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO: 0
- CLOSED (NAR): 0
- REVIEW_REQUIRED: 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados durante Gate 2: **0**

**Verificación empírica:**
- Pyright: 0 errors, 0 warnings, 0 informations
- Pytest: 586 passed, 5 skipped, 0 failures, 1 warning (no relacionado — `FutureWarning` de `google.generativeai` en `apps/llm_workers/adapters.py`)
- Zero-touch: 0 archivos existentes modificados
- Componentes stateless: `RegressionAdapter`, `RegressionEvaluationStrategy`, `DoubleProtectionMechanism` (ENGINEERING_PRINCIPLES §II)
- Determinismo: verificado en tests `test_deterministic` (mechanism y strategy)
- Corregibilidad P0-1: verificada en `test_recall_evaluators_called_exactly_once` (`call_count == 1`)
- Cumplimiento de protocolo: `evaluate_run()` retorna `TopologicalEvaluationReport` (verificado en `test_evaluate_run_returns_topological_report`)

**Justificación de ausencia de hallazgos:**

La implementación de Gate 2 fue limpia por las siguientes razones:
1. **Reutilización estricta (Reuse Before Invent):** Se consumió `OracleSemanticIdentityCalculator`, `BaselineCompletenessVerifier`, `IncompleteBaselineError`, `TreeEditDistanceEvaluator`, `EntityRecallEvaluator` y `CriticalityAwareCostContext` (Gate 1) sin modificación.
2. **Análisis iterativo:** Los defectos detectados (P0-1 doble llamada, P1 `overall_score` default) eran errores de la propuesta inicial que se corrigieron **inline** dentro de la misma wave, antes de declarar el Gate COMPLETED. No constituyen hallazgos diferibles porque no representan deuda técnica ni decisiones arquitectónicas pendientes.
3. **Zero-touch:** Ningún archivo existente fue modificado, eliminando el riesgo de regresiones sobre infraestructura de fases anteriores.
4. **Sin conflictos normativos:** No se identificaron contradicciones entre NADRs ni con el ADR Maestro.

**Nota de trazabilidad:** Los defectos P0-1 y P1 corregidos inline están documentados en las Notas de implementación del Execution Plan (§3.1-§3.4) y en el Changelog (v1.0.2), no como hallazgos en este Evidence Log, porque fueron resueltos dentro del mismo Gate sin requerir batches posteriores ni decisiones de clasificación.

---

## 4. TABLA CONSOLIDADA FINAL

Se completa al cierre del último Gate Exit Review. Los 4 DFs actuales están clasificados.
Si Gate 3 genera nuevos hallazgos, se agregarán a esta tabla.

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 3 | DF-01, DF-02, DF-03 |
| `REVIEW_REQUIRED` | 1 | DF-04 |
| `ACCEPTED_LIMITATION` | 0 | — |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RECLASSIFIED_FUTURE_PHASE` | Tests tautológicos → Fase 6 (ADR Maestro §6, NADR-10) |
| DF-02 | `RECLASSIFIED_FUTURE_PHASE` | CI workflows verification → Fase 6 (NADR-10) |
| DF-03 | `RECLASSIFIED_FUTURE_PHASE` | Deuda LayoutBlockDraft → Gate futuro (no bloquea) |
| DF-04 | `REVIEW_REQUIRED` | Dualidad ZhangShasha/APTED — pendiente benchmark Fase 5 |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado `PENDING_REVIEW`
- [x] La tabla consolidada final está completa
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [x] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [x] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación

> **Nota:** Los checkboxes reflejan el estado actual (Gate 1 + Gate 2 completados).
> Gate 2 no generó hallazgos nuevos, por lo que no hay entradas pendientes.
> El documento permanece `IN_PROGRESS` hasta el cierre de Gate 3, momento en el cual
> se ejecutará la verificación final y el documento pasará a `FROZEN`.

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones.