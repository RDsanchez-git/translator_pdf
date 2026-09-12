"""Dominio de errores indexables (NADR-24 SS5.4 R18, ENGINEERING_PRINCIPLES SSIV).

Cero Fallos Silenciosos: todo error operacional porta un codigo indexable
[ej. SANITIZE-001] que identifica la causa raiz de forma trazable.
"""
from __future__ import annotations


class IndexedError(Exception):
    """Error con codigo indexable para trazabilidad operacional."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")
