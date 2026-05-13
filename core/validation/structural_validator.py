import re
from typing import List
from core.execution.models import ValidationError

class StructuralValidator:
    """SOTA: Guardián de invariantes con tolerancia a escapes."""
    
    @classmethod
    def validate(cls, text: str) -> List[ValidationError]:
        errors = []
        
        if cls._has_residual_html(text):
            errors.append(ValidationError(
                code="RESIDUAL_HTML",
                message="Tags HTML detectados fuera de entornos seguros."
            ))
            
        brace_err = cls._check_braces(text)
        if brace_err: 
            errors.append(brace_err)
            
        env_err = cls._check_environments(text)
        if env_err: 
            errors.append(env_err)
            
        return errors

    @staticmethod
    def _has_residual_html(text: str) -> bool:
        # SOTA: Excluir zonas matemáticas antes de buscar HTML (evita falsos positivos en "a < b")
        temp = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
        temp = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', '', temp, flags=re.DOTALL)
        return bool(re.search(r'</?[a-zA-Z][a-zA-Z0-9]*\b[^>]*>', temp))

    @staticmethod
    def _check_braces(text: str) -> ValidationError | None:
        # SOTA: Purgar llaves escapadas explícitamente para no corromper la pila
        clean_text = re.sub(r'\\(\{|\})', '', text)
        stack = 0
        for char in clean_text:
            if char == '{':
                stack += 1
            elif char == '}':
                stack -= 1
            if stack < 0: 
                return ValidationError("UNBALANCED_BRACES_EARLY", "Cierre prematuro de llaves '}'.")
        return None

    @staticmethod
    def _check_environments(text: str) -> ValidationError | None:
        stack = []
        for match in re.finditer(r'\\(begin|end)\{([^}]+)\}', text):
            cmd, env = match.groups()
            if cmd == 'begin':
                stack.append(env)
            elif cmd == 'end':
                if not stack or stack[-1] != env:
                    return ValidationError(
                        "ENV_MISMATCH", f"Entorno desbalanceado: \\end{{{env}}} sin \\begin."
                    )
                stack.pop()
        if stack:
            return ValidationError("ENV_UNCLOSED", f"Entorno abierto sin cerrar: \\begin{{{stack[-1]}}}.")
        return None