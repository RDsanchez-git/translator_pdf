import os
import json
import asyncio
from core.pipeline.job import TranslationJob
from apps.bootstrap.pipeline_factory import build_pipeline
from tests.helpers.fakes import FakeChunker, FakeDispatcher
from tests.helpers.markdown_inspector import MarkdownInspector

async def capture_golden_snapshots():
    pdf_path = "tests/fixtures/sample_3_pages.pdf"
    golden_dir = "tests/golden"
    os.makedirs(golden_dir, exist_ok=True)

    pipeline = build_pipeline(chunker=FakeChunker(), dispatcher=FakeDispatcher())
    job = TranslationJob(job_id="job_bootstrap_capture", source_path=pdf_path)
    
    result = await pipeline.execute(job)
    content = result.document.content
    
    struct_path = os.path.join(golden_dir, "sample_3_pages.structure.json")
    latex_path = os.path.join(golden_dir, "sample_3_pages.latex.json")
    semantic_path = os.path.join(golden_dir, "sample_3_pages.semantics.json")

    # 1. Congelado Estructural y Técnico Determinista
    with open(struct_path, "w", encoding="utf-8") as f:
        json.dump(MarkdownInspector.extract_structure(content), f, indent=2)
    with open(latex_path, "w", encoding="utf-8") as f:
        json.dump(MarkdownInspector.extract_technical_tokens(content), f, indent=2)

    # 2. SOTA: Umbral estático empírico inmune a model drift
    semantic_data = {
        "minimum_similarity": 0.85
    }
    with open(semantic_path, "w", encoding="utf-8") as f:
        json.dump(semantic_data, f, indent=2)
        
    print("[Bootstrap] Todos los moldes (Estructura, LaTeX, Semántica) han sido congelados.")

if __name__ == "__main__":
    asyncio.run(capture_golden_snapshots())