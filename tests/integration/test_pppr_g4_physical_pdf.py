"""W4.2 physical witnesses: synthetic source, real parser/G3/G5 and Tectonic.

Only inference transport is fake. No private corpus, credentials or paid calls.
The typed G5 witness is intentionally separate from extraction capabilities.
"""
from contextlib import closing
from hashlib import sha256
from io import BytesIO
from math import isfinite
import os
from pathlib import Path
import shutil
import sqlite3
import sys

import fitz
import pytest
from PIL import Image

from apps.cli import main as cli
from apps.compiler.__main__ import RenderGeometryAdapter
from apps.compiler.tectonic_runner import HostTectonicRunner
from apps.compiler.tex_builder import TexBuilder
from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.hashing import compute_ast_hash
from core.ast.models import HeadingPayload, ImagePayload, TranslationTaskType
from core.ast.registry import ASTRegistry
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.models import RenderUnit
from core.document_profile.models import InferredDocumentProfile, PageLayout
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.control_repo import ControlPlaneRepository
from tests.integration.test_w08_cli_foreground_single_generation_offline import (
    _OfflineProvider, _install_offline_provider, _prepare_workspace,
)


# The normal local suite remains usable without a native compiler. The CI
# physical step explicitly sets this flag and MUST fail if Tectonic is absent.
pytestmark = pytest.mark.integration


@pytest.fixture
def require_physical_compiler():
    required = os.getenv("PPPR_G4_REQUIRE_PHYSICAL_PDF") == "1"
    if shutil.which("tectonic") is None:
        if required:
            pytest.fail("PPPR_G4_PHYSICAL_TECTONIC_UNAVAILABLE")
        pytest.skip("Physical G5 witness requires Tectonic on PATH")


_HEADINGS = (
    ("1 Methods", "1 Métodos", HeadingLevel.H1),
    ("1.1 Data", "1.1 Datos", HeadingLevel.H2),
    ("1.1.1 Samples", "1.1.1 Muestras", HeadingLevel.H3),
)
_BODY = (
    ("The sample contains measured values.", "La muestra contiene valores medidos."),
    ("The dataset contains independent observations.", "El conjunto contiene observaciones independientes."),
    ("The experiment measures the response.", "El experimento mide la respuesta."),
)


def _source_pdf(path: Path) -> None:
    # Explicitly numbered headings are the supported hierarchy witness.
    # Body dominates typography statistics; headings are distinct blocks.
    # All blocks are away from page margins and title-classification region.
    with fitz.open() as document:
        page = document.new_page(width=500, height=800)
        for i, ((source, _, _), (body, _)) in enumerate(zip(_HEADINGS, _BODY, strict=True)):
            y = 150 + i * 105
            page.insert_text((35, y), source, fontname="hebo", fontsize=13)
            page.insert_text((35, y + 38), body, fontname="helv", fontsize=10)
        # A real embedded raster with a nonwhite, asymmetric pattern.
        image = Image.new("RGB", (80, 40), "white")
        image.paste((20, 100, 180), (0, 0, 40, 40))
        image.paste((180, 50, 20), (40, 0, 80, 20))
        stream = BytesIO()
        image.save(stream, format="PNG")
        page.insert_image(fitz.Rect(35, 480, 195, 560), stream=stream.getvalue())
        document.save(path)


def _physical_heading_size(lines: list[dict], expected: str) -> float:
    """Locate one complete physical line, independent of PDF font-run splits.

    A span is an extractor grouping, not a structural heading boundary.
    Do not join separate lines or allow a substring in unrelated prose.
    The short, single-line synthetic headings must have a consistent size.
    """
    matches = [
        line for line in lines
        if "".join(span["text"] for span in line["spans"]).strip() == expected
    ]
    assert len(matches) == 1, (
        f"Expected one physical heading line {expected!r}, got {len(matches)}; "
        f"observed lines={[''.join(s['text'] for s in l['spans']) for l in lines]!r}"
    )
    sizes = [
        float(span["size"]) for span in matches[0]["spans"]
        if span["text"].strip()
    ]
    assert sizes and all(isfinite(size) and size > 0 for size in sizes), (
        f"Invalid physical heading sizes for {expected!r}: {sizes!r}"
    )
    # PDF point rounding is allowed, not a mix of heading and body sizes.
    assert max(sizes) - min(sizes) <= 0.05, (
        f"Inconsistent physical heading sizes for {expected!r}: {sizes!r}"
    )
    return min(sizes)


def test_heading_oracle_accepts_fragmented_same_size_font_runs() -> None:
    lines = [{"spans": [
        {"text": "1 M", "size": 14.35},
        {"text": "é", "size": 14.34},
        {"text": "todos", "size": 14.35},
    ]}]
    assert _physical_heading_size(lines, "1 Métodos") == pytest.approx(14.34)


@pytest.mark.parametrize("runs", [
    [[("1 M", 14.35), ("étodos", 10.95)]],  # inconsistent size
    [[("1 M", 14.35)], [("étodos", 14.35)]],  # different physical lines
    [[("Prefix 1 Métodos", 14.35)]],  # substring only
    [[("1 Métodos", 14.35)], [("1 Métodos", 14.35)]],  # ambiguous duplicate
    [[("1 Métodos", float("nan"))]],  # nonfinite geometry
])
def test_heading_oracle_rejects_unverified_correspondence(runs) -> None:
    lines = [
        {"spans": [{"text": text, "size": size} for text, size in run]}
        for run in runs
    ]
    with pytest.raises(AssertionError):
        _physical_heading_size(lines, "1 Métodos")


@pytest.mark.usefixtures("require_physical_compiler")
def test_real_source_to_selected_translation_to_physical_pdf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _prepare_workspace(tmp_path, monkeypatch)
    source = tmp_path / "source.pdf"
    _source_pdf(source)
    document_id = sha256(source.read_bytes()).hexdigest()
    translations = {source: target for source, target, _ in _HEADINGS}
    translations.update(dict(_BODY))
    provider = _OfflineProvider(translations)
    _install_offline_provider(monkeypatch, provider)

    # No parser/compiler monkeypatches: use the actual public CLI composition.
    monkeypatch.setattr(sys, "argv", ["apps.cli.main", "translate", str(source), "--run"])
    cli.main()

    with (
        closing(sqlite3.connect(state / "fsm.db")) as fsm,
        closing(sqlite3.connect(state / "queue.db")) as queue,
        closing(sqlite3.connect(state / "materialized.db")) as materialized,
    ):
        row = fsm.execute(
            "SELECT ast_hash,current_state,is_terminal FROM document_fsm WHERE document_id=?",
            (document_id,),
        ).fetchone()
        assert row is not None and row[1:] == ("COMPLETED", 1)
        ast_hash = row[0]
        ast = ASTRegistry(workspace_dir=str(tmp_path)).get_verified_document_ast(document_id, ast_hash)
        assert compute_ast_hash(ast) == ast_hash
        headings = [n for n in ast if n.node_type == ContentNodeType.HEADING]
        assert [
            (n.payload.content, n.payload.heading_level)
            for n in headings if isinstance(n.payload, HeadingPayload)
        ] == [(source, level) for source, _, level in _HEADINGS]
        images = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
        assert len(images) == 1
        image = images[0]
        assert isinstance(image.payload, ImagePayload)
        asset = image.payload.asset_path
        assert asset is not None
        assert len(image.metadata.physical_regions) == 1
        region = image.metadata.physical_regions[0]
        assert region.page_number == 1
        assert (region.page_width, region.page_height) == (500, 800)
        geometry = RenderGeometryAdapter().extract(image)
        assert geometry is not None
        assert geometry.relative_width == pytest.approx(160 / 500)
        assert geometry.relative_height == pytest.approx(80 / 800)

        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(queue)
        ).load_verified(document_id, ast_hash, ast)
        inference = [u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE]
        preserved = [u for u in plan.units if u.chunk_type == TranslationTaskType.PRESERVE]
        assert {m.node_id for u in preserved for m in u.members} == {image.node_id}
        assert {chunk for chunk, _ in provider.calls} == {u.chunk_id for u in inference}
        assert len(provider.calls) == len(inference)
        for node in headings:
            selected = [u for u in inference if any(m.node_id == node.node_id for m in u.members)]
            assert len(selected) == 1
            assert selected[0].context_id in snapshots

        projections = dict(materialized.execute(
            "SELECT node_id,normalized_response FROM valid_chunks_cache WHERE document_id=? AND ast_hash=?",
            (document_id, ast_hash),
        ).fetchall())
        for node, (_, target, _) in zip(headings, _HEADINGS, strict=True):
            assert projections[node.node_id] == target
        assert projections[image.node_id] == asset
        assert set(projections.values()) == set(translations.values()) | {asset}
        assert materialized.execute(
            "SELECT manifest_sha256 FROM g3_plan_publications WHERE document_id=? AND ast_hash=?",
            (document_id, ast_hash),
        ).fetchone() == (plan.digest,)

    result = tmp_path / "output" / f"translated_{document_id}.pdf"
    assert result.is_file()
    with fitz.open(result) as compiled:
        assert compiled.page_count >= 1
        text = "\n".join(page.get_text() for page in compiled)
        lines = [
            line
            for page in compiled
            for block in page.get_text("dict")["blocks"]
            if block["type"] == 0
            for line in block["lines"]
        ]
        heading_sizes = []
        for original, translated, _ in _HEADINGS:
            assert original not in text
            assert translated in text
            heading_sizes.append(_physical_heading_size(lines, translated))
        assert heading_sizes[0] > heading_sizes[1] > heading_sizes[2]
        for original, translated in _BODY:
            assert original not in text
            assert translated in " ".join(text.split())
        embedded = [
            image for page in compiled for image in page.get_image_info()
        ]
        assert len(embedded) == 1
        assert (embedded[0]["width"], embedded[0]["height"]) == (80, 40)
        x0, y0, x1, y1 = embedded[0]["bbox"]
        assert (x1 - x0) / (y1 - y0) == pytest.approx(2.0, rel=0.02)


@pytest.mark.usefixtures("require_physical_compiler")
def test_typed_protected_content_and_math_survive_real_compilation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Separate G5 witness: the physical parser is NOT claimed to recover
    # arbitrary CODE/TABLE structures from untagged source PDFs.
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    units = [
        RenderUnit("code", ContentNodeType.CODE, "value_1 = 5% & $"),
        RenderUnit("table", ContentNodeType.TABLE_SIMPLE, "left_col & right_col"),
        RenderUnit("math", ContentNodeType.PARAGRAPH, r"Formula $x^2+1$."),
    ]
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    tex = TexBuilder(RenderContextFactory.create(profile)).build(units)
    assert r"$x^2+1$" in tex
    result = HostTectonicRunner().compile(tex, output_dir=str(tmp_path))
    with fitz.open(result) as compiled:
        text = " ".join(" ".join(page.get_text().split()) for page in compiled)
        assert "value_1 = 5% & $" in text
        assert "left_col & right_col" in text
        assert "Formula" in text
        assert "$x^2+1$" not in text
        assert "x" in text and "2" in text and "+ 1" in text.replace("+1", "+ 1")
