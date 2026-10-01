# 2_METH_ADR_MASTER.md
## Metodología canónica para la emisión de ADRs Maestros

* **Versión:** 1.0.1
* **Estado:** FROZEN (efectivo con la aprobación del Architecture Board registrada en esta versión)
* **Fecha de emisión:** 2026-09-30
* **Aprobación Architecture Board:** 2026-09-30 (v1.0.1, corrección pre-freeze)
* **Autoridad:** Architecture Board
* **Alcance:** Todos los ADRs Maestros emitidos desde Fase 18 en adelante
* **Derivado de:** METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.4.0 (§2, §3.1, §6.1, §6.2, §7.2, §8.4, §9; reglas citadas presentes desde v1.3.0) y del exemplar FROZEN `ADR_F17_BIS_MASTER.md`

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-30 | Emisión inicial. Cierra el gap detectado al cierre de Fase 6: el ADR Maestro era el único nivel de la pirámide (§2) sin plantilla canónica propia. Derivado del exemplar FROZEN ADR_F17_BIS_MASTER (10 secciones validadas en 6 sub-fases) y de §3.1 de la metodología general. |
| 1.0.1 | 2026-09-30 | Corrección pre-freeze: fechas de emisión completadas; aprobación del Architecture Board registrada en header; nota de hogar resuelta (suite numerada confirmada por verificación de directorio); derivación actualizada a v1.4.0 (versión que referencia este documento); normalización de formato en §5. Sin cambios normativos: plantilla, reglas, anti-patrones y checklist idénticos a 1.0.0. FROZEN efectivo con esta versión. |

---

## 1. PROPÓSITO Y POSICIÓN JERÁRQUICA

Este documento define **cómo se emite un ADR Maestro conforme**: plantilla,
responsabilidad por sección, reglas de redacción, ciclo de vida, anti-patrones y
checklist de congelación.

* **Posición del artefacto:** el ADR Maestro es el nivel inmediatamente inferior
  al ROADMAP y superior a ADRs de Fase, NADRs y Execution Plan
  (metodología general §2).
* **Este documento NO es autoridad normativa** sobre el contenido de ningún ADR:
  cada ADR Maestro es la constitución de su propia fase. Este documento solo
  gobierna su forma y su ciclo de vida.
* **Relación con la metodología general:** ella secuencia el flujo
  (§6.1 paso 2: auditoría → ADR Maestro) y permanece como nivel máximo de
  meta-gobernanza (§9.3). Este documento es el template de artefacto de la suite
  metodológica; no introduce meta-gobernanza nueva.

---

## 2. CUÁNDO SE EMITE UN ADR MAESTRO

* **Uno por unidad de gobernanza de primer nivel:** cada fase del ROADMAP
  (Etapas I y II), o sub-fase que el Architecture Board eleve a unidad de
  gobernanza con re-baseline propia (precedente: 17-BIS dentro de Fase 17).
  Las sub-fases operativas dentro de una unidad gobernada usan ADR de Fase
  (`3_METH_ADR_PHASES.md`), nunca Maestro.
* **Precondición (Definition of Ready):** compuerta de auditoría forense
  (Fase 0 de la fase) completada, con HITos commiteados en `00-foundation/`
  (metodología general §3.5.1 y §6.2: "no se escribe evidencia forense sin
  auditoría").
* **Momento:** después de la auditoría y antes de cualquier NADR, Execution Plan
  o código de la fase (metodología general §6.2: precedencia).

---

## 3. PLANTILLA CANÓNICA (header + 10 secciones)

Todo ADR Maestro debe seguir exactamente esta estructura. No se permiten
secciones adicionales ni omisiones.

Nomenclatura y ubicación del artefacto: metodología general §7.2
(`ADR_F{FASE}_MASTER.md` en `docs/architecture/adr/phase-{fase}/ADR/`). Este
documento no redefine esa nomenclatura; solo la forma y el ciclo de vida.

```text
# ARCHITECTURE DECISION RECORD (ADR)
## ADR F{FASE}: {Título de la capacidad de la fase} (ADR Maestro)

* **Estado:** PROPOSED | FROZEN | SUPERSEDED
* **Fecha de Emisión Original:** {YYYY-MM-DD}
* **Fecha de Congelamiento:** {YYYY-MM-DD | —}
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** {FASE}
* **Módulos Afectados:** {subsistemas / bounded contexts / directorios}
* **Aprobación Architecture Board:** {YYYY-MM-DD}
* **Derivado de:** ROADMAP ARQUITECTÓNICO v{N} (objetivos de Fase {FASE})
* **Supersede:** {ADR previo | —}

## 1. CONTEXTO Y JUSTIFICACIÓN
## 2. PROBLEMA ARQUITECTÓNICO Y ESTADO OBSERVADO
   ## 2.1 Architectural Outcome de la compuerta de auditoría
## 3. SEPARACIÓN DE CONCEPTOS FUNDAMENTALES
## 4. ALCANCE Y NO-OBJETIVOS (OUT OF SCOPE)
## 5. INVARIANTES Y REGLAS DE GOBERNANZA
## 6. HOJA DE RUTA DE SUB-FASES GOBERNADAS
## 7. ESPECIFICACIÓN DE LA COMPUERTA DE AUDITORÍA (FASE 0)
## 8. REGISTRO DE DECISIONES CANDIDATAS (DC LOG)
## 9. ARCHITECTURE GOVERNANCE FRAMEWORK
## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES
```

---

## 4. RESPONSABILIDAD POR SECCIÓN

| § | Responde | Contiene | NO contiene |
|---|---|---|---|
| 1 | ¿Por qué existe la fase ahora? | Estado de la fase previa que la habilita; vínculo al ROADMAP traducido a capacidades; motivación; pivot normativo pre-freeze si la auditoría cambió el objetivo (declarado explícitamente) | Cronograma, implementación, reglas normativas |
| 2 | ¿Qué incertidumbres estructurales existen y qué demostró la auditoría? | Incertidumbres numeradas; estado observado citando IDs de evidencia forense (`HITO_`, `GAP-`, `E-`) de `00-foundation/`; hallazgos sistémicos; §2.1 con el outcome de la compuerta | Soluciones, diseño de clases, decisiones |
| 3 | ¿Qué dimensiones ortogonales deben permanecer desacopladas? | Dimensiones fundamentales y sus reglas de no-colapso ("X no implica Y") | Mecanismos de implementación |
| 4 | ¿Hasta dónde llega la fase y qué queda fuera con dueño? | Capacidades in-scope; no-objetivos con fase o documento propietario explícito de cada ítem | Tasks, owners personales, fechas |
| 5 | ¿Qué debe permanecer verdadero sin importar la implementación? | Invariantes constitucionales numeradas; reglas de gobernanza del proceso (Audit First, Reuse Before Invent) | Reglas RFC-2119 verificables (pertenecen a NADR); nombres de clases |
| 6 | ¿Qué capacidades se requieren y en qué orden lógico? | Árbol de sub-fases por capacidad; flujo de gobernanza; **Cláusula de Relación con el Execution Plan (obligatoria)** | Waves, tasks, dependencias operativas, fechas, deploy |
| 7 | ¿Cómo se audita antes de diseñar? | Regla de blindaje (NO CODE / NO I/O); inputs (directorios y componentes auditables); actividades; entregables obligatorios (Gap Matrix, Contract Map, Evidence Register con resoluciones DC, propuesta de congelamiento). Al completarse la auditoría, la sección se preserva como registro histórico inmutable | Soluciones, nuevas abstracciones |
| 8 | ¿Qué preguntas abiertas debe resolver la evidencia? | Log `DC-01..DC-NN` con preguntas; estado final con resolución evidenciada mediante IDs de `00-foundation/`; se preserva intacto como registro histórico | Respuestas sin evidencia; decisiones de implementación |
| 9 | ¿Cómo se norma esta fase dentro de la pirámide? | Cadena normativa **interna de la fase**: Maestro → [ADR de la compuerta de auditoría / ADRs de Fase si existen] → NADRs → Execution Plan → Registers. Los HITos de `00-foundation/` son evidencia de entrada que alimenta al Maestro (§6.2), no un nivel normativo de la cadena. Cláusula de jerarquía normativa incorporada por referencia a metodología general §2 | El diagrama o los niveles globales de metodología §2 (ROADMAP → … → TESTS/CI) |
| 10 | ¿Cuándo está congelado el ADR y cuándo cerrada la fase? | Nivel A: DoD de gobernanza (criterios de congelamiento). Nivel B: DoD global de la fase (condiciones de baseline operativa), verificables | DoD por tarea (pertenece al Execution Plan) |

---

## 5. REGLAS DE REDACCIÓN

* **Nivel de capacidad:** nombres de clases y componentes permitidos en §2 como
  estado observado, en §7 como objeto de auditoría y en §8 como objeto de las
  preguntas DC (los DCs se resuelven contra evidencia concreta; prohibir nombres
  allí los haría irresolubles). Prohibidos en §3, §4, §5 y §6.
* **Sin reglas normativas:** el ADR Maestro no emite reglas RFC-2119
  (MUST/SHOULD verificables). Sus invariantes (§5 del ADR) son declaraciones
  constitucionales de verdad; su materialización normativa ocurre en NADRs
  (`4_METH_NADR.md`).
* **Sin tareas ni cronograma:** ninguna sección contiene tasks, waves, owners,
  story points ni fechas de implementación (Execution Plan,
  `5_METH_EXECUTION_PLAN.md`).
* **No-objetivos exhaustivos:** cada ítem de out-of-scope nombra la fase o
  documento dueño de ese trabajo.
* **Evidencia vinculante:** §2 cita IDs de evidencia forense de
  `00-foundation/`; no transcribe auditorías (viven allí y en el Evidence Log).
* **DCs cerrados:** un DC se considera resuelto únicamente si consta con
  evidencia empírica (IDs de `00-foundation/` citados en §8 del ADR), o si la
  respuesta registrada es "la decisión se toma en {documento/fase X}"
  (diferimiento con destino explícito, que es estado terminal). Un DC sin
  respuesta es un DC abierto y **bloquea FROZEN**.
* **Fuente única:** no duplica objetivos del ROADMAP (los traduce a
  capacidades), ni reglas de NADRs, ni secuencias del Execution Plan, ni la
  pirámide global de la metodología general.
* **Jerarquía por referencia:** §9 del ADR declara únicamente la cadena
  normativa interna de la fase (§4, fila §9) e incorpora la cláusula de
  jerarquía normativa por referencia a metodología general §2. Prohibido
  reproducir el diagrama o los niveles globales (anti-patrón de §7).

---

## 6. CICLO DE VIDA Y MODIFICACIÓN

* **PROPOSED:** durante y después de la compuerta de auditoría; puede mutar con
  evidencia.
* **FROZEN:** tras resolver el 100% de los DCs según la regla de §5 de **este
  documento**, aprobación del Architecture Board registrada en el header, y
  checklist de congelación (§8 de **este documento**) completa. Habilita NADRs
  y código (metodología general §6.2).
* **SUPERSEDED:** un Maestro FROZEN es **inmutable**. Todo cambio sustantivo
  exige un ADR sucesor (nueva versión mayor del Maestro o ADR de Fase) que
  declare explícitamente el alcance superseded. Una errata que no altera
  decisiones no se corrige en el documento FROZEN; una que las alterara es, por
  definición, cambio sustantivo y exige sucesor.
* **Cláusula de abuelamiento:** los ADRs Maestros FROZEN antes de la emisión de
  este documento (`ADR_F17_BIS_MASTER`) **no se reformatean retroactivamente**.
  Esta plantilla obliga desde la primera emisión posterior (`ADR_F18_MASTER`).

---

## 7. ANTI-PATRONES PROHIBIDOS

| Anti-patrón | Descripción | Corrección |
|---|---|---|
| Invariantes con nombres de clases | "El ZhangShashaEngine debe ser canónico" | "El motor topológico canónico debe integrar la política de criticidad" (el nombre va a evidencia/NADR) |
| Reglas RFC-2119 en el Maestro | "§5: El sistema MUST verificar biyección" | Mover a NADR; en el Maestro queda la invariante declarativa |
| Hoja de ruta operacional | §6 con waves, fechas y owners | Mover al Execution Plan; §6 solo orden lógico de capacidades + cláusula de relación |
| Transcripción de evidencia | Copiar auditorías extensas en §2 | Citar IDs (`HITO_`, `GAP-`, `E-`); la evidencia vive en `00-foundation/` |
| Duplicar la pirámide global | §9 restata el diagrama ROADMAP → … → TESTS/CI de metodología §2 | §9 declara solo la cadena normativa interna de la fase y referencia §2 |
| HITos tratados como nivel normativo | §9 coloca `00-foundation/` como eslabón de la cadena | Los HITos son evidencia de entrada (§6.2); el nivel normativo es el ADR de la compuerta de auditoría, si existe |
| DC sin resolución | DC log con preguntas abiertas al congelar | Todo DC resuelto con evidencia o diferido con destino terminal (§5) |
| No-objetivos sin dueño | "Fuera de alcance: optimizaciones" | "Fuera de alcance: optimizaciones (pertenece a Fase 18)" |
| Maestro por sub-fase operativa | Emitir Maestros para sub-fases | Sub-fases operativas usan ADR de Fase (`3_METH_ADR_PHASES.md`) |
| Errata editada en FROZEN | Corregir typos o campos en un Maestro FROZEN | Inmutabilidad absoluta: errata no-sustantiva no se corrige; la sustantiva exige ADR sucesor (§6) |
| Flujo de gobernanza duplicado dentro del ADR | §7 repite el diagrama de flujo de §6 | §7 conserva solo lo específico de la compuerta de auditoría (inputs, actividades, entregables); el flujo de transición de estado vive únicamente en §6 |

---

## 8. CHECKLIST DE CONGELACIÓN

Antes de marcar un ADR Maestro como FROZEN, verificar:

- [ ] Header completo, incluido `Aprobación Architecture Board` con fecha.
- [ ] Las 10 secciones presentes, sin adicionales ni omisiones (§3).
- [ ] §1 deriva de objetivos ROADMAP de la fase (traducción a capacidades, no copia).
- [ ] §2 cita IDs de evidencia forense existentes en `00-foundation/`.
- [ ] §2.1 documenta el outcome de la compuerta de auditoría.
- [ ] §3 declara dimensiones ortogonales y sus no-implicaciones.
- [ ] §4 declara no-objetivos con fase propietaria explícita para cada ítem.
- [ ] §5 sin nombres de clases/tecnologías y sin reglas RFC-2119.
- [ ] §6 sin waves/tasks/owners/fechas; incluye la Cláusula de Relación con el Execution Plan.
- [ ] §7 conserva regla de blindaje y, si la auditoría está completa, queda como registro histórico.
- [ ] §8 sin DCs abiertos (resueltos con evidencia o diferidos con destino terminal).
- [ ] §9 declara solo la cadena normativa interna de la fase (HITos como evidencia, no como nivel) y referencia metodología general §2 sin duplicar la pirámide global.
- [ ] §10 define Nivel A y Nivel B verificables, sin DoD por tarea.
- [ ] ADRs Maestros pre-existentes no fueron reformateados (abuelamiento, §6).

---

## 9. RELACIÓN CON LA SUITE METODOLÓGICA

| Artefacto | Relación con el ADR Maestro |
|---|---|
| Metodología general | Secuencia el flujo (§6.1 paso 2) y permanece como nivel máximo de meta-gobernanza (§9.3); este documento es su template de artefacto para el nivel Maestro |
| `3_METH_ADR_PHASES.md` | Los ADRs de Fase derivan capacidades del Maestro; no lo redefinen |
| `4_METH_NADR.md` | Las invariantes de §5 del ADR son candidatas a materialización normativa en NADRs |
| `5_METH_EXECUTION_PLAN.md` | El Maestro §6 declara orden lógico de capacidades; el Execution Plan gobierna secuencia operativa, deploy y trazabilidad regla→task |
| `6_METH_*.md` | Los hallazgos de la fase (DF/GF) viven en Registers, nunca en el Maestro |
| `7_METH_HANDOFF.md` | El handoff de cierre referencia el Maestro como fuente de visión y restricciones carry-forward |

**Hogar confirmado:** suite metodológica numerada; este documento es
`2_METH_ADR_MASTER.md`. La alternativa de incorporación como §4.2 de la
metodología general quedó descartada por verificación de directorio (la suite
existe y el número 2 estaba libre).

---

## 10. VALIDACIÓN DE LA PLANTILLA

* **Retrospectiva:** `ADR_F17_BIS_MASTER.md` mapea 10/10 secciones de §3
  (contexto→§1, problema+outcome→§2/§2.1, separación→§3, alcance→§4,
  invariantes→§5, hoja de ruta→§6, Fase 0→§7, DC log→§8, governance→§9,
  DoD→§10). Queda abuelado sin reformatear (§6).
  Aclaración: el §9 del exemplar ya declaraba la cadena normativa interna
  (modelo de la regla actual); no cometía el anti-patrón de duplicar la pirámide
  global. Sus no-conformidades reales fueron: header sin campo de aprobación
  del Board y un componente nombrado en §4 (ambas abueladas, §6).
* **Prospectiva:** `ADR_F18_MASTER.md` (Advanced Local Runtime) es la primera
  emisión conforme a este documento; sus insumos son la auditoría forense del
  runtime y los hallazgos carry-forward con sinergia (DF-06, DF-34,
  DF-12-C/D/E) más los 5 entregables del ROADMAP para Fase 18.
* **Prácticas recomendadas (no normativas), derivadas del exemplar FROZEN
  ADR_F17_BIS_MASTER:** diagramas ASCII en §3 (dimensiones ortogonales) y §6
  (flujo de gobernanza); callout explícito de pivot normativo en §1 cuando la
  auditoría cambie el objetivo; nota "Historical Note" en §7 al pasar a registro
  histórico; preguntas DC formuladas sobre componentes concretos auditados
  (coherente con la regla de nivel de capacidad de §5). La conformidad se
  verifica con §8; estas prácticas elevan el techo comunicacional y se
  recomiendan, no se exigen.

---

**Nota de Gobernanza:** Este documento es el template canónico del nivel ADR
Maestro. No redefine la jerarquía de §2 de la metodología general ni las
responsabilidades de §3.1; las materializa en forma verificable para cada
emisión futura.