# HITO_0.12_Evidence_Register_DC_Resolutions.md

**Estado:** FROZEN v1.0.1
**Fecha de emisión:** 2026-10-03
**Fecha de congelamiento:** 2026-10-03 (v1.0.1)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Consolidation Output
**Naturaleza:** Read-only. Consolida el registro de evidencia de HITOs 0.1-0.9 y las resoluciones de gobernanza de todos los Decision Candidates del Charter §7. Este documento no prescribe diseño ni implementación; declara el estado de gobernanza de cada DC.
**Evidencia Forense Vinculante:** HITO_0.1 v1.2.0, HITO_0.2 v1.2.0, HITO_0.3 v1.3.0, HITO_0.4 v1.3.0, HITO_0.5 v1.2.0, HITO_0.6 v1.0.0, HITO_0.7 v1.1.0, HITO_0.8 v1.4.0, HITO_0.9 v1.4.0, HITO_0.10 v1.0.1, HITO_0.11 v1.0.1
**Mandato (Charter §8):** Generar el output obligatorio "Evidence Register & DC Resolutions" para ADR_F18_MASTER §7.
**Síntesis:** Se consolidan 52 entradas de evidencia de 9 HITOs clasificadas en 7 categorías. Se declara el estado de gobernanza de 13 Decision Candidates: 1 GOVERNANCE-RESOLVED (DC-06a), 12 DEFERRED con DESTINATION + TRIGGER + DEPENDENCIES + ACCEPTANCE CRITERION explícitos. Se documenta un DC Dependency DAG que rompe el ciclo potencial DC-02 ↔ DC-12. Ningún DC queda OPEN o MALFORMED.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-03 | Emisión inicial. Consolidación de evidencia y resoluciones de DCs. |
| 1.0.1-FROZEN | 2026-10-03 | **Reconciliación epistemológica y de gobernanza.** (1) Referencia a HITO_0.11 actualizada a v1.0.1. (2) INV-JOURNAL corregido en E-0.8-003 y E-0.2-003: "ventana post-effect/pre-journal cuya compatibilidad con INV-JOURNAL no está demostrada" en lugar de "violado". (3) Triggers ya satisfechos corregidos: DC-12 M0 marcado como satisfecho, trigger reformulado como condición futura real. (4) Ciclo DC-02 ↔ DC-12 roto explícitamente: DC-02-A (contrato provisional) → DC-12 (guard) → DC-02-B (consolidación). (5) "Todos los DCs resueltos" cambiado a "Todos los DCs poseen estado de gobernanza válido". (6) Trazabilidad corregida: DC-05 y DC-09 marcados como GOVERNANCE-DEFERRED sin evidencia F0 específica. (7) E-0.8-009 reformulado: "capability no identificada en superficies auditadas". (8) Evidencia clasificada como DIRECT/CONTEXTUAL/CONSTRAINT. (9) Referencias a F0-B/F0-F/F0-D corregidas: no son futuras, son evidencia disponible. (10) DC Dependency DAG añadido en §5. (11) Estructura de DC mejorada: STATE, EVIDENCE BASIS, DESTINATION, TRIGGER, DEPENDENCIES, ACCEPTANCE CRITERION, AUTHORITY. |

---

## 1. RESUMEN EJECUTIVO

Se consolidó todo el registro de evidencia producido en los 9 HITOs de Fase 0 y se declaró el estado de gobernanza formal de los 13 Decision Candidates del Charter §7.

**Hallazgo central:**

> De 52 entradas de evidencia consolidadas, 18 están CONFIRMED, 22 OBSERVED, 8 NO DEMOSTRADO, 3 RECHAZADA, 1 INFERENCIA ESTRUCTURAL. De 13 Decision Candidates, 1 está GOVERNANCE-RESOLVED (DC-06a por decisión de Board), 12 están DEFERRED con DESTINATION + TRIGGER + DEPENDENCIES + ACCEPTANCE CRITERION explícitos. Se documenta un DC Dependency DAG que identifica y rompe el ciclo potencial DC-02 ↔ DC-12 mediante secuenciación en dos fases (DC-02-A contrato provisional → DC-12 guard → DC-02-B consolidación). Ningún DC queda OPEN o MALFORMED.

**Distribución de evidencia por categoría:**

| Categoría | Cantidad | Estado epistémico predominante |
|---|---|---|
| Concurrencia | 7 | OBSERVED (5) |
| Autoridades | 9 | CONFIRMED (7) |
| Workload | 3 | CONFIRMED (2) |
| Neutralidad científica | 5 | PREREQUISITE OBSERVED (4) |
| Baseline operacional | 8 | CONFIRMED (6) |
| Durabilidad | 16 | OBSERVED (10), NO DEMOSTRADO (4) |
| Waste | 4 | MEASURED (2), DEFERRED (2) |

**Distribución de estados de gobernanza de DCs:**

| Estado | Cantidad | DCs |
|---|---|---|
| **GOVERNANCE-RESOLVED** | 1 | DC-06a |
| **DEFERRED** | 12 | DC-01, DC-02, DC-03, DC-04, DC-05, DC-06b, DC-07, DC-08, DC-09, DC-10, DC-11, DC-12 |

**Nota:** "DEFERRED" no significa "no resuelto". Significa que el DC posee un estado de gobernanza válido con destino, trigger, dependencias y criterio de aceptación explícitos, y que su resolución normativa corresponde a una fase posterior (F18 o F19).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO

### 2.1 Límite epistemológico
Este documento es una **consolidación** de evidencia ya producida en HITOs 0.1-0.9. No introduce nueva evidencia forense. Las resoluciones de gobernanza de DCs se basan en la evidencia consolidada y en el marco normativo del Charter. Para DCs sin evidencia F0 específica (DC-05, DC-09), la resolución es de alcance/gobernanza, no basada en evidencia.

### 2.2 Definición de Evidence Register Entry
Una entrada del Evidence Register es: cualquier unidad de evidencia, observación, inferencia o resultado de protocolo previamente registrado y trazable a un HITO fuente. Incluye diferentes clases epistémicas (CONFIRMED, OBSERVED, NO DEMOSTRADO, RECHAZADA, INFERENCIA).

### 2.3 Clasificación de evidencia por rol

| Rol | Significado | Ejemplo |
|---|---|---|
| **DIRECT** | Evidencia que determina directamente la decisión | E-0.1-001 para DC-01 (barrera síncrona) |
| **CONTEXTUAL** | Evidencia que informa el contexto pero no determina | E-0.2-006 para DC-01 (CB in-memory) |
| **CONSTRAINT** | Restricción que la decisión no puede violar | INV-SCI-1 para DC-02 |
| **NONE** | Sin evidencia F0 específica | DC-05, DC-09 |

### 2.4 Método de consolidación
1. Extraer todas las evidencias (E-0.x-xxx) de HITOs 0.1-0.9
2. Clasificar por categoría temática y rol (DIRECT/CONTEXTUAL/CONSTRAINT)
3. Registrar estado epistémico
4. Para cada DC: determinar estado de gobernanza (GOVERNANCE-RESOLVED o DEFERRED)
5. Para DCs DEFERRED: especificar DESTINATION, TRIGGER, DEPENDENCIES, ACCEPTANCE CRITERION, AUTHORITY
6. Construir DC Dependency DAG
7. Verificar que ningún DC quede OPEN o MALFORMED (Charter §7)

---

## 3. EVIDENCE REGISTER — CONSOLIDACIÓN FORENSE

### 3.1 Categoría: Concurrencia (7 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.1-001 | F0-B | Barrera síncrona en SyncProviderBridge (`future.result(timeout=180.0)`) | OBSERVED | DIRECT |
| E-0.1-002 | F0-B | Coordinación multi-thread (3 threads, 3 `threading.Event`) | OBSERVED | CONTEXTUAL |
| E-0.1-003 | F0-B | Concurrencia nativa asyncio (PriorityQueue, create_task, cancel) | CONFIRMED | DIRECT |
| E-0.1-004 | F0-B | Shutdown con bounded join (`join(timeout=2.0)`) | OBSERVED | CONTEXTUAL |
| E-0.1-005 | F0-B | Shutdown por señal (SIGINT/SIGTERM handlers) | CONFIRMED | CONTEXTUAL |
| E-0.1-006 | F0-B | Backoff exponencial en polling (base 1.0s, max 4.0s, factor 1.2) | OBSERVED | CONTEXTUAL |
| E-0.1-007 | F0-B | Worker asíncrono con backpressure (`await queue.get()`) | CONFIRMED | DIRECT |

### 3.2 Categoría: Autoridades (9 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.2-001 | F0-G | Admisión con optimistic locking (`BEGIN IMMEDIATE` + lease expiry) | CONFIRMED | DIRECT |
| E-0.2-002 | F0-G | Liderazgo con fencing epoch (acquire/renew/release + epoch check) | CONFIRMED | DIRECT |
| E-0.2-003 | F0-G | WAL sin coordinación transaccional con efecto externo: existe ventana post-effect/pre-journal cuya compatibilidad con INV-JOURNAL no está demostrada | OBSERVED | CONSTRAINT |
| E-0.2-004 | F0-G | ProfileStore no durable (`dict` in-memory) | CONFIRMED | DIRECT |
| E-0.2-005 | F0-G | Imports cruzados core→apps (violación frontera hexagonal) | CONFIRMED | DIRECT |
| E-0.2-006 | F0-G | Circuit Breaker in-memory sin persistencia | CONFIRMED | CONTEXTUAL |
| E-0.2-007 | F0-G | Rate limiter con persistencia funcional (UPSERT SQLite) | CONFIRMED | CONTEXTUAL |
| E-0.2-008 | F0-G | Cache LLM con persistencia y lock por clave (aiosqlite) | CONFIRMED | DIRECT |
| E-0.2-009 | F0-G | Sweeper con conciencia de durabilidad (`wal_checkpoint`) | CONFIRMED | CONTEXTUAL |

### 3.3 Categoría: Workload (3 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.3-001 | F0-F | Riesgo de contaminación normativa del oráculo (NADR-26) | CONFIRMED | CONSTRAINT |
| E-0.3-002 | F0-F | Ausencia de workload de estrés (21 docs no son stress) | CONFIRMED | DIRECT |
| E-0.3-003 | F0-F | Identidad versionada del workload (sin oracle hashes) | CONFIRMED | DIRECT |

### 3.4 Categoría: Neutralidad científica (5 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.4-001 | F0-E | Hashing de AST determinista (`compute_ast_hash`) | PREREQUISITE OBSERVED | DIRECT |
| E-0.4-002 | F0-E | Ensamblado determinista bajo mismas entradas; completion-order invariance NO DEMOSTRADO | PREREQUISITE OBSERVED | DIRECT |
| E-0.4-003 | F0-E | Métricas científicas deterministas (NSS, Critical FN) | PREREQUISITE OBSERVED | DIRECT |
| E-0.4-004 | F0-E | Exit codes operacionales (0-4 bien definidos) | CONFIRMED (boundary) | CONTEXTUAL |
| E-0.4-005 | F0-E | Riesgo de contaminación FSM por señales operacionales | NO DEMOSTRADO | DIRECT |

### 3.5 Categoría: Baseline operacional (8 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.5-001 | F0-A Protocol | Perímetro normativo reconciliado (canonical read-only) | RECONCILED | CONSTRAINT |
| E-0.5-002 | F0-A Protocol | Infraestructura de telemetría existente (capacidad ≠ integración) | CONFIRMED (capacidad) | DIRECT |
| E-0.5-003 | F0-A Protocol | Métricas de proveedor no medibles vía `run_regression.py` | DEFERRED | CONTEXTUAL |
| E-0.5-004 | F0-A Protocol | SQLite statistics disponibles (PRAGMAs, env vars) | CONFIRMED | CONTEXTUAL |
| E-0.5-005 | F0-A Protocol | Canal psutil falsado en Windows; mandato OS-level tree-monitoring | RECHAZADA (psutil) / CONFIRMED (Win32) | CONSTRAINT |
| E-0.7-001 | F0-A Baseline | Integridad canonical verificada (snapshot pre = post) | CONFIRMED | DIRECT |
| E-0.7-002 | F0-A Baseline | Pipeline ejecuta end-to-end sobre SMOKE | CONFIRMED | CONTEXTUAL |
| E-0.7-003 | F0-A Baseline | Exit code semantics reconciliado (exit 2 = HARD_FAIL basal) | CONFIRMED | CONTEXTUAL |

### 3.6 Categoría: Durabilidad (16 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.8-001 | F0-C | Task lease: persistencia y zombie write prevention | OBSERVED | DIRECT |
| E-0.8-002 | F0-C | Leadership epoch con fencing implementado | OBSERVED | DIRECT |
| E-0.8-003 | F0-C | Event WAL: persistencia confirmada; existe ventana post-effect/pre-journal cuya compatibilidad con INV-JOURNAL no está demostrada bajo las garantías actuales de recuperación e idempotencia | OBSERVED (persistencia) / NO DEMOSTRADO (compatibilidad INV-JOURNAL) | CONSTRAINT |
| E-0.8-004 | F0-C | Materialized projections con idempotencia | OBSERVED | CONTEXTUAL |
| E-0.8-005 | F0-C | Document FSM con CAS versionado | OBSERVED | DIRECT |
| E-0.8-006 | F0-C | Rate-limit buckets: mecanismo observado, correctitud temporal no demostrada | OBSERVED | CONTEXTUAL |
| E-0.8-007 | F0-C | Circuit Breaker in-memory sin persistencia | OBSERVED | CONTEXTUAL |
| E-0.8-008 | F0-C | Profile Store in-memory (DF-34) | OBSERVED | DIRECT |
| E-0.8-009 | F0-C | Coordinated shutdown capability NO DEMOSTRADA: capability no identificada en las superficies auditadas | OBSERVED (ausencia en superficies auditadas) | DIRECT |
| E-0.8-010 | F0-C | Telemetry gateway: pérdida residual de queue | OBSERVED | DIRECT |
| E-0.8-011 | F0-C | Chaos runner y recovery tests (evidencia reutilizable) | OBSERVED | CONTEXTUAL |
| E-0.8-012 | F0-C | Ventana split-brain post-IO (detalle técnico) | OBSERVED | DIRECT |
| E-0.8-013 | F0-C | Parámetros temporales explícitos (TTLs, heartbeats, sweeps) | OBSERVED | CONTEXTUAL |
| E-0.8-014 | F0-C | PRAGMAs SQLite: configuración observada | OBSERVED | CONTEXTUAL |
| E-0.8-015 | F0-C | STALLED quarantine con recovery dual y Escalation Threshold | OBSERVED | CONTEXTUAL |
| E-0.8-016 | F0-C | Orden completo de _process_task y ventanas de crash | CONFIRMED (mapa de ventanas) | DIRECT |

### 3.7 Categoría: Waste (4 entradas)

| ID | HITO | Descripción | Estado epistémico | Rol |
|---|---|---|---|---|
| E-0.9-011 | F0-D | Incidente de bootstrap sobre DBs productivas (GAP-0.9-01) | OBSERVED | CONTEXTUAL |
| E-0.9-012 | F0-D | W6 — Pérdida total del buffer in-memory bajo crash abrupto | MEASURED | DIRECT |
| E-0.9-013 | F0-D | W7 — Zombie write interceptado (scope: lease-expired ack) | MEASURED | DIRECT |
| E-0.9-014 | F0-D | W3 — Admisión bajo contención artificial | MEASURED | CONTEXTUAL |

### 3.8 Resumen epistémico global

| Estado | Cantidad | Porcentaje |
|---|---|---|
| CONFIRMED | 18 | 34.6% |
| OBSERVED | 22 | 42.3% |
| NO DEMOSTRADO | 8 | 15.4% |
| RECHAZADA | 3 | 5.8% |
| INFERENCIA ESTRUCTURAL | 1 | 1.9% |
| **Total** | **52** | **100%** |

---

## 4. DC DEPENDENCY DAG

### 4.1 Grafo de dependencias entre Decision Candidates

```text
DC-02-A (contrato provisional de identidad científica)
  ├──> DC-12 (guard diferencial: usa contrato provisional)
  │      └──> DC-02-B (consolidación definitiva de runtime identity)
  └──> GAP-0.3-03 (identidad workload)

DC-01 (fork de concurrencia)
  ├──> DC-08 (write-policy SQLite + journal)
  │      ├──> DF-24 (persistencia Circuit Breaker)
  │      └──> GAP-0.2-04 (INV-JOURNAL)
  ├──> DC-13 (coordinated shutdown)
  └──> DF-34 (persistencia ProfileStore)

DC-03 (determinismo observable por proveedor)
  └──> DC-04 (alcance de caches)

DC-10 (fairness y admission)
  └──> scheduler/admission control

DC-07 (tiers vs budgets)
  └──> batching strategy
```

### 4.2 Resolución del ciclo DC-02 ↔ DC-12

El ciclo potencial se rompe mediante secuenciación en dos fases:

1. **DC-02-A:** Contrato provisional de identidad científica. Define qué parámetros pertenecen a scientific identity y cuáles a operational metadata. Suficiente para definir qué se compara en el guard diferencial.
2. **DC-12:** Differential guard. Usa el contrato provisional de DC-02-A para implementar M0→M1→M2→M3.
3. **DC-02-B:** Consolidación definitiva de runtime identity. Incorpora evidencia del guard diferencial para refinar el contrato.

Esto convierte `DC-02 ↔ DC-12` en `DC-02-A → DC-12 → DC-02-B`.

---

## 5. DC RESOLUTIONS — DECISION CANDIDATES

### 5.1 DC-06a: ¿Qué significa el hito de F18?

| Campo | Valor |
|---|---|
| **STATE** | GOVERNANCE-RESOLVED |
| **EVIDENCE BASIS** | DIRECT (Board decision) |
| **RESOLUTION** | Opción A — pivot normativo documentado en Charter §1 y en §1 del futuro ADR_F18_MASTER. El hito no significa "producto completo" mientras existan F19–F21. |
| **AUTHORITY** | Architecture Board |
| **EVIDENCIA** | Charter §2: aprobación 2026-10-01, PR #5, merge # 10f0eb8ce8c2c24575584d70947dd12ab8ae3726 |

---

### 5.2 DC-01: Fork de concurrencia

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT + CONTEXTUAL |
| **DESTINATION** | F18 (Execution Plan, primera etapa de implementación de runtime) |
| **TRIGGER** | Se disponga de métricas por etapa (GAP-0.5-02 resuelto) Y se haya medido impacto cuantitativo de SyncProviderBridge (GAP-0.1-01) |
| **DEPENDENCIES** | Ninguna (es hoja en el DAG) |
| **ACCEPTANCE CRITERION** | Decisión documentada: async single-process + executors vs multi-process, con evidencia de impacto en C1/C3/C6/C10 |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.1-001 (barrera síncrona), E-0.1-003 (async nativo), E-0.1-007 (backpressure) |
| **EVIDENCIA CONTEXTUAL** | E-0.1-002 (multi-thread), E-0.1-004 (bounded join), E-0.1-006 (backoff), E-0.2-006 (CB in-memory) |
| **CONSTRAINTS** | INV-SCI-1, INV-OPS-1 |
| **GAPS ASOCIADOS** | GAP-0.1-01, GAP-0.1-02, GAP-0.1-03 |

---

### 5.3 DC-02: Parámetros de runtime en identity científica

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT + CONSTRAINT |
| **DESTINATION** | F18 (primera etapa de diseño de identidad) |
| **TRIGGER** | Se resuelva fórmula de identidad de workload (GAP-0.3-03) |
| **DEPENDENCIES** | Ninguna (es raíz en el DAG; DC-12 depende de DC-02-A) |
| **ACCEPTANCE CRITERION** | Definición congelada de qué parámetros pertenecen a scientific identity y cuáles a operational metadata; fórmula de identidad de workload |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.3-003 (identidad workload), E-0.4-001 (hash AST), E-0.4-004 (exit codes) |
| **CONSTRAINTS** | INV-SCI-1 |
| **GAPS ASOCIADOS** | GAP-0.3-01, GAP-0.3-03, GAP-0.4-03 |
| **NOTA** | Se ejecuta en dos fases: DC-02-A (contrato provisional, precondición de DC-12) y DC-02-B (consolidación definitiva, post DC-12) |

---

### 5.4 DC-03: Determinismo observable por proveedor

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | CONTEXTUAL |
| **DESTINATION** | F18 (provider characterization protocol) |
| **TRIGGER** | Se disponga de credenciales Groq/Gemini activas Y se integre telemetría en entry point de medición (GAP-0.5-02) |
| **DEPENDENCIES** | Ninguna |
| **ACCEPTANCE CRITERION** | Protocolo de caracterización ejecutado; nivel de determinismo observable documentado por proveedor; distinción entre comportamiento observado y garantía contractual |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA CONTEXTUAL** | E-0.2-008 (cache LLM), E-0.5-003 (métricas de proveedor) |
| **CONSTRAINTS** | INV-CACHE |
| **GAPS ASOCIADOS** | GAP-0.5-02, GAP-0.7-02 |

---

### 5.5 DC-04: Alcance de caches

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (primera etapa de diseño de caches) |
| **TRIGGER** | Se resuelva DC-03 (determinismo observable por proveedor) |
| **DEPENDENCIES** | DC-03 |
| **ACCEPTANCE CRITERION** | Decisión documentada: pure-function 🟢 / LLM 🟡 / semantic+embedding 🔴; checklist de completitud de clave |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.2-008 (cache LLM preexistente) |
| **CONSTRAINTS** | INV-CACHE, DC-03 |
| **GAPS ASOCIADOS** | — |

---

### 5.6 DC-05: ¿Unificar ExecutionContext o contextos especializados?

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | NONE — GOVERNANCE/SCOPE |
| **DESTINATION** | F18 (primera etapa de diseño de contextos) |
| **TRIGGER** | Se evalúe impacto de unificación vs especialización en concurrencia (post DC-01) |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Test de god-object: qué boundary protege cada contexto; decisión documentada |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA** | Ninguna específica de Fase 0 |
| **CONSTRAINTS** | ENGINEERING_PRINCIPLES §II (Hexagonal) |
| **GAPS ASOCIADOS** | — |

---

### 5.7 DC-06b: ¿Las técnicas prescritas del ROADMAP sobreviven?

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (evaluación post-baseline) |
| **TRIGGER** | Se disponga de baseline F0-A completo con métricas por etapa (GAP-0.5-02) Y se haya medido impacto de SyncProviderBridge (GAP-0.1-01) |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Evidencia de Fase 0 vs criterio preregistrado (§9); decisión de Board o enmienda ROADMAP v3.1 |
| **AUTHORITY** | Architecture Board |
| **EVIDENCIA DIRECTA** | E-0.1-001 (barrera síncrona), E-0.1-003 (async nativo) |
| **CONSTRAINTS** | Charter §2 (ADR no reescribe ROADMAP) |
| **GAPS ASOCIADOS** | GAP-0.1-01 |

---

### 5.8 DC-07: ¿Tiers 8k/32k/1M o batch = f(budgets)?

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | CONTEXTUAL |
| **DESTINATION** | F18 (primera etapa de diseño de batching) |
| **TRIGGER** | Se disponga de caracterización suficiente de tokens/call, límites del provider y workload stress para comparar tiers discretos frente a presupuesto continuo |
| **DEPENDENCIES** | DC-03 |
| **ACCEPTANCE CRITERION** | Decisión documentada: tiers discretos, budgets continuos o combinación; valores concretos sujetos a caracterización empírica |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA CONTEXTUAL** | E-0.3-002 (ausencia de stress), E-0.5-003 (métricas de proveedor) |
| **CONSTRAINTS** | C1 (Bounded Execution), C10 (Resource Efficiency) |
| **GAPS ASOCIADOS** | GAP-0.3-02, GAP-0.7-02 |

---

### 5.9 DC-08: Write-policy SQLite + mecanismo de journal de INV-JOURNAL

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT + CONSTRAINT |
| **DESTINATION** | F18 (primera etapa de diseño de durabilidad) |
| **TRIGGER** | Se resuelva DC-01 (fork de concurrencia) |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Decisión documentada: write-policy SQLite + mecanismo que garantice idempotent apply y ventana de duplicación acotada y medida; persistencia de CB resuelta |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.2-003 (ventana post-effect/pre-journal), E-0.8-003 (Event WAL), E-0.8-012 (ventana split-brain), E-0.8-016 (orden _process_task), E-0.9-013 (zombie interception) |
| **EVIDENCIA CONTEXTUAL** | E-0.2-006 (CB in-memory), E-0.8-001 (task lease), E-0.8-006 (rate-limit buckets) |
| **CONSTRAINTS** | INV-JOURNAL (propiedad semántica: idempotent apply + ventana de duplicación acotada; no prescribe orden físico journal-before-effect) |
| **GAPS ASOCIADOS** | GAP-0.2-04, GAP-0.8-06, GAP-0.8-07, GAP-0.9-04, GAP-0.9-05, DF-24 |

---

### 5.10 DC-09: Semántica de producto de interrupción

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | NONE — GOVERNANCE/SCOPE |
| **DESTINATION** | F19 (frontera F19) |
| **TRIGGER** | Se complete Fase 18 (runtime local maduro) Y se evalúe tolerancia existente del assembler |
| **DEPENDENCIES** | DC-01, DC-08 |
| **ACCEPTANCE CRITERION** | Decisión documentada: documento degradado coherente con warnings; tolerancia del assembler como evidencia |
| **AUTHORITY** | Architecture Board |
| **EVIDENCIA** | Ninguna específica de Fase 0 |
| **CONSTRAINTS** | INV-NO-RESOURCE-SIGNAL |
| **GAPS ASOCIADOS** | — |

---

### 5.11 DC-10: Fairness y admission deadlock-free

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | CONTEXTUAL |
| **DESTINATION** | F18 (primera etapa de diseño de admission control) |
| **TRIGGER** | Se caracterice workload de estrés (GAP-0.3-02) Y se resuelva DC-01 |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Decisión documentada: admitir conjuntos dependency-ready o diferir sin retener recursos |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA CONTEXTUAL** | E-0.3-001 (contaminación normativa), E-0.3-002 (ausencia de stress) |
| **CONSTRAINTS** | C2 (Admission Control), C10 (Resource Efficiency) |
| **GAPS ASOCIADOS** | GAP-0.3-02 |

---

### 5.12 DC-11: Semántica de admisión-diferida sin nuevo estado FSM

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (primera etapa de diseño de FSM) |
| **TRIGGER** | Se complete auditoría de propagación de señales operacionales al FSM (GAP-0.4-02) |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Decisión documentada: razón indexable + admission record antes que estado nuevo; auditoría de FSM existente completada |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.4-005 (riesgo de contaminación FSM) |
| **CONSTRAINTS** | INV-NO-RESOURCE-SIGNAL, DC-11 (Charter: sin nuevo estado FSM hasta auditar existente) |
| **GAPS ASOCIADOS** | GAP-0.4-02 |

---

### 5.13 DC-12: Contrato y promoción del guard diferencial

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (maduración M0→M1→M2→M3, Charter §8.1) |
| **TRIGGER** | Se resuelva DC-02-A (contrato provisional de identidad científica) |
| **DEPENDENCIES** | DC-02-A |
| **ACCEPTANCE CRITERION** | Contrato de comparación definido; experimento M1 implementado; estabilidad M2 demostrada; required check M3 en branch protection |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.4-001 (hash AST), E-0.4-002 (ensamblado), E-0.4-003 (métricas), E-0.4-004 (exit codes) |
| **CONSTRAINTS** | INV-SCI-1, INV-ASSEMBLY-ORDER |
| **GAPS ASOCIADOS** | GAP-0.4-01 |
| **NOTA** | M0 (contrato de comparación definido en F0-E) está satisfecho como prerrequisito. El trigger para M1 es DC-02-A. |

---

### 5.14 DC-13: Coordinated shutdown / daemon lifecycle

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (primera etapa de diseño de lifecycle) |
| **TRIGGER** | Se resuelva DC-01 (fork de concurrencia) |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Decisión documentada: coordinated shutdown / daemon lifecycle orchestration; resolución de telemetry durability en crash |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.8-009 (capability no identificada), E-0.9-012 (telemetry loss 100%) |
| **CONSTRAINTS** | C6 (Cancellation), C4 (Recovery) |
| **GAPS ASOCIADOS** | GAP-0.8-01, GAP-0.9-02 |
| **NOTA** | DC-13 contiene dos superficies conceptualmente distintas: lifecycle/shutdown orchestration (GAP-0.8-01) y telemetry durability (GAP-0.9-02). La separación normativa en sub-DCs queda pendiente de resolución en ADR_F18_MASTER. |

---

### 5.15 DF-06: Imports cruzados core→apps

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (refactor de composición) |
| **TRIGGER** | Se inicie refactor de composición en F18 |
| **DEPENDENCIES** | Ninguna |
| **ACCEPTANCE CRITERION** | Imports cruzados eliminados; frontera hexagonal respetada |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.2-005 (imports cruzados confirmados) |
| **CONSTRAINTS** | ENGINEERING_PRINCIPLES §II |
| **GAPS ASOCIADOS** | GAP-0.2-03 |

---

### 5.16 DF-24: Persistencia de Circuit Breaker

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | CONTEXTUAL |
| **DESTINATION** | F18 (subsumido en DC-08) |
| **TRIGGER** | Se resuelva DC-01 Y DC-08 |
| **DEPENDENCIES** | DC-01, DC-08 |
| **ACCEPTANCE CRITERION** | Decisión documentada: persistir o no persistir CB; si se persiste, patrón de store |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA CONTEXTUAL** | E-0.2-006 (CB in-memory), E-0.2-007 (patrón UPSERT como referencia) |
| **CONSTRAINTS** | C4 (Recovery), C10 (Resource Efficiency) |
| **GAPS ASOCIADOS** | GAP-0.2-02 |

---

### 5.17 DF-34: Persistencia de ProfileStore

| Campo | Valor |
|---|---|
| **STATE** | DEFERRED |
| **EVIDENCE BASIS** | DIRECT |
| **DESTINATION** | F18 (decisión de persistencia) |
| **TRIGGER** | Se resuelva DC-01 Y se cuantifique coste agregado de re-inferencia |
| **DEPENDENCIES** | DC-01 |
| **ACCEPTANCE CRITERION** | Decisión documentada: persistir o no persistir ProfileStore; si se persiste, patrón de store |
| **AUTHORITY** | Architecture Board / ADR_F18_MASTER |
| **EVIDENCIA DIRECTA** | E-0.2-004 (ProfileStore in-memory), E-0.8-008 (DF-34 confirmado) |
| **CONSTRAINTS** | C4 (Recovery) |
| **GAPS ASOCIADOS** | GAP-0.2-01 |

---

## 6. VERIFICACIÓN DE COMPLETITUD DE DCs

### 6.1 Checklist Charter §7

| DC | ¿Tiene estado? | ¿RESOLVED o DEFERRED? | Si DEFERRED: ¿DESTINATION? | ¿TRIGGER no satisfecho? | ¿DEPENDENCIES? | ¿ACCEPTANCE CRITERION? | Estado |
|---|---|---|---|---|---|---|---|
| DC-01 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ Ninguna | ✅ | VÁLIDO |
| DC-02 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ Ninguna | ✅ | VÁLIDO |
| DC-03 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ Ninguna | ✅ | VÁLIDO |
| DC-04 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-03 | ✅ | VÁLIDO |
| DC-05 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-01 | ✅ | VÁLIDO |
| DC-06a | ✅ | GOVERNANCE-RESOLVED | N/A | N/A | N/A | N/A | VÁLIDO |
| DC-06b | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-01 | ✅ | VÁLIDO |
| DC-07 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-03 | ✅ | VÁLIDO |
| DC-08 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-01 | ✅ | VÁLIDO |
| DC-09 | ✅ | DEFERRED | ✅ F19 | ✅ | ✅ DC-01, DC-08 | ✅ | VÁLIDO |
| DC-10 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-01 | ✅ | VÁLIDO |
| DC-11 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-01 | ✅ | VÁLIDO |
| DC-12 | ✅ | DEFERRED | ✅ F18 | ✅ | ✅ DC-02-A | ✅ | VÁLIDO |

**Veredicto:** Todos los DCs poseen estado de gobernanza válido. DC-06a está GOVERNANCE-RESOLVED; los 12 DC restantes están DEFERRED con DESTINATION + TRIGGER + DEPENDENCIES + ACCEPTANCE CRITERION explícitos. Ningún DC queda OPEN o MALFORMED.

### 6.2 DCs sin evidencia F0 específica

| DC | Razón | Clasificación |
|---|---|---|
| DC-05 | Sin evidencia F0 específica; diferido por alcance arquitectónico | GOVERNANCE-DEFERRED |
| DC-09 | Sin evidencia F0 específica; diferido por frontera F19 | GOVERNANCE-DEFERRED |

---

## 7. MATRIZ DE TRAZABILIDAD EVIDENCIA → DC

| DC | Evidencia DIRECTA | Evidencia CONTEXTUAL | Constraints | Gaps |
|---|---|---|---|---|
| DC-01 | E-0.1-001, E-0.1-003, E-0.1-007 | E-0.1-002, E-0.1-004, E-0.1-006, E-0.2-006 | INV-SCI-1, INV-OPS-1 | GAP-0.1-01, GAP-0.1-02, GAP-0.1-03 |
| DC-02 | E-0.3-003, E-0.4-001, E-0.4-004 | — | INV-SCI-1 | GAP-0.3-01, GAP-0.3-03, GAP-0.4-03 |
| DC-03 | — | E-0.2-008, E-0.5-003 | INV-CACHE | GAP-0.5-02, GAP-0.7-02 |
| DC-04 | E-0.2-008 | — | INV-CACHE, DC-03 | — |
| DC-05 | — | — | ENGINEERING §II | — |
| DC-06b | E-0.1-001, E-0.1-003 | — | Charter §2 | GAP-0.1-01 |
| DC-07 | — | E-0.3-002, E-0.5-003 | C1, C10 | GAP-0.3-02, GAP-0.7-02 |
| DC-08 | E-0.2-003, E-0.8-003, E-0.8-012, E-0.8-016, E-0.9-013 | E-0.2-006, E-0.8-001, E-0.8-006 | INV-JOURNAL | GAP-0.2-04, GAP-0.8-06, GAP-0.8-07, GAP-0.9-04, GAP-0.9-05, DF-24 |
| DC-09 | — | — | INV-NO-RESOURCE-SIGNAL | — |
| DC-10 | — | E-0.3-001, E-0.3-002 | C2, C10 | GAP-0.3-02 |
| DC-11 | E-0.4-005 | — | INV-NO-RESOURCE-SIGNAL | GAP-0.4-02 |
| DC-12 | E-0.4-001, E-0.4-002, E-0.4-003, E-0.4-004 | — | INV-SCI-1, INV-ASSEMBLY-ORDER | GAP-0.4-01 |
| DC-13 | E-0.8-009, E-0.9-012 | — | C6, C4 | GAP-0.8-01, GAP-0.9-02 |
| DF-06 | E-0.2-005 | — | ENGINEERING §II | GAP-0.2-03 |
| DF-24 | — | E-0.2-006, E-0.2-007 | C4, C10 | GAP-0.2-02 |
| DF-34 | E-0.2-004, E-0.8-008 | — | C4 | GAP-0.2-01 |

**Nota:** Matriz completa de cobertura de DCs. Los DCs sin evidencia F0 específica (DC-05, DC-09) están explícitamente marcados como GOVERNANCE-DEFERRED.

---

## 8. CIERRE DEL HITO 0.12

**Estado del HITO:** FROZEN v1.0.1
**Condición de cierre cumplida:** 52 entradas de evidencia consolidadas en 7 categorías con clasificación epistémica y rol (DIRECT/CONTEXTUAL/CONSTRAINT); 13 Decision Candidates con estado de gobernanza válido (1 GOVERNANCE-RESOLVED, 12 DEFERRED con DESTINATION + TRIGGER + DEPENDENCIES + ACCEPTANCE CRITERION); DC Dependency DAG documentado; ciclo DC-02 ↔ DC-12 roto explícitamente (DC-02-A → DC-12 → DC-02-B); INV-JOURNAL tratado como propiedad semántica, no como orden físico; triggers corregidos (ninguno ya satisfecho); DC-05 y DC-09 marcados como GOVERNANCE-DEFERRED; E-0.8-009 reformulado como "capability no identificada en superficies auditadas"; versiones fuente reconciliadas (HITO_0.10 v1.0.1, HITO_0.11 v1.0.1).
**Verificación de cadena de gobernanza:** Charter §7, §8 → HITOs 0.1-0.9 → HITO_0.10 v1.0.1 (Gap Matrix) → HITO_0.11 v1.0.1 (Current State & Contract Map) → este documento → ADR_F18_MASTER §7.
**Refinamientos respecto a HITOs previos:** No se identifican contradicciones materiales con la evidencia fuente; existen refinamientos de clasificación epistemológica, reformulación de INV-JOURNAL, corrección de triggers y resolución de dependencias circulares documentados en la consolidación.
**Siguiente paso recomendado:** Con los 4 outputs obligatorios de Charter §8 completos (HITO_0.10, 0.11, 0.12 + propuesta de congelamiento), emitir ADR_F18_MASTER.

---

## 📊 Estado final de Fase 0

| HITO | Estado | Rol |
|---|---|---|
| 0.1 F0-B Concurrency Blocking Map | FROZEN v1.2.0 | Discovery estático |
| 0.2 F0-G Authority Boundary Map | FROZEN v1.2.0 | Discovery de autoridades |
| 0.3 F0-F Workload Characterization | FROZEN v1.3.0 | Discovery de workload |
| 0.4 F0-E Scientific Neutrality Contract | FROZEN v1.3.0 | Compliance audit + contrato M0 |
| 0.5 F0-A Runtime Profile Protocol | FROZEN v1.2.0 | Protocolo |
| 0.6 Workload Anchor Reconciliation | FROZEN v1.0.0 | Reconciliación de perímetro |
| 0.7 F0-A Runtime Profile Baseline | FROZEN v1.1.0 | Baseline operacional |
| 0.8 F0-C State Durability & Recovery Map | FROZEN v1.4.0 | Matriz de durabilidad |
| 0.9 F0-D Waste/FinOps Map | FROZEN v1.4.0 | Baseline de waste |
| 0.10 Architecture Gap Matrix Consolidated | FROZEN v1.0.1 | Output obligatorio Charter §8 |
| 0.11 Current State & Contract Map | FROZEN v1.0.1 | Output obligatorio Charter §8 |
| **0.12 Evidence Register & DC Resolutions** | **FROZEN v1.0.1** | **Output obligatorio Charter §8** |

---

## ✅ FASE 0: DISCOVERY COMPLETE

**Todos los HITOs FROZEN. Todos los outputs obligatorios de Charter §8 emitidos. Todos los DCs poseen estado de gobernanza válido.**

**Semántica de cierre:** Fase 0 no afirma "tenemos todas las respuestas". Afirma: "sabemos qué sabemos, qué no sabemos, qué decisiones están autorizadas, qué decisiones siguen abiertas, qué evidencia las habilita y bajo qué condición pueden resolverse."

**Siguiente paso:** Emitir ADR_F18_MASTER.