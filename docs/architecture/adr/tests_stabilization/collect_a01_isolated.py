#!/usr/bin/env python3
"""Prepare an independent Git clone and optionally collect pytest metadata.

Not a security sandbox: separate filesystem and sanitized Python env are not
OS-enforced filesystem/network isolation. Never run untrusted repository code.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

REVISION = "refs/remotes/origin/tests_stabilization"
MODES: tuple[tuple[str, str | None], ...] = (
    ("all", None),
    ("unit", "unit"),
    ("integration_nonregression", "integration and not regression"),
    ("technical", "not e2e"),
)

PLUGIN_SOURCE = '''"""Observational pytest plugin used for --collect-only, never test execution."""
import json
import os
from pathlib import Path


def pytest_collection_finish(session):
    items = []
    for item in session.items:
        marks = sorted(set(m.name for m in item.iter_markers()))
        callspec = getattr(item, "callspec", None)
        items.append({
            "nodeid": item.nodeid,
            "markers": marks,
            "parameter_id": getattr(callspec, "id", None),
            "skip_or_xfail_mark_declared": any(
                name in {"skip", "skipif", "xfail"} for name in marks
            ),
        })
    output = Path(os.environ["A01_COLLECTION_JSON"])
    output.write_text(
        json.dumps({"count": len(items), "items": items}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
'''

SOCKET_GUARD_SOURCE = '''"""Best-effort Python socket guard; NOT an OS/network security boundary."""
import socket


def _blocked(*args, **kwargs):
    raise OSError("A01_ISOLATED_COLLECTION_NETWORK_CONNECTION_BLOCKED")


socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
socket.create_connection = _blocked
'''


def git(*args: str, cwd: Path | None = None) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"Git command failed (exit={result.returncode}): {command!r}; "
            f"stderr={result.stderr.strip()[:1500]}"
        )
    return result.stdout.strip()


def inside(root: Path, maybe_child: Path) -> bool:
    try:
        maybe_child.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def flagged_calls(text: str, name: str) -> list[dict[str, Any]]:
    """Index AST calls, not observed runtime effects.

    Scope/phase are hints only. A function can be invoked by import-time code.
    """
    try:
        tree = ast.parse(text, filename=name)
    except SyntaxError as exc:
        return [{"line": exc.lineno, "signal": "syntax_error", "detail": str(exc)}]
    signals = {
        "remove", "unlink", "rmtree", "write_text", "write_bytes",
        "mkdir", "makedirs", "connect", "Popen", "run", "system",
        "call", "check_output", "replace", "rename", "dump", "save",
        "post", "get", "urlopen", "open",
    }
    hits: list[dict[str, Any]] = []

    class CallScanner(ast.NodeVisitor):
        def __init__(self) -> None:
            self.scopes: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            # Decorators/default expressions are evaluated at definition time,
            # unlike the function body. Preserve that distinction for triage.
            for expr in node.decorator_list:
                self.visit(expr)
            for expr in (*node.args.defaults, *node.args.kw_defaults):
                if expr is not None:
                    self.visit(expr)
            self.scopes.append(f"function:{node.name}")
            for stmt in node.body:
                self.visit(stmt)
            self.scopes.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for expr in node.decorator_list:
                self.visit(expr)
            for expr in node.bases:
                self.visit(expr)
            for expr in node.keywords:
                self.visit(expr.value)
            self.scopes.append(f"class:{node.name}")
            for stmt in node.body:
                self.visit(stmt)
            self.scopes.pop()

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for expr in (*node.args.defaults, *node.args.kw_defaults):
                if expr is not None:
                    self.visit(expr)
            self.scopes.append("lambda")
            self.visit(node.body)
            self.scopes.pop()

        def visit_Call(self, node: ast.Call) -> None:
            func = node.func
            if isinstance(func, ast.Name):
                method = func.id
            elif isinstance(func, ast.Attribute):
                method = func.attr
            else:
                method = None
            if method in signals:
                deferred = any(
                    scope.startswith("function:") or scope == "lambda"
                    for scope in self.scopes
                )
                hits.append({
                    "line": node.lineno,
                    "signal": method,
                    "callee": ast.unparse(func)[:180],
                    "scope": ".".join(self.scopes) or "module",
                    "phase_hint": "function_body" if deferred else "definition_time",
                })
            self.generic_visit(node)

    CallScanner().visit(tree)
    return hits


def child_environment(repo: Path, scratch: Path, helpers: Path) -> dict[str, str]:
    # Pass only essential runtime configuration; do not forward API tokens,
    # application credentials, private HOME/APPDATA or arbitrary secrets.
    keys = (
        "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "LANG",
        "LC_ALL", "PYTHONIOENCODING", "VIRTUAL_ENV", "NUMBER_OF_PROCESSORS",
        "SSL_CERT_FILE", "SSL_CERT_DIR",
    )
    env = {k: os.environ[k] for k in keys if k in os.environ}
    for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CACHE_HOME",
                "XDG_CONFIG_HOME", "TMP", "TEMP", "TMPDIR"):
        folder = scratch / "child_home" / key.lower()
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    env["PYTHONPATH"] = os.pathsep.join((str(helpers), str(repo)))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTEST_ADDOPTS"] = ""
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("--collect", action="store_true", help="Opt in to importing tests for pytest --collect-only; default is prepare-only.")
    parser.add_argument("--timeout", type=int, default=240, help="Timeout per collection selection in seconds (default 240).")
    args = parser.parse_args(argv)
    source = Path(git("-C", str(args.repo_root), "rev-parse", "--show-toplevel")).resolve()
    if not (source / "pyproject.toml").is_file():
        raise RuntimeError("Source lacks pyproject.toml; select the repository root")
    original_status = git("-C", str(source), "status", "--porcelain=v1")
    sha = git("-C", str(source), "rev-parse", f"{args.revision}^{{commit}}")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise RuntimeError("Unable to pin a 40-character commit SHA")
    scratch = Path(tempfile.mkdtemp(prefix="translator-a01-isolated-", dir=tempfile.gettempdir())).resolve()
    if inside(source, scratch) or inside(scratch, source):
        raise RuntimeError("Isolation failure: scratch overlaps the source repository")
    repo = scratch / "repo"
    reports = scratch / "reports"
    helpers = scratch / "helpers"
    reports.mkdir()
    helpers.mkdir()
    git("clone", "--no-hardlinks", "--no-checkout", str(source), str(repo))
    git("-C", str(repo), "fetch", "--no-tags", str(source), args.revision)
    git("-C", str(repo), "checkout", "--detach", "FETCH_HEAD")
    if git("-C", str(repo), "rev-parse", "HEAD") != sha:
        raise RuntimeError("Isolated checkout SHA differs from source's remote-tracking ref")
    git("-C", str(repo), "remote", "remove", "origin")
    empty_hooks = scratch / "empty-hooks"
    empty_hooks.mkdir()
    git("-C", str(repo), "config", "core.hooksPath", str(empty_hooks))

    signals: list[dict[str, Any]] = []
    files = sorted((repo / "tests").rglob("*.py"))
    for p in files:
        rel = p.relative_to(repo).as_posix()
        # Only the scanner's in-memory decoding strips UTF-8 BOM; never change tests.
        for hit in flagged_calls(p.read_text(encoding="utf-8-sig"), rel):
            signals.append({"file": rel, **hit})

    manifest: dict[str, Any] = {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": "RDsanchez-git/translator_pdf",
        "revision_ref": args.revision,
        "revision_sha": sha,
        "python_executable": sys.executable,
        "scratch": str(scratch),
        "source_worktree_status_was_nonempty": bool(original_status),
        "source_worktree_status_preserved_by_design": True,
        "tests_python_files_examined": len(files),
        "scanner_version": "a05-static-v2-bom-callee-scope",
        "static_parse_errors": sum(x["signal"] == "syntax_error" for x in signals),
        "static_calls_in_definition_context": sum(
            x.get("phase_hint") == "definition_time" for x in signals
        ),
        "static_call_signals": len(signals),
        "collection_requested": args.collect,
        "network_isolation": "best-effort Python socket guard only; NOT OS-level isolation",
        "filesystem_isolation": "separate clone and env directory, not an OS-enforced sandbox",
        "modes": {},
    }
    (reports / "static_signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")
    print(f"Original repo: {source}")
    print(f"Isolated copy: {repo}")
    print(f"Pinned revision: {sha}")
    print(f"Python files statically scanned: {len(files)}; signals: {len(signals)}")
    print(f"Static AST parse errors: {manifest['static_parse_errors']}")
    if not args.collect:
        (reports / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print("PREPARED ONLY: no Python test imports, no pytest collection, no test execution.")
        print(f"Reports: {reports}")
        return 0

    (helpers / "a01_pytest_inventory_plugin.py").write_text(PLUGIN_SOURCE, encoding="utf-8")
    (helpers / "sitecustomize.py").write_text(SOCKET_GUARD_SOURCE, encoding="utf-8")
    env = child_environment(repo, scratch, helpers)
    failures = 0
    for name, expr in MODES:
        output_json = reports / f"{name}.json"
        args_pytest = [
            sys.executable, "-m", "pytest", "--collect-only", "-q",
            "-o", "addopts=", "--strict-markers", "--strict-config",
            "-p", "no:cacheprovider", "-p", "a01_pytest_inventory_plugin",
        ]
        if expr is not None:
            args_pytest += ["-m", expr]
        args_pytest += ["tests"]
        env["A01_COLLECTION_JSON"] = str(output_json)
        try:
            result = subprocess.run(args_pytest, cwd=repo, env=env,
                                    capture_output=True, text=True,
                                    timeout=args.timeout, check=False,
                                    encoding="utf-8", errors="replace")
            (reports / f"{name}.log").write_text(result.stdout + "\n--- STDERR ---\n" + result.stderr,
                                                     encoding="utf-8")
            code = result.returncode
        except subprocess.TimeoutExpired:
            (reports / f"{name}.log").write_text("Collection timed out; investigate unsafe import.\n", encoding="utf-8")
            code = 124
        count = None
        if output_json.exists():
            try:
                count = json.loads(output_json.read_text(encoding="utf-8"))["count"]
            except (ValueError, KeyError):
                pass
        manifest["modes"][name] = {"selector": expr or "ALL", "exit_code": code,
                                   "selected_nodes_reported": count}
        print(f"COLLECT {name}: exit={code}, nodes={count}, log={reports / (name + '.log')}")
        if code != 0:
            failures += 1
            break  # Do not repeat imports if the first collection failed.
    (reports / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Reports: {reports}")
    print("The isolated copy is intentionally retained for inspection; no cleanup was run.")
    if failures:
        print("COLLECTION INCOMPLETE: inspect the logs before interpreting any node counts.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"A01_ISOLATION_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(3)
