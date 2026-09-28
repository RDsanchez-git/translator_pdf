# PHASE 17-BIS FASE 6 EXECUTION PLAN v1.0.4
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.0.5
**Status:** DRAFT
**Date:** 2026-09-26
**Supersedes:** v1.0.4
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
| 4 | Hallazgos identificados derivados al Findings Register | ✅ DF-05, DF-06, DF-07 |
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
**Gate Status:** ⏳ PENDING

### 3.1 Wave 2.1 — Outcome & Failure Semantics (NADR-F17BIS-27)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Implementar y normalizar la taxonomía de resultados de Continuous Verification. Separar resultado científico de estado operacional. | NADR-F17BIS-27 §5.1 R1-R5; §5.2 R6-R10 | High | Gate 1 | TODO |
| **2.1.2** | Implementar la separación entre scientific verdict y operational/integrity failure. Precedencia de evaluación. Conformance/Regression/Divergence. | NADR-F17BIS-27 §5.3 R11-R15; §5.4 R16-R23 | High | 2.1.1 | TODO |
| **2.1.3** | Normalizar exit-code propagation y precedence. Criticalidad y política de evaluación. | NADR-F17BIS-27 §5.5 R24-R28; §5.6 R29-R35 | High | 2.1.2 | TODO |

#### Notas de implementación — Task 2.1.1

> {Pendiente de implementación}

#### Notas de implementación — Task 2.1.2

> {Pendiente de implementación}

#### Notas de implementación — Task 2.1.3

> {Pendiente de implementación}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 3.2 Wave 2.2 — Evidence, Identity & Reproducibility (NADR-F17BIS-28)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Completar la identity chain de ejecución. Determinismo de identidad. | NADR-F17BIS-28 §5.1 R1-R7; §5.2 R8-R13 | High | 2.1.3 | TODO |
| **2.2.2** | Persistir evidencia determinista con identity chain completa. | NADR-F17BIS-28 §5.3 R14-R19 | Medium | 2.2.1 | TODO |
| **2.2.3** | Validar reproducibilidad y distinguishability histórica. Inmutabilidad y trazabilidad. | NADR-F17BIS-28 §5.4 R20-R24; §5.5 R25-R30; §5.6 R31-R34 | Medium | 2.2.2 | TODO |

#### Notas de implementación — Task 2.2.1

> {Pendiente de implementación}

#### Notas de implementación — Task 2.2.2

> {Pendiente de implementación}

#### Notas de implementación — Task 2.2.3

> {Pendiente de implementación}

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

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §10 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 4. GATE 3 — CONTINUOUS VERIFICATION INTEGRATION

**Objective:** Integrar operacionalmente Continuous Verification en CI: materializar perfiles de ejecución, conectar CI al verification entry point, y validar la integración end-to-end.
**Execution Mode:** Secuencial (Wave 3.1 → 3.2 → 3.3)
**Rollback Plan:** Revertir commits de Wave 3.1, 3.2 y 3.3. El workflow CI anterior se restaura.
**Gate Status:** ⏳ PENDING

### 4.1 Wave 3.1 — Execution Profiles (NADR-F17BIS-29)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Materializar el perfil completo de Continuous Verification (cobertura completa del corpus canónico). | NADR-F17BIS-29 §5.1 R1-R7; §5.3 R14-R17 | Medium | Gate 2 | TODO |
| **3.1.2** | Materializar el perfil reducido / smoke de Continuous Verification (cobertura parcial declarada explícitamente). | NADR-F17BIS-29 §5.4 R18-R23 | Medium | 3.1.1 | TODO |
| **3.1.3** | Validar la semántica de cobertura e identidad de perfiles. Perfiles y mecanismo común. | NADR-F17BIS-29 §5.2 R8-R13; §5.5 R24-R27 | Low | 3.1.2 | TODO |

#### Notas de implementación — Task 3.1.1

> {Pendiente de implementación}

#### Notas de implementación — Task 3.1.2

> {Pendiente de implementación}

#### Notas de implementación — Task 3.1.3

> {Pendiente de implementación}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.2 Wave 3.2 — CI Entry-Point Integration (NADR-F17BIS-25, NADR-F17BIS-27, NADR-F17BIS-29)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Sustituir el selector nominal/empty pytest por la invocation normativa del verification entry point en el workflow CI. | NADR-F17BIS-25 §5.2 R5-R7; NADR-F17BIS-29 §5.7 R32-R35 | Critical | 3.1.3 | TODO |
| **3.2.2** | Conectar CI → CV entry point → production pipeline. Garantizar que la cadena completa está operativa. | NADR-F17BIS-25 §5.1 R1-R4; §5.3 R8-R10 | Critical | 3.2.1 | TODO |
| **3.2.3** | Propagar correctamente el resultado de Continuous Verification al CI. Perfiles y reproducibilidad. | NADR-F17BIS-27 §5.6 R29-R35; NADR-F17BIS-29 §5.6 R28-R31 | High | 3.2.2 | TODO |

#### Notas de implementación — Task 3.2.1

> {Pendiente de implementación}

#### Notas de implementación — Task 3.2.2

> {Pendiente de implementación}

#### Notas de implementación — Task 3.2.3

> {Pendiente de implementación}

#### Notas de referencia cruzada (§1.4)

> Las reglas de NADR-F17BIS-25 §5.1 R1-R4 y §5.2 R5-R7 aparecen en Task 1.1.1, 1.1.2 (implementación) y Task 3.2.1, 3.2.2 (verificación en contexto CI). No hay doble implementación: Task 1.1.x implementa la capacidad, Task 3.2.x verifica que la capacidad está operativa en CI.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.3 Wave 3.3 — Profile & Gate Validation (NADR-F17BIS-25 a NADR-F17BIS-29)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Validar el Full Profile end-to-end: EVENT → CI → PROFILE → ENTRY POINT → PRODUCTION PIPELINE → SEALED BASELINE → EVALUATION → RESULT → EVIDENCE → CI STATUS. | NADR-F17BIS-25 a NADR-F17BIS-29 (verificación transversal) | High | 3.2.3 | TODO |
| **3.3.2** | Validar el Reduced Profile y la cobertura explícita. Verificar que un resultado PASS del perfil reducido no implica cobertura completa. | NADR-F17BIS-29 §5.4 R18-R23 | Medium | 3.3.1 | TODO |
| **3.3.3** | Validar evidencia + resultado + exit semantics por perfil. Verificar que la identity chain permite distinguir perfiles. | NADR-F17BIS-28 §5.1 R1-R7; NADR-F17BIS-27 §5.6 R29-R35 | Medium | 3.3.2 | TODO |

#### Notas de implementación — Task 3.3.1

> {Pendiente de implementación}

#### Notas de implementación — Task 3.3.2

> {Pendiente de implementación}

#### Notas de implementación — Task 3.3.3

> {Pendiente de implementación}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 4.4 Gate 3 Exit Criteria

Todas las reglas de NADR-F17BIS-25 a NADR-F17BIS-29 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:

- El perfil completo está materializado y operativo.
- El perfil reducido / smoke está materializado con cobertura declarada explícitamente.
- CI invoca el verification entry point normativo (no el selector vacío pytest).
- La cadena EVENT → CI → PROFILE → ENTRY POINT → PRODUCTION PIPELINE → SEALED BASELINE → EVALUATION → RESULT → EVIDENCE → CI STATUS está completa y demostrable.
- El resultado de Continuous Verification se propaga correctamente al CI.

### 4.5 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §10 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** —
**Fecha de verificación:** —

---

## 5. GATE 4 — ENFORCEMENT & PHASE CLOSURE

**Objective:** Convertir Continuous Verification en control efectivo de integración (enforcement de merge) y cerrar la fase con cierre operativo completo.
**Execution Mode:** Secuencial (Wave 4.1 → 4.2 → 4.3)
**Rollback Plan:** Revertir commits de Wave 4.1, 4.2 y 4.3. La documentación de enforcement se elimina. La configuración server-side de branch protection debe revertirse manualmente por el administrador del repositorio.
**Gate Status:** ⏳ PENDING

### 5.1 Wave 4.1 — Merge Enforcement (NADR-F17BIS-30)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Declarar el enforcement contract: documentación de Required Checks y branch protection esperada. | NADR-F17BIS-30 §5.1 R1-R3; §5.2 R4-R6; §5.4 R11-R13 | Medium | Gate 3 | TODO |
| **4.1.2** | Verificar la relación resultado → integración. Garantizar que un resultado bloqueante impide la integración. | NADR-F17BIS-30 §5.3 R7-R10; §5.7 R20-R22 | High | 4.1.1, MIG-01 | TODO |
| **4.1.3** | Obtener y registrar evidencia server-side de branch protection. Si no se puede obtener, el estado permanece NO DEMOSTRADO conforme a NADR-F17BIS-30 §5.5 R14. | NADR-F17BIS-30 §5.5 R14-R16; §5.6 R17-R19 | Critical | 4.1.2, MIG-04 | TODO |

#### Notas de implementación — Task 4.1.1

> {Pendiente de implementación}

#### Notas de implementación — Task 4.1.2

> {Pendiente de implementación}

#### Notas de implementación — Task 4.1.3

> {Pendiente de implementación. Si la evidencia externa no se puede obtener, esta Task termina en BLOCKED / NO DEMOSTRADO y se deriva al Findings Register. Gate 4 se cierra como CONDITIONAL PASS con finding derivado.}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 5.2 Wave 4.2 — End-to-End Continuous Verification (NADR-F17BIS-25 a NADR-F17BIS-30)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

**Nota crítica sobre Task 4.2.1 (PASS path):** La existencia de un escenario PASS legítimo es una **precondición verificable**, no una asunción. Con el estado actual de la baseline (Phase 5: 163 Critical FN, NSS 0.7208), una ejecución legítima produce HARD_FAIL conforme a NADR-19 (DoubleProtectionMechanism). Si durante la ejecución no existe un escenario PASS legítimo (sin rutas sintéticas ni fixtures alternativos), la Task queda BLOCKED y se deriva al Findings Register. No se fabrica un PASS para cerrar el gate.

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Validar el PASS path end-to-end: Result PASS → Evidence → CI → Enforcement → Integration allowed. **Precondición:** Debe existir una ejecución legítima del verification subject contra la referencia canónica que produzca PASS sin rutas sintéticas. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Critical | 4.1.3 | TODO |
| **4.2.2** | Validar el REGRESSION / divergence path end-to-end: Result REGRESSION → Evidence → CI → Enforcement → Integration blocked. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.1 | TODO |
| **4.2.3** | Validar el Operational / integrity failure path end-to-end: Result FAILURE → Evidence → CI → Enforcement → Integration blocked. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.2 | TODO |

#### Notas de implementación — Task 4.2.1

> {Pendiente de implementación. Si no existe un escenario PASS legítimo, esta Task queda BLOCKED y se deriva al Findings Register.}

#### Notas de implementación — Task 4.2.2

> {Pendiente de implementación}

#### Notas de implementación — Task 4.2.3

> {Pendiente de implementación}

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| — | — | — |

### 5.3 Wave 4.3 — Final Verification & Exit Review (Todos los NADRs)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Full corpus Continuous Verification: ejecutar el perfil completo contra el corpus canónico sellado y verificar el resultado en sus dimensiones (Conformance, Regression si el perfil lo incluye, Operational integrity). | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Medium | 4.2.3 | TODO |
| **4.3.2** | Static analysis + complete test suite + import-linter. Verificar que no hay regresiones en el código existente. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Low | 4.3.1 | TODO |
| **4.3.3** | Exit Review Evidence / traceability closure. Verificar que todas las reglas están DONE en §10 y que la trazabilidad está completa. | NADR-F17BIS-25 a NADR-F17BIS-30 (verificación transversal) | Low | 4.3.2 | TODO |

#### Notas de implementación — Task 4.3.1

> {Pendiente de implementación}

#### Notas de implementación — Task 4.3.2

> {Pendiente de implementación}

#### Notas de implementación — Task 4.3.3

> {Pendiente de implementación}

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

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE o BLOCKED con finding derivado | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §10 o documentadas como NO DEMOSTRADO | ⏳ |
| 3 | Gate Exit Criteria satisfechos (o documentados como parcialmente satisfechos) | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** {PASS / CONDITIONAL PASS / FAIL}
**Fecha de verificación:** —

---

## 6. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-09-26 | 41/41 | 7/7 | 3 (DF-05, DF-06, DF-07) | Verification Foundation — PASS |
| Gate 2 | — | 0/69 | 0/6 | 0 | Verification Contract |
| Gate 3 | — | 0/35 | 0/9 | 0 | Continuous Verification Integration |
| Gate 4 | — | 0/22 | 0/9 | 0 | Enforcement & Phase Closure |
| **TOTAL** | — | **41/167** | **7/31** | **3** | — |

---

## 7. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Configurar branch protection en GitHub: requerir job `regression-gates` como Required Status Check en rama `main`. | GitHub (server-side) | NADR-F17BIS-30 §5.4 R11-R13 | Screenshot / API response | TODO |
| **MIG-02** | Configurar mecanismo de materialización de PDFs del corpus canónico en CI (artifact repository, object storage, o self-hosted runner). | CI | NADR-F17BIS-26 §5.1 R1-R5 | Workflow CI actualizado | TODO |
| **MIG-03** | Actualizar workflow CI para invocar el verification entry point normativo en lugar del selector vacío pytest. | CI | NADR-F17BIS-25 §5.2 R5-R7 | Workflow CI actualizado | TODO |
| **MIG-04** | Verificar que la configuración de branch protection está activa y es efectiva. | GitHub (server-side) | NADR-F17BIS-30 §5.5 R14-R16 | Evidencia externa | TODO |

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
| Gate 2 | 0 | 0 | 0 | 69 | ⏳ PENDING |
| Gate 3 | 0 | 0 | 0 | 35 | ⏳ PENDING |
| Gate 4 | 0 | 0 | 0 | 22 | ⏳ PENDING |
| **TOTAL** | **7** | **41** | **0** | **126** | 🟡 IN PROGRESS |

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
| NADR-F17BIS-25 §5.2 R5 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local DONE; verificación CI pendiente en Task 3.2.1 |
| NADR-F17BIS-25 §5.2 R6 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local DONE; verificación CI pendiente en Task 3.2.1 |
| NADR-F17BIS-25 §5.2 R7 | DONE | Wave 1.1 / Task 1.1.2; Wave 3.2 / Task 3.2.1 | Implementación local DONE; verificación CI pendiente en Task 3.2.1 |
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
| NADR-F17BIS-26 §5.1 R5 | DONE | Wave 1.2 / Task 1.2.4 | Separación baseline/fixtures por diseño; protección CI pendiente en Gate 3 |
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
| NADR-F17BIS-27 §5.1 R1-R5 | PENDING | Wave 2.1 / Task 2.1.1 | — |
| NADR-F17BIS-27 §5.2 R6-R10 | PENDING | Wave 2.1 / Task 2.1.1 | — |
| NADR-F17BIS-27 §5.3 R11-R15 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-F17BIS-27 §5.4 R16-R23 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-F17BIS-27 §5.5 R24-R28 | PENDING | Wave 2.1 / Task 2.1.3 | — |
| NADR-F17BIS-27 §5.6 R29-R35 | PENDING | Wave 2.1 / Task 2.1.3; Wave 3.2 / Task 3.2.3; Wave 3.3 / Task 3.3.3 | — |
| NADR-F17BIS-28 §5.1 R1-R7 | PENDING | Wave 2.2 / Task 2.2.1; Wave 3.3 / Task 3.3.3 | — |
| NADR-F17BIS-28 §5.2 R8-R13 | PENDING | Wave 2.2 / Task 2.2.1 | — |
| NADR-F17BIS-28 §5.3 R14-R19 | PENDING | Wave 2.2 / Task 2.2.2 | — |
| NADR-F17BIS-28 §5.4 R20-R24 | PENDING | Wave 2.2 / Task 2.2.3 | — |
| NADR-F17BIS-28 §5.5 R25-R30 | PENDING | Wave 2.2 / Task 2.2.3 | — |
| NADR-F17BIS-28 §5.6 R31-R34 | PENDING | Wave 2.2 / Task 2.2.3 | — |

### 10.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-29 §5.1 R1-R7 | PENDING | Wave 3.1 / Task 3.1.1 | — |
| NADR-F17BIS-29 §5.2 R8-R13 | PENDING | Wave 3.1 / Task 3.1.3 | — |
| NADR-F17BIS-29 §5.3 R14-R17 | PENDING | Wave 3.1 / Task 3.1.1 | — |
| NADR-F17BIS-29 §5.4 R18-R23 | PENDING | Wave 3.1 / Task 3.1.2; Wave 3.3 / Task 3.3.2 | — |
| NADR-F17BIS-29 §5.5 R24-R27 | PENDING | Wave 3.1 / Task 3.1.3 | — |
| NADR-F17BIS-29 §5.6 R28-R31 | PENDING | Wave 3.2 / Task 3.2.3 | — |
| NADR-F17BIS-29 §5.7 R32-R35 | PENDING | Wave 3.2 / Task 3.2.1 | — |

### 10.4 Gate 4 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-F17BIS-30 §5.1 R1-R3 | PENDING | Wave 4.1 / Task 4.1.1 | — |
| NADR-F17BIS-30 §5.2 R4-R6 | PENDING | Wave 4.1 / Task 4.1.1 | — |
| NADR-F17BIS-30 §5.3 R7-R10 | PENDING | Wave 4.1 / Task 4.1.2 | — |
| NADR-F17BIS-30 §5.4 R11-R13 | PENDING | Wave 4.1 / Task 4.1.1; MIG-01 | — |
| NADR-F17BIS-30 §5.5 R14-R16 | PENDING | Wave 4.1 / Task 4.1.3; MIG-04 | — |
| NADR-F17BIS-30 §5.6 R17-R19 | PENDING | Wave 4.1 / Task 4.1.3 | — |
| NADR-F17BIS-30 §5.7 R20-R22 | PENDING | Wave 4.1 / Task 4.1.2 | — |

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