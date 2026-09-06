# HITO_5.2_OPERATIONAL_INTEGRITY_AND_PERSISTENCE_ATOMICITY_AUDIT.md

**Estado:** FROZEN v1.1.0
**Fecha de emisión:** 2026-09-04
**Fecha de congelamiento:** 2026-09-04
**Fase:** 17-BIS — Fase 5 (Baseline Certification)
**Tipo de artefacto:** Operational Integrity & Persistence Atomicity Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.

**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-12, NADR-F17BIS-13, NADR-F17BIS-14 (FROZEN), HITO_5.0 v1.0.2 (FROZEN), HITO_5.1 v1.1.2 (FROZEN), FASE_4_HANDOFF (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN), ENGINEERING_PRINCIPLES.md (FROZEN), código fuente auditado en tools/evaluation/, infra/fs/, infra/serialization/, core/benchmark/persistence.py.

**Mandato:** Caracterizar mediante evidencia forense reproducible si las superficies operacionales pueden representar y propagar correctamente éxito, fallo y estados parciales, incluyendo la semántica de fallo (exit codes, propagación de excepciones, silenciamiento de errores), garantizando que ninguna operación de materialización pueda producir un estado físicamente ambiguo, parcialmente persistido o falsamente exitoso.

**Síntesis:** Se auditaron 9 entry points (1 DEPRECATED excluido) y 3 módulos de persistencia. Se confirma DF-18 en 4 entry points con múltiples caminos de error que terminan en exit 0 (P1). Se confirma GAP-5.0-03: 6 de 8 entry points tienen rutas hardcoded (P1). La atomicidad de reemplazo de archivo está verificada en `save_manifest_dto()` y `write_ast_json_atomic()` (patrón write-then-rename con `os.replace()`). La durabilidad ante power-loss es parcial (fsync silenciado). La persistencia de reportes y candidatos NO es atómica. `sanitize_ground_truth_types.py` puede sobrescribir SealedOracle sin verificación de estado sellado (Certification Boundary Integrity violation). Nota: v1.0.0 reportó 3 bugs de sintaxis (P0) que resultaron ser artefactos de transcripción de PowerShell; verificados con pyright como 0 errors (coherente con HITO 5.0 E-5.2-024).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-04 | Emisión inicial. Discovery físico y análisis de código fuente. |
| 1.0.0-FROZEN | 2026-09-04 | Cierre formal. RECHAZADO en revisión. |
| 1.1.0-FROZEN | 2026-09-04 | Corrección forense: (1) Eliminados E-5.2-010/011/012 y GAP-5.2-01/02/03 (bugs de sintaxis inexistentes, artefactos de transcripción PowerShell, verificados con pyright 0 errors, coherente con HITO 5.0 E-5.0-024); (2) Actualizado resumen ejecutivo y conteo de gaps (10→7); (3) Agregado análisis detallado de fsync silenciado; (4) Aclarada dualidad CorpusRepository/CorpusLoader; (5) Separada atomicidad de archivo de atomicidad de proceso completo; (6) Calificada afirmación de Zero Partial Sealing; (7) Separada atomicidad de durabilidad/power-loss; (8) Corregida afirmación de temp file cleanup; (9) Reformulada protección de SEALED como Certification Boundary Integrity; (10) Agregada Q13 (operación única de commit); (11) Separados requisitos normativos de hardening en Pilar VI; (12) Reformulada decisión de configuración como contrato; (13) Fortalecida conclusión de concurrencia; (14) Corregida trazabilidad de evidencias; (15) Agregada nota de corrección v1.0.0. |

### Nota de Corrección v1.0.0 → v1.1.0

**HITO 5.0 v1.0.0 reportó 3 bugs de sintaxis (P0) que NO EXISTEN.** Los fragmentos de código analizados fueron transcripciones de PowerShell con problemas de formato (líneas cortadas, indentación perdida). La verificación con pyright de los 3 archivos reporta **0 errors, 0 warnings**, coherente con HITO 5.0 v1.0.2 (E-5.0-024: `pyright tools/evaluation/freeze_ground_truth.py → 0 errors`). Las evidencias E-5.2-010, E-5.2-011, E-5.2-012 y los gaps GAP-5.2-01, GAP-5.2-02, GAP-5.2-03 de v1.0.0 son **eliminados** por basarse en evidencia incorrecta.

---

## 1. RESUMEN EJECUTIVO

Se ejecutó el discovery físico completo y el análisis de código fuente de todos los entry points de certificación y módulos de persistencia relevantes. La auditoría cubrió 9 entry points en `tools/evaluation/` y 3 módulos en `infra/fs/`, `infra/serialization/` y `core/benchmark/persistence.py`.

**Hallazgo central:**

> El tooling de certificación presenta **DF-18 confirmado en 4 entry points** con múltiples caminos de error que terminan en exit 0 (P1), y **GAP-5.0-03 confirmado**: 6 de 8 entry points tienen rutas hardcoded sin configuración explícita (P1). La atomicidad de reemplazo de archivo está verificada en `save_manifest_dto()` y `write_ast_json_atomic()` (patrón write-then-rename con `os.replace()`), pero la durabilidad ante power-loss es parcial (fsync silenciado con `except: pass`). La persistencia de reportes, candidatos y artefactos de benchmark NO es atómica. `sanitize_ground_truth_types.py` puede sobrescribir SealedOracle sin verificación de estado sellado, constituyendo una violación de Certification Boundary Integrity. La atomicidad transaccional del proceso completo de certificación (bootstrap → generate → freeze) no queda demostrada por este HITO.

**Defectos dominantes confirmados:**

1. **DF-18 confirmado en 4 entry points (E-5.2-001 a E-5.2-004, P1):** `freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py` y `sanitize_ground_truth_types.py` tienen múltiples caminos de error que terminan en exit 0.

2. **Rutas hardcoded (E-5.2-005, P1):** 6 de 8 entry points tienen rutas hardcoded sin configuración explícita. GAP-5.0-03 de HITO 5.0 confirmado.

3. **Certification Boundary Integrity violation (E-5.2-009, P1):** `sanitize_ground_truth_types.py` puede sobrescribir SealedOracle sin verificación de estado sellado. Existe una superficie de mutación fuera de la autoridad de sealing.

4. **Persistencia no atómica de artefactos secundarios (E-5.2-006 a E-5.2-008, P2):** `BenchmarkPersistenceGateway`, `generate_candidates.py` y `run_regression.py` usan escritura no atómica (`json.dump`, `write_text`).

5. **Durabilidad ante power-loss parcial (E-5.2-010, P2):** `fsync` silenciado con `except (AttributeError, OSError): pass` en `write_ast_json_atomic()` y `save_manifest_dto()`.

**Veredicto:** El sistema tiene **múltiples caminos de fallo silencioso que producen éxito falso** (DF-18). La atomicidad de reemplazo de archivo está garantizada para manifiestos y Ground Truths, pero la durabilidad ante power-loss es parcial y la atomicidad transaccional del proceso completo de certificación no está demostrada. El tooling no está listo para integración en CI sin remediación.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Lo que este HITO puede establecer

- El universo completo de entry points de certificación (9 identificados, 1 DEPRECATED excluido).
- La semántica de fallo de cada entry point (exit codes, excepciones, silenciamiento).
- La propagación de errores end-to-end (dominio → aplicación → CLI).
- La atomicidad de reemplazo de archivo en operaciones de persistencia (write/replace).
- La durabilidad ante crash de proceso y ante power-loss (parcial, por fsync silenciado).
- La idempotencia de CorpusRepository y GroundTruthStore.
- El comportamiento ante crash/recovery (análisis estático del código).
- La configuración explícita vs defaults hardcoded del tooling.

### 2.2 Lo que este HITO NO puede establecer

- La validez científica del contenido de los Ground Truths (HITO 5.4).
- La comparabilidad algorítmica de motores topológicos (HITO 5.3).
- La atomicidad física de SQLite del runtime (fuera de scope).
- La implementación de fixes (pertenece al Execution Plan).
- El comportamiento empírico ante crash/power-loss (requiere ejecución de tests de fault injection).
- La atomicidad transaccional del proceso completo de certificación (bootstrap → generate → freeze).

### 2.3 Límite 5.2 vs 5.3

```text
5.2: Infrastructure failure → ¿El sistema permanece operacionalmente seguro?
5.3: Algorithmic comparability → ¿ZhangShasha vs APTED producen resultados consistentes?
```

### 2.4 Límite 5.2 vs 5.4

```text
5.2: Infrastructure failure → ¿El sistema falla de forma segura?
5.4: AST mutation → ¿La métrica de regresión detecta degradación científica?
```

### 2.5 Taxonomía de Atomicidad

Este HITO distingue cuatro niveles de atomicidad:

| Nivel | Propiedad | Estado en este HITO |
|---|---|---|
| L1 | Atomicidad de reemplazo de archivo | ✅ Demostrada (tempfile + os.replace) |
| L2 | Durabilidad ante power-loss | ⚠️ Parcial (fsync silenciado, falta fsync de directorio) |
| L3 | Atomicidad de la operación de sellado | ✅ Demostrada (SealGroundTruthUseCase tiene una sola escritura) |
| L4 | Atomicidad del proceso completo de certificación | ❌ No demostrada (múltiples escrituras independientes) |

**Nota:** La afirmación "atomicidad física garantizada" de v1.0.0 se corrige a "atomicidad de reemplazo de archivo garantizada; durabilidad ante power-loss parcialmente degradada por silenciamiento de fsync".

---

## 3. ALCANCE AUDITADO

### 3.1 Scope de infra/fs/

| Superficie | Estado | Justificación |
|---|---|---|
| `infra/fs/corpus_repository.py` | Auditado | `LocalFileSystemCorpusLoader`: `save_manifest_dto()`, `load_raw_manifest()` |
| `infra/fs/ground_truth_store.py` | Auditado | `LocalFileSystemGroundTruthDraftWriter`: `save_draft_ast()` |
| `infra/serialization/ast_json.py` | Auditado | `write_ast_json_atomic()` |
| `core/benchmark/persistence.py` | Auditado | `BenchmarkPersistenceGateway` |
| `tools/evaluation/infrastructure/corpus_repository.py` | Auditado | `LocalFileSystemCorpusRepository` |
| SQLite del runtime | Excluido | Fuera de scope (CQRS, FSM, Telemetry) |
| Cache general del pipeline | Excluido | Fuera de scope |
| Outputs del traductor | Excluido | Fuera de scope (translated_*.pdf) |
| Logs del sistema | Excluido | Fuera de scope |

### 3.2 Dualidad CorpusRepository/CorpusLoader — RESUELTA

| Implementación | Ubicación | Responsabilidad | Recurso |
|---|---|---|---|
| `LocalFileSystemCorpusLoader` | `infra/fs/corpus_repository.py` | Manifest del corpus (load/save) | `manifest.json` |
| `LocalFileSystemCorpusRepository` | `tools/evaluation/infrastructure/corpus_repository.py` | Documentos del corpus (candidatos + GT) | `candidates/`, `ground_truth/` |

**Conclusión:** NO son duplicados. Tienen responsabilidades distintas y operan sobre recursos distintos. `LocalFileSystemCorpusLoader` implementa los puertos del dominio (`CorpusManifestReaderPort`, `CorpusManifestWriterPort`). `LocalFileSystemCorpusRepository` es una implementación de infraestructura para el tooling de evaluación que carga candidatos y ground truths como `BenchmarkDocument`.

### 3.3 Entry points auditados

| # | Entry point | Clasificación | Estado |
|---|---|---|---|
| EP-01 | `bootstrap_corpus.py` | Certificación | Auditado |
| EP-02 | `freeze_ground_truth.py` | Certificación | Auditado |
| EP-03 | `generate_golden_draft.py` | Certificación | Auditado |
| EP-04 | `generate_candidates.py` | Curaduría | Auditado |
| EP-05 | `generate_pymupdf_candidate.py` | Curaduría | Auditado |
| EP-06 | `run_regression.py` | Regresión (referencia positiva) | Auditado |
| EP-07 | `run_benchmark.py` | Benchmark | Auditado |
| EP-08 | `sanitize_ground_truth_types.py` | Migración GT | Auditado |
| EP-09 | `run_experimental_benchmark.py` | DEPRECATED | EXCLUDED (redirige a EP-07) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER.md §5 | Zero Partial Sealing, separación Integridad/Identidad/Regresión |
| NADR | NADR-F17BIS-14 §5.3 R7-R9 | Entry points, semántica de fallo, configuración |
| ENGINEERING_PRINCIPLES | §IV Cero Fallos Silenciosos | Propagación de errores |
| HITO previo | HITO_5.0 v1.0.2 | GAP-5.0-01 (DF-18), GAP-5.0-03 (rutas hardcodeadas), E-5.0-024 (pyright 0 errors) |
| HITO previo | HITO_5.1 v1.1.2 | GAP-5.1-07 (node_id), atomicidad física |
| Handoff | FASE_4_HANDOFF | run_regression.py con exit codes 0/1/2 (referencia positiva) |
| Código | tools/evaluation/*.py | 9 entry points auditados |
| Código | infra/fs/*.py, infra/serialization/ast_json.py | Persistencia atómica |
| Código | core/benchmark/persistence.py | BenchmarkPersistenceGateway |
| Verificación | pyright (3 ejecuciones, v1.1.0) | 0 errors en freeze_ground_truth.py, generate_golden_draft.py, generate_pymupdf_candidate.py |

---

## 5. LOS 6 PILARES DE AUDITORÍA

### Pilar I — CLI Contract Integrity

| Entry Point | --help | parse_args | Rutas hardcoded | Defaults peligrosos | Exit code |
|---|:---:|:---:|:---:|:---:|:---:|
| bootstrap_corpus | ❌ | ❌ | ✅ `benchmark_v1` | ❌ | Implícito |
| freeze_ground_truth | ❌ | ❌ | ✅ `benchmark_v1` | ❌ | Implícito (0 ante fallo) |
| generate_golden_draft | ❌ | ❌ | ✅ `benchmark_v1` | ❌ | Implícito (0 ante fallo) |
| generate_candidates | ✅ | ✅ | ❌ | ⚠️ `calibration_v1` | `sys.exit(1)` ante rechazo |
| generate_pymupdf_candidate | ❌ | ❌ | ✅ `calibration_v1` | ❌ | Implícito (0 ante fallo) |
| run_regression | ✅ | ✅ | ❌ | ⚠️ `reports/regression` | `sys.exit(0/1/2)` |
| run_benchmark | ✅ | ✅ | ❌ | ⚠️ `calibration_v1` | Implícito |
| sanitize_ground_truth_types | ❌ | ❌ | ✅ `calibration_v1` | ❌ | Implícito (0 ante fallo) |

**Veredicto del pilar:** PARCIAL. Solo 3 de 8 entry points tienen `parse_args()`. 6 de 8 tienen rutas hardcoded.

### Pilar II — Failure Semantics & Propagation

| Failure Class | bootstrap | freeze | generate_draft | generate_candidates | run_regression | run_benchmark | sanitize |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Manifest not found | Propaga (≠0) | **Captura → exit 0** | **Captura → exit 0** | N/A | Propaga (≠0) | Propaga (≠0) | N/A |
| Baseline incomplete | N/A | **Captura → exit 0** | N/A | N/A | `verify_completeness` → propagación | N/A | N/A |
| Oracle invalid | N/A | **Captura → exit 0** | N/A | N/A | Propaga (≠0) | N/A | N/A |
| Sealed oracle overwrite | N/A | N/A | **Captura → exit 0 (OK)** | N/A | N/A | N/A | **No verifica** |
| Write failure | Propaga (≠0) | Propaga (≠0) | Propaga (≠0) | Propaga (≠0) | Propaga (≠0) | Propaga (≠0) | **No captura** |
| Unexpected exception | Propaga (≠0) | **Captura → exit 0** | **Captura → exit 0** | Propaga (≠0) | Propaga (≠0) | Propaga (≠0) | **Captura → exit 0** |

**Veredicto del pilar:** FAIL. 4 entry points tienen caminos de fallo silencioso que producen exit 0.

### Pilar III — Physical Persistence Atomicity

| Operación | Mecanismo | Atomicidad de reemplazo (L1) | Durabilidad power-loss (L2) | Evidencia |
|---|---|:---:|:---:|---|
| `save_manifest_dto()` | tempfile + fsync + os.replace | ✅ | ⚠️ Parcial | E-5.2-013 |
| `save_draft_ast()` | `write_ast_json_atomic()` → temp + fsync + replace | ✅ | ⚠️ Parcial | E-5.2-014 |
| `write_ast_json_atomic()` | tempfile + fsync + os.replace | ✅ | ⚠️ Parcial | E-5.2-014 |
| `BenchmarkPersistenceGateway.save_final_report()` | `json.dump()` directo | ❌ | ❌ | E-5.2-006 |
| `BenchmarkPersistenceGateway.save_artifact()` | `write_text()` directo | ❌ | ❌ | E-5.2-006 |
| `generate_candidates.py` (escritura candidatos) | `json.dump()` directo | ❌ | ❌ | E-5.2-007 |
| `run_regression.py` (escritura reportes) | `write_text()` directo | ❌ | ❌ | E-5.2-008 |
| `sanitize_ground_truth_types.py` | `write_text()` directo | ❌ | ❌ | E-5.2-003 |

**Veredicto del pilar:** PARCIAL. La atomicidad de reemplazo de archivo (L1) está garantizada para manifiestos y Ground Truths. La durabilidad ante power-loss (L2) es parcial por silenciamiento de fsync. La persistencia de artefactos secundarios NO es atómica.

### Pilar IV — Idempotency & Repeatability

| Operación | Repetible | Idempotente (dominio) | Recovery tras crash | Recovery tras power-loss |
|---|:---:|:---:|:---:|:---:|
| `save_manifest_dto()` | ✅ (os.replace sobrescribe) | ✅ | ✅ (archivo original intacto si replace no se ejecuta) | ⚠️ (temp file residual posible) |
| `write_ast_json_atomic()` | ✅ (os.replace sobrescribe) | ✅ | ✅ (archivo original intacto si replace no se ejecuta) | ⚠️ (temp file residual posible) |
| `BenchmarkPersistenceGateway.save_final_report()` | ✅ (sobrescribe) | ⚠️ (puede dejar parcial) | ⚠️ (archivo corrupto posible) | ⚠️ |
| `generate_candidates.py` | ✅ (sobrescribe) | ⚠️ (puede dejar parcial) | ⚠️ (archivo corrupto posible) | ⚠️ |
| `sanitize_ground_truth_types.py` | ⚠️ (no verifica sellado) | ❌ (puede violar inmutabilidad de SEALED) | ⚠️ (GT corrupto posible) | ⚠️ |

**Nota sobre recovery:** El archivo original permanece intacto si `os.replace()` no llega a ejecutarse. Los temporales residuales tras interrupción anormal (crash duro, power-loss) requieren política explícita de recuperación/limpieza. `NamedTemporaryFile` con `delete=False` NO se limpia automáticamente ante interrupción anormal.

**Veredicto del pilar:** PARCIAL. Las operaciones atómicas son idempotentes y recuperables ante crash de proceso. La recuperación ante power-loss tiene degradación parcial (temp files residuales, fsync silenciado). `sanitize_ground_truth_types.py` puede violar la inmutabilidad de SEALED.

### Pilar V — Certification Boundary Integrity

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Qué impide que una operación parcialmente ejecutada sea interpretada como baseline válida? | `SealGroundTruthUseCase` verifica completitud y validez antes de sellar. `os.replace` garantiza atomicidad de reemplazo de archivo. | E-5.2-013, E-5.2-014 |
| ¿En qué punto aparece SEALED? | Después de `save_manifest_dto()` con `oracle_hash` y `ground_truth_state=SEALED`. | `SealGroundTruthUseCase.execute()` |
| ¿Puede aparecer SEALED pero faltan GTs? | NO en `SealGroundTruthUseCase`. `BaselineCompletenessVerifier` verifica biyección antes de sellar. | `freeze_ground_truth.py` |
| ¿`sanitize_ground_truth_types.py` puede corromper un SealedOracle? | **SÍ.** No verifica `ground_truth_state` antes de modificar. | E-5.2-009 |
| ¿La atomicidad del sellado (L3) está demostrada? | SÍ para `SealGroundTruthUseCase` (una sola escritura atómica). | E-5.2-013 |
| ¿La atomicidad del proceso completo de certificación (L4) está demostrada? | NO. El proceso tiene múltiples escrituras independientes (bootstrap → generate → freeze). | Q13 |

**Veredicto del pilar:** PARCIAL. El boundary de certificación está protegido en `SealGroundTruthUseCase` (L3). Pero `sanitize_ground_truth_types.py` constituye una superficie de mutación fuera de la autoridad de sealing que no demuestra respeto por la invariante de inmutabilidad de SEALED. La atomicidad del proceso completo de certificación (L4) no está demostrada.

### Pilar VI — Observability & Failure Detection (Tooling de Certificación)

**Requisitos normativos (obligatorios para certificación):**

| Requisito | Estado | Justificación |
|---|:---:|---|
| Exit status correcto (≠0 ante fallo) | ❌ FAIL | 4 entry points con exit 0 ante fallo |
| stderr/stdout semantics | ⚠️ PARCIAL | Mezcla de `print`, `logging`, `logger` |
| Failure identification (mensaje de error) | ⚠️ PARCIAL | Sin códigos indexables |
| Deterministic report | ⚠️ PARCIAL | `run_regression.py` tiene `--inject-timestamp` |

**Hardening (deseable, no obligatorio para certificación):**

| Requisito | Estado | Justificación |
|---|:---:|---|
| JSON structured logs | ❌ | Solo texto plano |
| Códigos indexables ([TOOL-001]) | ❌ | No implementados |
| execution_id | ❌ | No implementado |
| Centralized observability | ❌ | No implementado |
| Métricas agregables | ❌ | No implementadas |

**GAP-5.1-06 como input:** `Pydantic extra='ignore'` permite que campos legacy se ignoren silenciosamente. Ningún entry point registra cuando un DTO acepta campos no esperados.

**Veredicto del pilar:** FAIL en requisitos normativos. Hardening ausente pero no bloqueante para certificación.

---

## 6. LAS 12+1 PREGUNTAS FORENSES

### Q1 — ¿Cuáles son todos los entry points reales de certificación?

**Respuesta:** 9 entry points identificados en `tools/evaluation/`. 1 DEPRECATED excluido (`run_experimental_benchmark.py`).

| # | Entry point | Rol | Clasificación |
|---|---|---|---|
| EP-01 | bootstrap_corpus.py | Crea manifest del corpus | Certificación |
| EP-02 | freeze_ground_truth.py | Sella Ground Truths | Certificación |
| EP-03 | generate_golden_draft.py | Genera GT drafts | Certificación |
| EP-04 | generate_candidates.py | Genera candidatos (docling/pymupdf) | Curaduría |
| EP-05 | generate_pymupdf_candidate.py | Genera candidato PyMuPDF | Curaduría |
| EP-06 | run_regression.py | Evaluación de regresión | **Referencia positiva** |
| EP-07 | run_benchmark.py | Benchmark topológico | Benchmark |
| EP-08 | sanitize_ground_truth_types.py | Migra tipos de GT | Migración |
| EP-09 | run_experimental_benchmark.py | DEPRECATED → redirige a EP-07 | EXCLUDED |

### Q2 — ¿Cada entry point tiene contrato operacional explícito?

**Respuesta:** 3 de 8 entry points activos tienen `parse_args()` con `--help`. 5 de 8 NO tienen contrato operacional explícito.

| Entry Point | parse_args | --help | Contrato explícito |
|---|:---:|:---:|:---:|
| bootstrap_corpus | ❌ | ❌ | ❌ |
| freeze_ground_truth | ❌ | ❌ | ❌ |
| generate_golden_draft | ❌ | ❌ | ❌ |
| generate_candidates | ✅ | ✅ | ✅ |
| generate_pymupdf_candidate | ❌ | ❌ | ❌ |
| run_regression | ✅ | ✅ | ✅ |
| run_benchmark | ✅ | ✅ | ✅ |
| sanitize_ground_truth_types | ❌ | ❌ | ❌ |

### Q3 — ¿Cómo se representan éxitos y fallos hacia el proceso padre?

**Respuesta:**

| Entry Point | Éxito | Fallo |
|---|---|---|
| bootstrap_corpus | `print("[SUCCESS]...")` + exit 0 | Excepción propagada → exit ≠ 0 |
| freeze_ground_truth | `logger.info(...)` + exit 0 | `logger.critical(...)` + `return` → **exit 0** |
| generate_golden_draft | `logger.info(...)` + exit 0 | `logger.error/warning(...)` + `return`/`continue` → **exit 0** |
| generate_candidates | `print(...)` + exit 0 | `print(...)` + `sys.exit(1)` |
| generate_pymupdf_candidate | `print(...)` + exit 0 | `print(...)` + `return` → **exit 0** |
| run_regression | `sys.exit(0)` | `sys.exit(1)` o `sys.exit(2)` |
| run_benchmark | exit 0 | Excepción propagada → exit ≠ 0 |
| sanitize_ground_truth_types | `print(...)` + exit 0 | `print(...)` + `return` → **exit 0** |

### Q4 — ¿Existe algún camino de error que termine en exit 0?

**Respuesta:** SÍ. 4 entry points tienen caminos de error que terminan en exit 0.

| Entry Point | Camino de error → exit 0 | Evidencia |
|---|---|---|
| freeze_ground_truth | Manifest not found → `logger.critical` → `return` | E-5.2-001 |
| freeze_ground_truth | Baseline incomplete → `logger.critical` → `return` | E-5.2-001 |
| freeze_ground_truth | BaselineContractError → `logger.critical` → sin exit | E-5.2-001 |
| freeze_ground_truth | Exception genérica → `logger.critical` → sin exit | E-5.2-001 |
| generate_golden_draft | Manifest not found → `logger.error` → `return` | E-5.2-002 |
| generate_golden_draft | EmptyGroundTruthDraftError → `logger.error` → `continue` | E-5.2-002 |
| generate_golden_draft | Exception genérica → `logger.error` → `continue` | E-5.2-002 |
| generate_pymupdf_candidate | No PDFs → `print` → `return` | E-5.2-004 |
| sanitize_ground_truth_types | Directorio no existe → `print` → `return` | E-5.2-003 |

**Referencia positiva:** `run_regression.py` NO tiene este problema. Usa `sys.exit(0/1/2)` diferenciados (NADR-F17BIS-19 §5.5 R22).

### Q5 — ¿Las excepciones se propagan correctamente desde dominio → aplicación → CLI?

**Respuesta:** PARCIAL. 4 entry points capturan excepciones y las silencian.

| Entry Point | Propagación correcta | Evidencia |
|---|:---:|---|
| bootstrap_corpus | ✅ | Sin captura de excepciones |
| freeze_ground_truth | ❌ | Captura `FileNotFoundError`, `BaselineContractError`, `Exception` |
| generate_golden_draft | ❌ | Captura `FileNotFoundError`, `EmptyGroundTruthDraftError`, `Exception` |
| generate_candidates | ✅ | Sin captura de excepciones |
| generate_pymupdf_candidate | ⚠️ | Sin captura, pero `return` ante error → exit 0 |
| run_regression | ✅ | Sin captura de excepciones |
| run_benchmark | ✅ | Sin captura de excepciones |
| sanitize_ground_truth_types | ❌ | `return` ante error sin propagación |

### Q6 — ¿Qué operaciones de filesystem son realmente atómicas?

**Respuesta:** Solo `save_manifest_dto()` y `write_ast_json_atomic()` tienen atomicidad de reemplazo (L1). La durabilidad ante power-loss (L2) es parcial por fsync silenciado. El resto usa escritura directa no atómica.

### Q7 — ¿Qué ocurre ante fallo durante write/replace?

**Respuesta:**

| Operación | Comportamiento ante fallo de proceso | Comportamiento ante power-loss |
|---|---|---|
| `save_manifest_dto()` | Temp file queda en disco. `os.replace` no se ejecuta. Archivo original intacto. | Temp file residual posible. Durabilidad parcial (fsync silenciado). |
| `write_ast_json_atomic()` | Temp file queda en disco. `os.replace` no se ejecuta. Archivo original intacto. | Temp file residual posible. Durabilidad parcial (fsync silenciado). |
| `json.dump()` (no atómico) | Archivo puede quedar parcialmente escrito. Archivo original corrupto. | Archivo puede quedar parcialmente escrito. |
| `write_text()` (no atómico) | Archivo puede quedar parcialmente escrito. Archivo original corrupto. | Archivo puede quedar parcialmente escrito. |

### Q8 — ¿Puede una operación dejar un estado parcialmente persistido, incluyendo violación de Zero Partial Sealing (ADR Maestro §5, NADR-13 §5.2 R4-R8)?

**Respuesta:**

| Operación | Estado parcial posible (crash de proceso) | Zero Partial Sealing |
|---|:---:|:---:|
| `SealGroundTruthUseCase` | NO (una sola escritura atómica) | ✅ Protegido |
| `save_manifest_dto()` | NO (atómico) | ✅ |
| `write_ast_json_atomic()` | NO (atómico) | ✅ |
| Proceso completo de certificación | SÍ (múltiples escrituras independientes) | ⚠️ No demostrado a nivel L4 |
| `BenchmarkPersistenceGateway` | SÍ (no atómico) | N/A (no es sellado) |
| `generate_candidates.py` | SÍ (no atómico) | N/A |
| `sanitize_ground_truth_types.py` | SÍ (no atómico) | ❌ Puede corromper SealedOracle |

**Nota sobre Zero Partial Sealing:** `SealGroundTruthUseCase` demuestra una secuencia lógica de validación previa al sealing —completitud, validez y transición de lifecycle— con una sola escritura atómica (`save_manifest_dto`). La invariante Zero Partial Sealing (ADR Maestro §5) está protegida a nivel de la operación de sellado (L3). Sin embargo, la atomicidad transaccional del proceso completo de certificación (L4: bootstrap → generate → freeze) no queda demostrada por este HITO.

### Q9 — ¿Existe idempotencia real en CorpusRepository y GroundTruthStore (f(f(x)) = f(x)), y puede una segunda ejecución reparar de forma segura una primera ejecución incompleta (recovery after partial failure)?

**Respuesta:**

| Operación | Idempotente | Recovery tras crash |
|---|:---:|:---:|
| `save_manifest_dto()` | ✅ (`os.replace` sobrescribe, mismo contenido → mismo resultado) | ✅ (archivo original intacto si replace no se ejecuta) |
| `write_ast_json_atomic()` | ✅ (`os.replace` sobrescribe, mismo contenido → mismo resultado) | ✅ |
| `json.dump()` / `write_text()` | ⚠️ (sobrescribe pero puede quedar parcial tras crash) | ⚠️ (archivo corrupto posible) |

**Nota conceptual:** Repetibilidad de escritura ≠ Idempotencia operacional ≠ Inmutabilidad del artefacto sellado. `os.replace()` sobrescribe, lo cual hace la operación repetible. Pero para un SealedOracle, permitir re-escritura puede violar la inmutabilidad. La protección de inmutabilidad de SEALED está en el use case (`GenerateGoldenDraftUseCase` verifica `ground_truth_state`), no en el writer (`save_draft_ast`).

### Q10 — ¿Existe ruta que declare SEALED sin corpus físicamente completo?

**Respuesta:** NO en `SealGroundTruthUseCase`. El use case verifica:
1. `BaselineCompletenessVerifier.verify()` → biyección PDF ↔ GT
2. `OracleValidityContract.validate()` → validez de cada GT
3. `LifecycleTransitionAuthority.seal()` → solo desde VALIDATED
4. `save_manifest_dto()` → escritura atómica con `oracle_hash` y `ground_truth_state=SEALED`

**Conclusión:** La invariante Zero Partial Sealing está protegida a nivel de la operación de sellado.

### Q11 — ¿Existen mecanismos de exclusión para operaciones concurrentes?

**Respuesta:** NO. No se encontraron locks, file locks, ni mecanismos de exclusión en ningún entry point ni módulo de persistencia.

**Nota:** El ADR Maestro §4 dice "Single-node / No infraestructura distribuida", pero no prohíbe concurrencia local. Dos terminales ejecutando `freeze_ground_truth.py` simultáneamente podrían producir condiciones de carrera (TOCTOU: read → validate → mutate mientras otro proceso modifica el objeto). El ADR debe decidir el modelo de ejecución: single-writer local vs local concurrency allowed. No se debe introducir infraestructura de locking prematuramente (YAGNI, ENGINEERING_PRINCIPLES §I).

### Q12 — ¿El tooling tiene configuración explícita o depende de defaults hardcoded?

**Respuesta:** 6 de 8 entry points tienen rutas hardcoded. GAP-5.0-03 de HITO 5.0 confirmado.

| Entry Point | Rutas hardcoded | Configuración explícita |
|---|:---:|:---:|
| bootstrap_corpus | ✅ `tests/corpus/benchmark_v1` | ❌ |
| freeze_ground_truth | ✅ `tests/corpus/benchmark_v1` | ❌ |
| generate_golden_draft | ✅ `tests/corpus/benchmark_v1` | ❌ |
| generate_candidates | ❌ | ✅ `--corpus-dir` (default: `calibration_v1`) |
| generate_pymupdf_candidate | ✅ `tests/corpus/calibration_v1/pdf` | ❌ |
| run_regression | ❌ | ✅ `--corpus-dir`, `--pdf-dir` (required) |
| run_benchmark | ❌ | ✅ `--corpus` (default: `calibration_v1`) |
| sanitize_ground_truth_types | ✅ `tests/corpus/calibration_v1/ground_truth` | ❌ |

**Nota:** La decisión no es "usar argparse" (mecanismo), sino "cómo recibe configuración operacional un entry point" (contrato). El contrato podría ser CLI arguments, configuration object, environment variables, o application settings. argparse es simplemente el mecanismo CLI. La decisión del contrato pertenece a ADR_F17_BIS_05.

### Q13 — ¿Existe una operación única de commit del Baseline Certification State?

**Respuesta:** NO. El proceso completo de certificación tiene múltiples escrituras independientes:

```text
1. bootstrap_corpus.py       → escribe manifest inicial
2. generate_golden_draft.py  → escribe N oráculos (uno por documento)
3. freeze_ground_truth.py    → actualiza manifest con estado SEALED
```

Cada paso tiene escrituras independientes. No existe una operación única de commit atómico para todo el proceso.

Sin embargo, `SealGroundTruthUseCase.execute()` (paso 3) tiene UNA sola escritura (`save_manifest_dto()`), que es atómica. Los oráculos NO se escriben durante el sellado (ya están en disco desde el paso 2). El sellado solo actualiza el manifest con `oracle_hash` y `ground_truth_state=SEALED`.

**Implicación:** Si el proceso se interrumpe entre el paso 2 y el paso 3, el estado resultante es: N oráculos en disco + manifest sin estado SEALED. Esto NO es partial sealing (el manifest no dice SEALED), pero SÍ es un estado intermedio. La protección contra partial sealing está en `SealGroundTruthUseCase` (verifica completitud antes de sellar), no en el proceso completo.

---

## 7. MATRIZ DE OPERACIONES Y FALLOS (CONSOLIDADA)

| Operation | Success | Domain Failure | Infra Failure | Unexpected | Exit Code | Persisted State | Idempotent? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| bootstrap_corpus | ✅ exit 0 | Propaga ≠0 | Propaga ≠0 | Propaga ≠0 | ≠0 | Sin cambios | ✅ |
| freeze_ground_truth | ✅ exit 0 | **Captura → exit 0** | **Captura → exit 0** | **Captura → exit 0** | **0** | Sin cambios | ✅ |
| generate_golden_draft | ✅ exit 0 | **Captura → exit 0** | Propaga ≠0 | **Captura → exit 0** | **0** | Sin cambios | ✅ |
| generate_candidates | ✅ exit 0 | `sys.exit(1)` | Propaga ≠0 | Propaga ≠0 | 1 | Sin cambios | ✅ |
| generate_pymupdf_candidate | ✅ exit 0 | **`return` → exit 0** | Propaga ≠0 | Propaga ≠0 | **0** | Sin cambios | ✅ |
| run_regression | ✅ `sys.exit(0)` | `sys.exit(1/2)` | Propaga ≠0 | Propaga ≠0 | 0/1/2 | Sin cambios | ✅ |
| run_benchmark | ✅ exit 0 | Propaga ≠0 | Propaga ≠0 | Propaga ≠0 | ≠0 | Sin cambios | ✅ |
| sanitize_GT_types | ✅ exit 0 | **`return` → exit 0** | **No captura** | **No captura** | **0** | **GT modificado** | ❌ |
| save_manifest_dto | ✅ | N/A | ✅ atómico (L1) | Propaga ≠0 | N/A | ✅ atómico | ✅ |
| write_ast_json_atomic | ✅ | N/A | ✅ atómico (L1) | Propaga ≠0 | N/A | ✅ atómico | ✅ |
| BenchmarkPersistence.save_final_report | ✅ | N/A | ❌ no atómico | Propaga ≠0 | N/A | ❌ parcial posible | ⚠️ |
| generate_candidates (escritura) | ✅ | N/A | ❌ no atómico | Propaga ≠0 | N/A | ❌ parcial posible | ⚠️ |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev | Evidencia | Hallazgo |
|---|---|---|---|
| **E-5.2-001** | **P1** | `freeze_ground_truth.py`: 4 caminos de error → exit 0 | DF-18 confirmado. `FileNotFoundError`, `BaselineContractError`, `Exception` capturados con `logger.critical` + `return` (sin `sys.exit`). |
| **E-5.2-002** | **P1** | `generate_golden_draft.py`: múltiples caminos → exit 0 | DF-18 confirmado. `FileNotFoundError`, `EmptyGroundTruthDraftError`, `Exception` capturados con `logger.error/warning` + `return`/`continue`. |
| **E-5.2-003** | **P1** | `sanitize_ground_truth_types.py`: escritura no atómica + no verifica sellado | Usa `json_file.write_text()` directo. No verifica `ground_truth_state` antes de modificar. Puede corromper SealedOracle. |
| **E-5.2-004** | **P1** | `generate_pymupdf_candidate.py`: `return` ante error → exit 0 | Si no hay PDFs, `print` + `return` → exit 0. DF-18 confirmado. |
| **E-5.2-005** | **P1** | 6 de 8 entry points tienen rutas hardcoded | GAP-5.0-03 de HITO 5.0 confirmado. Sin `parse_args()` ni configuración explícita. |
| **E-5.2-006** | **P2** | `BenchmarkPersistenceGateway`: escritura no atómica | `save_final_report()` usa `json.dump()`. `save_artifact()` usa `write_text()`. Sin tempfile ni `os.replace`. |
| **E-5.2-007** | **P2** | `generate_candidates.py`: escritura no atómica | Usa `json.dump()` directo sin tempfile ni `os.replace`. |
| **E-5.2-008** | **P2** | `run_regression.py`: escritura de reportes no atómica | Usa `write_text()` directo sin tempfile ni `os.replace`. |
| **E-5.2-009** | **P2** | `sanitize_ground_truth_types.py`: puede sobrescribir SealedOracle | No verifica `ground_truth_state` antes de modificar GTs. Viola NADR-12 §5.3 R9. Certification Boundary Integrity violation. |
| **E-5.2-010** | **P2** | `fsync` silenciado en `write_ast_json_atomic()` y `save_manifest_dto()` | `except (AttributeError, OSError): pass`. Atomicidad de reemplazo (L1) garantizada. Durabilidad ante power-loss (L2) parcialmente degradada. Falta fsync de directorio padre. |
| **E-5.2-011** | **VERIFICACIÓN** | Dualidad CorpusRepository/CorpusLoader resuelta | NO son duplicados. Responsabilidades distintas: `CorpusLoader` opera sobre manifest, `CorpusRepository` opera sobre candidatos/GT. |
| **E-5.2-012** | **VERIFICACIÓN** | `run_regression.py` como referencia positiva | Exit codes diferenciados (0=PASS, 1=WARNING, 2=HARD_FAIL) según NADR-F17BIS-19 §5.5 R22. Coherente con FASE_4_HANDOFF. |
| **E-5.2-013** | **VERIFICACIÓN** | `save_manifest_dto()` es atómico (L1) | tempfile + flush + fsync + os.replace. Atomicidad de reemplazo garantizada. Durabilidad power-loss parcial (fsync silenciado). |
| **E-5.2-014** | **VERIFICACIÓN** | `write_ast_json_atomic()` es atómico (L1) | tempfile + flush + fsync + os.replace. Atomicidad de reemplazo garantizada. Durabilidad power-loss parcial (fsync silenciado). |

---

### Evidencia E-5.2-001: DF-18 confirmado en freeze_ground_truth.py

* **Archivo:** `tools/evaluation/freeze_ground_truth.py`
* **Observed:**

```python
# Camino 1: Manifest not found
try:
    manifest_dto = corpus_reader.load_raw_manifest()
except FileNotFoundError as e:
    logger.critical("Manifest not found. Aborting sealing: %s", str(e))
    return  # ← exit 0

# Camino 2: Baseline incomplete
if completeness_errors:
    logger.critical(
        "Baseline incompleta. Sellado abortado con %d errores.",
        len(completeness_errors),
    )
    return  # ← exit 0

# Camino 3: BaselineContractError
except BaselineContractError as e:
    logger.critical("Seal aborted by contract violation: %s", str(e))
    # ← sin return ni sys.exit → exit 0

# Camino 4: Exception genérica
except Exception as e:
    logger.critical("Catastrophic lineage sealing breakdown: %s", str(e))
    # ← sin return ni sys.exit → exit 0
```

* **Required:** ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos). NADR-14 §5.3 R8: fallos de integridad deben propagarse como errores explícitos.
* **Hallazgo:** 4 caminos de error terminan en exit 0. Un CI que ejecute `python freeze_ground_truth.py` interpretará un sellado abortado como éxito.

---

### Evidencia E-5.2-010: fsync silenciado en write_ast_json_atomic() y save_manifest_dto()

* **Archivo:** `infra/serialization/ast_json.py` (línea ~35), `infra/fs/corpus_repository.py` (línea ~55)
* **Observed:**

```python
try:
    os.fsync(tf.fileno())
except (AttributeError, OSError):
    pass  # ← silenciamiento
```

* **Required:** ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos).
* **Decision:** Ninguna fase previa abordó el silenciamiento de fsync.
* **Hallazgo Forense:** Si `fsync` falla (filesystem que no lo soporta, error de I/O), se ignora silenciosamente. La atomicidad de reemplazo (L1) está garantizada porque `os.replace()` es atómico independientemente del fsync. Sin embargo, la durabilidad ante power-loss (L2) está parcialmente degradada: sin fsync exitoso, los datos pueden estar solo en buffer del OS y perderse ante power-loss. Además, falta `fsync` del directorio padre después de `os.replace()`, lo cual es necesario para durabilidad completa en algunos filesystems.
* **Consecuencia Arquitectónica:** Atomicidad de reemplazo: ✅ garantizada. Durabilidad ante crash de proceso: ✅ garantizada. Durabilidad ante power-loss: ⚠️ parcial.
* **Estado:** OPEN — Requiere decisión de ADR sobre política de durabilidad.

---

## 13. MATRIZ DE PILARES (RESUMEN)

| Pilar | Veredicto | Justificación |
|---|---|---|
| I. CLI Contract Integrity | PARCIAL | 3/8 tienen parse_args. 6/8 tienen rutas hardcoded. |
| II. Failure Semantics | **FAIL** | 4 entry points con caminos de error → exit 0. |
| III. Physical Persistence Atomicity | PARCIAL | L1 (reemplazo) garantizado para manifest/GT. L2 (durabilidad) parcial. Artefactos secundarios no atómicos. |
| IV. Idempotency | PARCIAL | Operaciones atómicas idempotentes. No atómicas no. sanitize_GT puede violar inmutabilidad. |
| V. Certification Boundary | PARCIAL | L3 (sellado) protegido. sanitize_GT viola boundary. L4 (proceso completo) no demostrado. |
| VI. Observability | **FAIL** (normativo) | Exit codes incorrectos. Hardening ausente pero no bloqueante. |

---

## 14. GAPS CONSOLIDADOS

| GAP | Sev | Descripción | Evidencia | Pilar | Fase destino |
|---|---|---|---|---|---|
| **GAP-5.2-01** | **P1** | DF-18 confirmado en `freeze_ground_truth.py`: 4 caminos de error → exit 0. | E-5.2-001 | Pilar II | **ADR_F17_BIS_05** |
| **GAP-5.2-02** | **P1** | DF-18 confirmado en `generate_golden_draft.py`: múltiples caminos → exit 0. | E-5.2-002 | Pilar II | **ADR_F17_BIS_05** |
| **GAP-5.2-03** | **P1** | DF-18 confirmado en `generate_pymupdf_candidate.py`: `return` ante error → exit 0. | E-5.2-004 | Pilar II | **ADR_F17_BIS_05** |
| **GAP-5.2-04** | **P1** | 6 de 8 entry points tienen rutas hardcoded. GAP-5.0-03 confirmado. | E-5.2-005 | Pilar I | **ADR_F17_BIS_05** |
| **GAP-5.2-05** | **P1** | `sanitize_ground_truth_types.py` puede sobrescribir SealedOracle sin verificación. Certification Boundary Integrity violation. | E-5.2-003, E-5.2-009 | Pilar V | **ADR_F17_BIS_05** |
| **GAP-5.2-06** | **P2** | Persistencia de reportes/candidatos/benchmark no es atómica. | E-5.2-006 a E-5.2-008 | Pilar III | **ADR_F17_BIS_05** |
| **GAP-5.2-07** | **P2** | Sin logs estructurados, códigos indexables ni execution_id en tooling. Requisitos normativos (exit status) FAIL; hardening ausente. | Pilar VI | Pilar VI | **ADR_F17_BIS_05** |

**Nota sobre DF-18:** Este HITO caracteriza DF-18 mediante evidencia forense reproducible. No implementa fixes. La resolución pertenece al Execution Plan posterior.

**Nota sobre DF-19:** Este HITO no resuelve DF-19, pero caracteriza que la operación de escritura del manifest es atómica (`save_manifest_dto()` usa write-then-rename). La pregunta de migración de formato (4D → 6D) pertenece a ADR_F17_BIS_05.

**Nota sobre v1.0.0:** Los gaps GAP-5.2-01 a GAP-5.2-03 de v1.0.0 (bugs de sintaxis P0) fueron eliminados por basarse en evidencia incorrecta (artefactos de transcripción PowerShell). Los gaps actuales GAP-5.2-01 a GAP-5.2-03 corresponden a DF-18 (P1), no a bugs de sintaxis.

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| H-5.2-A | `save_manifest_dto()` tiene atomicidad de reemplazo (L1) | **CONFIRMADA** | E-5.2-013: tempfile + fsync + os.replace |
| H-5.2-B | `write_ast_json_atomic()` tiene atomicidad de reemplazo (L1) | **CONFIRMADA** | E-5.2-014: tempfile + fsync + os.replace |
| H-5.2-C | Todos los entry points tienen exit codes correctos | **RECHAZADA** | E-5.2-001 a E-5.2-004: 4 entry points con exit 0 ante fallo |
| H-5.2-D | `sanitize_ground_truth_types.py` respeta SealedOracle | **RECHAZADA** | E-5.2-009: no verifica estado sellado |
| H-5.2-E | `run_regression.py` es referencia positiva válida | **CONFIRMADA** | E-5.2-012: exit codes 0/1/2 diferenciados |
| H-5.2-F | Durabilidad ante power-loss está garantizada | **RECHAZADA** | E-5.2-010: fsync silenciado, falta fsync de directorio |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia | Fase destino |
|---|---|---|---|
| **DC-5.0-01** (heredado) | Estructura física del corpus | E-5.2-005 | ADR_F17_BIS_05 |
| **DC-5.0-03** (heredado) | Rutas hardcodeadas | E-5.2-005 | ADR_F17_BIS_05 |
| **DC-5.2-01** | Semántica canónica de exit codes | E-5.2-001 a E-5.2-004 | ADR_F17_BIS_05 |
| **DC-5.2-02** | Taxonomía de failure classes | Pilar II | ADR_F17_BIS_05 |
| **DC-5.2-03** | Política de propagación de excepciones | E-5.2-001 a E-5.2-004 | ADR_F17_BIS_05 |
| **DC-5.2-04** | Contrato de stdout/stderr para tooling | Pilar VI | ADR_F17_BIS_05 |
| **DC-5.2-05** | Política de atomicidad física de artefactos secundarios y durabilidad power-loss | E-5.2-006 a E-5.2-010 | ADR_F17_BIS_05 |
| **DC-5.2-06** | Política de protección de SealedOracle en scripts de migración (Certification Boundary Integrity) | E-5.2-009 | ADR_F17_BIS_05 |
| **DC-5.2-07** | Política de configuración de paths (contrato, no librería) | E-5.2-005 | ADR_F17_BIS_05 |
| **DC-5.2-08** | Mecanismo de observabilidad para tooling (separar requisitos normativos de hardening) | Pilar VI | ADR_F17_BIS_05 |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia |
|---|---|---|---|
| Sellado corrupto invisible en CI | Si DF-18 no se resuelve, un sellado fallido retorna exit 0 y CI lo trata como éxito. | **Alto:** Corrupción silenciosa de baseline. | E-5.2-001 |
| SealedOracle sobrescrito por sanitize | `sanitize_ground_truth_types.py` puede modificar GTs sellados. | **Alto:** Violación de inmutabilidad de SEALED. | E-5.2-009 |
| Reportes/candidatos corruptos tras crash | Escritura no atómica puede dejar archivos parciales. | **Medio:** Requiere re-ejecución. | E-5.2-006 a E-5.2-008 |
| Rutas hardcoded impiden integración CI | No se puede especificar corpus vía argumentos. | **Medio:** Requiere modificación de código para CI. | E-5.2-005 |
| Pérdida de datos ante power-loss | fsync silenciado degrada durabilidad. | **Bajo-Medio:** Atomicidad de reemplazo garantizada, durabilidad parcial. | E-5.2-010 |
| Temp files residuales tras crash | NamedTemporaryFile(delete=False) no se limpia ante interrupción anormal. | **Bajo:** Requiere política de cleanup. | E-5.2-013, E-5.2-014 |
| Proceso completo de certificación no atómico | Múltiples escrituras independientes sin commit único. | **Medio:** Estados intermedios posibles. | Q13 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

1. **DC-5.2-01:** ¿Cuál es la semántica canónica de exit codes para el tooling de certificación? ¿Se adopta el patrón de `run_regression.py` (0=PASS, 1=WARNING, 2=HARD_FAIL)?

2. **DC-5.2-03:** ¿Qué excepciones deben propagarse vs capturarse en cada entry point? ¿Cuál es la taxonomía de failure classes?

3. **DC-5.2-05:** ¿La persistencia de reportes y candidatos debe ser atómica? ¿O es aceptable la escritura directa dado que son artefactos regenerables? ¿Cuál es la política de durabilidad ante power-loss (fsync estricto vs actual)?

4. **DC-5.2-06:** ¿Cómo debe `sanitize_ground_truth_types.py` (o cualquier script de migración) verificar el estado sellado antes de modificar Ground Truths? ¿Se requiere una superficie de mutación separada con autorización explícita?

5. **DC-5.2-07:** ¿Cuál es el contrato de configuración para entry points de certificación? (No "usar argparse", sino el contrato: CLI arguments, configuration object, environment variables, application settings.)

6. **DC-5.2-08:** ¿Qué requisitos de observabilidad son normativos para certificación vs hardening deseable?

7. **DF-18:** ¿Se resuelve DF-18 como parte del Execution Plan de Fase 5, o se eleva a bloqueante de Fase 6 (CI)?

8. **Q13:** ¿Se requiere una operación única de commit atómico para el proceso completo de certificación, o es suficiente la atomicidad por operación individual con verificación de completitud previa al sellado?

9. **Concurrencia:** ¿Cuál es el modelo de ejecución del tooling de certificación: single-writer local o local concurrency allowed? ¿Se requiere algún mecanismo de exclusión mínimo?

---

## 21. CIERRE DEL HITO 5.2

Este HITO confirma que el tooling de certificación presenta **DF-18 confirmado en 4 entry points** (P1), **GAP-5.0-03 confirmado**: 6 de 8 entry points tienen rutas hardcoded (P1), y una **Certification Boundary Integrity violation** en `sanitize_ground_truth_types.py` (P1).

**La atomicidad de reemplazo de archivo (L1) está garantizada** para manifiestos y Ground Truths (`save_manifest_dto()` y `write_ast_json_atomic()` usan el patrón write-then-rename con `os.replace()`). La durabilidad ante power-loss (L2) es parcial por silenciamiento de fsync. La atomicidad de la operación de sellado (L3) está demostrada en `SealGroundTruthUseCase` (una sola escritura atómica). La atomicidad del proceso completo de certificación (L4) no está demostrada.

**SealGroundTruthUseCase demuestra una secuencia lógica de validación previa al sealing —completitud, validez y transición de lifecycle—. La operación de sellado tiene una sola escritura atómica (save_manifest_dto). Sin embargo, la atomicidad transaccional del proceso completo de certificación (bootstrap → generate → freeze) y la recuperación segura ante interrupción durante el sealing multi-artefacto no quedan demostradas por este HITO.**

**El tooling NO está listo para integración en CI** sin remediación de:
1. DF-18 en 4 entry points (P1, decisión de ADR)
2. Rutas hardcoded (P1, decisión de ADR)
3. Certification Boundary Integrity violation en sanitize_ground_truth_types.py (P1, decisión de ADR)

**Estado del HITO:** FROZEN v1.1.0

**Condición de cierre cumplida:**
- [x] Metadata completa y consistente
- [x] Changelog actualizado con nota de corrección v1.0.0
- [x] Límite epistemológico declarado
- [x] Taxonomía de atomicidad (L1-L4) declarada
- [x] Todas las superficies en scope inspeccionadas
- [x] Fuentes de evidencia listadas
- [x] Evidencias con ID estable, severidad y tipo
- [x] Evidencias verificables contra archivo real (pyright 0 errors)
- [x] 12+1 preguntas forenses respondidas con evidencia
- [x] 6 pilares auditados
- [x] Matriz de operaciones y fallos consolidada
- [x] 7 gaps consolidados con evidencia y fase destino (5 P1 + 2 P2)
- [x] 8 Decision Candidates generados
- [x] Nota de herencia de HITO 5.0 y 5.1
- [x] run_regression.py como referencia positiva
- [x] write_ast_json_atomic() auditado
- [x] Dualidad CorpusRepository/CorpusLoader resuelta
- [x] Separación atomicidad de archivo vs atomicidad de proceso
- [x] Separación atomicidad vs durabilidad power-loss
- [x] Protección de SEALED como Certification Boundary Integrity
- [x] Q13 (operación única de commit) respondida
- [x] Requisitos normativos vs hardening separados en Pilar VI
- [x] Configuración como contrato, no librería
- [x] Concurrencia como decisión explícita sin locks prematuros
- [x] Cadena de gobernanza verificada
- [x] Siguiente paso recomendado declarado

**Verificación de cadena de gobernanza:**
ADR_F17_BIS_MASTER → HITO 5.0 → HITO 5.1 → HITO 5.2 (este) → Gaps y DCs → ADR_F17_BIS_05 → Execution Plan.

**Siguiente paso recomendado:**
- **HITO 5.3** (Algorithmic Comparability Audit): resolver DF-04 (ZhangShasha vs APTED).
- **HITO 5.4** (GT Curation & Scientific Calibration): verificar H-5.1-C, H-5.1-D, H-5.1-F.
- **SYNTHESIS**: ADR_F17_BIS_05 con insumos de HITO 5.0, 5.1, 5.2, 5.3, 5.4.