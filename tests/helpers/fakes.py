from typing import List
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, TranslationTaskType

class FakeChunker:
    """Implementación de control estricta para cumplir con ChunkerProtocol."""
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]:
        return [
            TranslationUnit(
                chunk_index=1,
                chunk_id="chk_mock_001",
                chunk_fingerprint="mock_fingerprint_001",  # SOTA: Propiedad añadida en Fase 13
                chunk_type=TranslationTaskType.TRANSLATE,  # SOTA: Uso estricto del Enum
                source_sequence_range=(1, max(1, len(nodes))),
                node_count=len(nodes),
                context_id="CTX_GLOBAL_MOCK",              # SOTA: Reemplaza a reference_context
                context_depth=1,                           # SOTA: Propiedad añadida en Fase 13
                target_payload="Payload extraído del AST real",
                estimated_tokens=150,
                payload_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            )
        ]

class FakeDispatcher:
    """Implementación asíncrona de control homologada para el PricingEngine."""
    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        return [
            TranslatedUnit(
                chunk_index=u.chunk_index,
                chunk_id=u.chunk_id,
                # Extracción segura del valor primitivo del Enum para serialización mock
                chunk_type=u.chunk_type.value if hasattr(u.chunk_type, "value") else u.chunk_type, 
                source_sequence_range=u.source_sequence_range,
                translated_payload="Texto traducido simulado",
                payload_sha256=u.payload_sha256,
                model_name="gemini-2.5-flash",
                prompt_version="v3_latex_optimized",
                input_tokens=120,
                output_tokens=140,
                latency_ms=45.2
            ) for u in units
        ]