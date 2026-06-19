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
    call_DocumentAssembler["--> DocumentAssembler()"]:::callStyle
    call_SummaryBuilder["--> SummaryBuilder()"]:::callStyle
    call__build_default_validation_pipeline["--> _build_default_validation_pipeline()"]:::callStyle
    call_HealingPolicy["--> HealingPolicy()"]:::callStyle
    call_MarkdownLeakageHealingStrategy["--> MarkdownLeakageHealingStrategy()"]:::callStyle
    call_MetaTextLeakageHealingStrategy["--> MetaTextLeakageHealingStrategy()"]:::callStyle
    call_EOFBraceClosureStrategy["--> EOFBraceClosureStrategy()"]:::callStyle
    call_EOFMathClosureStrategy["--> EOFMathClosureStrategy()"]:::callStyle
    call_HealingPipeline["--> HealingPipeline()"]:::callStyle
    call_get_connection["--> get_connection()"]:::callStyle
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
        apps_llm_workers_prompt_builder_py_PromptBuilder["[CLASS] PromptBuilder"]:::classStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder___init__["__init__()"]:::funcStyle
        apps_llm_workers_prompt_builder_py_PromptBuilder_build["build()"]:::funcStyle
    call___hexdigest["--> *.hexdigest()"]:::callStyle
    call_hashlib_sha256["--> hashlib.sha256()"]:::callStyle
    call_hash_input_encode["--> hash_input.encode()"]:::callStyle
    call___estimate["--> *.estimate()"]:::callStyle
    call_PromptEnvelope["--> PromptEnvelope()"]:::callStyle

    subgraph apps_llm_workers_rate_limiter_py ["?? apps/llm_workers/rate_limiter.py"]
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
        core_ast_models_py_TranslationUnit["[CLASS] TranslationUnit"]:::classStyle
        core_ast_models_py_ChunkingReport["[CLASS] ChunkingReport"]:::classStyle
        core_ast_models_py_TranslatedUnit["[CLASS] TranslatedUnit"]:::classStyle
        core_ast_models_py_ReconstructedDocument["[CLASS] ReconstructedDocument"]:::classStyle

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
    call_cls["--> cls()"]:::callStyle
        core_ast_validator_py_ASTHealthReport___str__["__str__()"]:::funcStyle
        core_ast_validator_py_ASTValidator["[CLASS] ASTValidator"]:::classStyle
        core_ast_validator_py_ASTValidator_validate["validate()"]:::funcStyle
    call_ASTValidationError["--> ASTValidationError()"]:::callStyle
    call_set["--> set()"]:::callStyle
    call_seen_ids_add["--> seen_ids.add()"]:::callStyle
    call_LATEX_MATH_OPEN_search["--> LATEX_MATH_OPEN.search()"]:::callStyle
    call_LATEX_MATH_CLOSE_search["--> LATEX_MATH_CLOSE.search()"]:::callStyle

    subgraph core_ast___init___py ["?? core/ast/__init__.py"]

    subgraph core_compiler_assembler_py ["?? core/compiler/assembler.py"]
        core_compiler_assembler_py_DocumentAssembler["[CLASS] DocumentAssembler"]:::classStyle
        core_compiler_assembler_py_DocumentAssembler___init__["__init__()"]:::funcStyle
        core_compiler_assembler_py_DocumentAssembler__validate_sequence["_validate_sequence()"]:::funcStyle
    call_IncompleteDocumentError["--> IncompleteDocumentError()"]:::callStyle
        core_compiler_assembler_py_DocumentAssembler_assemble["assemble()"]:::funcStyle
    call_ReconstructedDocument["--> ReconstructedDocument()"]:::callStyle
    call_self__validate_sequence["--> self._validate_sequence()"]:::callStyle

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
    call_replace["--> replace()"]:::callStyle
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
    call_dict["--> dict()"]:::callStyle

    subgraph core_metrics_pricing_py ["?? core/metrics/pricing.py"]
        core_metrics_pricing_py_PricingEngine["[CLASS] PricingEngine"]:::classStyle
        core_metrics_pricing_py_PricingEngine_calculate_cost["calculate_cost()"]:::funcStyle
    call_model_name_startswith["--> model_name.startswith()"]:::callStyle

    subgraph core_metrics_summary_py ["?? core/metrics/summary.py"]
        core_metrics_summary_py_TranslationAuditSummary["[CLASS] TranslationAuditSummary"]:::classStyle
        core_metrics_summary_py_SummaryBuilder["[CLASS] SummaryBuilder"]:::classStyle
        core_metrics_summary_py_SummaryBuilder_build["build()"]:::funcStyle
    call_PricingEngine_calculate_cost["--> PricingEngine.calculate_cost()"]:::callStyle
    call_TranslationAuditSummary["--> TranslationAuditSummary()"]:::callStyle

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
    call_logger_debug["--> logger.debug()"]:::callStyle
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
    call___upper["--> *.upper()"]:::callStyle
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

    subgraph core_utils_config_py ["?? core/utils/config.py"]

    subgraph core_utils_fs_py ["?? core/utils/fs.py"]
        core_utils_fs_py_ensure_parent_dir["[FUNC] ensure_parent_dir()"]:::funcStyle
    call___mkdir["--> *.mkdir()"]:::callStyle

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

    subgraph core_validation_error_taxonomy_py ["?? core/validation/error_taxonomy.py"]

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
    call_Counter["--> Counter()"]:::callStyle
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

    subgraph graveyard_gemini_client_py ["?? graveyard/gemini_client.py"]
        graveyard_gemini_client_py_GeminiClient["[CLASS] GeminiClient"]:::classStyle
        graveyard_gemini_client_py_GeminiClient___init__["__init__()"]:::funcStyle
    call_CircuitBreakerRegistry_get_breaker["--> CircuitBreakerRegistry.get_breaker()"]:::callStyle
    call_requests_Session["--> requests.Session()"]:::callStyle
        graveyard_gemini_client_py_GeminiClient__clean_response["_clean_response()"]:::funcStyle
    call_result_startswith["--> result.startswith()"]:::callStyle
    call_result_endswith["--> result.endswith()"]:::callStyle
    call_result_strip["--> result.strip()"]:::callStyle
        graveyard_gemini_client_py_GeminiClient__build_fix_prompt["_build_fix_prompt()"]:::funcStyle
        graveyard_gemini_client_py_GeminiClient__is_transient["_is_transient()"]:::funcStyle
        graveyard_gemini_client_py_GeminiClient__execute_with_local_retries["_execute_with_local_retries()"]:::funcStyle
    call___check_state["--> *.check_state()"]:::callStyle
    call___acquire["--> *.acquire()"]:::callStyle
    call___post["--> *.post()"]:::callStyle
    call_self__is_transient["--> self._is_transient()"]:::callStyle
    call_TransientAPIError["--> TransientAPIError()"]:::callStyle
    call_response_raise_for_status["--> response.raise_for_status()"]:::callStyle
    call_response_json["--> response.json()"]:::callStyle
    call_self__clean_response["--> self._clean_response()"]:::callStyle
    call___release["--> *.release()"]:::callStyle
    call_retry["--> retry()"]:::callStyle
    call_wait_exponential["--> wait_exponential()"]:::callStyle
    call_stop_after_attempt["--> stop_after_attempt()"]:::callStyle
    call_retry_if_exception_type["--> retry_if_exception_type()"]:::callStyle
        graveyard_gemini_client_py_GeminiClient_translate["translate()"]:::funcStyle
    call_PromptBuilder["--> PromptBuilder()"]:::callStyle
    call_builder_build["--> builder.build()"]:::callStyle
    call___call["--> *.call()"]:::callStyle
    call_self__execute_with_local_retries["--> self._execute_with_local_retries()"]:::callStyle
        graveyard_gemini_client_py_GeminiClient_fix_latex["fix_latex()"]:::funcStyle
    call_self__build_fix_prompt["--> self._build_fix_prompt()"]:::callStyle
        graveyard_gemini_client_py_GeminiClient_generate["generate()"]:::funcStyle
        graveyard_gemini_client_py_GeminiClient__embed_with_local_retries["_embed_with_local_retries()"]:::funcStyle
        graveyard_gemini_client_py_GeminiClient_embed_text["embed_text()"]:::funcStyle
    call_self__embed_with_local_retries["--> self._embed_with_local_retries()"]:::callStyle

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

    subgraph tests_test_architecture_contract_py ["?? tests/test_architecture_contract.py"]
        tests_test_architecture_contract_py_test_ports_compliance["[FUNC] test_ports_compliance()"]:::funcStyle

    subgraph tests_test_ast_py ["?? tests/test_ast.py"]

    subgraph tests_test_dag_py ["?? tests/test_dag.py"]

    subgraph tests_test_fencing_py ["?? tests/test_fencing.py"]

    subgraph tests_test_math_protector_py ["?? tests/test_math_protector.py"]
        tests_test_math_protector_py_test_inline_math_protector["[FUNC] test_inline_math_protector()"]:::funcStyle
    call_InlineMathProtector_mask["--> InlineMathProtector.mask()"]:::callStyle
    call_masked_replace["--> masked.replace()"]:::callStyle
    call_InlineMathProtector_restore["--> InlineMathProtector.restore()"]:::callStyle

    subgraph tests_test_pipeline_py ["?? tests/test_pipeline.py"]
        tests_test_pipeline_py_run_stress_tests["[FUNC] run_stress_tests()"]:::funcStyle
    call_CORPUS_DIR_mkdir["--> CORPUS_DIR.mkdir()"]:::callStyle
    call_OUTPUT_DIR_mkdir["--> OUTPUT_DIR.mkdir()"]:::callStyle
    call_CORPUS_DIR_glob["--> CORPUS_DIR.glob()"]:::callStyle
    call_run_pipeline["--> run_pipeline()"]:::callStyle
    call_metrics_get["--> metrics.get()"]:::callStyle

    subgraph tests_test_pipeline_fidelity_py ["?? tests/test_pipeline_fidelity.py"]
        tests_test_pipeline_fidelity_py_TestPipelineFidelity["[CLASS] TestPipelineFidelity"]:::classStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_html_sanitization_variants["test_html_sanitization_variants()"]:::funcStyle
    call_self_assertEqual["--> self.assertEqual()"]:::callStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations["test_semantic_adjacency_and_mutations()"]:::funcStyle
    call_restored_lower["--> restored.lower()"]:::callStyle
    call_self_assertTrue["--> self.assertTrue()"]:::callStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math["test_mixed_inline_and_block_math()"]:::funcStyle
    call_self_assertIn["--> self.assertIn()"]:::callStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser["_execute_mock_parser()"]:::funcStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_safe_exists["safe_exists()"]:::funcStyle
    call_path_endswith["--> path.endswith()"]:::callStyle
    call_patch["--> patch()"]:::callStyle
    call_t_split["--> t.split()"]:::callStyle
    call_mock_open["--> mock_open()"]:::callStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_quarantine_quarantine["test_equation_quarantine_quarantine()"]:::funcStyle
    call_self__execute_mock_parser["--> self._execute_mock_parser()"]:::callStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation["test_mixed_image_block_continuation()"]:::funcStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_ratio_and_false_positives["test_equation_ratio_and_false_positives()"]:::funcStyle
        tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_worker_passthrough_alignment["test_worker_passthrough_alignment()"]:::funcStyle

    subgraph tests_helpers_bootstrap_translation_golden_py ["?? tests/helpers/bootstrap_translation_golden.py"]

    subgraph tests_helpers_fakes_py ["?? tests/helpers/fakes.py"]
        tests_helpers_fakes_py_FakeChunker["[CLASS] FakeChunker"]:::classStyle
        tests_helpers_fakes_py_FakeChunker_chunk["chunk()"]:::funcStyle
        tests_helpers_fakes_py_FakeDispatcher["[CLASS] FakeDispatcher"]:::classStyle

    subgraph tests_helpers_markdown_inspector_py ["?? tests/helpers/markdown_inspector.py"]
        tests_helpers_markdown_inspector_py_MarkdownInspector["[CLASS] MarkdownInspector"]:::classStyle
        tests_helpers_markdown_inspector_py_MarkdownInspector_extract_structure["extract_structure()"]:::funcStyle
        tests_helpers_markdown_inspector_py_MarkdownInspector_extract_technical_tokens["extract_technical_tokens()"]:::funcStyle
        tests_helpers_markdown_inspector_py_MarkdownInspector_verify_balances["verify_balances()"]:::funcStyle
    call_content_count["--> content.count()"]:::callStyle

    subgraph tests_helpers___init___py ["?? tests/helpers/__init__.py"]

    subgraph tests_integration_test_chunker_snapshot_py ["?? tests/integration/test_chunker_snapshot.py"]
        tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot["[CLASS] TestChunkerSnapshot"]:::classStyle
        tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_setUp["setUp()"]:::funcStyle
        tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification["test_snapshot_verification()"]:::funcStyle
    call_self_skipTest["--> self.skipTest()"]:::callStyle
    call_StructuralNodeType["--> StructuralNodeType()"]:::callStyle
    call_ContentNodeType["--> ContentNodeType()"]:::callStyle
    call_d_get["--> d.get()"]:::callStyle
    call_zip["--> zip()"]:::callStyle

    subgraph tests_integration_test_cli_router_py ["?? tests/integration/test_cli_router.py"]
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse["[CLASS] TestCLIRoutingAndArgparse"]:::classStyle
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing["test_translate_subcommand_routing()"]:::funcStyle
    call_argparse_Namespace["--> argparse.Namespace()"]:::callStyle
    call_main["--> main()"]:::callStyle
    call_mock_handle_assert_called_once_with["--> mock_handle.assert_called_once_with()"]:::callStyle
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing["test_resume_subcommand_routing()"]:::funcStyle
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing["test_sweep_subcommand_routing()"]:::funcStyle
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing["test_status_subcommand_routing()"]:::funcStyle

    subgraph tests_integration_test_e2e_walking_skeleton_py ["?? tests/integration/test_e2e_walking_skeleton.py"]
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E["[CLASS] TestTrueWalkingSkeletonE2E"]:::classStyle
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp["setUp()"]:::funcStyle
    call_BypassProvider["--> BypassProvider()"]:::callStyle
    call_ResilientProvider["--> ResilientProvider()"]:::callStyle
    call_QuotaManager["--> QuotaManager()"]:::callStyle
    call_RateLimitedProvider["--> RateLimitedProvider()"]:::callStyle
    call_CachedLLMProvider["--> CachedLLMProvider()"]:::callStyle
    call___initialize["--> *.initialize()"]:::callStyle
    call_MagicMock["--> MagicMock()"]:::callStyle
    call_AsyncDispatcher["--> AsyncDispatcher()"]:::callStyle
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_tearDown["tearDown()"]:::funcStyle
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units["_bridge_ast_to_units()"]:::funcStyle
    call_node_get["--> node.get()"]:::callStyle
    call_payload_strip["--> payload.strip()"]:::callStyle
    call_payload_encode["--> payload.encode()"]:::callStyle

    subgraph tests_integration_test_embedding_smoke_py ["?? tests/integration/test_embedding_smoke.py"]
        tests_integration_test_embedding_smoke_py_TestProviderSmoke["[CLASS] TestProviderSmoke"]:::classStyle

    subgraph tests_integration_test_golden_parser_py ["?? tests/integration/test_golden_parser.py"]
        tests_integration_test_golden_parser_py_TestGoldenParser["[CLASS] TestGoldenParser"]:::classStyle
        tests_integration_test_golden_parser_py_TestGoldenParser_setUp["setUp()"]:::funcStyle
        tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint["_generate_fingerprint()"]:::funcStyle
    call_distribution_get["--> distribution.get()"]:::callStyle
    call_sequence_append["--> sequence.append()"]:::callStyle
    call_content_str_strip["--> content_str.strip()"]:::callStyle
        tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint["test_parser_runtime_matches_golden_fingerprint()"]:::funcStyle
    call___parse["--> *.parse()"]:::callStyle
    call_self__generate_fingerprint["--> self._generate_fingerprint()"]:::callStyle
    call_abs["--> abs()"]:::callStyle
    call_self_assertLessEqual["--> self.assertLessEqual()"]:::callStyle

    subgraph tests_integration_test_healing_concurrency_py ["?? tests/integration/test_healing_concurrency.py"]
        tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency["[FUNC] test_telemetry_registry_async_concurrency()"]:::funcStyle
    call_registry_record["--> registry.record()"]:::callStyle
    call_asyncio_sleep["--> asyncio.sleep()"]:::callStyle
    call__async_worker["--> _async_worker()"]:::callStyle
    call__main_orchestrator["--> _main_orchestrator()"]:::callStyle
    call_registry_get_events["--> registry.get_events()"]:::callStyle
    call_registry_get_aggregate_metrics["--> registry.get_aggregate_metrics()"]:::callStyle
        tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline["[CLASS] ContextDrivenMockValidationPipeline"]:::classStyle
        tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline___init__["__init__()"]:::funcStyle
        tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline_validate_chunk["validate_chunk()"]:::funcStyle
        tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback["[FUNC] test_healing_pipeline_emits_full_audit_on_rollback()"]:::funcStyle
    call_ContextDrivenMockValidationPipeline["--> ContextDrivenMockValidationPipeline()"]:::callStyle
    call_pipeline_heal_and_revalidate["--> pipeline.heal_and_revalidate()"]:::callStyle

    subgraph tests_integration_test_healing_e2e_telemetry_py ["?? tests/integration/test_healing_e2e_telemetry.py"]
        tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline["[CLASS] MockValidationPipeline"]:::classStyle
        tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline___init__["__init__()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline_validate_chunk["validate_chunk()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_build_pipeline_and_registry["[FUNC] build_pipeline_and_registry()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py__builder["[FUNC] _builder()"]:::funcStyle
    call_MockValidationPipeline["--> MockValidationPipeline()"]:::callStyle
        tests_integration_test_healing_e2e_telemetry_py__make_ctx["[FUNC] _make_ctx()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_a_markdown_leakage["[FUNC] test_e2e_case_a_markdown_leakage()"]:::funcStyle
    call_build_pipeline_and_registry["--> build_pipeline_and_registry()"]:::callStyle
    call__make_ctx["--> _make_ctx()"]:::callStyle
        tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_b_unbalanced_braces["[FUNC] test_e2e_case_b_unbalanced_braces()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_c_math_truncation["[FUNC] test_e2e_case_c_math_truncation()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_test_e2e_rollback_guarantee_on_revalidation_failure["[FUNC] test_e2e_rollback_guarantee_on_revalidation_failure()"]:::funcStyle
        tests_integration_test_healing_e2e_telemetry_py_test_e2e_telemetry_aggregate_metrics["[FUNC] test_e2e_telemetry_aggregate_metrics()"]:::funcStyle

    subgraph tests_integration_test_pipeline_orchestration_py ["?? tests/integration/test_pipeline_orchestration.py"]
        tests_integration_test_pipeline_orchestration_py_FakeChunker["[CLASS] FakeChunker"]:::classStyle
        tests_integration_test_pipeline_orchestration_py_FakeChunker_chunk["chunk()"]:::funcStyle
        tests_integration_test_pipeline_orchestration_py_FakeDispatcher["[CLASS] FakeDispatcher"]:::classStyle
        tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration["[CLASS] TestPipelineOrchestration"]:::classStyle
        tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp["setUp()"]:::funcStyle
    call_build_pipeline["--> build_pipeline()"]:::callStyle
    call_FakeChunker["--> FakeChunker()"]:::callStyle
    call_FakeDispatcher["--> FakeDispatcher()"]:::callStyle

    subgraph tests_integration_test_real_e2e_py ["?? tests/integration/test_real_e2e.py"]
        tests_integration_test_real_e2e_py_FinOpsControlledChunker["[CLASS] FinOpsControlledChunker"]:::classStyle
        tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk["chunk()"]:::funcStyle
        tests_integration_test_real_e2e_py_TestRealE2EFinOps["[CLASS] TestRealE2EFinOps"]:::classStyle
        tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp["setUp()"]:::funcStyle
    call_SyncProviderBridge["--> SyncProviderBridge()"]:::callStyle
    call_FinOpsControlledChunker["--> FinOpsControlledChunker()"]:::callStyle
    call_fsm_db_execute["--> fsm_db.execute()"]:::callStyle
    call_fsm_db_commit["--> fsm_db.commit()"]:::callStyle
        tests_integration_test_real_e2e_py_TestRealE2EFinOps_tearDown["tearDown()"]:::funcStyle
    call___shutdown["--> *.shutdown()"]:::callStyle

    subgraph tests_integration_test_real_paper_py ["?? tests/integration/test_real_paper.py"]
        tests_integration_test_real_paper_py_TestRealPaperIntegration["[CLASS] TestRealPaperIntegration"]:::classStyle
        tests_integration_test_real_paper_py_TestRealPaperIntegration_setUp["setUp()"]:::funcStyle
        tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local["test_parser_and_validation_e2e_local()"]:::funcStyle
    call_ASTHealthReport_from_ast["--> ASTHealthReport.from_ast()"]:::callStyle
    call_ASTValidator_validate["--> ASTValidator.validate()"]:::callStyle
    call_self_assertGreater["--> self.assertGreater()"]:::callStyle
    call_self_fail["--> self.fail()"]:::callStyle

    subgraph tests_integration_test_real_parser_pipeline_py ["?? tests/integration/test_real_parser_pipeline.py"]
        tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation["[CLASS] TestRealParserIsolation"]:::classStyle
        tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_setUp["setUp()"]:::funcStyle
        tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence["test_parser_adapter_extracts_and_verifies_structural_presence()"]:::funcStyle
    call_self_assertIsInstance["--> self.assertIsInstance()"]:::callStyle
    call_self_assertIsNotNone["--> self.assertIsNotNone()"]:::callStyle

    subgraph tests_integration_test_recovery_flow_py ["?? tests/integration/test_recovery_flow.py"]
        tests_integration_test_recovery_flow_py_MockComponent["[CLASS] MockComponent"]:::classStyle
        tests_integration_test_recovery_flow_py_MockComponent_parse["parse()"]:::funcStyle
        tests_integration_test_recovery_flow_py_MockComponent_chunk["chunk()"]:::funcStyle
        tests_integration_test_recovery_flow_py_MockComponent_assemble["assemble()"]:::funcStyle
        tests_integration_test_recovery_flow_py_MockComponent_build["build()"]:::funcStyle
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd["[CLASS] TestRecoveryAndResumeEndToEnd"]:::classStyle
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass["setUpClass()"]:::funcStyle
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle["test_complete_crash_recovery_and_resume_lifecycle()"]:::funcStyle
    call_MockComponent["--> MockComponent()"]:::callStyle
    call_TranslationJob["--> TranslationJob()"]:::callStyle
    call_pipeline_execute["--> pipeline.execute()"]:::callStyle
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_tearDownClass["tearDownClass()"]:::funcStyle

    subgraph tests_integration_test_translation_layer_py ["?? tests/integration/test_translation_layer.py"]
        tests_integration_test_translation_layer_py_TestTranslationLayerIntegration["[CLASS] TestTranslationLayerIntegration"]:::classStyle
        tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp["setUp()"]:::funcStyle
        tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_tearDown["tearDown()"]:::funcStyle

    subgraph tests_integration_test_translation_semantics_py ["?? tests/integration/test_translation_semantics.py"]
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression["[CLASS] TestSemanticChunkRegression"]:::classStyle
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp["setUp()"]:::funcStyle
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_tearDown["tearDown()"]:::funcStyle
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity["_calculate_cosine_similarity()"]:::funcStyle
    call_math_sqrt["--> math.sqrt()"]:::callStyle

    subgraph tests_integration_test_translation_structure_py ["?? tests/integration/test_translation_structure.py"]
        tests_integration_test_translation_structure_py_TestTranslationStructure["[CLASS] TestTranslationStructure"]:::classStyle
        tests_integration_test_translation_structure_py_TestTranslationStructure_setUp["setUp()"]:::funcStyle

    subgraph tests_integration_test_translation_technical_py ["?? tests/integration/test_translation_technical.py"]
        tests_integration_test_translation_technical_py_TestTranslationTechnical["[CLASS] TestTranslationTechnical"]:::classStyle
        tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp["setUp()"]:::funcStyle

    subgraph tests_integration_test_validation_integration_py ["?? tests/integration/test_validation_integration.py"]
        tests_integration_test_validation_integration_py_StaticMockProvider["[CLASS] StaticMockProvider"]:::classStyle
        tests_integration_test_validation_integration_py_StaticMockProvider___init__["__init__()"]:::funcStyle
        tests_integration_test_validation_integration_py_SequenceMockProvider["[CLASS] SequenceMockProvider"]:::classStyle
        tests_integration_test_validation_integration_py_SequenceMockProvider___init__["__init__()"]:::funcStyle
        tests_integration_test_validation_integration_py_build_test_dispatcher["[FUNC] build_test_dispatcher()"]:::funcStyle

    subgraph tests_integration___init___py ["?? tests/integration/__init__.py"]

    subgraph tests_smoke_conftest_py ["?? tests/smoke/conftest.py"]
        tests_smoke_conftest_py_reliability_pipeline["[FUNC] reliability_pipeline()"]:::funcStyle

    subgraph tests_smoke_test_invariants_smoke_py ["?? tests/smoke/test_invariants_smoke.py"]
        tests_smoke_test_invariants_smoke_py_run_chunk_validation["[FUNC] run_chunk_validation()"]:::funcStyle
    call_pipeline_validate_chunk["--> pipeline.validate_chunk()"]:::callStyle
        tests_smoke_test_invariants_smoke_py_run_doc_validation["[FUNC] run_doc_validation()"]:::funcStyle
    call_pipeline_validate_document["--> pipeline.validate_document()"]:::callStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_si01_unclosed_brace["[FUNC] test_smoke_si01_unclosed_brace()"]:::funcStyle
    call_run_chunk_validation["--> run_chunk_validation()"]:::callStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_si02_unbalanced_math["[FUNC] test_smoke_si02_unbalanced_math()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_si03_unclosed_environment["[FUNC] test_smoke_si03_unclosed_environment()"]:::funcStyle
    call_run_doc_validation["--> run_doc_validation()"]:::callStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pi01_doi_alteration["[FUNC] test_smoke_pi01_doi_alteration()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pi02_url_domain_alteration["[FUNC] test_smoke_pi02_url_domain_alteration()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pi03_orcid_lost["[FUNC] test_smoke_pi03_orcid_lost()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pi04_cross_reference_lost["[FUNC] test_smoke_pi04_cross_reference_lost()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pei01_markdown_block["[FUNC] test_smoke_pei01_markdown_block()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_pei02_conversational_leak["[FUNC] test_smoke_pei02_conversational_leak()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_sei01_missing_number["[FUNC] test_smoke_sei01_missing_number()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_sei02_unit_mutation["[FUNC] test_smoke_sei02_unit_mutation()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_contraction["[FUNC] test_smoke_vi01_ratio_contraction()"]:::funcStyle
        tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_expansion["[FUNC] test_smoke_vi01_ratio_expansion()"]:::funcStyle

    subgraph tests_unit_test_adapters_py ["?? tests/unit/test_adapters.py"]
        tests_unit_test_adapters_py__make_envelope["[FUNC] _make_envelope()"]:::funcStyle

    subgraph tests_unit_test_assembler_py ["?? tests/unit/test_assembler.py"]
        tests_unit_test_assembler_py_TestDocumentAssembler["[CLASS] TestDocumentAssembler"]:::classStyle
        tests_unit_test_assembler_py_TestDocumentAssembler_setUp["setUp()"]:::funcStyle
        tests_unit_test_assembler_py_TestDocumentAssembler__mock_unit["_mock_unit()"]:::funcStyle
    call_TranslatedUnit["--> TranslatedUnit()"]:::callStyle
        tests_unit_test_assembler_py_TestDocumentAssembler_test_successful_assembly_and_token_telemetry["test_successful_assembly_and_token_telemetry()"]:::funcStyle
    call_self__mock_unit["--> self._mock_unit()"]:::callStyle
    call___assemble["--> *.assemble()"]:::callStyle
        tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error["test_missing_chunk_raises_incomplete_error()"]:::funcStyle
    call_self_assertRaises["--> self.assertRaises()"]:::callStyle
        tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error["test_duplicate_chunk_raises_value_error()"]:::funcStyle

    subgraph tests_unit_test_asset_placeholder_py ["?? tests/unit/test_asset_placeholder.py"]
        tests_unit_test_asset_placeholder_py_fixer["[FUNC] fixer()"]:::funcStyle
    call_StructuralAssetPlaceholder["--> StructuralAssetPlaceholder()"]:::callStyle
        tests_unit_test_asset_placeholder_py_test_canonical_placeholder_generation["[FUNC] test_canonical_placeholder_generation()"]:::funcStyle
    call_fixer_normalize["--> fixer.normalize()"]:::callStyle
        tests_unit_test_asset_placeholder_py_test_empty_content_passthrough["[FUNC] test_empty_content_passthrough()"]:::funcStyle

    subgraph tests_unit_test_ast_integrity_py ["?? tests/unit/test_ast_integrity.py"]
        tests_unit_test_ast_integrity_py_validator["[FUNC] validator()"]:::funcStyle
    call_ASTIntegrityValidator["--> ASTIntegrityValidator()"]:::callStyle
        tests_unit_test_ast_integrity_py_test_empty_ast_triggers_warning_only["[FUNC] test_empty_ast_triggers_warning_only()"]:::funcStyle
    call_validator_validate_ast["--> validator.validate_ast()"]:::callStyle
        tests_unit_test_ast_integrity_py_test_duplicate_node_id_collision["[FUNC] test_duplicate_node_id_collision()"]:::funcStyle
        tests_unit_test_ast_integrity_py_test_malformed_placeholder_syntax["[FUNC] test_malformed_placeholder_syntax()"]:::funcStyle
        tests_unit_test_ast_integrity_py_test_orphan_list_item_emits_info_only["[FUNC] test_orphan_list_item_emits_info_only()"]:::funcStyle

    subgraph tests_unit_test_cache_provider_py ["?? tests/unit/test_cache_provider.py"]
        tests_unit_test_cache_provider_py_MockLowLevelProvider["[CLASS] MockLowLevelProvider"]:::classStyle
        tests_unit_test_cache_provider_py_MockLowLevelProvider___init__["__init__()"]:::funcStyle
        tests_unit_test_cache_provider_py_temp_db_path["[FUNC] temp_db_path()"]:::funcStyle
    call_os_close["--> os.close()"]:::callStyle

    subgraph tests_unit_test_context_enricher_py ["?? tests/unit/test_context_enricher.py"]
        tests_unit_test_context_enricher_py_enricher["[FUNC] enricher()"]:::funcStyle
    call_HierarchicalContextEnricher["--> HierarchicalContextEnricher()"]:::callStyle
        tests_unit_test_context_enricher_py_test_homonym_section_isolation["[FUNC] test_homonym_section_isolation()"]:::funcStyle
    call_enricher_enrich_document["--> enricher.enrich_document()"]:::callStyle
        tests_unit_test_context_enricher_py_test_no_context_document_warning["[FUNC] test_no_context_document_warning()"]:::funcStyle

    subgraph tests_unit_test_context_resolver_py ["?? tests/unit/test_context_resolver.py"]
        tests_unit_test_context_resolver_py_FakeRegistry["[CLASS] FakeRegistry"]:::classStyle
        tests_unit_test_context_resolver_py_FakeRegistry___init__["__init__()"]:::funcStyle
        tests_unit_test_context_resolver_py_FakeRegistry_mappings["mappings()"]:::funcStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver["[CLASS] TestInMemoryContextResolver"]:::classStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_setUp["setUp()"]:::funcStyle
    call_FakeRegistry["--> FakeRegistry()"]:::callStyle
    call_InMemoryContextResolver["--> InMemoryContextResolver()"]:::callStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_valid_context["test_resolve_valid_context()"]:::funcStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_unknown_context["test_resolve_unknown_context()"]:::funcStyle
    call_self_assertRaisesRegex["--> self.assertRaisesRegex()"]:::callStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_breadcrumbs_are_tuple["test_breadcrumbs_are_tuple()"]:::funcStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolved_context_hashable["test_resolved_context_hashable()"]:::funcStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_success_and_deduplication["test_resolve_many_success_and_deduplication()"]:::funcStyle
    call___resolve_many["--> *.resolve_many()"]:::callStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order["test_resolve_many_preserves_order()"]:::funcStyle
    call_res_keys["--> res.keys()"]:::callStyle
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_atomic_failure["test_resolve_many_atomic_failure()"]:::funcStyle

    subgraph tests_unit_test_dispatcher_py ["?? tests/unit/test_dispatcher.py"]
        tests_unit_test_dispatcher_py_TestAsyncDispatcher["[CLASS] TestAsyncDispatcher"]:::classStyle
        tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp["setUp()"]:::funcStyle
    call_AsyncMock["--> AsyncMock()"]:::callStyle
        tests_unit_test_dispatcher_py_TestAsyncDispatcher__create_mock_unit["_create_mock_unit()"]:::funcStyle
        tests_unit_test_dispatcher_py_TestAsyncDispatcher__mock_translate_side_effect["_mock_translate_side_effect()"]:::funcStyle
    call_ProviderResult["--> ProviderResult()"]:::callStyle

    subgraph tests_unit_test_dispatcher_validation_py ["?? tests/unit/test_dispatcher_validation.py"]
        tests_unit_test_dispatcher_validation_py_StaticMockProvider["[CLASS] StaticMockProvider"]:::classStyle
        tests_unit_test_dispatcher_validation_py_StaticMockProvider___init__["__init__()"]:::funcStyle
        tests_unit_test_dispatcher_validation_py_MockDocumentFailValidator["[CLASS] MockDocumentFailValidator"]:::classStyle
        tests_unit_test_dispatcher_validation_py_MockDocumentFailValidator_validate["validate()"]:::funcStyle
        tests_unit_test_dispatcher_validation_py_build_test_dispatcher["[FUNC] build_test_dispatcher()"]:::funcStyle

    subgraph tests_unit_test_healing_idempotency_py ["?? tests/unit/test_healing_idempotency.py"]
        tests_unit_test_healing_idempotency_py_MockValidationPipelineWithResidualFail["[CLASS] MockValidationPipelineWithResidualFail"]:::classStyle
        tests_unit_test_healing_idempotency_py_MockValidationPipelineWithResidualFail_validate_chunk["validate_chunk()"]:::funcStyle
        tests_unit_test_healing_idempotency_py_MockValidationPipelinePass["[CLASS] MockValidationPipelinePass"]:::classStyle
        tests_unit_test_healing_idempotency_py_MockValidationPipelinePass_validate_chunk["validate_chunk()"]:::funcStyle
        tests_unit_test_healing_idempotency_py_test_markdown_healing_is_idempotent["[FUNC] test_markdown_healing_is_idempotent()"]:::funcStyle
    call_make_test_healing_context["--> make_test_healing_context()"]:::callStyle
        tests_unit_test_healing_idempotency_py_test_metatext_healing_is_idempotent["[FUNC] test_metatext_healing_is_idempotent()"]:::funcStyle
        tests_unit_test_healing_idempotency_py_test_healing_idempotency_not_applicable_chain["[FUNC] test_healing_idempotency_not_applicable_chain()"]:::funcStyle
        tests_unit_test_healing_idempotency_py_test_healing_edge_case_payload_vacio_returns_failure["[FUNC] test_healing_edge_case_payload_vacio_returns_failure()"]:::funcStyle
        tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail["[FUNC] test_healing_pipeline_enforces_rollback_on_residual_hard_fail()"]:::funcStyle
    call_MockValidationPipelineWithResidualFail["--> MockValidationPipelineWithResidualFail()"]:::callStyle

    subgraph tests_unit_test_legacy_adapter_py ["?? tests/unit/test_legacy_adapter.py"]
        tests_unit_test_legacy_adapter_py_DummyLegacyValid["[CLASS] DummyLegacyValid"]:::classStyle
        tests_unit_test_legacy_adapter_py_DummyLegacyValid_validate["validate()"]:::funcStyle
        tests_unit_test_legacy_adapter_py_DummyLegacyInvalid["[CLASS] DummyLegacyInvalid"]:::classStyle
        tests_unit_test_legacy_adapter_py_DummyLegacyInvalid_validate["validate()"]:::funcStyle
        tests_unit_test_legacy_adapter_py_test_adapter_converts_error_to_validation_result["[FUNC] test_adapter_converts_error_to_validation_result()"]:::funcStyle
    call_adapter_validate["--> adapter.validate()"]:::callStyle
        tests_unit_test_legacy_adapter_py_test_adapter_default_severity_hard_fail["[FUNC] test_adapter_default_severity_hard_fail()"]:::funcStyle
        tests_unit_test_legacy_adapter_py_test_adapter_unknown_code_raises_domain_exception["[FUNC] test_adapter_unknown_code_raises_domain_exception()"]:::funcStyle
    call_pytest_raises["--> pytest.raises()"]:::callStyle

    subgraph tests_unit_test_math_normalizer_py ["?? tests/unit/test_math_normalizer.py"]
        tests_unit_test_math_normalizer_py_normalizer["[FUNC] normalizer()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_verbatim_environment_is_immune["[FUNC] test_verbatim_environment_is_immune()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_nested_verbatim_immunity["[FUNC] test_nested_verbatim_immunity()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_verb_with_dynamic_delimiter["[FUNC] test_verb_with_dynamic_delimiter()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_lstinline_preserved["[FUNC] test_lstinline_preserved()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_mintinline_preserved["[FUNC] test_mintinline_preserved()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_mintinline_with_options["[FUNC] test_mintinline_with_options()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_html_sup_conversion["[FUNC] test_html_sup_conversion()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_html_sub_conversion["[FUNC] test_html_sub_conversion()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_html_double_wrap_protection["[FUNC] test_html_double_wrap_protection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_balanced_inline_math["[FUNC] test_balanced_inline_math()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_unbalanced_inline_math_detection["[FUNC] test_unbalanced_inline_math_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_balanced_display_math["[FUNC] test_balanced_display_math()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_unclosed_environment_detection["[FUNC] test_unclosed_environment_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_environment_mismatch_detection["[FUNC] test_environment_mismatch_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_orphaned_end_detection["[FUNC] test_orphaned_end_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_inline_deprecated_conversion["[FUNC] test_inline_deprecated_conversion()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_display_deprecated_conversion["[FUNC] test_display_deprecated_conversion()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_multiple_pass_idempotency["[FUNC] test_multiple_pass_idempotency()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_empty_input["[FUNC] test_empty_input()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_whitespace_input["[FUNC] test_whitespace_input()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_protected_region_roundtrip["[FUNC] test_protected_region_roundtrip()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_strict_warning_severity_and_telemetry["[FUNC] test_strict_warning_severity_and_telemetry()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_illegal_recursive_nesting_detection["[FUNC] test_illegal_recursive_nesting_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_complex_environment_arguments_parsing["[FUNC] test_complex_environment_arguments_parsing()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_escaped_dollar_immunity_in_fsm["[FUNC] test_escaped_dollar_immunity_in_fsm()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_verbatim_masking["[FUNC] test_verbatim_masking()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_inequalities_not_removed["[FUNC] test_inequalities_not_removed()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_math_delimiter_automaton["[FUNC] test_math_delimiter_automaton()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_illegal_nesting_detection["[FUNC] test_illegal_nesting_detection()"]:::funcStyle
        tests_unit_test_math_normalizer_py_test_idempotency_preserve_contract["[FUNC] test_idempotency_preserve_contract()"]:::funcStyle

    subgraph tests_unit_test_paragraph_idempotency_py ["?? tests/unit/test_paragraph_idempotency.py"]
        tests_unit_test_paragraph_idempotency_py_test_paragraph_normalizer_invariants_and_strict_idempotency["[FUNC] test_paragraph_normalizer_invariants_and_strict_idempotency()"]:::funcStyle
    call_f_startswith["--> f.startswith()"]:::callStyle
        tests_unit_test_paragraph_idempotency_py_test_strict_idempotency_contract_over_corpus["[FUNC] test_strict_idempotency_contract_over_corpus()"]:::funcStyle

    subgraph tests_unit_test_perimeter_validator_py ["?? tests/unit/test_perimeter_validator.py"]
        tests_unit_test_perimeter_validator_py_test_markdown_block_detected["[FUNC] test_markdown_block_detected()"]:::funcStyle
        tests_unit_test_perimeter_validator_py_test_conversational_leak_with_leading_whitespace_detected["[FUNC] test_conversational_leak_with_leading_whitespace_detected()"]:::funcStyle
        tests_unit_test_perimeter_validator_py_test_extended_conversational_leak_detected["[FUNC] test_extended_conversational_leak_detected()"]:::funcStyle
        tests_unit_test_perimeter_validator_py_test_technical_prose_prefixes_pass_successfully["[FUNC] test_technical_prose_prefixes_pass_successfully()"]:::funcStyle
        tests_unit_test_perimeter_validator_py_test_clean_translation_payload_passes["[FUNC] test_clean_translation_payload_passes()"]:::funcStyle

    subgraph tests_unit_test_preservation_validator_py ["?? tests/unit/test_preservation_validator.py"]
        tests_unit_test_preservation_validator_py_test_doi_case_insensitivity_is_preserved["[FUNC] test_doi_case_insensitivity_is_preserved()"]:::funcStyle
        tests_unit_test_preservation_validator_py_test_addbibresource_with_optional_arguments["[FUNC] test_addbibresource_with_optional_arguments()"]:::funcStyle
        tests_unit_test_preservation_validator_py_test_modern_reference_commands["[FUNC] test_modern_reference_commands()"]:::funcStyle

    subgraph tests_unit_test_pricing_engine_py ["?? tests/unit/test_pricing_engine.py"]
        tests_unit_test_pricing_engine_py_TestPricingEngine["[CLASS] TestPricingEngine"]:::classStyle
        tests_unit_test_pricing_engine_py_TestPricingEngine_test_flash_calculation["test_flash_calculation()"]:::funcStyle
    call_self_assertAlmostEqual["--> self.assertAlmostEqual()"]:::callStyle
        tests_unit_test_pricing_engine_py_TestPricingEngine_test_zero_usd_conditions["test_zero_usd_conditions()"]:::funcStyle
        tests_unit_test_pricing_engine_py_TestPricingEngine_test_invalid_model_raises_value_error["test_invalid_model_raises_value_error()"]:::funcStyle

    subgraph tests_unit_test_prompt_builder_py ["?? tests/unit/test_prompt_builder.py"]
        tests_unit_test_prompt_builder_py_TestPromptBuilder["[CLASS] TestPromptBuilder"]:::classStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp["setUp()"]:::funcStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types["test_envelope_structure_and_types()"]:::funcStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_test_deterministic_prompt_hash["test_deterministic_prompt_hash()"]:::funcStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_collision_avoidance["test_hash_collision_avoidance()"]:::funcStyle
    call_self_assertNotEqual["--> self.assertNotEqual()"]:::callStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_test_prompt_hash_stability["test_prompt_hash_stability()"]:::funcStyle
        tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change["test_hash_mutation_on_model_or_version_change()"]:::funcStyle
    call_builder_alt_model_build["--> builder_alt_model.build()"]:::callStyle
    call_builder_alt_version_build["--> builder_alt_version.build()"]:::callStyle

    subgraph tests_unit_test_rate_limiter_py ["?? tests/unit/test_rate_limiter.py"]
        tests_unit_test_rate_limiter_py_FakeClock["[CLASS] FakeClock"]:::classStyle
        tests_unit_test_rate_limiter_py_FakeClock___init__["__init__()"]:::funcStyle
        tests_unit_test_rate_limiter_py_FakeClock_now["now()"]:::funcStyle
        tests_unit_test_rate_limiter_py_FakeClock_advance["advance()"]:::funcStyle
        tests_unit_test_rate_limiter_py_MockUnderlyingProvider["[CLASS] MockUnderlyingProvider"]:::classStyle
        tests_unit_test_rate_limiter_py__make_envelope["[FUNC] _make_envelope()"]:::funcStyle

    subgraph tests_unit_test_resilient_provider_py ["?? tests/unit/test_resilient_provider.py"]
        tests_unit_test_resilient_provider_py_MockNetworkFailureProvider["[CLASS] MockNetworkFailureProvider"]:::classStyle
        tests_unit_test_resilient_provider_py_MockNetworkFailureProvider___init__["__init__()"]:::funcStyle
        tests_unit_test_resilient_provider_py__make_envelope["[FUNC] _make_envelope()"]:::funcStyle

    subgraph tests_unit_test_routing_py ["?? tests/unit/test_routing.py"]
        tests_unit_test_routing_py_TestTranslationStrategyRouter["[CLASS] TestTranslationStrategyRouter"]:::classStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_setUp["setUp()"]:::funcStyle
    call_TranslationStrategyRouter["--> TranslationStrategyRouter()"]:::callStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_translate["test_default_routing_translate()"]:::funcStyle
    call___route["--> *.route()"]:::callStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_partial["test_default_routing_partial()"]:::funcStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_preserve["test_default_routing_preserve()"]:::funcStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_test_fail_fast_on_unknown_task_type["test_fail_fast_on_unknown_task_type()"]:::funcStyle
        tests_unit_test_routing_py_FakeTaskType["[CLASS] FakeTaskType"]:::classStyle
    call_FakeTaskType["--> FakeTaskType()"]:::callStyle
        tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection["test_custom_routing_table_injection()"]:::funcStyle
    call_custom_router_route["--> custom_router.route()"]:::callStyle

    subgraph tests_unit_test_semantic_chunker_py ["?? tests/unit/test_semantic_chunker.py"]
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss["[CLASS] TestSemanticChunkerZeroLoss"]:::classStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_setUp["setUp()"]:::funcStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss__create_node["_create_node()"]:::funcStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction["test_zero_loss_reconstruction()"]:::funcStyle
    call_self__create_node["--> self._create_node()"]:::callStyle
    call_reconstructed_seqs_extend["--> reconstructed_seqs.extend()"]:::callStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_normalize["normalize()"]:::funcStyle
    call___splitlines["--> *.splitlines()"]:::callStyle
    call_normalize["--> normalize()"]:::callStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_deterministic_purity["test_deterministic_purity()"]:::funcStyle
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary["test_context_aware_hard_boundary()"]:::funcStyle

    subgraph tests_unit_test_semantic_classifier_py ["?? tests/unit/test_semantic_classifier.py"]
        tests_unit_test_semantic_classifier_py_classifier["[FUNC] classifier()"]:::funcStyle
    call_SemanticNodeClassifier["--> SemanticNodeClassifier()"]:::callStyle
        tests_unit_test_semantic_classifier_py_test_academic_pdf_greek_mix_reclassification["[FUNC] test_academic_pdf_greek_mix_reclassification()"]:::funcStyle
    call_classifier_classify_node["--> classifier.classify_node()"]:::callStyle
        tests_unit_test_semantic_classifier_py_test_financial_false_positive_immunity["[FUNC] test_financial_false_positive_immunity()"]:::funcStyle
        tests_unit_test_semantic_classifier_py_test_financial_noise_with_many_operators["[FUNC] test_financial_noise_with_many_operators()"]:::funcStyle
        tests_unit_test_semantic_classifier_py_test_algebraic_indices_are_equation["[FUNC] test_algebraic_indices_are_equation()"]:::funcStyle
        tests_unit_test_semantic_classifier_py_test_large_formula_diluted_in_prosa_reclassification["[FUNC] test_large_formula_diluted_in_prosa_reclassification()"]:::funcStyle
        tests_unit_test_semantic_classifier_py_test_complete_batch_idempotency["[FUNC] test_complete_batch_idempotency()"]:::funcStyle
    call_classifier_classify_batch["--> classifier.classify_batch()"]:::callStyle
        tests_unit_test_semantic_classifier_py_test_unbalanced_tokens_immunity["[FUNC] test_unbalanced_tokens_immunity()"]:::funcStyle
        tests_unit_test_semantic_classifier_py_test_pure_operators_noise_immunity["[FUNC] test_pure_operators_noise_immunity()"]:::funcStyle

    subgraph tests_unit_test_semantic_validator_py ["?? tests/unit/test_semantic_validator.py"]
        tests_unit_test_semantic_validator_py_test_number_cardinality_mismatch_exact_content["[FUNC] test_number_cardinality_mismatch_exact_content()"]:::funcStyle
        tests_unit_test_semantic_validator_py_test_ip_address_not_parsed_as_number["[FUNC] test_ip_address_not_parsed_as_number()"]:::funcStyle
        tests_unit_test_semantic_validator_py_test_complex_scientific_units_exact_content["[FUNC] test_complex_scientific_units_exact_content()"]:::funcStyle
        tests_unit_test_semantic_validator_py_test_unit_case_sensitivity_kelvin_vs_kilo["[FUNC] test_unit_case_sensitivity_kelvin_vs_kilo()"]:::funcStyle

    subgraph tests_unit_test_structural_healing_py ["?? tests/unit/test_structural_healing.py"]
        tests_unit_test_structural_healing_py_test_brace_closure_strategy_success_on_nested_macros["[FUNC] test_brace_closure_strategy_success_on_nested_macros()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_verb_does_not_consume_neighboring_braces["[FUNC] test_verb_does_not_consume_neighboring_braces()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_brace_closure_ignores_escaped_braces["[FUNC] test_brace_closure_ignores_escaped_braces()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_brace_closure_bounds_trigger_failure_from_policy["[FUNC] test_brace_closure_bounds_trigger_failure_from_policy()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_brace_closure_not_applicable["[FUNC] test_brace_closure_not_applicable()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_math_closure_strategy_inline_success["[FUNC] test_math_closure_strategy_inline_success()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_math_closure_strategy_display_success["[FUNC] test_math_closure_strategy_display_success()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_math_closure_strategy_handles_truncated_display_state["[FUNC] test_math_closure_strategy_handles_truncated_display_state()"]:::funcStyle
        tests_unit_test_structural_healing_py_test_math_closure_not_applicable["[FUNC] test_math_closure_not_applicable()"]:::funcStyle

    subgraph tests_unit_test_structural_validator_py ["?? tests/unit/test_structural_validator.py"]
        tests_unit_test_structural_validator_py_test_braces_balanced_and_escaped["[FUNC] test_braces_balanced_and_escaped()"]:::funcStyle
    call_StructuralValidator__check_braces["--> StructuralValidator._check_braces()"]:::callStyle
        tests_unit_test_structural_validator_py_test_braces_unbalanced["[FUNC] test_braces_unbalanced()"]:::funcStyle
        tests_unit_test_structural_validator_py_test_brackets_balanced_and_escaped["[FUNC] test_brackets_balanced_and_escaped()"]:::funcStyle
    call_StructuralValidator__check_brackets["--> StructuralValidator._check_brackets()"]:::callStyle
        tests_unit_test_structural_validator_py_test_brackets_unbalanced["[FUNC] test_brackets_unbalanced()"]:::funcStyle
        tests_unit_test_structural_validator_py_test_math_delimiters_balanced["[FUNC] test_math_delimiters_balanced()"]:::funcStyle
    call_StructuralValidator__check_math_delimiters["--> StructuralValidator._check_math_delimiters()"]:::callStyle
        tests_unit_test_structural_validator_py_test_math_delimiters_unbalanced["[FUNC] test_math_delimiters_unbalanced()"]:::funcStyle
        tests_unit_test_structural_validator_py_test_environments_balanced["[FUNC] test_environments_balanced()"]:::funcStyle
    call_StructuralValidator__check_environments["--> StructuralValidator._check_environments()"]:::callStyle
        tests_unit_test_structural_validator_py_test_environments_unbalanced["[FUNC] test_environments_unbalanced()"]:::funcStyle

    subgraph tests_unit_test_summary_builder_py ["?? tests/unit/test_summary_builder.py"]
        tests_unit_test_summary_builder_py_TestSummaryBuilder["[CLASS] TestSummaryBuilder"]:::classStyle
        tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation["test_metrics_and_roi_aggregation()"]:::funcStyle
    call_SummaryBuilder_build["--> SummaryBuilder.build()"]:::callStyle

    subgraph tests_unit_test_validation_pipeline_py ["?? tests/unit/test_validation_pipeline.py"]
        tests_unit_test_validation_pipeline_py_MockPassValidator["[CLASS] MockPassValidator"]:::classStyle
        tests_unit_test_validation_pipeline_py_MockPassValidator_validate["validate()"]:::funcStyle
        tests_unit_test_validation_pipeline_py_MockFailValidator["[CLASS] MockFailValidator"]:::classStyle
        tests_unit_test_validation_pipeline_py_MockFailValidator_validate["validate()"]:::funcStyle
        tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only["[FUNC] test_pipeline_runs_chunk_validators_only()"]:::funcStyle
    call_MockPassValidator["--> MockPassValidator()"]:::callStyle
    call_MockFailValidator["--> MockFailValidator()"]:::callStyle
        tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only["[FUNC] test_pipeline_runs_document_validators_only()"]:::funcStyle
        tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order["[FUNC] test_pipeline_preserves_registration_order()"]:::funcStyle

    subgraph tests_unit___init___py ["?? tests/unit/__init__.py"]

    subgraph tools_load_test_db_injector_variable_py ["?? tools/load_test/db_injector_variable.py"]
        tools_load_test_db_injector_variable_py_run_db_injection["[FUNC] run_db_injection()"]:::funcStyle
    call_mode_upper["--> mode.upper()"]:::callStyle
    call_random_choices["--> random.choices()"]:::callStyle
    call_conn_rollback["--> conn.rollback()"]:::callStyle
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
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_DocumentAssembler
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_SummaryBuilder
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call__build_default_validation_pipeline
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_HealingPolicy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_MarkdownLeakageHealingStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_MetaTextLeakageHealingStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_EOFBraceClosureStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_EOFMathClosureStrategy
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_HealingPipeline
    apps_bootstrap_pipeline_factory_py_build_pipeline --> call_get_connection
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
        apps_llm_workers_prompt_builder_py_PromptBuilder --- apps_llm_workers_prompt_builder_py_PromptBuilder_build
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___join
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___hexdigest
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_hashlib_sha256
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_hash_input_encode
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call___estimate
    apps_llm_workers_prompt_builder_py_PromptBuilder_build --> call_PromptEnvelope
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
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler___init__
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler__validate_sequence
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_len
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_set
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_ValueError
    core_compiler_assembler_py_DocumentAssembler__validate_sequence --> call_IncompleteDocumentError
        core_compiler_assembler_py_DocumentAssembler --- core_compiler_assembler_py_DocumentAssembler_assemble
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_ReconstructedDocument
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_sorted
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_self__validate_sequence
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_len
    core_compiler_assembler_py_DocumentAssembler_assemble --> call_sum
    core_compiler_assembler_py_DocumentAssembler_assemble --> call___join
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
        core_metrics_summary_py_SummaryBuilder --- core_metrics_summary_py_SummaryBuilder_build
    core_metrics_summary_py_SummaryBuilder_build --> call___startswith
    core_metrics_summary_py_SummaryBuilder_build --> call___replace
    core_metrics_summary_py_SummaryBuilder_build --> call_max
    core_metrics_summary_py_SummaryBuilder_build --> call_len
    core_metrics_summary_py_SummaryBuilder_build --> call_PricingEngine_calculate_cost
    core_metrics_summary_py_SummaryBuilder_build --> call_TranslationAuditSummary
    core_metrics_summary_py_SummaryBuilder_build --> call_round
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
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient___init__
    graveyard_gemini_client_py_GeminiClient___init__ --> call___get
    graveyard_gemini_client_py_GeminiClient___init__ --> call_ValueError
    graveyard_gemini_client_py_GeminiClient___init__ --> call_os_getenv
    graveyard_gemini_client_py_GeminiClient___init__ --> call_CircuitBreakerRegistry_get_breaker
    graveyard_gemini_client_py_GeminiClient___init__ --> call_requests_Session
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient__clean_response
    graveyard_gemini_client_py_GeminiClient__clean_response --> call___strip
    graveyard_gemini_client_py_GeminiClient__clean_response --> call_result_startswith
    graveyard_gemini_client_py_GeminiClient__clean_response --> call_result_endswith
    graveyard_gemini_client_py_GeminiClient__clean_response --> call_result_strip
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient__build_fix_prompt
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient__is_transient
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient__execute_with_local_retries
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call___check_state
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call___acquire
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_ctx_execution_id_get
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_ctx_worker_id_get
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call___post
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_logger_warning
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_self__is_transient
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_TransientAPIError
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_response_raise_for_status
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_response_json
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_str
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_self__clean_response
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call___release
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_retry
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_wait_exponential
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_stop_after_attempt
    graveyard_gemini_client_py_GeminiClient__execute_with_local_retries --> call_retry_if_exception_type
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient_translate
    graveyard_gemini_client_py_GeminiClient_translate --> call_TranslationUnit
    graveyard_gemini_client_py_GeminiClient_translate --> call_PromptBuilder
    graveyard_gemini_client_py_GeminiClient_translate --> call_builder_build
    graveyard_gemini_client_py_GeminiClient_translate --> call___call
    graveyard_gemini_client_py_GeminiClient_translate --> call_self__execute_with_local_retries
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient_fix_latex
    graveyard_gemini_client_py_GeminiClient_fix_latex --> call_self__build_fix_prompt
    graveyard_gemini_client_py_GeminiClient_fix_latex --> call___call
    graveyard_gemini_client_py_GeminiClient_fix_latex --> call_self__execute_with_local_retries
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient_generate
    graveyard_gemini_client_py_GeminiClient_generate --> call___call
    graveyard_gemini_client_py_GeminiClient_generate --> call_self__execute_with_local_retries
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient__embed_with_local_retries
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call___check_state
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call___acquire
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_ctx_execution_id_get
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_ctx_worker_id_get
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call___post
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_logger_warning
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_self__is_transient
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_TransientAPIError
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_response_raise_for_status
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_response_json
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_str
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call___release
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_retry
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_wait_exponential
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_stop_after_attempt
    graveyard_gemini_client_py_GeminiClient__embed_with_local_retries --> call_retry_if_exception_type
        graveyard_gemini_client_py_GeminiClient --- graveyard_gemini_client_py_GeminiClient_embed_text
    graveyard_gemini_client_py_GeminiClient_embed_text --> call_text_strip
    graveyard_gemini_client_py_GeminiClient_embed_text --> call___call
    graveyard_gemini_client_py_GeminiClient_embed_text --> call_self__embed_with_local_retries
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
    tests_test_architecture_contract_py_test_ports_compliance --> call_sqlite3_connect
    tests_test_architecture_contract_py_test_ports_compliance --> call_ControlPlaneRepository
    tests_test_architecture_contract_py_test_ports_compliance --> call_EventPlaneRepository
    tests_test_architecture_contract_py_test_ports_compliance --> call_MaterializedPlaneRepository
    tests_test_architecture_contract_py_test_ports_compliance --> call_isinstance
    tests_test_math_protector_py_test_inline_math_protector --> call_InlineMathProtector_mask
    tests_test_math_protector_py_test_inline_math_protector --> call_masked_replace
    tests_test_math_protector_py_test_inline_math_protector --> call_InlineMathProtector_restore
    tests_test_math_protector_py_test_inline_math_protector --> call_print
    tests_test_pipeline_py_run_stress_tests --> call_CORPUS_DIR_mkdir
    tests_test_pipeline_py_run_stress_tests --> call_OUTPUT_DIR_mkdir
    tests_test_pipeline_py_run_stress_tests --> call_list
    tests_test_pipeline_py_run_stress_tests --> call_CORPUS_DIR_glob
    tests_test_pipeline_py_run_stress_tests --> call_print
    tests_test_pipeline_py_run_stress_tests --> call_len
    tests_test_pipeline_py_run_stress_tests --> call_str
    tests_test_pipeline_py_run_stress_tests --> call_run_pipeline
    tests_test_pipeline_py_run_stress_tests --> call_metrics_get
    tests_test_pipeline_py_run_stress_tests --> call_round
    tests_test_pipeline_py_run_stress_tests --> call_open
    tests_test_pipeline_py_run_stress_tests --> call_json_dump
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_html_sanitization_variants
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_html_sanitization_variants --> call_sanitize_marker_html
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_html_sanitization_variants --> call_self_assertEqual
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_InlineMathProtector_mask
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_InlineMathProtector_restore
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_bool
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_re_search
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_restored_lower
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_semantic_adjacency_and_mutations --> call_self_assertTrue
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math --> call_InlineMathProtector_mask
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math --> call_self_assertEqual
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math --> call_len
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math --> call_self_assertIn
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_inline_and_block_math --> call_InlineMathProtector_restore
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_safe_exists
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_safe_exists --> call_path_endswith
    tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser --> call_patch
    tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser --> call_b_strip
    tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser --> call_t_split
    tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser --> call_mock_open
    tests_test_pipeline_fidelity_py_TestPipelineFidelity__execute_mock_parser --> call_parse_pdf
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_quarantine_quarantine
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_quarantine_quarantine --> call_self__execute_mock_parser
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_quarantine_quarantine --> call_self_assertEqual
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation --> call_self__execute_mock_parser
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation --> call_self_assertEqual
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation --> call_len
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_mixed_image_block_continuation --> call___get
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_ratio_and_false_positives
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_ratio_and_false_positives --> call_self__execute_mock_parser
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_equation_ratio_and_false_positives --> call_self_assertEqual
        tests_test_pipeline_fidelity_py_TestPipelineFidelity --- tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_worker_passthrough_alignment
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_worker_passthrough_alignment --> call_self_assertTrue
    tests_test_pipeline_fidelity_py_TestPipelineFidelity_test_worker_passthrough_alignment --> call_hasattr
        tests_helpers_fakes_py_FakeChunker --- tests_helpers_fakes_py_FakeChunker_chunk
    tests_helpers_fakes_py_FakeChunker_chunk --> call_TranslationUnit
    tests_helpers_fakes_py_FakeChunker_chunk --> call_max
    tests_helpers_fakes_py_FakeChunker_chunk --> call_len
        tests_helpers_markdown_inspector_py_MarkdownInspector --- tests_helpers_markdown_inspector_py_MarkdownInspector_extract_structure
    tests_helpers_markdown_inspector_py_MarkdownInspector_extract_structure --> call_len
    tests_helpers_markdown_inspector_py_MarkdownInspector_extract_structure --> call_re_findall
        tests_helpers_markdown_inspector_py_MarkdownInspector --- tests_helpers_markdown_inspector_py_MarkdownInspector_extract_technical_tokens
    tests_helpers_markdown_inspector_py_MarkdownInspector_extract_technical_tokens --> call_re_findall
        tests_helpers_markdown_inspector_py_MarkdownInspector --- tests_helpers_markdown_inspector_py_MarkdownInspector_verify_balances
    tests_helpers_markdown_inspector_py_MarkdownInspector_verify_balances --> call_content_count
        tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot --- tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_setUp
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_setUp --> call_FastWordEstimator
        tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot --- tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call___exists
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_self_skipTest
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_open
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_json_load
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_ASTNode
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_StructuralNodeType
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_ContentNodeType
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_d_get
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_build_semantic_chunks_as_units
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_hasattr
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_list
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_json_dump
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_logger_info
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_self_assertEqual
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_len
    tests_integration_test_chunker_snapshot_py_TestChunkerSnapshot_test_snapshot_verification --> call_zip
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse --- tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing --> call_argparse_Namespace
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing --> call_main
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing --> call_mock_handle_assert_called_once_with
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_translate_subcommand_routing --> call_patch
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse --- tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing --> call_argparse_Namespace
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing --> call_main
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing --> call_mock_handle_assert_called_once_with
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_resume_subcommand_routing --> call_patch
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse --- tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing --> call_argparse_Namespace
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing --> call_main
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing --> call_mock_handle_assert_called_once_with
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_sweep_subcommand_routing --> call_patch
        tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse --- tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing --> call_argparse_Namespace
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing --> call_main
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing --> call_mock_handle_assert_called_once_with
    tests_integration_test_cli_router_py_TestCLIRoutingAndArgparse_test_status_subcommand_routing --> call_patch
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E --- tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call___exists
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_self_skipTest
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_FastWordEstimator
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_PromptBuilder
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_BypassProvider
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_CircuitBreakerRegistry_get_breaker
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_ResilientProvider
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_QuotaManager
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_RateLimitedProvider
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_CachedLLMProvider
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_asyncio_run
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call___initialize
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_MagicMock
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_AsyncDispatcher
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_ValidationPipeline
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_setUp --> call_DocumentAssembler
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E --- tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_tearDown
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_tearDown --> call___exists
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E_tearDown --> call_os_remove
        tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E --- tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_enumerate
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_node_get
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_payload_strip
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call___hexdigest
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_hashlib_sha256
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_payload_encode
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_units_append
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_TranslationUnit
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_max
    tests_integration_test_e2e_walking_skeleton_py_TestTrueWalkingSkeletonE2E__bridge_ast_to_units --> call_len
        tests_integration_test_golden_parser_py_TestGoldenParser --- tests_integration_test_golden_parser_py_TestGoldenParser_setUp
    tests_integration_test_golden_parser_py_TestGoldenParser_setUp --> call_PdfParserAdapter
    tests_integration_test_golden_parser_py_TestGoldenParser_setUp --> call___exists
    tests_integration_test_golden_parser_py_TestGoldenParser_setUp --> call_FileNotFoundError
        tests_integration_test_golden_parser_py_TestGoldenParser --- tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_hasattr
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_str
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_distribution_get
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_sequence_append
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_len
    tests_integration_test_golden_parser_py_TestGoldenParser__generate_fingerprint --> call_content_str_strip
        tests_integration_test_golden_parser_py_TestGoldenParser --- tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call___exists
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_self_skipTest
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call___parse
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_self__generate_fingerprint
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_open
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_json_load
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_self_assertEqual
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_enumerate
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_abs
    tests_integration_test_golden_parser_py_TestGoldenParser_test_parser_runtime_matches_golden_fingerprint --> call_self_assertLessEqual
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_HealingTelemetryRegistry
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_range
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_HealingEvent
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_registry_record
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_asyncio_sleep
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call__async_worker
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_asyncio_gather
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_asyncio_run
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call__main_orchestrator
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_registry_get_events
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_len
    tests_integration_test_healing_concurrency_py_test_telemetry_registry_async_concurrency --> call_registry_get_aggregate_metrics
        tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline --- tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline___init__
    tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline___init__ --> call_____init__
    tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline___init__ --> call_super
        tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline --- tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline_validate_chunk
    tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline_validate_chunk --> call___get
    tests_integration_test_healing_concurrency_py_ContextDrivenMockValidationPipeline_validate_chunk --> call_ValidationResult
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_ContextDrivenMockValidationPipeline
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_HealingTelemetryRegistry
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_HealingPipeline
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_EOFBraceClosureStrategy
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_ValidationContext
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_ValidationResult
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_HealingContext
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_registry_get_events
    tests_integration_test_healing_concurrency_py_test_healing_pipeline_emits_full_audit_on_rollback --> call_len
        tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline --- tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline___init__
    tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline___init__ --> call_____init__
    tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline___init__ --> call_super
        tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline --- tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline_validate_chunk
    tests_integration_test_healing_e2e_telemetry_py_MockValidationPipeline_validate_chunk --> call_ValidationResult
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_MockValidationPipeline
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_MarkdownLeakageHealingStrategy
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_EOFBraceClosureStrategy
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_EOFMathClosureStrategy
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_HealingTelemetryRegistry
    tests_integration_test_healing_e2e_telemetry_py__builder --> call_HealingPipeline
    tests_integration_test_healing_e2e_telemetry_py__make_ctx --> call_ValidationContext
    tests_integration_test_healing_e2e_telemetry_py__make_ctx --> call_ValidationResult
    tests_integration_test_healing_e2e_telemetry_py__make_ctx --> call_HealingContext
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_a_markdown_leakage --> call_build_pipeline_and_registry
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_a_markdown_leakage --> call__make_ctx
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_a_markdown_leakage --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_a_markdown_leakage --> call_registry_get_events
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_b_unbalanced_braces --> call_build_pipeline_and_registry
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_b_unbalanced_braces --> call__make_ctx
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_b_unbalanced_braces --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_b_unbalanced_braces --> call_registry_get_events
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_c_math_truncation --> call_build_pipeline_and_registry
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_c_math_truncation --> call__make_ctx
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_case_c_math_truncation --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_rollback_guarantee_on_revalidation_failure --> call_build_pipeline_and_registry
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_rollback_guarantee_on_revalidation_failure --> call__make_ctx
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_rollback_guarantee_on_revalidation_failure --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_rollback_guarantee_on_revalidation_failure --> call_registry_get_events
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_telemetry_aggregate_metrics --> call_build_pipeline_and_registry
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_telemetry_aggregate_metrics --> call_pipeline_heal_and_revalidate
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_telemetry_aggregate_metrics --> call__make_ctx
    tests_integration_test_healing_e2e_telemetry_py_test_e2e_telemetry_aggregate_metrics --> call_registry_get_aggregate_metrics
        tests_integration_test_pipeline_orchestration_py_FakeChunker --- tests_integration_test_pipeline_orchestration_py_FakeChunker_chunk
    tests_integration_test_pipeline_orchestration_py_FakeChunker_chunk --> call_TranslationUnit
    tests_integration_test_pipeline_orchestration_py_FakeChunker_chunk --> call_max
    tests_integration_test_pipeline_orchestration_py_FakeChunker_chunk --> call_len
        tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration --- tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_sqlite3_connect
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call___execute
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_FSMRepository
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_DocumentCommandHandler
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_FSMStateStore
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_build_pipeline
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_FakeChunker
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_FakeDispatcher
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call___exists
    tests_integration_test_pipeline_orchestration_py_TestPipelineOrchestration_setUp --> call_FileNotFoundError
        tests_integration_test_real_e2e_py_FinOpsControlledChunker --- tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk
    tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk --> call_TranslationUnit
    tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk --> call_min
    tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk --> call_max
    tests_integration_test_real_e2e_py_FinOpsControlledChunker_chunk --> call_len
        tests_integration_test_real_e2e_py_TestRealE2EFinOps --- tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_uuid_uuid4
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_FastWordEstimator
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_PromptBuilder
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_BypassProvider
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_CircuitBreakerRegistry_get_breaker
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_ResilientProvider
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_QuotaManager
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_RateLimitedProvider
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_SyncProviderBridge
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_MagicMock
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_AsyncDispatcher
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_build_pipeline
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_FinOpsControlledChunker
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_fsm_db_execute
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_setUp --> call_fsm_db_commit
        tests_integration_test_real_e2e_py_TestRealE2EFinOps --- tests_integration_test_real_e2e_py_TestRealE2EFinOps_tearDown
    tests_integration_test_real_e2e_py_TestRealE2EFinOps_tearDown --> call___shutdown
        tests_integration_test_real_paper_py_TestRealPaperIntegration --- tests_integration_test_real_paper_py_TestRealPaperIntegration_setUp
    tests_integration_test_real_paper_py_TestRealPaperIntegration_setUp --> call_os_getenv
    tests_integration_test_real_paper_py_TestRealPaperIntegration_setUp --> call___exists
    tests_integration_test_real_paper_py_TestRealPaperIntegration_setUp --> call_self_skipTest
        tests_integration_test_real_paper_py_TestRealPaperIntegration --- tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_parse_pdf
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_ASTHealthReport_from_ast
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_print
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_ASTValidator_validate
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_self_assertGreater
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_logger_info
    tests_integration_test_real_paper_py_TestRealPaperIntegration_test_parser_and_validation_e2e_local --> call_self_fail
        tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation --- tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_setUp
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_setUp --> call_PdfParserAdapter
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_setUp --> call___exists
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_setUp --> call_FileNotFoundError
        tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation --- tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence --> call___parse
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence --> call_self_assertIsInstance
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence --> call_self_assertGreater
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence --> call_len
    tests_integration_test_real_parser_pipeline_py_TestRealParserIsolation_test_parser_adapter_extracts_and_verifies_structural_presence --> call_self_assertIsNotNone
        tests_integration_test_recovery_flow_py_MockComponent --- tests_integration_test_recovery_flow_py_MockComponent_parse
        tests_integration_test_recovery_flow_py_MockComponent --- tests_integration_test_recovery_flow_py_MockComponent_chunk
        tests_integration_test_recovery_flow_py_MockComponent --- tests_integration_test_recovery_flow_py_MockComponent_assemble
    tests_integration_test_recovery_flow_py_MockComponent_assemble --> call_ReconstructedDocument
        tests_integration_test_recovery_flow_py_MockComponent --- tests_integration_test_recovery_flow_py_MockComponent_build
    tests_integration_test_recovery_flow_py_MockComponent_build --> call_TranslationAuditSummary
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd --- tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_str
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call___exists
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_os_remove
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_get_connection
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_conn_execute
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_conn_commit
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_setUpClass --> call_conn_close
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd --- tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_get_connection
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_FSMRepository
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_fsm_repo_initialize_document
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_time_time
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_conn_execute
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_conn_commit
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_fsm_repo_get_status
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_self_assertEqual
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_conn_close
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_AbandonedProcessWatchdog
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_watchdog_execute_sweep
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_OnDemandResumeManager
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_self_assertTrue
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_resumer_rescue_stalled_document
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_DocumentCommandHandler
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_FSMStateStore
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_MockComponent
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_TranslationPipeline
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_TranslationJob
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_asyncio_run
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_test_complete_crash_recovery_and_resume_lifecycle --> call_pipeline_execute
        tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd --- tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_tearDownClass
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_tearDownClass --> call_time_sleep
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_tearDownClass --> call___exists
    tests_integration_test_recovery_flow_py_TestRecoveryAndResumeEndToEnd_tearDownClass --> call_os_remove
        tests_integration_test_translation_layer_py_TestTranslationLayerIntegration --- tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_uuid_uuid4
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_FastWordEstimator
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_PromptBuilder
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_BypassProvider
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_CircuitBreakerRegistry_get_breaker
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_ResilientProvider
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_QuotaManager
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_RateLimitedProvider
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_CachedLLMProvider
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_asyncio_run
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call___initialize
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_MagicMock
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_AsyncDispatcher
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_ValidationPipeline
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_setUp --> call_DocumentAssembler
        tests_integration_test_translation_layer_py_TestTranslationLayerIntegration --- tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_tearDown
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_tearDown --> call___exists
    tests_integration_test_translation_layer_py_TestTranslationLayerIntegration_tearDown --> call_os_remove
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression --- tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_FastWordEstimator
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_PromptBuilder
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_BypassProvider
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_CircuitBreakerRegistry_get_breaker
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_ResilientProvider
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_QuotaManager
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_RateLimitedProvider
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_SyncProviderBridge
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_build_pipeline
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_setUp --> call_FakeChunker
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression --- tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_tearDown
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression_tearDown --> call___shutdown
        tests_integration_test_translation_semantics_py_TestSemanticChunkRegression --- tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity --> call_len
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity --> call_sum
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity --> call_zip
    tests_integration_test_translation_semantics_py_TestSemanticChunkRegression__calculate_cosine_similarity --> call_math_sqrt
        tests_integration_test_translation_structure_py_TestTranslationStructure --- tests_integration_test_translation_structure_py_TestTranslationStructure_setUp
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_sqlite3_connect
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call___execute
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_FSMRepository
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_FSMStateStore
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_DocumentCommandHandler
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_build_pipeline
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_FakeChunker
    tests_integration_test_translation_structure_py_TestTranslationStructure_setUp --> call_FakeDispatcher
        tests_integration_test_translation_technical_py_TestTranslationTechnical --- tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_sqlite3_connect
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call___execute
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_FSMRepository
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_FSMStateStore
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_DocumentCommandHandler
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_build_pipeline
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_FakeChunker
    tests_integration_test_translation_technical_py_TestTranslationTechnical_setUp --> call_FakeDispatcher
        tests_integration_test_validation_integration_py_StaticMockProvider --- tests_integration_test_validation_integration_py_StaticMockProvider___init__
        tests_integration_test_validation_integration_py_SequenceMockProvider --- tests_integration_test_validation_integration_py_SequenceMockProvider___init__
    tests_integration_test_validation_integration_py_build_test_dispatcher --> call_MagicMock
    tests_integration_test_validation_integration_py_build_test_dispatcher --> call_PromptBuilder
    tests_integration_test_validation_integration_py_build_test_dispatcher --> call_AsyncDispatcher
    tests_smoke_conftest_py_reliability_pipeline --> call_ValidationPipeline
    tests_smoke_conftest_py_reliability_pipeline --> call_PreservationValidator
    tests_smoke_conftest_py_reliability_pipeline --> call_LegacyValidatorAdapter
    tests_smoke_conftest_py_reliability_pipeline --> call_pipeline_add_chunk_validator
    tests_smoke_conftest_py_reliability_pipeline --> call_PerimeterValidator
    tests_smoke_conftest_py_reliability_pipeline --> call_SemanticValidator
    tests_smoke_conftest_py_reliability_pipeline --> call_VolumetricValidator
    tests_smoke_conftest_py_reliability_pipeline --> call_pipeline_add_document_validator
    tests_smoke_test_invariants_smoke_py_run_chunk_validation --> call_ValidationContext
    tests_smoke_test_invariants_smoke_py_run_chunk_validation --> call_pipeline_validate_chunk
    tests_smoke_test_invariants_smoke_py_run_doc_validation --> call_ValidationContext
    tests_smoke_test_invariants_smoke_py_run_doc_validation --> call_pipeline_validate_document
    tests_smoke_test_invariants_smoke_py_test_smoke_si01_unclosed_brace --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_si01_unclosed_brace --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_si02_unbalanced_math --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_si02_unbalanced_math --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_si03_unclosed_environment --> call_run_doc_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_si03_unclosed_environment --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pi01_doi_alteration --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pi01_doi_alteration --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pi02_url_domain_alteration --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pi02_url_domain_alteration --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pi03_orcid_lost --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pi03_orcid_lost --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pi04_cross_reference_lost --> call_run_doc_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pi04_cross_reference_lost --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pei01_markdown_block --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pei01_markdown_block --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_pei02_conversational_leak --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_pei02_conversational_leak --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_sei01_missing_number --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_sei01_missing_number --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_sei02_unit_mutation --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_sei02_unit_mutation --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_contraction --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_contraction --> call_any
    tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_expansion --> call_run_chunk_validation
    tests_smoke_test_invariants_smoke_py_test_smoke_vi01_ratio_expansion --> call_any
    tests_unit_test_adapters_py__make_envelope --> call_PromptEnvelope
        tests_unit_test_assembler_py_TestDocumentAssembler --- tests_unit_test_assembler_py_TestDocumentAssembler_setUp
    tests_unit_test_assembler_py_TestDocumentAssembler_setUp --> call_DocumentAssembler
        tests_unit_test_assembler_py_TestDocumentAssembler --- tests_unit_test_assembler_py_TestDocumentAssembler__mock_unit
    tests_unit_test_assembler_py_TestDocumentAssembler__mock_unit --> call_TranslatedUnit
        tests_unit_test_assembler_py_TestDocumentAssembler --- tests_unit_test_assembler_py_TestDocumentAssembler_test_successful_assembly_and_token_telemetry
    tests_unit_test_assembler_py_TestDocumentAssembler_test_successful_assembly_and_token_telemetry --> call_self__mock_unit
    tests_unit_test_assembler_py_TestDocumentAssembler_test_successful_assembly_and_token_telemetry --> call___assemble
    tests_unit_test_assembler_py_TestDocumentAssembler_test_successful_assembly_and_token_telemetry --> call_self_assertEqual
        tests_unit_test_assembler_py_TestDocumentAssembler --- tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error
    tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error --> call_self__mock_unit
    tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error --> call_self_assertRaises
    tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error --> call___assemble
    tests_unit_test_assembler_py_TestDocumentAssembler_test_missing_chunk_raises_incomplete_error --> call_self_assertEqual
        tests_unit_test_assembler_py_TestDocumentAssembler --- tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error
    tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error --> call_self__mock_unit
    tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error --> call_self_assertRaises
    tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error --> call___assemble
    tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error --> call_self_assertEqual
    tests_unit_test_assembler_py_TestDocumentAssembler_test_duplicate_chunk_raises_value_error --> call_str
    tests_unit_test_asset_placeholder_py_fixer --> call_StructuralAssetPlaceholder
    tests_unit_test_asset_placeholder_py_test_canonical_placeholder_generation --> call_fixer_normalize
    tests_unit_test_asset_placeholder_py_test_empty_content_passthrough --> call_fixer_normalize
    tests_unit_test_ast_integrity_py_validator --> call_ASTIntegrityValidator
    tests_unit_test_ast_integrity_py_test_empty_ast_triggers_warning_only --> call_validator_validate_ast
    tests_unit_test_ast_integrity_py_test_empty_ast_triggers_warning_only --> call_any
    tests_unit_test_ast_integrity_py_test_duplicate_node_id_collision --> call_ASTNode
    tests_unit_test_ast_integrity_py_test_duplicate_node_id_collision --> call_validator_validate_ast
    tests_unit_test_ast_integrity_py_test_duplicate_node_id_collision --> call_any
    tests_unit_test_ast_integrity_py_test_malformed_placeholder_syntax --> call_ASTNode
    tests_unit_test_ast_integrity_py_test_malformed_placeholder_syntax --> call_validator_validate_ast
    tests_unit_test_ast_integrity_py_test_malformed_placeholder_syntax --> call_any
    tests_unit_test_ast_integrity_py_test_orphan_list_item_emits_info_only --> call_ASTNode
    tests_unit_test_ast_integrity_py_test_orphan_list_item_emits_info_only --> call_validator_validate_ast
    tests_unit_test_ast_integrity_py_test_orphan_list_item_emits_info_only --> call_any
        tests_unit_test_cache_provider_py_MockLowLevelProvider --- tests_unit_test_cache_provider_py_MockLowLevelProvider___init__
    tests_unit_test_cache_provider_py_MockLowLevelProvider___init__ --> call_asyncio_Lock
    tests_unit_test_cache_provider_py_temp_db_path --> call_tempfile_mkstemp
    tests_unit_test_cache_provider_py_temp_db_path --> call_os_close
    tests_unit_test_cache_provider_py_temp_db_path --> call_os_remove
    tests_unit_test_context_enricher_py_enricher --> call_HierarchicalContextEnricher
    tests_unit_test_context_enricher_py_test_homonym_section_isolation --> call_ASTNode
    tests_unit_test_context_enricher_py_test_homonym_section_isolation --> call_enricher_enrich_document
    tests_unit_test_context_enricher_py_test_no_context_document_warning --> call_ASTNode
    tests_unit_test_context_enricher_py_test_no_context_document_warning --> call_enricher_enrich_document
    tests_unit_test_context_enricher_py_test_no_context_document_warning --> call_any
        tests_unit_test_context_resolver_py_FakeRegistry --- tests_unit_test_context_resolver_py_FakeRegistry___init__
        tests_unit_test_context_resolver_py_FakeRegistry --- tests_unit_test_context_resolver_py_FakeRegistry_mappings
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_setUp
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_setUp --> call_FakeRegistry
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_setUp --> call_InMemoryContextResolver
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_valid_context
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_valid_context --> call___resolve
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_valid_context --> call_self_assertEqual
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_unknown_context
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_unknown_context --> call_self_assertRaisesRegex
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_unknown_context --> call___resolve
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_breadcrumbs_are_tuple
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_breadcrumbs_are_tuple --> call___resolve
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_breadcrumbs_are_tuple --> call_self_assertIsInstance
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolved_context_hashable
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolved_context_hashable --> call___resolve
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolved_context_hashable --> call_self_assertEqual
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_success_and_deduplication
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_success_and_deduplication --> call___resolve_many
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_success_and_deduplication --> call_self_assertEqual
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_success_and_deduplication --> call_len
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order --> call___resolve_many
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order --> call_self_assertEqual
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order --> call_list
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_preserves_order --> call_res_keys
        tests_unit_test_context_resolver_py_TestInMemoryContextResolver --- tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_atomic_failure
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_atomic_failure --> call_self_assertRaisesRegex
    tests_unit_test_context_resolver_py_TestInMemoryContextResolver_test_resolve_many_atomic_failure --> call___resolve_many
        tests_unit_test_dispatcher_py_TestAsyncDispatcher --- tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp
    tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp --> call_AsyncMock
    tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp --> call_MagicMock
    tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp --> call_PromptBuilder
    tests_unit_test_dispatcher_py_TestAsyncDispatcher_setUp --> call_AsyncDispatcher
        tests_unit_test_dispatcher_py_TestAsyncDispatcher --- tests_unit_test_dispatcher_py_TestAsyncDispatcher__create_mock_unit
    tests_unit_test_dispatcher_py_TestAsyncDispatcher__create_mock_unit --> call_TranslationUnit
        tests_unit_test_dispatcher_py_TestAsyncDispatcher --- tests_unit_test_dispatcher_py_TestAsyncDispatcher__mock_translate_side_effect
    tests_unit_test_dispatcher_py_TestAsyncDispatcher__mock_translate_side_effect --> call_ProviderResult
        tests_unit_test_dispatcher_validation_py_StaticMockProvider --- tests_unit_test_dispatcher_validation_py_StaticMockProvider___init__
        tests_unit_test_dispatcher_validation_py_MockDocumentFailValidator --- tests_unit_test_dispatcher_validation_py_MockDocumentFailValidator_validate
    tests_unit_test_dispatcher_validation_py_MockDocumentFailValidator_validate --> call_ValidationResult
    tests_unit_test_dispatcher_validation_py_build_test_dispatcher --> call_MagicMock
    tests_unit_test_dispatcher_validation_py_build_test_dispatcher --> call_PromptBuilder
    tests_unit_test_dispatcher_validation_py_build_test_dispatcher --> call_AsyncDispatcher
        tests_unit_test_healing_idempotency_py_MockValidationPipelineWithResidualFail --- tests_unit_test_healing_idempotency_py_MockValidationPipelineWithResidualFail_validate_chunk
    tests_unit_test_healing_idempotency_py_MockValidationPipelineWithResidualFail_validate_chunk --> call_ValidationResult
        tests_unit_test_healing_idempotency_py_MockValidationPipelinePass --- tests_unit_test_healing_idempotency_py_MockValidationPipelinePass_validate_chunk
    tests_unit_test_healing_idempotency_py_test_markdown_healing_is_idempotent --> call_MarkdownLeakageHealingStrategy
    tests_unit_test_healing_idempotency_py_test_markdown_healing_is_idempotent --> call_make_test_healing_context
    tests_unit_test_healing_idempotency_py_test_markdown_healing_is_idempotent --> call_strategy_heal
    tests_unit_test_healing_idempotency_py_test_metatext_healing_is_idempotent --> call_MetaTextLeakageHealingStrategy
    tests_unit_test_healing_idempotency_py_test_metatext_healing_is_idempotent --> call_make_test_healing_context
    tests_unit_test_healing_idempotency_py_test_metatext_healing_is_idempotent --> call_strategy_heal
    tests_unit_test_healing_idempotency_py_test_healing_idempotency_not_applicable_chain --> call_MarkdownLeakageHealingStrategy
    tests_unit_test_healing_idempotency_py_test_healing_idempotency_not_applicable_chain --> call_make_test_healing_context
    tests_unit_test_healing_idempotency_py_test_healing_idempotency_not_applicable_chain --> call_strategy_heal
    tests_unit_test_healing_idempotency_py_test_healing_edge_case_payload_vacio_returns_failure --> call_MarkdownLeakageHealingStrategy
    tests_unit_test_healing_idempotency_py_test_healing_edge_case_payload_vacio_returns_failure --> call_make_test_healing_context
    tests_unit_test_healing_idempotency_py_test_healing_edge_case_payload_vacio_returns_failure --> call_strategy_heal
    tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail --> call_MockValidationPipelineWithResidualFail
    tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail --> call_MarkdownLeakageHealingStrategy
    tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail --> call_HealingPipeline
    tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail --> call_make_test_healing_context
    tests_unit_test_healing_idempotency_py_test_healing_pipeline_enforces_rollback_on_residual_hard_fail --> call_pipeline_heal_and_revalidate
        tests_unit_test_legacy_adapter_py_DummyLegacyValid --- tests_unit_test_legacy_adapter_py_DummyLegacyValid_validate
    tests_unit_test_legacy_adapter_py_DummyLegacyValid_validate --> call_ValidationError
        tests_unit_test_legacy_adapter_py_DummyLegacyInvalid --- tests_unit_test_legacy_adapter_py_DummyLegacyInvalid_validate
    tests_unit_test_legacy_adapter_py_DummyLegacyInvalid_validate --> call_ValidationError
    tests_unit_test_legacy_adapter_py_test_adapter_converts_error_to_validation_result --> call_LegacyValidatorAdapter
    tests_unit_test_legacy_adapter_py_test_adapter_converts_error_to_validation_result --> call_ValidationContext
    tests_unit_test_legacy_adapter_py_test_adapter_converts_error_to_validation_result --> call_adapter_validate
    tests_unit_test_legacy_adapter_py_test_adapter_converts_error_to_validation_result --> call_len
    tests_unit_test_legacy_adapter_py_test_adapter_default_severity_hard_fail --> call_LegacyValidatorAdapter
    tests_unit_test_legacy_adapter_py_test_adapter_default_severity_hard_fail --> call_ValidationContext
    tests_unit_test_legacy_adapter_py_test_adapter_default_severity_hard_fail --> call_adapter_validate
    tests_unit_test_legacy_adapter_py_test_adapter_unknown_code_raises_domain_exception --> call_LegacyValidatorAdapter
    tests_unit_test_legacy_adapter_py_test_adapter_unknown_code_raises_domain_exception --> call_ValidationContext
    tests_unit_test_legacy_adapter_py_test_adapter_unknown_code_raises_domain_exception --> call_pytest_raises
    tests_unit_test_legacy_adapter_py_test_adapter_unknown_code_raises_domain_exception --> call_adapter_validate
    tests_unit_test_math_normalizer_py_normalizer --> call_MathDomainNormalizer
    tests_unit_test_math_normalizer_py_test_verbatim_environment_is_immune --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_verbatim_environment_is_immune --> call_any
    tests_unit_test_math_normalizer_py_test_nested_verbatim_immunity --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_nested_verbatim_immunity --> call_len
    tests_unit_test_math_normalizer_py_test_verb_with_dynamic_delimiter --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_lstinline_preserved --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_mintinline_preserved --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_mintinline_with_options --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_html_sup_conversion --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_html_sub_conversion --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_html_double_wrap_protection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_balanced_inline_math --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_balanced_inline_math --> call_len
    tests_unit_test_math_normalizer_py_test_unbalanced_inline_math_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_unbalanced_inline_math_detection --> call_any
    tests_unit_test_math_normalizer_py_test_balanced_display_math --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_balanced_display_math --> call_len
    tests_unit_test_math_normalizer_py_test_unclosed_environment_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_unclosed_environment_detection --> call_any
    tests_unit_test_math_normalizer_py_test_environment_mismatch_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_environment_mismatch_detection --> call_any
    tests_unit_test_math_normalizer_py_test_orphaned_end_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_orphaned_end_detection --> call_any
    tests_unit_test_math_normalizer_py_test_inline_deprecated_conversion --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_display_deprecated_conversion --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_multiple_pass_idempotency --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_empty_input --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_whitespace_input --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_protected_region_roundtrip --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_strict_warning_severity_and_telemetry --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_strict_warning_severity_and_telemetry --> call_len
    tests_unit_test_math_normalizer_py_test_strict_warning_severity_and_telemetry --> call_any
    tests_unit_test_math_normalizer_py_test_illegal_recursive_nesting_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_illegal_recursive_nesting_detection --> call_any
    tests_unit_test_math_normalizer_py_test_complex_environment_arguments_parsing --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_complex_environment_arguments_parsing --> call_any
    tests_unit_test_math_normalizer_py_test_escaped_dollar_immunity_in_fsm --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_escaped_dollar_immunity_in_fsm --> call_any
    tests_unit_test_math_normalizer_py_test_verbatim_masking --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_verbatim_masking --> call_any
    tests_unit_test_math_normalizer_py_test_inequalities_not_removed --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_math_delimiter_automaton --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_math_delimiter_automaton --> call_len
    tests_unit_test_math_normalizer_py_test_math_delimiter_automaton --> call_any
    tests_unit_test_math_normalizer_py_test_illegal_nesting_detection --> call_normalizer_normalize
    tests_unit_test_math_normalizer_py_test_illegal_nesting_detection --> call_any
    tests_unit_test_math_normalizer_py_test_idempotency_preserve_contract --> call_normalizer_normalize
    tests_unit_test_paragraph_idempotency_py_test_paragraph_normalizer_invariants_and_strict_idempotency --> call_ParagraphNormalizer
    tests_unit_test_paragraph_idempotency_py_test_paragraph_normalizer_invariants_and_strict_idempotency --> call_normalizer_normalize
    tests_unit_test_paragraph_idempotency_py_test_paragraph_normalizer_invariants_and_strict_idempotency --> call_f_startswith
    tests_unit_test_paragraph_idempotency_py_test_paragraph_normalizer_invariants_and_strict_idempotency --> call_len
    tests_unit_test_paragraph_idempotency_py_test_strict_idempotency_contract_over_corpus --> call_ParagraphNormalizer
    tests_unit_test_paragraph_idempotency_py_test_strict_idempotency_contract_over_corpus --> call_normalizer_normalize
    tests_unit_test_paragraph_idempotency_py_test_strict_idempotency_contract_over_corpus --> call_len
    tests_unit_test_perimeter_validator_py_test_markdown_block_detected --> call_PerimeterValidator
    tests_unit_test_perimeter_validator_py_test_markdown_block_detected --> call_ValidationContext
    tests_unit_test_perimeter_validator_py_test_markdown_block_detected --> call_validator_validate
    tests_unit_test_perimeter_validator_py_test_markdown_block_detected --> call_any
    tests_unit_test_perimeter_validator_py_test_conversational_leak_with_leading_whitespace_detected --> call_PerimeterValidator
    tests_unit_test_perimeter_validator_py_test_conversational_leak_with_leading_whitespace_detected --> call_ValidationContext
    tests_unit_test_perimeter_validator_py_test_conversational_leak_with_leading_whitespace_detected --> call_validator_validate
    tests_unit_test_perimeter_validator_py_test_conversational_leak_with_leading_whitespace_detected --> call_any
    tests_unit_test_perimeter_validator_py_test_extended_conversational_leak_detected --> call_PerimeterValidator
    tests_unit_test_perimeter_validator_py_test_extended_conversational_leak_detected --> call_ValidationContext
    tests_unit_test_perimeter_validator_py_test_extended_conversational_leak_detected --> call_validator_validate
    tests_unit_test_perimeter_validator_py_test_extended_conversational_leak_detected --> call_any
    tests_unit_test_perimeter_validator_py_test_technical_prose_prefixes_pass_successfully --> call_PerimeterValidator
    tests_unit_test_perimeter_validator_py_test_technical_prose_prefixes_pass_successfully --> call_ValidationContext
    tests_unit_test_perimeter_validator_py_test_technical_prose_prefixes_pass_successfully --> call_validator_validate
    tests_unit_test_perimeter_validator_py_test_technical_prose_prefixes_pass_successfully --> call_len
    tests_unit_test_perimeter_validator_py_test_clean_translation_payload_passes --> call_PerimeterValidator
    tests_unit_test_perimeter_validator_py_test_clean_translation_payload_passes --> call_ValidationContext
    tests_unit_test_perimeter_validator_py_test_clean_translation_payload_passes --> call_validator_validate
    tests_unit_test_perimeter_validator_py_test_clean_translation_payload_passes --> call_len
    tests_unit_test_preservation_validator_py_test_doi_case_insensitivity_is_preserved --> call_PreservationValidator
    tests_unit_test_preservation_validator_py_test_doi_case_insensitivity_is_preserved --> call_ValidationContext
    tests_unit_test_preservation_validator_py_test_doi_case_insensitivity_is_preserved --> call_validator_validate
    tests_unit_test_preservation_validator_py_test_doi_case_insensitivity_is_preserved --> call_any
    tests_unit_test_preservation_validator_py_test_addbibresource_with_optional_arguments --> call_PreservationValidator
    tests_unit_test_preservation_validator_py_test_addbibresource_with_optional_arguments --> call_ValidationContext
    tests_unit_test_preservation_validator_py_test_addbibresource_with_optional_arguments --> call_validator_validate
    tests_unit_test_preservation_validator_py_test_addbibresource_with_optional_arguments --> call_any
    tests_unit_test_preservation_validator_py_test_modern_reference_commands --> call_PreservationValidator
    tests_unit_test_preservation_validator_py_test_modern_reference_commands --> call_ValidationContext
    tests_unit_test_preservation_validator_py_test_modern_reference_commands --> call_validator_validate
    tests_unit_test_preservation_validator_py_test_modern_reference_commands --> call_any
        tests_unit_test_pricing_engine_py_TestPricingEngine --- tests_unit_test_pricing_engine_py_TestPricingEngine_test_flash_calculation
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_flash_calculation --> call_PricingEngine_calculate_cost
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_flash_calculation --> call_self_assertAlmostEqual
        tests_unit_test_pricing_engine_py_TestPricingEngine --- tests_unit_test_pricing_engine_py_TestPricingEngine_test_zero_usd_conditions
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_zero_usd_conditions --> call_self_assertEqual
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_zero_usd_conditions --> call_PricingEngine_calculate_cost
        tests_unit_test_pricing_engine_py_TestPricingEngine --- tests_unit_test_pricing_engine_py_TestPricingEngine_test_invalid_model_raises_value_error
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_invalid_model_raises_value_error --> call_self_assertRaises
    tests_unit_test_pricing_engine_py_TestPricingEngine_test_invalid_model_raises_value_error --> call_PricingEngine_calculate_cost
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp
    tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp --> call_FastWordEstimator
    tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp --> call_PromptBuilder
    tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp --> call_TranslationUnit
    tests_unit_test_prompt_builder_py_TestPromptBuilder_setUp --> call_ResolvedContext
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call___build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call_self_assertIsInstance
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call_self_assertEqual
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call_self_assertTrue
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call___startswith
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_envelope_structure_and_types --> call_self_assertGreater
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_test_deterministic_prompt_hash
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_deterministic_prompt_hash --> call___build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_deterministic_prompt_hash --> call_self_assertEqual
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_collision_avoidance
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_collision_avoidance --> call_ResolvedContext
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_collision_avoidance --> call___build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_collision_avoidance --> call_self_assertNotEqual
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_test_prompt_hash_stability
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_prompt_hash_stability --> call___build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_prompt_hash_stability --> call_range
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_prompt_hash_stability --> call_self_assertEqual
        tests_unit_test_prompt_builder_py_TestPromptBuilder --- tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change --> call_PromptBuilder
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change --> call___build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change --> call_builder_alt_model_build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change --> call_builder_alt_version_build
    tests_unit_test_prompt_builder_py_TestPromptBuilder_test_hash_mutation_on_model_or_version_change --> call_self_assertNotEqual
        tests_unit_test_rate_limiter_py_FakeClock --- tests_unit_test_rate_limiter_py_FakeClock___init__
        tests_unit_test_rate_limiter_py_FakeClock --- tests_unit_test_rate_limiter_py_FakeClock_now
        tests_unit_test_rate_limiter_py_FakeClock --- tests_unit_test_rate_limiter_py_FakeClock_advance
    tests_unit_test_rate_limiter_py__make_envelope --> call_PromptEnvelope
        tests_unit_test_resilient_provider_py_MockNetworkFailureProvider --- tests_unit_test_resilient_provider_py_MockNetworkFailureProvider___init__
    tests_unit_test_resilient_provider_py__make_envelope --> call_PromptEnvelope
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_setUp
    tests_unit_test_routing_py_TestTranslationStrategyRouter_setUp --> call_TranslationStrategyRouter
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_translate
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_translate --> call_self_assertEqual
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_translate --> call___route
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_partial
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_partial --> call_self_assertEqual
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_partial --> call___route
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_preserve
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_preserve --> call_self_assertEqual
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_default_routing_preserve --> call___route
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_test_fail_fast_on_unknown_task_type
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_fail_fast_on_unknown_task_type --> call_self_assertRaisesRegex
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_fail_fast_on_unknown_task_type --> call___route
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_fail_fast_on_unknown_task_type --> call_FakeTaskType
        tests_unit_test_routing_py_TestTranslationStrategyRouter --- tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection --> call_TranslationStrategyRouter
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection --> call_self_assertEqual
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection --> call_custom_router_route
    tests_unit_test_routing_py_TestTranslationStrategyRouter_test_custom_routing_table_injection --> call_self_assertRaisesRegex
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_setUp
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_setUp --> call_FastWordEstimator
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_setUp --> call_ChunkPolicy
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss__create_node
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss__create_node --> call_ASTNode
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_self__create_node
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_build_semantic_chunks_as_units
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_self_assertEqual
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_sum
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_len
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_reconstructed_seqs_extend
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_range
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_list
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_normalize
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_normalize --> call___join
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_normalize --> call_line_strip
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_normalize --> call___splitlines
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call_normalize
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_zero_loss_reconstruction --> call___join
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_deterministic_purity
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_deterministic_purity --> call_self__create_node
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_deterministic_purity --> call_build_semantic_chunks_as_units
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_deterministic_purity --> call_self_assertEqual
        tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss --- tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary --> call_self__create_node
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary --> call_build_semantic_chunks_as_units
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary --> call_self_assertEqual
    tests_unit_test_semantic_chunker_py_TestSemanticChunkerZeroLoss_test_context_aware_hard_boundary --> call_len
    tests_unit_test_semantic_classifier_py_classifier --> call_SemanticNodeClassifier
    tests_unit_test_semantic_classifier_py_test_academic_pdf_greek_mix_reclassification --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_academic_pdf_greek_mix_reclassification --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_financial_false_positive_immunity --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_financial_false_positive_immunity --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_financial_noise_with_many_operators --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_financial_noise_with_many_operators --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_algebraic_indices_are_equation --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_algebraic_indices_are_equation --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_large_formula_diluted_in_prosa_reclassification --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_large_formula_diluted_in_prosa_reclassification --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_complete_batch_idempotency --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_complete_batch_idempotency --> call_classifier_classify_batch
    tests_unit_test_semantic_classifier_py_test_complete_batch_idempotency --> call_zip
    tests_unit_test_semantic_classifier_py_test_unbalanced_tokens_immunity --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_unbalanced_tokens_immunity --> call_classifier_classify_node
    tests_unit_test_semantic_classifier_py_test_pure_operators_noise_immunity --> call_ASTNode
    tests_unit_test_semantic_classifier_py_test_pure_operators_noise_immunity --> call_classifier_classify_node
    tests_unit_test_semantic_validator_py_test_number_cardinality_mismatch_exact_content --> call_SemanticValidator
    tests_unit_test_semantic_validator_py_test_number_cardinality_mismatch_exact_content --> call_ValidationContext
    tests_unit_test_semantic_validator_py_test_number_cardinality_mismatch_exact_content --> call_validator_validate
    tests_unit_test_semantic_validator_py_test_number_cardinality_mismatch_exact_content --> call_len
    tests_unit_test_semantic_validator_py_test_ip_address_not_parsed_as_number --> call_SemanticValidator
    tests_unit_test_semantic_validator_py_test_ip_address_not_parsed_as_number --> call_ValidationContext
    tests_unit_test_semantic_validator_py_test_ip_address_not_parsed_as_number --> call_validator_validate
    tests_unit_test_semantic_validator_py_test_ip_address_not_parsed_as_number --> call_len
    tests_unit_test_semantic_validator_py_test_complex_scientific_units_exact_content --> call_SemanticValidator
    tests_unit_test_semantic_validator_py_test_complex_scientific_units_exact_content --> call_ValidationContext
    tests_unit_test_semantic_validator_py_test_complex_scientific_units_exact_content --> call_validator_validate
    tests_unit_test_semantic_validator_py_test_complex_scientific_units_exact_content --> call_len
    tests_unit_test_semantic_validator_py_test_unit_case_sensitivity_kelvin_vs_kilo --> call_SemanticValidator
    tests_unit_test_semantic_validator_py_test_unit_case_sensitivity_kelvin_vs_kilo --> call_ValidationContext
    tests_unit_test_semantic_validator_py_test_unit_case_sensitivity_kelvin_vs_kilo --> call_validator_validate
    tests_unit_test_semantic_validator_py_test_unit_case_sensitivity_kelvin_vs_kilo --> call_len
    tests_unit_test_structural_healing_py_test_brace_closure_strategy_success_on_nested_macros --> call_EOFBraceClosureStrategy
    tests_unit_test_structural_healing_py_test_brace_closure_strategy_success_on_nested_macros --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_brace_closure_strategy_success_on_nested_macros --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_verb_does_not_consume_neighboring_braces --> call_EOFBraceClosureStrategy
    tests_unit_test_structural_healing_py_test_verb_does_not_consume_neighboring_braces --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_verb_does_not_consume_neighboring_braces --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_brace_closure_ignores_escaped_braces --> call_EOFBraceClosureStrategy
    tests_unit_test_structural_healing_py_test_brace_closure_ignores_escaped_braces --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_brace_closure_ignores_escaped_braces --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_brace_closure_bounds_trigger_failure_from_policy --> call_HealingPolicy
    tests_unit_test_structural_healing_py_test_brace_closure_bounds_trigger_failure_from_policy --> call_EOFBraceClosureStrategy
    tests_unit_test_structural_healing_py_test_brace_closure_bounds_trigger_failure_from_policy --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_brace_closure_bounds_trigger_failure_from_policy --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_brace_closure_not_applicable --> call_EOFBraceClosureStrategy
    tests_unit_test_structural_healing_py_test_brace_closure_not_applicable --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_brace_closure_not_applicable --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_math_closure_strategy_inline_success --> call_EOFMathClosureStrategy
    tests_unit_test_structural_healing_py_test_math_closure_strategy_inline_success --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_math_closure_strategy_inline_success --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_math_closure_strategy_display_success --> call_EOFMathClosureStrategy
    tests_unit_test_structural_healing_py_test_math_closure_strategy_display_success --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_math_closure_strategy_display_success --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_math_closure_strategy_handles_truncated_display_state --> call_EOFMathClosureStrategy
    tests_unit_test_structural_healing_py_test_math_closure_strategy_handles_truncated_display_state --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_math_closure_strategy_handles_truncated_display_state --> call_strategy_heal
    tests_unit_test_structural_healing_py_test_math_closure_not_applicable --> call_EOFMathClosureStrategy
    tests_unit_test_structural_healing_py_test_math_closure_not_applicable --> call_make_test_healing_context
    tests_unit_test_structural_healing_py_test_math_closure_not_applicable --> call_strategy_heal
    tests_unit_test_structural_validator_py_test_braces_balanced_and_escaped --> call_StructuralValidator__check_braces
    tests_unit_test_structural_validator_py_test_braces_unbalanced --> call_StructuralValidator__check_braces
    tests_unit_test_structural_validator_py_test_brackets_balanced_and_escaped --> call_StructuralValidator__check_brackets
    tests_unit_test_structural_validator_py_test_brackets_unbalanced --> call_StructuralValidator__check_brackets
    tests_unit_test_structural_validator_py_test_math_delimiters_balanced --> call_StructuralValidator__check_math_delimiters
    tests_unit_test_structural_validator_py_test_math_delimiters_unbalanced --> call_StructuralValidator__check_math_delimiters
    tests_unit_test_structural_validator_py_test_environments_balanced --> call_StructuralValidator__check_environments
    tests_unit_test_structural_validator_py_test_environments_unbalanced --> call_StructuralValidator__check_environments
        tests_unit_test_summary_builder_py_TestSummaryBuilder --- tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation
    tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation --> call_TranslatedUnit
    tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation --> call_ReconstructedDocument
    tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation --> call_SummaryBuilder_build
    tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation --> call_self_assertEqual
    tests_unit_test_summary_builder_py_TestSummaryBuilder_test_metrics_and_roi_aggregation --> call_self_assertGreater
        tests_unit_test_validation_pipeline_py_MockPassValidator --- tests_unit_test_validation_pipeline_py_MockPassValidator_validate
    tests_unit_test_validation_pipeline_py_MockPassValidator_validate --> call_ValidationResult
        tests_unit_test_validation_pipeline_py_MockFailValidator --- tests_unit_test_validation_pipeline_py_MockFailValidator_validate
    tests_unit_test_validation_pipeline_py_MockFailValidator_validate --> call_ValidationResult
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_ValidationPipeline
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_pipeline_add_chunk_validator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_MockPassValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_MockFailValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_pipeline_add_document_validator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_ValidationContext
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_pipeline_validate_chunk
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_chunk_validators_only --> call_len
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_ValidationPipeline
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_pipeline_add_chunk_validator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_MockPassValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_pipeline_add_document_validator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_MockFailValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_ValidationContext
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_pipeline_validate_document
    tests_unit_test_validation_pipeline_py_test_pipeline_runs_document_validators_only --> call_len
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_ValidationPipeline
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_pipeline_add_chunk_validator
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_MockPassValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_MockFailValidator
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_ValidationContext
    tests_unit_test_validation_pipeline_py_test_pipeline_preserves_registration_order --> call_pipeline_validate_chunk
    tools_load_test_db_injector_variable_py_run_db_injection --> call___abspath
    tools_load_test_db_injector_variable_py_run_db_injection --> call_print
    tools_load_test_db_injector_variable_py_run_db_injection --> call_mode_upper
    tools_load_test_db_injector_variable_py_run_db_injection --> call_time_perf_counter
    tools_load_test_db_injector_variable_py_run_db_injection --> call_sqlite3_connect
    tools_load_test_db_injector_variable_py_run_db_injection --> call_conn_execute
    tools_load_test_db_injector_variable_py_run_db_injection --> call_ControlPlaneRepository
    tools_load_test_db_injector_variable_py_run_db_injection --> call_range
    tools_load_test_db_injector_variable_py_run_db_injection --> call_uuid_uuid4
    tools_load_test_db_injector_variable_py_run_db_injection --> call_random_choices
    tools_load_test_db_injector_variable_py_run_db_injection --> call_task_repo_enqueue_tasks
    tools_load_test_db_injector_variable_py_run_db_injection --> call_len
    tools_load_test_db_injector_variable_py_run_db_injection --> call_conn_commit
    tools_load_test_db_injector_variable_py_run_db_injection --> call_conn_rollback
    tools_load_test_db_injector_variable_py_run_db_injection --> call_sys_exit
    tools_load_test_db_injector_variable_py_run_db_injection --> call_conn_close
    classDef classStyle fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef funcStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:1px,color:#ddd;
    classDef callStyle fill:#111827,stroke:#374151,stroke-width:1px,color:#9ca3af,stroke-dasharray: 3 3;
```