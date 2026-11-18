# TST-STAB — Evidencia condensada de remediación de tests

> **Propósito:** cómo se hicieron las correcciones y con qué evidencia se aceptaron; complemento del [plan y acta de cierre técnico](PLAN_REMEDIACION_TESTS_PIPELINE.md).
> **Estado:** documentación retrospectiva del alcance técnico, **no** nueva ejecución de tests, certificado OS, CV científico ni producto listo.
> **Fuentes originales preservadas por historial Git:** [árbol histórico SHA `5e897fdbdd2b4d17d2d668f31863caa9c04fb393`](https://github.com/RDsanchez-git/translator_pdf/tree/5e897fdbdd2b4d17d2d668f31863caa9c04fb393/docs/architecture/adr/tests_stabilization/).
> **Criterio de lectura:** distinguir lectura de fuente (F), baseline positiva (E), mutación intencional detectada (K), sensibilidad `NOT_RUN` y alcance excluido (X).

## 1. Trazabilidad y cómo reproducir el juicio

La comparación de `tests_stabilization` contra `main@83ef0257f795f0d973f9393cc225e7af5b956ade` antes de compactar detectó **73 archivos: 21 tests modificados + 52 incorporaciones en documentación/herramientas TST-STAB; cero cambios en SUT, CI, GT o corpus**. La compactación retiene **exactamente los 21 archivos de tests**, reemplaza el expediente por **dos Markdown**, y retira **50 archivos auxiliares** de la carpeta.

- **SHA antes de compactar:** `5e897fdbdd2b4d17d2d668f31863caa9c04fb393`. Es un ancestro, **no la revisión contra la que se ejecutó el CI técnico**.
- **PR técnico final validado:** [#63](https://github.com/RDsanchez-git/translator_pdf/pull/63), HEAD de código/tests `428330317edcbc584ef834d3e81946c9ef361926`, merge probado `0798f7f99663b79123e225132fea1385df9f285a`.
- **Técnica de validación:** no se crea una K por fallo de import ni por excepción genérica; se exige rechazo, ausencia de escritura, estado durable o efecto prohibido que falle **por causa del contrato**. K de diferentes SHA no constituyen una sola corrida.
- **Expedientes previos no presentes en el árbol integrado:** permanecen en el historial anclado por SHA. Citar el blob/commit histórico cuando se necesiten las trazas completas.
- Los scripts `probe_*`, `run_b05_focal_isolated.ps1`, `collect_a01_isolated.py`, `preflight_a06_guest.py` y similares se usaron para diagnóstico en clones aislados; **no forman parte del producto ni del workflow actual**. Retirarlos del árbol no afecta selección `pytest`, que apunta a `tests/`.

## 2. Inventario exacto de los 21 archivos de tests modificados

La tabla dice **qué garantía es apropiado atribuir al cambio**, sin confundir nombres históricos con E2E científico. Se puede verificar cada archivo en `tests/` y su historia contra `main`.

| Archivo de test | Corrección / revisión efectuada | Límite explícito |
|---|---|---|
| `integration/test_chunker_snapshot.py` | Se retiró el snapshot autoescribible como autoridad; controles literales de miembros, orden, política y bytes de fuente sobre AST sintético. | No GT de traducción; no todos los campos del plan. |
| `integration/test_e2e_walking_skeleton.py` | Se acotó a contrato de caché/consumidor legacy y hit observable, evitando un E2E nominal falso. | No OCR→PDF real; fake permitido. |
| `integration/test_embedding_smoke.py` | Opt-in explícito para transporte Groq real y prueba de no-construcción con opt-in desactivado. | Prueba real SKIP sin credencial/opt-in. |
| `integration/test_g3_b3_structured_result_contract.py` | Borde de cuota en **bytes UTF-8** y negativos de bindings; respuesta G3-B3 con razones de rechazo. | No sensible a toda identidad ni K específico B3-08. |
| `integration/test_g3_b4_3a_engine_staging.py` | Rechazos precisos de salida/binding antes de staging/receipt. | Proveedor mock, no publicación global. |
| `integration/test_g5_assembler_lease_recovery.py` | Ajustes focales de tipado/contrato de lease en SQLite temporal y ausencia de PDF prohibido. | Sin multihost ni Tectonic real. |
| `integration/test_golden_parser.py` | Eliminado esperado circular/mock de parser; PDF descartable, extracción real y frase independiente verificable. | Extracción PDF→AST, no traducción científica. |
| `integration/test_healing_e2e_telemetry.py` | Nombres y docstrings ajustados a healing/telemetría que efectivamente ejercen. | Healing local, no E2E integral. |
| `integration/test_pipeline_orchestration.py` | Se explicita handoff del orquestador legacy con parser simulado. | No ruta operativa G3/G5 completa. |
| `integration/test_real_e2e.py` | Clase FinOps renombrada a `TestMockedFinOpsConsumerContract` y alcance mock documentado; aserciones conservadas. | No producción PDF→PDF; selector #63 verde, log `-q` sin PASS nominal por nodeid. |
| `integration/test_real_parser_pipeline.py` | Prueba real de parser mediante PDF temporal con textos literales e identidad estable. | No compila ni traduce PDF. |
| `integration/test_recovery_flow.py` | Aislamiento de efectos de recuperación legacy con rutas/DB temporales y parches acotados. | Final de pipeline simulado. |
| `integration/test_translation_layer.py` | Fixtures/control de I/O y estado local más seguro para el test de traducción legacy. | Dispatch/proveedores dobles, no G3 físico. |
| `integration/test_translation_structure.py` | Ajustes focales de fixtures/entorno y alcance de estructura legacy. | Golden/fixtures no certifican ciencia. |
| `integration/test_translation_technical.py` | Ajustes focales de fixtures/entorno y verificación técnica legacy. | Fórmulas y estructura, no calidad semántica. |
| `integration/test_verification_pipeline_connection.py` | Parser de composición productiva con PDF de texto descartable; prueba vector no representable falla cerrada. | No sustituye CV sellada/corpus canónico. |
| `integration/test_w06_g3_uncertain_effect_offline.py` | Aserciones del estado `G3_EXTERNAL_UNKNOWN` y no reintento de efecto incierto. | Se observa `accepted_calls` del fake, no proveedor HTTP real. |
| `test_pipeline_fidelity.py` | Nombre acotado a protección de matemáticas y restauración de tokens, no fidelidad científica. | Sin métricas lingüísticas ni PDF final. |
| `unit/test_b031_g3_reusable_fake.py` | Fake HTTP de uso reutilizable acotado a loopback y límites de prueba. | No control de egress global OS. |
| `unit/test_semantic_chunker.py` | Docstring/contratos de continuidad y orden; conservación byte-exact se acredita por B-02. | No duplicar afirmación de sensibilidad. |
| `unit/test_tectonic_runner.py` | Aislamiento del CWD/archivos temporales y efectos del runner Tectonic en test. | Binario invocado/errores bajo dobles; no CV científica. |

**Interpretación:** cambios de denominación/fixtures no tienen por qué aumentar cantidad de tests; un contrato previamente tautológico sí requiere reemplazo causal. El selector actual y los SHAs de controles focales son evidencia, no el número bruto de aserciones.

## 3. Ruta crítica: ocho fronteras y sus oráculos

| Frontera | Testigo causal existente | E/K acreditada en subcontrato | Limitación conocida |
|---|---|---|---|
| **1. B02 parser PDF→AST** | `test_golden_parser.py`; `test_verification_pipeline_connection.py`; `test_real_parser_pipeline.py`: frase literal y rechazo vectorial. | E focal, K de pérdida de texto. | OCR/PDF final científico X. |
| **2. AST/chunk plan/W08** | `test_chunker_snapshot.py`, `test_w08_durable_context_boundary.py`, G3-B3: source bytes, identidad y 0 escrituras ante plan inválido. | E focal, K de pérdida de bytes de fuente. | `MF-B3-03` y todas las identidades W08/manifest K=NOT_RUN. |
| **3. G3 efecto incierto** | `test_w06_g3_uncertain_effect_offline.py`: proveedor fake contado, `G3_EXTERNAL_UNKNOWN` no puede reenviar. | E + K C-03 de segundo envío. | No exactamente una vez HTTP real. |
| **4. G3 publicación/proyección** | `test_g3_b4_3b_publication_recovery.py`: proyección corrupta no avanza FSM; SQLite durable. | E + K C-04 de drift. | No todos los receipts/CAS. |
| **5. FSM/lease/recovery** | `test_g5_assembler_lease_recovery.py`, `test_c3_t05_process_boundary.py`: lease/epoch y crash/reopen. | E + K C-05 de lease vencido. | No clúster multi-host. |
| **6. G5 worker y PDF** | `test_g5_assembler_worker_integration.py`: método de worker real con compiler/renderer fake, fallo persistido. | E + 2 K G5W. | No Tectonic/maquetación real. |
| **7. Foreground/CLI** | `test_pdf_inbox_submission.py`, `test_w08_cli_foreground_single_generation_offline.py`: sin fallback/R1/falso éxito. | E + 2 K CLI + 2 K FG. | No cadena OCR→G3→PDF real. |
| **8. Puerto externo / fake proveedor** | `SyncProviderBridge`, cuotas SQLite, G3-B3: bytes UTF-8, restricciones de aceptación y no retry. | E + K UTF-8; comparte C-03 con frontera 3 (no duplicar). | Egress OS/proveedor pagado no ensayados. |

**No significa que las ocho fronteras tengan K universales.** En la matriz histórica se evaluaron 35 TR: **7 confiables solo en su subcontrato, 28 LIMITADO**, no 28 fallos. El inventario inicial tiene **1.476 nodeids únicos en 173 archivos**, posteriores **1.478 en CI #293**; 36 archivos técnicos compartidos suman **165 nodeids** clasificados en cinco grupos, con **20 variantes materiales y 8 expansiones del backend**. La clasificación no es certificación por nodeid.

## 4. Los 15 mutantes focales reportados como detectados

**Todos son tests de sensibilidad en entornos controlados; ninguno demuestra que se haya encontrado un bug productivo nuevo.** Evitar sumar dos veces K de una misma frontera.

| Grupo (cantidad) | Mutación inoculada / oráculo que la detectó | Evidencia histórica / límite |
|---|---|---|
| **B-05 (2)** | Watchdog/caché toleran efectos persistentes incorrectos; fallan checks de estado y cache real. | SHA `ffd70253`, expediente A-05. Solo ese I/O. |
| **B-01/B-02 (2)** | `parser_text_loss` y `chunk_source_byte_loss` producen ausencia de frase o alteración de espacio fuente. | SHA `5a537c9512b8ec1cb37dd2ac0022587daccf0d0d`; causas `B01_KNOWN_SOURCE_TEXT_MISSING` y `B02_SOURCE_BYTES_MISMATCH`. |
| **G3/G5 C-03/C-04/C-05 (3)** | Retry tras timeout aceptado, drift de proyección omitido y publicación con lease vencido. | SHA `16a68229`; segundo `accepted_calls`, `DID NOT RAISE` drift, PDF prohibido. |
| **A-03 (2)** | Cuota de JSON en caracteres en vez de bytes UTF-8; parser pierde frase de fuente. | SHA `83f99ddb`; fallos específicos de cuota y `B02_EXTRACTED_SOURCE_TEXT_MISSING`. |
| **Foreground (2)** | Se informa éxito con G3 incompleto o PDF inexistente. | `FG-NEG-01/02`; tracés en segunda tanda histórica. |
| **CLI (2)** | Admisión usa fallback no atómico o acepta ruta R1 prohibida. | `CLI-NEG-01/02`; dos tracebacks verificados históricamente. |
| **G5 worker (2)** | Lease vencido publica PDF o fallo de compilación no deja `FAILED_RETRYABLE`. | SHA `97a1bbef`; `G5W-NEG-01/02`, fallo contractual específico. |
| **Total** | **15 K focales** | No significa 15 K en una sola ejecución ni 15 garantías P0 universales. |

**NOT_RUN que no se promueven:** `MF-B3-03` (B3-08 `DUPLICATE_MEMBER`, test PASS sin falsador específico), toda la cadena C-02 plan→no publicación, varios campos W08/manifest/receipts/CAS/epoch y degradación parcial G5. Se evaluarán **solo** si aparece una obligación P0 concreta que los requiera.

## 5. Seguridad A-05/P4/P6 y remediación de efectos

| Riesgo observado | Acción/fuente | Lo que permite y lo que NO permite concluir |
|---|---|---|
| Test legacy de recuperación con DB/rutas de trabajo | DB temporal y monkeypatch acotado; tests en clon descartable. | Sin efectos persistentes observados sobre checkout protegido; no monitoreo de todo I/O externo. |
| Caché SQLite y creación implícita de ficheros | Fixtures/DB bajo directorio temporal, hit real observado. | Cierra riesgo focal, no todas las escrituras de child processes. |
| Hypothesis escribe `.hypothesis` al importar | Primer clon reveló 271 artefactos ignorados; redirección a scratch y revalidación limpia. | Lección de seguridad de plugins, no certificación de cero escritura OS. |
| Proveedor Groq | Opt-in `TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=1` **y** clave real requeridos; no activados en CI. | Smoke live SKIP; sin llamadas pagadas acreditadas por esa prueba, no prohibición OS de otras. |
| Archivos protegidos | Focales en clones aislados; 30 hashes SHA-256 iguales antes/después, Git limpio. | **Integridad persistente observada**, no detector crear→borrar o egress de red. |
| Runner GitHub Actions | `ubuntu-latest` hospedado y descartable; owner confirmó `GITHUB_TOKEN` default read-only. | **Criterio operativo proporcional aceptado**; `permissions:` / secretos administrativos no auditados completamente, cero egress no demostrado. |

**Decisión:** nunca correr suite global sobre checkout personal para acreditar esta campaña; no exigir Docker/firewall/VM/tracing por estética, pero sí controles adicionales si el entorno futuro tiene secretos reales, runner self-hosted sensible o un objetivo explícito de `NO_EGRESS_OS`. A05-P4/P6 y C08 **abiertos físicamente**.

## 6. CI técnico actual y Continuous Verification separada

| Ejecución | Resultado verificable | Lectura correcta |
|---|---|---|
| [PR #63](https://github.com/RDsanchez-git/translator_pdf/pull/63), [CI #293](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44207210090) | Merge sintético `0798f7f99663b79123e225132fea1385df9f285a`; Pyright/import-linter **SUCCESS**; unit **225 PASS**; marker integration **72 PASS**; pasos focales B03 **33**, W06/G3 **70**, W08 **13+16**, G3/G5 **6**; `not e2e` **1.454 PASS / 4 SKIP / 20 deselected / 3 warnings**. | Los pasos solapan casos; no sumar 225+72+138+1454 como total único. La línea `-q` no identifica por nombre cada PASS. |
| [PR #62](https://github.com/RDsanchez-git/translator_pdf/pull/62), [CI #292](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44005819069) | También SUCCESS técnico, antes de último rename FinOps. | Histórico; no sustituye revisión del último candidato. |
| [CV #47](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44207209078) | SMOKE **FAIL** `BASELINE_INTEGRITY_FAILURE` exit 3 por **15 PDFs `doc_08..doc_22`** faltantes; controles de no modificación de corpus/oráculos PASS; FULL SKIPPED en PR. | Ciencia **sin métricas** y D-5 diferido; fallo anterior al PR, no regresión técnica nueva. |

**Cuatro SKIP técnicos:** opt-in Groq real deshabilitado y tres moldes legacy semántico/estructural/técnico ausentes. No se reemplazan con fixtures sintéticos para obtener PASS engañoso.

## 7. Archivo histórico y referencias primarias

Se retiraron del **árbol** los 34 Markdown históricos restantes y los 17 scripts auxiliares; no se reescribió su contenido ni su historial. Se pueden consultar en el [árbol original fijado en el SHA anterior a la compactación](https://github.com/RDsanchez-git/translator_pdf/tree/5e897fdbdd2b4d17d2d668f31863caa9c04fb393/docs/architecture/adr/tests_stabilization/). Ese SHA es un ancestro de `tests_stabilization` mientras se conserve la rama, incluso después de squash a `main`.

| Fuente histórica bajo `docs/architecture/adr/tests_stabilization/` | Para qué sirve si se necesita una auditoría detallada |
|---|---|
| `A00_BASELINE_INVENTARIO_Y_RIESGOS.md` | Situación inicial, riesgos y sujeto de auditoría. |
| `A01_COLECCION_PYTEST_2026-11-15.md` y `A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md` | Colección, nodeids y diferencias de parametrización por SHA. |
| `A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md` | Las 35 fichas TR y su clasificación; puente hacia 1.476 nodeids. |
| `A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md` | B3-01…B3-33, causas de rechazo y oráculos. |
| `A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md` | Ocho fronteras, testigos G3/G5 y K C-03/04/05. |
| `A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md` | TS-001/002, B01/B02, dos K focales. |
| `A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md` | UTF-8, parser, 39 PASS y dos falsadores A03. |
| `A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md` | FG/CLI/G5W K, fragilidades y testigos C3/T05. |
| `A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md` | P4/P6, scripts de ejecución aislada, mitigaciones de SQLite/CWD y límites OS. |
| `A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md` | Sobrepromesas E2E, B03/B04, 8 PASS de scopes ajustados. |

**Trazabilidad operativa final:** contrastar un contrato con el **test actual**, después el [PR #63](https://github.com/RDsanchez-git/translator_pdf/pull/63) y sus jobs, y solo si se necesita reproducir una decisión histórica abrir el expediente del SHA anterior. Un enlace a un expediente borrado sin SHA es inválido; los documentos finales no lo usan.

## 8. Criterios de conservación para futuros refactors

- Si el contrato observable cambia legítimamente, versionar la decisión/ADR antes de actualizar un expected.
- Si un test pasa por un mock o fixture, declararlo; probar el método real solamente donde su comportamiento sea la garantía.
- Una K vale por su mutación exacta y SHA, no por compartir nombre de frontera.
- Reutilizar las barreras focales en el PR correspondiente; no agregar 1.478 fichas, 28 mutantes ni otra campaña por etiquetas `LIMITADO`.
- `main` debe incorporar únicamente **los 21 tests y estos dos documentos**: ningún script histórico de investigación, cambio de runtime, workflow, corpus ni GT.
