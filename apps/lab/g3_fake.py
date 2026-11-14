"""Reusable, offline-only G3 Groq test double (never a translation provider).

The original G4 historical fake was pinned to a single manifest. This adapter
reads the current G3 ChunkPlan from a read-only SQLite connection per request,
so distinct PDF generations can be exercised independently in isolated labs.
It returns source text unchanged (after trimming segment boundaries), without
model inference. All binding identities are checked against the durable plan.

Run only inside an explicitly opted-in, network-isolated lab. By default it
binds loopback; an explicit private-Docker-only option allows another service
on the same internal network to call it (never publish the port to the host).
It does not call an external network or load live credentials.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import sqlite3
import threading
from typing import NoReturn, cast

DUMMY_KEY = "translator-pdf-g3-offline-fake-only"
PATH = "/openai/v1/chat/completions"
MAX_BODY = 2 * 1024 * 1024
_BINDING_KEYS = frozenset(("schema_version", "document_id", "ast_hash", "manifest_sha256", "chunk_id"))
_PROMPT_KEYS = frozenset(("protocol", "transport", "instructions", "response_binding", "members"))
_MEMBER_KEYS = frozenset(("node_id", "segment_index", "source_sha256", "source_text"))
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class FakeContractError(ValueError):
    """Safe error category; never include input text or tokens in responses."""


def _fail(reason: str) -> NoReturn:
    raise FakeContractError(reason)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("duplicate_json_field")
        result[key] = value
    return result


def _parse(text: str):
    return json.loads(text, object_pairs_hook=_unique,
                      parse_constant=lambda _: _fail("nonstandard_json_constant"))


def _compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _load_unit(db: Path, binding: dict):
    if not db.is_file() or db.is_symlink():
        _fail("queue_db_unavailable")
    conn = sqlite3.connect(db.resolve(strict=True).as_uri() + "?mode=ro", uri=True, timeout=8)
    try:
        conn.execute("PRAGMA query_only=ON")
        found = conn.execute(
            "SELECT manifest_json,manifest_sha256 FROM chunk_plans "
            "WHERE document_id=? AND ast_hash=?",
            (binding["document_id"], binding["ast_hash"]),
        ).fetchall()
    finally:
        conn.close()
    if len(found) != 1 or not all(type(x) is str for x in found[0]):
        _fail("manifest_unavailable_or_ambiguous")
    raw, recorded_hash = found[0]
    if len(raw.encode("utf-8")) > 8 * 1024 * 1024:
        _fail("manifest_too_large")
    manifest = _parse(raw)
    if type(manifest) is not dict or manifest.keys() != {
        "schema_version", "document_id", "ast_hash", "units", "manifest_sha256"
    }:
        _fail("invalid_manifest_fields")
    digest = _hash(_compact({k: v for k, v in manifest.items() if k != "manifest_sha256"}))
    if (type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or manifest["document_id"] != binding["document_id"]
            or manifest["ast_hash"] != binding["ast_hash"]
            or digest != binding["manifest_sha256"]
            or manifest["manifest_sha256"] != digest or recorded_hash != digest):
        _fail("manifest_identity_mismatch")
    units = manifest["units"]
    if type(units) is not list or not units or len(units) > 10000:
        _fail("invalid_manifest_units")
    matches = [u for u in units if type(u) is dict and u.get("chunk_id") == binding["chunk_id"]]
    if len(matches) != 1:
        _fail("chunk_missing_or_ambiguous")
    unit = matches[0]
    if unit.get("chunk_type") not in ("translate", "partial_translate"):
        _fail("preserve_must_not_call_provider")
    members = unit.get("members")
    if type(members) is not list or not members or len(members) > 10000:
        _fail("invalid_chunk_members")
    return unit


def _resolve(request: dict, db: Path):
    if type(request) is not dict or request.get("stream") is not False:
        _fail("invalid_http_envelope")
    if (request.get("response_format") != {"type": "json_object"}
            or type(request.get("model")) is not str or not request["model"]):
        _fail("invalid_http_envelope")
    messages = request.get("messages")
    if (type(messages) is not list or len(messages) != 2 or
            any(type(m) is not dict for m in messages) or
            [m.get("role") for m in messages] != ["system", "user"] or
            any(type(m.get("content")) is not str for m in messages)):
        _fail("invalid_http_messages")
    prompt = _parse(messages[1]["content"])
    if type(prompt) is not dict or prompt.keys() != _PROMPT_KEYS:
        _fail("invalid_g3_prompt")
    if (prompt["protocol"] != "G3_CHUNK_RESPONSE_V1" or
            prompt["transport"] != {"root_key": "content",
                                   "content_type": "JSON-serialized G3 response string"} or
            type(prompt["instructions"]) is not str):
        _fail("invalid_g3_protocol")
    binding = prompt["response_binding"]
    if type(binding) is not dict or binding.keys() != _BINDING_KEYS:
        _fail("invalid_g3_binding")
    if (type(binding["schema_version"]) is not int or binding["schema_version"] != 1 or
            any(type(binding[k]) is not str for k in _BINDING_KEYS - {"schema_version"}) or
            not all(_HEX64.fullmatch(binding[k]) for k in ("document_id", "ast_hash", "manifest_sha256")) or
            not binding["chunk_id"]):
        _fail("invalid_g3_identity")
    unit = _load_unit(db, binding)
    supplied = prompt["members"]
    expected = unit["members"]
    if type(supplied) is not list or len(supplied) != len(expected):
        _fail("member_coverage")
    seen = set()
    response_members = []
    for item, original in zip(supplied, expected):
        if (type(item) is not dict or item.keys() != _MEMBER_KEYS or
                type(original) is not dict):
            _fail("invalid_member_fields")
        source = original.get("source_text")
        if (type(source) is not str or type(item["source_text"]) is not str or
                not item["source_text"].strip() or
                type(item["node_id"]) is not str or
                type(item["segment_index"]) is not int or
                type(item["source_sha256"]) is not str or
                item["node_id"] != original.get("node_id") or
                item["segment_index"] != original.get("segment_index") or
                item["source_sha256"] != _hash(source)):
            _fail("source_member_identity_mismatch")
        key = (item["node_id"], item["segment_index"])
        if key in seen:
            _fail("duplicate_source_member")
        seen.add(key)
        # Copy masked text precisely. G3 will verify tokens and restore LaTeX.
        response_members.append({
            "node_id": item["node_id"],
            "segment_index": item["segment_index"],
            "source_sha256": item["source_sha256"],
            "translated_text": item["source_text"].strip(),
        })
    return {**binding, "members": response_members}


class FakeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, address, db: Path, *, max_requests: int = 128):
        allowed_host = (address[0] == "127.0.0.1" or
                        (address[0] == "0.0.0.0" and
                         os.getenv("TPDF_FAKE_PRIVATE_DOCKER") == "EXPLICIT_INTERNAL_NETWORK_ONLY"))
        if not allowed_host or max_requests < 1 or max_requests > 10000:
            raise ValueError("offline_fake_must_bind_loopback_or_private_docker_with_bounded_requests")
        self.db = db
        self.max_requests = max_requests
        self.requests = 0
        self.lock = threading.Lock()
        super().__init__(address, _Handler)

    def audit_post(self, event: str, request_number: int, *,
                   binding: dict | None = None, reason: str | None = None) -> None:
        """Emit one bounded, prompt-free JSON line per HTTP result.

        Identity is attached only after _resolve() verifies the plan and unit.
        Rejected requests never emit untrusted document/chunk identifiers.
        """
        record = {"event": event, "request_number": request_number}
        if binding is not None:
            record.update({key: binding[key] for key in
                           ("document_id", "ast_hash", "manifest_sha256", "chunk_id")})
            record["status"] = 200
        else:
            record["status"] = 422
            if reason is not None:
                record["reason"] = reason
        with self.lock:
            print(_compact(record), flush=True)


class _Handler(BaseHTTPRequestHandler):
    server_version = "G3ReusableOfflineFake/1.0"
    sys_version = ""

    def log_message(self, format: str, *args: object) -> None:
        pass  # Do not leak prompts, filenames or authorization values.

    def _send(self, code: int, payload: dict):
        raw = _compact(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "provider": "g3_reusable_offline_fake"})
        else:
            self._send(404, {"error": "unknown_route"})

    def do_POST(self):
        # _Handler is installed by FakeServer.__init__; BaseServer lacks these fields.
        server = cast(FakeServer, self.server)
        with server.lock:
            server.requests += 1
            request_number = server.requests
            permitted = request_number <= server.max_requests
            # Count every POST, including rejects, without logging request bodies.
            print(_compact({"event": "G3_FAKE_POST_ATTEMPT",
                            "request_number": request_number}), flush=True)
        if not permitted:
            self._send(422, {"error": "request_limit_exceeded"})
            server.audit_post("G3_FAKE_REQUEST_REJECTED", request_number,
                              reason="request_limit_exceeded")
            return
        try:
            if self.path != PATH or self.headers.get("Authorization") != "Bearer " + DUMMY_KEY:
                _fail("unauthorized_or_unknown_route")
            size = self.headers.get("Content-Length", "")
            if not size.isascii() or not size.isdecimal() or not 0 < int(size) <= MAX_BODY:
                _fail("invalid_request_length")
            raw = self.rfile.read(int(size)).decode("utf-8", "strict")
            result = _resolve(_parse(raw), server.db)
            response = _compact({"content": _compact(result)})
            self._send(200, {
                "id": "chatcmpl-g3-reusable-offline", "object": "chat.completion",
                "created": 0, "model": "llama3-70b-8192",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": response},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            })
            server.audit_post("G3_FAKE_REQUEST_ACCEPTED", request_number, binding=result)
        except (ValueError, TypeError, KeyError, UnicodeError, sqlite3.Error, RecursionError) as exc:
            reason = str(exc) if isinstance(exc, FakeContractError) else "invalid_request"
            self._send(422, {"error": reason})
            server.audit_post("G3_FAKE_REQUEST_REJECTED", request_number, reason=reason)


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict reusable G3 fake; never a translation model")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        print("G3_REUSABLE_FAKE_V1")
        return
    if not args.serve:
        parser.error("--serve or --version required")
    if os.getenv("TPDF_OFFLINE_LAB") != "EXPLICIT_OFFLINE_TEST_ONLY":
        raise SystemExit("G3_FAKE_EXPLICIT_LAB_OPT_IN_REQUIRED")
    if os.getenv("GROQ_API_KEY") != DUMMY_KEY:
        raise SystemExit("G3_FAKE_REAL_OR_MISSING_CREDENTIAL_FORBIDDEN")
    path = Path(os.getenv("TPDF_FAKE_QUEUE_DB", ""))
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise SystemExit("G3_FAKE_QUEUE_DB_MISSING")
    max_requests = int(os.getenv("TPDF_FAKE_MAX_REQUESTS", "128"))
    host = os.getenv("TPDF_FAKE_BIND", "127.0.0.1")
    with FakeServer((host, 8080), path, max_requests=max_requests) as srv:
        print("G3_REUSABLE_FAKE_LISTENING_PRIVATE_LAB", flush=True)
        srv.serve_forever()


if __name__ == "__main__":
    main()
