# A-01 — Colección real de pytest en clon independiente (2026-11-15)

> **Estado:** EVIDENCIA DE COLECCIÓN RECIBIDA, **CONCILIACIÓN AÚN ABIERTA**. **No es ejecución de tests**.
>
> **Origen de evidencia:** salida PowerShell proporcionada por el owner; los JSON/logs locales todavía no fueron inspeccionados desde el repositorio remoto.
>
> **Rama:** `tests_stabilization`. **SHA exacto recolectado:** `86cd68672ee692f073b62869e7c9bd177e8d9e3b`.
>
> **Herramienta:** [`collect_a01_isolated.py`](collect_a01_isolated.py), opción explícita `--collect`.
>
> **Informe complementario de seguridad:** [A-05](A05_PREFLIGHT_A01_COLECCION_AISLADA.md).

## 1. Evidencia recibida

El owner ejecutó localmente:

```powershell
.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\collect_a01_isolated.py --repo-root . --collect
```

| Comprobación | Resultado observado |
|---|---|
| Revisión fijada | `86cd68672ee692f073b62869e7c9bd177e8d9e3b` |
| Clon temporal separado | `%LOCALAPPDATA%\Temp\translator-a01-isolated-k4f4mf10\repo` |
| Reportes locales | `%LOCALAPPDATA%\Temp\translator-a01-isolated-k4f4mf10\reports` |
| Archivos Python analizados estáticamente | **188** |
| Llamadas AST reportadas | **400** |
| Errores AST | **0** |
| `all` (sin filtro de markers) | **1.474 nodos**, exit **0** |
| `unit` (`-m unit`) | **225 nodos**, exit **0** |
| `integration_nonregression` (`-m "integration and not regression"`) | **70 nodos**, exit **0** |
| `technical` (`-m "not e2e"`) | **1.454 nodos**, exit **0** |
| Cuerpos de tests ejecutados | **0**; el programa sólo invocó `pytest --collect-only` |
| Resultado de cada test (PASS/FAIL/SKIP/XFAIL) | **NO MEDIDO** |

**El valor de `exit=0` significa colección sin errores reportados, no PASS de 1.474 pruebas.** Imports, decoradores y hooks sí se ejecutan durante la colección; no se ha demostrado ausencia completa de side effects a nivel del sistema operativo.

### Diferencias que debemos interpretar correctamente

- El [censo estático A-01](A01_INVENTARIO_CONSOLIDADO_Y_GATES.md) detectó **1.341 declaraciones de funciones**. La colección real encontró **1.474 ítems**, diferencia neta **+133**. **No atribuir automáticamente +133 a parametrizaciones**: la conciliación exige considerar funciones no recolectadas, fixtures, `unittest`, parametrizaciones y generación por plugins.
- `1.474 - 1.454 = 20` nodos excluidos por la expresión `not e2e`, **siempre que ambos JSON correspondan a la misma base de recolección y ninguna hook cambie la lista por ejecución**. Comparar node IDs para comprobarlo; esta resta **no prueba** por sí sola que sean veinte E2E reales.
- Los conjuntos `unit` e `integration_nonregression` son **subconjuntos por markers**, no particiones excluyentes de `all`; **no se deben sumar como cobertura**.
- La coincidencia de todos los exit codes en 0 no acredita SUT real, independencia de oráculo, sensibilidad, ausencia de SKIP/XFAIL ni protección científica.
- La selección focal por **paths explícitos** del workflow técnico aún debe contrastarse; los cuatro selectores no reproducen por sí solos todo el CI.

## 2. Artefactos locales (fuera de Git, por diseño)

| Archivo | Uso |
|---|---|
| `reports/manifest.json` | SHA, intérprete, selectors, exits y cantidad recolectada |
| `reports/all.json` | nodeids, markers efectivos y parámetro de cada ítem |
| `reports/unit.json` | nodeids de la selección unitaria |
| `reports/integration_nonregression.json` | nodeids de integración no regresión |
| `reports/technical.json` | nodeids de la selección técnica no E2E |
| `reports/*.log` | stdout/stderr de recolección; inspeccionar advertencias o plugins |
| `reports/static_signals.json` | scanner estático previo: **no** resultado de ejecución |

**No versionar volcados completos si incluyen rutas privadas o detalles de entorno**; el owner puede compartir sólo totales/síntesis. Preservar el clon hasta terminar la revisión de diferencias y la comprobación post-operación.

## 3. Conciliación pendiente — bloque de datos mínimo

Para completar A01-S4/S6 hay que obtener, **leyendo solamente los JSON locales**:

1. Número exacto de nodeids **únicos** en `all.json`; reportar cualquier duplicado.
2. Por marker efectivo: `unit`, `integration`, `regression`, `e2e`, `smoke`, `skip`, `skipif` y `xfail`. Las marcas skip/xfail son **declaradas**, no resultados de ejecución.
3. Total de nodos sin marker de nivel `unit/integration/e2e/regression/smoke`. **No declarar** que éstos no se recolectan: pueden estar dentro de `not e2e`.
4. Total de nodeids con `parameter_id` no nulo; **no confundir ítems parametrizados con funciones originales**.
5. Verificación de conjuntos: `unit ⊆ all`, `integration_nonregression ⊆ all`, `technical ⊆ all`; verificar que los 20 de `all - technical` tengan marker `e2e` y que `technical` no tenga `e2e`.
6. Los 10-15 archivos con más nodeids y los archivos en los que la cantidad de declaraciones difiere de los nodos recolectados. Diferencias no implican defecto automáticamente.
7. Aislamiento post-importación: `git status --short` en la copia del owner **comparado** con el inicial (PDF intencionalmente borrado), y `git status --short` dentro de la copia temporal; listar nuevos archivos/no rastreados bajo `tests/fixtures/`, `tests/corpus/` e `infra/db/` sin borrar nada.
8. Revisar los cuatro logs; marcar las advertencias de import/collection, el plugin set y dependencias que influyan en markers.

### PowerShell para una síntesis compacta (no ejecuta pytest)

```powershell
$reports = Join-Path $env:TEMP "translator-a01-isolated-k4f4mf10\reports"
$all = @((Get-Content (Join-Path $reports "all.json") -Raw | ConvertFrom-Json).items)
$unit = @((Get-Content (Join-Path $reports "unit.json") -Raw | ConvertFrom-Json).items)
$integration = @((Get-Content (Join-Path $reports "integration_nonregression.json") -Raw | ConvertFrom-Json).items)
$technical = @((Get-Content (Join-Path $reports "technical.json") -Raw | ConvertFrom-Json).items)

[pscustomobject]@{
    All = $all.Count
    AllUnique = @($all.nodeid | Sort-Object -Unique).Count
    Unit = $unit.Count
    IntegrationNonregression = $integration.Count
    Technical = $technical.Count
    ExcludedFromTechnical = $all.Count - $technical.Count
    WithParameterId = @($all | Where-Object { $null -ne $_.parameter_id }).Count
    WithoutLevelMarker = @($all | Where-Object {
        $m = @($_.markers)
        -not (@("unit","integration","e2e","regression","smoke") |
            Where-Object { $_ -in $m })
    }).Count
}

"Markers (declarados, no resultados):"
foreach ($mark in "unit","integration","regression","e2e","smoke","skip","skipif","xfail") {
    [pscustomobject]@{
        Marker = $mark
        Nodes = @($all | Where-Object { $mark -in @($_.markers) }).Count
    }
}

$allIds = @{}; $all | ForEach-Object { $allIds[$_.nodeid] = $true }
"Selectors outside all:"
foreach ($entry in @(
    @{Name="unit"; Items=$unit},
    @{Name="integration_nonregression"; Items=$integration},
    @{Name="technical"; Items=$technical}
)) {
    [pscustomobject]@{
        Selector = $entry.Name
        OutsideAll = @($entry.Items | Where-Object {
            -not $allIds.ContainsKey($_.nodeid)
        }).Count
    }
}
```

La lectura y presentación no modifica `tests/`. En PowerShell, las salidas tabulares pueden necesitar `Format-Table -AutoSize` para que todas las filas sean visibles.

## 3.1 Segunda conciliación a partir de JSON locales — 2026-11-15

**Evidencia:** salida PowerShell compartida por el owner, basada en los cuatro JSON de la carpeta temporal `translator-a01-isolated-k4f4mf10/reports`, SHA recolectado `86cd68672ee692f073b62869e7c9bd177e8d9e3b`. El contenido íntegro de los JSON sigue en la máquina local; no se copiaron ni subieron datos privados al repositorio.

| Observación | Resultado | Lo que demuestra |
|---|---:|---|
| Nodos `all` | **1.474** | Colección real, sin ejecución de tests |
| Nodeids únicos | **1.474** | **Cero duplicados** de nodeid en `all.json` |
| Selección `unit` | **225** | La expresión por marker devuelve 225 nodos |
| Selección `integration and not regression` | **70** | La expresión por marker devuelve 70 nodos |
| Selección `not e2e` | **1.454** | Excluye 20 nodos respecto al total, **por cantidad** |
| Nodos con `parameter_id != null` | **187** | Ítems parametrizados, **no** número de expansiones adicionales |
| Marker efectivo `unit` | **225** | Coincide **por cantidad** con el selector `unit` |
| Marker efectivo `integration` | **70** | Coincide **por cantidad** con `integration_nonregression` (marker `regression` es cero) |
| Marker efectivo `regression` | **0** | Ningún ítem recolectado declara este marker |
| Marker efectivo `e2e` | **20** | Coincide **por cantidad** con los 20 excluidos de `not e2e` |
| Marker efectivo `smoke` | **0** | No significa que `tests/smoke/` esté ausente de colección: es una **marca** |
| Marker efectivo `skip` | **0** | Marcadores declarados, no estado final de ejecución |
| Marker efectivo `skipif` | **1** | **Un caso condicionado**, no se comprobó si salta realmente |
| Marker efectivo `xfail` | **0** | Ningún marcador `xfail` declarado en ítems recogidos |

### Interpretación y hallazgos de selección

1. **No hay nodeids duplicados.** El inventario de 1.474 ítems es internamente único en la colección `all`.
2. **Marcas `regression` y `smoke` = 0.** Esto merece una ficha A-01: la pertenencia a carpetas no implica haber sido etiquetado con esas marcas. **No** se concluye que esas suites sean inútiles o que no estén seleccionadas por `-m "not e2e"`.
3. **La cobertura de markers es estrecha:** 225 `unit` y 70 `integration` frente a 1.474 nodos. Puede haber múltiples marcas o nodos sin marca; **todavía no** se calculó la unión ni la cifra precisa de casos sin marker de nivel. Investigar antes de atribuir alcance CI.
4. **187 `parameter_id` no explican directamente `+133` entre declaraciones estáticas (1.341) e ítems recolectados (1.474).** Esas métricas tienen denominadores distintos; quedan pendientes comparación por módulo y tratamiento de métodos de clases/funciones no recolectables.
5. **La igualdad de cantidades no prueba identidad de conjuntos.** Se debe verificar por `nodeid` que los 20 ítems excluidos sean exactamente los 20 marcados `e2e`, y que los conjuntos `unit`/`integration_nonregression` sean los seleccionados según sus markers.
6. **Inspección de integridad después de collection:** el owner ejecutó `git status --short` en el proyecto habitual y en el clon temporal. Se mostró **solo** la eliminación deliberada del PDF en el proyecto habitual y **ninguna línea** para el clon. Esto confirma **ausencia de cambios visibles en `git status --short`**; no demuestra ausencia de archivos ignorados, efectos fuera del clon, red o cambios no observables por Git.

### Resto de la conciliación

- [x] **Número y unicidad de nodos:** 1.474/1.474.
- [x] **Conteos por los ocho markers consultados:** registrados arriba, con `skipif` correctamente diferenciado de SKIP efectivo.
- [x] **Nodos con parámetro:** 187.
- [x] **Estado Git visible tras colección:** proyecto conserva solo PDF `D`, clon sin cambios visibles.
- [x] **Identidad de conjuntos de selección** por `nodeid`: cuatro discrepancias = 0, cotejadas con los recuentos por marker; análisis simétrico reproducible disponible en [`analyze_a01_collection.py`](analyze_a01_collection.py).
- [ ] **Nodos sin marker de nivel** y distribución por archivo; reconciliar declaraciones vs. ítems.
- [ ] **Selección explícita de paths en CI**, logs y advertencias de colección; clasificar el `skipif` declarado.
- [ ] **Revisar archivos ignorados/efectos externos** si hay indicios; el estado Git limpio no prueba sandbox OS.

**Alcance:** evidencia de colección **reproducible**, no validación semántica de los tests ni medición de su poder para detectar regresiones.

## 3.2 Identidad de selectores y caso `skipif` investigado (2026-11-15)

**Evidencia aportada por el owner, basada en los JSON del mismo SHA de colección:** las cuatro pruebas de consistencia de seleccionadores dieron **0 discrepancias**: `E2EMissingFromTechnical=0` (ningún ítem marcado e2e quedó en technical), `UnexpectedTechnicalExclusions=0` (ningún ítem no-e2e fue excluido), `UnexpectedUnitSelections=0` y `UnexpectedIntegrationSelections=0`. Junto a los recuentos ya observados **all=1.474**, **unit=225**, **integration_nonregression=70**, **technical=1.454** y **e2e=20**, los selectores se corresponden con sus markers por contenido, no sólo por cantidad.

**Límite metodológico:** las cuatro comprobaciones aportadas prueban la dirección de exclusión/inclusión expresada. Para formalizar igualdad bidireccional de los conjuntos `unit` e `integration_nonregression`, junto a supuestos de unicidad ya confirmados, se usó también la igualdad de cardinalidades con los respectivos markers. Un script de conciliación de solo lectura [`analyze_a01_collection.py`](analyze_a01_collection.py) permite verificar simétricamente `expected - observed` y `observed - expected` con los JSON locales y detectar divergencias por fichero.

**El único marker `skipif`:** `tests/integration/test_parameter_freeze.py::test_repo_freeze_artifact_matches_domain_defaults`. Inspección del [test](../../../../tests/integration/test_parameter_freeze.py): `REAL_FREEZE = Path('reports/calibration/parameter_freeze.json')` (línea 132); `@pytest.mark.skipif(not REAL_FREEZE.exists(), reason='Artefacto de freeze no materializado')` (línea 135). El archivo `reports/calibration/parameter_freeze.json` **existe versionado** en el árbol Git. **Inferencia limitada:** en un clon independiente de ese mismo commit, con el cwd estándar de pytest, la condición debería ser falsa. La prueba se recolectó, pero **no se ejecutó** y no hay evidencia de PASS ni de su resultado efectivo de skip. El caso verifica tooling de congelación/identidad científica; **fuera del alcance activo del refinamiento técnico PDF→PDF**, conservar y reclasificar sin alterar el freeze ni la baseline.

**Estado de selección por markers:** `regression=0` y `smoke=0` son **declaraciones ausentes**, no ausencia de módulos o ejecución seleccionable. Los tests marcados `unit`/`integration` son un subconjunto pequeño; la suite técnica también incluye pruebas sin estos markers. El seguimiento de su validez real permanece en A-02/A-03.

**Pendientes para completar A-01:** distribución de nodos por fichero y comparación con 1.341 declaraciones; identificación de módulos no seleccionados, tests legacy/ciencia vs ruta OCR/G3/G5, paths focales de CI, y lectura de advertencias/plugins en logs. Los reportes locales no necesitan publicarse enteros. **A-01 [ ]**, A-05 [ ].

## 3.3 Conciliación ampliada por archivo y selección CI — 2026-11-15

**Fuente:** salida JSON del analizador de sólo lectura `analyze_a01_collection.py` proporcionada por el owner, calculada sobre los reportes de colección SHA `86cd68672ee692f073b62869e7c9bd177e8d9e3b` y el código local. El análisis no ejecutó tests, no escribió archivos y no certifica calidad del pipeline.

### Cierre de igualdad bidireccional por nodeid

| Conjunto | Seleccionados | Únicos | `missing_expected` | `unexpected` | `duplicates` |
|---|---:|---:|---:|---:|---:|
| `all` | 1.474 | 1.474 | 0 | 0 | 0 |
| `unit` | 225 | 225 | 0 | 0 | 0 |
| `integration_nonregression` | 70 | 70 | 0 | 0 | 0 |
| `technical` (`not e2e`) | 1.454 | 1.454 | 0 | 0 | 0 |

**Confirmado:** cuatro selecciones correctas **en ambos sentidos**, sin IDs duplicados. Los **187 `parameter_id`** son ítems parametrizados; no equivalen por sí solos a 187 nuevos casos adicionales.

### Cobertura de markers y consecuencia operacional

- **1.159/1.474 nodos sin ninguno de los cinco markers de nivel** (`unit`, `integration`, `e2e`, `regression`, `smoke`). Representan aproximadamente **78,6 %** de los nodos. Se recolectan y, si no están marcados e2e, pueden entrar por la suite global del CI; **sin marker no equivale a «no se ejecuta»**.
- **225** marcados `unit`, **70** `integration`, **20** `e2e`, **0** `regression`, **0** `smoke`, **1** `skipif`, sin `skip` o `xfail` declarados. El `skipif` de freeze de parámetros sigue siendo una condición, no un SKIP observado.
- La marca `not e2e` **no excluye por sí misma los tests técnicos del tooling científico** que carecen de `e2e`; por tanto, el nombre «suite técnica» en el CI debe leerse como **selector**, no como garantía de exclusión total del ámbito científico. No cambiar el CI en A-01.

### Módulos y divergencias de fuente

| Medida | Resultado | Interpretación |
|---|---:|---|
| Archivos candidatos con `test_*.py` en tree (A-00) | 177 | Archivos fuente, no casos |
| Archivos con al menos un nodo recolectado | **173** | Pendientes **4 módulos de los 177** de identificar por nombre y explicar |
| Declaraciones estáticas identificadas | 1.341 | AST aproximado, incluye cuerpos anidados y otras definiciones |
| Nodos de pytest reales | 1.474 | Parametrizaciones y selección dinámica; diferencia neta **+133** |
| Archivos con diferencia nodo vs declaración | **24** | Requiere clasificar causa, no se presupone error |

Los archivos con mayor divergencia *nodos menos declaraciones* son:

| Módulo | Nodos | Declaraciones AST | Diferencia |
|---|---:|---:|---:|
| `test_g3_b3_structured_result_contract.py` | 33 | 12 | +21 |
| `test_b024_explicit_math_spans.py` | 18 | 4 | +14 |
| `test_w08_inference_identity_contract.py` | 21 | 8 | +13 |
| `test_semantic_classification.py` | 17 | 7 | +10 |
| `test_g3_b4_3a_engine_staging.py` | 25 | 18 | +7 |
| `test_b025_math_visual.py` | 15 | 8 | +7 |
| `test_b032_offline_pdf_lab.py` | 16 | 9 | +7 |
| `test_provenance_identities.py` | 19 | 12 | +7 |

**No diagnosticar estos +21, +14, etc. automáticamente como duplicación:** varios tests parametrizados generan más nodos que funciones. Se deben explicar diferencias **por función y archivo** antes de cerrar A01-S6; además, los cuatro archivos sin nodos requieren clasificación (script, test no coleccionable u otro caso).

### Doce rutas focales de CI encontradas en workflow, con colección no vacía

| Archivo incluido explícitamente en `.github/workflows/ci.yml` | Nodos recolectados |
|---|---:|
| `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py` | 10 |
| `tests/integration/test_g3_b4_3a_engine_staging.py` | 25 |
| `tests/integration/test_g3_b4_3b_publication_recovery.py` | 21 |
| `tests/integration/test_g3_b4_7b_sqlite_quota_thread_owner.py` | 3 |
| `tests/integration/test_g3_b4_8_preserve_engine.py` | 3 |
| `tests/integration/test_g3_b4_9_reconciler_fencing.py` | 14 |
| `tests/integration/test_g5_assembler_worker_integration.py` | 3 |
| `tests/integration/test_w06_g3_uncertain_effect_offline.py` | 7 |
| `tests/integration/test_w08_durable_context_boundary.py` | 13 |
| `tests/integration/test_w08_ocr_g3_context_wiring.py` | 6 |
| `tests/unit/test_b031_g3_reusable_fake.py` | 17 |
| `tests/unit/test_b032_offline_pdf_lab.py` | 16 |
| **12/12 rutas, total de nodos** | **138** |

**Alcance exacto:** los doce paths incluidos explícitamente en CI existen y todos aportaron nodos a la colección. Los **138** son el total por esos archivos, **no** ejecuciones exitosas ni una muestra disjunta respecto de los selectores `unit/integration/technical`, que pueden contener esos mismos casos. Verificación de ausencia de duplicaciones entre pasos de CI, condiciones del job y resultados **no realizada**.

### Reportes y salud de colección

Los cuatro logs `all/unit/integration_nonregression/technical` reportaron, según el analizador: **0 líneas `ERROR collecting`**, **0 secciones `warnings summary`** y **0 menciones `PytestCollectionWarning`**. El resultado no excluye cualquier otro tipo de advertencia, efectos de imports, red o archivos ignorados; es un chequeo textual acotado.

### Pendientes para cerrar la auditoría

- [x] Unicidad de nodeids; igualdad bidireccional de los cuatro selectores y conteos por marker.
- [x] Conteo de ítems parametrizados, nodos sin marker de nivel y distribución numérica por archivo.
- [x] Verificación de **12/12** rutas focales CI con nodos recolectados; revisión automatizada de las tres señales de advertencias/errores en cuatro logs.
- [ ] Identificar y clasificar los **4 módulos** con 0 nodos; explicar las **24 diferencias** de nodos versus declaración, prioritariamente las de la ruta PDF→PDF.
- [ ] Verificar impacto de imports en archivos ignorados o fuera del clon y revisar riesgos transitivos de plugins/host (A-05).
- [ ] Completar para cada caso relevante SUT, mocks, efectos externos, contrato observable y clasificación (A-02/A-04). **A-01 permanece [ ]** hasta trazabilidad definida en el plan.

## 4. Gate y siguiente acción

- [x] **A01-COLL-01 — Colección real ejecutada** en clon independiente, SHA y cuatro exit codes 0 con conteos explícitos.
- [x] **A01-COLL-02 — Conciliación de colecciones y markers.** Ver §3.3: unicidad, 4 conjuntos con diferencias bidireccionales cero, 187 parametrizados, 1.159 sin marcador de nivel, 173 módulos con nodos y 24 diferencias AST registradas. La **explicación individual de las diferencias** se mantiene como tarea separada A01-S6.
- [x] **A01-COLL-03 — Selección focal CI y marcadores declarados.** Ver §3.3: 12/12 archivos focales de CI con 138 nodos; markers `skip=0`, `skipif=1` (freeze de parámetros), `xfail=0`. No equivale a ejecución ni a PASS.
- [ ] **A01-COLL-04 — Integridad post-colección (PARCIAL).** Ambos `git status --short` observados: solo PDF `D` deliberado en original, clon sin cambios Git visibles. Los cuatro logs no presentan las tres señales textuales auditadas. **Faltan archivos ignorados y efectos externos/imports/plugins**; no equivale a aislamiento OS.
- [ ] **A01-COLL-05 — Fichas SUT/contratos en los casos pertinentes**, sin presuponer oráculo independiente.
- [ ] **A-01 cerrado**: requiere conciliación y fichas conforme al plan maestro.
- [ ] **A-05 cerrado**: requiere revisión de seguridad de import/colección y resultados, no sólo conteos.

**Invariantes de gobierno:** `main` no cambia; el PDF eliminado deliberadamente permanece sin restaurar/commitear; no se tocan tests, runtime, CI, corpus ni GT; D-4/D-5 siguen fuera de alcance.
