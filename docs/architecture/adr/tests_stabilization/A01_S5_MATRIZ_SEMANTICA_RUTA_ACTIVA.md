# A01-S5 — Matriz semántica de tests de la ruta técnica PDF→PDF

> **Programa:** TST-STAB; etapa **A01-S5 EN CURSO** (primera tanda dirigida de 19 fichas, no censo semántico total). **No se cierran A-01, A-02, A-03, A-04 ni A-05 por publicar esta matriz.**
>
> **Fecha de inspección:** 2026-11-15. **Tests y producción observados en Git:** commit `86cd68672ee692f073b62869e7c9bd177e8d9e3b` (mismo árbol de tests vigente en la rama de trabajo al comenzar la auditoría). **Evidencia operacional de la ruta:** [Atlas de la Ruta Operativa Única](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md), apartados 1, 3, 5 y 6. **Evidencia de colección:** [A01-S6](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md), 1.474 nodeids, sin ejecutar sus cuerpos.
>
> **Método:** lectura directa de los archivos de test y correlación de imports, llamadas y aserciones con la topología del Atlas. **No se ejecutó ningún test, mutación o pipeline** en esta fase. La existencia de un rechazo parametrizado es un *control negativo escrito*, **no** una demostración de «mutation kill» real.
>
> **Gobierno:** sólo documentación en `docs/architecture/adr/tests_stabilization`. No reabrir ciencia/GT, no duplicar el camino OCR→G3→G5, no modificar tests, CI ni producción, y no tocar el PDF eliminado deliberadamente en la copia del owner.

## 1. Qué valida esta auditoría (y qué no)

La ruta soportada es **admisión CLI → inbox → OCR/AST/perfil/plan/contextos → G3 provider/receipts/publicación → G5 resolver/lease/compilación/publicación PDF**. Sus pasos no comparten una transacción global: una prueba de éxito por estado de SQLite no implica éxito físico del PDF y un PDF presente no demuestra commit o fencing. El Atlas es mapa de fronteras, **no** oráculo científico.

Para cada ficha consignamos: **contrato observable**, **SUT real invocado**, **dobles y fronteras**, **aserción independiente observable**, **defecto relevante que debería detectar**, **límite demostrado por lectura** y **próxima comprobación negativa**. Los tests pueden ser estables ante refactors siempre que midan **resultados de API/puertos y estados persistidos**, no un orden accidental de helpers privados; los IDs/hashes/leases que sean contractuales siguen siendo exactos.

**Etiquetas provisionales**, exclusivas de esta auditoría estática:

- **E-OBS:** se leyó una llamada al SUT productivo y aserciones sobre un resultado observable. **No** significa PASS ni sensibilidad probada.
- **E-ALC:** test útil para una frontera **más estrecha** que un supuesto E2E completo (fake de parser/provider/Tectonic, o una sola capa).
- **R-REF:** dependencia visible de interfaz privada, detalles SQL o temporización que conviene evaluar para durabilidad frente a refactors.
- **P-NEG:** candidato a validación negativa/mutación, aún **no ejecutada**.
- **UNKNOWN:** comportamiento/efecto no acreditable sólo por código; no asumir por nombre de archivo o docstring.

**No aplicar «CONFIABLE_PARA_SU_ALCANCE» aún**: requiere ejecución focal, control negativo comprobado y, para P0, sensibilidad a la ruptura relevante del SUT. Tampoco declarar defectuoso un mock situado en una frontera externa.

## 2. Matriz de primera tanda — 19 fichas trazables

| ID / frontera | Test (archivo + línea) y SUT productivo observado | Dobles / alcance | Oracle observable escrito y defecto pretendido | Calificación provisional |
|---|---|---|---|---|
| **TR-001 — admisión** | [`test_pdf_inbox_submission.py`](../../../../tests/integration/test_pdf_inbox_submission.py) líneas 26–105: `submit_pdf_to_inbox` | PDF PyMuPDF generado en `tmp_path`; sustituye sólo `os.link` en el negativo «hardlink unavailable» | SHA-256 exacto, PDF con mismos bytes, sin parcial; deduplicación sin overwrite; colisión de hash/nombre, fuente no PDF/vacía y no disponibilidad de hardlink deben **rechazar sin publicar** | **E-OBS + P-NEG**, contrato de filesystem fuerte; no OCR/compilación |
| **TR-002 — CLI no R1** | mismo archivo, líneas 107–139: `apps.cli.main.handle_translate` | Monkeypatch del **handler R1 prohibido**, no del handler público; usa inbox temporal | R1 no invocado, PDF admitido; `job_id` legacy aborta antes de crear inbox | **E-OBS + E-ALC**, barrera entrypoint, no prueba G3/G5 |
| **TR-003 — parser real** | [`test_verification_pipeline_connection.py`](../../../../tests/integration/test_verification_pipeline_connection.py) líneas 55–105: `build_extraction_pipeline` → `PdfParserAdapter.parse` | PDF temporal real creado con PyMuPDF; **sin parchear parser** | AST no vacío, node_ids presentes/deterministas; vector no representable debe lanzar `B02_UNREPRESENTED_VECTOR_DRAWING` | **E-OBS + P-NEG**, buen candidato; no PDF→PDF ni GT |
| **TR-004 — OCR durable** | [`test_g3_b4_2_ocr_router_durable_plan.py`](../../../../tests/integration/test_g3_b4_2_ocr_router_durable_plan.py) líneas 172–256: `OCRRouterDaemon._process_document`, `DurableContextPlanRepository`, `ControlPlaneRepository` | **Parser, registry AST, profiler/store y FSM handler falsos**; queue SQLite real en `tmp_path`, bytes `%PDF` no analizados | Manifest persistido, un registro de tareas, reingesta idempotente; drifts y documento activo/fallido deben **no** parser ni enqueue | **E-OBS + E-ALC + R-REF**, valida orquestación OCR/queue, **no OCR físico** |
| **TR-005 — contexto W08** | [`test_w08_ocr_g3_context_wiring.py`](../../../../tests/integration/test_w08_ocr_g3_context_wiring.py) líneas 101–220: `prepare_contextual_plan`, `DurableContextPlanRepository` y `SyncProviderBridge.execute_chunk` | SQLite durable verdadero y AST sintético; fake prompt builder y proveedor, no ruta daemon OCR | Contextos de secciones distintos, snapshots reaperturados; contexto ausente/de otra generación falla **antes de provider.calls**; AST hash se conserva | **E-OBS + E-ALC + P-NEG**, preserva binding contextual |
| **TR-006 — staging G3** | [`test_g3_b4_3a_engine_staging.py`](../../../../tests/integration/test_g3_b4_3a_engine_staging.py) líneas 98–188: `stage_claimed_unit` y queue `ControlPlaneRepository` | Fake processor/provider; SQLite real; no loop de G3, ni FSM o publish | `RESULT_STAGED` sin `COMPLETED`; preservación bypass del proveedor; lease erróneo/expirado y respuesta inválida ⇒ sin recibo ni staging | **E-OBS + P-NEG**, seam de recibo acotado |
| **TR-007 — binding/formato LLM G3** | mismo archivo líneas 235–440: `SyncProviderBridge.execute_chunk`, `parse_chunk_response` | Fake provider y builder; sin transporte pagado | Binding `document_id/ast_hash/manifest/chunk`, miembros y tokens matemáticos; respuesta sin binding, PRESERVE enviado, token perdido/injectado ⇒ rechazo | **E-OBS + E-ALC + P-NEG**, valida contrato sintáctico, **no calidad semántica** |
| **TR-008 — recibos fenced** | [`test_g3_b3_2_fenced_receipts.py`](../../../../tests/integration/test_g3_b3_2_fenced_receipts.py) líneas 78–276: `ControlPlaneRepository.stage_chunk_result`, `load_staged_chunk_responses` | SQLite real y AST/plan sintéticos; sin proveedor | Reapertura durable; repeat idéntico sin cambiar `state_version`; conflicto, hash alterado, lease inválido, error SQL ⇒ rechazo/rollback sin recibos | **E-OBS + P-NEG**, contiene barreras normativas persistentes |
| **TR-009 — efecto incierto W06** | [`test_w06_g3_uncertain_effect_offline.py`](../../../../tests/integration/test_w06_g3_uncertain_effect_offline.py) líneas 195–254, 310–321: **`runtime.engine.run_pipeline` real**, `SyncProviderBridge` y `ControlPlaneRepository` | Fake proveedor «primera aceptación + respuesta perdida»; `ASTRegistry`, hash y `get_connection` parcheados hacia datos `tmp_path`; no HTTP real | **Una aceptación externa**, transición `G3_EXTERNAL_UNKNOWN`, sin receipt, sin claim posterior ni reinit de proveedor tras restart; auditoría de execution_id durable | **E-OBS + E-ALC + P-NEG**, **no** prueba exactamente-once de red real |
| **TR-010 — W06 reconciliación** | mismo archivo líneas 278–307: `Reconciler._sweep_tasks` y repo real | Constructor con test doubles y liderazgo simulado; SQLite real | Lease expirado de TRANSLATE sin recibo se cuarentena, conserva execution_id, no vuelve a ser runnable; segundo sweep no reescribe auditoría | **E-OBS + R-REF + P-NEG**, método privado, fake liderazgo |
| **TR-011 — publicación y crash G3** | [`test_g3_b4_3b_publication_recovery.py`](../../../../tests/integration/test_g3_b4_3b_publication_recovery.py) líneas 123–215 y 273–288: `advance_staged_document`, `publish_staged_plan`, `finalize_published_plan`, FSM/queue/materialized | SQLite real; falla inyectada en finalización o comando FSM; proveedor sólo guardado con `pytest.fail` en test de recuperación de engine | Sólo plan íntegro publica; crash antes de finalizar o después de cola se recupera; proyección tampered/incompleta/missing receipt **no** avanza FSM; reanudación sin inicializar proveedor | **E-OBS + P-NEG**, no crash de proceso real ni transacción global |
| **TR-012 — fencing reconciler** | [`test_g3_b4_9_reconciler_fencing.py`](../../../../tests/integration/test_g3_b4_9_reconciler_fencing.py) líneas 86–272: `ControlPlaneRepository` y `Reconciler` / handlers | SQLite in-memory real, fake leadership/reconciler dependencies; mezcla rutas legacy, no daemon vivo | Epoch/owner obsoleto, lease vigente y FSM cancelada bloquean recuperación; receipt G3 no se degrada vía conciliación legacy; requeue una vez | **E-OBS + E-ALC + R-REF**, separar contratos legacy de G3 soportado |
| **TR-013 — lease G5** | [`test_g5_assembler_lease_recovery.py`](../../../../tests/integration/test_g5_assembler_lease_recovery.py) líneas 101–249: `AssemblyLeaseRepository.claim/renew/advance/publish/recover` | SQLite WAL real bajo `tmp_path`; `%PDF-` como byte de control, sin Tectonic | Doble propietario no reclama; lease vivo bloquea recovery; old owner no renueva/publica; nuevo publica tras fencing; versión y estados observados | **E-OBS + P-NEG**, test real del repo, no calidad/compilación PDF |
| **TR-014 — crash y promoción G5** | mismo archivo líneas 253–313: `AssemblyLeaseRepository.publish`, `recover` | Fallo inyectado `os.replace` o commit SQLite, archivos `tmp_path` | Fallo antes de promoción no deja PDF; promoción previa a commit deja estado recuperable y nuevo lease repromueve PDF correcto | **E-OBS + P-NEG**, simula dos puntos de fallo, no crash/FS distribuido |
| **TR-015 — G5 proyección ausente** | mismo archivo líneas 316–434: `AssemblerWorkerDaemon._process_assembly_task` real + `CQRSAssemblyContextResolver` + `CompilationService/DocumentAssembler` | AST provider y materialized-view fake controlados; `NeverInvoked` en Tectonic y puertos no alcanzables; SQLite G5 real | Falta de proyección única => `AssemblyRejectedError`, FSM fallida/retryable y **ningún PDF ni temporal**; fallo si invoca puerto prohibido | **E-OBS + E-ALC + P-NEG**, caso de ausencia total; **no** probar rechazo universal de cualquier falta (política permite tolerancia limitada) |
| **TR-016 — proyección/perfil G5** | [`test_g3_b4_4_profile_projection_assembly.py`](../../../../tests/integration/test_g3_b4_4_profile_projection_assembly.py) líneas 53–205: `SQLiteProfileStore`, `MaterializedPlaneRepository`, `CQRSAssemblyContextResolver`, `CompilationService` | SQLite/ASTRegistry de disco real, fakes externos limitados; no Tectonic | Perfil durable/idempotente; hash de perfil y proyección alterados, generación/versión equivocadas ⇒ rechazo/no consumo; rehidratación produce TeX | **E-OBS + P-NEG**, **no** PDF físico |
| **TR-017 — foreground compuesto** | [`test_w08_cli_foreground_single_generation_offline.py`](../../../../tests/integration/test_w08_cli_foreground_single_generation_offline.py) líneas 85–238: **`apps.cli.main.main()` real**, OCR/G3/G5 roots y SQLite | `build_extraction_pipeline` **reemplazado por parser controlado**, provider offline; `HostTectonicRunner.compile` reemplazado por PyMuPDF que fabrica PDF válido; state `tmp_path` | FSM `COMPLETED`, AST hash, 2 contextos/llamadas de fake, receipts/proyecciones para misma generación y PDF físico de 1 página | **E-OBS + E-ALC + P-NEG**, test de **composición con fronteras simuladas**, **no** parser real + Tectonic real + traducción real |
| **TR-018 — delimitadores matemáticos** | [`test_b024_g3_g5_math_roundtrip.py`](../../../../tests/integration/test_b024_g3_g5_math_roundtrip.py) líneas 10–32: `InlineMathProtector` y `TextRenderStrategy` | Sólo modelos y objetos render; **no invoca daemons G3/G5** | Preserve/restaura expresiones matemáticas y escapa TeX externo; delimitador sin cierre falla | **E-OBS + E-ALC**, útil para invariantes, **nombre «G3/G5 roundtrip» es más amplio que el SUT real** |
| **TR-019 — política de outputs** | [`test_pdf_inbox_submission.py`](../../../../tests/integration/test_pdf_inbox_submission.py) líneas 55–105: `submit_pdf_to_inbox` (subcasos negativos) | `tmp_path`, monkeypatch `os.link` para fallo; sin procesos externos | Colisión con contenido distinto, entrada vacía, extensión inválida, hardlink ausente: siempre **sin PDF publicado y sin partial** | **E-OBS + P-NEG**, solapa TR-001 intencionalmente: ficha específica de «no efecto» |

**Lectura de la tabla:** `E-OBS` significa **«hay aserciones e invocación de SUT en el código»**, no que hayan pasado. `E-ALC` es un límite **honesto**, no un fallo. Los casos parametrizados se agrupan en esta primera tanda por **contrato y frontera**, sin perder la unidad primaria `nodeid` para la fase de sensibilidad.

## 3. Riesgos semánticos localizados, priorizados sin prejuzgar defectos

| ID | Hallazgo por lectura del código | Riesgo para un refactor | Acción de verificación propuesta (no ejecutada) |
|---|---|---|---|
| **RS-01 / P1** | TR-017 sustituye **parser, transporte y Tectonic**; PDF creado por PyMuPDF. Aun así sí ejerce roots CLI→OCR→G3→G5 y comprueba persistencia real | Presentarlo como prueba de **OCR físico o compilación Tectonic real** inventa cobertura. El helper `fake_compile` controla su propio output; no sirve de oráculo de TeX renderizado | Mantener como test de composición; verificar su contrato negativo de **generación/recibos/proyección** sin atribuirle un E2E físico real. No crear otro pipeline |
| **RS-02 / P1** | TR-004 invoca `OCRRouterDaemon._process_document` con **parser, AST registry, perfil y FSM falsos** pero queue real | Cambios legítimos internos pueden obligar a reescribir un test de orquestación; no confundir con OCR parser | Proteger persistencia de plan/manifest y rechazo de generación por **puerto observable**; si se rediseña el daemon, desacoplar nombres privados conservando estados/códigos normativos |
| **RS-03 / P1** | TR-010/TR-012 invocan métodos privados del reconciler y configuran liderazgo artificialmente | Cambios de organización del daemon pueden romper test correcto sin ruptura externa | Conservar pruebas de `G3_EXTERNAL_UNKNOWN`, fencing y no-retry; preferir una costura/puerto estable en remediación futura; no quitar los casos de lease |
| **RS-04 / P1** | TR-015 verifica rechazo de **una proyección ausente entre un solo nodo traducible** | Convertirlo en «cualquier proyección faltante debe fallar» contradice la política productiva del Atlas (hasta 5 % puede ser degradable con payload íntegro) | Probar umbral permitido vs excedido en controles separados, con integridad de fallback; no fijar rechazo universal |
| **RS-05 / P2** | TR-018 se llama `G3/G5 math roundtrip` pero invoca únicamente protector y estrategia de render | El nombre puede sugerir cobertura de integración de daemons que no existe | Conservar invariante de bytes matemáticos y delimitar alcance; valorar renombre en B si conviene |
| **RS-06 / P1** | TR-011 inyecta fallos en **funciones reales parcheadas para simular crash**, sin apagar procesos, mientras TR-014 inyecta fallo de commit tras promoción | Un test de control de recuperación local no acredita crash isolation de Compose ni atomicidad global | Conservar invariantes de recuperación sin segundo envío/old lease; no promoverlos a evidencia de crash en varios procesos |
| **RS-07 / P0 conocido (fuera de esta tanda)** | [`TS-001` golden parser](PLAN_REMEDIACION_TESTS_PIPELINE.md#3-hallazgos-semilla-estáticos) y [`TS-002` chunk snapshot](PLAN_REMEDIACION_TESTS_PIPELINE.md#3-hallazgos-semilla-estáticos) presentan oráculos autorreferentes o autogenerados | «PASS» ficticio para un test que pretende comprobar pipeline o snapshot | Reparar en B-01/B-02 con **fixture técnica independiente**, nunca reabrir GT científico ni hacer rebaseline automático |

### Qué parece correctamente acotado, pero todavía NO está certificado

- **TR-001/TR-019:** el doble `os.link` solo simula la frontera negativa del filesystem; el positivo sí llama a la función de admisión real, usa PDF real sintético y comprueba bytes persistidos. Es un test de frontera legítimo **si pasa y falsifica la ausencia de atomicidad**.
- **TR-008/TR-011/TR-013/TR-014:** SQLite real y estado persistido constituyen oráculos más independientes que los contadores de mocks. Es necesario determinar qué consultas representan **contratos públicos durables** y cuáles son detalle de schema incidental.
- **TR-009:** el fake de aceptación/perdida está diseñado para responder correctamente a un **segundo POST prohibido**; el conteo de llamadas es **un efecto externo observable del fake** y, por tanto, apropiado para este contrato. No representa billing de un proveedor real.
- **TR-003:** el parser del composition root no es mockeado, y el vector no representable constituye un test técnico negativo legítimo. El PDF es sintético y no reemplaza la baseline científica.
- **TR-017:** múltiples raíces productivas y state SQLite real proporcionan evidencia de cableado; los reemplazos de parser/Tectonic/proveedor limitan sus afirmaciones, **no invalidan** la prueba de composición.

## 4. Propuestas de falsación por contrato (fase C, no ejecución presente)

Las siguientes son **hipótesis de mutación** destinadas a demostrar sensibilidad futura. No afirmar `mutation killed` hasta ejecución reproducible y revisión de causa de fallo.

| F-## | Infracción provocada en entorno descartable | TR protector candidato | Señal que debería fallar **por el contrato** | Efecto prohibido |
|---|---|---|---|---|
| F-01 | Inhabilitar validación de colisión/hash de PDF en inbox | TR-001/TR-019 | Error esperado deja de emitirse o bytes previamente publicados cambian | Sobrescritura de inbox |
| F-02 | Permitir AST para vector no representable en parser | TR-003 | Ya no surge `B02_UNREPRESENTED_VECTOR_DRAWING` | AST falso-completo |
| F-03 | Aceptar plan G3 con hash/generación ajena | TR-004/TR-005 | Se encola/persiste plan inconsistente o fake recibe pedido | Estado durable de otra generación |
| F-04 | Omitir fence de ejecución en staging | TR-006/TR-008 | Lease inválido genera recibo o `RESULT_STAGED` | Receipt de otro owner |
| F-05 | Permitir segundo envío tras respuesta perdida | TR-009/TR-010 | `accepted_calls` supera 1 o UNKNOWN vuelve a runnable | Doble efecto del proveedor fake |
| F-06 | Completar FSM pese a proyección tampered/receipt ausente | TR-011/TR-016 | FSM llega a READY_FOR_ASSEMBLY o contenido corrupto consumido | Publicar plan inválido |
| F-07 | Permitir promoción de PDF por lease viejo | TR-013/TR-014 | Archivo destino aparece o `COMPLETED` cambia con owner anterior | Stale PDF published |
| F-08 | Ignorar proyección faltante cuando se excede tolerancia | TR-015 | No se rechaza, o aparece PDF temporal/final | PDF incompleto presentado como válido |
| F-09 | Eliminar binding de snapshot de contexto | TR-005/TR-017 | Provider fake recibe contexto de otra generación | Inferencia con identidad cruzada |
| F-10 | Perder o mover delimitador de math entre segmentos | TR-007/TR-018 | Token alterado aceptado o render distinto del invariante | Corrupción matemática |

**No ejecutar mutaciones en la copia local del owner.** En C se requiere entorno realmente descartable, inyección controlada, caso de control conforme, resultado esperado, resultado observado, revert y diff de efectos no permitidos.

## 5. Matriz de cobertura inicial por frontera (solo lectura de código)

| Frontera de Atlas | TR testigo | Positivo escrito | Negativo escrito | Componentes productivos/no simulados | Cobertura no acreditada |
|---|---|---|---|---|---|
| CLI/inbox | 001, 002, 019 | Sí | Sí | API admisión + archivos reales sintéticos | Montajes efectivos Docker, OCR |
| Extracción física PDF→AST | 003 | Sí | Sí | Parser real root | OCR daemon junto con parser real |
| OCR→plan→FSM/queue | 004 | Sí | Sí | Daemon orquestador + queue real | Perfil/parser/FSM reales en el mismo caso |
| Contexto OCR/G3 | 005 | Sí | Sí | Plan/repo/bridge reales | OCR físico + provider real |
| G3 provider/staging | 006–008 | Sí | Sí | Bridge, staging, queue real | Ingreso a proveedor de red |
| W06 efecto incierto | 009–010 | Sí (respuesta confirmada en otro caso) | Sí | Engine, repo, bridge, fake de aceptación | Incertidumbre en HTTP externo real |
| G3 publish/recovery | 011–012 | Sí | Sí | Publicación y repositorios reales | Crash de proceso con varios servicios |
| G5 lease/publicación | 013–015 | Sí | Sí | Repo, FSM, worker real en negativo | Tectonic real/umbral degradado en PDF físico |
| Perfil/proyección/TeX | 016 | Sí | Sí | DB, resolver, CompilationService | PDF físico compilado por Tectonic |
| Foreground CLI→PDF | 017 | Sí | No en el mismo test | Roots CLI/OCR/G3/G5 + SQLite | Parser/provider/Tectonic reales |
| Matemática → render | 007, 018 | Sí | Sí | Protector/bridge/renderer real | Garantía semántica de traducción |

Una fila «Sí» significa **existe ese caso escrito**, no que haya pasado. La tabla **no** mezcla estos testigos con certificación científica, ni convierte tests legacy en garantías de G3.

## 6. Criterios de avance y seguimiento de A01-S5

- [x] **S5-P1 — Identificar primera tanda de 19 fichas** con archivo, función de prueba, SUT, doubles, aserciones y defecto esperado.
- [x] **S5-P2 — Registrar límites de pruebas de composición**, particularmente parser falso, provider fake y Tectonic fake.
- [x] **S5-P3 — Seleccionar controles negativos candidatos** para ejecución futura sin mutar ahora.
- [ ] **S5-P4 — Ampliar trazabilidad a todos los tests pertinentes de la ruta**, incluyendo `test_g3_b2_sqlite_plan_contract.py`, `test_w08_durable_context_boundary.py`, `test_g5_assembler_worker_integration.py`, `test_c3_t05_process_boundary.py`, `test_w08_inference_identity_contract.py`, `test_w08_cli_foreground_single_generation_offline.py` y restantes testigos del Atlas; evitar contar el mismo test como dos contratos sin explicitarlo.
- [ ] **S5-P5 — Auditar independencia del oráculo** para cada caso/fake relevante, distinguiendo modelo de datos esperado del resultado obtenido (A-03); buscar tolerancias/configuración acopladas y aserciones que deberían ser negativas.
- [ ] **S5-P6 — Conciliar los 1.159 nodeids sin marker de nivel con su SUT/ámbito** para no confundir carpeta con selección o declarar todo `not e2e` como ruta activa; los tests de tooling científico/legacy **se clasifican, no se evalúan**.
- [ ] **S5-P7 — Acordar categorías finales por contrato** (`confiable para su alcance` / `limitado` / `defectuoso` / `pendiente de verificar`), con evidencia de falsación en C. **No** elevar provisionalmente E-OBS a «confiable» por lectura.
- [ ] **A01-S5 / A-01 global completo:** **PENDIENTES**; no lanzar B o C en base solo a estas 19 fichas.
- [ ] **A05-P4/P6:** revisar efectos de imports/archivos ignorados/red/host; las cuatro colecciones previas exitosas no acreditan ausencia universal de efectos.

**Siguiente paso recomendado:** seguir A01-S5 sobre la segunda tanda de testigos activos y aislar un **mínimo de contratos normativos** por capa. El propósito es preservar tests válidos ante cambios profundos del pipeline y remediar únicamente falsas garantías o dependencias accidentales, sin adaptar arbitrariamente los expected al comportamiento nuevo.
