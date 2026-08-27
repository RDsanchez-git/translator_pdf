# HITO_3.1_IDENTITY_DIMENSION_ONTOLOGY_MUTATION_MATRIX.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-08-25
**Fecha de congelamiento:** 2026-08-25
**Fase:** 17-BIS — Fase 3 (Identity & Trust Model) — Sub-fase 3.0 (Forensic Identity Audit)
**Tipo de artefacto:** Dimension & Mutation Semantics Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- `HITO_0.3_IDENTITY_AND_CRYPTOGRAPHIC_AUDIT.md` (FROZEN, Fase 0)
- `FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md` (FROZEN v1.0.0)
- `FASE_2_HANDOFF.md` (FROZEN v1.0.0)
- `FASE_1_HANDOFF.md` (FROZEN v1.0.0)
- `PHASE_17BIS_FASE2_EXECUTION_PLAN.md` (APPROVED v1.9.0)
- `NADR-F17BIS-12.md`, `NADR-F17BIS-13.md`, `NADR-F17BIS-14.md`, `NADR-F17BIS-15.md` (FROZEN v1.0)
- `ADR_F17_BIS_MASTER.md` (FROZEN)
- `ENGINEERING_PRINCIPLES.md` (FROZEN)
- `METHODOLOGY_FOR_FORENSIC_HITOs.md` (FROZEN v1.2.0)
- `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` (FROZEN v1.3.0)
- Módulos auditados: `core/ast/enums.py`, `core/ast/hashing.py`, `core/ast/models.py`, `core/benchmark/corpus/models.py`, `core/benchmark/corpus/services.py`, `core/benchmark/ground_truth/identity.py`, `core/execution/constants.py`, `core/shared/crypto.py`

**Mandato:** Determinar si el sistema puede reconstruir de forma determinista una única identidad criptográfica de baseline a partir de todas y solamente las dimensiones científicamente relevantes ya establecidas por la arquitectura, y demostrar mediante mutaciones controladas qué cambios deben alterar —o no alterar— dicha identidad y el estado de su sello.

**Síntesis:** Se auditó la taxonomía de identidades del sistema post-Fase 2. Se confirmó que `manifest_hash` es el candidato real a identidad global de baseline ($H_{baseline}$). Se identificó que `ASTSchemaVersion` no está evidenciado en runtime pese a estar declarado como DONE en NADR-15 §5.3 R8 (discrepancia documentación/runtime). Se documentó la remediación silenciosa de `compute_ast_hash` entre Fase 0 y Fase 2 sin trazabilidad documental. Se registraron 4 hallazgos forenses (H3.1-01 a H3.1-04), 3 gaps (GAP-3.1-01 a GAP-3.1-03) y 3 Decision Candidates (DC-01, DC-02, DC-03) para fases posteriores.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-08-25 | Emisión inicial. Inspección forense de 8 módulos, 12 dimensiones de identidad, 18 mutaciones. |
| 1.0.0-FROZEN | 2026-08-25 | Cierre formal del HITO. Todas las hipótesis cerradas. Gaps con fase destino explícita. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la taxonomía de identidades criptográficas del sistema post-Fase 2 (Scientific Baseline Domain). La auditoría cubrió 8 módulos de `core/ast`, `core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/execution` y `core/shared`, verificando 12 dimensiones de identidad declaradas por NADR-15 §5.3 R8 y ADR Maestro §5.

**Hallazgo central:**

> `manifest_hash` es el candidato real y existente para identidad global de baseline ($H_{baseline}$). No se requiere crear un hash paralelo. Sin embargo, `ASTSchemaVersion` no está evidenciado en runtime pese a estar declarado como DONE en NADR-15 §5.3 R8 y Execution Plan Task 4.3.1, lo que constituye una discrepancia documentación/runtime que requiere reconciliación formal en HITO 3.3. Adicionalmente, se documentó la remediación silenciosa de `compute_ast_hash` (GAP-0.3-01 de HITO 0.3 cerrado sin trazabilidad en Exit Review Evidence Log de Fase 2).

**Defectos dominantes confirmados:**

1. **H3.1-01 — ASTSchemaVersion no evidenciado en runtime (E-3.1-001, E-3.1-002, E-3.1-003):** NADR-15 §5.3 R8 y Task 4.3.1 declaran diferenciación de `ASTSchemaVersion`, `CorpusVersion` e Identity Hash. Solo `CorpusVersion` existe en runtime. `ASTSchemaVersion` no está evidenciado como entidad, campo, constante ni wiring. Estado: GAP-3.1-01 DEFERRED a HITO 3.3.

2. **H3.1-02 — Remedición silenciosa de `compute_ast_hash` (E-3.1-008):** HITO 0.3 documentó GAP-0.3-01 (P0) indicando que `compute_ast_hash` incluye `node_id`. Estado actual: `compute_ast_hash` excluye `node_id` y es determinista. Gap cerrado sin trazabilidad documental en Exit Review Evidence Log de Fase 2. Severidad: P2 (deuda de trazabilidad).

3. **H3.1-03 — Tensión documentación/implementación en `compute_ast_hash` (E-3.1-006):** Docstring afirma insensibilidad al "orden de procesamiento", pero la implementación preserva orden de secuencia. Dos contratos de hashing coexisten con propósitos distintos (`compute_ast_hash` vs `OracleSemanticIdentityCalculator`).

4. **H3.1-04 — Riesgo de canonicalización en `manifest_hash` (E-3.1-007, E-3.1-009):** Framing mediante `:` y `,` no demuestra inyectividad del encoding. No se evidencia restricción de dominio que prohíba caracteres delimitadores en `document_id` o `traits`. Ejemplo de colisión potencial: `["A:B", "C"]` y `["A", "B:C"]` producen el mismo payload `"A:B:C"`.

**Veredicto:** La arquitectura de identidad está sustancialmente implementada. `manifest_hash`, `DocumentFingerprint.sha256`, `oracle_hash` y `CorpusVersion` operan como identidades diferenciadas. La discrepancia principal es la ausencia de `ASTSchemaVersion` en runtime, que requiere reconciliación formal antes de cualquier decisión de implementación.

**Estado de preparación para siguiente documento:** HITO 3.1 proporciona evidencia forense completa para HITO 3.2 (Canonicalization Audit), HITO 3.3 (Identity Layer Compliance Audit) y HITO 3.4 (Identity Invalidation Matrix).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Este HITO no determina si `ASTSchemaVersion` debe implementarse como entidad, constante o convención. Solo registra que no está evidenciado en runtime y que existe discrepancia con la documentación de Fase 2.

Este HITO no decide si `ground_truth_state` debe formar parte de la identidad científica de baseline. Solo registra que está implementado y que su semántica ontológica (¿identidad científica o estado operacional?) permanece abierta.

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas (ADR Maestro, NADR-12..15, ENGINEERING_PRINCIPLES, METHODOLOGY).
2. Cargar HITO 0.3 como punto de partida (Reuse Before Invent, ADR Maestro §5).
3. Cargar handoffs de Fase 1 y Fase 2 para contexto histórico.
4. Cargar Execution Plan de Fase 2 como fuente de decisiones declaradas.
5. Inspeccionar runtime/código/artefactos post-Fase 2.
6. Separar Observed / Required / Decision en cada hallazgo.
7. Registrar evidencia estable con IDs canónicos (E-3.1-NNN).
8. Consolidar gaps solo cuando exista discrepancia demostrada.
9. Declarar `TO BE VERIFIED` cuando la evidencia sea insuficiente.
10. Cerrar hipótesis H1-H5 con veredicto forense.
11. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/ast/` | `hashing.py`, `models.py`, `enums.py` | 100% auditado |
| `core/benchmark/corpus/` | `models.py`, `services.py` | 100% auditado |
| `core/benchmark/ground_truth/` | `identity.py` | 100% auditado |
| `core/execution/` | `constants.py` | 100% auditado |
| `core/shared/` | `crypto.py` | 100% auditado |
| `tests/unit/` | `test_manifest_fingerprint.py`, `test_oracle_identity.py` | Referenciado (no re-auditado) |
| `docs/architecture/adr/phase-17-bis/` | NADR-15, Execution Plan, Exit Review Evidence Log | Referenciado |
| `HITO_0.3_IDENTITY_AND_CRYPTOGRAPHIC_AUDIT.md` | — | Referenciado (insumo forense) |

**Fuera de scope:**

- Evaluación topológica (TED, ZhangShasha, EntityRecall) — pertenece a Fase 4.
- Materialización del corpus canónico en disco — pertenece a Fase 5.
- Integración en CI Gates — pertenece a Fase 6.
- Implementación de `ASTSchemaVersion` — fuera de scope de auditoría forense.
- `infra/fs/corpus_repository.py` — pertenece a HITO 3.2.
- `tools/evaluation/freeze_ground_truth.py` — pertenece a HITO 3.3.

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR | `ADR_F17_BIS_MASTER.md` §3, §5 | Fuente normativa (separación de identidades, desacoplamiento) |
| NADR | `NADR-F17BIS-15.md` §5.1, §5.2, §5.3 | Regla normativa (linaje semántico, diferenciación de versiones) |
| NADR | `NADR-F17BIS-12.md`, `13.md`, `14.md` | Reglas normativas complementarias |
| HITO previo | `HITO_0.3_IDENTITY_AND_CRYPTOGRAPHIC_AUDIT.md` | Evidencia forense heredada (GAP-0.3-01, taxonomía tridimensional) |
| Código | `core/ast/hashing.py` | Observación runtime (`compute_ast_hash`) |
| Código | `core/ast/models.py` | Observación runtime (`ASTNode`, payloads) |
| Código | `core/ast/enums.py` | Observación runtime (`ContentNodeType`) |
| Código | `core/benchmark/corpus/models.py` | Observación runtime (`CorpusVersion`, `CorpusDocumentMetadata`) |
| Código | `core/benchmark/corpus/services.py` | Observación runtime (`ManifestFingerprintCalculator`) |
| Código | `core/benchmark/ground_truth/identity.py` | Observación runtime (`OracleSemanticIdentityCalculator`) |
| Código | `core/execution/constants.py` | Observación runtime (versionado de esquemas) |
| Código | `core/shared/crypto.py` | Observación runtime (funciones criptográficas base) |
| Handoff | `FASE_1_HANDOFF.md` | Estado post-Fase 1; DF-01-C diferido a Fase 3 |
| Handoff | `FASE_2_HANDOFF.md` | Estado post-Fase 2; decisiones AD-01 a AD-11 |
| Execution Plan | `PHASE_17BIS_FASE2_EXECUTION_PLAN.md` v1.9.0 | Trazabilidad regla→tarea (Task 4.3.1) |
| Evidence Log | `FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md` | Evidencia forense de decisiones de Fase 2 |
| Principios | `ENGINEERING_PRINCIPLES.md` | Fuente normativa |
| Metodología | `METHODOLOGY_FOR_FORENSIC_HITOs.md` v1.2.0 | Estructura canónica |

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

### 6.1 Matriz ontológica de dimensiones de identidad

La siguiente matriz captura qué representa cada dimensión, en qué nivel ontológico existe, quién es su autoridad, cuál es su fuente canónica, y cómo se comporta ante mutaciones.

| # | Dimensión | Ontología | Runtime representation | Authority | Canonical source | Included in `manifest_hash` | Mutation sensitivity | Expected invariance | Seal effect | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Document ID | Identidad lógica del documento dentro del corpus | `CorpusDocumentMetadata.document_id: str` | Bootstrap / Curaduría | Manifiesto | ✅ Sí (primer campo del payload) | Cambia identidad documental/global | Ninguna | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 2 | H_physical | Integridad física del PDF | `DocumentFingerprint.sha256: str` | Extraction provider (PyMuPDF) | Archivo PDF físico | ✅ Sí (segundo campo) | Cambia si cambia artefacto físico | Ninguna | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 3 | Extraction Traits | Características de desafío de extracción | `traits: FrozenSet[ExtractionChallengeTrait]` | Bootstrap / Curaduría | Manifiesto | ✅ Sí (tercer campo, ordenado alfabéticamente) | Cambia identidad de corpus | Orden de traits no altera hash | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 4 | Page Count | Metadato físico/documental | `page_count: int` | Extraction provider | Archivo PDF físico | ✅ Sí (cuarto campo) | Cambia si cambia representación física | Ninguna | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 5 | H_semantic (oracle_hash) | Identidad semántica del oráculo | `oracle_hash: Optional[str]` | `OracleSemanticIdentityCalculator` | Tupla de `ASTNode` del oráculo | ✅ Sí (quinto campo, sentinel `"none"`) | Cambia ante mutación semántica | Metadata física incidental no altera hash | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 6 | Ground Truth State | Estado del ciclo de vida del oráculo | `ground_truth_state: Optional[str]` | `LifecycleTransitionAuthority` | Transición de ciclo de vida | ✅ Sí (sexto campo, sentinel `"none"`) | Cambia identidad global actualmente | Transición `VALIDATED → SEALED` no cambia `H_semantic` | ⚠️ A DECIDIR (DC-03) | ⚠️ IMPLEMENTED / SEMANTICALLY OPEN |
| 7 | Corpus Version | Versión del conjunto de documentos | `CorpusVersion.value: str` | Bootstrap / Curaduría | Manifiesto | ✅ Sí (primer elemento del payload global) | Cambia identidad de baseline | Ninguna | Invalida sello; requiere reseal | ✅ CONFIRMADO |
| 8 | **AST Schema Version** | **Versión estructural del esquema AST** | **❌ No evidenciado en runtime** | **No asignada** | **No existe** | **❌ No visible en payload** | **Debería distinguir interpretación estructural** | **Cambio de vocabulario no altera hash** | **⚠️ A DECIDIR (DC-02)** | **🔴 GAP-3.1-01 DEFERRED** |
| 9 | manifest_hash | Identidad global del manifiesto/baseline | `ManifestFingerprintCalculator.compute_hash()` | `ManifestFingerprintCalculator` | Payload canónico | — (es el resultado) | Cambia cuando cambia payload | Orden de documentos no altera hash | Es la firma global | ✅ CONFIRMADO como candidato a $H_{baseline}$ |
| 10 | AST Semantic Hash | Firma semántica pura del AST | `compute_ast_hash()` | `core.ast.hashing` | Secuencia de `ASTNode` | ❌ No participa directamente | Cambios semánticos según su contrato | `node_id` no altera hash; orden de nodos sí (tensión con docstring) | — | ⚠️ CONTRATO DISTINTO DE H_semantic (DC-01) |
| 11 | Oracle Semantic Identity | Identidad semántica del oráculo sellado | `OracleSemanticIdentityCalculator.calculate()` | `core.benchmark.ground_truth.identity` | Tupla de `ASTNode` del oráculo | ✅ Sí (vía `oracle_hash`) | Incluye `node_id`, `node_type`, `strategy`, `payload` | Metadata física excluida | Invalida sello si cambia | ✅ CONFIRMADO |
| 12 | Regression Identity | Identidad de regresión topológica | Fuera de esta capa | `ZhangShashaEngine`, `EntityRecallEvaluator` | — | ❌ No | Cambia ante desviación estructural | — | — | ✅ ORTOGONAL (Fase 4) |

### 6.2 Nota sobre H_semantic vs Oracle Semantic Identity vs AST Semantic Hash

Tres mecanismos de hashing semántico coexisten con propósitos distintos:

- **`compute_ast_hash` (NADR-03):** Firma semántica pura del AST. Excluye `node_id`, `strategy`, `sequence_id`, `metadata`. Propósito: comparar ASTs semánticamente idénticos independientemente de identidad de nodos.
- **`OracleSemanticIdentityCalculator` (NADR-15 §5.1):** Identidad semántica del oráculo sellado. Incluye `node_id`, `node_type`, `strategy`, `payload_hash`. Propósito: capturar "qué dice el oráculo" incluyendo identidad de nodos.
- **`ASTFingerprintPolicy.semantic_fingerprint` (HITO 0.3):** Huella semántica para benchmark. Tupla `(node_type, content)`. Propósito: comparación topológica.

Son tres hashes con contratos distintos. No son redundantes. La tensión entre `compute_ast_hash` y `OracleSemanticIdentityCalculator` se documenta como DC-01.

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| AST Schema Version | No existe como entidad, campo, constante ni wiring en `core/benchmark/corpus/models.py`, `core/execution/constants.py` ni ningún módulo auditado | NADR-15 §5.3 R8: "La versión del esquema del AST, la versión del corpus y la identidad de la baseline MUST estar diferenciadas" | Task 4.3.1 (Execution Plan v1.9.0) declara DONE | 🔴 DISCREPANCY (GAP-3.1-01 DEFERRED) | E-3.1-001, E-3.1-002, E-3.1-003 |
| Corpus Version | `CorpusVersion` existe como `@dataclass(frozen=True, slots=True)` con campo `value: str` | NADR-15 §5.3 R8: diferenciación de Corpus Version | Task 4.3.1 declara DONE | ✅ COMPLIANT | E-3.1-004 |
| Identity Hash (manifest_hash) | `ManifestFingerprintCalculator.compute_hash()` calcula hash compuesto de 6 dimensiones | NADR-15 §5.3 R8: diferenciación de Identity Hash | Task 4.3.1 declara DONE | ✅ COMPLIANT | E-3.1-005 |
| H_semantic (oracle_hash) | `OracleSemanticIdentityCalculator.calculate()` calcula hash de 4 dimensiones (`node_id`, `node_type`, `strategy`, `payload`) | NADR-15 §5.1 R1-R3: oráculo sellado MUST portar identidad semántica | Task 4.1.1-4.1.3 declara DONE | ✅ COMPLIANT | E-3.1-006 |
| Separación de dimensiones | `oracle_hash`, `fingerprint.sha256`, `DocumentFingerprint`, `CorpusVersion`, `manifest_hash` residen en campos/entidades separados | NADR-15 §5.2 R4-R7: dimensiones MUST residir en lugares ontológicos diferenciados | Task 4.2.1-4.2.4 declara DONE | ✅ COMPLIANT | E-3.1-007 |
| ground_truth_state en hash | `ManifestFingerprintCalculator` incluye `ground_truth_state` en payload (sexto campo) | NADR-15 §5.3 R9: firma del catálogo MUST ser sensible al linaje de oráculos | Wave 4.2/4.3 decidió incluirlo (DF-17 RESOLVED) | ✅ COMPLIANT (semántica abierta) | E-3.1-009 |
| compute_ast_hash determinismo | `compute_ast_hash` excluye `node_id`, incluye solo `type` y `content` | NADR-03 §5.1: firma semántica determinista del AST | HITO 0.3 documentó GAP-0.3-01 (P0) indicando inclusión de `node_id` | ✅ COMPLIANT (remediación silenciosa) | E-3.1-008 |
| Observación X2 (atomicidad) | Docstring de `OracleSemanticIdentityCalculator`: "La atomicidad entre el hash físico (disco) y el hash semántico (memoria) se garantiza por la ausencia de escrituras concurrentes" | ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos | Execution Plan Task 4.1.3 documenta Observación X2 | ⚠️ ASUNCIÓN NO AUDITADA | E-3.1-010 |

---

## 8. MUTATION SEMANTICS MATRIX

| Mutación | H_physical | H_semantic | manifest_hash | ¿Identity cambia? | ¿Sello válido? | Observed behavior | Required behavior | Evidencia | Gap / DC |
|---|---|---|---|---|---|---|---|---|---|
| Cambiar bytes del PDF | ✅ Sí | ❌ No | ✅ Sí | ✅ Sí | ❌ No | Hash físico cambia, manifiesto invalidado | Correcto | E-3.1-011 | None |
| Cambiar `document_id` | ❌ No | ❌ No | ✅ Sí | ✅ Sí | ❌ No | Identidad lógica cambia, manifiesto invalidado | Correcto | E-3.1-012 | None |
| Cambiar `traits` | ❌ No | ❌ No | ✅ Sí | ✅ Sí | ❌ No | Características de extracción cambian | Correcto | E-3.1-013 | None |
| Cambiar `page_count` | ❌ No | ❌ No | ✅ Sí | ✅ Sí | ❌ No | Metadato físico cambia | Correcto | E-3.1-014 | None |
| Cambiar contenido del oráculo (payload) | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No | Identidad semántica cambia, manifiesto invalidado | Correcto | E-3.1-015 | None |
| Cambiar `node_id` sin cambiar contenido | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No | `OracleSemanticIdentityCalculator` es sensible a `node_id` | ⚠️ A DECIDIR | E-3.1-016 | **DC-01** |
| Cambiar `node_type` | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No | Tipo semántico cambia | Correcto | E-3.1-017 | None |
| Cambiar `strategy` | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No | Estrategia de traducción cambia | Correcto | E-3.1-018 | None |
| Cambiar `sequence_id` | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Sí | Metadata física, excluida de H_semantic | Correcto | E-3.1-019 | None |
| Cambiar `metadata.bboxes` | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Sí | Metadata física, excluida de H_semantic | Correcto | E-3.1-020 | None |
| Cambiar `confidence` | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Sí | Metadata de confianza, excluida de H_semantic | Correcto | E-3.1-021 | None |
| Cambiar `ground_truth_state` | ❌ No | ❌ No | ✅ Sí | ⚠️ A DECIDIR | ⚠️ A DECIDIR | Estado de lifecycle cambia, manifiesto invalidado | ⚠️ A DECIDIR | E-3.1-022 | **DC-03** |
| Cambiar `CorpusVersion` | ❌ No | ❌ No | ✅ Sí | ✅ Sí | ❌ No | Versión de corpus cambia | Correcto | E-3.1-023 | None |
| Cambiar AST schema | ❌ No | ⚠️ Potencialmente | ❌ No actualmente | ⚠️ A DECIDIR | ⚠️ A DECIDIR | No evidenciado en runtime | ⚠️ A DECIDIR | E-3.1-024 | **DC-02** |
| Reordenar documentos del manifiesto | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Sí | `sorted(documents, key=lambda doc: doc.document_id)` garantiza orden determinista | Correcto | E-3.1-025 | None |
| Reordenar `traits` dentro de documento | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Sí | `sorted([trait.value for trait in doc.traits])` garantiza orden determinista | Correcto | E-3.1-026 | None |
| Cambiar orden de nodos en oráculo | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No | `OracleSemanticIdentityCalculator` es sensible al orden | Correcto | E-3.1-027 | None |

### 8.1 Celdas A DECIDIR y su mapeo a Decision Candidates

| Celda | Pregunta forense | Decision Candidate |
|---|---|---|
| Cambiar `node_id` sin cambiar contenido | ¿Debe cambiar `H_semantic` ante mutación de `node_id` sin cambiar contenido? | **DC-01**: Ambigüedad entre `compute_ast_hash` y `OracleSemanticIdentityCalculator` |
| Cambiar AST schema | ¿Debe cambiar `manifest_hash` ante cambio de esquema AST? | **DC-02**: `ASTSchemaVersion` no materializada |
| Cambiar `ground_truth_state` | ¿Es `ground_truth_state` identidad científica o estado operacional? | **DC-03**: Semántica de `ground_truth_state` en identidad global |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-3.1-001** | P1 | `core/benchmark/corpus/models.py` → `CorpusVersion`, `CorpusDocumentMetadata`, `CorpusManifest` | **ASTSchemaVersion ausente en modelos de corpus.** No existe entidad, campo ni constante para versión de esquema AST. |
| **E-3.1-002** | P1 | `core/execution/constants.py` → `CURRENT_PROJECTION_VERSION = 1` | **constants.py no contiene ASTSchemaVersion.** Solo contiene versión de proyección de Fase 14 y nota sobre migración futura. |
| **E-3.1-003** | P1 | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `version: CorpusVersion, documents: List[CorpusDocumentMetadata]` | **manifest_hash no incluye ASTSchemaVersion.** Payload contiene 6 dimensiones, ninguna es versión de esquema AST. |
| **E-3.1-004** | — | `core/benchmark/corpus/models.py` → `@dataclass(frozen=True, slots=True) class CorpusVersion: value: str` | **CorpusVersion existe como entidad diferenciada.** Cumple NADR-15 §5.3 R8 para dimensión "Corpus Version". |
| **E-3.1-005** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` | **manifest_hash existe como identidad global.** Cumple NADR-15 §5.3 R8 para dimensión "Identity Hash". |
| **E-3.1-006** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **OracleSemanticIdentityCalculator implementa H_semantic.** Incluye `node_id`, `node_type`, `strategy`, `payload_hash`. Excluye metadata física. |
| **E-3.1-007** | — | `core/benchmark/corpus/models.py` → `oracle_hash`, `fingerprint.sha256`, `DocumentFingerprint`, `CorpusVersion` | **Dimensiones de identidad residen en campos separados.** No hay colapso de dimensiones. Cumple NADR-15 §5.2 R4-R7. |
| **E-3.1-008** | P2 | `core/ast/hashing.py::compute_ast_hash` → `return {"type": type_str, "content": n.text_content}` | **compute_ast_hash remediado silenciosamente.** HITO 0.3 documentó GAP-0.3-01 (P0) indicando inclusión de `node_id`. Estado actual: excluye `node_id`. Gap cerrado sin trazabilidad documental. |
| **E-3.1-009** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `gt_state_str = doc.ground_truth_state if doc.ground_truth_state is not None else "none"` | **ground_truth_state incluido en manifest_hash.** Sentinel `"none"` para valores ausentes. Cumple NADR-15 §5.3 R9. |
| **E-3.1-010** | P2 | `core/benchmark/ground_truth/identity.py` → docstring de `OracleSemanticIdentityCalculator.calculate()` | **Observación X2: asunción de atomicidad no auditada.** "La atomicidad entre el hash físico (disco) y el hash semántico (memoria) se garantiza por la ausencia de escrituras concurrentes durante la curaduría." |
| **E-3.1-011** | — | `core/benchmark/corpus/models.py::DocumentFingerprint.sha256` | **H_physical es SHA-256 del PDF.** Mutación de bytes físicos cambia fingerprint. |
| **E-3.1-012** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `f"{doc.document_id}:..."` | **document_id participa en manifest_hash.** Mutación cambia identidad global. |
| **E-3.1-013** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `traits_str = ",".join(sorted_traits)` | **traits participan en manifest_hash.** Ordenadas alfabéticamente para determinismo. |
| **E-3.1-014** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `f"{doc.page_count}:"` | **page_count participa en manifest_hash.** |
| **E-3.1-015** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` → `payload_hash = compute_sha256(payload_json.encode("utf-8"))` | **H_semantic es sensible a contenido de payload.** Mutación de contenido cambia oracle_hash. |
| **E-3.1-016** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` → `node_identity = f"{node.node_id}:{node.node_type.value}:{node.strategy.value}:{payload_hash}"` | **H_semantic es sensible a node_id.** Mutación de node_id sin cambiar contenido cambia oracle_hash. |
| **E-3.1-017** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **H_semantic es sensible a node_type.** |
| **E-3.1-018** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **H_semantic es sensible a strategy.** |
| **E-3.1-019** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **H_semantic excluye sequence_id.** Insensible a índice de procesamiento. |
| **E-3.1-020** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **H_semantic excluye metadata (bboxes, pages, confidence).** |
| **E-3.1-021** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` | **H_semantic excluye confidence.** |
| **E-3.1-022** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `gt_state_str` | **manifest_hash es sensible a ground_truth_state.** Mutación de estado cambia hash. |
| **E-3.1-023** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `parts = [version.value.encode("utf-8")]` | **manifest_hash es sensible a CorpusVersion.** |
| **E-3.1-024** | — | — | **AST schema change no evidenciado.** No se puede determinar impacto en manifest_hash sin evidencia de ASTSchemaVersion. |
| **E-3.1-025** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `sorted_documents = sorted(documents, key=lambda doc: doc.document_id)` | **manifest_hash es insensible a orden de documentos.** Ordenamiento determinista. |
| **E-3.1-026** | — | `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `sorted_traits = sorted([trait.value for trait in doc.traits])` | **manifest_hash es insensible a orden de traits.** Ordenamiento determinista. |
| **E-3.1-027** | — | `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` → `for node in nodes:` | **H_semantic es sensible a orden de nodos.** Iteración secuencial preserva orden. |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-3.1-01 | `compute_ast_hash` y `OracleSemanticIdentityCalculator` son dos hashes con contratos distintos. No son redundantes. `compute_ast_hash` es para comparación de parsers (agnóstico a `node_id`); `OracleSemanticIdentityCalculator` es para baseline (sensible a `node_id`). | Medio | OPEN (DC-01) |
| OBS-3.1-02 | `ground_truth_state` usa strings genéricos (`"sealed"`, `"none"`) en lugar de enum. Decisión de Fase 2 (AD-11) para evitar dependencia cruzada corpus→ground_truth. | Bajo | OPEN |
| OBS-3.1-03 | Sentinel `"none"` para valores ausentes en manifest_hash. Podría colisionar con valor legítimo si dominio permite string `"none"`. | Medio | OPEN (DQ-01) |
| OBS-3.1-04 | Delimitador `:` en payload de manifest_hash puede causar colisiones si `document_id` contiene `:`. Ejemplo: `["A:B", "C"]` y `["A", "B:C"]` producen el mismo payload `"A:B:C"`. | Medio | OPEN (DQ-02) |
| OBS-3.1-05 | DF-01-C (Fase 1) documenta explícitamente: "Linaje de identidad semántica en benchmark → Destino: Fase 2/3 → Pregunta: ¿dónde viaja `compute_ast_hash()` en lineage?" Puente explícito entre Fase 1 y Fase 3. | Medio | OPEN (contexto histórico) |
| OBS-3.1-06 | Observación X2 (atomicidad entre hash físico y hash semántico) es asunción no auditada en contexto de Fase 3. Si hay escrituras concurrentes durante curaduría, atomicidad puede violarse. | Bajo | OPEN (DQ-03) |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-3.1-01** | **ASTSchemaVersion no está evidenciado en runtime pese a estar declarado como DONE en NADR-15 §5.3 R8 y Task 4.3.1.** Discrepancia documentación/runtime. Requiere reconciliación formal en HITO 3.3. | E-3.1-001, E-3.1-002, E-3.1-003 | NADR-15 §5.3 R8 (diferenciación de versiones) | **Fase 3 (HITO 3.3)** | **DEFERRED** |
| **GAP-3.1-02** | **Tensión documentación/contrato semántico en `compute_ast_hash`.** Docstring afirma insensibilidad al "orden de procesamiento", pero la implementación preserva el orden de la secuencia de nodos. | E-3.1-006 | NADR-03 §5.1; ENGINEERING_PRINCIPLES §III | **Fase 3 (HITO 3.2)** | **OPEN** |
| **GAP-3.1-03** | **Riesgo de canonicalización en el framing de `manifest_hash`.** El payload usa `:` y `,` como delimitadores sin evidencia de restricciones formales sobre los dominios de los campos. No se demuestra colisión real, pero tampoco se demuestra inyectividad del encoding. | E-3.1-007, E-3.1-009 | ENGINEERING_PRINCIPLES §III; ADR Maestro §5 | **Fase 3 (HITO 3.2)** | **OPEN** |

**Nota sobre GAP-3.1-01:** Se clasifica como **DEFERRED** (no OPEN ni BLOCKING) porque:
- No bloquea el cierre del mandato de HITO 3.1.
- Requiere reconciliación formal en HITO 3.3 (Identity Layer Compliance Audit).
- Tiene fase destino explícita (Fase 3, HITO 3.3).
- Las hipótesis H1-H5 están cerradas (H3 y H4 confirmadas).

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-3.1-A (H1) | ASTSchemaVersion existe fuera de `core/benchmark/corpus` (ej: `core/execution/constants.py`) | **RECHAZADA** | E-3.1-002: `constants.py` contiene solo `CURRENT_PROJECTION_VERSION = 1` (Fase 14) | No existe en ubicación alternativa |
| H-3.1-B (H2) | ASTSchemaVersion existe como constante/convención implícita | **RECHAZADA** | E-3.1-001, E-3.1-002, E-3.1-003: no hay constante, campo ni wiring | No existe como convención |
| H-3.1-C (H3) | ASTSchemaVersion existe documentalmente pero no en runtime | **CONFIRMADA** | E-3.1-001, E-3.1-002, E-3.1-003: documentación declara DONE, runtime no evidencia | Discrepancia documentación/runtime |
| H-3.1-D (H4) | Documentación de Fase 2 declara DONE algo no materializado (error de gobernanza) | **CONFIRMADA** | E-3.1-001, E-3.1-002, E-3.1-003 + Execution Plan v1.9.0 Task 4.3.1 | Task 4.3.1 marcada DONE sin implementación |
| H-3.1-E (H5) | ASTSchemaVersion está representada indirectamente vía `ContentNodeType` + payloads | **RECHAZADA** | `core/ast/enums.py::ContentNodeType` es enum de tipos semánticos (11 valores), no versión de esquema | No es representación indirecta |

**Veredicto:** 3 hipótesis rechazadas, 2 confirmadas. Cero hipótesis abiertas.

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Puede el sistema reconstruir de forma determinista una única identidad criptográfica de baseline?

**Estado actual verificado:**

1. `ManifestFingerprintCalculator.compute_hash()` produce un hash SHA-256 determinista a partir de un payload canónico que incluye 6 dimensiones por documento: `document_id`, `fingerprint_sha256`, `traits`, `page_count`, `oracle_hash`, `ground_truth_state`.
2. El payload global incluye `corpus_version` como primer elemento, seguido de los payloads de documentos ordenados alfabéticamente por `document_id`.
3. Los traits de cada documento están ordenados alfabéticamente.
4. El hash es 100% determinista: mismo input → mismo output.

**Respuesta forense:**

Sí, el sistema puede reconstruir de forma determinista una única identidad criptográfica de baseline. `manifest_hash` es el candidato existente a $H_{baseline}$. No es necesario crear un mecanismo paralelo.

**Implicación:**

Fase 3 debe auditar si el contenido actual de `manifest_hash` satisface completamente el contrato de Baseline Identity, no si debe crearse un nuevo mecanismo.

### 16.2 ¿Qué cambios deben alterar —o no alterar— dicha identidad y el estado de su sello?

**Estado actual verificado:**

1. La Mutation Semantics Matrix (§8) documenta 18 mutaciones y su efecto sobre `H_physical`, `H_semantic`, `manifest_hash`, identidad global y sello.
2. 14 mutaciones tienen comportamiento claro (cambian o no cambian identidad, invalidan o no sello).
3. 3 mutaciones tienen comportamiento `A DECIDIR` mapeadas a Decision Candidates: cambiar `ground_truth_state` (DC-03), cambiar AST schema (DC-02), cambiar `node_id` sin cambiar contenido (DC-01).

**Respuesta forense:**

La mayoría de las mutaciones tienen comportamiento claro. Las 3 mutaciones `A DECIDIR` son Decision Candidates que deben resolverse en el ADR/NADR de Fase 3.

**Implicación:**

Fase 3 debe resolver los 3 Decision Candidates antes de implementar el encadenamiento criptográfico global.

### 16.3 ¿Existen todas y solamente las dimensiones científicamente relevantes ya establecidas por la arquitectura?

**Estado actual verificado:**

1. El inventario de dimensiones (§6) identifica 12 dimensiones.
2. 7 dimensiones están CONFIRMADAS.
3. 2 dimensiones tienen contratos distintos (`compute_ast_hash` y `OracleSemanticIdentityCalculator`).
4. 1 dimensión está semánticamente abierta (Ground Truth State).
5. 1 dimensión está GAP-3.1-01 DEFERRED (AST Schema Version).
6. 1 dimensión está explícitamente descartada (H_baseline separado).
7. 1 dimensión es ortogonal (Regression Identity, Fase 4).

**Respuesta forense:**

No todas las dimensiones establecidas por la arquitectura están materializadas. AST Schema Version (NADR-15 §5.3 R8) no está materializada en el runtime (GAP-3.1-01). Además, existen tensiones normativas en H_semantic (DC-01) y preguntas abiertas sobre Ground Truth State (DC-03).

**Implicación:**

Fase 3 debe resolver GAP-3.1-01, DC-01, y DC-03 antes de certificar la baseline.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-01** (nuevo) | **Ambigüedad entre `compute_ast_hash` y `OracleSemanticIdentityCalculator`.** ¿Son dos identidades semánticas distintas con propósitos distintos, o debe `OracleSemanticIdentityCalculator` usar `compute_ast_hash`? NADR-15 §5.1 R3 dice "gobernada por el contrato canónico de hashing". | E-3.1-006, E-3.1-008, E-3.1-016 | `compute_ast_hash` excluye `node_id`; `OracleSemanticIdentityCalculator` lo incluye. Ambos existen como mecanismos independientes. | **Fase 3** (ADR/NADR de Fase 3) |
| **DC-02** (nuevo) | **ASTSchemaVersion no materializada.** ¿Debe materializarse `ASTSchemaVersion` como entidad, o es suficiente con `ContentNodeType` como representación indirecta? NADR-15 §5.3 R8 exige diferenciación explícita. | E-3.1-001, E-3.1-002, E-3.1-003 | ASTSchemaVersion no existe en runtime. `ContentNodeType` define el vocabulario estructural, pero no hay versión explícita. | **Fase 3** (ADR/NADR de Fase 3) |
| **DC-03** (nuevo) | **Semántica de `ground_truth_state` en identidad global.** ¿Es identidad científica o estado operacional? Si es identidad científica, cambiar estado DEBE alterar `manifest_hash`. Si es estado operacional, NO debería alterarlo. | E-3.1-009, E-3.1-022 | Actualmente altera `manifest_hash` (DF-17 RESOLVED). Transición `VALIDATED → SEALED` no cambia `H_semantic`. | **Fase 3** (HITO 3.4 o ADR/NADR) |
| **DC-01** (histórico, HITO 0.3) | Rediseñar `compute_ast_hash` para H_semantic pura | E-3.1-008 | **RESUELTO** (remediación silenciosa entre Fase 0 y Fase 2). Gap cerrado sin trazabilidad documental. | Fase 2 (cerrado) |
| **DC-03** (histórico, HITO 0.3) | Fórmula de encadenamiento global $H_{baseline}$ | E-3.1-005, E-3.1-009 | **RESUELTO** (`manifest_hash` es candidato a $H_{baseline}$) | Fase 3 (HITO 3.3) |
| **DC-08** (histórico, HITO 0.3) | Determinismo de IDs de fragmentos | E-3.1-016 | **PARCIAL** (`OracleSemanticIdentityCalculator` incluye `node_id`, sensible a cambios) | Fase 3 (HITO 3.3) |
| **DC-09** (histórico, HITO 0.3) | Armonización de contrato de `BoundaryPolicy` | — | **OUT-OF-SCOPE** (no auditado en HITO 3.1) | Fase 18 |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| **Deuda de trazabilidad documental** | La remediación de `compute_ast_hash` (GAP-0.3-01 de HITO 0.3) se realizó entre Fase 0 y Fase 2, pero no está documentada en Exit Review Evidence Log de Fase 2. Esto viola la cadena de trazabilidad regla→tarea→evidencia. | Medio | E-3.1-008 |
| **Colisión por framing no inyectivo** | El payload de `manifest_hash` usa `:` y `,` como delimitadores. Si los dominios de `document_id`, `trait.value`, `oracle_hash` o `ground_truth_state` permiten estos caracteres, pueden producirse colisiones. | Medio | E-3.1-007, E-3.1-009 |
| **Asunción de atomicidad no auditada** | La Observación X2 asume ausencia de escrituras concurrentes durante curaduría. Si esta asunción falla, la atomicidad entre hash físico y hash semántico puede violarse. | Bajo | E-3.1-010 |
| **Sentinel `"none"` puede colisionar** | Si algún campo puede tener literalmente el valor `"none"`, el sentinel puede causar ambigüedad. | Bajo | E-3.1-009 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este Discovery, el ADR o NADR posterior de Fase 3 deberá responder:

1. **¿`OracleSemanticIdentityCalculator` debe reutilizar `compute_ast_hash`?** Si NADR-15 §5.1 R3 se interpreta como "usar el contrato canónico de hashing", entonces `OracleSemanticIdentityCalculator` debería usar `compute_ast_hash`. Si se interpreta como "usar un mecanismo de hashing determinista gobernado por un contrato canónico", entonces pueden coexistir. El ADR/NADR de Fase 3 debe clarificar esta interpretación.

2. **¿`ASTSchemaVersion` debe materializarse como entidad?** NADR-15 §5.3 R8 exige diferenciación explícita. El Execution Plan Task 4.3.1 declara DONE, pero el runtime no la materializó. El ADR/NADR de Fase 3 debe decidir si se materializa como entidad (ej: `ASTSchemaVersion(value="v2.0")`) o si se considera que `ContentNodeType` es la representación indirecta suficiente.

3. **¿El estado del Ground Truth es identidad científica o estado operacional?** Si es identidad científica, entonces cambiar el estado DEBE alterar `manifest_hash` (como ocurre actualmente). Si es estado operacional, entonces cambiar el estado NO debería alterar `manifest_hash` (solo debería alterar la validez del sello). El ADR/NADR de Fase 3 debe clarificar esta semántica.

4. **¿El framing de `manifest_hash` es suficientemente inyectivo?** El payload usa `:` y `,` como delimitadores. ¿Deben imponerse restricciones formales sobre los dominios de `document_id`, `trait.value`, `oracle_hash` y `ground_truth_state` para garantizar que no haya colisiones? El ADR/NADR de Fase 3 debe decidir si se requiere un framing más robusto (ej: length-prefixed fields, JSON canónico).

5. **¿La asunción de atomicidad (Observación X2) es válida en el contexto de Fase 3?** La atomicidad entre el hash físico (disco) y el hash semántico (memoria) se garantiza por la ausencia de escrituras concurrentes durante la curaduría. ¿Es válida esta asunción en el contexto de Fase 3? ¿Qué pasa si hay escrituras concurrentes?

---

## 21. CIERRE DEL HITO 3.1

Este HITO confirma que la taxonomía de identidades del sistema post-Fase 2 está sustancialmente implementada. `manifest_hash` es el candidato real a identidad global de baseline ($H_{baseline}$). `DocumentFingerprint.sha256`, `oracle_hash` y `CorpusVersion` operan como identidades diferenciadas. La discrepancia principal es la ausencia de `ASTSchemaVersion` en runtime (GAP-3.1-01 DEFERRED a HITO 3.3), que requiere reconciliación formal.

**Estado del HITO:** FROZEN v1.0.0

**Condición de cierre cumplida:**

- [x] Metadata completa y consistente.
- [x] Changelog actualizado a versión de cierre.
- [x] Límite epistemológico declarado.
- [x] Alcance auditado completo (8 módulos, 100% auditados).
- [x] Fuentes de evidencia listadas (18 fuentes).
- [x] 100% módulos auditados.
- [x] Todas evidencias tienen ID estable (E-3.1-001 a E-3.1-027).
- [x] Todas evidencias tienen severidad clasificada (P1, P2, —).
- [x] Todas evidencias relevantes separan Observed/Required/Decision.
- [x] Todos gaps tienen evidencia vinculada (GAP-3.1-01 → E-3.1-001, 002, 003; GAP-3.1-02 → E-3.1-006; GAP-3.1-03 → E-3.1-007, 009).
- [x] Todos gaps tienen fase destino explícita (Fase 3, HITO 3.2 o HITO 3.3).
- [x] Todas hipótesis cerradas (H-3.1-A a H-3.1-E: 2 CONFIRMADAS, 3 RECHAZADAS).
- [x] Cero hipótesis abiertas.
- [x] Cero contradicciones no documentadas con HITOs previos.
- [x] Contradicción con HITO 0.3 documentada y reconciliada (E-3.1-008: remediación silenciosa de `compute_ast_hash`).
- [x] IDs estables.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.

**Verificación de cadena de gobernanza:**

```
ADR_F17_BIS_MASTER §3, §5
  → NADR-F17BIS-15 §5.1, §5.2, §5.3
  → HITO_0.3_IDENTITY_AND_CRYPTOGRAPHIC_AUDIT (FROZEN)
  → FASE_1_HANDOFF (FROZEN)
  → FASE_2_HANDOFF (FROZEN)
  → FASE_2_EXIT_REVIEW_EVIDENCE_LOG (FROZEN)
  → PHASE_17BIS_FASE2_EXECUTION_PLAN v1.9.0 (APPROVED)
  → HITO_3.1_IDENTITY_DIMENSION_ONTOLOGY_MUTATION_MATRIX (FROZEN)
```

**Contradicciones con HITOs previos:**

- **HITO 0.3 GAP-0.3-01:** Documentó que `compute_ast_hash` incluye `node_id`. HITO 3.1 observa que `compute_ast_hash` excluye `node_id`. Contradicción reconciliada: gap cerrado silenciosamente entre Fase 0 y Fase 2. Trazabilidad documental faltante (E-3.1-008, severidad P2).

**Decision Candidates generados:**

1. **DC-01 (nuevo):** Ambigüedad entre `compute_ast_hash` y `OracleSemanticIdentityCalculator`. (Destino: ADR/NADR de Fase 3)
2. **DC-02 (nuevo):** ASTSchemaVersion no materializada. (Destino: ADR/NADR de Fase 3)
3. **DC-03 (nuevo):** Semántica de `ground_truth_state` en identidad global. (Destino: HITO 3.4 o ADR/NADR de Fase 3)

**Deferred Questions:**

1. **DQ-01:** ¿El sentinel `"none"` puede colisionar con un valor legítimo?
2. **DQ-02:** ¿El delimitador `:` puede causar colisiones si `document_id` contiene `:`?
3. **DQ-03:** ¿La asunción de atomicidad (Observación X2) es válida en el contexto de Fase 3?

**Siguiente paso recomendado:** Proceder con HITO 3.2 (Canonicalization & Hashing Audit) para auditar riesgos de canonicalización identificados en GAP-3.1-03 y tensiones de contratos de hashing identificadas en GAP-3.1-02.

---

**Nota de Gobernanza:** Este documento es evidencia forense pura. No prescribe implementación. No diseña código. No crea entidades. Su función es proporcionar evidencia confiable para que HITO 3.2, HITO 3.3, HITO 3.4 y el ADR de Fase 3 puedan tomar decisiones arquitectónicas fundamentadas.