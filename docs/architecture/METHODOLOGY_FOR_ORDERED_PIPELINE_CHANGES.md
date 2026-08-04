# METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
## Metodología General para Cambios Ordenados en el Pipeline del Traductor

* **Versión:** 1.0.0
* **Estado:** FROZEN
* **Fecha de Emisión:** 2026-08-04
* **Autoridad:** Architecture Board
* **Alcance:** Todas las fases futuras del proyecto (17-BIS en adelante)
* **Ubicación:** `docs/adr/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`

---

## 1. PROPÓSITO Y ALCANCE

Este documento define la metodología única y obligatoria para planificar, gobernar e implementar cambios arquitectónicos en el pipeline del traductor. Es aplicable a todas las fases futuras del proyecto.

Su objetivo es garantizar que:

- Todo cambio esté respaldado por evidencia forense antes de implementarse.
- La gobernanza arquitectónica esté separada de la ejecución operativa.
- La trazabilidad sea completa desde la visión hasta el commit.
- No se introduzca sobreingeniería documental.
- Cada documento tenga una única responsabilidad y no invada la de otros.

### Principio rector

> La documentación existe para habilitar implementación de calidad, no para existir. Cada artefacto documental debe justificar que reduce complejidad futura más de lo que añade complejidad presente.

---

## 2. JERARQUÍA DE GOBERNANZA

La gobernanza del proyecto se estructura en una pirámide de autoridad donde cada nivel responde una pregunta distinta:

```text
ROADMAP ARQUITECTÓNICO
│
│ ¿Hacia dónde va el proyecto?
▼
ADR MAESTRO (por fase)
│
│ ¿Por qué existe esta fase? ¿Qué capacidades requiere?
▼
ADR DE FASE (opcional, por sub-fase)
│
│ ¿Cuál es la decisión arquitectónica de esta sub-fase?
▼
NADRs (Normative Architecture Decision Records)
│
│ ¿Qué reglas son obligatorias? (constitución permanente)
▼
EXECUTION PLAN
│
│ ¿Cómo, cuándo y quién implementa cada regla?
▼
IMPLEMENTACIÓN
│
│ ¿Qué código materializa cada tarea?
▼
TESTS / CI
  ¿Cómo se verifica que la regla se cumple?
```

### Regla de autoridad

> Ningún nivel inferior tiene autoridad para redefinir o contradecir decisiones establecidas por un nivel superior. La modificación de un nivel superior requiere un proceso explícito de decisión arquitectónica.

---

## 3. TAXONOMÍA DOCUMENTAL

Cada tipo de documento tiene una responsabilidad única e intransferible. La violación de estas fronteras es un defecto de gobernanza.

### 3.1 ADR Maestro

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Por qué existe la fase? ¿Qué capacidades arquitectónicas requiere? |
| **Contiene** | Contexto, problema, decisión, alcance, no-objetivos, invariantes, sub-fases |
| **NO contiene** | Tareas de implementación, nombres de clases, secuencias operativas |
| **Estado** | FROZEN una vez aprobado |
| **Modificación** | Requiere nuevo ADR |

### 3.2 ADR de Fase (opcional)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Cuál es la decisión arquitectónica de una sub-fase específica? |
| **Contiene** | Problema, decisión ejecutiva, alcance, relación con el ADR Maestro |
| **NO contiene** | Reglas normativas detalladas, tareas de implementación |
| **Estado** | FROZEN una vez aprobado |
| **Cuándo usar** | Solo cuando una sub-fase tiene suficiente complejidad para requerir su propio documento de visión |

### 3.3 NADR (Normative Architecture Decision Record)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Qué reglas son obligatorias? ¿Qué está permitido, prohibido o requerido? |
| **Contiene** | Reglas normativas abstractas (RFC 2119), evidencia forense, consecuencias, frontera normativa |
| **NO contiene** | Nombres de clases en reglas, tareas de implementación, Definition of Done, cronogramas |
| **Naturaleza** | Constitución permanente. No pertenece a una fase específica. Gobierna capacidades. |
| **Estado** | FROZEN una vez aprobado |
| **Modificación** | Nueva versión mayor. La anterior pasa a SUPERSEDED. |

**Regla fundamental del NADR:**

> Un NADR gobierna una CAPACIDAD ARQUITECTÓNICA, no una implementación. Debe sobrevivir aunque cambien todos los nombres de clases, archivos y módulos que lo implementan.

### 3.4 Execution Plan

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Cómo, cuándo y quién implementa cada regla? |
| **Contiene** | Tareas atómicas, dependencias, owners, story points, riesgos, evidencia forense vinculante, rollback |
| **NO contiene** | Decisiones arquitectónicas, reglas normativas |
| **Naturaleza** | Documento operativo. Es la ÚNICA FUENTE DE VERDAD para la trazabilidad temporal. |
| **Estado** | Evoluciona durante la implementación |
| **Modificación** | Libre, siempre que no contradiga NADRs |

---

## 4. PLANTILLA CANÓNICA DEL NADR

Todo NADR debe seguir exactamente esta estructura de 9 secciones. No se permiten secciones adicionales ni omisiones.

```text
# NADR-{ID}: {Título}

## 1. METADATA
- Decision ID
- Título
- Clase de Decisión
- Nivel de Cumplimiento (MANDATORY)
- Versión
- Ciclo de Vida (DRAFT → APPROVED → FROZEN)
- Vigente Desde
- Autoridad
- Responsable Técnico
- Capacidad Arquitectónica (CAP-XXX)
- Evidencia Forense (IDs de hallazgos)
- Referencias Cruzadas (Depende de, Influencia, Conflictúa con, Reemplaza a)

## 2. ARCHITECTURE RISK SCORE
- Severidad (S1/S2/S3)
- Dimensiones: Operacional, Mantenibilidad, Recuperabilidad, Seguridad, Financiero
- Total Score /25

## 3. DECISIÓN EJECUTIVA
- Una única sentencia constitucional clara
- No es una lista de tareas ni una descripción de implementación
- Debe poder leerse como una ley permanente

## 4. CONTEXTO Y EVIDENCIA FORENSE
- Descripción abstracta del problema
- Sub-sección de evidencia concreta (aquí SÍ se permiten nombres de clases/archivos como prueba)
- Separación clara entre problema arquitectónico y manifestación concreta

## 5. REGLAS NORMATIVAS (RFC 2119)
- Reglas abstractas usando MUST / MUST NOT / SHOULD / MAY
- Agrupadas por dominio de responsabilidad
- Sin nombres de clases, archivos o tecnologías concretas
- Cada regla debe ser verificable

## 6. CONSECUENCIAS ARQUITECTÓNICAS
- Qué cambia en el sistema como resultado de la decisión
- No son tareas de implementación
- No son métricas de proyecto

## 7. VERIFICACIÓN Y VALIDACIÓN
- Verification: mecanismos estáticos/mecánicos (linters, type checkers, property tests)
- Validation: mecanismos dinámicos/comportamentales (golden corpus, E2E, regression gates)

## 8. RELACIÓN CON OTROS ARTEFACTOS
- Tabla de relaciones con otros NADRs, ADRs y Execution Plan
- Cada relación debe ser explícita y bidireccional

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)
- Lista explícita de responsabilidades que NO pertenecen a este NADR
- Con referencia al NADR que SÍ las gobierna
- OBLIGATORIA en todo NADR
```

### Reglas de redacción del NADR
* **Abstracción:** Las reglas normativas (sección 5) nunca mencionan clases, archivos, funciones o tecnologías concretas. Solo la sección 4 (evidencia) puede hacerlo.
* **Capacidad, no implementación:** El NADR gobierna una capacidad. Si la implementación cambia completamente, el NADR debe seguir siendo válido.
* **Sin cronograma:** El NADR no dice cuándo se implementa. Eso es responsabilidad del Execution Plan.
* **Sin Definition of Done:** El NADR no tiene criterios de aceptación operativa. Eso es responsabilidad del Execution Plan.
* **Frontera obligatoria:** Todo NADR debe declarar explícitamente qué NO gobierna.

---

## 5. MODELO REGLA-CÉNTRICO

### 5.1 Principio fundamental
Los NADRs no pertenecen a una fase. Son reglas constitucionales permanentes. Lo que se divide por fases no es el NADR, sino sus OBLIGACIONES (reglas individuales).

### 5.2 Estructura de trazabilidad

```text
ADR Maestro
    │
    ▼
NADR-XX
    │
    ├── Regla 5.1.1  ──►  Task 1.2.1  ──►  Commit abc123  ──►  Test X
    ├── Regla 5.1.2  ──►  Task 1.2.2  ──►  Commit def456  ──►  Test Y
    ├── Regla 5.2.1  ──►  Task 3.3.1  ──►  Commit ghi789  ──►  Test Z
    └── Regla 5.3.1  ──►  Task 5.1.1  ──►  Commit jkl012  ──►  Test W
```

### 5.3 Identificadores de regla
Cada regla de cada NADR tiene un identificador estable:
Ejemplos:
* `R-01-5.1.1` → NADR-01, sección 5.1, regla 1
* `R-08-5.2.3` → NADR-08, sección 5.2, regla 3

### 5.4 Fuente única de verdad para trazabilidad temporal
El Execution Plan es la ÚNICA fuente de verdad para el mapeo regla → tarea → fase. No se mantienen matrices de trazabilidad paralelas en los NADRs ni en documentos separados.

### 5.5 Matriz de trazabilidad en el Execution Plan
El Execution Plan incluye una tabla con las siguientes columnas:

| Task | Wave | NADR | Reglas implementadas | Estado |
|---|---|---|---|---|
| 1.2.1 | Wave 1 | NADR-01 | R-01-5.1.1, R-01-5.1.2 | DONE |
| 3.3.1 | Wave 3 | NADR-08 | R-08-5.2.1 | TODO |

### 5.6 Auditoría de completitud
En cualquier momento se puede responder:
* ¿Qué reglas RFC todavía no tienen tarea asignada?
* ¿Qué reglas RFC todavía no están implementadas?
* ¿Qué tareas están bloqueadas y por qué?

Esto se obtiene directamente del Execution Plan, sin consultar múltiples documentos.

---

## 6. FLUJO DE TRABAJO

### 6.1 Secuencia obligatoria

```text
1. AUDITORÍA (evidencia forense)
       │
       ▼
2. ADR MAESTRO (visión y capacidades)
       │
       ▼
3. ADR DE FASE (opcional, decisión de sub-fase)
       │
       ▼
4. NADRs (reglas normativas)
       │
       ▼
5. EXECUTION PLAN (tareas y secuencia)
       │
       ▼
6. IMPLEMENTACIÓN (código)
       │
       ▼
7. VERIFICACIÓN (tests, CI)
       │
       ▼
8. CONGELACIÓN (FROZEN)
```

### 6.2 Regla de precedencia
No se escribe código sin Execution Plan aprobado. No se escribe Execution Plan sin NADRs aprobados. No se escriben NADRs sin evidencia forense. No se escribe evidencia forense sin auditoría.

### 6.3 Definition of Ready (DoR)
Para iniciar una tarea del Execution Plan:
* El NADR que la respalda está en estado FROZEN
* Todas las tareas bloqueantes están DONE
* El owner tiene capacidad asignada
* El entorno de CI está listo

### 6.4 Definition of Done (DoD)
Para cerrar una tarea del Execution Plan:
* Código completo y revisado (PR aprobado)
* Cero violaciones a las reglas del NADR asociado
* Verification pasada (linters, type checks, property tests)
* Validation pasada (regression gates sin alterar oráculo)

### 6.5 Gates
Cada grupo de tareas (Wave) actúa como una compuerta. La Wave N no se considera finalizada hasta que:
* Todas sus tareas están DONE
* Los criterios de salida están verificados
* El mecanismo de rollback queda invalidado por estabilización en main

---

## 7. CONVENCIONES DE NOMENCLATURA

### 7.1 NADRs
| Aspecto | Convención |
|---|---|
| **Identificador canónico** | `NADR-F{FASE}-{XX}` (ej: NADR-F17BIS-01) |
| **Nombre de archivo** | `NADR_{XX}_{Nombre}.md` (ej: NADR_01_Canonical_AST_Representation.md) |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/NADR/` |
| **Identificador de regla** | `R-{XX}-{sección}.{regla}` (ej: R-01-5.1.1) |

### 7.2 ADRs
| Aspecto | Convención |
|---|---|
| **ADR Maestro** | `ADR_F{FASE}.md` (ej: ADR_F17_BIS.md) |
| **ADR de Fase** | `ADR_F{FASE}_{XX}.md` (ej: ADR_F17_BIS_01.md) |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/ADR/` |

### 7.3 Execution Plan
| Aspecto | Convención |
|---|---|
| **Nombre** | `PHASE_{FASE}_EXECUTION_PLAN.md` |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/plans/` |
| **Versión** | SemVer. Cambios operativos no requieren nueva versión mayor. |

### 7.4 Evidencia forense
| Aspecto | Convención |
|---|---|
| **Hallazgos de auditoría** | `P{bloque}-H{XX}` o `OBS-P{bloque}-{XX}` |
| **Gaps de arquitectura** | `GAP-{bloque}-{XX}` |
| **Evidencia de código** | `E-{bloque}-{XX}` |
| **Reglas de remediación** | `{bloque}-R{XX}` |

---

## 8. ANTI-PATRONES PROHIBIDOS

Los siguientes patrones están explícitamente prohibidos por esta metodología:

### 8.1 En NADRs

| Anti-patrón | Descripción | Corrección |
|---|---|---|
| **Nombres de clases en reglas** | "El PolymorphicValidationEngine debe..." | "El mecanismo canónico de validación debe..." |
| **Cronograma en NADR** | "Esto se implementa en la Fase 3" | Mover al Execution Plan |
| **Definition of Done en NADR** | "Se considera hecho cuando..." | Mover al Execution Plan |
| **Implementación en NADR** | "Usar Redis para..." | "Debe existir un puerto abstracto de coordinación distribuida" |
| **NADR sin frontera normativa** | No declarar qué NO gobierna | Añadir sección 9 obligatoria |
| **NADR que pertenece a una fase** | "NADR de la Fase 3" | Los NADRs son permanentes. Las fases implementan sus reglas. |

### 8.2 En Execution Plan

| Anti-patrón | Descripción | Corrección |
|---|---|---|
| **Decisiones arquitectónicas** | "Decidimos usar patrón X" | Mover a NADR |
| **Trazabilidad paralela** | Matriz de trazabilidad separada del plan | Consolidar en el Execution Plan |
| **Sin NADR de respaldo** | Tarea sin NADR FROZEN que la respalde | Crear NADR primero |

### 8.3 En la documentación general

| Anti-patrón | Descripción | Corrección |
|---|---|---|
| **Documento sin responsabilidad única** | Un documento que mezcla visión, reglas y tareas | Separar en ADR, NADR y Execution Plan |
| **Duplicación de información** | La misma regla en dos documentos | Una única fuente de verdad |
| **Documento que no habilita implementación** | Documentación que no desbloquea nada | No crear |
| **Sobreingeniería documental** | Crear artefactos "por si acaso" | Solo crear cuando hay ambigüedad que bloquea |

---

## 9. EVOLUCIÓN DE LA METODOLOGÍA

### 9.1 Principio de mínima documentación
No se crea un nuevo artefacto documental a menos que elimine una ambigüedad que esté bloqueando activamente la implementación.

### 9.2 Revisión de la metodología
Esta metodología puede evolucionar mediante:
1. Identificación de un defecto recurrente en la aplicación de la metodología.
2. Propuesta de cambio documentada.
3. Aprobación por el Architecture Board.
4. Actualización de este documento con nueva versión SemVer.

### 9.3 Prohibición de meta-gobernanza
No se crean documentos para gobernar cómo se crean documentos. Este documento es el nivel máximo de meta-gobernanza. Cualquier necesidad adicional se resuelve con una sección adicional aquí, no con un nuevo documento.

---

## 10. CHECKLIST DE CONGELACIÓN

Antes de marcar un NADR como FROZEN, verificar:
- [ ] La sección 3 (Decisión Ejecutiva) es una sentencia constitucional clara, no una lista de tareas.
- [ ] La sección 5 (Reglas) no contiene nombres de clases, archivos ni tecnologías concretas.
- [ ] La sección 9 (Frontera Normativa) está presente y es explícita.
- [ ] No hay sección de "Definition of Done" ni "Criterios de Aceptación".
- [ ] No hay sección de "Implementation Constraints".
- [ ] No hay sección de "Decision Drivers & Metrics".
- [ ] La evidencia forense (sección 4) referencia hallazgos concretos con IDs.
- [ ] Las referencias cruzadas (sección 8) son bidireccionales y verificables.
- [ ] El NADR no declara pertenecer a una fase específica.
- [ ] El NADR gobierna una capacidad, no una implementación.

---

## 11. RESUMEN EJECUTIVO

| Documento | Pregunta | Responsabilidad | NO contiene |
|---|---|---|---|
| **Roadmap** | ¿Hacia dónde vamos? | Visión a largo plazo | Implementación |
| **ADR Maestro** | ¿Por qué existe esta fase? | Visión, alcance, capacidades | Reglas, tareas |
| **ADR de Fase** | ¿Cuál es la decisión de esta sub-fase? | Decisión arquitectónica | Reglas detalladas, tareas |
| **NADR** | ¿Qué reglas son obligatorias? | Constitución permanente | Tareas, cronogramas, DoD |
| **Execution Plan** | ¿Cómo se implementa? | Tareas, secuencia, owners | Decisiones arquitectónicas |
| **Código** | ¿Qué hace el sistema? | Implementación | Gobernanza |
| **Tests/CI** | ¿Se cumple la regla? | Verificación | Gobernanza |

> **Nota de Gobernanza:** Este documento es la metodología única y obligatoria para todos los cambios arquitectónicos del proyecto. Cualquier desviación requiere aprobación explícita del Architecture Board. La sobreingeniería documental es un defecto tan grave como la falta de documentación.