# NADR-F18-02: Bounded Concurrent Execution

## 1. METADATA

* **Decision ID:** `NADR-F18-02`
* **Título:** Bounded Concurrent Execution
* **Clase de Decisión:** `STRUCTURAL / OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.1
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Fase 18, Subfase 18.1
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Staff Engineering
* **Capacidad Arquitectónica:** CAP-BOUNDED-EXEC (Bounded Concurrent Execution) — define las reglas normativas que todo modelo de ejecución concurrente del execution plane local debe satisfacer, independientemente del mecanismo concreto adoptado, garantizando ejecución acotada por recursos, cancelación limpia, seguridad de concurrencia y visibilidad operacional mínima.
* **Evidencia Forense:** `GAP-0.1-01`, `GAP-0.1-02`, `GAP-0.1-03`, `DC-01`, `DC-05`, `DF-06`, `E-0.1-001`, `E-0.1-002`, `E-0.1-003`, `E-0.1-004`, `E-0.1-005`, `E-0.1-006`, `E-0.1-007`, `E-0.2-005`, `HITO_0.1 v1.2.0`, `HITO_0.12 v1.0.1`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F18_MASTER.md` FROZEN, `ADR_F18.1` v1.0.2 FROZEN, `NADR-F18-01` v1.0.3 FROZEN
  * **Influencia:** `NADR-F18-03` (pendiente, Subfase 18.2, journal semantics condicionado al modelo de ejecución), `ADR_F18.3` (pendiente, Subfase 18.3, admission policy sobre el mecanismo aquí normado), `DC-08` (Subfase 18.2), `DC-10` / `DC-11` (Subfase 18.3), `DC-12` / `ADR_F18.5` (pendiente, Subfase 18.5)
  * **Conflictúa con:** cualquier modelo de ejecución que altere la identidad científica, que permita ejecución ilimitada sin acotamiento de recursos, o que produzca resultados científicos parciales ante cancelación
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial. Establece el marco normativo para la ejecución concurrente bounded del execution plane local. No resuelve DC-01 ni DC-05; establece las reglas que cualquier modelo de ejecución debe satisfacer. |
| 1.0.1 | 2026-10-04 | Corrección de fronteras normativas (13 cambios): (1) C1 reformulado como respeto a resource envelope externo, no determinación de recursos disponibles. (2) C1 R2 reformulado como admission grant. (3) C3 backpressure reformulado como bounded buffering o mecanismo equivalente de propagación de presión. (4) C6 R15 separa mecanismo de shutdown de semántica de recovery (18.2). (5) C6 R12 protege evidencia científica canónica, no "resultados parciales" genéricos. (6) C7 R18 reemplaza "normal operation" por "operational envelope declarado". (7) C11 R24 reformulado como propiedad observable, no nueva FSM. (8) Verification isolation reducido a cross-reference de INV-VERIFICATION-ISOLATION. (9) Regla 30 eliminada (redundante con DC-06b + Charter §9). (10) §7 convertido de métodos de test a propiedades verificables. (11) Lenguaje forense corregido: "impide" sustituido por "deja no demostrado". (12) Risk Score mantenido conforme al template canónico con justificaciones mejoradas. (13) Nota explícita de execution plane local añadida. |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin ejecución acotada, el sistema puede agotar recursos (OOM), perder trabajo en vuelo, o producir estado inconsistente bajo carga. La barrera síncrona observada (E-0.1-001) deja no demostrado el comportamiento de bounded execution y backpressure bajo carga. Sin cancelación limpia, el shutdown puede dejar threads residuales con sockets abiertos (E-0.1-004).
* **Mantenibilidad:** 4 — Sin un modelo de concurrencia normado, toda evolución del execution plane riesgo de introducir condiciones de carrera, deadlocks o fugas de recursos. La coordinación multi-thread actual mediante 3 threading.Event separados (E-0.1-002) dificulta el razonamiento sobre el estado concurrente.
* **Recuperabilidad:** 4 — Sin cancelación cooperativa y ejecución acotada, la recuperación ante fallos se vuelve no confiable. El riesgo de thread residual en shutdown (GAP-0.1-03) puede impedir el reinicio limpio del sistema.
* **Seguridad:** 2 — No es directamente una superficie de ataque externo. Sin embargo, el agotamiento de recursos por ejecución ilimitada podría degradar la disponibilidad del sistema.
* **Financiero:** 3 — La ejecución ilimitada o mal acotada puede producir trabajo duplicado, retries innecesarios y consumo de tokens sin valor. Sin embargo, el impacto financiero directo es menor que el operacional porque el sistema opera localmente conforme a ROADMAP v3.0 §I (herramienta local, no distribuida).

* **Total Score: 18/25**

**Severidad:** `S1` (crítico)

---

## 3. DECISIÓN EJECUTIVA

**Todo modelo de ejecución concurrente del execution plane local debe satisfacer las propiedades de ejecución acotada por recursos, cancelación cooperativa y oportuna, seguridad de concurrencia, mecanismo de admisión y backpressure, y visibilidad operacional mínima, sin alterar la identidad científica ni la evidencia científica canónica; la selección del modelo concreto de concurrencia queda sujeta a la resolución de DC-01 con evidencia cuantitativa previa.**

En consecuencia:

* Ningún modelo de ejecución puede ser adoptado sin evidencia cuantitativa de su impacto en bounded execution, backpressure y cancellation conforme al criterio preregistrado (Charter §9).
* Las reglas aquí establecidas son independientes del mecanismo concreto (async single-process, multi-process, híbrido); cualquier modelo que las satisfaga es arquitectónicamente válido.
* La admisión de trabajo como mecanismo de ejecución (cómo entra/sale trabajo del execution plane) queda normada aquí; la admisión como política de recursos (cuándo debe admitirse trabajo según recursos, prioridad y presupuesto) corresponde a la Subfase 18.3.
* El backpressure como mecanismo de flow control (cómo se propaga la presión) queda normado aquí; el backpressure como política de recursos (cuándo y cuánto limitar) corresponde a la Subfase 18.3.
* La visibilidad operacional mínima es un instrumento para gobernar la ejecución concurrente, no un fin en sí mismo; la observabilidad profunda corresponde a Fase 20.
* La frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II debe ser respetada; la evaluación del modelo de concurrencia debe ser independiente de la infraestructura de aplicaciones.

**Nota de alcance:** Este NADR gobierna el execution plane local de nodo único conforme a ROADMAP v3.0 §I y §V. No establece una arquitectura distribuida ni pretende ser una abstracción futura para multi-node. La infraestructura distribuida (Redis, Message Brokers, Kubernetes, microservicios) está explícitamente fuera del alcance del ROADMAP.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de ejecutar trabajo concurrentemente de forma acotada, cancelable y segura no está normada. El execution plane actual opera bajo un modelo híbrido dual cuya arquitectura de concurrencia no ha sido decidida formalmente sobre evidencia cuantitativa.

ADR_F18_MASTER §5.1 estableció las invariantes constitucionales (INV-SCI-1, INV-OPS-1, INV-VERIFICATION-ISOLATION). NADR-F18-01 estableció la frontera de identidad. Sin embargo, las reglas normativas que el modelo de ejecución concurrente debe satisfacer para respetar esas invariantes no han sido promulgadas.

Clases de defectos identificados:

1. **Ausencia de acotamiento normativo de la ejecución:** No existe regla que obligue al execution plane a respetar un límite de recursos asignado. La barrera síncrona observada (E-0.1-001) deja no demostrado el comportamiento de bounded execution y backpressure bajo carga (GAP-0.1-01).
2. **Coordinación concurrente no normada:** La coordinación multi-thread mediante 3 threading.Event separados (E-0.1-002) introduce una superficie de coordinación concurrente cuya seguridad frente a condiciones de carrera y cuyo comportamiento de cancelación limpia no han sido demostrados (GAP-0.1-02).
3. **Cancelación no garantizada:** El shutdown con bounded join (E-0.1-004) tiene un límite de tiempo acotado, pero si la coroutine subyacente no coopera con la cancelación, el thread puede quedar residual (GAP-0.1-03). No existe regla que obligue a la cancelación cooperativa.
4. **Mecanismo de admisión y backpressure ausente como norma:** El worker asíncrono observado (E-0.1-007) usa await queue.get() para backpressure, pero no existe regla normativa que obligue a todo modelo de ejecución a proporcionar este mecanismo.
5. **Visibilidad operacional mínima no normada:** No existe regla que obligue al execution plane a proporcionar la visibilidad mínima necesaria para gobernar la ejecución concurrente.
6. **Frontera hexagonal violada:** Existen imports cruzados de core hacia apps (E-0.2-005, DF-06) que dificultan la evaluación independiente del modelo de concurrencia. La frontera hexagonal ya está establecida en ENGINEERING_PRINCIPLES §II; DF-06 es una manifestación concreta que debe ser evaluada y eventualmente resuelta.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-0.1-001` (P1 — Alto):** Barrera síncrona en SyncProviderBridge (`apps/llm_workers/sync_bridge.py::SyncProviderBridge.execute`, L95). El método execute() bloquea el thread del worker con future.result(timeout=180.0). El impacto cuantitativo en C1 y C3 no ha sido medido (GAP-0.1-01).
* **`E-0.1-002` (P2 — Medio):** Coordinación multi-thread observada (`apps/llm_workers/__main__.py::LLMWorkerDaemon`, L96; TaskLeaseHeartbeat, L43; SyncProviderBridge, L26). El daemon usa 3 threads independientes y 3 threading.Event separados. El impacto en C7 y C10 no ha sido evaluado (GAP-0.1-02).
* **`E-0.1-003` (P2 — Medio):** Concurrencia nativa asyncio observada (`apps/llm_workers/dispatcher.py::AsyncDispatcher.dispatch`, L233, L285, L291). AsyncDispatcher implementa concurrencia asyncio con PriorityQueue, create_task y cancelación explícita. El daemon de producción no lo usa directamente.
* **`E-0.1-004` (P2 — Medio):** Shutdown con bounded join (`apps/llm_workers/sync_bridge.py::SyncProviderBridge.shutdown`, L48, L99). El shutdown cancela tareas pendientes y hace join(timeout=2.0). FACT: el shutdown tiene límite acotado. RISK: si la librería HTTP no coopera con asyncio cancellation, el thread puede quedar residual. NO DEMOSTRADO: que existan threads huérfanos o impacto material (GAP-0.1-03).
* **`E-0.1-005` (P2 — Medio):** Shutdown por señal observado (`apps/llm_workers/__main__.py`, L280-L281). El daemon maneja SIGINT/SIGTERM configurando _stop_event.
* **`E-0.1-006` (P2 — Medio):** Backoff exponencial en polling (`apps/llm_workers/__main__.py::LLMWorkerDaemon.run`, L113). El daemon usa backoff exponencial (base 1.0s, max 4.0s, factor 1.2) con jitter aleatorio. FACT: puede introducir hasta ~4.5s de latencia adicional bajo condición idle. NO DEMOSTRADO: relevancia bajo carga real.
* **`E-0.1-007` (P2 — Medio):** Worker asíncrono con backpressure (`apps/llm_workers/dispatcher.py::AsyncDispatcher._worker`, L134, L138, L219). El worker usa await queue.get() para backpressure, procesa asíncronamente y marca task_done(). La estructura observada es compatible con bounded execution.
* **`E-0.2-005` (P1 — Alto):** Imports cruzados de `core/benchmark/runners/` hacia `apps/llm_workers` y `apps/bootstrap` (DF-06). Violan la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II y dificultan la evaluación independiente del modelo de concurrencia.
* **`DC-01` (DEFERRED — destino 18.1):** Fork de concurrencia: async single-process + executors vs multi-process. Su resolución requiere evidencia cuantitativa previa (GAP-0.5-02 y GAP-0.1-01).
* **`DC-05` (DEFERRED — destino 18.1, dependencia DC-01):** Unificar ExecutionContext o contextos especializados. Condicionado a DC-01.
* **`DF-06` (Deferred Finding — destino 18.1, condicional):** Imports cruzados core→apps. Será evaluado y, si la auditoría confirma la dependencia arquitectónica identificada, su resolución quedará incluida en esta subfase. La frontera hexagonal ya está establecida en ENGINEERING_PRINCIPLES §II; DF-06 no genera un nuevo dominio normativo.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Bounded Execution (C1)

1. El execution plane **MUST** respetar el resource envelope vigente que le sea asignado por la política de recursos, limitando la concurrencia efectiva a dicho envelope.
2. Ninguna unidad de trabajo **MUST** comenzar ejecución sin haber sido admitida por el mecanismo de admisión dentro del resource envelope vigente.
3. Los límites de concurrencia **MUST** ser explícitos, configurables y verificables.
4. El agotamiento del resource envelope **MUST** producir un outcome operacional identificable, nunca un fallo silencioso ni una degradación no detectada.

> **Nota de transición:** Hasta que la Subfase 18.3 establezca la política de recursos, el resource envelope vigente será definido por el Execution Plan de la Subfase 18.1 como configuración inicial.

### 5.2 Admission Mechanism (C2 — dimensión de mecanismo)

5. El execution plane **MUST** proporcionar un mecanismo de admisión que determine si una unidad de trabajo puede ser aceptada para ejecución.
6. El mecanismo de admisión **MUST NOT** retener recursos para trabajo rechazado.
7. El mecanismo de admisión **MUST** ser distinguible de la política de admisión; el mecanismo define cómo entra/sale trabajo del execution plane, la política define cuándo debe admitirse trabajo según recursos, prioridad y presupuesto (responsabilidad de la Subfase 18.3).

### 5.3 Backpressure Mechanism (C3 — dimensión de mecanismo)

8. El execution plane **MUST** proporcionar un mecanismo de backpressure que propague la presión desde los consumidores hacia los productores de trabajo.
9. El mecanismo de backpressure **MUST** proporcionar bounded buffering o un mecanismo equivalente de propagación de presión que prevenga la acumulación no controlada de trabajo pendiente.
10. El mecanismo de backpressure **MUST** ser distinguible de la política de backpressure; el mecanismo define cómo se propaga la presión, la política define cuándo y cuánto limitar (responsabilidad de la Subfase 18.3).

### 5.4 Cancellation (C6)

11. Toda unidad de trabajo en vuelo **MUST** ser cancelable de forma cooperativa y oportuna.
12. La cancelación **MUST NOT** comprometer o publicar evidencia científica incompleta como evidencia canónica conforme a NADR-F18-01.
13. La cancelación **MUST** liberar los recursos asignados a la unidad de trabajo cancelada.
14. El mecanismo de cancelación **MUST** ser verificable: debe ser posible determinar si una unidad de trabajo fue completada, cancelada o fallida.
15. El shutdown del execution plane **MUST** proporcionar un mecanismo de terminación ordenada que cancele el trabajo en vuelo antes de terminar. La semántica de recuperación de estado persistente tras shutdown (leases, zombies, fencing) corresponde a la Subfase 18.2.

### 5.5 Concurrency Safety (C7)

16. El acceso concurrente a estado compartido del execution plane **MUST** ser seguro frente a condiciones de carrera.
17. Los primitivos de coordinación concurrente **MUST** ser explícitos y verificables.
18. El execution plane **MUST NOT** introducir deadlocks ni livelocks dentro del operational envelope declarado.
19. Toda superficie de coordinación concurrente **MUST** ser identificable y su comportamiento bajo cancelación y shutdown **MUST** ser demostrable.

### 5.6 Execution Context (DC-05)

20. Los límites del contexto de ejecución **MUST** ser explícitos y verificables.
21. El contexto de ejecución **MUST NOT** convertirse en un objeto que acumule responsabilidades sin frontera definida (god-object).
22. La estructura concreta del contexto de ejecución queda condicionada a la resolución de DC-01 y DC-05; este NADR no prescribe una estructura específica.

### 5.7 Minimal Operational Visibility (C11)

23. El execution plane **MUST** proporcionar visibilidad operacional mínima suficiente para gobernar bounded execution, backpressure, cancellation y concurrency safety.
24. El execution plane **MUST** exponer información suficiente para distinguir si una unidad de trabajo fue admitida, está en ejecución, fue completada, fue cancelada o falló. Esta exposición constituye una propiedad observable, no una nueva máquina de estados.
25. La visibilidad operacional **MUST** ser registrada como evidencia operacional separada de la evidencia científica conforme a NADR-F18-01.
26. La observabilidad profunda, forensía y reportes post-procesamiento **MUST NOT** ser introducidos como parte de esta capacidad; corresponden a Fase 20.

### 5.8 Scientific Neutrality of Execution

27. El modelo de ejecución concurrente **MUST NOT** alterar la identidad científica ni la evidencia científica canónica conforme a NADR-F18-01.
28. Las variaciones del modelo de ejecución **MUST** producir evidencia operacional separada, sin contaminar la evidencia científica.
29. El verification subject **MUST** respetar INV-VERIFICATION-ISOLATION conforme a ADR_F18_MASTER §5.1: ejecución sin scheduler ni concurrencia por defecto; concurrencia opt-in gobernada sujeta a INV-SCI-1.

### 5.9 Resolution of Execution Model (DC-01)

30. La selección del modelo concreto de concurrencia (async single-process + executors, multi-process, híbrido) **MUST** ser resuelta mediante DC-01 con evidencia cuantitativa previa.
31. La evidencia requerida para DC-01 **MUST** incluir, como mínimo: impacto cuantitativo de la barrera síncrona actual (GAP-0.1-01), métricas por etapa del pipeline (GAP-0.5-02), y evaluación del comportamiento de bounded execution y backpressure bajo carga.
32. Este NADR no prescribe un modelo de concurrencia específico; establece las reglas que cualquier modelo debe satisfacer.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El marco normativo para la ejecución concurrente bounded queda establecido normativamente. Su cumplimiento efectivo deberá ser demostrado por la implementación y la validación correspondientes.
* La resolución de DC-01 dispondrá de un conjunto de reglas verificables contra las cuales evaluar cualquier modelo de concurrencia candidato.
* La resolución de DC-05 dispondrá de reglas explícitas sobre límites de contexto de ejecución, evitando la acumulación de responsabilidades sin frontera.
* La Subfase 18.2 (journal semantics, DC-08) podrá condicionar su diseño al modelo de ejecución resuelto por DC-01.
* La Subfase 18.3 (admission policy, DC-10/DC-11) podrá construir la política de recursos sobre el mecanismo de admisión y backpressure aquí normado.
* La Subfase 18.5 (differential guard, DC-12) podrá verificar que el modelo de ejecución adoptado no altera la identidad científica conforme a NADR-F18-01.
* El verification subject queda protegido contra ejecución concurrente no gobernada conforme a INV-VERIFICATION-ISOLATION.
* La frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II queda reforzada como condición para la evaluación independiente del modelo de concurrencia; DF-06 será evaluado y eventualmente resuelto conforme al ADR_F18.1.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Propiedad verificable: el execution plane limita la concurrencia al resource envelope asignado.
  * Propiedad verificable: no existen primitivos de coordinación implícitos o no declarados.
  * Propiedad verificable: el mecanismo de admisión no retiene recursos para trabajo rechazado.
  * Propiedad verificable: el mecanismo de backpressure previene acumulación no controlada de trabajo pendiente.
  * Propiedad verificable: el mecanismo de cancelación libera recursos asignados.
  * Propiedad verificable: el contexto de ejecución tiene límites explícitos y no acumula responsabilidades sin frontera.
  * Propiedad verificable: ausencia de imports cruzados core→apps conforme a ENGINEERING_PRINCIPLES §II (verificación de DF-06).
  * Propiedad verificable: toda unidad de trabajo tiene un estado distinguible (admitida, en ejecución, completada, cancelada, fallida). El mecanismo concreto de exposición corresponde al Execution Plan, no a este NADR.

* **Validation (dinámica/comportamental):**
  * Propiedad validable: bajo carga superior a la capacidad del resource envelope, la concurrencia efectiva se mantiene acotada.
  * Propiedad validable: la presión introducida desde consumidores se propaga hacia productores sin acumulación no controlada.
  * Propiedad validable: la cancelación de unidades de trabajo en vuelo no compromete evidencia científica canónica ni deja recursos sin liberar.
  * Propiedad validable: el shutdown ordenado cancela todo trabajo en vuelo y libera recursos.
  * Propiedad validable: el acceso concurrente a estado compartido no introduce condiciones de carrera, deadlocks ni livelocks dentro del operational envelope declarado.
  * Propiedad validable: el mismo documento ejecutado bajo distintos modelos de ejecución produce evidencia científica canónica idéntica conforme a NADR-F18-01.
  * Propiedad validable: el verification subject se ejecuta sin scheduler ni concurrencia por defecto conforme a INV-VERIFICATION-ISOLATION.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F18_MASTER.md` FROZEN | Materializa las capacidades C1, C2, C3, C6, C7, C11 y las invariantes INV-SCI-1, INV-OPS-1, INV-VERIFICATION-ISOLATION declaradas en el ADR Maestro. |
| `ADR_F18.1` v1.0.2 FROZEN | Particulariza las decisiones DC-01 y DC-05 asignadas a la Subfase 18.1. Este NADR establece las reglas que DC-01 y DC-05 deben satisfacer al resolverse. |
| `NADR-F18-01` v1.0.3 FROZEN | **Dependencia directa:** Este NADR depende de la frontera de identidad establecida por NADR-F18-01. Toda regla de neutralidad científica (§5.8) referencia la frontera de NADR-F18-01. |
| `ENGINEERING_PRINCIPLES.md` | **Dependencia de autoridad:** La frontera hexagonal (Sección II) es establecida por los principios de ingeniería; este NADR no la redefine. DF-06 es una manifestación concreta que debe ser evaluada conforme al ADR_F18.1. |
| `NADR-F18-03` (pendiente, Subfase 18.2) | **Influencia:** El journal semantics y la recuperación durable (DC-08) quedan condicionados al modelo de ejecución resuelto por DC-01 bajo las reglas de este NADR. |
| `ADR_F18.3` (pendiente, Subfase 18.3) | **Influencia:** La política de admisión (DC-10), la política de backpressure y la semántica de admisión diferida (DC-11) se construyen sobre el mecanismo aquí normado. Este NADR gobierna el mecanismo; 18.3 gobierna la política. |
| `DC-12` / `ADR_F18.5` (pendiente, Subfase 18.5) | **Influencia:** El differential guard verificará que el modelo de ejecución adoptado no altera la identidad científica conforme a NADR-F18-01 y a las reglas §5.8 de este NADR. |
| `PHASE_18.1_EXECUTION_PLAN.md` (pendiente) | Materializa las tareas que implementan estas reglas normativas y define el DoD operativo. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la frontera entre scientific identity, execution identity y operational state (responsabilidad de `NADR-F18-01`).
* **No gobierna** la selección del modelo concreto de concurrencia (responsabilidad de DC-01, Subfase 18.1, con evidencia cuantitativa).
* **No gobierna** la estructura concreta del contexto de ejecución (responsabilidad de DC-05, Subfase 18.1, condicionado a DC-01).
* **No gobierna** admission policy, fairness, resource budgets, priority ni batching adaptativo (responsabilidad de la Subfase 18.3, DC-07/DC-10/DC-11).
* **No gobierna** journal semantics, durable recovery, fencing, zombie handling ni persistencia de estado (responsabilidad de la Subfase 18.2, DC-08).
* **No gobierna** la semántica de recuperación de estado persistente tras shutdown (responsabilidad de la Subfase 18.2).
* **No gobierna** provider characterization ni cache semantics (responsabilidad de la Subfase 18.4, DC-03/DC-04).
* **No gobierna** el guard diferencial ni la promoción a CI (responsabilidad de la Subfase 18.5, DC-12).
* **No gobierna** observabilidad profunda, forensía ni reportes post-procesamiento (responsabilidad de Fase 20).
* **No gobierna** la baseline científica ni los parámetros científicos congelados (responsabilidad de la Fase 17-BIS y su proceso de recalibración).
* **No redefine** la frontera hexagonal establecida en ENGINEERING_PRINCIPLES §II. DF-06 es un hallazgo concreto cuya evaluación y eventual resolución corresponde al ADR_F18.1 y al Execution Plan.
* **No establece** arquitectura distribuida ni pretende ser abstracción para multi-node (ROADMAP v3.0 §I y §V).
* **No prescribe** tareas de implementación, Definition of Done ni secuencia operativa (responsabilidad del `PHASE_18.1_EXECUTION_PLAN.md`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias que materializan el marco de ejecución concurrente bounded del execution plane local. No resuelve DC-01 ni DC-05; establece las reglas que cualquier modelo de ejecución debe satisfacer. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.