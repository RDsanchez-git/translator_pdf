# HITO_PPPR.0.8_VALIDACION_TECNICA_Y_CIENTIFICA.md

**Estado:** IN_PROGRESS v1.0.0  
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

## 10. REGISTRO DE EVIDENCIAS — PRIMERA PASADA (NO FROZEN)

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

**Severidad inicial §7.1:** 25 E-IDs, todas P2: hechos, testigos, límites y dependencias de datos. **Ningún nuevo P1/P0 confirmado** en esta apertura: la ausencia de validación de producto final es un objetivo de readiness aún no ejecutado y el bloqueo canónico ya tiene issue/destino. Si se encuentra un contrato aprobado de verificación de PDF final que el camino actual incumpla, abrir ficha P1 solo después de cotejar su aplicabilidad y consumidores. No duplicar GAP-0.2/0.3/0.4/0.5/0.6/0.7.

## 14. GAPs — APERTURA

**No hay GAP PPPR.0.8 confirmado todavía.** Se conservan dependencias anteriores y preguntas: issue #34 (15 PDFs privados ausentes), calidad de traducción de PPPR.0.4, render G5 PPPR.0.6, modalidad de proveedor PPPR.0.7. La inexistencia de un gate científico completo no se etiqueta automáticamente como defecto de un contrato F17-BIS de extracción. Pendiente precisar el *Required* propio para E2E EN→ES (ADR Maestro), el alcance de los posibles falsadores y la no-regresión normativa.

## 15. HIPÓTESIS — PRIMERA PASADA (NO TERMINALES)

| ID | Pregunta a falsar | Estado |
|---|---|---|
| **H-0.8-A** | ¿El CI de regresión topológica evalúa la salida PDF final traducida o solo extraction AST? | **CONFIRMADA extracción-only** E-006/012/022; especificar contrato y destino de producto |
| **H-0.8-B** | ¿La baseline v3.9 está materializada y accesible con 21 PDFs bajo las reglas selladas? | **CONFIRMADA ausencia en checkout Git**, NO VERIFICABLE fuente privada del owner → E-001/002/003, issue #34 |
| **H-0.8-C** | ¿Los 5 documentos de calibración y 5 workload pueden servir como GT oficial independiente? | **ABIERTA**, identidad/procedencia/partición E-010/011 → DQ-03 |
| **H-0.8-D** | ¿Los 8 preflight + estado CertificationStatus bastan para certificar EN→ES PDF final? | **ABIERTA**, verificar qué sujeto alimenta evidence/post-run E-007/008/009 |
| **H-0.8-E** | ¿Los tests con nombres e2e/real/semantic realmente ejecutan OCR→G3 real→G5 y comparan oráculos? | **CONFIRMADA cobertura parcial y legacy** E-015…019, no E2E científico |
| **H-0.8-F** | ¿C2/T07 y TST-STAB permiten reutilización sin fingir que se probó calidad de traducción? | **CONFIRMADA solo operacional/técnica histórica** E-014/020/021, mantener SHA/alcance |
| **H-0.8-G** | ¿Qué aspectos se pueden falsar sin corpus privado ni LLM y cuáles requieren custodia/autorización? | **ABIERTA**, delimitar testigos focales posteriores → DQ-01/02/04 |
| **H-0.8-H** | ¿Cómo identificar sujetos, oráculos y outcomes para evitar verde falso por PASS de extracción? | **ABIERTA**, contrastar reglas FROZEN de verificación contra el root D-1/D-2 → DC-01/02 |

### 15.1 Deferred Questions provisionales (§8.2)

| ID | Motivo y no-bloqueo del mandato forense estático | Destino |
|---|---|---|
| **DQ-0.8-01** | Los 15 PDFs originales de la baseline v3.9 no están en Git y su materialización, licencia/custodia y hashes reales requieren autorización del propietario. **No bloquea** localizar el fail-closed en código; sí impide ejecutar CV canónica. | Issue #34, ADR Maestro/Execution Plan solo si se decide materializador autorizado |
| **DQ-0.8-02** | Sin nuevo proveedor/modelo aprobado y muestras humanas bilingües legítimas, no existe evidencia de precisión/terminología EN→ES real. **No bloquea** clasificación de contratos fake, sí certificar traducción de producto. | PPPR.0.4/ADR Maestro y gate científico aprobado posterior |
| **DQ-0.8-03** | Calibración comparte SHA doc_01…05 con corpus canónico y workload tiene PDFs/GT sin manifest del mismo formato; no hay partición de evaluación aprobada ni proveniencia verificada. **No bloquea** inventario, sí comparación científica independiente. | ADR Maestro; evaluación científica/PPPR.0.9 si corresponde |
| **DQ-0.8-04** | La conservación de fórmulas, diagramas, figuras/vector, tablas y layout en PDF español exige outputs reales/criterio independiente y no se verificó aquí. **No bloquea** localizar testigos de bytes/topología, sí un PDF científico PASS. | PPPR.0.9 y plan de validación aprobado (no ejecutar por reflejo) |
| **DQ-0.8-05** | Continuidad de CI sobre un sujeto PDF→PDF completo exige contrato de alcance y runner/privacidad decididos; no hay test actual acreditado que juzgue ese sujeto. **No bloquea** señalar limitación extraction-only, sí gate final de producto. | ADR Maestro, Execution Plan, PPPR.0.9 según mandato |

### 15.2 Decision Candidates provisionales (no aprobados)

| ID | Decisión pendiente | Destino |
|---|---|---|
| **DC-0.8-01** | Definir el **sujeto** que se certificará (extracción-only vs EN→ES PDF→PDF completo) por niveles de garantía, sin invalidar tests topológicos. | ADR Maestro |
| **DC-0.8-02** | Definir **criterios y oráculos** para validez lingüística, invariancia de STEM y fidelity visual/layout con independencia suficiente. Reusar mecanismos antes de añadir nuevos. | ADR Maestro → Execution Plan |
| **DC-0.8-03** | Establecer **custodia y aprovisionamiento autorizado** de los 15 PDFs sin alterar manifest/GT/thresholds. No elegir storage/runner todavía. | Owner / issue #34 / Execution Plan condicionado |
| **DC-0.8-04** | Establecer gates y testigos **mínimos** de atribución (contrato, físico, científico, no falsos PASS), costo y aislamiento para proveedor comercial seleccionado. | ADR Maestro → Execution Plan |

## 16. RESPUESTAS INICIALES

El código ya contiene una capacidad sustancial de evaluación topológica y certificación formal de sus artefactos, que **no** debe descartarse ni duplicarse. La principal discontinuidad para el *producto objetivo* es de **alcance de sujeto y oráculo**, no una prueba de corrupción actual: la Continuous Verification compara PDFs fuente extraídos frente a Sealed Oracle AST, mientras la ruta convergida agrega G3 y G5 antes del PDF final. El bloqueo de 15 PDFs canónicos está reconocido por issue #34 y debe permanecer bajo custodia. Los testigos operativos con fake no validan idioma ni ciencia.

El trabajo pendiente de esta auditoría es clasificar contratos FROZEN aplicables, rutas de GT/provenance y límites de ejecución, confirmar si existe un consumidor de certificación PDF final actualmente conectado, y precisar verificadores reutilizables sin crear una segunda arquitectura por intuición.

## 21. CIERRE — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.0.** 25 E-IDs P2, ocho hipótesis iniciales, cinco DQ y cuatro DC provisionales; cero GAP locales confirmados. Revisión del corpus y del sujeto de Continuous Verification con evidencia estática; tests y certificación NOT_RUN. Pendientes: trazado de consumidores de certificación/evaluación, normas FROZEN compatibles y cierre §§8.1–8.2/9.2–9.4. Sin tocar corpus, GT, archivos del propietario, bases, proveedor, CI ni código de producción.

**Política Git:** abrir y mantener PR interno Draft con **solo este Markdown** desde `pppr/hito-0.8` → `pdf-pdf-product-readiness`; general #66 permanece Draft a `main`. No FROZEN/merge/implementación hasta completar la metodología y tener aprobación expresa; al integrar luego borrar rama corta antes de comenzar PPPR.0.9.
