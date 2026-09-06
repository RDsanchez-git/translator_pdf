# PHASE 17BIS_FASE5 EXECUTION PLAN v1.2.2
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.2.2
**Status:** FROZEN
**Date:** 2026-09-05
**Supersedes:** v1.2.1-DRAFT (2026-09-05)
**Derived From:** 5 NADRs FROZEN (NADR-F17BIS-20 a NADR-F17BIS-24, 166 reglas) + ADR_F17_BIS_MASTER (FROZEN) + ADR_F17_BIS_05 (FROZEN) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Fase 5 (Baseline Certification). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 5 Gates, 17 Waves, 68 Tasks. Basado en 5 NADRs FROZEN (166 reglas). |
| 1.1.0 | 2026-09-05 | Incorporación de 5 aspectos de la propuesta alternativa: (1) Criterios específicos de selección de documentos; (2) Curaduría manual explícita; (3) Criterio de decisión DF-04 explícito; (4) Runbook ampliado; (5) Formato de notas de implementación más explícito. |
| 1.2.0 | 2026-09-05 | FROZEN. Correcciones de conteo: Changelog corregido, Gate Completion Log reconciliado, Gate 2 tasks corregido. |
| 1.2.1 | 2026-09-05 | DRAFT — Hardening documental: (1) Gate 5: 8→10 Tasks en §3; (2) Rollback Plan Gate 2: eliminado rollback mutativo de SealedOracle; (3) Tasks 1.2.3/1.3.1 desambiguadas (contrato vs ejecución de migración); (4) Separación CERTIFIED/REJECTED/EXECUTION_FAILURE de Gate/Phase outcome; (5) Task 3.1.4 reformulada (estrategia aprobada, no opciones abiertas); (6) Task 3.2.2 reformulada (CAL→VAL→FREEZE, FINAL en Gate 5); (7) Task 2.2.1: "lógicamente atómico"; (8) Task 2.2.5: fault injection explícito; (9) Tasks 1.3.6/2.2.3 diferenciadas (candidato vs Oracle sellado); (10) Tasks 2.4.7/5.3.3 diferenciadas (implementación vs cierre administrativo); (11) §4 Runbook: aclarado como Deployment, Migration & Certification Operations; (12) §7 Appendix: nota normativa de granularidad. |
| 1.2.2 | 2026-09-05 | **FROZEN.** Corrección aritmética: (1) Nota normativa en §3 y §6 aclarando que las reglas de verificación no se contabilizan en el Gate que las verifica, solo en el Gate de implementación primaria; (2) Suma de reglas Gates 1-4 verificada: 57 + 43 + 31 + 37 = 166 (las 7 reglas de NADR-21 §5.6/§5.7 verificadas en Gate 2 se contabilizan en Gate 1). |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
ADR_F17_BIS_05 (decisión arquitectónica de Fase 5, FROZEN)
↓
NADRs 20-24 (reglas constitucionales permanentes, FROZEN, 166 reglas)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_FASE5_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_5_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-21 §5.5 R23` → NADR-F17BIS-21, sección 5.5, regla 23.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (166 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_5_DEFERRED_FINDINGS_REGISTER.md`), no en este documento.

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

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §11.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§3)
- Status Dashboard (§6)
- Traceability Appendix (§7)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

### 1.6 Phase 5 Scope Summary

La Fase 5 (Baseline Certification) materializa la Baseline Científica Inmutable definida por el ADR_F17_BIS_MASTER. Sus entregables son:

1. **Corpus Canónico Materializado:** 20-30 documentos de alta varianza catalogados y sellados en disco bajo la firma global $H_{baseline}$.
2. **Zero Partial Sealing:** Correspondencia biyectiva completa PDF↔oráculo verificada ($N_{PDF} = N_{GT}$).
3. **DF-04 Resuelto:** Benchmark comparativo ZhangShasha vs APTED ejecutado sobre el corpus materializado.
4. **Calibración Empírica:** Umbrales NSS y pesos de criticidad validados empíricamente bajo protocolo científico.
5. **Certificación End-to-End:** Certificación ejecutada con evidencia completa y auditable.

**Carry-forward from Phase 4:**
- DF-04 (Dualidad ZhangShasha/APTED) — requiere corpus materializado.
- DF-18 (Semántica de fallo heterogénea) — requiere remediación de entry points.
- GAP-5.0-03 (Configuración implícita del corpus) — requiere configuración explícita.
- GAP-5.2-05 (Certification Boundary Integrity violation) — requiere protección de SealedOracle.
- DF-19 (Manifest en formato legacy) — requiere migración a formato vigente.
- Baseline de tests: 624 passed, 5 skipped (NO DEBE DEGRADARSE).
- Pyright: 0 errors, 0 warnings.
- `build_extraction_pipeline()` es la factoría única de extracción (NADR-19 §5.5 R20).

---

## 2. GATES & WAVES

### 2.1 GATE 1 — Canonical Corpus & Ground Truth Qualification

**Objective:** Convertir el corpus físico candidato existente en un Corpus Canonical Qualified, y garantizar que sus Ground Truths cumplen los contratos necesarios para poder convertirse en autoridad.
**Execution Mode:** Secuencial
**Rollback Plan:** Revertir cambios al manifest y a los artefactos de corpus mediante backup previo (MIG-01). Los archivos de corpus son aditivos; el rollback consiste en eliminar los archivos del directorio `tests/corpus/canonical/` y el manifest generado. No se modifica código de producción.
**Gate Status:** ⏳ PENDING

#### 2.1.1 Wave 1.1 — Corpus Discovery & Identity (NADR-20 §5.1, §5.2, §5.5)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Seleccionar 20-30 documentos de alta varianza. Criterios específicos: papers IEEE (doble columna), libros densos, documentos con ecuaciones matemáticas complejas, tablas, figuras, gráficos. Verificar diversidad de layouts, estructuras documentales, desafíos de extracción y dominios científicos. | NADR-20 §5.5 R19-R21 | Medium | MIG-01 | TODO |
| **1.1.2** | Copiar los documentos seleccionados al directorio `tests/corpus/canonical/pdf/`. Verificar integridad de cada archivo (apertura con PyMuPDF). | NADR-20 §5.1 R1-R2 | Low | 1.1.1 | TODO |
| **1.1.3** | Calcular SHA-256 de cada documento del corpus canónico. Verificar unicidad de hashes (sin duplicados). | NADR-20 §5.1 R1, R3-R4 | Low | 1.1.2 | TODO |
| **1.1.4** | Deduplicación por contenido: consolidación de grupos G1/G2 (HITO 5.1). Verificar idempotencia. | NADR-20 §5.2 R5-R9 | Medium | 1.1.3 | TODO |
| **1.1.5** | Documentación del déficit de corpus y plan de adquisición. | NADR-20 §5.5 R19-R21 | Low | 1.1.4 | TODO |

#### 2.1.2 Wave 1.2 — Corpus Qualification & Manifest (NADR-20 §5.3, §5.4, §5.6, §5.7)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Verificación de traits por inspección de contenido de cada documento. Verificar contra catálogo vigente (ExtractionChallengeTrait). | NADR-20 §5.3 R10-R13 | High | 1.1.4 | TODO |
| **1.2.2** | Proceso de cualificación formal con registro auditable (origen, fecha, responsable). | NADR-20 §5.4 R14-R18 | Medium | 1.2.1 | TODO |
| **1.2.3** | Implementar el contrato del manifest canónico: formato 6D (document_id, sha256, traits, page_count, oracle_hash, ground_truth_state). Hash recomputable. Define el contrato, no ejecuta la migración. | NADR-20 §5.6 R22-R26 | High | 1.2.2 | TODO |
| **1.2.4** | Provenance de corpus: origen, fecha, responsable. Provenance ≠ identidad. | NADR-20 §5.7 R27-R28 | Low | 1.2.3 | TODO |

#### 2.1.3 Wave 1.3 — GT Migration & Eligibility (NADR-21 §5.1, §5.2, §5.3, §5.6, §5.7, §5.8)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Ejecutar/materializar la migración del artefacto legacy DF-19 al formato vigente (6D). Aplica el contrato definido en Task 1.2.3. | NADR-21 §5.8 R38, DF-19 | High | 1.2.3 | TODO |
| **1.3.2** | Canonicalización de node_ids: `"value='p1_b0'"` → `"p1_b0"`. Determinista, con trazabilidad de lineage. | NADR-21 §5.2 R8-R12 | Critical | 1.3.1 | TODO |
| **1.3.3** | Verificación de hidratación bajo contrato vigente (hydrate_ground_truth). | NADR-21 §5.1 R1-R3 | Medium | 1.3.2 | TODO |
| **1.3.4** | Verificación de validez estructural (no vaciedad, no duplicados, integridad, consistencia). | NADR-21 §5.3 R13-R16 | Medium | 1.3.3 | TODO |
| **1.3.5** | Verificación de elegibilidad completa. | NADR-21 §5.1 R4-R7 | Medium | 1.3.4 | TODO |
| **1.3.6** | Verificación de identidad semántica del candidato elegible (antes del sealing). | NADR-21 §5.6 R28-R31 | Medium | 1.3.5 | TODO |
| **1.3.7** | Verificación de identidad de baseline (hash encadenado). | NADR-21 §5.7 R32-R34 | Medium | 1.3.6 | TODO |
| **1.3.8** | Migración de .ast.json legacy (H-5.1-D) o decisión de re-extracción. | NADR-21 §5.8 R35-R37 | High | 1.3.5 | TODO |
| **1.3.9** | Curaduría manual de Ground Truths: verificar que cada AST representa fielmente la estructura del documento fuente. Corregir errores de extracción. La curaduría ocurre ANTES del sealing, nunca después. | NADR-21 §5.1 R5 | High | 1.3.8 | TODO |

#### 2.1.4 Gate 1 Exit Criteria

- El corpus canónico contiene entre 20 y 30 documentos.
- Todos los documentos tienen SHA-256 único y verificado.
- Deduplicación de G1/G2 completada y verificada (idempotente).
- Traits verificados por inspección de contenido.
- Manifest canónico en formato 6D con hash recomputable.
- Node_ids canonicalizados y verificados.
- Ground Truths hidratables bajo contrato vigente.
- Validez estructural verificada.
- Curaduría manual completada (antes del sealing).
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde (baseline 624 passed, 5 skipped no degradada).

#### 2.1.5 Gate 1 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** ⏳ PENDING
**Fecha de verificación:** —

---

### 2.2 GATE 2 — GT Sealing & Canonical Evaluation Configuration

**Objective:** Sellar los Ground Truths elegibles bajo Zero Partial Sealing, y congelar la configuración canónica del motor de evaluación topológica.
**Execution Mode:** Mixto (W2.1/W2.2 secuenciales, W2.3/W2.4 paralelizables con W2.1/W2.2)
**Rollback Plan:** No existe rollback mutativo de un Ground Truth sellado. Las operaciones fallidas ANTES de completar el sealing pueden revertirse operacionalmente (restaurar backup de MIG-02). Una corrección posterior al sealing requiere generar una nueva versión del artefacto y repetir el lifecycle de elegibilidad y sealing conforme a NADR-21. MIG-02 constituye precaución operacional pre-sealing, no mecanismo de rollback post-sealing. Revertir configuración canónica mediante restauración de configuración previa.
**Gate Status:** ⏳ PENDING

#### 2.2.1 Wave 2.1 — GT Validation & Structural Integrity (NADR-21 §5.4, §5.9)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Verificación del ciclo de vida Draft→Audited→Validated→Sealed. | NADR-21 §5.4 R17-R21 | Medium | Gate 1 | TODO |
| **2.1.2** | Protección de SealedOracle: remediación de GAP-5.2-05 (sanitize_ground_truth_types.py). Verificar que ningún mecanismo puede modificar oráculos sellados sin verificación de estado. | NADR-21 §5.9 R39-R43, GAP-5.2-05 | Critical | 2.1.1 | TODO |

#### 2.2.2 Wave 2.2 — Zero Partial Sealing & Oracle Identity (NADR-21 §5.5, §5.6, §5.7)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Sellado lógicamente atómico con Zero Partial Sealing (biyección PDF↔GT). Ejecutar `freeze_ground_truth.py`. | NADR-21 §5.5 R22-R27 | Critical | 2.1.2 | TODO |
| **2.2.2** | Verificación de correspondencia biyectiva ($N_{PDF} = N_{GT}$). Verificar que no hay documentos sin oráculo ni oráculos huérfanos. | NADR-21 §5.5 R23 | Critical | 2.2.1 | TODO |
| **2.2.3** | Verificación de identidad semántica del Oracle sellado (después del sealing). | NADR-21 §5.6 R28-R31 | Medium | 2.2.1 | TODO |
| **2.2.4** | Verificación de identidad de baseline (hash encadenado). Verificar que el manifest se actualiza correctamente con oracle_hash y ground_truth_state. | NADR-21 §5.7 R32-R34 | Medium | 2.2.2 | TODO |
| **2.2.5** | Verificación de atomicidad lógica del sellado mediante fault injection / test: o se sellan todos los documentos, o no se sella ninguno. | NADR-21 §5.5 R22, R27 | High | 2.2.1 | TODO |

#### 2.2.3 Wave 2.3 — Canonical Engine Composition (NADR-22 §5.1, §5.2, §5.3)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Configuración de ZhangShashaEngine como motor canónico. APTED queda como experimental/benchmark no normativo. | NADR-22 §5.1 R1-R4 | Medium | Gate 1 | TODO |
| **2.3.2** | Configuración de CriticalityAwareCostContext con pesos 5.0/2.0/1.0. Verificar implementa TreeEditCostContext. | NADR-22 §5.2 R5-R9 | Medium | 2.3.1 | TODO |
| **2.3.3** | Normalización de texto: sin .strip(), sin fingerprint. Registrar divergencia con ASTFingerprintPolicy como deuda técnica. | NADR-22 §5.3 R10-R12 | Medium | 2.3.2 | TODO |

#### 2.2.4 Wave 2.4 — Engine Configuration Freeze & Verification (NADR-22 §5.4-§5.8) + DF-04

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.4.1** | Raíz virtual condicional (solo si multi-root), costo 0. | NADR-22 §5.4 R13-R15 | Low | 2.3.3 | TODO |
| **2.4.2** | Metodología Σ TED(windows) con HeadingAnchorPartitionStrategy. | NADR-22 §5.5 R16-R18 | Medium | 2.4.1 | TODO |
| **2.4.3** | Identificador criptográfico de configuración canónica, congelación. Toda modificación invalida certificación vigente. | NADR-22 §5.6 R19-R21 | Medium | 2.4.2 | TODO |
| **2.4.4** | Thresholds específicos (no universales). DoubleProtectionMechanism canónico. CriticalityVerdictEmitter canónico. | NADR-22 §5.7 R22-R25 | Medium | 2.4.3 | TODO |
| **2.4.5** | Provenance de evaluación: registro de configuración canónica utilizada. Verificable contra configuración vigente. | NADR-22 §5.8 R26-R27 | Low | 2.4.4 | TODO |
| **2.4.6** | Verificación de determinismo del motor canónico: misma entrada → mismo resultado. | NADR-22 §5.1 R1, §5.5 R16 | Medium | 2.4.3 | TODO |
| **2.4.7** | Implementación/investigación empírica del benchmark DF-04: ZhangShasha vs APTED. Criterio de decisión (respaldado por FASE_4_HANDOFF §5.2 DF-04): divergencia < 1% TED normalizado → APTED queda como experimental sin acción adicional; divergencia ≥ 1% → investigar causa raíz y documentar. | NADR-22 §5.1 R3, DF-04 | Low | 2.4.3, Gate 1 | TODO |

#### 2.2.5 Gate 2 Exit Criteria

- Todos los Ground Truths sellados bajo Zero Partial Sealing (biyección verificada).
- Identidad de baseline computada y verificada (hash encadenado).
- Sellado lógicamente atómico verificado (todo o nada, fault injection).
- Configuración canónica del motor congelada e identificada criptográficamente.
- DF-04 ejecutado y resultado documentado (validación no normativa).
- GAP-5.2-05 remediado (sanitize_ground_truth_types.py protegido).
- Determinismo del motor canónico verificado.
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde (baseline 624 passed, 5 skipped no degradada).

#### 2.2.6 Gate 2 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** ⏳ PENDING
**Fecha de verificación:** —

---

### 2.3 GATE 3 — Scientific Calibration & Experimental Provenance

**Objective:** Ejecutar la calibración empírica de parámetros bajo un protocolo científico definido, con independencia de datasets y provenance reproducible. Gate 3 ejecuta CAL→VAL→FREEZE, dejando FINAL EVALUATION exclusivamente para Gate 5.
**Execution Mode:** Secuencial
**Rollback Plan:** Revertir parámetros calibrados a valores previos. Restaurar Calibration Provenance Record desde backup.
**Gate Status:** ⏳ PENDING

#### 2.3.1 Wave 3.1 — Dataset Independence & Partition (NADR-23 §5.1, §5.3)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Definición de CALIBRATION / VALIDATION / FINAL EVALUATION como fases secuenciales distintas. | NADR-23 §5.1 R1-R3 | Low | Gate 2 | TODO |
| **3.1.2** | Partición de datasets por content identity (SHA-256), no filename. Verificar que documentos con el mismo SHA-256 no aparecen en particiones diferentes. | NADR-23 §5.3 R9-R11 | High | 3.1.1 | TODO |
| **3.1.3** | Verificación de disjunción: Calibration dataset ∩ Final Evaluation dataset = ∅ a nivel de SHA-256. | NADR-23 §5.3 R10 | Medium | 3.1.2 | TODO |
| **3.1.4** | Evaluar el tamaño y características del corpus y materializar la estrategia de independencia estadística aprobada conforme al protocolo científico. Con <20 identidades, la partición clásica train/validation/holdout no se presume robusta. Registrar la estrategia elegida como evidencia. | NADR-23 §5.3 R12-R13 | Medium | 3.1.2 | TODO |

#### 2.3.2 Wave 3.2 — Calibration Protocol & Execution (NADR-23 §5.2, §5.4, §5.7)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Protocolo de calibración: definir experimento ANTES de elegir algoritmo de búsqueda. Definir: variable a calibrar, ground truth observable, función objetivo, espacio de parámetros, restricciones, unidad de evaluación, independencia de datasets, criterio de aceptación. | NADR-23 §5.2 R4-R8 | High | 3.1.4 | TODO |
| **3.2.2** | Definir y ejecutar el lifecycle CAL→VAL→FREEZE, dejando FINAL EVALUATION exclusivamente para Gate 5. Verificar que las fases no se mezclan. | NADR-23 §5.4 R14-R16 | Medium | 3.2.1 | TODO |
| **3.2.3** | Condiciones de validez científica: documentar que tuning ad-hoc sin protocolo ≠ calibración científica. Distinguir calibration validity de certification eligibility. | NADR-23 §5.7 R26-R28 | Low | 3.2.2 | TODO |

#### 2.3.3 Wave 3.3 — Provenance & Parameter Freeze (NADR-23 §5.5, §5.6, §5.8)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Calibration Provenance Record: 5 campos mínimos (corpus_identity, metric_configuration, parameters, result, timestamp). Referenciar protocolo aprobado y condiciones de ejecución. Distinguir experiment identity / parameter identity / result identity. | NADR-23 §5.5 R18-R22 | Medium | 3.2.3 | TODO |
| **3.3.2** | Parameter freeze: hash criptográfico determinista (parameter identity). Inmutabilidad: nueva configuración = nueva parameter identity = nueva línea de certificación. | NADR-23 §5.6 R23-R25 | Medium | 3.3.1 | TODO |
| **3.3.3** | Evaluation Provenance Record: independiente del Calibration Provenance Record como registro, pero trazable hacia la calibración que produjo los parámetros congelados. | NADR-23 §5.8 R29-R31 | Medium | 3.3.2 | TODO |

#### 2.3.4 Gate 3 Exit Criteria

- Partición de datasets verificada (disjunción por content identity).
- Estrategia de partición justificada y documentada como evidencia.
- Protocolo de calibración aprobado y ejecutado.
- Lifecycle CAL→VAL→FREEZE completado (FINAL EVALUATION queda para Gate 5).
- Calibration Provenance Record completo y verificable.
- Parameter freeze ejecutado (hash criptográfico, inmutabilidad verificada).
- Evaluation Provenance Record registrado (independiente pero trazable).
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde (baseline 624 passed, 5 skipped no degradada).

#### 2.3.5 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** ⏳ PENDING
**Fecha de verificación:** —

---

### 2.4 GATE 4 — Certification Tooling & Execution Safety

**Objective:** Implementar el tooling de certificación con PREFLIGHT, semántica de fallo uniforme, boundary integrity, evidence completeness, y determinismo operacional.
**Execution Mode:** Mixto (W4.1→W4.2→W4.4 secuenciales, W4.3 paralelizable con W4.2)
**Rollback Plan:** Revertir cambios al tooling mediante backup previo. Restaurar entry points a versión previa.
**Gate Status:** ⏳ PENDING

#### 2.4.1 Wave 4.1 — PREFLIGHT & Explicit Configuration (NADR-24 §5.1, §5.2, §5.3)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Contrato de ejecución explícito: inputs requeridos, precondiciones normativas, postcondiciones de éxito, condiciones de fallo. | NADR-24 §5.1 R1-R3 | Medium | Gate 3 | TODO |
| **4.1.2** | PREFLIGHT: verificación de precondiciones antes de RUN. Idempotente. Aborta con EXECUTION_FAILURE ante precondición no satisfecha. | NADR-24 §5.2 R6-R9 | High | 4.1.1 | TODO |
| **4.1.3** | Configuración explícita: corpus explícito, no fallback silencioso. Remediación de GAP-5.0-03 (rutas hardcoded). | NADR-24 §5.3 R10-R14, GAP-5.0-03 | High | 4.1.2 | TODO |

#### 2.4.2 Wave 4.2 — Failure Semantics & Exit Contract (NADR-24 §5.4, §5.5)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Semántica de fallo uniforme: 3 categorías (certificación válida, certificación rechazada, fallo de ejecución). Cero fallos silenciosos. | NADR-24 §5.4 R15-R19 | Critical | 4.1.3 | TODO |
| **4.2.2** | Tolerancia a fallos parciales ≠ certificación parcial. Resultado atómico a nivel de baseline. | NADR-24 §5.5 R20-R24 | High | 4.2.1 | TODO |
| **4.2.3** | Remediación de DF-18: exit codes en freeze_ground_truth.py, generate_golden_draft.py, generate_pymupdf_candidate.py, sanitize_ground_truth_types.py. Ningún camino de error crítico produce exit code de categoría "certificación válida". | NADR-24 §5.4 R15-R16, DF-18 | Critical | 4.2.1 | TODO |

#### 2.4.3 Wave 4.3 — Certification Boundary & Evidence (NADR-24 §5.6, §5.7, §5.9) + GAP-5.2-05

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Boundary integrity: Sealed inmutable sin excepción. Frontera Scientific Truth / Generated Output / Certification Evidence preservada. | NADR-24 §5.6 R25-R28 | High | 4.2.2 | TODO |
| **4.3.2** | Remediación de GAP-5.2-05: protección de SealedOracle en sanitize_ground_truth_types.py. Verificar estado de sellado antes de cualquier modificación. | NADR-24 §5.6 R25-R26, GAP-5.2-05 | Critical | 4.3.1 | TODO |
| **4.3.3** | Evidence completeness: 7 elementos mínimos (corpus identity, manifest identity, evaluation configuration identity, frozen parameters identity, evaluation provenance, per-document results, aggregate result). Auditable sin re-ejecución. | NADR-24 §5.7 R29-R31 | Medium | 4.3.1 | TODO |
| **4.3.4** | POST-RUN VALIDATION: verificar post-condiciones de certificación. | NADR-24 §5.9 R36-R37 | Medium | 4.3.3 | TODO |

#### 2.4.4 Wave 4.4 — Determinism, Idempotency & Recovery (NADR-24 §5.8)

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.4.1** | Determinismo operacional: mismas condiciones de ejecución certificables → mismo resultado. Distinguir de reproducibilidad científica (NADR-23). | NADR-24 §5.8 R32 | Medium | 4.2.2, 4.3.4 | TODO |
| **4.4.2** | Idempotencia lógica: re-ejecución sin reutilización no determinista de residuos. | NADR-24 §5.8 R33 | Medium | 4.4.1 | TODO |
| **4.4.3** | Recovery: estado post-fallo determinable (qué unidades evaluadas, qué artefactos en disco, si reutilizables, si re-ejecución reemplaza). No prometer atomicidad física completa si la infraestructura no la garantiza. | NADR-24 §5.8 R34-R35 | Medium | 4.4.2 | TODO |

#### 2.4.5 Gate 4 Exit Criteria

- PREFLIGHT implementado y verificado (aborta ante precondiciones no satisfechas, idempotente).
- Semántica de fallo uniforme implementada en todos los entry points de certificación (DF-18 resuelto).
- GAP-5.0-03 remediado (configuración explícita, no rutas hardcoded).
- GAP-5.2-05 remediado (sanitize_ground_truth_types.py protegido).
- Boundary integrity implementada (Sealed inmutable, frontera preservada).
- Evidence completeness implementado (7 elementos mínimos, auditable).
- POST-RUN VALIDATION implementado.
- Determinismo operacional verificado.
- Idempotencia lógica verificada.
- Recovery: estado post-fallo determinable.
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde (baseline 624 passed, 5 skipped no degradada).

#### 2.4.6 Gate 4 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** ⏳ PENDING
**Fecha de verificación:** —

---

### 2.5 GATE 5 — End-to-End Certification & Baseline Freeze

**Objective:** Ejecutar la certificación de la baseline de punta a punta, producir evidencia completa, y cerrar la fase. Gate 5 NO implementa comportamiento nuevo; solo ejecuta y verifica. Si la certificación falla, se abre un finding y se vuelve al Gate correspondiente.
**Execution Mode:** Secuencial
**Rollback Plan:** No aplica. Gate 5 no implementa comportamiento nuevo. Si la certificación falla, se identifica la causa raíz y se corrige en el Gate correspondiente.
**Gate Status:** ⏳ PENDING

#### 2.5.1 Wave 5.1 — Certification Readiness Verification

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **5.1.1** | Verificación del contrato de ejecución completo: CERTIFIED como condición compuesta (execution SUCCESS + scientific ACCEPTED + evidence complete + invariants satisfied). | NADR-24 §5.1 R1-R5 | Medium | Gate 4 | TODO |
| **5.1.2** | Verificación de que todas las 166 reglas de NADR-20 a NADR-24 están DONE. | Todas las reglas de NADR-20 a NADR-24 | Medium | 5.1.1 | TODO |

#### 2.5.2 Wave 5.2 — Independent Final Evaluation

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **5.2.1** | Ejecución de FINAL EVALUATION con parámetros congelados sobre dataset independiente. | NADR-23 §5.4 R17 | High | 5.1.2 | TODO |
| **5.2.2** | Registro de Evaluation Provenance Record (independiente pero trazable hacia calibración). | NADR-23 §5.8 R31 | Medium | 5.2.1 | TODO |

#### 2.5.3 Wave 5.3 — Baseline Certification & Closure

**Wave Status:** ⏳ PENDING
**Fecha de inicio:** —
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **5.3.1** | Ejecución de certificación: resultado CERTIFIED / REJECTED / EXECUTION_FAILURE. | NADR-24 §5.1 R4 | Critical | 5.2.2 | TODO |
| **5.3.2** | Persistencia de Certification Evidence (7 elementos mínimos). | NADR-24 §5.7 R29 | Medium | 5.3.1 | TODO |
| **5.3.3** | Verificación de cierre administrativo/documentación del finding DF-04. | DF-04 | Low | 5.3.1 | TODO |
| **5.3.4** | Verificación de que el reporte de certificación es determinista: dos ejecuciones independientes producen el mismo resultado. | NADR-24 §5.8 R32 | Medium | 5.3.1 | TODO |
| **5.3.5** | Generar handoff document para Fase 6 (Continuous Verification). Incluir: estado del corpus, Ground Truths sellados, parámetros calibrados, resolución de DF-04, y carry-forwards. | ADR_F17_BIS_MASTER §10 | Medium | 5.3.1 | TODO |
| **5.3.6** | Actualizar el Findings Register con todos los hallazgos de la Fase 5. Cerrar el Findings Register. | METHODOLOGY §3.5.3 | Low | 5.3.1 | TODO |

#### 2.5.4 Gate 5 Exit Criteria (Global DoD)

- Todas las 166 reglas de NADR-20 a NADR-24 en estado DONE.
- FINAL EVALUATION ejecutada con parámetros congelados sobre dataset independiente.
- Evaluation Provenance Record registrado.
- Certificación ejecutada: resultado CERTIFIED, REJECTED, o EXECUTION_FAILURE documentado.
- Certification Evidence persistida y auditable (7 elementos mínimos).
- Reporte de certificación determinista verificado.
- DF-04 cerrado con resultado documentado.
- Baseline certificada con identidad criptográfica verificada.
- Handoff document para Fase 6 generado.
- Findings Register cerrado.
- Pyright: 0 errors, 0 warnings.
- Tests: suite completa en verde (baseline 624 passed, 5 skipped no degradada).

#### 2.5.5 Gate 5 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⏳ |
| 2 | Todas las 166 reglas en estado DONE en §7 | ⏳ |
| 3 | Gate Exit Criteria satisfechos | ⏳ |
| 4 | Hallazgos identificados derivados al Findings Register | ⏳ |
| 5 | Pyright: 0 errors, 0 warnings | ⏳ |
| 6 | Tests: suite completa en verde | ⏳ |
| 7 | Notas de implementación completas para todas las Tasks | ⏳ |

**Veredicto del Gate:** ⏳ PENDING
**Fecha de verificación:** —

#### 2.5.6 Gate 5 Outcome Semantics

**Nota normativa:** Gate 5 distingue tres niveles de outcome:

```text
Execution outcome (NADR-24 §5.1 R4):
  CERTIFIED / REJECTED / EXECUTION_FAILURE

Gate outcome (este Execution Plan):
  PASS → todas las Tasks DONE, todos los criterios satisfechos
  CONDITIONAL PASS → ejecución completada pero con findings abiertos
  FAIL → criterios no satisfechos

Phase outcome (Global DoD):
  CERTIFIED → Fase completada, Baseline certificada
  REJECTED → certificación ejecutada pero Baseline NO certificada. 
             Gate 5 CONDITIONAL PASS. Return to originating decision/calibration Gate.
  EXECUTION_FAILURE → tooling failure. Return to originating implementation Gate.
```

**Nota crítica:** "Documentar REJECTED" NO satisface por sí mismo "Baseline certificada". Si FINAL EVALUATION produce REJECTED, la Fase 5 NO se considera completada como "Baseline certificada".

---

## 3. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | — | 0/57 | 0/18 | 0 | ⏳ PENDING |
| Gate 2 | — | 0/43 | 0/17 | 0 | ⏳ PENDING |
| Gate 3 | — | 0/31 | 0/10 | 0 | ⏳ PENDING |
| Gate 4 | — | 0/37 | 0/13 | 0 | ⏳ PENDING |
| Gate 5 | — | 0/166 (verification-only) | 0/10 | 0 | ⏳ PENDING |

**Nota normativa de contabilización:** Las reglas listadas como verificación en un Gate (§7, columna Implementation Notes) no se contabilizan en ese Gate. Se contabilizan únicamente en el Gate de implementación primaria. Gate 5 no posee reglas normativas primarias; sus verificaciones no alteran la asignación primaria de reglas. Gate 5 verifica que 57 + 43 + 31 + 37 = 166 reglas están DONE. Las 7 reglas de NADR-21 §5.6/§5.7 verificadas en Gate 2 (Wave 2.2 Tasks 2.2.3, 2.2.4) se contabilizan en Gate 1 (implementación primaria en Wave 1.3 Tasks 1.3.6, 1.3.7).

---

## 4. DEPLOYMENT, MIGRATION & CERTIFICATION OPERATIONS RUNBOOK

Tareas operativas de release, migración y certificación (no desarrollo). Incluye operaciones irreversibles o materializadoras de corpus, sealing, freeze y certification. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Backup/snapshot del corpus candidato antes de cualquier modificación | Local | NADR-20 §5.1 R1 | Backup verificado (SHA-256 de cada documento) | TODO |
| **MIG-02** | Backup de Ground Truths antes de sellado (precaución operacional pre-sealing, NO mecanismo de rollback post-sealing) | Local | NADR-21 §5.5 R22 | Backup verificado | TODO |
| **MIG-03** | Copiar 20-30 documentos del corpus canónico a `tests/corpus/canonical/pdf/` | Local | NADR-20 §5.1 R1-R2 | SHA-256 de cada documento verificado | TODO |
| **MIG-04** | Migración de manifest legacy (DF-19) a formato vigente (6D) | Local | NADR-21 §5.8 R38, NADR-20 §5.6 R23 | Manifest migrado y hash verificado | TODO |
| **MIG-05** | Canonicalización de node_ids en Ground Truths | Local | NADR-21 §5.2 R8-R12 | Node_ids canonicalizados y verificados | TODO |
| **MIG-06** | Ejecutar `freeze_ground_truth.py` contra el corpus canónico (Zero Partial Sealing). Operación irreversible: después del sealing, no existe rollback mutativo. | Local | NADR-21 §5.5 R22-R27 | Biyección verificada ($N_{PDF} = N_{GT}$), oráculos sellados | TODO |
| **MIG-07** | Congelación de configuración canónica del motor | Local | NADR-22 §5.6 R19-R21 | Configuración congelada e identificada | TODO |
| **MIG-08** | Congelación de parámetros calibrados (parameter freeze) | Local | NADR-23 §5.6 R23-R25 | Parameter freeze verificado (hash criptográfico) | TODO |

---

## 5. GLOBAL DoD (Definition of Done)

La Fase 5 (Baseline Certification) se considera oficialmente completada cuando:

```text
{All 166 rules in FROZEN NADRs 20-24} − {Rules with DONE status in §7} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

**Criterios específicos del DoD Nivel B (ADR_F17_BIS_MASTER §10):**
- [ ] Corpus Canónico Materializado: 20-30 documentos catalogados y sellados en disco bajo $H_{baseline}$.
- [ ] Zero Partial Sealing: Correspondencia biyectiva completa PDF↔oráculo verificada ($N_{PDF} = N_{GT}$).
- [ ] DF-04 Resuelto: Benchmark ZhangShasha vs APTED ejecutado con resolución documentada.
- [ ] DF-18 Resuelto: Semántica de fallo uniforme en todos los entry points de certificación.
- [ ] GAP-5.0-03 Remediado: Configuración explícita del corpus.
- [ ] GAP-5.2-05 Remediado: Protección de SealedOracle.
- [ ] DF-19 Resuelto: Manifest migrado a formato vigente (6D).
- [ ] Calibración Empírica: Umbrales NSS y pesos de criticidad calibrados empíricamente bajo protocolo científico.
- [ ] Certification Evidence: Completa y auditable (7 elementos mínimos).
- [ ] Verificación Estática y Pruebas Limpias: Pyright 0 errors, 0 warnings; suite de tests en verde.

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 0 | 0 | 0 | 57 | ⏳ PENDING |
| Gate 2 | 0 | 0 | 0 | 43 | ⏳ PENDING |
| Gate 3 | 0 | 0 | 0 | 31 | ⏳ PENDING |
| Gate 4 | 0 | 0 | 0 | 37 | ⏳ PENDING |
| Gate 5 | 0 | 0 | 0 | 166 (verification-only) | ⏳ PENDING |
| **TOTAL** | **0** | **0** | **0** | **166** | ⏳ PENDING |

**Nota normativa de contabilización:** Las reglas de verificación no se contabilizan en el Gate que las verifica, solo en el Gate de implementación primaria. Ver nota normativa en §3.

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2)
2. Se agregan las Notas de implementación de la Task (§2.{X}.{Y})
3. Se actualiza el `Derived Status` de sus reglas en §7
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.{X}.{Z})

---

## 7. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

**Nota normativa de granularidad:** Task DONE → todas las reglas asignadas DONE. Task IN_PROGRESS → todas las reglas PENDING. No se permiten estados parciales de reglas dentro de una Task. El agrupamiento por rango (ej. "R1-R4") solo es válido cuando el estado es homogéneo por Task.

### 7.1 Gate 1 — Rules Audit Board (NADR-20: 28 reglas + NADR-21 §5.1-§5.3/§5.6-§5.8: 29 reglas = 57 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-20 §5.1 R1-R4 | PENDING | Wave 1.1 / Task 1.1.2, 1.1.3 | — |
| NADR-20 §5.2 R5-R9 | PENDING | Wave 1.1 / Task 1.1.4 | — |
| NADR-20 §5.5 R19-R21 | PENDING | Wave 1.1 / Task 1.1.1, 1.1.5 | — |
| NADR-20 §5.3 R10-R13 | PENDING | Wave 1.2 / Task 1.2.1 | — |
| NADR-20 §5.4 R14-R18 | PENDING | Wave 1.2 / Task 1.2.2 | — |
| NADR-20 §5.6 R22-R26 | PENDING | Wave 1.2 / Task 1.2.3 | — |
| NADR-20 §5.7 R27-R28 | PENDING | Wave 1.2 / Task 1.2.4 | — |
| NADR-21 §5.8 R38 | PENDING | Wave 1.3 / Task 1.3.1 | — |
| NADR-21 §5.2 R8-R12 | PENDING | Wave 1.3 / Task 1.3.2 | — |
| NADR-21 §5.1 R1-R3 | PENDING | Wave 1.3 / Task 1.3.3 | — |
| NADR-21 §5.3 R13-R16 | PENDING | Wave 1.3 / Task 1.3.4 | — |
| NADR-21 §5.1 R4-R7 | PENDING | Wave 1.3 / Task 1.3.5 | — |
| NADR-21 §5.6 R28-R31 | PENDING | Wave 1.3 / Task 1.3.6 | — |
| NADR-21 §5.7 R32-R34 | PENDING | Wave 1.3 / Task 1.3.7 | — |
| NADR-21 §5.8 R35-R37 | PENDING | Wave 1.3 / Task 1.3.8 | — |

### 7.2 Gate 2 — Rules Audit Board (NADR-21 §5.4-§5.5/§5.9: 16 reglas + NADR-22: 27 reglas = 43 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-21 §5.4 R17-R21 | PENDING | Wave 2.1 / Task 2.1.1 | — |
| NADR-21 §5.9 R39-R43 | PENDING | Wave 2.1 / Task 2.1.2 | — |
| NADR-21 §5.5 R22-R27 | PENDING | Wave 2.2 / Task 2.2.1, 2.2.2, 2.2.5 | — |
| NADR-21 §5.6 R28-R31 | PENDING | Wave 2.2 / Task 2.2.3 | Verificación (implementación primaria en Wave 1.3 Task 1.3.6) |
| NADR-21 §5.7 R32-R34 | PENDING | Wave 2.2 / Task 2.2.4 | Verificación (implementación primaria en Wave 1.3 Task 1.3.7) |
| NADR-22 §5.1 R1-R4 | PENDING | Wave 2.3 / Task 2.3.1 | — |
| NADR-22 §5.2 R5-R9 | PENDING | Wave 2.3 / Task 2.3.2 | — |
| NADR-22 §5.3 R10-R12 | PENDING | Wave 2.3 / Task 2.3.3 | — |
| NADR-22 §5.4 R13-R15 | PENDING | Wave 2.4 / Task 2.4.1 | — |
| NADR-22 §5.5 R16-R18 | PENDING | Wave 2.4 / Task 2.4.2 | — |
| NADR-22 §5.6 R19-R21 | PENDING | Wave 2.4 / Task 2.4.3 | — |
| NADR-22 §5.7 R22-R25 | PENDING | Wave 2.4 / Task 2.4.4 | — |
| NADR-22 §5.8 R26-R27 | PENDING | Wave 2.4 / Task 2.4.5 | — |

### 7.3 Gate 3 — Rules Audit Board (NADR-23: 31 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-23 §5.1 R1-R3 | PENDING | Wave 3.1 / Task 3.1.1 | — |
| NADR-23 §5.3 R9-R13 | PENDING | Wave 3.1 / Task 3.1.2, 3.1.3, 3.1.4 | — |
| NADR-23 §5.2 R4-R8 | PENDING | Wave 3.2 / Task 3.2.1 | — |
| NADR-23 §5.4 R14-R16 | PENDING | Wave 3.2 / Task 3.2.2 | — |
| NADR-23 §5.7 R26-R28 | PENDING | Wave 3.2 / Task 3.2.3 | — |
| NADR-23 §5.5 R18-R22 | PENDING | Wave 3.3 / Task 3.3.1 | — |
| NADR-23 §5.6 R23-R25 | PENDING | Wave 3.3 / Task 3.3.2 | — |
| NADR-23 §5.8 R29-R31 | PENDING | Wave 3.3 / Task 3.3.3 | — |

### 7.4 Gate 4 — Rules Audit Board (NADR-24: 37 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-24 §5.1 R1-R3 | PENDING | Wave 4.1 / Task 4.1.1 | — |
| NADR-24 §5.2 R6-R9 | PENDING | Wave 4.1 / Task 4.1.2 | — |
| NADR-24 §5.3 R10-R14 | PENDING | Wave 4.1 / Task 4.1.3 | — |
| NADR-24 §5.4 R15-R19 | PENDING | Wave 4.2 / Task 4.2.1 | — |
| NADR-24 §5.5 R20-R24 | PENDING | Wave 4.2 / Task 4.2.2 | — |
| NADR-24 §5.6 R25-R28 | PENDING | Wave 4.3 / Task 4.3.1, 4.3.2 | — |
| NADR-24 §5.7 R29-R31 | PENDING | Wave 4.3 / Task 4.3.3 | — |
| NADR-24 §5.9 R36-R37 | PENDING | Wave 4.3 / Task 4.3.4 | — |
| NADR-24 §5.8 R32-R35 | PENDING | Wave 4.4 / Task 4.4.1, 4.4.2, 4.4.3 | — |

### 7.5 Gate 5 — Rules Audit Board (Verificación de las 166 reglas)

**Nota normativa:** Gate 5 no posee reglas normativas primarias. Verifica que las 166 reglas asignadas a Gates 1-4 están DONE.

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| Todas las reglas de NADR-20 a NADR-24 | PENDING | Wave 5.1 / Task 5.1.2 | Verificación de completitud (no implementación primaria) |
| NADR-23 §5.4 R17 | PENDING | Wave 5.2 / Task 5.2.1 | FINAL EVALUATION (ejecución, no implementación) |
| NADR-23 §5.8 R31 | PENDING | Wave 5.2 / Task 5.2.2 | Evaluation Provenance (ejecución, no implementación) |
| NADR-24 §5.1 R4 | PENDING | Wave 5.3 / Task 5.3.1 | Certificación (ejecución, no implementación) |
| NADR-24 §5.7 R29 | PENDING | Wave 5.3 / Task 5.3.2 | Certification Evidence (ejecución, no implementación) |

---

## 8. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_5_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.2.

**Hallazgos pre-identificados (carry-forward de HITOs y FASE_4_HANDOFF):**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo. Criterio: divergencia < 1% TED normalizado → experimental sin acción; divergencia ≥ 1% → investigar causa raíz. (Respaldado por FASE_4_HANDOFF §5.2 DF-04) | Gate 2 W2.4 Task 2.4.7 (implementación/investigación), Gate 5 W5.3 Task 5.3.3 (cierre administrativo) | Carry-forward de Fase 4 |
| DF-18 | Semántica de fallo heterogénea en 4 entry points | Gate 4 W4.2 Task 4.2.3 | Carry-forward de HITO 5.2 |
| DF-19 | Manifest en formato legacy (4 dimensiones) | Gate 1 W1.2 Task 1.2.3 (contrato), Gate 1 W1.3 Task 1.3.1 (ejecución de migración) | Carry-forward de HITO 5.1 |
| GAP-5.0-03 | Configuración implícita del corpus (rutas hardcoded) | Gate 4 W4.1 Task 4.1.3 | Carry-forward de HITO 5.0 |
| GAP-5.2-05 | Certification Boundary Integrity violation (sanitize_ground_truth_types.py) | Gate 2 W2.1 Task 2.1.2, Gate 4 W4.3 Task 4.3.2 | Carry-forward de HITO 5.2 |

**Carry-forwards from Phase 4 (no bloquean Fase 5):**
- DF-01: Tests tautológicos → Fase 6
- DF-02: Verificación ci.yml/pyproject.toml → Fase 6
- DF-03: Deuda LayoutBlockDraft → Gate futuro

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **ADR_F17_BIS_MASTER** define la visión arquitectónica de la Fase 17-BIS.
* **ADR_F17_BIS_05** define la decisión arquitectónica de la Fase 5.
* **NADRs 20-24** definen las reglas normativas obligatorias (166 reglas).
* **Este Execution Plan** define la secuencia operativa y el seguimiento de cumplimiento.
* **FASE_5_DEFERRED_FINDINGS_REGISTER** registra los hallazgos identificados durante la implementación.

Este documento **no prescribe implementaciones específicas, decisiones arquitectónicas, ni reglas normativas.**

Toda implementación que pretenda materializar una regla NADR deberá demostrar trazabilidad explícita hacia este Execution Plan y el NADR correspondiente.

---

## 10. FUTURE WORK

- Automatizar la generación del Traceability Appendix (§7) a partir del estado de las Tasks, eliminando la posibilidad de inconsistencias entre ambas secciones.
- Integrar el Status Dashboard (§6) con el sistema de CI para actualización automática.
- Evaluar la posibilidad de ejecutar el benchmark DF-04 en CI para regresión continua (Fase 6).
- Evaluar la automatización del PREFLIGHT como parte del pipeline de CI (Fase 6).

---

## 11. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 11.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 11.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2)
2. Redactar las **Notas de implementación** de la Task (§2.{X}.{Y})
3. Actualizar el `Derived Status` de las reglas implementadas en §7
4. Recalcular los contadores del Status Dashboard (§6)
5. Verificar que las reglas implementadas no aparecen como PENDING en §7

### 11.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave" (§2.{X}.{Z})
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 11.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist (§2.{X}.{Z})
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§3)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 11.5 Al cancelar una operación de Deployment

1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§4)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§11.3)

### 11.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN (166 reglas), no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.