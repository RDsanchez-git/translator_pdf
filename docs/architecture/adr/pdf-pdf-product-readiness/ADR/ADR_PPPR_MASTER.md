# ARCHITECTURE DECISION RECORD (ADR)
## ADR PPPR: PDF→PDF Product Readiness — Traducción científica EN→ES (ADR Maestro)

* **Estado:** PROPOSED
* **Fecha de Emisión Original:** 2026-11-20
* **Fecha de Congelamiento:** —
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** PPPR — iniciativa transversal autorizada; **no** fase numerada adicional del ROADMAP. Su reconocimiento como unidad de gobernanza equivalente al nivel Maestro queda sujeto a aprobación del Architecture Board antes de FROZEN.
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
4. **Conservación y salida:** G5 incorpora CODE/TABLE como TeX literal y pierde niveles de HEADING; `GAP-0.6-01/02`, `E-0.9-010` y `GAP-0.2-02 → E-0.6-028`. El defecto jerárquico de firma AST y el de render son **distintos**.
5. **Operación y custodia:** el host/Compose efectivo, la inyección de secretos y la modalidad comercial no fueron acreditados; PPPR.0.7 §14 conserva dos **candidatos NO CONFIRMADOS**, no nuevos P1 (`E-0.9-015/022`).
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
| Establecer métricas, umbrales científicos o particiones sin testigos independientes | **ADR de criterios científicos o NADR solo si es indispensable**, con Evidence/Execution Plan y autorización del owner |
| Obtener, reemplazar o alterar los 15 PDFs privados, GT, hashes o corpus canónico | **Owner/issue #34** y posterior protocolo de custodia/testigo autorizado |
| Atribuir certificación PDF→PDF a CV de extracción, laboratorio fake o subtools heredados | **Gobernanza de certificación del producto** (DC-09/10) y testigos autorizados posteriores |
| Reabrir, superseder o imponer íntegramente F17-BIS/F18 por analogía histórica | **Gobernanza del ADR/NADR de la capacidad afectada** mediante decisión explícita; FROZEN previo permanece |
| Definir programación, responsables personales, batches, story points, rollout o rollback | **Execution Plan único** de esta iniciativa, después de normas aprobadas |
| Crear registros Exit Review/Findings por anticipación | **Gates de ejecución y revisión post-implementación** según metodología general §6.5–6.6 |

## 5. INVARIANTES Y REGLAS DE GOBERNANZA

**Invariantes constitucionales propuestas (sujetas a aprobación de este Maestro; no son reglas RFC-2119 nuevas):**

1. **Unidad de ruta:** existe un solo flujo productivo soportado para el alcance inicial; rutas históricas o herramientas de laboratorio no se convierten en vías alternativas por la puerta de atrás.
2. **Intención lingüística explícita:** la entrada en inglés y el destino español forman parte del significado verificable de una generación, sin presuponer producto multilingüe.
3. **Preservación STEM y linaje:** la traducción y reconstrucción no degradan silenciosamente fórmulas, código, identificadores, tablas, jerarquía o atribución documental.
4. **Identidad con propósito:** toda identidad usada para cache, guardia, linaje o certificación tiene semántica y sensibilidad acordes a su consumidor; la coincidencia de hashes no reemplaza una prueba independiente.
5. **Autoridad al efecto:** inferencia y publicación quedan sujetas a autoridad vigente, manejo explícito de estados inciertos y evitación de segundos efectos remotos ciegos.
6. **Degradación explícita:** un resultado parcial o fallido conserva su condición y no se presenta como un PDF íntegro o certificado.
7. **Sujeto-oráculo-resultado inseparables:** cada afirmación de calidad tiene sujeto evaluado, evidencia independiente y límites reproducibles; técnica fake, extracción y ciencia del PDF final no se colapsan.
8. **Custodia, privacidad y costo:** ningún testigo científico o proveedor comercial se interpreta como autorizado por la sola existencia de herramientas, configuraciones o documentos.

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

**Regla de estado:** `CONFIRMADA POR DECISIÓN PREVIA` solo significa que el owner ya fijó el alcance nombrado; **no** aprueba una implementación. `DIFERIDA TERMINAL` indica explícitamente **en qué documento o autorización se tomará la decisión**, como permite la metodología `2_METH_ADR_MASTER.md` §5; no es una respuesta técnica ni una autorización anticipada. El ADR permanece PROPOSED hasta revisión del Board y checklist completo.

| DC | Pregunta y origen vinculante | Estado / respuesta terminal documentada | Documento o autoridad de la decisión pendiente |
|---|---|---|---|
| **DC-01** | ¿Qué autoridad y encuadre tiene PPPR como Maestro transversal no numerado? PPPR.0.1 §2; PPPR.0.9 §21; ROADMAP v3.0 | **DIFERIDA TERMINAL:** formalización de unidad de gobernanza PPPR, sin alterar numeración del ROADMAP | **Architecture Board / aprobación de este Maestro**; si exige cambio de ROADMAP, decisión superior explícita antes de FROZEN |
| **DC-02** | ¿Cuál es la dirección lingüística inicial y cómo queda reflejada en el contrato de generación? GAP-0.4-03; DC-0.4-02 | **CONFIRMADA POR DECISIÓN PREVIA:** inicialmente **EN→ES**. **DIFERIDA TERMINAL** su expresión/verificación contractual | **ADR de capacidad si fuera necesario / NADR compatible de contrato**, después de aprobar el Maestro |
| **DC-03** | ¿Qué inferencia vigente y política de fallback/presupuesto sostendrán EN→ES? GAP-0.4-01/02/04, GAP-0.1-01; DC-0.4-01/03/04 | **CONFIRMADA POR DECISIÓN PREVIA** necesidad de renovar inferencia; **DIFERIDA TERMINAL** elección backend, límite y fallos compatibles | **Decisión normativa de inferencia** (ADR específico solo si necesario) y evaluación autorizada; Execution Plan después |
| **DC-04** | ¿Qué semántica debe tener identidad de generación, hashing y preservación de jerarquía? GAP-0.3-01/02; DQ-0.9-01, E-0.9-025…028 | **DIFERIDA TERMINAL:** reconciliar propósito de firma, consumidores y aplicabilidad de NADR-F17BIS-03/16 sin rebajar GAP | **ADR/NADR de identidad solo ante vacío demostrado**, precedido por decisión del Board sobre contrato de producto |
| **DC-05** | ¿Cuál es el nivel de fidelidad topológica/visual y su frontera entre fuente y G5? GAP-0.2-01/02, GAP-0.6-02; DC-0.3-02, DC-0.6-02/03 | **DIFERIDA TERMINAL:** criterios independientes y conservación documentaria por clase | **Decisión de aceptación/layout** del ámbito aprobado; testigo/Execution Plan posterior |
| **DC-06** | ¿Cómo distinguir literal STEM/CODE/TABLE de comandos legítimos y preservar significado? GAP-0.6-01, DC-0.6-01, E-0.8-021 | **DIFERIDA TERMINAL:** contrato de preservación y aceptación con fidelidad | **Decisión normativa STEM** si no bastan contratos FROZEN; testigos posteriores |
| **DC-07** | ¿Qué política de autoridad/recuperación para UNKNOWN, lease y sweeper resulta exigible? GAP-0.5-01/02/03; DC-0.5-01…03 | **DIFERIDA TERMINAL:** aplicar F18 compatible y delimitar discrepancias sin doble efecto ciego | **NADR F18 FROZEN aplicable**, ADR específico solo ante nueva decisión; Execution Plan |
| **DC-08** | ¿Cuál modalidad local inicial y superficie de secretos/red/host es producto soportado? PPPR.0.7 DQ-01…05/DC-01…04 | **DIFERIDA TERMINAL:** modo host/contendor/foreground y mínima seguridad verificable | **Architecture Board** (modalidad), contrato de seguridad/NADR existente compatible y plan |
| **DC-09** | ¿Qué sujeto se certifica y qué separa técnica de evidencia científica? PPPR.0.8 DC-01/02/04, E-0.9-016…019 | **DIFERIDA TERMINAL:** garantía por sujeto PDF→AST vs PDF EN→ES, oráculos y niveles de aceptación | **ADR de alcance científico o regla normativa estrictamente necesaria**, luego Execution Plan y corpus autorizado |
| **DC-10** | ¿Cómo custodiar corpus y establecer evidencia independiente sin leakage ni oráculos ficticios? Issue #34, PPPR.0.8 DQ-01/03/DC-03 | **DIFERIDA TERMINAL:** licencia/materialización/partición/custodia y autorización de tests | **Owner / issue #34**, protocolo científico y Execution Plan una vez aprobado |
| **DC-11** | ¿Conviene reutilizar preflight/post-run F17-BIS para certificación del producto? E-0.8-026/046/047; DQ-0.8-06/07 | **DIFERIDA TERMINAL y CONDICIONAL:** primero acreditar caller, sujeto y contrato; no declarar nuevo gate por analogía | **Decisión de certificación DC-09** y revisión del subtool si se reutiliza |
| **DC-12** | ¿Se incorpora capacidad DEGRADED/fallback al producto inicial? PPPR.0.6 DQ-04/DC-04 | **DIFERIDA TERMINAL, CONDICIONAL:** nada obliga a habilitar DEGRADED por existir código | **ADR Maestro aprobado / ADR de capacidad solo si se adopta**, con testigo de aceptación posterior |

**Disposición y trazabilidad:** este registro agrupa familias de los **22 DC-IDs heredados** y **37 DQ-IDs heredados + DQ-0.9-01** sin renombrar ni eliminar ninguno; su disposición individual permanece vinculante en HITO_PPPR.0.9 §16. Los `DC-01…12` son las preguntas del **Maestro**, no 12 aprobaciones técnicas ni 12 nuevos ADRs. Una resolución sustantiva pendiente no se convierte en evidencia por figurar `DIFERIDA TERMINAL`. El Board puede requerir decisión explícita antes de FROZEN, en especial DC-01 y los límites propios del producto.

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

**Nota de compatibilidad metodológica:** el header de `2_METH_ADR_MASTER.md` v1.0.1 declara derivación de la metodología general **v1.4.0**; el archivo general consultado en `main@1d21cfe` lleva **v1.3.0 FROZEN**. Este ADR no resuelve, sustituye ni actualiza ambas fuentes por su cuenta: usa las reglas de jerarquía/precedencia verificadas y conserva la discrepancia editorial de versiones para revisión de autoridad antes de FROZEN. Tampoco presume que una iniciativa transversal equivalga automáticamente a una fase numerada del ROADMAP.

## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES

**Nivel A — gobernanza del ADR Maestro (condiciones de FROZEN):** plantilla exacta de diez secciones conforme a `2_METH_ADR_MASTER.md` v1.0.1; trazabilidad de §2 a E/GAP de Fase 0; distinciones y no-objetivos con dueño; invariantes de capacidad sin RFC-2119; roadmap lógico sin tareas ni calendario; §7 histórico; 100% del DC Log con resolución justificada por evidencia o diferimiento terminal a documento explícito, **y** aprobación del Architecture Board fechada en header; reconciliación de encuadre PPPR y discrepancia de versión metodológica sin arrogar autoridad. FROZEN del ADR **no** equivale a ejecución del producto.

**Nivel B — cierre global de la iniciativa PPPR (no acreditado):** ruta única capaz de aceptar PDFs científicos permitidos, traducir EN→ES con inferencia vigente y controlada, preservar invariantes STEM y estructura por observación reproducible, ensamblar salidas con estado atribuible, recuperar incertidumbres sin efectos externos no autorizados y operar bajo una modalidad local validada; evidencia independiente para cada nivel de calidad, con custodia/privacidad/costo y criterios de aceptación aprobados. GAP-IDs originales tratados y cerrados con falsadores atribuibles cuando correspondan, sin declarar PASS por CI extraction-only, fake o missing corpus. El cierre real requiere Execution Plan autorizado, implementación y verificaciones pertinentes, más revisiones de gobernanza; no se sustituye con el presente documento.

**Estado actual respecto de ambos niveles:** **PROPOSED**: Nivel A no satisface todavía aprobación del Board, decisiones y revisión de encuadre; Nivel B no está demostrado por evidencia física/científica. No se habilita código, tests con costos ni merge del PR #66.
