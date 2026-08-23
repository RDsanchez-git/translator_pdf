# NADR-F{FASE}-{XX}: {Título descriptivo de la capacidad gobernada}

## 1. METADATA

* **Decision ID:** `NADR-F{FASE}-{XX}`
* **Título:** {Título descriptivo de la capacidad arquitectónica gobernada}
* **Clase de Decisión:** `{STRUCTURAL | OPERATIONAL | DATA | GOVERNANCE}` {Puede ser múltiple: `OPERATIONAL / DATA`}
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** {X.Y.Z}
* **Ciclo de Vida:** `{DRAFT | APPROVED | FROZEN | SUPERSEDED}`
* **Vigente Desde:** {Fase o hito a partir del cual aplica}
* **Autoridad:** Architecture Board
* **Responsable Técnico:** {Equipo o rol responsable de la implementación}
* **Capacidad Arquitectónica:** {CAP-XXX} ({Nombre de la capacidad}) — {descripción breve}
* **Evidencia Forense:** {IDs de hallazgos, gaps y evidencias que motivan este NADR. Formato: `E-{bloque}-{N}`, `GAP-{bloque}-{N}`, `P{bloque}-H{N}`}
* **Referencias Cruzadas:**
  * **Depende de:** {NADRs, ADRs u otros artefactos que son prerequisito para este NADR}
  * **Influencia:** {NADRs o artefactos que este NADR condiciona o habilita}
  * **Conflictúa con:** {Patrones, prácticas o decisiones que este NADR prohíbe explícitamente}
  * **Reemplaza a:** {NADR anterior que este supersede, o `N/A`}

---

## 2. ARCHITECTURE RISK SCORE

{Evaluar cada dimensión de 1 (riesgo mínimo) a 5 (riesgo máximo).
Justificar brevemente cada puntaje. El score total determina la severidad:
S1 = 16-25 (crítico), S2 = 11-15 (alto), S3 = 6-10 (medio).}

* **Operacional:** {1-5} — {Justificación: qué pasa operacionalmente si no se gobierna esta capacidad}
* **Mantenibilidad:** {1-5} — {Justificación: impacto en la capacidad de evolucionar el sistema}
* **Recuperabilidad:** {1-5} — {Justificación: capacidad de recuperación ante fallo}
* **Seguridad:** {1-5} — {Justificación: exposición a vulnerabilidades}
* **Financiero:** {1-5} — {Justificación: impacto en costos de operación o desarrollo}
* **Total Score: {N}/25**

**Severidad:** `{S1 | S2 | S3}`

---

## 3. DECISIÓN EJECUTIVA

{Una única sentencia constitucional clara que define la decisión.
Debe poder leerse como una ley permanente.
NO es una lista de tareas ni una descripción de implementación.
NO menciona clases, archivos, funciones ni tecnologías concretas.}

**{La decisión en una sola oración imperativa.}**

En consecuencia:
* {Implicación directa 1: qué queda prohibido o requerido como consecuencia}
* {Implicación directa 2}
* {Implicación directa N}

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

{Descripción abstracta del problema en términos de capacidad arquitectónica.
Qué capacidad está ausente, degradada o violada.
NO mencionar soluciones ni implementaciones.}

{Describir las clases de defectos o ausencias identificadas:}
1. **{Clase de defecto 1}:** {Descripción abstracta}
2. **{Clase de defecto 2}:** {Descripción abstracta}
3. **{Clase de defecto N}:** {Descripción abstracta}

### 4.2 Manifestación concreta identificada por la auditoría

{Aquí SÍ se permiten nombres de clases, archivos y funciones como EVIDENCIA.
Cada manifestación debe referenciar el ID de evidencia forense.}

* **`{E-X.X-NNN}` / `{GAP-XX-NN}` ({P0 | P1 | P2} — {Crítico | Alto | Medio}):** {Descripción de la manifestación concreta con nombres de archivos, clases y líneas}

* **`{E-X.X-NNN}` / `{GAP-XX-NN}` ({P0 | P1 | P2} — {Crítico | Alto | Medio}):** {Descripción}

* **`{P{bloque}-H{N}}` ({P0 | P1 | P2} — {Crítico | Alto | Medio}):** {Descripción}

---

## 5. REGLAS NORMATIVAS (RFC 2119)

{Reglas abstractas agrupadas por dominio de responsabilidad.
Cada regla usa MUST / MUST NOT / SHOULD / MAY / SHOULD NOT.
Numeración continua a través de todas las sub-secciones.
NUNCA mencionar clases, archivos, funciones ni tecnologías concretas.
Cada regla debe ser verificable.}

### 5.1 {Dominio de responsabilidad 1}
1. {Sujeto abstracto} **MUST** {obligación}.
2. {Sujeto abstracto} **MUST NOT** {prohibición}.
3. {Condición} **MUST** {consecuencia obligatoria}.

### 5.2 {Dominio de responsabilidad 2}
4. {Sujeto abstracto} **MUST** {obligación}.
5. {Sujeto abstracto} **MUST NOT** {prohibición}.

### 5.3 {Dominio de responsabilidad 3}
6. {Sujeto abstracto} **MUST** {obligación}.
7. {Condición} **MUST** {consecuencia obligatoria}.

### 5.{N} {Dominio de responsabilidad N}
{Continuar numeración...}

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

{Qué cambia en el sistema como resultado de la decisión.
NO son tareas de implementación.
NO son métricas de proyecto.
Describir el estado resultante del sistema una vez materializadas las reglas.}

* {Consecuencia 1: qué capacidad queda garantizada o qué riesgo queda eliminado}
* {Consecuencia 2}
* {Consecuencia 3}
* {Consecuencia N}

---

## 7. VERIFICACIÓN Y VALIDACIÓN

{Separar explícitamente los mecanismos estáticos/mecánicos (verification)
de los mecanismos dinámicos/comportamentales (validation).}

* **Verification (estática/mecánica):**
  * {Verificación 1: linter, type checker, grep, import-linter, property test}
  * {Verificación 2}
  * {Verificación N}

* **Validation (dinámica/comportamental):**
  * {Validación 1: test de regresión, golden corpus, E2E, mutation testing}
  * {Validación 2}
  * {Validación N}

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

{Tabla de relaciones con otros NADRs, ADRs y Execution Plan.
Cada relación debe ser explícita y bidireccional.
Si este NADR depende de otro, el otro debe listar este como influencia.}

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F{FASE}_MASTER` | {Cómo este NADR materializa la visión del ADR Maestro} |
| `ADR_F{FASE}_{XX}` | {Relación con el ADR de Fase si existe} |
| `NADR-F{FASE}-{YY}` | **{Dependencia directa | Influencia | Conflicto}:** {Descripción de la relación} |
| `NADR-F{FASE}-{ZZ}` | **{Dependencia directa | Influencia | Conflicto}:** {Descripción de la relación} |
| `PHASE_{FASE}_EXECUTION_PLAN` | {Qué tareas materializan estas reglas} |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

{Lista explícita de responsabilidades que NO pertenecen a este NADR.
Con referencia al NADR o artefacto que SÍ las gobierna.
Esta sección es OBLIGATORIA en todo NADR.}

* **No gobierna** {responsabilidad excluida 1} (responsabilidad de {NADR/artefacto que sí la gobierna}).
* **No gobierna** {responsabilidad excluida 2} (responsabilidad de {NADR/artefacto}).
* **No gobierna** {responsabilidad excluida 3}.
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.