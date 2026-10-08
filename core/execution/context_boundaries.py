"""
Context Boundaries del Execution Plane — Documentación formal de DC-05.

Este módulo NO es un god-object. NO agrega comportamiento. NO encapsula
los contextos. Su única función es hacer EXPLÍCITOS los boundaries de
separación entre los 6 contextos especializados del execution plane,
conforme a:

  - DC-05 (F18_DC05_DECISION.md v1.0.0): MANTENER contextos especializados.
  - NADR-F18-02 §5.6 R20: context boundaries explícitos.
  - NADR-F18-02 §5.6 R21: no god-object.
  - ENGINEERING_PRINCIPLES §III: Explicit over Implicit.
  - ENGINEERING_PRINCIPLES §I: YAGNI (no crear código nuevo si ya existe).

God-Object Test aplicado (F18_DC05_DECISION.md §2.2):
  Cada contexto protege UN boundary único. Ningún contexto solapa
  responsabilidades con otro. Ningún módulo agrega múltiples contextos
  en un único objeto.

Thread-safety contract por contexto:
  ControlPlanePort:     SQLite WAL + busy_timeout (serializa writes)
  EventPlanePort:       SQLite WAL + busy_timeout (serializa writes)
  MaterializedPlanePort: SQLite WAL + busy_timeout (serializa writes)
  FSM State:            CAS versionado (optimistic locking)
  ContextResolver:      Thread-safe por diseño (tuplas inmutables)
  AssemblyContext:      Thread-safe por diseño (estado de solo lectura)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBoundary:
    """
    Documentación de un boundary de contexto.
    Inmutable: los boundaries no cambian durante el ciclo de vida del sistema.
    """
    context_name: str
    module_path: str
    responsibility: str
    thread_safety: str


# ── BOUNDARIES DE CONTEXTOS DEL EXECUTION PLANE (DC-05) ──

CONTROL_PLANE_BOUNDARY = ContextBoundary(
    context_name="ControlPlanePort",
    module_path="core/execution/ports.py::ControlPlanePort",
    responsibility=(
        "Scheduling, admission, task lifecycle. "
        "Claim/release de tareas, lease renewal, encolado. "
        "NO gestiona journal, NO gestiona projections, NO gestiona FSM."
    ),
    thread_safety="SQLite WAL + busy_timeout=30000 (serializa writes)",
)

EVENT_PLANE_BOUNDARY = ContextBoundary(
    context_name="EventPlanePort",
    module_path="core/execution/ports.py::EventPlanePort",
    responsibility=(
        "Journal de eventos, replay, idempotencia. "
        "Append WAL, get_replay, get_latest_event. "
        "NO gestiona scheduling, NO gestiona projections, NO gestiona FSM."
    ),
    thread_safety="SQLite WAL + busy_timeout=30000 (serializa writes)",
)

MATERIALIZED_PLANE_BOUNDARY = ContextBoundary(
    context_name="MaterializedPlanePort",
    module_path="core/execution/ports.py::MaterializedPlanePort",
    responsibility=(
        "Proyecciones de chunks traducidos, cache de resultados. "
        "get_projection_status, upsert_projection, get_assemblable_chunks. "
        "NO gestiona scheduling, NO gestiona journal, NO gestiona FSM."
    ),
    thread_safety="SQLite WAL + busy_timeout=30000 (serializa writes)",
)

FSM_STATE_BOUNDARY = ContextBoundary(
    context_name="FSM State",
    module_path="core/execution/state.py::DocumentState + FSMValidator",
    responsibility=(
        "Transiciones de estado del documento (CREATED→COMPLETED). "
        "Validación de transiciones, commands, CAS versionado. "
        "NO gestiona scheduling, NO gestiona journal, NO gestiona projections."
    ),
    thread_safety="CAS versionado (optimistic locking)",
)

CONTEXT_RESOLVER_BOUNDARY = ContextBoundary(
    context_name="ContextResolver",
    module_path="core/context/context_resolver.py::ContextResolverProtocol",
    responsibility=(
        "Contexto jerárquico para enriquecimiento de traducción. "
        "Breadcrumbs, depth, context_id. "
        "NO gestiona scheduling, NO gestiona journal, NO gestiona FSM."
    ),
    thread_safety="Thread-safe por diseño (tuplas inmutables)",
)

ASSEMBLY_CONTEXT_BOUNDARY = ContextBoundary(
    context_name="AssemblyContext",
    module_path="core/compiler/assembly_context.py::AssemblyExecutionContext",
    responsibility=(
        "Validación de completitud topológica antes de ensamblar. "
        "expected_node_ids, materialized_node_ids, missing_node_ids. "
        "NO gestiona scheduling, NO gestiona journal, NO gestiona FSM."
    ),
    thread_safety="Thread-safe por diseño (estado de solo lectura)",
)

# ── REGISTRO DE BOUNDARIES (para verificación programática) ──

ALL_BOUNDARIES: tuple[ContextBoundary, ...] = (
    CONTROL_PLANE_BOUNDARY,
    EVENT_PLANE_BOUNDARY,
    MATERIALIZED_PLANE_BOUNDARY,
    FSM_STATE_BOUNDARY,
    CONTEXT_RESOLVER_BOUNDARY,
    ASSEMBLY_CONTEXT_BOUNDARY,
)