# HITO_0.1_RUTA_OPERATIVA_Y_PERIMETRO.md

**Estado:** IN_PROGRESS v1.0.0  
**Fecha de emisión:** 2026-11-18  
**Fecha de congelamiento:** N/A  
**Etapa:** PDF→PDF Product Readiness — Fase 0 (auditoría forense). La numeración formal de fase, si corresponde, queda sujeta a gobernanza metodológica.  
**Tipo de artefacto:** Forensic Discovery / Flow Audit  
**Naturaleza:** Read-only. No prescribe código, diseño, cambios de arquitectura ni implementación.  
**Baseline de inspección:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`. Las observaciones posteriores deben citar su SHA de fuente.  
**Evidencia forense vinculante:** handoff de convergencia PDF→PDF, metodología general, metodología HITOs, ADR/NADR FROZEN aplicables, informes TST-STAB y código de `main`.  
**Mandato:** Determinar la ruta ejecutable real, sus fronteras y dependencias, la cobertura necesaria de auditoría y las incertidumbres que impiden planificar por evidencia una traducción PDF→PDF STEM utilizable.  
**Síntesis:** Inicio documentado de la auditoría. Se han identificado contratos y acoplamientos concretos en G3 y CLI, pero **aún no existe inventario exhaustivo, matriz consolidada ni cierre forense**.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-18 | Apertura del HITO, mandato, baseline, método, evidencias iniciales y condiciones de cierre; sin declarar una auditoría completada. |

## 1. RESUMEN EJECUTIVO

El objetivo es observar la composición PDF→PDF desde admisión hasta PDF publicado y los componentes que realmente pueden influir en ese recorrido, incluida la herencia legacy y las obligaciones FROZEN aplicables.

**Hallazgo central de apertura:**

> La convergencia operativa sobre fake está documentada, pero el contrato real de inferencia, los controles de gasto, la identidad de la generación y la fidelidad STEM todavía requieren reconciliación causal contra el código y la evidencia de ejecución. No corresponde fijar tareas ni seleccionar nuevas abstracciones antes de la Fase 0.

**Observaciones directas iniciales verificadas en código:** el constructor G3 usa un modelo y una ventana primaria literales; el presupuesto puede devolver `SWITCH_MODEL` sin cambio físico de `model_name`; el adaptador envía ese mismo modelo; la ruta foreground usa `FSM COMPLETED` como condición de retorno del PDF. Estas observaciones no sustituyen la inspección completa de sus consumidores.

**Veredicto actual:** `IN_PROGRESS`; no habilita ADR, NADR, plan ni PR de implementación.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

- **Observed:** comportamiento constatado por lectura del código, estructura y, cuando exista, pruebas bajo un SHA identificado.
- **Required:** obligación atribuible a fuente normativa vigente, explicitada con regla/alcance; no deducida de preferencia de diseño.
- **Decision:** acuerdo o conclusión histórica con autoridad y alcance comprobables; `FROZEN` no significa que todo esté implementado.
- No convertir test con fake, CI verde o PDF con cabecera válida en prueba de traducción real o fidelidad científica.
- No inferir `NO IMPLEMENTADO` de una búsqueda incompleta ni `RESUELTO` de la existencia de una clase.
- Ningún HITO accede al corpus privado ni altera sellos, GT, SQLite de uso o efectos de proveedor. Evidencia de runtime no disponible se clasifica `NO VERIFICABLE`.
- Este HITO es un arranque documental, **no** una auditoría declarada como realizada de todo el árbol.

### 2.2 Método forense y finitud

1. Congelar el SHA base y leer metodología, decisiones y handoffs relevantes.
2. Delimitar el grafo operativo `CLI → OCR → plan/AST → G3 → materialización → G5 → PDF` y las fronteras de error/reanudación.
3. Enumerar composición y consumidores mediante entrypoints, imports, factories, configuración, repositorios, tests y referencias dinámicas conocidas; declarar límites de búsqueda.
4. Inventariar capacidades por frontera: `CONECTADO`, `IMPLEMENTADO_NO_CONECTADO`, `LEGACY_CON_CONSUMIDOR`, `SOLO_TEST`, `NO_VERIFICADO` o `AUSENCIA_CONFIRMADA_EN_PERIMETRO`. Una clasificación no decide su destino.
5. Contrastar contratos y decisiones de W06/W08, F18, G3/G5, TST-STAB y el handoff existente con las implementaciones y tests actuales; registrar `Observed/Required/Decision`.
6. Documentar escenarios no verificables sin fingir pruebas físicas ni ejecutar proveedor/corpus en esta fase.
7. Emitir evidencias estables y gaps únicamente ante discrepancias fundamentadas; transferir aspectos de otras superficies a HITOs específicos cuando corresponda.
8. Cerrar cuando el perímetro y sus consumidores relevantes estén enumerados y las incertidumbres y límites explícitos sean suficientes para que los HITOs siguientes y la gobernanza no reinventen soluciones existentes.

**Control de alcance:** se inspeccionará todo componente *relevante para el recorrido y sus contratos*, no cada archivo incidental del repositorio con el mismo nivel de profundidad. Los hallazgos fuera de perímetro se derivan, no se absorben sin límite.

## 3. ALCANCE AUDITADO

| Superficie | Archivos/entrada inicial | Cobertura en esta apertura |
|---|---|---|
| CLI/foreground | `apps/cli/main.py`, `apps/cli/pdf_product.py` | AUDITADO FOCAL, no exhaustivo |
| G3/prompt/proveedor | `runtime/engine.py`, `core/validation/budget.py`, `apps/llm_workers/prompt_builder.py`, `apps/llm_workers/adapters.py`, `apps/llm_workers/sync_bridge.py`, `apps/bootstrap/provider_stack_factory.py` | AUDITADO FOCAL, no exhaustivo |
| Plan y contrato de reutilización | `core/chunking/manifest_contract.py`, `core/prompting/inference_identity.py` | REFERENCIADO / inspección parcial |
| OCR, B02, normalización, AST, clasificadores | `apps/ocr_router/`, `apps/bootstrap/pipeline_factory.py`, `core/ast/` y dependencias | POR AUDITAR |
| G5 y recursos científicos | `apps/compiler/`, `core/compiler/`, perfiles, renderer y activos | POR AUDITAR |
| Estado y recuperación | `infra/db/`, `runtime/recovery.py`, `runtime/resumer.py`, `runtime/sweeper.py`, reconciler, W06 | POR AUDITAR |
| Entornos | `docker-compose.yml`, `docker-compose.runtime.yml`, bootstrap, host Windows, Tectonic/cachés | REFERENCIADO; runtime físico no verificado |
| Oráculos y suites | `tests/`, `.github/workflows/`, `reports/certification/`, issue #34 | REFERENCIADO; evidencia científica real no re-ejecutada |
| Legacy | R1/R3, CLI histórica, `build_pipeline`, benchmarks y consumidores potenciales | POR AUDITAR |

**Fuera de alcance en Fase 0:** cambio de código, migración de datos, purga, traducción comercial, campaña de benchmark científico, carga de PDF de terceros y nuevos despliegues.

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Rol |
|---|---|---|
| Normativa | `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` | Secuencia, plantilla, criterio de evidencia y cierres |
| Normativa | `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`, ADR/NADR aplicables | Propósito del producto e invariantes |
| Forense/documentación vigente | `docs/architecture/adr/pipeline-stabilization/handoff/` | Ruta única D-1/D-2; alcance y límites de la convergencia |
| Forense/documentación histórica | `docs/architecture/adr/tests_stabilization/`; `docs/architecture/adr/phase-18/` | Alcances de tests, mecanismos, decisiones y obligaciones existentes |
| Código observado | `runtime/engine.py`, `core/validation/budget.py`, `apps/llm_workers/prompt_builder.py`, `apps/llm_workers/adapters.py`, `apps/cli/pdf_product.py` | Primeros testigos concretos; falta verificar consumidores completos |
| Fuente de restricción | [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34) | Evaluación científica/corpus diferidos y custodia |
| Evidencia pendiente | Host Windows, APIs y proveedores reales, archivos de corpus privados | No verificada por la auditoría de apertura |

## 5. MAPA DE FLUJOS OBSERVADOS

**Topología declarada en el handoff, pendiente de auditoría completa de llamadas y estado:**

```text
CLI/admisión
  → OCR + perfil → AST + ChunkPlan + snapshots durables
  → G3 runtime.engine → claims/leases → SyncProviderBridge
  → proveedor / PRESERVE → recibos y proyecciones
  → FSM READY_FOR_ASSEMBLY → G5/renderer/Tectonic → PDF
```

**Ramas cuyo efecto debe observarse:** rechazo B02; integridad de plan y contexto; unidades `PRESERVE`; `G3_EXTERNAL_UNKNOWN`; reanudación `RESULT_STAGED`; FSM `COMPLETED` y posible reutilización de una salida previa; lease G5; rechazo de PDF inexistente/inválido. Este dibujo no atribuye éxito E2E real.

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

La tabla de §3 es **un índice de superficies**, no un inventario terminado de implementaciones. Los HITOs posteriores o la expansión del presente deben acreditar sus dueños, entradas, consumidores, contratos y efectos. `NO_VERIFICADO` es una salida válida; ausencia solo después de buscar consumidores concretos.

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Dimensión | Observed (código/handoff) | Required (a reconciliar) | Decision previa |
|---|---|---|---|
| Ruta | Un foreground usa `runtime.engine` y el ensamblador existente | Ruta coherente y conservación STEM según scope/contratos | D-1/D-2 aprobadas; no segundo motor productivo |
| G3 budget | Una decisión `SWITCH_MODEL` puede terminar en `model_name` sin cambio de proveedor | No aceptar una capacidad que la petición física no satisface; norma específica aún por mapear | No se acredita un fallback multimodelo |
| Reutilización | G3 deshabilita caché legacy; `COMPLETED` puede devolver PDF existente | Identidad completa y no confundir la fuente con la generación | W08 define identidad candidata de reutilización; no autorización de replay |
| Ciencia | Fake y PDF publicado no demuestran traducción/fidelidad | `PROJECT_SCOPE` exige conservación técnica y rastreabilidad | Evaluación canónica permanece diferida según #34 |

**Esta matriz es inicial y no declara cumplimiento normativo exhaustivo.**

## 10. REGISTRO DE EVIDENCIA FORENSE

| ID | Sev preliminar | Fuente/código | Observación y límite |
|---|---|---|---|
| **E-0.1-001** | P1 | `runtime/engine.py::_create_chunk_processor` | `model_name="llama3-70b-8192"`, `primary_window_limit=8192`, `fallback_window_limit=1048576`. Disponibilidad real del modelo y capacidades de la cuenta NO verificadas aquí. |
| **E-0.1-002** | P1 | `core/validation/budget.py::PromptBudgetCalculator.calculate`; `apps/llm_workers/prompt_builder.py::PromptBuilder.build`; `apps/llm_workers/adapters.py::GroqProvider.translate` | `SWITCH_MODEL` puede ser tratado como éxito por builder, pero el envío usa `envelope.model_name`. No se acredita conmutación física de modelo; efecto operacional de una llamada real NO ensayado. |
| **E-0.1-003** | P1 | `apps/cli/pdf_product.py::run_admitted_pdf` | `COMPLETED` devuelve un PDF existente verificado por header, sin volver a ejecutar G3. Falta auditar si la generación guardada distingue configuración/idioma efectivo. |
| **E-0.1-004** | P1 | `runtime/engine.py::_create_chunk_processor`; `core/prompting/inference_identity.py::InferenceReuseIdentityV1` | Caché legacy G3 deshabilitada; identidad W08 candidata incluye idioma y config, pero no constituye autoridad de ejecución. Conexión efectiva a generación por verificar. |
| **E-0.1-005** | P1 | `apps/llm_workers/sync_bridge.py::execute_chunk`; `apps/llm_workers/adapters.py::GroqProvider.translate` | Instrucción menciona un idioma «configurado»; configuración de idioma explícita no fue acreditada en las firmas inspeccionadas. Se debe inspeccionar el resto de la ruta antes de concluir ausencia. |
| **E-0.1-006** | P1 | `apps/cli/pdf_product.py::preflight_product_run`; `docker-compose.runtime.yml`; handoff de laboratorio | Foreground exige Tectonic en PATH; runtime Docker con override documentado; no se ha demostrado un mismo entorno con Tectonic, acceso autenticado y corrida autorizada real. |

Los IDs se reservan y no se reasignan; estos testigos son **lectura de fuentes**, no falsación ejecutada ni certificación de comportamiento real. La clasificación de severidad y cumplimiento se revalidará antes de cierre; un P1 preliminar no es una conclusión normativa.

## 14. GAPS CONSOLIDADOS

**Estado: NO CERRADO.** En la apertura no se emite una Gap Matrix global ni se determina un destino de implementación sin reconciliar consumidores y autoridad normativa. Las E-0.1-001..006 son insumos para investigación, no equivalen automáticamente a GAP confirmado o a tarea aprobada.

| Gap | Evidencia | Contrato/autoridad | Destino | Estado |
|---|---|---|---|---|
| Sin gaps formalmente consolidados en este corte | E-0.1-001..006 | Por reconciliar con normas vigentes | Por resolver tras investigación | TO BE VERIFIED |

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis a falsar | Estado |
|---|---|---|
| H-0.1-A | El fallback lógico G3 carece de ruta física de respaldo para el proveedor seleccionado | OBSERVADO en la composición inspeccionada; falta verificar consumidores alternos |
| H-0.1-B | Cambiar idioma/modelo sobre el mismo documento puede devolver una generación anterior marcada `COMPLETED` | PLAUSIBLE; requiere inspección integral de persistencia e identidad |
| H-0.1-C | El estado real de F18 y componentes legacy contiene reutilización útil no visible desde la CLI | TO BE VERIFIED |
| H-0.1-D | Extracción/ensamblado omite o rechaza casos STEM representativos más allá de los tests focales | PARCIALMENTE DOCUMENTADO; requiere auditar fronteras y evidencia |
| H-0.1-E | La ruta real tiene restricciones de gasto/egress que pueden impedir una prueba comercial controlada | TO BE VERIFIED |

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

- **¿Hay una ruta PDF→PDF soportada?** Sí, según handoff integrado; éxito con fake no demuestra producto real.
- **¿Está auditado su grafo completo y sus capacidades?** No; este HITO registra apenas las primeras evidencias y el perímetro.
- **¿Se autorizan cambios por los hallazgos de apertura?** No; falta cerrar la auditoría, derivar decisiones normativas y aprobar el plan.
- **¿Debe la nueva etapa inventar soluciones?** No por defecto: se exige búsqueda y clasificación de capacidades y consumidores antes de afirmar ausencia.

## 21. CIERRE DEL HITO 0.1

**Estado del HITO:** IN_PROGRESS v1.0.0; **NO FROZEN**.  
**Condición de cierre:** pendiente. Requiere inventario completo de entrypoints y consumidores relevantes, reconciliación de obligaciones con su versión vigente, referencias de evidencia y límites por superficie, clasificación de hipótesis, contradicciones resueltas o declaradas, y criterios verificables de transferencia a otros HITOs.  
**Verificación de cadena de gobernanza:** metodología revisada; aún no existe ADR/NADR/Execution Plan de esta iniciativa.  
**Decision Candidates generados:** ninguno aprobado; posibles preguntas permanecen en `TO BE VERIFIED`.  
**Siguiente paso:** continuar auditoría read-only y ampliar/emitir HITOs necesarios, con base fija y cierre formal antes de decisiones de diseño.

> No usar esta versión `IN_PROGRESS` como prueba de que la auditoría de Fase 0 esté completa.
