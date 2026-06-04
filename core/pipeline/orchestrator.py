from __future__ import annotations
from typing import Protocol, List
from dataclasses import dataclass
from core.pipeline.job import TranslationJob, PipelineStep
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, ReconstructedDocument
from core.metrics.summary import TranslationAuditSummary
from core.pipeline.state_store import StateStoreProtocol
from core.ast.hashing import compute_ast_hash

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
    """SOTA: Application Service. Orquesta el flujo mediante hitos macro y contratos puros."""
    
    def __init__(
        self,
        parser: ParserProtocol,
        chunker: ChunkerProtocol,
        dispatcher: DispatcherProtocol,
        assembler: AssemblerProtocol,
        audit_builder: AuditBuilderProtocol,
        state_store: StateStoreProtocol
    ):
        self.parser = parser
        self.chunker = chunker
        self.dispatcher = dispatcher
        self.assembler = assembler
        self.audit_builder = audit_builder
        self.state_store = state_store

    async def execute(self, job: TranslationJob) -> PipelineResult:
        """Punto de entrada único. Ejecuta transformaciones guiadas por un flujo lineal uniforme."""
        
        # SOTA: Parseo único y temprano para cálculo del invariante genético (Evita Doble I/O)
        nodes = self.parser.parse(job.source_path)
        current_ast_hash = compute_ast_hash(nodes)

        # Inyección de metadatos operacionales en el DTO de dominio
        job.document_id = job.job_id
        job.ast_hash = current_ast_hash

        # 1. Búsqueda de Reanudación y Activación del Guardián Genético (Anti-Corruption)
        snapshot = self.state_store.load(job.job_id)
        is_valid_resume = False
        
        if snapshot:
            if snapshot.ast_hash == current_ast_hash:
                # El documento no sufrio mutaciones físicas; la reanudación macro es segura
                is_valid_resume = True
                if snapshot.state_value == "COMPLETED":
                    raise ValueError(f"Operación abortada: El documento {job.job_id} ya fue procesado con éxito.")
            else:
                # Mutación detectada. Ignoramos el snapshot para forzar un sobrescritura limpia desde cero
                is_valid_resume = False

        job.mark_processing()
        
        try:
            # --- BARRERA 1: PARSING (Hito operativo inicial) ---
            if not is_valid_resume:
                job.enter_step(PipelineStep.PARSING)
                self.state_store.save(job)

            # --- BARRERA 2: PROCESSING ---
            # DECISIÓN ARQUITECTÓNICA (Resume Macro): 
            # PROCESSING absorbe CHUNKING + DISPATCHING. No se emite checkpoint en DISPATCHING.
            # En caso de caída, la reanudación fuerza un re-chunking local; la SQLite Cache absorbe el 100% 
            # de las llamadas de red al LLM (idempotencia física).
            job.enter_step(PipelineStep.CHUNKING)
            self.state_store.save(job)
            
            translation_units = self.chunker.chunk(nodes)
            
            job.enter_step(PipelineStep.DISPATCHING)
            translated_units = await self.dispatcher.dispatch(translation_units)

            # --- BARRERA 3: ASSEMBLING ---
            # DECISIÓN ARQUITECTÓNICA: ASSEMBLING absorbe AUDITING.
            # El adaptador FSMStateStore promueve a READY_FOR_ASSEMBLY automáticamente.
            job.enter_step(PipelineStep.ASSEMBLING)
            self.state_store.save(job)

            reconstructed_doc = self.assembler.assemble(translated_units)

            job.enter_step(PipelineStep.AUDITING)
            summary = self.audit_builder.build(translated_units, reconstructed_doc)

            # --- BARRERA 4: FINISHED ---
            # mark_completed() inyecta internamente PipelineStep.FINISHED
            job.mark_completed(summary)
            self.state_store.save(job)
            
            return PipelineResult(document=reconstructed_doc, summary=summary)

        except Exception as e:
            job.mark_failed(error_type=e.__class__.__name__, error_message=str(e))
            try:
                self.state_store.save(job)
            except Exception:
                pass
            raise