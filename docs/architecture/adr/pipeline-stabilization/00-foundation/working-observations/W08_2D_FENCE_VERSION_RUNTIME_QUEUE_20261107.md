# W08-2d — Corte de barrera de protocolo SQLite por versión de runtime

**2026-11-07 · WORKING OBSERVATION / REVIEW / NO DEPLOY / NO MERGE**

**Cadena de dependencia:** [PR #40](https://github.com/RDsanchez-git/translator_pdf/pull/40) OCR/G3 contextual → [PR #41](https://github.com/RDsanchez-git/translator_pdf/pull/41) recuperación legacy por receipts → rama `w08-2d-protocol-fence-sqlite-review`. El issue rector sigue siendo #36, bajo el candidato D-1/D-2 y matriz §7. No modificar NADR-FROZEN.

## Problema identificado

Un chequeo de versión solamente en el código nuevo **no impide** que procesos antiguos accedan a una `queue.db` actualizada: los binarios viejos no ejecutarían ese chequeo. Además, W08-2c tiene un nuevo contrato de contexto que cambia los prompts; permitir workers antiguos sobre esos planes podría realizar inferencias con `breadcrumbs=()` sin el preflight W08. La transición no puede basarse en `IS_BENCHMARK`, flags de caché ni identidad de generación superficial.

## Barrera implementada, DESACTIVADA por defecto

- `infra/db/runtime_protocol_fence.py`: `bind_runtime_protocol(conn)` registra una función SQLite con la versión del protocolo que conoce este runtime, `w08_runtime_protocol()`. **No es un secreto ni autenticación**.
- `activate_runtime_protocol_fence(...)` requiere actor, ticket de cambio y confirmación explícita de drenaje externo. En una transacción local `BEGIN IMMEDIATE` rechaza tareas actualmente `PROCESSING`; registra activación en `g3_runtime_protocol_fence`; instala triggers `BEFORE INSERT/UPDATE/DELETE` sobre `chunk_tasks`, `chunk_plans`, `chunk_result_receipts`, `g3_context_snapshots` y el propio registro del fence. La activación no cambia las tareas ni asigna contexto a planes legacy.
- Después de activarla, una conexión SQLite antigua sin la función de protocolo aborta ante cualquier escritura protegida (`no such function: w08_runtime_protocol`). Una conexión actual abierta con `get_connection(...queue.db...)` registra la función en el composition root. El escritor nuevo tampoco se admite si faltan triggers o el registro está malformado.
- OCR Router verifica el protocolo antes de ingerir; G3 Engine lo verifica al iniciar y antes del sondeo del scheduler. **No se introdujo un daemon de despliegue ni migraciones automáticas**.
- Los tests con SQLite descartable cubren el modo desactivado, aceptación de versión nueva, rechazo de inserciones/modificaciones/borrados legacy y del registro auditable, reapertura, operador ausente, transacción externa, claims activos y rollback de DDL si faltan tablas.

## Límites de autoridad y seguridad, no ocultar

1. **No protege operaciones de proveedor que ya estaban en vuelo al activar.** El corte debe detener ingreso/dispatch y **drenar realmente todos los procesos antiguos antes de activar**, verificando que no haya llamadas remotas pendientes. El booleano `drained_legacy_runtimes=True` no certifica este hecho; la comprobación SQL de ausencia de `PROCESSING` es necesaria pero insuficiente.
2. La protección es contra clientes *cooperativos de versiones anteriores* sin la función SQLite. **No es una frontera de seguridad frente a un actor con privilegios DDL**: un actor que pueda hacer `DROP TRIGGER`, reemplazar la función registrada o alterar el archivo de base puede eludirla. Requiere permisos y políticas operativas externas. El runtime moderno detecta triggers eliminados en el preflight, pero no puede demostrar que el sistema no haya sufrido una escritura antes.
3. El gate es local a `queue.db`, no crea transacción distribuida ni cerca automáticamente escrituras independientes a `fsm.db`, `materialized.db` o archivos AST. Requiere exclusión de procesos antiguos también a nivel de despliegue. La recuperación legacy por receipts de #41 permanece manual y no gobernada por credencial autenticada.
4. El registro `operator_id/change_ticket` es una **declaración auditable, no autenticación ni aprobación criptográfica**. Activación del fence desde código de producción exige runbook y control de accesos fuera de la aplicación; **no habilitarla automáticamente al arranque de OCR/G3 ni al bootstrap de SQLite**.
5. No se incorporó `InferenceReuseIdentityV1` a caché v1, ni se habilitó replay automático W06. `G3_EXTERNAL_UNKNOWN` se conserva; NO volver a intentar.
6. Una vez activado el protocolo, **no volver a iniciar un binario antiguo contra esa cola** ni hacer rollback de código en caliente. El rollback operativo requiere detener servicios y un procedimiento aprobado; no retirar triggers ni alterar receipts como workaround.

## Criterios para revisión

- Pyright strict sin errores, Import Linter 4 kept, 0 broken.
- Suite unit + B03/W06/W08-2b/W08-2c + W08-2d legacy + testigos de fence **en el head exacto**.
- Rechazo de versión vieja con SQLite real, incluso si la conexión no llama a ningún método W08 nuevo, y ausencia de corrupción de tareas tras error.
- Regression Gates y B02 vector drawing mantienen sus FAIL históricos; **no adulterar** corpus ni oráculos para obtener una CI global verde.

**Veredicto hasta validar:** candidato técnico de exclusión de escrituras de versiones viejas; no certifica rollout, autenticación, drenaje real ni recuperación del estado de sistemas externos. PR #40/#41 y este corte siguen sin fusionar.
