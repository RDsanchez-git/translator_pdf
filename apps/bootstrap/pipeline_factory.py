from typing import Optional
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore, StateStoreProtocol
from core.pipeline.orchestrator import (TranslationPipeline, ChunkerProtocol, DispatcherProtocol,
                                         AuditBuilderProtocol)
from infra.adapters.pdf_parser import PdfParserAdapter
from core.metrics.summary import SummaryBuilder
from core.compiler.assembler import DocumentAssembler
from core.ast.parser import parse_pdf

def build_pipeline(
    chunker: ChunkerProtocol,
    dispatcher: DispatcherProtocol,
    audit_override: Optional[AuditBuilderProtocol] = None,
    state_store_override: Optional[StateStoreProtocol] = None
) -> TranslationPipeline:
    """SOTA: Composition Root parametrizada. Resuelve e inyecta el adaptador de la FSM 
    Operacional manteniendo el desacoplamiento estricto de la infraestructura.
    """
    # 1. Componentes estructurales locales estables
    parser = PdfParserAdapter(parser_callable=parse_pdf, verify_output=True)
    assembler = DocumentAssembler(separator="\n\n")
    
    # 2. Resolución de métricas de dominio
    audit_builder = audit_override or SummaryBuilder()
    
    # 3. Resolución del adaptador de persistencia oficial de la FSM (Gobernanza)
    if state_store_override:
        state_store = state_store_override
    else:
        fsm_conn = get_connection("infra/db/fsm.db", timeout=30)
        fsm_repo = FSMRepository(fsm_conn)
        command_handler = DocumentCommandHandler(fsm_repo)
        state_store = FSMStateStore(fsm_repo, command_handler)
    
    # 4. Construcción del Application Service libre de errores de tipo
    return TranslationPipeline(
        parser=parser,
        chunker=chunker,
        dispatcher=dispatcher,
        assembler=assembler,
        audit_builder=audit_builder,
        state_store=state_store
    )