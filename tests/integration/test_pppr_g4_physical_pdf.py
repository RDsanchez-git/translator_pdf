"""W4.2 physical witnesses: synthetic source, real parser/G3/G5 and Tectonic.

Only inference transport is fake. No private corpus, credentials or paid calls.
The typed G5 witness is intentionally separate from extraction capabilities.
"""
from contextlib import closing
from hashlib import sha256
from math import isfinite
import os
from pathlib import Path
import shutil
import sqlite3
import sys

import fitz
import pytest

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
    # The physical witness now exercises the actual operational LAB generator,
    # not a parallel fixture that could diverge from the owner execution.
    from apps.lab.offline_pdf_lab import _smoke_source
    _smoke_source(path)


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


def test_historical_lab_title_remains_unverified_and_rejected(tmp_path: Path) -> None:
    """Replay the original source classification and G5 rejection, without I/O to G3."""
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline

    source = tmp_path / "historical_smoke.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=595, height=842)
        page.insert_text((62, 88), "Scientific translation pipeline operational test", fontsize=16)
        sentences = (
            "The scientific method relies on observable evidence and careful measurement.",
            "Researchers record observations before drawing conclusions from the data.",
            "A reproducible process makes it easier to compare results across teams.",
            "This document is a laboratory fixture and contains no protected equations.",
        )
        for i, sentence in enumerate(sentences):
            page.insert_text((62, 145 + 41 * i), sentence, fontsize=11)
        doc.save(str(source))

    ast = build_extraction_pipeline().parse(str(source))
    headings = [node for node in ast if node.node_type == ContentNodeType.HEADING]
    assert len(headings) == 1
    heading = headings[0]
    assert isinstance(heading.payload, HeadingPayload)
    assert heading.payload.content == "Scientific translation pipeline operational test"
    assert heading.payload.heading_level == HeadingLevel.UNKNOWN
    unit = RenderUnit(
        node_id=heading.node_id, node_type=ContentNodeType.HEADING,
        content=heading.payload.content, heading_level=heading.payload.heading_level,
    )
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    with pytest.raises(ValueError, match="PPPR_G4_HEADING_LEVEL_UNVERIFIED"):
        TexBuilder(RenderContextFactory.create(profile)).build([unit])


def _df01_isolated_synthetic_figure() -> bytes:
    """Known boundary, not a detector. Test-only feasibility fixture.

    A show_pdf_page clip alone can retain exterior objects in PDF streams.
    Remove exterior marks on a disposable one-page copy before setting its
    crop box, then check the actual isolated visual and text. No claim about
    arbitrary PDFs or an exhaustive sanitization algorithm.
    """
    region = fitz.Rect(75, 75, 225, 185)
    with fitz.open() as source, fitz.open() as isolated:
        original = source.new_page(width=300, height=300)
        original.insert_text((20, 30), "EXTERNALBEFORE")
        original.draw_rect(fitz.Rect(80, 80, 220, 180))
        original.draw_line((90, 150), (200, 100))
        original.insert_text((110, 120), "FIGURELABEL")
        original.insert_text((20, 250), "EXTERNALAFTER")
        isolated.insert_pdf(source, from_page=0, to_page=0, links=False, annots=False, widgets=False)
        page = isolated[0]
        for exterior in (
            fitz.Rect(0, 0, 300, 75), fitz.Rect(0, 185, 300, 300),
            fitz.Rect(0, 75, 75, 185), fitz.Rect(225, 75, 300, 185),
        ):
            page.add_redact_annot(exterior, fill=False, cross_out=False)
        assert page.apply_redactions(images=1, graphics=2, text=0)
        page.set_cropbox(region)
        data = isolated.tobytes(garbage=4, clean=True, deflate=True, no_new_id=True)
        original_pixels = original.get_pixmap(clip=region, matrix=fitz.Matrix(2, 2))
        with fitz.open(stream=data, filetype="pdf") as reopened:
            assert len(reopened) == 1
            cropped = reopened[0]
            assert cropped.rect.width == 150 and cropped.rect.height == 110
            cropped_pixels = cropped.get_pixmap(matrix=fitz.Matrix(2, 2))
            assert (cropped_pixels.width, cropped_pixels.height) == (original_pixels.width, original_pixels.height)
            assert cropped_pixels.samples == original_pixels.samples
            assert len(cropped.get_drawings()) == 2
            assert not cropped.get_image_info()
            assert cropped.get_text().strip() == "FIGURELABEL"
            # Check the fixture's exterior sentinel strings, in decoded
            # streams and their ASCII hex form; not a general privacy proof.
            streams = b"\n".join(
                reopened.xref_stream(xref) or b""
                for xref in range(1, reopened.xref_length())
                if reopened.xref_is_stream(xref)
            ).lower()
            for sentinel in (b"EXTERNALBEFORE", b"EXTERNALAFTER"):
                assert sentinel.lower() not in streams
                assert sentinel.hex().encode() not in streams
    return data


def test_df01_known_figure_region_can_be_isolated_without_rasterization():
    _df01_isolated_synthetic_figure()


@pytest.mark.usefixtures("require_physical_compiler")
def test_df01_vector_region_survives_real_g5_compilation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real G5 renderer/staging/Tectonic, explicit asset; no OCR detection claim."""
    from core.compiler.rendering.models import AssetReference, RenderGeometry

    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    data = _df01_isolated_synthetic_figure()
    relative = "data/assets/" + sha256(data).hexdigest() + ".pdf"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(data)
    asset = AssetReference(path=relative, mime_type="application/pdf")
    units = [
        RenderUnit("before", ContentNodeType.PARAGRAPH, "Texto anterior."),
        RenderUnit("figure", ContentNodeType.IMAGE, relative,
                   geometry=RenderGeometry(.25, .25, .5, 110/300, 1), asset=asset),
        RenderUnit("after", ContentNodeType.PARAGRAPH, "Texto posterior."),
    ]
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    tex = TexBuilder(RenderContextFactory.create(profile)).build(units)
    assert "pagebox=cropbox" in tex
    result = HostTectonicRunner().compile(
        tex, output_dir=str(tmp_path), image_assets=(asset,),
    )
    with fitz.open(result) as compiled:
        text = " ".join(" ".join(page.get_text().split()) for page in compiled)
        assert text.count("FIGURELABEL") == 1
        assert text.count("Texto anterior.") == text.count("Texto posterior.") == 1
        assert "EXTERNALBEFORE" not in text and "EXTERNALAFTER" not in text
        assert not any(page.get_image_info() for page in compiled)
        drawings = [drawing for page in compiled for drawing in page.get_drawings()]
        assert any(d["rect"].height > 0 and
                   d["rect"].width / d["rect"].height == pytest.approx(1.4, rel=.02)
                   for d in drawings)


def test_df01_pdf_natural_size_is_preserved_and_oversize_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, require_physical_compiler,
) -> None:
    """Physical G5 witness: no enlargement, proportional shrink, no rasterization."""
    from core.compiler.rendering.models import AssetReference, RenderGeometry

    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    assets = []
    for page_width, line_width, stroke, crop in (
        (400, 60, .25, (35, 390, 105, 400)),
        (900, 880, .5, (0, 0, 900, 500)),
    ):
        with fitz.open() as source:
            page = source.new_page(width=page_width, height=500)
            x, y = (40, 395) if page_width == 400 else (10, 50)
            page.draw_line((x, y), (x + line_width, y), width=stroke)
            page.set_cropbox(fitz.Rect(crop))
            data = source.tobytes(garbage=4, deflate=True)
        ref = "data/assets/" + sha256(data).hexdigest() + ".pdf"
        target = tmp_path / ref
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        assets.append(AssetReference(path=ref, mime_type="application/pdf"))
    units = [
        RenderUnit("rule", ContentNodeType.IMAGE, assets[0].path,
                   geometry=RenderGeometry(.0875, .78, .175, .02, 1), asset=assets[0]),
        RenderUnit("wide", ContentNodeType.IMAGE, assets[1].path,
                   geometry=RenderGeometry(0, 0, 1, 1, 1), asset=assets[1]),
    ]
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    tex = TexBuilder(RenderContextFactory.create(profile)).build(units)
    result = HostTectonicRunner().compile(
        tex, output_dir=str(tmp_path), image_assets=tuple(assets),
    )
    with fitz.open(result) as compiled:
        assert not any(page.get_image_info() for page in compiled)
        lines = [(page.rect.width, d) for page in compiled for d in page.get_drawings()
                 if d["type"] == "s" and d["rect"].width > 0 and d["rect"].height < .1]
        assert len(lines) == 2
        small, large = sorted(lines, key=lambda pair: pair[1]["rect"].width)
        assert small[1]["rect"].width == pytest.approx(60, abs=.1)
        assert small[1]["width"] == pytest.approx(.25, abs=.01)
        assert 60 < large[1]["rect"].width < large[0]
        assert large[1]["width"] == pytest.approx(.5 * large[1]["rect"].width / 880, abs=.02)
