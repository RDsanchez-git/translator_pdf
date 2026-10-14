# FASE_18.1_HANDOFF.md — Subfase 18.1: Execution Plane & Concurrency

**Documento:** `docs/architecture/adr/phase-18/handoff/FASE_18.1_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-10-07
**Fase completada:** Subfase 18.1 — Execution Plane & Concurrency
**Siguiente fase:** Subfase 18.2 — Durable Execution & Recovery (ADR_F18_MASTER §6)
**Derivado de:** `PHASE_18.1_EXECUTION_PLAN.md` v1.0.7 + `FASE_18_DEFERRED_FINDINGS_REGISTER.md` v1.0.7 + `FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md` v1.0.7

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-07 | Emisión inicial al cierre de la Subfase 18.1 |

---

## 1. EXECUTIVE SUMMARY

**1. ¿Qué se logró?** La Subfase 18.1 materializó el execution plane bounded y concurrente conforme a NADR-F18-01 (Execution Identity & Scientific Isolation, 20 reglas) y NADR-F18-02 (Bounded Concurrent Execution, 32 reglas). Se implementaron los mecanismos de bounded execution, admission/backpressure, cancellation/shutdown, operational visibility e identity traceability sobre el modelo híbrido decidido en DC-01 (daemon secuencial + SyncProviderBridge). Se evaluaron las técnicas candidatas de DC-06b. Se corrigió la fórmula de execution_id en el contrato de identidad (v1.0.1→v1.0.2) alineándola con NADR-F17BIS-28. Estado final: **COMPLETED** — 52/52 reglas NADR DONE, 32/32 Tasks DONE, 4/4 Gates COMPLETED.

**2. ¿Cuál es el estado actual?** La suite de tests alcanza 854 passed (1 warning cosmético de google.generativeai no relacionado), pyright 0 errors, lint-imports 4 contratos KEPT / 0 BROKEN. Se analizaron 6 hallazgos: 5 RESOLVED (DF-06, DF-07, DF-09, DF-13, GF-01) y 1 CLOSED NAR (DF-08). Cero hallazgos pendientes. La regresión SMOKE produce scientific_verdict=HARD_FAIL (exit_code=2), condición pre-existente y legítima del corpus canónico documentada en HITO_0.7 v1.1.0 (no introducida por 18.1). NADR-F18-02 permanece en DRAFT; debe promoverse a FROZEN antes de iniciar 18.2.

**3. ¿Qué necesita la siguiente fase?** La Subfase 18.2 (Durable Execution & Recovery) requiere respetar la frontera mecanismo/política establecida en 18.1 (los mecanismos admission/backpressure son puertos abstractos; la política de recursos corresponde a 18.3). Debe implementar la semántica de recuperación de estado persistente tras shutdown (explícitamente excluida de 18.1 por NADR-F18-02 §5.4 R15), resolver DC-08 (write-policy SQLite + mecanismo de journal de INV-JOURNAL) y DC-13 (coordinated shutdown durable), y absorber DF-24 (persistencia de Circuit Breaker) y DF-34 (persistencia de ProfileStore). Debe preservar INV-SCI-1, INV-VERIFICATION-ISOLATION y la frontera hexagonal sin excepciones.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `main` |
| Commit hash de cierre | {a completar con el SHA del commit de cierre} |
| Estado del árbol | Limpio (al momento del cierre) |
| Baseline de tests | **854 passed, 1 warning cosmético** (no debe degradarse sin justificación) |
| Pyright / Type checker | **0 errors, 0 warnings** |
| Imports huérfanos | 0 detectados (grep frontera hexagonal vacío) |
| lint-imports | **4 contratos KEPT / 0 BROKEN** |

### 2.2 Validation Results

```text
pyright core/ apps/ infra/ runtime/                          # 0 errors, 0 warnings ✅
pytest tests/unit/                                           # 854 passed ✅
lint-imports                                                 # 4 KEPT / 0 BROKEN ✅
pytest tests/integration/test_recovery_flow.py               # PASSED ✅
python -m tools.evaluation.run_regression --profile SMOKE    # exit 2 (HARD_FAIL basal, pre-existente) ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR_F18_MASTER | FROZEN | v1.0.0 |
| ADR_F18.1 | FROZEN | v1.0.2 |
| NADR-F18-01 | FROZEN | v1.0.3 |
| NADR-F18-02 | **DRAFT** | v1.0.1 |
| F18_IDENTITY_BOUNDARY_CONTRACT | FROZEN | v1.0.2 |
| F18_DC01_DECISION | FROZEN | v1.0.0 |
| F18_DC05_DECISION | FROZEN | v1.0.0 |
| F18_DC06b_EVALUATION_REPORT | FROZEN | v1.0.0 |
| PHASE_18.1_EXECUTION_PLAN | COMPLETED | v1.0.7 |
| FASE_18_DEFERRED_FINDINGS_REGISTER | COMPLETED | v1.0.7 |
| FASE_18_EXIT_REVIEW_EVIDENCE_LOG | COMPLETED | v1.0.7 |
| METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES | FROZEN | v1.3.0 |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | 6 |
| Hallazgos resueltos | 5 (DF-06, DF-07, DF-09, DF-13, GF-01) |
| Hallazgos cerrados sin acción (NAR) | 1 (DF-08) |
| Hallazgos diferidos a fase futura | 0 |
| Gates ejecutados | 4 (todos COMPLETED) |
| Archivos eliminados | 1 (core/telemetry/adapters.py) |
| Archivos movidos | 3 (DF-06: groq_runner, gemini_runner, __main__.py → apps/benchmark/) |
| Archivos creados | ~20 (mecanismos core/execution, runtime/, tests, documentos) |
| Archivos modificados | ~6 (apps/llm_workers/__main__.py, report.py, run_regression.py, pyproject.toml, etc.) |

---

## 3. ARCHITECTURAL DECISIONS MADE

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | DC-01: Mantener modelo híbrido (daemon secuencial + SyncProviderBridge) | Fork de concurrencia; se evaluaron async puro y multi-process | ENGINEERING_PRINCIPLES §VII (Reuse Before Invent); ADR_F18_MASTER §5.2 (Benchmark Before Optimization). Benchmark: overhead 2-10ms, throughput 1.00x, RSS 0.02 MB | F18_DC01_DECISION.md v1.0.0 |
| AD-02 | DC-02-A: Contrato provisional de identidad en 3 dimensiones ortogonales | Definir frontera scientific/execution/operational identity (GAP-0.4-03) | NADR-F18-01 §5.1-§5.4; cláusula de invalidación con 3 condiciones + escalación | F18_IDENTITY_BOUNDARY_CONTRACT.md v1.0.2 |
| AD-03 | DC-05: Ratificar Specialized Contexts (CQRS) | Estructura de contextos de ejecución | ENGINEERING_PRINCIPLES §I (YAGNI), §II (Hexagonal); God-Object Test: 6 contextos sin solapamiento | F18_DC05_DECISION.md v1.0.0 |
| AD-04 | DF-13 Opción B: model_de_execution como metadata operacional | INV-EXEC-IDENTIFIABILITY parcial | NADR-F18-01 §5.2 R7/R9/R8 (identity_chain intacto, backward-compatible) | execution_metadata.py + reporte SMOKE |
| AD-05 | DF-06 destino apps/benchmark/runners/ (NO infra/) | Refactor de frontera hexagonal | Contrato 2 de import-linter prohíbe infra→apps | lint-imports 4 KEPT / 0 BROKEN |
| AD-06 | DC-06b evaluado pero NO resuelto | Decisión de Board compartida 18.1-18.4 | PHASE_18.1_EXECUTION_PLAN §2D.3 | F18_DC06b_EVALUATION_REPORT.md v1.0.0 |
| AD-07 | Contrato v1.0.1→v1.0.2: fórmula execution_id corregida | Contrato decía hash(baseline+config+profile+result) pero código excluye result, incluye subject y parameter | NADR-F17BIS-28 §5.1 R6 (Execution precede a Result), §5.2 R13 (result no sustituye entradas), §5.1 R3/R5 | Gate 4 Task 4.1.1 |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

| Capacidad | NADR | Estado |
|-----------|------|--------|
| Bounded execution (resource envelope) | NADR-F18-02 §5.1 | ✅ DONE |
| Admission mechanism (puerto abstracto) | NADR-F18-02 §5.2 | ✅ DONE |
| Backpressure mechanism (puerto abstracto) | NADR-F18-02 §5.3 | ✅ DONE |
| Cancellation cooperativa | NADR-F18-02 §5.4 | ✅ DONE |
| Shutdown ordenado (sin recovery) | NADR-F18-02 §5.4 R15 | ✅ DONE |
| Concurrency safety (primitivos) | NADR-F18-02 §5.5 | ✅ DONE |
| Execution context (6 boundaries) | NADR-F18-02 §5.6 | ✅ DONE |
| Operational visibility mínima | NADR-F18-02 §5.7 | ✅ DONE |
| Scientific neutrality | NADR-F18-02 §5.8 | ✅ DONE (verificado dinámicamente) |
| Measurement & decision evidence | NADR-F18-02 §5.9 | ✅ DONE |
| Execution identity isolation | NADR-F18-01 §5.1-§5.5 | ✅ DONE |

### 4.2 Archivos clave creados/modificados

**Creados (mecanismos):**
- `core/execution/models.py` — ExecutionEnvelope (frozen)
- `core/execution/exceptions.py` — ResourceExhaustedError, TaskCancelledError
- `core/execution/ports.py` — ResourceMonitorPort
- `core/execution/coordination.py` — CoordinationPrimitives
- `core/execution/context_boundaries.py` — ContextBoundary + 6 boundaries
- `core/execution/admission.py` — AdmissionMechanismPort
- `core/execution/backpressure.py` — BackpressureMechanismPort
- `core/execution/cancellation.py` — TaskOutcome, CancellationToken
- `core/execution/shutdown.py` — ShutdownReport, ShutdownMechanismPort
- `core/execution/visibility.py` — WorkUnitStatus, WorkUnitObservation, OperationalVisibilityPort
- `runtime/admission_mechanism.py` — SequentialAdmissionMechanism
- `runtime/backpressure_mechanism.py` — SequentialBackpressureMechanism
- `runtime/coordinated_shutdown.py` — CoordinatedShutdownMechanism
- `runtime/operational_visibility.py` — StructuredLogVisibility
- `infra/os/resource_monitor.py` — PsutilSelfResourceMonitor
- `core/benchmark/verification/execution_metadata.py` — ExecutionMetadata
- `core/telemetry/regression_gateway.py` — RegressionTelemetryGateway

**Creados (documentos):**
- `docs/architecture/adr/phase-18/reports/F18_IDENTITY_BOUNDARY_CONTRACT.md` v1.0.2
- `docs/architecture/adr/phase-18/reports/F18_DC01_DECISION.md` v1.0.0
- `docs/architecture/adr/phase-18/reports/F18_DC05_DECISION.md` v1.0.0
- `docs/architecture/adr/phase-18/reports/F18_BASELINE_CONCURRENCY.md` v1.0.0
- `docs/architecture/adr/phase-18/reports/F18_BASELINE_METRICS_PER_STAGE.md` v1.0.0
- `docs/architecture/adr/phase-18/reports/F18_DC06b_EVALUATION_REPORT.md` v1.0.0

**Modificados significativamente:**
- `apps/llm_workers/__main__.py` — Integración de todos los mecanismos (admission, backpressure, cancellation, visibility, shutdown)
- `apps/llm_workers/sync_bridge.py` — Token de cancelación integrado
- `core/benchmark/verification/report.py` — Campo execution_metadata
- `tools/evaluation/run_regression.py` — ExecutionMetadata + telemetry
- `pyproject.toml` — ignore_imports actualizados (DF-06 resuelto)

**Eliminados (zombies y deuda):**
- `core/telemetry/adapters.py` — GF-01 (NullTelemetryAdapter duplicado muerto)

**Movidos (DF-06):**
- `core/benchmark/runners/groq_runner.py` → `apps/benchmark/runners/groq_runner.py`
- `core/benchmark/runners/gemini_runner.py` → `apps/benchmark/runners/gemini_runner.py`
- `core/benchmark/__main__.py` → `apps/benchmark/__main__.py`

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

| Restricción | Fuente | Relevancia para 18.2 |
|-------------|--------|----------------------|
| Scientific identity NO se altera por cambios operacionales | INV-SCI-1 (ADR_F18_MASTER §5.1) | Cualquier mecanismo de recovery/journal de 18.2 debe ser operacionalmente neutro |
| Execution identity NO contamina scientific identity | NADR-F18-01 §5.2 R8 | Los artefactos de recovery de 18.2 son execution/operational identity, no scientific |
| execution_id = hash(baseline + subject + config + parameter + profile). NO incluye result | F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2; NADR-F17BIS-28 §5.1 R6/§5.2 R13 | 18.2 no debe alterar la fórmula de execution_id ni agregar result |
| Verification subject corre sin scheduler ni concurrencia | INV-VERIFICATION-ISOLATION (ADR_F18_MASTER §5.1) | 18.2 no debe introducir concurrencia en el verification path |
| Shutdown ordenado implementado; recovery de estado persistente es 18.2 | NADR-F18-02 §5.4 R15 | El CoordinatedShutdownMechanism de 18.1 NO hace recovery; 18.2 debe implementarlo sin invadir el shutdown |
| Mecanismos admission/backpressure son puertos abstractos | NADR-F18-02 §5.2 R7, §5.3 R10 | 18.2 no debe implementar política de recursos (eso es 18.3) |
| Frontera hexagonal: core/ no importa de apps/ ni infra/ | ENGINEERING_PRINCIPLES §II | 18.2 debe mantener la frontera sin excepciones |
| Agotamiento de budget ⇒ EXECUTION_FAILURE, nunca REGRESSION/PASS | INV-NO-RESOURCE-SIGNAL (ADR_F18_MASTER §5.1) | Los mecanismos de recovery de 18.2 no deben reinterpretar exit codes |
| Diferencias operacionales no falsifican evidencia científica | INV-OPS-1 (ADR_F18_MASTER §5.1) | El journal/leases de 18.2 son operational state, no deben afectar scientific evidence |
| Ningún efecto externo sin intención/lease recuperable tras crash | INV-JOURNAL (ADR_F18_MASTER §5.1) | 18.2 debe garantizar idempotent apply y ventana de duplicación acotada |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| DC-06b | Evaluación de técnicas candidatas (1 CAE, 5 requieren evidencia adicional) | Subfases 18.2-18.4 | Nada (decisión de Board) |
| DF-24 | Persistencia de Circuit Breaker (subsumido en DC-08) | Subfase 18.2 | Nada hasta DC-08 |
| DF-34 | Persistencia de ProfileStore | Subfase 18.2 | Nada hasta DC-01 + cuantificación |
| GAP-0.7-05 | Sin thresholds numéricos: MDE/Δ/ε abiertos | F0-D + Execution Plan | Nada (calibración de técnicas) |
| GAP-0.7-06 | INV-SCI-1 end-to-end y completion order no demostrados | Subfase 18.5 (DC-12, M1) | DC-12 |
| Observación HARD_FAIL basal | scientific_verdict=HARD_FAIL en corpus canónico | Subfase 17-BIS o 18.5 (DC-12) | Nada (condición legítima) |
| Observación handlers.py | core/execution/handlers.py → infra.db.fsm_repository | Refactor futuro (deuda Fase 17) | Nada |
| Observación runtime/engine.py | runtime/engine.py → apps/ (3 imports) | Refactor futuro | Nada |

### 5.3 Known Risks & Caveats

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| NADR-F18-02 en DRAFT | NADR-F18-02 v1.0.1 no fue promovido a FROZEN durante 18.1 | Debe promoverse a FROZEN antes de iniciar 18.2 |
| HARD_FAIL basal en corpus | La regresión SMOKE produce exit_code=2 por condición legítima del corpus (NSS 0.6385 < threshold). Puede confundirse con regresión real. | Documentado en HITO_0.7 v1.1.0; los exit codes no se reinterpretan; el plano científico está separado del plano de validez de medición |
| Comparación multi-modo pendiente | DC-01 decidió mantener un solo modo; INV-SCI-1 end-to-end bajo variación operacional no demostrado | Diferido a DC-12 (Subfase 18.5); la verificación actual cubre el modo único |
| safety_margin=0.90 hardcoded | SequentialAdmissionMechanism tiene default 0.90; podría considerarse política | Es un default configurable inyectable; la política corresponde a 18.3 |
| Deuda handlers.py | core/execution/handlers.py importa de infra.db.fsm_repository | En ignore_imports de pyproject.toml; resolución corresponde a refactor futuro |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ Modelo de concurrencia decidido (DC-01: modelo híbrido)
- ✅ Mecanismos de bounded execution, admission/backpressure, cancellation/shutdown implementados
- ✅ Primitivos de coordinación (CoordinationPrimitives) disponibles
- ✅ Context boundaries documentados (6 contextos)
- ✅ Identity boundary contract FROZEN v1.0.2
- ✅ Baselines de concurrencia y métricas por etapa FROZEN
- ✅ Telemetría por etapa integrada (RegressionTelemetryGateway)
- ✅ Suite de tests en verde (854 passed)

**Lo que se necesita antes de arrancar:**
- Promover NADR-F18-02 v1.0.1 de DRAFT a FROZEN (Architecture Board)
- Resolver DC-08 (write-policy SQLite + mecanismo de journal de INV-JOURNAL) — decisión arquitectónica de 18.2
- Resolver DC-13 (coordinated shutdown durable) — decisión arquitectónica de 18.2
- Absorber DF-24 (persistencia de Circuit Breaker, subsumido en DC-08)
- Absorber DF-34 (persistencia de ProfileStore)
- Definir el scope de journal/leases/fencing de 18.2 sin invadir el shutdown de 18.1

### 6.2 Next Phase Handoff Checklist

- [ ] Cargar este handoff + los documentos de Prioridad 1 (§8.4)
- [ ] Verificar que el árbol de trabajo está limpio (git status)
- [ ] Confirmar que la suite de tests está en verde (pytest tests/unit/)
- [ ] Confirmar que pyright está en 0 errors
- [ ] Promover NADR-F18-02 de DRAFT a FROZEN
- [ ] Leer NADR-F18-01 y NADR-F18-02 (reglas constitucionales)
- [ ] Leer ADR_F18.1 (visión de la Subfase 18.2)
- [ ] Identificar los DCs pendientes de 18.2 (DC-08, DC-13)
- [ ] Respetar la frontera mecanismo/política (no implementar política de recursos)
- [ ] Respetar INV-SCI-1, INV-JOURNAL e INV-VERIFICATION-ISOLATION en cualquier cambio

### 6.3 ROADMAP — Objetivos de la siguiente fase

La Subfase 18.2 (Durable Execution & Recovery) según ADR_F18_MASTER §6:

1. **Journal semantics** — Definir e implementar la semántica del journal conforme a INV-JOURNAL: ningún efecto externo sin intención/lease recuperable tras crash y aplicación idempotente del resultado.
2. **Recovery & fencing** — Implementar crash recovery, epoch fencing, zombie handling y ventana de duplicación acotada y medida.
3. **Write-policy SQLite (DC-08)** — Decidir la política de escritura duradera y el mecanismo que garantice idempotent apply.
4. **Coordinated shutdown durable (DC-13)** — Extender el shutdown ordenado de 18.1 con semántica de recuperación, sin invadir el mecanismo de shutdown ya implementado.
5. **Durable authorities (DF-24, DF-34)** — Resolver persistencia de Circuit Breaker y ProfileStore (autoridades actualmente in-memory).

**Hito crítico:** Al final de 18.2, el execution plane debe ser capaz de recuperarse de un crash sin pérdida de trabajo, sin corrupción de estado, con idempotent apply garantizado, y sin violar INV-SCI-1 ni INV-VERIFICATION-ISOLATION.

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| ADR_F18.2 | Plantilla canónica ADR | Visión y alcance de la Subfase 18.2 |
| NADR-F18-03 | Plantilla canónica NADR | Reglas constitucionales de Durable Execution & Recovery |
| PHASE_18.2_EXECUTION_PLAN | Plantilla canónica Execution Plan | Secuenciación operativa de 18.2 |
| FASE_18.2_DEFERRED_FINDINGS_REGISTER | Plantilla canónica Findings Register | Registro de hallazgos de 18.2 |
| FASE_18.2_EXIT_REVIEW_EVIDENCE_LOG | Plantilla canónica Evidence Log | Evidencia forense de 18.2 |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| ADR_F18_MASTER | `docs/architecture/adr/phase-18/ADR/ADR_F18_MASTER.md` |
| ADR_F18.1 | `docs/architecture/adr/phase-18/ADR/ADR_F18_1.md` |
| NADR-F18-01 | `docs/architecture/adr/phase-18/NADR/NADR-F18-01.md` |
| F18_IDENTITY_BOUNDARY_CONTRACT | `docs/architecture/adr/phase-18/reports/F18_IDENTITY_BOUNDARY_CONTRACT.md` |
| F18_DC01_DECISION | `docs/architecture/adr/phase-18/reports/F18_DC01_DECISION.md` |
| F18_DC05_DECISION | `docs/architecture/adr/phase-18/reports/F18_DC05_DECISION.md` |
| F18_BASELINE_CONCURRENCY | `docs/architecture/adr/phase-18/reports/F18_BASELINE_CONCURRENCY.md` |
| F18_BASELINE_METRICS_PER_STAGE | `docs/architecture/adr/phase-18/reports/F18_BASELINE_METRICS_PER_STAGE.md` |
| F18_DC06b_EVALUATION_REPORT | `docs/architecture/adr/phase-18/reports/F18_DC06b_EVALUATION_REPORT.md` |
| ENGINEERING_PRINCIPLES | `docs/architecture/ENGINEERING_PRINCIPLES.md` |
| METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES | `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` |

### 7.2 DRAFT documents (requieren promoción)

| Documento | Ruta | Acción requerida |
|-----------|------|-----------------|
| NADR-F18-02 | `docs/architecture/adr/phase-18/NADR/NADR-F18-02.md` | Promover de DRAFT a FROZEN antes de 18.2 |

### 7.3 COMPLETED documents

| Documento | Ruta |
|-----------|------|
| PHASE_18.1_EXECUTION_PLAN v1.0.7 | `docs/architecture/adr/phase-18/plans/PHASE_18.1_EXECUTION_PLAN.md` |
| FASE_18_DEFERRED_FINDINGS_REGISTER v1.0.7 | `docs/architecture/adr/phase-18/reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md` |
| FASE_18_EXIT_REVIEW_EVIDENCE_LOG v1.0.7 | `docs/architecture/adr/phase-18/reviews/FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md` |

### 7.4 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| HITO_0.7 v1.1.0 | `docs/architecture/adr/phase-18/00-foundation/HITO_0.7_F0-A_Runtime_Profile_Baseline.md` | Baseline operacional y HARD_FAIL basal |
| ROADMAP_ARQUITECTONICO_LP | `docs/architecture/ROADMAP_ARQUITECTONICO_LP.md` | Roadmap de largo plazo |
| PROJECT_SCOPE | `docs/architecture/PROJECT_SCOPE.md` | Alcance del proyecto |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: translator_pdf
Descripción: Sistema de traducción de PDFs científicos/técnicos con preservación de estructura, semántica y layout mediante AST. Fase activa: 18 (Advanced Local Runtime).
Stack: Python 3.11, SQLite (WAL), psutil, import-linter, pyright, pytest
Arquitectura: DDD + Hexagonal (Ports and Adapters), CQRS, Functional Core / Imperative Shell
Fase actual completada: Subfase 18.1 (Execution Plane & Concurrency)
Siguiente fase: Subfase 18.2 (Durable Execution & Recovery)
```

### 8.2 Code State

```text
Tests: 854 passed, 1 warning cosmético (BASELINE — NO DEBE DEGRADARSE)
Pyright: 0 errors, 0 warnings
lint-imports: 4 contratos KEPT / 0 BROKEN
Rama: main (limpio al cierre)
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. INV-SCI-1: Misma baseline + mismos parámetros científicos congelados ⇒ misma salida científica, independiente de schedule/concurrencia/budgets/cache.
2. INV-VERIFICATION-ISOLATION: El verification subject corre sin scheduler ni concurrencia por defecto.
3. INV-NO-RESOURCE-SIGNAL: Agotamiento de budget ⇒ EXECUTION_FAILURE con evidencia persistida; nunca REGRESSION/PASS.
4. INV-OPS-1: Las diferencias operacionales no alteran el resultado científico ni falsifican la evidencia científica.
5. INV-JOURNAL: Ningún efecto externo sin intención/lease recuperable tras crash; idempotent apply y ventana de duplicación acotada.
6. NADR-F18-01 §5.2 R8: Execution identity MUST NOT formar parte de scientific identity.
7. F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2: execution_id = hash(baseline + subject + config + parameter + profile). NO incluye result. Cualquier modificación requiere aprobación del Architecture Board.
8. NADR-F18-02 §5.4 R15: Shutdown ordenado implementado en 18.1; la semántica de recuperación de estado persistente tras shutdown corresponde a 18.2.
9. ENGINEERING_PRINCIPLES §II: Arquitectura Hexagonal — core/ no importa de apps/ ni infra/.
10. ENGINEERING_PRINCIPLES §III: Explicit over Implicit — toda decisión arquitectónica debe ser explícita y trazable.
11. Frontera mecanismo/política: los mecanismos admission/backpressure son puertos abstractos; la política de recursos corresponde a 18.3.
12. NADR-F18-01 §5.1 R4: Ninguna modificación del mecanismo de ejecución debe alterar la scientific identity ni la evidencia científica canónica.
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- docs/architecture/adr/phase-18/handoff/FASE_18.1_HANDOFF.md (este documento)
- docs/architecture/adr/phase-18/ADR/ADR_F18_MASTER.md
- docs/architecture/ENGINEERING_PRINCIPLES.md

Prioridad 2 (cargar para implementación de 18.2):
- docs/architecture/adr/phase-18/NADR/NADR-F18-01.md
- docs/architecture/adr/phase-18/NADR/NADR-F18-02.md
- docs/architecture/adr/phase-18/ADR/ADR_F18_1.md
- docs/architecture/adr/phase-18/reports/F18_IDENTITY_BOUNDARY_CONTRACT.md

Prioridad 3 (consultar según necesidad):
- docs/architecture/adr/phase-18/plans/PHASE_18.1_EXECUTION_PLAN.md
- docs/architecture/adr/phase-18/reviews/FASE_18_DEFERRED_FINDINGS_REGISTER.md
- docs/architecture/adr/phase-18/reviews/FASE_18_EXIT_REVIEW_EVIDENCE_LOG.md
- docs/architecture/adr/phase-18/00-foundation/HITO_0.7_F0-A_Runtime_Profile_Baseline.md
- docs/architecture/ROADMAP_ARQUITECTONICO_LP.md
```

### 8.5 Pending Items (carry-forward)

```text
[DC-08] Write-policy SQLite + mecanismo de journal de INV-JOURNAL
       → Destino: Subfase 18.2
       → Bloquea: Implementación de journal y recovery
       → Opciones: Pendiente de decisión en 18.2

[DC-13] Coordinated shutdown durable
       → Destino: Subfase 18.2
       → Bloquea: Extensión del shutdown con semántica de recuperación
       → Opciones: Pendiente de decisión en 18.2

[DF-24] Persistencia de Circuit Breaker (subsumido en DC-08)
       → Destino: Subfase 18.2
       → Bloquea: Nada hasta DC-08
       → Opciones: Resolver junto con DC-08

[DF-34] Persistencia de ProfileStore
       → Destino: Subfase 18.2
       → Bloquea: Nada hasta cuantificación de coste de re-inferencia
       → Opciones: Resolver junto con DC-08

[DC-06b] Evaluación de técnicas candidatas (1 CAE, 5 requieren evidencia)
       → Destino: Subfases 18.2-18.4
       → Bloquea: Nada (decisión de Board)
       → Opciones: F18_DC06b_EVALUATION_REPORT.md emitido

[GAP-0.7-06] INV-SCI-1 end-to-end y completion order no demostrados
       → Destino: Subfase 18.5 (DC-12, M1)
       → Bloquea: DC-12
       → Opciones: Experimento M1 del guard diferencial

[NADR-F18-02] Promover de DRAFT a FROZEN
       → Destino: Architecture Board
       → Bloquea: Inicio formal de Subfase 18.2
       → Opciones: Revisión y aprobación del Board

[OBS-HARD_FAIL] scientific_verdict=HARD_FAIL basal en corpus canónico
       → Destino: Subfase 17-BIS (re-calibración) o 18.5 (DC-12)
       → Bloquea: Nada (condición legítima según HITO_0.7 v1.1.0)
       → Opciones: Re-calibración del corpus o aceptación como baseline

[OBS-handlers] core/execution/handlers.py → infra.db.fsm_repository
       → Destino: Refactor futuro (deuda Fase 17)
       → Bloquea: Nada
       → Opciones: Refactor a puerto + inyección
```

### 8.6 Work Conventions

```text
- Implementación primero, gobernanza después: no actualizar documentos de gobernanza hasta que el usuario lo indique.
- No sobreingeniería: YAGNI estricto; no crear archivos ni tests innecesarios.
- Verificación forense antes de fixear: ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos).
- Benchmark Before Optimization: ADR_F18_MASTER §5.2.
- Reuse Before Invent: ENGINEERING_PRINCIPLES §VII.
- Frontera hexagonal sin excepciones: core/ no importa de apps/ ni infra/.
- Mecanismos son puertos abstractos; las políticas corresponden a subfases posteriores.
- Los exit codes no se reinterpretan: 0,1,2 = medición válida; 3,4 = invalidación.
- El plano científico está separado del plano operacional y del plano de validez de medición.
- Los hallazgos se registran en el Findings Register, no en el Execution Plan ni en el código.
```

### 8.7 System Entry Points

```text
apps/cli/main.py                                → CLI principal (entry point de producción)
apps/llm_workers/__main__.py                    → Daemon LLMWorkerDaemon (entry point del execution plane)
apps/ocr_router/__main__.py                     → Daemon OCR Router
apps/compiler/__main__.py                       → Ensamblador de documentos (composition root)
apps/benchmark/__main__.py                      → Benchmark runners (movido de core/ por DF-06)
tools/evaluation/run_regression.py              → Continuous Verification entry point
tools/evaluation/benchmark_sync_bridge.py       → Instrumento de medición efímero (Gate 1)
apps/bootstrap/pipeline_factory.py              → Factory centralizada del pipeline de extracción
apps/bootstrap/provider_stack_factory.py        → Factory de provider stack LLM
```

Los composition roots están en `apps/bootstrap/` (pipeline_factory, provider_stack_factory, provider_factory). Los mecanismos de 18.1 están en `core/execution/` (puertos) y `runtime/` (implementaciones). Los adaptadores de infraestructura están en `infra/`.

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

**Nota de Gobernanza:** Este documento es el punto de transición entre fases.
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado
exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que
cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4)
para tener contexto completo de arranque. Los detalles normativos se consultan bajo
demanda según la tarea específica.