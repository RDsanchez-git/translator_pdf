# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17_BIS_05: Canonical Corpus Qualification, Scientific Calibration & Baseline Certification

* **Estado:** FROZEN
* **Versión:** 1.0.0
* **Fecha de Emisión:** 2026-09-05
* **Fecha de Aprobación:** 2026-09-05
* **Fecha de Congelamiento:** 2026-09-05
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** 17-BIS (Scientific Baseline / Canonical Corpus)
* **Evidencia Forense Vinculante:** HITO_5.0 v1.0.2 (FROZEN), HITO_5.1 v1.1.2 (FROZEN), HITO_5.2 v1.1.0 (FROZEN), HITO_5.3 v1.1.3 (FROZEN), HITO_5.4 v1.0.3 (FROZEN), FASE_4_HANDOFF (FROZEN), Verificación forense H-5.1-F (2026-09-05)
* **Referencias Cruzadas:**
  * **Depende de:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-12 a NADR-F17BIS-19 (FROZEN)
  * **Implementado por:** NADR-F17BIS-20 a NADR-F17BIS-24 (a promulgar)
  * **Ejecutado por:** PHASE_17BIS_FASE5_EXECUTION_PLAN (a redactar)
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 17-BIS, conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para la subfase de Baseline Certification. Este ADR es el artefacto de síntesis de los HITOs forenses 5.0 a 5.4 y resuelve las Decisiones Candidatas acumuladas.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-09-05 | Emisión inicial DRAFT. 8 decisiones (D1-D8). H-5.1-F integrada como RECHAZADA. |
| 0.2.0 | 2026-09-05 | 7 correcciones: D7 LOOCV, citación D4, normalización texto, Target State, cláusula Fase 6, DoD, cláusula Execution Plan. |
| 0.3.0 | 2026-09-05 | Tabla de DCs completada. Invariantes consolidadas. |
| 0.4.0 | 2026-09-05 | 10 correcciones forenses: D4 adapter gap, D7 sin LOOCV normativo, DoD Fase 5/6, H_baseline, D2 "requiere como mínimo", D1 déficit, §2 fusión, Target State etapas, Regla de Oro limpia, DC-5.4-002 migración. |
| 1.0.0 | 2026-09-05 | APPROVED. Corrección final de nomenclatura de DCs en §10 (alineación con IDs estables de HITO 5.0). |
| 1.0.0-FROZEN | 2026-09-05 | **FROZEN.** Documento congelado. Listo para promulgación de NADRs de Fase 5 (NADR-F17BIS-20 a NADR-F17BIS-24). |

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 5 (Baseline Certification) tiene como mandato materializar en disco la Baseline Científica Inmutable y garantizar el Zero Partial Sealing conforme al ADR Maestro §5. Cinco HITOs forenses consecutivos (5.0 a 5.4) han auditado el estado actual del repositorio, produciendo un cuerpo de evidencia de 73 hallazgos únicos, 33 gaps consolidados y 27 Decisiones Candidatas. La clasificación global de readiness emitida por HITO 5.4 es **NOT READY**: calibration_v1 es INELIGIBLE bajo el contrato vigente, la infraestructura de calibración es insuficiente, y ningún parámetro ha sido calibrado empíricamente.

La verificación forense puntual de H-5.1-F (ejecutada 2026-09-05) confirmó empíricamente que los Ground Truths de calibration_v1 producen identidad criptográfica distinta bajo el algoritmo vigente debido a node_ids legacy (`"value='p1_b0'"` vs `"p1_b0"`). El hash legacy (`085cf4a81de34dd0602f0411cabf6df3366b72a9ffd48b2324096b5c43a4a109`) difiere del hash canónico (`fe0f8409dbbdd5122ce56719ae1cf5fbea0af4e53c7dd7749bbc15bf504fb97e`), cerrando la hipótesis como **RECHAZADA** y confirmando GAP-5.4-002 como defecto de identidad.

Adicionalmente, HITO 5.3 (v1.1.3) clasificó ZhangShasha y APTED como **Comparable but Non-Equivalent** (clasificación C), demostrando divergencias en modelo de costo, normalización de texto, raíz virtual y metodología de aplicación. HITO 5.3 identificó que el adapter actual de APTED (`StructuralTopologyMetric`) no integra `CriticalityAwareCostContext`, aunque la librería APTED sí permite configuración de costos variables mediante `apted.Config` (GAP-5.3-05, P1). HITO 5.2 confirmó DF-18 en 4 entry points con caminos de error que terminan en exit 0.

---

## 2. PROBLEMA ARQUITECTÓNICO

La arquitectura de certificación de la baseline presenta siete dimensiones estructurales que impiden la certificación científica en el estado actual:

1. **Corpus Físico Insuficiente y Cobertura No Demostrada:** El universo actual contiene 7 identidades únicas candidatas con cobertura de traits limitada a `native_pdf` (HITO 5.1). El ADR Maestro §6 exige 20-30 documentos de alta varianza. La cobertura real de traits está NO DEMOSTRADA (H-5.1-C) porque los nombres de archivos son indicios, no evidencia suficiente.

2. **Inelegibilidad de calibration_v1:** El manifest está en formato legacy (DF-19), incompatible con `ManifestFingerprintCalculator.compute_hash()` (HITO 5.4 E-5.4-001). Los node_ids legacy producen identidad criptográfica distinta bajo el algoritmo vigente (HITO 5.4 E-5.4-004 + verificación forense H-5.1-F).

3. **Ausencia de Infraestructura de Calibración:** No existe partición de datasets, provenance de calibration runs, capacidad funcional de análisis estadístico reproducible, ni protocolo de calibración empírica ejecutable (HITO 5.4 E-5.4-018, E-5.4-021). Ningún parámetro ha sido calibrado empíricamente.

4. **Divergencia Algorítmica:** ZhangShashaEngine y APTED son Comparable but Non-Equivalent (HITO 5.3 Clasificación C). El adapter actual de APTED no integra `CriticalityAwareCostContext` (la librería sí puede). Los thresholds de NSS no son transferibles entre motores.

5. **Integridad Operacional del Tooling:** DF-18 (semántica de fallo heterogénea en 4 entry points, HITO 5.2) y Certification Boundary Integrity violation (`sanitize_ground_truth_types.py`, HITO 5.2) impiden la certificación confiable.

6. **Identidad Criptográfica Rota:** Los Ground Truths existentes producen identidad distinta bajo el contrato vigente (node_ids legacy). El manifest legacy es incompatible con el algoritmo de hashing actual.

7. **Comparabilidad Algorítmica Ausente:** Los dos motores de evaluación topológica no calculan la misma función de distancia bajo la configuración actual. La divergencia de normalización de texto (`.strip()` vs sin `.strip()`) impide la evaluación unificada.

**Consecuencias de no resolver el problema:**
* La Baseline Científica no puede certificarse.
* La Fase 18 (Advanced Local Runtime) queda bloqueada sin red de seguridad.
* Los Regression Gates no pueden materializarse ni integrarse en CI.
* La deuda técnica se acumula sin verificación científica.

---

## 3. DECISIÓN ARQUITECTÓNICA

**La Fase 5 establecerá un proceso único, reproducible y criptográficamente identificable para convertir un corpus físicamente cualificado y Ground Truths curados en una Scientific Baseline certificable, separando estrictamente curaduría de Ground Truth, calibración empírica y evaluación final, y prohibiendo que los mismos datos utilizados para calibrar parámetros sean utilizados como evidencia independiente de evaluación.**

En consecuencia, se establecen las siguientes ocho decisiones arquitectónicas:

### D1 — Corpus Canónico (DC-5.0-01, DC-5.1-003, DC-5.4-004)

El corpus canónico es el conjunto de documentos físicamente cualificados que satisface el objetivo arquitectónico del ADR Maestro §6 (20-30 documentos de alta varianza). La cobertura de traits debe verificarse por inspección de contenido de los PDFs, no por nombres de archivos. El corpus actualmente cualificado no alcanza el objetivo: partiendo de las 7 identidades candidatas actuales, existe un **déficit de 13-23 identidades** respecto del rango objetivo de 20-30. La deduplicación se basa en content identity (SHA-256), no filename. Los documentos duplicados (HITO 5.1 G1: 4 copias, G2: 2 copias) se consolidan en una única identidad.

### D2 — Ground Truth Curation & Eligibility (DC-5.4-001, GAP-5.4-001, GAP-5.4-002)

La elegibilidad para sellado requiere, como mínimo: (a) que el Ground Truth pueda hidratarse bajo el contrato AST V2 actual; (b) que sus node_ids estén en representación canónica; (c) que su contenido haya sido curado por inspección humana experta; (d) que su oracle_hash haya sido recomputado bajo el contrato vigente. El contrato normativo completo de elegibilidad pertenece a los NADRs asociados (NADR-13, NADR-14). Los Ground Truths de calibration_v1 son INELIGIBLES bajo el contrato vigente y requieren migración o re-extracción. La decisión de migración vs. re-extracción corresponde a los NADRs asociados.

### D3 — Identidad, Sealing y Autoridad Única (GAP-5.4-001, GAP-5.4-002)

La arquitectura distingue cuatro identidades: Document identity (SHA-256 del PDF), Manifest identity (hash de 6 dimensiones), Oracle semantic identity (hash de node_id + node_type + strategy + payload), y Baseline identity (hash encadenado de todos los oráculos). La arquitectura establece una identidad criptográfica de Baseline derivada determinísticamente de los artefactos sellados que la componen ($H_{baseline}$). La definición exacta del framing, orden y composición pertenece al NADR correspondiente. Los artefactos legacy (manifest DF-19, node_ids `"value='p1_b0'"`, .ast.json) no pueden convertirse directamente en autoridad canónica; deben atravesar un proceso explícito de migración validada o ser reemplazados por nueva extracción/curaduría, conservando trazabilidad de lineage. La certificación de la baseline es gobernada por una única autoridad que produce una identidad de baseline criptográficamente encadenada. No existe certificación parcial ni autoridad de certificación distribuida.

### D4 — Canonical Evaluation Architecture (DC-5.3-001, DC-5.3-002, DC-5.3-007)

**ZhangShashaEngine** es el motor topológico canónico para regresión y certificación de la baseline. **CriticalityAwareCostContext** es el modelo de costo normativo para la cadena de certificación. Esta decisión se fundamenta en: (a) la integración actual de ZhangShasha con `CriticalityAwareCostContext` (HITO 5.4 E-5.4-014); (b) el adapter actual de APTED (`StructuralTopologyMetric`) no integra `CriticalityAwareCostContext`, aunque la librería APTED sí permite configuración de costos variables mediante `apted.Config` (HITO 5.3 GAP-5.3-05, P1); (c) HITO 5.3 clasificación C demuestra que los thresholds no son transferibles entre motores.

**APTED** queda fuera de la cadena normativa de certificación sin que ello implique que sea matemáticamente incorrecto o técnicamente incapaz de soportar otros modelos de costo. No se elimina del repositorio (ENGINEERING_PRINCIPLES §I: no eliminar sin evidencia de redundancia), pero no participa en la cadena de certificación ni en los Regression Gates.

Toda configuración del motor canónico debe estar identificada y congelada. Las reglas técnicas exactas (label, normalización de texto, root policy, metodología de evaluación, serialización) pertenecen a los NADRs asociados. El ADR establece que existe una configuración canónica única y congelada; el NADR define sus valores exactos.

Los thresholds de NSS son específicos del motor + configuración + metodología de evaluación. No puede existir `NSS_THRESHOLD = 0.95` como si fuera universal.

### D5 — Scientific Calibration (DC-5.4-005, DC-5.4-006)

La calibración empírica debe establecerse antes de la validación de parámetros. El protocolo de calibración debe definir el experimento (variable a calibrar, ground truth observable, función objetivo, espacio de parámetros, restricciones, unidad de evaluación, independencia, criterio de aceptación) antes de elegir algoritmo de búsqueda. Invariante: `Calibration dataset ∩ Final evaluation dataset = ∅` a nivel de content identity (SHA-256), no filename. Calibration ≠ Evaluation: no se calibra sobre los mismos datos con los que se evalúa.

### D6 — Experimental Provenance (DC-5.4-005, GAP-5.4-005)

Toda calibración que produzca parámetros candidatos deberá ser reproducible a partir de: (1) corpus_identity (SHA-256 del manifest), (2) metric_configuration (hash de configuración), (3) parameters (pesos/thresholds), (4) result (scores), (5) timestamp (fecha de ejecución). Estos cinco campos constituyen el mínimo exigible y no implican que el timestamp sea un mecanismo de identidad de experimento. La arquitectura distingue Artifact provenance (identidad de artefactos) de Calibration-run provenance (identidad de experimentos). No se prescribe MLflow, PostgreSQL ni infraestructura específica; eso pertenece a los NADRs/Execution Plan.

### D7 — Dataset Independence (DC-5.4-007)

Se establecen tres conceptos operacionalmente distintos:
* **CALIBRATION:** elige parámetros (pesos, thresholds)
* **VALIDATION:** comprueba generalización / selección de modelo
* **FINAL EVALUATION:** produce evidencia de baseline certificada

**Regla:** Los resultados de final evaluation no pueden participar en la selección de parámetros.

Con el corpus actual de 7 identidades, no existe evidencia suficiente para establecer una evaluación final independiente estadísticamente robusta. Los métodos de validación apropiados deberán definirse en el protocolo científico de calibración. LOOCV, bootstrap u otros métodos podrán ser considerados por dicho protocolo, pero este ADR no prescribe uno de ellos. La Final Evaluation independiente solo puede ejecutarse cuando exista una partición que preserve independencia a nivel de content identity y que haya sido declarada suficiente por el protocolo científico aprobado.

### D8 — Certification Operational Integrity (DF-18, GAP-5.2-01)

Los entry points de certificación deben implementar semántica de fallo uniforme con exit codes diferenciados. Ningún camino de error puede producir exit code 0 (ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos). La taxonomía específica de exit codes queda definida en los NADRs de Fase 5. El principio rector es: el tooling de certificación debe tener configuración explícita del corpus antes de la integración en CI. DF-18 y DF-19 deben resolverse antes de la certificación.

---

## 4. OBJETIVO DE LA SUBFASE

La Fase 5 tiene como objetivo certificar la Baseline Científica Canónica mediante la materialización del corpus canónico en disco, el sellado criptográfico de cada Ground Truth bajo Zero Partial Sealing estricto, el establecimiento de infraestructura de calibración empírica reproducible, y la materialización de compuertas de regresión topológica verificables.

El objetivo primordial es garantizar que:
> *"La Baseline Científica Canónica es un oráculo determinista, criptográficamente encadenado, con cobertura de traits verificada por inspección de contenido, que actúa como red de seguridad inmutable contra la cual se evalúa cualquier evolución técnica del pipeline de producción."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance
* Materialización del corpus canónico (20-30 documentos) con cobertura de traits verificada por inspección de contenido.
* Migración o re-extracción de calibration_v1 y artefactos .ast.json legacy.
* Canonicalización de node_ids y recomputación de oracle_hashes.
* Migración del manifest de calibration_v1 al formato actual (6 dimensiones).
* Establecimiento de infraestructura de calibración empírica reproducible.
* Definición del protocolo de calibración empírica de parámetros.
* Materialización de compuertas de regresión topológica (ejecutables y verificables fuera de CI).
* Resolución de DF-18 (semántica de fallo) y DF-19 (formato de manifest).
* Configuración explícita del corpus en el tooling de certificación.

### Fuera del Alcance (Out of Scope)
* **NO** realizar optimizaciones de rendimiento, asincronía o memoria (pertenece estrictamente a Fase 18).
* **NO** integrar nuevos adaptadores de extracción de visión computacional (pertenece a Fase 17).
* **NO** introducir infraestructura distribuida (Redis, Message Brokers, Kubernetes, DBs remotas) (ADR Maestro §4).
* **NO** modificar componentes de dominio ni crear abstracciones durante la certificación.
* **NO** calibrar parámetros mediante tuning sobre los mismos datos de evaluación (Calibration ≠ Tuning).
* **NO** declarar "científicamente calibrado" por tener un script. La calibración requiere protocolo previamente definido, datos independientes, y función objetivo explícita.
* **NO** eliminar APTED del repositorio (ENGINEERING_PRINCIPLES §I; queda como herramienta experimental).
* **NO** integrar los Regression Gates en CI/CD (pertenece a Fase 6).

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

### Invariantes específicas de la Fase 5:

* **Invariante de Motor Canónico Único:** La cadena de certificación y los Regression Gates operan exclusivamente con el motor canónico (ZhangShasha + CriticalityAwareCostContext). Ningún otro motor participa en la certificación.
* **Invariante de Separación de Datasets:** La calibración empírica debe utilizar separación de datasets basada en content identity (SHA-256), no filename. Documentos con el mismo SHA-256 no pueden aparecer en particiones diferentes.
* **Invariante de Provenance Mínimo:** Toda calibration run debe registrar al menos: corpus_identity, metric_configuration, parameters, result, timestamp.
* **Invariante de Cero Fallos Silenciosos en Certificación:** Ningún camino de error en los entry points de certificación puede producir exit code 0 (ENGINEERING_PRINCIPLES §IV).
* **Invariante de No Edición Forense:** Los HITOs forenses no editan Ground Truths. La curaduría y corrección se ejecutan exclusivamente a través del Execution Plan gobernado por este ADR y los NADRs asociados.
* **Invariante de Cobertura por Inspección:** La cobertura de traits del corpus canónico debe verificarse por inspección de contenido de los PDFs, no por nombres de archivos.
* **Invariante de Calibración Independiente:** Calibration ≠ Evaluation. Los datos utilizados para calibrar parámetros no pueden ser utilizados como evidencia independiente de evaluación.
* **Invariante de Autoridad Única:** La certificación de la baseline es gobernada por una única autoridad. No existe certificación parcial ni autoridad distribuida.

### Cláusula de Relación con el Execution Plan:
> *"Las decisiones arquitectónicas definidas en este ADR especifican las capacidades arquitectónicas requeridas. La secuenciación operativa, estrategia de despliegue, dependencias técnicas y logística de implementación son gobernadas independientemente por `PHASE_17BIS_FASE5_EXECUTION_PLAN.md`. El Execution Plan existe porque la auditoría forense demostró que las capacidades arquitectónicas no pueden implementarse independientemente. La remediación de producción debe preceder a la certificación científica según el grafo de dependencias identificado."*

### Cláusula de Relación con Fase 6:
> *"La Fase 5 materializa la Baseline Certificada y los Regression Gates como artefactos ejecutables y verificables fuera de CI. La Fase 6 (Continuous Verification) integra estos artefactos en el pipeline de CI/CD. La Fase 5 no implementa la integración en CI; eso pertenece a Fase 6."*

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

Tras la implementación de la Fase 5, la arquitectura de certificación opera como un pipeline determinista, atómico y auditable:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. CORPUS QUALIFICATION                                                │
│    PDF Documents (20-30, alta varianza)                                │
│    → Curation Protocol (inspección de contenido, verificación traits)  │
│    → Canonical Corpus (manifest.json, formato 6 dimensiones)           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. GROUND TRUTH CURATION                                               │
│    Candidate → Human/Forensic Curation → Ground Truth Draft            │
│    → Validation (OracleValidityContract)                               │
│    → Node ID Canonicalization (migración de legacy)                    │
│    → Oracle Hash Recomputation                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. SEALING & IDENTITY                                                  │
│    → Completeness Verification (BaselineCompletenessVerifier)          │
│    → Atomic Sealing (Zero Partial Sealing, autoridad única)            │
│    → Sealed Oracles + Sealed Manifest                                  │
│    → Cryptographic Chaining (H_baseline encadenado)                    │
│    → Certified Baseline (identidad criptográfica encadenada)           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. SCIENTIFIC CALIBRATION                                              │
│    Dataset Partition (content identity, no filename)                   │
│       ↓                                                                │
│    Calibration Dataset                                                  │
│       ↓                                                                │
│    Parameter Candidates                                                 │
│       ↓                                                                │
│    Validation (generalización / selección de modelo)                   │
│       ↓                                                                │
│    Parameter Selection                                                  │
│       ↓                                                                │
│    Parameter Freeze                                                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. FINAL EVALUATION                                                    │
│    Independent Evaluation Dataset (∩ Calibration = ∅)                 │
│       ↓                                                                │
│    Frozen Parameters                                                    │
│       ↓                                                                │
│    Canonical Engine (ZhangShasha + CriticalityAwareCostContext)        │
│       ↓                                                                │
│    Certification Evidence                                               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. CONTINUOUS VERIFICATION (Fase 6 — fuera del alcance de Fase 5)      │
│    → Regression Gates integrados en CI/CD                              │
│    → DoubleProtectionMechanism (NSS + Criticality)                     │
│    → Exit codes diferenciados (semántica de fallo uniforme)            │
└─────────────────────────────────────────────────────────────────────────┘
```

**Invariante del estado objetivo:**
> *"La Baseline Certificada es un artefacto criptográficamente inmutable, con correspondencia biyectiva completa entre PDFs y oráculos AST (N_PDF = N_GT), evaluada exclusivamente por el motor canónico contra thresholds calibrados empíricamente, con provenance reproducible y Regression Gates materializados como artefactos ejecutables y verificables."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la subfase de certificación | ✅ |
| `HITO_5.0 v1.0.2` | Evidencia forense: estado de contratos, DF-18, rutas hardcodeadas | ✅ |
| `HITO_5.1 v1.1.2` | Evidencia forense: universo físico del corpus, DF-19, node_ids legacy | ✅ |
| `HITO_5.2 v1.1.0` | Evidencia forense: estado operacional del tooling, atomicidad de persistencia | ✅ |
| `HITO_5.3 v1.1.3` | Evidencia forense: clasificación C, divergencias ZhangShasha/APTED, adapter gap | ✅ |
| `HITO_5.4 v1.0.3` | Evidencia forense: NOT READY, ausencia de infraestructura de calibración | ✅ |
| Verificación forense H-5.1-F | Evidencia empírica: node_ids legacy producen identidad distinta | ✅ |
| `NADR-F17BIS-12` | Ontología del Ground Truth (GroundTruthDraft, SealedOracle) | ✅ |
| `NADR-F17BIS-13` | Validez y Completitud (OracleValidityContract, Zero Partial Sealing) | ✅ |
| `NADR-F17BIS-14` | Asimetría de Puertos y Autoridad de Sellado | ✅ |
| `NADR-F17BIS-16` | Semántica de Identidad (ManifestFingerprintCalculator, OracleSemanticIdentityCalculator) | ✅ |
| `NADR-F17BIS-17` | Contratos de Dominio (DocumentId, NodeId) | ✅ |
| `NADR-F17BIS-18` | Taxonomía de Criticidad (CriticalityAwareCostContext) | ✅ |
| `NADR-F17BIS-19` | Regresión Topológica Graduada (DoubleProtectionMechanism) | ✅ |
| `NADR-F17BIS-20` a `NADR-F17BIS-24` | NADRs de Fase 5 (a promulgar) que implementan las decisiones de este ADR | ✅ |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN.md` | Secuencia las tareas que materializan este ADR | ✅ |
| `FASE_4_HANDOFF` | Evidencia: run_regression.py exit codes 0/1/2, DF-04 | ✅ |
| **Fase 6 (Continuous Verification)** | Este ADR materializa los Regression Gates. Fase 6 los integra en CI/CD. | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ). Resuelve las Decisiones Candidatas acumuladas de HITO 5.0 a 5.4 mediante decisiones arquitectónicas basadas en evidencia forense.
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase (NADR-F17BIS-12 a NADR-F17BIS-19 existentes, más NADRs adicionales a promulgar para: semántica de fallo de entry points, protocolo de calibración empírica, política de partición de datasets, configuración exacta del motor canónico).
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

---

## 10. REGISTRO DE DECISIONES CANDIDATAS RESUELTAS

| DC | Tema | Resolución | Evidencia |
|---|---|---|---|
| DC-5.0-01 | Estructura física del corpus aún no canónica | D1: corpus canónico con cobertura verificada por inspección | HITO 5.0, 5.1, 5.4 |
| DC-5.0-02 | Semántica de fallo y taxonomía de exit codes | D8: exit codes diferenciados, cero fallos silenciosos | HITO 5.0 GAP-5.0-01 |
| DC-5.0-03 | Configurabilidad de corpus_path | D8: configuración explícita antes de CI | HITO 5.0 GAP-5.0-03 |
| DC-5.0-04 | Clasificación de PDFs legacy | D1: consolidación en corpus canónico | HITO 5.1 E-5.1-008 |
| DC-5.3-01 | Canonical Topology Engine | D4: ZhangShasha canónico | HITO 5.3 clasificación C |
| DC-5.3-02 | Alternative Engine Status | D4: APTED fuera de certificación, no eliminado del repositorio | HITO 5.3 clasificación C |
| DC-5.3-03 | Equivalence Boundary | D4: acotado a UnitCostContext + single-root | HITO 5.3 E-5.3-001 a E-5.3-004 |
| DC-5.3-04 | Canonical Cost Model | D4: CriticalityAwareCostContext (5.0/2.0/1.0) | NADR-18 §5.3 R12 |
| DC-5.3-05 | Canonical Label + Text Normalization | D4: configuración canónica congelada; valores exactos al NADR | HITO 5.3 E-5.3-002 |
| DC-5.3-06 | Canonical Root Policy | D4: configuración canónica congelada; valores exactos al NADR | HITO 5.3 E-5.3-003 |
| DC-5.3-07 | Benchmark Policy | D4: solo motor canónico en certificación | HITO 5.3 clasificación C |
| DC-5.4-001 | Política de curaduría de GTs | D2: inspección humana experta + migración | HITO 5.4 E-5.4-004, E-5.4-012 |
| DC-5.4-002 | Política de migración .ast.json legacy | D3: .ast.json legacy NO es autoridad canónica; puede servir como input de migración; nunca se sella directamente | HITO 5.4 E-5.4-008 |
| DC-5.4-003 | Política de migración manifest legacy | D3: regeneración programática al formato actual | HITO 5.4 E-5.4-001 |
| DC-5.4-004 | Adquisición de corpus adicional | D1: déficit de 13-23 identidades respecto del objetivo | HITO 5.1 (7 docs), HITO 5.4 E-5.4-011 |
| DC-5.4-005 | Infraestructura de calibración | D5, D6: partición + provenance + protocolo | HITO 5.4 E-5.4-018, E-5.4-021 |
| DC-5.4-006 | Protocolo de calibración empírica | D5: definir experimento antes de algoritmo | HITO 5.4 E-5.4-019 |
| DC-5.4-007 | Política de partición de datasets | D7: método estadístico definido por protocolo científico | HITO 5.4 E-5.4-020 |
| DF-18 | Semántica de fallo de entry points | D8: exit codes diferenciados, cero fallos silenciosos | HITO 5.2 GAP-5.2-01 |

---

## 11. DEFINITION OF DONE (DoD) DE LA FASE 5

La Fase 5 se considerará oficialmente finalizada cuando se cumplan las siguientes condiciones:

### Fase 5 — Materialización y Certificación

1. **Corpus Canónico Materializado:** Mínimo 20 documentos con cobertura de traits verificada por inspección de contenido, catalogados y sellados en disco bajo la firma global $H_{baseline}$.
2. **Zero Partial Sealing Ejecutado:** Correspondencia biyectiva completa $N_{PDF} = N_{GT}$ verificada por `BaselineCompletenessVerifier`.
3. **Identidad Criptográfica Verificada:** Todos los oracle_hash recomputados bajo el contrato vigente con node_ids canónicos.
4. **Manifest en Formato Actual:** Formato de 6 dimensiones (document_id, sha256, traits, page_count, oracle_hash, ground_truth_state).
5. **Infraestructura de Calibración Operativa:** Partición de datasets basada en content identity, Calibration Provenance Record (5 campos mínimos), protocolo de calibración empírica definido.
6. **Parámetros Calibrados Empíricamente:** Pesos de criticidad y thresholds de NSS validados contra el corpus canónico con separación de datasets.
7. **Motor Canónico Congelado:** ZhangShasha + CriticalityAwareCostContext como motor exclusivo de certificación, con configuración canónica identificada y congelada.
8. **Semántica de Fallo Uniforme:** Todos los entry points de certificación con exit codes diferenciados (DF-18 resuelto).
9. **Regression Gates Materializados:** `CanonicalRegressionGate` implementado, ejecutable y verificable contra la Baseline certificada (fuera de CI).
10. **Verificación Estática Limpia:** Analizadores estáticos con 0 errors, 0 warnings. Suite de pruebas en verde.

### Fase 6 — Integración CI/CD (fuera del alcance de este DoD)

* Regression Gates integrados en pipeline de CI/CD.

---

## 12. REGLA DE ORO DE LA FASE 5

> **La Baseline Científica no se construye porque parece razonable; se certifica porque cada propiedad crítica tiene evidencia reproducible.**

> **No se certifica una baseline sobre un corpus INELIGIBLE. No se calibra sobre los mismos datos con los que se evalúa. Un script no es un protocolo científico. Un número elegido heurísticamente no es un número calibrado.**

> **Un indicio no es evidencia. Un nombre de archivo que sugiere un trait no demuestra la presencia de ese trait. La cobertura real requiere inspección de contenido.**

> **No se elimina una implementación porque "parece redundante". Se elimina únicamente cuando la equivalencia requerida, el dominio de validez y el impacto arquitectónico han sido demostrados y posteriormente aprobados mediante ADR.**

> **Una consecuencia lógica no demostrada empíricamente no equivale a una demostración.**

> **Calibration ≠ Evaluation. Los datos utilizados para calibrar parámetros no pueden ser utilizados como evidencia independiente de evaluación.**

---

**Estado:** FROZEN v1.0.0
**Siguiente paso:** Promulgación de NADRs de Fase 5 (NADR-F17BIS-20 a NADR-F17BIS-24), seguida de redacción de PHASE_17BIS_FASE5_EXECUTION_PLAN.md.