# NADR-F17BIS-29: Continuous Verification Execution Profiles

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-29`

* **Título:** Continuous Verification Execution Profiles

* **Clase de Decisión:** `OPERATIONAL / STRUCTURAL`

* **Nivel de Cumplimiento:** `MANDATORY`

* **Versión:** 1.0.0

* **Ciclo de Vida:** `FROZEN`

* **Fecha de Emisión:** 2026-09-25

* **Fecha de Congelamiento:** 2026-09-25

* **Vigente Desde:** Fase 6 (Continuous Verification)

* **Autoridad:** Architecture Board

* **Responsable Técnico:** Equipo de Arquitectura / Fase 6

* **Capacidad Arquitectónica:** CAP-5 / CAP-7 (Execution Profiles & Verification Coverage) — Define la frontera normativa de los perfiles de ejecución de Continuous Verification, garantizando que cualquier modalidad de ejecución conserve el sujeto, la referencia, la semántica, la evidencia y las garantías de integridad establecidas por los NADRs precedentes.

* **Evidencia Forense:** `E-6.3-005`, `E-6.3-011`, `GAP-6.3-01`, `GAP-6.3-05`, `DC-6.5`, `DC-6.8`, `DC-6.12`

* **Referencias Cruzadas:**

  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-25` (Verification Boundary & Production Subject), `NADR-F17BIS-26` (Canonical Baseline Materialization & Integrity), `NADR-F17BIS-27` (Verification Outcome & Failure Semantics), `NADR-F17BIS-28` (Evidence, Identity Chain & Reproducibility)

  * **Influencia:** `NADR-F17BIS-30` (CI Enforcement), `PHASE_17BIS_FASE6_EXECUTION_PLAN`

  * **Conflictúa con:** Cualquier práctica que cree perfiles de ejecución que omitan silenciosamente el production pipeline, sustituyan la baseline canónica, alteren la semántica de resultados o reduzcan la evidencia requerida sin declararlo explícitamente.

  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin perfiles de ejecución explícitamente gobernados, diferentes superficies de CI pueden ejecutar subconjuntos incompatibles del proceso y presentar todos ellos como Continuous Verification equivalente. Evidencia: `E-6.3-005`, `E-6.3-011`, `GAP-6.3-05`.

* **Mantenibilidad:** 4 — La ausencia de una definición común de perfil permite que cada integración introduzca sus propias reglas de cobertura y dificulta comparar ejecuciones. Evidencia: `GAP-6.3-05`.

* **Recuperabilidad:** 4 — Si no se conoce el perfil bajo el cual ocurrió una ejecución, resulta difícil determinar qué cobertura y qué garantías tenía el resultado. Evidencia: `NADR-F17BIS-28` (identity chain debe incluir identidad del perfil).

* **Seguridad:** 4 — Un perfil reducido no gobernado puede convertirse accidentalmente en una vía para evitar partes críticas de la verificación. Evidencia: `GAP-6.3-01`.

* **Financiero:** 3 — Ejecutar siempre la verificación completa puede incrementar innecesariamente el costo operativo, mientras que reducirla sin contrato puede degradar la protección. Evidencia: `E-6.3-007` (3.74s para corpus completo, factible en CI).

* **Total Score:** 20/25

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**Toda modalidad de Continuous Verification MUST ejecutarse bajo un perfil explícitamente definido que declare su alcance, cobertura y garantías, y ningún perfil reducido podrá omitir silenciosamente las condiciones normativas del sujeto, referencia, resultado o evidencia.**

En consecuencia:

* Todo perfil de ejecución **MUST** tener una definición explícita de su alcance.

* Todo perfil **MUST** identificar qué corpus y qué cobertura de verificación ejecuta.

* Todo perfil **MUST** conservar las fronteras establecidas por `NADR-F17BIS-25`, `NADR-F17BIS-26`, `NADR-F17BIS-27` y `NADR-F17BIS-28`.

* Un perfil reducido **MUST NOT** presentarse como equivalente a una ejecución completa si su cobertura es diferente.

* La existencia de varios perfiles **MUST NOT** crear varios mecanismos de Continuous Verification.

* Los perfiles pueden diferenciar cobertura, costo y duración, pero **MUST NOT** alterar silenciosamente el sujeto, la referencia, la semántica del resultado o las garantías mínimas de integridad.

* La selección y frecuencia temporal de cada perfil **MUST** ser gobernada fuera de este NADR.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

Continuous Verification puede ejecutarse bajo diferentes restricciones operacionales.

Una ejecución completa sobre todo el corpus canónico puede proporcionar una cobertura distinta de una ejecución reducida destinada a detectar rápidamente regresiones obvias. Ambas pueden ser arquitectónicamente legítimas, pero no son científicamente equivalentes.

La auditoría de Phase 6 identificó por tanto la necesidad de distinguir entre:

1. **Perfil de ejecución:** contrato que define qué se ejecuta y qué garantías conserva.

2. **Cobertura:** subconjunto de corpus, escenarios o verificaciones incluidos en el perfil.

3. **Semántica:** reglas bajo las cuales se interpreta el resultado.

4. **Frecuencia:** cuándo se ejecuta el perfil.

Estas dimensiones no deben confundirse.

En particular, un perfil reducido no puede convertirse implícitamente en un sustituto de la verificación completa.

### 4.2 Manifestaciones concretas identificadas por la auditoría

* **`E-6.3-005` / `E-6.3-011` (P2 — Medio):** No existen perfiles diferenciados de ejecución. Un único workflow (`.github/workflows/ci.yml`, 3541 bytes) con triggers push [main, develop] y pull_request [main]. Sin schedules (no hay perfil nightly), sin workflow_dispatch (no hay perfil manual), sin paths filter (se ejecuta en todo push, incluso cambios irrelevantes). No hay workflows adicionales (nightly, release, manual).

* **`GAP-6.3-05` (OPEN):** No existen perfiles diferenciados de ejecución (PR smoke, full merge, nightly). Un único workflow con triggers push/PR. Sin schedules, sin workflow_dispatch, sin paths filter. El corpus completo (3.74s) se ejecuta en todo push, incluso cambios irrelevantes.

* **`GAP-6.3-01` (P0 — Crítico):** CI no invoca el entry point real (`run_regression.py`). El job `regression-gates` ejecuta `pytest -m "regression"` que selecciona 0 tests. El entry point que conecta production pipeline + baseline sellada no es invocado. La integración CI → verification entry point es una precondición para que cualquier perfil constituya realmente Continuous Verification.

* **`DC-6.5`:** La auditoría identificó la necesidad de definir perfiles diferenciados de Continuous Verification, incluyendo la posibilidad de ejecuciones con distinta cobertura operacional. La decisión pendiente es la gobernanza de estos perfiles, no la imposición de una nomenclatura concreta. Resuelto por `ADR_F17_BIS_06` v1.2.0 D7: "CI debe soportar al menos un perfil de ejecución que ejecute la verificación completa contra el corpus canónico sellado. Perfiles adicionales son definidos por los NADRs."

* **`DC-6.8`:** La auditoría identificó la necesidad de un mecanismo de verificación rápida o *smoke verification* que permita detectar fallos evidentes sin convertirlo en sustituto de la evaluación completa. Resuelto por `ADR_F17_BIS_06` v1.2.0 D7 como capacidad adicional definible por NADRs.

* **`DC-6.12`:** Conexión CI ↔ entry point. Resuelto por `ADR_F17_BIS_06` v1.2.0 D4: "CI debe invocar el verification entry point real que ejecuta el production pipeline contra la baseline sellada."

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Definición de perfil

1. Todo perfil de Continuous Verification **MUST** estar explícitamente definido.

2. Un perfil **MUST** especificar, directa o indirectamente mediante contratos gobernados, su alcance de ejecución.

3. Un perfil **MUST** identificar la cobertura de corpus o escenarios sobre la cual produce su resultado.

4. Un perfil **MUST** conservar la utilización del production pipeline definido por `NADR-F17BIS-25`.

5. Un perfil **MUST** consumir la baseline bajo las reglas de integridad establecidas por `NADR-F17BIS-26`.

6. Un perfil **MUST** producir resultados bajo la semántica establecida por `NADR-F17BIS-27`.

7. Un perfil **MUST** producir evidencia bajo las reglas establecidas por `NADR-F17BIS-28`.

### 5.2 Cobertura y clasificación del perfil

8. La cobertura de un perfil **MUST** ser explícitamente distinguible de la cobertura de cualquier otro perfil.

9. Un perfil que ejecute una cobertura parcial **MUST** identificarse como cobertura parcial.

10. Una ejecución parcial **MUST NOT** presentarse como equivalente a una ejecución completa.

11. Una diferencia de cobertura entre perfiles **MUST** ser observable en la evidencia de ejecución.

12. Los perfiles **MUST NOT** modificar los criterios científicos de evaluación únicamente para compensar una reducción de cobertura.

13. La reducción de cobertura **MUST NOT** eliminar silenciosamente las condiciones de integridad de la baseline.

### 5.3 Perfil completo

14. Continuous Verification **MUST** disponer de al menos un perfil cuya cobertura represente la evaluación completa definida por los contratos vigentes de la fase.

15. El perfil completo **MUST** constituir la referencia contra la cual se interprete la suficiencia de cualquier perfil reducido.

16. La existencia de un perfil reducido **MUST NOT** eliminar ni reemplazar el perfil completo.

17. La definición de "completo" **MUST** derivarse de la cobertura gobernada por el corpus y las reglas científicas vigentes, y **MUST NOT** definirse únicamente por duración, cantidad de archivos o costo computacional.

### 5.4 Perfil reducido / Smoke Verification

18. Continuous Verification **SHOULD** disponer de un perfil reducido destinado a detectar rápidamente condiciones de fallo evidentes cuando las restricciones operacionales lo justifiquen.

19. Un perfil reducido **MUST** declarar explícitamente su cobertura limitada.

20. Un perfil reducido **MUST** conservar las mismas fronteras normativas de sujeto y referencia que el perfil completo.

21. Un perfil reducido **MUST NOT** sustituir al perfil completo cuando la política de ejecución requiera cobertura completa.

22. Un resultado satisfactorio de un perfil reducido **MUST NOT** interpretarse como evidencia de que las partes no ejecutadas del corpus también fueron verificadas.

23. Un fallo detectado por un perfil reducido **MUST** conservar la semántica establecida por `NADR-F17BIS-27`.

### 5.5 Perfiles y mecanismo de verificación

24. Los distintos perfiles **MUST** reutilizar el mismo verification entry point y mecanismo normativo de evaluación, salvo que una decisión arquitectónica posterior establezca explícitamente lo contrario.

25. Crear un mecanismo de evaluación diferente para cada perfil **MUST NOT** utilizarse como estrategia para diferenciar perfiles.

26. Las diferencias entre perfiles **MUST** expresarse mediante cobertura, alcance o contexto operacional gobernado, no mediante mecanismos científicos incompatibles.

27. Un perfil **MUST NOT** omitir el verification entry point y seguir considerándose una ejecución válida de Continuous Verification.

### 5.6 Perfiles y reproducibilidad

28. La identidad de un perfil **MUST** formar parte del contexto de ejecución cuando dicha identidad afecte la cobertura o interpretación del resultado.

29. Dos ejecuciones bajo perfiles diferentes **MUST** permanecer distinguibles en la evidencia.

30. La evidencia de una ejecución **MUST** permitir determinar bajo qué perfil fue producida.

31. Una ejecución que cambie de perfil **MUST NOT** conservar una identidad de ejecución indistinguible de una ejecución realizada bajo otro perfil cuando las condiciones de evaluación sean diferentes.

### 5.7 Perfil y frecuencia

32. Este NADR **MUST NOT** establecer por sí mismo la frecuencia temporal de ejecución de los perfiles.

33. La selección de un perfil para un evento determinado **MUST** estar gobernada por el mecanismo operacional correspondiente.

34. Una política de frecuencia **MUST NOT** modificar las garantías normativas definidas para el perfil seleccionado.

35. La existencia de una ejecución periódica o disparada por eventos **MUST NOT** alterar la identidad del perfil bajo el cual se ejecuta.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Continuous Verification posee una unidad explícita de configuración operacional: el perfil de ejecución.

* Una ejecución completa y una ejecución reducida pueden coexistir sin ser confundidas.

* La reducción de cobertura deja de ser una degradación silenciosa del control.

* Los perfiles reutilizan el mismo sujeto, referencia, mecanismo y semántica normativa.

* Las diferencias entre perfiles se expresan mediante cobertura y contexto operacional, no mediante duplicación de mecanismos científicos.

* La evidencia permite determinar qué perfil produjo cada resultado.

* La frecuencia de ejecución queda separada de la definición arquitectónica del perfil.

* La arquitectura puede incorporar posteriormente perfiles concretos —por ejemplo, una ejecución reducida y otra completa— sin modificar las fronteras establecidas por los NADRs anteriores.

* Un perfil reducido no puede convertirse en sustituto implícito de la cobertura completa.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

### Verification (estática/mecánica)

* Inspección de cada perfil para verificar que posee una definición explícita de alcance y cobertura.

* Verificación de que todos los perfiles utilizan el production pipeline normativo.

* Verificación de que todos los perfiles utilizan la baseline canónica bajo las reglas de `NADR-F17BIS-26`.

* Verificación de que todos los perfiles utilizan la misma semántica de resultado definida por `NADR-F17BIS-27`.

* Verificación de que la identidad del perfil forma parte de la evidencia cuando afecta la cobertura.

* Verificación de que no existen mecanismos científicos paralelos creados exclusivamente para perfiles diferentes.

* Verificación de que un perfil reducido está claramente identificado como parcial.

### Validation (dinámica/comportamental)

* Ejecutar el perfil completo contra el corpus definido como cobertura completa y verificar que la ejecución recorre la cobertura esperada.

* Ejecutar un perfil reducido y verificar que su cobertura es estrictamente identificable y diferente de la cobertura completa.

* Verificar que un resultado `PASS` del perfil reducido no implica que los artefactos no ejecutados hayan sido evaluados.

* Ejecutar dos perfiles diferentes y verificar que sus evidencias permanecen distinguibles.

* Verificar que ambos perfiles utilizan el mismo sujeto y referencia normativa.

* Verificar que una divergencia detectada por un perfil reducido conserva la semántica definida por `NADR-F17BIS-27`.

* Verificar que cambiar la frecuencia de ejecución no altera el contrato del perfil.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto                          | Relación                                                                                                                                                               |
| :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ADR_F17_BIS_MASTER`               | Este NADR materializa la capacidad de Continuous Verification como control operativo continuo sin convertir cada modalidad de ejecución en un mecanismo independiente. |
| `ADR_F17_BIS_06` v1.2.0            | Este NADR materializa D7 (Execution Profiles) y DC-6.5 / DC-6.8.                                                                                                       |
| `NADR-F17BIS-25`                   | **Dependencia directa:** define el production pipeline que todos los perfiles deben verificar.                                                                         |
| `NADR-F17BIS-26`                   | **Dependencia directa:** define las condiciones bajo las cuales todos los perfiles consumen la baseline canónica.                                                      |
| `NADR-F17BIS-27`                   | **Dependencia directa:** define la semántica común de los resultados producidos por los distintos perfiles.                                                            |
| `NADR-F17BIS-28`                   | **Dependencia directa:** define la evidencia e identity chain necesarias para distinguir ejecuciones realizadas bajo perfiles diferentes.                              |
| `NADR-F17BIS-30`                   | **Influencia:** el enforcement de CI puede seleccionar perfiles y utilizar sus resultados, pero debe conservar la semántica y cobertura declaradas por cada perfil.    |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | Las tareas que materializan los perfiles concretos y su integración operacional son gobernadas por el Execution Plan de Fase 6.                                        |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** cuál es el production pipeline ni el sujeto de verificación (responsabilidad de `NADR-F17BIS-25`).

* **No gobierna** la materialización ni la integridad de la baseline (responsabilidad de `NADR-F17BIS-26`).

* **No gobierna** la semántica de `PASS`, `REGRESSION / DIVERGENCE`, `BASELINE_INTEGRITY_FAILURE` o `EXECUTION_FAILURE` (responsabilidad de `NADR-F17BIS-27`).

* **No gobierna** la identity chain ni la persistencia de evidencia (responsabilidad de `NADR-F17BIS-28`).

* **No gobierna** el algoritmo, costos, thresholds, pesos o criterios científicos de evaluación (responsabilidad de `NADR-F17BIS-19`, `NADR-F17BIS-22` y los contratos científicos correspondientes).

* **No establece** por sí mismo una política de frecuencia como PR, merge, nightly u otra modalidad temporal.

* **No establece** la configuración concreta del workflow de CI.

* **No gobierna** branch protection ni merge enforcement (responsabilidad de `NADR-F17BIS-30`).

* **No prescribe** tareas de implementación ni Definition of Done; dichas responsabilidades pertenecen al Execution Plan de Fase 6.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.