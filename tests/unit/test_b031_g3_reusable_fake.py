"""Pure offline tests of B03.1 fake G3 protocol, SQLite read-only and isolation."""
from contextlib import contextmanager
from hashlib import sha256
import http.client
import json
from pathlib import Path
import sqlite3
import threading

import pytest

from apps.lab.g3_fake import DUMMY_KEY, FakeServer, _compact, _resolve, FakeContractError


def _plan(*, doc="a"*64, ast="b"*64, source="Alpha $x_i$.", kind="translate"):
    member = {"node_id": "n1", "sequence_id": 1, "segment_index": 0,
              "segment_count": 1, "source_text": source, "node_type": "paragraph",
              "strategy": "translate"}
    unit = {"chunk_index": 1, "chunk_id": "chunk_01", "chunk_fingerprint": "some-fp",
            "chunk_type": kind, "source_sequence_range": [1, 1], "node_count": 1,
            "context_id": "root", "context_depth": 0, "target_payload": source,
            "payload_sha256": sha256(source.encode()).hexdigest(), "estimated_tokens": 5,
            "members": [member]}
    body = {"schema_version": 1, "document_id": doc, "ast_hash": ast, "units": [unit]}
    digest = sha256(_compact(body).encode()).hexdigest()
    return {**body, "manifest_sha256": digest}


def _install(db: Path, *plans):
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE chunk_plans (document_id TEXT, ast_hash TEXT, "
                 "manifest_json TEXT, manifest_sha256 TEXT)")
    for p in plans:
        conn.execute("INSERT INTO chunk_plans VALUES (?,?,?,?)",
                     (p["document_id"], p["ast_hash"], _compact(p), p["manifest_sha256"]))
    conn.commit()
    conn.close()


def _request(plan, *, masked="Alpha __MATH_0__."):
    m = plan["units"][0]["members"][0]
    prompt = {
        "protocol": "G3_CHUNK_RESPONSE_V1",
        "transport": {"root_key": "content",
                      "content_type": "JSON-serialized G3 response string"},
        "instructions": "Test-only: return the masked source unchanged.",
        "response_binding": {"schema_version": 1, "document_id": plan["document_id"],
                             "ast_hash": plan["ast_hash"],
                             "manifest_sha256": plan["manifest_sha256"],
                             "chunk_id": plan["units"][0]["chunk_id"]},
        "members": [{"node_id": m["node_id"], "segment_index": m["segment_index"],
                     "source_sha256": sha256(m["source_text"].encode()).hexdigest(),
                     "source_text": masked}],
    }
    return {"model": "llama3-70b-8192", "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": "G3 fixture"},
                         {"role": "user", "content": _compact(prompt)}]}


def test_valid_contract_copies_masked_text_without_model(tmp_path):
    p = _plan(); db = tmp_path/"queue.db"; _install(db,p)
    data = _resolve(_request(p), db)
    assert data["manifest_sha256"] == p["manifest_sha256"]
    assert data["members"][0]["translated_text"] == "Alpha __MATH_0__."
    assert data["members"][0]["source_sha256"] == sha256(b"Alpha $x_i$.").hexdigest()


def test_reusable_across_two_different_document_generations(tmp_path):
    p1 = _plan(); p2 = _plan(doc="c"*64, ast="d"*64, source="Second sentence.")
    db = tmp_path/"queue.db"; _install(db,p1,p2)
    assert _resolve(_request(p1), db)["document_id"] == p1["document_id"]
    assert _resolve(_request(p2, masked="Second sentence."), db)["document_id"] == p2["document_id"]


def test_rejects_preserve_unit(tmp_path):
    p = _plan(kind="preserve"); db = tmp_path/"queue.db"; _install(db,p)
    with pytest.raises(FakeContractError, match="preserve_must_not_call_provider"):
        _resolve(_request(p), db)


def test_rejects_unknown_document(tmp_path):
    p = _plan(); db = tmp_path/"queue.db"; _install(db,p)
    r = _request(p); q = json.loads(r["messages"][1]["content"])
    q["response_binding"]["document_id"] = "c"*64
    r["messages"][1]["content"] = _compact(q)
    with pytest.raises(FakeContractError, match="manifest_unavailable"):
        _resolve(r, db)


def test_rejects_member_hash_drift(tmp_path):
    p = _plan(); db = tmp_path/"queue.db"; _install(db,p)
    r = _request(p); q = json.loads(r["messages"][1]["content"])
    q["members"][0]["source_sha256"] = "0"*64
    r["messages"][1]["content"] = _compact(q)
    with pytest.raises(FakeContractError, match="source_member_identity_mismatch"):
        _resolve(r, db)


def test_rejects_corrupted_manifest_digest(tmp_path):
    p = _plan(); db = tmp_path/"queue.db"; _install(db,p)
    conn=sqlite3.connect(db);conn.execute("UPDATE chunk_plans SET manifest_sha256=?",("0"*64,));conn.commit();conn.close()
    with pytest.raises(FakeContractError,match="manifest_identity_mismatch"):
        _resolve(_request(p),db)


def test_rejects_duplicate_prompt_fields(tmp_path):
    p = _plan(); db = tmp_path/"queue.db"; _install(db,p)
    r = _request(p)
    r["messages"][1]["content"] = '{"protocol":"G3_CHUNK_RESPONSE_V1","protocol":"bad"}'
    with pytest.raises(FakeContractError, match="duplicate_json_field"):
        _resolve(r,db)


@contextmanager
def _http_server(db, max_requests=4):
    with FakeServer(("127.0.0.1",0), db, max_requests=max_requests) as server:
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            yield server.server_address[1]
        finally:
            server.shutdown();t.join(timeout=5)


def _http(port, request, token=DUMMY_KEY):
    con=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
    headers={"Content-Type":"application/json","Authorization":"Bearer "+token}
    con.request("POST","/openai/v1/chat/completions",body=_compact(request),headers=headers)
    response=con.getresponse(); data=json.loads(response.read());con.close();return response.status,data


def test_http_sdk_envelope_and_copy(tmp_path):
    p = _plan(); db=tmp_path/"queue.db";_install(db,p)
    with _http_server(db) as port:
        code,data=_http(port,_request(p))
    assert code==200
    payload=json.loads(json.loads(data["choices"][0]["message"]["content"])["content"])
    assert payload["members"][0]["translated_text"]=="Alpha __MATH_0__."


def test_http_forbids_non_dummy_token(tmp_path):
    p = _plan(); db=tmp_path/"queue.db";_install(db,p)
    with _http_server(db) as port:
        code,_=_http(port,_request(p),token="real-or-other")
    assert code==422


def test_http_limits_requests(tmp_path):
    p=_plan();db=tmp_path/"queue.db";_install(db,p)
    with _http_server(db,max_requests=1) as port:
        assert _http(port,_request(p))[0]==200
        assert _http(port,_request(p))[0]==422


def test_invalid_bind_not_loopback(tmp_path):
    db=tmp_path/"queue.db"
    with pytest.raises(ValueError,match="loopback"):
        FakeServer(("0.0.0.0",0),db)


def test_missing_database_is_read_only(tmp_path):
    db=tmp_path/"not_created.db";p=_plan()
    with pytest.raises(FakeContractError,match="queue_db_unavailable"):
        _resolve(_request(p),db)
    assert not db.exists()


def test_private_docker_bind_requires_explicit_opt_in(tmp_path, monkeypatch):
    db = tmp_path / "queue.db"
    monkeypatch.setenv("TPDF_FAKE_PRIVATE_DOCKER", "EXPLICIT_INTERNAL_NETWORK_ONLY")
    with FakeServer(("0.0.0.0", 0), db) as server:
        assert server.server_address[1] > 0


def _audit_records(capfd):
    output = capfd.readouterr().out
    return [json.loads(line) for line in output.splitlines() if line.strip()], output


def test_http_audit_success_binds_whitelisted_identity_only(tmp_path, capfd):
    p = _plan()
    db = tmp_path / "queue.db"
    _install(db, p)
    with _http_server(db) as port:
        code, _ = _http(port, _request(p))
    assert code == 200
    records, output = _audit_records(capfd)
    assert records == [
        {"event": "G3_FAKE_POST_ATTEMPT", "request_number": 1},
        {
            "event": "G3_FAKE_REQUEST_ACCEPTED",
            "request_number": 1, "status": 200,
            "document_id": p["document_id"], "ast_hash": p["ast_hash"],
            "manifest_sha256": p["manifest_sha256"],
            "chunk_id": p["units"][0]["chunk_id"],
        },
    ]
    assert DUMMY_KEY not in output
    assert "Alpha" not in output
    assert "translated_text" not in output


def test_http_audit_preserve_attempt_is_rejected_not_accepted(tmp_path, capfd):
    p = _plan(kind="preserve")
    db = tmp_path / "queue.db"
    _install(db, p)
    with _http_server(db) as port:
        code, data = _http(port, _request(p))
    assert code == 422
    assert data["error"] == "preserve_must_not_call_provider"
    records, output = _audit_records(capfd)
    assert records == [
        {"event": "G3_FAKE_POST_ATTEMPT", "request_number": 1},
        {"event": "G3_FAKE_REQUEST_REJECTED", "request_number": 1,
         "status": 422, "reason": "preserve_must_not_call_provider"},
    ]
    assert p["document_id"] not in output
    assert DUMMY_KEY not in output


def test_http_audit_unauthorized_never_exposes_untrusted_identity(tmp_path, capfd):
    p = _plan()
    db = tmp_path / "queue.db"
    _install(db, p)
    with _http_server(db) as port:
        code, _ = _http(port, _request(p), token="wrong-token")
    assert code == 422
    records, output = _audit_records(capfd)
    assert [r["event"] for r in records] == [
        "G3_FAKE_POST_ATTEMPT", "G3_FAKE_REQUEST_REJECTED",
    ]
    assert records[1]["status"] == 422
    assert "document_id" not in records[1]
    assert "chunk_id" not in records[1]
    assert p["document_id"] not in output
    assert "wrong-token" not in output


def test_http_audit_limit_logs_all_attempts_and_only_one_accept(tmp_path, capfd):
    p = _plan()
    db = tmp_path / "queue.db"
    _install(db, p)
    with _http_server(db, max_requests=1) as port:
        assert _http(port, _request(p))[0] == 200
        assert _http(port, _request(p))[0] == 422
    records, _ = _audit_records(capfd)
    assert [r["request_number"] for r in records
            if r["event"] == "G3_FAKE_POST_ATTEMPT"] == [1, 2]
    assert [r["request_number"] for r in records
            if r["event"] == "G3_FAKE_REQUEST_ACCEPTED"] == [1]
    rejects = [r for r in records if r["event"] == "G3_FAKE_REQUEST_REJECTED"]
    assert len(rejects) == 1
    assert rejects[0]["request_number"] == 2
    assert rejects[0]["reason"] == "request_limit_exceeded"
