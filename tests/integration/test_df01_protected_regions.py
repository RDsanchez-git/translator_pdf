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
