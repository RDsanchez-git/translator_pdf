import os
import json
import asyncio
from core.pipeline.job import TranslationJob
from core.pipeline.orchestrator import TranslationPipeline
from core.metrics.summary import SummaryBuilder
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from infra.db.document_repository import SQLiteDocumentRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from helpers.fakes import FakeChunker, FakeDispatcher
from helpers.markdown_inspector import MarkdownInspector

async def capture_golden_snapshots():
    pdf_path = "tests/fixtures/sample_3_pages.pdf"
    golden_dir = "tests/golden"
    os.makedirs(golden_dir, exist_ok=True)

    # Construir TranslationPipeline directamente
    parser = build_extraction_pipeline()
    doc_conn = get_connection("infra/db/documents.db", timeout=30)
    document_repository = SQLiteDocumentRepository(doc_conn)
    
    fsm_conn = get_connection("infra/db/fsm.db", timeout=30)
    fsm_repo = FSMRepository(fsm_conn)
    command_handler = DocumentCommandHandler(fsm_repo)
    state_store = FSMStateStore(fsm_repo, command_handler)

    pipeline = TranslationPipeline(
        parser=parser,
        chunker=FakeChunker(),
        dispatcher=FakeDispatcher(),
        audit_builder=SummaryBuilder(),
        state_store=state_store,
        document_repository=document_repository,
    )

    job = TranslationJob(job_id="job_bootstrap_capture", source_path=pdf_path)
    result = await pipeline.execute(job)
    if result.document is None:
        print("[Bootstrap] El pipeline lógico no ensambla. Use el AssemblerWorkerDaemon para capturar golden snapshots.")
        return
    
    content = result.document.content

    struct_path = os.path.join(golden_dir, "sample_3_pages.structure.json")
    latex_path = os.path.join(golden_dir, "sample_3_pages.latex.json")
    semantic_path = os.path.join(golden_dir, "sample_3_pages.semantics.json")

    with open(struct_path, "w", encoding="utf-8") as f:
        json.dump(MarkdownInspector.extract_structure(content), f, indent=2)
    with open(latex_path, "w", encoding="utf-8") as f:
        json.dump(MarkdownInspector.extract_technical_tokens(content), f, indent=2)

    semantic_data = {"minimum_similarity": 0.85}
    with open(semantic_path, "w", encoding="utf-8") as f:
        json.dump(semantic_data, f, indent=2)

    print("[Bootstrap] Todos los moldes (Estructura, LaTeX, Semántica) han sido congelados.")

if __name__ == "__main__":
    asyncio.run(capture_golden_snapshots())