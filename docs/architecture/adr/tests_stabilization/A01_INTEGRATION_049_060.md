# A-01 — Censo integración 49–60 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 12 módulos; 29 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_pdf_pdf_sqlite_contracts.py` | 2 | DB/tmp | core.execution.handlers, core.execution.state, infra.db.connection, infra.db.control_repo |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py` | 7 | DB/tmp | core.execution.exceptions, core.execution.handlers, core.execution.state, infra.db.connection |
| `tests/integration/test_pipeline_orchestration.py` | 1 | mock,I/O,DB/tmp | core.ast.models, core.ast.enums, core.ast.builder, core.pipeline.job |
| `tests/integration/test_pymupdf_extraction_integrity.py` | 3 | DB/tmp | core.execution.exceptions, core.layout.classification, infra.extraction.providers.pymupdf_provider |
| `tests/integration/test_real_e2e.py` | 1 | mock,DB/tmp | core.ast.models, core.pipeline.job, apps.llm_workers.prompt_builder, apps.llm_workers.rate_limiter |
| `tests/integration/test_real_paper.py` | 1 | — | core.ast.validator, apps.bootstrap.pipeline_factory |
| `tests/integration/test_real_parser_pipeline.py` | 1 | mock,I/O | apps.bootstrap.pipeline_factory, core.ast.models, core.ast.enums, core.ast.builder |
| `tests/integration/test_recovery_flow.py` | 1 | mock,I/O | infra.db.connection, infra.db.fsm_repository, core.execution.handlers, core.pipeline.job |
| `tests/integration/test_regression_entry_point.py` | 9 | mock,DB/tmp | core.ast.enums, core.ast.models, core.benchmark.corpus.enums, core.benchmark.corpus.models |
| `tests/integration/test_translation_layer.py` | 1 | mock,I/O | core.ast.models, core.compiler.assembler, apps.llm_workers.prompt_builder, apps.llm_workers.rate_limiter |
| `tests/integration/test_translation_semantics.py` | 1 | mock,DB/tmp,skip | apps.llm_workers.prompt_builder, core.ast.models, apps.llm_workers.rate_limiter, apps.llm_workers.sync_bridge |
| `tests/integration/test_translation_structure.py` | 1 | DB/tmp,skip | core.pipeline.job, core.pipeline.orchestrator, infra.db.fsm_repository, core.execution.handlers |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_pdf_pdf_sqlite_contracts.py:71` | `test_ocr_handoff_fsm_is_durable_when_connections_close` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_contracts.py:103` | `test_scheduler_reuses_attached_fsm_database` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:57` | `test_initialize_is_durable_without_caller_commit` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:68` | `test_each_fsm_command_is_durable_on_separate_reopen` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:89` | `test_wrong_cas_rolls_back_without_state_mutation` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:104` | `test_scheduler_repeated_queries_do_not_detach_factory_alias` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:121` | `test_existing_alias_to_wrong_fsm_fails_closed` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:135` | `test_unprepared_connection_attaches_once_and_keeps_alias` | ? | ? | ? |
| `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py:148` | `test_absent_fsm_rejected_without_creating_database` | ? | ? | ? |
| `tests/integration/test_pipeline_orchestration.py:119` | `test_pipeline_executes_successfully_with_real_pdf_source` | ? | ? | ? |
| `tests/integration/test_pymupdf_extraction_integrity.py:22` | `test_text_only_pdf_remains_extractable` | integration | ? | ? |
| `tests/integration/test_pymupdf_extraction_integrity.py:31` | `test_real_embedded_image_is_preserved_as_asset` | integration | ? | ? |
| `tests/integration/test_pymupdf_extraction_integrity.py:49` | `test_real_vector_drawing_rejected_before_layout_ast` | integration | ? | ? |
| `tests/integration/test_real_e2e.py:146` | `test_real_pipeline_execution_spends_and_audits_money` | ? | ? | ? |
| `tests/integration/test_real_paper.py:31` | `test_parser_and_validation_e2e_local` | ? | ? | ? |
| `tests/integration/test_real_parser_pipeline.py:20` | `test_parser_adapter_extracts_and_verifies_structural_presence` | ? | ? | ? |
| `tests/integration/test_recovery_flow.py:46` | `test_complete_crash_recovery_and_resume_lifecycle` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:279` | `test_exit_code_pass_when_all_pass` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:292` | `test_exit_code_warning_when_any_warning` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:305` | `test_exit_code_hard_fail_when_any_hard_fail` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:322` | `test_fail_fast_on_incomplete_baseline` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:388` | `test_report_files_created` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:418` | `test_deterministic_report` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:455` | `test_required_args` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:474` | `test_inject_timestamp_flag` | ? | ? | ? |
| `tests/integration/test_regression_entry_point.py:491` | `test_custom_output_dir` | ? | ? | ? |
| `tests/integration/test_translation_layer.py:101` | `test_translation_layer_flow` | ? | ? | ? |
| `tests/integration/test_translation_semantics.py:101` | `test_chunk_semantic_similarity_bypass_cache` | ? | ? | posible |
| `tests/integration/test_translation_structure.py:55` | `test_structural_integrity_against_golden_snapshot` | ? | ? | posible |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
