import pathlib
from typing import Tuple
from core.ast.models import ASTNode
from core.benchmark.ground_truth.ports import ASTExtractionPort
from core.pipeline.orchestrator import ParserProtocol


class BenchmarkParserBridge(ASTExtractionPort):
    """Adaptador puente de infraestructura.

    DF-10 (cerrado): extract_ast retorna Tuple[ASTNode, ...] para cumplir
    el contrato actualizado de ASTExtractionPort (Gate 1).
    """

    def __init__(self, pdf_directory: pathlib.Path, pipeline_parser: ParserProtocol):
        self._pdf_directory = pdf_directory
        self._pipeline_parser = pipeline_parser

    def extract_ast(self, document_id: str) -> Tuple[ASTNode, ...]:
        pdf_path = self._pdf_directory / f"{document_id}.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"Physical binary file not found at path: {pdf_path}")

        # tuple() garantiza inmutabilidad en la frontera (DF-10).
        return tuple(self._pipeline_parser.parse(str(pdf_path)))