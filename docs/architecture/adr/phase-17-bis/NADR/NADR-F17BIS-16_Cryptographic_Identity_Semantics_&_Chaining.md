# NADR-F17BIS-16: Cryptographic Identity Semantics in the Baseline

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-16`
* **Título:** Semántica de Identidad Criptográfica en la Baseline
* **Clase de Decisión:** `DATA` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Phase 17-BIS (Fase 3 — Identity & Trust Model)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-016 (Cryptographic Identity Semantics in Baseline) — definición de la semántica de las dimensiones de identidad que participan en la baseline y coexistencia de contratos de hashing semántico.
* **Evidencia Forense:** `E-3.1-006`, `E-3.1-008`, `E-3.1-016`, `E-3.1-022`, `GAP-3.1-01`, `DC-01` (HITO 3.1), `DC-03` (HITO 3.1)
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-03` (firma semántica del AST), `NADR-F17BIS-12` (ontología del oráculo), `NADR-F17BIS-15` v2.0 (linaje de identidad semántica).
  * **Influencia:** `NADR-F17BIS-17` (integridad del encoding), Fase 4 (Scientific Verification).
  * **Conflictúa con:** Todo mecanismo que colapse la semántica de `ground_truth_state` con identidad científica del contenido; toda ambigüedad sobre qué contrato de hashing representa la identidad canónica del oráculo para el linaje de baseline.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin semántica clara de las dimensiones de identidad, los consumidores de la baseline no pueden determinar qué mutaciones invalidan el sello y cuáles no, generando corrupción silenciosa.
* **Mantenibilidad:** 4 — La coexistencia de múltiples contratos de hashing sin justificación arquitectónica explícita impide evolucionar el modelo de identidad sin introducir ambigüedades.
* **Recuperabilidad:** 4 — Sin semántica de `ground_truth_state` claramente definida, no es posible auditar transiciones de ciclo de vida ni detectar des-sellados silenciosos.
* **Seguridad:** 2 — La exposición se limita a la integridad de la baseline, no a superficie de red.
* **Financiero:** 3 — Una baseline con semántica ambigua invalida campañas de certificación y fuerza re-ejecuciones.
* **Total Score: 18/25**

**Severidad:** `S1`

---

## 3. DECISIÓN EJECUTIVA

**Las dimensiones de identidad que participan en la baseline poseen semánticas distintas y complementarias: la identidad semántica del oráculo captura el contenido científico, el estado de ciclo de vida captura el proceso de certificación, y la identidad física captura la integridad del artefacto. La coexistencia de múltiples contratos de hashing semántico es legítima cuando cada contrato sirve a un propósito arquitectónico distinto y está formalmente gobernado.**

En consecuencia:
* Queda prohibido colapsar la semántica de estado de ciclo de vida con la semántica de identidad científica del contenido.
* Queda prohibido utilizar un único contrato de hashing semántico para propósitos arquitectónicos distintos sin justificación explícita.
* Toda dimensión de identidad que participa en la baseline **MUST** tener una semántica formalmente definida y verificable.
* La inclusión de una dimensión de estado en la identidad global **MUST** estar justificada por su rol en la protección del proceso de certificación, no por su rol en la representación del contenido científico.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de definir formalmente la semántica de las dimensiones de identidad que participan en la baseline estaba ausente. La auditoría forense de Fase 3.0 identificó dos clases de defecto:

1. **Ambigüedad entre contratos de hashing semántico:** Coexisten dos mecanismos de hashing semántico con propósitos distintos pero sin justificación arquitectónica explícita. El primero excluye la identidad de nodo; el segundo la incluye. NADR-15 §5.1 R3 exige que la identidad semántica corresponda a "la firma semántica determinista del AST gobernada por el contrato canónico de hashing", lo que genera tensión interpretativa. Esta tensión se resuelve estableciendo que para el linaje de baseline, el contrato canónico es `OracleSemanticIdentityCalculator`, mientras que para otros propósitos (comparación de parsers, evaluación topológica), pueden existir contratos alternativos gobernados por este NADR.

2. **Semántica de estado de ciclo de vida no definida:** El estado de ciclo de vida del oráculo se incluye en la identidad global de la baseline, pero no está formalmente definido si representa identidad científica del contenido o estado operacional del proceso de certificación. La justificación de su inclusión es: (1) garantiza que un oráculo no pueda ser 'des-sellado' silenciosamente, (2) protege la integridad del proceso de certificación, y (3) cualquier cambio de estado invalida el sello y requiere re-certificación.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-3.1-006` / `DC-01` (P1 — Alto):** Dos contratos de hashing semántico coexisten: uno que excluye `node_id` (utilizado para comparación de parsers) y otro que lo incluye (utilizado para linaje de baseline). NADR-15 §5.1 R3 no clarifica cuál es la identidad canónica del oráculo.

* **`E-3.1-022` / `DC-03` (P1 — Alto):** El estado de ciclo de vida se incluye en la identidad global de la baseline. La transición de estado invalida el sello, pero no está definido si esto se debe a que el estado es identidad científica o porque protege el proceso de certificación.

* **`E-3.1-016` (P2 — Medio):** El contrato de hashing que incluye `node_id` es sensible a mutaciones de identidad de nodo sin cambiar contenido científico. Esto es correcto para linaje de baseline, pero genera confusión sobre qué representa la identidad semántica.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Semántica de identidad semántica del oráculo
1. La identidad semántica del oráculo **MUST** capturar las dimensiones científicamente relevantes del oráculo que permitan distinguir mutaciones de contenido científico.
2. La identidad semántica del oráculo **MUST** ser sensible a mutaciones de contenido científico.
3. La identidad semántica del oráculo **MUST NOT** ser sensible a metadata física incidental (coordenadas, páginas, confianza).

### 5.2 Coexistencia de contratos de hashing semántico
4. **MAY** coexistir múltiples contratos de hashing semántico cuando cada contrato sirve a un propósito arquitectónico distinto.
5. Todo contrato de hashing semántico **MUST** tener un propósito arquitectónico formalmente definido y documentado.
6. Todo contrato de hashing semántico **MUST** especificar explícitamente qué dimensiones de identidad incluye y excluye.
7. Todo contrato de hashing semántico **MUST** ser determinista y reproducible.
8. Para el linaje de baseline, el contrato canónico de hashing semántico es aquel que incluye la identidad de nodo como dimensión de identidad. Para otros propósitos (comparación de parsers, evaluación topológica), **MAY** utilizarse contratos alternativos que excluyan la identidad de nodo.

### 5.3 Semántica de estado de ciclo de vida
9. El estado de ciclo de vida del oráculo **MUST** representar el proceso de certificación, no el contenido científico del oráculo.
10. La inclusión del estado de ciclo de vida en la identidad global de la baseline **MUST** estar justificada por su rol en la protección del proceso de certificación. La justificación es: (1) garantiza que un oráculo no pueda ser 'des-sellado' silenciosamente, (2) protege la integridad del proceso de certificación, y (3) cualquier cambio de estado invalida el sello y requiere re-certificación.
11. La transición de estado de ciclo de vida **MUST** invalidar la identidad global de la baseline y requerir re-certificación.
12. El estado de ciclo de vida **MUST NOT** ser tratado como identidad científica del contenido del oráculo.

### 5.4 Composición de la identidad global de la baseline
13. La identidad global de la baseline **MUST** encadenar todas las dimensiones de identidad relevantes: identidad física, identidad semántica, estado de ciclo de vida y versión de corpus.[^1]
14. La identidad global de la baseline **MUST** ser sensible a mutaciones de cualquiera de sus dimensiones constituyentes.
15. La identidad global de la baseline **MUST** ser recomputable deterministamente a partir de las dimensiones constituyentes.
16. La identidad global de la baseline **MUST NOT** colapsar dimensiones con semánticas distintas en un único campo o mecanismo.

[^1]: **Nota:** La versión del esquema AST está implícitamente acoplada a la versión del corpus (ver `NADR-F17BIS-15` v2.0 §5.3 R10), por lo que no se requiere un campo separado en la identidad global.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La semántica de las dimensiones de identidad que participan en la baseline queda formalmente definida y verificable.
* La coexistencia de contratos de hashing semántico queda justificada arquitectónicamente, eliminando ambigüedades normativas.
* El estado de ciclo de vida queda claramente diferenciado de la identidad científica del contenido, permitiendo auditoría precisa de transiciones.
* Los consumidores de la baseline pueden determinar qué mutaciones invalidan el sello y cuáles no, basándose en semánticas formalmente definidas.
* La identidad global de la baseline queda protegida contra des-sellados silenciosos mediante la inclusión del estado de ciclo de vida.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que todo contrato de hashing semántico tiene documentación explícita de su propósito arquitectónico y dimensiones incluidas/excluidas.
  * Verificación de que el estado de ciclo de vida no se trata como identidad científica del contenido en ningún consumidor de la baseline.
  * Verificación de que la identidad global de la baseline incluye todas las dimensiones requeridas.
  * Análisis de tipos que confirme la separación semántica entre estado de ciclo de vida e identidad de contenido.

* **Validation (dinámica/comportamental):**
  * Mutar el contenido científico de un oráculo **MUST** alterar la identidad semántica del oráculo.
  * Mutar la identidad de nodo sin cambiar contenido científico **MUST** alterar la identidad semántica del oráculo utilizada para linaje de baseline.
  * Mutar metadata física incidental **MUST NOT** alterar la identidad semántica del oráculo.
  * Transicionar el estado de ciclo de vida **MUST** alterar la identidad global de la baseline.
  * Recomputar la identidad global de la baseline a partir de las mismas dimensiones constituyentes **MUST** producir el mismo hash.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa la Separación de Conceptos Fundamentales (§3) y el Desacoplamiento de Identidades (§5). |
| `ADR_F17_BIS_03` | **Dependencia directa:** materializa la decisión arquitectónica de semántica de dimensiones de identidad en la baseline. |
| `NADR-F17BIS-03` | **Dependencia directa:** la firma semántica del AST es consumida por los contratos de hashing semántico aquí gobernados. |
| `NADR-F17BIS-12` | **Dependencia directa:** la ontología del oráculo define el estado de ciclo de vida aquí gobernado. |
| `NADR-F17BIS-15` v2.0 | **Dependencia directa:** el linaje de identidad semántica es el contexto en el que operan los contratos aquí gobernados. |
| `NADR-F17BIS-17` | **Influencia:** la integridad del encoding garantiza que las dimensiones aquí gobernadas se serialicen sin colisiones. |
| `PHASE_17BIS_FASE3_EXECUTION_PLAN` | Las tareas de Fase 3 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la fórmula de cálculo de la firma semántica del AST (responsabilidad de `NADR-F17BIS-03`).
* **No gobierna** el mecanismo de encadenamiento global de la baseline ni su fórmula (responsabilidad de `NADR-F17BIS-15` v2.0), pero sí gobierna la semántica de las dimensiones que participan en dicho encadenamiento.
* **No gobierna** los estados del ciclo de vida del oráculo ni sus transiciones (responsabilidad de `NADR-F17BIS-12`).
* **No gobierna** las invariantes de validez ni la completitud (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** la integridad del encoding de las dimensiones de identidad (responsabilidad de `NADR-F17BIS-17`).
* **No gobierna** la evaluación topológica ni la semántica de regresión (responsabilidad de la Fase 4).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.