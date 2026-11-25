"""Real Compose parser regression; no container, image build or pull."""
import json
import os
import subprocess

import pytest

from tools import pppr_local_preflight as p


@pytest.mark.integration
def test_actual_local_overlay_effective_contract(tmp_path):
    try:
        version = subprocess.run(["docker", "compose", "version"],
                                 capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        if os.getenv("PPPR_REQUIRE_COMPOSE_PARSER") == "1":
            pytest.fail("Required Compose parser unavailable")
        pytest.skip("Docker Compose parser unavailable")
    print(version.stdout.strip())
    project = "tpdfppprcitest"
    config, declared = p.load_effective_config(["docker"], project)
    assert p.inspect(config, project, declared=declared) == []

    # Process actual negative overrides through the same Compose parser.
    override = tmp_path / "negative.json"
    override.write_text(json.dumps({"services": {"ocr_router": {
        "build": {"context": str(p.ROOT)},
        "volumes": [{"type": "bind", "source": str(p.ROOT),
                     "target": "/workspace", "read_only": True,
                     "bind": {"create_host_path": True}}]
    }}}), encoding="utf-8")
    dc = ["docker", "compose", "--project-name", project] + [
        arg for file in ("docker-compose.yml", "docker-compose.runtime.yml", "docker-compose.local.yml")
        for arg in ("-f", str(p.ROOT / file))
    ] + ["-f", str(override)]
    bad = json.loads(p._read(dc + ["config", "--format", "json"]))
    bad_declared = json.loads(p._read(dc + ["config", "--no-interpolate", "--format", "json"]))
    errors = p.inspect(bad, project, declared=bad_declared)
    assert "ocr_router:IMAGE_POLICY" in errors
    assert "ocr_router:MOUNT_POLICY" in errors
