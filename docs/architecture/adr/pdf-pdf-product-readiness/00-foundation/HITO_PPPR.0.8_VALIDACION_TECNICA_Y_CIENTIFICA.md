# HITO_PPPR.0.8_VALIDACION_TECNICA_Y_CIENTIFICA.md

**Estado:** IN_PROGRESS v1.0.1  
**Fecha de apertura:** 2026-11-20  
**Congelamiento:** N/A  
**Tipo:** Forensic Flow Audit — verificación técnica, regresión topológica y validación científica de PDF→PDF  
**Iniciativa:** PPPR Fase 0; **no** fase nueva del roadmap ni campaña de certificación  
**Baseline de código observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@17b5d2026212501f4129b59864fe2a4606c663c5` (PPPR.0.1–0.7 FROZEN)  
**Jerarquía:** `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN > `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN, `PROJECT_SCOPE`/principios, D-1/D-2, PPPR FROZEN, NADR compatibles según ámbito.  
**Ruta real:** CLI → OCR Router → G3 (`runtime/engine.py`) → G5 (`apps/compiler/__main__.py`) → PDF. Atlas `pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` v1.0.2: mapa descriptivo AS-IMPLEMENTED del corte `6818e86`, **no** autoridad normativa principal.  
**Modo de trabajo:** lectura de código, YAML, tests, actas, manifiestos y oráculos *solo como texto*. **NOT_RUN** — no proveedor, Docker, Tectonic, pytest, modificación de corpus, SQLite de usuario ni inferencias científicas certificantes.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-20 | Apertura: 25 evidencias estáticas, cuatro familias de testigos, censo del corpus v3.9 (21 GT/6 PDF versionados, 15 faltantes, issue #34), preflight/certificación existente, frontera extraction-only versus PDF→PDF completo, 8 hipótesis iniciales, 5 DQ y 4 DC provisionales. Sin GAP local confirmado, sin ejecución ni FROZEN. |

| 1.0.1-IN_PROGRESS | 2026-11-20 | Segunda pasada: 45 E-IDs (todos P2), matriz de productores/consumidores/oráculos, 8 hipótesis clasificadas parcialmente, 6 DQ y 4 DC. Preflight separado con tensión normativa R7(d) en verificación; CV extracción ≠ certificación PDF EN→ES; SemanticJudge y benchmark A/B históricos no son gates de producción. Sin nuevos GAP OPEN, sin tests ni FROZEN. |

## 1. RESUMEN EJECUTIVO

La verificación debe responder **qué componente y sujeto reales cubren los testigos** y **qué prueba falta para afirmar fidelidad científica de un traductor EN→ES** sin inventar umbrales, oráculos o motores. El código contiene un sistema consolidado de regresión/certificación de **extracción topológica PDF→AST**, y también testigos operacionales OCR→G3→G5 con proveedor fake; estos mecanismos son reutilizables dentro de su contrato, pero **no prueban de manera acumulativa** que un PDF traducido conserve ecuaciones, tablas, figuras, layout y significado lingüístico en condiciones reales.

**Bloqueo heredado inequívoco:** `tests/corpus/canonical/manifest.json` v3.9 registra 21 documentos y 21 Ground Truth sellados, pero el árbol Git solo contiene seis PDFs canónicos. Los 15 `doc_08…doc_22` faltantes ya se documentaron en **issue #34 OPEN** y en el handoff de CI; `run_regression.py` verifica materialización completa e integridad física **antes** del filtrado de perfiles SMOKE/FULL. No reabrirlo ni resolverlo mediante corpus sintético, descarte de casos o alteración de hash/GT. Su materialización precisa custodia y autorización.

**Diferencia de sujeto:** `tools/evaluation/run_regression.py::run_evaluation` utiliza `build_extraction_pipeline` y compara `runtime_ast` contra oráculos topológicos de origen; no llama G3 ni G5. `NADR-F17BIS-25` está **FROZEN** para el sujeto canónico **de extracción** que definía Fase 6; no universalizar su declaración al producto convergido OCR→G3→G5 sin decisión y evidencia nueva. `core/benchmark/certification/` implementa las capas de estado y precondiciones, pero la existencia del módulo no demuestra una certificación productiva ejecutada.

**Límites:** los PASS de TST-STAB PR #63, C2/T07 PR #46 y demás CI se atribuyen a sus commits, oráculos y fronteras exactos. Tests con `real` en el nombre pueden ser mocks; PDF con cabecera `%PDF-` o FSM `COMPLETED` no significa fidelidad científica. **No se acredita `PRODUCT_READINESS=PASS`.**

## 2. LÍMITE EPISTEMOLÓGICO, AUTORIDAD Y SEGURIDAD

- **Observed:** código actual de verificación, manifest/corpus en el árbol, tests y actas existentes; no inspección del Windows del propietario ni acceso a los 15 PDFs privados.
- **Required:** `PROJECT_SCOPE.md` exige preservación matemática, técnica y estructural; `ENGINEERING_PRINCIPLES.md` rechaza falsos PASS y degradación silenciosa; la auditoría debe distinguir evidencia del parser, del modelo, del PDF final y del corpus.
- **Decision:** solo EN→ES por ahora (owner); proveedor/modelo nuevo pendiente en PPPR.0.4. D-1/D-2 es único root seleccionado; no reactivar legacy R1/R3 ni una arquitectura de certificación paralela.
- **F17-BIS:** NADR-25/26 figuran **FROZEN** y sus contratos de verificación/integridad son útiles en la frontera original; el mandato actual de traducción completa no estaba acreditado por esa fase. F17BIS-06 **PROPOSED** no es autoridad automática. No se exige que un CV extraction-only sea un E2E G3/G5 solo por renombrar el producto.
- **Prohibido:** copiar, descargar, alterar, reconstruir o transmitir PDFs canónicos/GT o materializar `doc_08…doc_22` sin permiso explícito; no crear oráculos propios a partir del candidato, no relajar baseline, no publicar originales sujetos a copyright, no habilitar proveedor de pago ni LLM-judge por presunción.
- **Límite de prueba:** `NOT_RUN` significa que en este HITO se leyeron testigos. PASS históricos de PR #46/#63 tienen commit/fecha/alcance distintos. `NO VERIFICABLE` debe incluir razón/no-bloqueo/destino (§8.2).

## 3. INVENTARIO DE FRENTES DE VERIFICACIÓN

| Frontera | Archivos representativos | Estado inicial |
|---|---|---|
| Baseline canónica y custodias | `tests/corpus/canonical/{manifest.json,ground_truth/,pdf/}`, issue #34 | **AUDITADO** a nivel de árbol/manifiesto; bytes privados **NO DISPONIBLES** |
| Dataset de calibración y workload | `tests/corpus/calibration_v1/{manifest.json,pdf/,ground_truth/}`; `tests/corpus/workload/{pdf/,ground_truth/}` | **REFERENCIADO / CENSADO**; no equivalencia automática con baseline canónica |
| Regresión/extracción | `tools/evaluation/run_regression.py`, `apps/bootstrap/pipeline_factory.py`, `core/benchmark/topology/regression/` | **AUDITADO focal** — extracción, no G3/G5 |
| Integridad/GT sellado | `core/benchmark/{corpus/integrity,ground_truth/{completeness,validity,identity},topology/regression/adapter}.py` | **AUDITADO focal** |
| Certificación (dominio y CLI) | `core/benchmark/certification/{contract,preflight,evidence,post_run}.py`, `tools/evaluation/preflight_certification.py` | **AUDITADO focal**; no ejecución |
| Verificación CI | `.github/workflows/{ci,continuous-verification}.yml`, `core/benchmark/verification/` | **AUDITADO** por config/testigos |
| Convergencia OCR/G3/G5 | `docs/.../pipeline-stabilization/handoff/{EVIDENCIA_Y_CIERRE,LABORATORIO_Y_REPRODUCCION,ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF}.md` | **REFERENCIADO histórico con fake** |
| Tests técnicos con falsadores | `docs/.../tests_stabilization/{PLAN_REMEDIACION_TESTS_PIPELINE,EVIDENCIA_REMEDIACIONES_TESTS}.md`, tests integrados | **REFERENCIADO por alcances**, tests **NOT_RUN** |
| Testigos focales PDF/G5 | `tests/integration/{test_b03_foreground_pdf_product,test_b024_g3_g5_math_roundtrip,test_real_paper,test_real_e2e}.py` | **AUDITADO focal** (mock, math delimitada, entrada real opt-in, legacy) |
| Traducción lingüística real EN→ES / proveedor | `runtime/engine.py`, PPPR.0.4 FROZEN, tests fake/legacy | **NO VERIFICABLE** sin backend, evaluación/oráculo y autorización |
| Calidad del PDF físico/layout/figuras | `apps/compiler/tectonic_runner.py`, `core/compiler/rendering/`, PPPR.0.6 FROZEN | **NO VERIFICABLE** sin fuentes/outputs y evaluación física autorizada |
| Seguridad/recuperación y coste en host | PPPR.0.5/0.7 FROZEN, TST-STAB | **REFERENCIADO**, no duplicar auditoría ya cerrada |

## 4. FUENTES Y PRECEDENCIA

**Fuentes del product SUT:** `main@1d21cfe`, Atlas D-1/D-2 (solo DESCRIPTIVO), `PROJECT_SCOPE`/principios y PPPR.0.1–0.7 FROZEN. **Instrumental de verificación:** `tools/evaluation/run_regression.py`, `core/benchmark/{topology,corpus,ground_truth,verification,certification}`, workflows CI, tests y documentación TST-STAB. **Normas heredadas compatibles:** `NADR-F17BIS-25` (FROZEN, sujeto de extracción en Fase 6) y `NADR-F17BIS-26` (FROZEN, integridad baseline); no extender sin cotejar contratos. **Evidencia histórica:** C0–C4, DoD 9/9 con fake PR #46; TST-STAB PR #63 / #64, CI #293. **Dependencia de corpus:** issue #34 OPEN, sin autorización para repartir/mutar originales.

**Regla:** no equivocar **sujeto de prueba** (extraction-only o PDF→PDF completo), **oráculo** (AST de fuente, GT lingüístico, referencia visual), **mecanismo** (topología, juez, comparación física) y **reporte** (PASS contractual, test mock, estado FSM o resultado científico). La compatibilidad del contrato de F17-BIS se analiza como frontera, no como validación automática de PPPR.

## 5. FLUJO DE VERIFICACIÓN EVIDENCIADO

```text
A) CURRENT CI / REGRESIÓN TOPOLOGÍA — sujeto EXTRACTION-ONLY
   CI (main, pipeline_stabilization; PR #66 interno no dispara CV)
      -> tools.evaluation.run_regression
         -> corpus manifest v3.9 (21 IDs)
         -> [Gate previo] materialización 21 PDFs + SHA + GT sellados
            NO PASA con checkout Git de 6 PDFs (issue #34)
         -> perfil SMOKE/FULL tras gate íntegro
         -> build_extraction_pipeline().parse(PDF origen) -> Candidate AST
         -> Sealed Oracle AST -> RegressionEvaluationStrategy
         -> informe topológico y severidad / veredicto de regresión
   No llama G3, traducción, G5 ni compara PDF final EN→ES.

B) CONVERGENCIA OPERATIVA HISTÓRICA — fake
   CLI -> OCR -> G3 SyncProviderBridge(fake) -> G5 Tectonic -> PDF
   C2: físico PDF y FSM/receipts; sin proveedor comercial ni GT científico.

C) PRODUCTO OBJETIVO — PROPIEDADES AÚN NO CERTIFICADAS
   Inglés PDF origen -> OCR/AST -> G3 EN→ES real -> G5 PDF español
   [A] estructura matemática/técnica intacta y rechazos representables
   [B] calidad lingüística en→es y corrección terminológica
   [C] preservación de figuras/tablas/jerarquía y PDF visual/semántico
   [D] integridad/custodia de baseline, perfiles y provenance
   [E] operación real, coste/quotas, determinismo de reportes y rollback
   Preguntas de contrato -> ADR Maestro/Execution Plan; testigos físicos
   solo con autorización, no una nueva suite completa por reflejo.
```

## 6. MATRIZ DE PRODUCTORES, CONSUMIDORES Y GARANTÍAS (SEGUNDA PASADA)

| Mecanismo / composition root | Input real y sujeto | Productor y salida verificable | Consumidor observado / destino | Qué **NO** acredita |
|---|---|---|---|---|
| **CI Continuous Verification** — `.github/workflows/continuous-verification.yml` → `tools/evaluation/run_regression.py` | Manifest canónico + PDFs originales íntegros + GT topológico sellado; `build_extraction_pipeline().parse` | `RegressionReport` y `ContinuousVerificationReport` con `IdentityChain`, cobertura, outcome, PDF-source/AST-metrics; JSON y MD según resultado | GitHub workflow SMOKE/FULL sobre ramas configuradas, salida en `reports/continuous-verification*` | No G3/G5, traducción, PDF de salida ni validación humana; 15 PDFs faltantes impiden ejecución íntegra en checkout |
| **PREFLIGHT de certificación** — `tools/evaluation/preflight_certification.py` | Manifest, lista de GT, campo sealed, configuración y freeze/provenance `reports/calibration`; CLI explícita | `PreflightReport` de ocho condiciones; imprime éxito/error, exit 0/no-0 | `evaluate_preflight` puro; `__main__` permite invocación independiente. **No se encontró invocación de esta CLI** en CV ni en las raíces D-1/D-2 inspeccionadas | Que los hashes de GT fueron recalculados; que el certificado completo fue compuesto o que un corpus PDF final pasó |
| **Dominio de certificación** — `core/benchmark/certification/{contract,evidence,post_run}.py` | Estados `ExecutionOutcome`/`ScientificResult`, identidades y resultados que **deben ser aportados** por un caller | `CertificationStatus` puro, serializador determinista de `CertificationEvidence`, verificador de postcondiciones `PostRunReport` | Consumidores explícitos inspeccionados: tests unitarios de contrato/evidencia; no aparecen en el armado de `ContinuousVerificationReport` ni en CLI PDF→PDF | `post_run.is_pass` no es aceptación científica; no demuestra `CERTIFIED` sobre PDF final |
| **Regresión topológica** — `RegressionAdapter`, `RegressionEvaluationStrategy` | AST extracción de PDF fuente + oráculo sellado de fuente | Identidad/hash de oráculo y métricas topológicas graduadas | `tools.evaluation.run_regression._run_evaluation` | Fidelidad lingüística, semántica de traducción o maquetación en español |
| **Benchmark A/B histórico** — `apps/benchmark/__main__.py` → `SequentialBenchmarkOrchestrator` | Parser `build_extraction_pipeline()` sobre PDF hardcodeado por cwd; `TranslationUnit` ad hoc; dos GroqBenchmarkRunner | `BenchmarkRunReport`, telemetría, métricas de tokens/latencia/coste y proxies sintácticos | Herramienta de laboratorio, `BenchmarkPersistenceGateway` y telemetría; tests de orquestador usan mocks | No usa el plan durable OCR→G3→G5 ni GT lingüístico independiente o PDF físico G5 |
| **Juez semántico por LLM** — `core/benchmark/semantic_judge.py` | `source_text` y `target_text` enviados a API Groq | `ChunkEvaluationScore` (terminology, fluency, structure, fidelity, defectos); agregación configurable | No se halló invocación desde `apps/benchmark/__main__.py`, `runtime/engine.py` o CV inspeccionados. Otros consumidores externos: **UNKNOWN** | Rúbrica/LLM-judge no equivale a Ground Truth humano, evaluación independiente ni permiso de egress de texto privado |
| **Ruta productiva seleccionada** — CLI→OCR→G3→G5 | PDF en inglés, AST/manifest y snapshots/receipts, proveedor real a decidir | PDF traducido y FSM/publicación físicos cuando se ejecuta | CLI, G3, G5; testigo histórico C2 usa fake | Ningún `CertificationEvidence` ni `ScientificResult.ACCEPTED` fue observado como salida conectada de esa ruta |

**Reconciliación normativa:** NADR-F17BIS-23/24/25/26/29/30 tienen ciclo `FROZEN` en sus archivos: se aplican **en sus fronteras históricas explícitas**, sin sustituir por inferencia el sujeto elegido D-1/D-2. La regla positiva reutilizable es no aceptar una certificación sin sujeto preciso, corpus/GT íntegros, provenance, salida científica independiente y barrera de integración evidenciable. La política actual de calibración vacía en el shell preflight está documentada como decisión de Fase 5, **no** es prueba de partición independiente ni por sí sola una violación ejecutada.

### 6.1 Tensión concreta de PRE-FLIGHT: `oracle_hash` (mantener visible)

**Observed** — `tools/evaluation/preflight_certification.py::main` construye `oracle_violations` solo cuando `doc.oracle_hash` falta; hace biyección por nombres de ficheros, pero **no carga ni calcula en esa CLI el hash semántico** de los GT. `evaluate_preflight` procesa los errores inyectados sin I/O. Aun con un GT cuyo contenido haya variado, la condición denominada `ORACLE_HASHES_VERIFIABLE` puede quedar vacía si el manifiesto conserva un hash no vacío. **Esto es una limitación demostrada del alcance de ese preflight**, no una ejecución con GT corrupto.

**Required** — `NADR-F17-BIS-24` v1.2.0 **FROZEN**, §5.2 R6–R8 obliga a comprobar durante PREFLIGHT que los `oracle_hash` sean *verificables*. El **otro** camino, `RegressionAdapter.verify_oracle_integrity`, sí calcula y compara la identidad cuando se procesa un documento en `_run_evaluation`; no equivale a que el preflight independiente la calcule.

**Decision pendiente** — determinar si esa CLI es parte del **gate de certificación que hoy está realmente conectado** o permanece como tooling auxiliar heredado; ninguno de los entrypoints seleccionados ni el CV examinado la invocan. **OBS de correspondencia normativa P2 / H-0.8-D / DQ-0.8-06**, no P1 del producto por traslado de una ruta legacy. Si se aprueba usar ese preflight como condición de certificado, se deberá reconciliar el requisito R7(d), el consumidor y la consecuencia **antes** de acreditarlo como PASS. No ejecutar ni mutar un GT para fabricar prueba.

## 10. REGISTRO DE EVIDENCIAS — PRIMERA Y SEGUNDA PASADA (NO FROZEN)

| E-ID | Sev. inicial | Observed (archivo::símbolo o dato versionado) | Contrato/limitación precisa | Disposición |
|---|---|---|---|---|
| **E-0.8-001** | P2 | `tests/corpus/canonical/manifest.json` v3.9 declara **21 documentos** con `sha256`, `oracle_hash` y `ground_truth_state=sealed`; el árbol contiene 21 GT JSON. | Declaración de oráculo ≠ comprobación ejecutada de hash en filesystem ni acceso al PDF original. | BASELINE DECLARADA |
| **E-0.8-002** | P2 | Solo **6 PDFs** aparecen en `tests/corpus/canonical/pdf`; faltan los 15 IDs `doc_08…doc_22` del manifest. | **Issue #34 OPEN** contiene la misma observación y exige materialización privada autorizada; no reabrir ni añadir clones sintéticos. | DEPENDENCIA HEREDADA |
| **E-0.8-003** | P2 | `tools/evaluation/run_regression.py::main` invoca `verify_baseline_materialized` y `verify_baseline_physical_integrity` antes de `get_profile_document_ids`/ejecución; inspecciona manifiesto y GT. | SMOKE no puede seleccionar solo seis para evitar precondición de 21; ausencia → fallo de integridad, no PASS científico. | FAIL-CLOSED |
| **E-0.8-004** | P2 | `core/benchmark/corpus/integrity.py` coteja manifest_hash y PDF SHA físico; `ground_truth/completeness.py` exige biyección de IDs del manifest con artefactos/PDFs. | Se verifica integridad de fuentes cuando los archivos existen, no corrección del resultado traducido. | CONTRATO DE DATOS |
| **E-0.8-005** | P2 | `core/benchmark/topology/regression/adapter.py` verifica ID del oráculo, hash semántico, sealed y completitud; `ground_truth/validity.py` valida estructura mínima. | Integridad de **oráculo topológico**, no oráculo humano EN→ES ni salida G5. | REUSO FOCAL |
| **E-0.8-006** | P2 | `tools/evaluation/run_regression.py::run_evaluation` usa `build_extraction_pipeline()`, `parse(pdf)` y `RegressionEvaluationStrategy.evaluate_regression(ground_truth_ast=oracle.nodes)`. | **Subject solo PDF→AST**; sin llamada a `runtime.engine` G3, `CompilationService` o Tectonic. NADR-F17BIS-25 FROZEN se limita a ese sujeto histórico. | FRONTERA PPPR |
| **E-0.8-007** | P2 | `core/benchmark/certification/contract.py` distingue `ExecutionOutcome`, `ScientificResult`, `CertificationStatus`; `CERTIFIED` requiere ejecución exitosa, aceptación científica, evidencia completa e invariantes. | Capacidad existente del dominio; ninguna instancia CERTIFIED del producto se acreditó en este HITO. | REUSO/NO PASS |
| **E-0.8-008** | P2 | `certification/preflight.py::evaluate_preflight` enumera condiciones de corpus identidad, manifiesto válido, GT sellado, hash, configuración canónica, parámetros congelados, provenance y particiones sin leakage. | Función pura; sus tests con argumentos controlados no prueban que estas precondiciones estén satisfechas en el corpus actual. | REUSO/NO PASS |
| **E-0.8-009** | P2 | `certification/evidence.py::CertificationEvidence` y `post_run.py::validate_post_run` requieren identidades y resultados por documento biyectivos más provenance. | Integridad formal del reporte, no certeza sobre el sujeto G3/G5 ni validez de traducción sin oráculo. | REUSO/NO PASS |
| **E-0.8-010** | P2 | `tests/corpus/calibration_v1/manifest.json` lista cinco documentos, con los **mismos SHA de origen para doc_01…doc_05** del canon v3.9; estos cinco PDFs están versionados en calibración. | Identidades físicas compartidas no autorizan reutilizar particiones como independientes; si certificación exige disyunción, seleccionar partitions por SHA y provenance. No afirmar fuga en un run no ejecutado. | DEPENDENCIA DE IDENTIDAD |
| **E-0.8-011** | P2 | `tests/corpus/workload/pdf/` contiene cinco PDFs y cinco GT bajo workload, sin `manifest.json` en ese directorio del HEAD. | No elevar workload a baseline canónica sellada ni suponer que sustituye al corpus protegido; metadatos/procedencia por decidir. | DATASET DIFERENTE |
| **E-0.8-012** | P2 | `.github/workflows/continuous-verification.yml` ejecuta `tools.evaluation.run_regression` SMOKE en PR a `main`/`pipeline_stabilization`, FULL en push a main/dispatch. | Workflow no cubre PR interno a `pdf-pdf-product-readiness` ni ejecuta por sí mismo G3/G5; ausencia de check ≠ FAIL ni PASS. | CI / TRIGGER |
| **E-0.8-013** | P2 | `.github/workflows/ci.yml` ejecuta static/unit/integration y tests técnicos con fake; perfiles científicos corren en workflow separado. | PASS técnico de tests no equivale a resultado científico PDF traducido. | CI / LIMITES |
| **E-0.8-014** | P2 | `docs/.../tests_stabilization/EVIDENCIA_REMEDIACIONES_TESTS.md` acredita PR #63 CI #293: `not e2e` **1454 PASS / 4 SKIP / 20 deselected** y campañas focales, con tests limitados por alcance. | Evidencia histórica del sujeto y SHA de PR #63, no CI actual reejecutado ni validación científica de inglés→español. | TST-STAB NO REGRESIÓN |
| **E-0.8-015** | P2 | `tests/integration/test_real_e2e.py` se declara explícitamente *Legacy FinOps consumer shape contract*; mock de `TranslationPipeline.execute`, sin PDF de salida. | Nombre de test **no** implica E2E real; tras TST-STAB ya fue corregido el scope. | FALSA GARANTÍA EVITADA |
| **E-0.8-016** | P2 | `tests/integration/test_b03_foreground_pdf_product.py` usa orquestación OCR/G3/G5 monkeypatch y escribe bytes PDF simulados; comprueba transiciones y `scientific_status=NOT_CERTIFIED`. | Útil para contrato foreground, no traducción real, compilación física o layout STEM. | TESTIGO TÉCNICO |
| **E-0.8-017** | P2 | `tests/integration/test_b024_g3_g5_math_roundtrip.py` protege/restaura delimitadores matemáticos sobre texto con `InlineMathProtector` y `TextRenderStrategy`. | Bytes de spans matemáticos explícitos, no interpretación científica, validación visual ni PDF compilado. | TESTIGO TÉCNICO |
| **E-0.8-018** | P2 | `tests/integration/test_real_paper.py` está marcado `e2e`, opt-in `TEST_REAL_PDF_PATH`, evalúa extracción/AST y puede rechazar vectores no representables. | Ni el PDF privado autorizado ni los resultados reales se inspeccionaron; no prueba G3/G5 ni justifica sustituir un paper físico por fixture. | OPT-IN NO VERIFICABLE |
| **E-0.8-019** | P2 | `tests/integration/test_translation_semantics.py` instancia `core/pipeline/orchestrator.TranslationPipeline` legacy con `FakeChunker`, `FakeDispatcher` y similitud simulada. | No es juicio humano ni calidad lingüística EN→ES de `runtime/engine.py`. | LEGACY/FALSE CLAIM |
| **E-0.8-020** | P2 | Acta `EVIDENCIA_Y_CIERRE.md` C2, PR #46: OCR→G3→G5 produjo PDF Tectonic físico de 7050 bytes y un POST HTTP al fake; C3/T07 mismo tamaño PDF, SHA distinto. | Evidencia **operacional histórica** con identidad de commit; no PDF traducido con modelo vigente, ni oráculo STEM. | CONVERGENCIA CON FAKE |
| **E-0.8-021** | P2 | Atlas registra `%PDF-`/FSM `COMPLETED` como verificación de publicación operativa y `NOT_CERTIFIED` científico en foreground. | Cabecera válida ≠ semántica STEM/EN→ES, ni resultado de percepción visual. | G5/PRODUCT BOUNDARY |
| **E-0.8-022** | P2 | `NADR-F17BIS-25` metadata dice `FROZEN` y define sujeto normativo de Continuous Verification como composición de **extracción** `build_extraction_pipeline`, Candidate AST. | Norma histórica FROZEN aplicable a su frontera: no declarar que CV extracción es CV end-to-end del nuevo producto. Extensión de alcance es cuestión del ADR Maestro, no GAP por salto temporal. | AUTORIDAD ACOTADA |
| **E-0.8-023** | P2 | `NADR-F17BIS-26` metadata `FROZEN` exige corpus íntegro, hash por PDF y baseline materializada antes de evaluar. `tools/evaluation/run_regression.py` falla cerrado si no se cumple. | Requisito vigente dentro de regresión canónica; **issue #34** ya contiene el bloqueo físico. No degradar el contrato para conseguir verde. | AUTORIDAD REUSABLE |
| **E-0.8-024** | P2 | `core/benchmark/quality.py::StructuralQualityEvaluator` contabiliza fiabilidad operacional, proxy de densidad de tokens y checks de sintaxis Markdown/LaTeX por registro. | **Proxies técnicos**, no juicio de significado traducido, invariancia matemática o similitud visual de PDFs. | MÉTRICAS CON ALCANCE |
| **E-0.8-025** | P2 | `PROJECT_SCOPE.md` §4 requiere conservar fórmulas, código y estructura; PPPR.0.2/0.3/0.4/0.5/0.6/0.7 contienen GAPs, DQ y restricciones anteriores sin resolución productiva. | No cerrar esas obligaciones por PASS de extracción ni abrir P1 redundante sin prueba de una frontera nueva. La evaluación científica real todavía exige criterio/oráculo autorizado. | INTERDEPENDENCIAS |

| **E-0.8-026** | P2 | `tools/evaluation/preflight_certification.py::main` chequea campo `doc.oracle_hash` no vacío y lista IDs GT vía `LocalFileSystemGroundTruthArtifactAdapter`, pero no carga/calcula SHA del contenido GT. | `NADR-F17-BIS-24` FROZEN R7(d) pide hashes verificables **en PREFLIGHT**; tensión normativa local del subtool, no incidente de producto ejecutado. | OBS PRE-FLIGHT / DQ-06 |
| **E-0.8-027** | P2 | `certification/preflight.py::evaluate_preflight` solo consume `oracle_hash_violations` inyectadas y marca `is_pass` si no hay violaciones. | El core puro no puede subsanar la ausencia de verificación en el shell; evitar atribuirle I/O no programado. | PRODUCTOR CONDICIONAL |
| **E-0.8-028** | P2 | `tools/evaluation/preflight_certification.py` se ejecuta por `__main__` y produce `[PREFLIGHT] All 8 conditions satisfied`; no hay llamada a esa CLI desde `run_regression.py`/CI ni D-1/D-2 inspeccionados. | Capacidad auxiliar invocable no demuestra ser el *gate* que certifica PDF→PDF; caller externo NO VERIFICABLE. | FRONTERA CONSUMIDOR |
| **E-0.8-029** | P2 | En el preflight shell `calibration_provenance_available` se reduce a `Path.exists()`, y `calibration_partition_identities=frozenset()` viene justificado en comentario de Wave 3.1. | Presencia de archivo ≠ contenido reproducible; una partición vacía no demuestra independencia de una partición real. R7(g/h) NADR-24 y R9–10 NADR-23 solo si se usa ese contrato; no afirmar *leakage* ejecutado. | PRECONDITION CONDICIONAL |
| **E-0.8-030** | P2 | `RegressionAdapter.verify_oracle_integrity` usa `OracleSemanticIdentityCalculator.calculate(oracle.nodes)` y compara `metadata.oracle_hash`; `run_regression._run_evaluation` la invoca antes de evaluar. | **Hay** control criptográfico de GT en el camino de regresión; no afirmar ausencia universal. Pero ese control ocurre en etapa distinta al preflight CLI. | CAPACIDAD EXISTENTE |
| **E-0.8-031** | P2 | `NADR-F17-BIS-24` v1.2.0 FROZEN §5.1 R4–5 y §5.7–5.9 R29–37 separa éxito de ejecución, resultado científico, estado CERTIFIED y verificación post-run. | Norma de la **certificación de baseline**; su compatibilidad es relevante sin convertirla en prueba de CERTIFIED G3/G5. | REQUIRED ACOTADO |
| **E-0.8-032** | P2 | `certification/contract.py::compose_certification_status` devuelve CERTIFIED solo con SUCCESS, ACCEPTED, evidencia e invariantes, pero `run_regression.py` compone `ContinuousVerificationResult` y no llama esa función. | Dos conceptos distintos de resultado: CV topológico vs certificación compuesta, no duplicar ni equiparar estados. | NO FALSO CERTIFIED |
| **E-0.8-033** | P2 | `certification/post_run.py::validate_post_run` valida identidad, biyección per-document, agregados y existencia de provenance, sin decidir aceptación científica. | `PostRunReport.is_pass` indica **completitud de evidencia**, no juicio científico favorable. | CONTRATO DE EVIDENCIA |
| **E-0.8-034** | P2 | `tests/unit/test_certification_evidence.py::_evidence` construye un agregado `HARD_FAIL` con per-document PASS/HARD_FAIL y `test_complete_evidence_passes` espera post-run PASS. | Test válido para post-condiciones **estructurales**; no demuestra que un fallo científico pueda recibir CERTIFIED. | ORÁCULO TÉCNICO |
| **E-0.8-035** | P2 | `core/benchmark/verification/report.py::JsonContinuousVerificationReportFormatter` serializa `IdentityChain`, cobertura, `operational_result` y `regression_report`; `run_regression.py` produce JSON/MD y `subject_identity` por `git rev-parse HEAD` con fallback `None`. | Provenance de **extracción topológica** y su commit cuando existe, no hash o fidelidad de PDF español traducido. | PROVENANCE ACOTADA |
| **E-0.8-036** | P2 | `run_regression.py::main` emite `BASELINE_INTEGRITY_FAILURE`/resultado de ejecución, y solo ejecuta `_run_evaluation` si pasan materialización, SHA, biyección y GT. | Fallo de corpus no equivale a regresión científica; issue #34 conserva propiedad. | FAIL-CLOSED CONSERVADO |
| **E-0.8-037** | P2 | `tests/integration/test_regression_entry_point.py` parchea `verify_baseline_materialized`, `verify_baseline_physical_integrity`, `verify_pdf_ids` y `_run_evaluation` en distintos casos. | Tests útiles de códigos de salida y wiring, pero su PASS no valida físicamente los 21 PDFs ni evaluación real. | MOCKS DELIMITADOS |
| **E-0.8-038** | P2 | `core/benchmark/semantic_judge.py::SemanticJudge.evaluate_chunk` usa `AsyncGroq` con `GROQ_API_KEY`, envía SOURCE/TARGET a proveedor externo y espera `ChunkEvaluationScore` JSON. | Capacidad de juicio por modelo **existente**; ni independencia/human GT ni ejecución/egress fueron aprobados. No es parte del G3 seleccionado observado. | CANDIDATO REUSO / NO ORÁCULO |
| **E-0.8-039** | P2 | `judge_prompts.py` contiene rúbrica para terminología, fluidez, estructura y fidelidad, y `aggregation.py` tiene `LINEAL` por defecto con estrategias alternativas de dominancia por fidelidad. | Heurística/rúbrica sin calibración ni metrología aprobada; un score alto no constituye preservación STEM certificada. | MÉTRICA AUXILIAR |
| **E-0.8-040** | P2 | `apps/benchmark/__main__.py` prepara PDF desde cwd `[Amoretal_2023]_3hojas.pdf`, crea unidades ad hoc y compara dos modelos Groq en `SequentialBenchmarkOrchestrator`. | Entry point histórico separado, no root OCR durable→G3→G5 ni CI científica; puede consumir API pagada si se ejecuta. | BENCHMARK NO SELECCIONADO |
| **E-0.8-041** | P2 | `apps/benchmark/runners/groq_runner.py` crea `AsyncDispatcher` con `NullEventPlane`, dataset propio y respuestas con `TranslatedArtifact`/tokens y checks sintácticos. | Mide runner A/B, no persistencia FSM/receipts/proyección de la ruta seleccionada; no promoverlo a producción por nombre. | FRONTERA LEGACY |
| **E-0.8-042** | P2 | `core/benchmark/orchestrator.py::run_experiment` produce `BenchmarkRunReport` y utiliza `StructuralQualityEvaluator`/estadística; no llama `SemanticJudge`. | Incluso un experimento real Groq/Groq no sería automáticamente un juicio semántico independiente o PDF final. | PRODUCTOR BENCH |
| **E-0.8-043** | P2 | `core/benchmark/quality.py::StructuralQualityEvaluator` calcula fiabilidad, razón-proxy de tokens, sintaxis LaTeX y Markdown. | Sintaxis correcta y densidad aproximada no verifican verdad científica, traducción EN→ES ni fidelidad visual. | METRICS PROXY |
| **E-0.8-044** | P2 | `NADR-F17-BIS-23` v1.2.0 FROZEN R9–10 requiere particiones disjuntas por SHA; `calibration_v1` comparte cinco SHA con corpus canónico, pero el preflight histórico marca partición calibración **vacía**. | Solapamiento entre directorios ≠ fuga científica ejecutada sin partición/experimento efectivamente seleccionado. Definir protocolo primero. | DQ-03 / NO FALSO GAP |
| **E-0.8-045** | P2 | `NADR-F17BIS-29/30` son FROZEN para perfiles y enforcement de Continuous Verification, y `.github/workflows/continuous-verification.yml` apunta a `main`/`pipeline_stabilization`. | Perfil reducido no puede saltar integridad; workflow ejecutado no acredita barrera server-side ni product certification. PR #73 Draft interno no dispara CV por ese destino. | GOVERNANCE / DQ-05 |

**Clasificación de segunda pasada §7.1:** **45 E-IDs estables, todos P2; 0 P0/P1 confirmados y 0 GAP locales OPEN**. La E-026 describe una **tensión real con R7(d) FROZEN dentro del preflight heredado**, cuyo consumidor de certificación seleccionado no se acreditó: conservar OBS, DQ-0.8-06 y posible reevaluación **si se aprueba ese subtool como gate**, no ocultarla ni promulgar una remediación de producto sin sujeto. La ausencia de certificado PDF→PDF es una garantía aún no demostrada, no un PASS negativo ejecutado. Mantener issue #34, PPPR.0.4/0.6 y no generar falsos gaps por una ruta legacy.

## 14. GAPs — APERTURA

**No hay GAP PPPR.0.8 confirmado todavía.** Se conservan dependencias anteriores y preguntas: issue #34 (15 PDFs privados ausentes), calidad de traducción de PPPR.0.4, render G5 PPPR.0.6, modalidad de proveedor PPPR.0.7. La inexistencia de un gate científico completo no se etiqueta automáticamente como defecto de un contrato F17-BIS de extracción. Pendiente precisar el *Required* propio para E2E EN→ES (ADR Maestro), el alcance de los posibles falsadores y la no-regresión normativa.

## 15. HIPÓTESIS — SEGUNDA PASADA (CLASIFICACIÓN PARCIAL)

| ID | Pregunta a falsar | Estado |
|---|---|---|
| **H-0.8-A** | ¿El CV actual evalúa PDF español o PDF→AST de origen? | **CONFIRMADA extracción-only** E-006/012/022/035: `run_regression` produce `ContinuousVerificationReport` topológico; no G3/G5. Destino DC-01/02; mantener frontera FROZEN NADR-25 acotada |
| **H-0.8-B** | ¿Baseline canónica v3.9 accesible con 21 PDFs en Git? | **CONFIRMADA AUSENCIA FÍSICA EN CHECKOUT** (15 de 21) E-001/002/003/036; fuentes privadas del owner **NO VERIFICABLE**, issue #34 / DQ-01 |
| **H-0.8-C** | ¿Calibración/workload son GT final independiente ya autorizado? | **NO VERIFICABLE** la partición/protocolo en un run aprobado; SHA doc_01…05 se repite en canon, pero no hubo partición ejecutada ni `leakage` demostrado, E-010/011/029/044 → DQ-03 |
| **H-0.8-D** | ¿Preflight, estado y post-run actuales certifican PDF final EN→ES? | **RECHAZADA COMO GARANTÍA** E-007/009/026–034: funciones separadas sin caller G3/G5 acreditado; preflight CLI solo verifica presencia de oracle_hash; no equivale a PASS certificado. DQ-06/DC-01/02 |
| **H-0.8-E** | ¿Tests `real_e2e`/semantics ejecutan G3 real, G5 y comparan GT? | **RECHAZADA COMO GARANTÍA** E-015–019/037: mocks, PDF de cabecera y/o ruta legacy; no testigo E2E científico actual. DQ-02/04 |
| **H-0.8-F** | ¿C2/T07 y TST-STAB pueden reutilizarse sin inflar alcance? | **CONFIRMADA REUTILIZACIÓN ACOTADA** E-014/020/021: fake operativo, falsadores técnicos focales, no proveedor ni PDF científico. |
| **H-0.8-G** | ¿Qué se puede falsar sin corpus privado ni LLM? | **PARCIALMENTE CLASIFICADA**: frontera de hashes/GT, bytes de math explícita y falso éxito operacional por mocks son testigos focales; lingüística, visual y sistema completo **NO VERIFICABLE** sin permisos/oráculos → DQ-01/02/04/05 |
| **H-0.8-H** | ¿Cómo evitar PASS por confundir CV, certificación y benchmark? | **CONFIRMADA SEPARACIÓN DE OUTCOMES** E-031–035/038–045; sujeto/oráculo por nivel son DC-01/02 y gate por decidir. DQ-05 |

### 15.1 Deferred Questions de segunda pasada (§8.2)

| ID | Motivo y no-bloqueo del mandato forense estático | Destino |
|---|---|---|
| **DQ-0.8-01** | Los 15 PDFs originales de la baseline v3.9 no están en Git y su materialización, licencia/custodia y hashes reales requieren autorización del propietario. **No bloquea** localizar el fail-closed en código; sí impide ejecutar CV canónica. | Issue #34, ADR Maestro/Execution Plan solo si se decide materializador autorizado |
| **DQ-0.8-02** | Sin nuevo proveedor/modelo aprobado y muestras humanas bilingües legítimas, no existe evidencia de precisión/terminología EN→ES real. **No bloquea** clasificación de contratos fake, sí certificar traducción de producto. | PPPR.0.4/ADR Maestro y gate científico aprobado posterior |
| **DQ-0.8-03** | Calibración comparte SHA doc_01…05 con corpus canónico y workload tiene PDFs/GT sin manifest del mismo formato; no hay partición de evaluación aprobada ni proveniencia verificada. **No bloquea** inventario, sí comparación científica independiente. | ADR Maestro; evaluación científica/PPPR.0.9 si corresponde |
| **DQ-0.8-04** | La conservación de fórmulas, diagramas, figuras/vector, tablas y layout en PDF español exige outputs reales/criterio independiente y no se verificó aquí. **No bloquea** localizar testigos de bytes/topología, sí un PDF científico PASS. | PPPR.0.9 y plan de validación aprobado (no ejecutar por reflejo) |
| **DQ-0.8-05** | Continuidad de CI sobre un sujeto PDF→PDF completo exige contrato de alcance y runner/privacidad decididos; no hay test actual acreditado que juzgue ese sujeto. **No bloquea** señalar limitación extraction-only, sí gate final de producto. | ADR Maestro, Execution Plan, PPPR.0.9 según mandato |

| **DQ-0.8-06** | La CLI `preflight_certification.py` exige `oracle_hash` no vacío pero **no recalcula en ese shell** la identidad del contenido GT según NADR-F17-BIS-24 R7(d) FROZEN; `RegressionAdapter` sí compara durante la evaluación topológica. No se acreditó que la CLI independiente sea gate certificante del root D-1/D-2. **No bloquea** la auditoría estática ni justifica P1 comercial; sí exige reconciliar la suficiencia del preflight antes de usarlo como prueba de hashes verificados. | ADR Maestro (sujeto/gate), Execution Plan focal si se aprueba esa CLI; revisión normativa del subtool, sin tocar Sealed GT |

### 15.2 Decision Candidates (NO APROBADOS)

| ID | Decisión pendiente | Destino |
|---|---|---|
| **DC-0.8-01** | Definir el **sujeto** que se certificará (extracción-only vs EN→ES PDF→PDF completo) por niveles de garantía, sin invalidar tests topológicos. | ADR Maestro |
| **DC-0.8-02** | Definir **criterios y oráculos** para validez lingüística, invariancia de STEM y fidelity visual/layout con independencia suficiente. Reusar mecanismos antes de añadir nuevos. | ADR Maestro → Execution Plan |
| **DC-0.8-03** | Establecer **custodia y aprovisionamiento autorizado** de los 15 PDFs sin alterar manifest/GT/thresholds. No elegir storage/runner todavía. | Owner / issue #34 / Execution Plan condicionado |
| **DC-0.8-04** | Establecer gates y testigos **mínimos** de atribución (contrato, físico, científico, no falsos PASS), costo y aislamiento para proveedor comercial seleccionado. | ADR Maestro → Execution Plan |

## 16. RESPUESTAS A LA SEGUNDA PASADA

El código ya contiene una capacidad sustancial de evaluación topológica y certificación formal de sus artefactos, que **no** debe descartarse ni duplicarse. La principal discontinuidad para el *producto objetivo* es de **alcance de sujeto y oráculo**, no una prueba de corrupción actual: la Continuous Verification compara PDFs fuente extraídos frente a Sealed Oracle AST, mientras la ruta convergida agrega G3 y G5 antes del PDF final. El bloqueo de 15 PDFs canónicos está reconocido por issue #34 y debe permanecer bajo custodia. Los testigos operativos con fake no validan idioma ni ciencia.

**Segunda pasada:** se trazaron los productores/consumidores concretos. CV produce `ContinuousVerificationReport` de extracción; el preflight CLI es independiente y solo comprueba presencia (no integridad material) de `oracle_hash` en su shell; el dominio `CertificationEvidence`/`PostRunReport` tiene consumidores unitarios inspeccionados, no una certificación PDF→PDF conectada. El benchmark Groq A/B y `SemanticJudge` existen como capacidad distinta, no como oráculo aprobado ni ejecutado del producto. Queda pendiente la suficiencia normativa final para el HITO y la separación de testigos focales futuros, sin crear infraestructura.

## 21. CIERRE — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.1.** 45 E-IDs, todos P2; cero GAP locales OPEN; 8 hipótesis clasificadas parcialmente, seis DQ y cuatro DC, sin decisiones ni pruebas. La certificación tiene un preflight separado con limitación verificable de oracle_hash (E-026/027/030), y la verificación principal conserva su validación semántica de GT en RegressionAdapter. Falta examinar contratos de evidencia, elegibilidad real de los datasets y concluir §8.1–8.2 sin P1 ficticios. No se ejecutó CI, Docker, API, GT, SQLite ni corpus.

**Política Git:** abrir y mantener PR interno Draft con **solo este Markdown** desde `pppr/hito-0.8` → `pdf-pdf-product-readiness`; general #66 permanece Draft a `main`. No FROZEN/merge/implementación hasta completar la metodología y tener aprobación expresa; al integrar luego borrar rama corta antes de comenzar PPPR.0.9.
