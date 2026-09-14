# FASE_1_HANDOFF.md

**Documento:** `docs/architecture/adr/phase-17-bis/handoff/FASE_1_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-08-19
**Fase completada:** Fase 1 (Production Pipeline Alignment — F17-BIS)
**Siguiente fase:** Fase 18 (Advanced Local Runtime)
**Derivado de:** PHASE_17BIS_EXECUTION_PLAN.md v3.0.0 + FASE_1_DEFERRED_FINDINGS_REGISTER.md v1.0.0

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-19 | Emisión inicial al cierre de F17-BIS |

---

## 1. EXECUTIVE SUMMARY

La **Fase 1 (F17-BIS — Production Pipeline Alignment)** se completó exitosamente. Su objetivo fue alinear el pipeline de producción con los contratos normativos de los NADRs 01-11 FROZEN, prerrequisito arquitectónico obligatorio antes de construir la Scientific Baseline (Fases 2-6 del ADR Maestro).

**Estado final:**
- ✅ Los 4 Gates técnicos completados (95 reglas implementadas + 2 diferidas por GF-01 y resueltas vía `SQLiteRateLimitStore`)
- ✅ 34 hallazgos analizados, 29 resueltos o cerrados, 7 diferidos a fases futuras con destino explícito
- ✅ 0 hallazgos pendientes de implementación o revisión
- ✅ Pipeline productivo, benchmark y daemons alineados con el mismo Composition Root

**Qué queda para la siguiente fase:**
- Resolver **DF-34** (ProfileStore durable) como condición explícita del Recovery Gate (Gate I)
- Evolucionar el runtime con asincronía pura, backpressure y cache multinivel (ROADMAP §IV Fase 18)
- Mantener las restricciones activas (ADR Maestro §4: sin infraestructura distribuida)

La Scientific Baseline ya puede comenzar a construirse sobre un pipeline arquitectónicamente fiel.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` |
| Estado del árbol | Limpio, todos los documentos FROZEN |
| Baseline de tests | **274 passed, 5 skipped** (no debe degradarse sin justificación) |
| Pyright | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados |
| Frontera hexagonal | `core/` libre de imports de infraestructura (excepto casos ya tratados) |

### 2.2 Validation Results

```bash
# Validaciones ejecutadas al cierre
pytest -q                              # 274 passed, 5 skipped ✅
pyright                                # 0 errors, 0 warnings ✅
grep -r "from infra" core/             # 0 violaciones de frontera hexagonal ✅
grep -r "DummyContextResolver" apps/   # 0 residuos en ruta de producción ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR F17_BIS MASTER | FROZEN | 1.0.0 |
| ADR F17_BIS_01 | FROZEN | 1.0.0 |
| NADRs 01-11 | FROZEN | 1.0.0 |
| PHASE_17BIS_EXECUTION_PLAN | FROZEN | 3.0.0 |
| FASE_1_EXIT_REVIEW_EVIDENCE_LOG | FROZEN | 1.0.0 |
| FASE_1_DEFERRED_FINDINGS_REGISTER | ARCHIVED | 1.0.0 |
| METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES | FROZEN | 1.2.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 34 (27 DF/GF/H + 7 sub-DFs) |
| Hallazgos resueltos | 20 |
| Hallazgos cerrados sin acción (NAR) | 9 |
| Hallazgos diferidos a fase futura | 7 |
| Batches ejecutados | 7 |
| Archivos eliminados | 14 |
| Archivos movidos | 3 |
| Archivos creados | 2 |
| Archivos modificados | ~16 |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | SQLite WAL local en lugar de infraestructura distribuida para `RateLimitStore` | GF-01: conflicto entre NADR-08 §5.1 y ADR Maestro §4 | ADR Maestro §4 prohíbe infraestructura distribuida; ROADMAP §V aprueba SQLite WAL como Core Engine | `infra/resilience/sqlite_rate_limit_store.py` |
| AD-02 | `provider_stack_factory.py` como único punto de construcción del stack LLM | DF-26: 3 puntos de construcción duplicados con divergencia de configuración | Cumple NADR-11 §5.1 R1 (único Composition Root) | `apps/bootstrap/provider_stack_factory.py` |
| AD-03 | Runners de benchmark alineados con Composition Root de producción | DF-28: `DummyContextResolver` en runners | ADR_F17_BIS_01 §4: "Benchmark evalúa lo que producción ejecuta" | `core/benchmark/runners/{groq,gemini}_runner.py` |
| AD-04 | Centralización criptográfica en `core/shared/crypto.py` | DF-01-A: `hashlib.sha256()` disperso en benchmark | ENGINEERING_PRINCIPLES §III (Explicit over Implicit) | `core/shared/crypto.py` + migración de 6 archivos |
| AD-05 | Migración de providers OCR a `infra/extraction/providers/` | DF-11: violación de frontera hexagonal | ENGINEERING_PRINCIPLES §II (Hexagonal) | 3 providers movidos de `core/` a `infra/` |
| AD-06 | Eliminación de 6 stages zombis del layout pipeline | DF-12-A/B: `DocumentLayoutBuilder` + stages sin orquestador | ENGINEERING_PRINCIPLES §I (YAGNI) | 7 archivos eliminados |
| AD-07 | `AssemblyExecutionContext` como frontera Execution → Compilation | Task 4.2.3 | VO inmutable: Resolver valida, Assembler decide, Service materializa | `core/compiler/assembly_context.py` |
| AD-08 | `DispatchResult` dejó de ser contrato inter-stage | Task 4.2.3 | Elimina acoplamiento pipeline lógico ↔ daemon físico | `core/pipeline/orchestrator.py` termina en `MarkAssemblyReadyCommand` |
| AD-09 | `FlatASTBuilder._TYPE_MAPPING` como único puente `LayoutBlockType ↔ ContentNodeType` | DF-16: dos taxonomías ortogonales | Pérdida de información intencional; capas independientes | `core/ast/builder.py:52-83` |
| AD-10 | Sin `ExecutionContext` unificado (6 contextos bounded) | DF-18 | DDD bounded contexts correcto; YAGNI para unificación | `PROJECT_TREE` |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Determinismo criptográfico del AST | NADR-01, NADR-03 | ✅ DONE |
| Frontera hexagonal limpia (core/ libre de infraestructura) | NADR-02, NADR-11 | ✅ DONE |
| Hashing semántico determinista (`compute_ast_hash`) | NADR-03 | ✅ DONE |
| Validación polimórfica obligatoria | NADR-04 | ✅ DONE |
| Resolución de contexto real (sin Dummy) | NADR-05 | ✅ DONE |
| Token estimation BPE canónico | NADR-06 | ✅ DONE |
| Escapado TeX consciente del contexto | NADR-06 | ✅ DONE |
| Healing multi-fallo idempotente | NADR-07 | ✅ DONE |
| RateLimitStore persistente (SQLite WAL) | NADR-08 | ✅ DONE |
| FSM como única autoridad de transiciones | NADR-09 | ✅ DONE |
| Regression Gates activos en CI | NADR-10 | ✅ DONE |
| Composition Root único | NADR-11 | ✅ DONE |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `apps/bootstrap/provider_stack_factory.py` — Factory centralizada del stack LLM
- `infra/resilience/sqlite_rate_limit_store.py` — Backend persistente de cuotas
- `core/shared/crypto.py` (extendido con `compute_sha256_stream`)
- `core/compiler/ports.py` (`ASTProviderProtocol`)
- `core/compiler/assembly_context.py` (`AssemblyExecutionContext`)
- `core/compiler/context_resolver.py` (`CQRSAssemblyContextResolver`)

**Eliminados (zombies y deuda):**
- `core/ast/router.py`, `core/ast/ports.py`, `infra/adapters/pdf_router.py` (PDFRouter legacy)
- `core/layout/builder.py` (DocumentLayoutBuilder)
- `core/layout/{detector,identity,merger,normalizer,reading_order,base}.py` (6 stages zombis)
- `core/layout/classifier.py` (LogicalClassifier zombi)
- `runtime/reconciliation.py` (CQRSReconciliationDaemon — subconjunto de ReconcilerDaemon)
- `core/metrics/measure_density.py` (violación de frontera)
- Dicts zombies en `core/execution/state_mapping.py`

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para Fase 18 |
|-------------|--------|------------------------|
| NO introducir infraestructura distribuida (Redis, Brokers, K8s, DBs remotas) | ADR Maestro §4 | Todo caching/colas debe ser local (SQLite WAL, memoria) |
| NO integrar nuevos adaptadores de extracción de visión computacional | ADR Maestro §4 | PyMuPDF es el provider vigente; cambios requieren nuevo benchmark |
| Separación de identidades: Integrity ≠ Identity ≠ Regression | ADR Maestro §3, §5 | No colapsar hashes de PDF, AST, corpus en un solo mecanismo |
| Benchmark es subproducto controlado, no segunda implementación (P2) | ADR_F17_BIS_01 §4 | `REUSED ≠ IDENTICAL`, `TRANSFORM ≠ VIOLATION` |
| Composition Root único en `apps/bootstrap/` | NADR-11 §5.1 R1 | Todo entry point consume factory centralizada |
| Benchmark Before Optimization | ROADMAP §I Principio 7 | Cambios estructurales requieren evidencia estadística |
| Optimize Before Distribution | ROADMAP §I Principio 8 | Exprimir hardware local antes de considerar sistemas distribuidos |
| DTOs inmutables (`frozen=True`) | ENGINEERING_PRINCIPLES §II | Cero mutación in-place |
| Cero Fallos Silenciosos | ENGINEERING_PRINCIPLES §IV | Fail-fast ante datos anómalos |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| **DF-34** | `ProfileStore` durable (no `InMemoryProfileStore`) | **Recovery Gate (Gate I) / Fase 18** | **Recovery Gate no PASS sin resolver** |
| **DF-01-C** | Linaje de identidad semántica: dónde viaja `compute_ast_hash()` en benchmark | Fase 2/3 (Identity & Trust Model) | Certificación de Baseline |
| **DF-12-C/D/E** | Migrar `FlatASTBuilder` a consumir `list[LayoutBlock]` directo (eliminando `LayoutBlockDraft`/`LayoutBlockCollection`) | Fase 18 | Nada — deuda técnica documentada |
| **DF-17** | Habilitar extracción de imágenes (PyMuPDF type==1 descartado) | Fase 21 (Parser Routing) | Nada — dominio ya soporta IMAGE conceptualmente |
| **DF-18** | `ExecutionContext` unificado transversal | Fase 18 (coordinación) o Fase 20 (observabilidad) | Nada — bounded contexts correctos |
| **DF-24** | `CircuitBreakerStore` distribuido | Fase 18 (si se demuestra multi-proceso) | Nada — single-node hoy |
| **DF-04** | `HARD_BREAK` en chunking requiere semántica de contexto cruzado en AST | Post-Fase 18 | Nada — ALLOW es correcto hoy |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| **Crash de AssemblerWorkerDaemon** | `InMemoryProfileStore` no sobrevive crash → `ProfileNotFoundError` en documentos en cola | Perfil puede re-inferirse desde ASTRegistry (determinista), pero no hay recovery automático |
| **PyMuPDF no detecta tablas/ecuaciones/imágenes** | Limitación declarada en `ExtractionCapabilities` | Tests condicional sobre `.capabilities` (DF-13) |
| **CircuitBreaker en memoria** | Estado se pierde con el proceso | Suficiente para single-node; no promete coordinación multi-proceso |
| **`LayoutBlockDraft`/`LayoutBlockCollection`** | Capa de traducción innecesaria entre dominio y ASTBuilder | Funcional pero deuda técnica (DF-12-C) |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites (Fase 18 — Advanced Local Runtime)

**Lo que ya está listo:**
- ✅ Pipeline productivo alineado y gobernado por NADRs FROZEN
- ✅ Composition Root único funcional
- ✅ Tests verdes y deterministas (274 passed, 5 skipped)
- ✅ Pyright limpio (0 errors, 0 warnings)
- ✅ Metodología de gobernanza v1.2.0 establecida
- ✅ Flujo de trabajo: Auditoría → ADR → NADR → Execution Plan → Implementación → Reviews → Handoff

**Lo que se necesita antes de arrancar Fase 18:**
- Resolver **DF-34** (ProfileStore durable) como prerequisito del Recovery Gate
- Definir ADR_F18_MASTER con visión de Advanced Local Runtime
- Crear NADRs específicos de asincronía, memoria, batching
- Baseline de Scientific Corpus (Fases 2-6 del ADR Maestro)

### 6.2 Next Phase Handoff Checklist

- [ ] Crear `docs/architecture/adr/phase-18/`
- [ ] Redactar `ADR_F18_MASTER.md`
- [ ] Resolver DF-34 antes de Recovery Gate
- [ ] Considerar DF-18 (ExecutionContext) si hay necesidad demostrada de coordinación transversal
- [ ] Considerar DF-24 (CircuitBreakerStore) si se demuestra necesidad multi-proceso
- [ ] Considerar DF-12-C/D/E como refactor de simplificación
- [ ] Implementar capacidades de ROADMAP §IV Fase 18

### 6.3 ROADMAP §IV Fase 18 — Objetivos declarados

1. **Asincronía pura top-to-bottom** — elisión de `SyncProviderBridge`
2. **Memory Efficiency** — Object Pools, buffers Zero-copy, lazy loading
3. **Pipeline Backpressure** — prevención de OOM en procesamiento masivo
4. **Adaptive Batching & Scheduling** — agrupación dinámica según presupuesto (8k, 32k, 1M)
5. **Cache Multinivel** — Memoria → SQLite → Semantic/Embedding Cache

**Hito crítico:** Al concluir Fase 18, el Traductor PDF se considera funcionalmente completo para el procesamiento de documentos científicos reales.

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR Maestro | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md` |
| ADR de Fase | `docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_01.md` |
| NADRs 01-11 | `docs/architecture/adr/phase-17-bis/NADR/NADR_{XX}_{Nombre}.md` |
| Execution Plan | `docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_EXECUTION_PLAN.md` |
| Evidence Log | `docs/architecture/adr/phase-17-bis/reviews/FASE_1_EXIT_REVIEW_EVIDENCE_LOG.md` |
| Methodology | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |
| Engineering Principles | `docs/architecture/ENGINEERING_PRINCIPLES.md` |
| Project Scope | `docs/architecture/PROJECT_SCOPE.md` |
| Roadmap | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` |
| Project Tree | `docs/architecture/PROJECT_TREE.txt` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| Findings Register | `docs/architecture/adr/phase-17-bis/reviews/FASE_1_DEFERRED_FINDINGS_REGISTER.md` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| Handoff (este) | `docs/architecture/adr/phase-17-bis/handoff/FASE_1_HANDOFF.md` | Transición de fase y contexto LLM |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: Traductor PDF Científico (Proyecto Traductor)
Descripción: Pipeline automatizado SOTA para ingesta, normalización, traducción LLM y
             reconstrucción de documentos complejos (PDFs STEM/académicos) preservando
             topología, ecuaciones, tablas e invariantes lógicas.
Stack: Python 3.12+ | Pydantic v2 | SQLite (WAL) | pytest | pyright
Arquitectura: DDD + Hexagonal (Ports & Adapters) | Flat AST V2 | CQRS/FSM |
              Functional Core / Imperative Shell | FinOps First | Fail-Fast
Fase actual completada: Fase 1 / F17-BIS (Production Pipeline Alignment)
Siguiente fase: Fase 18 (Advanced Local Runtime)
```

### 8.2 Code State

```text
Tests: 274 passed, 5 skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
Rama: main (estado limpio)
Commits: Todos los documentos FROZEN commiteados
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. ADR Maestro §4: PROHIBIDO infraestructura distribuida (Redis, Brokers, K8s, DBs remotas).
   SQLite WAL es el Core Engine (ROADMAP §V).

2. ADR Maestro §4: PROHIBIDO integrar nuevos adaptadores de extracción de visión.
   PyMuPDF es el provider vigente.

3. ADR Maestro §3: Separación estricta de identidades:
   - INTEGRIDAD (SHA-256 del archivo físico)
   - IDENTIDAD (hash compuesto encadenado)
   - REGRESIÓN (evaluación topológica TED + criticidad)
   NO COLAPSAR en un solo mecanismo.

4. NADR-11 §5.1 R1: apps/bootstrap/pipeline_factory.py es el ÚNICO
   punto de construcción del grafo de objetos. Todo entry point (CLI,
   worker, daemon) consume factories centralizadas.

5. ADR_F17_BIS_01 §4: "Lo que el benchmark evalúa es exactamente lo
   que producción ejecuta." Benchmark NO es un segundo pipeline.

6. Corolario P2: REUSED ≠ IDENTICAL, TRANSFORM ≠ VIOLATION.

7. ROADMAP §I Principio 7: Benchmark Before Optimization — cambios
   estructurales requieren evidencia estadística empírica.

8. ROADMAP §I Principio 8: Optimize Before Distribution — exprimir
   hardware local antes de considerar sistemas distribuidos.

9. ENGINEERING_PRINCIPLES §II: DTOs inmutables (frozen=True).
   Cero mutación in-place.

10. ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos. Fail-fast
    ante datos anómalos.
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
- docs/architecture/ENGINEERING_PRINCIPLES.md
- docs/architecture/PROJECT_SCOPE.md
- docs/architecture/ROADMAP_ARQUITECTONICO_LP.md
- docs/architecture/adr/phase-17-bis/handoff/FASE_1_HANDOFF.md (este)

Prioridad 2 (cargar para implementación):
- docs/architecture/adr/phase-17-bis/ADR/ADR_F17_BIS_MASTER.md
- docs/architecture/adr/phase-17-bis/NADR/NADR_{XX}_{Nombre}.md (relevantes)
- docs/architecture/adr/phase-17-bis/plans/PHASE_17BIS_EXECUTION_PLAN.md

Prioridad 3 (consultar según necesidad):
- docs/architecture/adr/phase-17-bis/reviews/FASE_1_DEFERRED_FINDINGS_REGISTER.md
- docs/architecture/adr/phase-17-bis/reviews/FASE_1_EXIT_REVIEW_EVIDENCE_LOG.md
- docs/architecture/PROJECT_TREE.txt
```

### 8.5 Pending Items (carry-forward)

```text
[DF-34] ProfileStore durable (no InMemoryProfileStore)
        → Bloquea Recovery Gate (Gate I)
        → Destino: Fase 18
        → Opciones: SQLiteProfileStore | Re-inferencia desde AST | Serialización en FSM

[DF-01-C] Linaje de identidad semántica en benchmark
          → Destino: Fase 2/3 (Identity & Trust Model)
          → Pregunta: ¿dónde viaja compute_ast_hash() en lineage?

[DF-12-C/D/E] Migrar FlatASTBuilder → list[LayoutBlock] directo
              → Destino: Fase 18
              → Elimina LayoutBlockDraft/LayoutBlockCollection

[DF-17] Extracción de imágenes (PyMuPDF type==1 descartado)
        → Destino: Fase 21 (Parser Routing)
        → Requiere asset management (no existe)

[DF-18] ExecutionContext unificado transversal
        → Destino: Fase 18 (coordinación) o Fase 20 (observabilidad)
        → 6 bounded contexts hoy; correcto pero fragmentado

[DF-24] CircuitBreakerStore persistente
        → Destino: Fase 18 SI se demuestra multi-proceso
        → Hoy: single-node (deque en memoria)

[DF-04] HARD_BREAK en StructuralChunkBoundaryPolicy
        → Destino: Post-Fase 18
        → Requiere semántica de contexto cruzado en AST V2
```

### 8.6 Work Conventions

```text
- Todo cambio requiere: Auditoría → ADR/NADR → Execution Plan → Tests → Verificación → Cierre documentado
- NO modificar NADRs FROZEN sin proceso explícito de superposición (nuevo ADR de mayor nivel)
- NO implementar código sin Execution Plan aprobado y tasks definidas
- Pyright DEBE reportar 0 errors antes de cualquier commit
- Pytest baseline (274 passed, 5 skipped) NO DEBE DEGRADARSE sin justificación documentada
- Los hallazgos se registran en Findings Register, no se implementan durante Exit Review
- Los batches de implementación agrupan hallazgos por afinidad, no por orden de aparición
- Los documentos siguen plantilla canónica v1.2.0 de METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
- Todo documento pasa por estados: DRAFT → APPROVED → FROZEN → ARCHIVED (según tipo)
```

### 8.7 System Entry Points

```text
apps/cli/main.py                          → CLI de usuario (entry point batch)
apps/llm_workers/__main__.py              → Daemon de workers LLM
apps/ocr_workers/__main__.py              → Daemon de workers OCR (reservado)
apps/compiler/__main__.py                 → AssemblerWorkerDaemon (ensamblado físico)
apps/daemons/reconciler.py                → ReconcilerDaemon (CQRS anti-entropy)
apps/daemons/chaos_runner.py              → Chaos engineering (Game Day)
core/benchmark/__main__.py                → Benchmark framework
tools/evaluation/run_benchmark.py         → Topological evaluation
```

Todos los entry points consumen factories centralizadas en `apps/bootstrap/`:
- `pipeline_factory.py` (pipeline de traducción)
- `provider_stack_factory.py` (stack LLM: CB → Cache → RateLimiter → Provider)
- `provider_factory.py` (providers OCR)

---

## 9. CLOSURE CRITERIA

Este handoff se considera cerrado (FROZEN) cuando:

- [x] Resumen ejecutivo completo (§1)
- [x] Estado actual validado con evidencia (§2)
- [x] Decisiones arquitectónicas documentadas (§3)
- [x] Scope entregado listado (§4)
- [x] Todos los items diferidos listados con destino (§5.2)
- [x] Restricciones carry-forward identificadas (§5.1)
- [x] Known risks documentados (§5.3)
- [x] Prerequisitos de siguiente fase definidos (§6)
- [x] Mapa de referencias completo (§7)
- [x] LLM Context Block autocontenido (§8)

**Veredicto:** ✅ CERRADO — FROZEN

---

**Nota de Gobernanza:** Este documento es el punto de transición entre Fase 1 (F17-BIS) y Fase 2 (F17-BIS).
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado exacto del
proyecto al cierre de la fase y proporcionar el contexto necesario para que cualquier agente
(humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4) para
tener contexto completo de arranque. Los detalles normativos se consultan bajo demanda según
la tarea específica.