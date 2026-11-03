# I0-1E — Acta de evaluación final y cierre técnico acotado aceptado

**Corte local:** 2026-11-01 (Argentina, UTC−03:00). **Última ejecución:** 2026-11-02T01:13:58Z (identidad de corrida E3-S01).  
**Versión:** v1.0.0 — acta aceptada, derivada de la propuesta v0.1. **Estado del documento:** `CIERRE_TECNICO_ACOTADO_ACEPTADO_POR_EL_OWNER — PUBLICACION_GIT_PENDIENTE`.  
**Dictamen técnico aceptado:** `I0-1E_EVALUADO_EN_ALCANCE_ACOTADO_CON_RESERVAS_Y_NO_CONFORMIDAD_DOCUMENTAL`; **no** `PASS` irrestricto, certificación de producción ni aprobación del Architecture Board.  
**Sujeto de código:** `d4cda2c379c0efd93a70e795d31c37a0ede7a192`.  
**Imagen R2:** `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`.  
**Composición histórica D2-12:** SHA-256 `c8397cb6dd23666252b1d2b80d9b0bdd2b41eb911ecb816c7af34d0ea0f1db16`.  
**No se modificaron** con este documento el Atlas, Charter, el código, el corpus ni los expedientes de origen.

## 1. Autoridad, objetivo y límite del cierre

Esta acta aplica **exclusivamente al plan I0-1E acordado**: **E0**, reconciliación documental del sujeto y sandbox; **E1**, controles instrumentales del Audit Sandbox; **E2**, validación del PDF físico; **E3**, pruebas funcionales/de integración *pertinentes* y acotadas; y decisión documental de cierre. No sustituye el propósito forense más amplio de `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` ni convierte las propuestas del `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` (DRAFT) en decisiones FROZEN. No selecciona unilateralmente ruta productiva canónica ni modifica el cierre limitado previamente aceptado de I0-1D.

**Modalidad probatoria:** resultados comunicados por el operador desde PowerShell/Windows; lectura en esta conversación de los documentos/instrumentos locales y del PDF R2 recibido; lectura estática del código Git del HEAD para los tests E3. **No** se leyeron directamente desde este entorno el `RESULTADO_E1_S02.json`, `pytest_e3s01.log` o el recibo JSON E3 alojados en el PC del operador. Los hashes transcritos son anclas para cotejos posteriores, no una alegación de firma digital o validación independiente del contenido no recibido.

## 2. Matriz ejecutiva del plan acordado

| Etapa | Evidencia y resultado | Adjudicación acotada | Lo que NO acredita |
|---|---|---|---|
| **E0: corpus + sujeto R2** | HEAD fijado. Manifiesto canónico v3.9: **21/21 PDFs SHA correctos**, cero ausentes/divergentes; 21/21 GT JSON legibles, cero extras. `manifest.json` local diferente **solo por fin de línea**, conservado sin modificación. Identidad del laboratorio R2, Compose, recibos, PDF y seis backups individuales cotejados. | `PASS_LIMITED_REVIEW` | Integridad científica del contenido de cada GT, regresión topológica completa, atomicidad global entre seis DB. |
| **E1: seguridad del Audit Sandbox** | S01: **5/5** contenedores `exited`, **6/6** volúmenes privados, cero host binds escribibles, cero puertos publicados, red interna efectiva, UID 10001 en servicios productivos; `db_bootstrap` con root. S02: sonda nueva pasa negativas de red/escritura y control positivo `/tmp`, con recursos históricos preservados. | `E1_PASS_LIMITED_CON_RESERVAS` | Política universal de egress/IPv6; equivalencia con cinco servicios simultáneos; ausencia de todas las rutas de escritura o secretos. |
| **E2: PDF físico** | PDF R2 SHA `bcbe29a7963f312fbdf9e783b94785eee1e4d2936967556fbda0156dae18dafd`; **20.902 bytes, cuatro páginas, 4/4 renderizadas, 1/1 fuentes embebidas, sin reparación**. `/OpenAction` resultó destino interno `/Fit`, no JavaScript. | `E2_01_PASS_PHYSICAL_STRUCTURE_LIMITED` | Traducción real ni fidelidad científica del artefacto final. |
| **E2: observación documental adicional** | Comparación original→R2 identifica pérdida **visible** de notación en ecuaciones (1.1)–(1.4) y degradación de layout. El laboratorio declara `synthetic_copy_only_not_translation`: inglés remanente no implica fallo de proveedor real. | **`E2_02_MATH_PRESERVATION_FAIL_OBSERVED`**, preservación científica `NOT_ACREDITED` | No se infiere qué componente causó la pérdida; no se inició depuración causal. |
| **E3: pruebas focalizadas** | E3-S00: 152 módulos versionados, 55 en integración, 31 candidatos nominales; selección reducida a 4 módulos y 6 nodos de prueba. E3-S01 exportó snapshot del HEAD fuera de Git y obtuvo **8 passed, 2 warnings in 9.08s**, `pytest exit 0`; sin Docker/Groq/corpus. | **`E3_PASS_8_CASES_OFFLINE_LIMITED`** | Toda la suite de integración, recuperación real tras SIGKILL, traducción real, invariantes globales. |

## 3. E3-S01 — recibo comunicado y cobertura específica

**Identidad:** `i01e-e3s01-20261102T011358Z-86bcffc`; Python/pytest disponible: pytest **9.0.3**. Preflight `CHECK_PASS_NO_MUTATIONS`, exit 0; ejecución con autorización exacta, `ISOLATED_RUN`, `E3_S01_RUN_EXIT: 0`. Snapshot: `git archive HEAD` de allowlist fija y extracción controlada a directorio fuera del repositorio. `E3_S01_ARCHIVE_SHA256: 167ef151d9e43ad06671b13ba18d546d6fec6032741a489e78f138f5f2662a96`. Guardia de conexiones *Python socket* habilitada: protección limitada, **no** denegación universal por firewall.

**Los seis nodos seleccionados** (ocho instancias de pytest porque `PRESERVE` tiene tres modos):

1. `tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py::test_scheduler_repeated_queries_do_not_detach_factory_alias` — contrato SQLite de alias/ATTACH.
2. `tests/integration/test_g3_b4_3b_publication_recovery.py::test_crash_after_publication_replays_without_reinference` — replay de publicación en DB descartables.
3. `tests/integration/test_g3_b4_3b_publication_recovery.py::test_engine_recovery_never_initializes_provider` — recuperación sin inicializar proveedor pagado.
4. `tests/integration/test_g3_b4_8_preserve_engine.py::test_engine_preserve_provider_decision_and_full_publication` — **tres variantes** (`preserve_only`, `translated_already_staged`, `mixed_runnable`).
5. `tests/integration/test_g5_assembler_lease_recovery.py::test_expired_lease_old_worker_cannot_publish_even_without_takeover` — fencing de lease expirado.
6. `tests/integration/test_g5_assembler_lease_recovery.py::test_full_pdf_promoted_before_db_commit_is_recoverable` — ventana simulada entre promoción de PDF y commit DB.

**Salida:** `E3_S01_PYTEST_EXIT: 0`; `E3_S01_PYTEST_SUMMARY: 8 passed, 2 warnings in 9.08s`; `E3_S01_GATE: PASS_8_CASES_OFFLINE_LIMITED`; `E3_S01_RUN_EXIT: 0`. El testimonio de origen indica `E3_S01_ORIGINAL_REPO_NO_GIT_WRITE: YES`, `NO_DOCKER_NO_PROVIDER_NO_CANONICAL_CORPUS: YES`.

**Advertencias:** se comunicaron **dos warnings de pytest**, sin sus tipos ni mensajes. No se los denomina inocuos ni errores de producto; su clasificación queda `WARNING_DETAILS_NOT_REVIEWED`. Son compatibles con exit 0 y ocho pruebas aprobadas, pero permanecen como reserva de observabilidad si el owner decide hacer un cotejo documental de **logs ya existentes**; **no requieren repetir automáticamente la ejecución**.

**Anclas del expediente E3:** `E3_S01_LOG_SHA256: 11f7064ddf732164a73f2737130cd961a72f7d15b703a57a34e85b512760724c`; `E3_S01_RECEIPT_SHA256: a92cdb075d77ed76ed18ad6b83bb7336758ec842da764092571dcc5183cb69ec`; `E3_S01_EVIDENCE_FOLDER: i01e-e3s01-20261102T011358Z-86bcffc`. La fuente primaria sigue en custodia local del owner; esta acta no ha recibido el log completo ni el JSON para rehash directo.

**No duplicación:** las 42 integraciones, 233 pruebas dirigidas y 149 unitarias del commit aislado histórico `0caececb346a07b1cd6e241c45ab6ce33fa619b9` no se suman a los ocho como pruebas nuevas distintas. Se verificó coincidencia de blobs en módulos seleccionados y partes relevantes del Engine/Assembler entre ese commit y el HEAD; no implica identidad de cada dependencia. En el CI del PR #26 el job `integration-tests` quedó `SKIPPED` al depender del gate científico, no `PASS`. La nueva corrida E3 sí ejerce **los ocho casos concretos** en el snapshot del HEAD integrado.

## 4. Riesgos y obligaciones residuales — no extrapolar el cierre

| ID / dimensión | Situación al cierre aceptado | Tratamiento |
|---|---|---|
| **E2-02 — matemáticas/layout** | **No conformidad observada** en PDF R2 producido con fake; la estructura física pasó, no la fidelidad STEM. | Conservar hallazgo y evidencia visual; estudiar causas y remediación en trabajo gobernado posterior, no introducir como gate causal nuevo de I0-1E. No declarar aptitud científica. |
| **E1 — egress/escritura global** | S01 probó inspección estática efectiva del histórico; S02 una variante de sonda con dos destinos TCP y testigo RO. | `PASS_LIMITED`, sin alegar aislamiento exhaustivo de cinco servicios, ni control de IPv6/universal. |
| **E3 — dos warnings** | Contenido no recibido; pytest exit 0. | `WARNING_DETAILS_NOT_REVIEWED`; revisión posterior solo de evidencia conservada si hace falta, sin repetir. |
| **CI científico / corpus en CI** | Local: 21 PDFs y 21 GT disponibles. CI histórico: baseline incompleta en runner (15 PDFs ausentes), regresión `BASELINE_INTEGRITY_FAILURE` y job de integración `SKIPPED`. | No declarar Continuous Verification PASS ni integración CI completa. Provisión controlada del corpus y gate independiente pendientes. |
| **Recuperación / persistencia** | Casos sintéticos y SQLite aislados cubiertos parcialmente; no se observaron nuevas corridas SIGKILL en R2. | `FAILED_RETRYABLE`, ventana real PDF/SQL, W04/R3, W06/R1 y W07/caché relativa siguen pendientes; no atribuir los testigos históricos a R2. |
| **Proveedor y calidad** | Fake determinista probó transporte/procesamiento limitado; no hubo Groq real ni evaluación lingüística. | No promover a producción ni reclamar traducción científica real. Requiere autorización separada, política FinOps y criterios aplicables. |
| **I0-1F — supply chain** | R2 es build incremental local; no reconstrucción fría portátil/SBOM completos. | Mantener en I0-1F, sin adelantar cierre. |
| **Custodia de laboratorios** | Históricos D2-12 y sonda E1-S02 conservados; E3-S01 exportó su propio snapshot/recibo fuera de Git. | No ejecutar `rm`, `prune`, `compose down -v`, reinicios o limpieza de expedientes; cualquier retirada posterior requiere acto específico. |

## 5. Decisión aceptada y sucesión

**Decisión del owner (comunicada expresamente en esta conversación, 2026-11-01, zona local de Argentina):** «Acepto el cierre técnico acotado de I0-1E, manteniendo expresamente las reservas y el hallazgo E2-02».

**Adjudicación:** queda **aceptado el cierre técnico acotado de I0-1E**, con el dictamen `I0-1E_EVALUADO_EN_ALCANCE_ACOTADO_CON_RESERVAS_Y_NO_CONFORMIDAD_DOCUMENTAL`. Se consideran completados **exclusivamente los cuatro carriles E0–E3 pactados** en sus alcances probatorios identificados en §§2–4; no se requiere repetir tests para validar esta aceptación documental. La aceptación **no elimina** la no conformidad E2-02, **no** convierte `E1_PASS_LIMITED` ni `E3_PASS_8_CASES_OFFLINE_LIMITED` en PASS global y **no** certifica fidelidad científica, seguridad universal, traducción real o aptitud productiva.

**Hallazgo conservado sin modificar:** `E2_02_MATH_PRESERVATION_FAIL_OBSERVED` — degradación matemática visible en ecuaciones (1.1)–(1.4) del PDF producido con proveedor sintético. La localización causal y cualquier remediación quedan fuera del alcance del cierre aceptado, sin ocultar el fallo. También permanecen expresas las reservas sobre egress/IPv6, permisos en conjunto multiservicio, dos warnings E3 sin texto revisado, CI científico pendiente, recuperación/SIGKILL real de R2, W04/R3, W06/R1, W07/caché y build portátil/SBOM.

**Autoridad y límites:** aceptación técnica del owner; **no** firma digital, aprobación del Architecture Board, cambio de categoría normativa del Charter `DRAFT`, selección de ruta canónica, ni autorización para nuevas pruebas. No se han ejecutado desde este documento comandos de `git add`, `commit`, `push`, ni se ha editado el Atlas, Charter, código, corpus, logs, recibos o historia.

**Publicación pendiente:** el archivo Markdown aceptado queda listo para incorporación editorial posterior, mediante decisión y procedimiento de Git específicos; **la publicación no es un requisito para reconocer esta aceptación técnica local**. Conservar sin alteración la propuesta v0.1 como antecesor documental y los expedientes S01/S02/E3 como fuentes primarias.

**Continuidad:** I0-1D conserva su cierre limitado aprobado; I0-1E queda **cerrado técnicamente en alcance acotado con reservas y E2-02 registrado**; I0-1F (reproducibilidad/portabilidad, procedencia y SBOM) sigue pendiente y requiere sus propios controles y autorización. Las investigaciones científicas, funcionales y forenses que exceden este cierre no se consideran resueltas.

## 6. Cadena de evidencias y custodia

Referencias locales de apoyo: `I0-1E_E0_ACTA_INVENTARIO_CORPUS_Y_TRANSICION_E1_20261101.md`; `I0-1E_E0_DICTAMEN_DOCUMENTAL_SANDBOX_R2_Y_E2_01_20261101.md`; `I0-1E_E1_CIERRE_ACOTADO_Y_E3_APERTURA_20261101.md`; `I0-1E_E2_01_ACTA_ESTRUCTURA_PDF_R2_20261101.md`; `I0-1E_E2_02_COMPARACION_PDF_R2_20261101/I0-1E_E2_02_ACTA_COMPARACION_DOCUMENTAL_R2_20261101.md`; `I0-1E_E3_S00_DICTAMEN_SELECCION_Y_E3_S01_CONTRATO_20261101.md`; `I0-1D_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_2026-10-31.md` y los recibos/logs primarios custodiados en Windows.

**No se borran ni reescriben fuentes históricas.** Esta acta de aceptación es un nuevo documento derivado de la propuesta y no reemplaza la evidencia originaria ni acredita una firma digital. La propuesta v0.1 debe permanecer inalterada; el SHA-256 de esta copia sirve como ancla de integridad.
