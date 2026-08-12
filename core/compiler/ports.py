# core/compiler/ports.py
"""
Puertos del Bounded Context de Compilación.

NADR-06 §5.3: Contratos públicos del dominio de compilación.
Ubicación explícita para evitar import circulares.
"""
from typing import Protocol, List
from core.ast.models import ASTNode


class ASTProviderProtocol(Protocol):
    """
    Puerto para obtener el AST canónico de un documento.

    Implementado por ASTRegistry. Consumido exclusivamente por
    CQRSAssemblyContextResolver (NO por CompilationService).
    """
    def get_document_ast(self, document_id: str, ast_hash: str) -> List[ASTNode]: ...