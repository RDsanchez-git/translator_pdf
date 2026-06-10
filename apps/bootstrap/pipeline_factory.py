# apps/bootstrap/pipeline_factory.py
"""Composition Root libre de introspección por patito (hasattr) y desacoplado de dependencias cruzadas."""

from typing import Optional, Any
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore, StateStoreProtocol
from core.pipeline.orchestrator import TranslationPipeline, ChunkerProtocol, AuditBuilderProtocol
from infra.adapters.pdf_parser import PdfParserAdapter
from core.metrics.summary import SummaryBuilder
from core.compiler.assembler import DocumentAssembler
from core.ast.parser import parse_pdf

# Infraestructura de validación y curación nativa (Problema 1)
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
    parser = PdfParserAdapter(parser_callable=parse_pdf, verify_output=True)
    assembler = DocumentAssembler(separator="\n\n")
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
    
    # Inyección explícita por propiedades sin verificación de atributos en runtime (Problema 2)
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
        state_store=state_store
    )