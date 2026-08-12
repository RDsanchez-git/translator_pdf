# tests/unit/test_pipeline_fsm_emission.py
"""
Tests de contrato para la emisión FSM del TranslationPipeline.
NADR-09 §5.1 R1: Toda transición se origina en el orquestador.
"""
import asyncio
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock

from core.pipeline.job import TranslationJob
from core.pipeline.orchestrator import TranslationPipeline
from core.execution.state import (
    DocumentCommand,
    StartParsingCommand,
    StartProcessingCommand,
    MarkAssemblyReadyCommand,
)
from core.execution.state_mapping import RecoveredJobSnapshot
from core.ast.models import DispatchResult
from core.metrics.summary import TranslationAuditSummary


class FakeStateStore:
    """Implementación fake de StateStoreProtocol para tests."""

    def __init__(self, initial_state: Optional[str] = None, initial_hash: str = "abc123"):
        self._state = initial_state
        self._hash = initial_hash
        self._version = 0
        self.dispatched_commands: List[DocumentCommand] = []

    def initialize(self, doc_id: str, ast_hash: str) -> None:
        self._state = "CREATED"
        self._hash = ast_hash

    def dispatch(self, command: DocumentCommand) -> int:
        self.dispatched_commands.append(command)
        self._version += 1
        return self._version

    def load(self, job_id: str) -> Optional[RecoveredJobSnapshot]:
        if self._state is None:
            return None
        return RecoveredJobSnapshot(
            document_id=job_id,
            ast_hash=self._hash,
            state_value=self._state,
        )

    def get_current_version(self, doc_id: str, ast_hash: str) -> int:
        return self._version


def _make_pipeline(state_store: FakeStateStore) -> TranslationPipeline:
    """Construye pipeline con fakes mínimos."""
    parser = MagicMock()
    parser.parse.return_value = []

    chunker = MagicMock()
    chunker.chunk.return_value = []

    dispatcher = AsyncMock()
    dispatcher.dispatch.return_value = DispatchResult(outcomes=[])

    audit_builder = MagicMock()
    audit_builder.build.return_value = MagicMock(spec=TranslationAuditSummary)

    doc_repo = MagicMock()

    return TranslationPipeline(
        parser=parser,
        chunker=chunker,
        dispatcher=dispatcher,
        # assembler ELIMINADO
        audit_builder=audit_builder,
        state_store=state_store,
        document_repository=doc_repo,
    )


class TestPipelineFSMEmission:

    def test_new_document_emits_three_commands_in_order(self):
        """Documento nuevo emite StartParsing, StartProcessing, MarkAssemblyReady."""
        store = FakeStateStore(initial_state=None)
        pipeline = _make_pipeline(store)
        job = TranslationJob(job_id="test_job", source_path="test.pdf")

        from unittest.mock import patch
        with patch("core.pipeline.orchestrator.compute_ast_hash", return_value="abc123"):
            asyncio.run(pipeline.execute(job))

        assert len(store.dispatched_commands) == 3
        assert isinstance(store.dispatched_commands[0], StartParsingCommand)
        assert isinstance(store.dispatched_commands[1], StartProcessingCommand)
        assert isinstance(store.dispatched_commands[2], MarkAssemblyReadyCommand)

    def test_resume_from_processing_emits_only_mark_assembly_ready(self):
        """Resume desde PROCESSING solo emite MarkAssemblyReadyCommand."""
        store = FakeStateStore(initial_state="PROCESSING")
        pipeline = _make_pipeline(store)
        job = TranslationJob(job_id="test_job", source_path="test.pdf")

        from unittest.mock import patch
        with patch("core.pipeline.orchestrator.compute_ast_hash", return_value="abc123"):
            asyncio.run(pipeline.execute(job))

        assert len(store.dispatched_commands) == 1
        assert isinstance(store.dispatched_commands[0], MarkAssemblyReadyCommand)

    def test_resume_from_ready_for_assembly_raises(self):
        """Resume desde READY_FOR_ASSEMBLY retorna error (daemon lo toma)."""
        store = FakeStateStore(initial_state="READY_FOR_ASSEMBLY")
        pipeline = _make_pipeline(store)
        job = TranslationJob(job_id="test_job", source_path="test.pdf")

        from unittest.mock import patch
        with patch("core.pipeline.orchestrator.compute_ast_hash", return_value="abc123"):
            try:
                asyncio.run(pipeline.execute(job))
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "AssemblerWorkerDaemon" in str(e)

        assert len(store.dispatched_commands) == 0

    def test_completed_document_raises(self):
        """Documento COMPLETED debe lanzar error."""
        store = FakeStateStore(initial_state="COMPLETED")
        pipeline = _make_pipeline(store)
        job = TranslationJob(job_id="test_job", source_path="test.pdf")

        from unittest.mock import patch
        with patch("core.pipeline.orchestrator.compute_ast_hash", return_value="abc123"):
            try:
                asyncio.run(pipeline.execute(job))
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "ya fue procesado" in str(e)

    def test_pipeline_returns_document(self):
        """El pipeline lógico retorna document=None (ensamblado asíncrono)."""
        store = FakeStateStore(initial_state=None)
        pipeline = _make_pipeline(store)
        job = TranslationJob(job_id="test_job", source_path="test.pdf")

        from unittest.mock import patch
        with patch("core.pipeline.orchestrator.compute_ast_hash", return_value="abc123"):
            result = asyncio.run(pipeline.execute(job))

        # El pipeline lógico ya no ensambla. document es None.
        assert result.document is None
        assert result.summary is not None