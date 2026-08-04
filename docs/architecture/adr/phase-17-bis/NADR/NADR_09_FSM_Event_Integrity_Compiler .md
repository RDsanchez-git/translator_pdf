# NADR-F17BIS-09: FSM Event Integrity & Compiler I/O Isolation

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-09`
* **Título:** FSM Event Integrity & Compiler I/O Isolation
* **Clase de Decisión:** `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Runtime Domain / Compiler Domain
* **Capacidades Arquitectónicas:** CAP-003 (Event-Sourced CQRS Integrity), CAP-009 (Sandboxed Artifact Compilation)
* **Evidencia Forense:** `OBS-P1-07`, `P6-H02`, `P6-H03`, `P7-H05`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-03` (la firma documental determinista es precondición del Event Log y de la trazabilidad de artefactos).
  * **Relacionado con:** `NADR-F17BIS-08` (el plano de ejecución distribuido consume el Event Log para coordinar la recuperación y la rematerialización).
  * **Conflictúa con:** Toda transición de estado emitida fuera de la capa de orquestación; todo artefacto físico escrito en directorios compartidos del proceso.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S1)
* **Operacional:** 5 — Transiciones fantasma y eventos sintéticos corrompen el Event Log, estancando documentos indefinidamente en estados intermedios y haciendo imposible la reconciliación automática.
* **Mantenibilidad:** 4 — La mezcla de responsabilidades entre el adaptador de persistencia y la capa de orquestación impide razonar sobre el grafo real de estados.
* **Recuperabilidad:** 4 — Condiciones de carrera en el I/O del compilador corrompen artefactos finales de forma no determinista.
* **Seguridad:** 3 — Ejecución de binarios de compilación sin aislamiento expone el entorno anfitrión a recursos locales no autorizados.
* **Financiero:** 2 — Recompilaciones innecesarias por artefactos corruptos incrementan el costo de ciclo.
* **Total Score: 18/25**

---

## 3. DECISIÓN EJECUTIVA

**La máquina de estados constituye la única autoridad legítima para la evolución del ciclo de vida del documento.**

Esta decisión establece dos invariantes constitucionales:

**Invariante A — Integridad del Ciclo de Vida:**
La evolución del estado del documento está gobernada exclusivamente por la máquina de estados finitos y su Event Log. Toda transición se origina exclusivamente en la capa de orquestación. Los adaptadores de persistencia son materializadores pasivos sin capacidad de emitir, interceptar ni sintetizar transiciones de estado.

**Invariante B — Aislamiento de la Generación de Artefactos:**
La generación de artefactos físicos constituye una frontera aislada sin capacidad de modificar el estado del dominio. El compilador es un consumidor terminal del pipeline: lee proyecciones materializadas y produce artefactos binarios, pero no emite comandos, no muta entidades y no escribe en espacios compartidos del proceso.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Transiciones Sintéticas y Eventos Fantasma
* **`OBS-P1-07` / `P7-H05` (P2):** El adaptador de persistencia de estado, al recibir un comando de alto nivel, intercepta la transición y emite comandos intermedios sintéticos que la capa de orquestación jamás ordenó. Esto falsea la bitácora del Event Log, genera transiciones de compilación fantasma y rompe la trazabilidad causal del ciclo de vida.
* **Impacto:** El Event Log registra eventos que no corresponden a decisiones del orquestador, haciendo imposible auditar o reproducir el flujo real de estados.

### 4.2 Desalineación de Granularidad entre Pasos de Aplicación y FSM
* **`P7-H05` (P2):** Los pasos de la aplicación (`PARSING`, `CHUNKING`, `ASSEMBLING`, `FINISHED`) no coinciden uno-a-uno con los estados finos de la FSM (`READY_FOR_ASSEMBLY`, `ASSEMBLING`, `READY_FOR_COMPILATION`, `COMPILING`). El adaptador cubre este vacío emitiendo ráfagas de comandos encadenados.
* **Impacto:** La discrepancia de granularidad obliga al adaptador a "inventar" transiciones, ocultando la verdadera secuencia de estados.

### 4.3 Condiciones de Carrera en I/O del Compilador
* **`P6-H02` (P0):** El ejecutor de compilación escribe artefactos finales y registros de fallo directamente en el directorio de trabajo actual del proceso (`os.getcwd()`). Trabajos concurrentes sobreescriben mutuamente sus archivos, corrompiendo la salida final.
* **Impacto:** La salida del compilador no es determinista bajo concurrencia, violando el invariante de reproducibilidad.

### 4.4 Nomenclatura Engañosa de Infraestructura
* **`P6-H03` (P1):** El componente de ejecución del compilador está denominado como si ejecutara un contenedor aislado, pero en realidad invoca directamente el binario del sistema anfitrión mediante subproceso.
* **Impacto:** La nomenclatura engañosa oculta el nivel real de aislamiento y dificulta la auditoría de seguridad.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Integridad del Ciclo de Vida (Invariante A)
1. Toda transición de estado **MUST** originarse exclusivamente en la capa de orquestación mediante comandos explícitos.
2. Los adaptadores de persistencia **MUST NOT** emitir, interceptar ni sintetizar comandos o transiciones de estado que no hayan sido ordenados explícitamente por el orquestador.
3. Los pasos de la aplicación **MUST** estar sincronizados uno-a-uno con los estados de la máquina de estados finitos, de modo que cada invocación de persistencia refleje exactamente un paso ejecutado.
4. El Event Log **MUST** constituir la única bitácora causal del ciclo de vida del documento, conteniendo exclusivamente transiciones originadas por el orquestador.
5. **MUST NOT** existir mecanismos de auto-promoción que emitan comandos intermedios no ordenados para cubrir discrepancias de granularidad entre capas.

### 5.2 Aislamiento de la Generación de Artefactos (Invariante B)
6. Todo artefacto físico de compilación **MUST** escribirse en un espacio efímero y aislado por ejecución, prohibiendo escrituras en directorios compartidos del proceso.
7. La ejecución del compilador **MUST** constituir un efecto lateral aislado y **MUST NOT** emitir transiciones de estado ni modificar entidades del dominio.
8. El compilador **MUST** operar exclusivamente como consumidor terminal: lee proyecciones materializadas y produce artefactos binarios, sin capacidad de mutar el Event Log, la FSM ni el plano materializado.
9. Los componentes de infraestructura de compilación **MUST** ser denominados con veracidad, reflejando su naturaleza real de ejecución y su nivel efectivo de aislamiento.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El Event Log recupera su condición de bitácora causal fiel, conteniendo exclusivamente las transiciones ordenadas por el orquestador, lo que hace posible la auditoría y la reconciliación automática.
* La sincronización uno-a-uno entre pasos de aplicación y estados FSM elimina la necesidad de transiciones sintéticas, simplificando el razonamiento sobre el grafo de estados.
* El I/O del compilador deviene determinista bajo concurrencia, eliminando las condiciones de carrera y garantizando la integridad de los artefactos finales.
* La separación explícita entre el dominio y el compilador cierra la frontera hexagonal: el compilador no puede corromper el estado del sistema ni emitir eventos espurios.
* La nomenclatura honesta de infraestructura permite auditar con precisión el nivel real de aislamiento de cada componente.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que los adaptadores de persistencia no contienen lógica de emisión de comandos ni de auto-promoción de estados.
  * Verificación de que el I/O del compilador no escribe en directorios compartidos del proceso.
  * Verificación de que la nomenclatura de los componentes de infraestructura refleja su naturaleza real de ejecución.
  * Verificación de la sincronización uno-a-uno entre pasos de aplicación y estados FSM.

* **Validation (dinámica/comportamental):**
  * La ejecución concurrente de múltiples compilaciones **MUST** producir artefactos íntegros e independientes, sin sobrescritura ni corrupción.
  * El Event Log de un documento procesado **MUST** contener exclusivamente las transiciones originadas por el orquestador, sin comandos sintéticos ni transiciones fantasma.
  * La invocación del compilador **MUST NOT** alterar el estado de la FSM ni del plano materializado.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa los principios constitucionales de *Event Sourcing & CQRS Strictness* y *FSM State Machine Exclusivity*. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-03` | **Dependencia directa:** la firma documental determinista es precondición del Event Log y de la trazabilidad de artefactos. |
| `NADR-F17BIS-08` | **Relación:** el plano de ejecución distribuido consume el Event Log para coordinar la recuperación y la rematerialización. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `4.1.1`, `4.1.2` y `4.1.3` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la coordinación de cuotas, la resiliencia de circuitos ni el plano de ejecución distribuido (responsabilidad de `NADR-F17BIS-08`).
* **No gobierna** la fórmula de cálculo de firmas documentales ni la identidad semántica (responsabilidad de `NADR-F17BIS-03`).
* **No gobierna** la composición del pipeline ni el cableado de adaptadores (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** la tecnología específica de compilación ni el binario utilizado para producir el artefacto final.
* **No gobierna** la estructura de datos del Event Log ni el formato de las transiciones (responsabilidad del modelo de ejecución de `core/execution/`).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.