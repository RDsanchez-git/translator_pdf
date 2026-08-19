"""
Composition Root único del pipeline de traducción.

NADR-11 §5.1 R1: Este es el ÚNICO punto de construcción del grafo de objetos.
NADR-11 §5.1 R2: Cero mutaciones post-constructor.
NADR-04 §5.1 R2: ValidationPipeline y HealingPipeline se inyectan por constructor.
"""
import os
from typing import Optional

from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore, StateStoreProtocol
from core.pipeline.orchestrator import TranslationPipeline, ChunkerProtocol, AuditBuilderProtocol
from infra.adapters.pdf_parser import PdfParserAdapter
from core.metrics.summary import SummaryBuilder

from core.ast.models import ASTNode
from infra.db.document_repository import SQLiteDocumentRepository

from core.ast.builder import FlatASTBuilder

# Validación y curación (NADR-04: sin LegacyValidatorAdapter)
from core.validation.factory import build_validation_pipeline
from core.validation.pipeline import ValidationPipeline
from core.validation.ast.factory import build_default_validation_engine
from core.healing.pipeline import HealingPipeline
from core.healing.strategies.markdown_leakage import MarkdownLeakageHealingStrategy
from core.healing.strategies.meta_text_leakage import MetaTextLeakageHealingStrategy
from core.healing.strategies.structural import EOFBraceClosureStrategy, EOFMathClosureStrategy
from core.healing.config import HealingPolicy
from core.normalization.bootstrap import bootstrap_normalization_layer

# Layout validation (NADR-04 §5.1 R1)
from core.layout.validator import DocumentLayoutValidator

from core.document_profile.profiler import HeuristicDocumentProfiler
from core.document_profile.detectors.layout import HeuristicLayoutDetector
from core.document_profile.detectors.semantic import HeuristicTypeDetector
from infra.adapters.ast_profiling import NodeGeometryAdapter, NodeSemanticAdapter, FirstPagesSamplingPolicy

from core.domain.document import DocumentLayout
from core.layout.models import LayoutBlockCollection

from apps.bootstrap.extraction_config import ExtractionConfiguration, ExtractionProviderId
from apps.bootstrap.provider_factory import ExtractionProviderFactory

# Dispatcher (NADR-11: construcción interna)
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.routing import LLMProvider

from core.layout.models import LayoutBlockDraft
from core.domain.document import LayoutBlock, BoundingBox

from core.context.context_registry import ContextRegistry
from core.context.dynamic_resolver import DynamicContextResolver




def build_healing_pipeline(validation_pipeline: ValidationPipeline) -> HealingPipeline:
    """
    NADR-04: HealingPipeline se construye SOBRE la misma instancia de ValidationPipeline.
    Nunca dos ValidationPipeline distintos.
    """
    policy = HealingPolicy()
    strategies = [
        MarkdownLeakageHealingStrategy(),
        MetaTextLeakageHealingStrategy(),
        EOFBraceClosureStrategy(policy=policy),
        EOFMathClosureStrategy(policy=policy)
    ]
    return HealingPipeline(validation_pipeline, strategies)


# En build_pipeline(), actualizar la llamada:
def build_pipeline(
    chunker: ChunkerProtocol,
    prompt_builder: PromptBuilder,
    provider_stack: LLMProvider,
    concurrency: int = 20,
    extraction_config: ExtractionConfiguration | None = None,
    audit_override: Optional[AuditBuilderProtocol] = None,
    state_store_override: Optional[StateStoreProtocol] = None,
) -> TranslationPipeline:
    """
    Composition Root único del pipeline de traducción.

    NADR-05 §5.1 R1-R2: El resolver de contexto se construye aquí
    con un provider real. No se inyecta DummyContextResolver.
    NADR-11 §5.1 R1-R2: Cero mutaciones post-constructor.
    """
    bootstrap_normalization_layer()

    # 1. Validación y curación
    validation_pipeline = build_validation_pipeline()
    healing_pipeline = build_healing_pipeline(validation_pipeline)

    # 2. Context stack (NADR-05 §5.1 R1)
    context_registry, context_resolver = _build_context_stack()

    # 3. Dispatcher completo
    dispatcher = AsyncDispatcher(
        context_resolver=context_resolver,
        prompt_builder=prompt_builder,
        provider_stack=provider_stack,
        validation_pipeline=validation_pipeline,
        healing_pipeline=healing_pipeline,
        concurrency=concurrency,
    )

    # 4. Parser
    if extraction_config is None:
        extraction_config = ExtractionConfiguration(provider_id=ExtractionProviderId.PYMUPDF)
    parser: PdfParserAdapter = build_extraction_pipeline(extraction_config)

    # 5. Repositorio de documentos
    doc_conn = get_connection("infra/db/documents.db", timeout=30)
    document_repository = SQLiteDocumentRepository(doc_conn)

    # 6. Audit builder
    audit_builder = audit_override or SummaryBuilder()

    # 7. State store
    if state_store_override:
        state_store = state_store_override
    else:
        fsm_conn = get_connection("infra/db/fsm.db", timeout=30)
        fsm_repo = FSMRepository(fsm_conn)
        command_handler = DocumentCommandHandler(fsm_repo)
        state_store = FSMStateStore(fsm_repo, command_handler)

    # 8. Pre-LLM validator
    pre_llm_engine = build_default_validation_engine()

    # 9. TranslationPipeline
    return TranslationPipeline(
        parser=parser,
        chunker=chunker,
        dispatcher=dispatcher,
        audit_builder=audit_builder,
        state_store=state_store,
        document_repository=document_repository,
        pre_llm_validator=pre_llm_engine,
        context_registry=context_registry,
    )


def build_document_profiler() -> HeuristicDocumentProfiler:
    """Ensambla el servicio de perfilado inyectando configuración de infraestructura."""
    max_sampling_pages = int(os.getenv("PROFILER_MAX_SAMPLING_PAGES", "5"))

    geom_adapter = NodeGeometryAdapter()
    semantic_adapter = NodeSemanticAdapter()

    sampler = FirstPagesSamplingPolicy(geom_extractor=geom_adapter, max_pages=max_sampling_pages)
    layout_detector = HeuristicLayoutDetector(geom_extractor=geom_adapter)
    type_detector = HeuristicTypeDetector(semantic_adapter=semantic_adapter)

    return HeuristicDocumentProfiler(
        layout_detector=layout_detector,
        type_detector=type_detector,
        sampler=sampler
    )

def build_extraction_pipeline(config: ExtractionConfiguration | None = None) -> PdfParserAdapter:
    """
    Factoría única del pipeline de extracción de producción.
    """
    if config is None:
        config = ExtractionConfiguration(provider_id=ExtractionProviderId.PYMUPDF)
    
    provider = ExtractionProviderFactory.create(config.provider_id)
    mapper = FlatASTBuilder()
    layout_validator = DocumentLayoutValidator()

    def _layout_block_to_draft(block: LayoutBlock, page_number: int, reading_order: int) -> LayoutBlockDraft:
        """
        Traduce LayoutBlock (dominio) a LayoutBlockDraft (DTO de FlatASTBuilder).
        
        DF-12: LayoutBlockDraft pertenece al legacy DocumentLayoutBuilder (zombi).
        Este mapper es transicional. En Gate 3, FlatASTBuilder debe consumir
        LayoutBlock directamente, eliminando LayoutBlockDraft y LayoutBlockCollection.
        """
        return LayoutBlockDraft(
            block_id=block.block_id,
            logical_type=block.logical_type.value,
            content=block.content.normalized,
            bbox=block.bbox if block.bbox is not None else BoundingBox(x0=0, y0=0, x1=1, y1=1),
            confidence=block.metadata.confidence.ocr if block.metadata.confidence else 1.0,
            provider_native_id=str(block.metadata.provider.native_block_index) if block.metadata.provider else None,
            page_index=page_number,
            column_index=block.metadata.spatial.column_index if block.metadata.spatial else 0,
        )

    def _adapter_mapper(document_layout: DocumentLayout) -> list[ASTNode]:
        """Valida el layout, traduce bloques y construye el AST."""
        report = layout_validator.validate(document_layout)
        if not report.is_valid:
            error_summary = "; ".join(report.errors)
            raise ValueError(f"LAYOUT_VALIDATION_FAILED: {error_summary}")

        # DF-12: Traducción explícita LayoutBlock → LayoutBlockDraft
        draft_blocks: list[LayoutBlockDraft] = []
        reading_order = 0
        for page in document_layout.pages:
            for block in page.blocks:
                draft = _layout_block_to_draft(block, page.page_number, reading_order)
                draft_blocks.append(draft)
                reading_order += 1
        
        collection = LayoutBlockCollection(blocks=draft_blocks)
        return mapper.build(collection)

    return PdfParserAdapter(
        provider=provider,
        layout_to_ast_mapper=_adapter_mapper
    )

def _build_context_stack() -> tuple[ContextRegistry, DynamicContextResolver]:
    """
    Construye el subsistema de resolución de contexto.

    NADR-05 §5.1 R1: El contexto debe ser una capacidad real.
    NADR-11 §5.1 R1: El Composition Root es el único punto de construcción.

    Retorna:
        - ContextRegistry: dueño único de los mappings (se actualiza en execute())
        - DynamicContextResolver: resolver que consulta el registry dinámicamente
    """
    registry = ContextRegistry()
    resolver = DynamicContextResolver(registry=registry)
    return registry, resolver