from __future__ import annotations
import re
from typing import Protocol, List
from dataclasses import dataclass
from core.pipeline.job import TranslationJob, PipelineStep
from core.ast.models import ASTNode, TranslationUnit, ReconstructedDocument, ContentNodeType, DispatchResult
from core.metrics.summary import TranslationAuditSummary
from core.pipeline.state_store import StateStoreProtocol
from core.normalization.classifier import SemanticNodeClassifier
from core.normalization.fixers.asset_placeholder import StructuralAssetPlaceholder
from core.normalization.validators.ast_integrity import ASTIntegrityValidator
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher
from core.ast.hashing import compute_ast_hash
from core.compiler.assembler import DocumentAssemblyDecision, AssemblyReport
from core.validation.ast.models import ValidationSeverity
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.validation.ast.protocols import ValidationEngine

@dataclass(frozen=True)
class PipelineResult:
    document: ReconstructedDocument
    summary: TranslationAuditSummary
    assembly_report: AssemblyReport

class ParserProtocol(Protocol):
    def parse(self, file_path: str) -> List[ASTNode]: ...

class ChunkerProtocol(Protocol):
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]: ...

class DispatcherProtocol(Protocol):
    async def dispatch(self, units: List[TranslationUnit]) -> DispatchResult: ...

class AssemblerProtocol(Protocol):
    """SOTA: Contrato del motor de ensamblado con soporte de aislamiento de ejecución."""
    def assemble(self, job_id: str, dispatch_result: DispatchResult) -> DocumentAssemblyDecision: ...

class AuditBuilderProtocol(Protocol):
    def build(self, dispatch_result: DispatchResult, decision: DocumentAssemblyDecision) -> TranslationAuditSummary: ...

class DocumentRepositoryProtocol(Protocol):
    def save_batch(self, job_id: str, units: List[TranslationUnit]) -> None: ...
    

class TranslationPipeline:
    def __init__(
        self,
        parser: ParserProtocol,
        chunker: ChunkerProtocol,
        dispatcher: DispatcherProtocol,
        assembler: AssemblerProtocol,
        audit_builder: AuditBuilderProtocol,
        state_store: StateStoreProtocol,
        document_repository: DocumentRepositoryProtocol,
        pre_llm_validator: Optional["ValidationEngine"] = None,  # NUEVO
    ):
        self.parser = parser
        self.chunker = chunker
        self.dispatcher = dispatcher
        self.assembler = assembler
        self.audit_builder = audit_builder
        self.state_store = state_store
        self.document_repository = document_repository
        self._pre_llm_validator = pre_llm_validator  # NUEVO
        
        self._exotic_bullets = re.compile(r'^\s*([•▪‣◦■♦○]|[-‑‒–—-]>\s*)\s*')

    async def execute(self, job: TranslationJob) -> PipelineResult:
        nodes = self.parser.parse(job.source_path)
        
        if not hasattr(job, "pipeline_metadata"):
            job.pipeline_metadata = {}
        job.pipeline_metadata["ast_schema_version"] = "1.0.1"
        
        classifier = SemanticNodeClassifier()
        nodes = classifier.classify_batch(nodes)
        
        placeholder_fixer = StructuralAssetPlaceholder()
        processed_nodes = []
        for node in nodes:
            # SOTA FIX: Uso de la fachada polimórfica de extracción de texto plano
            text = node.text_content or ""
            text_stripped = text.strip()

            if not text_stripped:
                if node.text_content != "":
                    from core.ast.models import ParagraphPayload
                    node = node.model_copy(update={"payload": ParagraphPayload(content="")})
                processed_nodes.append(node)
                continue

            # SOTA FIX: Mapeo de LIST_ITEM obsoleto hacia ContentNodeType.LIST de la Fase 16
            if node.node_type == ContentNodeType.LIST:
                if self._exotic_bullets.match(text):
                    text = self._exotic_bullets.sub("- ", text, count=1)
                    from core.ast.models import ListPayload
                    node = node.model_copy(update={"payload": ListPayload(content=text)})

            # SOTA FIX: Especialización granular de tablas e imágenes (FIGURE mutó a IMAGE)
            if node.node_type in {ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX, ContentNodeType.IMAGE}:
                new_cp = dict(node.control_plane)
                new_cp["preserved_content"] = text
                new_cp["preserve_original"] = True
                new_cp["asset_type"] = node.node_type.value.upper()
                
                result = placeholder_fixer.normalize(
                    text=text, 
                    node_id=node.node_id, 
                    node_type=node.node_type.value
                )
                
                # SOTA FIX: Instanciación inmutable de sub-payloads respetando el esquema de ImagePayload (alt_text)
                from core.ast.models import TablePayload, ImagePayload
                if node.node_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
                    new_payload = TablePayload(content=result.text)
                elif node.node_type == ContentNodeType.IMAGE:
                    new_payload = ImagePayload(
                        alt_text=result.text, 
                        asset_path=getattr(node.payload, "asset_path", "")
                    )
                else:
                    new_payload = node.payload
                
                node = node.model_copy(update={
                    "payload": new_payload,
                    "control_plane": new_cp
                })
            processed_nodes.append(node)
        nodes = processed_nodes
        
        current_ast_hash = compute_ast_hash(nodes)

        validator = ASTIntegrityValidator()
        structural_warnings = validator.validate_ast(nodes)
        
        if any(w.severity == "SEVERE" for w in structural_warnings):
            critical_errors = "; ".join([w.message for w in structural_warnings if w.severity == "SEVERE"])
            raise ValueError(f"AST_INTEGRITY_VIOLATION: Pipeline halted due to topological corruption: {critical_errors}")

        # NADR-04 §5.1 R1: Validación pre-LLM del AST
        # DF-05: Conceptualmente pertenece al flujo de construcción del AST.
        # El bloque de validación pre-LLM queda:
        if self._pre_llm_validator:
            pre_llm_results = list(self._pre_llm_validator.validate_stream(nodes))
            hard_failures = [r for r in pre_llm_results if r.severity == ValidationSeverity.HARD_FAIL]
            if hard_failures:
                error_msgs = "; ".join([r.message for r in hard_failures])
                raise ValueError(f"PRE_LLM_VALIDATION_FAILED: {error_msgs}")

        context_enricher = HierarchicalContextEnricher()
        nodes, structured_registry, enricher_warnings, enricher_metrics = context_enricher.enrich_document(nodes)

        job.document_id = job.job_id
        job.ast_hash = current_ast_hash
        job.pipeline_metadata["context_store"] = structured_registry

        snapshot = self.state_store.load(job.job_id)
        is_valid_resume = False
        
        if snapshot:
            if snapshot.ast_hash == current_ast_hash:
                is_valid_resume = True
                if snapshot.state_value == "COMPLETED":
                    raise ValueError(f"Operación abortada: El documento {job.job_id} ya fue procesado con éxito.")
            else:
                is_valid_resume = False

        job.mark_processing()
        
        try:
            if not is_valid_resume:
                job.enter_step(PipelineStep.PARSING)
                self.state_store.save(job)

            job.enter_step(PipelineStep.CHUNKING)
            self.state_store.save(job)
            
            active_registry = job.pipeline_metadata["context_store"]["mappings"]
            for node in nodes:
                if node.node_type != ContentNodeType.HEADING:
                    ctx_id = node.control_plane.get("context_id")
                    if ctx_id and ctx_id not in active_registry:
                        raise ValueError(f"STATE_CORRUPTION: Node {node.node_id} references a missing context token {ctx_id} post-hydration.")
            
            translation_units = self.chunker.chunk(nodes)
            
            # SOTA FIX: Inyección del job_id para garantizar aislamiento en infraestructura
            self.document_repository.save_batch(job.job_id, translation_units)
            
            job.enter_step(PipelineStep.DISPATCHING)
            dispatch_result = await self.dispatcher.dispatch(translation_units)

            job.enter_step(PipelineStep.ASSEMBLING)
            self.state_store.save(job)
            decision = self.assembler.assemble(job.job_id, dispatch_result)
            
            # ... (Código previo del bloque try se mantiene idéntico)
            
            if not decision.is_accepted or decision.document is None:
                raise ValueError(f"ASSEMBLY_REJECTED: {decision.rejection_reason}")

            job.enter_step(PipelineStep.AUDITING)
            summary = self.audit_builder.build(dispatch_result, decision)

            job.mark_completed(summary)
            self.state_store.save(job)
            
            # SOTA FIX: Asignación local interna para control de flujo
            pipeline_result = PipelineResult(
                document=decision.document, 
                summary=summary,
                assembly_report=decision.audit_report,
            )

        except Exception as e:
            job.mark_failed(error_type=e.__class__.__name__, error_message=str(e))
            try:
                self.state_store.save(job)
            except Exception:
                pass
            raise

        # SOTA FIX: Retorno a nivel de raíz garantiza ruta de salida válida para el linter
        return pipeline_result