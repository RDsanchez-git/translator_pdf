"""B03.2.4: --run resolves the runtime workspace without changing admission-only CLI."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.cli import main as cli
from apps.cli import pdf_inbox, pdf_product


@pytest.mark.parametrize("run,configured", [
    (True, True), (True, False), (False, True), (False, False),
])
def test_foreground_root_selects_app_root_only_for_run(monkeypatch, tmp_path, run, configured):
    original_root = Path(cli.__file__).resolve().parents[2]
    if configured:
        monkeypatch.setenv("APP_ROOT", str(tmp_path))
    else:
        monkeypatch.delenv("APP_ROOT", raising=False)

    observed = []
    receipt = SimpleNamespace(
        already_present=False, document_id="a" * 64,
        inbox_path=tmp_path / "data" / "inbox" / "a.pdf",
    )

    def submit(source, inbox):
        observed.append(("submit", source, inbox))
        return receipt

    def preflight(root, inbox):
        observed.append(("preflight", root, inbox))

    def process(rec, root):
        observed.append(("process", rec, root))
        return SimpleNamespace(output_pdf=tmp_path / "output.pdf")

    monkeypatch.setattr(pdf_inbox, "submit_pdf_to_inbox", submit)
    monkeypatch.setattr(pdf_product, "preflight_product_run", preflight)
    monkeypatch.setattr(pdf_product, "run_admitted_pdf", process)

    cli.handle_translate(SimpleNamespace(
        job_id=None, file_path=str(tmp_path / "source.pdf"),
        inbox_dir=None, run=run,
    ))

    expected_root = tmp_path.resolve() if run and configured else original_root
    expected_inbox = expected_root / "data" / "inbox"
    assert ("submit", tmp_path / "source.pdf", expected_inbox) in observed
    if run:
        assert ("preflight", expected_root, expected_inbox) in observed
        assert ("process", receipt, expected_root) in observed
    else:
        assert all(action[0] not in {"preflight", "process"} for action in observed)
