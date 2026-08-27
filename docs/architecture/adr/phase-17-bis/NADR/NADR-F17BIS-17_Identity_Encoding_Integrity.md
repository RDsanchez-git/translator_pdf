# NADR-F17BIS-17: Domain Contracts for Cryptographic Identities

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-17`
* **Título:** Contratos de Dominio para Identidades Criptográficas
* **Clase de Decisión:** `DATA` / `GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Phase 17-BIS (Fase 3 — Identity & Trust Model)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-017 (Domain Contracts for Cryptographic Identities) — garantía de que los campos que participan en identidades criptográficas tengan contratos de dominio formalmente definidos, validados y verificables, previniendo colisiones, ambigüedades y comportamientos indefinidos.
* **Evidencia Forense:** `E-3.2-001`, `E-3.2-002`, `E-3.2-003`, `E-3.2-004`, `GAP-3.2-01`, `GAP-3.2-02`, `DC-04` (HITO 3.2), `DC-05` (HITO 3.2)
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-15` v2.0 (linaje de identidad semántica), `NADR-F17BIS-16` (semántica de dimensiones de identidad).
  * **Influencia:** `NADR-F17BIS-16` (la integridad del encoding garantiza que las dimensiones semánticas se serialicen sin colisiones).
  * **Conflictúa con:** Todo mecanismo que permita que campos con dominios no validados participen en identidades criptográficas; todo framing que no garantice inyectividad del encoding.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 3 — Aunque el riesgo de colisión es teórico en el dominio actual (Windows prohíbe `:` en nombres de archivo, `fingerprint.sha256` es ancla de 64 chars hex), la falta de validación explícita de dominio viola los principios de Explicit over Implicit y Fail-Fast, generando deuda técnica y riesgo de regresión futura si el dominio evoluciona.
* **Mantenibilidad:** 3 — La ausencia de contratos formales de dominio impide que implementadores futuros comprendan las restricciones de los campos que participan en identidades criptográficas, incrementando el riesgo de introducción de bugs.
* **Recuperabilidad:** 2 — No afecta directamente la recuperación de datos, pero una colisión en identidades criptográficas podría corromper la baseline y requerir re-certificación.
* **Seguridad:** 2 — La exposición se limita a la integridad de la baseline, no a superficie de red. Sin embargo, una colisión podría permitir mutaciones silenciosas de la baseline.
* **Financiero:** 3 — Una baseline corrupta por colisión de identidades fuerza re-ejecuciones de certificación y compromete la credibilidad del sistema.
* **Total Score: 13/25**

**Severidad:** `S2`

**Justificación del Score:** Aunque el riesgo de colisión es teórico en el dominio actual, la ausencia de validación explícita de dominio viola principios fundamentales de ingeniería (Explicit over Implicit, Fail-Fast) y genera deuda técnica. El score de 13/25 refleja que este NADR gobierna una capacidad crítica para la integridad a largo plazo del sistema, aunque el impacto inmediato sea bajo.

---

## 3. DECISIÓN EJECUTIVA

**Los campos que participan en identidades criptográficas deben tener contratos de dominio formalmente definidos, validados en el punto de construcción del objeto de dominio, y verificables mediante mecanismos automatizados, de tal forma que se prevengan colisiones, ambigüedades y comportamientos indefinidos en el encoding de identidades.**

En consecuencia:
* Queda prohibido que campos con dominios no validados participen en identidades criptográficas.
* Queda prohibido que los mecanismos de hashing utilicen framing que no garantice inyectividad del encoding.
* Todo campo que participe en una identidad criptográfica **MUST** tener su dominio formalmente definido y documentado.
* La validación de dominio **MUST** aplicarse mediante fail-fast (rechazo explícito en la construcción), no mediante advertencias silenciosas.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de garantizar que los campos que participan en identidades criptográficas tengan contratos de dominio formalmente definidos estaba ausente. La auditoría forense de Fase 3.0 identificó dos clases de defecto:

1. **Framing no formalmente inyectivo:** Los mecanismos de hashing (`manifest_hash`, `oracle_hash`) utilizan delimitadores (`:`, `,`) sin restricciones explícitas de dominio en los campos que delimitan. Aunque el análisis forense demostró que el riesgo de colisión es teórico y mitigado por las restricciones del dominio real (Windows prohíbe `:` en nombres de archivo, `fingerprint.sha256` es ancla de 64 chars hex, `node_id` sigue formato estricto), esto viola el principio de Explicit over Implicit.

2. **Ausencia de validación explícita de dominio:** Los campos `document_id` y `node_id` no tienen validaciones que restrinjan caracteres especiales, lo que permite teóricamente la inclusión de delimitadores en sus valores. Aunque en la práctica esto no ocurre (los valores provienen de nombres de archivo y formatos estrictos de generación), la ausencia de validación explícita genera deuda técnica y riesgo de regresión futura.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-3.2-001` / `GAP-3.2-01` (P2 — Medio):** `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` utiliza `:` como delimitador en el framing. `document_id` no tiene restricción explícita de dominio que prohíba `:`. Aunque el riesgo es teórico (Windows prohíbe `:` en nombres de archivo), viola Explicit over Implicit.

* **`E-3.2-003` / `GAP-3.2-02` (P2 — Medio):** `core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate` utiliza `:` como delimitador en `node_identity`. `node_id` no tiene restricción explícita de dominio que prohíba `:`. Aunque el formato de generación de `node_id` nunca produce `:`, la ausencia de validación explícita genera deuda técnica.

* **`E-3.2-002` (P3 — Bajo):** `core/benchmark/corpus/models.py::CorpusDocumentMetadata.document_id` tiene validación `min_length=1` pero no restringe caracteres especiales.

* **`E-3.2-004` (P3 — Bajo):** `core/ast/models.py::ASTNode.node_id` no tiene validación de dominio.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Contratos de dominio de campos criptográficos
1. Todo campo que participe en una identidad criptográfica **MUST** tener su dominio formalmente definido y documentado.
2. La definición de dominio **MUST** especificar explícitamente qué valores son válidos y qué valores están prohibidos.
3. La validación de dominio **MUST** aplicarse en el punto de construcción del objeto de dominio, no en puntos posteriores del pipeline.
4. La validación de dominio **MUST** aplicarse mediante fail-fast (rechazo explícito con excepción), no mediante advertencias silenciosas o correcciones implícitas.

### 5.2 Inyectividad del encoding
5. Los mecanismos de hashing **MUST** garantizar la inyectividad del encoding, de tal forma que dos payloads distintos no puedan producir el mismo hash debido a ambigüedades en el framing.
6. Cuando se utilice framing basado en concatenación con delimitadores, los dominios de los campos **MUST** excluir los caracteres utilizados como delimitadores.
7. Cuando los dominios de los campos no puedan garantizar la exclusión de delimitadores, los mecanismos de hashing **SHOULD** utilizar serialización canónica que garantice determinismo y unicidad.
8. La inyectividad del encoding **MUST** ser verificable mediante mecanismos automatizados (tests, análisis estático o verificación formal).

### 5.3 Delimitadores y valores especiales
9. Los delimitadores utilizados en el framing de identidades criptográficas **MUST NOT** poder aparecer como valores legítimos dentro de los campos que delimitan.
10. Los valores utilizados para representar ausencia o estados especiales en identidades criptográficas **MUST** formar un conjunto disjunto de los valores legítimos del dominio.
11. El conjunto de valores especiales (sentinels) **MUST** ser formalmente definido y documentado.
12. Los valores especiales **MUST NOT** colisionar con valores legítimos del dominio bajo ninguna circunstancia.

### 5.4 Trazabilidad y verificación
13. Los contratos de dominio **MUST** estar documentados en el modelo de dominio (tipos, validadores, docstrings).
14. La verificación del cumplimiento de los contratos de dominio **MUST** ser automatizable mediante tests unitarios o property-based testing.
15. Cualquier cambio en los contratos de dominio de campos criptográficos **MUST** ser tratado como un cambio de versión de esquema y requerir re-certificación de la baseline.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Los campos que participan en identidades criptográficas tienen contratos de dominio formalmente definidos y validados, eliminando ambigüedades y comportamientos indefinidos.
* La inyectividad del encoding está garantizada formalmente, previniendo colisiones en identidades criptográficas.
* La validación de dominio se aplica mediante fail-fast, cumpliendo el principio de Cero Fallos Silenciosos.
* Los valores especiales (sentinels) están formalmente definidos y garantizados como disjuntos de los valores legítimos.
* La trazabilidad de los contratos de dominio está documentada en el modelo de dominio, facilitando la mantenibilidad.
* Cualquier cambio en los contratos de dominio es tratado como cambio de versión de esquema, garantizando la integridad de la baseline.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Análisis estático que confirme que todo campo que participa en identidades criptográficas tiene validación de dominio en su construcción.
  * Verificación de que los delimitadores utilizados en el framing no pueden aparecer como valores legítimos en los campos que delimitan.
  * Verificación de que los valores especiales (sentinels) son disjuntos de los valores legítimos del dominio.
  * Análisis de tipos que confirme que las validaciones de dominio están presentes en los constructores de objetos de dominio.

* **Validation (dinámica/comportamental):**
  * Tests unitarios que verifiquen que la construcción de objetos de dominio con valores inválidos falla explícitamente (fail-fast).
  * Tests de propiedad (property-based testing) que verifiquen la inyectividad del encoding bajo múltiples combinaciones de valores de campos.
  * Tests de regresión que verifiquen que cambios en los contratos de dominio son detectados y requieren re-certificación.
  * Tests de integración que verifiquen que la baseline no puede ser corrompida por colisiones de identidades criptográficas.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio de Determinismo y Reproducibilidad (§5) y el Desacoplamiento de Identidades (§5). |
| `ADR_F17_BIS_03` | **Dependencia directa:** materializa la decisión arquitectónica de validación explícita de dominio (DC-04, DC-05). |
| `NADR-F17BIS-15` v2.0 | **Dependencia directa:** el linaje de identidad semántica consume los contratos de dominio aquí gobernados. |
| `NADR-F17BIS-16` | **Dependencia directa:** la semántica de las dimensiones de identidad consume los contratos de dominio aquí gobernados. |
| `HITO_3.2` | **Evidencia forense:** fundamenta DC-04 y DC-05. |
| `PHASE_17BIS_FASE3_EXECUTION_PLAN` | Las tareas de Fase 3 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la semántica de las dimensiones de identidad (responsabilidad de `NADR-F17BIS-16`).
* **No gobierna** el versionado implícito de `ASTSchemaVersion` (responsabilidad de `NADR-F17BIS-15` v2.0).
* **No gobierna** la fórmula de cálculo de los hashes (responsabilidad de `NADR-F17BIS-15` v2.0).
* **No gobierna** las invariantes de validez estructural del oráculo ni la completitud de la baseline (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** la evaluación topológica ni la semántica de regresión (responsabilidad de la Fase 4).
* **No prescribe** la implementación específica de la validación (regex, validadores de Pydantic, etc.) — eso queda gobernado por el Execution Plan.
* **No prescribe** la selección de algoritmos de hashing (SHA-256, BLAKE3, etc.) — eso queda gobernado por el Execution Plan.
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.