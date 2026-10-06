# F18_DC05_DECISION.md

**Documento:** docs/architecture/adr/phase-18/reports/F18_DC05_DECISION.md
**Estado:** FROZEN v1.0.0
**Fecha:** 2026-10-05
**Tipo:** Decisión arquitectónica (DC-05)
**Naturaleza:** Resolución de estructura de contextos de ejecución.
**Evidencia vinculante:**
  - PROJECT_TREE.txt (estructura de archivos)
  - HITO_0.11 v1.0.1 (Current State Map, Fronteras Hexagonales)
  - ADR_F18_MASTER (Invariantes y Reglas de Gobernanza)
  - ENGINEERING_PRINCIPLES (YAGNI, Hexagonal, Inmutabilidad de DTOs)
  - NADR-F18-01 (Scientific Identity)
**Mandato:** Resolver DC-05 (unificar ExecutionContext vs contextos especializados) aplicando test de god-object.
**Decisión:** MANTENER contextos especializados por plano (CQRS existente).

---

## 1. RESUMEN EJECUTIVO

Se evaluaron dos opciones para la estructura de contextos del execution plane:

| Opción | Descripción | Evidencia | Decisión |
|---|---|---|---|
| **A** | Mantener contextos especializados | 6 contextos con fronteras claras, sin solapamiento, preserva inmutabilidad | ACEPTADA |
| **B** | Unificar en ExecutionContext monolítico | Sin evidencia de beneficio; crearía god-object; violaría inmutabilidad de DTOs | Rechazada |

**Decisión DC-05:** Mantener los 6 contextos especializados existentes, cada uno protegiendo un boundary de responsabilidad único conforme al patrón CQRS.

**Justificación normativa:**
- ENGINEERING_PRINCIPLES (Hexagonal): puertos especializados por responsabilidad.
- ENGINEERING_PRINCIPLES (YAGNI): no unificar sin evidencia de necesidad.
- ADR_F18_MASTER (Reuse Before Invent): sin evidencia de insuficiencia.

---

## 2. ANÁLISIS FORENSE DE CONTEXTOS EXISTENTES

### 2.1 Inventario de contextos (PROJECT_TREE.txt + HITO_0.11)

| Contexto | Archivo | Responsabilidad | Plano CQRS |
|---|---|---|---|
| ControlPlanePort | core/execution/ports.py -> infra/db/control_repo.py | Task leases, scheduling, admission, retry logic | Control Plane |
| EventPlanePort | core/execution/ports.py -> infra/db/event_repo.py | WAL de eventos (chunk_events_log), replay, idempotencia | Event Plane |
| MaterializedPlanePort | core/execution/ports.py -> infra/db/materialized_repo.py | Proyecciones de chunks traducidos, cache de resultados | Materialized Plane |
| FSM State | core/execution/state.py + core/pipeline/state_store.py | Estado del documento (CREATED->COMPLETED), transiciones | State Machine |
| ContextResolver | core/context/context_resolver.py | Contexto jerárquico para traducción (breadcrumbs, depth) | Translation Context |
| AssemblyContext | core/compiler/assembly_context.py | Validación de completitud topológica antes de ensamblado | Assembly Validation |

### 2.2 Test de god-object

**Pregunta:** ¿Qué boundary protege cada contexto? ¿Se solapan las responsabilidades?

| Contexto | Boundary que protege | ¿Se solapa con otros? |
|---|---|---|
| ControlPlanePort | Scheduling, admission, task lifecycle (claim_task, renew_lease, mark_completed) | No (solo gestiona tareas pendientes y su lifecycle) |
| EventPlanePort | Journal de eventos, replay, deduplicación idempotente | No (solo gestiona WAL y replay) |
| MaterializedPlanePort | Proyecciones materializadas, cache de resultados de traducción | No (solo gestiona proyecciones y su estado) |
| FSM State | Transiciones de estado del documento (CREATED->PARSING->PROCESSING->COMPLETED) | No (solo gestiona lifecycle del documento) |
| ContextResolver | Contexto jerárquico para enriquecimiento de traducción (breadcrumbs, depth, context_id) | No (solo resuelve contexto para enriquecimiento) |
| AssemblyContext | Validación de completitud topológica (todos los nodos presentes antes de ensamblar) | No (solo valida antes de ensamblar) |

**Resultado del test:** Cada contexto protege un boundary de responsabilidad único. No hay solapamiento. No hay god-object.

### 2.3 Evidencia de HITO_0.11 v1.0.1

HITO_0.11 (Current State Map) documenta 13 autoridades del execution plane, cada una con frontera bien delimitada:
- 11 autoridades RETAIN (ControlPlane, EventPlane, MaterializedPlane, SystemPlane, FSM, Reconciler, RecoveryDaemon, RateLimiter, Cache, DocumentRepository, CommandHandlers).
- 2 autoridades REFACTOR (CircuitBreaker, ProfileStore).
- 12/13 superficies arquitectónicas auditadas respetan frontera hexagonal.
- 1 violación de frontera (imports cruzados core->apps en benchmark/runners).

**Conclusión:** La arquitectura ya sigue el patrón CQRS con contextos especializados por plano. No hay evidencia de necesidad de unificación.

---

## 3. EVALUACIÓN DE OPCIONES

### 3.1 Opción A: Mantener contextos especializados (status quo)

**Descripción:** Continuar usando los 6 contextos especializados existentes, cada uno con su propio puerto Protocol en core/ y su implementación en infra/.

**Evidencia a favor:**
1. Fronteras claras: Cada contexto protege un boundary de responsabilidad único.
2. Patrón CQRS implementado: Control/Event/Materialized separados (HITO_0.11).
3. Sin solapamiento: Test de god-object confirma ausencia de duplicación.
4. Hexagonal Architecture: Puertos especializados por responsabilidad.
5. Testabilidad: Cada contexto puede mockearse independientemente.
6. Mantenibilidad: Cambios en un contexto no afectan a los otros.
7. Evidencia de Fase 0: HITO_0.11 valida la estructura actual.

**Evidencia en contra:**
1. Complejidad de inyección: 6 parámetros en constructores vs 1.
2. Coordinación: Requiere orquestación explícita entre contextos.

**Cumplimiento de principios:**
- YAGNI: Satisface (No unificar sin evidencia de necesidad).
- Hexagonal: Satisface (Puertos especializados por responsabilidad).
- Explicit over Implicit: Satisface (Inyección explícita de cada contexto).
- Reuse Before Invent: Satisface (Sin evidencia de insuficiencia).
- Single Responsibility Principle: Satisface (Cada contexto tiene 1 responsabilidad).

### 3.2 Opción B: Unificar en ExecutionContext monolítico

**Descripción:** Crear un único ExecutionContext que encapsule los 6 contextos especializados y los exponga como propiedades.

**Evidencia a favor:**
1. Simplificación de inyección: 1 parámetro vs 6 en constructores.
2. Coordinación: Facilita passing de contexto entre operaciones.

**Evidencia en contra:**
1. God-object: 6 responsabilidades diferentes en 1 clase.
2. Violación de SRP: Single Responsibility Principle violado.
3. Violación de Hexagonal: ENGINEERING_PRINCIPLES exige puertos especializados.
4. Sin evidencia de beneficio: No hay métrica que justifique la unificación.
5. Testabilidad reducida: Mockear 6 responsabilidades en 1 objeto es más complejo.
6. Mantenibilidad reducida: Cambios en un contexto requieren recompilar todo.
7. Acoplamiento aumentado: Todos los consumidores dependen de ExecutionContext.
8. Violación de inmutabilidad de DTOs: ContextResolver retorna ResolvedContext (@dataclass(frozen=True)), mientras que DocumentState es mutable (transiciones FSM). Unificarlos en un ExecutionContext mutable rompería el contrato de inmutabilidad de DTOs (ENGINEERING_PRINCIPLES).

**Violaciones normativas:**
- YAGNI: unificar sin evidencia de necesidad.
- Hexagonal: viola puertos especializados.
- Inmutabilidad de DTOs: rompe contrato frozen.
- Reuse Before Invent: sustituye sin evidencia de insuficiencia.
- Single Responsibility Principle: 6 responsabilidades en 1 clase.

---

## 4. DECISIÓN

**DC-05 queda resuelto: MANTENER contextos especializados por plano (Opción A).**

El execution plane continúa usando 6 contextos especializados:
1. ControlPlanePort -> scheduling/admission/task lifecycle
2. EventPlanePort -> journal/durability/replay
3. MaterializedPlanePort -> projections/cache
4. FSM State -> document lifecycle transitions
5. ContextResolver -> translation context (breadcrumbs/depth)
6. AssemblyContext -> assembly validation

Cada contexto se inyecta explícitamente como parámetro independiente en los constructores que lo requieren.

---

## 5. JUSTIFICACIÓN NORMATIVA

### 5.1 YAGNI
No hay evidencia de que la unificación de contextos resuelva un problema actual. La complejidad de inyección (6 parámetros vs 1) no constituye insuficiencia arquitectónica; es una consecuencia natural del patrón CQRS.

### 5.2 Hexagonal Architecture
El patrón hexagonal exige puertos especializados por responsabilidad. Unificar 6 contextos en 1 violaría este principio al crear un puerto monolítico que expone 6 responsabilidades diferentes.

### 5.3 Reuse Before Invent
La estructura actual de 6 contextos especializados funciona correctamente según HITO_0.11. No hay evidencia de insuficiencia (bugs, performance issues, complejidad inmanejable) que justifique sustituirla por un ExecutionContext monolítico.

### 5.4 Single Responsibility Principle (SOLID)
Cada contexto tiene una y solo una razón para cambiar. Unificarlos en ExecutionContext violaría SRP: un cambio en scheduling requeriría modificar ExecutionContext, que también contiene journal, projections, FSM, etc.

### 5.5 HITO_0.11 (Current State Map)
HITO_0.11 documenta 13 autoridades del execution plane con fronteras bien delimitadas. La estructura actual es resultado de evolución arquitectónica validada, no de diseño arbitrario. Cambiarla sin evidencia de insuficiencia violaría el principio de estabilidad arquitectónica.

---

## 6. IMPLICACIONES

### 6.1 Para el execution plane
1. Los 6 contextos especializados se mantienen sin modificaciones.
2. Inyección explícita: cada consumidor declara explícitamente qué contextos necesita en su constructor.
3. Sin orquestador central: la coordinación entre contextos es responsabilidad del caso de uso (use case) que los consume.
4. Testabilidad preservada: cada contexto puede mockearse independientemente.

### 6.2 Para Gate 3 (implementación de capacidades NADR-F18-02)
Gate 3 implementa bounded execution, admission/backpressure, cancellation y operational visibility sobre los contextos especializados existentes:
- Bounded execution (C1): implementado en ControlPlanePort (admission control).
- Backpressure (C3): implementado en ControlPlanePort (queue depth monitoring).
- Cancellation (C6): implementado en ControlPlanePort + EventPlanePort.
- Operational visibility (NADR-F18-02 §5.7 R23-R26): implementado en todos los contextos vía telemetría (Task 1.1.1 ya instrumentó run_regression.py).

### 6.3 Para DC-08 (write-policy SQLite + journal)
DC-08 (Subfase 18.2) resolverá la semántica de journal sobre EventPlanePort existente, no sobre un ExecutionContext unificado. La decisión de DC-05 preserva la frontera de EventPlanePort como autoridad de journal.

### 6.4 Para DC-10 (fairness y admission)
DC-10 (Subfase 18.3) resolverá admission control sobre ControlPlanePort existente, no sobre un ExecutionContext unificado. La decisión de DC-05 preserva la frontera de ControlPlanePort como autoridad de admission.

### 6.5 Para DF-13 (model_de_execution ausente de identity_chain)
La decisión de DC-05 refuerza que el modo de ejecución debe registrarse en el contexto operacional (DocumentState o metadata de telemetría), nunca en ContextResolver (científico). Esto preserva NADR-F18-01 (Scientific identity MUST NOT incluir propiedades de ejecución). DF-13 se mantiene como hallazgo abierto para Gate 3 (Task 3.4.2, trazabilidad de identidad).

---

## 7. TRAZABILIDAD NORMATIVA

| Fuente | Regla/Sección | Cumplimiento |
|---|---|---|
| ENGINEERING_PRINCIPLES | YAGNI | No unificar sin evidencia de necesidad |
| ENGINEERING_PRINCIPLES | Hexagonal Architecture | Puertos especializados por responsabilidad |
| ENGINEERING_PRINCIPLES | Inmutabilidad de DTOs | Preserva contrato frozen de ResolvedContext |
| ADR_F18_MASTER | Reuse Before Invent | Sin evidencia de insuficiencia, no sustituir |
| Single Responsibility Principle | SRP (SOLID) | Cada contexto tiene 1 responsabilidad |
| HITO_0.11 | Current State Map | 13 autoridades con fronteras bien delimitadas |
| HITO_0.11 | Fronteras Hexagonales | 12/13 superficies respetan frontera |

---

## 8. MATRIZ DE TRAZABILIDAD DC

| DC | Relación con DC-05 | Estado |
|---|---|---|
| DC-01 | Modelo de concurrencia (resuelto en F18_DC01_DECISION.md) | RESUELTO |
| DC-02 | Contrato de identidad (resuelto en F18_IDENTITY_BOUNDARY_CONTRACT.md) | RESUELTO (DC-02-A) |
| DC-05 | Este documento resuelve DC-05 | RESUELTO |
| DC-08 | Write-policy sobre EventPlanePort existente | PENDIENTE (Subfase 18.2) |
| DC-10 | Admission sobre ControlPlanePort existente | PENDIENTE (Subfase 18.3) |
| DC-11 | Semántica de admisión sobre FSM State existente | PENDIENTE (Subfase 18.3) |
| DC-12 | Guard diferencial (usa DC-02-A) | PENDIENTE (Subfase 18.5) |

---

## 9. CIERRE

**Estado:** FROZEN v1.0.0
**Condición de cierre:** DC-05 resuelto con test de god-object aplicado; dos opciones evaluadas; decisión documentada con justificación normativa; análisis de inmutabilidad de DTOs incluido; trazabilidad a ENGINEERING_PRINCIPLES, ADR_F18_MASTER y HITO_0.11 completa.
**Próximo paso:** Gate 2 completado (Wave 2.1, 2.2, 2.3 todas DONE). Gate 3 (Subfase 18.1 implementation) puede proceder.