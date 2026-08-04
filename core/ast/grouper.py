from dataclasses import dataclass
from typing import List, Sequence
from core.ast.models import ASTNode

@dataclass
class SemanticGroup:
    structural_path: tuple
    context_id: str
    nodes: List[ASTNode]

class ContextAwareSemanticGrouper:
    @staticmethod
    def group(ast: Sequence[ASTNode]) -> List[SemanticGroup]:
        if not ast:
            return []
            
        groups: List[SemanticGroup] = []
        
        first_node_cp = ast[0].control_plane
        current_path = tuple(first_node_cp.get("structural_path", ()))
        current_ctx = first_node_cp.get("context_id", "GLOBAL_ROOT")
        current_nodes = []
        
        for node in ast:
            node_path = tuple(node.control_plane.get("structural_path", ()))
            
            if node_path != current_path:
                groups.append(SemanticGroup(
                    structural_path=current_path, 
                    context_id=current_ctx, 
                    nodes=current_nodes
                ))
                current_path = node_path
                current_ctx = node.control_plane.get("context_id", "GLOBAL_ROOT")
                current_nodes = [node]
            else:
                current_nodes.append(node)
                
        if current_nodes:
            groups.append(SemanticGroup(
                structural_path=current_path, 
                context_id=current_ctx, 
                nodes=current_nodes
            ))
            
        return groups