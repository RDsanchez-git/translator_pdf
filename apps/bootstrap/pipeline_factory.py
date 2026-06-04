from typing import Optional
from core.pipeline.orchestrator import TranslationPipeline, ChunkerProtocol, DispatcherProtocol, AuditBuilderProtocol
from infra.adapters.pdf_parser import PdfParserAdapter
from core.ast.parser import parse_pdf
from core.compiler.assembler import DocumentAssembler
from core.metrics.summary import SummaryBuilder

def build_pipeline(
    chunker: ChunkerProtocol,
    dispatcher: DispatcherProtocol,
    audit_override: Optional[AuditBuilderProtocol] = None
) -> TranslationPipeline:
    """SOTA: Composition Root parametrizada. Elimina acoplamientos prematuros de 
    infraestructura con estado y garantiza el cumplimiento estricto de protocolos.
    """
    # 1. Componentes estructurales locales estables
    parser = PdfParserAdapter(parser_callable=parse_pdf, verify_output=True)
    assembler = DocumentAssembler(separator="\n\n")
    
    # 2. Resolución de métricas de dominio
    audit_builder = audit_override or SummaryBuilder()
    
    # 3. Construcción del Application Service libre de errores de tipo
    return TranslationPipeline(
        parser=parser,
        chunker=chunker,
        dispatcher=dispatcher,
        assembler=assembler,
        audit_builder=audit_builder
    )