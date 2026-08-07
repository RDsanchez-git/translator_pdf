# PHASE 17-BIS EXECUTION PLAN v2.2.0
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 2.2.0
**Status:** `APPROVED BASELINE` — FROZEN
**Date:** 2026-08-04
**Supersedes:** v2.1.0
**Derived From:** 11 NADRs FROZEN + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas.

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model
```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
NADRs 01-11 (reglas constitucionales permanentes, FROZEN)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:
`NADR-{XX} §{sección} R{regla}`

Ejemplo: `NADR-08 §5.2 R3` → NADR-08, sección 5.2, regla 3.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN**. Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Operational Principles

- **Los NADRs no pertenecen a una fase.** Son reglas constitucionales permanentes. Lo que se asigna por fase son sus reglas individuales.
- **El Execution Plan es la única fuente de verdad temporal.** No existen matrices de trazabilidad paralelas.
- **Política de referencias cruzadas:** Una regla puede aparecer en múltiples tareas **únicamente** cuando una tarea la implementa y otra la verifica o completa. Nunca deben existir dos tareas implementando la misma obligación.
- **El estado de una regla es derivado.** Una regla no tiene estado propio. Su estado es el estado de la tarea que la implementa, salvo que esté distribuida (implementada en una tarea, verificada en otra).

---

## 2. GATE 1 — CORE INTEGRITY & AUTOMATED GATES

**Objective:** Sellar el repositorio contra regresiones arquitectónicas y garantizar el determinismo criptográfico.
**Execution Mode:** Altamente secuencial (Critical Path).
**Rollback Plan:** `git revert` + restaurar fingerprints `.json` congelados de Fase 16 desde backup.

### 2.1 Wave 1.1 — Regression Gates Infrastructure (NADR-10)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.1.1** | Definir configuración declarativa de CI Platform con Required Status Checks | NADR-10 §5.2 R6 | Low | — | DONE |
| **1.1.2** | Refactorizar `test_golden_parser.py`: eliminar tautologías, forzar matching Read-Only contra oráculo | NADR-10 §5.1 R2, R3; §5.2 R5 | High | 1.1.1 | DONE |
| **1.1.3** | Implementar mecanismo explícito de actualización de baseline; forzar `FileNotFoundError` en baselines ausentes | NADR-10 §5.1 R1, R4 | Medium | 1.1.2 | DONE |
| **1.1.4** | Forzar comparación completa de campos DTO en snapshot tests | NADR-10 §5.2 R13 | Medium | 1.1.2 | DONE |
| **1.1.5** | Eliminar sustitución artificial de componentes en integration tests | NADR-10 §5.2 R14 | High | 1.1.2 | DONE |
| **1.1.6** | Activar configuración declarativa de tooling (pyproject.toml) | NADR-10 §5.2 R7 | Low | 1.1.1 | DONE |
| **1.1.7** | Activar Daemon de Reconciliación CQRS vía configuración externa | NADR-10 §5.2 R8, R11, R12 | High | 1.1.1 | DONE |
| **1.1.8** | Alinear Benchmark con pipeline de producción (preparación) | NADR-10 §5.3 R9, R10 | Critical | 1.1.1 | DONE |

### 2.2 Wave 1.2 — Canonical AST & Deterministic Identity (NADR-01, NADR-03)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Eliminar `ast_deserializer.py`; rutear todas las cargas a `infra/serialization/ast_json.py` | NADR-01 §5.1 R1, R2 | Critical | 1.1.1 | DONE |
| **1.2.2** | Añadir regla de linter estático bloqueando instanciación directa de `ASTNode(**kwargs)` desde dicts no tipados | NADR-01 §5.1 R3, R4 | Low | 1.1.1 | DONE |
| **1.2.3** | Extraer lógica de chunking de `hashing.py` a `core/chunking/chunker.py` | NADR-03 §5.2 R1, R2, R3 | High | 1.2.1 | DONE |
| **1.2.4** | Refactorizar pre-imagen de `compute_ast_hash()` para excluir explícitamente `node_id` y metadata efímera | NADR-03 §5.1 R1, R2, R3 | Critical | 1.2.3 | DONE |
| **1.2.5** | Separar chunking de semantic hashing en responsabilidad modular | NADR-03 §5.2 R4, R5 | Medium | 1.2.3 | DONE |

### 2.3 Gate 1 Exit Criteria

Todas las reglas de NADR-01, NADR-03 y NADR-10 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:
- Cero aserciones tautológicas en tests de regresión
- `compute_ast_hash()` produce salida idéntica para ASTs semánticamente idénticos independientemente de `node_id`
- CI bloquea merges ante fallos de regresión
- Benchmark corre contra adaptador de producción (no parser legacy)

---

## 3. GATE 2 — HEXAGONAL BOUNDARIES & INGESTION PURITY

**Objective:** Centralizar inyección de dependencias y purgar infraestructura cruda del dominio.
**Execution Mode:** Épicas paralelas.
**Rollback Plan:** `git revert` de lógica de fábrica; re-habilitar temporalmente adaptador de validación legacy.

### 3.1 Wave 2.1 — Composition Root Consolidation (NADR-11, NADR-04)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Limpiar `pipeline_factory.py`: eliminar mutaciones post-constructor DI; forzar inyección solo por constructor | NADR-11 §5.1 R1, R2, R3 | High | Gate 1 | DONE |
| **2.1.2** | Inyectar `DocumentLayoutValidator` y `PolymorphicValidationEngine` vía constructores | NADR-04 §5.1 R1, R2; §5.2 R1 | High | 2.1.1 | DONE |
| **2.1.3** | Eliminar `LegacyValidatorAdapter` y remover lógica legacy de fases 11/12 | NADR-04 §5.2 R2, R3, R4 | Medium | 2.1.2 | DONE |
| **2.1.4** | Configurar contrato `import-linter` prohibiendo fugas `core/` → `infra/` | NADR-11 §5.2 R1, R2 | Low | Gate 1 | DONE |
| **2.1.5** | Formalizar contrato explícito `DispatcherProtocol` | NADR-11 §5.3 R1, R2 | Medium | 2.1.1 | DONE |

### 3.2 Wave 2.2 — Ingestion Purity (NADR-02, NADR-10)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Eliminar imports de `fitz` en `core/ast/router.py`; delegar traits a `infra/adapters` | NADR-02 §5.1 R1, R2, R3 | High | 2.1.4 | TODO |
| **2.2.2** | Actualizar `pipeline_factory.py` para instanciar proveedores de extracción vía configuraciones dinámicas | NADR-02 §5.2 R1, R2 | Medium | 2.2.1 | TODO |
| **2.2.3** | Eliminar `core/ast/parser.py` (parser legacy regex) y completar alineación de Benchmarks con adaptador de producción | NADR-02 §5.3 R1; NADR-10 §5.3 R10 (completa) | Critical | 2.2.2 | TODO |

> **Nota de referencia cruzada (§1.3):** `NADR-10 §5.3 R10` aparece en la tarea 1.1.8 (preparación) y en la tarea 2.2.3 (completación). La tarea 1.1.8 prepara la alineación; la tarea 2.2.3 la completa eliminando el parser legacy. No hay doble implementación.

### 3.3 Gate 2 Exit Criteria

Todas las reglas de NADR-02, NADR-04 y NADR-11 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Cero imports de `fitz` en `core/`
- Adaptador legacy de validación eliminado
- Composition Root usa inyección por constructor exclusivamente
- Contrato `import-linter` activo en CI

---

## 4. GATE 3 — DISTRIBUTED EXECUTION PLANE & HEALING

**Objective:** Alcanzar paridad operacional entre CLI/Daemon y escalar horizontalmente el worker loop.
**Execution Mode:** Épicas paralelas.
**Rollback Plan:** `git revert`; downgrade del cluster de workers a escala single-node.

### 4.1 Wave 3.1 — Context Resolution & Healing (NADR-05, NADR-07)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Eliminar `DummyContextResolver` e inyectar resolver real en orquestación CLI | NADR-05 §5.1 R1, R2, R3 | Medium | Gate 2 | DONE |
| **3.1.2** | Implementar invalidación de caché de contexto jerárquico | NADR-05 §5.2 R1, R2 | High | 3.1.1 | DONE |
| **3.1.3** | Eliminar slicing de array (`hard_fails[0]`) en `AsyncDispatcher` para permitir iteración multi-fallo | NADR-07 §5.2 R1, R2 | Medium | Gate 2 | DONE |
| **3.1.4** | Añadir detección de colisión de mutaciones dentro de `HealingPipeline` para seguridad de rollback atómico | NADR-07 §5.1 R1, R2, R3 | High | 3.1.3 | DONE |
| **3.1.5** | Forzar idempotencia de healing entre iteraciones consecutivas | NADR-07 §5.3 R1, R2 | Medium | 3.1.4 | DONE |

### 4.2 Wave 3.2 — Distributed Execution & CQRS Lineage (NADR-08)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Definir Protocol abstracto `RateLimitStore` en `core/resilience/rate_limit_store.py` | NADR-08 §5.1 R1, R2, R3 | Low | Gate 2 | DONE |
| **3.2.2** | Implementar adaptador distribuido para `TokenBucket` y `GlobalCircuitBreaker` | NADR-08 §5.1 R4; §5.2 R1, R2, R3 | Critical | 3.2.1 | PARTIAL — CircuitBreaker DONE; TokenBucket adapter BLOCKED (GF-01) |
| **3.2.3** | Eliminar `"unknown_ast_hash"` del Reconciler; inyectar hash criptográfico de linaje real en `RematerializeTaskCommand` | NADR-08 §5.3 R1, R2, R3 | High | Gate 1 | DONE |
| **3.2.4** | Activar reconciliación CQRS vía configuración externa | NADR-08 §5.4 R1, R2, R3 | Medium | 3.2.3 | DONE |
| **3.2.5** | Componer RateLimitStore y CircuitBreaker en el stack de proveedores | NADR-08 §5.5 R1, R2 | Medium | 3.2.2 | DONE |

> **Nota de gobernanza (Task 3.2.2):** El adaptador distribuido de `TokenBucket` queda bloqueado por GF-01 (conflicto normativo entre Execution Plan y ADR Maestro §4). El puerto `RateLimitStore` fue definido (Task 3.2.1) y la arquitectura está preparada para la implementación del backend, pero esta se difiere a Gate 4. La parte de `GlobalCircuitBreaker` sí fue completada vía `CircuitBreakerProvider`.

### 4.3 Gate 3 Exit Criteria

Todas las reglas de NADR-05, NADR-07 y NADR-08 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Cero `DummyContextResolver` en ruta de producción
- Iteración multi-fallo de healing operacional
- Rate limiting distribuido coordina entre N procesos
- Rematerialización CQRS usa `ast_hash` real
- Daemon de reconciliación activo en producción

---

## 5. GATE 4 — COMPILER & ARTIFACT GENERATION

**Objective:** Asegurar concurrencia de I/O y garantizar preservación de sintaxis matemática.
**Execution Mode:** Altamente paralelo (dominios separados).
**Rollback Plan:** Revertir implementaciones de runners.

### 5.1 Wave 4.1 — FSM Integrity & Compiler I/O Isolation (NADR-09)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Eliminar comandos sintéticos del adaptador de persistencia FSM; forzar orquestador como única fuente de eventos | NADR-09 §5.1 R1, R2, R3, R4, R5 | High | Gate 3 | TODO |
| **4.1.2** | Envolver I/O del compilador en directorios temporales efímeros; eliminar referencias a `os.getcwd()` | NADR-09 §5.2 R1, R2, R3, R4 | Critical | 4.1.1 | TODO |
| **4.1.3** | Forzar compilador como efecto lateral aislado sin mutación de dominio | NADR-09 §5.2 R5, R6, R7 | High | 4.1.2 | TODO |

### 5.2 Wave 4.2 — Token Estimation & Compilation Governance (NADR-06)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Implementar adaptador de Tokenizer BPE compatible con proveedor; eliminar `FastWordEstimator` | NADR-06 §5.1 R1, R2, R3, R4 | High | Gate 3 | TODO |
| **4.2.2** | Refactorizar `LatexEscaper` para detectar fronteras matemáticas y bypasear escapado interno | NADR-06 §5.2 R1, R2, R3, R4 | Critical | Gate 3 | TODO |
| **4.2.3** | Re-cablear Daemon para rutear todos los ensamblados estrictamente a través de `CompilationService` (sin bypass, sin ad-hoc) | NADR-06 §5.3 R1, R2, R3, R4 | High | 4.2.2 | TODO |

### 5.3 Gate 4 Exit Criteria

Todas las reglas de NADR-06 y NADR-09 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- FSM emite solo transiciones ordenadas por el orquestador
- I/O del compilador aislado en directorios efímeros
- Tokenizer BPE produce estimaciones precisas de LaTeX
- Escapado TeX preserva sintaxis matemática legítima
- Daemon rutea exclusivamente a través de `CompilationService`

---

### 5.4 GATE COMPLETION LOG

| Gate | Fecha de cierre | Reglas cubiertas | Observaciones |
|------|----------------|-----------------|---------------|
| Gate 1 | 2026-08-04 | 26/26 | pyright 0 errors. Imports migrados. AST hashing semántico confirmado. |
| Gate 2 | 2026-08-05 | 20/20 | fitz eliminado del dominio. Parser legacy eliminado. Composition Root consolidado. DF-11 registrado como Architecture Freeze Blocker. |
| Gate 3 | 2026-08-07 | 25/27 | Wave 3.1 completada (Context Resolution + Healing transaccional). Wave 3.2 completada con excepción de NADR-08 §5.1 R3-R4 diferidos por GF-01. `RateLimitStore` protocol definido. `CircuitBreakerProvider` integrado. `ast_hash` propagado en CQRS lineage. `resilient_provider.py` eliminado (DF-23). Gate Exit Review ejecutado: 12 DFs reclasificados a Gate 4, 1 resuelto (DF-23), 1 nuevo registrado (DF-28). |
| Gate 4 | — | 0/24 | — |

### 5.5 Gate Exit Review

Antes de declarar el Gate como COMPLETED, se revisarán todos los
Deferred Findings cuyo Gate destino sea el Gate actual.

**Estados posibles (Gate Exit Review §5.5):**

| Estado | Significado |
|--------|-------------|
| **RESUELTO** | El hallazgo fue implementado y cerrado |
| **RECLASIFICADO** | Cambia de Gate destino o prioridad con justificación |
| **CONVERTIDO EN GF** | Pasa a Governance Finding |
| **CLOSED (NAR)** | No Action Required |

**Regla:** Ningún Deferred Finding podrá permanecer asignado a un Gate ya cerrado.

**Nota sobre Governance Findings:** Los GFs se revisan cuando se llega al 
hito de gobernanza donde pueden resolverse, que puede coincidir o no con 
un Gate técnico.

## 6. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas.

| Step | Operation | Environment | Linked Rules | Evidence |
|---|---|---|---|---|
| **MIG-01** | Corpus Resealing: ejecutar `tools/reseal_corpus.py` para regenerar baselines `.fingerprint.json` y `.ast.json` con el nuevo hash determinista | Local, CI | NADR-03 §5.1 R1, R2 | E-0.1-003 |
| **MIG-02** | Truncar caché materializada: `DELETE FROM materialized_cache` para purgar claves legacy inyectadas por `DummyContextResolver` | Staging, Prod | NADR-05 §5.1 R1, R2 | P4-05 |
| ~~**MIG-03**~~ | ~~Desplegar KV Store distribuido: aprovisionar Redis (o backend equivalente) para `RateLimitStore`~~ | — | — | **ELIMINADO — contradice ADR Maestro §4 y GF-01.** La implementación del backend de `RateLimitStore` se difiere a Gate 4 donde se resolverá el conflicto normativo. El ROADMAP prohíbe explícitamente Redis. |

---

## 7. GLOBAL DoD (Definition of Done)

La Fase 17-BIS se considera oficialmente completada cuando:
`{All rules in FROZEN NADRs 01-11} − {Rules with DONE status in §9} = ∅`

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 8. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§9), no se hardcodean:

| Gate | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|
| Gate 1 | 26 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 20 | 0 | 0 | ✅ COMPLETED |
| Gate 3 | 25 | 2 (GF-01) | 0 | ✅ COMPLETED |
| Gate 4 | 0 | 0 | 24 | 🔴 Not Started |
| **TOTAL** | **71** | **2** | **24** | 🟡 In Progress |

**Nota operativa:** Las 2 reglas DEFERRED de Gate 3 (NADR-08 §5.1 R3, R4) están explícitamente diferidas por GF-01 (conflicto normativo). Se resolverán en Gate 4. No constituyen un fallo del Gate; son una decisión de gobernanza documentada.

**Nota operativa:** Cada vez que una tarea pase a `DONE`, el `Derived Status` de sus reglas en §9 se actualiza y los contadores de este dashboard se recalculan manualmente. El estado de una regla es siempre derivado del estado de la tarea que la implementa (§1.3).

---

## 9. TRACEABILITY APPENDIX — AUDIT BOARD

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la tarea que la implementa (§1.3). La relación Task → Rules ya está definida en los Gates (§2–§5); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence`

### 9.1 Gate 1 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-10 §5.2 R6 | DONE | Wave 1.1 |
| NADR-10 §5.1 R2 | DONE | Wave 1.1 |
| NADR-10 §5.1 R3 | DONE | Wave 1.1 |
| NADR-10 §5.2 R5 | DONE | Wave 1.1 |
| NADR-10 §5.1 R1 | DONE | Wave 1.1 |
| NADR-10 §5.1 R4 | DONE | Wave 1.1 |
| NADR-10 §5.2 R13 | DONE | Wave 1.1 |
| NADR-10 §5.2 R14 | DONE | Wave 1.1 |
| NADR-10 §5.2 R7 | DONE | Wave 1.1 |
| NADR-10 §5.2 R8 | DONE | Wave 1.1 |
| NADR-10 §5.2 R11 | DONE | Wave 1.1 |
| NADR-10 §5.2 R12 | DONE | Wave 1.1 |
| NADR-10 §5.3 R9 | DONE | Wave 1.1 |
| NADR-10 §5.3 R10 | DONE | Wave 1.1 |
| NADR-01 §5.1 R1 | DONE | Wave 1.2 |
| NADR-01 §5.1 R2 | DONE | Wave 1.2 |
| NADR-01 §5.1 R3 | DONE | Wave 1.2 |
| NADR-01 §5.1 R4 | DONE | Wave 1.2 |
| NADR-03 §5.2 R1 | DONE | Wave 1.2 |
| NADR-03 §5.2 R2 | DONE | Wave 1.2 |
| NADR-03 §5.2 R3 | DONE | Wave 1.2 |
| NADR-03 §5.1 R1 | DONE | Wave 1.2 |
| NADR-03 §5.1 R2 | DONE | Wave 1.2 |
| NADR-03 §5.1 R3 | DONE | Wave 1.2 |
| NADR-03 §5.2 R4 | DONE | Wave 1.2 |
| NADR-03 §5.2 R5 | DONE | Wave 1.2 |

### 9.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-11 §5.1 R1 | DONE | Wave 2.1 |
| NADR-11 §5.1 R2 | DONE | Wave 2.1 |
| NADR-11 §5.1 R3 | DONE | Wave 2.1 |
| NADR-04 §5.1 R1 | DONE | Wave 2.1 |
| NADR-04 §5.1 R2 | DONE | Wave 2.1 |
| NADR-04 §5.2 R1 | DONE | Wave 2.1 |
| NADR-04 §5.2 R2 | DONE | Wave 2.1 |
| NADR-04 §5.2 R3 | DONE | Wave 2.1 |
| NADR-04 §5.2 R4 | DONE | Wave 2.1 |
| NADR-11 §5.2 R1 | DONE | Wave 2.1 |
| NADR-11 §5.2 R2 | DONE | Wave 2.1 |
| NADR-11 §5.3 R1 | DONE | Wave 2.1 |
| NADR-11 §5.3 R2 | DONE | Wave 2.1 |
| NADR-02 §5.1 R1 | DONE | Wave 2.2 |
| NADR-02 §5.1 R2 | DONE | Wave 2.2 |
| NADR-02 §5.1 R3 | DONE | Wave 2.2 |
| NADR-02 §5.2 R1 | DONE | Wave 2.2 |
| NADR-02 §5.2 R2 | DONE | Wave 2.2 |
| NADR-02 §5.3 R1 | DONE | Wave 2.2 |
| NADR-10 §5.3 R10 (completa) | DONE | Wave 2.2 |

### 9.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-05 §5.1 R1 | DONE | Wave 3.1 — `DynamicContextResolver` + `ContextRegistry` + `_build_context_stack()` |
| NADR-05 §5.1 R2 | DONE | Wave 3.1 — `DummyContextResolver` eliminado de `apps/cli/main.py` |
| NADR-05 §5.1 R3 | DONE | Wave 3.1 — Fail-fast en `DynamicContextResolver`. Sin fallback. Sin contexto vacío silencioso |
| NADR-05 §5.2 R1 | DONE | Wave 3.1 — `prompt_hash` incorpora contexto real. Invalidación automática |
| NADR-05 §5.2 R2 | DONE | Wave 3.1 — Claves de materialización vinculadas a identidad contextual via `prompt_hash` |
| NADR-07 §5.2 R1 | DONE | Wave 3.1 — `heal_all_and_revalidate()` recibe colección completa de fallos |
| NADR-07 §5.2 R2 | DONE | Wave 3.1 — Estrategias aplicadas secuencialmente por prioridad |
| NADR-07 §5.1 R1 | DONE | Wave 3.1 — `_plan_healing()` con deduplicación por `strategy_id` |
| NADR-07 §5.1 R2 | DONE | Wave 3.1 — `_apply_mutations()` secuencial por prioridad |
| NADR-07 §5.1 R3 | DONE | Wave 3.1 — Sin descarte de fallos. Colección completa procesada |
| NADR-07 §5.3 R1 | DONE | Wave 3.1 — Revalidación única dentro del ciclo transaccional (`_validate_result()`) |
| NADR-07 §5.3 R2 | DONE | Wave 3.1 — Sin revalidación redundante en el dispatcher. `HealingFailedException` como resultado suficiente |
| NADR-08 §5.1 R1 | DONE | Wave 3.2 — `RateLimitStore` protocol creado en `core/resilience/rate_limit_store.py` |
| NADR-08 §5.1 R2 | DONE | Wave 3.2 — Protocol define operaciones `load()` y `save()` (contrato de persistencia) |
| NADR-08 §5.1 R3 | DEFERRED (GF-01) | Wave 3.2 — Puerto definido, pero `TokenBucket` aún usa memoria local. Implementación del backend diferida a Gate 4 por conflicto normativo (ADR Maestro §4 prohíbe infraestructura distribuida). |
| NADR-08 §5.1 R4 | DEFERRED (GF-01) | Wave 3.2 — Puerto permite selección de backend desde Composition Root, pero ningún backend está cableado aún. Diferido a Gate 4. |
| NADR-08 §5.2 R1 | DONE | Wave 3.2 — `CircuitBreakerProvider` integrado en stack de `apps/cli/main.py` y `apps/llm_workers/__main__.py` |
| NADR-08 §5.2 R2 | DONE | Wave 3.2 — `GlobalCircuitBreaker` con `failure_threshold`, `window_sec`, `recovery_timeout` configurables |
| NADR-08 §5.2 R3 | DONE | Wave 3.2 — Stack CB → Cache → RL → Provider. Ninguna ruta elude el CircuitBreaker |
| NADR-08 §5.3 R1 | DONE | Wave 3.2 — `ast_hash` agregado a `RematerializeTaskCommand` en `core/execution/state.py` |
| NADR-08 §5.3 R2 | DONE | Wave 3.2 — `"unknown_ast_hash"` eliminado de `core/execution/handlers.py`. Reemplazado por `cmd.ast_hash` |
| NADR-08 §5.3 R3 | DONE | Wave 3.2 — Propagación de `ast_hash` desde `ReconcilerDaemon._sweep_tasks()`. Proyecciones recuperables por el ensamblador |
| NADR-08 §5.4 R1 | DONE | Wave 3.2 — Reconciliación CQRS activa en producción (verificado) |
| NADR-08 §5.4 R2 | DONE | Wave 3.2 — Gobernada por `RuntimeSettings.reconciliation_enabled` (configuración externa) |
| NADR-08 §5.4 R3 | DONE | Wave 3.2 — Sin banderas hardcodeadas. `__main__` lee de `os.environ` en el borde |
| NADR-08 §5.5 R1 | DONE | Wave 3.2 — CircuitBreaker y RateLimiter operan de forma compuesta en el stack |
| NADR-08 §5.5 R2 | DONE | Wave 3.2 — CB antes de RL en el stack. Circuito abierto previene consumo de cuota |

### 9.4 Gate 4 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-09 §5.1 R1 | PENDING | — |
| NADR-09 §5.1 R2 | PENDING | — |
| NADR-09 §5.1 R3 | PENDING | — |
| NADR-09 §5.1 R4 | PENDING | — |
| NADR-09 §5.1 R5 | PENDING | — |
| NADR-09 §5.2 R1 | PENDING | — |
| NADR-09 §5.2 R2 | PENDING | — |
| NADR-09 §5.2 R3 | PENDING | — |
| NADR-09 §5.2 R4 | PENDING | — |
| NADR-09 §5.2 R5 | PENDING | — |
| NADR-09 §5.2 R6 | PENDING | — |
| NADR-09 §5.2 R7 | PENDING | — |
| NADR-06 §5.1 R1 | PENDING | — |
| NADR-06 §5.1 R2 | PENDING | — |
| NADR-06 §5.1 R3 | PENDING | — |
| NADR-06 §5.1 R4 | PENDING | — |
| NADR-06 §5.2 R1 | PENDING | — |
| NADR-06 §5.2 R2 | PENDING | — |
| NADR-06 §5.2 R3 | PENDING | — |
| NADR-06 §5.2 R4 | PENDING | — |
| NADR-06 §5.3 R1 | PENDING | — |
| NADR-06 §5.3 R2 | PENDING | — |
| NADR-06 §5.3 R3 | PENDING | — |
| NADR-06 §5.3 R4 | PENDING | — |

---

## 10. FUTURE WORK

> The Traceability Appendix (§9) is intentionally written manually in this version. Future versions **MAY** generate this appendix automatically from task metadata, eliminating manual synchronization. This note prevents the assumption that the appendix must always be maintained by hand.

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN, no este documento. El estado de cada regla es derivado del estado de la tarea que la implementa.


## 11. DEFERRED FINDINGS REGISTER

Hallazgos identificados durante la implementación que no bloquean
el Gate actual pero requieren atención en Gates futuros.

---

| # | Hallazgo | Origen | Gate destino | Prioridad | Estado | Motivo | Gate nuevo |
|---|----------|--------|--------------|-----------|--------|--------|------------|
| DF-01 | `core/benchmark/__main__.py` computa su propio SHA-256 por nodo en lugar de usar `compute_ast_hash()`. Identidad criptográfica desconectada del hash canónico. | Wave 1.2 | Gate 4 (Task 4.2.x) | Medium | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-02 | Patrón `hasattr(n.node_type, "value")` persiste en múltiples archivos. Código defensivo innecesario si `ContentNodeType` está tipado definitivamente. | Wave 1.2 | Gate 2 | Low | RECLASIFICADO | Revisión tardía: Gate 2 se cerró sin ejecutar Gate Exit Review. Patrón defensivo persiste. No es prioridad de Gate 3. | Gate 4 |
| DF-03 | `tools/benchmark_archive/` contiene scripts con hashing propio (`generate_sha256`). | Wave 1.2 | N/A | None | CLOSED (NAR) | Declarado OUT OF SCOPE. Archivado. | — |
| DF-04 | `SemanticChunkBoundaryPolicy.can_group()` siempre retorna `ALLOW`. Falta implementar reglas de HARD_BREAK cuando el AST incorpore semántica de contexto cruzado. | Pre-existente | Gate 3+ | Low | RECLASIFICADO | Renombrado a `StructuralChunkBoundaryPolicy`. Verificar si HARD_BREAK sigue sin implementar. Requiere semántica de contexto cruzado. | Gate 4 |
| DF-07 | El constructor de AsyncDispatcher acumula 6 dependencias. A futuro, introducir DispatcherFactory en `apps/bootstrap/`. | Wave 2.1 | Gate 3+ | Low | RECLASIFICADO | `DispatcherFactory` no existe en `apps/bootstrap/`. Mejora de mantenibilidad, no bloquea Gate 3. | Gate 4 |
| DF-10 | `core/ast/router.py` (PDFRouter) es un wrapper transicional. Eliminar una vez que todos los consumidores migren a `PdfTypeDetectorPort`. | Wave 2.2 | Gate 3 | Low | RECLASIFICADO | `core/ast/router.py` con `PDFRouter` sigue en PROJECT_TREE. Requiere migrar consumidores. | Gate 4 |
| DF-11 | `core/extraction/ocr_providers/` contiene implementaciones concretas dentro del dominio. Migrar a `infra/extraction/providers/`. | Wave 2.2 | Gate 2 | High | RECLASIFICADO | Revisión tardía: era "Architecture Freeze Blocker" de Gate 2. Providers siguen en `core/`. Migración requiere refactor de frontera hexagonal. | Gate 4 |
| DF-12 | `LayoutBlockCollection` y `LayoutBlockDraft` pertenecen al legacy `DocumentLayoutBuilder` (zombi). `FlatASTBuilder` debe consumir `list[LayoutBlock]` directamente. | Wave 2.2 | Gate 3 | Medium | RECLASIFICADO | `LayoutBlockDraft` y `LayoutBlockCollection` siguen en `core/layout/models.py`. Refactor grande de `FlatASTBuilder`. | Gate 4 |
| DF-13 | El contrato de `TestRealPaperIntegration` asume capacidades estructurales superiores a las declaradas por `PyMuPDFProvider`. Decidir si el benchmark evalúa contrato común mínimo o capacidades específicas por provider. | Wave 2.2 | Gate 3 | Medium | RECLASIFICADO | Test actualizado para consultar `parser.capabilities` (Wave 2.2). Decisión de benchmark pendiente. | Gate 4 |
| DF-14 | `core/layout/classifier.py` (LogicalClassifier) es un stage zombi. Auditar heurísticas y migrar las útiles a `HeuristicLayoutClassifier`. | Wave 2.2 | Gate 3 | Low | RECLASIFICADO | `LogicalClassifier` sigue en PROJECT_TREE. `HeuristicLayoutClassifier` creado, pero zombi no eliminado. Requiere auditoría. | Gate 4 |
| DF-15 | `PyMuPDFProvider` no detecta tablas, ecuaciones ni imágenes. Para recall estructural completo, evaluar Docling o Nougat. | Wave 2.2 | Gate 3 | Medium | RECLASIFICADO | Limitación conocida. Requiere evaluación de Docling/Nougat (Fase 17-BIS benchmark). | Gate 4 |
| DF-16 | Dos taxonomías a sincronizar: `LayoutBlockType` y `ContentNodeType`. Considerar unificar o establecer correspondencia declarativa centralizada. | Wave 2.2 | Fase 17-BIS | Medium | RECLASIFICADO | Sin correspondencia declarativa centralizada. Mejora de mantenibilidad. | Gate 4 |
| DF-17 | `PyMuPDFProvider` posee capacidad nativa de extracción de imágenes (`type==1`), pero filtra exclusivamente texto vectorial (`type==0`). | Wave 2.2 | Gate 3 | Medium | RECLASIFICADO | Flujo de extracción de imágenes no implementado. Feature nueva. | Gate 4 |
| DF-18 | Introducir `ExecutionContext` como objeto de transporte unificado del plano de ejecución. | Wave 3.1 | Gate 4 | Medium | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-19 | Separar `build_pipeline()` en sub-fábricas para evitar God Factory. | Wave 3.1 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-20 | El dispatcher no debería resolver contexto. Debería recibir `ResolvedContext` ya resuelto. | Wave 3.1 | Gate 4 | Medium | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-21 | `ContextRegistry`, `RateLimitRegistry`, `MaterializationRegistry` y `TelemetryRegistry` comparten el mismo patrón. Evaluar infraestructura común. | Wave 3.1 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-22 | `RuntimeContextMappingProvider` podría exponer `get(context_id)` directamente en lugar de mappings. | Wave 3.1 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-23 | `apps/llm_workers/resilient_provider.py` es byte-identical a `cache_provider.py` (clase `CachedLLMProvider` duplicada). | Wave 3.2 | Gate 3 | Low | RESUELTO | Archivo eliminado en Wave 3.2. Confirmado: no aparece en PROJECT_TREE actualizado. | — |
| DF-24 | `GlobalCircuitBreaker` usa `deque()` en memoria local. Para multi-proceso real requeriría `CircuitBreakerStore`. | Wave 3.2 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-25 | `ReconcilerDaemon` y `CQRSReconciliationDaemon` son complementarios pero comparten responsabilidad de sweep. | Wave 3.2 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-26 | `apps/cli/main.py` y `apps/llm_workers/__main__.py` construyen el provider stack de forma duplicada. Extraer a `_build_provider_stack()`. | Wave 3.2 | Gate 4 | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-27 | Backend persistente para cuotas multi-proceso (SQLite WAL). | Wave 3.2 | Gate 4 | Medium | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-28 | `core/benchmark/runners/groq_runner.py` y `gemini_runner.py` contienen `DummyContextResolver`. Viola NADR-05 §5.1 R2. Alinear runners con pipeline de producción. | Gate 3 (auditoría) | Gate 4 | Medium | RECLASIFICADO | Hallazgo nuevo de Gate 3. DummyContextResolver en runners de benchmark. Alineación pendiente. | Gate 4 |
| GF-01 | Execution Plan Task 3.2.2 requiere "adaptador distribuido", pero ADR Maestro §4 prohíbe infraestructura distribuida durante Production Alignment. Implementation intentionally deferred due to governance conflict. | Wave 3.2 | Gate 4 | High | PENDING | Governance Finding. Se revisará en Gate 4 cuando se resuelva el conflicto normativo. | Gate 4 |

---

### 11.1 Gate 3 Exit Review (2026-08-07)

**Árbol de decisión aplicado (§5.5):**
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF | ¿Válido? | ¿Resoluble en Gate 3? | ¿Técnico? | Decisión | Motivo |
|----|----------|----------------------|-----------|----------|--------|
| DF-02 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Revisión tardía: Gate 2 cerrado sin Gate Exit Review. |
| DF-04 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Renombrado a `StructuralChunkBoundaryPolicy`. Requiere semántica de contexto cruzado. |
| DF-07 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | `DispatcherFactory` no existe. Mejora de mantenibilidad. |
| DF-10 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | `PDFRouter` sigue en tree. Requiere migrar consumidores. |
| DF-11 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Revisión tardía: era blocker de Gate 2. Migración hexagonal. |
| DF-12 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Refactor grande de `FlatASTBuilder`. |
| DF-13 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Test actualizado. Decisión de benchmark pendiente. |
| DF-14 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Zombi `LogicalClassifier` no eliminado. Requiere auditoría. |
| DF-15 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Limitación conocida. Requiere nuevo provider. |
| DF-16 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Unificación de taxonomías. |
| DF-17 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Flujo de imágenes no implementado. Feature nueva. |
| DF-23 | ❌ No | — | — | RESOLVED | Archivo eliminado en Wave 3.2. Confirmado en PROJECT_TREE. |
| DF-28 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Hallazgo nuevo. `DummyContextResolver` en runners de benchmark. |

**Resumen:**
- RESOLVED: 1 (DF-23)
- RECLASIFICADO → Gate 4: 12 (DF-02, 04, 07, 10, 11, 12, 13, 14, 15, 16, 17, 28)
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 1 (DF-28)
- Revisiones tardías documentadas: 2 (DF-02, DF-11)

