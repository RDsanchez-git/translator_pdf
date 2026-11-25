from base64 import b64decode
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


def _read_verified_harmony_ranks(cache_dir: Path) -> tuple[Path, bytes]:
    """Read bounded bytes once, then validate the very bytes to be consumed."""
    path = cache_dir / sha1(HARMONY_RANKS_URL.encode("utf-8")).hexdigest()
    if cache_dir.is_symlink() or not cache_dir.is_dir() or path.is_symlink() or not path.is_file():
        raise ValueError("PPPR_G5_HARMONY_CACHE_MISSING")
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("PPPR_G5_HARMONY_CACHE_SIZE_INVALID")
    with path.open("rb") as source:
        data = source.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("PPPR_G5_HARMONY_CACHE_SIZE_INVALID")
    if sha256(data).hexdigest() != HARMONY_RANKS_SHA256:
        raise ValueError("PPPR_G5_HARMONY_CACHE_IDENTITY_DRIFT")
    return path, data


def verify_harmony_rank_cache(cache_dir: Path) -> Path:
    """Preflight only. Never invoke tiktoken's implicit download on a miss."""
    path, _ = _read_verified_harmony_ranks(cache_dir)
    return path


# Ordinary-text split pattern from tiktoken 0.14.0, o200k_base() (also
# used by o200k_harmony()). See upstream notice below. Preserve the exact
# pattern, not a hand-tuned approximation.
# https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py
# MIT License
# Copyright (c) 2022 OpenAI, Shantanu Jain
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
_HARMONY_ORDINARY_PATTERN = "|".join((
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
    r"""\p{N}{1,3}""",
    r""" ?[^\s\p{L}\p{N}]+[\r\n/]*""",
    r"""\s*[\r\n]+""",
    r"""\s+(?!\S)""",
    r"""\s+""",
))


class VerifiedHarmonyEstimator(ExactBPEEstimator):
    """Harmony ordinary-text BPE from explicitly verified local bytes.

    Reuse tiktoken's public Encoding and the existing estimator contract.
    No registry/cache loader, implicit acquisition, global monkeypatch or
    environment mutation. Literal special-token spellings remain ordinary
    text, as in ExactBPEEstimator's disallowed_special=() behavior.

    This measures the supplied string; it does NOT render Groq's server-side
    chat framing or establish a conservative provider token ceiling.
    """

    def __init__(self, cache_dir: Path):
        _, data = _read_verified_harmony_ranks(cache_dir)
        ranks: dict[bytes, int] = {}
        try:
            for line in data.splitlines():
                if not line:
                    continue
                encoded, rank = line.split()
                token = b64decode(encoded, validate=True)
                if not token or token in ranks or int(rank) != len(ranks):
                    raise ValueError("invalid rank sequence")
                ranks[token] = int(rank)
            # Every byte must have a rank so arbitrary UTF-8 text is encodable.
            if any(bytes([i]) not in ranks for i in range(256)):
                raise ValueError("incomplete byte vocabulary")
        except ValueError as exc:
            raise ValueError("PPPR_G5_HARMONY_RANK_FORMAT_INVALID") from exc
        self._encoding = tiktoken.Encoding(
            name="o200k_harmony_ordinary_verified",
            pat_str=_HARMONY_ORDINARY_PATTERN,
            mergeable_ranks=ranks,
            special_tokens={},
        )
