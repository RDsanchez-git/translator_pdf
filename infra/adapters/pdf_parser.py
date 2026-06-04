from typing import List, Callable
from core.ast.models import ASTNode
from core.pipeline.orchestrator import ParserProtocol

class PdfParserAdapter(ParserProtocol):
    """SOTA: Adaptador estructural por inversión de control. Desacopla la infraestructura
    de extracción del dominio del pipeline inyectando el invocable real en el constructor.
    """
    
    def __init__(self, parser_callable: Callable[[str], List[ASTNode]], verify_output: bool = True):
        self._parser_callable = parser_callable
        self._verify_output = verify_output

    def parse(self, file_path: str) -> List[ASTNode]:
        """Ejecuta la extracción delegando el control al invocable de producción."""
        nodes = self._parser_callable(file_path)
        
        if self._verify_output and not nodes:
            raise RuntimeError(f"El parser real retornó un árbol AST vacío para: {file_path}")
            
        return nodes