import re
from typing import Dict, List
from collections import defaultdict
from bs4 import BeautifulSoup, Comment
from bs4.formatter import HTMLFormatter  # INYECCIÓN SOTA
from core.normalization.base import BaseNormalizer, NormalizerResult, WarningEntry  # TIPADO ESTRUCTURADO

class ParagraphNormalizer(BaseNormalizer):
    """
    Normalizador defensivo para bloques de texto destinados a inferencia (TRANSLATE).
    
    LOSSY NORMALIZATION NOTE: Este componente desmantela intencionalmente envolturas de bloque
    y estructurales (span, div, p) priorizando la continuidad lineal del texto plano.
    Aplatana etiquetas inline anidadas mediante .get_text() para blindar a Tectonic.
    """

    def __init__(self, normalizer_version: str = "1.3.2"):
        self._version = normalizer_version
        self._heading_spacing_regex = re.compile(r'^(#{1,6})([^#\s])', re.MULTILINE)
        self._list_spacing_regex = re.compile(r'^([ \t]*[-*+])([^\s\-*+])', re.MULTILINE)
        self._numbered_list_regex = re.compile(r'^(\s*\d+\.)(?=[A-Z][a-z]+)', re.MULTILINE)
        
        self._leaked_math_regex = re.compile(r'(\\begin\{equation\}|\$\$|\\\[|\\\(|\\\)|\\\]|\\end\{equation\})')
        self._leaked_table_regex = re.compile(r'(\|\s*---|---\s*\||\\begin\{tabular\}|\\begin\{table\}|\\begin\{array\})')

    @property
    def normalizer_id(self) -> str:
        return "paragraph_normalizer"

    @property
    def normalizer_version(self) -> str:
        return self._version

    def _check_domain_anomalies(self, text: str, warnings: List[WarningEntry]) -> None:
        if self._leaked_math_regex.search(text):
            warnings.append(WarningEntry(
                severity="WARNING", 
                message="MISCLASSIFIED_NODE_LEAK: Math environment token detected inside text node."
            ))
        if self._leaked_table_regex.search(text):
            warnings.append(WarningEntry(
                severity="WARNING", 
                message="MISCLASSIFIED_NODE_LEAK: Table environment/pipe structure detected inside text node."
            ))

    def _normalize_html_dom(self, text: str, fixes_map: Dict[str, int]) -> str:
        if "<" not in text:
            return text

        # SOTA: Uso de html.parser para evitar la auto-generación de estructuras de control de lxml
        soup = BeautifulSoup(text, "html.parser")

        # Corrección de Advertencia: Transición de 'text' a 'string'
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
            fixes_map["html_comment_removed"] += 1

        for tag in soup.find_all("sup"):
            raw_text = tag.get_text().strip()
            if raw_text.startswith("^{") and raw_text.endswith("}"):
                tag.replace_with(raw_text)
            else:
                tag.replace_with(f"^{{{raw_text}}}")
                fixes_map["tag_sup_converted_to_latex"] += 1

        for tag in soup.find_all("sub"):
            raw_text = tag.get_text().strip()
            if raw_text.startswith("_{") and raw_text.endswith("}"):
                tag.replace_with(raw_text)
            else:
                tag.replace_with(f"_{{{raw_text}}}")
                fixes_map["tag_sub_converted_to_latex"] += 1

        for tag in soup.find_all(["b", "strong"]):
            raw_text = tag.get_text().strip()
            clean_text = re.sub(r'^\*\*|\*\*$', '', raw_text)
            if clean_text:
                tag.replace_with(f"**{clean_text}**")
                fixes_map["tag_bold_converted_to_markdown"] += 1

        for tag in soup.find_all(["i", "em"]):
            raw_text = tag.get_text().strip()
            clean_text = re.sub(r'^\*|\*$', '', raw_text)
            if clean_text:
                tag.replace_with(f"*{clean_text}*")
                fixes_map["tag_italic_converted_to_markdown"] += 1

        for tag in soup.find_all("br"):
            tag.replace_with("\n")
            fixes_map["tag_br_converted_to_newline"] += 1

        for tag in soup.find_all(["p", "div"]):
            tag.insert_before("\n")
            tag.insert_after("\n")
            tag.unwrap()
            fixes_map["block_wrapper_unwrapped_safely"] += 1

        for tag in soup.find_all("span"):
            tag.unwrap()
            fixes_map["inline_wrapper_unwrapped"] += 1

        for tag in soup.find_all(["script", "iframe", "style", "object", "embed"]):
            tag.decompose()
            fixes_map["malicious_tag_decomposed"] += 1

        # Configuración del formateador para evitar que se escapen caracteres markdown como > o *
        raw_formatter = HTMLFormatter(entity_substitution=None)
        return soup.decode_contents(formatter=raw_formatter).strip()

    def _normalize_markdown_syntax(self, text: str, fixes_map: Dict[str, int]) -> str:
        mutated_text = text

        if self._heading_spacing_regex.search(mutated_text):
            mutated_text = self._heading_spacing_regex.sub(r'\1 \2', mutated_text)
            fixes_map["markdown_heading_spacing_fixed"] += 1

        if self._list_spacing_regex.search(mutated_text):
            mutated_text = self._list_spacing_regex.sub(r'\1 \2', mutated_text)
            fixes_map["markdown_list_spacing_fixed"] += 1

        if self._numbered_list_regex.search(mutated_text):
            mutated_text = self._numbered_list_regex.sub(r'\1 ', mutated_text)
            fixes_map["markdown_numbered_list_spacing_fixed"] += 1

        return mutated_text

    def normalize(self, text: str) -> NormalizerResult:
        if not text.strip():
            return NormalizerResult(text=text)

        fixes_map: Dict[str, int] = defaultdict(int)
        local_warnings: List[WarningEntry] = []  # CORRECCIÓN: Tipado de DTO SOTA
        
        self._check_domain_anomalies(text, local_warnings)
        
        runtime_text = self._normalize_html_dom(text, fixes_map)
        runtime_text = self._normalize_markdown_syntax(runtime_text, fixes_map)

        # Limpieza de saltos de línea redundantes generados por la apertura de bloques
        runtime_text = re.sub(r'\n{3,}', '\n\n', runtime_text).strip()

        aggregated_fixes = [f"{key}:{value}" for key, value in fixes_map.items() if value > 0]

        return NormalizerResult(
            text=runtime_text,
            fixes=aggregated_fixes,
            warnings=local_warnings
        )