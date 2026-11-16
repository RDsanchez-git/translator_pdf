# A-05 — Evidencia postcolección del clon retenido y selección de tests históricos

> **Estado:** **A05-SAFE-P3 cerrado** (inventario posterior y clasificación de selección); **A05-P6 PARCIAL**, **A05-P4 y A-05 global ABIERTOS**. El owner ejecutó una herramienta **de solo lectura**, sin ejecutar pytest ni tests, sobre el clon previamente recolectado. No hay baseline completo previo ni sandbox OS acreditado.
>
> **Fecha:** 2026-11-15. **Reporte primario:** JSON compartido por el owner de [`inspect_a05_isolated_artifacts.py`](inspect_a05_isolated_artifacts.py). **SHA del clon** `86cd68672ee692f073b62869e7c9bd177e8d9e3b`; `scope=RETAINED_CLONE_POSTCOLLECT_READ_ONLY_NOT_BEFORE_AFTER`. **Trabajo local actualizado por fast-forward:** hasta `fb3243753f174221089e4bf644d6efe9ec683d4b`; la inspección lee el clon congelado, no el working tree habitual. Fuentes para causas y alcance: [auditoría A-03/A-05 de tests históricos](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md) y [preflight A-05](A05_PREFLIGHT_A01_COLECCION_AISLADA.md).

## 1. Inventario posterior: resultado observado

| Comprobación concreta | Resultado informado | Interpretación estricta |
|---|---:|---|
| Cambios versionados bajo `tests/` e `infra/db/` | **0** | `tracked_changes_within_tests_or_infra_db=[]`; no implica filesystem completo limpio |
| Archivos no rastreados bajo esas rutas | **0** | `untracked_count=0` |
| Archivos ignorados bajo esas rutas | **0** | `ignored_count=0` |
| Artefactos relevantes `e2e_cache_real.db`, `-wal`, `-shm` | **ausentes** | No permanecen esos archivos en el clon inspeccionado |
| `infra/db/test_fsm.db`, `-wal`, `-shm` | **ausentes** | No evidencia que una ejecución los creara/borrara |
| `infra/db/documents.db`, `-wal`, `-shm` | **ausentes** | No evidencia de ejecución de `setUp` ni prueba completa de no-I/O |
| `tests/golden/sample_3_pages.fingerprint.json` | **ausente** | Referencia golden requerida no estaba presente; no convertirlo en PASS/SKIP de ejecución |
| `tests/golden/sample_3_pages.semantics.json` | **ausente** | La certificación semántica histórica no está habilitada por la presencia de expected |
| `tests/fixtures/sample_3_pages.pdf` | **presente** (2.045.076 bytes) | Referencia técnica versionada; no se abrió su contenido |
| `tests/fixtures/sample_3_pages.pdf.ast.json` | **presente** (29.954 bytes) | Caché versionada; el tamaño es el del filesystem Windows post-checkout |
| `tests/fixtures/sample_chunks.json` | **presente** (22.792 bytes) | Snapshot versionado; no se regeneró ni comparó su contenido en esta inspección |
| `tests/stress_report.json` | **presente** (2.705 bytes) | Aparece como `TRACKED_OR_OTHER_PRESENT`; **no** significa que se haya ejecutado el script de estrés |

**No presentar diferencias de tamaño de checkout (por ejemplo, conversiones de fin de línea) como corrupción o modificación del archivo:** Git no detectó cambios versionados en estas rutas. El inspector no abrió contenido y la diferencia byte-a-byte con blobs Git no fue el objeto de esta corrida.

**Límites de seguridad:** no hay snapshot *pre*-colección de archivos no rastreados/ignorados ni observación de egress, procesos secundarios, ficheros fuera de `tests/` e `infra/db/` o estado del host. Una ausencia postfacto tampoco prueba que un archivo no haya sido creado y eliminado durante imports. **A05-P6 no puede cerrarse en su totalidad**.

## 2. Selección efectiva `not e2e` en la colección

Los datos de `all.json` y `technical.json` del clon muestran:

| Archivo histórico | Nodeids `all` | Seleccionados `not e2e` | Marcados `e2e` |
|---|---:|---:|---:|
| `tests/integration/test_real_e2e.py` | 1 | **1** | 0 |
| `tests/integration/test_e2e_walking_skeleton.py` | 1 | **1** | 0 |
| `tests/integration/test_pipeline_orchestration.py` | 1 | **1** | 0 |
| `tests/integration/test_real_parser_pipeline.py` | 1 | **1** | 0 |
| `tests/integration/test_recovery_flow.py` | 1 | **1** | 0 |
| `tests/integration/test_healing_e2e_telemetry.py` | 5 | **5** | 0 |
| `tests/integration/test_translation_semantics.py` | 1 | **1** | 0 |
| **Total** | **11** | **11** | **0** |

**Consecuencia P0 para selección de ejecución:** `python -m pytest -m "not e2e"` **seleccionaría** el test `test_recovery_flow.py`, cuyo `setUpClass` y `tearDownClass` llaman a `os.remove(BASE_DIR/infra/db/test_fsm.db)` y cuyo cuerpo cambia directamente `compute_ast_hash` sin restaurarlo. Que un fichero se llame E2E **no impide** seleccionarlo por este filtro. También se seleccionan el walking skeleton y el test `real_e2e` de aserciones autocreadas.

**Importante:** selección de colección **no** implica ejecución, PASS ni que todos los jobs del CI ejecuten ese mismo selector bajo idénticas condiciones. La [auditoría de origen](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md) determina por lectura por qué los tests son problemáticos.

## 3. Decisión técnica inmediata: qué se puede y no se puede aprobar

- **A05-SAFE-P3 [x]:** postinventario del clon congelado con conteos 0/0/0, probes de rutas y siete archivos históricos reconciliados con `not e2e`.
- **A05-P6 [ ] — PARCIAL:** la inspección posterior de `tests/` e `infra/db/` terminó sin artefactos no versionados o ignorados remanentes. **Falta** snapshot anterior comparable y revisar efectos temporales/extrarrepo, subprocesos/red y host.
- **A05-P4 [ ]:** siguen pendientes efectos transitivos de imports/decoradores y plugins, y sandbox OS. El clon y el guard Python best effort **no sustituyen aislamiento**.
- **Bloqueo P0 a A-06 general:** **no correr `pytest -m "not e2e"` en el repositorio habitual** mientras el test destructivo de recuperación permanezca seleccionado. Tampoco ejecutar tests E2E históricos con SQLite bajo rutas fijas.
- **Ruta de remediación B-05:** reemplazar eliminación de DB fija por `tmp_path` o recursos de sandbox protegidos y restaurar el símbolo global con `patch/monkeypatch`. Conservar los oráculos de FSM/watchdog/resumer reales; no transformar la prueba en un mock tautológico.
- **B-03:** reclasificar nombres/markers según SUT, sin ocultar tests peligrosos mediante una simple marca `e2e`. **El marker NO es una medida de aislamiento.** No usar exclusión de CI como sustituto de corregir side effects.

## 4. Lo que esta evidencia NO demuestra

Esta inspección **NO** acredita haber ejecutado tests, ausencia absoluta de I/O, ausencia de exfiltración o salida a internet, aislamiento de sistema operativo, inmutabilidad de snapshots científicos, calidad de PDF, ni compatibilidad de todo el CI. Tampoco autoriza restaurar el PDF deliberadamente eliminado en el working tree del owner.

**Siguiente gate:** decidir la estrategia de aislamiento OS/fixtures para el conjunto focal antes de A-06, y auditar imports/plugins P4 con evidencia reproducible sin ejecutar tests peligrosos en el repo habitual. A-01, A-03 y A-05 conservan sus casillas abiertas.
