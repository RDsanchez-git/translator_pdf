"""Perfiles de ejecución de Continuous Verification (NADR-F17BIS-29).

NADR-F17BIS-29 §5.1 R1: Todo perfil de Continuous Verification MUST estar
explícitamente definido.

NADR-F17BIS-29 §5.3 R14: Continuous Verification MUST disponer de al menos
un perfil cuya cobertura represente la evaluación completa.

NADR-F17BIS-29 §5.3 R17: La definición de "completo" MUST derivarse de la
cobertura gobernada por el corpus, y MUST NOT definirse únicamente por
duración, cantidad de archivos o costo computacional.

NADR-F17BIS-29 §5.4 R18-R23: Perfil reducido / Smoke Verification.

Separación de bounded contexts:
- core/benchmark/verification/profiles.py → definición de perfiles (NADR-29)
- core/benchmark/corpus/models.py → CorpusManifest (NADR-26, consumido)
"""
from __future__ import annotations

from enum import Enum

from core.benchmark.corpus.models import CorpusManifest


class VerificationProfile(str, Enum):
    """Perfil de ejecución de Continuous Verification (NADR-29 §5.1 R1).

    Cada perfil define un alcance de ejecución y una cobertura de corpus
    explícitos. Los perfiles reutilizan el mismo verification entry point
    y mecanismo de evaluación (NADR-29 §5.5 R24-R27).
    """

    FULL = "FULL"
    SMOKE = "SMOKE"


# Perfil SMOKE: lista hardcoded de documentos representativos (NADR-29 §5.4 R18-R23)
#
# Justificación de la selección (auditoría forense del corpus canonical v3.9):
# - El criterio por traits (traits ⊆ {native_pdf}) produce solo 2 documentos
#   calificantes en el corpus actual, activando el fallback siempre.
# - Una lista hardcoded de 5 documentos elegidos por representatividad es
#   determinista, estable, y cubre los principales rasgos del corpus.
#
# Selección (complejidad creciente):
# 1. doc_01_single: PDF nativo simple (baseline)
# 2. doc_04_table: Tablas anidadas + figuras flotantes (complejidad media)
# 3. doc_12_multi_col: Multi-columna (complejidad alta)
# 4. doc_18_table_math_doble_col: Combinación de 4 rasgos (stress test)
# 5. doc_22_table_fig_math: Todos los 5 rasgos (edge case)
SMOKE_DOCUMENT_IDS: frozenset[str] = frozenset({
    "doc_01_single",
    "doc_04_table",
    "doc_12_multi_col",
    "doc_18_table_math_doble_col",
    "doc_22_table_fig_math",
})


def get_profile_document_ids(
    profile: VerificationProfile,
    manifest: CorpusManifest,
) -> frozenset[str]:
    """Retorna los document_ids que cubre el perfil (NADR-29 §5.1 R3).

    Función pura, determinista (NADR-28 §5.2 R8). Retorna frozenset para
    inmutabilidad.

    NADR-F17BIS-29 §5.3 R14-R17: FULL retorna todos los documentos del
    manifest (cobertura completa gobernada por el corpus, no por duración
    ni costo).

    NADR-F17BIS-29 §5.4 R18-R23: SMOKE retorna lista hardcoded de documentos
    representativos, intersectada con el manifest para robustez ante cambios
    del corpus.

    Args:
        profile: Perfil de ejecución.
        manifest: Manifest del corpus canónico.

    Returns:
        frozenset de document_ids del perfil.

    Raises:
        ValueError: Si el perfil es desconocido.
    """
    if profile is VerificationProfile.FULL:
        return frozenset(doc.document_id for doc in manifest.documents)

    if profile is VerificationProfile.SMOKE:
        all_ids = frozenset(doc.document_id for doc in manifest.documents)
        return SMOKE_DOCUMENT_IDS & all_ids

    raise ValueError(f"Unknown profile: {profile}")