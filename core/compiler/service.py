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
    AssemblyStatus,
    DocumentAssembler,
    IntegrityCheckedDocumentRepository,
)
from core.compiler.assembly_context import AssemblyExecutionContext
from core.compiler.exceptions import AssemblyRejectedError, ProfileNotFoundError, ASTConsistencyError
from core.document_profile.ports import ProfileStore
from core.compiler.rendering.mapper import RenderUnitMapper
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.implementations import usable_image_width
from core.compiler.rendering.models import RenderUnit, AssetReference
from core.ast.enums import ContentNodeType
from apps.compiler.tex_builder import TexBuilder

logger = logging.getLogger(__name__)


class CompilationService:
    """
    Servicio canónico de compilación física.

    Responsabilidades:
    - Obtener perfil documental
    - Resolver contenido por nodo a partir de proyecciones CURRENT completas
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
        # Retain the existing constructor contract; historical backing is not
        # an authority for conforming PPPR reconstruction (DC-12).
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
        # DC-12 / FPPPR-02 R8: the legacy assembler may accept a DEGRADED
        # decision for diagnostic purposes, but this service feeds final PDF
        # publication. Only a complete SUCCESS can cross this boundary.
        if decision.status != AssemblyStatus.SUCCESS:
            missing = ascii(decision.missing_node_ids)
            if decision.status == AssemblyStatus.DEGRADED:
                raise AssemblyRejectedError(
                    f"PPPR_G4_DEGRADED_ASSEMBLY_FORBIDDEN missing_node_ids={missing}"
                )
            raise AssemblyRejectedError(
                f"PPPR_G4_ASSEMBLY_REJECTED missing_node_ids={missing}; "
                f"reason={decision.rejection_reason}"
            )

        # Paso 2: Obtener perfil documental
        profile = self._profile_store.get(context.document_id)
        if not profile:
            raise ProfileNotFoundError(f"InferredDocumentProfile ausente para job: {context.document_id}")

        # Paso 3: Resolver contenido por nodo (única materialización)
        projection_map = {p.node_id: p for p in context.projections}
        render_units: List[RenderUnit] = []

        for node in context.ast_nodes:
            projection = projection_map.get(node.node_id)
            if projection is None:
                # Defensive invariant: even an inconsistent SUCCESS must not
                # silently substitute an original payload.
                raise ASTConsistencyError(
                    f"PPPR_G4_CURRENT_PROJECTION_REQUIRED node_id={ascii(node.node_id)}"
                )
            text = projection.normalized_response

            rendered = self._mapper.map_to_unit([node], text)
            # G2 can attest partial physical regions. Never silently substitute
            # fabricated geometry when such provenance is present but invalid.
            if node.metadata.physical_regions and rendered.geometry is None:
                # FPPPR-04 R9: provenance that cannot be transformed is
                # attributable uncertainty, not an automatic rejection of
                # unrelated logical content. No synthetic geometry is emitted.
                logger.warning(
                    "PPPR_G4_GEOMETRY_UNVERIFIED node_id=%r",
                    node.node_id,
                    extra=log_ctx,
                )
            render_units.append(rendered)

        # Paso 4: Renderizado LaTeX
        render_context = RenderContextFactory.create(profile)
        # NADR-FPPPR-02 R8 / FPPPR-04 R9: unknown two-column image
        # width cannot be represented as verified narrow. Keep independent
        # text renderable, but refuse conforming publication of this image.
        for unit in render_units:
            if (render_context.is_multi_column
                    and unit.node_type == ContentNodeType.IMAGE
                    and usable_image_width(unit.geometry) is None):
                safe_id = ascii(unit.node_id)
                logger.error(
                    "PPPR_G4_IMAGE_WIDTH_UNVERIFIED node_id=%s",
                    safe_id, extra=log_ctx,
                )
                raise ASTConsistencyError(
                    f"PPPR_G4_IMAGE_WIDTH_UNVERIFIED node_id={safe_id}"
                )
        builder = TexBuilder(render_context)

        assets: list[AssetReference] = []
        for unit in render_units:
            if unit.node_type == ContentNodeType.IMAGE:
                if unit.asset is None:
                    raise ASTConsistencyError("B02_G5_IMAGE_ASSET_REFERENCE_MISSING")
                assets.append(unit.asset)
        return builder.build(render_units), tuple(assets)