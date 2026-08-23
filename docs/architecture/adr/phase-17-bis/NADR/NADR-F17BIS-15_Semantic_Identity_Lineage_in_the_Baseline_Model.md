# NADR-F17BIS-15: Semantic Identity Lineage in the Baseline Model

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-15`
* **Título:** Linaje de la Identidad Semántica en el Modelo de Baseline
* **Clase de Decisión:** `DATA` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS (Fase 2 — Scientific Baseline Domain)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-013 (Semantic Identity Lineage in Baseline Model) — lugar ontológico de la identidad semántica y separación de dimensiones de identidad.
* **Evidencia Forense:** `E-2.0-02`, `E-2.0-10`, `E-2.0-11`, `E-2.0-13`, `GAP-2.0-05`, `GAP-2.0-06`, `OBS-2.0-01`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-03` (la firma semántica que viaja en la baseline), `NADR-F17BIS-12` (el oráculo sellado es el portador de la identidad).
  * **Influencia:** La Fase 3 (Identity & Trust Model), que construye el encadenamiento sobre esta ontología.
  * **Conflictúa con:** Todo colapso de la identidad semántica, la integridad del artefacto y la identidad física en un único mecanismo; todo linaje de sellado que omita la identidad semántica.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE
* **Operacional:** 5 — Con la identidad semántica huérfana, la firma de la baseline es ciega al contenido científico; las mutaciones de oráculos son indetectables.
* **Mantenibilidad:** 4 — La ambigüedad entre dimensiones de identidad impide evolucionar el modelo de linaje sin introducir colisiones.
* **Recuperabilidad:** 4 — Sin linaje semántico no es posible reconstruir ni verificar la identidad de un oráculo tras un fallo.
* **Seguridad:** 2 — El riesgo es de integridad de la baseline, no de superficie externa.
* **Financiero:** 3 — Un linaje inválido invalida cachés y fuerzas re-ejecuciones de certificación.
* **Total Score: 18/25**

**Severidad:** `S1`

---

## 3. DECISIÓN EJECUTIVA

**El oráculo sellado porta su identidad semántica como un linaje de primera clase dentro del modelo de baseline, y las dimensiones de identidad —semántica, integridad del artefacto, identidad física del documento fuente y versión de esquema— residen en lugares ontológicos diferenciados que no pueden colapsarse.**

En consecuencia:
* Queda prohibido tratar el hash de integridad de los bytes de un artefacto como la identidad semántica del oráculo.
* Queda prohibido colapsar la identidad semántica, la integridad del artefacto y la identidad física del documento fuente en un único campo o mecanismo.
* El linaje del sellado **MUST** incluir la identidad semántica del oráculo, no únicamente la integridad del artefacto.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de representar la identidad semántica del oráculo dentro del modelo de baseline está ausente. El linaje de sellado transporta únicamente la integridad de los bytes del artefacto, y las distintas dimensiones de identidad no están formalmente desacopladas. Se identifican las siguientes clases de defecto:

1. **Identidad semántica huérfana:** la firma semántica del AST no viaja en ningún modelo de la baseline.
2. **Colapso de dimensiones:** la integridad del artefacto se confunde con la identidad semántica del oráculo.
3. **Firma ciega al Ground Truth:** la firma del catálogo excluye el linaje de los oráculos, permitiendo mutaciones silenciosas.
4. **Versión de esquema ausente:** la versión del esquema del AST no está diferenciada en el modelo de identidad.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-2.0-10` / `GAP-2.0-05` (P0 — Crítico):** Ningún modelo, DTO, puerto o servicio de `core/benchmark/corpus` o `core/benchmark/ground_truth` referencia `compute_ast_hash`. Lo único que viaja es `ground_truth_sha256`, calculado como SHA-256 de los bytes del archivo (dimensión Integridad). Materializa DF-01-C.
* **`E-2.0-02` (P0 — Crítico):** `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` construye el payload a partir de `document_id`, `sha256`, `traits` y `page_count`, excluyendo `ground_truth_sha256` y cualquier identidad semántica. Verifica `E-0.2-003` de Fase 0.
* **`E-2.0-11` / `GAP-2.0-06` (P1 — Alto):** No existe representación de la versión de esquema del AST; el ADR Maestro §5 exige diferenciar AST Schema Version, Corpus Version e Identity Hash.
* **`E-2.0-13` (P1 — Alto):** `core/benchmark/corpus/models.py::DocumentFingerprint` porta un único campo `sha256`, mientras la firma del catálogo opera sobre cuatro campos, evidenciando un desacople entre el VO de identidad y la identidad firmada.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Linaje de identidad semántica
1. El oráculo sellado **MUST** portar su identidad semántica como parte de su linaje dentro del modelo de baseline.
2. El linaje del sellado **MUST** incluir la identidad semántica del oráculo, además de la integridad del artefacto.
3. La identidad semántica **MUST** corresponder a la firma semántica determinista del AST gobernada por el contrato canónico de hashing.

### 5.2 Separación de dimensiones de identidad
4. La identidad semántica, la integridad del artefacto, la identidad física del documento fuente y la versión de esquema **MUST** residir en lugares ontológicos diferenciados.
5. **MUST NOT** colapsarse dos o más dimensiones de identidad en un único campo o mecanismo.
6. El hash de integridad de los bytes de un artefacto **MUST NOT** ser utilizado como identidad semántica del oráculo.
7. La identidad física del documento fuente **MUST NOT** incorporar la identidad semántica del oráculo.

### 5.3 Diferenciación de versiones
8. La versión del esquema del AST, la versión del corpus y la identidad de la baseline **MUST** estar diferenciadas en el modelo de identidad.
9. La firma del catálogo **MUST** ser sensible al linaje de los oráculos; una mutación de un oráculo **MUST** alterar la firma resultante.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La identidad semántica del oráculo deviene un linaje de primera clase verificable dentro de la baseline.
* Las mutaciones de oráculos dejan de ser silenciosas: la firma del catálogo es sensible al contenido científico.
* Las dimensiones de identidad quedan formalmente desacopladas, habilitando el encadenamiento global de la Fase 3 sin colisiones.
* El precedente DF-01-D queda preservado: la identidad física y la identidad semántica permanecen ortogonales.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el modelo de baseline porta un campo de identidad semántica diferenciado de la integridad del artefacto.
  * Verificación de que la firma del catálogo incorpora el linaje de los oráculos.
  * Verificación de que la versión de esquema está representada y diferenciada.
* **Validation (dinámica/comportamental):**
  * Mutar el contenido semántico de un oráculo **MUST** alterar la firma del catálogo.
  * Reemplazar un oráculo por otro semánticamente idéntico pero con bytes distintos **MUST NOT** alterar la identidad semántica.
  * Verificar que dos documentos con idéntico PDF fuente pero distinto oráculo producen identidades de baseline distintas.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa la Separación de Conceptos Fundamentales (§3) y el Desacoplamiento de Identidades (§5). |
| `ADR_F17_BIS_02` | **Dependencia directa:** materializa el Principio de Separación de Identidades y responde DF-01-C declarado por el ADR de Fase. |
| `NADR-F17BIS-03` | **Dependencia directa:** la identidad semántica que viaja en la baseline es la firma semántica aquí gobernada. |
| `NADR-F17BIS-12` | **Dependencia directa:** el oráculo sellado es el portador de la identidad semántica. |
| `NADR-F17BIS-13` | **Relación:** un oráculo válido es precondición para portar identidad semántica. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas de Fase 2 materializan estas reglas; la Fase 3 construye el encadenamiento sobre esta ontología. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la fórmula de cálculo de la firma semántica del AST (responsabilidad de `NADR-F17BIS-03`).
* **No gobierna** el mecanismo de encadenamiento global $H_{baseline}$ ni su fórmula (responsabilidad de la Fase 3 — Identity & Trust Model).
* **No gobierna** los estados del ciclo de vida del oráculo (responsabilidad de `NADR-F17BIS-12`).
* **No gobierna** las invariantes de validez ni la completitud (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** la evaluación topológica ni la semántica de regresión (responsabilidad de la Fase 4).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.