import re
import uuid
from typing import Dict, List, Tuple
from collections import defaultdict
from bs4 import BeautifulSoup
from bs4.element import NavigableString 
from bs4.formatter import HTMLFormatter
from core.normalization.base import BaseNormalizer, NormalizerResult, WarningEntry

# =====================================================================
# COMPONENTES ATÓMICOS FUNCIONALES (Stateless & Thread-Safe)
# =====================================================================

class ProtectedRegionMasker:
    """Lexer de enmascaramiento libre de estado. Extrae regiones literales."""

    @staticmethod
    def _scan_inline_verbatim(text: str, vault: Dict[str, str]) -> str:
        """SOTA: Lexer real con ramas separadas para verb, lstinline y mintinline."""
        # Patrón base: captura los comandos, sin \b para no fallar con delimitadores
        cmd_pattern = re.compile(r'\\(?:verb\*?|Verb\*?|lstinline|mintinline)')
        result = []
        i = 0
        n = len(text)

        while i < n:
            match = cmd_pattern.match(text, i)
            if match:
                cmd_text = match.group(0)
                start_idx = match.start()
                curr = match.end()

                # ---------- Rama para mintinline ----------
                if 'mintinline' in cmd_text:
                    # Consumir espacios
                    while curr < n and text[curr] in ' \t':
                        curr += 1
                    # Consumir opciones entre corchetes (opcional)
                    if curr < n and text[curr] == '[':
                        curr += 1
                        while curr < n and text[curr] != ']':
                            curr += 1
                        if curr < n:
                            curr += 1
                    # Consumir espacios después de opciones
                    while curr < n and text[curr] in ' \t':
                        curr += 1
                    # Consumir argumento obligatorio: {lenguaje}
                    if curr < n and text[curr] == '{':
                        braces = 1
                        curr += 1
                        while curr < n and braces > 0:
                            if text[curr] == '\\':
                                curr = min(curr + 2, n)
                            elif text[curr] == '{':
                                braces += 1
                                curr += 1  # CORRECCIÓN: Faltaba avanzar el puntero
                            elif text[curr] == '}':
                                braces -= 1
                                curr += 1  # CORRECCIÓN: Faltaba avanzar el puntero
                            else:
                                curr += 1
                    # Consumir espacios antes del delimitador de código
                    while curr < n and text[curr] in ' \t':
                        curr += 1

                # ---------- Rama para lstinline ----------
                elif 'lstinline' in cmd_text:
                    # Consumir espacios antes del delimitador
                    while curr < n and text[curr] in ' \t':
                        curr += 1

                # ---------- Rama para verb (incluye verb* y Verb*) ----------
                else:   # 'verb' in cmd_text
                    # verb no tiene argumentos previos, solo espacios opcionales
                    while curr < n and text[curr] in ' \t':
                        curr += 1

                # --- Delimitador y contenido (común a todas las ramas) ---
                if curr < n:
                    delim = text[curr]
                    curr += 1
                    if delim == '{':
                        braces = 1
                        while curr < n and braces > 0:
                            if text[curr] == '\\':
                                curr = min(curr + 2, n)
                            elif text[curr] == '{':
                                braces += 1
                                curr += 1  # CORRECCIÓN: Faltaba avanzar el puntero
                            elif text[curr] == '}':
                                braces -= 1
                                curr += 1  # CORRECCIÓN: Faltaba avanzar el puntero
                            else:
                                curr += 1
                        end_idx = curr
                    else:
                        # Delimitador arbitrario (|, +, !, etc.)
                        while curr < n and text[curr] != delim:
                            if text[curr] == '\\':
                                curr = min(curr + 2, n)
                            else:
                                curr += 1
                        if curr < n:
                            curr += 1  # incluir delimitador de cierre
                        end_idx = curr

                    block = text[start_idx:end_idx]
                    marker = f"⟪DNL_PROTECTED_{uuid.uuid4().hex[:8]}⟫"
                    vault[marker] = block
                    result.append(marker)
                    i = end_idx
                    continue

            result.append(text[i])
            i += 1

        return "".join(result)

    @staticmethod
    def mask(text: str) -> Tuple[str, Dict[str, str]]:
        vault: Dict[str, str] = {}
        masked_text = ProtectedRegionMasker._scan_inline_verbatim(text, vault)

        def replacer(match) -> str:
            placeholder = f"⟪DNL_PROTECTED_{uuid.uuid4().hex[:8]}⟫"
            vault[placeholder] = match.group(0)
            return placeholder

        # Soporta entornos protegidos con posibles parámetros (ej. {minted}{python})
        env_pattern = re.compile(
            r'\\begin\{(verbatim\*?|Verbatim|lstlisting|minted\*?|comment|filecontents\*?|tcblisting|pycode|luacode\*?)\}'
            r'(?:\[[^\]]*\])*(?:\{[^{}]*\})*'
            r'(.*?)\\end\{\1\}',
            re.DOTALL
        )
        masked_text = env_pattern.sub(replacer, masked_text)

        return masked_text, vault


class ProtectedRegionRestorer:
    """Reinyecta los bloques literales al final del pipeline."""

    @staticmethod
    def restore(text: str, vault: Dict[str, str]) -> str:
        restored_text = text
        # SOTA: Bucle de evaluación continua. Resuelve el anidamiento de marcadores
        # destapando los contenedores externos y procesando los internos en pasadas sucesivas.
        while any(marker in restored_text for marker in vault):
            for marker, original_content in vault.items():
                restored_text = restored_text.replace(marker, original_content)
        return restored_text


class MathDelimiterValidator:
    """Autómata de estados finitos puro. Sin regex auxiliares que generen falsos positivos."""

    @staticmethod
    def validate(text: str, warnings: List[WarningEntry]) -> None:
        state = 0  # 0: NORMAL, 1: INLINE ($), 2: DISPLAY ($$)
        i = 0
        n = len(text)

        while i < n:
            # Manejo de escapes: saltar \\ o \$ correctamente
            if text[i] == '\\':
                i = min(i + 2, n)
                continue

            if i + 1 < n and text[i] == '$' and text[i+1] == '$':
                if state == 0:
                    state = 2
                elif state == 2:
                    state = 0
                else:
                    warnings.append(WarningEntry("SEVERE", "Collision: $$ encountered inside INLINE math ($)."))
                    state = 2
                i += 2
                continue

            if text[i] == '$':
                if state == 0:
                    state = 1
                elif state == 1:
                    state = 0
                else:
                    warnings.append(WarningEntry("SEVERE", "Collision: $ encountered inside DISPLAY math ($$)."))
                i += 1
                continue

            i += 1

        if state != 0:
            warnings.append(WarningEntry("SEVERE", "Unbalanced mathematical delimiters at EOF."))


class MathEnvironmentValidator:
    """Validador topológico por Pila LIFO."""

    SUPPORTED = {
        "equation", "equation*", "align", "align*", "gather", "gather*",
        "multline", "multline*", "cases", "cases*", "matrix", "pmatrix",
        "bmatrix", "Bmatrix", "vmatrix", "Vmatrix", "array", "aligned",
        "split", "subequations", "smallmatrix", "alignedat", "alignedat*",
        "flalign", "flalign*", "xalignat", "xalignat*", "xxalignat", "CD", "tikzcd"
    }
    NON_NESTABLE = {"equation", "equation*", "align", "align*", "gather", "gather*", "flalign", "flalign*"}

    @classmethod
    def validate(cls, text: str, warnings: List[WarningEntry], metrics: Dict[str, int]) -> None:
        stack: List[str] = []

        # SOTA: Extrae EXCLUSIVAMENTE la firma de apertura/cierre ignorando parámetros opcionales.
        # NUNCA debe consumir el contenido interno, o destruirá el escáner LIFO paso a paso.
        env_token = re.compile(
            r'\\(begin|end)\{([a-zA-Z\*]+)\}'
            r'(?:\[[^\]]*\])*'          # consume opciones silenciosamente
            r'(?:\{[^{}]*\})*'          # consume argumentos silenciosamente
        )

        for match in env_token.finditer(text):
            action, env = match.groups()
            if action == "begin":
                if env in cls.SUPPORTED:
                    metrics[f"env_{env}"] += 1
                else:
                    warnings.append(WarningEntry("INFO", f"UNSUPPORTED_ENV: '{env}'"))

                if stack and env == stack[-1] and env in cls.NON_NESTABLE:
                    warnings.append(WarningEntry("SEVERE", f"ILLEGAL_NESTING: recursive '{env}'"))

                stack.append(env)
            else:  # end
                if not stack:
                    warnings.append(WarningEntry("SEVERE", f"LATEX_TOPOLOGY: Orphaned \\end{{{env}}}"))
                    continue

                expected = stack.pop()
                if expected != env:
                    warnings.append(WarningEntry("SEVERE", f"LATEX_TOPOLOGY: Mismatch. Expected \\end{{{expected}}} but got \\end{{{env}}}"))

        if stack:
            warnings.append(WarningEntry("SEVERE", f"LATEX_TOPOLOGY: Unclosed environments: {', '.join(stack)}"))


class MathHtmlPurifier:
    """SOTA: Purificador que preserva la semántica de sub/sup e inecuaciones algebraicas."""

    _fast_signature = re.compile(r'</?(?:span|div|p|b|strong|i|em|sup|sub)\b[^>]*>', re.IGNORECASE)

    @classmethod
    def purify(cls, text: str, metrics: Dict[str, int]) -> str:
        if not cls._fast_signature.search(text):
            return text

        soup = BeautifulSoup(text, "html.parser")

        for tag in soup.find_all(["sup", "sub"]):
            if tag.parent is None:
                continue

            raw = tag.get_text().strip()
            marker = "^" if tag.name == "sup" else "_"

            if raw.startswith(f"{marker}{{") and raw.endswith("}"):
                tag.replace_with(raw)
                metrics[f"html_{tag.name}_unwrapped"] += 1
                continue

            prev = tag.previous_element
            if isinstance(prev, NavigableString) and (str(prev).endswith(marker) or str(prev).endswith(f"{marker}{{")):
                tag.replace_with(raw)
                metrics[f"html_{tag.name}_unwrapped"] += 1
            else:
                tag.replace_with(f"{marker}{{{raw}}}")
                metrics[f"html_{tag.name}_converted"] += 1

        for tag in soup.find_all(["span", "div", "p", "b", "strong", "i", "em"]):
            if tag.parent is None:
                continue
            tag.unwrap()
            metrics["html_safe_unwrap"] += 1

        # Configuración del formateador para congelar entidades tipográficas
        raw_formatter = HTMLFormatter(entity_substitution=None)
        return soup.decode_contents(formatter=raw_formatter).strip()


class DeprecatedDelimiterConverter:
    """Transpilación rápida a sintaxis Tectonic/Pandoc."""

    _inline = re.compile(r'\\\((.+?)\\\)', re.DOTALL)
    _display = re.compile(r'\\\[(.+?)\\\]', re.DOTALL)

    @classmethod
    def convert(cls, text: str, metrics: Dict[str, int]) -> str:
        new_text = cls._inline.sub(r'$\1$', text)
        if new_text != text:
            metrics["deprecated_inline_converted"] += 1

        newer_text = cls._display.sub(r'$$\1$$', new_text)
        if newer_text != new_text:
            metrics["deprecated_display_converted"] += 1

        return newer_text


# =====================================================================
# INTEGRACIÓN DEL FRAMEWORK (El Normalizador Registrable)
# =====================================================================

class MathDomainNormalizer(BaseNormalizer):
    """
    Patrón Facade: Conecta los módulos funcionales manteniendo compatibilidad estricta
    con el framework `NormalizationPolicy`, garantizando ejecución concurrente segura.
    """

    def __init__(self, normalizer_version: str = "3.1.0"):
        self._version = normalizer_version

    @property
    def normalizer_id(self) -> str:
        return "math_domain_normalizer"

    @property
    def normalizer_version(self) -> str:
        return self._version

    def normalize(self, text: str) -> NormalizerResult:
        if not text.strip():
            return NormalizerResult(text=text)

        metrics: Dict[str, int] = defaultdict(int)
        warnings: List[WarningEntry] = []

        masked_text, vault = ProtectedRegionMasker.mask(text)

        MathDelimiterValidator.validate(masked_text, warnings)
        MathEnvironmentValidator.validate(masked_text, warnings, metrics)

        processed = MathHtmlPurifier.purify(masked_text, metrics)
        processed = DeprecatedDelimiterConverter.convert(processed, metrics)

        final_text = ProtectedRegionRestorer.restore(processed, vault)

        aggregated_fixes = [f"{k}:{v}" for k, v in metrics.items() if v > 0]

        return NormalizerResult(
            text=final_text,
            fixes=aggregated_fixes,
            warnings=warnings,
            hard_fails=[]
        )