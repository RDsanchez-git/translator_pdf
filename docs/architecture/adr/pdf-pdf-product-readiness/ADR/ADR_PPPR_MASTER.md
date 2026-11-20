# ARCHITECTURE DECISION RECORD (ADR)
## ADR PPPR: PDF→PDF Product Readiness — Traducción científica EN→ES (ADR Maestro)

* **Estado:** PROPOSED
* **Fecha de Emisión Original:** 2026-11-20
* **Fecha de Congelamiento:** —
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** PPPR — iniciativa transversal autorizada para auditoría; **no** fase numerada del ROADMAP. La **elevación formal a unidad de gobernanza de nivel Maestro** y la **especialización de nombre/ubicación** (frente a `ADR_F{FASE}_MASTER.md` en `phase-{fase}/ADR/`) son materia de DC-01 **ABIERTA**, sujetas a aprobación del Architecture Board antes de FROZEN.
* **Módulos Afectados:** CLI/ingesta, OCR y perfiles documentales, AST/normalización/chunking, G3 e inferencia, autoridad W06/FSM/SQLite, G5/ensamblado, empaquetado local, tests/CI y certificación de producto.
* **Aprobación Architecture Board:** — (pendiente; no inferida de aprobación de HITOs o PRs)
* **Derivado de:** ROADMAP_ARQUITECTONICO_LP v3.0 (Etapa I: nacimiento del traductor científico; Etapa II: madurez operativa), PROJECT_SCOPE.md, ENGINEERING_PRINCIPLES.md, convergencia D-1/D-2 y PPPR.0.1–0.9 FROZEN.
* **Supersede:** — (primera propuesta PPPR; no reemplaza ADR F18 ni ADR F17-BIS)

## 1. CONTEXTO Y JUSTIFICACIÓN

El ROADMAP v3.0 describe un producto local de un nodo que traduce documentos científicos complejos preservando contenido técnico, topología y posibilidad de operación. Las capacidades del motor, el runtime local y la madurez de producto son horizontes distintos; ningún hito histórico de convergencia fake o regresión de extracción equivale a una traducción EN→ES científicamente acreditada.

La convergencia D-1/D-2 seleccionó una ruta operativa única **CLI → OCR → G3 → G5 → PDF**, apoyada por contratos de estado y testigos técnicos delimitados. El owner definió la meta inicial **exclusivamente EN→ES** y la necesidad de renovar la inferencia obsoleta, **sin** aprobar aquí proveedor, modelo, implementación ni modalidad comercial. La iniciativa PPPR reúne evidencia transversal para decidir las capacidades mínimas que faltan antes de poder acreditar esa meta.

**Relación formal con el ROADMAP y pre-freeze:** PPPR no está enumerada como fase en el ROADMAP v3.0. Es una iniciativa transversal autorizada documentalmente, motivada por la diferencia entre la capacidad operativa comprobada en laboratorio y la garantía científica/comercial pretendida. Este Maestro no cambia la numeración, reabre Fase 18 ni declara un pivot aprobado del ROADMAP: **su estatus como unidad autónoma de gobernanza Maestro es materia de aprobación del Architecture Board (DC-01)**. Hasta entonces el documento es solo PROPOSED.

## 2. PROBLEMA ARQUITECTÓNICO Y ESTADO OBSERVADO

La auditoría forense PPPR.0.1–0.9, vinculada a `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`, identifica las siguientes incertidumbres **sin prescribir soluciones**:

1. **Contrato EN→ES y proveedor:** G3 declara un modelo obsoleto, no transporta destino español en el contrato inspeccionado y presenta conmutación de fallback lógica sin materialización física; `GAP-0.4-01/02/03/04`, `GAP-0.1-01`, `E-0.9-003/004/005`. El par `0.1-01 ↔ 0.4-02` tiene una causa compartida, no dos remediaciones independientes.
2. **Identidad y continuidad documental:** perfilado usa muestreo sin página real y ancho `612.0`; la firma AST pierde semántica jerárquica y no asegura canonización Unicode de su pre-image; `GAP-0.2-01/02`, `GAP-0.3-01/02`, `E-0.9-006…009/025…028`. Los contratos de `NADR-F17BIS-03` y `-16` requieren examen de **sujeto y propósito** para identidad de generación (DQ-0.9-01).
3. **Autoridad y efectos externos:** la cuarentena UNKNOWN no tiene escalamiento conectado, el lease se comprueba antes de una espera y el sweeper Compose mezcla estados/reporting; `GAP-0.5-01/02/03`, `E-0.9-011…013`. No se probó doble cobro o incidente remoto.
4. **Conservación, política lingüística y salida:** G5 incorpora CODE/TABLE como TeX literal y pierde niveles de HEADING (`GAP-0.6-01/02`, `E-0.9-010`). PPPR.0.3 `E-0.3-013/018` y `DC-0.3-01` muestran que los encabezados observados pueden llegar como PRESERVE **sin traducción**, pese a una estrategia TRANSLATE; **traducirlos o preservarlos requiere una política aún no aprobada**. `GAP-0.2-02 → E-0.6-028` es propagación geométrica upstream. El defecto jerárquico de firma AST y el de render son **distintos**.
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

**Capacidades in-scope de esta unidad transversal propuesta:** continuidad observable de la ruta única PDF→PDF; traducción explícita inicialmente EN→ES con inferencia vigente; integridad estructural y matemática desde documento fuente hasta salida; identidad coherente con consumidores reales; autoridad/fail-closed ante efectos, pausas y recuperación; salida PDF con reporte atribuible; operación local según modalidad aprobada; y evidencia técnica/científica diferenciada por sujeto, privacidad y custodia.

**No-objetivos y dueño documental/temporal explícito:**

| Fuera de alcance del ADR Maestro | Dueño / destino |
|---|---|
| Elegir implementación, clase, patrón de conmutación, proveedor específico, cifra de presupuesto, memoria o algoritmo Unicode | NADR compatible si hace falta una regla; **Execution Plan** aprobado para mecanismo/tareas; evaluación empírica autorizada para escoger proveedor |
| Modificar pipelines o construir runtime, workers, cachés, servicio, CI o motor de PDF nuevo | **Implementación posterior** a paquete normativo y plan aprobado, bajo PR de código independiente |
| Reentrenar OCR o LLM, ampliar producto a multidioma, UI compleja o infraestructura distribuida | **ROADMAP/Scope futuro**, sujeto a un cambio formal de objetivos y decisión de governance; no PPPR inicial |
| Establecer métricas, umbrales científicos o particiones sin testigos independientes | **Etapa normativa de verificación científica de PPPR**, con ADR de subfase solo ante decisión autónoma necesaria, NADR únicamente ante laguna comprobada, y **Execution Plan** de testigos autorizados; no se presupone un segundo framework |
| Obtener, reemplazar o alterar los 15 PDFs privados, GT, hashes o corpus canónico | **Owner/issue #34** y posterior protocolo de custodia/testigo autorizado |
| Atribuir certificación PDF→PDF a CV de extracción, laboratorio fake o subtools heredados | **Gobernanza de certificación del producto** (DC-09/10) y testigos autorizados posteriores |
| Reabrir, superseder o imponer íntegramente F17-BIS/F18 por analogía histórica | **Gobernanza del ADR/NADR de la capacidad afectada** mediante decisión explícita; FROZEN previo permanece |
| Definir programación, responsables personales, batches, story points, rollout o rollback | **Execution Plan único** de esta iniciativa, después de normas aprobadas |
| Crear registros Exit Review/Findings por anticipación | **Gates de ejecución y revisión post-implementación** según metodología general §6.5–6.6 |
| Publicar una vía alternativa `DEGRADED` como salida inicial del producto **sin una política explícita aprobada** | **Decisión constitucional DC-12 de este Maestro** (pendiente Board): propuesta de excluir DEGRADED del alcance inicial; si en el futuro se quiere admitir, **ADR sucesor o ADR de subfase expresamente autorizado** y luego norma/plan/testigo conforme a ese alcance |

## 5. INVARIANTES Y REGLAS DE GOBERNANZA

**Invariantes constitucionales propuestas (sujetas a aprobación de este Maestro; no son reglas RFC-2119 nuevas):**

1. **Unidad de ruta:** existe un solo flujo productivo soportado para el alcance inicial; rutas históricas o herramientas de laboratorio no se convierten en vías alternativas por la puerta de atrás.
2. **Intención lingüística explícita:** la entrada en inglés y el destino español forman parte del significado verificable de una generación, sin presuponer producto multilingüe.
3. **Preservación STEM y linaje:** la traducción y reconstrucción no degradan silenciosamente fórmulas, código, identificadores, tablas, jerarquía o atribución documental.
4. **Identidad con propósito:** toda identidad usada para cache, guardia, linaje o certificación tiene semántica y sensibilidad acordes a su consumidor; la coincidencia de hashes no reemplaza una prueba independiente.
5. **Inferencia compatible y acotada:** el alcance EN→ES contempla un backend vigente y autorizado, coherencia entre modelo realmente invocado, capacidad de contexto, presupuesto total e identidad de petición; una alternativa de inferencia no demostrada no equivale a fallback viable.
6. **Autoridad al efecto:** inferencia y publicación quedan sujetas a autoridad vigente, manejo explícito de estados inciertos y evitación de segundos efectos remotos ciegos.
7. **Degradación explícita:** un resultado parcial o fallido conserva su condición y no se presenta como un PDF íntegro o certificado. **La admisión comercial de DEGRADED no se presupone**, conforme a DC-12 pendiente de ratificación.
8. **Sujeto-oráculo-resultado inseparables:** el **PDF científico final EN→ES** es el sujeto de aceptación del producto inicial; cada afirmación de calidad tiene evidencia independiente y límites reproducibles. Extracción PDF→AST, técnica fake y ciencia del PDF final no se colapsan.
9. **Custodia, privacidad y costo:** ningún testigo científico o proveedor comercial se interpreta como autorizado por la sola existencia de herramientas, configuraciones o documentos.

**Gobernanza del proceso:** Audit First, Reuse Before Invent, YAGNI y minimización de nuevos contratos. Las 14 GAP-IDs heredadas conservan su autoridad original, aunque dos compartan causa. Las reglas de capacidad se expresarán, si corresponde, en NADR aplicables, sin duplicar F18 ni importar F17-BIS íntegro. La falta de evidencia no se transforma en mecanismo por preferencia.

## 6. HOJA DE RUTA DE SUB-FASES GOBERNADAS

**Árbol de capacidades y dependencia lógica propuesta**, sin asignar fases numeradas del ROADMAP, fechas, waves ni trabajos técnicos:

```text
PPPR (unidad transversal propuesta)
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

**Cláusula de Relación con el Execution Plan (obligatoria):** este ADR define **qué capacidades y dependencias lógicas** sostienen el objetivo; **no** ordena tareas, adjudica prioridades ejecutivas, reparaciones, tecnologías, coste o calendario. El **único Execution Plan** posterior, una vez aprobadas las normas necesarias, será la fuente de tareas, dependencias operativas, aceptación, presupuesto y rollback, con trazabilidad a decisiones, reglas y E/GAP-IDs de origen. Ninguna parte de este §6 autoriza implementación.

## 7. ESPECIFICACIÓN DE LA COMPUERTA DE AUDITORÍA (FASE 0)

**Historical Note — compuerta ya completada:** la auditoría de esta iniciativa transversal quedó documentada por PPPR.0.1–0.9 FROZEN en la rama general antes de la emisión de este ADR. Esta sección conserva el **contrato y resultado histórico** de esa compuerta, sin volver a prescribir otra campaña.

**Blindaje aplicado:** `NO CODE / NO I/O` para las pasadas documentales; no pytest/CI, Docker, Tectonic, proveedor de pago, lectura o transmisión de corpus privado, mutación de SQLite/GT/manifests. Las no-verificaciones se registraron en Deferred Questions, sin fabricar PASS.

**Entradas y actividades acreditadas por HITOs:** fuentes de ruta/consumidores (0.1), ingesta/perfiles (0.2), AST/identidad (0.3), G3/modelo/idioma/presupuestos (0.4), W06/FSM/SQLite (0.5), G5/TeX (0.6), host/Compose (0.7), tests/corpus/certificación (0.8) y cruces causales/autoridad (0.9). Versiones y E-IDs vinculantes residen en `00-foundation/`; no se transcriben aquí.

**Entregables de auditoría ya trazables, sin documentación paralela:** **Gap Matrix** incorporada a HITO_PPPR.0.9 §14; **Contract Map** distribuido en HITO_PPPR.0.1 §6.1 y HITO_PPPR.0.9 §§5/7; **Evidence Register** materializado como E-ID estables en PPPR.0.1–0.9 (reconciliación PPPR.0.9 §10); **DC y DQ** transferidas individualmente en PPPR.0.9 §16. El cierre documentado **no** certifica resultado físico y mantiene issue #34.

**Resultado de compuerta:** auditoría FROZEN, sin nuevo P1 global, con GAP-IDs previos abiertos y decisiones pendientes para este ADR. Una nueva prueba empírica exige sujeto/oráculo y autorización propios, fuera de esta compuerta histórica.

## 8. REGISTRO DE DECISIONES CANDIDATAS (DC LOG)

**Criterio canónico:** `2_METH_ADR_MASTER.md` v1.0.1 §5 considera terminal un DC **solo** con resolución respaldada por evidencia de `00-foundation/` o con la decisión explícita de que se tomará en **un documento/fase X identificable**. Una opción condicional (`ADR de subfase si hace falta`) **no** es automáticamente un destino terminal. `ABIERTA` y `PROPUESTA PENDIENTE DE RATIFICACIÓN` **bloquean FROZEN**. La aprobación previa de la auditoría o del PR no equivale a decisión del Architecture Board.

| DC | Pregunta y evidencia de origen | Disposición documentada actual | Autoridad / destino y gate que falta |
|---|---|---|---|
| **DC-01** | ¿PPPR puede ser unidad Maestro transversal no numerada? ¿Se autoriza nombre `ADR_PPPR_MASTER.md` y hogar `adr/pdf-pdf-product-readiness/ADR/` como especialización de la convención `ADR_F{FASE}_MASTER.md` / `phase-{fase}/ADR/`? PPPR.0.1 §21.2, PPPR.0.9 §21, ROADMAP v3.0 | **OPCIÓN A RESPALDADA POR EL OWNER (2026-11-20); APROBACIÓN CONSTITUTIVA BOARD PENDIENTE — BLOQUEA FROZEN:** reconocer PPPR como unidad transversal de gobernanza de primer nivel **sin** crear fase numerada y autorizar expresamente el nombre y hogar actuales como especialización excepcional, limitada a PPPR. La autorización histórica de HITOs no demostraba por sí sola esta autorización del Maestro; la conformidad actual del owner **no acredita automáticamente** ratificación de Architecture Board. | **Decisión constitutiva previa y explícita del Architecture Board**, sobre autoridad **y** nombre/ubicación, documentada en este §8 con fecha y autoridad. **No** basta con aprobar circularmente el propio ADR, ni se modifica ROADMAP/metodología sin decisión superior. Alternativa B: designar unidad ya autorizada o cambio formal de norma **antes** de seleccionar plantilla/hogar definitivos. |
| **DC-02** | ¿Cuál es el idioma destino del producto inicial y cómo queda exigible en la generación? PPPR.0.4 DC-0.4-02, GAP-0.4-03, E-0.9-005 | **ALCANCE RESUELTO POR OWNER:** exclusivamente **EN→ES**. **Contrato detallado PENDIENTE:** intención verificable `source=en,target=es`, propagación y oráculo, sin selector multilingüe presumido | **Nivel Maestro:** §4/§5 fijan el alcance; **etapa normativa PPPR de contrato de inferencia** conforme a §9, mediante normas FROZEN reutilizables o NADR solo por vacío; **Execution Plan** posterior para pruebas |
| **DC-03** | ¿Qué inferencia, presupuesto y fallback son compatibles con EN→ES? PPPR.0.4 GAP-01/02/04, GAP-0.1-01, DC-0.4-01/03/04 | **MARCO CONSTITUCIONAL PROPUESTO (§5):** inferencia vigente y autorizada; modelo realmente enviado, ventana total y presupuesto coherentes; fallback real verificado o rechazo explícito. **ABIERTA** la elección arquitectónica del backend y si su complejidad justifica ADR separado. Renueva inferencia por voluntad previa del owner, **sin** proveedor seleccionado | **Architecture Board debe elegir antes de FROZEN**: resolver aquí la política/alcance y diferir únicamente elección específica a **ADR de subfase PPPR de inferencia** identificado y autorizado, o registrar íntegramente la decisión de capacidad en este Maestro; la etapa normativa PPPR / Execution Plan **no** puede decidir arquitectura por omisión |
| **DC-04** | ¿Qué significa identidad de generación frente a hashing alternativo? GAP-0.3-01/02; DQ-0.9-01; E-0.9-025…028 | **DIFERIMIENTO PROPUESTO, NO TERMINAL AÚN:** uso de `compute_ast_hash` como identidad durable no queda legitimado por la etiqueta «comparación de parsers»; NADR-F17BIS-03/16 compatible solo por sujeto. No rebajar GAP heredados ni elegir NFC/NFKC | **Etapa normativa PPPR de identidad y linaje** bajo §9; Board debe confirmar si los NADR FROZEN bastan o designar formalmente ADR de subfase/NADR requerido antes de dar destino terminal |
| **DC-05** | ¿Qué se hace con texto de HEADING: traducirlo o preservarlo? ¿Qué jerarquía/layout debe conservar PDF? PPPR.0.3 **DC-0.3-01/02, E-0.3-013/018/019**; GAP-0.6-02, PPPR.0.2 GAP-02 | **ABIERTA A DECISIÓN DE ALCANCE DEL MAESTRO:** no inferir que EN→ES obliga a traducir todos los headings ni que PRESERVE es aceptable sin política. Conservación de niveles y atribución STEM sí es objetivo constitucional; tolerancias visuales y oráculos siguen **NO VERIFICABLE** | **Architecture Board en este Maestro:** política de idioma de títulos/encabezados; después **etapa normativa PPPR de layout/fidelidad** para criterios y **Execution Plan** para testigos con corpus autorizado |
| **DC-06** | ¿Cómo se distingue contenido CODE/TABLE literal de matemática/TeX legítimo? GAP-0.6-01, DC-0.6-01, E-0.8-021 | **ALCANCE CONSTITUCIONAL PROPUESTO:** preservar contenido técnico sin tratar todo texto fuente como comando ejecutable; mecanismo y criterios independientes no resueltos | **Etapa normativa PPPR de preservación STEM/G5** (reusar norma compatible antes de crear NADR); **Execution Plan** para validación física autorizada; Board debe ratificar frontera de producto |
| **DC-07** | ¿Qué autoridad para UNKNOWN, lease y sweeper corresponde a D-1/D-2? GAP-0.5-01/02/03, DC-0.5-01…03 | **MARCO EXISTENTE:** no retry ciego, autoridad antes del efecto y recuperación coherente están cubiertos por ADR/NADR **F18 aplicables**. Los tres GAP siguen OPEN; no se infiere gasto doble observado ni obligatoriedad de 2PC/power-loss universal | **ADR-F18.2 y NADR-F18-03/04/05 vigentes** como contrato de capacidad, con **Execution Plan PPPR** posterior para remediaciones trazables; NADR nuevo solo ante vacío formalmente probado |
| **DC-08** | ¿Cuál es la modalidad local **inicial soportada**? PPPR.0.7 DC-01…04, DQ-02/03, E-0.9-015/022 | **ALCANCE BASE RECONOCIDO:** un solo nodo y CLI como entrada seleccionada D-1/D-2. **ABIERTA — BLOQUEA FROZEN:** si la admisión será dentro de contenedor, en host con transferencia explícita o foreground como modalidad de producto; testigo C2 fake dentro de contenedor **no** autoriza ninguno como modo comercial | **Architecture Board debe fijar el alcance de modalidad en este Maestro** o aprobar explícitamente el traslado a un **ADR de subfase PPPR de operación local** identificable; contrato de secretos/red y preflight solo **después** en norma/Execution Plan |
| **DC-09** | ¿Cuál es el sujeto de aceptación científica del producto? PPPR.0.8 DC-01/02/04 y E-0.9-016…019 | **ALCANCE CONSTITUCIONAL DEL MAESTRO (§3/§5):** el **PDF final científico EN→ES** es el sujeto objetivo; la regresión **PDF→AST** y la continuidad fake son testigos de otras propiedades, no certificación del producto. **ABIERTOS** los criterios, oráculos independientes, niveles de aceptación y cobertura física | **Architecture Board ratifica este sujeto**; los criterios pasan a **etapa normativa PPPR de verificación científica** conforme a §9, y los testigos a **Execution Plan** una vez autorizado corpus/proveedor. Un ADR científico separado solo si el Board identifica decisión autónoma |
| **DC-10** | ¿Cómo se obtiene corpus y se evita falsa independencia? Issue #34, PPPR.0.8 DQ-01/03/DC-03 | **DIFERIDA A AUTORIZACIÓN IDENTIFICADA:** 15 PDFs ausentes, custodia/licencia, materialización física y particiones siguen sin evidencia; no alterar manifest/GT, inventar leakage o certificar | **Owner e issue #34** (autorización y custodia) → protocolo de evaluación dentro de la **etapa normativa científica PPPR** y del **Execution Plan** aprobado; no ejecutar antes |
| **DC-11** | ¿Se reutilizan herramientas F17-BIS de preflight/post-run? E-0.8-026/046/047; DQ-0.8-06/07 | **CONDICIONAL:** no hay caller D-1/D-2 certificante acreditado; provenance bool no es fallo por sí solo, pero preflight sin recálculo local y `frozenset` sin cardinalidad limitan esos subtools. **No se presupone reutilización ni una plataforma nueva** | **Etapa normativa PPPR de verificación científica (DC-09)**: si se autoriza reutilizar, revisar caller/sujeto, integridad y unicidad antes de aceptarlo; si no se usa, sin tarea de remediación automática |
| **DC-12** | ¿Se admite publicar PDF `DEGRADED` como variante del producto inicial? PPPR.0.6 DC-0.6-04/DQ-0.6-04, E-0.6-035…042 | **PROPUESTA DE RESOLUCIÓN EN ESTE MAESTRO — PENDIENTE BOARD:** **DEGRADED queda fuera del alcance de publicación aceptada inicial**. No hay productor soportado acreditado que publique esa salida y no se admite fallback opaco al inglés ni un PDF científicamente certificado por ausencia de errores visibles | **Architecture Board en este Maestro** ratifica o rechaza esta exclusión. Admisión posterior solo mediante **ADR sucesor o ADR de subfase autorizado**, contrato/gate y evidencia acordes; **sin autorreferencia** a «ADR Maestro aprobado» |

**DC-01 — propuesta de acuerdo constitucional respaldada por el owner, pendiente de ratificación del Board.** El owner manifestó explícitamente estar de acuerdo con **Opción A** el **2026-11-20** durante la revisión de gobernanza del PR #75. Se documenta esa **conformidad de alcance**, sin atribuirle una votación/acta o facultad formal no acreditada del Architecture Board. La elevación de PPPR no puede deducirse de la aprobación del documento que pretende crear tal autoridad.

- **Fundamento documental:** `2_METH_ADR_MASTER.md` v1.0.1 FROZEN §2 habilita un Maestro para unidad de primer nivel del ROADMAP o subfase formalmente elevada; §3 remite a la convención `ADR_F{FASE}_MASTER.md` dentro de `phase-{fase}/ADR/`. PPPR.0.1 registra autorización de identificador de HITOs y perímetro transversal; PPPR.0.9 FROZEN reconcilia nueve HITOs y 14 GAP-IDs P1, sin añadir fase al ROADMAP v3.0. Son antecedentes suficientes para **proponer** la excepción, no para presumir su aprobación.
- **Opción A — aceptada por el owner, presentada a ratificación del Board:** el Architecture Board **reconoce expresamente PPPR como unidad transversal de gobernanza de primer nivel, acotada al Product Readiness PDF→PDF EN→ES**, sin numeración ni cambio del ROADMAP; aprueba como **excepción documental específica** el identificador `ADR_PPPR_MASTER.md` y la ubicación `docs/architecture/adr/pdf-pdf-product-readiness/ADR/`, y confirma que ello **no crea un precedente automático** para otras iniciativas, subfases o Maestros. Los nueve HITOs y el PR #66 permanecen en la gobernanza ya registrada; esta resolución no aprueba los otros once DC, no congela el ADR ni autoriza implementación.
- **Opción B — si se rechaza A:** el Board identifica la unidad ya autorizada que gobernaría PPPR **o** ordena regularizar la excepción mediante un cambio metodológico/ROADMAP formal conforme a su autoridad; solo después determina el ADR, nombre y hogar definitivos. **No se transfiere automáticamente a F18** ni se renombra preventivamente.
- **Registro de dos autoridades (sin confundir):** **conformidad owner:** Opción A, **2026-11-20**, manifestada expresamente en la conversación de revisión del PR #75 (referencia externa verificable en acta del Board **aún no aportada**). **Acuerdo constitutivo Architecture Board:** PENDIENTE; **opción/resolución formal:** —; **autoridad / competencia acreditada:** —; **fecha de resolución:** —; **referencia de acta/aprobación:** —. Una vez ratificada, reconciliar la fila DC-01 y el header sin inferir de este acuerdo la aprobación final del ADR. El gate de compatibilidad v1.4.0/v1.3.0 del §9 y los otros DC siguen separados.

### Propuestas de decisión de alcance para el Architecture Board (pendientes, no aprobadas)

Las propuestas siguientes se derivan de los HITO FROZEN; **no** se atribuye aquí decisión del owner sobre estos cinco asuntos. Cada una separa la **política constitucional** que debe ratificarse de mecanismos/oráculos que corresponden a decisión normativa identificable y a un Execution Plan posterior. Las alternativas se mantienen abiertas hasta constancia formal.

| DC | Política constitucional propuesta para ratificación | Alternativa explícita o límite | Materia posterior, sin implementación ni nuevo ADR automático |
|---|---|---|---|
| **DC-03 — inferencia** | Para la ruta EN→ES, solo inferencia con backend vigente/autorizado; decisión de presupuesto por ventana **total** y modelo efectivamente invocado; si no se dispone de modelo compatible, no representar una conmutación lógica como fallback exitoso y conservar fallo explícito. | La política **no** selecciona proveedor comercial/modelo/API, cifras de costo ni obliga a tener fallback; el Board puede optar por **rechazo sin fallback** mientras no exista alternativa contrastada. | Selección arquitectónica concreta en **decisión de capacidad de inferencia PPPR a identificar formalmente por Board** (si amerita ADR de subfase), contrato en NADR solo por vacío y testigos bajo Execution Plan. Hasta asignar documento inequívoco, el DC permanece **ABIERTO**. HITO 0.4 GAP-01/02/04. |
| **DC-05 — títulos, headings y jerarquía** | **Propuesta:** traducir a español el contenido de encabezados que sea lenguaje natural, conservando niveles y función estructural; proteger expresiones STEM, código, símbolos, identificadores y nombres que el contrato de preservación excluya de traducción. | No equiparar traducción de heading con modificación de fórmulas ni declarar automáticamente aceptable el PRESERVE actual. **El owner/Board aún no ha ratificado** la política. | Contrato formal de clases protegidas/layout y oráculos independientes, sujeto al alcance aprobado; Execution Plan/testigo de salida PDF. HITO 0.3 E-013/018/019 y HITO 0.6 GAP-02. |
| **DC-08 — modalidad local** | **Propuesta acotada de mínima superficie:** inicialmente **CLI ejecutada dentro de un contenedor en un solo nodo** como *modalidad objetivo a validar*, preservando D-1/D-2; no asumir que C2 fake prueba producción. | Alternativa legítima: **CLI host con puente explícito** u otro modo local, siempre que el Board lo elija antes de presupuestar su integración. **La selección comercial todavía no ocurrió.** | El modo elegido fija más adelante el alcance de mounts, UID/ACL, secrets, red, Compose real y preflight no destructivo; solo plan/norma estrictamente necesaria después. HITO 0.7 DQ-02/03 y DC-01…04. |
| **DC-09 — sujeto de certificación** | **Propuesta de ratificación:** la afirmación de conformidad del producto inicial se refiere al **PDF científico final traducido EN→ES**, con atribución a su documento origen y evidencias de lengua, STEM, topología y representación que sean independientes y acordadas. | No sustituir esa evidencia con `PDF→AST`, `%PDF-`, `COMPLETED` o proveedor fake; tampoco inventar umbrales o declarar certificación hoy. | Criterios/oráculos/gates del sujeto en **decisión formal de capacidad científica PPPR a designar por Board**, y protocolo de evaluación/custodia con owner/issue #34 y Execution Plan, sin nuevo framework por reflejo. HITO 0.8. |
| **DC-12 — DEGRADED** | **Propuesta:** una salida `DEGRADED` o incompleta **no se admite como PDF final conforme ni certificado** en el alcance inicial. **Se permite considerar un artefacto parcial inequívocamente rotulado para diagnóstico/recuperación**, sin hacerlo pasar por resultado de producto aceptado. | La existencia de manejo de fallos parciales no obliga a comercializar salidas DEGRADED; tampoco se prohíbe la recuperación o el diagnóstico ya previsto por principios. **Falta ratificación del Board.** | Si se quiere admitir salida DEGRADED como resultado de producto en el futuro, decisión arquitectónica de alcance (ADR sucesor/subfase autorizado), contrato, testigo y plan; no producir mecanismo nuevo ahora. HITO 0.6 DQ-04/DC-04. |

**Gate de esta propuesta:** las alternativas anteriores son material para deliberación, **no resoluciones terminales**. En particular, la elección de **DC-05, DC-08, DC-12** y el destino **documental inequívoco** de DC-03/09 todavía necesitan decisión y constancia. `DC-04/06/07/10/11` conservan su revisión de suficiencia de contratos FROZEN y destino formal separada; la conformidad del owner con DC-01 **no aprueba en bloque** el DC Log.

**Estado del DC Log:** **12 DC-IDs del Maestro, todos conservados**. Hay alcance ya fijado por el owner (EN→ES, renovar inferencia) y contratos F18 anteriores que se reutilizan; **DC-01, DC-03, DC-05, DC-08 y DC-12 tienen gates de decisión del Board explícitos** y otros diferimientos están condicionados a la definición de norma/documento. **No se declara que los 12 DC estén terminalmente resueltos**. La revisión favorable del borrador no sustituye aprobación del Board. El ADR permanece **PROPOSED**, con **FROZEN BLOQUEADO** hasta que ningún DC quede abierto o tenga una disposición terminal válida conforme a la metodología.

**Trazabilidad de origen:** los 12 DC aquí agrupan **22 DC-IDs heredados y 37 DQ-IDs heredados más DQ-0.9-01**; la disposición individual y los estados permanecen en PPPR.0.9 §16, sin falsificar decisiones ni abrir doce ADR/NADR. La jerarquía se preserva: la etapa normativa PPPR de §9 no equivale a una fase numerada del ROADMAP ni autoriza implementación.

## 9. ARCHITECTURE GOVERNANCE FRAMEWORK

**Cadena normativa interna de PPPR propuesta:**

```text
ADR Maestro PPPR (constitución de capacidades; aún PROPOSED)
  → [ADR de subfase, solo cuando hay decisión autónoma necesaria]
  → [NADR de capacidad nuevo, solo si falta norma aprobada aplicable]
  → Execution Plan único aprobado
  → Exit Review Evidence Log / Deferred Findings Register en gates de implementación
```

Los HITOs PPPR.0.1–0.9 de `00-foundation/` son **evidencia vinculante de entrada**, no nivel normativo de esa cadena. Los NADRs existentes F18 y los F17-BIS compatibles conservan su autoridad propia, sin reproducirse ni modificarse por este ADR. La jerarquía global se incorpora **por referencia** a `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` §2, sin duplicar su pirámide. La plantilla y el ciclo de vida de este artefacto siguen `docs/architecture/2_METH_ADR_MASTER.md` v1.0.1 FROZEN.

**Gate de compatibilidad metodológica (pendiente Board):** el header de `2_METH_ADR_MASTER.md` v1.0.1 declara derivación de la metodología general **v1.4.0**; el archivo general consultado en `main@1d21cfe` lleva **v1.3.0 FROZEN**. Los apartados citados de jerarquía, taxonomía ADR, flujo, nomenclatura y precedencia son identificables en v1.3.0, pero **eso no equivale a confirmación formal de compatibilidad de versiones**. Antes de FROZEN, el Architecture Board debe registrar la interpretación de autoridad y compatibilidad **sin** editar una fuente FROZEN por conveniencia. En el mismo gate ratificará o corregirá la elevación PPPR y la excepción de denominación/ubicación de DC-01. Ninguna discrepancia se «resuelve» por inferencia del redactante.

## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES

**Nivel A — gobernanza del ADR Maestro (condiciones de FROZEN):** plantilla exacta de diez secciones conforme a `2_METH_ADR_MASTER.md` v1.0.1; trazabilidad de §2 a E/GAP de Fase 0; distinciones y no-objetivos con dueño; invariantes de capacidad sin RFC-2119; roadmap lógico sin tareas ni calendario; §7 histórico; **100% de DC del §8 resueltos por evidencia o diferidos terminalmente a documento/fase inequívoca**. Requiere además **resolución Board de DC-01** (autoridad de Maestro y especialización nombre/hogar), ratificación/disposición terminal de los gates abiertos **DC-03/05/08/12**, delimitación científica **DC-09**, revisión de la discrepancia v1.4.0/v1.3.0 y **aprobación Architecture Board fechada en header**. Nada de ello se presume por el cierre PPPR.0.9. FROZEN del ADR **no** equivale a ejecución del producto.

**Nivel B — cierre global de la iniciativa PPPR (no acreditado):** ruta única capaz de aceptar PDFs científicos permitidos, traducir EN→ES con inferencia vigente y controlada, preservar invariantes STEM y estructura por observación reproducible, ensamblar salidas con estado atribuible, recuperar incertidumbres sin efectos externos no autorizados y operar bajo una modalidad local validada; evidencia independiente para cada nivel de calidad, con custodia/privacidad/costo y criterios de aceptación aprobados. GAP-IDs originales tratados y cerrados con falsadores atribuibles cuando correspondan, sin declarar PASS por CI extraction-only, fake o missing corpus. El cierre real requiere Execution Plan autorizado, implementación y verificaciones pertinentes, más revisiones de gobernanza; no se sustituye con el presente documento.

**Estado actual respecto de ambos niveles:** **PROPOSED**: Nivel A no satisface todavía aprobación del Board, decisiones y revisión de encuadre; Nivel B no está demostrado por evidencia física/científica. No se habilita código, tests con costos ni merge del PR #66.
