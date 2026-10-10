# NADR-F18-03: Autoridad de Ejecución y Resolución de Efectos Inciertos

## 1. METADATA

* **Decision ID:** `NADR-F18-03`
* **Título:** Autoridad de Ejecución y Resolución de Efectos Inciertos
* **Clase de Decisión:** `OPERATIONAL / DATA`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.1.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Subfase 18.2 — Durable Execution & Recovery
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Staff Engineering / Execution Plane Team
* **Capacidad Arquitectónica:** CAP-18-03 (Autoridad de Ejecución y Resolución de Efectos Inciertos) — Conservar autoridad recuperable antes de ejecutar efectos externos y definir la semántica de recuperación cuando se desconoce si esos efectos ocurrieron.
* **Evidencia Forense:**
  * `GAP-18.2.2-01` (P1): Ausencia de semántica de recuperación para efectos externos inciertos
  * `GAP-18.2.2-02` (P2): Capacidades de idempotencia del proveedor no verificadas
  * `E-18.2.2-001` (P2): Verificación de lease POST-EFFECT; el lease persistido antes de la llamada constituye mecanismo observado de intención pre-efecto
  * `E-18.2.2-002` (P2): Heartbeat asíncrono no detiene ejecución; el lease persistido antes del efecto externo es recuperable bajo crash dentro del modelo de fallos aprobado
  * `E-18.2.2-004` (P2): Código cliente sin mecanismos de external-effect fencing
  * `E-18.2.2-005` (P2): Ventana execute→append_wal sin transacción
  * `E-18.2.2-007` (P1): Event journal sin estados pre-efecto; el lease persistido en control plane cumple rol de intención durable, pero la ausencia de representación pre-efecto en event plane impide que el reconciler disponga de información suficiente para distinguir todas las situaciones de recuperación
  * `E-18.2.2-008` (P1): Ausencia de lógica de verificación con proveedor
  * `E-18.2.2-013` (P2): Código cliente sin idempotencia en frontera LLM
* **Referencias Cruzadas:**
  * **Depende de:**
    * `ADR_F18_MASTER` (INV-JOURNAL §5.1, DC-08 §8.2)
    * `ADR_F18.2` v3.3.0 FROZEN (DC-08a RATIFICADO, DC-08b RATIFICADO CON ENMIENDA, §3.2 Política de recuperación bajo incertidumbre)
    * `NADR-F18-01` v1.0.3 FROZEN (Execution Identity & Scientific Isolation)
    * `NADR-F18-02` v1.0.1 FROZEN (Bounded Concurrent Execution, §5.4 R15)
    * `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN (distinción identidad científica vs identidad de intento)
  * **Influencia prevista:**
    * `NADR-F18-04` (pendiente): recibirá responsabilidad de persistencia local de trazabilidad de operaciones inciertas
    * `NADR-F18-05` (pendiente): recibirá responsabilidad de semántica de medición y contadores de reejecución
    * `PHASE_18.2_EXECUTION_PLAN` (pendiente): definirá tareas de materialización y umbrales operativos
  * **Conflictúa con:** Reejecución automática no autorizada de efectos externos inciertos; tratamiento equivalente de "efecto no iniciado" y "efecto iniciado pero no registrado"
  * **Reemplaza a:** N/A (primer NADR que gobierna esta capacidad)

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 4/5 — Sin gobierno de autoridad y efectos inciertos, el sistema puede reejecutar ciegamente operaciones externas completadas, generando duplicación de costes FinOps y corrupción de estado.
* **Mantenibilidad:** 3/5 — La ausencia de políticas explícitas de recuperación bajo incertidumbre dificulta la evolución del sistema y la incorporación de nuevos proveedores externos.
* **Recuperabilidad:** 4/5 — Este NADR gobierna directamente la capacidad de recuperación segura y gobernada ante efectos externos inciertos. Sin él, el sistema carece de semántica explícita para distinguir operaciones elegibles de reejecución de operaciones que requieren resolución controlada.
* **Seguridad:** 3/5 — La falta de fencing de efectos externos puede permitir que workers obsoletos produzcan efectos no autorizados en proveedores remotos.
* **Financiero:** 4/5 — La duplicación de efectos externos tiene impacto directo en costes de tokens LLM. Sin trazabilidad y escalamiento, el riesgo FinOps no es acotado.
* **Total Score: 18/25**

**Severidad:** `S1` (Crítico)

**Justificación de la severidad:** Se clasifica como Crítico (S1) conforme al template metodológico (rango 16-25). El NADR gobierna la capacidad de recuperación segura ante efectos externos inciertos, cuya ausencia permite duplicación no controlada de costes FinOps y carece de semántica explícita para distinguir operaciones elegibles de reejecución de operaciones que requieren resolución controlada.

---

## 3. DECISIÓN EJECUTIVA

**Toda ejecución de efecto externo debe estar respaldada por una autoridad recuperable persistida antes del inicio del efecto, y toda operación cuyo resultado externo sea incierto debe conservar su trazabilidad y resolverse bajo una política explícita que prohíba la reejecución automática no autorizada.**

En consecuencia:

* Queda prohibida la reejecución automática de operaciones cuyo efecto externo sea incierto sin autorización explícita y contabilizable.
* Queda requerida la trazabilidad obligatoria de toda operación clasificada como incierta, incluyendo el identificador del intento original y el momento de primera detección.
* Queda requerido un mecanismo de escalamiento configurable que impida el olvido silencioso de operaciones inciertas.
* Queda explícito que el escalamiento de una operación incierta no constituye evidencia de que la reejecución sea segura.
* Queda reconocida la limitación fundamental: sin cooperación verificable del proveedor externo, no siempre es posible garantizar simultáneamente progreso automático y ausencia de duplicación externa.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de ejecutar efectos externos con autoridad recuperable y de resolver coherentemente operaciones de resultado incierto está ausente o degradada en el execution plane actual.

El sistema puede conocer que una tarea estaba asignada mediante un mecanismo de autoridad persistida, y puede registrar de forma idempotente un resultado recibido. Sin embargo, cuando el proveedor externo completa una operación pero el proceso falla antes de registrar su resultado local, la recuperación actual no distingue ese escenario de una operación que nunca llegó a ejecutarse.

Esta desconexión introduce las siguientes clases de defectos:

1. **Ausencia de semántica de recuperación para efectos inciertos:** El mecanismo de recuperación trata indistintamente operaciones cuyo efecto externo no se inició y operaciones cuyo efecto externo pudo haber ocurrido pero cuyo resultado no fue registrado localmente.

2. **Reejecución ciega bajo incertidumbre:** Ante la ausencia de resultado local registrado, el sistema asume implícitamente que el efecto externo no ocurrió y autoriza la reejecución automática, lo cual puede generar duplicación de efectos externos con impacto FinOps no acotado.

3. **Frontera distribuida no reconocida en sistema local:** Aunque la arquitectura es local (conforme al ROADMAP_ARQUITECTÓNICO_LP §V), la llamada a un proveedor remoto introduce una frontera distribuida de efectos y conocimiento que el sistema no reconoce explícitamente en su semántica de recuperación.

4. **Ausencia de trazabilidad de operaciones inciertas:** Las operaciones cuyo resultado externo es incierto no conservan trazabilidad suficiente para permitir su resolución posterior, escalamiento controlado o aceptación explícita de riesgo.

### 4.2 Manifestación concreta identificada por la auditoría

* **`GAP-18.2.2-01` (P1 — Alto):** El mecanismo de recuperación actual clasifica como "zombie puro" toda tarea con autoridad persistida expirada y sin resultado local registrado, devolviéndola a estado elegible para reejecución sin distinguir si el efecto externo pudo haber ocurrido. Esta clasificación indistinguible permite un escenario de duplicación de efectos externos cuando el proveedor completa la operación y el proceso falla antes del registro local.

* **`GAP-18.2.2-02` (P2 — Medio):** El código cliente auditado no implementa mecanismos de idempotencia, consulta de estado ni deduplicación en las llamadas al proveedor externo de LLM. Las capacidades de idempotencia del proveedor no están verificadas, lo cual impide asumir que el proveedor previene duplicación por sí mismo.

* **`E-18.2.2-007` (P1 — Alto):** El event journal carece de estados pre-efecto. El lease persistido en el control plane cumple el rol de intención durable pre-efecto, pero la ausencia de representación pre-efecto en el event plane significa que el reconciler no dispone de información suficiente para distinguir todas las situaciones de recuperación. Esta separación entre control plane y event plane, combinada con la ausencia de lógica de verificación con proveedor (E-18.2.2-008), crea el escenario de efecto externo incierto que este NADR gobierna.

* **`E-18.2.2-008` (P1 — Alto):** No existe lógica en el código auditado que consulte al proveedor externo para verificar si una llamada previa se completó. Ante un crash en la ventana entre el efecto externo y el registro local, el mecanismo de recuperación no puede resolver la ambigüedad mediante evidencia externa verificable.

* **`E-18.2.2-013` (P2 — Medio):** La búsqueda exhaustiva en el código cliente no revela implementación de mecanismos de idempotencia, request IDs ni deduplicación. Esta evidencia demuestra ausencia en el código cliente auditado; no demuestra que el proveedor externo carezca de capacidades de idempotencia (verificación pendiente de capacidad externa).

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Autoridad de ejecución pre-efecto

1. Toda ejecución de efecto externo **MUST** estar precedida por una autoridad recuperable persistida antes del inicio del efecto.
2. La autoridad de ejecución **MUST** ser verificable como vigente antes de iniciar el efecto externo.
3. La pérdida o expiración de autoridad durante una operación externa **MUST** ser detectable por el sistema, y **MUST NOT** interpretarse como capacidad demostrada para detener o revertir efectos externos ya iniciados.
4. La autoridad recuperable **MUST** preservar el identificador del intento de ejecución como distinto de la identidad científica del contrato de identidad.

### 5.2 Clasificación semántica de resultados

5. Respecto de cada intento externo, la recuperación **MUST** distinguir entre: (a) existencia de resultado local recuperable, (b) ausencia demostrable de inicio del efecto externo, y (c) incertidumbre sobre su ejecución o resultado; esas condiciones **MUST NOT** equipararse.
6. Una operación clasificada como incierta **MUST NOT** tratarse como equivalente a una operación cuyo no inicio está demostrablemente verificado.
7. La ausencia de resultado local registrado **MUST NOT** interpretarse automáticamente como prueba de que el efecto externo no ocurrió.
8. Ante evidencia insuficiente para determinar si el efecto externo ocurrió, la clasificación conservadora como incierta **MUST** ser el comportamiento por defecto.

### 5.3 Política de recuperación bajo incertidumbre

9. Una operación con resultado externo incierto **MUST NOT** ser reejecutada automáticamente por el mecanismo de recuperación.
10. Toda operación con resultado externo incierto **MUST** conservar trazabilidad suficiente para permitir su resolución posterior, escalamiento controlado o aceptación explícita de riesgo, incluyendo como mínimo el identificador del intento original y el momento de primera detección de la incertidumbre.
11. Toda operación con resultado externo incierto **MUST** disponer de un mecanismo de escalamiento configurable que impida su olvido silencioso.
12. El escalamiento de una operación incierta **MUST NOT** interpretarse como evidencia de que la reejecución sea segura.
13. La reejecución de una operación con resultado externo incierto **MUST** requerir autorización explícita.
14. Toda reejecución excepcional de una operación incierta **MUST** ser contabilizable como excepción arquitectónicamente autorizada.
15. La autorización excepcional de reejecución **MUST** requerir aceptación explícita del riesgo de duplicación.

### 5.4 Resolución por evidencia externa

16. Cuando exista evidencia externa verificable sobre el resultado de una operación incierta, el sistema **MUST** resolver su estado conforme a dicha evidencia.
17. La ausencia de evidencia externa verificable **MUST NOT** utilizarse como fundamento para asumir que el efecto externo no ocurrió.
18. La capacidad del proveedor externo de proporcionar evidencia verificable sobre el resultado de una operación **MAY** ser utilizada para resolver incertidumbre, pero **MUST NOT** asumirse sin verificación previa.

### 5.5 Identidad y compatibilidad

19. La identidad de intento utilizada para la autoridad de ejecución **MUST** preservarse como distinta de la identidad científica definida por el contrato de identidad.
20. La preservación de la correlación entre identidad de intento e identidad científica **MUST** ser verificable cuando el contrato congelado lo exija.

### 5.6 Progresión y límites

21. El sistema **SHOULD** proveer mecanismos para resolver operaciones inciertas, reconociendo el límite fundamental: sin cooperación verificable del proveedor externo, no siempre es posible garantizar simultáneamente progreso automático y ausencia de duplicación externa.
22. Toda incertidumbre externa no resuelta **MUST** conservar una representación recuperable y distinguible de las operaciones elegibles para ejecución automática, hasta su resolución o disposición autorizada.
23. La política de resolución de operaciones inciertas **MAY** configurar umbrales de escalamiento, pero dichos umbrales **MUST NOT** interpretarse como garantías de seguridad de reejecución.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

Una vez materializadas y validadas las reglas de este NADR:

* **No-reejecución ciega gobernada:** El mecanismo de recuperación no autorizará automáticamente nuevas ejecuciones de operaciones clasificadas como inciertas. Esto reduce la exposición a duplicación atribuible a recuperación ciega, sin constituir garantía de ausencia universal de efectos externos duplicados.

* **Trazabilidad obligatoria de incertidumbre:** Toda operación con resultado externo incierto conservará trazabilidad suficiente para permitir su resolución posterior, escalamiento controlado o aceptación explícita de riesgo.

* **Eliminación del olvido silencioso:** Ninguna operación incierta podrá quedar olvidada silenciosamente en el sistema, mediante mecanismos de escalamiento configurables que alcancen un estado explícito de disposición autorizada.

* **Reconocimiento explícito del trade-off:** Quedará explícito en la arquitectura el trade-off fundamental entre progreso automático y ausencia de duplicación externa, reconociendo que sin cooperación verificable del proveedor no siempre es posible garantizar ambos simultáneamente.

* **Compatibilidad con identidad científica:** Quedará preservada la distinción entre identidad de intento (autoridad de ejecución) e identidad científica (contrato de identidad congelado), conforme a NADR-F18-01 y F18_IDENTITY_BOUNDARY_CONTRACT.

* **Separación de responsabilidades normativas:** Quedará claramente delimitado que este NADR gobierna la autoridad de ejecución y la resolución de efectos inciertos, mientras que la persistencia del estado local y la observabilidad de duplicación quedan gobernadas por NADRs posteriores de la subfase.

* **Reconocimiento de frontera distribuida:** Quedará reconocido explícitamente que, aunque la arquitectura es local, la llamada a un proveedor remoto introduce una frontera distribuida de efectos y conocimiento que la semántica de recuperación debe tratar coherentemente.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Análisis de tipos que verifique la separación contractual entre identidad de intento e identidad científica.
  * Verificación de contratos de autoridad recuperable mediante type checker.
  * Import-linter que verifique que este NADR no introduce dependencias de tecnologías concretas ni de NADRs posteriores no aprobados.
  * Análisis estático de flujo de control que verifique la ausencia de rutas de reejecución automática de operaciones clasificadas como inciertas.

* **Validation (dinámica/comportamental):**
  * Pruebas de propiedad que verifiquen la clasificación mutuamente excluyente de operaciones en las categorías semánticas requeridas (resultado local recuperable, no inicio demostrable, incertidumbre).
  * Chaos harness con inyección de crash en la ventana entre efecto externo y registro local, verificando que el mecanismo de recuperación clasifica correctamente la operación como incierta y no la reejecuta automáticamente.
  * Pruebas de fencing de frontera externa que verifiquen el comportamiento del sistema ante pérdida de autoridad durante la ejecución del efecto externo.
  * Pruebas de trazabilidad que verifiquen que las operaciones inciertas conservan el identificador del intento original y el momento de primera detección.
  * Pruebas de escalamiento configurable que verifiquen que las operaciones inciertas alcanzan un estado explícito de disposición autorizada dentro de un tiempo finito.
  * Pruebas de autorización excepcional que verifiquen que la reejecución de operaciones inciertas requiere autorización explícita y se contabiliza como excepción.
  * Pruebas de compatibilidad con identidad científica que verifiquen la preservación de la correlación entre identidad de intento e identidad científica tras recuperación.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F18_MASTER` | **Materializa:** INV-JOURNAL §5.1 (DC-08a intención pre-efecto, DC-08b efectos inciertos). Este NADR desarrolla las decisiones arquitectónicas del Maestro sin redefinir los invariantes congelados. |
| `ADR_F18.2` v3.3.0 FROZEN | **Materializa:** DC-08a RATIFICADO (reutilización del lease como mecanismo principal de intención pre-efecto), DC-08b RATIFICADO CON ENMIENDA (política de recuperación bajo incertidumbre §3.2). Este NADR proporciona las reglas normativas obligatorias que materializan las decisiones del ADR. |
| `NADR-F18-01` v1.0.3 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de identidad científica definidos en NADR-F18-01. La distinción entre identidad de intento e identidad científica es condición de compatibilidad. |
| `NADR-F18-02` v1.0.1 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de ejecución bounded definidos en NADR-F18-02, incluido el límite de modificación señalado en §5.4 R15. |
| `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN | **Dependencia directa:** Este NADR preserva la distinción entre identidad científica (hash determinista) e identidad de intento (autoridad de ejecución) definida en el contrato congelado. |
| `NADR-F18-04` (pendiente) | **Influencia prevista:** Este NADR requiere que el estado local de las operaciones inciertas sea persistido coherentemente. La trazabilidad de operaciones inciertas dependerá de las garantías de persistencia durable que gobernará NADR-F18-04. |
| `NADR-F18-05` (pendiente) | **Influencia prevista:** Este NADR requiere que la exposición a reejecución de operaciones inciertas sea medible. La contabilización de reejecuciones excepcionales dependerá de la semántica de medición y contadores que gobernará NADR-F18-05. |
| `PHASE_18.2_EXECUTION_PLAN` (pendiente) | **Materializa:** Las tareas del Execution Plan implementan las reglas de este NADR. Los umbrales operativos concretos de escalamiento (número de sweeps, tiempo transcurrido) se definen en el Execution Plan, no en este NADR. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la política física de durabilidad del almacenamiento ni la configuración de write-policy SQLite (responsabilidad prevista de `NADR-F18-04`).
* **No gobierna** la idempotencia de materialización local de resultados confirmados (responsabilidad prevista de `NADR-F18-04`).
* **No gobierna** la semántica de indicadores de duplicación ni la diferenciación entre reejecuciones del cliente, duplicación inferida y duplicación confirmada (responsabilidad prevista de `NADR-F18-05`).
* **No gobierna** la semántica de contadores, tasas y ventanas temporales de medición de duplicación (responsabilidad prevista de `NADR-F18-05`).
* **No gobierna** los umbrales operativos concretos de escalamiento (número de sweeps, tiempo transcurrido, tamaño de benchmarks); estos son decisiones operativas del `PHASE_18.2_EXECUTION_PLAN`.
* **No gobierna** la configuración específica de proveedores externos ni asume capacidades no verificadas de proveedores; la verificación de capacidades externas corresponde al `PHASE_18.2_EXECUTION_PLAN`.
* **No gobierna** los diferimientos formales condicionados DF-24 (CircuitBreaker) y DF-34 (ProfileStore); estos mantienen su trazabilidad propia conforme a `ADR_F18.2` §8.3 y quedan pendientes de resolución cuando se cumplan sus triggers.
* **No prescribe** tareas de implementación, nombres de clases, archivos, funciones o tecnologías concretas.
* **No prescribe** Definition of Done ni criterios de aceptación operativa (responsabilidad del `PHASE_18.2_EXECUTION_PLAN`).
* **No modifica** los contratos congelados de la Subfase 18.1 (responsabilidad de `NADR-F18-01` y `NADR-F18-02`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias que gobiernan la capacidad de autoridad de ejecución y resolución de efectos inciertos. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el `PHASE_18.2_EXECUTION_PLAN` correspondiente. Los umbrales operativos concretos (número de sweeps, tiempo transcurrido, tamaño de benchmarks) no forman parte de este NADR y corresponden al Execution Plan. Las dependencias de NADR-F18-04 y NADR-F18-05 son influencias previstas; sus contratos normativos específicos se establecerán cuando esos documentos sean emitidos.