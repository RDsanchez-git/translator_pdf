# Decisión de convergencia D-1 / D-2 — Contrato único de producto PDF→PDF

**ESTADO VIGENTE — DIRECCIÓN D-1/D-2 APROBADA POR EL OWNER (confirmación 2026-11-08).** El owner ratificó expresamente que la convergencia ya había sido aprobada y que se está implementando conforme a esta decisión. Por tanto, **D-1 (un único contrato PDF→PDF desde la CLI) y D-2 (continuidad G3→G5 como referencia técnica condicionada, con transferencia selectiva R1/R3) no están pendientes de nueva aprobación de dirección**. Se preservan sus límites técnicos, las garantías FROZEN y la separación entre integración de código, activación productiva y certificación científica.

**Trazabilidad de autoridad:** esta actualización registra la confirmación explícita del owner; no inventa fecha/acta/voto independiente del Architecture Board. Las etiquetas `CANDIDATE / NON-NORMATIVE / NOT APPROVED` y menciones a G-1/G-2 pendientes que figuran más abajo describen **el estado histórico al corte del 2026-11-05**, no la dirección vigente. Las obligaciones de implementación, validación y operación G-3/G-4/G-5 siguen siendo evaluables por separado. El nombre original del archivo se conserva para no romper enlaces.

---

**Fecha de corte:** 2026-11-05 (evidencia histórica; revisión documental sobre ese corte)  
**Edición:** `v0.2.1 — PRECISIÓN FORENSE + EVALUACIÓN G-1…G-5 PARA BOARD` (artefacto de trabajo; **no** versionado normativo)  
**Estado del expediente al 2026-11-05:** `CANDIDATE / NON-NORMATIVE / NOT APPROVED` (estado histórico, supersedido para la dirección D-1/D-2 por la aprobación del owner arriba)  
**Destinatario histórico del expediente:** Architecture Board; D-1/D-2 estaban pendientes al 2026-11-05  
**Repositorio:** `RDsanchez-git/translator_pdf`, rama `pipeline_stabilization`  
**Sujeto funcional:** [`d4cda2c379c0efd93a70e795d31c37a0ede7a192`](https://github.com/RDsanchez-git/translator_pdf/tree/d4cda2c379c0efd93a70e795d31c37a0ede7a192)  
**Gobierno:** Charter v0.1.0 `DRAFT`, Atlas v0.2.16 `IN_PROGRESS`, NADR-F18-02/03/04/05 `FROZEN`.  
**Tipo de evidencia:** `S` inspección estática; `H` registros históricos con sujeto delimitado; `V` artefactos históricos verificados; `P` propuesta de contrato, no implementación; `U` sin acreditar.  
**No es:** ADR nuevo, decisión ratificada, orden de implementación, autorización de nuevos tests, reclasificación `KEEP/RETIRE`, ni certificación del producto.

**Proveniencia de esta revisión:** se conserva como fuente inmutable el Decision Candidate original SHA-256 `f7061ed16e9ee6fdd6e74d4ccc6396208af4163e04c69ebeb6691bd0f6b7592a` (incluido idéntico en `Audit 10.rar` y `Continuación real.rar`). Esta edición deriva de **v0.2**, SHA-256 `3802a7f18bb022f9054a11d3473e2a97e96d0096ce1cd472cf7b7953ee3ccc3d`, sin sobrescribirla. Incorpora reservas forenses sobre extracción, contexto R1, handoff CLI y concurrencia R2/R3, además de la evaluación de G-1…G-5 frente a obligaciones vigentes. **No se ha ejecutado ninguna nueva prueba dinámica ni existe voto del Board.**

## 0. Decisión solicitada y límites

**D-1 candidata — contrato de producto:** una sola cadena contractual para PDF→PDF, con entrada CLI como adaptador y procesos OCR/LLM/Reconciler/Assembler especializados, sin motores de traducción productivos competidores. El número de procesos no se restringe a uno.

**D-2 candidata — referencia de continuidad:** evaluar como punto de partida el grafo R2/G3→G5 porque es la única variante que ha alcanzado un PDF físico en ejecución integrada controlada, **sin aprobar por ello su extractor, calidad científica, composición Compose base o autoridad F18 integral**. R1 aporta funciones semánticas y de validación; R3 aporta mecanismos operativos. Su aprovechamiento se decide por contrato demostrado, no por copiar ejecutores enteros.

**No solicitado:** declarar retirados `AsyncDispatcher`, `LLMWorkerDaemon` o sus consumidores; reescribir el AST; sustituir G3/G5; abrir infraestructura distribuida; modificar NADR FROZEN; seleccionar Docling hoy; convertir un único paper en criterio universal.

**Gate de gobierno:** El Charter [§3 D-1/D-2 y §10](https://github.com/RDsanchez-git/translator_pdf/blob/pipeline_stabilization/docs/architecture/adr/pipeline-stabilization/00-foundation/PIPELINE_STABILIZATION_AUDIT_CHARTER.md) sigue `DRAFT`. La presente propuesta no satisface por sí misma las aprobaciones pendientes ni autoriza remediación F18.2 fuera del alcance del Charter §4.2. El Board puede aceptar la dirección, condicionarla o rechazarla.

### 0.1 Invariantes de producto: Paso 0 de la secuencia acordada

Estos invariantes se **recuperan** del `PROJECT_SCOPE.md` (§§1, 2 y 4), de los contratos del Atlas y de NADR aplicables; no se introducen métricas, tipos documentales ni oráculos nuevos:

| Obligación de producto | Traducción a frontera verificable | Referencia | Lo que NO constituye prueba |
|---|---|---|---|
| Completitud topológica y linaje | Elemento relevante del PDF → bloque/AST → miembro/unidad → proyección/activo → salida, con pérdidas y cambios explícitos | Scope §4; Atlas CAP-02/03/04/09/12, CTR-02/08/12 | `ChunkPlan` íntegro cuando la extracción omitió un elemento |
| Robustez científica y técnica | Matemáticas, código, identificadores, tablas/figuras pertinentes no se alteran silenciosamente; `PRESERVE` evita inferencia cuando corresponde y se verifica físicamente | Scope §4; Atlas CAP-07/09/10; CTR-10/11/12 | Eco de fake o PDF que abre y tiene páginas |
| Traducción lingüística fiel | Para `TRANSLATE`, el resultado debe ser una traducción evaluable, no eco; no confundir modo fake con validación de idioma | Scope §§1–2; Charter §6.2 | 59/59 ecos del original en P5 R2 |
| Layout y reconstrucción | Documento compilado a partir de AST/proyecciones/perfil/activos de la generación correcta, con evidencia visual/geométrica pertinente | Scope §§1–2; Atlas CAP-09/10/12 | FSM `COMPLETED` sin correspondencia científica |
| Resiliencia, idempotencia y costo | Autoridad persistente, recuperación compatible con fallo incierto, presupuesto y límites de recursos por efecto externo | Scope §4; Principios; NADR-F18-02/03/04/05 | Lease válido antes de timeout, ausencia de errores en CI o cancelación local |

**Generalidad:** considerar las clases ya registradas en el corpus (`heavy_math`, `scanned_noise`, `multi_column`, `nested_tables`, `floating_figures`, `bilingual_mix`, entre otras), sin convertirlas aquí en un nuevo estándar de evaluación. El expediente transversal registra 21 casos en manifest/oráculos pero disponibilidad física distinta según Git/host; esa cobertura documental **no** significa 21 ejecuciones E2E. El paper discutido es únicamente candidato a testigo adicional con custodia y admisión explícita.

**Resultado de Paso 0:** los invariantes están definidos a nivel de contrato existente. **No acreditados como garantías de producción**. La propuesta no cambia el modelo de AST ni la definición formal de métricas de 17-BIS.

### 0.2 Regla de autoridad y cambios respecto de la inclinación del Charter

El Charter v0.1.0 `DRAFT`, §3 D-2, es explícito: el **objetivo** es el plano persistente con garantías F18 y la **inclinación inicial no vinculante** era `pipeline_factory`/`AsyncDispatcher` con cola/FSM. Esta candidatura se inclina ahora por las **fronteras durables R2 G3→G5** porque el expediente de R1 no acreditó handoff al Assembler ni PDF, R3 estático quedó bloqueado, y R2 sí tiene un testigo PDF físico controlado y recibos durables. Esto es **delta razonado por evidencia posterior**, no revocación silenciosa del Charter ni conclusión automática de §6.1.

El Charter §6.1 registra `A/B/C` como **resultado de caracterización E2E**, no como nota de calidad científica. El `A` físico de R2 coexiste con `scientific_verdict=FAIL` y con garantías operativas `UNKNOWN`; R3 tiene estado `NO ELEGIBLE — PRECONDICIÓN` y no un E2E `C` inventado. Las condiciones de §6.1 siguen sometidas a la decisión del Board, incluido cómo interpretar rutas no elegibles. Cualquier corrección del preregistro requiere su autoridad.

**Separación de votos:** D-1 puede aprobarse como principio de contrato único sin elegir un ejecutor; D-2 puede admitir una **referencia candidata de continuidad** sin aprobar todavía el diseño final ni autorizar código. En ambos casos los NADR `FROZEN` prevalecen sobre recomendaciones locales.

## 1. Sujeto AS-IS y por qué no elegir por «ruta ganadora»

| Ruta | Lo que demuestra/codifica | Límite pertinente |
|---|---|---|
| **R1 CLI** | Clasificación/contexto jerárquico, validación/healing y `AsyncDispatcher`; componentes compartidos de AST y chunking | Histórico STOP `GLOBAL_ROOT` antes de fake LLM; no entrega proyecciones G3/AST al Assembler; sin PDF propio acreditado |
| **R2 OCR/Engine/G3–G5** | AST/plan durables, `TaskLease`, receipt G3, publicación por miembro, Assembler/Tectonic y PDF físico controlado | P5: 5 receipts, 61 proyecciones y 4 páginas; **scientific_verdict=FAIL**; sin autoridad/incertidumbre F18 certificada; Compose base no equivale al sujeto P5 |
| **R3 daemon alternativo** | Admisión RSS, backpressure, heartbeat, cancelación, shutdown | `claim_next_pending_task` y `mark_task_failed` ausentes del repositorio que instancia; contratos legacy nodo≠chunk; sin E2E R3 |

**Disciplina probatoria:** G5/2 acreditó casos SIGKILL de Assembler en laboratorio sintético histórico, no exactly-once de llamadas LLM ni resiliencia científica del P5 integrado. El estado de los expedientes es caracterización, no certificación. Fuente: expedientes R1/R2/R3, comparación transversal AS-IS y [acta G5/2](https://github.com/RDsanchez-git/translator_pdf/blob/pipeline_stabilization/docs/architecture/adr/pipeline-stabilization/G5_2_CERTIFICACION_Y_REPRODUCCION_20261030.md).

## 2. Grafo único candidato de responsabilidades (no diagrama de código ya conectado)

```text
CLI/API/Batch → admisión documental + identidad PDF
                       │
           Extracción / Layout / AST plano
     [cobertura científica y activos trazables]
                       │
        clasificación/estrategia coherentes
                       │
        ASTRegistry + perfil + ChunkPlan G3
                       │
                queue.db: TaskLease
                       │
           admisión de recursos / precheck
                       │
          ┌────────────┴─────────────┐
          │                          │
     TRANSLATE/PARTIAL             PRESERVE
          │                          │
 contexto durable, prompt,       bypass local
 modelo/config, efecto LLM       sin llamada LLM
          │                          │
 validación/healing bajo         original recuperable
 autoridad + efecto incierto      y conservación verificable
          └────────────┬─────────────┘
                       │
         receipt G3 + intento causal durable
                       │
      publicación idempotente por AST node_id
                       │
       AST + proyecciones + perfil + activos
                       │
         G5 Assembler → TeX → PDF privado
                       │
      validación científica / promoción fenced
                       │
          PDF final + estado consistente

   Reconciler: recovery de resultados y disposición
   de intentos inciertos, NUNCA retry ciego.
```

Los invariantes de G3/G5 se conservan; **los vínculos de procedencia, cobertura de activos, validación científica y gestión de incertidumbre del diagrama son requerimientos candidatos pendientes de implementación/verificación**. `PRESERVE` no se traduce en la unidad de R2 actual: [stage_claimed_unit](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/runtime/chunk_staging.py#L24-L64).

### 2.1 Propietarios de contratos y autoridad; no corresponde a servicios nuevos

La propuesta describe **un recorrido lógico de producto**, potencialmente multiproceso. A continuación `propietario candidato` designa **responsabilidad a asignar y verificar**, no código ya integrado:

| Frontera | Qué debe persistir o poder recuperarse | Propietario candidato/reutilización | Condición de falsación |
|---|---|---|---|
| Entrada → extracción | identidad bytes PDF, fuente, políticas de admisión, procedencia y perfil | CLI/API como entrada; OCR/extracción compartida | mismo PDF se procesa con identidades inconciliables o pierde regiones sin aviso |
| Layout → AST | nodos, jerarquía, geometría, activos y vínculos necesarios sin adulteración | proveedor + ASTRegistry/perfil existente | fuente tiene estructura reconocible omitida o transformada de forma irrecuperable |
| AST → ChunkPlan | miembros `node_id`, orden, estrategia, hash/generación, cardinalidad N→1→N | `ChunkPlan` G3 y validadores actuales | miembro sin cobertura, colisión nodo/chunk o `PRESERVE` en unidad `TRANSLATE` |
| Plan → claim | `task_id`, `execution_id` vigente, lease/fence y decisión pre-efecto durable | `ControlPlaneRepository`/Engine G3 | una vía obtiene permiso para llamar sin autoridad o desconoce un intento incierto |
| Prompt → proveedor | contexto efectivamente resuelto, bytes/estructura del prompt enviado, modelo/versión/opciones, identidad de intento | `PromptBuilder`/bridge + capacidades semánticas compatibles | cache/replay responde bajo contexto/configuración distinta |
| Resultado → receipt/publicación | respuesta, validación y disposición causal ligadas al intento/miembros; proyección por nodo con fencing | receipts G3 + publicación G3 | resultado de otra generación/autoridad se materializa o reemplaza same-version |
| Proyección → Assembler → PDF | AST/perfil/activos recuperables, lote íntegro, versión/fence y trazabilidad del artefacto | `CQRSAssemblyContextResolver`, G5, Tectonic | PDF no atribuible o `COMPLETED` sin evidencia física/científica |
| Fallo → reconciliación | evidencia de efecto externo / no-inicio / resultado durable / incertidumbre y decisión autorizada | control plane + Reconciler/Sweeper existentes | cualquier recuperación evita la decisión de elegibilidad y repite LLM incierto |

**Reserva de frontera D-1 / handoff CQRS (R1, `ATLAS-RTE-05`, W-05).** El recorrido CLI R1 inspeccionado utiliza `documents.db` para unidades, despacha respuestas y emite `MarkAssemblyReadyCommand`, **pero no acredita** registrar el AST en el `ASTRegistry` compartido, generar el `ChunkPlan` G3 o materializar por `node_id` los datos que G5 espera en `valid_chunks_cache`. Una orden `READY_FOR_ASSEMBLY` no aporta por sí misma los precursores físicos de ensamblado. **La consecuencia contractual obligatoria es cerrar esa frontera de productor→consumidor; no convertir automáticamente a la CLI en un segundo escritor de planes, receipts y proyecciones.** Bajo D-1 la CLI puede limitarse a admisión y solicitud documentada, dejando generación de AST/plan, claim, staging y publicación a la única composición productiva autorizada. Si se eligiera preservar la orquestación R1 como ejecutor, el delta CQRS sería mayor y necesitaría justificación comparativa y gates propios. Ambos diseños requieren demostrar handoff recuperable desde proceso nuevo; ninguno se declara implementado.

**Una sola fuente autoritativa por hecho.** `queue.db` puede ser autoridad de tareas/receipts y `materialized.db` de proyecciones sin fusionar esos DB. El contrato exige consistencia observable y recuperación, no una transacción ACID ficticia entre SQLite, filesystem y proveedor. El Assembler consume resultado y activos necesarios, no toda la conversación jerárquica del prompt. Los activos físicos no se copian a `materialized.db` por reflejo.

## 3. Pilar A — fidelidad científica y fallo explícito

**Contrato mínimo candidato:** cada estructura relevante del PDF fuente debe estar (a) recuperablemente representada y trazada al Layout/AST y luego al renderer, (b) preservada con equivalencia científica/visual demostrable, o (c) declarada `UNRESOLVED`/fallida explícitamente. La completitud documental es distinta de la cobertura interna del `ChunkPlan`.

**Condiciones que impiden una falsa solución:**

- `PyMuPDFProvider` productivo declara `supports_math=False`; el recorrido actual no acredita ecuaciones, tablas y figuras completas. El mero etiquetado heurístico de R1 no repara glifos perdidos.
- `DoclingProvider` existe, pero su adaptador y los consumidores AST/render siguen teniendo límites; `supports_math=True` no demuestra fidelidad E2E. La elección de proveedor queda **abierta y condicionada a pruebas de productor→consumidor**.
- `PRESERVE` de un texto ya corrupto preserva la **corrupción**. Para una región original físicamente recuperable puede evaluarse conservación controlada como activo/región anclada, con evidencia de fidelidad; de lo contrario, rechazo explícito. No inventar un «LaTeX original» desde glifos ambiguos ni asumir que pasar una imagen por LLM garantiza exactitud.
- La observación referida al carácter `￿` exige cuidado: el carácter mostrado es **U+FFFF** (noncharacter Unicode), mientras `�` es **U+FFFD** (replacement character). No equivalen y U+FFFF tampoco es, por sí mismo, un carácter del área de uso privado. Sin inspección de los bytes y la salida de cada frontera no puede atribuirse la pérdida a una etapa específica ni identificar qué símbolo matemático debería reemplazarlo. **Su observación en el paper externo no demuestra que fuera ese mismo carácter el registrado en `doc_01_single.pdf` durante P5-R2.**
- **Reserva forense de causalidad (R2):** `PyMuPDFProvider.capabilities.supports_math=False` es una **declaración de capacidad**; el dato P5 de 0 ecuaciones tipadas y la pérdida científica física son **observaciones de integración**. Su coexistencia acredita un riesgo de cobertura, **no** que esa propiedad haya reemplazado los glifos ni que un error de `/ToUnicode`, `font cmap`, área de uso privado, heurística o mapeo AST sea ya la causa probada. El código omite bloques no textuales; el punto exacto de primera pérdida entre fuente→extracción→layout→AST→renderer permanece `NOT_ISOLATED`. El selector de extracción productivo observado únicamente construye PyMuPDF; `DoclingProvider` declara `supports_math=True`, pero su conexión real y mapeo de fórmulas hasta AST/renderer tampoco están acreditados.
- **No se adjuntó en este intercambio el PDF/texto íntegro** del paper «Minimum Viable Scale Extinction...». Por ahora se trata como **testigo sugerido, no fixture aceptado**. Antes de usarlo: input exacto, SHA-256, custodia y correspondencia con corpus/oráculo. El Charter §4.2 excluye rebaseline del corpus y modificación de oráculos sellados.

**Prueba decisiva:** usar **W-09** según Atlas —ecuaciones inline/display, código e imagen; medir interfaz/egress y salida o fallo explícito— más casos representativos de tablas, columnas, figuras, scan y matemática del corpus disponible. No reducir el estándar científico a un solo paper.

### 3.1 Paso 1 — Diagnóstico vs elección de mecanismo

**Primer punto de pérdida conocido, con precisión probatoria:** en P5-R2 el AST inspeccionado sobre `doc_01_single.pdf` ya tenía 61 nodos (59 párrafos, 2 encabezados) y **0 nodos matemáticos**, mientras el oráculo de referencia del expediente registra nodos de ecuación; el fake posterior únicamente devolvió eco. Por ello el daño es **anterior al fake**, pero la función exacta entre extracción, clasificación, normalización y proyección **NO quedó aislada dinámicamente**. El código del `PyMuPDFProvider` omite bloques no textuales; eso constituye un límite estático adicional para figuras, no una prueba automática de cuál causó E2-02.

**Regla para una decisión futura de extractor:** comparar el proveedor que alimenta **toda la cadena** (layout, AST tipado, geometría/activo, estrategia, proyección y renderer) contra los mismos rasgos/oráculos existentes. Docling y PyMuPDF deben evaluarse como alternativas de adaptación *productor→consumidor*, no por el atributo `supports_math` aislado. Una imagen/fallback físico es aceptable solo si dispone de región original verificada y su salida conserva información requerida; rasterización indiscriminada puede comprometer traducción, accesibilidad y fidelidad de layout.

**Disposición:** el cierre científico del producto sigue **`NOT_DEMONSTRATED`**, con E2-02 en **`FAIL`** dentro de su alcance. Ningún gate debe tratar un PDF físicamente válido como excepción a ese veto de producto. No fijar nuevo umbral NSS ni corregir oráculos sellados en esta unidad.

## 4. Pilar B — identidad de inferencia, contexto y materialización

**Mantener** `ASTRegistry` como fuente de nodos y geometría, `ChunkPlan` para miembros/estrategia/orden, receipts para resultado durable y `valid_chunks_cache` para proyección textual. Evitar copiar binarios/bbox a cada fila CQRS sin necesidad demostrada.

**Cerrar brecha causal:** una traducción reutilizable debe vincular (operación lógica: documento/generación/chunk/miembros) ↔ (contexto resuelto usado) ↔ (prompt efectivo luego de compresión/masking) ↔ (modelo, proveedor, versión y parámetros relevantes) ↔ (intento `execution_id` y autoridad) ↔ (resultado validado y receipt). El `prompt_hash` actual solo cubre el esquema del prompt y `CachedLLMProvider` busca por él sin verificar toda la configuración; el replay legado no identifica contexto íntegro. **No confundir huella de inferencia con clave de idempotencia remota.**

El `compute_ast_hash()` semántico **excluye** `node_id`, `sequence_id` y metadata física, pero **sí es sensible al orden de los nodos**. Su contrato está expresamente marcado en `core/ast/hashing.py` como **alternativo para comparación de parsers/topología**, no como identidad canónica del linaje de baseline; esa frontera corresponde al `OracleSemanticIdentityCalculator`. El handoff productivo requiere conservar referencias y generaciones recuperables sin elevar `ast_hash` por sí solo a identidad científica integral. R1 aporta contexto jerárquico, pero su contrato `GLOBAL_ROOT`/breadcrumbs no se puede cablear sin reconciliar tipos y disponibilidad entre procesos. **Reserva de integración (R1 P2):** la ejecución original sufrió `STOP` dinámico antes de tráfico al fake: `KeyError: UNKNOWN_CONTEXT_IDS: ['GLOBAL_ROOT']`. El `ContextAwareSemanticGrouper` puede producir el fallback `GLOBAL_ROOT`, mientras el `ContextRegistry` observado no ofrecía un mapping recuperable para resolverlo. `DynamicContextResolver` **falló correctamente de forma explícita** ante un ID ausente; no constituye evidencia de que su política fail-fast sea defectuosa. La reutilización exige reconciliar **productor de contexto → mapeo → resolución/hidratación → identidad del prompt → disponibilidad interproceso**. El diagnóstico V2.1 alcanzó construcción de prompts en alcance acotado, pero no se incorporó como reparación productiva. Sustituir el error por breadcrumbs vacías no satisface el contrato de contexto. Validación/healing de R1 son candidatos **después** de definir su integración con validación por miembro, receipts y reintentos externos gobernados: no se prescribe poner todo dentro de `SyncProviderBridge`.

**`PRESERVE` G3 actual:** un receipt sin `raw_response` para una unidad que el manifiesto tipa `PRESERVE` ya diferencia bypass de un resultado LLM; **no es indispensable añadir un booleano redundante** `inference_bypassed` antes de probar una brecha de audibilidad concreta. Acreditar aparte ausencia de llamada al proveedor y conservación física.

### 4.1 Paso 2 — Huellas y claves: distinciones obligatorias

| Identificador/dato | Significado | Lo que **no** demuestra |
|---|---|---|
| `document_id` y referencia de PDF | identidad de documento/bytes bajo contrato actual, con ID de job de CLI como alias externo cuando corresponda | que AST, imagen y perfil sean equivalentes |
| `ast_hash` semántico | contrato alternativo de comparación topológica: `node_type`+contenido, **sensible al orden**; excluye `node_id`, `sequence_id` y geometría | identidad canónica de baseline (`OracleSemanticIdentityCalculator`), imagen, bbox, contexto o ejecución |
| `node_id` / `chunk_id` | miembro materializable / unidad agregada de traducción; no son intercambiables | que un `chunk_id` encuentre un ASTNode |
| `manifest_sha256` / `ChunkPlan` | membresía y estrategia N→1→N reproducibles | cobertura de lo que el extractor nunca representó |
| `prompt_hash` existente | huella de esquema de prompt bajo el canonicalizer | identidad suficiente del proveedor, opciones efectivas, efecto remoto o deduplicación |
| `execution_id` y receipt | intento/autoridad local y resultado comprometido cuando existe receipt verificable | que un intento sin receipt jamás alcanzó al proveedor |
| `projection_version` + atestación G3 | versión local/publicación de proyecciones autorizadas | equivalencia científica del PDF resultante |

**Contrato de inferencia efectiva (conceptual):** debe ser posible verificar qué contexto **se resolvió de verdad**, qué transformaciones afectaron el prompt final, qué proveedor/modelo/versión/opciones relevantes se emplearon, qué intento tenía autoridad y qué respuesta validada llegó a cada miembro. La implementación puede usar hashes, referencias y metadatos existentes si se prueban suficientes; no se decreta ahora un DTO universal ni se replica todo en cada plano. El contenido que requiera protección de privacidad o presupuesto se ancla mediante evidencia duradera suficiente, sin publicar secretos.

**Política de cache/replay:** hit permitido únicamente cuando la identidad de inferencia y la política de reutilización prueben compatibilidad; mismatch → miss seguro, nunca sustitución silenciosa. El `event.db` legado, `llm_translation_cache`, receipts y `valid_chunks_cache` no son cuatro sinónimos de «journal»: tienen finalidades distintas y deben reconciliarse sin fuentes de verdad competitivas. `PRESERVE` necesita prueba separada de bypass y de integridad del activo, además de su distinción en el plan y receipt; un nuevo booleano `inference_bypassed` es opcional, no presupuesto del diseño.

**Falsador:** dos casos con mismo texto pero contexto/modelo/opciones distintos no deben recuperar indebidamente una respuesta idéntica mediante caché/replay; W-08 y pruebas condicionadas por generación deben seguir el Atlas.

## 5. Pilar C — autoridad e incertidumbre F18-03, sin prometer exactly-once externo

### 5.1 Situaciones epistemológicas mínimas

| Situación | Evidencia recuperable | Disposición permitida |
|---|---|---|
| `NOT_STARTED_PROVEN` | Prueba suficiente de no cruce a la frontera de efecto | Reejecución automática elegible |
| `LOCAL_RESULT_DURABLE` | Receipt/source autoritativa comprometido y verificable | Recuperar publicación y ACK local; **no repetir LLM** |
| `EXTERNAL_EFFECT_UNCERTAIN` | Efecto pudo ejecutarse; resultado ausente o no verificado | Bloquear todo retry automático, conservar intento y primera detección, escalar |
| `AUTHORIZED_EXCEPTION` | Autorización y aceptación explícita del riesgo durables | Reintento excepcional correlacionado, medible, no implica efecto previo ausente |

Estas etiquetas son **conceptuales**, no un mandato de agregar exactamente cuatro estados a la FSM documental o a `chunk_tasks`.

### 5.2 Controles que deben cubrir **todas** las vías

En el commit inspeccionado:

- [`pick_task()`](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/control_repo.py#L340-L375) reclama `PENDING`/`RETRYABLE_ERROR` y asigna un `execution_id` nuevo en la fila mutable.
- [`abandon_execution()`](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/control_repo.py#L389-L405) puede convertir un error tras I/O en `RETRYABLE_ERROR`.
- [`recover_expired_g3_task()`](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/control_repo.py#L474-L529) reencola `PROCESSING` expirado sin receipt, con CAS/epoch válidos pero sin acreditar no-inicio remoto.
- El [Engine](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/runtime/engine.py#L180-L218) también dispone de liberaciones `release_task_untouched` para circuit breaker y rutas de recuperación de FSM. Todas las transiciones que habiliten trabajo externo deben respetar la misma clasificación.

**Convergencia candidata:** una decisión de elegibilidad común (o contrato equivalente) debe impedir que scheduler, Engine, Reconciler, Sweeper o reinicio recuperador salten una cuarentena semántica de incertidumbre. El registro de intento debe conservar `execution_id` original, operación lógica estable, identidad de inferencia, primera detección, evidencia causal y disposición. No basta una marca efímera en memoria ni un mensaje en `error_log` que pueda sobrescribirse.

### 5.3 ¿Nueva tabla lateral?

**Necesidad demostrada:** historial durable y recuperable por intento; `chunk_tasks.execution_id` mutable y receipt único por chunk no acreditan el historial completo de múltiples intentos inciertos.  
**Decisión de almacenamiento NO demostrada:** una tabla append-only en `queue.db` puede ser la solución mínima si permite registrar intención y claim en una transacción local, pero también debe contrastarse con una evolución de un journal existente sin crear dos fuentes de verdad ni exigir commit atómico entre DB distintas.  
**Regla:** elegir una sola fuente autoritativa para historial/intentos/disposición y reconstruir proyecciones desde evidencia local. Nueva tabla **condicional**, no «inevitable» sin prueba de alternativas. Tampoco una nueva FSM documental por defecto.

**Groq:** [`GroqProvider.translate()`](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/apps/llm_workers/adapters.py#L12-L59) llama a chat completions sin clave explícita de idempotencia. La [referencia pública de la API](https://console.groq.com/docs/api-reference) consultada no acredita en este análisis la deduplicación recuperable de una solicitud síncrona por `prompt_hash`/`execution_id`. No suponer `GET status by hash`, `exactly-once`, ni que `future.cancel()` revierte coste/efecto remoto. El parámetro `seed` de la referencia pública, cuando corresponde, tampoco proporciona garantía de determinismo absoluto ni de no duplicación de efectos externos. Cualquier soporte proveedor-específico exigiría verificación independiente.

**Bounded execution:** evaluar reutilizar `ExecutionEnvelope`, los **contratos** de admisión/backpressure, `CancellationToken`, coordinación y observabilidad de R3 en el Engine G3, **solo si** se identifica una garantía F18-02 insuficiente; no dar por supuesto que sus implementaciones `Sequential*` sean reutilizables sin adaptación. `TaskLeaseHeartbeat` de R3 **no se injerta literalmente**: renueva por `task_id`/owner, no por `execution_id`/versión, y su valor de vigencia previo a I/O se guarda localmente. No adoptar `LLMWorkerDaemon` ni sus APIs incompatibles.

**Reserva de modelo de concurrencia (R2/R3; NADR-F18-02 §5):** R3 inspeccionado ejecuta admisión RSS **antes del claim** en un loop pull-based secuencial; `HOLD` detiene el pull mediante espera interrumpible. R2/G3 utiliza `ThreadPoolExecutor` con `MAX_CONCURRENT_CHUNKS` y `GLOBAL_LLM_SEMAPHORE`, con varias adquisiciones y efectos potenciales en vuelo. Un precheck RSS secuencial no garantiza por trasplante la admisión acotada del conjunto concurrente; podrían existir carreras de admisión y recursos en vuelo sin que eso constituya **una incidencia dinámica demostrada**. Comprobar R1–R19 y R23–R25 pertinentes de F18-02 sobre el **mismo sujeto concurrente**, incluidos presupuesto efectivo, propagación de presión, cancelación, shutdown, seguridad y neutralidad científica. El `safety_margin=0.90` de R3 es parámetro de ese mecanismo, **no** nuevo umbral de producto. No añadir daemon, scheduler o control duplicado por inercia.

### 5.4 Journal CP-08 y recuperación G5

`chunk_result_receipts` es fuente durable autoritativa de resultados G3; `g3_plan_publications` atestigua materialización; `chunk_events_log` legacy sirve otras responsabilidades. En P5 constan **5 receipts y 0 eventos**; no declarar CP-08 cumplido sin reconciliar formalmente su modalidad/contrato. La mera duplicación de escritura de respuesta en `event.db` no cura la ventana previo al receipt ni el efecto remoto incierto.

G5/2 acreditó SIGKILL de Assembler en sujetos sintéticos históricos; **no** una llamada LLM exactamente una vez. `os.replace()` antes de `COMMIT` deja ventana filesystem/SQLite; el error normal `FAILED_RETRYABLE`/tarea `FAILED` necesita política de recuperación coherente. No introducir un journal remoto para reparar G5.

### 5.5 Paso 3 — Secuencia de decisión antes de efectos externos

1. **Claim y elegibilidad:** la autoridad local identifica operación lógica, intento y lease. Antes de autorizar I/O, persiste de manera recuperable lo necesario para recuperar el caso incierto; la evidencia y la autoridad deben corresponder a la misma generación/versión. El mero claim no prueba que no se haya contactado al proveedor.
2. **Cruce de frontera:** si hay prueba suficiente de que no se emitió I/O, `NOT_STARTED_PROVEN` puede ser elegible para repetición; si el proceso cayó entre la marca de intención y el envío de HTTP, sin prueba de no-inicio, la interpretación segura es **incierta**, aun cuando eso reduzca liveness.
3. **Respuesta y durabilidad:** la respuesta en RAM no es receipt; si cae antes de quedar recuperable, la recuperación no puede inferir ausencia de efecto externo. Si existe receipt íntegro, se rematerializa sin nuevo LLM.
4. **Timeout/cancelación:** `future.cancel()` o vencimiento del lease no revocan retroactivamente un request procesado por Groq. F18-03 prohíbe elegir ciegamente el retry solo porque `retry_count < max_retries`. Se registra primera detección de incertidumbre y se exige disposición autorizada antes de toda nueva llamada.
5. **Reconciler/Sweeper/restart:** todas las vías que habilitan `PENDING`/`RETRYABLE_ERROR` para nuevos I/O deben aplicar una política común de elegibilidad con prueba local. Las tareas de *republicación* pueden ser seguras sin proveedor si se basan en resultado durable y fencing válido.
6. **Excepción:** cualquier reejecución autorizada tiene que conservar la relación entre intento original, nueva intención, autoridad aprobatoria, aceptación explícita de exposición y resultado final. No demuestra que no existió costo o efecto previo; F18-05 distingue **intentos del cliente** de **duplicación externa demostrada**.

**Decisión de estructura de almacenamiento reservada:** comparar A) extender journal autoritativo existente si puede registrar claim/intención y resolución sin ventana transaccional peligrosa; B) historial por intento en `queue.db` con transacción local junto a la tarea; C) otro mecanismo de durabilidad ya existente si supera las mismas pruebas. La opción que demande commits cruzados entre DB sin recuperación definida, o dos registros autoritativos incompatibles, debe rechazarse. El nombre `chunk_execution_attempts` no está aprobado, y agregar una tabla no sustituye decidir quién puede consumir/reintentar. Registrar tiempos/evidencia según F18-05 no obliga a interpretar causalidad de Groq por timestamps locales.

**Cuestión distinta de G5:** `os.replace()` del PDF y commit SQLite no son una sola operación atómica. El contrato G5 requiere recuperación idempotente de la ventana filesystem↔estado y política consistente ante `FAILED_RETRYABLE`/`FAILED`; no se pretende resolverlo añadiendo un journal de LLM. La certificación histórica de SIGKILL cubre solo sus sujetos ensayados.

## 6. Alternativas evaluadas y decisión negativa explícita

| Alternativa | Evidencia favorable | Coste contractual/riesgo conocido | Disposición propuesta, refutable |
|---|---|---|---|
| **R1 (`pipeline_factory`/`AsyncDispatcher`) como ejecutor principal** | Contexto/validación/healing reales; V2.1 focal completó 33 prompts, no aplicada | Falta handoff durable AST/proyecciones G3→G5; STOP original por `GLOBAL_ROOT`; ningún PDF R1 acreditado | **No preferida hoy** como raíz, pero conservar capacidades y volver a evaluar si evidencia nueva reduce la brecha |
| **R2/G3→G5 como referencia de continuidad** | Plan, receipts, publicación, 61 proyecciones y PDF físico con fake; recuperación G5 sintética acotada | Extracción científica `FAIL`; contexto y efecto incierto incompletos; no equivalencia del Compose base | **Preferida condicionalmente** como interfaz base; **no** aprobada como producto listo |
| **R3 (`LLMWorkerDaemon`) como ejecutor principal** | Recursos, admisión, backpressure, cancelación, shutdown y heartbeat disponibles estáticamente | `claim_next_pending_task`/`mark_task_failed` incompatibles con repositorio real; nodo ≠ unidad G3; no E2E | **No preferida hoy** como raíz; evaluar mecanismos puntuales solo según obligación incumplida |
| **Núcleo nuevo/reescritura completa** | Podría rediseñar contratos de cero | Elimina evidencia G3/G5 e incrementa interfaces/regresión/superficies sin necesidad probada | **Rechazar salvo prueba concreta** de que las alternativas existentes no pueden satisfacer una obligación |
| **Tres rutas productivas permanentes** | Evita migración inmediata | Doble semántica de autoridad, validación, CI, fixes y salida; contradice intención D-1 | **No proponer** como estado objetivo; preservar entradas compatibles y herramientas de ensayo |

**Criterio de desempate no arbitrario:** cobertura real de contratos FROZEN + continuidad de PDF + integridad científica + complejidad de interfaces que deben cerrarse. No inventar puntajes o benchmarks comparativos inexistentes. **Falsador directo de la preferencia R2:** demostrar que el núcleo G3→G5 no puede representar/publicar/recuperar las estructuras exigidas sin una sustitución desproporcionada, mientras otra continuidad verificada satisface los mismos contratos con menos cambios y sin riesgos adicionales.

## 7. Matriz de delta mínimo: contrato → reutilización → decisión pendiente

| Frontera/condición | Evidencia/capacidad reutilizable | Delta necesario para afirmar cumplimiento | Clasificación preliminar Charter §7.3 | Prohibición de sobreingeniería |
|---|---|---|---|---|
| Estructuras STEM PDF→AST→render | PyMuPDF/Docling adapters, AST plano, perfil, estrategias y G5 | Identificar pérdida por frontera; producir representación recuperable o fallo explícito | A? obligación de integridad; método exacto pendiente de evidencia | No segundo AST, ni proveedor nuevo por etiqueta de capacidad |
| Política `PRESERVE` | `ChunkPlan` validación + bypass `stage_claimed_unit` + clases R1 | Garantizar clasificación sobre entrada fiel, no-LLM y salida conservada | A? CTR-03/10/11 | No recuperar falsa matemática desde texto aplanado |
| Contexto real | Resolver/enricher R1, `PromptBuilder` y puente G3 | Disponibilidad/versionado del contexto usado, coherencia con cache/receipt | A? CTR-10/11; mapeo de DTO pendiente | No transportar breadcrumbs completas al Assembler por reflejo |
| Identidad de inferencia y replay | Hash de prompt, cache, receipt, `execution_id` | Separar identidad semántica de prompt efectivo+modelo y autoridad por intento; rechazar replay cruzado | A? CTR-02/06/08/10 | No «idempotency key» local convertida en promesa remota |
| Autoridad ante incertidumbre | Claim G3, lease, fencing, `ControlPlaneRepository`, Reconciler | Estado/evidencia de intento durables; gate único sobre reintento y reparación de todas las vías | **A por garantía F18-03/04/05**, diseño de persistencia pendiente | No segundo scheduler/FSMS ni tabla nueva por decreto |
| Límite de recursos | R2 thread pool/concurrencia; R3 `ExecutionEnvelope`, admission/backpressure/cancel | Medir y cubrir **solo** obligaciones F18-02 no acreditadas en Engine seleccionado | A? F18-02; alcance a comprobar | No desplegar daemon R3 entero |
| Publicación G3 y CP-08 | receipts, `g3_plan_publications`, `valid_chunks_cache`, `chunk_events_log` legado | Fijar responsable/modalidad de journal exigido y testigos de recuperación, sin equiparar tablas | A?/B? según lectura normativa y gobierno | No duplicar cada respuesta en dos journals autoritativos |
| G5 atomicidad archivo/SQLite | `AssemblyLeaseRepository`, `os.replace()`, FSM, reconciler | Política recuperable para crash/fracaso normal, con linaje PDF y fencing | A? F18-04; prueba acotada necesaria | No transacción distribuida ni reescritura G5 sin causalidad |
| Entrada CLI/duplicaciones | CLI existente, Engine G3, daemon R3 y tests consumidores | Contrato de adaptador + migración/retirada solo después de compatibilidad/cobertura | **B** D-1/D-2 pendiente del Board | No `RETIRE` automático de clases o ficheros |

`A?` indica **candidato** a incumplimiento de obligación vigente, no finding oficial. `B?` indica que tal vez se precise decisión de vacío normativo. `C` sólo procede ante contradicción demostrada entre **contratos vigentes**, no entre dos rutas de código distintas. La clasificación y los IDs formales corresponden al Board/método; no asignar nuevos `GAP-*` ni reabrir findings F18 cerrados por mera inferencia.

## 8. Gates de aceptación diferenciados: dirección, demostración e implementación

### 8.1 Gate de decisión de dirección — lo que puede resolverse **ahora**

| Gate | Decisión explícita del Board | Condición mínima para aceptar dirección | Condición que obliga a deferir/rechazar |
|---|---|---|---|
| **G-1 — D-1** | Contrato único de producto PDF→PDF, CLI como adaptador de entrada y separación explícita de instrumentación | Distingue entrada, ejecución, FSM/journal, validación/healing, salida; no impone único proceso | Aceptación exige desplegar múltiples motores o suprime garantías FROZEN; o autoridad del Charter sin resolver |
| **G-2 — D-2** | Continuidad R2/G3→G5 como **referencia de diseño** condicionada, no canonicidad certificada | Comparación explícita R1/R2/R3, `A` físico R2 + `FAIL` científico, límites de R3 y delta de D-2 respecto del Charter | Se declara productiva por PDF fake; se trata R3 no elegible como E2E fallido; se ignora alternativa de menor delta demostrada |
| **G-3 — límites normativos** | Precisar alcance F18-02/03/04/05, CP-08 y permisos de remediación F18.2 | Se reconocen contratos `FROZEN` y el Charter §4.2 que excluye nueva implementación F18.2; se resuelve autoridad antes de ejecutar | Se entiende que aprobación D-1/D-2 por sí sola reabre Wave 1.2, cambia NADR o autoriza código |

**Resultado actual propuesto:** G-1 `RECOMMEND_ACCEPT_DIRECTION`, G-2 `RECOMMEND_CONDITIONAL_REFERENCE`, G-3 `BOARD_ACTION_REQUIRED`. **No son PASS** ni votos emitidos. El Board puede `ACCEPT_DIRECTION_WITH_CONDITIONS`, `DEFER_FOR_EVIDENCE` o `REJECT_WITH_REASON`; debe dejar registrada la elección, la condición y la autoridad competente. Si la unidad y la gobernanza formal no están aprobadas, la candidata sigue siendo `NON-NORMATIVE`.

### 8.2 Gate de verificación — qué acreditaría o refutaría la arquitectura después, **sin autorización implícita**

| Contrato/capacidad | Testigo/fuente existente | Observable positivo mínimo | Resultado que refuta o bloquea |
|---|---|---|---|
| **A: fidelidad PDF→AST** | Corpus/oráculos disponibles, análisis focal de extracción y W-09 | Elementos relevantes representados o preservables físicamente con linaje; caso no soportado falla explícitamente | Ecuación/tabla/figura omitida o alterada silenciosamente, aunque `ChunkPlan` conserve todo su AST |
| **A: `PRESERVE` y salida** | W-09 con inline/display, código, imagen, más clases del corpus; W-10 para PDF | Bypass observable sin contacto LLM, resultado conservado/explicado físicamente, PDF verificable | Solo etiqueta de `PRESERVE` o eco de fake sin prueba física; degradación sin aviso |
| **B: miembros/identidad** | `ChunkPlan` actual, W-03 cuando aplique; W-08 para contexto/replay | N→1→N exacto de **elementos representados**, sin mezcla de generaciones; misma entrada semántica con distinta inferencia no da hit incompatible | Confusión `chunk_id`/`node_id`, proyección ajena, cache/replay de contexto/modelo distinto |
| **C: incertidumbre** | W-06 según Atlas | No inicio probado / resultado durable / incierto diferenciados tras crash/timeout; todo retry incierto detenido sin disposición autorizada | Una vía de `pick_task`, Reconciler, Sweeper o restart autoriza nuevo LLM sobre efecto incierto |
| **C: fencing/idempotencia local** | W-07 | Autoridad obsoleta y colisión same-version no pueden reemplazar estado válido; recuperación solo con resultado durable | Writer stale gana o cambia contenido irreversible sin version/fence |
| **C: recursos** | F18-02 y testigo focal de carga/abort bajo plan autorizado | Memoria, admisión, cancelación, shutdown y visibilidad acorde al envelope aplicable | Sobrecarga sin backpressure o pérdida de seguridad por cancelación |
| **G3→G5 y artefacto** | W-10, CP-10..12, pruebas G5 locales existentes cuando correspondan | AST, perfil, proyección, activos, PDF y estado final correlacionados; recuperación de crash/fracaso normal verificable | PDF válido sin linaje; promoción incoherente; reproducción imposible |
| **Journal/observabilidad** | CP-08, F18-05 + W-06/08 | Atribución causal de intentos/receipts/resultados y métricas de **cliente**, con límites declarados de observación externa | Confundir `chunk_result_receipts` con `event.chunk_events_log`; afirmar exactly-once remoto por ausencia de duplicados en logs |

**Condiciones de diseño de pruebas:** mantener W-06…W-10 como testigos ya definidos por el Atlas, no renombrarlos ni inventar criterios incompatibles; registrar sujeto, commit, configuración, origen/sha PDF, fase y outputs; usar un proveedor controlado con semántica representativa. El fake mide solicitudes del cliente, no garantiza cobro/respuesta del proveedor real. Seleccionar documentos por rasgos preexistentes y preregistro del Charter; el paper externo no es fixture canónico sin admisión y hash. Rechazar post hoc un oráculo porque el sistema falla.

**Límites de alcance:** las pruebas aisladas no sustituyen E2E real ni equivalen a autorización de acceso a Groq. Las verificaciones quedan **PENDIENTES**, no `FAIL` por ausencia de ejecución. Ante fallo de precondición: `NO ELEGIBLE — PRECONDICIÓN` o `NOT_REACHED`, no reparación silenciosa para llegar al siguiente gate.

### 8.3 Gate de implementación — solo después de actos separados

**G-4 — Experimentos focales:** el Board/owner define qué W se necesita para resolver cada pregunta, sujeto/inputs/hashes, presupuesto, STOP y recibo. No se ejecuta durante esta candidatura. Puede exigirse una prueba de contrato pura/aislada antes que un nuevo E2E costoso, sin sostener por ello que R1/R3 ya son equivalentes.

**G-5 — Cambios incrementales:** si G-1/G-2 se resuelven, G-3 delimita autoridad y las evidencias de G-4 permiten elegir implementación, se secuencia un único delta por frontera con pruebas de regresión, rollback y validación de la cadena. El orden lógico respeta **A (no perder ciencia) → B (identidad) → C (autoridad) → publicación/G5 → aceptación PDF**, sin convertirlo en una exigencia de implementar cada eje serialmente o crear cinco subproyectos. No se autoriza aquí modificar código, migrar DB, añadir campos, desplegar servicios ni retirar componentes.

### 8.4 Veto de cierre de producto (transversal a todos los gates)

`execution_outcome=A` y `FSM=COMPLETED` **no** autorizan declarar `product_readiness=PASS` si hay `scientific_verdict=FAIL`, traducción fake no evaluable, cobertura documental `UNKNOWN`, integridad contextual o seguridad ante efectos inciertos no demostradas. La aceptación final requiere las dimensiones del Scope y del Charter §6.2 evaluadas **independientemente** y bajo sus propios sujetos. No se imponen nuevos scores para «aprobar» matemáticas ni se exige perfección estética indeterminada: se aplican corpus/oráculos y contratos de preservación autorizados.

### 8.5 Evaluación de G-1…G-5 frente a las obligaciones existentes — **dictamen de revisión, no PASS del Board**

**Método.** Se examina (1) si el *texto de decisión* cumple las restricciones normativas identificables, (2) qué evidencia AS-IS histórica respalda la preferencia y (3) qué comprobación/autorización falta para implantarla. `VIABLE COMO PROPUESTA` **no** significa `CONTRATO SATISFECHO EN RUNTIME`. Fuentes rectoras: Scope §§1–4; Charter v0.1.0 `DRAFT` §§3/4/6/7/10; Atlas v0.2.16 `IN_PROGRESS` §§4, 8.5.2, 10–13; NADR-F18-01 v1.0.3 (identidad, `FROZEN`), F18-02 v1.0.1, F18-03 v1.1.0, F18-04 v1.1.1 y F18-05 v1.3.0 (`FROZEN`). Las referencias `R#` siguientes son **números internos de regla de cada NADR**, no rutas R1/R2/R3.

| Gate | Obligación/autoridad ya existente | Evidencia a favor y límites demostrados | Evaluación actual | Acto de cierre legítimo / falsador |
|---|---|---|---|---|
| **G-1 / D-1: principio de ruta contractual única** | Charter §3 D-1 (propuesto) y §6.2 identidad/handoff; Scope §4; Atlas CTR-02/08/10/12; F18-01 §5 R1–5, R14–20: identidad científica/ejecución separadas | Tres composition roots con contratos divergentes; CLI R1 no acredita `ASTRegistry`+`ChunkPlan`+proyecciones de G5 (`ATLAS-RTE-05`); ningún código unificado ya existe | **VIABLE COMO DIRECCIÓN; BOARD DECISION REQUIRED**. No `PASS` técnico | Board define contrato/roles y el estatuto de la CLI sin ordenar que replique G3. **Refuta:** requiere conservar dos productores productivos de resultados incompatibles o desdibuja identidad científica/ejecución. |
| **G-2 / D-2: referencia G3→G5 condicional** | Charter §3 D-2 inicialmente inclinada a `pipeline_factory`/`AsyncDispatcher`, §6.1 E2E-0 por rutas elegibles y §6.2 producto; Atlas CP/CTR; Scope §4; F18-01 identidad y F18-04 §5 R5–10 | R2 escalonado aportó PDF físico, 5 receipts y 61 proyecciones; P5 científico `FAIL`, fake lingüístico `NOT_EVALUABLE`; R1 `STOP` contextual, R3 `BLOCKED-STATIC`; no certificación del Compose base | **REFERENCIA CONDICIONAL DEFENDIBLE; BOARD DECISION REQUIRED**. No «ganador», no referencia normativa | Board consigna el **delta de preferencia** respecto al Charter y trata explícitamente R3 no elegible sin inventar `C` E2E. **Refuta:** alternativa con menores deltas y garantías superiores demostradas, o imposibilidad de cerrar pérdidas/contratos en el recorrido propuesto. |
| **G-3: obligaciones y autorización** | NADR-F18-02 §5 R1–19, R23–31; F18-03 §5 R1–23; F18-04 §5 R1–16; F18-05 §5 R1–16; F18-01 §5 R1–20; Charter §4.2 prohíbe una implementación F18.2 nueva sin acto correspondiente | G3 incorpora claims, leases, receipts, proyecciones y algunas barreras de fencing; **no** demuestra clasificación recuperable de todos los intentos inciertos, compatibilidad del journal CP-08 ni bounded execution integral. G5/2 tiene alcances de crash limitados | **BARRERA NORMATIVA ABIERTA; BOARD ACTION REQUIRED**. No autoriza código | Identificar deber por frontera, decidir autoridad/proceso para corregir bajo NADR FROZEN y documentar cualquier conflicto de gobernanza. **Refuta aprobación incondicional:** declarar equivalentes receipt, journal y telemetría, o reanudar F18.2 por la sola aprobación de D-1/D-2. |
| **G-4: evidencia focal y falsadores** | Atlas §8.5.2 W-03/05/06/07/08/09/10; Charter §6.1–6.4 preregistro/alcance; F18-02 §7; F18-03 §7; F18-04 §7; F18-05 §7 | Hay evidencia histórica R1/R2 y ensayos G5/2 acotados; **no** sustituye pruebas completas sobre el contrato TO-BE. W-06/07/08/09/10 son testigos especificados, no nuevas ejecuciones realizadas | **DISEÑO DE VERIFICACIÓN DISPONIBLE; EJECUCIÓN NO AUTORIZADA / EVIDENCIA PENDIENTE** | Para cada hipótesis pendiente: sujeto exacto, input/hash, prerrequisitos, oráculo/observable, falsador, STOP/recibo, permiso y presupuesto. **Refuta:** replay cruzado W-08, retry incierto W-06, stale write W-07 o pérdida silenciosa W-09. No convertir pruebas focales en un supuesto E2E-0 aprobado. |
| **G-5: deltas implementables y cierre** | Charter §§4.2, 6.2, 8–10; Scope §4; F18-01/02/03/04/05 según frontera; Atlas CAP-01…12, CP-00…12 y W-10 | No existe arquitectura convergida ya integrada; la CLI no entrega CQRS G3, la fidelidad P5 falla, el modelo concurrente y la autoridad remota siguen condicionados | **NOT_READY_FOR_IMPLEMENTATION / IMPLEMENTACIÓN NO AUTORIZADA / PRODUCT_READINESS NOT_DEMONSTRATED** | Después de decisiones y pruebas autorizadas: cerrar **un delta de contrato por vez** con consumidor, verificación interproceso, regresión/rollback, archivo→DB y evidencia física-científica; elegir mecanismos mínimos. **Refuta cierre:** PDF fake usado como prueba lingüística, `COMPLETED` sin linaje, o recuperación que reintente efecto incierto. |

**Lectura obligatoria de barreras, sin reabrir automáticamente findings:**

1. **G-1 y G-2 son separables.** La conveniencia del contrato único no demuestra que R2/G3 sea una composición certificada. La preferencia D-2 debe explicitar su revisión frente al Charter `DRAFT`; el E2E `A` físico de R2 no reemplaza ninguna obligación del producto. El Atlas registra impedimentos estáticos de R3, no un `C` dinámico ficticio. Las decisiones D-3…D-7 del Charter y la constitución/autorización de la unidad no se consideran resueltas por aprobar D-1/D-2.
2. **La ciencia impone un veto transversal (G-1/2/4/5).** Scope §4, CAP-02/03/07/09/10/12, CTR-10/11/12 y F18-01 no admiten confundir `ChunkPlan` íntegro con cobertura PDF. E2-02 `FAIL` es un resultado histórico del sujeto R2, no un error de extracción causalmente aislado. El testigo de U+FFFF del paper no sustituye la custodia/selección formal de corpus ni autoriza rebaseline.
3. **Identidad y CQRS (G-1/2/3/4).** El consumidor G5 exige AST/plan/perfil/proyecciones concordantes por generación. F18-01 obliga distinguir identidad científica, de ejecución y estado operacional; F18-04 §5 R5–10 exige reaplicación idempotente, fencing y reconstrucción verificable. El contrato de contexto R1 no se adopta hasta demostrar hidratación y vínculo de inferencia, y la CLI no es propietaria automática del journal.
4. **Efectos externos (G-3/4/5).** F18-03 §5 R1–4 exige autoridad persistida **antes** de I/O; R5–8 clasificación conservadora; R9–15 bloqueo/escalamiento/autorización de reintentos inciertos. F18-04 §5 R1–4 y R8–16 separa durabilidad y coherencia entre planos. F18-05 §5 R1–3, R4–10 y R11–16 exige historia correlacionable, distinguir cliente de duplicación externa y exposición/costo sin números inventados; tampoco impone un backend de telemetría específico. `chunk_result_receipts` no prueba solo el historial de intentos, y ningún hash local garantiza deduplicación Groq.
5. **Concurrencia (G-3/4/5).** F18-02 §5 R1–4 requiere resource envelope/admisión y límites explícitos; R5–10 mecanismos de admisión/backpressure; R11–19 cancelación y seguridad; R23–29 visibilidad y neutralidad; R30–31 selección del modelo DC-01 con evidencia cuantitativa. La implementación secuencial de R3 no prueba equivalencia con el pool concurrente R2. Las cifras de umbrales existentes son configuración histórica del mecanismo, no nuevas métricas de aceptación.
6. **Barrera de procedimiento.** La aprobación de un *dossier no normativo* puede registrar el contexto y una preferencia sin habilitar experimentos, proveedor real, cambios de código, rollback, decisiones `KEEP/RETIRE`, modificación de NADR ni reanudación de F18.2. Cada acto requiere su propio gate y autorización registrada. Si el Board quiere modificar el preregistro E2E-0 del Charter, debe tramitarlo expresamente; esta candidatura no lo corrige en silencio.

**Veredicto conjunto de revisión:** `G-1: BOARD DECISION REQUIRED (favorable condicional)` · `G-2: BOARD DECISION REQUIRED (referencia condicional)` · `G-3: BOARD ACTION REQUIRED (barrera normativa)` · `G-4: SPECIFIED, NOT AUTHORIZED / NOT EXECUTED` · `G-5: NOT READY / NOT AUTHORIZED`. **Ningún gate recibe `PASS` productivo ni se afirma conformidad global F18.**

## 9. Registro breve de cuestiones todavía abiertas — decisiones, no tareas disfrazadas

| Pregunta | Evidencia que la resuelve | Quién puede decidir / estado |
|---|---|---|
| ¿D-1 único contrato, no una implementación? | Comparación y Scope + Charter | Board: `DECISION REQUIRED` |
| ¿D-2 referencia R2 G3→G5 pese a inclinación inicial R1 y `FAIL` científico? | Expedientes, E2E-0 R1/R2, R3 no elegible, delta de contratos | Board: `DECISION REQUIRED`; solo dirección condicional defendible |
| ¿Qué representación física/semántica falta por clase de corpus? | Comparación productor→consumidor y testigos focales sobre entrada/oráculo fijado | Ingeniería propone; validación científica y Board autorizan alcance |
| ¿Qué artefacto durable identifica contexto/prompt efectivo/modelo sin duplicar datos? | W-08 y auditoría de cache/replay/receipts existentes | Arquitectura/Board según necesidad de contrato nuevo; `UNKNOWN` |
| ¿Dónde registrar historia por intento sin dos fuentes autoritativas ni transacción cross-DB ficticia? | Contraste de esquema, atomicidad y F18-03/04/05; W-06/07 | Autoridad de contrato: pendiente, no tabla aprobada |
| ¿Cuál es la disposición de timeout incierto en TODAS las vías y la suspensión/reanudación autorizada? | W-06 + lectura de scheduler/reconciler/sweeper | Normativa FROZEN aplicable; implementación y permisos pendientes |
| ¿Qué capacidades R3 faltan realmente en Engine? | F18-02 vs pruebas bajo carga sobre mismo ejecutor | Medición antes de portar; no daemon completo aprobado |
| ¿CP-08 exige usar/expandir EventPlane o equivalente contractual con una autoridad clara? | Comparación CTR/NADR, `event.db=0` frente a receipts 5, tests de recuperación | Board/método; `UNKNOWN`, no equiparación automática |
| ¿Cómo se recupera G5 con `os.replace` antes de commit o fallo normal? | Escenarios G5/2 y test focal del caso con linaje PDF/FSM | Acreditación posterior; no nueva transacción distribuida |
| ¿Cuándo y qué código R1/R3 podría retirarse? | Grafo de consumidores, pruebas, compatibilidad de entrada, autoridad D-1/D-2 | **NO DECISION** hasta convergencia certificada |

## 10. Solicitud consolidada al Architecture Board

**Texto propuesto para el acta — no expresa aprobación ya emitida:**

> Se solicita al Architecture Board resolver D-1 y D-2 del Charter v0.1.0, hoy `DRAFT`, sobre la base de la caracterización comparativa de R1/R2/R3 y de la continuidad física controlada R2 G3→G5. Para D-1 se recomienda un único **contrato** de producto PDF→PDF con CLI como adaptador de entrada; no se propone un único proceso ni retiro de fuentes. Para D-2 se solicita aceptar **solo como referencia técnica candidata** el contrato G3 de planes, autoridad y receipts hasta la publicación y G5 de ensamblado/fencing, condicionado a cerrar integridad científica, identidad de inferencia/contexto, efecto externo incierto, bounded execution, CP-08 y coherencia filesystem–SQLite. La elección de implementación concreta, cualquier cambio F18.2 y el retiro de rutas quedan reservados a decisiones y autorizaciones posteriores. La producción no se acredita por un PDF de fake ni por un estado FSM. Los testigos W-06…W-10 sólo se prepararán/ejecutarán bajo preregistro y permiso específicos, preservando historial y oráculos.

### Opciones de resolución explícita

- **Aceptar dirección condicionalmente:** dejar por escrito contrato/propiedad/riesgos y acciones de gobierno, manteniendo `product_readiness=NOT_DEMONSTRATED`, y sin implementar por la aprobación.
- **Diferir para evidencia:** definir la pregunta concreta, testigo, sujeto y condición de cierre; no solicitar una repetición genérica de E2E de las tres rutas.
- **Rechazar motivadamente:** identificar contrato vigente o evidencia comparativa que invalida el recorrido único propuesto o la preferencia G3→G5; no atribuir a la candidata un `PASS` que nunca reivindicó.

**Materia que no se solicita votar ahora:** `KEEP/RETIRE` de ficheros, elección PyMuPDF/Docling, un nuevo schema/tablas por nombre, ADR/NADR nuevos, presupuesto de proveedor real, nuevas métricas de calidad, remediación sin autoridad, ni reemplazo total de la cadena.

**Dictamen propuesto:** `RECOMMEND CONDITIONAL ACCEPTANCE OF DESIGN DIRECTION` · `BOARD DECISION PENDING` · `NO IMPLEMENTATION AUTHORIZATION` · `NO PRODUCT CERTIFICATION`.

## 11. Fuentes, versión y límites de verificación

**Jerarquía aplicada:** `FROZEN` normativos aplicables → Atlas v0.2.16 `IN_PROGRESS` (reconstrucción AS-IS, §§0–12 con corte histórico y adenda §13) + Charter v0.1.0 `DRAFT` (preregistro, §§3/4/6/7/10) → código funcional pinneado `d4cda2c…` + imagen/evidencia histórica por sujeto → expedientes no versionados y conversación. Las fuentes de estudio no promueven un DRAFT a FROZEN ni inventan findings oficiales.

- **Producto y principios:** `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, `ROADMAP_ARQUITECTONICO_LP(1).md` disponibles en el proyecto.
- **Rectoría:** [Atlas v0.2.16](https://github.com/RDsanchez-git/translator_pdf/blob/pipeline_stabilization/docs/architecture/adr/pipeline-stabilization/00-foundation/PRODUCTION_PIPELINE_EXECUTION_ATLAS.md), [Charter v0.1.0 DRAFT](https://github.com/RDsanchez-git/translator_pdf/blob/pipeline_stabilization/docs/architecture/adr/pipeline-stabilization/00-foundation/PIPELINE_STABILIZATION_AUDIT_CHARTER.md) y [Gobernanza sandbox DRAFT](https://github.com/RDsanchez-git/translator_pdf/blob/pipeline_stabilization/docs/architecture/adr/pipeline-stabilization/00-foundation/SANDBOX_GOBERNANZA_Y_GUIA_OPERATIVA.md).
- **Normativa:** [NADR-F18-02](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/docs/architecture/adr/phase-18/NADR/NADR-F18-02.md), [NADR-F18-03](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/docs/architecture/adr/phase-18/NADR/NADR-F18-03.md), [NADR-F18-04](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/docs/architecture/adr/phase-18/NADR/NADR-F18-04.md), [NADR-F18-05](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/docs/architecture/adr/phase-18/NADR/NADR-F18-05.md). Ninguno se edita aquí.
- **Sujetos/evidencia:** `EXPEDIENTE_FORENSE_R1_PDF_PDF_ASIS_20261105.md`, `EXPEDIENTE_FORENSE_R2_PDF_PDF_ASIS_20261105.md`, `EXPEDIENTE_FORENSE_R3_PDF_PDF_ASIS_20261105.md`, `COMPARACION_TRANSVERSAL_R1_R2_R3_PIPELINE_PDF_PDF_20261105.md`, `ATLAS_CONVERGENCIA_CANDIDATOS_R1_R2_R3_20261105.md`; `Continuación real.md` y Candidate original son fuentes locales de secuencia argumental, sin elevar su estado.
- **Implementaciones:** [PyMuPDF adapter](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/extraction/providers/pymupdf_provider.py), [Docling adapter](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/extraction/providers/docling_provider.py), [AST hash](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/core/ast/hashing.py), [ChunkPlan](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/core/chunking/manifest_contract.py), [R2 Engine](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/runtime/engine.py), [staging](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/runtime/chunk_staging.py), [publicación](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/staged_publication.py), [control plane](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/control_repo.py), [G5](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/infra/db/assembly_recovery.py), [R1 cache](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/apps/llm_workers/cache_provider.py), [R3 daemon](https://github.com/RDsanchez-git/translator_pdf/blob/d4cda2c379c0efd93a70e795d31c37a0ede7a192/apps/llm_workers/__main__.py).
- **Proveedor externo:** [Groq API Reference](https://console.groq.com/docs/api-reference), consultada documentalmente el 2026-11-05: la referencia pública disponible no acredita para la llamada síncrona utilizada en el código una API de deduplicación/consulta por huella local. No constituye prueba de *ausencia universal* de funcionalidades de Groq ni de egress/cobros reales.

**Distinción probatoria final:** `S` = código inspeccionado, `H` = resultado histórico referido por sujeto, `V` = artefacto contrastado en expedientes precedentes, `P` = propuesta, `U` = no acreditado. En esta revisión se cotejaron archivos locales y código/documentación en lectura; **no** se reabrieron recibos Docker ni se ejecutaron ensayos. No se ha obtenido nueva evidencia dinámica, emitido decisión normativa ni comprobado una instalación productiva en el host.

**Custodia y posible registro documental:** mientras siga pendiente de revisión/aceptación del owner, conservar esta edición descargada **fuera del checkout** en `C:\Users\Admin\Downloads`. **Si el owner lo autoriza expresamente**, puede incorporarse como nuevo archivo documental `DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md` dentro de `docs/architecture/adr/pipeline-stabilization/00-foundation/` en la rama `pipeline_stabilization`, con commit `docs(...)` trazable y revisión de diff, preservando texto y estado `CANDIDATE / NON-NORMATIVE / NOT APPROVED`. La presencia en Git **no** constituye ratificación del Board, no modifica el Charter ni congela el Atlas. No modificar Git, Atlas, Charter, NADR, laboratorios ni recibos históricos sin autorización específica posterior.

## 12. Adenda informativa posterior al corte — testigo B03 del 2026-11-06

Esta adenda **no altera** la fecha de corte 2026-11-05, el carácter `CANDIDATE / NON-NORMATIVE / NOT APPROVED` del documento ni la evaluación histórica de G-1…G-5. En el commit `f6d258e87cc7479b55c0354bae71db5d37597611` se encuentra versionada la variante B03.2.4 de `translate --run` con `APP_ROOT`, y el owner aportó un testigo operacional completo: OCR/AST, G3 con fake HTTP 200, G5/Tectonic, PDF sintético legible y `FSM COMPLETED`.

El caso posterior Amor/`doc_02_double.pdf` fue rechazado en extracción mediante `B02_UNREPRESENTED_VECTOR_DRAWING`, sin G3/G5 ni PDF final. Por tanto, la continuidad funcional de R2 en un PDF compatible refuerza la **viabilidad técnica de G-1** y la **referencia condicional G-2**, pero no elimina los límites científicos, de cobertura, contextuales ni de autoridad. `G-3` conserva barreras normativas; `G-4` requiere testigos preregistrados propios; `G-5` sigue sin cierre de producto. No se transforma un smoke fake en aceptación de traducción, E2E-0 oficial, aprobación D-1/D-2 ni conformidad F18.

**Referencia probatoria:** [observación de trabajo B03](working-observations/B03_20261106_CONVERGENCIA_FUNCIONAL_OFFLINE_NO_CIERRE_GOBIERNO.md). Permanecen `G-1/G-2=BOARD_DECISION_REQUIRED`, `G-3=BOARD_ACTION_REQUIRED`, `PRODUCT_READINESS=NOT_DEMONSTRATED`; la autoridad debe decidir expresamente la convergencia D-1/D-2.
