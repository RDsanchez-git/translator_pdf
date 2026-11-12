"""C0/T01 contract tests; no Docker and no environment secrets."""
from copy import deepcopy

from apps.lab.convergence_compose_preflight import _BASE, _IMAGE

from apps.lab.convergence_compose_preflight import inspect_topology


def _good() -> dict:
    commands = {
        "db_bootstrap": ["python", "-B", "/workspace/apps/lab/convergence_db_bootstrap.py"],
        "ocr_router": ["python", "-B", "/workspace/apps/ocr_router/__main__.py"],
        "llm_worker": ["python", "-B", "/workspace/runtime/engine.py"],
        "assembler": ["python", "-B", "/workspace/apps/compiler/__main__.py"],
        "reconciler": ["python", "-B", "/workspace/apps/daemons/reconciler.py"],
        "sweeper": ["python", "-B", "/workspace/runtime/sweeper.py"],
        "g3_fake": ["python", "-B", "-m", "apps.lab.g3_fake", "--serve"],
    }
    common = {
        "SQLITE_STATE_DIR": "/app/state/db",
        "FSM_DB_PATH": "/app/state/db/fsm.db",
        "QUEUE_DB_PATH": "/app/state/db/queue.db",
        "EVENT_DB_PATH": "/app/state/db/event.db",
        "MAT_DB_PATH": "/app/state/db/materialized.db",
    }
    shared = [
        {"type": "bind", "source": str(_BASE), "target": "/workspace", "read_only": True},
        {"type": "volume", "source": "g3_runtime_state", "target": "/app/state", "volume": {"nocopy": True}},
        {"type": "volume", "source": "g3_runtime_data", "target": "/app/data", "volume": {"nocopy": True}},
        {"type": "volume", "source": "g3_runtime_output", "target": "/app/output", "volume": {"nocopy": True}},
    ]
    services = {
        name: {
            "command": command,
            "image": _IMAGE,
            "pull_policy": "never",
            "working_dir": "/app",
            "restart": "no",
            "networks": {"chaos_net": None},
            "environment": {**deepcopy(common), "PYTHONPATH": "/workspace",
                            "PYTHONSAFEPATH": "1", "PYTHONDONTWRITEBYTECODE": "1"},
            "volumes": deepcopy(shared),
        }
        for name, command in commands.items()
    }
    for name in ("ocr_router", "llm_worker"):
        services[name]["environment"]["TIKTOKEN_CACHE_DIR"] = "/app/data/tiktoken-cache"
    services["db_bootstrap"]["user"] = "0:0"
    services["db_bootstrap"]["environment"]["TPDF_C0_VOLUME_INIT"] = (
        "EXPLICIT_CONVERGENCE_C0_LAB_ONLY"
    )
    services["llm_worker"]["environment"].update({
        "IS_BENCHMARK": "0",
        "GROQ_API_KEY": "translator-pdf-g3-offline-fake-only",
        "GROQ_BASE_URL": "http://g3_fake:8080/openai/v1",
    })
    services["llm_worker"]["depends_on"] = {
        "db_bootstrap": {"condition": "service_completed_successfully"},
        "g3_fake": {"condition": "service_healthy"},
    }
    services["g3_fake"]["volumes"] = [
        {"type": "bind", "source": str(_BASE), "target": "/workspace", "read_only": True},
        {"type": "volume", "source": "g3_runtime_state",
         "target": "/app/state", "read_only": True, "volume": {"nocopy": True}},
    ]
    services["g3_fake"]["environment"] = {
        "PYTHONPATH": "/workspace",
        "PYTHONSAFEPATH": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GROQ_API_KEY": "translator-pdf-g3-offline-fake-only",
        "TPDF_OFFLINE_LAB": "EXPLICIT_OFFLINE_TEST_ONLY",
        "TPDF_FAKE_PRIVATE_DOCKER": "EXPLICIT_INTERNAL_NETWORK_ONLY",
        "TPDF_FAKE_QUEUE_DB": "/app/state/db/queue.db",
    }
    services["toxiproxy"] = {"profiles": ["lab"]}
    services["fake-gemini"] = {"profiles": ["lab"]}
    return {"services": services, "networks": {"chaos_net": {"internal": True}}}


def test_current_candidate_topology_contract() -> None:
    assert inspect_topology(_good()) == []


def test_rejects_missing_or_wrong_tiktoken_cache_dir() -> None:
    bad = _good()
    bad["services"]["ocr_router"]["environment"].pop("TIKTOKEN_CACHE_DIR")
    bad["services"]["llm_worker"]["environment"]["TIKTOKEN_CACHE_DIR"] = "/tmp/wrong-cache"

    issues = inspect_topology(bad)

    assert "ocr_router:TIKTOKEN_CACHE_DIR_DRIFT" in issues
    assert "llm_worker:TIKTOKEN_CACHE_DIR_DRIFT" in issues


def test_rejects_legacy_worker_and_benchmark() -> None:
    bad = _good()
    bad["services"]["llm_worker"]["command"] = [
        "python", "apps/llm_workers/__main__.py",
    ]
    bad["services"]["llm_worker"]["environment"]["IS_BENCHMARK"] = "1"
    issues = inspect_topology(bad)
    assert "llm_worker:UNEXPECTED_COMMAND" in issues
    assert "llm_worker:BENCHMARK_MODE_NOT_DISABLED" in issues


def test_rejects_split_state_and_real_egress() -> None:
    bad = _good()
    bad["services"]["ocr_router"]["volumes"][1]["source"] = "wrong_state"
    bad["networks"]["chaos_net"]["internal"] = False
    bad["services"]["llm_worker"]["ports"] = [{"published": "8080", "target": 8080}]
    issues = inspect_topology(bad)
    assert "ocr_router:VOLUME_SOURCE_DRIFT" in issues
    assert "COMPOSE_NETWORK_NOT_INTERNAL" in issues
    assert "llm_worker:NETWORK_EXPOSURE" in issues


def test_rejects_fake_write_access_and_old_services() -> None:
    bad = _good()
    bad["services"]["g3_fake"]["volumes"][1]["read_only"] = False
    bad["services"]["toxiproxy"]["profiles"] = []
    issues = inspect_topology(bad)
    assert "g3_fake:STATE_MUST_BE_READ_ONLY" in issues
    assert "toxiproxy:HISTORICAL_SERVICE_ENABLED" in issues


def test_inactive_profile_services_may_be_omitted_by_compose() -> None:
    config = _good()
    config["services"].pop("toxiproxy")
    config["services"].pop("fake-gemini")
    assert inspect_topology(config) == []


def test_unexpected_service_not_ignored() -> None:
    config = _good()
    config["services"]["legacy_r3_worker"] = {"command": ["python", "-B", "/workspace/apps/llm_workers/__main__.py"]}
    assert "COMPOSE_UNEXPECTED_SERVICES" in inspect_topology(config)


def test_provider_diagnostics_do_not_include_secret_values() -> None:
    bad = _good()
    env = bad["services"]["llm_worker"]["environment"]
    env["GROQ_API_KEY"] = "not-the-test-token"
    env["GROQ_BASE_URL"] = "https://example.invalid"
    env["GEMINI_API_KEY"] = "unwanted-secret"
    env["GEMINI_API_URL"] = "https://example.invalid"
    issues = inspect_topology(bad)
    assert "llm_worker:GROQ_KEY_NOT_DUMMY" in issues
    assert "llm_worker:GROQ_URL_NOT_PRIVATE_FAKE" in issues
    assert "llm_worker:GEMINI_KEY_STILL_PRESENT" in issues
    assert "llm_worker:GEMINI_URL_STILL_PRESENT" in issues
    assert "not-the-test-token" not in repr(issues)
    assert "unwanted-secret" not in repr(issues)


def test_rejects_named_volume_copy_up() -> None:
    bad = _good()
    bad["services"]["ocr_router"]["volumes"][1]["volume"]["nocopy"] = False
    bad["services"]["g3_fake"]["volumes"][1]["volume"]["nocopy"] = False
    issues = inspect_topology(bad)
    assert "ocr_router:VOLUME_COPYUP_FORBIDDEN" in issues
    assert "g3_fake:VOLUME_COPYUP_FORBIDDEN" in issues


def test_rejects_build_and_pull_attempts() -> None:
    bad = _good()
    bad["services"]["llm_worker"]["build"] = {"context": ".", "dockerfile": "Dockerfile"}
    bad["services"]["ocr_router"]["pull_policy"] = "always"
    bad["services"]["assembler"]["image"] = "python:3.11-slim"
    issues = inspect_topology(bad)
    assert "llm_worker:BUILD_FORBIDDEN" in issues
    assert "ocr_router:PULL_FORBIDDEN" in issues
    assert "assembler:HISTORICAL_IMAGE_DRIFT" in issues


def test_rejects_writable_or_wrong_source_checkout() -> None:
    bad = _good()
    bad["services"]["assembler"]["volumes"][0]["read_only"] = False
    bad["services"]["db_bootstrap"]["volumes"][0]["source"] = "/tmp/other-code"
    bad["services"]["ocr_router"]["environment"]["PYTHONPATH"] = "/app"
    issues = inspect_topology(bad)
    assert "assembler:CURRENT_CODE_MUST_BE_READ_ONLY" in issues
    assert "db_bootstrap:CURRENT_CODE_MUST_BE_READ_ONLY" in issues
    assert "ocr_router:CURRENT_CODE_IMPORT_DRIFT" in issues


def test_rejects_writable_host_bind_outside_checkout() -> None:
    bad = _good()
    bad["services"]["reconciler"]["volumes"].append({
        "type": "bind", "source": "/tmp/host-output",
        "target": "/app/output",
        "read_only": False,
    })
    issues = inspect_topology(bad)
    assert "reconciler:NON_ISOLATED_MOUNT" in issues


def test_root_is_restricted_to_bootstrap_init() -> None:
    bad = _good()
    bad["services"]["db_bootstrap"]["user"] = "10001:10001"
    bad["services"]["llm_worker"]["user"] = "0:0"
    issues = inspect_topology(bad)
    assert "db_bootstrap:ROOT_INIT_USER_REQUIRED" in issues
    assert "llm_worker:ROOT_WORKER_FORBIDDEN" in issues


def test_volume_init_token_must_not_leak_to_workers() -> None:
    bad = _good()
    bad["services"]["db_bootstrap"]["environment"]["TPDF_C0_VOLUME_INIT"] = ""
    bad["services"]["ocr_router"]["environment"]["TPDF_C0_VOLUME_INIT"] = (
        "EXPLICIT_CONVERGENCE_C0_LAB_ONLY"
    )
    issues = inspect_topology(bad)
    assert "db_bootstrap:VOLUME_INIT_OPT_IN_MISSING" in issues
    assert "ocr_router:VOLUME_INIT_PRIVILEGE_LEAK" in issues
