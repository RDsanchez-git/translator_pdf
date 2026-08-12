# core/pipeline/orchestrator.py
from __future__ import annotations
import re
from typing import Protocol, List, Optional, Type, TYPE_CHECKING
from dataclasses import dataclass

from core.pipeline.job import TranslationJob, PipelineStep
from core.ast.models import (
    ASTNode, TranslationUnit, DispatchResult,
    ReconstructedDocument, ContentNodeType,
)
from core.metrics.summary import TranslationAuditSummary
from core.pipeline.state_store import StateStoreProtocol
from core.normalization.classifier import SemanticNodeClassifier
from core.normalization.fixers.asset_placeholder import StructuralAssetPlaceholder
from core.normalization.validators.ast_integrity import ASTIntegrityValidator
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher
from core.ast.hashing import compute_ast_hash
from core.validation.ast.models import ValidationSeverity
from core.context.context_registry import ContextRegistry
from core.compiler.assembler import AssemblyReport

from core.execution.state import (
    DocumentCommand,
    StartParsingCommand,
    StartProcessingCommand,
    MarkAssemblyReadyCommand,
    FailDocumentCommand,
)

if TYPE_CHECKING:
    from core.validation.ast.protocols import ValidationEngine


@dataclass(frozen=True)
class PipelineResult:
    document: Optional[ReconstructedDocument]  # None: ensamblado físico es asíncrono
    summary: TranslationAuditSummary
    assembly_report: Optional[AssemblyReport]  # None: ensamblado físico es asíncrono


class ParserProtocol(Protocol):
    def parse(self, file_path: str) -> List[ASTNode]: ...

class ChunkerProtocol(Protocol):
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]: ...

class DispatcherProtocol(Protocol):
    async def dispatch(self, units: List[TranslationUnit]) -> DispatchResult: ...

class AuditBuilderProtocol(Protocol):
    def build(self, dispatch_result: DispatchResult) -> TranslationAuditSummary: ...


class DocumentRepositoryProtocol(Protocol):
    def save_batch(self, job_id: str, units: List[TranslationUnit]) -> None: ...


class TranslationPipeline:
    """
    Orquestador de la fase lógica del pipeline.

    NADR-09 §5.1 R1: Toda transición se origina exclusivamente
    en la capa de orquestación mediante comandos explícitos.

    Comandos emitidos: StartParsing, StartProcessing, MarkAssemblyReady.
    Comandos que NO emite (pertenecen al AssemblerWorkerDaemon):
    StartAssembly, MarkCompilationReady, StartCompilation, CompleteDocument.
    """

    def __init__(
        self,
        parser: ParserProtocol,
        chunker: ChunkerProtocol,
        dispatcher: DispatcherProtocol,
        audit_builder: AuditBuilderProtocol,
        state_store: StateStoreProtocol,
        document_repository: DocumentRepositoryProtocol,
        pre_llm_validator: Optional["ValidationEngine"] = None,
        context_registry: Optional[ContextRegistry] = None,
    ):
        self.parser = parser
        self.chunker = chunker
        self.dispatcher = dispatcher
        self.audit_builder = audit_builder
        self.state_store = state_store
        self.document_repository = document_repository
        self._pre_llm_validator = pre_llm_validator
        self._context_registry = context_registry
        self._exotic_bullets = re.compile(r'^\s*([•▪‣◦■♦○]|[-‑‒–—-]>\s*)\s*')

    def _emit(self, job: TranslationJob, command_class: Type[DocumentCommand], **kwargs: object) -> int:
        """Emite un comando explícito. Sin estado de instancia."""
        doc_id = job.document_id or job.job_id
        ast_hash = job.ast_hash
        if not ast_hash:
            raise RuntimeError(f"No se puede emitir comando sin ast_hash para {doc_id}")
        current_version = self.state_store.get_current_version(doc_id, ast_hash)
        command = command_class(
            document_id=doc_id,
            ast_hash=ast_hash,
            owner_id="pipeline_runtime_layer",
            expected_version=current_version,
            **kwargs,
        )
        return self.state_store.dispatch(command)

    async def execute(self, job: TranslationJob) -> PipelineResult:
        # ── Fase 1: Extracción y preparación del AST ──
        nodes = self.parser.parse(job.source_path)
        job.pipeline_metadata["ast_schema_version"] = "1.0.1"

        classifier = SemanticNodeClassifier()
        nodes = classifier.classify_batch(nodes)

        placeholder_fixer = StructuralAssetPlaceholder()
        processed_nodes: List[ASTNode] = []
        for node in nodes:
            text = node.text_content or ""
            text_stripped = text.strip()

            if not text_stripped:
                if node.text_content != "":
                    from core.ast.models import ParagraphPayload
                    node = node.model_copy(update={"payload": ParagraphPayload(content="")})
                processed_nodes.append(node)
                continue

            if node.node_type == ContentNodeType.LIST:
                if self._exotic_bullets.match(text):
                    text = self._exotic_bullets.sub("- ", text, count=1)
                    from core.ast.models import ListPayload
                    node = node.model_copy(update={"payload": ListPayload(content=text)})

            if node.node_type in {ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX, ContentNodeType.IMAGE}:
                new_cp = dict(node.control_plane)
                new_cp["preserved_content"] = text
                new_cp["preserve_original"] = True
                new_cp["asset_type"] = node.node_type.value.upper()
                result = placeholder_fixer.normalize(
                    text=text, node_id=node.node_id, node_type=node.node_type.value
                )
                from core.ast.models import TablePayload, ImagePayload
                if node.node_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
                    new_payload = TablePayload(content=result.text)
                elif node.node_type == ContentNodeType.IMAGE:
                    new_payload = ImagePayload(
                        alt_text=result.text,
                        asset_path=getattr(node.payload, "asset_path", ""),
                    )
                else:
                    new_payload = node.payload
                node = node.model_copy(update={"payload": new_payload, "control_plane": new_cp})
            processed_nodes.append(node)
        nodes = processed_nodes

        current_ast_hash = compute_ast_hash(nodes)

        validator = ASTIntegrityValidator()
        structural_warnings = validator.validate_ast(nodes)
        if any(w.severity == "SEVERE" for w in structural_warnings):
            critical_errors = "; ".join(
                [w.message for w in structural_warnings if w.severity == "SEVERE"]
            )
            raise ValueError(
                f"AST_INTEGRITY_VIOLATION: Pipeline halted due to topological corruption: {critical_errors}"
            )

        if self._pre_llm_validator:
            pre_llm_results = list(self._pre_llm_validator.validate_stream(nodes))
            hard_failures = [r for r in pre_llm_results if r.severity == ValidationSeverity.HARD_FAIL]
            if hard_failures:
                error_msgs = "; ".join([r.message for r in hard_failures])
                raise ValueError(f"PRE_LLM_VALIDATION_FAILED: {error_msgs}")

        context_enricher = HierarchicalContextEnricher()
        nodes, structured_registry, _warnings, _metrics = context_enricher.enrich_document(nodes)

        if self._context_registry is not None:
            self._context_registry.update(structured_registry["mappings"])

        job.document_id = job.job_id
        job.ast_hash = current_ast_hash
        job.pipeline_metadata["context_store"] = structured_registry

        # ── Fase 2: Determinar estado FSM ──
        doc_id = job.document_id or job.job_id
        snapshot = self.state_store.load(job_id=job.job_id)
        is_new_document = (snapshot is None) or (snapshot.ast_hash != current_ast_hash)

        if is_new_document:
            self.state_store.initialize(doc_id, current_ast_hash)
            fsm_state: str = "CREATED"
        else:
            assert snapshot is not None  # garantizado por is_new_document
            fsm_state = snapshot.state_value

        if fsm_state == "COMPLETED":
            raise ValueError(
                f"Operación abortada: El documento {job.job_id} ya fue procesado con éxito."
            )
        if fsm_state in ("FAILED_RETRYABLE", "FAILED_FATAL", "CANCELLED"):
            raise ValueError(
                f"Operación abortada: El documento {job.job_id} está en estado terminal {fsm_state}."
            )
        if fsm_state in ("READY_FOR_ASSEMBLY", "ASSEMBLING", "READY_FOR_COMPILATION", "COMPILING"):
            raise ValueError(
                f"Documento {job.job_id} en estado {fsm_state}. "
                f"La fase física está delegada al AssemblerWorkerDaemon."
            )

        job.mark_processing()

        try:
            # ── Fase 3: Emisión de comandos según estado FSM ──
            if fsm_state == "CREATED":
                job.enter_step(PipelineStep.PARSING)
                self._emit(job, StartParsingCommand)

            if fsm_state in ("CREATED", "PARSING"):
                job.enter_step(PipelineStep.CHUNKING)
                self._emit(job, StartProcessingCommand)

            # ── Fase 4: Trabajo real (chunk + persist + dispatch) ──
            active_registry = job.pipeline_metadata["context_store"]["mappings"]
            for node in nodes:
                if node.node_type != ContentNodeType.HEADING:
                    ctx_id = node.control_plane.get("context_id")
                    if ctx_id and ctx_id not in active_registry:
                        raise ValueError(
                            f"STATE_CORRUPTION: Node {node.node_id} references "
                            f"a missing context token {ctx_id} post-hydration."
                        )

            translation_units = self.chunker.chunk(nodes)
            self.document_repository.save_batch(job.job_id, translation_units)

            job.enter_step(PipelineStep.DISPATCHING)
            dispatch_result = await self.dispatcher.dispatch(translation_units)

            # Emitir MarkAssemblyReadyCommand al finalizar el trabajo
            self._emit(job, MarkAssemblyReadyCommand)

            # ── Fase 5: HANDOFF al Execution Plane ──
            # NADR-06 §5.3: El ensamblado físico es responsabilidad
            # del AssemblerWorkerDaemon, no del pipeline lógico.
            # DispatchResult se usa solo para auditoría del dispatch.
            summary = self.audit_builder.build(dispatch_result)
            job.mark_completed(summary)

            pipeline_result = PipelineResult(
                document=None,
                summary=summary,
                assembly_report=None,
            )

        except Exception as e:
            job.mark_failed(error_type=e.__class__.__name__, error_message=str(e))
            try:
                snapshot_for_fail = self.state_store.load(job_id=job.job_id)
                if snapshot_for_fail is not None:
                    self._emit(job, FailDocumentCommand, reason=str(e)[:250])
            except Exception:
                pass
            raise

        return pipeline_result