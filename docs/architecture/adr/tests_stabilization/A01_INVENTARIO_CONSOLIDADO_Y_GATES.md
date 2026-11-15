# A-01 — Índice consolidado del inventario de declaraciones de tests

> **Programa:** TST-STAB. **Estado: A-01 EN CURSO — censo estático completo y colección real efectuada; conciliación JSON, CI focal y clasificación SUT pendientes.**
> **Fecha:** 2026-11-15. **Ref de lectura de código:** `tests_stabilization` @ `d638c35af2311fb05679aadee375ac2ac0450561` (mismos archivos de tests que `main` @ `83ef0257f795f0d973f9393cc225e7af5b956ade`).
> **Método:** leer individualmente las fuentes de **177 módulos** en GitHub; detectar declaraciones `def test_*` por expresión de texto, registrar archivo/línea, indicador cercano de decoradores, importaciones productivas y palabras clave de fakes, skip, I/O/SQLite/red. **No ejecuta ni importa código.**

## 1. Resultado, exactamente qué se contó

| Grupo | Módulos `test_*.py` leídos | Declaraciones de funciones `def test_*` detectadas |
|---|---:|---:|
| Unitarios | 102 | 946 |
| Integración | 67 | 376 |
| Smoke | 1 | 13 |
| Raíz de `tests/` | 7 | 6 |
| **TOTAL** | **177** | **1341** |

**Interpretación obligatoria:** las **1341 declaraciones estáticas NO son 1341 pruebas efectivamente ejecutadas o recolectadas**. La cifra incluye funciones anidadas si coinciden con el patrón y omite la expansión de `@pytest.mark.parametrize`, marcadores heredados y generación por plugins. Puede haber funciones definidas pero no recolectadas. Los casos `unittest.TestCase` se reconocerán correctamente sólo al verificar el árbol de nodos de pytest. Los títulos “unit”/“integration” son carpetas, no prueba de marcación ni de alcance real.

La clave reproducible **archivo + línea + nombre** permite hallar cada declaración en el SHA pinneado. La etiqueta de marker “?” significa **desconocido**. Un “posible” skip/xfail o parametrización es una pista léxica, no una conclusión. Los imports del módulo son **candidatos de SUT**, no evidencia de que la prueba ejecute esas funciones. Ninguna de estas tablas otorga la categoría `CONFIABLE_PARA_SU_ALCANCE`.

## 2. Dossiers de fuentes (16 entregables)

| Registro de declaraciones | Módulos cubiertos | Funciones declaradas |
|---|---:|---:|
| [`A01_UNIT_001_012.md`](A01_UNIT_001_012.md) | 12 | 92 |
| [`A01_UNIT_013_024.md`](A01_UNIT_013_024.md) | 12 | 88 |
| [`A01_UNIT_025_036.md`](A01_UNIT_025_036.md) | 12 | 173 |
| [`A01_UNIT_037_048.md`](A01_UNIT_037_048.md) | 12 | 120 |
| [`A01_UNIT_049_060.md`](A01_UNIT_049_060.md) | 12 | 118 |
| [`A01_UNIT_061_072.md`](A01_UNIT_061_072.md) | 12 | 62 |
| [`A01_UNIT_073_084.md`](A01_UNIT_073_084.md) | 12 | 129 |
| [`A01_UNIT_085_096.md`](A01_UNIT_085_096.md) | 12 | 75 |
| [`A01_UNIT_097_102.md`](A01_UNIT_097_102.md) | 6 | 89 |
| [`A01_INTEGRATION_001_012.md`](A01_INTEGRATION_001_012.md) | 12 | 48 |
| [`A01_INTEGRATION_013_024.md`](A01_INTEGRATION_013_024.md) | 12 | 61 |
| [`A01_INTEGRATION_025_036.md`](A01_INTEGRATION_025_036.md) | 12 | 138 |
| [`A01_INTEGRATION_037_048.md`](A01_INTEGRATION_037_048.md) | 12 | 64 |
| [`A01_INTEGRATION_049_060.md`](A01_INTEGRATION_049_060.md) | 12 | 29 |
| [`A01_INTEGRATION_061_067.md`](A01_INTEGRATION_061_067.md) | 7 | 36 |
| [`A01_CENSO_ROOT_SMOKE.md`](A01_CENSO_ROOT_SMOKE.md) | 8 | 19 |
| **TOTAL** | **177** | **1341** |

Cada dossier contiene tabla por **módulo** y por **declaración**, más las señales textuales de mocks, `tmp_path`, SQLite, scripts y librerías externas. Son inventarios técnicos; su tamaño no se interpreta como cobertura.

## 2.1 Colección real obtenida después del censo inicial

**Evidencia aportada por el owner en `tests_stabilization` @ `86cd68672ee692f073b62869e7c9bd177e8d9e3b`**: `pytest --collect-only` en clon separado dio exit **0** para cuatro modos: **1.474 all**, **225 unit**, **70 integration and not regression**, **1.454 not e2e**. Cuerpos de tests ejecutados: **cero**. Véase [A01_COLECCION_PYTEST_2026-11-15.md](A01_COLECCION_PYTEST_2026-11-15.md) para los JSON locales, las comprobaciones por marker y las tareas de conciliación.

La diferencia entre **1.341 declaraciones estáticas** y **1.474 nodos reales** es **+133 netos**, no necesariamente 133 parametrizaciones: todavía no se inspeccionaron los nodeids ni los registros `parameter_id`. Los markers efectivos y la selección por rutas focales del workflow ya fueron verificados en §3.3 del [informe de colección](A01_COLECCION_PYTEST_2026-11-15.md); la explicación de +133 está documentada en [A01-S6](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md). El inventario de declaraciones del §2 es evidencia anterior y se conserva sin reetiquetarlo como cobertura.

## 3. Selección CI que se puede afirmar sin ejecutar pytest

Fuentes: [`pyproject.toml`](../../../../pyproject.toml), [`.github/workflows/ci.yml`](../../../../.github/workflows/ci.yml) en SHA `83ef0257` y [A-00](A00_BASELINE_INVENTARIO_Y_RIESGOS.md).

1. El `addopts` por defecto aplica `-m "not e2e"`. **Sólo** excluye marcas `e2e` efectivas, no archivos que tengan `e2e` en el nombre.
2. El job unitario usa `python -m pytest -m "unit" ...`. El job de integración usa `-m "integration and not regression"`, más **cinco pasos focales** por rutas explícitas y una suite global `-m "not e2e"`.
3. En consecuencia, una función en un archivo `tests/unit/` sin marker no queda seleccionada automáticamente por `-m unit` (podría entrar en el paso global). Una función en `tests/integration/` sin marker también puede entrar en el paso global.
4. La selección **real** incluye decoradores de clases, `pytestmark`, parametrize, `skipif`, collection hooks y plugins. **No está calculada aquí**. Un `SKIP` no cumple un contrato obligatorio; una coincidencia por `-m` tampoco demuestra ejecución del SUT.
5. El workflow técnico GitHub **no usa el `pyright-local.json` del owner**: su `pyrightconfig.json` sigue excluyendo `tests/`. Los 0 errores previos de Pyright local son tipado, no hallazgos semánticos de A-01.

### 3.1 Distinción entre evidencia directa e hipótesis

| Capa de evidencia | Estado ahora | Qué no permite afirmar |
|---|---|---|
| Módulos y `def test_*` de Git tree | **CENSADO** (177/177, declaración por línea) | Casos recolectados, éxito/fracaso |
| Marker/decorador cercano | **INDICIO ESTÁTICO** | Marker efectivo de clase/módulo y CI real por caso |
| Imports de `core/apps/runtime/infra` | **INDICIO ESTÁTICO** | Que se invoque el SUT productivo |
| Fakes, DB, filesystem, librerías externas | **INDICIO ESTÁTICO** | Que una llamada se ejecute o exista egress |
| Casos parametrizados expandidos, `pytest --collect-only` | **NO VERIFICADO** | Conteo dinámico, ids/marks exactos |
| `SKIP/XFAIL` efectivos | **NO VERIFICADO** | Cobertura válida, obligatoriedad |
| Contrato → SUT → oráculo por caso | **NO VERIFICADO** | Que el test sea robusto, independiente o inmune a refactor |
| Fixture autouse/efecto indirecto | **NO VERIFICADO** | Seguridad al correr suites en working tree del owner |

## 4. Casos y riesgos ya demostrados que deben influir en A-01

Los siguientes **hallazgos de código** no provienen de contar palabras clave: se inspeccionaron fuentes y rutas de efectos en [A-00](A00_BASELINE_INVENTARIO_Y_RIESGOS.md), en especial IO-01…IO-10.

| ID | Fuente | Observación real en el código | Decisión provisional |
|---|---|---|---|
| TS-001 | `tests/integration/test_golden_parser.py` | `patch.object(adapter, 'parse')` sustituye el parser y `expected_fingerprint = current_fingerprint` autoaprueba la aserción; la falta de GT conduce a skip y puede escribir un PDF ficticio | **FALSA GARANTÍA CONFIRMADA**; no correr en árbol owner antes de A-05 |
| TS-002 | `tests/integration/test_chunker_snapshot.py` | Si no existe la fixture obligatoria, genera y escribe su propio snapshot y termina sin validarlo. No implica que esa rama se tome hoy con snapshot presente | **FALSA GARANTÍA CONDICIONAL CONFIRMADA**, B-02 posterior |
| TS-003 | `tests/integration/test_real_e2e.py` | `pipeline.execute` se sustituye por un valor simulado; no demuestra ejecución de todo el pipeline | **ALCANCE SOBREDECLARADO**, conserva posible valor del consumidor |
| IO-05 | `tests/integration/test_e2e_walking_skeleton.py` | DB fija `tests/fixtures/e2e_cache_real.db`, con borrado en cleanup; AST fixture se autogenera si falta | **AISLAMIENTO OBLIGATORIO** |
| IO-06 | `tests/integration/test_recovery_flow.py` | Borra `infra/db/test_fsm.db` antes/después y usa la misma ruta fija | **RIESGO DE DESTRUCCIÓN**, veto a ejecución en working tree |
| TS-006 | `tests/integration/test_verification_pipeline_connection.py` | Extrae PDFs técnicos sintéticos reales y verifica rechazo vectorial | **CANDIDATO DE BUEN TEST**, sensibilidad/contrato aún por auditar |

No ejecutar `pytest` amplio, `--collect-only` ni scripts de estrés en la copia principal por comodidad. Algunas operaciones de import/collection pueden causar efectos aun sin ejecutar un test. No tocar el PDF borrado deliberadamente, ni aplicar `git clean` / `git reset --hard`.

## 5. Bloqueos de A-01 y plan para completarlo rigurosamente

**La colección y selección real ya están conciliadas** (véase §2.1 y [reporte detallado](A01_COLECCION_PYTEST_2026-11-15.md)). **A-01 sigue abierto**: los cuatro módulos sin nodos y las 24 divergencias fuente/colección están **explicados** (véase [A01-S6](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md)); faltan las fichas por SUT/contrato pertinentes (A01-S5) y el gate de seguridad A-05. No declarar confianza en tests por su mera colección. No declarar confianza en tests a partir de que pytest los recolecta.

Secuencia pendiente (sin incluir ciencia ni nuevo E2E global):

- [x] **A01-S1** — Censo fuente a archivo/línea de las 177 unidades (este dossier y 16 anexos).
- [x] **A01-S2** — Mapa estático de selección CI, marcas y riesgos, con incertidumbre explícita.
- [ ] **A01-S3** — [Preflight A-05](A05_PREFLIGHT_A01_COLECCION_AISLADA.md) **parcialmente preparado**, con herramienta de clon independiente en modo prepare-only y prueba del recolector con repositorio sintético. **Pendiente** comprobar seguridad real de imports/decoradores/plugins, rutas absolutas y aislamiento OS antes de colección. A-05 y A-01 permanecen abiertos.
- [x] **A01-S4 — Colección y selectores reconciliados.** `pytest --collect-only` en clon a SHA `86cd6867`: 1.474 nodos únicos, 187 con ID de parametrización, 1.159 sin marcador de nivel, cuatro diferencias bidireccionales de selección = 0; 12/12 rutas focales de CI con nodos y 0 señales auditadas de error/warning en logs. [Informe actualizado](A01_COLECCION_PYTEST_2026-11-15.md). **Este check acredita colección, NO ejecución de tests**, ni reemplaza A01-S5/S6.
- [ ] **A01-S5** — Trazar cada caso crítico al **SUT real** por análisis dirigido y fichas `TR-###` (A-02/A-04), anotar fakes legítimos y efectos/fixture; los casos legacy se reclasifican en lugar de atribuir cobertura PDF→PDF.
- [x] **A01-S6 — Conciliación estática/dinámica cerrada.** 177 módulos (173 con nodos; 3 placeholders y 1 script manual sin nodos), 1.341 funciones fuente, 1.474 nodeids y **133 expansiones parametrizadas**, sin funciones no recolectadas ni nodeids huérfanos. Las **24/24 diferencias** están justificadas; 23 decoradores literales y uno definido por la lista `CERTIFICATION_MODULES` de 4 rutas. [Evidencia completa](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md). **No acredita PASS ni confianza semántica.**

**Regla de seguridad:** no proporcionar una orden de borrado o limpiar la copia del owner. La selección `--collect-only` nunca se ejecuta allí si persisten los riesgos IO-01…IO-06; el aislamiento debe revisarse y documentarse primero.

## 6. Criterio de avance

La documentación de esta fecha completa el **inventario de declaraciones estáticas**, no la auditoría semántica ni A-01 en su totalidad. Pueden comenzar A-02/A-03 **en paralelo sólo mediante lectura de código** mientras se prepara A-05. Ningún ajuste al runtime, corpus, GT científico, reglas de CI, ground truth o compilación se autoriza desde este dossier.

**Siguiente acción segura:** examinar los JSON y logs de la colección **ya realizada** en la copia aislada, contrastar markers, parametrizaciones y paths de CI, y verificar `git status` post-colección; **no ejecutar cuerpos de tests** hasta cerrar el análisis de riesgos A-05.
