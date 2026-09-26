# NADR-F17BIS-28: Evidence, Identity Chain & Reproducibility

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-28`

* **Título:** Evidence, Identity Chain & Reproducibility

* **Clase de Decisión:** `DATA / GOVERNANCE`

* **Nivel de Cumplimiento:** `MANDATORY`

* **Versión:** 1.0.0

* **Ciclo de Vida:** `FROZEN`

* **Fecha de Congelamiento:** 2026-09-25

* **Vigente Desde:** Fase 6 (Continuous Verification)

* **Autoridad:** Architecture Board

* **Responsable Técnico:** Equipo de Arquitectura / Fase 6

* **Capacidad Arquitectónica:** CAP-10 (Evidence Persistence & Reproducibility) — Garantiza que cada ejecución de Continuous Verification produzca evidencia determinista, persistente y reconstruible, vinculando inequívocamente sujeto, referencia, configuración, parámetros, evaluación y resultado mediante una identity chain completa.

* **Evidencia Forense:** `E-6.1-001`, `E-6.1-002`, `E-6.2-006`, `E-6.2-007`, `E-6.2-008`, `E-6.2-010`, `E-6.3-002`, `E-6.3-012`, `GAP-6.2-02`, `GAP-6.2-06`, `GAP-6.2-07`, `GAP-6.3-02`, `GAP-6.3-06`, `DC-6.11`, `DC-6.13`

* **Referencias Cruzadas:**

  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-16` (Cryptographic Identity Semantics), `NADR-F17BIS-17` (Identity Encoding Integrity), `NADR-F17BIS-19` (Regresión Topológica Graduada), `NADR-F17BIS-21` (Ground Truth Eligibility, Migration & Sealing), `NADR-F17BIS-25` (Verification Boundary & Production Subject), `NADR-F17BIS-26` (Canonical Baseline Materialization & Integrity), `NADR-F17BIS-27` (Verification Outcome & Failure Semantics)

  * **Influencia:** `NADR-F17BIS-29` (Execution Profiles), `NADR-F17BIS-30` (CI Enforcement), `PHASE_17BIS_FASE6_EXECUTION_PLAN`

  * **Conflictúa con:** Cualquier práctica que produzca resultados de Continuous Verification sin evidencia persistente suficiente para reconstruir la ejecución, que permita desacoplar el resultado de las identidades de sus entradas, que sobrescriba evidencia de ejecuciones anteriores de forma que destruya su trazabilidad, o que trate la coincidencia de un resultado numérico como demostración de equivalencia de condiciones de entrada.

  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 4 — Sin evidencia persistente y reconstruible, un resultado de Continuous Verification puede ser observable en el momento de ejecución pero imposible de auditar posteriormente. Evidencia: `E-6.3-002`, `E-6.3-012`, `GAP-6.3-02`, `GAP-6.3-06`.

* **Mantenibilidad:** 5 — La ausencia de una cadena de identidad estable obliga a reconstruir manualmente qué corpus, configuración y parámetros produjeron cada resultado. Evidencia: `GAP-6.3-06`, `DC-6.13`.

* **Recuperabilidad:** 5 — Sin evidencia histórica suficiente, diagnosticar una divergencia o determinar si una ejecución fue comparable con otra resulta significativamente más difícil. Evidencia: `E-6.3-012`, `GAP-6.3-06`.

* **Seguridad:** 4 — Una evidencia que no está vinculada criptográfica o lógicamente a sus entradas puede ser sustituida, desacoplada o interpretada fuera de contexto. Evidencia: `GAP-6.2-06`, `GAP-6.2-07`.

* **Financiero:** 3 — La pérdida de reproducibilidad incrementa costos de diagnóstico, reruns y análisis forense.

* **Total Score:** 21/25

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**Toda ejecución de Continuous Verification MUST producir evidencia persistente y determinista cuya identity chain permita reconstruir inequívocamente qué sujeto, referencia, configuración y parámetros produjeron el resultado observado.**

En consecuencia:

* Toda evidencia de verificación **MUST** estar vinculada a la identidad de la baseline consumida.

* Toda evidencia **MUST** permitir identificar el contexto de ejecución que produjo el resultado.

* El resultado **MUST** ser trazable a las entradas y configuración que determinaron la evaluación.

* Las ejecuciones distintas **MUST** permanecer distinguibles entre sí.

* La evidencia histórica **MUST NOT** ser sobrescrita de manera que destruya la trazabilidad de ejecuciones anteriores.

* La identidad de la evidencia **MUST** ser determinista para entradas, configuración y reglas de evaluación equivalentes.

* La existencia de un reporte persistido **MUST NOT**, por sí sola, considerarse evidencia suficiente de reproducibilidad si no puede establecerse su relación con las entradas y condiciones que produjeron el resultado.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

Continuous Verification no termina conceptualmente con la producción de un verdict.

Para que el resultado tenga valor científico y operativo debe ser posible determinar posteriormente:

1. qué sujeto fue ejecutado;
2. contra qué baseline se ejecutó;
3. bajo qué configuración se realizó la evaluación;
4. qué parámetros científicos participaron;
5. qué resultado produjo la evaluación;
6. qué identidad corresponde a cada uno de esos elementos.

Sin esta relación, dos ejecuciones pueden producir resultados aparentemente equivalentes sin existir evidencia suficiente para demostrar que fueron realizadas bajo las mismas condiciones.

La auditoría de Phase 6 identificó una separación entre:

* **Resultado:** qué ocurrió.
* **Evidence:** qué fue observado y persistido.
* **Identity:** a qué ejecución, baseline y configuración pertenece.
* **Reproducibility:** si una ejecución equivalente puede reconstruirse a partir de las identidades y condiciones registradas.

Estas dimensiones están relacionadas, pero no son intercambiables.

### 4.2 Manifestaciones concretas identificadas por la auditoría

* **`E-6.1-001` / `E-6.1-002` (P2 — Medio):** El verification entry point (`tools/evaluation/run_regression.py`) invoca el production pipeline canónico (`apps/bootstrap/pipeline_factory.py::build_extraction_pipeline()`) y ejecuta la extracción real sobre PDFs del corpus, demostrando que la capacidad funcional existe. Sin embargo, la persistencia de evidencia con identity chain completa es un gap identificado por HITO 6.3 (`E-6.3-002`, `E-6.3-012`).

* **`E-6.2-006` (P2 — Medio):** El `RegressionAdapter` (`core/benchmark/topology/regression/adapter.py`) verifica identidad documental, estado sellado, integridad criptográfica (oracle_hash) y completitud biyectiva antes de evaluar. Estas verificaciones constituyen precondiciones de integridad de la referencia.

* **`E-6.2-007` / `E-6.2-008` (P2 — Medio):** La identidad del manifest (`core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash()`) y la identidad del oracle (`core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate()`) son deterministas y sensibles. Constituyen la base criptográfica de la identity chain. El manifest_hash incluye corpus_version, document_id, sha256, traits, page_count, oracle_hash, ground_truth_state. El oracle_hash captura node_id, node_type, strategy, payload_hash.

* **`E-6.2-010` (P2 — Medio):** La baseline v3.9 está completamente sellada: 21 documentos con estado "sealed" y oracle_hash calculado. manifest_hash `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`.

* **`E-6.3-002` / `GAP-6.3-02` (P1 — Alto):** El reporte de regresión generado por el verification entry point no incluye el `configuration_fingerprint`. El entry point lo calcula (`ConfigurationFingerprintCalculator.calculate(config)`) pero no lo persiste en el reporte JSON. Esto rompe la reproducibilidad: no se puede reconstruir qué configuración produjo un verdict específico.

* **`E-6.3-012` / `GAP-6.3-06` (P1 — Alto):** El reporte de regresión no incluye la identity chain completa. El reporte incluye NSS, verdict, versión, documentos con métricas detalladas, y contadores. NO incluye: `configuration_fingerprint`, `manifest_hash`, `parameter_identity`, `result_identity`, `commit_sha`, `schema_version`.

* **`GAP-6.2-02` (P0 — Crítico):** No existe mecanismo de materialización (artifact download, object storage, cache, self-hosted runner) para que CI acceda a los PDFs completos del corpus canónico. 14 de 21 PDFs no están trackeados en git.

* **`GAP-6.2-06` (P1 — Alto):** El verification entry point (`tools/evaluation/run_regression.py`) no verifica el `manifest_hash` contra el manifest recalculado antes de ejecutar la verificación. Un manifest mutado en disco no sería detectado.

* **`GAP-6.2-07` (P1 — Alto):** El verification entry point (`tools/evaluation/run_regression.py`) no verifica el `sha256` de cada PDF contra el valor declarado en el manifest antes de intentar la extracción. Un PDF sustituido no sería detectado.

* **`DC-6.11` / `DC-6.13`:** La auditoría identifica como decisiones necesarias la verificación de manifest_hash y sha256 (DC-6.11) y la persistencia explícita de la identity chain en la evidencia de verificación (DC-6.13). Ambas fueron resueltas por `ADR_F17_BIS_06` v1.2.0 D6.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Identity Chain de la ejecución

1. Toda ejecución de Continuous Verification **MUST** poseer una identidad determinista que permita distinguirla de otras ejecuciones.

2. La evidencia de una ejecución **MUST** mantener una relación explícita con la identidad de la baseline utilizada como referencia.

3. La evidencia **MUST** mantener una relación explícita con la identidad del sujeto de verificación evaluado.

4. La evidencia **MUST** identificar el contexto de configuración bajo el cual se realizó la evaluación.

5. Cuando la evaluación dependa de parámetros científicos o de configuración que afecten su resultado, dichos parámetros **MUST** estar representados en la identidad o evidencia de la ejecución.

6. La identity chain **MUST** permitir establecer la relación entre:

   **Execution → Subject → Baseline → Configuration → Parameters → Evaluation → Result.**

7. La ausencia de un vínculo necesario de la identity chain **MUST** impedir que una ejecución sea considerada completamente reproducible.

### 5.2 Determinismo de identidad

8. Las identidades derivadas de entradas, configuración y parámetros equivalentes **MUST** ser deterministas.

9. La generación de identidades **MUST NOT** depender de información incidental que no forme parte del contexto semántico de la evaluación.

10. Dos ejecuciones que utilicen entradas, configuración, parámetros y reglas de evaluación equivalentes **SHOULD** producir identidades comparables según los contratos de identidad vigentes.

11. La identidad de una ejecución **MUST NOT** confundirse con la identidad de la baseline.

12. La identidad de la baseline **MUST NOT** ser sustituida por la identidad del resultado.

13. La identidad del resultado **MUST NOT** utilizarse como sustituto de las identidades de las entradas que lo produjeron.

### 5.3 Evidencia persistente

14. Cada ejecución de Continuous Verification **MUST** producir evidencia persistente suficiente para reconstruir su contexto de evaluación.

15. La evidencia **MUST** incluir, directa o indirectamente mediante referencias verificables, las identidades necesarias para establecer qué baseline y qué sujeto fueron utilizados.

16. La evidencia **MUST** registrar el resultado producido por la evaluación conforme a la semántica definida por `NADR-F17BIS-27`.

17. La evidencia **MUST** conservar la relación entre el resultado y la configuración que determinó su producción.

18. La evidencia **MUST NOT** depender exclusivamente de información efímera disponible únicamente durante la ejecución.

19. Una ejecución sin evidencia persistente suficiente **MUST NOT** considerarse completamente trazable.

### 5.4 Inmutabilidad y trazabilidad histórica

20. La evidencia de una ejecución completada **MUST** permanecer trazable después de la finalización del proceso.

21. Una nueva ejecución **MUST NOT** sobrescribir evidencia histórica de manera que impida distinguirla de una ejecución anterior.

22. La evidencia histórica **MUST** conservar suficiente identidad para diferenciar ejecuciones sucesivas del mismo sujeto y baseline.

23. Las modificaciones posteriores de una evidencia persistida **MUST NOT** alterar silenciosamente la identidad de la ejecución a la que pertenece.

24. Cuando la evidencia sea reemplazada, versionada o migrada conforme a un mecanismo gobernado, la relación con la evidencia precedente **MUST** permanecer reconstruible.

### 5.5 Reproducibilidad

25. Una ejecución de Continuous Verification **MUST** ser reproducible en el sentido de que sus condiciones relevantes puedan reconstruirse a partir de la evidencia y de los artefactos gobernados por los contratos correspondientes.

26. La reproducibilidad **MUST** distinguirse de la mera repetición del mismo comando.

27. La reproducción de una evaluación **MUST** utilizar una baseline cuya identidad sea compatible con la registrada en la ejecución original.

28. La reproducción de una evaluación **MUST** utilizar una configuración y parámetros compatibles con los registrados en la ejecución original.

29. Cuando una ejecución no pueda ser reproducida debido a la ausencia de una entrada, configuración o identidad requerida, dicha limitación **MUST** ser observable en la evidencia.

30. Una ejecución que produzca el mismo resultado numérico pero no pueda demostrar equivalencia de sus condiciones de entrada **MUST NOT** considerarse científicamente equivalente únicamente por coincidencia del resultado.

### 5.6 Evidencia y resultado

31. La evidencia **MUST** permitir distinguir el resultado de la evaluación de las condiciones que hicieron posible producirlo.

32. La evidencia de un `PASS`, `REGRESSION / DIVERGENCE`, `BASELINE_INTEGRITY_FAILURE` o `EXECUTION_FAILURE` **MUST** conservar la identidad suficiente para determinar qué clase de ejecución produjo dicho estado.

33. La persistencia de evidencia **MUST NOT** modificar el significado del resultado establecido por `NADR-F17BIS-27`.

34. La evidencia **MUST NOT** utilizarse para transformar retrospectivamente una ejecución inválida en una ejecución científicamente válida.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Cada ejecución de Continuous Verification queda vinculada a una identity chain determinista.

* La baseline, el sujeto, la configuración, los parámetros, la evaluación y el resultado dejan de ser artefactos independientes sin relación demostrable.

* Los resultados históricos pueden diferenciarse de ejecuciones posteriores del mismo sujeto.

* La reproducibilidad deja de depender exclusivamente de repetir manualmente un comando.

* Una discrepancia entre resultados puede analizarse junto con las identidades de las condiciones que produjeron cada ejecución.

* La evidencia persistida adquiere valor forense y no constituye simplemente una salida informativa de CI.

* La identidad de la baseline permanece conceptualmente separada de la identidad de la ejecución y del resultado.

* La semántica de los resultados permanece gobernada por `NADR-F17BIS-27`.

* La materialización e integridad física de la baseline permanecen gobernadas por `NADR-F17BIS-26`.

* Los detalles concretos de persistencia y formato de reportes quedan abiertos a implementación mientras satisfagan la identity chain normativa.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

### Verification (estática/mecánica)

* Inspección de la evidencia persistida para verificar que existe una identidad de ejecución.

* Verificación de que la evidencia mantiene una relación identificable con la baseline utilizada.

* Verificación de que la evidencia identifica el sujeto de verificación.

* Verificación de que configuración y parámetros relevantes forman parte de la identity chain.

* Verificación de que ejecuciones sucesivas no sobrescriben silenciosamente la identidad histórica de ejecuciones anteriores.

* Verificación de que la representación de identidad es determinista para entradas equivalentes.

* Inspección de los reportes para comprobar que el resultado puede relacionarse con las condiciones que lo produjeron.

### Validation (dinámica/comportamental)

* Ejecutar dos veces una evaluación con entradas, baseline, configuración y parámetros equivalentes y verificar la reproducibilidad de sus identidades y evidencia conforme a los contratos vigentes.

* Ejecutar evaluaciones con baselines diferentes y verificar que sus identidades no colisionan semánticamente.

* Modificar una condición relevante de configuración y verificar que la identity chain resultante permite distinguir la nueva ejecución.

* Ejecutar sucesivamente el mismo sujeto y baseline y verificar que las ejecuciones permanecen históricamente distinguibles.

* Intentar reconstruir una ejecución únicamente a partir de su evidencia persistida y verificar que las identidades necesarias para establecer su contexto están disponibles.

* Verificar que una coincidencia del resultado numérico no oculta diferencias en baseline, configuración o parámetros.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto                          | Relación                                                                                                                                                 |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ADR_F17_BIS_MASTER`               | Este NADR materializa la exigencia de determinismo, reproducibilidad y evidencia verificable de la arquitectura de Scientific Baseline.                  |
| `ADR_F17_BIS_06` v1.2.0            | Este NADR materializa D6 (Operational Semantics), específicamente la persistencia de evidencia, y D8 (Integrity Protection), además de resolver DC-6.13. |
| `NADR-F17BIS-16`                   | **Dependencia directa:** NADR-16 gobierna las identidades criptográficas (Cryptographic Identity Semantics) que este NADR consume para la identity chain. |
| `NADR-F17BIS-17`                   | **Dependencia directa:** NADR-17 gobierna la integridad de codificación de identidad (Identity Encoding Integrity) que este NADR consume para la identity chain. |
| `NADR-F17BIS-19`                   | **Dependencia directa:** proporciona el contexto científico de evaluación cuyos parámetros y resultados deben quedar vinculados a la evidencia.          |
| `NADR-F17BIS-21`                   | **Dependencia directa:** proporciona la identidad y el estado de la baseline sellada que debe formar parte de la identity chain.                         |
| `NADR-F17BIS-25`                   | **Dependencia directa:** define el sujeto cuya ejecución debe quedar identificada en la evidencia.                                                       |
| `NADR-F17BIS-26`                   | **Dependencia directa:** establece la identidad física e integridad de la baseline consumida.                                                            |
| `NADR-F17BIS-27`                   | **Dependencia directa:** define la semántica del resultado que debe ser persistido y relacionado con la ejecución.                                       |
| `NADR-F17BIS-29`                   | **Influencia:** los perfiles de ejecución forman parte del contexto que debe poder distinguirse en la evidencia cuando afecten la evaluación.            |
| `NADR-F17BIS-30`                   | **Influencia:** el enforcement consume resultados cuya procedencia debe poder demostrarse mediante la evidencia persistida.                              |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | Las tareas que materializan estas reglas son gobernadas por el Execution Plan de Fase 6.                                                                 |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** qué constituye el production pipeline ni cómo se ejecuta el sujeto de verificación (responsabilidad de `NADR-F17BIS-25`).

* **No gobierna** la materialización física ni la integridad de la baseline (responsabilidad de `NADR-F17BIS-26`).

* **No gobierna** la cualificación, elegibilidad, migración ni sealing de la baseline (responsabilidad de `NADR-F17BIS-20` y `NADR-F17BIS-21`).

* **No gobierna** la semántica del resultado ni la taxonomía de exit codes (responsabilidad de `NADR-F17BIS-27`).

* **No gobierna** los algoritmos, thresholds, pesos ni políticas científicas de evaluación (responsabilidad de `NADR-F17BIS-19` y los contratos científicos correspondientes).

* **No establece** una nueva política de calibración ni una nueva baseline de divergencia.

* **No prescribe** un formato concreto de archivo, esquema JSON, nombre de campo, clase, función o tecnología de persistencia.

* **No gobierna** la definición de identidades criptográficas ni el framing de hash (responsabilidad de `NADR-F17BIS-16` y `NADR-F17BIS-17`). Este NADR consume las identidades criptográficas; no las define.

* **No gobierna** la frecuencia ni selección de perfiles de ejecución (responsabilidad de `NADR-F17BIS-29`).

* **No gobierna** branch protection ni merge enforcement (responsabilidad de `NADR-F17BIS-30`).

* **No prescribe** tareas de implementación ni Definition of Done; dichas responsabilidades pertenecen al Execution Plan de Fase 6.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.