# NADR-F17-BIS-23: Scientific Calibration, Dataset Independence & Experimental Provenance

## 1. METADATA

* **Decision ID:** `NADR-F17-BIS-23`
* **Título:** Scientific Calibration, Dataset Independence & Experimental Provenance
* **Clase de Decisión:** `DATA / OPERATIONAL / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.2.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 17-BIS — Fase 5 (Baseline Certification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-F5-04 (Scientific Calibration, Dataset Independence & Provenance) — Establece las reglas normativas para la calibración empírica de parámetros de evaluación topológica, la independencia de datasets basada en content identity, el provenance experimental reproducible, el Evaluation Provenance Record, y el congelamiento de parámetros antes de la certificación de la baseline.
* **Evidencia Forense:** `E-5.4-018` (ausencia de infraestructura de calibración), `E-5.4-019` (ningún parámetro calibrado empíricamente), `E-5.4-020` (7 identidades no suficientes para partición clásica), `E-5.4-021` (ausencia de provenance de calibration runs), `GAP-5.4-005`, `GAP-5.4-006`, `GAP-5.4-007`, HITO 5.1 (duplicados físicos G1/G2), HITO 5.3 Clasificación C (thresholds no transferibles entre motores)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_05` (FROZEN, D5/D6/D7), `NADR-F17-BIS-20` (Canonical Corpus Qualification), `NADR-F17-BIS-21` (Ground Truth Eligibility, Migration & Sealing), `NADR-F17-BIS-22` (Canonical Topological Evaluation Configuration), `NADR-F17BIS-18` (Taxonomía de Criticidad), `NADR-F17BIS-19` (Regresión Topológica Graduada)
  * **Influencia:** `NADR-F17-BIS-24` (Certification Tooling Integrity), `PHASE_17BIS_FASE5_EXECUTION_PLAN`
  * **Conflictúa con:** Calibración sobre los mismos datos de evaluación, tuning sin protocolo, calibración sin provenance, calibración sin reproducibilidad, calibración sin independencia de datasets.
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 30 reglas normativas en 8 dominios. |
| 1.1.0 | 2026-09-05 | Versión combinada: (1) Agregado Evaluation Provenance (R31); (2) Referencia HITO 5.1 G1/G2; (3) Referencia HITO 5.3 Clasificación C; (4) Clase de Decisión DATA / OPERATIONAL / GOVERNANCE. Total: 31 reglas. |
| 1.2.0 | 2026-09-05 | **FROZEN** **Hardening científico:** (1) R12: eliminada equivalencia normativa 20 identidades = robustez estadística; (2) R26: separada calibration validity de certification eligibility en tres conceptos distintos; (3) R20: rediseñada experiment identity (experiment identity ≠ parameter identity ≠ result identity); (4) R8: reproducibilidad reformulada para métodos estocásticos (seed, configuración de búsqueda); (5) R19: agregada referencia al protocolo aprobado; (6) R15: terminología de selección aclarada; (7) R9-R13: "content identity" consistente; (8) R23-R25: inmutabilidad de parámetros congelados (nueva configuración = nueva identidad = nueva certificación); (9) R31: independiente ≠ aislado (trazable hacia calibración); (10) Consecuencias: intensidad de leakage ajustada; (11) R14: "Ciclo de Calibración" → "Experimental Lifecycle". Total: 31 reglas normativas en 8 dominios. |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin calibración empírica, los parámetros de evaluación (pesos de criticidad, thresholds de NSS) quedan como propuestas heurísticas no validadas. La certificación de la baseline queda sin fundamento científico.
* **Mantenibilidad:** 4 — Sin protocolo de calibración definido, la evolución de parámetros es ambigua y propensa a tuning ad-hoc.
* **Recuperabilidad:** 4 — Sin provenance de calibration runs, la recuperación ante corrupción o sustitución de parámetros es imposible.
* **Seguridad:** 2 — No hay exposición directa a vulnerabilidades de seguridad. El riesgo es de integridad científica.
* **Financiero:** 3 — Sin calibración, la certificación de la baseline queda bloqueada, generando costo de oportunidad significativo.
* **Total Score: 18/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La calibración empírica de parámetros de evaluación topológica se ejecuta exclusivamente mediante un protocolo científico definido que establece el experimento, la función objetivo, el espacio de parámetros, la independencia de datasets y el criterio de aceptación antes de elegir algoritmo de búsqueda, con provenance reproducible, parameter freeze verificable, y Evaluation Provenance Record independiente pero trazable hacia la calibración.**

En consecuencia:
* Ninguna calibración puede ejecutarse sin un protocolo de calibración definido y aprobado.
* Ninguna calibración puede utilizar los mismos datos para calibrar parámetros y para evaluación final.
* Ninguna calibración puede producir resultados de certificación sin provenance reproducible.
* Ningún parámetro puede ser congelado sin haber completado el ciclo completo de calibración, validación y evaluación final.
* La evaluación final debe registrar un Evaluation Provenance Record independiente pero trazable hacia la calibración que produjo los parámetros congelados.
* El tuning ad-hoc sin protocolo **MUST NOT** ser considerado calibración científica.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de certificación de la baseline requiere parámetros de evaluación calibrados empíricamente. Sin embargo, la auditoría forense (HITO 5.4) demostró que el estado actual del repositorio presenta cuatro clases de deficiencias que impiden la calibración científica:

1. **Ausencia de infraestructura de calibración:** No existe partición de datasets, provenance de calibration runs, capacidad funcional de análisis estadístico reproducible, ni protocolo de calibración empírica ejecutable.

2. **Ningún parámetro calibrado empíricamente:** Todos los parámetros actuales (pesos de criticidad, thresholds de NSS) son normativos o heurísticos. Ninguno ha sido validado empíricamente contra el corpus canónico.

3. **Corpus insuficiente para partición clásica:** El corpus actual contiene 7 identidades únicas candidatas, lo cual no es suficiente para una partición clásica train/validation/holdout estadísticamente robusta. El rango arquitectónico objetivo es 20-30 documentos.

4. **Ausencia de provenance de calibration runs:** No existe sistema de tracking de calibration runs. No hay registro de corpus_identity, metric_configuration, parameters, result, timestamp.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-5.4-018` (P1 — Alto):** No existe partición de datasets, provenance de calibration runs, capacidad funcional de análisis estadístico reproducible, ni protocolo de calibración empírica ejecutable.

* **`E-5.4-019` (P1 — Alto):** Ningún parámetro ha sido calibrado empíricamente. Todos son normativos o heurísticos. La validación empírica de pesos de criticidad (NADR-18 §5.3 R12 Condición B) está pendiente.

* **`E-5.4-020` (P2 — Medio):** Con 7 identidades únicas, un esquema clásico train/validation/holdout no resulta estadísticamente robusto. El rango arquitectónico objetivo es 20-30 documentos.

* **`E-5.4-021` (P1 — Alto):** No existe sistema de tracking de calibration runs. No hay registro de corpus_identity, metric_configuration, parameters, result, timestamp.

* **HITO 5.1 (G1/G2):** Duplicados físicos identificados por SHA-256. Grupo G1: 4 copias del mismo contenido (`84891f98...`) distribuidas en diferentes rutas y nombres de archivo. Grupo G2: 2 copias del mismo contenido (`21b9283a...`) en diferentes rutas. La separación de datasets debe basarse en content identity (SHA-256), no filename, para evitar leakage por duplicados físicos que tienen el mismo contenido pero diferentes nombres.

* **HITO 5.3 Clasificación C (Comparable but Non-Equivalent):** Los thresholds de NSS no son transferibles entre motores. ZhangShashaEngine y StructuralTopologyMetric (APTED) no calculan la misma función de distancia bajo la configuración actual. Todo threshold debe estar asociado a una configuración canónica específica definida por NADR-F17-BIS-22.

* **`GAP-5.4-005` (P1):** Ausencia de infraestructura de calibración. Justifica R4-R8 (protocolo de calibración).
* **`GAP-5.4-006` (P1):** Ningún parámetro calibrado empíricamente. Justifica R14-R17 (experimental lifecycle).
* **`GAP-5.4-007` (P2):** Partición no robusta con 7 identidades. Justifica R9-R13 (independencia de datasets).

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Definiciones de Calibración, Validación y Evaluación Final

1. La arquitectura distingue tres conceptos operacionalmente distintos: CALIBRATION (genera y evalúa parámetros candidatos conforme al espacio de búsqueda), VALIDATION (determina la elegibilidad y selección de candidatos conforme al criterio predefinido), y FINAL EVALUATION (produce evidencia de baseline certificada con parámetros congelados).

2. Los resultados de FINAL EVALUATION **MUST NOT** participar en la selección de parámetros. La contaminación de la evaluación final por el proceso de calibración **MUST NOT** ser permitida.

3. CALIBRATION, VALIDATION y FINAL EVALUATION **MUST** ser ejecutadas como fases secuenciales distintas. La ejecución simultánea o la mezcla de fases **MUST NOT** ser permitida.

### 5.2 Protocolo de Calibración Empírica

4. Toda calibración **MUST** ser gobernada por un protocolo de calibración definido antes de la ejecución. La calibración sin protocolo **MUST NOT** ser permitida.

5. El protocolo de calibración **MUST** definir, como mínimo: la variable a calibrar, el ground truth observable, la función objetivo, el espacio de parámetros, las restricciones, la unidad de evaluación, la independencia de datasets, y el criterio de aceptación.

6. El protocolo de calibración **MUST** definir el experimento antes de elegir el algoritmo de búsqueda. La selección del algoritmo de búsqueda (Grid Search, Bayesian Optimization, LOOCV, bootstrap, u otro) **MUST** ser posterior a la definición del experimento.

7. El protocolo de calibración **MUST** ser aprobado antes de la ejecución de la calibración. La calibración sin protocolo aprobado **MUST NOT** ser permitida.

8. El protocolo de calibración **MUST** capturar las condiciones necesarias para reproducir el resultado: protocolo/versión, corpus identity, configuración del motor, parámetros iniciales y restricciones, seed cuando exista aleatoriedad, y configuración del algoritmo de búsqueda cuando aplique. La reproducibilidad con configuración controlada **MUST** ser garantizada. El determinismo absoluto **MUST NOT** ser asumido como requisito si el protocolo utiliza métodos estocásticos con seed controlado.

### 5.3 Independencia de Datasets

9. La separación de datasets **MUST** basarse en cryptographic content identity (SHA-256), no en filename ni en document_id. Documentos con el mismo SHA-256 **MUST NOT** aparecer en particiones diferentes.

10. El conjunto de calibración (calibration dataset) **MUST** ser disjunto del conjunto de evaluación final (final evaluation dataset) a nivel de cryptographic content identity. La intersección `Calibration dataset ∩ Final evaluation dataset` **MUST** ser vacía a nivel de SHA-256.

11. La política de partición de datasets **MUST** ser definida por el protocolo de calibración. Este NADR no prescribe un método específico de partición (LOOCV, bootstrap, holdout, u otro).

12. Con un corpus inferior a 20 identidades únicas, una partición clásica train/validation/holdout **MUST NOT** ser presumida estadísticamente robusta únicamente en virtud de la partición. Su utilización **MUST** ser explícitamente justificada por el protocolo de calibración. El alcance de 20-30 identidades establecido por ADR_F17_BIS_05 constituye el objetivo mínimo de corpus para la fase, pero no constituye por sí mismo una garantía de suficiencia estadística.

13. La política de partición **MUST** ser documentada en el protocolo de calibración. La partición sin documentación **MUST NOT** ser permitida.

### 5.4 Experimental Lifecycle

14. El proceso de obtención y certificación de parámetros **MUST** completar las siguientes fases secuenciales: CALIBRATION → VALIDATION → PARAMETER FREEZE → FINAL EVALUATION. La omisión de cualquier fase **MUST NOT** ser permitida.

15. La fase de CALIBRATION **MUST** generar y evaluar un conjunto de parámetros candidatos conforme al espacio de búsqueda definido por el protocolo. La selección de parámetros **MUST** ocurrir en la fase de VALIDATION, no en la fase de CALIBRATION.

16. La fase de VALIDATION **MUST** verificar la generalización de los parámetros candidatos sobre un conjunto de validación disjunto del conjunto de calibración a nivel de cryptographic content identity.

17. La fase de FINAL EVALUATION **MUST** producir evidencia de baseline certificada sobre un conjunto de evaluación final disjunto del conjunto de calibración y del conjunto de validación a nivel de cryptographic content identity.

### 5.5 Provenance Experimental

18. Toda calibración que produzca parámetros candidatos **MUST** registrar un Calibration Provenance Record con, como mínimo: (1) corpus_identity (SHA-256 del manifest), (2) metric_configuration (hash de configuración), (3) parameters (pesos/thresholds), (4) result (scores), (5) timestamp (fecha de ejecución).

19. El Calibration Provenance Record **MUST** ser suficiente para reproducir la calibración. El record **MUST** referenciar el protocolo de calibración aprobado y las condiciones necesarias de ejecución conforme a R8. La calibración sin provenance suficiente **MUST NOT** producir resultados de certificación.

20. La arquitectura distingue tres tipos de identidad en el contexto experimental: (a) Experiment identity, derivada de los elementos que describen cómo se ejecutó el experimento (corpus_identity, protocol_identity/versión, metric_configuration, search_configuration, seed cuando aplique); (b) Parameter identity, derivada del conjunto concreto de parámetros congelados; (c) Result identity, derivada del resultado producido por esa ejecución. El timestamp **MUST NOT** ser considerado un mecanismo de identidad de experimento.

21. La arquitectura distingue Artifact provenance (identidad de artefactos) de Calibration-run provenance (identidad de experimentos). La confusión de ambos tipos de provenance **MUST NOT** ser permitida.

22. No se prescribe infraestructura específica de provenance (MLflow, PostgreSQL, u otra). La implementación del Calibration Provenance Record pertenece al Execution Plan.

### 5.6 Parameter Freeze

23. Los parámetros calibrados **MUST** ser congelados (parameter freeze) antes de la certificación de la baseline. La certificación sin parameter freeze **MUST NOT** ser permitida.

24. El parameter freeze **MUST** ser verificable: los parámetros congelados **MUST** ser identificables mediante un hash criptográfico determinista (parameter identity conforme a R20).

25. Los parámetros congelados **MUST** ser inmutables. Toda nueva configuración de parámetros constituye una nueva parameter identity y **MUST** requerir una nueva línea de certificación. La modificación de parámetros congelados sin nueva certificación **MUST NOT** ser permitida.

### 5.7 Condiciones de Validez Científica

26. La arquitectura distingue tres conceptos de validez: (a) Calibration validity: una calibración **MUST** ser considerada científicamente válida si fue ejecutada conforme a un protocolo aprobado, utilizó datasets independientes a nivel de cryptographic content identity, produjo un Calibration Provenance Record suficiente, y completó las fases CALIBRATION y VALIDATION. (b) Parameter eligibility: un conjunto de parámetros **MUST** ser considerado elegible para freeze si sobrevivió la fase de VALIDATION conforme al criterio de aceptación. (c) Certification eligibility: una certificación **MUST** ser considerada elegible si los parámetros congelados fueron utilizados en una FINAL EVALUATION independiente. La calibration validity **MUST NOT** depender del éxito de la certificación.

27. El tuning ad-hoc sin protocolo **MUST NOT** ser considerado calibración científica. La distinción entre calibración y tuning **MUST** ser verificable.

28. Un parámetro calibrado empíricamente **MUST** ser distinguible de un parámetro normativo o heurístico. La confusión de tipos de parámetros **MUST NOT** ser permitida.

### 5.8 Relación con la Configuración Canónica y Evaluation Provenance

29. Toda calibración **MUST** utilizar la configuración canónica del motor de evaluación definida por NADR-F17-BIS-22. La calibración con configuración no canónica **MUST NOT** producir resultados de certificación.

30. Los thresholds de NSS calibrados **MUST** estar asociados a la configuración canónica específica utilizada en la calibración. No existe NSS_THRESHOLD universal.

31. La evaluación final de la baseline **MUST** registrar un Evaluation Provenance Record independiente del Calibration Provenance Record como registro de evidencia. El Evaluation Provenance Record **MUST** incluir, como mínimo: corpus_identity, configuration_identity, frozen_parameters_identity, result, y timestamp. El Evaluation Provenance Record **MUST** ser trazable hacia la calibración que produjo los parámetros congelados: "independiente" significa registro independiente, no ausencia de relación. El Evaluation Provenance Record **MUST** poder demostrar que los parámetros congelados provienen de una calibración/validación específica.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **Protocolo de calibración definido:** Toda calibración se ejecuta conforme a un protocolo definido y aprobado. Esto elimina el riesgo de tuning ad-hoc y garantiza que la calibración sea científicamente válida.
* **Independencia de datasets garantizada:** La separación de datasets se basa en cryptographic content identity (SHA-256), no en filename ni document_id. Esto elimina el riesgo de leakage derivado de duplicados físicos con contenido idéntico que aparezcan bajo distintos filenames (HITO 5.1 G1/G2).
* **Provenance reproducible:** Toda calibración produce un Calibration Provenance Record suficiente para reproducir la calibración, incluyendo referencia al protocolo aprobado y condiciones de ejecución. Esto elimina el riesgo de calibración no reproducible.
* **Parameter freeze inmutable:** Los parámetros congelados son inmutables. Toda nueva configuración de parámetros constituye una nueva parameter identity y requiere una nueva línea de certificación. Esto garantiza que la certificación sea estable y verificable.
* **Experimental lifecycle completo:** Toda calibración completa el ciclo CALIBRATION → VALIDATION → PARAMETER FREEZE → FINAL EVALUATION. Esto elimina el riesgo de certificación con parámetros no validados.
* **Configuración canónica:** Toda calibración utiliza la configuración canónica del motor de evaluación. Los thresholds de NSS son específicos de la configuración canónica (HITO 5.3 Clasificación C). Esto elimina el riesgo de calibración con configuración no canónica.
* **Evaluation Provenance independiente pero trazable:** La evaluación final registra un Evaluation Provenance Record independiente como registro de evidencia, pero trazable hacia la calibración que produjo los parámetros congelados. Esto garantiza la trazabilidad completa de la certificación y habilita la auditoría forense de la evaluación final.
* **Calibration validity separada de certification eligibility:** Una calibración puede ser científicamente válida aunque la validación rechace todos los candidatos y no haya certificación. Esto evita la contaminación retroactiva de la validez científica de la calibración.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que toda calibración tiene un protocolo de calibración aprobado.
  * Verificación de que la separación de datasets se basa en cryptographic content identity (SHA-256).
  * Verificación de que el conjunto de calibración es disjunto del conjunto de evaluación final a nivel de SHA-256.
  * Verificación de que toda calibración produce un Calibration Provenance Record con los 5 campos mínimos y referencia al protocolo aprobado.
  * Verificación de que los parámetros calibrados están congelados mediante parameter identity (hash criptográfico).
  * Verificación de que la configuración utilizada en la calibración es la configuración canónica definida por NADR-F17-BIS-22.
  * Verificación de que la evaluación final produce un Evaluation Provenance Record independiente pero trazable hacia la calibración.
  * Verificación de que toda nueva configuración de parámetros constituye una nueva parameter identity.

* **Validation (dinámica/comportamental):**
  * Ejecución del protocolo de calibración sobre el corpus canónico, verificando que la calibración se ejecuta correctamente.
  * Verificación de la independencia de datasets: ningún documento con el mismo SHA-256 aparece en particiones diferentes.
  * Verificación de la reproducibilidad: la misma ejecución del protocolo con las mismas condiciones produce los mismos resultados. Para métodos estocásticos, verificación de que el seed controlado produce reproducibilidad.
  * Verificación del parameter freeze: los parámetros congelados son identificables mediante parameter identity (hash criptográfico).
  * Verificación de que toda nueva configuración de parámetros requiere una nueva línea de certificación.
  * Verificación de que el experimental lifecycle completo CALIBRATION → VALIDATION → PARAMETER FREEZE → FINAL EVALUATION se completa.
  * Verificación de que el Evaluation Provenance Record es independiente pero trazable hacia el Calibration Provenance Record.
  * Verificación de que la calibration validity no depende del éxito de la certificación.
  * Verificación de que el corpus cualificado puede ser consumido por el proceso de certificación de Fase 5 sin violar las invariantes definidas por este NADR y los NADRs dependientes.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro §5 (Determinismo y Reproducibilidad) y §6 (Golden Corpus Driven Development). |
| `ADR_F17_BIS_05` | Este NADR implementa D5 (Scientific Calibration), D6 (Experimental Provenance) y D7 (Dataset Independence) del ADR de Fase 5. |
| `NADR-F17BIS-20` | **Dependencia directa:** Este NADR depende de la cualificación del corpus establecida por NADR-20. La partición de datasets se basa en el corpus canónico cualificado. |
| `NADR-F17-BIS-21` | **Dependencia directa:** Este NADR depende de los oráculos sellados establecidos por NADR-21. La calibración se ejecuta contra oráculos sellados. |
| `NADR-F17-BIS-22` | **Dependencia directa:** Este NADR depende de la configuración canónica del motor de evaluación establecida por NADR-22. Los thresholds de NSS calibrados están asociados a la configuración canónica específica. |
| `NADR-F17BIS-18` | **Dependencia directa:** Este NADR extiende la taxonomía de criticidad definida por NADR-18 (pesos de criticidad sujetos a validación empírica). |
| `NADR-F17BIS-19` | **Dependencia directa:** Este NADR extiende la regresión topológica graduada definida por NADR-19 (thresholds de NSS del DoubleProtectionMechanism). |
| `NADR-F17-BIS-24` | **Influencia:** NADR-24 (Certification Tooling Integrity) depende de los parámetros calibrados y del Evaluation Provenance establecidos por este NADR para la certificación. |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN` | Materializa las reglas de este NADR mediante tareas de calibración, validación, evaluación final y provenance. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la cualificación del corpus ni la cobertura de traits de los documentos (responsabilidad de `NADR-F17BIS-20`).
* **No gobierna** la elegibilidad, curaduría o sellado de Ground Truths (responsabilidad de `NADR-F17-BIS-21`).
* **No gobierna** la configuración del motor de evaluación topológica ni el modelo de costo (responsabilidad de `NADR-F17-BIS-22`).
* **No gobierna** la integridad operacional del tooling de certificación ni la semántica de fallo (responsabilidad de `NADR-F17-BIS-24`).
* **No gobierna** la integración en CI/CD de los Regression Gates (responsabilidad de Fase 6).
* **No prescribe** el método específico de partición de datasets (LOOCV, bootstrap, holdout, u otro). La selección del método pertenece al protocolo de calibración aprobado.
* **No prescribe** el algoritmo específico de búsqueda de parámetros (Grid Search, Bayesian Optimization, u otro). La selección del algoritmo pertenece al protocolo de calibración aprobado.
* **No prescribe** la infraestructura específica de provenance (MLflow, PostgreSQL, u otra). La implementación del Calibration Provenance Record y Evaluation Provenance Record pertenece al Execution Plan.
* **No prescribe** el método estadístico específico de calibración. La selección del método pertenece al protocolo de calibración aprobado.
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del `PHASE_17BIS_FASE5_EXECUTION_PLAN`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.