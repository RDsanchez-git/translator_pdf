"""Read-only preflight for the supported local/offline Compose overlay.

No Docker build/pull/start. Output only fixed reason codes, not config values.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824"
IMAGE_ID = "sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd"
COMMANDS = {
    "db_bootstrap": "infra/db/local_volume_bootstrap.py",
    "ocr_router": "apps/ocr_router/__main__.py",
    "llm_worker": "runtime/engine.py",
    "assembler": "apps/compiler/__main__.py",
    "reconciler": "apps/daemons/reconciler.py",
    "sweeper": "runtime/sweeper.py",
}
MOUNTS = {
    "/app/state": "g3_runtime_state",
    "/app/data": "g3_runtime_data",
    "/app/output": "g3_runtime_output",
    "/app/.cache/hf": "hf_models_cache",
    "/app/.cache/torch": "torch_cache",
    "/app/.cache/tectonic": "tectonic_cache",
}
SECRETS = (
    "GROQ_API_KEY", "GROQ_BASE_URL", "GEMINI_API_KEY", "GEMINI_API_URL",
    "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
)
DB_ENV = {
    "SQLITE_STATE_DIR": "/app/state/db",
    **{key: "/app/state/db/" + name for key, name in (
        ("FSM_DB_PATH", "fsm.db"), ("QUEUE_DB_PATH", "queue.db"),
        ("EVENT_DB_PATH", "event.db"), ("MAT_DB_PATH", "materialized.db"),
    )},
}


def _read(command: list[str], source: str | None = None) -> str:
    return subprocess.run(command, cwd=ROOT, input=source, capture_output=True,
                          text=True, check=True, timeout=30).stdout


def load_effective_config(docker: list[str], project: str) -> tuple[dict, dict]:
    """Read the same merged files in canonical and non-interpolated model views.

    The latter preserves explicit booleans before typed Project serialization.
    Both views are needed: the non-interpolated model alone is not runtime config.
    """
    dc = docker + ["compose", "--project-name", project] + [
        arg for file in ("docker-compose.yml", "docker-compose.runtime.yml", "docker-compose.local.yml")
        for arg in ("-f", str(ROOT / file))
    ]
    effective = json.loads(_read(dc + ["config", "--format", "json"]))
    declared = json.loads(_read(dc + ["config", "--no-interpolate", "--format", "json"]))
    return effective, declared


def _declared_no_create(model: dict, name: str) -> bool:
    """Require explicit false for the matching merged long-form bind."""
    mounts = model.get("services", {}).get(name, {}).get("volumes", [])
    code = [v for v in mounts if isinstance(v, dict) and v.get("target") == "/workspace"]
    if len(code) != 1:
        return False
    mount = code[0]
    bind = mount.get("bind", {})
    return (mount.get("type") == "bind" and mount.get("read_only") is True
            and Path(mount.get("source", "")).resolve() == ROOT
            and isinstance(bind, dict) and bind.get("create_host_path") is False)


def inspect(config: dict, project: str, *, declared: dict | None = None) -> list[str]:
    errors = []
    services = config.get("services", {})
    if set(services) != set(COMMANDS):
        errors.append("SERVICE_SET_DRIFT")
    networks = config.get("networks", {})
    net = networks.get("chaos_net", {})
    if (set(networks) != {"chaos_net"} or net.get("internal") is not True
            or net.get("driver") != "bridge" or net.get("external")
            or net.get("name") != project + "_chaos_net"):
        errors.append("NETWORK_DRIFT")
    definitions = config.get("volumes", {})
    for key in MOUNTS.values():
        volume = definitions.get(key, {})
        if (volume.get("name") != project + "_" + key or volume.get("external")
                or volume.get("driver", "local") != "local" or volume.get("driver_opts")):
            errors.append("VOLUME_DEFINITION_DRIFT")
    for name, script in COMMANDS.items():
        s = services.get(name, {})
        root = name == "db_bootstrap"
        if (s.get("image") != IMAGE or s.get("build") is not None
                or s.get("pull_policy") != "never"):
            errors.append(name + ":IMAGE_POLICY")
        if (s.get("command") != ["python", "-B", "/workspace/" + script]
                or s.get("working_dir") != "/app"
                or s.get("user") != ("0:0" if root else "10001:10001")
                or s.get("restart") != "no"):
            errors.append(name + ":ENTRYPOINT_POLICY")
        if (set(s.get("cap_drop", [])) != {"ALL"}
                or set(s.get("cap_add", [])) != (
                    {"CHOWN", "DAC_OVERRIDE", "SETGID", "SETUID"} if root else set()
                )
                or "no-new-privileges:true" not in s.get("security_opt", [])
                or s.get("privileged") or s.get("devices")):
            errors.append(name + ":PRIVILEGE_POLICY")
        if (set(s.get("networks", {})) != {"chaos_net"} or s.get("ports")
                or s.get("network_mode") or s.get("extra_hosts") or s.get("profiles")):
            errors.append(name + ":NETWORK_POLICY")
        deps = s.get("depends_on") or {}
        if (set(deps) != (set() if root else {"db_bootstrap"})
                or (not root and deps.get("db_bootstrap", {}).get("condition")
                    != "service_completed_successfully")):
            errors.append(name + ":DEPENDENCY_POLICY")
        volumes = s.get("volumes", [])
        targets = {v.get("target"): v for v in volumes}
        code = targets.get("/workspace", {})
        bind = code.get("bind", {})
        # Typed JSON can omit false; only an explicit matching declaration
        # in the same merged model can disambiguate that omission.
        no_create = (
            isinstance(bind, dict)
            and ("create_host_path" not in bind or bind.get("create_host_path") is False)
            and _declared_no_create(config if declared is None else declared, name)
        )
        if (len(targets) != len(volumes) or set(targets) != set(MOUNTS) | {"/workspace"}
                or code.get("type") != "bind" or not code.get("read_only")
                or Path(code.get("source", "")).resolve() != ROOT
                or not ROOT.is_dir() or not no_create):
            errors.append(name + ":MOUNT_POLICY")
        for target, source in MOUNTS.items():
            v = targets.get(target, {})
            if (v.get("type") != "volume" or v.get("source") != source
                    or v.get("read_only") or v.get("volume", {}).get("nocopy") is not True):
                errors.append(name + ":VOLUME_POLICY")
        env = s.get("environment", {})
        expected = {**DB_ENV, "APP_ROOT": "/app", "PYTHONPATH": "/workspace",
                    "PYTHONSAFEPATH": "1", "PYTHONDONTWRITEBYTECODE": "1",
                    "IS_BENCHMARK": "0", "TIKTOKEN_CACHE_DIR": "/app/data/tiktoken-cache"}
        if any(env.get(k) != v for k, v in expected.items()):
            errors.append(name + ":ENV_POLICY")
        if any(env.get(k) for k in SECRETS) or any(
            env.get(k) for k in ("TPDF_C0_VOLUME_INIT", "TPDF_OFFLINE_LAB", "TPDF_FAKE_PRIVATE_DOCKER")
        ):
            errors.append(name + ":OFFLINE_POLICY")
        if env.get("TPDF_LOCAL_VOLUME_INIT") != (
            "EXPLICIT_LOCAL_RUNTIME_VOLUME_INIT" if root else None
        ):
            errors.append(name + ":BOOTSTRAP_POLICY")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--context", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"tpdfpppr[a-z0-9]{4,20}", args.project):
        parser.error("project must be an isolated tpdfpppr identifier")
    if (any(os.getenv(k) for k in ("COMPOSE_PROFILES", "COMPOSE_FILE", "COMPOSE_ENV_FILES"))
            or (ROOT / ".env").exists()):
        print("LOCAL_PREFLIGHT_BLOCKED:HOST_COMPOSE_ENV")
        return 2
    docker = ["docker", "--context", args.context]
    try:
        config, declared = load_effective_config(docker, args.project)
        errors = inspect(config, args.project, declared=declared)
        local = json.loads(_read(docker + ["image", "inspect", IMAGE]))[0]
        if local["Id"] != IMAGE_ID or local["Config"].get("Volumes"):
            errors.append("LOCAL_IMAGE_ID_OR_IMPLICIT_VOLUME_DRIFT")
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, IndexError, AttributeError):
        print("LOCAL_PREFLIGHT_BLOCKED:CONFIG_OR_IMAGE_UNAVAILABLE")
        return 2
    if errors:
        for error in errors:
            print("LOCAL_PREFLIGHT_FAIL:" + error)
        return 1
    print("PPPR_G5_LOCAL_STATIC_PASS: runtime still unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
