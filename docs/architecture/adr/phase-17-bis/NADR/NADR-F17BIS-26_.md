# NADR-F17BIS-26: Canonical Baseline Materialization & Integrity

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-26`

* **Título:** Canonical Baseline Materialization & Integrity

* **Clase de Decisión:** `DATA / OPERATIONAL`

* **Nivel de Cumplimiento:** `MANDATORY`

* **Versión:** 1.0.0

* **Ciclo de Vida:** `FROZEN`

* **Vigente Desde:** Fase 6 (Continuous Verification)

* **Autoridad:** Architecture Board

* **Responsable Técnico:** Equipo de Arquitectura / Fase 6

* **Capacidad Arquitectónica:** CAP-2 (Canonical Baseline Consumption & Integrity) — Garantiza que Continuous Verification consuma exactamente la baseline canónica sellada por Phase 5, con integridad física, identidad verificable, completitud y protección contra sustitución o mutación durante la ejecución.

* **Evidencia Forense:** `E-6.2-001`, `E-6.2-002`, `E-6.2-003`, `E-6.2-004`, `E-6.2-005`, `E-6.2-006`, `E-6.2-007`, `E-6.3-003`, `GAP-6.2-01`, `GAP-6.2-02`, `GAP-6.2-03`, `GAP-6.2-06`, `GAP-6.2-07`, `GAP-6.3-03`, `DC-6.2`, `DC-6.10`, `DC-6.11`, `DC-6.14`

* **Referencias Cruzadas:**

  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-16` (Cryptographic Identity Semantics), `NADR-F17BIS-17` (Identity Encoding Integrity), `NADR-F17BIS-20` (Canonical Corpus Qualification), `NADR-F17BIS-21` (Ground Truth Eligibility, Migration & Sealing), `NADR-F17BIS-25` (Verification Boundary & Production Subject)

  * **Influencia:** `NADR-F17BIS-27` (Failure Semantics), `NADR-F17BIS-28` (Evidence & Identity Chain), `NADR-F17BIS-29` (Execution Profiles), `NADR-F17BIS-30` (CI Enforcement), `PHASE_17BIS_FASE6_EXECUTION_PLAN`

  * **Conflictúa con:** Cualquier práctica que sustituya la baseline canónica por fixtures legacy, corpus alternativos, artefactos no identificados, copias no verificadas o materiales modificados durante la ejecución de Continuous Verification.

  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Si la baseline no está materializada de forma determinista y verificable, el verification entry point puede ejecutarse contra un corpus inexistente, incompleto, sustituido o diferente del que fue sellado. La verificación deja de representar la referencia canónica. Evidencia: `E-6.2-001`, `GAP-6.2-01`, `GAP-6.2-02`.

* **Mantenibilidad:** 4 — Una materialización no gobernada permite que diferentes entornos utilicen representaciones físicas distintas de la misma baseline, dificultando la reproducibilidad y aumentando la divergencia entre ejecución local y CI. Evidencia: `GAP-6.2-06`, `GAP-6.2-07`.

* **Recuperabilidad:** 4 — La ausencia de integridad verificable dificulta distinguir una regresión real del production pipeline de una corrupción, sustitución o incompletitud de la baseline. Evidencia: `GAP-6.2-03`.

* **Seguridad:** 5 — Una baseline sustituible o mutable constituye una superficie de evasión del control de verificación: modificar la referencia puede alterar el resultado sin modificar el sujeto evaluado. Evidencia: `E-6.3-003`, `GAP-6.3-03`.

* **Financiero:** 2 — El costo operativo directo es moderado, pero una verificación realizada contra una baseline incorrecta puede producir ciclos de diagnóstico, retrabajo y ejecución innecesarios.

* **Total Score:** 20/25

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La Continuous Verification MUST consumir exactamente la baseline canónica sellada y MUST verificar su integridad, completitud e identidad física antes de utilizarla como referencia de evaluación.**

En consecuencia:

* La baseline consumida por Continuous Verification **MUST** corresponder al corpus canónico sellado definido por los contratos de Phase 5.

* Los artefactos de la baseline **MUST** ser materializados de forma determinista y verificable en el entorno de ejecución.

* La integridad física de los artefactos **MUST** ser verificada antes de iniciar la evaluación.

* La baseline **MUST NOT** ser modificada durante una ejecución de Continuous Verification.

* Una baseline ausente, incompleta, sustituida, inconsistente o cuya integridad no pueda demostrarse **MUST NOT** ser utilizada como referencia de verificación.

* Fixtures legacy, corpus auxiliares o artefactos sintéticos **MUST NOT** sustituir a la baseline canónica.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

Continuous Verification depende de una referencia física estable contra la cual comparar la salida del production pipeline.

La existencia lógica de una baseline sellada no garantiza por sí misma que dicha baseline esté disponible, completa, íntegra y correctamente identificada en el entorno donde se ejecuta la verificación.

La auditoría de Phase 6 identificó una separación entre:

1. **Baseline sellada:** referencia científica establecida por Phase 5.

2. **Materialización física:** artefactos que deben estar disponibles en el entorno de ejecución.

3. **Integridad:** demostración de que los artefactos materializados corresponden físicamente a los artefactos esperados.

4. **Consumo:** utilización de esos artefactos por el verification entry point.

La ausencia de esta cadena completa permite que Continuous Verification ejecute una evaluación contra una referencia diferente, incompleta o inexistente.

### 4.2 Manifestaciones concretas identificadas por la auditoría

* **`E-6.2-001` / `GAP-6.2-01` (P0 — Crítico):** 14 de 21 PDFs del corpus canónico no están trackeados en el repositorio (regla de exclusión en `.gitignore` sobre la ruta `tests/corpus/canonical/pdf/`). Un clonado estándar del repositorio no incluye estos PDFs. La baseline canónica utilizada durante Phase 5 no está materializada de forma suficiente en el entorno CI para garantizar su disponibilidad como referencia de Continuous Verification.

* **`E-6.2-002` / `GAP-6.2-02` (P0 — Crítico):** No existe mecanismo de materialización (artifact download, object storage, cache, self-hosted runner) para que CI acceda a los PDFs completos. La verificación forense exhaustiva confirma ausencia de archivos de configuración declarativa, workflows de materialización, o dependencias de gestión de artefactos.

* **`E-6.2-003` / `GAP-6.2-03` (P1 — Alto):** La ausencia de un PDF produce un fallo de infraestructura no tipado (crash del proveedor de extracción), no un error de dominio con mensaje indexable. El verification entry point (`tools/evaluation/run_regression.py`) no verifica la existencia de PDFs antes de intentar la extracción.

* **`E-6.2-004` / `DC-6.10` (P1 — Alto):** La existencia y validez de los artefactos PDF requeridos por la verificación deben poder comprobarse antes de ejecutar la evaluación.

* **`E-6.2-005` / `DC-6.11` (P1 — Alto):** La integridad física de los artefactos y del manifest debe poder verificarse mediante las identidades criptográficas establecidas por los contratos de baseline.

* **`GAP-6.2-06` (P1 — Alto):** El verification entry point (`tools/evaluation/run_regression.py`) no verifica el `manifest_hash` contra el manifest recalculado antes de ejecutar la verificación. Un manifest mutado no sería detectado.

* **`GAP-6.2-07` (P1 — Alto):** El verification entry point (`tools/evaluation/run_regression.py`) no verifica el `sha256` de cada PDF contra el valor declarado en el manifest antes de intentar la extracción. Un PDF sustituido no sería detectado.

* **`E-6.2-006` / `DC-6.14` (P1 — Alto):** La protección de la baseline en CI debe impedir que una modificación física de los artefactos pase inadvertida y sea interpretada como una referencia canónica válida.

* **`E-6.3-003` / `GAP-6.3-03` (P1 — Alto):** La infraestructura de CI verifica la inmutabilidad de una ruta legacy (`tests/fixtures/`) pero no de la ruta canónica de la baseline (`tests/corpus/canonical/`). Mutaciones a la baseline no serían detectadas por CI.

* **`E-6.2-007` (P2 — Medio):** La auditoría distingue entre los artefactos canónicos de la baseline (`tests/corpus/canonical/`) y los fixtures legacy existentes en el repositorio (`tests/fixtures/`). La existencia de estos últimos no demuestra que constituyan una representación válida de la baseline sellada.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Identidad y materialización de la baseline

1. La Continuous Verification **MUST** utilizar exclusivamente la baseline canónica cualificada y sellada bajo los contratos vigentes de Phase 5.

2. La baseline **MUST** estar físicamente materializada en el entorno de ejecución antes de iniciar la evaluación.

3. La materialización **MUST** conservar correspondencia verificable con los artefactos que constituyen la baseline canónica.

4. La presencia física de archivos con nombres, rutas o estructuras similares a las de la baseline **MUST NOT** considerarse evidencia suficiente de identidad.

5. La materialización **MUST NOT** sustituir, reconstruir o aproximar la baseline mediante fixtures legacy, corpus alternativos o artefactos sintéticos.

### 5.2 Integridad física

6. La integridad física de cada artefacto requerido por la baseline **MUST** ser verificable antes de su consumo.

7. La identidad criptográfica declarada por la baseline **MUST** corresponder a la identidad criptográfica observada en los artefactos materializados.

8. La integridad del manifest de la baseline **MUST** ser verificable antes de utilizarlo como fuente de referencia.

9. La verificación de integridad **MUST** abarcar, como mínimo, los artefactos cuya identidad física sea requerida por los contratos de baseline y su manifest.

10. Una discrepancia entre la identidad esperada y la identidad observada **MUST** impedir el consumo de la baseline como referencia de Continuous Verification.

### 5.3 Completitud y precondiciones de consumo

11. La baseline **MUST** satisfacer las precondiciones de completitud establecidas por sus contratos antes de iniciar la evaluación.

12. La ausencia de cualquiera de los artefactos obligatorios **MUST** impedir el consumo de la baseline.

13. Un artefacto ilegible, corrupto o físicamente inconsistente con su identidad declarada **MUST NOT** ser tratado como un artefacto válido de la baseline.

14. La verificación de precondiciones de la baseline **MUST** preceder a la evaluación topológica del production pipeline.

15. La evaluación topológica **MUST NOT** ejecutarse utilizando una baseline cuya integridad o completitud no haya sido demostrada.

### 5.4 Inmutabilidad durante la verificación

16. Los artefactos de la baseline **MUST** permanecer inmutables durante una ejecución de Continuous Verification.

17. El entorno de ejecución **MUST NOT** modificar los artefactos canónicos de la baseline como efecto de la verificación.

18. Una modificación detectada en la baseline durante la ejecución **MUST** invalidar su utilización como referencia.

19. La baseline consumida por una ejecución **MUST** ser la misma referencia física durante toda la evaluación correspondiente.

### 5.5 Separación entre baseline canónica y fixtures auxiliares

20. Los fixtures legacy, corpus sintéticos y artefactos auxiliares **MUST NOT** presentarse como sustitutos de la baseline canónica.

21. La existencia de fixtures auxiliares **MUST NOT** alterar la identidad ni las precondiciones de consumo de la baseline canónica.

22. Los artefactos auxiliares utilizados para pruebas internas **MUST** permanecer distinguibles de los artefactos que constituyen la referencia normativa de Continuous Verification.

### 5.6 Fallo de integridad de la referencia

23. La imposibilidad de demostrar la identidad, integridad o completitud de la baseline **MUST** impedir que dicha baseline sea utilizada como referencia válida.

24. Un fallo de integridad de la baseline **MUST** distinguirse semánticamente de una divergencia producida por el production pipeline.

25. La detección de un fallo de integridad de la baseline **MUST NOT** interpretarse como evidencia de una regresión científica del production pipeline.

### 5.7 Separación de identidades

26. La identidad de artefacto individual (identidad física de cada PDF, identidad semántica de cada Ground Truth) **MUST NOT** ser confundida con la identidad global de la baseline (identidad del manifest). Ningún artefacto individual **MUST** ser considerado sustituto de la identidad global de la baseline.

27. La materialización **MUST** preservar la cadena de identidad desde la identidad global de la baseline hasta cada artefacto individual, garantizando trazabilidad completa desde el manifest hasta cada artefacto del corpus.

28. La verificación de identidad **MUST** cubrir tanto la identidad global de la baseline (manifest) como la identidad individual de cada artefacto requerido, sin que una verificación sustituya a la otra.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Continuous Verification dispone de una referencia física determinista y verificable antes de iniciar la evaluación.

* La baseline canónica queda diferenciada de cualquier fixture legacy, corpus auxiliar o representación sintética.

* La integridad física de la referencia se convierte en una precondición explícita de la evaluación.

* Una divergencia entre la identidad esperada y la observada de la baseline no puede confundirse con una divergencia del production pipeline.

* La baseline permanece inmutable durante la ejecución de Continuous Verification.

* La materialización física de la baseline queda subordinada a los contratos de cualificación y sealing establecidos por `NADR-F17BIS-20` y `NADR-F17BIS-21`.

* La identidad de los artefactos físicos queda separada conceptualmente de la identity chain completa del resultado de verificación, cuya responsabilidad corresponde a `NADR-F17BIS-28`.

* La semántica final y los códigos operacionales asociados a un fallo de integridad quedan fuera de este NADR y son responsabilidad de `NADR-F17BIS-27`.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

### Verification (estática/mecánica)

* Inspección del corpus materializado para verificar que contiene los artefactos requeridos por la baseline canónica.

* Verificación de que los artefactos materializados poseen identidades físicas compatibles con el manifest y los contratos de baseline.

* Verificación de que el manifest utilizado por Continuous Verification corresponde a la baseline canónica esperada (verificación del manifest_hash).

* Inspección de CI para verificar que la baseline canónica no es sustituida por fixtures legacy o corpus alternativos.

* Verificación de que los artefactos de baseline son tratados como referencia de solo lectura durante la ejecución.

* Verificación de que la verificación de integridad cubre tanto la identidad global de la baseline como la identidad individual de cada artefacto.

### Validation (dinámica/comportamental)

* Ejecución de Continuous Verification con la baseline canónica físicamente materializada.

* Ejecución con un artefacto de baseline modificado (identidad criptográfica alterada), verificando que la discrepancia de integridad impide su consumo como referencia válida.

* Ejecución con un artefacto obligatorio ausente, verificando que la evaluación no continúa utilizando una baseline incompleta.

* Ejecución con un manifest mutado (manifest_hash incorrecto), verificando que la discrepancia de integridad del manifest impide su consumo como referencia válida.

* Ejecución con la baseline canónica intacta, verificando que la evaluación consume exactamente los artefactos esperados.

* Verificación de que un fallo de integridad de la baseline no se presenta como una divergencia científica del production pipeline.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto                          | Relación                                                                                                                                             |
| :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ADR_F17_BIS_MASTER`               | Este NADR materializa la capacidad de consumo continuo de la Scientific Baseline establecida por el ADR Maestro.                                     |
| `ADR_F17_BIS_06` v1.2.0            | Este NADR materializa D3 (Baseline como referencia inmutable), D5 (Baseline Materialization Contract) y parte de D8 (Baseline Integrity Protection). |
| `NADR-F17BIS-16`                   | **Dependencia directa:** NADR-16 gobierna las identidades criptográficas (Cryptographic Identity Semantics) que este NADR consume para la verificación de integridad de artefactos. |
| `NADR-F17BIS-17`                   | **Dependencia directa:** NADR-17 gobierna la integridad de codificación de identidad (Identity Encoding Integrity) que este NADR consume para la verificación de integridad de artefactos. |
| `NADR-F17BIS-20`                   | **Dependencia directa:** gobierna la cualificación del Canonical Corpus que constituye la referencia consumida por Continuous Verification.          |
| `NADR-F17BIS-21`                   | **Dependencia directa:** gobierna la elegibilidad, migración y sealing de la baseline cuya materialización es consumida por Continuous Verification. |
| `NADR-F17BIS-25`                   | **Influencia:** NADR-25 define el production pipeline como sujeto; este NADR define la baseline sellada como referencia de verificación. Ambos son necesarios para la Continuous Verification. |
| `NADR-F17BIS-27`                   | **Influencia:** define la semántica de los estados derivados de una baseline ausente, inválida o inconsistente.                                      |
| `NADR-F17BIS-28`                   | **Influencia:** utiliza la identidad física de la baseline como uno de los componentes de la identity chain persistida en la evidencia.              |
| `NADR-F17BIS-29`                   | **Influencia:** los perfiles de ejecución deben consumir la baseline canónica bajo las mismas reglas de integridad y materialización.                |
| `NADR-F17BIS-30`                   | **Influencia:** el enforcement de CI depende de que el resultado provenga de una ejecución realizada contra una baseline íntegra y canónica.         |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | Las tareas que materializan estas reglas son gobernadas por el Execution Plan de Fase 6.                                                             |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la cualificación científica del Canonical Corpus (responsabilidad de `NADR-F17BIS-20`).

* **No gobierna** la elegibilidad, migración, Ground Truth ni el sealing original de la baseline (responsabilidad de `NADR-F17BIS-21`).

* **No gobierna** la definición de identidades criptográficas ni el framing de hash (responsabilidad de `NADR-F17BIS-16` y `NADR-F17BIS-17`). Este NADR consume las identidades criptográficas; no las define.

* **No gobierna** el production pipeline ni el sujeto de verificación (responsabilidad de `NADR-F17BIS-25` y sus contratos de producción).

* **No gobierna** el mecanismo de evaluación topológica ni sus costos, labels, roots o políticas de regresión (responsabilidad de `NADR-F17BIS-19`).

* **No gobierna** la taxonomía de resultados, precedencia de fallos ni exit codes (responsabilidad de `NADR-F17BIS-27`).

* **No gobierna** la identity chain completa del resultado de verificación ni la persistencia integral de la evidencia de ejecución (responsabilidad de `NADR-F17BIS-28`). Este NADR gobierna la identidad física de la baseline materializada; NADR-28 gobierna la identidad del resultado de la verificación.

* **No gobierna** los perfiles de ejecución ni su frecuencia (responsabilidad de `NADR-F17BIS-29`).

* **No gobierna** el enforcement de merge protection ni la configuración externa de branch protection (responsabilidad de `NADR-F17BIS-30`).

* **No prescribe** el mecanismo específico de materialización (git tracking, artifact repository, object storage, self-hosted runner). La forma específica es definida por el Execution Plan conforme a las reglas de este NADR.

* **No prescribe** tareas de implementación ni Definition of Done; dichas responsabilidades pertenecen al Execution Plan de Fase 6.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.