# FASE_2_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_2_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 2.0.0
**Estado:** ARCHIVED
**Fecha de creación:** 2026-08-23
**Última actualización:** 2026-08-25
**Derivado de:** `PHASE_17BIS_FASE2_EXECUTION_PLAN.md` v1.9.0
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de Fase 2 (Scientific Baseline Domain), su clasificación,
resolución y evidencia empírica de los batches.

---

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-23 | Emisión inicial |
| 1.7.0 | 2026-08-25 | Gates 1-3 COMPLETED |
| 1.8.0 | 2026-08-25 | Gate 3 Exit Review completado |
| 1.9.0 | 2026-08-25 | Gate 4 COMPLETED. DF-17 RESOLVED, DF-19 DOCUMENTED |
| 2.0.0 | 2026-08-25 | **ARCHIVED**. DF-01 y DF-18 reclasificados a RECLASSIFIED_FUTURE_PHASE (DF-16 fue reclasificado en Gate 2 / v1.7.0). Exit Review Evidence Log FROZEN. Fase 2 COMPLETADA. |


## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER > ADR_F17_BIS_02 > NADR-F17BIS-12..15 > PHASE_17BIS_FASE2_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que el Scientific Baseline Domain
> sea una ontología formal, inmutable, semánticamente identificada y
> arquitectónicamente fiel de la verdad científica que Fase 3 encadenará
> criptográficamente y Fase 5 certificará en disco?"*

### 0.3 Reglas transversales aplicables

> **Zero Partial Sealing (ADR Maestro §5):** Ninguna baseline entra en estado
> sellado sin correspondencia biyectiva completa N_PDF = N_GT.

> **Separación de Identidades (ADR Maestro §3):** Integridad ≠ Identidad ≠
> Regresión. Las dimensiones de identidad no se colapsan.

> **Disyunción Ontológica (ADR_F17_BIS_02 §6):** Draft y Oracle son tipos
> disjuntos. Ningún estado permite tratar un borrador como oráculo.

> **No-Inferencia de Estado (ADR_F17_BIS_02 §6):** El estado de un Ground Truth
> nunca se deduce de la presencia de un artefacto o de un campo incidental.

> **Inmutabilidad (ENGINEERING_PRINCIPLES §II):** Toda transición de estado
> retorna una copia nueva. Cero mutación in-place.

> **Corolario forense P2:** REUSED ≠ IDENTICAL, TRANSFORM ≠ VIOLATION.

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

### 1.5 Clasificación semántica de hallazgos (nota aclaratoria)

Los hallazgos registrados en este documento pueden ser de tres tipos:

1. **Hallazgos fuera de scope:** Se detectan durante la implementación pero
   corresponden a otra fase/gate. Se clasifican como RECLASSIFIED_FUTURE_PHASE
   o DEFERRED — FASE X.

2. **Hallazgos bloqueantes:** Se detectan durante la implementación y bloquean
   la tarea actual. Se resuelven inline y se clasifican como RESOLVED.

3. **Decisiones de diseño inline:** Elecciones arquitectónicas que surgen
   durante la implementación y se resuelven en la misma tarea/wave. Se
   clasifican como RESOLVED.

DF-06, DF-11 y DF-12 de Gate 1 corresponden a la categoría 3 (decisiones de diseño
inline). Están correctamente clasificados como RESOLVED. Para Gate 2 en
adelante, las decisiones de diseño inline se documentarán en las Notas de
Implementación del Execution Plan, no en este registro.

---

## 2. GATE EXIT REVIEWS

### 2.1 Gate 1 — Oracle Ontology & Lifecycle (NADR-F17BIS-12)

**Estado:** ✅ COMPLETED (Waves 1.1, 1.2 y 1.3 COMPLETED — 9 tareas completadas)

#### Hallazgos identificados durante Task 1.1.1

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-01** | Deuda técnica: 4 copias locales de helper de construcción `ASTNode` en tests (`test_zhang_shasha.py`, `test_structural_metric.py`, `test_semantic_chunker.py`, `test_ground_truth_models.py`). Confirmado por grep que no existe helper compartido en `tests/helpers/`. | `REVIEW_REQUIRED` | Refactor futuro test-infra | Abierto |
| **DF-02** | Decisión ontológica fundacional: ¿`GroundTruth` es Entity (identidad propia) o Value Object (identidad derivada de atributos)? Sub-preguntas: (2A) ¿`ground_truth_id` propio vs `document_id`? (2B) ¿Agregación con `CorpusManifest` o agregado separado? | `RESOLVED` | Task 1.1.2 | **Cerrado** — Entity con `document_id` como campo; agregado separado; relación con `CorpusManifest` por referencia |
| **DF-03** | El campo `state` en `GroundTruth` condiciona las opciones de diseño de Task 1.1.2 (tipos disjuntos Draft/Oracle). Task 1.1.1 introdujo una entidad genérica con campo `state`; Task 1.1.2 debe decidir si mantener este patrón o eliminar el campo. | `RESOLVED` | Task 1.1.2 | **Cerrado** — Campo `state` eliminado; el tipo mismo determina el estado (`GroundTruthDraft` vs `SealedOracle`) |
| **DF-04** | ACCEPTED_LIMITATION: La inmutabilidad profunda de `ASTNode` tiene fugas vía `control_plane: Dict[str, Any]` y `NodeMetadata.bboxes/pages: List[...]` (mutables dentro de modelos `frozen=True`). `frozen=True` bloquea reasignación de campos, no mutación de valores de colección. Patrón heredado de Fase 16, fuera del scope de NADR-12..15. | `ACCEPTED_LIMITATION` | — | Cerrado (documentado) |
| **DF-05** | Nota forward-looking: los puertos vigentes (`GroundTruthReaderPort`, `GroundTruthDraftWriterPort`) usan `Sequence[ASTNode]`, mientras que la entidad `GroundTruth` usa `Tuple[ASTNode, ...]`. La conversión `Sequence → Tuple` debe hacerse con `tuple()` en Task 1.1.3 para garantizar inmutabilidad. | `RESOLVED` | Task 1.1.3 | **Cerrado** — Puertos actualizados a `Tuple[ASTNode, ...]`; adaptador convierte `List → Tuple` tras `read_ast_json` |

#### Hallazgos identificados durante Task 1.1.2

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-06** | 4 estados en enum `GroundTruthLifecycleState` (DRAFT, AUDITED, VALIDATED, SEALED) vs 2 tipos disjuntos (`GroundTruthDraft`, `SealedOracle`). Preguntas: ¿AUDITED y VALIDATED son sub-estados de DRAFT? ¿Son estados internos del proceso de sellado? ¿Requieren tipos propios? | `RESOLVED` | Task 1.2.1 | **Cerrado** — AUDITED y VALIDATED son sub-estados del Draft (`DraftSubState`), no tipos propios. Resuelto en Task 1.2.1. |
| **DF-07** | Redundancia potencial de `document_id` en puertos y entidad: los puertos (`GroundTruthReaderPort`, `GroundTruthDraftWriterPort`) toman `document_id` como parámetro y las entidades (`GroundTruthDraft`, `SealedOracle`) lo portan como campo. Cuando los puertos se integren con los nuevos tipos, el `document_id` estará tanto en el parámetro del método como en el campo de la entidad. | `RESOLVED` | Task 1.1.3 | **Cerrado** — El parámetro es clave de acceso (puerto), el campo es identidad (entidad). La fábrica `hydrate_ground_truth` los unifica. |
| **DF-08** | Coexistencia de Draft y Oracle para el mismo `document_id`: ¿pueden coexistir simultáneamente? Si el Oracle es la verdad sellada, ¿debe el Draft ser descartado tras el sellado? NADR-12 §5.3 R8 permite reemplazo de borrador durante curaduría, R9 prohíbe alteración del oráculo por curaduría, pero ninguna regla especifica si la coexistencia es permitida. | `RESOLVED` | Task 1.2.1 | **Cerrado** — La coexistencia es permitida por diseño. Test `test_same_document_id_different_types` de Task 1.1.2 verifica esta propiedad. |

#### Hallazgos identificados durante Task 1.1.3

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-09** | Import ausente de `ASTNode` en `ground_truth_store.py` detectado por inspección (el archivo anota `Sequence[ASTNode]` pero el import estaba truncado/ausente). | `RESOLVED` | Task 1.1.3 | **Cerrado** — Import añadido en Task 1.1.3 como parte de la actualización del adaptador |
| **DF-10** | `BenchmarkParserBridge.extract_ast` en `infra/benchmarks/adapters/ground_truth_parser_adapter.py` debe retornar `Tuple[ASTNode, ...]` para cumplir el nuevo contrato de `ASTExtractionPort` (actualizado en Task 1.1.3 a `Tuple`). | `REVIEW_REQUIRED` | Task 1.3.1 (prerequisito Wave 1.3) | Abierto (verificar antes de iniciar Wave 1.3) |
| **DF-11** | Mapeo prematuro de AUDITED y VALIDATED a `GroundTruthDraft` en la fábrica `hydrate_ground_truth`: tomaba una decisión ontológica (DF-06) que es responsabilidad de Task 1.2.1, violando el mapeo 1:1 regla→tarea. | `RESOLVED` | Task 1.1.3 | **Cerrado** — Fábrica corregida para solo aceptar DRAFT y SEALED; AUDITED y VALIDATED lanzan `ValueError` con trazabilidad a DF-06 |

#### Hallazgos identificados durante Wave 1.2 (Tasks 1.2.1, 1.2.2, 1.2.3)

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-12** | Persistencia de `sub_state`: ¿el estado del ciclo de vida se persiste en disco o es efímero en memoria? Si se persiste, ¿dónde (artefacto, metadata separada, manifiesto)? Si es efímero, ¿cómo se recupera el estado sellado al hidratar? | `RESOLVED` | Task 1.2.1 | **Cerrado** — Opción 3: `sub_state` es efímero en memoria. El oráculo en disco se trata como DRAFT al hidratar. El estado SEALED requiere mecanismo de persistencia (DF-13, Gate 3). La fábrica `hydrate_ground_truth` es trust-based: el consumidor que conoce el estado lo provee explícitamente. |
| **DF-13** | Persistencia del estado SEALED requiere mecanismo que no sea inferencia. Opciones candidatas: B (archivo de metadata separado) o D (campo `ground_truth_state` explícito en manifiesto). Gate 3 debe resolver. Implicaciones: (1) refactorización de `SealGroundTruthUseCase`; (2) si Opción D, posible migración de manifiestos y actualización de `ManifestFingerprintCalculator`; (3) sincronización entre estado sellado persistente y sub_state efímero al hidratar. La fábrica `hydrate_ground_truth` es trust-based y depende de que Gate 3 verifique el estado correctamente. | `REVIEW_REQUIRED` | Task 3.2.1 (Gate 3) | Abierto |

#### Hallazgos identificados durante Wave 1.3 (Tasks 1.3.1, 1.3.2, 1.3.3)

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-14** | Protección contra sobrescritura de oráculos sellados en disco. Requiere mecanismo de persistencia del estado SEALED (DF-13). NADR-12 §5.3 R9 materializado a nivel de modelo (frozen=True) y autoridad (sin rollback); protección de persistencia completada en Gate 3. | `REVIEW_REQUIRED` | Task 3.2.1 (Gate 3) | Abierto (depende de DF-13) |
| **DF-15** | Bug multiplataforma en `write_ast_json_atomic`: `Path.rename()` lanza `FileExistsError` en Windows si el destino existe. Viola NADR-F17BIS-01 §5.6 (reemplazo atómico) en Windows. Corregido con `os.replace()`, que es atómico y multiplataforma. El test `test_draft_writer_overwrites_existing_file` (Task 1.3.2) expuso el bug. | `RESOLVED` | Task 1.3.2 (Gate 1) | **Cerrado** — Corregido en Task 1.3.2 |

#### Archivos auditados

- `core/ast/models.py` — Contrato de `ASTNode` (3 campos requeridos: `node_id`, `node_type`, `payload`; `frozen=True`)
- `core/benchmark/ground_truth/models.py` — Entidades creadas en Tasks 1.1.1 y 1.1.2; fábrica añadida en Task 1.1.3; `DraftSubState` y `sub_state` añadidos en Task 1.2.1
- `core/benchmark/ground_truth/lifecycle.py` — Autoridad de transiciones introducida en Task 1.2.1
- `core/benchmark/ground_truth/ports.py` — Puertos actualizados a `Tuple[ASTNode, ...]` en Task 1.1.3
- `core/benchmark/ground_truth/use_cases.py` — Casos de uso vigentes (`LoadGroundTruthUseCase`, `GenerateGoldenDraftUseCase`, `SealGroundTruthUseCase`)
- `core/benchmark/corpus/models.py` — `CorpusManifest`, `CorpusDocumentMetadata` (sin referencia a Ground Truth)
- `core/benchmark/corpus/services.py` — `ManifestLineageSealer` (inferencia de estado documentada para Gate 3)
- `core/benchmark/ground_truth/services.py` — `ManifestGroundTruthUpdater` (código muerto duplicado; eliminación en Gate 3, Task 3.2.2)
- `infra/fs/ground_truth_store.py` — Adaptadores físicos actualizados en Task 1.1.3
- `infra/serialization/ast_json.py` — Contrato canónico de serialización (retorna `List[ASTNode]`)
- `tests/helpers/fakes.py` — Confirmado: importa `ASTNode` como anotación, no como fábrica
- `tests/unit/test_zhang_shasha.py` — Helper local `create_node()`
- `tests/unit/test_structural_metric.py` — Helper local (confirmado por PROJECT_TREE)
- `tests/unit/test_semantic_chunker.py` — Helper local `_create_node()` (confirmado por PROJECT_TREE)

---

### 2.2 Gate 2 — Ground Truth Validity & Baseline Completeness (NADR-F17BIS-13)

**Estado:** ✅ COMPLETED (10 tareas completadas, 10 reglas materializadas)

#### Hallazgos identificados durante Gate 2

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-16** | `ASTValidator.validate()` tiene parámetros `unknown_count_floor` y `max_unknown_ratio` no utilizados en el cuerpo del método (dead code o API incompleta de Fase 16). Identificado durante Task 2.1.2 (reutilización de ASTValidator). | `RECLASSIFIED_FUTURE_PHASE` | Post-Fase 2 | Diferido |

**Justificación de diferimiento:** Los parámetros no afectan la implementación de Gate 2 (el contrato de validez del oráculo no los usa). Su evaluación (uso o eliminación) requiere análisis de impacto en Fase 16 y pertenece a una fase de limpieza técnica posterior.

#### Archivos auditados

- `core/ast/validator.py` — `ASTValidator.validate()` con parámetros no usados
- `core/benchmark/ground_truth/validity.py` — `OracleValidityContract` (nuevo)
- `core/benchmark/ground_truth/completeness.py` — `BaselineCompletenessVerifier` (nuevo)
- `core/benchmark/ground_truth/errors.py` — Taxonomía de errores de contrato
- `core/benchmark/ground_truth/use_cases.py` — `SealGroundTruthUseCase` refactorizado
- `core/benchmark/ground_truth/ports.py` — `GroundTruthArtifactPort` extendido
- `infra/fs/ground_truth_store.py` — `LocalFileSystemGroundTruthArtifactAdapter` extendido
- `tools/evaluation/freeze_ground_truth.py` — Entry point actualizado

---

### 2.3 Gate 3 — Curation/Runtime Port Asymmetry & Sealing Authority (NADR-F17BIS-14)

**Estado:** ✅ COMPLETED (9 tareas completadas, 9 reglas materializadas)

#### Hallazgos identificados durante Gate 3

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-10** | `BenchmarkParserBridge.extract_ast` en `infra/benchmarks/adapters/ground_truth_parser_adapter.py` debe retornar `Tuple[ASTNode, ...]` para cumplir el contrato actualizado de `ASTExtractionPort` (Gate 1). | `RESOLVED` | Wave 3.1 | **Cerrado** — `extract_ast` retorna `Tuple[ASTNode, ...]` envolviendo con `tuple()` el retorno del parser. |
| **DF-13** | Persistencia del estado SEALED requiere mecanismo que no sea inferencia. Opción D (campo `ground_truth_state` en `RawDocumentEntryDTO`) seleccionada. Default None interpretado como DRAFT. | `RESOLVED` | Waves 3.1 + 3.2 | **Cerrado** — Campo agregado en Wave 3.1; persistencia completada en Wave 3.2. |
| **DF-14** | Protección contra sobrescritura de oráculos sellados en disco. Requiere mecanismo de persistencia del estado SEALED (DF-13). | `RESOLVED` | Wave 3.3 | **Cerrado** — `GenerateGoldenDraftUseCase` verifica `ground_truth_state == "sealed"` antes de escribir. Lanza `SealedOracleOverwriteError` si sellado. |
| **DF-17** | Ventana entre Gate 3 y Gate 4 donde el estado sellado no está protegido por el hash del manifiesto. `ManifestLineageSealer` calcula hash sin incluir `ground_truth_state`. | `DEFERRED — FASE 4` | Gate 4 (Task 4.3.2) | **Diferido** — Gate 4 encadena el estado en la firma vía NADR-15 §5.3 R9. |
| **E-2.0-03** | `ManifestGroundTruthUpdater` duplicado línea por línea de `ManifestLineageSealer`. Cero consumidores. | `RESOLVED` | Wave 3.2 | **Cerrado** — Archivo eliminado (Zero Debt). `services.py` como placeholder. |
| **E-2.0-05** | `load_raw_manifest()` retorna DTO vacío si el archivo no existe (fail-open). Viola Cero Fallos Silenciosos. | `RESOLVED` | Wave 3.1 | **Cerrado** — Corregido a fail-fast: lanza `FileNotFoundError`. |
| **E-2.0-06** | `save_manifest_dto()` usa `open()` directo sin atomicidad. Inconsistente con `write_ast_json_atomic`. | `RESOLVED` | Wave 3.1 | **Cerrado** — Corregido con `tempfile + fsync + os.replace`. |

#### Archivos auditados

- `core/benchmark/corpus/ports.py` — Segregación Reader/Writer
- `infra/fs/corpus_repository.py` — Fail-fast + escritura atómica
- `core/benchmark/corpus/dtos.py` — Campo `ground_truth_state` agregado
- `core/benchmark/corpus/use_cases.py` — Bootstrap=reader+writer, Load=reader
- `core/benchmark/ground_truth/use_cases.py` — SealGroundTruthUseCase como autoridad única + GenerateGoldenDraftUseCase con verificación de sellado
- `core/benchmark/ground_truth/services.py` — ManifestGroundTruthUpdater eliminado
- `core/benchmark/ground_truth/errors.py` — SealedOracleOverwriteError agregado
- `tools/evaluation/bootstrap_corpus.py` — Inyección de puertos segregados
- `tools/evaluation/freeze_ground_truth.py` — Orquestación del ciclo de vida en memoria
- `tools/evaluation/generate_golden_draft.py` — Inyección de corpus_reader
- `infra/benchmarks/adapters/ground_truth_parser_adapter.py` — DF-10 cerrado

### 2.4 Gate 4 — Semantic Identity Lineage (NADR-F17BIS-15)

**Estado:** ✅ COMPLETED (9 tareas completadas, 9 reglas materializadas)

#### Hallazgos identificados durante Gate 4

| ID | Hallazgo | Clasificación | Dueño | Estado |
|----|----------|---------------|-------|--------|
| **DF-17** | Ventana entre Gate 3 y Gate 4 donde el estado sellado no está protegido por el hash del manifiesto. `ManifestLineageSealer` calculaba hash sin incluir `ground_truth_state`. | `RESOLVED` | Wave 4.3 | **Cerrado** — `ManifestFingerprintCalculator` ahora incluye `oracle_hash` y `ground_truth_state` en el payload. Test `test_ground_truth_state_change_produces_different_hash` verifica sensibilidad. |
| **DF-19** | Migración de formato de hash del manifiesto. Wave 4.2 cambió el formato del payload de 4 a 6 dimensiones, rompiendo compatibilidad con hashes anteriores. | `DOCUMENTED` | Wave 4.2 | **Documentado** — Docstring de `ManifestFingerprintCalculator` documenta el cambio de formato. Test `test_df19_regression_old_format_differs_from_new_format` verifica empíricamente la ruptura. Manifiestos existentes deben re-sellarse. |

#### Archivos auditados

- `core/benchmark/ground_truth/identity.py` — `OracleSemanticIdentityCalculator` (nuevo)
- `core/benchmark/corpus/dtos.py` — `oracle_hash` agregado a `RawDocumentEntryDTO`
- `core/benchmark/corpus/models.py` — `oracle_hash` y `ground_truth_state` agregados a `CorpusDocumentMetadata`
- `core/benchmark/corpus/services.py` — `ManifestFingerprintCalculator` (formato extendido) + `ManifestLineageSealer` (propagación)
- `core/benchmark/corpus/use_cases.py` — `LoadCorpusManifestUseCase` + `BootstrapCorpusManifestUseCase` (propagación)
- `core/benchmark/ground_truth/use_cases.py` — `SealGroundTruthUseCase` (cálculo de `oracle_hashes` + `ground_truth_states`)
- `tests/unit/test_oracle_identity.py` — 8 tests de identidad semántica (nuevo)
- `tests/unit/test_manifest_fingerprint.py` — 10 tests de fingerprint (nuevo)
- `tests/unit/test_ground_truth_sealing_atomicity.py` — tests actualizados para verificar propagación


## 3. TABLA CONSOLIDADA FINAL


### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `REVIEW_REQUIRED` | 0 | - |
| `ACCEPTED_LIMITATION` | 1 | DF-04 |
| `RESOLVED` | 17 | DF-02, DF-03, DF-05, DF-06, DF-07, DF-08, DF-09, DF-10, DF-11, DF-12, DF-13, DF-14, DF-15, DF-17, E-2.0-03, E-2.0-05, E-2.0-06 |
| `RECLASSIFIED_FUTURE_PHASE` | 3 | DF-1, DF-16, DF-18 |
| `DOCUMENTED` | 1 | DF-19 |
| `DEFERRED — FASE 4` | 0 | — (DF-17 movido a RESOLVED) |
| `IMPLEMENTATION_REQUIRED` | 0 | — |

### 3.2 Tabla consolidada

| DF | Estado | Decisión | Dueño |
|----|--------|----------|-------|
| DF-01 | `RECLASSIFIED_FUTURE_PHASE` | Deuda de testing diferida a Fase 18 / Refactor test-infra. No afecta ontología ni identidad. YAGNI (ENGINEERING_PRINCIPLES §I). | Fase 18 / Refactor test-infra |
| DF-02 | `RESOLVED` | GroundTruth es Entity con `document_id` como campo. Agregado separado de `CorpusManifest`, relación por referencia. | Task 1.1.2 (cerrado) |
| DF-03 | `RESOLVED` | Campo `state` eliminado; el tipo mismo determina el estado (`GroundTruthDraft` vs `SealedOracle`). | Task 1.1.2 (cerrado) |
| DF-04 | `ACCEPTED_LIMITATION` | Fugas de inmutabilidad en `ASTNode` heredadas de Fase 16. Documentado, no remediable en Fase 2. | — |
| DF-05 | `RESOLVED` | Puertos actualizados a `Tuple[ASTNode, ...]`; adaptador convierte `List → Tuple` tras `read_ast_json`. | Task 1.1.3 (cerrado) |
| DF-06 | `RESOLVED` | AUDITED y VALIDATED son sub-estados del Draft (`DraftSubState`). Resuelto en Task 1.2.1. | Task 1.2.1 (cerrado) |
| DF-07 | `RESOLVED` | Parámetro `document_id` es clave de acceso (puerto); campo `document_id` es identidad (entidad). La fábrica los unifica. | Task 1.1.3 (cerrado) |
| DF-08 | `RESOLVED` | Coexistencia Draft/Oracle permitida por diseño. Verificado en test `test_same_document_id_different_types`. | Task 1.2.1 (cerrado) |
| DF-09 | `RESOLVED` | Import de `ASTNode` añadido en `ground_truth_store.py` como parte de la actualización del adaptador. | Task 1.1.3 (cerrado) |
| DF-10 | `RESOLVED` | BenchmarkParserBridge.extract_ast retorna Tuple[ASTNode, ...] | Wave 3.1 (cerrado) |
| DF-11 | `RESOLVED` | Fábrica `hydrate_ground_truth` corregida: solo acepta DRAFT y SEALED. AUDITED/VALIDATED lanzan `ValueError` con trazabilidad a DF-06. | Task 1.1.3 (cerrado) |
| DF-12 | `RESOLVED` | `sub_state` es efímero en memoria (Opción 3). El oráculo en disco se trata como DRAFT al hidratar. Estado SEALED requiere DF-13 (Gate 3). Fábrica trust-based. | Task 1.2.1 (cerrado) |
| DF-13 | `RESOLVED` | Campo ground_truth_state agregado a RawDocumentEntryDTO; persistencia completada | Waves 3.1 + 3.2 (cerrado) |
| DF-14 | `RESOLVED` | GenerateGoldenDraftUseCase verifica estado sellado antes de escribir | Wave 3.3 (cerrado) |
| DF-15 | `RESOLVED` | Bug multiplataforma en `write_ast_json_atomic` corregido con `os.replace()`. Test `test_draft_writer_overwrites_existing_file` expuso el bug. | Task 1.3.2 (cerrado) |
| DF-16 | `RECLASSIFIED_FUTURE_PHASE` | `ASTValidator.validate()` tiene parámetros no utilizados (dead code de Fase 16). Diferido a post-Fase 2 para evaluación de uso o eliminación. | Post-Fase 2 |
| DF-17 | `RESOLVED` | Ventana de estado no protegido por hash cerrada. `ManifestFingerprintCalculator` incluye `oracle_hash` y `ground_truth_state`. | Wave 4.3 (cerrado) |
| DF-18 | `RECLASSIFIED_FUTURE_PHASE` | Exit code 0 en fallo es degradación silenciosa (ENGINEERING_PRINCIPLES §IV). Debe resolverse antes de integración en CI. Destino: Fase 5 / Baseline Certification. Punto crítico: Fase 6 (CI Gates). | Fase 5 / Baseline Certification |
| DF-19 | `DOCUMENTED` | Migración de formato de hash del manifiesto. Documentado en docstring + test de regresión. Manifiestos existentes deben re-sellarse. | Wave 4.2 (documentado) |
| E-2.0-03 | `RESOLVED` | ManifestGroundTruthUpdater eliminado (Zero Debt) | Wave 3.2 (cerrado) |
| E-2.0-05 | `RESOLVED` | Fail-fast en load_raw_manifest | Wave 3.1 (cerrado) |
| E-2.0-06 | `RESOLVED` | Escritura atómica con tempfile + fsync + os.replace | Wave 3.1 (cerrado) |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

**No se ejecutaron batches de implementación.**

Justificación: según METHODOLOGY §6.6, los batches agrupan findings
`IMPLEMENTATION_REQUIRED`. En Fase 2 no hubo ningún hallazgo en ese estado:
todos los findings se resolvieron inline durante las waves normales
(RESOLVED), se reclasificaron a fases futuras (RECLASSIFIED_FUTURE_PHASE),
se aceptaron como limitación (ACCEPTED_LIMITATION) o se documentaron
(DOCUMENTED). Por lo tanto, no se planificaron ni ejecutaron batches.

---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 22 |
| Hallazgos resueltos | 17 (DF-02, DF-03, DF-05, DF-06, DF-07, DF-08, DF-09, DF-10, DF-11, DF-12, DF-13, DF-14, DF-15, DF-17, E-2.0-03, E-2.0-05, E-2.0-06) |
| Hallazgos documentados | 1 (DF-19, migración Fase 5) |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos reclasificados a fase futura | 3 (DF-01, DF-18, DF-16) |
| Hallazgos diferidos a Fase 4 | 0 (DF-17 movido a RESOLVED) |
| Hallazgos aceptados como limitación | 1 (DF-04) |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos pendientes de implementación | 0 |
| Batches completados | 0 (no requeridos: 0 findings IMPLEMENTATION_REQUIRED) |
| Archivos eliminados totales | 1 (ManifestGroundTruthUpdater en services.py) |
| Archivos movidos totales | 0 |
| Archivos creados totales | 16 (Gate 1: 5, Gate 2: 3, Gate 3: 5, Gate 4: 3) |
| Archivos modificados totales | 21 (Gate 1: 4, Gate 2: 4, Gate 3: 7, Gate 4: 6) |
| Tests finales | 368 passed, 5 skipped (baseline 274 + 94 nuevos) |
| Pyright final | 0 errors |

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| DF-01 (deuda helpers de test) | Fase 18 / Refactor test-infra | No bloquea Fase 2; deuda de infraestructura de testing. YAGNI. |
| DF-04 (fugas inmutabilidad ASTNode) | Fuera de scope Fase 2 | Código de Fase 16 congelado; requiere decisión arquitectónica sobre ASTNode. |
| DF-16 (parámetros no usados en ASTValidator) | Post-Fase 2 | Evaluación de uso o eliminación requiere análisis de impacto en Fase 16. |
| DF-18 (exit code 0 en entry points) | Fase 5 / Baseline Certification | Degradación silenciosa (ENGINEERING_PRINCIPLES §IV). Punto crítico: Fase 6 (CI Gates). |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → sin degradación del baseline inicial de Fase 2: 274 passed, 5 skipped)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 22 |
| Hallazgos resueltos | 17 |
| Hallazgos documentados | 1 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos aceptados como limitación | 1 |
| Hallazgos reclasificados a fase futura | 3 |
| Batches completados | N/A (0 planificados, 0 findings IMPLEMENTATION_REQUIRED) |
| Estado del Exit Review | ✅ **ARCHIVED** (Fase 2 COMPLETADA: 4 Gates PASS, 37/37 reglas, Evidence Log FROZEN) |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan de Fase 2 y su resolución.