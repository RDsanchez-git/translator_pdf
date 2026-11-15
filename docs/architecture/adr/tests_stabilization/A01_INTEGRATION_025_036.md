# A-01 — Censo integración 25–36 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 12 módulos; 138 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_g3_b1_policy_guardrails.py` | 4 | — | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py` | 11 | DB/tmp | core.ast.enums, core.ast.models, core.chunking.semantic_chunking, core.chunking.manifest_contract |
| `tests/integration/test_g3_b3_2_fenced_receipts.py` | 13 | DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b3_3a_staged_publication.py` | 13 | DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b3_3b_finalization.py` | 20 | mock,DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b3_structured_result_contract.py` | 12 | — | core.ast.models, core.ast.enums, core.ast.grouper, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b4_1_worker_coexistence.py` | 6 | DB/tmp | core.ast.enums, core.ast.models, core.chunking.manifest_contract, core.chunking.semantic_chunking |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py` | 8 | mock,I/O,DB/tmp | apps.ocr_router, core.ast.enums, core.ast.hashing, core.ast.models |
| `tests/integration/test_g3_b4_3a_engine_staging.py` | 18 | DB/tmp | apps.llm_workers.sync_bridge, apps.llm_workers.routing, apps.llm_workers.prompt_builder, core.ast.enums |
| `tests/integration/test_g3_b4_3b_publication_recovery.py` | 17 | mock,DB/tmp | core.ast.enums, core.ast.models, core.ast.grouper, core.chunking.manifest_contract |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py` | 13 | DB/tmp | core.ast.enums, core.ast.hashing, core.ast.models, core.ast.registry |
| `tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py` | 3 | DB/tmp | apps.llm_workers.rate_limiter, apps.llm_workers.sync_bridge, apps.llm_workers.routing, apps.llm_workers.prompt_builder |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_g3_b1_policy_guardrails.py:37` | `test_g3_r1_single_translate_cannot_be_disguised_as_preserve` | ? | ? | ? |
| `tests/integration/test_g3_b1_policy_guardrails.py:45` | `test_g3_r1_protected_equation_cannot_be_disguised_as_translate` | ? | ? | ? |
| `tests/integration/test_g3_b1_policy_guardrails.py:53` | `test_g3_r1_partial_table_cannot_be_disguised_as_preserve` | ? | ? | ? |
| `tests/integration/test_g3_b1_policy_guardrails.py:61` | `test_g3_r1_co_located_segments_use_original_source_bytes_as_payload` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:49` | `test_persisted_manifest_and_tasks_survive_reopening` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:64` | `test_retry_is_idempotent_and_does_not_reset_task_state` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:77` | `test_conflicting_plan_for_same_generation_is_rejected_without_mutation` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:90` | `test_legacy_tasks_without_manifest_are_not_adopted` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:104` | `test_injected_sqlite_failure_rolls_back_plan_and_all_tasks` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:121` | `test_savepoint_does_not_commit_caller_transaction` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:135` | `test_tampered_manifest_is_rejected_when_loading` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:147` | `test_missing_queue_task_blocks_loading_and_idempotent_retry` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:162` | `test_existing_queue_schema_migrates_with_no_task_data_loss` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:174` | `test_ast_generation_mismatch_fails_before_database_write` | ? | ? | ? |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py:185` | `test_nested_savepoint_failure_does_not_rollback_caller_changes` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:78` | `test_stage_reopen_replay_and_recompose_two_nodes` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:98` | `test_preserve_bypass_recovered_with_translation` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:117` | `test_incomplete_staged_plan_is_not_materializable` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:131` | `test_bad_or_expired_lease_rejects_without_receipts` | ? | sí? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:151` | `test_bad_response_rejected_before_sqlite_mutation` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:164` | `test_identical_retry_is_no_op_and_conflicting_retry_is_rejected` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:180` | `test_missing_non_preserve_response_rejected_before_sqlite_mutation` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:192` | `test_preserve_chunk_rejects_provider_result` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:205` | `test_injected_update_failure_rolls_back_receipt_and_state` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:221` | `test_nested_transaction_owned_by_caller_is_not_committed` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:237` | `test_corrupt_receipt_checksum_rejected_for_replay` | ? | ? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:251` | `test_drift_between_receipts_and_queue_blocks_replay` | ? | sí? | ? |
| `tests/integration/test_g3_b3_2_fenced_receipts.py:267` | `test_old_queue_schema_without_receipts_upgrades_on_first_stage` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:91` | `test_publishes_complete_two_node_chunk_and_attests_source` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:106` | `test_reopen_uses_durable_queue_receipt_for_idempotent_publication` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:118` | `test_preserve_node_does_not_require_provider_response` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:126` | `test_incomplete_receipts_cannot_publish` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:142` | `test_corrupted_receipt_rejects_before_publishing` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:152` | `test_failure_on_publication_insert_rolls_back_all_nodes` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:164` | `test_legacy_projection_without_publication_is_not_overwritten` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:175` | `test_corrupt_projection_rejected_on_replay` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:185` | `test_tampered_publication_sha_rejected_on_replay` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:195` | `test_source_hash_and_node_coverage_fenced` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:207` | `test_nested_transaction_ownership_and_rollback` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:219` | `test_idempotent_retry_does_not_commit_parent_transaction` | ? | ? | ? |
| `tests/integration/test_g3_b3_3a_staged_publication.py:231` | `test_rejects_invalid_projection_version` | ? | sí? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:92` | `test_full_plan_finalizes_atomically` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:106` | `test_replay_is_idempotent_and_preserves_timestamps` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:115` | `test_replay_after_reopening_both_databases` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:124` | `test_recovery_after_crash_between_publication_and_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:133` | `test_missing_publication_rejects_without_marking_completed` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:141` | `test_uncommitted_materialized_publication_cannot_authorize_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:152` | `test_corrupt_materialized_projection_blocks_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:162` | `test_altered_publication_digest_blocks_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:171` | `test_corrupt_queue_receipt_blocks_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:181` | `test_missing_receipt_blocks_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:190` | `test_execution_identity_drift_blocks_completion` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:199` | `test_half_completed_plan_fails_closed` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:208` | `test_queue_update_trigger_rolls_back_whole_plan` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:225` | `test_expired_lease_does_not_block_recovery_from_durable_staged_receipt` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:233` | `test_missing_owner_fails_closed` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:242` | `test_nested_queue_transaction_ownership` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:253` | `test_already_completed_with_lease_is_rejected` | ? | ? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:264` | `test_invalid_version_cannot_finalize` | ? | sí? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:271` | `test_scheduler_does_not_treat_all_result_staged_as_finished` | ? | sí? | ? |
| `tests/integration/test_g3_b3_3b_finalization.py:286` | `test_completed_replay_rejects_tampered_receipts` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:59` | `test_two_nodes_one_chunk_response_order_is_identity_based_not_positional` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:74` | `test_fragments_across_chunks_reassemble_without_added_delimiters` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:89` | `test_preserve_is_bypassed_and_partial_remains_explicit` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:113` | `test_only_preserve_nodes_materialize_without_provider_results` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:138` | `test_invalid_member_responses_fail_closed` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:155` | `test_invalid_json_is_rejected` | ? | sí? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:161` | `test_unknown_chunk_rejected_before_payload_parse` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:167` | `test_incomplete_or_extra_chunks_never_return_partial_nodes` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:179` | `test_source_boundary_whitespace_preserved_through_segmented_translation` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:188` | `test_whitespace_only_source_never_silently_disappears_in_translation` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:195` | `test_response_size_bound_rejects_uncontrolled_payload` | ? | ? | ? |
| `tests/integration/test_g3_b3_structured_result_contract.py:201` | `test_translated_unicode_surrogates_rejected_before_projection` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:88` | `test_read_manifest_and_idempotent_enqueue_after_assembler_trigger` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:99` | `test_engine_pickup_never_claims_assembler_trigger` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:110` | `test_finalize_ignores_assembler_trigger_but_never_completes_it` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:121` | `test_replay_after_both_dbs_reopen_with_assembler_task` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:134` | `test_unexpected_foreign_worker_does_not_hide_as_assembler` | ? | ? | ? |
| `tests/integration/test_g3_b4_1_worker_coexistence.py:146` | `test_scheduler_considers_only_llm_tasks_even_if_assembler_pending` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:172` | `test_fresh_ingestion_persists_manifest_and_exactly_one_ast` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:185` | `test_incomplete_generation_retries_without_illegal_cas` | ? | sí? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:194` | `test_replay_existing_identical_manifest_is_idempotent` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:205` | `test_generation_drift_fails_closed_before_ast_or_enqueue` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:216` | `test_legacy_tasks_without_plan_not_adopted` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:228` | `test_active_or_finished_document_shortcuts_before_ocr` | ? | sí? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:238` | `test_fsm_lookup_error_fails_closed_without_parsing` | ? | ? | ? |
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py:250` | `test_failed_generation_requires_explicit_policy` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:98` | `test_translation_members_are_staged_not_acked` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:114` | `test_preserve_unit_bypasses_provider_and_stages_null` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:125` | `test_preserve_unit_accepts_no_processor` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:134` | `test_translation_unit_rejects_missing_processor_before_staging` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:145` | `test_malformed_response_never_stages_or_completes` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:158` | `test_bad_lease_rejected_before_provider` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:175` | `test_database_fence_remains_authoritative_after_provider` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:235` | `test_bridge_prompt_contains_manifest_binding_and_all_member_sources` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:261` | `test_bridge_rejects_unbound_provider_output` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:273` | `test_bridge_preserve_unit_is_never_sent` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:301` | `test_bridge_masks_and_restores_exact_inline_math_in_each_member` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:322` | `test_bridge_rejects_lost_or_modified_math_token` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:338` | `test_openai_dialect_unwraps_content_json_string_for_g3` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:369` | `test_openai_dialect_plain_inner_object_is_rejected_by_g3_parser` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:387` | `test_math_source_uncertain_fails_before_provider` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:404` | `test_math_token_cannot_move_between_two_members` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:420` | `test_math_token_injection_is_rejected_even_when_expected_tokens_survive` | ? | ? | ? |
| `tests/integration/test_g3_b4_3a_engine_staging.py:433` | `test_hallucinated_math_token_rejected_in_no_math_unit` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:123` | `test_staged_to_publication_to_completion_and_ready` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:133` | `test_incomplete_tasks_do_not_publish_or_advance` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:140` | `test_crash_after_publication_replays_without_reinference` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:154` | `test_crash_after_queue_completion_replays_to_fsm` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:165` | `test_completed_with_no_publication_fails_closed` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:176` | `test_corrupt_projection_never_advances_fsm` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:187` | `test_completed_without_receipt_never_advances_fsm` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:198` | `test_completed_mixed_with_staged_is_rejected` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:208` | `test_fsm_cas_cannot_retransition_out_of_processing` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:219` | `test_g3_recovery_selector_handles_both_homogeneous_states` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:232` | `test_g3_recovery_selector_excludes_incomplete_and_finished_fsm` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:243` | `test_failed_plus_staged_plan_is_selected_for_fatal_handling` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:254` | `test_g3_recovery_selector_rejects_invalid_limit` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:259` | `test_reconciler_does_not_bypass_g3_publication_barrier` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:273` | `test_engine_recovery_never_initializes_provider` | ? | ? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:295` | `test_g3_scheduler_excludes_unknown_generation` | ? | sí? | ? |
| `tests/integration/test_g3_b4_3b_publication_recovery.py:329` | `test_g3_scheduler_keeps_valid_pending_and_completed_generations` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:53` | `test_profile_survives_independent_connection_and_restart` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:63` | `test_profile_replay_is_idempotent` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:72` | `test_conflicting_profile_replay_never_overwrites` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:82` | `test_profile_not_found_returns_none` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:87` | `test_profile_document_isolation` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:96` | `test_profile_integrity_rejects_tampered_row` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:106` | `test_profile_invalid_enum_rejected_on_read_even_if_hash_matches` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:118` | `test_profile_invalid_type_rejected` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:125` | `test_assembly_projection_validates_digest` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:134` | `test_tampered_projection_fails_at_assembly_read` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:144` | `test_tampered_hash_fails_at_assembly_read` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:154` | `test_wrong_generation_or_projection_version_not_consumed` | ? | ? | ? |
| `tests/integration/test_g3_b4_4_profile_projection_assembly.py:163` | `test_restarted_ast_profile_and_projection_build_tex_without_external_services` | ? | ? | ? |
| `tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py:93` | `test_bridge_worker_threads_persist_quota_on_single_owner` | ? | ? | ? |
| `tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py:138` | `test_old_direct_connection_reproduces_thread_affinity_error` | ? | ? | ? |
| `tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py:151` | `test_store_close_is_idempotent_and_rejects_late_writes` | ? | ? | ? |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
