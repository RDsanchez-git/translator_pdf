import pathlib
from typing import Sequence
from core.ast.models import ASTNode
from core.benchmark.ground_truth.ports import ASTExtractionPort
from core.pipeline.orchestrator import ParserProtocol  # Reutilización estricta del contrato global del pipeline

class BenchmarkParserBridge(ASTExtractionPort):
    """
    Adaptador puente de infraestructura. Conecta la resolución semántica del benchmark 
    (document_id) con el motor de extracción oficial mediante su contrato global.
    """
    def __init__(self, pdf_directory: pathlib.Path, pipeline_parser: ParserProtocol):
        self._pdf_directory = pdf_directory
        self._pipeline_parser = pipeline_parser

    def extract_ast(self, document_id: str) -> Sequence[ASTNode]:
        pdf_path = self._pdf_directory / f"{document_id}.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"Physical binary file not found at path: {pdf_path}")
            
        # Delegación incondicional a la firma única del sistema
        return self._pipeline_parser.parse(str(pdf_path))