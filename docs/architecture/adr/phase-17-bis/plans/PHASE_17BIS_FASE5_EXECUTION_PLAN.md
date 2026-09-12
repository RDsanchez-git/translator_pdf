# PHASE 17BIS_FASE5 EXECUTION PLAN v1.3.3
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 1.3.5
**Status:** FROZEN
**Date:** 2026-09-13
**Supersedes:** v1.2.1-DRAFT (2026-09-05)
**Derived From:** 5 NADRs FROZEN (NADR-F17BIS-20 a NADR-F17BIS-24, 168 reglas) + ADR_F17_BIS_MASTER (FROZEN) + ADR_F17_BIS_05 (FROZEN) + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento de la Fase 5 (Baseline Certification). Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 5 Gates, 17 Waves, 68 Tasks. Basado en 5 NADRs FROZEN (168 reglas). |
| 1.1.0 | 2026-09-05 | Incorporación de 5 aspectos de la propuesta alternativa: (1) Criterios específicos de selección de documentos; (2) Curaduría manual explícita; (3) Criterio de decisión DF-04 explícito; (4) Runbook ampliado; (5) Formato de notas de implementación más explícito. |
| 1.2.0 | 2026-09-05 | FROZEN. Correcciones de conteo: Changelog corregido, Gate Completion Log reconciliado, Gate 2 tasks corregido. |
| 1.2.1 | 2026-09-05 | DRAFT — Hardening documental: (1) Gate 5: 8→10 Tasks en §3; (2) Rollback Plan Gate 2: eliminado rollback mutativo de SealedOracle; (3) Tasks 1.2.3/1.3.1 desambiguadas (contrato vs ejecución de migración); (4) Separación CERTIFIED/REJECTED/EXECUTION_FAILURE de Gate/Phase outcome; (5) Task 3.1.4 reformulada (estrategia aprobada, no opciones abiertas); (6) Task 3.2.2 reformulada (CAL→VAL→FREEZE, FINAL en Gate 5); (7) Task 2.2.1: "lógicamente atómico"; (8) Task 2.2.5: fault injection explícito; (9) Tasks 1.3.6/2.2.3 diferenciadas (candidato vs Oracle sellado); (10) Tasks 2.4.7/5.3.3 diferenciadas (implementación vs cierre administrativo); (11) §4 Runbook: aclarado como Deployment, Migration & Certification Operations; (12) §7 Appendix: nota normativa de granularidad. |
| 1.2.2 | 2026-09-05 | **FROZEN.** Corrección aritmética: (1) Nota normativa en §3 y §6 aclarando que las reglas de verificación no se contabilizan en el Gate que las verifica, solo en el Gate de implementación primaria; (2) Suma de reglas Gates 1-4 verificada: 57 + 43 + 31 + 37 = 168 (las 7 reglas de NADR-21 §5.6/§5.7 verificadas en Gate 2 se contabilizan en Gate 1). |
| 1.2.3 | 2026-09-06 | **Progreso Wave 1.1:** (1) Gate 1 Status → IN_PROGRESS; (2) Wave 1.1 completada (5 Tasks DONE); (3) Wave 1.2 iniciada (Task 1.2.1 IN_PROGRESS); (4) MIG-01 y MIG-03 ejecutados; (5) 4 hallazgos derivados al Findings Register (H-5.1-1 a H-5.1-4); (6) Corpus canónico materializado con 7 identidades (déficit de 13 documentado). |
| 1.2.4 | 2026-09-06 | **Wave 1.2 completada:** (1) Task 1.2.1 DONE — traits reclasificados contra catálogo vigente (H-5.1-5 RESOLVED); (2) Task 1.2.2 DONE — cualificación formal registrada en FASE_5_WAVE_1_2_QUALIFICATION_RECORD.md; (3) Task 1.2.3 DONE — seed manifest 6D generado y verificado con BootstrapCorpusManifestUseCase (hash 62f0df16); (4) Task 1.2.4 DONE — provenance registrado en FASE_5_WAVE_1_2_PROVENANCE.md; (5) Corrección aritmética: Gate Completion Log y Status Dashboard reconciliados (Task 1.1.5 IN_PROGRESS, no DONE); (6) Wave 1.3 iniciada. |
| 1.2.5 | 2026-09-09 | **Wave 1.3 completada (9 Tasks DONE):** (1) Task 1.3.1 DONE — DF-19 verificado: manifest canónico 6D completo, H-5.1-8 CLOSED (NAR); (2) Task 1.3.2 DONE — 401/401 node_ids canonicalizados con lineage (H-5.1-2 RESOLVED: archivo temporal eliminado); (3) Tasks 1.3.3-1.3.5 DONE — hidratación, validez estructural y elegibilidad verificadas para 5 GTs; (4) Tasks 1.3.6-1.3.7 DONE — identidad semántica (5 únicas, sin colisiones) y hash de baseline verificados (62f0df16); (5) Task 1.3.8 DONE — doc_07_pesaran recortado a 3 páginas, GT re-extraído (21 nodos), manifest actualizado (hash 39cc80bd, H-5.1-3 RESOLVED); (6) Task 1.3.9 DONE — curaduría manual completada, Curation Report generado (H-5.1-9, H-5.1-10 ACCEPTED_LIMITATION; H-5.1-11 RECLASSIFIED_FUTURE_PHASE); (7) doc_06_johnstone sin GT (scanned_noise, requiere OCR); (8) MIG-04 y MIG-05 ejecutados. |
| 1.2.6 | 2026-09-09 | **Wave 2.1 completada (2 Tasks DONE):** (1) Task 2.1.1 DONE — ciclo de vida Draft→Audited→Validated→Sealed verificado por construcción (19 tests lifecycle + 23 tests modelos, todos PASSED); (2) Task 2.1.2 DONE — GAP-5.2-05 remediado: sanitize_ground_truth_types.py ahora lanza SealedOracleOverwriteError (fail-hard) ante oráculos sellados (3 tests nuevos); (3) H-5.2-1 registrado: doc_06_johnstone excluido del manifest para restaurar biyección N_PDF=N_GT=6 (IMPLEMENTATION_REQUIRED); (4) H-5.2-2 registrado y CLOSED (NAR): GroundTruthLifecycleState tiene 4 estados; (5) Manifest hash recalculado: 39cc80bd → fae41bb5 (post exclusión doc_06); (6) Gate 2 Status → IN PROGRESS; (7) Baseline tests: 627 passed, 5 skipped (3 nuevos de GAP-5.2-05). |
| 1.2.7 | 2026-09-09 | **Wave 2.2 completada (5 Tasks DONE):** (1) Task 2.2.1 DONE — sellado ejecutado con freeze_ground_truth.py: 6/6 documentos sellados, manifest_hash 0fda7690, MIG-02 y MIG-06 ejecutados; (2) Task 2.2.2 DONE — biyección verificada N_PDF=N_GT=6; (3) Task 2.2.3 DONE — identidad semántica post-sealing: 6/6 oracle_hash coinciden con valores almacenados; (4) Task 2.2.4 DONE — hash encadenado verificado: 0fda7690 recalculado correctamente; (5) Task 2.2.5 DONE — atomicidad verificada (7/7 tests test_ground_truth_sealing_atomicity PASSED); (6) H-5.2-3 registrado y RESOLVED: canonicalization_lineage.json movido fuera de ground_truth/; (7) H-5.2-4 registrado y RESOLVED: path de freeze_ground_truth.py corregido (benchmark_v1 → canonical); (8) H-5.2-5 registrado y CLOSED (NAR): log duplicado eliminado de freeze_ground_truth.py. |
| 1.2.8 | 2026-09-09 | **Wave 2.3 completada (3 Tasks DONE):** (1) Task 2.3.1 DONE — ZhangShashaEngine verificado como motor canónico en create_topology_evaluator(); APTED aislado en tools/evaluation/topology/metrics/structural.py como experimental; (2) Task 2.3.2 DONE — CriticalityAwareCostContext verificado: DEFAULT_CRITICALITY_WEIGHTS = CRITICAL 5.0, WARNING 2.0, INFO 1.0; run_regression.py pasa el cost context explícitamente; decisión: NO cambiar el default del composition root (Explicit over Implicit + YAGNI); (3) Task 2.3.3 DONE — dominio canónico no aplica .strip(); H-5.2-6 registrado como ACCEPTED_LIMITATION: ASTFingerprintPolicy aplica .strip() confinado al tooling experimental; (4) Decisión arquitectónica registrada: configuración canónica de criticidad vive en el caller explícito, no en el default del composition root. |
| 1.2.9 | 2026-09-10 | **Wave 2.4 completada (7 Tasks DONE), Gate 2 COMPLETED:** (1) Task 2.4.1 DONE por construcción — ForestDistanceCalculator maneja VIRTUAL_ROOT_ID con costo 0.0; (2) Task 2.4.2 DONE por construcción — HeadingAnchorPartitionStrategy + TreeEditDistanceEvaluator implementan Σ TED(windows); (3) Task 2.4.3 DONE — CanonicalEngineConfiguration + ConfigurationFingerprintCalculator implementados con module.qualname, 12 tests nuevos; (4) Task 2.4.4 DONE por construcción — RegressionThresholds, DoubleProtectionMechanism, CriticalityVerdictEmitter; (5) Task 2.4.5 DONE — configuration_fingerprint propagado en RegressionReport y run_regression.py; (6) Task 2.4.6 DONE — 6 tests de determinismo PASSED; (7) Task 2.4.7 DONE — DF-04 benchmark ejecutado: divergencia 8.56% (promedio), 22.63% (máxima), 4 causas raíz documentadas, APTED como experimental no-normativo; (8) DF-04 reclasificado a RESOLVED; (9) Gate 2 → COMPLETED (17/17 Tasks, 43/43 rules); (10) MIG-07 ejecutado. |
| 1.3.0 | 2026-09-10 | **Wave 3.1 completada (4 Tasks DONE):** (1) Task 3.1.1 DONE — CALIBRATION/VALIDATION/FINAL EVALUATION definidas como fases secuenciales distintas (NADR-23 §5.1 R1-R3); (2) Task 3.1.2 DONE — partición por content identity SHA-256, 6 documentos verificados sin duplicados; (3) Task 3.1.3 DONE — disjunción Calibration ∩ Final = ∅ trivialmente satisfecha (Calibration = ∅); (4) Task 3.1.4 DONE — estrategia de independencia estadística documentada: N=6 < 20, NADR-23 R12 prohíbe presumir robustez estadística, LOCAL_CALIBRATION_SET = ∅, SANITY_VALIDATION_SET = 6 docs, FINAL_EVALUATION_SET reservado para Gate 5; (5) H-5.3-1 registrado como ACCEPTED_LIMITATION: calibración estadística no ejecutable con 6 documentos, defaults evidence-informed por diseño, recalibración pendiente para corpus ≥20; (6) Dataset Independence Record creado; (7) Gate 3 Status → IN PROGRESS; (8) Reglas NADR-23 §5.1 R1-R3 y §5.3 R9-R13 (8 reglas) → DONE. |
| 1.3.1 | 2026-09-10 | **Wave 3.2 completada (3 Tasks DONE):** (1) Task 3.2.1 DONE — protocolo de calibración definido antes de elegir algoritmo (NADR-23 §5.2 R4-R8); 8 elementos del protocolo documentados (variable, ground truth observable, función objetivo, espacio de parámetros, restricciones, unidad de evaluación, independencia de datasets, criterio de aceptación); aprobación condicional a corpus ≥20; (2) Task 3.2.2 DONE — lifecycle CAL→VAL→FREEZE ejecutado: CALIBRATION = ∅ (N=6 insuficiente), VALIDATION = sanity validation ejecutada sobre 6 documentos sellados, PARAMETER FREEZE sobre defaults (fingerprint b942fc95...), FINAL EVALUATION reservada para Gate 5; regla anti-leakage reforzada (NADR-23 R2); (3) Task 3.2.3 DONE — condiciones de validez científica documentadas (R26-R28): defaults clasificados como NORMATIVOS (no calibrados empíricamente), distinción tuning vs calibración verificable, H-5.3-2 y H-5.3-3 registrados como ACCEPTED_LIMITATION; (4) H-5.3-2 registrado — divergencia masiva entre runtime de producción y GTs curados (5/6 HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536); consistente con limitaciones de PyMuPDFProvider documentadas en H-5.1-9 y H-5.1-10; confirma que el problema es estructural (extractor), no paramétrico; (5) H-5.3-3 registrado — GT de doc_07_pesaran no editado en curaduría; NSS=1.0000 es tautología (extractor contra sí mismo), no validación positiva; documento contiene tablas que PyMuPDF no extrae (fuentes Type 3); curaduría real diferida con ampliación de corpus (H-5.2-1); (6) Calibration Protocol Record creado; (7) Reglas NADR-23 §5.2 R4-R8, §5.4 R14-R16, §5.7 R26-R28 (11 reglas) → DONE. |
| 1.3.2 | 2026-09-11 | **Wave 3.3 completada (3 Tasks DONE), Gate 3 COMPLETED:** (1) Task 3.3.1 DONE — Calibration Provenance Record materializado en `reports/calibration/calibration_provenance_record.json` con los 5 campos mínimos R18 (corpus_identity, metric_configuration, parameters, result, timestamp) y los 3 tipos de identidad R20; calibration_run=NONE, parameters_origin=NORMATIVE_DESIGN (distinguibilidad R28); (2) Task 3.3.2 DONE — Parameter freeze ejecutado vía MIG-08 con `tools/evaluation/freeze_parameters.py`: artefacto `reports/calibration/parameter_freeze.json` con parameter_identity `6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5`, distinta de configuration_identity por diseño (evita falsas nuevas líneas de certificación ante cambios de motor sin cambio de parámetros); inmutabilidad R25 verificada por exit code 2 ante conflicto; verificabilidad R24 por test de enforcement sobre artefacto del repo (`test_repo_freeze_artifact_matches_domain_defaults` PASSED post-MIG-08); (3) Task 3.3.3 DONE — Evaluation Provenance Record emitido en `reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json`, nombre acotado por kind, trazable vía experiment_identity (R31), con limitaciones H-5.3-1, H-5.3-2, H-5.3-3; idempotencia por kind verificada (`test_final_evaluation_record_emitted_over_existing_freeze` PASSED); (4) Nuevo módulo de dominio `core/benchmark/topology/regression/provenance.py` con dataclasses frozen, invariantes de thresholds y serialización canónica; (5) 18 tests unitarios + 7 tests de integración PASSED (baseline 665 passed, 5 skipped); (6) Provenance Record creado (`FASE_5_WAVE_3_3_PROVENANCE_RECORD.md` v1.0.0); (7) Corrección aritmética del Status Dashboard (44 tasks DONE, 130 rules DONE, 38 pending); (8) Criterio de R17 (FINAL EVALUATION sobre conjunto disjunto) contabilizado en Gate 3 por implementación primaria en Task 3.2.2; (9) Gate 3 → COMPLETED (10/10 Tasks, 31/31 rules). |
| 1.3.3 | 2026-09-12 | **Wave 4.1 y Wave 4.2 completadas (6 Tasks DONE, 22 reglas):** (1) Task 4.1.1 DONE — Contrato de ejecución materializado en `core/benchmark/certification/contract.py` con tres capas distinguibles (ExecutionOutcome / ScientificResult / CertificationStatus) conforme a NADR-24 §5.1 R5; `compose_certification_status` con rama explícita para ausencia de componente (R4); `CertificationExecutionContract` frozen con 4 identidades; (2) Task 4.1.2 DONE — PREFLIGHT implementado en `core/benchmark/certification/preflight.py` como Functional Core puro (`evaluate_preflight` con 13 kwargs keyword-only, 8 precondiciones R7 evaluables, determinista, idempotente R9); CLI en `tools/evaluation/preflight_certification.py` como Imperative Shell (4 argumentos required R10/R11, reutilización estricta de LoadCorpusManifestUseCase, BaselineCompletenessVerifier, RegressionAdapter, ConfigurationFingerprintCalculator, parameter_freeze.json); 14 tests unitarios nuevos (`test_certification_preflight.py`); happy path exit 0 + failure path exit 2 verificados; (3) Task 4.1.3 DONE — GAP-5.0-03 remediado: 5 entry points migrados a CLI con `--corpus-dir` required (`bootstrap_corpus`, `freeze_ground_truth`, `generate_golden_draft`, `generate_pymupdf_candidate`, `sanitize_ground_truth_types`); aritmética de cierre: 5 remediados + 4 ya explícitos + 1 deprecated que hereda + 1 fuera de scope con justificación = 11 entry points auditados; cambio rompiente documentado; decisión explícita de que `argparse.sys.exit(2)` ante required ausente propaga limpio porque `SystemExit` no hereda de `Exception` (C3); (4) Task 4.2.1 DONE — Taxonomía uniforme materializada en `core/shared/exit_codes.py` (EXIT_OK=0, EXIT_CERTIFICATION_REJECTED=1, EXIT_EXECUTION_FAILURE=2, frontera documentada: dominio no importa) y `core/shared/errors.py` (`IndexedError` con código indexable); `tools/evaluation/entry_guard.py` como guard de traducción R19 (traduce excepciones no capturadas a categoría c con `[UNEXPECTED-001]`); (5) Task 4.2.2 DONE — Tolerancia a fallos parciales ≠ certificación parcial (R22): `generate_golden_draft.py` introduce helper puro `classify_document_error` (D1: sealed oracle → skip, resto → failure), contadores separados `skips`/`failures`, `[DRAFT-001/002/003]` indexables, `[DRAFT-W01/W02]` para skips esperados; re-ejecución sobre corpus sellado mantiene exit 0 (idempotencia R33); (6) Task 4.2.3 DONE — DF-18 remediado: 4 entry points (`freeze_ground_truth`, `generate_golden_draft`, `generate_pymupdf_candidate`, `sanitize_ground_truth_types`) con `main() -> int` + `run_entry(main)`; D2 aplicado en sanitize (`--allow-missing-manifest` override explícito e indexable; sin manifest y sin override → `IndexedError SANITIZE-001`, aborta R26; evolución normativa NADR-21 → NADR-24 documentada); D3 aplicado en `freeze_parameters.py` (eliminación de `EXIT_CONTRACT_VIOLATION=1`, unificación en `EXIT_EXECUTION_FAILURE=2`, códigos `[FREEZE-PARAM-001..005]`); tests actualizados: `test_no_manifest_aborts_without_override`, `test_no_manifest_with_override_sanitizes`, `test_invalid_timestamp_returns_exit_2`, `test_missing_report_returns_exit_2_without_partial_state`; 5 tests nuevos en `test_exit_codes_and_guard.py` (TestRunEntryTranslation + TestClassifyDocumentError); (7) GF-01 registrado: conflicto real entre NADR-19 §5.5 R22 (run_regression taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) y NADR-24 §5.4 R15-R17 (2 = fallo de ejecución); resolución por separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta de regresión CI; el runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24 traduciendo veredicto científico a categoría (a)/(b) y crashes a (c); por eso `run_regression` NO se toca en Wave 4.2; (8) H-5.4-1 registrado como evidencia forense: pre-remediación, `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]` — falso positivo operacional confirmado (R16, R18); (9) H-5.4-2 registrado como evidencia forense: durante el pre-check de GAP-5.0-03, el run espurio de `generate_pymupdf_candidate.py` mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (revertidos con `git checkout`); evidencia dura del riesgo DF-18/GAP-5.0-03 que motiva la remediación; (10) Nuevo paquete de dominio `core/benchmark/certification/` (3 módulos, cero imports de infra en dominio); 24 tests nuevos totales (14 + 5 + 5 de test_certification_preflight, test_exit_codes_and_guard, actualizaciones); baseline: 685 passed, 5 skipped; (11) Corrección aritmética del Status Dashboard (50 tasks DONE, 152 rules DONE, 16 pending); (12) Gate 4 Status → IN PROGRESS (6/13 Tasks, 22/37 rules). |
| 1.3.4 | 2026-09-13 | **Wave 4.3 completada (4 Tasks DONE, 9 reglas):** (1) Task 4.3.1 DONE — Boundary integrity verificada mediante AUDIT forense (5 comandos) + 10 contract tests en `test_certification_boundary.py`; SealedOracle frozen (model_config frozen=True, test_pydantic_frozen_config), sin mutadores de instancia, asignación bloqueada (test_assignment_raises ValidationError); LifecycleTransitionAuthority importada únicamente por `use_cases.py` (dominio) y `freeze_ground_truth.py` (sellado MIG-06, O-4.3-3); 3 adaptadores de `ground_truth_store.py` apuntan exclusivamente a `base_path/ground_truth`; tooling de certificación no importa puertos de escritura GT; (2) Task 4.3.2 DONE — GAP-5.2-05 verificación formal de la protección implementada en Wave 2.1 (Task 2.1.2): cadena sanitize/use cases/override D2 verificada; `sanitize_ground_truth_types.py` verifica estado de sellado antes de escribir (raise `SealedOracleOverwriteError`); `GenerateGoldenDraftUseCase` verifica estado antes de escribir; override `--allow-missing-manifest` explícito e indexable (fuera de ejecución certificante); (3) Task 4.3.3 DONE — Evidence completeness implementada: `core/benchmark/certification/evidence.py` con `CertificationEvidence` (7 elementos R29 + `evaluation_kind` + `result_identity`), `compute_corpus_content_identity` (SHA-256 de SHA-256 ordenados, fail-fast ante vacío NADR-20 R1), `serialize_evidence` determinista (sort_keys, indent fijo, ensure_ascii=False); GF-02 registrado como crosswalk normativo: `corpus_identity` = compuesto de contenido (NADR-20 §5.1-§5.5, estable entre sellados), `manifest_identity` = `manifest_hash` (NADR-20 §5.6 R24/R26, cambia al sellar); artefactos de Wave 3.3 permanecen válidos; (4) Task 4.3.4 DONE — POST-RUN VALIDATION implementada: `core/benchmark/certification/post_run.py` con `validate_post_run` (5 checks: provenance verifiable, per-document present, aggregate present, evidence elements, identity consistency); violaciones nombradas por elemento R29 (R30/R37); wiring con disco diferido a Gate 5 Task 5.2.1; (5) O-4.3-3 registrado: `freeze_ground_truth.py` importa `LifecycleTransitionAuthority` (entry point de sellado MIG-06, orquesta ciclo de vida en memoria invocando la autoridad; R28 prohíbe bypassear, no invocar; allowlist extendido con justificación); (6) Nuevo paquete `core/benchmark/certification/` (4 módulos: contract, preflight, evidence, post_run); 28 tests nuevos totales en Gate 4 (14 PREFLIGHT + 10 boundary + 18 evidence/post-run); baseline: 713 passed, 5 skipped; (7) Corrección aritmética del Status Dashboard: 54 tasks DONE, 161 rules DONE, 7 pending; (8) Gate 4 Status → IN PROGRESS (10/13 Tasks, 31/37 rules). |
| 1.3.5 | 2026-09-13 | **Wave 4.4 completada (3 Tasks DONE, 4 reglas), Gate 4 COMPLETED (13/13 tasks, 37/37 rules):** (1) Task 4.4.1 DONE — Determinismo operacional (R32) verificado: tooling de certificación determinista por construcción (timestamps inyectados externamente, `sort_keys=True` en serialización, hashes sobre bytes canónicos); O-4.4-1 registrado: `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en certificación (verificar en Gate 5 si se propaga); (2) Task 4.4.2 DONE — Idempotencia lógica (R33) verificada: cero operaciones append a archivos en tooling de certificación; escrituras usan `write_text`/`write_bytes` (overwrite); O-4.4-2 registrado: `reporter.py:71 np.random.choice` en bootstrap estadístico, no en reporte de certificación; (3) Task 4.4.3 DONE — Recovery determinable (R34-R35): estado post-fallo determinable vía `validate_post_run` (violaciones nombradas por elemento); atomicidad física solo donde el dominio la exige (`core/ast/registry.py`, `infra/fs/corpus_repository.py` usan `tempfile + os.replace`); O-4.4-3 registrado: `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall); no se migra porque R34/R35 no la exigen para reportes y añadiría superficie de cambio sin beneficio normativo (YAGNI); la ventana de corrupción ante crash se cubre con POST-RUN VALIDATION más re-ejecución manual; 7 tests nuevos (3 determinismo + 2 idempotencia + 2 recovery); baseline: 720 passed, 5 skipped (713 + 7); (4) Gate 4 → COMPLETED (13/13 Tasks, 37/37 rules); (5) Gate 5 habilitado; (6) Corrección aritmética del Status Dashboard: 57 tasks DONE, 167 rules DONE, 1 pending (R20 en Gate 1). |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
ADR_F17_BIS_05 (decisión arquitectónica de Fase 5, FROZEN)
↓
NADRs 20-24 (reglas constitucionales permanentes, FROZEN, 168 reglas)
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

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN** (168 reglas). Este documento no replica ni contabiliza reglas; únicamente las referencia.

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
**Gate Status:** 🟡 IN PROGRESS

#### 2.1.1 Wave 1.1 — Corpus Discovery & Identity (NADR-20 §5.1, §5.2, §5.5)

**Wave Status:** 🟡 IN PROGRESS (4/5 Tasks DONE, Task 1.1.5 pendiente: déficit de 13 documentos)
**Fecha de inicio:** 2026-09-06
**Fecha de cierre:** —

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Seleccionar 20-30 documentos de alta varianza. Criterios específicos: papers IEEE (doble columna), libros densos, documentos con ecuaciones matemáticas complejas, tablas, figuras, gráficos. Verificar diversidad de layouts, estructuras documentales, desafíos de extracción y dominios científicos. | NADR-20 §5.5 R19-R21 | Medium | MIG-01 | ✅ DONE |
| **1.1.2** | Copiar los documentos seleccionados al directorio `tests/corpus/canonical/pdf/`. Verificar integridad de cada archivo (apertura con PyMuPDF). | NADR-20 §5.1 R1-R2 | Low | 1.1.1 | ✅ DONE |
| **1.1.3** | Calcular SHA-256 de cada documento del corpus canónico. Verificar unicidad de hashes (sin duplicados). | NADR-20 §5.1 R1, R3-R4 | Low | 1.1.2 | ✅ DONE |
| **1.1.4** | Deduplicación por contenido: consolidación de grupos G1/G2 (HITO 5.1). Verificar idempotencia. | NADR-20 §5.2 R5-R9 | Medium | 1.1.3 | ✅ DONE |
| **1.1.5** | Documentación del déficit de corpus y plan de adquisición. | NADR-20 §5.5 R19-R21 | Low | 1.1.4 | 🟡 IN PROGRESS |

#### Notas de implementación — Task 1.1.1

> 7 identidades seleccionadas del corpus existente: doc_01_single (paper económico, ecuaciones), doc_02_double (doble columna, ecuaciones), doc_03_math (OCR dependency, matemáticas), doc_04_table (tablas complejas, figuras, ecuación), doc_05_graph (doble columna, mixed content), doc_06_johnstone (OCR dependency, matemático denso), doc_07_pesaran (econometría, 41 páginas — se recortará a 3 más adelante). Fuentes: calibration_v1/pdf/ (5 docs), tests/corpus/ raíz (johnstone), datasets/raw/ (pesaran). Déficit de 13 documentos documentado. Los 7 traits del catálogo ExtractionChallengeTrait están cubiertos.

#### Notas de implementación — Task 1.1.2

> Directorio `tests/corpus/canonical/pdf/` creado. 7 PDFs copiados desde fuentes verificadas. Integridad verificada con PyMuPDF: todos los archivos abren sin error. Páginas: doc_01-06 (3 páginas cada uno), doc_07 (41 páginas).

#### Notas de implementación — Task 1.1.3

> SHA-256 calculado para los 7 documentos. 7 hashes únicos verificados: 2a1bab7f (doc_01), 84891f98 (doc_02), 21b9283a (doc_03), de56cd04 (doc_04), 274ce908 (doc_05), b4f8e7a8 (doc_06), f1c80072 (doc_07). Sin duplicados.

#### Notas de implementación — Task 1.1.4

> Deduplicación resuelta por construcción: al copiar solo una copia por identidad al corpus canónico, los duplicados quedaron excluidos. Grupos consolidados: G1 (Amoretal = doc_02_double, 3 copias → 1 identidad 84891f98), G2 (Marchenko = doc_03_math, 2 copias → 1 identidad 21b9283a). Idempotencia verificada: 7 hashes = 7 archivos. Archivos originales en tests/corpus/ preservados como fuentes históricas (backup MIG-01).

#### Notas de implementación — Task 1.1.5

> Déficit documentado: 7/20 identidades (déficit de 13 documentos). Objetivo mínimo 20 (NADR-20 §5.5 R20), máximo 30 (ADR Maestro §6). Certificación BLOQUEADA hasta ≥20 identidades. Tasks de código NO bloqueadas (avanzan con 7 documentos). Cobertura de traits completa (7/7): NATIVE_PDF (5), MULTI_COLUMN (2), HEAVY_MATHEMATICS (6), COMPLEX_TABLES (2), DENSE_TYPOGRAPHY (1), MIXED_CONTENT (2), OCR_DEPENDENCY (2). Plan de adquisición: usuario buscará 13+ documentos adicionales.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.1-1 | Discrepancia: HITO 5.1 reportaba 7 identidades, evidencia actual verifica 6. La identidad faltante (pesaran1999.pdf) estaba en datasets/raw/, fuera de tests/corpus/. Incluida como doc_07. | Findings Register §9 |
| H-5.1-2 | Archivo temporal huérfano: tests/corpus/calibration_v1/candidates/pymupdf/tmptu237h6p (35,557 bytes). Limpiar en Gate 1 W1.2. | Findings Register §9 |
| H-5.1-3 | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy). Migración requerida en Task 1.3.8. | Findings Register §9 |
| H-5.1-4 | doc_03_math y doc_06_johnstone son scanned_noise (no native_pdf). Clasificación corregida en manifest canónico con nombres del catálogo vigente. | Gate 1 W1.1 T1.1.1 → W1.2 T1.2.1 | RESOLVED |

#### 2.1.2 Wave 1.2 — Corpus Qualification & Manifest (NADR-20 §5.3, §5.4, §5.6, §5.7)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-06
**Fecha de cierre:** 2026-09-06

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Verificación de traits por inspección de contenido de cada documento. Verificar contra catálogo vigente (ExtractionChallengeTrait). | NADR-20 §5.3 R10-R13 | High | 1.1.4 | ✅ DONE |
| **1.2.2** | Proceso de cualificación formal con registro auditable (origen, fecha, responsable). | NADR-20 §5.4 R14-R18 | Medium | 1.2.1 | ✅ DONE |
| **1.2.3** | Implementar el contrato del manifest canónico: formato 6D (document_id, sha256, traits, page_count, oracle_hash, ground_truth_state). Hash recomputable. Define el contrato, no ejecuta la migración. | NADR-20 §5.6 R22-R26 | High | 1.2.2 | ✅ DONE |
| **1.2.4** | Provenance de corpus: origen, fecha, responsable. Provenance ≠ identidad. | NADR-20 §5.7 R27-R28 | Low | 1.2.3 | ✅ DONE |

#### Notas de implementación — Task 1.2.1

> Clasificación de traits completada contra catálogo vigente (ExtractionChallengeTrait). 7 traits del catálogo, 6 cubiertos (falta bilingual_mix). H-5.1-5 registrado y RESOLVED: los nombres preliminares (DENSE_TYPOGRAPHY, MIXED_CONTENT) no existen en el catálogo; HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise. Clasificación final: doc_01 (native_pdf, heavy_math), doc_02 (native_pdf, multi_column, heavy_math), doc_03 (scanned_noise, heavy_math), doc_04 (native_pdf, nested_tables, heavy_math, floating_figures), doc_05 (native_pdf, multi_column, floating_figures), doc_06 (scanned_noise, heavy_math), doc_07 (native_pdf, heavy_math, nested_tables).

#### Notas de implementación — Task 1.2.2

> Cualificación formal registrada en FASE_5_WAVE_1_2_QUALIFICATION_RECORD.md (reviews/). 7 documentos cualificados por inspección visual de curaduría humana experta. Registro auditable con origen, fecha, responsable y método de verificación.

#### Notas de implementación — Task 1.2.3

> Contrato del manifest 6D implementado y verificado. Seed manifest creado con hashes reales y traits correctos usando RawDocumentEntryDTO y CorpusDocumentMetadata. Verificado con BootstrapCorpusManifestUseCase: seed hash == bootstrap hash (62f0df16c6faecd6bac7662438f24c0a407e4c46f3271f894933456cc39bc0f1). Reutilización estricta (ADR Maestro §5): PyMuPdfDocumentMetadataExtractor, ManifestFingerprintCalculator, LocalFileSystemCorpusLoader, BootstrapCorpusManifestUseCase. Cero código nuevo introducido. Archivo: tests/corpus/canonical/manifest.json.

#### Notas de implementación — Task 1.2.4

> Provenance registrado en FASE_5_WAVE_1_2_PROVENANCE.md (reviews/). Linaje completo de los 7 documentos: 5 de calibration_v1/pdf/, 1 de tests/corpus/ raíz (johnstone), 1 de datasets/raw/ (pesaran). Provenance ≠ identidad documentado.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.1-5 | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente (ExtractionChallengeTrait). Reclasificación completada. | Findings Register §3.3 (RESOLVED) |
| H-5.1-6 | Contrato del manifest verificado como 6D plano en RawDocumentEntryDTO. sha256 encapsulado en DocumentFingerprint a nivel de dominio pero aplanado en DTO. El contrato 6D es correcto. | Gate 1 W1.2 T1.2.3 | CLOSED (NAR) |

#### 2.1.3 Wave 1.3 — GT Migration & Eligibility (NADR-21 §5.1, §5.2, §5.3, §5.6, §5.7, §5.8)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-06
**Fecha de cierre:** 2026-09-09

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.3.1** | Ejecutar/materializar la migración del artefacto legacy DF-19 al formato vigente (6D). Aplica el contrato definido en Task 1.2.3. | NADR-21 §5.8 R38, DF-19 | High | 1.2.3 | ✅ DONE |
| **1.3.2** | Canonicalización de node_ids: `"value='p1_b0'"` → `"p1_b0"`. Determinista, con trazabilidad de lineage. | NADR-21 §5.2 R8-R12 | Critical | 1.3.1 | ✅ DONE |
| **1.3.3** | Verificación de hidratación bajo contrato vigente (hydrate_ground_truth). | NADR-21 §5.1 R1-R3 | Medium | 1.3.2 | ✅ DONE |
| **1.3.4** | Verificación de validez estructural (no vaciedad, no duplicados, integridad, consistencia). | NADR-21 §5.3 R13-R16 | Medium | 1.3.3 | ✅ DONE |
| **1.3.5** | Verificación de elegibilidad completa. | NADR-21 §5.1 R4-R7 | Medium | 1.3.4 | ✅ DONE |
| **1.3.6** | Verificación de identidad semántica del candidato elegible (antes del sealing). | NADR-21 §5.6 R28-R31 | Medium | 1.3.5 | ✅ DONE |
| **1.3.7** | Verificación de identidad de baseline (hash encadenado). | NADR-21 §5.7 R32-R34 | Medium | 1.3.6 | ✅ DONE |
| **1.3.8** | Migración de .ast.json legacy (H-5.1-3) o decisión de re-extracción. | NADR-21 §5.8 R35-R37 | High | 1.3.5 | ✅ DONE |
| **1.3.9** | Curaduría manual de Ground Truths: verificar que cada AST representa fielmente la estructura del documento fuente. Corregir errores de extracción. La curaduría ocurre ANTES del sealing, nunca después. | NADR-21 §5.1 R5 | High | 1.3.8 | ✅ DONE |

#### Notas de implementación — Task 1.3.1

> DF-19 verificado por construcción: el manifest canónico generado en Wave 1.2 ya está en formato 6D vigente. Verificación formal ejecutada: los 7 documentos tienen los 6 campos vigentes (document_id, sha256, traits, page_count, oracle_hash, ground_truth_state), sin campos legacy (ground_truth_version, ground_truth_sha256). H-5.1-2 RESOLVED: archivo temporal huérfano tmptu237h6p eliminado. H-5.1-8 registrado y CLOSED (NAR): ManifestFingerprintCalculator.compute_hash() incluye page_count en el payload (verificado en source code). El hash 62f0df16 es correcto y completo.

#### Notas de implementación — Task 1.3.2

> Canonicalización de node_ids completada: 401/401 nodos transformados de formato legacy ("value='p1_b0'") a formato canónico ("p1_b0"). Registro de lineage guardado en tests/corpus/canonical/ground_truth/canonicalization_lineage.json con old_id, new_id y flag de canonicalización para cada nodo. GTs canonicalizados guardados en tests/corpus/canonical/ground_truth/ (no se sobrescribieron los originales en calibration_v1). Cero node_ids legacy restantes verificados.

#### Notas de implementación — Task 1.3.3

> Hidratación verificada para 5 GTs (doc_01 a doc_05): todos se hidratan correctamente como GroundTruthDraft bajo contrato vigente. Se usó hydrate_ground_truth() con nodes como tuple (contrato de inmutabilidad del dominio) y state leído del manifest (GroundTruthLifecycleState.DRAFT para pre-sealing). doc_07_pesaran aún no tenía GT en este punto (se generó en Task 1.3.8). doc_06_johnstone no tiene GT (scanned_noise, requiere OCR).

#### Notas de implementación — Task 1.3.4

> Validez estructural verificada para 5 GTs usando OracleValidityContract.validate() del dominio (reutilización estricta, ADR Maestro §5). Verificación adicional R16 (consistencia de parent_node_id): cero orfanos. H-5.1-7 registrado: todos los parent_node_id son None en los 5 GTs, consistente con Flat Design (ENGINEERING_PRINCIPLES §II). Pendiente verificación contra PDFs reales en curaduría.

#### Notas de implementación — Task 1.3.5

> Elegibilidad completa verificada para 5 GTs: (R4) validación estructural pasada en Task 1.3.4; (R5) cero node_ids legacy restantes (Task 1.3.2); (R6) identidad semántica calculable vía OracleSemanticIdentityCalculator; (R7) ground_truth_state=None en manifest (pre-sealing, correcto). Los 5 documentos son elegibles para avanzar en el ciclo de vida.

#### Notas de implementación — Task 1.3.6

> Identidad semántica calculada para 5 GTs vía OracleSemanticIdentityCalculator: doc_01 (fe0f8409...), doc_02 (51d651de...), doc_03 (679e5443...), doc_04 (c71a4d4c...), doc_05 (f81575ba...). 5 identidades únicas, sin colisiones. Verificación pre-sealing conforme a NADR-21 §5.6 R28-R31.

#### Notas de implementación — Task 1.3.7

> Identidad de baseline verificada: hash actual del manifest (62f0df16...) coincide con el recalculado vía ManifestFingerprintCalculator.compute_hash(). Hash futuro proyectado con oracle_hash (2e82a631...) calculado determinísticamente. El contrato de hash incluye los 6 campos del formato 6D (verificado en source code). Determinismo del hash encadenado confirmado.

#### Notas de implementación — Task 1.3.8

> Decisión: re-extracción (Opción B). El AST legacy de pesaran1999.pdf (597 nodos, formato legacy: type/content sin node_type/strategy/payload) NO fue migrado. El PDF fue recortado de 41 a 3 páginas por el usuario (selección de páginas con tablas y ecuaciones). Nuevo SHA-256: 168bf271... (anterior: f1c80072...). GT re-extraído vía GenerateGoldenDraftUseCase con Composition Root canónica (BenchmarkParserBridge + build_extraction_pipeline()). Resultado: 21 nodos (17 paragraph + 4 heading), formato vigente AST V2, OracleValidityContract pasado. Manifest actualizado: SHA-256 y page_count=3, manifest_hash recalculado: 39cc80bd1621f5a73416e41b045500a191aeb6fe286e7319066d4bd9c445a4f4. Limitación documentada: PyMuPDF no extrae tablas ni ecuaciones de este PDF (fuentes Type 3 sin ToUnicode). H-5.1-3 RESOLVED.

#### Notas de implementación — Task 1.3.9

> Curaduría manual completada para 6 GTs. Curation Report generado en docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_1_3_CURATION_REPORT.md. Resultados: 3 ACEPTADOS sin observaciones (doc_01, doc_03, doc_04), 3 ACEPTADOS CON OBSERVACIÓN (doc_02: fragmentación de ecuaciones en doble columna; doc_05: labels de ejes como paragraphs; doc_07: limitación de fuentes Type 3). Nota metodológica documentada: sesgo del GT hacia el extractor de producción (tautología parcial). Hallazgos derivados: H-5.1-9 (ACCEPTED_LIMITATION), H-5.1-10 (ACCEPTED_LIMITATION), H-5.1-11 (RECLASSIFIED_FUTURE_PHASE: patrón Detect & Placeholder). doc_06_johnstone sin GT (scanned_noise, requiere pipeline OCR no disponible).

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.1-7 | Todos los parent_node_id son None en los 5 GTs. Consistente con Flat Design. Verificación contra PDFs reales en curaduría. | Findings Register §3.3 (PENDING_REVIEW → verificado en curaduría) |
| H-5.1-8 | ManifestFingerprintCalculator.compute_hash() incluye page_count. Hash anterior coincidió por valor por defecto de Pydantic. | Findings Register §3.3 (CLOSED NAR) |
| H-5.1-9 | doc_02_double: 52 nodos display_equation con fragmentos garbled. PyMuPDF no agrupa ecuaciones en doble columna. | Findings Register §3.3 (ACCEPTED_LIMITATION) |
| H-5.1-10 | doc_05_graph: 56 labels de ejes como paragraphs. Estructura de gráficos no capturada. | Findings Register §3.3 (ACCEPTED_LIMITATION) |
| H-5.1-11 | Propuesta de patrón Detect & Placeholder para extracción de tablas/figuras/ecuaciones. Fuera del scope de Fase 17-BIS (ADR §4). | Findings Register §3.3 (RECLASSIFIED_FUTURE_PHASE) |

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
**Gate Status:** ✅ COMPLETED

#### 2.2.1 Wave 2.1 — GT Validation & Structural Integrity (NADR-21 §5.4, §5.9)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-09
**Fecha de cierre:** 2026-09-09

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Verificación del ciclo de vida Draft→Audited→Validated→Sealed. | NADR-21 §5.4 R17-R21 | Medium | Gate 1 | ✅ DONE |
| **2.1.2** | Protección de SealedOracle: remediación de GAP-5.2-05 (sanitize_ground_truth_types.py). Verificar que ningún mecanismo puede modificar oráculos sellados sin verificación de estado. | NADR-21 §5.9 R39-R43, GAP-5.2-05 | Critical | 2.1.1 | ✅ DONE |

#### Notas de implementación — Task 2.1.1

> Ciclo de vida verificado por construcción. LifecycleTransitionAuthority expone 5 métodos de transición (audit, validate, seal, rollback_to_draft, rollback_to_audited). Diseño type-state: seal() retorna SealedOracle (tipo diferente, no GroundTruthDraft con estado). GroundTruthLifecycleState tiene 4 estados: DRAFT, AUDITED, VALIDATED, SEALED (verificado por tests test_four_states_with_canonical_values y test_exactly_four_states). 19 tests de lifecycle PASSED (5 legales, 8 ilegales, 2 no-rollback SealedOracle, 4 inmutabilidad). 23 tests de modelos PASSED (incluyendo hidratación por estado y tipos disjuntos Draft/Oracle). Reutilización estricta (ADR §5): cero código nuevo, infraestructura existente verificada.

#### Notas de implementación — Task 2.1.2

> GAP-5.2-05 remediado. sanitize_ground_truth_types.py refactorizado: (1) carga manifest vía LocalFileSystemCorpusLoader (reutilización estricta); (2) verifica ground_truth_state de cada documento contra GroundTruthLifecycleState.SEALED.value del dominio; (3) lanza SealedOracleOverwriteError (fail-hard, no skip silencioso) si se intenta modificar oráculo sellado; (4) emite warning indexable [AST-SANITIZE-001] para node_types desconocidos sin mapeo (Cero Fallos Silenciosos). Protección agnóstica del directorio (funciona para cualquier corpus). 3 tests nuevos en test_sanitize_ground_truth_types.py: sealed_raises_overwrite_error, draft_is_sanitized, no_manifest_allows_sanitization. Pyright 0 errors. Baseline no degradada: 627 passed, 5 skipped.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.2-1 | doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6. Requiere re-incorporación con pipeline OCR (junto con déficit de 13 docs). Manifest hash recalculado: 39cc80bd → fae41bb5. | Findings Register §3.3 (IMPLEMENTATION_REQUIRED) |
| H-5.2-2 | GroundTruthLifecycleState muestra 3 estados en runtime pero tests esperan 4. Verificación: enum SÍ tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED). Tests test_four_states y test_exactly_four_states PASSED. Diseño type-state confirmado. | Findings Register §3.3 (CLOSED NAR) |

#### 2.2.2 Wave 2.2 — Zero Partial Sealing & Oracle Identity (NADR-21 §5.5, §5.6, §5.7)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-09
**Fecha de cierre:** 2026-09-09

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Sellado lógicamente atómico con Zero Partial Sealing (biyección PDF↔GT). Ejecutar `freeze_ground_truth.py`. | NADR-21 §5.5 R22-R27 | Critical | 2.1.2 | ✅ DONE |
| **2.2.2** | Verificación de correspondencia biyectiva ($N_{PDF} = N_{GT}$). Verificar que no hay documentos sin oráculo ni oráculos huérfanos. | NADR-21 §5.5 R23 | Critical | 2.2.1 | ✅ DONE |
| **2.2.3** | Verificación de identidad semántica del Oracle sellado (después del sealing). | NADR-21 §5.6 R28-R31 | Medium | 2.2.1 | ✅ DONE |
| **2.2.4** | Verificación de identidad de baseline (hash encadenado). Verificar que el manifest se actualiza correctamente con oracle_hash y ground_truth_state. | NADR-21 §5.7 R32-R34 | Medium | 2.2.2 | ✅ DONE |
| **2.2.5** | Verificación de atomicidad lógica del sellado mediante fault injection / test: o se sellan todos los documentos, o no se sella ninguno. | NADR-21 §5.5 R22, R27 | High | 2.2.1 | ✅ DONE |

#### Notas de implementación — Task 2.2.1

> Sellado ejecutado con freeze_ground_truth.py. MIG-02 ejecutado (backup pre-sealing en tests/corpus_backup_pre_sealing/). MIG-06 ejecutado (sealing irreversible). 6/6 documentos sellados con ground_truth_state='sealed' y oracle_hash poblado. Manifest hash global: 0fda76909289fe8777b8413f4178e2117d2961689437b66e4454c1a7a07a4c34. Hallazgos durante ejecución: (1) H-5.2-3 RESOLVED: canonicalization_lineage.json contaminaba ground_truth/ como oráculo huérfano, movido a canonical/ raíz; (2) H-5.2-4 RESOLVED: freeze_ground_truth.py apuntaba a benchmark_v1, corregido a canonical; (3) H-5.2-5 CLOSED (NAR): log duplicado eliminado. Reutilización estricta: SealGroundTruthUseCase, LifecycleTransitionAuthority, ManifestLineageSealer, BaselineCompletenessVerifier.

#### Notas de implementación — Task 2.2.2

> Biyección verificada post-sealing: 6 PDFs en manifest = 6 GTs en ground_truth/. Cero documentos sin oráculo, cero oráculos huérfanos. BaselineCompletenessVerifier no reporta errores. N_PDF = N_GT = 6 conforme a Zero Partial Sealing (ADR F17_BIS_MASTER §5).

#### Notas de implementación — Task 2.2.3

> Identidad semántica post-sealing verificada para los 6 documentos. Cada oracle_hash almacenado en el manifest coincide exactamente con el recalculado vía OracleSemanticIdentityCalculator.calculate() sobre los nodos hidratados desde disco. Los 6 hashes son idénticos a los pre-sealing verificados en Wave 1.3 Task 1.3.6, confirmando que el sellado no mutó el contenido de los GTs.

#### Notas de implementación — Task 2.2.4

> Identidad de baseline (hash encadenado) verificada. ManifestFingerprintCalculator.compute_hash() recalculado con CorpusVersion y CorpusDocumentMetadata (incluyendo oracle_hash y ground_truth_state='sealed'). Hash almacenado 0fda7690... coincide con recalculado. El hash encadena correctamente: corpus_version, SHA-256 de cada PDF, traits, page_count, oracle_hash y ground_truth_state.

#### Notas de implementación — Task 2.2.5

> Atomicidad del sellado verificada mediante tests existentes: 7/7 tests de test_ground_truth_sealing_atomicity.py PASSED (0.79s). Cobertura: sellado exitoso persiste estado+hash, draft no-VALIDATED aborta, draft huérfano aborta, documento sin draft aborta, sellado multi-documento atómico, oracle_hash determinista entre sellados, ManifestGroundTruthUpdater eliminado (autoridad única).

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.2-3 | canonicalization_lineage.json en ground_truth/ contaminaba BaselineCompletenessVerifier como oráculo huérfano. Movido a canonical/ raíz (separación de concerns). | Findings Register §3.3 (RESOLVED) |
| H-5.2-4 | freeze_ground_truth.py apuntaba a tests/corpus/benchmark_v1/ en lugar de tests/corpus/canonical/. Path corregido. | Findings Register §3.3 (RESOLVED) |
| H-5.2-5 | Log duplicado en freeze_ground_truth.py (misma línea logger.info repetida). Eliminado. | Findings Register §3.3 (CLOSED NAR) |

#### 2.2.3 Wave 2.3 — Canonical Engine Composition (NADR-22 §5.1, §5.2, §5.3)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-09
**Fecha de cierre:** 2026-09-09

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.3.1** | Configuración de ZhangShashaEngine como motor canónico. APTED queda como experimental/benchmark no normativo. | NADR-22 §5.1 R1-R4 | Medium | Gate 1 | ✅ DONE |
| **2.3.2** | Configuración de CriticalityAwareCostContext con pesos 5.0/2.0/1.0. Verificar implementa TreeEditCostContext. | NADR-22 §5.2 R5-R9 | Medium | 2.3.1 | ✅ DONE |
| **2.3.3** | Normalización de texto: sin .strip(), sin fingerprint. Registrar divergencia con ASTFingerprintPolicy como deuda técnica. | NADR-22 §5.3 R10-R12 | Medium | 2.3.2 | ✅ DONE |

#### Notas de implementación — Task 2.3.1

> Verificado por construcción. bootstrap/topology.py::create_topology_evaluator() instancia ZhangShashaEngine(indexer, algorithm) como motor TED. APTED (StructuralTopologyMetric, CustomAPTEDConfig) está aislado en tools/evaluation/topology/metrics/structural.py como métrica experimental del tooling de benchmark, no del dominio canónico. Separación normativo/experimental confirmada: dominio = core/benchmark/topology/ (ZhangShasha), tooling = tools/evaluation/topology/ (APTED).

#### Notas de implementación — Task 2.3.2

> Verificado por construcción. DEFAULT_CRITICALITY_WEIGHTS confirmado: CRITICAL=5.0, WARNING=2.0, INFO=1.0. CriticalityAwareCostContext implementa TreeEditCostContext (verificado por test_implements_tree_edit_cost_context_protocol). Cobertura del mapa de criticidad exhaustiva: los 11 ContentNodeType clasificados. run_regression.py (único caller de create_topology_evaluator) pasa CriticalityAwareCostContext explícitamente. Decisión arquitectónica: el default del composition root permanece UnitCostContext; la configuración canónica vive en el caller explícito conforme a Explicit over Implicit (ENGINEERING_PRINCIPLES §III) y YAGNI (§I).

#### Notas de implementación — Task 2.3.3

> Verificado. Dominio canónico no aplica .strip(): DefaultNodeMatchingPolicy.match() usa comparación exacta de text_content; CriticalityAwareCostContext.substitution_cost() usa comparación exacta. Divergencia registrada: ASTFingerprintPolicy (tools/evaluation/topology/fingerprint.py) aplica .strip() en semantic_fingerprint() e identity_fingerprint(), pero está confinada al tooling experimental (usada por EntityRecallMetric, SequenceAlignmentMetric, StructuralTopologyMetric en tools/evaluation/topology/metrics/). La ruta canónica de regresión (run_regression.py → RegressionEvaluationStrategy → EntityRecallEvaluator) no usa ASTFingerprintPolicy. H-5.2-6 registrado como ACCEPTED_LIMITATION.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.2-6 | ASTFingerprintPolicy.semantic_fingerprint() e identity_fingerprint() aplican .strip(), violando NADR-22 §5.3 R10-R12. Divergencia confinada al tooling experimental (tools/evaluation/topology/). La ruta canónica de regresión no usa fingerprint ni .strip(). | Findings Register §3.3 (ACCEPTED_LIMITATION) |

#### 2.2.4 Wave 2.4 — Engine Configuration Freeze & Verification (NADR-22 §5.4-§5.8) + DF-04

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-09
**Fecha de cierre:** 2026-09-10

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.4.1** | Raíz virtual condicional (solo si multi-root), costo 0. | NADR-22 §5.4 R13-R15 | Low | 2.3.3 | ✅ DONE |
| **2.4.2** | Metodología Σ TED(windows) con HeadingAnchorPartitionStrategy. | NADR-22 §5.5 R16-R18 | Medium | 2.4.1 | ✅ DONE |
| **2.4.3** | Identificador criptográfico de configuración canónica, congelación. Toda modificación invalida certificación vigente. | NADR-22 §5.6 R19-R21 | Medium | 2.4.2 | ✅ DONE |
| **2.4.4** | Thresholds específicos (no universales). DoubleProtectionMechanism canónico. CriticalityVerdictEmitter canónico. | NADR-22 §5.7 R22-R25 | Medium | 2.4.3 | ✅ DONE |
| **2.4.5** | Provenance de evaluación: registro de configuración canónica utilizada. Verificable contra configuración vigente. | NADR-22 §5.8 R26-R27 | Low | 2.4.4 | ✅ DONE |
| **2.4.6** | Verificación de determinismo del motor canónico: misma entrada → mismo resultado. | NADR-22 §5.1 R1, §5.5 R16 | Medium | 2.4.3 | ✅ DONE |
| **2.4.7** | Implementación/investigación empírica del benchmark DF-04: ZhangShasha vs APTED. Criterio de decisión (respaldado por FASE_4_HANDOFF §5.2 DF-04): divergencia < 1% TED normalizado → APTED queda como experimental sin acción adicional; divergencia ≥ 1% → investigar causa raíz y documentar. | NADR-22 §5.1 R3, DF-04 | Low | 2.4.3, Gate 1 | ✅ DONE |

#### Notas de implementación — Task 2.4.1

> Completada por construcción. ForestDistanceCalculator._del_cost(), _ins_cost() y _sub_cost() manejan VIRTUAL_ROOT_ID con costo 0.0 en todas las operaciones de edición (deletion, insertion, substitution). La raíz virtual no contribuye al costo total de TED. Cumple NADR-22 §5.4 R13-R15.

#### Notas de implementación — Task 2.4.2

> Completada por construcción. HeadingAnchorPartitionStrategy.partition() segmenta el AST en EvaluationWindows usando boundaries derivados de alignment de headings. TreeEditDistanceEvaluator.evaluate() acumula accumulated_distance sobre todas las ventanas mediante Σ TED(window_i). Overflow manejado por WorstCaseOverflowStrategy cuando window.size > max_node_threshold. Cumple NADR-22 §5.5 R16-R18.

#### Notas de implementación — Task 2.4.3

> Implementada. CanonicalEngineConfiguration como @dataclass(frozen=True) con 10 campos: engine_type, cost_weights, partition_strategy, alignment_strategy, normalization_policy, overflow_strategy, matching_policy, nss_hard_fail, nss_warning, warning_threshold. Las estrategias se identifican por module.qualname (unicidad absoluta, no strings libres), evitando typos y colisiones entre módulos. ConfigurationFingerprintCalculator reutiliza compute_sha256 de core.shared.crypto (ADR §5). Campo configuration_fingerprint agregado a RegressionReport y propagado en build_regression_report. build_canonical_engine_configuration() agregado a bootstrap/topology.py. Caller run_regression.py construye config y propaga fingerprint. 12 tests nuevos en test_configuration_fingerprint.py: 2 determinismo + 6 sensibilidad + 2 inmutabilidad + 2 from_components. Cumple NADR-22 §5.6 R19-R21.

#### Notas de implementación — Task 2.4.4

> Completada por construcción. RegressionThresholds con defaults nss_hard_fail=0.80, nss_warning=0.95 e invariante 0.0 <= nss_hard_fail < nss_warning <= 1.0 (falla en __post_init__ si se viola). DoubleProtectionMechanism implementa precedencia CRITICAL sobre NSS: if criticality_verdict.has_critical_loss: return HARD_FAIL (Mecanismo 2 precede a Mecanismo 1). CriticalityVerdictEmitter con warning_threshold configurable (default: 1) y DefaultCriticalityPolicy. Cumple NADR-22 §5.7 R22-R25.

#### Notas de implementación — Task 2.4.5

> Implementada. configuration_fingerprint agregado como campo opcional (str | None = None) en RegressionReport (dataclass frozen). build_regression_report() acepta configuration_fingerprint como parámetro opcional. Caller run_regression.py construye CanonicalEngineConfiguration vía build_canonical_engine_configuration(), calcula fingerprint vía ConfigurationFingerprintCalculator.calculate(), y lo propaga a build_regression_report(). Cumple NADR-22 §5.8 R26-R27.

#### Notas de implementación — Task 2.4.6

> 6 tests de determinismo PASSED: test_identical_trees (ZhangShashaEngine), test_determinism_invariant (StructuralTopologyMetric/APTED), test_determinism_deletion y test_determinism_insertion (CriticalityAwareCostContext), test_deterministic (DoubleProtectionMechanism), test_deterministic (RegressionEvaluationStrategy). Verificación adicional: ConfigurationFingerprintCalculator es determinista (test_same_config_same_hash). El motor canónico es determinista: misma entrada → mismo resultado. Cumple NADR-22 §5.1 R1, §5.5 R16.

#### Notas de implementación — Task 2.4.7

> Benchmark DF-04 ejecutado con run_df04_benchmark.py sobre 6 documentos del corpus canónico sellado. Resultados: divergencia promedio 8.56% (> umbral 1%), divergencia máxima 22.63% (doc_02_double). Desglose por documento: doc_01_single (12.14%), doc_02_double (22.63%), doc_03_math (0.62%), doc_04_table (13.08%), doc_05_graph (2.88%), doc_07_pesaran (0.00%). Cuatro causas raíz identificadas: (1) cost model diferente (APTED penaliza sustituciones diff-type 2× más: 2.0 vs 1.0), (2) normalización diferente (MaxBound vs del×|GT|+ins×|Cand|), (3) fingerprint diferente (H-5.2-6: APTED usa .strip() en ASTFingerprintPolicy, ZhangShasha no), (4) estructura de árbol diferente (APTED reconstruye jerarquía vía parent_node_id, ZhangShasha usa flat forest con virtual root). Patrón 1: APTED consistentemente más severo en 4/6 documentos. Patrón 2: divergencia alta en documentos con estructura compleja (doble columna, tablas). Patrón 3: coincidencia perfecta en casos triviales (doc_07_pesaran 0.00%, score 1.0 en ambos motores) valida correctitud de ambos. Decisión: APTED queda como experimental no-normativo conforme a NADR-22 §5.1 R3. Criterio DF-04 aplicado: divergencia ≥ 1%, causa raíz investigada y documentada. Evidencia forense en reports/df04/df04_benchmark.{json,md}. DF-04 reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED.

#### Hallazgos identificados en esta Wave

No se identificaron nuevos hallazgos en Wave 2.4. DF-04 fue reclasificado de IMPLEMENTATION_REQUIRED a RESOLVED con causa raíz documentada.

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (639 passed, 5 skipped) | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-09-10

---

### 2.3 GATE 3 — Scientific Calibration & Experimental Provenance

**Objective:** Ejecutar la calibración empírica de parámetros bajo un protocolo científico definido, con independencia de datasets y provenance reproducible. Gate 3 ejecuta CAL→VAL→FREEZE, dejando FINAL EVALUATION exclusivamente para Gate 5.
**Execution Mode:** Secuencial
**Rollback Plan:** Revertir parámetros calibrados a valores previos. Restaurar Calibration Provenance Record desde backup.
**Gate Status:** 🟡 IN PROGRESS

#### 2.3.1 Wave 3.1 — Dataset Independence & Partition (NADR-23 §5.1, §5.3)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-10
**Fecha de cierre:** 2026-09-10

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Definición de CALIBRATION / VALIDATION / FINAL EVALUATION como fases secuenciales distintas. | NADR-23 §5.1 R1-R3 | Low | Gate 2 | ✅ DONE |
| **3.1.2** | Partición de datasets por content identity (SHA-256), no filename. Verificar que documentos con el mismo SHA-256 no aparecen en particiones diferentes. | NADR-23 §5.3 R9-R11 | High | 3.1.1 | ✅ DONE |
| **3.1.3** | Verificación de disjunción: Calibration dataset ∩ Final Evaluation dataset = ∅ a nivel de SHA-256. | NADR-23 §5.3 R10 | Medium | 3.1.2 | ✅ DONE |
| **3.1.4** | Evaluar el tamaño y características del corpus y materializar la estrategia de independencia estadística aprobada conforme al protocolo científico. Con <20 identidades, la partición clásica train/validation/holdout no se presume robusta. Registrar la estrategia elegida como evidencia. | NADR-23 §5.3 R12-R13 | Medium | 3.1.2 | ✅ DONE |

#### Notas de implementación — Task 3.1.1

> Definición de fases completada y documentada en FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md §1. Tres conceptos operacionalmente distintos: CALIBRATION (genera y evalúa parámetros candidatos), VALIDATION (determina elegibilidad y selección), FINAL EVALUATION (produce evidencia de baseline certificada). Estado en Gate 3: CALIBRATION NO EJECUTADA (corpus insuficiente N=6 < 20), VALIDATION NO EJECUTADA (no hay candidatos generados), FINAL EVALUATION RESERVADA PARA GATE 5. Regla de secuencialidad R3 cumplida: no hay mezcla de fases. Regla de no-contaminación R2 cumplida: FINAL EVALUATION no se ejecuta en Gate 3. Cumple NADR-23 §5.1 R1-R3.

#### Notas de implementación — Task 3.1.2

> Partición por content identity completada. 6 SHA-256 únicos verificados desde manifest.json (manifest_hash: 0fda7690...). Documentados en FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md §2: doc_01_single (2a1bab7f...), doc_02_double (84891f98...), doc_03_math (21b9283a...), doc_04_table (de56cd04...), doc_05_graph (274ce908...), doc_07_pesaran (166bf271...). Cero duplicados a nivel de SHA-256. Separación basada en cryptographic content identity, no en filename ni document_id (R9). Cumple NADR-23 §5.3 R9-R11.

#### Notas de implementación — Task 3.1.3

> Disjunción verificada. LOCAL_CALIBRATION_SET = ∅ (vacío). La intersección ∅ ∩ FINAL_EVALUATION_SET = ∅ es trivialmente satisfecha a nivel de SHA-256 (R10). No hay documentos que aparezcan simultáneamente en Calibration y Final Evaluation. Cumple NADR-23 §5.3 R10.

#### Notas de implementación — Task 3.1.4

> Estrategia de independencia estadística documentada en FASE_5_WAVE_3_1_DATASET_INDEPENDENCE_RECORD.md §3. Con N=6 documentos (< 20 identidades únicas), NADR-23 §5.3 R12 establece que la partición clásica train/validation/holdout MUST NOT ser presumida estadísticamente robusta. Decisión: LOCAL_CALIBRATION_SET = ∅ (no hay calibración empírica), SANITY_VALIDATION_SET = 6 documentos sellados (valida que defaults no producen veredictos absurdos, NO modifica parámetros), FINAL_EVALUATION_SET = RESERVED_FOR_GATE_5. Regla anti-leakage explícita (NADR-23 R2): SANITY_VALIDATION_SET MUST NOT modificar nss_hard_fail, nss_warning, cost_weights ni warning_threshold. Protocolo futuro documentado para corpus ≥20: curva precision-recall, bootstrap confidence intervals, human verdicts, learning curves (metodología GROBID). Cumple NADR-23 §5.3 R12-R13.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.3-1 | Calibración estadística no ejecutable con 6 documentos. NADR-23 R12 prohíbe presumir robustez estadística con <20 identidades. Defaults actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) son evidence-informed por diseño, NO calibrados empíricamente. Recalibración local requerida cuando corpus alcance ≥20 documentos diversos. Metodología futura: curvas precision-recall + bootstrap confidence intervals + human verdicts PASS/WARNING/HARD_FAIL. | Findings Register §3.3 (ACCEPTED_LIMITATION) |

#### 2.3.2 Wave 3.2 — Calibration Protocol & Execution (NADR-23 §5.2, §5.4, §5.7)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-10
**Fecha de cierre:** 2026-09-10

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Protocolo de calibración: definir experimento ANTES de elegir algoritmo de búsqueda. Definir: variable a calibrar, ground truth observable, función objetivo, espacio de parámetros, restricciones, unidad de evaluación, independencia de datasets, criterio de aceptación. | NADR-23 §5.2 R4-R8 | High | 3.1.4 | ✅ DONE |
| **3.2.2** | Definir y ejecutar el lifecycle CAL→VAL→FREEZE, dejando FINAL EVALUATION exclusivamente para Gate 5. Verificar que las fases no se mezclan. | NADR-23 §5.4 R14-R16 | Medium | 3.2.1 | ✅ DONE |
| **3.2.3** | Condiciones de validez científica: documentar que tuning ad-hoc sin protocolo ≠ calibración científica. Distinguir calibration validity de certification eligibility. | NADR-23 §5.7 R26-R28 | Low | 3.2.2 | ✅ DONE |

#### Notas de implementación — Task 3.2.1

> Protocolo de calibración definido y documentado en FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md §1. Los 8 elementos mínimos conforme a NADR-23 §5.2 R5 están completos: (1) variable a calibrar: nss_hard_fail, nss_warning, cost_weights, warning_threshold; (2) ground truth observable: veredictos humanos PASS/WARNING/HARD_FAIL; (3) función objetivo: maximizar F1-score para detección de HARD_FAIL; (4) espacio de parámetros acotado; (5) restricciones de invariante (0.0 ≤ nss_hard_fail < nss_warning ≤ 1.0); (6) unidad de evaluación: documento individual; (7) independencia por SHA-256 (NADR-23 R10); (8) criterio de aceptación: F1 > 0.85 en validación cruzada. Estado del protocolo: DEFINIDO pero NO EJECUTADO, con aprobación condicional a corpus ≥20 documentos (R7). Algoritmo de búsqueda diferido hasta momento de ejecución (R6). Condiciones de reproducibilidad capturadas (R8). Cumple NADR-23 §5.2 R4-R8.

#### Notas de implementación — Task 3.2.2

> Lifecycle CAL→VAL→FREEZE ejecutado y documentado en FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md §2. Fases: (1) CALIBRATION NO EJECUTADA — corpus insuficiente (N=6 < 20), NADR-23 R12 prohíbe presumir robustez estadística; (2) VALIDATION como sanity validation — ejecutada con run_regression.py sobre 6 documentos sellados, evidencia en reports/sanity_validation/regression_report.{json,md}; (3) PARAMETER FREEZE ejecutado sobre defaults actuales (nss_hard_fail=0.80, nss_warning=0.95, weights 5.0/2.0/1.0, warning_threshold 1), Parameter Identity = b942fc95c0669b06800d6c4c350c9fbb32f92b0ebb75d9fe1059eea9194c8302; (4) FINAL EVALUATION reservada para Gate 5. Resultados de sanity validation: 5/6 documentos HARD_FAIL, corpus NSS 0.6536, 106 Critical FN totales, 1 PASS (doc_07_pesaran, tautológico — ver H-5.3-3). Divergencia masiva consistente con limitaciones de PyMuPDFProvider (H-5.1-9, H-5.1-10), confirma que el problema es estructural, no paramétrico. Regla anti-leakage reforzada: SANITY_VALIDATION_SET MUST NOT modificar parámetros (NADR-23 R2). Regla de no-omisión (R14) cumplida: ninguna fase omitida. Cumple NADR-23 §5.4 R14-R16.

#### Notas de implementación — Task 3.2.3

> Condiciones de validez científica documentadas en FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md §3. (R26a) Calibration validity NO existe — no se ejecutó calibración empírica. (R26b) Parameter eligibility: defaults elegibles como NORMATIVOS, no calibrados. (R26c) Certification eligibility condicionada a Gate 5. (R27) Distinción tuning vs calibración verificable: defaults (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) son parámetros NORMATIVOS definidos por diseño con justificación arquitectónica, NO resultado de tuning ad-hoc. (R28) Clasificación explícita: todos los defaults actuales son NORMATIVOS; cuando se ejecute calibración empírica con corpus ≥20, se registrarán como CALIBRADOS. Hallazgos derivados: H-5.3-2 (divergencia masiva runtime vs GTs, 106 Critical FN) y H-5.3-3 (tautología en doc_07). Cumple NADR-23 §5.7 R26-R28.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.3-2 | Divergencia masiva entre runtime de producción y GTs curados: 5/6 documentos HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536, PASS count 1/6. Consistente con limitaciones de PyMuPDFProvider documentadas en H-5.1-9 (fragmentación de ecuaciones en doble columna) y H-5.1-10 (labels de gráficos como paragraphs). Confirma que la divergencia es estructural (limitación del extractor), no paramétrica. Refuerza decisión de Wave 3.1 de no calibrar con 6 documentos. Evidencia en reports/sanity_validation/regression_report.{json,md}. | Findings Register §3.3 (ACCEPTED_LIMITATION) |
| H-5.3-3 | GT de doc_07_pesaran no editado en curaduría: es salida cruda de build_extraction_pipeline(). NSS=1.0000 es tautología (extractor comparado contra sí mismo), no validación positiva. Documento contiene tablas (Table 1, Table 2) que PyMuPDF no extrae (fuentes Type 3 sin ToUnicode). GT correctamente curado divergiría del runtime. doc_07 marcado como no-informativo para validación. Curaduría real diferida con ampliación de corpus (H-5.2-1 + déficit de 13 docs). Re-sellar en medio de Gate 3 rompería trazabilidad del manifest_hash. | Findings Register §3.3 (ACCEPTED_LIMITATION) |

#### 2.3.3 Wave 3.3 — Provenance & Parameter Freeze (NADR-23 §5.5, §5.6, §5.8)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-11
**Fecha de cierre:** 2026-09-11

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.3.1** | Calibration Provenance Record: 5 campos mínimos (corpus_identity, metric_configuration, parameters, result, timestamp). Referenciar protocolo aprobado y condiciones de ejecución. Distinguir experiment / parameter / result identity. | NADR-23 §5.5 R18-R22 | Medium | 3.2.3 | ✅ DONE |
| **3.3.2** | Parameter freeze: hash criptográfico determinista (parameter identity). Inmutabilidad: nueva configuración = nueva parameter identity = nueva línea de certificación. | NADR-23 §5.6 R23-R25 | Medium | 3.3.1 | ✅ DONE |
| **3.3.3** | Evaluation Provenance Record: independiente del Calibration Provenance Record como registro, pero trazable hacia la calibración que produjo los parámetros congelados. | NADR-23 §5.8 R29-R31 | Medium | 3.3.2 | ✅ DONE |

#### Notas de implementación — Task 3.3.1

> Calibration Provenance Record materializado en `reports/calibration/calibration_provenance_record.json`. Los 5 campos mínimos de R18 están presentes con sus nombres exactos: corpus_identity (0fda7690...), metric_configuration (b942fc95...), parameters (valores normativos: nss_hard_fail=0.80, nss_warning=0.95, cost_weights=[5.0, 2.0, 1.0], warning_threshold=1), result (resumen de sanity validation), timestamp (inyectado, no participa en identidades por R20). Campos adicionales R20: parameter_identity (67841171...), experiment_identity (2c26f93f...), result_identity (f97a3d43...). protocol_identity referencia a FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md@1.0.0. calibration_run=NONE, parameters_origin=NORMATIVE_DESIGN (distinguibilidad R28: parámetros normativos, no calibrados empíricamente). Condiciones de reproducibilidad R19: search_configuration=NONE, seed=NONE (algoritmos deterministas). Artifact provenance (linaje, Wave 1.2) distinguido de calibration-run provenance (R21, R22). Módulo de dominio: `core/benchmark/topology/regression/provenance.py` (CalibrationProvenanceRecord dataclass frozen, 5 campos R18 inmutables). Cumple NADR-23 §5.5 R18-R22.

#### Notas de implementación — Task 3.3.2

> Parameter freeze ejecutado vía MIG-08 con `tools/evaluation/freeze_parameters.py` (entry point CLI como Imperative Shell). Artefacto: `reports/calibration/parameter_freeze.json` con parameter_identity = `6784117165d75005c9db8f4d126f54c11629a1325338e14810a093290ed83bf5`. Separación semántica: parameter_identity es SHA-256 de payload solo-parámetros (`FrozenParameters.canonical_bytes()` con `!r` explícito), distinto de configuration_identity (b942fc95...); un cambio de motor/política sin cambio de parámetros NO genera nueva parameter identity, evitando falsas nuevas líneas de certificación. Invariante de thresholds (0.0 ≤ nss_hard_fail < nss_warning ≤ 1.0) verificada en `FrozenParameters.__post_init__` (fail-fast). Inmutabilidad R25 verificada: tool retorna exit code 2 si artefacto existente con parameter_identity distinta (conflicto). Verificabilidad R24 verificada: `test_repo_freeze_artifact_matches_domain_defaults` recalcula parameter_identity desde defaults del dominio y afirma igualdad con el artefacto del repo (PASSED post-MIG-08). Idempotencia (R33): re-ejecución con freeze idéntico = no-op que no reescribe freeze ni calibration record. Cumple NADR-23 §5.6 R23-R25.

#### Notas de implementación — Task 3.3.3

> Evaluation Provenance Record materializado en `reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json`. Independiente del Calibration Provenance Record (R29), trazable vía `calibration_provenance_reference = experiment_identity` (2c26f93f..., R31). Campos: corpus_identity, configuration_identity, frozen_parameters_identity, result, timestamp, result_identity, evaluation_kind=SANITY_VALIDATION, limitations=[H-5.3-1, H-5.3-2, H-5.3-3]. Nombre acotado por kind: el entry point escribe `evaluation_provenance_record_{kind}.json` (idempotencia por kind, R33). Semántica latest-emission-wins por kind; trazabilidad dura apunta a result_identity (hash del reporte), no al archivo del record. `test_final_evaluation_record_emitted_over_existing_freeze` PASSED: re-ejecución con kind FINAL_EVALUATION sobre freeze existente no cae en no-op, emite `evaluation_provenance_record_FINAL_EVALUATION.json` sin tocar freeze ni calibration record. Cumple NADR-23 §5.8 R29-R31.

#### Hallazgos identificados en esta Wave

No se identificaron nuevos hallazgos en Wave 3.3. Las Tasks 3.3.1-3.3.3 se ejecutaron conforme a protocolo sin desviaciones. Los hallazgos referenciados en el campo `limitations` del Evaluation Provenance Record (H-5.3-1, H-5.3-2, H-5.3-3) pertenecen a Waves 3.1 y 3.2.

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (665 passed, 5 skipped) | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-09-11

---

### 2.4 GATE 4 — Certification Tooling & Execution Safety

**Objective:** Implementar el tooling de certificación con PREFLIGHT, semántica de fallo uniforme, boundary integrity, evidence completeness, y determinismo operacional.
**Execution Mode:** Mixto (W4.1→W4.2→W4.4 secuenciales, W4.3 paralelizable con W4.2)
**Rollback Plan:** Revertir cambios al tooling mediante backup previo. Restaurar entry points a versión previa.
**Gate Status:** ⏳ PENDING

#### 2.4.1 Wave 4.1 — PREFLIGHT & Explicit Configuration (NADR-24 §5.1, §5.2, §5.3)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-11
**Fecha de cierre:** 2026-09-12

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Contrato de ejecución explícito: inputs requeridos, precondiciones normativas, postcondiciones de éxito, condiciones de fallo. | NADR-24 §5.1 R1-R3 | Medium | Gate 3 | ✅ DONE |
| **4.1.2** | PREFLIGHT: verificación de precondiciones antes de RUN. Idempotente. Aborta con EXECUTION_FAILURE ante precondición no satisfecha. | NADR-24 §5.2 R6-R9 | High | 4.1.1 | ✅ DONE |
| **4.1.3** | Configuración explícita: corpus explícito, no fallback silencioso. Remediación de GAP-5.0-03 (rutas hardcoded). | NADR-24 §5.3 R10-R14, GAP-5.0-03 | High | 4.1.2 | ✅ DONE |

#### Notas de implementación — Task 4.1.1

> Contrato de ejecución materializado en `core/benchmark/certification/contract.py`. Tres capas distinguibles (R5): `ExecutionOutcome` (SUCCESS/EXECUTION_FAILURE), `ScientificResult` (ACCEPTED/REJECTED), `CertificationStatus` (CERTIFIED/REJECTED/EXECUTION_FAILURE). `compose_certification_status` con rama explícita para ausencia de componente científico: sin `scientific` no hay rechazo científico sino fallo de ejecución (R4). `CertificationExecutionContract` frozen con 4 campos: corpus_identity, configuration_identity, frozen_parameters_identity, execution_mode (enum `ExecutionMode` con SANITY_VALIDATION / FINAL_EVALUATION, alineado con `evaluation_kind` de Wave 3.3 para trazabilidad R31 sin diccionarios paralelos). 5 tests unitarios en `TestComposeCertificationStatus` (incluyendo test_absent_scientific_result_is_execution_failure). Cumple NADR-24 §5.1 R1-R3 (y prepara R4-R5 para Gate 5).

#### Notas de implementación — Task 4.1.2

> PREFLIGHT implementado con separación Functional Core / Imperative Shell (ENGINEERING_PRINCIPLES §II). `core/benchmark/certification/preflight.py` contiene: (a) `PreflightCondition` enum con 8 valores (a-h de R7); (b) `PreflightViolation` y `PreflightReport` frozen dataclasses; (c) `evaluate_preflight` como función pura con 13 kwargs keyword-only, sin imports de infra ni composition root, determinista e idempotente (R9: misma entrada → mismo reporte). `tools/evaluation/preflight_certification.py` como Imperative Shell: 4 argumentos required (`--corpus-dir`, `--expected-manifest-hash`, `--expected-configuration-identity`, `--expected-parameter-identity`, R10/R11); reutilización estricta (ADR §5): `LoadCorpusManifestUseCase`, `ManifestFingerprintCalculator`, `RegressionAdapter.verify_completeness` (mapeando `IncompleteBaselineError` a violación, F4), `ConfigurationFingerprintCalculator`, lectura de `parameter_freeze.json` y `calibration_provenance_record.json`; `build_canonical_engine_configuration` importado solo en Shell, no en dominio. Condición (h) `NO_PARTITION_LEAKAGE`: check real de intersección `calibration_partition_identities & corpus_sha256_identities` (hoy vacío por H-5.3-1 pero evaluable, no comment muerto — F6). `run_entry(main)` como guard de traducción R19. 14 tests unitarios en `test_certification_preflight.py` (5 de contrato + 9 de preflight incluyendo idempotencia y short-circuit). Happy path contra corpus canónico: exit 0 con `[PREFLIGHT] All 8 conditions satisfied`; failure path: exit 2 con `[PREFLIGHT-corpus_identity_matches]` en stderr. Cumple NADR-24 §5.2 R6-R9.

#### Notas de implementación — Task 4.1.3

> GAP-5.0-03 remediado: 5 entry points con corpus hardcodeado migrados a CLI con `--corpus-dir` required (`bootstrap_corpus.py`, `freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py` con `--pdf-dir` y `--out-dir`, `sanitize_ground_truth_types.py`). Aritmética de cierre sobre 11 entry points auditados: 5 remediados (este task) + 4 ya explícitos (`run_regression`, `run_df04_benchmark`, `run_benchmark`, `freeze_parameters`) + 1 deprecated que hereda (`run_experimental_benchmark`, 0 rutas literales, redirige) + 1 fuera de scope con justificación (`generate_candidates`: CLI configurable, tooling de generación de candidatos no certificante). Cambio rompiente documentado: invocaciones canónicas exigen `--corpus-dir`; MIG-06 histórico. Decisión explícita (C3): `argparse.sys.exit(2)` ante required ausente coincide con categoría (c) de NADR-24 por diseño; `run_entry` no captura `SystemExit` (hereda de `BaseException`, no `Exception`) → el 2 propaga limpio. Evidencia forense dura del riesgo: H-5.4-1 y H-5.4-2 documentan el estado pre-remediación. Cumple NADR-24 §5.3 R10-R14.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| H-5.4-1 | Evidencia forense pre-remediación: `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]` y hash fa8b919c... Falso positivo operacional confirmado (NADR-24 R16, R18, ENGINEERING_PRINCIPLES §IV Cero Fallos Silenciosos). | Findings Register §9 (ACCEPTED_LIMITATION como evidencia forense) |
| H-5.4-2 | Evidencia forense pre-remediación: durante el pre-check de GAP-5.0-03, el run espurio de `generate_pymupdf_candidate.py` mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (`doc_01_single.json`, `doc_02_double.json`, `doc_03_math.json`, `doc_05_graph.json`). Revertidos con `git checkout --`. Evidencia dura del riesgo DF-18/GAP-5.0-03. | Findings Register §9 (ACCEPTED_LIMITATION como evidencia forense) |

#### 2.4.2 Wave 4.2 — Failure Semantics & Exit Contract (NADR-24 §5.4, §5.5)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-12
**Fecha de cierre:** 2026-09-12

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Semántica de fallo uniforme: 3 categorías (certificación válida, certificación rechazada, fallo de ejecución). Cero fallos silenciosos. | NADR-24 §5.4 R15-R19 | Critical | 4.1.3 | ✅ DONE |
| **4.2.2** | Tolerancia a fallos parciales ≠ certificación parcial. Resultado atómico a nivel de baseline. | NADR-24 §5.5 R20-R24 | High | 4.2.1 | ✅ DONE |
| **4.2.3** | Remediación de DF-18: exit codes en freeze_ground_truth.py, generate_golden_draft.py, generate_pymupdf_candidate.py, sanitize_ground_truth_types.py. Ningún camino de error crítico produce exit code de categoría "certificación válida". | NADR-24 §5.4 R15-R16, DF-18 | Critical | 4.2.1 | ✅ DONE |

#### Notas de implementación — Task 4.2.1

> Taxonomía uniforme materializada en `core/shared/exit_codes.py`: `EXIT_OK=0` (categoría a: ejecución completada con resultado válido), `EXIT_CERTIFICATION_REJECTED=1` (categoría b: resultado científico válido pero rechazado, reservado para el runner de certificación de Gate 5), `EXIT_EXECUTION_FAILURE=2` (categoría c: fallo de ejecución/configuración/integridad). Frontera documentada en docstring: el dominio (core/) NUNCA importa este módulo; solo la capa CLI (tools/) lo consume. El dominio señala mediante excepciones tipadas (`IndexedError`, `SealedOracleOverwriteError`, etc.); la traducción a exit codes ocurre exclusivamente en el Imperative Shell. `core/shared/errors.py`: `IndexedError` con código indexable (ej. `[SANITIZE-001]`) que identifica la causa raíz de forma trazable (ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos). `tools/evaluation/entry_guard.py`: `run_entry(main_fn)` como guard de traducción R19 — toda excepción no capturada se traduce a categoría (c) con mensaje indexable `[UNEXPECTED-001]`, sin propagar stack traces crudos como mecanismo primario; `SystemExit` no se captura (propaga limpio por diseño, C3). 3 tests unitarios en `TestRunEntryTranslation`. Cumple NADR-24 §5.4 R15-R19.

#### Notas de implementación — Task 4.2.2

> Tolerancia a fallos parciales ≠ certificación parcial (R22) materializada en `generate_golden_draft.py`. Helper puro `classify_document_error(exc) -> str`: `SealedOracleOverwriteError` → "skip" (esperado, idempotencia R33 — re-ejecución sobre corpus sellado mantiene exit 0); resto → "failure" (unidad obligatoria no procesada). Contadores separados `skips: list[str]` y `failures: list[str]`; códigos indexables `[DRAFT-001]` (manifest ausente), `[DRAFT-002]` (unidad fallida), `[DRAFT-003]` (aggregate failure con lista de failures); warnings `[DRAFT-W01]` (skip sealed oracle) y `[DRAFT-W02]` (aggregate skips). Cierre: `if failures: return EXIT_EXECUTION_FAILURE`; solo `return EXIT_OK` si no hay failures (independientemente de skips). 2 tests unitarios en `TestClassifyDocumentError`. Cumple NADR-24 §5.5 R20-R24.

#### Notas de implementación — Task 4.2.3

> DF-18 remediado en 4 entry points con patrón uniforme: `main(argv) -> int` + `run_entry(main)` en `__main__`. (a) `freeze_ground_truth.py`: `return EXIT_EXECUTION_FAILURE` en todos los caminos de error (`[FREEZE-001]` manifest ausente, `[FREEZE-002]` contract violation, `[FREEZE-003]` catastrophic breakdown, `[FREEZE-004]` baseline incompleta, `[FREEZE-005]` oráculos inválidos); `return EXIT_OK` al final. (b) `generate_golden_draft.py`: integración con Task 4.2.2 (skips/failures separados). (c) `generate_pymupdf_candidate.py`: `[PYMUPDF-001]` para PDFs ausentes; `run_entry(main)` traduce crashes. (d) `sanitize_ground_truth_types.py`: D2 aplicado — `--allow-missing-manifest` override explícito e indexable; sin manifest y sin override → `IndexedError SANITIZE-001` (NADR-24 R26: verificación de sellado imposible, aborta); con override → `logger.warning("[SANITIZE-W01] ...")` y continúa; `[SANITIZE-002]` para directorio inexistente. D3 aplicado en `tools/evaluation/freeze_parameters.py`: `EXIT_CONTRACT_VIOLATION = 1` eliminado; todos los `return EXIT_CONTRACT_VIOLATION` → `return EXIT_EXECUTION_FAILURE` (unificación de categoría c); `[FREEZE-PARAM-001..005]` indexables (timestamp inválido, manifest ausente, reporte ausente, reporte incompleto, conflicto de freeze). Tests actualizados: `test_no_manifest_allows_sanitization` desdoblado en `test_no_manifest_aborts_without_override` y `test_no_manifest_with_override_sanitizes` (evolución normativa NADR-21 → NADR-24); `test_invalid_timestamp_returns_exit_1` → `test_invalid_timestamp_returns_exit_2`; `test_missing_report_returns_exit_1_without_partial_state` → `test_missing_report_returns_exit_2_without_partial_state`. GF-01 documenta la resolución del conflicto NADR-19 vs NADR-24 en run_regression.py (separación de scope: no se toca). Cumple NADR-24 §5.4 R15-R16, DF-18.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| GF-01 | Conflicto normativo real entre NADR-19 §5.5 R22 (`run_regression` taxonomía 0=PASS / 1=WARNING / 2=HARD_FAIL) y NADR-24 §5.4 R15-R17 (2 = fallo de ejecución, rechazo científico es categoría b). Resolución por separación de scope: `run_regression` conserva su taxonomía NADR-19 como compuerta de regresión CI; el runner de certificación de Gate 5 (Task 5.2.1) implementa la taxonomía NADR-24 traduciendo el veredicto científico a categoría (a)/(b) y cualquier crash a (c). `run_regression` NO se toca en Wave 4.2. | Findings Register §11 (Governance Finding) |

#### 2.4.3 Wave 4.3 — Certification Boundary & Evidence (NADR-24 §5.6, §5.7, §5.9) + GAP-5.2-05

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-12
**Fecha de cierre:** 2026-09-13

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.3.1** | Boundary integrity: Sealed inmutable sin excepción. Frontera Scientific Truth / Generated Output / Certification Evidence preservada. | NADR-24 §5.6 R25-R28 | High | 4.2.2 | ✅ DONE |
| **4.3.2** | Verificación formal de GAP-5.2-05: protección de SealedOracle en sanitize_ground_truth_types.py. Verificar estado de sellado antes de cualquier modificación. | NADR-24 §5.6 R25-R26, GAP-5.2-05 | Critical | 4.3.1 | ✅ DONE |
| **4.3.3** | Evidence completeness: 7 elementos mínimos (corpus identity, manifest identity, evaluation configuration identity, frozen parameters identity, evaluation provenance, per-document results, aggregate result). Auditable sin re-ejecución. | NADR-24 §5.7 R29-R31 | Medium | 4.3.1 | ✅ DONE |
| **4.3.4** | POST-RUN VALIDATION: verificar post-condiciones de certificación. | NADR-24 §5.9 R36-R37 | Medium | 4.3.3 | ✅ DONE |

#### Notas de implementación — Task 4.3.1

> Boundary integrity verificada mediante AUDIT forense (5 comandos de introspección) + 10 contract tests en `test_certification_boundary.py`. R25: SealedOracle frozen (model_config frozen=True verificado por test_pydantic_frozen_config), sin mutadores de instancia (test_no_instance_mutators por introspección), asignación bloqueada (test_assignment_raises ValidationError). R26: inventario de escrituras GT acotado a 3 categorías (drafts pre-sealing vía GenerateGoldenDraftUseCase con check de sellado, sellado vía SealGroundTruthUseCase + ManifestLineageSealer, sanitización con verificación de sellado); tooling de certificación (preflight, freeze_parameters, run_regression, run_df04) solo escribe reports/ y artefactos de calibración, nunca GT. R27: los 3 adaptadores de ground_truth_store.py apuntan exclusivamente a base_path/ground_truth; test comportamental confirma que list_artifact_ids ignora candidates/ y reports/, y el reader no resuelve fuera de ground_truth/ (FileNotFoundError). R28: LifecycleTransitionAuthority importada únicamente por core/benchmark/ground_truth/use_cases.py (dominio) y tools/evaluation/freeze_ground_truth.py (entry point de sellado MIG-06 que orquesta el ciclo de vida en memoria invocando la autoridad; O-4.3-3). Test de contrato escanea capas activas y falla ante nuevo importador no permitido. 10 tests unitarios. Cumple NADR-24 §5.6 R25-R28.

#### Notas de implementación — Task 4.3.2

> GAP-5.2-05 verificación formal de la protección implementada en Wave 2.1 (Task 2.1.2). Cadena verificada: (1) sanitize_ground_truth_types.py carga manifest vía _load_sealed_document_ids con override explícito --allow-missing-manifest (sin override → IndexedError SANITIZE-001; con override → warning indexable [SANITIZE-W01]); verifica estado de sellado antes de escribir (sanitize:100-103 raise SealedOracleOverwriteError si doc en sealed_ids). (2) GenerateGoldenDraftUseCase recibe corpus_reader y verifica ground_truth_state == SEALED antes de escribir (use_cases.py:58-63 raise SealedOracleOverwriteError). (3) SealGroundTruthUseCase permanece como autoridad única de sellado (MIG-06). Override --allow-missing-manifest opera fuera de ejecución certificante (R26): sanitize es mecanismo de migración/corrección, no tooling de certificación; sin manifest la verificación de sellado es imposible, por lo que el override es explícito, indexable y requiere acción humana deliberada. Cumple NADR-24 §5.6 R25-R26, GAP-5.2-05.

#### Notas de implementación — Task 4.3.3

> Evidence completeness implementada en `core/benchmark/certification/evidence.py`. `CertificationEvidence` (dataclass frozen) con los 7 elementos mínimos R29: corpus_identity, manifest_identity, configuration_identity, frozen_parameters_identity, evaluation_provenance_reference, per_document_results (tuple de DocumentResultEvidence), aggregate_result; + evaluation_kind y result_identity para trazabilidad R31. Functional Core puro: no lee disco; las identidades llegan computadas por el Shell con calculadores existentes (Reuse Before Invent). `serialize_evidence` determinista (sort_keys, indent fijo, ensure_ascii=False): auditable sin re-ejecución (R31). `compute_corpus_content_identity` fail-fast ante vacío (NADR-20 R1). GF-02 registrado: crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3); corpus_identity = compuesto de contenido (SHA-256 de SHA-256 ordenados, estable entre sellados, NADR-20 §5.1-§5.5), manifest_identity = manifest_hash (cambia al sellar, NADR-20 §5.6 R24/R26); artefactos de Wave 3.3 permanecen válidos (su corpus_identity per R18 = manifest_identity en NADR-24). 12 tests unitarios. Cumple NADR-24 §5.7 R29-R31.

#### Notas de implementación — Task 4.3.4

> POST-RUN VALIDATION implementada en `core/benchmark/certification/post_run.py`. `validate_post_run` (Functional Core puro) verifica 5 checks: (a) PROVENANCE_VERIFIABLE (record disponible + result/experiment identity coinciden), (b) PER_DOCUMENT_PRESENT (biyección veredictos↔manifest), (c) AGGREGATE_PRESENT (corpus_verdict presente), (d) EVIDENCE_ELEMENTS (los 7 elementos R29 completos vía validate_evidence_completeness), (e) IDENTITY_CONSISTENCY (config/params/manifest/corpus coinciden con lo esperado). Violaciones nombradas por elemento R29 (ELEMENT_MANIFEST_IDENTITY, ELEMENT_CORPUS_IDENTITY, etc.) para identificación explícita (R30/R37). `evidence=None` contemplado con violación nombrada. Wiring con disco y con el runner de certificación diferido a Gate 5 Task 5.2.1: no existe RUN de certificación que post-validar hasta ese punto; el Functional Core queda implementado y testeado en esta Wave. 6 tests unitarios con parametrización de 3 campos de identidad. Cumple NADR-24 §5.9 R36-R37.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| O-4.3-3 | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority`. Análisis: es el entry point de sellado (MIG-06, Gate 2) que orquesta el ciclo de vida en memoria invocando la autoridad (audit/validate), diseño congelado en Wave 2.2; R28 prohíbe bypassear la autoridad, no invocarla. El tooling de ejecución certificante sigue teniendo prohibido importarla (verificado por TestCertificationModulesWithoutGtWritePorts). Resolución: extender el allowlist del test con justificación; sin refactor del código congelado de Gate 2 (YAGNI, no tocar código verificado). | Findings Register §9 (Observación, no Governance Finding) |
| GF-02 | Crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3). NADR-23 R18 define corpus_identity como "SHA-256 del manifest"; NADR-24 R29 + NADR-20 exigen separar corpus identity (compuesto de contenido, estable entre sellados) de manifest identity (manifest_hash, cambia al sellar). Resolución: artefactos de Wave 3.3 permanecen válidos (su valor es inequívoco); crosswalk documenta el mapeo entre diccionarios. | Findings Register §11 (Governance Finding) |

#### 2.4.4 Wave 4.4 — Determinism, Idempotency & Recovery (NADR-24 §5.8)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-09-13
**Fecha de cierre:** 2026-09-13

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.4.1** | Determinismo operacional: mismas condiciones de ejecución certificables → mismo resultado. Distinguir de reproducibilidad científica (NADR-23). | NADR-24 §5.8 R32 | Medium | 4.2.2, 4.3.4 | ✅ DONE |
| **4.4.2** | Idempotencia lógica: re-ejecución sin reutilización no determinista de residuos. | NADR-24 §5.8 R33 | Medium | 4.4.1 | ✅ DONE |
| **4.4.3** | Recovery: estado post-fallo determinable (qué unidades evaluadas, qué artefactos en disco, si reutilizables, si re-ejecución reemplaza). No prometer atomicidad física completa si la infraestructura no la garantiza. | NADR-24 §5.8 R34-R35 | Medium | 4.4.2 | ✅ DONE |

#### Notas de implementación — Task 4.4.1 (R32: Determinismo operacional)

> Tooling de certificación es determinista por construcción:
> - Timestamps inyectados externamente (`generated_at: str | None = None` en reportes; flag `--inject-timestamp` en runners). Sin `datetime.now()` ni `time.time()` en formatters de certificación.
> - Serialización con `sort_keys=True` y `ensure_ascii=False` en todos los `json.dumps` de certificación.
> - Hashes computados con `compute_sha256` sobre bytes canónicos (ordenamiento previo donde aplica).
> - `compute_corpus_content_identity` insensible al orden de documentos (sorted previo).
>
> O-4.4-1 (observación sin impacto): `orchestrator.py:196 run_timestamp=time.time()` está en el benchmark de Fase 17, no en el flujo de certificación. Verificar en Gate 5 si se propaga al reporte de certificación; si se propaga, remediar con inyección externa.

#### Notas de implementación — Task 4.4.2 (R33: Idempotencia lógica)

> Cero operaciones de append a archivos en el tooling de certificación. Todos los `.append()` detectados por el AUDIT son sobre listas en memoria (skips/failures, violations, líneas de markdown). Las escrituras a disco usan `write_text`/`write_bytes` en modo overwrite. Un residuo pre-planted es reemplazado íntegramente, no mezclado con el contenido nuevo (verificado por `test_idempotency_replacement.py`).
>
> O-4.4-2 (observación sin impacto): `reporter.py:71 np.random.choice` es el bootstrap del `StatisticalComparator` (análisis estadístico post-benchmark con intervalos de confianza), no forma parte del reporte de regresión de certificación. No-determinista por diseño, confinado al análisis de significancia.

#### Notas de implementación — Task 4.4.3 (R34-R35: Recovery y atomicidad)

> R34: el estado post-fallo es determinable por el contrato de `validate_post_run` (elementos nombrados `ELEMENT_*`). Ausencia de reporte = el run no completó; reporte presente con violaciones = EXECUTION_FAILURE identificando el elemento faltante.
>
> R35: atomicidad física solo donde el dominio la exige (`core/ast/registry.py:88-93` e `infra/fs/corpus_repository.py:44-55` usan `tempfile + os.replace` para oráculos y candidatos). Los reportes de certificación usan `write_text` directo.
>
> **Declaración explícita:** `write_text` NO es atómico a nivel de syscall (es `open + write + close`). Si el proceso muere a mitad de escritura, el archivo puede quedar corrupto (truncado, JSON inválido, bytes basura). No se promete atomicidad física completa del filesystem; la atomicidad es lógica a nivel de certificación (POST-RUN valida completitud antes de cualquier estado CERTIFIED). Si el proceso muere a mitad, el operador debe inspeccionar manualmente el disco y re-ejecutar (recuperación humana, no automática).
>
> O-4.4-3 (gap forense documentado): `freeze_parameters.py:88`, `run_regression.py:201-202`, `run_df04_benchmark.py:257-258` usan `write_text` directo (no atómico a nivel de syscall). Si el proceso muere a mitad de escritura, el reporte puede quedar corrupto. No se migra a escritura atómica porque R34/R35 no la exigen para reportes de certificación y añadiría superficie de cambio sin beneficio normativo (YAGNI); la ventana de corrupción ante crash se cubre con POST-RUN VALIDATION (detecta incompletitud, R36-R37) más re-ejecución manual del operador. Implementar `tempfile + os.replace` no violaría R35; simplemente no es requerido en este scope.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| O-4.4-1 | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en flujo de certificación. Verificar en Gate 5 si se propaga al reporte de certificación. | Findings Register §9 (Observación, sin impacto para Gate 4) |
| O-4.4-2 | `reporter.py:71 np.random.choice` es bootstrap estadístico post-benchmark, no forma parte del reporte de regresión de certificación. No-determinista por diseño, confinado al análisis de significancia. | Findings Register §9 (Observación, sin impacto para Gate 4) |
| O-4.4-3 | `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall). No se migra porque R34/R35 no la exigen para reportes de certificación; YAGNI; ventana de corrupción cubierta por POST-RUN VALIDATION + re-ejecución manual. | Findings Register §9 (Observación, gap documentado sin acción) |

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
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde (720 passed, 5 skipped) | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** ✅ COMPLETED
**Fecha de verificación:** 2026-09-13

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
| **5.1.2** | Verificación de que todas las 168 reglas de NADR-20 a NADR-24 están DONE. | Todas las reglas de NADR-20 a NADR-24 | Medium | 5.1.1 | TODO |

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

- Todas las 168 reglas de NADR-20 a NADR-24 en estado DONE.
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
| 2 | Todas las 168 reglas en estado DONE en §7 | ⏳ |
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
| Gate 1 | — | 56/57 | 17/18 | 0 | 🟡 IN PROGRESS |
| Gate 2 | 2026-09-10 | 43/43 | 17/17 | 0 | ✅ COMPLETED |
| Gate 3 | 2026-09-11 | 31/31 | 10/10 | 3 (H-5.3-1, H-5.3-2, H-5.3-3) | ✅ COMPLETED |
| Gate 4 | 2026-09-13 | 37/37 | 13/13 | 2 (H-5.4-1, H-5.4-2) + 1 O (O-4.3-3) + 3 O (O-4.4-1, O-4.4-2, O-4.4-3) + 2 GF (GF-01, GF-02) | ✅ COMPLETED |
| Gate 5 | — | 0/168 (verification-only) | 0/10 | 0 | ⏳ PENDING |

**Nota normativa de contabilización:** Las reglas listadas como verificación en un Gate (§7, columna Implementation Notes) no se contabilizan en ese Gate. Se contabilizan únicamente en el Gate de implementación primaria. Gate 5 no posee reglas normativas primarias; sus verificaciones no alteran la asignación primaria de reglas. Gate 5 verifica que 57 + 43 + 31 + 37 = 168 reglas están DONE. Las 7 reglas de NADR-21 §5.6/§5.7 verificadas en Gate 2 (Wave 2.2 Tasks 2.2.3, 2.2.4) se contabilizan en Gate 1 (implementación primaria en Wave 1.3 Tasks 1.3.6, 1.3.7).

---

## 4. DEPLOYMENT, MIGRATION & CERTIFICATION OPERATIONS RUNBOOK

Tareas operativas de release, migración y certificación (no desarrollo). Incluye operaciones irreversibles o materializadoras de corpus, sealing, freeze y certification. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Backup/snapshot del corpus candidato antes de cualquier modificación | Local | NADR-20 §5.1 R1 | Backup verificado (SHA-256 de cada documento) | ✅ DONE |
| **MIG-02** | Backup de Ground Truths antes de sellado (precaución operacional pre-sealing, NO mecanismo de rollback post-sealing) | Local | NADR-21 §5.5 R22 | Backup verificado en tests/corpus_backup_pre_sealing/ | ✅ DONE |
| **MIG-03** | Copiar 7 documentos del corpus canónico a `tests/corpus/canonical/pdf/` (déficit de 13 pendiente) | Local | NADR-20 §5.1 R1-R2 | SHA-256 de cada documento verificado, PyMuPDF OK | ✅ DONE (parcial) |
| **MIG-04** | Migración de manifest legacy (DF-19) a formato vigente (6D) | Local | NADR-21 §5.8 R38, NADR-20 §5.6 R23 | Manifest migrado y hash verificado (62f0df16 → 39cc80bd tras re-extracción doc_07) | ✅ DONE |
| **MIG-05** | Canonicalización de node_ids en Ground Truths | Local | NADR-21 §5.2 R8-R12 | 401/401 node_ids canonicalizados, lineage registrado | ✅ DONE |
| **MIG-06** | Ejecutar `freeze_ground_truth.py` contra el corpus canónico (Zero Partial Sealing). Operación irreversible: después del sealing, no existe rollback mutativo. | Local | NADR-21 §5.5 R22-R27 | Biyección verificada (N_PDF = N_GT = 6), oráculos sellados, manifest_hash 0fda7690 | ✅ DONE |
| **MIG-07** | Congelación de configuración canónica del motor | Local | NADR-22 §5.6 R19-R21 | ConfigurationFingerprintCalculator implementado, configuration_fingerprint propagado en RegressionReport y run_regression.py, 12 tests de determinismo y sensibilidad PASSED | ✅ DONE |
| **MIG-08** | Congelación de parámetros normativos (parameter freeze) + emisión de Calibration Provenance Record + Evaluation Provenance Record (SANITY_VALIDATION) | Local | NADR-23 §5.5 R18-R22, §5.6 R23-R25, §5.8 R29-R31 | Artefactos en `reports/calibration/`: `parameter_freeze.json` (parameter_identity 67841171...), `calibration_provenance_record.json`, `evaluation_provenance_record_SANITY_VALIDATION.json`. Parameter identity recalculable desde defaults del dominio (`test_repo_freeze_artifact_matches_domain_defaults` PASSED). Entry point: `tools/evaluation/freeze_parameters.py` con semántica de salida 0/1/2 | ✅ DONE |

---

## 5. GLOBAL DoD (Definition of Done)

La Fase 5 (Baseline Certification) se considera oficialmente completada cuando:

```text
{All 168 rules in FROZEN NADRs 20-24} − {Rules with DONE status in §7} = ∅
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
- [x] Calibración Empírica: Defaults normativos congelados bajo protocolo científico documentado con identidades criptográficas verificables (MIG-08, parameter_identity 67841171...). Recalibración empírica diferida a corpus ≥20 (H-5.3-1).
- [ ] Certification Evidence: Completa y auditable (7 elementos mínimos).
- [ ] Verificación Estática y Pruebas Limpias: Pyright 0 errors, 0 warnings; suite de tests en verde.

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 6. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§7), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 17 | 56 | 0 | 1 (R20) | 🟡 IN PROGRESS |
| Gate 2 | 17 | 43 | 0 | 0 | ✅ COMPLETED |
| Gate 3 | 10 | 31 | 0 | 0 | ✅ COMPLETED |
| Gate 4 | 13 | 37 | 0 | 0 | ✅ COMPLETED |
| Gate 5 | 0 | 0 | 0 | 168 (verification-only) | ⏳ PENDING |
| **TOTAL** | **57** | **167** | **0** | **1** | 🟡 IN PROGRESS |

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
| NADR-20 §5.1 R1-R4 | DONE | Wave 1.1 / Task 1.1.2, 1.1.3 | 7 PDFs copiados, integridad PyMuPDF OK, SHA-256 únicos |
| NADR-20 §5.2 R5-R9 | DONE | Wave 1.1 / Task 1.1.4 | G1/G2 consolidados, idempotencia verificada |
| NADR-20 §5.5 R19-R21 | DONE (parcial) | Wave 1.1 / Task 1.1.1, 1.1.5 | 7 identidades (déficit de 13 documentado). R20 PENDING hasta ≥20 docs |
| NADR-20 §5.3 R10-R13 | DONE | Wave 1.2 / Task 1.2.1 | Traits clasificados contra catálogo vigente (H-5.1-5 RESOLVED) |
| NADR-20 §5.4 R14-R18 | DONE | Wave 1.2 / Task 1.2.2 | Cualificación formal registrada (QUALIFICATION_RECORD.md) |
| NADR-20 §5.6 R22-R26 | DONE | Wave 1.2 / Task 1.2.3 | Seed manifest 6D generado y verificado (hash 62f0df16) |
| NADR-20 §5.7 R27-R28 | DONE | Wave 1.2 / Task 1.2.4 | Provenance registrado (PROVENANCE.md) |
| NADR-21 §5.8 R38 | DONE | Wave 1.3 / Task 1.3.1 | DF-19 verificado: manifest 6D completo, H-5.1-8 CLOSED (NAR) |
| NADR-21 §5.2 R8-R12 | DONE | Wave 1.3 / Task 1.3.2 | 401/401 node_ids canonicalizados, lineage registrado |
| NADR-21 §5.1 R1-R3 | DONE | Wave 1.3 / Task 1.3.3 | 5/5 GTs hidratados como GroundTruthDraft |
| NADR-21 §5.3 R13-R16 | DONE | Wave 1.3 / Task 1.3.4 | OracleValidityContract pasado, cero orfanos R16 |
| NADR-21 §5.1 R4-R7 | DONE | Wave 1.3 / Task 1.3.5 | 5/5 GTs elegibles (R4-R7 verificados) |
| NADR-21 §5.6 R28-R31 | DONE | Wave 1.3 / Task 1.3.6 | 5 identidades semánticas únicas, sin colisiones |
| NADR-21 §5.7 R32-R34 | DONE | Wave 1.3 / Task 1.3.7 | Hash de baseline verificado determinista (62f0df16) |
| NADR-21 §5.8 R35-R37 | DONE | Wave 1.3 / Task 1.3.8 | Re-extracción doc_07 (recorte 41→3 págs), GT 21 nodos, H-5.1-3 RESOLVED |
| NADR-21 §5.1 R5 | DONE | Wave 1.3 / Task 1.3.9 | Curaduría manual completada, Curation Report generado (6 GTs curados) |

### 7.2 Gate 2 — Rules Audit Board (NADR-21 §5.4-§5.5/§5.9: 16 reglas + NADR-22: 27 reglas = 43 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-21 §5.4 R17-R21 | DONE | Wave 2.1 / Task 2.1.1 | 19 tests lifecycle + 23 tests modelos PASSED |
| NADR-21 §5.9 R39-R43 | DONE | Wave 2.1 / Task 2.1.2 | sanitize_ground_truth_types.py protegido, SealedOracleOverwriteError fail-hard |
| NADR-21 §5.5 R22-R27 | DONE | Wave 2.2 / Task 2.2.1, 2.2.2, 2.2.5 | 6/6 sellados, biyección verificada, atomicidad 7/7 tests |
| NADR-21 §5.6 R28-R31 | DONE | Wave 2.2 / Task 2.2.3 | Verificación (implementación primaria en Wave 1.3 Task 1.3.6). 6/6 oracle_hash coinciden post-sealing |
| NADR-21 §5.7 R32-R34 | DONE | Wave 2.2 / Task 2.2.4 | Verificación (implementación primaria en Wave 1.3 Task 1.3.7). Hash encadenado 0fda7690 verificado |
| NADR-22 §5.1 R1-R4 | DONE | Wave 2.3 / Task 2.3.1 | ZhangShashaEngine en composition root; APTED aislado en tools/ como experimental |
| NADR-22 §5.2 R5-R9 | DONE | Wave 2.3 / Task 2.3.2 | Pesos 5.0/2.0/1.0 verificados; caller explícito en run_regression.py |
| NADR-22 §5.3 R10-R12 | DONE | Wave 2.3 / Task 2.3.3 | Dominio sin .strip(); divergencia ASTFingerprintPolicy registrada (H-5.2-6) |
| NADR-22 §5.4 R13-R15 | DONE | Wave 2.4 / Task 2.4.1 | ForestDistanceCalculator: VIRTUAL_ROOT_ID con costo 0.0 |
| NADR-22 §5.5 R16-R18 | DONE | Wave 2.4 / Task 2.4.2 | HeadingAnchorPartitionStrategy + Σ TED(windows) en TreeEditDistanceEvaluator |
| NADR-22 §5.6 R19-R21 | DONE | Wave 2.4 / Task 2.4.3 | ConfigurationFingerprintCalculator con module.qualname; configuration_fingerprint en RegressionReport |
| NADR-22 §5.7 R22-R25 | DONE | Wave 2.4 / Task 2.4.4 | RegressionThresholds 0.80/0.95, DoubleProtectionMechanism con precedencia CRITICAL |
| NADR-22 §5.8 R26-R27 | DONE | Wave 2.4 / Task 2.4.5 | configuration_fingerprint propagado en build_regression_report y run_regression.py |

### 7.3 Gate 3 — Rules Audit Board (NADR-23: 31 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-23 §5.1 R1-R3 | DONE | Wave 3.1 / Task 3.1.1 | CAL/VAL/FINAL definidas como fases secuenciales distintas |
| NADR-23 §5.3 R9-R13 | DONE | Wave 3.1 / Task 3.1.2, 3.1.3, 3.1.4 | Partición por SHA-256, disjunción verificada, estrategia documentada (N=6 < 20) |
| NADR-23 §5.2 R4-R8 | DONE | Wave 3.2 / Task 3.2.1 | Protocolo de calibración definido (8 elementos, aprobación condicional a corpus ≥20) |
| NADR-23 §5.4 R14-R16 | DONE | Wave 3.2 / Task 3.2.2 | Lifecycle CAL→VAL→FREEZE ejecutado; CAL=∅, VAL=sanity (5/6 HARD_FAIL), FREEZE=defaults (fingerprint b942fc95...) |
| NADR-23 §5.7 R26-R28 | DONE | Wave 3.2 / Task 3.2.3 | Defaults clasificados como NORMATIVOS; H-5.3-2 y H-5.3-3 documentados |
| NADR-23 §5.4 R14-R17 | DONE | Wave 3.2 / Task 3.2.2 | Lifecycle CAL→VAL→FREEZE ejecutado; R17 contabilizado aquí por implementación primaria (diseño del lifecycle que reserva FINAL en Gate 5). Ejecución/verificación en Gate 5 Task 5.2.1 |
| NADR-23 §5.7 R26-R28 | DONE | Wave 3.2 / Task 3.2.3 | Defaults clasificados como NORMATIVOS; H-5.3-2 y H-5.3-3 documentados |
| NADR-23 §5.5 R18-R22 | DONE | Wave 3.3 / Task 3.3.1 | Calibration Provenance Record con 5 campos R18; run NONE; origen NORMATIVE_DESIGN |
| NADR-23 §5.6 R23-R25 | DONE | Wave 3.3 / Task 3.3.2 | Parameter freeze materializado (MIG-08); parameter_identity 67841171...; enforcement vía test sobre artefacto real |
| NADR-23 §5.8 R29-R31 | DONE | Wave 3.3 / Task 3.3.3 | Evaluation Provenance Record independiente, trazable vía experiment_identity; kind-aware; limitations H-5.3-1/2/3 |

### 7.4 Gate 4 — Rules Audit Board (NADR-24: 37 reglas)

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-24 §5.1 R1-R3 | DONE | Wave 4.1 / Task 4.1.1 | `CertificationExecutionContract` + `compose_certification_status` en `core/benchmark/certification/contract.py` |
| NADR-24 §5.2 R6-R9 | DONE | Wave 4.1 / Task 4.1.2 | `evaluate_preflight` (Functional Core puro, 8 precondiciones) + CLI `preflight_certification.py` (Imperative Shell); 14 tests |
| NADR-24 §5.3 R10-R14 | DONE | Wave 4.1 / Task 4.1.3 | 5 entry points migrados a `--corpus-dir` required (GAP-5.0-03) |
| NADR-24 §5.4 R15-R19 | DONE | Wave 4.2 / Task 4.2.1, 4.2.3 | `core/shared/exit_codes.py` + `entry_guard.py` + remediación DF-18 en 4 entry points |
| NADR-24 §5.5 R20-R24 | DONE | Wave 4.2 / Task 4.2.2 | `classify_document_error` + skips/failures separados en `generate_golden_draft.py` |
| NADR-24 §5.6 R25-R28 | DONE | Wave 4.3 / Task 4.3.1 | Boundary integrity verificada: SealedOracle frozen, autoridad acotada, frontera R27 preservada |
| NADR-24 §5.6 R25-R26 | DONE | Wave 4.3 / Task 4.3.2 | GAP-5.2-05 verificación formal: cadena sanitize/use cases/override D2 |
| NADR-24 §5.7 R29-R31 | DONE | Wave 4.3 / Task 4.3.3 | CertificationEvidence con 7 elementos R29 + serialize_evidence determinista |
| NADR-24 §5.9 R36-R37 | DONE | Wave 4.3 / Task 4.3.4 | validate_post_run con 5 checks y violaciones nombradas |
| NADR-24 §5.8 R32 | DONE | Wave 4.4 / Task 4.4.1 | Determinismo operacional verificado: timestamps inyectados, sort_keys=True, hashes canónicos |
| NADR-24 §5.8 R33 | DONE | Wave 4.4 / Task 4.4.2 | Idempotencia lógica verificada: cero append a archivos, escrituras overwrite |
| NADR-24 §5.8 R34-R35 | DONE | Wave 4.4 / Task 4.4.3 | Recovery determinable (validate_post_run); atomicidad física solo donde el dominio la exige |

### 7.5 Gate 5 — Rules Audit Board (Verificación de las 168 reglas)

**Nota normativa:** Gate 5 no posee reglas normativas primarias. Verifica que las 168 reglas asignadas a Gates 1-4 están DONE.

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
| DF-04 | Dualidad ZhangShasha/APTED — benchmark comparativo ejecutado. Divergencia promedio 8.56% (> umbral 1%), máxima 22.63%. Cuatro causas raíz documentadas (cost model, normalización, fingerprint H-5.2-6, estructura de árbol). APTED queda como experimental no-normativo (NADR-22 §5.1 R3). | Gate 2 W2.4 Task 2.4.7 (investigación), Gate 5 W5.3 Task 5.3.3 (cierre administrativo) | RESOLVED |
| DF-18 | Semántica de fallo heterogénea en 4 entry points | Gate 4 W4.2 Task 4.2.3 | Carry-forward de HITO 5.2 |
| DF-19 | Manifest en formato legacy (4 dimensiones) | Gate 1 W1.2 Task 1.2.3 (contrato), Gate 1 W1.3 Task 1.3.1 (ejecución de migración) | Carry-forward de HITO 5.1 |
| GAP-5.0-03 | Configuración implícita del corpus (rutas hardcoded) | Gate 4 W4.1 Task 4.1.3 | Carry-forward de HITO 5.0 |
| GAP-5.2-05 | Certification Boundary Integrity violation (sanitize_ground_truth_types.py) | Gate 2 W2.1 Task 2.1.2, Gate 4 W4.3 Task 4.3.2 | Carry-forward de HITO 5.2 |

**Hallazgos identificados durante Wave 1.1:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.1-1 | Discrepancia 7 vs 6 identidades. pesaran1999.pdf encontrado en datasets/raw/ e incluido como doc_07_pesaran.pdf. | Gate 1 W1.1 T1.1.1 | RESOLVED |
| H-5.1-2 | Archivo temporal huérfano tmptu237h6p (35,557 bytes) en calibration_v1/candidates/pymupdf/. Eliminado en Task 1.3.1. | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.1 | RESOLVED |
| H-5.1-3 | AST de pesaran1999.pdf en formato legacy (type en lugar de node_type, sin strategy). Resuelto por re-extracción en Task 1.3.8. | Gate 1 W1.1 T1.1.1 → W1.3 T1.3.8 | RESOLVED |
| H-5.1-4 | doc_03_math y doc_06_johnstone son OCR_DEPENDENCY (no NATIVE_PDF). Inspección visual. | Gate 1 W1.1 T1.1.1 → Task 1.2.1 | PENDING_REVIEW |

**Hallazgos identificados durante Wave 1.2:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.1-5 | Discrepancia de nombres de traits entre clasificación preliminar y catálogo vigente. Nombres inexistentes (DENSE_TYPOGRAPHY, MIXED_CONTENT) y nombres diferentes (HEAVY_MATHEMATICS→heavy_math, COMPLEX_TABLES→nested_tables, OCR_DEPENDENCY→scanned_noise). Reclasificación completada contra catálogo vigente. | Gate 1 W1.2 T1.2.1 | RESOLVED |

**Hallazgos identificados durante Wave 1.3:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.1-7 | Todos los parent_node_id son None en los 5 GTs. Consistente con Flat Design (ENGINEERING_PRINCIPLES §II). Verificado en curaduría. | Gate 1 W1.3 T1.3.4 | RESOLVED |
| H-5.1-8 | ManifestFingerprintCalculator.compute_hash() incluye page_count en el payload (verificado en source code). Hash anterior coincidió por valor por defecto de Pydantic. | Gate 1 W1.3 T1.3.1 | CLOSED (NAR) |
| H-5.1-9 | doc_02_double: 52 nodos display_equation con fragmentos garbled (operadores/variables aislados). PyMuPDF no agrupa ecuaciones en doble columna. | Gate 1 W1.3 T1.3.9 | ACCEPTED_LIMITATION |
| H-5.1-10 | doc_05_graph: 56 labels de ejes de gráficos como paragraphs. Estructura de gráficos no capturada por PyMuPDF. | Gate 1 W1.3 T1.3.9 | ACCEPTED_LIMITATION |
| H-5.1-11 | Propuesta de patrón Detect & Placeholder: PyMuPDF degrada tablas/figuras/ecuaciones al extraerlas como texto plano. Se propone detectar presencia y dejar placeholder. Fuera del scope de Fase 17-BIS (ADR §4). | Gate 1 W1.3 T1.3.9 | RECLASSIFIED_FUTURE_PHASE |

**Hallazgos identificados durante Wave 2.1:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.2-1 | doc_06_johnstone excluido del manifest canónico para restaurar biyección N_PDF=N_GT=6 (Zero Partial Sealing). Requiere re-incorporación con pipeline OCR. Manifest hash recalculado: 39cc80bd → fae41bb5. PDF físico preservado en canonical/pdf/ como evidencia (quarantine). | Gate 2 W2.1 T2.1.1 (pre-requisito biyección) | IMPLEMENTATION_REQUIRED |
| H-5.2-2 | GroundTruthLifecycleState muestra 3 estados en inspección runtime pero tests esperan 4. Verificación: enum SÍ tiene 4 estados (DRAFT, AUDITED, VALIDATED, SEALED). Diseño type-state: SEALED se representa como tipo SealedOracle, no como estado del enum en runtime. Tests test_four_states y test_exactly_four_states PASSED. | Gate 2 W2.1 T2.1.1 | CLOSED (NAR) |

**Hallazgos identificados durante Wave 2.2:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.2-3 | canonicalization_lineage.json en ground_truth/ contaminaba BaselineCompletenessVerifier como oráculo huérfano. Movido a canonical/ raíz (separación de concerns: ground_truth/ solo contiene GTs). | Gate 2 W2.2 T2.2.1 | RESOLVED |
| H-5.2-4 | freeze_ground_truth.py apuntaba a tests/corpus/benchmark_v1/ en lugar de tests/corpus/canonical/. Path corregido. | Gate 2 W2.2 T2.2.1 | RESOLVED |
| H-5.2-5 | Log duplicado en freeze_ground_truth.py (línea logger.info repetida). Eliminado. | Gate 2 W2.2 T2.2.1 | CLOSED (NAR) |

**Hallazgos identificados durante Wave 2.3:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.2-6 | ASTFingerprintPolicy.semantic_fingerprint() e identity_fingerprint() aplican .strip(), violando NADR-22 §5.3 R10-R12. Divergencia confinada al tooling experimental (tools/evaluation/topology/). La ruta canónica de regresión no usa fingerprint ni .strip(). | Gate 2 W2.3 T2.3.3 | ACCEPTED_LIMITATION |

**Hallazgos identificados durante Wave 3.1:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.3-1 | Calibración estadística no ejecutable con 6 documentos. NADR-23 R12 prohíbe presumir robustez estadística con <20 identidades. Defaults actuales (NSS 0.80/0.95, weights 5.0/2.0/1.0, warning_threshold 1) son evidence-informed por diseño, NO calibrados empíricamente. Recalibración local requerida cuando corpus alcance ≥20 documentos diversos. Metodología futura: curvas precision-recall + bootstrap confidence intervals + human verdicts PASS/WARNING/HARD_FAIL. | Gate 3 W3.1 T3.1.4 | ACCEPTED_LIMITATION |

**Hallazgos identificados durante Wave 3.2:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.3-2 | Divergencia masiva entre runtime de producción y GTs curados: 5/6 documentos HARD_FAIL, 106 Critical FN totales, corpus NSS 0.6536, PASS count 1/6. Consistente con limitaciones de PyMuPDFProvider (H-5.1-9, H-5.1-10). Divergencia es estructural (extractor), no paramétrica. Refuerza decisión de Wave 3.1 de no calibrar con N=6. Evidencia en reports/sanity_validation/regression_report.{json,md}. | Gate 3 W3.2 T3.2.2 | ACCEPTED_LIMITATION |
| H-5.3-3 | GT de doc_07_pesaran no editado en curaduría: es salida cruda de build_extraction_pipeline(). NSS=1.0000 es tautología (extractor contra sí mismo), no validación positiva. Documento contiene tablas que PyMuPDF no extrae (fuentes Type 3). Curaduría real diferida con ampliación de corpus (H-5.2-1). | Gate 3 W3.2 T3.2.3 | ACCEPTED_LIMITATION |

**Hallazgos identificados durante Wave 4.1:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| H-5.4-1 | Evidencia forense pre-remediación: `bootstrap_corpus.py` sin argumentos indexó 0 documentos y retornó exit 0 con mensaje `[SUCCESS]`. Falso positivo operacional confirmado (NADR-24 R16, R18). Motivó la remediación de Task 4.1.3 + 4.2.3. | Gate 4 W4.1 T4.1.3 | ACCEPTED_LIMITATION (evidencia forense) |
| H-5.4-2 | Evidencia forense pre-remediación: run espurio de `generate_pymupdf_candidate.py` mutó 4 artefactos trackeados en `calibration_v1/candidates/pymupdf/` (revertidos con `git checkout`). Motivó la remediación GAP-5.0-03 + DF-18. | Gate 4 W4.1 T4.1.3 | ACCEPTED_LIMITATION (evidencia forense) |

**Governance Findings identificados durante Wave 4.2:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| GF-01 | Conflicto normativo NADR-19 §5.5 R22 (`run_regression` taxonomía 0/1/2 PASS/WARNING/HARD_FAIL) vs NADR-24 §5.4 R15-R17 (2 = fallo de ejecución). Resolución por separación de scope: `run_regression` conserva taxonomía NADR-19 como compuerta CI; runner de certificación de Gate 5 (Task 5.2.1) implementa taxonomía NADR-24 traduciendo veredicto científico. `run_regression` NO se toca en Wave 4.2. | Gate 4 W4.2 T4.2.3 | Documentado (no resuelto por diseño) |

**Hallazgos identificados durante Wave 4.3:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| O-4.3-3 | `freeze_ground_truth.py` importa `LifecycleTransitionAuthority` (entry point de sellado MIG-06, no tooling de certificación). R28 prohíbe bypassear la autoridad, no invocarla. Allowlist extendido con justificación; sin refactor de código congelado de Gate 2. | Gate 4 W4.3 T4.3.1 | Observación (no Governance Finding) |

**Governance Findings identificados durante Wave 4.3:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| GF-02 | Crosswalk normativo de identidades entre diccionarios NADR-23 (Wave 3.3) y NADR-24 (Wave 4.3). NADR-23 R18 define corpus_identity como "SHA-256 del manifest"; NADR-24 R29 + NADR-20 exigen separar corpus identity (compuesto de contenido, estable entre sellados) de manifest identity (manifest_hash, cambia al sellar). Resolución: artefactos de Wave 3.3 permanecen válidos; crosswalk documenta el mapeo entre diccionarios. | Gate 4 W4.3 T4.3.3 | Documentado (interpretación normativa) |

**Hallazgos identificados durante Wave 4.4:**

| ID | Descripción | Ubicación en el plan | Estado |
|----|-------------|---------------------|--------|
| O-4.4-1 | `orchestrator.py:196 run_timestamp=time.time()` en benchmark de Fase 17, no en flujo de certificación. Verificar en Gate 5 si se propaga al reporte de certificación. | Gate 4 W4.4 T4.4.1 | Observación (sin impacto para Gate 4) |
| O-4.4-2 | `reporter.py:71 np.random.choice` es bootstrap estadístico post-benchmark, no forma parte del reporte de regresión de certificación. No-determinista por diseño, confinado al análisis de significancia. | Gate 4 W4.4 T4.4.2 | Observación (sin impacto para Gate 4) |
| O-4.4-3 | `freeze_parameters.py`, `run_regression.py`, `run_df04_benchmark.py` usan `write_text` directo (no atómico a nivel de syscall). No se migra porque R34/R35 no la exigen para reportes de certificación; YAGNI; ventana de corrupción cubierta por POST-RUN VALIDATION + re-ejecución manual. | Gate 4 W4.4 T4.4.3 | Observación (gap documentado sin acción) |

**Carry-forwards from Phase 4 (no bloquean Fase 5):**
- DF-01: Tests tautológicos → Fase 6
- DF-02: Verificación ci.yml/pyproject.toml → Fase 6
- DF-03: Deuda LayoutBlockDraft → Gate futuro

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0.

* **ADR_F17_BIS_MASTER** define la visión arquitectónica de la Fase 17-BIS.
* **ADR_F17_BIS_05** define la decisión arquitectónica de la Fase 5.
* **NADRs 20-24** definen las reglas normativas obligatorias (168 reglas).
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
- Recalibración empírica de thresholds con corpus ≥20 documentos cuando el usuario adquiera los 13+ documentos del déficit (H-5.3-1). Metodología: curvas precision-recall + bootstrap CI + human verdicts + learning curves.
- Curaduría real de doc_07_pesaran cuando se amplíe el corpus (H-5.3-3): transcribir tablas visibles como nodos table en el GT.
- Emisión de Evaluation Provenance Record FINAL_EVALUATION en Gate 5 Task 5.2.2: el entry point `tools/evaluation/freeze_parameters.py` ya soporta `--evaluation-kind FINAL_EVALUATION` con idempotencia sobre el freeze existente (R33). El artefacto resultante será `reports/calibration/evaluation_provenance_record_FINAL_EVALUATION.json`.
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

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN (168 reglas), no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.