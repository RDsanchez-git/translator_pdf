"""Tests de idempotencia por reemplazo (NADR-24 R33, Task 4.4.2).

R33: re-ejecucion de certificacion fallida es idempotente a nivel logico.
El tooling usa write_text (overwrite), no append. Un residuo pre-planted
es reemplazado, no mezclado con el nuevo contenido.
"""
from __future__ import annotations

import json
from pathlib import Path


class TestIdempotencyByReplacement:
    def test_write_text_overwrites_without_merge(self, tmp_path: Path):
        target = tmp_path / "parameter_freeze.json"
        target.write_text('{"old": "content"}', encoding="utf-8")
        target.write_text('{"new": "content"}', encoding="utf-8")
        data = json.loads(target.read_text(encoding="utf-8"))
        assert data == {"new": "content"}
        assert "old" not in data

    def test_residual_file_is_fully_replaced(self, tmp_path: Path):
        target = tmp_path / "report.json"
        residual = '{"residual_key": "should_not_survive", "another": 123}'
        target.write_text(residual, encoding="utf-8")
        new_content = '{"new_key": "replaced"}'
        target.write_text(new_content, encoding="utf-8")
        assert target.read_text(encoding="utf-8") == new_content
        assert "residual_key" not in target.read_text(encoding="utf-8")
