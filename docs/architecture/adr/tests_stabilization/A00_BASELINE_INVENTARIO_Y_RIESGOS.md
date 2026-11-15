# A-00 — Línea base, inventario estructural y riesgos de ejecución

**Programa:** TST-STAB / A-00 (etapa A, primera tarea)  
**Estado:** COMPLETADO **sólo como inventario estático**; la auditoría de casos y las pruebas dinámicas corresponden a A-01…A-07.  
**Fecha de observación:** 2026-11-15  
**Repositorio:** `RDsanchez-git/translator_pdf`  
**Base protegida:** `main` @ `83ef0257f795f0d973f9393cc225e7af5b956ade` (sin cambios durante esta tarea).  
**Rama del programa:** `tests_stabilization` @ `9495259f1e35419ddf88c02a5649be6444ad062e` (**HEAD de observación ANTES** de registrar A-00).  
**Fuente del censo:** Git tree recursivo de ese HEAD, con `truncated=false` y 1263 elementos en el árbol.  
**Rastreo:** el archivo y su SHA de commit en GitHub documentan el estado posterior. No se debe suponer que un HEAD futuro conserve este inventario.

## 1. Qué es y qué NO es A-00

Este documento congela: referencia de código, rutas de módulos candidatos, **configuración de selección** de pytest/GitHub, material técnico presente en el árbol y **superficies conocidas de escritura**. Distingue la topología productiva de rutas heredadas y ciencia.

**A-00 NO**: ejecuta tests ni Pyright, no recopila casos/parametrizaciones dinámicas, no calcula cobertura, no certifica cada test, no garantiza que toda escritura potencial haya sido descubierta, no valida fidelidad científica, no modifica componentes. Su objetivo es entregar insumos trazables y una política de aislamiento a **A-01 (inventario semántico) y A-05 (seguridad de ejecución)**.

La declaración del owner de **Pyright local 0 errors/0 warnings/0 informations** se conserva como antecedente, **no como una ejecución A-00**. Los **188** módulos Python enumerados aquí tampoco son 188 tests: un módulo puede tener cero, una o muchas funciones y parametrizaciones.

## 2. Censo estático de rutas en el tree

| Grupo de archivos `tests/` | Cantidad verificable | Significado |
|---|---:|---|
| Módulos `test_*.py` en `tests/unit/` | 102 | **Candidatos** de pytest, no todos marcados necesariamente `unit` |
| Módulos `test_*.py` en `tests/integration/` | 67 | **Candidatos** de pytest, no todos marcados necesariamente `integration` |
| Módulos `test_*.py` en `tests/smoke/` | 1 | Candidatos de smoke |
| Módulos `test_*.py` en raíz `tests/` | 7 | Categoría pendiente de clasificar |
| **Total de módulos `test_*.py`** | **177** | Conteo de archivos, **no** de test cases |
| Otros archivos Python bajo `tests/` | **11** | Helpers, `__init__`, `conftest.py`, fixtures, adaptadores |
| **Total Python bajo `tests/`** | **188** | Censo Python; coincidencia numérica con el resultado Pyright local anterior |
| Archivos versionados de cualquier tipo bajo `tests/` | **294** | Incluye PDF, JSON, assets, datos y outputs históricos |

**Cálculo:** búsqueda por rutas de blobs del tree (`tests/**/test_*.py`). No se evaluaron imports, selectors, markers, `skipif`, parametrizaciones ni hooks dinámicos. La lista íntegra de 177 rutas está en el **Anexo A** para evitar depender del estado mutable de GitHub cuando se avance.

**Archivos adicionales Python:** `tests/__init__.py`, `tests/fixtures/unit_cost_context.py`, `tests/helpers/__init__.py`, `tests/helpers/bootstrap_translation_golden.py`, `tests/helpers/cv_execution.py`, `tests/helpers/fakes.py`, `tests/helpers/markdown_inspector.py`, `tests/integration/__init__.py`, `tests/integration/_reconciler_test_factory.py`, `tests/smoke/conftest.py`, `tests/unit/__init__.py`.

## 3. Censo de CI y selección real declarada

**Fuente a SHA 83ef0257f795f0d973f9393cc225e7af5b956ade:** [`.github/workflows/ci.yml`](../../../../.github/workflows/ci.yml), [`pyproject.toml`](../../../../pyproject.toml), [`pyrightconfig.json`](../../../../pyrightconfig.json) y [`.github/workflows/continuous-verification.yml`](../../../../.github/workflows/continuous-verification.yml).

### 3.1 Configuración de pytest observada

En `pyproject.toml` ``[tool.pytest.ini_options]`:

- `testpaths = ["tests"]`; `python_files = ["test_*.py"]`, `python_classes = ["Test*"]`, `python_functions = ["test_*"]`.
- `addopts = ["--strict-markers", "--strict-config", "-ra", "-m", "not e2e"]`: el uso ordinario de pytest deselecciona **marcadores `e2e`**, no nombres de archivo que contienen la cadena «e2e».
- Markers declarados: `regression`, `integration`, `unit`, `smoke`, `e2e`. Las **asignaciones reales a cada caso** aún no se enumeraron (A-01).
- Una ejecución de CI con `-m` explícito selecciona la expresión solicitada, en lugar de interpretar `integration` como directorio.
- El resultado de `pytest --collect-only` está **pendiente**: no se ejecutó sobre la copia del owner por los riesgos de escritura del §5.

### 3.2 CI técnico vigente (comandos exactos)

| Workflow/job | Invocación declarada | Notas de alcance |
|---|---|---|
| `static-analysis` | `pyright`; `lint-imports --config pyproject.toml` | Pyright oficial **incluye core/apps/infra/runtime y excluye tests**; modo standard/Python 3.11/Linux. Check obligatorio: `Static Analysis (pyright + import-linter)` |
| `unit-tests` | `python -m pytest -m "unit" -v --tb=short --no-header -x` | Selección por marker, no todos los archivos de `tests/unit/` |
| `integration-tests` paso B03 | `python -m pytest tests/unit/test_b031_g3_reusable_fake.py tests/unit/test_b032_offline_pdf_lab.py -q -ra` | Selección explícita |
| `integration-tests` paso W06/G3 | Cinco archivos: `test_w06_g3_uncertain_effect_offline.py`, `test_g3_b4_9_reconciler_fencing.py`, `test_g3_b4_8_preserve_engine.py`, `test_g3_b4_3a_engine_staging.py`, `test_g3_b4_3b_publication_recovery.py` | Selección explícita (sin marcador requerido) |
| `integration-tests` W08-2b | `test_w08_durable_context_boundary.py` | Selección explícita |
| `integration-tests` W08-2c | `test_w08_ocr_g3_context_wiring.py`, `test_g3_b4_2_ocr_router_durable_plan.py` | Selección explícita |
| `integration-tests` G3/G5 | `test_g3_b4_7b_sqlite_quota_thread_owner.py`, `test_g5_assembler_worker_integration.py` | Selección explícita |
| `integration-tests` por marker | `python -m pytest -m "integration and not regression" -v --tb=short --no-header` | Omite casos sin marker `integration` |
| `integration-tests` suite técnica | `python -m pytest -m "not e2e" -q -ra` | **Incluye tests legacy no-e2e aunque no tengan marker**; no prueba que sus oráculos sean válidos |

Los pasos focales anteriores son argumentos del propio workflow y no un inventario de tests ejecutados o sus resultados en este SHA. Algunos casos pueden ejecutarse más de una vez en diferentes pasos; **no sumarlos** como casos independientes.

**Disparadores GitHub Actions:** CI técnico `push: [main, develop]` y `pull_request: [main, pipeline_stabilization]`. Un push directo a `tests_stabilization` **no activa por sí solo** esos workflows. Para cobertura en GitHub, abrir un PR **Draft** con `head=tests_stabilization` y `base=main`. No fusionar automáticamente ni cambiar branch protection.

### 3.3 Continuous Verification — fuera de la campaña

El workflow `continuous-verification.yml` ejecuta SMOKE en PR a `main/pipeline_stabilization` y FULL en push a `main` o `workflow_dispatch`, usando `tools.evaluation.run_regression` y corpus canónico. **No se ejecuta ni se remedia en A/B/C**. El fallo conocido del corpus en CI (issue #34) no se transforma en PASS ni se equipara a fallo de los tests técnicos.

**Evidencia estática de materialización, sólo para evitar writes:** en el tree hay 21 JSON de Ground Truth canónico y 6 PDF canónicos versionados, además del manifiesto. Ese desnivel es la superficie separada y **diferida** del corpus, no un objetivo de A-00.

## 4. Separación de rutas: raíz soportada vs legacy, benchmark y ciencia

**Fuente:** [Atlas PDF→PDF ``2 y 6](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md), contrastado con `apps/cli/main.py`, `apps/bootstrap/pipeline_factory.py`, `apps/ocr_router/__main__.py`, `runtime/engine.py` (ruta declarada en Atlas) y `apps/compiler/__main__.py`.

| Ruta o superficie | Entrada/autoridad | Tratamiento en esta campaña |
|---|---|---|
| **Ruta activa:** admisión CLI → OCR Router → plan/snapshots → G3 `runtime/engine.py` → materialización → G5 `apps/compiler/__main__.py` | Root PDF→PDF seleccionado; foreground `--run` reutiliza contratos en entorno aislado | **Sujeto técnico prioritario** para A-01/A-02 |
| Reconciler / Sweeper | Recuperación y mantenimiento sin egress incierto | Auditar sus **contratos técnicos** (STOP, fencing, CAS) por casos relevantes |
| **R1 legacy (CLI)** | `handle_translate_async` en `apps/cli/main.py` es fail-closed, `C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED` | Retener test de desactivación; **no** atribuir a tests de la biblioteca R1 cobertura del root actual |
| **R1 biblioteca/históricos** | `build_pipeline()`, `TranslationPipeline`, `AsyncDispatcher`, `legacy_translate_async.py` | **Separar** tests útiles de consumidores/legacy; decidir etiqueta/alcance en A-01/B, **no borrar** |
| **R3 no seleccionado** | `apps/llm_workers/__main__.py::LLMWorkerDaemon` puede ejecutarse manualmente; no root soportado | Tests R3 pueden ser válidos para su contrato, pero no certifican G3; no activar R3 |
| Benchmark / comparación / CV | `core/benchmark`, `tools/evaluation`, `tests/corpus/canonical/`, `tests/corpus/calibration_v1/` | **D-5 diferido**; si pruebas de tooling se ejecutan en CI, clasificar la **selección** y su riesgo, sin cambiar GT ni CV |

**Precaución de clasificación:** la tabla de rutas no asigna por similitud de nombres todos los módulos a una ruta. La asignación por **SUT real y consumidor** se hace en A-01/A-02. Un mismo archivo puede contener tests de varias fronteras; la categoría del archivo no es un resultado.

### 4.1 Rutas candidatas de primera lectura (NO equivalen a cobertura acreditada)

| Frontera | Test paths a estudiar |
|---|---|
| CLI/inbox | `tests/integration/test_pdf_inbox_submission.py`; `tests/integration/test_cli_router.py`; `tests/integration/test_b03_foreground_pdf_product.py` |
| Parser/B02 y AST | `tests/integration/test_verification_pipeline_connection.py`; `tests/integration/test_pymupdf_extraction_integrity.py`; `tests/integration/test_b023_raster_image_pipeline.py`; `tests/integration/test_b025_math_visual_preservation.py` |
| OCR/plan/contexto | `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py`; `tests/integration/test_w08_ocr_g3_context_wiring.py`; `tests/integration/test_w08_durable_context_boundary.py` |
| G3 efectos inciertos, staging y publish | `tests/integration/test_w06_g3_uncertain_effect_offline.py`; `tests/integration/test_g3_b4_3a_engine_staging.py`; `tests/integration/test_g3_b4_3b_publication_recovery.py` |
| FSM, CQRS, leases y G5 | `tests/integration/test_g3_b4_9_reconciler_fencing.py`; `tests/integration/test_g5_assembler_worker_integration.py`; `tests/integration/test_g5_assembler_lease_recovery.py` |
| Histórico/posible falsa cobertura | `tests/integration/test_golden_parser.py`; `test_chunker_snapshot.py`; `test_real_parser_pipeline.py`; `test_pipeline_orchestration.py`; `test_real_e2e.py`; `test_e2e_walking_skeleton.py`; `tests/test_pipeline_fidelity.py` |

Esta lista abre la auditoría semántica; la **lista estructural completa** está en Anexo A.

## 5. Inventario inicial de fixtures, artefactos y escrituras

### 5.1 Fixtures y outputs versionados (no deben ser tratados como scratch)

**`tests/fixtures/` — 12 blobs versionados:**

- `tests/fixtures/sample_3_pages.pdf` — 2045076 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0001-01.png` — 20419 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0001-05.png` — 20159 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0001-07.png` — 2694 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0003-02.png` — 49151 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0003-05.png` — 21486 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0003-10.png` — 7442 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf_assets/sample_3_pages.pdf-0003-12.png` — 16039 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf.ast.json` — 29352 bytes (blob versionado)
- `tests/fixtures/sample_3_pages.pdf.debug.md` — 18581 bytes (blob versionado)
- `tests/fixtures/sample_chunks.json` — 22631 bytes (blob versionado)
- `tests/fixtures/unit_cost_context.py` — 548 bytes (blob versionado)

**`tests/output/` — 7 artefactos versionados:**

- `tests/output/debug_translated_[Amoretal_2023]_3hojas_attempt_1.tex` — 21097 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/debug_translated_[Amoretal_2023]_3hojas.tex` — 165 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/debug_translated_johnstone00distribution_3hoja_attempt_1.tex` — 9019 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/debug_translated_johnstone00distribution_3hoja.tex` — 165 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/debug_translated_marchenko_pastur_1967_3hoja_attempt_1.tex` — 7954 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/debug_translated_marchenko_pastur_1967_3hoja.tex` — 165 bytes (archivo **versionado**, no destino descartable por defecto)
- `tests/output/translated_marchenko_pastur_1967_3hoja.pdf` — 26831 bytes (archivo **versionado**, no destino descartable por defecto)

Además existen fixtures/candidatos y datos en `tests/corpus/`, incluidos `calibration_v1`, `canonical`, `workload` y `archive`. La existencia en Git **no autoriza** su transformación ni borrado. La regla de `.gitignore` excluye nuevas incorporaciones de `tests/corpus/canonical/pdf/`, pero los PDFs previamente versionados se muestran en Git; un ignore **no es** protección contra escritura en archivos trackeados.

### 5.2 Riesgos de escritura/autoaprobación **observados en el código** (fuentes inspeccionadas)

| Riesgo | Archivo / disparador observado | Superficie e impacto potencial | Dictamen estático y acción pendiente |
|---|---|---|---|
| **IO-01** | `test_golden_parser.py` ``setUp`: si falta `tests/fixtures/sample_3_pages.pdf`, crea directorio y escribe PDF ficticio | Fixture versionada; además ``skipTest` si falta `tests/golden/*.fingerprint.json`, hoy no versionado | **CONFIRMADO**; no ejecutarlo sobre working tree antes de A-05; TS-001/B-01 |
| **IO-02** | `test_real_parser_pipeline.py` ``setUp`: if missing → escribe `tests/fixtures/sample_3_pages.pdf` | Fixture versionada, puede falsear evidencia de ingesta | **CONFIRMADO**; evaluar SUT mockeado y pasar a `tmp_path` si se remedia |
| **IO-03** | `test_pipeline_orchestration.py` ``setUp`: if missing → escribe `tests/fixtures/sample_3_pages.pdf` | Mismo archivo versionado; parser del test parcheado | **CONFIRMADO**; no contar como integración de PDF real |
| **IO-04** | `test_chunker_snapshot.py`: si falta `tests/fixtures/sample_chunks.json`, **genera el expected** desde el actual y retorna sin aserciones | Contamina línea de base técnica y puede dar falso verde | **CONFIRMADO** como rama condicional; snapshot existe en el tree actual, **no** se afirma que se haya ejecutado dicha rama; TS-002/B-02 |
| **IO-05** | `test_e2e_walking_skeleton.py`: si falta `tests/fixtures/sample_3_pages.pdf.ast.json`, la crea; usa ``tests/fixtures/e2e_cache_real.db` y elimina DB/WAL/SHM en teardown | Ruta fija bajo fixtures, base SQLite y borrado por nombre; en caso de falla, residual posible | **CONFIRMADO**; priorizar aislamiento, no asumir comportamiento E2E |
| **IO-06** | `test_recovery_flow.py` ``setUpClass`/``tearDownClass`: usa ``infra/db/test_fsm.db` y elimina archivo preexistente | **RIESGO ALTO**: colisión/destrucción de archivo de BD en ruta fija fuera de ``tmp_path` | **CONFIRMADO**; **NO ejecutar en la copia del owner** sin aislamiento y revisión previa |
| **IO-07** | `test_translation_semantics.py`: apunta a `tests/golden/sample_3_pages.semantics.json` y llama a `skipTest` si falta | No escribe el oráculo observado, pero puede convertir una ausencia de cobertura en SKIP | **CONFIRMADO**; clasificación y alcance diferidos a A-01 |
| **IO-08** | `tests/test_pipeline.py` ejecutado como **script** (`__main__`) crea `tests/output/` y escribe `tests/stress_report.json`, procesa PDFs reales mediante `run_pipeline` | Mutación de outputs históricos/directorios y ejecución potencial fuera de la ruta actual | **CONFIRMADO** como operación invocable **directamente**, no como test ``test_*`` recolectado automáticamente |
| **IO-09** | `test_real_e2e.py`: ``patch.object(self.pipeline, 'execute', return_value=mock_result)` | Falsa atribución de cobertura de la operación si se presenta como E2E; no se observó escritura destructiva en los fragmentos examinados | **CONFIRMADO** patrón de mock; A-01 debe clasificar |
| **IO-10** | `test_healing_e2e_telemetry.py`: funciones ``test_e2e_*`` sin ``@pytest.mark.e2e`` visible en sus definiciones | Posible selección en ``not e2e`` pese al nombre; no se acredita E2E por ello | **INDICIO**, a confirmar por marker real en A-01 |
| **IO-11** | Suite completa y herramientas de bootstrap/sellado/corpus | Pueden existir más escrituras o pasos de collection con side effects | **NO AUDITADO EXHAUSTIVAMENTE**; A-01/A-05 deben identificar todos antes de ejecución amplia |

### 5.3 Política inmediata de seguridad

1. **No correr `pytest -q`, `--collect-only` o módulos legacy de riesgo en el working tree del owner** hasta A-05 o usar copia/worktree aislado. Importar módulos durante colección puede desencadenar side effects.
2. Inspeccionar primero el uso de ``tests/fixtures``, ``tests/output``, ``infra/db`` y todo ``open(...,'w')``, ``write_text``, ``write_bytes``, ``unlink``, ``remove``, ``rmtree``, además de funciones llamadas indirectamente. Esta tabla **no sustituye** la búsqueda completa.
3. Preservar la eliminación local deliberada del PDF previamente acordada, otras diferencias del working tree y todos los oráculos. Prohibido ``git clean``, ``git reset --hard`` o restaurar archivos sin decisión del owner.
4. Para futuros negativos, usar ``tmp_path``, SQLite disposable y fake loopback; no servicios de pago ni red externa. Verificar estado de árbol antes/después.
5. Si falla un test por una precondición obligatoria ausente, registrar el fallo; **no autogenerar un snapshot/corpus** ni suavizarlo con SKIP.
6. Este censo es **observacional**: ni ejecuté tests ni comprobé runtime; los riesgos son paths y ramas de código vistos por inspección.

## 6. Contratos que A-01 debe investigar, no dar por cubiertos

| Capa/contrato | Riesgo al interpretar un PASS | Evidencia faltante para considerar el test confiable |
|---|---|---|
| PDF/AST físico | Parser monkeypatched, PDF ficticio, sólo ``len > 0`` | Invocación real del SUT y oráculo de propiedades relevantes |
| G3/UNKNOWN | Fake sin aceptar llamada real o segunda llamada permitida | Una única aceptación y **cero reenvío automático** demostrables |
| Identidad de plan | Comparar sólo conteos sin binding real | Manipulación de hash/generación que produzca rechazo |
| G5/lease y publicación | Probar estado en memoria sin artifact/SQLite | Lease/fencing durable y ausencia de publicación vieja |
| FSM/foreground | Mock de éxito o ruta R1 en vez del root | Rechazo real ante estado ausente y sin PDF falsamente exitoso |
| Legacy/benchmark/CV | Nombre “real/e2e/regression” o marker sin garantía | Reclasificar scope y excluir ciencia de la campaña activa |
| Seguridad de ejecución | CI verde con fixtures aparentemente presentes | No escribe a rutas trackeadas ni borra DB en rutas fijas |

Las tareas B/C **no están empezadas**. Las fichas ``TR-###``, las mutaciones, el resultado de pytest por caso y la matriz contrato×test son A-01…A-07.

## 7. Comprobaciones realizadas y límites de evidencia

- [x] Lectura de ``main`` y ``tests_stabilization`` mediante GitHub: refs comparados, baseline inmóvil.
- [x] Censo del git tree **no truncado**; paths del Anexo A y fixtures/outputs de `5.1.
- [x] Lectura de workflow técnico, CV, Pyright, pytest y ``.gitignore``.
- [x] Contraste de rutas CLI/OCR/G3/G5, R1/R3 y benchmark contra Atlas y entrypoints visibles.
- [x] Inspección estática de tests seleccionados que demuestra riesgos de I/O y de atribución de cobertura.
- [ ] **No ejecutado:** pytest collection, pytest suite, mutations, process-level tests, Docker/lab, Pyright local, validación científica. Corresponde a etapas posteriores y entornos seguros.
- [ ] **Pendiente:** enumeración dinámica de todos los casos/parametrizaciones, markers efectivos, SKIP/XFAIL, I/O indirecta, exhaustividad de escritura, coverage/sensibilidad. A-01/A-05.

**DoD específico A-00:** refs fijados + censo de paths + selección/CI documentada + fuentes de fixtures/escrituras identificadas y riesgos registrados + separación de roots. **Satisfecho por inspección estática**, sujeto a que A-05 mantenga los riesgos controlados antes de correr suites.

**No se afirma:** “suite de tests sana”, “CI técnico validado sobre nuevo SHA”, “fidelidad científica”, “todos los tests son seguros”, “A-01 terminada”.

## Anexo A. Lista completa de módulos pytest candidatos (`test_*.py`)

Fuente: tree de `tests_stabilization` @ `9495259f1e35419ddf88c02a5649be6444ad062e` con `truncated=false`.

### tests/unit — 102 módulos

```text
tests/unit/test_adapters.py
tests/unit/test_assembler.py
tests/unit/test_asset_placeholder.py
tests/unit/test_ast_integrity.py
tests/unit/test_ast_models.py
tests/unit/test_b022_image_rendering.py
tests/unit/test_b023_raster_asset_contract.py
tests/unit/test_b024_explicit_math_spans.py
tests/unit/test_b025_math_visual.py
tests/unit/test_b031_g3_reusable_fake.py
tests/unit/test_b0324_foreground_app_root.py
tests/unit/test_b032_offline_pdf_lab.py
tests/unit/test_backpressure_mechanism.py
tests/unit/test_baseline_integrity.py
tests/unit/test_baseline_integrity_semantics.py
tests/unit/test_baseline_pdf_completeness.py
tests/unit/test_c4_t06_supported_roots.py
tests/unit/test_cache_provider.py
tests/unit/test_cancellation_mechanism.py
tests/unit/test_certification_boundary.py
tests/unit/test_certification_evidence.py
tests/unit/test_certification_preflight.py
tests/unit/test_configuration_fingerprint.py
tests/unit/test_context_enricher.py
tests/unit/test_context_resolver.py
tests/unit/test_convergence_compose_preflight.py
tests/unit/test_convergence_db_bootstrap.py
tests/unit/test_coordinated_shutdown.py
tests/unit/test_corpus_models.py
tests/unit/test_corpus_port_asymmetry.py
tests/unit/test_criticality_costs.py
tests/unit/test_criticality_policy.py
tests/unit/test_criticality_verdict.py
tests/unit/test_cv_workflow_contract.py
tests/unit/test_dispatcher.py
tests/unit/test_dispatcher_validation.py
tests/unit/test_docling_provider.py
tests/unit/test_dynamic_context_resolver_live_update.py
tests/unit/test_enforcement_contract.py
tests/unit/test_execution_context_boundaries.py
tests/unit/test_execution_metadata.py
tests/unit/test_exit_codes_and_guard.py
tests/unit/test_framing_injectivity.py
tests/unit/test_ground_truth_completeness.py
tests/unit/test_ground_truth_lifecycle.py
tests/unit/test_ground_truth_models.py
tests/unit/test_ground_truth_ports.py
tests/unit/test_ground_truth_sealed_protection.py
tests/unit/test_ground_truth_sealing_atomicity.py
tests/unit/test_ground_truth_validity.py
tests/unit/test_healing_idempotency.py
tests/unit/test_healing_multi_failure_transaction.py
tests/unit/test_idempotency_replacement.py
tests/unit/test_identity_chain.py
tests/unit/test_layout_validator.py
tests/unit/test_leaderboard_service.py
tests/unit/test_manifest_fingerprint.py
tests/unit/test_math_normalizer.py
tests/unit/test_operational_visibility.py
tests/unit/test_oracle_identity.py
tests/unit/test_paragraph_idempotency.py
tests/unit/test_perimeter_validator.py
tests/unit/test_pipeline_factory.py
tests/unit/test_pipeline_fsm_emission.py
tests/unit/test_preservation_validator.py
tests/unit/test_pricing_engine.py
tests/unit/test_prompt_builder.py
tests/unit/test_provenance_identities.py
tests/unit/test_pymupdf_integrity.py
tests/unit/test_rate_limiter.py
tests/unit/test_recovery_determinability.py
tests/unit/test_regression_adapter.py
tests/unit/test_regression_aggregation.py
tests/unit/test_regression_mechanism.py
tests/unit/test_regression_models.py
tests/unit/test_regression_report.py
tests/unit/test_regression_strategy.py
tests/unit/test_resilient_provider.py
tests/unit/test_routing.py
tests/unit/test_sanitize_ground_truth_types.py
tests/unit/test_score_policy.py
tests/unit/test_semantic_chunker.py
tests/unit/test_semantic_classification.py
tests/unit/test_semantic_classifier.py
tests/unit/test_semantic_validator.py
tests/unit/test_state_projection.py
tests/unit/test_structural_healing.py
tests/unit/test_structural_metric.py
tests/unit/test_structural_validator.py
tests/unit/test_subject_identity.py
tests/unit/test_summary_builder.py
tests/unit/test_tectonic_runner.py
tests/unit/test_text_render_strategy.py
tests/unit/test_tooling_determinism.py
tests/unit/test_validation_pipeline.py
tests/unit/test_verification_boundary.py
tests/unit/test_verification_outcome.py
tests/unit/test_verification_profiles.py
tests/unit/test_verification_report.py
tests/unit/test_w08_g3_cache_barrier.py
tests/unit/test_w08_inference_identity_contract.py
tests/unit/test_zhang_shasha.py
```

### tests/integration — 67 módulos

```text
tests/integration/test_add_document_to_corpus.py
tests/integration/test_b022_image_staging.py
tests/integration/test_b023_raster_image_pipeline.py
tests/integration/test_b024_g3_g5_math_roundtrip.py
tests/integration/test_b025_math_visual_preservation.py
tests/integration/test_b03_foreground_pdf_product.py
tests/integration/test_baseline_gt_preconditions.py
tests/integration/test_baseline_integrity_exit_code.py
tests/integration/test_baseline_materialization.py
tests/integration/test_baseline_physical_integrity.py
tests/integration/test_benchmark_orchestration_integration.py
tests/integration/test_c3_t05_process_boundary.py
tests/integration/test_canonicalize_gt_hardening.py
tests/integration/test_chunker_snapshot.py
tests/integration/test_cli_router.py
tests/integration/test_curate_gt.py
tests/integration/test_cv_failure_path.py
tests/integration/test_cv_profile_validation.py
tests/integration/test_cv_regression_path.py
tests/integration/test_cv_report_persistence.py
tests/integration/test_e2e_walking_skeleton.py
tests/integration/test_embedding_smoke.py
tests/integration/test_execution_failure_exit_code.py
tests/integration/test_freeze_gt_curation_gate.py
tests/integration/test_g3_b1_policy_guardrails.py
tests/integration/test_g3_b2_sqlite_plan_contract.py
tests/integration/test_g3_b3_2_fenced_receipts.py
tests/integration/test_g3_b3_3a_staged_publication.py
tests/integration/test_g3_b3_3b_finalization.py
tests/integration/test_g3_b3_structured_result_contract.py
tests/integration/test_g3_b4_1_worker_coexistence.py
tests/integration/test_g3_b4_2_ocr_router_durable_plan.py
tests/integration/test_g3_b4_3a_engine_staging.py
tests/integration/test_g3_b4_3b_publication_recovery.py
tests/integration/test_g3_b4_4_profile_projection_assembly.py
tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py
tests/integration/test_g3_b4_8_preserve_engine.py
tests/integration/test_g3_b4_9_reconciler_fencing.py
tests/integration/test_g3_chunk_identity_contract.py
tests/integration/test_g3_wal_stage_write_scope.py
tests/integration/test_g5_assembler_lease_recovery.py
tests/integration/test_g5_assembler_worker_integration.py
tests/integration/test_golden_parser.py
tests/integration/test_healing_concurrency.py
tests/integration/test_healing_e2e_telemetry.py
tests/integration/test_parameter_freeze.py
tests/integration/test_pdf_inbox_submission.py
tests/integration/test_pdf_pdf_fsm_transaction_ownership.py
tests/integration/test_pdf_pdf_sqlite_contracts.py
tests/integration/test_pdf_pdf_sqlite_g2_guardrails.py
tests/integration/test_pipeline_orchestration.py
tests/integration/test_pymupdf_extraction_integrity.py
tests/integration/test_real_e2e.py
tests/integration/test_real_paper.py
tests/integration/test_real_parser_pipeline.py
tests/integration/test_recovery_flow.py
tests/integration/test_regression_entry_point.py
tests/integration/test_translation_layer.py
tests/integration/test_translation_semantics.py
tests/integration/test_translation_structure.py
tests/integration/test_translation_technical.py
tests/integration/test_validation_integration.py
tests/integration/test_verification_pipeline_connection.py
tests/integration/test_w06_g3_uncertain_effect_offline.py
tests/integration/test_w08_cli_foreground_single_generation_offline.py
tests/integration/test_w08_durable_context_boundary.py
tests/integration/test_w08_ocr_g3_context_wiring.py
```

### tests/smoke — 1 módulos

```text
tests/smoke/test_invariants_smoke.py
```

### tests/ (raíz) — 7 módulos

```text
tests/test_architecture_contract.py
tests/test_ast.py
tests/test_dag.py
tests/test_fencing.py
tests/test_math_protector.py
tests/test_pipeline.py
tests/test_pipeline_fidelity.py
```

## Anexo B. Procedimiento para reproducir el censo sin ejecutar tests

GitHub: abrir el ref `9495259f1e35419ddf88c02a5649be6444ad062e` y enumerar `git/trees/<sha>?recursive=1` o usar la vista árbol del repo. Regla de filtrado: blobs Python con ``path.startsWith("tests/")``; módulos pytest por patrón ``/test_[^/]+\.py$/``; dividir en `unit`, `integration`, `smoke` y raíz. **Ningún test se ejecuta con este procedimiento**.

Un mantenedor puede comprobar sobre un **clon limpio** (sin ejecutar tests) con herramientas habituales:

```powershell
git rev-parse HEAD
git ls-files "tests/**/*.py" "tests/test_*.py"
git ls-files "tests/fixtures/**" "tests/output/**"
git status --short
```

La comparación debe estar pinneada al SHA y puede diferir si el clon tiene una rama nueva. No reconstruir la cifra de test cases a partir de este conteo.

## 8. Transición formal

**A-00 puede marcarse [x]** en el plan maestro tras archivar este documento y comprobar que su diff no contiene runtime, tests, corpus, workflows ni oráculos. **Siguiente tarea A-01**: clasificación dinámica/semántica por caso con fichas ``TR-###``, siempre sujeta al veto de seguridad `A-05` y sin mover D-4/D-5 al alcance activo.
