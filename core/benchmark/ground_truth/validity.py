from __future__ import annotations

from typing import Tuple

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode
from core.ast.validator import ASTValidationError, ASTValidator
from core.benchmark.ground_truth.errors import OracleValidityError


class OracleValidityContract:
    """Contrato de validez estructural del oráculo (NADR-13 §5.1).

    4 invariantes: (1) no-vaciedad lista [ASTValidator], (2) IDs únicos
    [ASTValidator], (3) balanceo LaTeX [ASTValidator], (4) no-vaciedad de
    contenido excluyendo IMAGE [propia].
    """

    @staticmethod
    def validate(document_id: str, nodes: Tuple[ASTNode, ...]) -> None:
        try:
            ASTValidator.validate(list(nodes))
        except ASTValidationError as e:
            raise OracleValidityError(
                f"Oracle '{document_id}' failed structural validity: {e}"
            ) from e

        # Invariante 4: no-vaciedad de contenido. Excluye IMAGE (no portan
        # texto, coherente con ASTHealthReport.from_ast). Si no hay nodos
        # no-IMAGE (oráculo de solo imágenes), el oráculo pasa.
        non_image_nodes = [n for n in nodes if n.node_type != ContentNodeType.IMAGE]
        if non_image_nodes and not any(n.text_content for n in non_image_nodes):
            raise OracleValidityError(
                f"Oracle '{document_id}' failed content non-emptiness: "
                f"all non-image nodes have empty content."
            )