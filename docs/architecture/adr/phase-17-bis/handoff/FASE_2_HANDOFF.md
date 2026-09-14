# FASE_2_HANDOFF.md

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_2_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-08-25
**Fase completada:** Fase 2 — Scientific Baseline Domain (Ontología, Validez, Autoridad, Identidad Semántica del Oráculo)
**Siguiente fase:** Fase 3 — Identity & Trust Model (Hashes deterministas, linaje y encadenamiento criptográfico)
**Derivado de:** `PHASE_17BIS_FASE2_EXECUTION_PLAN.md` v1.9.0 + `FASE_2_DEFERRED_FINDINGS_REGISTER.md` v2.0.0

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-25 | Emisión inicial al cierre de Fase 2 |

---

## 1. EXECUTIVE SUMMARY

**¿Qué se logró?** La Fase 2 (Scientific Baseline Domain) está **COMPLETED** con 4 Gates PASS y **37/37 reglas** de NADR-F17BIS-12..15 materializadas. Se formalizó la ontología del Ground Truth como entidad de dominio con ciclo de vida gobernado, se materializó el contrato de validez estructural con completitud biyectiva (Zero Partial Sealing), se consolidó una autoridad única de sellado con asimetría de puertos, y se portó la identidad semántica del oráculo como linaje de primera clase encadenado en la firma global del manifiesto.

**¿Cuál es el estado actual?** El repositorio está limpio, con 368 tests passed y 5 skipped, 0 errors de Pyright. Se analizaron 22 hallazgos: 17 resueltos (16 RESOLVED + 1 RESOLVED — DELETE [E-2.0-03]), 1 DOCUMENTED (DF-19, migración de formato de hash), 3 RECLASSIFIED_FUTURE_PHASE (DF-01, DF-16, DF-18) y 1 ACCEPTED_LIMITATION (DF-04). No hay hallazgos `REVIEW_REQUIRED` ni `IMPLEMENTATION_REQUIRED` pendientes.

**¿Qué necesita la siguiente fase?** La Fase 3 (Identity & Trust Model) requiere construir el encadenamiento criptográfico global $H_{baseline}$ sobre la ontología ya formalizada. Los prerequisitos críticos están listos: `OracleSemanticIdentityCalculator` para $H_{semantic}$, asimetría de puertos Reader/Writer, autoridad única de sellado en `SealGroundTruthUseCase`, y el formato extendido del hash del manifiesto (6 dimensiones). Restricción carry-forward principal: la separación de identidades (Integridad ≠ Identidad ≠ Regresión) y el uso de strings genéricos para el estado del ciclo de vida (no enums en el bounded context `corpus`).

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` |
| Commit hash de cierre | `0fbe2b310a4cfaf295d66e730fe7d529ae8d25ec` |
| Estado del árbol | Limpio (commit `0fbe2b3` aplicado; 2 directorios untracked: `handoff/` pendiente de commit, `tools/archive/` verificar `.gitignore`) |
| Baseline de tests | **368 passed, 5 skipped** (no debe degradarse sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados |
| `.gitignore` | Actualizado con cachés de herramientas de verificación + `tests/corpus/benchmark_v1/` |

### 2.2 Validation Results

```bash
# Comandos ejecutados al cierre de la fase
pyright core/benchmark/corpus core/benchmark/ground_truth    # 0 errors, 0 warnings ✅
pytest tests/unit/                                           # 368 passed, 5 skipped ✅
pytest tests/unit/test_oracle_identity.py -v                 # 8 passed ✅
pytest tests/unit/test_manifest_fingerprint.py -v            # 10 passed ✅
pytest tests/unit/test_ground_truth_sealing_atomicity.py -v  # 7 passed ✅
pytest -q                                                    # 368 passed, 5 skipped ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro (`ADR_F17_BIS_MASTER.md`) | FROZEN | Post-Phase 0 |
| ADR de Fase 2 (`ADR_F17_BIS_02.md`) | FROZEN | v1.0 |
| NADRs (4 documentos: NADR-F17BIS-12..15) | FROZEN | v1.0 |
| Execution Plan (`PHASE_17BIS_FASE2_EXECUTION_PLAN.md`) | FROZEN | v1.9.0 |
| Evidence Log (`FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md`) | FROZEN | v1.0.0 |
| Findings Register (`FASE_2_DEFERRED_FINDINGS_REGISTER.md`) | ARCHIVED | v2.0.0 |
| Methodology (`METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`) | FROZEN | v1.3.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Gates completados | 4/4 (NADR-12, NADR-13, NADR-14, NADR-15) |
| Rules materializadas | 37/37 |
| Waves completadas | 12/12 |
| Tasks DONE | 37/37 |
| Hallazgos analizados | 22 |
| Hallazgos resueltos | 17 (16 RESOLVED + 1 RESOLVED — DELETE [E-2.0-03]) |
| Hallazgos documentados con acción operativa | 1 (DF-19, migración Fase 5) |
| Hallazgos cerrados sin acción (NAR) | 0 |
| Hallazgos diferidos a fase futura | 3 (DF-01, DF-16, DF-18) |
| Hallazgos aceptados como limitación | 1 (DF-04) |
| Archivos eliminados | 1 (ManifestGroundTruthUpdater en services.py) |
| Archivos creados | 16 |
| Archivos modificados | 21 |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | GroundTruth es Entity con `document_id` como identidad propia | DF-02: ¿Entity o Value Object? | DDD: agregado separado de `CorpusManifest`, relación por referencia | `core/benchmark/ground_truth/models.py` |
| AD-02 | Campo `state` eliminado; el tipo mismo determina el estado | DF-03: tipos disjuntos vs campo state | NADR-12 §5.1 R2 (disyunción ontológica a nivel de tipos) | `GroundTruthDraft`, `SealedOracle` |
| AD-03 | AUDITED/VALIDATED son sub-estados del Draft (`DraftSubState`) | DF-06: 4 estados vs 2 tipos | NADR-12 §5.2 R4; evita multiplicar tipos innecesariamente | `core/benchmark/ground_truth/models.py` |
| AD-04 | `sub_state` es efímero en memoria (Opción 3) | DF-12: ¿persistir o no el sub_state? | ADR_F17_BIS_02 §6 (No-Inferencia de Estado); fábrica trust-based | `hydrate_ground_truth()` |
| AD-05 | Reporte agregado en sellado (no short-circuit) | Decisión inline Wave 2.3 | ENGINEERING_PRINCIPLES §IV (observabilidad científica completa) | `BaselineContractError` compuesto |
| AD-06 | Opción D para persistencia del estado SEALED | DF-13: ¿archivo separado o campo en manifiesto? | Fuente de verdad única, coherencia con NADR-15, no es inferencia | `RawDocumentEntryDTO.ground_truth_state` |
| AD-07 | Segregación de puertos Reader/Writer | Gate 3 Wave 3.1 | NADR-14 §5.1 R1-R3; asimetría curaduría/runtime | `CorpusManifestReaderPort`, `CorpusManifestWriterPort` |
| AD-08 | Autoridad única de sellado en `SealGroundTruthUseCase` | Gate 3 Wave 3.2 | NADR-14 §5.2 R4-R6; eliminación de `ManifestGroundTruthUpdater` (Zero Debt) | `core/benchmark/ground_truth/use_cases.py` |
| AD-09 | `OracleSemanticIdentityCalculator` con 4 dimensiones semánticas | Gate 4 Wave 4.1 | NADR-15 §5.1 R1-R3; insensible a metadata física | `core/benchmark/ground_truth/identity.py` |
| AD-10 | Formato de hash del manifiesto extendido (4 → 6 dimensiones) | Gate 4 Wave 4.2 | NADR-15 §5.3 R9; protección criptográfica de identidad semántica y estado | `ManifestFingerprintCalculator.compute_hash()` |
| AD-11 | Strings genéricos para estado del ciclo de vida | Gate 3 + Gate 4 | Separación de bounded contexts: `corpus` no importa `GroundTruthLifecycleState` | `ManifestLineageSealer` recibe `Dict[str, str]` |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Ontología del oráculo: tipos disjuntos, ciclo de vida gobernado, inmutabilidad | NADR-F17BIS-12 | ✅ DONE (9/9 reglas) |
| Validez estructural del oráculo y completitud biyectiva de la baseline | NADR-F17BIS-13 | ✅ DONE (10/10 reglas) |
| Asimetría de puertos curaduría/runtime y autoridad única de sellado | NADR-F17BIS-14 | ✅ DONE (9/9 reglas) |
| Identidad semántica del oráculo y encadenamiento en firma global | NADR-F17BIS-15 | ✅ DONE (9/9 reglas) |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `core/benchmark/ground_truth/models.py` — Entidades `GroundTruthDraft`, `SealedOracle`, fábrica `hydrate_ground_truth`
- `core/benchmark/ground_truth/lifecycle.py` — `LifecycleTransitionAuthority` con 5 transiciones válidas
- `core/benchmark/ground_truth/validity.py` — `OracleValidityContract` con 4 invariantes
- `core/benchmark/ground_truth/completeness.py` — `BaselineCompletenessVerifier` (biyección bidireccional)
- `core/benchmark/ground_truth/identity.py` — `OracleSemanticIdentityCalculator` ($H_{semantic}$)
- `tests/unit/test_ground_truth_models.py` — Tests de ontología
- `tests/unit/test_ground_truth_lifecycle.py` — Tests de ciclo de vida
- `tests/unit/test_ground_truth_validity.py` — Tests de validez estructural
- `tests/unit/test_ground_truth_completeness.py` — Tests de completitud
- `tests/unit/test_ground_truth_sealing_atomicity.py` — Tests de atomicidad y autoridad única
- `tests/unit/test_ground_truth_sealed_protection.py` — Tests de protección contra sobrescritura
- `tests/unit/test_corpus_port_asymmetry.py` — Tests de asimetría de puertos
- `tests/unit/test_oracle_identity.py` — Tests de identidad semántica
- `tests/unit/test_manifest_fingerprint.py` — Tests de fingerprint y regresión DF-19
- `docs/architecture/adr/phase-17-bis/reviews/FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md` — Evidence Log FROZEN
- `docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md` — Findings Register ARCHIVED

**Modificados significativamente:**
- `core/benchmark/ground_truth/use_cases.py` — `SealGroundTruthUseCase` como autoridad única; `GenerateGoldenDraftUseCase` con verificación de sellado
- `core/benchmark/ground_truth/errors.py` — Taxonomía completa: `BaselineContractError`, `SealedOracleOverwriteError`
- `core/benchmark/corpus/dtos.py` — `RawDocumentEntryDTO` con `oracle_hash` y `ground_truth_state`
- `core/benchmark/corpus/models.py` — `CorpusDocumentMetadata` con dimensiones de identidad
- `core/benchmark/corpus/services.py` — `ManifestFingerprintCalculator` (formato 6 dimensiones) + `ManifestLineageSealer` (propagación)
- `core/benchmark/corpus/use_cases.py` — Bootstrap y Load propagan nuevas dimensiones
- `core/benchmark/corpus/ports.py` — Segregación Reader/Writer
- `infra/fs/corpus_repository.py` — Fail-fast + escritura atómica
- `tools/evaluation/freeze_ground_truth.py` — Orquestación del ciclo de vida en memoria

**Eliminados (zombies y deuda):**
- `ManifestGroundTruthUpdater` en `core/benchmark/ground_truth/services.py` — Duplicado línea por línea de `ManifestLineageSealer`, cero consumidores (Zero Debt, E-2.0-03)

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para Fase 3 |
|-------------|--------|------------------------|
| **Separación de Identidades** (Integridad ≠ Identidad ≠ Regresión) | ADR Maestro §3 | Fase 3 construye el encadenamiento $H_{baseline}$; debe mantener las dimensiones separadas |
| **Zero Partial Sealing** | ADR Maestro §5 | El encadenamiento criptográfico debe preservar la biyección completa |
| **Determinismo y Reproducibilidad** | ADR Maestro §5 | Todo hash debe ser 100% determinista |
| **Desacoplamiento de Identidades** | ADR Maestro §5 | AST Schema Version, Corpus Version e Identity Hash deben permanecer diferenciados |
| **No-Inferencia de Estado** | ADR_F17_BIS_02 §6 | El estado del oráculo nunca se deduce de campos incidentales |
| **Asimetría de puertos** | NADR-14 §5.1 | Fase 3 debe respetar la segregación Reader/Writer existente |
| **Strings genéricos para estado** | Decisión AD-11 | El bounded context `corpus` NO debe importar enums de `ground_truth` |
| **Inmutabilidad estricta** | ENGINEERING_PRINCIPLES §II | DTOs `frozen=True`, cero mutación in-place |
| **Cero Fallos Silenciosos** | ENGINEERING_PRINCIPLES §IV | Todo fallo debe ser explícito o indexable |
| **Single-node / No infraestructura distribuida** | ADR Maestro §4 | Prohibido Redis, Brokers, K8s, DBs remotas |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| DF-01 | Deuda: 4 copias de helper `_make_node` en tests | Fase 18 / Refactor test-infra | Nada |
| DF-16 | Parámetros no usados en `ASTValidator.validate()` (dead code) | Post-Fase 2 | Nada |
| DF-18 | Entry points retornan exit code 0 en fallo | Fase 5 / Baseline Certification | **Riesgo crítico en Fase 6 (CI Gates)** |
| DF-19 | Migración de formato de hash del manifiesto (4 → 6 dimensiones) | Fase 5 / Baseline Certification | Manifiestos antiguos deben re-sellarse |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| **Migración de formato de hash (DF-19)** | Manifiestos sellados con formato antiguo (4 dimensiones) no son compatibles con el formato nuevo (6 dimensiones). Si existen, deben re-sellarse. | Documentado en docstring de `ManifestFingerprintCalculator` + test de regresión `test_df19_regression_old_format_differs_from_new_format`. Acción operativa en Fase 5. |
| **Exit code 0 en entry points (DF-18)** | `bootstrap_corpus.py`, `freeze_ground_truth.py`, `generate_golden_draft.py` retornan exit code 0 aunque fallen. En CI (Fase 6), un sellado corrupto pasaría desapercibido. | Documentado en Findings Register. Debe resolverse antes de integración en CI. |
| **Fugas de inmutabilidad en ASTNode (DF-04)** | `control_plane: Dict[str, Any]` y `NodeMetadata.bboxes/pages: List[...]` son mutables dentro de modelos `frozen=True`. Patrón heredado de Fase 16. | ACCEPTED_LIMITATION. No afecta la ontología del oráculo. |
| **Ventana de confianza en hydrate_ground_truth** | La fábrica es trust-based: el consumidor que conoce el estado lo provee explícitamente. Si el estado es incorrecto, la hidratación produce el tipo equivocado. | Mitigado por la autoridad única de sellado y la verificación de estado en `GenerateGoldenDraftUseCase`. |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Ontología del oráculo (`GroundTruthDraft`, `SealedOracle`, `DraftSubState`)
- ✅ Ciclo de vida gobernado (`LifecycleTransitionAuthority`)
- ✅ Validez estructural (`OracleValidityContract`)
- ✅ Completitud biyectiva (`BaselineCompletenessVerifier`)
- ✅ Autoridad única de sellado (`SealGroundTruthUseCase`)
- ✅ Asimetría de puertos (`CorpusManifestReaderPort`, `CorpusManifestWriterPort`)
- ✅ Identidad semántica (`OracleSemanticIdentityCalculator`)
- ✅ Formato extendido del hash del manifiesto (6 dimensiones)
- ✅ Campo `oracle_hash` y `ground_truth_state` en `RawDocumentEntryDTO` y `CorpusDocumentMetadata`
- ✅ Taxonomía de errores completa (`BaselineContractError`, `SealedOracleOverwriteError`)

**Lo que se necesita antes de arrancar:**
- Auditoría forense de Fase 3 (HITOs de Fase 0 de la sub-fase)
- ADR de Fase 3 (`ADR_F17_BIS_03.md`)
- NADRs de Fase 3 (encadenamiento criptográfico, linaje, confianza)
- Execution Plan de Fase 3

### 6.2 Next Phase Handoff Checklist

- [ ] Cargar este documento (`FASE_2_HANDOFF.md`) al iniciar sesión
- [ ] Cargar los documentos de Prioridad 1 (§8.4)
- [ ] Reemplazar `{COMMIT_HASH_FASE2}` con el SHA real del commit de cierre
- [ ] Verificar que `git status` está limpio
- [ ] Ejecutar `pytest -q` para confirmar la baseline de 368 passed
- [ ] Realizar auditoría forense de Fase 3 (HITOs de Fase 0)
- [ ] Redactar `ADR_F17_BIS_03.md` con la visión de Identity & Trust Model
- [ ] Promulgar NADRs de Fase 3
- [ ] Redactar `PHASE_17BIS_FASE3_EXECUTION_PLAN.md`

### 6.3 ROADMAP — Objetivos de la siguiente fase

Según ADR Maestro §6 (Hoja de Ruta de Sub-Fases Gobernadas):

1. **FASE 3 — Identity & Trust Model** — Hashes deterministas, linaje y encadenamiento criptográfico
   - Construir el encadenamiento criptográfico global $H_{baseline}$
   - Formalizar el linaje de los oráculos
   - Establecer el modelo de confianza del corpus

**Hito crítico:** Encadenamiento criptográfico completo de la baseline con $H_{baseline}$ determinista y reproducible.

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| `ADR_F17_BIS_03.md` | Plantilla de ADR Maestro §3.2 | Visión y capacidades de Identity & Trust Model |
| NADRs de Fase 3 | Plantilla canónica de NADR (9 secciones) | Reglas normativas de encadenamiento criptográfico |
| `PHASE_17BIS_FASE3_EXECUTION_PLAN.md` | Plantilla de Execution Plan | Secuencia operativa de Fase 3 |
| HITOs de Auditoría Forense | Plantilla de HITO | Evidencia forense de Fase 0 de la sub-fase |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` |
| ADR de Fase 2 | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_02.md` |
| NADR-F17BIS-12 (Ontología) | `docs/architecture/adr/phase-17-bis/NADR/NADR_12_Oracle_Ontology.md` |
| NADR-F17BIS-13 (Validez) | `docs/architecture/adr/phase-17-bis/NADR/NADR_13_Validity_Completeness.md` |
| NADR-F17BIS-14 (Autoridad) | `docs/architecture/adr/phase-17-bis/NADR/NADR_14_Authority_Ports.md` |
| NADR-F17BIS-15 (Identidad Semántica) | `docs/architecture/adr/phase-17-bis/NADR/NADR_15_Semantic_Identity.md` |
| Execution Plan | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE2_EXECUTION_PLAN.md` |
| Evidence Log | `docs/architecture/adr/phase-17-bis/reviews/FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md` |
| Methodology v1.3.0 | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |
| ENGINEERING_PRINCIPLES | `docs/architecture/ENGINEERING_PRINCIPLES.md` |
| ROADMAP | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` |
| PROJECT_SCOPE | `docs/architecture/PROJECT_SCOPE.md` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register | `docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| PROJECT_TREE | `.gitignore` (no commiteado) | Estructura del repositorio para auditoría forense |
| HITOs de Fase 0 | `docs/architecture/adr/phase-17-bis/00-foundation/` | Evidencia forense original |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.

### 8.1 Project Identity

```text
Proyecto: Traductor PDF Científico
Descripción: Pipeline local para ingesta, normalización, traducción LLM y reconstrucción de PDFs académicos/STEM preservando estructura, semántica y layout mediante AST V2.
Stack: Python 3.11, Pydantic, SQLite WAL, PyMuPDF, asyncio
Arquitectura: DDD + Hexagonal (Ports and Adapters), Functional Core / Imperative Shell, Flat AST
Fase actual completada: Fase 17-BIS / Fase 2 (Scientific Baseline Domain)
Siguiente fase: Fase 17-BIS / Fase 3 (Identity & Trust Model)
```

### 8.2 Code State

```text
Tests: 368 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
Rama: main (limpio)
Commit de cierre: 0fbe2b310a4cfaf295d66e730fe7d529ae8d25ec
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. Separación de Identidades: Integridad ≠ Identidad ≠ Regresión (ADR Maestro §3)
2. Zero Partial Sealing: biyección completa N_PDF = N_GT (ADR Maestro §5)
3. Determinismo y Reproducibilidad: todo hash es 100% determinista (ADR Maestro §5)
4. Desacoplamiento de Identidades: AST Schema Version, Corpus Version, Identity Hash diferenciados (ADR Maestro §5)
5. No-Inferencia de Estado: el estado del oráculo nunca se deduce de campos incidentales (ADR_F17_BIS_02 §6)
6. Asimetría de puertos: Reader/Writer segregados (NADR-14 §5.1)
7. Strings genéricos para estado: corpus NO importa enums de ground_truth (Decisión AD-11)
8. Inmutabilidad estricta: DTOs frozen=True, cero mutación in-place (ENGINEERING_PRINCIPLES §II)
9. Cero Fallos Silenciosos: todo fallo es explícito o indexable (ENGINEERING_PRINCIPLES §IV)
10. YAGNI: no implementar sin necesidad demostrada (ENGINEERING_PRINCIPLES §I)
11. Single-node: prohibido Redis, Brokers, K8s, DBs remotas (ADR Maestro §4)
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- docs/architecture/adr/phase-17-bis/handoff/FASE_2_HANDOFF.md
- docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md

Prioridad 2 (cargar para implementación):
- docs/architecture/ENGINEERING_PRINCIPLES.md
- docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md
- docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md

Prioridad 3 (consultar según necesidad):
- docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_FASE2_EXECUTION_PLAN.md
- docs/architecture/adr/phase-17-bis/reviews/FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md
- docs/architecture/adr/phase-17-bis/NADR/NADR_12..15_*.md
- docs/architecture/ROADMAP_ARQUITECTONICO_LP.md
- docs/architecture/PROJECT_SCOPE.md
```

### 8.5 Pending Items (carry-forward)

```text
[DF-01] Deuda: 4 copias de helper _make_node en tests
       → Destino: Fase 18 / Refactor test-infra
       → Bloquea: Nada

[DF-16] Parámetros no usados en ASTValidator.validate() (dead code)
       → Destino: Post-Fase 2
       → Bloquea: Nada

[DF-18] Entry points retornan exit code 0 en fallo
       → Destino: Fase 5 / Baseline Certification
       → Bloquea: Nada hasta Fase 6 (CI Gates)
       → Riesgo crítico: sellado corrupto pasaría desapercibido en CI

[DF-19] Migración de formato de hash del manifiesto (4 → 6 dimensiones)
       → Destino: Fase 5 / Baseline Certification
       → Bloquea: Nada hasta Fase 5
       → Acción operativa: manifiestos antiguos deben re-sellarse
```

### 8.6 Work Conventions

```text
- Auditar antes de implementar (Audit First, ADR Maestro §5)
- Reutilizar antes de inventar (Reuse Before Invent, ADR Maestro §5)
- Todo cambio requiere evidencia forense antes de implementarse (METHODOLOGY §1)
- Verificación obligatoria: pyright 0 errors + pytest suite en verde antes de cerrar tarea
- Commits atómicos por Gate con mensaje estructurado (feat/docs/chore)
- Documentos de gobernanza en docs/architecture/adr/phase-17-bis/
- No commitear notas de trabajo, grafos generados ni scripts temporales (.gitignore)
- Cuadruple comillas (````) para ventanas markdown en conversación
```

### 8.7 System Entry Points

```text
tools/evaluation/bootstrap_corpus.py        → Bootstrap del corpus canónico (curaduría)
tools/evaluation/freeze_ground_truth.py     → Sellado de la baseline (autoridad única)
tools/evaluation/generate_golden_draft.py   → Generación de drafts dorados (curaduría)
apps/bootstrap/pipeline_factory.py          → Composition root del pipeline de producción
core/shared/crypto.py                       → Funciones de hashing (compute_sha256)
```

`apps/bootstrap/pipeline_factory.py` es la composition root del pipeline de producción.
Los entry points de curaduría (`tools/evaluation/`) son Imperative Shells que componen los casos de uso del dominio.

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