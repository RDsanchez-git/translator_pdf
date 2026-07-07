from typing import Iterable, List
from core.ast.models import ASTNode

class ASTSequenceNormalizer:
    """
    SOTA: Reparador topológico O(n).
    Tras la expansión de fragmentos (1 a N), los sequence_id originales pierden contigüidad.
    Este componente reasigna la secuencia matemática garantizando un documento lineal sin huecos.
    """
    
    @staticmethod
    def normalize(nodes: Iterable[ASTNode]) -> List[ASTNode]:
        """Aplica una nueva numeración indexada en base 1."""
        return [
            node.with_sequence_id(idx + 1)
            for idx, node in enumerate(nodes)
        ]