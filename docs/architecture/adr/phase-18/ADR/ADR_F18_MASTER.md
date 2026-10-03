# ARCHITECTURE DECISION RECORD (ADR)

## ADR F18: Advanced Local Runtime — Execution Plane Maturity (ADR Maestro)

* **Estado:** FROZEN
* **Fecha de Emisión Original:** 2026-10-02
* **Fecha de Congelamiento:** — (pendiente de aprobación del Architecture Board)
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** 18 — Advanced Local Runtime
* **Módulos Afectados:** `apps/llm_workers/`, `apps/daemons/`, `apps/compiler/`, `core/execution/`, `core/pipeline/`, `core/resilience/`, `core/telemetry/`, `core/compiler/`, `infra/db/`, `infra/resilience/`, `runtime/`
* **Aprobación Architecture Board:** — (pendiente)
* **Derivado de:** ROADMAP_ARQUITECTONICO_LP v3.0 (§IV Fase 18), ADR_F17_BIS_MASTER v1.0.0, FASE0_AUDIT_CHARTER v1.0.0
* **Supersede:** — (primera emisión conforme a 2_METH_ADR_MASTER v1.0.1)

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 16 completó la estabilización del Core Engine y la Fase 17-BIS estableció la Scientific Baseline y el mecanismo de Continuous Verification. El ROADMAP_ARQUITECTONICO_LP v3.0 (§IV) define la Fase 18 como "Advanced Local Runtime" con el objetivo de exprimir el rendimiento computacional local eliminando bloqueos I/O y optimizando el ciclo de CPU y memoria.

**Pivot Normativo (DC-06a, decisión de Board 2026-10-01):**

> La Fase 18 constituye la maduración del Execution Plane local para operar bajo recursos finitos con concurrencia controlada, backpressure, recovery, idempotencia y cancelación, preservando la semántica científica, las autoridades existentes y la reproducibilidad de la evidencia científica. **F18 modifica el mecanismo de ejecución; no modifica la verdad científica.** El hito no significa "producto funcionalmente completo" mientras existan las Fases 19-21 del ROADMAP.

**Motivación:**

La auditoría forense de Fase 0 (12 HITOs FROZEN en `00-foundation/`) demostró que el Execution Plane actual presenta incertidumbres y fracturas estructurales que impiden demostrar actualmente la certificación científica bajo variación operacional: barreras síncronas en el flujo asíncrono nativo, durabilidad heterogénea entre autoridades, ventana post-effect/pre-journal no coordinada transaccionalmente, ausencia de mecanismo reproducible para demostrar neutralidad científica end-to-end, y telemetría existente no consumida por el entry point de medición.

**Vínculo al ROADMAP:**

Este ADR traduce los objetivos del ROADMAP §IV a capacidades arquitectónicas gobernadas. Las técnicas candidatas (pure async, object pools, zero-copy, lazy loading, batching adaptativo, LLM cache, SQLite cache, tiers 8k/32k/1M) permanecen subordinadas a evidencia de necesidad, compatibilidad arquitectónica y ausencia de degradación científica, conforme al principio "Benchmark Before Optimization".

---

## 2. PROBLEMA ARQUITECTÓNICO Y ESTADO OBSERVADO

La auditoría forense de Fase 0 identificó las siguientes incertidumbres estructurales, cada una con evidencia trazable a `00-foundation/`:

1. **Barrera síncrona en flujo asíncrono:** El daemon de producción utiliza `SyncProviderBridge` que introduce `future.result(timeout=180.0)` bloqueando el hilo llamante (E-0.1-001). El impacto cuantitativo en C1/C3 no ha sido medido (GAP-0.1-01).
2. **Durabilidad heterogénea:** ProfileStore y Circuit Breaker operan in-memory sin persistencia (E-0.2-004, E-0.2-006). Tras crash, el estado se pierde completamente. El coste agregado de re-inferencia y el riesgo de recuperación agresiva post-crash no han sido cuantificados (GAP-0.2-01, GAP-0.2-02).
3. **Coordinación transaccional journal/efecto externo:** El orden `execute() → append_wal()` abre una ventana post-effect/pre-journal cuya compatibilidad con INV-JOURNAL no está demostrada bajo las garantías actuales de idempotencia y recovery (E-0.2-003, E-0.8-003, E-0.8-012). GAP-0.2-04.
4. **Ausencia de guard diferencial:** No existe mecanismo reproducible para ejecutar y comparar dos modos de ejecución bajo iguales parámetros científicos. Los prerrequisitos están verificados como implementación, pero la invariancia end-to-end bajo variación operacional no ha sido demostrada experimentalmente (GAP-0.4-01).
5. **Identidad científica vs operacional:** No existe definición congelada que determine qué parámetros pertenecen a scientific identity y cuáles a operational metadata. Esta ambigüedad impide definir el contrato de comparación del guard diferencial (GAP-0.4-03, DC-02).
6. **Coordinated shutdown no identificado en las superficies auditadas:** No se identificó una capacidad de coordinated shutdown suficientemente demostrada en las superficies auditadas (E-0.8-009, GAP-0.8-01).
7. **Telemetry loss en crash abrupto:** `SQLiteTelemetryGateway` pierde el 100% del buffer in-memory bajo crash abrupto (E-0.9-012). Graceful shutdown persiste 200/200 eventos; crash abrupto persiste 0/200. GAP-0.9-02.

### 2.1 Architectural Outcome of Gate 0

La auditoría forense de Fase 0 produjo: 12 HITOs FROZEN, 52 entradas de evidencia clasificadas epistémicamente, 25 GAPs abiertos con fase de resolución propuesta explícita (3 P0, 15 P1, 7 P2), 13 Decision Candidates con estado de gobernanza válido, y 4 outputs obligatorios de Charter §8 completados.

**Veredicto de Fase 0:** Discovery complete / evidence package frozen. Sabemos qué sabemos, qué no sabemos, qué decisiones están autorizadas, qué decisiones siguen abiertas, qué evidencia las habilita y bajo qué condición pueden resolverse.

---

## 3. SEPARACIÓN DE CONCEPTOS FUNDAMENTALES

La arquitectura de Fase 18 distingue estrictamente las siguientes dimensiones ortogonales. Cada dimensión tiene reglas de no-colapso explícitas:

* **Scientific Identity ≠ Execution Identity ≠ Operational State:** Cambiar el modo de ejecución no constituye nueva identidad científica.
* **Concurrency Model ≠ Execution Semantics:** Cambiar el modelo de concurrencia no debe alterar la semántica científica.
* **Durability Mechanism ≠ Journal Semantics:** Elegir un mecanismo de persistencia no define la semántica de journal; la semántica es obligatoria, el mecanismo es abierto.
* **Cache Hit ≠ Provider Determinism:** Un hit de cache no demuestra que el proveedor sea determinista; DC-03 caracteriza el determinismo observable independientemente.
* **Resource Pressure ≠ Scientific Outcome:** Agotamiento de recursos produce outcome operacional, nunca señal científica.
* **Recovery ≠ Exactly-once delivery:** Recovery garantiza idempotent apply + ventana de duplicación acotada, no exactly-once.
* **Performance ≠ Architectural correctness:** Medición de performance no implica corrección arquitectónica.

---

## 4. ALCANCE Y NO-OBJETIVOS (OUT OF SCOPE)

### 4.1 In-Scope
Fase 18 gobierna la maduración del Execution Plane local para permitir ejecución concurrente, acotada por recursos, recuperable, cancelable, idempotente y científicamente neutra. Comprende: execution identity, resource-bounded concurrency, admission control, backpressure, durable execution, scheduling, adaptive batching, provider characterization, cache semantics, minimal operational visibility, y differential verification.

### 4.2 Out-of-Scope (con dueño explícito)
* Semantic/embedding cache, Smart model routing, Parser routing, Adaptive healing → **Fase 21**
* CLI de grado industrial, Docker packaging, Gestión de configuración de usuario → **Fase 19**
* Deep local observability, Reportes post-procesamiento, Interfaz forense sobre SQLite → **Fase 20**
* Distribución multi-node, Redis, Kubernetes, microservicios → **Fuera del ROADMAP**
* Re-baseline científico → **Fase 17-BIS / proceso de recalibración**
* Modificación de Ground Truth / Sealed Oracle como efecto lateral → **Prohibido por NADR-26**
* Redefinición de thresholds científicos sin recalibración → **Prohibido por Charter §9**

---

## 5. INVARIANTES Y REGLAS DE GOBERNANZA

### 5.1 Invariantes constitucionales
Las siguientes invariantes declaran **qué debe ser verdadero** en Fase 18. Los mecanismos concretos quedan abiertos a los Decision Candidates correspondientes.

* **INV-SCI-1:** Misma baseline sellada + mismos parámetros científicos congelados ⇒ misma salida científica y evidencia científica canónica, independiente de schedule, concurrencia, budgets y cache.
* **INV-OPS-1:** Las diferencias operacionales no alteran el resultado científico ni falsifican la evidencia científica; viven en evidencia operacional separada.
* **INV-ASSEMBLY-ORDER:** Ejecuciones concurrentes con permutaciones forzadas del orden de completitud producen identidad de artefacto idéntica bajo parámetros científicos congelados; el ensamblado mergea por identidad/lineage.
* **INV-CACHE:** Un hit de cache devuelve exactamente el valor almacenado bajo su clave de identidad; la clave es identidad framed; no se atribuye al cache garantía que el proveedor no ofrece (DC-03).
* **INV-JOURNAL:** Ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash y una aplicación idempotente del resultado. El mecanismo concreto de persistencia y coordinación permanece abierto a DC-08. La propiedad obligatoria es: idempotent apply y ventana de duplicación acotada y medida.
* **INV-UNITS:** Documento = aislamiento/recuperación; chunk = scheduling/retry; batch-call = costo FinOps; execution = identidad/evidencia.
* **INV-EXEC-IDENTIFIABILITY:** El modo/política de ejecución es identificable y reproducible y habilita testing diferencial; excluido de la identity científica (DC-02); sin nombres de modo congelados.
* **INV-NO-RESOURCE-SIGNAL:** Agotamiento de budget ⇒ EXECUTION_FAILURE (exit 4) con evidencia persistida; nunca REGRESSION/PASS; shed/cancel/hold con razón indexable propia.
* **INV-VERIFICATION-ISOLATION:** El verification subject corre sin scheduler ni concurrencia por defecto; concurrencia opt-in gobernada sujeta a INV-SCI-1.

### 5.2 Reglas de gobernanza del proceso
* **Audit First, Design Later:** toda decisión de implementación se basa en evidencia forense de Fase 0.
* **Reuse Before Invent:** toda sustitución de autoridad existente exige evidencia de insuficiencia.
* **No New Authority Without Boundary:** toda autoridad nueva propuesta declara frontera contra autoridades existentes.
* **Benchmark Before Optimization:** ninguna técnica candidata se implementa sin evidencia empírica de beneficio.
* **Evidence-driven technique selection:** las técnicas candidatas sobreviven o caen según evidencia del baseline y criterio preregistrado en FASE0_AUDIT_CHARTER.md §9.

---

## 6. HOJA DE RUTA DE SUB-FASES GOBERNADAS

Fase 18 se estructura en **5 sub-fases gobernadas**. Cada sub-fase representa una capacidad arquitectónica diferenciada con frontera conceptual clara, conjunto coherente de DCs, invariantes principalmente propias y dependencias identificables.

```text
                         FASE 18
              ADVANCED LOCAL EXECUTION PLANE
                              │
                              ▼
              ┌─────────────────────────────┐
              │ 18.1 Execution Plane &      │
              │ Concurrency                 │
              │ DC-01 / DC-02 / DC-05       │
              └──────────────┬──────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
       ┌──────────────────┐ ┌──────────────────┐
       │ 18.2 Durable     │ │ 18.3 Resource    │
       │ Execution &      │ │ Governance &     │
       │ Recovery         │ │ Adaptive         │
       │ DC-08            │ │ Scheduling       │
       │                  │ │ DC-07 / DC-10    │
       └────────┬─────────┘ └────────┬─────────┘
                │                    │
                │    ┌───────────────┘
                │    │
                ▼    ▼
       ┌──────────────────────────────┐
       │ 18.4 Provider & Cache        │
       │ Runtime Semantics            │
       │ DC-03 / DC-04                │
       └──────────────┬───────────────┘
                      │
                      ▼
       ┌──────────────────────────────┐
       │ 18.5 Runtime Verification    │
       │ & Promotion                  │
       │ DC-12                        │
       └──────────────────────────────┘
```

**Cláusula de dependencias de gobernanza:** The sub-phase graph expresses governance dependencies, not an exhaustive execution schedule. Individual decision candidates may proceed when their explicit prerequisites are satisfied; no sub-phase is required to await unrelated completion of another sub-phase.

### 6.1 a 6.5 Resumen de Sub-fases
* **18.1 Execution Plane & Concurrency:** Modelo de ejecución, identity boundary, bounded execution, cancellation. (DC-01, DC-02, DC-05, DF-06).
* **18.2 Durable Execution & Recovery:** Journal semantics, recovery, fencing, zombie handling, idempotency, durable authorities. (DC-08, DF-24, DF-34). Incluye validación empírica local de recovery.
* **18.3 Resource Governance & Adaptive Scheduling:** Admission, backpressure, resource budgets, batching, marco de evaluación de técnicas candidatas. (DC-07, DC-10, DC-11).
* **18.4 Provider & Cache Runtime Semantics:** Provider characterization, cache scope/identity/correctness, cache persistence. (DC-03, DC-04).
* **18.5 Runtime Verification & Promotion:** Extensión de Continuous Verification de F17-BIS, differential guard M1→M2→M3, reproducibilidad bajo variación operacional. (DC-12).

### 6.6 Capacidades transversales (no sub-fases)
| Capacidad | Ámbito principal | Sub-fases relacionadas |
|---|---|---|
| C8 Scientific Neutrality | 18.5 (demostración integrada) | 18.1, 18.2, 18.3, 18.4 (constricción) |
| C9 Scientific Determinism | 18.5 (demostración integrada) | 18.1, 18.2, 18.3, 18.4 (constricción) |
| C11 Operational Visibility | 18.1 (ámbito principal, aplicación transversal) | Transversal, mínimo contractual en todas |
| C12 Outcome-Taxonomy Integrity | 18.5 (promoción) | 18.1, 18.2, 18.3 (constricción) |
| C13 Verification-Path Determinism | 18.5 (demostración) | 18.1 (constricción) |

### 6.7 Cláusula de Relación con el Execution Plan (obligatoria)
The architectural sub-phases defined in this ADR specify the required architectural capabilities and their governance dependencies. The operational sequencing, deployment strategy, technical dependencies, implementation logistics, waves, tasks, owners and dates are governed independently by the future `PHASE_18_EXECUTION_PLAN.md`.

---

## 7. ESPECIFICACIÓN DE LA COMPUERTA DE AUDITORÍA (FASE 0)

**Historical Note:** This section is preserved for traceability purposes. Phase 0 has been completed and its results are materialized in the 12 HITOs FROZEN in `00-foundation/`.

### 7.1 Regla de blindaje
* **NO CODE:** no se modificó código de producción ni se introdujeron abstracciones.
* **NO MUTACIÓN de estado normativo:** no se modificó estado productivo, artefactos sellados, oráculos, ni ninguna autoridad de gobernanza.
* **Medición externa:** `tracemalloc`, `resource`, SQLite statistics, provider logs, subprocess wrappers, timing externo, observación de filesystem. Sin instrumentación interna nueva.

### 7.2 Entradas y Actividades
Código fuente actual (`apps/`, `core/`, `infra/`, `runtime/`, `tools/evaluation/`, `tests/`), fuentes normativas (ROADMAP, ADR_F17_BIS_MASTER, ENGINEERING_PRINCIPLES, FASE0_AUDIT_CHARTER), y estado basal (FASE_6_HANDOFF). Se ejecutaron las auditorías F0-B, F0-G, F0-F, F0-E, F0-A Protocol, Reconciliation, F0-A Baseline, F0-C, y F0-D.

### 7.3 Entregables obligatorios (completados)
* ✅ Architecture Gap Matrix (HITO_0.10 v1.0.1)
* ✅ Current State & Contract Map (HITO_0.11 v1.0.1)
* ✅ Evidence Register & DC Resolutions (HITO_0.12 v1.0.1)
* ✅ ADR_F18_MASTER PROPOSED — artefacto arquitectónico derivado de los tres outputs consolidados de Fase 0; no constituye evidencia forense.

---

## 8. REGISTRO DE DECISIONES CANDIDATAS (DC LOG)

El siguiente registro se conserva como registro histórico. Todos los DCs tienen estado de gobernanza válido según Charter §7.

### 8.1 DC-06a — ¿Qué significa el hito de F18?
**Estado:** GOVERNANCE-RESOLVED. **Resolución:** Opción A — pivot normativo documentado en §1 de este ADR. El hito no significa "producto completo" mientras existan F19-F21. **Evidencia:** FASE0_AUDIT_CHARTER.md §2, aprobación registrada en PR #5.

### 8.2 DCs DEFERRED

**DC-01 — Fork de concurrencia**
* **Estado:** DEFERRED | **Destino:** 18.1 | **Dependencias:** Ninguna
* **Prerrequisito:** Disponibilidad de métricas por etapa y medición de impacto de SyncProviderBridge.
* **Trigger:** Evidencia cuantitativa de GAP-0.5-02 y GAP-0.1-01 disponible para evaluación.
* **Criterio de cierre:** Decisión documentada: async single-process + executors vs multi-process, con evidencia de impacto en C1/C3/C6/C10.
* **Evidencia:** HITO_0.12 / DC-01.

**DC-02 — Parámetros de runtime en identity científica vs metadata operacional**
* **Estado:** DEFERRED | **Destino:** 18.1 | **Dependencias:** Ninguna
* **Trigger:** Se resuelva fórmula de identidad de workload (GAP-0.3-03).
* **Criterio de cierre:** Definición congelada de qué parámetros pertenecen a scientific identity y cuáles a operational metadata; fórmula de identidad de workload.
* **Evidencia:** HITO_0.12 / DC-02.

**DC-03 — Determinismo observable por proveedor**
* **Estado:** DEFERRED | **Destino:** 18.4 | **Dependencias:** Ninguna
* **Prerrequisito:** Credenciales de proveedores activas.
* **Trigger:** Disponibilidad de evidencia de determinismo observable e integración de telemetría en entry point de medición (GAP-0.5-02).
* **Criterio de cierre:** Protocolo de caracterización ejecutado; nivel de determinismo observable documentado por proveedor; distinción entre comportamiento observado y garantía contractual.
* **Evidencia:** HITO_0.12 / DC-03.

**DC-04 — Alcance de caches**
* **Estado:** DEFERRED | **Destino:** 18.4 | **Dependencias:** Parcial con DC-03 (DC-04 puede resolver el contrato de identidad y corrección del cache independientemente; la admisibilidad de cachear resultados dependientes del proveedor queda condicionada a DC-03).
* **Trigger:** Disponibilidad de definición de identidad de cache y evaluación de garantías del proveedor.
* **Criterio de cierre:** Decisión documentada: pure-function / LLM / semantic+embedding; checklist de completitud de clave. Semantic/embedding → F21.
* **Evidencia:** HITO_0.12 / DC-04.

**DC-05 — ¿Unificar ExecutionContext o contextos especializados?**
* **Estado:** DEFERRED | **Destino:** 18.1 | **Dependencias:** DC-01
* **Trigger:** Disponibilidad de evidencia sobre el impacto de unificación vs especialización post DC-01.
* **Criterio de cierre:** Test de god-object: qué boundary protege cada contexto; decisión documentada.
* **Evidencia:** HITO_0.12 / DC-05 (GOVERNANCE-DEFERRED).

**DC-06b — ¿Las técnicas prescritas del ROADMAP sobreviven?**
* **Estado:** DEFERRED | **Destino:** 18.1-18.4 (evaluación post-baseline) | **Dependencias:** DC-01
* **Trigger:** Disponibilidad de baseline F0-A completo con métricas por etapa (GAP-0.5-02) y medición de impacto de barreras síncronas (GAP-0.1-01).
* **Criterio de cierre:** Evidencia de Fase 0 vs criterio preregistrado; decisión de Board o enmienda ROADMAP v3.1.
* **Evidencia:** HITO_0.12 / DC-06b.

**DC-07 — ¿Tiers 8k/32k/1M o batch = f(budgets)?**
* **Estado:** DEFERRED | **Destino:** 18.3 | **Dependencias:** DC-03
* **Trigger:** Disponibilidad de caracterización suficiente de tokens/call, límites del proveedor y workload stress para comparar tiers discretos frente a presupuesto continuo.
* **Criterio de cierre:** Decisión documentada: tiers discretos, budgets continuos o combinación; valores concretos sujetos a caracterización empírica.
* **Evidencia:** HITO_0.12 / DC-07.

**DC-08 — Write-policy SQLite + mecanismo de journal de INV-JOURNAL**
* **Estado:** DEFERRED | **Destino:** 18.2 | **Dependencias:** DC-01
* **Trigger:** Se resuelva DC-01 (fork de concurrencia).
* **Criterio de cierre:** Decisión documentada: write-policy SQLite + mecanismo que garantice idempotent apply y ventana de duplicación acotada y medida; persistencia de autoridades in-memory resuelta.
* **Evidencia:** HITO_0.12 / DC-08.

**DC-09 — Semántica de producto de interrupción**
* **Estado:** DEFERRED | **Destino:** F19 | **Dependencias:** DC-01, DC-08
* **Trigger:** Se complete Fase 18 (runtime local maduro) Y se evalúe tolerancia existente del assembler.
* **Criterio de cierre:** Decisión documentada: documento degradado coherente con warnings; tolerancia del assembler como evidencia.
* **Evidencia:** HITO_0.12 / DC-09 (GOVERNANCE-DEFERRED).

**DC-10 — Fairness y admission deadlock-free**
* **Estado:** DEFERRED | **Destino:** 18.3 | **Dependencias:** DC-01
* **Trigger:** Se caracterice workload de estrés (GAP-0.3-02) Y se resuelva DC-01.
* **Criterio de cierre:** Decisión documentada: admitir conjuntos dependency-ready o diferir sin retener recursos.
* **Evidencia:** HITO_0.12 / DC-10.

**DC-11 — Semántica de admisión-diferida sin nuevo estado FSM**
* **Estado:** DEFERRED | **Destino:** 18.3 | **Dependencias:** DC-01
* **Trigger:** Se complete auditoría de propagación de señales operacionales al FSM (GAP-0.4-02).
* **Criterio de cierre:** Decisión documentada: razón indexable + admission record antes que estado nuevo; auditoría de FSM existente completada.
* **Evidencia:** HITO_0.12 / DC-11.

**DC-12 — Contrato y promoción del guard diferencial**
* **Estado:** DEFERRED | **Destino:** 18.5 | **Dependencias:** DC-02
* **Trigger:** Se resuelva DC-02 (contrato de identity científica).
* **Criterio de cierre:** Contrato de comparación definido (M0); experimento implementado (M1); estabilidad demostrada (M2); required check en branch protection (M3).
* **Evidencia:** HITO_0.12 / DC-12.

### 8.3 Deferred Findings
* **DF-06 (Imports cruzados core→apps):** Destino 18.1. Trigger: Se inicie refactor de composición.
* **DF-24 (Persistencia de Circuit Breaker):** Destino 18.2 (subsumido en DC-08). Trigger: Se resuelva DC-01 Y DC-08.
* **DF-34 (Persistencia de ProfileStore):** Destino 18.2. Trigger: Se resuelva DC-01 Y se cuantifique coste agregado de re-inferencia.

---

## 9. ARCHITECTURE GOVERNANCE FRAMEWORK

### 9.1 Cadena normativa interna de Fase 18
```text
ADR_F18_MASTER (este documento)
      ↓
ADR de sub-fase (18.1, 18.2, 18.3, 18.4, 18.5)
      ↓
NADRs (reglas RFC-2119 verificables)
      ↓
PHASE_18_EXECUTION_PLAN (secuencia operativa, waves, owners, fechas)
      ↓
Registers / implementation / validation
```

### 9.2 Cláusula de jerarquía normativa
No lower governance level is authorized to redefine or contradict decisions established by an upper level. The normative hierarchy of the project is governed by methodology general §2. This ADR incorporates that hierarchy by reference.

### 9.3 Rol de los HITOs de Fase 0
Los HITOs de `00-foundation/` son **evidencia de entrada** que alimenta este ADR Maestro, no un nivel normativo de la cadena. Su función es proporcionar la base forense para las decisiones arquitectónicas.

### 9.4 Relación con Continuous Verification de F17-BIS
F17-BIS ya estableció el mecanismo de Continuous Verification. DC-12 (differential guard) es una **extensión gobernada** de esa infraestructura existente, no un reemplazo. El principio **Reuse Before Invent** aplica: F18 extiende la CV existente con verificación diferencial bajo variación operacional.

---

## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES

### 10.1 Nivel A — DoD de gobernanza (congelamiento del ADR)
Este ADR Maestro pasa de estado PROPOSED a FROZEN cuando se cumplan:
- [ ] Header completo, incluido `Aprobación Architecture Board` con fecha.
- [ ] Las 10 secciones presentes, sin adicionales ni omisiones.
- [ ] §1 deriva de objetivos ROADMAP de Fase 18 (traducción a capacidades).
- [ ] §2 cita IDs de evidencia forense existentes en `00-foundation/`.
- [ ] §2.1 documenta el outcome de la compuerta de auditoría.
- [ ] §3 declara dimensiones ortogonales y sus no-implicaciones.
- [ ] §4 declara no-objetivos con fase propietaria explícita para cada ítem.
- [ ] §5 sin nombres de clases/tecnologías y sin reglas RFC-2119.
- [ ] §6 sin waves/tasks/owners/fechas; incluye la Cláusula de Relación con el Execution Plan.
- [ ] §7 conserva regla de blindaje y registro histórico de Fase 0.
- [ ] §8 sin DCs abiertos (todos RESOLVED o DEFERRED+DESTINATION+TRIGGER+DEPENDENCIES+ACCEPTANCE CRITERION).
- [ ] §9 declara solo la cadena normativa interna de la fase y referencia metodología general §2.
- [ ] §10 define Nivel A y Nivel B verificables, sin DoD por tarea.

### 10.2 Nivel B — DoD global de Fase 18 (cierre de la fase)
La Fase 18 se considerará oficialmente finalizada cuando se cumplan:
1. **Pipeline alineado:** SyncProviderBridge eliminado o justificado con evidencia; INV-JOURNAL satisfecho o ventana de duplicación acotada y medida.
2. **Concurrencia madura:** Modelo de concurrencia decidido (DC-01) e implementado; backpressure funcional; cancelación limpia.
3. **Durabilidad verificada:** Todos los activos críticos con persistencia validada; tests de epoch fencing y zombie recovery pasando.
4. **Resource efficiency:** Técnicas candidatas (object pools, zero-copy, lazy loading, batching) evaluadas conforme al criterio preregistrado; únicamente las técnicas cuya adopción haya sido decidida mediante evidencia forman parte del runtime final.
5. **Cache operativo:** Cache scope resuelto conforme a DC-04; los mecanismos aprobados, si corresponde, implementados y validados contra su contrato de identidad y exactitud.
6. **Lifecycle gobernado:** La semántica de coordinated shutdown queda satisfecha y validada, cuando resulte necesaria según la arquitectura de ejecución adoptada; telemetry loss bajo umbral definido.
7. **Guard diferencial activo:** M3 completado; required check en branch protection para todo PR que toque runtime.
8. **CI gates activos:** Continuous Verification ejecutándose contra el corpus canónico con todos los perfiles, extendiendo la infraestructura de F17-BIS.
9. **Verificación estática limpia:** 0 errors, 0 warnings en analizadores estáticos; suite de pruebas en verde.
10. **Baseline operacional actualizada:** Nuevo baseline de wall/CPU/RSS post-F18 comparado contra baseline de Fase 0 (HITO_0.7 v1.1.0).
11. **Waste ratio cuantificado:** Baseline de waste ratio con provider real (extensión de HITO_0.9 v1.4.0).
12. **No regresión científica:** INV-SCI-1, INV-OPS-1, INV-ASSEMBLY-ORDER, INV-NO-RESOURCE-SIGNAL se mantienen verdaderas bajo todas las condiciones operativas.

---

**Nota de Gobernanza:** Este documento es la constitución arquitectónica de Fase 18. No define reglas normativas RFC-2119 (eso corresponde a NADRs posteriores). No define secuencia operativa (eso corresponde al Execution Plan). No constituye evidencia forense (eso son los HITOs de `00-foundation/`). Toda afirmación conceptual nueva a partir de este punto entra como DC o finding con evidencia, no como análisis textual.