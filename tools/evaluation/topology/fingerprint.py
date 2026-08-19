from typing import Hashable

from core.ast.models import ASTNode


class ASTFingerprintPolicy:
    """
    Política de generación de huellas digitales (fingerprints) de nodos AST.

    Soporta estrategias semánticas (contenido + tipo) e identitarias (contenido + tipo + id).
    """

    @staticmethod
    def semantic_fingerprint(node: ASTNode) -> tuple[str, str]:
        """
        Devuelve la tupla semántica (node_type_str, text_content).
        Garantiza que la comparación considere tanto el tipo de nodo como su contenido.
        """
        node_type_str = node.node_type.value
        content_str = node.text_content.strip()
        return (node_type_str, content_str)

    @staticmethod
    def identity_fingerprint(node: ASTNode) -> Hashable:
        """
        Fingerprint estricto con identidad física de nodo (incluye ID explícito).

        ADVERTENCIA DE USO:
        Identity fingerprints únicamente deben utilizarse cuando ambos árboles compartan
        una identidad estable o previamente normalizada. Si los IDs de nodo son generados de
        forma no determinista entre ejecuciones (ej. UUIDs efímeros), esta estrategia
        producirá falsos negativos masivos.
        """
        node_id = getattr(node, "id", getattr(node, "node_id", None))
        if node_id is None:
            raise ValueError(
                "identity_fingerprint requiere un nodo con identidad estable."
            )

        node_type = getattr(node, "type", type(node).__name__)
        content = getattr(node, "content", getattr(node, "text", ""))
        return (str(node_type), str(content).strip(), str(node_id))