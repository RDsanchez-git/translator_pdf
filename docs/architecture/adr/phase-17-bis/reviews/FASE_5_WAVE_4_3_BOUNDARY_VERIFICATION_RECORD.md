# FASE 5 — WAVE 4.3 FASE A: BOUNDARY VERIFICATION RECORD

**Documento:** docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_4_3_BOUNDARY_VERIFICATION_RECORD.md
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-12
**Gate:** Gate 4 — Certification Tooling & Execution Safety
**Wave:** 4.3 Fase A — Certification Boundary (Tasks 4.3.1, 4.3.2)
**Derivado de:** NADR-F17BIS-24 §5.6 R25-R28 | GAP-5.2-05 | PHASE_17BIS_FASE5_EXECUTION_PLAN v1.3.3

---

## 1. ALCANCE

Verificación de las invariantes de frontera de certificación sobre el estado
actual del repositorio (post Wave 4.2):

- R25: Ground Truths sellados inmutables sin excepción; sin autorización que permita mutar un Sealed GT.
- R26: todo mecanismo que modifica GTs verifica estado de sellado antes de modificar.
- R27: ningún artefacto generado (candidates/, reports/) adquiere autoridad de GT.
- R28: transiciones de estado gobernadas exclusivamente por LifecycleTransitionAuthority.
- GAP-5.2-05: verificación formal de la protección implementada en Wave 2.1 (Task 2.1.2),
  incluyendo el path de override D2 de Wave 4.2.

## 2. EVIDENCIA POR REGLA

| Regla | Evidencia | Veredicto |
|---|---|---|
| R25 | Superficie pública de SealedOracle auditada por introspección: sin mutadores de instancia (update_forward_refs es classmethod de schema, no mutación). Modelo Pydantic frozen (model_config frozen=True verificado); inmutabilidad profunda cubierta por test_oracle_is_immutable (Wave 2) y test_assignment_raises (contract test, ValidationError). | CUMPLE |
| R26 | Inventario de escrituras GT: (1) drafts pre-sealing vía GenerateGoldenDraftUseCase con check de sellado (use_cases.py:58-63 raise SealedOracleOverwriteError); (2) sellado vía SealGroundTruthUseCase + ManifestLineageSealer (autoridad única); (3) sanitización con verificación de sellado previa (sanitize:100-103) y override explícito --allow-missing-manifest (IndexedError SANITIZE-001 sin override). El tooling de certificación (freeze_parameters, run_regression, run_df04, preflight_certification) solo escribe reports/ y artefactos de calibración, nunca GT. | CUMPLE |
| R27 | Los 3 adaptadores de infra/fs/ground_truth_store.py apuntan exclusivamente a base_path/ground_truth. Scan de core/ e infra/fs/: ninguna referencia a candidates/ o reports/ como fuente de GT. Test comportamental: list_artifact_ids ignora candidates/ y reports/; el reader no resuelve artefactos fuera de ground_truth/ (FileNotFoundError). | CUMPLE |
| R28 | LifecycleTransitionAuthority (audit/validate/seal/rollback_to_draft/rollback_to_audited, todas retornan instancia nueva; seal retorna SealedOracle) importada en capas activas únicamente por core/benchmark/ground_truth/use_cases.py y por tools/evaluation/freeze_ground_truth.py (entry point de sellado MIG-06 que orquesta el ciclo de vida en memoria invocando la autoridad; ver O-4.3-3). R28 prohíbe ejecutar transiciones fuera del gobierno de la autoridad (bypass), no invocarla; el tooling de ejecución certificante tiene prohibido importarla (verificado por TestCertificationModulesWithoutGtWritePorts). El test de contrato escanea capas activas y falla ante un nuevo importador no permitido. | CUMPLE |

## 3. OBSERVACIONES

- **O-4.3-1:** tools/benchmark_archive/run_calibration_v1.py importa LifecycleTransitionAuthority,
  SealGroundTruthUseCase y LocalFileSystemGroundTruthDraftWriter. Clasificado como tooling
  legacy de archivo: no forma parte de la ruta de certificación ni del pipeline activo,
  y no se ejecuta en CI de certificación. Se excluye del scan R28 con justificación
  (YAGNI sobre código de archivo); la exclusión queda congelada en este record y en el
  test de contrato (ACTIVE_SCAN_ROOTS no incluye tools/benchmark_archive).
- **O-4.3-2:** SealedOracle es modelo Pydantic frozen (no dataclass). La inmutabilidad se
  verifica por config frozen + tests, no por dataclass(frozen=True). Sin impacto normativo.
- **O-4.3-3:** El test de contrato R28 detectó que tools/evaluation/freeze_ground_truth.py importa
  LifecycleTransitionAuthority. Análisis: es el entry point de sellado (MIG-06, Gate 2) que
  orquesta el ciclo de vida en memoria invocando la autoridad (audit/validate), diseño
  congelado en Wave 2.2; R28 prohíbe bypassear la autoridad, no invocarla. El tooling de
  ejecución certificante sigue teniendo prohibido importarla (verificado por
  TestCertificationModulesWithoutGtWritePorts). Resolución: extender el allowlist del test
  con justificación; sin refactor del código congelado de Gate 2 (YAGNI, no tocar código
  verificado). El hallazgo del test se congela como excepción documentada, no como deuda.

## 4. DECISIONES CONGELADAS

| Decisión | Justificación |
|---|---|
| Override --allow-missing-manifest opera fuera de ejecución certificante (R26) | Sin manifest la verificación de sellado es imposible; el override es explícito, indexable ([SANITIZE-W01]) y requiere acción humana deliberada. Sanitize es mecanismo de migración/corrección, no tooling de certificación (R26 permite migraciones fuera del run certificante bajo NADR-21). |
| Exclusión de tools/benchmark_archive del scan R28 (O-4.3-1) | Código legacy de archivo sin ruta de ejecución en certificación. Remediarlo sería deuda sin beneficio (YAGNI); documentarlo congela la frontera. |

## 5. TESTS DE CONTRATO

tests/unit/test_certification_boundary.py (10 tests):
- TestSealedOracleImmutability: test_no_instance_mutators, test_pydantic_frozen_config, test_assignment_raises (ValidationError sobre instancia frozen)
- TestCertificationModulesWithoutGtWritePorts: 4 módulos parametrizados sin símbolos de escritura GT
- TestGtAdaptersScopedToGroundTruthDir: adapter ignora candidates/reports; reader no resuelve fuera de ground_truth/ (comportamental, sin acceso a privados)
- TestLifecycleAuthorityOwnership: autoridad acotada a use_cases.py (dominio) + freeze_ground_truth.py (sellado MIG-06, O-4.3-3)

## 6. TRAZABILIDAD

| Task | Reglas | Estado |
|---|---|---|
| 4.3.1 | NADR-24 §5.6 R25-R28 | DONE (verificación + contract tests) |
| 4.3.2 | NADR-24 §5.6 R25-R26, GAP-5.2-05 | DONE (verificación formal cadena sanitize/use cases/override D2) |

**Nota de Gobernanza:** Este documento es evidencia forense de verificación de frontera.
No tiene autoridad normativa. No redefine reglas de NADRs ni ADRs.
