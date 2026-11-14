"""B02.5: visual formula survives PDF -> AST -> G3 PRESERVE -> G5 asset staging.

No remote provider, Tectonic executable, or Docker is used.
This test does NOT attest to math semantics or page layout fidelity.
"""
from pathlib import Path
import fitz
import pytest
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import TranslationTaskType
from core.ast.hashing import compute_ast_hash
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import materialize_node_results
from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from core.compiler.rendering.image_assets import stage_image_assets
from core.execution.exceptions import LayoutRecoveryError


class SimpleEstimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1,len(text.split()))


def source_pdf(path: Path, *, mixed: bool=False) -> None:
    with fitz.open() as doc:
        p=doc.new_page()
        p.insert_text((72,72), "A scientific statement.",fontname="helv")
        p.insert_text((72,120),"abgDS",fontname="symb",fontsize=16)
        if mixed:
            # Same physical block is produced using raw text spans if positions
            # meet; force classification via a monkeypatch below instead.
            pass
        doc.save(str(path))


@pytest.mark.integration
def test_dedicated_math_font_survives_as_visual_preserve(tmp_path,monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    pdf=tmp_path/"formula.pdf";source_pdf(pdf)
    ast=build_extraction_pipeline().parse(str(pdf))
    images=[n for n in ast if n.node_type==ContentNodeType.IMAGE]
    assert len(images)==1
    visual=images[0]
    assert visual.strategy == TranslationStrategy.PASSTHROUGH
    assert (tmp_path / visual.payload.asset_path).exists()
    assert visual.metadata.pages == [1]
    units,_=build_semantic_chunks_as_units(ast,SimpleEstimator())
    plan=ChunkPlan.build("document",compute_ast_hash(ast),ast,units)
    preservation=[u for u in plan.units if any(m.node_id==visual.node_id for m in u.members)]
    assert len(preservation)==1
    assert preservation[0].chunk_type==TranslationTaskType.PRESERVE
    assert preservation[0].members[0].source_text == visual.payload.asset_path

    import json,hashlib
    replies={}
    for u in plan.units:
        if u.chunk_type!=TranslationTaskType.PRESERVE:
            replies[u.chunk_id]=json.dumps({
                "schema_version":1,"document_id":plan.document_id,"ast_hash":plan.ast_hash,
                "manifest_sha256":plan.digest,"chunk_id":u.chunk_id,
                "members":[{"node_id":m.node_id,"segment_index":m.segment_index,
                            "source_sha256":hashlib.sha256(m.source_text.encode()).hexdigest(),
                            "translated_text":m.source_text.strip()} for m in u.members]})
    result=materialize_node_results(plan,replies)
    assert next(x.text for x in result if x.node_id==visual.node_id)==visual.payload.asset_path
    unit=DefaultRenderUnitMapper(RenderGeometryAdapter(),RenderAssetAdapter()).map_to_unit(
        [visual], visual.payload.asset_path)
    assert unit.asset is not None
    private=tmp_path/"compiled"; private.mkdir()
    stage_image_assets((unit.asset,),source_root=tmp_path,execution_dir=private)
    assert (private/"assets"/Path(visual.payload.asset_path).name).is_file()


@pytest.mark.integration
def test_no_visual_fallback_when_image_writing_disabled(tmp_path,monkeypatch):
    from infra.extraction.providers.pymupdf_provider import PyMuPDFProvider
    from core.layout.classification import HeuristicLayoutClassifier
    monkeypatch.setenv("APP_ROOT",str(tmp_path))
    pdf=tmp_path/"disabled.pdf";source_pdf(pdf)
    provider=PyMuPDFProvider(HeuristicLayoutClassifier(),write_images=False)
    with pytest.raises(LayoutRecoveryError,match="B025_MATH_VISUAL_DISABLED"):
        provider.extract(str(pdf))
    assert not (tmp_path/"data"/"assets").exists()
