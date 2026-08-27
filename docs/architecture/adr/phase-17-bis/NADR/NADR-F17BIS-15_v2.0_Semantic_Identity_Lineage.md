# NADR-F17BIS-15: Semantic Identity Lineage in the Baseline Model

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-15`
* **Título:** Linaje de la Identidad Semántica en el Modelo de Baseline
* **Clase de Decisión:** `DATA` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 2.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Phase 17-BIS (Fase 3 — Identity & Trust Model)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-013 (Semantic Identity Lineage in Baseline Model) — lugar ontológico de la identidad semántica, separación de dimensiones de identidad y versionado implícito de esquema AST.
* **Evidencia Forense:** `E-2.0-02`, `E-2.0-10`, `E-2.0-11`, `E-2.0-13`, `GAP-2.0-05`, `GAP-2.0-06`, `OBS-2.0-01`, `GAP-3.3-01` (HITO 3.3)
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-03` (la firma semántica que viaja en la baseline), `NADR-F17BIS-12` (el oráculo sellado es el portador de la identidad).
  * **Influencia:** La Fase 3 (Identity & Trust Model), que construye el encadenamiento sobre esta ontología.
  * **Conflictúa con:** Todo colapso de la identidad semántica, la integridad del artefacto y la identidad física en un único mecanismo; todo linaje de sellado que omita la identidad semántica; toda materialización explícita de `ASTSchemaVersion` como entidad separada.
  * **Reemplaza a:** `NADR-F17BIS-15` v1.0.0 (SUPERSEDED).

### Cambios respecto a v1.0

* **§5.3 R8:** Eliminada la mención a "versión del esquema del AST" como dimensión diferenciada explícita. Ahora gobernada por §5.3 R10 (versionado implícito).
* **§5.3 R10:** Nueva regla que establece el versionado implícito de esquema AST mediante acoplamiento a `CorpusVersion`.
* **§3 (Decisión Ejecutiva):** Agregada prohibición de materializar `ASTSchemaVersion` como entidad separada.
* **§4.2:** Agregada evidencia `GAP-3.3-01` (HITO 3.3) sobre alucinación documental.
* **§2 (Architecture Risk Score):** Justificación explícita de la disminución de 18/25 a 17/25.

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin ontología ni ciclo de vida gobernado, una operación de curaduría puede sobrescribir un oráculo sellado sin que el dominio lo detecte, corrompiendo la línea base contra la cual se certifica el sistema.
* **Mantenibilidad:** 4 — La ausencia de estados formales impide razonar sobre la verdad científica; el "sello" se deduce de datos incidentales, acoplando a los consumidores a una convención frágil.
* **Recuperabilidad:** 4 — Sin estado explícito no es posible distinguir un borrador de un oráculo durante la recuperación ni auditar transiciones ilegales.
* **Seguridad:** 2 — La exposición se limita a la integridad del artefacto de baseline, no a superficie de red.
* **Financiero:** 2 — Una baseline corrupta fuerza re-ejecuciones de certificación, pero el impacto es acotado al laboratorio.
* **Total Score: 17/25**

**Severidad:** `S1`

**Justificación de la disminución de 18/25 (v1.0) a 17/25 (v2.0):** El Architecture Risk Score disminuyó en 1 punto debido a la eliminación de la alucinación documental de `ASTSchemaVersion` (GAP-3.3-01, HITO 3.3). La v1.0 exigía diferenciación explícita de `ASTSchemaVersion` como entidad separada, lo que generaba una discrepancia entre la documentación normativa y el runtime real, incrementando el riesgo de confusión en implementadores. La v2.0 alinea la documentación con el runtime mediante el versionado implícito, reduciendo este riesgo.

---

## 3. DECISIÓN EJECUTIVA

**El oráculo sellado porta su identidad semántica como un linaje de primera clase dentro del modelo de baseline, y las dimensiones de identidad —semántica, integridad del artefacto, identidad física del documento fuente y versión de corpus— residen en lugares ontológicos diferenciados que no pueden colapsarse. La versión del esquema AST está implícitamente acoplada a la versión del corpus y al release del software, por lo que no se requiere un campo de identidad separado en el modelo de dominio.**

En consecuencia:
* Queda prohibido tratar el hash de integridad de los bytes de un artefacto como la identidad semántica del oráculo.
* Queda prohibido colapsar la identidad semántica, la integridad del artefacto y la identidad física del documento fuente en un único campo o mecanismo.
* El linaje del sellado **MUST** incluir la identidad semántica del oráculo, no únicamente la integridad del artefacto.
* Queda prohibido materializar la versión del esquema AST como entidad, campo o constante separada en el modelo de identidad, dado que está implícitamente acoplada a la versión del corpus.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La v1.0 estableció correctamente la identidad semántica del oráculo (`oracle_hash`) y su inclusión en el linaje de la baseline. Sin embargo, la v1.0 exigía la diferenciación explícita de `ASTSchemaVersion` como entidad separada, lo que generaba una discrepancia entre la documentación normativa y el runtime real (GAP-3.3-01, HITO 3.3).

Se identifican las siguientes clases de defecto:

1. **Identidad semántica huérfana (resuelto en v1.0):** la firma semántica del AST no viajaba en ningún modelo de la baseline.
2. **Colapso de dimensiones (resuelto en v1.0):** la integridad del artefacto se confundía con la identidad semántica del oráculo.
3. **Firma ciega al Ground Truth (resuelto en v1.0):** la firma del catálogo excluía el linaje de los oráculos, permitiendo mutaciones silenciosas.
4. **Alucinación documental de ASTSchemaVersion (resuelto en v2.0):** la v1.0 exigía diferenciación explícita de la versión de esquema AST, pero el runtime no la materializaba, generando una discrepancia entre documentación e implementación.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-2.0-10` / `GAP-2.0-05` (P0 — Crítico):** Ningún modelo, DTO, puerto o servicio de `core/benchmark/corpus` o `core/benchmark/ground_truth` referenciaba `compute_ast_hash`. Lo único que viajaba era `ground_truth_sha256`, calculado como SHA-256 de los bytes del archivo (dimensión Integridad).

* **`E-2.0-02` (P0 — Crítico):** `core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash` construía el payload a partir de `document_id`, `sha256`, `traits` y `page_count`, excluyendo `ground_truth_sha256` y cualquier identidad semántica.

* **`E-2.0-11` / `GAP-2.0-06` (P1 — Alto):** No existía representación de la versión de esquema del AST; el ADR Maestro §5 exigía diferenciar AST Schema Version, Corpus Version e Identity Hash.

* **`GAP-3.3-01` (P2 — Medio, HITO 3.3):** La v1.0 declaraba DONE la diferenciación de `ASTSchemaVersion`, pero el runtime no contenía ninguna entidad, campo o constante que la representara. El análisis de impacto práctico demostró que este riesgo es teórico y mitigado por el acoplamiento implícito a `CorpusVersion`.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Linaje de identidad semántica
1. El oráculo sellado **MUST** portar su identidad semántica como parte de su linaje dentro del modelo de baseline.
2. El linaje del sellado **MUST** incluir la identidad semántica del oráculo, además de la integridad del artefacto.
3. La identidad semántica **MUST** corresponder a la firma semántica determinista del AST gobernada por el contrato canónico de hashing.

### 5.2 Separación de dimensiones de identidad
4. La identidad semántica, la integridad del artefacto, la identidad física del documento fuente y la versión de corpus **MUST** residir en lugares ontológicos diferenciados.
5. **MUST NOT** colapsarse dos o más dimensiones de identidad en un único campo o mecanismo.
6. El hash de integridad de los bytes de un artefacto **MUST NOT** ser utilizado como identidad semántica del oráculo.
7. La identidad física del documento fuente **MUST NOT** incorporar la identidad semántica del oráculo.

### 5.3 Diferenciación de versiones y versionado implícito de esquema AST
8. La versión del corpus y la identidad de la baseline **MUST** estar diferenciadas en el modelo de identidad.[^1]
9. La firma del catálogo **MUST** ser sensible al linaje de los oráculos; una mutación de un oráculo **MUST** alterar la firma resultante.
10. La versión del esquema AST **MUST** estar implícitamente acoplada a la versión del corpus, de tal forma que cualquier cambio en el esquema AST requiera la generación de una nueva versión de corpus.

[^1]: **Nota:** La mención a "versión del esquema del AST" fue eliminada en v2.0 porque ahora está gobernada por R10 (versionado implícito).

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La identidad semántica del oráculo deviene un linaje de primera clase verificable dentro de la baseline.
* Las mutaciones de oráculos dejan de ser silenciosas: la firma del catálogo es sensible al contenido científico.
* Las dimensiones de identidad quedan formalmente desacopladas, habilitando el encadenamiento global de la Fase 3 sin colisiones.
* La versión del esquema AST queda implícitamente acoplada a la versión del corpus, eliminando la alucinación documental y alineando la documentación con el runtime.
* Se elimina la necesidad de un campo separado para `ASTSchemaVersion`, simplificando el modelo de identidad y cumpliendo YAGNI.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el modelo de baseline porta un campo de identidad semántica diferenciado de la integridad del artefacto.
  * Verificación de que la firma del catálogo incorpora el linaje de los oráculos.
  * Verificación de que NO existe entidad, campo ni constante separada para `ASTSchemaVersion` en el modelo de identidad.
  * Verificación de que cualquier modificación en `ContentNodeType` (adición, deprecación o cambio de semántica) obliga a incrementar la versión del corpus en el manifiesto.

* **Validation (dinámica/comportamental):**
  * Mutar el contenido semántico de un oráculo **MUST** alterar la firma del catálogo.
  * Reemplazar un oráculo por otro semánticamente idéntico pero con bytes distintos **MUST NOT** alterar la identidad semántica.
  * Verificar que dos documentos con idéntico PDF fuente pero distinto oráculo producen identidades de baseline distintas.
  * Verificar que un cambio de esquema AST (sin cambio de corpus) no es posible sin generar una nueva versión de corpus.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa la Separación de Conceptos Fundamentales (§3) y el Desacoplamiento de Identidades (§5). |
| `ADR_F17_BIS_03` | **Dependencia directa:** materializa el Principio de Versionado Implícito de Esquema AST declarado por el ADR de Fase 3. |
| `NADR-F17BIS-03` | **Dependencia directa:** la identidad semántica que viaja en la baseline es la firma semántica aquí gobernada. |
| `NADR-F17BIS-12` | **Dependencia directa:** el oráculo sellado es el portador de la identidad semántica. |
| `NADR-F17BIS-13` | **Relación:** un oráculo válido es precondición para portar identidad semántica. |
| `PHASE_17BIS_FASE3_EXECUTION_PLAN` | Las tareas de Fase 3 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la fórmula de cálculo de la firma semántica del AST (responsabilidad de `NADR-F17BIS-03`).
* **No gobierna** el mecanismo de encadenamiento global $H_{baseline}$ ni su fórmula (responsabilidad de la Fase 3 — Identity & Trust Model).
* **No gobierna** los estados del ciclo de vida del oráculo (responsabilidad de `NADR-F17BIS-12`).
* **No gobierna** las invariantes de validez ni la completitud (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** la evaluación topológica ni la semántica de regresión (responsabilidad de la Fase 4).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento superseedea a `NADR-F17BIS-15` v1.0.0. La v2.0 modifica §5.3 R8 y agrega §5.3 R10 para establecer el versionado implícito de esquema AST, preservando las otras 8 reglas de la v1.0. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.