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
