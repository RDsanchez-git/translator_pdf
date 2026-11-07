# W08-2d — Aprobación firmada y ligada al inventario exacto de queue.db

**2026-11-07 · WORKING OBSERVATION · DRAFT / NO MERGE / NO DEPLOY**

**Dependencias:** PR #40 (contexto OCR/G3) → PR #41 (recuperación manual de receipts) → PR #42 (barrera de escritura SQLite) → este corte de autorización. La referencia sigue siendo la convergencia PDF→PDF D-1/D-2 (§7), no las hojas de ruta generales.

## 1. Modelo propuesto, alcances reales

- `inspect_queue_cutover()`: consulta **solo lectura** sobre `queue.db` y obtiene cantidades de planes/tareas/receipts/contextos, `PROCESSING`, `G3_EXTERNAL_UNKNOWN`, staged/completed y leases activos. Calcula una huella SHA-256 determinista de todas las filas relevantes, incluidos los manifiestos completos, metadatos de ejecución y **digests de los textos de receipts**, y del path real de la base. **No** emite contenido de documentos ni recibos como parte del DTO.
- `issue_cutover_approval()`: emisión offline de `SignedCutoverApproval` con propósito fijo (`activate-w08-context-durable-v1`), identidad declarada de operador, ticket, huella de inventario y ruta, timestamps, nonce aleatorio y HMAC-SHA256. Validez máxima de cinco minutos, por defecto dos.
- `verify_cutover_approval()`: verifica ámbito/tiempo/operador autorizado y firma con una **clave secreta confiable que el caller suministra desde fuera del repositorio**. No acepta claves suministradas dentro del token. No hay clave productiva embebida, ni consulta de usuarios a un servicio externo.
- `activate_runtime_protocol_fence()`: **se elimina el atajo de `operator_id/change_ticket/drained=True` sin firma**. Toma aprobación firmada y registro de claves confiables. Bajo `BEGIN IMMEDIATE`, vuelve a inventariar la misma base y exige identidad exacta, firma válida, cero tareas `PROCESSING` y cero leases vivos; luego instala el fence existente atómicamente. Si un estado cambió entre lectura y activación aborta y revierte. Una activación ya realizada no acepta una segunda operación/replay.

## 2. Qué no demuestra

**HMAC autentica posesión de un secreto**, no necesariamente a una persona física. Si una clave está disponible a varios operadores o al runtime, la identidad en `operator_id` no es independiente y la pista local de `queue.db` no es auditoría inmutable. La asignación exclusiva de claves por operador y revocación son responsabilidad de un sistema externo de identidad/secretos, actualmente **no integrado**. La clave secreta nunca debe vivir en GitHub, logs, CI, PDFs o configuración versionada; los valores estáticos de tests son únicamente ficciones descartables.

**El inventario es de queue.db**, no un backup coherente de `fsm.db`, `materialized.db`, event.db, rate limits y archivos AST. No acredita ausencia de procesos antiguos, operaciones ya en vuelo, llamadas LLM no recibidas, ni aprobación de terceros. El flag `drained_legacy_runtimes=True` sigue siendo una aseveración operativa no verificable desde SQLite y NO debe usarse para activar despliegue sin evidencias externas.

**La barrera contra writes es cooperativa**, basada en UDF+triggers; un proceso con permiso DDL o acceso al secreto puede eludirla. El fence tampoco protege lectores antiguos ni scripts ajenos a las tablas enumeradas. No hay CLI de producción, endpoint remoto de activación ni conexión a una cuenta de operador.

## 3. Gates operativos pendientes (NO ejecutados)

1. **Inventario interplanos** en copia coherente y respaldada: document_id/ast_hash/manifest, estados y receipts en queue.db, FSM, materialized.db, ASTRegistry y leases; reconciliar sin modificar cada origen, incluir UNKNOWN.
2. **Drenaje físico y ausencia de provider I/O**, stop-the-world que realmente pare OCR, G3, reconciler y demás escritores antiguos. Exigir evidencias de versión de procesos y privilegios DDL restringidos, no solo task_state ni el booleano.
3. **Aprobación por identidad confiable**: provisionar un registro de secretos por operador en un almacén de secretos externo, política de emisión/supervisión/revocación y registro append-only independiente. Evaluar firmas asimétricas si el runtime no debe conocer claves de firma.
4. **Ejecución y rollback**: procedimiento reproducible para activar el protocolo únicamente en ventana aprobada, revalidar ausencia de writes de versiones viejas y preservar `G3_EXTERNAL_UNKNOWN`; sin borrado de triggers ni rollback automático de código tras activar.
5. **Evidencia del head CI**: Pyright/Import Linter, tests unitarios, B03, W06, W08-2b/2c, receipts legacy y testigos de protocolo/aprobación, más registro transparente de B02 y corpus privado.

**Veredicto:** implementación propuesta de control criptográfico de ámbito+inventario exacto de `queue.db`. No es una certificación de autoridad de despliegue ni cierra toda W08-2d. PR #40/#41/#42 y este corte deben permanecer Draft hasta evidencia operativa de los cinco puntos anteriores.
