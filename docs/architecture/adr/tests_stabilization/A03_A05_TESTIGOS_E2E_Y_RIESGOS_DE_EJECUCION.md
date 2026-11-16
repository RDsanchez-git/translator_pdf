# A-03/A-05 — Testigos E2E históricos y riesgos de ejecución

> **Estado:** inspección estática dirigida; **A-03, A-04, A-05 y A01-S5 continúan ABIERTOS**. Revisión de fuentes sobre SHA de tests `86cd68672ee692f073b62869e7c9bd177e8d9e3b`, sin ejecutar pruebas, modificar producción ni tocar GT. Un riesgo condicional de código **no es evidencia de un efecto realmente producido** durante `--collect-only`.

## 1. Alcance efectivo de pruebas con nombres E2E/real

| Hallazgo | Archivo y zona | SUT / afirmación real | Diagnóstico estático |
|---|---|---|---|
| **A03-E2E-01** | [`test_real_e2e.py`](../../../../tests/integration/test_real_e2e.py) 97–171 | Se construye `TranslationPipeline`, pero `execute` se **parchea** para devolver `mock_result`. `job.status = COMPLETED` y los importes/tokens se asignan manualmente | **Falsa garantía de ejecución y FinOps E2E**, no prueba de traducción ni auditoría de costo real. El objeto de salida puede servir solo a prueba de consumidor/shape |
| **A03-E2E-02** | [`test_e2e_walking_skeleton.py`](../../../../tests/integration/test_e2e_walking_skeleton.py) 37–100, 131–194 | `AsyncDispatcher.dispatch` corre dos veces y hay `CachedLLMProvider` real con proveedor falso; **no** parser físico, daemons G3/G5 ni PDF final | El test **escribe** `model_name="cache_hit:..."` en el `TranslatedUnit` y luego lo afirma. Sustituye `SummaryBuilder.build` con resumen simulado que ya contiene hit ratio/costo positivo. **Las aserciones no acreditan un cache hit real** |
| **A03-E2E-03** | [`test_pipeline_orchestration.py`](../../../../tests/integration/test_pipeline_orchestration.py) 71–142 | `TranslationPipeline.execute` **real**, pero parser `parse` simulado, `FakeChunker` y `FakeDispatcher` | Conserva un test de **orquestación/estado** válido para su frontera, no extracción de PDF real ni PDF→PDF |
| **A03-E2E-04** | [`test_real_parser_pipeline.py`](../../../../tests/integration/test_real_parser_pipeline.py) 20–53 | `adapter.parse` parcheado con cuatro ASTNodes fabricados | Esperados de tipo, ID y cantidad verifican el **mock**, no parser real. Existe [test con parser real](../../../../tests/integration/test_verification_pipeline_connection.py) reutilizable |
| **A03-E2E-05** | [`test_healing_e2e_telemetry.py`](../../../../tests/integration/test_healing_e2e_telemetry.py) 33–114 | `HealingPipeline.heal_and_revalidate` y telemetría reales, validador artificial | Útil como **integración de healing**, no E2E PDF→PDF. Cinco funciones `test_e2e_*` sin `@pytest.mark.e2e` visible: verificar inclusión exacta con `technical.json` |
| **A03-E2E-06** | [`tests/test_pipeline_fidelity.py`](../../../../tests/test_pipeline_fidelity.py) 17–58 | `InlineMathProtector.mask/restore` y enums reales | Invariantes técnicos aprovechables; no fidelidad lingüística/PDF final |
| **A03-REC-01** | [`test_recovery_flow.py`](../../../../tests/integration/test_recovery_flow.py) 23–143 | `AbandonedProcessWatchdog.execute_sweep`, `OnDemandResumeManager.rescue_stalled_document` y FSM reales; al final `TranslationPipeline.execute` parcheado para **escribir manualmente COMPLETED** | Preservar aserciones del **watchdog y resumer**, pero no atribuir a ese caso ejecución real de pipeline |

**Regla:** el nombre, clase o docstring «E2E» **no constituye** marker `e2e` ni verifica ejecución. El selector `not e2e` puede incluir pruebas con ese nombre. La pertenencia exacta se obtiene de los reportes de colección; tampoco equivale a PASS.

## 2. Seguridad: efectos comprobados en fuente, no observados en ejecución

| Riesgo | Fuente / instante | Impacto potencial y decisión |
|---|---|---|
| **A05-FS-01 / P0 — eliminación de base de datos preexistente** | `test_recovery_flow.py` líneas 23–32 y 135–142: `setUpClass/tearDownClass` usan `os.remove(BASE_DIR/infra/db/test_fsm.db)` | **No ejecutar en el checkout del owner.** Si el archivo existe, puede borrarlo. La redirección `SQLITE_STATE_DIR` de `get_connection` **no protege el `os.remove` directo** |
| **A05-GLOBAL-01 / P0 — contaminación global Python** | `test_recovery_flow.py` 94–95: `core.pipeline.orchestrator.compute_ast_hash = lambda ...` sin restauración ni scope de patch | Otros tests del mismo proceso podrían recibir una función alterada; usar `patch`/`monkeypatch` con restauración en B sin perder las aserciones reales de recovery |
| **A05-FS-02 / P1 — SQLite real en setup** | `test_real_e2e.py` 107–109 y `test_pipeline_orchestration.py` 100–102: `get_connection("infra/db/documents.db")` | `sqlite3.connect`/PRAGMAs WAL pueden afectar o crear DB/sidecars. El mock de `execute` **no elimina** este I/O de setup. Usar `tmp_path` e independencia de estado |
| **A05-FS-03 / P0 — cache local fija** | `test_e2e_walking_skeleton.py` 37–44, 67–68, 93–100: `tests/fixtures/e2e_cache_real.db`, inicialización y posterior eliminación DB/WAL/SHM | Colisión con otros tests/datos y escritura en fixtures; trasladar a `tmp_path` y cerrar DB antes de limpiar; no ejecutar sobre archivos persistentes |
| **A05-FS-04 / P1 — fabricación de «PDF» no válido** | `test_real_parser_pipeline.py` 9–18 y `test_pipeline_orchestration.py` 113–117 crean en `tests/fixtures/sample_3_pages.pdf` un dummy si falta | Puede ocultar una fixture ausente o contaminarla. Fallo de precondición explícito, o PDF sintético válido fuera del árbol versionado |
| **A05-IMPORT-01 / P1 — cambio del import path** | `test_recovery_flow.py` 9–10 y `tests/test_pipeline_fidelity.py` 1–6: `sys.path.append` a nivel módulo | Mutación **in-memory durante import/colección**, no I/O de disco ni red por sí misma. Revisar dependencia del orden de imports antes de B |
| **A05-SCOPE-01 / diferido** | [`test_translation_semantics.py`](../../../../tests/integration/test_translation_semantics.py) 101–139: `_mock_embed_text` retorna siempre `[0.5] * 10` | Similaridad entre vectores idénticos constante; no es garantía de fidelidad semántica ni CV científica. Preservar GT y diferir cualquier remediación de ciencia |

El walking skeleton **sí** construye objetos útiles con dispatcher/cache y puede tener algún valor técnico para reentrancia, pero las aserciones `cache_hit`/métricas **son autorreferentes**. No descartar un test solo por tener dobles legítimos: el defecto depende de *qué propiedad promete* y *cómo la comprueba*.

## 3. A-05 — Fronteras aún no acreditadas

**A05-P4:** no hay revisión completa de imports/decoradores transitivos y plugins, ni prueba de egress negado por sistema operativo. La colección anterior se ejecutó en un clon con un guard de Python de mejor esfuerzo; eso **no equivale** a contenedor/VM con aislamiento de red/filesystem.

**A05-P6:** `git status` limpio del clon descarta cambios rastreados, pero **no** revela todos los ignorados, archivos nuevos, efectos fuera del repo ni alteraciones del host. Se agregó [`inspect_a05_isolated_artifacts.py`](inspect_a05_isolated_artifacts.py), una comprobación **de solo lectura del clon retenido y de los JSON de colección**, sin importar tests ni procesar PDFs. Enumerará `tests/` y `infra/db/` ignorados/untracked y consultará rutas de riesgo por existencia y tamaño. **El owner ejecutó el inspector**: [resultado A-05](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md): 0 cambios versionados, 0 untracked y 0 ignorados bajo `tests/` e `infra/db/`; además, **11/11 nodos de siete archivos históricos entran en `not e2e`**. La inspección posterior no tiene baseline anterior ni prueba ausencia de efectos externos.

**Límite fundamental:** un inventario **posterior** sin snapshot previo **no permite atribuir cuándo o quién creó los archivos**; las entradas `__pycache__` tampoco prueban que los cuerpos de los tests se ejecutaran. La herramienta NO cierra A05-P6 ni demuestra aislamiento OS.

### Comprobación local de solo lectura

```powershell
git pull --ff-only origin tests_stabilization

$clone = Join-Path $env:TEMP "translator-a01-isolated-k4f4mf10\repo"
$reports = Join-Path $env:TEMP "translator-a01-isolated-k4f4mf10\reports"

.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\inspect_a05_isolated_artifacts.py --isolated-repo $clone --reports $reports --limit 35
```

**No ejecutar ninguno de los tests anteriores sobre el working tree. No limpiar, resetear, borrar ni restaurar el PDF eliminado intencionalmente.** No ejecutar scripts de bootstrap de golden ni regenerar snapshots.

## 4. Falsadores contractuales pendientes (fase C)

| ID | Violación controlada en sandbox descartable | Oráculo exigido |
|---|---|---|
| **F-E2E-01** | `TranslationPipeline.execute` real falla | El test de ejecución real **debe** fallar; el mock que retorna `MagicMock` no cuenta |
| **F-CACHE-01** | El proveedor fake recibe dos requests para la misma identidad | Conteo externo **observado**, no valor `model_name` escrito por test |
| **F-CACHE-02** | `SummaryBuilder` real registra 0 hits/costo | Métrica real falsifica expected; no comparar contra `mock_summary` |
| **F-REC-01** | `OnDemandResumeManager` falla al recuperar estado | FSM tras reopen y transición normativa detectan la violación |
| **F-GLOBAL-01** | Se mantiene `compute_ast_hash` parcheado tras un test | Aserción de restauración del símbolo original |
| **F-IO-01** | DB/fixture requerida ausente | Falla de precondición, **cero escritura en directorios persistentes** |

## 5. Subgates

- [x] **A03-E2E-P1:** testigos E2E y parser inspeccionados, SUT real/mocks separados.
- [x] **A03-E2E-P2:** autovalidación de caché/FinOps y estado `COMPLETED` documentada por fuente.
- [x] **A05-SAFE-P1:** DB fija, borrado y patch global no restaurado identificados.
- [x] **A05-SAFE-P2:** escritura potencial en `setUp` separada del SUT de ejecución y cambio de `sys.path` por import.
- [x] **A05-SAFE-P3:** [inspección de solo lectura del clon realizada por el owner](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md): 0 cambios versionados/untracked/ignorados en las dos rutas y 11/11 nodos históricos seleccionados por `not e2e`. **P4/P6 globales abiertos.**
- [ ] **A05-P4/P6:** revisión de imports/host y efectos OS; no se dispone de baseline previo ni aislamiento de red acreditado.
- [ ] **A-03/A-04/B-03/B-05:** otras familias, clasificación final y remediaciones aún pendientes. **No declarar PASS.**

**Decisión de gobierno:** se preservan las pruebas de estado y healing realmente ejercitadas; se remedia el oráculo falso/sobrealcance, no la producción para «volver verde». Se mantiene íntegramente fuera de campaña el Ground Truth y CV científico.
