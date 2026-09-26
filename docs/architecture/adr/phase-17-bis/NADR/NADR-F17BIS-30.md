# NADR-F17BIS-30: CI Enforcement & Merge Protection

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-30`

* **Título:** CI Enforcement & Merge Protection

* **Clase de Decisión:** `GOVERNANCE / OPERATIONAL`

* **Nivel de Cumplimiento:** `MANDATORY`

* **Versión:** 1.0.0

* **Ciclo de Vida:** `FROZEN`

* **Fecha de Emisión:** 2026-09-25

* **Fecha de Congelamiento:** 2026-09-25

* **Vigente Desde:** Fase 6 (Continuous Verification)

* **Autoridad:** Architecture Board

* **Responsable Técnico:** Equipo de Arquitectura / Fase 6

* **Capacidad Arquitectónica:** CAP-11 (CI Enforcement & Merge Protection) — Establece la obligación constitucional de que la integración de cambios esté condicionada por el cumplimiento verificable de los controles obligatorios de Continuous Verification, distinguiendo explícitamente entre ejecución de verificación y enforcement efectivo sobre la integración.

* **Evidencia Forense:** `C5-R09` (HITO 0.4.4, P0), `Regla 4` (HITO 0.5 Deliverable 3, MUST), `GAP-C5-04` (HITO 0.5 Deliverable 1, P0), `E-6.3-004`, `GAP-6.3-04`, `DC-6.15`, `D8` (ADR_F17_BIS_06 v1.2.0)

* **Referencias Cruzadas:**

  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-25` (Verification Boundary & Production Subject), `NADR-F17BIS-26` (Canonical Baseline Materialization & Integrity), `NADR-F17BIS-27` (Verification Outcome & Failure Semantics), `NADR-F17BIS-28` (Evidence, Identity Chain & Reproducibility), `NADR-F17BIS-29` (Continuous Verification Execution Profiles)

  * **Influencia:** `PHASE_17BIS_FASE6_EXECUTION_PLAN`, CI/CD configuration, operational verification

  * **Conflictúa con:** Cualquier mecanismo que permita integrar cambios sin satisfacer los controles obligatorios de Continuous Verification, o que presente ejecución de CI como equivalente a enforcement efectivo sin barrera de integración demostrable.

  * **Reemplaza a:** N/A

### Evidencia epistemológica

La evidencia disponible demuestra la **obligación arquitectónica de enforcement**, pero no demuestra por sí misma que la protección server-side de ramas se encuentre actualmente activada.

Por tanto:

> **Estado actual de activación server-side: NO DEMOSTRADO.**

La activación efectiva constituye una condición verificable de cumplimiento y no una consecuencia automática de la existencia de workflows, jobs o nombres de checks dentro del repositorio.

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin enforcement, la Continuous Verification puede ejecutarse sin constituir una barrera efectiva de integración. Evidencia: `E-6.3-004`, `GAP-6.3-04`, `DC-6.15`.

* **Mantenibilidad:** 4 — La ausencia de una frontera explícita entre ejecución y enforcement permite divergencias entre intención y operación. Evidencia: `GAP-C5-04`.

* **Recuperabilidad:** 4 — Un cambio no controlado puede integrarse aun cuando la verificación haya producido un resultado inválido. Evidencia: `C5-R09`.

* **Seguridad:** 5 — La protección de la frontera de integración constituye un control de gobernanza sobre cambios. Evidencia: `Regla 4` (HITO 0.5 Deliverable 3).

* **Financiero:** 3 — Cambios regresivos integrados pueden producir ciclos posteriores de diagnóstico, retrabajo y ejecución innecesaria.

* **Total Score:** 21/25

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La integración de cambios MUST estar condicionada por el cumplimiento verificable de los controles obligatorios de Continuous Verification, y ningún mecanismo declarativo, workflow o resultado de CI podrá considerarse enforcement efectivo sin una barrera de integración demostrable.**

En consecuencia:

* La ejecución de CI y el enforcement sobre la integración son capacidades distintas.

* Un workflow existente no constituye por sí mismo una protección de merge.

* Un job ejecutado correctamente no demuestra que su resultado sea requerido para integrar cambios.

* Un Required Status Check configurado únicamente en el repositorio tampoco demuestra necesariamente su activación efectiva en el sistema de control remoto.

* La evidencia de enforcement debe demostrar la relación:

```text
Continuous Verification
        ↓
CI Result
        ↓
Required Check
        ↓
Merge Protection
        ↓
Integration Decision
```

* La ausencia de evidencia suficiente debe conservar el estado **NO DEMOSTRADO** y no transformarse en una afirmación de cumplimiento.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La existencia de un mecanismo de Continuous Verification no garantiza que sus resultados controlen realmente la integración de cambios.

Existe una diferencia fundamental entre:

```text
VERIFICACIÓN
"el sistema produjo un resultado"
(propiedad de ejecución)
```

y:

```text
ENFORCEMENT
"ese resultado controla efectivamente la integración"
(propiedad de gobernanza operacional)
```

La primera es una propiedad de ejecución.

La segunda es una propiedad de gobernanza operacional.

La arquitectura de Fase 6 requiere que ambas sean trazables sin depender de convenciones humanas, interpretación manual o intención declarada.

La ausencia de enforcement efectivo permitiría el siguiente estado:

```text
Cambio
  ↓
CI
  ↓
Continuous Verification
  ↓
REGRESSION / FAILURE
  ↓
Merge todavía permitido
```

Ese estado contradice el objetivo de Continuous Verification como control de integración.

### 4.2 Manifestaciones concretas identificadas por la auditoría

* **`C5-R09` (HITO 0.4.4, P0):** Protección de Ramas vía Required Status Checks. La evidencia de HITO 0.4.4 establece como requisito P0 que los controles obligatorios de estado deben constituir una barrera para la integración. **Interpretación:** la protección frente a integración no controlada es un requisito arquitectónico preexistente y no una decisión creada exclusivamente durante Fase 6.

* **`Regla 4` (HITO 0.5 Deliverable 3, MUST):** CI Enforcement declarativo obligatorio. HITO 0.5 Deliverable 3 establece que el enforcement declarativo de CI debe impedir la integración cuando los controles obligatorios no son satisfechos. **Interpretación:** la arquitectura no considera suficiente la mera ejecución de los controles; exige una relación normativa entre resultado y capacidad de integración.

* **`GAP-C5-04` (HITO 0.5 Deliverable 1, P0):** Inexistencia de barreras de control remotas demostradas. La Gap Matrix de HITO 0.5 identifica este gap como P0 asociado a la ausencia de barreras remotas demostradas. **Interpretación:** la ausencia histórica de enforcement efectivo es un gap reconocido desde Fase 0.

* **`E-6.3-004` / `GAP-6.3-04` (HITO 6.3, P1):** Enforcement NO DEMOSTRADO. HITO 6.3 demuestra la existencia de infraestructura CI denominada como regression gate, pero también demuestra que dicha infraestructura no constituye por sí sola evidencia suficiente de enforcement efectivo. Branch protection y required status checks son configuración del servidor GitHub, no del repositorio. No hay evidencia de que el job `regression-gates` bloquee merges a main.

* **`DC-6.15` (HITO 6.4 / ADR_F17_BIS_06):** Branch protection / enforcement clasificado como NO DEMOSTRADO. HITO 6.4 clasifica este Decision Candidate como NO DEMOSTRADO debido a que la configuración efectiva reside fuera del perímetro verificable del repositorio. Resuelto por `ADR_F17_BIS_06` v1.2.0 D8 como obligación arquitectónica con evidencia externa requerida.

* **`D8` (ADR_F17_BIS_06 v1.2.0):** Protección de Integridad y Enforcement. El ADR de Fase 6 establece que el enforcement es obligatorio y que su cumplimiento requiere evidencia externa cuando la configuración efectiva reside en infraestructura server-side. La obligación de enforcement fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0) y permaneció pendiente durante Fases 1-5; Fase 6 asume su resolución.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Enforcement como capacidad independiente

1. Continuous Verification **MUST** distinguir entre ejecución de verificación y enforcement sobre la integración.

2. La existencia de una ejecución exitosa de CI **MUST NOT** considerarse evidencia suficiente de enforcement.

3. La existencia de un workflow, job, check o resultado de verificación **MUST NOT** considerarse por sí sola una garantía de protección de integración.

### 5.2 Integración condicionada

4. La integración de cambios **MUST** estar condicionada al cumplimiento de los controles de Continuous Verification declarados como obligatorios para el contexto de integración correspondiente.

5. Un resultado que represente una condición de bloqueo **MUST** impedir la integración cuando dicho resultado corresponda a un control requerido para esa integración.

6. Un cambio **MUST NOT** considerarse arquitectónicamente conforme para integración cuando los controles obligatorios no hayan sido satisfechos.

### 5.3 Relación entre resultado y barrera

7. La relación entre resultado de Continuous Verification y decisión de integración **MUST** ser determinista y demostrable.

8. La arquitectura **MUST NOT** depender de intervención manual para transformar un resultado obligatorio de Continuous Verification en una condición de bloqueo.

9. La ausencia, invalidez o indisponibilidad de un control obligatorio **MUST NOT** interpretarse silenciosamente como cumplimiento.

10. Un control que no pueda demostrar su ejecución o su estado requerido **MUST NOT** producir implícitamente una condición equivalente a PASS.

### 5.4 Enforcement remoto

11. Cuando la capacidad efectiva de protección de integración resida fuera del perímetro del repositorio, su cumplimiento **MUST** ser verificable mediante evidencia externa apropiada.

12. La documentación declarativa del repositorio **MUST NOT** presentarse como evidencia suficiente de activación efectiva de una protección administrada externamente.

13. La arquitectura **MUST** distinguir entre:

    * intención declarada;
    * configuración declarada;
    * configuración activa;
    * enforcement efectivo.

### 5.5 Estado epistemológico

14. Cuando la activación efectiva de un mecanismo de enforcement no pueda ser demostrada, su estado **MUST** permanecer explícitamente como `NO DEMOSTRADO`.

15. La ausencia de evidencia de enforcement **MUST NOT** ser sustituida por inferencias derivadas del nombre de workflows, jobs, checks, documentación o convenciones operativas.

16. La declaración de cumplimiento de la capacidad de enforcement **MUST** requerir evidencia suficiente de la barrera efectiva de integración.

### 5.6 Trazabilidad de cumplimiento

17. La evidencia de enforcement **MUST** permitir establecer la correspondencia entre el control de Continuous Verification, su resultado y la condición de integración que dicho resultado gobierna.

18. La evidencia **MUST** distinguir entre controles ejecutados y controles efectivamente requeridos para la integración.

19. La configuración de enforcement **MUST** ser auditable sin depender exclusivamente de conocimiento tácito del equipo.

### 5.7 Ausencia de mecanismos alternativos

20. No podrán introducirse mecanismos paralelos que reproduzcan parcialmente el enforcement definido por esta arquitectura y produzcan una semántica distinta de integración.

21. La implementación de enforcement **MUST** reutilizar los resultados y contratos establecidos por los mecanismos normativos de Continuous Verification.

22. El enforcement **MUST NOT** introducir una segunda definición de PASS, REGRESSION, FAILURE o INTEGRITY FAILURE.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Continuous Verification pasa de ser exclusivamente una capacidad de diagnóstico a constituir una capacidad gobernable de integración.

* Se establece una frontera explícita entre:

  * ejecución;
  * resultado;
  * required check;
  * protección;
  * decisión de integración.

* Se elimina la equivalencia incorrecta:

```text
CI existe ≠ Merge protegido
```

* La arquitectura puede demostrar cuándo la capacidad de enforcement está realmente satisfecha.

* La ausencia de configuración externa deja de ocultarse detrás de evidencia únicamente declarativa.

* La integración queda vinculada a los contratos definidos por `NADR-F17BIS-25` a `NADR-F17BIS-29`.

* El cumplimiento completo depende parcialmente de infraestructura externa al repositorio.

* La evidencia de enforcement deberá mantenerse disponible para auditorías posteriores.

* Los cambios administrativos sobre protección de ramas pasan a formar parte del perímetro de gobernanza aunque no sean código del proyecto.

* No podrá declararse la capacidad de enforcement como satisfecha únicamente mediante tests locales.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

### Verification (estática/mecánica)

* Verificación de que los controles declarados como obligatorios estén identificados.

* Verificación de que exista correspondencia entre dichos controles y el proceso de integración.

* Verificación de que la documentación no confunda CI con enforcement.

* Verificación de que la configuración declarativa no sea presentada como evidencia de activación efectiva.

* Verificación de que los estados `NO DEMOSTRADO` estén preservados cuando falte evidencia externa.

* Verificación de que no existan mecanismos alternativos con semántica divergente.

* Verificación de que la relación entre resultado y condición de integración esté documentada.

### Validation (dinámica/comportamental)

* Demostración de que un resultado bloqueante impide la integración cuando el control es requerido.

* Demostración de que un resultado conforme permite continuar cuando las demás condiciones obligatorias también son satisfechas.

* Demostración de que la ausencia o invalidación de un required check no produce un PASS implícito.

* Demostración de que la protección permanece efectiva frente a cambios en el contenido verificado.

* Demostración de que la evidencia resultante permite reconstruir qué control gobernó la decisión de integración.

La validación dinámica debe distinguir explícitamente:

```text
CI execution
        ≠
Required Check
        ≠
Merge Protection
```

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto                                | Relación |
| :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ADR_F17_BIS_MASTER`               | Este NADR materializa la gobernanza global de la baseline y Continuous Verification definida por el ADR Maestro. |
| `ADR_F17_BIS_06` v1.2.0            | Este NADR materializa D8 (Protección de Integridad y Enforcement) y DC-6.15. |
| `NADR-F17BIS-25`                   | **Dependencia directa:** define el sujeto y boundary de verificación cuyos resultados son gobernados por el enforcement. |
| `NADR-F17BIS-26`                   | **Dependencia directa:** define la referencia física y su integridad, cuya protección es precondición del enforcement. |
| `NADR-F17BIS-27`                   | **Dependencia directa:** define el significado de los resultados que el enforcement consume para decidir la integración. |
| `NADR-F17BIS-28`                   | **Dependencia directa:** define la evidencia e identidad que permiten demostrar qué control gobernó la decisión de integración. |
| `NADR-F17BIS-29`                   | **Dependencia directa:** define los perfiles válidos de ejecución cuyos resultados pueden ser requeridos para la integración. |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | **Influencia:** materializa las condiciones y tareas necesarias para implementar y verificar el enforcement. |
| CI/CD Configuration                  | **Influencia:** materializa los controles operacionales definidos por la arquitectura. |
| Configuración server-side de integración | **Influencia:** materializa la protección efectiva cuando reside fuera del repositorio. |
| Exit Review Evidence Log             | **Influencia:** conserva la evidencia de cumplimiento de la capacidad. |
| Deferred Findings Register           | **Influencia:** registra cualquier incumplimiento residual que permanezca fuera del alcance de la ejecución actual. |

### Relación bidireccional obligatoria

Los artefactos dependientes de este NADR **MUST** declarar su dependencia cuando incorporen requisitos de enforcement o merge protection.

Este NADR **MUST NOT** absorber responsabilidades propias de `NADR-F17BIS-25` a `NADR-F17BIS-29`.

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** cuál es el production pipeline ni el sujeto de verificación (responsabilidad de `NADR-F17BIS-25`).

* **No gobierna** la materialización ni la integridad de la baseline (responsabilidad de `NADR-F17BIS-26`).

* **No gobierna** la semántica de `PASS`, `REGRESSION / DIVERGENCE`, `BASELINE_INTEGRITY_FAILURE` o `EXECUTION_FAILURE` (responsabilidad de `NADR-F17BIS-27`).

* **No gobierna** la identity chain ni la persistencia de evidencia (responsabilidad de `NADR-F17BIS-28`).

* **No gobierna** los perfiles de ejecución ni su cobertura (responsabilidad de `NADR-F17BIS-29`).

* **No gobierna** el algoritmo, costos, thresholds, pesos o criterios científicos de evaluación (responsabilidad de `NADR-F17BIS-19`, `NADR-F17BIS-22` y los contratos científicos correspondientes).

* **No gobierna** la frecuencia concreta de ejecución de cada perfil.

* **No gobierna** el workflow concreto de CI: no define jobs, stages, comandos, runners, archivos ni tecnologías específicas.

* **No gobierna** la configuración administrativa concreta de la plataforma de integración.

* **No prescribe** tareas de implementación ni Definition of Done; dichas responsabilidades pertenecen al Execution Plan de Fase 6.

---

## Nota de Gobernanza

Este NADR establece la obligación constitucional de que Continuous Verification tenga una barrera de integración demostrable.

No declara que dicha barrera esté actualmente activa.

Por tanto, hasta disponer de evidencia server-side suficiente:

> **CAP-11 — Enforcement = NO DEMOSTRADO.**

La posterior demostración de cumplimiento constituye evidencia de ejecución/validación, no una modificación retroactiva de este NADR.

Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.