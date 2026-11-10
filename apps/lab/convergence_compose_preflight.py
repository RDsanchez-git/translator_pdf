"""C0/T01: inspect effective Compose without starting containers or printing secrets.

This validates only the declared candidate topology. It does not certify an
actual Docker runtime, egress isolation, or PDF->PDF execution.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

_BASE = Path(__file__).resolve().parents[2]
_FILES = (
    "docker-compose.yml", "docker-compose.runtime.yml",
    "docker-compose.convergence-lab.yml",
)
_DUMMY = "translator-pdf-g3-offline-fake-only"
_IMAGE = "i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824"
_IMAGE_ID = "sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd"
_COMMANDS = {
    "db_bootstrap": ["python", "-B", "/workspace/infra/db/bootstrap.py"],
    "ocr_router": ["python", "-B", "/workspace/apps/ocr_router/__main__.py"],
    "llm_worker": ["python", "-B", "/workspace/runtime/engine.py"],
    "assembler": ["python", "-B", "/workspace/apps/compiler/__main__.py"],
    "reconciler": ["python", "-B", "/workspace/apps/daemons/reconciler.py"],
    "sweeper": ["python", "-B", "/workspace/runtime/sweeper.py"],
    "g3_fake": ["python", "-B", "-m", "apps.lab.g3_fake", "--serve"],
}

_DB_PATHS = {
    "SQLITE_STATE_DIR": "/app/state/db",
    "FSM_DB_PATH": "/app/state/db/fsm.db",
    "QUEUE_DB_PATH": "/app/state/db/queue.db",
    "EVENT_DB_PATH": "/app/state/db/event.db",
    "MAT_DB_PATH": "/app/state/db/materialized.db",
}


def inspect_topology(config: dict[str, Any]) -> list[str]:
    """Return reason codes only; never return environment values or credentials."""
    errors: list[str] = []
    services = config.get("services")
    networks = config.get("networks")
    if not isinstance(services, dict) or not isinstance(networks, dict):
        return ["COMPOSE_CONFIG_INVALID"]
    # Compose may omit services behind inactive profiles from `config`.
    # Only the seven selected services are required; historical lab roots are optional.
    unexpected = set(services) - (set(_COMMANDS) | {"toxiproxy", "fake-gemini"})
    if unexpected:
        errors.append("COMPOSE_UNEXPECTED_SERVICES")
    net = networks.get("chaos_net")
    if not isinstance(net, dict) or net.get("internal") is not True:
        errors.append("COMPOSE_NETWORK_NOT_INTERNAL")

    for name, command in _COMMANDS.items():
        service = services.get(name)
        if not isinstance(service, dict):
            errors.append(f"{name}:MISSING")
            continue
        if service.get("command") != command:
            errors.append(f"{name}:UNEXPECTED_COMMAND")
        if service.get("build") is not None:
            errors.append(f"{name}:BUILD_FORBIDDEN")
        if service.get("image") != _IMAGE:
            errors.append(f"{name}:HISTORICAL_IMAGE_DRIFT")
        if service.get("pull_policy") != "never":
            errors.append(f"{name}:PULL_FORBIDDEN")
        if service.get("working_dir") != "/app":
            errors.append(f"{name}:WORKDIR_DRIFT")
        if service.get("ports") or service.get("network_mode") or service.get("extra_hosts"):
            errors.append(f"{name}:NETWORK_EXPOSURE")
        if set(service.get("networks", {})) != {"chaos_net"}:
            errors.append(f"{name}:NETWORK_DRIFT")
        if service.get("profiles"):
            errors.append(f"{name}:WRONG_PROFILE")
        if service.get("restart") not in ("no", "none", None):
            errors.append(f"{name}:AUTO_RESTART")
        volumes = service.get("volumes", [])
        if not isinstance(volumes, list):
            errors.append(f"{name}:VOLUMES_INVALID")
            continue
        targets = {v.get("target"): v for v in volumes if isinstance(v, dict)}
        if len(targets) != len(volumes):
            errors.append(f"{name}:DUPLICATE_MOUNT_TARGET")
        code = targets.get("/workspace", {})
        if (code.get("type") != "bind" or not code.get("read_only")
                or Path(str(code.get("source", ""))).resolve() != _BASE.resolve()):
            errors.append(f"{name}:CURRENT_CODE_MUST_BE_READ_ONLY")
        # Only one checkout bind is allowed; state and caches must be volumes.
        if any(
            not isinstance(v, dict) or
            (v.get("type") != "volume" and v is not code) or
            (v.get("type") == "bind" and v.get("target") != "/workspace")
            for v in volumes
        ):
            errors.append(f"{name}:NON_ISOLATED_MOUNT")
        required = {"/app/state", "/app/data", "/app/output"}
        if name == "g3_fake":
            if (set(targets) != {"/workspace", "/app/state"}
                    or not targets.get("/app/state", {}).get("read_only")):
                errors.append("g3_fake:STATE_MUST_BE_READ_ONLY")
        elif not required.issubset(targets):
            errors.append(f"{name}:MISSING_SHARED_VOLUME")
        for target in required & set(targets):
            actual = targets[target].get("source")
            expected = {
                "/app/state": "g3_runtime_state",
                "/app/data": "g3_runtime_data",
                "/app/output": "g3_runtime_output",
            }[target]
            if actual != expected:
                errors.append(f"{name}:VOLUME_SOURCE_DRIFT")

        env = service.get("environment", {})
        if not isinstance(env, dict):
            errors.append(f"{name}:ENV_INVALID")
            continue
        if (env.get("PYTHONPATH") != "/workspace"
                or str(env.get("PYTHONSAFEPATH")) != "1"
                or str(env.get("PYTHONDONTWRITEBYTECODE")) != "1"):
            errors.append(f"{name}:CURRENT_CODE_IMPORT_DRIFT")
        if name != "g3_fake" and any(env.get(k) != v for k, v in _DB_PATHS.items()):
            errors.append(f"{name}:DB_NAMESPACE_DRIFT")
        if name == "llm_worker":
            # Output reason codes only; never print the effective credential/URL.
            if str(env.get("IS_BENCHMARK")) != "0":
                errors.append("llm_worker:BENCHMARK_MODE_NOT_DISABLED")
            if env.get("GROQ_API_KEY") != _DUMMY:
                errors.append("llm_worker:GROQ_KEY_NOT_DUMMY")
            if env.get("GROQ_BASE_URL") != "http://g3_fake:8080/openai/v1":
                errors.append("llm_worker:GROQ_URL_NOT_PRIVATE_FAKE")
            if env.get("GEMINI_API_KEY") not in (None, ""):
                errors.append("llm_worker:GEMINI_KEY_STILL_PRESENT")
            if env.get("GEMINI_API_URL") not in (None, ""):
                errors.append("llm_worker:GEMINI_URL_STILL_PRESENT")
            deps = service.get("depends_on", {})
            if not isinstance(deps, dict) or set(deps) != {"db_bootstrap", "g3_fake"}:
                errors.append("llm_worker:UNEXPECTED_DEPENDENCY")
        if name == "g3_fake":
            if (env.get("GROQ_API_KEY") != _DUMMY
                    or env.get("TPDF_OFFLINE_LAB") != "EXPLICIT_OFFLINE_TEST_ONLY"
                    or env.get("TPDF_FAKE_PRIVATE_DOCKER") != "EXPLICIT_INTERNAL_NETWORK_ONLY"
                    or env.get("TPDF_FAKE_QUEUE_DB") != "/app/state/db/queue.db"):
                errors.append("g3_fake:FAKE_CONFIGURATION_DRIFT")

    for name in ("toxiproxy", "fake-gemini"):
        # Omitted by inactive profiles is safe. If present in the model, it
        # must remain tagged as a historical lab-only service.
        if name not in services:
            continue
        service = services[name]
        if not isinstance(service, dict) or "lab" not in service.get("profiles", []):
            errors.append(f"{name}:HISTORICAL_SERVICE_ENABLED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="C0/T01 read-only Compose topology preflight")
    parser.add_argument("--run-id", required=True, help="Unique lowercase a-z0-9 id (8-16 chars)")
    parser.add_argument(
        "--verify-local-image", action="store_true",
        help="Read-only docker image inspect; require pre-existing pinned image ID",
    )
    args = parser.parse_args()
    if os.getenv("COMPOSE_PROFILES"):
        print("C0_T01_BLOCKED:HOST_COMPOSE_PROFILES_SET")
        return 2
    if re.fullmatch(r"[a-z0-9]{8,16}", args.run_id) is None:
        parser.error("run-id must match [a-z0-9]{8,16}")
    command = [
        "docker", "compose", "--project-name", f"tpdfconv{args.run_id}",
        *(part for file in _FILES for part in ("-f", str(_BASE / file))),
        "config", "--format", "json",
    ]
    try:
        proc = subprocess.run(
            command, cwd=_BASE, capture_output=True, text=True,
            check=False, timeout=30,
        )
        if proc.returncode:
            print("C0_T01_BLOCKED:COMPOSE_CONFIG_UNAVAILABLE")
            return 2
        config = json.loads(proc.stdout)
        if not isinstance(config, dict):
            raise ValueError("expected object")
        issues = inspect_topology(config)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError):
        print("C0_T01_BLOCKED:CONFIG_OR_DOCKER_UNAVAILABLE")
        return 2
    if issues:
        for issue in issues:
            print("C0_T01_FAIL:" + issue)
        return 1
    if args.verify_local_image:
        # No pull, build, container, or volume creation.
        try:
            image = subprocess.run(
                ["docker", "image", "inspect", _IMAGE, "--format", "{{.Id}}"],
                capture_output=True, text=True, check=False, timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            print("C0_T01_BLOCKED:LOCAL_IMAGE_UNAVAILABLE")
            return 2
        if image.returncode or image.stdout.strip() != _IMAGE_ID:
            print("C0_T01_BLOCKED:LOCAL_IMAGE_MISSING_OR_ID_DRIFT")
            return 2
    print("C0_T01_STATIC_CANDIDATE_PASS: no containers started; runtime still unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
