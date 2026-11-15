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

## 4. Gate y siguiente acción

- [x] **A01-COLL-01 — Colección real ejecutada** en clon independiente, SHA y cuatro exit codes 0 con conteos explícitos.
- [ ] **A01-COLL-02 — Conciliación JSON** de nodeids, parametrizaciones y markers efectivos.
- [ ] **A01-COLL-03 — Trazar todos los selectores focales del CI** y los SKIP/XFAIL declarados.
- [ ] **A01-COLL-04 — Verificar efectos de import/colección y estado Git posterior.**
- [ ] **A01-COLL-05 — Fichas SUT/contratos en los casos pertinentes**, sin presuponer oráculo independiente.
- [ ] **A-01 cerrado**: requiere conciliación y fichas conforme al plan maestro.
- [ ] **A-05 cerrado**: requiere revisión de seguridad de import/colección y resultados, no sólo conteos.

**Invariantes de gobierno:** `main` no cambia; el PDF eliminado deliberadamente permanece sin restaurar/commitear; no se tocan tests, runtime, CI, corpus ni GT; D-4/D-5 siguen fuera de alcance.
