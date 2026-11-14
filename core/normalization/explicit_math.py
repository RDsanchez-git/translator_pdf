"""B02.4: deterministic boundaries for *explicit source LaTeX*, not OCR math recognition.

No inference, no normalization, no guesswork.  A balanced source region is
preserved byte-for-byte in Unicode.  Unknown/unbalanced delimiters fail closed
before a provider can translate a partial formula.  This does NOT protect
formulas which PyMuPDF mis-extracted or failed to type as equations.
"""

from __future__ import annotations

import re

# Common LaTeX math environments only; prose environments remain prose.
_MATH_BEGIN = re.compile(
    r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|math|displaymath)\}"
)
_MATH_END = re.compile(
    r"\\end\{(equation\*?|align\*?|gather\*?|multline\*?|math|displaymath)\}"
)


def find_explicit_math_spans(text: str) -> list[tuple[int, int]]:
    """Return non-overlapping [start,end) of balanced LaTeX math in source order.

    Delimiters: $...$, $$...$$, \\(...\\), \\[...\\], and whitelisted math
    environments. Backslash escapes (including \\$) are respected.  A literal
    currency "$10" can be ambiguous; rather than guessing, unmatched dollar
    delimiters reject.  No implicit conversion of Unicode glyphs to LaTeX.
    """
    spans: list[tuple[int, int]] = []
    i, n = 0, len(text)
    while i < n:
        opener = closer = ""
        if text.startswith(r"\(", i):
            opener, closer = r"\(", r"\)"
        elif text.startswith(r"\[", i):
            opener, closer = r"\[", r"\]"
        elif text.startswith(r"\)", i) or text.startswith(r"\]", i):
            raise ValueError(f"B024_ORPHAN_MATH_CLOSER: offset={i}")
        elif text.startswith(r"\begin{", i):
            match = _MATH_BEGIN.match(text, i)
            if match:
                opener, closer = match.group(0), rf"\end{{{match.group(1)}}}"
        elif text.startswith(r"\end{", i):
            if _MATH_END.match(text, i):
                raise ValueError(f"B024_ORPHAN_MATH_CLOSER: offset={i}")
        elif text[i] == "$":
            opener = "$$" if text.startswith("$$", i) else "$"
            closer = opener
        elif text[i] == "\\":
            # All other backslash escapes are prose data, not math openers.
            i += 2
            continue

        if not opener:
            i += 1
            continue

        start, cursor = i, i + len(opener)
        while cursor < n:
            if text.startswith(closer, cursor):
                if not text[i + len(opener):cursor].strip():
                    raise ValueError(f"B024_EMPTY_MATH: offset={start}")
                end = cursor + len(closer)
                if (opener.startswith("$") and spans
                        and spans[-1][1] == start
                        and text[spans[-1][0]] == "$"):
                    raise ValueError(f"B024_ADJACENT_DOLLAR_MATH: offset={start}")
                spans.append((start, end))
                i = end
                break
            # All TeX escapes consume exactly the following character except
            # a matching close token, which was checked immediately above.
            if text[cursor] == "\\":
                cursor += 2
                continue
            if opener == "$" and text.startswith("$$", cursor):
                raise ValueError(f"B024_MIXED_DOLLAR_DELIMITERS: offset={cursor}")
            cursor += 1
        else:
            raise ValueError(f"B024_UNCLOSED_MATH: offset={start} opener={opener}")
    return spans
