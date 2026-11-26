"""DF01 producer witnesses: synthetic PDFs only; no network or real inference."""
from hashlib import sha256

import fitz
import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import VisualTablePayload, ImagePayload
from core.layout.classification import HeuristicLayoutClassifier
from core.execution.exceptions import LayoutRecoveryError
from infra.extraction.providers.pymupdf_provider import PyMuPDFProvider


def _source(tmp_path, kind, *, extra=None):
    path = tmp_path / (kind + ".pdf")
    with fitz.open() as doc:
        p = doc.new_page(width=400, height=400)
        p.insert_text((35, 55), "BEFORE PROSE")
        if kind == "table":
            for a, b in (
                ((100,100),(300,100)), ((100,140),(300,140)),
                ((100,180),(300,180)), ((100,220),(300,220)),
                ((100,100),(100,220)), ((300,100),(300,220)),
                ((200,140),(200,180)), ((200,180),(200,220)),
            ):
                p.draw_line(a, b, width=.5)
            for x,y,t in ((140,125,"Merged title"), (120,165,"Left A"),
                          (220,165,"Right B"), (120,205,"Left C"), (220,205,"Right D")):
                p.insert_text((x,y),t,fontsize=10)
        else:
            p.draw_rect(fitz.Rect(100,100,300,220),width=.5)
            p.draw_line((120,200),(280,120),width=.5)
            p.insert_text((140,140),"FIGLABEL",fontsize=10)
        if extra != "no_caption":
            p.insert_text((100,250),("Table" if kind == "table" else "Figure")+" 1. Results")
        p.insert_text((35,330),"AFTER PROSE")
        if extra == "orphan":
            p.draw_line((35,290),(80,290))
        elif extra == "crossing":
            p.insert_text((80,150),"Boundary crossing sentence",fontsize=10)
        elif extra == "rotation":
            p.set_rotation(90)
        doc.save(str(path))
    return path


@pytest.mark.integration
@pytest.mark.parametrize("kind,count,node_type,payload_type", [
    ("table",8,ContentNodeType.TABLE_COMPLEX,VisualTablePayload),
    ("figure",2,ContentNodeType.IMAGE,ImagePayload),
])
def test_df01_protected_region_pipeline(tmp_path, monkeypatch, kind, count, node_type, payload_type):
    monkeypatch.setenv("APP_ROOT",str(tmp_path))
    path = _source(tmp_path,kind)
    provider = PyMuPDFProvider(HeuristicLayoutClassifier())
    layout = provider.extract(str(path))
    second = provider.extract(str(path))
    assert layout == second
    blocks = layout.pages[0].blocks
    assert len(blocks) == 4
    assert blocks[1].metadata.provider is None
    assert blocks[1].block_id.value == "p1_region0"
    # Use the connected extraction composition root, not a duplicate mapper.
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline
    ast = build_extraction_pipeline().parse(str(path))
    protected = [n for n in ast if n.node_type == node_type]
    assert len(protected) == 1
    node = protected[0]
    assert isinstance(node.payload,payload_type)
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    captions = [n for n in ast if n.node_type == ContentNodeType.CAPTION]
    assert len(captions) == 1 and captions[0].strategy == TranslationStrategy.TRANSLATE
    assert captions[0].text_content.endswith("1. Results")
    assert len(node.metadata.physical_regions) == 1
    region = node.metadata.physical_regions[0]
    assert region.page_number == 1 and region.bbox is not None
    assert region.page_width == region.page_height == 400
    ref = node.text_content
    data = (tmp_path / ref).read_bytes()
    assert ref == "data/assets/"+sha256(data).hexdigest()+".pdf"
    assert len(list((tmp_path/"data/assets").glob("*.pdf"))) == 1
    with fitz.open(str(path)) as original, fitz.open(stream=data,filetype="pdf") as asset:
        assert len(asset) == 1
        page = asset[0]
        assert len(page.get_drawings()) == count
        assert not page.get_image_info()
        text = page.get_text()
        for token in ("BEFORE PROSE","AFTER PROSE","1. Results"):
            assert token not in text
            assert sum(token in n.text_content for n in ast) == 1
        for token in (("Merged title","Left A","Right B","Left C","Right D") if kind=="table" else ("FIGLABEL",)):
            assert text.count(token) == 1
            assert not any(token in n.text_content for n in ast)
        streams = b"\n".join(asset.xref_stream(x) or b"" for x in range(1,asset.xref_length()) if asset.xref_is_stream(x)).lower()
        for token in (b"BEFORE PROSE",b"AFTER PROSE",b"1. Results"):
            assert token.lower() not in streams
            assert token.hex().encode() not in streams
        box = region.bbox
        for scale in (1,2):
            matrix = fitz.Matrix(scale,scale)
            a = original[0].get_pixmap(clip=fitz.Rect(box.x0,box.y0,box.x1,box.y1),matrix=matrix)
            b = page.get_pixmap(matrix=matrix)
            assert (a.width,a.height,a.samples) == (b.width,b.height,b.samples)


@pytest.mark.integration
@pytest.mark.parametrize("extra",["orphan","crossing","rotation","no_caption"])
def test_df01_ambiguous_figure_fails_before_asset_publication(tmp_path,monkeypatch,extra):
    monkeypatch.setenv("APP_ROOT",str(tmp_path))
    path = _source(tmp_path,"figure",extra=extra)
    with pytest.raises(LayoutRecoveryError,match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(path))
    assert not (tmp_path/"data/assets").exists()


@pytest.mark.integration
def test_df01_disabled_assets_fail_closed(tmp_path,monkeypatch):
    monkeypatch.setenv("APP_ROOT",str(tmp_path))
    with pytest.raises(LayoutRecoveryError,match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier(),write_images=False).extract(str(_source(tmp_path,"table")))
    assert not (tmp_path/"data/assets").exists()


@pytest.mark.integration
def test_df01_exact_merged_grid_independent_of_native_table_detector(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    path = _source(tmp_path, "table")
    layout = PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(path))
    tables = [b for b in layout.pages[0].blocks if b.logical_type.value == "TABLE_COMPLEX"]
    assert len(tables) == 1
    assert tables[0].asset_path is not None
    with fitz.open(tmp_path / tables[0].asset_path) as asset:
        assert len(asset[0].get_drawings()) == 8


@pytest.mark.integration
def test_df01_independent_grid_without_caption_is_rejected(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(_source(tmp_path, "table", extra="no_caption")))
    assert not (tmp_path / "data/assets").exists()


def _three_rule_source(tmp_path, *, defect=None, multiple_rules=False, caption_below=False):
    path = tmp_path / "three_rules.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=500, height=500)
        page.insert_text((50, 60), "BEFORE PROSE")
        if not caption_below:
            page.insert_text((100, 95), "Table 1. Multilevel results" if defect != "caption" else "Ordinary text")
        rules = (120, 144, 175, 230, 290) if multiple_rules else (120, 175, 290)
        if defect == "empty_band":
            rules = (120, 124, *rules[1:])
        if defect == "simple":
            rules = (120, 144, 175, 207, 230, 253, 290)
        for y in rules:
            page.draw_line((90, y), (410, y), width=.5)
        for row, y in enumerate((138, 157, 195, 218, 241, 264)):
            if multiple_rules and row == 0 and defect != "simple":
                page.insert_text((120, y), "SECTION GROUP", fontsize=10)
                continue
            for col, x in enumerate((120, 220, 320)):
                if defect == "prose":
                    if col == 0:
                        page.insert_text((x, y), "Ordinary continuous prose")
                else:
                    page.insert_text((x, y), f"R{row}C{col}", fontsize=10)
        if caption_below:
            page.insert_text((100, 320), "Table 1. Multilevel results")
        if defect == "orphan":
            page.draw_line((40, 350), (80, 350))
        if defect == "crossing":
            page.insert_text((70, 165), "Boundary crossing text", fontsize=10)
        page.insert_text((50, 390), "AFTER PROSE")
        doc.save(str(path))
    return path


@pytest.mark.integration
@pytest.mark.parametrize("multiple_rules", [False, True], ids=["three_rules", "multiple_rules"])
def test_df01_three_rule_multilevel_header_table_is_preserved(tmp_path, monkeypatch, multiple_rules):
    from types import SimpleNamespace
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline

    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    source = _three_rule_source(tmp_path, multiple_rules=multiple_rules)
    ast = build_extraction_pipeline().parse(str(source))
    tables = [n for n in ast if n.node_type == ContentNodeType.TABLE_COMPLEX]
    assert len(tables) == 1
    node = tables[0]
    assert isinstance(node.payload, VisualTablePayload)
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    assert len([n for n in ast if n.node_type == ContentNodeType.CAPTION]) == 1
    assert all("R0C0" not in n.text_content for n in ast)
    with fitz.open(tmp_path / node.payload.asset_path) as asset:
        assert len(asset[0].get_drawings()) == (5 if multiple_rules else 3)
        assert not asset[0].get_image_info()
        text = asset[0].get_text()
        assert all(text.count(f"R{r}C{c}") == 1
                   for r in range(1 if multiple_rules else 0, 6) for c in range(3))
        if multiple_rules:
            assert text.count("SECTION GROUP") == 1
            assert all("SECTION GROUP" not in n.text_content for n in ast)
            box = node.metadata.physical_regions[0].bbox
            assert box is not None
            rect = fitz.Rect(box.x0, box.y0, box.x1, box.y1)
            with fitz.open(source) as original:
                for scale in (1, 2):
                    matrix = fitz.Matrix(scale, scale)
                    assert asset[0].get_pixmap(matrix=matrix).samples == original[0].get_pixmap(clip=rect, matrix=matrix).samples
        assert "Table 1." not in text and "BEFORE PROSE" not in text and "AFTER PROSE" not in text


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["caption", "prose", "orphan", "crossing"])
def test_df01_three_rule_table_requires_complete_evidence(tmp_path, monkeypatch, defect):
    from types import SimpleNamespace
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(_three_rule_source(tmp_path, defect=defect)))
    assert not (tmp_path / "data/assets").exists()


def _form_source(tmp_path, *, defect=None):
    path = tmp_path / "composed.pdf"
    with fitz.open() as figure, fitz.open() as doc:
        if defect == "clipped_form":
            # The full Form still fits on the destination page, but contains
            # a mark beyond the requested clip. Reject rather than enlarging
            # the candidate to the hidden portion of the source.
            source = figure.new_page(width=240, height=140)
            source.insert_text((20, 125), "HIDDEN EXTERIOR")
        else:
            source = figure.new_page(width=200, height=100)
        source.draw_rect(fitz.Rect(10, 10, 190, 90))
        source.draw_line((20, 80), (180, 20))
        source.insert_text((60, 50), "INTERNAL")
        page = doc.new_page(width=400, height=400)
        page.insert_text((40, 60), "BEFORE")
        page.show_pdf_page(
            fitz.Rect(100, 120, 300, 220), figure, 0,
            clip=fitz.Rect(0, 0, 200, 100),
        )
        page.insert_text((100, 260), "Figure 1. caption" if defect != "caption" else "Other text")
        page.insert_text((40, 330), "AFTER")
        if defect == "orphan":
            page.draw_line((30, 350), (80, 350))
        doc.save(str(path))
    return path


@pytest.mark.integration
def test_df01_complete_form_composition_is_preserved(tmp_path, monkeypatch):
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline

    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    path = _form_source(tmp_path)
    ast = build_extraction_pipeline().parse(str(path))
    figures = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
    assert len(figures) == 1
    node = figures[0]
    assert isinstance(node.payload, ImagePayload)
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    assert node.payload.asset_path is not None
    assert all("INTERNAL" not in n.text_content for n in ast)
    assert len([n for n in ast if n.node_type == ContentNodeType.CAPTION]) == 1
    with fitz.open(tmp_path / node.payload.asset_path) as asset, fitz.open(path) as original:
        page = asset[0]
        assert len(page.get_xobjects()) == 2
        assert len(page.get_drawings()) == 2
        assert not page.get_image_info()
        assert page.get_text().strip() == "INTERNAL"
        box = node.metadata.physical_regions[0].bbox
        assert box is not None
        rect = fitz.Rect(box.x0, box.y0, box.x1, box.y1)
        for scale in (1, 2):
            matrix = fitz.Matrix(scale, scale)
            assert page.get_pixmap(matrix=matrix).samples == original[0].get_pixmap(clip=rect, matrix=matrix).samples
        streams = b"\n".join(asset.xref_stream(x) or b"" for x in range(1, asset.xref_length())
                             if asset.xref_is_stream(x)).lower()
        for token in (b"BEFORE", b"AFTER", b"Figure 1. caption"):
            assert token.lower() not in streams
            assert token.hex().encode() not in streams


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["clipped_form", "caption", "orphan"])
def test_df01_unproven_form_composition_rejected(tmp_path, monkeypatch, defect):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    with pytest.raises(LayoutRecoveryError):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(_form_source(tmp_path, defect=defect)))
    assert not (tmp_path / "data/assets").exists()


@pytest.mark.integration
def test_df01_equal_nested_clip_bounds_are_one_candidate(tmp_path):
    from infra.extraction.providers.pymupdf_protected_regions import (
        _composition, prepare_protected_regions,
    )
    with fitz.open(_form_source(tmp_path)) as doc:
        page = doc[0]
        scopes, signature = _composition(page)
        assert len(scopes) >= 2
        assert len({tuple(r) for r in scopes}) == 1
        assert sum(e["type"] == "clip" for e in signature) >= 2
        regions = prepare_protected_regions(page, page.get_text("dict")["blocks"], page_number=1)
        assert len(regions) == 1
        assert len(regions[0].covered_drawings) == 2


def _note_rule_source(tmp_path, *, defect=None):
    path = tmp_path / "note_rule.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=400, height=500)
        page.insert_text((40, 380), "Body prose before note. A longer body line.", fontsize=12)
        page.draw_line((40, 395), (100, 395), width=.25)
        if defect != "no_note":
            page.insert_text((40 if defect != "misaligned" else 50, 410),
                             "1 Small footnote text with several words.",
                             fontsize=12 if defect == "same_size" else 8)
        if defect == "crossing":
            page.draw_line((70, 392), (70, 398), width=.25)
        if defect == "orphan":
            page.draw_line((30, 100), (90, 100), width=.25)
        doc.save(str(path))
    return path


@pytest.mark.integration
def test_df01_footnote_rule_is_intact_visual_asset_without_consuming_prose(tmp_path, monkeypatch):
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    path = _note_rule_source(tmp_path)
    ast = build_extraction_pipeline().parse(str(path))
    assert len(ast) == 3
    assert "Body prose before note." in ast[0].text_content
    assert "Small footnote text" in ast[2].text_content
    node = ast[1]
    assert node.node_type == ContentNodeType.IMAGE
    assert isinstance(node.payload, ImagePayload)
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    assert node.payload.asset_path is not None
    assert node.metadata.provider_native_id is None
    assert PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(path)) == PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(path))
    box = node.metadata.physical_regions[0].bbox
    assert box is not None
    region = fitz.Rect(box.x0, box.y0, box.x1, box.y1)
    with fitz.open(tmp_path / node.payload.asset_path) as asset, fitz.open(path) as original:
        assert len(asset[0].get_drawings()) == 1
        assert not asset[0].get_text().strip()
        assert not asset[0].get_image_info()
        for scale in (1, 2):
            matrix = fitz.Matrix(scale, scale)
            assert asset[0].get_pixmap(matrix=matrix).samples == original[0].get_pixmap(clip=region, matrix=matrix).samples
        streams = b"\n".join(asset.xref_stream(x) or b"" for x in range(1, asset.xref_length())
                             if asset.xref_is_stream(x)).lower()
        for token in (b"Body prose before note.", b"Small footnote text"):
            assert token.lower() not in streams
            assert token.hex().encode() not in streams


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["no_note", "same_size", "misaligned", "crossing", "orphan"])
def test_df01_rule_without_editorial_evidence_fails_closed(tmp_path, monkeypatch, defect):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(_note_rule_source(tmp_path, defect=defect)))
    assert not (tmp_path / "data/assets").exists()


def _panel_source(tmp_path, *, defect=None):
    path = tmp_path / "panels.pdf"
    with fitz.open() as figure, fitz.open() as doc:
        source = figure.new_page(width=100, height=80)
        source.draw_rect(fitz.Rect(10, 10, 90, 70))
        source.draw_line((20, 60), (80, 20))
        source.insert_text((30, 40), "PANEL")
        page = doc.new_page(width=400, height=400)
        page.insert_text((40, 40), "BEFORE")
        if defect == "distant_caption":
            page.insert_text((80, 15), "Figure 2. Other caption", fontsize=8)
            page.insert_text((80, 55), "Intervening prose", fontsize=8)
        for rect in ((80, 80, 180, 160), (210, 80, 310, 160),
                     (80, 180, 180, 260), (210, 180, 310, 260)):
            page.show_pdf_page(fitz.Rect(rect), figure, 0)
        if defect == "gap_text":
            page.insert_text((183, 145), "PROSE", fontsize=6)
        if defect == "two_captions":
            page.insert_text((80, 65), "Figure 2. Other caption")
        if defect == "orphan":
            page.draw_line((185, 170), (205, 170))
        page.insert_text((80, 290), "Figure 1. Four panels" if defect != "no_caption" else "Other text")
        if defect == "two_captions_late":
            page.insert_text((80, 65), "Figure 2. Other caption")
        page.insert_text((40, 340), "AFTER")
        doc.save(str(path))
    return path


@pytest.mark.integration
def test_df01_multiple_forms_one_caption_one_protected_region(tmp_path, monkeypatch):
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    path = _panel_source(tmp_path)
    ast = build_extraction_pipeline().parse(str(path))
    figures = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
    assert len(figures) == 1
    node = figures[0]
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    assert isinstance(node.payload, ImagePayload)
    assert node.payload.asset_path is not None
    assert len([n for n in ast if n.node_type == ContentNodeType.CAPTION]) == 1
    assert all("PANEL" not in n.text_content for n in ast)
    assert sum("BEFORE" in n.text_content for n in ast) == 1
    assert sum("AFTER" in n.text_content for n in ast) == 1
    with fitz.open(tmp_path / node.payload.asset_path) as asset, fitz.open(path) as original:
        page = asset[0]
        assert len(page.get_drawings()) == 8
        assert len(page.get_xobjects()) == len(original[0].get_xobjects())
        assert page.get_text().count("PANEL") == 4
        assert "BEFORE" not in page.get_text() and "AFTER" not in page.get_text()
        assert "Figure 1." not in page.get_text()
        assert not page.get_image_info()
        region = node.metadata.physical_regions[0].bbox
        assert region is not None
        box = fitz.Rect(region.x0, region.y0, region.x1, region.y1)
        for scale in (1, 2):
            matrix = fitz.Matrix(scale, scale)
            assert page.get_pixmap(matrix=matrix).samples == original[0].get_pixmap(clip=box, matrix=matrix).samples


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["gap_text", "two_captions", "two_captions_late", "orphan", "no_caption"])
def test_df01_panel_union_without_common_ownership_fails_closed(tmp_path, monkeypatch, defect):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    with pytest.raises(LayoutRecoveryError):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(_panel_source(tmp_path, defect=defect)))
    assert not (tmp_path / "data/assets").exists()


@pytest.mark.integration
def test_df01_distant_caption_separated_by_prose_is_not_a_competitor(tmp_path):
    from infra.extraction.providers.pymupdf_protected_regions import prepare_protected_regions

    with fitz.open(_panel_source(tmp_path, defect="distant_caption")) as doc:
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        regions = prepare_protected_regions(page, blocks, page_number=1)
        assert len(regions) == 1
        region = regions[0]
        assert len(region.covered_drawings) == 8
        assert region.caption_block is not None
        caption = blocks[region.caption_block]
        assert "Figure 1." in "".join(
            span["text"] for line in caption["lines"] for span in line["spans"]
        )
        with fitz.open(stream=region.pdf, filetype="pdf") as asset:
            assert asset[0].get_text().count("PANEL") == 4
            assert "Other caption" not in asset[0].get_text()
            assert "Intervening prose" not in asset[0].get_text()


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["caption", "prose", "orphan", "crossing", "empty_band", "simple"])
def test_df01_multiple_rule_table_requires_structural_evidence(tmp_path, monkeypatch, defect):
    from types import SimpleNamespace
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(
            _three_rule_source(tmp_path, defect=defect, multiple_rules=True)
        ))
    assert not (tmp_path / "data/assets").exists()


@pytest.mark.integration
@pytest.mark.parametrize("caption_below", [False, True], ids=["above", "below"])
@pytest.mark.parametrize("defect", [None, "prose", "crossing", "two_captions", "missing_native_id"])
def test_df01_fused_caption_keeps_native_identity_and_complete_table(tmp_path, monkeypatch, defect, caption_below):
    from types import SimpleNamespace
    from infra.extraction.providers.pymupdf_protected_regions import prepare_protected_page
    from infra.extraction.providers.pymupdf_integrity import UnrepresentedPdfContentError

    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setattr(fitz.Page, "find_tables", lambda self, **kwargs: SimpleNamespace(tables=[]))
    path = _three_rule_source(tmp_path, caption_below=caption_below)
    with fitz.open(path) as doc:
        page = doc[0]
        original = page.get_text("dict")["blocks"]
        caption_index = next(i for i, b in enumerate(original)
                             if b["lines"][0]["spans"][0]["text"].startswith("Table 1."))
        caption = original[caption_index]
        table_index = caption_index - 1 if caption_below else caption_index + 1
        table = original[table_index]
        # Simulate native grouping without altering source glyphs or line
        # order in the positive case. Negative views exercise split guards.
        caption_lines = list(caption["lines"])
        if defect == "prose":
            first = caption_lines[0]
            caption_lines[0] = {**first, "spans": [{**first["spans"][0], "text": "Ordinary prose"}]}
        if defect == "crossing":
            first = caption_lines[0]
            caption_lines[0] = {**first, "bbox": (100, 285, 200, 325) if caption_below else (100, 85, 200, 125)}
        if defect == "two_captions":
            first = caption_lines[0]
            caption_lines.append({**first, "spans": [{**first["spans"][0], "text": "Table 2. Other"}]})
        lines = table["lines"] + caption_lines if caption_below else caption_lines + table["lines"]
        merged_box = fitz.Rect(caption["bbox"]) | fitz.Rect(table["bbox"])
        merged = {**caption, "bbox": tuple(merged_box), "lines": lines}
        start = min(caption_index, table_index)
        fused = original[:start] + [merged] + original[start + 2:]
        if defect == "missing_native_id":
            fused[-1] = {k: v for k, v in fused[-1].items() if k != "number"}
        if defect:
            with pytest.raises(UnrepresentedPdfContentError):
                prepare_protected_page(page, fused, page_number=1)
            return
        blocks, regions = prepare_protected_page(page, fused, page_number=1)
        assert len(regions) == 1
        region = regions[0]
        assert region.logical_type.name == "TABLE_COMPLEX"
        assert region.caption_block == caption_index
        assert caption_index not in region.covered_blocks
        assert table_index in region.covered_blocks
        assert blocks[caption_index]["number"] == caption["number"]
        assert blocks[caption_index]["bbox"] == caption["bbox"]
        assert blocks[caption_index]["lines"] == caption["lines"]
        assert blocks[table_index]["lines"] == table["lines"]
        with fitz.open(stream=region.pdf, filetype="pdf") as asset:
            assert len(asset[0].get_drawings()) == 3
            assert "Table 1." not in asset[0].get_text()
            assert all(asset[0].get_text().count(f"R{r}C{c}") == 1
                       for r in range(6) for c in range(3))


    # Exercise the provider's actual publication path with the same grouped
    # source view; disposable isolated PDFs still use real native extraction.
    native_get_text = fitz.Page.get_text

    def grouped_get_text(self, option="text", *args, **kwargs):
        result = native_get_text(self, option, *args, **kwargs)
        if option == "dict" and self.parent is not None and self.parent.name == str(path):
            return {**result, "blocks": fused}
        return result

    monkeypatch.setattr(fitz.Page, "get_text", grouped_get_text)
    layout = PyMuPDFProvider(HeuristicLayoutClassifier()).extract(str(path))
    published = layout.pages[0].blocks
    assert len({b.block_id.value for b in published}) == len(published)
    captions = [b for b in published if b.logical_type.name == "CAPTION"]
    tables = [b for b in published if b.logical_type.name == "TABLE_COMPLEX"]
    assert len(captions) == len(tables) == 1
    assert captions[0].block_id.value == f"p1_b{caption['number']}"
    assert captions[0].metadata.provider is not None
    assert captions[0].metadata.provider.native_block_index == caption["number"]
    assert tables[0].metadata.provider is None
    assert all("R0C0" not in b.content.original for b in published)


@pytest.mark.integration
@pytest.mark.parametrize("defect", [None, "visible", "value", "default", "action", "print"])
def test_df01_hidden_empty_widget_only(tmp_path, monkeypatch, defect):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    original = _form_source(tmp_path)
    path = tmp_path / "widget.pdf"
    with fitz.open(original) as doc:
        page = doc[0]
        widget = fitz.Widget()
        widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        widget.field_name = "empty_control"
        widget.field_value = "DATA" if defect == "value" else ""
        widget.rect = fitz.Rect(40, 80, 80, 100)
        widget.border_width = 1
        widget.border_color = (0, 0, 0)
        page.add_widget(widget)
        xref = page.first_widget.xref
        # Build explicit serialized PDF flag values rather than rely on
        # a version-dependent PyMuPDF annotation constant.
        flags = 4 if defect == "visible" else 6 if defect == "print" else 2
        doc.xref_set_key(xref, "F", str(flags))
        doc.xref_set_key(xref, "FT", "/Tx")
        if defect == "default":
            doc.xref_set_key(xref, "DV", "(DATA)")
        if defect == "action":
            doc.xref_set_key(xref, "A", "<< /S /Named /N /NextPage >>")
        doc.save(path)
    # Verify the intended condition survives serialization, independently
    # of the producer. A negative must not pass due to a broken fixture.
    with fitz.open(path) as reopened:
        saved_widget = reopened[0].first_widget
        assert saved_widget is not None
        xref = saved_widget.xref
        assert reopened.xref_get_key(xref, "F") == ("int", str(flags))
        assert reopened.xref_get_key(xref, "FT") == ("name", "/Tx")
        if defect == "value":
            assert reopened.xref_get_key(xref, "V") == ("string", "DATA")
        if defect == "default":
            assert reopened.xref_get_key(xref, "DV") == ("string", "DATA")
        if defect == "action":
            assert reopened.xref_get_key(xref, "A")[0] == "dict"
    provider = PyMuPDFProvider(HeuristicLayoutClassifier())
    if defect:
        key = {"visible": "F", "print": "F", "value": "V", "default": "DV", "action": "A"}[defect]
        with pytest.raises(LayoutRecoveryError, match=rf"DF01_WIDGET_CONTENT_UNPROVEN: {key}\b"):
            provider.extract(str(path))
        assert not (tmp_path / "data/assets").exists()
        return
    layout = provider.extract(str(path))
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline
    ast = build_extraction_pipeline().parse(str(path))
    assert layout.pages[0].blocks
    figures = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
    assert len(figures) == 1
    payload = figures[0].payload
    assert isinstance(payload, ImagePayload) and payload.asset_path is not None
    with fitz.open(tmp_path / payload.asset_path) as asset:
        assert asset[0].first_widget is None
        assert asset[0].first_annot is None
        assert asset[0].get_text().strip() == "INTERNAL"
        assert len(asset[0].get_drawings()) == 2


@pytest.mark.integration
@pytest.mark.parametrize("hidden_paint", [False, True])
def test_df01_direct_nested_clip_is_not_a_larger_hidden_form(tmp_path, hidden_paint):
    from infra.extraction.providers.pymupdf_integrity import UnrepresentedPdfContentError
    from infra.extraction.providers.pymupdf_protected_regions import (
        _composition, prepare_protected_regions,
    )
    with fitz.open() as doc:
        page = doc.new_page(width=400, height=400)
        page.insert_text((40, 50), "BEFORE")
        page.insert_text((130, 160), "INTERNAL")
        page.insert_text((100, 260), "Figure 1. caption")
        page.insert_text((40, 330), "AFTER")
        page.draw_rect(fitz.Rect(120, 130, 280, 210))
        page.draw_line((130, 200), (270, 140))
        first = page.get_contents()[-2]
        if hidden_paint:
            page.draw_line((90, 225), (310, 225))
        last = page.get_contents()[-1]
        # An explicit direct clip, followed by a larger redundant clip.
        # Neither is a Form invocation or contains separate source data.
        doc.update_stream(first, b"q 100 180 200 100 re W n 90 170 220 120 re W n\n"
                          + doc.xref_stream(first))
        doc.update_stream(last, doc.xref_stream(last) + b"\nQ\n")
        assert not page.get_xobjects()
        scopes, signature = _composition(page)
        assert scopes == [fitz.Rect(100, 120, 300, 220)] * 2
        assert sum(entry["type"] == "clip" for entry in signature) == 2
        if hidden_paint:
            # get_drawings observes this exterior stroke even though the
            # outer clip makes it invisible. Full coverage remains required.
            with pytest.raises(UnrepresentedPdfContentError, match="DF01_UNCOVERED_VECTOR_DRAWINGS"):
                prepare_protected_regions(page, page.get_text("dict")["blocks"], page_number=1)
            return
        regions = prepare_protected_regions(page, page.get_text("dict")["blocks"], page_number=1)
        assert len(regions) == 1
        region = regions[0]
        assert len(region.covered_drawings) == 2
        with fitz.open(stream=region.pdf, filetype="pdf") as asset:
            assert asset[0].get_text().strip() == "INTERNAL"
            assert not asset[0].get_xobjects()
            for scale in (1, 2):
                matrix = fitz.Matrix(scale, scale)
                assert asset[0].get_pixmap(matrix=matrix).samples == page.get_pixmap(
                    clip=fitz.Rect(region.bbox), matrix=matrix
                ).samples
