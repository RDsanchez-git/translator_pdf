from hashlib import sha1, sha256
from pathlib import Path

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

# GPT-OSS uses Harmony with the o200k_base mergeable ranks. The upstream
# checksum is public; checking it does not acquire or initialize an encoding.
HARMONY_RANKS_URL = "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"
HARMONY_RANKS_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"


def verify_harmony_rank_cache(cache_dir: Path) -> Path:
    """Preflight only. Never invoke tiktoken's implicit download on a miss.

    A verified rank file is necessary, not sufficient for a provider-exact
    wire bound. Actual loading must be in a network-disabled preflight.
    """
    path = cache_dir / sha1(HARMONY_RANKS_URL.encode("utf-8")).hexdigest()
    if cache_dir.is_symlink() or not cache_dir.is_dir() or path.is_symlink() or not path.is_file():
        raise ValueError("PPPR_G5_HARMONY_CACHE_MISSING")
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("PPPR_G5_HARMONY_CACHE_SIZE_INVALID")
    if sha256(path.read_bytes()).hexdigest() != HARMONY_RANKS_SHA256:
        raise ValueError("PPPR_G5_HARMONY_CACHE_IDENTITY_DRIFT")
    return path
