# NADR-F17BIS-08: Distributed Execution Plane & CQRS Lineage Integrity

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-08`
* **Título:** Distributed Execution Plane & CQRS Lineage Integrity
* **Clase de Decisión:** `STRUCTURAL` / `OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Runtime Domain / FinOps Domain
* **Capacidades Arquitectónicas:** CAP-003 (Event-Sourced CQRS Integrity), CAP-007 (Budgeting & Token Estimation), CAP-008 (Unified Execution Plane)
* **Evidencia Forense:** `P4-01`, `P4-02`, `P4-03`, `P7-H01`, `P7-H02`, `P7-H06`, `GAP-P4-01`, `GAP-P4-03`, `GAP-P7-02`, `GAP-P7-03`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-03` (la firma documental es precondición del linaje CQRS), `NADR-F17BIS-11` (la Composition Root gobierna la inyección de este plano).
  * **Influencia:** `NADR-F17BIS-07` (la curación opera dentro del plano de ejecución), `NADR-F17BIS-09` (la integridad FSM depende del linaje CQRS correcto).
  * **Conflictúa con:** Toda coordinación de estado operativo que resida fuera del plano de ejecución.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S1)
* **Operacional:** 5 — La incapacidad de coordinar cuotas entre instancias del plano de ejecución multiplica el tráfico hacia proveedores externos, provocando bloqueos masivos por rebasamiento.
* **Mantenibilidad:** 4 — La ausencia de puertos abstractos acopla la lógica de coordinación a un backend concreto, impidiendo la evolución independiente.
* **Recuperabilidad:** 5 — La corrupción del linaje CQRS estanca documentos indefinidamente en estados intermedios, imposibilitando la recuperación automática.
* **Seguridad:** 2
* **Financiero:** 4 — La descoordinación de cuotas fuerza re-ejecuciones innecesarias y desperdicio de tokens.
* **Total Score: 20/25**

---

## 3. DECISIÓN EJECUTIVA

**El plano de ejecución constituye la única autoridad responsable de coordinar el estado operativo distribuido del sistema.**

El plano de ejecución distribuido debe gobernar la coordinación de cuotas, la resiliencia de circuitos y la integridad del linaje CQRS mediante puertos abstractos inyectables desde la Composition Root.

En consecuencia:
* La coordinación de cuotas debe operar a través de un puerto abstracto desacoplado del backend de persistencia.
* El mecanismo canónico de circuit breaking debe estar activo en el plano de ejecución, interceptando todas las llamadas a proveedores externos.
* La rematerialización CQRS debe transportar la identidad documental completa, preservando el linaje criptográfico.
* La reconciliación CQRS debe estar activa y gobernada por configuración externa.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

El plano de ejecución presenta cuatro fracturas estructurales que comprometen la coordinación distribuida, la resiliencia operacional y la integridad del linaje:

1. **Estado de coordinación local al proceso.** El mecanismo de coordinación de cuotas mantiene estado exclusivamente local al proceso, imposibilitando la coordinación distribuida entre múltiples instancias del plano de ejecución.

2. **Resiliencia de circuitos inactiva.** El mecanismo canónico de circuit breaking existe en el dominio pero no está integrado en el plano de ejecución. Ante fallos consecutivos de proveedores externos, el sistema carece de un mecanismo fail-fast para interrumpir el flujo.

3. **Dualidad de modos de ejecución.** Coexisten dos modos de ejecución desalineados: uno síncrono en proceso que no atraviesa el plano transaccional CQRS, y otro distribuido que sí lo hace. El dominio no puede garantizar comportamiento uniforme.

4. **Corrupción del linaje CQRS.** La rematerialización de proyecciones desde el Event Log inyecta identidades no derivadas del documento, corrompiendo el Query Model y estancando documentos indefinidamente.

### 4.2 Manifestación concreta identificada por la auditoría

* **`P4-03` / `GAP-P4-03` (P0):** El mecanismo de coordinación de cuotas (`TokenBucket`, `QuotaManager` en `apps/llm_workers/rate_limiter.py`) mantiene contadores y marcas de tiempo en variables locales de memoria RAM. En despliegues multi-instancia, las cuotas no se comparten, multiplicando el tráfico hacia las APIs por el número de instancias concurrentes.

* **`P4-01` / `GAP-P4-01` (P0):** `GlobalCircuitBreaker` (`core/resilience/circuit_breaker.py`) implementa una máquina de estados determinista (`CLOSED`, `OPEN`, `HALF_OPEN`) con poda de ventanas deslizantes. El grafo estático AST confirma que ningún punto de entrada, fábrica ni despachador lo instancia o invoca.

* **`P4-02` (P0):** El modo CLI ejecuta despacho in-process mediante semáforos en memoria sin atravesar la cola transaccional CQRS. El modo daemon sí consume la cola `ControlPlaneRepository`. El dominio no puede garantizar paridad de comportamiento.

* **`P7-H06` / `GAP-P7-02` (P0):** `ReconciliationCommandHandler.handle_rematerialize()` inyecta la cadena literal `"unknown_ast_hash"` al invocar `upsert_projection()`, porque `RematerializeTaskCommand` carece del atributo de identidad documental. Las proyecciones rematerializadas jamás coinciden con la consulta del ensamblador.

* **`P7-H02` / `GAP-P7-03` (P0):** `CQRSReconciliationDaemon.run_reconciliation_cycle()` tiene la bandera hardcodeada `EXPERIMENTAL_ENABLED = False`. El daemon retorna inmediatamente sin procesar tareas expiradas.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Coordinación distribuida de cuotas
1. **MUST** existir un puerto abstracto de coordinación de cuotas desacoplado del backend de persistencia.
2. El puerto **MUST** definir operaciones atómicas de reserva, consulta y liberación de cuotas.
3. **MUST NOT** existir estado de coordinación de cuotas residente exclusivamente en la memoria local de un proceso.
4. La selección del backend de persistencia **MUST** realizarse exclusivamente desde la Composition Root.

### 5.2 Resiliencia de circuitos
5. El mecanismo canónico de circuit breaking **MUST** estar integrado en el plano de ejecución, interceptando todas las llamadas a proveedores externos.
6. El circuito **MUST** abrirse determinísticamente tras un número configurable de fallos consecutivos dentro de una ventana de tiempo deslizante.
7. **MUST NOT** existir ninguna ruta de despacho hacia proveedores externos que eluda el mecanismo de circuit breaking.

### 5.3 Integridad del linaje CQRS
8. Todo comando de rematerialización **MUST** transportar la identidad documental completa necesaria para preservar el linaje CQRS.
9. **MUST NOT** existir rutas de escritura hacia el Query Model que utilicen identidades no derivadas del documento real.
10. La rematerialización **MUST** producir proyecciones recuperables por las consultas del ensamblador.

### 5.4 Reconciliación activa
11. El mecanismo de reconciliación CQRS **MUST** estar activo en producción.
12. El mecanismo de reconciliación **MUST** estar gobernado por configuración externa.
13. **MUST NOT** existir banderas de código que desactiven la reconciliación de forma hardcodeada.

### 5.5 Composición de mecanismos
14. La coordinación de cuotas y el mecanismo de circuit breaking **MUST** operar de forma compuesta dentro del plano de ejecución.
15. La apertura del circuito **MUST** prevenir el consumo de cuotas durante el periodo de enfriamiento.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El plano de ejecución adquiere independencia del modelo de despliegue, permitiendo desde ejecución local hasta topologías distribuidas sin alterar la lógica del dominio.
* La resiliencia de circuitos protege al sistema contra fallos en cascada de proveedores externos, interrumpiendo el flujo ante errores consecutivos.
* La integridad del linaje CQRS queda garantizada, eliminando la corrupción del Query Model y permitiendo la recuperación automática de documentos estancados.
* La reconciliación activa libera tareas huérfanas y sana proyecciones inconsistentes de forma continua.
* La coordinación de cuotas deviene escalable, permitiendo que múltiples instancias del plano de ejecución operen sin sobrepasar los límites contractuales de los proveedores.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que no existen rutas de escritura hacia el Query Model que utilicen identidades no derivadas del documento.
  * Verificación de que el mecanismo de circuit breaking está integrado en el plano de ejecución.
  * Verificación de que no existen banderas de código que desactiven la reconciliación.
  * Verificación de que el puerto de coordinación de cuotas está desacoplado del backend concreto.

* **Validation (dinámica/comportamental):**
  * Múltiples instancias concurrentes **MUST** coordinar el consumo de cuotas sin sobrepasar la capacidad global.
  * Ante fallos consecutivos de un proveedor externo, el circuito **MUST** abrirse y rechazar peticiones subsiguientes.
  * La rematerialización de proyecciones **MUST** producir registros recuperables por las consultas del ensamblador.
  * El mecanismo de reconciliación **MUST** liberar tareas huérfanas y sanar proyecciones inconsistentes.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa los principios constitucionales de Event Sourcing & CQRS Strictness y FSM State Machine Exclusivity. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-03` | **Dependencia directa:** la identidad semántica del documento es precondición del linaje CQRS correcto. |
| `NADR-F17BIS-11` | **Dependencia directa:** la Composition Root gobierna la inyección del plano de ejecución. |
| `NADR-F17BIS-07` | **Influencia:** la curación opera dentro del plano de ejecución gobernado por este NADR. |
| `NADR-F17BIS-09` | **Influencia:** la integridad FSM depende del linaje CQRS correcto. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `3.3.1`, `3.3.2` y `3.3.3` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la implementación concreta del backend de coordinación distribuida.
* **No gobierna** la máquina de estados FSM ni los comandos de transición de estado (responsabilidad de `NADR-F17BIS-09`).
* **No gobierna** el Event Log ni el formato de la WAL (responsabilidad de `NADR-F17BIS-09`).
* **No gobierna** las estrategias de curación post-validación (responsabilidad de `NADR-F17BIS-07`).
* **No gobierna** la Composition Root ni el mecanismo de inyección de dependencias (responsabilidad de `NADR-F17BIS-11`).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.