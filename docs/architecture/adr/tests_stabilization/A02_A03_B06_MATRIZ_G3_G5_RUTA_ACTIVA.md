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
