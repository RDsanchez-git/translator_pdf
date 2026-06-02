import sys
import os

# Asegurar que el contenedor reconozca la raíz del proyecto para los imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.normalization.latex_sanitizer import InlineMathProtector

def test_inline_math_protector():
    test_cases = [
        ("The value is $x$.", "The value is $x$."),
        ("Formula $x^2$ is used.", "Formula $x^2$ is used."),
        ("Subscripts like $x_{i,j}$ work.", "Subscripts like $x_{i,j}$ work."),
        ("Greek letters \\alpha and \\beta.", "Greek letters \\alpha and \\beta."),
        ("Cost is \\text{Price is \\$100} here.", "Cost is \\text{Price is \\$100} here."),
        ("Don't touch $$ block $$.", "Don't touch $$ block $$."),
        ("Equation $a\\$b$ is weird but valid.", "Equation $a\\$b$ is weird but valid.")
    ]

    for original, expected in test_cases:
        masked, mapping = InlineMathProtector.mask(original)
        
        # Simulación de alteración de espaciado del LLM para probar tolerancia
        mutated_masked = masked.replace("__MATH_0__", "__ MATH_0 __")
        restored = InlineMathProtector.restore(mutated_masked, mapping)
        
        assert expected == restored, f"Fallo en restitución.\nOriginal: {original}\nObtenido: {restored}"

    print("[OK] Test de invarianza matemática superado exitosamente.")

if __name__ == "__main__":
    test_inline_math_protector()