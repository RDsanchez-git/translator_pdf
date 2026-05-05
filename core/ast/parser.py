from core.ast.models import ASTNode

def load_mock_ast_small() -> list[ASTNode]:
    """Test unitario: Inyección de casos hostiles para probar sanitización y fallback."""
    return [
        ASTNode(node_id="sec_1", type="section", content="Introduction to the Model"),
        ASTNode(node_id="txt_1", type="text_block", content="The model achieves 99% accuracy and uses variable_name."),
        ASTNode(node_id="eq_1", type="display_equation", latex="\\hat{y} = \\sum_{i=1}^{n} \\alpha_i x_i + \\epsilon"),
        ASTNode(node_id="txt_2", type="text_block", content="This block contains a balanced brace {like this} which is safe for Tectonic."),
        ASTNode(node_id="txt_3", type="text_block", content="Here we define the parameter $x_i$ for the objective function."),
        ASTNode(node_id="txt_4", type="text_block", content="The path is C:\\Users\\Admin\\Data.")
    ]

def load_mock_ast_large() -> list[ASTNode]:
    """Test de integración: Carga volumétrica para forzar Macro-Chunking y consistencia de LLM."""
    nodes = []
    # Generamos 3 secciones. Cada sección superará los 800 caracteres para forzar el corte semántico.
    for i in range(1, 4):
        nodes.append(ASTNode(
            node_id=f"sec_{i}", 
            type="section", 
            content=f"Section {i}: Econometric Model Analysis"
        ))
        nodes.append(ASTNode(
            node_id=f"txt_{i}_1", 
            type="text_block", 
            content=("This academic paper studies the econometric function $f(x)$ and its primary properties. " * 15)
        ))
        nodes.append(ASTNode(
            node_id=f"eq_{i}", 
            type="display_equation", 
            latex="\\hat{y} = \\sum_{i=1}^{n} \\alpha_i x_i + \\epsilon"
        ))
        nodes.append(ASTNode(
            node_id=f"txt_{i}_2", 
            type="text_block", 
            content=("We reuse the function $f(x)$ defined earlier to compute the final regression results. " * 15)
        ))
    return nodes

def load_mock_ast(mode: str = "large") -> list[ASTNode]:
    """Enrutador de pruebas."""
    if mode == "small":
        return load_mock_ast_small()
    return load_mock_ast_large()