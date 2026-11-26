# HITO_PPPR.0.4_G3_PROMPTS_MODELOS_IDIOMA_Y_PRESUPUESTOS.md

**Estado:** FROZEN v1.0.3  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** 2026-11-19  
**Fase:** PPPR — Fase 0 transversal de `pdf-pdf-product-readiness` (no fase numerada del roadmap)  
**Tipo de artefacto:** Forensic Flow Audit  
**Naturaleza:** Auditoría read-only; no implementa ni aprueba soluciones.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@da7006059521393532e109d5b3f68be75540d449` (incluye PPPR.0.1, 0.2 y 0.3 FROZEN).  
**Evidencia Forense Vinculante:** Metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2, Atlas; HITO PPPR.0.1–0.3 FROZEN; NADR-F17BIS-06 §5.1 (presupuestación) y NADR-F17BIS-05 (contexto), sujetos a contraste completo en esta auditoría.  
**Mandato:** Determinar el G3 **efectivamente cableado**: prompts y lengua objetivo, modelo y ruta de proveedor, estimación de tokens/ventana/compresión/fallback, autorización de I/O, límites de gasto/quotas, respuesta estructurada y guardias de incertidumbre. Distinguir límites de este mandato de FSM/SQLite/W06 (PPPR.0.5), host/secretos (0.7) y pruebas científicas (0.8).
**Aclaración owner — 2026-11-19:** primera versión = traducción **inglés→español (`en→es`)**, exclusivamente; no se requiere soporte multidioma ni selector de destinos. El owner solicita actualizar la configuración de inferencia obsoleta. La decisión fija el alcance del producto, **no** selecciona todavía proveedor, modelo, diseño ni presupuesto; formalizarla en ADR Maestro/Execution Plan.  
**Síntesis:** Cerrado el Flow Audit documental de G3: 4 GAP P1 locales OPEN (modelo retirado, fallback sin conmutación, destino `en→es` ausente y fallback con cabida insuficiente), 21 evidencias, 7 hipótesis clasificadas, 4 DQ y 4 DC. Sin ejecución comercial, calidad científica certificada ni implementación autorizada.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura posterior al merge del PR #68; lectura focal de engine, builder, schema, renderer, Groq, presupuestos, stack de proveedor y testigos W06/G3. Evidencia provisional con límites; no ejecución ni FROZEN. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Segunda pasada: CLI→OCR→G3, documentación oficial Groq, modelo retirado, idioma y SWITCH_MODEL; tres fichas P1/GAP OPEN. Se inspeccionaron presupuesto, representación medida vs request, JSON/matemáticas y testigos fake; 18 evidencias, 7 hipótesis clasificadas provisionalmente. Sin ejecución comercial ni FROZEN. |
| 1.0.2-IN_PROGRESS | 2026-11-19 | Cierre de cobertura tokens/FinOps, JSON/math y W06; owner confirma EN→ES y actualización de inferencia; nuevo GAP-0.4-04 por cabida de fallback, 21 E-IDs y DQ/DC clasificadas. Sin ejecución ni FROZEN. |
| 1.0.3-FROZEN | 2026-11-19 | Revisión de cierre §8.1–8.2: 21 E-IDs con cuatro fichas P1, 4 GAP OPEN, H-0.4-A…G clasificadas, 4 DQ y 4 DC trazables; normalización de tablas/editorial, garantías negativas y no-regresión con otros HITOs. Evidencia de retiro Groq vigente, sin ejecución comercial ni código productivo. |

## 1. RESUMEN EJECUTIVO

Se auditó la composición G3 que sigue a `ChunkPlan` en la ruta D-1/D-2. El root `runtime/engine.py::_create_chunk_processor` construye `PromptBuilder` con modelo y presupuestos fijos, inyecta el proveedor Groq a través de `build_provider_stack` y `SyncProviderBridge`, que materializa el prompt y valida respuestas JSON del chunk.

**Hallazgo central:**

> Hay diferencias verificables entre la decisión lógica de fallback, el modelo realmente transportado al proveedor y la ausencia de un idioma destino explícito en el esquema/prompt efectivos; estimación de tokens y límites comerciales son contratos distintos de un presupuesto de gasto ejecutable.

**Defectos dominantes confirmados:** **GAP-0.4-01** (E-001/013, modelo retirado), **GAP-0.4-02** (E-002, fallback no conmuta), **GAP-0.4-03** (E-003/011/012, destino `es` ausente), **GAP-0.4-04** (E-019, fallback puede autorizar un total mayor que su ventana). P1 locales; ningún fallo de API medido.

**Veredicto forense de cierre:** el mecanismo de entrada, prompt, presupuestación, proveedor y validación está caracterizado con cuatro defectos locales trazados y límites de evidencia explícitos. Los controles de salida/estimación no prueban un máximo comercial de gasto, y los GAP permanecen OPEN. **FROZEN documental**, no `PRODUCT_READINESS=PASS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **OBSERVED:** código leído de `main@1d21cfe`, especificando campo, constructor y consumidor. No se realizaron requests LLM, cargos, pruebas de tokenización contra el modelo comercial ni CI.
- **REQUIRED:** reglas FROZEN pertinentes y mandato de traducir PDF científico al idioma objetivo; cualquier norma adicional debe citarse literalmente antes de atribuir obligaciones.
- **DECISION:** D-1/D-2 fijaron OCR→G3→G5; owner aclaró EN→ES y necesidad de actualizar inferencia el 2026-11-19. No autorizó modelo/proveedor concreto, multidioma ni gasto.
- **LÍMITE:** proveedor real, tokens facturados, privacidad y cotas por operación son **NO VERIFICABLE** mediante lectura estática. La **retirada del modelo** sí se verificó contra el anuncio oficial de Groq (fuente externa de 2025, consultada 2026-11-19), pero sin request autenticado. PPPR.0.5 auditará autoridad de ejecución, retries, UNKNOWN y estado; PPPR.0.7 despliegue/secretos; PPPR.0.8 testigos científicos.
- **NO EJECUTADO:** pytest, SQLite, SDK de Groq/Gemini, red, PDF privado, Tectonic y corpus sellado.

## 3. ALCANCE AUDITADO — PERÍMETRO DE CIERRE

| Superficie | Símbolos / pruebas observadas | Estado y límite |
|---|---|---|
| CLI y admisión | `apps/cli/{main,pdf_product,pdf_inbox}.py::parse_arguments/_run_g3/run_admitted_pdf` | **AUDITADO** — E-0.4-011. Host/permisos/seguridad de input: 0.7 |
| Root G3 | `runtime/engine.py::_create_chunk_processor/run_pipeline`; selección de runnable y configuración | **AUDITADO focal** — E-001/007/018/019. Lease/CAS FSM/SQLite: 0.5 |
| Prompt y lengua | `apps/llm_workers/{prompt_builder,sync_bridge}.py`; `core/prompting/{models,renderer,canonicalizer,intent_mapper,measurement_adapter}.py` | **AUDITADO** — E-002/003/004/012/015/017 |
| Modelo y salida de red | `apps/bootstrap/provider_stack_factory.py`, `apps/llm_workers/adapters.py::GroqProvider.translate`, `core/prompting/dialects/openai_compatible.py` | **AUDITADO** — E-001/002/006; request comercial NO EJECUTADO |
| Fuente externa de estado modelo | Groq Docs, `/docs/deprecations`, entrada «August 30, 2025: llama3-70b-8192» | **CONSULTADO** 2026-11-19 — E-013; no sustituye estado de credenciales propias |
| FinOps y cuotas | `core/validation/{budget,estimators}.py`, `core/finops/measurement.py`, `apps/llm_workers/{rate_limiter,cache_provider}.py` | **AUDITADO focal** — E-005/008/009/014/017/019; no presupuesto monetario acreditado |
| Tests versionados | `tests/unit/{test_prompt_builder,test_rate_limiter}.py`, `tests/integration/{test_g3_b4_3a_engine_staging,test_g3_b3_structured_result_contract,test_w06_g3_uncertain_effect_offline,test_g3_b1_policy_guardrails,test_w08_cli_foreground_single_generation_offline}.py` | **AUDITADOS como fuentes / NOT_RUN** — E-010/016/020/021, sin certificación comercial |
| Contratos FROZEN | NADR-F17BIS-06 §5.1; NADR-F17BIS-05 (contexto); scope/principios/PPPR.0.1–0.3 | **CONTRASTADO** para obligación de compatibilidad de tokens, identidad y fail-closed |
| FSM W06, reutilización y publicación | `runtime/engine.py`, W06 offline; repositorios y g5 | **REFERENCIADO**: PPPR.0.5/0.6; no generalizar de un harness |
| Host/seguridad, modelo vigente y corpus | Docker, claves, cuenta, tests con PDFs y oráculos científicos | **FUERA DEL MANDATO o NO VERIFICABLE**: PPPR.0.7/0.8 |

**Suficiencia §8.1:** las responsabilidades del mandato **CLI→G3→request/guards, presupuesto, cuotas y testigos** fueron auditadas por lectura focal de código y norma del SHA fijado. Modelos futuros, tokenizador real, costo facturado, estado FSM, G5, secretos/host y oráculo científico se delimitan como **REFERENCIADOS/NO VERIFICABLE** y se derivan a PPPR.0.5–0.8, ADR Maestro o Execution Plan. El 100% se refiere al perímetro forense **declarado**, no a equivalencia de PDF traducido, cobertura de todos los consumidores del repositorio ni ejecución de CI.

## 4. FUENTES DE EVIDENCIA Y PRECEDENCIA

**Normativa:** metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN (§4.7/4.8, §7/§8); `PROJECT_SCOPE.md` §§1–2 y `ENGINEERING_PRINCIPLES.md` §§III–IV; `NADR_06_Token_Estimation_Compilation_Governance.md` §5.1 R1–R4 (**compatibilidad con tokenizador efectivo**); `NADR_05_Real_Context_Resolution.md` §5; D-1/D-2 y Atlas. **No se atribuye al NADR-06 una regla de precio/costo absoluto que su §5.1 no expresa.**

**Código primario del SHA fijado:** `apps/cli/main.py`, `apps/cli/pdf_product.py`, `runtime/engine.py`, `apps/llm_workers/{prompt_builder,sync_bridge,adapters,rate_limiter,cache_provider}.py`, `apps/bootstrap/provider_stack_factory.py`, `core/prompting/{models,renderer,measurement_adapter,canonicalizer}.py`, `core/validation/{budget,estimators}.py`.

**Fuente externa oficial del proveedor (contextual, no un test):** Groq, «Model Deprecation», <https://console.groq.com/docs/deprecations> (verificada el **2026-11-19**). Enumera `llama3-70b-8192` con **shutdown 2025-08-30** y aclara que los IDs retirados dejan de ser accesibles. Su reemplazo histórico sugerido, `llama-3.3-70b-versatile`, también figura retirado el 2026-08-16 para free/developer (con excepciones enterprise). **No** seleccionar automáticamente modelos por una recomendación histórica; requerir validación vigente y de cuenta. No se ejecutó ninguna llamada pagada.

**Testigos (solo código, `NOT_RUN`):** `tests/unit/{test_prompt_builder,test_rate_limiter}.py`; `tests/integration/{test_g3_b4_3a_engine_staging,test_g3_b3_structured_result_contract,test_w06_g3_uncertain_effect_offline,test_g3_b1_policy_guardrails,test_w08_cli_foreground_single_generation_offline}.py`. Son testigos versionados con fakes, reloj artificial, SQLite descartable y/o PDF sintético; **ninguno se ejecutó** durante este HITO, ni certifica proveedor real o `en→es` científico.

**Forense heredada:** HITOs PPPR.0.1–0.3 FROZEN; el informe F17-BIS y TST-STAB son cortes históricos y no prueban viabilidad comercial del G3 actual.

## 5. MAPA DE FLUJOS OBSERVADOS (RUTA ÚNICA, PUNTOS DE CONTROL)

```text
apps/cli/main.py translate file.pdf [SIN target_language]              (E-011)
 → inbox → OCR Router → ChunkPlan                                      [PPPR.0.1–0.3]
 → apps/cli/pdf_product.py::_run_g3 → runtime/engine.py::run_pipeline
    → por runnable INFERENCE: _create_chunk_processor
        → PromptBuilder(model=llama3-70b-8192)                         (E-001)
        → BudgetCalculator(primary 8192, fallback 1048576)
        → Groq stack, cache_db_path=None, RPM/TPM quota
    → SyncProviderBridge.execute_chunk
        → contexto W08 validado; protocolos JSON y máscaras matemáticas (E-015)
        → PromptBuilder.build [PromptSchema sin target_lang]           (E-003)
            → presupuesto VALID / COMPRESS / SWITCH_MODEL / REJECT
            → SWITCH_MODEL: target_provider=fallback_large_window
               pero envelope.model_name == builder.model_name         (E-002)
        → GroqProvider.translate
            → RenderedPrompt sin idioma destino                        (E-012)
            → dialecto: messages + response_format json_object
            → create(model=envelope.model_name, SIN max_tokens)         (E-006/014)
        → parse_chunk_response / verificación miembros y math tokens  (E-015)
    → receipt/estados y publicación [PPPR.0.5/0.6]
```

**Separación de límites:** `cache_db_path=None` desactiva una caché LLM por prompt, no estados `COMPLETED` ni materializaciones de FSM. `GROQ_RPM_LIMIT/GROQ_TPM_LIMIT` regulan solicitudes/tokens estimados por ventana, **no** un máximo facturable de USD; NADR-06 §5.1 gobierna estimación compatible con proveedor, no precio. No se llama al proveedor en esta auditoría.

## 10. REGISTRO DE EVIDENCIA FORENSE — FINAL

| ID | Sev. | Observed y fuente | Required / Decision / límite | Estado |
|---|---|---|---|---|
| **E-0.4-001** | **P1** | `runtime/engine.py::_create_chunk_processor` fija `llama3-70b-8192`; Groq anuncia shutdown 2025-08-30 (E-013). | Modelo comercial activo exigible para traducción real (scope §§1–2); no se prescribe sustituto ni se presume ensayo API. | **GAP-0.4-01 OPEN** |
| **E-0.4-002** | **P1** | `PromptBudgetCalculator.calculate` emite `SWITCH_MODEL`; `PromptBuilder` conserva `envelope.model_name`; `GroqProvider` envía ese mismo modelo pese a `target_provider=fallback_large_window`. | Decision aceptada no gobierna modelo físico; ventana fallback distinta del request real. | **GAP-0.4-02 OPEN** |
| **E-0.4-003** | **P1** | `PromptSchema` y `PromptRenderer` omiten idioma destino; tampoco lo transmite el CLI; el puente alude a idioma «configurado» inexistente en ese contrato (E-011/012). | La traducción fiel necesita identidad de idioma objetivo trazable, no inferida por el modelo (scope §1 y principios III/IV). | **GAP-0.4-03 OPEN** |
| **E-0.4-004** | P2 | `SyncProviderBridge.execute_chunk` crea JSON de miembros, preserva máscaras y usa `target_lang_expansion=2.0` al presupuestar. | `expansion` es reserva estimada, NO elección de lengua ni techo físico de salida. | OBSERVADO |
| **E-0.4-005** | P2 | `ExactBPEEstimator("cl100k_base")` es inyectado a la medición. | NADR-06 §5.1 exige compatibilidad con el tokenizador del modelo efectivo; `cl100k_base` por sí mismo no la acredita. | PENDIENTE VALIDACIÓN |
| **E-0.4-006** | P2 | `GroqProvider.translate` invoca SDK sin `max_tokens`/`max_completion_tokens` en la llamada ni en `OpenAICompatibleDialect.build_request_kwargs`. | Reserva presupuestaria ≠ imposición de máximo físico de salida; no inventar obligación absoluta de gasto en NADR-06. | RIESGO DOCUMENTADO |
| **E-0.4-007** | P2 | `build_provider_stack` selecciona Groq por defecto y admite Gemini para benchmark; `cache_db_path=None` desactiva solo caché `CachedLLMProvider`. | No declarar desactivados reutilización durable o estados de tareas en PPPR.0.5. | RECONCILIADO |
| **E-0.4-008** | P2 | `NADR-F17BIS-06` §5.1 R1–R4 exige estimación compatible y desacoplada. El G3 inyecta BPE, no el contador heurístico de palabras usado por algunos tests. | El contador versionado no prueba equivalencia al tokenizador remoto ni sobreprecio. | NORMA CONTRASTADA |
| **E-0.4-009** | P2 | `QuotaManager` reserva RPM/TPM por `envelope.estimated_tokens`, no moneda ni respuesta real facturada. | Rate limiting y budget comercial son responsabilidades distintas. Estado persistente: PPPR.0.5. | LÍMITE |
| **E-0.4-010** | P2 | `test_w06_g3_uncertain_effect_offline.py` usa fake para pérdida de respuesta post-aceptación, comprobando por aserción una sola llamada y estado UNKNOWN. | Testigo declarativo `NOT_RUN` y auditoría FSM real en PPPR.0.5. | TESTIGO |
| **E-0.4-011** | P2 | `apps/cli/main.py::parse_arguments` define `translate file_path` con `--job-id`, `--inbox-dir`, `--run`; no `--target-language`. `pdf_product.py::_run_g3` llama `run_pipeline(document_id,ast_hash)` sin idioma. | Corrobora el origen ausente de la identidad lingüística; **no** afirma que la interfaz futura deba usar ese nombre de bandera. | CONFIRMADO |
| **E-0.4-012** | P2 | `sync_bridge.py::execute_chunk` instruye «configured target language» sin código concreto; `PromptRenderer.render` transmite solo intent/topología/breadcrumbs/constraints/payload. | El texto puede pedir traducir, pero no especifica lengua destino; sin inventar una configuración fuera del schema. | CONFIRMADO |
| **E-0.4-013** | P2 | Groq Docs `/docs/deprecations` presenta `llama3-70b-8192` con **shutdown 2025-08-30**; consulta pública 2026-11-19. | Estado de soporte documental externo, no error reproducido con credenciales ni disponibilidad particular por cuenta. | CONFIRMADO DOCUMENTAL |
| **E-0.4-014** | P2 | `PromptBudgetCalculator` calcula reserva dinámica y el G3 mide `estimated_tokens`, pero la llamada SDK no fija techo output y no hay acumulador monetario en la ruta inspeccionada. | FinOps/tokens estimados ≠ hard cap de dólares; evaluar necesidad y gate seguro en ADR PPPR. | LÍMITE / DECISION CANDIDATE |
| **E-0.4-015** | P2 | `SyncProviderBridge.execute_chunk` valida `ContextSnapshotV1`, binding del plan, tokens de matemáticas por miembro y `parse_chunk_response` tras extraer JSON root `content`. | Preservación/validación estructural estática; respuesta comercial y traducción lingüística no verificadas. | GUARDIA CONECTADA |
| **E-0.4-016** | P2 | `test_prompt_builder.py` prueba hash/envelope; `test_rate_limiter.py` usa clock fake; G3-B4/3a y W06 usan dobles/SQLite temporal. | No hay en estos testigos una aserción de extremo a extremo sobre idioma destino o fallback de modelo físico; no atribuir `PASS`. | LÍMITE DE TEST |
| **E-0.4-017** | P2 | `PromptMeasurementAdapter.physical_network_payload` es JSON canónico de `PromptSchema`, mientras la petición HTTP contiene `RenderedPrompt`→messages y `response_format`; representaciones diferentes. | Requiere demostrar si la medición de tokens sobre el schema aproxima correctamente el request y el modelo efectivo (NADR-06). No atribuir subestimación cuantitativa sin caso focal. | HALLAZGO POR PROFUNDIZAR |
| **E-0.4-018** | P2 | `runtime/engine.py` marca `G3_EXTERNAL_UNKNOWN` ante fallos posiblemente posteriores al efecto y distingue `CircuitOpenError` antes de red; W06 test usa fake. | Respetar separación de autoridad/retry y durabilidad en PPPR.0.5. No alegar segundo efecto sin evidencia. | FRONTERA DELIMITADA |
| **E-0.4-019** | **P1** | `PromptBudgetCalculator.calculate` emite `SWITCH_MODEL` si `core_tokens <= fallback_window_limit` sin comparar `core_tokens + ctx_tok` contra fallback; `PromptBuilder` acepta esa decisión. | Puede aprobar un total que supera su propia ventana alternativa. | **GAP-0.4-04 OPEN** |
| **E-0.4-020** | P2 | `parse_chunk_response` rechaza >4 MiB de respuesta por bytes UTF-8 **después** de la llamada comercial. | No equivale a `max_completion_tokens` pre-red ni tope de gasto; E-006/014. | GUARD POST-EFECTO |
| **E-0.4-021** | P2 | `test_w08_cli_foreground_single_generation_offline.py` usa PDF sintético, parser controlado, proveedor fake y SQLite descartable para la ruta foreground. | Testigo de wiring, no calidad STEM ni Groq real; **NOT_RUN** aquí. | ALCANCE TEST |

### Fichas P1 extendidas (§4.7)

#### Evidencia E-0.4-001 — ID de modelo fuera de soporte documentado

- **Fuente primaria:** `runtime/engine.py::_create_chunk_processor`; `apps/llm_workers/adapters.py::GroqProvider.translate`. **Fuente oficial independiente:** `https://console.groq.com/docs/deprecations` (consulta 2026-11-19).
- **Declaración observada:**

```python
# runtime/engine.py
builder = PromptBuilder(model_name="llama3-70b-8192", ...)

# apps/llm_workers/adapters.py
response = await self._client.chat.completions.create(model=envelope.model_name, ...)
```

- **Observed:** el modelo se fija en la composición y llega por `envelope.model_name` a la llamada real. El proveedor **documenta shutdown del ID exacto el 2025-08-30**. No se ejecutó ninguna request con claves.
- **Required:** el propósito de traducción LLM del `PROJECT_SCOPE.md` §§1–2 requiere un servicio seleccionable **utilizable** por la operación; ingeniería §IV exige no ocultar fallos de borde. La política de ciclo de vida del proveedor es **hecho externo**, no un NADR interno que prescriba modelo.
- **Decision:** D-1/D-2 eligieron la ruta G3, **no** un modelo congelado ni reemplazo comercial concreto.
- **Hallazgo/consecuencia:** el ID configurado carece de soporte según la documentación oficial, lo que bloquea presumir disponibilidad comercial de la composición actual. No se presenta como HTTP 4xx efectivamente observado ni como prueba de incidencia en un tenant específico.
- **Severidad:** **P1 LOCAL**, defecto de viabilidad del provider configurado; P0/certificación física pendiente de un gate separado.
- **Estado:** **OPEN → GAP-0.4-01**. Destino: gobernanza PPPR después de Fase 0, con modelo/proveedor y autorización para prueba a decidir en ADR/Execution Plan.

#### Evidencia E-0.4-002 — SWITCH_MODEL lógico sin conmutación física

- **Fuentes/símbolos:** `core/validation/budget.py::PromptBudgetCalculator.calculate`, `apps/llm_workers/prompt_builder.py::PromptBuilder.build`, `apps/llm_workers/adapters.py::GroqProvider.translate`.
- **Declaración observada:**

```python
if core_tokens <= self.fallback_window_limit:
    return BudgetDecision(status=BudgetDecisionType.SWITCH_MODEL, ...)

# PromptBuilder
if decision.status in (BudgetDecisionType.VALID, BudgetDecisionType.SWITCH_MODEL):
    best_schema = test_schema
model_name=self.model_name,
target_provider="fallback_large_window" if decision.status == BudgetDecisionType.SWITCH_MODEL else "primary"

# GroqProvider
model=envelope.model_name,
```

- **Observed:** el builder acepta el branch de fallback, marca metadata `target_provider`, pero conserva el modelo primario; el adaptador Groq ignora `target_provider` y envía `envelope.model_name`. No existe un segundo ID de modelo en esta composición.
- **Required:** contrato local explícito `SWITCH_MODEL` y presupuesto de ventana alternativa: si se autoriza por capacidad alternativa, esa decisión debe gobernar la operación física o rechazarse; `ENGINEERING_PRINCIPLES.md` §§III–IV exige explicitud y cero fallback silencioso. **No** se atribuye esta regla a NADR-06 como obligación textual de tener dos proveedores.
- **Decision:** no hay decisión aprobada de nuevo fallback/modelo comercial en PPPR; no se prescribe cómo resolverlo.
- **Consecuencia demostrable:** unidades que exceden la capacidad primaria pueden recibir autorización `SWITCH_MODEL` sin conmutación física. No demuestra cuántos casos ocurren, ni error HTTP concreto; el modelo retirado es un GAP independiente.
- **Severidad:** **P1 LOCAL**, discrepancia estructural entre decisión y ejecución.
- **Estado:** **OPEN → GAP-0.4-02**, gate de modelos/ventanas en ADR y Execution Plan posterior.

#### Evidencia E-0.4-003 — idioma destino no representado ni transmitido

- **Fuentes/símbolos:** `apps/cli/main.py::parse_arguments`, `apps/cli/pdf_product.py::_run_g3`, `runtime/engine.py::run_pipeline`, `apps/llm_workers/sync_bridge.py::execute_chunk`, `core/prompting/models.py::PromptSchema`, `core/prompting/renderer.py::PromptRenderer.render`.
- **Declaración observada:**

```python
# CLI (subcomando translate)
t_parser.add_argument("file_path", type=str, ...)

# pdf_product.py
run_pipeline(document_id, ast_hash)

# SyncProviderBridge
"each member independently into the provider's configured target language."

# PromptRenderer
f"INTENT: {schema.intent.value}\\n"
```

- **Observed:** ni la CLI, ni la firma de G3, ni el esquema, ni el render de instrucciones aportan un idioma/código de destino. La única referencia verbal en el payload es a un idioma supuestamente configurado en el proveedor, sin propiedad correspondiente en la composición revisada. `target_lang_expansion` es un factor numérico de presupuesto, no una selección lingüística.
- **Required:** traducir documentos STEM a un destino identificable es condición semántica del producto `PROJECT_SCOPE.md` §1 y del mandato PPPR; `ENGINEERING_PRINCIPLES.md` §§III–IV exige un contrato explícito y trazable. **No** se infiere que deba existir exactamente una bandera CLI `--target-language`, ni qué idiomas se soportarán.
- **Decision:** D-1/D-2 definen la ruta; ninguna decisión vigente de destino implícito global ha sido acreditada.
- **Consecuencia:** el LLM recibe una instrucción de traducción sin objetivo explícito; no se puede garantizar idioma de salida ni validar identidad lingüística del resultado desde este contrato. No se afirma que un LLM real haya traducido al idioma equivocado.
- **Severidad:** **P1 LOCAL**, omisión en interfaz de requisito funcional esencial.
- **Estado:** **OPEN → GAP-0.4-03**. Política de idiomas y propagación de identidad a decidir después de Fase 0.

#### Evidencia E-0.4-019 — fallback admite sobrepasar su propia ventana

**Archivo/símbolos:** `core/validation/budget.py::PromptBudgetCalculator.calculate`, `apps/llm_workers/prompt_builder.py::PromptBuilder.build`.

```python
core_tokens = sys_tok + pay_tok + reserve
if core_tokens <= self.fallback_window_limit:
    return BudgetDecision(
        status=BudgetDecisionType.SWITCH_MODEL,
        required_window_size=core_tokens + ctx_tok,
        # ...
    )
```

**Observed:** la rama compara solo `core_tokens` con `fallback_window_limit` y acepta `SWITCH_MODEL` sin comprobar el contexto. El builder lo acepta en la primera iteración. **Contrajemplo analítico NO ejecutado:** con ventana primaria 8192, fallback 1048576, núcleo 9000 y contexto 1100000, se acepta el núcleo aunque el total requerido sea 1109000, mayor a fallback.

**Required:** contrato tipado de presupuesto y `ENGINEERING_PRINCIPLES.md` §IV: no afirmar cabida bajo un límite que el propio `required_window_size` supera; NADR-06 §5.1 exige estimación compatible, no prescribe el algoritmo de fallback. **Decision:** D-1/D-2 no seleccionó modelo/ventana alternativos.

**Consecuencia:** una decisión `SWITCH_MODEL` puede representar un plan que no cabe ni en su ventana alternativa. Es distinto de GAP-0.4-02 (modelo físico sin cambio); no se demuestra error HTTP ni gasto medido. **P1 LOCAL, OPEN → GAP-0.4-04**, destino ADR Maestro/Execution Plan.

## 14. GAPS CONSOLIDADOS — ABIERTOS, SIN IMPLEMENTACIÓN

| GAP | Descripción | Evidencia | Pilar / contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.4-01** | El modelo concreto configurado para G3 fue retirado oficialmente en 2025 | **E-0.4-001, E-0.4-013** | `PROJECT_SCOPE.md` §§1–2 (operación de traducción); soporte de Groq publicado en Docs oficiales | PPPR posterior a Fase 0: decisión modelo/proveedor y testigo autorizado en ADR/Execution Plan | **OPEN · P1 LOCAL** |
| **GAP-0.4-02** | `SWITCH_MODEL` autoriza fallback pero ninguna rama cambia `envelope.model_name` | **E-0.4-002** | Contrato `BudgetDecisionType.SWITCH_MODEL` + principios explicitud/fail-closed | PPPR posterior a Fase 0: decisión sobre comportamiento de fallback y modelo real; Execution Plan | **OPEN · P1 LOCAL** |
| **GAP-0.4-03** | Falta destino español explícito en CLI→prompt | **E-0.4-003, E-0.4-011/012** | Scope STEM + owner 2026-11-19: EN→ES; principios III–IV | ADR/Execution Plan: contrato explícito sin multidioma inicial | **OPEN · P1 LOCAL** |
| **GAP-0.4-04** | `SWITCH_MODEL` puede autorizar core+contexto por encima de fallback | **E-0.4-019** | Contrato tipado BudgetCalculator + fail-closed | ADR Maestro / Execution Plan posterior con ventana real verificada | **OPEN · P1 LOCAL** |

**Responsable de implementación:** **NO ASIGNADO** hasta el Execution Plan aprobado. El owner fijó EN→ES y la necesidad de actualizar inferencia, no su diseño. Estos GAPs identifican responsables **técnicos del comportamiento**, no prescriben un modelo, un API, una CLI nueva ni un plan de remediación. No se promueven a GAP automáticamente: falta de hard cap en dólares, ausencia de `max_completion_tokens`, compatibilidad no medida de `cl100k_base`, ni diferencia entre schema medido y request real. Son riesgos o Decision Candidates, sujetos a contrato adicional y falsadores.

## 15. ESTADO TERMINAL DE HIPÓTESIS Y DESTINOS (§8.1–8.2)

| ID | Veredicto de esta pasada | Evidencia, límite y destino |
|---|---|---|
| **H-0.4-A** | **CONFIRMADA** | Lengua destino ausente en CLI→schema→renderer→provider, E-003/011/012 → GAP-0.4-03. No se atribuye error comercial medido |
| **H-0.4-B** | **CONFIRMADA** | `SWITCH_MODEL` no cambia modelo físico, E-002 → GAP-0.4-02. Branch causal demostrable sin llamada |
| **H-0.4-C** | **CONFIRMADA DOCUMENTALMENTE** | Groq anuncia retirada exacta del modelo, E-001/013 → GAP-0.4-01; acceso y respuesta de cuenta real NO VERIFICABLE |
| **H-0.4-D** | **CONFIRMADA ACOTADA** | Reserva/quota RPM/TPM no equivale a hard cap monetario; la guarda de respuesta de 4 MiB es post-efecto, no salida pre-red (E-006/009/014/020). `DC-0.4-01` decide la necesidad y umbral |
| **H-0.4-E** | **CONFIRMADA EN CÓDIGO** | JSON root `content`, inner manifest y math tokens tienen guards, E-004/015; salida física y degradación real NO VERIFICABLE → `DQ-0.4-01` en PPPR.0.8 |
| **H-0.4-F** | **NO VERIFICABLE en 0.4** | W06 offline y handler UNKNOWN observados, E-010/018, pero no se audita aquí todo el estado duradero; `DQ-0.4-02` → PPPR.0.5, no bloqueo de G3 prompt |
| **H-0.4-G** | **NO VERIFICABLE** | `cl100k_base` inyectado, pero compatibilidad con tokenizador efectivo y esquema físico de request no demostrados; `DQ-0.4-03` → PPPR.0.8/0.7 con proveedor autorizado, sin gasto no autorizado |

### 15.1 Deferred Questions y Decision Candidates (diferidas a sus gates)

| ID | Objeto y motivo de diferimiento | Destino |
|---|---|---|
| **DQ-0.4-01** | ¿Los guards JSON/math y la respuesta realmente operan bajo un proveedor disponible? Fake ≠ servicio real | PPPR.0.8; posible testigo focal seguro posterior a aprobación |
| **DQ-0.4-02** | ¿Qué autoridad maneja efectivamente UNKNOWN/retry/recovery? Requiere contratos FSM/SQLite y W06 completos | PPPR.0.5; no reabrir W06 como defecto sin evidencia |
| **DQ-0.4-03** | ¿La medición de tokens del prompt físico coincide con la tokenización del modelo futuro y su ventana? El schema medido difiere del request real (E-017) | PPPR.0.7/0.8, NADR-06 |
| **DQ-0.4-04** | ¿Qué modelo/proveedor vigente sirve para EN→ES con JSON, ventana, privacidad, costo y cuenta autorizada? Requiere selección posterior, sin calls pagas hoy | ADR Maestro / PPPR.0.8 |
| **DC-0.4-01** | ¿Es requisito contractual un presupuesto monetario/tokens por operación antes de toda llamada comercial, con qué techo y protección? | ADR Maestro posterior a Fase 0; no imponer cifras arbitrarias |
| **DC-0.4-02** | **Fijado:** solo EN→ES por owner. **Pendiente:** expresar y validar `source=en,target=es` en contrato/generación sin implementar multidioma innecesario | ADR Maestro/Execution Plan |
| **DC-0.4-03** | Comportamiento de fallback: modelo compatible real o rechazo explícito, con ventana comprobada | ADR Maestro/Execution Plan |
| **DC-0.4-04** | **Fijado:** renovar inferencia obsoleta. **Pendiente:** Groq con modelo vigente u otro backend, según calidad STEM EN→ES, límite, tokenizer, privacidad y costo; no copiar sustitutos históricos | ADR Maestro/Execution Plan |

**Disposición §8.1–8.2:** H-0.4-A…E tienen conclusiones estáticas/documentales confirmadas en su alcance; H-0.4-F/G son `NO VERIFICABLE` en este HITO y se derivan a DQ concretas. Las cuatro DQ indican motivo, no-bloqueo y destino; las cuatro DC delimitan decisiones que solo podrá resolver gobernanza posterior. **Ninguna queda abierta como hipótesis indeterminada.** Esta clasificación no acredita ejecución ni aprueba un diseño de proveedor/fallback.

## 16. RESPUESTAS AL MANDATO — CONCLUSIÓN

El G3 usa Groq con ID retirado y contiene estimación, cuotas y validación JSON/math. Son **4 GAP P1 locales**: modelo retirado, fallback sin conmutación física, destino `es` ausente y aceptación de fallback sin comprobar el total de la ventana. El owner fija EN→ES solamente y pide renovar inferencia, sin elegir proveedor. `cl100k_base` y el schema medido no acreditan tokenizador/prompt wire; 4 MiB post-respuesta no limita costo pre-I/O.

## 21. CIERRE DEL HITO PPPR.0.4 — FROZEN v1.0.3

### 21.1 Checklist obligatorio de cierre (§8.1–8.2)

| Condición | Resultado y evidencia |
|---|---|
| Metadata, estado, tipo, fecha y changelog | **CUMPLE** — encabezado, baseline `main@1d21cfe`, versiones 1.0.0–1.0.3 |
| Resumen con hallazgo central, consecuencias y veredicto | **CUMPLE** — §1, E-001/002/003/019 y los cuatro GAPs |
| Método read-only y límite epistemológico | **CUMPLE** — §2; documentación externa ≠ llamada comercial |
| Cobertura del perímetro declarado | **CUMPLE para mandato estático** — §3: CLI→G3, builder, presupuesto, proveedor, respuesta y testigos; estado/host/G5/GT referenciados o no verificables |
| Fuentes normativas, código, tests y estado proveedor | **CUMPLE** — §4 y SHA fijado; Groq oficial citado como hecho externo |
| Mapa del flujo conectado y separación de consumidores | **CUMPLE** — §5; D-1/D-2 no reabiertos; cache prompt ≠ FSM |
| IDs estables y severidad de toda evidencia | **CUMPLE** — 21 entradas E-0.4-001…021 (§10) |
| Fichas extendidas P1, Observed/Required/Decision | **CUMPLE** — E-0.4-001/002/003/019 (§10); alcance P1 LOCAL delimitado |
| Gaps con evidencia, contrato, estado y destino | **CUMPLE** — GAP-0.4-01…04 **OPEN** (§14); ninguna solución aprobada |
| Hipótesis con veredicto terminal | **CUMPLE** — H-0.4-A…G (§15); ninguna `TO BE VERIFIED` sin disposición |
| Deferred Questions con motivo, no-bloqueo y destino | **CUMPLE** — DQ-0.4-01…04 → PPPR.0.5/0.7/0.8 y ADR, §15 |
| Decision Candidates separados de decisiones previas | **CUMPLE** — DC-0.4-01…04, §15; owner fija EN→ES y necesidad de renovar inferencia, no proveedor concreto |
| Contradicciones con HITOs anteriores y no-regresión | **CUMPLE en el perímetro** — PPPR.0.1–0.3 reutilizados; W06/SQLite y ciencia derivadas a sus HITOs, no declaradas erróneamente como ausentes |
| Garantías, cadena de gobernanza y próximo paso | **CUMPLE** — §§21.2–21.4 |
| Ejecución real/CI/GT | **NO REQUERIDA** para el mandato read-only; **NOT_RUN**, sin `PRODUCT_READINESS=PASS` |

**Regla §8.2:** el modelo comercial sustituto, tokenizador efectivo, coste facturado y comportamiento de W06/JSON bajo servicios reales **no se resuelven en este HITO**. Sus limitaciones, destinos y ausencia de bloqueo del inventario estático están documentados. Impiden certificar el producto y deben quedar como gates posteriores, no como `PASS`.

### 21.2 Declaración de cierre y garantías

**Estado: FROZEN v1.0.3 — 2026-11-19.** Se cierra **exclusivamente** la auditoría documental y estática de G3 (prompt, idioma, proveedor/modelo, ventanas, presupuesto, cuota, salida JSON/math y límites de W06) para la ruta observada en `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.

**Garantías positivas por código:** el stack conecta proveedor Groq, limitador RPM/TPM, circuit breaker y validador estructurado; el builder calcula reservas y decisiones; el bridge liga la respuesta a identidad de unidad y placeholders matemáticos; existe límite de 4 MiB del parser **post-respuesta**, no un techo físico pre-red. `cache_db_path=None` desactiva la capa de cache por prompt, no todos los reusos durables.

**Hallazgos abiertos:** `GAP-0.4-01` (modelo retirado), `GAP-0.4-02` (fallback sin conmutación física), `GAP-0.4-03` (idioma destino español no transmitido) y `GAP-0.4-04` (fallback no valida el contexto total) permanecen **P1 LOCAL / OPEN**. El propietario fijó como producto inicial solo **inglés→español**, sin multidioma, y pidió renovar inferencia. **No** se ha elegido el proveedor/modelo sustituto ni autorizado cambios de producción.

**Garantías NO otorgadas:** llamadas HTTP exitosas, cuenta o credenciales aptas, calidad STEM EN→ES, preservación semántica de PDFs, selección de modelo vigente, compatibilidad `cl100k_base` con tokenizer de proveedor, cabida real del prompt wire, máximo de salida o de gasto facturable, autoridad de retry/CAS/UNKNOWN, seguridad de hosting, GT/corpus ni PDF final certificado. No hubo nuevos `pytest`, Docker, SQLite comercial, requests LLM, cobros, compilación TeX, CI ni CV/GT.

**Herramienta de ejecución de código:** no se requiere para acreditar los cuatro desacoples de contrato observables estáticamente; los testigos del repositorio se inspeccionaron pero **no se ejecutaron**. La prueba de proveedor deberá esperar una selección aprobada y un sandbox explícitamente autorizado con límite de gasto, control de una llamada, sin reintentos automáticos y sin corpus privado. El detalle del gate se determinará en ADR/Execution Plan, no en este informe.

### 21.3 Cadena de gobernanza, hechos del owner y no-regresión

Metodología general v1.3.0 FROZEN → metodología forense v1.2.0 FROZEN → `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md` → D-1/D-2 y Atlas de ruta única → NADR-F17BIS-06 §5.1 (tokenización) y -05 (contexto) → HITOs PPPR.0.1/0.2/0.3 FROZEN → **PPPR.0.4 FROZEN v1.0.3** → auditorías PPPR.0.5–0.9 → ADR Maestro, ADR/NADR aplicables → Execution Plan aprobado e integrado en `main` → cambios productivos futuros en PRs separados.

**Reconciliaciones:** no se considera `llama-3.3-70b-versatile` un reemplazo vigente por el mero hecho de figurar en una migración histórica; Groq también documentó su retiro en 2026 para determinados planes. No se trasladan a este HITO defectos de W06 ni de compilación de cortes históricos. La elección `en→es` proviene del owner y debe formalizarse en el ADR; los GAPs ya tienen destino pero ninguno asigna responsable implementativo o arquitectura nueva.

### 21.4 Próximo gate y política Git

El HITO queda **documentalmente preparado para revisión y aprobación del PR interno #69** hacia `pdf-pdf-product-readiness`; el estado FROZEN **no supone aprobación externa ni merge**. Tras aprobar e integrar #69, verificar el documento en la rama general, eliminar la rama corta `pppr/hito-0.4` y recién entonces abrir PPPR.0.5 desde el HEAD general actualizado.

El PR general **#66 permanece Draft y sin merge a `main`** hasta completar los HITOs, ADR Maestro, ADR/NADR y Execution Plan aprobados. El cierre **no** permite cambiar producción.

> FROZEN documental ≠ Fase 0 terminada ≠ modelo comercial viable acreditado ≠ certificación científica ≠ autorización de implementación.
