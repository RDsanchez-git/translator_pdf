# ARCHITECTURE DECISION RECORD (ADR)

## ADR_F18.1: Execution Plane & Concurrency

* **Estado:** FROZEN
* **Versión:** 1.0.2
* **Fecha de Emisión:** 2026-10-04
* **Fecha de Congelamiento:** 2026-10-04
* **Autor:** Architecture Board / Staff Engineering
* **Unidad de Gobernanza Parent:** Fase 18 (Advanced Local Runtime)
* **Evidencia Forense Vinculante:** HITO_0.1 v1.2.0 (E-0.1-001 a E-0.1-007, GAP-0.1-01 a GAP-0.1-03), HITO_0.12 v1.0.1 (DC-01, DC-02, DC-05, DC-06b, DF-06), FASE0_AUDIT_CHARTER v1.0.0 §3/§9, ADR_F18_MASTER FROZEN §6.1
* **Referencias Cruzadas:**
  * **Depende de:** ADR_F18_MASTER.md FROZEN (2026-10-04)
  * **Implementado por:** NADRs de la Subfase 18.1 (pendientes de emisión)
  * **Ejecutado por:** PHASE_18.1_EXECUTION_PLAN.md (pendiente de emisión)
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 18, conforme a la arquitectura definida por el ADR_F18_MASTER.md FROZEN. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase. En este documento, "Fase 18" refiere a la unidad de gobernanza de primer nivel y "Subfase 18.1" a esta unidad gobernada.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial |
| 1.0.1 | 2026-10-04 | Corrección de gobernanza: (1) DC-13 eliminado por no existir en el registro canónico. (2) DC-02-A/B reformulados como descomposición operativa interna de DC-02. (3) Frontera admission 18.1/18.3 explicitada. (4) Target State no precongelala composición de scientific identity. (5) Principio de evidencia suavizado a "apropiada a su naturaleza". (6) DF-06 mantenido condicional. (7) "Autoridad exclusiva" sustituida por "unidad de gobierno dentro de límites del Master". (8) Conteo corregido: 4 DC + 1 DF. |
| 1.0.2 | 2026-10-04 | Corrección final de consistencia: (1) Cláusula de estabilidad de la definición provisional de DC-02 frente a DC-12 con invalidación explícita. (2) Target State alineado con el alcance de DC-02 incluyendo estabilidad para DC-12. (3) Dimensiones §2 reformuladas como evidencia no demostrada en lugar de defecto afirmado. (4) Semántica de §8 corregida: NADRs promulgan, Execution Plan materializa. FROZEN. |

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La auditoría forense de Fase 0 (HITO_0.1 v1.2.0) demostró que el execution plane actual opera bajo un modelo híbrido dual: el flujo vía CLI utiliza concurrencia asyncio nativa (AsyncDispatcher con PriorityQueue, E-0.1-003), mientras que el daemon de producción opera a través de un adaptador síncrono (SyncProviderBridge) que introduce una barrera de bloqueo en el hilo llamante (future.result(timeout=180.0), E-0.1-001), con coordinación multi-thread mediante 3 threads independientes y 3 threading.Event separados (E-0.1-002). El impacto cuantitativo de esta barrera en C1 (Bounded Execution) y C3 (Backpressure) no ha sido medido (GAP-0.1-01).

HITO_0.12 v1.0.1 declaró el estado de gobernanza de las decisiones que corresponden a esta subfase: 4 Decision Candidates (DC-01 fork de concurrencia, DC-02 identity científica vs operacional, DC-05 ExecutionContext, DC-06b técnicas del ROADMAP) y 1 Deferred Finding (DF-06 imports cruzados core→apps). Todos están DEFERRED con destino 18.1, triggers explícitos y dependencias documentadas. DC-01 es la raíz del DAG de dependencias de toda Fase 18: DC-08, DC-10, DC-11, DF-24 y DF-34 dependen de su resolución.

La complejidad de esta subfase (4 Decision Candidates + 1 Deferred Finding, 6 capacidades gobernadas, 4 invariantes constitucionales, posición de raíz del DAG) supera el umbral de METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES §3.2, justificando un ADR de subfase propio.

---

## 2. PROBLEMA ARQUITECTÓNICO

El execution plane actual presenta una fractura estructural entre el modelo de concurrencia del pipeline (asyncio nativo) y el modelo de ejecución del daemon de producción (síncrono con puente thread-based). Esta fractura impide demostrar que el sistema opera bajo recursos finitos con concurrencia controlada, backpressure, cancellation e idempotencia.

**Dimensiones estructurales afectadas:**

1. **Modelo de ejecución:** El daemon introduce una barrera de bloqueo en el hilo llamante durante la duración de la llamada LLM (E-0.1-001), dejando sin demostrar el comportamiento de bounded execution y backpressure bajo carga (GAP-0.1-01).

2. **Coordinación de estado:** La coordinación multi-thread mediante 3 threading.Event separados (E-0.1-002) introduce una superficie de coordinación concurrente cuya seguridad frente a condiciones de carrera y cuyo comportamiento de cancelación limpia no han sido demostrados. El impacto en C7 y C10 no ha sido evaluado (GAP-0.1-02).

3. **Identidad de ejecución:** No existe definición congelada de qué parámetros pertenecen a scientific identity y cuáles a operational metadata (GAP-0.4-03, DC-02). Esta ambigüedad impide definir el contrato de comparación del guard diferencial (DC-12, Subfase 18.5).

4. **Fronteras de composición:** Imports cruzados de core/benchmark/runners/ hacia apps/ (E-0.2-005, DF-06) violan la frontera hexagonal y dificultan la evaluación independiente del modelo de concurrencia.

5. **Técnicas candidatas no validadas:** Las técnicas prescritas por el ROADMAP (pure async, elisión de SyncProviderBridge, threads/process pools, object pools, zero-copy, lazy loading) permanecen subordinadas a evidencia; ninguna ha sido medida contra el criterio preregistrado (DC-06b, Charter §9). Existe riesgo de adopción prematura sin demostración de beneficio.

**Consecuencias de no resolver el problema:**

* **Imposibilidad de demostrar INV-SCI-1 bajo variación operacional:** sin frontera de identidad definida, no se puede garantizar que el cambio de modelo de ejecución preserve la verdad científica.
* **Propagación de la decisión DC-01 a toda Fase 18:** DC-08, DC-10, DC-11, DF-24 y DF-34 permanecen bloqueados hasta que DC-01 se resuelva.
* **Riesgo de adopción prematura de técnicas:** sin medición previa, existe riesgo de implementar técnicas candidatas sin evidencia de beneficio, violando Benchmark Before Optimization.

---

## 3. DECISIÓN ARQUITECTÓNICA

> **La Subfase 18.1 constituye la unidad de gobierno arquitectónico de la maduración del modelo de ejecución concurrente del execution plane local, dentro de los límites establecidos por el ADR_F18_MASTER. Toda modificación del runtime que afecte la concurrencia, la cancelación o la identidad de ejecución queda sujeta a la frontera constitucional entre scientific identity, execution identity y operational state. Ninguna técnica de implementación será adoptada sin evidencia de beneficio conforme al criterio preregistrado del Charter §9.**

En consecuencia:

* La resolución de DC-01 requiere evidencia cuantitativa previa (GAP-0.5-02 y GAP-0.1-01 resueltos). No se decide el modelo de ejecución sin medición.

* DC-02 será resuelto mediante una secuencia interna de definición y validación de la frontera de identidad. Esta secuencia no crea nuevos Decision Candidates ni nuevos niveles de autoridad; constituye una descomposición operativa de DC-02. Una definición provisional de la frontera de identidad puede establecerse como prerrequisito para DC-12, siempre que sus dimensiones relevantes para la comparación queden explícitamente fijadas durante la ejecución del guard. La consolidación definitiva de DC-02 deberá confirmar dicha frontera; cualquier modificación posterior que afecte las dimensiones utilizadas por DC-12 invalidará la evidencia dependiente y requerirá su reevaluación conforme a la gobernanza de la Subfase 18.5. La definición provisional no depende de DC-01 (HITO_0.12 §5.3) y puede avanzar en paralelo con su medición.

* La evaluación de DC-05 queda condicionada a DC-01. No se evalúa la estructura de contextos sin conocer el modelo de concurrencia.

* DC-06b es una decisión de Board que evalúa las técnicas del ROADMAP contra el criterio preregistrado. Es una evaluación compartida entre las Subfases 18.1 a 18.4; la Subfase 18.1 aporta la medición de barreras síncronas (GAP-0.1-01). Puede resultar en adopción, rechazo o enmienda del ROADMAP, no necesariamente en resolución técnica.

* DF-06 será evaluado y, si la auditoría confirma la dependencia arquitectónica identificada, su resolución quedará incluida en esta subfase.

* La definición de la semántica de coordinated shutdown pertenece a la Subfase 18.2 cuando resulte necesaria según el modelo de ejecución resuelto por DC-01.

---

## 4. OBJETIVO DE LA SUBFASE

El objetivo primordial es garantizar que:

> *"El execution plane local opera bajo un modelo de ejecución concurrente, acotado por recursos, cancelable y científicamente neutro, cuya modificación no altera la identidad científica ni la verdad del resultado."*

La Subfase 18.1 gobierna la maduración del modelo de ejecución concurrente estableciendo la frontera entre scientific identity, execution identity y operational state, y normando bounded execution, cancellation y minimal operational visibility como capacidades obligatorias. La subfase no prescribe un modelo de ejecución específico (async puro, multi-process, híbrido); esa decisión corresponde a DC-01 y se toma con evidencia cuantitativa durante la ejecución del Execution Plan.

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance

* Maduración del modelo de ejecución concurrente del execution plane local (DC-01)
* Definición de la frontera entre scientific identity, execution identity y operational state (DC-02, mediante descomposición operativa interna)
* Evaluación de la estructura de contextos de ejecución (DC-05, condicionado a DC-01)
* Evaluación de técnicas candidatas del ROADMAP contra criterio preregistrado (DC-06b, decisión de Board)
* Evaluación y eventual resolución de imports cruzados core→apps (DF-06, condicional)
* Bounded execution (C1), admission control como mecanismo de ejecución y coordinación (C2, dimensión de 18.1), backpressure (C3), cancellation (C6), concurrency safety (C7), minimal operational visibility (C11)

### Fuera del Alcance (Out of Scope)

* **NO** journal semantics y recuperación de estado (pertenece a Subfase 18.2, DC-08)
* **NO** admission como política de recursos, fairness y presupuesto (pertenece a Subfase 18.3, DC-10/DC-11; 18.1 gobierna admission como mecanismo de ejecución, 18.3 como política de recursos)
* **NO** resource budgets y batching adaptativo (pertenece a Subfase 18.3, DC-07)
* **NO** provider characterization y cache semantics (pertenece a Subfase 18.4, DC-03/DC-04)
* **NO** differential guard y promoción a CI (pertenece a Subfase 18.5, DC-12)
* **NO** semántica de coordinated shutdown ni lifecycle orchestration (pertenece a Subfase 18.2, cuando resulte necesaria según DC-01)
* **NO** semántica de producto de interrupción (pertenece a Fase 19, DC-09)
* **NO** deep local observability (pertenece a Fase 20)
* **NO** semantic/embedding cache, model routing, parser routing (pertenece a Fase 21)
* **NO** infraestructura distribuida (Redis, brokers, Kubernetes, microservicios), prohibida por ROADMAP v3.0 §I y §V
* **NO** implementación de código durante la emisión de este ADR (regla Audit First, Design Later del ADR Maestro §5.2)

---

## 6. GOBERNANZA DE LA SUBFASE

Esta subfase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (ADR_F18_MASTER.md FROZEN):

* **INV-SCI-1:** Misma baseline sellada + mismos parámetros científicos congelados = misma salida científica, independiente de schedule, concurrencia, budgets y cache.
* **INV-OPS-1:** Las diferencias operacionales no alteran el resultado científico ni falsifican la evidencia científica.
* **INV-EXEC-IDENTIFIABILITY:** El modo/política de ejecución es identificable y reproducible y habilita testing diferencial; excluido de la identity científica.
* **INV-VERIFICATION-ISOLATION:** El verification subject corre sin scheduler ni concurrencia por defecto.

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta subfase**.

**Principios específicos de 18.1 (no son reglas normativas; las reglas van en NADRs):**

1. **Evidencia apropiada a la naturaleza de cada decisión:** Cada Decision Candidate debe resolverse con la evidencia apropiada a su naturaleza; cuando su criterio de resolución sea empírico o cuantitativo, dicha evidencia debe preceder su cierre. DC-01 requiere resolución de GAP-0.5-02 y GAP-0.1-01. DC-05 requiere DC-01 resuelto. DC-06b requiere baseline F0-A completo. DC-02 puede requerir definición contractual y validación experimental. DF-06 puede resolverse mediante análisis de frontera arquitectónica.

2. **Identidad científica intocable:** Ninguna decisión de esta subfase puede alterar la scientific identity ni la scientific baseline. INV-SCI-1 es restricción absoluta.

3. **Técnicas candidatas subordinadas a evidencia:** Las técnicas candidatas del Charter §3 (pure async, elisión de SyncProviderBridge, threads/process pools, object pools, zero-copy, lazy loading) permanecen subordinadas a evidencia de necesidad. No se implementa ninguna sin evidencia de beneficio según el criterio preregistrado (Charter §9).

4. **Coordinated shutdown condicionado a DC-01:** La semántica de coordinated shutdown pertenece a la Subfase 18.2 cuando resulte necesaria según el modelo de ejecución decidido en DC-01. No se diseña lifecycle antes de conocer el modelo de concurrencia.

5. **Minimal operational visibility:** C11 se implementa en esta subfase como capacidad transversal con mínimo contractual. La observabilidad profunda pertenece a F20.

6. **Orden lógico, no cronograma:** La secuencia de decisiones expresa dependencias de gobernanza, no un cronograma operativo. La definición provisional de DC-02 puede avanzar en paralelo con la medición de DC-01 al no existir dependencia entre ellos. La secuenciación concreta de tareas, owners y despliegue corresponde al PHASE_18.1_EXECUTION_PLAN.md.

7. **Frontera de admission explícita:** 18.1 gobierna admission como mecanismo de ejecución y coordinación (cómo entra/sale trabajo del execution plane). 18.3 gobierna admission como política de recursos, fairness y presupuesto (cuándo debe admitirse trabajo según recursos, prioridad y presupuesto).

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

El estado objetivo de la arquitectura tras la implementación de esta subfase es un execution plane donde:

1. El modelo de ejecución concurrente ha sido decidido con evidencia e implementado.
2. La frontera entre scientific identity, execution identity y operational state ha sido definida y validada conforme al alcance de DC-02, incluyendo la estabilidad necesaria para las comparaciones gobernadas por DC-12.
3. La estructura de contextos de ejecución tiene boundaries claros.
4. Las técnicas del ROADMAP han sido evaluadas contra criterio preregistrado.
5. Los imports cruzados core→apps han sido evaluados y, si se confirma la dependencia, eliminados.
6. Bounded execution, cancellation y minimal operational visibility están implementados y verificados.

    TARGET STATE — SUBFASE 18.1

    +-----------------------------------------------------------+
    | SCIENTIFIC IDENTITY (invariante, intocable)                |
    | baseline sellada                                           |
    | + parámetros científicos congelados                        |
    | + dimensiones de identidad definidas por DC-02             |
    +-----------------------------------------------------------+
                             |
                       no altera
                             |
    +-----------------------------------------------------------+
    | EXECUTION IDENTITY (identificable, reproducible)           |
    | modelo de concurrencia + política de ejecución             |
    | + parámetros operacionales identificables                  |
    +-----------------------------------------------------------+
                             |
                        produce
                             |
    +-----------------------------------------------------------+
    | OPERATIONAL STATE (observable, puede diferir)              |
    | scheduling order, retry timing, resource utilization       |
    | (C11: minimal operational visibility)                      |
    +-----------------------------------------------------------+

    CAPACIDADES GOBERNADAS:
    C1 Bounded Execution --- C3 Backpressure --- C6 Cancellation
    C2 Admission Control (mecanismo) --- C7 Concurrency Safety
    C11 Operational Visibility (ámbito: 18.1, transversal)

> *"El execution plane opera bajo un modelo de ejecución concurrente decidido con evidencia, donde la modificación del mecanismo de ejecución no constituye una nueva interpretación científica del documento."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| ADR_F18_MASTER.md FROZEN | Este ADR particulariza las decisiones del Maestro para la Subfase 18.1 | Sí |
| HITO_0.1 v1.2.0 | Evidencia forense de concurrencia (E-0.1-001 a E-0.1-007) | Sí |
| HITO_0.12 v1.0.1 | Estado de gobernanza de DC-01, DC-02, DC-05, DC-06b, DF-06 | Sí |
| FASE0_AUDIT_CHARTER.md v1.0.0 | Capacidades C1-C13, técnicas candidatas, criterio preregistrado §9 | Sí |
| NADRs de 18.1 (pendientes) | Promulgan las reglas normativas que desarrollan esta decisión arquitectónica | Sí |
| PHASE_18.1_EXECUTION_PLAN.md (pendiente) | Secuencia las tareas que materializan esta decisión y sus obligaciones normativas; define el DoD operativo | Sí |
| ADR_F18.2 (pendiente) | DC-08 depende de DC-01 resuelto en esta subfase; coordinated shutdown condicionado a DC-01 | Sí |
| ADR_F18.3 (pendiente) | DC-07, DC-10, DC-11 dependen de DC-01 resuelto en esta subfase; gobierna admission como política de recursos | Sí |
| ADR_F18.5 (pendiente) | DC-12 depende de la definición provisional de DC-02 resuelta en esta subfase; sujeto a cláusula de invalidación §3 | Sí |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el Architecture Governance Framework definido en METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0.

* **Este ADR** define exclusivamente la visión arquitectónica de la subfase 18.1 (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el PHASE_18.1_EXECUTION_PLAN.md.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.