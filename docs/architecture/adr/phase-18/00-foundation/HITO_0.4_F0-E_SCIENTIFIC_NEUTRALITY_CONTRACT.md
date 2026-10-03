# HITO_0.4_F0-E_SCIENTIFIC_NEUTRALITY_CONTRACT.md

**Estado:** FROZEN v1.3.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Compliance Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** `core/ast/hashing.py`, `core/benchmark/topology/regression/mechanism.py`, `core/benchmark/verification/outcome.py`, `core/benchmark/verification/identity_chain.py`, `core/compiler/assembler.py`, `core/execution/state.py`, `INV-SCI-1`, `INV-NO-RESOURCE-SIGNAL`, `INV-ASSEMBLY-ORDER`, `FASE0_AUDIT_CHARTER.md` §4, `HITO_0.1_F0-B`, `HITO_0.2_F0-G`, `HITO_0.3_F0-F`
**Mandato:** Definir el contrato del guard diferencial y el mapa de aislamiento runtime vs. ciencia para garantizar INV-SCI-1 e INV-NO-RESOURCE-SIGNAL.
**Síntesis:** Se identifican los prerrequisitos necesarios para el guard diferencial (determinismo de componentes), pero la neutralidad científica end-to-end del runtime queda pendiente de demostración experimental (M1). Se establece la separación estricta entre scientific equality (strict) y operational evidence (not required). DC-02 se identifica como precondición para definir qué constituye igualdad científica.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-02 | Emisión inicial basada en auditoría de mecanismos de hashing y exit codes. |
| 1.1.0-FROZEN | 2026-10-02 | Cierre formal tras reconciliación de invariantes científicas. |
| 1.2.0-FROZEN | 2026-10-02 | Adición de secciones 11, 18, 19 (completitud estructural). |
| 1.3.0-FROZEN | 2026-10-02 | Reconciliación epistemológica: E-0.4-001/002/003 rebajadas a prerrequisitos (no neutralidad end-to-end); INV-ASSEMBLY-ORDER pendiente de M1; INV-NO-RESOURCE-SIGNAL rebajado a PARTIAL; separación scientific equality / operational evidence; DC-02 identificado como precondición; eliminación de implementation prescription. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la superficie de hashing, ensamblado y propagación de exit codes para definir el contrato del guard diferencial que garantizará INV-SCI-1 (neutralidad científica) e INV-NO-RESOURCE-SIGNAL (presión de recursos ⇒ outcome operacional, nunca señal científica).

**Hallazgo central:**

> Se identifican los prerrequisitos necesarios para el guard diferencial (determinismo de componentes: hashing de AST, ensamblado de artefactos, métricas científicas), pero la neutralidad científica end-to-end del runtime (que el modo concurrente preserve la entrada científica final) queda pendiente de demostración experimental (M1 del Charter §8.1). Se establece la separación estricta entre scientific equality (strict) y operational evidence (not required). DC-02 se identifica como precondición para definir qué constituye igualdad científica.

**Prerrequisitos verificados:**

1. **Hashing de AST determinista (E-0.4-001):** `compute_ast_hash()` es determinista e insensible al orden de procesamiento.
2. **Ensamblado determinista bajo mismas entradas (E-0.4-002):** `DocumentAssembler.assemble()` mergea por identidad/lineage.
3. **Métricas científicas deterministas bajo mismo AST (E-0.4-003):** `DoubleProtectionMechanism.evaluate()` calcula NSS y Critical FN de forma reproducible.
4. **Exit codes operacionales (E-0.4-004):** Mapeo bien definido de verdicts científicos a exit codes 0-4.

**Propiedades end-to-end pendientes de M1:**

1. **Neutralidad científica end-to-end:** Que el runtime concurrente preserve la entrada científica final (no demostrado; requiere M1).
2. **INV-ASSEMBLY-ORDER end-to-end:** Que ejecuciones concurrentes con permutaciones forzadas del orden de completitud produzcan identidad de artefacto idéntica (no demostrado; requiere M1).
3. **INV-NO-RESOURCE-SIGNAL end-to-end:** Que las señales operacionales (OOM, timeout) no contaminen el estado científico (parcial; requiere auditoría de propagación interna en F0-C).

**Veredicto:** Se requiere un mecanismo reproducible para ejecutar y comparar dos modos de ejecución bajo iguales parámetros científicos (guard diferencial). La demostración completa de neutralidad científica end-to-end corresponde al experimento M1, no a este HITO.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Este HITO es read-only. No prescribe la implementación del guard diferencial. No demuestra neutralidad científica end-to-end (eso corresponde a M1). Solo identifica los prerrequisitos necesarios y establece el contrato de separación entre scientific equality y operational evidence.

### 2.2 Método forense
1. Cargar fuentes normativas (`INV-SCI-1`, `INV-NO-RESOURCE-SIGNAL`, `FASE0_AUDIT_CHARTER.md` §4).
2. Inspeccionar `core/ast/hashing.py` para identificar el mecanismo de hashing de AST.
3. Inspeccionar `core/compiler/assembler.py` para identificar el mecanismo de ensamblado.
4. Inspeccionar `core/benchmark/verification/outcome.py` para mapear exit codes.
5. Separar Observed (mecanismos actuales) / Required (invariantes) / Decision (contrato de comparación).
6. Registrar evidencia estable con IDs y severidad.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/ast/` | `hashing.py` | 100% Auditado |
| `core/compiler/` | `assembler.py` | 100% Auditado |
| `core/benchmark/topology/regression/` | `mechanism.py` | 100% Auditado |
| `core/benchmark/verification/` | `outcome.py`, `identity_chain.py` | 100% Auditado |
| `core/execution/` | `state.py` | Referenciado (FSM) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Código | `core/ast/hashing.py` | Observación de mecanismo de hashing de AST |
| Código | `core/compiler/assembler.py` | Observación de mecanismo de ensamblado |
| Código | `core/benchmark/topology/regression/mechanism.py` | Observación de DoubleProtectionMechanism (NSS, Critical FN) |
| Código | `core/benchmark/verification/outcome.py` | Observación de exit codes 0-4 |
| Invariante | `INV-SCI-1`, `INV-NO-RESOURCE-SIGNAL`, `INV-ASSEMBLY-ORDER` (Charter §4) | Required: Neutralidad científica y aislamiento operacional |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Hashing de AST (prerrequisito) | `compute_ast_hash()` calcula SHA-256 sobre nodos AST (content, type, strategy) | INV-SCI-1: misma baseline + mismos params ⇒ misma salida científica | Ninguna | PREREQUISITE VERIFIED | E-0.4-001 |
| Ensamblado de artefactos (prerrequisito) | `DocumentAssembler.assemble()` reconstruye documento desde proyecciones materializadas | INV-ASSEMBLY-ORDER: ejecuciones concurrentes ⇒ misma identidad de artefacto | Ninguna | PREREQUISITE VERIFIED; end-to-end pending M1 | E-0.4-002 |
| Métricas científicas (prerrequisito) | `DoubleProtectionMechanism.evaluate()` calcula NSS y Critical FN | INV-SCI-1: métricas científicas invariantes ante variación operacional | Ninguna | PREREQUISITE VERIFIED | E-0.4-003 |
| Exit codes (boundary) | `outcome_to_exit_code()` mapea verdicts científicos a exit codes 0-4 | INV-NO-RESOURCE-SIGNAL: presión de recursos ⇒ exit 4, nunca señal científica | Ninguna | PARTIAL (boundary verified; internal propagation pending F0-C) | E-0.4-004, E-0.4-005 |
| Contaminación FSM (internal propagation) | `DocumentState` tiene estados `FAILED_RETRYABLE`, `FAILED_FATAL`, `CANCELLED` | INV-NO-RESOURCE-SIGNAL: OOM/timeout ⇒ estado operacional, no científico | Ninguna | TO BE VERIFIED | E-0.4-005 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.4-001: Hashing de AST determinista (prerrequisito)
* **Archivo Fuente Primario:** `core/ast/hashing.py`
* **Símbolo Auditado:** `compute_ast_hash`
* **Declaración Observada:** Calcula SHA-256 sobre una representación canónica de los nodos AST (content, type, strategy, omitiendo sequence_id).
* **Observed:** El hashing es determinista e insensible al orden de procesamiento (omite sequence_id).
* **Required:** INV-SCI-1 exige que misma baseline + mismos params ⇒ misma salida científica.
* **Hallazgo Forense:** **PREREQUISITE VERIFIED:** El mecanismo de hashing existente satisface la condición necesaria para INV-SCI-1 a nivel de nodo AST. **NO DEMOSTRADO:** Que el runtime concurrente preserve la entrada científica final (eso requiere M1).
* **Consecuencia Arquitectónica:** Reutilizar `compute_ast_hash()` como base del guard diferencial.
* **Estado:** PREREQUISITE VERIFIED (end-to-end pending M1)
* **Severidad:** P0

### Evidencia E-0.4-002: Ensamblado determinista bajo mismas entradas (prerrequisito)
* **Archivo Fuente Primario:** `core/compiler/assembler.py`
* **Símbolo Auditado:** `DocumentAssembler.assemble`
* **Declaración Observada:** Reconstruye el documento desde proyecciones materializadas, validando secuencia y completitud.
* **Observed:** El ensamblado es determinista si las proyecciones de entrada son idénticas.
* **Required:** INV-ASSEMBLY-ORDER exige que ejecuciones concurrentes con permutaciones forzadas del orden de completitud produzcan identidad de artefacto idéntica.
* **Hallazgo Forense:** **PREREQUISITE VERIFIED:** El ensamblado mergea por identidad/lineage, no por orden de llegada. Esta es una condición necesaria para INV-ASSEMBLY-ORDER. **NO DEMOSTRADO:** Que ejecuciones concurrentes con permutaciones forzadas produzcan efectivamente la misma identidad de artefacto (eso requiere M1).
* **Consecuencia Arquitectónica:** Reutilizar el hash del artefacto ensamblado como base del guard diferencial.
* **Estado:** PREREQUISITE VERIFIED; end-to-end pending M1
* **Severidad:** P0

### Evidencia E-0.4-003: Métricas científicas deterministas bajo mismo AST (prerrequisito)
* **Archivo Fuente Primario:** `core/benchmark/topology/regression/mechanism.py`
* **Símbolo Auditado:** `DoubleProtectionMechanism.evaluate`
* **Declaración Observada:** Calcula NSS (Normalized Structural Similarity) y Critical FN (False Negatives críticos) comparando el AST sujeto contra el oráculo sellado.
* **Observed:** Las métricas son deterministas si el AST sujeto es idéntico.
* **Required:** INV-SCI-1 exige que las métricas científicas sean invariantes ante variación operacional.
* **Hallazgo Forense:** **PREREQUISITE VERIFIED:** Las métricas científicas existentes satisfacen la condición necesaria para INV-SCI-1 bajo mismo AST. **NO DEMOSTRADO:** Que el runtime concurrente preserve el AST sujeto (eso requiere M1).
* **Consecuencia Arquitectónica:** Reutilizar NSS y Critical FN como base del guard diferencial.
* **Estado:** PREREQUISITE VERIFIED (end-to-end pending M1)
* **Severidad:** P0

### Evidencia E-0.4-004: Exit codes operacionales (boundary verified)
* **Archivo Fuente Primario:** `core/benchmark/verification/outcome.py`
* **Símbolo Auditado:** `outcome_to_exit_code`
* **Declaración Observada:** Mapea verdicts científicos (PASS, WARNING, HARD_FAIL) a exit codes 0-2, y fallos de integridad/ejecución a exit codes 3-4.
* **Observed:** Los exit codes están bien definidos y son mutuamente excluyentes a nivel de boundary del proceso.
* **Required:** INV-NO-RESOURCE-SIGNAL exige que presión de recursos ⇒ exit 4 (EXECUTION_FAILURE), nunca señal científica.
* **Hallazgo Forense:** **PARTIAL:** El mapeo de exit codes satisface INV-NO-RESOURCE-SIGNAL a nivel de boundary del proceso. **NO DEMOSTRADO:** Que la propagación interna (resource exhaustion → execution layer → FSM/persistence → verification outcome → process exit) no contamine el estado científico (E-0.4-005).
* **Consecuencia Arquitectónica:** Reutilizar exit codes 0-4 en el guard diferencial; requiere auditoría de propagación interna en F0-C.
* **Estado:** PARTIAL (boundary verified; internal propagation pending F0-C)
* **Severidad:** P0

### Evidencia E-0.4-005: Riesgo de contaminación FSM por señales operacionales
* **Archivo Fuente Primario:** `core/execution/state.py`
* **Símbolo Auditado:** `DocumentState`
* **Declaración Observada:** El FSM tiene estados `FAILED_RETRYABLE`, `FAILED_FATAL`, `CANCELLED`, `STALLED`.
* **Observed:** No hay evidencia forense de que un OOM o timeout derive explícitamente en un estado operacional separado (ej. `RESOURCE_EXHAUSTED`) sin contaminar los estados científicos.
* **Required:** INV-NO-RESOURCE-SIGNAL exige que presión de recursos ⇒ outcome operacional, nunca señal científica.
* **Hallazgo Forense:** Riesgo de que un OOM derive en `FAILED_FATAL` (estado científico) en lugar de un estado operacional, contaminando la evidencia científica.
* **Consecuencia Arquitectónica:** Requiere auditoría de flujo en F0-C para verificar cómo se propagan las señales de recursos al FSM.
* **Estado:** TO BE VERIFIED
* **Severidad:** P1

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-0.4-01 | El guard diferencial requiere ejecutar el pipeline dos veces (modo actual vs. experimental), duplicando el costo computacional. | Medio | OPEN |
| OBS-0.4-02 | La tolerancia "bit a bit" debe aplicarse solo a scientific identity, no a operational evidence (timestamps, execution_id, queue timings, etc.). | Alto | OPEN |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.4-01** | Ausencia de mecanismo reproducible para ejecutar y comparar dos modos de ejecución bajo iguales parámetros científicos (guard diferencial). | E-0.4-001, E-0.4-002, E-0.4-003 | INV-SCI-1, Charter §4 | **Fase 18** (DC-12, M0→M1→M2→M3) | OPEN |
| **GAP-0.4-02** | Riesgo de contaminación FSM por señales operacionales (OOM/timeout ⇒ estado científico). | E-0.4-005 | INV-NO-RESOURCE-SIGNAL, Charter §4 | **Fase 18** (F0-C) | TO BE VERIFIED |
| **GAP-0.4-03** | DC-02 no resuelto: parámetros de runtime en identity científica vs metadata operacional. Precondición para definir qué constituye igualdad científica. | E-0.4-001, E-0.4-004 | INV-SCI-1, Charter §4 | **Fase 18** (DC-02) | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.4-A | `compute_ast_hash()` es determinista e insensible al orden de procesamiento. | CONFIRMADA (prerrequisito) | E-0.4-001 | Satisface condición necesaria para INV-SCI-1 a nivel de nodo. End-to-end pending M1. |
| H-0.4-B | `DocumentAssembler.assemble()` es determinista si las proyecciones de entrada son idénticas. | CONFIRMADA (prerrequisito) | E-0.4-002 | Satisface condición necesaria para INV-ASSEMBLY-ORDER. End-to-end pending M1. |
| H-0.4-C | Los exit codes 0-4 están bien definidos y son mutuamente excluyentes a nivel de boundary. | CONFIRMADA (boundary) | E-0.4-004 | Satisface INV-NO-RESOURCE-SIGNAL a nivel de salida del proceso. Internal propagation pending F0-C. |
| H-0.4-D | Un OOM o timeout puede derivar en `FAILED_FATAL` (estado científico) en lugar de un estado operacional. | TO BE VERIFIED | E-0.4-005 | Requiere auditoría de flujo en F0-C. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué se comparará en el guard diferencial?

**Estado actual verificado:**

1. `compute_ast_hash()` calcula SHA-256 sobre nodos AST (E-0.4-001) — prerrequisito verificado.
2. `DocumentAssembler.assemble()` reconstruye documentos desde proyecciones (E-0.4-002) — prerrequisito verificado.
3. `DoubleProtectionMechanism.evaluate()` calcula NSS y Critical FN (E-0.4-003) — prerrequisito verificado.

**Respuesta forense:**

El guard diferencial debe comparar:

**Scientific equality (strict, tolerancia cero):**
- Hash del AST por nodo: `compute_ast_hash(node)` para cada nodo del AST sujeto vs. el AST de referencia.
- Hash del artefacto ensamblado: SHA-256 del documento científico ensamblado vs. el artefacto de referencia (solo scientific artifact, no operational envelope).
- Métricas científicas por documento: NSS y Critical FN del `DoubleProtectionMechanism` vs. los valores de referencia.

**Operational evidence (not required, puede diferir):**
- Timestamps, execution_id, queue timings, worker ID, retry timing, CPU time, cache hit/miss, scheduling order.

**Subset canónico de evidencia científica:**
- Exit codes, identidad de ejecución, cobertura de perfil.

**Nota:** La distinción entre scientific artifact y operational envelope debe resolverse en DC-02 antes de definir el contrato final del guard diferencial.

**Implicación:**

Fase 18 debe implementar un mecanismo reproducible para ejecutar y comparar dos modos de ejecución bajo iguales parámetros científicos (M0→M1→M2→M3 del Charter §8.1). La demostración completa de neutralidad científica end-to-end corresponde al experimento M1.

### 16.2 ¿Cómo se garantiza INV-NO-RESOURCE-SIGNAL?

**Estado actual verificado:**

1. Los exit codes 0-4 están bien definidos a nivel de boundary (E-0.4-004).
2. El FSM tiene estados `FAILED_RETRYABLE`, `FAILED_FATAL`, `CANCELLED` (E-0.4-005).

**Respuesta forense:**

INV-NO-RESOURCE-SIGNAL se garantiza si:
- Agotamiento de budget ⇒ `EXECUTION_FAILURE` (exit 4) con evidencia persistida.
- Shed/cancel/hold con razón indexable propia (sin contaminar `DEAD_LETTER`/`RETRYING`).
- Sin nuevo estado FSM hasta auditar el existente (DC-11).

**Implicación:**

Fase 18 debe auditar cómo se propagan las señales de recursos (OOM, timeout, cancelación) al FSM y garantizar que derivan en estados operacionales, no científicos. Esto se verifica en F0-C.

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO ADR/NADR

| Regla | Fuente | Required | Observed | Estado | Evidencia |
|---|---|---|---|---|---|
| INV-SCI-1 | Charter §4 | Misma baseline + mismos params ⇒ misma salida científica | Prerrequisitos verificados (hashing, ensamblado, métricas); end-to-end pending M1 | PARTIAL (prerrequisitos verified; end-to-end pending M1) | E-0.4-001, E-0.4-002, E-0.4-003 |
| INV-NO-RESOURCE-SIGNAL | Charter §4 | Presión de recursos ⇒ outcome operacional, nunca señal científica | Exit codes 0-4 bien definidos a nivel de boundary; FSM requiere auditoría | PARTIAL | E-0.4-004, E-0.4-005 |
| INV-ASSEMBLY-ORDER | Charter §4 | Ejecuciones concurrentes ⇒ misma identidad de artefacto | Prerrequisito verificado (merge por identidad/lineage); end-to-end pending M1 | PARTIAL (prerrequisito verified; end-to-end pending M1) | E-0.4-002 |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-02** | Parámetros de runtime en identity científica vs metadata operacional | E-0.4-001, E-0.4-004 | Ausente: distinción scientific artifact / operational envelope no resuelta | **Fase 18** (precondición para definir igualdad científica) |
| **DC-12** | Contrato y promoción del guard diferencial | E-0.4-001, E-0.4-002, E-0.4-003 | Ausente: M0 no definido | **Fase 18** (M0→M1→M2→M3) |

---

## 19. APÉNDICE NO NORMATIVO -- RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Falsos positivos en guard diferencial | Si la tolerancia "bit a bit" se aplica a operational evidence (timestamps, execution_id), el guard rechazará ejecuciones válidas. | Alto (bloquea F18) | E-0.4-002, OBS-0.4-02 |
| Falsos negativos en guard diferencial | Si la tolerancia es demasiado laxa (ej. solo NSS), el guard aceptará ejecuciones degradadas. | Alto (viola INV-SCI-1) | E-0.4-002 |
| Costo computacional del guard | Ejecutar el pipeline dos veces duplica el costo computacional. | Medio | OBS-0.4-01 |
| Contaminación FSM por OOM | Si un OOM deriva en `FAILED_FATAL` en lugar de un estado operacional, contamina la evidencia científica. | Alto | E-0.4-005, H-0.4-D |
| DC-02 no resuelto | Si no se resuelve la distinción scientific artifact / operational envelope, el guard diferencial puede comparar incorrectamente. | Alto | GAP-0.4-03 |

---

## 21. CIERRE DEL HITO 0.4

Este HITO identifica los prerrequisitos necesarios para el guard diferencial (determinismo de componentes: hashing de AST, ensamblado de artefactos, métricas científicas), pero la neutralidad científica end-to-end del runtime queda pendiente de demostración experimental (M1). Se establece la separación estricta entre scientific equality (strict) y operational evidence (not required). DC-02 se identifica como precondición para definir qué constituye igualdad científica.

**Estado del HITO:** FROZEN v1.3.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados, todas las evidencias tienen ID estable y severidad, todos los gaps tienen fase destino explícita (Fase 18 / F0-C / DC-02 / DC-12), hipótesis H-0.4-A/B/C confirmadas como prerrequisitos, H-0.4-D marcada como TO BE VERIFIED con destino a F0-C, separación scientific equality / operational evidence establecida, DC-02 identificado como precondición, eliminación de implementation prescription.
**Verificación de cadena de gobernanza:** Alineado con `INV-SCI-1`, `INV-NO-RESOURCE-SIGNAL`, `INV-ASSEMBLY-ORDER` (Charter §4).
**Contradicciones con HITOs previos:** Ninguna.
**Decision Candidates generados:** DC-02 (precondición para igualdad científica), DC-12 (evidencia de entrada).
**Siguiente paso recomendado:** Consumir este HITO como evidencia de discovery para `ADR_F18_MASTER` §2 (Problema Arquitectónico) y §5 (Invariantes). La demostración completa de neutralidad científica end-to-end corresponde al experimento M1 (Charter §8.1).