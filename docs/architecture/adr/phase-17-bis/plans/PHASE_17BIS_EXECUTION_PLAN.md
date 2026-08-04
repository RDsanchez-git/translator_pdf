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
| **1.1.1** | Definir configuración declarativa de CI Platform con Required Status Checks | NADR-10 §5.2 R6 | Low | — | TODO |
| **1.1.2** | Refactorizar `test_golden_parser.py`: eliminar tautologías, forzar matching Read-Only contra oráculo | NADR-10 §5.1 R2, R3; §5.2 R5 | High | 1.1.1 | TODO |
| **1.1.3** | Implementar mecanismo explícito de actualización de baseline; forzar `FileNotFoundError` en baselines ausentes | NADR-10 §5.1 R1, R4 | Medium | 1.1.2 | TODO |
| **1.1.4** | Forzar comparación completa de campos DTO en snapshot tests | NADR-10 §5.2 R13 | Medium | 1.1.2 | TODO |
| **1.1.5** | Eliminar sustitución artificial de componentes en integration tests | NADR-10 §5.2 R14 | High | 1.1.2 | TODO |
| **1.1.6** | Activar configuración declarativa de tooling (pyproject.toml) | NADR-10 §5.2 R7 | Low | 1.1.1 | TODO |
| **1.1.7** | Activar Daemon de Reconciliación CQRS vía configuración externa | NADR-10 §5.2 R8, R11, R12 | High | 1.1.1 | TODO |
| **1.1.8** | Alinear Benchmark con pipeline de producción (preparación) | NADR-10 §5.3 R9, R10 | Critical | 1.1.1 | TODO |

### 2.2 Wave 1.2 — Canonical AST & Deterministic Identity (NADR-01, NADR-03)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Eliminar `ast_deserializer.py`; rutear todas las cargas a `infra/serialization/ast_json.py` | NADR-01 §5.1 R1, R2 | Critical | 1.1.1 | TODO |
| **1.2.2** | Añadir regla de linter estático bloqueando instanciación directa de `ASTNode(**kwargs)` desde dicts no tipados | NADR-01 §5.1 R3, R4 | Low | 1.1.1 | TODO |
| **1.2.3** | Extraer lógica de chunking de `hashing.py` a `core/chunking/chunker.py` | NADR-03 §5.2 R1, R2, R3 | High | 1.2.1 | TODO |
| **1.2.4** | Refactorizar pre-imagen de `compute_ast_hash()` para excluir explícitamente `node_id` y metadata efímera | NADR-03 §5.1 R1, R2, R3 | Critical | 1.2.3 | TODO |
| **1.2.5** | Separar chunking de semantic hashing en responsabilidad modular | NADR-03 §5.2 R4, R5 | Medium | 1.2.3 | TODO |

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
| **2.1.1** | Limpiar `pipeline_factory.py`: eliminar mutaciones post-constructor DI; forzar inyección solo por constructor | NADR-11 §5.1 R1, R2, R3 | High | Gate 1 | TODO |
| **2.1.2** | Inyectar `DocumentLayoutValidator` y `PolymorphicValidationEngine` vía constructores | NADR-04 §5.1 R1, R2; §5.2 R1 | High | 2.1.1 | TODO |
| **2.1.3** | Eliminar `LegacyValidatorAdapter` y remover lógica legacy de fases 11/12 | NADR-04 §5.2 R2, R3, R4 | Medium | 2.1.2 | TODO |
| **2.1.4** | Configurar contrato `import-linter` prohibiendo fugas `core/` → `infra/` | NADR-11 §5.2 R1, R2 | Low | Gate 1 | TODO |
| **2.1.5** | Formalizar contrato explícito `DispatcherProtocol` | NADR-11 §5.3 R1, R2 | Medium | 2.1.1 | TODO |

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
| **3.1.1** | Eliminar `DummyContextResolver` e inyectar resolver real en orquestación CLI | NADR-05 §5.1 R1, R2, R3 | Medium | Gate 2 | TODO |
| **3.1.2** | Implementar invalidación de caché de contexto jerárquico | NADR-05 §5.2 R1, R2 | High | 3.1.1 | TODO |
| **3.1.3** | Eliminar slicing de array (`hard_fails[0]`) en `AsyncDispatcher` para permitir iteración multi-fallo | NADR-07 §5.2 R1, R2 | Medium | Gate 2 | TODO |
| **3.1.4** | Añadir detección de colisión de mutaciones dentro de `HealingPipeline` para seguridad de rollback atómico | NADR-07 §5.1 R1, R2, R3 | High | 3.1.3 | TODO |
| **3.1.5** | Forzar idempotencia de healing entre iteraciones consecutivas | NADR-07 §5.3 R1, R2 | Medium | 3.1.4 | TODO |

### 4.2 Wave 3.2 — Distributed Execution & CQRS Lineage (NADR-08)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Definir Protocol abstracto `RateLimitStore` en `core/ports/` | NADR-08 §5.1 R1, R2, R3 | Low | Gate 2 | TODO |
| **3.2.2** | Implementar adaptador distribuido para `TokenBucket` y `GlobalCircuitBreaker` | NADR-08 §5.1 R4; §5.2 R1, R2, R3 | Critical | 3.2.1 | TODO |
| **3.2.3** | Eliminar `"unknown_ast_hash"` del Reconciler; inyectar hash criptográfico de linaje real en `RematerializeTaskCommand` | NADR-08 §5.3 R1, R2, R3 | High | Gate 1 | TODO |
| **3.2.4** | Activar reconciliación CQRS vía configuración externa | NADR-08 §5.4 R1, R2, R3 | Medium | 3.2.3 | TODO |
| **3.2.5** | Componer RateLimitStore y CircuitBreaker en el stack de proveedores | NADR-08 §5.5 R1, R2 | Medium | 3.2.2 | TODO |

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

## 6. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas.

| Step | Operation | Environment | Linked Rules | Evidence |
|---|---|---|---|---|
| **MIG-01** | Corpus Resealing: ejecutar `tools/reseal_corpus.py` para regenerar baselines `.fingerprint.json` y `.ast.json` con el nuevo hash determinista | Local, CI | NADR-03 §5.1 R1, R2 | E-0.1-003 |
| **MIG-02** | Truncar caché materializada: `DELETE FROM materialized_cache` para purgar claves legacy inyectadas por `DummyContextResolver` | Staging, Prod | NADR-05 §5.1 R1, R2 | P4-05 |
| **MIG-03** | Desplegar KV Store distribuido: aprovisionar Redis (o backend equivalente) para `RateLimitStore` | Staging, Prod | NADR-08 §5.1 R4; §5.2 R1 | P4-03 |

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

| Gate | Rules Pending (derived) | Rules In Progress | Rules DONE | Gate Status |
|---|---|---|---|---|
| Gate 1 | count(§9 Gate 1 where Derived Status = PENDING) | count(... = IN PROGRESS) | count(... = DONE) | 🔴 Not Started |
| Gate 2 | count(§9 Gate 2 where Derived Status = PENDING) | count(... = IN PROGRESS) | count(... = DONE) | 🔴 Not Started |
| Gate 3 | count(§9 Gate 3 where Derived Status = PENDING) | count(... = IN PROGRESS) | count(... = DONE) | 🔴 Not Started |
| Gate 4 | count(§9 Gate 4 where Derived Status = PENDING) | count(... = IN PROGRESS) | count(... = DONE) | 🔴 Not Started |
| **TOTAL** | **sum of all gates** | — | — | 🔴 Not Started |

**Nota operativa:** Cada vez que una tarea pase a `DONE`, el `Derived Status` de sus reglas en §9 se actualiza y los contadores de este dashboard se recalculan automáticamente. El estado de una regla es siempre derivado del estado de la tarea que la implementa (§1.3).

---

## 9. TRACEABILITY APPENDIX — AUDIT BOARD

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la tarea que la implementa (§1.3). La relación Task → Rules ya está definida en los Gates (§2–§5); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence`

### 9.1 Gate 1 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-10 §5.2 R6 | PENDING | — |
| NADR-10 §5.1 R2 | PENDING | — |
| NADR-10 §5.1 R3 | PENDING | — |
| NADR-10 §5.2 R5 | PENDING | — |
| NADR-10 §5.1 R1 | PENDING | — |
| NADR-10 §5.1 R4 | PENDING | — |
| NADR-10 §5.2 R13 | PENDING | — |
| NADR-10 §5.2 R14 | PENDING | — |
| NADR-10 §5.2 R7 | PENDING | — |
| NADR-10 §5.2 R8 | PENDING | — |
| NADR-10 §5.2 R11 | PENDING | — |
| NADR-10 §5.2 R12 | PENDING | — |
| NADR-10 §5.3 R9 | PENDING | — |
| NADR-10 §5.3 R10 | PENDING | — |
| NADR-01 §5.1 R1 | PENDING | — |
| NADR-01 §5.1 R2 | PENDING | — |
| NADR-01 §5.1 R3 | PENDING | — |
| NADR-01 §5.1 R4 | PENDING | — |
| NADR-03 §5.2 R1 | PENDING | — |
| NADR-03 §5.2 R2 | PENDING | — |
| NADR-03 §5.2 R3 | PENDING | — |
| NADR-03 §5.1 R1 | PENDING | — |
| NADR-03 §5.1 R2 | PENDING | — |
| NADR-03 §5.1 R3 | PENDING | — |
| NADR-03 §5.2 R4 | PENDING | — |
| NADR-03 §5.2 R5 | PENDING | — |

### 9.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-11 §5.1 R1 | PENDING | — |
| NADR-11 §5.1 R2 | PENDING | — |
| NADR-11 §5.1 R3 | PENDING | — |
| NADR-04 §5.1 R1 | PENDING | — |
| NADR-04 §5.1 R2 | PENDING | — |
| NADR-04 §5.2 R1 | PENDING | — |
| NADR-04 §5.2 R2 | PENDING | — |
| NADR-04 §5.2 R3 | PENDING | — |
| NADR-04 §5.2 R4 | PENDING | — |
| NADR-11 §5.2 R1 | PENDING | — |
| NADR-11 §5.2 R2 | PENDING | — |
| NADR-11 §5.3 R1 | PENDING | — |
| NADR-11 §5.3 R2 | PENDING | — |
| NADR-02 §5.1 R1 | PENDING | — |
| NADR-02 §5.1 R2 | PENDING | — |
| NADR-02 §5.1 R3 | PENDING | — |
| NADR-02 §5.2 R1 | PENDING | — |
| NADR-02 §5.2 R2 | PENDING | — |
| NADR-02 §5.3 R1 | PENDING | — |
| NADR-10 §5.3 R10 (completa) | PENDING | — |

### 9.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence |
|---|---|---|
| NADR-05 §5.1 R1 | PENDING | — |
| NADR-05 §5.1 R2 | PENDING | — |
| NADR-05 §5.1 R3 | PENDING | — |
| NADR-05 §5.2 R1 | PENDING | — |
| NADR-05 §5.2 R2 | PENDING | — |
| NADR-07 §5.2 R1 | PENDING | — |
| NADR-07 §5.2 R2 | PENDING | — |
| NADR-07 §5.1 R1 | PENDING | — |
| NADR-07 §5.1 R2 | PENDING | — |
| NADR-07 §5.1 R3 | PENDING | — |
| NADR-07 §5.3 R1 | PENDING | — |
| NADR-07 §5.3 R2 | PENDING | — |
| NADR-08 §5.1 R1 | PENDING | — |
| NADR-08 §5.1 R2 | PENDING | — |
| NADR-08 §5.1 R3 | PENDING | — |
| NADR-08 §5.1 R4 | PENDING | — |
| NADR-08 §5.2 R1 | PENDING | — |
| NADR-08 §5.2 R2 | PENDING | — |
| NADR-08 §5.2 R3 | PENDING | — |
| NADR-08 §5.3 R1 | PENDING | — |
| NADR-08 §5.3 R2 | PENDING | — |
| NADR-08 §5.3 R3 | PENDING | — |
| NADR-08 §5.4 R1 | PENDING | — |
| NADR-08 §5.4 R2 | PENDING | — |
| NADR-08 §5.4 R3 | PENDING | — |
| NADR-08 §5.5 R1 | PENDING | — |
| NADR-08 §5.5 R2 | PENDING | — |

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