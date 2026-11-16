# A01-S5 — Matriz semántica de tests de la ruta técnica PDF→PDF

> **Programa:** TST-STAB; etapa **A01-S5 EN CURSO** (primera tanda dirigida de 19 fichas, no censo semántico total). **Segunda tanda:** [TR-020 a TR-035 y riesgos de refactor](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md). **35 fichas acumuladas por contrato/frontera**, no necesariamente 35 archivos únicos ni 35 casos independientes. **No se cierran A-01, A-02, A-03, A-04 ni A-05.**
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
- [ ] **S5-P4 — Ampliación en curso:** se revisaron los testigos `test_g3_b2_sqlite_plan_contract.py`, `test_w08_durable_context_boundary.py`, `test_g5_assembler_worker_integration.py`, `test_c3_t05_process_boundary.py`, `test_w08_inference_identity_contract.py` y otros once archivos, con [16 fichas adicionales TR-020…035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md). El foreground W08 estaba ya en TR-017; evitar duplicar la acreditación. **Falta cobertura exhaustiva por nodeid y clasificación de ámbito del resto**.
- [ ] **S5-P5 — Auditar independencia del oráculo** para cada caso/fake relevante, distinguiendo modelo de datos esperado del resultado obtenido (A-03); buscar tolerancias/configuración acopladas y aserciones que deberían ser negativas.
- [ ] **S5-P6 — Conciliar los 1.159 nodeids sin marker de nivel con su SUT/ámbito** para no confundir carpeta con selección o declarar todo `not e2e` como ruta activa; los tests de tooling científico/legacy **se clasifican, no se evalúan**.
- [ ] **S5-P7 — Acordar categorías finales por contrato** (`confiable para su alcance` / `limitado` / `defectuoso` / `pendiente de verificar`), con evidencia de falsación en C. **No** elevar provisionalmente E-OBS a «confiable» por lectura.
- [ ] **A01-S5 / A-01 global completo:** **PENDIENTES**; no lanzar B o C en base solo a estas 19 fichas.
- [ ] **A05-P4/P6:** revisar efectos de imports/archivos ignorados/red/host; las cuatro colecciones previas exitosas no acreditan ausencia universal de efectos.

**Siguiente paso recomendado:** con [35 fichas preliminares acumuladas](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md), ordenar la restante auditoría por **nodeids y contratos activos**, no por cantidad de archivos. Empezar independencia de oráculos sin cerrar A01-S5, y registrar las excepciones fuera de la ruta activa. Mantener tests válidos ante cambios profundos del pipeline y remediar sólo garantías falsas o acoplamientos accidentales, sin adaptar expected al nuevo comportamiento.

## 7. A-03/A-04 — clasificación de las 35 fichas por contrato, sin ampliar campañas (2026-11-16)

**Propósito:** completar la revisión de **independencia del oráculo, sustituciones del SUT y alcance real** de las **35 fichas TR ya abiertas**. Se aplican las categorías del [plan §5.2](PLAN_REMEDIACION_TESTS_PIPELINE.md): \`CONFIABLE_PARA_SU_ALCANCE\`, \`LIMITADO\`, \`DEFECTUOSO\`, \`DESCONOCIDO\`. **No es una clasificación de los 1.476 nodeids del censo previo ni una ejecución de suite en el HEAD actual.** Un TR agrupa contrato/testigos; la decisión focal vale **solo para el subconjunto probado**, y no certifica todos los casos que puedan existir en ese archivo.

**Fuentes:** [TR-001–019 §2](#2-matriz-de-primera-tanda--19-fichas-trazables), [TR-020–035 §2](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md), [A-02 ocho fronteras §9](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md), [P0 Golden/snapshot](A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md), [G3-B3 OI](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md) y evidencias de ejecución por SHA en el [plan §10.2](PLAN_REMEDIACION_TESTS_PIPELINE.md). Se contrastaron nuevamente fuentes actuales de TR-022, TR-027, TR-029, TR-032 y TR-035. **F = solamente código/oráculo inspeccionado**, **E = baseline positiva pertinente**, **K = mutación específica detectada**. La evidencia E/K se asigna **solo si existe un testigo de ese TR efectivamente ejecutado**; no se hereda por compartir frontera.

| TR | Dictamen provisional A-03/A-04 | Evidencia | Razón contractual o límite específico |
|---|---|---|---|
| **001** Admisión | **CONFIABLE_PARA_SU_ALCANCE**, para atomicidad y bytes | E/K | \`test_pdf_inbox_submission.py\` 8 PASS y mutación de fallback no atómico detectada; no OCR |
| **002** CLI R1 | **CONFIABLE_PARA_SU_ALCANCE**, para exclusión de R1 | E/K | Handler CLI real y mutación de invocación legacy detectada; no ejecución de stages |
| **003** Parser | **CONFIABLE_PARA_SU_ALCANCE**, para PDF sintético | E/K | Parser real, texto conocido independiente, rechazo de vector y detección de pérdida de frase; no GT |
| **004** OCR durable | **DESCONOCIDO** en ejecución focal | F | OCR Router con parser/registry y otros puertos falsos; contrato válido de queue, no OCR físico |
| **005** Contexto W08 | **DESCONOCIDO** en ejecución focal | F | Binding/persistencia observables por código; falta acreditar estos nodeids específicos |
| **006** Staging G3 | **DESCONOCIDO** en ejecución focal | F | Resultados staged y fencing con SQLite; sin evidencia directa nueva de sus nodeids |
| **007** Binding LLM | **DESCONOCIDO** en ejecución focal | F | Bridge con proveedor fake y parser de respuesta; no atribuir los 39 PASS de otro módulo a este TR |
| **008** Receipts fenced | **DESCONOCIDO** en ejecución focal | F | Rechazo/rollback por SQL temporal escritos; no ejecutados en la campaña focal presentada |
| **009** W06 UNKNOWN | **CONFIABLE_PARA_SU_ALCANCE**, para efecto offline incierto | E/K | Engine/SQLite reales; 9 PASS G3/G5 y segundo accepted call detectado por fake; no exactly-once HTTP |
| **010** W06 reconciler | **DESCONOCIDO** en ejecución focal | F | Método privado, liderazgo simulado y oráculos SQL; no mismo testigo que el reintento G3 K |
| **011** Publicación G3 | **LIMITADO**, con barrera corrupta acreditada | E/K parcial | Proyección alterada aceptada fue detectada; otros escenarios de crash/finalización no tienen todos E/K focal individual |
| **012** Reconciler fencing | **DESCONOCIDO** en ejecución focal | F | Leadership y flujo legacy parcial con mocks; no reclamar G3 end-to-end |
| **013** G5 lease | **CONFIABLE_PARA_SU_ALCANCE**, para lease expirado | E/K | SQLite/filesystem reales; mutante publica PDF prohibido y test lo detecta, no Tectonic |
| **014** G5 crash/promotion | **DESCONOCIDO** en ejecución focal | F | Fallos de \`os.replace\`/commit simulados; no extraer PASS del TR-013 por compartir módulo |
| **015** G5 proyección ausente | **DESCONOCIDO** en ejecución focal | F | Worker/repositorio reales con fuentes externas fake; contrato de ausencia, no todas las degradaciones |
| **016** G5 perfil/proyección | **DESCONOCIDO** en ejecución focal | F | SQLite, resolver y TeX; sin compilación de PDF real |
| **017** Foreground compuesto | **LIMITADO** | F | CLI/OCR/G3/G5 compuestos con parser, proveedor y renderer sustituidos; no E2E físico integral |
| **018** Math roundtrip | **LIMITADO** | F | Solo protector/renderer, no daemons G3/G5 pese al nombre del archivo; no calidad lingüística |
| **019** Sin efectos de admisión | **CONFIABLE_PARA_SU_ALCANCE**, mismo testigo de 001 | E/K **compartida** | Colisión, vacío, no fallback; **no sumar de nuevo** la mutación del TR-001 |
| **020** Plan SQLite | **DESCONOCIDO** en ejecución focal | F | Idempotencia/conflicto con base temporal; sensibilidad y ejecución específica pendientes |
| **021** Snapshot W08 | **DESCONOCIDO** en ejecución focal | F | Plan/contexto persisted y tampered; no adjudicar K de manifest de otro SUT |
| **022** Worker G5 | **CONFIABLE_PARA_SU_ALCANCE**, método real con dobles | E/K | 3 PASS y dos K de publicación expirado/fallo no persistido; sigue **P1 fragilidad** por \`__new__\` y fixture cruzada |
| **023** Crash G3 entre procesos | **LIMITADO**, baseline real positiva | E | Hijo \`os._exit(73)\`, recovery SQLite y tercer lector verifican persistencia; no mutation kill propio ni daemon completo |
| **024** Identidad de reuso | **DESCONOCIDO** en ejecución focal | F | Hash/JSON y rechazo escritos; no comprobar el replay productivo completo |
| **025** Cuota SQLite/thread | **DESCONOCIDO** en ejecución focal | F | Puente y SQL en threads reales con proveedor fake; sin gasto/red real |
| **026** PRESERVE | **DESCONOCIDO** en ejecución focal | F | Engine real con proveedor vigilado; no adjudicar otra prueba W06 a este test |
| **027** Roots R1/R3 | **LIMITADO** | F | Solo análisis AST/textual del launcher; conteos de statements/handlers son frágiles ante refactor |
| **028** Chunk identity | **DESCONOCIDO** en ejecución focal | F | Member/source/manifest en test técnico, pero B-02 K pertenece a otro archivo/testigo |
| **029** WAL write scope | **LIMITADO** | F | Aserta método privado, locking y tiempos de threads; riesgo de fragilidad P1, no defecto probado |
| **030** Queue LLM/ASSEMBLER | **DESCONOCIDO** en ejecución focal | F | Demultiplexado y estados SQL escritos, sin daemons reales en el mismo test |
| **031** Coordinator foreground | **LIMITADO**, dos rechazos acreditados | E/K parcial | Dos pruebas G3 incompleto/PDF ausente con coordinator real y **stages completamente fake**; no E2E |
| **032** Barrera cache W08 | **LIMITADO** | F | \`cache_db_path=None\` y factory privado; prueba el opt-out, no replay versionado |
| **033** G3 materialized | **DESCONOCIDO** en ejecución focal | F | Publicación/verificación por repo con SQL real; C-04 K protege otro testigo de misma frontera |
| **034** Finalización G3 | **DESCONOCIDO** en ejecución focal | F | CAS/commit/rollback escritos; no trasladar PASS del test de avance G3 |
| **035** FSM/queue legacy | **LIMITADO** | F | SQLite temporal y handoff acotado; docstring del test refiere a una falla en SHA histórico, no evidencia del HEAD |

**Balance de 35 fichas por contrato:** \`CONFIABLE_PARA_SU_ALCANCE\` **7** (solo el subcontrato focal declarado), \`LIMITADO\` **9**, \`DESCONOCIDO\` **19**, \`DEFECTUOSO\` **0 confirmados en estas fichas por la revisión presente**. **No significa que no existan defectos en los 19 desconocidos**, ni que el contrato completo de cada TR confiable esté cubierto. Los **P0 TS-001/TS-002** confirmados históricamente eran tests distintos: sus **reemplazos técnicos B-01/B-02** y controles negativos están documentados en el expediente A-03; no confundir la etiqueta \`DEFECTUOSO=0\` de esta tabla de TR con inexistencia de falsos oráculos históricos.

### A-03: diagnóstico de independencia y acciones justificadas (sin nuevos testigos)

| Hallazgo | Estado actual y acción mínima |
|---|---|
| **P0 TS-001** expected circular / parser mockeado | **REMEDIADO focalmente**: B-01 usa texto conocido en PDF efímero, parser real; control de pérdida de texto reportado K. No llamar a esta fixture GT científico |
| **P0 TS-002** snapshot self-writing / omisión de miembros | **REMEDIADO focalmente**: B-02 coteja fuentes/miembros y rechaza alteraciones, sin regenerar oráculo en pytest; mutante de pérdida de bytes reportado K |
| **G3-B3 OI-04** límite UTF-8 solo ASCII | **REMEDIADO**: nuevo test multibyte y mutación detectada en \`83f99ddb\` |
| **G3-B3 OI-01/OI-02/OI-03/OI-05** plan compartido, cardinalidad de chunker, regex parcial, all-or-nothing puro | **LIMITACIONES DOCUMENTADAS**: independencia no total en todos los inputs; algunos asserts podrían ser frágiles ante refactor y el parser puro no prueba commits/red. No alterar esperados sin contrato violado; los testigos de persistencia/bridge son complementarios, no sustitutos |
| **P1 de alcance/refactor** TR-017/018/022/027/029/031/032/035 | **LIMITADO o condicionado** por mocks legítimos, \`__new__\`, helper privado, matching textual o nomenclatura. No reescribir por estética; abrir corrección B únicamente ante falsa garantía comprobada o rotura real de contrato |
| **Seguridad A-05 / CI / censo** | **ABIERTOS**: hay solo inventarios focales Git en clones; no egress físico/aislamiento OS, no suite técnica completa, no required CI sobre HEAD; el censo \`1476\` pertenece a \`5447963d\` antes del test extra de G3-B3 |

**Decisión A-03/A-04:** se completó **clasificación provisional de 35/35 fichas TR existentes por contrato** sin inventar evidencia. **No se cierra A-03/A-04 global** porque A-04 requiere clasificar cada nodeid pertinente, y el [puente A01-S5](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md) informó **277 nodeids en 29 archivos con TR vs. 1.197 sin TR** sobre el SHA histórico; los datos del HEAD nuevo no se sustituyen automáticamente. La prioridad siguiente **dentro del plan** es resolver alcance del inventario relevante y ficha de brechas A-07 usando lo ya inspeccionado, no más mutaciones o infraestructura. Las excepciones y riesgos se deben llevar a revisión formal del owner.

## 8. A-04 — delimitación del denominador de nodeids sin ficha TR (2026-11-16)

**Progreso del gate A-04; no cierre.** La clasificación de **35 fichas TR** en §7 concierne a contratos, no a todos los ítems de pytest. Para delimitar el trabajo restante **sin inventar cobertura**, se cotejó el [puente A01-S5 histórico](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md) con sus **8 fuentes sin TR ya inspeccionadas**, la [conciliación posterior A01/A04](A01_A04_RECONCILIACION_HEAD_2026-11-16.md) y lecturas directas de fuentes actuales en GitHub. Mantener separados los SHA; **no extrapolar los conteos de 2026-11-15 al HEAD de hoy**.

### 8.1 Partición exacta del inventario **histórico** de 1.474 nodeids

| Grupo mutuamente excluyente por archivo (SHA histórico \`86cd6867\`) | Archivos con nodos | Nodeids | Decisión de alcance A-04 |
|---|---:|---:|---|
| Archivos **vinculados por ruta** a una o más fichas TR-001–035 | **29** | **277** | Testigos candidatos de la ruta; **vínculo de archivo, NO 277 oráculos auditados por nodeid**. Dentro de estas 29 fuentes existen también casos de alcance legacy/compartido. Ver clasificación **por contrato** en §7 |
| **G3-B3 estructurado** sin ficha TR: \`test_g3_b3_structured_result_contract.py\` | **1** | **33** | **ACTIVA — G3**. Los **33 nodeids históricos** tienen auditoría granular [B3-01…33](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md); el test multibyte posterior agregó **un** caso, validado en otra ejecución. No atribuir C/E/K uniforme a cada escenario |
| **Técnica compartida**, sin ficha TR: AST, math normalizer, TeX render | **3** | **76** | **PERTINENTE DE APOYO**, no prueba de ensamblado físico: \`test_ast_models.py\` **28**; \`test_math_normalizer.py\` **30**; \`test_text_render_strategy.py\` **18** |
| **Ciencia / corpus / veredicto**, sin ficha TR | **3** | **97** | **DIFERIR D-5** para remediación científica, preservando tests/selección: \`test_criticality_verdict.py\` **40**, \`test_corpus_models.py\` **30**, \`test_verification_outcome.py\` **27** |
| **Gobernanza de workflow CV**, sin ficha TR | **1** | **30** | **CI/CV-administración**, no test de la ruta operativa: \`test_cv_workflow_contract.py\` **30**. Usa \`pytest.importorskip("yaml")\`; colección ≠ CV ejecutado |
| **Sin ámbito de SUT revisado en ese puente** | **136** | **961** | **DESCONOCIDO / PENDIENTE**: puede contener ruta activa, legacy, utilidades o ciencia. No llamarlos 961 defectos ni 961 tests prescindibles |
| **TOTAL** | **173** | **1.474** | **29+1+3+3+1+136=173**; **277+33+76+97+30+961=1.474** |

**Control cruzado:** los cuatro subgrupos con alcance conocido fuera de TR suman **8 archivos, 236 nodeids** (33+76+97+30). Con los 136 archivos no estudiados suman **144 archivos/1.197 nodeids**, exactamente la partición del [puente A01-S5](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md). La clasificación anterior es **por archivo y SUT observado**, salvo los 33 nodeids del expediente granular G3-B3. No elevar los 76+97+30 a «tests revisados uno por uno». Tampoco deduplicar o sumar marcas \`unit\`/\`integration\`: no constituyen una partición.

**Cambio de SHA:** la recolección posterior del owner dio **1.476** nodeids en \`5447963d\`, con 14 identidades retiradas, 16 añadidas y 1.460 compartidas; **no** se ha ejecutado aquí una segunda clasificación por archivo a ese SHA. Después se añadió un test UTF-8 G3-B3 al HEAD. No usar la resta histórica para declarar un nuevo censo de \`961\` ni un total actualizado sin JSON de colección del nuevo SHA.

### 8.2 Cinco fuentes adicionales sin TR: lectura directa del HEAD actual (sin ejecución)

Las cinco fuentes siguientes pertenecen a los **136 archivos no clasificados en el puente histórico**. Se leyeron en \`tests_stabilization\` para determinar **prioridad de clasificación**, sin conocer aquí el número exacto de nodeids recolectados por cada una. Por tanto **no se restan números a los 961** ni se cambian los totales históricos.

| Archivo | Categoría provisional A-04 | SUT y oráculo comprobados por fuente | Límite / decisión concreta |
|---|---|---|---|
| \`tests/integration/test_pymupdf_extraction_integrity.py\` | **ACTIVA / B02** | \`PyMuPDFProvider.extract\`, \`HeuristicLayoutClassifier\`; PDF temporal real, bloque de texto/asset de imagen y rechazo \`B02_UNREPRESENTED_VECTOR_DRAWING\` | Alto valor para parser/layout; no OCR→G5 ni PDF traducido final. No añadir nuevos tests sin defecto acreditado |
| \`tests/integration/test_b023_raster_image_pipeline.py\` | **ACTIVA / B02→G5 assets** | Parser real, \`ChunkPlan\`, rutas \`PRESERVE\`, mapper, \`stage_image_assets\`; comprueba bytes PNG y hash de asset, reutilización y rechazo vectorial | Camino técnico visual parcialmente compuesto; respuestas de texto sintéticas, sin proveedor ni Tectonic |
| \`tests/integration/test_b025_math_visual_preservation.py\` | **ACTIVA / B02→G5 assets** | PDF efímero con fuente visual, \`build_extraction_pipeline\`, \`ChunkPlan\`, \`PRESERVE\`, \`stage_image_assets\` y error \`B025_MATH_VISUAL_DISABLED\` | Contrato **visual**: no fidelidad de significado matemático, maquetación ni PDF final; no fingir CV |
| \`tests/integration/test_cli_router.py\` | **LIMITADO / CLI dispatch** | \`apps.cli.main.main\` real, pero \`parse_arguments\` y cada handler sustituidos por mocks; exige delegación nominal | No ejecuta admisión/foreground; además añade globalmente al \`sys.path\` en import. Fragilidad de refactor, **no P0 demostrado** |
| \`tests/integration/test_recovery_flow.py\` | **LEGACY / NO CONTAR COMO RUTA ACTIVA** | \`AbandonedProcessWatchdog\`, \`OnDemandResumeManager\` y FSM reales; \`TranslationPipeline.execute\` *mockeado*, con estado \`COMPLETED\` creado por el propio doble | **Corrección frente a informe antiguo IO-06:** el **HEAD actual usa \`tempfile.TemporaryDirectory\` y \`addClassCleanup\`** para su SQLite, no el borrado de DB fija previamente documentado. El oráculo de culminación de pipeline sigue siendo **legacy simulado**. Sin auditoría exhaustiva de imports/efectos OS |

**Decisión de prioridad de A-04:** trabajar primero con rutas de producción/contratos **activos** de los archivos pendientes, luego tests técnicos compartidos, y separar **legacy** de **benchmark/ciencia/CV** aunque sean seleccionables por \`pytest -m "not e2e"\`. Para cada futuro archivo anotaremos **ruta→SUT real→oráculo→mocks→selección→categoría y número de nodeids cuando exista JSON**, no fichas redundantes por cada parametrización idéntica. Esta clasificación se puede hacer por lectura; **no requiere más scripts, nuevas mutaciones, Docker ni reejecución de la suite**.

**Gates:** A-04 **AVANCE PARCIAL, ABIERTA**: ocho archivos (236 nodeids históricos) clasificados por *familia* y cinco fuentes adicionales clasificadas por lectura de HEAD, más 35 fichas TR revisadas por contrato (§7). La inmensa mayoría de los 961 nodeids históricos del grupo restante **aún no tiene clasificación por SUT ni prioridad individual verificadas**. El P0 de falso test parser y el de snapshot fueron remediados; los cinco archivos nuevos **no presentan otro defecto P0 confirmado** en la lectura acotada. No sustituir la revisión A-05/CI por estos hallazgos estáticos.

## 9. A-04 — segunda tanda de clasificación por fuente: contratos activos, auxiliares y legacy (2026-11-16)

**Método y límite:** lectura directa en \`tests_stabilization\` de **26 archivos adicionales con tests** no incluidos entre las 35 fichas TR ni los 13 archivos sin TR ya inspeccionados en §8, más **cuatro archivos raíz sin test pytest ordinario**. Se contrastaron importaciones, método productivo realmente llamado, oráculos, mocks y escrituras/condiciones de SKIP. Esto **no** ejecuta pytest/Pyright ni acredita PASS/FAIL/SKIP efectivos. **No** se tienen aquí los JSON \`all.json\` de esos archivos para atribuir cantidades de nodeids exactos. Se mantiene **sin cambio** el denominador del inventario histórico: \`961\` nodeids/136 archivos entonces pendientes; no restar esta tanda de esa cifra sin cruzar los nodeids de la colección congelada.

### 9.1 Ruta activa o apoyo técnico directo: 10 archivos

| Archivo \`tests/\` (ruta relativa) | SUT / oráculo escrito | Estado por alcance y reserva |
|---|---|---|
| \`integration/test_g3_b1_policy_guardrails.py\` | \`TokenBudgetChunker\` y \`ChunkPlan.build\`; rechaza incompatibilidades \`TRANSLATE/PRESERVE/PARTIAL\` y verifica concatenación de bytes de fuente | **ACTIVA G3 / REVISADO ESTÁTICAMENTE**. Unitarios de política, no entrega de proveedor |
| \`integration/test_pdf_pdf_fsm_transaction_ownership.py\` | \`FSMRepository\` SQLite \`tmp_path\`; verifica transacción del caller abierta, rollback externo y CAS fallido sin perder trabajo ajeno | **ACTIVA G2 / OBSERVACIÓN IMPORTANTE:** su docstring dice explícitamente que el candidato G2 **puede fallar**. **NO hay PASS acreditado** ni contrato de atomicidad entre bases; priorizar evidencia de CI/ejecución para A-07, no cambiar runtime por anticipado |
| \`integration/test_pdf_pdf_sqlite_g2_guardrails.py\` | \`FSMRepository\`, \`ControlPlaneRepository\`, alias SQLite y CAS; estado durable al reabrir, alias errado/DB ausente rechazados | **ACTIVA G2 / ESTÁTICO**. Siete casos escritos, \`tmp_path\`, sin certificar transacción cross-DB |
| \`integration/test_b022_image_staging.py\` | \`stage_image_assets\`, \`HostTectonicRunner.compile\`, PNG con digest, missing/tamper rechazados | **ACTIVA B02/G5 / LIMITADO:** \`subprocess.run\` está simulado; el fake crea un archivo con cabecera \`%PDF\`, **no Tectonic real** |
| \`unit/test_b022_image_rendering.py\` | \`AdaptiveFloatStrategy\`, \`canonical_image_name\`, escaping de \`\\includegraphics\` y referencias canónicas | **APOYO ACTIVO DE RENDER / ESTÁTICO**. String TeX, no PDF compilado |
| \`unit/test_b023_raster_asset_contract.py\` | \`persist_png_asset\`, \`validate_pymupdf_page_coverage\`, \`ChunkPlan\`; idempotencia, SHA, overwrite, symlink y vector rechazados | **APOYO ACTIVO B02 / ESTÁTICO**, \`tmp_path\`. **Un caso hace \`pytest.skip\` si Windows deniega symlinks**: la recolección no certifica esa rama |
| \`unit/test_b024_explicit_math_spans.py\` | \`find_explicit_math_spans\` y \`InlineMathProtector\`, literal exacto y rechazo de fuentes ambiguas | **APOYO ACTIVO DE PRESERVACIÓN / ESTÁTICO**, no corrección matemática científica |
| \`unit/test_b025_math_visual.py\` | \`classify_math_font_block\` y \`render_math_visual_png\`, fuente visual, crop PNG y bbox inválida | **APOYO ACTIVO B02 / ESTÁTICO**, no semántica de fórmula ni Tectonic |
| \`unit/test_semantic_chunker.py\` | \`build_semantic_chunks_as_units\`; reconstrucción normalizada, determinismo, separación de contextos | **APOYO ACTIVO G3 / LIMITADO:** el comparador **normaliza/descarta whitespace**; no acreditar preservación byte-exacta con este test (esa barrera tiene otros testigos B-02) |
| \`unit/test_pipeline_factory.py\` | \`ExtractionProviderFactory.create\`; provider PyMuPDF válido y rechazo de ID desconocido | **APOYO ACTIVO B02 / ESTÁTICO**; no procesa PDF. **Comprobado:** importa \`pytest\` dentro de la función negativa; no imputar error de importación inexistente |

### 9.2 Contratos técnicos auxiliares / capacidad parcial: 8 archivos

| Archivo relativo a \`tests/\` | SUT y oráculo | Decisión A-04 |
|---|---|---|
| \`integration/test_healing_concurrency.py\` | \`HealingTelemetryRegistry\` 50.000 eventos async; \`HealingPipeline\` con \`ValidationPipeline\` controlada y rollback | **TÉCNICA AUXILIAR / ESTÁTICO**, no demuestra concurrencia entre procesos ni PDF físico |
| \`integration/test_validation_integration.py\` | \`AsyncDispatcher\` real, provider/resolver fakes, \`ValidationPipeline\`; HARD_FAIL/WARNING | **LEGACY / ALCANCE LIMITADO**: no es el bridge G3 operativo ni publica PDF |
| \`smoke/test_invariants_smoke.py\` | \`reliability_pipeline\` inyectada por fixture, \`ValidationContext\`; familias SI/PI/PeI/SeI/VI por entrada literal | **TÉCNICA COMPARTIDA / ESTÁTICO**; un \`smoke\` nombrado no prueba la ruta física; requiere fixture para atribuir composición exacta |
| \`test_architecture_contract.py\` | Protocolos \`Control/Event/MaterializedPlanePort\` y scanner AST que prohíbe \`ASTNode(**kwargs)\` | **GOBERNANZA ARQUITECTÓNICA / LIMITADO**: excepción \`SyntaxError/UnicodeDecodeError\` omitida en scanner; no tomarlo como prueba de parseabilidad total |
| \`test_math_protector.py\` | \`InlineMathProtector.mask/restore\`, siete literales de roundtrip | **TÉCNICA COMPARTIDA / LIMITADO**: \`expected\` copia entrada, útil para roundtrip, no calidad de traducción. Modifica \`sys.path\` en import |
| \`unit/test_tectonic_runner.py\` | \`HostTectonicRunner.compile\` con \`subprocess.run\` simulado: éxito, error, timeout, cwd privado | **APOYO G5 / LIMITADO + RIESGO A-05**: \`test_no_crash_log_written_to_cwd\` **borra** \`tectonic_crash.log\` si existe en el CWD antes y después de probar. **No ejecutar en el working tree del owner**; el test no lanza Tectonic real |
| \`unit/test_execution_context_boundaries.py\` | Módulos/puertos de seis contextos importables; escaneo AST de dependencias para evitar god-object | **GOBERNANZA ARQUITECTÓNICA / ESTÁTICO**, no ejecución de la ruta soportada |
| \`unit/test_routing.py\` | \`TranslationStrategyRouter\` y \`ProviderStrategy\`, tabla de rutas \`GROQ_*\` y rechazos | **TÉCNICA DE RUTEO / ALCANCE NO VINCULADO**: falta probar que ese router es consumidor del G3 \`SyncProviderBridge\` activo; no atribuirlo al root |

### 9.3 Legacy y ciencia/gobernanza, con riesgos comprobables por lectura: 8 archivos

| Archivo relativo a \`tests/\` | Evidencia del cuerpo/Setup | Dictamen A-04 |
|---|---|---|
| \`integration/test_translation_semantics.py\` | \`TranslationPipeline\` legacy; \`parser.parse\` parcheado, falta de \`tests/golden/*.semantics.json\` produce \`skipTest\`; **\`_mock_embed_text\` devuelve \`[0.5]*10\` para cualquier texto** y el coseno entre ambos vectores no nulos siempre es 1 | **LEGACY / FALSA GARANTÍA SEMÁNTICA POTENCIAL CONFIRMADA POR FUENTE**: el umbral de similitud no discrimina traducciones correctas/incorrectas. **No es verificación científica real ni P0 nuevo de ruta activa**. No modificar GT para forzar el caso |
| \`integration/test_translation_structure.py\` | Pipeline/dispatcher legacy; \`skipTest\` si golden no existe o si \`result.document\` es \`None\` | **LEGACY / SKIP PUEDE OCULTAR FALTA DE GARANTÍA**. Su \`setUp\` conecta a **\`infra/db/documents.db\`** antes de evaluar el SKIP: riesgo de crear/tocar DB de ruta fija (**A-05**) |
| \`integration/test_translation_technical.py\` | Como el anterior; compara tokens/ecuaciones solo si existe golden y documento compilado | **LEGACY / SKIP PUEDE OCULTAR FALTA DE GARANTÍA**. Mismo \`get_connection("infra/db/documents.db")\` en \`setUp\`; no ejecutar en checkout del owner |
| \`integration/test_translation_layer.py\` | \`AsyncDispatcher\`, \`DocumentAssembler\`, provider fake; cache SQLite en \`tests/fixtures/integration_cache_<uuid>.db\` y \`asyncTearDown\` borra \`-wal\`/\`-shm\` | **LEGACY / AISLAMIENTO A-05 PENDIENTE**: escribe y borra bajo \`tests/fixtures\` del CWD; no acredita el ensamblado G5 activo |
| \`integration/test_parameter_freeze.py\` | \`tools.evaluation.freeze_parameters.main\`, artefactos nuevos en \`tmp_path\`; caso \`REAL_FREEZE=reports/calibration/parameter_freeze.json\` hace \`skipif\` cuando falta | **CIENCIA/CV/TOOLING — DIFERIR D-5**. Condición de skip es dato de selección, no certificación del freeze |
| \`unit/test_manifest_fingerprint.py\` | \`core.benchmark.corpus.services\`; hash/oracle de manifiesto GT | **CIENCIA/CORPUS — DIFERIR D-5**, no \`ChunkPlan\` de G3 (coincidencia del término «manifest») |
| \`unit/test_identity_chain.py\` | \`core.benchmark.verification.identity_chain\`, perfiles, ejecución y resultado científico | **CIENCIA/CV — DIFERIR D-5**, no identidad de ejecución G3 ni lease G5 |
| \`unit/test_state_projection.py\` | \`core.pipeline.job.PipelineStep → core.execution.state.DocumentState\`, enum y mapping congelado | **LEGACY/TRANSVERSAL — LIMITADO**: no es prueba de transición SQLite/FSM del root activo; mantener como compatibilidad contractual |

### 9.4 Archivos raíz que no corresponden a nodeids ordinarios

Se verificaron directamente \`tests/test_ast.py\`, \`tests/test_dag.py\` y \`tests/test_fencing.py\`: **archivos vacíos**. \`tests/test_pipeline.py\` contiene **\`run_stress_tests()\` + \`if __name__ == "__main__"\`**, pero ningún \`test_*\`; no pertenece a la colección pytest como test. **No ejecutar manualmente** \`test_pipeline.py\` en el working tree: cuando se invoca explícitamente, crea \`tests/corpus\`, \`tests/output\` y escribe \`tests/stress_report.json\`.

### 9.5 Decisión operativa, sin sobreingeniería

1. **A-04:** estas **26 fuentes adicionales** quedan clasificadas **por archivo y SUT**, NO por número exacto de nodeids ni como PASS. Sumadas a las **cinco fuentes** de §8.2, hay **31 fuentes sin ficha TR inspeccionadas explícitamente** fuera del bloque de ocho con alcance histórico; la distribución histórica **1.474/277/236/961** sigue sin cambios hasta cruzar JSON por ruta.
2. **Hallazgos prioritarios a A-05/A-07 (no corregir durante esta clasificación):** borrado directo de \`tectonic_crash.log\` del CWD; conexiones a \`infra/db/documents.db\` en dos setups legacy; SQLite bajo \`tests/fixtures\` en translation layer; falso oráculo de similitud constante y SKIPs de supuesta certificación legacy; test G2 de propiedad transaccional que declara posible fallo **no ejecutado**. Son **riesgos sustentados por lectura**, no evidencia de que hayan ocurrido o de fallos productivos.
3. **Sin ejecutar tests, sin crear nuevos scripts, mutantes, CI jobs ni GT**. Mantener en abierto A-04 global, A-05/A-06 y A-07, y no iniciar D-4/D-5. El siguiente avance debe ser una **matriz de decisión A-04 de los nodeids pertinentes**, basada en su lista real de colección cuando esté disponible, evitando revisar ciencia irrelevante por inercia.

**Resumen estricto:** los tests activos y técnicos de esta tanda tienen oráculos plausibles y limitaciones delimitadas; los riesgos graves de efectos persistentes y falsa certificación corresponden principalmente a tests de infraestructura/legacy, y **no justifican desviarse ahora a construir más pruebas**.

## 10. A-04 — conciliación del alcance de los 105 archivos restantes (2026-11-16)

**Resultado de esta tanda:** se leyeron las importaciones, los tests declarados, las dependencias y los fragmentos pertinentes de las **105 fuentes de tests no incluidas en TR ni §§8–9**, todas presentes en el árbol `tests_stabilization` de partida `b8a669f95eaacf271bc74c24200b0523aa32c1c1`. En testigos de alcance delicado se contrastaron además cuerpos y condiciones de `skip`. Es una **clasificación por archivo/SUT**, **no** una revisión exhaustiva de todos sus nodeids, asserts o side effects. **No se ejecutaron tests, Docker, red, CI ni mutantes.**

### 10.1 Partición exacta por ruta de archivo

| Grupo sin solapamientos | Archivos | Regla de interpretación |
|---|---:|---|
| Ruta operativa o componentes compartidos | **36** | Protegen SUT activos o reglas de dominio reutilizables; **no se presupone el cableado de todos ellos al root G3/G5**. Contiene testigos acotados, fakes de red y un `e2e` opt-in |
| Legacy/compatibilidad | **9** | `AsyncDispatcher`, caché R1, `TranslationPipeline` legado o auditoría/metrics; no usarlos como evidencia de la ruta actual |
| Laboratorio offline / preflight | **4** | Fakes, argumentos de Docker y topología C0; se inspeccionan **sin levantar Docker** ni afirmar laboratorio D-4 |
| Ciencia/benchmark/GT/CV y herramientas de evaluación | **56** | Separar de la ruta operativa para **decisiones de remediación**, **sin eliminarlos ni excluirlos automáticamente del selector CI** |
| **TOTAL** | **105** | Rutas distintas, presentes en Git y asignadas a una sola familia |

La lista de fuentes que respalda cada grupo es explícita; los nombres se refieren al árbol del SHA citado. **Ninguna de estas cifras expresa nodeids**, ni permite restar cantidades del saldo histórico de 961.

**Ruta operativa o componentes técnicos compartidos — 36 archivos:**
- integration: `tests/integration/test_chunker_snapshot.py`, `tests/integration/test_golden_parser.py`, `tests/integration/test_healing_e2e_telemetry.py`, `tests/integration/test_real_paper.py`, `tests/integration/test_real_parser_pipeline.py`.
- unit: `tests/unit/test_adapters.py`, `tests/unit/test_assembler.py`, `tests/unit/test_asset_placeholder.py`, `tests/unit/test_ast_integrity.py`, `tests/unit/test_b0324_foreground_app_root.py`, `tests/unit/test_backpressure_mechanism.py`, `tests/unit/test_cancellation_mechanism.py`, `tests/unit/test_context_enricher.py`, `tests/unit/test_context_resolver.py`, `tests/unit/test_coordinated_shutdown.py`, `tests/unit/test_docling_provider.py`, `tests/unit/test_dynamic_context_resolver_live_update.py`, `tests/unit/test_healing_idempotency.py`, `tests/unit/test_healing_multi_failure_transaction.py`, `tests/unit/test_layout_validator.py`, `tests/unit/test_operational_visibility.py`, `tests/unit/test_paragraph_idempotency.py`, `tests/unit/test_perimeter_validator.py`, `tests/unit/test_preservation_validator.py`, `tests/unit/test_pricing_engine.py`, `tests/unit/test_prompt_builder.py`, `tests/unit/test_pymupdf_integrity.py`, `tests/unit/test_rate_limiter.py`, `tests/unit/test_resilient_provider.py`, `tests/unit/test_semantic_classification.py`, `tests/unit/test_semantic_classifier.py`, `tests/unit/test_semantic_validator.py`, `tests/unit/test_structural_healing.py`, `tests/unit/test_structural_validator.py`, `tests/unit/test_validation_pipeline.py`.
- root: `tests/test_pipeline_fidelity.py`.

**Legacy/compatibilidad (no root G3/G5) — 9 archivos:**
- integration: `tests/integration/test_e2e_walking_skeleton.py`, `tests/integration/test_embedding_smoke.py`, `tests/integration/test_pipeline_orchestration.py`, `tests/integration/test_real_e2e.py`.
- unit: `tests/unit/test_cache_provider.py`, `tests/unit/test_dispatcher.py`, `tests/unit/test_dispatcher_validation.py`, `tests/unit/test_pipeline_fsm_emission.py`, `tests/unit/test_summary_builder.py`.

**Laboratorio offline / preflight (sin ejecutar) — 4 archivos:**
- unit: `tests/unit/test_b031_g3_reusable_fake.py`, `tests/unit/test_b032_offline_pdf_lab.py`, `tests/unit/test_convergence_compose_preflight.py`, `tests/unit/test_convergence_db_bootstrap.py`.

**Ciencia, corpus, benchmark, CV y tooling de evaluación — 56 archivos:**
- integration: `tests/integration/test_add_document_to_corpus.py`, `tests/integration/test_baseline_gt_preconditions.py`, `tests/integration/test_baseline_integrity_exit_code.py`, `tests/integration/test_baseline_materialization.py`, `tests/integration/test_baseline_physical_integrity.py`, `tests/integration/test_benchmark_orchestration_integration.py`, `tests/integration/test_canonicalize_gt_hardening.py`, `tests/integration/test_curate_gt.py`, `tests/integration/test_cv_failure_path.py`, `tests/integration/test_cv_profile_validation.py`, `tests/integration/test_cv_regression_path.py`, `tests/integration/test_cv_report_persistence.py`, `tests/integration/test_execution_failure_exit_code.py`, `tests/integration/test_freeze_gt_curation_gate.py`, `tests/integration/test_regression_entry_point.py`.
- unit: `tests/unit/test_baseline_integrity.py`, `tests/unit/test_baseline_integrity_semantics.py`, `tests/unit/test_baseline_pdf_completeness.py`, `tests/unit/test_certification_boundary.py`, `tests/unit/test_certification_evidence.py`, `tests/unit/test_certification_preflight.py`, `tests/unit/test_configuration_fingerprint.py`, `tests/unit/test_corpus_port_asymmetry.py`, `tests/unit/test_criticality_costs.py`, `tests/unit/test_criticality_policy.py`, `tests/unit/test_enforcement_contract.py`, `tests/unit/test_execution_metadata.py`, `tests/unit/test_exit_codes_and_guard.py`, `tests/unit/test_framing_injectivity.py`, `tests/unit/test_ground_truth_completeness.py`, `tests/unit/test_ground_truth_lifecycle.py`, `tests/unit/test_ground_truth_models.py`, `tests/unit/test_ground_truth_ports.py`, `tests/unit/test_ground_truth_sealed_protection.py`, `tests/unit/test_ground_truth_sealing_atomicity.py`, `tests/unit/test_ground_truth_validity.py`, `tests/unit/test_idempotency_replacement.py`, `tests/unit/test_leaderboard_service.py`, `tests/unit/test_oracle_identity.py`, `tests/unit/test_provenance_identities.py`, `tests/unit/test_recovery_determinability.py`, `tests/unit/test_regression_adapter.py`, `tests/unit/test_regression_aggregation.py`, `tests/unit/test_regression_mechanism.py`, `tests/unit/test_regression_models.py`, `tests/unit/test_regression_report.py`, `tests/unit/test_regression_strategy.py`, `tests/unit/test_sanitize_ground_truth_types.py`, `tests/unit/test_score_policy.py`, `tests/unit/test_structural_metric.py`, `tests/unit/test_subject_identity.py`, `tests/unit/test_tooling_determinism.py`, `tests/unit/test_verification_boundary.py`, `tests/unit/test_verification_profiles.py`, `tests/unit/test_verification_report.py`, `tests/unit/test_zhang_shasha.py`.

### 10.2 Casos frontera y riesgos: decisiones sin pruebas nuevas

- **`test_real_paper.py`:** test **marcado `e2e` y opt-in**. Su `setUp` **falla** si no se proporciona `TEST_REAL_PDF_PATH` o si el archivo no existe; llama al parser real, no a G3/G5/Tectonic. Clasificar como **extracción real condicionada**, sin presentarlo como PASS ni incluirlo en `not e2e`.
- **`test_embedding_smoke.py`:** test legacy de `GroqProvider` que se **salta** sin `GROQ_API_KEY` y, si existe, puede intentar **una petición de red real**; **no ejecutar** en el working tree por inercia. `test_adapters.py` es distinto: mockea `client.chat.completions.create` y no certifica transporte real.
- **`test_cache_provider.py`:** usa SQLite en `tempfile.mkstemp` con cleanup explícito; no prueba replay/versionado G3. `test_b031_g3_reusable_fake.py` protege un fake del laboratorio, **no** respuestas de un proveedor productivo.
- **`test_real_e2e.py` y `test_pipeline_orchestration.py`:** pruebas renombradas en B05; un `execute` o parser simulado no se contabiliza como E2E operativo. `test_healing_e2e_telemetry.py` sí utiliza un `HealingPipeline` real con validador controlado, pero su nombre de archivo **no** acredita PDF final.
- **`test_assembler.py`:** ejercita decisión `DocumentAssembler.assemble` con `AssemblyExecutionContext` sintético y repositorio `MagicMock`; **no** hace compilación G5 física. `test_docling_provider.py` prueba un provider alternativo con mocks, no el provider PyMuPDF por defecto.
- **`test_b032_offline_pdf_lab.py`:** comprueba comandos `docker run --network none` como **datos**, no arranca un contenedor ni acredita egress aislado a nivel SO. Lo mismo para contratos C0/preflight de la familia lab.
- **`test_pipeline_fsm_emission.py`:** usa `core.pipeline.orchestrator.TranslationPipeline` **legacy**; no sustituye las pruebas de la FSM/queue de la ruta soportada.
- **Los 56 archivos de evaluación** incluyen oráculos GT, frozen parameters, reportes, regresión, perfiles y certificación. Pueden ser seleccionados por `pytest -m "not e2e"`, pero el programa de estabilización **no autoriza regenerar sus GT ni homologarlos como PDF→PDF**.

### 10.3 Corte A-04: qué está hecho y qué no

En el **árbol de pruebas con nodeids** se identificaron **173 archivos con tests**: **29** vinculados por ruta a TR-001–035 (§§2/7), **8** de la tanda histórica sin TR (§8.1), **31** clasificados por lectura del HEAD (§§8.2 y 9) y **105** clasificados ahora (§10.1). **29 + 8 + 31 + 105 = 173 archivos**, sin duplicados en esta partición. Fuera de ellos hay **4 archivos `test_*.py` que no definen tests ordinarios** (tres vacíos y un script manual), ya detallados en §9.4.

**A-04 — alcance por archivo: COMPLETO (173/173).** **A-04 — clasificación literal de cada nodeid/parametrización, eficacia semántica y su ejecución: ABIERTA.** La referencia `1.474` corresponde al censo histórico `86cd6867`, `1.476` al censo posterior `5447963d`, y la prueba UTF-8 agregada después no tiene un nuevo recenso completo acreditado. Se dispone de **ítems históricos** y de conciliación agregada, pero **no del `all.json` actual completo en este entorno**; por ello no fingimos un balance de 961→0 ni una nueva clasificación cuantitativa por nodeid.

**Decisión para evitar sobreingeniería:** el mapeo por archivos permite **priorizar A-05/A-07** sin ampliar B/C por rutina. Para cerrar formalmente A-04 por nodeid, solo falta **cruzar el inventario JSON ya producido por el owner con estas familias y las fichas existentes**, y separar los subcontratos con oráculo real de los condicionados por mock/skip. **No se requiere escribir otro recolector ni modificar CI/GT**, y tampoco es obligatorio revisar científicamente cada combinación parametrizada para clasificar su *alcance*. Hasta disponer de ese inventario exacto, el checkbox global permanece abierto.

## 11. A-04 — cruce exacto de nodeids del inventario aportado por el owner (2026-11-16)

**Fuente primaria reabierta:** adjunto \`all.rar\`, archivo \`all.json\` (364.053 bytes sin comprimir) y \`all.log\`. Se descomprimió el JSON y se comprobó que \`count=1476\`, \`len(items)=1476\`, hay **1.476 nodeids distintos** y **173 rutas de archivos con nodos**. Cada registro conserva \`nodeid\`, \`markers\`, \`parameter_id\` y \`skip_or_xfail_mark_declared\`. **El RAR no trae \`manifest.json\` ni campo \`revision_sha\`**: la atribución al censo de \`5447963d1c2dbce257d94aede30baabb11bd9f98\` se basa en coincidencia con el conteo, selectors y contenido que el owner reportó previamente, **no en un SHA verificable dentro de este RAR**. No aplicarlo al HEAD posterior, donde se añadió el test UTF-8.

### 11.1 Conciliación por ruta y por nodeid, sin inventar PASS

Se cruzó **cada \`nodeid\`** de \`all.json\` con su ruta (\`split("::")[0]\`) contra las listas expresas de las secciones §§2/7–10. Los grupos no se superponen y suman exactamente el inventario.

| Grupo de rutas auditadas en A-04 | Archivos | Nodeids exactos en \`all.json\` | Selección \`not e2e\` | \`e2e\` marcados |
|---|---:|---:|---:|---:|
| TR-001–035: 29 archivos vinculados por ruta | **29** | **277** | 277 | 0 |
| Puente histórico: ocho archivos sin TR (§8.1) | **8** | **236** | 236 | 0 |
| Cinco fuentes de §8.2 | **5** | **13** | 13 | 0 |
| Veintiséis fuentes de §9 | **26** | **172** | 172 | 0 |
| §10: operación y técnica compartida | **36** | **165** | 164 | 1 |
| §10: legacy/compatibilidad | **9** | **20** | 20 | 0 |
| §10: laboratorio offline/preflight | **4** | **54** | 54 | 0 |
| §10: ciencia, GT, benchmark y CV | **56** | **539** | 520 | 19 |
| **TOTAL CRUZADO** | **173** | **1.476** | **1.456** | **20** |

**Invariantes comprobados:** \`29+8+5+26+36+9+4+56 = 173\`; \`277+236+13+172+165+20+54+539 = 1476\`; \`1456+20=1476\`. Para cada ruta del mapeo hubo nodos presentes en el archivo; no quedaron rutas sobrantes ni nodeids sin familia. Los markers del JSON fueron leídos directamente: **225 \`unit\`**, **72 \`integration\`**, **20 \`e2e\`**. No se suma \`unit\` + \`integration\` como si fueran las únicas clases: hay casos sin marker de nivel.

**Diferencia decisiva:** este paso sí acredita el **100 % del cruce de identidades → archivo → familia**, pero la clasificación del **oráculo/SUT de cada escenario parametrizado** no se hereda automáticamente por compartir archivo. Los **277 nodeids de los 29 archivos TR** continúan siendo vínculos de archivo, no 277 casos de prueba validados en ejecución. Los **539 casos científicos** pueden estar en \`not e2e\` aunque la remediación de su Ground Truth siga diferida: no excluirlos silenciosamente del CI.

### 11.2 Estado formal de A-04 y próximo gate

- [x] **Inventario pinneado:** 1.476 nodeids únicos, 173 archivos, 20 E2E por marker, 1.456 seleccionables técnicos, reportado por el owner en RAR.
- [x] **Cruce completo por ruta/familia:** 1.476/1.476 nodeids vinculados a 173/173 rutas de los ocho grupos de arriba, sin reclasificar GT ni legacy como root soportado.
- [x] **Clasificación de las 35 fichas TR:** siete confiables **para su subcontrato acreditado**, nueve limitadas y diecinueve desconocidas por falta de ejecución focal; sin afirmar cobertura individual de todos los nodeids.
- [ ] **A-04 global cerrado por oráculo individual:** no acreditado; es una decisión de alcance del owner si bastan fichas de contrato + clasificación por archivo o si necesita fichas por cada parametrización. No hay justificación para crear 1.476 informes repetidos. Una futura recolección del HEAD solo se justificaría antes del gate final de CI, para evitar trasladar un censo de SHA anterior.
- [ ] **A-05/A-06/A-07 y CI:** siguen abiertos; los riesgos de escrituras en rutas fijas y testigos legacy se preservan como hallazgos a priorizar, no como bugs productivos demostrados.

**No hubo ejecución de tests, mutantes, Docker, egress, cambios en SUT, CI, corpus ni GT en este cruce.** Solo inspección de un adjunto, comparación con rutas documentadas y registro de evidencia. A-04 tiene **mapeo completo por identidad y alcance**; la protección efectiva de cada oráculo exige otra evidencia y **no se inventa**.

## 12. A-04 — criterio aprobado: parametrización material, no 1.476 fichas (2026-11-16)

**Decisión de alcance del owner:** aplicar literalmente el [plan §5.1–5.3](PLAN_REMEDIACION_TESTS_PIPELINE.md): unidad primaria **función de test o parametrización *material***, agrupada por contrato/SUT. Las variantes que prueban **distintas causas de rechazo, estados, identidades, tipos o efectos** conservan su significado individual aunque compartan función. Las meras variaciones de datos con el mismo oráculo se pueden documentar en una sola ficha de función con sus nodeids. La **ausencia de ejecución/sensibilidad** no se corrige inventando PASS: \`LIMITADO\` si el test y sus límites se conocen; \`DESCONOCIDO\` si todavía faltan lecturas/evidencia suficiente; \`CONFIABLE_PARA_SU_ALCANCE\` solo donde se ha verificado SUT, oráculo independiente, scope y sensibilidad concreta.

**Fuente de identidades:** \`all.json\` incluido en \`all.rar\` del owner, **colección de 1.476 nodeids atribuible por concordancia a \`5447963d\`, sin SHA interno en el adjunto**. Las fichas de TR son documentos de varios SHA; una función renombrada puede seguir teniendo el mismo contrato, pero **no se transfiere a ciegas un PASS desde otro SHA**. No se ejecutó nada en esta revisión.

### 12.1 Ruta crítica en fichas TR: cardinalidad real antes de reclasificar

En los **29 archivos relacionados con TR-001…035**, el JSON contiene exactamente **277 nodeids** que corresponden a **229 funciones/clases de test distintas** (agrupadas por su nodeid sin \`[parameter_id]\`). De ellas, **210 funciones no están parametrizadas** y **19 funciones se expanden en 67 nodeids**, aportando **48 variantes adicionales** sobre la cuenta de funciones. Los 277 son **vínculos a archivos de TR**, no 277 tests con oráculo certificado.

Las **19 familias parametrizadas relevantes** son las siguientes. En cada fila se conserva el **conjunto completo de IDs exactos en \`all.json\`**, aunque aquí se resumen sus sufijos legibles. La etiqueta **DIFERENCIAR** significa que el parámetro cruza una rama contractual potencialmente distinta; no declararlo redundante.

| Archivo de \`tests/\` | Función parametrizada (prefijo \`test_\`) | Nodeids | Dimensiones observadas y decisión A-04 |
|---|---|---:|---|
| \`integration/test_g3_b4_2_ocr_router_durable_plan.py\` | \`incomplete_generation_retries_without_illegal_cas\` | 2 | CREATED/PARSING; **DIFERENCIAR** por estado y llamadas OCR |
| Igual | \`active_or_finished_document_shortcuts_before_ocr\` | 2 | PROCESSING/COMPLETED; **DIFERENCIAR** active vs. terminal |
| \`integration/test_g3_b4_3a_engine_staging.py\` | \`bad_lease_rejected_before_provider\` | 3 | chunk erróneo / task errónea / expirado; **DIFERENCIAR** autoridad |
| Igual | \`bridge_rejects_unbound_provider_output\` | 3 | plain text / chunk erróneo / response errónea; **DIFERENCIAR** formato e identidad |
| Igual | \`bridge_rejects_lost_or_modified_math_token\` | 3 | token ausente / duplicado / case cambiado; **DIFERENCIAR** integridad |
| Igual | \`math_source_uncertain_fails_before_provider\` | 2 | matemática sin cerrar / colisión de placeholder; **DIFERENCIAR** causa |
| \`integration/test_g3_b3_2_fenced_receipts.py\` | \`bad_or_expired_lease_rejects_without_receipts\` | 4 | owner/execution/expiración/estado PENDING; **DIFERENCIAR** |
| Igual | \`drift_between_receipts_and_queue_blocks_replay\` | 2 | task_state/execution_id; **DIFERENCIAR** |
| \`integration/test_g3_b4_3b_publication_recovery.py\` | \`g3_recovery_selector_handles_both_homogeneous_states\` | 2 | RESULT_STAGED/COMPLETED; misma función, **dos transiciones** |
| Igual | \`g3_scheduler_excludes_unknown_generation\` | 4 | UNKNOWN/PENDING/COMPLETED/RESULT_STAGED; **DIFERENCIAR** |
| \`integration/test_g3_b4_9_reconciler_fencing.py\` | \`fenced_recovery_rejects_stale_authority\` | 4 | epoch/owner/renovación/FSM CANCELLED; **DIFERENCIAR** |
| \`integration/test_g5_assembler_lease_recovery.py\` | \`recovery_fences_old_owner_and_new_owner_completes\` | 3 | ASSEMBLING/READY_FOR_COMPILATION/COMPILING; **DIFERENCIAR** |
| \`integration/test_b024_g3_g5_math_roundtrip.py\` | \`mask_restore_render_preserves_all_math_bytes\` | 4 | delimitador inline / display / equation / placeholder literal; **DIFERENCIAR** sintaxis |
| \`integration/test_w08_durable_context_boundary.py\` | \`w08_detects_snapshot_tampering_on_restart\` | 3 | JSON/digest de snapshot/digest de manifest; **DIFERENCIAR** integridad |
| \`unit/test_w08_inference_identity_contract.py\` | \`w08_context_snapshot_rejects_invalid_producer_frame\` | 4 | frame shape, identidad y tipos; mismo error en ciertos pares pero **no descartar tipos distintos** |
| Igual | \`w08_inference_reuse_identity_invalidates_every_dimension\` | 11 | document/AST/manifest/chunk/context/prompt/provider/model/version/lang/config; **cada dimensión es material** |
| \`integration/test_g3_b4_8_preserve_engine.py\` | \`engine_preserve_provider_decision_and_full_publication\` | 3 | preserve-only / ya staged / mixto; **DIFERENCIAR** rutas de proveedor |
| \`integration/test_g3_b3_3a_staged_publication.py\` | \`rejects_invalid_projection_version\` | 4 | 0, -1, bool, float; **TIPOS Y RANGO** bajo mismo contrato de versión estricta |
| \`integration/test_g3_b3_3b_finalization.py\` | \`invalid_version_cannot_finalize\` | 4 | 0, bool, -1, float; **TIPOS Y RANGO**, aplicados a finalización |
| **TOTAL** | **19 funciones** | **67** | **Conservar las 67 identidades**; **una ficha por función con sus variantes justificadas**, no 67 documentos nuevos |

**Interpretación:** una función con once valores de identidad W08 contiene once guardas relevantes; una función con cuatro versiones inválidas puede conservar **una ficha** porque prueba el mismo contrato estricto, sin ocultar las cuatro clases de entrada. **No se verificó una mutación independiente para cada variante**, por lo que el estado de eficacia de esas variantes permanece según §7 (F/E/K pertinente o \`NOT_RUN\`).

### 12.2 Contratos críticos activos sin TR: límite de revisión

| Archivo con nodeids en el censo aportado | Casos | Comportamientos materiales y oráculo | Decisión de confianza |
|---|---:|---|---|
| \`integration/test_g3_b3_structured_result_contract.py\` | 33 | **12 funciones**, 17 invalidaciones de miembros y 6 de JSON; orden, identidad, PRESERVE/OMIT, coverage y límites UTF-8; [B3-01…33](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md) explican cada caso | **LIMITADO para el conjunto**: validación de \`result_contract\` real, pero plan de entrada compartido; el test de límite UTF-8 multibyte **se añadió después** de esta colección y fue K en otro SHA. No atribuir K a las demás variantes |
| \`integration/test_chunker_snapshot.py\` | 3 | B-02: bytes/miembros/política y dos alteraciones de manifest/source | **CONFIABLE_PARA_SU_ALCANCE únicamente donde** baseline y falsador B-02 del owner protegen la garantía puntual; otros negativos con evidencia F |
| \`integration/test_golden_parser.py\` | 1 | Parser real y contenido conocido independiente, ya no huella generada por el SUT | **LIMITADO** al PDF sintético; no GT científico |
| \`integration/test_real_parser_pipeline.py\` | 1 | Parser real de dos páginas, 4 textos conocidos y estabilidad de IDs | **E**: 1 PASS en \`f713eafc\`; alcance PDF→AST, no PDF→PDF |
| \`integration/test_pymupdf_extraction_integrity.py\` | 3 | Texto, assets visuales y dibujo no representable | **F / LIMITADO** sin prueba global OCR→G5; no deducir PASS de otro módulo |
| \`integration/test_g3_b1_policy_guardrails.py\` | 4 | Política TRANSLATE/PRESERVE/PARTIAL y reconstrucción source | **F / LIMITADO**; fuente sintética y ruta de producción parcial |
| \`integration/test_pdf_pdf_fsm_transaction_ownership.py\` | 3 | Savepoint/caller-owned transaction y rollback de FSM G2 | **F / DESCONOCIDO en ejecución**: docstring advierte posible FAIL; no cambiar contrato de transacción antes de obtener baseline segura |
| \`integration/test_pdf_pdf_sqlite_g2_guardrails.py\` | 7 | Base SQLite, alias y CAS, reabrir y rechazar DB/ruta errónea | **F / LIMITADO**; no garantía de transacción distribuida |
| \`integration/test_b023_raster_image_pipeline.py\` | 3 | Plan/PRESERVE, asset PNG/hash y rechazo vector | **F / LIMITADO**; no proveedor/Tectonic real |
| \`integration/test_b025_math_visual_preservation.py\` | 2 | Fuente visual de matemática y rechazo cuando se deshabilita | **F / LIMITADO**; no semántica ni maquetación científica |

**Control de denominadores:** esta tabla es **focal**, no suma de todos los tests activos. No cambiar el cruce exacto de **1.476/1.476** de §11 ni declarar testigos compartidos como certificados por las 35 TR. Los nodeids de ciencia/GT/legacy siguen explícitamente asignados a sus familias y **no pasan por defecto a \`CONFIABLE_PARA_SU_ALCANCE\`**; conservar la selección CI actual hasta decisión de A-05/A-07.

### 12.3 Decisión formal adoptada para A-04

- [x] **Unidad de análisis y agrupación acordada:** función/parametrización material por contrato, **no** una ficha por valor de parámetro.
- [x] **Rastro completo de identidad/alcance:** 1.476/1.476 nodeids → archivo → familia, 173/173 archivos, conforme al \`all.json\` del owner, con salvedad de SHA ya anotada.
- [x] **TR críticas:** 277 nodeids → 229 funciones, de las cuales **19** son parametrizadas; se reconocen las **67 variantes materiales o de tipos/rango**. Las fuentes TR existentes cubren SUT/oráculo/fixtures/mocks en sentido documental; los estados E/K sólo se atribuyen a sus subcontratos efectivamente ejecutados.
- [x] **G3-B3 y B01/B02:** fichas granularizadas y falsos oráculos históricos corregidos; se preservan sus límites.
- [ ] **Cierre de A-04 como garantía individual de todos los 1.476 oráculos:** **NO** es lo que permite afirmar esta evidencia. Las familias críticas todavía \`DESCONOCIDO\` por falta de comprobación material no deben promocionarse. A-04 queda **documentalmente avanzado con trazabilidad y criterio definido**; confirmar cierre formal por **calidad de clasificación**, no por un requisito artificial de 1.476 mutaciones/PASS. Los déficits reales se trasladan como riesgos a A-07, y los riesgos de host/CI a A-05/A-06.

**No se crean TR redundantes, runners, nuevas mutaciones ni ejecuciones; no se cambian contratos productivos, CI, corpus ni Ground Truth.** La eventual certificación final sobre HEAD requiere cotejar los nodeids cambiados desde el SHA del \`all.json\` y comprobar required checks, sin reabrir D-4/D-5 durante A-04.

## 13. A-04 — decisión sobre las 19 excepciones críticas (2026-11-16)

**Criterio aprobado:** §5.1–5.3 del plan: **función o parametrización material**, agrupada por contrato. Las 19 fichas \`TR\` que el resumen provisional de §7 mantenía en \`DESCONOCIDO\` **por carecer de baseline focal específica** han sido cotejadas con los tests fuente actuales, sus aserciones, dobles y efectos SQLite/ficheros. **La falta de una campaña de mutación no vuelve desconocido un SUT visible:** según §5.2, si el test es legítimo y su scope es parcial o su sensibilidad insuficiente, su clasificación documental correcta es **\`LIMITADO\`**. Esta es una **reclasificación de alcance, no un resultado nuevo de pytest ni una certificación de eficacia**.

**Leyenda:** \`F\` lectura directa de código/tests; \`E/K\` solo cuando el **testigo específico** tuvo baseline o mutación acreditadas (ver §7 y el plan); \`NOT_RUN\` ninguna nueva comprobación de sensibilidad de esta ficha. **Todo riesgo P1 aquí es prioridad de revisión documental, no error de producción observado.**

| TR antes \`DESCONOCIDO\` | SUT verdadero / oráculo material observado | Límite inequívoco y decisión A-04 |
|---|---|---|
| **004** OCR durable | \`OCRRouterDaemon._process_document\`, cola SQLite: manifest, reingesta, drift/estados evitan enqueue | **LIMITADO · F**: parser/AST store/profiler/FSM falsos; no OCR físico; variantes CREATED/PARSING vs PROCESSING/COMPLETED **distintas**, no descartarlas |
| **005** Contexto W08 OCR→G3 | \`prepare_contextual_plan\`, SQLite y \`SyncProviderBridge\`: snapshots, contexto/AST hash, error antes de \`provider.calls\` | **LIMITADO · F**: provider/prompt falsos; no inferencia pagada ni replay integral |
| **006** Staging G3 | \`stage_claimed_unit\`, recibos/estados SQLite: \`RESULT_STAGED\` sin \`COMPLETED\`, lease y respuesta inválidos no escriben | **LIMITADO · F**: fake processor; las variantes de lease **no** son redundantes |
| **007** Binding LLM | \`SyncProviderBridge.execute_chunk\`, binding/manifest/miembros y tokens math | **LIMITADO · F; P1 de precisión:** en \`test_bridge_rejects_unbound_provider_output\`, \`pytest.raises(ValueError)\` sin \`match\` podría aceptar **una causa de rechazo distinta**. Otros tests del módulo sí exigen códigos concretos. No concluir aceptación indebida del provider sin mutación |
| **008** Recibos fenced | \`ControlPlaneRepository.stage_chunk_result\`: reabrir, idempotencia, \`LEASE_FENCE_REJECTED\`, checksum, rollback y caller-owned transaction | **LIMITADO · F**: SQLite real \`tmp_path\` y plan sintético; oráculos SQL observables, no G3 daemon |
| **010** Reconciliación W06 | \`Reconciler._sweep_tasks\` con leadership falso: lease vencido sin receipt pasa a \`G3_EXTERNAL_UNKNOWN\`; segundo sweep no rehace auditoría | **LIMITADO · F**: método privado / fake liderazgo; misma fuente que otros W06, **no heredar K de reintento** |
| **012** Fencing de reconciler | \`ControlPlaneRepository\` y \`Reconciler\`: epoch, owner, lease revalidado, FSM CANCELLED; ruta G3 no va por handlers legacy | **LIMITADO · F**: líder fake y partes legacy; variantes de autoridad **materiales** |
| **014** Recuperación G5 promoción | \`AssemblyLeaseRepository.publish/recover\`, PDF temporal: \`os.replace\` fallido y commit posterior recuperable | **LIMITADO · F**: fallo inyectado, **no crash real** ni Tectonic; no atribuir K del lease vencido a ambos puntos de fallo |
| **015** Falta proyección G5 | Worker G5 + \`CQRSAssemblyContextResolver\`: \`AssemblyRejectedError\`, sin PDF/temporal ni compilador invocado | **LIMITADO · F**: test de **ausencia total**; no certificar rechazo universal de cualquier proyección faltante (política puede tolerar faltantes parciales) |
| **016** Perfil y proyección G5 | \`SQLiteProfileStore\` y \`MaterializedPlaneRepository\`: perfil reabierto, conflicto/tamper/generación/version rechazada y TeX rehidratado | **LIMITADO · F**: sin compilación física Tectonic, no PDF final |
| **020** Plan G3 SQLite | \`ControlPlaneRepository.enqueue/load_chunk_plan\`: reopen, conflicto, manifest tampered, savepoint, error SQL sin COMMIT ajeno | **LIMITADO · F**: SQL temporal real; no OCR/provider y sin sensibilidad focal de cada variante |
| **021** Snapshot durable W08 | \`DurableContextPlanRepository\`: JSON/digest/manifest alterados, snapshots faltantes, rollback, plan nuevo rechazado antes de escribir | **LIMITADO · F**: plan/AST sintéticos; tres variantes de tampering **no equivalentes** |
| **024** Identidad W08 | \`ContextSnapshotV1\`, \`InferenceReuseIdentityV1\`: hash estable y variación por 11 campos, formato inválido/rechazo | **LIMITADO · F**: los **11 campos** son dimensiones materiales; prueba identidad de modelo puro, no verificación de caché operativa |
| **025** Quota SQLite thread | \`ThreadOwnedSQLiteRateLimitStore\`, \`SyncProviderBridge\`: dos workers, escritura por hilo dueño, datos tras reapertura, cierre | **LIMITADO · F**: proveedor fake, sin gasto externo, transporte HTTP ni cuota remota |
| **026** PRESERVE engine | \`runtime.engine.run_pipeline\`, SQLite FSM/queue/materialized: no inicializa provider innecesario y completa ruta PRESERVE | **LIMITADO · F**: provider factory vigilado, no se verifica red real; preservar distinción preserve-only / staged / mixed |
| **028** Identidad chunk | \`TokenBudgetChunker\`/\`ChunkPlan\`: node vs chunk, cobertura de miembros, bytes fuente, manifest y overflow inválido | **LIMITADO · F**: estimator/AST sintéticos; tiene oráculos literales de bytes pero no provee PDF físico |
| **030** Coexistencia worker | \`ControlPlaneRepository\`: LLM no reclama trigger ASSEMBLER, finalización G3 no lo completa, reopen/worker_type | **LIMITADO · F**: repos y SQL reales, no loop de daemons; error de tipo de worker observable |
| **033** Publicación staged G3 | \`publish_staged_plan\`, \`verify_published_nodes\`: hash, coverage, receipts, rollback, replay/drift de proyecciones | **LIMITADO · F**: contenido sintético y SQL; **no trasladar K de otro test** de publicación a cada escenario |
| **034** Finalización G3 | \`finalize_published_plan\`: barrera de commit, identidad, checksum, transacción ajena, replay tras reopen | **LIMITADO · F**: sin FSM/engine real en el mismo test, ni prueba de atomicidad cross-DB global; versiones inválidas **tipos/rangos distintos** |

### 13.1 Decisiones de brecha frente a cobertura limitada

- **Sin P0 nuevo confirmado:** los 19 testigos invocan SUT reales de su frontera y contienen al menos una comprobación observable (texto exacto, SQL/estado, error específico o no-efecto). **No hay evidencia suficiente para declararlos globalmente defectuosos**, ni para subirlos a \`CONFIABLE_PARA_SU_ALCANCE\` sin sensibilidad apropiada.
- **P1 accionable de A-07: TR-007, precisión del oráculo de error.** La prueba usa \`pytest.raises(ValueError)\` genérico en un escenario de output de proveedor mal ligado. **Una excepción ValueError por otra razón daría verde**; candidato a endurecer únicamente si el contrato exige un motivo de rechazo específico, mediante revisión del marcador ya usado por pruebas vecinas. **No crear test nuevo por rutina.**
- **P1 de alcance, no corrección inmediata:** TR-004/005/006/010/012/014/015/016/025/026/030/033/034 no acreditan OCR físico, proveedor HTTP o Tectonic según corresponda; sus dobles son lícitos para contratos inferiores, **no** para llamar E2E a los resultados. **D-4/D-5 siguen diferidos**.
- **P1 de fragilidad, mantenimiento condicional:** TR-012 método/leadership privado; TR-014 fallo sintético; TR-033/034 columnas y versiones SQL; TR-024 identidad de once campos. **No refactorizar por estética**; sólo si falla un requisito de contrato o un refactor legítimo rompe el test.
- **Separar claramente A-05 y A-07:** riesgos de \`tectonic_crash.log\`, DB fija legacy y SQLite en fixtures son **seguridad de ejecución A-05**, no un defecto probado de G3/G5. Deben pasar a la matriz priorizada A-07 sin reinterpretar una inspección estática como daño ocurrido.

### 13.2 Estado de A-04 después de resolver las excepciones

El balance **actual de clasificación documental de las 35 fichas TR** es:

| Clasificación §5.2 | Antes (§7, snapshot provisional) | Ahora, tras lectura focal |
|---|---:|---:|
| \`CONFIABLE_PARA_SU_ALCANCE\` (subcontrato con E/K) | 7 | **7** |
| \`LIMITADO\` (mock legítimo, alcance acotado, sensibilidad no acreditada) | 9 | **28** |
| \`DESCONOCIDO\` *en estas 35 fichas TR* | 19 | **0** |
| \`DEFECTUOSO\` **nuevo confirmado en estas 35** | 0 | **0** |

**Esta tabla actualiza —no elimina— la foto provisional de §7.** No son 35 PASS, ni 35 K, ni garantías de toda la ruta. Ya se documentaron **1.476/1.476 nodeids → 173 rutas → familias**, las parametrizaciones materiales de la ruta TR y las limitaciones de los testigos activos sin TR (§§11–12). **La clasificación exigida para el tramo crítico de A-04 queda resuelta documentalmente; no queda ninguna de las 19 excepciones originales sin dictamen.** No hay argumento técnico para multiplicar esta auditoría en 1.476 fichas ni para reabrir B/C automáticamente.

**Límite de cierre:** el censo adjunto corresponde a la colección anterior (RAR sin SHA interno), no al HEAD posterior; no existe PASS de CI completo para esta rama ni revisión OS-level. Esos límites pertenecen a **A-05/A-06 y al cierre técnico**, no deben convertirse en una condición artificial de nuevas fichas A-04. La revisión formal del owner del dictamen sigue siendo necesaria antes de cambiar el checkbox global. **Siguiente trabajo del plan: A-05 (seguridad de ejecución) y A-07 (matriz de brechas), reutilizando esta lista de hallazgos.** No se ejecutaron nuevos tests ni se modificaron SUT, CI o GT.
