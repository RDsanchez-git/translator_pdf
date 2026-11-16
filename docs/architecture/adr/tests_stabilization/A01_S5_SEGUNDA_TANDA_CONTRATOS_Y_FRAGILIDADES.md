# A01-S5 — Segunda tanda de trazabilidad: contratos durables, G5 y límites de entrypoints

> **Estado:** 16 fichas adicionales **TR-020 a TR-035** documentadas por inspección estática; [primera tanda TR-001–TR-019](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md). **35 fichas acumuladas**, no necesariamente 35 archivos únicos ni 35 tests independientes. **A01-S5, A-01 y A-05 permanecen abiertos.**
>
> **Fecha:** 2026-11-15. **SHA fuente fijado:** `86cd68672ee692f073b62869e7c9bd177e8d9e3b` (mismo SHA de la colección previa). **Método:** lectura directa del código fuente, test y [Atlas operativo](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md). **No se ejecutaron tests ni mutaciones; no se alteraron CI, runtime, fixtures ni Ground Truth.**

## 1. Alcance, definición y criterio de clasificación

Segunda tanda centrada en contratos que deben sobrevivir a refactors de implementación: identidad de plan/contexto, transacciones SQLite/savepoints, frontera LLM vs ASSEMBLER, W06/PRESERVE, publicación durable y recuperación entre procesos, lease G5, CLI foreground y exclusión de roots legacy.

Las etiquetas **E-OBS** (SUT realmente llamado + aserción observable escrita), **E-ALC** (alcance acotado), **R-REF** (fragilidad ante refactors), **P-NEG** (control negativo codificado o candidato) **NO equivalen a test PASS ni mutation kill**. Evitar categoría final «confiable para su alcance» hasta A-03/C.

**Unidades de trazabilidad:** el identificador TR representa un **contrato/frontera y sus tests testigo**, no un nodeid. La unidad verificable de pytest sigue siendo cada nodeid. Pueden repetirse archivos entre fichas y fases sin reclamar cobertura adicional.

## 2. Matriz exhaustiva de esta tanda

| Ficha | Frontera | Fuente (líneas) | SUT productivo realmente ejercitado | Simulaciones / límite | Oráculo/defecto que debería detectar | Dictamen provisional y riesgo |
|---|---|---|---|---|---|---|
| **TR-020** | G3 B2 durable | [`test_g3_b2_sqlite_plan_contract.py`](../../../../tests/integration/test_g3_b2_sqlite_plan_contract.py) 49–205 | ControlPlaneRepository.enqueue_chunk_plan/load_chunk_plan; SQLite real en tmp_path | AST/plan sintético, estimador simple; sin OCR/LLM | Persistencia tras reopen; idempotencia; conflicto de manifest y drift de tasks; rollback y savepoint del caller. **Falsador:** Manifest alterado aceptado, fila huérfana o COMMIT ajeno | **E-OBS; P-NEG**. Las consultas SQL validan el contrato durable; parte del schema puede cambiar en refactor |
| **TR-021** | W08 snapshot durable | [`test_w08_durable_context_boundary.py`](../../../../tests/integration/test_w08_durable_context_boundary.py) 60–217 | DurableContextPlanRepository; ControlPlaneRepository; enrich/derive context; SQLite tmp_path | AST sintético/estimador; sin provider ni OCR físico | Snapshots rehidratados, plan idempotente, tampering de JSON/SHA/manifest y pérdida de snapshot => rechazo sin tareas/side effects. **Falsador:** Se permite contexto de otra generación; snapshot incompleto o no confiable | **E-OBS; P-NEG**. Hay assertions SQL del esquema de snapshots; preservar propiedad, no columnas incidentales |
| **TR-022** | G5 worker real, puertos falsos | [`test_g5_assembler_worker_integration.py`](../../../../tests/integration/test_g5_assembler_worker_integration.py) 24–113 | AssemblerWorkerDaemon._process_assembly_task; AssemblyLeaseRepository real y WAL real | FakeResolver, FakeCompiler y FakeRunner; construcción con __new__; fixture importada desde OTRO test | Estado COMPLETED, PDF con cabecera, temporales ausentes; lease expirado prohíbe publicación; fallo de compilación pasa a FAILED_RETRYABLE. **Falsador:** Worker viejo publica PDF o reporta éxito tras Tectonic fallido | **E-OBS; E-ALC; R-REF**. Crítico: __new__, método privado y dependencia cruzada de tests; no Tectonic físico |
| **TR-023** | Crash real entre procesos G3 | [`test_c3_t05_process_boundary.py`](../../../../tests/integration/test_c3_t05_process_boundary.py) 178–225 | Dos subprocess Python reales + os._exit(73) en primer proceso; ControlPlaneRepository, publicación y advance_staged_document | Estado en carpeta tempfile; contenido de provider preconstruido; sin proveedor/daemon/pdf | Primer proceso materializa y muere antes de completar queue/FSM; segundo reabre SQLite y llega a READY_FOR_ASSEMBLY sin cambiar proyecciones; tercer lector readonly. **Falsador:** No puede reanudar después de terminación abrupta o repite materialización | **E-OBS; P-NEG**. Aislamiento de procesos REAL en test, NO Docker/daemon completo. Ejecutarlo solo bajo A-05; procesos secundarios pueden ejecutar imports |
| **TR-024** | W08 identidad de reuso | [`test_w08_inference_identity_contract.py`](../../../../tests/unit/test_w08_inference_identity_contract.py) 29–150 | ContextSnapshotV1; InferenceReuseIdentityV1 reales | Entradas sintéticas; sin I/O | Hash determinista; cambia ante dimensiones de identidad; rechazo JSON tampered y digest inválido; excluye execution_id/lease_owner por contrato. **Falsador:** Se reusa respuesta bajo contexto/generación/configuración incorrecta | **E-OBS; P-NEG**. Verificar norma de campos relevantes, no convertir hashes de objeto interno en snapshot libremente regenerable |
| **TR-025** | Quota SQLite thread ownership | [`test_g3_b4_7b_sqlite_quota_thread_owner.py`](../../../../tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py) 93–157 | SyncProviderBridge real, QuotaManager y ThreadOwnedSQLiteRateLimitStore; ThreadPoolExecutor | Proveedor y prompt builder fake; DB de tmp_path | Dos inferencias concurrentes guardan cuotas; lectura tras cierre y nueva instancia; adapter legacy falla por affinity; close idempotente. **Falsador:** Write en thread ajeno o cuota perdida tras reinicio | **E-OBS; P-NEG**. Control técnico sobre afinidad SQLite; no rate limit remoto o gasto real |
| **TR-026** | PRESERVE sin proveedor | [`test_g3_b4_8_preserve_engine.py`](../../../../tests/integration/test_g3_b4_8_preserve_engine.py) 90–148 | runtime.engine.run_pipeline real; repos durables de queue/FSM/materialized | ASTRegistry/hash/get_connection inyectados a tmp_path, factory de proveedor vigilado | PRESERVE genera receipt nulo, no abre proveedor cuando no corresponde, completa y publica; modo mixed sólo envía TRANSLATE. **Falsador:** Se hace POST para PRESERVE o se exige proveedor innecesariamente | **E-OBS; E-ALC; P-NEG**. assert exacto de shutdowns/acceso a engine._create_chunk_processor puede ser frágil, contrastar contrato de no-egress |
| **TR-027** | Roots y R1/R3 | [`test_c4_t06_supported_roots.py`](../../../../tests/unit/test_c4_t06_supported_roots.py) 28–98 | AST de apps/cli/main.py; strings de Compose/Dockerfile/pyproject.toml | NO importa SUT ni ejecuta entrypoints | R1 no registrado en CLI; launchers versionados no apuntan a R3; entrypoint CLI apunta a apps.cli.main. **Falsador:** Un root soportado selecciona legacy R1 o R3 | **E-ALC; R-REF**. Es un oráculo *textual/estructural* acoplado a nombres/shape (número de statements/handlers); cambios semánticamente válidos lo romperían |
| **TR-028** | Identidad chunk vs miembro | [`test_g3_chunk_identity_contract.py`](../../../../tests/integration/test_g3_chunk_identity_contract.py) 29–114 | TokenBudgetChunker, ChunkPlan.build/from_json, dominio AST | AST sintético, estimator fake; sin DB/proveedor | chunk_id no igual a node_id; cobertura de todos los miembros; bytes fuente intactos; manifest tampered y overflow/restrategias inválidas rechazados. **Falsador:** Desaparecen miembros o cruza generación sin detectar | **E-OBS; P-NEG**. Contratos de hash/generation exactos válidos si normativos; algunos outputs pueden ser internos |
| **TR-029** | WAL write scope | [`test_g3_wal_stage_write_scope.py`](../../../../tests/integration/test_g3_wal_stage_write_scope.py) 32–106 | ControlPlaneRepository._chunk_plan_write_scope y sqlite3 WAL en dos threads | DB tmp_path, competidor sintético; sin servicio G3 | Un segundo writer queda bloqueado, inserción staged se confirma; transacciones caller-owned no se autocommittean; exception rollback. **Falsador:** SQLITE_BUSY_SNAPSHOT o commit indebido a transacción ajena | **E-OBS; R-REF; P-NEG**. Acoplamiento a método privado y scheduling/timing; portar a contrato transaccional observable cuando sea posible |
| **TR-030** | LLM y ASSEMBLER comparten queue | [`test_g3_b4_1_worker_coexistence.py`](../../../../tests/integration/test_g3_b4_1_worker_coexistence.py) 88–160 | ControlPlaneRepository; publish_staged_plan/finalize; SQLite tmp_path | AST/plan sintético; no daemons | LLM pickup no reclama ASSEMBLER; finalización G3 no completa trigger; replay soporta ambas tareas; worker extraño es drift. **Falsador:** Falsa finalización de trigger ASSEMBLER o claim del tipo incorrecto | **E-OBS; P-NEG**. Comprobación por worker_type/estado durable; detalles SQL requieren trazabilidad normativa |
| **TR-031** | Foreground policy/errores | [`test_b03_foreground_pdf_product.py`](../../../../tests/integration/test_b03_foreground_pdf_product.py) 58–172 | apps.cli.pdf_product.run_admitted_pdf/preflight_product_run | **_ingest, _run_g3, _run_g5 y _read_status totalmente parcheados**; PDF/control creados por el propio fake | Orden OCR→G3→G5, reanudación, rechazos de FSM incorrecto, PDF ausente/cabecera inválida, DB/compilador no disponible. **Falsador:** Reporta COMPLETED sin PDF o llama G3/G5 después de fallo | **E-ALC; R-REF; P-NEG**. No es E2E: mockea todos los stages; puede romper con refactor de helpers privados aunque API conserve contrato |
| **TR-032** | W08 cache legacy deshabilitada | [`test_w08_g3_cache_barrier.py`](../../../../tests/unit/test_w08_g3_cache_barrier.py) 16–83 | runtime.engine._create_chunk_processor y build_provider_stack reales | Constructor de provider/bridge/rate store monkeypatch; ningún proveedor se invoca | cache_db_path=None y no crear CachedLLMProvider; wrapper CircuitBreaker mantenido. **Falsador:** Reaparece cache insegura solo por prompt_hash | **E-OBS; R-REF; P-NEG**. Comprueba kwargs internos y nombre de fábrica privada; convertir a observación de no-acceso a caché en remediación si procede |
| **TR-033** | Publicación G3 materialized | [`test_g3_b3_3a_staged_publication.py`](../../../../tests/integration/test_g3_b3_3a_staged_publication.py) 91–237 | publish_staged_plan/verify_published_nodes; ControlPlaneRepository; SQLite reales tmp_path | Responses sintéticas, no proveedor | Proyecciones completas con hash fuente, sin completar queue antes de publication; idempotencia; tampering/receipt incompleto/rollback falla cerrado. **Falsador:** Proyección corrupta publicada o repetición invalida estado | **E-OBS; P-NEG**. Oracle sensible a schema columnar; recuperar invariantes de hash/coverage desde puerto estable donde se pueda |
| **TR-034** | Finalización G3 barrier | [`test_g3_b3_3b_finalization.py`](../../../../tests/integration/test_g3_b3_3b_finalization.py) 92–294 | finalize_published_plan; SQLite queue/materialized | Plan pre-staged; sin FSM daemon/proveedor | COMPLETED sólo tras publicación confirmada; no acepta publicación sin commit, checksum alterado, ejecución equivocada; rollback transacción caller-owned. **Falsador:** Completar plan mixto, drift o publicar datos no commiteados | **E-OBS; P-NEG**. Algunos contadores state_version/timestamps son normativa de CAS, otros schema accidental; por revisar |
| **TR-035** | Handoff FSM/SQLite heredado | [`test_pdf_pdf_sqlite_contracts.py`](../../../../tests/integration/test_pdf_pdf_sqlite_contracts.py) 29–136 | DocumentCommandHandler, FSMRepository, get_connection, ControlPlaneRepository; DB temporal | Rutas SQLite remapeadas a tmp_path | FSM PROCESSING durable y visible tras cerrar conexiones; queue ya adjunta FSM para scheduler. **Falsador:** Queue persistida apunta a FSM perdida o consulta a DB equivocada | **E-OBS; E-ALC; P-NEG**. Docstring refiere a commit histórico y predice FAIL allí, **no prueba estado actual**; no E2E |

## 3. Hallazgos con prioridad de mantenimiento

### RM-01 — Test G5 con fixture importada entre archivos y constructor `__new__` (P1: fragilidad, no defecto probado)

[TR-022](../../../../tests/integration/test_g5_assembler_worker_integration.py) importa la fixture `sandbox` y helpers `_expire`, `_fsm`, `_recover` de `tests/integration/test_g5_assembler_lease_recovery.py` y crea un `AssemblerWorkerDaemon.__new__(AssemblerWorkerDaemon)` sin usar su inicializador. Ejecuta **el método real**, pero establece manualmente dependencias en atributos y simula Tectonic/compilación/contexto.

**Riesgo:** un cambio legítimo del constructor/estructura privada requiere editar tests sin afectar contrato de publicación, y la importación cruzada arrastra dependencias de colección. **No eliminar ni mover durante A:** en B, si se aprueba, extraer solo fixture contractual compartida a `tests/helpers` o `conftest` y preferir composición pública, conservando el witness de lease vencido.

### RM-02 — Contrato técnico G3 con método privado y timing de WAL (P1: fragilidad)

[TR-029](../../../../tests/integration/test_g3_wal_stage_write_scope.py) usa `ControlPlaneRepository._chunk_plan_write_scope()`, un nombre privado, y espera que un competidor reciba `SQLITE_BUSY` en una ventana de tiempo concreta. **El efecto contractual** que sí interesa preservar es una escritura serializable sin `SQLITE_BUSY_SNAPSHOT`, con rollback y **sin** apropiarse del commit del caller.

**Riesgo:** cambios en la estrategia de lock/WAL o scheduler de threads pueden romper el test aunque la garantía real siga vigente. Candidata a test de puerto durable con sincronización robusta y control de concurrencia controlado.

### RM-03 — Root R1/R3 protegido mediante estructura AST/textual (P1: fragilidad y alcance restringido)

[TR-027](../../../../tests/unit/test_c4_t06_supported_roots.py) prueba imports, la forma de un handler (`len(body)==2`), cantidad de registrations, strings literales de Compose y Dockerfile. **Esto protege la configuración versionada y una forma concreta del código**, pero no resuelve el Compose **efectivo** ni launchers externos.

**Falsador normativo mejor:** ejecutar/verificar la **selección real** por entrypoint público bajo aislamiento y comprobar que nunca deriva a R1/R3; conservar AST como un chequeo estático complementario, no como autoridad exclusiva.

### RM-04 — Foreground B03 simula *todas* sus etapas (P1: límite de alcance)

[TR-031](../../../../tests/integration/test_b03_foreground_pdf_product.py) parchea `_ingest`, `_run_g3`, `_run_g5` y `_read_status`; sus archivos PDF son construidos por los dobles. **Sí ejerce `run_admitted_pdf` y su guard de estados, reanudaciones y errores**; **no** acredita integración OCR/G3/G5 ni PDF físico real. Compararlo con TR-017, que ejerce las raíces y usa solo tres fronteras externas simuladas.

**Riesgo:** nombre `integration` no debe usarse para declarar E2E completo. Conviene proteger el contrato de errores y publicación observable sin acoplar demasiado el test a helpers privados.

### RM-05 — Crash G3 entre procesos es más fuerte que la simulación por excepción (P0 de seguridad de ejecución, NO defecto de test)

[TR-023](../../../../tests/integration/test_c3_t05_process_boundary.py) sí ejecuta **dos procesos Python distintos** y el primero llama `os._exit(73)` tras persistir proyecciones, antes de finalizar queue/FSM. El segundo vuelve a abrir SQLite en el mismo directorio temporal y verifica recuperación, y el padre es un tercer lector. Esta cobertura **no se puede reducir** a «crash simulado con una excepción».

**Pero:** el child hereda parte del entorno y usa `cwd=ROOT`/PYTHONPATH del checkout; es un **test de ejecución**, no inocuo por el mero hecho de usar `tempfile`. No ejecutarlo fuera de un aislamiento/control A-05; lectura estática y colección no bastan para afirmar ausencia de efectos import-time transitivos.

### RM-06 — W08 cache barrera de no-uso no acredita replay versionado (P1: alcance contractual)

[TR-032](../../../../tests/unit/test_w08_g3_cache_barrier.py) vigila que el engine **no active la caché legacy por `prompt_hash`**. El mismo archivo advierte explícitamente que el contrato completo de caché versionada/replay está **abierto**. No usar el hecho de que se deshabilita caché legacy como prueba de corrección de un cache nuevo; necesitará identidad completa o un oráculo independiente.

### RM-07 — Estado científico/histórico queda registrado, pero fuera de ejecución y remediación actual

[TR-035](../../../../tests/integration/test_pdf_pdf_sqlite_contracts.py) contiene docstring sobre fallar sobre un commit anterior; no demuestra fallo del estado actual. Se lee como contexto histórico de regresión técnica. **GT y evaluación científica permanecen explícitamente diferidos**. No modificar corpus ni umbrales.

## 4. Matriz de falsación propuesta (NO EJECUTADA)

| Código | Contrato estable | Mutación candidata en sandbox descartable | TR protector | Prohibido |
|---|---|---|---|---|
| F-11 | Persistencia B2 del manifest | Rechazar verificación del manifest/tareas tras reabrir SQLite | TR-020 | Adoptar tareas legacy sin plan |
| F-12 | Snapshot W08 verificable | Aceptar snapshot con SHA o contexto de generación alterados | TR-021/TR-024 | Inferencia con contexto ajeno |
| F-13 | G5 worker fencing real | Permitir `publish` tras caducar lease durante compilación | TR-022 | PDF final publicado por stale owner |
| F-14 | Recover tras crash abrupto | Suprimir recuperación por proceso independiente después de publicar materialized | TR-023 | FSM o tareas falsamente completadas |
| F-15 | Store cuotas ownership | Reutilizar conexión SQLite creada en thread equivocado | TR-025 | Escribir cuota insegura o perder estado |
| F-16 | PRESERVE no necesita LLM | Inicializar provider para unidad exclusivamente PRESERVE | TR-026 | Egress indebido/facturación |
| F-17 | LLM/ASSEMBLER no se confunden | Permitir que G3 claim/finalize alcance tarea ASSEMBLER | TR-030 | Trigger de ensamblado consumido/COMPLETED |
| F-18 | G3 publicación atómica por DB | Permitir proyección parcialmente persistida tras INSERT de falla | TR-033/TR-034 | Proyección corrupta o plan mixto |
| F-19 | Preflight foreground no publica falso éxito | Retornar COMPLETED con PDF ausente/malformado | TR-031 | Éxito reportado sin PDF válido |
| F-20 | G3 cache legacy prohibida | Activar `CachedLLMProvider` en ruta G3 sin binding versionado | TR-032 | Reuso por prompt_hash no autorizado |

**Regla:** no se declara un test sensible por incluir un `pytest.raises`; hay que romper la barrera en SUT de una copia descartable y observar fallo por causa contractual, sin aceptar un fallo por import error o por mock defectuoso.

## 5. Priorización de tests resistentes a refactors

| Nivel | Contrato que merece test resistente | Oráculo que debería sobrevivir cambios profundos | Evitar fijar (si no normativo) |
|---|---|---|---|
| P0 | UNKNOWN no reintenta, G5 lease impide stale publication, G3 no completa sin publicación | Estado durable tras reconexión + ausencia de receipt/PDF/POST indebido | Método privado o orden de helper |
| P0 | Contexto/generación/identidad de respuesta y manifest | Hashes normativos + rechazo de cross-generation y no-effect | Forma incidental del DTO o número de llamadas internas |
| P1 | Ownership transaccional y recuperación física | Estado de dos conexiones/procesos + snapshot de bytes de salida | Número de SQL statements o estrategia de locking |
| P1 | CLI pública no deriva a R1/R3 | Exit code/estado observable/artefacto de ruta seleccionada | Forma AST literal, líneas y tokens de Compose |
| P1 | Quota store y provider wiring | Cuotas persistidas tras reopen, no egress de caché legacy | Nombre concreto de factory privada |
| P2 | Render sintáctico y normalización matemática | Bytes matemáticos y errores explícitos ante alteración | Texto exacto del prompt no normativo |

## 6. Checklist y alcance de cierre

- [x] **S5-T2-01 — 16 fichas TR-020…035** con SUT, doubles, oráculo, defecto candidato y límite.
- [x] **S5-T2-02 — Diferenciar crash de proceso real del crash simulado**, y documentar su requisito de aislamiento.
- [x] **S5-T2-03 — Señalar fragilidades de test de G5, WAL, foreground, roots y cache** sin reescribirlos ni calificarlos falsamente como defectos.
- [x] **S5-T2-04 — Añadir falsadores F-11…F-20** sin ejecutarlos.
- [ ] **S5-T2-05 — Cobertura semántica exhaustiva por nodeid de la ruta activa**, no resuelta por contar 35 fichas de frontera.
- [ ] **S5-T2-06 — Independencia de oráculos A-03, ensayos de sensibilidad C**, aún pendientes.
- [ ] **S5-T2-07 — Completar clasificación de tests no pertinentes a la ruta activa**, incluidos legacy y científicos, sin certificar GT.
- [ ] **A01-S5 y A-01 globales cerrados** — NO. A-05 también pendiente.

**Siguiente acción:** consolidar la trazabilidad de la **ruta activa por familias de test**, después auditar independencia de oráculos (A-03). Evitar que ampliar la cantidad de fichas reemplace la evaluación de si un test protege un contrato.

## 7. Foreground/CLI — sensibilidad focal preparada después de A-03 (2026-11-16)

**Motivo de prioridad:** TR-031 ya identifica \`tests/integration/test_b03_foreground_pdf_product.py\` como test del **coordinador real** \`run_admitted_pdf\` con \`_ingest\`, \`_run_g3\`, \`_run_g5\` y \`_read_status\` falsos. Su oráculo sí debe proteger el límite operativo G3/G5: **nunca continuar al ensamblado tras G3 incompleto y nunca declarar éxito sin PDF publicado**. No es ni se promoverá a E2E OCR→G3→G5.

**Fuentes existentes auditadas:** \`apps/cli/pdf_product.py\` comprueba \`_require_state(doc, "READY_FOR_ASSEMBLY")\` antes de lanzar G5, y exige \`_verify_published_pdf\` antes de devolver \`PDFProductResult\`. Las pruebas ya presentes:
- \`test_foreground_fails_on_incomplete_g3_before_g5\`: fake deja FSM en \`PROCESSING\`, espera \`PDFProductError/STAGE_NOT_COMPLETE\` y \`events=["OCR","G3"]\`.
- \`test_foreground_fails_when_g5_did_not_publish\`: fake G5 marca \`COMPLETED\` sin crear PDF; espera \`PDFProductError/WITHOUT_PUBLISHED_PDF\` y \`events=["OCR","G3","G5"]\`.

Se reutilizaron **los dos tests originales y sus aserciones**, sin editar SUT ni fixtures. Se preparó [\`probe_foreground_sensitivity.py\`](probe_foreground_sensitivity.py) y bandera \`-CheckForegroundSensitivity\` del runner aislado. Primero se ejecutan esos **dos nodeids** sin mutar y solo con \`pytest exit=0\` se lanzan dos procesos Python con parches efímeros:

| Control | Violación del SUT in-memory | Detector previsto |
|---|---|---|
| **FG-NEG-01** | \`_require_state\` informa falsamente \`READY_FOR_ASSEMBLY\` aunque el estado real tras G3 es \`PROCESSING\` | \`test_foreground_fails_on_incomplete_g3_before_g5\` falla por \`Failed: DID NOT RAISE\` (G5 ya se habría invocado) |
| **FG-NEG-02** | \`_verify_published_pdf\` devuelve \`PDFProductResult(COMPLETED)\` aun sin PDF final | \`test_foreground_fails_when_g5_did_not_publish\` falla por \`Failed: DID NOT RAISE\` |

Cada hijo requiere **exit 1, exactamente \`1 failed\`, marcador \`DID NOT RAISE\`** y ausencia de errores de colección/internos. Reporta \`foreground_mutation_summary.json\` más dos tracebacks individuales. No se cambia runtime/CI/GT ni se requiere Docker. El clon sin hardlinks no es sandbox OS; la comprobación Git post detecta solo cambios persistentes en ese clon.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckForegroundSensitivity
\`\`\`

**Estado:** implementación del falsador, **ninguna baseline nueva ni mutation kills FG acreditados aún**. La evidencia A-03 anterior está en [informe G3-B3 §8](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md): **39 PASS en el mismo SHA y TWO_KILLED inspeccionados directamente desde \`reports.rar\`**, con \`status_changes.txt\` vacío. La colección global A-01 de **1.476 nodeids** corresponde al SHA \`5447963d\`; el test multibyte añadido posteriormente exige nueva colección en otro hito, no reinterpretar el censo antiguo. A/B/C generales, A-05/06 y CI siguen abiertos.

## 8. Admisión PDF/CLI — contratos existentes y dos falsadores preparados (2026-11-16)

**Evidencia de fuente sobre el HEAD de esta preparación, no ejecución dinámica:** revisión de \`apps/cli/pdf_inbox.py\`, \`apps/cli/main.py\` y \`tests/integration/test_pdf_inbox_submission.py\`. Ya existen **ocho tests nominales**, con \`pytestmark=integration\`: SHA-256 sobre bytes admitidos, idempotencia de entrada, colisión con contenido distinto, extensión no PDF, fuente vacía, prohibición de fallback no atómico, no selección de R1 y rechazo de \`--job-id\` heredado. Todos usan \`tmp_path\` y PDF de texto sintético \`fitz\`; no usan DB, proveedor ni Tectonic.

**Contrato real:** \`submit_pdf_to_inbox\` publica por \`os.link\` de un temporal \`.pdf-admission-*.partial\` en el mismo volumen; si no es posible publicar atómicamente debe elevar \`PDF_INBOX_ATOMIC_PUBLISH_UNAVAILABLE\`, sin reemplazar el destino. La CLI \`handle_translate\`, en modo admisión sin \`--run\`, **no** llama \`handle_translate_async\` (compatibilidad R1 deshabilitada); el nombre no convierte ese test en ruta OCR→G3→G5 ejecutada.

La nueva herramienta [\`probe_cli_admission_sensitivity.py\`](probe_cli_admission_sensitivity.py) y el selector \`-CheckCLIAdmissionSensitivity\` reutilizan **todos los ocho tests originales**, sin cambiarlos. Después de una baseline verde, lanzan un proceso Python por mutación transitoria:

| Control | Mutación SUT en memoria | Testigo / razón esperada |
|---|---|---|
| **CLI-NEG-01** | \`submit_pdf_to_inbox\` acepta una **copia final no atómica** tras error de \`os.link\` | \`test_no_nonatomic_fallback_if_hard_links_unavailable\`: \`Failed: DID NOT RAISE\` (debería rechazar) |
| **CLI-NEG-02** | \`handle_translate\` llama \`handle_translate_async\` legado antes de efectuar admisión | \`test_cli_translate_never_invokes_legacy_r1_pipeline\`: sentinel \`AssertionError: R1 must not execute\` |

El helper comprueba para cada mutación exit 1, \`1 failed\`, marcador contractual y ausencia de \`ERROR collecting\`/\`INTERNALERROR\`, registrando \`cli_admission_mutation_summary.json\` y los dos logs individuales. **Sin ejecución: no declarar KILLED todavía.**

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckCLIAdmissionSensitivity
\`\`\`

La selección se realiza en clon independiente, sin hardlinks ni remoto, con HOME/TEMP apartados y inventarios Git. No es aislamiento de SO, ni evita todo efecto transitorio fuera del clon; **no** ejecutar suite \`not e2e\` en working tree. No se ha modificado runtime/CI, fixtures científicas ni Ground Truth. A/B/C global, A-05 y CI pendiente.

## 9. FG-NEG-01/02 — evidencia directa completada desde RAR (2026-11-16)

El owner volvió a adjuntar \`reports.rar\`; se inspeccionaron directamente sus **seis miembros** (RAR5): \`pytest_focal.log\`, \`summary.txt\`, \`foreground_mutation_summary.json\`, \`foreground_mutation_foreground_incomplete_g3.log\`, \`foreground_mutation_foreground_missing_pdf.log\` y \`status_changes.txt\` vacío. El SHA reportado es **\`e2d2fd5f64165357b8c9e2dbf25f23139a04c351\`**, correspondiente a una corrida ya registrada por JSON. Esta ampliación **no constituye una segunda corrida distinta**.

| Control | Evidencia observada | Decisión focal |
|---|---|---|
| Baseline sin mutación | \`.. [100%]\`, **\`2 passed in 0.62s\`**, \`pytest_exit_code=0\` | PASS para dos casos del coordinador en ese SHA |
| **FG-NEG-01** G3 incompleto | \`test_foreground_fails_on_incomplete_g3_before_g5\`, línea 88: \`Failed: DID NOT RAISE <class 'apps.cli.pdf_product.PDFProductError'>\`; **\`1 failed in 0.64s\`**, exit 1 | **MUTATION_KILLED**, causa contractual confirmada directamente |
| **FG-NEG-02** PDF ausente | \`test_foreground_fails_when_g5_did_not_publish\`, línea 95: \`Failed: DID NOT RAISE <class 'apps.cli.pdf_product.PDFProductError'>\`; **\`1 failed in 0.69s\`**, exit 1 | **MUTATION_KILLED**, causa contractual confirmada directamente |
| Verificador/integridad | \`verdict=TWO_KILLED\`, \`sensitivity_exit_code=0\`, \`status_changes.txt\` **0 bytes**, \`docker_used=false\` | Sin diferencias Git persistentes en el clon; no implica aislamiento OS |

**Corrección de alcance histórico:** §7 describía los falsadores como preparados, y el primer reporte del owner solo permitió confirmar el JSON. Ahora constan ambos tracebacks y el inventario Git. Los dos falsadores son resultados de **una única ejecución** en el SHA citado, no cuatro kills. El coordinador \`run_admitted_pdf\` es real, pero OCR/G3/G5 siguen simulados: **no se ha acreditado E2E PDF→PDF, seguridad de ejecución a nivel SO, CI ni Ground Truth**. Los gates generales A/B/C permanecen abiertos.
