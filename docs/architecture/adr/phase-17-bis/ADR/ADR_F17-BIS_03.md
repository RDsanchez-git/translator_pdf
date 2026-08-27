# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17-BIS_03: Identity & Trust Model — Cryptographic Baseline Identity

* **Estado:** APPROVED
* **Versión:** 1.0.0
* **Fecha de Emisión:** 2026-08-27
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** Fase 17-BIS (Scientific Baseline / Canonical Corpus)
* **Evidencia Forense Vinculante:**
  * `HITO_3.1_IDENTITY_DIMENSION_ONTOLOGY_MUTATION_MATRIX.md` (FROZEN v1.0.0) — DC-01, DC-02, DC-03
  * `HITO_3.2_CANONICALIZATION_AND_HASHING_AUDIT.md` (FROZEN v1.2.0) — DC-04, DC-05, DC-06
  * `HITO_3.3_IDENTITY_LAYER_COMPLIANCE_AUDIT.md` (FROZEN v1.1.0) — DC-07, DC-08
  * `FASE_2_EXIT_REVIEW_EVIDENCE_LOG.md` (FROZEN v1.0.0) — DF-17, DF-19
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER.md` (FROZEN), `ADR_F17_BIS_02.md` (FROZEN)
  * **Implementado por:** NADRs de Fase 3 (por promulgar)
  * **Ejecutado por:** `PHASE_17BIS_FASE3_EXECUTION_PLAN.md` (por redactar)
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla la decisión arquitectónica de la Fase 3 (Identity & Trust Model) dentro de Fase 17-BIS, conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase, resolviendo los Decision Candidates identificados en la auditoría forense de Fase 3.0.

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 2 (Scientific Baseline Domain) completó exitosamente la formalización de la ontología del oráculo (`GroundTruthDraft`/`SealedOracle`), el contrato de validez estructural, la completitud biyectiva (Zero Partial Sealing), la autoridad única de sellado y el portado de la identidad semántica (`oracle_hash`) al modelo de baseline. El wiring de identidad es funcionalmente robusto: `manifest_hash`, `DocumentFingerprint.sha256`, `oracle_hash` y `CorpusVersion` operan como identidades diferenciadas.

Sin embargo, la auditoría forense de Fase 3.0 (HITOs 3.1, 3.2, 3.3) identificó tres incertidumbres arquitectónicas que deben resolverse formalmente antes de certificar la baseline:

1. **Ambigüedad entre contratos de hashing semántico (DC-01, HITO 3.1):** `compute_ast_hash` (NADR-03) y `OracleSemanticIdentityCalculator` (NADR-15) coexisten con semánticas distintas. El primero excluye `node_id`; el segundo lo incluye. NADR-15 §5.1 R3 exige que la identidad semántica corresponda a "la firma semántica determinista del AST gobernada por el contrato canónico de hashing", lo que genera tensión interpretativa.

2. **Framing no formalmente inyectivo (DC-04, DC-05, HITO 3.2):** `manifest_hash` y `oracle_hash` usan `:` como delimitador sin restricciones explícitas de dominio en `document_id` y `node_id`. El análisis forense demostró que el riesgo de colisión es teórico y mitigado por las restricciones del dominio real (Windows prohíbe `:` en nombres de archivo, `fingerprint.sha256` es ancla de 64 chars hex, `node_id` sigue formato estricto), pero viola el principio de Explicit over Implicit.

3. **Alucinación documental de ASTSchemaVersion (DC-07, HITO 3.3):** NADR-15 §5.3 R8 y Execution Plan Task 4.3.1 declaran DONE la diferenciación de `ASTSchemaVersion`, pero el runtime no contiene ninguna entidad, campo o constante que la represente. El análisis de impacto práctico demostró que este riesgo es teórico y mitigado por el acoplamiento implícito a `CorpusVersion` (cualquier cambio de esquema AST obliga a regenerar el corpus, forzando un nuevo `CorpusVersion`).

---

## 2. PROBLEMA ARQUITECTÓNICO

La identidad criptográfica de la baseline existe en el runtime (`manifest_hash`), pero su contrato formal no está cerrado. Las dimensiones de identidad están desacopladas en la práctica, pero no están formalmente gobernadas en su totalidad. Esto impide que la baseline sea certificable bajo los invariantes del ADR Maestro §5 (Determinismo y Reproducibilidad, Desacoplamiento de Identidades).

**Dimensiones estructurales afectadas:**

1. **Identidad Semántica ($H_{semantic}$):** La coexistencia de dos contratos de hashing semántico (`compute_ast_hash` y `OracleSemanticIdentityCalculator`) sin una justificación arquitectónica explícita genera ambigüedad sobre cuál es la identidad canónica del oráculo.

2. **Inyectividad del Encoding:** El framing de `manifest_hash` y `oracle_hash` no garantiza formalmente la inyectividad, aunque el dominio real mitiga el riesgo. Esto viola el principio de Explicit over Implicit y Fail-Fast.

3. **Versionado de Esquema AST:** La ausencia de `ASTSchemaVersion` como dimensión explícita viola literalmente NADR-15 §5.3 R8, aunque el acoplamiento implícito a `CorpusVersion` mitiga el impacto práctico.

**Consecuencias de no resolver el problema:**

* **Imposibilidad de certificación formal:** La baseline no puede ser certificada como "identidad criptográfica inmutable" si existen ambigüedades normativas no resueltas.
* **Violación de invariantes del ADR Maestro:** El Desacoplamiento de Identidades (§5) y el Determinismo (§5) no están formalmente garantizados.
* **Deuda de gobernanza:** La discrepancia entre documentación (NADR-15 §5.3 R8 declarada DONE) y runtime (`ASTSchemaVersion` inexistente) erosiona la credibilidad del Architecture Board.

---

## 3. DECISIÓN ARQUITECTÓNICA

**La identidad criptográfica de la baseline ($H_{baseline}$) se materializa como `manifest_hash`, calculado determinísticamente por `ManifestFingerprintCalculator` a partir de las dimensiones de identidad desacopladas: `CorpusVersion`, `DocumentFingerprint.sha256` ($H_{physical}$), `oracle_hash` ($H_{semantic}$), `ground_truth_state`, `traits` y `page_count`. La versión del esquema AST está implícitamente acoplada a `CorpusVersion` y al release del software, por lo que no se requiere un campo de identidad separado en el modelo de dominio.**

En consecuencia:

* **DC-01 — Coexistencia de contratos de hashing semántico:** `compute_ast_hash` y `OracleSemanticIdentityCalculator` coexisten como contratos legítimos con propósitos distintos. `compute_ast_hash` es la firma semántica pura del AST (agnóstica a `node_id`), utilizada para comparación de parsers y evaluación topológica. `OracleSemanticIdentityCalculator` es la identidad semántica del oráculo sellado (sensible a `node_id`), utilizada para el linaje de la baseline. Ambos son deterministas y sensibles a mutaciones relevantes.

* **DC-03 — Semántica de `ground_truth_state`:** Se establece que `ground_truth_state` es estado operacional del ciclo de vida, no identidad científica del contenido. Sin embargo, su inclusión en `manifest_hash` es correcta porque: (1) garantiza que un oráculo no pueda ser 'des-sellado' silenciosamente, (2) protege la integridad del proceso de certificación, y (3) cualquier cambio de estado invalida el sello y requiere re-certificación. Por lo tanto, `ground_truth_state` forma parte de la identidad de baseline en el sentido de 'identidad del proceso de certificación', no de 'identidad del contenido científico'.

* **DC-04, DC-05 — Validación explícita de dominio:** Se requiere validación explícita de `document_id` y `node_id` para garantizar formalmente la inyectividad del framing, cumpliendo Explicit over Implicit y Fail-Fast sin incurrir en sobreingeniería (YAGNI). El mecanismo específico de validación (regex, validadores de Pydantic, etc.) queda gobernado por los NADRs de Fase 3.

* **DC-07 — Superseedado de NADR-15:** Se promulga NADR-F17BIS-15 v2.0 que superseedea a v1.0, estableciendo explícitamente que la versión del esquema AST está implícitamente acoplada a `CorpusVersion`, eliminando la necesidad de un campo separado y alineando la documentación con el runtime.

* **DC-06 — Sensibilidad al orden en `compute_ast_hash`:** Se establece que `compute_ast_hash` es sensible al orden de los nodos, lo cual es semánticamente correcto para un AST (el orden de los nodos es parte de la identidad estructural del documento). El docstring actual es ambiguo al mencionar "independientemente de su orden de procesamiento". Se requiere actualizar la documentación para clarificar que la función es sensible al orden de la secuencia de nodos. Los detalles de implementación quedan gobernados por el NADR de Fase 3 que formalice DC-06.

* **Confianza = Verificabilidad por recomputación:** "Trust" en "Identity & Trust Model" significa la capacidad de cualquier consumidor autorizado para verificar/recomputar la identidad de manera determinista a partir de inputs canónicos. No incluye PKI, infraestructura de claves, modelo de linaje con predecesores, attestation authority ni identidad de productor.

* **Atomicidad de hashes:** La atomicidad entre el hash físico (disco) y el hash semántico (memoria) se garantiza por la ausencia de escrituras concurrentes durante la curaduría (Observación X2, HITO 3.2). Esta asunción es válida en el contexto de single-node local y no requiere validación adicional. Si en el futuro se introduce concurrencia en la curaduría, se deberá reevaluar esta garantía.

---

## 4. OBJETIVO DE LA SUBFASE

El objetivo de la Fase 3 (Identity & Trust Model) es formalizar el encadenamiento criptográfico global de la baseline, garantizando que cualquier consumidor autorizado pueda recomputar la identidad de manera determinista a partir de los inputs canónicos, y que las dimensiones de identidad estén formalmente desacopladas y gobernadas.

El objetivo primordial es garantizar que:

> *"La identidad de la baseline ($H_{baseline}$) sea recomputable, determinista y sensible a todas las mutaciones científicamente relevantes, sin ambigüedades normativas ni discrepancias entre documentación y runtime."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance

* Formalización del contrato de identidad de baseline ($H_{baseline}$) como `manifest_hash`.
* Resolución normativa de DC-01 (coexistencia de `compute_ast_hash` y `OracleSemanticIdentityCalculator`).
* Resolución normativa de DC-03 (semántica de `ground_truth_state` como estado operacional del ciclo de vida).
* Resolución normativa de DC-07 (superseedado de NADR-15 v1.0 por NADR-15 v2.0 para acoplamiento implícito de `ASTSchemaVersion` a `CorpusVersion`).
* Implementación de validación explícita de dominio para `document_id` y `node_id` como defensa en profundidad (DC-04, DC-05).
* Aclaración del docstring de `compute_ast_hash` para eliminar ambigüedad sobre sensibilidad al orden (DC-06).
* Limpieza de campos huérfanos en `RawDocumentEntryDTO` (`ground_truth_version`, `ground_truth_sha256`) que no participan en la identidad (DC-08).

### Fuera del Alcance (Out of Scope)

* **NO** materializar el corpus canónico en disco (pertenece a Fase 5 — Baseline Certification).
* **NO** implementar evaluación topológica ni semántica de regresión (pertenece a Fase 4 — Scientific Verification).
* **NO** integrar compuertas de regresión en CI/CD (pertenece a Fase 6 — Continuous Verification).
* **NO** introducir infraestructura distribuida (Redis, Message Brokers, Kubernetes, DBs remotas) (viola ADR Maestro §4).
* **NO** modificar la ontología del oráculo formalizada en Fase 2 (NADRs 12-14 permanecen FROZEN; NADR-15 es superseedado por v2.0).

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`):

* **Separación de Conceptos Fundamentales (§3):** Integridad ≠ Identidad ≠ Regresión. Las dimensiones de identidad no se colapsan.
* **Zero Partial Sealing (§5):** Ninguna baseline entra en estado sellado sin correspondencia biyectiva completa ($N_{PDF} = N_{GT}$).
* **Determinismo y Reproducibilidad (§5):** Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser 100% determinista.
* **Desacoplamiento de Identidades (§5):** AST Schema Version, Corpus Version e Identity Hash deben permanecer diferenciados (o, en el caso de `ASTSchemaVersion`, implícitamente acoplados a `CorpusVersion` con justificación normativa explícita).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

**Principios específicos de la subfase (no normativos, declarativos):**

* **Trust como verificabilidad por recomputación:** "Trust" en "Identity & Trust Model" significa la capacidad de cualquier consumidor autorizado para verificar/recomputar la identidad de manera determinista a partir de inputs canónicos. No incluye PKI, atestación ni autoridad de productor.
* **Pragmatismo sobre pureza teórica:** Las decisiones arquitectónicas deben equilibrar principios de ingeniería (Explicit over Implicit, Fail-Fast) con pragmatismo (YAGNI, impacto práctico nulo). La validación explícita de dominio es la solución óptima: bajo costo, alto beneficio, sin sobreingeniería.

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

Tras la implementación de la Fase 3, la arquitectura de identidad de la baseline será:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IDENTIDAD DE BASELINE ($H_{baseline}$)            │
│                    manifest_hash = SHA-256(payload canónico)         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ CorpusVersion │         │ H_physical      │         │ H_semantic      │
│ (conjunto)    │         │ (artefacto)     │         │ (oráculo)       │
│               │         │                 │         │                 │
│ "v1.0"        │         │ SHA-256 del PDF │         │ OracleSemantic  │
│               │         │ + page_count    │         │ IdentityCalc    │
│               │         │ + traits        │         │ (node_id,       │
│               │         │   document_id   │         │  node_type,     │
│               │         │                 │         │  strategy,      │
│               │         │                 │         │  payload)       │
└───────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ ground_truth_state            │
                    │ ("sealed" | "none")           │
                    │ Estado operacional del        │
                    │ ciclo de vida                 │
                    └───────────────────────────────┘

ASTSchemaVersion: Implícitamente acoplado a CorpusVersion.
                  Cualquier cambio de esquema → nuevo CorpusVersion.
```

**Invariante del estado objetivo:**

> *"La identidad de la baseline es recomputable, determinista y sensible a todas las mutaciones científicamente relevantes. Las dimensiones de identidad están formalmente desacopladas, validadas explícitamente y gobernadas por contratos normativos sin ambigüedades."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la Fase 3 (Identity & Trust Model) | ✅ |
| `ADR_F17_BIS_02.md` | Este ADR depende de la ontología del oráculo formalizada en Fase 2 | ✅ |
| `NADR-F17BIS-12.md` | Fase 2 materializó la ontología del oráculo; Fase 3 la consume sin modificar | ✅ |
| `NADR-F17BIS-13.md` | Fase 2 materializó validez y completitud; Fase 3 la consume sin modificar | ✅ |
| `NADR-F17BIS-14.md` | Fase 2 materializó autoridad única y asimetría de puertos; Fase 3 la consume sin modificar | ✅ |
| `NADR-F17BIS-15.md` | Fase 2 materializó linaje de identidad semántica; Fase 3 superseedea §5.3 R8 (DC-07) y formaliza §5.1 R3 (DC-01) | ✅ |
| `HITO_3.1_IDENTITY_DIMENSION_ONTOLOGY_MUTATION_MATRIX.md` | Evidencia forense que fundamenta DC-01, DC-02, DC-03 | ✅ |
| `HITO_3.2_CANONICALIZATION_AND_HASHING_AUDIT.md` | Evidencia forense que fundamenta DC-04, DC-05, DC-06 | ✅ |
| `HITO_3.3_IDENTITY_LAYER_COMPLIANCE_AUDIT.md` | Evidencia forense que fundamenta DC-07, DC-08 | ✅ |
| `PHASE_17BIS_FASE3_EXECUTION_PLAN.md` | Secuencia las tareas que materializan este ADR (por redactar) | ✅ |
| NADRs de Fase 3 (por promulgar) | Implementan las reglas normativas de este ADR | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

---

**Nota de Gobernanza:** Este ADR resuelve formalmente los Decision Candidates identificados en la auditoría forense de Fase 3.0 (DC-01, DC-03, DC-04, DC-05, DC-06, DC-07, DC-08). Las decisiones están fundamentadas en evidencia empírica del código real y equilibradas con los principios de ingeniería del proyecto (YAGNI, Explicit over Implicit, Fail-Fast, Pragmatismo). Los detalles normativos específicos quedan gobernados por los NADRs de Fase 3 (por promulgar).