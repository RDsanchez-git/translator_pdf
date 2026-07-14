import tiktoken
from core.validation.protocols import TokenEstimatorProtocol

class ExactBPEEstimator(TokenEstimatorProtocol):
    """SOTA: Tokenización determinista para evadir HTTP 400."""
    def __init__(self, encoding_name: str = "cl100k_base"):
        self._encoding = tiktoken.get_encoding(encoding_name)
        
    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self._encoding.encode(text, disallowed_special=()))