# tests/unit/test_state_projection.py
"""
Tests del contrato normativo de proyección PipelineStep → DocumentState.

Task 4.1.1 — Paso A.1.b
NADR-09 §5.1 R3: Los pasos de la aplicación MUST estar sincronizados
con los estados de la máquina de estados finitos.

CONTRATO NORMATIVO (Paso A.1.a — FROZEN):

| PipelineStep           | DocumentState         | Cardinalidad |
|------------------------|-----------------------|--------------|
| INITIALIZING           | CREATED               | 1:1          |
| PARSING                | PARSING               | 1:1          |
| CHUNKING               | PROCESSING            | N:1          |
| DISPATCHING            | PROCESSING            | N:1          |
| READY_FOR_ASSEMBLY     | READY_FOR_ASSEMBLY    | 1:1          |
| ASSEMBLING             | ASSEMBLING            | 1:1          |
| READY_FOR_COMPILATION  | READY_FOR_COMPILATION | 1:1          |
| COMPILING              | COMPILING             | 1:1          |
| FINISHED               | COMPLETED             | 1:1          |

Estos tests verifican el contrato funcional de los enums.
No verifican implementación (la Policy se implementa en A.4).
No verifican dependencias entre capas (pyright / import-linter).

Nota de secuenciación TDD:
    Estos tests fallarán en A.2 hasta que A.3 sincronice PipelineStep.
"""

from core.pipeline.job import PipelineStep
from core.execution.state import DocumentState


# ------------------------------------------------------------------
# Matriz normativa declarativa (única fuente de verdad del test)
# ------------------------------------------------------------------

# Los 9 PipelineStep que el contrato exige.
EXPECTED_STEPS: tuple[str, ...] = (
    "INITIALIZING",
    "PARSING",
    "CHUNKING",
    "DISPATCHING",
    "READY_FOR_ASSEMBLY",
    "ASSEMBLING",
    "READY_FOR_COMPILATION",
    "COMPILING",
    "FINISHED",
)

# Pasos que NO deben existir (sin estado FSM asociado).
FORBIDDEN_STEPS: tuple[str, ...] = (
    "AUDITING",
)

# Los DocumentState destino que el contrato exige.
EXPECTED_TARGET_STATES: tuple[str, ...] = (
    "CREATED",
    "PARSING",
    "PROCESSING",
    "READY_FOR_ASSEMBLY",
    "ASSEMBLING",
    "READY_FOR_COMPILATION",
    "COMPILING",
    "COMPLETED",
)


# ------------------------------------------------------------------
# Invariante 1: Los 9 PipelineStep normativos existen
# ------------------------------------------------------------------

def test_all_expected_pipeline_steps_exist() -> None:
    """
    NADR-09 §5.1 R3: Cada paso de la matriz normativa MUST existir
    en PipelineStep.

    Se verifica pertenencia al contrato del Enum vía __members__,
    no existencia incidental de un atributo.
    """
    missing = [name for name in EXPECTED_STEPS if name not in PipelineStep.__members__]
    assert missing == [], (
        f"PipelineStep carece de pasos normativos: {missing}. "
        f"NADR-09 §5.1 R3 exige sincronización completa con DocumentState."
    )


# ------------------------------------------------------------------
# Invariante 2: AUDITING no existe (no tiene estado FSM)
# ------------------------------------------------------------------

def test_no_forbidden_pipeline_steps_exist() -> None:
    """
    PipelineStep MUST NOT incluir pasos sin estado FSM asociado.

    AUDITING no tiene correspondencia en DocumentState. Si existe,
    debe migrarse su consumidor y eliminarse del Enum (Paso A.3).
    """
    existing_forbidden = [name for name in FORBIDDEN_STEPS if name in PipelineStep.__members__]
    assert existing_forbidden == [], (
        f"PipelineStep contiene pasos sin estado FSM: {existing_forbidden}. "
        f"Migrar consumidores y eliminar antes de cerrar Task 4.1.1."
    )


# ------------------------------------------------------------------
# Invariante 3: El número de pasos coincide con el contrato
# ------------------------------------------------------------------

def test_pipeline_step_count_matches_contract() -> None:
    """
    La cantidad de miembros de PipelineStep MUST coincidir exactamente
    con la matriz normativa.

    Esto detecta tanto pasos faltantes como pasos residuales no
    contemplados por el contrato.
    """
    expected_count = len(EXPECTED_STEPS)
    actual_count = len(PipelineStep.__members__)
    assert actual_count == expected_count, (
        f"PipelineStep tiene {actual_count} miembros, el contrato espera "
        f"{expected_count}. Verificar matriz de transición normativa."
    )


# ------------------------------------------------------------------
# Invariante 4: Los 9 DocumentState destino existen
# ------------------------------------------------------------------

def test_all_target_document_states_exist() -> None:
    """
    Cada DocumentState de la matriz normativa MUST existir.

    DocumentState ya es el modelo canónico (no se modifica en Task 4.1.1).
    Este test es una verificación de sanidad del modelo de dominio.
    """
    missing = [name for name in EXPECTED_TARGET_STATES if name not in DocumentState.__members__]
    assert missing == [], (
        f"DocumentState carece de estados normativos: {missing}. "
        f"El modelo de dominio no debe modificarse sin revisar la matriz."
    )