"""Fail-closed synthetic scope, no Docker or commercial I/O."""
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
import asyncio
import json

import pytest

from apps.lab import pppr_offline_scope as lab
from core.execution.exceptions import G3ExternalEffectNotStartedError


@pytest.fixture
def isolated(monkeypatch):
    for key in lab._FORBIDDEN_ENV:
        monkeypatch.delenv(key, raising=False)
    for key, value in {
        "TPDF_OFFLINE_LAB": lab.OPT_IN, "GROQ_API_KEY": lab.DUMMY_KEY,
        "GROQ_BASE_URL": lab.ENDPOINT, "IS_BENCHMARK": "0",
        "APP_ROOT": "/app", "SQLITE_STATE_DIR": "/app/state",
        "COMPILER_OUTPUT_DIR": "/app/output",
        "TIKTOKEN_CACHE_DIR": "/app/data/tiktoken-cache",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(lab.sys, "platform", "linux")
    for key in ("getuid", "geteuid", "getgid", "getegid"):
        monkeypatch.setattr(lab.os, key, lambda: 10001, raising=False)
    monkeypatch.setattr(lab.socket, "if_nameindex", lambda: [(1, "lo")])
    status = "CapEff: 0\nCapPrm: 0\nCapBnd: 0\nNoNewPrivs: 1"
    mounts = "\n".join(
        f"1 2 0:1 / {path} {mode} - tmpfs tmpfs {mode}"
        for path, mode in (
            ("/workspace", "ro"), ("/app/state", "rw"), ("/app/data", "rw"),
            ("/app/output", "rw"), ("/app/.cache/tectonic", "rw"),
        )
    )
    monkeypatch.setattr(Path, "read_text", lambda self: status if self.name == "status" else mounts)
    return lab.OfflineLabScope("a" * 64)


@pytest.mark.unit
def test_scope_is_immutable_and_distinct_from_product(isolated):
    from runtime.engine import _product_effective_config_sha256
    isolated.validate("a" * 64)
    assert isolated.root_config_sha256 != _product_effective_config_sha256()
    with pytest.raises(FrozenInstanceError):
        isolated.document_id = "b" * 64
    with pytest.raises(G3ExternalEffectNotStartedError, match="DOCUMENT_SCOPE"):
        isolated.validate("b" * 64)


@pytest.mark.unit
@pytest.mark.parametrize("key,value", [
    ("TPDF_OFFLINE_LAB", ""), ("GROQ_API_KEY", "not-dummy"),
    ("GROQ_BASE_URL", "https://example.invalid"), ("IS_BENCHMARK", "1"),
    ("SQLITE_STATE_DIR", "/other"), ("HTTPS_PROXY", "http://proxy.invalid"),
    ("OPENAI_API_KEY", "not-authorized"), ("TPDF_C0_VOLUME_INIT", "1"),
])
def test_environment_drift_rejected(isolated, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(G3ExternalEffectNotStartedError, match="ENVIRONMENT_REJECTED"):
        isolated.validate(isolated.document_id)


@pytest.mark.unit
@pytest.mark.parametrize("drift", ["interface", "uid", "capability", "mount"])
def test_isolation_drift_rejected(isolated, monkeypatch, drift):
    if drift == "interface":
        monkeypatch.setattr(lab.socket, "if_nameindex", lambda: [(1, "lo"), (2, "eth0")])
    elif drift == "uid":
        monkeypatch.setattr(lab.os, "geteuid", lambda: 0)
    else:
        original = Path.read_text
        def changed(self):
            value = original(self)
            return value.replace("CapEff: 0", "CapEff: 1") if drift == "capability" else value.replace("/workspace ro", "/workspace rw")
        monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(G3ExternalEffectNotStartedError, match="ISOLATION_REQUIRED"):
        isolated.validate(isolated.document_id)


@pytest.mark.unit
def test_env_opt_in_alone_never_selects_runtime(isolated, monkeypatch):
    from runtime import engine
    def forbidden(*args, **kwargs):
        pytest.fail("DB opened before explicit scope")
    monkeypatch.setattr(engine, "get_connection", forbidden)
    with pytest.raises(G3ExternalEffectNotStartedError, match="EXPLICIT_SCOPE_REQUIRED"):
        engine.run_pipeline(isolated.document_id, "b" * 64)


@pytest.mark.unit
@pytest.mark.parametrize("model,document,target", [
    ("commercial-model", "a" * 64, "primary"),
    (lab.FAKE_MODEL, "b" * 64, "primary"),
    (lab.FAKE_MODEL, "a" * 64, "fallback_large_window"),
])
def test_transport_selection_rejected_before_client(isolated, monkeypatch, model, document, target):
    import groq
    def forbidden(*args, **kwargs):
        pytest.fail("SDK constructed before validation")
    monkeypatch.setattr(groq, "AsyncGroq", forbidden)
    provider = lab.OfflineLoopbackProvider(isolated)
    envelope = SimpleNamespace(
        model_name=model, target_provider=target,
        schema=SimpleNamespace(payload=SimpleNamespace(content=json.dumps({
            "response_binding": {"document_id": document},
        }))),
    )
    with pytest.raises(G3ExternalEffectNotStartedError):
        asyncio.run(provider.translate(envelope))
