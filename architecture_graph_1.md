# Mapa de Arquitectura (Dependencias entre M?dulos)

```mermaid
graph LR
    classDef fileStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff;
    apps_api_server_py["?? apps/api/server.py"]:::fileStyle
    apps_api___init___py["?? apps/api/__init__.py"]:::fileStyle
    apps_bootstrap_pipeline_factory_py["?? apps/bootstrap/pipeline_factory.py"]:::fileStyle
    apps_bootstrap___init___py["?? apps/bootstrap/__init__.py"]:::fileStyle
    apps_cli_main_py["?? apps/cli/main.py"]:::fileStyle
    apps_compiler_docker_runner_py["?? apps/compiler/docker_runner.py"]:::fileStyle
    apps_compiler_log_parser_py["?? apps/compiler/log_parser.py"]:::fileStyle
    apps_compiler_tex_builder_py["?? apps/compiler/tex_builder.py"]:::fileStyle
    apps_compiler___init___py["?? apps/compiler/__init__.py"]:::fileStyle
    apps_compiler___main___py["?? apps/compiler/__main__.py"]:::fileStyle
    apps_compiler_sandbox_server_py["?? apps/compiler/sandbox/server.py"]:::fileStyle
    apps_daemons_chaos_runner_py["?? apps/daemons/chaos_runner.py"]:::fileStyle
    apps_daemons_fake_gemini_py["?? apps/daemons/fake_gemini.py"]:::fileStyle
    apps_daemons_reconciler_py["?? apps/daemons/reconciler.py"]:::fileStyle
    apps_llm_workers_cache_py["?? apps/llm_workers/cache.py"]:::fileStyle
    apps_llm_workers_chunk_processor_py["?? apps/llm_workers/chunk_processor.py"]:::fileStyle
    apps_llm_workers_dispatcher_py["?? apps/llm_workers/dispatcher.py"]:::fileStyle
    apps_llm_workers_gemini_client_py["?? apps/llm_workers/gemini_client.py"]:::fileStyle
    apps_llm_workers_prompt_builder_py["?? apps/llm_workers/prompt_builder.py"]:::fileStyle
    apps_llm_workers_resilience_py["?? apps/llm_workers/resilience.py"]:::fileStyle
    apps_llm_workers_router_translation_py["?? apps/llm_workers/router_translation.py"]:::fileStyle
    apps_llm_workers_workers_py["?? apps/llm_workers/workers.py"]:::fileStyle
    apps_llm_workers___init___py["?? apps/llm_workers/__init__.py"]:::fileStyle
    apps_llm_workers___main___py["?? apps/llm_workers/__main__.py"]:::fileStyle
    apps_ocr_router___main___py["?? apps/ocr_router/__main__.py"]:::fileStyle
    apps_ocr_workers_router_py["?? apps/ocr_workers/router.py"]:::fileStyle
    apps_ocr_workers___init___py["?? apps/ocr_workers/__init__.py"]:::fileStyle
    core_ast_hashing_py["?? core/ast/hashing.py"]:::fileStyle
    core_ast_models_py["?? core/ast/models.py"]:::fileStyle
    core_ast_parser_py["?? core/ast/parser.py"]:::fileStyle
    core_ast_registry_py["?? core/ast/registry.py"]:::fileStyle
    core_ast_router_py["?? core/ast/router.py"]:::fileStyle
    core_ast_segmenter_py["?? core/ast/segmenter.py"]:::fileStyle
    core_ast_validator_py["?? core/ast/validator.py"]:::fileStyle
    core_ast___init___py["?? core/ast/__init__.py"]:::fileStyle
    core_compiler_assembler_py["?? core/compiler/assembler.py"]:::fileStyle
    core_execution_event_log_py["?? core/execution/event_log.py"]:::fileStyle
    core_execution_exceptions_py["?? core/execution/exceptions.py"]:::fileStyle
    core_execution_handlers_py["?? core/execution/handlers.py"]:::fileStyle
    core_execution_invariants_py["?? core/execution/invariants.py"]:::fileStyle
    core_execution_job_model_py["?? core/execution/job_model.py"]:::fileStyle
    core_execution_models_py["?? core/execution/models.py"]:::fileStyle
    core_execution_ports_py["?? core/execution/ports.py"]:::fileStyle
    core_execution_state_py["?? core/execution/state.py"]:::fileStyle
    core_execution_state_mapping_py["?? core/execution/state_mapping.py"]:::fileStyle
    core_execution___init___py["?? core/execution/__init__.py"]:::fileStyle
    core_healing_base_py["?? core/healing/base.py"]:::fileStyle
    core_healing_config_py["?? core/healing/config.py"]:::fileStyle
    core_healing_models_py["?? core/healing/models.py"]:::fileStyle
    core_healing_pipeline_py["?? core/healing/pipeline.py"]:::fileStyle
    core_healing_telemetry_py["?? core/healing/telemetry.py"]:::fileStyle
    core_healing_testing_factories_py["?? core/healing/testing_factories.py"]:::fileStyle
    core_healing___init___py["?? core/healing/__init__.py"]:::fileStyle
    core_healing_strategies_markdown_leakage_py["?? core/healing/strategies/markdown_leakage.py"]:::fileStyle
    core_healing_strategies_meta_text_leakage_py["?? core/healing/strategies/meta_text_leakage.py"]:::fileStyle
    core_healing_strategies_structural_py["?? core/healing/strategies/structural.py"]:::fileStyle
    core_metrics_exporters_py["?? core/metrics/exporters.py"]:::fileStyle
    core_metrics_measure_density_py["?? core/metrics/measure_density.py"]:::fileStyle
    core_metrics_metrics_py["?? core/metrics/metrics.py"]:::fileStyle
    core_metrics_pricing_py["?? core/metrics/pricing.py"]:::fileStyle
    core_metrics_summary_py["?? core/metrics/summary.py"]:::fileStyle
    core_normalization_html_decoder_py["?? core/normalization/html_decoder.py"]:::fileStyle
    core_normalization_latex_sanitizer_py["?? core/normalization/latex_sanitizer.py"]:::fileStyle
    core_normalization_normalizer_py["?? core/normalization/normalizer.py"]:::fileStyle
    core_normalization_unicode_py["?? core/normalization/unicode.py"]:::fileStyle
    core_pipeline_job_py["?? core/pipeline/job.py"]:::fileStyle
    core_pipeline_orchestrator_py["?? core/pipeline/orchestrator.py"]:::fileStyle
    core_pipeline_state_store_py["?? core/pipeline/state_store.py"]:::fileStyle
    core_pipeline___init___py["?? core/pipeline/__init__.py"]:::fileStyle
    core_resilience_circuit_breaker_py["?? core/resilience/circuit_breaker.py"]:::fileStyle
    core_utils_config_py["?? core/utils/config.py"]:::fileStyle
    core_utils_fs_py["?? core/utils/fs.py"]:::fileStyle
    core_utils_logger_py["?? core/utils/logger.py"]:::fileStyle
    core_utils_rate_limiter_py["?? core/utils/rate_limiter.py"]:::fileStyle
    core_utils_telemetry_py["?? core/utils/telemetry.py"]:::fileStyle
    core_utils_time_py["?? core/utils/time.py"]:::fileStyle
    core_utils___init___py["?? core/utils/__init__.py"]:::fileStyle
    core_validation_base_py["?? core/validation/base.py"]:::fileStyle
    core_validation_error_taxonomy_py["?? core/validation/error_taxonomy.py"]:::fileStyle
    core_validation_interfaces_py["?? core/validation/interfaces.py"]:::fileStyle
    core_validation_latex_validator_py["?? core/validation/latex_validator.py"]:::fileStyle
    core_validation_legacy_adapter_py["?? core/validation/legacy_adapter.py"]:::fileStyle
    core_validation_math_validator_py["?? core/validation/math_validator.py"]:::fileStyle
    core_validation_models_py["?? core/validation/models.py"]:::fileStyle
    core_validation_perimeter_py["?? core/validation/perimeter.py"]:::fileStyle
    core_validation_pipeline_py["?? core/validation/pipeline.py"]:::fileStyle
    core_validation_preservation_py["?? core/validation/preservation.py"]:::fileStyle
    core_validation_semantic_py["?? core/validation/semantic.py"]:::fileStyle
    core_validation_structural_validator_py["?? core/validation/structural_validator.py"]:::fileStyle
    core_validation_volumetric_py["?? core/validation/volumetric.py"]:::fileStyle
    core_validation___init___py["?? core/validation/__init__.py"]:::fileStyle
    infra_adapters_pdf_parser_py["?? infra/adapters/pdf_parser.py"]:::fileStyle
    infra_adapters___init___py["?? infra/adapters/__init__.py"]:::fileStyle
    infra_db_bootstrap_py["?? infra/db/bootstrap.py"]:::fileStyle
    infra_db_connection_py["?? infra/db/connection.py"]:::fileStyle
    infra_db_control_repo_py["?? infra/db/control_repo.py"]:::fileStyle
    infra_db_event_repo_py["?? infra/db/event_repo.py"]:::fileStyle
    infra_db_fsm_repository_py["?? infra/db/fsm_repository.py"]:::fileStyle
    infra_db_materialized_repo_py["?? infra/db/materialized_repo.py"]:::fileStyle
    infra_db_system_repo_py["?? infra/db/system_repo.py"]:::fileStyle
    infra_db___init___py["?? infra/db/__init__.py"]:::fileStyle
    infra_redis_queues_py["?? infra/redis/queues.py"]:::fileStyle
    infra_redis___init___py["?? infra/redis/__init__.py"]:::fileStyle
    runtime_engine_py["?? runtime/engine.py"]:::fileStyle
    runtime_reconciliation_py["?? runtime/reconciliation.py"]:::fileStyle
    runtime_recovery_py["?? runtime/recovery.py"]:::fileStyle
    runtime_resumer_py["?? runtime/resumer.py"]:::fileStyle
    runtime_sweeper_py["?? runtime/sweeper.py"]:::fileStyle
    runtime___init___py["?? runtime/__init__.py"]:::fileStyle
    tests_test_architecture_contract_py["?? tests/test_architecture_contract.py"]:::fileStyle
    tests_test_ast_py["?? tests/test_ast.py"]:::fileStyle
    tests_test_dag_py["?? tests/test_dag.py"]:::fileStyle
    tests_test_fencing_py["?? tests/test_fencing.py"]:::fileStyle
    tests_test_math_protector_py["?? tests/test_math_protector.py"]:::fileStyle
    tests_test_pipeline_py["?? tests/test_pipeline.py"]:::fileStyle
    tests_test_pipeline_fidelity_py["?? tests/test_pipeline_fidelity.py"]:::fileStyle
    tests_helpers_bootstrap_translation_golden_py["?? tests/helpers/bootstrap_translation_golden.py"]:::fileStyle
    tests_helpers_fakes_py["?? tests/helpers/fakes.py"]:::fileStyle
    tests_helpers_markdown_inspector_py["?? tests/helpers/markdown_inspector.py"]:::fileStyle
    tests_helpers___init___py["?? tests/helpers/__init__.py"]:::fileStyle
    tests_integration_test_chunker_snapshot_py["?? tests/integration/test_chunker_snapshot.py"]:::fileStyle
    tests_integration_test_cli_router_py["?? tests/integration/test_cli_router.py"]:::fileStyle
    tests_integration_test_e2e_walking_skeleton_py["?? tests/integration/test_e2e_walking_skeleton.py"]:::fileStyle
    tests_integration_test_embedding_smoke_py["?? tests/integration/test_embedding_smoke.py"]:::fileStyle
    tests_integration_test_golden_parser_py["?? tests/integration/test_golden_parser.py"]:::fileStyle
    tests_integration_test_healing_concurrency_py["?? tests/integration/test_healing_concurrency.py"]:::fileStyle
    tests_integration_test_healing_e2e_telemetry_py["?? tests/integration/test_healing_e2e_telemetry.py"]:::fileStyle
    tests_integration_test_pipeline_orchestration_py["?? tests/integration/test_pipeline_orchestration.py"]:::fileStyle
    tests_integration_test_real_e2e_py["?? tests/integration/test_real_e2e.py"]:::fileStyle
    tests_integration_test_real_paper_py["?? tests/integration/test_real_paper.py"]:::fileStyle
    tests_integration_test_real_parser_pipeline_py["?? tests/integration/test_real_parser_pipeline.py"]:::fileStyle
    tests_integration_test_recovery_flow_py["?? tests/integration/test_recovery_flow.py"]:::fileStyle
    tests_integration_test_translation_layer_py["?? tests/integration/test_translation_layer.py"]:::fileStyle
    tests_integration_test_translation_semantics_py["?? tests/integration/test_translation_semantics.py"]:::fileStyle
    tests_integration_test_translation_structure_py["?? tests/integration/test_translation_structure.py"]:::fileStyle
    tests_integration_test_translation_technical_py["?? tests/integration/test_translation_technical.py"]:::fileStyle
    tests_integration_test_validation_integration_py["?? tests/integration/test_validation_integration.py"]:::fileStyle
    tests_integration___init___py["?? tests/integration/__init__.py"]:::fileStyle
    tests_smoke_conftest_py["?? tests/smoke/conftest.py"]:::fileStyle
    tests_smoke_test_invariants_smoke_py["?? tests/smoke/test_invariants_smoke.py"]:::fileStyle
    tests_unit_test_assembler_py["?? tests/unit/test_assembler.py"]:::fileStyle
    tests_unit_test_cache_py["?? tests/unit/test_cache.py"]:::fileStyle
    tests_unit_test_dispatcher_py["?? tests/unit/test_dispatcher.py"]:::fileStyle
    tests_unit_test_dispatcher_validation_py["?? tests/unit/test_dispatcher_validation.py"]:::fileStyle
    tests_unit_test_healing_idempotency_py["?? tests/unit/test_healing_idempotency.py"]:::fileStyle
    tests_unit_test_legacy_adapter_py["?? tests/unit/test_legacy_adapter.py"]:::fileStyle
    tests_unit_test_perimeter_validator_py["?? tests/unit/test_perimeter_validator.py"]:::fileStyle
    tests_unit_test_preservation_validator_py["?? tests/unit/test_preservation_validator.py"]:::fileStyle
    tests_unit_test_pricing_engine_py["?? tests/unit/test_pricing_engine.py"]:::fileStyle
    tests_unit_test_resilience_py["?? tests/unit/test_resilience.py"]:::fileStyle
    tests_unit_test_semantic_chunker_py["?? tests/unit/test_semantic_chunker.py"]:::fileStyle
    tests_unit_test_semantic_validator_py["?? tests/unit/test_semantic_validator.py"]:::fileStyle
    tests_unit_test_structural_healing_py["?? tests/unit/test_structural_healing.py"]:::fileStyle
    tests_unit_test_structural_validator_py["?? tests/unit/test_structural_validator.py"]:::fileStyle
    tests_unit_test_summary_builder_py["?? tests/unit/test_summary_builder.py"]:::fileStyle
    tests_unit_test_validation_pipeline_py["?? tests/unit/test_validation_pipeline.py"]:::fileStyle
    tests_unit___init___py["?? tests/unit/__init__.py"]:::fileStyle
    tools_load_test_db_injector_py["?? tools/load_test/db_injector.py"]:::fileStyle
    tools_load_test_db_injector_variable_py["?? tools/load_test/db_injector_variable.py"]:::fileStyle
    tools_load_test_injector_py["?? tools/load_test/injector.py"]:::fileStyle
    tools_load_test_monitor_py["?? tools/load_test/monitor.py"]:::fileStyle

    apps_bootstrap_pipeline_factory_py --> core_compiler_assembler_py
    apps_bootstrap_pipeline_factory_py --> core_execution_handlers_py
    apps_bootstrap_pipeline_factory_py --> core_healing_config_py
    apps_bootstrap_pipeline_factory_py --> core_healing_pipeline_py
    apps_bootstrap_pipeline_factory_py --> core_healing_strategies_markdown_leakage_py
    apps_bootstrap_pipeline_factory_py --> core_healing_strategies_meta_text_leakage_py
    apps_bootstrap_pipeline_factory_py --> core_healing_strategies_structural_py
    apps_bootstrap_pipeline_factory_py --> core_metrics_summary_py
    apps_bootstrap_pipeline_factory_py --> core_pipeline_orchestrator_py
    apps_bootstrap_pipeline_factory_py --> core_pipeline_state_store_py
    apps_bootstrap_pipeline_factory_py --> core_validation_legacy_adapter_py
    apps_bootstrap_pipeline_factory_py --> core_validation_perimeter_py
    apps_bootstrap_pipeline_factory_py --> core_validation_pipeline_py
    apps_bootstrap_pipeline_factory_py --> core_validation_preservation_py
    apps_bootstrap_pipeline_factory_py --> core_validation_semantic_py
    apps_bootstrap_pipeline_factory_py --> core_validation_volumetric_py
    apps_bootstrap_pipeline_factory_py --> infra_adapters_pdf_parser_py
    apps_bootstrap_pipeline_factory_py --> infra_db_connection_py
    apps_bootstrap_pipeline_factory_py --> infra_db_fsm_repository_py
    apps_cli_main_py --> apps_bootstrap_pipeline_factory_py
    apps_cli_main_py --> apps_llm_workers_cache_py
    apps_cli_main_py --> apps_llm_workers_chunk_processor_py
    apps_cli_main_py --> apps_llm_workers_dispatcher_py
    apps_cli_main_py --> apps_llm_workers_gemini_client_py
    apps_cli_main_py --> apps_llm_workers_prompt_builder_py
    apps_cli_main_py --> apps_llm_workers_workers_py
    apps_cli_main_py --> apps_ocr_router___main___py
    apps_cli_main_py --> core_ast_hashing_py
    apps_cli_main_py --> core_ast_models_py
    apps_cli_main_py --> core_pipeline_job_py
    apps_cli_main_py --> core_pipeline_state_store_py
    apps_cli_main_py --> infra_db_connection_py
    apps_cli_main_py --> infra_db_fsm_repository_py
    apps_cli_main_py --> runtime_recovery_py
    apps_cli_main_py --> runtime_resumer_py
    apps_compiler___main___py --> apps_compiler_docker_runner_py
    apps_compiler___main___py --> apps_compiler_tex_builder_py
    apps_compiler___main___py --> apps_llm_workers_chunk_processor_py
    apps_compiler___main___py --> apps_ocr_router___main___py
    apps_compiler___main___py --> core_ast_registry_py
    apps_compiler___main___py --> core_execution_handlers_py
    apps_compiler___main___py --> core_execution_state_py
    apps_compiler___main___py --> core_utils_telemetry_py
    apps_compiler___main___py --> infra_db_connection_py
    apps_compiler___main___py --> infra_db_control_repo_py
    apps_compiler___main___py --> infra_db_fsm_repository_py
    apps_compiler___main___py --> infra_db_materialized_repo_py
    apps_compiler___main___py --> tests_integration_test_recovery_flow_py
    apps_compiler_docker_runner_py --> apps_ocr_router___main___py
    apps_compiler_sandbox_server_py --> apps_ocr_router___main___py
    apps_daemons_chaos_runner_py --> apps_llm_workers_chunk_processor_py
    apps_daemons_chaos_runner_py --> infra_db_control_repo_py
    apps_daemons_chaos_runner_py --> infra_db_fsm_repository_py
    apps_daemons_fake_gemini_py --> core_metrics_metrics_py
    apps_daemons_reconciler_py --> apps_llm_workers_chunk_processor_py
    apps_daemons_reconciler_py --> apps_ocr_router___main___py
    apps_daemons_reconciler_py --> core_execution_handlers_py
    apps_daemons_reconciler_py --> core_execution_state_py
    apps_daemons_reconciler_py --> core_metrics_metrics_py
    apps_daemons_reconciler_py --> core_utils_telemetry_py
    apps_daemons_reconciler_py --> infra_db_connection_py
    apps_daemons_reconciler_py --> infra_db_control_repo_py
    apps_daemons_reconciler_py --> infra_db_event_repo_py
    apps_daemons_reconciler_py --> infra_db_fsm_repository_py
    apps_daemons_reconciler_py --> infra_db_materialized_repo_py
    apps_daemons_reconciler_py --> infra_db_system_repo_py
    apps_llm_workers___main___py --> apps_llm_workers_chunk_processor_py
    apps_llm_workers___main___py --> apps_llm_workers_gemini_client_py
    apps_llm_workers___main___py --> apps_ocr_router___main___py
    apps_llm_workers___main___py --> core_ast_registry_py
    apps_llm_workers___main___py --> core_execution_exceptions_py
    apps_llm_workers___main___py --> core_metrics_metrics_py
    apps_llm_workers___main___py --> core_utils_telemetry_py
    apps_llm_workers___main___py --> infra_db_connection_py
    apps_llm_workers___main___py --> infra_db_control_repo_py
    apps_llm_workers___main___py --> infra_db_event_repo_py
    apps_llm_workers___main___py --> infra_db_materialized_repo_py
    apps_llm_workers___main___py --> tests_unit_test_semantic_chunker_py
    apps_llm_workers_cache_py --> apps_llm_workers_chunk_processor_py
    apps_llm_workers_chunk_processor_py --> apps_llm_workers_gemini_client_py
    apps_llm_workers_chunk_processor_py --> apps_llm_workers_router_translation_py
    apps_llm_workers_chunk_processor_py --> core_metrics_metrics_py
    apps_llm_workers_dispatcher_py --> apps_llm_workers_gemini_client_py
    apps_llm_workers_dispatcher_py --> core_ast_models_py
    apps_llm_workers_dispatcher_py --> core_execution_exceptions_py
    apps_llm_workers_dispatcher_py --> core_healing_models_py
    apps_llm_workers_dispatcher_py --> core_healing_pipeline_py
    apps_llm_workers_dispatcher_py --> core_validation_legacy_adapter_py
    apps_llm_workers_dispatcher_py --> core_validation_models_py
    apps_llm_workers_dispatcher_py --> core_validation_perimeter_py
    apps_llm_workers_dispatcher_py --> core_validation_pipeline_py
    apps_llm_workers_dispatcher_py --> core_validation_preservation_py
    apps_llm_workers_dispatcher_py --> core_validation_semantic_py
    apps_llm_workers_dispatcher_py --> core_validation_volumetric_py
    apps_llm_workers_dispatcher_py --> tests_unit_test_healing_idempotency_py
    apps_llm_workers_gemini_client_py --> apps_llm_workers_prompt_builder_py
    apps_llm_workers_gemini_client_py --> core_ast_models_py
    apps_llm_workers_gemini_client_py --> core_execution_exceptions_py
    apps_llm_workers_gemini_client_py --> core_resilience_circuit_breaker_py
    apps_llm_workers_gemini_client_py --> core_utils_rate_limiter_py
    apps_llm_workers_gemini_client_py --> tests_integration_test_recovery_flow_py
    apps_llm_workers_resilience_py --> apps_llm_workers_gemini_client_py
    apps_llm_workers_workers_py --> core_ast_models_py
    apps_llm_workers_workers_py --> tests_integration_test_recovery_flow_py
    apps_ocr_router___main___py --> apps_llm_workers_chunk_processor_py
    apps_ocr_router___main___py --> core_ast_hashing_py
    apps_ocr_router___main___py --> core_ast_models_py
    apps_ocr_router___main___py --> core_ast_parser_py
    apps_ocr_router___main___py --> core_ast_registry_py
    apps_ocr_router___main___py --> core_execution_handlers_py
    apps_ocr_router___main___py --> core_execution_state_py
    apps_ocr_router___main___py --> core_utils_telemetry_py
    apps_ocr_router___main___py --> infra_db_connection_py
    apps_ocr_router___main___py --> infra_db_control_repo_py
    apps_ocr_router___main___py --> infra_db_fsm_repository_py
    core_ast_hashing_py --> core_ast_models_py
    core_ast_parser_py --> apps_compiler_docker_runner_py
    core_ast_parser_py --> core_ast_models_py
    core_ast_parser_py --> core_ast_router_py
    core_ast_parser_py --> core_ast_segmenter_py
    core_ast_parser_py --> core_pipeline_state_store_py
    core_ast_registry_py --> core_pipeline_state_store_py
    core_ast_segmenter_py --> apps_compiler_docker_runner_py
    core_ast_validator_py --> apps_compiler_docker_runner_py
    core_compiler_assembler_py --> core_ast_models_py
    core_compiler_assembler_py --> core_execution_exceptions_py
    core_execution_exceptions_py --> tests_unit_test_dispatcher_validation_py
    core_execution_handlers_py --> core_execution_state_py
    core_execution_handlers_py --> core_metrics_metrics_py
    core_execution_handlers_py --> infra_db_control_repo_py
    core_execution_handlers_py --> infra_db_event_repo_py
    core_execution_handlers_py --> infra_db_fsm_repository_py
    core_execution_handlers_py --> infra_db_materialized_repo_py
    core_execution_handlers_py --> infra_db_system_repo_py
    core_execution_handlers_py --> tests_unit_test_semantic_chunker_py
    core_execution_handlers_py --> tests_unit_test_validation_pipeline_py
    core_execution_state_py --> core_execution_exceptions_py
    core_healing_pipeline_py --> core_healing_models_py
    core_healing_pipeline_py --> core_healing_strategies_structural_py
    core_healing_pipeline_py --> core_healing_telemetry_py
    core_healing_pipeline_py --> tests_unit_test_healing_idempotency_py
    core_healing_strategies_markdown_leakage_py --> apps_compiler_docker_runner_py
    core_healing_strategies_markdown_leakage_py --> core_healing_models_py
    core_healing_strategies_meta_text_leakage_py --> apps_compiler_docker_runner_py
    core_healing_strategies_meta_text_leakage_py --> core_healing_models_py
    core_healing_strategies_structural_py --> apps_compiler_docker_runner_py
    core_healing_strategies_structural_py --> core_healing_config_py
    core_healing_strategies_structural_py --> core_healing_models_py
    core_healing_testing_factories_py --> core_healing_models_py
    core_healing_testing_factories_py --> core_validation_models_py
    core_metrics_summary_py --> core_metrics_pricing_py
    core_normalization_latex_sanitizer_py --> apps_compiler_docker_runner_py
    core_normalization_normalizer_py --> tests_unit_test_semantic_chunker_py
    core_pipeline_orchestrator_py --> core_ast_hashing_py
    core_pipeline_orchestrator_py --> core_pipeline_job_py
    core_pipeline_orchestrator_py --> core_pipeline_state_store_py
    core_pipeline_orchestrator_py --> tests_integration_test_recovery_flow_py
    core_pipeline_state_store_py --> core_execution_handlers_py
    core_pipeline_state_store_py --> core_execution_state_mapping_py
    core_pipeline_state_store_py --> core_execution_state_py
    core_pipeline_state_store_py --> infra_db_fsm_repository_py
    core_resilience_circuit_breaker_py --> core_execution_exceptions_py
    core_validation_legacy_adapter_py --> core_validation_models_py
    core_validation_legacy_adapter_py --> tests_unit_test_validation_pipeline_py
    core_validation_perimeter_py --> apps_compiler_docker_runner_py
    core_validation_perimeter_py --> core_validation_models_py
    core_validation_pipeline_py --> tests_unit_test_validation_pipeline_py
    core_validation_preservation_py --> apps_compiler_docker_runner_py
    core_validation_preservation_py --> core_validation_models_py
    core_validation_semantic_py --> apps_compiler_docker_runner_py
    core_validation_semantic_py --> core_validation_models_py
    core_validation_structural_validator_py --> core_execution_models_py
    core_validation_volumetric_py --> core_validation_models_py
    infra_db_bootstrap_py --> apps_llm_workers_chunk_processor_py
    infra_db_bootstrap_py --> infra_db_connection_py
    infra_db_connection_py --> apps_llm_workers_chunk_processor_py
    infra_db_control_repo_py --> apps_llm_workers_chunk_processor_py
    infra_db_control_repo_py --> core_execution_exceptions_py
    infra_db_control_repo_py --> core_execution_ports_py
    infra_db_event_repo_py --> apps_llm_workers_chunk_processor_py
    infra_db_event_repo_py --> core_execution_ports_py
    infra_db_fsm_repository_py --> apps_llm_workers_chunk_processor_py
    infra_db_fsm_repository_py --> core_execution_exceptions_py
    infra_db_materialized_repo_py --> apps_llm_workers_chunk_processor_py
    infra_db_materialized_repo_py --> core_execution_ports_py
    infra_db_system_repo_py --> apps_llm_workers_chunk_processor_py
    runtime_reconciliation_py --> apps_llm_workers_chunk_processor_py
    runtime_reconciliation_py --> core_execution_handlers_py
    runtime_reconciliation_py --> core_execution_state_py
    runtime_reconciliation_py --> core_metrics_metrics_py
    runtime_reconciliation_py --> core_utils_telemetry_py
    runtime_reconciliation_py --> infra_db_connection_py
    runtime_reconciliation_py --> infra_db_control_repo_py
    runtime_reconciliation_py --> infra_db_event_repo_py
    runtime_reconciliation_py --> infra_db_materialized_repo_py
    runtime_reconciliation_py --> infra_db_system_repo_py
    runtime_recovery_py --> core_execution_handlers_py
    runtime_recovery_py --> core_execution_state_py
    runtime_recovery_py --> core_utils_telemetry_py
    runtime_recovery_py --> infra_db_connection_py
    runtime_recovery_py --> infra_db_fsm_repository_py
    runtime_resumer_py --> core_execution_handlers_py
    runtime_resumer_py --> core_execution_state_py
    runtime_resumer_py --> infra_db_connection_py
    runtime_resumer_py --> infra_db_fsm_repository_py
    runtime_sweeper_py --> apps_llm_workers_chunk_processor_py
    runtime_sweeper_py --> core_execution_handlers_py
    runtime_sweeper_py --> core_execution_state_py
    runtime_sweeper_py --> core_utils_logger_py
    runtime_sweeper_py --> infra_db_connection_py
    runtime_sweeper_py --> infra_db_control_repo_py
    runtime_sweeper_py --> infra_db_fsm_repository_py
    tests_helpers_bootstrap_translation_golden_py --> apps_bootstrap_pipeline_factory_py
    tests_helpers_bootstrap_translation_golden_py --> apps_llm_workers_chunk_processor_py
    tests_helpers_bootstrap_translation_golden_py --> apps_ocr_router___main___py
    tests_helpers_bootstrap_translation_golden_py --> core_pipeline_job_py
    tests_helpers_bootstrap_translation_golden_py --> tests_helpers_markdown_inspector_py
    tests_helpers_bootstrap_translation_golden_py --> tests_integration_test_pipeline_orchestration_py
    tests_helpers_fakes_py --> core_ast_models_py
    tests_integration_test_chunker_snapshot_py --> core_ast_hashing_py
    tests_integration_test_chunker_snapshot_py --> core_ast_models_py
    tests_integration_test_chunker_snapshot_py --> core_pipeline_state_store_py
    tests_integration_test_cli_router_py --> apps_cli_main_py
    tests_integration_test_e2e_walking_skeleton_py --> apps_llm_workers_cache_py
    tests_integration_test_e2e_walking_skeleton_py --> apps_llm_workers_dispatcher_py
    tests_integration_test_e2e_walking_skeleton_py --> apps_llm_workers_resilience_py
    tests_integration_test_e2e_walking_skeleton_py --> apps_llm_workers_workers_py
    tests_integration_test_e2e_walking_skeleton_py --> core_ast_models_py
    tests_integration_test_e2e_walking_skeleton_py --> core_compiler_assembler_py
    tests_integration_test_e2e_walking_skeleton_py --> core_pipeline_state_store_py
    tests_integration_test_e2e_walking_skeleton_py --> core_validation_pipeline_py
    tests_integration_test_e2e_walking_skeleton_py --> tests_integration_test_recovery_flow_py
    tests_integration_test_embedding_smoke_py --> apps_llm_workers_gemini_client_py
    tests_integration_test_golden_parser_py --> core_pipeline_state_store_py
    tests_integration_test_golden_parser_py --> infra_adapters_pdf_parser_py
    tests_integration_test_golden_parser_py --> tests_integration_test_recovery_flow_py
    tests_integration_test_healing_concurrency_py --> apps_ocr_router___main___py
    tests_integration_test_healing_concurrency_py --> core_healing_models_py
    tests_integration_test_healing_concurrency_py --> core_healing_pipeline_py
    tests_integration_test_healing_concurrency_py --> core_healing_strategies_structural_py
    tests_integration_test_healing_concurrency_py --> core_healing_telemetry_py
    tests_integration_test_healing_concurrency_py --> core_validation_models_py
    tests_integration_test_healing_concurrency_py --> tests_unit_test_dispatcher_validation_py
    tests_integration_test_healing_e2e_telemetry_py --> core_healing_models_py
    tests_integration_test_healing_e2e_telemetry_py --> core_healing_pipeline_py
    tests_integration_test_healing_e2e_telemetry_py --> core_healing_strategies_markdown_leakage_py
    tests_integration_test_healing_e2e_telemetry_py --> core_healing_strategies_structural_py
    tests_integration_test_healing_e2e_telemetry_py --> core_healing_telemetry_py
    tests_integration_test_healing_e2e_telemetry_py --> core_validation_models_py
    tests_integration_test_healing_e2e_telemetry_py --> tests_unit_test_dispatcher_validation_py
    tests_integration_test_pipeline_orchestration_py --> apps_bootstrap_pipeline_factory_py
    tests_integration_test_pipeline_orchestration_py --> apps_llm_workers_chunk_processor_py
    tests_integration_test_pipeline_orchestration_py --> core_ast_models_py
    tests_integration_test_pipeline_orchestration_py --> core_execution_handlers_py
    tests_integration_test_pipeline_orchestration_py --> core_pipeline_job_py
    tests_integration_test_pipeline_orchestration_py --> core_pipeline_state_store_py
    tests_integration_test_pipeline_orchestration_py --> infra_db_fsm_repository_py
    tests_integration_test_real_e2e_py --> apps_bootstrap_pipeline_factory_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_cache_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_chunk_processor_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_dispatcher_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_gemini_client_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_prompt_builder_py
    tests_integration_test_real_e2e_py --> apps_llm_workers_workers_py
    tests_integration_test_real_e2e_py --> core_ast_models_py
    tests_integration_test_real_e2e_py --> core_pipeline_job_py
    tests_integration_test_real_paper_py --> apps_cli_main_py
    tests_integration_test_real_paper_py --> core_ast_parser_py
    tests_integration_test_real_paper_py --> core_ast_validator_py
    tests_integration_test_real_paper_py --> tests_unit_test_validation_pipeline_py
    tests_integration_test_real_parser_pipeline_py --> infra_adapters_pdf_parser_py
    tests_integration_test_real_parser_pipeline_py --> tests_integration_test_recovery_flow_py
    tests_integration_test_recovery_flow_py --> apps_cli_main_py
    tests_integration_test_recovery_flow_py --> apps_llm_workers_chunk_processor_py
    tests_integration_test_recovery_flow_py --> apps_ocr_router___main___py
    tests_integration_test_recovery_flow_py --> core_ast_models_py
    tests_integration_test_recovery_flow_py --> core_execution_handlers_py
    tests_integration_test_recovery_flow_py --> core_metrics_summary_py
    tests_integration_test_recovery_flow_py --> core_pipeline_job_py
    tests_integration_test_recovery_flow_py --> core_pipeline_orchestrator_py
    tests_integration_test_recovery_flow_py --> core_pipeline_state_store_py
    tests_integration_test_recovery_flow_py --> infra_db_connection_py
    tests_integration_test_recovery_flow_py --> infra_db_fsm_repository_py
    tests_integration_test_recovery_flow_py --> runtime_recovery_py
    tests_integration_test_recovery_flow_py --> runtime_resumer_py
    tests_integration_test_translation_layer_py --> apps_llm_workers_cache_py
    tests_integration_test_translation_layer_py --> apps_llm_workers_dispatcher_py
    tests_integration_test_translation_layer_py --> apps_llm_workers_resilience_py
    tests_integration_test_translation_layer_py --> apps_llm_workers_workers_py
    tests_integration_test_translation_layer_py --> core_ast_models_py
    tests_integration_test_translation_layer_py --> core_compiler_assembler_py
    tests_integration_test_translation_layer_py --> tests_integration_test_recovery_flow_py
    tests_integration_test_translation_semantics_py --> apps_bootstrap_pipeline_factory_py
    tests_integration_test_translation_semantics_py --> apps_llm_workers_cache_py
    tests_integration_test_translation_semantics_py --> apps_llm_workers_dispatcher_py
    tests_integration_test_translation_semantics_py --> apps_llm_workers_gemini_client_py
    tests_integration_test_translation_semantics_py --> apps_llm_workers_prompt_builder_py
    tests_integration_test_translation_semantics_py --> apps_llm_workers_workers_py
    tests_integration_test_translation_semantics_py --> core_ast_models_py
    tests_integration_test_translation_semantics_py --> core_pipeline_state_store_py
    tests_integration_test_translation_semantics_py --> tests_integration_test_pipeline_orchestration_py
    tests_integration_test_translation_semantics_py --> tests_integration_test_recovery_flow_py
    tests_integration_test_translation_structure_py --> apps_bootstrap_pipeline_factory_py
    tests_integration_test_translation_structure_py --> apps_llm_workers_chunk_processor_py
    tests_integration_test_translation_structure_py --> core_execution_handlers_py
    tests_integration_test_translation_structure_py --> core_pipeline_job_py
    tests_integration_test_translation_structure_py --> core_pipeline_state_store_py
    tests_integration_test_translation_structure_py --> infra_db_fsm_repository_py
    tests_integration_test_translation_structure_py --> tests_helpers_markdown_inspector_py
    tests_integration_test_translation_structure_py --> tests_integration_test_pipeline_orchestration_py
    tests_integration_test_translation_technical_py --> apps_bootstrap_pipeline_factory_py
    tests_integration_test_translation_technical_py --> apps_llm_workers_chunk_processor_py
    tests_integration_test_translation_technical_py --> core_execution_handlers_py
    tests_integration_test_translation_technical_py --> core_pipeline_job_py
    tests_integration_test_translation_technical_py --> core_pipeline_state_store_py
    tests_integration_test_translation_technical_py --> infra_db_fsm_repository_py
    tests_integration_test_translation_technical_py --> tests_helpers_markdown_inspector_py
    tests_integration_test_translation_technical_py --> tests_integration_test_pipeline_orchestration_py
    tests_integration_test_validation_integration_py --> apps_llm_workers_dispatcher_py
    tests_integration_test_validation_integration_py --> core_ast_models_py
    tests_smoke_conftest_py --> core_validation_legacy_adapter_py
    tests_smoke_conftest_py --> core_validation_perimeter_py
    tests_smoke_conftest_py --> core_validation_pipeline_py
    tests_smoke_conftest_py --> core_validation_preservation_py
    tests_smoke_conftest_py --> core_validation_semantic_py
    tests_smoke_conftest_py --> core_validation_volumetric_py
    tests_smoke_test_invariants_smoke_py --> core_validation_models_py
    tests_smoke_test_invariants_smoke_py --> core_validation_pipeline_py
    tests_smoke_test_invariants_smoke_py --> tests_unit_test_healing_idempotency_py
    tests_test_architecture_contract_py --> infra_db_control_repo_py
    tests_test_architecture_contract_py --> infra_db_event_repo_py
    tests_test_architecture_contract_py --> infra_db_materialized_repo_py
    tests_test_math_protector_py --> core_normalization_latex_sanitizer_py
    tests_test_pipeline_fidelity_py --> apps_cli_main_py
    tests_test_pipeline_fidelity_py --> core_ast_parser_py
    tests_test_pipeline_fidelity_py --> core_normalization_latex_sanitizer_py
    tests_unit_test_assembler_py --> core_ast_models_py
    tests_unit_test_assembler_py --> core_compiler_assembler_py
    tests_unit_test_assembler_py --> tests_integration_test_recovery_flow_py
    tests_unit_test_cache_py --> apps_llm_workers_cache_py
    tests_unit_test_dispatcher_py --> apps_llm_workers_dispatcher_py
    tests_unit_test_dispatcher_py --> core_ast_models_py
    tests_unit_test_dispatcher_validation_py --> apps_llm_workers_dispatcher_py
    tests_unit_test_dispatcher_validation_py --> core_ast_models_py
    tests_unit_test_dispatcher_validation_py --> core_validation_models_py
    tests_unit_test_dispatcher_validation_py --> core_validation_pipeline_py
    tests_unit_test_healing_idempotency_py --> core_healing_pipeline_py
    tests_unit_test_healing_idempotency_py --> core_healing_strategies_markdown_leakage_py
    tests_unit_test_healing_idempotency_py --> core_healing_strategies_meta_text_leakage_py
    tests_unit_test_healing_idempotency_py --> core_healing_strategies_structural_py
    tests_unit_test_healing_idempotency_py --> core_healing_testing_factories_py
    tests_unit_test_healing_idempotency_py --> core_validation_models_py
    tests_unit_test_legacy_adapter_py --> core_execution_models_py
    tests_unit_test_legacy_adapter_py --> core_validation_legacy_adapter_py
    tests_unit_test_legacy_adapter_py --> core_validation_models_py
    tests_unit_test_legacy_adapter_py --> tests_unit_test_validation_pipeline_py
    tests_unit_test_perimeter_validator_py --> core_validation_models_py
    tests_unit_test_perimeter_validator_py --> core_validation_perimeter_py
    tests_unit_test_perimeter_validator_py --> tests_unit_test_validation_pipeline_py
    tests_unit_test_preservation_validator_py --> core_validation_models_py
    tests_unit_test_preservation_validator_py --> core_validation_preservation_py
    tests_unit_test_preservation_validator_py --> tests_unit_test_validation_pipeline_py
    tests_unit_test_pricing_engine_py --> core_metrics_pricing_py
    tests_unit_test_resilience_py --> apps_llm_workers_gemini_client_py
    tests_unit_test_resilience_py --> apps_llm_workers_resilience_py
    tests_unit_test_resilience_py --> core_ast_models_py
    tests_unit_test_resilience_py --> core_execution_exceptions_py
    tests_unit_test_semantic_chunker_py --> core_ast_hashing_py
    tests_unit_test_semantic_chunker_py --> core_ast_models_py
    tests_unit_test_semantic_validator_py --> core_validation_models_py
    tests_unit_test_semantic_validator_py --> core_validation_semantic_py
    tests_unit_test_semantic_validator_py --> tests_unit_test_validation_pipeline_py
    tests_unit_test_structural_healing_py --> core_healing_config_py
    tests_unit_test_structural_healing_py --> core_healing_strategies_structural_py
    tests_unit_test_structural_healing_py --> core_healing_testing_factories_py
    tests_unit_test_structural_validator_py --> core_validation_structural_validator_py
    tests_unit_test_summary_builder_py --> core_ast_models_py
    tests_unit_test_summary_builder_py --> tests_integration_test_recovery_flow_py
    tests_unit_test_validation_pipeline_py --> core_validation_models_py
    tests_unit_test_validation_pipeline_py --> core_validation_pipeline_py
    tests_unit_test_validation_pipeline_py --> tests_unit_test_healing_idempotency_py
    tools_load_test_db_injector_variable_py --> apps_llm_workers_chunk_processor_py
    tools_load_test_db_injector_variable_py --> infra_db_control_repo_py
```