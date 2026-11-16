# A-02 / A-03 / B-06 — primera matriz focal de barreras G3/G5 de la ruta activa

> **Estado:** AUDITORÍA DE FUENTE Y SELECCIÓN FOCAL IMPLEMENTADAS, baseline dinámica del HEAD PENDIENTE.
> **Fecha:** 2026-11-16.
> **Sujeto:** \`tests_stabilization\`, código inspeccionado a partir de \`5839458ae1e10f9dcc01ba79454a3b93a97b77fb\`. Los SHA posteriores de esta misma rama incluyen únicamente el ejecutor, la matriz y el plan hasta obtener nuevas evidencias del owner.
> **No significa:** PASS de CI, product-readiness, E2E PDF→PDF, validación científica, ni aislamiento de seguridad del SO.

## 1. Relación con el plan rector

- **A-02:** trazar un contrato a su SUT, test real, oráculo y brechas.
- **A-03:** verificar independencia de oráculos y límites de mocks.
- **B-06:** revisar testigos W06/G3/G5 importantes antes de reescribir algo.
- **C-03/C-04/C-05:** solo candidatos a futuros falsadores, NO ejecutados.
- Se mantiene **A-00 cerrado; A-01…A-07, B-06 y C general abiertos**. B-01/B-02/B05 tienen evidencia focal, pero no sustituyen auditoría global.

## 2. Trazabilidad contrato → test → SUT → efectos prohibidos

| ID | Contrato observable / prioridad | SUT real | Testigo focal existente | Oráculo independiente | Límite de evidencia |
|---|---|---|---|---|---|
| G3-W06-UNKNOWN | **P0:** respuesta del proveedor perdida tras un efecto aceptado se conserva como \`G3_EXTERNAL_UNKNOWN\` y jamás se reintenta automáticamente | \`runtime.engine.run_pipeline\`, \`SyncProviderBridge\`, \`ControlPlaneRepository\`, SQLite efímera | \`test_w06_lost_reply_is_quarantined_without_second_provider_call\` | Fake cuenta \`accepted_calls == 1\`; SQLite declara \`G3_EXTERNAL_UNKNOWN\`, \`retry_count=0\`, cero receipts y re-claim denegado | Fake en puerto de proveedor, no HTTP externo; hash AST inyectado solo para aislar plan válido |
| G3-W06-RESTART | **P0:** reiniciar el engine no reenvía ni recrea proveedor para UNKNOWN | \`runtime.engine.run_pipeline\`, SQLite real | \`test_w06_restart_never_reinitializes_provider_for_unknown\` | Segundo arranque con \`_create_chunk_processor\` reemplazado por fail-fast; conserva fila y resultado \`staging_incomplete\` | No crash físico multiproceso; prueba reincorporación lógica en proceso |
| G3-PUB-MISSING | **P0:** faltar un registro de publicación no permite pasar a \`READY_FOR_ASSEMBLY\` | \`runtime.publication_pipeline.advance_staged_document\`, \`infra.db.staged_publication\`, FSM y SQLite reales | \`test_completed_with_no_publication_fails_closed\` | Se elimina una fila \`g3_plan_publications\`; error \`PUBLICATION_CONFLICT_OR_MISSING\` y FSM sigue \`PROCESSING\` | Sin motor de G5 ni render PDF |
| G3-PUB-DRIFT | **P0:** proyección materializada alterada no puede cerrar G3 | Mismos SUT + \`valid_chunks_cache\` real | \`test_corrupt_projection_never_advances_fsm\` | \`normalized_response\` cambiado a \`tampered\`, error \`PROJECTION_DRIFT\`, tareas staged y FSM \`PROCESSING\` | El test corrompe **solo SQLite temporal**; no GT |
| G5-EPOCH | **P0:** propietario/epoch incorrecto no puede recuperar lease ni cambiar FSM | \`infra.db.assembly_recovery.AssemblyLeaseRepository.recover_expired\`, SQLite attach real | \`test_wrong_epoch_and_wrong_leader_cannot_recover\` | \`None\` para epoch y owner inválidos; FSM \`ASSEMBLING\`, tarea \`PROCESSING\` | Reconciler reducido a llamada al repositorio, no daemon |
| G5-STALE-PUBLISH | **P0:** lease expirado no puede promover PDF aun sin takeover | \`AssemblyLeaseRepository.publish\`, filesystem temporal y SQLite reales | \`test_expired_lease_old_worker_cannot_publish_even_without_takeover\` | \`publish\` falso y destino **no existe** | PDF artificial de bytes de cabecera \`%PDF-\`, no compilación Tectonic |
| G5-RECOVERY | **P0:** recuperación del lease debe fencing al dueño anterior y permitir una nueva generación legítima | \`AssemblyLeaseRepository.recover_expired/claim/advance/publish\`, SQLite WAL real y archivo temporal | \`test_recovery_fences_old_owner_and_new_owner_completes\` (parametrizado 3 fases) | Viejo token no renueva/publica; nuevo token tiene ejecución distinta; FSM \`COMPLETED\` solo tras publicación válida | Test de persistencia/fencing, no aval de PDF científico ni de pipeline completo |

**Riesgos identificados:** los testigos ya implementados usan SQLite descartable, connections cerradas, mocks en fronteras precisas y no hacen llamadas externas intencionales. Hay tests con patches de \`os.replace\` acotados a fixtures de pytest, pero **no se incluyen en esta primera tanda**. La lectura de código descarta rutas fijas obvias en los siete nodos propuestos, **no una auditoría exhaustiva de imports indirectos, plugins de pytest ni red del SO**.

## 3. Primera baseline focal — runner sin Docker

El ejecutor existente [\`run_b05_focal_isolated.ps1\`](run_b05_focal_isolated.ps1) acepta \`-CheckG3G5\`, mutuamente excluyente con \`-CheckSensitivity\`, \`-CheckB01B02\` o \`-CheckB01B02Sensitivity\`. Su clon sin hardlinks ni remoto ejecuta exactamente **7 selectores nominales**, de los que el de recuperación G5 genera **3 casos parametrizados**; se esperan **9 nodeids**, a confirmar por el log real de colección/pytest. **No cambiar la selección para forzar verde.** Los tests no requieren Docker ni proveedor real.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckG3G5
pyright tests/integration/test_w06_g3_uncertain_effect_offline.py tests/integration/test_g3_b4_3b_publication_recovery.py tests/integration/test_g5_assembler_lease_recovery.py
\`\`\`

Revisar \`summary.txt\`, \`pytest_focal.log\`, \`status_changes.txt\`, y si existe un error, el traceback completo; correlacionar al **SHA exacto**. Pyright invocado por ruta verifica tests fuera del \`pyrightconfig.json\` oficial, que excluye \`tests/\`. No es sinónimo de check CI.

## 4. Falsadores diseñables solo tras baseline verde

| Control del plan | Inyección focal futura | Evidencia para matarlo |
|---|---|---|
| C-03 | Permitir una segunda llamada al fake tras el primer timeout aceptado | Contador \`accepted_calls\` >1; falla la aserción o aparece estado inválido. Un error de import **no** mata el mutante |
| C-04 | Tratar una proyección alterada como válida y avanzar el estado, o aceptar publicación faltante | Error omitido y FSM altera desde \`PROCESSING\` o se publica sin quorum. El test debe rechazarlo explícitamente |
| C-05 | Permitir publicación con lease expirado o fallo de epoch/owner | Aparece archivo final inesperado o transición de FSM no autorizada; se exige comprobar el efecto prohibido, no solo return code |

**Pendiente:** no se implementan aún mutantes C-03/C-04/C-05, ni se ejecuta C2/laboratorio. No se cambia el runtime, CI, GT, snapshots ni contratos normativos. La prioridad es demostrar baseline y revisar eventuales fallos reales sin ajustar el expected.

## 5. Evidencia focal de tipado aportada por el owner — 2026-11-16

El owner ejecutó en PowerShell con `venv` activa el comando `pyright` explícito sobre los tres archivos:

- `tests/integration/test_w06_g3_uncertain_effect_offline.py`
- `tests/integration/test_g3_b4_3b_publication_recovery.py`
- `tests/integration/test_g5_assembler_lease_recovery.py`

**Salida reportada:** `0 errors, 0 warnings, 0 informations`; el aviso `v1.1.411 -> v1.1.414` indica únicamente una versión nueva disponible. **Resultado: Pyright local focal limpio**, no un resultado del workflow oficial (que excluye `tests/`).

**Límite de trazabilidad:** el mensaje que contiene la salida no incluye `git rev-parse HEAD`; por tanto, no adjudicar esta ejecución a un SHA local determinado sin correlación adicional. El `pytest` focal `-CheckG3G5`, sus nueve nodeids previstos, el estado del clon, los controles negativos C-03/C-04/C-05 y el CI del HEAD **continúan sin resultado comunicado**. Ningún gate global se cierra por un check de tipado.

## 6. Baseline G3/G5 observada directamente y controles C-03/C-04/C-05 preparados

**Evidencia dinámica del owner, 2026-11-16.** Se inspeccionó el archivo \`reports.rar\` aportado, con su \`summary.txt\`, \`pytest_focal.log\` y \`status_changes.txt\`; no se infirió el resultado de una captura incompleta.

| Dato | Resultado |
|---|---|
| SHA de la ejecución | \`78f36678918535d3525287d1e3c9866dff5fe43e\` |
| Selector | \`g3_g5_requested=True\`, \`b01_b02_requested=False\`, \`sensitivity_requested=False\` |
| Pytest | **\`9 passed, 2 warnings in 3.31s\`**; exit **0** |
| Inventario Git | \`status_changes.txt\` de tamaño **0 bytes**, sin diferencias persistentes en el clon |
| Docker | \`docker_used=false\` |
| Entorno | Python 3.11.9 según warning; Windows y \`venv\` del owner; clon Git sin remoto |
| Límites | No hay sandbox OS, prueba de egress físico, ni laboratorio completo PDF→PDF |

**Advertencias no bloqueantes (2, NO 0):** (1) \`google.api_core\` avisa del fin de soporte futuro de Python 3.11, señalado para 2027-10-24; (2) \`apps/llm_workers/adapters.py\` importa el paquete obsoleto \`google.generativeai\`. Son hallazgos para seguimiento de dependencias y **no** justifican cambiar runtime dentro de B-06. Pyright focal de los tres archivos, reportado previamente por owner, dio \`0 errors, 0 warnings, 0 informations\`. El aviso de versión nueva de Pyright y los dos \`FutureWarning\` de pytest son señales distintas.

**Primeros tres falsadores C, IMPLEMENTADOS y TODAVÍA NO EJECUTADOS.** Se incorporó [\`probe_g3g5_sensitivity.py\`](probe_g3g5_sensitivity.py) y la bandera \`-CheckG3G5Sensitivity\` al [runner aislado](run_b05_focal_isolated.ps1). Este modo selecciona los mismos **9 nodeids** y los exige con pytest exit 0 **antes** de ejecutar cada mutante en otro proceso Python. No requiere Docker ni modifica archivos de runtime o GT.

| Control | Mutación *en memoria* del SUT | Fallo exigido del test protector |
|---|---|---|
| **C-03** G3 UNKNOWN | \`SyncProviderBridge.execute_chunk\` vuelve a llamar al proveedor tras timeout que pudo ocurrir después del efecto | \`test_w06_lost_reply_is_quarantined_without_second_provider_call\`: \`W06_UNSAFE_RETRY\`, \`1 failed\`, exit 1 |
| **C-04** G3 proyección | \`infra.db.staged_publication._verify_rows\` deja de verificar publicación/bytes materializados | \`test_corrupt_projection_never_advances_fsm\`: \`DID NOT RAISE\` el error de drift, \`1 failed\`, exit 1 |
| **C-05** G5 lease | \`AssemblyLeaseRepository._has_authority\` omite expiración pero retiene checks de propietario/generación/estado | \`test_expired_lease_old_worker_cannot_publish_even_without_takeover\`: destino PDF aparece indebidamente, \`G5_STALE_LEASE_PUBLISHED_PDF\`, \`1 failed\`, exit 1 |

**SUT y oráculo:** para C-03 se mantiene el fake del proveedor y se muta el bridge real; para C-04 se muta la verificación de publicaciones del repositorio real contra SQLite efímera; para C-05 se modifica la decisión de autoridad del repositorio y se observa **el efecto físico prohibido en el directorio temporal**. El ajuste a los tests solo añade mensajes de fallo y prioriza la aserción de ausencia del archivo G5 frente al return bool. Ninguno de los tres cambios modifica contratos o implementación productiva.

**Criterio fail-closed:** para declarar \`MUTATION_KILLED\`, el script exige \`exit_code=1\`, exactamente \`1 failed\`, traceback con \`AssertionError\` o \`Failed:\`, marcador específico y ausencia de errores de recolección/\`INTERNALERROR\`. \`NOT_ACCREDITED\` ante cualquier otra salida; el JSON \`g3g5_mutation_summary.json\` asocia resultados, fallos y SHA del clon. **No declarar mutaciones KILLED antes de inspeccionar JSON/logs del owner.** La herramienta no prueba cobertura exhaustiva ni la seguridad de otras rutas de ejecución.

**Invocación focal siguiente** (PowerShell 5.1, desde raíz del repo y \`venv\` activa):

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckG3G5Sensitivity
\`\`\`

Registrar \`summary.txt\`, \`pytest_focal.log\`, \`status_changes.txt\`, \`g3g5_mutation_summary.json\`, y tres \`g3g5_mutation_*.log\`. La nueva ejecución acredita solo su propio SHA; la baseline verde de \`78f36678\` no se hereda al SHA nuevo que añadió marcadores/runner.

## 7. C-03/C-04/C-05 — reporte de sensibilidad del owner, 2026-11-16

El owner aportó **íntegro el JSON de \`g3g5_mutation_summary.json\`** generado por el helper focal. El sujeto reportado es \`tests_stabilization\` SHA \`16a6822927ffc0b11caa84faf406c083fa0b15fd\`; \`verdict=THREE_KILLED\`. No se recibieron aquí los tracebacks de las mutaciones, el \`pytest_focal.log\` nuevo ni \`status_changes.txt\` para esta ejecución. El runner requiere \`pytest exit_code=0\` en los 9 nodeids antes de inyectar mutaciones; el JSON declara esa precondición, **pero no contiene el log del baseline**.

| Control | Mutación de SUT | Marcador exigido por helper | Exit del hijo | Veredicto reportado |
|---|---|---|---|---|
| C-03 | \`c03_g3_unknown_retry\` | \`W06_UNSAFE_RETRY\` | 1 | **MUTATION_KILLED** |
| C-04 | \`c04_g3_projection_drift\` | \`DID NOT RAISE\` | 1 | **MUTATION_KILLED** |
| C-05 | \`c05_g5_expired_lease_publish\` | \`G5_STALE_LEASE_PUBLISHED_PDF\` | 1 | **MUTATION_KILLED** |

La fuente de \`probe_g3g5_sensitivity.py\` exige por hijo \`exit=1\`, exactamente \`1 failed\`, un fallo de assert/pytest, el marcador específico y ausencia de \`ERROR collecting\`/\`INTERNALERROR\` para computar KILLED. **Esto acredita el veredicto del verificador compartido por el owner**, no una inspección directa del traceback ni la cobertura exhaustiva de la barrera.

**Límites técnicos concretos:** C-03 cuenta llamadas aceptadas por un fake de proveedor, no POST HTTP reales; C-04 inutiliza temporalmente el verificador de filas publicado, no ensaya todas las modalidades de proyección CURRENT; C-05 demuestra protección del archivo temporal contra publicación de un lease expirado, sin Tectonic ni artefacto científico. La baseline anterior sí fue inspeccionada directamente desde el RAR sobre \`78f36678\`: 9 PASS, 2 warnings y Git sin diferencias persistentes. La ejecución de sensibilidad se atribuye **solo** a su SHA \`16a68229\`.

**Estado:** evidencia focal de C-03/C-04/C-05 **POSITIVA POR RESUMEN DEL OWNER**; continúan abiertos C-00/C-01/C-02/C-06/C-07 total/C-08/C-09, A/B/C generales, seguridad de ejecución global y CI del HEAD. No actualizar \`main\`, no reejecutar C0–C4 ni modificar GT como resultado de estas tres detecciones.

**Siguiente prioridad dentro de B:** revisar la sobredeclaración E2E/parser y otras pruebas históricas (B-03/B-04), con SUT real y fixtures descartables, sin permitir que un test antiguo se presente como evaluación científica ni como comprobación de la ruta PDF→PDF completa.

## 8. Corroboración directa de baseline y tres tracebacks (owner, 2026-11-16)

**Ampliación de §7; no es una ejecución nueva.** El owner compartió íntegramente en el chat el contenido útil de los informes del clon de SHA \`16a6822927ffc0b11caa84faf406c083fa0b15fd\`:

- **\`pytest_focal.log\`:** \`......... [100%]\`, **\`9 passed, 2 warnings in 4.73s\`**. Las dos \`FutureWarning\` corresponden al soporte futuro de Python 3.11 en \`google.api_core\` y la deprecación de \`google.generativeai\` en \`apps/llm_workers/adapters.py\`. No son fallos del contrato.
- **\`summary.txt\`:** \`source_sha=16a6822927ffc0b11caa84faf406c083fa0b15fd\`; \`pytest_exit_code=0\`, \`g3_g5_requested=True\`, \`g3_g5_sensitivity_requested=True\`, \`sensitivity_exit_code=0\`, \`docker_used=false\`, \`no_OS_level_sandbox_claim=true\`.
- **C-03 log individual:** el test falla en \`test_w06_g3_uncertain_effect_offline.py:218\` con \`AssertionError: W06_UNSAFE_RETRY\`; observación independiente **\`len(fake.accepted_calls)=2\` en vez de \`1\`**; \`1 failed, 2 warnings in 3.71s\`.
- **C-04 log individual:** \`test_g3_b4_3b_publication_recovery.py:181\`, \`Failed: DID NOT RAISE <class 'ValueError'>\` donde el test exigía \`PROJECTION_DRIFT\`; \`1 failed in 0.96s\`.
- **C-05 log individual:** \`test_g5_assembler_lease_recovery.py:203\`, \`AssertionError: G5_STALE_LEASE_PUBLISHED_PDF\`; \`dst.exists() is True\` para el \`translated_doc.pdf\` del \`tmp_path\`; \`1 failed in 1.21s\`.

**Conclusión reforzada:** ya no se basa únicamente en el JSON del comprobador. Existen **tres fallos contractuales específicos inspeccionados directamente**, además de baseline nueve PASS y exit 0 en el mismo SHA, sin Docker. Los fallos son **intencionales** por parches temporales del SUT; no son fallos de la implementación sin mutar. No repetir estos tres controles para obtener la evidencia que ahora consta.

**Lo que no se ha proporcionado en estos fragmentos:** el contenido de \`status_changes.txt\` del clon de esta corrida. Por tanto, no acreditar aquí su inventario Git post, ausencia de efectos transitorios ni aislamiento del SO. Tampoco extender los resultados de este SHA al HEAD más reciente de B-03 ni al CI del repositorio. El siguiente testigo dispuesto, separado, es B-03 parser real con PDF sintético de dos páginas.

## 9. A-02 — conciliación de las ocho fronteras del plan rector (§2.4, 2026-11-16)

**Objetivo exclusivo de A-02:** relacionar **cada contrato de frontera** con SUT real, testigo y su oráculo positivo/negativo, evidencia observable y huecos. No es un plan de nuevas mutaciones, ni A-04 (ficha por cada nodeid), ni A-07 (decisión global P0/P1/P2), ni una reevaluación PDF→PDF. Esta sección consolida las [TR-001–019](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), [TR-020–035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md), matriz G3/G5 §§2–8 y los reportes focales ya acreditados en el [plan](PLAN_REMEDIACION_TESTS_PIPELINE.md). Los TR iniciales describían fuente en \`86cd6867\`; **no trasladar automáticamente sus nombres de tests al HEAD** cuando B los renombró.

**Leyenda:** **F** = contrato/SUT/oráculo inspeccionado en código (sin afirmar pytest PASS); **E** = resultado focal dinámico acreditado **en su SHA concreto**, con test sin mutar; **K** = regresión específica detectada por control negativo. **PENDIENTE** = garantía no demostrada en este programa; no inferir defecto productivo. Los resultados de diferentes SHA **no son una única suite ejecutada**.

| Frontera contractual de §2.4 | SUT y testigos trazados (fichas TR) | Positivo y negativo / oráculo independiente | Evidencia efectiva y límite | Brecha restante |
|---|---|---|---|---|
| **1. Parser / extracción B02** | \`build_extraction_pipeline → PdfParserAdapter.parse\`; \`test_verification_pipeline_connection.py\` (TR-003), \`test_real_parser_pipeline.py\` (B-03) | **+** Texto literal de PDF sintético conocido presente, nodeids únicos/estables. **−** Dibujo vectorial no representable debe producir \`B02_UNREPRESENTED_VECTOR_DRAWING\`; pérdida simulada de frase debe fallar, no basta \`len(AST)>0\` | **E:** B-03 \`1 passed\` en \`f713eafc\`; A03 selección G3-B3+B02 \`39 passed\` en \`83f99ddb\`. **K:** \`parser_dropped_source\` en \`83f99ddb\`. No OCR físico + Tectonic | Un test completo OCR→extracción real→publicación no está demostrado; corresponde al laboratorio posterior D-4, **no bloquea por sí solo la trazabilidad A-02** |
| **2. AST / plan / contexto** | \`TokenBudgetChunker\`, \`prepare_contextual_plan\`, \`DurableContextPlanRepository\`, \`ContextSnapshotV1\`, \`ControlPlaneRepository\` (TR-005/007/020/021/024/028; B-02) | **+** Cobertura de miembros/fuentes y hashing de \`document_id\`, \`ast_hash\`, \`manifest_sha256\`, persistencia W08. **−** Pérdida de miembro, cambio de bytes/manifest, snapshot/contexto de generación equivocada → rechazo; identidad incorrecta no debe avanzar ni llamar al proveedor | **F:** pruebas W08, G3 chunk/plan y B-02 con oráculos SQL/byte explícitos. **K:** \`chunk_source_byte_loss\` B01/B02 (reporte del owner, \`5a537c95\`). **E:** selección G3-B3 de \`39 passed\` incluye binding de resultado (SHA \`83f99ddb\`) | Falta una **consolidación específica** de sensibilidad para todas las dimensiones de identidad W08/manifest, no afirmar que una sola mutación las cubre. **P0 a revisar en A-07 si hay falso PASS probado**, no por falta de laboratorio |
| **3. G3 — efecto incierto del proveedor** | \`runtime.engine.run_pipeline\`, \`SyncProviderBridge\`, queue SQLite (TR-009/010, G3-W06-UNKNOWN/RESTART) | **+** Ante respuesta perdida tras aceptación se conserva \`G3_EXTERNAL_UNKNOWN\` y \`retry_count=0\`. **−** Segundo envío prohibido; fake observa \`accepted_calls == 1\`; reinicio no reinstancia provider | **E:** matriz focal \`9 passed\` y **K:** \`c03_g3_unknown_retry\`, SHA \`16a68229\`, logs inspeccionados directamente | No confirma exactly-once HTTP real, que está fuera de este ensayo offline |
| **4. G3 — proyecciones y publicación** | \`advance_staged_document\`, \`publish_staged_plan\`, \`finalize_published_plan\`, \`valid_chunks_cache\`, FSM/queue (TR-006/008/011/033/034; G3-PUB-MISSING/DRIFT) | **+** Materialización y receipts/manifest íntegros antes de \`READY_FOR_ASSEMBLY\`. **−** Publicación faltante/proyección corrupta → \`PUBLICATION_CONFLICT_OR_MISSING\` / \`PROJECTION_DRIFT\`; FSM permanece \`PROCESSING\` | **E:** \`9 passed\` en \`16a68229\`; **K:** \`c04_g3_projection_drift\` con \`DID NOT RAISE\` al anular verificación, traceback revisado. **E:** recuperación tras corte real C3/T05 \`1 passed\` SHA \`d1592715\` | No hay declaración de transacción atómica conjunta de SQLite y filesystem ni de progreso G5 real en estos tests |
| **5. FSM / leases / recovery** | \`AssemblyLeaseRepository\`, \`FSMRepository\`, \`Reconciler\`, \`advance_staged_document\`, subprocess de C3/T05 (TR-011/012/013/014/023/029/034) | **+** Recuperación autorizada tras expiración y crash; nuevo dueño completa, FSM consistente. **−** Owner/epoch antiguo o lease vencido no recupera/publica; se preservan proyecciones y receipts tras \`os._exit(73)\` | **E:** G3/G5 \`9 passed\` + **K:** \`c05_g5_expired_lease_publish\` en \`16a68229\`. **E:** C3/T05 real entre procesos \`1 passed\` en \`d1592715\`, Pyright 0 y Git clon limpio; no K propio de TR-023 | Aislamiento de procesos no equivale a sandbox OS ni a un ensayo multihost real. Las garantías de epoch/owner se observan por casos existentes, no todas por mutación |
| **6. G5 / publicación del PDF** | \`AssemblerWorkerDaemon._process_assembly_task\`, \`AssemblyLeaseRepository.publish\`, \`CQRSAssemblyContextResolver\` y puertos de compilación (TR-013–016/022) | **+** Lease vigente puede llevar a \`COMPLETED\` y archivo con cabecera PDF; temporales eliminados. **−** Lease expirado no debe promover PDF; error de compilador debe registrar \`FAILED_RETRYABLE\`, sin PDF final | **E:** 3 tests del worker \`3 passed\` SHA \`97a1bbef\`. **K:** \`g5_worker_stale_publish\` y \`g5_worker_unrecorded_compiler_failure\` en el mismo SHA, logs directos; + C-05 repo en \`16a68229\` | Compiler y renderer son fakes; **Tectonic real/PDF científico expresamente diferidos D-4/D-5**. No contabilizar falsos positivos E2E |
| **7. Foreground / CLI** | \`submit_pdf_to_inbox\`, \`handle_translate\`, \`run_admitted_pdf\` (TR-001/002/017/019/031) | **+** PDF admitido por SHA-256 sin copia no atómica y secuencia de stages coordinada. **−** No fallback a copia parcial, nunca R1; G3 incompleto no inicia G5 y PDF ausente no produce éxito | **E/K:** admisión \`8 passed\` y dos K en \`b1476250\`; foreground \`2 passed\` y dos K en \`e2d2fd5f\`. **Etapas del foreground simuladas**, no OCR físico | Error de OCR real y PDF completo bajo un único test quedan **no acreditados**; no nombrar estas pruebas E2E |
| **8. Límite externo / fake de proveedor** | \`SyncProviderBridge\`, \`QuotaManager\`, \`ThreadOwnedSQLiteRateLimitStore\`, engine PRESERVE y barrera cache W08 (TR-007/009/025/026/032) | **+** Fakes deterministas, sin credenciales; PRESERVE no debe invocar proveedor; respuestas válidas respetan plan/identidad. **−** \`G3_EXTERNAL_UNKNOWN\` no permite segundo accepted call; respuestas con token/manifest erróneos y JSON UTF-8 mayor de 4 MiB rechazadas | **F:** provider/count, cuotas SQLite y PRESERVE en testigos TR. **E/K:** G3-B3 \`39 passed\` + byte-cap mutado detectado en \`83f99ddb\`, y W06 retry K en \`16a68229\` | No demuestra bloqueo de egress por SO, costos o llamadas a un proveedor real. Advertencias sobre \`google.generativeai\` registradas como deuda de dependencias, **sin rediseño en TST-STAB** |

### Dictamen A-02 y próximos límites

**La trazabilidad requerida por el §2.4 está documentada para 8/8 fronteras** con testigos, SUT, oráculos positivos y negativos, evidencia disponible y límites. Las **35 fichas TR siguen siendo la unidad documental histórica**; esta tabla es un índice de contratos, **no 35 PASS, 35 controles negativos, un censo por nodeid ni evidencia uniforme sobre el HEAD nuevo**. Los dos P0 históricos (parser Golden y chunker snapshot autojustificado) tienen remediaciones específicas B-01/B-02 con testigos y falsadores registrados; las demás brechas son de alcance, CI o auditoría aún pendiente, no bugs de producción demostrados.

**Decisión de alcance:** no abrir más scripts, mutaciones, laboratorios ni suites ahora. A-02 **mapeo 8/8 COMPLETADO**; pendiente solo la revisión formal del owner para tratar el checkbox global como cerrado. La **clasificación de todos los nodeids relevantes (A-04)**, la **matriz priorizada de defectos reales (A-07)**, la **seguridad global A-05/A-06** y **CI del HEAD** permanecen abiertos. Siguiente trabajo lógico: revisión de brechas existentes A-04/A-07, **sin ejecutar otra campaña focal por rutina**.
