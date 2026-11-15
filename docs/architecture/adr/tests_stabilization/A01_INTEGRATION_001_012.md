# A-01 — Censo integración 1–12 (estático)

Base `d638c35af2311fb05679aadee375ac2ac0450561`. **No se ejecutó código ni se verificó colección.** 12 módulos; 48 declaraciones de funciones `test_*`. Marcadores/parametrizaciones “?” son **desconocidos**, no ausentes. Indicadores I/O y mock son coincidencias sintácticas.

| Archivo | Declaraciones | Señales inspeccionadas | Imports productivos (no certifican SUT) |
|---|---:|---|---|
| `tests/integration/test_add_document_to_corpus.py` | 4 | I/O,DB/tmp | core.benchmark.corpus.services, core.shared.errors, core.benchmark.corpus.models |
| `tests/integration/test_b022_image_staging.py` | 5 | mock,I/O,DB/tmp,externo | apps.compiler.tectonic_runner, core.compiler.rendering.models, core.compiler.rendering.image_assets |
| `tests/integration/test_b023_raster_image_pipeline.py` | 3 | DB/tmp | apps.bootstrap.pipeline_factory, core.ast.enums, core.ast.hashing, core.ast.models |
| `tests/integration/test_b024_g3_g5_math_roundtrip.py` | 2 | — | core.normalization.latex_sanitizer, core.compiler.rendering.implementations, core.compiler.rendering.models, core.ast.enums |
| `tests/integration/test_b025_math_visual_preservation.py` | 2 | DB/tmp | apps.bootstrap.pipeline_factory, core.ast.enums, core.ast.models, core.ast.hashing |
| `tests/integration/test_b03_foreground_pdf_product.py` | 14 | mock,I/O,DB/tmp | apps.cli.pdf_inbox, apps.cli, infra.db |
| `tests/integration/test_baseline_gt_preconditions.py` | 4 | I/O,DB/tmp | core.ast.enums, core.ast.models, core.benchmark.corpus.enums, core.benchmark.corpus.integrity |
| `tests/integration/test_baseline_integrity_exit_code.py` | 1 | mock,I/O,DB/tmp | core.benchmark.corpus.integrity, core.benchmark.verification.outcome |
| `tests/integration/test_baseline_materialization.py` | 6 | I/O,DB/tmp | core.benchmark.corpus.enums, core.benchmark.corpus.models |
| `tests/integration/test_baseline_physical_integrity.py` | 4 | I/O,DB/tmp | core.benchmark.corpus.enums, core.benchmark.corpus.integrity, core.benchmark.corpus.models, core.benchmark.corpus.services |
| `tests/integration/test_benchmark_orchestration_integration.py` | 2 | mock,externo | core.benchmark.models, core.benchmark.orchestrator, core.benchmark.ports, core.benchmark.types |
| `tests/integration/test_c3_t05_process_boundary.py` | 1 | DB/tmp,externo | core.ast.enums, core.ast.models, core.chunking.contextual_plan, infra.db.context_snapshot_repo |

| Archivo:línea | Caso declarado | Marcador cercano aproximado | Parametrize declarado | Skip/Xfail |
|---|---|---|---|---|
| `tests/integration/test_add_document_to_corpus.py:53` | `test_duplicate_doc_id_raises` | ? | ? | ? |
| `tests/integration/test_add_document_to_corpus.py:67` | `test_duplicate_sha256_raises` | ? | ? | ? |
| `tests/integration/test_add_document_to_corpus.py:99` | `test_same_corpus_version_raises` | ? | ? | ? |
| `tests/integration/test_add_document_to_corpus.py:113` | `test_preserves_sealed_entry_and_recalculates_hash` | ? | ? | ? |
| `tests/integration/test_b022_image_staging.py:30` | `test_stage_copies_digest_verified_bytes_and_deduplicates` | integration | ? | ? |
| `tests/integration/test_b022_image_staging.py:39` | `test_staging_detects_tampered_bytes` | integration | ? | ? |
| `tests/integration/test_b022_image_staging.py:48` | `test_staging_detects_missing_asset` | integration | ? | ? |
| `tests/integration/test_b022_image_staging.py:58` | `test_runner_stages_files_for_tectonic_without_real_compiler` | integration | ? | ? |
| `tests/integration/test_b022_image_staging.py:84` | `test_runner_refuses_tampering_before_compiler` | integration | ? | ? |
| `tests/integration/test_b023_raster_image_pipeline.py:49` | `test_raster_survives_ast_plan_preserve_and_g5_staging` | integration | ? | ? |
| `tests/integration/test_b023_raster_image_pipeline.py:109` | `test_repeated_raster_uses_one_asset_and_distinct_ast_nodes` | integration | ? | ? |
| `tests/integration/test_b023_raster_image_pipeline.py:119` | `test_vector_is_still_blocked_before_persisting_image` | integration | ? | ? |
| `tests/integration/test_b024_g3_g5_math_roundtrip.py:18` | `test_mask_restore_render_preserves_all_math_bytes` | integration | sí? | ? |
| `tests/integration/test_b024_g3_g5_math_roundtrip.py:27` | `test_mathematical_delimiter_error_prevents_render` | integration | ? | ? |
| `tests/integration/test_b025_math_visual_preservation.py:40` | `test_dedicated_math_font_survives_as_visual_preserve` | integration | ? | ? |
| `tests/integration/test_b025_math_visual_preservation.py:84` | `test_no_visual_fallback_when_image_writing_disabled` | integration | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:58` | `test_foreground_runs_ocr_g3_g5_then_requires_published_pdf` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:67` | `test_foreground_resumes_processing_without_repeat_ocr` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:73` | `test_foreground_resumes_ready_for_assembly_without_llm` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:79` | `test_foreground_fails_after_ocr_error_no_false_success` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:86` | `test_foreground_fails_on_incomplete_g3_before_g5` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:93` | `test_foreground_fails_when_g5_did_not_publish` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:100` | `test_foreground_rejects_unrelated_state_without_work` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:107` | `test_foreground_rejects_invalid_document_id` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:115` | `test_foreground_requires_pdf_header_even_when_fsm_completed` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:124` | `test_preflight_rejects_custom_inbox_before_io` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:130` | `test_preflight_rejects_missing_sqlite_without_creating_files` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:141` | `test_preflight_rejects_missing_compiler` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:154` | `test_g3_exception_is_operational_error` | ? | ? | ? |
| `tests/integration/test_b03_foreground_pdf_product.py:164` | `test_g5_exception_is_operational_error` | ? | ? | ? |
| `tests/integration/test_baseline_gt_preconditions.py:60` | `test_passes_with_valid_gt` | integration | ? | ? |
| `tests/integration/test_baseline_gt_preconditions.py:72` | `test_raises_on_missing_gt` | ? | ? | ? |
| `tests/integration/test_baseline_gt_preconditions.py:85` | `test_raises_on_corrupt_gt` | ? | ? | ? |
| `tests/integration/test_baseline_gt_preconditions.py:99` | `test_error_contains_document_id` | ? | ? | ? |
| `tests/integration/test_baseline_integrity_exit_code.py:24` | `test_exit_code_3_on_baseline_integrity_failure` | integration | ? | ? |
| `tests/integration/test_baseline_materialization.py:57` | `test_passes_when_all_pdfs_present` | integration | ? | ? |
| `tests/integration/test_baseline_materialization.py:71` | `test_raises_when_pdf_dir_missing` | ? | ? | ? |
| `tests/integration/test_baseline_materialization.py:81` | `test_raises_when_single_pdf_missing` | ? | ? | ? |
| `tests/integration/test_baseline_materialization.py:95` | `test_error_message_lists_all_missing_pdfs_sorted` | ? | ? | ? |
| `tests/integration/test_baseline_materialization.py:109` | `test_empty_manifest_passes_with_existing_dir` | ? | ? | ? |
| `tests/integration/test_baseline_materialization.py:121` | `test_extra_pdfs_in_dir_do_not_cause_failure` | ? | ? | ? |
| `tests/integration/test_baseline_physical_integrity.py:72` | `test_passes_with_valid_baseline` | integration | ? | ? |
| `tests/integration/test_baseline_physical_integrity.py:77` | `test_raises_on_manifest_hash_mismatch` | integration | ? | ? |
| `tests/integration/test_baseline_physical_integrity.py:84` | `test_raises_on_pdf_missing` | ? | ? | ? |
| `tests/integration/test_baseline_physical_integrity.py:92` | `test_raises_on_pdf_tampered` | ? | ? | ? |
| `tests/integration/test_benchmark_orchestration_integration.py:120` | `test_orchestrator_parser_evaluation_ocp` | ? | ? | ? |
| `tests/integration/test_benchmark_orchestration_integration.py:177` | `test_orchestrator_llm_run_experiment_smoke` | ? | ? | ? |
| `tests/integration/test_c3_t05_process_boundary.py:178` | `test_t05_g3_staged_publication_crash_and_recovery_between_processes` | ? | ? | ? |

**Pendiente A-01:** marcadores heredados, invocación real del SUT, fixtures autouse, skip/xfail efectivo, parametrizaciones expandidas, CI selectivo y todos los efectos indirectos. Confirmar en un entorno aislado después de A-05.
