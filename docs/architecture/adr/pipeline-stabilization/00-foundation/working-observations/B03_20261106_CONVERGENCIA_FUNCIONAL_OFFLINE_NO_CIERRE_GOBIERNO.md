# B03 — Observación post-corte de continuidad PDF→PDF con proveedor controlado

**Fecha de la observación:** 2026-11-06.
**Estado:** WORKING OBSERVATION / NON-NORMATIVE / NO CIERRE.
**Procedencia:** transcripciones PowerShell comunicadas por el owner, comprobación visual comunicada por el owner y código consultable en Git. No constituye auditoría independiente de los archivos temporales de Docker.
**Código versionado:** `pipeline_stabilization`, commit `f6d258e87cc7479b55c0354bae71db5d37597611` (contiene el commit base `e70adc72e3182cc14faf386c2f50e53a3839906c` y la corrección B03.2.4 de `APP_ROOT`).
**Sujeto de ejecución:** laboratorio `apps.lab.offline_pdf_lab`, `--run-smoke` y `--run-pdf`; no es Compose base ni concurrencia productiva.

## 1. Alcance del recorrido integrado

El adaptador `apps/cli/main.py translate --run` admite el PDF usando SHA-256 e inbox y ejecuta en primer plano los componentes existentes: OCR Router → Layout/AST/ChunkPlan → `runtime.engine` G3 → materialización → G5 Assembler/Tectonic → PDF y FSM. En ausencia de `--run`, la CLI conserva el contrato de solo admisión. El laboratorio monta el checkout solo lectura en `/workspace`, separa escritura en `/app/data`, `/app/state`, `/app/output` y caché, usa `--network none` y un fake Groq accesible solo por loopback. No se infiere equivalencia de R1, R3, Compose base o recuperación entre procesos por el uso de una secuencia en primer plano.

Imagen Docker fijada por ID `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`. Se sembraron selectivamente 294 archivos Tectonic y 1 archivo tiktoken procedentes de G4; no se restauraron DB, AST, PDFs ni volúmenes históricos.

## 2. Caso A — smoke sintético completado

- Pruebas comunicadas tras B03.2.4: `34 passed, 2 warnings`. Las advertencias son de dependencias deprecadas y soporte futuro, no de ejecución del pipeline.
- Comando: `python -m apps.lab.offline_pdf_lab --run-smoke`.
- Log: `B032_PREFLIGHT_OK`, bootstrap de cuatro bases SQLite, `B032_FAKE_READY_LOOPBACK_OFFLINE`, OCR con dos unidades, FSM `CREATED → PARSING → PROCESSING → READY_FOR_ASSEMBLY`, petición HTTP 200 al fake, `G5_ASSEMBLER_PDF_PUBLISHED`, `FSM COMPLETED` y `B032_OPERATIONAL_PASS`.
- Entrada sintética: `document_id=42f2605e5f3257f3b7cb4f7e1c2d879f030cf5758122bd84c5a21d9563aa6469`. AST comunicado: `71e7f0e971b4942779dd9ba9bf22bd9a9bdc3fa7769451e60e83aac1868cf54c`.
- `B032_VERIFIED_COMPLETE` registró `requests=1`. La salida publicada se exportó con nombre `OFFLINE_FAKE_translated_42f2605e5f3257f3b7cb4f7e1c2d879f030cf5758122bd84c5a21d9563aa6469.pdf` en `Downloads/translator_pdf_offline`.
- El owner abrió la salida y comunicó texto legible en inglés, con división silábica LaTeX. No se obtuvo en esta revisión SHA-256 del PDF final ni se inspeccionaron sus bytes de manera independiente.
- Dictamen restringido: `OPERATIONAL_PDF_PUBLISHED = DEMONSTRATED_BY_OWNER_TRACE`; `LINGUISTIC_TRANSLATION = NOT_EVALUABLE_FAKE_ECHO`; `SCIENTIFIC_FIDELITY = NOT_CERTIFIED`.

## 3. Caso B — documento de corpus detenido explícitamente

- Comando comunicado: `python -m apps.lab.offline_pdf_lab --run-pdf "C:\\Users\\Admin\\Desktop\\Proyectos\\translator_pdf\\[Amoretal_2023]_3hojas.pdf"`.
- El archivo es la misma entidad Git blob que `tests/corpus/canonical/pdf/doc_02_double.pdf` y `tests/fixtures/sample_3_pages.pdf` en el corte `e70adc7`; tamaño Git: 2.045.076 bytes. `document_id` reportado: `84891f98114b90a7b8b80eee46d5de9990707046b8cea29affb3536da51a3123`.
- El OCR Router detuvo extracción en la página 1 con `B02_UNREPRESENTED_VECTOR_DRAWING`, porque la ruta actual no representa trazos vectoriales en Layout/AST. La CLI informó posteriormente `PDF_RUN_OCR_NO_FSM_STATE`; este mensaje secundario no reemplaza la causa primaria.
- G3 y G5 `NOT_REACHED`; no hubo PDF publicado. La guarda es `fail-closed`; no implica recuperación ni conservación completa de fórmulas/figuras.
- Dictamen restringido: `EXTRACTION_COVERAGE = BLOCKED_BY_EXPLICIT_VECTOR_GUARD`; `PRODUCT_PDF = NOT_PUBLISHED`.

## 4. Reconciliación con D-1/D-2 y gates del Candidate v0.2.1

| Gate | Delta observado | Reserva que permanece |
|---|---|---|
| G-1 / D-1 | Conexión funcional CLI → OCR → G3 → G5 sin traductor alternativo en `--run`. | Dirección viable; aprobación del Board pendiente; no equivale a despliegue canónico. |
| G-2 / D-2 | R2/G3→G5 recibe un nuevo testigo de PDF físico. | Referencia técnica condicional, no elección normativa; el Charter DRAFT mantiene su inclinación histórica hasta decisión explícita. |
| G-3 | FSM y PDF coherentes en este caso aislado. | F18-02/03/04/05, CP-08, efectos inciertos, fencing, recuperación y concurrencia no acreditados globalmente. |
| G-4 | Smoke y STOP como nuevos testigos acotados. | No sustituyen W-06…W-10 ni E2E-0 preregistrado sobre corpus designado. |
| G-5 | Entrega física visible y fallo de cobertura transparente. | Traducción real, integridad científica, vectores, cobertura de corpus y garantías de producto pendientes. |

El `execution_outcome=A` y `scientific_verdict=FAIL` de C/L1 R2 histórico pertenecen al sujeto fechado 2026-11-03; no se reescriben ni se transfieren automáticamente a estas ejecuciones B03. El smoke usa un PDF sintético, no un PDF del corpus preregistrado por el Charter; el ensayo Amor, si bien usa un PDF del corpus, se detuvo antes de G3. No se declara cumplimiento del procedimiento completo de E2E-0.

## 5. Decisión operativa y control documental

**Resultado del hito técnico:** `RUTA_INTEGRADA_FUNCIONAL_OFFLINE = DEMOSTRADA EN LABORATORIO PARA EL SMOKE COMPATIBLE`.

**No cierres:** `D1_D2_BOARD_DECISION = PENDING`; `F18_INTEGRAL = NOT_DEMONSTRATED`; `PRODUCT_READINESS = NOT_DEMONSTRATED`; `LANGUAGE_TRANSLATION = FAKE_ECHO`; `MATH_AND_VECTOR_PRESERVATION = OPEN`.

Actualizar Atlas (adenda), Decision Candidate (adenda) y guía de sandbox (variante) preservando sus cortes y estados. No alterar ni ratificar tácitamente Charter, NADR/ADR FROZEN, actas de cierre anteriores, oráculos sellados, F18.2 o repositorio `main`. Un voto D-1/D-2, un presupuesto de proveedor real, la aceptación científica y las remediaciones de autoridad requieren sus actos específicos.

**Custodia pendiente:** archivos PDF y hashes del run, logs primarios/fingerprints completos de entorno, pruebas interproceso y del corpus representativo. Las rutas temporales comunicadas no constituyen una evidencia de conservación universal.
