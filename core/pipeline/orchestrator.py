from __future__ import annotations
from typing import Protocol, List
from dataclasses import dataclass
from core.pipeline.job import TranslationJob, PipelineStep
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, ReconstructedDocument
from core.metrics.summary import TranslationAuditSummary

@dataclass(frozen=True)
class PipelineResult:
    """SOTA: DTO inmutable de salida pura del pipeline para consumo de adaptadores (CLI/API)."""
    document: ReconstructedDocument
    summary: TranslationAuditSummary

class ParserProtocol(Protocol):
    def parse(self, file_path: str) -> List[ASTNode]: ...

class ChunkerProtocol(Protocol):
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]: ...

class DispatcherProtocol(Protocol):
    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]: ...

class AssemblerProtocol(Protocol):
    def assemble(self, units: List[TranslatedUnit]) -> ReconstructedDocument: ...

class AuditBuilderProtocol(Protocol):
    def build(self, units: List[TranslatedUnit], doc: ReconstructedDocument) -> TranslationAuditSummary: ...

class TranslationPipeline:
    """SOTA: Application Service. Coordina el flujo mediante contratos abstractos."""
    
    def __init__(
        self,
        parser: ParserProtocol,
        chunker: ChunkerProtocol,
        dispatcher: DispatcherProtocol,
        assembler: AssemblerProtocol,
        audit_builder: AuditBuilderProtocol
    ):
        self.parser = parser
        self.chunker = chunker
        self.dispatcher = dispatcher
        self.assembler = assembler
        self.audit_builder = audit_builder

    async def execute(self, job: TranslationJob) -> PipelineResult:
        """Punto de entrada único. Ejecuta transformaciones y propaga excepciones tras auditoría."""
        job.mark_processing()
        
        try:
            # 1. Extracción
            job.enter_step(PipelineStep.PARSING)
            nodes = self.parser.parse(job.source_path)
            
            # 2. Fragmentación Semántica
            job.enter_step(PipelineStep.CHUNKING)
            translation_units = self.chunker.chunk(nodes)
            
            # 3. Despacho Concurrente Asíncrono
            job.enter_step(PipelineStep.DISPATCHING)
            translated_units = await self.dispatcher.dispatch(translation_units)
            
            # 4. Reconstrucción Textual
            job.enter_step(PipelineStep.ASSEMBLING)
            reconstructed_doc = self.assembler.assemble(translated_units)
            
            # 5. Auditoría Operativa
            job.enter_step(PipelineStep.AUDITING)
            summary = self.audit_builder.build(translated_units, reconstructed_doc)
            
            # Consolidación de Cierre Exitoso
            job.mark_completed(summary)
            return PipelineResult(document=reconstructed_doc, summary=summary)
            
        except Exception as e:
            # Registro pasivo del error y propagación intacta del traceback original
            job.mark_failed(error_type=e.__class__.__name__, error_message=str(e))
            raise