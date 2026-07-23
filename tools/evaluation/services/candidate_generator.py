import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.ast.builder import FlatASTBuilder
from core.ast.models import ASTNode
from core.domain.document import BoundingBox
from core.extraction.provider import ExtractionProvider
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft
from core.layout.validator import DocumentLayoutValidator, LayoutValidationReport


@dataclass(frozen=True)
class CandidateMetadata:
    """DTO inmutable con metadatos de trazabilidad de un candidato."""
    input_pdf_sha256: str
    parser_name: str
    execution_timestamp: datetime
    elapsed_time_ms: float
    parser_version: Optional[str] = None


@dataclass(frozen=True)
class CandidateGenerationResult:
    """DTO inmutable del resultado de la canalización de aplicación."""
    doc_id: str
    ast_nodes: tuple[ASTNode, ...]
    validation_report: LayoutValidationReport
    metadata: Optional[CandidateMetadata] = None


class CandidateGenerationService:
    """
    Servicio de aplicación puro para orquestar la canalización:
    ExtractionProvider -> DocumentLayout -> DocumentLayoutValidator -> LayoutBlockCollection -> FlatASTBuilder -> tuple[ASTNode, ...].
    """

    def __init__(
        self,
        validator: Optional[DocumentLayoutValidator] = None,
        builder: Optional[FlatASTBuilder] = None,
    ) -> None:
        self._validator = validator or DocumentLayoutValidator()
        self._builder = builder or FlatASTBuilder()

    def generate_candidate(
        self,
        provider: ExtractionProvider,
        provider_name: str,
        pdf_path: Path,
        pdf_sha256: str,
    ) -> CandidateGenerationResult:
        doc_id = pdf_path.stem

        start_time = time.perf_counter()
        layout = provider.extract(str(pdf_path))
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        validation_report = self._validator.validate(layout)
        if not validation_report.is_valid:
            return CandidateGenerationResult(
                doc_id=doc_id,
                ast_nodes=(),
                validation_report=validation_report,
                metadata=None,
            )

        # Mapeo estricto conforme a la firma keyword-only de LayoutBlockDraft
        draft_blocks: list[LayoutBlockDraft] = []
        for page in layout.pages:
            for block in page.blocks:
                text_content = block.content.cleaned if block.content else ""
                
                confidence_score = (
                    block.metadata.confidence.ocr
                    if block.metadata and block.metadata.confidence
                    else 1.0
                )
                
                bbox = block.bbox or BoundingBox(x0=0.0, y0=0.0, x1=0.0, y1=0.0)

                draft_blocks.append(
                    LayoutBlockDraft(
                        block_id=block.block_id,
                        logical_type=block.logical_type.value if hasattr(block.logical_type, "value") else str(block.logical_type),
                        content=text_content,
                        bbox=bbox,
                        confidence=confidence_score,
                        page_index=page.page_number,
                    )
                )

        block_collection = LayoutBlockCollection(blocks=draft_blocks)
        ast_nodes = tuple(self._builder.build(block_collection))
        parser_version = getattr(provider, "version", None)

        metadata = CandidateMetadata(
            input_pdf_sha256=pdf_sha256,
            parser_name=provider_name,
            execution_timestamp=datetime.now(timezone.utc),
            elapsed_time_ms=round(elapsed_ms, 2),
            parser_version=str(parser_version) if parser_version is not None else None,
        )

        return CandidateGenerationResult(
            doc_id=doc_id,
            ast_nodes=ast_nodes,
            validation_report=validation_report,
            metadata=metadata,
        )