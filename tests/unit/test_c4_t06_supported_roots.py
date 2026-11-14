"""C4/T06: pure source checks for the supported PDF->PDF product entrypoints.

No import of the application, execution, HTTP, Docker, SQLite, PDF or temp files.
Legacy libraries remain available to historical benchmarks/tests; this only
proves they are not started by the supported CLI/Compose/Docker roots in Git.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _tree(relative: str) -> ast.Module:
    return ast.parse((ROOT / relative).read_text(encoding="utf-8"), filename=relative)


def _def(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    functions = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    assert len(functions) == 1, (name, len(functions))
    return functions[0]


def test_t06_cli_never_imports_or_dispatches_r1_executor():
    tree = _tree("apps/cli/main.py")
    imports = [
        name.name
        for statement in ast.walk(tree)
        if isinstance(statement, ast.Import)
        for name in statement.names
    ] + [
        statement.module or ""
        for statement in ast.walk(tree)
        if isinstance(statement, ast.ImportFrom)
    ]
    assert not any(
        name == "core.pipeline.orchestrator"
        or name in (
            "core.pipeline.job", "apps.llm_workers.dispatcher",
            "apps.cli.legacy_translate_async",
        )
        for name in imports
    )
    calls = [
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "build_pipeline" not in calls
    assert "TranslationPipeline" not in calls
    assert "AsyncDispatcher" not in calls

    legacy = _def(tree, "handle_translate_async")
    assert len(legacy.body) == 2  # docstring + fail-closed
    assert isinstance(legacy.body[-1], ast.Raise)
    assert "C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED" in ast.unparse(legacy.body[-1])

    parser = _def(tree, "parse_arguments")
    registrations = [
        call for call in ast.walk(parser)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
        and call.func.attr == "set_defaults"
    ]
    assert len(registrations) == 4
    handlers = {
        kw.value.id
        for call in registrations for kw in call.keywords
        if kw.arg == "func" and isinstance(kw.value, ast.Name)
    }
    assert handlers == {
        "handle_translate", "handle_sweep", "handle_resume", "handle_status",
    }
    assert "handle_translate_async" not in handlers
    assert "run_admitted_pdf" in (ROOT / "apps/cli/main.py").read_text(encoding="utf-8")
    historical = _tree("apps/cli/legacy_translate_async.py")
    assert _def(historical, "handle_translate_async")
    assert "build_pipeline" in (
        ROOT / "apps/cli/legacy_translate_async.py"
    ).read_text(encoding="utf-8")


def test_t06_supported_launchers_select_engine_not_r3():
    compose_base = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    compose_runtime = (ROOT / "docker-compose.runtime.yml").read_text(encoding="utf-8")
    compose_lab = (ROOT / "docker-compose.convergence-lab.yml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    launchers = (compose_base, compose_runtime, compose_lab, dockerfile)
    assert all("apps/llm_workers/__main__.py" not in source for source in launchers)
    assert "runtime/engine.py" in compose_base
    assert "runtime/engine.py" in compose_lab
    assert 'CMD ["python", "runtime/engine.py"]' in dockerfile
    assert 'translator-pdf = "apps.cli.main:main"' in project
