# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17_BIS_01: Production Pipeline Alignment

* **Estado:** FROZEN
* **Versión:** 1.1.0
* **Fecha de Emisión:** 2026-08-04
* **Fecha de Última Actualización:** 2026-08-04
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** 17-BIS (Scientific Baseline / Canonical Corpus)
* **Capacidades Afectadas:** Las definidas por el ADR Maestro que resulten afectadas por esta subfase.
* **Evidencia Forense Vinculante:** HITO_0.1, HITO_0.2, HITO_0.3, HITO_0.4.1, HITO_0.4.2, HITO_0.4.3, HITO_0.4.4, HITO_0.4.5, HITO_0.5 (Gap Matrix)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER.md` (ADR Maestro de la Fase 17-BIS)
  * **Implementado por:** NADR-01 a NADR-11 (reglas normativas de la Fase 1)
  * **Ejecutado por:** `PHASE_17BIS_EXECUTION_PLAN.md`
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 17-BIS, conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase.

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 0 (Architecture & Baseline Audit Gate) demostró mediante evidencia forense irrebatible que el pipeline de producción real del sistema diverge críticamente de la arquitectura teórica declarada en las Fases 16 y 17.

El benchmark topológico (Fase 17) seleccionó a un proveedor de extracción basándose en métricas estadísticas. Sin embargo, la auditoría forense reveló la "Ilusión del Benchmark": el laboratorio de evaluación medía una ruta *legacy* aislada, mientras el pipeline productivo real operaba fracturado y con múltiples inconsistencias.

---

## 2. PROBLEMA ARQUITECTÓNICO

La divergencia entre la teoría y la práctica en tiempo de ejecución (runtime) se manifiesta en cuatro dimensiones estructurales documentadas en la evidencia forense (Hitos 0.1 a 0.4.5):

1. **Módulos Zombis:** Componentes de dominio de grado científico, completamente implementados y probados, que jamás son invocados en el *runtime* productivo.
2. **Bypasses Procedimentales:** Fugas de lógica de negocio hacia módulos de infraestructura o utilidades, saltando las fronteras del dominio.
3. **Dualidad Operacional:** Dos planos de ejecución divergentes (CLI *in-process* vs. Daemons distribuidos) que no comparten la misma orquestación.
4. **Falsas Garantías de Regresión:** Compuertas de evaluación en Integración Continua (CI) que operan bajo aserciones tautológicas, incapaces de detener regresiones estructurales.

La persistencia de esta divergencia produce tres consecuencias arquitectónicas:
* **Imposibilidad de certificación:** El oráculo científico se construiría y validaría contra un pipeline incorrecto.
* **Invalidez del benchmark:** Las métricas de laboratorio no reflejan el comportamiento ni el rendimiento del entorno productivo.
* **Imposibilidad de evolucionar hacia la Fase 18:** Optimizar o introducir asincronía en un pipeline fracturado únicamente agravaría la fractura.

---

## 3. DECISIÓN ARQUITECTÓNICA

La organización adopta la **Production Pipeline Alignment** (Alineación del Pipeline de Producción) como **prerrequisito obligatorio** para toda actividad relacionada con la *Scientific Baseline*.

En consecuencia:
* Ninguna baseline podrá certificarse o validarse sobre un pipeline que no esté alineado con la arquitectura teórica.
* Toda alineación estructural del *runtime* de producción deberá realizarse **antes** de la certificación científica.
* Las capacidades arquitectónicas definidas por el ADR Maestro que resulten afectadas por esta subfase serán materializadas progresivamente mediante normativas estrictas (NADRs) y ejecutadas a través de planes operativos (*Execution Plans*).

---

## 4. OBJETIVO DE LA SUBFASE

Alinear el pipeline de producción real con la arquitectura de dominio declarada, eliminando cortocircuitos, conectando los módulos aislados y unificando el plano de ejecución.

El objetivo primordial es garantizar que:
> *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta, y lo que producción ejecuta es exactamente lo que la arquitectura declara."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance
* Alineación estructural de las brechas de integridad, determinismo y Clean Architecture documentadas en la Fase 0.
* Unificación de la orquestación entre todos los puntos de entrada (CLI y Daemons).
* Reintegración de la lógica de dominio inactiva al flujo principal de producción.
* Aislamiento de I/O y aseguramiento del estado transaccional (CQRS/FSM).
* Habilitación de compuertas remotas de Integración Continua (CI).

### Fuera del Alcance (Out of Scope)
* **NO** construir ni certificar la Scientific Baseline (corresponde a las sub-fases posteriores de la 17-BIS).
* **NO** optimizar rendimiento, concurrencia o uso de memoria (corresponde a la Fase 18).
* **NO** modificar la ontología del AST V2 ni introducir nuevos adaptadores de extracción.

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

El estado objetivo de la arquitectura establece un flujo unidireccional y unificado, donde todo punto de entrada converge en una única raíz de composición y atraviesa el pipeline completo de dominio antes de materializarse.

```text
    Entry Points
          │
          ▼
    Composition Root
          │
          ▼
    Production Pipeline
          │
          ▼
    Execution Services
          │
          ▼
    Artifact Generation & Persistence
```

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la subfase de alineación del pipeline | ✅ |
| `ADR_F17_BIS_0.md` | La evidencia forense de la Fase 0 fundamenta la decisión de este ADR | ✅ |
| `NADR_01` a `NADR_11` | Implementan las reglas normativas derivadas de esta decisión arquitectónica | ✅ |
| `PHASE_17BIS_EXECUTION_PLAN.md` | Secuencia las tareas que materializan este ADR | ✅ |
| `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` | Este ADR actúa en cumplimiento de la metodología de gobernanza | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para la Fase 1.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.