# PHASE 17-BIS EXECUTION PLAN v3.0.0
## Implementation Execution Plan & Rule-Centric Traceability Matrix

**Version:** 3.0.0
**Status:** `APPROVED BASELINE` — FROZEN
**Date:** 2026-08-19
**Supersedes:** v2.2.0
**Derived From:** 11 NADRs FROZEN + METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.2.0
**Governance Bridge:** Este documento es la **única fuente de verdad** para la secuenciación operativa y el seguimiento de cumplimiento. Los NADRs permanecen inmutables como reglas constitucionales; este plan materializa la asignación temporal de sus reglas a tareas concretas y registra el progreso de la implementación.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 2.2.0 | 2026-08-04 | Emisión con Gates 1-4 completos. |
| 3.0.0 | 2026-08-19 | Migración a plantilla canónica v1.2.0. Separación del Findings Register a documento independiente (`FASE_1_DEFERRED_FINDINGS_REGISTER.md`). Incorporación de Gate Exit Reviews, Dynamic Update Protocol, Finding Reference Convention, y Documento Vivo convention. Corrección de estados stale en Wave 2.2. |

---

## 1. EXECUTIVE SUMMARY & METHODOLOGICAL CONVENTION

### 1.1 Rule-Centric Traceability Model

```text
ADR_F17_BIS_MASTER (visión y capacidades)
↓
NADRs 01-11 (reglas constitucionales permanentes, FROZEN)
↓ Cada regla se identifica por: NADR-XX §sección Rregla
PHASE_17BIS_EXECUTION_PLAN (ESTE DOCUMENTO)
↓ Mapea: Task → Rules → Gate/Wave → Status → Implementation Evidence
FASE_1_DEFERRED_FINDINGS_REGISTER (hallazgos y resolución)
↓ Mapea: Finding → Classification → Batch → Resolution → Status
Implementación (commits, tests)
↓ Referencia reglas como Implementation Evidence
Verificación (CI gates, regression tests)
```

### 1.2 Rule Reference Convention

Las reglas se referencian directamente por su ubicación en el NADR FROZEN, sin inventar identificadores paralelos:

```text
NADR-{XX} §{sección} R{regla}
```

Ejemplo: `NADR-08 §5.2 R3` → NADR-08, sección 5.2, regla 3.

El inventario autoritativo de reglas es el **corpus de NADRs FROZEN**. Este documento no replica ni contabiliza reglas; únicamente las referencia.

### 1.3 Finding Reference Convention

Los hallazgos identificados durante la implementación se registran en el **Deferred Findings Register** (`reviews/FASE_1_DEFERRED_FINDINGS_REGISTER.md`), no en este documento. Este plan los identifica y los deriva al registro por ID:

```text
DF-{XX} | GF-{XX}
```

**Responsabilidad de este documento:** Identificar el hallazgo y derivarlo al registro.
**Responsabilidad del Findings Register:** Clasificar, resolver o diferir el hallazgo.

### 1.4 Operational Principles

- **Los NADRs no pertenecen a una fase.** Son reglas constitucionales permanentes. Lo que se asigna por fase son sus reglas individuales.
- **El Execution Plan es la única fuente de verdad temporal.** No existen matrices de trazabilidad paralelas.
- **Política de referencias cruzadas:** Una regla puede aparecer en múltiples tareas **únicamente** cuando una tarea la implementa y otra la verifica o completa. Nunca deben existir dos tareas implementando la misma obligación.
- **El estado de una regla es derivado.** Una regla no tiene estado propio. Su estado es el estado de la tarea que la implementa, salvo que esté distribuida (implementada en una tarea, verificada en otra).

### 1.5 Documento Vivo — Convención de Actualización

Este documento es **vivo**: se actualiza durante la implementación conforme al protocolo definido en §11. Los estados, notas de implementación, completion logs y contadores se actualizan a medida que las tareas se completan.

**Elementos que se actualizan durante la implementación:**
- Status de cada Task en las tablas de Waves (§2)
- Notas de implementación por Task (§2.{X}.{Y})
- Gate Completion Log (§3)
- Status Dashboard (§6)
- Traceability Appendix (§7)

**Elementos que NO se actualizan:**
- Reglas de referencia (NADRs)
- Gate Exit Criteria (se definen antes de iniciar el Gate)
- Deployment & Migration Runbook (se define antes de iniciar la fase)
- Global DoD (se define antes de iniciar la fase)

---

## 2. GATE 1 — CORE INTEGRITY & AUTOMATED GATES

**Objective:** Sellar el repositorio contra regresiones arquitectónicas y garantizar el determinismo criptográfico.
**Execution Mode:** Altamente secuencial (Critical Path).
**Rollback Plan:** `git revert` + restaurar fingerprints `.json` congelados de Fase 16 desde backup.
**Gate Status:** ✅ COMPLETED

### 2.1 Wave 1.1 — Regression Gates Infrastructure (NADR-10)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-04
**Fecha de cierre:** 2026-08-04

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

#### Notas de implementación — Wave 1.1

> Configuración CI declarativa con Required Status Checks activos. Tests de regresión refactorizados para eliminar tautologías. Daemon de reconciliación activado vía `RuntimeSettings.reconciliation_enabled`. Benchmark alineado con adaptador de producción.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-01 | `core/benchmark/__main__.py` computa SHA-256 propio por nodo | Findings Register §2 |
| DF-02 | Patrón `hasattr(n.node_type, "value")` defensivo | Findings Register §5 |
| DF-03 | `tools/benchmark_archive/` con hashing propio | Findings Register §4 |
| DF-04 | `StructuralChunkBoundaryPolicy.can_group()` siempre ALLOW | Findings Register §6 |

### 2.2 Wave 1.2 — Canonical AST & Deterministic Identity (NADR-01, NADR-03)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-04
**Fecha de cierre:** 2026-08-04

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **1.2.1** | Eliminar `ast_deserializer.py`; rutear todas las cargas a `infra/serialization/ast_json.py` | NADR-01 §5.1 R1, R2 | Critical | 1.1.1 | DONE |
| **1.2.2** | Añadir regla de linter estático bloqueando instanciación directa de `ASTNode(**kwargs)` desde dicts no tipados | NADR-01 §5.1 R3, R4 | Low | 1.1.1 | DONE |
| **1.2.3** | Extraer lógica de chunking de `hashing.py` a `core/chunking/chunker.py` | NADR-03 §5.2 R1, R2, R3 | High | 1.2.1 | DONE |
| **1.2.4** | Refactorizar pre-imagen de `compute_ast_hash()` para excluir explícitamente `node_id` y metadata efímera | NADR-03 §5.1 R1, R2, R3 | Critical | 1.2.3 | DONE |
| **1.2.5** | Separar chunking de semantic hashing en responsabilidad modular | NADR-03 §5.2 R4, R5 | Medium | 1.2.3 | DONE |

#### Notas de implementación — Wave 1.2

> `ast_deserializer.py` eliminado. Linter estático activo bloqueando instanciación directa de `ASTNode`. Chunking separado de hashing. `compute_ast_hash()` excluye `node_id` y metadata efímera. pyright 0 errors.

### 2.3 Gate 1 Exit Criteria

Todas las reglas de NADR-01, NADR-03 y NADR-10 referenciadas en este Gate deben alcanzar estado `DONE` (derivado de sus tareas). Específicamente:
- Cero aserciones tautológicas en tests de regresión
- `compute_ast_hash()` produce salida idéntica para ASTs semánticamente idénticos independientemente de `node_id`
- CI bloquea merges ante fallos de regresión
- Benchmark corre contra adaptador de producción (no parser legacy)

### 2.4 Gate 1 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** PASS
**Fecha de verificación:** 2026-08-04

---

## 3. GATE 2 — HEXAGONAL BOUNDARIES & INGESTION PURITY

**Objective:** Centralizar inyección de dependencias y purgar infraestructura cruda del dominio.
**Execution Mode:** Épicas paralelas.
**Rollback Plan:** `git revert` de lógica de fábrica; re-habilitar temporalmente adaptador de validación legacy.
**Gate Status:** ✅ COMPLETED

### 3.1 Wave 2.1 — Composition Root Consolidation (NADR-11, NADR-04)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-05
**Fecha de cierre:** 2026-08-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.1.1** | Limpiar `pipeline_factory.py`: eliminar mutaciones post-constructor DI; forzar inyección solo por constructor | NADR-11 §5.1 R1, R2, R3 | High | Gate 1 | DONE |
| **2.1.2** | Inyectar `DocumentLayoutValidator` y `PolymorphicValidationEngine` vía constructores | NADR-04 §5.1 R1, R2; §5.2 R1 | High | 2.1.1 | DONE |
| **2.1.3** | Eliminar `LegacyValidatorAdapter` y remover lógica legacy de fases 11/12 | NADR-04 §5.2 R2, R3, R4 | Medium | 2.1.2 | DONE |
| **2.1.4** | Configurar contrato `import-linter` prohibiendo fugas `core/` → `infra/` | NADR-11 §5.2 R1, R2 | Low | Gate 1 | DONE |
| **2.1.5** | Formalizar contrato explícito `DispatcherProtocol` | NADR-11 §5.3 R1, R2 | Medium | 2.1.1 | DONE |

#### Notas de implementación — Wave 2.1

> `pipeline_factory.py` limpiado: inyección solo por constructor. `LegacyValidatorAdapter` eliminado. `import-linter` activo. `DispatcherProtocol` formalizado.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-07 | AsyncDispatcher con 6 dependencias en constructor | Findings Register §7 |

### 3.2 Wave 2.2 — Ingestion Purity (NADR-02, NADR-10)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-05
**Fecha de cierre:** 2026-08-05

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **2.2.1** | Eliminar imports de `fitz` en `core/ast/router.py`; delegar traits a `infra/adapters` | NADR-02 §5.1 R1, R2, R3 | High | 2.1.4 | DONE |
| **2.2.2** | Actualizar `pipeline_factory.py` para instanciar proveedores de extracción vía configuraciones dinámicas | NADR-02 §5.2 R1, R2 | Medium | 2.2.1 | DONE |
| **2.2.3** | Eliminar `core/ast/parser.py` (parser legacy regex) y completar alineación de Benchmarks con adaptador de producción | NADR-02 §5.3 R1; NADR-10 §5.3 R10 (completa) | Critical | 2.2.2 | DONE |

#### Notas de implementación — Wave 2.2

> Imports de `fitz` eliminados de `core/`. Parser legacy regex eliminado. Benchmark alineado con adaptador de producción. Providers de extracción instanciados vía `ExtractionProviderFactory`.

#### Notas de referencia cruzada (§1.4)

> `NADR-10 §5.3 R10` aparece en la tarea 1.1.8 (preparación) y en la tarea 2.2.3 (completación). La tarea 1.1.8 prepara la alineación; la tarea 2.2.3 la completa eliminando el parser legacy. No hay doble implementación.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-10 | `PDFRouter` wrapper transicional | Findings Register §8 |
| DF-11 | Providers OCR en `core/extraction/` | Findings Register §9 |
| DF-12 | `LayoutBlockDraft`/`LayoutBlockCollection` + `DocumentLayoutBuilder` zombi | Findings Register §10 |
| DF-13 | Contrato `TestRealPaperIntegration` vs capacidades | Findings Register §11 |
| DF-14 | `LogicalClassifier` zombi | Findings Register §12 |
| DF-15 | PyMuPDF no detecta tablas/ecuaciones/imágenes | Findings Register §13 |
| DF-16 | Dualidad `LayoutBlockType` vs `ContentNodeType` | Findings Register §14 |
| DF-17 | PyMuPDF filtra imágenes (type==1) | Findings Register §15 |

### 3.3 Gate 2 Exit Criteria

Todas las reglas de NADR-02, NADR-04 y NADR-11 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Cero imports de `fitz` en `core/`
- Adaptador legacy de validación eliminado
- Composition Root usa inyección por constructor exclusivamente
- Contrato `import-linter` activo en CI

### 3.4 Gate 2 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** PASS
**Fecha de verificación:** 2026-08-05

---

## 4. GATE 3 — DISTRIBUTED EXECUTION PLANE & HEALING

**Objective:** Alcanzar paridad operacional entre CLI/Daemon y escalar horizontalmente el worker loop.
**Execution Mode:** Épicas paralelas.
**Rollback Plan:** `git revert`; downgrade del cluster de workers a escala single-node.
**Gate Status:** ✅ COMPLETED

### 4.1 Wave 3.1 — Context Resolution & Healing (NADR-05, NADR-07)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-06
**Fecha de cierre:** 2026-08-07

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.1.1** | Eliminar `DummyContextResolver` e inyectar resolver real en orquestación CLI | NADR-05 §5.1 R1, R2, R3 | Medium | Gate 2 | DONE |
| **3.1.2** | Implementar invalidación de caché de contexto jerárquico | NADR-05 §5.2 R1, R2 | High | 3.1.1 | DONE |
| **3.1.3** | Eliminar slicing de array (`hard_fails[0]`) en `AsyncDispatcher` para permitir iteración multi-fallo | NADR-07 §5.2 R1, R2 | Medium | Gate 2 | DONE |
| **3.1.4** | Añadir detección de colisión de mutaciones dentro de `HealingPipeline` para seguridad de rollback atómico | NADR-07 §5.1 R1, R2, R3 | High | 3.1.3 | DONE |
| **3.1.5** | Forzar idempotencia de healing entre iteraciones consecutivas | NADR-07 §5.3 R1, R2 | Medium | 3.1.4 | DONE |

#### Notas de implementación — Wave 3.1

> `DummyContextResolver` eliminado de `apps/cli/main.py`. `DynamicContextResolver` + `ContextRegistry` inyectados vía `_build_context_stack()`. Healing multi-fallo operacional con deduplicación por `strategy_id`. Idempotencia verificada.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-18 | `ExecutionContext` unificado | Findings Register §16 |
| DF-19 | `build_pipeline()` como God Factory | Findings Register §17 |
| DF-20 | Dispatcher resolviendo contexto | Findings Register §18 |
| DF-21 | Registros compartidos | Findings Register §19 |
| DF-22 | `RuntimeContextMappingProvider` get() vs mappings | Findings Register §20 |

### 4.2 Wave 3.2 — Distributed Execution & CQRS Lineage (NADR-08)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-06
**Fecha de cierre:** 2026-08-07

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **3.2.1** | Definir Protocol abstracto `RateLimitStore` en `core/resilience/rate_limit_store.py` | NADR-08 §5.1 R1, R2, R3 | Low | Gate 2 | DONE |
| **3.2.2** | Implementar adaptador distribuido para `TokenBucket` y `GlobalCircuitBreaker` | NADR-08 §5.1 R4; §5.2 R1, R2, R3 | Critical | 3.2.1 | PARTIAL — CircuitBreaker DONE; TokenBucket adapter BLOCKED (GF-01) |
| **3.2.3** | Eliminar `"unknown_ast_hash"` del Reconciler; inyectar hash criptográfico de linaje real en `RematerializeTaskCommand` | NADR-08 §5.3 R1, R2, R3 | High | Gate 1 | DONE |
| **3.2.4** | Activar reconciliación CQRS vía configuración externa | NADR-08 §5.4 R1, R2, R3 | Medium | 3.2.3 | DONE |
| **3.2.5** | Componer RateLimitStore y CircuitBreaker en el stack de proveedores | NADR-08 §5.5 R1, R2 | Medium | 3.2.2 | DONE |

#### Notas de implementación — Wave 3.2

> `RateLimitStore` protocol creado. `CircuitBreakerProvider` integrado en stack. `"unknown_ast_hash"` eliminado, reemplazado por `cmd.ast_hash`. Reconciliación CQRS activa vía `RuntimeSettings.reconciliation_enabled`.

> **Nota de gobernanza (Task 3.2.2):** El adaptador distribuido de `TokenBucket` queda bloqueado por GF-01 (conflicto normativo entre Execution Plan y ADR Maestro §4). El puerto `RateLimitStore` fue definido (Task 3.2.1) y la arquitectura está preparada para la implementación del backend, pero esta se difiere a Gate 4. La parte de `GlobalCircuitBreaker` sí fue completada vía `CircuitBreakerProvider`.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-23 | `resilient_provider.py` duplicado | Findings Register (RESUELTO en Wave 3.2) |
| DF-24 | `GlobalCircuitBreaker` en memoria local | Findings Register §21 |
| DF-25 | `ReconcilerDaemon` + `CQRSReconciliationDaemon` overlap | Findings Register §22 |
| DF-26 | Provider stack duplicado en entry points | Findings Register §23 |
| DF-27 | Backend persistente para cuotas (SQLite WAL) | Findings Register §24 |
| DF-28 | `DummyContextResolver` en runners de benchmark | Findings Register §25 |
| GF-01 | Conflicto normativo Task 3.2.2 vs ADR Maestro §4 | Findings Register §1 |

### 4.3 Gate 3 Exit Criteria

Todas las reglas de NADR-05, NADR-07 y NADR-08 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- Cero `DummyContextResolver` en ruta de producción
- Iteración multi-fallo de healing operacional
- Rate limiting distribuido coordina entre N procesos
- Rematerialización CQRS usa `ast_hash` real
- Daemon de reconciliación activo en producción

### 4.4 Gate 3 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ⚠️ Task 3.2.2 PARTIAL (GF-01) |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ⚠️ 25/27 (2 DEFERRED por GF-01) |
| 3 | Gate Exit Criteria satisfechos | ⚠️ Rate limiting distribuido diferido |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** CONDITIONAL PASS — 2 reglas DEFERRED por GF-01 (conflicto normativo resuelto en Gate 4 Exit Review)
**Fecha de verificación:** 2026-08-07

---

## 5. GATE 4 — COMPILER & ARTIFACT GENERATION

**Objective:** Asegurar concurrencia de I/O y garantizar preservación de sintaxis matemática.
**Execution Mode:** Altamente paralelo (dominios separados).
**Rollback Plan:** Revertir implementaciones de runners.
**Gate Status:** ✅ COMPLETED

### 5.1 Wave 4.1 — FSM Integrity & Compiler I/O Isolation (NADR-09)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-08
**Fecha de cierre:** 2026-08-10

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.1.1** | Eliminar comandos sintéticos del adaptador de persistencia FSM; forzar orquestador como única fuente de eventos | NADR-09 §5.1 R1, R2, R3, R4, R5 | High | Gate 3 | DONE |
| **4.1.2** | Envolver I/O del compilador en directorios temporales efímeros; eliminar referencias a `os.getcwd()` | NADR-09 §5.2 R1, R2, R3, R4 | Critical | 4.1.1 | DONE |
| **4.1.3** | Forzar compilador como efecto lateral aislado sin mutación de dominio | NADR-09 §5.2 R5, R6, R7 | High | 4.1.2 | DONE |

#### Notas de implementación — Task 4.1.1

> `FSMStateStore` convertido a adaptador pasivo (`initialize`, `dispatch`, `load`, `get_current_version`). `TranslationPipeline` emite comandos explícitos.

#### Notas de implementación — Task 4.1.2

> `DockerRunner` renombrado a `HostTectonicRunner` (DF-30). I/O completamente aislado en `TemporaryDirectory()`. `output_dir` obligatorio (sin default). Eliminados `os.getcwd()` y `tectonic_crash.log`. 6 tests de contrato.

#### Notas de implementación — Task 4.1.3

> Verificado sin cambios. `HostTectonicRunner` no emite comandos FSM ni muta entidades del dominio. `AssemblerWorkerDaemon` es el propietario legítimo de la fase física.

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-29 | `FSM_TO_PIPELINE_RESUME` dependencia inversa | Findings Register §26 |
| DF-30 | `DockerRunner` nomenclatura engañosa | Findings Register (RESUELTO en Task 4.1.2) |

### 5.2 Wave 4.2 — Token Estimation & Compilation Governance (NADR-06)

**Wave Status:** ✅ COMPLETED
**Fecha de inicio:** 2026-08-08
**Fecha de cierre:** 2026-08-11

| Task | Description | Rules Implemented | Risk | Deps | Status |
|---|---|---|---|---|---|
| **4.2.1** | Implementar adaptador de Tokenizer BPE compatible con proveedor; eliminar `FastWordEstimator` | NADR-06 §5.1 R1, R2, R3, R4 | High | Gate 3 | DONE |
| **4.2.2** | Refactorizar `LatexEscaper` para detectar fronteras matemáticas y bypasear escapado interno | NADR-06 §5.2 R1, R2, R3, R4 | Critical | Gate 3 | DONE |
| **4.2.3** | Re-cablear Daemon para rutear todos los ensamblados estrictamente a través de `CompilationService` (sin bypass, sin ad-hoc) | NADR-06 §5.3 R1, R2, R3, R4 | High | 4.2.2 | DONE |

#### Notas de implementación — Task 4.2.3

> Refactor arquitectónico profundo del plano de ensamblado.
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

#### Hallazgos identificados en esta Wave

| ID | Hallazgo | Derivado a |
|----|----------|------------|
| DF-31 | Proyecciones huérfanas no observables desde port | Findings Register §27 |
| DF-33 | Verificación de consumidores `decision.document` | Findings Register (RESUELTO en pre-implementación) |
| DF-34 | `ProfileStore` durable para AssemblerWorkerDaemon | Findings Register §28 |

### 5.3 Gate 4 Exit Criteria

Todas las reglas de NADR-06 y NADR-09 referenciadas en este Gate deben alcanzar estado `DONE`. Específicamente:
- FSM emite solo transiciones ordenadas por el orquestador
- I/O del compilador aislado en directorios efímeros
- Tokenizer BPE produce estimaciones precisas de LaTeX
- Escapado TeX preserva sintaxis matemática legítima
- Daemon rutea exclusivamente a través de `CompilationService`

### 5.4 Gate 4 Exit Review

**Checklist de cierre:**

| # | Verificación | Estado |
|---|-------------|--------|
| 1 | Todas las Tasks del Gate en estado DONE | ✅ |
| 2 | Todas las reglas del Gate en estado DONE en §7 | ✅ 24/24 |
| 3 | Gate Exit Criteria satisfechos | ✅ |
| 4 | Hallazgos identificados derivados al Findings Register | ✅ |
| 5 | Pyright: 0 errors, 0 warnings | ✅ |
| 6 | Tests: suite completa en verde | ✅ |
| 7 | Notas de implementación completas para todas las Tasks | ✅ |

**Veredicto del Gate:** PASS
**Fecha de verificación:** 2026-08-11

---

## 6. GATE COMPLETION LOG (Living Document)

Se actualiza al cierre de cada Gate.

| Gate | Fecha de cierre | Rules DONE / Total | Tasks DONE / Total | Hallazgos derivados | Observaciones |
|------|----------------|-------------------|-------------------|-------------------|---------------|
| Gate 1 | 2026-08-04 | 26/26 | 13/13 | 4 (DF-01, DF-02, DF-03, DF-04) | pyright 0 errors. AST hashing semántico confirmado. |
| Gate 2 | 2026-08-05 | 20/20 | 8/8 | 8 (DF-10 a DF-17) | fitz eliminado. Parser legacy eliminado. |
| Gate 3 | 2026-08-07 | 25/27 | 9/10 | 8 (DF-18 a DF-28, GF-01) | Wave 3.1+3.2 completadas. 2 reglas diferidas por GF-01. |
| Gate 4 | 2026-08-11 | 24/24 | 6/6 | 4 (DF-29, DF-31, DF-33, DF-34) | Wave 4.1 COMPLETADA (12 reglas NADR-09). Wave 4.2 COMPLETADA (12 reglas NADR-06). GF-01 resuelto en Exit Review. |

---

## 7. DEPLOYMENT & MIGRATION RUNBOOK

Tareas operativas de release (no desarrollo). Vinculadas a reglas específicas. Se definen antes de iniciar la fase y NO se actualizan durante la implementación salvo por cancelación justificada.

| Step | Operation | Environment | Linked Rules | Evidence | Status |
|---|---|---|---|---|---|
| **MIG-01** | Corpus Resealing: ejecutar `tools/reseal_corpus.py` para regenerar baselines `.fingerprint.json` y `.ast.json` con el nuevo hash determinista | Local, CI | NADR-03 §5.1 R1, R2 | E-0.1-003 | TODO |
| **MIG-02** | Truncar caché materializada: `DELETE FROM materialized_cache` para purgar claves legacy inyectadas por `DummyContextResolver` | Staging, Prod | NADR-05 §5.1 R1, R2 | P4-05 | TODO |
| ~~**MIG-03**~~ | ~~Desplegar KV Store distribuido~~ | — | — | — | **ELIMINADO** |

> **Justificación MIG-03:** Contradice ADR Maestro §4 y GF-01. La implementación del backend de `RateLimitStore` se resolvió vía `SQLiteRateLimitStore` local (DF-27). El ROADMAP prohíbe explícitamente Redis.

---

## 8. GLOBAL DoD (Definition of Done)

La Fase 17-BIS se considera oficialmente completada cuando:

```text
{All rules in FROZEN NADRs 01-11} − {Rules with DONE status in §9} = ∅
```

**Verificación:** Cada regla debe ser trazable a:
1. Una implementación commiteada (**Implementation Evidence**)
2. Un mecanismo de verification superado (linter/type-check/property-test)
3. Un mecanismo de validation superado (regression gate / golden corpus)

> **Nota:** "Implementation Evidence" es un identificador abstracto de la evidencia de implementación (commit SHA, changeset, o equivalente en el sistema de control de versiones). No está acoplado a ninguna plataforma específica.

---

## 9. STATUS DASHBOARD (Living Document)

Los contadores se **derivan computacionalmente** del Traceability Appendix (§10), no se hardcodean:

| Gate | Tasks DONE | Rules DONE | Rules DEFERRED | Rules PENDING | Gate Status |
|---|---|---|---|---|---|
| Gate 1 | 13 | 26 | 0 | 0 | ✅ COMPLETED |
| Gate 2 | 8 | 20 | 0 | 0 | ✅ COMPLETED |
| Gate 3 | 9 | 25 | 2 (GF-01) | 0 | ✅ COMPLETED |
| Gate 4 | 6 | 24 | 0 | 0 | ✅ COMPLETED |
| **TOTAL** | **36** | **95** | **2** | **0** | ✅ ALL GATES COMPLETED |

**Regla de actualización:** Cada vez que una Task pase a `DONE`:
1. Se actualiza el `Status` de la Task en la tabla de Wave correspondiente (§2-§5)
2. Se agregan las Notas de implementación de la Task
3. Se actualiza el `Derived Status` de sus reglas en §10
4. Se recalculan los contadores de este dashboard
5. Si todas las Tasks del Gate están DONE, se ejecuta el Gate Exit Review (§2.4, §3.4, §4.4, §5.4)

> **Nota operativa:** Las 2 reglas DEFERRED de Gate 3 (NADR-08 §5.1 R3, R4) fueron resueltas mediante `SQLiteRateLimitStore` (DF-27) conforme a la resolución de GF-01. Gate 4 COMPLETADO con 24/24 reglas propias.

---

## 10. TRACEABILITY APPENDIX — AUDIT BOARD (Living Document)

**Propósito:** Tablero auditable de completitud. El estado de cada regla es **derivado** del estado de la Task que la implementa (§1.4). La relación Task → Rules ya está definida en los Gates (§2–§5); este appendix no la repite.

**Formato:** `Rule | Derived Status | Evidence | Implementation Notes`

### 10.1 Gate 1 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-10 §5.2 R6 | DONE | Wave 1.1 | CI declarativa con Required Status Checks |
| NADR-10 §5.1 R2 | DONE | Wave 1.1 | Tests de regresión sin tautologías |
| NADR-10 §5.1 R3 | DONE | Wave 1.1 | Matching Read-Only contra oráculo |
| NADR-10 §5.2 R5 | DONE | Wave 1.1 | Baseline actualizada explícitamente |
| NADR-10 §5.1 R1 | DONE | Wave 1.1 | `FileNotFoundError` en baselines ausentes |
| NADR-10 §5.1 R4 | DONE | Wave 1.1 | Mecanismo explícito de actualización |
| NADR-10 §5.2 R13 | DONE | Wave 1.1 | Comparación completa de campos DTO |
| NADR-10 §5.2 R14 | DONE | Wave 1.1 | Sin sustitución artificial en integration tests |
| NADR-10 §5.2 R7 | DONE | Wave 1.1 | pyproject.toml declarativo |
| NADR-10 §5.2 R8 | DONE | Wave 1.1 | Daemon de reconciliación activo |
| NADR-10 §5.2 R11 | DONE | Wave 1.1 | Configuración externa |
| NADR-10 §5.2 R12 | DONE | Wave 1.1 | Sin banderas hardcodeadas |
| NADR-10 §5.3 R9 | DONE | Wave 1.1 | Benchmark consume Composition Root |
| NADR-10 §5.3 R10 | DONE | Wave 1.1 | Preparación de alineación |
| NADR-01 §5.1 R1 | DONE | Wave 1.2 | `ast_deserializer.py` eliminado |
| NADR-01 §5.1 R2 | DONE | Wave 1.2 | Cargas ruteadas a `infra/serialization/ast_json.py` |
| NADR-01 §5.1 R3 | DONE | Wave 1.2 | Linter estático activo |
| NADR-01 §5.1 R4 | DONE | Wave 1.2 | Bloqueo de instanciación directa |
| NADR-03 §5.2 R1 | DONE | Wave 1.2 | Chunking extraído |
| NADR-03 §5.2 R2 | DONE | Wave 1.2 | Responsabilidad modular |
| NADR-03 §5.2 R3 | DONE | Wave 1.2 | `core/chunking/chunker.py` |
| NADR-03 §5.1 R1 | DONE | Wave 1.2 | `compute_ast_hash()` sin `node_id` |
| NADR-03 §5.1 R2 | DONE | Wave 1.2 | Sin metadata efímera |
| NADR-03 §5.1 R3 | DONE | Wave 1.2 | Hash semántico determinista |
| NADR-03 §5.2 R4 | DONE | Wave 1.2 | Chunking separado de hashing |
| NADR-03 §5.2 R5 | DONE | Wave 1.2 | Responsabilidad modular independiente |

### 10.2 Gate 2 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-11 §5.1 R1 | DONE | Wave 2.1 | Inyección solo por constructor |
| NADR-11 §5.1 R2 | DONE | Wave 2.1 | Sin mutaciones post-constructor |
| NADR-11 §5.1 R3 | DONE | Wave 2.1 | Composition Root único |
| NADR-04 §5.1 R1 | DONE | Wave 2.1 | `DocumentLayoutValidator` inyectado |
| NADR-04 §5.1 R2 | DONE | Wave 2.1 | `PolymorphicValidationEngine` inyectado |
| NADR-04 §5.2 R1 | DONE | Wave 2.1 | Validación obligatoria en pipeline |
| NADR-04 §5.2 R2 | DONE | Wave 2.1 | `LegacyValidatorAdapter` eliminado |
| NADR-04 §5.2 R3 | DONE | Wave 2.1 | Lógica legacy removida |
| NADR-04 §5.2 R4 | DONE | Wave 2.1 | Sin adaptadores legacy |
| NADR-11 §5.2 R1 | DONE | Wave 2.1 | `import-linter` activo |
| NADR-11 §5.2 R2 | DONE | Wave 2.1 | Prohibición `core/` → `infra/` |
| NADR-11 §5.3 R1 | DONE | Wave 2.1 | `DispatcherProtocol` formalizado |
| NADR-11 §5.3 R2 | DONE | Wave 2.1 | Contrato explícito |
| NADR-02 §5.1 R1 | DONE | Wave 2.2 | Imports `fitz` eliminados |
| NADR-02 §5.1 R2 | DONE | Wave 2.2 | Traits delegados a `infra/adapters` |
| NADR-02 §5.1 R3 | DONE | Wave 2.2 | Frontera hexagonal respetada |
| NADR-02 §5.2 R1 | DONE | Wave 2.2 | Providers vía `ExtractionProviderFactory` |
| NADR-02 §5.2 R2 | DONE | Wave 2.2 | Configuraciones dinámicas |
| NADR-02 §5.3 R1 | DONE | Wave 2.2 | Parser legacy eliminado |
| NADR-10 §5.3 R10 (completa) | DONE | Wave 2.2 | Benchmark alineado con adaptador de producción |

### 10.3 Gate 3 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-05 §5.1 R1 | DONE | Wave 3.1 | `DynamicContextResolver` + `ContextRegistry` |
| NADR-05 §5.1 R2 | DONE | Wave 3.1 | `DummyContextResolver` eliminado de producción |
| NADR-05 §5.1 R3 | DONE | Wave 3.1 | Fail-fast sin fallback |
| NADR-05 §5.2 R1 | DONE | Wave 3.1 | `prompt_hash` con contexto real |
| NADR-05 §5.2 R2 | DONE | Wave 3.1 | Claves vinculadas a identidad contextual |
| NADR-07 §5.2 R1 | DONE | Wave 3.1 | `heal_all_and_revalidate()` multi-fallo |
| NADR-07 §5.2 R2 | DONE | Wave 3.1 | Estrategias por prioridad |
| NADR-07 §5.1 R1 | DONE | Wave 3.1 | `_plan_healing()` con deduplicación |
| NADR-07 §5.1 R2 | DONE | Wave 3.1 | `_apply_mutations()` secuencial |
| NADR-07 §5.1 R3 | DONE | Wave 3.1 | Colección completa procesada |
| NADR-07 §5.3 R1 | DONE | Wave 3.1 | Revalidación única transaccional |
| NADR-07 §5.3 R2 | DONE | Wave 3.1 | Sin revalidación redundante |
| NADR-08 §5.1 R1 | DONE | Wave 3.2 | `RateLimitStore` protocol creado |
| NADR-08 §5.1 R2 | DONE | Wave 3.2 | Operaciones `load()`/`save()` |
| NADR-08 §5.1 R3 | DONE | DF-27 (Batch 3) | `SQLiteRateLimitStore` implementado. GF-01 resuelto. |
| NADR-08 §5.1 R4 | DONE | DF-27 (Batch 3) | Backend seleccionado desde Composition Root. GF-01 resuelto. |
| NADR-08 §5.2 R1 | DONE | Wave 3.2 | `CircuitBreakerProvider` integrado |
| NADR-08 §5.2 R2 | DONE | Wave 3.2 | `GlobalCircuitBreaker` configurable |
| NADR-08 §5.2 R3 | DONE | Wave 3.2 | Stack CB → Cache → RL → Provider |
| NADR-08 §5.3 R1 | DONE | Wave 3.2 | `ast_hash` en `RematerializeTaskCommand` |
| NADR-08 §5.3 R2 | DONE | Wave 3.2 | `"unknown_ast_hash"` eliminado |
| NADR-08 §5.3 R3 | DONE | Wave 3.2 | Propagación desde `ReconcilerDaemon` |
| NADR-08 §5.4 R1 | DONE | Wave 3.2 | Reconciliación activa |
| NADR-08 §5.4 R2 | DONE | Wave 3.2 | Gobernada por config externa |
| NADR-08 §5.4 R3 | DONE | Wave 3.2 | Sin banderas hardcodeadas |
| NADR-08 §5.5 R1 | DONE | Wave 3.2 | CB y RL compuestos |
| NADR-08 §5.5 R2 | DONE | Wave 3.2 | CB antes de RL |

### 10.4 Gate 4 — Rules Audit Board

| Rule | Derived Status | Evidence | Implementation Notes |
|---|---|---|---|
| NADR-09 §5.1 R1 | DONE | Task 4.1.1 | Comandos explícitos desde orquestador |
| NADR-09 §5.1 R2 | DONE | Task 4.1.1 | `FSMStateStore` adaptador pasivo |
| NADR-09 §5.1 R3 | DONE | Task 4.1.1 | `PipelineStep` sincronizado con `DocumentState` |
| NADR-09 §5.1 R4 | DONE | Task 4.1.1 | `FSMValidator` única autoridad |
| NADR-09 §5.1 R5 | DONE | Task 4.1.1 | Sin auto-promoción |
| NADR-09 §5.2 R1 | DONE | Task 4.1.2 | `HostTectonicRunner` en `TemporaryDirectory` |
| NADR-09 §5.2 R2 | DONE | Task 4.1.2 | `cwd=tmp` en `subprocess.run()` |
| NADR-09 §5.2 R3 | DONE | Task 4.1.2 | Artefactos en sandbox |
| NADR-09 §5.2 R4 | DONE | Task 4.1.2 | `os.getcwd()` eliminado |
| NADR-09 §5.2 R5 | DONE | Task 4.1.3 | Runner no modifica FSM |
| NADR-09 §5.2 R6 | DONE | Task 4.1.3 | Runner no muta dominio |
| NADR-09 §5.2 R7 | DONE | Task 4.1.3 | Efecto lateral aislado |
| NADR-06 §5.1 R1 | DONE | Task 4.2.1 | `ExactBPEEstimator` canónico |
| NADR-06 §5.1 R2 | DONE | Task 4.2.1 | `FastWordEstimator` eliminado |
| NADR-06 §5.1 R3 | DONE | Task 4.2.1 | BPE real |
| NADR-06 §5.1 R4 | DONE | Task 4.2.1 | Inyectable vía `TokenEstimatorProtocol` |
| NADR-06 §5.2 R1 | DONE | Task 4.2.2 | `$...$` y `$$...$$` preservadas |
| NADR-06 §5.2 R2 | DONE | Task 4.2.2 | Escapado consciente del contexto |
| NADR-06 §5.2 R3 | DONE | Task 4.2.2 | Tokens Unicode inmunes |
| NADR-06 §5.2 R4 | DONE | Task 4.2.2 | 18 tests + 4 regresión |
| NADR-06 §5.3 R1 | DONE | Task 4.2.3 | Daemon rutea vía `CompilationService` |
| NADR-06 §5.3 R2 | DONE | Task 4.2.3 | `AssemblerProtocol` eliminado |
| NADR-06 §5.3 R3 | DONE | Task 4.2.3 | `CQRSAssemblyContextResolver` valida topología |
| NADR-06 §5.3 R4 | DONE | Task 4.2.3 | `AssemblyPolicy` gobierna decisiones |

---

## 11. FINDINGS REGISTER REFERENCE

Los hallazgos identificados durante la implementación de este Execution Plan se registran y gestionan en:

```text
docs/architecture/adr/phase-17-bis/reviews/FASE_1_DEFERRED_FINDINGS_REGISTER.md
```

Este documento **NO contiene** hallazgos, decisiones de clasificación, resultados de batches ni hallazgos diferidos. Esos artefactos pertenecen al Deferred Findings Register conforme a la METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §3.5.3.

**Responsabilidad de este documento:**
- Identificar hallazgos durante la implementación de Tasks
- Derivarlos al Findings Register con ID único
- Referenciar los IDs de hallazgos relevantes en las Notas de implementación

**Responsabilidad del Findings Register:**
- Clasificar cada hallazgo (implementable / diferido / NAR / limitación)
- Registrar resultados de implementación por batch
- Documentar hallazgos diferidos a fases futuras

---

## 12. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.2.0.

* **El ADR Maestro** (`ADR_F17_BIS_MASTER.md`) define la visión arquitectónica de la fase (el QUÉ y el POR QUÉ).
* **El ADR de Fase** (`ADR_F17_BIS_01.md`) particulariza la decisión para la sub-fase de alineación del pipeline.
* Las **reglas técnicas obligatorias** se encuentran promulgadas en NADR-01 a NADR-11.
* **Este Execution Plan** define la secuencia operativa, tareas concretas y seguimiento de cumplimiento.
* El **Deferred Findings Register** (`FASE_1_DEFERRED_FINDINGS_REGISTER.md`) registra los hallazgos identificados, su clasificación y resolución.

Este documento **no prescribe implementaciones específicas, decisiones arquitectónicas, criterios de revisión de código ni registro de hallazgos.**

---

## 13. FUTURE WORK

> The Traceability Appendix (§10) is intentionally written manually in this version. Future versions **MAY** generate this appendix automatically from task metadata, eliminating manual synchronization. This note prevents the assumption that the appendix must always be maintained by hand.

---

## 14. DYNAMIC UPDATE PROTOCOL

Este documento se actualiza conforme al siguiente protocolo durante la implementación:

### 14.1 Al iniciar una Task

1. Actualizar el `Status` de la Task a `IN_PROGRESS` en la tabla de Wave (§2-§5)
2. Actualizar el `Gate Status` a `🟡 IN PROGRESS` si era `⏳ PENDING`

### 14.2 Al completar una Task

1. Actualizar el `Status` de la Task a `DONE` en la tabla de Wave (§2-§5)
2. Redactar las **Notas de implementación** de la Task
3. Actualizar el `Derived Status` de las reglas implementadas en §10
4. Recalcular los contadores del Status Dashboard (§9)
5. Verificar que las reglas implementadas no aparecen como PENDING en §10

### 14.3 Al identificar un hallazgo

1. Registrar el hallazgo en la tabla "Hallazgos identificados en esta Wave"
2. Asignar ID único (`DF-{XX}` o `GF-{XX}`)
3. Derivar al Deferred Findings Register con el ID asignado
4. Si el hallazgo bloquea la Task, actualizar el `Status` a `BLOCKED`

### 14.4 Al cerrar un Gate

1. Verificar el Gate Exit Review Checklist
2. Actualizar el `Gate Status` a `✅ COMPLETED`
3. Registrar en el Gate Completion Log (§6)
4. Derivar todos los hallazgos identificados al Findings Register
5. Ejecutar el Gate Exit Review en el Findings Register

### 14.5 Al cancelar una operación de Deployment

1. Actualizar el `Status` a `ELIMINADO` en la tabla de Deployment (§7)
2. Agregar justificación de cancelación como nota al pie de la tabla
3. Si la cancelación afecta reglas NADR, registrar como hallazgo (§14.3)

### 14.6 Prohibiciones

- ❌ No modificar Gate Exit Criteria después de iniciar el Gate
- ❌ No eliminar Tasks (se marcan como `ELIMINADO` con justificación)
- ❌ No agregar reglas nuevas al Traceability Appendix sin referencia a NADR
- ❌ No registrar hallazgos en este documento (se derivan al Findings Register)
- ❌ No registrar resultados de implementación de hallazgos en este documento

---

**Nota de Gobernanza:** Este documento es la única fuente de verdad para la trazabilidad temporal entre reglas normativas (NADRs FROZEN) e implementación. Los NADRs permanecen inmutables; cualquier cambio en la secuencia operativa se refleja únicamente aquí. El inventario autoritativo de reglas es el corpus de NADRs FROZEN, no este documento. El estado de cada regla es derivado del estado de la Task que la implementa. Los hallazgos identificados durante la implementación se gestionan en el Deferred Findings Register, no en este documento.