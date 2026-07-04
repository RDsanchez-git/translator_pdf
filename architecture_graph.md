# Mapa de Arquitectura y Conexiones

```mermaid
graph TD

    subgraph apps_api_server_py ["?? apps/api/server.py"]
    end

    subgraph apps_api___init___py ["?? apps/api/__init__.py"]

    subgraph apps_bootstrap_pipeline_factory_py ["?? apps/bootstrap/pipeline_factory.py"]
        apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline["[FUNC] _build_default_validation_pipeline()"]:::funcStyle
    call_LegacyValidatorAdapter["--> LegacyValidatorAdapter()"]:::callStyle
    call_ValidationPipeline["--> ValidationPipeline()"]:::callStyle
    call_pipeline_add_chunk_validator["--> pipeline.add_chunk_validator()"]:::callStyle
    call_pipeline_add_document_validator["--> pipeline.add_document_validator()"]:::callStyle
    call_PreservationValidator["--> PreservationValidator()"]:::callStyle
    call_PerimeterValidator["--> PerimeterValidator()"]:::callStyle
    call_SemanticValidator["--> SemanticValidator()"]:::callStyle
    call_VolumetricValidator["--> VolumetricValidator()"]:::callStyle
        apps_bootstrap_pipeline_factory_py_build_pipeline["[FUNC] build_pipeline()"]:::funcStyle
    call_bootstrap_normalization_layer["--> bootstrap_normalization_layer()"]:::callStyle
    call_PdfParserAdapter["--> PdfParserAdapter()"]:::callStyle
    call_get_connection["--> get_connection()"]:::callStyle
    call_SQLiteDocumentRepository["--> SQLiteDocumentRepository()"]:::callStyle
    call_AssemblyPolicy["--> AssemblyPolicy()"]:::callStyle
    call_frozenset["--> frozenset()"]:::callStyle
    call_DocumentAssembler["--> DocumentAssembler()"]:::callStyle
    call_SummaryBuilder["--> SummaryBuilder()"]:::callStyle
    call__build_default_validation_pipeline["--> _build_default_validation_pipeline()"]:::callStyle
    call_HealingPolicy["--> HealingPolicy()"]:::callStyle
    call_MarkdownLeakageHealingStrategy["--> MarkdownLeakageHealingStrategy()"]:::callStyle
    call_MetaTextLeakageHealingStrategy["--> MetaTextLeakageHealingStrategy()"]:::callStyle
    call_EOFBraceClosureStrategy["--> EOFBraceClosureStrategy()"]:::callStyle
    call_EOFMathClosureStrategy["--> EOFMathClosureStrategy()"]:::callStyle
    call_HealingPipeline["--> HealingPipeline()"]:::callStyle
    call_FSMRepository["--> FSMRepository()"]:::callStyle
    call_DocumentCommandHandler["--> DocumentCommandHandler()"]:::callStyle
    call_FSMStateStore["--> FSMStateStore()"]:::callStyle
    call_TranslationPipeline["--> TranslationPipeline()"]:::callStyle

    subgraph apps_bootstrap___init___py ["?? apps/bootstrap/__init__.py"]

    subgraph apps_cli_main_py ["?? apps/cli/main.py"]
        apps_cli_main_py_ChunkerProtocolAdapter["[CLASS] ChunkerProtocolAdapter"]:::classStyle
        apps_cli_main_py_ChunkerProtocolAdapter___init__["__init__()"]:::funcStyle
        apps_cli_main_py_ChunkerProtocolAdapter_chunk["chunk()"]:::funcStyle
    call_build_semantic_chunks_as_units["--> build_semantic_chunks_as_units()"]:::callStyle
        apps_cli_main_py_DummyContextResolver["[CLASS] DummyContextResolver"]:::classStyle
        apps_cli_main_py_DummyContextResolver_resolve["resolve()"]:::funcStyle
    call_ResolvedContext["--> ResolvedContext()"]:::callStyle
        apps_cli_main_py_DummyContextResolver_resolve_many["resolve_many()"]:::funcStyle
        apps_cli_main_py_handle_sweep["[FUNC] handle_sweep()"]:::funcStyle
    call_AbandonedProcessWatchdog["--> AbandonedProcessWatchdog()"]:::callStyle
    call_console_print["--> console.print()"]:::callStyle
    call_watchdog_execute_sweep["--> watchdog.execute_sweep()"]:::callStyle
        apps_cli_main_py_update_ux_boundary["[FUNC] update_ux_boundary()"]:::funcStyle
    call_macro_status_update["--> macro_status.update()"]:::callStyle
        apps_cli_main_py_proxy_enter_step["[FUNC] proxy_enter_step()"]:::funcStyle
    call_original_enter_step["--> original_enter_step()"]:::callStyle
    call_update_ux_boundary["--> update_ux_boundary()"]:::callStyle
        apps_cli_main_py_handle_translate["[FUNC] handle_translate()"]:::funcStyle
    call_asyncio_run["--> asyncio.run()"]:::callStyle
    call_handle_translate_async["--> handle_translate_async()"]:::callStyle
        apps_cli_main_py_handle_resume["[FUNC] handle_resume()"]:::funcStyle
    call_OnDemandResumeManager["--> OnDemandResumeManager()"]:::callStyle
    call_resumer_rescue_stalled_document["--> resumer.rescue_stalled_document()"]:::callStyle
        apps_cli_main_py_handle_status["[FUNC] handle_status()"]:::funcStyle
    call_repo_get_status["--> repo.get_status()"]:::callStyle
    call_Table["--> Table()"]:::callStyle
    call_table_add_column["--> table.add_column()"]:::callStyle
    call_table_add_row["--> table.add_row()"]:::callStyle
    call_str["--> str()"]:::callStyle
        apps_cli_main_py_parse_arguments["[FUNC] parse_arguments()"]:::funcStyle
    call_argparse_ArgumentParser["--> argparse.ArgumentParser()"]:::callStyle
    call_parser_add_subparsers["--> parser.add_subparsers()"]:::callStyle
    call_subparsers_add_parser["--> subparsers.add_parser()"]:::callStyle
    call_t_parser_add_argument["--> t_parser.add_argument()"]:::callStyle
    call_t_parser_set_defaults["--> t_parser.set_defaults()"]:::callStyle
    call_sw_parser_set_defaults["--> sw_parser.set_defaults()"]:::callStyle
    call_r_parser_add_argument["--> r_parser.add_argument()"]:::callStyle
    call_r_parser_set_defaults["--> r_parser.set_defaults()"]:::callStyle
    call_st_parser_add_argument["--> st_parser.add_argument()"]:::callStyle
    call_st_parser_set_defaults["--> st_parser.set_defaults()"]:::callStyle
    call_parser_parse_args["--> parser.parse_args()"]:::callStyle
        apps_cli_main_py_main["[FUNC] main()"]:::funcStyle
    call_parse_arguments["--> parse_arguments()"]:::callStyle
    call_args_func["--> args.func()"]:::callStyle

    subgraph apps_compiler_docker_runner_py ["?? apps/compiler/docker_runner.py"]
        apps_compiler_docker_runner_py_DockerRunner["[CLASS] DockerRunner"]:::classStyle
        apps_compiler_docker_runner_py_DockerRunner_compile["compile()"]:::funcStyle
    call_re_sub["--> re.sub()"]:::callStyle
    call___replace["--> *.replace()"]:::callStyle
    call_tex_content_replace["--> tex_content.replace()"]:::callStyle
    call_tempfile_TemporaryDirectory["--> tempfile.TemporaryDirectory()"]:::callStyle
    call___join["--> *.join()"]:::callStyle
    call_open["--> open()"]:::callStyle
    call_f_write["--> f.write()"]:::callStyle
    call_subprocess_run["--> subprocess.run()"]:::callStyle
    call_Exception["--> Exception()"]:::callStyle
    call_logger_error["--> logger.error()"]:::callStyle
    call_os_getcwd["--> os.getcwd()"]:::callStyle
    call_shutil_copy["--> shutil.copy()"]:::callStyle

    subgraph apps_compiler_log_parser_py ["?? apps/compiler/log_parser.py"]
        apps_compiler_log_parser_py_ErrorType["[CLASS] ErrorType"]:::classStyle
        apps_compiler_log_parser_py_ParsedError["[CLASS] ParsedError"]:::classStyle
        apps_compiler_log_parser_py_LogParser["[CLASS] LogParser"]:::classStyle
        apps_compiler_log_parser_py_LogParser_parse["parse()"]:::funcStyle
    call_re_search["--> re.search()"]:::callStyle
    call_int["--> int()"]:::callStyle
    call_line_match_group["--> line_match.group()"]:::callStyle
    call_ParsedError["--> ParsedError()"]:::callStyle
    call_LogParser__extract_context["--> LogParser._extract_context()"]:::callStyle
        apps_compiler_log_parser_py_LogParser__extract_context["_extract_context()"]:::funcStyle
    call_log_split["--> log.split()"]:::callStyle
    call_enumerate["--> enumerate()"]:::callStyle
    call_max["--> max()"]:::callStyle
    call_min["--> min()"]:::callStyle
    call_len["--> len()"]:::callStyle

    subgraph apps_compiler_tex_builder_py ["?? apps/compiler/tex_builder.py"]
        apps_compiler_tex_builder_py_TexBuilder["[CLASS] TexBuilder"]:::classStyle
        apps_compiler_tex_builder_py_TexBuilder___init__["__init__()"]:::funcStyle
        apps_compiler_tex_builder_py_TexBuilder_build["build()"]:::funcStyle
    call_list["--> list()"]:::callStyle
    call___strip["--> *.strip()"]:::callStyle
    call_ValueError["--> ValueError()"]:::callStyle
    call___lower["--> *.lower()"]:::callStyle
    call_getattr["--> getattr()"]:::callStyle
    call_safe_text_replace["--> safe_text.replace()"]:::callStyle
    call_document_append["--> document.append()"]:::callStyle
    call_document_extend["--> document.extend()"]:::callStyle

    subgraph apps_compiler___init___py ["?? apps/compiler/__init__.py"]

    subgraph apps_compiler___main___py ["?? apps/compiler/__main__.py"]
        apps_compiler___main___py_AssemblerWorkerDaemon["[CLASS] AssemblerWorkerDaemon"]:::classStyle
        apps_compiler___main___py_AssemblerWorkerDaemon___init__["__init__()"]:::funcStyle
    call_uuid_uuid4["--> uuid.uuid4()"]:::callStyle
        apps_compiler___main___py_AssemblerWorkerDaemon_run["run()"]:::funcStyle
    call_logger_info["--> logger.info()"]:::callStyle
    call___find_next_ready_for_assembly["--> *.find_next_ready_for_assembly()"]:::callStyle
    call_time_sleep["--> time.sleep()"]:::callStyle
    call_random_uniform["--> random.uniform()"]:::callStyle
    call_self__process_assembly_task["--> self._process_assembly_task()"]:::callStyle
    call_logger_warning["--> logger.warning()"]:::callStyle
    call_logger_exception["--> logger.exception()"]:::callStyle
        apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely["_fail_document_safely()"]:::funcStyle
    call___get_status["--> *.get_status()"]:::callStyle
    call_FailDocumentCommand["--> FailDocumentCommand()"]:::callStyle
    call___handle["--> *.handle()"]:::callStyle
    call_logger_critical["--> logger.critical()"]:::callStyle
        apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task["_process_assembly_task()"]:::funcStyle
    call_time_perf_counter["--> time.perf_counter()"]:::callStyle
    call_StartAssemblyCommand["--> StartAssemblyCommand()"]:::callStyle
    call____load_document["--> *._load_document()"]:::callStyle
    call___get["--> *.get()"]:::callStyle
    call_sorted["--> sorted()"]:::callStyle
    call_doc_nodes_keys["--> doc_nodes.keys()"]:::callStyle
    call___get_assemblable_chunks["--> *.get_assemblable_chunks()"]:::callStyle
    call_doc_nodes_get["--> doc_nodes.get()"]:::callStyle
    call_valid_chunks_append["--> valid_chunks.append()"]:::callStyle
    call___build["--> *.build()"]:::callStyle
    call_MarkCompilationReadyCommand["--> MarkCompilationReadyCommand()"]:::callStyle
    call_StartCompilationCommand["--> StartCompilationCommand()"]:::callStyle
    call___compile["--> *.compile()"]:::callStyle
    call_CompleteDocumentCommand["--> CompleteDocumentCommand()"]:::callStyle
    call_self__fail_document_safely["--> self._fail_document_safely()"]:::callStyle

    subgraph apps_compiler_sandbox_server_py ["?? apps/compiler/sandbox/server.py"]
        apps_compiler_sandbox_server_py_CompileRequest["[CLASS] CompileRequest"]:::classStyle
        apps_compiler_sandbox_server_py_CompileResult["[CLASS] CompileResult"]:::classStyle

    subgraph apps_daemons_chaos_runner_py ["?? apps/daemons/chaos_runner.py"]
        apps_daemons_chaos_runner_py_SystemObserver["[CLASS] SystemObserver"]:::classStyle
        apps_daemons_chaos_runner_py_SystemObserver___init__["__init__()"]:::funcStyle
    call___abspath["--> *.abspath()"]:::callStyle
        apps_daemons_chaos_runner_py_SystemObserver__get_ro_connection["_get_ro_connection()"]:::funcStyle
    call_sqlite3_connect["--> sqlite3.connect()"]:::callStyle
    call_conn_execute["--> conn.execute()"]:::callStyle
        apps_daemons_chaos_runner_py_SystemObserver_inject_load["inject_load()"]:::funcStyle
    call_ControlPlaneRepository["--> ControlPlaneRepository()"]:::callStyle
    call_range["--> range()"]:::callStyle
    call_fsm_repo_initialize_document["--> fsm_repo.initialize_document()"]:::callStyle
    call_task_repo_enqueue_tasks["--> task_repo.enqueue_tasks()"]:::callStyle
    call_fsm_repo_transition_to["--> fsm_repo.transition_to()"]:::callStyle
    call_doc_ids_append["--> doc_ids.append()"]:::callStyle
    call_conn_close["--> conn.close()"]:::callStyle
        apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics["get_convergence_metrics()"]:::funcStyle
    call_time_time["--> time.time()"]:::callStyle
    call_self__get_ro_connection["--> self._get_ro_connection()"]:::callStyle
    call_conn_cursor["--> conn.cursor()"]:::callStyle
    call_cursor_execute["--> cursor.execute()"]:::callStyle
    call_cursor_fetchone["--> cursor.fetchone()"]:::callStyle
        apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence["wait_for_convergence()"]:::funcStyle
    call_self_get_convergence_metrics["--> self.get_convergence_metrics()"]:::callStyle
        apps_daemons_chaos_runner_py_ChaosInjector["[CLASS] ChaosInjector"]:::classStyle
        apps_daemons_chaos_runner_py_ChaosInjector___init__["__init__()"]:::funcStyle
    call_docker_from_env["--> docker.from_env()"]:::callStyle
    call_os_getenv["--> os.getenv()"]:::callStyle
        apps_daemons_chaos_runner_py_ChaosInjector_kill_service["kill_service()"]:::funcStyle
    call___list["--> *.list()"]:::callStyle
    call_container_kill["--> container.kill()"]:::callStyle
        apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream["mutate_upstream()"]:::funcStyle
    call_requests_post["--> requests.post()"]:::callStyle
    call_resp_raise_for_status["--> resp.raise_for_status()"]:::callStyle
        apps_daemons_chaos_runner_py_game_day_1_crash_consistency["[FUNC] game_day_1_crash_consistency()"]:::funcStyle
    call_SystemObserver["--> SystemObserver()"]:::callStyle
    call_ChaosInjector["--> ChaosInjector()"]:::callStyle
    call_injector_mutate_upstream["--> injector.mutate_upstream()"]:::callStyle
    call_observer_inject_load["--> observer.inject_load()"]:::callStyle
    call_injector_kill_service["--> injector.kill_service()"]:::callStyle
    call_observer_wait_for_convergence["--> observer.wait_for_convergence()"]:::callStyle

    subgraph apps_daemons_fake_gemini_py ["?? apps/daemons/fake_gemini.py"]
        apps_daemons_fake_gemini_py_ChaosConfig["[CLASS] ChaosConfig"]:::classStyle
        apps_daemons_fake_gemini_py_ChaosConfig___init__["__init__()"]:::funcStyle
    call_asyncio_Lock["--> asyncio.Lock()"]:::callStyle
        apps_daemons_fake_gemini_py_Metrics["[CLASS] Metrics"]:::classStyle
        apps_daemons_fake_gemini_py_Metrics___init__["__init__()"]:::funcStyle
        apps_daemons_fake_gemini_py_ChaosMutation["[CLASS] ChaosMutation"]:::classStyle
        apps_daemons_fake_gemini_py_health_check["[FUNC] health_check()"]:::funcStyle
    call_app_get["--> app.get()"]:::callStyle

    subgraph apps_daemons_reconciler_py ["?? apps/daemons/reconciler.py"]
        apps_daemons_reconciler_py_ReconcilerDaemon["[CLASS] ReconcilerDaemon"]:::classStyle
        apps_daemons_reconciler_py_ReconcilerDaemon___init__["__init__()"]:::funcStyle
    call_threading_Event["--> threading.Event()"]:::callStyle
        apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls["_sweep_fsm_stalls()"]:::funcStyle
    call___execute["--> *.execute()"]:::callStyle
    call_cursor_fetchall["--> cursor.fetchall()"]:::callStyle
    call_MarkAssemblyReadyCommand["--> MarkAssemblyReadyCommand()"]:::callStyle
        apps_daemons_reconciler_py_ReconcilerDaemon__leadership_heartbeat["_leadership_heartbeat()"]:::funcStyle
    call___wait["--> *.wait()"]:::callStyle
    call___renew_leadership["--> *.renew_leadership()"]:::callStyle
        apps_daemons_reconciler_py_ReconcilerDaemon_run["run()"]:::funcStyle
    call_copy_context["--> copy_context()"]:::callStyle
    call_ctx_worker_id_set["--> ctx_worker_id.set()"]:::callStyle
    call_threading_Thread["--> threading.Thread()"]:::callStyle
    call_ctx_run["--> ctx.run()"]:::callStyle
    call_heartbeat_thread_start["--> heartbeat_thread.start()"]:::callStyle
    call___is_set["--> *.is_set()"]:::callStyle
    call___acquire_leadership["--> *.acquire_leadership()"]:::callStyle
    call_self__sweep_tasks["--> self._sweep_tasks()"]:::callStyle
    call_self__sweep_fsm_stalls["--> self._sweep_fsm_stalls()"]:::callStyle
    call___set["--> *.set()"]:::callStyle
    call_heartbeat_thread_join["--> heartbeat_thread.join()"]:::callStyle
    call___release_leadership["--> *.release_leadership()"]:::callStyle
        apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks["_sweep_tasks()"]:::funcStyle
    call___get_latest_event["--> *.get_latest_event()"]:::callStyle
    call_RematerializeTaskCommand["--> RematerializeTaskCommand()"]:::callStyle
    call_RecoverZombieTaskCommand["--> RecoverZombieTaskCommand()"]:::callStyle

    subgraph apps_llm_workers_adapters_py ["?? apps/llm_workers/adapters.py"]
        apps_llm_workers_adapters_py_BypassProvider["[CLASS] BypassProvider"]:::classStyle
        apps_llm_workers_adapters_py_GroqProvider["[CLASS] GroqProvider"]:::classStyle
        apps_llm_workers_adapters_py_GroqProvider___init__["__init__()"]:::funcStyle
    call_AsyncGroq["--> AsyncGroq()"]:::callStyle
        apps_llm_workers_adapters_py_GeminiProvider["[CLASS] GeminiProvider"]:::classStyle
        apps_llm_workers_adapters_py_GeminiProvider___init__["__init__()"]:::funcStyle
    call_genai_configure["--> genai.configure()"]:::callStyle

    subgraph apps_llm_workers_cache_provider_py ["?? apps/llm_workers/cache_provider.py"]
        apps_llm_workers_cache_provider_py_CachedLLMProvider["[CLASS] CachedLLMProvider"]:::classStyle
        apps_llm_workers_cache_provider_py_CachedLLMProvider___init__["__init__()"]:::funcStyle

    subgraph apps_llm_workers_dispatcher_py ["?? apps/llm_workers/dispatcher.py"]
        apps_llm_workers_dispatcher_py_AsyncDispatcher["[CLASS] AsyncDispatcher"]:::classStyle
        apps_llm_workers_dispatcher_py_AsyncDispatcher___init__["__init__()"]:::funcStyle
    call_self__default_pipeline["--> self._default_pipeline()"]:::callStyle
        apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline["_default_pipeline()"]:::funcStyle

    subgraph apps_llm_workers_prompt_builder_py ["?? apps/llm_workers/prompt_builder.py"]
        apps_llm_workers_prompt_builder_py_PromptEnvelope["[CLASS] PromptEnvelope"]:::classStyle
        apps_llm_workers_prompt_builder_py_BuildSuccess["[CLASS] BuildSuccess"]:::classStyle
        apps_llm_workers_prompt_builder_py_BuildFailure["[CLASS] BuildFailure"]:::classStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder["[CLASS] PromptBuilder"]:::classStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder___init__["__init__()"]:::funcStyle
    call_StandardCompressionPolicy["--> StandardCompressionPolicy()"]:::callStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder__build_system["_build_system()"]:::funcStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder_build["build()"]:::funcStyle
    call_BuildFailure["--> BuildFailure()"]:::callStyle
    call_full_context_str_split["--> full_context_str.split()"]:::callStyle
    call_context_levels_get["--> context_levels.get()"]:::callStyle
    call_self__build_system["--> self._build_system()"]:::callStyle
    call___calculate["--> *.calculate()"]:::callStyle
    call___get_levels["--> *.get_levels()"]:::callStyle
    call___estimate_tokens["--> *.estimate_tokens()"]:::callStyle
    call___hexdigest["--> *.hexdigest()"]:::callStyle
    call_hashlib_sha256["--> hashlib.sha256()"]:::callStyle
    call_hash_input_encode["--> hash_input.encode()"]:::callStyle
    call_PromptEnvelope["--> PromptEnvelope()"]:::callStyle
    call_BuildSuccess["--> BuildSuccess()"]:::callStyle

    subgraph apps_llm_workers_rate_limiter_py ["?? apps/llm_workers/rate_limiter.py"]
        apps_llm_workers_rate_limiter_py_QuotaRejectionReason["[CLASS] QuotaRejectionReason"]:::classStyle
        apps_llm_workers_rate_limiter_py_QuotaReservation["[CLASS] QuotaReservation"]:::classStyle
        apps_llm_workers_rate_limiter_py_QuotaReservation_create_granted["create_granted()"]:::funcStyle
    call_cls["--> cls()"]:::callStyle
        apps_llm_workers_rate_limiter_py_QuotaReservation_create_rejected["create_rejected()"]:::funcStyle
        apps_llm_workers_rate_limiter_py_QuotaManagerProtocol["[CLASS] QuotaManagerProtocol"]:::classStyle
        apps_llm_workers_rate_limiter_py_ClockProtocol["[CLASS] ClockProtocol"]:::classStyle
        apps_llm_workers_rate_limiter_py_ClockProtocol_now["now()"]:::funcStyle
        apps_llm_workers_rate_limiter_py_SystemClock["[CLASS] SystemClock"]:::classStyle
        apps_llm_workers_rate_limiter_py_SystemClock_now["now()"]:::funcStyle
    call_time_monotonic["--> time.monotonic()"]:::callStyle
        apps_llm_workers_rate_limiter_py_TokenBucket["[CLASS] TokenBucket"]:::classStyle
        apps_llm_workers_rate_limiter_py_TokenBucket___init__["__init__()"]:::funcStyle
    call_float["--> float()"]:::callStyle
    call___now["--> *.now()"]:::callStyle
        apps_llm_workers_rate_limiter_py_TokenBucket__refill["_refill()"]:::funcStyle
        apps_llm_workers_rate_limiter_py_TokenBucket_get_wait_time["get_wait_time()"]:::funcStyle
    call_self__refill["--> self._refill()"]:::callStyle
        apps_llm_workers_rate_limiter_py_TokenBucket_consume["consume()"]:::funcStyle
        apps_llm_workers_rate_limiter_py_QuotaManager["[CLASS] QuotaManager"]:::classStyle
        apps_llm_workers_rate_limiter_py_QuotaManager___init__["__init__()"]:::funcStyle
    call_SystemClock["--> SystemClock()"]:::callStyle
    call_TokenBucket["--> TokenBucket()"]:::callStyle
        apps_llm_workers_rate_limiter_py_RateLimitedProvider["[CLASS] RateLimitedProvider"]:::classStyle
        apps_llm_workers_rate_limiter_py_RateLimitedProvider___init__["__init__()"]:::funcStyle

    subgraph apps_llm_workers_resilient_provider_py ["?? apps/llm_workers/resilient_provider.py"]
        apps_llm_workers_resilient_provider_py_ResilientProvider["[CLASS] ResilientProvider"]:::classStyle
        apps_llm_workers_resilient_provider_py_ResilientProvider___init__["__init__()"]:::funcStyle

    subgraph apps_llm_workers_router_translation_py ["?? apps/llm_workers/router_translation.py"]
        apps_llm_workers_router_translation_py_TranslationRouter["[CLASS] TranslationRouter"]:::classStyle
        apps_llm_workers_router_translation_py_TranslationRouter_get_strategy["get_strategy()"]:::funcStyle

    subgraph apps_llm_workers_routing_py ["?? apps/llm_workers/routing.py"]
        apps_llm_workers_routing_py_ProviderResult["[CLASS] ProviderResult"]:::classStyle
        apps_llm_workers_routing_py_LLMProvider["[CLASS] LLMProvider"]:::classStyle
        apps_llm_workers_routing_py_ProviderStrategy["[CLASS] ProviderStrategy"]:::classStyle
        apps_llm_workers_routing_py_TranslationStrategyRouter["[CLASS] TranslationStrategyRouter"]:::classStyle
        apps_llm_workers_routing_py_TranslationStrategyRouter___init__["__init__()"]:::funcStyle
        apps_llm_workers_routing_py_TranslationStrategyRouter_route["route()"]:::funcStyle

    subgraph apps_llm_workers_sync_bridge_py ["?? apps/llm_workers/sync_bridge.py"]
        apps_llm_workers_sync_bridge_py_SyncProviderBridge["[CLASS] SyncProviderBridge"]:::classStyle
        apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__["__init__()"]:::funcStyle
    call_asyncio_new_event_loop["--> asyncio.new_event_loop()"]:::callStyle
    call___start["--> *.start()"]:::callStyle
    call_RuntimeError["--> RuntimeError()"]:::callStyle
        apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop["_start_loop()"]:::funcStyle
    call_asyncio_set_event_loop["--> asyncio.set_event_loop()"]:::callStyle
    call___run_forever["--> *.run_forever()"]:::callStyle
    call_asyncio_all_tasks["--> asyncio.all_tasks()"]:::callStyle
    call_task_cancel["--> task.cancel()"]:::callStyle
    call___run_until_complete["--> *.run_until_complete()"]:::callStyle
    call_asyncio_gather["--> asyncio.gather()"]:::callStyle
    call___shutdown_asyncgens["--> *.shutdown_asyncgens()"]:::callStyle
    call___close["--> *.close()"]:::callStyle
        apps_llm_workers_sync_bridge_py_SyncProviderBridge_shutdown["shutdown()"]:::funcStyle
    call___is_running["--> *.is_running()"]:::callStyle
    call___call_soon_threadsafe["--> *.call_soon_threadsafe()"]:::callStyle
        apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute["execute()"]:::funcStyle
    call_target_payload_encode["--> target_payload.encode()"]:::callStyle
    call_TranslationUnit["--> TranslationUnit()"]:::callStyle
    call_asyncio_run_coroutine_threadsafe["--> asyncio.run_coroutine_threadsafe()"]:::callStyle
    call___translate["--> *.translate()"]:::callStyle
    call_future_result["--> future.result()"]:::callStyle
    call_future_cancel["--> future.cancel()"]:::callStyle
    call_TimeoutError["--> TimeoutError()"]:::callStyle

    subgraph apps_llm_workers___init___py ["?? apps/llm_workers/__init__.py"]

    subgraph apps_llm_workers___main___py ["?? apps/llm_workers/__main__.py"]
        apps_llm_workers___main___py_TaskLeaseHeartbeat["[CLASS] TaskLeaseHeartbeat"]:::classStyle
        apps_llm_workers___main___py_TaskLeaseHeartbeat___init__["__init__()"]:::funcStyle
        apps_llm_workers___main___py_TaskLeaseHeartbeat__beat["_beat()"]:::funcStyle
    call_control_repo_renew_task_lease["--> control_repo.renew_task_lease()"]:::callStyle
        apps_llm_workers___main___py_TaskLeaseHeartbeat___enter__["__enter__()"]:::funcStyle
        apps_llm_workers___main___py_TaskLeaseHeartbeat___exit__["__exit__()"]:::funcStyle
        apps_llm_workers___main___py_LLMWorkerDaemon["[CLASS] LLMWorkerDaemon"]:::classStyle
        apps_llm_workers___main___py_LLMWorkerDaemon___init__["__init__()"]:::funcStyle
        apps_llm_workers___main___py_LLMWorkerDaemon_stop["stop()"]:::funcStyle
        apps_llm_workers___main___py_LLMWorkerDaemon_run["run()"]:::funcStyle
    call___claim_next_pending_task["--> *.claim_next_pending_task()"]:::callStyle
    call_self__process_task["--> self._process_task()"]:::callStyle
        apps_llm_workers___main___py_LLMWorkerDaemon__process_task["_process_task()"]:::funcStyle
    call___get_node["--> *.get_node()"]:::callStyle
    call___mark_task_failed["--> *.mark_task_failed()"]:::callStyle
    call_content_encode["--> content.encode()"]:::callStyle
    call___get_projection_status["--> *.get_projection_status()"]:::callStyle
    call___mark_task_completed["--> *.mark_task_completed()"]:::callStyle
    call___get_replay["--> *.get_replay()"]:::callStyle
    call_TaskLeaseHeartbeat["--> TaskLeaseHeartbeat()"]:::callStyle
    call_OptimisticLockError["--> OptimisticLockError()"]:::callStyle
    call___append_wal["--> *.append_wal()"]:::callStyle
    call_TextNormalizer_normalize["--> TextNormalizer.normalize()"]:::callStyle
    call_normalized_encode["--> normalized.encode()"]:::callStyle
    call___upsert_projection["--> *.upsert_projection()"]:::callStyle
    call___observe["--> *.observe()"]:::callStyle
        apps_llm_workers___main___py_shutdown_handler["[FUNC] shutdown_handler()"]:::funcStyle
    call_daemon_stop["--> daemon.stop()"]:::callStyle

    subgraph apps_ocr_router___main___py ["?? apps/ocr_router/__main__.py"]
        apps_ocr_router___main___py_OCRRouterDaemon["[CLASS] OCRRouterDaemon"]:::classStyle
        apps_ocr_router___main___py_OCRRouterDaemon___init__["__init__()"]:::funcStyle
    call_Path["--> Path()"]:::callStyle
    call_d_mkdir["--> d.mkdir()"]:::callStyle
        apps_ocr_router___main___py_OCRRouterDaemon_run["run()"]:::funcStyle
    call_next["--> next()"]:::callStyle
    call___glob["--> *.glob()"]:::callStyle
    call_self__process_document["--> self._process_document()"]:::callStyle
        apps_ocr_router___main___py_OCRRouterDaemon__process_document["_process_document()"]:::funcStyle
    call_f_read["--> f.read()"]:::callStyle
    call___is_document_already_processed["--> *.is_document_already_processed()"]:::callStyle
    call_shutil_move["--> shutil.move()"]:::callStyle
    call_parse_pdf["--> parse_pdf()"]:::callStyle
    call_compute_ast_hash["--> compute_ast_hash()"]:::callStyle
    call_FastWordEstimator["--> FastWordEstimator()"]:::callStyle
    call___register_ast["--> *.register_ast()"]:::callStyle
    call___initialize_document["--> *.initialize_document()"]:::callStyle
    call_StartParsingCommand["--> StartParsingCommand()"]:::callStyle
    call___enqueue_tasks["--> *.enqueue_tasks()"]:::callStyle
    call_StartProcessingCommand["--> StartProcessingCommand()"]:::callStyle
    call_round["--> round()"]:::callStyle
    call_isinstance["--> isinstance()"]:::callStyle
    call_pdf_path_exists["--> pdf_path.exists()"]:::callStyle
    call_traceback_format_exc["--> traceback.format_exc()"]:::callStyle
    call_json_dump["--> json.dump()"]:::callStyle

    subgraph apps_ocr_workers_router_py ["?? apps/ocr_workers/router.py"]

    subgraph apps_ocr_workers___init___py ["?? apps/ocr_workers/__init__.py"]

    subgraph core_ast_grouper_py ["?? core/ast/grouper.py"]
        core_ast_grouper_py_SemanticGroup["[CLASS] SemanticGroup"]:::classStyle
        core_ast_grouper_py_ContextAwareSemanticGrouper["[CLASS] ContextAwareSemanticGrouper"]:::classStyle
        core_ast_grouper_py_ContextAwareSemanticGrouper_group["group()"]:::funcStyle
    call_tuple["--> tuple()"]:::callStyle
    call_first_node_cp_get["--> first_node_cp.get()"]:::callStyle
    call_groups_append["--> groups.append()"]:::callStyle
    call_SemanticGroup["--> SemanticGroup()"]:::callStyle
    call_current_nodes_append["--> current_nodes.append()"]:::callStyle

    subgraph core_ast_hashing_py ["?? core/ast/hashing.py"]
        core_ast_hashing_py_compute_ast_hash["[FUNC] compute_ast_hash()"]:::funcStyle
        core_ast_hashing_py_serialize_node["[FUNC] serialize_node()"]:::funcStyle
    call_hasattr["--> hasattr()"]:::callStyle
    call_serialize_node["--> serialize_node()"]:::callStyle
    call_json_dumps["--> json.dumps()"]:::callStyle
    call_raw_encode["--> raw.encode()"]:::callStyle
        core_ast_hashing_py_ChunkPolicy["[CLASS] ChunkPolicy"]:::classStyle
        core_ast_hashing_py_TokenBudgetChunker["[CLASS] TokenBudgetChunker"]:::classStyle
        core_ast_hashing_py_TokenBudgetChunker___init__["__init__()"]:::funcStyle
    call_ChunkPolicy["--> ChunkPolicy()"]:::callStyle
    call_ChunkingReport["--> ChunkingReport()"]:::callStyle
        core_ast_hashing_py_TokenBudgetChunker__split_by_sentence["_split_by_sentence()"]:::funcStyle
    call_re_split["--> re.split()"]:::callStyle
    call_s_strip["--> s.strip()"]:::callStyle
        core_ast_hashing_py_TokenBudgetChunker_chunk_group["chunk_group()"]:::funcStyle
        core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk["flush_translate_chunk()"]:::funcStyle
    call_payload_text_encode["--> payload_text.encode()"]:::callStyle
    call_hashlib_md5["--> hashlib.md5()"]:::callStyle
    call___encode["--> *.encode()"]:::callStyle
    call_units_append["--> units.append()"]:::callStyle
    call_flush_translate_chunk["--> flush_translate_chunk()"]:::callStyle
    call___estimate["--> *.estimate()"]:::callStyle
    call_self__split_by_sentence["--> self._split_by_sentence()"]:::callStyle
    call_ASTNode["--> ASTNode()"]:::callStyle
        core_ast_hashing_py_build_semantic_chunks_as_units["[FUNC] build_semantic_chunks_as_units()"]:::funcStyle
    call_ContextAwareSemanticGrouper_group["--> ContextAwareSemanticGrouper.group()"]:::callStyle
    call_TokenBudgetChunker["--> TokenBudgetChunker()"]:::callStyle
    call_chunker_chunk_group["--> chunker.chunk_group()"]:::callStyle
    call_all_units_extend["--> all_units.extend()"]:::callStyle
    call_sum["--> sum()"]:::callStyle

    subgraph core_ast_models_py ["?? core/ast/models.py"]
        core_ast_models_py_StructuralNodeType["[CLASS] StructuralNodeType"]:::classStyle
        core_ast_models_py_ContentNodeType["[CLASS] ContentNodeType"]:::classStyle
        core_ast_models_py_TranslationTaskType["[CLASS] TranslationTaskType"]:::classStyle
        core_ast_models_py_OverflowPolicy["[CLASS] OverflowPolicy"]:::classStyle
        core_ast_models_py_ASTNode["[CLASS] ASTNode"]:::classStyle
        core_ast_models_py_ASTNode_has_valid_sequence["has_valid_sequence()"]:::funcStyle
        core_ast_models_py_TokenEstimator["[CLASS] TokenEstimator"]:::classStyle
        core_ast_models_py_TokenEstimator_estimate["estimate()"]:::funcStyle
        core_ast_models_py_FastWordEstimator["[CLASS] FastWordEstimator"]:::classStyle
        core_ast_models_py_FastWordEstimator_estimate["estimate()"]:::funcStyle
    call_text_split["--> text.split()"]:::callStyle
        core_ast_models_py_FastWordEstimator_estimate_tokens["estimate_tokens()"]:::funcStyle
    call_self_estimate["--> self.estimate()"]:::callStyle
        core_ast_models_py_TranslationUnit["[CLASS] TranslationUnit"]:::classStyle
        core_ast_models_py_ChunkingReport["[CLASS] ChunkingReport"]:::classStyle
        core_ast_models_py_TranslatedUnit["[CLASS] TranslatedUnit"]:::classStyle
        core_ast_models_py_ReconstructedDocument["[CLASS] ReconstructedDocument"]:::classStyle
        core_ast_models_py_ExecutionStatus["[CLASS] ExecutionStatus"]:::classStyle
        core_ast_models_py_FailureReason["[CLASS] FailureReason"]:::classStyle
        core_ast_models_py_ChunkOutcome["[CLASS] ChunkOutcome"]:::classStyle
        core_ast_models_py_ChunkOutcome___post_init__["__post_init__()"]:::funcStyle
        core_ast_models_py_ChunkOutcome_is_success["is_success()"]:::funcStyle
        core_ast_models_py_DispatchResult["[CLASS] DispatchResult"]:::classStyle
        core_ast_models_py_DispatchResult_total_processed["total_processed()"]:::funcStyle
        core_ast_models_py_DispatchResult_total_failed["total_failed()"]:::funcStyle
        core_ast_models_py_DispatchResult_success_rate["success_rate()"]:::funcStyle
        core_ast_models_py_DispatchResult_failed_by_reason["failed_by_reason()"]:::funcStyle
    call_Counter["--> Counter()"]:::callStyle
    call_dict["--> dict()"]:::callStyle
        core_ast_models_py_OriginalChunk["[CLASS] OriginalChunk"]:::classStyle
        core_ast_models_py_DispatchAnalytics["[CLASS] DispatchAnalytics"]:::classStyle
        core_ast_models_py_DispatchAnalytics_calculate_success_rate["calculate_success_rate()"]:::funcStyle
        core_ast_models_py_DispatchAnalytics_aggregate_failures["aggregate_failures()"]:::funcStyle
        core_ast_models_py_ExecutionRoute["[CLASS] ExecutionRoute"]:::classStyle
        core_ast_models_py_ExecutionStage["[CLASS] ExecutionStage"]:::classStyle

    subgraph core_ast_parser_py ["?? core/ast/parser.py"]
        core_ast_parser_py_sanitize_marker_html["[FUNC] sanitize_marker_html()"]:::funcStyle
    call_html_unescape["--> html.unescape()"]:::callStyle
        core_ast_parser_py__is_stem_table["[FUNC] _is_stem_table()"]:::funcStyle
    call_line_strip["--> line.strip()"]:::callStyle
    call_block_splitlines["--> block.splitlines()"]:::callStyle
    call_STEM_TABLE_ROW_PATTERN_search["--> STEM_TABLE_ROW_PATTERN.search()"]:::callStyle
        core_ast_parser_py__run_tesseract_on_bytes["[FUNC] _run_tesseract_on_bytes()"]:::funcStyle
    call_Image_open["--> Image.open()"]:::callStyle
    call_io_BytesIO["--> io.BytesIO()"]:::callStyle
    call_pytesseract_image_to_string["--> pytesseract.image_to_string()"]:::callStyle
        core_ast_parser_py__extract_document_text["[FUNC] _extract_document_text()"]:::funcStyle
    call_os_makedirs["--> os.makedirs()"]:::callStyle
    call_pymupdf4llm_to_markdown["--> pymupdf4llm.to_markdown()"]:::callStyle
    call_fitz_open["--> fitz.open()"]:::callStyle
    call_pages_tasks_append["--> pages_tasks.append()"]:::callStyle
    call___get_pixmap["--> *.get_pixmap()"]:::callStyle
    call_pix_tobytes["--> pix.tobytes()"]:::callStyle
    call_doc_close["--> doc.close()"]:::callStyle
        core_ast_parser_py__worker_task["[FUNC] _worker_task()"]:::funcStyle
    call__run_tesseract_on_bytes["--> _run_tesseract_on_bytes()"]:::callStyle
    call_ThreadPoolExecutor["--> ThreadPoolExecutor()"]:::callStyle
    call_executor_map["--> executor.map()"]:::callStyle
        core_ast_parser_py_parse_pdf["[FUNC] parse_pdf()"]:::funcStyle
    call___exists["--> *.exists()"]:::callStyle
    call_FileNotFoundError["--> FileNotFoundError()"]:::callStyle
    call_json_load["--> json.load()"]:::callStyle
    call_PDFRouter_detect_pdf_type["--> PDFRouter.detect_pdf_type()"]:::callStyle
    call__extract_document_text["--> _extract_document_text()"]:::callStyle
    call_sanitize_marker_html["--> sanitize_marker_html()"]:::callStyle
    call_dbg_f_write["--> dbg_f.write()"]:::callStyle
    call_gc_collect["--> gc.collect()"]:::callStyle
    call_MarkdownSegmenter["--> MarkdownSegmenter()"]:::callStyle
    call_segmenter_segment["--> segmenter.segment()"]:::callStyle
    call_bool["--> bool()"]:::callStyle
    call_re_match["--> re.match()"]:::callStyle
    call_block_strip["--> block.strip()"]:::callStyle
    call_any["--> any()"]:::callStyle
    call___startswith["--> *.startswith()"]:::callStyle
    call_block_lower["--> block.lower()"]:::callStyle
    call_re_finditer["--> re.finditer()"]:::callStyle
    call_match_start["--> match.start()"]:::callStyle
    call_ast_nodes_append["--> ast_nodes.append()"]:::callStyle
    call_match_group["--> match.group()"]:::callStyle
    call_match_end["--> match.end()"]:::callStyle
    call_EQUATION_BLOCK_PATTERNS_search["--> EQUATION_BLOCK_PATTERNS.search()"]:::callStyle
    call__is_stem_table["--> _is_stem_table()"]:::callStyle
    call_block_startswith["--> block.startswith()"]:::callStyle
    call_n_model_dump["--> n.model_dump()"]:::callStyle
    call_shutil_rmtree["--> shutil.rmtree()"]:::callStyle

    subgraph core_ast_registry_py ["?? core/ast/registry.py"]
        core_ast_registry_py_ASTRegistry["[CLASS] ASTRegistry"]:::classStyle
        core_ast_registry_py_ASTRegistry___init__["__init__()"]:::funcStyle
        core_ast_registry_py_ASTRegistry_get_node["get_node()"]:::funcStyle
    call_self__load_document["--> self._load_document()"]:::callStyle
    call_doc_cache_get["--> doc_cache.get()"]:::callStyle
        core_ast_registry_py_ASTRegistry__load_document["_load_document()"]:::funcStyle
    call_raw_data_get["--> raw_data.get()"]:::callStyle
    call_ASTNode_model_validate["--> ASTNode.model_validate()"]:::callStyle
        core_ast_registry_py_ASTRegistry_register_ast["register_ast()"]:::funcStyle
    call_tempfile_mkstemp["--> tempfile.mkstemp()"]:::callStyle
    call_os_fdopen["--> os.fdopen()"]:::callStyle
    call_os_replace["--> os.replace()"]:::callStyle
    call_os_remove["--> os.remove()"]:::callStyle

    subgraph core_ast_router_py ["?? core/ast/router.py"]
        core_ast_router_py_PDFRouter["[CLASS] PDFRouter"]:::classStyle
        core_ast_router_py_PDFRouter_detect_pdf_type["detect_pdf_type()"]:::funcStyle
    call_page_get_text["--> page.get_text()"]:::callStyle
    call_text_str_strip["--> text_str.strip()"]:::callStyle
    call_empty_pages_append["--> empty_pages.append()"]:::callStyle

    subgraph core_ast_segmenter_py ["?? core/ast/segmenter.py"]
        core_ast_segmenter_py_SegmentState["[CLASS] SegmentState"]:::classStyle
        core_ast_segmenter_py_MarkdownSegmenter["[CLASS] MarkdownSegmenter"]:::classStyle
        core_ast_segmenter_py_MarkdownSegmenter___init__["__init__()"]:::funcStyle
    call_re_compile["--> re.compile()"]:::callStyle
        core_ast_segmenter_py_MarkdownSegmenter_segment["segment()"]:::funcStyle
    call_full_text_splitlines["--> full_text.splitlines()"]:::callStyle
        core_ast_segmenter_py_MarkdownSegmenter_flush_block["flush_block()"]:::funcStyle
    call_blocks_append["--> blocks.append()"]:::callStyle
    call_flush_block["--> flush_block()"]:::callStyle
    call___match["--> *.match()"]:::callStyle
    call_current_block_append["--> current_block.append()"]:::callStyle
    call___search["--> *.search()"]:::callStyle
    call_b_strip["--> b.strip()"]:::callStyle

    subgraph core_ast_validator_py ["?? core/ast/validator.py"]
        core_ast_validator_py_ASTValidationError["[CLASS] ASTValidationError"]:::classStyle
        core_ast_validator_py_ASTHealthReport["[CLASS] ASTHealthReport"]:::classStyle
        core_ast_validator_py_ASTHealthReport___init__["__init__()"]:::funcStyle
        core_ast_validator_py_ASTHealthReport_from_ast["from_ast()"]:::funcStyle
        core_ast_validator_py_ASTHealthReport___str__["__str__()"]:::funcStyle
        core_ast_validator_py_ASTValidator["[CLASS] ASTValidator"]:::classStyle
        core_ast_validator_py_ASTValidator_validate["validate()"]:::funcStyle
    call_ASTValidationError["--> ASTValidationError()"]:::callStyle
    call_set["--> set()"]:::callStyle
    call_seen_ids_add["--> seen_ids.add()"]:::callStyle
    call_LATEX_MATH_OPEN_search["--> LATEX_MATH_OPEN.search()"]:::callStyle
    call_LATEX_MATH_CLOSE_search["--> LATEX_MATH_CLOSE.search()"]:::callStyle

    subgraph core_ast___init___py ["?? core/ast/__init__.py"]

    subgraph core_benchmark_aggregation_py ["?? core/benchmark/aggregation.py"]
        core_benchmark_aggregation_py_calculate_decoupled_overall_score["[FUNC] calculate_decoupled_overall_score()"]:::funcStyle
    call___upper["--> *.upper()"]:::callStyle

    subgraph core_benchmark_judge_models_py ["?? core/benchmark/judge_models.py"]
        core_benchmark_judge_models_py_DefectCategory["[CLASS] DefectCategory"]:::classStyle
        core_benchmark_judge_models_py_ChunkEvaluationScore["[CLASS] ChunkEvaluationScore"]:::classStyle
        core_benchmark_judge_models_py_ChunkEvaluationScore_overall_score["overall_score()"]:::funcStyle
    call_calculate_decoupled_overall_score["--> calculate_decoupled_overall_score()"]:::callStyle

    subgraph core_benchmark_judge_prompts_py ["?? core/benchmark/judge_prompts.py"]
        core_benchmark_judge_prompts_py_build_judge_prompt["[FUNC] build_judge_prompt()"]:::funcStyle

    subgraph core_benchmark_models_py ["?? core/benchmark/models.py"]
        core_benchmark_models_py_ProviderDescriptor["[CLASS] ProviderDescriptor"]:::classStyle
        core_benchmark_models_py_HardwareTelemetry["[CLASS] HardwareTelemetry"]:::classStyle
        core_benchmark_models_py_BenchmarkMetadata["[CLASS] BenchmarkMetadata"]:::classStyle
        core_benchmark_models_py_DocumentComplexity["[CLASS] DocumentComplexity"]:::classStyle
        core_benchmark_models_py_BenchmarkMode["[CLASS] BenchmarkMode"]:::classStyle
        core_benchmark_models_py_QuotaSnapshot["[CLASS] QuotaSnapshot"]:::classStyle
        core_benchmark_models_py_QualityPolicy["[CLASS] QualityPolicy"]:::classStyle
        core_benchmark_models_py_StructuralQualityMetrics["[CLASS] StructuralQualityMetrics"]:::classStyle
        core_benchmark_models_py_TranslatedArtifact["[CLASS] TranslatedArtifact"]:::classStyle
        core_benchmark_models_py_ChunkBenchmarkRecord["[CLASS] ChunkBenchmarkRecord"]:::classStyle
        core_benchmark_models_py_ChunkBenchmarkRecord_tps_formula["tps_formula()"]:::funcStyle
        core_benchmark_models_py_BenchmarkDocument["[CLASS] BenchmarkDocument"]:::classStyle
        core_benchmark_models_py_BenchmarkDataset["[CLASS] BenchmarkDataset"]:::classStyle
        core_benchmark_models_py_LatencyMetrics["[CLASS] LatencyMetrics"]:::classStyle
        core_benchmark_models_py_StatisticalMoments["[CLASS] StatisticalMoments"]:::classStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics["[CLASS] ProviderBenchmarkMetrics"]:::classStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_total_tokens["total_tokens()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_reliability_score["reliability_score()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_input_tps["input_tps()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_output_tps["output_tps()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_total_tps["total_tps()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1m_tokens_usd["cost_per_1m_tokens_usd()"]:::funcStyle
        core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1k_tokens_usd["cost_per_1k_tokens_usd()"]:::funcStyle
        core_benchmark_models_py_MetricAggregator["[CLASS] MetricAggregator"]:::classStyle
        core_benchmark_models_py_MetricAggregator__percentile["_percentile()"]:::funcStyle
    call_math_ceil["--> math.ceil()"]:::callStyle
        core_benchmark_models_py_MetricAggregator_aggregate["aggregate()"]:::funcStyle
    call_LatencyMetrics["--> LatencyMetrics()"]:::callStyle
    call_MetricAggregator__percentile["--> MetricAggregator._percentile()"]:::callStyle
    call_ProviderBenchmarkMetrics["--> ProviderBenchmarkMetrics()"]:::callStyle
        core_benchmark_models_py_BenchmarkRunReport["[CLASS] BenchmarkRunReport"]:::classStyle
        core_benchmark_models_py_BenchmarkRunReport_total_tps_delta_percentage["total_tps_delta_percentage()"]:::funcStyle
        core_benchmark_models_py_BenchmarkRunReport_cost_delta_percentage["cost_delta_percentage()"]:::funcStyle
        core_benchmark_models_py_PreparedBenchmarkDataset["[CLASS] PreparedBenchmarkDataset"]:::classStyle

    subgraph core_benchmark_orchestrator_py ["?? core/benchmark/orchestrator.py"]
        core_benchmark_orchestrator_py_DatasetIntegrityValidator["[CLASS] DatasetIntegrityValidator"]:::classStyle
        core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify["verify()"]:::funcStyle
    call_sha256_update["--> sha256.update()"]:::callStyle
    call_sha256_hexdigest["--> sha256.hexdigest()"]:::callStyle
        core_benchmark_orchestrator_py_SequentialBenchmarkOrchestrator["[CLASS] SequentialBenchmarkOrchestrator"]:::classStyle
        core_benchmark_orchestrator_py_SequentialBenchmarkOrchestrator___init__["__init__()"]:::funcStyle

    subgraph core_benchmark_persistence_py ["?? core/benchmark/persistence.py"]
        core_benchmark_persistence_py_BenchmarkPersistenceGateway["[CLASS] BenchmarkPersistenceGateway"]:::classStyle
        core_benchmark_persistence_py_BenchmarkPersistenceGateway___init__["__init__()"]:::funcStyle
    call___mkdir["--> *.mkdir()"]:::callStyle
        core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_raw_records_checkpoint["save_raw_records_checkpoint()"]:::funcStyle
        core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report["save_final_report()"]:::funcStyle
    call_base_dir_mkdir["--> base_dir.mkdir()"]:::callStyle

    subgraph core_benchmark_ports_py ["?? core/benchmark/ports.py"]
        core_benchmark_ports_py_RunnerExecutionResult["[CLASS] RunnerExecutionResult"]:::classStyle
        core_benchmark_ports_py_BenchmarkRunnerProtocol["[CLASS] BenchmarkRunnerProtocol"]:::classStyle

    subgraph core_benchmark_quality_py ["?? core/benchmark/quality.py"]
        core_benchmark_quality_py_FormalLatexSyntaxParser["[CLASS] FormalLatexSyntaxParser"]:::classStyle
        core_benchmark_quality_py_FormalLatexSyntaxParser_validate_syntax["validate_syntax()"]:::funcStyle
    call_LatexWalker["--> LatexWalker()"]:::callStyle
    call_walker_get_latex_nodes["--> walker.get_latex_nodes()"]:::callStyle
    call_logger_debug["--> logger.debug()"]:::callStyle
        core_benchmark_quality_py_FormalMarkdownTableParser["[CLASS] FormalMarkdownTableParser"]:::classStyle
        core_benchmark_quality_py_FormalMarkdownTableParser_validate_syntax["validate_syntax()"]:::funcStyle
    call_MarkdownIt["--> MarkdownIt()"]:::callStyle
    call_md_parse["--> md.parse()"]:::callStyle
        core_benchmark_quality_py_StructuralQualityEvaluator["[CLASS] StructuralQualityEvaluator"]:::classStyle
        core_benchmark_quality_py_StructuralQualityEvaluator_evaluate["evaluate()"]:::funcStyle
    call_StructuralQualityMetrics["--> StructuralQualityMetrics()"]:::callStyle
    call_original_nodes_map_get["--> original_nodes_map.get()"]:::callStyle
    call_density_ratios_append["--> density_ratios.append()"]:::callStyle

    subgraph core_benchmark_reporter_py ["?? core/benchmark/reporter.py"]
        core_benchmark_reporter_py_ScientificSignificanceReport["[CLASS] ScientificSignificanceReport"]:::classStyle
        core_benchmark_reporter_py_StatisticalComparator["[CLASS] StatisticalComparator"]:::classStyle
        core_benchmark_reporter_py_StatisticalComparator__interpret_cliffs_delta["_interpret_cliffs_delta()"]:::funcStyle
    call_abs["--> abs()"]:::callStyle
        core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci["_bootstrap_estimator_ci()"]:::funcStyle
    call_np_array["--> np.array()"]:::callStyle
    call_estimator_func["--> estimator_func()"]:::callStyle
    call___choice["--> *.choice()"]:::callStyle
    call_np_percentile["--> np.percentile()"]:::callStyle
        core_benchmark_reporter_py_StatisticalComparator_compare_series["compare_series()"]:::funcStyle
    call_ScientificSignificanceReport["--> ScientificSignificanceReport()"]:::callStyle
    call_cast["--> cast()"]:::callStyle
    call_stats_mannwhitneyu["--> stats.mannwhitneyu()"]:::callStyle
    call_stats_ks_2samp["--> stats.ks_2samp()"]:::callStyle
    call_cls__bootstrap_estimator_ci["--> cls._bootstrap_estimator_ci()"]:::callStyle
        core_benchmark_reporter_py_StatisticalComparator__p95_estimator["_p95_estimator()"]:::funcStyle
    call_cls__interpret_cliffs_delta["--> cls._interpret_cliffs_delta()"]:::callStyle
        core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni["_apply_holm_bonferroni()"]:::funcStyle
    call_reports_items["--> reports.items()"]:::callStyle
    call_items_sort["--> items.sort()"]:::callStyle
    call_replace["--> replace()"]:::callStyle
        core_benchmark_reporter_py_StatisticalComparator_run_stratified_analysis["run_stratified_analysis()"]:::funcStyle
    call_cls_compare_series["--> cls.compare_series()"]:::callStyle
    call_cls__apply_holm_bonferroni["--> cls._apply_holm_bonferroni()"]:::callStyle

    subgraph core_benchmark_semantic_judge_py ["?? core/benchmark/semantic_judge.py"]
        core_benchmark_semantic_judge_py_SemanticJudge["[CLASS] SemanticJudge"]:::classStyle
        core_benchmark_semantic_judge_py_SemanticJudge___init__["__init__()"]:::funcStyle

    subgraph core_benchmark___init___py ["?? core/benchmark/__init__.py"]

    subgraph core_benchmark___main___py ["?? core/benchmark/__main__.py"]

    subgraph core_benchmark_runners_gemini_runner_py ["?? core/benchmark/runners/gemini_runner.py"]
        core_benchmark_runners_gemini_runner_py_DummyContextResolver["[CLASS] DummyContextResolver"]:::classStyle
        core_benchmark_runners_gemini_runner_py_DummyContextResolver_resolve_many["resolve_many()"]:::funcStyle
        core_benchmark_runners_gemini_runner_py_DummyContextResolver_resolve["resolve()"]:::funcStyle
        core_benchmark_runners_gemini_runner_py_GeminiBenchmarkRunner["[CLASS] GeminiBenchmarkRunner"]:::classStyle
        core_benchmark_runners_gemini_runner_py_GeminiBenchmarkRunner___init__["__init__()"]:::funcStyle

    subgraph core_benchmark_runners_groq_runner_py ["?? core/benchmark/runners/groq_runner.py"]
        core_benchmark_runners_groq_runner_py_DummyContextResolver["[CLASS] DummyContextResolver"]:::classStyle
        core_benchmark_runners_groq_runner_py_DummyContextResolver_resolve_many["resolve_many()"]:::funcStyle
        core_benchmark_runners_groq_runner_py_DummyContextResolver_resolve["resolve()"]:::funcStyle
        core_benchmark_runners_groq_runner_py_GroqBenchmarkRunner["[CLASS] GroqBenchmarkRunner"]:::classStyle
        core_benchmark_runners_groq_runner_py_GroqBenchmarkRunner___init__["__init__()"]:::funcStyle

    subgraph core_compiler_assembler_py ["?? core/compiler/assembler.py"]
        core_compiler_assembler_py_RepositoryUnavailableError["[CLASS] RepositoryUnavailableError"]:::classStyle
        core_compiler_assembler_py_PayloadNotFoundError["[CLASS] PayloadNotFoundError"]:::classStyle
        core_compiler_assembler_py_HashMismatchError["[CLASS] HashMismatchError"]:::classStyle
        core_compiler_assembler_py_IntegrityCheckedDocumentRepository["[CLASS] IntegrityCheckedDocumentRepository"]:::classStyle
        core_compiler_assembler_py_IntegrityCheckedDocumentRepository_get_verified_payload["get_verified_payload()"]:::funcStyle
        core_compiler_assembler_py_AssemblyStatus["[CLASS] AssemblyStatus"]:::classStyle
        core_compiler_assembler_py_AssemblyPolicy["[CLASS] AssemblyPolicy"]:::classStyle
        core_compiler_assembler_py_AssemblyReport["[CLASS] AssemblyReport"]:::classStyle
        core_compiler_assembler_py_DocumentAssemblyDecision["[CLASS] DocumentAssemblyDecision"]:::classStyle
        core_compiler_assembler_py_DocumentAssemblyDecision_is_accepted["is_accepted()"]:::funcStyle
        core_compiler_assembler_py_DocumentAssembler["[CLASS] DocumentAssembler"]:::classStyle
        core_compiler_assembler_py_DocumentAssembler___init__["__init__()"]:::funcStyle
        core_compiler_assembler_py_DocumentAssembler__validate_sequence["_validate_sequence()"]:::funcStyle
    call_IncompleteDocumentError["--> IncompleteDocumentError()"]:::callStyle
        core_compiler_assembler_py_DocumentAssembler_assemble["assemble()"]:::funcStyle
    call_self__build_rejection["--> self._build_rejection()"]:::callStyle
    call_self__validate_sequence["--> self._validate_sequence()"]:::callStyle
    call_content_parts_append["--> content_parts.append()"]:::callStyle
    call___get_verified_payload["--> *.get_verified_payload()"]:::callStyle
    call_ReconstructedDocument["--> ReconstructedDocument()"]:::callStyle
    call_AssemblyReport["--> AssemblyReport()"]:::callStyle
    call_DocumentAssemblyDecision["--> DocumentAssemblyDecision()"]:::callStyle
        core_compiler_assembler_py_DocumentAssembler__build_rejection["_build_rejection()"]:::funcStyle

    subgraph core_context_context_resolver_py ["?? core/context/context_resolver.py"]
        core_context_context_resolver_py_ResolvedContext["[CLASS] ResolvedContext"]:::classStyle
        core_context_context_resolver_py_ResolvedContext_depth["depth()"]:::funcStyle
        core_context_context_resolver_py_ContextResolverProtocol["[CLASS] ContextResolverProtocol"]:::classStyle
        core_context_context_resolver_py_ContextResolverProtocol_resolve["resolve()"]:::funcStyle
        core_context_context_resolver_py_ContextResolverProtocol_resolve_many["resolve_many()"]:::funcStyle
        core_context_context_resolver_py_ContextMappingProvider["[CLASS] ContextMappingProvider"]:::classStyle
        core_context_context_resolver_py_ContextMappingProvider_mappings["mappings()"]:::funcStyle
        core_context_context_resolver_py_InMemoryContextResolver["[CLASS] InMemoryContextResolver"]:::classStyle
        core_context_context_resolver_py_InMemoryContextResolver___init__["__init__()"]:::funcStyle
        core_context_context_resolver_py_InMemoryContextResolver_resolve["resolve()"]:::funcStyle
    call_KeyError["--> KeyError()"]:::callStyle
        core_context_context_resolver_py_InMemoryContextResolver_resolve_many["resolve_many()"]:::funcStyle
    call_dict_fromkeys["--> dict.fromkeys()"]:::callStyle
    call_missing_append["--> missing.append()"]:::callStyle

    subgraph core_execution_constants_py ["?? core/execution/constants.py"]

    subgraph core_execution_event_log_py ["?? core/execution/event_log.py"]

    subgraph core_execution_exceptions_py ["?? core/execution/exceptions.py"]
        core_execution_exceptions_py_PipelineIntegrityError["[CLASS] PipelineIntegrityError"]:::classStyle
        core_execution_exceptions_py_IncompleteDocumentError["[CLASS] IncompleteDocumentError"]:::classStyle
        core_execution_exceptions_py_IncompleteDocumentError___init__["__init__()"]:::funcStyle
    call_____init__["--> *.__init__()"]:::callStyle
    call_super["--> super()"]:::callStyle
        core_execution_exceptions_py_OptimisticLockError["[CLASS] OptimisticLockError"]:::classStyle
        core_execution_exceptions_py_LeaseExpiredError["[CLASS] LeaseExpiredError"]:::classStyle
        core_execution_exceptions_py_IllegalStateTransitionError["[CLASS] IllegalStateTransitionError"]:::classStyle
        core_execution_exceptions_py_CircuitOpenError["[CLASS] CircuitOpenError"]:::classStyle
        core_execution_exceptions_py_CircuitOpenError___init__["__init__()"]:::funcStyle
        core_execution_exceptions_py_CircuitTripError["[CLASS] CircuitTripError"]:::classStyle
        core_execution_exceptions_py_TransientAPIError["[CLASS] TransientAPIError"]:::classStyle
        core_execution_exceptions_py_ChunkExecutionError["[CLASS] ChunkExecutionError"]:::classStyle
        core_execution_exceptions_py_ChunkExecutionError___init__["__init__()"]:::funcStyle
        core_execution_exceptions_py_ChunkValidationError["[CLASS] ChunkValidationError"]:::classStyle
        core_execution_exceptions_py_ChunkValidationError___init__["__init__()"]:::funcStyle
        core_execution_exceptions_py_DocumentValidationError["[CLASS] DocumentValidationError"]:::classStyle
        core_execution_exceptions_py_DocumentValidationError___init__["__init__()"]:::funcStyle
        core_execution_exceptions_py_TranslationDomainError["[CLASS] TranslationDomainError"]:::classStyle
        core_execution_exceptions_py_ContextOverflowError["[CLASS] ContextOverflowError"]:::classStyle
        core_execution_exceptions_py_ContextOverflowError___init__["__init__()"]:::funcStyle
        core_execution_exceptions_py_ContextOverflowError___str__["__str__()"]:::funcStyle
    call_____str__["--> *.__str__()"]:::callStyle
        core_execution_exceptions_py_PermanentQuotaRejection["[CLASS] PermanentQuotaRejection"]:::classStyle
        core_execution_exceptions_py_QuotaTimeoutError["[CLASS] QuotaTimeoutError"]:::classStyle

    subgraph core_execution_handlers_py ["?? core/execution/handlers.py"]
        core_execution_handlers_py_DocumentCommandHandler["[CLASS] DocumentCommandHandler"]:::classStyle
        core_execution_handlers_py_DocumentCommandHandler___init__["__init__()"]:::funcStyle
        core_execution_handlers_py_DocumentCommandHandler__get_target_state["_get_target_state()"]:::funcStyle
    call_DocumentState["--> DocumentState()"]:::callStyle
    call_mapping_get["--> mapping.get()"]:::callStyle
    call_type["--> type()"]:::callStyle
    call_TypeError["--> TypeError()"]:::callStyle
        core_execution_handlers_py_DocumentCommandHandler_handle["handle()"]:::funcStyle
    call_self__get_target_state["--> self._get_target_state()"]:::callStyle
    call_FSMValidator_validate["--> FSMValidator.validate()"]:::callStyle
    call___transition_to["--> *.transition_to()"]:::callStyle
        core_execution_handlers_py_ReconciliationCommandHandler["[CLASS] ReconciliationCommandHandler"]:::classStyle
        core_execution_handlers_py_ReconciliationCommandHandler___init__["__init__()"]:::funcStyle
        core_execution_handlers_py_ReconciliationCommandHandler_handle["handle()"]:::funcStyle
    call_self_handle_rematerialize["--> self.handle_rematerialize()"]:::callStyle
    call_self_handle_recover_zombie["--> self.handle_recover_zombie()"]:::callStyle
        core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize["handle_rematerialize()"]:::funcStyle
    call___get_current_epoch["--> *.get_current_epoch()"]:::callStyle
    call___inc["--> *.inc()"]:::callStyle
    call___mark_cqrs_reconciled["--> *.mark_cqrs_reconciled()"]:::callStyle
        core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie["handle_recover_zombie()"]:::funcStyle
    call___mark_zombie_recovered["--> *.mark_zombie_recovered()"]:::callStyle

    subgraph core_execution_invariants_py ["?? core/execution/invariants.py"]

    subgraph core_execution_job_model_py ["?? core/execution/job_model.py"]

    subgraph core_execution_models_py ["?? core/execution/models.py"]
        core_execution_models_py_ProcessingStage["[CLASS] ProcessingStage"]:::classStyle
        core_execution_models_py_ChunkLifecycle["[CLASS] ChunkLifecycle"]:::classStyle
        core_execution_models_py_FailureType["[CLASS] FailureType"]:::classStyle
        core_execution_models_py_ValidationError["[CLASS] ValidationError"]:::classStyle
        core_execution_models_py_ChunkPayload["[CLASS] ChunkPayload"]:::classStyle
        core_execution_models_py_ChunkExecutionEvent["[CLASS] ChunkExecutionEvent"]:::classStyle
        core_execution_models_py_ChunkExecutionEvent_content_hash["content_hash()"]:::funcStyle
    call_base_encode["--> base.encode()"]:::callStyle
        core_execution_models_py_ChunkExecutionEvent_is_assemblable["is_assemblable()"]:::funcStyle

    subgraph core_execution_ports_py ["?? core/execution/ports.py"]
        core_execution_ports_py_ProcessingOutcome["[CLASS] ProcessingOutcome"]:::classStyle
        core_execution_ports_py_ProjectionState["[CLASS] ProjectionState"]:::classStyle
        core_execution_ports_py_EventLifecycle["[CLASS] EventLifecycle"]:::classStyle
        core_execution_ports_py_TaskLease["[CLASS] TaskLease"]:::classStyle
        core_execution_ports_py_ReplayPayload["[CLASS] ReplayPayload"]:::classStyle
        core_execution_ports_py_ProjectionStatus["[CLASS] ProjectionStatus"]:::classStyle
        core_execution_ports_py_ProjectionRecord["[CLASS] ProjectionRecord"]:::classStyle
        core_execution_ports_py_ControlPlanePort["[CLASS] ControlPlanePort"]:::classStyle
        core_execution_ports_py_ControlPlanePort_enqueue_tasks["enqueue_tasks()"]:::funcStyle
        core_execution_ports_py_ControlPlanePort_pick_task["pick_task()"]:::funcStyle
        core_execution_ports_py_ControlPlanePort_acknowledge_execution["acknowledge_execution()"]:::funcStyle
        core_execution_ports_py_ControlPlanePort_abandon_execution["abandon_execution()"]:::funcStyle
        core_execution_ports_py_ControlPlanePort_renew_task_lease["renew_task_lease()"]:::funcStyle
        core_execution_ports_py_EventPlanePort["[CLASS] EventPlanePort"]:::classStyle
        core_execution_ports_py_EventPlanePort_get_replay["get_replay()"]:::funcStyle
        core_execution_ports_py_EventPlanePort_append_wal["append_wal()"]:::funcStyle
        core_execution_ports_py_MaterializedPlanePort["[CLASS] MaterializedPlanePort"]:::classStyle
        core_execution_ports_py_MaterializedPlanePort_get_projection_status["get_projection_status()"]:::funcStyle
        core_execution_ports_py_MaterializedPlanePort_upsert_projection["upsert_projection()"]:::funcStyle
        core_execution_ports_py_MaterializedPlanePort_get_assemblable_chunks["get_assemblable_chunks()"]:::funcStyle

    subgraph core_execution_state_py ["?? core/execution/state.py"]
        core_execution_state_py_DocumentState["[CLASS] DocumentState"]:::classStyle
        core_execution_state_py_FSMValidator["[CLASS] FSMValidator"]:::classStyle
        core_execution_state_py_FSMValidator_validate["validate()"]:::funcStyle
    call_LEGAL_TRANSITIONS_get["--> LEGAL_TRANSITIONS.get()"]:::callStyle
    call_IllegalStateTransitionError["--> IllegalStateTransitionError()"]:::callStyle
        core_execution_state_py_DocumentCommand["[CLASS] DocumentCommand"]:::classStyle
        core_execution_state_py_StartParsingCommand["[CLASS] StartParsingCommand"]:::classStyle
        core_execution_state_py_StartProcessingCommand["[CLASS] StartProcessingCommand"]:::classStyle
        core_execution_state_py_MarkAssemblyReadyCommand["[CLASS] MarkAssemblyReadyCommand"]:::classStyle
        core_execution_state_py_StartAssemblyCommand["[CLASS] StartAssemblyCommand"]:::classStyle
        core_execution_state_py_MarkCompilationReadyCommand["[CLASS] MarkCompilationReadyCommand"]:::classStyle
        core_execution_state_py_StartCompilationCommand["[CLASS] StartCompilationCommand"]:::classStyle
        core_execution_state_py_CompleteDocumentCommand["[CLASS] CompleteDocumentCommand"]:::classStyle
        core_execution_state_py_FailDocumentCommand["[CLASS] FailDocumentCommand"]:::classStyle
        core_execution_state_py_CancelDocumentCommand["[CLASS] CancelDocumentCommand"]:::classStyle
        core_execution_state_py_StallDocumentCommand["[CLASS] StallDocumentCommand"]:::classStyle
        core_execution_state_py_ResumeDocumentCommand["[CLASS] ResumeDocumentCommand"]:::classStyle
        core_execution_state_py_ReconcilerCommand["[CLASS] ReconcilerCommand"]:::classStyle
        core_execution_state_py_RecoverZombieTaskCommand["[CLASS] RecoverZombieTaskCommand"]:::classStyle
        core_execution_state_py_RematerializeTaskCommand["[CLASS] RematerializeTaskCommand"]:::classStyle

    subgraph core_execution_state_mapping_py ["?? core/execution/state_mapping.py"]
        core_execution_state_mapping_py_RecoveredJobSnapshot["[CLASS] RecoveredJobSnapshot"]:::classStyle

    subgraph core_execution___init___py ["?? core/execution/__init__.py"]

    subgraph core_healing_base_py ["?? core/healing/base.py"]
        core_healing_base_py_BaseHealingStrategy["[CLASS] BaseHealingStrategy"]:::classStyle
        core_healing_base_py_BaseHealingStrategy_invariant_family["invariant_family()"]:::funcStyle
        core_healing_base_py_BaseHealingStrategy_priority["priority()"]:::funcStyle
        core_healing_base_py_BaseHealingStrategy_heal["heal()"]:::funcStyle

    subgraph core_healing_config_py ["?? core/healing/config.py"]
        core_healing_config_py_HealingPolicy["[CLASS] HealingPolicy"]:::classStyle

    subgraph core_healing_models_py ["?? core/healing/models.py"]
        core_healing_models_py_HealingContractViolationError["[CLASS] HealingContractViolationError"]:::classStyle
        core_healing_models_py_HealingOutcome["[CLASS] HealingOutcome"]:::classStyle
        core_healing_models_py_HealingResult["[CLASS] HealingResult"]:::classStyle
        core_healing_models_py_HealingResult_final_text["final_text()"]:::funcStyle
        core_healing_models_py_HealingContext["[CLASS] HealingContext"]:::classStyle
        core_healing_models_py_HealingContext___post_init__["__post_init__()"]:::funcStyle
    call_HealingContractViolationError["--> HealingContractViolationError()"]:::callStyle

    subgraph core_healing_pipeline_py ["?? core/healing/pipeline.py"]
        core_healing_pipeline_py_HealingPipeline["[CLASS] HealingPipeline"]:::classStyle
        core_healing_pipeline_py_HealingPipeline___init__["__init__()"]:::funcStyle
    call_HealingTelemetryRegistry["--> HealingTelemetryRegistry()"]:::callStyle
        core_healing_pipeline_py_HealingPipeline_heal_and_revalidate["heal_and_revalidate()"]:::funcStyle
    call_HealingResult["--> HealingResult()"]:::callStyle
    call___record["--> *.record()"]:::callStyle
    call_HealingEvent["--> HealingEvent()"]:::callStyle
    call_strategy_heal["--> strategy.heal()"]:::callStyle
    call___validate_chunk["--> *.validate_chunk()"]:::callStyle

    subgraph core_healing_telemetry_py ["?? core/healing/telemetry.py"]
        core_healing_telemetry_py_HealingEvent["[CLASS] HealingEvent"]:::classStyle
        core_healing_telemetry_py_HealingEvent_to_dict["to_dict()"]:::funcStyle
    call_asdict["--> asdict()"]:::callStyle
        core_healing_telemetry_py_HealingTelemetryRegistry["[CLASS] HealingTelemetryRegistry"]:::classStyle
        core_healing_telemetry_py_HealingTelemetryRegistry___init__["__init__()"]:::funcStyle
    call_deque["--> deque()"]:::callStyle
    call_threading_Lock["--> threading.Lock()"]:::callStyle
        core_healing_telemetry_py_HealingTelemetryRegistry_record["record()"]:::funcStyle
    call___append["--> *.append()"]:::callStyle
    call_self__update_aggregates_unlocked["--> self._update_aggregates_unlocked()"]:::callStyle
    call_event_to_dict["--> event.to_dict()"]:::callStyle
        core_healing_telemetry_py_HealingTelemetryRegistry__update_aggregates_unlocked["_update_aggregates_unlocked()"]:::funcStyle
        core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics["get_aggregate_metrics()"]:::funcStyle
    call_v_copy["--> v.copy()"]:::callStyle
    call___items["--> *.items()"]:::callStyle
    call_snapshot_items["--> snapshot.items()"]:::callStyle
        core_healing_telemetry_py_HealingTelemetryRegistry_get_events["get_events()"]:::funcStyle

    subgraph core_healing_testing_factories_py ["?? core/healing/testing_factories.py"]
        core_healing_testing_factories_py_make_test_healing_context["[FUNC] make_test_healing_context()"]:::funcStyle
    call_ValidationContext["--> ValidationContext()"]:::callStyle
    call_ValidationResult["--> ValidationResult()"]:::callStyle
    call_HealingContext["--> HealingContext()"]:::callStyle

    subgraph core_healing___init___py ["?? core/healing/__init__.py"]

    subgraph core_healing_strategies_markdown_leakage_py ["?? core/healing/strategies/markdown_leakage.py"]
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy["[CLASS] MarkdownLeakageHealingStrategy"]:::classStyle
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_invariant_family["invariant_family()"]:::funcStyle
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_priority["priority()"]:::funcStyle
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal["heal()"]:::funcStyle
    call_pattern_match["--> pattern.match()"]:::callStyle

    subgraph core_healing_strategies_meta_text_leakage_py ["?? core/healing/strategies/meta_text_leakage.py"]
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy["[CLASS] MetaTextLeakageHealingStrategy"]:::classStyle
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_invariant_family["invariant_family()"]:::funcStyle
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_priority["priority()"]:::funcStyle
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal["heal()"]:::funcStyle
    call_pattern_sub["--> pattern.sub()"]:::callStyle
    call_cleaned_strip["--> cleaned.strip()"]:::callStyle

    subgraph core_healing_strategies_structural_py ["?? core/healing/strategies/structural.py"]
        core_healing_strategies_structural_py_MathState["[CLASS] MathState"]:::classStyle
        core_healing_strategies_structural_py_EOFBraceClosureStrategy["[CLASS] EOFBraceClosureStrategy"]:::classStyle
        core_healing_strategies_structural_py_EOFBraceClosureStrategy___init__["__init__()"]:::funcStyle
        core_healing_strategies_structural_py_EOFBraceClosureStrategy_invariant_family["invariant_family()"]:::funcStyle
        core_healing_strategies_structural_py_EOFBraceClosureStrategy_priority["priority()"]:::funcStyle
        core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal["heal()"]:::funcStyle
    call_verbatim_block_pattern_sub["--> verbatim_block_pattern.sub()"]:::callStyle
    call_inline_verb_pattern_sub["--> inline_verb_pattern.sub()"]:::callStyle
        core_healing_strategies_structural_py_EOFMathClosureStrategy["[CLASS] EOFMathClosureStrategy"]:::classStyle
        core_healing_strategies_structural_py_EOFMathClosureStrategy___init__["__init__()"]:::funcStyle
        core_healing_strategies_structural_py_EOFMathClosureStrategy_invariant_family["invariant_family()"]:::funcStyle
        core_healing_strategies_structural_py_EOFMathClosureStrategy_priority["priority()"]:::funcStyle
        core_healing_strategies_structural_py_EOFMathClosureStrategy_heal["heal()"]:::funcStyle
    call_original_rstrip["--> original.rstrip()"]:::callStyle
    call_base_text_endswith["--> base_text.endswith()"]:::callStyle

    subgraph core_metrics_exporters_py ["?? core/metrics/exporters.py"]
        core_metrics_exporters_py_MetricsExporter["[CLASS] MetricsExporter"]:::classStyle
        core_metrics_exporters_py_MetricsExporter_export["export()"]:::funcStyle
        core_metrics_exporters_py_ConsoleMetricsExporter["[CLASS] ConsoleMetricsExporter"]:::classStyle
        core_metrics_exporters_py_ConsoleMetricsExporter_export["export()"]:::funcStyle
    call_print["--> print()"]:::callStyle
        core_metrics_exporters_py_JsonMetricsExporter["[CLASS] JsonMetricsExporter"]:::classStyle
        core_metrics_exporters_py_JsonMetricsExporter___init__["__init__()"]:::funcStyle
        core_metrics_exporters_py_JsonMetricsExporter_export["export()"]:::funcStyle
    call_dataclasses_asdict["--> dataclasses.asdict()"]:::callStyle

    subgraph core_metrics_measure_density_py ["?? core/metrics/measure_density.py"]
        core_metrics_measure_density_py_measure_pdf_density["[FUNC] measure_pdf_density()"]:::funcStyle
    call_char_counts_append["--> char_counts.append()"]:::callStyle

    subgraph core_metrics_metrics_py ["?? core/metrics/metrics.py"]
        core_metrics_metrics_py_Metrics["[CLASS] Metrics"]:::classStyle
        core_metrics_metrics_py_Metrics___init__["__init__()"]:::funcStyle
    call_defaultdict["--> defaultdict()"]:::callStyle
        core_metrics_metrics_py_Metrics_inc["inc()"]:::funcStyle
        core_metrics_metrics_py_Metrics_observe["observe()"]:::funcStyle
        core_metrics_metrics_py_Metrics_summary["summary()"]:::funcStyle

    subgraph core_metrics_pricing_py ["?? core/metrics/pricing.py"]
        core_metrics_pricing_py_PricingEngine["[CLASS] PricingEngine"]:::classStyle
        core_metrics_pricing_py_PricingEngine_calculate_cost["calculate_cost()"]:::funcStyle
    call_model_name_startswith["--> model_name.startswith()"]:::callStyle

    subgraph core_metrics_summary_py ["?? core/metrics/summary.py"]
        core_metrics_summary_py_TranslationAuditSummary["[CLASS] TranslationAuditSummary"]:::classStyle
        core_metrics_summary_py_SummaryBuilder["[CLASS] SummaryBuilder"]:::classStyle
        core_metrics_summary_py_SummaryBuilder__percentile["_percentile()"]:::funcStyle
        core_metrics_summary_py_SummaryBuilder_build["build()"]:::funcStyle
    call_utilization_ratios_append["--> utilization_ratios.append()"]:::callStyle
    call_quota_waits_append["--> quota_waits.append()"]:::callStyle
    call_quota_attempts_append["--> quota_attempts.append()"]:::callStyle
    call_PricingEngine_calculate_cost["--> PricingEngine.calculate_cost()"]:::callStyle
    call_TranslationAuditSummary["--> TranslationAuditSummary()"]:::callStyle
    call_SummaryBuilder__percentile["--> SummaryBuilder._percentile()"]:::callStyle

    subgraph core_normalization_base_py ["?? core/normalization/base.py"]
        core_normalization_base_py_WarningEntry["[CLASS] WarningEntry"]:::classStyle
        core_normalization_base_py_NormalizerResult["[CLASS] NormalizerResult"]:::classStyle
        core_normalization_base_py_NormalizerTrace["[CLASS] NormalizerTrace"]:::classStyle
        core_normalization_base_py_NormalizationReport["[CLASS] NormalizationReport"]:::classStyle
        core_normalization_base_py_NormalizationEvent["[CLASS] NormalizationEvent"]:::classStyle
        core_normalization_base_py_BaseNormalizer["[CLASS] BaseNormalizer"]:::classStyle
        core_normalization_base_py_BaseNormalizer_normalizer_id["normalizer_id()"]:::funcStyle
        core_normalization_base_py_BaseNormalizer_normalizer_version["normalizer_version()"]:::funcStyle
        core_normalization_base_py_BaseNormalizer_signature["signature()"]:::funcStyle
        core_normalization_base_py_BaseNormalizer_normalize["normalize()"]:::funcStyle

    subgraph core_normalization_bootstrap_py ["?? core/normalization/bootstrap.py"]
        core_normalization_bootstrap_py_bootstrap_normalization_layer["[FUNC] bootstrap_normalization_layer()"]:::funcStyle
    call_NormalizationPolicyRegistry_get_instance["--> NormalizationPolicyRegistry.get_instance()"]:::callStyle
    call___find_spec["--> *.find_spec()"]:::callStyle
    call_NormalizationPolicy["--> NormalizationPolicy()"]:::callStyle
    call_paragraph_policy_append["--> paragraph_policy.append()"]:::callStyle
    call_ParagraphNormalizer["--> ParagraphNormalizer()"]:::callStyle
    call_registry_register_policy["--> registry.register_policy()"]:::callStyle
    call_registry_map_type_to_domain["--> registry.map_type_to_domain()"]:::callStyle
    call_math_policy_append["--> math_policy.append()"]:::callStyle
    call_MathDomainNormalizer["--> MathDomainNormalizer()"]:::callStyle
    call_registry_freeze["--> registry.freeze()"]:::callStyle

    subgraph core_normalization_classifier_py ["?? core/normalization/classifier.py"]
        core_normalization_classifier_py_SemanticNodeClassifier["[CLASS] SemanticNodeClassifier"]:::classStyle
        core_normalization_classifier_py_SemanticNodeClassifier___init__["__init__()"]:::funcStyle
        core_normalization_classifier_py_SemanticNodeClassifier__infer_heading["_infer_heading()"]:::funcStyle
    call_text_stripped_startswith["--> text_stripped.startswith()"]:::callStyle
    call_node_model_copy["--> node.model_copy()"]:::callStyle
        core_normalization_classifier_py_SemanticNodeClassifier_classify_node["classify_node()"]:::funcStyle
    call_text_strip["--> text.strip()"]:::callStyle
    call_self__infer_heading["--> self._infer_heading()"]:::callStyle
    call_env_match_group["--> env_match.group()"]:::callStyle
    call_self__mutate_node_type["--> self._mutate_node_type()"]:::callStyle
    call___findall["--> *.findall()"]:::callStyle
    call___finditer["--> *.finditer()"]:::callStyle
    call_inner_content_isdigit["--> inner_content.isdigit()"]:::callStyle
        core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type["_mutate_node_type()"]:::funcStyle
        core_normalization_classifier_py_SemanticNodeClassifier_classify_batch["classify_batch()"]:::funcStyle
    call_self_classify_node["--> self.classify_node()"]:::callStyle

    subgraph core_normalization_html_decoder_py ["?? core/normalization/html_decoder.py"]

    subgraph core_normalization_latex_sanitizer_py ["?? core/normalization/latex_sanitizer.py"]
        core_normalization_latex_sanitizer_py_InlineMathProtector["[CLASS] InlineMathProtector"]:::classStyle
        core_normalization_latex_sanitizer_py_InlineMathProtector_mask["mask()"]:::funcStyle
        core_normalization_latex_sanitizer_py_InlineMathProtector__replacer["_replacer()"]:::funcStyle
    call___sub["--> *.sub()"]:::callStyle
        core_normalization_latex_sanitizer_py_InlineMathProtector_restore["restore()"]:::funcStyle
    call_mapping_items["--> mapping.items()"]:::callStyle
    call___split["--> *.split()"]:::callStyle
    call_token_strip["--> token.strip()"]:::callStyle
    call_safe_token_pattern_sub["--> safe_token_pattern.sub()"]:::callStyle

    subgraph core_normalization_normalizer_py ["?? core/normalization/normalizer.py"]
        core_normalization_normalizer_py_TextNormalizer["[CLASS] TextNormalizer"]:::classStyle
        core_normalization_normalizer_py_TextNormalizer__decode_html["_decode_html()"]:::funcStyle
        core_normalization_normalizer_py_TextNormalizer__normalize_unicode["_normalize_unicode()"]:::funcStyle
    call_unicodedata_normalize["--> unicodedata.normalize()"]:::callStyle
        core_normalization_normalizer_py_TextNormalizer__strip_control_chars["_strip_control_chars()"]:::funcStyle
        core_normalization_normalizer_py_TextNormalizer_normalize["normalize()"]:::funcStyle
    call_step["--> step()"]:::callStyle

    subgraph core_normalization_pipeline_py ["?? core/normalization/pipeline.py"]
        core_normalization_pipeline_py_NormalizationPipeline["[CLASS] NormalizationPipeline"]:::classStyle
        core_normalization_pipeline_py_NormalizationPipeline___init__["__init__()"]:::funcStyle
    call_Lock["--> Lock()"]:::callStyle
        core_normalization_pipeline_py_NormalizationPipeline_dropped_events_count["dropped_events_count()"]:::funcStyle
        core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash["_compute_deterministic_hash()"]:::funcStyle
    call_text_encode["--> text.encode()"]:::callStyle
    call_json_payload_encode["--> json_payload.encode()"]:::callStyle
        core_normalization_pipeline_py_NormalizationPipeline_process_node["process_node()"]:::funcStyle
    call___get_policy_for_type["--> *.get_policy_for_type()"]:::callStyle
    call_self__compute_deterministic_hash["--> self._compute_deterministic_hash()"]:::callStyle
    call_NormalizationReport["--> NormalizationReport()"]:::callStyle
    call_normalizer_normalize["--> normalizer.normalize()"]:::callStyle
    call_traces_append["--> traces.append()"]:::callStyle
    call_NormalizerTrace["--> NormalizerTrace()"]:::callStyle
    call_warnings_extend["--> warnings.extend()"]:::callStyle
    call_hard_fails_extend["--> hard_fails.extend()"]:::callStyle
    call_NormalizationEvent["--> NormalizationEvent()"]:::callStyle
    call___put_nowait["--> *.put_nowait()"]:::callStyle
        core_normalization_pipeline_py_NormalizationPipeline_process_batch["process_batch()"]:::funcStyle
    call_self_process_node["--> self.process_node()"]:::callStyle

    subgraph core_normalization_registry_py ["?? core/normalization/registry.py"]
        core_normalization_registry_py_NormalizationDomain["[CLASS] NormalizationDomain"]:::classStyle
        core_normalization_registry_py_NormalizationPolicy["[CLASS] NormalizationPolicy"]:::classStyle
        core_normalization_registry_py_NormalizationPolicy___init__["__init__()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicy_append["append()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry["[CLASS] NormalizationPolicyRegistry"]:::classStyle
        core_normalization_registry_py_NormalizationPolicyRegistry___new__["__new__()"]:::funcStyle
    call_____new__["--> *.__new__()"]:::callStyle
    call____init_registry["--> *._init_registry()"]:::callStyle
        core_normalization_registry_py_NormalizationPolicyRegistry__init_registry["_init_registry()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_is_bootstrapped["is_bootstrapped()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_map_type_to_domain["map_type_to_domain()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_register_policy["register_policy()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_get_policy_for_type["get_policy_for_type()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_freeze["freeze()"]:::funcStyle
        core_normalization_registry_py_NormalizationPolicyRegistry_get_instance["get_instance()"]:::funcStyle

    subgraph core_normalization_unicode_py ["?? core/normalization/unicode.py"]

    subgraph core_normalization_enrichers_context_enricher_py ["?? core/normalization/enrichers/context_enricher.py"]
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher["[CLASS] HierarchicalContextEnricher"]:::classStyle
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher___init__["__init__()"]:::funcStyle
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher__validate_registry["_validate_registry()"]:::funcStyle
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document["enrich_document()"]:::funcStyle
    call___lstrip["--> *.lstrip()"]:::callStyle
    call_warnings_append["--> warnings.append()"]:::callStyle
    call_WarningEntry["--> WarningEntry()"]:::callStyle
    call_hierarchy_stack_append["--> hierarchy_stack.append()"]:::callStyle
    call_enriched_nodes_append["--> enriched_nodes.append()"]:::callStyle
    call_hashlib_blake2b["--> hashlib.blake2b()"]:::callStyle
    call_self__validate_registry["--> self._validate_registry()"]:::callStyle

    subgraph core_normalization_fixers_asset_placeholder_py ["?? core/normalization/fixers/asset_placeholder.py"]
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder["[CLASS] StructuralAssetPlaceholder"]:::classStyle
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder___init__["__init__()"]:::funcStyle
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalizer_id["normalizer_id()"]:::funcStyle
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalizer_version["normalizer_version()"]:::funcStyle
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize["normalize()"]:::funcStyle
    call_NormalizerResult["--> NormalizerResult()"]:::callStyle
    call_node_type_upper["--> node_type.upper()"]:::callStyle
    call_asset_type_lower["--> asset_type.lower()"]:::callStyle

    subgraph core_normalization_fixers_math_pipeline_py ["?? core/normalization/fixers/math_pipeline.py"]
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker["[CLASS] ProtectedRegionMasker"]:::classStyle
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim["_scan_inline_verbatim()"]:::funcStyle
    call_cmd_pattern_match["--> cmd_pattern.match()"]:::callStyle
    call_result_append["--> result.append()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_mask["mask()"]:::funcStyle
    call_ProtectedRegionMasker__scan_inline_verbatim["--> ProtectedRegionMasker._scan_inline_verbatim()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_replacer["replacer()"]:::funcStyle
    call_env_pattern_sub["--> env_pattern.sub()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer["[CLASS] ProtectedRegionRestorer"]:::classStyle
        core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer_restore["restore()"]:::funcStyle
    call_vault_items["--> vault.items()"]:::callStyle
    call_restored_text_replace["--> restored_text.replace()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_MathDelimiterValidator["[CLASS] MathDelimiterValidator"]:::classStyle
        core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate["validate()"]:::funcStyle
        core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator["[CLASS] MathEnvironmentValidator"]:::classStyle
        core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate["validate()"]:::funcStyle
    call_env_token_finditer["--> env_token.finditer()"]:::callStyle
    call_match_groups["--> match.groups()"]:::callStyle
    call_stack_append["--> stack.append()"]:::callStyle
    call_stack_pop["--> stack.pop()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_MathHtmlPurifier["[CLASS] MathHtmlPurifier"]:::classStyle
        core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify["purify()"]:::funcStyle
    call_BeautifulSoup["--> BeautifulSoup()"]:::callStyle
    call_soup_find_all["--> soup.find_all()"]:::callStyle
    call_tag_get_text["--> tag.get_text()"]:::callStyle
    call_raw_startswith["--> raw.startswith()"]:::callStyle
    call_raw_endswith["--> raw.endswith()"]:::callStyle
    call_tag_replace_with["--> tag.replace_with()"]:::callStyle
    call___endswith["--> *.endswith()"]:::callStyle
    call_tag_unwrap["--> tag.unwrap()"]:::callStyle
    call_HTMLFormatter["--> HTMLFormatter()"]:::callStyle
    call_soup_decode_contents["--> soup.decode_contents()"]:::callStyle
        core_normalization_fixers_math_pipeline_py_DeprecatedDelimiterConverter["[CLASS] DeprecatedDelimiterConverter"]:::classStyle
        core_normalization_fixers_math_pipeline_py_DeprecatedDelimiterConverter_convert["convert()"]:::funcStyle
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer["[CLASS] MathDomainNormalizer"]:::classStyle
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer___init__["__init__()"]:::funcStyle
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalizer_id["normalizer_id()"]:::funcStyle
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalizer_version["normalizer_version()"]:::funcStyle
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize["normalize()"]:::funcStyle
    call_ProtectedRegionMasker_mask["--> ProtectedRegionMasker.mask()"]:::callStyle
    call_MathDelimiterValidator_validate["--> MathDelimiterValidator.validate()"]:::callStyle
    call_MathEnvironmentValidator_validate["--> MathEnvironmentValidator.validate()"]:::callStyle
    call_MathHtmlPurifier_purify["--> MathHtmlPurifier.purify()"]:::callStyle
    call_DeprecatedDelimiterConverter_convert["--> DeprecatedDelimiterConverter.convert()"]:::callStyle
    call_ProtectedRegionRestorer_restore["--> ProtectedRegionRestorer.restore()"]:::callStyle
    call_metrics_items["--> metrics.items()"]:::callStyle

    subgraph core_normalization_fixers_paragraph_normalizer_py ["?? core/normalization/fixers/paragraph_normalizer.py"]
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer["[CLASS] ParagraphNormalizer"]:::classStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer___init__["__init__()"]:::funcStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalizer_id["normalizer_id()"]:::funcStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalizer_version["normalizer_version()"]:::funcStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__check_domain_anomalies["_check_domain_anomalies()"]:::funcStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom["_normalize_html_dom()"]:::funcStyle
    call_comment_extract["--> comment.extract()"]:::callStyle
    call_raw_text_startswith["--> raw_text.startswith()"]:::callStyle
    call_raw_text_endswith["--> raw_text.endswith()"]:::callStyle
    call_tag_insert_before["--> tag.insert_before()"]:::callStyle
    call_tag_insert_after["--> tag.insert_after()"]:::callStyle
    call_tag_decompose["--> tag.decompose()"]:::callStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_markdown_syntax["_normalize_markdown_syntax()"]:::funcStyle
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize["normalize()"]:::funcStyle
    call_self__check_domain_anomalies["--> self._check_domain_anomalies()"]:::callStyle
    call_self__normalize_html_dom["--> self._normalize_html_dom()"]:::callStyle
    call_self__normalize_markdown_syntax["--> self._normalize_markdown_syntax()"]:::callStyle
    call_fixes_map_items["--> fixes_map.items()"]:::callStyle

    subgraph core_normalization_validators_ast_integrity_py ["?? core/normalization/validators/ast_integrity.py"]
        core_normalization_validators_ast_integrity_py_ASTIntegrityValidator["[CLASS] ASTIntegrityValidator"]:::classStyle
        core_normalization_validators_ast_integrity_py_ASTIntegrityValidator___init__["__init__()"]:::funcStyle
        core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast["validate_ast()"]:::funcStyle
    call___count["--> *.count()"]:::callStyle

    subgraph core_pipeline_job_py ["?? core/pipeline/job.py"]
        core_pipeline_job_py_JobStatus["[CLASS] JobStatus"]:::classStyle
        core_pipeline_job_py_PipelineStep["[CLASS] PipelineStep"]:::classStyle
        core_pipeline_job_py_TranslationJob["[CLASS] TranslationJob"]:::classStyle
        core_pipeline_job_py_TranslationJob_mark_started["mark_started()"]:::funcStyle
    call_datetime_now["--> datetime.now()"]:::callStyle
        core_pipeline_job_py_TranslationJob_mark_processing["mark_processing()"]:::funcStyle
    call_self_mark_started["--> self.mark_started()"]:::callStyle
        core_pipeline_job_py_TranslationJob_enter_step["enter_step()"]:::funcStyle
        core_pipeline_job_py_TranslationJob_mark_completed["mark_completed()"]:::funcStyle
        core_pipeline_job_py_TranslationJob_mark_failed["mark_failed()"]:::funcStyle

    subgraph core_pipeline_orchestrator_py ["?? core/pipeline/orchestrator.py"]
        core_pipeline_orchestrator_py_PipelineResult["[CLASS] PipelineResult"]:::classStyle
        core_pipeline_orchestrator_py_ParserProtocol["[CLASS] ParserProtocol"]:::classStyle
        core_pipeline_orchestrator_py_ParserProtocol_parse["parse()"]:::funcStyle
        core_pipeline_orchestrator_py_ChunkerProtocol["[CLASS] ChunkerProtocol"]:::classStyle
        core_pipeline_orchestrator_py_ChunkerProtocol_chunk["chunk()"]:::funcStyle
        core_pipeline_orchestrator_py_DispatcherProtocol["[CLASS] DispatcherProtocol"]:::classStyle
        core_pipeline_orchestrator_py_AssemblerProtocol["[CLASS] AssemblerProtocol"]:::classStyle
        core_pipeline_orchestrator_py_AssemblerProtocol_assemble["assemble()"]:::funcStyle
        core_pipeline_orchestrator_py_AuditBuilderProtocol["[CLASS] AuditBuilderProtocol"]:::classStyle
        core_pipeline_orchestrator_py_AuditBuilderProtocol_build["build()"]:::funcStyle
        core_pipeline_orchestrator_py_DocumentRepositoryProtocol["[CLASS] DocumentRepositoryProtocol"]:::classStyle
        core_pipeline_orchestrator_py_DocumentRepositoryProtocol_save_batch["save_batch()"]:::funcStyle
        core_pipeline_orchestrator_py_TranslationPipeline["[CLASS] TranslationPipeline"]:::classStyle
        core_pipeline_orchestrator_py_TranslationPipeline___init__["__init__()"]:::funcStyle

    subgraph core_pipeline_state_store_py ["?? core/pipeline/state_store.py"]
        core_pipeline_state_store_py_StateStoreProtocol["[CLASS] StateStoreProtocol"]:::classStyle
        core_pipeline_state_store_py_StateStoreProtocol_save["save()"]:::funcStyle
        core_pipeline_state_store_py_StateStoreProtocol_load["load()"]:::funcStyle
        core_pipeline_state_store_py_FSMStateStore["[CLASS] FSMStateStore"]:::classStyle
        core_pipeline_state_store_py_FSMStateStore___init__["__init__()"]:::funcStyle
        core_pipeline_state_store_py_FSMStateStore_load["load()"]:::funcStyle
    call___get_by_document_id["--> *.get_by_document_id()"]:::callStyle
    call_RecoveredJobSnapshot["--> RecoveredJobSnapshot()"]:::callStyle
        core_pipeline_state_store_py_FSMStateStore_save["save()"]:::funcStyle
    call_cmd_class["--> cmd_class()"]:::callStyle

    subgraph core_pipeline___init___py ["?? core/pipeline/__init__.py"]

    subgraph core_resilience_circuit_breaker_py ["?? core/resilience/circuit_breaker.py"]
        core_resilience_circuit_breaker_py_CircuitState["[CLASS] CircuitState"]:::classStyle
        core_resilience_circuit_breaker_py_GlobalCircuitBreaker["[CLASS] GlobalCircuitBreaker"]:::classStyle
        core_resilience_circuit_breaker_py_GlobalCircuitBreaker___init__["__init__()"]:::funcStyle
        core_resilience_circuit_breaker_py_GlobalCircuitBreaker__prune_window["_prune_window()"]:::funcStyle
    call___popleft["--> *.popleft()"]:::callStyle
        core_resilience_circuit_breaker_py_CircuitBreakerRegistry["[CLASS] CircuitBreakerRegistry"]:::classStyle
        core_resilience_circuit_breaker_py_CircuitBreakerRegistry_get_breaker["get_breaker()"]:::funcStyle
    call_GlobalCircuitBreaker["--> GlobalCircuitBreaker()"]:::callStyle

    subgraph core_telemetry_analyzer_py ["?? core/telemetry/analyzer.py"]
        core_telemetry_analyzer_py_TelemetryAnalyzer["[CLASS] TelemetryAnalyzer"]:::classStyle
        core_telemetry_analyzer_py_TelemetryAnalyzer___init__["__init__()"]:::funcStyle
    call_SLOConfig["--> SLOConfig()"]:::callStyle
        core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar["_query_scalar()"]:::funcStyle
        core_telemetry_analyzer_py_TelemetryAnalyzer__query_list["_query_list()"]:::funcStyle
        core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report["generate_report()"]:::funcStyle
    call_self__query_scalar["--> self._query_scalar()"]:::callStyle
    call_ProductionHealthReport["--> ProductionHealthReport()"]:::callStyle
    call_self__query_list["--> self._query_list()"]:::callStyle
    call_violations_append["--> violations.append()"]:::callStyle
    call_SLOViolation["--> SLOViolation()"]:::callStyle

    subgraph core_telemetry_gates_py ["?? core/telemetry/gates.py"]
        core_telemetry_gates_py_SystemHealthState["[CLASS] SystemHealthState"]:::classStyle
        core_telemetry_gates_py_HealthGateEvaluator["[CLASS] HealthGateEvaluator"]:::classStyle
        core_telemetry_gates_py_HealthGateEvaluator_evaluate["evaluate()"]:::funcStyle
        core_telemetry_gates_py_HealthGateEvaluator_enforce["enforce()"]:::funcStyle
    call_HealthGateEvaluator_evaluate["--> HealthGateEvaluator.evaluate()"]:::callStyle

    subgraph core_telemetry_gateway_py ["?? core/telemetry/gateway.py"]
        core_telemetry_gateway_py_SQLiteTelemetryGateway["[CLASS] SQLiteTelemetryGateway"]:::classStyle
        core_telemetry_gateway_py_SQLiteTelemetryGateway___init__["__init__()"]:::funcStyle
    call_asyncio_Queue["--> asyncio.Queue()"]:::callStyle
    call_self__init_db["--> self._init_db()"]:::callStyle
        core_telemetry_gateway_py_SQLiteTelemetryGateway__init_db["_init_db()"]:::funcStyle
        core_telemetry_gateway_py_SQLiteTelemetryGateway_emit["emit()"]:::funcStyle
        core_telemetry_gateway_py_SQLiteTelemetryGateway__write_batch["_write_batch()"]:::funcStyle
    call_conn_executemany["--> conn.executemany()"]:::callStyle

    subgraph core_telemetry_models_py ["?? core/telemetry/models.py"]
        core_telemetry_models_py_TelemetryEventType["[CLASS] TelemetryEventType"]:::classStyle
        core_telemetry_models_py_ProviderSelectionReason["[CLASS] ProviderSelectionReason"]:::classStyle
        core_telemetry_models_py_ProductionTelemetryEvent["[CLASS] ProductionTelemetryEvent"]:::classStyle
        core_telemetry_models_py_SLOConfig["[CLASS] SLOConfig"]:::classStyle
        core_telemetry_models_py_SLOViolation["[CLASS] SLOViolation"]:::classStyle
        core_telemetry_models_py_ProductionHealthReport["[CLASS] ProductionHealthReport"]:::classStyle

    subgraph core_utils_config_py ["?? core/utils/config.py"]

    subgraph core_utils_fs_py ["?? core/utils/fs.py"]
        core_utils_fs_py_ensure_parent_dir["[FUNC] ensure_parent_dir()"]:::funcStyle

    subgraph core_utils_logger_py ["?? core/utils/logger.py"]
        core_utils_logger_py_JsonFormatter["[CLASS] JsonFormatter"]:::classStyle
        core_utils_logger_py_JsonFormatter_format["format()"]:::funcStyle
    call_time_strftime["--> time.strftime()"]:::callStyle
    call_time_gmtime["--> time.gmtime()"]:::callStyle
    call_record_getMessage["--> record.getMessage()"]:::callStyle
    call_log_record_update["--> log_record.update()"]:::callStyle
        core_utils_logger_py_setup_logger["[FUNC] setup_logger()"]:::funcStyle
    call_logging_getLogger["--> logging.getLogger()"]:::callStyle
    call_logger_setLevel["--> logger.setLevel()"]:::callStyle
    call_logging_StreamHandler["--> logging.StreamHandler()"]:::callStyle
    call_handler_setFormatter["--> handler.setFormatter()"]:::callStyle
    call_JsonFormatter["--> JsonFormatter()"]:::callStyle

    subgraph core_utils_telemetry_py ["?? core/utils/telemetry.py"]
        core_utils_telemetry_py_DistributedContextFilter["[CLASS] DistributedContextFilter"]:::classStyle
        core_utils_telemetry_py_DistributedContextFilter_filter["filter()"]:::funcStyle
    call_ctx_execution_id_get["--> ctx_execution_id.get()"]:::callStyle
    call_ctx_worker_id_get["--> ctx_worker_id.get()"]:::callStyle
    call_ctx_task_id_get["--> ctx_task_id.get()"]:::callStyle
    call_ctx_node_id_get["--> ctx_node_id.get()"]:::callStyle
        core_utils_telemetry_py_JSONFormatter["[CLASS] JSONFormatter"]:::classStyle
        core_utils_telemetry_py_JSONFormatter_format["format()"]:::funcStyle
    call___isoformat["--> *.isoformat()"]:::callStyle
    call_datetime_fromtimestamp["--> datetime.fromtimestamp()"]:::callStyle
    call_self_formatException["--> self.formatException()"]:::callStyle
        core_utils_telemetry_py_setup_distributed_logger["[FUNC] setup_distributed_logger()"]:::funcStyle
    call_handler_addFilter["--> handler.addFilter()"]:::callStyle
    call_DistributedContextFilter["--> DistributedContextFilter()"]:::callStyle
    call_JSONFormatter["--> JSONFormatter()"]:::callStyle
    call_logger_addHandler["--> logger.addHandler()"]:::callStyle
        core_utils_telemetry_py_track_latency["[FUNC] track_latency()"]:::funcStyle
        core_utils_telemetry_py_decorator["[FUNC] decorator()"]:::funcStyle
        core_utils_telemetry_py_wrapper["[FUNC] wrapper()"]:::funcStyle
    call_func["--> func()"]:::callStyle
    call_wraps["--> wraps()"]:::callStyle

    subgraph core_utils_time_py ["?? core/utils/time.py"]

    subgraph core_utils___init___py ["?? core/utils/__init__.py"]

    subgraph core_validation_base_py ["?? core/validation/base.py"]
        core_validation_base_py_Validator["[CLASS] Validator"]:::classStyle
        core_validation_base_py_Validator_validate["validate()"]:::funcStyle

    subgraph core_validation_budget_py ["?? core/validation/budget.py"]
        core_validation_budget_py_TokenEstimatorProtocol["[CLASS] TokenEstimatorProtocol"]:::classStyle
        core_validation_budget_py_TokenEstimatorProtocol_estimate_tokens["estimate_tokens()"]:::funcStyle
        core_validation_budget_py_BudgetViolationReason["[CLASS] BudgetViolationReason"]:::classStyle
        core_validation_budget_py_BudgetDecisionType["[CLASS] BudgetDecisionType"]:::classStyle
        core_validation_budget_py_ContextReductionLevel["[CLASS] ContextReductionLevel"]:::classStyle
        core_validation_budget_py_ContextCompressionPolicy["[CLASS] ContextCompressionPolicy"]:::classStyle
        core_validation_budget_py_ContextCompressionPolicy_get_levels["get_levels()"]:::funcStyle
        core_validation_budget_py_StandardCompressionPolicy["[CLASS] StandardCompressionPolicy"]:::classStyle
        core_validation_budget_py_StandardCompressionPolicy_get_levels["get_levels()"]:::funcStyle
        core_validation_budget_py_PromptBudget["[CLASS] PromptBudget"]:::classStyle
        core_validation_budget_py_PromptBudget_total_estimated["total_estimated()"]:::funcStyle
        core_validation_budget_py_PromptBudget_utilization_ratio["utilization_ratio()"]:::funcStyle
        core_validation_budget_py_BudgetDecision["[CLASS] BudgetDecision"]:::classStyle
        core_validation_budget_py_PromptBudgetCalculator["[CLASS] PromptBudgetCalculator"]:::classStyle
        core_validation_budget_py_PromptBudgetCalculator___init__["__init__()"]:::funcStyle
        core_validation_budget_py_PromptBudgetCalculator_calculate["calculate()"]:::funcStyle
    call_PromptBudget["--> PromptBudget()"]:::callStyle
    call_BudgetDecision["--> BudgetDecision()"]:::callStyle

    subgraph core_validation_error_taxonomy_py ["?? core/validation/error_taxonomy.py"]

    subgraph core_validation_estimators_py ["?? core/validation/estimators.py"]
        core_validation_estimators_py_ExactBPEEstimator["[CLASS] ExactBPEEstimator"]:::classStyle
        core_validation_estimators_py_ExactBPEEstimator___init__["__init__()"]:::funcStyle
    call_tiktoken_get_encoding["--> tiktoken.get_encoding()"]:::callStyle
        core_validation_estimators_py_ExactBPEEstimator_estimate_tokens["estimate_tokens()"]:::funcStyle

    subgraph core_validation_interfaces_py ["?? core/validation/interfaces.py"]
        core_validation_interfaces_py_BaseValidator["[CLASS] BaseValidator"]:::classStyle
        core_validation_interfaces_py_BaseValidator_validate["validate()"]:::funcStyle

    subgraph core_validation_latex_validator_py ["?? core/validation/latex_validator.py"]

    subgraph core_validation_legacy_adapter_py ["?? core/validation/legacy_adapter.py"]
        core_validation_legacy_adapter_py_UnknownLegacyValidationCodeError["[CLASS] UnknownLegacyValidationCodeError"]:::classStyle
        core_validation_legacy_adapter_py_LegacyValidatorAdapter["[CLASS] LegacyValidatorAdapter"]:::classStyle
        core_validation_legacy_adapter_py_LegacyValidatorAdapter___init__["__init__()"]:::funcStyle
        core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate["validate()"]:::funcStyle
    call___validate["--> *.validate()"]:::callStyle
    call_UnknownLegacyValidationCodeError["--> UnknownLegacyValidationCodeError()"]:::callStyle
    call_results_append["--> results.append()"]:::callStyle

    subgraph core_validation_math_validator_py ["?? core/validation/math_validator.py"]

    subgraph core_validation_models_py ["?? core/validation/models.py"]
        core_validation_models_py_Severity["[CLASS] Severity"]:::classStyle
        core_validation_models_py_Scope["[CLASS] Scope"]:::classStyle
        core_validation_models_py_ValidationContext["[CLASS] ValidationContext"]:::classStyle
        core_validation_models_py_ValidationResult["[CLASS] ValidationResult"]:::classStyle

    subgraph core_validation_perimeter_py ["?? core/validation/perimeter.py"]
        core_validation_perimeter_py_PerimeterValidator["[CLASS] PerimeterValidator"]:::classStyle
        core_validation_perimeter_py_PerimeterValidator_validate["validate()"]:::funcStyle

    subgraph core_validation_pipeline_py ["?? core/validation/pipeline.py"]
        core_validation_pipeline_py_ValidationPipeline["[CLASS] ValidationPipeline"]:::classStyle
        core_validation_pipeline_py_ValidationPipeline___init__["__init__()"]:::funcStyle
        core_validation_pipeline_py_ValidationPipeline_add_chunk_validator["add_chunk_validator()"]:::funcStyle
        core_validation_pipeline_py_ValidationPipeline_add_document_validator["add_document_validator()"]:::funcStyle
        core_validation_pipeline_py_ValidationPipeline_validate_chunk["validate_chunk()"]:::funcStyle
    call_self__run_validators["--> self._run_validators()"]:::callStyle
        core_validation_pipeline_py_ValidationPipeline_validate_document["validate_document()"]:::funcStyle
        core_validation_pipeline_py_ValidationPipeline__run_validators["_run_validators()"]:::funcStyle
    call_results_extend["--> results.extend()"]:::callStyle
    call_validator_validate["--> validator.validate()"]:::callStyle

    subgraph core_validation_preservation_py ["?? core/validation/preservation.py"]
        core_validation_preservation_py_PreservationValidator["[CLASS] PreservationValidator"]:::classStyle
        core_validation_preservation_py_PreservationValidator_validate["validate()"]:::funcStyle
    call_self__check_doi["--> self._check_doi()"]:::callStyle
    call_self__check_url["--> self._check_url()"]:::callStyle
    call_self__check_isbn_orcid["--> self._check_isbn_orcid()"]:::callStyle
    call_self__check_cross_references["--> self._check_cross_references()"]:::callStyle
    call_self__check_labels["--> self._check_labels()"]:::callStyle
    call_self__check_dependencies["--> self._check_dependencies()"]:::callStyle
        core_validation_preservation_py_PreservationValidator__check_doi["_check_doi()"]:::funcStyle
    call_d_lower["--> d.lower()"]:::callStyle
        core_validation_preservation_py_PreservationValidator__check_url["_check_url()"]:::funcStyle
    call_u_rstrip["--> u.rstrip()"]:::callStyle
        core_validation_preservation_py_PreservationValidator__check_isbn_orcid["_check_isbn_orcid()"]:::funcStyle
    call_o_lower["--> o.lower()"]:::callStyle
        core_validation_preservation_py_PreservationValidator__check_cross_references["_check_cross_references()"]:::funcStyle
    call_self__extract_sub_keys["--> self._extract_sub_keys()"]:::callStyle
        core_validation_preservation_py_PreservationValidator__check_labels["_check_labels()"]:::funcStyle
        core_validation_preservation_py_PreservationValidator__check_dependencies["_check_dependencies()"]:::funcStyle
        core_validation_preservation_py_PreservationValidator__extract_sub_keys["_extract_sub_keys()"]:::funcStyle
    call_match_split["--> match.split()"]:::callStyle
    call_part_strip["--> part.strip()"]:::callStyle
    call_keys_add["--> keys.add()"]:::callStyle

    subgraph core_validation_semantic_py ["?? core/validation/semantic.py"]
        core_validation_semantic_py_SemanticValidator["[CLASS] SemanticValidator"]:::classStyle
        core_validation_semantic_py_SemanticValidator_validate["validate()"]:::funcStyle
    call_self__missing_numbers["--> self._missing_numbers()"]:::callStyle
    call_self__missing_units["--> self._missing_units()"]:::callStyle
        core_validation_semantic_py_SemanticValidator__missing_numbers["_missing_numbers()"]:::funcStyle
    call_source_counts_items["--> source_counts.items()"]:::callStyle
    call_missing_extend["--> missing.extend()"]:::callStyle
        core_validation_semantic_py_SemanticValidator__missing_units["_missing_units()"]:::funcStyle

    subgraph core_validation_structural_validator_py ["?? core/validation/structural_validator.py"]
        core_validation_structural_validator_py_StructuralValidator["[CLASS] StructuralValidator"]:::classStyle
        core_validation_structural_validator_py_StructuralValidator_validate["validate()"]:::funcStyle
    call_cls__has_residual_html["--> cls._has_residual_html()"]:::callStyle
    call_errors_append["--> errors.append()"]:::callStyle
    call_ValidationError["--> ValidationError()"]:::callStyle
    call_cls__check_braces["--> cls._check_braces()"]:::callStyle
    call_cls__check_brackets["--> cls._check_brackets()"]:::callStyle
    call_cls__check_math_delimiters["--> cls._check_math_delimiters()"]:::callStyle
    call_cls__check_environments["--> cls._check_environments()"]:::callStyle
        core_validation_structural_validator_py_StructuralValidator__has_residual_html["_has_residual_html()"]:::funcStyle
    call_re_findall["--> re.findall()"]:::callStyle
    call_tag_lower["--> tag.lower()"]:::callStyle
        core_validation_structural_validator_py_StructuralValidator__check_braces["_check_braces()"]:::funcStyle
        core_validation_structural_validator_py_StructuralValidator__check_brackets["_check_brackets()"]:::funcStyle
        core_validation_structural_validator_py_StructuralValidator__check_math_delimiters["_check_math_delimiters()"]:::funcStyle
    call_text_count["--> text.count()"]:::callStyle
    call_temp_count["--> temp.count()"]:::callStyle
        core_validation_structural_validator_py_StructuralValidator__check_environments["_check_environments()"]:::funcStyle

    subgraph core_validation_volumetric_py ["?? core/validation/volumetric.py"]
        core_validation_volumetric_py_VolumetricValidator["[CLASS] VolumetricValidator"]:::classStyle
        core_validation_volumetric_py_VolumetricValidator___init__["__init__()"]:::funcStyle
        core_validation_volumetric_py_VolumetricValidator_validate["validate()"]:::funcStyle

    subgraph core_validation___init___py ["?? core/validation/__init__.py"]

    subgraph infra_adapters_pdf_parser_py ["?? infra/adapters/pdf_parser.py"]
        infra_adapters_pdf_parser_py_PdfParserAdapter["[CLASS] PdfParserAdapter"]:::classStyle
        infra_adapters_pdf_parser_py_PdfParserAdapter___init__["__init__()"]:::funcStyle
        infra_adapters_pdf_parser_py_PdfParserAdapter_parse["parse()"]:::funcStyle
    call_self__parser_callable["--> self._parser_callable()"]:::callStyle

    subgraph infra_adapters___init___py ["?? infra/adapters/__init__.py"]

    subgraph infra_db_bootstrap_py ["?? infra/db/bootstrap.py"]
        infra_db_bootstrap_py_bootstrap_all_databases["[FUNC] bootstrap_all_databases()"]:::funcStyle
    call_BASE_DIR_mkdir["--> BASE_DIR.mkdir()"]:::callStyle
    call_DB_CONFIGS_items["--> DB_CONFIGS.items()"]:::callStyle
    call_sys_exit["--> sys.exit()"]:::callStyle
    call_conn_executescript["--> conn.executescript()"]:::callStyle
    call_conn_commit["--> conn.commit()"]:::callStyle

    subgraph infra_db_connection_py ["?? infra/db/connection.py"]
        infra_db_connection_py__to_absolute_path["[FUNC] _to_absolute_path()"]:::funcStyle
    call_p_is_absolute["--> p.is_absolute()"]:::callStyle
    call_p_resolve["--> p.resolve()"]:::callStyle
        infra_db_connection_py__attach_fsm_database["[FUNC] _attach_fsm_database()"]:::funcStyle
    call__to_absolute_path["--> _to_absolute_path()"]:::callStyle
    call___fetchall["--> *.fetchall()"]:::callStyle
    call_fsm_db_path_replace["--> fsm_db_path.replace()"]:::callStyle
        infra_db_connection_py_get_connection["[FUNC] get_connection()"]:::funcStyle
    call_p_db_is_absolute["--> p_db.is_absolute()"]:::callStyle
    call_p_db_resolve["--> p_db.resolve()"]:::callStyle
    call___resolve["--> *.resolve()"]:::callStyle
    call__attach_fsm_database["--> _attach_fsm_database()"]:::callStyle

    subgraph infra_db_control_repo_py ["?? infra/db/control_repo.py"]
        infra_db_control_repo_py_ControlPlaneRepository["[CLASS] ControlPlaneRepository"]:::classStyle
        infra_db_control_repo_py_ControlPlaneRepository___init__["__init__()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks["enqueue_tasks()"]:::funcStyle
    call_tasks_append["--> tasks.append()"]:::callStyle
    call___executemany["--> *.executemany()"]:::callStyle
    call___commit["--> *.commit()"]:::callStyle
        infra_db_control_repo_py_ControlPlaneRepository_pick_task["pick_task()"]:::funcStyle
    call_TaskLease["--> TaskLease()"]:::callStyle
    call___rollback["--> *.rollback()"]:::callStyle
        infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution["acknowledge_execution()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_abandon_execution["abandon_execution()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_renew_task_lease["renew_task_lease()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched["release_task_untouched()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled["mark_cqrs_reconciled()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered["mark_zombie_recovered()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task["enqueue_assembler_task()"]:::funcStyle
        infra_db_control_repo_py_ControlPlaneRepository_find_documents_with_pending_chunks["find_documents_with_pending_chunks()"]:::funcStyle

    subgraph infra_db_document_repository_py ["?? infra/db/document_repository.py"]
        infra_db_document_repository_py_SQLiteDocumentRepository["[CLASS] SQLiteDocumentRepository"]:::classStyle
        infra_db_document_repository_py_SQLiteDocumentRepository___init__["__init__()"]:::funcStyle
    call_self__ensure_schema["--> self._ensure_schema()"]:::callStyle
        infra_db_document_repository_py_SQLiteDocumentRepository__ensure_schema["_ensure_schema()"]:::funcStyle
    call___executescript["--> *.executescript()"]:::callStyle
        infra_db_document_repository_py_SQLiteDocumentRepository_save_batch["save_batch()"]:::funcStyle
        infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload["get_verified_payload()"]:::funcStyle
    call___cursor["--> *.cursor()"]:::callStyle
    call_PayloadNotFoundError["--> PayloadNotFoundError()"]:::callStyle
    call_HashMismatchError["--> HashMismatchError()"]:::callStyle
    call_payload_encode["--> payload.encode()"]:::callStyle

    subgraph infra_db_event_repo_py ["?? infra/db/event_repo.py"]
        infra_db_event_repo_py_EventPlaneRepository["[CLASS] EventPlaneRepository"]:::classStyle
        infra_db_event_repo_py_EventPlaneRepository___init__["__init__()"]:::funcStyle
        infra_db_event_repo_py_EventPlaneRepository_get_replay["get_replay()"]:::funcStyle
    call_ReplayPayload["--> ReplayPayload()"]:::callStyle
        infra_db_event_repo_py_EventPlaneRepository_append_wal["append_wal()"]:::funcStyle
        infra_db_event_repo_py_EventPlaneRepository_get_latest_event["get_latest_event()"]:::funcStyle
    call_EventRecord["--> EventRecord()"]:::callStyle

    subgraph infra_db_fsm_repository_py ["?? infra/db/fsm_repository.py"]
        infra_db_fsm_repository_py_DocumentStatusDTO["[CLASS] DocumentStatusDTO"]:::classStyle
        infra_db_fsm_repository_py_FSMRepository["[CLASS] FSMRepository"]:::classStyle
        infra_db_fsm_repository_py_FSMRepository___init__["__init__()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_initialize_document["initialize_document()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_transition_to["transition_to()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_get_status["get_status()"]:::funcStyle
    call___fetchone["--> *.fetchone()"]:::callStyle
    call_DocumentStatusDTO["--> DocumentStatusDTO()"]:::callStyle
        infra_db_fsm_repository_py_FSMRepository_find_stalled_documents["find_stalled_documents()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_find_next_ready_for_assembly["find_next_ready_for_assembly()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_is_document_already_processed["is_document_already_processed()"]:::funcStyle
        infra_db_fsm_repository_py_FSMRepository_get_by_document_id["get_by_document_id()"]:::funcStyle

    subgraph infra_db_materialized_repo_py ["?? infra/db/materialized_repo.py"]
        infra_db_materialized_repo_py_MaterializedPlaneRepository["[CLASS] MaterializedPlaneRepository"]:::classStyle
        infra_db_materialized_repo_py_MaterializedPlaneRepository___init__["__init__()"]:::funcStyle
        infra_db_materialized_repo_py_MaterializedPlaneRepository_get_projection_status["get_projection_status()"]:::funcStyle
    call_ProjectionStatus["--> ProjectionStatus()"]:::callStyle
        infra_db_materialized_repo_py_MaterializedPlaneRepository_upsert_projection["upsert_projection()"]:::funcStyle
        infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks["get_assemblable_chunks()"]:::funcStyle
    call_ProjectionRecord["--> ProjectionRecord()"]:::callStyle

    subgraph infra_db_system_repo_py ["?? infra/db/system_repo.py"]
        infra_db_system_repo_py_SystemPlaneRepository["[CLASS] SystemPlaneRepository"]:::classStyle
        infra_db_system_repo_py_SystemPlaneRepository___init__["__init__()"]:::funcStyle
        infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership["acquire_leadership()"]:::funcStyle
        infra_db_system_repo_py_SystemPlaneRepository_renew_leadership["renew_leadership()"]:::funcStyle
        infra_db_system_repo_py_SystemPlaneRepository_release_leadership["release_leadership()"]:::funcStyle
        infra_db_system_repo_py_SystemPlaneRepository_get_current_epoch["get_current_epoch()"]:::funcStyle

    subgraph infra_db___init___py ["?? infra/db/__init__.py"]

    subgraph infra_redis_queues_py ["?? infra/redis/queues.py"]

    subgraph infra_redis___init___py ["?? infra/redis/__init__.py"]

    subgraph runtime_reconciliation_py ["?? runtime/reconciliation.py"]
        runtime_reconciliation_py_CQRSReconciliationDaemon["[CLASS] CQRSReconciliationDaemon"]:::classStyle
        runtime_reconciliation_py_CQRSReconciliationDaemon___init__["__init__()"]:::funcStyle
    call_Metrics["--> Metrics()"]:::callStyle
        runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle["run_reconciliation_cycle()"]:::funcStyle
    call_EventPlaneRepository["--> EventPlaneRepository()"]:::callStyle
    call_MaterializedPlaneRepository["--> MaterializedPlaneRepository()"]:::callStyle
    call_SystemPlaneRepository["--> SystemPlaneRepository()"]:::callStyle
    call_ReconciliationCommandHandler["--> ReconciliationCommandHandler()"]:::callStyle
    call_system_repo_get_current_epoch["--> system_repo.get_current_epoch()"]:::callStyle
    call_task_repo_find_documents_with_pending_chunks["--> task_repo.find_documents_with_pending_chunks()"]:::callStyle
    call_q_conn_execute["--> q_conn.execute()"]:::callStyle
    call_time_time_ns["--> time.time_ns()"]:::callStyle
    call_handler_handle["--> handler.handle()"]:::callStyle
    call_q_conn_commit["--> q_conn.commit()"]:::callStyle

    subgraph runtime_recovery_py ["?? runtime/recovery.py"]
        runtime_recovery_py_AbandonedProcessWatchdog["[CLASS] AbandonedProcessWatchdog"]:::classStyle
        runtime_recovery_py_AbandonedProcessWatchdog___init__["__init__()"]:::funcStyle
        runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep["execute_sweep()"]:::funcStyle
    call_fsm_repo_find_stalled_documents["--> fsm_repo.find_stalled_documents()"]:::callStyle
    call_fsm_repo_get_status["--> fsm_repo.get_status()"]:::callStyle
    call_StallDocumentCommand["--> StallDocumentCommand()"]:::callStyle
    call_cmd_handler_handle["--> cmd_handler.handle()"]:::callStyle

    subgraph runtime_resumer_py ["?? runtime/resumer.py"]
        runtime_resumer_py_OnDemandResumeManager["[CLASS] OnDemandResumeManager"]:::classStyle
        runtime_resumer_py_OnDemandResumeManager___init__["__init__()"]:::funcStyle
        runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document["rescue_stalled_document()"]:::funcStyle
    call_ResumeDocumentCommand["--> ResumeDocumentCommand()"]:::callStyle

    subgraph runtime_sweeper_py ["?? runtime/sweeper.py"]
        runtime_sweeper_py_RecoveryDaemon["[CLASS] RecoveryDaemon"]:::classStyle
        runtime_sweeper_py_RecoveryDaemon___init__["__init__()"]:::funcStyle
        runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint["_force_wal_checkpoint()"]:::funcStyle
        runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle["run_sweep_cycle()"]:::funcStyle
    call_self__force_wal_checkpoint["--> self._force_wal_checkpoint()"]:::callStyle
    call_conn_fsm_execute["--> conn_fsm.execute()"]:::callStyle
    call_conn_queue_execute["--> conn_queue.execute()"]:::callStyle
    call_c_close["--> c.close()"]:::callStyle

    subgraph runtime___init___py ["?? runtime/__init__.py"]
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_LegacyValidatorAdapter
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_ValidationPipeline
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_pipeline_add_chunk_validator
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_pipeline_add_document_validator
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_PreservationValidator
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_PerimeterValidator
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_SemanticValidator
    apps_bootstrap_pipeline_factory_py__build_default_validation_pipeline --> call_VolumetricValidator
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_bootstrap_normalization_layer
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_PdfParserAdapter
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_get_connection
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_SQLiteDocumentRepository
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_AssemblyPolicy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_frozenset
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_DocumentAssembler
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_SummaryBuilder
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call__build_default_validation_pipeline
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_HealingPolicy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_MarkdownLeakageHealingStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_MetaTextLeakageHealingStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_EOFBraceClosureStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_EOFMathClosureStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_HealingPipeline
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_FSMRepository
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_DocumentCommandHandler
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_FSMStateStore
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_TranslationPipeline
        apps_cli_main_py_ChunkerProtocolAdapter --- apps_cli_main_py_ChunkerProtocolAdapter___init__
        apps_cli_main_py_ChunkerProtocolAdapter --- apps_cli_main_py_ChunkerProtocolAdapter_chunk
    apps_cli_main_py_ChunkerProtocolAdapter_chunk --> call_build_semantic_chunks_as_units
        apps_cli_main_py_DummyContextResolver --- apps_cli_main_py_DummyContextResolver_resolve
    apps_cli_main_py_DummyContextResolver_resolve --> call_ResolvedContext
        apps_cli_main_py_DummyContextResolver --- apps_cli_main_py_DummyContextResolver_resolve_many
    apps_cli_main_py_handle_sweep --> call_AbandonedProcessWatchdog
    apps_cli_main_py_handle_sweep --> call_console_print
    apps_cli_main_py_handle_sweep --> call_watchdog_execute_sweep
    apps_cli_main_py_update_ux_boundary --> call_macro_status_update
    apps_cli_main_py_proxy_enter_step --> call_original_enter_step
    apps_cli_main_py_proxy_enter_step --> call_update_ux_boundary
    apps_cli_main_py_handle_translate --> call_asyncio_run
    apps_cli_main_py_handle_translate --> call_handle_translate_async
    apps_cli_main_py_handle_resume --> call_OnDemandResumeManager
    apps_cli_main_py_handle_resume --> call_console_print
    apps_cli_main_py_handle_resume --> call_resumer_rescue_stalled_document
    apps_cli_main_py_handle_status --> call_get_connection
    apps_cli_main_py_handle_status --> call_FSMRepository
    apps_cli_main_py_handle_status --> call_repo_get_status
    apps_cli_main_py_handle_status --> call_console_print
    apps_cli_main_py_handle_status --> call_Table
    apps_cli_main_py_handle_status --> call_table_add_column
    apps_cli_main_py_handle_status --> call_table_add_row
    apps_cli_main_py_handle_status --> call_str
    apps_cli_main_py_parse_arguments --> call_argparse_ArgumentParser
    apps_cli_main_py_parse_arguments --> call_parser_add_subparsers
    apps_cli_main_py_parse_arguments --> call_subparsers_add_parser
    apps_cli_main_py_parse_arguments --> call_t_parser_add_argument
    apps_cli_main_py_parse_arguments --> call_t_parser_set_defaults
    apps_cli_main_py_parse_arguments --> call_sw_parser_set_defaults
    apps_cli_main_py_parse_arguments --> call_r_parser_add_argument
    apps_cli_main_py_parse_arguments --> call_r_parser_set_defaults
    apps_cli_main_py_parse_arguments --> call_st_parser_add_argument
    apps_cli_main_py_parse_arguments --> call_st_parser_set_defaults
    apps_cli_main_py_parse_arguments --> call_parser_parse_args
    apps_cli_main_py_main --> call_parse_arguments
    apps_cli_main_py_main --> call_args_func
        apps_compiler_docker_runner_py_DockerRunner --- apps_compiler_docker_runner_py_DockerRunner_compile
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_re_sub
    apps_compiler_docker_runner_py_DockerRunner_compile --> call___replace
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_tex_content_replace
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_tempfile_TemporaryDirectory
    apps_compiler_docker_runner_py_DockerRunner_compile --> call___join
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_open
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_f_write
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_subprocess_run
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_Exception
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_logger_error
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_os_getcwd
    apps_compiler_docker_runner_py_DockerRunner_compile --> call_shutil_copy
        apps_compiler_log_parser_py_LogParser --- apps_compiler_log_parser_py_LogParser_parse
    apps_compiler_log_parser_py_LogParser_parse --> call_re_search
    apps_compiler_log_parser_py_LogParser_parse --> call_int
    apps_compiler_log_parser_py_LogParser_parse --> call_line_match_group
    apps_compiler_log_parser_py_LogParser_parse --> call_ParsedError
    apps_compiler_log_parser_py_LogParser_parse --> call_LogParser__extract_context
        apps_compiler_log_parser_py_LogParser --- apps_compiler_log_parser_py_LogParser__extract_context
    apps_compiler_log_parser_py_LogParser__extract_context --> call_log_split
    apps_compiler_log_parser_py_LogParser__extract_context --> call_enumerate
    apps_compiler_log_parser_py_LogParser__extract_context --> call_max
    apps_compiler_log_parser_py_LogParser__extract_context --> call_min
    apps_compiler_log_parser_py_LogParser__extract_context --> call_len
    apps_compiler_log_parser_py_LogParser__extract_context --> call___join
        apps_compiler_tex_builder_py_TexBuilder --- apps_compiler_tex_builder_py_TexBuilder___init__
        apps_compiler_tex_builder_py_TexBuilder --- apps_compiler_tex_builder_py_TexBuilder_build
    apps_compiler_tex_builder_py_TexBuilder_build --> call_list
    apps_compiler_tex_builder_py_TexBuilder_build --> call_len
    apps_compiler_tex_builder_py_TexBuilder_build --> call___strip
    apps_compiler_tex_builder_py_TexBuilder_build --> call_str
    apps_compiler_tex_builder_py_TexBuilder_build --> call_ValueError
    apps_compiler_tex_builder_py_TexBuilder_build --> call___lower
    apps_compiler_tex_builder_py_TexBuilder_build --> call_getattr
    apps_compiler_tex_builder_py_TexBuilder_build --> call___replace
    apps_compiler_tex_builder_py_TexBuilder_build --> call_safe_text_replace
    apps_compiler_tex_builder_py_TexBuilder_build --> call_document_append
    apps_compiler_tex_builder_py_TexBuilder_build --> call_document_extend
    apps_compiler_tex_builder_py_TexBuilder_build --> call___join
        apps_compiler___main___py_AssemblerWorkerDaemon --- apps_compiler___main___py_AssemblerWorkerDaemon___init__
    apps_compiler___main___py_AssemblerWorkerDaemon___init__ --> call_uuid_uuid4
        apps_compiler___main___py_AssemblerWorkerDaemon --- apps_compiler___main___py_AssemblerWorkerDaemon_run
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_logger_info
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call___find_next_ready_for_assembly
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_min
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_time_sleep
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_random_uniform
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_self__process_assembly_task
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_logger_warning
    apps_compiler___main___py_AssemblerWorkerDaemon_run --> call_logger_exception
        apps_compiler___main___py_AssemblerWorkerDaemon --- apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call___get_status
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call_logger_error
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call_FailDocumentCommand
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call___handle
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call_logger_info
    apps_compiler___main___py_AssemblerWorkerDaemon__fail_document_safely --> call_logger_critical
        apps_compiler___main___py_AssemblerWorkerDaemon --- apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_time_perf_counter
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_logger_info
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___get_status
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_ValueError
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_StartAssemblyCommand
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___handle
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call____load_document
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___get
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_sorted
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_doc_nodes_keys
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___get_assemblable_chunks
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_doc_nodes_get
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_valid_chunks_append
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___build
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_MarkCompilationReadyCommand
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_StartCompilationCommand
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call___compile
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_CompleteDocumentCommand
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_logger_error
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_self__fail_document_safely
    apps_compiler___main___py_AssemblerWorkerDaemon__process_assembly_task --> call_str
        apps_daemons_chaos_runner_py_SystemObserver --- apps_daemons_chaos_runner_py_SystemObserver___init__
    apps_daemons_chaos_runner_py_SystemObserver___init__ --> call___abspath
        apps_daemons_chaos_runner_py_SystemObserver --- apps_daemons_chaos_runner_py_SystemObserver__get_ro_connection
    apps_daemons_chaos_runner_py_SystemObserver__get_ro_connection --> call_sqlite3_connect
    apps_daemons_chaos_runner_py_SystemObserver__get_ro_connection --> call_conn_execute
        apps_daemons_chaos_runner_py_SystemObserver --- apps_daemons_chaos_runner_py_SystemObserver_inject_load
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_sqlite3_connect
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_conn_execute
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_FSMRepository
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_ControlPlaneRepository
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_range
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_uuid_uuid4
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_fsm_repo_initialize_document
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_task_repo_enqueue_tasks
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_fsm_repo_transition_to
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_doc_ids_append
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_conn_close
    apps_daemons_chaos_runner_py_SystemObserver_inject_load --> call_logger_info
        apps_daemons_chaos_runner_py_SystemObserver --- apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_time_time
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_self__get_ro_connection
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_conn_cursor
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_cursor_execute
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_cursor_fetchone
    apps_daemons_chaos_runner_py_SystemObserver_get_convergence_metrics --> call_conn_close
        apps_daemons_chaos_runner_py_SystemObserver --- apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence
    apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence --> call_logger_info
    apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence --> call_time_perf_counter
    apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence --> call_self_get_convergence_metrics
    apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence --> call_time_sleep
    apps_daemons_chaos_runner_py_SystemObserver_wait_for_convergence --> call_logger_error
        apps_daemons_chaos_runner_py_ChaosInjector --- apps_daemons_chaos_runner_py_ChaosInjector___init__
    apps_daemons_chaos_runner_py_ChaosInjector___init__ --> call_docker_from_env
    apps_daemons_chaos_runner_py_ChaosInjector___init__ --> call_os_getenv
        apps_daemons_chaos_runner_py_ChaosInjector --- apps_daemons_chaos_runner_py_ChaosInjector_kill_service
    apps_daemons_chaos_runner_py_ChaosInjector_kill_service --> call___list
    apps_daemons_chaos_runner_py_ChaosInjector_kill_service --> call_logger_error
    apps_daemons_chaos_runner_py_ChaosInjector_kill_service --> call_container_kill
    apps_daemons_chaos_runner_py_ChaosInjector_kill_service --> call_logger_warning
        apps_daemons_chaos_runner_py_ChaosInjector --- apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream
    apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream --> call_requests_post
    apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream --> call_resp_raise_for_status
    apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream --> call_logger_warning
    apps_daemons_chaos_runner_py_ChaosInjector_mutate_upstream --> call_logger_error
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_logger_info
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_SystemObserver
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_ChaosInjector
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_injector_mutate_upstream
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_observer_inject_load
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_time_sleep
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_injector_kill_service
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_observer_wait_for_convergence
    apps_daemons_chaos_runner_py_game_day_1_crash_consistency --> call_logger_critical
        apps_daemons_fake_gemini_py_ChaosConfig --- apps_daemons_fake_gemini_py_ChaosConfig___init__
    apps_daemons_fake_gemini_py_ChaosConfig___init__ --> call_asyncio_Lock
        apps_daemons_fake_gemini_py_Metrics --- apps_daemons_fake_gemini_py_Metrics___init__
    apps_daemons_fake_gemini_py_health_check --> call_app_get
        apps_daemons_reconciler_py_ReconcilerDaemon --- apps_daemons_reconciler_py_ReconcilerDaemon___init__
    apps_daemons_reconciler_py_ReconcilerDaemon___init__ --> call_uuid_uuid4
    apps_daemons_reconciler_py_ReconcilerDaemon___init__ --> call_threading_Event
        apps_daemons_reconciler_py_ReconcilerDaemon --- apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call___execute
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call_cursor_fetchall
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call_logger_info
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call_MarkAssemblyReadyCommand
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call___handle
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_fsm_stalls --> call_logger_warning
        apps_daemons_reconciler_py_ReconcilerDaemon --- apps_daemons_reconciler_py_ReconcilerDaemon__leadership_heartbeat
    apps_daemons_reconciler_py_ReconcilerDaemon__leadership_heartbeat --> call___wait
    apps_daemons_reconciler_py_ReconcilerDaemon__leadership_heartbeat --> call___renew_leadership
    apps_daemons_reconciler_py_ReconcilerDaemon__leadership_heartbeat --> call_logger_critical
        apps_daemons_reconciler_py_ReconcilerDaemon --- apps_daemons_reconciler_py_ReconcilerDaemon_run
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_logger_info
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_copy_context
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_ctx_worker_id_set
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_threading_Thread
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_ctx_run
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_heartbeat_thread_start
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call___is_set
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call___acquire_leadership
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call___wait
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_random_uniform
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_time_time
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_self__sweep_tasks
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_self__sweep_fsm_stalls
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_logger_exception
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call___set
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call_heartbeat_thread_join
    apps_daemons_reconciler_py_ReconcilerDaemon_run --> call___release_leadership
        apps_daemons_reconciler_py_ReconcilerDaemon --- apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call___execute
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call_cursor_fetchall
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call___get_latest_event
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call_logger_info
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call_RematerializeTaskCommand
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call___handle
    apps_daemons_reconciler_py_ReconcilerDaemon__sweep_tasks --> call_RecoverZombieTaskCommand
        apps_llm_workers_adapters_py_GroqProvider --- apps_llm_workers_adapters_py_GroqProvider___init__
    apps_llm_workers_adapters_py_GroqProvider___init__ --> call_AsyncGroq
        apps_llm_workers_adapters_py_GeminiProvider --- apps_llm_workers_adapters_py_GeminiProvider___init__
    apps_llm_workers_adapters_py_GeminiProvider___init__ --> call_genai_configure
        apps_llm_workers_cache_provider_py_CachedLLMProvider --- apps_llm_workers_cache_provider_py_CachedLLMProvider___init__
    apps_llm_workers_cache_provider_py_CachedLLMProvider___init__ --> call_asyncio_Lock
        apps_llm_workers_dispatcher_py_AsyncDispatcher --- apps_llm_workers_dispatcher_py_AsyncDispatcher___init__
    apps_llm_workers_dispatcher_py_AsyncDispatcher___init__ --> call_self__default_pipeline
        apps_llm_workers_dispatcher_py_AsyncDispatcher --- apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_LegacyValidatorAdapter
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_ValidationPipeline
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_pipeline_add_chunk_validator
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_pipeline_add_document_validator
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_PreservationValidator
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_PerimeterValidator
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_SemanticValidator
    apps_llm_workers_dispatcher_py_AsyncDispatcher__default_pipeline --> call_VolumetricValidator
        apps_llm_workers_prompt_builder_py_PromptBuilder --- apps_llm_workers_prompt_builder_py_PromptBuilder___init__
    apps_llm_workers_prompt_builder_py_PromptBuilder___init__ --> call_StandardCompressionPolicy
        apps_llm_workers_prompt_builder_py_PromptBuilder --- apps_llm_workers_prompt_builder_py_PromptBuilder__build_system
        apps_llm_workers_prompt_builder_py_PromptBuilder --- apps_llm_workers_prompt_builder_py_PromptBuilder_build
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_BuildFailure
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___join
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_full_context_str_split
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_context_levels_get
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_self__build_system
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___calculate
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___get_levels
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___estimate_tokens
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___hexdigest
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_hashlib_sha256
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_hash_input_encode
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_PromptEnvelope
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_BuildSuccess
        apps_llm_workers_rate_limiter_py_QuotaReservation --- apps_llm_workers_rate_limiter_py_QuotaReservation_create_granted
    apps_llm_workers_rate_limiter_py_QuotaReservation_create_granted --> call_cls
        apps_llm_workers_rate_limiter_py_QuotaReservation --- apps_llm_workers_rate_limiter_py_QuotaReservation_create_rejected
    apps_llm_workers_rate_limiter_py_QuotaReservation_create_rejected --> call_cls
        apps_llm_workers_rate_limiter_py_ClockProtocol --- apps_llm_workers_rate_limiter_py_ClockProtocol_now
        apps_llm_workers_rate_limiter_py_SystemClock --- apps_llm_workers_rate_limiter_py_SystemClock_now
    apps_llm_workers_rate_limiter_py_SystemClock_now --> call_time_monotonic
        apps_llm_workers_rate_limiter_py_TokenBucket --- apps_llm_workers_rate_limiter_py_TokenBucket___init__
    apps_llm_workers_rate_limiter_py_TokenBucket___init__ --> call_float
    apps_llm_workers_rate_limiter_py_TokenBucket___init__ --> call___now
        apps_llm_workers_rate_limiter_py_TokenBucket --- apps_llm_workers_rate_limiter_py_TokenBucket__refill
    apps_llm_workers_rate_limiter_py_TokenBucket__refill --> call___now
    apps_llm_workers_rate_limiter_py_TokenBucket__refill --> call_min
        apps_llm_workers_rate_limiter_py_TokenBucket --- apps_llm_workers_rate_limiter_py_TokenBucket_get_wait_time
    apps_llm_workers_rate_limiter_py_TokenBucket_get_wait_time --> call_self__refill
        apps_llm_workers_rate_limiter_py_TokenBucket --- apps_llm_workers_rate_limiter_py_TokenBucket_consume
    apps_llm_workers_rate_limiter_py_TokenBucket_consume --> call_self__refill
        apps_llm_workers_rate_limiter_py_QuotaManager --- apps_llm_workers_rate_limiter_py_QuotaManager___init__
    apps_llm_workers_rate_limiter_py_QuotaManager___init__ --> call_SystemClock
    apps_llm_workers_rate_limiter_py_QuotaManager___init__ --> call_TokenBucket
    apps_llm_workers_rate_limiter_py_QuotaManager___init__ --> call_asyncio_Lock
        apps_llm_workers_rate_limiter_py_RateLimitedProvider --- apps_llm_workers_rate_limiter_py_RateLimitedProvider___init__
        apps_llm_workers_resilient_provider_py_ResilientProvider --- apps_llm_workers_resilient_provider_py_ResilientProvider___init__
        apps_llm_workers_router_translation_py_TranslationRouter --- apps_llm_workers_router_translation_py_TranslationRouter_get_strategy
    apps_llm_workers_router_translation_py_TranslationRouter_get_strategy --> call___get
        apps_llm_workers_routing_py_TranslationStrategyRouter --- apps_llm_workers_routing_py_TranslationStrategyRouter___init__
        apps_llm_workers_routing_py_TranslationStrategyRouter --- apps_llm_workers_routing_py_TranslationStrategyRouter_route
    apps_llm_workers_routing_py_TranslationStrategyRouter_route --> call_ValueError
        apps_llm_workers_sync_bridge_py_SyncProviderBridge --- apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call_asyncio_new_event_loop
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call_threading_Thread
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call_threading_Event
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call___start
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call___wait
    apps_llm_workers_sync_bridge_py_SyncProviderBridge___init__ --> call_RuntimeError
        apps_llm_workers_sync_bridge_py_SyncProviderBridge --- apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call_asyncio_set_event_loop
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call___set
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call___run_forever
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call_asyncio_all_tasks
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call_task_cancel
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call___run_until_complete
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call_asyncio_gather
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call___shutdown_asyncgens
    apps_llm_workers_sync_bridge_py_SyncProviderBridge__start_loop --> call___close
        apps_llm_workers_sync_bridge_py_SyncProviderBridge --- apps_llm_workers_sync_bridge_py_SyncProviderBridge_shutdown
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_shutdown --> call___is_running
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_shutdown --> call___call_soon_threadsafe
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_shutdown --> call___join
        apps_llm_workers_sync_bridge_py_SyncProviderBridge --- apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call___hexdigest
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_hashlib_sha256
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_target_payload_encode
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_TranslationUnit
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call___get
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_ResolvedContext
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call___build
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_asyncio_run_coroutine_threadsafe
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call___translate
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_future_result
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_logger_error
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_future_cancel
    apps_llm_workers_sync_bridge_py_SyncProviderBridge_execute --> call_TimeoutError
        apps_llm_workers___main___py_TaskLeaseHeartbeat --- apps_llm_workers___main___py_TaskLeaseHeartbeat___init__
    apps_llm_workers___main___py_TaskLeaseHeartbeat___init__ --> call_threading_Event
    apps_llm_workers___main___py_TaskLeaseHeartbeat___init__ --> call_copy_context
    apps_llm_workers___main___py_TaskLeaseHeartbeat___init__ --> call_threading_Thread
    apps_llm_workers___main___py_TaskLeaseHeartbeat___init__ --> call_ctx_run
        apps_llm_workers___main___py_TaskLeaseHeartbeat --- apps_llm_workers___main___py_TaskLeaseHeartbeat__beat
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call_get_connection
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call_ControlPlaneRepository
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call___wait
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call_control_repo_renew_task_lease
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call_logger_critical
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call___set
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call_logger_error
    apps_llm_workers___main___py_TaskLeaseHeartbeat__beat --> call___close
        apps_llm_workers___main___py_TaskLeaseHeartbeat --- apps_llm_workers___main___py_TaskLeaseHeartbeat___enter__
    apps_llm_workers___main___py_TaskLeaseHeartbeat___enter__ --> call___start
        apps_llm_workers___main___py_TaskLeaseHeartbeat --- apps_llm_workers___main___py_TaskLeaseHeartbeat___exit__
    apps_llm_workers___main___py_TaskLeaseHeartbeat___exit__ --> call___set
    apps_llm_workers___main___py_TaskLeaseHeartbeat___exit__ --> call___join
        apps_llm_workers___main___py_LLMWorkerDaemon --- apps_llm_workers___main___py_LLMWorkerDaemon___init__
    apps_llm_workers___main___py_LLMWorkerDaemon___init__ --> call_uuid_uuid4
    apps_llm_workers___main___py_LLMWorkerDaemon___init__ --> call_threading_Event
        apps_llm_workers___main___py_LLMWorkerDaemon --- apps_llm_workers___main___py_LLMWorkerDaemon_stop
    apps_llm_workers___main___py_LLMWorkerDaemon_stop --> call___set
        apps_llm_workers___main___py_LLMWorkerDaemon --- apps_llm_workers___main___py_LLMWorkerDaemon_run
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_logger_info
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call___is_set
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call___claim_next_pending_task
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_min
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call___wait
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_random_uniform
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_self__process_task
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_logger_warning
    apps_llm_workers___main___py_LLMWorkerDaemon_run --> call_logger_exception
        apps_llm_workers___main___py_LLMWorkerDaemon --- apps_llm_workers___main___py_LLMWorkerDaemon__process_task
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_time_perf_counter
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_uuid_uuid4
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_logger_info
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___get_node
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_logger_error
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___mark_task_failed
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___hexdigest
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_hashlib_sha256
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_content_encode
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___get_projection_status
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___mark_task_completed
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___get_replay
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_os_getenv
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_TaskLeaseHeartbeat
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___execute
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___is_set
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_OptimisticLockError
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___append_wal
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_getattr
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_TextNormalizer_normalize
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call_normalized_encode
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___upsert_projection
    apps_llm_workers___main___py_LLMWorkerDaemon__process_task --> call___observe
    apps_llm_workers___main___py_shutdown_handler --> call_logger_info
    apps_llm_workers___main___py_shutdown_handler --> call_daemon_stop
        apps_ocr_router___main___py_OCRRouterDaemon --- apps_ocr_router___main___py_OCRRouterDaemon___init__
    apps_ocr_router___main___py_OCRRouterDaemon___init__ --> call_uuid_uuid4
    apps_ocr_router___main___py_OCRRouterDaemon___init__ --> call_Path
    apps_ocr_router___main___py_OCRRouterDaemon___init__ --> call_d_mkdir
        apps_ocr_router___main___py_OCRRouterDaemon --- apps_ocr_router___main___py_OCRRouterDaemon_run
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call_logger_info
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call_next
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call___glob
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call_time_sleep
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call_self__process_document
    apps_ocr_router___main___py_OCRRouterDaemon_run --> call_logger_exception
        apps_ocr_router___main___py_OCRRouterDaemon --- apps_ocr_router___main___py_OCRRouterDaemon__process_document
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_time_perf_counter
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_open
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___hexdigest
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_hashlib_sha256
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_f_read
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_logger_info
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___is_document_already_processed
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_logger_warning
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_shutil_move
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_str
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_logger_error
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_parse_pdf
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_compute_ast_hash
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_FastWordEstimator
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_build_semantic_chunks_as_units
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___register_ast
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___initialize_document
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___get_status
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_ValueError
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_StartParsingCommand
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___handle
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call___enqueue_tasks
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_StartProcessingCommand
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_len
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_round
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_uuid_uuid4
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_isinstance
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_pdf_path_exists
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_time_time
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_traceback_format_exc
    apps_ocr_router___main___py_OCRRouterDaemon__process_document --> call_json_dump
        core_ast_grouper_py_ContextAwareSemanticGrouper --- core_ast_grouper_py_ContextAwareSemanticGrouper_group
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call_tuple
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call_first_node_cp_get
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call___get
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call_groups_append
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call_SemanticGroup
    core_ast_grouper_py_ContextAwareSemanticGrouper_group --> call_current_nodes_append
    core_ast_hashing_py_serialize_node --> call_hasattr
    core_ast_hashing_py_serialize_node --> call_str
    core_ast_hashing_py_serialize_node --> call_getattr
    core_ast_hashing_py_serialize_node --> call_serialize_node
    core_ast_hashing_py_compute_ast_hash --> call_json_dumps
    core_ast_hashing_py_compute_ast_hash --> call_serialize_node
    core_ast_hashing_py_compute_ast_hash --> call___hexdigest
    core_ast_hashing_py_compute_ast_hash --> call_hashlib_sha256
    core_ast_hashing_py_compute_ast_hash --> call_raw_encode
        core_ast_hashing_py_TokenBudgetChunker --- core_ast_hashing_py_TokenBudgetChunker___init__
    core_ast_hashing_py_TokenBudgetChunker___init__ --> call_ChunkPolicy
    core_ast_hashing_py_TokenBudgetChunker___init__ --> call_ChunkingReport
        core_ast_hashing_py_TokenBudgetChunker --- core_ast_hashing_py_TokenBudgetChunker__split_by_sentence
    core_ast_hashing_py_TokenBudgetChunker__split_by_sentence --> call_re_split
    core_ast_hashing_py_TokenBudgetChunker__split_by_sentence --> call_s_strip
        core_ast_hashing_py_TokenBudgetChunker --- core_ast_hashing_py_TokenBudgetChunker_chunk_group
        core_ast_hashing_py_TokenBudgetChunker --- core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call___join
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call___hexdigest
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_hashlib_sha256
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_payload_text_encode
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_hashlib_md5
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call___encode
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_units_append
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_TranslationUnit
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_len
    core_ast_hashing_py_TokenBudgetChunker_flush_translate_chunk --> call_max
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_flush_translate_chunk
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call___estimate
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call___hexdigest
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_hashlib_sha256
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_content_encode
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_hashlib_md5
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call___encode
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_units_append
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_TranslationUnit
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_len
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_max
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_self__split_by_sentence
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_ASTNode
    core_ast_hashing_py_TokenBudgetChunker_chunk_group --> call_current_nodes_append
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_ContextAwareSemanticGrouper_group
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_TokenBudgetChunker
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_ChunkPolicy
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_len
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_chunker_chunk_group
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_all_units_extend
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_int
    core_ast_hashing_py_build_semantic_chunks_as_units --> call_sum
        core_ast_models_py_ASTNode --- core_ast_models_py_ASTNode_has_valid_sequence
        core_ast_models_py_TokenEstimator --- core_ast_models_py_TokenEstimator_estimate
        core_ast_models_py_FastWordEstimator --- core_ast_models_py_FastWordEstimator_estimate
    core_ast_models_py_FastWordEstimator_estimate --> call_int
    core_ast_models_py_FastWordEstimator_estimate --> call_len
    core_ast_models_py_FastWordEstimator_estimate --> call_text_split
        core_ast_models_py_FastWordEstimator --- core_ast_models_py_FastWordEstimator_estimate_tokens
    core_ast_models_py_FastWordEstimator_estimate_tokens --> call_int
    core_ast_models_py_FastWordEstimator_estimate_tokens --> call_self_estimate
        core_ast_models_py_ChunkOutcome --- core_ast_models_py_ChunkOutcome___post_init__
    core_ast_models_py_ChunkOutcome___post_init__ --> call_ValueError
        core_ast_models_py_ChunkOutcome --- core_ast_models_py_ChunkOutcome_is_success
        core_ast_models_py_DispatchResult --- core_ast_models_py_DispatchResult_total_processed
    core_ast_models_py_DispatchResult_total_processed --> call_len
        core_ast_models_py_DispatchResult --- core_ast_models_py_DispatchResult_total_failed
    core_ast_models_py_DispatchResult_total_failed --> call_sum
        core_ast_models_py_DispatchResult --- core_ast_models_py_DispatchResult_success_rate
        core_ast_models_py_DispatchResult --- core_ast_models_py_DispatchResult_failed_by_reason
    core_ast_models_py_DispatchResult_failed_by_reason --> call_Counter
    core_ast_models_py_DispatchResult_failed_by_reason --> call_dict
        core_ast_models_py_DispatchAnalytics --- core_ast_models_py_DispatchAnalytics_calculate_success_rate
        core_ast_models_py_DispatchAnalytics --- core_ast_models_py_DispatchAnalytics_aggregate_failures
    core_ast_models_py_DispatchAnalytics_aggregate_failures --> call_Counter
    core_ast_models_py_DispatchAnalytics_aggregate_failures --> call_dict
    core_ast_parser_py_sanitize_marker_html --> call_re_sub
    core_ast_parser_py_sanitize_marker_html --> call_html_unescape
    core_ast_parser_py__is_stem_table --> call_re_search
    core_ast_parser_py__is_stem_table --> call_line_strip
    core_ast_parser_py__is_stem_table --> call_block_splitlines
    core_ast_parser_py__is_stem_table --> call_len
    core_ast_parser_py__is_stem_table --> call_sum
    core_ast_parser_py__is_stem_table --> call_STEM_TABLE_ROW_PATTERN_search
    core_ast_parser_py__run_tesseract_on_bytes --> call_Image_open
    core_ast_parser_py__run_tesseract_on_bytes --> call_io_BytesIO
    core_ast_parser_py__run_tesseract_on_bytes --> call_pytesseract_image_to_string
    core_ast_parser_py__run_tesseract_on_bytes --> call_logger_error
    core_ast_parser_py__run_tesseract_on_bytes --> call_str
    core_ast_parser_py__extract_document_text --> call_os_makedirs
    core_ast_parser_py__extract_document_text --> call_logger_info
    core_ast_parser_py__extract_document_text --> call_pymupdf4llm_to_markdown
    core_ast_parser_py__extract_document_text --> call_isinstance
    core_ast_parser_py__extract_document_text --> call_fitz_open
    core_ast_parser_py__extract_document_text --> call_len
    core_ast_parser_py__extract_document_text --> call_range
    core_ast_parser_py__extract_document_text --> call_pages_tasks_append
    core_ast_parser_py__extract_document_text --> call___get_pixmap
    core_ast_parser_py__extract_document_text --> call_pix_tobytes
    core_ast_parser_py__extract_document_text --> call_doc_close
    core_ast_parser_py__worker_task --> call__run_tesseract_on_bytes
    core_ast_parser_py__extract_document_text --> call_ThreadPoolExecutor
    core_ast_parser_py__extract_document_text --> call_executor_map
    core_ast_parser_py__extract_document_text --> call___join
    core_ast_parser_py_parse_pdf --> call_hasattr
    core_ast_parser_py_parse_pdf --> call_RuntimeError
    core_ast_parser_py_parse_pdf --> call___exists
    core_ast_parser_py_parse_pdf --> call_FileNotFoundError
    core_ast_parser_py_parse_pdf --> call_logger_info
    core_ast_parser_py_parse_pdf --> call_open
    core_ast_parser_py_parse_pdf --> call_json_load
    core_ast_parser_py_parse_pdf --> call_ASTNode
    core_ast_parser_py_parse_pdf --> call_PDFRouter_detect_pdf_type
    core_ast_parser_py_parse_pdf --> call_len
    core_ast_parser_py_parse_pdf --> call__extract_document_text
    core_ast_parser_py_parse_pdf --> call_sanitize_marker_html
    core_ast_parser_py_parse_pdf --> call_dbg_f_write
    core_ast_parser_py_parse_pdf --> call_gc_collect
    core_ast_parser_py_parse_pdf --> call_MarkdownSegmenter
    core_ast_parser_py_parse_pdf --> call_segmenter_segment
    core_ast_parser_py_parse_pdf --> call_enumerate
    core_ast_parser_py_parse_pdf --> call_bool
    core_ast_parser_py_parse_pdf --> call_re_search
    core_ast_parser_py_parse_pdf --> call_re_match
    core_ast_parser_py_parse_pdf --> call_re_sub
    core_ast_parser_py_parse_pdf --> call_block_strip
    core_ast_parser_py_parse_pdf --> call_any
    core_ast_parser_py_parse_pdf --> call___startswith
    core_ast_parser_py_parse_pdf --> call_block_lower
    core_ast_parser_py_parse_pdf --> call_list
    core_ast_parser_py_parse_pdf --> call_re_finditer
    core_ast_parser_py_parse_pdf --> call___strip
    core_ast_parser_py_parse_pdf --> call_match_start
    core_ast_parser_py_parse_pdf --> call_ast_nodes_append
    core_ast_parser_py_parse_pdf --> call_match_group
    core_ast_parser_py_parse_pdf --> call_match_end
    core_ast_parser_py_parse_pdf --> call_EQUATION_BLOCK_PATTERNS_search
    core_ast_parser_py_parse_pdf --> call__is_stem_table
    core_ast_parser_py_parse_pdf --> call_block_startswith
    core_ast_parser_py_parse_pdf --> call___replace
    core_ast_parser_py_parse_pdf --> call_str
    core_ast_parser_py_parse_pdf --> call_json_dump
    core_ast_parser_py_parse_pdf --> call_n_model_dump
    core_ast_parser_py_parse_pdf --> call_shutil_rmtree
        core_ast_registry_py_ASTRegistry --- core_ast_registry_py_ASTRegistry___init__
    core_ast_registry_py_ASTRegistry___init__ --> call___join
    core_ast_registry_py_ASTRegistry___init__ --> call_os_makedirs
        core_ast_registry_py_ASTRegistry --- core_ast_registry_py_ASTRegistry_get_node
    core_ast_registry_py_ASTRegistry_get_node --> call_self__load_document
    core_ast_registry_py_ASTRegistry_get_node --> call___get
    core_ast_registry_py_ASTRegistry_get_node --> call_doc_cache_get
        core_ast_registry_py_ASTRegistry --- core_ast_registry_py_ASTRegistry__load_document
    core_ast_registry_py_ASTRegistry__load_document --> call___join
    core_ast_registry_py_ASTRegistry__load_document --> call___exists
    core_ast_registry_py_ASTRegistry__load_document --> call_logger_warning
    core_ast_registry_py_ASTRegistry__load_document --> call_open
    core_ast_registry_py_ASTRegistry__load_document --> call_json_load
    core_ast_registry_py_ASTRegistry__load_document --> call_isinstance
    core_ast_registry_py_ASTRegistry__load_document --> call_raw_data_get
    core_ast_registry_py_ASTRegistry__load_document --> call_ValueError
    core_ast_registry_py_ASTRegistry__load_document --> call_ASTNode_model_validate
    core_ast_registry_py_ASTRegistry__load_document --> call_logger_info
    core_ast_registry_py_ASTRegistry__load_document --> call_logger_error
        core_ast_registry_py_ASTRegistry --- core_ast_registry_py_ASTRegistry_register_ast
    core_ast_registry_py_ASTRegistry_register_ast --> call___join
    core_ast_registry_py_ASTRegistry_register_ast --> call_n_model_dump
    core_ast_registry_py_ASTRegistry_register_ast --> call_tempfile_mkstemp
    core_ast_registry_py_ASTRegistry_register_ast --> call_os_fdopen
    core_ast_registry_py_ASTRegistry_register_ast --> call_json_dump
    core_ast_registry_py_ASTRegistry_register_ast --> call_os_replace
    core_ast_registry_py_ASTRegistry_register_ast --> call___exists
    core_ast_registry_py_ASTRegistry_register_ast --> call_os_remove
    core_ast_registry_py_ASTRegistry_register_ast --> call_logger_error
    core_ast_registry_py_ASTRegistry_register_ast --> call_logger_info
        core_ast_router_py_PDFRouter --- core_ast_router_py_PDFRouter_detect_pdf_type
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_fitz_open
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_len
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_ValueError
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_range
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_page_get_text
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_isinstance
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_text_str_strip
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_empty_pages_append
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_doc_close
    core_ast_router_py_PDFRouter_detect_pdf_type --> call_logger_info
        core_ast_segmenter_py_MarkdownSegmenter --- core_ast_segmenter_py_MarkdownSegmenter___init__
    core_ast_segmenter_py_MarkdownSegmenter___init__ --> call_re_compile
        core_ast_segmenter_py_MarkdownSegmenter --- core_ast_segmenter_py_MarkdownSegmenter_segment
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_full_text_splitlines
        core_ast_segmenter_py_MarkdownSegmenter --- core_ast_segmenter_py_MarkdownSegmenter_flush_block
    core_ast_segmenter_py_MarkdownSegmenter_flush_block --> call_blocks_append
    core_ast_segmenter_py_MarkdownSegmenter_flush_block --> call___join
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_enumerate
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_line_strip
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_flush_block
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call___match
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_current_block_append
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_logger_error
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call___search
    core_ast_segmenter_py_MarkdownSegmenter_segment --> call_b_strip
        core_ast_validator_py_ASTHealthReport --- core_ast_validator_py_ASTHealthReport___init__
        core_ast_validator_py_ASTHealthReport --- core_ast_validator_py_ASTHealthReport_from_ast
    core_ast_validator_py_ASTHealthReport_from_ast --> call_len
    core_ast_validator_py_ASTHealthReport_from_ast --> call_cls
        core_ast_validator_py_ASTHealthReport --- core_ast_validator_py_ASTHealthReport___str__
        core_ast_validator_py_ASTValidator --- core_ast_validator_py_ASTValidator_validate
    core_ast_validator_py_ASTValidator_validate --> call_ASTValidationError
    core_ast_validator_py_ASTValidator_validate --> call_set
    core_ast_validator_py_ASTValidator_validate --> call_seen_ids_add
    core_ast_validator_py_ASTValidator_validate --> call_hasattr
    core_ast_validator_py_ASTValidator_validate --> call_str
    core_ast_validator_py_ASTValidator_validate --> call_len
    core_ast_validator_py_ASTValidator_validate --> call_logger_warning
    core_ast_validator_py_ASTValidator_validate --> call_bool
    core_ast_validator_py_ASTValidator_validate --> call_LATEX_MATH_OPEN_search
    core_ast_validator_py_ASTValidator_validate --> call_LATEX_MATH_CLOSE_search
    core_benchmark_aggregation_py_calculate_decoupled_overall_score --> call___upper
    core_benchmark_aggregation_py_calculate_decoupled_overall_score --> call_os_getenv
    core_benchmark_aggregation_py_calculate_decoupled_overall_score --> call_round
    core_benchmark_aggregation_py_calculate_decoupled_overall_score --> call_min
        core_benchmark_judge_models_py_ChunkEvaluationScore --- core_benchmark_judge_models_py_ChunkEvaluationScore_overall_score
    core_benchmark_judge_models_py_ChunkEvaluationScore_overall_score --> call_calculate_decoupled_overall_score
        core_benchmark_models_py_ChunkBenchmarkRecord --- core_benchmark_models_py_ChunkBenchmarkRecord_tps_formula
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_total_tokens
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_reliability_score
    core_benchmark_models_py_ProviderBenchmarkMetrics_reliability_score --> call_round
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_input_tps
    core_benchmark_models_py_ProviderBenchmarkMetrics_input_tps --> call_round
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_output_tps
    core_benchmark_models_py_ProviderBenchmarkMetrics_output_tps --> call_round
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_total_tps
    core_benchmark_models_py_ProviderBenchmarkMetrics_total_tps --> call_round
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1m_tokens_usd
    core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1m_tokens_usd --> call_round
        core_benchmark_models_py_ProviderBenchmarkMetrics --- core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1k_tokens_usd
    core_benchmark_models_py_ProviderBenchmarkMetrics_cost_per_1k_tokens_usd --> call_round
        core_benchmark_models_py_MetricAggregator --- core_benchmark_models_py_MetricAggregator__percentile
    core_benchmark_models_py_MetricAggregator__percentile --> call_sorted
    core_benchmark_models_py_MetricAggregator__percentile --> call_math_ceil
    core_benchmark_models_py_MetricAggregator__percentile --> call_len
    core_benchmark_models_py_MetricAggregator__percentile --> call_max
        core_benchmark_models_py_MetricAggregator --- core_benchmark_models_py_MetricAggregator_aggregate
    core_benchmark_models_py_MetricAggregator_aggregate --> call_len
    core_benchmark_models_py_MetricAggregator_aggregate --> call_sum
    core_benchmark_models_py_MetricAggregator_aggregate --> call_LatencyMetrics
    core_benchmark_models_py_MetricAggregator_aggregate --> call_MetricAggregator__percentile
    core_benchmark_models_py_MetricAggregator_aggregate --> call_max
    core_benchmark_models_py_MetricAggregator_aggregate --> call_ProviderBenchmarkMetrics
    core_benchmark_models_py_MetricAggregator_aggregate --> call_round
        core_benchmark_models_py_BenchmarkRunReport --- core_benchmark_models_py_BenchmarkRunReport_total_tps_delta_percentage
    core_benchmark_models_py_BenchmarkRunReport_total_tps_delta_percentage --> call_round
        core_benchmark_models_py_BenchmarkRunReport --- core_benchmark_models_py_BenchmarkRunReport_cost_delta_percentage
    core_benchmark_models_py_BenchmarkRunReport_cost_delta_percentage --> call_round
        core_benchmark_orchestrator_py_DatasetIntegrityValidator --- core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call___exists
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_logger_error
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_hashlib_sha256
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_open
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_f_read
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_sha256_update
    core_benchmark_orchestrator_py_DatasetIntegrityValidator_verify --> call_sha256_hexdigest
        core_benchmark_orchestrator_py_SequentialBenchmarkOrchestrator --- core_benchmark_orchestrator_py_SequentialBenchmarkOrchestrator___init__
        core_benchmark_persistence_py_BenchmarkPersistenceGateway --- core_benchmark_persistence_py_BenchmarkPersistenceGateway___init__
    core_benchmark_persistence_py_BenchmarkPersistenceGateway___init__ --> call_Path
    core_benchmark_persistence_py_BenchmarkPersistenceGateway___init__ --> call___mkdir
        core_benchmark_persistence_py_BenchmarkPersistenceGateway --- core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_raw_records_checkpoint
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_raw_records_checkpoint --> call_logger_info
        core_benchmark_persistence_py_BenchmarkPersistenceGateway --- core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report --> call_int
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report --> call_base_dir_mkdir
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report --> call_open
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report --> call_json_dump
    core_benchmark_persistence_py_BenchmarkPersistenceGateway_save_final_report --> call_logger_info
        core_benchmark_quality_py_FormalLatexSyntaxParser --- core_benchmark_quality_py_FormalLatexSyntaxParser_validate_syntax
    core_benchmark_quality_py_FormalLatexSyntaxParser_validate_syntax --> call_LatexWalker
    core_benchmark_quality_py_FormalLatexSyntaxParser_validate_syntax --> call_walker_get_latex_nodes
    core_benchmark_quality_py_FormalLatexSyntaxParser_validate_syntax --> call_logger_debug
        core_benchmark_quality_py_FormalMarkdownTableParser --- core_benchmark_quality_py_FormalMarkdownTableParser_validate_syntax
    core_benchmark_quality_py_FormalMarkdownTableParser_validate_syntax --> call_MarkdownIt
    core_benchmark_quality_py_FormalMarkdownTableParser_validate_syntax --> call_md_parse
    core_benchmark_quality_py_FormalMarkdownTableParser_validate_syntax --> call_sum
        core_benchmark_quality_py_StructuralQualityEvaluator --- core_benchmark_quality_py_StructuralQualityEvaluator_evaluate
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_StructuralQualityMetrics
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_len
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_sum
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_original_nodes_map_get
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_min
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_max
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_density_ratios_append
    core_benchmark_quality_py_StructuralQualityEvaluator_evaluate --> call_round
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator__interpret_cliffs_delta
    core_benchmark_reporter_py_StatisticalComparator__interpret_cliffs_delta --> call_abs
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_np_array
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_estimator_func
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call___choice
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_len
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_range
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_round
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_float
    core_benchmark_reporter_py_StatisticalComparator__bootstrap_estimator_ci --> call_np_percentile
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator_compare_series
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_ScientificSignificanceReport
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_cast
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_stats_mannwhitneyu
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_float
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_hasattr
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_stats_ks_2samp
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_len
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_cls__bootstrap_estimator_ci
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator__p95_estimator
    core_benchmark_reporter_py_StatisticalComparator__p95_estimator --> call_float
    core_benchmark_reporter_py_StatisticalComparator__p95_estimator --> call_np_percentile
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_round
    core_benchmark_reporter_py_StatisticalComparator_compare_series --> call_cls__interpret_cliffs_delta
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_list
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_reports_items
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_items_sort
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_min
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_len
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_enumerate
    core_benchmark_reporter_py_StatisticalComparator__apply_holm_bonferroni --> call_replace
        core_benchmark_reporter_py_StatisticalComparator --- core_benchmark_reporter_py_StatisticalComparator_run_stratified_analysis
    core_benchmark_reporter_py_StatisticalComparator_run_stratified_analysis --> call_cls_compare_series
    core_benchmark_reporter_py_StatisticalComparator_run_stratified_analysis --> call_cls__apply_holm_bonferroni
        core_benchmark_semantic_judge_py_SemanticJudge --- core_benchmark_semantic_judge_py_SemanticJudge___init__
    core_benchmark_semantic_judge_py_SemanticJudge___init__ --> call_AsyncGroq
    core_benchmark_semantic_judge_py_SemanticJudge___init__ --> call_os_getenv
        core_benchmark_runners_gemini_runner_py_DummyContextResolver --- core_benchmark_runners_gemini_runner_py_DummyContextResolver_resolve_many
        core_benchmark_runners_gemini_runner_py_DummyContextResolver --- core_benchmark_runners_gemini_runner_py_DummyContextResolver_resolve
    core_benchmark_runners_gemini_runner_py_DummyContextResolver_resolve --> call_ResolvedContext
        core_benchmark_runners_gemini_runner_py_GeminiBenchmarkRunner --- core_benchmark_runners_gemini_runner_py_GeminiBenchmarkRunner___init__
        core_benchmark_runners_groq_runner_py_DummyContextResolver --- core_benchmark_runners_groq_runner_py_DummyContextResolver_resolve_many
        core_benchmark_runners_groq_runner_py_DummyContextResolver --- core_benchmark_runners_groq_runner_py_DummyContextResolver_resolve
    core_benchmark_runners_groq_runner_py_DummyContextResolver_resolve --> call_ResolvedContext
        core_benchmark_runners_groq_runner_py_GroqBenchmarkRunner --- core_benchmark_runners_groq_runner_py_GroqBenchmarkRunner___init__
        core_compiler_assembler_py_IntegrityCheckedDocumentRepository --- core_compiler_assembler_py_IntegrityCheckedDocumentRepository_get_verified_payload
        core_compiler_assembler_py_DocumentAssemblyDecision --- core_compiler_assembler_py_DocumentAssemblyDecision_is_accepted
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler___init__
    core_compiler_assembler_py_DocumentAssembler___init__ --> call_AssemblyPolicy
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler__validate_sequence
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_len
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_set
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_ValueError
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_IncompleteDocumentError
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler_assemble
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_self__build_rejection
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_sorted
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_self__validate_sequence
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_len
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_content_parts_append
    core_compiler_assembler_py_DocumentAssembler_assemble --> call___get_verified_payload
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_str
    core_compiler_assembler_py_DocumentAssembler_assemble --> call___join
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_ReconstructedDocument
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_AssemblyReport
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_time_time
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_dict
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_Counter
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_bool
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_DocumentAssemblyDecision
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler__build_rejection
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_AssemblyReport
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_time_time
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_max
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_len
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_dict
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_Counter
    core_compiler_assembler_py_DocumentAssembler__build_rejection --> call_DocumentAssemblyDecision
        core_context_context_resolver_py_ResolvedContext --- core_context_context_resolver_py_ResolvedContext_depth
    core_context_context_resolver_py_ResolvedContext_depth --> call_len
        core_context_context_resolver_py_ContextResolverProtocol --- core_context_context_resolver_py_ContextResolverProtocol_resolve
        core_context_context_resolver_py_ContextResolverProtocol --- core_context_context_resolver_py_ContextResolverProtocol_resolve_many
        core_context_context_resolver_py_ContextMappingProvider --- core_context_context_resolver_py_ContextMappingProvider_mappings
        core_context_context_resolver_py_InMemoryContextResolver --- core_context_context_resolver_py_InMemoryContextResolver___init__
        core_context_context_resolver_py_InMemoryContextResolver --- core_context_context_resolver_py_InMemoryContextResolver_resolve
    core_context_context_resolver_py_InMemoryContextResolver_resolve --> call___get
    core_context_context_resolver_py_InMemoryContextResolver_resolve --> call_KeyError
    core_context_context_resolver_py_InMemoryContextResolver_resolve --> call_ResolvedContext
    core_context_context_resolver_py_InMemoryContextResolver_resolve --> call_tuple
        core_context_context_resolver_py_InMemoryContextResolver --- core_context_context_resolver_py_InMemoryContextResolver_resolve_many
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call_dict_fromkeys
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call___get
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call_missing_append
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call_ResolvedContext
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call_tuple
    core_context_context_resolver_py_InMemoryContextResolver_resolve_many --> call_KeyError
        core_execution_exceptions_py_IncompleteDocumentError --- core_execution_exceptions_py_IncompleteDocumentError___init__
    core_execution_exceptions_py_IncompleteDocumentError___init__ --> call_____init__
    core_execution_exceptions_py_IncompleteDocumentError___init__ --> call_super
        core_execution_exceptions_py_CircuitOpenError --- core_execution_exceptions_py_CircuitOpenError___init__
    core_execution_exceptions_py_CircuitOpenError___init__ --> call_____init__
    core_execution_exceptions_py_CircuitOpenError___init__ --> call_super
        core_execution_exceptions_py_ChunkExecutionError --- core_execution_exceptions_py_ChunkExecutionError___init__
    core_execution_exceptions_py_ChunkExecutionError___init__ --> call_____init__
    core_execution_exceptions_py_ChunkExecutionError___init__ --> call_super
    core_execution_exceptions_py_ChunkExecutionError___init__ --> call_str
        core_execution_exceptions_py_ChunkValidationError --- core_execution_exceptions_py_ChunkValidationError___init__
    core_execution_exceptions_py_ChunkValidationError___init__ --> call_____init__
    core_execution_exceptions_py_ChunkValidationError___init__ --> call_super
    core_execution_exceptions_py_ChunkValidationError___init__ --> call_Exception
        core_execution_exceptions_py_DocumentValidationError --- core_execution_exceptions_py_DocumentValidationError___init__
    core_execution_exceptions_py_DocumentValidationError___init__ --> call_____init__
    core_execution_exceptions_py_DocumentValidationError___init__ --> call_super
        core_execution_exceptions_py_ContextOverflowError --- core_execution_exceptions_py_ContextOverflowError___init__
    core_execution_exceptions_py_ContextOverflowError___init__ --> call_____init__
    core_execution_exceptions_py_ContextOverflowError___init__ --> call_super
        core_execution_exceptions_py_ContextOverflowError --- core_execution_exceptions_py_ContextOverflowError___str__
    core_execution_exceptions_py_ContextOverflowError___str__ --> call_____str__
    core_execution_exceptions_py_ContextOverflowError___str__ --> call_super
        core_execution_handlers_py_DocumentCommandHandler --- core_execution_handlers_py_DocumentCommandHandler___init__
        core_execution_handlers_py_DocumentCommandHandler --- core_execution_handlers_py_DocumentCommandHandler__get_target_state
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_isinstance
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_getattr
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_ValueError
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_DocumentState
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_mapping_get
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_type
    core_execution_handlers_py_DocumentCommandHandler__get_target_state --> call_TypeError
        core_execution_handlers_py_DocumentCommandHandler --- core_execution_handlers_py_DocumentCommandHandler_handle
    core_execution_handlers_py_DocumentCommandHandler_handle --> call___get_status
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_ValueError
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_DocumentState
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_self__get_target_state
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_FSMValidator_validate
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_getattr
    core_execution_handlers_py_DocumentCommandHandler_handle --> call___transition_to
    core_execution_handlers_py_DocumentCommandHandler_handle --> call_logger_info
        core_execution_handlers_py_ReconciliationCommandHandler --- core_execution_handlers_py_ReconciliationCommandHandler___init__
        core_execution_handlers_py_ReconciliationCommandHandler --- core_execution_handlers_py_ReconciliationCommandHandler_handle
    core_execution_handlers_py_ReconciliationCommandHandler_handle --> call_isinstance
    core_execution_handlers_py_ReconciliationCommandHandler_handle --> call_self_handle_rematerialize
    core_execution_handlers_py_ReconciliationCommandHandler_handle --> call_self_handle_recover_zombie
    core_execution_handlers_py_ReconciliationCommandHandler_handle --> call_TypeError
    core_execution_handlers_py_ReconciliationCommandHandler_handle --> call_type
        core_execution_handlers_py_ReconciliationCommandHandler --- core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_time_perf_counter
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___get_current_epoch
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_logger_warning
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___inc
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___get_latest_event
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_logger_error
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_TextNormalizer_normalize
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___hexdigest
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_hashlib_sha256
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_normalized_encode
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___upsert_projection
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call___mark_cqrs_reconciled
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_logger_info
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_round
    core_execution_handlers_py_ReconciliationCommandHandler_handle_rematerialize --> call_logger_exception
        core_execution_handlers_py_ReconciliationCommandHandler --- core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie
    core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie --> call___get_current_epoch
    core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie --> call_logger_warning
    core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie --> call___inc
    core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie --> call___mark_zombie_recovered
    core_execution_handlers_py_ReconciliationCommandHandler_handle_recover_zombie --> call_logger_info
        core_execution_models_py_ChunkExecutionEvent --- core_execution_models_py_ChunkExecutionEvent_content_hash
    core_execution_models_py_ChunkExecutionEvent_content_hash --> call_json_dumps
    core_execution_models_py_ChunkExecutionEvent_content_hash --> call___hexdigest
    core_execution_models_py_ChunkExecutionEvent_content_hash --> call_hashlib_sha256
    core_execution_models_py_ChunkExecutionEvent_content_hash --> call_base_encode
        core_execution_models_py_ChunkExecutionEvent --- core_execution_models_py_ChunkExecutionEvent_is_assemblable
        core_execution_ports_py_ControlPlanePort --- core_execution_ports_py_ControlPlanePort_enqueue_tasks
        core_execution_ports_py_ControlPlanePort --- core_execution_ports_py_ControlPlanePort_pick_task
        core_execution_ports_py_ControlPlanePort --- core_execution_ports_py_ControlPlanePort_acknowledge_execution
        core_execution_ports_py_ControlPlanePort --- core_execution_ports_py_ControlPlanePort_abandon_execution
        core_execution_ports_py_ControlPlanePort --- core_execution_ports_py_ControlPlanePort_renew_task_lease
        core_execution_ports_py_EventPlanePort --- core_execution_ports_py_EventPlanePort_get_replay
        core_execution_ports_py_EventPlanePort --- core_execution_ports_py_EventPlanePort_append_wal
        core_execution_ports_py_MaterializedPlanePort --- core_execution_ports_py_MaterializedPlanePort_get_projection_status
        core_execution_ports_py_MaterializedPlanePort --- core_execution_ports_py_MaterializedPlanePort_upsert_projection
        core_execution_ports_py_MaterializedPlanePort --- core_execution_ports_py_MaterializedPlanePort_get_assemblable_chunks
        core_execution_state_py_FSMValidator --- core_execution_state_py_FSMValidator_validate
    core_execution_state_py_FSMValidator_validate --> call_LEGAL_TRANSITIONS_get
    core_execution_state_py_FSMValidator_validate --> call_set
    core_execution_state_py_FSMValidator_validate --> call_IllegalStateTransitionError
        core_healing_base_py_BaseHealingStrategy --- core_healing_base_py_BaseHealingStrategy_invariant_family
        core_healing_base_py_BaseHealingStrategy --- core_healing_base_py_BaseHealingStrategy_priority
        core_healing_base_py_BaseHealingStrategy --- core_healing_base_py_BaseHealingStrategy_heal
        core_healing_models_py_HealingResult --- core_healing_models_py_HealingResult_final_text
        core_healing_models_py_HealingContext --- core_healing_models_py_HealingContext___post_init__
    core_healing_models_py_HealingContext___post_init__ --> call_HealingContractViolationError
        core_healing_pipeline_py_HealingPipeline --- core_healing_pipeline_py_HealingPipeline___init__
    core_healing_pipeline_py_HealingPipeline___init__ --> call_HealingTelemetryRegistry
    core_healing_pipeline_py_HealingPipeline___init__ --> call_sorted
        core_healing_pipeline_py_HealingPipeline --- core_healing_pipeline_py_HealingPipeline_heal_and_revalidate
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call___get
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_HealingResult
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call___record
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_HealingEvent
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_getattr
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_time_perf_counter
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_strategy_heal
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_logger_error
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_str
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_round
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_replace
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call___validate_chunk
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call___join
    core_healing_pipeline_py_HealingPipeline_heal_and_revalidate --> call_logger_warning
        core_healing_telemetry_py_HealingEvent --- core_healing_telemetry_py_HealingEvent_to_dict
    core_healing_telemetry_py_HealingEvent_to_dict --> call_asdict
        core_healing_telemetry_py_HealingTelemetryRegistry --- core_healing_telemetry_py_HealingTelemetryRegistry___init__
    core_healing_telemetry_py_HealingTelemetryRegistry___init__ --> call_deque
    core_healing_telemetry_py_HealingTelemetryRegistry___init__ --> call_threading_Lock
        core_healing_telemetry_py_HealingTelemetryRegistry --- core_healing_telemetry_py_HealingTelemetryRegistry_record
    core_healing_telemetry_py_HealingTelemetryRegistry_record --> call___append
    core_healing_telemetry_py_HealingTelemetryRegistry_record --> call_self__update_aggregates_unlocked
    core_healing_telemetry_py_HealingTelemetryRegistry_record --> call_logger_info
    core_healing_telemetry_py_HealingTelemetryRegistry_record --> call_event_to_dict
        core_healing_telemetry_py_HealingTelemetryRegistry --- core_healing_telemetry_py_HealingTelemetryRegistry__update_aggregates_unlocked
        core_healing_telemetry_py_HealingTelemetryRegistry --- core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics
    core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics --> call_v_copy
    core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics --> call___items
    core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics --> call_snapshot_items
    core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics --> call_round
    core_healing_telemetry_py_HealingTelemetryRegistry_get_aggregate_metrics --> call_int
        core_healing_telemetry_py_HealingTelemetryRegistry --- core_healing_telemetry_py_HealingTelemetryRegistry_get_events
    core_healing_telemetry_py_HealingTelemetryRegistry_get_events --> call_list
    core_healing_testing_factories_py_make_test_healing_context --> call_ValidationContext
    core_healing_testing_factories_py_make_test_healing_context --> call_ValidationResult
    core_healing_testing_factories_py_make_test_healing_context --> call_HealingContext
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy --- core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_invariant_family
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy --- core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_priority
        core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy --- core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal
    core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal --> call_re_compile
    core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal --> call_pattern_match
    core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal --> call_HealingResult
    core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal --> call___strip
    core_healing_strategies_markdown_leakage_py_MarkdownLeakageHealingStrategy_heal --> call_match_group
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy --- core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_invariant_family
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy --- core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_priority
        core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy --- core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal
    core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal --> call_re_compile
    core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal --> call_pattern_match
    core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal --> call_HealingResult
    core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal --> call_pattern_sub
    core_healing_strategies_meta_text_leakage_py_MetaTextLeakageHealingStrategy_heal --> call_cleaned_strip
        core_healing_strategies_structural_py_EOFBraceClosureStrategy --- core_healing_strategies_structural_py_EOFBraceClosureStrategy___init__
    core_healing_strategies_structural_py_EOFBraceClosureStrategy___init__ --> call_HealingPolicy
        core_healing_strategies_structural_py_EOFBraceClosureStrategy --- core_healing_strategies_structural_py_EOFBraceClosureStrategy_invariant_family
        core_healing_strategies_structural_py_EOFBraceClosureStrategy --- core_healing_strategies_structural_py_EOFBraceClosureStrategy_priority
        core_healing_strategies_structural_py_EOFBraceClosureStrategy --- core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal
    core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal --> call_re_compile
    core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal --> call_verbatim_block_pattern_sub
    core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal --> call_inline_verb_pattern_sub
    core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal --> call_len
    core_healing_strategies_structural_py_EOFBraceClosureStrategy_heal --> call_HealingResult
        core_healing_strategies_structural_py_EOFMathClosureStrategy --- core_healing_strategies_structural_py_EOFMathClosureStrategy___init__
    core_healing_strategies_structural_py_EOFMathClosureStrategy___init__ --> call_HealingPolicy
        core_healing_strategies_structural_py_EOFMathClosureStrategy --- core_healing_strategies_structural_py_EOFMathClosureStrategy_invariant_family
        core_healing_strategies_structural_py_EOFMathClosureStrategy --- core_healing_strategies_structural_py_EOFMathClosureStrategy_priority
        core_healing_strategies_structural_py_EOFMathClosureStrategy --- core_healing_strategies_structural_py_EOFMathClosureStrategy_heal
    core_healing_strategies_structural_py_EOFMathClosureStrategy_heal --> call_len
    core_healing_strategies_structural_py_EOFMathClosureStrategy_heal --> call_HealingResult
    core_healing_strategies_structural_py_EOFMathClosureStrategy_heal --> call_original_rstrip
    core_healing_strategies_structural_py_EOFMathClosureStrategy_heal --> call_base_text_endswith
        core_metrics_exporters_py_MetricsExporter --- core_metrics_exporters_py_MetricsExporter_export
        core_metrics_exporters_py_ConsoleMetricsExporter --- core_metrics_exporters_py_ConsoleMetricsExporter_export
    core_metrics_exporters_py_ConsoleMetricsExporter_export --> call_print
        core_metrics_exporters_py_JsonMetricsExporter --- core_metrics_exporters_py_JsonMetricsExporter___init__
        core_metrics_exporters_py_JsonMetricsExporter --- core_metrics_exporters_py_JsonMetricsExporter_export
    core_metrics_exporters_py_JsonMetricsExporter_export --> call_open
    core_metrics_exporters_py_JsonMetricsExporter_export --> call_json_dump
    core_metrics_exporters_py_JsonMetricsExporter_export --> call_dataclasses_asdict
    core_metrics_measure_density_py_measure_pdf_density --> call_print
    core_metrics_measure_density_py_measure_pdf_density --> call_time_time
    core_metrics_measure_density_py_measure_pdf_density --> call_fitz_open
    core_metrics_measure_density_py_measure_pdf_density --> call_len
    core_metrics_measure_density_py_measure_pdf_density --> call_range
    core_metrics_measure_density_py_measure_pdf_density --> call_page_get_text
    core_metrics_measure_density_py_measure_pdf_density --> call_isinstance
    core_metrics_measure_density_py_measure_pdf_density --> call_text_str_strip
    core_metrics_measure_density_py_measure_pdf_density --> call_char_counts_append
    core_metrics_measure_density_py_measure_pdf_density --> call_doc_close
    core_metrics_measure_density_py_measure_pdf_density --> call_sum
    core_metrics_measure_density_py_measure_pdf_density --> call_min
    core_metrics_measure_density_py_measure_pdf_density --> call_max
        core_metrics_metrics_py_Metrics --- core_metrics_metrics_py_Metrics___init__
    core_metrics_metrics_py_Metrics___init__ --> call_defaultdict
    core_metrics_metrics_py_Metrics___init__ --> call_float
    core_metrics_metrics_py_Metrics___init__ --> call_time_time
        core_metrics_metrics_py_Metrics --- core_metrics_metrics_py_Metrics_inc
        core_metrics_metrics_py_Metrics --- core_metrics_metrics_py_Metrics_observe
    core_metrics_metrics_py_Metrics_observe --> call_max
    core_metrics_metrics_py_Metrics_observe --> call_min
        core_metrics_metrics_py_Metrics --- core_metrics_metrics_py_Metrics_summary
    core_metrics_metrics_py_Metrics_summary --> call_round
    core_metrics_metrics_py_Metrics_summary --> call_time_time
    core_metrics_metrics_py_Metrics_summary --> call_dict
    core_metrics_metrics_py_Metrics_summary --> call___items
        core_metrics_pricing_py_PricingEngine --- core_metrics_pricing_py_PricingEngine_calculate_cost
    core_metrics_pricing_py_PricingEngine_calculate_cost --> call_model_name_startswith
    core_metrics_pricing_py_PricingEngine_calculate_cost --> call___get
    core_metrics_pricing_py_PricingEngine_calculate_cost --> call_ValueError
        core_metrics_summary_py_SummaryBuilder --- core_metrics_summary_py_SummaryBuilder__percentile
    core_metrics_summary_py_SummaryBuilder__percentile --> call_sorted
    core_metrics_summary_py_SummaryBuilder__percentile --> call_len
    core_metrics_summary_py_SummaryBuilder__percentile --> call_math_ceil
    core_metrics_summary_py_SummaryBuilder__percentile --> call_max
        core_metrics_summary_py_SummaryBuilder --- core_metrics_summary_py_SummaryBuilder_build
    core_metrics_summary_py_SummaryBuilder_build --> call_len
    core_metrics_summary_py_SummaryBuilder_build --> call_utilization_ratios_append
    core_metrics_summary_py_SummaryBuilder_build --> call___get
    core_metrics_summary_py_SummaryBuilder_build --> call_quota_waits_append
    core_metrics_summary_py_SummaryBuilder_build --> call_quota_attempts_append
    core_metrics_summary_py_SummaryBuilder_build --> call_sum
    core_metrics_summary_py_SummaryBuilder_build --> call___startswith
    core_metrics_summary_py_SummaryBuilder_build --> call___replace
    core_metrics_summary_py_SummaryBuilder_build --> call_max
    core_metrics_summary_py_SummaryBuilder_build --> call_PricingEngine_calculate_cost
    core_metrics_summary_py_SummaryBuilder_build --> call_TranslationAuditSummary
    core_metrics_summary_py_SummaryBuilder_build --> call_round
    core_metrics_summary_py_SummaryBuilder_build --> call_SummaryBuilder__percentile
        core_normalization_base_py_BaseNormalizer --- core_normalization_base_py_BaseNormalizer_normalizer_id
        core_normalization_base_py_BaseNormalizer --- core_normalization_base_py_BaseNormalizer_normalizer_version
        core_normalization_base_py_BaseNormalizer --- core_normalization_base_py_BaseNormalizer_signature
    core_normalization_base_py_BaseNormalizer_signature --> call___hexdigest
    core_normalization_base_py_BaseNormalizer_signature --> call_hashlib_sha256
    core_normalization_base_py_BaseNormalizer_signature --> call___encode
    core_normalization_base_py_BaseNormalizer_signature --> call_str
        core_normalization_base_py_BaseNormalizer --- core_normalization_base_py_BaseNormalizer_normalize
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_NormalizationPolicyRegistry_get_instance
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_logger_debug
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call___find_spec
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_RuntimeError
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_NormalizationPolicy
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_paragraph_policy_append
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_ParagraphNormalizer
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_registry_register_policy
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_registry_map_type_to_domain
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_math_policy_append
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_MathDomainNormalizer
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_registry_freeze
    core_normalization_bootstrap_py_bootstrap_normalization_layer --> call_logger_info
        core_normalization_classifier_py_SemanticNodeClassifier --- core_normalization_classifier_py_SemanticNodeClassifier___init__
    core_normalization_classifier_py_SemanticNodeClassifier___init__ --> call_re_compile
        core_normalization_classifier_py_SemanticNodeClassifier --- core_normalization_classifier_py_SemanticNodeClassifier__infer_heading
    core_normalization_classifier_py_SemanticNodeClassifier__infer_heading --> call_text_stripped_startswith
    core_normalization_classifier_py_SemanticNodeClassifier__infer_heading --> call_min
    core_normalization_classifier_py_SemanticNodeClassifier__infer_heading --> call_dict
    core_normalization_classifier_py_SemanticNodeClassifier__infer_heading --> call_node_model_copy
        core_normalization_classifier_py_SemanticNodeClassifier --- core_normalization_classifier_py_SemanticNodeClassifier_classify_node
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_text_strip
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_self__infer_heading
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call___search
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_env_match_group
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_self__mutate_node_type
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_len
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call___findall
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call___finditer
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call___strip
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call___replace
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_match_group
    core_normalization_classifier_py_SemanticNodeClassifier_classify_node --> call_inner_content_isdigit
        core_normalization_classifier_py_SemanticNodeClassifier --- core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type
    core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type --> call_dict
    core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type --> call_hasattr
    core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type --> call_str
    core_normalization_classifier_py_SemanticNodeClassifier__mutate_node_type --> call_node_model_copy
        core_normalization_classifier_py_SemanticNodeClassifier --- core_normalization_classifier_py_SemanticNodeClassifier_classify_batch
    core_normalization_classifier_py_SemanticNodeClassifier_classify_batch --> call_self_classify_node
        core_normalization_latex_sanitizer_py_InlineMathProtector --- core_normalization_latex_sanitizer_py_InlineMathProtector_mask
        core_normalization_latex_sanitizer_py_InlineMathProtector --- core_normalization_latex_sanitizer_py_InlineMathProtector__replacer
    core_normalization_latex_sanitizer_py_InlineMathProtector__replacer --> call_len
    core_normalization_latex_sanitizer_py_InlineMathProtector__replacer --> call_match_group
    core_normalization_latex_sanitizer_py_InlineMathProtector_mask --> call___sub
        core_normalization_latex_sanitizer_py_InlineMathProtector --- core_normalization_latex_sanitizer_py_InlineMathProtector_restore
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call_mapping_items
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call___split
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call_token_strip
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call_re_compile
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call_str
    core_normalization_latex_sanitizer_py_InlineMathProtector_restore --> call_safe_token_pattern_sub
        core_normalization_normalizer_py_TextNormalizer --- core_normalization_normalizer_py_TextNormalizer__decode_html
    core_normalization_normalizer_py_TextNormalizer__decode_html --> call_html_unescape
        core_normalization_normalizer_py_TextNormalizer --- core_normalization_normalizer_py_TextNormalizer__normalize_unicode
    core_normalization_normalizer_py_TextNormalizer__normalize_unicode --> call_unicodedata_normalize
        core_normalization_normalizer_py_TextNormalizer --- core_normalization_normalizer_py_TextNormalizer__strip_control_chars
    core_normalization_normalizer_py_TextNormalizer__strip_control_chars --> call_re_sub
        core_normalization_normalizer_py_TextNormalizer --- core_normalization_normalizer_py_TextNormalizer_normalize
    core_normalization_normalizer_py_TextNormalizer_normalize --> call_step
        core_normalization_pipeline_py_NormalizationPipeline --- core_normalization_pipeline_py_NormalizationPipeline___init__
    core_normalization_pipeline_py_NormalizationPipeline___init__ --> call_NormalizationPolicyRegistry_get_instance
    core_normalization_pipeline_py_NormalizationPipeline___init__ --> call_Lock
        core_normalization_pipeline_py_NormalizationPipeline --- core_normalization_pipeline_py_NormalizationPipeline_dropped_events_count
        core_normalization_pipeline_py_NormalizationPipeline --- core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash
    core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash --> call___hexdigest
    core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash --> call_hashlib_sha256
    core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash --> call_text_encode
    core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash --> call_json_dumps
    core_normalization_pipeline_py_NormalizationPipeline__compute_deterministic_hash --> call_json_payload_encode
        core_normalization_pipeline_py_NormalizationPipeline --- core_normalization_pipeline_py_NormalizationPipeline_process_node
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_hasattr
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_str
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call___get_policy_for_type
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_self__compute_deterministic_hash
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call___get
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_NormalizationReport
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_dict
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_time_time
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_node_model_copy
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_normalizer_normalize
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_traces_append
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_NormalizerTrace
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_len
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_warnings_extend
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_hard_fails_extend
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_NormalizationEvent
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_json_dumps
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call___put_nowait
    core_normalization_pipeline_py_NormalizationPipeline_process_node --> call_logger_warning
        core_normalization_pipeline_py_NormalizationPipeline --- core_normalization_pipeline_py_NormalizationPipeline_process_batch
    core_normalization_pipeline_py_NormalizationPipeline_process_batch --> call_self_process_node
        core_normalization_registry_py_NormalizationPolicy --- core_normalization_registry_py_NormalizationPolicy___init__
        core_normalization_registry_py_NormalizationPolicy --- core_normalization_registry_py_NormalizationPolicy_append
    core_normalization_registry_py_NormalizationPolicy_append --> call___append
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry___new__
    core_normalization_registry_py_NormalizationPolicyRegistry___new__ --> call_____new__
    core_normalization_registry_py_NormalizationPolicyRegistry___new__ --> call_super
    core_normalization_registry_py_NormalizationPolicyRegistry___new__ --> call____init_registry
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry__init_registry
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_is_bootstrapped
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_map_type_to_domain
    core_normalization_registry_py_NormalizationPolicyRegistry_map_type_to_domain --> call_RuntimeError
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_register_policy
    core_normalization_registry_py_NormalizationPolicyRegistry_register_policy --> call_RuntimeError
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_get_policy_for_type
    core_normalization_registry_py_NormalizationPolicyRegistry_get_policy_for_type --> call___get
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_freeze
    core_normalization_registry_py_NormalizationPolicyRegistry_freeze --> call___items
    core_normalization_registry_py_NormalizationPolicyRegistry_freeze --> call_RuntimeError
        core_normalization_registry_py_NormalizationPolicyRegistry --- core_normalization_registry_py_NormalizationPolicyRegistry_get_instance
    core_normalization_registry_py_NormalizationPolicyRegistry_get_instance --> call_cls
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher --- core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher___init__
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher --- core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher__validate_registry
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher__validate_registry --> call___get
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher__validate_registry --> call_ValueError
        core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher --- core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___get
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___strip
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___lstrip
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_warnings_append
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_WarningEntry
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_hierarchy_stack_append
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_enriched_nodes_append
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___encode
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___join
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___upper
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call___hexdigest
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_hashlib_blake2b
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_dict
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_len
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_node_model_copy
    core_normalization_enrichers_context_enricher_py_HierarchicalContextEnricher_enrich_document --> call_self__validate_registry
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder --- core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder___init__
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder --- core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalizer_id
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder --- core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalizer_version
        core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder --- core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize
    core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize --> call_text_strip
    core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize --> call_NormalizerResult
    core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize --> call_node_type_upper
    core_normalization_fixers_asset_placeholder_py_StructuralAssetPlaceholder_normalize --> call_asset_type_lower
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker --- core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_re_compile
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_len
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_cmd_pattern_match
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_match_group
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_match_start
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_match_end
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_min
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_uuid_uuid4
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call_result_append
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker__scan_inline_verbatim --> call___join
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker --- core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_mask
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_mask --> call_ProtectedRegionMasker__scan_inline_verbatim
        core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker --- core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_replacer
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_replacer --> call_uuid_uuid4
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_replacer --> call_match_group
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_mask --> call_re_compile
    core_normalization_fixers_math_pipeline_py_ProtectedRegionMasker_mask --> call_env_pattern_sub
        core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer --- core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer_restore
    core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer_restore --> call_any
    core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer_restore --> call_vault_items
    core_normalization_fixers_math_pipeline_py_ProtectedRegionRestorer_restore --> call_restored_text_replace
        core_normalization_fixers_math_pipeline_py_MathDelimiterValidator --- core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate
    core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate --> call_len
    core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate --> call_min
    core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate --> call_warnings_append
    core_normalization_fixers_math_pipeline_py_MathDelimiterValidator_validate --> call_WarningEntry
        core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator --- core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_re_compile
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_env_token_finditer
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_match_groups
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_warnings_append
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_WarningEntry
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_stack_append
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call_stack_pop
    core_normalization_fixers_math_pipeline_py_MathEnvironmentValidator_validate --> call___join
        core_normalization_fixers_math_pipeline_py_MathHtmlPurifier --- core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call___search
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_BeautifulSoup
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_soup_find_all
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call___strip
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_tag_get_text
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_raw_startswith
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_raw_endswith
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_tag_replace_with
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_isinstance
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call___endswith
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_str
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_tag_unwrap
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_HTMLFormatter
    core_normalization_fixers_math_pipeline_py_MathHtmlPurifier_purify --> call_soup_decode_contents
        core_normalization_fixers_math_pipeline_py_DeprecatedDelimiterConverter --- core_normalization_fixers_math_pipeline_py_DeprecatedDelimiterConverter_convert
    core_normalization_fixers_math_pipeline_py_DeprecatedDelimiterConverter_convert --> call___sub
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer --- core_normalization_fixers_math_pipeline_py_MathDomainNormalizer___init__
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer --- core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalizer_id
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer --- core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalizer_version
        core_normalization_fixers_math_pipeline_py_MathDomainNormalizer --- core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_text_strip
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_NormalizerResult
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_defaultdict
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_ProtectedRegionMasker_mask
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_MathDelimiterValidator_validate
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_MathEnvironmentValidator_validate
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_MathHtmlPurifier_purify
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_DeprecatedDelimiterConverter_convert
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_ProtectedRegionRestorer_restore
    core_normalization_fixers_math_pipeline_py_MathDomainNormalizer_normalize --> call_metrics_items
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer___init__
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer___init__ --> call_re_compile
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalizer_id
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalizer_version
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__check_domain_anomalies
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__check_domain_anomalies --> call___search
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__check_domain_anomalies --> call_warnings_append
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__check_domain_anomalies --> call_WarningEntry
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_BeautifulSoup
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_soup_find_all
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_isinstance
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_comment_extract
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call___strip
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_get_text
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_raw_text_startswith
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_raw_text_endswith
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_replace_with
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_re_sub
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_insert_before
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_insert_after
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_unwrap
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_tag_decompose
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_HTMLFormatter
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_html_dom --> call_soup_decode_contents
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_markdown_syntax
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_markdown_syntax --> call___search
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer__normalize_markdown_syntax --> call___sub
        core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer --- core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_text_strip
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_NormalizerResult
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_defaultdict
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_self__check_domain_anomalies
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_self__normalize_html_dom
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_self__normalize_markdown_syntax
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call___strip
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_re_sub
    core_normalization_fixers_paragraph_normalizer_py_ParagraphNormalizer_normalize --> call_fixes_map_items
        core_normalization_validators_ast_integrity_py_ASTIntegrityValidator --- core_normalization_validators_ast_integrity_py_ASTIntegrityValidator___init__
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator___init__ --> call_re_compile
        core_normalization_validators_ast_integrity_py_ASTIntegrityValidator --- core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_warnings_append
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_WarningEntry
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_set
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_len
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_enumerate
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_seen_ids_add
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call___count
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call___findall
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_range
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_max
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call_min
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call___get
    core_normalization_validators_ast_integrity_py_ASTIntegrityValidator_validate_ast --> call___search
        core_pipeline_job_py_TranslationJob --- core_pipeline_job_py_TranslationJob_mark_started
    core_pipeline_job_py_TranslationJob_mark_started --> call_datetime_now
        core_pipeline_job_py_TranslationJob --- core_pipeline_job_py_TranslationJob_mark_processing
    core_pipeline_job_py_TranslationJob_mark_processing --> call_ValueError
    core_pipeline_job_py_TranslationJob_mark_processing --> call_self_mark_started
        core_pipeline_job_py_TranslationJob --- core_pipeline_job_py_TranslationJob_enter_step
    core_pipeline_job_py_TranslationJob_enter_step --> call_RuntimeError
        core_pipeline_job_py_TranslationJob --- core_pipeline_job_py_TranslationJob_mark_completed
    core_pipeline_job_py_TranslationJob_mark_completed --> call_datetime_now
        core_pipeline_job_py_TranslationJob --- core_pipeline_job_py_TranslationJob_mark_failed
    core_pipeline_job_py_TranslationJob_mark_failed --> call_datetime_now
        core_pipeline_orchestrator_py_ParserProtocol --- core_pipeline_orchestrator_py_ParserProtocol_parse
        core_pipeline_orchestrator_py_ChunkerProtocol --- core_pipeline_orchestrator_py_ChunkerProtocol_chunk
        core_pipeline_orchestrator_py_AssemblerProtocol --- core_pipeline_orchestrator_py_AssemblerProtocol_assemble
        core_pipeline_orchestrator_py_AuditBuilderProtocol --- core_pipeline_orchestrator_py_AuditBuilderProtocol_build
        core_pipeline_orchestrator_py_DocumentRepositoryProtocol --- core_pipeline_orchestrator_py_DocumentRepositoryProtocol_save_batch
        core_pipeline_orchestrator_py_TranslationPipeline --- core_pipeline_orchestrator_py_TranslationPipeline___init__
    core_pipeline_orchestrator_py_TranslationPipeline___init__ --> call_re_compile
        core_pipeline_state_store_py_StateStoreProtocol --- core_pipeline_state_store_py_StateStoreProtocol_save
        core_pipeline_state_store_py_StateStoreProtocol --- core_pipeline_state_store_py_StateStoreProtocol_load
        core_pipeline_state_store_py_FSMStateStore --- core_pipeline_state_store_py_FSMStateStore___init__
        core_pipeline_state_store_py_FSMStateStore --- core_pipeline_state_store_py_FSMStateStore_load
    core_pipeline_state_store_py_FSMStateStore_load --> call___get_by_document_id
    core_pipeline_state_store_py_FSMStateStore_load --> call_RecoveredJobSnapshot
        core_pipeline_state_store_py_FSMStateStore --- core_pipeline_state_store_py_FSMStateStore_save
    core_pipeline_state_store_py_FSMStateStore_save --> call_RuntimeError
    core_pipeline_state_store_py_FSMStateStore_save --> call___get_status
    core_pipeline_state_store_py_FSMStateStore_save --> call___initialize_document
    core_pipeline_state_store_py_FSMStateStore_save --> call___get
    core_pipeline_state_store_py_FSMStateStore_save --> call_FailDocumentCommand
    core_pipeline_state_store_py_FSMStateStore_save --> call_MarkAssemblyReadyCommand
    core_pipeline_state_store_py_FSMStateStore_save --> call___handle
    core_pipeline_state_store_py_FSMStateStore_save --> call_MarkCompilationReadyCommand
    core_pipeline_state_store_py_FSMStateStore_save --> call_StartCompilationCommand
    core_pipeline_state_store_py_FSMStateStore_save --> call_cmd_class
        core_resilience_circuit_breaker_py_GlobalCircuitBreaker --- core_resilience_circuit_breaker_py_GlobalCircuitBreaker___init__
    core_resilience_circuit_breaker_py_GlobalCircuitBreaker___init__ --> call_deque
    core_resilience_circuit_breaker_py_GlobalCircuitBreaker___init__ --> call_asyncio_Lock
        core_resilience_circuit_breaker_py_GlobalCircuitBreaker --- core_resilience_circuit_breaker_py_GlobalCircuitBreaker__prune_window
    core_resilience_circuit_breaker_py_GlobalCircuitBreaker__prune_window --> call___popleft
        core_resilience_circuit_breaker_py_CircuitBreakerRegistry --- core_resilience_circuit_breaker_py_CircuitBreakerRegistry_get_breaker
    core_resilience_circuit_breaker_py_CircuitBreakerRegistry_get_breaker --> call_GlobalCircuitBreaker
        core_telemetry_analyzer_py_TelemetryAnalyzer --- core_telemetry_analyzer_py_TelemetryAnalyzer___init__
    core_telemetry_analyzer_py_TelemetryAnalyzer___init__ --> call_SLOConfig
        core_telemetry_analyzer_py_TelemetryAnalyzer --- core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar --> call_sqlite3_connect
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar --> call_conn_execute
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar --> call_cursor_fetchone
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_scalar --> call_float
        core_telemetry_analyzer_py_TelemetryAnalyzer --- core_telemetry_analyzer_py_TelemetryAnalyzer__query_list
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_list --> call_sqlite3_connect
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_list --> call_conn_execute
    core_telemetry_analyzer_py_TelemetryAnalyzer__query_list --> call_cursor_fetchall
        core_telemetry_analyzer_py_TelemetryAnalyzer --- core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_self__query_scalar
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_ProductionHealthReport
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_int
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_sqlite3_connect
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_conn_execute
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_cursor_fetchall
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_round
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_self__query_list
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_float
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_np_percentile
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_violations_append
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_SLOViolation
    core_telemetry_analyzer_py_TelemetryAnalyzer_generate_report --> call_len
        core_telemetry_gates_py_HealthGateEvaluator --- core_telemetry_gates_py_HealthGateEvaluator_evaluate
    core_telemetry_gates_py_HealthGateEvaluator_evaluate --> call_logger_critical
    core_telemetry_gates_py_HealthGateEvaluator_evaluate --> call_logger_warning
        core_telemetry_gates_py_HealthGateEvaluator --- core_telemetry_gates_py_HealthGateEvaluator_enforce
    core_telemetry_gates_py_HealthGateEvaluator_enforce --> call_HealthGateEvaluator_evaluate
    core_telemetry_gates_py_HealthGateEvaluator_enforce --> call_RuntimeError
    core_telemetry_gates_py_HealthGateEvaluator_enforce --> call_logger_warning
        core_telemetry_gateway_py_SQLiteTelemetryGateway --- core_telemetry_gateway_py_SQLiteTelemetryGateway___init__
    core_telemetry_gateway_py_SQLiteTelemetryGateway___init__ --> call_Path
    core_telemetry_gateway_py_SQLiteTelemetryGateway___init__ --> call___mkdir
    core_telemetry_gateway_py_SQLiteTelemetryGateway___init__ --> call_asyncio_Queue
    core_telemetry_gateway_py_SQLiteTelemetryGateway___init__ --> call_self__init_db
        core_telemetry_gateway_py_SQLiteTelemetryGateway --- core_telemetry_gateway_py_SQLiteTelemetryGateway__init_db
    core_telemetry_gateway_py_SQLiteTelemetryGateway__init_db --> call_sqlite3_connect
    core_telemetry_gateway_py_SQLiteTelemetryGateway__init_db --> call_conn_execute
        core_telemetry_gateway_py_SQLiteTelemetryGateway --- core_telemetry_gateway_py_SQLiteTelemetryGateway_emit
    core_telemetry_gateway_py_SQLiteTelemetryGateway_emit --> call___put_nowait
    core_telemetry_gateway_py_SQLiteTelemetryGateway_emit --> call_logger_error
        core_telemetry_gateway_py_SQLiteTelemetryGateway --- core_telemetry_gateway_py_SQLiteTelemetryGateway__write_batch
    core_telemetry_gateway_py_SQLiteTelemetryGateway__write_batch --> call_sqlite3_connect
    core_telemetry_gateway_py_SQLiteTelemetryGateway__write_batch --> call_conn_executemany
    core_utils_fs_py_ensure_parent_dir --> call___mkdir
    core_utils_fs_py_ensure_parent_dir --> call_Path
        core_utils_logger_py_JsonFormatter --- core_utils_logger_py_JsonFormatter_format
    core_utils_logger_py_JsonFormatter_format --> call_time_strftime
    core_utils_logger_py_JsonFormatter_format --> call_time_gmtime
    core_utils_logger_py_JsonFormatter_format --> call_record_getMessage
    core_utils_logger_py_JsonFormatter_format --> call_getattr
    core_utils_logger_py_JsonFormatter_format --> call_log_record_update
    core_utils_logger_py_JsonFormatter_format --> call_json_dumps
    core_utils_logger_py_setup_logger --> call_logging_getLogger
    core_utils_logger_py_setup_logger --> call_logger_setLevel
    core_utils_logger_py_setup_logger --> call_logging_StreamHandler
    core_utils_logger_py_setup_logger --> call_handler_setFormatter
    core_utils_logger_py_setup_logger --> call_JsonFormatter
        core_utils_telemetry_py_DistributedContextFilter --- core_utils_telemetry_py_DistributedContextFilter_filter
    core_utils_telemetry_py_DistributedContextFilter_filter --> call_ctx_execution_id_get
    core_utils_telemetry_py_DistributedContextFilter_filter --> call_ctx_worker_id_get
    core_utils_telemetry_py_DistributedContextFilter_filter --> call_ctx_task_id_get
    core_utils_telemetry_py_DistributedContextFilter_filter --> call_ctx_node_id_get
        core_utils_telemetry_py_JSONFormatter --- core_utils_telemetry_py_JSONFormatter_format
    core_utils_telemetry_py_JSONFormatter_format --> call___isoformat
    core_utils_telemetry_py_JSONFormatter_format --> call_datetime_fromtimestamp
    core_utils_telemetry_py_JSONFormatter_format --> call_getattr
    core_utils_telemetry_py_JSONFormatter_format --> call_record_getMessage
    core_utils_telemetry_py_JSONFormatter_format --> call_isinstance
    core_utils_telemetry_py_JSONFormatter_format --> call_log_record_update
    core_utils_telemetry_py_JSONFormatter_format --> call_self_formatException
    core_utils_telemetry_py_JSONFormatter_format --> call_json_dumps
    core_utils_telemetry_py_setup_distributed_logger --> call_logging_getLogger
    core_utils_telemetry_py_setup_distributed_logger --> call_logger_setLevel
    core_utils_telemetry_py_setup_distributed_logger --> call_logging_StreamHandler
    core_utils_telemetry_py_setup_distributed_logger --> call_handler_addFilter
    core_utils_telemetry_py_setup_distributed_logger --> call_DistributedContextFilter
    core_utils_telemetry_py_setup_distributed_logger --> call_handler_setFormatter
    core_utils_telemetry_py_setup_distributed_logger --> call_JSONFormatter
    core_utils_telemetry_py_setup_distributed_logger --> call_logger_addHandler
    core_utils_telemetry_py_wrapper --> call_time_perf_counter
    core_utils_telemetry_py_wrapper --> call_func
    core_utils_telemetry_py_wrapper --> call_logging_getLogger
    core_utils_telemetry_py_wrapper --> call_logger_info
    core_utils_telemetry_py_wrapper --> call_round
    core_utils_telemetry_py_wrapper --> call_wraps
        core_validation_base_py_Validator --- core_validation_base_py_Validator_validate
        core_validation_budget_py_TokenEstimatorProtocol --- core_validation_budget_py_TokenEstimatorProtocol_estimate_tokens
        core_validation_budget_py_ContextCompressionPolicy --- core_validation_budget_py_ContextCompressionPolicy_get_levels
        core_validation_budget_py_StandardCompressionPolicy --- core_validation_budget_py_StandardCompressionPolicy_get_levels
        core_validation_budget_py_PromptBudget --- core_validation_budget_py_PromptBudget_total_estimated
        core_validation_budget_py_PromptBudget --- core_validation_budget_py_PromptBudget_utilization_ratio
        core_validation_budget_py_PromptBudgetCalculator --- core_validation_budget_py_PromptBudgetCalculator___init__
        core_validation_budget_py_PromptBudgetCalculator --- core_validation_budget_py_PromptBudgetCalculator_calculate
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call___estimate_tokens
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call_int
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call_min
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call_max
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call_PromptBudget
    core_validation_budget_py_PromptBudgetCalculator_calculate --> call_BudgetDecision
        core_validation_estimators_py_ExactBPEEstimator --- core_validation_estimators_py_ExactBPEEstimator___init__
    core_validation_estimators_py_ExactBPEEstimator___init__ --> call_tiktoken_get_encoding
        core_validation_estimators_py_ExactBPEEstimator --- core_validation_estimators_py_ExactBPEEstimator_estimate_tokens
    core_validation_estimators_py_ExactBPEEstimator_estimate_tokens --> call_len
    core_validation_estimators_py_ExactBPEEstimator_estimate_tokens --> call___encode
        core_validation_interfaces_py_BaseValidator --- core_validation_interfaces_py_BaseValidator_validate
        core_validation_legacy_adapter_py_LegacyValidatorAdapter --- core_validation_legacy_adapter_py_LegacyValidatorAdapter___init__
        core_validation_legacy_adapter_py_LegacyValidatorAdapter --- core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate
    core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate --> call___validate
    core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate --> call___get
    core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate --> call_UnknownLegacyValidationCodeError
    core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate --> call_results_append
    core_validation_legacy_adapter_py_LegacyValidatorAdapter_validate --> call_ValidationResult
        core_validation_perimeter_py_PerimeterValidator --- core_validation_perimeter_py_PerimeterValidator_validate
    core_validation_perimeter_py_PerimeterValidator_validate --> call_results_append
    core_validation_perimeter_py_PerimeterValidator_validate --> call_ValidationResult
    core_validation_perimeter_py_PerimeterValidator_validate --> call___search
    core_validation_perimeter_py_PerimeterValidator_validate --> call___strip
    core_validation_perimeter_py_PerimeterValidator_validate --> call_match_group
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline___init__
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline_add_chunk_validator
    core_validation_pipeline_py_ValidationPipeline_add_chunk_validator --> call___append
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline_add_document_validator
    core_validation_pipeline_py_ValidationPipeline_add_document_validator --> call___append
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline_validate_chunk
    core_validation_pipeline_py_ValidationPipeline_validate_chunk --> call_self__run_validators
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline_validate_document
    core_validation_pipeline_py_ValidationPipeline_validate_document --> call_self__run_validators
        core_validation_pipeline_py_ValidationPipeline --- core_validation_pipeline_py_ValidationPipeline__run_validators
    core_validation_pipeline_py_ValidationPipeline__run_validators --> call_results_extend
    core_validation_pipeline_py_ValidationPipeline__run_validators --> call_validator_validate
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator_validate
    core_validation_preservation_py_PreservationValidator_validate --> call_results_extend
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_doi
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_url
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_isbn_orcid
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_cross_references
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_labels
    core_validation_preservation_py_PreservationValidator_validate --> call_self__check_dependencies
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_doi
    core_validation_preservation_py_PreservationValidator__check_doi --> call_d_lower
    core_validation_preservation_py_PreservationValidator__check_doi --> call___findall
    core_validation_preservation_py_PreservationValidator__check_doi --> call_ValidationResult
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_url
    core_validation_preservation_py_PreservationValidator__check_url --> call_u_rstrip
    core_validation_preservation_py_PreservationValidator__check_url --> call___findall
    core_validation_preservation_py_PreservationValidator__check_url --> call_ValidationResult
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_isbn_orcid
    core_validation_preservation_py_PreservationValidator__check_isbn_orcid --> call_o_lower
    core_validation_preservation_py_PreservationValidator__check_isbn_orcid --> call___findall
    core_validation_preservation_py_PreservationValidator__check_isbn_orcid --> call_results_append
    core_validation_preservation_py_PreservationValidator__check_isbn_orcid --> call_ValidationResult
    core_validation_preservation_py_PreservationValidator__check_isbn_orcid --> call_set
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_cross_references
    core_validation_preservation_py_PreservationValidator__check_cross_references --> call_self__extract_sub_keys
    core_validation_preservation_py_PreservationValidator__check_cross_references --> call___findall
    core_validation_preservation_py_PreservationValidator__check_cross_references --> call_ValidationResult
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_labels
    core_validation_preservation_py_PreservationValidator__check_labels --> call_self__extract_sub_keys
    core_validation_preservation_py_PreservationValidator__check_labels --> call___findall
    core_validation_preservation_py_PreservationValidator__check_labels --> call_ValidationResult
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__check_dependencies
    core_validation_preservation_py_PreservationValidator__check_dependencies --> call_self__extract_sub_keys
    core_validation_preservation_py_PreservationValidator__check_dependencies --> call___findall
    core_validation_preservation_py_PreservationValidator__check_dependencies --> call_ValidationResult
        core_validation_preservation_py_PreservationValidator --- core_validation_preservation_py_PreservationValidator__extract_sub_keys
    core_validation_preservation_py_PreservationValidator__extract_sub_keys --> call_set
    core_validation_preservation_py_PreservationValidator__extract_sub_keys --> call_match_split
    core_validation_preservation_py_PreservationValidator__extract_sub_keys --> call_part_strip
    core_validation_preservation_py_PreservationValidator__extract_sub_keys --> call_keys_add
        core_validation_semantic_py_SemanticValidator --- core_validation_semantic_py_SemanticValidator_validate
    core_validation_semantic_py_SemanticValidator_validate --> call_self__missing_numbers
    core_validation_semantic_py_SemanticValidator_validate --> call_results_append
    core_validation_semantic_py_SemanticValidator_validate --> call_ValidationResult
    core_validation_semantic_py_SemanticValidator_validate --> call_self__missing_units
        core_validation_semantic_py_SemanticValidator --- core_validation_semantic_py_SemanticValidator__missing_numbers
    core_validation_semantic_py_SemanticValidator__missing_numbers --> call_Counter
    core_validation_semantic_py_SemanticValidator__missing_numbers --> call___findall
    core_validation_semantic_py_SemanticValidator__missing_numbers --> call_source_counts_items
    core_validation_semantic_py_SemanticValidator__missing_numbers --> call_missing_extend
        core_validation_semantic_py_SemanticValidator --- core_validation_semantic_py_SemanticValidator__missing_units
    core_validation_semantic_py_SemanticValidator__missing_units --> call_set
    core_validation_semantic_py_SemanticValidator__missing_units --> call___findall
    core_validation_semantic_py_SemanticValidator__missing_units --> call_list
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator_validate
    core_validation_structural_validator_py_StructuralValidator_validate --> call_cls__has_residual_html
    core_validation_structural_validator_py_StructuralValidator_validate --> call_errors_append
    core_validation_structural_validator_py_StructuralValidator_validate --> call_ValidationError
    core_validation_structural_validator_py_StructuralValidator_validate --> call_cls__check_braces
    core_validation_structural_validator_py_StructuralValidator_validate --> call_cls__check_brackets
    core_validation_structural_validator_py_StructuralValidator_validate --> call_cls__check_math_delimiters
    core_validation_structural_validator_py_StructuralValidator_validate --> call_cls__check_environments
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator__has_residual_html
    core_validation_structural_validator_py_StructuralValidator__has_residual_html --> call_re_sub
    core_validation_structural_validator_py_StructuralValidator__has_residual_html --> call_re_findall
    core_validation_structural_validator_py_StructuralValidator__has_residual_html --> call_any
    core_validation_structural_validator_py_StructuralValidator__has_residual_html --> call_tag_lower
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator__check_braces
    core_validation_structural_validator_py_StructuralValidator__check_braces --> call_re_sub
    core_validation_structural_validator_py_StructuralValidator__check_braces --> call_ValidationError
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator__check_brackets
    core_validation_structural_validator_py_StructuralValidator__check_brackets --> call_re_sub
    core_validation_structural_validator_py_StructuralValidator__check_brackets --> call_ValidationError
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator__check_math_delimiters
    core_validation_structural_validator_py_StructuralValidator__check_math_delimiters --> call_text_count
    core_validation_structural_validator_py_StructuralValidator__check_math_delimiters --> call_ValidationError
    core_validation_structural_validator_py_StructuralValidator__check_math_delimiters --> call_re_sub
    core_validation_structural_validator_py_StructuralValidator__check_math_delimiters --> call_temp_count
        core_validation_structural_validator_py_StructuralValidator --- core_validation_structural_validator_py_StructuralValidator__check_environments
    core_validation_structural_validator_py_StructuralValidator__check_environments --> call_re_finditer
    core_validation_structural_validator_py_StructuralValidator__check_environments --> call_match_groups
    core_validation_structural_validator_py_StructuralValidator__check_environments --> call_stack_append
    core_validation_structural_validator_py_StructuralValidator__check_environments --> call_ValidationError
    core_validation_structural_validator_py_StructuralValidator__check_environments --> call_stack_pop
        core_validation_volumetric_py_VolumetricValidator --- core_validation_volumetric_py_VolumetricValidator___init__
        core_validation_volumetric_py_VolumetricValidator --- core_validation_volumetric_py_VolumetricValidator_validate
    core_validation_volumetric_py_VolumetricValidator_validate --> call_len
    core_validation_volumetric_py_VolumetricValidator_validate --> call___strip
    core_validation_volumetric_py_VolumetricValidator_validate --> call_results_append
    core_validation_volumetric_py_VolumetricValidator_validate --> call_ValidationResult
        infra_adapters_pdf_parser_py_PdfParserAdapter --- infra_adapters_pdf_parser_py_PdfParserAdapter___init__
        infra_adapters_pdf_parser_py_PdfParserAdapter --- infra_adapters_pdf_parser_py_PdfParserAdapter_parse
    infra_adapters_pdf_parser_py_PdfParserAdapter_parse --> call_self__parser_callable
    infra_adapters_pdf_parser_py_PdfParserAdapter_parse --> call_RuntimeError
    infra_db_bootstrap_py_bootstrap_all_databases --> call_logger_info
    infra_db_bootstrap_py_bootstrap_all_databases --> call_BASE_DIR_mkdir
    infra_db_bootstrap_py_bootstrap_all_databases --> call_DB_CONFIGS_items
    infra_db_bootstrap_py_bootstrap_all_databases --> call___exists
    infra_db_bootstrap_py_bootstrap_all_databases --> call_logger_critical
    infra_db_bootstrap_py_bootstrap_all_databases --> call_sys_exit
    infra_db_bootstrap_py_bootstrap_all_databases --> call_open
    infra_db_bootstrap_py_bootstrap_all_databases --> call_f_read
    infra_db_bootstrap_py_bootstrap_all_databases --> call_get_connection
    infra_db_bootstrap_py_bootstrap_all_databases --> call_conn_execute
    infra_db_bootstrap_py_bootstrap_all_databases --> call_conn_executescript
    infra_db_bootstrap_py_bootstrap_all_databases --> call_conn_commit
    infra_db_bootstrap_py_bootstrap_all_databases --> call_conn_close
    infra_db_bootstrap_py_bootstrap_all_databases --> call_logger_error
    infra_db_connection_py__to_absolute_path --> call_os_getenv
    infra_db_connection_py__to_absolute_path --> call_Path
    infra_db_connection_py__to_absolute_path --> call_p_is_absolute
    infra_db_connection_py__to_absolute_path --> call_str
    infra_db_connection_py__to_absolute_path --> call_p_resolve
    infra_db_connection_py__attach_fsm_database --> call__to_absolute_path
    infra_db_connection_py__attach_fsm_database --> call___exists
    infra_db_connection_py__attach_fsm_database --> call___fetchall
    infra_db_connection_py__attach_fsm_database --> call_conn_execute
    infra_db_connection_py__attach_fsm_database --> call_any
    infra_db_connection_py__attach_fsm_database --> call_fsm_db_path_replace
    infra_db_connection_py__attach_fsm_database --> call_logger_debug
    infra_db_connection_py__attach_fsm_database --> call_logger_error
    infra_db_connection_py__attach_fsm_database --> call_conn_close
    infra_db_connection_py__attach_fsm_database --> call_logger_warning
    infra_db_connection_py_get_connection --> call_Path
    infra_db_connection_py_get_connection --> call_p_db_is_absolute
    infra_db_connection_py_get_connection --> call_str
    infra_db_connection_py_get_connection --> call_p_db_resolve
    infra_db_connection_py_get_connection --> call___resolve
    infra_db_connection_py_get_connection --> call_sqlite3_connect
    infra_db_connection_py_get_connection --> call_conn_execute
    infra_db_connection_py_get_connection --> call__to_absolute_path
    infra_db_connection_py_get_connection --> call__attach_fsm_database
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository___init__
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call___encode
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call___hexdigest
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call_hashlib_sha256
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call_tasks_append
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call___executemany
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_tasks --> call___commit
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_pick_task
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_int
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_uuid_uuid4
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_cursor_fetchone
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call___commit
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_TaskLease
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call_time_monotonic
    infra_db_control_repo_py_ControlPlaneRepository_pick_task --> call___rollback
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution
    infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution --> call___commit
    infra_db_control_repo_py_ControlPlaneRepository_acknowledge_execution --> call_OptimisticLockError
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_abandon_execution
    infra_db_control_repo_py_ControlPlaneRepository_abandon_execution --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_abandon_execution --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_abandon_execution --> call___commit
    infra_db_control_repo_py_ControlPlaneRepository_abandon_execution --> call_OptimisticLockError
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_renew_task_lease
    infra_db_control_repo_py_ControlPlaneRepository_renew_task_lease --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_renew_task_lease --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_renew_task_lease --> call___commit
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched
    infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched --> call___commit
    infra_db_control_repo_py_ControlPlaneRepository_release_task_untouched --> call_OptimisticLockError
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled
    infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled --> call___rollback
    infra_db_control_repo_py_ControlPlaneRepository_mark_cqrs_reconciled --> call___commit
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered
    infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered --> call___rollback
    infra_db_control_repo_py_ControlPlaneRepository_mark_zombie_recovered --> call___commit
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call_time_time
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call___commit
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call___rollback
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call_logger_info
    infra_db_control_repo_py_ControlPlaneRepository_enqueue_assembler_task --> call_logger_error
        infra_db_control_repo_py_ControlPlaneRepository --- infra_db_control_repo_py_ControlPlaneRepository_find_documents_with_pending_chunks
    infra_db_control_repo_py_ControlPlaneRepository_find_documents_with_pending_chunks --> call_os_getenv
    infra_db_control_repo_py_ControlPlaneRepository_find_documents_with_pending_chunks --> call___execute
    infra_db_control_repo_py_ControlPlaneRepository_find_documents_with_pending_chunks --> call_cursor_fetchall
        infra_db_document_repository_py_SQLiteDocumentRepository --- infra_db_document_repository_py_SQLiteDocumentRepository___init__
    infra_db_document_repository_py_SQLiteDocumentRepository___init__ --> call_self__ensure_schema
        infra_db_document_repository_py_SQLiteDocumentRepository --- infra_db_document_repository_py_SQLiteDocumentRepository__ensure_schema
    infra_db_document_repository_py_SQLiteDocumentRepository__ensure_schema --> call___executescript
        infra_db_document_repository_py_SQLiteDocumentRepository --- infra_db_document_repository_py_SQLiteDocumentRepository_save_batch
    infra_db_document_repository_py_SQLiteDocumentRepository_save_batch --> call___executemany
        infra_db_document_repository_py_SQLiteDocumentRepository --- infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call___cursor
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_cursor_execute
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_cursor_fetchone
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_PayloadNotFoundError
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_HashMismatchError
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call___hexdigest
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_hashlib_sha256
    infra_db_document_repository_py_SQLiteDocumentRepository_get_verified_payload --> call_payload_encode
        infra_db_event_repo_py_EventPlaneRepository --- infra_db_event_repo_py_EventPlaneRepository___init__
        infra_db_event_repo_py_EventPlaneRepository --- infra_db_event_repo_py_EventPlaneRepository_get_replay
    infra_db_event_repo_py_EventPlaneRepository_get_replay --> call___execute
    infra_db_event_repo_py_EventPlaneRepository_get_replay --> call_cursor_fetchone
    infra_db_event_repo_py_EventPlaneRepository_get_replay --> call_ReplayPayload
        infra_db_event_repo_py_EventPlaneRepository --- infra_db_event_repo_py_EventPlaneRepository_append_wal
    infra_db_event_repo_py_EventPlaneRepository_append_wal --> call___execute
    infra_db_event_repo_py_EventPlaneRepository_append_wal --> call_uuid_uuid4
    infra_db_event_repo_py_EventPlaneRepository_append_wal --> call_time_time
    infra_db_event_repo_py_EventPlaneRepository_append_wal --> call___commit
        infra_db_event_repo_py_EventPlaneRepository --- infra_db_event_repo_py_EventPlaneRepository_get_latest_event
    infra_db_event_repo_py_EventPlaneRepository_get_latest_event --> call___execute
    infra_db_event_repo_py_EventPlaneRepository_get_latest_event --> call_cursor_fetchone
    infra_db_event_repo_py_EventPlaneRepository_get_latest_event --> call_EventRecord
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository___init__
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_initialize_document
    infra_db_fsm_repository_py_FSMRepository_initialize_document --> call_time_time
    infra_db_fsm_repository_py_FSMRepository_initialize_document --> call___execute
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_transition_to
    infra_db_fsm_repository_py_FSMRepository_transition_to --> call_time_time
    infra_db_fsm_repository_py_FSMRepository_transition_to --> call___execute
    infra_db_fsm_repository_py_FSMRepository_transition_to --> call_logger_error
    infra_db_fsm_repository_py_FSMRepository_transition_to --> call_OptimisticLockError
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_get_status
    infra_db_fsm_repository_py_FSMRepository_get_status --> call___fetchone
    infra_db_fsm_repository_py_FSMRepository_get_status --> call___execute
    infra_db_fsm_repository_py_FSMRepository_get_status --> call_DocumentStatusDTO
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_find_stalled_documents
    infra_db_fsm_repository_py_FSMRepository_find_stalled_documents --> call_time_time
    infra_db_fsm_repository_py_FSMRepository_find_stalled_documents --> call___execute
    infra_db_fsm_repository_py_FSMRepository_find_stalled_documents --> call_cursor_fetchall
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_find_next_ready_for_assembly
    infra_db_fsm_repository_py_FSMRepository_find_next_ready_for_assembly --> call___execute
    infra_db_fsm_repository_py_FSMRepository_find_next_ready_for_assembly --> call_cursor_fetchone
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_is_document_already_processed
    infra_db_fsm_repository_py_FSMRepository_is_document_already_processed --> call___execute
    infra_db_fsm_repository_py_FSMRepository_is_document_already_processed --> call_cursor_fetchone
        infra_db_fsm_repository_py_FSMRepository --- infra_db_fsm_repository_py_FSMRepository_get_by_document_id
    infra_db_fsm_repository_py_FSMRepository_get_by_document_id --> call___fetchone
    infra_db_fsm_repository_py_FSMRepository_get_by_document_id --> call___execute
    infra_db_fsm_repository_py_FSMRepository_get_by_document_id --> call_DocumentStatusDTO
        infra_db_materialized_repo_py_MaterializedPlaneRepository --- infra_db_materialized_repo_py_MaterializedPlaneRepository___init__
        infra_db_materialized_repo_py_MaterializedPlaneRepository --- infra_db_materialized_repo_py_MaterializedPlaneRepository_get_projection_status
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_projection_status --> call___execute
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_projection_status --> call_cursor_fetchone
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_projection_status --> call_ProjectionStatus
        infra_db_materialized_repo_py_MaterializedPlaneRepository --- infra_db_materialized_repo_py_MaterializedPlaneRepository_upsert_projection
    infra_db_materialized_repo_py_MaterializedPlaneRepository_upsert_projection --> call___execute
    infra_db_materialized_repo_py_MaterializedPlaneRepository_upsert_projection --> call_time_time
    infra_db_materialized_repo_py_MaterializedPlaneRepository_upsert_projection --> call___commit
        infra_db_materialized_repo_py_MaterializedPlaneRepository --- infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks --> call___join
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks --> call_len
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks --> call___execute
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks --> call_ProjectionRecord
    infra_db_materialized_repo_py_MaterializedPlaneRepository_get_assemblable_chunks --> call_cursor_fetchall
        infra_db_system_repo_py_SystemPlaneRepository --- infra_db_system_repo_py_SystemPlaneRepository___init__
        infra_db_system_repo_py_SystemPlaneRepository --- infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership
    infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership --> call_time_time
    infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership --> call___execute
    infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership --> call_cursor_fetchone
    infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership --> call___commit
    infra_db_system_repo_py_SystemPlaneRepository_acquire_leadership --> call___rollback
        infra_db_system_repo_py_SystemPlaneRepository --- infra_db_system_repo_py_SystemPlaneRepository_renew_leadership
    infra_db_system_repo_py_SystemPlaneRepository_renew_leadership --> call_time_time
    infra_db_system_repo_py_SystemPlaneRepository_renew_leadership --> call___execute
    infra_db_system_repo_py_SystemPlaneRepository_renew_leadership --> call___commit
        infra_db_system_repo_py_SystemPlaneRepository --- infra_db_system_repo_py_SystemPlaneRepository_release_leadership
    infra_db_system_repo_py_SystemPlaneRepository_release_leadership --> call_time_time
    infra_db_system_repo_py_SystemPlaneRepository_release_leadership --> call___execute
    infra_db_system_repo_py_SystemPlaneRepository_release_leadership --> call___commit
        infra_db_system_repo_py_SystemPlaneRepository --- infra_db_system_repo_py_SystemPlaneRepository_get_current_epoch
    infra_db_system_repo_py_SystemPlaneRepository_get_current_epoch --> call___execute
    infra_db_system_repo_py_SystemPlaneRepository_get_current_epoch --> call_cursor_fetchone
        runtime_reconciliation_py_CQRSReconciliationDaemon --- runtime_reconciliation_py_CQRSReconciliationDaemon___init__
    runtime_reconciliation_py_CQRSReconciliationDaemon___init__ --> call_Metrics
        runtime_reconciliation_py_CQRSReconciliationDaemon --- runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_logger_info
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_get_connection
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_ControlPlaneRepository
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_EventPlaneRepository
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_MaterializedPlaneRepository
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_SystemPlaneRepository
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_ReconciliationCommandHandler
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_system_repo_get_current_epoch
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_task_repo_find_documents_with_pending_chunks
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_q_conn_execute
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_time_time
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_cursor_fetchall
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_logger_warning
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_RecoverZombieTaskCommand
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_time_time_ns
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_handler_handle
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_q_conn_commit
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_logger_error
    runtime_reconciliation_py_CQRSReconciliationDaemon_run_reconciliation_cycle --> call_str
        runtime_recovery_py_AbandonedProcessWatchdog --- runtime_recovery_py_AbandonedProcessWatchdog___init__
        runtime_recovery_py_AbandonedProcessWatchdog --- runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_get_connection
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_FSMRepository
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_DocumentCommandHandler
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_fsm_repo_find_stalled_documents
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_fsm_repo_get_status
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_logger_warning
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_StallDocumentCommand
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_cmd_handler_handle
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_conn_commit
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_logger_info
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_logger_error
    runtime_recovery_py_AbandonedProcessWatchdog_execute_sweep --> call_str
        runtime_resumer_py_OnDemandResumeManager --- runtime_resumer_py_OnDemandResumeManager___init__
        runtime_resumer_py_OnDemandResumeManager --- runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_get_connection
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_FSMRepository
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_DocumentCommandHandler
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_fsm_repo_get_status
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_logger_error
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_logger_info
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_logger_critical
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_ResumeDocumentCommand
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_cmd_handler_handle
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_conn_commit
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_logger_warning
    runtime_resumer_py_OnDemandResumeManager_rescue_stalled_document --> call_str
        runtime_sweeper_py_RecoveryDaemon --- runtime_sweeper_py_RecoveryDaemon___init__
        runtime_sweeper_py_RecoveryDaemon --- runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint
    runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint --> call_get_connection
    runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint --> call_conn_execute
    runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint --> call_cursor_fetchone
    runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint --> call_logger_warning
    runtime_sweeper_py_RecoveryDaemon__force_wal_checkpoint --> call_logger_error
        runtime_sweeper_py_RecoveryDaemon --- runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_self__force_wal_checkpoint
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_get_connection
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_conn_fsm_execute
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_conn_queue_execute
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_FSMRepository
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_ControlPlaneRepository
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_DocumentCommandHandler
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_fsm_repo_find_stalled_documents
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_logger_warning
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_fsm_repo_get_status
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_FailDocumentCommand
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_cmd_handler_handle
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_logger_info
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_logger_error
    runtime_sweeper_py_RecoveryDaemon_run_sweep_cycle --> call_c_close
    classDef classStyle fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef funcStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:1px,color:#ddd;
    classDef callStyle fill:#111827,stroke:#374151,stroke-width:1px,color:#9ca3af,stroke-dasharray: 3 3;
```