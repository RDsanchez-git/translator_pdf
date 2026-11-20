# ARCHITECTURE DECISION RECORD (ADR)
## ADR PPPR: PDF→PDF Product Readiness — Traducción científica EN→ES (ADR Maestro)

* **Estado:** PROPOSED
* **Fecha de Emisión Original:** 2026-11-20
* **Fecha de Congelamiento:** —
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** PPPR — unidad transversal de gobernanza de nivel Maestro **aprobada por el Board según comunicación del owner de 2026-11-20** (DC-01). No introduce fase numerada del ROADMAP; `ADR_PPPR_MASTER.md` en `docs/architecture/adr/pdf-pdf-product-readiness/ADR/` es especialización documental autorizada **para PPPR exclusivamente**. El ADR integral sigue PROPOSED hasta cierre del DC Log y checklist.
* **Módulos Afectados:** CLI/ingesta, OCR y perfiles documentales, AST/normalización/chunking, G3 e inferencia, autoridad W06/FSM/SQLite, G5/ensamblado, empaquetado local, tests/CI y certificación de producto.
* **Aprobación Architecture Board:** **PENDIENTE DE APROBACIÓN INTEGRAL / FROZEN**. DC-01 y políticas DC-03/05/08/09/12 ratificadas según comunicación del owner el **2026-11-20**; las demás disposiciones de §8 se adoptan en este borrador **por mandato explícito de decisión técnica del owner** en esta conversación. Sin acta externa independiente ni autorización final para FROZEN o merge acreditadas.
* **Derivado de:** ROADMAP_ARQUITECTONICO_LP v3.0 (Etapa I: nacimiento del traductor científico; Etapa II: madurez operativa), PROJECT_SCOPE.md, ENGINEERING_PRINCIPLES.md, convergencia D-1/D-2 y PPPR.0.1–0.9 FROZEN.
* **Supersede:** — (primera propuesta PPPR; no reemplaza ADR F18 ni ADR F17-BIS)

## 1. CONTEXTO Y JUSTIFICACIÓN

El ROADMAP v3.0 describe un producto local de un nodo que traduce documentos científicos complejos preservando contenido técnico, topología y posibilidad de operación. Las capacidades del motor, el runtime local y la madurez de producto son horizontes distintos; ningún hito histórico de convergencia fake o regresión de extracción equivale a una traducción EN→ES científicamente acreditada.

La convergencia D-1/D-2 seleccionó una ruta operativa única **CLI → OCR → G3 → G5 → PDF**, apoyada por contratos de estado y testigos técnicos delimitados. El owner definió la meta inicial **exclusivamente EN→ES** y la necesidad de renovar la inferencia obsoleta, **sin** aprobar aquí proveedor, modelo, implementación ni modalidad comercial. La iniciativa PPPR reúne evidencia transversal para decidir las capacidades mínimas que faltan antes de poder acreditar esa meta.

**Relación formal con el ROADMAP y autoridad de DC-01:** PPPR no figura como fase numerada en ROADMAP v3.0. El Board **aprobó**, según comunicación del owner de **2026-11-20**, su tratamiento excepcional como **unidad transversal de gobernanza de nivel Maestro**, con nombre/hogar documental específicos exclusivamente para PPPR. No se modifica ROADMAP, no se reabre Fase 18 ni se establece precedente automático. **La constitución de la unidad queda resuelta (DC-01); el ADR como paquete sigue PROPOSED** aunque su §8 ya dispone las 12 DC: faltan verificación final del checklist y aprobación integral del Architecture Board para FROZEN.

## 2. PROBLEMA ARQUITECTÓNICO Y ESTADO OBSERVADO

La auditoría forense PPPR.0.1–0.9, vinculada a `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`, identifica las siguientes incertidumbres **sin prescribir soluciones**:

1. **Contrato EN→ES y proveedor:** G3 declara un modelo obsoleto, no transporta destino español en el contrato inspeccionado y presenta conmutación de fallback lógica sin materialización física; `GAP-0.4-01/02/03/04`, `GAP-0.1-01`, `E-0.9-003/004/005`. El par `0.1-01 ↔ 0.4-02` tiene una causa compartida, no dos remediaciones independientes.
2. **Identidad y continuidad documental:** perfilado usa muestreo sin página real y ancho `612.0`; la firma AST pierde semántica jerárquica y no asegura canonización Unicode de su pre-image; `GAP-0.2-01/02`, `GAP-0.3-01/02`, `E-0.9-006…009/025…028`. Los contratos de `NADR-F17BIS-03` y `-16` requieren examen de **sujeto y propósito** para identidad de generación (DQ-0.9-01).
3. **Autoridad y efectos externos:** la cuarentena UNKNOWN no tiene escalamiento conectado, el lease se comprueba antes de una espera y el sweeper Compose mezcla estados/reporting; `GAP-0.5-01/02/03`, `E-0.9-011…013`. No se probó doble cobro o incidente remoto.
4. **Conservación, política lingüística y salida:** G5 incorpora CODE/TABLE como TeX literal y pierde niveles de HEADING (`GAP-0.6-01/02`, `E-0.9-010`). PPPR.0.3 `E-0.3-013/018` y `DC-0.3-01` muestran que los encabezados observados pueden llegar como PRESERVE **sin traducción**, pese a una estrategia TRANSLATE; **en la auditoría todavía faltaba decidir si traducirlos o preservarlos** (decisión constitucional posterior DC-05 registrada en §8). `GAP-0.2-02 → E-0.6-028` es propagación geométrica upstream. El defecto jerárquico de firma AST y el de render son **distintos**.
5. **Operación y custodia:** el host/Compose efectivo, la inyección de secretos y la modalidad comercial no fueron acreditados; PPPR.0.7 §16 muestra admisión CLI **dentro del contenedor con proveedor fake**, no una CLI Windows con puente validado ni una modalidad comercial aprobada. Sus dos **candidatos NO CONFIRMADOS** no son nuevos P1 (`E-0.9-015/022`).
6. **Atribución científica:** Continuous Verification evalúa **PDF→AST**, no calidad del **PDF traducido**. C2/T07 utilizaron proveedor fake. Los subtools históricos de preflight/post-run tienen observaciones locales, no un gate producto demostrado; `E-0.8-006/026/046/047`, `E-0.9-016/018`. El corpus canónico registra 21 documentos y solo seis PDFs en Git; 15 originales requieren custodia autorizada (issue #34, `E-0.9-017`).

### 2.1 Architectural Outcome de la compuerta de auditoría

**Outcome cerrado por evidencia documental:** los nueve HITOs PPPR.0.1–0.9 están FROZEN en `pdf-pdf-product-readiness@2e932a702780164dfc64b6cbb12d1ddabe92502a`; PPPR.0.9 §14 reconcilia **14 GAP-IDs P1 OPEN heredados** en **13 núcleos causales preliminares** (un par duplicado confirmado). Consta **270 E-IDs de PPPR.0.1–0.8 más 30 E-IDs P2 propios de PPPR.0.9**; **37 DQ-IDs heredados (2 resueltos en origen, 35 diferidos) más DQ-0.9-01**, y **22 DC-IDs heredados sin soluciones aprobadas por 0.9**. GAP-0.6-03 está retirado y los dos candidatos de 0.7 no se suman como OPEN.

**La compuerta auditora queda cerrada; la compuerta de producto no.** No hay testigo autorizado de fidelidad lingüística, matemática y visual EN→ES de extremo a extremo, ni evidencia física de corpus completo, proveedor real, coste o host final. `PRODUCT_READINESS=PASS` **no** está acreditado. F17-BIS constituye antecedente histórico, con NADRs aplicables **solo cuando el contrato y sujeto compatibles se demuestran**, no autoridad automática de la ruta D-1/D-2. Estos son los límites del outcome, no defectos nuevos ni aprobación de reparaciones.

## 3. SEPARACIÓN DE CONCEPTOS FUNDAMENTALES

Las decisiones siguientes preservan dimensiones **ortogonales**; ninguna implica la otra:

1. **Ruta seleccionada ≠ resultado conforme:** continuidad CLI→OCR→G3→G5 y PDF físicamente emitido no implican traducción científica válida.
2. **Extracción ≠ traducción ≠ ensamblado:** equivalencia topológica de AST no implica terminología EN→ES correcta ni conservación visual del PDF final.
3. **Identidad semántica ≠ identidad de oráculo ≠ identidad operacional:** hashes distintos pueden tener propósitos distintos; usar una firma como identificador durable no demuestra que capture toda mutación relevante.
4. **Conservación de bytes STEM ≠ suficiencia de significado:** proteger delimitadores o texto literal no demuestra que ecuaciones, relaciones y figuras estén correctamente representadas en la salida.
5. **Estado FSM ≠ efecto remoto ≠ publicación:** un estado local terminal no acredita llamada al proveedor exactamente una vez ni publicación durable y científicamente válida.
6. **Configuración versionada ≠ despliegue efectivo:** Compose y testigos de laboratorio no acreditan host, secretos, privacidad, costes ni política comercial.
7. **Norma heredada FROZEN ≠ obligación universal:** autoridad se determina por sujeto, ámbito y compatibilidad con D-1/D-2 y decisiones F18 posteriores.
8. **Auditoría FROZEN ≠ aprobación normativa ≠ aceptación de producto:** evidencias, decisiones, reglas y validación física viven en etapas distintas.

## 4. ALCANCE Y NO-OBJETIVOS (OUT OF SCOPE)

**Capacidades in-scope de la unidad transversal PPPR ratificada; el presente ADR integral sigue PROPOSED:** continuidad observable de la ruta única PDF→PDF; traducción explícita inicialmente EN→ES con inferencia vigente; integridad estructural y matemática desde documento fuente hasta salida; identidad coherente con consumidores reales; autoridad/fail-closed ante efectos, pausas y recuperación; salida PDF con reporte atribuible; operación local según modalidad aprobada; y evidencia técnica/científica diferenciada por sujeto, privacidad y custodia.

**No-objetivos y dueño documental/temporal explícito:**

| Fuera de alcance del ADR Maestro | Dueño / destino |
|---|---|
| Elegir implementación, clase, patrón de conmutación, proveedor específico, cifra de presupuesto, memoria o algoritmo Unicode | **Execution Plan** solo para evaluación y selección concreta **dentro de una frontera arquitectónica de datos/proveedor previamente aprobada**; una decisión que altere egress, privacidad, retención, tratamiento del documento o política de inferencia requiere autoridad arquitectónica antes del plan. NADR solo si hace falta una regla testable |
| Modificar pipelines o construir runtime, workers, cachés, servicio, CI o motor de PDF nuevo | **`PHASE_PPPR_EXECUTION_PLAN.md`** para secuencia y límites aprobados; implementación solo bajo PRs de código posteriores independientes, no en este Maestro |
| Reentrenar OCR o LLM, ampliar producto a multidioma, UI compleja o infraestructura distribuida | **`ROADMAP_ARQUITECTONICO_LP.md` y `PROJECT_SCOPE.md`**, exclusivamente mediante una decisión formal futura del Board/owner; **ninguna fase nueva se asigna aquí** |
| Establecer métricas, umbrales científicos o particiones sin testigos independientes | **etapa normativa PPPR (§8.1, metodología general §6.1 y `4_METH_NADR.md`)** para identificar garantías vigentes y obligaciones verificables faltantes; **PHASE_PPPR_EXECUTION_PLAN.md** para evaluación, muestreo y falsadores autorizados. **No** abrir ADR científico de subfase por defecto ni trasladar autoridad del oráculo al plan |
| Obtener, reemplazar o alterar los 15 PDFs privados, GT, hashes o corpus canónico | **Owner/issue #34** y posterior protocolo de custodia/testigo autorizado |
| Atribuir certificación PDF→PDF a CV de extracción, laboratorio fake o subtools heredados | **Este Maestro §8 DC-09/11** delimita la no equivalencia; **etapa normativa PPPR (§8.1)** determinará la cobertura de reglas verificables del PDF EN→ES y **`PHASE_PPPR_EXECUTION_PLAN.md`** de testigos autorizados |
| Reabrir, superseder o imponer íntegramente F17-BIS/F18 por analogía histórica | **ADRs F17-BIS/F18 y sus NADR FROZEN** mantienen autoridad en su sujeto; cualquier sustitución exige **ADR sucesor de la unidad afectada** conforme a la metodología general, no este Maestro PPPR |
| Definir programación, responsables personales, batches, story points, rollout o rollback | **Execution Plan único** de esta iniciativa, después de normas aprobadas |
| Crear registros Exit Review/Findings por anticipación | **`PHASE_PPPR_EXECUTION_PLAN.md` y sus gates de revisión/Findings** conforme a metodología general §§6.5–6.6, cuando exista implementación aprobada; no se crean ahora |
| Admitir un PDF `DEGRADED` como **resultado final conforme o certificado** del producto inicial | **DC-12 ratificada por Board** según comunicación del owner (2026-11-20): resultado parcial no conforme; artefacto parcial inequívocamente etiquetado puede usarse para diagnóstico/recuperación sin certificación. Una admisión futura como resultado conforme exige **ADR sucesor o ADR de subfase autorizado**, contrato y testigos; no se prohíbe diagnóstico por esta política |

## 5. INVARIANTES Y REGLAS DE GOBERNANZA

**Invariantes constitucionales (parcialmente ratificadas como políticas de alcance DC-03/05/08/09/12; aprobación integral del Maestro aún pendiente; no son reglas RFC-2119 nuevas):**

1. **Unidad de ruta:** existe un solo flujo productivo soportado para el alcance inicial; rutas históricas o herramientas de laboratorio no se convierten en vías alternativas por la puerta de atrás.
2. **Intención lingüística explícita:** la entrada en inglés y el destino español forman parte del significado verificable de una generación, sin presuponer producto multilingüe.
3. **Preservación STEM y linaje:** la traducción y reconstrucción no degradan silenciosamente fórmulas, código, identificadores, tablas, jerarquía o atribución documental.
4. **Identidades diferenciadas por consumidor (DC-04 resuelta en §8):** AST fuente, generación traducida, intento operacional y referencia/oráculo científico tienen propósitos distintos. La identidad de generación distingue idioma, contrato y variaciones semánticas relevantes; cambios incidentales de scheduling, timeouts y concurrencia no alteran por sí mismos la identidad científica. No se impone hash universal, algoritmo o pre-image desde el Maestro.
5. **Inferencia compatible, acotada y con custodia (DC-03 resuelta en §8):** el alcance EN→ES contempla un backend vigente/autorizado y coherencia entre modelo realmente invocado, ventana total, presupuesto y petición. El tránsito de contenido a terceros solo pertenece al perímetro de datos/egress aceptado expresamente por el owner, con finalidades, tratamiento y retención documentados; si falta autorización o alternativa compatible, el resultado es fallo explícito. Ningún modelo se escoge aquí.
6. **Autoridad al efecto:** inferencia y publicación quedan sujetas a autoridad vigente, manejo explícito de estados inciertos y evitación de segundos efectos remotos ciegos.
7. **Degradación explícita:** un resultado parcial o fallido conserva su condición y no se presenta como PDF final íntegro/certificado. **DC-12 ratificada:** `DEGRADED` no se acepta como resultado conforme inicial; no impide artefactos parciales inequívocamente etiquetados para diagnóstico/recuperación, sin aprobación automática de su productor.
8. **Sujeto-oráculo-resultado inseparables:** el **PDF científico final EN→ES** es el sujeto de aceptación del producto inicial; cada afirmación de calidad tiene evidencia independiente y límites reproducibles. Extracción PDF→AST, técnica fake y ciencia del PDF final no se colapsan.
9. **Custodia, privacidad y costo:** ningún testigo científico o proveedor comercial se interpreta como autorizado por la sola existencia de herramientas, configuraciones o documentos.

**Gobernanza del proceso:** Audit First, Reuse Before Invent, YAGNI y minimización de nuevos contratos. Las 14 GAP-IDs heredadas conservan su autoridad original, aunque dos compartan causa. Las reglas de capacidad se expresarán, si corresponde, en NADR aplicables, sin duplicar F18 ni importar F17-BIS íntegro. La falta de evidencia no se transforma en mecanismo por preferencia.

## 6. HOJA DE RUTA DE SUB-FASES GOBERNADAS

**Árbol de capacidades y dependencia lógica propuesta**, sin asignar fases numeradas del ROADMAP, fechas, waves ni trabajos técnicos:

```text
PPPR (unidad transversal de gobernanza ratificada; ADR integral PROPOSED)
 ├─ Delimitación de contrato de producto y garantía EN→ES
 │   ├─ Identidad y conservación de entrada/documento
 │   └─ Sujeto y oráculos de aceptación técnica/científica
 ├─ Continuidad de generación confiable
 │   ├─ Inferencia EN→ES verificable y presupuestada
 │   └─ Autoridad de efectos, incertidumbre y recuperación
 ├─ Reconstrucción STEM y salida atribuible
 │   └─ Fidelidad estructural, representación y estados de salida
 └─ Modalidad de operación y evidencia de preparación del producto
     └─ Seguridad local, custodia y gates acordes al sujeto
```

El orden refleja **dependencias epistemológicas y de capacidades**, no obliga a implementar en una secuencia equivalente ni a crear un ADR de Fase para cada rama. Un ADR de subfase solo tendrá lugar si existe una decisión autónoma de complejidad suficiente, bajo `3_METH_ADR_SUBPHASES.md` y sin reabrir el Maestro.

**Cláusula de Relación con el Execution Plan (obligatoria):** este ADR define **qué capacidades y dependencias lógicas** sostienen el objetivo; **no** ordena tareas, adjudica prioridades ejecutivas, reparaciones, tecnologías, coste o calendario. La etapa normativa PPPR posterior al Maestro comprobará normas FROZEN y decidirá reglas adicionales únicamente por necesidad, sin número, identidad ni partición NADR predeterminados. El **Execution Plan único**, posterior a las normas suficientes y aprobadas, será la fuente de tareas, dependencias operativas, aceptación, presupuesto y rollback, con trazabilidad a decisiones, reglas y E/GAP-IDs de origen. Ninguna parte de este §6 autoriza implementación.

## 7. ESPECIFICACIÓN DE LA COMPUERTA DE AUDITORÍA (FASE 0)

**Historical Note — compuerta ya completada:** la auditoría de esta iniciativa transversal quedó documentada por PPPR.0.1–0.9 FROZEN en la rama general antes de la emisión de este ADR. Esta sección conserva el **contrato y resultado histórico** de esa compuerta, sin volver a prescribir otra campaña.

**Blindaje aplicado:** `NO CODE / NO I/O` para las pasadas documentales; no pytest/CI, Docker, Tectonic, proveedor de pago, lectura o transmisión de corpus privado, mutación de SQLite/GT/manifests. Las no-verificaciones se registraron en Deferred Questions, sin fabricar PASS.

**Entradas y actividades acreditadas por HITOs:** fuentes de ruta/consumidores (0.1), ingesta/perfiles (0.2), AST/identidad (0.3), G3/modelo/idioma/presupuestos (0.4), W06/FSM/SQLite (0.5), G5/TeX (0.6), host/Compose (0.7), tests/corpus/certificación (0.8) y cruces causales/autoridad (0.9). Versiones y E-IDs vinculantes residen en `00-foundation/`; no se transcriben aquí.

**Entregables de auditoría ya trazables, sin documentación paralela:** **Gap Matrix** incorporada a HITO_PPPR.0.9 §14; **Contract Map** distribuido en HITO_PPPR.0.1 §6.1 y HITO_PPPR.0.9 §§5/7; **Evidence Register** materializado como E-ID estables en PPPR.0.1–0.9 (reconciliación PPPR.0.9 §10); **DC y DQ** transferidas individualmente en PPPR.0.9 §16. El cierre documentado **no** certifica resultado físico y mantiene issue #34.

**Resultado histórico de compuerta:** auditoría FROZEN, sin nuevo P1 global, con GAP-IDs previos abiertos y decisiones **entonces pendientes** transferidas a este ADR. Su disposición documental posterior vive en §8; no altera retrospectivamente el resultado forense. Una nueva prueba empírica exige sujeto/oráculo y autorización propios.

## 8. REGISTRO DE DECISIONES CANDIDATAS (DC LOG)

**Regla de cierre:** conforme a `2_METH_ADR_MASTER.md` v1.0.1 §5, un DC se resuelve con evidencia/decisión de alcance justificada o se difiere **terminalmente** a un artefacto/fase identificable. Resolver **la autoridad del contrato** no supone haber corregido código ni verificado físicamente los GAP. Se conservan los **22 DC heredados**, **37 DQ heredadas más DQ-0.9-01** y sus destinos individuales en HITO PPPR.0.9 §16; este Maestro consolida **12 DC de nivel constitucional**, sin borrar IDs forenses.

**Procedencia de autoridad:** DC-01 y las políticas DC-03/05/08/09/12 fueron aprobadas por comunicación del owner el **2026-11-20**. En esta revisión el owner pidió explícitamente «como board que eres, revisa y decide»; las restantes resoluciones se registran como **decisiones de gobernanza técnica adoptadas por ese mandato dentro del borrador**. La conversación es su referencia de procedencia; **no se afirma acta externa, revisión independiente del Board ni aprobación integral del ADR**. La decisión final de FROZEN y su fecha permanecen separadas en el header.

| DC | Pregunta y evidencia de origen | Resolución de alcance / política | Destino de obligaciones subordinadas, sujeto a validación de cierre §5 |
|---|---|---|---|
| **DC-01** | ¿Quién gobierna PPPR y con qué nomenclatura? HITO 0.1 §21.2; HITO 0.9 §21; ROADMAP v3.0 | **RESUELTA — Opción A:** PPPR es unidad transversal de gobernanza de nivel Maestro, no fase numerada; `ADR_PPPR_MASTER.md` en `docs/architecture/adr/pdf-pdf-product-readiness/ADR/` es excepción propia de PPPR. No modifica ROADMAP ni F18. | **Este ADR §1 y header**. La autoridad constitucional comunicada por el owner el 2026-11-20 es distinta de aprobación final FROZEN. |
| **DC-02** | ¿Cómo se garantiza idioma EN→ES en la generación? DC-0.4-02; GAP-0.4-03; E-0.9-005 | **RESUELTA EN ALCANCE:** únicamente fuente inglesa y destino español para producto inicial; intención de lengua forma parte del contrato observable de generación. Sin expansión multilingüe por implicación. | **Este ADR §§4–5** para la decisión; `PHASE_PPPR_EXECUTION_PLAN.md` para expresión física de `source=en,target=es`, propagación y testigos conforme al contrato. GAP-0.4-03 sigue OPEN. |
| **DC-03** | ¿Qué inferencia y egress están autorizados? GAP-0.4-01/02/04 y GAP-0.1-01; DC-0.4-01/03/04; HITO 0.7 DQ-01/04 | **RESUELTA EN FRONTERA DE PRODUCTO — Opción B acotada:** ninguna transmisión externa de PDF/prompt o material confidencial sin **autorización explícita del owner**, con destino, finalidad, retención, posible uso para entrenamiento y garantías del proveedor documentados y aceptados. Se excluye el uso de corpus/GT privado o secretos como payload comercial sin autorización separada. Inferencia EN→ES vigente, capaz de respetar formato/STEM y ventana total; presupuesto autorizado antes de incurrir en coste; modelo físico y fallback coherentes, alternativa no acreditada implica rechazo/fail-closed. No se aprueba proveedor ni política comercial concreta. | **Este ADR §§4–5/8** fija la frontera; **`PHASE_PPPR_EXECUTION_PLAN.md`** solo compara/selecciona proveedor/modelo **dentro** de ella y con permisos efectivos. Una alternativa que cambie egress, tratamiento de datos, política de fallback o modalidad requiere **nueva decisión de autoridad arquitectónica previa**, no elección del plan; ADR de subfase **no** necesario bajo la frontera aprobada. |
| **DC-04** | ¿Qué representa la identidad de generación? GAP-0.3-01/02; DQ-0.9-01; E-0.9-025…028 | **RESUELTA CONSTITUCIONALMENTE:** se distinguen **identidad semántica del AST fuente** (incluida jerarquía), **identidad de la generación traducida** (fuente + idioma/contrato y parámetros o versiones que puedan cambiar resultado), **identidad operacional del intento** y **referencia/oráculo científico**. Configuraciones incidentales (p. ej. timeout/scheduling) no cambian por sí mismas identidad semántica; una firma no sustituye oráculo. **No existe hash universal impuesto.** | **Este ADR §§3/5/8** fija propósitos; `NADR-F17BIS-03/16` y `NADR-F18-01` FROZEN se reutilizan **por ámbito compatible**; composición, canonización compatible STEM, invalidación y falsadores al **`PHASE_PPPR_EXECUTION_PLAN.md`** conforme a esos contratos. Si resulta una obligación verificable no cubierta, requerirá decisión normativa posterior **antes** de planificar esa parte. GAP-0.3-01/02 siguen OPEN; no se elige NFC/NFKC. |
| **DC-05** | ¿Se traducen HEADING y se conserva nivel? DC-0.3-01/02; E-0.3-013/018/019; GAP-0.6-02 | **RESUELTA:** títulos/encabezados de lenguaje natural se traducen EN→ES conservando jerarquía y función; no se modifican por ello fórmulas, identificadores ni código protegido. | **Este ADR §5** decide la política HEADING. En la **etapa normativa PPPR (§8.1)** se comprueba suficiencia de contratos FROZEN sobre jerarquía, clases protegidas y G5. Nuevas reglas solo si se demuestra vacío; **no se predetermina un NADR**. Pruebas físicas al Execution Plan único posterior. |
| **DC-06** | ¿Qué garantía arquitectónica exige la preservación del contenido literal CODE/TABLE frente a sintaxis TeX legítima? GAP-0.6-01; E-0.6-025; Scope §4 | **RESUELTA CONSTITUCIONALMENTE EN ESTE MAESTRO:** preservar CODE/TABLE literal sin interpretación involuntaria como TeX y conservar TeX/STEM legítimo, sin degradación silenciosa. Cotejo focal de 36 NADR F17-BIS/F18 no identificó regla FROZEN específica suficiente entre los examinados: NADR-F17BIS-09 FROZEN cubre aislamiento, NADR-F17BIS-06 permanece PROPOSED; no se afirma ausencia global ni se crea otro GAP. | **Cierre de esta DC: este ADR §§4–5/8**, sustentado por GAP-0.6-01 / E-0.6-025 y Scope §4. La **etapa normativa PPPR (§8.1; metodología general §6.1 y `4_METH_NADR.md`)** comprobará normas FROZEN compatibles y materializará las obligaciones verificables residuales, **sin reabrir la decisión constitucional ni predeterminar NADR**. Si aparece una decisión arquitectónica nueva fuera de esta garantía, exigirá autoridad previa. El Execution Plan único solo implementará contratos aprobados; GAP-0.6-01 permanece OPEN. |
| **DC-07** | ¿Qué autoridad gobierna UNKNOWN, lease y sweeper? GAP-0.5-01/02/03; DC-0.5-01…03 | **RESUELTA POR REUTILIZACIÓN:** `ADR_F18_2.md` v3.3.0 y `NADR-F18-03/04/05` FROZEN cubren preautoridad, estados inciertos, durabilidad/idempotencia local y observabilidad dentro de sus ámbitos. | **Contratos F18 citados** y `PHASE_PPPR_EXECUTION_PLAN.md` para falsadores de los tres GAP existentes; sin otro NADR ni garantías de power loss universal. |
| **DC-08** | ¿Qué modalidad local soportar inicialmente? PPPR.0.7 DC-01…04; E-0.9-015/022 | **RESUELTA:** objetivo inicial a validar CLI dentro del contenedor en **un nodo**, ruta D-1/D-2. Testigo fake C2 no certifica host comercial; no se incluye puente Windows→Docker en el producto inicial. | **Este ADR §§4–5**; `PHASE_PPPR_EXECUTION_PLAN.md` para secrets, mounts, red, preflight y host autorizado. Sin nuevo servicio o modo distribuido. |
| **DC-09** | ¿Cuál es el sujeto de aceptación científica de PPPR y qué dimensiones de garantía deben acreditarse independientemente? HITO 0.8 DC-01/02/04; E-0.9-016…019; issue #34 | **RESUELTA CONSTITUCIONALMENTE EN ESTE MAESTRO:** aceptar científicamente el **PDF final EN→ES**, con evidencia independiente de fidelidad lingüística, integridad STEM y estructura/visual, linaje y límites expresos. CV PDF→AST, 21 GT históricos topológicos, fake, `%PDF-` o `COMPLETED` no prueban aceptación bilingüe. No se demuestra ahora decisión arquitectónica autónoma que exija ADR de subfase, sin excluirlo ante evidencia nueva. | **Cierre de esta DC: este ADR §§3/5/8**, sustentado por HITO 0.8 y E-0.9-016…019. La **etapa normativa PPPR (§8.1; metodología general §6.1 y `4_METH_NADR.md`)** examinará reglas FROZEN compatibles (incluidas F17BIS-23/24, limitadas a sus sujetos), obligaciones testables de independencia/oráculos y eventual necesidad de normas adicionales **sin fijar número, identidad ni agrupación de NADR**. No se delega a un NADR ni al Execution Plan **crear silenciosamente un nuevo modelo de autoridad/confianza de oráculos**: si se descubre una decisión arquitectónica autónoma que exceda este Maestro, se decide con autoridad arquitectónica previa. La evaluación física requiere permiso owner/issue #34. |
| **DC-10** | ¿Quién custodia los 15 PDFs y habilita evaluación? HITO 0.8 DQ-01/03/DC-03; issue #34 | **DIFERIDA TERMINALMENTE POR AUTORIDAD IDENTIFICADA:** licencia, posesión, autorización y materialización de los 15 originales ausentes no se presumen, ni se alteran GT, SHA o manifest de la baseline. | **Owner + issue GitHub #34** para autorización, licencia y custodia. **Etapa normativa PPPR (§8.1)** para reglas de independencia que no estén cubiertas por normas FROZEN; sin asignar NADR por anticipación. Execution Plan único para testigos autorizados; issue abierto no equivale a PASS. |
| **DC-11** | ¿Se heredan subtools de certificación F17-BIS? E-0.8-026/046/047; DQ-0.8-06/07 | **RESUELTA POR NO ADOPCIÓN INICIAL:** preflight/post-run históricos **no** se declaran gates certificantes del PDF final EN→ES ni se reparan por reflejo; CV topológica de extracción mantiene su propósito. Una futura adopción exige nueva decisión de pertinencia de sujeto y caller, con evidencia, sin reescribir GT. | **Este ADR §8** resuelve no adopción inicial. **Etapa normativa PPPR (§8.1)** determina garantías aplicables de certificación PDF final, sin NADR predeterminado ni obligación de reparar herramientas no adoptadas. Execution Plan único solo para tooling autorizado. |
| **DC-12** | ¿Se admite salida DEGRADED? HITO 0.6 DC-0.6-04/DQ-0.6-04 | **RESUELTA:** PDF parcial/DEGRADED no es resultado final conforme o certificado; artefactos inequívocamente rotulados para diagnóstico/recuperación no quedan prohibidos, sin presuponer ruta productiva soportada. | **Este ADR §§4–5**. Cambio futuro de admisión comercial requiere ADR sucesor o decisión arquitectónica autónoma aprobada. |

### 8.1 Etapa normativa PPPR — sin cantidad, nombre ni partición NADR anticipados

**Responsabilidad normativa posterior, no diferimiento de las DC constitucionales:** la etapa normativa PPPR corresponde al tramo NADR de la secuencia de `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §6.1, regido por `4_METH_NADR.md`, posterior al ADR Maestro aprobado y anterior al Execution Plan. **No es una fase numerada nueva** del ROADMAP, ni se invoca como sustituto de una decisión arquitectónica abierta, ni autoriza documentos paralelos.

En esa etapa se examina para cada capacidad aprobada la suficiencia de reglas **FROZEN aplicables por estado, sujeto y frontera**, se identifica toda obligación verificable residual y se decide si basta reutilizar, si corresponde la sucesión normativa formal o si hace falta un NADR adicional. **El número, la identidad, el nombre y la agrupación de futuros NADR no se conocen ni se aprueban en este Maestro.** No confundir el examen focal de 36 NADR de F17-BIS/F18 con una autorización para crear una cantidad concreta.

**Capacidades para el contraste, no entregables prefijados:** preservación contextual G5 de CODE/TABLE y TeX legítimo (DC-05/06); aceptación independiente del PDF científico final EN→ES (DC-09/10/11); identidad por propósito (DC-04) y restantes obligaciones de producto. Reuse Before Invent y YAGNI; ninguna regla pendiente puede ser legislada por el Execution Plan.

**ADR de subfase:** no hay evidencia actual de una decisión arquitectónica autónoma que obligue a abrir uno. Esa constatación **no prohíbe** un ADR posterior si aparece una decisión real con suficiente autonomía, bajo `3_METH_ADR_SUBPHASES.md`.

### 8.2 Cierre constitucional del DC Log y gate de congelación

**Control de cierre §5 canónico:** **12/12 DC con decisión constitucional resuelta o disposición terminal explícita y trazable** en el presente §8. En particular, **DC-06 y DC-09 están resueltas aquí**, mediante garantías y límites propios de este ADR Maestro y evidencia referenciada en sus filas. No dependen de un futuro NADR individual ni de interpretar una «etapa normativa» como fase terminal de una decisión arquitectónica abierta.

**Materialización posterior (no parte abierta de DC-06/09):** la etapa normativa PPPR de §8.1 determinará qué obligaciones verificables ya satisfacen contratos FROZEN compatibles y cuáles requieren formalización. La cantidad, identidad y partición de eventuales NADR **no están decididas**. Si esa revisión descubre un nuevo asunto arquitectónico autónomo —por ejemplo, un cambio en la autoridad o el modelo de confianza de los oráculos— se deberá decidir con la autoridad correspondiente **antes** de crear reglas o tareas que lo presupongan; no se introducirá implícitamente por NADR o Execution Plan.

**Resultado de control 11:** **CUMPLE DOCUMENTALMENTE** por cierre de las preguntas constitucionales con fundamento forense y decisión del ámbito Maestro. Esto **no** implica que los GAP estén corregidos ni que exista certificación científica del PDF final.

**Gate separado:** el ADR permanece `PROPOSED`; falta **aprobación integral expresa del Architecture Board con fecha en el header**. El permiso de merge de PR #75 es otro acto distinto, aún no concedido.

## 9. ARCHITECTURE GOVERNANCE FRAMEWORK

**Cadena normativa interna PPPR, sin prefijar normas futuras:**

```text
ADR Maestro PPPR (capacidades; aún PROPOSED)
  → [ADR de subfase solo ante decisión arquitectónica autónoma]
  → etapa normativa PPPR: cotejo de NADR FROZEN compatibles por sujeto
    → NADR adicionales solo si son necesarios, sin número prefijado
  → Execution Plan único aprobado (posterior a normas necesarias)
  → Exit Review Evidence Log / Deferred Findings Register en sus gates
```

Los HITOs PPPR.0.1–0.9 de `00-foundation/` son **evidencia vinculante de entrada**, no nivel normativo de esa cadena. Los NADRs existentes F18 y los F17-BIS compatibles conservan su autoridad propia, sin reproducirse ni modificarse por este ADR. La jerarquía global se incorpora **por referencia** a `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §2, sin duplicar su pirámide. La plantilla y el ciclo de vida de este artefacto siguen `docs/architecture/2_METH_ADR_MASTER.md` v1.0.1 FROZEN.

**Interpretación de compatibilidad metodológica de esta revisión de gobernanza:** `2_METH_ADR_MASTER.md` v1.0.1 cita general **v1.4.0**, mientras `main@1d21cfe` contiene general **v1.3.0 FROZEN**. Se comprobó directamente que v1.3.0 contiene jerarquía §2, taxonomía §3.1/3.2, precedencia §6.1/6.2, convención §7.2 y anti-proliferación §8.4/§9. El header de la metodología Maestro declara que esas reglas citadas ya estaban presentes desde v1.3.0. **Decisión interpretativa:** aplicar la plantilla Maestro v1.0.1 FROZEN y las reglas compatibles efectivamente verificadas de general v1.3.0, **sin afirmar equivalencia global con el texto v1.4.0 no disponible, sin modificar FROZEN y sin crear metodología nueva**. La aprobación integral del ADR sigue pendiente aunque esta discrepancia editorial no exige, por lo observado, un proyecto normativo separado.

## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES

**Nivel A — gobernanza del ADR Maestro (condiciones de FROZEN):** header y diez secciones exigidas por `2_METH_ADR_MASTER.md` v1.0.1; §2 con E/GAP de auditoría FROZEN; distinciones §3, alcance §4 con destinos, invariantes §5 sin RFC-2119, §6 lógico sin tareas, §7 histórico y **§8 con 12/12 DC resueltas constitucionalmente o diferidas terminalmente a una autoridad identificada**, según la regla §5 canónica. DC-06/09 están resueltas en este Maestro; su posterior materialización normativa no es una decisión pendiente. §9 referencia metodología general sin duplicar pirámide; interpretación v1.3.0/v1.4.0 asentada en §9. **Para FROZEN falta la aprobación integral explícita del Architecture Board con fecha en header**; la autorización de integración Git será separada. Ninguna cantidad ni identidad de NADR futuros está aprobada.

**Nivel B — cierre global de la iniciativa PPPR (no acreditado):** ruta única capaz de aceptar PDFs científicos permitidos, traducir EN→ES con inferencia vigente y controlada, preservar invariantes STEM y estructura por observación reproducible, ensamblar salidas con estado atribuible, recuperar incertidumbres sin efectos externos no autorizados y operar bajo una modalidad local validada; evidencia independiente para cada nivel de calidad, con custodia/privacidad/costo y criterios de aceptación aprobados. GAP-IDs originales tratados y cerrados con falsadores atribuibles cuando correspondan, sin declarar PASS por CI extraction-only, fake o missing corpus. El cierre real requiere Execution Plan autorizado, implementación y verificaciones pertinentes, más revisiones de gobernanza; no se sustituye con el presente documento.

### 10.1 Checklist pre-FROZEN — aplicación de `2_METH_ADR_MASTER.md` v1.0.1 §8 (2026-11-20)

Se registra aquí el **resultado de inspección documental revalidado tras alinear las preguntas DC-06/09 con su resolución constitucional**, no una aprobación del Architecture Board, ejecución de producto ni acto de congelamiento. La checklist tiene **14 controles** y un gate pendiente: aprobación integral.

| # | Comprobación canónica | Veredicto documental y testigo |
|---|---|---|
| 1 | Header completo, aprobación del Board con fecha | **PENDIENTE** — header contiene ratificaciones parciales fechadas, pero **no** aprobación integral del Maestro; fecha de congelamiento `—` |
| 2 | Diez secciones exactas | **CUMPLE** — §§1–10; §2.1 y §8.1/8.2, §10.1 son subsecciones, no niveles nuevos |
| 3 | §1 deriva objetivos ROADMAP | **CUMPLE** — ROADMAP v3.0, Etapas I/II, alcance EN→ES y PPPR transversal autorizado por DC-01 |
| 4 | §2 evidencia de `00-foundation/` | **CUMPLE** — E-IDs y GAP-IDs referenciados a PPPR.0.1–0.9 FROZEN |
| 5 | §2.1 outcome forense | **CUMPLE** — 270+30 E-IDs, 14 GAP-IDs P1 OPEN/13 causas preliminares, 38 DQ total; no ciencia PASS |
| 6 | §3 dimensiones ortogonales/no implicaciones | **CUMPLE** — identidades, extracción/traducción, intento/publicación, fake/certificación |
| 7 | §4 no-objetivos con dueño explícito | **CUMPLE** — cada ítem remite al Maestro, etapa normativa PPPR §8.1, ROADMAP/Scope, contratos vigentes o sucesor autorizado, owner/issue #34 o Execution Plan único; sin inventar NADR o tareas |
| 8 | §5 sin clases/tecnologías ni RFC-2119 | **CUMPLE** — invariantes constitucionales de capacidad, sin imponer clases, proveedor ni reglas MUST/SHOULD nuevas |
| 9 | §6 sin waves/tasks/owners/fechas; cláusula del plan | **CUMPLE** — dependencias de capacidades, no secuencia operativa; cláusula del único Execution Plan |
| 10 | §7 blindaje e histórico de auditoría | **CUMPLE** — NO CODE/NO I/O y fuentes/entregables trazados en 0.1–0.9; **Gap Matrix incorporada** en HITO 0.9 §14, expresamente **no** plantilla autónoma de cinco secciones (§21.1) |
| 11 | §8 ninguna DC abierta | **CUMPLE DOCUMENTALMENTE** — DC-06 y DC-09 quedan resueltas por garantías constitucionales explícitas y evidencia de `00-foundation/` (no por diferimiento a una etapa). Las 12 DC tienen resolución o destino terminal; las futuras reglas normativas no se consideran decisiones pendientes del Maestro ni se anticipa número de NADR |
| 12 | §9 solo cadena normativa interna y jerarquía por referencia | **CUMPLE** — reutilización de NADR FROZEN compatibles, etapa normativa PPPR sin cantidad/identificadores anticipados y Execution Plan único; HITOs son evidencia, no nivel normativo |
| 13 | §10 DoD Nivel A y Nivel B, no por tarea | **CUMPLE** — gobernanza del ADR diferenciada de producto científicamente acreditado |
| 14 | Maestros anteriores no reformateados (abuelamiento) | **CUMPLE** — diff del PR #75 limitado a `ADR_PPPR_MASTER.md`; ningún Maestro histórico modificado |

**Resultado revalidado:** **13/14 controles satisfechos documentalmente; 1/14 pendiente** (control 1: aprobación integral del Architecture Board con fecha). La lectura de `2_METH_ADR_MASTER.md` v1.0.1 y general v1.3.0 FROZEN se documenta en §9 sin presumir equivalencia total con v1.4.0 no disponible. Ningún estado de PR ni ratificación parcial se convierte en aprobación final por inferencia.

**Gate para cambiar de estado:** el órgano competente debe aprobar **integralmente este texto en su HEAD final**, con fecha en el header, y autorizar expresamente su paso a FROZEN. La validación técnica documental del control 11 no sustituye la aprobación integral. **El merge del PR #75 es un acto separado**, no autorizado por completar esta tabla; PR #66 y `main` permanecen fuera de este gate.

**Estado actual respecto de ambos niveles:** **PROPOSED**: las 12 DC cuentan con resolución constitucional o destino terminal documental; DC-06/09 cierran en este Maestro. Falta **aprobación integral/final del Board** para FROZEN. Nivel B sigue **NO ACREDITADO**: no hay NADR PPPR adicionales aprobados, Execution Plan aprobado ni evidencia de calidad física/científica. Sin autorización de implementación, proveedor de pago, corpus/GT privados ni merge de PR #75/#66.
