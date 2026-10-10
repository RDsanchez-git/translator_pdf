# NADR-F18-05: Observabilidad de Intentos, Exposición y Duplicación de Efectos Externos

## 1. METADATA

* **Decision ID:** `NADR-F18-05`
* **Título:** Observabilidad de Intentos, Exposición y Duplicación de Efectos Externos
* **Clase de Decisión:** `OPERATIONAL / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.3.0
* **Ciclo de Vida:** `FROZEN`
* **Fecha de Congelamiento:** 2026-10-11
* **Vigente Desde:** Subfase 18.2 — Durable Execution & Recovery
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Staff Engineering / Execution Plane Team
* **Capacidad Arquitectónica:** CAP-18-05 (Observabilidad de Intentos, Exposición y Duplicación) — Proveer trazabilidad observable que permita correlacionar intentos, resultados y decisiones de recuperación, distinguir estratificadamente actividad del cliente de evidencia sobre duplicación externa, y caracterizar la exposición temporal y económica dentro de límites epistemológicos explícitos, sin atribuir al proveedor garantías no verificadas ni crear fuentes de verdad paralelas inconsistentes con la persistencia gobernada.
* **Evidencia Forense:**
  * `GAP-18.2.2-04` (P1): Ausencia de medición directa suficiente de ventana de duplicación y frecuencia natural
  * `E-18.2.2-030` (P1): Ausencia de instrumentación entre `execute()` y `append_wal()` para caracterizar ventana de exposición. La falta de instrumentación local impide medir adecuadamente la ventana cliente, pero incluso instrumentarla no bastaría por sí sola para observar el momento causal de finalización remota.
  * `E-18.2.2-033` (P1): `ProductionTelemetryEvent` carece de campos para distinguir primera ejecución de re-ejecución (`retry_count`, `attempt_number`, `is_replay`)
  * `E-18.2.2-029` (P2): Timing con `perf_counter` mide latencia total del nodo, no ventana específica de exposición
  * `E-18.2.2-031` (P2): Telemetry gateway con buffer in-memory; pérdida de eventos en crash abrupto
  * `HITO_18.2.1 v1.2.0`: Estimación indirecta de ventana ~1ms (resta de latencia mock); no constituye medición directa de ventana causal
* **Referencias Cruzadas:**
  * **Depende de:**
    * `ADR_F18_MASTER` (INV-JOURNAL §5.1: "ventana de duplicación acotada y medida"; DC-08 §8.2)
    * `ADR_F18.2` v3.3.0 FROZEN (DC-08c RATIFICADO: medición de duplicación; §3.1 Matriz de decisión arquitectónica; §7 Capacidades de verificación requeridas)
    * `NADR-F18-01` v1.0.3 FROZEN (Execution Identity & Scientific Isolation: distinción identidad científica vs identidad de intento)
    * `NADR-F18-02` v1.0.1 FROZEN (Bounded Concurrent Execution: contratos de ejecución bounded)
    * `NADR-F18-03` v1.2.0 FROZEN (Autoridad de Ejecución y Resolución de Efectos Inciertos: política de reejecución excepcional autorizada)
    * `NADR-F18-04` v1.1.1 FROZEN (Persistencia Recuperable e Idempotencia de Aplicación Local: garantías de persistencia para trazabilidad de decisiones)
    * `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN (distinción identidad científica vs identidad de intento)
  * **Influencia prevista:**
    * `PHASE_18.2_EXECUTION_PLAN` (pendiente): definirá tareas de materialización, umbrales operativos, instrumentos de medición y criterios de aceptación
  * **Conflictúa con:** Agregación engañosa de métricas de duplicación; presentación de inferencia como confirmación; creación de fuentes de verdad paralelas inconsistentes con NADR-F18-04
  * **Reemplaza a:** N/A (primer NADR que gobierna esta capacidad)

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 3/5 — La falta de observabilidad gobernada no corrompe directamente el sistema, pero impide caracterizar riesgos de duplicación y tomar decisiones informadas de recuperación. Sin trazabilidad estratificada, el equipo operativo no puede distinguir reejecuciones legítimas de duplicaciones no autorizadas.
* **Mantenibilidad:** 4/5 — Sin reglas normativas explícitas de observabilidad, la evolución del sistema introduce deuda de medición: cada equipo interpreta las métricas de forma inconsistente, las agregaciones se vuelven engañosas y la capacidad de auditar decisiones de recuperación se degrada progresivamente.
* **Recuperabilidad:** 3/5 — La observabilidad no es directamente recuperabilidad (gobernada por NADR-F18-03 y NADR-F18-04), pero provee la evidencia necesaria para auditoría post-fallo, reconstrucción de secuencias de eventos y validación de que las políticas de recuperación se aplicaron conforme a diseño.
* **Seguridad:** 2/5 — No es vector de ataque directo, pero la ausencia de trazabilidad de decisiones excepcionales (reejecuciones autorizadas bajo incertidumbre) puede ocultar comportamientos anómalos o abusos.
* **Financiero:** 4/5 — Sin medición gobernada de duplicación de efectos externos, el impacto FinOps no puede caracterizarse ni verificarse adecuadamente: no se puede estimar la exposición real, no se puede validar el coste de reejecuciones, y no se puede evaluar si la propiedad de "ventana de duplicación acotada y medida" (INV-JOURNAL) se satisface. La observabilidad permite estimar, caracterizar y verificar límites; el control efectivo de costes depende también de las políticas de ejecución y recuperación.
* **Total Score: 16/25**

**Severidad:** `S1` (Crítico)

**Justificación de la severidad:** Se clasifica como Crítico (S1) conforme al template metodológico (rango 16-25). El riesgo financiero es alto porque sin observabilidad gobernada no se puede caracterizar ni verificar el coste de duplicación de efectos externos, impidiendo evaluar la propiedad de "ventana de duplicación acotada y medida" exigida por INV-JOURNAL. La mantenibilidad es alta porque la ausencia de reglas normativas permite que cada equipo interprete las métricas de forma inconsistente, introduciendo deuda técnica y riesgo de agregaciones engañosas.

---

## 3. DECISIÓN EJECUTIVA

**Toda ejecución de efecto externo debe disponer de trazabilidad observable que permita correlacionar intentos, resultados y decisiones de recuperación, distinguir estratificadamente actividad del cliente de evidencia sobre duplicación externa, y caracterizar la exposición temporal y económica dentro de límites epistemológicos explícitos, sin atribuir al proveedor garantías no verificadas ni crear fuentes de verdad paralelas inconsistentes con la persistencia gobernada.**

En consecuencia:

* Queda requerida la correlación observable entre operación lógica, intentos de ejecución y resultados locales conocidos.
* Queda prohibida la agregación engañosa de métricas que confluyan actividad del cliente y evidencia de duplicación externa sin desglose estratificado explícito.
* Queda prohibida la presentación de inferencia como confirmación; la incapacidad de medir debe reportarse explícitamente como tal, no inferirse como cero ni como duplicación confirmada.
* Queda requerida la distinción entre ventanas de exposición observables en el cliente y ventanas causales externas, sin declarar la primera como cota demostrada de la segunda sin validación de la relación correspondiente.
* Queda requerida la trazabilidad durable de decisiones excepcionales (reejecuciones autorizadas bajo incertidumbre) conforme a las garantías de persistencia de NADR-F18-04.
* Queda explícito que este NADR no impone infraestructura específica de observabilidad ni umbrales universales de aceptación; la materialización técnica y la calibración de límites corresponden al Execution Plan.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de observar intentos de ejecución, caracterizar exposición a duplicación y medir impacto económico de reejecuciones está ausente o degradada en el execution plane actual.

El sistema puede registrar eventos locales (append_wal, upsert_projection) y puede medir latencia total del nodo (node_latency), pero no dispone de instrumentación suficiente para:

1. **Distinguir estratificadamente actividad del cliente de evidencia de duplicación externa:** Las métricas actuales no separan "el cliente re-ejecutó" de "hay evidencia de que el proveedor aplicó el efecto múltiples veces". Esta confluencia impide caracterizar la exposición real y genera agregaciones engañosas.

2. **Caracterizar la ventana de exposición causal:** La estimación indirecta de ~1 ms de `HITO_18.2.1` intenta aproximar un componente temporal local mediante resta de latencias con mock, pero no constituye una medición directa de la ventana cliente ni demuestra la duración de la ventana causal externa (efecto remoto completado → resultado local durable). Sin instrumentación específica, no se puede validar la relación entre ambas ventanas ni declarar cotas causales.

3. **Proveer trazabilidad de decisiones excepcionales:** Cuando el sistema autoriza una reejecución bajo incertidumbre (conforme a NADR-F18-03 §3.2), no hay garantía de que esa decisión conserve correlación observable durable con su autorización y aceptación de riesgo.

4. **Exponer datos accionables para FinOps:** Los costes observados, estimados y la exposición económica potencial no confirmada no se distinguen explícitamente, lo que impide que los mecanismos de control de presupuesto consuman datos confiables para evaluar la propiedad de "ventana de duplicación acotada y medida".

Esta ausencia de observabilidad gobernada introduce las siguientes clases de defectos:

1. **Agregación engañosa:** Las métricas de duplicación confluyen categorías epistemológicamente distintas (actividad del cliente, evidencia inferida, evidencia confirmada), generando indicadores que no reflejan la exposición real y pueden llevar a decisiones erróneas.

2. **Riesgo de falsa certeza operacional:** La incapacidad de medir duplicación confirmada (por ausencia de evidencia verificable del proveedor) podría presentarse silenciosamente como "cero duplicación" o inferirse como "duplicación confirmada" a partir de reejecuciones del cliente, violando la honestidad epistemológica. Esta es una hipótesis de riesgo basada en la falta de instrumentación observada, no una afirmación demostrada de comportamiento actual.

3. **Pérdida de trazabilidad de decisiones:** Las reejecuciones excepcionales autorizadas bajo incertidumbre no conservan correlación observable durable con su autorización, impidiendo auditoría post-fallo y validación de que las políticas se aplicaron conforme a diseño.

4. **Incapacidad de evaluar INV-JOURNAL:** Sin medición estratificada de duplicación, no se puede evaluar si la propiedad de "ventana de duplicación acotada y medida" se satisface, dejando el cumplimiento de INV-JOURNAL como afirmación no verificable.

### 4.2 Manifestación concreta identificada por la auditoría

* **`GAP-18.2.2-04` (P1 — Alto):** Telemetría sin distinción de re-ejecución. `ProductionTelemetryEvent` no tiene campos `retry_count`, `attempt_number`, `is_replay`, ni similar. No se puede medir tasa natural de duplicación en producción. Esta ausencia impide evaluar la propiedad de "ventana de duplicación acotada y medida" exigida por INV-JOURNAL.

* **`E-18.2.2-030` (P1 — Alto):** Ausencia de instrumentación entre `execute()` y `append_wal()`. No hay métricas intermedias, logs de timing, ni telemetría específica de la ventana de exposición. Esto impide caracterizar la ventana causal externa y validar su relación con la ventana cliente observable. La falta de instrumentación local impide medir adecuadamente la ventana cliente, pero incluso instrumentarla no bastaría por sí sola para observar el momento causal de finalización remota.

* **`E-18.2.2-033` (P1 — Alto):** `ProductionTelemetryEvent` carece de campos para distinguir primera ejecución de re-ejecución. El modelo de datos actual no soporta la taxonomía estratificada exigida por DC-08c.

* **`E-18.2.2-029` (P2 — Medio):** Timing con `perf_counter` mide latencia total del nodo, no ventana específica de exposición. La métrica existente no es suficiente para caracterizar la propiedad de "ventana de duplicación acotada y medida".

* **`E-18.2.2-031` (P2 — Medio):** Telemetry gateway con buffer in-memory; pérdida de eventos en crash abrupto. La durabilidad de la trazabilidad de decisiones excepcionales debe gobernarse conforme a NADR-F18-04.

* **`HITO_18.2.1 v1.2.0` (evidencia heredada):** Estimación indirecta de ventana ~1ms (resta de latencia mock de 25ms a medición total de ~26ms). Esta estimación no constituye medición directa de ventana causal y no debe presentarse como cota demostrada.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Correlación e Identidad

1. Todo intento de efecto externo **MUST** ser correlacionable con su operación lógica original y su resultado local conocido, mediante identificadores estables que preserven la trazabilidad a lo largo de reintentos, recuperaciones y decisiones excepcionales.

2. La observabilidad **MUST NOT** equiparar, confluir ni sustituir la identidad de intento (autoridad de ejecución) por la identidad científica definida en el contrato de identidad congelado. La preservación de esta distinción **MUST** ser verificable en toda métrica, log o reporte que involucre ejecución de efectos externos.

3. Toda operación lógica **MUST** disponer de una clave de correlación lógica estable que permita correlacionar sus múltiples intentos de ejecución a lo largo del tiempo. Esta clave **MAY** derivarse de identidades existentes cuando resulte inequívoca, sin imponer un identificador físico adicional si las identidades existentes son suficientes para la correlación requerida.

### 5.2 Taxonomía y Medición Estratificada

4. La observabilidad **MUST** distinguir dos dimensiones conceptuales:
   - **Actividad del cliente:** intento inicial, reejecución y cantidad de intentos de una operación lógica.
   - **Evidencia de duplicación externa:** desconocida, inferida o confirmada, según el alcance de la evidencia disponible.
   
   Estas dimensiones **MUST NOT** modelarse como estados mutuamente excluyentes de una operación. Una operación **MAY** tener simultáneamente reejecución del cliente y evidencia de duplicación externa. La duplicación externa inferida y confirmada **MUST** identificarse según su fundamento probatorio, sin contabilizar una misma duplicación varias veces por cambios en su clasificación.

5. **Duplicación externa confirmada** se define como: evidencia verificable y suficientemente atribuible que acredita más de una aplicación externa de la misma operación lógica, conforme al criterio de confirmación declarado. La mera existencia de múltiples intentos del cliente, cargos agregados o señales indirectas **MUST NOT** constituir por sí sola confirmación. La fuente de evidencia **MAY** ser el proveedor, reportes de facturación atribuibles, o cualquier otra fuente verificable y suficientemente atribuible.

6. Toda tasa reportada **MUST** declarar explícitamente su numerador, denominador, unidad de observación (intento, operación lógica o efecto externo), período de observación, cobertura de datos y limitaciones de comparabilidad. Queda **PROHIBIDO** presentar una "tasa de duplicación" única que confluya actividad del cliente y evidencia de duplicación externa sin desglose explícito de ambas dimensiones.

7. La ausencia de evidencia externa verificable **MUST NOT** interpretarse como evidencia de ausencia de duplicación. La incapacidad de confirmar duplicación **MUST** documentarse explícitamente como limitación epistemológica, no como garantía de no-duplicación.

### 5.3 Ventanas y Límites Epistemológicos

8. Las ventanas temporales observables del cliente y las ventanas causales externas **MUST** distinguirse conceptualmente y en todo reporte aplicable. Cada duración **MUST** identificarse como medida, estimada, acotada mediante evidencia validada, o no observable. Una ventana cliente **MUST NOT** presentarse como duración ni como cota causal demostrada de la ventana externa sin validación explícita de la relación correspondiente.

9. Una medición o estimación indirecta de ventana de exposición **MUST NOT** presentarse como cota superior validada sin evidencia que demuestre la relación entre la medición indirecta y la cota causal. La distinción entre "duración medida" y "cota superior validada" **MUST** preservarse en toda documentación, reporte o métrica.

10. La pérdida, insuficiencia o ceguera deliberada de observabilidad **MUST** ser identificable y reportada explícitamente; **MUST NOT** transformarse silenciosamente en valores cero, suposiciones de éxito o inferencias no fundamentadas.

### 5.4 Excepciones y FinOps

11. Toda reejecución excepcional autorizada bajo incertidumbre (conforme a NADR-F18-03 §3.2) **MUST** conservar una correlación observable y durable (conforme a las garantías de persistencia de NADR-F18-04) con su decisión de autorización, la aceptación explícita del riesgo asociado y la identidad de la autoridad que tomó la decisión.

12. Los costes derivados de efectos externos **MUST** distinguirse explícitamente en tres categorías en los reportes financieros:
    - **Coste observado o facturado:** coste real confirmado por el proveedor o sistema de facturación.
    - **Coste estimado:** coste calculado a partir de precios conocidos y uso observado, sin confirmación directa del proveedor.
    - **Exposición económica potencial no confirmada:** coste hipotético derivado de duplicación inferida o efectos inciertos, sin evidencia suficiente de que ocurrió.
    
    Queda **PROHIBIDO** presentar costes hipotéticos de benchmark como gasto real de producción sin declaración explícita de su naturaleza estimada o potencial. La atribución de reejecuciones a operaciones lógicas **MUST** preservarse cuando sea posible, de forma que el impacto económico pueda correlacionarse con operaciones específicas y no solo con agregados globales.

### 5.5 Integridad de la Evidencia

13. **Integridad y autoridad de evidencia:** La observabilidad **MUST** respetar la jerarquía de autoridad y las garantías de persistencia gobernadas por NADR-F18-04. La observabilidad **MUST NOT** crear una fuente de verdad paralela e inconsistente con la persistencia del estado local.

14. **Recuperabilidad de decisiones excepcionales:** La trazabilidad de decisiones excepcionales (reejecuciones autorizadas bajo incertidumbre) **MUST** regirse por las mismas garantías de persistencia durable que el estado local gobernado por NADR-F18-04, permitiendo reconstrucción tras fallos y auditoría post-recuperación.

15. **Distinción entre evidencia auditable y telemetría derivada:** Las métricas de agregación (histogramas, contadores, tasas) **MAY** ser efímeras si su pérdida no compromete la capacidad de auditar decisiones o reconstruir secuencias de eventos. La evidencia necesaria para autorizar y auditar decisiones excepcionales **MUST** ser durable conforme a NADR-F18-04. La retención concreta de métricas agregadas corresponde al Execution Plan, siempre que se identifique la autoridad responsable de aprobarla y se respeten requisitos superiores aplicables.

16. La observabilidad **MUST NOT** imponer infraestructura específica (sistemas de telemetría, backends de métricas, herramientas de visualización) ni prescribir tecnologías concretas. La materialización técnica corresponde al Execution Plan, conforme a los principios de Reuse Before Invent y YAGNI.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

Una vez materializadas y validadas las reglas de este NADR:

* **Correlación observable garantizada:** Toda ejecución de efecto externo dispondrá de trazabilidad que permita correlacionar operación lógica, intentos de ejecución y resultados locales conocidos, preservando la distinción entre identidad de intento e identidad científica.

* **Taxonomía estratificada de duplicación:** Las métricas de exposición distinguirán explícitamente actividad del cliente (intentos, reejecuciones) de evidencia sobre duplicación externa (desconocida, inferida, confirmada), eliminando agregaciones engañosas y permitiendo caracterizar la exposición real.

* **Honestidad epistemológica:** La incapacidad de medir duplicación confirmada se reportará explícitamente como limitación epistemológica, no se inferirá como cero duplicación ni se presentará como confirmación. La falsa certeza operacional quedará prohibida por contrato normativo.

* **Distinción de ventanas:** Las ventanas de exposición observables en el cliente se identificarán como medidas, estimadas, acotadas o no observables, sin declarar la primera como cota demostrada de la ventana causal externa sin validación explícita de la relación correspondiente.

* **Trazabilidad durable de decisiones excepcionales:** Las reejecuciones autorizadas bajo incertidumbre conservarán correlación observable durable con su autorización y aceptación de riesgo, conforme a las garantías de persistencia de NADR-F18-04, permitiendo auditoría post-fallo y validación de políticas.

* **Exposición FinOps accionable:** Los costes observados, estimados y la exposición económica potencial no confirmada se distinguirán explícitamente, y la observabilidad expondrá datos accionables para los mecanismos de control de presupuesto, permitiendo evaluar la propiedad de "ventana de duplicación acotada y medida".

* **Integridad de evidencia:** La observabilidad respetará la jerarquía de autoridad de NADR-F18-04, sin crear fuentes de verdad paralelas inconsistentes. La trazabilidad de decisiones excepcionales se regirá por las mismas garantías de persistencia durable que el estado local.

* **Evaluabilidad de INV-JOURNAL:** La observabilidad permitirá evaluar de forma explícita la evidencia disponible sobre exposición temporal y duplicación externa, identificando qué propiedades están demostradas, cuáles permanecen inferidas y cuáles no pueden certificarse con la información disponible. La existencia de métricas estratificadas no constituirá por sí misma demostración de una cota causal externa.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación estática de la existencia y consistencia estructural de los contratos de correlación, complementada por validación dinámica de su cobertura efectiva.
  * Revisión normativa del documento que verifique que este NADR no prescribe tecnologías concretas de observabilidad (Prometheus, OpenTelemetry, backends específicos).
  * Verificación de que las métricas de exposición distinguen las dos dimensiones (actividad del cliente y evidencia de duplicación externa) y no las confluyen en agregaciones únicas.
  * Análisis estático de contratos de persistencia que verifique que la trazabilidad de decisiones excepcionales respeta las garantías de NADR-F18-04.
  * Verificación de que toda tasa reportada declara explícitamente numerador, denominador, unidad de observación, período y cobertura.

* **Validation (dinámica/comportamental):**
  * **Correlación:** Pruebas que verifiquen que varios intentos de una misma operación lógica conservan atribución correcta a lo largo de reintentos, recuperaciones y decisiones excepcionales.
  * **Taxonomía:** Pruebas que verifiquen que reejecución del cliente no implica automáticamente duplicación externa confirmada, y que ambas dimensiones se reportan separadamente.
  * **Evolución de evidencia:** Pruebas que verifiquen que un caso inicialmente inferido puede pasar a confirmado sin doble conteo, preservando la trazabilidad del cambio de clasificación.
  * **Denominadores:** Pruebas que verifiquen que las tasas declaran unidades, período, cobertura y datos ausentes, y que no presentan agregaciones engañosas.
  * **Ventanas:** Pruebas que verifiquen que la duración cliente no se reporta como cota externa sin evidencia, y que cada ventana se identifica como medida, estimada, acotada o no observable.
  * **Ceguera de observabilidad:** Pruebas que verifiquen que eventos perdidos o ausentes se identifican explícitamente y no producen ceros engañosos o suposiciones de éxito.
  * **FinOps:** Pruebas que verifiquen que costes observados, estimados y exposición potencial no confirmada se distinguen explícitamente y no se confunden en reportes.
  * **Auditoría:** Pruebas que verifiquen que una autorización excepcional sigue siendo correlacionable con su decisión y aceptación de riesgo después de recuperación tras crash.
  * **Simulación vs realidad:** Pruebas de simulación que verifiquen la clasificación y los contadores del cliente bajo condiciones controladas, declarando explícitamente que la simulación valida el comportamiento del cliente pero no certifica duplicaciones reales del proveedor.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F18_MASTER` v1.0.0 FROZEN | **Materializa:** DC-08c (medición de duplicación) y propiedad de "ventana de duplicación acotada y medida" de INV-JOURNAL §5.1. Este NADR desarrolla las decisiones arquitectónicas del Maestro sin redefinir los invariantes congelados. |
| `ADR_F18.2` v3.3.0 FROZEN | **Materializa:** DC-08c RATIFICADO (medición de duplicación con tres magnitudes diferenciadas), §3.1 Matriz de decisión arquitectónica, §7 Capacidades de verificación requeridas. Este NADR proporciona las reglas normativas obligatorias que materializan las decisiones del ADR. |
| `NADR-F18-01` v1.0.3 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de identidad científica definidos en NADR-F18-01. La observabilidad preserva la distinción entre identidad de intento e identidad científica. |
| `NADR-F18-02` v1.0.1 FROZEN | **Dependencia directa:** Este NADR respeta los contratos de ejecución bounded definidos en NADR-F18-02. La observabilidad no introduce concurrencia no gobernada ni viola los límites de ejecución. |
| `NADR-F18-03` v1.2.0 FROZEN | **Dependencia directa:** Este NADR provee la observabilidad necesaria para auditar las decisiones de reejecución excepcional autorizada gobernadas por NADR-F18-03 §3.2. La trazabilidad de decisiones excepcionales conserva correlación con su autorización y aceptación de riesgo. |
| `NADR-F18-04` v1.1.1 FROZEN | **Dependencia directa:** Este NADR respeta las garantías de persistencia durable gobernadas por NADR-F18-04. La trazabilidad de decisiones excepcionales se rige por las mismas garantías de persistencia que el estado local. Las métricas de agregación pueden ser efímeras si su pérdida no compromete la auditoría de decisiones. |
| `F18_IDENTITY_BOUNDARY_CONTRACT` v1.0.2 FROZEN | **Dependencia directa:** Este NADR preserva la distinción entre identidad científica (hash determinista) e identidad de intento (autoridad de ejecución) definida en el contrato congelado. La observabilidad no confluye ambas identidades. |
| `PHASE_18.2_EXECUTION_PLAN` (pendiente) | **Materializa:** Las tareas del Execution Plan implementan las reglas de este NADR. La materialización técnica (instrumentos de medición, backends de métricas, herramientas de visualización, umbrales operativos, criterios de aceptación) se define en el Execution Plan, no en este NADR. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la política de reejecución de operaciones inciertas ni la autorización de reejecuciones excepcionales (responsabilidad de `NADR-F18-03`).
* **No gobierna** la persistencia durable del estado local ni las garantías de idempotencia de aplicación (responsabilidad de `NADR-F18-04`).
* **No gobierna** la autoridad de ejecución pre-efecto ni la clasificación semántica de resultados (responsabilidad de `NADR-F18-03`).
* **No prescribe** infraestructura específica de observabilidad (sistemas de telemetría, backends de métricas, herramientas de visualización, protocolos de exportación); la materialización técnica corresponde al `PHASE_18.2_EXECUTION_PLAN`.
* **No prescribe** umbrales universales de aceptación de duplicación ni límites económicos máximos; la calibración de límites corresponde al `PHASE_18.2_EXECUTION_PLAN` con validación del Architecture Board si los riesgos exceden la autoridad del plan.
* **No prescribe** tareas de implementación, nombres de clases, archivos, funciones, esquemas de eventos concretos o secuencia de cambios.
* **No prescribe** Definition of Done ni criterios de aceptación operativa (responsabilidad del `PHASE_18.2_EXECUTION_PLAN`).
* **No gobierna** los diferimientos formales condicionados DF-24 (CircuitBreaker) y DF-34 (ProfileStore); estos mantienen su trazabilidad propia conforme a `ADR_F18.2` §8.3.
* **No modifica** los contratos congelados de la Subfase 18.1 (responsabilidad de `NADR-F18-01` y `NADR-F18-02`).
* **No crea** una fuente de verdad paralela e inconsistente con la persistencia gobernada por `NADR-F18-04`; la observabilidad respeta la jerarquía de autoridad del estado local.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias que gobiernan la capacidad de observabilidad de intentos, exposición y duplicación de efectos externos. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el `PHASE_18.2_EXECUTION_PLAN` correspondiente. La materialización técnica (instrumentos de medición, backends de métricas, herramientas de visualización, umbrales operativos) no forma parte de este NADR y corresponde al Execution Plan. NADR-F18-04 es una dependencia normativa congelada cuyas garantías de persistencia son obligatorias para la trazabilidad de decisiones excepcionales. Este NADR cierra las tres capacidades normativas previstas para la Subfase 18.2: autoridad y efectos inciertos (NADR-F18-03), persistencia e idempotencia local (NADR-F18-04), y observabilidad de exposición y duplicación (NADR-F18-05).