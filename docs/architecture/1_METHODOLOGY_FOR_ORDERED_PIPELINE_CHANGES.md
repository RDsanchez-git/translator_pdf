# METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md
## Metodología General para Cambios Ordenados en el Pipeline del Traductor

* **Versión:** 1.3.0
* **Estado:** FROZEN
* **Fecha de Emisión:** 2026-08-04
* **Fecha de Última Actualización:** 2026-08-25
* **Autoridad:** Architecture Board
* **Alcance:** Todas las fases futuras del proyecto (17-BIS en adelante)
* **Ubicación:** `docs/architecture/METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-08-04 | Emisión inicial |
| 1.1.0 | 2026-08-04 | Sección 3.5: Artefactos de Auditoría y Revisión. Sección 6.6: Flujo de Revisión Post-Implementación. Sección 7.5: Nomenclatura de reportes. Sección 7.6: Estructura de directorios. Actualización de jerarquía y resumen ejecutivo. |
| 1.2.0 | 2026-08-19 | Unificación de nomenclatura a *Deferred Findings Register*. Corrección del flujo de trabajo (§6.1) para separar el *Exit Review Evidence Log* de la empiria de implementación. Incorporación del *Evidence Log* en nomenclatura (§7.5), estructura de directorios (§7.6) y resumen ejecutivo (§11). |
| 1.3.0 | {fecha actual} | Clarificación del ciclo de vida del Exit Review Evidence Log: construcción incremental gate por gate, inmutabilidad de entradas registradas, FROZEN al cierre de la fase. Actualización de §3.5.2, §6.1, §6.5, §6.6, §6.7. |

---

## 1. PROPÓSITO Y ALCANCE

Este documento define la metodología única y obligatoria para planificar, gobernar e implementar cambios arquitectónicos en el pipeline del traductor. Es aplicable a todas las fases futuras del proyecto.

Su objetivo es garantizar que:

- Todo cambio esté respaldado por evidencia forense antes de implementarse.
- La gobernanza arquitectónica esté separada de la ejecución operativa.
- La trazabilidad sea completa desde la visión hasta el commit.
- No se introduzca sobreingeniería documental.
- Cada documento tenga una única responsabilidad y no invada la de otros.
- Los artefactos de auditoría y revisión tengan ubicación, nomenclatura y ciclo de vida definidos.

### Principio rector

> La documentación existe para habilitar implementación de calidad, no para existir. Cada artefacto documental debe justificar que reduce complejidad futura más de lo que añade complejidad presente.

### Principio de clasificación de artefactos

> Un artefacto se commitea al repositorio si y solo si es **referenciable** desde un documento de gobernanza superior (ADR, NADR, Execution Plan) y su ausencia rompería la trazabilidad. Los insumos descartables del proceso de trabajo (notas intermedias, grafos generados, scripts de análisis temporal) no se commitean.

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
AUDIT & REVIEW REGISTERS
│
│ ¿Qué se encontró, por qué se decidió así y cómo se resolvió?
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
| **Contiene** | Tareas atómicas, dependencias, owners, story points, riesgos, evidencia forense vinculante, rollback, notas de implementación |
| **NO contiene** | Decisiones arquitectónicas, reglas normativas |
| **Naturaleza** | Documento operativo vivo. Es la ÚNICA FUENTE DE VERDAD para la trazabilidad temporal. |
| **Estado** | Evoluciona durante la implementación |
| **Modificación** | Libre, siempre que no contradiga NADRs |

### 3.5 Artefactos de Auditoría y Revisión

Los artefactos de auditoría y revisión son el registro formal de lo que se encontró y cómo se resolvió. Se dividen en tres categorías según el momento del ciclo de vida en que se generan:

#### 3.5.1 HITOs de Auditoría Forense (Fase 0)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Qué se encontró en la auditoría forense del código existente? |
| **Contiene** | Inventario de módulos, mapeo de flujos, evidencia de código, gaps arquitectónicos, matriz de gaps |
| **NO contiene** | Soluciones, código nuevo, decisiones de implementación |
| **Naturaleza** | Evidencia forense pura. Es la entrada para el ADR Maestro y los NADRs. |
| **Estado** | FROZEN una vez completada la auditoría. No se modifica. |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/00-foundation/` |
| **Nomenclatura** | `HITO_{X.X}_{NOMBRE}.md` |

#### 3.5.2 Exit Review Evidence Log (Evidencia Forense de Clasificación)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Qué evidencia forense fundamenta cada clasificación del Findings Register? |
| **Contiene** | Por cada DF/GF: texto original, reformulación, archivos auditados, análisis, gaps confirmados, no-gaps, impacto, sub-acciones, clasificación consolidada, regla aplicada |
| **NO contiene** | Resultados de implementación por batch (van en Findings Register), métricas acumuladas |
| **Naturaleza** | Registro de evidencia forense. Se construye incrementalmente gate por gate; cada entrada es inmutable una vez registrada. El documento completo se FROZEN al cierre de la fase. |
| **Construcción** | Incremental. Cada Gate Exit Review agrega su sección de evidencia forense al documento. Las entradas registradas no se modifican durante los batches de resolución. |
| **Estado** | En construcción durante la fase. FROZEN al cierre de la fase. |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/reviews/` |
| **Nomenclatura** | `FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md` |
| **Relación** | El Deferred Findings Register referencia este documento para justificar cada clasificación |

#### 3.5.3 Deferred Findings Register (Revisión Post-Implementación)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Qué hallazgos se encontraron? ¿Cómo se clasificaron? ¿Qué se implementó en los batches? |
| **Contiene** | Tabla de hallazgos con ID, estado, decisión. Gate Exit Reviews. Batches de implementación. Métricas de cierre. |
| **NO contiene** | Código, reglas normativas, auditorías forenses detalladas (esas van en el Evidence Log) |
| **Naturaleza** | Registro operativo de trazabilidad findings → clasificación → batch → commit. |
| **Estado** | Evoluciona durante la implementación de los batches. Se ARCHIVA cuando la fase se cierra. |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/reviews/` |
| **Nomenclatura** | `FASE_{X}_DEFERRED_FINDINGS_REGISTER.md` |

#### 3.5.4 Reportes de Resolución Consolidados (opcional)

| Aspecto | Descripción |
|---|---|
| **Responde** | ¿Cuál es el detalle de la resolución de un hallazgo específico que requirió análisis profundo? |
| **Contiene** | Análisis de un DF específico, opciones evaluadas, decisión, evidencia de validación |
| **NO contiene** | Múltiples hallazgos (eso va en el Findings Register), reglas normativas |
| **Cuándo usar** | Solo cuando un hallazgo tiene complejidad suficiente para requerir su propio documento. Hallazgos simples se resuelven directamente en el Findings Register. |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/reviews/` |
| **Nomenclatura** | `DF-{XX}_{NOMBRE_CORTO}.md` |

#### Regla de clasificación de artefactos de auditoría

> Los HITOs de Fase 0 son **evidencia forense** y se commitean como parte de la fundación de la fase. El Evidence Log es **evidencia forense de decisiones** y se congela al cierre del Exit Review. Los Findings Registers son **trazabilidad operativa** y se commitean como parte del cierre de la fase. Las notas de trabajo intermedias (auditorías parciales, grafos generados, scripts temporales) **no se commitean** y se gestionan vía `.gitignore`.

---

## 4. PLANTILLA CANÓNICA DEL NADR

Todo NADR debe seguir exactamente esta estructura de 9 secciones. No se permiten secciones adicionales ni omisiones.

```text
# NADR-{ID}: {Título}

## 1. METADATA
## 2. ARCHITECTURE RISK SCORE
## 3. DECISIÓN EJECUTIVA
## 4. CONTEXTO Y EVIDENCIA FORENSE
## 5. REGLAS NORMATIVAS (RFC 2119)
## 6. CONSECUENCIAS ARQUITECTÓNICAS
## 7. VERIFICACIÓN Y VALIDACIÓN
## 8. RELACIÓN CON OTROS ARTEFACTOS
## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)
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
* `NADR-01 §5.1 R1` → NADR-01, sección 5.1, regla 1
* `NADR-08 §5.2 R3` → NADR-08, sección 5.2, regla 3

### 5.4 Fuente única de verdad para trazabilidad temporal
El Execution Plan es la ÚNICA fuente de verdad para el mapeo regla → tarea → fase. No se mantienen matrices de trazabilidad paralelas en los NADRs ni en documentos separados.

### 5.5 Matriz de trazabilidad en el Execution Plan
El Execution Plan incluye una tabla con las siguientes columnas:

| Task | Wave | NADR | Reglas implementadas | Estado |
|---|---|---|---|---|
| 1.2.1 | Wave 1 | NADR-01 | §5.1 R1, §5.1 R2 | DONE |
| 3.3.1 | Wave 3 | NADR-08 | §5.2 R1 | TODO |

### 5.6 Auditoría de completitud
En cualquier momento se puede responder:
* ¿Qué reglas RFC todavía no tienen tarea asignada?
* ¿Qué reglas RFC todavía no están implementadas?
* ¿Qué tareas están bloqueadas y por qué?

Esto se obtiene directamente del Execution Plan, sin consultar múltiples documentos.

### 5.7 Trazabilidad de findings (extensión v1.1.0)
El Deferred Findings Register es la fuente única de verdad para el mapeo hallazgo → resolución → commit:

```text
Deferred Findings Register
    │
    ├── DF-01  ──►  Batch 5  ──►  Commit xyz789  ──►  Estado: RESOLVED
    ├── DF-14  ──►  Batch 1  ──►  Commit abc123  ──►  Estado: RESOLVED
    ├── DF-26  ──►  Batch 3  ──►  Commit def456  ──►  Estado: RESOLVED
    └── DF-12-C ──► Diferido a Fase 18  ──►  Estado: RECLASSIFIED_FUTURE_PHASE
```

---

## 6. FLUJO DE TRABAJO

### 6.1 Secuencia obligatoria

```text
1. AUDITORÍA (evidencia forense) → 00-foundation/
       │
       ▼
2. ADR MAESTRO (visión y capacidades) → ADR/
       │
       ▼
3. ADR DE FASE (opcional, decisión de sub-fase) → ADR/
       │
       ▼
4. NADRs (reglas normativas) → NADR/
       │
       ▼
5. EXECUTION PLAN (tareas y secuencia) → plans/
       │
       ▼
6. IMPLEMENTACIÓN (código) → repositorio
       │
       ▼
7. VERIFICACIÓN (tests, CI)
       │
       ▼
8. EXIT REVIEW EVIDENCE LOG (evidencia forense de hallazgos) → reviews/
   Nota: Este documento se construye INCREMENTALMENTE. Cada Gate Exit Review
   agrega su sección de evidencia forense. El documento completo se FROZEN
   al cierre de la fase (§3.5.2).
       │
       ▼
9. DEFERRED FINDINGS REGISTER (clasificación, batches y resolución) → reviews/
   Nota: Este documento se actualiza gate por gate durante la implementación.
   Se ARCHIVA al cierre de la fase (§3.5.3).
       │
       ▼
10. CONGELACIÓN (FROZEN / ARCHIVED) → todos los documentos y handoff final
```

### 6.2 Regla de precedencia
No se escribe código sin Execution Plan aprobado. No se escribe Execution Plan sin NADRs aprobados. No se escriben NADRs sin evidencia forense. No se escribe evidencia forense sin auditoría. No se cierra una fase sin Findings Register actualizado.

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
Al cerrar un Gate (agrupación de Waves), se ejecuta el **Gate Exit Review**, que actualiza ambos artefactos de revisión:
* El *Exit Review Evidence Log*: se agrega la sección de evidencia forense del Gate mientras la evidencia está fresca. Las entradas registradas son inmutables.
* El *Deferred Findings Register*: se clasifican los hallazgos identificados en el Gate y se registra el Gate Exit Review.

### 6.6 Revisión Post-Implementación (v1.1.0)

La revisión estructurada se ejecuta incrementalmente en cada Gate Exit Review y se consolida al cierre de la fase:

1. **Identificación de findings:** Se audita el código implementado contra los NADRs y el ADR Maestro. Los hallazgos se registran con ID único (`DF-{XX}` o `GF-{XX}`).
2. **Evidencia Forense:** Se documenta el análisis detallado de cada hallazgo en el *Exit Review Evidence Log*. Esta evidencia se registra en cada Gate Exit Review, mientras está fresca, para minimizar el riesgo de omisión. Las entradas registradas son inmutables.
3. **Clasificación:** Cada finding se clasifica en el *Deferred Findings Register* como:
   - `IMPLEMENTATION_REQUIRED`: Requiere código nuevo o modificación
   - `REVIEW_REQUIRED`: Requiere análisis adicional antes de decidir
   - `CLOSED (NAR)`: No es un problema real (se cierra con justificación)
   - `RECLASSIFIED_FUTURE_PHASE`: Se difiere a una fase futura con justificación
   - `ACCEPTED_LIMITATION`: Limitación conocida y documentada
4. **Resolución por batches:** Los findings `IMPLEMENTATION_REQUIRED` se agrupan en batches de implementación coherentes. Cada batch se ejecuta con validaciones post-implementación (pyright, pytest, greps de verificación).
5. **Cierre:** Un finding se cierra formalmente cuando:
   - El código está implementado y commiteado
   - Las validaciones pasan (pyright 0 errors, pytest suite en verde)
   - El estado se actualiza en el Findings Register
   - Se documenta la justificación si fue cerrado como NAR o diferido

### 6.7 Criterio de commiteo de artefactos de revisión

| Artefacto | ¿Se commitea? | Momento |
|---|---|---|
| HITOs de Fase 0 | ✅ Sí | Al finalizar la Fase 0, como parte de `00-foundation/` |
| Exit Review Evidence Log | ✅ Sí | Se construye gate por gate; se commitea en estado `FROZEN` al cierre de la fase, como parte de `reviews/` |
| Deferred Findings Register | ✅ Sí | Al cerrar cada fase, como parte de `reviews/` |
| DF Reports consolidados | ✅ Sí (si existen) | Junto con el Findings Register |
| Notas de trabajo intermedias | ❌ No | Se gestionan vía `.gitignore` |
| Grafos generados | ❌ No | Se gestionan vía `.gitignore` |
| Scripts temporales | ❌ No | Se gestionan vía `.gitignore` |

---

## 7. CONVENCIONES DE NOMENCLATURA

### 7.1 NADRs
| Aspecto | Convención |
|---|---|
| **Identificador canónico** | `NADR-F{FASE}-{XX}` (ej: NADR-F17BIS-01) |
| **Nombre de archivo** | `NADR_{XX}_{Nombre}.md` (ej: NADR_01_Canonical_AST_Representation.md) |
| **Ubicación** | `docs/architecture/adr/phase-{fase}/NADR/` |
| **Identificador de regla** | `NADR-{XX} §{sección} R{regla}` (ej: NADR-01 §5.1 R1) |

### 7.2 ADRs
| Aspecto | Convención |
|---|---|
| **ADR Maestro** | `ADR_F{FASE}_MASTER.md` (ej: ADR_F17_BIS_MASTER.md) |
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

### 7.5 Artefactos de Auditoría y Revisión (v1.2.0)
| Aspecto | Convención |
|---|---|
| **HITOs de auditoría** | `HITO_{X.X}_{NOMBRE}.md` en `00-foundation/` |
| **Gap Matrix** | `HITO_0.5_ENTREGABLE_1_GAP_MATRIX.md` en `00-foundation/` |
| **Exit Review Evidence Log** | `FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md` en `reviews/` |
| **Deferred Findings Register** | `FASE_{X}_DEFERRED_FINDINGS_REGISTER.md` en `reviews/` |
| **DF Report individual** | `DF-{XX}_{NOMBRE_CORTO}.md` en `reviews/` (opcional) |
| **Identificador de finding** | `DF-{XX}` o `GF-{XX}` (ej: DF-01, GF-01) |
| **Identificador de batch** | `Batch {N}` dentro del Findings Register |

### 7.6 Estructura de directorios por fase

```text
docs/architecture/adr/phase-{fase}/
├── 00-foundation/          # HITOs de auditoría forense (Fase 0)
│   ├── HITO_0.1_*.md
│   ├── HITO_0.2_*.md
│   ├── HITO_0.5_ENTREGABLE_1_GAP_MATRIX.md
│   └── FINAL_INTEGRATED_REPORT_*.md
├── ADR/                    # ADRs (Maestro y de Fase)
│   ├── ADR_F{FASE}_MASTER.md
│   ├── ADR_F{FASE}_0.md
│   └── ADR_F{FASE}_01.md
├── NADR/                   # NADRs (reglas normativas)
│   ├── NADR_01_*.md
│   ├── NADR_02_*.md
│   └── ...
├── plans/                  # Execution Plans
│   └── PHASE_{FASE}_EXECUTION_PLAN.md
├── reviews/                # Evidence Logs y Findings Registers
│   ├── FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md   ← Evidencia forense de las decisiones
│   ├── FASE_{X}_DEFERRED_FINDINGS_REGISTER.md ← Registro de decisiones + batches
│   └── DF-{XX}_{NOMBRE}.md                    ← Opcional, para hallazgos muy complejos
└── handoff/                # Documentos de traspaso entre sesiones
```

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

### 8.3 En Artefactos de Revisión (v1.1.0)

| Anti-patrón | Descripción | Corrección |
|---|---|---|
| **Commitear notas de trabajo** | `auditoria_*.txt`, grafos P1-P7, scripts generadores en el repo | Agregar a `.gitignore` |
| **Findings sin estado** | Hallazgo registrado pero sin estado ni resolución | Todo hallazgo debe tener estado y resolución |
| **Finding cerrado sin evidencia** | Hallazgo cerrado sin validación (pyright/pytest) | Cierre requiere evidencia de validación |
| **DF Report para hallazgo simple** | Documento individual para un hallazgo trivial | Hallazgos simples se resuelven en el Findings Register |
| **Duplicar Findings Register** | Múltiples registros paralelos de hallazgos | Un único Deferred Findings Register por fase |
| **Mezclar evidencia con batches** | Poner auditorías forenses de 500 líneas en el Findings Register | Mover al Exit Review Evidence Log |

### 8.4 En la documentación general

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

### 10.1 Checklist de cierre de fase (v1.1.0)
Antes de cerrar una fase y commitear el Deferred Findings Register, verificar:
- [ ] Todos los hallazgos `IMPLEMENTATION_REQUIRED` están resueltos o justificados como NAR.
- [ ] Todos los hallazgos `REVIEW_REQUIRED` tienen decisión documentada.
- [ ] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito (fase y justificación).
- [ ] El `.gitignore` incluye las reglas para artefactos de trabajo no commiteables.
- [ ] Los HITOs de auditoría están en `00-foundation/` y commiteados.
- [ ] El Exit Review Evidence Log está en `reviews/` y FROZEN.
- [ ] El Deferred Findings Register está en `reviews/` y ARCHIVED.
- [ ] Pyright: 0 errors, 0 warnings.
- [ ] Pytest: suite completa en verde.

---

## 11. RESUMEN EJECUTIVO

| Documento | Pregunta | Responsabilidad | NO contiene |
|---|---|---|---|
| **Roadmap** | ¿Hacia dónde vamos? | Visión a largo plazo | Implementación |
| **ADR Maestro** | ¿Por qué existe esta fase? | Visión, alcance, capacidades | Reglas, tareas |
| **ADR de Fase** | ¿Cuál es la decisión de esta sub-fase? | Decisión arquitectónica | Reglas detalladas, tareas |
| **NADR** | ¿Qué reglas son obligatorias? | Constitución permanente | Tareas, cronogramas, DoD |
| **Execution Plan** | ¿Cómo se implementa? | Tareas, secuencia, owners, notas | Decisiones arquitectónicas |
| **HITOs de Auditoría** | ¿Qué se encontró en la auditoría? | Evidencia forense inicial | Soluciones, código |
| **Evidence Log** | ¿Qué evidencia fundamenta cada decisión? | Evidencia forense del Exit Review | Resultados de implementación, métricas |
| **Findings Register** | ¿Qué se decidió y cómo se resolvió? | Trazabilidad findings → batches → commit | Código, reglas normativas |
| **Código** | ¿Qué hace el sistema? | Implementación | Gobernanza |
| **Tests/CI** | ¿Se cumple la regla? | Verificación | Gobernanza |

> **Nota de Gobernanza:** Este documento es la metodología única y obligatoria para todos los cambios arquitectónicos del proyecto. Cualquier desviación requiere aprobación explícita del Architecture Board. La sobreingeniería documental es un defecto tan grave como la falta de documentación.