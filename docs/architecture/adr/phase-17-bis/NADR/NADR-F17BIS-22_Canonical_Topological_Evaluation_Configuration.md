# NADR-F17-BIS-22: Canonical Topological Evaluation Configuration

## 1. METADATA

* **Decision ID:** `NADR-F17-BIS-22`
* **Título:** Canonical Topological Evaluation Configuration
* **Clase de Decisión:** `DATA / OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 17-BIS — Fase 5 (Baseline Certification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-F5-03 (Canonical Topological Evaluation Configuration) — Establece la configuración canónica del motor de evaluación topológica para la certificación de la baseline, incluyendo el motor, el modelo de costo, la normalización de texto, la política de raíz virtual, la metodología de evaluación, y los thresholds de veredicto.
* **Evidencia Forense:** `E-5.3-001` (modelo de costo diferente), `E-5.3-002` (normalización de texto diferente), `E-5.3-003` (raíz virtual diferente), `E-5.3-004` (metodología diferente), `E-5.3-005` (APTED adapter no integra CriticalityAwareCostContext), `E-5.3-013` (normalización equivalente bajo UnitCostContext), `E-5.3-014` (CriticalityAwareCostContext implementa TreeEditCostContext), HITO 5.3 Clasificación C (Comparable but Non-Equivalent)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_05` (FROZEN), `NADR-F17-BIS-20` (Canonical Corpus Qualification), `NADR-F17BIS-21` (Ground Truth Eligibility, Migration & Sealing), `NADR-F17BIS-18` (Taxonomía de Criticidad), `NADR-F17BIS-19` (Regresión Topológica Graduada)
  * **Influencia:** `NADR-F17-BIS-23` (Scientific Calibration), `NADR-F17-BIS-24` (Certification Tooling Integrity), `PHASE_17BIS_FASE5_EXECUTION_PLAN`
  * **Conflictúa con:** Uso de motores no canónicos en la cadena de certificación, thresholds de NSS universales, normalización de texto divergente entre componentes de evaluación, configuración no identificada o no congelada.
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | **FROZEN** Emisión inicial. 27 reglas normativas en 8 dominios. |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin motor canónico de evaluación, la certificación de la baseline no puede ejecutarse. Toda evaluación de regresión queda sin referencia determinista.
* **Mantenibilidad:** 4 — Sin configuración canónica identificada y congelada, la evolución del motor de evaluación es ambigua y propensa a divergencias silenciosas.
* **Recuperabilidad:** 3 — Sin reproducibilidad de evaluación, la recuperación ante corrupción o sustitución de resultados es imposible.
* **Seguridad:** 2 — No hay exposición directa a vulnerabilidades de seguridad. El riesgo es de integridad científica.
* **Financiero:** 3 — Sin certificación, las fases posteriores (18-21) quedan bloqueadas, generando costo de oportunidad significativo.
* **Total Score: 17/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La evaluación topológica de certificación se ejecuta exclusivamente con una configuración canónica única, identificada y congelada, que establece el motor, el modelo de costo, la normalización de texto, la política de raíz virtual, la metodología de evaluación y los thresholds de veredicto.**

En consecuencia:
* Ningún motor que no sea el motor canónico puede participar en la cadena de certificación.
* Ningún modelo de costo que no sea el modelo canónico puede utilizarse en la evaluación de certificación.
* La normalización de texto del motor canónico es sin transformación de fingerprint ni `.strip()`.
* La metodología de evaluación canónica es Σ TED(windows) con partición por headings, no TED(full tree).
* Los thresholds de NSS son específicos del motor + configuración + metodología. No existe NSS_THRESHOLD universal.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de certificación de la baseline requiere un motor de evaluación topológica canónico con configuración identificada y congelada. Sin embargo, la auditoría forense (HITO 5.3) demostró que el estado actual del repositorio presenta cinco clases de deficiencias que impiden la evaluación de certificación:

1. **Divergencia de modelo de costo:** Los dos motores de evaluación topológica (ZhangShashaEngine y StructuralTopologyMetric/APTED) utilizan modelos de costo diferentes. ZhangShashaEngine utiliza UnitCostContext (sub=1.0), mientras que APTED utiliza CostMatrix (rename_same=0.5, rename_diff=2.0).

2. **Divergencia de normalización de texto:** CriticalityAwareCostContext opera sobre ASTNode.text_content directamente (sin `.strip()`), mientras que ASTFingerprintPolicy.semantic_fingerprint() aplica `.strip()` al contenido. Esto produce divergencias en la evaluación de certificación.

3. **Divergencia de raíz virtual:** ZhangShashaEngine agrega raíz virtual condicionalmente (solo si multi-root) con costo 0, mientras que APTED agrega raíz virtual siempre con costo normal.

4. **Divergencia de metodología de evaluación:** ZhangShashaEngine evalúa Σ TED(windows) con partición por headings, mientras que APTED evalúa TED(full tree).

5. **APTED adapter no integra CriticalityAwareCostContext:** El adapter actual de APTED (StructuralTopologyMetric) no integra CriticalityAwareCostContext, aunque la librería APTED sí permite configuración de costos variables mediante apted.Config.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-5.3-001` (P1 — Alto):** UnitCostContext utiliza sub=1.0 uniforme. CostMatrix.default_v1() utiliza rename_same_type=0.5, rename_diff_type=2.0. Los modelos de costo son diferentes.

* **`E-5.3-002` (P1 — Alto):** CriticalityAwareCostContext.substitution_cost() opera sobre ASTNode.text_content directamente (sin `.strip()`). ASTFingerprintPolicy.semantic_fingerprint() aplica `.strip()` al contenido. Esto produce divergencias en la evaluación de certificación.

* **`E-5.3-003` (P1 — Alto):** ZhangShashaEngine agrega raíz virtual condicionalmente (solo si multi-root) con costo 0. StructuralTopologyMetric agrega raíz virtual siempre con costo normal.

* **`E-5.3-004` (P1 — Alto):** ZhangShashaEngine evalúa Σ TED(windows) con partición por headings. StructuralTopologyMetric evalúa TED(full tree). Son magnitudes diferentes por diseño.

* **`E-5.3-005` (P1 — Alto):** El adapter actual de APTED (StructuralTopologyMetric) no integra CriticalityAwareCostContext. La librería APTED sí permite configuración de costos variables mediante apted.Config, pero el adapter actual no lo implementa.

* **`E-5.3-013` (VERIF):** La normalización es equivalente bajo UnitCostContext. La divergencia de normalización solo se manifiesta con CriticalityAwareCostContext.

* **`E-5.3-014` (VERIF):** CriticalityAwareCostContext implementa TreeEditCostContext correctamente.

* **HITO 5.3 Clasificación C (Comparable but Non-Equivalent):** ZhangShasha y APTED no calculan la misma función de distancia bajo la configuración actual. Las divergencias son de configuración, representación y metodología, no del algoritmo TED en sí.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Motor Canónico

1. El motor canónico de evaluación topológica para la certificación de la baseline **MUST** ser ZhangShashaEngine.
2. Ningún motor que no sea el motor canónico **MUST** participar en la cadena de certificación.
3. StructuralTopologyMetric (APTED) **MAY** permanecer como herramienta experimental o benchmark no normativo.
4. StructuralTopologyMetric (APTED) **MUST NOT** ser eliminado del repositorio sin evidencia de redundancia demostrada conforme a ENGINEERING_PRINCIPLES §I (YAGNI).

### 5.2 Modelo de Costo Canónico

5. El modelo de costo canónico para la evaluación de certificación **MUST** ser CriticalityAwareCostContext.
6. Los pesos por defecto del modelo de costo canónico **MUST** ser: CRITICAL=5.0, WARNING=2.0, INFO=1.0.
7. Los pesos del modelo de costo canónico **MUST** ser configurables mediante inyección conforme a NADR-F17BIS-18 §5.3 R13.
8. La validación empírica de los pesos del modelo de costo canónico **MUST** ser realizada conforme a NADR-F17BIS-18 §5.3 R12 Condición B antes de la certificación final.
9. Los thresholds de NSS **MUST** ser específicos del motor + configuración + metodología de evaluación. No existe NSS_THRESHOLD universal.

### 5.3 Normalización de Texto

10. El motor canónico **MUST** operar sobre ASTNode.text_content directamente, sin transformación de fingerprint.
11. La normalización de texto canónica **MUST** ser SIN `.strip()`.
12. La divergencia entre CriticalityAwareCostContext (sin `.strip()`) y ASTFingerprintPolicy.semantic_fingerprint() (con `.strip()`) **MUST** ser registrada como deuda técnica y resuelta en el Execution Plan.

### 5.4 Política de Raíz Virtual

13. La política de raíz virtual canónica **MUST** ser condicional: raíz virtual solo si el documento tiene múltiples raíces.
14. El costo de la raíz virtual canónica **MUST** ser 0.0.
15. Una raíz virtual siempre-presente (como en StructuralTopologyMetric) **MUST NOT** ser considerada canónica para la evaluación de certificación.

### 5.5 Metodología de Evaluación

16. La metodología de evaluación canónica **MUST** ser Σ TED(windows) con partición por headings.
17. La estrategia de partición canónica **MUST** ser HeadingAnchorPartitionStrategy.
18. TED(full tree) (como en StructuralTopologyMetric) **MUST NOT** ser considerado canónico para la evaluación de certificación.

### 5.6 Configuración Canónica

19. La configuración canónica del motor de evaluación **MUST** estar identificada mediante un identificador criptográfico determinista.
20. La configuración canónica **MUST** ser congelada antes de la certificación. Toda modificación de la configuración canónica **MUST** invalidar la certificación vigente.
21. Toda evaluación de certificación **MUST** utilizar la configuración canónica. La evaluación con configuración no canónica **MUST NOT** producir resultados de certificación.

### 5.7 Thresholds y Veredictos

22. Los thresholds de NSS **MUST** ser definidos por el protocolo de calibración conforme a NADR-F17-BIS-23.
23. No existe NSS_THRESHOLD universal. Todo threshold **MUST** estar asociado a una configuración canónica específica.
24. DoubleProtectionMechanism **MUST** ser el mecanismo canónico de veredicto para la evaluación de certificación conforme a NADR-F17BIS-19.
25. CriticalityVerdictEmitter **MUST** ser el emisor canónico de veredictos de criticidad conforme a NADR-F17BIS-18.

### 5.8 Provenance de Evaluación

26. Toda evaluación de certificación **MUST** registrar la configuración canónica utilizada.
27. La configuración utilizada en una evaluación **MUST** ser verificable contra la configuración canónica vigente. La evaluación con configuración no verificable **MUST NOT** producir resultados de certificación.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **Motor canónico único:** La evaluación de certificación se ejecuta exclusivamente con ZhangShashaEngine. Esto elimina el riesgo de divergencias entre motores y garantiza que la evaluación sea determinista y reproducible.
* **Modelo de costo canónico:** La evaluación de certificación utiliza CriticalityAwareCostContext. Esto garantiza que la evaluación de certificación refleje la taxonomía de criticidad definida por NADR-18.
* **Normalización de texto canónica:** El motor canónico opera sobre ASTNode.text_content directamente, sin transformación de fingerprint ni `.strip()`. Esto elimina el riesgo de divergencias de normalización entre componentes de evaluación.
* **Metodología de evaluación canónica:** La evaluación de certificación utiliza Σ TED(windows) con partición por headings. Esto garantiza que la evaluación de certificación sea consistente con la arquitectura de partición definida por el ADR Maestro.
* **Configuración canónica identificada y congelada:** La configuración del motor de evaluación está identificada y congelada. Toda modificación de la configuración invalida la certificación vigente. Esto garantiza que la evaluación sea reproducible y verificable.
* **Thresholds específicos:** Los thresholds de NSS son específicos del motor + configuración + metodología. No existe NSS_THRESHOLD universal. Esto elimina el riesgo de aplicar thresholds incorrectos a configuraciones no canónicas.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el motor de evaluación de certificación es ZhangShashaEngine.
  * Verificación de que el modelo de costo de evaluación de certificación es CriticalityAwareCostContext.
  * Verificación de que la normalización de texto del motor canónico es sin `.strip()`.
  * Verificación de que la metodología de evaluación de certificación es Σ TED(windows) con partición por headings.
  * Verificación de que la configuración canónica está identificada y congelada.
  * Verificación de que no existen evaluaciones de certificación con configuración no canónica.

* **Validation (dinámica/comportamental):**
  * Ejecución de la evaluación de certificación sobre el corpus canónico, verificando que la evaluación se ejecuta correctamente con la configuración canónica.
  * Verificación del determinismo de la evaluación: la misma colección de oráculos produce la misma evaluación en múltiples ejecuciones.
  * Verificación de la reproducibilidad de la evaluación: la misma configuración canónica produce la misma evaluación en múltiples ejecuciones.
  * Verificación de que la evaluación con configuración no canónica no produce resultados de certificación.
  * Verificación de que los thresholds de NSS son específicos del motor + configuración + metodología.
  * Verificación de que el corpus cualificado puede ser consumido por el proceso de certificación de Fase 5 sin violar las invariantes definidas por este NADR y los NADRs dependientes.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro §3 (Separación Integridad/Identidad/Regresión) y DC-06 (Taxonomía de Criticidad de Nodos). |
| `ADR_F17_BIS_05` | Este NADR implementa D4 (Canonical Evaluation Architecture) del ADR de Fase 5. |
| `NADR-F17BIS-20` | **Dependencia directa:** Este NADR depende de la cualificación del corpus establecida por NADR-20. |
| `NADR-F17BIS-21` | **Dependencia directa:** Este NADR depende de los oráculos sellados establecidos por NADR-21. |
| `NADR-F17BIS-18` | **Dependencia directa:** Este NADR extiende la taxonomía de criticidad definida por NADR-18 (CriticalityAwareCostContext, CriticalityVerdictEmitter). |
| `NADR-F17BIS-19` | **Dependencia directa:** Este NADR extiende la regresión topológica graduada definida por NADR-19 (DoubleProtectionMechanism). |
| `NADR-F17-BIS-23` | **Influencia:** NADR-23 (Scientific Calibration) depende de la configuración canónica establecida por este NADR para la calibración empírica. |
| `NADR-F17-BIS-24` | **Influencia:** NADR-24 (Certification Tooling Integrity) depende de la configuración canónica establecida por este NADR para la certificación. |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN` | Materializa las reglas de este NADR mediante tareas de configuración, evaluación y certificación. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la cualificación del corpus ni la cobertura de traits de los documentos (responsabilidad de `NADR-F17BIS-20`).
* **No gobierna** la elegibilidad, curaduría o sellado de Ground Truths (responsabilidad de `NADR-F17BIS-21`).
* **No gobierna** la calibración empírica de parámetros ni la independencia de datasets (responsabilidad de `NADR-F17-BIS-23`).
* **No gobierna** la integridad operacional del tooling de certificación ni la semántica de fallo (responsabilidad de `NADR-F17-BIS-24`).
* **No gobierna** la integración en CI/CD de los Regression Gates (responsabilidad de Fase 6).
* **No gobierna** la definición del framing canónico de H_baseline (responsabilidad de `NADR-F17BIS-16`).
* **No gobierna** la definición del ciclo de vida del Ground Truth (responsabilidad de `NADR-F17BIS-12`).
* **No prescribe** el protocolo de calibración empírica ni los criterios específicos de calibración (responsabilidad de `NADR-F17-BIS-23` y el Execution Plan).
* **No prescribe** la implementación específica del motor de evaluación ni la serialización de oráculos (responsabilidad del Execution Plan).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del `PHASE_17BIS_FASE5_EXECUTION_PLAN`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.