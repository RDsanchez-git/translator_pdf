# NADR-F17BIS-07: Healing Iteration & Atomic Rollback

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-07`
* **Título:** Healing Iteration & Atomic Rollback
* **Clase de Decisión:** `STRUCTURAL` / `BEHAVIORAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Validation Domain
* **Capacidad Arquitectónica:** CAP-008 (Unified Execution Plane) — etapa de curación iterativa post-inferencia
* **Evidencia Forense:** `P5-H03`, `P5-H05`, `GAP-P5-02`, `GAP-P5-03`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-04` (el pipeline de validación debe estar correctamente cableado para que la curación reciba los fallos reales).
  * **Influencia:** `NADR-F17BIS-08` (el plano de ejecución distribuido consume los resultados de la curación para decidir el estado de la unidad).
  * **Conflictúa con:** Toda arquitectura de curación que permita mutación no verificada del texto traducido.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operacional:** 4 — Unidades con múltiples fallos recuperables de familias distintas se rechazan prematuramente en una sola pasada, reduciendo la tasa de éxito del pipeline.
* **Mantenibilidad:** 3 — La revalidación redundante duplica la responsabilidad de verificación entre capas.
* **Recuperabilidad:** 4 — Sin detección de conflicto de mutaciones, una estrategia de curación puede introducir un nuevo fallo que pase desapercibido hasta el ensamblado final.
* **Seguridad:** 1
* **Financiero:** 2 — Unidades rechazadas prematuramente fuerzan re-inferencias al LLM, incrementando el costo FinOps.
* **Total Score: 14/25**

---

## 3. DECISIÓN EJECUTIVA

**El sistema de curación constituye una etapa transaccional del pipeline.**

Toda operación de curación constituye una transacción lógica con dos únicos estados finales válidos:

1. **Estado curado y certificado:** la mutación fue verificada y aceptada.
2. **Restauración íntegra del estado previo:** la mutación fue descartada y el texto original preservado sin degradación.

La curación debe operar mediante iteración controlada sobre los fallos recuperables y garantizar que únicamente estados completamente verificados puedan propagarse al flujo de producción.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

El bucle de curación post-inferencia presenta dos limitaciones estructurales que reducen la tasa de éxito del pipeline y duplican la responsabilidad de verificación:

1. **Disparo monofoco:** El despachador envía únicamente el primer fallo al contenedor de curación. Si una unidad posee múltiples fallos recuperables de familias distintas (por ejemplo, fuga de Markdown y desbalance de llaves simultáneamente), solo se intenta reparar el primero. Si la reparación del primer fallo no resuelve el segundo, la unidad se rechaza prematuramente.

2. **Revalidación redundante:** El contenedor de curación ejecuta internamente una revalidación para verificar la mutación. Sin embargo, el despachador vuelve a ejecutar la validación sobre el mismo texto tras recibir el resultado exitoso. Esta segunda llamada no aporta información nueva y duplica la responsabilidad de verificación entre capas.

### 4.2 Manifestación concreta identificada por la auditoría

* **`P5-H05` / `GAP-P5-02` (P2):** El despachador asíncrono ejecuta `healing_ctx = HealingContext(..., validation_result=hard_fails[0])`, enviando exclusivamente el primer fallo al pipeline de curación. No existe un bucle iterativo que procese múltiples familias de invariantes en una sola pasada.

* **`P5-H05` / `GAP-P5-03` (P2):** Tras recibir un resultado de curación exitoso, el despachador ejecuta una segunda llamada a `validate_chunk()` sobre el mismo texto que ya fue revalidado internamente por el contenedor de curación. Esta redundancia no compromete la seguridad pero duplica innecesariamente la responsabilidad de verificación.

* **`P5-H03` (SOTA / APROBADO):** Se demostró que el contenedor de curación posee un mecanismo de rollback atómico correcto: si la revalidación interna detecta un nuevo fallo tras la mutación, el resultado se marca como `FAILURE` y se preserva el texto original. El despachador solo actualiza el texto traducido si el resultado es `SUCCESS`. Esta garantía **debe** preservarse y extenderse a la iteración multi-falla.

### 4.3 Capacidad canónica existente

El dominio de curación ya define una arquitectura SOTA con:
* Un contrato base de estrategias de curación deterministas, registradas por familia de invariante y prioridad.
* Un contenedor de curación que orquesta la secuencia: evaluar → reparar → revalidar.
* Un modelo de resultado inmutable con soporte de rollback al texto original.
* Estrategias concretas para fuga de Markdown, fuga de metatexto y cierre de llaves/entornos matemáticos.

Estos componentes funcionan correctamente en el caso de un solo fallo. La limitación reside exclusivamente en el desencadenante monofoco del despachador y en la revalidación redundante.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Iteración multi-falla
1. El sistema de curación **MUST** ser capaz de recibir y procesar la colección completa de fallos recuperables emitidos por la validación, no un subconjunto arbitrario.
2. Cuando una unidad presente múltiples fallos recuperables de familias distintas, el contenedor de curación **MUST** aplicar las estrategias correspondientes de forma secuencial, respetando la prioridad declarada por cada estrategia.
3. **MUST NOT** existir un mecanismo de selección que descarte fallos recuperables adicionales antes de que el contenedor de curación haya tenido la oportunidad de procesarlos.

### 5.2 Rollback atómico
4. Toda mutación producida por una estrategia de curación **MUST** ser verificada mediante revalidación antes de ser aceptada como resultado final.
5. Si la revalidación detecta que la mutación introdujo un nuevo fallo o no resolvió el original, el sistema **MUST** restaurar el texto original de forma atómica, sin degradación parcial.
6. **MUST NOT** existir un camino de ejecución en el que una mutación no verificada sea propagada al ensamblador o al plano de persistencia.

### 5.3 Autoridad única de verificación
7. La revalidación **MUST** ocurrir exactamente una vez, dentro del contenedor de curación, como parte integral del ciclo evaluar → reparar → revalidar.
8. Las capas externas al contenedor de curación **MUST NOT** ejecutar una revalidación redundante sobre el texto ya certificado por el contenedor.
9. El resultado emitido por el contenedor de curación **MUST** ser suficiente para que las capas externas determinen si la mutación fue aceptada o rechazada, sin necesidad de re-ejecutar la validación.

### 5.4 Detección de conflictos de curación
10. Cuando múltiples estrategias de curación produzcan modificaciones incompatibles, el sistema **MUST** detectar el conflicto antes de aceptar el resultado.
11. Ante cualquier conflicto de curación, el rollback **MUST** restaurar el último estado válido.
12. **MUST NOT** permitirse que dos estrategias de curación produzcan modificaciones simultáneas sin un mecanismo de detección de conflicto.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **La curación deja de ser un algoritmo de reparación y se convierte en una transacción arquitectónica** con garantías de atomicidad y certificación. Toda mutación es verificada antes de ser aceptada, y cualquier fallo en la verificación restaura íntegramente el estado previo.
* Unidades con múltiples fallos recuperables de familias distintas dejarán de rechazarse prematuramente, incrementando la tasa de éxito del pipeline y reduciendo re-inferencias al LLM.
* Existe una única autoridad de verificación: el contenedor de curación es el único componente responsable de certificar una mutación antes de su aceptación.
* La eliminación de la revalidación redundante consolida la responsabilidad de verificación en una sola capa, simplificando el diagnóstico y la trazabilidad.
* La detección de conflictos de mutaciones previene que una estrategia de curación introduzca un nuevo fallo que pase desapercibido hasta el ensamblado final.
* La garantía de rollback atómico se extiende del caso de un solo fallo al caso de múltiples fallos secuenciales, preservando el invariante de no-degradación.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el contenedor de curación constituye la única autoridad de verificación del pipeline de curación.
  * Verificación de que la certificación de una mutación ocurre una única vez antes de su aceptación.
  * Verificación de que el resultado emitido por el contenedor de curación es suficiente para determinar la aceptación o rechazo de la mutación sin re-ejecutar la validación.

* **Validation (dinámica/comportamental):**
  * Una unidad con dos fallos recuperables de familias distintas **MUST** ser procesada por ambas estrategias de curación en una sola pasada.
  * Si la segunda estrategia introduce un nuevo fallo, el sistema **MUST** restaurar el texto original y marcar el resultado como `FAILURE`.
  * Una unidad curada exitosamente **MUST NOT** ser revalidada por capas externas al contenedor de curación.
  * Ante un conflicto de mutaciones, el sistema **MUST** activar el mecanismo de rollback atómico y preservar el estado previo.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio de tolerancia a fallos parciales aplicado a la etapa de curación. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-04` | **Dependencia directa:** el pipeline de validación debe estar correctamente cableado para que la curación reciba los fallos reales. |
| `NADR-F17BIS-08` | **Influencia:** el plano de ejecución distribuido consume los resultados de la curación para decidir el estado de la unidad y actualizar la FSM. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `3.2.1` y `3.2.2` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la implementación interna de las estrategias de curación individuales (fuga de Markdown, cierre de llaves, etc.). Cada estrategia gobierna su propia lógica de reparación.
* **No gobierna** el pipeline de validación que produce los fallos recuperables (responsabilidad de `NADR-F17BIS-04`).
* **No gobierna** el mecanismo de despacho asíncrono ni la gestión de concurrencia del despachador (responsabilidad de `NADR-F17BIS-08`).
* **No gobierna** la taxonomía de errores de validación ni la severidad de los fallos (responsabilidad del dominio de validación).
* **No gobierna** el ensamblado del documento ni la política de tolerancia a fallos degradables (responsabilidad del ensamblador y `AssemblyPolicy`).
* **No gobierna** el mecanismo específico de detección de conflictos de curación (offsets, AST, diff, spans, hashes). El NADR exige la existencia del mecanismo, no su implementación.
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.