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
| **4.1.1** | Eliminar comandos sintéticos del adaptador de persistencia FSM; forzar orquestador como única fuente de eventos | NADR-09 §5.1 R1, R2, R3, R4, R5 | High | Gate 3 | DONE |
| **4.1.2** | Envolver I/O del compilador en directorios temporales efímeros; eliminar referencias a `os.getcwd()` | NADR-09 §5.2 R1, R2, R3, R4 | Critical | 4.1.1 | DONE |
| **4.1.3** | Forzar compilador como efecto lateral aislado sin mutación de dominio | NADR-09 §5.2 R5, R6, R7 | High | 4.1.2 | DONE |

> **Nota de implementación (Task 4.1.1):** `FSMStateStore` convertido a adaptador pasivo (`initialize`, `dispatch`, `load`, `get_current_version`). `TranslationPipeline` emite comandos explícitos.
> 
> **Nota de implementación (Task 4.1.2):** `DockerRunner` renombrado a `HostTectonicRunner` (DF-30). I/O completamente aislado en `TemporaryDirectory()`. `output_dir` obligatorio (sin default). Eliminados `os.getcwd()` y `tectonic_crash.log`. 6 tests de contrato.
> 
> **Nota de implementación (Task 4.1.3):** Verificado sin cambios. `HostTectonicRunner` no emite comandos FSM ni muta entidades del dominio. `AssemblerWorkerDaemon` es el propietario legítimo de la fase física.

### 5.2 Wave 4.2 — Token Estimation & Compilation Governance (NADR-06)

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Implementar adaptador de Tokenizer BPE compatible con proveedor; eliminar `FastWordEstimator` | NADR-06 §5.1 R1, R2, R3, R4 | High | Gate 3 | DONE |
| **4.2.2** | Refactorizar `LatexEscaper` para detectar fronteras matemáticas y bypasear escapado interno | NADR-06 §5.2 R1, R2, R3, R4 | Critical | Gate 3 | DONE |
| **4.2.3** | Re-cablear Daemon para rutear todos los ensamblados estrictamente a través de `CompilationService` (sin bypass, sin ad-hoc) | NADR-06 §5.3 R1, R2, R3, R4 | High | 4.2.2 | DONE |

> **Nota de implementación (Task 4.2.3):** Refactor arquitectónico profundo del plano de ensamblado.
> - Creado `core/compiler/ports.py` con `ASTProviderProtocol` (evita import circular).
> - Creado `core/compiler/assembly_context.py` con `AssemblyExecutionContext` (VO inmutable de evidencia validada).
> - Creado `core/compiler/context_resolver.py` con `CQRSAssemblyContextResolver` (único punto de acceso al Execution Plane).
> - `DocumentAssembler.assemble()` migrado de `(job_id, dispatch_result)` a `(context: AssemblyExecutionContext)`. El Assembler solo decide política, NO reconstruye contenido.
> - `CompilationService.compile_document()` migrado de `(job_id, ast_hash, dispatch_result)` a `(context: AssemblyExecutionContext)`. Única materialización de RenderUnits.
> - `TranslationPipeline` elimina `AssemblerProtocol` y Fase 5. Termina en `MarkAssemblyReadyCommand` (handoff al Execution Plane).
> - `SummaryBuilder.build()` separado de `DocumentAssemblyDecision`. `TranslationAuditSummary` describe exclusivamente el Dispatch Plane.
> - `AssemblerWorkerDaemon` usa `CQRSAssemblyContextResolver` + `CompilationService`. Sin reconstrucción ad-hoc.
> - `ASTRegistry.get_document_ast()` agregado como contrato público.
> - Semántica OMIT excluida del contexto de ensamblado. Validación topológica sobre AST completo antes del filtro.
> - `AssemblyReport` resemantizado: `total_nodes` + `missing_projection_nodes` (sin ambigüedad con fallos de dispatch).
> - 274 tests passed, 0 errors pyright.

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
| Gate 1 | 2026-08-04 | 26/26 | pyright 0 errors. AST hashing semántico confirmado. |
| Gate 2 | 2026-08-05 | 20/20 | fitz eliminado. Parser legacy eliminado. |
| Gate 3 | 2026-08-07 | 25/27 | Wave 3.1+3.2 completadas. 2 reglas diferidas por GF-01. |
| Gate 4 | 2026-08-11 | 24/24 | Wave 4.1 COMPLETADA (12 reglas NADR-09). Wave 4.2 COMPLETADA: Task 4.2.1 (4 reglas NADR-06 §5.1), Task 4.2.2 (4 reglas NADR-06 §5.2), Task 4.2.3 (4 reglas NADR-06 §5.3). GF-01 pendiente (2 reglas de Gate 3 diferidas). |

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
| Gate 4 | 24 | 0 | 0 | ✅ COMPLETED |
| **TOTAL** | **95** | **2** | **0** | 🟡 GF-01 pendiente |

**Nota operativa:** Gate 4 COMPLETADO con 24/24 reglas propias. Wave 4.1: 12 reglas NADR-09 (Tasks 4.1.1-4.1.3). Wave 4.2: 12 reglas NADR-06 (Tasks 4.2.1-4.2.3). Las 2 reglas DEFERRED (NADR-08 §5.1 R3, R4) pertenecen a Gate 3 y están diferidas por GF-01. No son reglas de Gate 4.

**Nota operativa:** Las 2 reglas DEFERRED de Gate 3 (NADR-08 §5.1 R3, R4) están explícitamente diferidas por GF-01 (conflicto normativo). Se resolverán en Gate 4. No constituyen un fallo del Gate; son una decisión de gobernanza documentada.

**Nota operativa:** Gate 4 tiene 5 reglas DONE (Task 4.1.1: NADR-09 §5.1 R1-R5) y 19 reglas PENDING (Tasks 4.1.2, 4.1.3, 4.2.1-4.2.3). La Task 4.1.1 fue implementada con enfoque contract-first (A.1.a contrato → A.1.b tests → C.1/C.2 implementación).

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
| NADR-09 §5.1 R1 | DONE | Task 4.1.1 — `TranslationPipeline` emite comandos explícitos (`StartParsingCommand`, `StartProcessingCommand`, `MarkAssemblyReadyCommand`) |
| NADR-09 §5.1 R2 | DONE | Task 4.1.1 — `FSMStateStore` es adaptador pasivo (`initialize`, `dispatch`, `load`, `get_current_version`). Sin `save(job)`, sin síntesis |
| NADR-09 §5.1 R3 | DONE | Task 4.1.1 — `PipelineStep` sincronizado 1:1 con `DocumentState` (9 miembros). `DefaultPipelineStateProjection` en `core/pipeline/state_projection.py` |
| NADR-09 §5.1 R4 | DONE | Task 4.1.1 — `FSMValidator.validate()` es la única autoridad de legalidad. Sin bypass desde adaptadores |
| NADR-09 §5.1 R5 | DONE | Task 4.1.1 — `STEP_TO_COMMAND_CLASS`, Intercepción A (MarkAssemblyReady), Intercepción B (MarkCompilationReady+StartCompilation) eliminados |
| NADR-09 §5.2 R1 | PENDING | Task 4.1.2 — `apps/compiler/docker_runner.py` escribe en `os.getcwd()` |
| NADR-09 §5.1 R1 | DONE | Task 4.1.1 — Orquestador emite comandos explícitos |
| NADR-09 §5.1 R2 | DONE | Task 4.1.1 — `FSMStateStore` pasivo, sin síntesis |
| NADR-09 §5.1 R3 | DONE | Task 4.1.1 — `PipelineStep` sincronizado con `DocumentState` |
| NADR-09 §5.1 R4 | DONE | Task 4.1.1 — `FSMValidator` como única autoridad |
| NADR-09 §5.1 R5 | DONE | Task 4.1.1 — Sin mecanismos de auto-promoción |
| NADR-09 §5.2 R1 | DONE | Task 4.1.2 — `HostTectonicRunner` en `TemporaryDirectory` |
| NADR-09 §5.2 R2 | DONE | Task 4.1.2 — `cwd=tmp` en `subprocess.run()` |
| NADR-09 §5.2 R3 | DONE | Task 4.1.2 — Artefactos intermedios en sandbox |
| NADR-09 §5.2 R4 | DONE | Task 4.1.2 — `os.getcwd()` eliminado del runner |
| NADR-09 §5.2 R5 | DONE | Task 4.1.3 — Runner no modifica FSM (verificado) |
| NADR-09 §5.2 R6 | DONE | Task 4.1.3 — Runner no modifica entidades del dominio (verificado) |
| NADR-09 §5.2 R7 | DONE | Task 4.1.3 — Efecto lateral aislado (resuelto en 4.1.2) |
| NADR-06 §5.1 R1 | DONE | Task 4.2.1 — `ExactBPEEstimator` (tiktoken cl100k_base) como estimador canónico |
| NADR-06 §5.1 R2 | DONE | Task 4.2.1 — `FastWordEstimator` eliminado. Sin fallback heurístico |
| NADR-06 §5.1 R3 | DONE | Task 4.2.1 — BPE real refleja densidad de sub-palabras del contenido científico |
| NADR-06 §5.1 R4 | DONE | Task 4.2.1 — `ExactBPEEstimator` inyectable vía `TokenEstimatorProtocol` |
| NADR-06 §5.2 R1 | DONE | Task 4.2.2 — `TextRenderStrategy` preserva `$...$` y `$$...$$` intactas |
| NADR-06 §5.2 R2 | DONE | Task 4.2.2 — Escapado consciente del contexto (mask → escape → restore) |
| NADR-06 §5.2 R3 | DONE | Task 4.2.2 — Tokens Unicode inmunes al escape, sin sustitución ciega |
| NADR-06 §5.2 R4 | DONE | Task 4.2.2 — 18 tests + 4 de regresión verifican la estrategia |
| NADR-06 §5.3 R1 | DONE | Task 4.2.3 — `AssemblerWorkerDaemon` rutea exclusivamente a través de `CompilationService`. Sin bypass, sin reconstrucción ad-hoc |
| NADR-06 §5.3 R2 | DONE | Task 4.2.3 — `TranslationPipeline` elimina `AssemblerProtocol`. Ensamblado físico delegado al `AssemblerWorkerDaemon` vía FSM |
| NADR-06 §5.3 R3 | DONE | Task 4.2.3 — `CQRSAssemblyContextResolver` valida topología, unicidad de node_id, semántica OMIT y proyecciones CURRENT antes del ensamblado |
| NADR-06 §5.3 R4 | DONE | Task 4.2.3 — `DocumentAssembler` aplica `AssemblyPolicy` (tolerance_ratio, allow_fallback). Decisiones desde políticas del dominio |

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
| DF-29 | `core/execution/state_mapping.py` contiene `FSM_TO_PIPELINE_RESUME` (mapeo inverso DocumentState → PipelineStep) que introduce dependencia `core.execution → core.pipeline`. Viola la dirección de dependencia correcta (pipeline → execution). Requiere decisión arquitectónica: mover a `core/pipeline/`, extraer protocolo de recovery, o documentar como excepción. | Task 4.1.1 (auditoría) | Gate 4 | Low | PENDING | Decisión arquitectónica pendiente. No bloquea Task 4.1.1 porque `FSM_TO_PIPELINE_RESUME` solo se usa en `OnDemandResumeManager`. | Gate 4 |
| DF-30 | `apps/compiler/docker_runner.py` tiene clase `DockerRunner` pero invoca `tectonic` nativamente. Nomenclatura engañosa. | Task 4.1.1 (auditoría) | Gate 4 (Task 4.1.2) | Low | RESUELTO | Renombrado a `HostTectonicRunner` en Task 4.1.2. Nomenclatura veraz (NADR-09 §5.2 R9). | — |
| DF-31 | `get_assemblable_chunks()` filtra por `expected_node_ids` en SQL (`WHERE node_id IN (...)`). La detección de proyecciones huérfanas (`materialized - expected`) no es observable desde el port actual. Requiere consulta de integridad separada o modificación del contrato del port. | Task 4.2.3 (auditoría) | Gate 4 Exit Review | Low | PENDING | Se revisará en Gate 4 Exit Review | Gate 4 |
| DF-33 | Verificación de consumidores de `decision.document` y `failed_outcomes` completada durante pre-implementación. Todos los consumidores estaban dentro del alcance de la migración (SummaryBuilder, TranslationPipeline, tests). Sin consumidores ocultos. | Task 4.2.3 (pre-implementación) | — | — | RESUELTO | Grep de consumidores confirmó alcance completo. Migración ejecutada sin impacto no previsto. | — |
| DF-34 | `ProfileStore` requiere backend durable para el `AssemblerWorkerDaemon`. `InMemoryProfileStore` no sobrevive crash del proceso. El daemon necesita recuperar `InferredDocumentProfile` desde persistencia para compilar documentos después de un restart. | Task 4.2.3 (auditoría) | Gate 4 Exit Review / Fase 18 | Medium | PENDING | Condición: Recovery Gate (Gate I) no se declara PASS hasta resolver. No bloquea Tasks 4.2.1-4.2.3. | Gate 4 |

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


### 11.3 Gate 4 Partial Exit Review — Wave 4.2 (2026-08-08)

**Nota:** Gate 4 alcanza 24/24 reglas propias DONE. GF-01 (2 reglas de Gate 3) sigue pendiente como Governance Finding.

**Árbol de decisión aplicado (§5.5):**

| DF | ¿Válido? | ¿Resoluble en Wave 4.2? | ¿Técnico? | Decisión | Motivo |
|----|----------|------------------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | `core/benchmark/__main__.py` sigue con hashing propio. |
| DF-18 | ✅ Sí | ⚠️ Parcial | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | `AssemblyExecutionContext` es un paso hacia `ExecutionContext` unificado, pero no lo reemplaza. |
| DF-31 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | Hallazgo nuevo. Detección de orphans requiere modificación del port. |
| DF-33 | ❌ No | — | — | RESUELTO | Grep de consumidores confirmó alcance completo. |
| DF-34 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review / Fase 18 | Hallazgo nuevo. ProfileStore durable. Condición de Recovery Gate. |

**Resumen Wave 4.2:**
- RESUELTO: 1 (DF-33)
- RECLASIFICADO → Gate 4 Exit Review: 3 (DF-01, DF-18, DF-31)
- RECLASIFICADO → Gate 4 Exit Review / Fase 18: 1 (DF-34)
- Nuevos hallazgos registrados: 2 (DF-31, DF-34)

**Decisiones arquitectónicas congeladas en Wave 4.2:**

| Decisión | Task | Justificación |
|----------|------|---------------|
| `ExactBPEEstimator` como estimador canónico único | 4.2.1 | NADR-06 §5.1. Sin fallback heurístico. |
| `TextRenderStrategy` con protección local de math (tokens Unicode) | 4.2.2 | NADR-06 §5.2. `InlineMathProtector` no protege `$$...$$` ni sobrevive al escape. |
| `DispatchResult` deja de ser contrato inter-stage | 4.2.3 | NADR-06 §5.3. Objeto efímero del proceso de dispatch. |
| `AssemblyExecutionContext` como frontera Execution Plane → Compilation Plane | 4.2.3 | VO inmutable de evidencia validada. Resolver valida, Assembler decide, Service materializa. |
| `TranslationPipeline` termina en `MarkAssemblyReadyCommand` | 4.2.3 | NADR-09 §5.1. Separación de planos lógico y físico. |
| `TranslationAuditSummary` describe solo Dispatch Plane | 4.2.3 | `AssemblyReport` describe Assembly Plane. Sin mezcla de telemetría. |
| `ProfileStore` canónico (`core/document_profile/ports.py`) | 4.2.3 | Eliminado `ProfileStoreProtocol` duplicado en `service.py`. |
| Validación topológica sobre AST completo antes del filtro OMIT | 4.2.3 | Gaps de OMIT son legales. La continuidad se verifica sobre el AST completo. |

**Lecciones aprendidas Wave 4.2:**
- El enfoque audit-first (census → diseño → implementación) previno 3 bloqueadores arquitectónicos (import circular, semántica OMIT, doble reconstrucción)
- La separación de planos (Resolver valida / Assembler decide / Service materializa) eliminó la doble materialización de contenido
- `DispatchResult` como contrato inter-stage era la raíz del acoplamiento entre el pipeline lógico y el daemon físico
- Los tests que dependían del ensamblado lógico quedaron obsoletos correctamente (el ensamblado es asíncrono)


## 12. GATES EXIT REVIEWS — FINDINGS REGISTER & EVIDENCE LOG

**Las tablas fueron construidas en base al `docs\architecture\adr\phase-17-bis\reports`. Para más detalles consultar ese archivo. **

## Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 6 | DF-03, DF-07, DF-20, DF-21, DF-22, GF-01 |
| `RESOLVED — DELETE` | 4 | DF-10, DF-14, DF-25, DF-29 |
| `RESOLVED` | 2 | DF-13, DF-16 |
| `IMPLEMENTATION_REQUIRED` | 7 | DF-01, DF-02, DF-11, DF-12, DF-26, DF-27, DF-28 |
| `RECLASSIFIED_FUTURE_PHASE` | 6 | DF-04, DF-17, DF-18, DF-24, DF-34 |
| `REVIEW_REQUIRED` | 2 | DF-19, H-11-A |
| `ACCEPTED_LIMITATION` | 2 | DF-15, DF-31 |

## Tabla consolidada final

| DF | Estado | Decisión |
|----|--------|----------|
| GF-01 | `CLOSED — NORMATIVE COMPATIBILITY ESTABLISHED` | Reconciliación normativa |
| DF-01 | `IMPLEMENTATION_REQUIRED — ACCIÓN PENDIENTE` | Identidad semántica en Benchmark |
| DF-02 | `IMPLEMENTATION_REQUIRED — ALCANCE ACOTADO` | Patrón defensivo `hasattr` |
| DF-03 | `CLOSED (NAR)` | Ya cerrado en Gate 3 |
| DF-04 | `RECLASSIFIED_FUTURE_PHASE` | AST sin contexto cruzado |
| DF-07 | `CLOSED (NAR)` | Dependencias legítimas |
| DF-10 | `RESOLVED — DELETE` | Eliminar 3 archivos |
| DF-11 | `IMPLEMENTATION_REQUIRED — HEXAGONAL_BOUNDARY` | Migrar providers a infra/ |
| DF-12 | `IMPLEMENTATION_REQUIRED — ALCANCE POR DEFINIR` | Zombis + migración FlatASTBuilder |
| DF-13 | `RESOLVED` | Capacidades por provider |
| DF-14 | `RESOLVED — DELETE` | Eliminar LogicalClassifier |
| DF-15 | `ACCEPTED_LIMITATION` | Limitación de PyMuPDF |
| DF-16 | `RESOLVED — ACCEPTED SEPARATION` | Taxonomías ortogonales |
| DF-17 | `RECLASSIFIED_FUTURE_PHASE` | Asset management no existe |
| DF-18 | `RECLASSIFIED_FUTURE_PHASE` | AssemblyExecutionContext ≠ ExecutionContext unificado |
| DF-19 | `REVIEW_REQUIRED` | God Factory parcial |
| DF-20 | `CLOSED (NAR)` | Dispatcher delega vía DI |
| DF-21 | `CLOSED (NAR)` | Registries de bounded contexts distintos |
| DF-22 | `CLOSED (NAR)` | Snapshot intencional |
| DF-24 | `RECLASSIFIED_FUTURE_PHASE` | CB en memoria suficiente |
| DF-25 | `RESOLVED — DELETE` | CQRSReconciliationDaemon zombie |
| DF-26 | `IMPLEMENTATION_REQUIRED — EXTRAER PROVIDER STACK FACTORY` | 3 puntos + divergencia QuotaManager |
| DF-27 | `IMPLEMENTATION_REQUIRED — ALCANCE POR DEFINIR` | RateLimitStore sin implementación |
| DF-28 | `IMPLEMENTATION_REQUIRED — ALCANCE ACOTADO` | Divergencia benchmark/producción |
| DF-29 | `RESOLVED — DELETE ZOMBIE + REMOVE IMPORT` | Eliminados dicts zombies + import |
| DF-31 | `ACCEPTED_LIMITATION` | Port no detecta huérfanos. Funcionalmente correcto |
| DF-34 | `RECLASSIFIED_FUTURE_PHASE` | Recovery gap. Destino: Recovery Gate / Fase 18 |
| H-11-A | `REVIEW_REQUIRED` | measure_density.py |


## 13. RESULTADOS FINALES DE DFs 

### BATCH 1 — Limpieza de Código Zombie (Completado)

**Fecha de ejecución:** 2026-08-16  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-10** | `RESOLVED — DELETE` | DELETE 3 archivos | `core/ast/router.py`,`core/ast/ports.py``infra/adapters/pdf_router.py` | ✅ 0 imports✅ Pyright clean✅ Tests green |
| **DF-14** | `RESOLVED — DELETE` | DELETE 1 archivo | `core/layout/classifier.py` | ✅ 0 imports✅ Pyright clean✅ Tests green |
| **DF-25** | `RESOLVED — DELETE` | DELETE 1 archivo | `runtime/reconciliation.py` | ✅ 0 imports✅ Pyright clean✅ Tests green |
| **DF-29** | `RESOLVED — DELETE ZOMBIE` | DELETE dicts zombies + import | `core/execution/state_mapping.py`(eliminados: `PIPELINE_TO_FSM`, `FSM_TO_PIPELINE_RESUME`, imports innecesarios) | ✅ 0 imports de core.pipeline✅ 0 referencias a dicts✅ Pyright clean✅ Tests green |

---

### Extensión Post-Batch 1 — Hallazgo Post-DF-29 (Completado)

**Fecha de ejecución:** 2026-08-16  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped | state_mapping.py eliminado

| Acción | Detalle |
|--------|---------|
| Mover `RecoveredJobSnapshot` | De `core/execution/state_mapping.py` → `core/execution/models.py` |
| Eliminar archivo con nombre engañoso | `core/execution/state_mapping.py` (Test-Path → False) |
| Actualizar imports | `core/pipeline/state_store.py:12` + `tests/unit/test_pipeline_fsm_emission.py:18` |
| Cero referencias a `state_mapping` en el proyecto | ✅ Confirmado |
| Bounded context preservado | Clase permanece en `core/execution/` (dirección de dependencia intacta) |

**Justificación de la extensión:**  
Tras eliminar los dicts zombies en DF-29, `state_mapping.py` quedó con una sola clase cuyo nombre ya no reflejaba su contenido. Mover `RecoveredJobSnapshot` a `core/execution/models.py` (donde ya residen `ProcessingStage`, `ChunkLifecycle`, `FailureType`) elimina el archivo con nombre engañoso sin violar la dirección de dependencia pipeline → execution.

---

### Métricas acumuladas post-Batch 1 + extensión

| Métrica | Valor |
|---------|-------|
| Archivos eliminados | 6 (5 en Batch 1 + 1 en extensión) |
| Archivos reubicados | 1 clase movida a `core/execution/models.py` |
| Tests ejecutados | 274 passed, 5 skipped (baseline mantenida) |
| Errores de tipo estático | 0 |
| Warnings | 1 (google.generativeai deprecated, no relacionado) |
| Dependencias huérfanas detectadas | 0 |

---

### Batches Pendientes

| Batch | DFs Incluidos | Estado |
|-------|--------------|--------|
| **Batch 2** | DF-11 (migrar providers a infra/) + DF-12-A (eliminar DocumentLayoutBuilder) | ⏳ Siguiente |
| **Diseño DF-27** | Especificación de SQLiteRateLimitStore | ⏳ Pendiente |
| **Batch 3** | DF-26 (extraer provider stack factory) + DF-27 (con diseño) | ⏳ Pendiente |
| **Auditoría DF-12-B** | Evaluar stages del layout (veredicto propio) | ⏳ Pendiente |
| **Batch 4** | DF-02 (eliminar hasattr) | ⏳ Pendiente |
| **Diseño DF-01** | Especificación de identidad semántica en benchmark | ⏳ Pendiente |
| **Batch 5** | DF-01 (con diseño) + DF-28 (alinear runners con Composition Root) | ⏳ Pendiente |
| **Reevaluación** | DF-19, DF-12-C/D/E, H-11-A | ⏳ Pendiente |

---

### Notas de Gobernanza

**Criterio de cierre por batch:**  
Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest -q → baseline mantenida: 274 passed, 5 skipped)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

**Batch 1 + extensión completados sin bloqueos:**  
Todos los DFs ejecutados eran de bajo riesgo (eliminación de código zombie sin dependencias activas). La extensión post-DF-29 se ejecutó como acción documentada y validada independiente.

**Próximo hito — Batch 2:**
- **DF-11:** Migración de `core/extraction/ocr_providers/` a `infra/extraction/providers/` (pymupdf, tesseract, docling). Requiere actualizar imports en provider_factory.py, generate_candidates.py, generate_pymupdf_candidate.py, test_docling_provider.py, test_pipeline_factory.py.
- **DF-12-A:** Eliminar `core/layout/builder.py` (DocumentLayoutBuilder, 0 instancias confirmadas en Paso 0).
- **H-11-A** queda excluido del Batch 2 conforme a la corrección normativa de la revisión de gobernanza: es `REVIEW_REQUIRED`, no `IMPLEMENTATION_REQUIRED`.
- **PROJECT_TREE** actualizado para reflejar los cambios del Batch 1 y la extensión post-DF-29.

---

### Estado del Exit Review: ✅ CERRADO

| Categoría | Cantidad |
|-----------|----------|
| Total de DFs analizados | 27 (25 DF + GF-01 + H-11-A) |
| DFs resueltos en Batch 1 | 4 |
| Extensión post-DF-29 | ✅ Completada |
| DFs pendientes de implementación | 7 (DF-01, DF-02, DF-11, DF-12, DF-26, DF-27, DF-28) |
| DFs pendientes de revisión | 2 (DF-19, H-11-A) |
| DFs cerrados sin acción | 16 |


### Batch 2 — Migración Hexagonal + Limpieza de Zombis (Completado)

**Fecha de ejecución:** 2026-08-16  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-11** | `RESOLVED — MOVE` | MOVE 3 providers de `core/` a `infra/` | `core/extraction/ocr_providers/pymupdf_provider.py` → `infra/extraction/providers/`<br>`core/extraction/ocr_providers/tesseract_provider.py` → `infra/extraction/providers/`<br>`core/extraction/ocr_providers/docling_provider.py` → `infra/extraction/providers/` | ✅ 0 infra imports en core/ (excepto H-11-A)<br>✅ Pyright clean<br>✅ Tests green |
| **DF-12-A** | `RESOLVED — DELETE` | DELETE `DocumentLayoutBuilder` + corregir import | `core/layout/builder.py` eliminado<br>`apps/bootstrap/pipeline_factory.py:43` corregido (import canónico) | ✅ 0 instancias de DocumentLayoutBuilder<br>✅ Pyright clean<br>✅ Tests green |

**Correcciones adicionales durante ejecución:**
- `tests/unit/test_docling_provider.py`: Actualizado `@patch` con nueva ruta de módulo
- `tools/benchmark_archive/run_calibration_v1.py`: Agregado `# pyright: ignore` (archivo archivado, DF-03 NAR)

**Hallazgo registrado (pendiente de revisión):**
- **H-11-A:** `core/metrics/measure_density.py` importa `fitz` directamente
- Clasificación: `REVIEW_REQUIRED`
- Acción: Determinar si es métrica de dominio o inspección física antes de decidir MOVE/DELETE

**Métricas post-batch:**
- Archivos movidos: 3 (providers OCR)
- Archivos eliminados: 1 (DocumentLayoutBuilder)
- Imports corregidos: 5 (4 en consumidores + 1 en test)
- Tests ejecutados: 274 passed, 5 skipped
- Errores de tipo estático: 0

**Estructura hexagonal correcta:**
- `core/extraction/provider.py` → Puerto abstracto (permanece en dominio)
- `infra/extraction/providers/` → Adaptadores concretos (movidos desde core/)
- `core/` libre de imports de infraestructura (excepto H-11-A pendiente)


### Batch 3 — Composición y Wiring (Completado)

**Fecha de ejecución:** 2026-08-17  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-26** | `RESOLVED — FACTORY EXTRACTION` | Extraer `build_provider_stack()` | `apps/bootstrap/provider_stack_factory.py` (nuevo)<br>`apps/llm_workers/rate_limiter.py` (agregar `store` param)<br>`apps/cli/main.py` (usar factory)<br>`apps/llm_workers/__main__.py` (usar factory)<br>`runtime/engine.py` (usar factory + agregar cache/CB) | ✅ 0 construcciones inline<br>✅ Factory centralizada<br>✅ Pyright clean<br>✅ Tests green |
| **DF-27** | `RESOLVED — SQLITE_RATE_LIMIT_STORE` | Implementar persistencia de cuotas | `infra/resilience/sqlite_rate_limit_store.py` (nuevo)<br>`core/resilience/rate_limit_store.py` (Protocol sync + docstring epoch)<br>`apps/llm_workers/rate_limiter.py` (_restore/_persist epoch↔monotonic)<br>`apps/cli/main.py` (inyectar store)<br>`apps/llm_workers/__main__.py` (inyectar store)<br>`runtime/engine.py` (inyectar store) | ✅ Store creado<br>✅ Protocol sync<br>✅ Conversión epoch↔monotonic<br>✅ 3 entry points inyectan store<br>✅ 3 entry points cierran rl_conn<br>✅ Pyright clean<br>✅ Tests green |

**Cambios normativos aplicados:**
- **NADR-08 §5.1 R1 cumplido:** Puerto abstracto `RateLimitStore` implementado
- **NADR-08 §5.1 R2 cumplido:** Operaciones atómicas `load()`/`save()` con SQLite WAL
- **NADR-08 §5.1 R3 cumplido:** Estado persistente en SQLite (no exclusivamente en RAM)
- **NADR-08 §5.1 R4 cumplido:** Backend seleccionado desde Composition Root (entry points)
- **GF-01 satisfecho:** Backend local SQLite WAL, sin infraestructura distribuida

**Decisiones de diseño clave:**
- **epoch↔monotonic:** `BucketState.last_update` almacena `time.time()` (epoch). `QuotaManager` convierte al cargar/guardar para compatibilidad con `TokenBucket` que usa `time.monotonic()`
- **Sin `close()` en SQLiteRateLimitStore:** Coherente con patrón DI de `infra/db/` (8 repos). El caller cierra la conexión
- **Factory NO crea store:** Caller decide si inyectar persistencia. `rate_limit_store=None` = memoria local (backward compatible, testeable)
- **PRAGMA WAL idempotente:** Coherente con patrón de `CachedLLMProvider.initialize()`

**Métricas acumuladas Batch 3:**
- Archivos creados: 2 (`provider_stack_factory.py`, `sqlite_rate_limit_store.py`)
- Archivos modificados: 6 (rate_limit_store.py, rate_limiter.py, 3 entry points, pipeline_factory.py indirecto)
- Tests ejecutados: 274 passed, 5 skipped
- Errores de tipo estático: 0



### Batch 4 — Limpieza de Zombis Layout + Eliminación de Patrones Defensivos (Completado)

**Fecha de ejecución:** 2026-08-17  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-12-B** | `RESOLVED — DELETE` | Eliminar 6 stages zombis del layout pipeline | `core/layout/detector.py` (SpatialAnalyzer) — eliminado<br>`core/layout/identity.py` (BlockIdentityGenerator) — eliminado<br>`core/layout/merger.py` (SpatialMerger) — eliminado<br>`core/layout/normalizer.py` (CoordinateNormalizer) — eliminado<br>`core/layout/reading_order.py` (ReadingOrderResolver) — eliminado<br>`core/layout/base.py` (LayoutStage, PipelineContext, PipelineConfig, ProviderDescriptor, MergePolicy, ReadingOrderPolicy) — eliminado | ✅ 6 archivos eliminados<br>✅ 3 archivos preservados (models.py, classification.py, validator.py)<br>✅ 0 referencias huérfanas<br>✅ Pyright clean<br>✅ Tests green |
| **DF-02-A** | `RESOLVED — REFACTORED` | Eliminar `hasattr(node.node_type, "value")` en producción | `core/benchmark/__main__.py:93`<br>`core/normalization/classifier.py:146`<br>`core/normalization/pipeline.py:44` | ✅ Acceso directo a `.value`<br>✅ Pyright clean<br>✅ Tests green |
| **DF-02-B** | `RESOLVED — REFACTORED` | Eliminar `hasattr` en tooling de benchmark | `tools/evaluation/topology/fingerprint.py:19` | ✅ Acceso directo a `.value`<br>✅ Pyright clean<br>✅ Tests green |

---

#### DF-12-B: Eliminación de Stages Zombis del Layout Pipeline

**Evidencia de auditoría:**
- Los 5 stages tenían **0 instancias** y **0 consumidores externos** en todo el proyecto
- `base.py` era un zombi derivado: sus 6 clases solo eran consumidas por los 5 stages eliminados
- `DocumentLayoutBuilder` (orquestador) fue eliminado previamente en DF-12-A (Batch 2)
- El benchmark NO usa estos stages — usa `LayoutBlockDraft`/`LayoutBlockCollection` como DTOs hacia `FlatASTBuilder`, sin invocar ningún stage

**Archivos preservados en `core/layout/`:**
- `models.py` — `LayoutBlockDraft` + `LayoutBlockCollection` (activos, consumidos por FlatASTBuilder)
- `classification.py` — `HeuristicLayoutClassifier` (activo, consumido por PyMuPDFProvider)
- `validator.py` — `DocumentLayoutValidator` (activo, consumido por pipeline_factory)

**DF-12-C/D/E diferido:**
La migración de `FlatASTBuilder` a consumir `list[LayoutBlock]` directamente (eliminando la capa `LayoutBlockDraft`/`LayoutBlockCollection`) es un refactor de contrato que afecta 5+ archivos activos. Requiere ADR de diseño propio y se difiere a un batch futuro.

---

#### DF-02: Eliminación de Patrón `hasattr` Defensivo

**Justificación técnica:**
- `ASTNode.node_type` está tipado como `ContentNodeType` (Enum puro, sin Union)
- Pydantic garantiza el tipo post-construcción — si el tipo fuera incorrecto, fallaría con `ValidationError`
- El fallback `else str(node.node_type)` violaba ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos)
- Método de edición: manual (Opción A) para preservar encoding original y evitar BOM de PowerShell

**Verificación previa del tipo:**
- `ASTNode.node_type: ContentNodeType` — tipo puro, sin Union, sin Optional
- `ContentNodeType(str, Enum)` — Enum con 11 miembros, `.value` siempre existe

---


### DF-01 — Identidad Semántica y Centralización Criptográfica (Parcial)

**Fecha de ejecución:** 2026-08-19  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| Sub-DF | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|--------|--------------|------------------|-------------------|------------|
| **DF-01-A** | `RESOLVED — REFACTORED` | Migrar `hashlib.sha256()` directo a funciones canónicas de `core/shared/crypto.py` | `core/shared/crypto.py` (nueva función pura `compute_sha256_stream`)<br>`core/benchmark/__main__.py` (2 puntos, 1 con streaming)<br>`core/benchmark/runners/gemini_runner.py`<br>`core/benchmark/runners/groq_runner.py`<br>`core/benchmark/corpus/services.py`<br>`core/benchmark/orchestrator.py` (streaming) | ✅ 0 `hashlib` directo en benchmark<br>✅ 0 `.read_bytes()` (soporte para libros 500+ págs)<br>✅ Pyright clean<br>✅ Tests green |

**Decisiones de diseño clave:**
- **Streaming para libros extensos:** Se agregó `compute_sha256_stream(chunks: Iterable[bytes])` como función pura (Functional Core). El I/O de lectura por chunks se aísla en el caller (Imperative Shell). Esto previene cargar PDFs de 200-500 MB en RAM.
- **Centralización criptográfica:** Todo el hashing del benchmark pasa ahora por el punto canónico `core/shared/crypto.py` (ENGINEERING_PRINCIPLES §III).

**Reclasificación de sub-hallazgos de DF-01:**
| Sub-DF | Estado Final | Justificación |
|--------|--------------|---------------|
| **DF-01-A** | `RESOLVED` | Centralización criptográfica completada. |
| **DF-01-B** | `CLOSED — NAR` | Falso positivo: `node_sha` por chunk y `compute_ast_hash()` por documento tienen propósitos ortogonales. |
| **DF-01-C** | `DEFERRED — FASE 2/3` | Requiere ADR de diseño futuro sobre el linaje de identidad semántica en la Scientific Baseline. |
| **DF-01-D** | `CLOSED — NAR` | Agregar `ast_hash` a `DocumentFingerprint` violaría la separación de dimensiones del ADR Maestro §3 (Integridad física vs Identidad semántica). |


### DF-28 — Alineación de Runners de Benchmark con Stack de Producción (Completado)

**Fecha de ejecución:** 2026-08-19  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-28** | `RESOLVED — PRODUCTION ALIGNMENT` | Alinear runners de benchmark con stack de producción | `apps/bootstrap/pipeline_factory.py` (`_build_healing_pipeline` → `build_healing_pipeline` público)<br>`apps/bootstrap/provider_stack_factory.py` (parámetro `base_provider` agregado)<br>`core/benchmark/runners/groq_runner.py` (usar factory canónica)<br>`core/benchmark/runners/gemini_runner.py` (usar factory canónica) | ✅ `DummyContextResolver` eliminado<br>✅ `DynamicContextResolver` con registry vacío<br>✅ `CircuitBreakerProvider` incluido vía factory<br>✅ `build_healing_pipeline()` reutilizado<br>✅ Pyright clean<br>✅ Tests green |

**Cambios normativos aplicados:**
- **NADR-05 §5.1 R1 cumplido:** Contexto real (DynamicContextResolver) en benchmark. Registry vacío es funcionalmente equivalente pero usa el mismo code path que producción.
- **NADR-08 §5.2 R7 cumplido:** CircuitBreaker MANDATORY en benchmark (vía `build_provider_stack()`).
- **NADR-11 §5.1 R1 cumplido:** Único punto de construcción del grafo de objetos (`build_provider_stack` reutilizado, no se creó factory paralela).
- **ADR_F17_BIS_01 §4 cumplido:** "Lo que el benchmark evalúa es exactamente lo que producción ejecuta."

**Decisiones de diseño clave:**
- **Sin cache en benchmark** (decisión metodológica): El benchmark mide capacidad del modelo (TPS, latencia, calidad), no eficiencia del sistema. `cache_db_path=None` deshabilita cache en la factory canónica.
- **`base_provider` en `build_provider_stack()`:** Permite al GeminiRunner inyectar `GeminiProvider` como base sin duplicar lógica de CB + RateLimiter.
- **`build_healing_pipeline()` pública:** Extraída de `_build_healing_pipeline()` para eliminar duplicación de ~20 líneas entre producción y benchmark.


### H-11-A — Limpieza de Frontera Hexagonal en core/metrics (Completado)

**Fecha de ejecución:** 2026-08-19  
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| Item | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|------|--------------|------------------|-------------------|------------|
| **H-11-A** | `RESOLVED — DELETE` | Eliminar script de diagnóstico con violación de frontera hexagonal | `core/metrics/measure_density.py` — eliminado | ✅ Archivo eliminado<br>✅ 0 imports de `fitz` en `core/`<br>✅ 0 referencias huérfanas<br>✅ Pyright clean<br>✅ Tests green |

**Justificación de la eliminación:**
- **Violación NADR-02:** `import fitz` (PyMuPDF) directamente en la capa `core/`. El dominio no debe conocer proveedores concretos de extracción.
- **Violación ENGINEERING_PRINCIPLES §II:** Functional Core contaminado con I/O de terceros.
- **Código zombi completo:** 0 consumidores, 0 imports, 0 tests. Script de diagnóstico manual sin integración al pipeline.
- **No pertenece a `core/metrics/`:** Los otros archivos (`metrics.py`, `pricing.py`, `summary.py`, `exporters.py`) son componentes activos del pipeline.

**Métrica:** -1 archivo, -25 líneas de código muerto, frontera hexagonal restaurada.