"""B02: muestras PDF sintéticas. No contienen originales ni usan red/LLM."""

import fitz
import pytest

from core.execution.exceptions import LayoutRecoveryError
from core.layout.classification import HeuristicLayoutClassifier
from infra.extraction.providers.pymupdf_provider import PyMuPDFProvider


def _save_pdf(tmp_path, name, decorate):
    path = tmp_path / name
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "A normal scientific paragraph.")
        decorate(page)
        doc.save(str(path))
    return path


@pytest.mark.integration
def test_text_only_pdf_remains_extractable(tmp_path):
    pdf = _save_pdf(tmp_path, "prose.pdf", lambda _: None)
    provider = PyMuPDFProvider(classifier=HeuristicLayoutClassifier())
    layout = provider.extract(str(pdf))
    assert len(layout.pages) == 1
    assert len(layout.pages[0].blocks) == 1


@pytest.mark.integration
def test_real_embedded_image_is_preserved_as_asset(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    def add_image(page):
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 2, 2), False)
        pix.clear_with(255)
        page.insert_image(fitz.Rect(80, 100, 115, 135), pixmap=pix)

    pdf = _save_pdf(tmp_path, "figure.pdf", add_image)
    provider = PyMuPDFProvider(classifier=HeuristicLayoutClassifier())
    layout = provider.extract(str(pdf))
    images = [block for page in layout.pages for block in page.blocks
              if block.logical_type.value == "IMAGE"]
    assert len(images) == 1
    assert images[0].content.original.startswith("data/assets/")
    assert (tmp_path / images[0].content.original).is_file()


@pytest.mark.integration
def test_real_vector_drawing_rejected_before_layout_ast(tmp_path):
    pdf = _save_pdf(
        tmp_path,
        "drawing.pdf",
        lambda page: page.draw_line(fitz.Point(100, 100), fitz.Point(180, 150)),
    )
    provider = PyMuPDFProvider(classifier=HeuristicLayoutClassifier())
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        provider.extract(str(pdf))
