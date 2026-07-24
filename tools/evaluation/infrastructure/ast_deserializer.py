from typing import Any

from core.ast.models import ASTNode


class ASTJsonDeserializer:
    """Deserializador de infraestructura para reconstruir nodos AST a partir de JSON."""

    @staticmethod
    def deserialize_nodes(raw_data: Any) -> tuple[ASTNode, ...]:
        if isinstance(raw_data, dict):
            raw_nodes = raw_data.get("nodes", [])
        elif isinstance(raw_data, list):
            raw_nodes = raw_data
        else:
            raw_nodes = []

        nodes: list[ASTNode] = []
        for item in raw_nodes:
            if isinstance(item, dict):
                clean_kwargs = {k: v for k, v in item.items() if isinstance(k, str)}
                nodes.append(ASTNode(**clean_kwargs))

        return tuple(nodes)