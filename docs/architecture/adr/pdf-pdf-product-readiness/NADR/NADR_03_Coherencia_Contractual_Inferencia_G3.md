# NADR-FPPPR-03: Coherencia Contractual de la Inferencia EN→ES — Intención, Selección y Admisión de la Petición Efectiva

**FROZEN v1.0.0 — aprobado integralmente por el Architecture Board el 2026-11-20; congelamiento documental autorizado.**

## 1. METADATA

- **Decision ID:** `NADR-FPPPR-03` — identificador ratificado por el Architecture Board.
- **Título:** Coherencia Contractual de la Inferencia EN→ES — Intención, Selección y Admisión de la Petición Efectiva.
- **Clase de Decisión:** OPERATIONAL / DATA.
- **Nivel de Cumplimiento:** MANDATORY.
- **Versión:** 1.0.0 — primera versión FROZEN; diez reglas RFC 2119 aprobadas sin alteraciones desde DRAFT v0.2.0.
- **Ciclo de Vida:** FROZEN.
- **Fecha de Aprobación Integral:** 2026-11-20; decisión expresa del Architecture Board comunicada por el owner sobre PR #78, HEAD `cea98b19f603f632ef7f45396cd566d9bb0f41d4` (DRAFT v0.2.0).
- **Fecha de Congelamiento Documental:** 2026-11-20; autorizado en la misma decisión.
- **Procedencia de Autoridad:** Comunicación directa del owner en esta conversación; no se presume acta externa, firma ni review formal independiente en GitHub. El owner autorizó posteriormente en la misma intervención la integración del PR #78 exclusivamente en `pdf-pdf-product-readiness`.
- **Vigente Desde:** Etapa normativa PPPR — 2026-11-20 tras la aprobación integral del Board; su ejecución posterior requiere el Execution Plan y las autorizaciones aplicables.
- **Autoridad:** Architecture Board.
- **Responsable Técnico:** Staff Engineering / G3 — rol ratificado por el Architecture Board; no se designa persona.
- **Capacidad Arquitectónica:** `CAP-PPPR-03` — código ratificado por el Architecture Board. Coherencia verificable entre intención lingüística, selección de backend/modelo, admisión presupuestaria y petición efectiva de inferencia G3.
- **Evidencia Forense:** `GAP-0.1-01`, `GAP-0.4-01…04`; `E-0.1-002/023`; `E-0.4-001/002/003/005/006/011/012/013/014/017/019`; reconciliación PPPR.0.9 §14.
- **Referencias Cruzadas:**
  - **Depende de:** ADR Maestro PPPR FROZEN, especialmente DC-02 y DC-03.
  - **Influencia prevista:** futuro `PHASE_PPPR_EXECUTION_PLAN.md`, únicamente después de aprobación.
  - **Contratos existentes de frontera:** `NADR-F17BIS-08`, `NADR-F18-03/05` y `NADR-FPPPR-01/02` FROZEN, cada uno en su ámbito compatible; no se presumen dependencias recíprocas.
  - **Referencia no vinculante:** `NADR-F17BIS-06` PROPOSED.
  - **Conflictúa con:** admitir o despachar una petición cuya intención, modelo, ventana, autorización o presupuesto no correspondan a la operación efectiva.
  - **Reemplaza a:** N/A.

No se crea una fase numerada del ROADMAP ni se modifica la gobernanza de contratos FROZEN existentes. El Architecture Board aprobó integralmente las diez reglas de esta capacidad, ratificó sus metadatos y autorizó FROZEN v1.0.0; la integración se autorizó expresamente como acto posterior y separado. No se autorizan implementación, egress, gasto comercial ni certificación científica.

## 2. ARCHITECTURE RISK SCORE

Puntuación de riesgo arquitectónico ratificada por el Architecture Board para una inferencia contractual o presupuestariamente incoherente. No describe incidentes comerciales observados.

| Dimensión | Puntaje | Justificación |
|---|---:|---|
| Operacional | 4/5 | Pueden admitirse peticiones destinadas a un modelo no soportado, sin idioma explícito o fuera de ventana. |
| Mantenibilidad | 3/5 | La divergencia entre selección lógica y petición física dificulta evolucionar proveedores y mecanismos de fallback. |
| Recuperabilidad | 2/5 | La atribución deficiente de una decisión complica el diagnóstico; F18 gobierna la recuperación operacional. |
| Seguridad | 3/5 | Una selección o despacho sin verificación de autoridad puede vulnerar las restricciones de egress; no se acredita exposición real. |
| Financiero | 3/5 | La admisión incompatible con presupuesto o condiciones comerciales puede ocasionar gasto no previsto; no hay cargos medidos. |
| **Total** | **15/25** | **S2 — ALTO, ratificado por el Board** |

- **Total Score:** `15/25`.
- **Severidad:** `S2` (ALTO), ratificada por el Architecture Board (15/25).

## 3. DECISIÓN EJECUTIVA

**Toda petición de inferencia EN→ES DEBERÁ ser admitida y despachada únicamente cuando exista correspondencia verificable entre la intención lingüística de la generación, el backend y modelo efectivamente seleccionados, todos los límites de capacidad aplicables, el criterio de medición, las autorizaciones de egress y presupuesto requeridas, y la petición que realmente será transmitida. Si cualquiera de esas precondiciones obligatorias falla o no está acreditada, el despacho DEBERÁ bloquearse antes de iniciar el efecto externo.**

La decisión no selecciona proveedor, modelo físico, tarifa, algoritmo de estimación ni política comercial nueva.

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La ruta PPPR requiere inferencia G3 para traducir documentos científicos desde inglés hacia español.

Entre la intención de traducción y el envío efectivo existen decisiones sobre modelo, capacidad de ventana, representación del prompt, fallback y presupuesto. Si esas decisiones no corresponden a la petición real, el sistema puede declarar admisible una operación distinta de la que terminaría solicitando.

Se distinguen cuatro obligaciones de una sola capacidad:

1. Intención lingüística explícita y transmitida hasta la frontera efectiva de inferencia.
2. Selección de backend/modelo coherente con capacidades efectivas, autorización y condiciones del destino seleccionado, incluidas las conmutaciones.
3. Admisión por límites completos e independientes que correspondan al modelo y petición reales; medición directa o estimación conservadora acreditada, sin imponer identidad byte a byte de representaciones.
4. Bloqueo del despacho antes del efecto externo cuando cualquier precondición obligatoria no está satisfecha, preservando la autoridad F18 sobre efectos que pudieron iniciarse.

No se presupone proveedor comercial aprobado ni gasto previamente autorizado.

### 4.2 Manifestación concreta identificada por la auditoría

**GAP-0.4-01 — E-0.4-001/013.** La configuración G3 utiliza un identificador de modelo que el proveedor documentó como retirado desde 2025-08-30. El estado documental del modelo fue constatado; no hubo solicitud autenticada ni fallo efectivo demostrado para una cuenta.

**GAP-0.1-01 ↔ GAP-0.4-02 — E-0.1-002/023 y E-0.4-002.** La decisión `SWITCH_MODEL` puede aceptarse lógicamente sin modificar el modelo utilizado en la petición del proveedor. Son dos identificadores forenses conservados para una misma causa.

**GAP-0.4-03 — E-0.4-003/011/012.** La ruta CLI→G3 no transporta explícitamente el destino español en el esquema y las instrucciones efectivas. Una mención a un idioma supuestamente configurado no acredita la existencia de ese contrato.

**GAP-0.4-04 — E-0.4-019.** La decisión de fallback puede comprobar el núcleo de tokens contra la ventana alternativa sin incluir el contexto total. La admisión puede representar una petición mayor que la capacidad supuestamente seleccionada.

**E-0.4-005/017 — P2.** El estimador y la representación lógica medida no demuestran, por sí solos, compatibilidad con el tokenizador efectivo ni cobertura suficiente de la petición física renderizada. No se ha acreditado una subestimación cuantitativa ni se exige conteo exacto para toda alternativa posible.

**E-0.4-006/014 — P2.** Las estimaciones de tokens, cuotas y guardas posteriores a una respuesta no constituyen automáticamente un límite monetario pre-efecto.

**ADR Maestro PPPR — DC-02/03 FROZEN.** El alcance inicial fija EN→ES y exige inferencia autorizada, presupuesto previamente aceptado, compatibilidad de modelo/ventana y rechazo explícito cuando falten condiciones necesarias. No aprueba proveedor concreto, límite monetario universal ni traslado automático de autorizaciones entre destinos de egress.

**Contratos existentes.** `NADR-F17BIS-08` FROZEN gobierna cuotas y circuitos en su ámbito; `NADR-F18-03/05` FROZEN gobierna autoridad externa, incertidumbre y observabilidad. `NADR-F17BIS-06` permanece PROPOSED y no aporta obligación FROZEN por analogía.

## 5. REGLAS NORMATIVAS (RFC 2119)

**Las siguientes diez reglas RFC 2119 constituyen el contrato normativo aprobado por el Architecture Board y FROZEN v1.0.0 de esta capacidad.**

### 5.1 Intención lingüística y petición efectiva

1. Toda operación de inferencia perteneciente al producto PPPR inicial **MUST** conservar una intención lingüística explícita, verificable y atribuible a la generación: origen inglés y destino español. La intención **MUST NOT** depender exclusivamente de supuestos implícitos sobre el idioma del proveedor, el prompt o el entorno.

2. La petición efectiva destinada a producir traducción **MUST** expresar inequívocamente la intención EN→ES aprobada y **MUST** corresponder a la intención de generación. Una referencia textual a un idioma «configurado», un factor de expansión estimado o una configuración sin vínculo comprobable con la petición **MUST NOT** sustituir esa expresión.

### 5.2 Coherencia del backend y del fallback

3. Un backend/modelo de inferencia **MUST** contar con evidencia suficiente de vigencia, disponibilidad aplicable y compatibilidad con las capacidades requeridas por la operación antes de ser declarado admisible. Un identificador conocido pero retirado, o una capacidad no acreditada, **MUST NOT** tratarse como disponibilidad demostrada.

4. Toda selección alternativa o decisión de fallback **MUST** corresponder al backend/modelo realmente incorporado en la petición efectiva, incluidos los límites y capacidades utilizados para admitirla. Toda conmutación efectiva **MUST** reevaluar, antes del despacho, las precondiciones aplicables de capacidad, autorización de egress y presupuesto respecto del backend/modelo finalmente seleccionado. Una autorización o admisión anterior **MUST NOT** transferirse automáticamente a otra selección; una conmutación meramente lógica sin alternativa acreditada **MUST NOT** admitirse.

### 5.3 Admisión por capacidad, medición y presupuesto

5. Antes de declarar admisible una petición, la evaluación de capacidad **MUST** verificar todos los límites aplicables al modelo y a la petición efectiva, incluidos, cuando existan, límites independientes de entrada, salida y ventana total, y sus componentes relevantes de instrucciones, contenido, contexto y reserva de salida. La satisfacción de un agregado o subconjunto de componentes **MUST NOT** presentarse como cumplimiento de los demás límites aplicables.

6. La medición directa o estimación conservadora utilizada para admitir una petición **MUST** estar suficientemente acreditada para el modelo seleccionado, los límites aplicables y la representación efectivamente enviada. Una estimación conservadora **MAY** sustituir el conteo exacto cuando su suficiencia esté demostrada; no se requiere identidad byte a byte entre esquema lógico y solicitud física, pero las diferencias y limitaciones **MUST** ser consideradas y **MUST NOT** encubrir una cobertura insuficiente de la petición transmitida.

7. Toda petición que implique transmisión de contenido a un proveedor externo **MUST** respetar previamente la autorización aplicable de destino, finalidad, tratamiento, retención, posible uso para entrenamiento y alcance de datos, conforme al ADR Maestro DC-03. La existencia de un adaptador, configuración o proveedor disponible **MUST NOT** considerarse autorización de egress.

8. Toda petición sujeta a coste **MUST** contar previamente con autorización presupuestaria aplicable y condiciones de admisión compatibles con ella. Las cuotas técnicas, las estimaciones de tokens y las guardas posteriores a la respuesta **MUST NOT** presentarse por sí solas como presupuesto monetario aprobado ni como cota máxima de gasto efectivamente impuesta.

### 5.4 Atribución de decisiones y rechazo seguro

9. La decisión de admisión **MUST** ser atribuible a la generación correspondiente y permitir comprobar la relación entre intención lingüística, backend/modelo efectivo, capacidad declarada, estimación utilizada, autorización aplicable y petición despachada. Esta trazabilidad **MUST NOT** confundir identidad de generación con identidad del intento operacional ni requerir exposición innecesaria del contenido protegido.

10. Una petición que no satisfaga todas las precondiciones obligatorias de idioma, compatibilidad, selección efectiva, límites aplicables, medición suficiente, presupuesto o autorización **MUST NOT** ser despachada. Su rechazo **MUST** producirse antes del inicio del efecto externo y **MUST** conservar una causa distinguible. Los efectos que ya hayan podido iniciarse permanecen bajo la semántica de incertidumbre y recuperación F18; este NADR **MUST NOT** tratar su incertidumbre como rechazo pre-efecto demostrado ni autorizar reintentos ciegos.

## 6. CONSECUENCIAS ARQUITECTÓNICAS

- La intención EN→ES deja de depender de una instrucción ambigua o de la configuración supuesta del proveedor.
- La selección lógica y la petición efectiva quedan sujetas a un contrato verificable; cada conmutación exige nueva admisión para el destino real.
- La admisión contempla límites independientes aplicables, no solo una suma agregada, y puede sustentarse en estimación conservadora suficientemente acreditada.
- El fallback deja de representar capacidad disponible cuando no hay alternativa compatible, autorizada y acreditada.
- La autorización de egress y gasto permanece como precondición, no como efecto de configurar un proveedor.
- La falta de cualquier precondición obligatoria impide **iniciar** el despacho, no únicamente etiquetarlo como inadmisible.
- La trazabilidad permite diferenciar decisiones locales de admisión, efectos externos inciertos y resultados científicos, sin crear nuevas taxonomías de estado ni mecanismos de recuperación.
- La selección técnica concreta queda reservada al Execution Plan bajo las autorizaciones arquitectónicas correspondientes.

## 7. VERIFICACIÓN Y VALIDACIÓN

**Estado: NOT_RUN.** Los controles siguientes son falsadores propuestos para planificación y ejecución posteriores, cuando exista autorización. No se efectuaron llamadas comerciales, pruebas de API ni mediciones físicas de gasto.

**Verification — estática/mecánica**

- Comprobar que la intención EN→ES es atribuible a la generación y llega a la representación realmente enviada.
- Comprobar que una selección alternativa actualiza el modelo efectivo y provoca una **reevaluación completa** de límites de capacidad, autorización de egress y presupuesto para el destino final antes del despacho.
- Comprobar que cada límite independiente aplicable (entrada, salida y total, cuando corresponda) se evalúa respecto de la petición realmente contemplada; no dar por satisfechos todos los límites por comprobar solo el total.
- Comprobar que la medición directa o estimación conservadora cubre suficientemente la representación enviada y el modelo seleccionado; no exigir identidad byte a byte con el esquema lógico ni aceptar equivalencia supuesta.
- Comprobar que la autorización de egress y gasto no se infiere de la mera configuración.
- Comprobar que ninguna rama que rechace por falta de precondiciones obligatorias pueda iniciar el efecto externo; preservar la distinción entre rechazo pre-despacho y resultado incierto post-despacho gobernado por F18.

**Validation — dinámica/comportamental**

| Falsador propuesto | Resultado exigido |
|---|---|
| Generación con destino español ausente en la petición | No despachar; rechazo pre-efecto atribuible a la precondición lingüística. |
| Instrucción «idioma configurado» sin destino identificable | No considerarla intención lingüística suficiente ni permitir despacho. |
| Modelo configurado retirado o sin compatibilidad acreditada | Rechazo pre-despacho o selección alternativa autorizada y nuevamente admitida. |
| Fallback lógico conserva físicamente el modelo primario | No despachar como alternativa válida; rechazo por incoherencia de selección. |
| Fallback cambia de modelo, ventana o proveedor, pero reutiliza presupuesto o autorización de egress del anterior | Nueva admisión obligatoria de capacidad, egress y presupuesto para el seleccionado; bloqueo si falla alguna. |
| Núcleo dentro de ventana alternativa, total con contexto fuera de ventana | Rechazo pre-despacho; no admitir por haber comprobado solo el núcleo. |
| Total dentro de ventana, pero entrada o reserva de salida excede un límite independiente aplicable | Rechazo pre-despacho aunque la suma agregada quepa. |
| Estimación conservadora acreditada cubre la representación física y los límites relevantes | Puede sustentar admisión sin conteo exacto; no exigir identidad byte a byte entre representaciones. |
| Estimador incompatible o sin suficiencia demostrada para la petición efectiva | No despachar basándose en compatibilidad supuesta. |
| Proveedor disponible sin autorización de egress para los datos | Bloqueo anterior a toda transmisión. |
| Cuotas RPM/TPM disponibles pero presupuesto comercial no aprobado | No despachar una petición con coste no autorizado; cuotas no sustituyen presupuesto. |
| Guarda de tamaño post-respuesta usada como supuesto tope monetario | No aceptarla como prueba de autorización o límite monetario pre-efecto. |
| Precondición fallida pero existe rama alternativa que envía la petición | Falsador de R10: ninguna ruta de despacho puede sobrevivir al rechazo pre-efecto. |
| Efecto externo posiblemente iniciado antes de la pérdida de respuesta | No reclasificar como rechazo pre-efecto ni autorizar reintento ciego; aplicar semántica F18. |

Los escenarios de admisión pueden formalizarse mediante testigos sintéticos y dobles sin utilizar material privado. La evaluación comercial de un modelo real requiere aprobación específica de proveedor, datos, presupuesto, secretos y alcance.

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
|---|---|
| ADR Maestro PPPR FROZEN | **Autoridad constitucional:** DC-02 fija EN→ES; DC-03 delimita inferencia, egress, presupuesto, coherencia y rechazo seguro. |
| HITO PPPR.0.1 FROZEN | **Evidencia:** `GAP-0.1-01`, `E-0.1-002/023`, solapados causalmente con la discrepancia de fallback de PPPR.0.4. |
| HITO PPPR.0.4 FROZEN | **Evidencia principal:** `GAP-0.4-01…04`, `E-0.4-001…021` según sus respectivos ámbitos y severidades. |
| HITO PPPR.0.9 FROZEN | **Reconciliación:** confirma que los dos GAP de fallback representan una sola causa y preserva los demás núcleos. |
| `NADR-F17BIS-06` PROPOSED | **Antecedente no vinculante:** estimación de tokens; no constituye norma FROZEN ni se adopta automáticamente. |
| `NADR-F17BIS-08` FROZEN | **Frontera compatible:** coordinación de cuotas y circuitos, sin sustituir la admisión contractual de esta capacidad. |
| `NADR-F18-03` FROZEN | **Autoridad operacional:** preautoridad, efectos externos inciertos, recuperación y prohibición de reintentos ciegos. |
| `NADR-F18-05` FROZEN | **Observabilidad:** correlación y exposición de intentos, sin redefinir aquí su taxonomía ni persistencia. |
| `NADR-FPPPR-01` FROZEN | **Frontera científica:** legitimidad de afirmaciones de conformidad del PDF final EN→ES, no coherencia del request G3. |
| `NADR-FPPPR-02` FROZEN | **Frontera de reconstrucción:** fidelidad representacional del contenido y la jerarquía en G5. |
| Futuro `PHASE_PPPR_EXECUTION_PLAN.md` | **Destino de materialización:** selección autorizada de proveedores/modelos, mecanismos, falsadores y presupuestos aplicables, sin introducir decisiones constitucionales nuevas. |

Las relaciones de ámbito o contraste no constituyen dependencias normativas recíprocas nuevas. El cotejo de suficiencia y clasificación de relaciones conforme a `4_METH_NADR.md` §8 quedó aprobado por el Architecture Board para este FROZEN: se reconocen los contratos F17-BIS/F18 y NADR-FPPPR-01/02 en sus fronteras vigentes, sin declarar nuevas dependencias directas ni editar documentos FROZEN para simular reciprocidad.

## 9. FRONTERA NORMATIVA (QUÉ NO GOBIERNA ESTE NADR)

- **No selecciona** Groq, Gemini, otro proveedor, un modelo físico ni su sustituto comercial.
- **No decide** nuevos destinos de egress, políticas de privacidad, tratamiento de documentos, retención o permisos de entrenamiento; el ADR Maestro DC-03 conserva esa autoridad.
- **No impone** un importe, tarifa, tokenizador, fórmula específica de presupuesto, valor de ventana o límite monetario universal.
- **No gobierna** coordinación de cuotas, circuit breaking ni ejecución distribuida regulados por contratos existentes compatibles.
- **No gobierna** leases, intentos, reintentos, UNKNOWN ni recuperación de efectos externos bajo F18.
- **No gobierna** la fórmula de identidad científica o generación traducida; el ADR Maestro DC-04 y los contratos existentes conservan sus ámbitos.
- **No gobierna** la reconstrucción G5 ni la preservación representacional cubierta por `NADR-FPPPR-02`.
- **No certifica** fidelidad lingüística, integridad STEM o calidad científica del PDF final; esa atribución se rige por `NADR-FPPPR-01`.
- **No autoriza** gasto comercial, transmisión de corpus privados, pruebas físicas, implementación o integración a `main`.
- **No prescribe** clases, funciones, SDK, arquitectura de proveedor, código, tareas ni Definition of Done.

**Nota de gobernanza:** las diez reglas constituyen el contrato normativo FROZEN de esta capacidad. La aprobación no selecciona ni acredita proveedor/modelo, no concede autorización de egress o presupuesto, no repara GAP, no implica ejecución de pruebas ni constituye certificación científica del producto. La implementación se somete al futuro Execution Plan y a permisos independientes.
