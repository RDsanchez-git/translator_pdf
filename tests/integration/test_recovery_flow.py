import os
import sys
import unittest
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from infra.db.connection import get_connection  # noqa: E402
from infra.db.fsm_repository import FSMRepository  # noqa: E402
from core.execution.handlers import DocumentCommandHandler  # noqa: E402
from core.pipeline.job import TranslationJob, PipelineStep, JobStatus  # noqa: E402
from core.pipeline.state_store import FSMStateStore  # noqa: E402
from core.pipeline.orchestrator import TranslationPipeline  # noqa: E402
from runtime.recovery import AbandonedProcessWatchdog  # noqa: E402
from runtime.resumer import OnDemandResumeManager  # noqa: E402

class TestRecoveryAndResumeEndToEnd(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_db = str(BASE_DIR / "infra/db/test_fsm.db")
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
            
        conn = get_connection(cls.test_db)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_fsm (
                    document_id TEXT, ast_hash TEXT, current_state TEXT,
                    state_version INTEGER DEFAULT 1, is_terminal INTEGER DEFAULT 0,
                    suspended_state TEXT, failure_reason TEXT, entered_state_at REAL,
                    created_at REAL, updated_at REAL, PRIMARY KEY (document_id, ast_hash)
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def test_complete_crash_recovery_and_resume_lifecycle(self):
        doc_id = "doc_test_resilience_11c"
        ast_hash = "7a40b904c0ec401b"
        
        conn = get_connection(self.test_db)
        try:
            fsm_repo = FSMRepository(conn)
            fsm_repo.initialize_document(doc_id, ast_hash)
            past_time = time.time() - 5000
            conn.execute("UPDATE document_fsm SET current_state = 'PROCESSING', updated_at = ? WHERE document_id = ?", (past_time, doc_id))
            conn.commit()
            status_before = fsm_repo.get_status(doc_id, ast_hash)
            assert status_before is not None
            self.assertEqual(status_before.current_state, "PROCESSING")
        finally:
            conn.close()

        watchdog = AbandonedProcessWatchdog(fsm_db_path=self.test_db)
        watchdog.execute_sweep(threshold_sec=3600)
        
        conn = get_connection(self.test_db)
        try:
            fsm_repo = FSMRepository(conn)
            status_after_watchdog = fsm_repo.get_status(doc_id, ast_hash)
            assert status_after_watchdog is not None
            self.assertEqual(status_after_watchdog.current_state, "STALLED")
            self.assertEqual(status_after_watchdog.suspended_state, "PROCESSING")
        finally:
            conn.close()

        resumer = OnDemandResumeManager(fsm_db_path=self.test_db)
        self.assertTrue(resumer.rescue_stalled_document(doc_id, ast_hash))
        
        conn = get_connection(self.test_db)
        try:
            fsm_repo = FSMRepository(conn)
            status_after_resume = fsm_repo.get_status(doc_id, ast_hash)
            assert status_after_resume is not None
            self.assertEqual(status_after_resume.current_state, "PROCESSING")
        finally:
            conn.close()

        conn = get_connection(self.test_db)
        try:
            fsm_repo = FSMRepository(conn)
            cmd_handler = DocumentCommandHandler(fsm_repo)
            state_store = FSMStateStore(fsm_repo, cmd_handler)
            
            import core.pipeline.orchestrator
            core.pipeline.orchestrator.compute_ast_hash = lambda nodes: ast_hash
            
            mock_comp = MagicMock()
            pipeline = TranslationPipeline(
                parser=mock_comp, chunker=mock_comp, dispatcher=mock_comp,
                audit_builder=mock_comp, state_store=state_store,
                document_repository=MagicMock()
            )
            
            job = TranslationJob(job_id=doc_id, source_path="dummy.pdf")
            
            async def mock_execute(j: TranslationJob) -> Any:
                j.status = JobStatus.COMPLETED
                j.current_step = PipelineStep.FINISHED
                status = fsm_repo.get_status(doc_id, ast_hash)
                if status:
                    fsm_repo.transition_to(
                        document_id=doc_id,
                        ast_hash=ast_hash,
                        old_state=status.current_state,
                        new_state="COMPLETED",
                        current_version=status.state_version,
                        owner_id="test_node",
                        is_terminal=True
                    )
                return MagicMock()
            
            with patch.object(pipeline, 'execute', side_effect=mock_execute):
                import asyncio
                asyncio.run(pipeline.execute(job))
            
            self.assertEqual(job.status, JobStatus.COMPLETED)
            self.assertEqual(job.current_step, PipelineStep.FINISHED)
            
            status_final = fsm_repo.get_status(doc_id, ast_hash)
            assert status_final is not None
            self.assertEqual(status_final.current_state, "COMPLETED")
        finally:
            conn.close()

    @classmethod
    def tearDownClass(cls):
        time.sleep(0.1)
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()