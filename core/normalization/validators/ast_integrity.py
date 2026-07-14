import re
from typing import List, Set
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.normalization.base import WarningEntry

class ASTIntegrityValidator:
    """
    Analizador topológico y sintáctico estricto pre-chunking.
    Asegura los invariantes de la estructura de datos del AST y detecta tokens malformados.
    """
    def __init__(self):
        self._version = "12.00.6"
        self._valid_asset_regex = re.compile(r'\[\[ASSET:(TABLE|FIGURE|IMAGE):[^\]]+\]\]')

    def validate_ast(self, nodes: List[ASTNode]) -> List[WarningEntry]:
        """
        Escanea el AST completo. 
        HARD_FAIL (SEVERE): Duplicados, malformaciones sintácticas estrictas.
        SOFT_FAIL (WARNING/INFO): Inconsistencias de layout tolerables en PDFs reales.
        """
        warnings: List[WarningEntry] = []
        
        if not nodes:
            warnings.append(WarningEntry(
                severity="WARNING",
                message="EMPTY_AST: The document contains zero extracted nodes. Legitimate for blank/scanned pages."
            ))
            return warnings

        seen_ids: Set[str] = set()
        total_nodes = len(nodes)

        for idx, node in enumerate(nodes):
            if not node.node_id:
                warnings.append(WarningEntry(
                    severity="SEVERE",
                    message=f"MISSING_NODE_ID: Node at index {idx} lacks a unique identifier."
                ))
            elif node.node_id in seen_ids:
                warnings.append(WarningEntry(
                    severity="SEVERE",
                    message=f"DUPLICATE_NODE_ID: Collision detected for node_id '{node.node_id}'."
                ))
            else:
                seen_ids.add(node.node_id)

            if node.text_content and "[[ASSET:" in node.text_content:
                asset_starts = node.text_content.count("[[ASSET:")
                valid_assets = len(self._valid_asset_regex.findall(node.text_content))
                
                if asset_starts > valid_assets:
                    warnings.append(WarningEntry(
                        severity="SEVERE",
                        message=f"MALFORMED_ASSET_PLACEHOLDER: Node {node.node_id} contains an unclosed or broken asset token."
                    ))

            if node.node_type == ContentNodeType.CAPTION:
                has_nearby_asset = False
                look_range = range(max(0, idx - 3), min(total_nodes, idx + 4))
                
                for l_idx in look_range:
                    if l_idx == idx:
                        continue
                    neighbor = nodes[l_idx]
                    
                    if neighbor.control_plane.get("preserve_original") is True:
                        has_nearby_asset = True
                        break
                    if neighbor.text_content and self._valid_asset_regex.search(neighbor.text_content):
                        has_nearby_asset = True
                        break

                if not has_nearby_asset:
                    warnings.append(WarningEntry(
                        severity="WARNING",
                        message=f"ORPHAN_CAPTION_LINT: Caption node {node.node_id} lacks a visual asset context within a 3-node window."
                    ))

        return warnings