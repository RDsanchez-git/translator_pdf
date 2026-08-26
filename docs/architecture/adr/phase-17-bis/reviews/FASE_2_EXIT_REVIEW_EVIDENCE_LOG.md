# FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-08-25
**Última actualización:** 2026-08-25
**Derivado de:** `PHASE_17BIS_FASE2_EXECUTION_PLAN.md` v1.9.0 — Gates 1-4 Exit Review
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review. Cada finding incluye los archivos auditados, el análisis,
los gaps confirmados, la justificación normativa y la clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-25 | Emisión inicial. Evidencia forense de los 22 hallazgos de Fase 2 (Gates 1-4). Documento FROZEN al cierre del Exit Review. |

---

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

> **Cero Fallos Silenciosos (ENGINEERING_PRINCIPLES §IV):** Ninguna anomalía
> se degrada silenciosamente. Todo fallo es explícito o indexable.

> **YAGNI (ENGINEERING_PRINCIPLES §I):** No se implementa lógica sin necesidad
> demostrada. Cada componente responde a una necesidad actual y medible.

> **Corolario forense P2:** REUSED ≠ IDENTICAL, TRANSFORM ≠ VIOLATION.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `E-{X}.{X}-{XX}` | Hallazgo de auditoría | Evidencia de código heredada de Fase 0 |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `DOCUMENTED` | Documentado sin acción de código requerida |

### 1.3 Reglas de evidencia

- Cada finding incluye la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding distingue: (a) gap objetivo confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

```text
1. ¿Sigue siendo válido el hallazgo?
   → NO: CLOSED (NAR)
   → SÍ: continuar

2. ¿Puede resolverse dentro del Gate actual?
   → SÍ: RESOLVED
   → NO: continuar

3. ¿Es un problema técnico?
   → SÍ: RECLASIFICADO a Gate futuro
   → NO: continuar

4. ¿Es un conflicto normativo?
   → SÍ: CONVERTIDO EN GF
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. EVIDENCIA FORENSE POR FINDING

### 2.1 DF-01 — Deuda: helpers de construcción ASTNode duplicados en tests

| Campo | Valor |
|-------|-------|
| **ID** | DF-01 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Gate 1 / Task 1.1.1 |
| **Estado previo** | `REVIEW_REQUIRED` |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No en Fase 2 |
| **¿Bloquea la ontología del oráculo?** | No |

#### 2.1.1 Archivos y documentos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `tests/unit/test_zhang_shasha.py` | Helper local `create_node()` presente |
| 2 | `tests/unit/test_structural_metric.py` | Helper local presente (confirmado en PROJECT_TREE) |
| 3 | `tests/unit/test_semantic_chunker.py` | Helper local `_create_node()` presente |
| 4 | `tests/unit/test_ground_truth_models.py` | Helper local `_make_node()` presente |
| 5 | `tests/helpers/` | No existe helper compartido de ASTNode |

#### 2.1.2 Análisis

La condición existe: hay 4 copias locales de helpers de construcción ASTNode. Es deuda de infraestructura de testing, no un gap arquitectónico del dominio ground_truth. No afecta la ontología del oráculo ni la identidad semántica (scope de Fase 2). YAGNI (ENGINEERING_PRINCIPLES §I): no hay necesidad demostrada de resolverlo durante la implementación de NADR-12..15.

#### 2.1.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 2 | ❌ No |
| Bloquea la ontología del oráculo | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Fase 18 / Refactor test-infra |

#### 2.1.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas."*

El refactor de helpers de test tiene dueño natural en la fase de madurez del runtime (Fase 18), no en la formalización de la ontología del oráculo.

---

### 2.2 DF-02 — Decisión ontológica: GroundTruth como Entity con document_id

| Campo | Valor |
|-------|-------|
| **ID** | DF-02 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.1 |
| **Prioridad** | Alta |
| **¿Bloquea la ontología del oráculo?** | Sí |

#### 2.2.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/models.py` | `GroundTruthDraft` y `SealedOracle` con campo `document_id` |
| 2 | `core/benchmark/corpus/models.py` | `CorpusManifest` como agregado separado |

#### 2.2.2 Análisis

La decisión ontológica se resolvió en Task 1.1.2: GroundTruth es Entity con `document_id` como campo de identidad. Agregado separado de `CorpusManifest`, relación por referencia vía `document_id`. Esto respeta DDD: cada agregado tiene su propia identidad y ciclo de vida.

#### 2.2.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Clasificación | `RESOLVED` |

#### 2.2.4 Regla aplicada

> **ADR_F17_BIS_02 §6 (Disyunción Ontológica):**
> *"Draft y Oracle son tipos disjuntos. Ningún estado permite tratar un borrador como oráculo."*

La decisión de Entity con `document_id` habilita la disyunción ontológica al dar identidad propia a cada tipo.

---

### 2.3 DF-03 — Campo `state` eliminado; tipo determina el estado

| Campo | Valor |
|-------|-------|
| **ID** | DF-03 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.1 |
| **Prioridad** | Alta |

#### 2.3.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/models.py` | Campo `state` ausente; tipos `GroundTruthDraft` y `SealedOracle` determinan el estado |

#### 2.3.2 Análisis

En Task 1.1.1 se introdujo una entidad genérica con campo `state`. En Task 1.1.2 se decidió eliminar el campo y usar tipos disjuntos: el tipo mismo determina el estado. Esto materializa la disyunción ontológica a nivel de sistema de tipos.

#### 2.3.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.3.4 Regla aplicada

> **NADR-12 §5.1 R2:** *"Definir tipos disjuntos para el estado de borrador curado y el estado de oráculo sellado, sin conversión implícita."*

---

### 2.4 DF-04 — ACCEPTED_LIMITATION: fugas de inmutabilidad en ASTNode

| Campo | Valor |
|-------|-------|
| **ID** | DF-04 |
| **Tipo** | Deferred Finding |
| **Estado** | `ACCEPTED_LIMITATION` |
| **Origen** | Gate 1 / Task 1.1.1 |
| **Prioridad** | Media |
| **¿Bloquea la ontología del oráculo?** | No |

#### 2.4.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/ast/models.py` | `ASTNode` con `control_plane: Dict[str, Any]` y `NodeMetadata.bboxes/pages: List[...]` |

#### 2.4.2 Análisis

La inmutabilidad profunda de `ASTNode` tiene fugas vía campos mutables (`Dict[str, Any]`, `List[...]`) dentro de modelos `frozen=True`. `frozen=True` bloquea reasignación de campos, no mutación de valores de colección. Es un patrón heredado de Fase 16 que excede el mandato de NADR-12..15. Corregirlo requiere decisión arquitectónica sobre `ASTNode` que pertenece a Fase 18 (Advanced Local Runtime).

#### 2.4.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ⚠️ Parcial |
| Pertenece a Fase 2 | ❌ No |
| Clasificación | `ACCEPTED_LIMITATION` |

#### 2.4.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Inmutabilidad de DTOs):**
> *"Las entidades de transporte de datos deben ser inmutables (frozen=True)."*

La limitación se acepta porque el scope de Fase 2 es la ontología del oráculo, no la inmutabilidad profunda del AST de producción.

---

### 2.5 DF-05 — Puertos actualizados a Tuple[ASTNode, ...]

| Campo | Valor |
|-------|-------|
| **ID** | DF-05 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.1 |
| **Prioridad** | Alta |

#### 2.5.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/ports.py` | `GroundTruthReaderPort.load_ground_truth()` retorna `Tuple[ASTNode, ...]` |
| 2 | `infra/fs/ground_truth_store.py` | Adaptador convierte `List → Tuple` tras `read_ast_json` |

#### 2.5.2 Análisis

Los puertos originales usaban `Sequence[ASTNode]`. La entidad `GroundTruth` usa `Tuple[ASTNode, ...]`. En Task 1.1.3 se actualizaron los puertos a `Tuple` para garantizar inmutabilidad en la frontera hexagonal. El adaptador convierte `List → Tuple` tras `read_ast_json`.

#### 2.5.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.5.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Inmutabilidad de DTOs):**
> *"Las estructuras de datos en tránsito están congeladas."*

---

### 2.6 DF-06 — AUDITED y VALIDATED son sub-estados del Draft

| Campo | Valor |
|-------|-------|
| **ID** | DF-06 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.2 |
| **Prioridad** | Alta |

#### 2.6.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/models.py` | `DraftSubState` enum con DRAFT, AUDITED, VALIDATED |

#### 2.6.2 Análisis

El enum `GroundTruthLifecycleState` tiene 4 estados. La pregunta era si AUDITED y VALIDATED son sub-estados de DRAFT o tipos propios. Se resolvió en Task 1.2.1: AUDITED y VALIDATED son sub-estados del Draft (`DraftSubState`), no tipos propios. Esto mantiene la disyunción ontológica (2 tipos disjuntos: Draft/Oracle) sin multiplicar tipos innecesariamente.

#### 2.6.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.6.4 Regla aplicada

> **NADR-12 §5.2 R4:** *"Definir explícitamente los estados de ciclo de vida y las únicas transiciones permitidas."*

---

### 2.7 DF-07 — Parámetro document_id en puertos vs campo en entidad

| Campo | Valor |
|-------|-------|
| **ID** | DF-07 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.2 |
| **Prioridad** | Baja |

#### 2.7.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/models.py` | Fábrica `hydrate_ground_truth(document_id, nodes, state)` unifica el parámetro de acceso con el campo de identidad |
| 2 | `core/benchmark/ground_truth/ports.py` | Puertos toman `document_id` como parámetro de acceso (clave de búsqueda, no identidad) |

#### 2.7.2 Análisis

El parámetro `document_id` en los puertos es clave de acceso (puerto), mientras que el campo `document_id` en la entidad es identidad (entidad). La fábrica `hydrate_ground_truth` los unifica. No hay redundancia real: son conceptos semánticamente distintos.

#### 2.7.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente |
| Clasificación | `RESOLVED` |

---

### 2.8 DF-08 — Coexistencia Draft/Oracle permitida por diseño

| Campo | Valor |
|-------|-------|
| **ID** | DF-08 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.2 |
| **Prioridad** | Media |

#### 2.8.1 Análisis

La pregunta era si Draft y Oracle pueden coexistir para el mismo `document_id`. Se resolvió en Task 1.2.1: la coexistencia es permitida por diseño. El test `test_same_document_id_different_types` verifica esta propiedad. NADR-12 §5.3 R8 permite reemplazo de borrador durante curaduría; R9 prohíbe alteración del oráculo.

#### 2.8.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.8.3 Regla aplicada

> **NADR-12 §5.3 R8:** *"Permitir el reemplazo de un borrador por una nueva instancia durante la curaduría."*

---

### 2.9 DF-09 — Import ausente de ASTNode en ground_truth_store.py

| Campo | Valor |
|-------|-------|
| **ID** | DF-09 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.3 |
| **Prioridad** | Baja |

#### 2.9.1 Análisis

Se detectó que `ground_truth_store.py` anotaba `Sequence[ASTNode]` pero el import estaba truncado/ausente. Se corrigió añadiendo el import en Task 1.1.3 como parte de la actualización del adaptador.

#### 2.9.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

---

### 2.10 DF-10 — BenchmarkParserBridge.extract_ast retorna Tuple

| Campo | Valor |
|-------|-------|
| **ID** | DF-10 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.3 |
| **Gate destino original** | Gate 3 (Wave 3.1) |
| **Prioridad** | Alta |

#### 2.10.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `infra/benchmarks/adapters/ground_truth_parser_adapter.py` | `extract_ast()` retornaba `Sequence[ASTNode]` |

#### 2.10.2 Análisis

El adaptador debía retornar `Tuple[ASTNode, ...]` para cumplir el contrato actualizado de `ASTExtractionPort` (Gate 1). Se resolvió en Wave 3.1 envolviendo el retorno con `tuple()`.

#### 2.10.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.10.4 Regla aplicada

> **NADR-14 §5.1 R1:** *"Exponer las operaciones de curaduría y de runtime sobre la baseline mediante contratos de acceso distintos."*

---

### 2.11 DF-11 — Mapeo prematuro AUDITED/VALIDATED en fábrica

| Campo | Valor |
|-------|-------|
| **ID** | DF-11 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.1.3 |
| **Prioridad** | Alta |

#### 2.11.1 Análisis

La fábrica `hydrate_ground_truth` en Task 1.1.3 mapeaba AUDITED y VALIDATED a `GroundTruthDraft`, tomando una decisión ontológica (DF-06) que era responsabilidad de Task 1.2.1. Se corrigió para solo aceptar DRAFT y SEALED; AUDITED y VALIDATED lanzan `ValueError` con trazabilidad a DF-06. Tras la resolución de DF-06 en Task 1.2.1, la fábrica acepta los 4 estados.

#### 2.11.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

---

### 2.12 DF-12 — Persistencia de sub_state: Opción 3 (efímero en memoria)

| Campo | Valor |
|-------|-------|
| **ID** | DF-12 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.2.1 |
| **Prioridad** | Alta |

#### 2.12.1 Análisis

La pregunta era si el estado del ciclo de vida se persiste en disco o es efímero en memoria. Se resolvió con Opción 3: `sub_state` es efímero en memoria. El oráculo en disco se trata como DRAFT al hidratar. El estado SEALED requiere mecanismo de persistencia (DF-13, Gate 3). La fábrica `hydrate_ground_truth` es trust-based: el consumidor que conoce el estado lo provee explícitamente.

#### 2.12.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.12.3 Regla aplicada

> **ADR_F17_BIS_02 §6 (No-Inferencia de Estado):**
> *"El estado de un Ground Truth nunca se deduce de la presencia de un artefacto."*

#### 2.12.4 Impacto y sub-acciones

**Impacto:** La decisión de `sub_state` efímero en memoria condiciona el mecanismo de persistencia del estado SEALED (DF-13). Sin persistencia, un oráculo sellado en disco sería tratado como DRAFT al hidratar, permitiendo sobrescritura accidental.

**Sub-acciones derivadas:**
- DF-13 (Gate 3): Implementar mecanismo de persistencia del estado SEALED.
- DF-14 (Gate 3): Proteger contra sobrescritura de oráculos sellados en disco.

---

### 2.13 DF-13 — Persistencia del estado SEALED (Opción D)

| Campo | Valor |
|-------|-------|
| **ID** | DF-13 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.2.1 |
| **Gate destino original** | Gate 3 (Task 3.2.1) |
| **Prioridad** | Critical |

#### 2.13.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/corpus/dtos.py` | `RawDocumentEntryDTO.ground_truth_state: Optional[str] = None` agregado |
| 2 | `core/benchmark/corpus/use_cases.py` | `LoadCorpusManifestUseCase` y `BootstrapCorpusManifestUseCase` propagan el campo |

#### 2.13.2 Análisis

La persistencia del estado SEALED requiere mecanismo que no sea inferencia. Se evaluaron Opción B (archivo de metadata separado) y Opción D (campo `ground_truth_state` explícito en manifiesto). Se seleccionó Opción D porque:
- Fuente de verdad única (el manifiesto ya porta el linaje)
- Coherencia con NADR-15 (la firma del catálogo se encadena al estado)
- No es inferencia: un campo de estado dedicado es declaración explícita
- Simplicidad: reutiliza estructura existente

Default None interpretado como DRAFT por la capa de consumo. Valor canónico `"sealed"` en minúsculas coherente con `GroundTruthLifecycleState.SEALED.value`.

#### 2.13.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.13.4 Regla aplicada

> **NADR-14 §5.2 R4:** *"Consolidar la certificación de oráculos y baselines en una única autoridad de sellado."*

#### 2.13.5 Impacto y sub-acciones

**Impacto:** La persistencia del estado SEALED es prerrequisito para la protección contra sobrescritura (DF-14) y para el encadenamiento criptográfico del estado en la firma del catálogo (DF-17, Gate 4). Sin persistencia, el estado sellado es efímero y no puede ser verificado por consumidores posteriores.

**Sub-acciones derivadas:**
- DF-14 (Gate 3, Wave 3.3): `GenerateGoldenDraftUseCase` verifica `ground_truth_state` antes de escribir.
- DF-17 (Gate 4, Wave 4.2): `ManifestFingerprintCalculator` incluye `ground_truth_state` en el payload del hash.

---

### 2.14 DF-14 — Protección contra sobrescritura de oráculos sellados

| Campo | Valor |
|-------|-------|
| **ID** | DF-14 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.3.3 |
| **Gate destino original** | Gate 3 (Task 3.2.1) |
| **Prioridad** | Critical |

#### 2.14.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/use_cases.py` | `GenerateGoldenDraftUseCase` verifica `ground_truth_state == "sealed"` antes de escribir |
| 2 | `core/benchmark/ground_truth/errors.py` | `SealedOracleOverwriteError(GroundTruthError)` agregado |

#### 2.14.2 Análisis

La protección contra sobrescritura de oráculos sellados requiere mecanismo de persistencia del estado SEALED (DF-13). Se materializa en Gate 3 Wave 3.3: `GenerateGoldenDraftUseCase` verifica `ground_truth_state == "sealed"` antes de escribir. Si está sellado → lanza `SealedOracleOverwriteError`; si no está en manifiesto o state ≠ sealed → permite. Esto materializa NADR-12 §5.3 R9 a nivel de persistencia (la protección de modelo ya existe desde Gate 1 vía `frozen=True`).

#### 2.14.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.14.4 Regla aplicada

> **NADR-12 §5.3 R9:** *"Impedir que un oráculo sellado sea alterado o sobrescrito por operaciones de curaduría."*

#### 2.14.5 Impacto y sub-acciones

**Impacto:** Sin protección contra sobrescritura, un operador de curaduría podría regenerar un draft sobre un oráculo sellado, corrompiendo la baseline certificada. Esto viola NADR-12 §5.3 R9 y compromete la integridad del Golden Corpus.

**Sub-acciones derivadas:**
- Ninguna. El hallazgo se cierra completamente en Gate 3 Wave 3.3.

---

### 2.15 DF-15 — Bug multiplataforma en write_ast_json_atomic

| Campo | Valor |
|-------|-------|
| **ID** | DF-15 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 1 / Task 1.3.2 |
| **Prioridad** | Critical |

#### 2.15.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `infra/serialization/ast_json.py` | `write_ast_json_atomic` usaba `Path.rename()` que lanza `FileExistsError` en Windows |

#### 2.15.2 Análisis

`Path.rename()` usa `os.rename()` que lanza `FileExistsError` (WinError 183) en Windows si el destino existe. En Unix, `os.rename()` sobrescribe el destino atómicamente. Esto viola NADR-F17BIS-01 §5.6 (reemplazo atómico) en Windows. Se corrigió con `os.replace()` que es atómico y multiplataforma. El test `test_draft_writer_overwrites_existing_file` expuso el bug.

#### 2.15.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.15.4 Regla aplicada

> **NADR-F17BIS-01 §5.6 (Escritura atómica):**
> *"MUST toda escritura de AST a disco garantizar atomicidad a nivel de sistema operativo."*

---

### 2.16 DF-16 — Parámetros no usados en ASTValidator.validate()

| Campo | Valor |
|-------|-------|
| **ID** | DF-16 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Gate 2 / Task 2.1.2 |
| **Prioridad** | Baja |
| **¿Bloquea la validez del oráculo?** | No |

#### 2.16.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/ast/validator.py` | `ASTValidator.validate()` tiene parámetros `unknown_count_floor` y `max_unknown_ratio` no utilizados en el cuerpo |

#### 2.16.2 Análisis

`ASTValidator.validate()` tiene parámetros que no se usan en el cuerpo del método. Es dead code o API incompleta de Fase 16. Los parámetros no afectan la implementación de Gate 2 (el contrato de validez del oráculo no los usa). Su evaluación (uso o eliminación) requiere análisis de impacto en Fase 16 y pertenece a una fase de limpieza técnica posterior.

#### 2.16.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Pertenece a Fase 2 | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Post-Fase 2 |

#### 2.16.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas."*

---

### 2.17 DF-17 — Ventana de estado sellado no protegido por hash

| Campo | Valor |
|-------|-------|
| **ID** | DF-17 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 3 / Task 3.2.1 |
| **Gate destino original** | Gate 4 (Task 4.3.2) |
| **Estado previo** | `DEFERRED — FASE 4` |
| **Prioridad** | Critical |

#### 2.17.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/corpus/services.py` | `ManifestFingerprintCalculator.compute_hash()` ahora incluye `oracle_hash` y `ground_truth_state` en el payload |
| 2 | `tests/unit/test_manifest_fingerprint.py` | `test_ground_truth_state_change_produces_different_hash` verifica sensibilidad |

#### 2.17.2 Análisis

Entre Gate 3 y Gate 4, el `manifest_hash` calculado por `ManifestLineageSealer` NO incluía `ground_truth_state`. Esto creaba una ventana de vulnerabilidad: el estado sellado no estaba protegido por el hash del manifiesto. Se resolvió en Gate 4 Wave 4.2: `ManifestFingerprintCalculator` ahora incluye `oracle_hash` y `ground_truth_state` en el payload. Test de sensibilidad verifica que cambiar el estado produce hash diferente.

#### 2.17.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.17.4 Regla aplicada

> **NADR-15 §5.3 R9:** *"Hacer la firma del catálogo sensible al linaje de los oráculos; una mutación de oráculo altera la firma resultante."*

#### 2.17.5 Impacto y sub-acciones

**Impacto:** Entre Gate 3 y Gate 4, el estado sellado persistido en el manifiesto NO está protegido por el hash del manifiesto. Una mutación del campo `ground_truth_state` en el JSON no sería detectada por verificación de integridad. Esto crea una ventana de vulnerabilidad donde un oráculo sellado podría ser "des-sellado" silenciosamente.

**Sub-acciones derivadas:**
- DF-17 resuelto en Gate 4 Wave 4.2: `ManifestFingerprintCalculator` incluye `ground_truth_state` en el payload.
- DF-19 (Gate 4, Wave 4.2): El cambio de formato del hash requiere re-sellado de manifiestos existentes (responsabilidad de Fase 5).

---

### 2.18 E-2.0-03 — ManifestGroundTruthUpdater duplicado

| Campo | Valor |
|-------|-------|
| **ID** | E-2.0-03 |
| **Tipo** | Hallazgo de auditoría |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Gate 3 / Task 3.2.2 |
| **Prioridad** | Alta |

#### 2.18.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/ground_truth/services.py` | `ManifestGroundTruthUpdater` duplicado línea por línea de `ManifestLineageSealer` |

#### 2.18.2 Análisis

`ManifestGroundTruthUpdater` era duplicado línea por línea de `ManifestLineageSealer` (corpus/services.py). Cero consumidores. Se eliminó (Zero Debt). El archivo `services.py` queda como placeholder con docstring de historial.

#### 2.18.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED — DELETE` |

#### 2.18.4 Regla aplicada

> **NADR-14 §5.2 R5:** *"Eliminar la coexistencia de múltiples autoridades de sellado con lógica duplicada o divergente."*

---

### 2.19 E-2.0-05 — Fail-open en load_raw_manifest

| Campo | Valor |
|-------|-------|
| **ID** | E-2.0-05 |
| **Tipo** | Hallazgo de auditoría |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 3 / Task 3.1.1 |
| **Prioridad** | Alta |

#### 2.19.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `infra/fs/corpus_repository.py` | `load_raw_manifest()` retornaba DTO vacío si el archivo no existe |

#### 2.19.2 Análisis

`load_raw_manifest()` retornaba `RawCorpusManifestDTO(corpus_version="v1.0", manifest_hash="", documents=[])` si el archivo no existe. Esto es fail-open, violando Cero Fallos Silenciosos. Se corrigió a fail-fast: lanza `FileNotFoundError`.

#### 2.19.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.19.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un Warning indexable explícito o fallar duro."*

---

### 2.20 E-2.0-06 — Escritura no atómica en save_manifest_dto

| Campo | Valor |
|-------|-------|
| **ID** | E-2.0-06 |
| **Tipo** | Hallazgo de auditoría |
| **Estado** | `RESOLVED` |
| **Origen** | Gate 3 / Task 3.1.1 |
| **Prioridad** | Alta |

#### 2.20.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `infra/fs/corpus_repository.py` | `save_manifest_dto()` usaba `open()` directo sin atomicidad |

#### 2.20.2 Análisis

`save_manifest_dto()` usaba `with open(self.manifest_file, "w", encoding="utf-8")` directo. Esto es inconsistente con `write_ast_json_atomic` (NADR-F17BIS-01 §5.6). Se corrigió con `tempfile + fsync + os.replace`.

#### 2.20.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Clasificación | `RESOLVED` |

#### 2.20.4 Regla aplicada

> **NADR-F17BIS-01 §5.6 (Escritura atómica):**
> *"MUST toda escritura garantizar atomicidad a nivel de sistema operativo."*

---

### 2.21 DF-18 — Entry points retornan exit code 0 en fallo

| Campo | Valor |
|-------|-------|
| **ID** | DF-18 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Gate 3 / Task 3.3.2 |
| **Estado previo** | `REVIEW_REQUIRED` |
| **Prioridad** | Media |
| **¿Bloquea la ontología del oráculo?** | No |

#### 2.21.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `tools/evaluation/bootstrap_corpus.py` | `main()` retorna `None` en fallo (exit code 0) |
| 2 | `tools/evaluation/freeze_ground_truth.py` | `main()` retorna `None` en fallo (exit code 0) |
| 3 | `tools/evaluation/generate_golden_draft.py` | `main()` retorna `None` en fallo (exit code 0) |

#### 2.21.2 Análisis

Los 3 entry points de curaduría retornan exit code 0 aunque el proceso falle. Esto viola ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos). Los entry points se ejecutan en Fase 5 para materializar el corpus canónico (ejecución manual/semiautomática, donde un fallo con exit code 0 es visible para el operador humano). **El riesgo crítico se materializa en Fase 6** (Continuous Verification / CI Gates): cuando CI consume estos entry points automáticamente, un sellado corrupto con exit code 0 pasaría desapercibido y una baseline inválida podría certificarse. Debe resolverse antes de la integración en CI.

#### 2.21.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ⚠️ Parcial |
| Pertenece a Fase 2 | ❌ No |
| Bloquea la ontología del oráculo | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Fase 5 / Baseline Certification |
| Punto crítico de materialización | Fase 6 (Continuous Verification / CI Gates) |

#### 2.21.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un Warning indexable explícito o fallar duro."*

El exit code 0 en fallo es degradación silenciosa. El dueño natural es la fase de certificación (Fase 5), pero el riesgo crítico se materializa en CI (Fase 6).

#### 2.21.5 Impacto y sub-acciones

**Impacto:** En Fase 5 (ejecución manual), un fallo con exit code 0 es visible para el operador humano. En Fase 6 (CI automatizado), un fallo con exit code 0 es invisible: CI no detecta el fallo y un sellado corrupto podría certificarse. Esto viola ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos) de forma crítica en el contexto de CI.

**Sub-acciones derivadas:**
- Resolver antes de la integración en CI (Fase 6): los 3 entry points deben retornar exit code no-cero en fallo.
- Archivos afectados: `tools/evaluation/bootstrap_corpus.py`, `tools/evaluation/freeze_ground_truth.py`, `tools/evaluation/generate_golden_draft.py`.

---

### 2.22 DF-19 — Migración de formato de hash del manifiesto

| Campo | Valor |
|-------|-------|
| **ID** | DF-19 |
| **Tipo** | Deferred Finding |
| **Estado** | `DOCUMENTED` |
| **Origen** | Gate 4 / Task 4.2.1 |
| **Prioridad** | Media |
| **¿Bloquea la identidad semántica?** | No |

#### 2.22.1 Archivos auditados

| # | Archivo | Evidencia |
|---|---------|-----------|
| 1 | `core/benchmark/corpus/services.py` | `ManifestFingerprintCalculator.compute_hash()` cambió de 4 a 6 dimensiones |
| 2 | `tests/unit/test_manifest_fingerprint.py` | `test_df19_regression_old_format_differs_from_new_format` verifica empíricamente la ruptura |

#### 2.22.2 Análisis

Wave 4.2 cambió el formato del payload del hash del manifiesto:
- **Antes (Gate 1-3):** `{doc_id}:{fingerprint_sha256}:{traits}:{page_count}`
- **Ahora (Gate 4):** `{doc_id}:{fingerprint_sha256}:{traits}:{page_count}:{oracle_hash}:{ground_truth_state}`

Esto rompe la compatibilidad de hashes con manifiestos sellados bajo el formato anterior. Si existen manifiestos sellados con el formato antiguo, deben re-sellarse con el formato nuevo para mantener la protección criptográfica completa. Esto es responsabilidad de Fase 5 (Baseline Certification), no de Fase 2.

El docstring de `ManifestFingerprintCalculator` documenta explícitamente el cambio de formato y la necesidad de re-sellado. Test de regresión verifica empíricamente que el formato nuevo produce hash diferente al antiguo.

#### 2.22.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Requiere acción operativa | ⚠️ Sí (Fase 5) |
| Clasificación | `DOCUMENTED` |
| Destino operativo | Fase 5 / Baseline Certification |

#### 2.22.4 Regla aplicada

> **ADR_F17_BIS_MASTER §5 (Determinismo y Reproducibilidad):**
> *"Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser 100% determinista."*

El cambio de formato es determinista y está documentado. La migración es responsabilidad de la fase de materialización.

---

## 3. GATE EXIT REVIEW SUMMARY

### 3.1 Gate 1 Exit Review (2026-08-24)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO | Deuda de testing, no bloquea ontología |
| DF-02 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Decisión ontológica tomada en Task 1.1.2 |
| DF-03 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Campo state eliminado en Task 1.1.2 |
| DF-04 | ✅ Sí | ❌ No | ✅ Sí | ACCEPTED_LIMITATION | Código de Fase 16 congelado |
| DF-05 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Puertos actualizados en Task 1.1.3 |
| DF-06 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Sub-estados del Draft en Task 1.2.1 |
| DF-07 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Unificado por hydrate_ground_truth |
| DF-08 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Coexistencia permitida por diseño |
| DF-09 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Import añadido en Task 1.1.3 |
| DF-10 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 3 | Prerequisito de Wave 1.3 |
| DF-11 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Fábrica corregida en Task 1.1.3 |
| DF-12 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Opción 3 (efímero) en Task 1.2.1 |
| DF-13 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 3 | Requiere mecanismo de persistencia |
| DF-14 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 3 | Depende de DF-13 |
| DF-15 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Bug multiplataforma corregido |

**Resumen:**
- RESOLVED: 10 (DF-02, DF-03, DF-05, DF-06, DF-07, DF-08, DF-09, DF-11, DF-12, DF-15)
- RECLASIFICADO → Gate 3: 3 (DF-10, DF-13, DF-14)
- RECLASIFICADO → Post-Fase 2: 1 (DF-01)
- ACCEPTED_LIMITATION: 1 (DF-04)
- Nuevos hallazgos registrados: 15

### 3.2 Gate 2 Exit Review (2026-08-25)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-16 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Post-Fase 2 | Dead code de Fase 16 |

**Resumen:**
- RECLASIFICADO → Post-Fase 2: 1 (DF-16)
- Nuevos hallazgos registrados: 1

### 3.3 Gate 3 Exit Review (2026-08-25)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-10 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Wave 3.1 cerró el hallazgo |
| DF-13 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Opción D materializada en Waves 3.1 + 3.2 |
| DF-14 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Wave 3.3 cerró el hallazgo |
| DF-17 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Ventana cerrada por Gate 4 |
| DF-18 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Fase 5 | Riesgo crítico en Fase 6 (CI) |
| E-2.0-03 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED — DELETE | Zero Debt |
| E-2.0-05 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Fail-fast |
| E-2.0-06 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | Escritura atómica |

**Resumen:**
- RESOLVED: 6 (DF-10, DF-13, DF-14, E-2.0-03, E-2.0-05, E-2.0-06)
- RECLASIFICADO → Gate 4: 1 (DF-17)
- RECLASIFICADO → Fase 5: 1 (DF-18)
- Nuevos hallazgos registrados: 6

### 3.4 Gate 4 Exit Review (2026-08-25)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-17 | ✅ Sí | ✅ Sí | ✅ Sí | RESOLVED | ManifestFingerprintCalculator incluye oracle_hash y ground_truth_state |
| DF-19 | ✅ Sí | ❌ No | ⚠️ Operativo | DOCUMENTED | Migración de formato responsabilidad de Fase 5 |

**Resumen:**
- RESOLVED: 1 (DF-17)
- DOCUMENTED: 1 (DF-19)
- Nuevos hallazgos registrados: 2

---

## 4. TABLA CONSOLIDADA FINAL

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 1 | E-2.0-03 |
| `RESOLVED` | 16 | DF-02, DF-03, DF-05, DF-06, DF-07, DF-08, DF-09, DF-10, DF-11, DF-12, DF-13, DF-14, DF-15, DF-17, E-2.0-05, E-2.0-06 |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 3 | DF-01 (Fase 18), DF-16 (Post-Fase 2), DF-18 (Fase 5) |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 1 | DF-04 |
| `DOCUMENTED` | 1 | DF-19 |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RECLASSIFIED_FUTURE_PHASE` | Deuda de testing diferida a Fase 18 / Refactor test-infra |
| DF-02 | `RESOLVED` | GroundTruth es Entity con document_id como campo |
| DF-03 | `RESOLVED` | Campo state eliminado; tipo determina el estado |
| DF-04 | `ACCEPTED_LIMITATION` | Fugas de inmutabilidad en ASTNode heredadas de Fase 16 |
| DF-05 | `RESOLVED` | Puertos actualizados a Tuple[ASTNode, ...] |
| DF-06 | `RESOLVED` | AUDITED y VALIDATED son sub-estados del Draft |
| DF-07 | `RESOLVED` | Parámetro document_id unificado por hydrate_ground_truth |
| DF-08 | `RESOLVED` | Coexistencia Draft/Oracle permitida por diseño |
| DF-09 | `RESOLVED` | Import de ASTNode añadido en ground_truth_store.py |
| DF-10 | `RESOLVED` | BenchmarkParserBridge.extract_ast retorna Tuple |
| DF-11 | `RESOLVED` | Fábrica hydrate_ground_truth corregida |
| DF-12 | `RESOLVED` | sub_state efímero en memoria (Opción 3) |
| DF-13 | `RESOLVED` | ground_truth_state en RawDocumentEntryDTO (Opción D) |
| DF-14 | `RESOLVED` | GenerateGoldenDraftUseCase verifica estado sellado |
| DF-15 | `RESOLVED` | Bug multiplataforma corregido con os.replace() |
| DF-16 | `RECLASSIFIED_FUTURE_PHASE` | Parámetros no usados en ASTValidator diferidos a Post-Fase 2 |
| DF-17 | `RESOLVED` | Ventana cerrada en Gate 4 (NADR-15 §5.3 R9) |
| DF-18 | `RECLASSIFIED_FUTURE_PHASE` | Exit code 0 diferido a Fase 5; riesgo crítico en Fase 6 |
| DF-19 | `DOCUMENTED` | Migración de formato de hash documentada; responsabilidad de Fase 5 |
| E-2.0-03 | `RESOLVED — DELETE` | ManifestGroundTruthUpdater eliminado (Zero Debt) |
| E-2.0-05 | `RESOLVED` | Fail-fast en load_raw_manifest |
| E-2.0-06 | `RESOLVED` | Escritura atómica con tempfile + fsync + os.replace |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado `PENDING_REVIEW`
- [x] La tabla consolidada final está completa
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [x] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [x] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación (ninguno pendiente)

### 5.2 Relación con el Findings Register

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register tiene una referencia cruzada a la sección correspondiente de este Evidence Log (§2.1 a §2.22).

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones.