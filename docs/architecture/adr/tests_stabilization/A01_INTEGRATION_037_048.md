# A-01 — Censo integración 37–48 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 12 módulos; 64 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_g3_b4_8_preserve_engine.py` | 1 | mock,DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.manifest_contract |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py` | 11 | DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.manifest_contract |
| `tests/integration/test_g3_chunk_identity_contract.py` | 8 | I/O,DB/tmp | core.ast.models, core.ast.enums, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_wal_stage_write_scope.py` | 3 | DB/tmp | infra.db.control_repo |
| `tests/integration/test_g5_assembler_lease_recovery.py` | 12 | mock,I/O,DB/tmp | infra.db.assembly_recovery, apps.compiler.__main__, apps.compiler.tectonic_runner, core.ast.enums |
| `tests/integration/test_g5_assembler_worker_integration.py` | 3 | I/O | apps.compiler.__main__, core.execution.exceptions, infra.db.assembly_recovery |
| `tests/integration/test_golden_parser.py` | 1 | mock,I/O,skip | core.ast.models, apps.bootstrap.pipeline_factory, core.ast.enums, core.ast.builder |
| `tests/integration/test_healing_concurrency.py` | 2 | — | core.validation.models, core.healing.models, core.healing.telemetry, core.healing.pipeline |
| `tests/integration/test_healing_e2e_telemetry.py` | 5 | — | core.validation.models, core.healing.models, core.healing.telemetry, core.healing.pipeline |
| `tests/integration/test_parameter_freeze.py` | 7 | I/O,DB/tmp,skip | core.benchmark.topology.criticality.costs, core.benchmark.topology.regression.provenance |
| `tests/integration/test_pdf_inbox_submission.py` | 8 | mock,I/O,DB/tmp | apps.cli.pdf_inbox, apps.cli.main |
| `tests/integration/test_pdf_pdf_fsm_transaction_ownership.py` | 3 | DB/tmp | core.execution.exceptions, infra.db.fsm_repository |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_g3_b4_8_preserve_engine.py:91` | `test_engine_preserve_provider_decision_and_full_publication` | ? | sí? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:86` | `test_fenced_expired_g3_requeued_only_once_and_reclaimed` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:97` | `test_stale_lease_cannot_stage_after_fenced_reclaim` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:113` | `test_fenced_recovery_rejects_stale_authority` | ? | sí? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:132` | `test_g3_staged_receipt_cannot_be_rewound_or_completed_by_legacy` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:149` | `test_g3_no_receipt_never_cqrs_completes` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:157` | `test_legacy_reconciliation_without_g3_manifest_preserved` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:170` | `test_reconciler_routes_g3_without_legacy_event_or_handler` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:183` | `test_handler_direct_g3_rematerialization_has_no_materialized_side_effect` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:204` | `test_reconciler_heartbeat_sqlite_connection_is_owned_by_heartbeat_thread` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:244` | `test_g3_assembler_trigger_is_never_requeued_by_legacy_handler` | ? | ? | ? |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py:268` | `test_g3_recovery_creates_receipt_table_if_old_queue_has_no_receipts` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:29` | `test_g3_t01_two_nodes_one_chunk_distinct_member_identities` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:39` | `test_g3_t02_deterministic_roundtrip_and_generation_binding` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:53` | `test_g3_t03_sentence_overflow_preserves_parent_lineage_and_all_source_bytes` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:67` | `test_g3_reject_missing_extra_duplicate_member_and_payload_tampering` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:79` | `test_g3_fails_closed_if_sentence_cannot_fit_budget` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:85` | `test_g3_preserve_and_omit_are_not_sent_as_regular_translate_members` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:99` | `test_g3_fail_closed_on_defer_strategy` | ? | ? | ? |
| `tests/integration/test_g3_chunk_identity_contract.py:107` | `test_g3_rejects_unimplemented_overflow_policy_instead_of_overbudget_unit` | ? | ? | ? |
| `tests/integration/test_g3_wal_stage_write_scope.py:32` | `test_staging_write_scope_reserves_wal_writer_before_snapshot` | ? | ? | ? |
| `tests/integration/test_g3_wal_stage_write_scope.py:70` | `test_existing_caller_transaction_remains_caller_owned` | ? | ? | ? |
| `tests/integration/test_g3_wal_stage_write_scope.py:86` | `test_nested_and_owned_write_scopes_rollback_on_exception` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:101` | `test_claim_double_owner_and_monotonic_versions` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:114` | `test_alive_heartbeat_blocks_recovery_even_with_old_fsm_updated_at` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:132` | `test_recovery_fences_old_owner_and_new_owner_completes` | ? | sí? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:167` | `test_wrong_epoch_and_wrong_leader_cannot_recover` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:179` | `test_retry_budget_quarantines_instead_of_infinite_loop` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:193` | `test_expired_lease_old_worker_cannot_publish_even_without_takeover` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:206` | `test_failure_only_current_valid_owner_can_change_fsm` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:217` | `test_pdf_guard_rejects_invalid_bytes_and_foreign_paths` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:230` | `test_concurrent_claim_only_one_worker_is_admitted` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:253` | `test_rollback_after_pdf_promotion_is_recoverable` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:270` | `test_full_pdf_promoted_before_db_commit_is_recoverable` | ? | ? | ? |
| `tests/integration/test_g5_assembler_lease_recovery.py:316` | `test_missing_projection_blocks_real_g5_worker_before_pdf` | ? | ? | ? |
| `tests/integration/test_g5_assembler_worker_integration.py:77` | `test_real_worker_method_publishes_fenced_document` | ? | ? | ? |
| `tests/integration/test_g5_assembler_worker_integration.py:88` | `test_real_worker_method_rejects_expired_lease_without_final_publication` | ? | ? | ? |
| `tests/integration/test_g5_assembler_worker_integration.py:103` | `test_real_worker_method_fences_failure_state` | ? | ? | ? |
| `tests/integration/test_golden_parser.py:49` | `test_parser_runtime_matches_golden_fingerprint` | ? | ? | posible |
| `tests/integration/test_healing_concurrency.py:12` | `test_telemetry_registry_async_concurrency` | ? | ? | ? |
| `tests/integration/test_healing_concurrency.py:72` | `test_healing_pipeline_emits_full_audit_on_rollback` | ? | ? | ? |
| `tests/integration/test_healing_e2e_telemetry.py:59` | `test_e2e_case_a_markdown_leakage` | ? | ? | ? |
| `tests/integration/test_healing_e2e_telemetry.py:69` | `test_e2e_case_b_unbalanced_braces` | ? | ? | ? |
| `tests/integration/test_healing_e2e_telemetry.py:79` | `test_e2e_case_c_math_truncation` | ? | ? | ? |
| `tests/integration/test_healing_e2e_telemetry.py:88` | `test_e2e_rollback_guarantee_on_revalidation_failure` | ? | ? | ? |
| `tests/integration/test_healing_e2e_telemetry.py:102` | `test_e2e_telemetry_aggregate_metrics` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:48` | `test_freeze_materializes_artifacts_with_recomputable_identity` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:80` | `test_rerun_is_idempotent_noop` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:90` | `test_conflict_returns_exit_2_without_writing` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:103` | `test_final_evaluation_record_emitted_over_existing_freeze` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:119` | `test_invalid_timestamp_returns_exit_2` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:126` | `test_missing_report_returns_exit_2_without_partial_state` | ? | ? | ? |
| `tests/integration/test_parameter_freeze.py:136` | `test_repo_freeze_artifact_matches_domain_defaults` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:26` | `test_atomic_submission_uses_ocr_byte_identity` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:41` | `test_identical_pdf_does_not_overwrite_existing_inbox_item` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:55` | `test_named_collision_with_different_content_fails_closed` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:69` | `test_rejects_non_pdf_filename_without_copying` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:79` | `test_empty_input_not_published` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:90` | `test_no_nonatomic_fallback_if_hard_links_unavailable` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:107` | `test_cli_translate_never_invokes_legacy_r1_pipeline` | ? | ? | ? |
| `tests/integration/test_pdf_inbox_submission.py:126` | `test_cli_legacy_job_id_is_rejected_before_writing` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_fsm_transaction_ownership.py:58` | `test_initialize_does_not_commit_outer_transaction` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_fsm_transaction_ownership.py:74` | `test_transition_does_not_commit_outer_transaction` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_fsm_transaction_ownership.py:91` | `test_failed_cas_does_not_rollback_outer_transaction` | ? | ? | ? |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
