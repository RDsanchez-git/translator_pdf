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
