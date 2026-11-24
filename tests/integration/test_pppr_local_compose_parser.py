"""Real Compose parser regression; no container, image build or pull."""
import os
import subprocess

import pytest

from tools import pppr_local_preflight as p


@pytest.mark.integration
def test_actual_local_overlay_effective_contract():
    try:
        version = subprocess.run(["docker", "compose", "version"],
                                 capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        if os.getenv("PPPR_REQUIRE_COMPOSE_PARSER") == "1":
            pytest.fail("Required Compose parser unavailable")
        pytest.skip("Docker Compose parser unavailable")
    assert version.stdout.strip()
    config, false_omitted = p.load_effective_config(["docker"], "tpdfppprcitest")
    assert p.inspect(config, "tpdfppprcitest", false_bind_omitted=false_omitted) == []
    config["services"]["ocr_router"]["build"] = {"context": "."}
    for mount in config["services"]["ocr_router"]["volumes"]:
        if mount["target"] == "/workspace":
            mount["bind"] = {"create_host_path": True}
    errors = p.inspect(config, "tpdfppprcitest", false_bind_omitted=false_omitted)
    assert "ocr_router:IMAGE_POLICY" in errors
    assert "ocr_router:MOUNT_POLICY" in errors
