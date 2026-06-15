from __future__ import annotations
import re
from typing import Protocol, List
from dataclasses import dataclass
from core.pipeline.job import TranslationJob, PipelineStep
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, ReconstructedDocument, ContentNodeType
from core.metrics.summary import TranslationAuditSummary
from core.pipeline.state_store import StateStoreProtocol
from core.normalization.classifier import SemanticNodeClassifier
from core.normalization.fixers.asset_placeholder import StructuralAssetPlaceholder
from core.normalization.validators.ast_integrity import ASTIntegrityValidator
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher
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
        
        self._exotic_bullets = re.compile(r'^\s*([•▪‣◦■♦○]|[-‑‒–—-]>\s*)\s*')

    async def execute(self, job: TranslationJob) -> PipelineResult:
        """Punto de entrada único. Ejecuta transformaciones guiadas por un flujo lineal uniforme."""
        
        # SOTA: Parseo único y temprano para cálculo del invariante genético (Evita Doble I/O)
        nodes = self.parser.parse(job.source_path)
        
        # Sello de versionado del esquema estructural (Alineación defensiva)
        if not hasattr(job, "pipeline_metadata"):
            job.pipeline_metadata = {}
        job.pipeline_metadata["ast_schema_version"] = "1.0.1"
        
        # 1. Enmienda heurística del OCR (Fase 12.00.1)
        classifier = SemanticNodeClassifier()
        nodes = classifier.classify_batch(nodes)
        
        # 2. Marcado, higiene léxica y aislamiento de activos estructurales (Fase 12.00.5)
        placeholder_fixer = StructuralAssetPlaceholder()
        processed_nodes = []
        for node in nodes:
            text = node.content or ""
            text_stripped = text.strip()

            # Higiene A: Neutralización de contaminación por espacios (In-place)
            if not text_stripped:
                if node.content != "":
                    node = node.model_copy(update={"content": ""})
                processed_nodes.append(node)
                continue

            # Higiene B: Estandarización de viñetas visuales puras
            if node.type == ContentNodeType.LIST_ITEM:
                if self._exotic_bullets.match(text):
                    text = self._exotic_bullets.sub("- ", text, count=1)
                    node = node.model_copy(update={"content": text})

            # Aislamiento de activos
            if node.type in {ContentNodeType.TABLE, ContentNodeType.FIGURE, ContentNodeType.IMAGE}:
                new_cp = dict(node.control_plane)
                new_cp["preserved_content"] = text
                new_cp["preserve_original"] = True
                new_cp["asset_type"] = node.type.value.upper()
                
                result = placeholder_fixer.normalize(
                    text=text, 
                    node_id=node.node_id, 
                    node_type=node.type.value
                )
                
                node = node.model_copy(update={
                    "content": result.text,
                    "control_plane": new_cp
                })
            processed_nodes.append(node)
        nodes = processed_nodes
        
        current_ast_hash = compute_ast_hash(nodes)

        # 3. Validación de Integridad Estructural del AST (Fase 12.00.6 - Fail-Fast)
        validator = ASTIntegrityValidator()
        structural_warnings = validator.validate_ast(nodes)
        
        if any(w.severity == "SEVERE" for w in structural_warnings):
            critical_errors = "; ".join([w.message for w in structural_warnings if w.severity == "SEVERE"])
            raise ValueError(f"AST_INTEGRITY_VIOLATION: Pipeline halted due to topological corruption: {critical_errors}")

        # 4. Enriquecimiento Jerárquico Relacional Inmune (Fase 12.00.8 - BLAKE2b)
        context_enricher = HierarchicalContextEnricher()
        nodes, structured_registry, enricher_warnings, enricher_metrics = context_enricher.enrich_document(nodes)

        # Inyección de metadatos operacionales en el DTO de dominio y persistencia
        job.document_id = job.job_id
        job.ast_hash = current_ast_hash
        job.pipeline_metadata["context_store"] = structured_registry

        # 5. Búsqueda de Reanudación y Activación del Guardián Genético (Anti-Corruption)
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
            
            # -----------------------------------------------------------------
            # BARRERA DE CONTROL: Verificación cruzada en la frontera de segmentación
            # -----------------------------------------------------------------
            active_registry = job.pipeline_metadata["context_store"]["mappings"]
            for node in nodes:
                if node.type != ContentNodeType.HEADING:
                    ctx_id = node.control_plane.get("context_id")
                    if ctx_id and ctx_id not in active_registry:
                        raise ValueError(f"STATE_CORRUPTION: Node {node.node_id} references a missing context token {ctx_id} post-hydration.")
            
            translation_units = self.chunker.chunk(nodes)
            
            job.enter_step(PipelineStep.DISPATCHING)
            translated_units = await self.dispatcher.dispatch(translation_units)

            job.enter_step(PipelineStep.ASSEMBLING)
            self.state_store.save(job)

            reconstructed_doc = self.assembler.assemble(translated_units)

            job.enter_step(PipelineStep.AUDITING)
            summary = self.audit_builder.build(translated_units, reconstructed_doc)

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