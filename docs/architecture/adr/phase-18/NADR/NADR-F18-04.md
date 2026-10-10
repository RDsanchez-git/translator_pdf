# NADR-F18-04: Persistencia Recuperable e Idempotencia de Aplicación Local

## 1. METADATA

* **Decision ID:** `NADR-F18-04`
* **Título:** Persistencia Recuperable e Idempotencia de Aplicación Local
* **Clase de Decisión:** `DATA / OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.1.1
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Subfase 18.2 — Durable Execution & Recovery
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Staff Engineering / Execution Plane Team
* **Capacidad Arquitectónica:** CAP-18-04 (Persistencia Recuperable e Idempotencia de Aplicación Local) — Garantizar que las decisiones y resultados locales necesarios para recuperar una ejecución sobrevivan a los fallos incluidos en el contrato, manteniendo aplicación idempotente y coherencia entre autoridad, journal y proyecciones.
* **Evidencia Forense:**
  * `GAP-18.2.2-03` (P2): Incertidumbre de durabilidad frente al modelo de fallos requerido
  * `GAP-18.2.2-05` (P2): Cobertura de validación incompleta para escenarios críticos
  * `E-18.2.2-009` (P2): append_wal idempotente con ON CONFLICT DO NOTHING
  * `E-18.2.2-010` (P2): upsert_projection idempotente con version check monotónico
  * `E-18.2.2-011` (P2): Reconciliation commands idempotentes por reconciliation_id
  * `E-18.2.2-012` (P2): FSM transitions con CAS (Compare-And-Swap)
  * `E-18.2.2-014` (P2): WAL + NORMAL + busy_timeout en bootstrap
  * `E-18.2.2-015` (P2): Mismos PRAGMAs en connection factory
  * `E-18.2.2-016` (P2): synchronous=FULL ausente en código auditado
  * `E-18.2.2-021` (P2): fsync solo para corpus/AST, no para execution plane
  * `E-18.2.2-027` (P2): Solo UN escenario de chaos (game_day_1)
  * `E-18.2.2-028` (P2): game_day_1 ejecuta kill real pero no prueba efecto incierto
  * `E-18.2.2-036` (P2): test_fencing.py vacío (0 bytes)
  * `E-18.2.2-037` (P2): Sin tests automatizados para power loss, SIGKILL, fencing frontera externa
* **Referencias Cruzadas:**
  * **Depende de:**
    * `ADR_F18_MASTER` (INV-JOURNAL §5.1, DC-08 §8.2)
    * `ADR_F18.2` v3.3.0 FROZEN (DC-08d RATIFICACIÓN CONDICIONADA, §8.1 Modelo de fallos, §8.2 Consecuencias honestas de write-policy)
    * `NADR-F18-01` v1.0.3 FROZEN (Execution Identity & Scientific Isolation)
    * `NADR-F18-02` v1.0.1 FROZEN (Bounded Concurrent Execution, §5.4 R15)
    * `NADR-F18-03` v1.2.0 FROZEN (Autoridad de Ejecución y Resolución de Efectos Inciertos, §5.2 Clasificación semántica, R7)
    * `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN (distinción identidad científica vs identidad de intento)
  * **Influencia prevista:**
    * `NADR-F18-05` (pendiente): recibirá responsabilidad de observabilidad de duplicación; este NADR provee la base de persistencia idempotente sobre la cual NADR-05 medirá
    * `PHASE_18.2_EXECUTION_PLAN` (pendiente): definirá tareas de materialización, umbrales operativos y validaciones empíricas
  * **Conflictúa con:** Ninguno identificado
  * **Reemplaza a:** N/A (primer NADR que gobierna esta capacidad)

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 4/5 — Sin persistencia recuperable gobernada, el estado local (autoridad de ejecución, resultados confirmados, proyecciones materializadas) se pierde o corrompe ante fallos incluidos en el modelo, impidiendo la recuperación coherente.
* **Mantenibilidad:** 3/5 — La coherencia entre planos (control, event, materialized) requiere disciplina normativa sostenida; sin reglas explícitas, la evolución del sistema puede introducir inconsistencias recuperables.
* **Recuperabilidad:** 5/5 — Este NADR gobierna directamente la capacidad de recuperar el estado local de forma coherente tras fallos. Sin él, el sistema no puede garantizar que el trabajo completado sobreviva a interrupciones.
* **Seguridad:** 2/5 — No es un vector de ataque directo, pero la corrupción de estado local podría comprometer la integridad del pipeline si no se gobierna adecuadamente.
* **Financiero:** 3/5 — La pérdida de estado local puede requerir re-trabajo (re-ejecución de efectos externos), pero el impacto FinOps principal está gobernado por NADR-F18-03 (duplicación de efectos externos).
* **Total Score: 17/25**

**Severidad:** `S1` (Crítico)

**Justificación de la severidad:** Se clasifica como Crítico (S1) conforme al template metodológico (rango 16-25). Este NADR gobierna la capacidad de persistencia recuperable e idempotencia de aplicación local, cuya ausencia compromete la integridad del estado del sistema ante fallos incluidos en el modelo de fallos aprobado. La recuperabilidad se puntúa en 5/5 porque este es el NADR central que gobierna la recuperación del estado local; sin él, el sistema no puede garantizar que el trabajo completado sobreviva a interrupciones.

---

## 3. DECISIÓN EJECUTIVA

**Todo resultado local confirmado y toda autoridad de ejecución deben persistir de forma recuperable conforme a la política de durabilidad aprobada, y la aplicación de dichos resultados debe ser idempotente de modo que reaplicaciones o recuperaciones tras fallos parciales no produzcan efectos duplicados o inconsistentes.**

En consecuencia:

* Queda requerida la durabilidad del estado local para los escenarios incluidos en el modelo de fallos aprobado, bajo la política inicial SQLite WAL + synchronous=NORMAL.
* Queda prohibida la aplicación duplicada o inconsistente de un mismo resultado confirmado, incluso tras interrupciones entre el registro del evento y la materialización de la proyección.
* Queda requerida la coherencia recuperable entre autoridad local, registro de eventos y proyecciones materializadas, tratando estas últimas como derivadas reconstruibles.
* Queda explícito que las garantías de durabilidad se limitan a los escenarios incluidos en el modelo de fallos aprobado y no se extienden implícitamente a escenarios excluidos (power loss, fallo físico).

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de persistir recuperablemente el estado local y de aplicar idempotentemente los resultados confirmados está presente en el execution plane actual, pero no gobernada normativamente de forma explícita.

Existen mecanismos observados que contribuyen a la atomicidad de determinadas operaciones, la persistencia local, la idempotencia de escrituras y la recuperación. Sin embargo, su suficiencia integral frente al modelo de fallos aprobado permanece pendiente de validación, y la ausencia de reglas normativas abstractas que las preserven ante la evolución del sistema introduce riesgos de inconsistencia.

Esta ausencia de gobernanza normativa introduce las siguientes clases de defectos:

1. **Ausencia de reglas normativas explícitas de persistencia recuperable:** Los mecanismos de persistencia existen, pero no hay reglas que gobiernen qué propiedades deben satisfacer para los escenarios incluidos en el modelo de fallos aprobado, ni que limiten explícitamente las garantías a esos escenarios.

2. **Ausencia de contrato de convergencia post-fallo parcial:** No existe una regla que gobierne explícitamente qué ocurre si el journal registra un resultado pero el proceso falla antes de actualizar la proyección o reconocer la tarea como completada, dejando la recuperación dependiente de implementaciones ad-hoc.

3. **Ausencia de reglas normativas explícitas de coherencia entre planos:** Los tres planos (control, event, materialized) existen, pero no hay reglas que gobiernen la coherencia recuperable entre ellos tras una interrupción, ni que exijan que las proyecciones materializadas sean reconstruibles a partir de sus fuentes autoritativas.

4. **Ausencia de separación explícita de propiedades:** Las propiedades de atomicidad, durabilidad, idempotencia y recuperabilidad están presentes en la implementación de forma aislada, pero no hay reglas que exijan declararlas y verificarlas por separado, lo cual puede llevar a confundir una propiedad con otra.

### 4.2 Manifestación concreta identificada por la auditoría

* **`GAP-18.2.2-03` (P2 — Medio):** Incertidumbre de durabilidad frente al modelo de fallos requerido. La configuración observada es WAL + synchronous=NORMAL. No se encontró synchronous=FULL ni llamadas explícitas a fsync en el execution plane. La semántica documentada de SQLite es EVIDENCIA DOCUMENTAL. El comportamiento empírico ante power loss NO está DEMOSTRADO.

* **`GAP-18.2.2-05` (P2 — Medio):** Cobertura de validación incompleta. game_day_1 ejecuta kill real (SIGKILL vía Docker) pero NO prueba el caso crítico de crash post-effect/pre-journal con efecto realmente ocurrido en el proveedor. test_fencing.py vacío (0 bytes).

* **`E-18.2.2-009` a `E-18.2.2-012` (P2 — Medio):** Mecanismos observados de idempotencia local: append_wal con ON CONFLICT DO NOTHING, upsert_projection con version check monotónico, reconciliation commands con processed_reconciliation_commands, FSM transitions con CAS. Estas evidencias demuestran que la idempotencia local es factible con los mecanismos existentes.

* **`E-18.2.2-014` a `E-18.2.2-016` (P2 — Medio):** Configuración y semántica documental de SQLite. WAL + NORMAL + busy_timeout=30000 observados en bootstrap y connection factory. synchronous=FULL ausente.

* **`E-18.2.2-021` (P2 — Medio):** fsync solo para corpus/AST, no para execution plane. Los 4 planos de ejecución (Event, Materialized, FSM, Queue) NO usan fsync explícito.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Durabilidad y Política de Persistencia

1. Toda autoridad de ejecución y todo resultado confirmado localmente **MUST** persistir en almacenamiento recuperable conforme al modelo de fallos aprobado en `ADR_F18.2 §8.1`.
2. Un resultado local **MUST NOT** considerarse confirmado durablemente hasta que su fuente autoritativa haya completado satisfactoriamente el contrato de confirmación de persistencia aplicable. La recepción de una respuesta externa, una escritura iniciada o una actualización de proyección no constituyen, por sí solas, confirmación durable.
3. La persistencia del execution plane **MUST** respetar la política inicial SQLite `WAL` + `synchronous=NORMAL` + `busy_timeout` aprobada en `ADR_F18.2 §3.1/§8.2`. Cualquier modificación de esta política **MUST** seguir la gobernanza de cambios correspondiente y **MUST NOT** introducir garantías de durabilidad no demostradas.
4. Las garantías de durabilidad aplican exclusivamente a los escenarios incluidos en el modelo de fallos aprobado y **MUST NOT** extenderse implícitamente a escenarios excluidos (pérdida de energía, fallo físico del almacenamiento).

### 5.2 Idempotencia de Aplicación Local

5. La reaplicación de un mismo resultado confirmado **MUST** ser idempotente y no producir efectos locales duplicados o inconsistentes.
6. Para una misma identidad lógica y versión de resultado, la aplicación repetida **MUST** preservar un estado equivalente. Una versión igual con contenido incompatible **MUST NOT** sobrescribir silenciosamente un resultado previamente confirmado.
7. Las escrituras producidas por una autoridad obsoleta **MUST NOT** sobrescribir resultados pertenecientes a una autoridad vigente, garantizado mediante mecanismos de control de concurrencia (versionado, bloqueo optimista u otros) que prevengan la corrupción del estado local.

### 5.3 Coherencia y Recuperación entre Planos

8. Tras toda recuperación, la coherencia entre autoridad local, registro de eventos y proyecciones materializadas **MUST** verificarse conforme a las reglas de reconciliación aprobadas.
9. Toda proyección materializada que represente resultados confirmados **MUST** ser reconstruible de forma determinista a partir de sus fuentes locales autoritativas recuperables. Cuando el event journal sea la fuente autoritativa del resultado, **MUST** contener o referenciar de forma recuperable la información suficiente para reconstruir dicha proyección.
10. Cuando un resultado haya alcanzado confirmación durable en su fuente local autoritativa, cualquier interrupción posterior **MUST** permitir completar o reconstruir idempotentemente las transiciones locales derivadas pendientes, sin requerir una nueva ejecución externa por la sola ausencia de materialización o reconocimiento final.

### 5.4 Separación de Propiedades

11. Las garantías de atomicidad, durabilidad, idempotencia y recuperabilidad **MUST** declararse y verificarse por separado.
12. La atomicidad de una transición local **MUST NOT** interpretarse como garantía de durabilidad ante fallos.
13. La durabilidad ante fallos **MUST NOT** interpretarse como garantía de idempotencia de aplicación.
14. La idempotencia de aplicación local **MUST NOT** interpretarse como garantía de recuperación coherente entre planos.

### 5.5 Compatibilidad con NADR-F18-03

15. La recuperación del estado local **MUST** respetar la clasificación semántica de resultados establecida en `NADR-F18-03 §5.2`.
16. La ausencia de confirmación local de un resultado **MUST NOT** interpretarse como prueba de ausencia de efecto externo, conforme a `NADR-F18-03 R7`.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

Una vez materializadas y validadas las reglas de este NADR:

* **Durabilidad del estado local:** La autoridad de ejecución y los resultados confirmados localmente sobrevivirán a los fallos incluidos en el modelo de fallos aprobado, permitiendo la recuperación coherente del trabajo completado bajo la política WAL+NORMAL.

* **Convergencia idempotente post-fallo parcial:** Quedará garantizado que, si el journal registra un resultado pero el proceso falla antes de actualizar la proyección, el sistema podrá completar o reconstruir idempotentemente las transiciones locales derivadas sin requerir una nueva ejecución externa.

* **Reconstruibilidad de proyecciones:** Las proyecciones materializadas serán tratadas como derivadas reconstruibles a partir de sus fuentes autoritativas (principalmente el event journal), eliminando la dependencia de que estén siempre sincronizadas en tiempo real con el journal.

* **Separación explícita de propiedades:** Las garantías de atomicidad, durabilidad, idempotencia y recuperabilidad serán declaradas y verificadas por separado, evitando confusiones entre propiedades distintas (ej: no asumir que idempotencia implica recuperabilidad).

* **Compatibilidad con semántica de NADR-F18-03:** La recuperación del estado local respetará la clasificación semántica de resultados establecida en NADR-F18-03, y la ausencia de confirmación local no se interpretará como prueba de ausencia de efecto externo.

* **Límites explícitos de durabilidad:** Las garantías de durabilidad se limitarán explícitamente a los escenarios incluidos en el modelo de fallos aprobado, sin extenderse implícitamente a escenarios excluidos (power loss, fallo físico del almacenamiento).

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Análisis estático de contratos de persistencia que verifique que toda autoridad de ejecución y todo resultado confirmado localmente persisten en almacenamiento recuperable.
  * Verificación de dependencias arquitectónicas mediante import-linter u otro mecanismo equivalente, cuando corresponda, para comprobar que los componentes implementados respetan las fronteras de los planos de control, eventos y materialización y los contratos de dependencia aprobados.
  * Análisis estático de flujo de control que verifique la separación de tipos y la ausencia de dependencias cíclicas entre los planos de control, evento y materialización.
  * Verificación de contratos de persistencia y recuperación que demuestre que la información recuperable permite aplicar la clasificación semántica de NADR-F18-03, sin imponer una representación física específica de estados, tablas o enums.

* **Validation (dinámica/comportamental):**
  * Pruebas de propiedad (property tests) que verifiquen que la reaplicación de un mismo resultado confirmado (misma identidad y versión) no produce efectos locales duplicados o inconsistentes, incluso bajo concurrencia.
  * Chaos harness con inyección de crash en escenarios incluidos en el modelo de fallos aprobado (ej: entre journal y proyección), verificando que el estado local se recupera de forma coherente y reconstruye las proyecciones pendientes sin re-ejecución externa.
  * Pruebas de no sobrescritura por autoridad obsoleta que verifiquen que las escrituras producidas por una autoridad vencida son rechazadas por los mecanismos de control de concurrencia (ej: CAS o version check).
  * Pruebas de separación de propiedades que verifiquen que atomicidad, durabilidad, idempotencia y recuperabilidad se declaran y validan mediante mecanismos independientes.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F18_MASTER` v1.0.0 FROZEN | **Materializa:** DC-08d (durabilidad) y propiedad idempotent apply de INV-JOURNAL §5.1. Este NADR desarrolla las decisiones arquitectónicas del Maestro sin redefinir los invariantes congelados. |
| `ADR_F18.2` v3.3.0 FROZEN | **Materializa:** DC-08d RATIFICACIÓN CONDICIONADA (modelo de fallos y write-policy), §8.1 Modelo de fallos aprobado, §8.2 Consecuencias honestas de write-policy. Este NADR proporciona las reglas normativas obligatorias que materializan las decisiones del ADR. |
| `NADR-F18-01` v1.0.3 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de identidad científica definidos en NADR-F18-01. La distinción entre identidad de intento e identidad científica es condición de compatibilidad. |
| `NADR-F18-02` v1.0.1 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de ejecución bounded definidos en NADR-F18-02, incluido el límite de modificación señalado en §5.4 R15. |
| `NADR-F18-03` v1.2.0 FROZEN | **Dependencia directa:** Este NADR respeta la clasificación semántica de resultados establecida en NADR-F18-03 §5.2. La regla R16 de este NADR es compatible con R7 de NADR-F18-03 (ausencia de confirmación local no implica ausencia de efecto externo). |
| `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN | **Dependencia directa:** Este NADR preserva la distinción entre identidad científica (hash determinista) e identidad de intento (autoridad de ejecución) definida en el contrato congelado. |
| `NADR-F18-05` (pendiente) | **Influencia prevista:** Este NADR provee la base de persistencia idempotente sobre la cual NADR-F18-05 medirá la observabilidad de duplicación. La contabilización de reejecuciones excepcionales depende de la persistencia idempotente gobernada por este NADR. |
| `PHASE_18.2_EXECUTION_PLAN` (pendiente) | **Materializa:** Las tareas del Execution Plan implementan las reglas de este NADR. Los umbrales operativos concretos, las validaciones empíricas y los métodos de verificación se definen en el Execution Plan, no en este NADR. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la autoridad de ejecución pre-efecto ni la clasificación semántica de resultados (confirmado, no iniciado, incierto) (responsabilidad de `NADR-F18-03`).
* **No gobierna** la política de recuperación bajo incertidumbre ni la prohibición de reejecución automática de efectos inciertos (responsabilidad de `NADR-F18-03`).
* **No gobierna** la observabilidad de intentos, exposición a duplicación y medición de tasas de reejecución (responsabilidad prevista de `NADR-F18-05`).
* **No prescribe** implementaciones técnicas particulares (nombres de clases, archivos, funciones, migraciones de esquema o secuencia de cambios), aunque sí materializa la política de persistencia aprobada por el ADR superior.
* **No prescribe** Definition of Done ni criterios de aceptación operativa (responsabilidad del `PHASE_18.2_EXECUTION_PLAN`).
* **No gobierna** los diferimientos formales condicionados DF-24 (CircuitBreaker) y DF-34 (ProfileStore); estos mantienen su trazabilidad propia conforme a `ADR_F18.2` §8.3 y quedan pendientes de resolución cuando se cumplan sus triggers.
* **No modifica** los contratos congelados de la Subfase 18.1 (responsabilidad de `NADR-F18-01` y `NADR-F18-02`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias que gobiernan la capacidad de persistencia recuperable e idempotencia de aplicación local. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el `PHASE_18.2_EXECUTION_PLAN` correspondiente. Las dependencias de NADR-F18-05 son influencias previstas; sus contratos normativos específicos se establecerán cuando ese documento sea emitido.