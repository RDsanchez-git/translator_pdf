"""H-G5-01: supported local configuration cannot silently inherit lab controls."""
from copy import deepcopy

import pytest

from tools import pppr_local_preflight as p


def candidate():
    services = {}
    for name, command in p.COMMANDS.items():
        root = name == "db_bootstrap"
        env = {**p.DB_ENV, "APP_ROOT": "/app", "PYTHONPATH": "/workspace",
               "PYTHONSAFEPATH": "1", "PYTHONDONTWRITEBYTECODE": "1",
               "IS_BENCHMARK": "0", "TIKTOKEN_CACHE_DIR": "/app/data/tiktoken-cache"}
        if root:
            env["TPDF_LOCAL_VOLUME_INIT"] = "EXPLICIT_LOCAL_RUNTIME_VOLUME_INIT"
        services[name] = {
            "image": p.IMAGE, "pull_policy": "never", "working_dir": "/app",
            "command": ["python", "-B", "/workspace/" + command],
            "user": "0:0" if root else "10001:10001", "restart": "no",
            "cap_drop": ["ALL"], "cap_add": ["CHOWN", "DAC_OVERRIDE", "SETGID", "SETUID"] if root else [],
            "security_opt": ["no-new-privileges:true"],
            "networks": {"chaos_net": None},
            "depends_on": {} if root else {"db_bootstrap": {"condition": "service_completed_successfully"}},
            "environment": env,
            "volumes": [
                {"type": "bind", "source": str(p.ROOT), "target": "/workspace",
                 "read_only": True, "bind": {"create_host_path": False}},
                *[{"type": "volume", "source": source, "target": target, "volume": {"nocopy": True}}
                  for target, source in p.MOUNTS.items()],
            ],
        }
    return {"services": services, "networks": {"chaos_net": {
        "internal": True, "driver": "bridge", "name": "tpdfppprtest_chaos_net"}},
        "volumes": {name: {"name": "tpdfppprtest_" + name} for name in p.MOUNTS.values()}}


@pytest.mark.unit
def test_local_candidate():
    assert p.inspect(candidate(), "tpdfppprtest") == []


@pytest.mark.unit
@pytest.mark.parametrize(("key", "value", "reason"), [
    ("user", "0:0", "ENTRYPOINT_POLICY"),
    ("restart", "unless-stopped", "ENTRYPOINT_POLICY"),
    ("build", {"context": "."}, "IMAGE_POLICY"),
    ("pull_policy", "always", "IMAGE_POLICY"),
    ("image", "other", "IMAGE_POLICY"),
    ("cap_add", ["SYS_ADMIN"], "PRIVILEGE_POLICY"),
    ("ports", [{"published": "8080"}], "NETWORK_POLICY"),
    ("depends_on", {"g3_fake": {}}, "DEPENDENCY_POLICY"),
])
def test_reject_worker_drift(key, value, reason):
    cfg = candidate()
    cfg["services"]["llm_worker"][key] = value
    assert "llm_worker:" + reason in p.inspect(cfg, "tpdfppprtest")


@pytest.mark.unit
def test_reject_lab_secrets_and_copyup():
    cfg = candidate()
    cfg["services"]["llm_worker"]["environment"]["GROQ_API_KEY"] = "secret-not-to-print"
    cfg["services"]["assembler"]["volumes"][1]["volume"]["nocopy"] = False
    cfg["services"]["g3_fake"] = deepcopy(cfg["services"]["llm_worker"])
    errors = p.inspect(cfg, "tpdfppprtest")
    assert "SERVICE_SET_DRIFT" in errors
    assert "llm_worker:OFFLINE_POLICY" in errors
    assert "assembler:VOLUME_POLICY" in errors
    assert "secret-not-to-print" not in repr(errors)


@pytest.mark.unit
def test_reject_external_volume_and_network():
    cfg = candidate()
    cfg["networks"]["chaos_net"]["internal"] = False
    cfg["volumes"]["g3_runtime_state"]["external"] = True
    assert {"NETWORK_DRIFT", "VOLUME_DEFINITION_DRIFT"} <= set(p.inspect(cfg, "tpdfppprtest"))


@pytest.mark.unit
@pytest.mark.parametrize("false_omitted", [False, True])
def test_bind_serializer_never_accepts_auto_create(false_omitted):
    cfg = candidate()
    bind = cfg["services"]["ocr_router"]["volumes"][0]["bind"]
    bind["create_host_path"] = True
    assert "ocr_router:MOUNT_POLICY" in p.inspect(
        cfg, "tpdfppprtest", false_bind_omitted=false_omitted)
    bind.pop("create_host_path")
    errors = p.inspect(cfg, "tpdfppprtest", false_bind_omitted=false_omitted)
    assert ("ocr_router:MOUNT_POLICY" not in errors) == false_omitted


@pytest.mark.unit
@pytest.mark.parametrize(("disabled", "enabled", "expected"), [
    ({}, {"create_host_path": True}, True),
    ({"create_host_path": False}, {"create_host_path": True}, False),
    ({}, {}, None),
    ({"create_host_path": True}, {"create_host_path": True}, None),
    ({"create_host_path": False}, {}, None),
])
def test_serializer_calibration(monkeypatch, disabled, enabled, expected):
    import json
    model = {"services": {
        name: {"volumes": [{"bind": bind}]}
        for name, bind in (("disabled", disabled), ("enabled", enabled))
    }}
    monkeypatch.setattr(p, "_read", lambda *_: json.dumps(model))
    if expected is None:
        with pytest.raises(ValueError, match="ambiguous"):
            p._false_bind_omitted(["docker"])
    else:
        assert p._false_bind_omitted(["docker"]) is expected
