# HITO_PPPR.0.4_G3_PROMPTS_MODELOS_IDIOMA_Y_PRESUPUESTOS.md

**Estado:** IN_PROGRESS v1.0.0  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** N/A  
**Fase:** PPPR — Fase 0 transversal de `pdf-pdf-product-readiness` (no fase numerada del roadmap)  
**Tipo de artefacto:** Forensic Flow Audit  
**Naturaleza:** Auditoría read-only; no implementa ni aprueba soluciones.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@da7006059521393532e109d5b3f68be75540d449` (incluye PPPR.0.1, 0.2 y 0.3 FROZEN).  
**Evidencia Forense Vinculante:** Metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2, Atlas; HITO PPPR.0.1–0.3 FROZEN; NADR-F17BIS-06 §5.1 (presupuestación) y NADR-F17BIS-05 (contexto), sujetos a contraste completo en esta auditoría.  
**Mandato:** Determinar el G3 **efectivamente cableado**: prompts y lengua objetivo, modelo y ruta de proveedor, estimación de tokens/ventana/compresión/fallback, autorización de I/O, límites de gasto/quotas, respuesta estructurada y guardias de incertidumbre. Distinguir límites de este mandato de FSM/SQLite/W06 (PPPR.0.5), host/secretos (0.7) y pruebas científicas (0.8).  
**Síntesis:** Apertura con ruta G3 de código verificada; falta reconciliar contratos de idioma, modelo/fallback y presupuestos contra normas y testigos antes de clasificar severidad y congelar.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura posterior al merge del PR #68; lectura focal de engine, builder, schema, renderer, Groq, presupuestos, stack de proveedor y testigos W06/G3. Evidencia provisional con límites; no ejecución ni FROZEN. |

## 1. RESUMEN EJECUTIVO

Se auditó inicialmente la composición G3 que sigue a `ChunkPlan` en la ruta D-1/D-2. El root `runtime/engine.py::_create_chunk_processor` construye `PromptBuilder` con modelo y presupuestos fijos, inyecta el proveedor Groq a través de `build_provider_stack` y `SyncProviderBridge`, que materializa el prompt y valida respuestas JSON del chunk.

**Hallazgo central:**

> Hay diferencias verificables entre la decisión lógica de fallback, el modelo realmente transportado al proveedor y la ausencia de un idioma destino explícito en el esquema/prompt efectivos; estimación de tokens y límites comerciales son contratos distintos de un presupuesto de gasto ejecutable.

**Veredicto provisional:** se confirma el mecanismo en código, pero no se ha demostrado el impacto físico en proveedor comercial ni la cobertura de todas las restricciones normativas. **IN_PROGRESS**; no emitir todavía GAPs/decisiones definitivas ni afirmar `PRODUCT_READINESS=PASS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **OBSERVED:** código leído de `main@1d21cfe`, especificando campo, constructor y consumidor. No se realizaron requests LLM, cargos, pruebas de tokenización contra el modelo comercial ni CI.
- **REQUIRED:** reglas FROZEN pertinentes y mandato de traducir PDF científico al idioma objetivo; cualquier norma adicional debe citarse literalmente antes de atribuir obligaciones.
- **DECISION:** D-1/D-2 fijaron OCR→G3→G5; no autorizaron un modelo fijo, un nuevo proveedor, presupuesto de pago ni una política de fallback específica para este HITO.
- **LÍMITE:** proveedor real, estado comercial de modelos, tokens facturados, privacidad y cotas por operación son **NO VERIFICABLE** mediante lectura estática. PPPR.0.5 auditará autoridad de ejecución, retries, UNKNOWN y estado; PPPR.0.7 despliegue/secretos; PPPR.0.8 testigos científicos.
- **NO EJECUTADO:** pytest, SQLite, SDK de Groq/Gemini, red, PDF privado, Tectonic y corpus sellado.

## 3. ALCANCE AUDITADO — PRIMERA PASADA

| Superficie | Código y contrato revisado | Estado / frontera |
|---|---|---|
| G3 root | `runtime/engine.py::_create_chunk_processor`, `run_pipeline` | **AUDITADO focal**; estados y publicación PPPR.0.5–0.6 |
| Builder y schema | `apps/llm_workers/prompt_builder.py`; `core/prompting/{models,renderer,intent_mapper,constraint_factory,measurement_adapter}.py` | **AUDITADO focal** |
| Modelo/provider | `apps/bootstrap/provider_stack_factory.py`, `apps/llm_workers/adapters.py::GroqProvider.translate` | **AUDITADO focal**; API comercial NO VERIFICABLE |
| Token budget | `core/validation/{budget,estimators}.py`, `core/prompting/dialects/openai_compatible.py` | **AUDITADO focal**; adecuación al tokenizador comercial NO VERIFICABLE |
| Frontera de chunks | `apps/llm_workers/sync_bridge.py::execute_chunk`; `core/chunking/contextual_plan.py` | **AUDITADO focal**; response binding y output final pendiente |
| Cuotas y cache | `apps/llm_workers/{rate_limiter,cache_provider}.py`, `apps/bootstrap/provider_stack_factory.py` | **INSPECCIONADO**; uso/efectos en PPPR.0.5 |
| Testigos | `tests/integration/{test_g3_b1_policy_guardrails,test_w06_g3_uncertain_effect_offline}.py`, tests G3 B4/W08 y unit tests de budget/prompt por localizar | **PARCIAL / NOT_RUN** |
| Deuda histórica, NADRs adicionales y consumidores CLI | Se comprobarán en revisión del HITO | **TO BE VERIFIED** |
| G5, SQLite/FSM, host, corpus/oráculos | HITOs PPPR.0.5–0.8 | **REFERENCIADOS, NO auditados aquí** |

**No se cumple aún §8.1.** La matriz clasifica el alcance progresivo, no certifica módulos ni ciencia fuera del mandato.

## 4. FUENTES DE EVIDENCIA

**Primarias:** rutas Python de §3 en `main@1d21cfe`. **Normativa:** metodología general y forense FROZEN, `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, NADR-F17BIS-06 y -05 (los demás se cotejarán en siguientes pasadas). **Antecedentes:** HITO PPPR.0.1–0.3 FROZEN y Atlas; no se reabre convergencia. **Testigos:** pruebas de G3 y W06 solo leídas, `NOT_RUN`, con dobles offline.

## 5. MAPA DEL FLUJO OBSERVADO (PARCIAL)

```text
OCR → ChunkPlan verificable [PPPR.0.1/0.3]
  → runtime/engine.py::_create_chunk_processor
      → ExactBPEEstimator("cl100k_base")
      → PromptBudgetCalculator(primary=8192, fallback=1048576)
      → PromptBuilder(model_name="llama3-70b-8192", prompt_version="v1.0")
      → build_provider_stack(Groq por default, SQLite quota store, cache_db_path=None)
          → GroqProvider → RateLimitedProvider → CircuitBreakerProvider
      → SyncProviderBridge.execute_chunk(plan, unit)
          → contexto validado (W08) y JSON multi-member con máscaras math
          → PromptBuilder.build(..., target_lang_expansion=2.0)
              → PromptSchema(intent, context, constraints, payload)
              → PromptBudgetCalculator.calculate
              → PromptEnvelope(model_name=builder.model_name, target_provider=primary/fallback)
          → GroqProvider.translate(envelope)
              → PromptRenderer.render(schema) → dialecto HTTP
              → AsyncGroq.chat.completions.create(model=envelope.model_name)
          → parse_chunk_response(...) y guardias de membresía [verificar alcance]
  → recepción/estado y publicación G3/G5 [PPPR.0.5/0.6]
```

La política `cache_db_path=None` deshabilita **esa capa de cache de prompts**, no demuestra que todas las reutilizaciones durables de `COMPLETED` estén desactivadas. También existe una ruta Gemini de benchmark por factory, no acreditada como seleccionada en el root G3 inspeccionado.

## 10. REGISTRO DE EVIDENCIA FORENSE — PRIMERA PASADA

| ID | Sev. preliminar | Observed | Required / Decision / límite | Estado |
|---|---|---|---|---|
| **E-0.4-001** | P2 | `runtime/engine.py::_create_chunk_processor` fija `model_name="llama3-70b-8192"`, ventana primaria 8192 y fallback 1048576; pide `GROQ_API_KEY`. | Configuration hardcoded de la ruta elegida, no prueba por sí sola que el modelo esté disponible o retirado en el servicio real. | OBSERVADO |
| **E-0.4-002** | P2 | `PromptBudgetCalculator.calculate` puede devolver `SWITCH_MODEL`; `PromptBuilder.build` lo acepta, marca `target_provider="fallback_large_window"`, pero conserva `envelope.model_name=self.model_name`. | `GroqProvider.translate` manda `model=envelope.model_name`; decisión lógica no se convierte en cambio de modelo. Requiere evaluar contrato de fallback e impacto antes de P1/GAP. | DESACOPLE ESTÁTICO |
| **E-0.4-003** | P2 | `PromptSchema` carece de `target_language` y `source_language`; `PromptRenderer.render` solo emite intent, topología, breadcrumbs, constraints y payload. | No se expresa al LLM un idioma de destino en la ruta de prompt inspeccionada; falta cruzar mandato y CLI antes de calificar severidad. | AUSENCIA LOCAL DEMOSTRADA |
| **E-0.4-004** | P2 | `SyncProviderBridge.execute_chunk` genera payload JSON de miembros con máscaras matemáticas y llama a `PromptBuilder.build(..., target_lang_expansion=2.0)`. | El multiplicador es **reserva estimativa de salida**, no idioma destino ni máximo de tokens de generación impuesto al SDK. | OBSERVADO |
| **E-0.4-005** | P2 | `ExactBPEEstimator` usa `tiktoken.get_encoding("cl100k_base")`; `PromptBudgetCalculator` suma sistema/contexto/payload y reserva dinámica. | NADR-F17BIS-06 §5.1 exige compatibilidad con tokenizador efectivo; no hay verificación de compatibilidad de ese BPE con la configuración Groq conectada. | TO BE VERIFIED |
| **E-0.4-006** | P2 | `GroqProvider.translate` llama `AsyncGroq.chat.completions.create` con `model`, temperatura y kwargs del dialecto; no se observó `max_tokens` en esa frontera. | Estimar/cotizar tokens no impone un techo físico de salida ni gasto por operación. Efectos comerciales y límites reales no verificados. | LÍMITE |
| **E-0.4-007** | P2 | `build_provider_stack` construye Groq por defecto y acepta Gemini para benchmark; `cache_db_path=None` evita instanciar `CachedLLMProvider` en este root. | No confundir cache LLM de `prompt_hash` desactivado con FSM duradera, W06, W08 o reutilización de unidades (PPPR.0.5). | OBSERVADO |
| **E-0.4-008** | P2 | `NADR-F17BIS-06` §5.1 exige estimación compatible con proveedor y prohíbe heurística solo por palabras; el root usa BPE explícito. | La presencia de BPE no prueba compatibilidad con tokenizador Groq ni el importe facturable; contrato con necesidad de contraste. | NORMA/OBSERVADO |
| **E-0.4-009** | P2 | `rate_limiter.QuotaManager` reserva tokens y requests para bucket RPM/TPM estimado. | Cuotas de ritmo ≠ presupuesto comercial de gasto total; persistencia y fences de cuota se auditarán por PPPR.0.5. | LÍMITE DE GARANTÍA |
| **E-0.4-010** | P2 | `tests/integration/test_w06_g3_uncertain_effect_offline.py` emplea fake provider para pérdida de respuesta tras llamada aceptada y exige ausencia de segundo efecto. | Testigo offline de comportamiento pretendido; NO_RUN en esta auditoría, no garantía probada de SDK comercial ni permiso para retry. | ALCANCE DE TEST |

**Severidades provisionales:** P2 significa evidencia o límite con consecuencia todavía no reconciliada contra obligación efectiva; **no** certifica ausencia de P1 ni identifica una implementación aprobada. El registro se ampliará con fichas P0/P1 extendidas **si** corresponde tras cotejo normativo y revisión de tests.

## 14. GAPS CONSOLIDADOS

**Sin GAP emitido aún.** Se investigan tres candidatos: idioma objetivo, `SWITCH_MODEL` sin conmutación real y controles de presupuesto/salida. Una ausencia observada puede ser defectuosa, pero §4.7–4.8 exige contrato, causalidad, consecuencia y estado antes de promoverla a GAP.

## 15. HIPÓTESIS ABIERTAS / DEFERRED QUESTIONS

| ID | Pregunta falsable | Estado y próximo control |
|---|---|---|
| **H-0.4-A** | ¿La ruta soportada transmite el idioma destino hasta el prompt enviado a Groq? | **TO BE VERIFIED**: revisar CLI, comando y consumidores; ruta de schema actualmente sin campo |
| **H-0.4-B** | ¿El presupuesto puede autorizar `SWITCH_MODEL` sin cambiar modelo físico? | **CONFIRMADA POR CÓDIGO** en E-002; contrato de modelo/fallback pendiente |
| **H-0.4-C** | ¿La configuración G3 es utilizable con un modelo comercial actualmente disponible? | **NO VERIFICABLE SOLO EN CÓDIGO**: requiere documentación de API vigente y/o test seguro, sin claves ni gasto no autorizados |
| **H-0.4-D** | ¿`ChunkPlan`/quota imponen un techo de coste por operación además de estimar tokens? | **TO BE VERIFIED**: rastreo de `max_tokens`, presupuesto efectivo y consumidor físico; FinOps/host fuera de 0.4 si requiere ejecución |
| **H-0.4-E** | ¿Las protecciones JSON/matemática llegan a Groq y se validan tras respuesta? | **TO BE VERIFIED**: lectura completa de bridge/dialecto, tests y reply binding |
| **H-0.4-F** | ¿La ruta W06/UNKNOWN permite un retry inseguro ante respuesta perdida? | **TO BE VERIFIED**, límite 0.5; testigo fake W06 disponible pero NO_RUN |
| **H-0.4-G** | ¿El BPE usado es compatible con el tokenizador efectivo del modelo seleccionado? | **NO VERIFICABLE SOLO EN CÓDIGO**, NADR-06 y validación de proveedor/tokenización por etapas posteriores |

No se dejarán hipótesis `TO BE VERIFIED` al pasar a FROZEN sin disposición explícita, motivo de no-bloqueo y fase destino §8.1–8.2.

## 16. RESPUESTAS INICIALES AL MANDATO

El G3 conectado usa Groq por defecto, construye un prompt estructurado a partir de unidades contextualizadas y dispone de estimación de tokens, cuota RPM/TPM y validadores de respuesta. Hasta esta pasada, **el prompt inspeccionado carece de una lengua destino** y la señal `SWITCH_MODEL` no selecciona otro modelo físico. Esas discrepancias serán cotejadas con normas y objetivos de producto antes de elevarse a GAP. Ninguna cifra de tokens planificados se presenta como máximo de coste facturable.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN.** Falta completar el perímetro de productores/consumidores, verificar las normas de G3, reconciliar CLI/idioma, estudiar testigos y W06 de frontera, y clasificar los hallazgos con `Observed ≠ Required ≠ Decision`. No se han ejecutado tests ni servicios comerciales, no hay evaluación científica nueva.

**Siguiente paso:** mantener un PR interno Draft de solo documentación; revisar de forma rigurosa el mismo HITO antes de congelarlo y, una vez aprobado/integrado, eliminar `pppr/hito-0.4` antes de PPPR.0.5. El PR general #66 permanece Draft hacia `main`. Ninguna implementación de producción se autoriza.
