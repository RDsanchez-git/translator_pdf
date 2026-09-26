# NADR-F17BIS-27: Verification Outcome & Failure Semantics

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-27`

* **Título:** Verification Outcome & Failure Semantics

* **Clase de Decisión:** `OPERATIONAL / STRUCTURAL`

* **Nivel de Cumplimiento:** `MANDATORY`

* **Versión:** 1.0.0

* **Ciclo de Vida:** `FROZEN`

* **Vigente Desde:** Fase 6 (Continuous Verification)

* **Autoridad:** Architecture Board

* **Responsable Técnico:** Equipo de Arquitectura / Fase 6

* **Capacidad Arquitectónica:** CAP-7 (Verification Outcome & Failure Semantics) — Establece una semántica determinista y no ambigua para distinguir resultados científicos de divergencia, fallos de integridad de la referencia y fallos operacionales de ejecución, garantizando que ningún estado de Continuous Verification pueda interpretarse simultáneamente como éxito, regresión y fallo de ejecución.

* **Evidencia Forense:** `E-6.0-003`, `E-6.0-004`, `E-6.1-006`, `E-6.2-004`, `E-6.2-006`, `E-6.3-002`, `E-6.3-003`, `E-6.3-005`, `GAP-6.0-02`, `GAP-6.3-02`, `GAP-6.3-03`, `DC-6.1`, `DC-6.4`, `DC-6.9`, `DC-6.10`

* **Referencias Cruzadas:**

  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-19` (Regresión Topológica Graduada), `NADR-F17BIS-21` (Ground Truth Eligibility, Migration & Sealing), `NADR-F17BIS-25` (Verification Boundary & Production Subject), `NADR-F17BIS-26` (Canonical Baseline Materialization & Integrity)

  * **Influencia:** `NADR-F17BIS-28` (Evidence & Identity Chain), `NADR-F17BIS-29` (Execution Profiles), `NADR-F17BIS-30` (CI Enforcement), `PHASE_17BIS_FASE6_EXECUTION_PLAN`

  * **Conflictúa con:** Cualquier práctica que utilice un mismo resultado para representar simultáneamente una divergencia científica, un fallo de integridad de la baseline y un fallo operacional; cualquier práctica que trate un proceso abortado como una evaluación científica válida; cualquier práctica que convierta un resultado ambiguo en un éxito silencioso.

  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Una semántica ambigua permite que CI trate de manera indistinguible una regresión científica, un fallo de infraestructura o una baseline inválida.

* **Mantenibilidad:** 4 — Sin una taxonomía estable, cada nuevo consumidor del resultado puede interpretar de manera diferente los mismos estados.

* **Recuperabilidad:** 5 — La ausencia de separación entre divergencia y fallo operacional dificulta determinar si debe investigarse el production pipeline, la baseline o la infraestructura de ejecución.

* **Seguridad:** 4 — Un estado ambiguo puede permitir que un fallo de ejecución sea interpretado como ausencia de regresión y, por tanto, evite el comportamiento de protección esperado.

* **Financiero:** 2 — La ambigüedad genera principalmente costos indirectos de diagnóstico y retrabajo.

* **Total Score:** 20/25

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La Continuous Verification MUST producir un resultado operacionalmente determinista que distinga inequívocamente entre éxito de evaluación, divergencia científica, fallo de integridad de la referencia y fallo de ejecución, y MUST NOT representar un fallo no evaluable como una evaluación exitosa.**

En consecuencia:

* Un resultado de **evaluación científica** solo puede emitirse cuando el production pipeline y la baseline hayan satisfecho sus respectivas precondiciones.

* Una **divergencia científica** MUST distinguirse de un fallo operacional.

* Un **fallo de integridad de la baseline** MUST distinguirse de una divergencia producida por el production pipeline.

* Un proceso que no haya completado las etapas necesarias para producir una evaluación válida **MUST NOT** generar un resultado científico equivalente a `PASS`.

* Los resultados MUST ser deterministas respecto de las mismas entradas, configuración y baseline.

* Los exit codes utilizados por el verification entry point **MUST** representar estados operacionales inequívocos y no pueden utilizarse de manera que un mismo código tenga significados incompatibles.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La Continuous Verification combina dos dimensiones que deben permanecer separadas:

1. **Resultado de la evaluación:** qué relación existe entre la salida del production pipeline y la referencia de verificación.

2. **Estado de ejecución:** si la evaluación pudo ejecutarse de manera válida y completa.

La auditoría de Phase 6 identificó que ambas dimensiones no están suficientemente separadas en la superficie operacional actual.

Esto genera cuatro clases conceptualmente distintas:

* **Evaluación válida sin divergencia relevante.**
* **Evaluación válida con divergencia.**
* **Referencia de evaluación inválida o no verificable.**
* **Ejecución no válida o incompleta.**

Confundir estas clases produce falsos positivos, falsos negativos o resultados no reproducibles.

### 4.2 Manifestaciones concretas identificadas por la auditoría

* **`E-6.0-003` / `DC-6.1`:** La auditoría identificó la necesidad de distinguir entre **conformance**, **regression** y una eventual **baseline of divergence**. Estas dimensiones no son equivalentes y pueden producir estados diferentes sobre el mismo resultado.

* **`E-6.0-004` / `GAP-6.0-02` (P0 — Crítico):** El mecanismo existente `DoubleProtectionMechanism` establece una precedencia de fallo crítico donde `Critical FN > 0` produce `HARD_FAIL` independientemente del NSS. Esta semántica corresponde a una evaluación contra la referencia y no constituye por sí misma una clasificación de fallo operacional.

* **`E-6.1-006`:** El verification entry point existente puede producir resultados de evaluación mediante el mecanismo de regresión topológica, demostrando que la capacidad funcional existe fuera de la integración CI.

* **`E-6.2-004` / `DC-6.10`:** La ausencia o invalidez de artefactos requeridos por la baseline constituye una condición previa a la evaluación y no una divergencia del production pipeline.

* **`E-6.2-006` / `DC-6.14`:** Una discrepancia de integridad física de la baseline debe impedir su utilización como referencia válida.

* **`E-6.3-002` / `GAP-6.3-02` (P1 — Alto):** El estado operacional de la ejecución no está completamente expresado en una taxonomía diferenciada que permita distinguir una divergencia de una falla de infraestructura o precondición.

* **`E-6.3-003` / `GAP-6.3-03` (P1 — Alto):** El exit code `1` puede resultar ambiguo entre una condición de regresión/fallo de evaluación y otros estados de ejecución.

* **`E-6.3-005`:** La ejecución de `run_regression.py` demuestra que existe una superficie de exit semantics, pero la integración CI y la propagación completa de dichos estados aún requieren una semántica normativa inequívoca.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Separación entre resultado científico y estado operacional

1. Continuous Verification **MUST** distinguir entre el resultado de la evaluación científica y el estado operacional de la ejecución.

2. Una evaluación científica **MUST** considerarse válida únicamente cuando se hayan satisfecho las precondiciones necesarias del sujeto de verificación y de la referencia.

3. Un fallo que impida completar la evaluación **MUST NOT** ser interpretado como evidencia de ausencia de divergencia.

4. Un fallo de infraestructura **MUST NOT** ser interpretado como una divergencia científica del production pipeline.

5. Una divergencia científica **MUST NOT** ser interpretada como un fallo de integridad de la baseline.

### 5.2 Taxonomía normativa de resultados

6. El resultado de Continuous Verification **MUST** pertenecer a una taxonomía determinista que distinga, como mínimo:

   * **PASS:** evaluación completada y sin condición de divergencia que active el criterio de fallo correspondiente.

   * **REGRESSION / DIVERGENCE:** evaluación completada y evidencia de divergencia respecto de la referencia bajo la política de evaluación vigente.

   * **BASELINE_INTEGRITY_FAILURE:** la referencia requerida no pudo demostrarse íntegra, completa o correctamente identificada.

   * **EXECUTION_FAILURE:** la evaluación no pudo completarse debido a una condición operacional del proceso de ejecución.

7. Los estados anteriores **MUST** ser mutuamente distinguibles.

8. Un estado de `BASELINE_INTEGRITY_FAILURE` **MUST NOT** ser contabilizado como `REGRESSION / DIVERGENCE`.

9. Un estado de `EXECUTION_FAILURE` **MUST NOT** ser contabilizado como `PASS`.

10. Un estado de `EXECUTION_FAILURE` **MUST NOT** ser contabilizado como evidencia científica de regresión.

### 5.3 Precedencia de evaluación

11. Las precondiciones de integridad de la baseline **MUST** ser satisfechas antes de emitir cualquier resultado de evaluación científica.

12. La evaluación del production pipeline **MUST** completarse antes de emitir un resultado científico basado en su salida.

13. Cuando una precondición de referencia falla, la ejecución **MUST** detener la evaluación científica dependiente de dicha referencia.

14. Cuando una condición operacional impide completar la evaluación, el resultado **MUST** conservar la distinción entre ejecución incompleta y divergencia científica.

15. Un resultado parcial **MUST NOT** presentarse como una evaluación científica completa.

### 5.4 Conformance, Regression y Divergence Baseline

16. **Conformance** y **Regression** **MUST** considerarse dimensiones conceptualmente distintas de evaluación.

17. La evaluación de **Conformance** **MUST** representar la relación entre el resultado actual y la referencia normativa correspondiente.

18. La evaluación de **Regression** **MUST** representar la relación entre ejecuciones o referencias comparables según la política de regresión vigente.

19. Una eventual **Baseline of Divergence** **MUST** ser tratada como una referencia explícitamente gobernada y no podrá inferirse automáticamente a partir de cualquier ejecución previa.

20. La existencia simultánea de resultados de Conformance y Regression **MUST** permitir que ambos estados sean representados independientemente cuando sus referencias y criterios sean diferentes.

21. Un resultado de `REGRESSION = PASS` **MUST NOT** implicar automáticamente `CONFORMANCE = PASS`.

22. Un resultado de `CONFORMANCE = FAIL` **MUST NOT** implicar automáticamente `REGRESSION = FAIL`.

23. La adopción de una nueva baseline de divergencia o recalibración **MUST** estar sujeta al proceso de gobernanza correspondiente y no podrá realizarse implícitamente durante una ejecución de Continuous Verification.

### 5.5 Criticalidad y política de evaluación

24. Cuando el mecanismo de evaluación vigente determine que una condición crítica tiene precedencia sobre otras métricas, dicha precedencia **MUST** conservarse en el resultado de evaluación.

25. Un `HARD_FAIL` producido por el mecanismo de evaluación **MUST** conservar su significado como resultado de evaluación y **MUST NOT** confundirse con un `EXECUTION_FAILURE`.

26. Las métricas científicas utilizadas para determinar una divergencia, incluyendo NSS y criticality-aware evaluation, **MUST** conservar las políticas establecidas por sus contratos normativos.

27. Continuous Verification **MUST NOT** modificar silenciosamente thresholds, pesos, criterios de criticalidad o políticas de evaluación para convertir un resultado divergente en un resultado exitoso.

28. La recalibración de thresholds, pesos, criticalidad o baseline **MUST** seguir un proceso de decisión explícito y separado de la ejecución ordinaria de Continuous Verification.

### 5.6 Exit Codes y propagación operacional

29. Cada resultado operacional **MUST** tener una representación de exit status determinista y no ambigua.

30. Un mismo exit code **MUST NOT** representar simultáneamente estados operacionales incompatibles.

31. El exit status del verification entry point **MUST** preservar la distinción entre evaluación científica fallida y ejecución operacional inválida.

32. La capa de CI **MUST** recibir y propagar el resultado operacional del verification entry point sin reinterpretarlo de manera que elimine su semántica.

33. La traducción entre resultado de dominio, estado operacional y exit status **MUST** ser determinista y verificable.

34. Un proceso que termine por una excepción no controlada **MUST NOT** ser interpretado como un resultado científico válido.

35. La ausencia de un resultado científico válido **MUST NOT** ser equivalente a `PASS`.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Continuous Verification posee una semántica operacional explícita y determinista.

* Una divergencia científica queda separada de un fallo de infraestructura o de integridad de la referencia.

* La evaluación puede representar simultáneamente dimensiones independientes de conformance y regression sin colapsarlas en un único significado.

* `HARD_FAIL` conserva su significado como resultado de la política de evaluación y no se confunde con un crash o fallo de ejecución.

* La ausencia de una evaluación válida deja de poder interpretarse silenciosamente como éxito.

* La propagación hacia CI conserva la semántica producida por el verification entry point.

* Los cambios de thresholds, pesos, criticalidad o baseline requieren gobernanza explícita y no pueden introducirse como efecto lateral de la ejecución.

* El estado científico de la baseline existente permanece separado de la semántica operacional del gate. En particular, el resultado actual de Phase 5 —incluyendo `163 Critical FN` y `NSS 0.7208`— no es modificado ni reinterpretado por este NADR.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

### Verification (estática/mecánica)

* Inspección del contrato de resultados para verificar que los estados de evaluación científica y ejecución operacional son distinguibles.

* Inspección del verification entry point para verificar que cada condición de terminación tiene una representación operacional determinista.

* Verificación de que los exit codes no tienen significados superpuestos.

* Inspección de la propagación del resultado desde el verification entry point hasta CI.

* Verificación de que los thresholds, pesos y criterios de evaluación provienen de configuración gobernada y no son modificados silenciosamente durante la ejecución.

* Verificación de que los estados de `BASELINE_INTEGRITY_FAILURE`, `EXECUTION_FAILURE` y `REGRESSION / DIVERGENCE` permanecen diferenciados.

### Validation (dinámica/comportamental)

* Ejecución contra la baseline canónica íntegra, verificando que una evaluación completada produce un resultado científico válido.

* Ejecución con una baseline cuya integridad haya sido alterada, verificando que se produce un estado de fallo de integridad y no una regresión científica.

* Ejecución con un artefacto obligatorio ausente, verificando que no se emite `PASS`.

* Ejecución con una condición operacional que impida completar la evaluación, verificando que se produce `EXECUTION_FAILURE` y no una divergencia científica.

* Ejecución que produzca una divergencia topológica, verificando que la divergencia se representa como resultado de evaluación y no como fallo de infraestructura.

* Verificación de la precedencia de una condición crítica cuando el mecanismo de evaluación vigente la establece.

* Verificación de que `CONFORMANCE = FAIL` puede coexistir con `REGRESSION = PASS` sin que uno sobrescriba semánticamente al otro.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto                          | Relación                                                                                                                                                              |
| :--------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ADR_F17_BIS_MASTER`               | Este NADR materializa la semántica operacional necesaria para la Continuous Verification definida por el ADR Maestro.                                                 |
| `ADR_F17_BIS_06` v1.2.0            | Este NADR materializa D6 (Operational Semantics) y parte de D9 (Conformance como modelo primario, con separación respecto de Regression y Divergence Baseline).       |
| `NADR-F17BIS-19`                   | **Dependencia directa:** gobierna el mecanismo y las políticas científicas de evaluación topológica cuyos resultados son clasificados operacionalmente por este NADR. |
| `NADR-F17BIS-21`                   | **Dependencia directa:** define las condiciones de integridad y sealing de la referencia cuya validez precede a la evaluación.                                        |
| `NADR-F17BIS-25`                   | **Dependencia directa:** define el sujeto de verificación cuyo resultado es clasificado por este NADR.                                                                |
| `NADR-F17BIS-26`                   | **Dependencia directa:** define las precondiciones de materialización e integridad de la baseline.                                                                    |
| `NADR-F17BIS-28`                   | **Influencia:** persiste la identidad y evidencia necesaria para reconstruir el significado del resultado producido.                                                  |
| `NADR-F17BIS-29`                   | **Influencia:** los perfiles de ejecución determinan el contexto operacional en que se producen los resultados.                                                       |
| `NADR-F17BIS-30`                   | **Influencia:** consume el resultado operacional definido aquí para determinar el comportamiento de enforcement.                                                      |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | Las tareas que materializan estas reglas son gobernadas por el Execution Plan de Fase 6.                                                                              |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** qué constituye el production pipeline ni cuál es el sujeto de verificación (responsabilidad de `NADR-F17BIS-25`).

* **No gobierna** la materialización física ni la integridad de los artefactos de la baseline (responsabilidad de `NADR-F17BIS-26`).

* **No gobierna** la cualificación, elegibilidad o sealing original de la baseline (responsabilidad de `NADR-F17BIS-20` y `NADR-F17BIS-21`).

* **No gobierna** el algoritmo de evaluación topológica, sus costos, pesos, labels, raíces ni thresholds científicos (responsabilidad de `NADR-F17BIS-19` y los contratos científicos correspondientes).

* **No establece** una nueva política científica de calibración ni modifica los thresholds, pesos o bandas de NSS existentes.

* **No establece** una nueva baseline de divergencia ni autoriza por sí mismo un proceso de re-baseline.

* **No gobierna** la identity chain completa ni la persistencia integral de la evidencia (responsabilidad de `NADR-F17BIS-28`).

* **No gobierna** los perfiles de ejecución ni su frecuencia (responsabilidad de `NADR-F17BIS-29`).

* **No gobierna** la relación entre el resultado y branch protection / merge protection (responsabilidad de `NADR-F17BIS-30`).

* **No prescribe** tareas de implementación ni Definition of Done; dichas responsabilidades pertenecen al Execution Plan de Fase 6.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.
