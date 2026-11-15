# A-05 (preflight parcial) — Colección A-01 en clon separado

> **Fecha:** 2026-11-15  
> **Estado:** PROCEDIMIENTO PREPARADO Y PROBADO CON REPOSITORIO SINTÉTICO. **No ejecutado sobre `translator_pdf`**. No se marca A-05 ni A-01 completos.  
> **Ramas:** `tests_stabilization` (trabajo), `main` (intacta).  
> **Herramienta:** [`collect_a01_isolated.py`](collect_a01_isolated.py).  
> **Ámbito:** seguridad de **colección de pytest** para contrastar declaraciones estáticas (A-01). **No autoriza ejecución de tests, mutaciones o evaluación científica.**

## 1. Qué significa «entorno descartable» aquí

Un **clon Git independiente** en un directorio temporal nuevo, fuera del working tree habitual del owner. Se fija el SHA, se hace checkout **detached**, se elimina el remoto del clon, se redirigen cachés y `HOME`/temp del proceso, se preserva intacta la copia del owner y se guardan los resultados fuera del repositorio original. Los cambios de archivos relativos —por ejemplo `tests/fixtures/*.json` o `infra/db/test_fsm.db`— sucederían en el clon, nunca en la copia del owner.

**Límite de seguridad esencial:** un clon separado **no es una sandbox de sistema operativo**. Si el código importado contiene rutas absolutas, invoca procesos externos, abre sockets nativos o accede directamente al HOME verdadero, puede escapar de la copia. El guard de sockets Python es *best-effort*, no una barrera de red. Para código no confiable exigir VM/contenedor con filesystem y red restringidos a nivel del host antes de usar `--collect`. Los imports pueden ejecutar código aunque `--collect-only` no ejecute las funciones de prueba.

**Por qué el preflight es necesario:** A-00 registró `IO-01…IO-06`: autogeneración de fixtures en `test_golden_parser.py`, `test_real_parser_pipeline.py`, `test_pipeline_orchestration.py` y `test_e2e_walking_skeleton.py`, autogeneración de snapshot en `test_chunker_snapshot.py`, rutas SQLite fijas y borrados en `test_recovery_flow.py`. Son códigos reales vistos en el SHA base; aún se requiere revisar sus efectos de import/colección antes de ejecutar el modo opt-in.

## 2. Evidencia existente y límites

- **A-00** — Inventario del código: [`A00_BASELINE_INVENTARIO_Y_RIESGOS.md`](A00_BASELINE_INVENTARIO_Y_RIESGOS.md).
- **A-01** — 177 archivos de módulos candidatos y 1.341 declaraciones estáticas: [`A01_INVENTARIO_CONSOLIDADO_Y_GATES.md`](A01_INVENTARIO_CONSOLIDADO_Y_GATES.md). No son 1.341 ítems coleccionados.
- **Revisión puntual del preflight:** `test_recovery_flow.py` sitúa el borrado de `infra/db/test_fsm.db` en `setUpClass`/`tearDownClass`, es decir, ejecución de unittest y no definición de prueba. En `test_e2e_walking_skeleton.py` los writes detectados están en `asyncSetUp` y `asyncTearDown`. Esto reduce el riesgo de colección **de esos fragmentos**, pero no demuestra ausencia global de I/O por import, decoradores, módulos externos o plugins.
- **Ejercicio del ejecutor:** se probó en repositorio Git sintético de **1 módulo**, con tres funciones base (`unit`, `integration` parametrizada tres veces y `e2e`). En modo prepare-only no ejecutó pytest; en modo opt-in recolectó **5 nodos totales / 1 unit / 3 integration / 4 technical**, con exit code 0 para los cuatro selectores. **No es evidencia de colección del proyecto real.**
- **Disponibilidad remota:** el entorno de ejecución del asistente no tiene conectividad Git HTTPS hacia GitHub ni la copia real del owner; el conector GitHub permite leer/escribir archivos, no ejecutar pytest en el repositorio remoto. **La colección real se mantiene pendiente**.

## 3. Procedimiento de uso (Windows PowerShell, desde raíz del repo)

**Inspeccionar antes de ejecutar:**

```powershell
git status --short
git fetch origin
git switch tests_stabilization
git rev-parse HEAD
```

Esta comprobación no restaura PDFs deliberadamente eliminados ni altera oráculos. Si la copia local tiene cambios de trabajo, preservarlos.

**Paso 1 — Crear clon independiente y ejecutar sólo análisis AST de archivos Python (recomendado ahora):**

```powershell
.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\collect_a01_isolated.py --repo-root .
```

El programa muestra el SHA fijado, carpeta `Isolated copy` y carpeta `Reports`; genera `static_signals.json` y `manifest.json`. **Sin `--collect`, no importa los tests ni ejecuta pytest.** No ejecuta borrado ni limpieza automática. El clon está en una carpeta nueva de `$env:TEMP` (no bajo el proyecto).

**Paso 2 — Revisión de seguridad (PENDIENTE ANTES DE ACTIVAR):** revisar `static_signals.json`, imports/colección potencialmente peligrosa, dependencias necesarias y que el clon no tenga acceso a credenciales ni paths ajenos. Para aislamiento de seguridad completo usar VM/contenedor con filesystem y egress host-restringidos. En caso de duda, **no ejecutar `--collect`**.

**Paso 3 — Colección opt-in, sólo después de aprobar el preflight:** 

```powershell
.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\collect_a01_isolated.py --repo-root . --collect
```

Este paso crea **otro clon temporal nuevo**, no reutiliza el anterior. No llama a las funciones de tests, pero sí importa módulos y evalúa hooks/decoradores. Incluye la prueba de cuatro selecciones: todos los nodos, `-m unit`, `-m "integration and not regression"` y `-m "not e2e"`. El reporte `all.json` incluye nodeids, markers efectivos, ids de parametrización y marcas skip/xfail **declaradas**; **no** estados ejecutados de skip/xfail. Si el primer selector falla por import/dependencia, se detiene sin presentar números como cobertura. Los logs quedan en `Reports`. `pytest` se invoca con `-o addopts=` para evitar que el `-m not e2e` por defecto altere la selección `all`; se desactiva `cacheprovider` para no generar `.pytest_cache`.

**Nota de precisión:** el script usa el intérprete invocante (el venv 3.11 del proyecto), no instala ni cambia paquetes; el shell conserva el repo original mientras se ejecuta el subprocess con `cwd` del clon. Los plugins autodescubiertos de pytest permanecen presentes, para reproducir la selección real. Si el plugin set causa efectos o dependencias, documentar y ejecutar en un contenedor sin red en lugar de en la PC habitual.

## 4. Verificaciones post-operación obligatorias

- La SHA indicada debe coincidir con la rama remota `origin/tests_stabilization` obtenida tras `git fetch`. No dar por válido un SHA inesperado.
- Comparar `git status --short` antes y después en la copia del owner. **No corregir el estado usando limpieza o reset destructivo**.
- Conservar los archivos de `Reports` fuera del proyecto para evidencia de A-01; revisar si contienen rutas o configuraciones sensibles antes de publicar.
- Inspeccionar el clon temporal **antes de borrarlo**. La herramienta no lo borra; sólo eliminarlo cuando se compruebe inequívocamente su ruta temporal y se hayan conservado los logs. **Nunca ejecutar `Remove-Item -Recurse` sobre la raíz del proyecto ni sobre rutas no verificadas**.
- Los reportes no validan ejecución efectiva de tests, ausencia de red a nivel OS, ni seguridad universal de importación. Si aparecen errores de colección, registrar `INCOMPLETE`, la causa y el SHA, no “PASS”.

## 4.1 Evidencia local aportada por el owner — preparación real, sin importación

**Fecha de registro:** 2026-11-15. **Origen:** salida de consola PowerShell aportada por el owner (los JSON locales aún no fueron inspeccionados de forma independiente).

| Campo | Resultado observado |
|---|---|
| Comando | `venv/Scripts/python.exe docs/architecture/adr/tests_stabilization/collect_a01_isolated.py --repo-root .` (sin `--collect`) |
| Revisión fijada | `268240d2c0018b0f67783a67d5b4386cd7efcd60` |
| Archivos Python inspeccionados | **188** |
| Señales de llamadas AST | **390**, **no** equivalen a fallos, escrituras realizadas ni hallazgos de seguridad confirmados |
| Carpeta separada | `%LOCALAPPDATA%/Temp/translator-a01-isolated-vlqmrcki/repo` (ubicación local observada; no existe en GitHub) |
| Informes | `%LOCALAPPDATA%/Temp/translator-a01-isolated-vlqmrcki/reports` |
| Modalidad | **PREPARED ONLY** — ninguna importación de tests ni colección o ejecución pytest |

**Estado de aprobación:** se confirma **sólo que la preparación real terminó**. Todavía falta leer y agrupar `static_signals.json`, contrastar posibles operaciones en import/decoradores y revisar el `manifest.json` para acreditar A05-P4. No se dispone de evidencia de `--collect`, ni de sandbox OS, ni de comparación posterior de `git status`; A05-P4/P5/P6 permanecen [ ].

**Próximo dato requerido:** recuentos de `signal` y archivos con operaciones de riesgo, sin compartir credenciales, rutas privadas adicionales ni el volcado completo de 390 señales. Registrar los resultados antes de habilitar cualquier importación.

## 4.2 Resultado del agrupamiento de señales — evidencia aportada por owner

**Fecha:** 2026-11-15. El owner leyó `static_signals.json` y aportó dos agrupamientos de PowerShell, además del estado del árbol local. **No se ha inspeccionado aquí el JSON completo**. El total de preparación permanece en **390 señales AST sobre 188 archivos Python**.

**Tipos de señal que aparecen en la salida compartida:**

| Señal | Cantidad mostrada | Interpretación |
|---|---:|---|
| `get` | 61 | Llamada léxica no necesariamente peligrosa |
| `mkdir` | 57 | Llamada léxica no necesariamente peligrosa |
| `open` | 34 | Llamada léxica no necesariamente peligrosa |
| `write_bytes` | 27 | Revisar contexto, destinatario y fase de ejecución |
| `replace` | 25 | Revisar contexto, destinatario y fase de ejecución |
| `save` | 19 | Revisar contexto, destinatario y fase de ejecución |
| `run` | 16 | Revisar contexto, destinatario y fase de ejecución |
| `write_text` | 12 | Revisar contexto, destinatario y fase de ejecución |
| `syntax_error` | 12 | El analizador no pudo parsear el archivo; requiere triage individual |
| `remove` | 7 | Revisar contexto, destinatario y fase de ejecución |
| `dump` | 6 | Revisar contexto, destinatario y fase de ejecución |
| `makedirs` | 5 | Revisar contexto, destinatario y fase de ejecución |
| `call` | 4 | Revisar contexto, destinatario y fase de ejecución |
| `unlink` | 4 | Revisar contexto, destinatario y fase de ejecución |
| **Suma de filas compartidas** | **289** | **Difiere de las 390 señales globales**; faltan **101** en el texto mostrado. Puede haber truncamiento o un recuento parcial; **no interpretar las filas anteriores como exhaustivas** |

**`syntax_error` = 12 registros:** `flagged_calls` emite a lo sumo uno por módulo que `ast.parse` no puede analizar y no inspecciona sus llamadas internas. Hasta conocer **archivo/línea/detalle** no se pueden atribuir esos errores a una causa o considerar exhaustivo el preflight. Un `syntax_error` del scanner **no es prueba** de fallo de ejecución pytest.

**Archivos con mayor número de señales de escritura/borrado identificadas en la salida:**

| Archivo | Señales |
|---|---:|
| `tests/integration/test_pdf_inbox_submission.py` | 9 |
| `tests/integration/test_g3_chunk_identity_contract.py` | 4 |
| `tests/integration/test_b03_foreground_pdf_product.py` | 4 |
| `tests/integration/test_g3_b4_3a_engine_staging.py` | 3 |
| `tests/unit/test_b032_offline_pdf_lab.py` | 3 |
| `tests/integration/test_g3_b2_sqlite_plan_contract.py` | 3 |
| `tests/integration/test_g3_b1_policy_guardrails.py` | 3 |
| `tests/integration/test_baseline_physical_integrity.py` | 3 |
| `tests/integration/test_b022_image_staging.py` | 3 |
| `tests/integration/test_recovery_flow.py` | 2 |

El archivo `tests/integration/test_pdf_inbox_submission.py` contiene numerosos usos de `tmp_path` (incluido `write_bytes`), por lo que **nueve señales no equivalen a nueve riesgos de seguridad**. En cambio, `test_recovery_flow.py` conserva la ruta fija de la base SQLite; el número dos no la vuelve segura. El resto de los archivos debe clasificarse por **momento de invocación** (import/collection vs fixture/test body), alcance de ruta y capacidad de salir del clon.

**Estado local aportado por owner:**
- `D tests/integration/test_benchmark_orchestration_integration.py`
- `D translated_c17cb80d10105b3497b142d04fa19078c4573ae0bade70cabc87dba80314aa19.pdf`

Son **dos eliminaciones locales de archivos versionados**; no se debe hacer checkout para restaurarlas, `git clean`, `git reset --hard` ni un commit que las incorpore sin decisión del owner. El clon del commit puede contener archivos que faltan en el working tree local. El resultado de `git status --short` aportado tras la preparación no revela nuevas modificaciones.

**Bloqueo actual A05-P4:** ya reconciliadas las 390 señales e identificada la causa de los 12 errores de escáner; falta repetir el análisis v2 y revisar import-time code, decoradores, plugins, rutas absolutas y subprocess. **No ejecutar `--collect` todavía**.

## 4.3 Triage reconciliado y corrección del scanner (2026-11-15)

**Datos del owner confirmados:** `static_signals.json` contenía **390 registros**, y el agrupamiento completo sumó **390**. Los **101** ausentes del primer listado eran de tipo `connect`; no hay descuadre real. El scanner original agrupaba por nombre de método y no distinguía `sqlite3.connect(...)`, otras conexiones o métodos homónimos. **No atribuir egress de red a esas 101 señales**.

**Causa de los 12 `syntax_error` verificada con fuentes GitHub:** los doce archivos reportados comienzan con **BOM UTF-8 U+FEFF** (incluido `tests/unit/test_idempotency_replacement.py`, cuya salida PowerShell no mostraba el detalle por formato). Es un defecto del escáner previo (`read_text(encoding="utf-8")` + `ast.parse(text)`), **no evidencia de sintaxis inválida de pytest**. **No se editaron los tests**.

Se actualizó [`collect_a01_isolated.py`](collect_a01_isolated.py) para:

1. Leer los archivos **únicamente en memoria** con `utf-8-sig`, conservando intactos los bytes de origen y el árbol de Git.
2. Conservar `signal` y `file/line`, agregando `callee` (expresión llamada, p. ej. `sqlite3.connect`), `scope` y `phase_hint` (`function_body` o `definition_time`).
3. Incluir errores AST remanentes y número de llamadas en contextos de definición en el manifiesto.

**Advertencia:** `phase_hint` es un *indicio estático*, no un análisis de efectos transitivos. Código dentro de funciones puede ejecutarse durante imports si es llamado desde nivel módulo; decoradores, imports de dependencias, metaclases y plugins pueden ejecutar código no evidente para este scanner. La nueva clasificación **no acredita seguridad de colección por sí sola**.

**Estado Git local del owner después de restaurar el test de benchmark:** únicamente se reporta `D translated_c17cb80d10105b3497b142d04fa19078c4573ae0bade70cabc87dba80314aa19.pdf`. Esa eliminación sigue **deliberada y sin staged/commit**, y no se debe restaurar, eliminar de Git ni mezclar con la campaña. El test `test_benchmark_orchestration_integration.py` ya no figura eliminado.

**Evidencia dinámica del scanner v2:** **pendiente de repetir** en la PC del owner con modo `prepare-only` después de `git pull --ff-only`. La conclusión sobre ausencia de errores BOM se refiere al **cambio del código de lectura y a la inspección de archivos**, no a una corrida nueva que todavía no ocurrió. A05-P4/P5/P6 y A-01 permanecen abiertos. **No ejecutar `--collect` todavía.**

## 5. Gates y seguimiento

- [x] **A05-P1:** riesgos IO-01…IO-06 vinculados al código de A-00 y restricciones de seguridad documentadas.
- [x] **A05-P2:** script prepare-only y collect opt-in creado, con chequeo SHA, clon sin remoto, entorno depurado, logs externos y sin limpieza automática.
- [x] **A05-P3:** prueba funcional en un repositorio **sintético** del programa de recopilación, con resultados de markers/parametrize.
- [ ] **A05-P4:** preflight del conjunto real de imports/decoradores/plugins y rutas absolutas, preferiblemente en host con aislamiento OS.
- [ ] **A05-P5:** colección real aislada de `translator_pdf` y conciliación `nodeid/markers/parametrizaciones` contra A-01.
- [ ] **A05-P6:** demostrar integridad de working tree del owner y registrar divergencias/efectos indirectos de colección.
- [ ] **A-05 completo:** pendiente revisión de seguridad de **todos** los tests pertinentes, no sólo un prototipo.
- [ ] **A-01 completo:** pendiente selección real CI, SUT por caso y conciliación dinámica.

**Decisión de ingeniería:** **habilitamos preparación**, no damos automáticamente autorización para la colección de código potencialmente peligroso. A-01 permanece abierto, A-05 también; `main`, CI y runtime no deben cambiar por esta preparación.
