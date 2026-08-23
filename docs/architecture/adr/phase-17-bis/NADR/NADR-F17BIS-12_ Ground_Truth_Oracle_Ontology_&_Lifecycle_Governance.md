# NADR-F17BIS-12: Ground Truth Oracle Ontology & Lifecycle Governance

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-12`
* **Título:** Ontología del Oráculo de Ground Truth y Gobierno de su Ciclo de Vida
* **Clase de Decisión:** `DATA` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS (Fase 2 — Scientific Baseline Domain)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-010 (Ground Truth Oracle Ontology & Lifecycle) — existencia formal, disyunción y transiciones gobernadas de la verdad científica.
* **Evidencia Forense:** `E-2.0-04`, `E-2.0-10`, `E-2.0-12`, `GAP-2.0-01`, `GAP-2.0-02`, `OBS-2.0-05`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-01` (el oráculo se hidrata sobre la representación canónica del AST).
  * **Influencia:** `NADR-F17BIS-13` (la completitud opera sobre entidades con estado), `NADR-F17BIS-14` (la autoridad de sellado gobierna estas transiciones), `NADR-F17BIS-15` (el oráculo sellado porta la identidad semántica).
  * **Conflictúa con:** Toda inferencia de estado de sellado a partir de la presencia o el contenido de un artefacto serializado; toda mutación in-place de una entidad de ciclo de vida.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE
* **Operacional:** 5 — Sin ontología ni ciclo de vida gobernado, una operación de curaduría puede sobrescribir un oráculo sellado sin que el dominio lo detecte, corrompiendo la línea base contra la cual se certifica el sistema.
* **Mantenibilidad:** 4 — La ausencia de estados formales impide razonar sobre la verdad científica; el "sello" se deduce de datos incidentales, acoplando a los consumidores a una convención frágil.
* **Recuperabilidad:** 3 — Sin estado explícito no es posible distinguir un borrador de un oráculo durante la recuperación ni auditar transiciones ilegales.
* **Seguridad:** 2 — La exposición se limita a la integridad del artefacto de baseline, no a superficie de red.
* **Financiero:** 2 — Una baseline corrupta fuerza re-ejecuciones de certificación, pero el impacto es acotado al laboratorio.
* **Total Score: 16/25**

**Severidad:** `S1`

---

## 3. DECISIÓN EJECUTIVA

**La verdad científica del sistema existe como una entidad de dominio cuyo tipo y estado están determinados por un ciclo de vida formal y gobernado, en el que el borrador curado y el oráculo sellado son tipos disjuntos, y ninguna transición de estado puede inferirse de un artefacto ni ejecutarse fuera de la autoridad designada.**

En consecuencia:
* Queda prohibido tratar un artefacto serializado en disco como un oráculo por el mero hecho de existir.
* Queda prohibido deducir el estado de un Ground Truth a partir de la presencia de un archivo o de un campo incidental.
* Toda transición del ciclo de vida produce una nueva instancia inmutable; ninguna entidad de ciclo de vida es mutada en el lugar.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de representar la verdad científica como un objeto de dominio con estado formal está ausente. El sistema no distingue un borrador de un oráculo, y el estado de sello se reduce a la existencia de un artefacto o a un dato opcional. Se identifican las siguientes clases de defecto:

1. **Orfandad ontológica:** no existe una entidad que represente el oráculo como verdad certificada; la "verdad" es indistinguible de su representación serializada.
2. **Ausencia de gobierno de transiciones:** no hay estados formales ni autoridad que los gobierne; el paso de borrador a sellado es un efecto lateral no regulado.
3. **Inferencia de estado:** el sello se deduce de datos incidentales, violando el principio de no-inferencia y haciendo imposible detectar transiciones ilegales.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-2.0-04` / `GAP-2.0-02` (P0 — Crítico):** `core/benchmark/corpus/dtos.py::RawDocumentEntryDTO` modela el estado del Ground Truth mediante `ground_truth_version: Optional[str]` y `ground_truth_sha256: Optional[str]`. No existe ningún tipo de estado `Draft/Audited/Validated/Sealed`; el sello se infiere de la presencia de un string no nulo.
* **`E-2.0-12` (P0 — Crítico):** `infra/fs/ground_truth_store.py::LocalFileSystemGroundTruthDraftWriter.save_draft_ast` escribe en la misma ruta que `LocalFileSystemGroundTruthReader.load_ground_truth`. Un borrador puede sobrescribir un oráculo sellado sin guardia, porque el escritor no consulta estado alguno.
* **`E-2.0-10` / `GAP-2.0-01` (P0 — Crítico):** Ningún modelo, puerto o servicio de `core/benchmark/ground_truth` representa el oráculo como entidad de dominio; el camino de lectura devuelve una secuencia cruda de nodos sin envoltorio de estado ni de validez.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Existencia ontológica del oráculo
1. El Ground Truth **MUST** ser modelado como una entidad de dominio cuyo tipo está determinado por su estado dentro del ciclo de vida.
2. El estado de borrador curado y el estado de oráculo sellado **MUST** estar representados como tipos disjuntos que no pueden confundirse ni convertirse implícitamente entre sí.
3. Un artefacto serializado **MUST NOT** ser tratado como oráculo por el hecho de existir; su consideración como verdad científica **MUST** requerir hidratación y validación previas mediante el contrato canónico.

### 5.2 Ciclo de vida y no-inferencia de estado
4. El ciclo de vida del Ground Truth **MUST** definir explícitamente los estados de borrador, auditado, validado y sellado, y las únicas transiciones permitidas entre ellos.
5. El estado de un Ground Truth **MUST NOT** ser inferido de la presencia de un archivo, del contenido de un artefacto ni de un campo de datos incidental.
6. Toda transición de estado **MUST** ser producida por una operación explícita y gobernada, nunca como efecto lateral de una operación de lectura o de escritura de artefactos.

### 5.3 Inmutabilidad y reemplazo
7. Toda entidad del ciclo de vida **MUST** ser inmutable; una transición **MUST** producir una nueva instancia en lugar de alterar la instancia origen.
8. Un borrador **MAY** ser descartado y sustituido por una nueva instancia de borrador durante la curaduría; un borrador **MUST NOT** ser mutado en el lugar.
9. Un oráculo sellado **MUST NOT** ser alterado ni sobrescrito por ninguna operación de curaduría.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El oráculo sellado deviene una entidad de dominio distinguible de su borrador y de su representación serializada.
* El estado de un Ground Truth es explícito y auditable; las transiciones ilegales son detectables y rechazables.
* La curaduría pierde la capacidad de corromper un oráculo sellado, eliminando el riesgo de corrupción de la línea base.
* Los consumidores de la baseline pueden consultar el estado de un oráculo sin depender de convenciones incidentales.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Análisis de tipos que confirme la disyunción entre los tipos de borrador y de oráculo sellado.
  * Verificación de inmutabilidad: las entidades del ciclo de vida son estructuras congeladas sin asignación mutativa.
  * Verificación estática de que ningún consumidor infiere el estado de sellado a partir de la presencia de un artefacto.
* **Validation (dinámica/comportamental):**
  * Intentar sobrescribir un oráculo sellado mediante una operación de curaduría **MUST** ser rechazado por el dominio.
  * Recorrer el ciclo de vida completo y verificar que cada transición produce una nueva instancia y que las transiciones ilegales son abortadas.
  * Verificar que un Ground Truth sin artefacto asociado no es reportado como sellado.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio constitucional de separación de conceptos y el invariante de identidad de la baseline. |
| `ADR_F17_BIS_02` | **Dependencia directa:** materializa el Principio de Disyunción Ontológica y el Principio de No-Inferencia de Estado declarados por el ADR de Fase. |
| `NADR-F17BIS-01` | **Dependencia directa:** el oráculo se hidrata sobre la representación canónica del AST. |
| `NADR-F17BIS-13` | **Influencia:** la completitud y la validez operan sobre entidades que ya poseen estado formal. |
| `NADR-F17BIS-14` | **Influencia:** la autoridad de sellado es quien gobierna las transiciones aquí definidas. |
| `NADR-F17BIS-15` | **Influencia:** el oráculo sellado es el portador de la identidad semántica. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas de Fase 2 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** las invariantes estructurales que definen la validez de un oráculo ni la completitud de la baseline (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** la segregación de superficies de acceso ni la autoridad única de sellado (responsabilidad de `NADR-F17BIS-14`).
* **No gobierna** las identidades que porta el oráculo ni su separación (responsabilidad de `NADR-F17BIS-15`).
* **No gobierna** la fórmula de la firma semántica del AST (responsabilidad de `NADR-F17BIS-03`).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.