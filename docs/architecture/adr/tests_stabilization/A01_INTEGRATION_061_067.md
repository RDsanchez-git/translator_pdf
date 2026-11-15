# A-01 — Censo integración 61–67 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 7 módulos; 36 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_translation_technical.py` | 1 | DB/tmp,skip | core.pipeline.job, core.pipeline.orchestrator, infra.db.fsm_repository, core.execution.handlers |
| `tests/integration/test_validation_integration.py` | 5 | mock | core.ast.models, apps.llm_workers.dispatcher, apps.llm_workers.prompt_builder, core.finops.measurement |
| `tests/integration/test_verification_pipeline_connection.py` | 5 | DB/tmp | apps.bootstrap.pipeline_factory, core.execution.exceptions, infra.adapters.pdf_parser |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py` | 7 | mock,DB/tmp | apps.llm_workers.sync_bridge, apps.llm_workers.prompt_builder, core.prompting.inference_result, core.ast.enums |
| `tests/integration/test_w08_cli_foreground_single_generation_offline.py` | 1 | mock,DB/tmp | apps.cli, core.ast.enums, core.ast.hashing, core.ast.models |
| `tests/integration/test_w08_durable_context_boundary.py` | 11 | DB/tmp | core.ast.enums, core.ast.hashing, core.ast.models, core.ast.grouper |
| `tests/integration/test_w08_ocr_g3_context_wiring.py` | 6 | DB/tmp | apps.llm_workers.sync_bridge, apps.llm_workers.prompt_builder, apps.llm_workers.routing, core.ast.enums |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_translation_technical.py:55` | `test_latex_token_sets_and_balances` | ? | ? | posible |
| `tests/integration/test_validation_integration.py:114` | `test_integration_hard_fail_on_unbalanced_braces` | ? | ? | ? |
| `tests/integration/test_validation_integration.py:133` | `test_integration_preservation_fail_on_missing_doi` | ? | ? | ? |
| `tests/integration/test_validation_integration.py:153` | `test_integration_warning_does_not_block` | ? | ? | ? |
| `tests/integration/test_validation_integration.py:173` | `test_integration_perimeter_fail_on_markdown` | ? | ? | ? |
| `tests/integration/test_validation_integration.py:192` | `test_integration_document_level_pi04_fail` | ? | ? | ? |
| `tests/integration/test_verification_pipeline_connection.py:59` | `test_build_extraction_pipeline_returns_pdf_parser_adapter` | integration | ? | ? |
| `tests/integration/test_verification_pipeline_connection.py:67` | `test_pipeline_extracts_nonempty_ast_from_text_pdf` | ? | ? | ? |
| `tests/integration/test_verification_pipeline_connection.py:76` | `test_extracted_ast_nodes_have_minimum_structure` | ? | ? | ? |
| `tests/integration/test_verification_pipeline_connection.py:87` | `test_extracted_ast_is_deterministic` | ? | ? | ? |
| `tests/integration/test_verification_pipeline_connection.py:98` | `test_production_root_rejects_unrepresented_vector_pdf` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:127` | `test_w06_not_started_expired_lease_blocks_fake_before_io` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:142` | `test_w06_confirmed_response_durable_receipt_no_second_claim` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:215` | `test_w06_lost_reply_is_quarantined_without_second_provider_call` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:232` | `test_w06_contract_oracle_never_automatically_repeats_unknown_effect` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:241` | `test_w06_restart_never_reinitializes_provider_for_unknown` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:278` | `test_w06_reconciler_quarantines_expired_translate_without_receipt` | ? | ? | ? |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py:310` | `test_w06_unknown_survives_new_sqlite_connection` | ? | ? | ? |
| `tests/integration/test_w08_cli_foreground_single_generation_offline.py:86` | `test_cli_foreground_context_receipts_projections_and_pdf_same_generation` | integration | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:60` | `test_w08_snapshot_persists_with_plan_and_survives_new_connection` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:78` | `test_w08_context_enrollment_idempotent_and_does_not_reset_task` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:90` | `test_w08_rejects_legacy_manifest_without_snapshots` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:106` | `test_w08_detects_snapshot_tampering_on_restart` | ? | sí? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:122` | `test_w08_missing_snapshot_fails_closed_after_restart` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:137` | `test_w08_inference_plan_with_global_root_is_rejected_before_writing` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:149` | `test_w08_plan_context_depth_mismatch_is_rejected` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:161` | `test_w08_ast_generation_mismatch_rejected_without_database_mutation` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:175` | `test_w08_injected_sqlite_failure_rolls_back_plan_tasks_and_snapshot` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:196` | `test_w08_snapshot_write_respects_external_transaction_rollback` | ? | ? | ? |
| `tests/integration/test_w08_durable_context_boundary.py:212` | `test_w08_derived_snapshots_never_claim_a_provider_authority` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:101` | `test_w08_ocr_produces_distinct_contexts_without_global_root` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:112` | `test_w08_new_connection_delivers_effective_section_context_to_fake` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:135` | `test_w08_missing_context_fails_before_fake_provider` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:154` | `test_w08_context_from_other_generation_fails_before_fake` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:181` | `test_w08_ast_cache_and_sqlite_rehydrate_across_fresh_instances` | ? | ? | ? |
| `tests/integration/test_w08_ocr_g3_context_wiring.py:212` | `test_w08_ocr_contextual_ast_hash_matches_raw_semantic_identity` | ? | ? | ? |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
