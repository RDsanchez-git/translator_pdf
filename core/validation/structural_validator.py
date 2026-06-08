# core/validation/structural_validator.py
import re
from typing import List
from core.execution.models import ValidationError

class StructuralValidator:
    """
    Guardián de invariantes estructurales sintácticos locales y globales.
    Mantiene compatibilidad estricta con la interfaz pública legacy.
    """

    @classmethod
    def validate(cls, text: str) -> List[ValidationError]:
        errors = []
        
        # HTML Residual (Mantenido por compatibilidad legacy)
        if cls._has_residual_html(text):
            errors.append(ValidationError(
                code="RESIDUAL_HTML",
                message="Tags HTML detectados fuera de entornos seguros."
            ))
            
        # SI-01: Control atómico de delimitadores ({}, [])
        brace_err = cls._check_braces(text)
        if brace_err: 
            errors.append(brace_err)
            
        bracket_err = cls._check_brackets(text)
        if bracket_err: 
            errors.append(bracket_err)
            
        # SI-02: Control de delimitadores matemáticos (Heurístico)
        math_err = cls._check_math_delimiters(text)
        if math_err: 
            errors.append(math_err)
            
        # SI-03: Integridad topográfica de entornos LaTeX
        env_err = cls._check_environments(text)
        if env_err: 
            errors.append(env_err)
            
        return errors

    @staticmethod
    def _has_residual_html(text: str) -> bool:
        temp = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
        temp = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', '', temp, flags=re.DOTALL)
        return bool(re.search(r'</?[a-zA-Z][a-zA-Z0-9]*\b[^>]*>', temp))

    # ========== SI-01: Braces ({}) ==========
    @staticmethod
    def _check_braces(text: str) -> ValidationError | None:
        clean = re.sub(r'\\(\{|\})', '', text)
        stack = 0
        for ch in clean:
            if ch == '{': 
                stack += 1
            elif ch == '}': 
                stack -= 1
            
            if stack < 0:
                return ValidationError("UNBALANCED_BRACES_EARLY", "Cierre prematuro de llaves '}'.")
        
        if stack > 0:
            return ValidationError("UNBALANCED_BRACES_OPEN", f"Llaves abiertas sin cerrar (residual: {stack}).")
        return None

    # ========== SI-01: Brackets ([]) ==========
    @staticmethod
    def _check_brackets(text: str) -> ValidationError | None:
        clean = re.sub(r'\\\[|\\\]', '', text)
        stack = 0
        for ch in clean:
            if ch == '[': 
                stack += 1
            elif ch == ']': 
                stack -= 1
            
            if stack < 0:
                return ValidationError("UNBALANCED_BRACKETS_EARLY", "Cierre prematuro de corchetes ']'.")
        
        if stack > 0:
            return ValidationError("UNBALANCED_BRACKETS_OPEN", f"Corchetes abiertos sin cerrar (residual: {stack}).")
        return None

    # ========== SI-02: Math Delimiters (Heurístico) ==========
    @staticmethod
    def _check_math_delimiters(text: str) -> ValidationError | None:
        """
        Validación heurística.
        NO garantiza corrección sintáctica completa de LaTeX matemático.
        Solo detecta desbalances evidentes.
        """
        # 1. Validamos desbalance directo de bloques display math ($$)
        display_count = text.count('$$')
        if display_count % 2 != 0:
            return ValidationError("UNBALANCED_DISPLAY_MATH", f"Paridad impar de bloques '$$' ({display_count}).")
            
        # 2. Purgamos los bloques display y los dólares legítimamente escapados (\$)
        temp = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
        temp = re.sub(r'\\\$', '', temp)
        
        # 3. Conteo plano sobre el residuo para matemática inline
        inline_count = temp.count('$')
        if inline_count % 2 != 0:
            return ValidationError("UNBALANCED_INLINE_MATH", f"Paridad impar de matemática inline '$' ({inline_count}).")
            
        return None

    # ========== SI-03: Environments ==========
    @staticmethod
    def _check_environments(text: str) -> ValidationError | None:
        # Se revierte a la expresión regular original estable sin espacios opcionales
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