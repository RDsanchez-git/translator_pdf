# HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-09-24
**Fecha de congelamiento:** 2026-09-24
**Fase:** 17-BIS — Fase 6 (Continuous Verification)
**Tipo de artefacto:** Forensic Discovery / Boundary Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- ADR_F17_BIS_MASTER.md (FROZEN)
- ADR_F17_BIS_05.md (FROZEN)
- METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0 (FROZEN)
- METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN)
- ENGINEERING_PRINCIPLES.md (FROZEN)
- ROADMAP_ARQUITECTONICO_LP.md (FROZEN)
- PROJECT_SCOPE.md (FROZEN)
- FASE_5_HANDOFF.md v1.0.1 (FROZEN)
- PHASE_17BIS_FASE5_EXECUTION_PLAN.md v1.5.0 (FROZEN)
- .github/workflows/ci.yml
- pyproject.toml (markers)
- tests/ (búsqueda exhaustiva)
- .gitignore
**Mandato:** ¿Qué significa arquitectónicamente Continuous Verification dentro de F17-BIS y dónde termina la responsabilidad de Phase 5 / comienza Phase 6?
**Síntesis:** La arquitectura exige que Continuous Verification integre Regression Gates en CI/CD contra el pipeline productivo. La evidencia demuestra que existe un job CI nominal que no ejecuta ninguna verificación efectiva contra la baseline sellada.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-DRAFT | 2026-09-24 | Emisión inicial. |
| 1.0.0-FROZEN | 2026-09-24 | FROZEN. Corrección de numeración de secciones. Revisión de arquitectura completada. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la frontera arquitectónica entre Fase 5 (Baseline Certification, cerrada) y Fase 6 (Continuous Verification) dentro de Fase 17-BIS. La auditoría cubrió: el ADR Maestro y ADR de Fase como fuentes normativas, el CI workflow actual, el tooling de regresión existente, el corpus canónico sellado, los tests de regresión y la infraestructura de materialización.

**Hallazgo central:**

> Existe un job CI denominado `regression-gates` que ejecuta `pytest -m "regression"`, pero el repositorio contiene cero tests con ese marker. El resultado es exit code 5 (no tests collected). No existe invocación demostrada de `run_regression.py` ni del corpus canónico desde CI. No existe infraestructura de materialización de PDFs. La verificación de inmutabilidad apunta a `tests/fixtures/` (caches y fixtures sintéticos), no a la baseline canónica. Esto constituye una **Regression Gate Illusion**: la infraestructura CI tiene la apariencia de un control de regresión, pero no verifica efectivamente la Scientific Baseline sellada por Fase 5.

**Defectos dominantes confirmados:**

1. **Regression Gate Illusion (E-6.0-001, E-6.0-002):** El CI tiene un job que selecciona 0 tests y retorna exit code 5.
2. **Desconexión del pipeline productivo (E-6.0-003):** 6 tests de integración usan `build_extraction_pipeline()` pero ninguno tiene marker `regression`.
3. **Ausencia de materialización de corpus (E-6.0-004, E-6.0-005):** 14 de 21 PDFs del corpus no están trackeados y no existe mecanismo de descarga/materialización.

**Veredicto:** La capacidad de Continuous Verification definida por el ADR Maestro §6 NO está implementada. Existe infraestructura nominal (job CI, marker definido, entry point CLI) pero NO existe conexión funcional entre esa infraestructura y la baseline sellada. La frontera Fase 5 → Fase 6 está claramente definida por ADR_F17_BIS_05 §5: "La Fase 5 materializa los Regression Gates como artefactos ejecutables y verificables fuera de CI. La Fase 6 integra estos artefactos en el pipeline de CI/CD." Esa integración no existe.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Específicamente, este HITO:
- **NO** decide si la semántica de Continuous Verification debe ser conformance, regression o baseline de divergencia.
- **NO** propone soluciones para materializar el corpus en CI.
- **NO** diseña el adapter CI ↔ dominio.
- **NO** decide si se requiere recalibración o re-baseline.
- **NO** resuelve ningún Decision Candidate.

Este HITO **SÍ**:
- Documenta qué existe y qué no existe.
- Documenta qué exige la arquitectura.
- Documenta dónde difieren.
- Identifica Decision Candidates que el ADR/NADR de Fase 6 deberá resolver.
- Preserva el hallazgo de "Regression Gate Illusion" como evidencia forense fundacional.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (ADR Master, ADR Fase 5, METHODOLOGY, ENGINEERING_PRINCIPLES).
2. Cargar HITOs/artefactos previos aplicables (FASE_5_HANDOFF, Execution Plan v1.5.0).
3. Inspeccionar runtime/código/artefactos (CI workflow, tests, .gitignore, corpus).
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar `TO BE VERIFIED` cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

### 2.3 Axioma de entrada

> **Fase 6 no tiene permiso para "arreglar" silenciosamente aquello que Fase 5 materializó y selló.** Su primera responsabilidad es determinar si la baseline sellada puede ser consumida de forma correcta, reproducible y operativamente útil para verificar cambios del pipeline productivo. Si descubre que no puede, produce evidencia y un Decision Candidate, no recalibra por su cuenta.

Este axioma protege:
- La inmutabilidad de los 21 oráculos sellados (NADR-21 §5.4 R19).
- El manifest hash `727782fe0df26d9d...` (corpus v3.9).
- Los parámetros congelados (parameter identity `67841171...`).
- La certificación REJECTED_WITH_DOCUMENTED_LIMITATIONS como resultado final de Fase 5.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `.github/workflows/ci.yml` | Workflow CI completo (4 jobs) | 100% auditado |
| `tests/` | Búsqueda exhaustiva de `pytest.mark.regression` y `build_extraction_pipeline` | 100% auditado |
| `tools/evaluation/run_regression.py` | Entry point de regresión (Imperative Shell) | Referenciado (auditoría completa en HITO 6.1) |
| `core/benchmark/topology/regression/` | Functional Core de regresión | Referenciado (auditoría completa en HITO 6.3) |
| `tests/corpus/canonical/` | Corpus canónico sellado | Parcial (tracking en git auditado, contenido en HITO 6.2) |
| `.gitignore` | Reglas de exclusión de corpus | 100% auditado |
| `pyproject.toml` | Markers de pytest, configuración | 100% auditado |
| `apps/bootstrap/pipeline_factory.py` | `build_extraction_pipeline()` | Referenciado (SUT normativo, auditoría en HITO 6.1) |
| ADR_F17_BIS_MASTER.md | Fuente normativa | 100% auditado |
| ADR_F17_BIS_05.md | Fuente normativa (Phase 5 boundary) | 100% auditado |
| FASE_5_HANDOFF.md v1.0.1 | Estado de cierre Fase 5 | 100% auditado |
| ENGINEERING_PRINCIPLES.md | Principios transversales | Referenciado |
| ROADMAP_ARQUITECTONICO_LP.md | Visión a largo plazo | Referenciado |
| PROJECT_SCOPE.md | Alcance del proyecto | Referenciado |
| `tests/fixtures/` | Contenido real vs uso en CI | 100% auditado |
| Métricas de pytest | 744 tests colectables | Verificado por ejecución |

**Fuera de scope:**
- Contenido detallado de los 21 Ground Truths (HITO 6.2)
- Mecanismo interno de DoubleProtectionMechanism (HITO 6.3)
- Semántica de exit codes de run_regression.py en detalle (HITO 6.3)
- Performance de ejecución del regression gate (HITO 6.4)
- Diseño de solución para materialización de corpus (fuera de HITO por naturaleza read-only)

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR (normativa) | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` | Define Phase 6 como "Continuous Verification (Integración definitiva en CI Gates)" |
| ADR (normativa) | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_05.md` | Define frontera Phase 5 → Phase 6, Cláusula de relación con Fase 6 |
| Metodología (normativa) | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 | Flujo de gobernanza, taxonomía documental |
| Principios (normativa) | `docs/architecture/ENGINEERING_PRINCIPLES.md` | Cero Fallos Silenciosos, Reuse Before Invent |
| Roadmap (normativa) | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` | Definición de Fase 17_BIS: "Regression Gates: Aserción estricta en CI" |
| Scope (normativa) | `docs/architecture/PROJECT_SCOPE.md` | Alcance del proyecto y restricciones |
| Handoff (forense) | `docs/architecture/adr/phase-17-bis/handoff/FASE_5_HANDOFF.md` v1.0.1 | Estado de cierre Fase 5, carry-forwards |
| Execution Plan (forense) | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.5.0 | Gate 5 CONDITIONAL_PASS, Phase REJECTED |
| CI (runtime) | `.github/workflows/ci.yml` | Evidencia del job regression-gates |
| Tests (runtime) | `tests/` (búsqueda exhaustiva) | Evidencia de markers y uso de pipeline |
| Configuración (runtime) | `pyproject.toml` | Marker "regression" definido pero sin tests |
| Git (runtime) | `.gitignore` | Reglas de exclusión de corpus PDFs |
| Ejecución (forense) | `python -m pytest -m "regression" --collect-only` | Exit code 5, 0 tests seleccionados |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Continuous Verification según ADR Maestro (estado requerido)

```text
CI/CD trigger (push/PR)
    -> regression-gates job
    -> materialización del corpus canónico
    -> invocación del Regression Gate (NADR-22 §5.7)
    -> build_extraction_pipeline() [production pipeline]
    -> candidate AST
    -> DoubleProtectionMechanism (NSS + Criticality)
    -> evidence (regression_report.json)
    -> exit code (PASS/WARNING/HARD_FAIL)
    -> CI decision (merge block / report)

Leyenda:
  [REQUIRED] definido por ADR/NADR pero no implementado
```

**Estado:** [REQUIRED] — Este flujo NO existe en el repositorio actual.

### FLUJO B — CI actual observado (Regression Gate Illusion)

```text
CI/CD trigger (push main/develop, PR main)
    -> regression-gates job
    -> pytest -m "regression"                    [GAP: 0 tests]
    -> exit code 5 (no tests collected)          [GAP: job falla]
    -> git diff --exit-code tests/fixtures/      [GAP: ruta incorrecta]

Leyenda:
  [GAP] gap confirmado con evidencia
```

**Estado:** [GAP] — El flujo existe nominalmente pero no verifica la baseline.

### FLUJO C — Producción vs Tests de regresión (desconexión)

```text
build_extraction_pipeline()
    -> usado en test_chunker_snapshot.py          [OK: usa production pipeline]
    -> usado en test_golden_parser.py             [OK: usa production pipeline]
    -> usado en test_pipeline_orchestration.py    [OK: usa production pipeline]
    -> usado en test_real_e2e.py                  [OK: usa production pipeline]
    -> usado en test_real_paper.py                [OK: usa production pipeline]
    -> usado en test_real_parser_pipeline.py      [OK: usa production pipeline]
    -> NINGUNO tiene @pytest.mark.regression      [GAP: desconexión]

test_regression_entry_point.py
    -> usa mocks (NO production pipeline)         [GAP: no verifica SUT real]
    -> NO tiene @pytest.mark.regression           [GAP: no seleccionable]
```

**Estado:** [GAP] — El production pipeline se usa en tests de integración, pero esos tests no están conectados al marker `regression`.

### FLUJO D — Materialización de corpus (inexistente)

```text
tests/corpus/canonical/pdf/
    -> .gitignore: "tests/corpus/canonical/pdf/"  [GAP: excluido de git]
    -> git ls-files: solo doc_01 a doc_07         [GAP: 7/21 trackeados]
    -> CI: no download, no artifact, no cache     [GAP: no materialización]
    -> run_regression.py requiere --pdf-dir       [GAP: input no disponible]

Leyenda:
  [GAP] gap confirmado
```

**Estado:** [GAP] — 14 de 21 PDFs no están disponibles en un clone fresco y no existe mecanismo de materialización.

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| Continuous Verification (concepto) | ADR Master §6, ADR_05 §5/§7 | Sí (DoD Level B) | Integración de Regression Gates en CI/CD | CONFIRMADO (requerido) |
| Regression Gate (concepto) | ADR_05 §7 Target State paso 6, ROADMAP "Regression Gates" | Sí | Mecanismo que ejecuta regresión topológica contra baseline | CONFIRMADO (requerido) |
| Job CI `regression-gates` | `.github/workflows/ci.yml` línea 42 | Parcial (existe pero no funcional) | Ejecuta `pytest -m "regression"` | CONFIRMADO (nominal, no efectivo) |
| Marker `regression` | `pyproject.toml` línea 75 | Sí (definido) | "Regression gate tests (golden corpus, snapshots) — NADR-10" | CONFIRMADO (definido, sin tests) |
| Tests con marker `regression` | Búsqueda exhaustiva en `tests/` | No | Ningún archivo tiene `@pytest.mark.regression` | MISSING |
| `build_extraction_pipeline()` | `apps/bootstrap/pipeline_factory.py` | Sí (SUT normativo) | Composición productiva de extracción | CONFIRMADO (existe, usado en 6 tests sin marker) |
| `run_regression.py` | `tools/evaluation/run_regression.py` | Sí (Imperative Shell) | Entry point de regresión con exit codes 0/1/2 | CONFIRMADO (existe, no invocado desde CI) |
| `DoubleProtectionMechanism` | `core/benchmark/topology/regression/mechanism.py` | Sí (Functional Core) | NSS + Criticality, precedencia CRITICAL | CONFIRMADO (existe, conformance absoluta) |
| Corpus canónico sellado | `tests/corpus/canonical/` (21 docs) | Sí (baseline Phase 5) | v3.9, manifest 727782fe... | CONFIRMADO (sellado, parcialmente trackeado) |
| Materialización de corpus en CI | No existe | No | Mecanismo de descarga/provisión de PDFs | MISSING |
| Verificación de inmutabilidad | `ci.yml` línea 70: `git diff tests/fixtures/` | Parcial (existe pero incorrecta) | Protege fixtures sintéticos, no baseline | CONFIRMADO (ruta incorrecta) |
| Concepto de delta-regression | No existe en código | No | Comparación contra referencia previa | MISSING |
| Estado BASELINE_INTEGRITY_FAILURE | No existe en código | No | Distinción de integridad de baseline | MISSING |
| Adaptador CI ↔ dominio | No existe | No | Conexión entre CI y Regression Gate | MISSING |

---

## 7. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-6.0-001** | P0 | `.github/workflows/ci.yml::regression-gates` → `python -m pytest -m "regression"` | **Job CI ejecuta selector vacío.** El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests de 744 colectables. |
| **E-6.0-002** | P0 | Ejecución forense: `python -m pytest -m "regression" --collect-only` → `Exit code: 5` | **Exit code 5 confirmado.** pytest retorna 5 (no tests collected). Sin `continue-on-error`, el job falla. |
| **E-6.0-003** | P1 | `tests/` → búsqueda `pytest.mark.regression` → 0 resultados | **Cero tests con marker regression.** Ningún archivo en el repositorio contiene `@pytest.mark.regression`. |
| **E-6.0-004** | P0 | `.github/workflows/ci.yml` → búsqueda de download/artifact/corpus/cache → 0 mecanismos | **No existe materialización de corpus.** Ningún step descarga, cachea o materializa PDFs del corpus canónico. |
| **E-6.0-005** | P1 | `.gitignore` → `tests/corpus/canonical/pdf/` | **Corpus PDFs excluidos de git.** La regla ignora explícitamente el directorio de PDFs. Solo 7/21 trackeados (agregados antes de la regla). |
| **E-6.0-006** | P1 | `.github/workflows/ci.yml::regression-gates` → `git diff --exit-code tests/fixtures/` | **Inmutabilidad verifica ruta incorrecta.** El check protege `tests/fixtures/` (caches, PDF genérico), no `tests/corpus/canonical/`. |
| **E-6.0-007** | P1 | `tests/integration/test_chunker_snapshot.py`, `test_golden_parser.py`, `test_pipeline_orchestration.py`, `test_real_e2e.py`, `test_real_paper.py`, `test_real_parser_pipeline.py` → `build_extraction_pipeline()` | **Production pipeline sin marker regression.** 6 tests de integración usan la composición productiva pero ninguno tiene `@pytest.mark.regression`. |
| **E-6.0-008** | P1 | `tests/integration/test_regression_entry_point.py` → usa `MagicMock`, `patch`, fixtures en memoria | **Entry point de regresión usa mocks.** El test que debería verificar el regression gate no ejecuta el corpus canónico ni el production pipeline. |
| **E-6.0-009** | P2 | `core/benchmark/topology/regression/mechanism.py::DoubleProtectionMechanism` → compara candidate ↔ oracle | **Solo conformance absoluta.** El mecanismo compara candidato contra oráculo sellado. No existe concepto de delta-regression ni baseline de divergencia. |
| **E-6.0-010** | P2 | FASE_5_HANDOFF.md v1.0.1 → Phase outcome: REJECTED_WITH_DOCUMENTED_LIMITATIONS | **Fase 5 NO certificó científicamente.** El resultado fue REJECTED (NSS 0.7208 < 0.80, 163 Critical FN). La baseline está sellada pero no certificada. |
| **E-6.0-011** | P2 | `pyproject.toml` línea 75 → `"regression: Regression gate tests (golden corpus, snapshots) — NADR-10"` | **Marker definido con referencia a NADR-10.** La descripción del marker referencia "golden corpus, snapshots" y NADR-10, pero no hay implementación asociada. |
| **E-6.0-012** | P2 | `tests/fixtures/` → 40+ archivos `*_cache_*.db`, `sample_3_pages.pdf`, `unit_cost_context.py` | **tests/fixtures/ contiene basura de tests.** No contiene oráculos del corpus canónico. La verificación de inmutabilidad del CI inspecciona esta ruta. |

### Evidencia E-6.0-001: Job CI ejecuta selector vacío

* **Archivo Fuente Primario:** `.github/workflows/ci.yml`
* **Símbolo Auditado:** Job `regression-gates`, step "Run regression gates (pytest marker)"
* **Declaración Observada:**

```yaml
- name: Run regression gates (pytest marker)
  run: |
    python -m pytest -m "regression" -v --tb=short --no-header
  env:
    CORPUS_READONLY: "true"
```

* **Observed:** El CI ejecuta `pytest -m "regression"`. No hay `continue-on-error`. No hay tolerancia al exit code.
* **Required:** ADR Master §6 exige "Integración definitiva en CI Gates". ADR_05 §5 exige que Fase 6 integre los Regression Gates en CI/CD. ROADMAP exige "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos."
* **Decision:** Fase 5 declaró en su Execution Plan v1.5.0: "Regression Gates Materializados: ejecutable y verificable contra la Baseline certificada (fuera de CI)". La integración en CI fue explícitamente diferida a Fase 6.
* **Hallazgo Forense:** El job existe pero ejecuta un selector que retorna 0 tests. La infraestructura CI fue creada con una frontera nominal de regresión, pero no existe sujeto ejecutable conectado a dicha frontera.
* **Consecuencia Arquitectónica:** Continuous Verification NO está implementada. El DoD Level B del ADR Master ("Compuertas de CI Activas") NO está satisfecho.
* **Estado:** OPEN

### Evidencia E-6.0-002: Exit code 5 confirmado

* **Archivo Fuente Primario:** Ejecución forense directa
* **Símbolo Auditado:** `pytest -m "regression" --collect-only`
* **Declaración Observada:**

```text
collected 744 items / 744 deselected / 0 selected
Exit code: 5
```

* **Observed:** pytest retorna exit code 5, que según documentación oficial significa "no tests were collected".
* **Required:** El CI debe ejecutar una verificación efectiva. Un exit code 5 sin `continue-on-error` hace que el job falle, bloqueando `integration-tests` (que depende de `regression-gates`).
* **Decision:** No existe decisión previa que explique por qué el job existe sin tests. Posible explicación: el job fue creado como placeholder durante una fase anterior con la intención de poblarlo después.
* **Hallazgo Forense:** El job `regression-gates` falla sistemáticamente si se ejecuta en CI. Esto significa que o bien (a) el CI ha estado fallando en main/develop, o (b) no se han hecho pushes desde que se agregó el job, o (c) el workflow no se ha ejecutado.
* **Consecuencia Arquitectónica:** Si el CI se ejecuta, falla. Si no se ejecuta, no hay protección. En ambos casos, no existe Continuous Verification efectiva.
* **Estado:** OPEN

### Evidencia E-6.0-007: Production pipeline sin marker regression

* **Archivo Fuente Primario:** `tests/integration/` (6 archivos)
* **Símbolo Auditado:** `build_extraction_pipeline()` en tests de integración
* **Declaración Observada:**

```text
tests/integration/test_chunker_snapshot.py:17: self.adapter = build_extraction_pipeline()
tests/integration/test_golden_parser.py:17: self.adapter = build_extraction_pipeline()
tests/integration/test_pipeline_orchestration.py:95: parser = build_extraction_pipeline()
tests/integration/test_real_e2e.py:104: parser = build_extraction_pipeline()
tests/integration/test_real_paper.py:19: parser = build_extraction_pipeline()
tests/integration/test_real_parser_pipeline.py:13: self.adapter = build_extraction_pipeline()
```

* **Observed:** 6 tests de integración usan la composición productiva (`build_extraction_pipeline()`), que es el SUT normativo según NADR-19 §5.5 R20 y el ADR Master §2.1 ("la baseline evalúa el pipeline de producción"). Sin embargo, ninguno de estos tests tiene `@pytest.mark.regression`.
* **Required:** Los tests que ejercen el production pipeline contra la baseline sellada deberían ser seleccionables por el marker `regression` para que el CI los ejecute.
* **Decision:** Estos tests fueron creados en fases anteriores (Fase 4, integración) con propósito de verificación funcional, no de regresión topológica contra baseline sellada.
* **Hallazgo Forense:** Existe una desconexión entre los tests que usan el production pipeline y el marker de regresión. Los tests que deberían ser el Regression Gate (contra baseline sellada) no existen. Los tests que usan el production pipeline (para otros propósitos) no están conectados al gate.
* **Consecuencia Arquitectónica:** Aunque se corrigiera el CI para ejecutar `pytest -m "regression"`, no hay tests que verificarían la baseline. Se necesitarían tests nuevos que ejecuten el production pipeline contra el corpus canónico sellado.
* **Estado:** OPEN

---

## 8. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-6.0-01 | La variable `CORPUS_READONLY: "true"` en el workflow CI no tiene consumidor demostrado en el código. No se encontró lectura de esta variable en ningún archivo Python. | Bajo | OPEN |
| OBS-6.0-02 | El nombre del job "Regression Gates (Golden Corpus + Snapshots)" sugiere dos capacidades (golden corpus + snapshots), pero ninguna de las dos está implementada como test seleccionable. | Bajo | OPEN |
| OBS-6.0-03 | El comentario en ci.yml dice "El corpus es Read-Only: los tests no pueden mutar los oráculos" y usa `persist-credentials: false`. Esto es correcto como protección, pero presupone que el corpus está disponible (no lo está para 14/21 PDFs). | Medio | OPEN |
| OBS-6.0-04 | `tests/fixtures/sample_3_pages.pdf` (2MB) está trackeado en git y es el único PDF de test disponible en un clone fresco. No es parte del corpus canónico. | Bajo | OPEN |
| OBS-6.0-05 | El marker `regression` en pyproject.toml referencia "NADR-10", que no existe en la numeración actual de NADRs de 17-BIS (NADR-F17BIS-01 a NADR-F17BIS-24). Posible referencia a un NADR de una fase anterior. | Bajo | OPEN |
| OBS-6.0-06 | La descripción del marker dice "golden corpus, snapshots" pero el concepto de "snapshots" no aparece en ningún test ni en la arquitectura de regresión topológica de Fase 5. Posible referencia a un mecanismo de snapshot testing no implementado. | Bajo | OPEN |

---

## 9. MATRIZ DE PILARES

### Pilar 1 — Integración de Regression Gates en CI/CD

| Elemento | Estado | Evidencia |
|---|---|---|
| Job CI `regression-gates` existe | EXISTENTE | E-6.0-001 |
| Job ejecuta selector `pytest -m "regression"` | EXISTENTE | E-6.0-001 |
| Tests con marker `regression` | FALTANTE | E-6.0-003 |
| Invocación de `run_regression.py` desde CI | FALTANTE | E-6.0-001, E-6.0-002 |
| Materialización de corpus en CI | FALTANTE | E-6.0-004, E-6.0-005 |
| Exit code handling (PASS/WARNING/HARD_FAIL) | PARCIAL (definido en dominio, no conectado a CI) | E-6.0-002 |
| Verificación de inmutabilidad de baseline | PARCIAL (existe pero apunta a ruta incorrecta) | E-6.0-006 |
| Evidence generation (regression_report.json) | EXISTENTE (en tooling, no en CI) | E-6.0-008 |

**Veredicto del pilar:** La infraestructura nominal existe (job, marker, env vars) pero la conexión funcional entre CI y la baseline sellada NO existe. El pilar está FALTANTE en términos de funcionalidad efectiva.

### Pilar 2 — Sujeto bajo prueba (Production Pipeline)

| Elemento | Estado | Evidencia |
|---|---|---|
| `build_extraction_pipeline()` existe | EXISTENTE | E-6.0-007 |
| Tests que usan production pipeline | EXISTENTE (6 tests de integración) | E-6.0-007 |
| Tests de producción conectados a regression gate | FALTANTE | E-6.0-003, E-6.0-007 |
| Entry point de regresión usa production pipeline | PARCIAL (run_regression.py sí, test_regression_entry_point.py no) | E-6.0-008 |
| Verificación contra corpus canónico sellado desde tests | FALTANTE | E-6.0-003 |

**Veredicto del pilar:** El SUT normativo existe y es usado en tests de integración, pero NO está conectado al mecanismo de regresión topológica contra la baseline sellada.

### Pilar 3 — Baseline canónica consumible

| Elemento | Estado | Evidencia |
|---|---|---|
| Corpus v3.9 sellado (21 docs) | EXISTENTE | FASE_5_HANDOFF v1.0.1 |
| Manifest trackeado en git | EXISTENTE | git ls-files |
| Ground Truths trackeados (17/21) | PARCIAL | git ls-files |
| PDFs trackeados (7/21) | PARCIAL | git ls-files |
| Mecanismo de materialización de PDFs en CI | FALTANTE | E-6.0-004 |
| Verificación de identidad (SHA-256) disponible | EXISTENTE (en manifest) | FASE_5_HANDOFF |

**Veredicto del pilar:** La baseline existe y está sellada, pero NO es consumible en CI porque 14/21 PDFs no están disponibles y no hay mecanismo de materialización.

### Pilar 4 — Semántica operacional

| Elemento | Estado | Evidencia |
|---|---|---|
| Conformance absoluta (candidate ↔ oracle) | EXISTENTE | E-6.0-009 |
| Delta-regression (candidate_N ↔ candidate_N-1) | FALTANTE | E-6.0-009 |
| Baseline de divergencia (D₀ vs D₁) | FALTANTE | E-6.0-009 |
| Estado BASELINE_INTEGRITY_FAILURE | FALTANTE | Inventario §6 |
| Taxonomía PASS/WARNING/HARD_FAIL | EXISTENTE (en dominio) | run_regression.py exit codes |
| Traducción de exit codes a CI decision | FALTANTE | E-6.0-001 |

**Veredicto del pilar:** La semántica de conformance absoluta existe. La semántica de regression relativa NO existe. La taxonomía de estados operacionales está incompleta.

---

## 10. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-6.0-01** | No existe Continuous Verification efectiva: el CI tiene un job nominal que no ejecuta ninguna verificación contra la baseline sellada. | E-6.0-001, E-6.0-002, E-6.0-003 | Pilar 1 / ADR Master §6, DoD Level B | **Fase 6** | BLOCKING |
| **GAP-6.0-02** | No existe mecanismo de materialización del corpus canónico en CI. 14/21 PDFs no están trackeados. | E-6.0-004, E-6.0-005 | Pilar 3 / NADR-20 §5.1 | **Fase 6** | BLOCKING |
| **GAP-6.0-03** | La verificación de inmutabilidad del CI protege `tests/fixtures/` (caches y fixtures sintéticos), no la baseline canónica en `tests/corpus/canonical/`. | E-6.0-006, E-6.0-012 | Pilar 1 / NADR-21 §5.4 R19 | **Fase 6** | OPEN |
| **GAP-6.0-04** | Los tests que usan el production pipeline (`build_extraction_pipeline()`) no están conectados al marker `regression`. No existe test que ejecute el production pipeline contra el corpus canónico sellado. | E-6.0-007, E-6.0-003 | Pilar 2 / NADR-19 §5.5 R20 | **Fase 6** | BLOCKING |
| **GAP-6.0-05** | El mecanismo actual implementa solo conformance absoluta (candidate ↔ oracle). No existe concepto de delta-regression ni baseline de divergencia. | E-6.0-009 | Pilar 4 / DC-6.1 | **Fase 6 (DC)** | OPEN |
| **GAP-6.0-06** | No existe estado `BASELINE_INTEGRITY_FAILURE` separado de `EXECUTION_FAILURE`. La taxonomía operacional está incompleta. | Inventario §6 | Pilar 4 / DC-6.4 | **Fase 6 (DC)** | OPEN |

---

## 11. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-6.0-A | El job `regression-gates` fue creado como placeholder con intención de poblarlo después. | CONFIRMADA (indirecta) | E-6.0-011 (marker referencia NADR-10, descripción menciona "golden corpus, snapshots" sin implementación) | El job no es un error accidental sino una frontera nominal pre-diseñada. |
| H-6.0-B | Los tests de integración que usan `build_extraction_pipeline()` podrían ser reutilizados como regression tests con el marker adecuado. | TO BE VERIFIED | E-6.0-007 | Requiere determinar si esos tests verifican contra la baseline sellada o solo contra fixtures locales. Destino: HITO 6.1. |
| H-6.0-C | La variable `CORPUS_READONLY` tiene un consumidor no descubierto. | RECHAZADA | OBS-6.0-01 (búsqueda exhaustiva no encontró consumidor) | La variable es decorativa o su consumidor fue eliminado. |
| H-6.0-D | El CI ha estado fallando en main/develop desde que se agregó el job regression-gates. | NO VERIFICABLE | E-6.0-002 | No se puede verificar el historial de ejecución de GitHub Actions desde el repositorio local. Requiere acceso al dashboard de CI. |
| H-6.0-E | `run_regression.py` podría ejecutarse directamente desde CI sin necesidad de un adapter pytest. | TO BE VERIFIED | E-6.0-008 | Requiere determinar si la invocación directa es suficiente o si se necesita integración con el framework de tests. Destino: HITO 6.3 (DC-6.3). |

---

## 12. RESPUESTAS A PREGUNTAS DEL MANDATO

### 12.1 ¿Qué significa arquitectónicamente Continuous Verification dentro de F17-BIS?

**Estado actual verificado:**

1. ADR Master §6 define Fase 6 como "Continuous Verification (Integración definitiva en CI Gates)".
2. ADR Master §10 DoD Level B exige: "Compuertas de CI Activas: Pipeline en integración continua ejecutándose de forma exitosa contra los Regression Gates."
3. ROADMAP define: "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos."
4. ADR_05 §5 establece: "La Fase 5 materializa la Baseline Certificada y los Regression Gates como artefactos ejecutables y verificables fuera de CI. La Fase 6 integra estos artefactos en el pipeline de CI/CD."

**Respuesta forense:**

Continuous Verification significa, según la arquitectura vigente: **la integración de los Regression Gates (construidos en Fase 5) en el pipeline de CI/CD, de manera que cada cambio al pipeline productivo sea confrontado automáticamente contra la Scientific Baseline sellada, con capacidad de bloquear regresiones.**

NO significa:
- Re-calibrar la baseline (eso sería una nueva certificación).
- Modificar los oráculos sellados (prohibido por NADR-21 §5.4 R19).
- Mejorar el extractor (eso es un carry-forward a fase posterior).
- Crear nueva infraestructura de evaluación (el Functional Core ya existe).

**Implicación:**

La arquitectura exige que Fase 6 tome los artefactos existentes (DoubleProtectionMechanism, run_regression.py, corpus sellado, thresholds) y los conecte al CI de manera que:
1. Se ejecuten automáticamente ante cambios relevantes.
2. Usen el production pipeline real (no fixtures sintéticos).
3. Consuman la baseline sellada (no una copia parcial).
4. Produzcan evidencia auditable (regression_report).
5. Bloqueen o reporten según el veredicto.

### 12.2 ¿Dónde termina la responsabilidad de Phase 5 / comienza Phase 6?

**Estado actual verificado:**

1. Fase 5 cerró con Gate outcome CONDITIONAL_PASS, Phase outcome REJECTED_WITH_DOCUMENTED_LIMITATIONS.
2. Fase 5 materializó: corpus sellado (21 docs), GTs sellados, tooling de regresión (Functional Core + Imperative Shell), Certification Evidence, Handoff Document.
3. Fase 5 NO implementó: integración en CI, materialización de corpus en CI, tests de regresión contra corpus sellado.
4. ADR_05 §7 Target State muestra "CONTINUOUS VERIFICATION" como paso 6, explícitamente "fuera del alcance de Fase 5".

**Respuesta forense:**

La frontera está definida por ADR_05 §5 y §7:

```text
FASE 5 (cerrada):
├── Corpus canónico materializado y sellado ✅
├── Ground Truths sellados ✅
├── Tooling de regresión construido (Functional Core + Imperative Shell) ✅
├── Certification Evidence emitida ✅
├── Semántica de fallo implementada ✅
├── Determinismo verificado ✅
└── NO: integración en CI ❌

FASE 6 (pendiente):
├── Integración del Regression Gate en CI/CD ← frontera
├── Materialización del corpus en CI
├── Tests de regresión contra corpus sellado
├── Semántica operacional para CI
├── Perfil de ejecución por evento
└── Posiblemente: delta-regression, recalibración
```

**Implicación:**

Fase 6 NO construye la baseline (ya existe). NO construye el mecanismo de regresión (ya existe). NO certifica la baseline (Fase 5 lo intentó y el resultado fue REJECTED). Lo que Fase 6 debe hacer es **conectar** lo existente al CI de manera efectiva.

### 12.3 ¿Existe una "Regression Gate Illusion"?

**Estado actual verificado:**

1. El job `regression-gates` existe en CI (E-6.0-001).
2. El marker `regression` está definido en pyproject.toml (E-6.0-011).
3. El nombre del job dice "Regression Gates (Golden Corpus + Snapshots)" (E-6.0-002).
4. `pytest -m "regression"` selecciona 0 tests (E-6.0-002).
5. No hay tests con `@pytest.mark.regression` (E-6.0-003).
6. La verificación de inmutabilidad apunta a `tests/fixtures/` (E-6.0-006).

**Respuesta forense:**

Sí. Existe una **Regression Gate Illusion** análoga a la "Ilusión del Benchmark" identificada en Fase 0 (ADR Master §2.1). La infraestructura CI tiene la apariencia de un control de regresión (job dedicado, marker definido, variable de entorno, verificación de inmutabilidad), pero no verifica efectivamente la Scientific Baseline.

La diferencia con la "Ilusión del Benchmark" de Fase 0 es que en aquel caso el benchmark medía una ruta legacy aislada. En este caso, el gate no mide ninguna ruta: selecciona cero tests.

**Implicación:**

Este hallazgo es el equivalente forense de HITO_0.1 para Fase 6. Demuestra que no se puede asumir que "CI existe y funciona" sin verificar qué ejecuta realmente. El ADR/NADR de Fase 6 debe abordar explícitamente esta desconexión.

---

## 13. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-6.1** | Semántica de Continuous Verification: conformance vs regression vs baseline de divergencia vs ambas | E-6.0-009, GAP-6.0-05 | Ausente (solo conformance absoluta existe) | **Fase 6** |
| **DC-6.2** | Materialización del corpus canónico en CI (espacio de alternativas) | E-6.0-004, E-6.0-005, GAP-6.0-02 | Ausente | **Fase 6** |
| **DC-6.3** | Frontera CI ↔ dominio: pytest marker vs invocación directa vs wrapper | E-6.0-001, E-6.0-002, E-6.0-007, E-6.0-008, GAP-6.0-04 | Ausente | **Fase 6** |
| **DC-6.4** | Taxonomía de estados operacionales (¿agregar BASELINE_INTEGRITY_FAILURE?) | E-6.0-009, GAP-6.0-06 | Ausente (solo PASS/WARNING/HARD_FAIL) | **Fase 6** |
| **DC-6.5** | Perfil de ejecución por evento (PR smoke vs merge full vs nightly) | E-6.0-004, E-6.0-005, GAP-6.0-02 | Ausente | **Fase 6** |
| **DC-6.6** | Alcance de recalibración/re-baseline (dentro de Fase 6 vs nuevo ciclo gobernado) | E-6.0-010, FASE_5_HANDOFF | TO BE VERIFIED (puede ser restricción de gobernanza) | **Fase 6 o posterior** |

> **Nota de gobernanza:** Una resolución normativa no equivale a implementación. Esta matriz rastrea la materialización operativa en código, wiring, tests o artefactos.

---

## 14. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| CI actualmente fallando | Si se hace push a main/develop, el job regression-gates retorna exit 5 y falla. Esto bloquea integration-tests. | Alto (bloquea merges si CI se ejecuta) | E-6.0-002 |
| Falsa sensación de protección | El nombre "Regression Gates (Golden Corpus + Snapshots)" puede hacer creer a desarrolladores que existe protección contra regresiones. | Medio | E-6.0-001, E-6.0-011 |
| Inmutabilidad no verificada | La verificación de inmutabilidad protege la ruta incorrecta, por lo que mutaciones al corpus canónico pasarían desapercibidas en CI. | Alto | E-6.0-006 |
| Corpus no reproducible en CI | Si se construye un regression gate sin resolver la materialización, se corre el riesgo de verificar solo 7/21 documentos (los trackeados). | Alto | E-6.0-005 |
| Conformance absoluta inoperativa | Si el mecanismo actual (conformance absoluta con precedencia CRITICAL) se conecta directamente a CI con el estado de Fase 5 (163 Critical FN), siempre emitirá HARD_FAIL. | Alto | E-6.0-009, E-6.0-010 |

---

## 15. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR o NADR posterior deberá responder:

1. ¿La semántica de Continuous Verification es conformance absoluta contra el Sealed Oracle, regression relativa respecto de una referencia previa, o ambas evaluaciones independientes?
2. ¿Cómo se materializa el corpus canónico en CI sin alterar la identidad científica ni violar restricciones de distribución?
3. ¿Cuál es el punto de entrada normativo en CI: pytest marker, invocación directa del tooling, u otro boundary?
4. ¿Debe existir un estado BASELINE_INTEGRITY_FAILURE separado de EXECUTION_FAILURE?
5. ¿Qué perfil de ejecución requiere cada evento de CI (PR, merge, release, nightly)?
6. ¿La recalibración de thresholds o el re-baseline pertenecen a Fase 6 o a un ciclo gobernado posterior?
7. ¿Cómo se resuelve la tensión entre conformance absoluta (que siempre emitirá HARD_FAIL con 163 Critical FN) y la necesidad de un gate operativo en CI?
8. ¿El ADR_F17_BIS_06 es necesario como ADR de Fase, o basta con NADRs que extiendan los existentes?

---

## 16. CIERRE DEL HITO 6.0

Este HITO confirma que la capacidad de Continuous Verification definida por el ADR Maestro §6 **NO está implementada**. Existe infraestructura nominal (job CI, marker, env vars, verificación de inmutabilidad) pero NO existe conexión funcional entre esa infraestructura y la Scientific Baseline sellada por Fase 5. La frontera Fase 5 → Fase 6 está claramente definida por la arquitectura: Fase 5 construyó los artefactos, Fase 6 debe integrarlos en CI/CD.

El hallazgo de "Regression Gate Illusion" es análogo a la "Ilusión del Benchmark" de Fase 0 y constituye la evidencia forense fundacional sobre la cual debe construirse el ADR/NADR de Fase 6.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** Sí — evidencia completa, Decision Candidates identificados, sin decisiones resueltas.
**Verificación de cadena de gobernanza:** ADR Master → ADR_05 → HITO 6.0 → (futuro) ADR_06 / NADRs → Execution Plan.
**Contradicciones con HITOs previos:** Ninguna. Los HITOs de Fase 5 (5.0-5.4) documentaron la construcción de la baseline. Este HITO documenta la ausencia de integración en CI, que es consistente con la declaración de Fase 5 de que CI es responsabilidad de Fase 6.
**Decision Candidates generados:** DC-6.1, DC-6.2, DC-6.3, DC-6.4, DC-6.5, DC-6.6.
**Siguiente paso recomendado:** Redactar HITO 6.1 (Production Pipeline & Verification Subject) para auditar en detalle el SUT normativo y determinar cómo conectar el production pipeline al regression gate. Posteriormente, HITO 6.2 (Corpus Materialization), HITO 6.3 (CI & Operational Semantics), HITO 6.4 (Dependency Graph & Readiness). Con los 5 HITOs completados, evaluar si se requiere ADR_F17_BIS_06 o si bastan NADRs de extensión.

---

**Nota de Gobernanza:** Este HITO es read-only. No tiene autoridad normativa. No redefine reglas. Su propósito es documentar la evidencia forense de la frontera arquitectónica entre Fase 5 y Fase 6, y producir los Decision Candidates que el ADR/NADR de Fase 6 deberá resolver. La implementación de Continuous Verification corresponde exclusivamente al Execution Plan de Fase 6, gobernado por los NADRs correspondientes.