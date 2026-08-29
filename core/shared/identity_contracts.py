"""Contratos de dominio para identidades criptográficas (NADR-F17BIS-17 §5.1).

Este módulo centraliza los contratos de dominio para campos que participan
en identidades criptográficas, garantizando inyectividad del framing.

Ubicación en core/shared/ porque ambos bounded contexts (core/ast y
core/benchmark/corpus) necesitan acceder a estos contratos sin crear
dependencias invertidas. Precedente: core/shared/crypto.py.

DC-04 (resuelto): Validación de document_id (excluir ':')
DC-05 (resuelto): Validación de node_id (excluir ':')
DF-01 (resuelto en Wave 2.4): Validación de ground_truth_state (excluir ':')

@see NADR-F17BIS-17 §5.1 R1-R4
@see NADR-F17BIS-17 §5.3 R9 (delimitadores excluidos del dominio)
"""

from typing import Annotated

from pydantic import StringConstraints

# =====================================================================
# NADR-F17BIS-17 §5.1: Contrato de dominio para document_id
# =====================================================================
#
# DOMINIO: cualquier string no vacío que NO contenga el carácter ':'.
# PROHIBIDO: ':' (delimitador de campo en el framing criptográfico
#            de ManifestFingerprintCalculator).
# JUSTIFICACIÓN: garantizar inyectividad del encoding. Si document_id
#                pudiera contener ':', dos payloads distintos podrían
#                producir representaciones ambiguas antes del hash.
# VALIDACIÓN: fail-fast en construcción vía StringConstraints (Pydantic v2).
# SENTINEL: no aplica (document_id es obligatorio).
DocumentId = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^:]+$")]

# =====================================================================
# NADR-F17BIS-17 §5.1: Contrato de dominio para node_id
# =====================================================================
#
# DOMINIO: cualquier string no vacío que NO contenga el carácter ':'.
# PROHIBIDO: ':' (delimitador de campo en el framing criptográfico
#            de OracleSemanticIdentityCalculator).
# JUSTIFICACIÓN: garantizar inyectividad del encoding en oracle_hash.
#                El framing es node_id:type:strategy:payload_hash.
# VALIDACIÓN: fail-fast en construcción vía StringConstraints (Pydantic v2).
# SENTINEL: no aplica (node_id es obligatorio).
NodeId = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^:]+$")]

# =====================================================================
# NADR-F17BIS-17 §5.1: Contrato de dominio para ground_truth_state
# =====================================================================
#
# DOMINIO: cualquier string no vacío que NO contenga el carácter ':'.
# PROHIBIDO: ':' (delimitador de campo en el framing criptográfico
#            de ManifestFingerprintCalculator).
# JUSTIFICACIÓN: garantizar inyectividad del encoding en manifest_hash.
#                El framing incluye ground_truth_state como dimensión de
#                identidad del proceso de certificación.
# VALIDACIÓN: fail-fast en construcción vía StringConstraints (Pydantic v2).
# SENTINEL: None es válido (interpretado como DRAFT por la capa de consumo,
#           según DF-13). El sentinel "none" en el framing se aplica solo
#           cuando el valor es None.
# VALORES CANÓNICOS: los valores provienen de GroundTruthLifecycleState
#                    enum ("draft", "audited", "validated", "sealed"),
#                    pero el contrato permite cualquier string sin ':'
#                    para no acoplar el DTO al enum (Problema B).
#
# DF-01 (Wave 2.4): Cierre de asimetría defensiva. ground_truth_state
#                   participa en el framing de manifest_hash al igual que
#                   document_id, por lo que debe tener el mismo contrato.
GroundTruthState = Annotated[str, StringConstraints(min_length=1, pattern=r"^[^:]+$")]