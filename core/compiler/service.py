# core/compiler/service.py
"""
Servicio canónico de compilación física.

NADR-06 §5.3 R9: Ensamblado gobernado por servicio canónico.
NADR-06 §5.3 R10: Sin ensamblado ad-hoc en el plano de ejecución.

Nota: ASTProviderProtocol NO es dependencia de este servicio.
El AST ya está resuelto en AssemblyExecutionContext por el Resolver.
"""
import logging
from typing import List

from core.compiler.assembler import (
    DocumentAssembler,
    IntegrityCheckedDocumentRepository,
    PayloadNotFoundError,
    HashMismatchError,
    RepositoryUnavailableError
)
from core.compiler.assembly_context import AssemblyExecutionContext
from core.compiler.exceptions import AssemblyRejectedError, ProfileNotFoundError, ASTConsistencyError
from core.document_profile.ports import ProfileStore
from core.compiler.rendering.mapper import RenderUnitMapper
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.models import RenderUnit, AssetReference
from core.ast.enums import ContentNodeType
from apps.compiler.tex_builder import TexBuilder

logger = logging.getLogger(__name__)


class CompilationService:
    """
    Servicio canónico de compilación física.

    Responsabilidades:
    - Obtener perfil documental
    - Resolver contenido por nodo (projections + fallback)
    - Mapear a RenderUnits
    - Renderizar LaTeX

    NO es responsabilidad de este servicio:
    - Decidir política de ensamblado (pertenece al Assembler)
    - Cargar AST (pertenece al Resolver)
    """

    def __init__(
        self,
        assembler: DocumentAssembler,
        payload_repository: IntegrityCheckedDocumentRepository,
        profile_store: ProfileStore,
        mapper: RenderUnitMapper,
    ):
        self._assembler = assembler
        self._payload_repository = payload_repository
        self._profile_store = profile_store
        self._mapper = mapper

    def compile_document(self, context: AssemblyExecutionContext) -> str:
        """Legacy text-only caller: refuse to silently omit image dependencies."""
        tex, assets = self.compile_document_with_assets(context)
        if assets:
            raise ASTConsistencyError("B02_G5_IMAGE_BUNDLE_REQUIRED")
        return tex

    def compile_document_with_assets(
        self, context: AssemblyExecutionContext
    ) -> tuple[str, tuple[AssetReference, ...]]:
        """Render an isolated TeX document plus its explicit asset dependencies.

        This is still an assembler read, not publication or execution authority.
        """
        log_ctx = {"document_id": context.document_id[:12], "ast_hash": context.ast_hash[:12]}
        logger.info("Iniciando compilación LaTeX", extra=log_ctx)

        # Paso 1: Ensamblado lógico con políticas (decisión)
        decision = self._assembler.assemble(context)
        if not decision.is_accepted:
            raise AssemblyRejectedError(f"Ensamblado denegado: {decision.rejection_reason}")

        # Paso 2: Obtener perfil documental
        profile = self._profile_store.get(context.document_id)
        if not profile:
            raise ProfileNotFoundError(f"InferredDocumentProfile ausente para job: {context.document_id}")

        # Paso 3: Resolver contenido por nodo (única materialización)
        projection_map = {p.node_id: p for p in context.projections}
        render_units: List[RenderUnit] = []

        for node in context.ast_nodes:
            if node.node_id in projection_map:
                text = projection_map[node.node_id].normalized_response
            else:
                # Fallback con integridad criptográfica
                chunk_id = node.control_plane.get("chunk_id", "")
                payload_sha256 = node.control_plane.get("payload_sha256", "")
                try:
                    text = self._payload_repository.get_verified_payload(
                        context.document_id, chunk_id, payload_sha256
                    )
                except (PayloadNotFoundError, HashMismatchError) as e:
                    raise ASTConsistencyError(f"Fallo de integridad referencial en fallback: {e}")
                except RepositoryUnavailableError:
                    logger.critical("Base de datos de payloads inaccesible.", extra=log_ctx)
                    raise

            render_units.append(self._mapper.map_to_unit([node], text))

        # Paso 4: Renderizado LaTeX
        render_context = RenderContextFactory.create(profile)
        builder = TexBuilder(render_context)

        assets: list[AssetReference] = []
        for unit in render_units:
            if unit.node_type == ContentNodeType.IMAGE:
                if unit.asset is None:
                    raise ASTConsistencyError("B02_G5_IMAGE_ASSET_REFERENCE_MISSING")
                assets.append(unit.asset)
        return builder.build(render_units), tuple(assets)