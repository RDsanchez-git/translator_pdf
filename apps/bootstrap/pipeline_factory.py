"""Composition Root libre de introspección por patito (hasattr) y desacoplado de dependencias cruzadas."""
import os
from typing import Optional, Any
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore, StateStoreProtocol
from core.pipeline.orchestrator import TranslationPipeline, ChunkerProtocol, AuditBuilderProtocol
from infra.adapters.pdf_parser import PdfParserAdapter
from core.metrics.summary import SummaryBuilder

# SOTA Fase 15.4-D: Importaciones del Motor de Ensamblado e Hidratación
from core.ast.models import FailureReason, ASTNode
from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
from infra.db.document_repository import SQLiteDocumentRepository

# Importaciones SOTA para el adaptador hexagonal
from core.extraction.ocr_providers.pymupdf_provider import PyMuPDFProvider
from core.ast.builder import FlatASTBuilder

# Infraestructura de validación y curación nativa
from core.validation.pipeline import ValidationPipeline
from core.validation.models import Severity
from core.validation.legacy_adapter import LegacyValidatorAdapter
from core.validation.structural_validator import StructuralValidator
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator
from core.validation.volumetric import VolumetricValidator

from core.healing.pipeline import HealingPipeline
from core.healing.strategies.markdown_leakage import MarkdownLeakageHealingStrategy
from core.healing.strategies.meta_text_leakage import MetaTextLeakageHealingStrategy
from core.healing.strategies.structural import EOFBraceClosureStrategy, EOFMathClosureStrategy
from core.healing.config import HealingPolicy
from core.normalization.bootstrap import bootstrap_normalization_layer

from core.document_profile.profiler import HeuristicDocumentProfiler
from core.document_profile.detectors.layout import HeuristicLayoutDetector
from core.document_profile.detectors.semantic import HeuristicTypeDetector
from infra.adapters.ast_profiling import NodeGeometryAdapter, NodeSemanticAdapter, FirstPagesSamplingPolicy

from core.layout.builder import DocumentLayout
from core.layout.models import LayoutBlockCollection

def _build_default_validation_pipeline() -> ValidationPipeline:
    """Aislamiento explícito de la composición del pipeline de análisis sintáctico."""
    severity_map = {
        "RESIDUAL_HTML": Severity.HARD_FAIL,
        "UNBALANCED_BRACES_EARLY": Severity.HARD_FAIL,
        "UNBALANCED_BRACES_OPEN": Severity.HARD_FAIL,
        "UNBALANCED_BRACKETS_EARLY": Severity.HARD_FAIL,
        "UNBALANCED_BRACKETS_OPEN": Severity.HARD_FAIL,
        "UNBALANCED_DISPLAY_MATH": Severity.HARD_FAIL,
        "UNBALANCED_INLINE_MATH": Severity.HARD_FAIL,
        "ENV_MISMATCH": Severity.HARD_FAIL,
        "ENV_UNCLOSED": Severity.HARD_FAIL,
    }
    adapter = LegacyValidatorAdapter(StructuralValidator, severity_map)
    pipeline = ValidationPipeline()
    pipeline.add_chunk_validator(adapter)
    pipeline.add_document_validator(adapter)
    pipeline.add_chunk_validator(PreservationValidator())
    pipeline.add_chunk_validator(PerimeterValidator())
    pipeline.add_chunk_validator(SemanticValidator())
    pipeline.add_chunk_validator(VolumetricValidator())
    pipeline.add_document_validator(PreservationValidator())
    return pipeline


def build_pipeline(
    chunker: ChunkerProtocol,
    dispatcher: Any,  # AsyncDispatcher libre de duck-typing
    audit_override: Optional[AuditBuilderProtocol] = None,
    state_store_override: Optional[StateStoreProtocol] = None
) -> TranslationPipeline:
    """Composition Root encargado del wiring explícito mediante asignación de inyección directa."""
    bootstrap_normalization_layer()
    
    # SOTA FIX: Encapsulamiento estricto mediante función interna tipada
    provider = PyMuPDFProvider()
    mapper = FlatASTBuilder()
    
    def _adapter_mapper(document_layout: DocumentLayout) -> list[ASTNode]:
        """SOTA FIX: Extrae y aplana los bloques del Aggregate jerárquico."""
        # Aplanar todos los bloques de todas las páginas físicas
        flat_blocks = []
        for page in document_layout.pages:
            flat_blocks.extend(page.blocks)
            
        # Empaquetar en el DTO que la firma de FlatASTBuilder exige estrictamente.
        # (Si LayoutBlockCollection se instancia pasando un argumento posicional, usa LayoutBlockCollection(flat_blocks))
        collection = LayoutBlockCollection(blocks=flat_blocks) 
        
        return mapper.build(collection)

    parser = PdfParserAdapter(
        provider=provider, 
        layout_to_ast_mapper=_adapter_mapper
    )
    
    # -----------------------------------------------------------------
    # SOTA Fase 15.4: Setup del Repositorio de Hidratación y Políticas
    # -----------------------------------------------------------------
    doc_conn = get_connection("infra/db/documents.db", timeout=30)
    document_repository = SQLiteDocumentRepository(doc_conn)
    
    assembly_policy = AssemblyPolicy(
        tolerance_ratio=0.05, # Tolerancia del 5% de fallos a nivel documento
        allow_fallback=True,  # Activa la mitigación (Graceful Degradation)
        degradable_failures=frozenset([
            FailureReason.CONTEXT_OVERFLOW,
            FailureReason.PROVIDER_FAILURE,
            FailureReason.RETRY_EXHAUSTED
            # NOTA: VALIDATION_FAILURE intencionalmente excluido. (Hard Fail)
        ])
    )
    
    assembler = DocumentAssembler(
        repository=document_repository, 
        separator="\n\n", 
        policy=assembly_policy
    )
    # -----------------------------------------------------------------

    audit_builder = audit_override or SummaryBuilder()
    
    # Construcción desacoplada aislada de los entornos del Dispatcher
    validation_pipeline = _build_default_validation_pipeline()

    policy = HealingPolicy()
    strategies = [
        MarkdownLeakageHealingStrategy(),
        MetaTextLeakageHealingStrategy(),
        EOFBraceClosureStrategy(policy=policy),
        EOFMathClosureStrategy(policy=policy)
    ]

    healing_pipeline = HealingPipeline(validation_pipeline, strategies)
    
    # Inyección explícita por propiedades sin verificación de atributos en runtime
    dispatcher.validation_pipeline = validation_pipeline
    dispatcher.healing_pipeline = healing_pipeline
    
    if state_store_override:
        state_store = state_store_override
    else:
        fsm_conn = get_connection("infra/db/fsm.db", timeout=30)
        fsm_repo = FSMRepository(fsm_conn)
        command_handler = DocumentCommandHandler(fsm_repo)
        state_store = FSMStateStore(fsm_repo, command_handler)
        
    return TranslationPipeline(
        parser=parser,
        chunker=chunker,
        dispatcher=dispatcher,
        assembler=assembler,
        audit_builder=audit_builder,
        state_store=state_store,
        document_repository=document_repository
    )

def build_document_profiler() -> HeuristicDocumentProfiler:
    """Ensambla el servicio de perfilado inyectando configuración de infraestructura."""
    # Configuración paramétrica
    max_sampling_pages = int(os.getenv("PROFILER_MAX_SAMPLING_PAGES", "5"))

    geom_adapter = NodeGeometryAdapter()
    semantic_adapter = NodeSemanticAdapter()

    # Inyección
    sampler = FirstPagesSamplingPolicy(geom_extractor=geom_adapter, max_pages=max_sampling_pages)
    layout_detector = HeuristicLayoutDetector(geom_extractor=geom_adapter)
    type_detector = HeuristicTypeDetector(semantic_adapter=semantic_adapter)

    return HeuristicDocumentProfiler(
        layout_detector=layout_detector,
        type_detector=type_detector,
        sampler=sampler
    )