# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F18.2: Durable Execution & Recovery

* **Estado:** FROZEN
* **Versión:** v3.3.0
* **Fecha de Emisión:** 2026-10-10
* **Fecha de Congelamiento:** 2026-10-10
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** Fase 18 (Advanced Local Runtime)
* **Subfase:** 18.2 (Durable Execution & Recovery)
* **Tipo de artefacto:** ADR de Subfase (decisión arquitectónica)
* **Naturaleza:** Documento de decisión. No prescribe implementación, no define reglas normativas detalladas, no define secuencia operativa.
* **Evidencia Forense Vinculante:**
  - HITO_18.2.0 v1.3.0 FROZEN
  - HITO_18.2.1 v1.2.0 FROZEN
  - HITO_18.2.2 v1.4.1 FROZEN
* **Referencias Cruzadas:**
  * **Depende de:** ADR_F18_MASTER v1.0.0 FROZEN, ADR_F18.1 v1.0.2 FROZEN, NADR-F18-01 v1.0.3 FROZEN, NADR-F18-02 v1.0.1 FROZEN, F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 FROZEN
  * **Implementado por:** NADRs de la Subfase 18.2 (pendientes de emisión)
  * **Ejecutado por:** PHASE_18.2_EXECUTION_PLAN (pendiente)
  * **Conflictúa con:** Ninguno identificado; verificación normativa completada en §10

> **Nota de Gobernanza:** Este ADR desarrolla las decisiones de la subfase 18.2 dentro de la autoridad de `ADR_F18_MASTER`. No sustituye, modifica ni reinterpreta los invariantes congelados del Maestro o los contratos congelados de 18.1. Las reglas técnicas vinculantes de materialización corresponden exclusivamente a los NADRs de la Subfase 18.2 (pendientes de emisión); las tareas, secuencia de cambios y validaciones operativas corresponden al `PHASE_18.2_EXECUTION_PLAN`.

**Advertencia epistemológica:** Este ADR se basa en evidencia forense y experimental de tres HITOs FROZEN. Las garantías que establece están acotadas al modelo de fallos aprobado en §8. La ausencia de capacidad verificada en un proveedor externo no puede utilizarse como fundamento de una garantía normativa. Este documento NO certifica el cumplimiento integral de INV-JOURNAL; establece la dirección arquitectónica para alcanzarlo dentro del modelo de fallos aprobado. La validación de la implementación corresponde a los NADRs de la Subfase 18.2 (pendientes de emisión) y al Execution Plan.

**Convención de DCs:** DC-08a, DC-08b, DC-08c y DC-08d son dimensiones analíticas del único DC-08 definido en ADR_F18_MASTER §8.2. El ADR las resuelve de forma coherente como una única decisión maestra, no como cuatro decisiones independientes.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-09 | Emisión inicial. |
| 2.0.0 | 2026-10-10 | División analítica de DC-08. |
| 2.1.0 | 2026-10-10 | Incorporación de reservas metodológicas. |
| 2.2.1 | 2026-10-10 | Correcciones de consistencia interna. |
| 3.0.0-DRAFT | 2026-10-10 | Reescritura canónica como ADR de subfase. |
| 3.1.0-DRAFT | 2026-10-10 | 8 correcciones integradas tras revisión externa v4. |
| 3.2.0-DRAFT | 2026-10-10 | 8 cambios tras dictamen arquitectónico v5 (desigualdad ventana causal, política DC-08b, tabla escenarios DC-08d, diferimientos DF-24/DF-34, distinción identidad, observabilidad, lenguaje §3 y §7). |
| **3.3.0-FROZEN** | **2026-10-10** | **Resolución del Architecture Board: APROBACIÓN CON ENMIENDAS.** (1) DC-08a RATIFICADO: el lease identifica autoridad local, no prueba inicio de llamada externa; conservadurismo deliberado. (2) DC-08b RATIFICADO CON ENMIENDA: eliminada afirmación de forward progress garantizado; reconocido límite fundamental sin cooperación del proveedor; umbral "5 sweeps/1 hora" reclasificado como candidato operativo para Execution Plan. (3) DC-08c RATIFICADO: eliminada estimación "trivial"; materialización y coste a NADR/Plan. (4) DC-08d RATIFICACIÓN CONDICIONADA: reconocido que sistema local con proveedor remoto mantiene frontera distribuida de efectos y conocimiento; tabla de escenarios completada; WAL+NORMAL con consecuencias honestas; eliminada justificación "10-100ms por write" como NO DEMOSTRADA. (5) DF-24/DF-34 diferidos con umbrales como hipótesis de calibración, no límites fundamentados. (6) Añadida §10 Verificación Normativa. (7) Añadida §11 Limitaciones Aceptadas y Riesgos. |

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 18 dispone de un execution plane con mecanismos de control de tareas, leases, fencing SQL, event journal, proyecciones idempotentes y recuperación mediante componentes especializados. Los HITOs 18.2.0 y 18.2.1 establecieron el estado de estos mecanismos y sus limitaciones operativas. HITO_18.2.2 v1.4.1 FROZEN profundizó el análisis de las fronteras entre ejecución externa, persistencia y recuperación, consolidando cinco gaps (dos P1, tres P2) y verificando la taxonomía de fencing en cuatro categorías (DB/SQL, Reconciler Epoch, External-Effect, Duplicate-Effect Prevention).

La evidencia E-18.2.2-005, E-18.2.2-007 y E-18.2.2-008 identifica una ambigüedad arquitectónica central: cuando el proveedor externo completa una operación, pero el proceso falla antes de registrar su resultado, la recuperación actual no distingue ese escenario de una operación que nunca llegó a ejecutarse. Los mecanismos existentes de idempotencia local y fencing SQL no resuelven por sí solos esa incertidumbre. Esta brecha se consolida en GAP-18.2.2-01 (P1).

Adicionalmente, GAP-18.2.2-04 (P1) establece que la ventana de duplicación no cuenta con medición directa suficiente; GAP-18.2.2-02, GAP-18.2.2-03 y GAP-18.2.2-05 registran incertidumbres sobre la frontera LLM, el modelo de durabilidad y la cobertura de validación. En consecuencia, la subfase requiere una decisión arquitectónica integrada sobre DC-08, sin confundir recuperación durable con entrega exactamente una vez.

**Relación con ADR_F18_MASTER:** Este ADR materializa DC-08 ("Write-policy SQLite + mecanismo de journal de INV-JOURNAL", ADR_F18_MASTER §8.2) y establece disposiciones trazables para los Deferred Findings DF-24 y DF-34 (§8.3), conforme a la cadena normativa interna de Fase 18 (§9.1 del Maestro).

**Naturaleza del sistema (relevante para DC-08d):** ROADMAP_ARQUITECTÓNICO_LP §V establece un producto de nodo único, con SQLite WAL como persistencia, sin Redis, sin Kubernetes, sin mensajería distribuida, sin microservicios. ENGINEERING_PRINCIPLES §I (YAGNI) y §VII (Reuse Before Invent) gobiernan la proporcionalidad de la solución. Estas restricciones respaldan una arquitectura local, pero no eliminan la frontera distribuida de efectos y conocimiento introducida por la llamada a un proveedor remoto de LLM.

---

## 2. PROBLEMA ARQUITECTÓNICO

El problema de 18.2 es la desconexión entre la autoridad local de ejecución, el conocimiento del resultado externo y la capacidad de recuperación tras una interrupción.

El sistema puede conocer que una tarea estaba asignada (lease persistido en chunk_tasks) y puede registrar de forma idempotente un resultado recibido (append_wal con ON CONFLICT DO NOTHING). Sin embargo, no siempre puede establecer si una operación externa ocurrió cuando su resultado no alcanzó el journal.

Esta desconexión introduce cuatro dimensiones estructurales:

1. **Incertidumbre del efecto externo:** La ausencia de resultado local no demuestra que el proveedor no haya ejecutado la operación. La evidencia E-18.2.2-013 confirma que el código cliente auditado no implementa mecanismos de idempotencia ni consulta de estado; las capacidades del proveedor externo NO están verificadas.

2. **Autoridad y propiedad:** La protección de escrituras locales (DB/SQL fencing, DEMOSTRADO en HITO_18.2.1) no equivale a impedir efectos externos iniciados bajo autoridad vencida. El external-effect fencing es PARCIAL (check post-execute); el duplicate-effect prevention está NOT EMPIRICALLY VALIDATED.

3. **Recuperabilidad y durabilidad:** La persistencia de un lease no demuestra por sí sola la suficiencia de la recuperación frente a todos los fallos. La recuperabilidad estructural bajo crash NO está demostrada empíricamente (HITO_18.2.2 §13 Pilar 1). La configuración WAL+NORMAL es OBSERVADA; la semántica de durabilidad es EVIDENCIA DOCUMENTAL; el comportamiento empírico ante cada escenario de fallo es NOT EMPIRICALLY VALIDATED.

4. **Observabilidad:** Sin identificación de intentos y medición del intervalo de exposición, no es posible demostrar la propiedad de duplicación exigida. ProductionTelemetryEvent carece de campos retry_count, attempt_number, is_replay (E-18.2.2-033). No hay instrumentación entre execute() y append_wal() (E-18.2.2-030).

La consecuencia es que el execution plane no puede acreditar todavía el cumplimiento integral de INV-JOURNAL. La propiedad obligatoria de "idempotent apply y ventana de duplicación acotada y medida" (ADR_F18_MASTER §5.1) no está completamente satisfecha: la idempotencia integral del flujo NO está demostrada; la estimación indirecta heredada (~1ms) no constituye cota de la ventana causal real, cuya relación cuantitativa con el intervalo cliente observable es NO DEMOSTRADA y depende de la semántica verificable del proveedor; y la medición de frecuencia natural de duplicación NO está demostrada.

---

## 3. DECISIÓN ARQUITECTÓNICA

**DECISIÓN — DC-08:**

> La subfase 18.2 adopta una arquitectura de ejecución durable y recuperación consciente de efectos externos inciertos, que preserve una autoridad de ejecución recuperable, distinga los resultados confirmados de los resultados inciertos, impida la reejecución ciega de estos últimos, mantenga la aplicación local idempotente y haga explícita, acotable y medible la exposición residual a duplicación, conforme al modelo de fallos aprobado en §8.

Esta decisión establece una dirección arquitectónica, no la obligatoriedad de crear un segundo journal ni de extender `EventLifecycle`.

Sus implicaciones son:

- El control plane y el event plane conservan responsabilidades diferenciadas. El mecanismo existente de lease puede reutilizarse si se demuestra su suficiencia contractual. La ausencia de estado INTENT en el event journal (E-18.2.2-007) no equivale a ausencia de intención durable; el lease en chunk_tasks constituye un mecanismo observado de intención (E-18.2.2-001, E-18.2.2-002).

- La recuperación de una tarea con efecto externo incierto no puede tratarse como equivalente a la recuperación de una tarea cuyo efecto no se inició. El reconciler actual trata ambos casos igual (Vector 1: zombie puro → PENDING), lo cual permite un escenario de duplicación del efecto externo (GAP-18.2.2-01).

- La estrategia para resolver incertidumbre puede depender de capacidades verificadas del proveedor; si estas no existen o no están verificadas, la arquitectura debe reconocer explícitamente el límite de conocimiento. No se asume que el proveedor ofrezca idempotencia, consulta de estado, o deduplicación.

- La idempotencia de las escrituras locales se preserva, pero no se presenta como prueba de idempotencia del proveedor. Son contratos distintos (E-18.2.2-009 a E-18.2.2-012 vs E-18.2.2-013).

- La exposición residual a duplicación debe poder caracterizarse y medirse, sin declarar garantías de exactly-once no demostradas. La arquitectura objetivo deberá satisfacer la propiedad de idempotent apply y ventana de duplicación acotada y medida, cuya conformidad todavía requiere validación conforme a ADR_F18_MASTER §3 (separación "Recovery ≠ Exactly-once delivery").

- La política de durabilidad responde al modelo de fallos explícito aprobado en §8, no a una elección anticipada de parámetros SQLite. El Maestro no menciona fsync ni synchronous=FULL; la elección depende del modelo de fallos.

### 3.1 Matriz de decisión arquitectónica

| Dimensión | Decisión del Board | Estado |
|---|---|---|
| DC-08a — Intención pre-efecto | Reutilizar el lease durable existente como mecanismo principal de intención pre-efecto. No crear un segundo journal ni introducir obligatoriamente INTENT en EventLifecycle. El lease identifica autoridad local; su existencia no prueba que la llamada al proveedor haya comenzado. La arquitectura elige reutilizarlo y exige validar que la reserva sea durable antes de iniciar el efecto externo y que pueda recuperarse inequívocamente. Al recuperar una tarea con lease vencido y sin resultado, el sistema puede necesitar tratarla como incierta, aunque algunas de esas tareas nunca hayan llegado a llamar al proveedor. Ese conservadurismo es deliberado. | **RATIFICADO** |
| DC-08b — Efectos inciertos | Política por defecto: una operación cuyo efecto externo sea incierto no será reejecutada automáticamente por el reconciler. Rutas de resolución: (a) con evidencia externa verificable, resolver estado y actuar según resultado; (b) sin evidencia suficiente, conservar incertidumbre de forma recuperable con trazabilidad obligatoria y política de escalamiento; (c) reejecución bajo incertidumbre como excepción arquitectónicamente autorizada y contabilizable, nunca comportamiento implícito. Se reconoce el límite fundamental: sin cooperación del proveedor no siempre es posible garantizar simultáneamente progreso automático y ausencia de duplicación externa. El escalamiento impide olvido silencioso pero no constituye prueba de que reejecutar sea seguro. | **RATIFICADO CON ENMIENDA** |
| DC-08c — Medición de duplicación | Exigir observabilidad de intentos, resultados, exposición y duplicación. Diferenciar tres magnitudes: reejecuciones del cliente, duplicación inferida, duplicación confirmada. Una tasa calculada a partir de reintentos no debe denominarse automáticamente tasa real de duplicación del proveedor. La arquitectura aprueba la capacidad; los NADRs de la Subfase 18.2 (pendientes de emisión) y el Execution Plan deciden materialización y coste. | **RATIFICADO** |
| DC-08d — Durabilidad | Aprobar el modelo de fallos local acotado definido en §8. Mantener WAL + synchronous=NORMAL + busy_timeout como política inicial de la arquitectura local, sin exigir FULL ni fsync adicional por defecto. La exclusión de power loss y fallo físico del almacenamiento es una decisión de alcance, no una demostración de durabilidad ante esos eventos. Ratificación condicionada a la verificación normativa de §10. | **RATIFICACIÓN CONDICIONADA** |

**Nota sobre el estado RATIFICACIÓN CONDICIONADA:** La condición se satisface en §10 de este mismo documento, donde se verifica que el modelo de fallos acotado no contradice ninguna garantía superior congelada. Al cumplirse la condición dentro del mismo acto de congelamiento, la ratificación queda efectiva.

### 3.2 Política de recuperación bajo incertidumbre

Cuando una operación externa queda clasificada como incierta, la arquitectura debe preservar su trazabilidad y permitir su resolución posterior. Un diferimiento sin salida definida reduce duplicaciones a costa de introducir tareas bloqueadas indefinidamente; pero tampoco puede prometerse progreso automático sin aceptar riesgo de duplicación.

El ADR establece las siguientes propiedades arquitectónicas obligatorias:

- **Trazabilidad:** toda operación incierta debe registrar su estado, el intento original, el momento de primera detección y el historial de sweeps.
- **Escalamiento:** toda operación incierta debe alcanzar un estado explícito que impida su olvido silencioso. El escalamiento no constituye prueba de que reejecutar sea seguro.
- **Autorización excepcional:** si se permite reejecución bajo incertidumbre, debe ser excepción arquitectónicamente autorizada, contabilizable y con aceptación explícita del riesgo.
- **Cierre:** toda operación incierta debe poder cerrarse por resolución con evidencia, expiración o aceptación formal de riesgo.

Los umbrales concretos de escalamiento (candidatos: número de sweeps, tiempo transcurrido) son decisiones operativas del Execution Plan, no decisiones arquitectónicas del ADR. Los candidatos discutidos durante la deliberación (5 sweeps, 1 hora) se registran como hipótesis operativas pendientes de calibración, no como límites fundamentados.

---

## 4. OBJETIVO DE LA SUBFASE

El objetivo de 18.2 es cerrar la brecha entre ejecución externa y recuperación durable, de manera que una interrupción no convierta automáticamente la ausencia de resultado local en autorización para repetir un efecto externo potencialmente completado.

La subfase desarrolla el invariante INV-JOURNAL de ADR_F18_MASTER §5.1, según su formulación literal:

> *"Ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash y una aplicación idempotente del resultado. El mecanismo concreto de persistencia y coordinación permanece abierto a DC-08. La propiedad obligatoria es: idempotent apply y ventana de duplicación acotada y medida."*

El cumplimiento debe demostrarse dentro del modelo de fallos decidido por el Board, diferenciando garantías locales, comportamiento de proveedores externos y limitaciones aceptadas formalmente.

---

## 5. ALCANCE Y NO-OBJETIVOS

| Dentro del alcance arquitectónico | Fuera del alcance |
|---|---|
| Semántica de recuperación ante resultados externos inciertos | Garantizar exactly-once universal en proveedores LLM |
| Suficiencia de la autoridad recuperable pre-efecto | Crear obligatoriamente un nuevo event journal |
| Relación entre fencing local y ejecución externa | Reescribir los mecanismos congelados de 18.1 |
| Medición de exposición y duplicación | Convertir una estimación mock de ~1 ms en garantía contractual |
| Modelo de fallos y garantías de durabilidad | Imponer synchronous=FULL sin decisión del modelo de fallos |
| Convergencia verificable bajo escenarios críticos | Construir un framework genérico de recovery sin necesidad demostrada |
| Preservación de idempotencia y trazabilidad locales | Rediseñar el pipeline de traducción o el AST |
| Evaluación de límites operacionales relacionados con DC-08 | Persistir automáticamente ProfileStore o CircuitBreaker sin resolver sus triggers |
| Disposición trazable para DF-24 y DF-34 | Redefinir invariantes congelados del Maestro |
| Reconocimiento de la frontera distribuida de efectos en sistema local | Introducir infraestructura distribuida (Redis, K8s, mensajería) |

Las cuestiones DF-24 (CircuitBreaker, subsumido en DC-08) y DF-34 (ProfileStore, trigger propio independiente) mantienen su trazabilidad propia. La subfase no debe transformar su condición de componentes in-memory en un mandato automático de persistencia.

---

## 6. GOBERNANZA DE LA SUBFASE

El ADR establece qué arquitectura se adopta y por qué. Las reglas técnicas vinculantes de materialización corresponden exclusivamente a los NADRs de la Subfase 18.2 (pendientes de emisión); las tareas, secuencia de cambios y validaciones operativas corresponden al PHASE_18.2_EXECUTION_PLAN.

La gobernanza se apoya en estos principios (no constituyen reglas técnicas vinculantes; orientan las decisiones subordinadas):

- **Preservación de autoridad:** Ningún mecanismo nuevo puede contradecir ADR_F18_MASTER ni alterar los contratos congelados de 18.1 (NADR-F18-02 §5.4 R15).

- **Separación de garantías:** Idempotencia local, deduplicación externa, fencing y durabilidad son propiedades distintas. Una prueba de fencing SQL no demuestra fencing de efecto externo. Una prueba con mock demuestra el comportamiento de la aplicación bajo condiciones simuladas, no una garantía universal del proveedor.

- **Recuperación basada en evidencia:** Un resultado ausente no constituye prueba de que el efecto no ocurrió. La recuperación debe distinguir entre "efecto no iniciado" y "efecto iniciado pero no registrado".

- **Reuse Before Invent:** Los activos existentes son la primera opción de evaluación. La evidencia no justifica sustituir indiscriminadamente la maquinaria de recovery. Los componentes clasificados como `PRESENT — behavior observed` en HITO_18.2.2 §12 constituyen la base de evaluación.

- **Límites epistemológicos explícitos:** Una capacidad no verificada del proveedor no puede utilizarse como fundamento de una garantía normativa. Las estimaciones indirectas (ventana ~1ms por resta) no constituyen mediciones directas de la ventana causal; la relación cuantitativa entre intervalo cliente y ventana causal es NO DEMOSTRADA y depende de la semántica del proveedor.

- **Validación proporcional al contrato:** Cada garantía debe disponer de evidencia reproducible dentro de su alcance declarado. El ADR define capacidades de verificación requeridas; los métodos concretos de verificación corresponden al Execution Plan.

- **Reconocimiento de frontera distribuida:** Aunque la arquitectura es local (ROADMAP §V), la llamada a un proveedor remoto introduce una frontera distribuida de efectos y conocimiento. La arquitectura no requiere infraestructura distribuida, pero sí debe reconocer explícitamente esa frontera.

---

## 7. ARQUITECTURA OBJETIVO — TARGET STATE

El estado objetivo separa tres conceptos que hoy pueden confundirse: autoridad para ejecutar, resultado de un efecto externo y confirmación local durable de ese resultado.

~~~text
MODELO CONCEPTUAL DE ARQUITECTURA OBJETIVO
(Diagrama conceptual, no secuencia de implementación)

  AUTORIDAD PARA EJECUTAR          EFECTO EXTERNO              CONFIRMACIÓN LOCAL
  (Control Plane)                  (Proveedor LLM)             (Event Plane)
  ┌─────────────────────┐         ┌──────────────────┐        ┌─────────────────────┐
  │ Lease persistido    │         │ LLM call         │        │ append_wal          │
  │ PROCESSING +        │ ──────► │ (efecto externo  │ ─────► │ GENERATED           │
  │ lease_owner +       │         │  no verificable  │        │ (confirmación       │
  │ execution_id de     │         │  desde el repo)  │        │  local durable)     │
  │ intento (*)         │         │                  │        │                     │
  └─────────────────────┘         └──────────────────┘        └─────────────────────┘
         │                                │                           │
         │  ┌─────────────────────────────┴────────────────────────┐ │
         │  │ VENTANAS DE EXPOSICIÓN (distintas, no equiparables)  │ │
         │  │                                                      │ │
         │  │ VENTANA CLIENTE (observable):                        │ │
         │  │   execute() → append_wal()                           │ │
         │  │   Estimación indirecta: ~1ms (HITO_18.2.1)           │ │
         │  │   Medible con instrumentación local                  │ │
         │  │                                                      │ │
         │  │ VENTANA CAUSAL (inobservable sin colaboración):      │ │
         │  │   efecto externo completado → resultado durable      │ │
         │  │   RELACIÓN CUANTITATIVA CON VENTANA CLIENTE:         │ │
         │  │   NO DEMOSTRADA. Depende de la semántica verificable │ │
         │  │   del proveedor (síncrono vs asíncrono, confirmación │ │
         │  │   de aceptación, latencia de red). El instante de    │ │
         │  │   aplicación del efecto remoto puede ocurrir en      │ │
         │  │   cualquier punto durante o después de execute().    │ │
         │  └──────────────────────────────────────────────────────┘ │
         │                                                          │
         ▼                                                          ▼
  RECUPERACIÓN TRAS CRASH:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ SITUACIÓN                  │ CONOCIMIENTO      │ TRATAMIENTO           │
  │────────────────────────────│───────────────────│──────────────────────│
  │ Resultado registrado       │ Efecto confirmado │ Reutilización o       │
  │ y válido                   │ localmente        │ materialización       │
  │                            │                   │ idempotente           │
  │────────────────────────────│───────────────────│──────────────────────│
  │ Efecto no iniciado,        │ No existe efecto  │ Elegibilidad para     │
  │ demostrado                 │ externo que       │ ejecución bajo        │
  │                            │ preservar         │ autoridad válida      │
  │────────────────────────────│───────────────────│──────────────────────│
  │ Efecto externo incierto    │ No se puede       │ Política §3.2:        │
  │ (incluye lease vencido     │ determinar si     │ trazabilidad +        │
  │ sin resultado, por         │ ocurrió           │ escalamiento +        │
  │ conservadurismo            │                   │ autorización          │
  │ deliberado DC-08a)         │                   │ excepcional           │
  │────────────────────────────│───────────────────│──────────────────────│
  │ Autoridad vencida          │ El ejecutor ya    │ Protección de estado  │
  │                            │ no posee          │ local y tratamiento   │
  │                            │ autoridad local   │ del efecto            │
  │                            │ válida            │ potencialmente        │
  │                            │                   │ ocurrido              │
  └─────────────────────────────────────────────────────────────────────────┘

  (*) El execution_id del lease (identidad de intento) es distinto del
      execution_id científico definido por F18_IDENTITY_BOUNDARY_CONTRACT
      v1.0.2 (hash determinista de baseline+subject+config+parameter+profile).
      HITO_18.2.0 v1.3.0 advirtió que no deben equipararse. Esta distinción
      se preserva como condición de compatibilidad con el contrato congelado.

  Esta tabla describe distinciones lógicas; no prescribe nombres de estados,
  tablas, enums ni APIs. La materialización corresponde a ols NADRs de la Subfase 
  18.2 (pendientes de emisión).
~~~

El objetivo no es eliminar toda incertidumbre física, sino establecer un tratamiento arquitectónico verificable y compatible con INV-JOURNAL, evitando que el sistema interprete incorrectamente la ausencia de resultado como autorización para repetir efectos externos.

**Capacidades de verificación requeridas:**

El ADR define capacidades de verificación requeridas. Los métodos concretos y criterios de aceptación corresponden al Execution Plan.

1. Capacidad de caracterizar la ventana de exposición entre efecto externo y confirmación durable, dentro de los límites observables del sistema y declarando explícitamente qué categoría de duplicación se mide (reejecución del cliente, duplicación inferida, duplicación confirmada).
2. Capacidad de demostrar convergencia bajo escenarios críticos de fallo.
3. Capacidad de verificar el comportamiento de fencing en la frontera externa (no solo SQL).
4. Capacidad de observar tasa de duplicación en condiciones de operación, con indicadores que declaren sus límites de inferencia.
5. Capacidad de caracterizar durabilidad ante terminación abrupta real.
6. Capacidad de evaluar impacto económico de re-inferencia de perfiles documentales (trigger DF-34).
7. Capacidad de caracterizar tiempo efectivo de recuperación tras reinicio (trigger DF-24).

---

## 8. RELACIÓN CON OTROS ARTEFACTOS Y MODELO DE FALLOS

| Artefacto | Relación con ADR_F18.2 |
|---|---|
| ADR_F18_MASTER v1.0.0 FROZEN | Autoridad superior; define INV-JOURNAL y DC-08 |
| ADR_F18.1 v1.0.2 FROZEN | Arquitectura previa que debe preservarse |
| NADR-F18-01 v1.0.3 FROZEN | Restricciones normativas previas aplicables |
| NADR-F18-02 v1.0.1 FROZEN | Contratos de 18.1, incluido el límite de modificación señalado en §5.4 R15 |
| F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 FROZEN | Contrato de identidad y frontera que requiere verificación de compatibilidad; preserva la distinción entre identidad científica (hash determinista) e identidad de intento (lease) |
| HITO_18.2.0 v1.3.0 FROZEN | Evidencia inicial de gaps de ejecución y recuperación |
| HITO_18.2.1 v1.2.0 FROZEN | Evidencia de benchmarks, fencing SQL y crash injection |
| HITO_18.2.2 v1.4.1 FROZEN | Evidencia forense vinculante de fronteras, gaps y dimensiones de DC-08 |
| NADRs de la Subfase 18.2 (pendientes de emisión) | Futuros instrumentos de reglas técnicas vinculantes |
| PHASE_18.2_EXECUTION_PLAN (pendiente) | Futuro instrumento de ejecución y validación |

La trazabilidad de DC-08 debe conservarse como una única decisión maestra, aunque su análisis se organice en las dimensiones DC-08a, DC-08b, DC-08c y DC-08d.

| Dimensión analítica | Evidencia vinculante | Respuesta arquitectónica | Estado |
|---|---|---|---|
| DC-08a — intención pre-efecto | E-18.2.2-001, E-18.2.2-002, E-18.2.2-007 | Reutilización del lease durable existente como candidato principal; conservadurismo deliberado ante lease vencido sin resultado | RATIFICADO |
| DC-08b — efectos inciertos | E-18.2.2-005, E-18.2.2-007, E-18.2.2-008, E-18.2.2-013 | Política §3.2: no reejecución automática + trazabilidad + escalamiento + autorización excepcional | RATIFICADO CON ENMIENDA |
| DC-08c — duplicación medible | E-18.2.2-030, E-18.2.2-033 | Tres magnitudes diferenciadas (cliente / inferida / confirmada); materialización a NADR/Plan | RATIFICADO |
| DC-08d — durabilidad | E-18.2.2-014, E-18.2.2-015, E-18.2.2-016, E-18.2.2-021 | Modelo de fallos acotado (tabla siguiente); WAL+NORMAL como política inicial | RATIFICACIÓN CONDICIONADA (condición satisfecha en §10) |

### 8.1 Modelo de fallos aprobado (DC-08d)

Un sistema local que llama a un proveedor remoto sigue teniendo una frontera distribuida de efectos y conocimiento. No necesita infraestructura distribuida para reconocer esa frontera, pero sí debe declarar explícitamente qué escenarios cubre y cuáles excluye.

| Escenario | Inclusión | Garantía arquitectónica | Evidencia | Consecuencia para la política de durabilidad |
|---|---|---|---|---|
| Terminación coordinada del proceso (SIGTERM/SIGINT) | Dentro del contrato | Preservación de estado recuperable y cierre coherente | Mecanismos de shutdown observados (HITO_18.2.2 §13 Pilar 5) | WAL+NORMAL suficiente bajo shutdown ordenado |
| SIGKILL (terminación abrupta del proceso) | Dentro del contrato | Recuperación de intención persistida y tratamiento de efectos inciertos conforme a §3.2 | Convergencia demostrada para game_day_1 (HITO_18.2.1); alcance para otros puntos de fallo pendiente en Gate 4 | WAL+NORMAL suficiente bajo crash de proceso; validación complementaria en Execution Plan |
| Crash entre llamada externa y journal | Dentro del contrato | No reejecución ciega; aplicación local idempotente; tratamiento conforme a §3.2 | Escenario identificado en GAP-18.2.2-01 (P1); política de recuperación aprobada en §3.2 | Idempotencia local preservada; trazabilidad obligatoria del intento |
| Pérdida de energía (power loss) | Fuera del contrato de durabilidad garantizada | Riesgo residual documentado; no se promete recuperación completa ante este evento | Sin validación empírica en los HITOs; semántica WAL+NORMAL documentada por SQLite como EVIDENCIA DOCUMENTAL | No se exige synchronous=FULL; no se asume presencia de UPS o caché con batería sin evidencia del entorno |
| Fallo físico del almacenamiento | Fuera del contrato | No se promete recuperación ante pérdida o corrupción física irreversible | Sin evidencia suficiente en los HITOs | Fuera del alcance de la arquitectura de aplicación; responsabilidad del hardware/sistema de archivos |

### 8.2 Consecuencias honestas de WAL + synchronous=NORMAL

La política de durabilidad aprobada tiene consecuencias que deben declararse explícitamente:

- SQLite en modo WAL con synchronous=NORMAL ofrece propiedades transaccionales útiles y recuperación frente a fallos de proceso, dentro de sus condiciones documentadas.
- No ofrece la misma garantía de persistencia de transacciones confirmadas frente a pérdida de energía que una política de sincronización más fuerte.
- Excluir power loss del modelo contractual es una decisión de alcance, no una demostración de durabilidad ante ese evento.
- No puede afirmarse que una UPS o una caché con batería estén presentes sin evidencia del entorno.
- La estimación "10-100ms por write" discutida durante la deliberación queda como NO DEMOSTRADA para este proyecto y no se utiliza como justificación de la decisión.

### 8.3 Deferred Findings

| Deferred Finding | Tema | Evidencia | Disposición | Condición | Destino de seguimiento |
|---|---|---|---|---|---|
| DF-24 | CircuitBreaker persistencia | E-18.2.2-042, OBS-18.2.2-02 | **Diferimiento formal condicionado:** mantener in-memory provisionalmente, sujeto a evaluación del impacto efectivo de reinicio | Sin afirmar que el coste efectivo ya fue medido; sin aprobar ningún umbral como criterio universal de aceptación; evaluación pendiente en Execution Plan (trigger DF-24, subsumido en DC-08) | Enmienda del ADR o decisión posterior del Board cuando se cumpla el trigger; autoridad: Board |
| DF-34 | ProfileStore persistencia | E-18.2.2-044 | **Diferimiento formal condicionado:** mantener in-memory provisionalmente, sujeto a benchmark de reconstrucción | Sin presentar la reconstrucción determinista como garantía ya demostrada; sin aprobar número de documentos ni umbrales de tiempo/porcentaje como límites fundamentados; trigger DF-34 pendiente | Enmienda del ADR o decisión posterior del Board cuando se cumpla el trigger; autoridad: Board |

**Nota sobre diferimientos formales:** Un diferimiento formal condicionado no equivale a cierre del finding ni a aceptación de limitación. Es una disposición trazable con trigger, autoridad y destino de seguimiento explícitos. El finding permanece formalmente abierto hasta que el trigger se cumpla y la autoridad designada tome la decisión de cierre.

---

## 9. RELACIÓN CON METODOLOGÍA DE GOBERNANZA

Este ADR se sitúa en la cadena de gobernanza establecida por METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES v1.3.0 §2:

~~~text
ADR MAESTRO (ADR_F18_MASTER v1.0.0 FROZEN)
│
│ ¿Por qué existe Fase 18? ¿Qué capacidades requiere?
▼
ADR DE FASE (este documento: ADR_F18.2 v3.3.0 FROZEN)
│
│ ¿Cuál es la decisión arquitectónica de la sub-fase 18.2?
▼
NADR (NADRs de la Subfase 18.2, pendientes de emisión)
│
│ ¿Qué reglas técnicas vinculantes materializan la decisión?
▼
EXECUTION PLAN (PHASE_18.2_EXECUTION_PLAN, pendiente)
│
│ ¿Cómo, cuándo y quién implementa cada regla?
▼
IMPLEMENTACIÓN → TESTS / CI
~~~

### Frontera ADR → NADR

Este ADR define capacidades arquitectónicas y decisiones de subfase. NADRs de la Subfase 18.2 (pendientes de emisión) define reglas técnicas vinculantes en formato RFC-2119. El ADR no contiene:
- Reglas normativas con MUST/SHALL/MAY
- Nombres de clases o archivos concretos en reglas
- Definition of Done o criterios de aceptación operativa
- Cronograma o secuencia de tareas
- Umbrales operativos concretos (número de sweeps, tiempos de escalamiento, tamaños de benchmark)

### Frontera ADR → Execution Plan

Este ADR define qué arquitectura adoptar. El Execution Plan define:
- Tareas atómicas y secuencia (waves)
- Owners y dependencias
- Criterios de aceptación operativa
- Rollback y validaciones
- Métodos concretos para las capacidades de verificación requeridas (§7)
- Umbrales operativos concretos para escalamiento, benchmark y calibración

### Regla de precedencia

Ningún nivel inferior tiene autoridad para redefinir o contradecir decisiones establecidas por un nivel superior. Los NADRs de la Subfase 18.2 (pendientes de emisión) no puede contradecir este ADR. El Execution Plan no puede contradecir los NADRs de la Subfase 18.2 (pendientes de emisión) ni este ADR.

---

## 10. VERIFICACIÓN NORMATIVA

Conforme al punto 2 de la resolución del Architecture Board, se verifica la compatibilidad de este ADR con las autoridades congeladas.

| Autoridad | Verificación | Resultado |
|---|---|---|
| ADR_F18_MASTER §5.1 (INV-JOURNAL) | El ADR desarrolla INV-JOURNAL sin redefinirlo. Mantiene las tres propiedades (intención/lease/reserva recuperable, idempotent apply, ventana acotada y medida) como objetivo, declarando explícitamente cuáles están observadas y cuáles pendientes de validación. No declara cumplimiento integral no demostrado. | COMPATIBLE |
| ADR_F18_MASTER §5.1 (separación Recovery ≠ Exactly-once) | El ADR no promete exactly-once. Declara explícitamente que la recuperación garantiza idempotent apply + ventana de duplicación acotada, no entrega exactamente una vez. | COMPATIBLE |
| ADR_F18_MASTER §8.2 (DC-08) | El ADR materializa DC-08 como decisión única con cuatro dimensiones analíticas. No crea DCs maestros nuevos. | COMPATIBLE |
| ADR_F18_MASTER §8.3 (DF-24, DF-34) | DF-24 subsumido en DC-08; DF-34 con trigger propio independiente. Ambos como diferimientos formales condicionados, no como cierres. | COMPATIBLE |
| ADR_F18_MASTER §9.1 (cadena normativa interna) | El ADR se sitúa correctamente entre el Maestro y los NADRs de la Subfase 18.2 (pendientes de emisión) / Execution Plan. | COMPATIBLE |
| ADR_F18.1 v1.0.2 (Execution Plane & Concurrency) | El ADR preserva los mecanismos de 18.1. No modifica coordinación, shutdown, cancelación, admisión ni backpressure. | COMPATIBLE |
| NADR-F18-01 v1.0.3 (Execution Identity & Scientific Isolation) | El ADR preserva la distinción entre identidad de intento (lease) e identidad científica (hash determinista). No introduce identificadores nuevos que contradigan el contrato. | COMPATIBLE |
| NADR-F18-02 v1.0.1 §5.4 R15 (shutdown sin recovery) | El ADR no modifica los contratos de 18.1. Los cambios de recovery se materializarán en los NADRs de la Subfase 18.2 (pendientes de emisión) sin alterar 18.1. | COMPATIBLE |
| F18_IDENTITY_BOUNDARY_CONTRACT v1.0.2 (DC-02-A) | El ADR cita el contrato y preserva la distinción de identidades. No redefine fronteras de identidad. | COMPATIBLE |
| ROADMAP_ARQUITECTÓNICO_LP §V (nodo único, SQLite, sin infraestructura distribuida) | El ADR adopta arquitectura local coherente con el ROADMAP. Reconoce explícitamente la frontera distribuida de efectos introducida por el proveedor remoto sin introducir infraestructura distribuida. | COMPATIBLE |
| ENGINEERING_PRINCIPLES §I (YAGNI) | El ADR no introduce segundo journal, ni INTENT obligatorio en EventLifecycle, ni synchronous=FULL por defecto, ni framework genérico de recovery. | COMPATIBLE |
| ENGINEERING_PRINCIPLES §VII (Reuse Before Invent) | El ADR reutiliza el lease existente, la maquinaria de recovery existente y la write-policy observada. | COMPATIBLE |

**Conclusión de la verificación:** No se identifica contradicción entre este ADR y las autoridades congeladas. La condición de ratificación de DC-08d (verificación de que el modelo de fallos acotado no contradice ninguna garantía superior) queda satisfecha.

---

## 11. LIMITACIONES ACEPTADAS Y RIESGOS

Conforme al punto 3 de la resolución del Architecture Board, se registran formalmente las limitaciones aceptadas y los riesgos residuales de la arquitectura aprobada.

### 11.1 Limitaciones aceptadas explícitamente

| Limitación | Naturaleza | Justificación |
|---|---|---|
| No se garantiza exactly-once en efectos externos | Límite fundamental sin cooperación del proveedor | ADR_F18_MASTER §3 separa Recovery de Exactly-once delivery |
| No se garantiza progreso automático simultáneo con ausencia de duplicación | Trade-off reconocido por el Board | Sin cooperación del proveedor, ambos objetivos pueden entrar en conflicto |
| Power loss fuera del contrato de durabilidad | Decisión de alcance | Sistema local; responsabilidad del hardware/sistema de archivos |
| Fallo físico del almacenamiento fuera del contrato | Decisión de alcance | No es problema de arquitectura de aplicación |
| Capacidades de idempotencia del proveedor NO verificadas | Límite epistemológico | No se asumen capacidades no demostradas |
| Ventana causal real NO cuantificada | Límite de medición | Solo se dispone de estimación indirecta del intervalo cliente |
| CircuitBreaker in-memory provisional | Diferimiento formal (DF-24) | Trigger pendiente; autoridad: Board |
| ProfileStore in-memory provisional | Diferimiento formal (DF-34) | Trigger pendiente; autoridad: Board |

### 11.2 Riesgos residuales

| Riesgo | Impacto | Mitigación arquitectónica |
|---|---|---|
| Duplicación de efectos externos tras crash en ventana | FinOps (coste de tokens) | Política §3.2: no reejecución automática + trazabilidad + escalamiento |
| Tareas bloqueadas indefinidamente sin política de escalamiento efectiva | Forward progress | §3.2 exige escalamiento explícito; umbrales en Execution Plan |
| Tormenta de reintentos tras restart con CircuitBreaker frío | FinOps + disponibilidad | DF-24 diferido con trigger cuantitativo |
| Pérdida de perfiles documentales tras crash | Coste de re-inferencia | DF-34 diferido con benchmark |
| Pérdida de WAL ante power loss | Durabilidad fuera de contrato | Limitación aceptada explícitamente; documentación al usuario final |
| Sobreingeniería de recovery | Deuda técnica, YAGNI | Principio Reuse Before Invent; no framework genérico |

### 11.3 Condiciones de validación pendientes

El congelamiento del ADR no implica validación de implementación. Las siguientes validaciones corresponden a los NADRs de la Subfase 18.2 (pendientes de emisión) y al Execution Plan:

1. Suficiencia contractual del lease bajo los escenarios incluidos en §8.1.
2. Caracterización de la ventana de exposición dentro de los límites observables.
3. Comportamiento de fencing en la frontera externa.
4. Convergencia bajo los escenarios críticos del modelo de fallos.
5. Durabilidad ante SIGKILL más allá de game_day_1.
6. Materialización de las tres magnitudes de observabilidad (DC-08c).
7. Evaluación de triggers DF-24 y DF-34.

---

## 12. CIERRE Y SIGUIENTE PASO

**Estado del ADR:** FROZEN v3.3.0. DC-08 cerrado a nivel de decisión arquitectónica. La validación de implementación corresponde a los NADRs de la Subfase 18.2 (pendientes de emisión) y al Execution Plan.

**Contradicciones con artefactos previos:**

- HITO_18.2.1 v1.2.0 estimaba ventana ~1ms como OBSERVADO. HITO_18.2.2 v1.4.1 la reclasificó como ESTIMACIÓN INDIRECTA HEREDADA. Este ADR adopta la clasificación de HITO_18.2.2 y precisa que ~1ms es una estimación indirecta del intervalo cliente, no cota de la ventana causal.
- HITO_18.2.0 v1.3.0 identificó GAP-18.2.0-01 como P1. HITO_18.2.2 v1.4.1 lo consolidó como GAP-18.2.2-01 P1 con evidencia más profunda. Este ADR adopta la consolidación de HITO_18.2.2.
- ADR_F18.1 v1.0.1 eliminó DC-13 del registro canónico. Referencias residuales en documentos derivados constituyen deuda documental. Este ADR no reabre DC-13.

**Siguiente paso recomendado:**

1. Definir y emitir NADRs con reglas técnicas vinculantes en formato RFC-2119 que materialicen:
   - Política de recuperación bajo incertidumbre (§3.2)
   - Tres magnitudes de observabilidad (DC-08c)
   - Modelo de fallos y write-policy (DC-08d)
   - Diferimientos DF-24 y DF-34 con sus triggers
2. Emitir PHASE_18.2_EXECUTION_PLAN con:
   - Tareas atómicas y secuencia (waves)
   - Umbrales operativos concretos para escalamiento
   - Capacidades de verificación requeridas (§7) con métodos concretos
   - Triggers y benchmarks para DF-24 y DF-34
3. Ejecutar validaciones pendientes (§11.3) en Gate 4 del Execution Plan.

---

**Nota de Gobernanza:** Este ADR es una decisión de subfase. No define reglas normativas RFC-2119 (eso corresponde a los NADRs de la Subfase 18.2, pendientes de emisión). No define secuencia operativa (eso corresponde al Execution Plan). No constituye evidencia forense (eso son los HITOs). Toda afirmación conceptual nueva a partir de este punto entra como decisión con evidencia, no como análisis textual. La versión v3.3.0 está FROZEN y constituye la referencia canónica para los NADRs y PHASE_18.2_EXECUTION_PLAN.