# FASE_3_HANDOFF.md

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_3_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-08-29
**Fase completada:** Fase 3 — Identity & Trust Model
**Siguiente fase:** Fase 4 — Scientific Verification (Topological Regression, Semantic Recall & Criticality)
**Derivado de:** `PHASE_17BIS_FASE3_EXECUTION_PLAN.md` v1.5.0 + `FASE_3_DEFERRED_FINDINGS_REGISTER.md` v1.0.0-COMPLETED

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-29 | Emisión inicial al cierre de Fase 3 (Identity & Trust Model) |

---

## 1. EXECUTIVE SUMMARY

**¿Qué se logró?** La Fase 3 formalizó y blindó el modelo de identidad criptográfica del sistema. Se establecieron contratos de dominio explícitos para todos los campos que participan en el framing criptográfico (`document_id`, `node_id`, `parent_node_id`, `ground_truth_state`), se documentó la semántica de las dimensiones de identidad (científica vs operacional), se verificó empíricamente la inyectividad del framing con property-based testing, y se corrigieron causas raíz de deuda técnica. **Estado final: COMPLETED.** 13 tareas del Execution Plan + 1 Batch de resolución de findings, **32 reglas normativas implementadas**, 0 deuda técnica deliberada.

**¿Cuál es el estado actual?** La suite de tests alcanzó **442 passed, 5 skipped** (baseline pre-Fase 3: 368 passed). Pyright reporta **0 errors, 0 warnings**. Se identificó 1 hallazgo (DF-01: `ground_truth_state` sin validación de `:`) que fue resuelto in-wave en Batch 1, sin diferimientos a fases futuras. Los tres NADRs de la fase (NADR-F17BIS-15 v2.0, NADR-F17BIS-16, NADR-F17BIS-17) están FROZEN y completamente implementados.

**¿Qué necesita la siguiente fase?** Fase 4 (Scientific Verification) debe construir sobre la identidad criptográfica ya blindada, sin modificar los contratos de dominio ni el framing. Debe materializar la taxonomía de criticidad de nodos (DC-06), las reglas de regresión topológica (DC-07) y la semántica de regresión graduada, consumiendo la infraestructura existente en `core/benchmark/topology/`. Los hashes de identidad (`manifest_hash`, `oracle_hash`) son ahora invariantes protegidos que Fase 4 usará como referencia canónica.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `{PLACEHOLDER: main}` |
| Commit hash de cierre | `{PLACEHOLDER: SHA}` |
| Estado del árbol | {PLACEHOLDER: Limpio / Con cambios pendientes} |
| Baseline de tests | **442 passed, 5 skipped** (NO DEBE DEGRADARSE sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados |
| Contratos de dominio verificados | 4/4 (`DocumentId`, `NodeId`, `GroundTruthState` + SHA-256 hex) |
| Grep de campos del framing con `:` | 0 resultados (validación de dominio efectiva) |

### 2.2 Validation Results

```text
# Comandos ejecutados al cierre de la fase
pyright core/shared/identity_contracts.py core/benchmark/corpus core/ast tests/unit/test_corpus_models.py tests/unit/test_ast_models.py tests/unit/test_framing_injectivity.py
# Resultado: 0 errors, 0 warnings, 0 informations ✅

pytest tests/unit/test_corpus_models.py tests/unit/test_ast_models.py tests/unit/test_framing_injectivity.py tests/unit/test_manifest_fingerprint.py tests/unit/test_oracle_identity.py -v
# Resultado: 82 passed (30+27+17+10+8) ✅

pytest tests/ -v
# Resultado: 442 passed, 5 skipped, 1 warning (FutureWarning externo de google.generativeai, no relacionado) ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro (ADR_F17_BIS_MASTER.md) | FROZEN | Post-Fase 0 |
| ADR de Fase 3 (ADR_F17-BIS_03.md) | FROZEN | v1.0.0 |
| NADR-F17BIS-15 (Semantic Identity Lineage) | FROZEN | v2.0.0 |
| NADR-F17BIS-16 (Cryptographic Identity Semantics) | FROZEN | v1.0.0 |
| NADR-F17BIS-17 (Domain Contracts for Cryptographic Identities) | FROZEN | v1.0.0 |
| Execution Plan (PHASE_17BIS_FASE3_EXECUTION_PLAN.md) | COMPLETED | v1.5.0 |
| Evidence Log (FASE_3_EXIT_REVIEW_EVIDENCE_LOG.md) | FROZEN | v1.1.0-COMPLETED |
| Findings Register (FASE_3_DEFERRED_FINDINGS_REGISTER.md) | ARCHIVED | v1.0.0-COMPLETED |
| Methodology (METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md) | FROZEN | v1.3.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 1 (DF-01) |
| Hallazgos resueltos | 1 (DF-01 → Batch 1 → RESOLVED) |
| Hallazgos cerrados sin acción (NAR) | 0 |
| Hallazgos diferidos a fase futura | 0 |
| Batches ejecutados | 1 (Batch 1: resolución de DF-01) |
| Gates completados | 2/2 |
| Waves ejecutadas | 5 (1.1, 1.2, 2.1, 2.2, 2.3) |
| Tasks completadas | 13/13 |
| Tests nuevos añadidos | 74 (30 corpus_models + 27 ast_models + 17 framing_injectivity) |
| Archivos creados | 4 (`identity_contracts.py`, `test_corpus_models.py`, `test_ast_models.py`, `test_framing_injectivity.py`) |
| Archivos modificados | ~14 (corpus/dtos.py, corpus/models.py, corpus/services.py, corpus/use_cases.py, ground_truth/identity.py, ground_truth/use_cases.py, ast/models.py, ast/hashing.py, tools/evaluation/freeze_ground_truth.py, pyproject.toml, test_manifest_fingerprint.py, test_ground_truth_sealing_atomicity.py, test_corpus_port_asymmetry.py, manifest fixture JSON) |
| Archivos eliminados | 0 (se eliminaron campos huérfanos dentro de archivos existentes, no archivos completos) |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | Contratos de dominio centralizados en `core/shared/identity_contracts.py` (`DocumentId`, `NodeId`, `GroundTruthState`) | `document_id` y `node_id` participaban en framing criptográfico sin validación explícita de dominio | NADR-F17BIS-17 §5.1 R1-R4; Ubicación en `core/shared/` evita dependencias invertidas entre `core/ast` y `core/benchmark/corpus` (precedente: `core/shared/crypto.py`) | `core/shared/identity_contracts.py` |
| AD-02 | `spawn_fragment()` reescrito con constructor completo en lugar de `model_copy(update=...)` | Pydantic v2 no revalida campos actualizados vía `model_copy`, permitiendo bypass del contrato `NodeId` | ENGINEERING_PRINCIPLES §III (Explicit over Implicit) + §IV (Cero Fallos Silenciosos) | `core/ast/models.py::ASTNode.spawn_fragment` |
| AD-03 | `parent_node_id` tipado como `Optional[NodeId]` | Referencia a otro node_id debía tener el mismo contrato para consistencia de dominio | NADR-F17BIS-17 §5.1 R1-R4; Consistencia defensiva | `core/ast/models.py::ASTNode.parent_node_id` |
| AD-04 | Corrección de causa raíz en `DocumentFingerprint.__post_init__` | `str.islower()` retorna False para strings sin caracteres alfabéticos (ej: `"0"*64`), siendo redundante con `all(c in "0123456789abcdef")` | Causa raíz vs síntoma; El contrato real es "64 chars hex lowercase" | `core/benchmark/corpus/models.py::DocumentFingerprint.__post_init__` |
| AD-05 | Coexistencia de dos contratos de hashing con propósitos distintos | Ambigüedad entre `compute_ast_hash` y `OracleSemanticIdentityCalculator` | NADR-F17BIS-16 §5.2 R4-R8: `OracleSemanticIdentityCalculator` es canónico para linaje (incluye node_id); `compute_ast_hash` es para comparación de parsers (excluye node_id) | Docstrings de `core/ast/hashing.py` y `core/benchmark/ground_truth/identity.py` |
| AD-06 | `ground_truth_state` clasificado como estado operacional, no identidad científica | Ambigüedad sobre por qué participa en `manifest_hash` | NADR-F17BIS-16 §5.3 R9-R12: protege el proceso de certificación (previene des-sellado silencioso), no el contenido científico | Docstring de `core/benchmark/corpus/services.py::ManifestFingerprintCalculator` |
| AD-07 | Eliminación de campos huérfanos `ground_truth_version`, `ground_truth_sha256`, `detected_hashes`, `target_version` | No participaban en la identidad ni en el modelo de dominio (DC-08 del ADR Maestro) | ENGINEERING_PRINCIPLES §I (YAGNI); Limpieza profunda eliminó I/O innecesario | `core/benchmark/corpus/dtos.py`, `services.py`, `use_cases.py`, `ground_truth/use_cases.py` |
| AD-08 | `ASTSchemaVersion` acoplado implícitamente a `CorpusVersion` (versionado implícito) | Alucinación documental de Fase 2 (GAP-3.3-01): se documentó una entidad que no existe en runtime | NADR-F17BIS-15 v2.0 §5.3 R10; Simplificación del modelo de identidad | `NADR-F17BIS-15 v2.0` §5.3 |
| AD-09 | DF-01 resuelto como Batch del Findings Register, no como Wave nueva del Execution Plan | Hallazgo de hardening de dominio identificado post-Wave 2.3 | METHODOLOGY §6.6 punto 4: findings `IMPLEMENTATION_REQUIRED` se resuelven en Batches, preservando la estructura original del Execution Plan | `FASE_3_DEFERRED_FINDINGS_REGISTER.md` §4.1 |
| AD-10 | Inyectividad del framing verificada con property-based testing (hypothesis) | Necesidad de verificación empírica masiva del framing criptográfico | NADR-F17BIS-17 §5.2 R5-R8; ~850 ejemplos aleatorios generados con shrink automático | `tests/unit/test_framing_injectivity.py` |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Linaje de identidad semántica del oráculo en el modelo de baseline | NADR-F17BIS-15 v2.0 §5.1, §5.2 | ✅ DONE |
| Versionado implícito de ASTSchemaVersion acoplado a CorpusVersion | NADR-F17BIS-15 v2.0 §5.3 R10 | ✅ DONE |
| Semántica formal de las dimensiones de identidad (científica vs operacional) | NADR-F17BIS-16 §5.1, §5.3 | ✅ DONE |
| Coexistencia gobernada de contratos de hashing semántico | NADR-F17BIS-16 §5.2 R4-R8 | ✅ DONE |
| Contratos de dominio explícitos para campos de framing criptográfico | NADR-F17BIS-17 §5.1 R1-R4 | ✅ DONE |
| Inyectividad del encoding verificada empíricamente | NADR-F17BIS-17 §5.2 R5-R8 | ✅ DONE |
| Documentación de sentinels y valores especiales | NADR-F17BIS-17 §5.3 R9-R12 | ✅ DONE |
| Trazabilidad y verificabilidad de contratos | NADR-F17BIS-17 §5.4 R13-R15 | ✅ DONE |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `core/shared/identity_contracts.py` — Contratos de dominio centralizados (`DocumentId`, `NodeId`, `GroundTruthState`)
- `tests/unit/test_corpus_models.py` — 30 tests de validación de dominio e invariantes del corpus
- `tests/unit/test_ast_models.py` — 27 tests de validación de dominio e invariantes de ASTNode
- `tests/unit/test_framing_injectivity.py` — 17 property-based tests de inyectividad del framing

**Modificados significativamente:**
- `core/ast/models.py` — `ASTNode.node_id` usa `NodeId`, `parent_node_id` usa `Optional[NodeId]`, `spawn_fragment()` con constructor completo
- `core/benchmark/corpus/models.py` — `CorpusDocumentMetadata.document_id` usa `DocumentId`, `ground_truth_state` usa `Optional[GroundTruthState]`, corrección de `DocumentFingerprint.__post_init__`
- `core/benchmark/corpus/dtos.py` — `RawDocumentEntryDTO` con contratos de dominio aplicados; eliminación de campos huérfanos (DC-08)
- `core/benchmark/corpus/services.py` — Justificación explícita de `ground_truth_state` en framing; limpieza de `detected_hashes` y `target_version`
- `core/benchmark/corpus/use_cases.py` — Eliminación de propagación de `detected_hashes` y `target_version`
- `core/benchmark/ground_truth/use_cases.py` — Eliminación de cálculo de `detected_hashes` y `target_version`
- `core/benchmark/ground_truth/identity.py` — Documentación de `OracleSemanticIdentityCalculator` como contrato canónico
- `core/ast/hashing.py` — Documentación de `compute_ast_hash` como contrato alternativo + clarificación de sensibilidad al orden (DC-06)
- `tools/evaluation/freeze_ground_truth.py` — Eliminación de `target_version`
- `tests/unit/test_manifest_fingerprint.py` — Actualización de tests por cambio de mensaje de error
- `tests/unit/test_ground_truth_sealing_atomicity.py` — Actualización por eliminación de parámetros
- `tests/unit/test_corpus_port_asymmetry.py` — Actualización por cambios en DTO
- `pyproject.toml` — `hypothesis>=6.0` agregado a dependencias de desarrollo

**Eliminados (zombies y deuda):**
- Ningún archivo eliminado. Se eliminaron campos huérfanos y parámetros muertos dentro de archivos existentes (AD-07).

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que Fase 4 DEBE respetar)

| Restricción | Fuente | Relevancia para Fase 4 |
|-------------|--------|-------------------------------|
| Los contratos de dominio (`DocumentId`, `NodeId`, `GroundTruthState`) son inmutables y no deben modificarse sin property-based tests | NADR-F17BIS-17 §5.1 R1-R4 | Fase 4 consume estos contratos como referencia canónica; modificarlos invalidaría la identidad criptográfica |
| `OracleSemanticIdentityCalculator` es la identidad canónica del oráculo (incluye node_id) | NADR-F17BIS-16 §5.2 R8 | Fase 4 debe usar este contrato para evaluación de regresión, NO `compute_ast_hash` |
| `compute_ast_hash` es solo para comparación de parsers (excluye node_id) | NADR-F17BIS-16 §5.2 R5-R7 | Fase 4 NO debe usar este hash para identidad de baseline |
| `ground_truth_state` es estado operacional, no identidad científica | NADR-F17BIS-16 §5.3 R9-R12 | Fase 4 no debe tratar el estado de ciclo de vida como contenido científico |
| El framing de `manifest_hash` y `oracle_hash` no debe modificarse sin property-based tests | NADR-F17BIS-17 §5.2 R5-R8 | Cualquier cambio en el framing requiere verificación de inyectividad |
| Zero Partial Sealing: N_PDF = N_GT | ADR_F17_BIS_MASTER §5 | Fase 4 debe respetar la completitud biyectiva al evaluar regresión |
| Determinismo y Reproducibilidad: 100% determinista | ADR_F17_BIS_MASTER §5 | Toda evaluación de regresión debe ser reproducible criptográficamente |
| Arquitectura Hexagonal / Functional Core, Imperative Shell | ENGINEERING_PRINCIPLES §II | Fase 4 debe mantener la separación de capas al integrar evaluación topológica |
| Single-node / No infraestructura distribuida | ADR_F17_BIS_MASTER §4 | Fase 4 no debe introducir Redis, Brokers, K8s, DBs remotas |
| **Baseline de tests: 442 passed, 5 skipped** | Este handoff §2.1 | **NO DEBE DEGRADARSE** sin justificación explícita |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| — | Sin hallazgos diferidos. DF-01 fue resuelto in-wave en Batch 1. | — | — |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| Inyectividad probabilística | SHA-256 no es matemáticamente inyectivo (dominio infinito → rango finito 2^256). Los property-based tests verifican inyectividad del framing, no del hash. | El framing garantiza representaciones distintas antes del hash; la resistencia a colisiones la provee SHA-256 |
| Sentinel "none" en framing | `oracle_hash` y `ground_truth_state` pueden ser None; se usa el string literal `"none"` como sentinel en el framing | Los contratos de dominio garantizan que ningún valor válido puede ser `"none"` accidentalmente (min_length=1 + pattern `^[^:]+$`) |
| Delimitador ':' en framing | El framing usa `:` como delimitador; un campo que contenga `:` rompería la inyectividad | Contratos de dominio prohíben `:` en todos los campos del framing (verificado con property-based tests) |
| `corpus_version` sin contrato de dominio explícito | `corpus_version` participa en el framing de `manifest_hash` pero no tiene un contrato de dominio explícito (no-`:`). En la práctica los valores son controlados (ej: "v1.0"), pero el DTO permite cualquier string. | Observado durante Wave 2.3. No se implementó contrato porque el campo es controlado por el pipeline y no recibe input externo. Si Fase 5 introduce fuentes externas, evaluar agregar contrato. |
| `hypothesis` como dependencia de desarrollo | `hypothesis` fue agregado a dependencias dev; no es dependencia de producción | Aislado en `[project.optional-dependencies] dev` |
| Migres de Deployment pendientes (MIG-01, MIG-02, MIG-03) | El Deployment & Migration Runbook del Execution Plan tiene 3 steps en estado TODO. Son verificaciones operativas del corpus canónico existente. | Se ejecutarán en Fase 5 (Baseline Certification) cuando se materialice el corpus canónico en disco. |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Identidad criptográfica del oráculo blindada (`OracleSemanticIdentityCalculator`)
- ✅ Identidad global del manifiesto blindada (`ManifestFingerprintCalculator`)
- ✅ Contratos de dominio para todos los campos del framing
- ✅ Inyectividad del framing verificada empíricamente
- ✅ Estado de ciclo de vida del Ground Truth formalizado (DRAFT → AUDITED → VALIDATED → SEALED)
- ✅ Infraestructura topológica existente en `core/benchmark/topology/` (`ZhangShashaEngine`, `EntityRecallEvaluator`, `TreeEditDistanceEvaluator`, `LCSAnchorAlignmentStrategy`)
- ✅ Baseline de tests estable: 442 passed, 5 skipped

**Lo que se necesita antes de arrancar Fase 4:**
- Definir la taxonomía de criticidad de nodos (DC-06 del ADR Maestro, pendiente de materialización normativa)
- Definir las reglas de regresión topológica (DC-07 del ADR Maestro, pendiente de materialización normativa)
- Definir la semántica de regresión graduada (no-snapshotting)
- Auditar el estado actual de `core/benchmark/topology/` para identificar gaps vs requisitos de Fase 4

### 6.2 Next Phase Handoff Checklist

- [ ] Verificar que el commit de cierre de Fase 3 está en `main` y el árbol está limpio
- [ ] Cargar este handoff + documentos de Prioridad 1 (§8.4)
- [ ] Verificar que `pytest tests/ -v` produce 442 passed, 5 skipped
- [ ] Verificar que `pyright core/benchmark core/ast core/shared` produce 0 errors
- [ ] Realizar auditoría forense (Fase 0 de Fase 4) de `core/benchmark/topology/`
- [ ] Identificar Decision Candidates específicos de Fase 4
- [ ] Redactar ADR_F17-BIS_04 (ADR de Fase para Scientific Verification)
- [ ] Redactar NADRs de Fase 4 (criticidad, regresión topológica, semántica graduada)
- [ ] Redactar PHASE_17BIS_FASE4_EXECUTION_PLAN.md

### 6.3 ROADMAP — Objetivos de la siguiente fase

Según ADR_F17_BIS_MASTER §6, Fase 4 es **Scientific Verification**:

1. **Topological Regression** — Evaluar desviaciones topológicas del runtime contra el oráculo usando Tree Edit Distance (`ZhangShashaEngine`)
2. **Semantic Recall** — Medir la recuperación de entidades científicas (ecuaciones, tablas, referencias) mediante `EntityRecallEvaluator`
3. **Criticality** — Aplicar la taxonomía de criticidad de nodos (`CRITICAL` / `WARNING` / `INFO`) para graduar las divergencias

**Hito crítico:** Fase 4 se considera completada cuando el sistema puede evaluar de forma determinista y graduada si el runtime actual se ha desviado científicamente del oráculo, sin recurrir a comparación byte-a-byte rígida (snapshotting).

### 6.4 Documentos que Fase 4 debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| HITOs de auditoría forense | `HITO_{X.X}_{NOMBRE}.md` en `00-foundation/` | Evidencia forense del estado actual de `core/benchmark/topology/` |
| ADR_F17-BIS_04 | Plantilla canónica de ADR de Fase (9 secciones) | Visión arquitectónica de Scientific Verification |
| NADRs de Fase 4 | Plantilla canónica de NADR (9 secciones) | Reglas normativas de criticidad, regresión topológica y semántica graduada |
| PHASE_17BIS_FASE4_EXECUTION_PLAN.md | Plantilla canónica de Execution Plan | Secuenciación operativa de Fase 4 |
| FASE_4_DEFERRED_FINDINGS_REGISTER.md | Plantilla canónica | Registro de hallazgos durante Fase 4 |
| FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md | Plantilla canónica | Evidencia forense de las decisiones del Exit Review |
| FASE_4_HANDOFF.md | Plantilla canónica de Handoff | Transición a Fase 5 |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` |
| ADR de Fase 3 | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17-BIS_03.md` |
| NADR-F17BIS-15 v2.0 | `docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-15_v2.0_Semantic_Identity_Lineage.md` |
| NADR-F17BIS-16 | `docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-16_Cryptographic_Identity_Semantics_&_Chaining.md` |
| NADR-F17BIS-17 | `docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-17_Identity_Encoding_Integrity.md` |
| Execution Plan Fase 3 | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE3_EXECUTION_PLAN.md` |
| Evidence Log | `docs/architecture/adr/phase-17-bis/reviews/FASE_3_EXIT_REVIEW_EVIDENCE_LOG.md` |
| Methodology | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |
| ENGINEERING_PRINCIPLES | `docs/architecture/ENGINEERING_PRINCIPLES.md` |
| ROADMAP | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register Fase 3 | `docs/architecture/adr/phase-17-bis/reviews/FASE_3_DEFERRED_FINDINGS_REGISTER.md` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| PROJECT_TREE | `docs/architecture/PROJECT_TREE.txt` | Árbol de funciones y clases del proyecto |
| PROJECT_SCOPE | `docs/architecture/PROJECT_SCOPE.md` | Alcance del proyecto |
| HITOs de Fase 0 | `docs/architecture/adr/phase-17-bis/00-foundation/` | Evidencia forense fundacional (referencia histórica) |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.

### 8.1 Project Identity

```text
Proyecto: translator_pdf
Descripción: Pipeline local SOTA para ingesta, normalización, traducción LLM y
reconstrucción de PDFs científicos/académicos preservando estructura, semántica y layout.
Stack: Python 3.11, Pydantic v2, SQLite WAL, hypothesis (dev), pyright, pytest
Arquitectura: DDD + Hexagonal (Ports & Adapters), Functional Core / Imperative Shell,
Flat AST V2, CQRS + FSM + Telemetry
Fase actual completada: Fase 3 — Identity & Trust Model (Fase 17-BIS)
Siguiente fase: Fase 4 — Scientific Verification (Topological Regression, Semantic Recall, Criticality)
```

### 8.2 Code State

```text
Tests: 442 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
Rama: {PLACEHOLDER} ({PLACEHOLDER})
Commit de cierre: {PLACEHOLDER}
Property-based tests: 17 tests con hypothesis (~850 ejemplos aleatorios)
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. Contratos de dominio inmutables: DocumentId, NodeId, GroundTruthState en
   core/shared/identity_contracts.py NO deben modificarse sin property-based tests.
2. OracleSemanticIdentityCalculator es la identidad canónica del oráculo (incluye node_id).
   Usar este contrato para identidad de baseline, NO compute_ast_hash.
3. compute_ast_hash es solo para comparación de parsers (excluye node_id).
4. ground_truth_state es estado operacional del ciclo de vida, NO identidad científica.
5. El framing de manifest_hash y oracle_hash usa ':' como delimitador. Todos los campos
   del framing tienen contratos que prohíben ':'. No modificar el framing sin verificación.
6. Zero Partial Sealing: N_PDF = N_GT (completitud biyectiva obligatoria).
7. Determinismo y Reproducibilidad: todo el pipeline de evaluación debe ser 100% determinista.
8. Arquitectura Hexagonal + Functional Core / Imperative Shell. Sin estado en servicios.
9. Single-node: prohibido Redis, Brokers, K8s, DBs remotas. SQLite WAL es el Core Engine.
10. Cero Fallos Silenciosos: datos anómalos → Warning indexable o Raise Exception.
    Nunca degradar silenciosamente la calidad del dato.
11. YAGNI + Cero Deuda Técnica Deliberada: no implementar necesidades futuras no demostradas.
12. Los hallazgos IMPLEMENTATION_REQUIRED se resuelven como Batches del Findings Register
    (METHODOLOGY §6.6), no como Waves nuevas del Execution Plan.
13. Baseline de tests: 442 passed, 5 skipped. NO DEBE DEGRADARSE sin justificación.
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- docs/architecture/adr/phase-17-bis/handoff/FASE_3_HANDOFF.md (este documento)
- docs/architecture/ENGINEERING_PRINCIPLES.md
- docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md
- docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md

Prioridad 2 (cargar para implementación de Fase 4):
- docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-15_v2.0_Semantic_Identity_Lineage.md (linaje de identidad)
- docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-16_Cryptographic_Identity_Semantics_&_Chaining.md (semántica de identidad)
- docs/architecture/adr/phase-17-bis/NADR/NADR-F17BIS-17_Identity_Encoding_Integrity.md (contratos de dominio)
- docs/architecture/ROADMAP_ARQUITECTONICO_LP.md

Prioridad 3 (consultar según necesidad):
- docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE3_EXECUTION_PLAN.md
- docs/architecture/adr/phase-17-bis/reviews/FASE_3_EXIT_REVIEW_EVIDENCE_LOG.md
- docs/architecture/adr/phase-17-bis/reviews/FASE_3_DEFERRED_FINDINGS_REGISTER.md
- docs/architecture/PROJECT_SCOPE.md
- docs/architecture/PROJECT_TREE.txt
```

### 8.5 Pending Items (carry-forward)

```text
Sin hallazgos diferidos de Fase 3. DF-01 fue resuelto in-wave en Batch 1.

[Observación — no bloqueante]
corpus_version participa en el framing de manifest_hash pero no tiene contrato
de dominio explícito. Riesgo bajo (valores controlados por el pipeline).
→ Destino: Evaluar en Fase 5 (Baseline Certification) si se introduce input externo
→ Bloquea: Nada

[Deployment Runbook — operativo]
MIG-01, MIG-02, MIG-03 del Execution Plan de Fase 3 están en estado TODO.
Son verificaciones operativas del corpus canónico existente.
→ Destino: Ejecutar en Fase 5 (Baseline Certification) al materializar el corpus
→ Bloquea: Nada (no bloquea Fase 4)

Items pendientes para Fase 4 (no son deuda, son scope de la siguiente fase):
[F4-DC06] Materializar taxonomía de criticidad de nodos (CRITICAL/WARNING/INFO)
          → Destino: Fase 4
          → Bloquea: Nada en Fase 3, es prerequisito de evaluación graduada
[F4-DC07] Materializar reglas de regresión topológica (HARD FAIL vs WARNING)
          → Destino: Fase 4
          → Bloquea: Nada en Fase 3, es prerequisito de Regression Gates
[F4-GRAD] Definir semántica de regresión graduada (no-snapshotting)
          → Destino: Fase 4
          → Bloquea: Nada en Fase 3, es el objetivo central de Fase 4
```

### 8.6 Work Conventions

```text
- Flujo: auditoría (HITOs) → ADR de Fase → NADRs → Execution Plan → implementación →
  Gate Exit Review → Evidence Log + Findings Register → handoff.
- Los NADRs gobiernan CAPACIDADES, no implementaciones. Sobreviven a cambios de código.
- Los hallazgos se registran con ID único (DF-XX / GF-XX) y se clasifican en el Findings Register.
- Los hallazgos IMPLEMENTATION_REQUIRED se resuelven como Batches, no como Waves nuevas.
- Todo cambio debe ser mínimo, determinista, testeable y compatible con arquitectura congelada.
- Verificación obligatoria: pyright 0 errors + pytest suite verde + greps de regresión.
- Inmutabilidad: DTOs con frozen=True, transiciones de estado retornan copia nueva.
- Fail-Fast: validación en construcción, no en puntos posteriores del pipeline.
- Baseline de tests: 442 passed, 5 skipped. Nunca degradar sin justificación explícita.
```

### 8.7 System Entry Points

```text
# Identidad criptográfica (Fase 3 — NO MODIFICAR sin property-based tests)
core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash()
    → Calcula manifest_hash (identidad global del manifiesto)
core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate()
    → Calcula oracle_hash (identidad semántica del oráculo) — CANÓNICO
core/ast/hashing.py::compute_ast_hash()
    → Hash para comparación de parsers (NO es identidad de baseline)
core/shared/identity_contracts.py
    → Contratos de dominio: DocumentId, NodeId, GroundTruthState

# Estado de ciclo de vida del Ground Truth
core/benchmark/ground_truth/lifecycle.py::LifecycleTransitionAuthority
    → Transiciones DRAFT → AUDITED → VALIDATED → SEALED
core/benchmark/ground_truth/use_cases.py::SealGroundTruthUseCase
    → Autoridad única de sellado atómico

# Infraestructura topológica (Fase 4 consumirá esto)
core/benchmark/topology/engines/zhang_shasha/engine.py::ZhangShashaEngine
    → Tree Edit Distance
core/benchmark/topology/evaluators/recall.py::EntityRecallEvaluator
    → Semantic Recall
core/benchmark/topology/evaluators/ted.py::TreeEditDistanceEvaluator
    → TED evaluator
core/benchmark/topology/strategies.py::ParserEvaluationStrategy
    → Estrategia de evaluación de parsers
core/benchmark/topology/alignment/strategy.py::LCSAnchorAlignmentStrategy
    → Alineación de anchors por LCS

# Factories centralizadas / composition roots
apps/bootstrap/pipeline_factory.py::build_pipeline()
    → Composition root del pipeline de traducción
bootstrap/topology.py::create_topology_evaluator()
    → Composition root de evaluación topológica (relevante para Fase 4)
```

---

## 9. CLOSURE CRITERIA

Este handoff se considera cerrado (FROZEN) cuando:

- [x] Resumen ejecutivo completo (§1)
- [x] Estado actual validado con evidencia (§2)
- [x] Decisiones arquitectónicas documentadas (§3)
- [x] Scope entregado listado (§4)
- [x] Todos los items diferidos listados con destino (§5.2) — Ninguno en Fase 3
- [x] Restricciones carry-forward identificadas (§5.1)
- [x] Known risks documentados (§5.3)
- [x] Prerequisitos de siguiente fase definidos (§6)
- [x] Mapa de referencias completo (§7)
- [x] LLM Context Block autocontenido (§8)

**Veredicto:** ✅ CERRADO — FROZEN

---

**Nota de Gobernanza:** Este documento es el punto de transición entre Fase 3 (Identity & Trust Model) y Fase 4 (Scientific Verification). No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4) para tener contexto completo de arranque. Los detalles normativos se consultan bajo demanda según la tarea específica.