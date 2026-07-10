import logging
from typing import Protocol, List, Dict
from collections import defaultdict

from core.ast.models import ASTNode, DispatchResult
from core.ast.enums import ContentNodeType
from core.compiler.assembler import (
    DocumentAssembler, 
    IntegrityCheckedDocumentRepository,
    PayloadNotFoundError,
    HashMismatchError,
    RepositoryUnavailableError
)
from core.compiler.exceptions import AssemblyRejectedError, ProfileNotFoundError, ASTConsistencyError
from core.document_profile.models import InferredDocumentProfile
from core.compiler.rendering.mapper import RenderUnitMapper
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.models import RenderUnit
from apps.compiler.tex_builder import TexBuilder

logger = logging.getLogger(__name__)

class ASTProviderProtocol(Protocol):
    def get_document_ast(self, document_id: str, ast_hash: str) -> List[ASTNode]: ...

class ProfileStoreProtocol(Protocol):
    def get_profile(self, document_id: str) -> InferredDocumentProfile | None: ...

class CompilationService:
    def __init__(self, 
                 assembler: DocumentAssembler,
                 payload_repository: IntegrityCheckedDocumentRepository,
                 ast_provider: ASTProviderProtocol,
                 profile_store: ProfileStoreProtocol,
                 mapper: RenderUnitMapper):
        self._assembler = assembler
        self._payload_repository = payload_repository
        self._ast_provider = ast_provider
        self._profile_store = profile_store
        self._mapper = mapper

    def compile_document(self, job_id: str, ast_hash: str, dispatch_result: DispatchResult) -> str:
        log_ctx = {"job_id": job_id, "ast_hash": ast_hash}
        logger.info("Iniciando compilación LaTeX", extra=log_ctx)
        
        decision = self._assembler.assemble(job_id, dispatch_result)
        if not decision.is_accepted:
            raise AssemblyRejectedError(f"Ensamblado denegado: {decision.rejection_reason}")
            
        profile = self._profile_store.get_profile(job_id)
        if not profile:
            raise ProfileNotFoundError(f"InferredDocumentProfile ausente para job: {job_id}")
            
        ast_nodes = self._ast_provider.get_document_ast(job_id, ast_hash)
        if not ast_nodes:
            raise ASTConsistencyError(f"AST vacío o hash {ast_hash} no encontrado.")
            
        nodes_by_chunk: Dict[str, List[ASTNode]] = defaultdict(list)
        for node in ast_nodes:
            chunk_id = node.control_plane.get("chunk_id")
            if chunk_id:
                nodes_by_chunk[chunk_id].append(node)

        # Contrato Explícito Fail-Fast: Si hay nodos pero ninguno tiene chunk_id, la Fase 15 falló.
        if ast_nodes and not nodes_by_chunk:
            raise ASTConsistencyError(
                "Violación de Contrato: El Chunker no persistió 'chunk_id' en el control_plane del AST. "
                "Imposible reconciliar topología 1:N."
            )

        render_units: List[RenderUnit] = []
        
        for outcome in sorted(dispatch_result.outcomes, key=lambda x: x.chunk_index):
            chunk_ctx = {**log_ctx, "chunk_id": outcome.chunk_id}
            target_nodes = nodes_by_chunk.get(outcome.chunk_id, [])
            
            if outcome.is_success and outcome.translated_unit:
                text = outcome.translated_unit.translated_payload
            else:
                try:
                    text = self._payload_repository.get_verified_payload(
                        job_id, outcome.chunk_id, outcome.original_payload_sha256
                    )
                except (PayloadNotFoundError, HashMismatchError) as e:
                    raise ASTConsistencyError(f"Fallo de integridad referencial en fallback: {e}")
                except RepositoryUnavailableError:
                    logger.critical("Base de datos de payloads inaccesible durante degradación.", extra=chunk_ctx)
                    raise

            if target_nodes:
                render_units.append(self._mapper.map_to_unit(target_nodes, text))
            else:
                logger.warning("Chunk carece de linaje en el AST. Forzando degradación estructural.", extra=chunk_ctx)
                render_units.append(RenderUnit(
                    node_id=f"orphan_{outcome.chunk_id}",
                    node_type=ContentNodeType.PARAGRAPH,
                    content=text,
                    geometry=None,
                    asset=None
                ))

        context = RenderContextFactory.create(profile)
        builder = TexBuilder(context)
        
        return builder.build(render_units)