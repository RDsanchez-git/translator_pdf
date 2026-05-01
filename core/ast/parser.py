from core.ast.models import ASTNode

def load_mock_ast():
    return [
        ASTNode(
            node_id="sec_1", 
            type="section", 
            content="Introduction to the Model"
        ),
        ASTNode(
            node_id="txt_1", 
            type="text_block", 
            # Caso hostil: Porcentaje crudo y guiones bajos (forzará sanitización)
            content="The model achieves 99% accuracy and uses variable_name."
        ),
        ASTNode(
            node_id="eq_1", 
            type="display_equation", 
            # Caso hostil: Bypass puro, no debe ser tocado por el LLM ni mutado
            latex="\\hat{y} = \\sum_{i=1}^{n} \\alpha_i x_i + \\epsilon"
        ),
        ASTNode(
            node_id="txt_2", 
            type="text_block", 
            # Caso hostil: Llave desbalanceada (forzará _is_latex_structurally_suspicious y Fallback)
            content="This block contains an unclosed brace { which normally crashes Tectonic."
        ),
        ASTNode(
            node_id="txt_3", 
            type="text_block", 
            # Caso hostil: Ecuación inline (forzará validación de $ par)
            content="Here we define the parameter $x_i$ for the objective function."
        ),
        ASTNode(
            node_id="txt_4", 
            type="text_block", 
            # Caso hostil: Barra invertida literal (forzará _safe_fallback si el anterior falla)
            content="The path is C:\\Users\\Admin\\Data."
        )
    ]