# FASE_1_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_1_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 1.0.0
**Estado:** ARCHIVED
**Fecha de creación:** 2026-08-19
**Última actualización:** 2026-08-19
**Derivado de:** `PHASE_17BIS_EXECUTION_PLAN.md` v3.0.0
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan, su clasificación, resolución y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_01 > NADR-01..11 > PHASE_17BIS_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Scientific Baseline sea
> una representación determinista, reproducible y arquitectónicamente fiel
> del pipeline productivo que vamos a certificar?"*

### 0.3 Reglas transversales aplicables

> **Regla de separación Benchmark/Producción (ADR_F17_BIS_01 §4):**
> *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta,
> y lo que producción ejecuta es exactamente lo que la arquitectura declara."*

> **Corolario forense P2:**
> `REUSED ≠ IDENTICAL` y `TRANSFORM ≠ VIOLATION`. El benchmark es un
> subproducto controlado del production pipeline, no una segunda
> implementación. No confundir reutilización de capacidades con identidad
> de pipelines.

> **Separación de identidades (ADR Maestro §3 y §5):**
> *"Integridad no implica Identidad."* La arquitectura mantiene diferenciados
> los conceptos de AST Schema Version, Corpus Version e Identity Hash.
> No todos los hashes deben colapsarse en un único mecanismo.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `RESOLVED — PRODUCTION ALIGNMENT` | Alineado con stack de producción |
| `RESOLVED — SQLITE_RATE_LIMIT_STORE` | Backend persistente implementado |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Diferido a fase futura con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `DEFERRED — FASE {X}` | Diferido a fase específica con ADR pendiente |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos/documentos auditados.
- Cada finding **DEBE** distinguir: (a) gap confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún finding se cierra sin evidencia de código o documental.
- No se implementa código durante el Exit Review. La implementación se agrupa en batches posteriores.

### 1.4 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Fase cerrada | Estado del documento → `ARCHIVED` |

---

## 2. GATE EXIT REVIEWS

### 2.1 Gate 3 Exit Review (2026-08-07)

**Árbol de decisión aplicado:**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
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

### 2.2 Gate 4 Partial Exit Review — Wave 4.2 (2026-08-08)

**Nota:** Gate 4 alcanza 24/24 reglas propias DONE. GF-01 (2 reglas de Gate 3) sigue pendiente como Governance Finding.

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
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

#### Decisiones arquitectónicas congeladas en Gate 4

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

#### Lecciones aprendidas Gate 4

- El enfoque audit-first (census → diseño → implementación) previno 3 bloqueadores arquitectónicos (import circular, semántica OMIT, doble reconstrucción).
- La separación de planos (Resolver valida / Assembler decide / Service materializa) eliminó la doble materialización de contenido.
- `DispatchResult` como contrato inter-stage era la raíz del acoplamiento entre el pipeline lógico y el daemon físico.
- Los tests que dependían del ensamblado lógico quedaron obsoletos correctamente (el ensamblado es asíncrono).

---

## 3. TABLA CONSOLIDADA FINAL

### 3.1 Resumen por clasificación (estado inicial post-Exit Review)

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 6 | DF-03, DF-07, DF-20, DF-21, DF-22, GF-01 |
| `RESOLVED — DELETE` | 4 | DF-10, DF-14, DF-25, DF-29 |
| `RESOLVED` | 2 | DF-13, DF-16 |
| `IMPLEMENTATION_REQUIRED` | 7 | DF-01, DF-02, DF-11, DF-12, DF-26, DF-27, DF-28 |
| `RECLASSIFIED_FUTURE_PHASE` | 5 | DF-04, DF-17, DF-18, DF-24, DF-34 |
| `REVIEW_REQUIRED` | 2 | DF-19, H-11-A |
| `ACCEPTED_LIMITATION` | 2 | DF-15, DF-31 |

### 3.2 Tabla consolidada (estado final post-implementación)

| DF | Estado Final | Decisión |
|----|--------------|----------|
| GF-01 | `CLOSED — NORMATIVE COMPATIBILITY ESTABLISHED` | Reconciliación normativa. SQLite WAL local satisface NADR-08 sin infra distribuida. |
| DF-01-A | `RESOLVED — REFACTORED` | Centralización criptográfica en `core/shared/crypto.py`. |
| DF-01-B | `CLOSED (NAR)` | Falso positivo: `node_sha` por chunk y `compute_ast_hash()` por documento son ortogonales. |
| DF-01-C | `DEFERRED — FASE 2/3` | Requiere ADR de diseño sobre linaje de identidad semántica en Scientific Baseline. |
| DF-01-D | `CLOSED (NAR)` | Agregar `ast_hash` a `DocumentFingerprint` violaría ADR Maestro §3. |
| DF-02 | `RESOLVED — REFACTORED` | Patrón `hasattr` eliminado en 4 archivos (DF-02-A + DF-02-B). |
| DF-03 | `CLOSED (NAR)` | `tools/benchmark_archive/` archivado. Fuera de alcance. |
| DF-04 | `RECLASSIFIED_FUTURE_PHASE` | AST sin contexto cruzado. HARD_BREAK requiere semántica futura. Destino: post-Fase 18. |
| DF-07 | `CLOSED (NAR)` | 5 dependencias legítimas. NADR-11 cumplido. YAGNI aplica. |
| DF-10 | `RESOLVED — DELETE` | 3 archivos eliminados (router.py, ports.py, pdf_router.py). |
| DF-11 | `RESOLVED — MOVE` | 3 providers movidos de `core/` a `infra/extraction/providers/`. |
| DF-12-A | `RESOLVED — DELETE` | `DocumentLayoutBuilder` eliminado (0 instancias). |
| DF-12-B | `RESOLVED — DELETE` | 6 stages zombis del layout eliminados. |
| DF-12-C/D/E | `RECLASSIFIED_FUTURE_PHASE` | Migración `FlatASTBuilder` → `list[LayoutBlock]`. Refactor de contrato. Destino: Fase 18. |
| DF-13 | `RESOLVED` | Test consulta `parser.capabilities`. Capacidades específicas por provider. |
| DF-14 | `RESOLVED — DELETE` | `LogicalClassifier` eliminado (zombi, 0 instancias). |
| DF-15 | `ACCEPTED_LIMITATION` | PyMuPDF no detecta tablas/ecuaciones/imágenes. Limitación documentada. |
| DF-16 | `RESOLVED — ACCEPTED SEPARATION` | Taxonomías ortogonales por diseño. Mapeo centralizado en `FlatASTBuilder._TYPE_MAPPING`. |
| DF-17 | `RECLASSIFIED_FUTURE_PHASE` | Extracción de imágenes requiere asset management. Destino: Fase 21. |
| DF-18 | `RECLASSIFIED_FUTURE_PHASE` | `AssemblyExecutionContext` ≠ `ExecutionContext` unificado. Destino: Fase 18/20. |
| DF-19 | `RESOLVED` | Resuelto por DF-26 (factory extraction). `build_pipeline()` ya no es God Factory. |
| DF-20 | `CLOSED (NAR)` | Dispatcher delega vía DI (`ContextResolverProtocol`). NADR-05 satisfecho. |
| DF-21 | `CLOSED (NAR)` | Registries de bounded contexts distintos. Sin contrato común que abstraer. |
| DF-22 | `CLOSED (NAR)` | Snapshot intencional (`MappingProxyType`). Semántica de determinismo. |
| DF-24 | `RECLASSIFIED_FUTURE_PHASE` | CB en memoria suficiente para single-node. Destino: Fase 18 si se demuestra necesidad. |
| DF-25 | `RESOLVED — DELETE` | `CQRSReconciliationDaemon` eliminado (subconjunto estricto de `ReconcilerDaemon`). |
| DF-26 | `RESOLVED — FACTORY EXTRACTION` | `build_provider_stack()` extraído a `apps/bootstrap/provider_stack_factory.py`. |
| DF-27 | `RESOLVED — SQLITE_RATE_LIMIT_STORE` | `SQLiteRateLimitStore` implementado. NADR-08 §5.1 R1-R4 cumplidos. GF-01 satisfecho. |
| DF-28 | `RESOLVED — PRODUCTION ALIGNMENT` | Runners alineados con Composition Root. `DummyContextResolver` eliminado. |
| DF-29 | `RESOLVED — DELETE` | Dicts zombies eliminados + import inverso removido. `RecoveredJobSnapshot` preservado. |
| DF-31 | `ACCEPTED_LIMITATION` | Port no detecta huérfanos. Funcionalmente correcto. Destino natural: Fase 20. |
| DF-33 | `RESOLVED` | Grep de consumidores confirmó alcance completo. Sin impacto no previsto. |
| DF-34 | `RECLASSIFIED_FUTURE_PHASE` | `InMemoryProfileStore` no sobrevive crash. Destino: Recovery Gate / Fase 18. |
| H-11-A | `RESOLVED — DELETE` | `core/metrics/measure_density.py` eliminado. Frontera hexagonal restaurada. |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

### 4.1 BATCH 1 — Limpieza de Código Zombie (Completado)

**Fecha de ejecución:** 2026-08-16
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-10** | `RESOLVED — DELETE` | DELETE 3 archivos | `core/ast/router.py`, `core/ast/ports.py`, `infra/adapters/pdf_router.py` | ✅ 0 imports, ✅ Pyright clean, ✅ Tests green |
| **DF-14** | `RESOLVED — DELETE` | DELETE 1 archivo | `core/layout/classifier.py` | ✅ 0 imports, ✅ Pyright clean, ✅ Tests green |
| **DF-25** | `RESOLVED — DELETE` | DELETE 1 archivo | `runtime/reconciliation.py` | ✅ 0 imports, ✅ Pyright clean, ✅ Tests green |
| **DF-29** | `RESOLVED — DELETE` | DELETE dicts zombies + import | `core/execution/state_mapping.py` (eliminados: `PIPELINE_TO_FSM`, `FSM_TO_PIPELINE_RESUME`, imports innecesarios) | ✅ 0 imports de core.pipeline, ✅ 0 referencias a dicts, ✅ Pyright clean, ✅ Tests green |

#### Extensión Post-Batch 1 — Hallazgo Post-DF-29 (Completado)

**Fecha de ejecución:** 2026-08-16
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| Acción | Detalle |
|--------|---------|
| Mover `RecoveredJobSnapshot` | De `core/execution/state_mapping.py` → `core/execution/models.py` |
| Eliminar archivo con nombre engañoso | `core/execution/state_mapping.py` (Test-Path → False) |
| Actualizar imports | `core/pipeline/state_store.py:12` + `tests/unit/test_pipeline_fsm_emission.py:18` |
| Cero referencias a `state_mapping` | ✅ Confirmado |
| Bounded context preservado | Clase permanece en `core/execution/` (dirección de dependencia intacta) |

**Justificación de la extensión:**
Tras eliminar los dicts zombies en DF-29, `state_mapping.py` quedó con una sola clase cuyo nombre ya no reflejaba su contenido. Mover `RecoveredJobSnapshot` a `core/execution/models.py` (donde ya residen `ProcessingStage`, `ChunkLifecycle`, `FailureType`) elimina el archivo con nombre engañoso sin violar la dirección de dependencia pipeline → execution.

#### Métricas post-Batch 1 + extensión

| Métrica | Valor |
|---------|-------|
| Archivos eliminados | 6 (5 en Batch 1 + 1 en extensión) |
| Archivos reubicados | 1 clase movida a `core/execution/models.py` |
| Tests ejecutados | 274 passed, 5 skipped (baseline mantenida) |
| Errores de tipo estático | 0 |
| Dependencias huérfanas detectadas | 0 |

---

### 4.2 BATCH 2 — Migración Hexagonal + Limpieza de Zombis (Completado)

**Fecha de ejecución:** 2026-08-16
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-11** | `RESOLVED — MOVE` | MOVE 3 providers de `core/` a `infra/` | `core/extraction/ocr_providers/pymupdf_provider.py` → `infra/extraction/providers/`, `core/extraction/ocr_providers/tesseract_provider.py` → `infra/extraction/providers/`, `core/extraction/ocr_providers/docling_provider.py` → `infra/extraction/providers/` | ✅ 0 infra imports en core/ (excepto H-11-A), ✅ Pyright clean, ✅ Tests green |
| **DF-12-A** | `RESOLVED — DELETE` | DELETE `DocumentLayoutBuilder` + corregir import | `core/layout/builder.py` eliminado, `apps/bootstrap/pipeline_factory.py:43` corregido (import canónico) | ✅ 0 instancias de DocumentLayoutBuilder, ✅ Pyright clean, ✅ Tests green |

#### Correcciones adicionales durante ejecución

- `tests/unit/test_docling_provider.py`: Actualizado `@patch` con nueva ruta de módulo.
- `tools/benchmark_archive/run_calibration_v1.py`: Agregado `# pyright: ignore` (archivo archivado, DF-03 NAR).

#### Hallazgos registrados durante el batch

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| H-11-A | `core/metrics/measure_density.py` importa `fitz` directamente | `REVIEW_REQUIRED` | Determinar si es métrica de dominio o inspección física antes de decidir MOVE/DELETE |

#### Métricas post-Batch 2

| Métrica | Valor |
|---------|-------|
| Archivos movidos | 3 (providers OCR) |
| Archivos eliminados | 1 (DocumentLayoutBuilder) |
| Imports corregidos | 5 (4 en consumidores + 1 en test) |
| Tests ejecutados | 274 passed, 5 skipped |
| Errores de tipo estático | 0 |

**Estructura hexagonal correcta post-migración:**
- `core/extraction/provider.py` → Puerto abstracto (permanece en dominio)
- `infra/extraction/providers/` → Adaptadores concretos (movidos desde core/)
- `core/` libre de imports de infraestructura (excepto H-11-A pendiente)

---

### 4.3 BATCH 3 — Composición y Wiring (Completado)

**Fecha de ejecución:** 2026-08-17
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-26** | `RESOLVED — FACTORY EXTRACTION` | Extraer `build_provider_stack()` | `apps/bootstrap/provider_stack_factory.py` (nuevo), `apps/llm_workers/rate_limiter.py` (agregar `store` param), `apps/cli/main.py` (usar factory), `apps/llm_workers/__main__.py` (usar factory), `runtime/engine.py` (usar factory + agregar cache/CB) | ✅ 0 construcciones inline, ✅ Factory centralizada, ✅ Pyright clean, ✅ Tests green |
| **DF-27** | `RESOLVED — SQLITE_RATE_LIMIT_STORE` | Implementar persistencia de cuotas | `infra/resilience/sqlite_rate_limit_store.py` (nuevo), `core/resilience/rate_limit_store.py` (Protocol sync + docstring epoch), `apps/llm_workers/rate_limiter.py` (_restore/_persist epoch↔monotonic), `apps/cli/main.py` (inyectar store), `apps/llm_workers/__main__.py` (inyectar store), `runtime/engine.py` (inyectar store) | ✅ Store creado, ✅ Protocol sync, ✅ Conversión epoch↔monotonic, ✅ 3 entry points inyectan store, ✅ 3 entry points cierran rl_conn, ✅ Pyright clean, ✅ Tests green |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| NADR-08 | §5.1 R1 | Puerto abstracto `RateLimitStore` implementado |
| NADR-08 | §5.1 R2 | Operaciones atómicas `load()`/`save()` con SQLite WAL |
| NADR-08 | §5.1 R3 | Estado persistente en SQLite (no exclusivamente en RAM) |
| NADR-08 | §5.1 R4 | Backend seleccionado desde Composition Root (entry points) |
| GF-01 | — | Backend local SQLite WAL, sin infraestructura distribuida |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| epoch↔monotonic en `BucketState.last_update` | `time.time()` (epoch) para persistencia. `QuotaManager` convierte al cargar/guardar para compatibilidad con `TokenBucket` que usa `time.monotonic()` | Almacenar monotonic directamente (no serializable entre procesos) |
| Sin `close()` en SQLiteRateLimitStore | Coherente con patrón DI de `infra/db/` (8 repos). El caller cierra la conexión | Agregar `close()` al store (rompería patrón DI existente) |
| Factory NO crea store | Caller decide si inyectar persistencia. `rate_limit_store=None` = memoria local (backward compatible, testeable) | Factory crea store automáticamente (acoplamiento, no testeable) |
| PRAGMA WAL idempotente | Coherente con patrón de `CachedLLMProvider.initialize()` | PRAGMA en cada operación (overhead innecesario) |

#### Métricas post-Batch 3

| Métrica | Valor |
|---------|-------|
| Archivos creados | 2 (`provider_stack_factory.py`, `sqlite_rate_limit_store.py`) |
| Archivos modificados | 6 (rate_limit_store.py, rate_limiter.py, 3 entry points, pipeline_factory.py indirecto) |
| Tests ejecutados | 274 passed, 5 skipped |
| Errores de tipo estático | 0 |

---

### 4.4 BATCH 4 — Limpieza de Zombis Layout + Eliminación de Patrones Defensivos (Completado)

**Fecha de ejecución:** 2026-08-17
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-12-B** | `RESOLVED — DELETE` | Eliminar 6 stages zombis del layout pipeline | `core/layout/detector.py`, `core/layout/identity.py`, `core/layout/merger.py`, `core/layout/normalizer.py`, `core/layout/reading_order.py`, `core/layout/base.py` | ✅ 6 archivos eliminados, ✅ 3 archivos preservados, ✅ 0 referencias huérfanas, ✅ Pyright clean, ✅ Tests green |
| **DF-02-A** | `RESOLVED — REFACTORED` | Eliminar `hasattr(node.node_type, "value")` en producción | `core/benchmark/__main__.py:93`, `core/normalization/classifier.py:146`, `core/normalization/pipeline.py:44` | ✅ Acceso directo a `.value`, ✅ Pyright clean, ✅ Tests green |
| **DF-02-B** | `RESOLVED — REFACTORED` | Eliminar `hasattr` en tooling de benchmark | `tools/evaluation/topology/fingerprint.py:19` | ✅ Acceso directo a `.value`, ✅ Pyright clean, ✅ Tests green |

#### DF-12-B: Evidencia de auditoría

- Los 5 stages tenían **0 instancias** y **0 consumidores externos** en todo el proyecto.
- `base.py` era un zombi derivado: sus 6 clases solo eran consumidas por los 5 stages eliminados.
- `DocumentLayoutBuilder` (orquestador) fue eliminado previamente en DF-12-A (Batch 2).
- El benchmark NO usa estos stages — usa `LayoutBlockDraft`/`LayoutBlockCollection` como DTOs hacia `FlatASTBuilder`, sin invocar ningún stage.

**Archivos preservados en `core/layout/`:**
- `models.py` — `LayoutBlockDraft` + `LayoutBlockCollection` (activos, consumidos por FlatASTBuilder)
- `classification.py` — `HeuristicLayoutClassifier` (activo, consumido por PyMuPDFProvider)
- `validator.py` — `DocumentLayoutValidator` (activo, consumido por pipeline_factory)

**DF-12-C/D/E diferido:**
La migración de `FlatASTBuilder` a consumir `list[LayoutBlock]` directamente (eliminando la capa `LayoutBlockDraft`/`LayoutBlockCollection`) es un refactor de contrato que afecta 5+ archivos activos. Requiere ADR de diseño propio y se difiere a Fase 18.

#### DF-02: Justificación técnica

- `ASTNode.node_type` está tipado como `ContentNodeType` (Enum puro, sin Union).
- Pydantic garantiza el tipo post-construcción — si el tipo fuera incorrecto, fallaría con `ValidationError`.
- El fallback `else str(node.node_type)` violaba ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos).
- Método de edición: manual para preservar encoding original y evitar BOM de PowerShell.

#### Métricas post-Batch 4

| Métrica | Valor |
|---------|-------|
| Archivos eliminados | 6 (stages zombis) |
| Archivos modificados | 4 (hasattr eliminado) |
| Tests ejecutados | 274 passed, 5 skipped |
| Errores de tipo estático | 0 |

---

### 4.5 DF-01 — Identidad Semántica y Centralización Criptográfica (Completado)

**Fecha de ejecución:** 2026-08-19
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| Sub-DF | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|--------|--------------|------------------|-------------------|------------|
| **DF-01-A** | `RESOLVED — REFACTORED` | Migrar `hashlib.sha256()` directo a funciones canónicas de `core/shared/crypto.py` | `core/shared/crypto.py` (nueva función pura `compute_sha256_stream`), `core/benchmark/__main__.py` (2 puntos, 1 con streaming), `core/benchmark/runners/gemini_runner.py`, `core/benchmark/runners/groq_runner.py`, `core/benchmark/corpus/services.py`, `core/benchmark/orchestrator.py` (streaming) | ✅ 0 `hashlib` directo en benchmark, ✅ 0 `.read_bytes()` (soporte para libros 500+ págs), ✅ Pyright clean, ✅ Tests green |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| Streaming para libros extensos | `compute_sha256_stream(chunks: Iterable[bytes])` como función pura (Functional Core). I/O aislado en caller (Imperative Shell). Previene cargar PDFs de 200-500 MB en RAM. | `read_bytes()` directo (carga archivo completo en RAM) |
| Centralización criptográfica | Todo el hashing del benchmark pasa por `core/shared/crypto.py` (ENGINEERING_PRINCIPLES §III) | Hashlib directo en cada archivo (dispersión, no auditable) |

#### Reclasificación de sub-hallazgos de DF-01

| Sub-DF | Estado Final | Justificación |
|--------|--------------|---------------|
| **DF-01-A** | `RESOLVED` | Centralización criptográfica completada. |
| **DF-01-B** | `CLOSED (NAR)` | Falso positivo: `node_sha` por chunk y `compute_ast_hash()` por documento tienen propósitos ortogonales. |
| **DF-01-C** | `DEFERRED — FASE 2/3` | Requiere ADR de diseño futuro sobre el linaje de identidad semántica en la Scientific Baseline. |
| **DF-01-D** | `CLOSED (NAR)` | Agregar `ast_hash` a `DocumentFingerprint` violaría la separación de dimensiones del ADR Maestro §3 (Integridad física vs Identidad semántica). |

#### Métricas post-DF-01

| Métrica | Valor |
|---------|-------|
| Archivos modificados | 6 |
| Funciones nuevas | 1 (`compute_sha256_stream`) |
| Tests ejecutados | 274 passed, 5 skipped |
| Errores de tipo estático | 0 |

---

### 4.6 DF-28 — Alineación de Runners de Benchmark con Stack de Producción (Completado)

**Fecha de ejecución:** 2026-08-19
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| DF ID | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|-------|--------------|------------------|-------------------|------------|
| **DF-28** | `RESOLVED — PRODUCTION ALIGNMENT` | Alinear runners de benchmark con stack de producción | `apps/bootstrap/pipeline_factory.py` (`_build_healing_pipeline` → `build_healing_pipeline` público), `apps/bootstrap/provider_stack_factory.py` (parámetro `provider_type` agregado), `core/benchmark/runners/groq_runner.py` (usar factory canónica), `core/benchmark/runners/gemini_runner.py` (usar factory canónica) | ✅ `DummyContextResolver` eliminado, ✅ `DynamicContextResolver` con registry vacío, ✅ `CircuitBreakerProvider` incluido vía factory, ✅ `build_healing_pipeline()` reutilizado, ✅ Pyright clean, ✅ Tests green |

#### Cambios normativos aplicados

| NADR | Regla | Cómo se cumple |
|------|-------|----------------|
| NADR-05 | §5.1 R1 | Contexto real (DynamicContextResolver) en benchmark. Registry vacío es funcionalmente equivalente pero usa el mismo code path que producción. |
| NADR-08 | §5.2 R7 | CircuitBreaker MANDATORY en benchmark (vía `build_provider_stack()`). |
| NADR-11 | §5.1 R1 | Único punto de construcción del grafo de objetos (`build_provider_stack` reutilizado, no se creó factory paralela). |
| ADR_F17_BIS_01 | §4 | "Lo que el benchmark evalúa es exactamente lo que producción ejecuta." |

#### Decisiones de diseño clave

| Decisión | Justificación | Alternativas rechazadas |
|----------|---------------|------------------------|
| Sin cache en benchmark | El benchmark mide capacidad del modelo (TPS, latencia, calidad), no eficiencia del sistema. `cache_db_path=None` deshabilita cache. | Incluir cache (inflaría TPS artificialmente) |
| `provider_type` en `build_provider_stack()` | Permite al GeminiRunner inyectar `GeminiProvider` como base sin duplicar lógica de CB + RateLimiter. | `base_provider` como parámetro (acoplamiento a tipo concreto) |
| `build_healing_pipeline()` pública | Extraída de `_build_healing_pipeline()` para eliminar duplicación de ~20 líneas entre producción y benchmark. | Duplicar construcción en runners (violación NADR-11) |

#### Métricas post-DF-28

| Métrica | Valor |
|---------|-------|
| Archivos modificados | 4 |
| Tests ejecutados | 274 passed, 5 skipped |
| Errores de tipo estático | 0 |

---

### 4.7 H-11-A — Limpieza de Frontera Hexagonal en core/metrics (Completado)

**Fecha de ejecución:** 2026-08-19
**Validación:** Pyright 0 errors | pytest 274 passed, 5 skipped

| Item | Estado Final | Acción Ejecutada | Archivos Afectados | Validación |
|------|--------------|------------------|-------------------|------------|
| **H-11-A** | `RESOLVED — DELETE` | Eliminar script de diagnóstico con violación de frontera hexagonal | `core/metrics/measure_density.py` — eliminado | ✅ Archivo eliminado, ✅ 0 imports de `fitz` en `core/`, ✅ 0 referencias huérfanas, ✅ Pyright clean, ✅ Tests green |

#### Justificación de la eliminación

- **Violación NADR-02:** `import fitz` (PyMuPDF) directamente en la capa `core/`. El dominio no debe conocer proveedores concretos de extracción.
- **Violación ENGINEERING_PRINCIPLES §II:** Functional Core contaminado con I/O de terceros.
- **Código zombi completo:** 0 consumidores, 0 imports, 0 tests. Script de diagnóstico manual sin integración al pipeline.
- **No pertenece a `core/metrics/`:** Los otros archivos (`metrics.py`, `pricing.py`, `summary.py`, `exporters.py`) son componentes activos del pipeline.

**Métrica:** -1 archivo, -25 líneas de código muerto, frontera hexagonal restaurada.

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 34 (27 DF/GF/H + 7 sub-DFs) |
| Hallazgos resueltos | 20 |
| Hallazgos cerrados sin acción | 9 |
| Hallazgos reclasificados a fase futura | 7 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Batches completados | 7 (Batch 1-4 + DF-01 + DF-28 + H-11-A) |
| Archivos eliminados totales | 14 |
| Archivos movidos totales | 3 |
| Archivos creados totales | 2 |
| Archivos modificados totales | 16 |
| Tests finales | 274 passed, 5 skipped |
| Pyright final | 0 errors, 0 warnings |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| DF-01-C | Fase 2/3 (Identity & Trust Model) | Requiere ADR de diseño sobre linaje de identidad semántica en Scientific Baseline. |
| DF-04 | Post-Fase 18 | HARD_BREAK requiere semántica de contexto cruzado en AST V2. |
| DF-12-C/D/E | Fase 18 (Advanced Local Runtime) | Migración `FlatASTBuilder` → `list[LayoutBlock]`. Refactor de contrato. |
| DF-17 | Fase 21 (Parser Routing) | Extracción de imágenes requiere asset management inexistente. |
| DF-18 | Fase 18 o Fase 20 | `ExecutionContext` unificado. Evolución arquitectónica, no corrección. |
| DF-24 | Fase 18 (si se demuestra necesidad) | CircuitBreakerStore solo si se demuestra coordinación multi-proceso. |
| DF-34 | Recovery Gate / Fase 18 | `InMemoryProfileStore` no sobrevive crash. Condición explícita del Recovery Gate. |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida: 274 passed, 5 skipped)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito

**Verificación de cierre:**
- [x] Cero hallazgos `IMPLEMENTATION_REQUIRED` pendientes
- [x] Cero hallazgos `REVIEW_REQUIRED` sin decisión
- [x] 7/7 batches completados
- [x] 7 hallazgos `RECLASSIFIED_FUTURE_PHASE` con destino explícito

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 34 |
| Hallazgos resueltos | 20 |
| Hallazgos cerrados sin acción | 9 |
| Hallazgos reclasificados a fase futura | 7 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Batches completados | 7/7 |
| Estado del Exit Review | ✅ CERRADO |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan y su resolución.