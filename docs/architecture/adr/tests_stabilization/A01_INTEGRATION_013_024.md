# A-01 — Censo integración 13–24 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 12 módulos; 61 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_canonicalize_gt_hardening.py` | 4 | DB/tmp,externo | core.ast.enums, core.ast.models, core.benchmark.corpus.dtos, infra.fs.corpus_repository |
| `tests/integration/test_chunker_snapshot.py` | 1 | I/O,skip | core.ast.models, core.validation.estimators, core.chunking.semantic_chunking, apps.bootstrap.pipeline_factory |
| `tests/integration/test_cli_router.py` | 4 | mock | apps.cli.main |
| `tests/integration/test_curate_gt.py` | 6 | DB/tmp,externo | core.benchmark.corpus.dtos, infra.fs.corpus_repository |
| `tests/integration/test_cv_failure_path.py` | 6 | I/O,DB/tmp,externo | — |
| `tests/integration/test_cv_profile_validation.py` | 13 | mock,DB/tmp | core.benchmark.verification.outcome |
| `tests/integration/test_cv_regression_path.py` | 6 | DB/tmp,externo | — |
| `tests/integration/test_cv_report_persistence.py` | 12 | mock,I/O,DB/tmp | core.benchmark.topology.criticality.costs, core.benchmark.topology.regression.models, core.benchmark.topology.regression.report, core.benchmark.verification.report |
| `tests/integration/test_e2e_walking_skeleton.py` | 1 | mock,I/O | core.ast.models, core.compiler.assembler, apps.llm_workers.prompt_builder, apps.llm_workers.rate_limiter |
| `tests/integration/test_embedding_smoke.py` | 1 | mock,skip | core.ast.models, apps.llm_workers.adapters, core.prompting.dialects.openai_compatible |
| `tests/integration/test_execution_failure_exit_code.py` | 2 | mock,I/O,DB/tmp | core.benchmark.verification.outcome |
| `tests/integration/test_freeze_gt_curation_gate.py` | 5 | I/O,DB/tmp,externo | core.ast.enums, core.ast.models, core.benchmark.corpus.dtos, infra.fs.corpus_repository |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_canonicalize_gt_hardening.py:46` | `test_no_legacy_ids_is_noop` | ? | ? | ? |
| `tests/integration/test_canonicalize_gt_hardening.py:57` | `test_legacy_ids_canonicalized_with_lineage` | ? | ? | ? |
| `tests/integration/test_canonicalize_gt_hardening.py:69` | `test_collision_aborts` | ? | ? | ? |
| `tests/integration/test_canonicalize_gt_hardening.py:77` | `test_refuse_sealed` | ? | ? | ? |
| `tests/integration/test_chunker_snapshot.py:22` | `test_snapshot_verification` | ? | ? | posible |
| `tests/integration/test_cli_router.py:16` | `test_translate_subcommand_routing` | ? | ? | ? |
| `tests/integration/test_cli_router.py:32` | `test_resume_subcommand_routing` | ? | ? | ? |
| `tests/integration/test_cli_router.py:48` | `test_sweep_subcommand_routing` | ? | ? | ? |
| `tests/integration/test_cli_router.py:62` | `test_status_subcommand_routing` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:35` | `test_create_curated_entry` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:45` | `test_pending_to_curated_and_back_resets` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:59` | `test_refuse_sealed` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:67` | `test_refuse_unknown_doc` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:74` | `test_refuse_empty_report_ref` | ? | ? | ? |
| `tests/integration/test_curate_gt.py:81` | `test_serialization_deterministic` | ? | ? | ? |
| `tests/integration/test_cv_failure_path.py:45` | `test_missing_pdf_dir_produces_exit_3` | integration | ? | ? |
| `tests/integration/test_cv_failure_path.py:60` | `test_failure_is_explicit_in_stderr` | ? | ? | ? |
| `tests/integration/test_cv_failure_path.py:76` | `test_evidence_persisted_without_regression_report` | integration | ? | ? |
| `tests/integration/test_cv_failure_path.py:95` | `test_failure_aborts_before_any_extraction` | ? | ? | ? |
| `tests/integration/test_cv_failure_path.py:136` | `test_invalid_json_manifest_produces_exit_3_with_evidence` | ? | ? | ? |
| `tests/integration/test_cv_failure_path.py:153` | `test_schema_invalid_manifest_produces_exit_3_with_evidence` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:129` | `test_full_profile_produces_scientific_verdict` | e2e | ? | ? |
| `tests/integration/test_cv_profile_validation.py:142` | `test_full_profile_coverage_is_21_documents` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:158` | `test_full_profile_identity_chain_complete` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:180` | `test_full_profile_regression_report_present` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:198` | `test_smoke_profile_produces_scientific_verdict` | e2e | ? | ? |
| `tests/integration/test_cv_profile_validation.py:209` | `test_smoke_profile_coverage_is_5_documents` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:228` | `test_smoke_coverage_is_subset_of_full` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:250` | `test_smoke_pass_does_not_imply_full_verification` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:283` | `test_execution_id_differs_between_profiles` | e2e | ? | ? |
| `tests/integration/test_cv_profile_validation.py:304` | `test_profile_identity_differs_between_profiles` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:324` | `test_execution_id_is_deterministic` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:350` | `test_profile_identity_is_deterministic` | ? | ? | ? |
| `tests/integration/test_cv_profile_validation.py:369` | `test_exit_code_matches_scientific_verdict` | ? | ? | ? |
| `tests/integration/test_cv_regression_path.py:46` | `test_exit_code_is_hard_fail` | e2e | ? | ? |
| `tests/integration/test_cv_regression_path.py:54` | `test_exit_code_nonzero_so_ci_check_is_red` | ? | ? | ? |
| `tests/integration/test_cv_regression_path.py:59` | `test_stderr_is_explicit` | ? | ? | ? |
| `tests/integration/test_cv_regression_path.py:67` | `test_evidence_persisted_with_regression_outcome` | e2e | ? | ? |
| `tests/integration/test_cv_regression_path.py:76` | `test_evidence_contains_coverage_and_identity` | ? | ? | ? |
| `tests/integration/test_cv_regression_path.py:86` | `test_regression_report_present_in_evidence` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:32` | `test_filename_contains_execution_id_prefix` | unit | ? | ? |
| `tests/integration/test_cv_report_persistence.py:38` | `test_filename_contains_timestamp` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:42` | `test_timestamp_shell_has_no_colons` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:47` | `test_different_timestamps_produce_different_filenames` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:161` | `test_report_written_with_unique_filename` | integration | ? | ? |
| `tests/integration/test_cv_report_persistence.py:183` | `test_report_contains_identity_chain` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:217` | `test_execution_id_is_reproducible` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:249` | `test_report_contains_profile_identity` | integration | ? | ? |
| `tests/integration/test_cv_report_persistence.py:274` | `test_report_contains_coverage` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:296` | `test_different_profiles_produce_different_execution_id` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:325` | `test_smoke_profile_with_documents_produces_correct_coverage` | ? | ? | ? |
| `tests/integration/test_cv_report_persistence.py:371` | `test_full_profile_with_documents_produces_full_coverage` | ? | ? | ? |
| `tests/integration/test_e2e_walking_skeleton.py:131` | `test_full_pipeline_from_ast_with_cache_reentrancy` | ? | ? | ? |
| `tests/integration/test_embedding_smoke.py:12` | `test_isolated_generation_request` | ? | ? | posible |
| `tests/integration/test_execution_failure_exit_code.py:19` | `test_exit_code_4_on_execution_failure` | integration | ? | ? |
| `tests/integration/test_execution_failure_exit_code.py:77` | `test_execution_failure_exit_code_does_not_collide_with_warning` | ? | ? | ? |
| `tests/integration/test_freeze_gt_curation_gate.py:103` | `test_draft_without_curated_entry_aborts` | ? | ? | ? |
| `tests/integration/test_freeze_gt_curation_gate.py:117` | `test_draft_with_curated_entry_seals` | ? | ? | ? |
| `tests/integration/test_freeze_gt_curation_gate.py:133` | `test_allow_uncurated_overrides_gate_with_warning` | ? | ? | ? |
| `tests/integration/test_freeze_gt_curation_gate.py:146` | `test_fully_sealed_corpus_without_checklist_is_noop` | ? | ? | ? |
| `tests/integration/test_freeze_gt_curation_gate.py:160` | `test_missing_checklist_with_pending_drafts_aborts` | ? | ? | ? |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
