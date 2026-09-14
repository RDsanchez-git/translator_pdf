# FASE_4_HANDOFF.md — Scientific Verification → Baseline Certification

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_4_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-02
**Fase completada:** Fase 4 — Scientific Verification (Topological regression, semantic recall y criticality)
**Siguiente fase:** Fase 5 — Baseline Certification (Materialización en disco y Zero Partial Sealing)
**Derivado de:** `PHASE_17BIS_FASE4_EXECUTION_PLAN.md` v1.0.3 + `FASE_4_DEFERRED_FINDINGS_REGISTER.md` v0.6.0

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-02 | Emisión inicial al cierre de Fase 4 (Scientific Verification) |

---

## 1. EXECUTIVE SUMMARY

**1. ¿Qué se logró?**
La Fase 4 (Scientific Verification) se completó al 100%. Se materializaron las 51 reglas normativas de NADR-F17BIS-18 (Taxonomía de Criticidad, 22 reglas) y NADR-F17BIS-19 (Regresión Topológica Graduada, 29 reglas) a través de 37 tareas atómicas organizadas en 3 Gates y 8 Waves. El sistema ahora posee: (a) una taxonomía de criticidad de nodos con ponderación de costos de edición, (b) un doble mecanismo de protección que combina NSS ponderado con regla absoluta de pérdida CRITICAL, (c) un adaptador Fail-Fast que verifica integridad criptográfica, estado de sellado y completitud biyectiva antes de evaluar, y (d) un entry point CLI ejecutable (`run_regression.py`) que orquesta la evaluación de regresión de punta a punta con exit codes diferenciados (0/1/2) y reportes JSON + Markdown deterministas.

**2. ¿Cuál es el estado actual?**
624 tests passed, 5 skipped, 0 failures. Pyright: 0 errors, 0 warnings. Zero-touch sobre infraestructura de fases anteriores. 4 hallazgos analizados (PRE-01 a PRE-04), todos reclasificados a fases futuras con destino explícito. 0 hallazgos resueltos, 0 cerrados como NAR, 0 batches ejecutados. 26 archivos creados, 2 modificados (type hint OCP en strategy.py + exports en __init__.py). 6 fixes de pyright aplicados inline durante Gate 3 (tipado estático, no funcionales).

**3. ¿Qué necesita la siguiente fase?**
La Fase 5 (Baseline Certification) necesita: (a) materializar el corpus canónico de 20-30 documentos en disco con sus oráculos AST sellados, (b) ejecutar Zero Partial Sealing verificando la biyección PDF↔oráculo, (c) calibrar empíricamente los umbrales de NSS y pesos de criticidad que actualmente son propuestas iniciales no validadas, y (d) resolver DF-04 (benchmark comparativo ZhangShasha vs APTED) que requiere el corpus materializado como prerequisito.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` |
| Commit hash de cierre | `219bc5c` |
| Estado del árbol | Limpio |
| Baseline de tests | **624 passed, 5 skipped** (no debe degradarse sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados |
| Tests de Fase 4 | **182 tests nuevos** (66 Gate 1 + 78 Gate 2 + 38 Gate 3) |

### 2.2 Validation Results

```bash
# Comandos ejecutados al cierre de la fase
python -m pytest tests/ -q --tb=short                                    # 624 passed, 5 skipped ✅
pyright core/benchmark/topology/criticality/                             # 0 errors, 0 warnings ✅
pyright core/benchmark/topology/regression/                              # 0 errors, 0 warnings ✅
pyright tools/evaluation/run_regression.py                               # 0 errors, 0 warnings ✅
pyright tests/integration/test_regression_entry_point.py                 # 0 errors, 0 warnings ✅
python -m pytest tests/unit/test_zhang_shasha.py -v                      # 17 passed ✅ (zero-touch)
python -m pytest tests/unit/test_structural_metric.py -v                 # 8 passed ✅ (zero-touch)
python -m pytest tests/integration/test_regression_entry_point.py -v     # 9 passed ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro (ADR_F17_BIS_MASTER) | FROZEN | 2026-08-02 |
| ADR de Fase (ADR_F17-BIS_04) | FROZEN | 2026-08-30 |
| NADR-F17BIS-18 (Taxonomía de Criticidad) | FROZEN | 2026-08-30 |
| NADR-F17BIS-19 (Regresión Topológica Graduada) | FROZEN | 2026-08-30 |
| Execution Plan | FROZEN | v1.0.3 |
| Evidence Log | FROZEN | v0.6.0 |
| Findings Register | ARCHIVED | v0.6.0 |
| Methodology (METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES) | FROZEN | v1.3.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 4 (PRE-01→DF-01, PRE-02→DF-02, PRE-03→DF-03, PRE-04→DF-04) |
| Hallazgos resueltos | 0 |
| Hallazgos cerrados sin acción (NAR) | 0 |
| Hallazgos diferidos a fase futura | 4 (DF-01, DF-02 → Fase 6; DF-03 → Gate futuro; DF-04 → Fase 5) |
| Batches ejecutados | 0 |
| Archivos eliminados | 0 |
| Archivos movidos | 0 |
| Archivos creados | 26 (Gate 1: 10, Gate 2: 12, Gate 3: 4) |
| Archivos modificados | 2 (strategy.py type hint OCP, regression/__init__.py exports) |
| Fixes de pyright inline | 6 (Gate 3, tipado estático) |
| Reglas materializadas | 51/51 (100%) |
| Tasks completadas | 37/37 (100%) |
| Gates completados | 3/3 (100%) |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | Taxonomía de 3 niveles (CRITICAL/WARNING/INFO) sin properties YAGNI | DC-06 del ADR Maestro requería mapeo de criticidad | ENGINEERING_PRINCIPLES §I (YAGNI); NADR-18 §5.1 R2 | `criticality/models.py` |
| AD-02 | `CriticalityPolicy` como Protocol sin `@runtime_checkable` | Overhead innecesario sin consumidor actual de `isinstance()` | ENGINEERING_PRINCIPLES §I (YAGNI) | `criticality/ports.py` |
| AD-03 | Mapeo canónico declarativo en dict de módulo | Clasificación por tipo, no por contenido | ENGINEERING_PRINCIPLES §III (Explicit over Implicit); NADR-18 §5.1 R6, R7 | `criticality/policy.py` |
| AD-04 | `CriticalityAwareCostContext` importa `TreeEditCostContext` del puerto canónico | DRY: no redefinir protocolos existentes | NADR-18 §5.3 R11 | `criticality/costs.py` |
| AD-05 | `substitution_cost` con `max(peso_cand, peso_gt)` | Semántica conservadora: la sustitución de un nodo CRITICAL siempre tiene la mayor penalización, independientemente del tipo del nodo sustituto | NADR-18 §5.3 R14 (conservadurismo) | `criticality/costs.py` |
| AD-06 | `CriticalityVerdictEmitter` con input `RecallByNodeType` | Integración con `EntityRecallEvaluator` sin duplicar lógica de matching | NADR-18 §5.4 R16 | `criticality/verdict.py` |
| AD-07 | `ClassificationTracer` stateless + `trace_types()` eliminado por YAGNI | Functional Core sin acumulación de estado | ENGINEERING_PRINCIPLES §II | `criticality/traceability.py` |
| AD-08 | `RegressionCriticalitySignal` como enum tipado (no string libre) | Evita strings libres frágiles | ENGINEERING_PRINCIPLES §III | `regression/models.py` |
| AD-09 | `overall_score` obligatorio en `RegressionEvaluationReport`, `nss_score` como alias | Única fuente de verdad, sin divergencia posible | ENGINEERING_PRINCIPLES §III (Explicit over Implicit) | `regression/models.py` |
| AD-10 | `DoubleProtectionMechanism` con precedencia total de CRITICAL | 1 CRITICAL perdido → HARD_FAIL independientemente del NSS | NADR-19 §5.2 R9, R10 | `regression/mechanism.py` |
| AD-11 | `RegressionAdapter` con orden Fail-Fast: identidad → completitud → estado → integridad | Chequeos más baratos y más probables de fallar van primero | NADR-19 §5.4 R18 | `regression/adapter.py` |
| AD-12 | `_evaluate_recall_once()` evalúa UNA vez por evaluador | Elimina doble llamada (corrección P0-1) | ENGINEERING_PRINCIPLES §II | `regression/strategy.py` |
| AD-13 | `Dict[ContentNodeType, EntityRecallEvaluator]` en vez de `Sequence` | Type-safe sin parsing frágil de `metric_name` | ENGINEERING_PRINCIPLES §III | `regression/strategy.py` |
| AD-14 | `evaluate_run()` + `evaluate_regression()` en strategy | Cumple protocolo `EvaluationStrategy` existente Y expone veredicto completo | NADR-19 §5.1 R1-R3 | `regression/strategy.py` |
| AD-15 | Type hint `TopologicalEvaluatorProtocol` en strategy (OCP) | Dependencia de protocolo, no de implementación concreta | ENGINEERING_PRINCIPLES §III (OCP) | `regression/strategy.py` |
| AD-16 | `run_regression.py` reutiliza `build_extraction_pipeline()` | NADR-19 §5.5 R20-R21: no crear pipeline separado | NADR-19 §5.5 R20 | `tools/evaluation/run_regression.py` |
| AD-17 | Verificaciones individuales por documento (no `verify_all()` en loop) | Evita redundancia de `verify_completeness()` por documento | ENGINEERING_PRINCIPLES §I (YAGNI) | `tools/evaluation/run_regression.py` |
| AD-18 | `RegressionReport` con `build_regression_report()` como función pura | Functional Core, sin I/O | ENGINEERING_PRINCIPLES §II | `regression/report.py` |
| AD-19 | Formatters como Protocol + clases (JSON/Markdown) | OCP: nuevos formatos sin modificar existentes | ENGINEERING_PRINCIPLES §III (OCP) | `regression/report.py` |
| AD-20 | `generated_at: str \| None = None` inyectado externamente | Determinismo total por defecto; timestamp solo si se inyecta | NADR-19 §5.7 R29 | `regression/report.py` |
| AD-21 | Exit codes 0/1/2 (PASS/WARNING/HARD_FAIL) | CI/CD consumible sin parsing de output | NADR-19 §5.5 R22 | `tools/evaluation/run_regression.py` |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Taxonomía de criticidad de nodos (3 niveles) | NADR-18 §5.1 | ✅ DONE |
| Extensibilidad de taxonomía con fail-fast | NADR-18 §5.2 | ✅ DONE |
| Ponderación de costos de edición por criticidad | NADR-18 §5.3 | ✅ DONE |
| Veredicto por criticidad (CRITICAL/WARNING/INFO) | NADR-18 §5.4 | ✅ DONE |
| Trazabilidad de clasificación + eventos de gobernanza | NADR-18 §5.5 | ✅ DONE |
| Veredicto graduado PASS/WARNING/HARD_FAIL | NADR-19 §5.1 | ✅ DONE |
| Doble mecanismo de protección (NSS + CRITICAL absoluto) | NADR-19 §5.2 | ✅ DONE |
| Umbrales de NSS configurables | NADR-19 §5.3 | ✅ DONE |
| Verificación previa Fail-Fast (integridad, estado, completitud) | NADR-19 §5.4 | ✅ DONE |
| Entry point de regresión con exit codes | NADR-19 §5.5 | ✅ DONE |
| Recall ponderado por criticidad | NADR-19 §5.6 | ✅ DONE |
| Reporte de regresión JSON + Markdown determinista | NADR-19 §5.7 | ✅ DONE |

### 4.2 Archivos clave creados/modificados

**Creados (Gate 1 — Taxonomía de Criticidad):**
- `core/benchmark/topology/criticality/__init__.py` — Exports del subpaquete
- `core/benchmark/topology/criticality/models.py` — `NodeCriticality` enum
- `core/benchmark/topology/criticality/ports.py` — `CriticalityPolicy` Protocol
- `core/benchmark/topology/criticality/policy.py` — `DefaultCriticalityPolicy`
- `core/benchmark/topology/criticality/costs.py` — `CriticalityAwareCostContext`
- `core/benchmark/topology/criticality/verdict.py` — `CriticalityVerdictEmitter`
- `core/benchmark/topology/criticality/traceability.py` — `ClassificationTracer` + `ReclassificationEvent`
- `tests/unit/test_criticality_policy.py` — 13 tests
- `tests/unit/test_criticality_costs.py` — 13 tests
- `tests/unit/test_criticality_verdict.py` — 40 tests

**Creados (Gate 2 — Regresión Topológica Graduada):**
- `core/benchmark/topology/regression/__init__.py` — Exports del subpaquete
- `core/benchmark/topology/regression/models.py` — `RegressionVerdict`, `RegressionThresholds`, `RegressionEvaluationReport`
- `core/benchmark/topology/regression/aggregation.py` — `aggregate_corpus_verdicts()`
- `core/benchmark/topology/regression/mechanism.py` — `DoubleProtectionMechanism`
- `core/benchmark/topology/regression/errors.py` — 5 errores tipados
- `core/benchmark/topology/regression/adapter.py` — `RegressionAdapter`
- `core/benchmark/topology/regression/strategy.py` — `RegressionEvaluationStrategy`
- `tests/unit/test_regression_models.py` — Tests de modelos
- `tests/unit/test_regression_aggregation.py` — Tests de agregación
- `tests/unit/test_regression_mechanism.py` — 17 tests
- `tests/unit/test_regression_adapter.py` — 15 tests
- `tests/unit/test_regression_strategy.py` — 16 tests

**Creados (Gate 3 — Entry Point y Reporte):**
- `core/benchmark/topology/regression/report.py` — `RegressionReport` + formatters
- `tools/evaluation/run_regression.py` — Entry point CLI
- `tests/unit/test_regression_report.py` — 29 tests
- `tests/integration/test_regression_entry_point.py` — 9 tests

**Modificados significativamente:**
- `core/benchmark/topology/regression/strategy.py` — Type hint `TopologicalEvaluatorProtocol` (OCP, Fix 2 de pyright)
- `core/benchmark/topology/regression/__init__.py` — Exports de `RegressionReport` y formatters

**Eliminados (zombies y deuda):**
- Ninguno. Zero-touch sobre infraestructura existente.

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para Fase 5 |
|-------------|--------|-------------------------------|
| Zero Partial Sealing: biyección completa PDF↔oráculo para estado SEALED | ADR Maestro §5 | Fase 5 materializa el corpus y ejecuta el sellado. No puede haber sellado parcial. |
| Determinismo: todo pipeline de evaluación y serialización 100% determinista | ADR Maestro §5 | Los reportes de regresión y hashes de oráculo deben ser reproducibles. |
| Los umbrales de NSS (0.80/0.95) son propuesta inicial NO calibrada | NADR-19 §5.3 R12-R14 | Fase 5 debe validar empíricamente estos umbrales sobre el corpus canónico. |
| Los pesos de criticidad (5.0/2.0/1.0) son propuesta inicial NO calibrada | NADR-18 §5.3 R12, R14 | Fase 5 debe validar empíricamente estos pesos sobre el corpus canónico. |
| Reutilización estricta de `build_extraction_pipeline()` | NADR-19 §5.5 R20-R21 | Fase 5 no debe crear pipelines de extracción alternativos. |
| Verificación previa Fail-Fast antes de evaluar | NADR-19 §5.4 R15-R19 | Fase 5 debe verificar integridad, estado y completitud antes de cualquier evaluación. |
| `CriticalityAwareCostContext` importa del puerto canónico (no redefinir) | NADR-18 §5.3 R11 | Fase 5 no debe redefinir protocolos existentes. |
| Tests con `spec=` en mocks | Consistencia Gate 2/3 | Fase 5 debe mantener el estándar de `MagicMock(spec=...)`. |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| DF-01 | Tests tautológicos (`test_golden_parser.py`, `test_chunker_snapshot.py`) | Fase 6 (Continuous Verification) | Nada en Fase 5 |
| DF-02 | Verificación de `pyproject.toml` y `ci.yml` para tests de regresión | Fase 6 (Continuous Verification) | Nada en Fase 5 |
| DF-03 | Deuda técnica `LayoutBlockDraft` (mapper transicional) | Gate futuro (remediación de layout) | Nada en Fase 5 |
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo | **Fase 5 (Baseline Certification)** | **Requiere corpus canónico materializado** |

> **⚠️ DF-04 es el único finding que afecta directamente a Fase 5.** El benchmark comparativo entre `ZhangShashaEngine` y `StructuralTopologyMetric` (APTED) solo puede ejecutarse una vez que el corpus canónico esté materializado en disco. Criterio de decisión: divergencia < 1% en TED normalizado → deprecar APTED; divergencia ≥ 1% → investigar causa raíz. Deadline: cierre de Fase 5.

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| Umbrales no calibrados | Los umbrales de NSS (0.80/0.95) y pesos de criticidad (5.0/2.0/1.0) son propuestas iniciales. Podrían producir falsos positivos/negativos en el corpus real. | Documentados como "propuesta inicial sujeta a validación empírica" en NADR-19 §5.3 R12 y NADR-18 §5.3 R14. Fase 5 debe calibrar. |
| Entry point no probado contra corpus real | `run_regression.py` fue testeado con mocks y fixtures, no contra un corpus sellado real. | Los tests de integración usan fixtures en `tmp_path`. Fase 5 proporcionará el corpus real para validación end-to-end. |
| Dualidad TED sin resolver | `ZhangShashaEngine` (core/) y `StructuralTopologyMetric` (tools/) coexisten. Riesgo de resultados divergentes si se usan para el mismo documento. | Fase 4 eligió ZhangShasha formalmente (NADR-19 §5.2 R8). DF-04 programado para Fase 5. |
| `ImagePayload.text_content` retorna string vacío | `ImagePayload` no tiene campo `content`, solo `alt_text` y `asset_path`. `text_content` retorna `""`. | Comportamiento documentado en `test_ast_models.py::test_image_payload_has_empty_text_content`. Los evaluadores de recall manejan esto correctamente. |
| GAP-4.5-02: Verificación de PDF antes de extraer | El provider no tiene Fail-Fast explícito si el PDF no existe o está corrupto antes de `fitz.open()`. Prioridad P1, no bloqueante. | Fail-Fast implementado a través del `RegressionAdapter` (integridad, estado sellado, completitud). Si el PDF no existe, el pipeline fallará aunque sin mensaje específico de PDF. |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Taxonomía de criticidad completa (NADR-18, 22 reglas)
- ✅ Doble mecanismo de protección operativo (NADR-19 §5.2)
- ✅ Entry point `run_regression.py` funcional con exit codes 0/1/2
- ✅ Reportes JSON + Markdown deterministas
- ✅ `RegressionAdapter` con verificaciones Fail-Fast
- ✅ Infraestructura de sellado (`SealGroundTruthUseCase`, `LifecycleTransitionAuthority`)
- ✅ Infraestructura de completitud (`BaselineCompletenessVerifier`)
- ✅ Identidad semántica del oráculo (`OracleSemanticIdentityCalculator`)
- ✅ Serialización atómica (`write_ast_json_atomic`, `read_ast_json`)
- ✅ `LocalFileSystemGroundTruthReader/Writer/ArtifactAdapter`
- ✅ `LocalFileSystemCorpusLoader`
- ✅ `LoadCorpusManifestUseCase`, `BootstrapCorpusManifestUseCase`

**Lo que se necesita antes de arrancar Fase 5:**
- Selección de los 20-30 documentos del corpus canónico (papers IEEE, doble columna, libros densos, alta varianza)
- Definición de la estrategia de curaduría de Ground Truth (quién audita, cómo se valida)
- Plan de ejecución del benchmark comparativo ZhangShasha vs APTED (DF-04)
- Plan de calibración empírica de umbrales NSS y pesos de criticidad

### 6.2 Next Phase Handoff Checklist

- [ ] Ejecutar `python -m pytest tests/ -q` y confirmar baseline 624 passed, 5 skipped
- [ ] Ejecutar `pyright core/ tools/ tests/` y confirmar 0 errors
- [ ] Cargar este documento (FASE_4_HANDOFF.md) + documentos de Prioridad 1 (§8.4)
- [ ] Redactar ADR_F17-BIS_05 (Baseline Certification — visión arquitectónica)
- [ ] Identificar NADRs necesarios para Fase 5
- [ ] Seleccionar corpus canónico (20-30 documentos)
- [ ] Planificar curaduría y sellado de Ground Truth
- [ ] Planificar benchmark ZhangShasha vs APTED (DF-04)
- [ ] Planificar calibración empírica de umbrales y pesos

### 6.3 ROADMAP — Objetivos de la siguiente fase

Según ROADMAP_ARQUITECTONICO_LP.md §IV (FASE 17_BIS) y ADR_F17_BIS_MASTER §6:

1. **Golden Corpus** — Materialización de 20-30 documentos de alta varianza (papers IEEE, doble columna, libros densos) catalogados y sellados en disco bajo la firma global $H_{baseline}$.
2. **Ground Truth** — Congelamiento criptográfico del AST perfecto en disco. Verificación de biyección completa PDF↔oráculo (Zero Partial Sealing).
3. **Regression Gates** — Aserción estricta en CI que impida el merge de alteraciones a nodos críticos. (Nota: la integración en CI pertenece a Fase 6; Fase 5 habilita la semántica.)
4. **Calibración empírica** — Validación de umbrales NSS y pesos de criticidad sobre el corpus canónico real.
5. **Resolución de DF-04** — Benchmark comparativo ZhangShasha vs APTED sobre el corpus materializado.

**Hito crítico:** Al cierre de Fase 5, el corpus canónico está materializado en disco con todos los oráculos sellados, la biyección PDF↔oráculo verificada, y los umbrales/pesos calibrados empíricamente. `run_regression.py` ejecuta exitosamente contra el corpus real con veredicto PASS.

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| `ADR_F17-BIS_05.md` | Plantilla canónica de ADR de Fase | Visión arquitectónica de Baseline Certification |
| NADRs de Fase 5 | Plantilla canónica de NADR (9 secciones) | Reglas normativas para materialización, sellado y calibración |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` | Plantilla de Execution Plan | Secuenciación operativa de Fase 5 |
| `FASE_5_DEFERRED_FINDINGS_REGISTER.md` | Plantilla canónica | Registro de hallazgos de Fase 5 |
| `FASE_5_EXIT_REVIEW_EVIDENCE_LOG.md` | Plantilla canónica | Evidencia forense de decisiones |
| HITOs de auditoría (Fase 0 de Fase 5) | Plantilla de HITO | Evidencia forense del estado actual |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro | `docs/architecture/adr/phase-17-bis/ADR_F17_BIS_MASTER.md` |
| ADR Fase 4 | `docs/architecture/adr/phase-17-bis/ADR_F17-BIS_04.md` |
| NADR-F17BIS-18 | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-18.md` |
| NADR-F17BIS-19 | `docs/architecture/adr/phase-17-bis/NADR-F17BIS-19.md` |
| Methodology | `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |
| ENGINEERING_PRINCIPLES | `ENGINEERING_PRINCIPLES.md` |
| ROADMAP | `ROADMAP_ARQUITECTONICO_LP.md` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register Fase 4 | `docs/architecture/adr/phase-17-bis/reviews/FASE_4_DEFERRED_FINDINGS_REGISTER.md` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| Execution Plan Fase 4 | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE4_EXECUTION_PLAN.md` | Trazabilidad temporal de tareas |
| Evidence Log Fase 4 | `docs/architecture/adr/phase-17-bis/reviews/FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md` | Evidencia forense de decisiones |
| PROJECT_TREE | `PROJECT_TREE.txt` | Estructura completa del repositorio |
| PROJECT_SCOPE | `PROJECT_SCOPE.md` | Alcance del proyecto |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: Traductor PDF Científico/Técnico
Descripción: Pipeline local SOTA para ingesta, normalización, traducción LLM y
             reconstrucción de documentos científicos (papers, libros STEM)
             preservando topología, ecuaciones y layout.
Stack: Python 3.11, Pydantic v2, PyMuPDF, pytest, pyright
Arquitectura: DDD + Hexagonal (Ports & Adapters), Functional Core / Imperative Shell,
              Flat AST, Stateless Components, Inmutabilidad estricta
Fase actual completada: Fase 4 — Scientific Verification
Siguiente fase: Fase 5 — Baseline Certification
```

### 8.2 Code State

```text
Tests: 624 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
Rama: main (limpio)
Commit de cierre: 219bc5c
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. Zero Partial Sealing: biyección completa PDF↔oráculo para estado SEALED (ADR Maestro §5)
2. Determinismo: todo pipeline de evaluación/serialización 100% determinista (ADR Maestro §5)
3. Umbrales NSS (0.80/0.95) y pesos criticidad (5.0/2.0/1.0) son PROPUESTA INICIAL
   NO calibrada — Fase 5 debe validar empíricamente (NADR-19 §5.3 R12, NADR-18 §5.3 R14)
4. Reutilizar build_extraction_pipeline() — NO crear pipelines alternativos (NADR-19 §5.5 R20)
5. Verificación Fail-Fast antes de evaluar: integridad → estado → completitud (NADR-19 §5.4)
6. DF-04 pendiente: benchmark ZhangShasha vs APTED requiere corpus materializado (Fase 5)
7. Tests con MagicMock(spec=...) — estándar de Gates 2/3
8. ENGINEERING_PRINCIPLES: YAGNI, Explicit over Implicit, Functional Core, OCP, Cero Fallos Silenciosos
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- FASE_4_HANDOFF.md (este documento)
- ADR_F17_BIS_MASTER.md
- ENGINEERING_PRINCIPLES.md
- ROADMAP_ARQUITECTONICO_LP.md

Prioridad 2 (cargar para implementación):
- NADR-F17BIS-18 (Taxonomía de Criticidad)
- NADR-F17BIS-19 (Regresión Topológica Graduada)
- PHASE_17BIS_FASE4_EXECUTION_PLAN.md (trazabilidad)

Prioridad 3 (consultar según necesidad):
- FASE_4_DEFERRED_FINDINGS_REGISTER.md (hallazgos diferidos)
- FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md (evidencia forense)
- PROJECT_TREE.txt (estructura del repo)
- METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md (gobernanza)
```

### 8.5 Pending Items (carry-forward)

```text
[DF-01] Tests tautológicos (test_golden_parser.py, test_chunker_snapshot.py)
        → Destino: Fase 6 (Continuous Verification)
        → Bloquea: Nada en Fase 5

[DF-02] Verificación ci.yml/pyproject.toml para tests de regresión
        → Destino: Fase 6 (Continuous Verification)
        → Bloquea: Nada en Fase 5

[DF-03] Deuda LayoutBlockDraft (mapper transicional en pipeline_factory.py)
        → Destino: Gate futuro (remediación de layout)
        → Bloquea: Nada en Fase 5

[DF-04] Dualidad ZhangShasha/APTED — benchmark comparativo
        → Destino: Fase 5 (Baseline Certification)
        → Bloquea: Requiere corpus canónico materializado
        → Criterio: divergencia < 1% TED normalizado → deprecar APTED
        → Deadline: Cierre de Fase 5

[GAP-4.5-02] Verificación de PDF antes de extraer (P1, no bloqueante)
        → Destino: Fase 5 o posterior
        → Bloquea: Nada (Fail-Fast implementado vía RegressionAdapter)
```

### 8.6 Work Conventions

```text
- Staff Engineer workflow: auditar → ADR → implementar. Nunca código antes que gobernanza.
- Todo NADR sigue plantilla canónica de 9 secciones. Sin secciones extra.
- Todo cambio requiere Execution Plan aprobado antes de código.
- Findings van al Deferred Findings Register, NO al Execution Plan.
- Tests con MagicMock(spec=...). Sin mocks sin spec.
- Pyright 0 errors, 0 warnings antes de declarar cualquier Gate COMPLETED.
- Zero-touch: no modificar archivos de fases anteriores sin justificación explícita.
- Nombres de archivos: snake_case. Clases: PascalCase. Constantes: UPPER_SNAKE_CASE.
- Inmutabilidad: frozen=True en todos los DTOs. Sin mutación in-place.
- Fail-Fast: ValueError tipado o excepción específica. Nunca degradación silenciosa.
```

### 8.7 System Entry Points

```text
tools/evaluation/run_regression.py          → Evaluación de regresión del runtime contra
                                               oráculo sellado. Exit codes 0/1/2.
tools/evaluation/run_benchmark.py           → Benchmark topológico de extractores.
tools/evaluation/bootstrap_corpus.py        → Bootstrap del manifiesto del corpus.
tools/evaluation/freeze_ground_truth.py     → Sellado de Ground Truth.
tools/evaluation/generate_golden_draft.py   → Generación de borradores dorados.
apps/bootstrap/pipeline_factory.py          → Composition root del pipeline de producción.
                                               build_extraction_pipeline() es la factoría
                                               única de extracción.
bootstrap/topology.py                       → Composition root de evaluación topológica.
                                               create_topology_evaluator() ensambla el TED.
```

---

## 9. CLOSURE CRITERIA

Este handoff se considera cerrado (FROZEN) cuando:

- [x] Resumen ejecutivo completo (§1)
- [x] Estado actual validado con evidencia (§2)
- [x] Decisiones arquitectónicas documentadas (§3)
- [x] Scope entregado listado (§4)
- [x] Todos los items diferidos listados con destino (§5.2)
- [x] Restricciones carry-forward identificadas (§5.1)
- [x] Known risks documentados (§5.3)
- [x] Prerequisitos de siguiente fase definidos (§6)
- [x] Mapa de referencias completo (§7)
- [x] LLM Context Block autocontenido (§8)

**Veredicto:** ✅ CERRADO — FROZEN

---

**Nota de Gobernanza:** Este documento es el punto de transición entre fases.
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado
exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que
cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4)
para tener contexto completo de arranque. Los detalles normativos se consultan bajo
demanda según la tarea específica.