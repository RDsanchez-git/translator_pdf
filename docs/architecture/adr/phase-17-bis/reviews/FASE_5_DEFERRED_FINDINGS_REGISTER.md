# FASE_5_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_5_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.16.0
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-09-05
**Última actualización:** 2026-09-13
**Derivado de:** `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` v1.2.2
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de Fase 5 (Baseline Certification), su clasificación, resolución y
evidencia empírica de los batches.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-09-05 | Emisión inicial. Esqueleto con hallazgos pre-registrados. |
| 0.2.0 | 2026-09-05 | Hardening documental: expansión de marco normativo, estados de evidencia, árbol de decisión, mapeo Finding→Task, plantillas. |
| 0.3.0 | 2026-09-05 | **Conversión a esqueleto dinámico de descubrimiento.** Se eliminan análisis detallados pre-escritos. Las secciones dinámicas (§2, §3, §4) quedan vacías, listas para recibir evidencia durante los Gate Exit Reviews. Los hallazgos pre-identificados (§9) se conservan únicamente como referencia de trazabilidad. |
| 0.4.0 | 2026-09-06 | **Wave 1.1 completada:** 4 hallazgos derivados registrados (H-5.1-1 a H-5.1-4). H-5.1-1 RESOLVED (pesaran1999.pdf encontrado e incluido como doc_07). H-5.1-2, H-5.1-3 IMPLEMENTATION_REQUIRED. H-5.1-4 PENDING_REVIEW. Métricas actualizadas. |
| 0.5.0 | 2026-09-06 | **Wave 1.2 completada:** (1) H-5.1-4 reclasificado de PENDING_REVIEW a RESOLVED — traits reclasificados con nombres correctos del catálogo vigente (scanned_noise, heavy_math, nested_tables, floating_figures); (2) H-5.1-5 registrado y RESOLVED — discrepancia de nombres de traits (DENSE_TYPOGRAPHY y MIXED_CONTENT no existen; HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise); (3) H-5.1-6 registrado y CLOSED (NAR) — contrato del manifest verificado como 6D plano en RawDocumentEntryDTO; (4) Manifest canónico generado y verificado (hash 62f0df16); (5) Métricas y estado actualizados. |
| 0.6.0 | 2026-09-09 | **Wave 1.3 completada:** (1) H-5.1-2 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — archivo temporal tmptu237h6p eliminado en Task 1.3.1; (2) H-5.1-3 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — AST legacy reemplazado por re-extracción en Task 1.3.8; (3) H-5.1-7 registrado y RESOLVED — parent_node_id=None en todos los GTs, consistente con Flat Design, verificado en curaduría; (4) H-5.1-8 registrado y CLOSED (NAR) — ManifestFingerprintCalculator.compute_hash() incluye page_count (verificado en source code); (5) H-5.1-9 registrado como ACCEPTED_LIMITATION — doc_02_double: fragmentación de ecuaciones por PyMuPDF en doble columna; (6) H-5.1-10 registrado como ACCEPTED_LIMITATION — doc_05_graph: labels de ejes como paragraphs; (7) H-5.1-11 registrado como RECLASSIFIED_FUTURE_PHASE — patrón Detect & Placeholder, fuera del scope de Fase 17-BIS (ADR §4); (8) Métricas y estado actualizados. |
| 0.7.0 | 2026-09-09 | **Wave 2.1 completada:** (1) H-5.2-1 registrado como IMPLEMENTATION_REQUIRED — doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6, requiere re-incorporación con pipeline OCR; (2) H-5.2-2 registrado y CLOSED (NAR) — GroundTruthLifecycleState tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED), diseño type-state confirmado por tests; (3) GAP-5.2-05 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — sanitize_ground_truth_types.py protegido con SealedOracleOverwriteError (fail-hard), 3 tests nuevos; (4) Manifest hash recalculado: 39cc80bd → fae41bb5 (post exclusión doc_06); (5) Baseline tests: 627 passed, 5 skipped (3 nuevos de GAP-5.2-05); (6) Métricas y estado actualizados. |
| 0.8.0 | 2026-09-09 | **Wave 2.2 completada:** (1) H-5.2-3 registrado y RESOLVED — canonicalization_lineage.json movido de ground_truth/ a canonical/ raíz (separación de concerns); (2) H-5.2-4 registrado y RESOLVED — freeze_ground_truth.py path corregido de benchmark_v1 a canonical; (3) H-5.2-5 registrado y CLOSED (NAR) — log duplicado eliminado de freeze_ground_truth.py; (4) DF-19 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — manifest en formato 6D completo y sellado; (5) Sellado ejecutado: manifest_hash 0fda7690, 6/6 GTs sellados con oracle_hash; (6) MIG-02 y MIG-06 ejecutados; (7) Métricas y estado actualizados. |
| 0.9.0 | 2026-09-09 | **Wave 2.3 completada:** (1) H-5.2-6 registrado como ACCEPTED_LIMITATION — ASTFingerprintPolicy.semantic_fingerprint() e identity_fingerprint() aplican .strip(), violando NADR-22 §5.3 R10-R12; divergencia confinada al tooling experimental (tools/evaluation/topology/); la ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no usa ASTFingerprintPolicy ni aplica .strip(); dominio canónico (DefaultNodeMatchingPolicy, CriticalityAwareCostContext) verificado libre de .strip(); (2) Métricas y estado actualizados. |
| 0.10.0 | 2026-09-10 | **Wave 2.4 completada, Gate 2 COMPLETED:** (1) DF-04 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — benchmark ejecutado con run_df04_benchmark.py sobre 6 documentos del corpus canónico sellado, divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double), 4 causas raíz documentadas (cost model, normalización, fingerprint H-5.2-6, estructura de árbol), APTED queda como experimental no-normativo (NADR-22 §5.1 R3); (2) Tasks 2.4.1-2.4.2, 2.4.4 completadas por construcción; (3) Task 2.4.3 implementada: CanonicalEngineConfiguration + ConfigurationFingerprintCalculator con module.qualname, 12 tests nuevos; (4) Task 2.4.5 implementada: configuration_fingerprint propagado en RegressionReport; (5) Task 2.4.6 completada: 6 tests de determinismo PASSED; (6) Gate 2 → COMPLETED (17/17 Tasks, 43/43 rules); (7) Métricas actualizadas: 23 hallazgos analizados (DF-04 cerrado), 9 resueltos. |
| 0.11.0 | 2026-09-10 | **Wave 3.1 completada (4 Tasks DONE):** (1) Tasks 3.1.1-3.1.4 DONE — definidas fases CAL/VAL/FINAL, partición por SHA-256, disjunción verificada, estrategia de independencia estadística documentada; (2) H-5.3-1 registrado como ACCEPTED_LIMITATION — calibración estadística no ejecutable con 6 documentos (N=6 < 20, NADR-23 R12 prohíbe presumir robustez), defaults evidence-informed por diseño, recalibración pendiente para corpus ≥20 con curvas precision-recall + bootstrap CI + human verdicts; (3) Dataset Independence Record creado en reviews/; (4) Métricas actualizadas: 24 hallazgos analizados, 4 aceptados como limitación. |
| 0.12.0 | 2026-09-10 | **Wave 3.2 completada (3 Tasks DONE):** (1) Tasks 3.2.1-3.2.3 DONE — protocolo de calibración definido (R4-R8), lifecycle CAL→VAL→FREEZE ejecutado (R14-R16), condiciones de validez científica documentadas (R26-R28); (2) Sanity validation ejecutada sobre 6 documentos: 5/6 HARD_FAIL, corpus NSS 0.6536, 106 Critical FN totales, 1 PASS (doc_07 tautológico); (3) H-5.3-2 registrado como ACCEPTED_LIMITATION — divergencia masiva entre runtime de producción y GTs curados, confirma problema estructural del extractor (PyMuPDFProvider), no paramétrico; (4) H-5.3-3 registrado como ACCEPTED_LIMITATION — GT de doc_07_pesaran no editado en curaduría, NSS=1.0000 es tautología (extractor contra sí mismo), documento contiene tablas no extraídas por PyMuPDF (fuentes Type 3), curaduría real diferida con ampliación de corpus; (5) Parameter Identity (fingerprint) b942fc95... congelada sobre defaults normativos; (6) Calibration Protocol Record creado; (7) Métricas actualizadas: 26 hallazgos analizados, 6 aceptados como limitación. |
| 0.13.0 | 2026-09-11 | **Wave 3.3 completada (3 Tasks DONE), Gate 3 COMPLETED:** (1) Tasks 3.3.1-3.3.3 DONE — Calibration Provenance Record materializado con 5 campos R18 (run NONE, origen NORMATIVE_DESIGN), Parameter freeze ejecutado vía MIG-08 (parameter_identity 67841171..., enforcement R24 vía test sobre artefacto del repo PASSED, inmutabilidad R25 verificada), Evaluation Provenance Record emitido con kind SANITY_VALIDATION y limitaciones H-5.3-1/2/3 (idempotencia por kind verificada, R33); (2) Sin nuevos hallazgos en Wave 3.3 (operación de materialización, no de descubrimiento); (3) Nuevo módulo de dominio `core/benchmark/topology/regression/provenance.py` con dataclasses frozen, invariantes de thresholds y serialización canónica; (4) 18 tests unitarios + 7 tests de integración PASSED; (5) Provenance Record creado (`FASE_5_WAVE_3_3_PROVENANCE_RECORD.md` v1.0.0); (6) Artefactos de freeze materializados en `reports/calibration/`; (7) Gate 3 → COMPLETED (10/10 Tasks, 31/31 rules); (8) Baseline tests: 665 passed, 5 skipped; (9) Métricas actualizadas: archivos creados totales = 24; sin cambios en contadores de hallazgos (Wave 3.3 no generó nuevos findings). |
| 0.14.0 | 2026-09-12 | **Wave 4.1 y Wave 4.2 completadas (6 Tasks DONE, 22 reglas):** (1) DF-18 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — semántica de fallo uniforme implementada en 4 entry points (`freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`) con `main() -> int` + `run_entry(main)`; `core/shared/exit_codes.py` con taxonomía uniforme (EXIT_OK=0, EXIT_CERTIFICATION_REJECTED=1, EXIT_EXECUTION_FAILURE=2); `core/shared/errors.py` con `IndexedError` para códigos indexables; `tools/evaluation/entry_guard.py` como guard de traducción R19; (2) GAP-5.0-03 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED — 5 entry points migrados a CLI con `--corpus-dir` required (`bootstrap_corpus`, `freeze_ground_truth`, `generate_golden_draft`, `generate_pymupdf_candidate` con `--pdf-dir`/`--out-dir`, `sanitize_ground_truth_types`); aritmética de cierre: 5 remediados + 4 ya explícitos + 1 deprecated que hereda + 1 fuera de scope = 11 entry points auditados; (3) H-5.4-1 registrado como ACCEPTED_LIMITATION (evidencia forense) — pre-remediación, `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]`; falso positivo operacional confirmado (R16, R18); (4) H-5.4-2 registrado como ACCEPTED_LIMITATION (evidencia forense) — pre-remediación, run espurio de `generate_pymupdf_candidate.py` mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (revertidos con `git checkout`); evidencia dura del riesgo DF-18/GAP-5.0-03; (5) GF-01 registrado como Governance Finding — conflicto real entre NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) y NADR-24 §5.4 R15-R17 (2 = fallo de ejecución); resolución por separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta CI; runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24; `run_regression` NO se toca en Wave 4.2; (6) D1 aplicado en `generate_golden_draft.py`: helper puro `classify_document_error` (sealed oracle → skip, resto → failure), contadores separados `skips`/`failures`, idempotencia R33 (re-ejecución sobre corpus sellado mantiene exit 0); (7) D2 aplicado en `sanitize_ground_truth_types.py`: `--allow-missing-manifest` override explícito e indexable; sin manifest y sin override → `IndexedError SANITIZE-001` (NADR-24 R26); evolución normativa NADR-21 → NADR-24 documentada; (8) D3 aplicado en `freeze_parameters.py`: eliminación de `EXIT_CONTRACT_VIOLATION=1`, unificación en `EXIT_EXECUTION_FAILURE=2`; (9) Tests actualizados: `test_no_manifest_aborts_without_override`, `test_no_manifest_with_override_sanitizes`, `test_invalid_timestamp_returns_exit_2`, `test_missing_report_returns_exit_2_without_partial_state`; 5 tests nuevos en `test_exit_codes_and_guard.py` (TestRunEntryTranslation + TestClassifyDocumentError); (10) Nuevo paquete de dominio `core/benchmark/certification/` (3 módulos); 24 tests nuevos totales (14 de `test_certification_preflight.py` + 5 de `test_exit_codes_and_guard.py` + 5 actualizados); baseline: 685 passed, 5 skipped; (11) Gate 4 Status → IN PROGRESS (6/13 Tasks DONE, 22/37 rules DONE); (12) Métricas actualizadas: 29 hallazgos analizados, 13 resueltos, 1 Governance Finding registrado. |
| 0.15.0 | 2026-09-13 | **Wave 4.3 completada (4 Tasks DONE, 9 reglas nuevas en Gate 4):** (1) Task 4.3.1 DONE — Boundary integrity verificada mediante AUDIT forense (5 comandos) + 10 contract tests en `test_certification_boundary.py`; SealedOracle frozen (model_config frozen=True), sin mutadores de instancia, asignación bloqueada (ValidationError); LifecycleTransitionAuthority importada únicamente por `use_cases.py` (dominio) y `freeze_ground_truth.py` (sellado MIG-06, O-4.3-3); 3 adaptadores de `ground_truth_store.py` apuntan exclusivamente a `base_path/ground_truth`; tooling de certificación no importa puertos de escritura GT; (2) Task 4.3.2 DONE — GAP-5.2-05 verificación formal de la protección implementada en Wave 2.1 (Task 2.1.2): cadena sanitize/use cases/override D2 verificada; `sanitize_ground_truth_types.py` verifica sellado antes de escribir (raise `SealedOracleOverwriteError`); `GenerateGoldenDraftUseCase` verifica estado antes de escribir; override `--allow-missing-manifest` explícito e indexable (fuera de ejecución certificante); GAP-5.2-05 estado actualizado de `RESOLVED (primaria)` a `RESOLVED` (verificación formal completada); (3) Task 4.3.3 DONE — Evidence completeness implementada: `core/benchmark/certification/evidence.py` con `CertificationEvidence` (7 elementos R29 + `evaluation_kind` + `result_identity`), `compute_corpus_content_identity` (SHA-256 de SHA-256 ordenados, fail-fast ante vacío NADR-20 R1), `serialize_evidence` determinista; GF-02 registrado: crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3); `corpus_identity` = compuesto de contenido (estable entre sellados), `manifest_identity` = `manifest_hash` (cambia al sellar); artefactos de Wave 3.3 permanecen válidos; (4) Task 4.3.4 DONE — POST-RUN VALIDATION implementada: `core/benchmark/certification/post_run.py` con `validate_post_run` (5 checks, violaciones nombradas por elemento R29); wiring con disco diferido a Gate 5 Task 5.2.1; (5) O-4.3-3 registrado: `freeze_ground_truth.py` importa `LifecycleTransitionAuthority` (entry point de sellado MIG-06; R28 prohíbe bypassear, no invocar; allowlist extendido con justificación); (6) Nuevo paquete `core/benchmark/certification/` expandido a 4 módulos (contract, preflight, evidence, post_run); 18 tests nuevos (10 boundary + 12 evidence - 4 overlap = 18 netos); baseline: 713 passed, 5 skipped; (7) Gate 4 Status → IN PROGRESS (10/13 Tasks DONE, 31/37 rules DONE; Wave 4.4 pendiente); (8) Métricas actualizadas: 31 hallazgos analizados, 14 resueltos, 2 Governance Findings registrados (GF-01, GF-02). |
| 0.16.0 | 2026-09-13 | **Wave 4.4 completada (3 Tasks DONE, 4 reglas), Gate 4 COMPLETED (13/13 tasks, 37/37 rules):** (1) Task 4.4.1 DONE — Determinismo operacional (R32) verificado: tooling de certificación determinista por construcción (timestamps inyectados externamente, `sort_keys=True` en serialización, hashes sobre bytes canónicos); O-4.4-1 registrado: `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en certificación; (2) Task 4.4.2 DONE — Idempotencia lógica (R33) verificada: cero operaciones append a archivos en tooling de certificación; escrituras usan `write_text`/`write_bytes` (overwrite); O-4.4-2 registrado: `reporter.py:71 np.random.choice` en bootstrap estadístico, no en reporte de certificación; (3) Task 4.4.3 DONE — Recovery determinable (R34-R35): estado post-fallo determinable vía `validate_post_run` (violaciones nombradas por elemento); atomicidad física solo donde el dominio la exige; O-4.4-3 registrado: `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall); no se migra porque R34/R35 no la exigen para reportes y añadiría superficie de cambio sin beneficio normativo (YAGNI); 7 tests nuevos (3 determinismo + 2 idempotencia + 2 recovery); baseline: 720 passed, 5 skipped (713 + 7); (4) Gate 4 → COMPLETED (13/13 Tasks, 37/37 rules); (5) Gate 5 habilitado; (6) Métricas actualizadas: 34 hallazgos analizados, 4 observaciones registradas (O-4.3-3, O-4.4-1, O-4.4-2, O-4.4-3), 2 Governance Findings (GF-01, GF-02). |
---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_05 > NADR-F17BIS-20..24 > PHASE_17BIS_FASE5_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

Este registro no tiene autoridad normativa. Su función es operacional:
documentar hallazgos, clasificaciones, resoluciones, batches y evidencia.

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Scientific Baseline sea una
> representación determinista, reproducible y arquitectónicamente fiel del
> pipeline productivo que vamos a certificar?"*

Sub-preguntas aplicables durante la revisión:

- ¿El finding compromete la inmutabilidad de un Ground Truth sellado?
- ¿El finding compromete la biyección PDF↔oráculo exigida por Zero Partial Sealing?
- ¿El finding compromete el determinismo de serialización, evaluación o hashing?
- ¿El finding permite un fallo silencioso, un falso PASS o un exit code incorrecto?
- ¿El finding mezcla identidades que deben permanecer desacopladas?
- ¿El finding mezcla datos de calibración con datos de evaluación final?
- ¿El finding impide auditar el linaje del corpus, oráculo, configuración o parámetros?
- ¿El finding contradice una decisión congelada en ADR/NADR?

### 0.3 Reglas transversales aplicables

- **Zero Partial Sealing** — `ADR_F17_BIS_MASTER §5`: Un corpus NO podrá entrar en estado `SEALED` si no existe una correspondencia biyectiva completa entre los PDFs declarados y sus oráculos AST auditados ($N_{\text{PDF}} = N_{\text{GT}}$).
- **Determinismo y Reproducibilidad** — `ADR_F17_BIS_MASTER §5`: Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser determinista.
- **Desacoplamiento de Identidades** — `ADR_F17_BIS_MASTER §5`: La arquitectura debe mantener diferenciados los conceptos de AST Schema Version, Corpus Version, Identity Hash, Oracle Hash, Baseline Hash, Parameter Identity y Evaluation Configuration Identity.
- **Cero Fallos Silenciosos** — `ENGINEERING_PRINCIPLES §IV`: Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un warning indexable explícito o fallar duro.
- **Trazabilidad Absoluta** — `ENGINEERING_PRINCIPLES §IV`: El linaje del dato debe propagarse intacto a través de todas las transformaciones del pipeline.
- **Calidad sobre Velocidad** — `ENGINEERING_PRINCIPLES`: No se acepta deuda técnica deliberada en dominio core.
- **Cero Sesgo de Confirmación** — `ENGINEERING_PRINCIPLES`: Las decisiones de clasificación deben basarse en evidencia, invariantes comprobables y métricas.
- **Inmutabilidad de Sealed** — `NADR-F17BIS-21 §5.4 R19`, `NADR-F17BIS-24 §5.6 R25`: Un Ground Truth en estado `SEALED` no debe modificarse, sobrescribirse ni eliminarse. No existe rollback mutativo post-sealing.
- **Calibration ≠ Evaluation** — `NADR-F17BIS-23 §5.1 R2`: Los resultados de FINAL EVALUATION no deben participar en la selección, ajuste o justificación de parámetros.

### 0.4 Corolario forense

> *Un finding solo es válido si puede demostrarse mediante evidencia de código,
> artefacto, test, reporte o documento congelado. Un indicio —nombre de archivo,
> comentario, convención informal o sospecha— no constituye evidencia suficiente
> para clasificar un finding como gap confirmado.*

Implicaciones:

- Todo finding debe clasificar explícitamente su estado de evidencia: `gap confirmado`, `hipótesis pendiente`, `no-gap`.
- Ningún finding puede cerrarse como `RESOLVED` sin evidencia empírica.
- Ningún finding puede convertirse en `GF` sin citar la contradicción normativa exacta entre niveles de gobernanza.
- Ningún finding puede justificar mutación in-place de un artefacto sellado.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-5.{N}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF en Fase 5 |
| `GAP-5.{N}-{XX}` | Gap heredado de HITO | Gap pre-identificado durante auditorías/hitos previos de Fase 5 |

Notas:

- Los `DF-01`, `DF-02` y `DF-03` son carry-forwards de Fase 4 y no bloquean Fase 5.
- Los hallazgos activos que afectan Fase 5 son: `DF-04`, `DF-18`, `DF-19`, `GAP-5.0-03`, `GAP-5.2-05`.
- Los IDs nuevos generados durante Fase 5 deben asignarse secuencialmente a partir del siguiente identificador disponible.

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `PENDING_REVIEW` | Identificado, pendiente de clasificación |
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `RESOLVED — MIGRATION` | Artefacto migrado a formato vigente |
| `RESOLVED — CONFIGURATION` | Configuración explícita implementada |
| `RESOLVED — FAILURE SEMANTICS` | Semántica de fallo/exit codes corregida |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Diferido a fase futura con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación dentro del scope de Fase 5 |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `CONVERTED_TO_GF` | Convertido en Governance Finding |
| `DEFERRED — FASE {X}` | Diferido a fase específica con ADR pendiente |

### 1.3 Estados de evidencia

| Estado | Significado |
|--------|-------------|
| `GAP_CONFIRMED` | Gap confirmado con evidencia |
| `HYPOTHESIS_PENDING` | Hipótesis plausible, pendiente de evidencia |
| `NO_GAP` | No hay gap; correcto por diseño o falso positivo |
| `PARTIAL_GAP` | Gap parcialmente confirmado o acotado |
| `GOVERNANCE_CONFLICT` | Conflicto entre niveles normativos |

### 1.4 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos, tests, documentos o artefactos auditados.
- Cada finding **DEBE** distinguir: gap confirmado, hipótesis pendiente, no-gap, limitación aceptada.
- Ningún finding se cierra sin evidencia de código, test, artefacto o documento.
- No se implementa código durante el Gate Exit Review. La implementación se agrupa en batches posteriores.
- Todo finding que involucre un oráculo sellado **DEBE** verificar que no se propone mutación in-place.
- Todo finding que implique cambios normativos **DEBE** convertirse en `GF`.
- Todo finding diferido a fase futura **DEBE** tener destino explícito y justificación.

### 1.5 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Hallazgo validado | Actualizar Evidence Status (`GAP_CONFIRMED`, `NO_GAP`, etc.) |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación planificado | Asociar findings a batch |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Hallazgo convertido en GF | Crear entrada `GF-{XX}` y referenciar DF original |
| Fase cerrada | Estado del documento → `ARCHIVED` |

---

## 2. GATE EXIT REVIEWS

Los Gate Exit Reviews se agregan dinámicamente conforme se ejecutan los Gates del
Execution Plan. Cada Exit Review aplica el árbol de decisión estándar y registra
las decisiones tomadas sobre los hallazgos pre-identificados y los nuevos
hallazgos descubiertos durante la implementación.

### Árbol de decisión estándar

```text
1. ¿Sigue siendo válido el hallazgo?
   ├── NO  → CLOSED (NAR)
   └── SÍ  → continuar

2. ¿Existe evidencia suficiente?
   ├── NO  → REVIEW_REQUIRED
   └── SÍ  → continuar

3. ¿Es un problema técnico resoluble dentro del scope del Gate/Fase?
   ├── SÍ  → IMPLEMENTATION_REQUIRED / RESOLVED
   └── NO  → continuar

4. ¿Es un conflicto normativo entre niveles de gobernanza?
   ├── SÍ  → CONVERTED_TO_GF
   └── NO  → continuar

5. ¿Debe diferirse a fase futura?
   ├── SÍ  → RECLASSIFIED_FUTURE_PHASE / DEFERRED — FASE {X}
   └── NO  → ACCEPTED_LIMITATION o REVIEW_REQUIRED
```

### 2.1 Gate 1 Exit Review — Canonical Corpus & Ground Truth Qualification

**Estado:** ⏳ PENDING — Gate 1 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 1 / Waves 1.1, 1.2, 1.3
**Hallazgos pre-asignados:** DF-19

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 1 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 1

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

### 2.2 Gate 2 Exit Review — GT Sealing & Canonical Evaluation Configuration

**Estado:** ✅ COMPLETED — Gate 2 cerrado con 17/17 Tasks DONE y 43/43 rules DONE.
**Fecha de ejecución:** 2026-09-10
**Execution Plan:** Gate 2 / Waves 2.1, 2.2, 2.3, 2.4
**Hallazgos pre-asignados:** GAP-5.2-05, DF-04

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| GAP-5.2-05 | ✅ Sí | sanitize_ground_truth_types.py protegido con SealedOracleOverwriteError (fail-hard), 3 tests nuevos PASSED | ✅ Sí | ✅ Sí | RESOLVED | Protección de SealedOracle implementada y verificada (Wave 2.1 Task 2.1.2) |
| DF-04 | ✅ Sí | Benchmark ejecutado: divergencia 8.56% promedio, 22.63% máxima, 4 causas raíz documentadas | ✅ Sí | ✅ Sí | RESOLVED | APTED queda como experimental no-normativo (NADR-22 §5.1 R3) |

**Resumen:**
- RESOLVED: 2 (GAP-5.2-05, DF-04)
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 2

| Decisión | Task | Justificación |
|----------|------|---------------|
| ConfigurationFingerprint con module.qualname | 2.4.3 | Unicidad absoluta de identidad tipada, evita strings libres y colisiones entre módulos (ENGINEERING_PRINCIPLES §III) |
| Default del composition root permanece UnitCostContext | 2.3.2 | Caller explícito en run_regression.py, Explicit over Implicit + YAGNI |
| APTED como experimental no-normativo | 2.4.7 | Divergencia 8.56% con 4 causas raíz documentadas, NADR-22 §5.1 R3 |

#### Lecciones aprendidas

- La divergencia algorítmica entre motores TED (ZhangShasha vs APTED) es esperable y documentable. Las 4 causas raíz (cost model, normalización, fingerprint, estructura de árbol) son factores conocidos que no indican bugs en ninguno de los dos motores.
- El uso de `type(x).__module__ + "." + type(x).__qualname__` como identidad tipada es superior a strings libres o enums nuevos para fingerprints de configuración.

---

### 2.3 Gate 3 Exit Review — Scientific Calibration & Experimental Provenance

**Estado:** ✅ COMPLETED — Gate 3 cerrado con 10/10 Tasks DONE y 31/31 rules DONE.
**Fecha de ejecución:** 2026-09-10 (inicio), 2026-09-11 (cierre)
**Execution Plan:** Gate 3 / Waves 3.1, 3.2, 3.3
**Hallazgos pre-asignados:** H-5.3-1 (derivado en Wave 3.1)

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| H-5.3-1 | ✅ Sí | N=6 < 20 identidades, NADR-23 R12 prohíbe presumir robustez estadística. Dataset Independence Record documenta estrategia. | ✅ Sí | ✅ Sí | ACCEPTED_LIMITATION | Calibración estadística no ejecutable con corpus actual; defaults evidence-informed por diseño, recalibración pendiente para corpus ≥20 |
| H-5.3-2 | ✅ Sí | Sanity validation: 5/6 HARD_FAIL, corpus NSS 0.6536, 106 Critical FN totales. reports/sanity_validation/regression_report.{json,md} | ✅ Sí | ✅ Sí | ACCEPTED_LIMITATION | Divergencia masiva runtime vs GTs es estructural (limitación PyMuPDFProvider H-5.1-9, H-5.1-10), no paramétrica. Refuerza decisión de no calibrar con N=6. |
| H-5.3-3 | ✅ Sí | doc_07 NSS=1.0000 con global_ted=0.0 (tautología). Curation Report Wave 1.3 documenta observación "fuentes Type 3" sin edición. PDF contiene Table 1, Table 2 visibles. | ✅ Sí | ✅ Sí | ACCEPTED_LIMITATION | GT no editado = salida cruda del extractor. PASS es tautológico, no validación positiva. Curaduría real diferida con ampliación de corpus (H-5.2-1). |

(Wave 3.3 no generó nuevos hallazgos. Las Tasks 3.3.1-3.3.3 materializaron los registros de provenance conforme al diseño sin desviaciones. Los tres findings en la tabla son de Waves 3.1 y 3.2 y se referencian en el campo `limitations` del Evaluation Provenance Record.)

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- ACCEPTED_LIMITATION: 3 (H-5.3-1, H-5.3-2, H-5.3-3)
- Nuevos hallazgos registrados en Wave 3.3: 0

#### Decisiones arquitectónicas congeladas en Gate 3

| Decisión | Task | Justificación |
|----------|------|---------------|
| LOCAL_CALIBRATION_SET = ∅ con N=6 | 3.1.4 | NADR-23 R12 prohíbe presumir robustez estadística con <20 identidades. Defaults de diseño (no calibrados) validados como sanity check, no como calibración empírica. |
| Regla anti-leakage SANITY→parámetros | 3.1.4 | NADR-23 R2: resultados de SANITY_VALIDATION_SET MUST NOT modificar nss_hard_fail, nss_warning, cost_weights ni warning_threshold. |
| Protocolo de calibración APROBADO CONDICIONAL | 3.2.1 | 8 elementos del protocolo definidos (R5). Ejecución condicionada a corpus ≥20. Algoritmo de búsqueda diferido hasta momento de ejecución (R6). |
| Defaults = NORMATIVOS, no CALIBRADOS | 3.2.3 | Distinción verificable (R27, R28): parámetros de diseño arquitectónico con justificación explícita, no resultado de tuning ad-hoc. |
| doc_07 no-informativo para validación | 3.2.3 | Tautología por construcción (GT sin editar = salida del extractor). Curaduría diferida agrupada con ampliación de corpus. |
| Parameter freeze con identidad separada de configuración | 3.3.2 | Cambio de motor sin cambio de parámetros NO genera nueva parameter identity (distinción R20/R25); evita falsas nuevas líneas de certificación. |
| Evaluation record por kind con idempotencia (R33) | 3.3.3 | Nombre acotado por kind permite FINAL_EVALUATION sobre freeze existente sin caer en no-op; trazabilidad dura apunta a result_identity. |

#### Lecciones aprendidas

- Con corpus < 20 documentos, la calibración estadística (LOOCV, bootstrap, curva precision-recall) no es metodológicamente válida. La alternativa honesta es documentar defaults como evidence-informed por diseño y planificar recalibración cuando el corpus alcance tamaño suficiente.
- La industria (GROBID, DocLayNet, Nougat) no publica umbrales PASS/WARNING/HARD_FAIL transferibles para regresión topológica de papers científicos. Los umbrales son específicos del caso de uso y requieren calibración local con learning curves.
- La divergencia masiva entre runtime y GTs (106 Critical FN) confirma que el problema es el extractor (PyMuPDFProvider), no los thresholds. Los defaults (0.80/0.95) están funcionando correctamente al detectar la divergencia.
- Un PASS perfecto (NSS=1.0) en sanity validation puede ser señal de tautología (GT = salida del extractor) y no de calidad. La curaduría real es indispensable para validación positiva.
- La separación entre parameter_identity y configuration_identity resuelve un bug semántico latente: sin separación, un cambio de motor (normalización, matching) sin tocar thresholds falsamente invalidaría una certificación vigente.
- El enforcement de R24 mediante un test que recalcula la identidad desde los defaults del dominio y la compara con el artefacto del repo (`test_repo_freeze_artifact_matches_domain_defaults`) es la forma correcta de cerrar el ciclo: la identidad no es solo declarada, es verificable en CI.

---

### 2.4 Gate 4 Exit Review — Certification Tooling & Execution Safety

**Estado:** ✅ COMPLETED — Gate 4 cerrado con 13/13 Tasks DONE y 37/37 rules DONE.
**Fecha de ejecución:** 2026-09-11 (inicio), 2026-09-13 (cierre)
**Execution Plan:** Gate 4 / Waves 4.1, 4.2, 4.3, 4.4
**Hallazgos pre-asignados:** GAP-5.0-03, DF-18, GAP-5.2-05

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| GAP-5.0-03 | ✅ Sí | 5 entry points con corpus hardcodeado migrados a CLI con `--corpus-dir` required; 11 entry points auditados (5 remediados + 4 ya explícitos + 1 deprecated + 1 fuera de scope) | ✅ Sí | ✅ Sí | RESOLVED | Configuración explícita implementada (Wave 4.1 Task 4.1.3) |
| DF-18 | ✅ Sí | 4 entry points con `main() -> int` + `run_entry(main)`; `core/shared/exit_codes.py` con taxonomía uniforme; códigos indexables; D1 (skips/failures), D2 (override `--allow-missing-manifest`), D3 (unificación exit codes) | ✅ Sí | ✅ Sí | RESOLVED | Semántica de fallo uniforme implementada (Wave 4.2 Tasks 4.2.1-4.2.3) |
| GAP-5.2-05 | ✅ Sí | Remediación primaria en Wave 2.1 Task 2.1.2; verificación formal de boundary completada en Wave 4.3 Task 4.3.2 (cadena sanitize/use cases/override D2 verificada) | ✅ Sí | ✅ Sí | RESOLVED | Protección de SealedOracle implementada y verificación formal completada |
| H-5.4-1 | ✅ Sí | Pre-remediación: `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con `[SUCCESS]` | ✅ Sí | ✅ Sí | ACCEPTED_LIMITATION | Evidencia forense del falso positivo operacional (R16, R18) que motivó la remediación |
| H-5.4-2 | ✅ Sí | Pre-remediación: run espurio de `generate_pymupdf_candidate.py` mutó 4 artefactos trackeados (revertidos con `git checkout`) | ✅ Sí | ✅ Sí | ACCEPTED_LIMITATION | Evidencia forense del riesgo DF-18/GAP-5.0-03 que motivó la remediación |
| GF-01 | ✅ Sí | Conflicto NADR-19 §5.5 R22 (`run_regression` 0/1/2 PASS/WARNING/HARD_FAIL) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución) | ❌ No (resuelto por diseño) | ❌ No (gobernanza) | Documentado (no resuelto por diseño) | Separación de scope: `run_regression` conserva taxonomía NADR-19; runner de Gate 5 implementa NADR-24 |
| O-4.3-3 | ✅ Sí | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority`; AUDIT forense confirma entry point de sellado MIG-06 que orquesta ciclo de vida en memoria invocando la autoridad; `TestCertificationModulesWithoutGtWritePorts` verifica que tooling certificante no importa puertos de escritura GT | ✅ Sí | ✅ Sí | Observación (no Governance Finding) | R28 prohíbe bypassear la autoridad, no invocarla; allowlist extendido con justificación; sin refactor de código congelado de Gate 2 (YAGNI) |
| GF-02 | ✅ Sí | Crosswalk normativo: NADR-23 R18 define corpus_identity como "SHA-256 del manifest"; NADR-24 R29 + NADR-20 exigen separar corpus identity (compuesto de contenido) de manifest identity (manifest_hash); evidencia en `FASE_5_WAVE_4_3_EVIDENCE_RECORD.md` | ❌ No (interpretación normativa) | ❌ No (gobernanza) | Documentado (interpretación normativa) | Artefactos de Wave 3.3 permanecen válidos; crosswalk documenta mapeo entre diccionarios |
| O-4.4-1 | ✅ Sí | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en flujo de certificación | ✅ Sí | ✅ Sí | Observación (sin impacto para Gate 4) | Timestamp en orquestador de benchmark, no en tooling de certificación; verificar en Gate 5 si se propaga al reporte |
| O-4.4-2 | ✅ Sí | `reporter.py:71 np.random.choice` es bootstrap del StatisticalComparator (análisis estadístico post-benchmark), no forma parte del reporte de regresión de certificación | ✅ Sí | ✅ Sí | Observación (sin impacto para Gate 4) | No-determinista por diseño, confinado al análisis de significancia estadística |
| O-4.4-3 | ✅ Sí | `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall); si el proceso muere a mitad de escritura, el reporte puede quedar corrupto | ✅ Sí | ✅ Sí | Observación (gap documentado sin acción) | No se migra porque R34/R35 no exigen atomicidad física para reportes; YAGNI; ventana de corrupción cubierta por POST-RUN VALIDATION + re-ejecución manual |

**Resumen:**
- RESOLVED: 3 (GAP-5.0-03, DF-18, GAP-5.2-05)
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- ACCEPTED_LIMITATION: 2 (H-5.4-1, H-5.4-2)
- Governance Findings: 2 (GF-01, GF-02)
- Observaciones: 4 (O-4.3-3, O-4.4-1, O-4.4-2, O-4.4-3)
- Nuevos hallazgos registrados en Waves 4.1-4.4: 3 (H-5.4-1, H-5.4-2, GF-01) + 5 (O-4.3-3, GF-02, O-4.4-1, O-4.4-2, O-4.4-3) = 8 totales

#### Decisiones arquitectónicas congeladas en Gate 4 (Waves 4.1-4.3)

| Decisión | Task | Justificación |
|----------|------|---------------|
| `evaluate_preflight` como Functional Core puro | 4.1.2 | 13 kwargs keyword-only, sin imports de infra ni composition root; determinista e idempotente (R9); reutilización estricta de LoadCorpusManifestUseCase, BaselineCompletenessVerifier, RegressionAdapter, ConfigurationFingerprintCalculator |
| `SystemExit` propaga limpio desde argparse | 4.1.3 | `argparse.sys.exit(2)` ante required ausente coincide con categoría (c) de NADR-24 por diseño; `run_entry` no captura `SystemExit` (hereda de `BaseException`, no `Exception`) |
| `classify_document_error` como helper puro (D1) | 4.2.2 | Sealed oracle → skip (idempotencia R33: re-ejecución sobre corpus sellado mantiene exit 0); resto → failure (unidad obligatoria no procesada); contadores separados |
| Override explícito `--allow-missing-manifest` (D2) | 4.2.3 | Sin manifest y sin override → `IndexedError SANITIZE-001` (NADR-24 R26: verificación de sellado imposible); con override → warning indexable `[SANITIZE-W01]`; evolución normativa NADR-21 → NADR-24 documentada |
| Unificación de exit codes en `freeze_parameters.py` (D3) | 4.2.3 | Eliminación de `EXIT_CONTRACT_VIOLATION=1`; timestamp inválido, manifest ausente, reporte incompleto y conflicto de freeze → todos categoría (c) `EXIT_EXECUTION_FAILURE=2` |
| `run_regression` NO se toca en Wave 4.2 (GF-01) | 4.2.3 | Separación de scope: `run_regression` conserva taxonomía NADR-19 §5.5 R22 (0/1/2 PASS/WARNING/HARD_FAIL) como compuerta CI; runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24 traduciendo veredicto científico a categoría (a)/(b) |
| `freeze_ground_truth.py` en allowlist R28 (O-4.3-3) | 4.3.1 | Entry point de sellado (MIG-06) que orquesta el ciclo de vida en memoria invocando la autoridad; R28 prohíbe bypassear, no invocar; sin refactor de código congelado de Gate 2 (YAGNI) |
| Crosswalk GF-02 sin re-freeze de artefactos | 4.3.3 | Artefactos de Wave 3.3 permanecen válidos (su valor es inequívoco); crosswalk documenta el mapeo entre diccionarios NADR-23 y NADR-24 |
| `CertificationEvidence` como Functional Core puro | 4.3.3 | No lee disco; identidades llegan computadas por Shell con calculadores existentes (Reuse Before Invent); `serialize_evidence` determinista (sort_keys, indent fijo) |
| `validate_post_run` wiring diferido a Gate 5 | 4.3.4 | No existe RUN de certificación que post-validar hasta Gate 5 Task 5.2.1; Functional Core implementado y testeado, Shell + disco en Gate 5 |
| Determinismo operacional por construcción (O-4.4-1) | 4.4.1 | Timestamps inyectados externamente; `sort_keys=True` en serialización; hashes sobre bytes canónicos |
| Idempotencia por overwrite (O-4.4-2) | 4.4.2 | Cero operaciones append a archivos; escrituras usan `write_text`/`write_bytes` en modo overwrite |
| Recovery determinable sin atomicidad física (O-4.4-3) | 4.4.3 | Estado post-fallo determinable vía `validate_post_run`; atomicidad física solo donde el dominio la exige; reportes usan `write_text` directo (no atómico a nivel de syscall); YAGNI + POST-RUN VALIDATION cubre ventana de corrupción |

#### Lecciones aprendidas

- El falso positivo operacional (exit 0 con 0 documentos indexados) es evidencia forense dura del riesgo de configuración implícita + semántica de fallo heterogénea. La remediación GAP-5.0-03 + DF-18 elimina el riesgo de raíz.
- La separación entre skips (esperados, idempotentes) y failures (unidades obligatorias no procesadas) es crítica para R33 (idempotencia): re-ejecutar `generate_golden_draft.py` sobre corpus sellado debe mantener exit 0, no degradar a exit 2.
- El conflicto normativo GF-01 (NADR-19 vs NADR-24) se resuelve por separación de scope, no por modificación de `run_regression`. La taxonomía NADR-19 es correcta para su propósito (compuerta CI de regresión); la taxonomía NADR-24 es correcta para certificación. El runner de Gate 5 traduce entre ambas.
- El override explícito `--allow-missing-manifest` conserva operatividad legacy (corpus sin manifest) pero la hace explícita e indexable, cumpliendo R26 (verificación de sellado antes de modificar) sin romper tests cerrados de Gate 2.
- La arquitectura Hexagonal (Functional Core / Imperative Shell) permite implementar PREFLIGHT, CertificationEvidence y PostRunValidator con dominio puro y Shell con I/O, facilitando tests unitarios sin mocks de infraestructura.
- El crosswalk GF-02 demuestra que la misma entidad puede tener nombres diferentes en distintos scopes normativos (NADR-23 vs NADR-24); la resolución es documentar el mapeo, no renombrar artefactos ya materializados (estabilidad de baseline).
- R28 (autoridad de lifecycle) prohíbe bypassear la autoridad, no invocarla; `freeze_ground_truth.py` la invoca correctamente (sellado MIG-06), por lo que pertenece al allowlist sin violar la regla.
- La atomicidad física (`tempfile + os.replace`) solo es requerida donde el dominio la exige (oráculos sellados, candidatos de GT). Para reportes de certificación, `write_text` directo es suficiente; si el proceso muere a mitad, el operador re-ejecuta manualmente (recuperación humana, no automática).
- El determinismo operacional se garantiza por construcción: timestamps inyectados externamente, serialización con `sort_keys=True`, hashes sobre bytes canónicos. No requiere mecanismos adicionales.
- La idempotencia lógica se garantiza por overwrite: cero operaciones append a archivos; un residuo pre-planted es reemplazado íntegramente, no mezclado con contenido nuevo.

---

### 2.5 Gate 5 Exit Review — End-to-End Certification & Baseline Freeze

**Estado:** ⏳ PENDING — Gate 5 no ha iniciado.
**Fecha de ejecución:** —
**Execution Plan:** Gate 5 / Waves 5.1, 5.2, 5.3
**Hallazgos pre-asignados:** DF-04 (cierre administrativo)

| DF/GF | ¿Válido? | Evidencia | ¿Resoluble en Gate? | ¿Técnico? | Decisión | Motivo |
|-------|----------|-----------|---------------------|-----------|----------|--------|
| — | — | — | — | — | — | Pendiente de ejecución del Gate 5 Exit Review |

**Resumen:**
- RESOLVED: 0
- IMPLEMENTATION_REQUIRED: 0
- REVIEW_REQUIRED: 0
- CLOSED (NAR): 0
- CONVERTED_TO_GF: 0
- Nuevos hallazgos registrados: 0

#### Decisiones arquitectónicas congeladas en Gate 5

| Decisión | Task | Justificación |
|----------|------|---------------|
| — | — | — |

#### Lecciones aprendidas

- —

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs/GAPs |
|--------------|----------|----------|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED` (cualquier subtipo) | 0 | — |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 0 | — |
| `CONVERTED_TO_GF` | 0 | — |

### 3.2 Tabla consolidada

| ID | Estado | Evidence Status | Decisión |
|----|--------|-----------------|----------|
| — | — | — | Pendiente de cierre de los Gate Exit Reviews |

### 3.3 Hallazgos identificados durante implementación

| ID | Estado | Evidence Status | Descripción | Gate/Wave/Task | Fecha |
|----|--------|-----------------|-------------|----------------|-------|
| H-5.1-1 | RESOLVED | GAP_CONFIRMED | Discrepancia 7 vs 6 identidades (HITO 5.1). La identidad faltante (pesaran1999.pdf) estaba en datasets/raw/, fuera de tests/corpus/. Encontrada e incluida como doc_07_pesaran.pdf. SHA-256: f1c80072. | Gate 1 W1.1 T1.1.1 | 2026-09-06 |
| H-5.1-2 | RESOLVED | GAP_CONFIRMED | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en tests/corpus/calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.1 | 2026-09-09 |
| H-5.1-3 | RESOLVED | GAP_CONFIRMED | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy, content en lugar de payload.content). Resuelto por re-extracción en Task 1.3.8: PDF recortado a 3 páginas, GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente). | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.8 | 2026-09-09 |
| H-5.1-4 | RESOLVED | GAP_CONFIRMED | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Inspección visual confirmó PDFs escaneados. Clasificación corregida en manifest canónico con nombres del catálogo vigente. | Gate 1 W1.1 T1.1.1 → W1.2 T1.2.1 | 2026-09-06 |
| H-5.1-5 | RESOLVED | GAP_CONFIRMED | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). Nombres inexistentes: DENSE_TYPOGRAPHY, MIXED_CONTENT. Nombres corregidos: HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise. Reclasificación completada. | Gate 1 W1.2 T1.2.1 | 2026-09-06 |
| H-5.1-6 | CLOSED (NAR) | NO_GAP | Hipótesis: contrato del manifest NO es 6 campos planos. Verificación: RawDocumentEntryDTO SÍ es 6D plano (document_id, sha256, traits, page_count, ground_truth_state, oracle_hash). El sha256 está encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en el DTO de serialización. El contrato 6D es correcto. | Gate 1 W1.2 T1.2.3 | 2026-09-06 |
| H-5.1-7 | RESOLVED | GAP_CONFIRMED | Todos los parent_node_id son None en los 5 GTs canonicalizados. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II: secuencias lineales enriquecidas con metadatos topológicos). Verificado en curaduría manual (Task 1.3.9). | Gate 1 W1.3 T1.3.4 → T1.3.9 | 2026-09-09 |
| H-5.1-8 | CLOSED (NAR) | NO_GAP | Hipótesis: ManifestFingerprintCalculator.compute_hash() no incluye page_count. Verificación en source code: el payload SÍ incluye page_count (f"{doc.page_count}:"). El hash anterior coincidió por valor por defecto de Pydantic que igualó el valor real. | Gate 1 W1.3 T1.3.1 | 2026-09-09 |
| H-5.1-9 | ACCEPTED_LIMITATION | GAP_CONFIRMED | doc_02_double: 52 nodos display_equation contienen fragmentos garbled (operadores/variables aislados: "+", "= = =", "p", "i t i i"). PyMuPDF no agrupa tokens matemáticos en layout de doble columna. El GT es fiel a la salida del extractor pero NO al contenido matemático real. Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |
| H-5.1-10 | ACCEPTED_LIMITATION | GAP_CONFIRMED | doc_05_graph: 56 labels de ejes de gráficos vectoriales extraídos como paragraph individuales (ej. "–20", "0", "15"). Estructura del gráfico no capturada. Comportamiento esperado de PyMuPDF frente a gráficos vectoriales. Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |
| H-5.1-11 | RECLASSIFIED_FUTURE_PHASE | PARTIAL_GAP | Propuesta de patrón "Detect & Placeholder": PyMuPDF degrada silenciosamente tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar la presencia y dejar placeholder para pegado manual. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4: no modificar extractores). Documentado en FASE_5_WAVE_1_3_CURATION_REPORT.md. | Gate 1 W1.3 T1.3.9 | 2026-09-09 |
| H-5.2-1 | IMPLEMENTATION_REQUIRED | GAP_CONFIRMED | doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6 (Zero Partial Sealing). El documento tiene trait scanned_noise y requiere pipeline OCR no disponible. PDF físico preservado en canonical/pdf/ como evidencia (quarantine). Manifest hash recalculado: 39cc80bd → fae41bb5. Re-incorporación planificada junto con déficit de 13 documentos. | Gate 2 W2.1 (pre-requisito biyección) | 2026-09-09 |
| H-5.2-2 | CLOSED (NAR) | NO_GAP | Hipótesis: GroundTruthLifecycleState muestra 3 estados en runtime pero tests esperan 4. Verificación: enum SÍ tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED). Tests test_four_states_with_canonical_values y test_exactly_four_states PASSED. Diseño type-state: SEALED se representa como tipo SealedOracle (no GroundTruthDraft con estado). | Gate 2 W2.1 T2.1.1 | 2026-09-09 |
| H-5.2-3 | RESOLVED | GAP_CONFIRMED | canonicalization_lineage.json estaba en ground_truth/ contaminando BaselineCompletenessVerifier como oráculo huérfano. Movido a canonical/ raíz (separación de concerns: ground_truth/ solo contiene GTs, uno por documento). | Gate 2 W2.2 T2.2.1 | 2026-09-09 |
| H-5.2-4 | RESOLVED | GAP_CONFIRMED | freeze_ground_truth.py apuntaba a tests/corpus/benchmark_v1/ en lugar de tests/corpus/canonical/. Path corregido a canonical/. Entry point funcional para sellado del corpus canónico. | Gate 2 W2.2 T2.2.1 | 2026-09-09 |
| H-5.2-5 | CLOSED (NAR) | NO_GAP | Log duplicado en freeze_ground_truth.py (línea logger.info repetida). Eliminado. No afecta funcionalidad ni integridad. | Gate 2 W2.2 T2.2.1 | 2026-09-09 |
| H-5.2-6 | ACCEPTED_LIMITATION | GAP_CONFIRMED | ASTFingerprintPolicy.semantic_fingerprint() aplica node.text_content.strip() e identity_fingerprint() aplica str(content).strip(), violando NADR-22 §5.3 R10-R12. Divergencia confinada al tooling experimental (tools/evaluation/topology/). Usada por EntityRecallMetric, SequenceAlignmentMetric y StructuralTopologyMetric (todas en tools/evaluation/topology/metrics/). La ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no usa ASTFingerprintPolicy. Dominio canónico (DefaultNodeMatchingPolicy, CriticalityAwareCostContext) no aplica .strip(). | Gate 2 W2.3 T2.3.3 | 2026-09-09 |
| DF-04 | RESOLVED | GAP_CONFIRMED | Benchmark comparativo ZhangShasha vs APTED ejecutado sobre 6 documentos del corpus canónico sellado con run_df04_benchmark.py. Divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double). Desglose: doc_01_single (12.14%), doc_02_double (22.63%), doc_03_math (0.62%), doc_04_table (13.08%), doc_05_graph (2.88%), doc_07_pesaran (0.00%). Cuatro causas raíz identificadas: (1) cost model diferente (APTED penaliza sustituciones diff-type 2× más: 2.0 vs 1.0), (2) normalización diferente (MaxBound vs del×|GT|+ins×|Cand|), (3) fingerprint diferente (H-5.2-6: APTED usa .strip()), (4) estructura de árbol diferente (APTED reconstruye jerarquía vía parent_node_id). Patrón 1: APTED consistentemente más severo en 4/6 documentos. Patrón 2: divergencia alta en docs con estructura compleja. Patrón 3: coincidencia perfecta en casos triviales (doc_07_pesaran 0.00%, score 1.0 en ambos) valida correctitud de ambos motores. Decisión: APTED queda como experimental no-normativo conforme a NADR-22 §5.1 R3. Criterio DF-04 aplicado: divergencia ≥ 1%, causa raíz investigada y documentada. Evidencia forense en reports/df04/df04_benchmark.{json,md}. | Gate 2 W2.4 T2.4.7 | 2026-09-10 |
| H-5.3-1 | ACCEPTED_LIMITATION | GAP_CONFIRMED | Calibración estadística no ejecutable con 6 documentos (N=6 < 20). NADR-23 §5.3 R12 prohíbe presumir robustez estadística con <20 identidades. No existen estándares publicados de umbrales PASS/WARNING/HARD_FAIL para regresión topológica de papers científicos (GROBID declara: "no fixed threshold, depends on document variability"). Los defaults actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) son evidence-informed por diseño, NO calibrados empíricamente. Estrategia: LOCAL_CALIBRATION_SET = ∅, SANITY_VALIDATION_SET = 6 docs (no modifica parámetros), FINAL_EVALUATION_SET reservado para Gate 5. Recalibración local requerida cuando corpus alcance ≥20 documentos diversos con metodología: curvas precision-recall + bootstrap confidence intervals + human verdicts PASS/WARNING/HARD_FAIL + learning curves (GROBID). Evidencia en FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md. | Gate 3 W3.1 T3.1.4 | 2026-09-10 |
| H-5.3-2 | ACCEPTED_LIMITATION | GAP_CONFIRMED | Divergencia masiva entre runtime de producción (build_extraction_pipeline() → PyMuPDFProvider) y GTs curados: 5/6 documentos HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536. Desglose: doc_01 (0.4286, 14 Critical FN), doc_02 (0.3643, 68 Critical FN), doc_03 (0.7350, 9 Critical FN), doc_04 (0.6355, 15 Critical FN), doc_05 (0.7582, 0 Critical FN pero 29 Warning FN), doc_07 (1.0000 PASS, tautológico ver H-5.3-3). Consistente con limitaciones de PyMuPDFProvider documentadas en H-5.1-9 (fragmentación de ecuaciones) y H-5.1-10 (labels de gráficos como paragraphs). Confirma que la divergencia es estructural (limitación del extractor), no paramétrica. Refuerza decisión de Wave 3.1 de no calibrar con N=6. Evidencia en reports/sanity_validation/regression_report.{json,md}. | Gate 3 W3.2 T3.2.2 | 2026-09-10 |
| H-5.3-3 | ACCEPTED_LIMITATION | GAP_CONFIRMED | GT de doc_07_pesaran no editado en curaduría: es salida cruda de build_extraction_pipeline() (GenerateGoldenDraftUseCase). NSS=1.0000 con global_ted=0.0 es tautología (extractor comparado contra sí mismo), no validación positiva. El documento contiene tablas (Table 1, Table 2 con estadísticas econométricas) que PyMuPDF no extrae (fuentes Type 3 sin ToUnicode, documentado en Curation Report Wave 1.3). GT correctamente curado divergiría del runtime y produciría HARD_FAIL como los demás documentos. doc_07 marcado como no-informativo para validación. Curaduría real diferida y agrupada con ampliación de corpus (H-5.2-1 + déficit de 13 docs). Re-sellar en medio de Gate 3 rompería trazabilidad del manifest_hash usado en Waves 3.1-3.2 y no cambiaría ninguna decisión de calibración. | Gate 3 W3.2 T3.2.3 | 2026-09-10 |
| H-5.4-1 | ACCEPTED_LIMITATION | GAP_CONFIRMED | Evidencia forense pre-remediación: `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]` y hash fa8b919c... Falso positivo operacional confirmado (NADR-24 R16, R18, ENGINEERING_PRINCIPLES §IV Cero Fallos Silenciosos). Motivó la remediación de Task 4.1.3 + 4.2.3. | Gate 4 W4.1 T4.1.3 | 2026-09-12 |
| H-5.4-2 | ACCEPTED_LIMITATION | GAP_CONFIRMED | Evidencia forense pre-remediación: durante el pre-check de GAP-5.0-03, el run espurio de `generate_pymupdf_candidate.py` (sin CLI, rutas hardcodeadas) mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (`doc_01_single.json`, `doc_02_double.json`, `doc_03_math.json`, `doc_05_graph.json`). Revertidos con `git checkout --`. Evidencia dura del riesgo DF-18/GAP-5.0-03 que motiva la remediación. | Gate 4 W4.1 T4.1.3 | 2026-09-12 |
| O-4.3-3 | Observación (no GF) | GAP_CONFIRMED | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority`. Análisis: es el entry point de sellado (MIG-06, Gate 2) que orquesta el ciclo de vida en memoria invocando la autoridad (audit/validate), diseño congelado en Wave 2.2; R28 prohíbe bypassear la autoridad, no invocarla. El tooling de ejecución certificante sigue teniendo prohibido importarla (verificado por `TestCertificationModulesWithoutGtWritePorts`). Resolución: extender el allowlist del test con justificación; sin refactor del código congelado de Gate 2 (YAGNI). | Gate 4 W4.3 T4.3.1 | 2026-09-13 |
| GF-02 | Governance Finding (documentado) | GOVERNANCE_CONFLICT | Crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3). NADR-23 §5.5 R18 define corpus_identity como "SHA-256 del manifest"; NADR-24 §5.7 R29 + NADR-20 exigen separar corpus identity (compuesto de contenido, SHA-256 de SHA-256 ordenados, estable entre sellados, NADR-20 §5.1-§5.5) de manifest identity (manifest_hash, cambia al sellar, NADR-20 §5.6 R24/R26). Resolución: artefactos de Wave 3.3 permanecen válidos (su valor es inequívoco); crosswalk documenta el mapeo entre diccionarios. Evidencia en `FASE_5_WAVE_4_3_EVIDENCE_RECORD.md`. | Gate 4 W4.3 T4.3.3 | 2026-09-13 |
| O-4.4-1 | Observación (no GF) | GAP_CONFIRMED | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en flujo de certificación. Verificar en Gate 5 si se propaga al reporte de certificación; si se propaga, remediar con inyección externa. | Gate 4 W4.4 T4.4.1 | 2026-09-13 |
| O-4.4-2 | Observación (no GF) | GAP_CONFIRMED | `reporter.py:71 np.random.choice` es bootstrap del StatisticalComparator (análisis estadístico post-benchmark con intervalos de confianza), no forma parte del reporte de regresión de certificación. No-determinista por diseño, confinado al análisis de significancia. | Gate 4 W4.4 T4.4.2 | 2026-09-13 |
| O-4.4-3 | Observación (gap documentado) | GAP_CONFIRMED | `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall). Si el proceso muere a mitad de escritura, el reporte puede quedar corrupto. No se migra a escritura atómica porque R34/R35 no la exigen para reportes de certificación y añadiría superficie de cambio sin beneficio normativo (YAGNI); la ventana de corrupción ante crash se cubre con POST-RUN VALIDATION (detecta incompletitud, R36-R37) más re-ejecución manual del operador. Implementar `tempfile + os.replace` no violaría R35; simplemente no es requerido en este scope. | Gate 4 W4.4 T4.4.3 | 2026-09-13 |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

Las secciones de batch se agregan dinámicamente conforme se ejecuten las remediaciones.

### 4.1 BATCH 1 — Pendiente

**Fecha de ejecución:** —
**Validación:** Pyright — errors | pytest — passed, — skipped
**Estado:** ⏳ PENDING

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| — | — | — | — | — |

#### Correcciones adicionales durante ejecución

- —

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| — | — | — | — |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| — | — | — |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|-------------------------|
| — | — | — |

#### Métricas post-batch

| Métrica | Valor |
|---------|-------|
| Archivos creados | — |
| Archivos modificados | — |
| Archivos eliminados | — |
| Archivos movidos | — |
| Imports corregidos | — |
| Tests ejecutados | — |
| Errores de tipo estático | — |

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 34 |
| Hallazgos activos de Fase 5 | 5 pre-identificados (DF-18, GAP-5.0-03, DF-19, GAP-5.2-05, DF-04 — todos resueltos) + 27 derivados = 32 activos con resolución + 2 Governance Findings |
| Hallazgos resueltos | 11 derivados (H-5.1-1, H-5.1-2, H-5.1-3, H-5.1-4, H-5.1-5, H-5.1-7, H-5.2-3, H-5.2-4, DF-04, H-5.4-1, H-5.4-2) + 4 pre-identificados (DF-19, GAP-5.2-05, DF-18, GAP-5.0-03) = 15 totales |
| Hallazgos cerrados sin acción | 4 (H-5.1-6, H-5.1-8, H-5.2-2, H-5.2-5) |
| Hallazgos reclasificados a fase futura | 1 (H-5.1-11) |
| Hallazgos aceptados como limitación | 8 (H-5.1-9, H-5.1-10, H-5.2-6, H-5.3-1, H-5.3-2, H-5.3-3, H-5.4-1, H-5.4-2) |
| Hallazgos pendientes de implementación | 1 (H-5.2-1) |
| Hallazgos pendientes de revisión | 0 |
| Observaciones registradas | 4 (O-4.3-3, O-4.4-1, O-4.4-2, O-4.4-3) |
| Governance Findings abiertos | 2 (GF-01, GF-02) |
| Batches completados | 0 |
| Archivos eliminados totales | 1 (tmptu237h6p) |
| Archivos movidos totales | 1 (canonicalization_lineage.json de ground_truth/ a canonical/) |
| Archivos creados totales | 39 (incluyendo los 3 de Wave 4.4: test_tooling_determinism.py, test_idempotency_replacement.py, test_recovery_determinability.py) |
| Tests finales | 720 passed, 5 skipped (baseline definitiva post-Wave 4.4) |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

Los hallazgos diferidos a fases futuras se registran aquí con destino explícito y justificación.

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| H-5.1-11 | Post Fase 17-BIS (requiere ADR dedicado) | ADR F17_BIS_MASTER §4: la modificación de extractores de producción está fuera del scope de Fase 17-BIS. El patrón Detect & Placeholder requiere diseño de nuevos tipos de nodo (placeholder) y modificación de PyMuPDFProvider. Se recomienda evaluar en Fase 18 (Advanced Local Runtime) o en una fase dedicada de mejora de extracción. |
| H-5.3-1 | Post Fase 17-BIS o recalibración con corpus ampliado | NADR-23 §5.3 R12: con <20 identidades no se presume robustez estadística. Recalibración requerida cuando corpus alcance ≥20 documentos diversos. Metodología: curvas precision-recall + bootstrap CI + human verdicts + learning curves. Destino: Fase 6 (Continuous Verification) o extensión de Fase 5 cuando usuario adquiera 13+ documentos. |
| H-5.3-2 | Post Fase 17-BIS o recalibración con corpus ampliado | Divergencia masiva runtime vs GTs (106 Critical FN) confirma limitación estructural de PyMuPDFProvider. No requiere acción en Gate 3 (problema del extractor, no de thresholds). Destino: mejora de extractor en fase futura (H-5.1-11) o recalibración cuando corpus ≥20. |
| H-5.3-3 | Recalibración con corpus ampliado (agrupado con H-5.2-1) | Curaduría real de doc_07 (transcribir tablas como nodos table) requerirá re-sellado con nuevo manifest_hash. Diferida hasta ampliación del corpus para evitar romper trazabilidad de Waves 3.1-3.2 sin cambiar decisiones. |
| GF-01 | Gate 5 Task 5.2.1 (runner de certificación) | Conflicto normativo NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución). Resolución por separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta CI; runner de certificación de Gate 5 implementa taxonomía NADR-24 traduciendo veredicto científico a categoría (a)/(b) y crashes a (c). `run_regression` NO se toca en Wave 4.2. |
| GF-02 | Interpretación normativa documentada (no requiere acción futura) | Crosswalk normativo de identidades NADR-20/23/24. No requiere acción adicional: los artefactos de Wave 3.3 permanecen válidos; el crosswalk está documentado en `FASE_5_WAVE_4_3_EVIDENCE_RECORD.md`. Si un Gate futuro introduce nuevos diccionarios de identidades, el crosswalk debe extenderse. |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:

1. Todos los tests pasan:
   ```text
   pytest → baseline 624 passed, 5 skipped mantenida o mejorada
   ```
2. Pyright reporta:
   ```text
   0 errors
   ```
3. No se detectan imports huérfanos.
4. Los cambios están commiteados o registrados como Implementation Evidence.
5. Ningún oráculo sellado fue mutado in-place.
6. La evidencia del batch referencia explícitamente los DF/GF cerrados.
7. Si el batch toca contratos o artefactos de baseline, se registra hash/identidad antes y después.

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:

1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado.
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión.
3. Todos los batches planificados están completados.
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito.
5. DF-04 está cerrado con resolución documentada:
   - divergencia `< 1%` TED normalizado → APTED experimental sin acción adicional
   - divergencia `≥ 1%` TED normalizado → causa raíz investigada y documentada
6. DF-18 está resuelto:
   - semántica de fallo uniforme en entry points afectados
   - cero caminos críticos con exit code de éxito indebido
7. DF-19 está resuelto:
   - manifest migrado a formato 6D
   - hash recomputable
   - formato legacy eliminado o marcado como no canónico
8. GAP-5.0-03 está remediado:
   - configuración explícita de corpus
   - sin fallback silencioso a rutas hardcoded
9. GAP-5.2-05 está remediado:
   - protección de SealedOracle
   - no mutación in-place de artefactos sellados
10. El Gate 5 Exit Review no contiene findings bloqueantes abiertos.
11. El documento pasa a estado `ARCHIVED`.

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 34 |
| Hallazgos activos de Fase 5 (pre-identificados) | 5 (todos resueltos: DF-18, GAP-5.0-03, DF-19, GAP-5.2-05, DF-04) |
| Hallazgos derivados de Waves 1.1-4.4 | 27 |
| Hallazgos resueltos | 15 (11 derivados + 4 pre-identificados: DF-19, GAP-5.2-05, DF-18, GAP-5.0-03, DF-04) |
| Hallazgos cerrados sin acción | 4 (H-5.1-6, H-5.1-8, H-5.2-2, H-5.2-5) |
| Hallazgos aceptados como limitación | 8 (H-5.1-9, H-5.1-10, H-5.2-6, H-5.3-1, H-5.3-2, H-5.3-3, H-5.4-1, H-5.4-2) |
| Hallazgos reclasificados a fase futura | 1 (H-5.1-11) |
| Hallazgos pendientes de implementación | 1 (H-5.2-1) |
| Hallazgos pendientes de revisión | 0 |
| Observaciones registradas | 4 (O-4.3-3, O-4.4-1, O-4.4-2, O-4.4-3) |
| Governance Findings abiertos | 2 (GF-01, GF-02) |
| Batches completados | 0/— |
| Estado del Exit Review | 🟡 IN PROGRESS (Gate 2 COMPLETED, Gate 3 COMPLETED, Gate 4 COMPLETED, Gate 5 PENDING) |

---

## 9. REGISTRO DE HALLAZGOS PRE-IDENTIFICADOS (REFERENCIA DE TRAZABILIDAD)

Los siguientes hallazgos fueron identificados en HITOs anteriores y/o en el
Execution Plan. Se registran aquí **únicamente como referencia de trazabilidad**.
La clasificación formal, evidencia forense y decisión arquitectónica se construirán
durante los Gate Exit Reviews correspondientes, aplicando el árbol de decisión de §1.

> **Nota:** La existencia de estos hallazgos como carry-forward o pre-identificación
> no implica que su evidencia forense esté completa. El análisis detallado (archivos
> auditados, gaps confirmados, sub-acciones, regla aplicada) se registra en §2
> cuando se ejecute el Gate Exit Review correspondiente.

### 9.1 Carry-forwards de Fase 4 — no bloquean Fase 5

| ID | Descripción | Estado preliminar | Destino | Fuente |
|----|-------------|-------------------|---------|--------|
| DF-01 | Tests tautológicos en `test_golden_parser.py` y `test_chunker_snapshot.py` | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 (Continuous Verification) | FASE_4_HANDOFF §5.2 |
| DF-02 | Verificación de `ci.yml` y `pyproject.toml` para tests de regresión | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Fase 6 (Continuous Verification) | FASE_4_HANDOFF §5.2 |
| DF-03 | Deuda técnica `LayoutBlockDraft` / mapper transicional | `RECLASSIFIED_FUTURE_PHASE` (preliminar) | Gate futuro de remediación de layout | FASE_4_HANDOFF §5.2 |

### 9.2 Hallazgos activos de Fase 5 — pendientes de análisis formal

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo ejecutado con run_df04_benchmark.py sobre 6 documentos del corpus canónico sellado. Divergencia promedio 8.56% (> umbral 1%), máxima 22.63% (doc_02_double). Cuatro causas raíz documentadas: (1) cost model diferente, (2) normalización diferente, (3) fingerprint diferente (H-5.2-6), (4) estructura de árbol diferente. APTED queda como experimental no-normativo (NADR-22 §5.1 R3). Criterio DF-04 aplicado y cerrado. | `RESOLVED` | Gate 2 W2.4 Task 2.4.7 (investigación); Gate 5 W5.3 Task 5.3.3 (cierre administrativo) | FASE_4_HANDOFF §5.2 → Resolución Wave 2.4 |
| DF-18 | Semántica de fallo heterogénea en 4 entry points (`freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`). Múltiples caminos de error pueden terminar en exit 0. **RESOLVED en Wave 4.2:** `main() -> int` + `run_entry(main)`; `core/shared/exit_codes.py` con taxonomía uniforme; códigos indexables; D1 (skips/failures), D2 (override `--allow-missing-manifest`), D3 (unificación exit codes). | `RESOLVED` | Gate 4 W4.2 Task 4.2.3 | HITO 5.2 → Resolución Wave 4.2 |
| DF-19 | Manifest en formato legacy (4 dimensiones) incompatible con formato vigente (6 dimensiones). Hash almacenado ≠ hash calculado. Tasks 1.2.3 (contrato) y 1.3.1 (ejecución de migración) completadas. Manifest sellado en formato 6D con oracle_hash y ground_truth_state. | `RESOLVED` | Gate 1 W1.2 Task 1.2.3 (contrato); Gate 1 W1.3 Task 1.3.1 (ejecución de migración) | HITO 5.1 → Resolución Wave 1.3 |
| GAP-5.0-03 | Configuración implícita del corpus. 6 de 8 entry points tienen rutas hardcoded sin argumentos CLI configurables. **RESOLVED en Wave 4.1:** 5 entry points migrados a CLI con `--corpus-dir` required; 11 entry points auditados (5 remediados + 4 ya explícitos + 1 deprecated + 1 fuera de scope). | `RESOLVED` | Gate 4 W4.1 Task 4.1.3 | HITO 5.0 → Resolución Wave 4.1 |
| GAP-5.2-05 | Certification Boundary Integrity violation. `sanitize_ground_truth_types.py` puede sobrescribir Ground Truths sellados sin verificar estado de sellado. Remediado en Task 2.1.2: protección fail-hard con SealedOracleOverwriteError. Verificación formal de boundary completada en Wave 4.3 Task 4.3.2: cadena sanitize/use cases/override D2 verificada; `GenerateGoldenDraftUseCase` verifica estado antes de escribir; `SealGroundTruthUseCase` permanece como autoridad única de sellado. | `RESOLVED` | Gate 2 W2.1 Task 2.1.2 (remediación primaria); Gate 4 W4.3 Task 4.3.2 (verificación formal completada) | HITO 5.2 → Resolución Wave 2.1 → Verificación Wave 4.3 |


### 9.2.1 Hallazgos derivados de Wave 1.1 y 1.2 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.1-1 | Discrepancia 7 vs 6 identidades (HITO 5.1). pesaran1999.pdf encontrado en datasets/raw/ e incluido como doc_07_pesaran.pdf (SHA-256: f1c80072). | `RESOLVED` | Gate 1 W1.1 T1.1.1 | Auditoría Wave 1.1 |
| H-5.1-2 | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en tests/corpus/calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | `RESOLVED` | Gate 1 W1.3 T1.3.1 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-3 | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy). Resuelto por re-extracción: PDF recortado a 3 páginas, GT regenerado con GenerateGoldenDraftUseCase (21 nodos, formato vigente). | `RESOLVED` | Gate 1 W1.3 T1.3.8 | Auditoría Wave 1.1 → Resolución Wave 1.3 |
| H-5.1-4 | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Clasificación corregida en manifest canónico con nombres del catálogo vigente. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Inspección visual Wave 1.1 → Reclasificación Wave 1.2 |
| H-5.1-5 | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). DENSE_TYPOGRAPHY y MIXED_CONTENT no existen. Reclasificación completada. | `RESOLVED` | Gate 1 W1.2 T1.2.1 | Auditoría Wave 1.2 |
| H-5.1-6 | Contrato del manifest verificado como 6D plano en RawDocumentEntryDTO. El sha256 está encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en el DTO. El contrato 6D es correcto. | `CLOSED (NAR)` | Gate 1 W1.2 T1.2.3 | Auditoría Wave 1.2 |


### 9.2.2 Hallazgos derivados de Wave 1.3 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.1-7 | Todos los parent_node_id son None en los 5 GTs canonicalizados. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II). Verificado en curaduría manual. | `RESOLVED` | Gate 1 W1.3 T1.3.4 → T1.3.9 | Auditoría Wave 1.3 |
| H-5.1-8 | ManifestFingerprintCalculator.compute_hash() incluye page_count en el payload (verificado en source code). Hash anterior coincidió por valor por defecto de Pydantic. | `CLOSED (NAR)` | Gate 1 W1.3 T1.3.1 | Auditoría Wave 1.3 |
| H-5.1-9 | doc_02_double: 52 nodos display_equation con fragmentos garbled. PyMuPDF no agrupa ecuaciones en doble columna. GT fiel al extractor, no al documento fuente. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos como paragraphs. Estructura de gráficos no capturada por PyMuPDF. | `ACCEPTED_LIMITATION` | Gate 1 W1.3 T1.3.9 | Curaduría Wave 1.3 |
| H-5.1-11 | Propuesta de patrón "Detect & Placeholder" para extracción de tablas/figuras/ecuaciones. Fuera del scope de Fase 17-BIS (ADR F17_BIS_MASTER §4). | `RECLASSIFIED_FUTURE_PHASE` | Post Fase 17-BIS | Curaduría Wave 1.3 |


### 9.2.3 Hallazgos derivados de Wave 2.1 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.2-1 | doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6 (Zero Partial Sealing). Requiere re-incorporación con pipeline OCR. Manifest hash recalculado: 39cc80bd → fae41bb5. PDF físico preservado como evidencia. | `IMPLEMENTATION_REQUIRED` | Gate 2 W2.1 (pre-requisito biyección) | Auditoría Wave 2.1 |
| H-5.2-2 | GroundTruthLifecycleState muestra 3 estados en inspección runtime pero tests esperan 4. Verificación: enum SÍ tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED). Diseño type-state: SEALED se representa como tipo SealedOracle. | `CLOSED (NAR)` | Gate 2 W2.1 T2.1.1 | Auditoría Wave 2.1 |

### 9.2.4 Hallazgos derivados de Wave 2.2 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.2-3 | canonicalization_lineage.json estaba en ground_truth/ contaminando BaselineCompletenessVerifier como oráculo huérfano. Movido a canonical/ raíz (separación de concerns). | `RESOLVED` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |
| H-5.2-4 | freeze_ground_truth.py apuntaba a tests/corpus/benchmark_v1/ en lugar de tests/corpus/canonical/. Path corregido. | `RESOLVED` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |
| H-5.2-5 | Log duplicado en freeze_ground_truth.py (línea logger.info repetida). Eliminado. No afecta funcionalidad. | `CLOSED (NAR)` | Gate 2 W2.2 T2.2.1 | Ejecución Wave 2.2 |

> **Nota:** H-5.2-3 y H-5.2-4 se marcan como `RESOLVED` porque fueron remediados
> durante la ejecución del sellado en Task 2.2.1. H-5.2-5 se marca como `CLOSED (NAR)`
> porque el log duplicado no afectaba la funcionalidad ni la integridad del sellado.
> La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.


### 9.2.5 Hallazgos derivados de Wave 2.3 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.2-6 | ASTFingerprintPolicy.semantic_fingerprint() e identity_fingerprint() aplican .strip() en el contenido, violando NADR-22 §5.3 R10-R12 (normalización de texto: sin .strip(), sin fingerprint). Divergencia confinada al tooling experimental (tools/evaluation/topology/). La ruta canónica de regresión no usa ASTFingerprintPolicy. Dominio canónico no aplica .strip(). | `ACCEPTED_LIMITATION` | Gate 2 W2.3 T2.3.3 | AUDIT Wave 2.3 |

> **Nota:** H-5.2-6 se marca como `ACCEPTED_LIMITATION` porque:
> (1) ASTFingerprintPolicy está en tools/evaluation/topology/fingerprint.py (tooling experimental, no dominio);
> (2) los únicos usuarios son EntityRecallMetric, SequenceAlignmentMetric y StructuralTopologyMetric, todos en tools/evaluation/topology/metrics/;
> (3) la ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no importa ni usa ASTFingerprintPolicy;
> (4) el dominio canónico (DefaultNodeMatchingPolicy.match(), CriticalityAwareCostContext.substitution_cost()) usa comparación exacta de text_content sin normalización destructiva;
> (5) modificar ASTFingerprintPolicy podría romper tests del tooling experimental sin beneficio para la certificación.
> Se documenta como deuda técnica para Fase 6 (mejora del tooling de evaluación).
> La evidencia forense formal se registrará en §2 durante el Gate 2 Exit Review.

### 9.2.6 Hallazgos derivados de Wave 3.1 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.3-1 | Calibración estadística no ejecutable con 6 documentos. NADR-23 R12 prohíbe presumir robustez estadística con <20 identidades. No existen estándares publicados de umbrales PASS/WARNING/HARD_FAIL para regresión topológica de papers científicos (GROBID declara explícitamente: "no fixed threshold, depends on document variability, use learning curves"). Los defaults actuales son evidence-informed por diseño, NO calibrados empíricamente. Estrategia: LOCAL_CALIBRATION_SET = ∅, SANITY_VALIDATION_SET = 6 docs (no modifica parámetros), FINAL_EVALUATION_SET reservado para Gate 5. Recalibración pendiente para corpus ≥20. | `ACCEPTED_LIMITATION` | Gate 3 W3.1 T3.1.4 | AUDIT Wave 3.1 |

> **Nota:** H-5.3-1 se marca como `ACCEPTED_LIMITATION` porque:
> (1) NADR-23 §5.3 R12 explícitamente prohíbe presumir robustez estadística con <20 identidades;
> (2) La industria (GROBID, DocLayNet, Nougat) no publica umbrales transferibles de regresión topológica;
> (3) Los defaults actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0) son de diseño, no calibrados;
> (4) La estrategia LOCAL_CALIBRATION_SET = ∅ evita overfitting a 6 documentos;
> (5) La regla anti-leakage (NADR-23 R2) garantiza que SANITY_VALIDATION no contamina parámetros;
> (6) El protocolo de recalibración (curvas PR + bootstrap + human verdicts + learning curves) queda documentado para cuando el corpus alcance ≥20 documentos.
> Se documenta como deuda técnica para recalibración en Fase 6 o cuando el usuario adquiera 13+ documentos adicionales.
> La evidencia forense formal se registrará en §2 durante el Gate 3 Exit Review.

### 9.2.7 Hallazgos derivados de Wave 3.2 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.3-2 | Divergencia masiva entre runtime de producción y GTs curados: 5/6 documentos HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536. Consistente con limitaciones estructurales de PyMuPDFProvider (H-5.1-9, H-5.1-10). Confirma que la divergencia es estructural, no paramétrica. Refuerza decisión de Wave 3.1 de no calibrar con N=6. | `ACCEPTED_LIMITATION` | Gate 3 W3.2 T3.2.2 | Sanity Validation Wave 3.2 |
| H-5.3-3 | GT de doc_07_pesaran no editado en curaduría: es salida cruda de build_extraction_pipeline(). NSS=1.0000 es tautología (extractor contra sí mismo), no validación positiva. Documento contiene tablas (Table 1, Table 2) que PyMuPDF no extrae (fuentes Type 3). Curaduría real diferida con ampliación de corpus (H-5.2-1). | `ACCEPTED_LIMITATION` | Gate 3 W3.2 T3.2.3 | Sanity Validation Wave 3.2 |

> **Nota:** H-5.3-2 se marca como `ACCEPTED_LIMITATION` porque:
> (1) La divergencia masiva (106 Critical FN) es consistente con limitaciones ya documentadas de PyMuPDFProvider (H-5.1-9, H-5.1-10);
> (2) El problema es estructural (extractor), no paramétrico — los thresholds actuales detectan correctamente la divergencia;
> (3) Cualquier "calibración" sobre estos datos sería calibrar para aceptar mediocridad del extractor;
> (4) No requiere acción en Gate 3 — la recalibración es innecesaria hasta que el extractor mejore o el corpus se amplíe.
> Se documenta como evidencia de que los defaults normativos funcionan correctamente.
>
> H-5.3-3 se marca como `ACCEPTED_LIMITATION` porque:
> (1) El Curation Report de Wave 1.3 documenta que doc_07 fue revisado pero NO editado (observación: "fuentes Type 3");
> (2) El NSS=1.0000 con global_ted=0.0 confirma que GT y runtime son idénticos por construcción;
> (3) El documento contiene tablas visibles (Table 1, Table 2) que PyMuPDF no extrae;
> (4) Re-sellar doc_07 en medio de Gate 3 rompería la trazabilidad del manifest_hash usado en Waves 3.1-3.2;
> (5) No cambia ninguna decisión de calibración (ya decidimos no calibrar con N=6).
> Curaduría real diferida y agrupada con ampliación de corpus (H-5.2-1 + déficit de 13 docs).
> La evidencia forense formal se registrará en §2 durante el Gate 3 Exit Review.

### 9.2.8 Hallazgos derivados de Wave 4.1 y 4.2 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| H-5.4-1 | Evidencia forense pre-remediación: `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]` y hash fa8b919c... Falso positivo operacional confirmado (NADR-24 R16, R18, ENGINEERING_PRINCIPLES §IV Cero Fallos Silenciosos). Motivó la remediación de Task 4.1.3 + 4.2.3. | `ACCEPTED_LIMITATION` | Gate 4 W4.1 T4.1.3 | Pre-check GAP-5.0-03 |
| H-5.4-2 | Evidencia forense pre-remediación: durante el pre-check de GAP-5.0-03, el run espurio de `generate_pymupdf_candidate.py` (sin CLI, rutas hardcodeadas) mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (`doc_01_single.json`, `doc_02_double.json`, `doc_03_math.json`, `doc_05_graph.json`). Revertidos con `git checkout --`. Evidencia dura del riesgo DF-18/GAP-5.0-03 que motiva la remediación. | `ACCEPTED_LIMITATION` | Gate 4 W4.1 T4.1.3 | Pre-check GAP-5.0-03 |
| GF-01 | Conflicto normativo NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución, rechazo científico es categoría b). Resolución por separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta CI; runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24 traduciendo veredicto científico a categoría (a)/(b) y crashes a (c). `run_regression` NO se toca en Wave 4.2. | Governance Finding (documentado) | Gate 4 W4.2 T4.2.3 | Auditoría DF-18 |

> **Nota:** H-5.4-1 y H-5.4-2 se marcan como `ACCEPTED_LIMITATION` (evidencia forense) porque:
> (1) Son evidencia pre-remediación que motivó la implementación de GAP-5.0-03 y DF-18;
> (2) Documentan el riesgo real de configuración implícita + semántica de fallo heterogénea;
> (3) No requieren acción adicional (la remediación ya está implementada);
> (4) Sirven como evidencia forense para auditorías futuras de por qué se implementaron los cambios.
>
> GF-01 se marca como Governance Finding porque:
> (1) Evidencia un conflicto real entre dos NADRs congelados (NADR-19 y NADR-24);
> (2) La resolución es por separación de scope, no por modificación de ninguno de los dos;
> (3) `run_regression` conserva su taxonomía NADR-19 (correcta para su propósito de compuerta CI);
> (4) El runner de certificación de Gate 5 (Task 5.2.1) implementará la taxonomía NADR-24 traduciendo veredictos;
> (5) No se toca `run_regression` en Wave 4.2 para evitar violar NADR-19 §5.5 R22.

### 9.2.9 Hallazgos derivados de Wave 4.3 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| O-4.3-3 | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority` (entry point de sellado MIG-06, Gate 2). R28 prohíbe bypassear la autoridad, no invocarla; el entry point orquesta el ciclo de vida en memoria invocando la autoridad (audit/validate), diseño congelado en Wave 2.2. Allowlist extendido con justificación; sin refactor de código congelado de Gate 2 (YAGNI). | Observación (no Governance Finding) | Gate 4 W4.3 T4.3.1 | AUDIT Wave 4.3 Fase A |
| GF-02 | Crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3). NADR-23 §5.5 R18 define corpus_identity como "SHA-256 del manifest"; NADR-24 §5.7 R29 + NADR-20 exigen separar corpus identity (compuesto de contenido, estable entre sellados) de manifest identity (manifest_hash, cambia al sellar). Resolución: artefactos de Wave 3.3 permanecen válidos (su valor es inequívoco); crosswalk documenta el mapeo entre diccionarios. | Governance Finding (interpretación normativa) | Gate 4 W4.3 T4.3.3 | Diseño Wave 4.3 Fase B |

> **Nota:** O-4.3-3 se marca como Observación (no Governance Finding) porque:
> (1) R28 prohíbe bypassear la autoridad, no invocarla;
> (2) `freeze_ground_truth.py` es el entry point de sellado (MIG-06, Gate 2) que orquesta el ciclo de vida en memoria invocando la autoridad;
> (3) El tooling de ejecución certificante (preflight, freeze_parameters, futuro runner de Gate 5) sigue teniendo prohibido importarla (verificado por `TestCertificationModulesWithoutGtWritePorts`);
> (4) No hay conflicto normativo, solo una excepción justificada al allowlist del test de contrato.
> Se documenta como observación para trazabilidad futura.
>
> GF-02 se marca como Governance Finding (interpretación normativa) porque:
> (1) Evidencia una tensión entre dos NADRs congelados (NADR-23 R18 vs NADR-24 R29 + NADR-20);
> (2) La resolución es por interpretación normativa + crosswalk, no por modificación de artefactos;
> (3) Los artefactos de Wave 3.3 permanecen válidos (su corpus_identity per R18 = manifest_identity en NADR-24);
> (4) El crosswalk documenta el mapeo entre diccionarios para auditorías futuras.
> La evidencia forense formal se registrará en §2 durante el Gate 4 Exit Review.

### 9.2.10 Hallazgos derivados de Wave 3.3 — registrados durante implementación

Wave 3.3 (Provenance & Parameter Freeze) no generó nuevos hallazgos derivados. Las Tasks 3.3.1-3.3.3 se ejecutaron conforme a protocolo sin desviaciones. Los hallazgos referenciados en el campo `limitations` del Evaluation Provenance Record (H-5.3-1, H-5.3-2, H-5.3-3) son de Waves 3.1 y 3.2.

> **Nota:** Esta ausencia de hallazgos es consistente con el diseño de Wave 3.3: la materialización de provenance es una operación de registro y verificación, no de descubrimiento. Las limitaciones conocidas del corpus y del extractor ya están documentadas en Waves anteriores. La evidencia forense completa de Wave 3.3 reside en:
> - `reports/calibration/parameter_freeze.json`
> - `reports/calibration/calibration_provenance_record.json`
> - `reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json`
> - `tests/unit/test_provenance_identities.py` (18 tests)
> - `tests/integration/test_parameter_freeze.py` (7 tests)
> - `reviews/FASE_5_WAVE_3_3_PROVENANCE_RECORD.md` v1.0.0

### 9.2.11 Hallazgos derivados de Wave 4.4 — registrados durante implementación

| ID | Descripción | Estado preliminar | Gate destino primario | Fuente |
|----|-------------|-------------------|----------------------|--------|
| O-4.4-1 | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en flujo de certificación. Verificar en Gate 5 si se propaga al reporte de certificación; si se propaga, remediar con inyección externa. | Observación (sin impacto para Gate 4) | Gate 4 W4.4 T4.4.1 | AUDIT Wave 4.4 |
| O-4.4-2 | `reporter.py:71 np.random.choice` es bootstrap del StatisticalComparator (análisis estadístico post-benchmark con intervalos de confianza), no forma parte del reporte de regresión de certificación. No-determinista por diseño, confinado al análisis de significancia. | Observación (sin impacto para Gate 4) | Gate 4 W4.4 T4.4.2 | AUDIT Wave 4.4 |
| O-4.4-3 | `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall). Si el proceso muere a mitad de escritura, el reporte puede quedar corrupto. No se migra a escritura atómica porque R34/R35 no la exigen para reportes de certificación y añadiría superficie de cambio sin beneficio normativo (YAGNI); la ventana de corrupción ante crash se cubre con POST-RUN VALIDATION (detecta incompletitud, R36-R37) más re-ejecución manual del operador. Implementar `tempfile + os.replace` no violaría R35; simplemente no es requerido en este scope. | Observación (gap documentado sin acción) | Gate 4 W4.4 T4.4.3 | AUDIT Wave 4.4 |

> **Nota:** Los tres hallazgos de Wave 4.4 (O-4.4-1, O-4.4-2, O-4.4-3) se marcan como Observaciones (no Governance Findings) porque:
> (1) No evidencian conflictos normativos entre niveles de gobernanza;
> (2) Documentan gaps forenses o limitaciones conocidas que no requieren acción inmediata;
> (3) La serie GF-* está reservada a conflictos/interpretaciones normativas; la serie O-* cubre observaciones sin conflicto normativo (ver FASE_5_WAVE_4_3_EVIDENCE_RECORD.md §1).
>
> O-4.4-1 y O-4.4-2 son observaciones sin impacto para Gate 4: los timestamps y bootstrap estadístico están en componentes de benchmark/análisis, no en el flujo de certificación.
>
> O-4.4-3 documenta un gap forense real (write_text no es atómico a nivel de syscall) pero la resolución es no actuar (YAGNI): R34/R35 no exigen atomicidad física para reportes, y la ventana de corrupción se cubre con POST-RUN VALIDATION + re-ejecución manual.

### 9.3 Mapeo Finding → Task (referencia cruzada con Execution Plan)

| Finding | Task primaria | Tipo de relación | Nota |
|---------|---------------|------------------|------|
| DF-19 | 1.2.3 | Contrato | Define contrato de manifest canónico 6D (DONE) |
| DF-19 | 1.3.1 | Implementación / migración | Ejecuta migración del artefacto legacy (TODO) |
| H-5.1-1 | 1.1.1 | Resolución | pesaran1999.pdf incluido como doc_07 (RESOLVED) |
| H-5.1-2 | 1.3.1 | Limpieza | Archivo temporal huérfano eliminado (RESOLVED) |
| H-5.1-3 | 1.3.8 | Re-extracción | AST legacy reemplazado por re-extracción post-recorte (RESOLVED) |
| H-5.1-4 | 1.2.1 | Documentación | doc_03/doc_06 son scanned_noise, documentado en manifest (RESOLVED) |
| H-5.1-5 | 1.2.1 | Reclasificación | Nombres de traits corregidos contra catálogo vigente (RESOLVED) |
| H-5.1-6 | 1.2.3 | Verificación | Contrato 6D verificado como correcto (CLOSED NAR) |
| H-5.1-7 | 1.3.9 | Verificación | parent_node_id=None consistente con Flat Design (RESOLVED) |
| H-5.1-8 | 1.3.1 | Verificación | page_count incluido en hash (CLOSED NAR) |
| H-5.1-9 | 1.3.9 | Documentación | Limitación de PyMuPDF con ecuaciones en doble columna (ACCEPTED_LIMITATION) |
| H-5.1-10 | 1.3.9 | Documentación | Limitación de PyMuPDF con gráficos vectoriales (ACCEPTED_LIMITATION) |
| H-5.1-11 | 1.3.9 | Propuesta | Patrón Detect & Placeholder diferido a fase futura (RECLASSIFIED_FUTURE_PHASE) |
| H-5.2-1 | (pre-requisito biyección) | Exclusión temporal | doc_06_johnstone excluido del manifest, requiere re-incorporación con OCR (IMPLEMENTATION_REQUIRED) |
| H-5.2-2 | 2.1.1 | Verificación | GroundTruthLifecycleState tiene 4 estados, diseño type-state confirmado (CLOSED NAR) |
| GAP-5.2-05 | 2.1.2 | Remediación primaria | Protección de SealedOracle en tooling de GT |
| DF-04 | 2.4.7 | Investigación empírica | Benchmark ejecutado, causa raíz documentada, APTED experimental no-normativo (RESOLVED) |
| GAP-5.0-03 | 4.1.3 | Remediación primaria | Configuración explícita de corpus |
| DF-18 | 4.2.3 | Remediación primaria | Semántica de fallo uniforme |
| GAP-5.2-05 | 4.3.2 | Verificación de boundary | Validación de frontera de certificación |
| DF-04 | 5.3.3 | Cierre administrativo | Documentación final del finding (pendiente Gate 5) |
| DF-19 | 1.2.3, 1.3.1 | Resolución | Manifest migrado a 6D y sellado (RESOLVED) |
| H-5.2-3 | 2.2.1 | Limpieza | canonicalization_lineage.json movido fuera de ground_truth/ (RESOLVED) |
| H-5.2-4 | 2.2.1 | Corrección | Path de freeze_ground_truth.py corregido (RESOLVED) |
| H-5.2-5 | 2.2.1 | Limpieza | Log duplicado eliminado (CLOSED NAR) |
| H-5.2-6 | 2.3.3 | Documentación | ASTFingerprintPolicy .strip() confinado a tooling experimental, deuda técnica registrada (ACCEPTED_LIMITATION) |
| H-5.3-1 | 3.1.4 | Documentación | Estrategia de independencia estadística con N=6: LOCAL_CALIBRATION=∅, SANITY=6 docs (no modifica parámetros), FINAL reservado para Gate 5. Recalibración pendiente para corpus ≥20 (ACCEPTED_LIMITATION) |
| H-5.3-2 | 3.2.2 | Evidencia empírica | Divergencia masiva runtime vs GTs: 5/6 HARD_FAIL, 106 Critical FN, confirma problema estructural del extractor (ACCEPTED_LIMITATION) |
| H-5.3-3 | 3.2.3 | Documentación | GT de doc_07 no editado, NSS=1.0 tautológico; curaduría diferida con ampliación de corpus (ACCEPTED_LIMITATION) |
| H-5.3-1 | 3.3.3 | Referenciado en limitations | Limitación de calibración estadística con N=6; referenciado en Evaluation Provenance Record de Wave 3.3 (ACCEPTED_LIMITATION) |
| H-5.3-2 | 3.3.3 | Referenciado en limitations | Divergencia masiva runtime vs GTs; referenciado en Evaluation Provenance Record de Wave 3.3 (ACCEPTED_LIMITATION) |
| H-5.3-3 | 3.3.3 | Referenciado en limitations | Tautología de doc_07; referenciado en Evaluation Provenance Record de Wave 3.3 (ACCEPTED_LIMITATION) |
| H-5.4-1 | 4.1.3 | Evidencia forense | Falso positivo operacional pre-remediación (ACCEPTED_LIMITATION) |
| H-5.4-2 | 4.1.3 | Evidencia forense | Mutación accidental de artefactos trackeados pre-remediación (ACCEPTED_LIMITATION) |
| GF-01 | 4.2.3 | Conflicto normativo | NADR-19 vs NADR-24 en taxonomía de exit codes; resuelto por separación de scope |
| O-4.3-3 | 4.3.1 | Observación | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority` (sellado MIG-06); allowlist extendido |
| GF-02 | 4.3.3 | Conflicto normativo | NADR-23 R18 vs NADR-24 R29 + NADR-20 en identidades; resuelto por crosswalk normativo |
| GAP-5.2-05 | 4.3.2 | Verificación formal | Verificación de boundary completada; estado actualizado a RESOLVED |
| O-4.4-1 | 4.4.1 | Observación | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17; verificar en Gate 5 si se propaga |
| O-4.4-2 | 4.4.2 | Observación | `reporter.py:71 np.random.choice` en bootstrap estadístico; no forma parte del reporte de certificación |
| O-4.4-3 | 4.4.3 | Observación | `write_text` directo en entry points de certificación; no atómico a nivel de syscall; YAGNI + POST-RUN VALIDATION |

---

## 10. RELACIÓN CON EL EXECUTION PLAN

| Gate | Waves | Tasks | Hallazgos pre-asignados |
|------|-------|-------|-------------------------|
| Gate 1 — Canonical Corpus & GT Qualification | W1.1, W1.2, W1.3 | 18 | DF-19 |
| Gate 2 — GT Sealing & Canonical Evaluation Configuration | W2.1, W2.2, W2.3, W2.4 | 17 | GAP-5.2-05, DF-04 |
| Gate 3 — Scientific Calibration & Experimental Provenance | W3.1, W3.2, W3.3 | 10 | H-5.3-1, H-5.3-2, H-5.3-3 (derivados en Waves 3.1 y 3.2) |
| Gate 4 — Certification Tooling & Execution Safety | W4.1, W4.2, W4.3, W4.4 | 13 | GAP-5.0-03, DF-18, GAP-5.2-05 |
| Gate 5 — End-to-End Certification & Baseline Freeze | W5.1, W5.2, W5.3 | 10 | DF-04 (cierre administrativo) |

---

## 11. REGISTRO DE GOVERNANCE FINDINGS

Los Governance Findings se registran únicamente cuando un hallazgo evidencia una
contradicción entre niveles de gobernanza. Se agregan dinámicamente durante los
Gate Exit Reviews.

| GF | DF origen | Estado | Conflicto normativo | Decisión |
|----|-----------|--------|---------------------|----------|
| GF-01 | DF-18 | Documentado (no resuelto por diseño) | NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución, rechazo científico es categoría b) | Separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta CI; runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24 traduciendo veredicto científico a categoría (a)/(b) y crashes a (c). `run_regression` NO se toca en Wave 4.2. |
| GF-02 | (diseño Wave 4.3) | Documentado (interpretación normativa) | NADR-23 §5.5 R18 (corpus_identity = SHA-256 del manifest) vs NADR-24 §5.7 R29 (corpus identity y manifest identity como entidades distintas conforme a NADR-20) | Crosswalk normativo: `corpus_identity` = compuesto de contenido (SHA-256 de SHA-256 ordenados, estable entre sellados, NADR-20 §5.1-§5.5); `manifest_identity` = `manifest_hash` (cambia al sellar, NADR-20 §5.6 R24/R26). Artefactos de Wave 3.3 permanecen válidos; crosswalk documenta el mapeo entre diccionarios. Evidencia en `FASE_5_WAVE_4_3_EVIDENCE_RECORD.md`. |

---

## 12. APÉNDICE — PLANTILLAS PARA NUEVOS HALLAZGOS

Cuando se identifique un hallazgo durante la implementación o un Gate Exit Review,
se agrega una entrada en §2 y/o §3.3 con la siguiente estructura mínima:

### 12.1 Plantilla para entrada en tabla de Gate Exit Review

| Campo | Valor |
|-------|-------|
| DF/GF | {ID} |
| ¿Válido? | {✅ Sí / ❌ No / ⚠️ Parcial} |
| Evidencia | {Breve descripción de la evidencia o "pendiente"} |
| ¿Resoluble en Gate? | {✅ Sí / ❌ No} |
| ¿Técnico? | {✅ Sí / ❌ No} |
| Decisión | {Estado final de clasificación} |
| Motivo | {Justificación breve con referencia normativa} |

### 12.2 Plantilla para hallazgo nuevo en §3.3

| Campo | Valor |
|-------|-------|
| ID | {DF/GF/H-5.N-X} |
| Estado | {Estado de clasificación} |
| Evidence Status | {GAP_CONFIRMED / HYPOTHESIS_PENDING / NO_GAP / PARTIAL_GAP / GOVERNANCE_CONFLICT} |
| Descripción | {Descripción breve} |
| Gate/Wave/Task | {Ubicación donde se identificó} |
| Fecha | {YYYY-MM-DD} |

### 12.3 Plantilla para entrada en batch (§4)

| Campo | Valor |
|-------|-------|
| DF ID | {ID} |
| Estado Final | {RESOLVED — acción / CLOSED (NAR) / etc.} |
| Acción Ejecutada | {Descripción de la acción} |
| Archivos Afectados | {Lista de archivos} |
| Validación | {✅ Evidencia de validación} |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → evidencia. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución. Los hallazgos que comprometan la
inmutabilidad de un oráculo sellado, la biyección PDF↔oráculo, el determinismo
de la evaluación, la independencia entre calibración y evaluación final, o la
semántica de fallo uniforme son bloqueantes hasta que se resuelvan o se
reclasifiquen formalmente con evidencia durante los Gate Exit Reviews.