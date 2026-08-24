"""Modelos de dominio del Ground Truth.

Materializa NADR-F17BIS-12 §5.1 R1 y R2:
- R1: El Ground Truth se modela como una entidad de dominio.
- R2: Tipos disjuntos para borrador curado y oráculo sellado, sin conversión
     implícita.

Este módulo define la ontología fundacional del Ground Truth:
- GroundTruthDraft: borrador curado (mutable en el sentido de ciclo de vida,
  pero inmutable en instancia).
- SealedOracle: oráculo sellado (inmutable, portador de la verdad científica).

Ambos son entidades de dominio con identidad propia (document_id). Cada
entidad es la raíz de su propio agregado (en el sentido DDD: una entidad
simple que actúa como Aggregate Root de una frontera de consistencia
unitaria). La relación con CorpusManifest es por referencia (document_id),
no por composición.

NOTA SOBRE VALIDACIÓN DE NO-VACIEDAD: Este módulo NO valida que la secuencia
de nodos sea no-vacía. La validación de no-vaciedad es responsabilidad del
contrato de validez estructural (NADR-13 §5.1 R2, Task 2.1.2). Las entidades
aceptan tuplas vacías a nivel de modelo; la autoridad de sellado debe
rechazarlas antes de crear un SealedOracle.
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple

from pydantic import BaseModel, ConfigDict, Field

from core.ast.models import ASTNode


class GroundTruthLifecycleState(str, Enum):
    """Estados de ciclo de vida del Ground Truth.

    NADR-F17BIS-12 §5.2 R4: define explícitamente los estados y las únicas
    transiciones permitidas (gobernadas por Task 1.2.1).

    Este enum se utiliza para:
    - Documentación de estados canónicos.
    - Parámetros de transición en la autoridad de sellado (Task 1.2.1).
    - NO para determinar el tipo de la entidad (eso lo hace la clase misma).

    NOTA DE TRAZABILIDAD: La correspondencia entre estos 4 estados y los
    tipos disjuntos (GroundTruthDraft, SealedOracle) es responsabilidad de
    Task 1.2.1. Las preguntas abiertas son:
    - ¿AUDITED y VALIDATED son sub-estados de DRAFT?
    - ¿Son estados internos del proceso de sellado (no estados del oráculo)?
    - ¿Requieren tipos propios?
    Task 1.2.1 debe resolver estas preguntas explícitamente.
    """

    DRAFT = "draft"
    AUDITED = "audited"
    VALIDATED = "validated"
    SEALED = "sealed"

class DraftSubState(str, Enum):
    """Sub-estados del borrador curado.

    NADR-F17BIS-12 §5.2 R4: AUDITED y VALIDATED son sub-estados del Draft,
    estados del proceso de curaduría antes del sello.

    Resolución de DF-06: AUDITED y VALIDATED son sub-estados del Draft,
    no estados del oráculo ni tipos propios.
    """

    DRAFT = "draft"
    AUDITED = "audited"
    VALIDATED = "validated"


class GroundTruthDraft(BaseModel):
    """Borrador curado del Ground Truth.

    NADR-F17BIS-12 §5.1 R1: entidad de dominio con identidad propia
    (document_id).

    NADR-F17BIS-12 §5.1 R2: tipo disjunto del oráculo sellado. No existe
    conversión implícita entre GroundTruthDraft y SealedOracle; la
    transición es gobernada por la autoridad de sellado (Task 1.2.1).

    Invariantes (ENGINEERING_PRINCIPLES §II, NADR-F17BIS-12 §5.3 R7-R8):
    - La entidad es ``frozen=True`` (inmutabilidad de instancia).
    - Puede ser reemplazada por una nueva instancia durante la curaduría
      (NADR-F17BIS-12 §5.3 R8), pero nunca mutada in-place.
    """

    model_config = ConfigDict(frozen=True)

    document_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Identidad de la entidad. Referencia al CorpusDocumentMetadata "
            "en el manifiesto del corpus (relación por ID, no por composición)."
        ),
    )
    nodes: Tuple[ASTNode, ...] = Field(
        ...,
        description="Secuencia inmutable de nodos AST del borrador curado.",
    )

    sub_state: DraftSubState = Field(
        default=DraftSubState.DRAFT,
        description=(
            "Sub-estado del borrador curado. Estados del proceso de "
            "curaduría antes del sello (DF-06 resuelto: AUDITED y "
            "VALIDATED son sub-estados del Draft)."
        ),
    )


class SealedOracle(BaseModel):
    """Oráculo sellado — verdad científica inmutable.

    NADR-F17BIS-12 §5.1 R1: entidad de dominio con identidad propia
    (document_id).

    NADR-F17BIS-12 §5.1 R2: tipo disjunto del borrador curado. No existe
    conversión implícita desde GroundTruthDraft; la creación de un
    SealedOracle es gobernada por la autoridad de sellado (Task 1.2.1)
    tras validar las invariantes de completitud y validez (Gate 2).

    Invariantes (ENGINEERING_PRINCIPLES §II, NADR-F17BIS-12 §5.3 R9):
    - La entidad es ``frozen=True`` (inmutabilidad de instancia).
    - Un oráculo sellado NO puede ser alterado ni sobrescrito por
      operaciones de curaduría.
    """

    model_config = ConfigDict(frozen=True)

    document_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Identidad de la entidad. Referencia al CorpusDocumentMetadata "
            "en el manifiesto del corpus (relación por ID, no por composición)."
        ),
    )
    nodes: Tuple[ASTNode, ...] = Field(
        ...,
        description="Secuencia inmutable de nodos AST del oráculo sellado.",
    )


def hydrate_ground_truth(
    document_id: str,
    nodes: Tuple[ASTNode, ...],
    state: GroundTruthLifecycleState,
) -> GroundTruthDraft | SealedOracle:
    """Fábrica de hidratación: único punto de construcción de entidades.

    NADR-F17BIS-12 §5.1 R3: garantiza que un artefacto serializado no sea
    tratado como oráculo sin hidratación previa vía contrato canónico.

    Esta fábrica es consumida por:
    - La autoridad de sellado (Task 1.2.1) al sellar (state=SEALED).
    - Casos de uso de lectura que conocen el estado por contexto.

    La validación estructural de los nodos (no-vaciedad, integridad) es
    responsabilidad del contrato de validez (NADR-F17BIS-13 §5.1 R2,
    Task 2.1.2), no de esta fábrica.

    NOTA SOBRE PERSISTENCIA DEL ESTADO:
    - DRAFT, AUDITED, VALIDATED son estados efímeros del proceso de
      curaduría. El artefacto serializado NO porta metadata de estado
      (NADR-F17BIS-01 FROZEN §5.7). Al cargar desde disco, el consumidor
      debe proveer el estado explícitamente.
    - SEALED es el estado persistente del oráculo. La verificación del
      estado SEALED es responsabilidad de Gate 3 (NADR-F17BIS-14 §5.2,
      DF-13), no de esta fábrica. Esta fábrica confía en el estado
      provisto por el consumidor (operación trust-based).

    NOTA SOBRE ESTADOS EFÍMEROS:
    - Los estados AUDITED y VALIDATED son aceptados por esta fábrica por
      completitud de API y para testing. En la práctica, estos estados son
      producidos exclusivamente por LifecycleTransitionAuthority durante la
      sesión de curaduría en memoria, no por hidratación desde disco.
    - Al cargar desde disco, el estado por defecto es DRAFT (el artefacto
      no porta metadata de estado).
    """
    if state == GroundTruthLifecycleState.SEALED:
        return SealedOracle(document_id=document_id, nodes=nodes)
    if state == GroundTruthLifecycleState.DRAFT:
        return GroundTruthDraft(
            document_id=document_id,
            nodes=nodes,
            sub_state=DraftSubState.DRAFT,
        )
    if state == GroundTruthLifecycleState.AUDITED:
        return GroundTruthDraft(
            document_id=document_id,
            nodes=nodes,
            sub_state=DraftSubState.AUDITED,
        )
    if state == GroundTruthLifecycleState.VALIDATED:
        return GroundTruthDraft(
            document_id=document_id,
            nodes=nodes,
            sub_state=DraftSubState.VALIDATED,
        )
    raise ValueError(
        f"Invariant failure: unknown lifecycle state '{state}' "
        f"for document '{document_id}'."
    )