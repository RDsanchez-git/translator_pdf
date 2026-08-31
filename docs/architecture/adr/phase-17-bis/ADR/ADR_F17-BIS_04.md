# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17-BIS_04: Scientific Verification — Topological Regression, Semantic Recall & Criticality

* **Estado:** FROZEN
* **Versión:** 1.0.0
* **Fecha de Emisión:** 2026-08-30
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** Fase 17-BIS (Scientific Baseline / Canonical Corpus)
* **Evidencia Forense Vinculante:** HITO_4.1 (E-4.1-001 a E-4.1-022, GAP-4.1-01 a GAP-4.1-07), HITO_4.2 (E-4.2-001 a E-4.2-015, GAP-4.2-01 a GAP-4.2-07), HITO_4.3 (E-4.3-001 a E-4.3-008, GAP-4.3-01 a GAP-4.3-07), HITO_4.4 (E-4.4-001 a E-4.4-015, GAP-4.4-01 a GAP-4.4-13), HITO_4.5 (E-4.5-001 a E-4.5-008, GAP-4.5-01 a GAP-4.5-07), HITO_0.4.4_C1 (E-0.4-301 a E-0.4-310), HITO_0.4.4_C2 (E-0.4-321 a E-0.4-332), HITO_0.4.4_C5 (E-0.4-381 a E-0.4-390)
* **Referencias Cruzadas:**
  * **Depende de:** ADR_F17_BIS_MASTER (FROZEN), ADR_F17-BIS_01, ADR_F17-BIS_02, ADR_F17-BIS_03
  * **Implementado por:** NADR-F17BIS-18 (Taxonomía de Criticidad de Nodos), NADR-F17BIS-19 (Reglas de Regresión Topológica), NADR-F17BIS-20 (Semántica de Evaluación Graduada)
  * **Ejecutado por:** PHASE_17BIS_FASE4_EXECUTION_PLAN.md
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 17-BIS (Scientific Baseline / Canonical Corpus), conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-08-30 | Emisión inicial. Decisión arquitectónica de la Fase 4 (Scientific Verification). Taxonomía y pesos de criticidad reformulados como "propuesta inicial sujeta a validación empírica". Doble mecanismo de protección explícito. Verificación de ground_truth_state == SEALED explícita. |

---

## 1. CONTEXTO Y JUSTIFICACIÓN

Las Fases 1, 2 y 3 de la Fase 17-BIS han establecido los fundamentos arquitectónicos necesarios para la certificación científica: la alineación del pipeline de producción (Fase 1), la ontología del oráculo y el ciclo de vida del Ground Truth (Fase 2), y el modelo de identidad y confianza criptográfica (Fase 3). Con la baseline sellada (`SealedOracle`), la identidad semántica del oráculo (`oracle_hash`), la firma global del manifiesto (`manifest_hash`), y los contratos de dominio formalizados (`DocumentId`, `NodeId`, `GroundTruthState`), el sistema posee ahora una referencia canónica inmutable contra la cual evaluar cualquier desviación.

Sin embargo, la auditoría forense de la Fase 0 (HITO_0.4.4_C1 a C5) y la Fase 4 (HITO_4.1 a 4.5) han demostrado que el repositorio carece de la infraestructura necesaria para ejecutar la regresión científica graduada. Aunque existe un motor topológico funcional (`ZhangShashaEngine`, `EntityRecallEvaluator`) y una infraestructura de benchmark madura (`TopologyBenchmarkService`, `run_benchmark.py`), no existe ningún mecanismo que conecte el `SealedOracle` con la evaluación topológica, verifique la integridad criptográfica del oráculo antes de evaluar, aplique una taxonomía de criticidad a los nodos del AST, ni emita veredictos graduados (`PASS`/`WARNING`/`HARD_FAIL`) basados en la magnitud de la desviación topológica.

Los Decision Candidates DC-06 (Taxonomía de Criticidad de Nodos) y DC-07 (Reglas de Regresión Topológica), declarados en el ADR Maestro §8, permanecen sin materialización operativa. Sin su resolución, la Fase 5 (Baseline Certification) no puede certificar que la baseline canónica protege efectivamente contra regresiones estructurales, ni la Fase 6 (Continuous Verification) puede integrar compuertas de regresión en CI/CD que bloqueen fusiones ante desviaciones topológicas.

---

## 2. PROBLEMA ARQUITECTÓNICO

El problema arquitectónico de la Fase 4 es la ausencia de un contrato de dominio que gobierne la regresión científica graduada del runtime contra el oráculo sellado. El sistema posee la infraestructura topológica y la baseline sellada, pero carece del mecanismo que conecte ambos mundos y emita juicios de calidad basados en la magnitud de la desviación.

Las dimensiones estructurales afectadas son:

1. **Dimensión de Criticidad:** No existe taxonomía que clasifique los nodos del AST por su impacto científico. Una ecuación perdida tiene el mismo peso que un caption ausente, lo que impide priorizar las desviaciones que destruyen contenido científico primario frente a las que degradan elementos auxiliares.
2. **Dimensión de Veredicto Graduado:** No existe mecanismo que emita juicios diferenciados (`PASS`/`WARNING`/`HARD_FAIL`) basados en la magnitud de la desviación topológica. El sistema actual solo puede comparar binariamente (pasa/falla), sin graduar la severidad de la desviación.
3. **Dimensión de Conexión Baseline→Evaluación:** No existe adaptador que conecte el `SealedOracle` con la evaluación topológica, verifique la integridad criptográfica del oráculo antes de evaluar, verifique el estado de ciclo de vida (`ground_truth_state == SEALED`), y produzca un veredicto de regresión. El pipeline actual evalúa candidatos contra Ground Truth genérico, no contra el oráculo sellado.
4. **Dimensión de Entry Point de Regresión:** No existe entry point dedicado que ejecute la evaluación de regresión del runtime contra el oráculo sellado. El `run_benchmark.py` actual evalúa extractores contra Ground Truth, pero no evalúa el pipeline de producción contra el oráculo sellado.

Las consecuencias de no resolver este problema son:

* **La Fase 5 (Baseline Certification) no puede certificar la baseline:** Sin taxonomía de criticidad ni reglas de regresión graduada, no se puede certificar que la baseline protege efectivamente contra regresiones estructurales.
* **La Fase 6 (Continuous Verification) no puede integrar compuertas de regresión en CI/CD:** Sin entry point de regresión ni veredictos graduados, no se pueden integrar compuertas que bloqueen fusiones ante desviaciones topológicas.
* **Las regresiones topológicas pasan desapercibidas:** Sin taxonomía de criticidad, una ecuación perdida tiene el mismo peso que un caption ausente, lo que impide priorizar las desviaciones que destruyen contenido científico primario.
* **El benchmark no evalúa el pipeline de producción:** El `run_benchmark.py` actual evalúa extractores contra Ground Truth, pero no evalúa el pipeline de producción contra el oráculo sellado.

---

## 3. DECISIÓN ARQUITECTÓNICA

**La regresión científica del runtime contra el oráculo sellado se gobierna mediante un contrato de dominio que clasifica los nodos del AST por criticidad, emite veredictos graduados basados en la magnitud de la desviación topológica, y conecta el `SealedOracle` con la evaluación topológica mediante un adaptador dedicado que verifica la integridad criptográfica y el estado de ciclo de vida del oráculo antes de evaluar.**

En consecuencia:

* La taxonomía de criticidad clasifica los nodos del AST en tres niveles (`CRITICAL`, `WARNING`, `INFO`) basados en su impacto científico. La taxonomía específica y los pesos de criticidad constituyen una **propuesta inicial sujeta a validación empírica** mediante benchmark comparativo sobre el corpus canónico. El NADR-F17BIS-18 materializará la taxonomía definitiva basada en evidencia empírica.
* El veredicto de regresión se basa en **dos mecanismos complementarios**: (1) el NSS ponderado por criticidad, que captura la desviación estructural gradual; y (2) la regla de pérdida de nodo CRITICAL, que emite `HARD_FAIL` independiente del NSS ante la pérdida de cualquier nodo `CRITICAL`. Ambos mecanismos son necesarios y complementarios. `HARD_FAIL` se emite ante pérdida de nodos `CRITICAL` o desviación estructural severa, `WARNING` ante pérdida de nodos `WARNING` o desviación estructural moderada, y `PASS` ante ausencia de desviación significativa.
* El adaptador baseline→evaluación conecta el `SealedOracle` con la evaluación topológica, verifica la integridad criptográfica del oráculo mediante `oracle_hash`, verifica la completitud biyectiva mediante `BaselineCompletenessVerifier`, verifica el estado de ciclo de vida (`ground_truth_state == SEALED`), y produce un veredicto de regresión graduado. No se evalúa contra un oráculo que no esté en estado `SEALED`.
* El entry point de regresión ejecuta la evaluación de regresión del runtime contra el oráculo sellado, reutilizando el composition root `build_extraction_pipeline()` para generar el AST del runtime, y emite un veredicto de regresión graduado por documento y por corpus.

---

## 4. OBJETIVO DE LA SUBFASE

La Fase 4 (Scientific Verification) establece el contrato de dominio que gobierna la regresión científica graduada del runtime contra el oráculo sellado. Esta subfase no construye nueva infraestructura topológica (el motor `ZhangShashaEngine` y el `EntityRecallEvaluator` ya existen); su objetivo es conectar la baseline sellada con la evaluación topológica, definir la taxonomía de criticidad de nodos, establecer las reglas de regresión graduada, y crear el entry point de regresión que ejecute la evaluación del runtime contra el oráculo sellado.

El objetivo primordial es garantizar que:
> *"La regresión científica del runtime contra el oráculo sellado se evalúa de forma determinista, graduada y reproducible, clasificando los nodos del AST por criticidad, emitiendo veredictos basados en la magnitud de la desviación topológica, y verificando la integridad criptográfica y el estado de ciclo de vida del oráculo antes de evaluar."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance

* Definición de la taxonomía de criticidad de nodos (`NodeCriticality`) que clasifica los nodos del AST en tres niveles (`CRITICAL`, `WARNING`, `INFO`) basados en su impacto científico (propuesta inicial sujeta a validación empírica).
* Definición de las reglas de regresión graduada (`RegressionVerdict`) que emiten tres juicios diferenciados (`PASS`, `WARNING`, `HARD_FAIL`) basados en la magnitud de la desviación topológica, incluyendo el doble mecanismo de protección (NSS ponderado + regla de pérdida CRITICAL).
* Definición del contexto de costos ponderados por criticidad (`CriticalityAwareCostContext`) que extiende `TreeEditCostContext` para aplicar penalizaciones diferenciadas según la criticidad del nodo.
* Definición del adaptador baseline→evaluación que conecta el `SealedOracle` con la evaluación topológica, verifica la integridad criptográfica del oráculo, verifica el estado de ciclo de vida (`ground_truth_state == SEALED`), y produce un veredicto de regresión graduado.
* Definición del entry point de regresión que ejecuta la evaluación de regresión del runtime contra el oráculo sellado.
* Definición de los prerrequisitos de testing que deben satisfacerse antes de que la regresión graduada pueda ser efectiva.
* Materialización de DC-06 (Taxonomía de Criticidad de Nodos) y DC-07 (Reglas de Regresión Topológica) declarados en el ADR Maestro §8.

### Fuera del Alcance (Out of Scope)

* **NO** construir nueva infraestructura topológica (el motor `ZhangShashaEngine`, el `EntityRecallEvaluator`, y las políticas de alineamiento y particionamiento ya existen y están auditados por HITO_4.1). Pertenece a Fase 0 (completada).
* **NO** construir nueva infraestructura de benchmark (el `TopologyBenchmarkService`, `run_benchmark.py`, y los formateadores de reporte ya existen y están auditados por HITO_0.4.4_C1). Pertenece a Fase 0 (completada).
* **NO** definir la ontología del oráculo ni el ciclo de vida del Ground Truth. Pertenece a Fase 2 (completada).
* **NO** definir el modelo de identidad ni los contratos de dominio criptográficos. Pertenece a Fase 3 (completada).
* **NO** certificar la baseline canónica ni ejecutar el sellado criptográfico. Pertenece a Fase 5.
* **NO** integrar compuertas de regresión en CI/CD. Pertenece a Fase 6.
* **NO** optimizar el rendimiento del motor topológico ni de la evaluación de regresión. Pertenece a Fase 18 (Advanced Local Runtime).

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

Las invariantes específicas de esta subfase que no están en el Maestro se declaran aquí como principios:

* **Principio de Criticidad Graduada:** La regresión científica no es coincidencia binaria. La evaluación debe graduar la severidad de la desviación topológica basándose en la criticidad de los nodos afectados. Una ecuación perdida no tiene el mismo peso que un caption ausente.
* **Principio de Verificación Previo:** Antes de evaluar el runtime contra el oráculo sellado, se debe verificar la integridad criptográfica del oráculo mediante `oracle_hash`, la completitud biyectiva mediante `BaselineCompletenessVerifier`, y el estado de ciclo de vida (`ground_truth_state == SEALED`). No se evalúa contra un oráculo no verificado o que no esté en estado `SEALED`.
* **Principio de Reutilización del Composition Root:** El entry point de regresión reutiliza el composition root `build_extraction_pipeline()` para generar el AST del runtime. No se crea un pipeline de extracción separado para regresión.
* **Principio de Veredicto Graduado con Doble Mecanismo:** El veredicto de regresión emite tres juicios diferenciados (`PASS`/`WARNING`/`HARD_FAIL`) basados en dos mecanismos complementarios: (1) el NSS ponderado por criticidad para desviación gradual, y (2) la regla de pérdida de nodo CRITICAL para protección absoluta. No se emite un juicio binario (pasa/falla).

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

Tras la implementación de esta subfase, la arquitectura de regresión científica del sistema queda estructurada de la siguiente forma:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REGRESSION SCIENTIFIC GATE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────────────────────┐   │
│  │  SealedOracle       │         │  Runtime Pipeline (build_extraction_ │   │
│  │  (Baseline Sellada) │         │  pipeline())                         │   │
│  │  - document_id      │         │  - ExtractionProvider                │   │
│  │  - nodes: Tuple[    │         │  - DocumentLayoutValidator           │   │
│  │      ASTNode, ...]  │         │  - FlatASTBuilder                    │   │
│  │  - oracle_hash      │         │  → Runtime AST: List[ASTNode]        │   │
│  └──────────┬──────────┘         └──────────────────┬──────────────────┘   │
│             │                                       │                       │
│             ▼                                       ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              RegressionAdapter (Adaptador Baseline→Evaluación)      │   │
│  │  1. Verificar oracle_hash (OracleSemanticIdentityCalculator)        │   │
│  │  2. Verificar completitud biyectiva (BaselineCompletenessVerifier)  │   │
│  │  3. Verificar ground_truth_state == SEALED                          │   │
│  │  4. Cargar SealedOracle desde disco                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│             │                                       │                       │
│             ▼                                       ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              RegressionEvaluationStrategy                            │   │
│  │  1. Evaluar TED (ZhangShashaEngine + CriticalityAwareCostContext)   │   │
│  │  2. Evaluar Recall (EntityRecallEvaluator por tipo CRITICAL)        │   │
│  │  3. Aplicar Reglas de Regresión (RegressionVerdict)                 │   │
│  │     - Mecanismo 1: NSS ponderado por criticidad (protección gradual)│   │
│  │     - Mecanismo 2: Pérdida de nodo CRITICAL (protección absoluta)   │   │
│  │  4. Emitir veredicto graduado (PASS/WARNING/HARD_FAIL)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              RegressionVerdict (Veredicto Graduado)                  │   │
│  │  - PASS: Sin desviación significativa                               │   │
│  │  - WARNING: Desviación estructural moderada                         │   │
│  │  - HARD_FAIL: Pérdida de nodos CRITICAL o desviación severa         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              NodeCriticality (Taxonomía de Criticidad)               │   │
│  │  PROPUESTA INICIAL (sujeta a validación empírica en NADR-18):       │   │
│  │  - CRITICAL: DISPLAY_EQUATION, INLINE_EQUATION, TABLE_SIMPLE,       │   │
│  │              TABLE_COMPLEX                                           │   │
│  │  - WARNING:  HEADING, PARAGRAPH, CODE                               │   │
│  │  - INFO:     IMAGE, CAPTION, LIST, COMPOSITE_BLOCK                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              CriticalityAwareCostContext                             │   │
│  │  PROPUESTA INICIAL (sujeta a validación empírica en NADR-18):       │   │
│  │  Extiende TreeEditCostContext con penalizaciones ponderadas:         │   │
│  │  - CRITICAL: peso ponderado (pérdida de contenido científico prim.) │   │
│  │  - WARNING:  peso ponderado (pérdida de estructura significativa)   │   │
│  │  - INFO:     peso ponderado (pérdida de elementos auxiliares)       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

NOTA: La taxonomía de criticidad y los pesos de criticidad mostrados en este
diagrama son propuestas iniciales basadas en la evidencia forense de HITO_4.2.
La taxonomía final y los pesos definitivos serán definidos por el NADR-F17BIS-18
basándose en evidencia empírica (benchmark comparativo sobre el corpus canónico).
```

La invariante del estado objetivo:
> *"La regresión científica del runtime contra el oráculo sellado se evalúa de forma determinista, graduada y reproducible, verificando la integridad criptográfica y el estado de ciclo de vida del oráculo antes de evaluar, clasificando los nodos por criticidad, y emitiendo veredictos basados en la magnitud de la desviación topológica mediante un doble mecanismo de protección."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la Fase 4 (Scientific Verification). Resuelve DC-06 y DC-07 declarados en el Maestro §8. | ✅ |
| `ADR_F17-BIS_01.md` | Este ADR depende de la alineación del pipeline de producción establecida en Fase 1. | ✅ |
| `ADR_F17-BIS_02.md` | Este ADR depende de la ontología del oráculo y el ciclo de vida del Ground Truth establecidos en Fase 2. | ✅ |
| `ADR_F17-BIS_03.md` | Este ADR depende del modelo de identidad y los contratos de dominio criptográficos establecidos en Fase 3. | ✅ |
| `NADR-F17BIS-18` | Implementa la taxonomía de criticidad de nodos (DC-06) definida en este ADR. | ✅ |
| `NADR-F17BIS-19` | Implementa las reglas de regresión topológica (DC-07) definidas en este ADR. | ✅ |
| `NADR-F17BIS-20` | Implementa la semántica de evaluación graduada definida en este ADR. | ✅ |
| `PHASE_17BIS_FASE4_EXECUTION_PLAN.md` | Secuencia las tareas que materializan este ADR. | ✅ |
| `HITO_4.1` | Evidencia forense de la infraestructura topológica existente. | ✅ |
| `HITO_4.2` | Evidencia forense de la ausencia de taxonomía de criticidad y reglas de regresión. | ✅ |
| `HITO_4.3` | Evidencia forense de la ausencia de adaptador baseline→evaluación y entry point de regresión. | ✅ |
| `HITO_4.4` | Evidencia forense de los prerrequisitos de testing no satisfechos. | ✅ |
| `HITO_4.5` | Evidencia forense del pipeline de producción y el composition root reutilizable. | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.