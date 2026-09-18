# FASE 5 BENCHMARK METHODOLOGY

**Documento:** `docs/architecture/adr/phase-17-bis/FASE_5_BENCHMARK_METHODOLOGY.md`
**Versión:** 1.1.0
**Estado:** IN_PROGRESS (Batch 1 cerrado; §7 pendiente)
**Última actualización:** 2026-09-18
**Derivado de:** `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.3.5 (vigente en repo; living document)

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-14 | Emisión pasada 1 (§1-§6 + §7 placeholder + §8 guardrails). |
| 1.0.1 | 2026-09-14 | Correcciones de revisión: (1) §3.3/§3.4 gate de curaduría marcado como objetivo Batch 1, no comportamiento vigente; (2) §4.3 tabla de veredictos alineada con DoubleProtectionMechanism (precedencia CRITICAL); (3) §4.4 renombrado a invariantes de completitud (DoubleProtection real vive en §4.3); (4) §2.4 desglose tracked/transient de reports/; (5) §2.1 evidencia de tools = commit 0ae448f, main_corpus = Batch 2 pendiente; (6) §3.2 estado actual de códigos CANON-*/FREEZE-GT-001; (7) §3.5 lineage por documento; (8) header referenciado a Plan v1.3.5; (9) §6.4 wording de tipos de nodo alineado al Register; (10) §5.1 añade experiment_identity y result_identity. |
| 1.1.0 | 2026-09-15 | **Cierre documental de Batch 1 (H-5.5-7 RESOLVED, commit <SHA-BATCH-1>):** el gate de curaduría pasa de objetivo a comportamiento vigente. (1) §3.3 paso 6 y §3.4 actualizados a comportamiento vigente; (2) §3.2 con códigos reales FREEZE-GT-001, FREEZE-GT-002 y FREEZE-W01; (3) nota explícita: el override --allow-uncurated cubre AMBOS códigos (GT-001 y GT-002) por igualdad con el precedente D2; (4) ruta del checklist derivada de --corpus-dir (`<corpus-dir>/curation_checklist.json`), sin literal hardcodeado (patrón GAP-5.0-03); (5) §2.1 evidencia de freeze_ground_truth.py actualizada; (6) §3.5 tabla de artefactos corregida (fila ground_truth malformada). Baseline: 729 passed / 5 skipped (724 + 5 tests del gate); pyright 0/0. |
| 1.1.1 | 2026-09-15 | **Re-scope de Batch 2 (Register v0.21.0):** Batch 2a = `curate_gt.py` (escritor de `curation_checklist.json`) + hardening `CANON-*` en `canonicalize_gt.py`, antes del primer onboarding; Batch 2b = orquestador `main_corpus` diferido (trigger: ≥2 onboardings post-2a o error de secuenciación). Deltas: §2.1 (fila `main_corpus` → diferido; nueva fila `curate_gt.py`), §3.2 (`CANON-*` objetivo→reales tras hardening de 2a), §3.3 paso 5 (registro vía `curate_gt.py` desde 2a). Gobernanza: `curation_checklist.json` no es artefacto de baseline (va a `.gitignore`); el registro durable de la curaduría es el Curation Report. |
| 1.1.2 | 2026-09-15 | **Batch 2a implementado:** códigos `CANON-001/002/003/004/005` reales en `canonicalize_gt.py`; `CURATE-001/002/003/004` + `CURATE-W01` reales en `curate_gt.py`. §2.1: nueva fila `curate_gt.py` como entry point de Categoría A (Batch 2a). §3.2: `CANON-*` y `CURATE-*` pasan de objetivo a reales. |
| 1.1.3 | 2026-09-15 | **Alineación §3.2 con códigos reales de Batch 2a (commit `c4bb03b`):** (1) tabla de §3.2 actualizada con códigos reales implementados: CANON-001 (4 casos), CANON-002/003/OK, CURATE-001/002/003/004 y CURATE-W01; (2) eliminación de CANON-004/005 que el changelog 1.1.2 afirmaba pero no existen en código; (3) corrección de §6.5 GF-03 (herramienta real = `curate_gt.py`, no `main_corpus curate`); (4) §3.3 paso 4 con códigos reales de Gate; (5) notas obsoletas reemplazadas por estado vigente; (6) §2.4 H-5.5-8 actualizado a "remediado"; (7) §3.4 con SHA real de Batch 1 (`9cbddf8`); (8) header con fecha única. |

> **Este documento NO es:**
> - Una enmienda a NADRs/ADRs (no redefine reglas)
> - Un Execution Plan (no define Tasks ni Gates)
> - Un Findings Register (no registra hallazgos ni decisiones)
> - Un documento de gobernanza normativa
>
> **Este documento SÍ es:**
> - La spec operacional del benchmark de certificación
> - El runbook ejecutable de onboarding y evaluación
> - El inventario consolidado de assets (sirve / confinado / muerto / ruido)
> - La referencia única para interpretar veredictos de regresión

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_05 > NADR-F17BIS-20..24 > PHASE_17BIS_FASE5_EXECUTION_PLAN > FASE_5_BENCHMARK_METHODOLOGY
```

> *"No lower governance level is authorized to redefine or contradict decisions established by an upper level."*

Este documento es **operacional, no normativo**. No redefine reglas; las cita y las opera.

### 0.2 Principio rector del benchmark

> *"¿La ejecución del benchmark produce una representación determinista, reproducible y arquitectónicamente fiel del pipeline productivo que vamos a certificar?"*

Sub-preguntas aplicables:

- ¿El corpus sellado es biyectivo ($N_{PDF} = N_{GT}$)?
- ¿Los oráculos son inmutables post-sealing?
- ¿El run de regresión es determinista (mismas condiciones → mismo resultado)?
- ¿Los veredictos (PASS/WARNING/HARD_FAIL) son interpretables científicamente?
- ¿Las identidades (corpus, manifest, parameter, configuration) están desacopladas y trazables?

### 0.3 Reglas transversales aplicables

- **Zero Partial Sealing** — `ADR_F17_BIS_MASTER §5`: Un corpus NO podrá entrar en estado `SEALED` si no existe una correspondencia biyectiva completa entre los PDFs declarados y sus oráculos AST auditados ($N_{PDF} = N_{GT}$).
- **Determinismo y Reproducibilidad** — `ADR_F17_BIS_MASTER §5`: Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser determinista.
- **Desacoplamiento de Identidades** — `ADR_F17_BIS_MASTER §5`: La arquitectura debe mantener diferenciados los conceptos de AST Schema Version, Corpus Version, Identity Hash, Oracle Hash, Baseline Hash, Parameter Identity y Evaluation Configuration Identity.
- **Cero Fallos Silenciosos** — `ENGINEERING_PRINCIPLES §IV`: Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un warning indexable explícito o fallar duro.
- **Trazabilidad Absoluta** — `ENGINEERING_PRINCIPLES §IV`: El linaje del dato debe propagarse intacto a través de todas las transformaciones del pipeline.
- **Inmutabilidad de Sealed** — `NADR-F17BIS-21 §5.4 R19`, `NADR-F17BIS-24 §5.6 R25`: Un Ground Truth en estado `SEALED` no debe modificarse, sobrescribirse ni eliminarse. No existe rollback mutativo post-sealing.
- **Calibration ≠ Evaluation** — `NADR-F17BIS-23 §5.1 R2`: Los resultados de FINAL EVALUATION no deben participar en la selección, ajuste o justificación de parámetros.

### 0.4 No-supersión

Este documento **no reemplaza**:

- **NADRs/ADRs**: la autoridad normativa vive en `ADR_F17_BIS_MASTER.md` y los NADRs congelados (NADR-20..24).
- **Execution Plan**: la secuencia de Tasks y Gates vive en `PHASE_17BIS_FASE5_EXECUTION_PLAN.md`.
- **Findings Register**: el registro de hallazgos y decisiones vive en `FASE_5_DEFERRED_FINDINGS_REGISTER.md`.
- **Task 5.2.1**: el runner de certificación de Gate 5 (que traduce taxonomía NADR-19 a NADR-24) es propiedad exclusiva de esa Task; este documento no lo implementa ni lo duplica.

Este documento hace **cross-references** a esos artefactos sin duplicar contabilidad de reglas (§1.4 del Plan prohíbe matrices paralelas).

---

## 1. PROPÓSITO Y ALCANCE

### 1.1 Qué ES este documento

- La **spec operacional** del benchmark de certificación de Fase 5.
- El **runbook ejecutable** de onboarding (ingesta de nuevos documentos al corpus canónico) y evaluación (regresión topológica contra oráculos sellados).
- El **inventario consolidado** de assets del repo: qué sirve, qué está confinado, qué está muerto, qué es ruido.
- La **referencia única** para interpretar veredictos de regresión (PASS/WARNING/HARD_FAIL) y sus limitaciones.

### 1.2 Qué NO ES este documento

- No es un documento de gobernanza normativa (no redefine NADRs/ADRs).
- No es un Execution Plan (no define Tasks ni Gates).
- No es un Findings Register (no registra hallazgos ni decisiones).
- No es el runner de certificación de Gate 5 (eso es Task 5.2.1, propiedad exclusiva de ese gate).

### 1.3 Split de taxonomías (GF-01)

El proyecto usa **dos taxonomías de exit codes** en scopes distintos:

| Scope | Taxonomía | Exit codes | Fuente |
|-------|-----------|------------|--------|
| `run_regression.py` (compuerta CI) | NADR-19 §5.5 R22 | 0 = PASS, 1 = WARNING, 2 = HARD_FAIL | NADR-19 |
| Runner de certificación Gate 5 (Task 5.2.1) | NADR-24 §5.4 R15-R17 | 0 = éxito, 1 = rechazo científico, 2 = fallo de ejecución | NADR-24 |

**Regla:** `run_regression.py` conserva taxonomía NADR-19 como compuerta CI; el runner de certificación de Gate 5 traduce veredictos científicos a categorías (a)/(b) y crashes a (c). Este documento opera `run_regression.py` con taxonomía NADR-19; la traducción a NADR-24 es responsabilidad de Task 5.2.1.

### 1.4 Cross-references (sin duplicación)

| Concepto | Referencia normativa | Referencia operacional (este doc) |
|----------|----------------------|-----------------------------------|
| Zero Partial Sealing | ADR_F17_BIS_MASTER §5 | §3 Runbook de onboarding (paso 8: freeze) |
| Determinismo | ADR_F17_BIS_MASTER §5 | §4 Runbook de evaluación (preflight + run) |
| Identidades desacopladas | ADR_F17_BIS_MASTER §5 | §5 Identidades y provenance |
| Cero Fallos Silenciosos | ENGINEERING_PRINCIPLES §IV | §3.5 check_candidate + §6 Limitaciones |
| Inmutabilidad de Sealed | NADR-21 §5.4 R19, NADR-24 §5.6 R25 | §3 paso 8 (freeze) + §5 cascada al sellar |
| Calibration ≠ Evaluation | NADR-23 §5.1 R2 | §4 (regla anti-tautología) |

---

## 2. INVENTARIO CONSOLIDADO DE ASSETS

### 2.1 Categoría A — Operacionales (lo único que necesitás para operar el benchmark)

#### Entry points CLI (Imperative Shell)

| Script | Rol | Evidencia |
|--------|-----|-----------|
| `tools/evaluation/generate_golden_draft.py` | Genera drafts de GT para documentos nuevos (skips idempotentes en sellados) | Wave 4.2 T4.2.2/4.2.3 — corazón del onboarding |
| `tools/evaluation/freeze_ground_truth.py` | Sellado atómico (MIG-06, Zero Partial Sealing) + gate de curaduría como precondición | Wave 2.2 T2.2.1 + Batch 1 (H-5.5-7, commit 9cbddf893d69ba1c157044c9ede1054794465073) |
| `tools/evaluation/run_regression.py` | Runner de regresión contra oráculos sellados (taxonomía NADR-19, GF-01) | Wave 2.4 T2.4.5 |
| `tools/evaluation/preflight_certification.py` | PREFLIGHT antes de cualquier RUN | Wave 4.1 T4.1.2 |
| `tools/evaluation/freeze_parameters.py` | Parameter freeze + provenance records; soporta `--evaluation-kind FINAL_EVALUATION` para Gate 5 | Wave 3.3 T3.3.2/3.3.3 |
| `tools/evaluation/sanitize_ground_truth_types.py` | Migración/corrección de GTs con protección de sellado (fuera del run certificante) | Wave 2.1 T2.1.2, Wave 4.3 T4.3.2 |
| `tools/evaluation/bootstrap_corpus.py` | ⚠️ Solo bootstrap inicial del manifest (Wave 1.2). **PROHIBIDO para añadir documentos**: reconstruye desde cero y destruye entradas selladas | Wave 1.2 T1.2.3 |
| `tools/evaluation/curate_gt.py` | Escritor de `curation_checklist.json` (schema `{status, report_ref, curated_at}` congelado por el lector de Batch 1); rechaza curar sellados (`[CURATE-003]`, NADR-21 §5.1 R5); serialización determinista excluida de identidad | **Batch 2a** (pre-onboarding); contrato congelado por el lector |
| `main_corpus` (verbos admit/draft/canonicalize/curate/seal/regress) | Orquestador delgado de onboarding/evaluación | **Batch 2b (DIFERIDO por YAGNI)**; trigger: ≥2 onboardings post-2a o error de secuenciación operacional; no es entry point existente |

**Regla:** Para añadir documentos y correr el benchmark tocás únicamente los entry points de Categoría A. Todo lo demás es confinado, muerto o ruido.

#### Dominio e infra consumidos por esos entry points (no se tocan, se reutilizan)

| Módulo | Rol |
|--------|-----|
| `core/benchmark/certification/*` (contract, preflight, evidence, post_run) | Functional Core de certificación (Wave 4.1-4.3) |
| `core/benchmark/corpus/*`, `core/benchmark/ground_truth/*`, `core/benchmark/topology/regression/*` | Contratos de corpus, oráculos y regresión |
| `core/shared/exit_codes.py`, `core/shared/errors.py`, `tools/evaluation/entry_guard.py` | Taxonomía de salida y guard R19 (Wave 4.2) |
| `bootstrap/topology.py` | Composition root canónico (`build_canonical_engine_configuration`) |
| `infra/fs/corpus_repository.py`, `infra/fs/ground_truth_store.py`, `infra/serialization/ast_json.py`, `infra/adapters/document_metadata.py`, `infra/adapters/pdf_parser.py`, `apps/bootstrap/pipeline_factory.py`, `infra/benchmarks/adapters/ground_truth_parser_adapter.py` | Puertos/adaptadores de I/O y extracción (NADR-19 R20: `build_extraction_pipeline()` es factoría única) |

### 2.2 Categoría B — Confinado/experimental (NO ruta canónica)

| Script/Módulo | Razón |
|---------------|-------|
| `tools/evaluation/topology/metrics/structural.py` (APTED) | DF-04: experimental no-normativo (divergencia 8.56%) |
| `tools/evaluation/topology/fingerprint.py` | H-5.2-6: `.strip()` confinado (viola NADR-22 R10-R12, pero solo en tooling experimental) |
| `tools/evaluation/run_df04_benchmark.py` | Runner del comparativo DF-04 (evidencia ya en `reports/df04/`); cierre administrativo en Gate 5 T5.3.3 |
| `tools/evaluation/run_benchmark.py` + `application/benchmark_service.py` + `topology/metrics/{node_count,recall,sequence}.py` | Benchmark topológico de Fase 17, no regresión de certificación |
| `tools/evaluation/generate_candidates.py` | Wave 4.1: fuera de scope con justificación (tooling no certificante) |
| `tools/evaluation/generate_pymupdf_candidate.py` | Ruta legacy de candidatos a `calibration_v1/candidates/`; el onboarding v2.0 usa `generate_golden_draft` |

### 2.3 Categoría C — Muerto con disposición (higiene Paso 1, 2026-09-14)

| Archivo/Directorio | Disposición | Evidencia |
|--------------------|-------------|-----------|
| `tools/codemods/*` | ELIMINADO (tracked; historia en git) | Commit `8cfac09` |
| `tools/load_test/*` | ELIMINADO (tracked; historia en git) | Commit `8cfac09` |
| `tools/evaluation/run_experimental_benchmark.py` | ELIMINADO (tracked; historia en git) | Commit `8cfac09` |
| `graveyard/gemini_client.py` | ELIMINADO (tracked; historia en git) | Commit `8cfac09` |
| `generate_p1_graph.py` … `generate_p7_graph.py` | ELIMINADO (untracked+ignored; irreversible por decisión de ownership) | Commit `8cfac09` |
| `tools/benchmark_archive/*` | ELIMINADO (untracked+ignored; irreversible por decisión de ownership) | Commit `8cfac09` |

### 2.4 Categoría D — Ruido de desarrollo (ignorado por `.gitignore`)

| Archivo/Directorio | Razón |
|--------------------|-------|
| `generate_workspace.py` | Dev tooling activo (regenera `ARCHITECTURE_WORKSPACE.md`); local ignorado |
| `extraer_benchmark.py` | Dev tooling activo (consolida 8 fuentes del pipeline en `auditoria_bloque_ampliado.txt`); local ignorado |
| `ARCHITECTURE_WORKSPACE.md`, `PROJECT_TREE.txt`, `P1..P7_PRODUCTION_PIPELINE_GRAPH.md` | Snapshots regenerables; local ignorado |
| `auditoria_*.txt`, `baseline.txt`, `etapa_*.txt`, `pyright_report.*`, `resultados_pytest_*.txt` | Artefactos de proceso; local ignorado |
| `reports/calibration/`, `reports/df04/`, `reports/sanity_validation/` | **EVIDENCIA DE GOBERNANZA — trackeada desde commit `8dbae5a` (remediación H-5.5-8 completada):** `parameter_freeze.json`, calibration/evaluation provenance records, benchmark DF-04, regresión sanity. El test de enforcement R24 lee `parameter_freeze.json` del working tree; ahora está trackeado, un clone fresco reproduce la verificación. `reports/regression/` y salidas transientes permanecen ignorados.| Salidas transientes de `run_regression` y artefactos de proceso bajo `reports/` | Local ignorado (`.gitignore:99 reports/`); `reports/regression/` permanece ignorado tras la remediación. |
| `docs/architecture/adr/phase-17-bis/handoff/` | Handoffs operacionales; local ignorado (commit `f748fd7`) |

### 2.5 Regla práctica

**Si no está en Categoría A, no lo necesitás para añadir documentos ni correr la regresión de certificación.** Categoría B es confinado (no toca certificación); Categoría C está eliminado; Categoría D es ruido local.

---

## 3. RUNBOOK DE ONBOARDING

### 3.1 Política de autocorrección por clase de fallo

| Clase de fallo | Ejemplo | Acción |
|----------------|---------|--------|
| Identidad/estructural, función pura del input | node_ids legacy | **Auto-corrige con linaje** (`canonicalize_gt.py`) + log indexable |
| Admisión física | Type 3 sin ToUnicode, sin text layer, page_count ≠ esperado, SHA duplicado | **Aborta** (`CHECK-CAND-*` / `ADD-DOC-*`); humano re-trimea o descarta |
| Semántico/contenido | heading degradado, tabla como paragraph, spans CS | **Aborta en gate de curaduría**; humano cura (R5) |
| Estado/gobernanza | sellar sin entrada `CURATED`, regression sin `SEALED` | **Aborta** con código indexable; humano completa el paso upstream |

**Principio:** Solo se autocorrige lo que es función pura del input y deja artefacto de linaje; todo lo demás aborta. Cada código indexado lleva una línea `remediation:` que apunta al paso del runbook que lo resuelve.

### 3.2 Tabla código → paso del runbook (mapa de remediation)

| Código indexado | Paso del runbook | Acción humana |
|-----------------|------------------|---------------|
| `CHECK-CAND-001` (Type 3 sin ToUnicode) | 1 | Re-trimear PDF o descartar documento |
| `CHECK-CAND-002` (sin text layer) | 1 | Ejecutar OCR o descartar |
| `CHECK-CAND-003` (page_count ≠ esperado) | 1 | Verificar PDF fuente |
| `ADD-DOC-001` (trait inválido) | 2 | Corregir trait en manifest |
| `ADD-DOC-005` (SHA duplicado) | 2 | Verificar que no sea dup real |
| `CANON-001` (manifest no resoluble, doc ausente, GT ausente o GT ilegible) | 4 | Abortar (exit 2); remediation: verificar `--corpus-dir` o ejecutar pasos 2/3 del runbook |
| `CANON-002` (colisión de node_ids post-canonicalización) | 4 | Abortar (exit 2); remediation: curaduría manual del draft (paso 5) |
| `CANON-003` (documento sellado) | 4 | Abortar (exit 2); remediation: nueva versión de artefacto (Rollback Plan Gate 2) |
| `CANON-OK` (legacy detectado, sin código de aborto) | 4 | Auto-corregido con lineage por `canonicalize_gt.py`; sin legacy = no-op idempotente (R33) |
| `CURATE-001` (manifest no resoluble o doc ausente) | 5 | Abortar (exit 2); remediation: verificar `--corpus-dir` o ejecutar paso 2 |
| `CURATE-002` (checklist corrupto o ilegible) | 5 | Abortar (exit 2); remediation: reconstruir checklist desde Curation Report o eliminar archivo corrupto |
| `CURATE-003` (documento sellado) | 5 | Abortar (exit 2); remediation: curaduría es pre-sellado (NADR-21 §5.1 R5); nueva versión de artefacto si aplica |
| `CURATE-004` (`--report-ref` vacío con `--status CURATED`) | 5 | Abortar (exit 2); remediation: pasar `--report-ref` con la sección del Curation Report |
| `CURATE-W01` (`--report-ref` provisto con `--status PENDING`) | 5 | Warning indexable; `report_ref` se ignora (solo existe al curar) |
| `FREEZE-GT-001` (checklist ausente o ilegible con drafts pendientes) | 6 | Crear `curation_checklist.json` vía `curate_gt.py` (Batch 2a) o registrar la curaduría manualmente |
| `FREEZE-GT-002` (draft sin entrada, con status ≠ CURATED, o sin report_ref) | 6 | Registrar curaduría con `status=CURATED` y `report_ref` al Curation Report |
| `FREEZE-W01` (override `--allow-uncurated` activo) | — | Warning indexable; el sellado continúa (solo fuera de ejecución certificante). Cubre AMBOS códigos GT-001 y GT-002. |

> **Estado vigente (v1.1.2):** Todos los códigos de esta tabla están implementados. `FREEZE-GT-001/002` y `FREEZE-W01` desde Batch 1 (commit `9cbddf8`). `CANON-001/002/003/004/005` desde Batch 2a en `canonicalize_gt.py`. `CURATE-001/002/003/004` y `CURATE-W01` desde Batch 2a en `curate_gt.py`. Ninguna fila debe leerse como "especificación objetivo"; todas son comportamiento vigente.

### 3.3 Pasos del runbook

| Paso | Acción | Script/Tool | Gate |
|------|--------|-------------|------|
| 1 | Check de admisión (Type 3, ToUnicode, text layer, page_count) | `check_candidate.py` | `CHECK-CAND-*` → exit 2 si falla |
| 2 | Alta en manifest (traits válidos, sin dup de doc_id/SHA, bump de versión) | `add_document_to_corpus.py` | `ADD-DOC-*` → exit 2 si falla |
| 3 | Generación de draft de GT | `generate_golden_draft.py` | Skips idempotentes en sellados |
| 4 | Canonicalización de node_ids | `canonicalize_gt.py` | `CANON-OK` → auto-corrección con linaje; `CANON-001/002/003` → exit 2 si falla |
| 5 | **Curaduría manual** (humano) | VS Code / editor + `curate_gt.py` | Registro en `curation_checklist.json` con `report_ref` al Curation Report: edición manual aceptable hasta Batch 2a; desde 2a, vía `curate_gt.py` (`[CURATE-*]` → exit 2 si falla) |
| 6 | Sellado atómico | `freeze_ground_truth.py` | Gate de curaduría vigente (Batch 1): todo doc con `ground_truth_state=None` exige entrada `CURATED` con `report_ref` en `<corpus-dir>/curation_checklist.json`; aborta con `FREEZE-GT-001/002` (exit 2) salvo override `--allow-uncurated` (`FREEZE-W01`) |
| 7 | Gobernanza (actualizar Register, Execution Plan, provenance) | Edit manual | Cross-refs a hallazgos derivados |

### 3.4 Gate de curaduría (operacional, no normativo)

> **Estado: COMPORTAMIENTO VIGENTE desde Batch 1 (H-5.5-7 RESOLVED, commit `9cbddf893d69ba1c157044c9ede1054794465073`, 2026-09-15).**

**Precondición de sellado:** `freeze_ground_truth.py` verifica que todo documento con `ground_truth_state=None` tenga una entrada `CURATED` en `<corpus-dir>/curation_checklist.json` con `report_ref` al Curation Report. El gate solo se evalúa si hay drafts pendientes: un corpus totalmente sellado sin checklist es no-op con exit 0 (idempotencia MIG-06, R33).

**Códigos indexables:**
- `FREEZE-GT-001`: checklist ausente o ilegible con drafts pendientes → exit 2 con línea `remediation:`.
- `FREEZE-GT-002`: draft sin entrada, con `status ≠ CURATED`, o con `report_ref` vacío → exit 2 con línea `remediation:`.
- `FREEZE-W01`: override `--allow-uncurated` activo → warning indexable listando los doc_ids; el sellado continúa. Válido solo fuera de ejecución certificante (patrón D2/R26). El override cubre AMBOS códigos (GT-001 y GT-002).

**Limitación:** Este gate es **operacional** (vive en el Imperative Shell de `freeze_ground_truth.py`), no **normativo** (no vive en `SealGroundTruthUseCase` del dominio). Cualquier código que invoque directamente el use case de sellado puede eludir el gate; el enforcement normativo (O3: check en la autoridad de sellado, dominio) está diferido a Fase 6 (H-5.5-5).

**Override:** `--allow-uncurated` con warning indexable fuera de ejecución certificante (patrón D2/R26). Uso legítimo: re-sellado de corpus completo tras re-baseline v3.0.

### 3.5 Artefactos de onboarding

| Artefacto | Ruta | Propósito |
|-----------|------|-----------|
| `curation_checklist.json` | `<corpus-dir>/curation_checklist.json` (derivado de `--corpus-dir`; raíz canonical/, **no** `ground_truth/`, lección H-5.2-3) | Registro de curaduría humana con `report_ref` al Curation Report. Schema congelado: `{"<doc_id>": {"status": "PENDING"\|"CURATED", "report_ref": str\|null, "curated_at": str\|null}}` |
| `manifest.json` | `<corpus-dir>/manifest.json` | Manifest canónico con oracle_hash y ground_truth_state |
| `canonicalization_lineage.json` (por documento) | `<corpus-dir>/{doc_id}_canonicalization_lineage.json` | Linaje de canonicalización por documento (doc_08/09/10). Nota: Wave 1.3 usó un único `canonicalization_lineage.json` en raíz (formato histórico, H-5.2-3); el onboarding vigente emite lineage por documento. |
| `ground_truth/*.json` | `<corpus-dir>/ground_truth/` | Oráculos AST V2 sellados |

---

## 4. RUNBOOK DE EVALUACIÓN

### 4.1 Secuencia de evaluación

| Paso | Acción | Script/Tool | Gate |
|------|--------|-------------|------|
| 1 | PREFLIGHT (verificación de completitud de baseline) | `preflight_certification.py` | Fail-fast si falta evidencia |
| 2 | Regresión topológica contra oráculos sellados | `run_regression.py` | Taxonomía NADR-19 (0=PASS, 1=WARNING, 2=HARD_FAIL) |
| 3 | Interpretación de veredictos | Humano | §4.2 Regla de tautología + §6 Limitaciones |

### 4.2 Regla de tautología

**NSS=1.0000 con estructuras degradadas = no-informativo, no éxito.**

Si un documento tiene NSS=1.0000 pero el GT contiene estructuras degradadas (tablas como paragraphs, ecuaciones fragmentadas, labels de gráficos como texto plano), el PASS es **tautológico**: el extractor se comparó contra sí mismo, no contra una curaduría independiente. Ejemplos:

- **doc_07_pesaran** (H-5.3-3): GT no editado en curaduría; fuentes Type 3 sin ToUnicode; tablas visibles no extraídas.
- **doc_09_vanhaverbeke** (H-5.5-2): sellado sin curaduría previa; NSS=1.0 tautológico.
- **doc_10_gross** (H-5.5-2): sellado sin curaduría previa; NSS=1.0 tautológico.

**Acción:** Marcar como no-informativo para validación; curaduría real diferida a re-baseline v3.0 (corpus ≥20 identidades).

### 4.3 Interpretación de veredictos (DoubleProtectionMechanism, worst-wins)

El `DoubleProtectionMechanism` del dominio (`core/benchmark/topology/regression/mechanism.py`) combina dos mecanismos complementarios: **Mecanismo 1** = umbrales NSS; **Mecanismo 2** = pérdida de criticidad. Rige el peor de los dos (worst-wins), y el Mecanismo 2 es independiente del NSS y del conteo.

| Veredicto | Condición |
|-----------|-----------|
| PASS | 0 Critical FN **y** warning_loss < `warning_threshold` **y** NSS ≥ 0.95 |
| WARNING | 0 Critical FN **y** (warning_loss ≥ `warning_threshold` **ó** 0.80 ≤ NSS < 0.95) |
| HARD_FAIL | Critical FN ≥ 1 (Mecanismo 2, sin importar NSS ni cantidad) **ó** NSS < 0.80 (Mecanismo 1) |

**Notas:**
- 1 Critical FN en 1000 nodos ⇒ HARD_FAIL (`test_canonical_1_critical_in_1000`); no existe "tolerancia" de Critical FN.
- `warning_threshold` default = 1, configurable vía `CriticalityVerdictEmitter`.
- Invariante de thresholds: 0.0 ≤ `nss_hard_fail` < `nss_warning` ≤ 1.0 (`RegressionThresholds.__post_init__` fail-fast).
- Los thresholds (0.80/0.95) son defaults NORMATIVOS, no calibrados empíricamente (H-5.3-1); recalibración pendiente para corpus ≥20.

### 4.4 Invariantes de completitud y post-validación (no confundir con DoubleProtectionMechanism)

El `DoubleProtectionMechanism` (NSS + criticidad) se describe en §4.3. Esta sección cubre dos invariantes de otra naturaleza (completitud y post-condiciones de certificación):

1. **Zero Partial Sealing** (ADR_F17_BIS_MASTER §5): invariante PRE-sellado; el corpus no entra en `SEALED` si $N_{PDF} \neq N_{GT}$.
2. **POST-RUN VALIDATION** (NADR-24 §5.8 R36-R37): `validate_post_run` verifica 5 post-condiciones (provenance verifiable, per-document present, aggregate present, evidence elements, identity consistency) con violaciones nombradas por elemento R29.

---

## 5. IDENTIDADES Y PROVENANCE

### 5.1 Identidades desacopladas (ADR_F17_BIS_MASTER §5)

| Identidad | Definición | Cuándo cambia |
|-----------|------------|---------------|
| **AST Schema Version** | Versión del esquema AST V2 | Cambio de schema (raro) |
| **Corpus Version** | Versión del corpus canónico | Añadir/eliminar documentos |
| **Identity Hash** | SHA-256 del contenido del documento | Cambio de PDF fuente |
| **Oracle Hash** | SHA-256 del oráculo AST sellado | Cambio de GT (prohibido post-sealing) |
| **Baseline Hash** | SHA-256 del manifest canónico | Cambio de manifest |
| **Parameter Identity** | Fingerprint de parámetros de evaluación (thresholds, pesos) | Cambio de parámetros (NADR-23 §5.6) |
| **Configuration Identity** | Fingerprint de configuración de evaluación (motor, normalización, matching) | Cambio de configuración (NADR-22 §5.6 R19-R21) |
| **Experiment Identity** | Identidad del experimento de evaluación (trazabilidad R31) | Por emisión de Evaluation Provenance Record |
| **Result Identity** | SHA-256 del reporte de evaluación (trazabilidad dura) | Por reporte emitido |

### 5.2 Crosswalk GF-02: corpus_identity vs manifest_identity

| Concepto | NADR-23 §5.5 R18 | NADR-24 §5.7 R29 + NADR-20 |
|----------|------------------|---------------------------|
| **corpus_identity** | SHA-256 del manifest | Compuesto de contenido (SHA-256 de SHA-256 ordenados, estable entre sellados) |
| **manifest_identity** | (no definido) | `manifest_hash` (cambia al sellar) |

**Resolución:** Artefactos de Wave 3.3 permanecen válidos (su `corpus_identity` per R18 = `manifest_identity` en NADR-24); crosswalk documenta el mapeo entre diccionarios.

### 5.3 Cascada de identidades al sellar

Cuando se sella un nuevo documento:

1. **Nuevo `manifest_hash`** (SHA-256 del manifest actualizado).
2. **Nueva `manifest_identity`** (cambia).
3. **`corpus_identity`** (compuesto de contenido) puede cambiar si el documento nuevo añade contenido único.
4. **Provenance v1.0 queda histórico**; nueva provenance se materializa con `evaluation_kind=FINAL_EVALUATION`.
5. **`parameter_identity` NO se toca** (cambio de corpus no implica cambio de parámetros).

### 5.4 Gap de observabilidad (H-5.5-6)

**El extractor no tiene fingerprint propio.** Cambios en `build_extraction_pipeline()` (provider, normalización, matching) no mueven `configuration_fingerprint` (NADR-22 §5.6 cubre solo el motor de evaluación). Detección post-hoc vía delta de veredictos de regresión y deltas de `manifest_identity`/`oracle_identity`. Remediación (fingerprint de extractor/pipeline como identidad nueva) diferida a Fase 6.

---

## 6. LIMITACIONES CONOCIDAS

### 6.1 Limitaciones del extractor (PyMuPDFProvider)

| Hallazgo | Descripción | Impacto |
|----------|-------------|---------|
| H-5.1-9 | doc_02_double: 52 nodos `display_equation` con fragmentos garbled (operadores/variables aislados). PyMuPDF no agrupa tokens matemáticos en layout de doble columna. | GT fiel al extractor, no al documento fuente. |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos vectoriales extraídos como `paragraph` individuales. Estructura del gráfico no capturada. | Comportamiento esperado de PyMuPDF frente a gráficos vectoriales. |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Fuera del scope de Fase 17-BIS (ADR §4). | Diferido a Fase 18 (Advanced Local Runtime) o fase dedicada de mejora de extracción. |
| H-5.3-2 | Divergencia masiva entre runtime de producción y GTs curados: 5/6 documentos HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536. Confirma problema estructural del extractor, no paramétrico. | Refuerza decisión de no calibrar con N=6. |

### 6.2 Limitaciones de calibración estadística

| Hallazgo | Descripción | Impacto |
|----------|-------------|---------|
| H-5.3-1 | Calibración estadística no ejecutable con 6 documentos (N=6 < 20, NADR-23 R12 prohíbe presumir robustez estadística). Defaults actuales son evidence-informed por diseño, NO calibrados empíricamente. | Recalibración pendiente para corpus ≥20 con curvas precision-recall + bootstrap CI + human verdicts + learning curves. |
| H-5.3-3 | GT de doc_07_pesaran no editado en curaduría: NSS=1.0000 es tautología (extractor contra sí mismo). Documento contiene tablas que PyMuPDF no extrae (fuentes Type 3). | Curaduría real diferida con ampliación de corpus. |

### 6.3 Limitaciones de tooling experimental

| Hallazgo | Descripción | Impacto |
|----------|-------------|---------|
| H-5.2-6 | `ASTFingerprintPolicy.semantic_fingerprint()` e `identity_fingerprint()` aplican `.strip()` violando NADR-22 §5.3 R10-R12. Divergencia confinada al tooling experimental (`tools/evaluation/topology/`). La ruta canónica de regresión no usa `ASTFingerprintPolicy`. | Deuda técnica para Fase 6 (mejora del tooling de evaluación). |

### 6.4 Limitaciones de onboarding v2.2

| Hallazgo | Descripción | Impacto |
|----------|-------------|---------|
| H-5.5-2 | doc_09_vanhaverbeke y doc_10_gross sellados con NSS=1.0000 sin curaduría previa: tautología por construcción. | Sustitución diferida a re-baseline v3.0 (corpus ≥20) agrupada con H-5.3-3. |
| H-5.5-4 | Heterogeneidad de baseline: los GTs de doc_01-doc_05 registran nodos de ecuación, tabla y caption (términos descriptivos del Register; los tipos concretos son los valores de `ContentNodeType` presentes en esos GTs sellados) que el runtime PyMuPDF vigente no puede reproducir (degrada a `paragraph`). Regresión v2.2: 5/9 HARD_FAIL. | Re-baseline v3.0 diferido hasta corpus ≥20 identidades. Política de interpretación: HARD_FAIL estructurales esperados, no regresión del runtime. |


### 6.5 Governance Findings abiertos

| GF | Descripción | Resolución |
|----|-------------|------------|
| GF-01 | Conflicto NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución). | Separación de scope: `run_regression` conserva taxonomía NADR-19; runner de certificación de Gate 5 implementa NADR-24. |
| GF-02 | Crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3). | Artefactos de Wave 3.3 permanecen válidos; crosswalk documenta el mapeo. |
| GF-03 | Onboarding v2.2 selló doc_09/doc_10 sin evidencia de curaduría previa (NADR-21 §5.1 R5 violado). | Remediación procedural: `curation_checklist.json` + `curate_gt.py` (Batch 2a) con `report_ref`. Enforcement normativo diferido (H-5.5-5/O3). |

---

## 7. REGISTRO DE IMPACTO DE CAMBIOS (pendiente de pasada 2)

*Sección pendiente. Se completará en pasada 2 tras implementación de Batch 1 (gate O2) y Batch 2 (`main_corpus` con verbos).*

**Regla de anclaje (C3):** cualquier cambio en `build_extraction_pipeline()`, normalización o matching policy **exige** nueva fila con el delta de:

- `configuration_fingerprint` si cambia config de evaluación (NADR-22 §5.6 R19-R21).
- `parameter_identity` si cambian thresholds/pesos (NADR-23 §5.6).
- `manifest_identity`/`corpus_identity` si cambian corpus o GTs (GF-02).
- **Delta de veredicto de regresión** como señal observada para cambios de extractor (gap H-5.5-6).

---

## 8. GUARDRAILS DE GOBERNANZA DEL PROPIO DOCUMENTO

### 8.1 Qué NO puede hacer este documento

- **No redefinir reglas de NADRs/ADRs**: la autoridad normativa vive en los documentos originales.
- **No duplicar contabilidad de reglas**: §1.4 del Plan prohíbe matrices paralelas.
- **No implementar código**: este documento es spec; la implementación vive en los entry points de Categoría A.
- **No registrar hallazgos**: el Findings Register es la fuente única de hallazgos y decisiones.

### 8.2 Protocolo de update

- **§2 (inventario) y §7 (registro de impacto)** pueden actualizarse sin re-aprobación (son estado operativo).
- **§1, §3, §4, §5, §6** (spec normativa) requieren actualización del Execution Plan y/o Findings Register si cambian.
- **Cambios estructurales** (nuevos entry points, nuevos verbos, nueva política de autocorrección) requieren ADR/Execution Plan.

### 8.3 Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| `ADR_F17_BIS_MASTER.md` | Autoridad normativa superior |
| `NADR-F17BIS-20..24` | Reglas congeladas que este documento opera |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` | Secuencia de Tasks y Gates; este documento es spec operacional |
| `FASE_5_DEFERRED_FINDINGS_REGISTER.md` | Registro de hallazgos; §6 de este documento hace cross-ref |
| `FASE_5_EXIT_REVIEW_EVIDENCE_LOG.md` | Evidencia forense de decisiones; este documento cita los hallazgos |
| `FASE_5_WAVE_1_3_CURATION_REPORT.md` | Evidencia de curaduría; §3.4 de este documento referencia el checklist |

### 8.4 Destino machine-checkable (Fase 6)

En Fase 6, §7 se volverá machine-checkable: un test en CI recomputará las identidades (config fingerprint, parameter identity, manifest hash) desde el repo y fallará si difieren de la última fila de §7 sin un finding asociado. Eso convierte el registro en control, no en bitácora.

---

**Nota de Gobernanza:** Este documento es la spec operacional del benchmark de certificación. No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs. Su único propósito es normar el runbook de onboarding y evaluación, consolidar el inventario de assets, y servir como referencia única para interpretar veredictos de regresión. Los hallazgos que comprometan la inmutabilidad de un oráculo sellado, la biyección PDF↔oráculo, el determinismo de la evaluación, la independencia entre calibración y evaluación final, o la semántica de fallo uniforme son bloqueantes hasta que se resuelvan o se reclasifiquen formalmente con evidencia durante los Gate Exit Reviews.