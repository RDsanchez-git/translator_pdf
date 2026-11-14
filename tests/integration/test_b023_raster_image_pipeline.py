"""B02.3: synthetic PDF raster -> Layout -> AST -> G3 -> staged G5 asset.

No network, Docker, real provider or Tectonic binary.
"""
from hashlib import sha256
from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.hashing import compute_ast_hash
from core.ast.models import TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan, validate_chunk_coverage
from core.chunking.result_contract import materialize_node_results
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.compiler.rendering.image_assets import stage_image_assets
from core.compiler.rendering.models import AssetReference, RenderingConfiguration
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from core.compiler.rendering.implementations import AdaptiveFloatStrategy
from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
from core.execution.exceptions import LayoutRecoveryError


class SimpleEstimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split()) + 1


def _pdf(tmp_path: Path, *, vector: bool = False, repeated: bool = False) -> Path:
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 12, 12), False)
    pix.clear_with(180)
    raw = pix.tobytes("png")
    path = tmp_path / "scientific.pdf"
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "Reproducible diagram and label.")
        page.insert_image(fitz.Rect(72, 100, 150, 178), stream=raw)
        if repeated:
            page.insert_image(fitz.Rect(160, 100, 240, 180), stream=raw)
        if vector:
            page.draw_line(fitz.Point(50, 50), fitz.Point(70, 80))
        doc.save(str(path))
    return path


@pytest.mark.integration
def test_raster_survives_ast_plan_preserve_and_g5_staging(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    original = _pdf(tmp_path)
    ast = build_extraction_pipeline().parse(str(original))
    images = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
    assert len(images) == 1
    image = images[0]
    assert image.strategy == TranslationStrategy.PASSTHROUGH
    assert image.text_content == image.payload.asset_path
    assert image.metadata.pages == [1]
    image_ref = image.payload.asset_path
    assert image_ref is not None
    assert (tmp_path / image_ref).is_file()
    data = (tmp_path / image_ref).read_bytes()
    assert image_ref == "data/assets/" + sha256(data).hexdigest() + ".png"
    assert fitz.Pixmap(data).width == 12

    units, _report = build_semantic_chunks_as_units(ast, SimpleEstimator())
    plan = ChunkPlan.build("document", compute_ast_hash(ast), ast, units)
    matching = [u for u in plan.units if any(m.node_id == image.node_id for m in u.members)]
    assert len(matching) == 1
    assert matching[0].chunk_type == TranslationTaskType.PRESERVE
    assert matching[0].members[0].source_text == image_ref

    responses = {}  # Only PRESERVE is exercised: keep non-image TRANSLATE independent.
    for unit in plan.units:
        if unit.chunk_type != TranslationTaskType.PRESERVE:
            from json import dumps
            responses[unit.chunk_id] = dumps({
                "schema_version": 1, "document_id": plan.document_id,
                "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
                "chunk_id": unit.chunk_id,
                "members": [{"node_id": m.node_id, "segment_index": m.segment_index,
                             "source_sha256": sha256(m.source_text.encode()).hexdigest(),
                             "translated_text": m.source_text.strip()} for m in unit.members],
            })
    nodes = materialize_node_results(plan, responses)
    assert next(n.text for n in nodes if n.node_id == image.node_id) == image_ref
    render_unit = DefaultRenderUnitMapper(
        RenderGeometryAdapter(), RenderAssetAdapter(),
    ).map_to_unit([image], image_ref)
    assert render_unit.asset is not None
    assert render_unit.asset.path == image_ref
    rendered = AdaptiveFloatStrategy(
        RenderingConfiguration(is_multi_column=False)
    ).render(render_unit)
    assert r"\includegraphics" in rendered
    assert "assets/" + Path(image_ref).name in rendered

    private = tmp_path / "private"
    private.mkdir()
    stage_image_assets((AssetReference(path=image_ref),), source_root=tmp_path, execution_dir=private)
    assert (private / "assets" / Path(image_ref).name).read_bytes() == data


@pytest.mark.integration
def test_repeated_raster_uses_one_asset_and_distinct_ast_nodes(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    ast = build_extraction_pipeline().parse(str(_pdf(tmp_path, repeated=True)))
    images = [n for n in ast if n.node_type == ContentNodeType.IMAGE]
    assert len(images) == 2 and images[0].node_id != images[1].node_id
    assert images[0].text_content == images[1].text_content
    assert len(list((tmp_path / "data" / "assets").glob("*.png"))) == 1


@pytest.mark.integration
def test_vector_is_still_blocked_before_persisting_image(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    with pytest.raises(LayoutRecoveryError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        build_extraction_pipeline().parse(str(_pdf(tmp_path, vector=True)))
    assert not (tmp_path / "data" / "assets").exists()
