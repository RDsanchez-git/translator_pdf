from core.ast.models import ASTNode

class TexBuilder:
    def build(self, nodes: list[ASTNode]) -> str:
        document = [
            "\\documentclass{article}",
            "\\begin{document}"
        ]

        for n in nodes:
            if not n.latex:
                continue
                
            if n.type == "section":
                document.append(f"\\section{{{n.latex}}}")
            elif n.type == "display_equation":
                document.append(f"\\begin{{equation}}\n{n.latex}\n\\end{{equation}}")
            elif n.type == "text_block":
                document.append(n.latex)

        document.append("\\end{document}")

        return "\n".join(document)