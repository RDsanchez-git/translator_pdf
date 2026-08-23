# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F{FASE}_{XX}: {Título de la Subfase}

* **Estado:** {DRAFT | APPROVED | FROZEN | SUPERSEDED}
* **Versión:** {X.Y.Z}
* **Fecha de Emisión:** {YYYY-MM-DD}
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** {Fase a la que pertenece} ({Nombre de la Fase})
* **Evidencia Forense Vinculante:** {IDs de HITOs, Findings, Observaciones}
* **Referencias Cruzadas:**
  * **Depende de:** {ADR Maestro, otros ADRs de Fase}
  * **Implementado por:** {NADRs que materializan esta decisión}
  * **Ejecutado por:** {Execution Plan que secuencia las tareas}
  * **Conflictúa con:** {Otros ADRs si aplica, o "Ninguno"}

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la {Fase Parent}, conforme a la arquitectura definida por el `{ADR_PARENT_MASTER.md}`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase.

---

## 1. CONTEXTO Y JUSTIFICACIÓN

{Descripción del estado actual que motiva la decisión. Debe referenciar evidencia forense concreta con IDs. Máximo 3 párrafos.}

---

## 2. PROBLEMA ARQUITECTÓNICO

{Descripción del problema en términos arquitectónicos abstractos. No en términos de código.}

{Lista de dimensiones estructurales afectadas:}
1. **{Dimensión 1}:** {Descripción}
2. **{Dimensión 2}:** {Descripción}
3. **{Dimensión N}:** {Descripción}

{Consecuencias de no resolver el problema:}
* **{Consecuencia 1}**
* **{Consecuencia 2}**
* **{Consecuencia N}**

---

## 3. DECISIÓN ARQUITECTÓNICA

{Una única sentencia ejecutiva clara que define la decisión. Debe poder leerse como una ley permanente. No es una lista de tareas ni una descripción de implementación.}

En consecuencia:
* {Implicación directa 1}
* {Implicación directa 2}
* {Implicación directa N}

---

## 4. OBJETIVO DE LA SUBFASE

{Descripción concisa del objetivo. Máximo 2 párrafos.}

El objetivo primordial es garantizar que:
> *"{Cita rectora que define el invariant de la subfase}"*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance
* {Alcance 1}
* {Alcance 2}
* {Alcance N}

### Fuera del Alcance (Out of Scope)
* **NO** {No-objetivo 1} ({justificación y a qué fase pertenece})
* **NO** {No-objetivo 2} ({justificación y a qué fase pertenece})
* **NO** {No-objetivo N} ({justificación y a qué fase pertenece})

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`{ADR_PARENT_MASTER.md}`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

{Si hay invariantes específicas de la subfase que no están en el Maestro, se declaran aquí como principios, NO como reglas normativas.}

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

{Descripción del estado objetivo de la arquitectura tras la implementación de esta subfase.}

```text
{Diagrama de flujo o estructura del estado objetivo}
```

{Invariante del estado objetivo:}
> *"{Cita que define el invariant del target state}"*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `{ADR_PARENT_MASTER.md}` | Este ADR particulariza las decisiones del Maestro para la subfase | ✅ |
| `{NADR_XX.md}` | Implementa la regla {R-XX-Y.Z} de este ADR | ✅ |
| `{NADR_YY.md}` | Implementa la regla {R-YY-W.V} de este ADR | ✅ |
| `{PHASE_XX_EXECUTION_PLAN.md}` | Secuencia las tareas que materializan este ADR | ✅ |
| `{Otro ADR de Fase}` | {Relación si aplica} | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.