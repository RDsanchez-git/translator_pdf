# FASE_6_HANDOFF.md — Continuous Verification → Transición a Fase 18

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_6_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN (al merge del PR de cierre)
**Fecha:** 2026-09-30
**Fase completada:** Fase 6 — Continuous Verification (Phase 17-BIS)
**Siguiente fase:** Fase 18 — Advanced Local Runtime (ROADMAP_ARQUITECTONICO_LP v3.0)
**Derivado de:** `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.11 + `FASE_6_DEFERRED_FINDINGS_REGISTER.md` v0.10.0

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-30 | Emisión inicial al cierre de Fase 6 (Gate 4 CONDITIONAL PASS) |

---

## 1. EXECUTIVE SUMMARY

**¿Qué se logró?** Fase 6 (Continuous Verification) quedó COMPLETED con veredicto
de Gate 4 CONDITIONAL PASS: 167/167 reglas de los 6 NADRs FROZEN (NADR-F17BIS-25 a
30) en estado DONE, 30/31 tasks (Task 4.2.1 BLOCKED → DF-10). Se construyó un
control de verificación continua que ejecuta el pipeline productivo real contra
la baseline canónica sellada, con taxonomía inequívoca de resultados (exit codes
0-4), evidencia persistida con identity chain completa y determinista, perfiles
de ejecución FULL/SMOKE, integración en CI y branch protection activa sobre
`main` con required check de static analysis.

**¿Cuál es el estado actual?** Suite completa 930 passed / 5 skipped (baseline no
degradada), pyright 0 errors, import-linter 4/4 KEPT. 210 tests nuevos de Fase 6
(13 e2e de perfiles, 6 e2e de regression path, 6 de failure path, 12 de contrato
de enforcement, resto unit/integration). 8 hallazgos analizados: 5 RESOLVED
(DF-01, DF-05, DF-07, DF-08, DF-11), 1 ACCEPTED_LIMITATION (DF-09), 2
RECLASSIFIED_FUTURE_PHASE (DF-06, DF-10), 0 NAR, 0 GFs. El estado basal del
extractor produce HARD_FAIL legítimo (NSS 0.7208 < 0.80, 163 Critical FN) en FULL
y SMOKE: es el veredicto científico correcto (NADR-19 DoubleProtectionMechanism),
no un defecto del control.

**¿Qué necesita la siguiente fase?** Respetar las restricciones carry-forward de
§5.1 (thresholds congelados, biyección del corpus, baseline inmutable, exit codes
sin reinterpretar, flujo rama→PR por required checks). No hay prerequisitos
bloqueantes para Fase 18: el control de verificación está operativo y puede usarse
como red de seguridad para cualquier refactor de runtime. Si Fase 18 toca la
composición del benchmark, resolver DF-06 en esa misma tarea (sinergia natural).

> **Regla:** Este bloque es lo único que un humano necesita leer para entender dónde está
> el proyecto. Si alguien solo lee esta sección, debe poder decidir si continuar o no.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` (protegida: required check "Static Analysis (pyright + import-linter)") |
| Commit hash de cierre | `403a0735a084264df47a6aae12847e484417c5a3` (anterior en main: `8734e8b`, Gate 3) |
| Estado del árbol | Limpio al freeze (todo el cierre entra en un commit atómico vía rama → PR) |
| Baseline de tests | **930 passed, 5 skipped** (no debe degradarse sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** (scope: core, apps, infra, runtime) |
| Imports huérfanos | 0 (import-linter 4/4 KEPT; 1 `ignore_import` documentado para DF-06) |
| Branch protection | Activa sobre `main` (evidencia en `reports/evidence/branch-protection-main.png` y `-detail.png`) |

### 2.2 Validation Results

```bash
python -m pytest tests/unit/ tests/integration/ -q --tb=short
    # 930 passed, 5 skipped, 0 collection errors ✅
python -m pytest tests/integration/test_cv_profile_validation.py tests/integration/test_cv_regression_path.py -m e2e -v
    # 19 passed (13 perfiles + 6 regression path) ✅
pyright core/ apps/ infra/ runtime/
    # 0 errors, 0 warnings ✅
lint-imports --config pyproject.toml
    # 4 kept, 0 broken, exit 0 ✅
python -m tools.evaluation.run_regression --corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf --output-dir reports/full-check --profile FULL
    # exit 2 (HARD_FAIL basal esperado y documentado: DF-10) ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro | FROZEN | n/a (constitución de Phase 17-BIS) |
| ADR de Fase (ADR_F17_BIS_06) | FROZEN | v1.2.0 |
| NADRs (6 documentos: NADR-F17BIS-25 a 30) | FROZEN | 167 reglas |
| Execution Plan | FROZEN al merge | v1.0.11 |
| Evidence Log | FROZEN al merge | v0.8.0 |
| Findings Register | ARCHIVED al merge | v0.10.0 |
| Methodology | FROZEN | v1.3.0 |
| Guía de Documentación de Arquitectura | FROZEN | v1.0.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 8 |
| Hallazgos resueltos | 5 |
| Hallazgos cerrados sin acción (NAR) | 0 |
| Hallazgos diferidos a fase futura | 2 (DF-06, DF-10) + 1 ACCEPTED_LIMITATION activo (DF-09) |
| Batches ejecutados | 0 (implementación por waves, sin batches de findings) |
| Archivos eliminados | 0 |
| Archivos movidos | 1 (`doc_06_johnstone.pdf` → `tests/corpus/archive/`, DF-08) |
| Archivos creados | 30 (25 de Gates 1-3 + 5 de Gate 4: enforcement_contract, helpers/cv_execution, 3 tests nuevos) |
| Archivos modificados | 17 (incluye fixes de translation tests y pyproject.toml) |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | Bounded context `core/benchmark/verification/` separado de `topology/regression/` | NADR-27/28 (operacional) vs NADR-19/23 (científico) no debían mezclarse | Separación de resultados científicos y operacionales | `core/benchmark/verification/{outcome,identity_chain,report,profiles}.py` |
| AD-02 | Entry point normativo único `tools/evaluation/run_regression.py` invocando `build_extraction_pipeline()` | Riesgo de rutas de verificación paralelas o sintéticas | NADR-25 §5.1-§5.4 | Test AST `test_verification_boundary.py`; contrato import-linter 4 |
| AD-03 | `execution_id` = hash determinista de inputs (baseline+subject+config+params+profile), sin UUID | Reproducibilidad y distinguibilidad de perfiles | NADR-28 §5.2 R8; NADR-29 §5.6 R31 | `identity_chain.build_execution_id()`; tests e2e de determinismo |
| AD-04 | Evidencia con filename único por ejecución; sin `latest.json` | Evitar sobrescritura de evidencia histórica | NADR-28 §5.4 R21 | `run_regression._build_report_filename()`; `test_cv_report_persistence.py` |
| AD-05 | Perfiles FULL/SMOKE con mismo mecanismo y diferente cobertura; SMOKE = lista hardcoded de 5 docs auditada | Criterio por traits producía solo 2 docs calificantes | NADR-29 §5.1-§5.5 | `verification/profiles.py`; auditoría forense del corpus |
| AD-06 | CI invoca el entry point real (`python -m tools.evaluation.run_regression`); workflow separado `continuous-verification.yml` para FULL | GAP-6.3-01: CI ejecutaba `pytest -m regression` (0 tests) | NADR-25 §5.2 R5-R7; NADR-29 §5.7 | `.github/workflows/ci.yml`, `continuous-verification.yml`; `test_cv_workflow_contract.py` |
| AD-07 | Opción B transicional de enforcement: `static-analysis` required; checks CV informativos con cláusula de activación 6.1; classic rule (no ruleset) | Rojo basal permanente sería teatro de enforcement; ruleset rompería push directo por chicken-and-egg | NADR-30 §5.1-§5.7; ENGINEERING_PRINCIPLES §IV | `plans/FASE_6_ENFORCEMENT_CONTRACT.md`; branch protection activa |
| AD-08 | No fabricar PASS: Task 4.2.1 BLOCKED → DF-10 | Estado basal HARD_FAIL legítimo (NSS 0.7208) | Execution Plan §5.2; NADR-26 §5.5 R20-R22 | Ejecuciones FULL/SMOKE exit 2; Findings Register §2.4 |
| AD-09 | DF-11 resuelto en Gate 4, no diferido | Regla NADR-27 §5.6 R34 marcada DONE no podía tener contraejemplo vivo al closure | NADR-27 §5.6 R34; NADR-28 §5.3 R14 | `run_regression.py` except Pasos 1-2b extendido; `TestCorruptManifestPath` |
| AD-10 | PDF orphan movido a `tests/corpus/archive/`, no eliminado | Biyección manifest↔PDFs rota sin tocar baseline sellada | NADR-26 §5.3 R11-R12 | `tests/corpus/archive/README.md`; manifest_hash invariante |
| AD-11 | Fix de imports `helpers.*` → `tests.helpers.*` en 3 tests de Fase 16, en vez de excluirlos de la suite | Collection rota por deuda preexistente; excluir tests es burocracia | ENGINEERING_PRINCIPLES (tests vivos) | `tests/integration/test_translation_*.py` |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Verification boundary sobre production pipeline (sin rutas paralelas) | NADR-F17BIS-25 | ✅ DONE |
| Baseline canónica materializable, íntegra y completa (hashes, biyección, precondiciones) | NADR-F17BIS-26 | ✅ DONE |
| Taxonomía de outcomes y exit codes inequívocos (0-4) con precedencia | NADR-F17BIS-27 | ✅ DONE |
| Evidence persistida con identity chain completa, determinista y reproducible | NADR-F17BIS-28 | ✅ DONE |
| Perfiles de ejecución FULL/SMOKE con cobertura e identidad distinguibles | NADR-F17BIS-29 | ✅ DONE |
| Enforcement de merge documentado y activo para static analysis; CV diferido condicionalmente | NADR-F17BIS-30 | ⚠️ PARTIAL (DF-09) |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `core/benchmark/verification/{__init__,outcome,identity_chain,report,profiles}.py` — bounded context de verificación operacional
- `core/benchmark/corpus/integrity.py` — verificación pura de integridad de baseline
- `tests/helpers/cv_execution.py` — SSOT de invocación CV vía subprocess
- `tests/unit/test_{verification_boundary,verification_outcome,identity_chain,verification_report,subject_identity,verification_profiles,cv_workflow_contract,enforcement_contract}.py`
- `tests/integration/test_{verification_pipeline_connection,baseline_materialization,baseline_physical_integrity,baseline_pdf_completeness,baseline_gt_preconditions,baseline_integrity_exit_code,execution_failure_exit_code,cv_report_persistence,regression_entry_point,cv_profile_validation,cv_regression_path,cv_failure_path}.py`
- `.github/workflows/continuous-verification.yml`
- `plans/FASE_6_ENFORCEMENT_CONTRACT.md`
- `handoff/FASE_6_HANDOFF.md` (este documento)
- `tests/corpus/archive/README.md`
- `reports/evidence/branch-protection-{main,main-detail}.png` (+ `branch-protection-pr-gate.png` al merge)

**Modificados significativamente:**
- `tools/evaluation/run_regression.py` — exit codes normativos, identity chain, coverage, `--profile`, except DF-11
- `.github/workflows/ci.yml` — job `regression-gates` invoca entry point real (SMOKE)
- `pyproject.toml` — marker `e2e`, contrato import-linter 4, excludes de pyright
- `core/benchmark/topology/regression/report.py` — serializadores públicos reutilizados
- `tests/integration/test_translation_{semantics,structure,technical}.py` — fix de imports

**Eliminados (zombies y deuda):**
- Ninguno. (Deuda movida, no eliminada: `doc_06_johnstone.pdf` → `tests/corpus/archive/`.)

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para siguiente fase |
|-------------|--------|-------------------------------|
| Thresholds de regresión congelados (NSS ≥ 0.80, 0 Critical FN); recalibración solo vía gobernanza DC-6.6 | ADR_F17_BIS_MASTER DC-6.6; NADR-19 | Fase 18 no puede "arreglar" el gate tocando thresholds |
| No fabricar PASS ni usar fixtures como baseline | NADR-26 §5.5 R20-R22 | Cualquier demo de PASS debe ser ejecución legítima contra corpus sellado |
| Biyección manifest↔PDFs y baseline sellada inmutable (manifest_hash `727782fe...19f7d`, v3.9, 21 docs) | NADR-26 §5.3 R11-R12 | Agregar/quitar PDFs de `canonical/pdf/` rompe toda ejecución con exit 3 |
| Exit codes propagan sin reinterpretar; wrapper WARNING→0 prohibido | NADR-27 §5.6 R32 | CI y scripts de Fase 18 deben respetar la semántica 0-4 |
| Commits nuevos entran a `main` vía rama → PR → merge (required checks activos) | Branch protection 2026-09-30; ENFORCEMENT_CONTRACT §4.2 | El flujo de trabajo de Fase 18 es PR-based |
| Checks CV (`regression-gates`, `cv-full-profile`) informativos hasta cláusula 6.1 | ENFORCEMENT_CONTRACT §6.1; DF-09 | No asumir que una regresión estructural bloquea merge hoy |
| `ignore_import` documentado para cadena `core.benchmark.__main__ → apps` | DF-06; contrato import-linter 3 | Si Fase 18 refactoriza composición del benchmark, eliminar el ignore en esa tarea |
| Evidencia con filename único; sin `latest.json` | NADR-28 §5.4 R21 | Herramientas de Fase 18 que consuman evidencia deben parsear por identity chain |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| DF-06 | `core.benchmark.__main__` importa `apps/` (cadena transitiva a fitz) | Fase futura no faseada (refactor de composición del benchmark); sinergia con Fase 18 si toca runtime | Nada operativo (mitigado con ignore_import documentado) |
| DF-09 | Enforcement de merge de CV diferido: checks CV informativos hasta cláusula 6.1/6.3 | Activación condicionada dentro de Fase 6+ (basal PASS o DC-6.6); migración a PRs+ruleset opcional | Promoción de checks CV a required |
| DF-10 | PASS path no demostrable: estado basal HARD_FAIL (NSS 0.7208, 163 Critical FN) | Fase futura no faseada de mejora de fidelidad de extracción, o recalibración gobernada DC-6.6 | Cierre completo del enforcement (CONDITIONAL PASS de Gate 4) |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| Rojo basal de checks CV | `regression-gates` y `cv-full-profile` están en rojo permanente (HARD_FAIL basal); una regresión nueva no se distingue por color de check | Distinguir por artifact de evidencia (NSS, verdict, coverage en el JSON); cláusula 6.1 define cuándo el rojo pasa a bloqueante |
| 5 skips por precondiciones | GROQ_API_KEY ausente; golden fingerprint y 3 moldes de traducción no generados | Skips documentados y estables; no cuentan como degradación de baseline |
| Pyright no cubre tests/tools en escaneo global | Política de include acotada a core/apps/infra/runtime; tests/tools se chequean por CLI/editor | Excludes explícitos en `pyproject.toml`; CI usa paths explícitos |
| GitHub Free plan solo enforcea repos públicos | Si el repo se privatiza, la branch protection deja de enforcear | Repo público al cierre; verificar si cambia de visibilidad |
| `subject_identity` puede ser None sin git | Limitación observable en identity chain | Campo `limitations` del reporte lo declara (NADR-28 §5.5 R29) |
| Eliminación accidental de archive/ | `doc_06_johnstone.pdf` en archive/ podría perderse en limpiezas futuras | README.md en archive/ documenta el archivo; no es crítico pero pierde trazabilidad |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Entry point CV operativo con perfiles FULL/SMOKE y exit codes normativos
- ✅ Baseline canónica sellada e íntegra (21 docs, manifest v3.9)
- ✅ CI con checks CV y static analysis; branch protection activa
- ✅ Pipeline de evidencia con identity chain y artifacts en CI (`if: always()`)
- ✅ Suite de 930 tests como red de regresión para cualquier refactor de runtime

**Lo que se necesita antes de arrancar:**
- Nada bloqueante. Opcional: decidir si DF-06 se resuelve dentro del scope de Fase 18 (recomendado si se refactoriza composición del benchmark).

### 6.2 Next Phase Handoff Checklist

- [ ] Cargar este handoff + documentos de Prioridad 1 (§8.4)
- [ ] Verificar baseline: `python -m pytest tests/unit/ tests/integration/ -q` → 930 passed, 5 skipped
- [ ] Confirmar branch protection activa y flujo rama→PR antes del primer commit
- [ ] No modificar thresholds ni `FrozenParameters` sin gobernanza DC-6.6
- [ ] Si se toca `core/benchmark/__main__.py`: resolver DF-06 y eliminar el `ignore_import` del contrato 3
- [ ] Si se elide `SyncProviderBridge` (objetivo de Fase 18): verificar que ningún test e2e de CV dependa del bridge; la invocación CV es subprocess sobre el entry point, no sobre providers
- [ ] Si el estado basal pasa a PASS: ejecutar cláusula 6.1 del ENFORCEMENT_CONTRACT (promover checks CV) y cerrar DF-09/DF-10
- [ ] Mantener biyección del corpus al agregar documentos (re-sellado vía `SealGroundTruthUseCase` con gobernanza)

### 6.3 ROADMAP — Objetivos de la siguiente fase (Fase 18 — Advanced Local Runtime)

1. **Asincronía pura top-to-bottom** — Elisión de `SyncProviderBridge` (`apps/llm_workers/sync_bridge.py`)
2. **Memory Efficiency** — Object pools, buffers zero-copy y lazy loading
3. **Pipeline Backpressure** — Prevención de Out-Of-Memory en procesamiento masivo
4. **Adaptive Batching & Scheduling** — Agrupación dinámica de chunks según presupuesto (8k, 32k, 1M)
5. **Cache Multinivel** — Memoria → SQLite → Semantic/Embedding Cache

**Hito crítico (texto del ROADMAP v3.0):** "Al concluir esta fase, el Traductor PDF
se considera funcionalmente completo para el procesamiento de documentos científicos reales."
*(Detalle completo: `ROADMAP_ARQUITECTONICO_LP.md` §IV, Fase 18.)*

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| ADR de Fase 18 | `docs/architecture/3_METH_ADR_PHASES.md` | Constitución y capacidades de Advanced Local Runtime |
| NADRs de Fase 18 | `docs/architecture/4_METH_NADR.md` | Reglas técnicas inmutables (asincronía, memoria, backpressure) |
| Execution Plan Fase 18 | `docs/architecture/5_METH_EXECUTION_PLAN.md` | Gates/waves/tasks y trazabilidad de reglas |
| Findings Register + Evidence Log Fase 18 | `docs/architecture/6_METH_*.md` | Ciclo de vida de hallazgos y evidencia forense |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro Phase 17-BIS | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` |
| ADR de Fase 6 | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_06.md` (v1.2.0) |
| NADRs Fase 6 (6 docs, 167 reglas) | `docs/architecture/adr/phase-17-bis/NADR/` (NADR-F17BIS-25 a 30) |
| Methodology | `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` (v1.3.0) |
| Guía de Documentación de Arquitectura | `docs/architecture/` (v1.0.0, FROZEN) |
| ENGINEERING_PRINCIPLES | `docs/architecture/` (FROZEN) |
| ROADMAP | `docs/architecture/roadmap/ROADMAP_ARQUITECTONICO_LP.md` (v3.0) |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register Fase 6 | `docs/architecture/adr/phase-17-bis/reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md` (v0.10.0) |
| Evidence Log Fase 6 | `docs/architecture/adr/phase-17-bis/reviews/FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md` (v0.8.0) |
| Este handoff | `docs/architecture/adr/phase-17-bis/handoff/FASE_6_HANDOFF.md` (v1.0.0) |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| Execution Plan Fase 6 | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE6_EXECUTION_PLAN.md` (v1.0.11) | Trazabilidad task→regla y notas de implementación |
| Enforcement Contract | `docs/architecture/adr/phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md` | Required checks, cláusulas de activación, alternativas rechazadas |
| Evidencia server-side | `docs/architecture/adr/phase-17-bis/reports/evidence/` | Screenshots MIG-01/MIG-04 y gate de PR |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: Traductor PDF científico/técnico
Descripción: Pipeline que extrae AST estructural de PDFs y lo traduce preservando layout y semántica
Stack: Python 3.11, pydantic v2, PyMuPDF (fitz), pytest, hypothesis, pyright, import-linter, GitHub Actions
Arquitectura: DDD + Hexagonal; Functional Core / Imperative Shell; inmutabilidad; fail-fast; determinismo; FinOps First
Fase actual completada: Fase 6 — Continuous Verification (Gate 4 CONDITIONAL PASS)
Siguiente fase: Fase 18 — Advanced Local Runtime
```

### 8.2 Code State

```text
Tests: 930 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings (scope core/apps/infra/runtime)
Import-linter: 4/4 KEPT
Rama: main (protegida; required check "Static Analysis (pyright + import-linter)")
Flujo: commits nuevos vía rama → PR → merge (push directo de commits sin checks es rechazado)
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. No fabricar PASS ni recalibrar thresholds sin gobernanza DC-6.6 (estado basal: HARD_FAIL, NSS 0.7208)
2. Baseline sellada inmutable: manifest v3.9, 21 docs, hash 727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d
3. Biyección manifest↔PDFs obligatoria: tocar canonical/pdf/ sin re-sellar rompe todo con exit 3
4. Exit codes 0-4 propagan sin reinterpretar; wrapper WARNING→0 prohibido (NADR-27 §5.6 R32)
5. Checks CV informativos hasta cláusula 6.1 del ENFORCEMENT_CONTRACT (DF-09)
6. Evidencia con filename único; sin latest.json; identity chain completa en todo reporte
7. Entry point CV único: python -m tools.evaluation.run_regression (nada de rutas paralelas)
8. ignore_import documentado para core.benchmark.__main__ → apps (DF-06); eliminarlo si se refactoriza composición
9. Tests que fallan por deuda se arreglan con fix mínimo, nunca se excluyen de la suite
10. Gobernanza en 3 docs sincronizados (Execution Plan / Findings Register / Evidence Log) + handoff al cierre
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- FASE_6_HANDOFF.md (este documento)
- ENGINEERING_PRINCIPLES.md
- ROADMAP_ARQUITECTONICO_LP.md

Prioridad 2 (cargar para implementación):
- PHASE_17BIS_FASE6_EXECUTION_PLAN.md (v1.0.11)
- FASE_6_ENFORCEMENT_CONTRACT.md
- FASE_6_DEFERRED_FINDINGS_REGISTER.md (v0.10.0)

Prioridad 3 (consultar según necesidad):
- FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md (v0.8.0)
- NADR-F17BIS-25 a 30 (regla específica citada en cada tarea)
- ADR_F17_BIS_MASTER.md (DoD, DC-6.6, jerarquía normativa)
```

### 8.5 Pending Items (carry-forward)

```text
[DF-06] core.benchmark.__main__ importa apps/ (cadena transitiva a fitz)
       → Destino: fase futura no faseada (sinergia con Fase 18 si toca composición)
       → Bloquea: nada operativo (ignore_import documentado)
       → Opciones: inyección de dependencias o puerto de extracción

[DF-09] Checks CV informativos (enforcement de merge diferido)
       → Destino: cláusula 6.1/6.3 del ENFORCEMENT_CONTRACT
       → Bloquea: promoción de regression-gates/cv-full-profile a required
       → Opciones: basal PASS (mejora de extractor) o recalibración DC-6.6; migrar a PRs+ruleset

[DF-10] PASS path no demostrable (HARD_FAIL basal legítimo)
       → Destino: mejora de fidelidad de extracción (fase futura) o DC-6.6
       → Bloquea: cierre completo del enforcement (Gate 4 CONDITIONAL PASS)
       → Opciones: mejorar extractor (doble columna, tablas anidadas, math, figuras)
```

### 8.6 Work Conventions

```text
- Commits atómicos por gate/wave con mensaje estructurado (feat/fix/docs + refs a NADR y DF)
- Análisis forense antes de implementar: evidencia → invariantes → riesgos → decisión
- Tests e2e con marker @pytest.mark.e2e (lentos, bajo demanda); failure paths en suite estándar
- Invocación CV en tests vía subprocess (tests/helpers/cv_execution.py): reproduce lo que ve CI
- Ubicaciones según Guía de Documentación: plans/ (contratos y planes), reviews/ (findings y evidencia forense), reports/ (métricas y evidencia de CI), handoff/ (transición)
- NO DEMOSTRADO no es DONE; BLOCKED se deriva al Findings Register con destino explícito
```

### 8.7 System Entry Points

```text
tools/evaluation/run_regression.py            → Entry point normativo de Continuous Verification (--profile FULL|SMOKE, exit codes 0-4)
apps/bootstrap/pipeline_factory.py            → build_extraction_pipeline(): composition root del pipeline de extracción
apps/bootstrap/provider_factory.py            → ExtracciónProviderFactory: construcción de providers (infra)
core/benchmark/__main__.py                    → CLI de benchmark (con deuda DF-06: importa apps/)
apps/llm_workers/sync_bridge.py               → SyncProviderBridge: objetivo de elisión en Fase 18
.github/workflows/ci.yml                      → static-analysis (required), regression-gates SMOKE, unit, integration
.github/workflows/continuous-verification.yml → cv-full-profile (push main + workflow_dispatch)
```

Composition root: `apps/bootstrap/pipeline_factory.build_extraction_pipeline()` es el único
punto de construcción del pipeline; el entry point CV lo invoca directamente (NADR-25).
No crear factories paralelas.

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
- [x] SHA de cierre completado en §2.1 (al merge del PR)

**Veredicto:** 🟡 EN PROGRESO — pasa a ✅ CERRADO — FROZEN al merge del PR `gate-4-closure` y completar el SHA en §2.1.

---

**Nota de Gobernanza:** Este documento es el punto de transición entre fases.
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado
exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que
cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4)
para tener contexto completo de arranque. Los detalles normativos se consultan bajo
demanda según la tarea específica.