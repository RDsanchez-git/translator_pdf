import re
import html
import unicodedata
from typing import Callable, List

class TextNormalizer:
    """SOTA: Transformaciones deterministas seguras. No evalúa, solo limpia."""
    
    @staticmethod
    def _decode_html(text: str) -> str:
        return html.unescape(text)
        
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        return unicodedata.normalize("NFKC", text)
        
    @staticmethod
    def _strip_control_chars(text: str) -> str:
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Arquitectura Pipeline-based
    PIPELINE: List[Callable[[str], str]] = [
        _decode_html,
        _normalize_unicode,
        _strip_control_chars
    ]

    @classmethod
    def normalize(cls, text: str) -> str:
        result = text
        for step in cls.PIPELINE:
            result = step(result)
        return result