from typing import List, Callable
from core.ast.models import ASTNode
from core.pipeline.orchestrator import ParserProtocol
from core.domain.document import DocumentLayout
from core.execution.exceptions import LayoutRecoveryError, ASTMappingError
from core.extraction.provider import ExtractionProvider

class PdfParserAdapter(ParserProtocol):
    def __init__(
        self, 
        provider: ExtractionProvider, 
        layout_to_ast_mapper: Callable[[DocumentLayout], List[ASTNode]]
    ):
        self._provider = provider
        self._layout_to_ast_mapper = layout_to_ast_mapper

    def parse(self, file_path: str) -> List[ASTNode]:
        document_layout = self._provider.extract(file_path)
        
        if not document_layout or not document_layout.pages:
            raise LayoutRecoveryError(
                message="El ecosistema de extracción devolvió una estructura vacía o sin páginas físicas.",
                provider_name=self._provider.__class__.__name__,
                pdf_path=file_path
            )
            
        try:
            nodes = self._layout_to_ast_mapper(document_layout)
        except Exception as e:
            raise ASTMappingError(
                message=f"Corrupción crítica en la traducción de bloques hacia el AST: {str(e)}",
                pdf_path=file_path
            )
        
        if not nodes:
            raise ASTMappingError(
                message="El mapeador estratégico devolvió un árbol vacío (0 nodos lógicos).",
                pdf_path=file_path
            )
            
        return nodes