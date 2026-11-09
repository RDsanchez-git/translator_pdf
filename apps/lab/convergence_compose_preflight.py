"""C0/T01: inspect effective Compose without starting containers or printing secrets.

This validates only the declared candidate topology. It does not certify an
actual Docker runtime, egress isolation, or PDF->PDF execution.
"""
from __future__ import annotations

import argparse
import json
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
_COMMANDS = {
    "db_bootstrap": ["python", "infra/db/bootstrap.py"],
    "ocr_router": ["python", "apps/ocr_router/__main__.py"],
    "llm_worker": ["python", "runtime/engine.py"],
    "assembler": ["python", "apps/compiler/__main__.py"],
    "reconciler": ["python", "apps/daemons/reconciler.py"],
    "sweeper": ["python", "runtime/sweeper.py"],
    "g3_fake": ["python", "-m", "apps.lab.g3_fake", "--serve"],
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
    if set(services) != set(_COMMANDS) | {"toxiproxy", "fake-gemini"}:
        errors.append("COMPOSE_SERVICE_SET_DRIFT")
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
        if len(targets) != len(volumes) or any(
            not isinstance(v, dict) or v.get("type") != "volume"
            for v in volumes
        ):
            errors.append(f"{name}:NON_ISOLATED_MOUNT")
        required = {"/app/state", "/app/data", "/app/output"}
        if name == "g3_fake":
            if set(targets) != {"/app/state"} or not targets["/app/state"].get("read_only"):
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
        if name != "g3_fake" and any(env.get(k) != v for k, v in _DB_PATHS.items()):
            errors.append(f"{name}:DB_NAMESPACE_DRIFT")
        if name == "llm_worker":
            if (str(env.get("IS_BENCHMARK")) != "0"
                    or env.get("GROQ_API_KEY") != _DUMMY
                    or env.get("GROQ_BASE_URL") != "http://g3_fake:8080/openai/v1"
                    or env.get("GEMINI_API_KEY") not in (None, "")
                    or env.get("GEMINI_API_URL") not in (None, "")):
                errors.append("llm_worker:PROVIDER_CONFIGURATION_DRIFT")
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
        service = services.get(name, {})
        if not isinstance(service, dict) or "lab" not in service.get("profiles", []):
            errors.append(f"{name}:HISTORICAL_SERVICE_ENABLED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="C0/T01 read-only Compose topology preflight")
    parser.add_argument("--run-id", required=True, help="Unique lowercase a-z0-9 id (8-16 chars)")
    args = parser.parse_args()
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
    print("C0_T01_STATIC_CANDIDATE_PASS: no containers started; runtime still unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
