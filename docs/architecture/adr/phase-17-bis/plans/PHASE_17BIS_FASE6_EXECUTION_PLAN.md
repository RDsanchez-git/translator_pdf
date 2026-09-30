# PHASE 17-BIS FASE 6 EXECUTION PLAN v1.0.11
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.11
**Status:** DRAFT
**Date:** 2026-09-30
**Supersedes:** v1.0.10
**Derived From:** 6 NADRs FROZEN (NADR-F17BIS-25 a NADR-F17BIS-30) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de Fase 6 (Continuous Verification). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-25 | Emisión inicial DRAFT. 4 Gates / 9 Waves / 31 Tasks. 167 reglas de 6 NADRs FROZEN asignadas. |
| 1.0.1 | 2026-09-25 | Reestructuración de secciones: Gates como nivel 2. Clarificación de dependencia MIG-02 → Task 1.2.1. |
| 1.0.2 | 2026-09-25 | Correcciones estructurales: Gate 4 NO DEMOSTRADO, eliminación dependencia circular, TASK vs MIG. |
| 1.0.3 | 2026-09-25 | Adaptación a metodología canónica: §1.4 simplificado, tablas con "Rules Implemented", Traceability Appendix con formato canónico de 4 columnas. |
| 1.0.4 | 2026-09-26 | Wave 1.1 completada: Tasks 1.1.1, 1.1.2, 1.1.3 → DONE. 13 reglas de NADR-F17BIS-25 → DONE. Gate 1 → IN PROGRESS. |
| 1.0.5 | 2026-09-26 | Wave 1.2 completada: Tasks 1.2.1-1.2.4 → DONE. 28 reglas de NADR-F17BIS-26 → DONE. Gate 1 → COMPLETED (41/41 reglas, 7/7 Tasks). Gate 1 Exit Review: PASS. |
| 1.0.6 | 2026-09-26 | Wave 2.1 completada: Tasks 2.1.1-2.1.3 → DONE. 35 reglas de NADR-F17BIS-27 → DONE. Gate 2 → IN PROGRESS. |
| 1.0.7 | 2026-09-26 | Wave 2.2 completada: Tasks 2.2.1-2.2.3 → DONE. 34 reglas de NADR-F17BIS-28 → DONE. Gate 2 → COMPLETED (69/69 reglas, 6/6 Tasks). Gate 2 Exit Review: PASS. |
| 1.0.8 | 2026-09-30 | Wave 3.1 completada: Tasks 3.1.1-3.1.3 → DONE. 31 reglas de NADR-F17BIS-29 (§5.1-§5.6) → DONE. Gate 3 → IN PROGRESS. |
| 1.0.9 | 2026-09-30 | Wave 3.2 completada: Tasks 3.2.1-3.2.3 → DONE. 4 reglas adicionales de NADR-F17BIS-29 §5.7 R32-R35 → DONE (35/35 total NADR-29). GAP-6.3-01 (P0) resuelto: CI invoca el verification entry point real vía workflow dedicado. Corrección de contadores en §10.3 (eliminación de filas duplicadas PENDING). |
| 1.0.10 | 2026-09-30 | Wave 3.3 completada: Tasks 3.3.1-3.3.3 → DONE (validación end-to-end transversal, 0 reglas nuevas). DF-08 identificado y resuelto: PDF orphan `doc_06_johnstone.pdf` movido a `tests/corpus/archive/`. Gate 3 → COMPLETED (35/35 reglas NADR-29, 9/9 Tasks). Gate 3 Exit Review: PASS. |
| 1.0.11 | 2026-09-30 | Gate 4 completado: Waves 4.1-4.3 → DONE (Task 4.2.1 BLOCKED → DF-10). 22/22 reglas NADR-30 DONE. MIG-01/MIG-04 ejecutados con evidencia server-side (Task 4.1.3 RESOLVED). DF-11 RESOLVED; DF-06 y DF-10 RECLASSIFIED_FUTURE_PHASE; DF-09 ACCEPTED_LIMITATION. Gate 4 → CONDITIONAL PASS. Fase 6 cerrada: 167/167 reglas, 30/31 tasks. |
---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
ADR_F17_BIS_06 v1.2.0 (decisión arquitectónica de Fase 6, 9 decisiones D1-D9)
↓
NADRs F17BIS-25 a F17BIS-30 (reglas constitucionales permanentes, FROZEN)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_FASE6_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_6_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-F17BIS-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-F17BIS-26 §5.2 R7` → NADR-F17BIS-26, sección 5.2, regla 7.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (NADR-F17BIS-25 a NADR-F17BIS-30, 167 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

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

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §14. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2-§5)
- Notas de implementación por Task (§{N}.{X}.{Y})
- Gate Completion Log (§6)
- Status Dashboard (§9)
- Traceability Appendix (§10)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

### 1.6 Inventario de Reglas por NADR

| NADR | Capacidad | Reglas |
|------|-----------|:------:|
| NADR-F17BIS-25 | Verification Boundary & Production Subject | 13 |
| NADR-F17BIS-26 | Canonical Baseline Materialization & Integrity | 28 |
| NADR-F17BIS-27 | Verification Outcome & Failure Semantics | 35 |
| NADR-F17BIS-28 | Evidence, Identity Chain & Reproducibility | 34 |
| NADR-F17BIS-29 | Continuous Verification Execution Profiles | 35 |
| NADR-F17BIS-30 | CI Enforcement & Merge Protection | 22 |
| **TOTAL** | | **167** |

---

## 2. GATE 1 — VERIFICATION FOUNDATION

**Objective:** Construir la fundación física y arquitectónica sobre la que puede ejecutarse Continuous Verification: el sujeto de verificación conectado al production pipeline y la baseline canónica materializada con integridad verificable.
**Execution Mode:** Secuencial (Wave 1.1 antes que Wave 1.2)
**Rollback Plan:** Revertir commits de Wave 1.1 y 1.2. La baseline sellada no se modifica; solo se modifica el mecanismo de acceso y verificación.
**Gate Status:** ✅ COMPLETED

### 2.1 Wave 1.1 — Production Verification Boundary (NADR-F17BIS-25)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-25
**Fecha de cierre:** 2026-09-26

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Formalizar y aislar el verification entry point normativo de Continuous Verification. Garantizar que el entry point invoca exclusivamente el production pipeline canónico. | NADR-F17BIS-25 §5.1 R1-R4 | High | — | DONE |
| **1.1.2** | Verificar y demostrar que el verification entry point invoca el production pipeline canónico y ejecuta la extracción real sobre los artefactos del corpus. | NADR-F17BIS-25 §5.2 R5-R7 | High | 1.1.1 | DONE |
| **1.1.3** | Verificar que no exista ruta alternativa, sintética o legacy de verificación. Garantizar la frontera de verificación y la prohibición de mecanismos paralelos. | NADR-F17BIS-25 §5.3 R8-R10; §5.4 R11-R13 | Medium | 1.1.2 | DONE |

#### Notas de implementación — Task 1.1.1

> Creado `tests/unit/test_verification_boundary.py` con 6 tests de verificación estructural vía AST parsing. Los tests verifican: (1) el entry point existe en la ubicación canónica, (2) importa `build_extraction_pipeline` desde `apps.bootstrap.pipeline_factory`, (3) no importa módulos prohibidos (providers, adapters), (4) usa `RegressionEvaluationStrategy`, (5) invoca `build_extraction_pipeline()` (correspondencia demostrable), (6) ningún módulo en core/apps/infra importa `RegressionEvaluationStrategy`. Resultado: 6/6 tests passed, pyright 0 errors. Marker `@pytest.mark.integration` (los tests leen archivos del filesystem).

#### Notas de implementación — Task 1.1.2

> Creado `tests/integration/test_verification_pipeline_connection.py` con 4 tests de integración. Los tests verifican: (1) `build_extraction_pipeline()` retorna `PdfParserAdapter`, (2) el pipeline extrae AST no vacío de `doc_01_single.pdf` del corpus canónico, (3) los nodos del AST tienen estructura mínima (node_id, node_type), (4) el pipeline es determinista (dos ejecuciones → mismo AST). Resultado: 4/4 tests passed, pyright 0 errors. Se usa PDF del corpus canónico trackeado en git, no fixtures sintéticos (NADR-F17BIS-26 §5.5 R20-R22).

#### Notas de implementación — Task 1.1.3

> Agregado contrato import-linter en `pyproject.toml`: "Regression orchestration not imported by apps or infra" (source_modules = ["apps", "infra"], forbidden_modules = [strategy, mechanism, adapter, report]). También se corrigió el contrato preexistente de OCR providers: agregado `include_external_packages = true` en configuración top-level y `ignore_imports` para la cadena transitiva `core.benchmark.__main__ → apps.bootstrap.pipeline_factory → ... → fitz`. Resultado: 4/4 contratos KEPT, exit code 0.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-01 | Contrato OCR providers roto por `include_external_packages`; resuelto con `ignore_imports` para cadena transitiva | Findings Register |
| DF-05 | `ignore_imports` huérfanos en pyproject.toml (`core.extraction.ocr_providers.*` inexistente) | Findings Register |
| DF-06 | `core.benchmark.__main__` importa de `apps/` (deuda técnica Gate 3-4) | Findings Register |
| DF-07 | Contrato 3 sin `ignore_imports` para DF-06, causando BROKEN al eliminar ignores huérfanos | Findings Register |

### 2.2 Wave 1.2 — Canonical Baseline Consumption (NADR-F17BIS-26)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-26
**Fecha de cierre:** 2026-09-26

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Implementar el mecanismo de materialización determinista de la baseline canónica en el entorno de ejecución. | NADR-F17BIS-26 §5.1 R1-R5 | High | 1.1.2 | DONE |
| **1.2.2** | Implementar la verificación de integridad física de artefactos (SHA-256 de PDFs, oracle_hash de GTs, manifest_hash del manifest). | NADR-F17BIS-26 §5.2 R6-R10 | High | 1.2.1 | DONE |
| **1.2.3** | Implementar la verificación de completitud y precondiciones de consumo de la baseline. | NADR-F17BIS-26 §5.3 R11-R15 | Medium | 1.2.2 | DONE |
| **1.2.4** | Implementar la protección contra baseline incorrecta, incompleta o mutada. Separación baseline/fixtures. Fallo de integridad de la referencia. Separación de identidades. | NADR-F17BIS-26 §5.4 R16-R19; §5.5 R20-R22; §5.6 R23-R25; §5.7 R26-R28 | Medium | 1.2.3 | DONE |

#### Notas de implementación — Task 1.2.1

> Creada función `verify_baseline_materialized(pdf_dir, manifest)` en `tools/evaluation/run_regression.py`. Verifica que cada PDF listado en el manifest existe en `pdf_dir` antes de iniciar la evaluación. Función simple en el Imperative Shell (YAGNI, ENGINEERING_PRINCIPLES §I). No se creó servicio de dominio completo. Creado `tests/integration/test_baseline_materialization.py` con 6 tests: caso feliz, pdf_dir ausente, PDF individual ausente, mensaje con múltiples PDFs ordenados, manifest vacío, PDFs extra no causan fallo. Resultado: 6/6 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-26 §5.1 R1-R3. R4-R5 se completan con verificación de hashes (Task 1.2.2) y separación baseline/fixtures (Task 1.2.4).

#### Notas de implementación — Task 1.2.2

> Creado `core/benchmark/corpus/integrity.py` con funciones puras de verificación (Functional Core, ENGINEERING_PRINCIPLES §II): `verify_manifest_hash()` (R8, reutiliza `ManifestFingerprintCalculator.compute_hash()`), `verify_pdf_hash()` (R9). Errores de dominio: `BaselineIntegrityError`, `ManifestHashMismatchError`, `PdfIntegrityError`, `PdfMissingError`. Orquestación en `run_regression.py`: `verify_baseline_physical_integrity()` lee PDFs con `compute_sha256_stream()` (streaming, no carga completa en memoria). `manifest_hash` se extrae del DTO (`RawCorpusManifestDTO`) porque `CorpusManifest` no incluye el hash. Creados `tests/unit/test_baseline_integrity.py` (6 tests unitarios, función pura) y `tests/integration/test_baseline_physical_integrity.py` (4 tests de integración). Resultado: 10/10 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-26 §5.2 R6-R10.

#### Notas de implementación — Task 1.2.3

> Implementación combinada de dos propuestas. Parte A: agregado `verify_pdf_ids()` como método estático puro en `BaselineCompletenessVerifier` (`core/benchmark/ground_truth/completeness.py`), verifica biyección manifest↔PDFs incluyendo PDFs orfanos (R11-R12). Parte B: agregado `GTUnreadableError` en `core/benchmark/corpus/integrity.py` y `verify_ground_truth_preconditions()` en `run_regression.py`, verifica legibilidad de GTs antes de evaluación (R13-R14). Captura `except (OSError, ValueError)` que cubre `FileNotFoundError`, `pydantic.ValidationError`, `UnicodeDecodeError` sin capturar errores de programación. Creados `tests/unit/test_baseline_pdf_completeness.py` (6 tests unitarios) y `tests/integration/test_baseline_gt_preconditions.py` (4 tests de integración). Resultado: 10/10 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-26 §5.3 R11-R15.

#### Notas de implementación — Task 1.2.4

> Agregado `EXIT_BASELINE_INTEGRITY_FAILURE = 3` en `run_regression.py` (R25: fallo de integridad no es regresión). Pasos 1-2b envueltos en `try/except (BaselineIntegrityError, IncompleteBaselineError, FileNotFoundError)` → exit code 3. Creado `tests/unit/test_baseline_integrity_semantics.py` (10 tests unitarios: jerarquía de errores R24, separación de identidades R26-R28). Creado `tests/integration/test_baseline_integrity_exit_code.py` (1 test de integración: exit code 3 con mock). Resultado: 11/11 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-26 §5.4 R16-R19 (por diseño: funciones read-only), §5.5 R20-R22 (por diseño + protección CI pendiente en Gate 3), §5.6 R23-R25, §5.7 R26-R28.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 2.3 Gate 1 Exit Criteria

Todas las reglas de NADR-F17BIS-25 y NADR-F17BIS-26 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:

- El verification entry point normativo existe y está formalmente aislado.
- El verification entry point invoca el production pipeline canónico.
- No existe ruta alternativa, sintética o legacy de verificación.
- La baseline canónica es materializable de forma determinista en el entorno de ejecución.
- La integridad física de los artefactos es verificable (SHA-256, oracle_hash, manifest_hash).
- La completitud de la baseline es verificable antes de la evaluación.
- La baseline está protegida contra mutación durante la ejecución.
- La separación entre baseline canónica y fixtures está garantizada.

### 2.4 Gate 1 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 7/7 |
| 2 | Todas las reglas del Gate en estado DONE en §10 | ✅ 41/41 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ DF-01, DF-05, DF-06, DF-07 |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 47 tests |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ PASS
**Fecha de verificación:** 2026-09-26

---

## 3. GATE 2 — VERIFICATION CONTRACT

**Objective:** Eliminar la ambigüedad semántica y hacer que cada ejecución produzca evidencia reconstruible. El resultado de Continuous Verification debe ser inequívoco y la identity chain completa.
**Execution Mode:** Secuencial (Wave 2.1 antes que Wave 2.2)
**Rollback Plan:** Revertir commits de Wave 2.1 y 2.2. La semántica anterior se restaura.
**Gate Status:** ✅ COMPLETED

### 3.1 Wave 2.1 — Outcome & Failure Semantics (NADR-F17BIS-27)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-26
**Fecha de cierre:** 2026-09-26

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Implementar y normalizar la taxonomía de resultados de Continuous Verification. Separar resultado científico de estado operacional. | NADR-F17BIS-27 §5.1 R1-R5; §5.2 R6-R10 | High | Gate 1 | DONE |
| **2.1.2** | Implementar la separación entre scientific verdict y operational/integrity failure. Precedencia de evaluación. Conformance/Regression/Divergence. | NADR-F17BIS-27 §5.3 R11-R15; §5.4 R16-R23 | High | 2.1.1 | DONE |
| **2.1.3** | Normalizar exit-code propagation y precedence. Criticalidad y política de evaluación. | NADR-F17BIS-27 §5.5 R24-R28; §5.6 R29-R35 | High | 2.1.2 | DONE |

#### Notas de implementación — Task 2.1.1

> Creado `core/benchmark/verification/outcome.py` con `VerificationOutcome` enum de 4 estados mutuamente distinguibles (PASS, REGRESSION, BASELINE_INTEGRITY_FAILURE, EXECUTION_FAILURE). Funciones puras: `map_scientific_verdict()` (NADR-19 → NADR-27) y `outcome_to_exit_code()` (traducción determinista). Separación de bounded contexts: `topology/regression/` para NADR-19 (científico), `verification/` para NADR-27 (operacional). Creado `tests/unit/test_verification_outcome.py` con 18 tests: taxonomía R6-R7, mapeo científico/operacional R1, exit codes R29-R33, invariantes R8-R10, test de determinismo (documentación del contrato, no verificación robusta). Resultado: 18/18 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-27 §5.1 R1, §5.2 R6-R10.

#### Notas de implementación — Task 2.1.2

> Agregado `ContinuousVerificationResult` dataclass con `exit_code` como `@property` calculado (DRY, única fuente de verdad). Agregada `resolve_operational_outcome()` que formaliza la precedencia R11-R15: baseline_integrity > execution > scientific. R15 documentado explícitamente: `scientific_verdict=None` produce EXECUTION_FAILURE, no PASS (previene "sin evaluación = sin regresión"). R16-R23 (Conformance/Regression) documentados en docstring sin implementar Conformance (YAGNI). 9 tests nuevos de precedencia e invariantes. Resultado: 27/27 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-27 §5.3 R11-R15, §5.4 R16-R23.

#### Notas de implementación — Task 2.1.3

> Refactorizado `run_regression.py`: eliminadas 4 constantes EXIT_* locales, importadas desde `core.benchmark.verification.outcome` (única fuente de verdad). Extraída función `_run_evaluation()` para Pasos 3-7. Agregado try/except que produce EXIT_EXECUTION_FAILURE = 4 ante excepciones no controladas (resuelve colisión de exit code 1). Paso 7 refactorizado para usar `resolve_operational_outcome()`. Test AST `TestNoLocalExitCodesInEntryPoint` verifica que no hay constantes EXIT_* locales. Creado `test_execution_failure_exit_code.py` con 2 tests (exit 4, no colisión con WARNING). Actualizado import en `test_baseline_integrity_exit_code.py`. Resultado: 77/77 tests passed, pyright 0 errors, import-linter 4/4 KEPT. Cobertura: NADR-F17BIS-27 §5.5 R24-R28, §5.6 R29-R35.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.2 Wave 2.2 — Evidence, Identity & Reproducibility (NADR-F17BIS-28)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-29
**Fecha de cierre:** 2026-09-29

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Completar la identity chain de ejecución. Determinismo de identidad. | NADR-F17BIS-28 §5.1 R1-R7; §5.2 R8-R13 | High | 2.1.3 | DONE |
| **2.2.2** | Persistir evidencia determinista con identity chain completa. | NADR-F17BIS-28 §5.3 R14-R19; §5.6 R31-R34 | Medium | 2.2.1 | DONE |
| **2.2.3** | Validar reproducibilidad y distinguishability histórica. Inmutabilidad y trazabilidad. | NADR-F17BIS-28 §5.4 R20-R24; §5.5 R25-R30 | Medium | 2.2.2 | DONE |

#### Notas de implementación — Task 2.2.1

> Creado `core/benchmark/verification/identity_chain.py` con `IdentityChain` dataclass frozen y funciones puras de composición: `build_parameter_identity()` (reutiliza `FrozenParameters` + `ParameterIdentityCalculator` de NADR-23, ENGINEERING_PRINCIPLES §I), `build_execution_id()` (hash determinista de baseline + subject + config + params, NO incluye result para evitar circularidad), `build_result_identity()` (hash del resultado operacional + científico), `build_identity_chain()` (compone todo y agrega limitations observables R29). Separación de bounded contexts: `topology/regression/provenance.py` tiene los calculadores (NADR-23), `verification/identity_chain.py` tiene la composición (NADR-28). Creado `tests/unit/test_identity_chain.py` con 12 tests: determinismo R8, composición R6, limitations R29. Resultado: 12/12 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-28 §5.1 R1-R7, §5.2 R8-R13.

#### Notas de implementación — Task 2.2.2

> Creado `core/benchmark/verification/report.py` con `ContinuousVerificationReport` dataclass (wrapper que compone `RegressionReport` + `ContinuousVerificationResult` + `IdentityChain` + `schema_version`), `ContinuousVerificationReportFormatter` protocolo, y `JsonContinuousVerificationReportFormatter`. El formatter serializa identity chain completa y resuelve GAP-6.3-02 (`configuration_fingerprint` ahora se incluye). Renombradas funciones privadas `_serialize_evaluation_report` y `_serialize_metric` a públicas en `regression/report.py` (encapsulación). Modificado `build_result_identity()` en `identity_chain.py` para aceptar `regression_report_json` opcional (evolución de diseño: outcomes sin regression_report). Creado `tests/unit/test_verification_report.py` con 13 tests: schema_version R24, identity_chain R15, operational_result R16, regression_report R17, configuration_fingerprint GAP-6.3-02, determinismo R8, R31 (resultado ≠ condiciones). Resultado: 13/13 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-28 §5.3 R14-R19, §5.6 R31-R34.

#### Notas de implementación — Task 2.2.3

> Integración completa en `run_regression.py`: (1) agregadas funciones helper `_get_subject_identity()` (git SHA via subprocess con fallback None, Imperative Shell), `_build_report_filename()` (filename único con execution_id[:16] + timestamp_shell), `_build_timestamp_shell()` (UTC ISO 8601 con guiones para cross-platform); (2) modificado `_run_evaluation()` para retornar `EvaluationArtifacts` (dataclass con regression_report + config_fingerprint + cost_weights); (3) `main()` construye `result_identity`, `IdentityChain`, `ContinuousVerificationReport`, y escribe JSON con filename único (R21: no sobrescribe evidencia histórica) + Markdown con filename fijo (para humanos). Decisiones: sin `latest.json` (Opción C, evita tensión conceptual con R21), `build_result_identity` acepta `regression_report_json=None` para outcomes sin evaluación. Creados `tests/unit/test_subject_identity.py` (5 tests: git disponible, git error, OSError, timeout, stdout vacío) y `tests/integration/test_cv_report_persistence.py` (7 tests: filename único, identity chain en JSON, reproducibilidad de execution_id). Actualizado `tests/integration/test_regression_entry_point.py` (9 tests reescritos para mockear `_run_evaluation` y funciones de Task 2.2.3). Resultado: 835/835 tests passed (suite completa), pyright 0 errors, import-linter 4/4 KEPT. Cobertura: NADR-F17BIS-28 §5.4 R20-R24, §5.5 R25-R30.
> **Evolución de diseño:** Se usó `EvaluationArtifacts` dataclass en lugar de `tuple[RegressionReport, str]` para mayor claridad y legibilidad. El dataclass encapsula `regression_report`, `config_fingerprint` y `cost_weights` como retorno de `_run_evaluation()`.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.3 Gate 2 Exit Criteria

Todas las reglas de NADR-F17BIS-27 y NADR-F17BIS-28 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:

- La taxonomía de resultados está implementada y normalizada.
- El resultado científico está separado del estado operacional.
- Los exit codes son inequívocos y no ambiguos.
- La identity chain de ejecución está completa.
- La evidencia es determinista y persistente.
- La reproducibilidad es verificable.

### 3.4 Gate 2 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 6/6 |
| 2 | Todas las reglas del Gate en estado DONE en §10 | ✅ 69/69 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ Sin hallazgos nuevos |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 835 tests |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ PASS
**Fecha de verificación:** 2026-09-30

---

## 4. GATE 3 — CONTINUOUS VERIFICATION INTEGRATION

**Objective:** Integrar operacionalmente Continuous Verification en CI: materializar perfiles de ejecución, conectar CI al verification entry point, y validar la integración end-to-end.
**Execution Mode:** Secuencial (Wave 3.1 → 3.2 → 3.3)
**Rollback Plan:** Revertir commits de Wave 3.1, 3.2 y 3.3. El workflow CI anterior se restaura.
**Gate Status:** ✅ COMPLETED

### 4.1 Wave 3.1 — Execution Profiles (NADR-F17BIS-29)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-29
**Fecha de cierre:** 2026-09-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Materializar el perfil completo de Continuous Verification (cobertura completa del corpus canónico). | NADR-F17BIS-29 §5.1 R1-R3; §5.3 R14-R17 | Medium | Gate 2 | DONE |
| **3.1.2** | Materializar el perfil reducido / smoke de Continuous Verification (cobertura parcial declarada explícitamente). | NADR-F17BIS-29 §5.4 R18-R23 | Medium | 3.1.1 | DONE |
| **3.1.3** | Validar la semántica de cobertura e identidad de perfiles. Perfiles y mecanismo común. | NADR-F17BIS-29 §5.2 R8-R13; §5.5 R24-R27; §5.6 R28-R31 | High | 3.1.2 | DONE |

#### Notas de implementación — Task 3.1.1

> Creado `core/benchmark/verification/profiles.py` con `VerificationProfile` enum (FULL) y función pura `get_profile_document_ids()`. FULL retorna `frozenset` de todos los `document_id` del `CorpusManifest` (determinista, inmutable, ENGINEERING_PRINCIPLES §III). Separación de bounded contexts: `profiles.py` consume `CorpusManifest` de NADR-26 sin modificarlo. Creado `tests/unit/test_verification_profiles.py` con 10 tests: existencia del enum, inmutabilidad, valor canónico, determinismo, independencia de orden, casos edge (manifest vacío, documento único). Resultado: 10/10 tests passed, pyright 0 errors. Cobertura: NADR-F17BIS-29 §5.1 R1-R3, §5.3 R14-R17.

#### Notas de implementación — Task 3.1.2

> Agregado `SMOKE` al `VerificationProfile` enum con lista hardcoded de 5 documentos representativos: `doc_01_single`, `doc_04_table`, `doc_12_multi_col`, `doc_18_table_math_doble_col`, `doc_22_table_fig_math`. La selección cubre complejidad creciente (baseline → edge case) y los principales rasgos del corpus canonical (native_pdf, nested_tables, multi_column, heavy_math, floating_figures). Intersección con el manifest (`SMOKE_DOCUMENT_IDS & all_ids`) para robustez ante cambios del corpus: si un documento se elimina, el subset se ajusta sin fallar. **Decisión de diseño documentada:** auditoría forense del corpus reveló que el criterio inicial por traits (`traits ⊆ {native_pdf}` + `page_count <= 5`) producía solo 2 documentos calificantes, activando el fallback siempre. La lista hardcoded con justificación explícita es SOTA para este corpus específico. 9 tests nuevos: SMOKE existe, retorna subset de FULL, es determinista, intersección con manifest, frozenset inmutable, exactamente 5 documentos, no altera criterios científicos. Resultado: 19/19 tests acumulados passed, pyright 0 errors. Cobertura: NADR-F17BIS-29 §5.4 R18-R23.

#### Notas de implementación — Task 3.1.3

> Evolución coordinada de 3 componentes:
>
> **1. `IdentityChain` (Wave 2.2 → evolución):** Agregado campo `profile_identity: str`. Modificada función `build_execution_id()` para incluir `profile_identity` en el payload del hash (NADR-29 §5.6 R31: ejecuciones bajo perfiles diferentes producen execution_ids distinguibles). Modificada `build_identity_chain()` para aceptar `profile_identity` como parámetro requerido. Creada función pura `build_profile_identity(profile_name, document_ids)` con ordenamiento determinista (`sorted(document_ids)`).
>
> **2. `ContinuousVerificationReport` (Wave 2.2 → evolución):** Agregado campo `coverage: tuple[str, ...]` que declara explícitamente qué documentos fueron evaluados. `JsonContinuousVerificationReportFormatter` serializa `coverage` como lista ordenada (`sorted()`) para determinismo JSON (NADR-28 §5.2 R8).
>
> **3. `tools/evaluation/run_regression.py`:** Agregado flag `--profile` con choices `["FULL", "SMOKE"]` (default `FULL`). Modificado `_run_evaluation()` para filtrar `manifest.documents` por perfil antes de evaluar (NADR-29 §5.1 R3, §5.5 R24-R27: mismo mecanismo, diferente cobertura). `main()` construye `profile_identity` y `coverage` antes de `build_identity_chain()` y `ContinuousVerificationReport`. Manejo especial: si `manifest is None` (baseline failure), `profile_document_ids = frozenset()` para que la identity chain siempre sea construible.
>
> 17 tests nuevos: `TestBuildProfileIdentity` (5 tests incluyendo edge case empty), `TestCoverageField` (5 tests incluyendo ordenamiento y empty), `TestProfileArgument` (3 tests de CLI), actualización de tests existentes de `build_execution_id` y `build_identity_chain` para incluir `profile_identity`. Resultado: 47/47 tests passed, pyright 0 errors, import-linter 4/4 KEPT. Cobertura: NADR-F17BIS-29 §5.2 R8-R13, §5.5 R24-R27, §5.6 R28-R31.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.2 Wave 3.2 — CI Entry-Point Integration (NADR-F17BIS-25, NADR-F17BIS-27, NADR-F17BIS-29)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-30
**Fecha de cierre:** 2026-09-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Modificar job `regression-gates` en `ci.yml` para invocar `run_regression.py --profile SMOKE`. NO renombrar (preserva branch protection existente). Agregar verificación de mutación del corpus y upload-artifact. | NADR-F17BIS-25 §5.2 R5-R7; NADR-F17BIS-26 §5.4 R16-R19; NADR-F17BIS-29 §5.4 R18-R23 | Critical | 3.1.3 | DONE |
| **3.2.2** | Crear workflow separado `continuous-verification.yml` con job `cv-full-profile`. Triggers: push [main], workflow_dispatch. NO trigger en pull_request (SMOKE cubre PRs). | NADR-F17BIS-25 §5.1 R1-R4; §5.3 R8-R10; NADR-F17BIS-29 §5.1 R1-R7; §5.7 R32-R35 | High | 3.2.1 | DONE |
| **3.2.3** | Tests de contrato del workflow (`test_cv_workflow_contract.py`). Verifica: YAML válido, invocación correcta, persist-credentials, upload-artifact, no pytest -m "regression". | NADR-F17BIS-27 §5.6 R29-R35; NADR-F17BIS-29 §5.6 R28-R31 | Medium | 3.2.2 | DONE |

#### Notas de implementación — Task 3.2.1

> Modificado el job `regression-gates` en `.github/workflows/ci.yml` para invocar `python -m tools.evaluation.run_regression --profile SMOKE` (resuelve GAP-6.3-01 P0: CI ahora invoca el verification entry point real). **Decisión pragmática:** NO se renombró el job a `legacy-regression-gates` para preservar branch protection existente (MIG-01 de Gate 4 actualizará después). Reemplazado completamente el comando `pytest -m "regression"` (que seleccionaba 0 tests). Agregados: verificación de mutación del corpus canónico (`git diff tests/corpus/canonical/`, NADR-26 §5.4 R16-R19), upload-artifact con `if: always()` (NADR-28 §5.3 R14, crítico para debugging de EXECUTION_FAILURE y BASELINE_INTEGRITY_FAILURE). Mantenido: verificación de mutación de oráculos (`git diff tests/fixtures/`, NADR-10 §5.1 R2). Invocación como módulo (`python -m`) resuelve imports absolutos sin PYTHONPATH.

#### Notas de implementación — Task 3.2.2

> Creado `.github/workflows/continuous-verification.yml` con job `cv-full-profile`. Triggers: push [main] + workflow_dispatch. NO se incluye trigger `pull_request`: FULL es costoso (~4 min) y SMOKE en `ci.yml` cubre PRs con ~1 min, consistente con NADR-29 §5.4 R18 (detección rápida). Sin `static-analysis` en este workflow: corre en paralelo con `ci.yml` (separación de responsabilidades). `persist-credentials: false`, `CORPUS_READONLY: true`, verificación de mutación del corpus (`git diff tests/corpus/canonical/`), upload-artifact con `if: always()` apuntando a `reports/continuous-verification/` (output dir separado del SMOKE `reports/continuous-verification-smoke/`). Concurrency control evita ejecuciones redundantes en el mismo ref.

#### Notas de implementación — Task 3.2.3

> Creado `tests/unit/test_cv_workflow_contract.py` con 22 tests de contrato en 4 clases: `TestWorkflowFilesExist` (4 tests: existencia + YAML válido), `TestRegressionGatesJobContract` (8 tests: invocación de `run_regression.py`, uso de SMOKE, no pytest marker, persist-credentials, verificación de mutación, upload-artifact con `if: always()`), `TestCvFullProfileWorkflowContract` (9 tests: job, invocación FULL, triggers push [main] + workflow_dispatch, no pull_request, persist-credentials, verificación de mutación, upload-artifact, concurrency), `TestProfileSeparation` (1 test: output dirs distinguibles entre FULL y SMOKE). Usa `pyyaml` (disponible 6.0.3) para parseo YAML; skip condicional con `pytest.importorskip` si no está disponible. Resuelve GAP-6.3-01 a nivel de test contract. Resultado: 22/22 passed, pyright 0 errors, import-linter 4/4 KEPT.

#### Decisiones de diseño documentadas

| Decisión | Justificación |
|----------|---------------|
| NO renombrar `regression-gates` a legacy | Preserva branch protection existente. Renombrado se hará en Gate 4 (MIG-01) cuando se actualice la configuración server-side |
| FULL sin pull_request trigger | Costo ~4 min por PR degrada experiencia de desarrollo. SMOKE (~1 min) cubre PRs (NADR-29 §5.4 R18) |
| Sin static-analysis en CV workflow | Separación de responsabilidades. Ambos workflows corren en paralelo |
| `python -m tools.evaluation.run_regression` | Invocación como módulo resuelve imports absolutos sin PYTHONPATH |
| Output dirs separados | `reports/continuous-verification/` (FULL) vs `reports/continuous-verification-smoke/` (SMOKE) |
| Reemplazo total de `pytest -m "regression"` | El comando anterior seleccionaba 0 tests. No tiene sentido mantenerlo junto al nuevo |

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

#### Notas de referencia cruzada (§1.4)

> Las reglas de NADR-F17BIS-25 §5.1 R1-R4 y §5.2 R5-R7 aparecen en Task 1.1.1, 1.1.2 (implementación) y Task 3.2.1, 3.2.2 (verificación en contexto CI). No hay doble implementación: Task 1.1.x implementa la capacidad, Task 3.2.x verifica que la capacidad está operativa en CI.

### 4.3 Wave 3.3 — Profile & Gate Validation (NADR-F17BIS-25 a NADR-F17BIS-29)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-30
**Fecha de cierre:** 2026-09-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Validar el Full Profile end-to-end contra corpus canónico real. | NADR-F17BIS-28 §5.3 R14-R17; NADR-F17BIS-29 §5.3 R14-R17 (verificación transversal) | High | 3.2.3 | DONE |
| **3.3.2** | Validar el Reduced Profile y la cobertura explícita. Verificar que un resultado PASS del perfil reducido no implica cobertura completa. | NADR-F17BIS-29 §5.2 R8-R13; §5.4 R18-R23 (verificación transversal) | Medium | 3.3.1 | DONE |
| **3.3.3** | Validar evidencia + resultado + exit semantics por perfil. Verificar que la identity chain permite distinguir perfiles. | NADR-F17BIS-28 §5.2 R8; NADR-F17BIS-29 §5.6 R28-R31 (verificación transversal) | Medium | 3.3.2 | DONE |

#### Notas de implementación — Task 3.3.1

> Creado `tests/integration/test_cv_profile_validation.py` con clase `TestFullProfileValidation` (4 tests e2e). Ejecuta `run_regression.py --profile FULL` contra el corpus canónico real (21 documentos del manifest v3.9). Verifica: veredicto científico válido (no operacional), coverage = 21 documentos, identity chain completa con todos los campos, regression_report presente. Marker `@pytest.mark.e2e` para ejecución bajo demanda (~25s total). Assert contra BASELINE_INTEGRITY_FAILURE y EXECUTION_FAILURE como defensa en profundidad: si el pipeline falla operacionalmente, el test falla con mensaje claro indicando que el problema es del pipeline, no de la validación de perfiles.
>
> **Hallazgo DF-08:** Durante la primera ejecución, el test detectó `BASELINE_INTEGRITY_FAILURE: PDF completeness violations: Orphan PDF (not in manifest): doc_06_johnstone`. El PDF orphan estaba en `tests/corpus/canonical/pdf/` sin entrada en `manifest.json` v3.9, violando NADR-26 §5.3 R11-R12 (biyección perfecta). Resuelto moviendo el PDF a `tests/corpus/archive/` con README documentando. Manifest v3.9 y manifest_hash (`727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`) permanecen invariados. La baseline sellada no se modifica. Ver §2.4 del Findings Register.

#### Notas de implementación — Task 3.3.2

> Agregada clase `TestSmokeProfileValidation` (4 tests e2e). Ejecuta `run_regression.py --profile SMOKE` contra corpus canónico. Verifica: veredicto científico válido, coverage = 5 documentos específicos (`doc_01_single`, `doc_04_table`, `doc_12_multi_col`, `doc_18_table_math_doble_col`, `doc_22_table_fig_math`), smoke ⊂ full (subconjunto estricto), PASS de SMOKE no implica verificación completa (R22: la cobertura limitada es observable en la evidencia independientemente del veredicto).
>
> **Bug corregido durante implementación:** La versión inicial del test `test_smoke_pass_does_not_imply_full_verification` intentaba comparar `smoke_coverage` con `set(data["regression_report"]["documents"])`, pero `documents` contiene dicts serializados (no hashables). Simplificado a verificación directa de `len(coverage) < EXPECTED_FULL_COVERAGE_SIZE`, que es la propiedad fundamental que R22 exige.

#### Notas de implementación — Task 3.3.3

> Agregada clase `TestProfileIdentityValidation` (5 tests e2e). Ejecuta FULL y SMOKE y compara evidencia: execution_id diferente entre perfiles (NADR-29 §5.6 R31), profile_identity diferente entre perfiles (R28-R29), determinismo de execution_id en dos ejecuciones equivalentes de SMOKE (NADR-28 §5.2 R8), determinismo de profile_identity, exit code consistente con veredicto científico (NADR-27 §5.6 R29-R35).
>
> **Nota sobre determinismo:** Se usa SMOKE en lugar de FULL para las pruebas de determinismo, reduciendo tiempo de ejecución. El determinismo es una propiedad del mecanismo de identidad, no del perfil específico.

#### Decisiones de diseño documentadas

| Decisión | Justificación |
|----------|---------------|
| Marker `@pytest.mark.e2e` para tests lentos | ~25s de ejecución total; ejecutables bajo demanda sin ralentizar suite estándar |
| Veredicto científico válido sin asumir HARD_FAIL | Robusto ante mejora futura de baseline (Fase 18). El corpus actual produce REGRESSION (NSS ~0.72 < threshold 0.80), pero el test no acopla a ese estado específico |
| Assert contra fallos operacionales | Defensa en profundidad: distingue problema de pipeline de divergencia topológica real |
| PDF orphan movido a archive/ (no eliminado) | Preserva trazabilidad histórica del corpus. Reversible si se sella GT en el futuro |
| Sin fixture para tests e2e | El assert contra BASELINE_INTEGRITY_FAILURE es la defensa correcta. Un fixture sería redundante |

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-08 | PDF orphan `doc_06_johnstone.pdf` en `tests/corpus/canonical/pdf/` sin entrada en manifest v3.9 | Findings Register §2.4 |

#### Notas de referencia cruzada (§1.4)

> Wave 3.3 es validación transversal end-to-end: no implementa reglas nuevas, verifica que las reglas implementadas en Waves 3.1 y 3.2 funcionan correctamente en ejecución real contra el corpus canónico. Las reglas NADR-28 §5.2 R8, §5.3 R14-R17 y NADR-29 §5.2 R8-R13, §5.3 R14-R17, §5.4 R18-R23, §5.6 R28-R31 fueron verificadas end-to-end en esta Wave.

### 4.4 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-25 a NADR-F17BIS-29 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:

- El perfil completo está materializado y operativo.
- El perfil reducido / smoke está materializado con cobertura declarada explícitamente.
- CI invoca el verification entry point normativo (no el selector vacío pytest).
- La cadena EVENT → CI → PROFILE → ENTRY POINT → PRODUCTION PIPELINE → SEALED BASELINE → EVALUATION → RESULT → EVIDENCE → CI STATUS está completa y demostrable.
- El resultado de Continuous Verification se propaga correctamente al CI.

### 4.5 Gate 3 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ 9/9 |
| 2 | Todas las reglas del Gate en estado DONE en §10 | ✅ 35/35 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ DF-08 RESOLVED |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 906 tests (incluye 13 e2e) |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ PASS
**Fecha de verificación:** 2026-09-30

---

## 5. GATE 4 — ENFORCEMENT & PHASE CLOSURE

**Objective:** Convertir Continuous Verification en control efectivo de integración (enforcement de merge) y cerrar la fase con cierre operativo completo.
**Execution Mode:** Secuencial (Wave 4.1 → 4.2 → 4.3)
**Rollback Plan:** Revertir commits de Wave 4.1, 4.2 y 4.3. La documentación de enforcement se elimina. La configuración server-side de branch protection debe revertirse manualmente por el administrador del repositorio.
**Gate Status:** ✅ COMPLETED (CONDITIONAL PASS)

### 5.1 Wave 4.1 — Merge Enforcement (NADR-F17BIS-30)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-30
**Fecha de cierre:** 2026-09-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Declarar el enforcement contract: documentación de Required Checks y branch protection esperada. | NADR-F17BIS-30 §5.1 R1-R3; §5.2 R4-R6; §5.4 R11-R13 | Medium | Gate 3 | DONE |
| **4.1.2** | Verificar la relación resultado → integración. Garantizar que un resultado bloqueante impide la integración. | NADR-F17BIS-30 §5.3 R7-R10; §5.7 R20-R22 | High | 4.1.1, MIG-01 | DONE |
| **4.1.3** | Obtener y registrar evidencia server-side de branch protection. | NADR-F17BIS-30 §5.5 R14-R16; §5.6 R17-R19 | Critical | 4.1.2, MIG-04 | DONE |

#### Notas de implementación — Task 4.1.1

> Creado `docs/architecture/adr/phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md` v1.0.0 (parcheado post-MIG-01). Declara Opción B transicional: `static-analysis` como único required check; `regression-gates` (SMOKE) y `cv-full-profile` (FULL) informativos. Cláusulas de activación §6.1 (promoción de checks CV a required cuando el estado basal sea PASS o exista recalibración gobernada DC-6.6, con declaración explícita de que WARNING también bloqueará al promocionar y prohibición de wrapper por NADR-27 §5.6 R32), §6.2 (evidencia server-side en `reports/evidence/`), §6.3 (cierre del hueco restante: migración a PRs + ruleset). Alternativas rechazadas documentadas: A (required hoy → teatro de enforcement), C (sin protection → hueco total), D (gate relativo → cambia semántica NADR-19/27 sin gobernanza), ruleset transicional (chicken-and-egg con push directo). Ubicación en `plans/` según Guía de Documentación de Arquitectura §4.
>
> **Parches post-MIG-01 (verificación empírica):** §4.2 item 2 corregido: con required status checks activos, un commit nuevo sin checks pasados es rechazado (el push directo del maintainer queda gateado); lo diferido no es el bloqueo de entrada sino que los checks CV aún no son required. §6.3 corregido en consecuencia. Nota de nombres reportados agregada bajo §3 (GitHub lista checks por el campo `name:` del job, no por su ID). §10 DF-09 re-scoped: el hueco de push directo quedó cerrado por la activación; DF-09 cubre solo el enforcement CV diferido.

#### Notas de implementación — Task 4.1.2

> Creado `tests/unit/test_enforcement_contract.py` (12 tests, marker unit): verifica que `static-analysis` es el único REQUIRED, que ambos checks CV son informativos, que la cláusula 6.1 declara el comportamiento de WARNING al promocionar y prohíbe el wrapper (NADR-27 §5.6 R32), que la tabla de alternativas rechazadas existe (A, C, D, Ruleset), que el scope de enforcement post-MIG-01 consta sin eufemismos, y que la evidencia binaria vive en `reports/evidence/` (no `reviews/`). Relación resultado → integración: garantizada hoy para `static-analysis` (required); para checks CV, diferida condicionalmente por cláusula 6.1 (DF-09). Paths REGRESSION y FAILURE verificados end-to-end en Wave 4.2 (exit 2 y exit 3 ⇒ check rojo ⇒ bloqueo al ser required).

#### Notas de implementación — Task 4.1.3

> MIG-01 ejecutado 2026-09-30: classic branch protection rule sobre `main` con "Static Analysis (pyright + import-linter)" como único required status check (desviación documentada respecto del texto original de MIG-01, que nombraba `regression-gates`; la desviación es la Opción B del contrato §3). Evidencia server-side: `docs/architecture/adr/phase-17-bis/reports/evidence/branch-protection-main.png` (regla creada, aplica a 1 branch) y `branch-protection-main-detail.png` (required checks visibles). MIG-04: configuración activa verificada; la efectividad operativa (merge gateado hasta check verde) se demuestra con el flujo rama → PR → merge del commit de cierre, cuya evidencia (`branch-protection-pr-gate.png`) se anexa al merge. NADR-30 §5.5 R14-R16 satisfecho con evidencia real: NO es NO DEMOSTRADO.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-09 | Enforcement de merge de CV diferido condicionalmente (checks CV informativos hasta cláusula 6.1) | Findings Register §2.4 |

### 5.2 Wave 4.2 — End-to-End Continuous Verification (NADR-F17BIS-25 a NADR-F17BIS-30)

**Wave Status:** ✅ COMPLETED (con Task 4.2.1 BLOCKED)
**Fecha de inicio:** 2026-09-30
**Fecha de cierre:** 2026-09-30

**Nota crítica sobre Task 4.2.1 (PASS path):** La existencia de un escenario PASS legítimo es una **precondición verificable**, no una asunción. Con el estado actual de la baseline (Phase 5: 163 Critical FN, NSS 0.7208), una ejecución legítima produce HARD_FAIL conforme a NADR-19 (DoubleProtectionMechanism). Si durante la ejecución no existe un escenario PASS legítimo (sin rutas sintéticas ni fixtures alternativos), la Task queda BLOCKED y se deriva al Findings Register. No se fabrica un PASS para cerrar el gate.

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Validar el PASS path end-to-end. **Precondición:** ejecución legítima PASS contra la referencia canónica sin rutas sintéticas. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Critical | 4.1.3 | BLOCKED |
| **4.2.2** | Validar el REGRESSION / divergence path end-to-end. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.1 | DONE |
| **4.2.3** | Validar el Operational / integrity failure path end-to-end. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.2 | DONE |

#### Notas de implementación — Task 4.2.1

> **BLOCKED.** Verificación empírica 2026-09-30: `run_regression.py --profile FULL` y `--profile SMOKE` contra el corpus canónico producen exit code 2 (HARD_FAIL / REGRESSION) en ambos perfiles (NSS 0.7208 < threshold 0.80, 163 Critical FN). No existe escenario PASS legítimo: recalibrar thresholds está fuera de scope (DC-6.6 del ADR Maestro) y fabricar un PASS con fixtures violaría NADR-26 §5.5 R20-R22. Derivado como DF-10 (RECLASSIFIED_FUTURE_PHASE: mejora de fidelidad de extracción en fase futura no faseada, o recalibración gobernada). No se fabrica un PASS para cerrar el gate.

#### Notas de implementación — Task 4.2.2

> Creado `tests/integration/test_cv_regression_path.py` (6 tests, marker e2e, fixture module-scoped que ejecuta SMOKE una sola vez contra el corpus real para no multiplicar costo). Verifica la cadena completa: RESULT (outcome REGRESSION, scientific_verdict HARD_FAIL, exit code 2) → EVIDENCE (CV report persistido con coverage de 5 docs, identity chain completa con profile_identity y execution_id, regression_report presente con corpus_verdict HARD_FAIL) → CI STATUS (exit ≠ 0 ⇒ check rojo ⇒ bloquea integración cuando el check sea required, cláusula 6.1). Creado `tests/helpers/cv_execution.py` como SSOT de invocación vía subprocess: reproduce exactamente lo que observa CI (exit code del proceso `python -m tools.evaluation.run_regression`), conforme NADR-27 §5.6 R32.

#### Notas de implementación — Task 4.2.3

> Creado `tests/integration/test_cv_failure_path.py` (6 tests, marker integration: el failure path aborta en verificación de materialización antes de cualquier extracción, es rápido y queda cubierto por la suite estándar). Verifica cadena: FAILURE (BASELINE_INTEGRITY_FAILURE, exit 3) → EVIDENCE (CV report con operational_result exit 3, scientific_verdict None, clave `regression_report` ausente por diseño del formatter) → CI STATUS (exit 3 ⇒ rojo). Escenarios: pdf_dir inexistente con corpus mínimo válido; y cobertura de **DF-11**: manifest JSON inválido (`json.JSONDecodeError`) y manifest con schema inválido (`pydantic.ValidationError`) producen exit 3 con evidencia persistida, no traceback. Relación con `test_baseline_integrity_exit_code.py` (Gate 1): aquel verifica exit 3 in-process con mock; este verifica el proceso real completo vía subprocess. Sin duplicación de lógica (Reuse Before Invent).

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-10 | PASS path no demostrable con estado basal del extractor (HARD_FAIL legítimo en FULL y SMOKE) | Findings Register §2.4 |
| DF-11 | Manifest corrupto escapaba del except de Pasos 1-2b (traceback, exit 1, sin evidencia) | Findings Register §2.4 |

### 5.3 Wave 4.3 — Final Verification & Exit Review (Todos los NADRs)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-30
**Fecha de cierre:** 2026-09-30

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Full corpus Continuous Verification: ejecutar el perfil completo contra el corpus canónico sellado y verificar el resultado en sus dimensiones. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.3 | DONE |
| **4.3.2** | Static analysis + complete test suite + import-linter. Verificar que no hay regresiones en el código existente. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Low | 4.3.1 | DONE |
| **4.3.3** | Exit Review Evidence / traceability closure. Verificar que todas las reglas están DONE en §10 y que la trazabilidad está completa. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Low | 4.3.2 | DONE |

#### Notas de implementación — Task 4.3.1

> Re-ejecución de validación end-to-end incluida en la suite completa: 13 tests e2e de `test_cv_profile_validation.py` (Wave 3.3) + 6 tests e2e de `test_cv_regression_path.py` (Wave 4.2) = 19/19 passed contra el corpus canónico sellado (manifest v3.9, manifest_hash `727782fe...19f7d`). Resultado científico basal: HARD_FAIL (REGRESSION), coherente con el estado del extractor y documentado como esperado (DF-10). Dimensiones verificadas: Regression (veredicto y métricas), Operational integrity (exit codes y evidencia), Conformance no implementada (YAGNI, documentado en NADR-27 §5.4).

#### Notas de implementación — Task 4.3.2

> Suite completa: 930 passed, 5 skipped, 0 collection errors. Los 5 skips son precondiciones ausentes documentadas (GROQ_API_KEY, golden fingerprint, 3 moldes de traducción). Pyright: 0 errors. Import-linter: 4/4 KEPT. Incluye fix de deuda preexistente de Fase 16: imports `helpers.*` → `tests.helpers.*` en `test_translation_semantics.py`, `test_translation_structure.py` y `test_translation_technical.py` (fallaban en collection con `ModuleNotFoundError`); fix de 2 líneas por archivo, sin exclusión de tests (excluirlos habría sido burocracia, no ingeniería). Agrega excludes de directorios pesados en `[tool.pyright]` de `pyproject.toml` (venv, reports, build, dist, node_modules, __pycache__, dot-dirs) sin cambiar la política de include (core/apps/infra/runtime).

#### Notas de implementación — Task 4.3.3

> Traceability closure: las 22 reglas de NADR-30 trazadas en §10.4 con estado DONE y notas donde aplica (§5.3 R7-R10: garantizado para `static-analysis`; para checks CV, diferido por cláusula 6.1 / DF-09). Gate 4 Exit Review ejecutado con veredicto CONDITIONAL PASS: Task 4.2.1 BLOCKED (DF-10) y enforcement CV diferido (DF-09). DoD Nivel B del ADR Maestro: satisfecho en implementación local, verificación estática, corpus materializado y evidencia server-side de enforcement; parcialmente satisfecho en PASS path end-to-end y en bloqueo de merge por regresión estructural (ambos documentados con destino explícito). Cierre de Fase 6 con handoff (`handoff/FASE_6_HANDOFF.md`).

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 5.4 Gate 4 Exit Criteria

Todas las reglas de NADR-F17BIS-25 a NADR-F17BIS-30 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:

- El enforcement contract está documentado en el repositorio.
- La relación resultado → integración está verificada.
- La evidencia server-side de branch protection está obtenida **O** documentada como NO DEMOSTRADO con finding derivado al Findings Register.
- Los tres paths end-to-end (PASS, REGRESSION, FAILURE) están validados **O** documentados como BLOCKED con finding derivado.
- El full corpus Continuous Verification está ejecutado y verificado.
- Static analysis + complete test suite + import-linter están en verde.
- La trazabilidad está completa y cerrada.

**Nota sobre NO DEMOSTRADO y CONDITIONAL PASS:**

Si Task 4.1.3 (evidencia server-side) o Task 4.2.1 (PASS path) quedan BLOCKED o NO DEMOSTRADO, el Gate 4 se cierra como **CONDITIONAL PASS** y los findings se derivan al Findings Register. El DoD Nivel B del ADR Maestro queda **parcialmente satisfecho** y esto se documenta explícitamente en el Exit Review. NO DEMOSTRADO no es una forma alternativa de DONE; es un estado que impide el cierre completo del Gate.

### 5.5 Gate 4 Exit Review

Antes de declarar el Gate como COMPLETED, se ejecuta el proceso de Revisión Post-Implementación definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §6.6.

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE o BLOCKED con finding derivado | ✅ 8/9 DONE + 1 BLOCKED (4.2.1 → DF-10) |
| 2 | Todas las reglas del Gate en estado DONE en §10 o documentadas como NO DEMOSTRADO | ✅ 22/22 DONE (sin NO DEMOSTRADO: MIG-01/MIG-04 con evidencia real) |
| 3 | Gate Exit Criteria satisfechos (o documentados como parcialmente satisfechos) | ⚠️ Parciales: enforcement CV diferido (DF-09); PASS path BLOCKED (DF-10) |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ DF-06 reclasificado, DF-09, DF-10, DF-11 |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ 930 passed, 5 skipped |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** CONDITIONAL PASS
**Fecha de verificación:** 2026-09-30

**Justificación del CONDITIONAL PASS:** Task 4.2.1 (PASS path) queda BLOCKED porque el estado basal del extractor produce HARD_FAIL legítimo (NSS 0.7208 < 0.80, 163 Critical FN) en FULL y SMOKE; no existe PASS legítimo sin recalibración gobernada (DC-6.6) ni fabricación de fixtures (NADR-26 §5.5 R20-R22). DF-09 documenta que el enforcement de merge de Continuous Verification está diferido condicionalmente (checks CV informativos hasta cláusula 6.1). Ambos derivados al Findings Register con destino explícito. El DoD Nivel B del ADR Maestro queda parcialmente satisfecho en esas dos dimensiones y completamente satisfecho en el resto, incluida la evidencia server-side de branch protection (Task 4.1.3 RESOLVED, no NO DEMOSTRADO).

---

## 6. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-09-26 | 41/41 | 7/7 | 4 (DF-01, DF-05, DF-06, DF-07) | Verification Foundation — PASS |
| Gate 2 | 2026-09-29 | 69/69 | 6/6 | 0 | Verification Contract — PASS |
| Gate 3 | 2026-09-30 | 35/35 | 9/9 | 1 (DF-08 RESOLVED) | Continuous Verification Integration — PASS |
| Gate 4 | 2026-09-30 | 22/22 | 8/9 | 4 (DF-06 reclasificado, DF-09, DF-10, DF-11) | Enforcement & Phase Closure — CONDITIONAL PASS |
| **TOTAL** | — | **167/167** | **30/31** | **8 distintos + 1 reclasificación** | Fase 6 cerrada |

**Nota de contabilidad de hallazgos:** El total cuenta 8 hallazgos distintos (DF-01, DF-05, DF-06, DF-07, DF-08, DF-09, DF-10, DF-11). DF-06 aparece dos
veces en el log porque se deriva en Gate 1 y se reclasifica en Gate 4; la columna registra eventos de derivación/reclasificación, no hallazgos nuevos.

**Nota sobre Wave 3.3:** Las 3 tasks de Wave 3.3 (3.3.1, 3.3.2, 3.3.3) son validación end-to-end transversal que no implementa reglas nuevas de NADRs. Verifican que las 35 reglas NADR-29 implementadas en Waves 3.1 y 3.2 funcionan correctamente en ejecución real contra el corpus canónico. Todas las reglas NADR-29 (35) están implementadas.

---

## 7. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Configurar branch protection en GitHub: requerir check como Required Status Check en rama `main`. | GitHub (server-side) | NADR-F17BIS-30 §5.4 R11-R13 | Screenshot / API response | DONE (2026-09-30, con desviación documentada: required check = "Static Analysis (pyright + import-linter)" según ENFORCEMENT_CONTRACT §3; checks CV informativos hasta cláusula 6.1) |
| **MIG-02** | Configurar mecanismo de materialización de PDFs del corpus canónico en CI. | CI | NADR-F17BIS-26 §5.1 R1-R5 | Workflow CI actualizado | DONE (corpus trackeado en git; el checkout materializa los PDFs; verificado en runs de Gate 3 y Gate 4) |
| **MIG-03** | Actualizar workflow CI para invocar el verification entry point normativo en lugar del selector vacío pytest. | CI | NADR-F17BIS-25 §5.2 R5-R7 | Workflow CI actualizado | DONE (Gate 3, Wave 3.2; GAP-6.3-01 resuelto) |
| **MIG-04** | Verificar que la configuración de branch protection está activa y es efectiva. | GitHub (server-side) | NADR-F17BIS-30 §5.5 R14-R16 | Evidencia externa | DONE (2026-09-30: activa vía `reports/evidence/branch-protection-main.png` y `-detail.png`; efectividad operativa demostrada con el PR gateado del commit de cierre, `branch-protection-pr-gate.png`) |

---

## 8. GLOBAL DoD (Definition of Done)

La Fase 6 se considera oficialmente completada cuando:

```text
{All rules in FROZEN NADRs} − {Rules with DONE status in §10} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 9. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§10), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 7 | 41 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 6 | 69 | 0 | 0 | ✅ COMPLETED |
| Gate 3 | 9 | 35 | 0 | 0 | ✅ COMPLETED |
| Gate 4 | 8 | 22 | 0 | 0 | 🟡 CONDITIONAL PASS |
| **TOTAL** | **30** | **167** | **0** | **0** | ✅ FASE 6 CERRADA |

**Nota de contabilidad:** Task 4.2.1 queda BLOCKED (no DONE) con DF-10 derivado; por eso el total de tasks es 30/31. Las 167 reglas de los NADRs FROZEN están en estado DONE: el Global DoD §8 se cumple en reglas, con condicionantes operativos documentados en DF-09 (enforcement CV diferido) y DF-10 (PASS path no demostrable con el estado basal del extractor).

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2-§5)
2. Se agregan las Notas de implementación de la Task (§{N}.{X}.{Y})
3. Se actualiza el `Derived Status` de sus reglas en §10
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§{N}.4 o §{N}.5)

---

## 10. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2-§5); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 10.1 Gate 1 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-25 §5.1 R1 | DONE | Wave 1.1 / Task 1.1.1 | Test AST: entry point existe en ubicación canónica |
| NADR-F17BIS-25 §5.1 R2 | DONE | Wave 1.1 / Task 1.1.1 | Test AST: importa desde composition root canónica, no importa módulos prohibidos |
| NADR-F17BIS-25 §5.1 R3 | DONE | Wave 1.1 / Task 1.1.1 | Test AST: no importa providers/adapters directamente |
| NADR-F17BIS-25 §5.1 R4 | DONE | Wave 1.1 / Task 1.1.1 | Test AST: usa RegressionEvaluationStrategy e invoca build_extraction_pipeline() |
| NADR-F17BIS-25 §5.2 R5 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local + verificación CI: job `regression-gates` invoca `run_regression.py --profile SMOKE` |
| NADR-F17BIS-25 §5.2 R6 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local + verificación CI: job `regression-gates` invoca `run_regression.py --profile SMOKE` |
| NADR-F17BIS-25 §5.2 R7 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local + verificación CI: job `regression-gates` invoca `run_regression.py --profile SMOKE` |
| NADR-F17BIS-25 §5.3 R8 | DONE | Wave 1.1 / Task 1.1.3; Wave 3.2 / Task 3.2.2 | Test AST + contrato import-linter KEPT |
| NADR-F17BIS-25 §5.3 R9 | DONE | Wave 1.1 / Task 1.1.3; Wave 3.2 / Task 3.2.2 | Test AST + contrato import-linter KEPT |
| NADR-F17BIS-25 §5.3 R10 | DONE | Wave 1.1 / Task 1.1.3; Wave 3.2 / Task 3.2.2 | Test AST + contrato import-linter KEPT |
| NADR-F17BIS-25 §5.4 R11 | DONE | Wave 1.1 / Task 1.1.3 | Test AST: no hay mecanismo paralelo en core/apps/infra |
| NADR-F17BIS-25 §5.4 R12 | DONE | Wave 1.1 / Task 1.1.3 | Test AST: no hay mecanismo paralelo en core/apps/infra |
| NADR-F17BIS-25 §5.4 R13 | DONE | Wave 1.1 / Task 1.1.3 | Test AST: no hay mecanismo paralelo en core/apps/infra |
| NADR-F17BIS-26 §5.1 R1 | DONE | Wave 1.2 / Task 1.2.1; MIG-02 | verify_baseline_materialized: presencia de PDFs en pdf_dir |
| NADR-F17BIS-26 §5.1 R2 | DONE | Wave 1.2 / Task 1.2.1; MIG-02 | verify_baseline_materialized: materialización antes de evaluación |
| NADR-F17BIS-26 §5.1 R3 | DONE | Wave 1.2 / Task 1.2.1; MIG-02 | verify_baseline_materialized: correspondencia con documentos del manifest |
| NADR-F17BIS-26 §5.1 R4 | DONE | Wave 1.2 / Task 1.2.2 | verify_pdf_hash: sha256 demuestra identidad real, no solo presencia |
| NADR-F17BIS-26 §5.1 R5 | DONE | Wave 1.2 / Task 1.2.4; Wave 3.2 / Task 3.2.1 | Separación baseline/fixtures por diseño; protección CI resuelta en Gate 3 (git diff tests/corpus/canonical/ en workflows) |
| NADR-F17BIS-26 §5.2 R6 | DONE | Wave 1.2 / Task 1.2.2 | verify_pdf_hash: integridad verificable antes de consumo |
| NADR-F17BIS-26 §5.2 R7 | DONE | Wave 1.2 / Task 1.2.2 | verify_pdf_hash: identidad declarada == observada |
| NADR-F17BIS-26 §5.2 R8 | DONE | Wave 1.2 / Task 1.2.2 | verify_manifest_hash: manifest_hash declarado == recalculado |
| NADR-F17BIS-26 §5.2 R9 | DONE | Wave 1.2 / Task 1.2.2 | verify_pdf_hash: sha256 de cada PDF contra manifest |
| NADR-F17BIS-26 §5.2 R10 | DONE | Wave 1.2 / Task 1.2.2 | ManifestHashMismatchError / PdfIntegrityError impiden consumo |
| NADR-F17BIS-26 §5.3 R11 | DONE | Wave 1.2 / Task 1.2.3 | verify_pdf_ids + verify_completeness: biyección completa |
| NADR-F17BIS-26 §5.3 R12 | DONE | Wave 1.2 / Task 1.2.3 | verify_baseline_materialized + verify_pdf_ids: ausencia impide consumo |
| NADR-F17BIS-26 §5.3 R13 | DONE | Wave 1.2 / Task 1.2.3 | verify_ground_truth_preconditions: GT corrupto → GTUnreadableError |
| NADR-F17BIS-26 §5.3 R14 | DONE | Wave 1.2 / Task 1.2.3 | Pasos 1d y 2b preceden Paso 3 y Paso 4 |
| NADR-F17BIS-26 §5.3 R15 | DONE | Wave 1.2 / Task 1.2.3 | Fail-fast en Pasos 1d y 2b |
| NADR-F17BIS-26 §5.4 R16 | DONE | Wave 1.2 / Task 1.2.4 | Por diseño: funciones de verificación son read-only |
| NADR-F17BIS-26 §5.4 R17 | DONE | Wave 1.2 / Task 1.2.4 | Por diseño: el entorno de verificación no escribe en la baseline |
| NADR-F17BIS-26 §5.4 R18 | DONE | Wave 1.2 / Task 1.2.4 | Detección vía git diff del CI (protección CI en Gate 3) |
| NADR-F17BIS-26 §5.4 R19 | DONE | Wave 1.2 / Task 1.2.4 | Consecuencia de R16-R17: baseline no se modifica durante evaluación |
| NADR-F17BIS-26 §5.5 R20 | DONE | Wave 1.2 / Task 1.2.4 | Separación por diseño: baseline en tests/corpus/canonical/, fixtures en tests/fixtures/ |
| NADR-F17BIS-26 §5.5 R21 | DONE | Wave 1.2 / Task 1.2.4 | Por diseño: directorios separados, fixtures no alteran la baseline |
| NADR-F17BIS-26 §5.5 R22 | DONE | Wave 1.2 / Task 1.2.4 | Por diseño: estructura de directorios distinguible |
| NADR-F17BIS-26 §5.6 R23 | DONE | Wave 1.2 / Task 1.2.4 | BaselineIntegrityError impide consumo; try/except en main() |
| NADR-F17BIS-26 §5.6 R24 | DONE | Wave 1.2 / Task 1.2.4 | BaselineIntegrityError ≠ RegressionError (test de jerarquía) |
| NADR-F17BIS-26 §5.6 R25 | DONE | Wave 1.2 / Task 1.2.4 | EXIT_BASELINE_INTEGRITY_FAILURE = 3 ≠ exit codes de evaluación (0, 1, 2) |
| NADR-F17BIS-26 §5.7 R26 | DONE | Wave 1.2 / Task 1.2.4 | ManifestHashMismatchError (global) vs PdfIntegrityError (individual) |
| NADR-F17BIS-26 §5.7 R27 | DONE | Wave 1.2 / Task 1.2.4 | Cadena de identidad: manifest_hash → document_id → sha256 |
| NADR-F17BIS-26 §5.7 R28 | DONE | Wave 1.2 / Task 1.2.4 | verify_manifest_hash (global) + verify_pdf_hash (individual) |

### 10.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-27 §5.1 R1 | DONE | Wave 2.1 / Task 2.1.1 | VerificationOutcome enum separa operacional de RegressionVerdict |
| NADR-F17BIS-27 §5.1 R2 | DONE | Wave 2.1 / Task 2.1.1 | map_scientific_verdict() requiere precondiciones satisfechas |
| NADR-F17BIS-27 §5.1 R3 | DONE | Wave 2.1 / Task 2.1.1 | Fallo de ejecución no es ausencia de divergencia |
| NADR-F17BIS-27 §5.1 R4 | DONE | Wave 2.1 / Task 2.1.1 | BaselineIntegrityError ≠ RegressionError (Gate 1 Task 1.2.4) |
| NADR-F17BIS-27 §5.1 R5 | DONE | Wave 2.1 / Task 2.1.1 | Divergencia científica ≠ fallo de integridad |
| NADR-F17BIS-27 §5.2 R6 | DONE | Wave 2.1 / Task 2.1.1 | Taxonomía 4 estados: PASS, REGRESSION, BASELINE_INTEGRITY_FAILURE, EXECUTION_FAILURE |
| NADR-F17BIS-27 §5.2 R7 | DONE | Wave 2.1 / Task 2.1.1 | Estados mutuamente distinguibles (test explícito) |
| NADR-F17BIS-27 §5.2 R8 | DONE | Wave 2.1 / Task 2.1.1; Wave 4.2 / Task 4.2.3 | BASELINE_INTEGRITY_FAILURE y EXECUTION_FAILURE no llevan regression_report; verificado end-to-end (clave ausente en JSON) |
| NADR-F17BIS-27 §5.2 R9 | DONE | Wave 2.1 / Task 2.1.1 | EXECUTION_FAILURE no lleva scientific_verdict |
| NADR-F17BIS-27 §5.2 R10 | DONE | Wave 2.1 / Task 2.1.1 | EXECUTION_FAILURE ≠ REGRESSION (enum distinto) |
| NADR-F17BIS-27 §5.3 R11 | DONE | Wave 2.1 / Task 2.1.2 | resolve_operational_outcome: baseline tiene precedencia |
| NADR-F17BIS-27 §5.3 R12 | DONE | Wave 2.1 / Task 2.1.2 | Evaluación completa antes de resultado científico |
| NADR-F17BIS-27 §5.3 R13 | DONE | Wave 2.1 / Task 2.1.2 | Fallo de precondición detiene evaluación (fail-fast) |
| NADR-F17BIS-27 §5.3 R14 | DONE | Wave 2.1 / Task 2.1.2 | Precondiciones de baseline preceden a evaluación (resolve_operational_outcome) |
| NADR-F17BIS-27 §5.3 R15 | DONE | Wave 2.1 / Task 2.1.2 | scientific_verdict=None produce EXECUTION_FAILURE, no PASS |
| NADR-F17BIS-27 §5.4 R16 | DONE | Wave 2.1 / Task 2.1.2 | Conformance/Regression representables independientemente (taxonomía) |
| NADR-F17BIS-27 §5.4 R17 | DONE | Wave 2.1 / Task 2.1.2 | Documentado (gobernanza, no código) |
| NADR-F17BIS-27 §5.4 R18 | DONE | Wave 2.1 / Task 2.1.2 | Documentado (gobernanza, no código) |
| NADR-F17BIS-27 §5.4 R19 | DONE | Wave 2.1 / Task 2.1.2 | Documentado (gobernanza, no código) |
| NADR-F17BIS-27 §5.4 R20 | DONE | Wave 2.1 / Task 2.1.2 | Taxonomía permite representar dimensiones independientemente |
| NADR-F17BIS-27 §5.4 R21 | DONE | Wave 2.1 / Task 2.1.2 | Documentado: REGRESSION=PASS no implica CONFORMANCE=PASS |
| NADR-F17BIS-27 §5.4 R22 | DONE | Wave 2.1 / Task 2.1.2 | Documentado: CONFORMANCE=FAIL no implica REGRESSION=FAIL |
| NADR-F17BIS-27 §5.4 R23 | DONE | Wave 2.1 / Task 2.1.2 | Documentado: recalibración requiere gobernanza explícita |
| NADR-F17BIS-27 §5.5 R24 | DONE | Wave 2.1 / Task 2.1.3 | resolve_operational_outcome preserva precedencia crítica |
| NADR-F17BIS-27 §5.5 R25 | DONE | Wave 2.1 / Task 2.1.3 | HARD_FAIL (exit 2) ≠ EXECUTION_FAILURE (exit 4) |
| NADR-F17BIS-27 §5.5 R26 | DONE | Wave 2.1 / Task 2.1.3 | Métricas conservan políticas (thresholds inmutables) |
| NADR-F17BIS-27 §5.5 R27 | DONE | Wave 2.1 / Task 2.1.3 | No se modifican thresholds silenciosamente |
| NADR-F17BIS-27 §5.5 R28 | DONE | Wave 2.1 / Task 2.1.3 | Recalibración requiere gobernanza explícita |
| NADR-F17BIS-27 §5.6 R29 | DONE | Wave 2.1 / Task 2.1.3 | Exit codes 0-4 deterministas |
| NADR-F17BIS-27 §5.6 R30 | DONE | Wave 2.1 / Task 2.1.3 | Exit codes mutuamente distintos; sin colisión WARNING=1 |
| NADR-F17BIS-27 §5.6 R31 | DONE | Wave 2.1 / Task 2.1.3 | main() preserva distinción en stderr |
| NADR-F17BIS-27 §5.6 R32 | DONE | Wave 2.1 / Task 2.1.3 | sys.exit(result.exit_code) propaga sin reinterpretar |
| NADR-F17BIS-27 §5.6 R33 | DONE | Wave 2.1 / Task 2.1.3 | outcome_to_exit_code() es traducción determinista |
| NADR-F17BIS-27 §5.6 R34 | DONE | Wave 2.1 / Task 2.1.3; Wave 4.2 / Task 4.2.3 (DF-11) | Catch-all except Exception → EXECUTION_FAILURE; DF-11 extendió el except de Pasos 1-2b a OSError+ValueError para que manifest corrupto sea exit 3 con evidencia, no traceback |
| NADR-F17BIS-27 §5.6 R35 | DONE | Wave 2.1 / Task 2.1.2 | scientific_verdict=None ≠ PASS (R15) |
| NADR-F17BIS-28 §5.1 R1 | DONE | Wave 2.2 / Task 2.2.1 | execution_id determinista via build_execution_id() |
| NADR-F17BIS-28 §5.1 R2 | DONE | Wave 2.2 / Task 2.2.2 | baseline_identity persistida en identity_chain |
| NADR-F17BIS-28 §5.1 R3 | DONE | Wave 2.2 / Task 2.2.3 | subject_identity via git SHA con fallback None |
| NADR-F17BIS-28 §5.1 R4 | DONE | Wave 2.2 / Task 2.2.1 | configuration_identity via ConfigurationFingerprintCalculator |
| NADR-F17BIS-28 §5.1 R5 | DONE | Wave 2.2 / Task 2.2.1 | parameter_identity via ParameterIdentityCalculator + FrozenParameters |
| NADR-F17BIS-28 §5.1 R6 | DONE | Wave 2.2 / Task 2.2.1 | build_identity_chain() compone toda la cadena |
| NADR-F17BIS-28 §5.1 R7 | DONE | Wave 2.2 / Task 2.2.1 | limitations observable si falta componente |
| NADR-F17BIS-28 §5.2 R8 | DONE | Wave 2.2 / Task 2.2.1; Wave 3.3 / Task 3.3.3 | execution_id determinista; verificado end-to-end (dos ejecuciones equivalentes → mismo hash) |
| NADR-F17BIS-28 §5.2 R9 | DONE | Wave 2.2 / Task 2.2.1 | Sin información incidental en identidades |
| NADR-F17BIS-28 §5.2 R10 | DONE | Wave 2.2 / Task 2.2.1 | Ejecuciones equivalentes → identidades comparables |
| NADR-F17BIS-28 §5.2 R11 | DONE | Wave 2.2 / Task 2.2.1 | execution_id ≠ baseline_identity (hash distinto) |
| NADR-F17BIS-28 §5.2 R12 | DONE | Wave 2.2 / Task 2.2.1 | baseline_identity ≠ result_identity |
| NADR-F17BIS-28 §5.2 R13 | DONE | Wave 2.2 / Task 2.2.1 | result_identity calculado sobre report+outcome, no sustituye entradas |
| NADR-F17BIS-28 §5.3 R14 | DONE | Wave 2.2 / Task 2.2.2; Wave 3.3 / Task 3.3.1 | ContinuousVerificationReport persiste evidencia completa; verificado end-to-end |
| NADR-F17BIS-28 §5.3 R15 | DONE | Wave 2.2 / Task 2.2.2; Wave 3.3 / Task 3.3.1 | identity_chain en JSON incluye todos los campos; verificado end-to-end |
| NADR-F17BIS-28 §5.3 R16 | DONE | Wave 2.2 / Task 2.2.2; Wave 3.3 / Task 3.3.1 | operational_result con outcome conforme a NADR-27; verificado end-to-end |
| NADR-F17BIS-28 §5.3 R17 | DONE | Wave 2.2 / Task 2.2.2 | configuration_fingerprint serializado (GAP-6.3-02 resuelto) |
| NADR-F17BIS-28 §5.3 R18 | DONE | Wave 2.2 / Task 2.2.3 | Sin información efímera en filename único |
| NADR-F17BIS-28 §5.3 R19 | DONE | Wave 2.2 / Task 2.2.3 | Evidencia completa en disco, no depende de runtime |
| NADR-F17BIS-28 §5.4 R20 | DONE | Wave 2.2 / Task 2.2.3 | Evidencia trazable post-ejecución (filename incluye execution_id) |
| NADR-F17BIS-28 §5.4 R21 | DONE | Wave 2.2 / Task 2.2.3 | Filename único por ejecución, no sobreescribe |
| NADR-F17BIS-28 §5.4 R22 | DONE | Wave 2.2 / Task 2.2.3 | Ejecuciones sucesivas distinguibles por timestamp_shell |
| NADR-F17BIS-28 §5.4 R23 | DONE | Wave 2.2 / Task 2.2.3 | Identity chain inmutable una vez persistida |
| NADR-F17BIS-28 §5.4 R24 | DONE | Wave 2.2 / Task 2.2.2 | schema_version = "cv-1.0.0" permite migraciones futuras |
| NADR-F17BIS-28 §5.5 R25 | DONE | Wave 2.2 / Task 2.2.3 | Condiciones reconstruibles desde evidence |
| NADR-F17BIS-28 §5.5 R26 | DONE | Wave 2.2 / Task 2.2.3 | Reproducibilidad ≠ repetición (identity chain completa) |
| NADR-F17BIS-28 §5.5 R27 | DONE | Wave 2.2 / Task 2.2.3 | baseline_identity permite verificar compatibilidad |
| NADR-F17BIS-28 §5.5 R28 | DONE | Wave 2.2 / Task 2.2.3 | configuration_identity + parameter_identity permiten reproducir |
| NADR-F17BIS-28 §5.5 R29 | DONE | Wave 2.2 / Task 2.2.1 | limitations field observable cuando subject_identity=None |
| NADR-F17BIS-28 §5.5 R30 | DONE | Wave 2.2 / Task 2.2.3 | Coincidencia numérica sin identity chain no es equivalencia |
| NADR-F17BIS-28 §5.6 R31 | DONE | Wave 2.2 / Task 2.2.2 | JSON distingue operational_result de identity_chain |
| NADR-F17BIS-28 §5.6 R32 | DONE | Wave 2.2 / Task 2.2.2 | Evidencia por tipo de outcome (con/sin regression_report) |
| NADR-F17BIS-28 §5.6 R33 | DONE | Wave 2.2 / Task 2.2.2 | Persistencia no modifica significado del outcome |
| NADR-F17BIS-28 §5.6 R34 | DONE | Gate 1 + Wave 2.1 | Ejecución inválida produce EXECUTION_FAILURE, no PASS |

### 10.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-29 §5.1 R1 | DONE | Wave 3.1 / Task 3.1.1 | `VerificationProfile` enum explícitamente definido en bounded context `verification/profiles.py` |
| NADR-F17BIS-29 §5.1 R2 | DONE | Wave 3.1 / Task 3.1.3 | `get_profile_document_ids()` especifica alcance via `frozenset[str]` |
| NADR-F17BIS-29 §5.1 R3 | DONE | Wave 3.1 / Task 3.1.1 | Identifica cobertura de corpus: retorna document_ids del manifest |
| NADR-F17BIS-29 §5.1 R4 | DONE | Wave 3.1 / Task 3.1.3 | Ambos perfiles usan mismo `build_extraction_pipeline()` (NADR-25) |
| NADR-F17BIS-29 §5.1 R5 | DONE | Wave 3.1 / Task 3.1.3 | Ambos perfiles consumen misma baseline canónica (NADR-26) |
| NADR-F17BIS-29 §5.1 R6 | DONE | Wave 3.1 / Task 3.1.3 | Ambos perfiles producen resultados bajo semántica NADR-27 |
| NADR-F17BIS-29 §5.1 R7 | DONE | Wave 3.1 / Task 3.1.3 | Ambos perfiles producen evidencia bajo reglas NADR-28 |
| NADR-F17BIS-29 §5.2 R8 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.2 | `coverage` explícito en `ContinuousVerificationReport`; verificado end-to-end en ejecución real |
| NADR-F17BIS-29 §5.2 R9 | DONE | Wave 3.1 / Task 3.1.2 | SMOKE identificado como cobertura parcial (docstring + enum value) |
| NADR-F17BIS-29 §5.2 R10 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.2 | `coverage` difiere entre FULL y SMOKE; verificado end-to-end (smoke ⊂ full) |
| NADR-F17BIS-29 §5.2 R11 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.3 | Diferencia de cobertura observable; execution_id y profile_identity diferentes entre perfiles |
| NADR-F17BIS-29 §5.2 R12 | DONE | Wave 3.1 / Task 3.1.3 | Mismos thresholds NADR-19 y semántica NADR-27 en ambos perfiles |
| NADR-F17BIS-29 §5.2 R13 | DONE | Wave 3.1 / Task 3.1.3 | Mismas verificaciones de integridad NADR-26 en ambos perfiles |
| NADR-F17BIS-29 §5.3 R14 | DONE | Wave 3.1 / Task 3.1.1; Wave 3.3 / Task 3.3.1 | FULL evalúa todo el `CorpusManifest`; verificado end-to-end (coverage = 21 docs) |
| NADR-F17BIS-29 §5.3 R15 | DONE | Wave 3.1 / Task 3.1.1 | FULL es referencia (valor default de `--profile`) |
| NADR-F17BIS-29 §5.3 R16 | DONE | Wave 3.1 / Task 3.1.2 | SMOKE coexiste con FULL (ambos en enum, no se reemplazan) |
| NADR-F17BIS-29 §5.3 R17 | DONE | Wave 3.1 / Task 3.1.1 | "Completo" definido por cobertura del corpus, no duración ni costo |
| NADR-F17BIS-29 §5.4 R18 | DONE | Wave 3.1 / Task 3.1.2; Wave 3.2 / Task 3.2.1; Wave 3.3 / Task 3.3.2 | SMOKE existe y es ejecutado en PRs; verificado end-to-end (coverage = 5 docs) |
| NADR-F17BIS-29 §5.4 R19 | DONE | Wave 3.1 / Task 3.1.2 | Cobertura limitada declarada en docstring + `SMOKE_DOCUMENT_IDS` |
| NADR-F17BIS-29 §5.4 R20 | DONE | Wave 3.1 / Task 3.1.3 | SMOKE conserva fronteras: mismo entry point, baseline, semántica, evidencia |
| NADR-F17BIS-29 §5.4 R21 | DONE | Wave 3.1 / Task 3.1.3 | SMOKE no sustituye FULL por diseño (FULL en push [main] via workflow separado) |
| NADR-F17BIS-29 §5.4 R22 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.2 | PASS de SMOKE no implica verificación completa; verificado end-to-end |
| NADR-F17BIS-29 §5.4 R23 | DONE | Wave 3.1 / Task 3.1.3 | Fallo en SMOKE conserva semántica NADR-27 (`VerificationOutcome`) |
| NADR-F17BIS-29 §5.5 R24 | DONE | Wave 3.1 / Task 3.1.3 | Ambos perfiles usan mismo `run_regression.py` entry point |
| NADR-F17BIS-29 §5.5 R25 | DONE | Wave 3.1 / Task 3.1.3 | Sin mecanismos paralelos; solo filtrado por perfil |
| NADR-F17BIS-29 §5.5 R26 | DONE | Wave 3.1 / Task 3.1.3 | Diferencias por cobertura, no por mecanismo científico |
| NADR-F17BIS-29 §5.5 R27 | DONE | Wave 3.2 / Task 3.2.1 | Entry point no omitido: CI invoca `run_regression.py` (GAP-6.3-01 resuelto) |
| NADR-F17BIS-29 §5.6 R28 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.3 | `profile_identity` en `IdentityChain`; verificado end-to-end (diferente entre perfiles) |
| NADR-F17BIS-29 §5.6 R29 | DONE | Wave 3.1 / Task 3.1.3 | Perfiles distinguibles en evidencia (profile_identity + coverage) |
| NADR-F17BIS-29 §5.6 R30 | DONE | Wave 3.1 / Task 3.1.3 | Evidencia JSON permite determinar perfil vía `profile_identity` |
| NADR-F17BIS-29 §5.6 R31 | DONE | Wave 3.1 / Task 3.1.3; Wave 3.3 / Task 3.3.3 | Perfiles diferentes producen execution_ids diferentes; verificado end-to-end |
| NADR-F17BIS-29 §5.7 R32 | DONE | Wave 3.2 / Task 3.2.2 | NADR no establece frecuencia; gobernada por triggers del workflow `continuous-verification.yml` |
| NADR-F17BIS-29 §5.7 R33 | DONE | Wave 3.2 / Task 3.2.2 | `workflow_dispatch` permite ejecución manual gobernada |
| NADR-F17BIS-29 §5.7 R34 | DONE | Wave 3.2 / Task 3.2.2 | Triggers no modifican garantías del perfil |
| NADR-F17BIS-29 §5.7 R35 | DONE | Wave 3.2 / Task 3.2.2 | Ejecución por eventos no altera identidad del perfil |

### 10.4 Gate 4 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-30 §5.1 R1-R3 | DONE | Wave 4.1 / Task 4.1.1 | ENFORCEMENT_CONTRACT.md declara required checks, checks informativos y branch protection esperada |
| NADR-F17BIS-30 §5.2 R4-R6 | DONE | Wave 4.1 / Task 4.1.1 | Contrato declara semántica de bloqueo por check y exit codes → estado de check (§5) |
| NADR-F17BIS-30 §5.3 R7-R10 | DONE | Wave 4.1 / Task 4.1.2; Wave 4.2 / Tasks 4.2.2-4.2.3 | Garantizado hoy para `static-analysis` (required); para checks CV, diferido por cláusula 6.1 (DF-09). Paths REGRESSION (exit 2) y FAILURE (exit 3) verificados end-to-end: exit ≠ 0 ⇒ check rojo ⇒ bloquea al ser required |
| NADR-F17BIS-30 §5.4 R11-R13 | DONE | Wave 4.1 / Task 4.1.3; MIG-01 | Branch protection activa sobre `main` con required check; evidencia server-side |
| NADR-F17BIS-30 §5.5 R14-R16 | DONE | Wave 4.1 / Task 4.1.3; MIG-04 | Evidencia server-side obtenida (screenshots de regla y detalle): RESOLVED, no NO DEMOSTRADO |
| NADR-F17BIS-30 §5.6 R17-R19 | DONE | Wave 4.1 / Task 4.1.3 | Configuración verificada activa; efectividad operativa verificada con PR gateado del cierre |
| NADR-F17BIS-30 §5.7 R20-R22 | DONE | Wave 4.1 / Task 4.1.2 | Relación resultado → integración declarada en contrato y verificada por tests; activación de checks CV condicionada y documentada (cláusula 6.1, DF-09) |

---

## 11. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.2.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (implementable / diferido / NAR / limitación)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 12. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase (NADR-F17BIS-25 a NADR-F17BIS-30).
* La **secuencia operativa, tareas concretas y seguimiento de cumplimiento** se rigen por el Execution Plan (`PHASE_17BIS_FASE6_EXECUTION_PLAN.md`).
* Los **hallazgos identificados durante la implementación, su clasificación y resolución** se registran en el Deferred Findings Register (`FASE_6_DEFERRED_FINDINGS_REGISTER.md`).

Este documento **no prescribe implementaciones específicas, planificación operacional, criterios de revisión de código ni registro de hallazgos.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

---

## 13. FUTURE WORK

> - Automatización del Traceability Appendix: considerar un script que derive computacionalmente el estado de las reglas desde el estado de las Tasks.
> - Integración con CI: considerar un check de CI que verifique que el Execution Plan está actualizado conforme al protocolo §14.
> - Métricas de progreso: considerar un dashboard visual que muestre el progreso de la fase en tiempo real.

---

## 14. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 14.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2-§5)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 14.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2-§5)
2. Redactar las **Notas de implementación** de la Task (§{N}.{X}.{Y})
3. Actualizar el `Derived Status` de las reglas implementadas en §10
4. Recalcular los contadores del Status Dashboard (§9)
5. Verificar que las reglas implementadas no aparecen como PENDING en §10

### 14.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§{N}.{X}.{Z})
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 14.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§{N}.4 o §{N}.5)
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§6)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 14.5 Al cancelar una operación de Deployment

1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§7)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§14.3)

### 14.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN (NADR-F17BIS-25 a NADR-F17BIS-30, 167 reglas), no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.