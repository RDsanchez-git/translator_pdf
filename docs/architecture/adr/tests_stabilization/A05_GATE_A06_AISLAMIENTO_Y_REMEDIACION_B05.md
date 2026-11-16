# A-05 → A-06 — Gate de ejecución aislada y remediación mínima B-05

> **Estado:** DISEÑO DE GATE DOCUMENTADO, **NO HABILITA EJECUCIÓN**. No se ha instalado/verificado una VM/contenedor de seguridad para los cuerpos de tests ni remediado B-05. **A05-P4, A05-P6, A-05 global, A-06 y B-05 siguen [ ].** No se ha ejecutado un test nuevo ni mutaciones.
>
> **Fecha:** 2026-11-15. **Rama:** \`tests_stabilization\`; sujeto de tests en SHA de colección \`86cd68672ee692f073b62869e7c9bd177e8d9e3b\`. [Registro estático de riesgos](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md), [evidencia de 11 casos históricos incluidos en \`not e2e\`](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md), [A-05 actual](A05_PREFLIGHT_A01_COLECCION_AISLADA.md), [plan maestro](PLAN_REMEDIACION_TESTS_PIPELINE.md). Contrastar los cambios de tests futuros contra **el SHA real antes del primer test**.
>
> **Decisión:** no ejecutar \`pytest -m "not e2e"\` en el checkout original del owner. Un clon Git independiente, un \`TMP\` nuevo y un guard de sockets Python **no son sandbox de seguridad**. La limpieza observada post-\`--collect-only\` (0 cambios/versionados, 0 ignored, 0 untracked en dos subárboles) **no autoriza** una ejecución de cuerpos.

## 1. Peligros que condicionan el gate

| ID | Hecho verificado directamente en fuente/colección | Riesgo | Alcance correcto |
|---|---|---|---|
| **P0-DB-DELETE** | [\`test_recovery_flow.py\`](../../../../tests/integration/test_recovery_flow.py) líneas 23–32 y 135–142: \`setUpClass/tearDownClass\` eliminan \`BASE_DIR / "infra/db/test_fsm.db"\` con \`os.remove\` | Destrucción de archivo existente y pérdida silenciosa de estado; \`SQLITE_STATE_DIR\` **no protege** contra \`os.remove\` literal | Cuerpo/fixture de test; no se ejecuta en \`collect-only\` |
| **P0-GLOBAL-PATCH** | Mismo archivo, líneas 94–95: \`core.pipeline.orchestrator.compute_ast_hash = lambda nodes: ast_hash\` sin restauración | Mutación global persiste hasta fin del intérprete pytest; contaminación por orden | Cuerpo de test; ninguna prueba de restauración |
| **P0-SELECTOR** | \`.github/workflows/ci.yml\` líneas 130–135 incluye \`pytest -m "not e2e"\`; [colección real](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md) incluye el caso de recuperación y otros 10 nodos de seis archivos históricos, todos sin marker \`e2e\` | El selector no excluye por nombre; \`not e2e\` **sí** puede ejecutar los tests peligrosos | Reproducido por colección; **no** es resultado PASS/FAIL |
| **P1-FIXED-CACHE** | [\`test_e2e_walking_skeleton.py\`](../../../../tests/integration/test_e2e_walking_skeleton.py) líneas 37–44, 67, 93–100 usa \`tests/fixtures/e2e_cache_real.db\` y borra DB/WAL/SHM | Colisiones entre ejecutores, borrado de referencias locales y contaminaciones | Cuerpo/setUp/tearDown; caché histórica, no W08/G3 soportado |
| **P1-DOC-DB** | [\`test_real_e2e.py\`](../../../../tests/integration/test_real_e2e.py) línea 108 y [\`test_pipeline_orchestration.py\`](../../../../tests/integration/test_pipeline_orchestration.py) línea 101 abren \`get_connection("infra/db/documents.db")\` en \`setUp\` | I/O SQLite persistente aunque el cuerpo haga mocks; con \`journal_mode=WAL\` | Estado dependiente del checkout; no biblioteca de solo lectura |
| **P1-FALSE-E2E** | \`test_real_e2e.py\` parchea \`execute\` y rellena \`COMPLETED\`; walking skeleton reescribe \`cache_hit\` y crea resumen de costes | Falsas garantías si se presenta \`PASS\` como pipeline/traducción/caché reales | Oráculos a corregir **sin** fabricar nueva ruta PDF→PDF |

**No inferir** que estos efectos hayan ocurrido durante colección: el inspector del clon encontró 0 ignorados/no rastreados y no hay baseline previo para efectos temporales. **No cerrar P4/P6** por este documento.

## 2. Estrategia de ejecución recomendada: aislamiento REAL del sistema operativo

La opción de menor riesgo para la baseline histórica es una **VM descartable** (o contenedor con aislamiento del host verificado) cuya única copia del proyecto sea un checkout/clon independiente. **No se acepta como gate un clon en \`%TEMP%\` del host** para ejecutar los cuerpos.

### Preparación fuera de la máquina de trabajo

1. **Provisionar VM descartable**, sin carpetas compartidas, unidades del host, credenciales, SSH agent, tokens de GitHub/LLM o perfil personal montados. No copiar la carpeta \`venv\` del host. El volumen de trabajo de pytest y SQLite queda en el disco virtual de la VM.
2. **Egress de red deshabilitado por hipervisor/firewall del entorno virtual**, no solamente por monkeypatch de Python. Si hay que instalar dependencias, abastecer la VM antes y cortar la red **antes** de importar tests; registrar cómo se verificó el bloqueo. No introducir credenciales de proveedores en la VM.
3. **Copiar o clonar un commit fijado** del repo dentro de la VM, después eliminar acceso a remoto/red para fase de ejecución. Los tests siguen siendo los del SHA auditado o un SHA posterior cuyo diff de \`tests/\` esté documentado. No usar el working tree del owner como shared folder.
4. Ejecutar **usuario sin privilegios** dentro de VM. \`HOME\`, \`TMP/TEMP\`, \`APP_ROOT\`, \`SQLITE_STATE_DIR\` y rutas de caché deben apuntar a directorios **dentro del volumen virtual**. \`--basetemp\` y \`-p no:cacheprovider\` ayudan a acotar artefactos pytest, **no redirigen** un \`os.remove(BASE_DIR/...)\` ni reemplazan el sandbox OS.
5. Registrar **antes** de la ejecución: SHA, versión Python/pytest/plugins, \`pytest --version\`, dependencias, variables relevantes **sin valores secretos**, inventario de paths incluidos ignorados/untracked, y presencia/tamaño/hash de fixtures de prueba. Inventariar también SQLite y posibles sidecars bajo rutas de riesgo. Un baseline pre/post habilita atribución aproximada; para operaciones creadas-borradas se requiere **observación adicional del SO**, no comparación posterior solamente.
6. **Desactivar plugins de pytest no necesarios solo cuando se pueda demostrar equivalencia de selección**. \`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1\` cambia el entorno respecto de CI y puede alterar fixtures/decoradores; registrar y comparar el conjunto de plugins antes de interpretar PASS/FAIL.
7. **Ejecutar tests SOLO dentro de la VM**, primero un conjunto mínimo de contratos puros, luego fixtures SQLite de rutas temporales, y por último históricos **solo tras remediación B-05 o aislamiento realmente demostrado**. El CI hospedado (\`ubuntu-latest\`) es un entorno externo del dueño, pero su egress/plugins/fiabilidad semántica tampoco se acreditan por ser CI.
8. Registrar **después**: códigos de salida, PASS/FAIL/SKIP/XFAIL por nodeid, stdout/stderr, selección real, diff de tracked/untracked/ignored, diferencias de DB/sidecars y evidencia de red/recursos. Ningún SKIP de referencia obligatoria ni error de infraestructura cuenta como PASS del contrato.
9. **Descartar la VM** al terminar. Exportar solo informes textuales y evidencias saneadas, nunca datos del owner. No hay paso de limpieza ni restauración en el checkout original; la eliminación deliberada del PDF local queda intacta.

**Si falta un control esencial (volumen exclusivo, sin secretos ni carpetas compartidas, red negada por SO, baseline de efectos), el gate es \`BLOCKED\`**. En ese caso seguir con auditoría estática y diseño de B-05, no ejecutar tests para forzar progreso.

## 3. Contratos de remediación mínima B-05 (NO IMPLEMENTADA)

### B05-R1 — Recuperación: no borrar DB fija, no mutar símbolos globales

**Fuente:** \`TestRecoveryAndResumeEndToEnd(unittest.TestCase)\` de \`test_recovery_flow.py\`.

**Diseño compatible con unittest:** usar \`tempfile.TemporaryDirectory()\` creado en \`setUpClass\` y registrar \`addClassCleanup(tmp.cleanup)\` **al instante**; \`cls.test_db = Path(tmp.name) / "test_fsm.db"\`. Crear la DB a través de \`get_connection(cls.test_db)\`. Los repositorios \`AbandonedProcessWatchdog\` y \`OnDemandResumeManager\` reciben **esa misma ruta desechable**. Eliminar los \`os.remove\` condicionales de la ruta relativa al repo; cerrar conexiones antes del cleanup. Cualquier sidecar \`-wal/-shm\` permanece dentro de TemporaryDirectory.

**Patch global:** suprimir la asignación directa a \`core.pipeline.orchestrator.compute_ast_hash\` si ya no es necesaria (el test actualmente parchea \`pipeline.execute\`), o utilizar \`with patch("core.pipeline.orchestrator.compute_ast_hash", return_value=ast_hash)\` durante **solo** la operación que la requiera. Confirmar que la referencia original se restaura, incluso si hay excepción.

**Contrato que NO debe degradarse:** \`PROCESSING → STALLED → PROCESSING\` mediante watchdog y resumer **reales**, verificando FSM **reabierta** y versionada; no acreditar el \`COMPLETED\` final como evidencia de pipeline real cuando lo asigna un mock. Idealmente separar watchdog/resumer de la simulación de finalización.

**Falsadores B05-R1:** estado inicial ajeno no se rescata, lease/versión equivocado falla cerrado; tabla de fsm permanece reabrible; ningún fichero bajo \`infra/db/\` del checkout cambia; \`compute_ast_hash\` conserva la identidad de función original fuera del scope del patch.

### B05-R2 — Caché histórica: DB temporal y hit observado, nunca escrito por el test

Mover \`test_e2e_walking_skeleton.py\` a DB dentro del \`TemporaryDirectory\` de la instancia (por ejemplo, \`self.test_db_path\` dentro de \`asyncSetUp\`), registrada para cleanup al terminar; no crear caché ni AST faltante dentro de \`tests/fixtures/\`. Si la caché AST histórica es fixture obligatoria, falta = precondición fallida explícita, no escritura.

El \`CachedLLMProvider\` productivo ([\`apps/llm_workers/cache_provider.py\`](../../../../apps/llm_workers/cache_provider.py)) abre conexiones \`aiosqlite\` **por operación con \`async with\`**; verificar que todas finalicen antes de liberar TemporaryDirectory. En un contrato focal, medir **contador de invocaciones del proveedor falso**, \`cache_provider.metrics["cache_hits"]\`, estado de tabla y \`InferenceResult.finish_reason="cache_hit"\` **tal como lo devuelve el SUT**. No usar \`object.__setattr__\` sobre resultados congelados ni \`patch.object(SummaryBuilder, "build", return_value=mock_summary)\` para establecer el expected.

**Limitación:** esta caché por \`prompt_hash\` es **histórica**, no la barrera de identidad W08/G3 soportada. Corregirla no autoriza introducir \`CachedLLMProvider\` en la ruta nueva ni reabrir R1/R3. Si se clasifica como legacy, conservar su propósito y excluir claims sobre pipeline actual.

### B05-R3 — Setup SQLite y fixtures técnicas de otros tests

\`test_real_e2e.py\` y \`test_pipeline_orchestration.py\`: redirigir \`get_connection("infra/db/documents.db")\` a SQLite desechable con conexión cerrada al finalizar; si el repositorio no se ejerce por estar \`execute\` parcheado, suprimir la DB del setup solo después de demostrar que no era un SUT real del test. Reemplazar cualquier fabricación condicional de \`tests/fixtures/sample_3_pages.pdf\` por **precondición explícita** o por PDF válido generado en \`tmp_path\`/temporales. Renombrar reclamos de «E2E real» si el SUT no se ejecuta, sin descartar aserciones útiles de un consumidor.

**No confundir** estas correcciones de seguridad con B-01 golden parser, B-02 chunker snapshot ni certificación científica. Cambios en tests se preparan como PR/commits separados con diff y falsadores por frontera; **no se aplican durante este diseño**.

## 4. Secuencia recomendada de gate A → baseline A-06 → B/C

| Etapa | Acción | Entrada obligatoria | Salida exigida | Estado |
|---|---|---|---|---|
| **A05-Q1** | Validar entorno descartable sin host shares/secrets, egress negado por SO, intérprete y plugins registrados | VM/contenedor aprovisionado; evidencia humana/config verificable | \`OS_ISOLATION_VERIFIED\`, mecanismo documentado; sin conclusiones sobre tests | **[ ]** |
| **A05-Q2** | Inventario *pre*-ejecución del volumen virtual y paths sensibles | VM preparada y commit fijado | Lista tracked/untracked/ignored, DB/sidecars y hash de inputs técnicos | **[ ]** |
| **A05-Q3** | Determinar subconjunto seguro y selectores exactos por nodeid | [Colección 1.474/1.454 y hallazgos P0](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md) | Lista explícita, sin \`-m not e2e\` como «seguridad»; tests de escritura bloqueados | **[ ]** |
| **A06-Q1** | Primera baseline **focal**, p.ej. \`tests/integration/test_g3_b3_structured_result_contract.py\`, **dentro de VM** | A05-Q1/2/3 aprobados; plugins y dependencias congruentes | PASS/FAIL/SKIP/XFAIL, timings, nodeids, efectos pre/post; **no** certificación física | **[ ]** |
| **B05-R1/R2/R3** | Remediaciones separadas, testigo negativo y auditoría de cambio | Contratos anteriores, red/FS aislados, diff fuente | DB fija inexistente, patch restaurado, oráculos no autorreferentes, evidencia focal en VM | **[ ]** |
| **A06-Q2** | Ampliación por capas: estado durable G3/G5 y recuperación, solo cuando cada SUT sea seguro | B05 mínimo o VM con protección probada y scope aprobado; control de artefactos | Resultados por frontera y side effects comparados | **[ ]** |
| **C** | Mutaciones contractuales en árbol descartable, una por vez | Baseline válida por SUT y diseño de falsador | Test detecta mutación **por causa normativa**, no por infraestructura | **[ ]** |

**Orden importante:** el diseño no obliga a remediar todos los tests antes de medir ningún contrato puro; sí prohíbe correr el selector global peligroso en el original. Si se aprueba adelantar una corrección de seguridad B-05 antes de cerrar A global, registrarla **como excepción de seguridad revisable**, sin declarar pasado el resto de gates.

## 5. Veredicto de este documento y criterios de no-falsa-confianza

- [x] **A05-D1:** peligro de \`not e2e\` contrastado con \`.github/workflows/ci.yml\` y el JSON de colección; 11 testigos históricos incluidos.
- [x] **A05-D2:** mecanismo compatible con \`unittest.TestCase\` para DB temporal y restauración de \`compute_ast_hash\` definido; **no aplicado**.
- [x] **A05-D3:** contrato de caché medible con \`CachedLLMProvider\` real y fake medido en frontera; sin \`SummaryBuilder\` simulado como oráculo.
- [x] **A05-D4:** gate OS, pre/post observables y secuencia A-06/C definidos, sin ejecutar tests ni modificar CI.
- [ ] **A05-Q1/2/3:** no hay VM/config y baseline pre-ejecución demostradas en esta conversación.
- [ ] **B05-R1/R2/R3:** ninguna remediación implementada ni autorizada como parte de este gate documental.
- [ ] **A-05 y A-06:** ABIERTOS. **\`0\` cuerpos de tests ejecutados por este trabajo**.

**Regla de preservación:** no restaurar ni incluir en commits el PDF que figura \`D\` en el working tree del owner, no utilizar \`git clean\`/\`reset --hard\`, no regenerar golden/snapshots, no abrir GT científico ni hacer baseline científica.

## 6. Preparación verificable de A05-Q1/Q2/Q3 (sin habilitar A-06)

**Evidencia de implementación:** [`preflight_a06_guest.py`](preflight_a06_guest.py) está versionado en `tests_stabilization`. Es un preflight **de solo lectura** previsto para ejecutar **dentro de una VM Linux descartable**. No importa tests ni ejecuta pytest o probes de red; guarda `preflight.json` y `focal_nodeids.txt` en un directorio nuevo fuera del checkout. La existencia de este script **no equivale** a tener VM ni firewall verificados. Por tanto **A05-Q1/Q2/P4/P6 y A-06 siguen pendientes**.

**Lo que el preflight verifica dentro del guest:** Git `HEAD`, worktree limpio, ausencia de remotos Git, ejecución sin privilegios, tipo de filesystem visible en `/proc/self/mountinfo`, nombres (no valores) de posibles variables de credenciales, tamaño/hash de archivos de `tests/fixtures`, `tests/golden` e `infra/db`, y ausencia de symlinks en esas rutas inspeccionadas. Coteja `manifest.json` y `all.json` de la colección A-01 (1.474 nodeids) con el SHA de colección y el objeto Git del árbol `tests/`; no toma el orden de declaración como identidad. No recorre ni modifica `tests/corpus/canonical`.

**Condición exterior no verificable desde el guest:** la política de red negada por hipervisor/firewall, ausencia de bind mounts hacia host y de agentes/credenciales externos requiere **inspección del operador del host**. El script acepta un JSON `--host-evidence` con declaraciones explícitas y método de comprobación, pero las etiquetas `DECLARED_NOT_INDEPENDENTLY_VERIFIED` y `READY_FOR_INDEPENDENT_HOST_REVIEW` **no sustituyen** revisión humana. Una prueba de conectividad fallida dentro de Python tampoco certificaría el firewall del host. `BLOCKED` es el estado por defecto cuando faltan datos.

**Selección focal propuesta (A05-Q3, candidatos, NO ejecutados):**

- `tests/integration/test_g3_b3_structured_result_contract.py::test_two_nodes_one_chunk_response_order_is_identity_based_not_positional`
- `tests/integration/test_g3_b3_structured_result_contract.py::test_only_preserve_nodes_materialize_without_provider_results`
- `tests/integration/test_g3_b3_structured_result_contract.py::test_unknown_chunk_rejected_before_payload_parse`
- `tests/integration/test_g3_b3_structured_result_contract.py::test_translated_unicode_surrogates_rejected_before_projection`

Se eligieron por lectura de los cuerpos y ausencia de I/O físico declarado: ejercitan `ChunkPlan`, `parse_chunk_response` y/o `materialize_node_results`, sin provider, SQLite ni PDF. **No se ha probado su seguridad dinámica**, ni se acredita PASS. El script exige que estén en la lista congelada y que no tengan markers `e2e/skip/skipif/xfail`. Otros 29 casos del mismo archivo quedan para una ronda siguiente, no se excluyen definitivamente. No ejecutar `pytest -m "not e2e"` como sustituto.

**Invocación prevista dentro de la VM (solo después de aprovisionamiento y revisión del host):**

```bash
python docs/architecture/adr/tests_stabilization/preflight_a06_guest.py \
  --repo-root /guest/work/translator_pdf \
  --reports /guest/evidence/a01-frozen \
  --output /guest/evidence/a05-preflight-01 \
  --host-evidence /guest/evidence/host-isolation.json
```

Los `reports` son copias independientes de `manifest.json` y `all.json` originados en la colección del owner; deben mantenerse fuera del checkout para no alterar su estado. El script requiere que la revisión congelada esté disponible en el historial Git del guest y que el árbol `tests/` coincida exactamente. Es una **comprobación de preparación** y retorna código 2 si hay bloqueos, 3 si no puede preparar/leer evidencia; no se debe "arreglar" un bloqueo debilitando condiciones.

El JSON `host-isolation.json` debe contener **solo afirmaciones verificadas por el operador y su método**, por ejemplo:

```json
{
  "guest_private_disk_no_host_shares": true,
  "guest_checkout_without_host_bind_mounts": true,
  "no_host_secrets_or_agents_mounted": true,
  "network_egress_denied_by_host_or_hypervisor": true,
  "verification_method": "Describir configuración concreta de hipervisor, NIC/firewall y montajes revisados"
}
```

Los valores del ejemplo **no son evidencia real**. No crearlos como afirmación de un host que no se inspeccionó. `--output` se crea solo si todas las entradas básicas pueden ser leídas; puede almacenar resultado `BLOCKED` para análisis. Falta aún captura de `pytest --version`/plugins y del inventario integral tracked/untracked/ignored (el script registra Git limpio y paths técnicos de alto riesgo, **no** una certificación global de efectos). Se requieren OS-level tracing o equivalentes cuando se pretenda acreditar ausencia de escrituras temporales creadas y borradas.

**Estado de avance al añadir este script:** control preliminar reproducible **PREPARADO**; `A05-Q3` contiene cuatro candidatos definidos, pero **no cerrado** hasta reconciliación y revisión en el guest; `A05-Q1/Q2` **no cerrados**; `A06-Q1` **no ejecutado**; `B05` **sin cambios**. La creación y prueba sintética del script fuera del repositorio se registran por separado de un resultado en VM real.

## 7. Preparación del host Windows: comprobador no destructivo (no acredita Q1)

Se añadió [\`probe_a05_hyperv_host.ps1\`](probe_a05_hyperv_host.ps1), compatible con **Windows PowerShell 5.1**. Inspecciona exclusivamente el **host**: presencia de cmdlets de Hyper-V, VM por nombre, estado apagado, adaptadores conectados a switches, discos virtuales y servicio «Guest Service Interface». **No crea, arranca, desconecta, instala ni modifica nada**. Produce JSON en stdout, con \`host_isolation_verified=false\` y \`a06_authorized=false\` **incluso cuando no detecta un bloqueo**.

Comprobación sugerida desde un PowerShell abierto en el repo habitual, sin privilegios añadidos solo por este paso:

\`\`\`powershell
& .\docs\architecture\adr\tests_stabilization\probe_a05_hyperv_host.ps1 -VMName 'TST-STAB-LAB' -OwnerRepoRoot (Get-Location).Path
\`\`\`

**No presuponer que existe \`TST-STAB-LAB\` ni que el equipo soporta Hyper-V.** Si falta la VM, los cmdlets o permisos de inspección, el resultado es \`BLOCKED\` y código 2; **no intentar remediar el bloqueo creando VM ni cambiando funcionalidades de Windows sin decisión del owner**. Si existe una VM, el resultado \`PRECHECK_ONLY_HUMAN_REVIEW_REQUIRED\` exige inspeccionar después la configuración efectiva del host, las credenciales, sesiones mejoradas, rutas físicas, servicios compartidos, filtros de red y archivos del guest, antes de declarar \`A05-Q1\`.

La ausencia de \`SwitchName\` sugiere que un adaptador Hyper-V no está conectado a un switch: **no es una prueba de firewall**, ni acredita red cortada en otros dispositivos o entornos virtuales. El guest script no verifica dinámicamente la red. La evaluación exterior por el operador del host sigue siendo indispensable. No insertar automáticamente declaraciones \`true\` en \`host-isolation.json\` ni aprobar A-06 basándose solo en este sondeo.

**Evidencia pendiente:** no disponemos de acceso directo a las características de Windows ni a una VM del owner desde esta sesión. No se ha ejecutado el \`.ps1\` en Windows; tampoco \`preflight_a06_guest.py\` dentro de una VM real. La presencia de ambos archivos en GitHub es **preparación**, no validación del entorno ni tests PASS.

## 8. Decisión de ejecución sin Docker y B05-R1 implementada (evidencia estática)

**Decisión del owner:** Hyper-V deja de ser el camino de trabajo. **Docker no es requisito de la suite pytest/CI técnico**; no agregar dependencias de daemon, Compose, red o proveedores externos a pruebas que pueden verificar contratos con Python, SQLite temporal y fakes en el límite. Conservar el laboratorio Docker PDF→PDF existente solo como validación operacional **separada y explícita**, de acuerdo con el Atlas/handoff; no repetir C0–C4 durante esta campaña.

**Distinción obligatoria:** la hermeticidad en tests (directorios temporales, conexiones cerradas, no modificar estado global, fakes externos y no efectos sobre fixtures) es requisito de calidad; una VM/contendor OS no puede trasladarse como prerequisito universal para que un desarrollador o GitHub Actions ejecute pytest. Hasta remediar los demás tests históricos peligrosos, **no interpretar la suite completa como segura para el checkout del owner**. El preflight Hyper-V y guest Linux permanece como material histórico/no normativo; no es gate de ejecución obligatorio para tests que ya acrediten hermeticidad. Los cambios a la selección de CI, si son necesarios, se revisarán aparte.

**B05-R1 — código modificado, validación pendiente:** [\`test_recovery_flow.py\`](../../../../tests/integration/test_recovery_flow.py), commit \`06362b60d9d3aa140bda2f5a9fcc7a18c9bb652f\`, únicamente en \`tests_stabilization\`.

- Se reemplazó la ruta persistente \`infra/db/test_fsm.db\` y sus dos \`os.remove\` por \`tempfile.TemporaryDirectory()\`, \`addClassCleanup\` y DB dentro del directorio temporal. Las conexiones del test conservan sus \`finally: close()\`.
- Se eliminó la asignación directa a \`core.pipeline.orchestrator.compute_ast_hash\`; el test no llamaba al método real de \`pipeline.execute\` en ese bloque, sino a un \`side_effect\` parcheado.
- **Se mantiene el oráculo central:** FSM real \`PROCESSING → STALLED → PROCESSING\` a través de watchdog y resumer reales. La fase \`COMPLETED\` final es una **simulación del test**, no evidencia de ejecución real del pipeline único.
- Revisión solo por fuente/diff; **no se ejecutó pytest, no hay PASS/FAIL, ni prueba dinámica de aislamiento ni mutaciones**. No equivale a \`B05-R1 CLOSED\` todavía. Se necesita test focal en entorno Python seguro, revisar versión FSM, estado Git y sidecars antes/después, y ausencia de contaminación global.
- No se cambió CI, runtime ni GT. \`B05-R2\` caché histórica y \`B05-R3\` DB/fixtures de otros tests siguen pendientes.

**Próximo avance:** corregir los demás riesgos de escrituras fijas (B05-R2/R3) con fixtures Python temporales y oráculos observables. Ejecutar luego pruebas focales Python/pytest sin Docker para los casos revisados; las pruebas multiproceso y de PDF real permanecen en el laboratorio separado. Actualizar el plan rector con los SHA y límites; no acreditar el cierre de B05 hasta evidencia dinámica.

## 9. B05-R2/R3 — implementación de seguridad y oráculos, sin acreditación dinámica

**Cambios en \`tests_stabilization\`:**

| ID | Archivo/commit | Cambio verificable en fuente | Alcance real |
|---|---|---|---|
| B05-R2 | [\`test_e2e_walking_skeleton.py\`](../../../../tests/integration/test_e2e_walking_skeleton.py), \`e8a24bee\` | Se sustituyó \`tests/fixtures/e2e_cache_real.db\` por \`TemporaryDirectory\` + SQLite efímera; se eliminó la escritura condicional de AST en \`tests/fixtures\`, las asignaciones \`object.__setattr__\` de \`cache_hit\` y el mock de \`SummaryBuilder.build\`. Se observa \`FakeLLMProvider.translate_calls\`, métricas del \`CachedLLMProvider\` real y \`SummaryBuilder.build\` real en dos dispatches. | Contrato de caché del dispatcher **legacy R1**, no prueba E2E ni ruta G3/W08 actual |
| B05-R3a | [\`test_real_e2e.py\`](../../../../tests/integration/test_real_e2e.py), \`bdb85717\` | \`documents.db\` persistente sustituido por SQLite \`:memory:\` con \`addCleanup\`; FSM \`:memory:\` también cerrada con cleanup; nombre del test indica que \`pipeline.execute\` está mockeado. | Solo shape de resultado de consumidor FinOps; no ejecución del SUT ni gasto real |
| B05-R3b | [\`test_pipeline_orchestration.py\`](../../../../tests/integration/test_pipeline_orchestration.py), \`8552d628\` | \`documents.db\` persistente sustituido por SQLite \`:memory:\` con \`addCleanup\`; FSM \`:memory:\` cerrada; se elimina fabricación de \`sample_3_pages.pdf\` dentro de \`tests/fixtures\`. | Orquestador lógico real con parser mockeado y dispatcher fake; no validación de PDF físico |

**Inspección posterior de fuente (no observación de efectos de ejecución):** los tres archivos ya no contienen \`infra/db/documents.db\` ni \`tests/fixtures/e2e_cache_real.db\`, borrados \`os.remove\` ni escritura de sus fixtures. La caché dejó de asignar \`model_name\` manualmente o de parchear \`SummaryBuilder.build\`. Las conexiones SQLite y sus operaciones siguen siendo componentes **reales dentro de \`:memory:\` o un temporal**, no una simulación de SQLite.

**Impacto en la colección histórica:** se cambiaron los nombres de los tres testigos a identificadores cuyo alcance es más honesto. Por tanto **los nodeids antiguos de A-01 son datos históricos del SHA \`86cd6867\`, no la selección del HEAD nuevo**. Una nueva \`pytest --collect-only\` y la conciliación de markers/nombres en el SHA remediado siguen pendientes. No eliminar ni presentar los registros anteriores como prueba dinámica.

**Gate aún abierto:**
- [x] **R2/R3 — parche aplicado y revisión estática de rutas fijas/oráculos.**
- [ ] **R2/R3 — pytest focal real y casos negativos/positivos medidos** en entorno Python normal controlado, sin Docker.
- [ ] **B05 global — validación dinámica completa**, incluida la corrección R1 y revisión de side effects no previstos.
- [ ] **A-05 / A-06 — baseline selectiva**: no se ha ejecutado ningún cuerpo de test de este bloque.
- [ ] **C — sensibilidad**: ningún \`MUTATION_KILLED\` por esta implementación.

**Señal potencial de fallo que debe investigarse, no silenciarse:** \`AsyncDispatcher\` usa \`NullEventPlane\` para el contrato de caché legacy; \`FakeLLMProvider\` devuelve un \`InferenceResult\` compatible con su puerto real y el test exige una única llamada externa simulada. Si pytest falla por configuración/validación efectiva, mantener el fallo como evidencia y distinguirlo del problema de cache, sin autogenerar un expected ni reducir las aserciones para obtener verde.

**Norma adoptada por el owner:** Docker/Hyper-V no son prerequisitos de pytest ni de CI. El laboratorio C2 PDF→PDF del handoff queda diferido. Mantener \`B05-R1/R2/R3\` como **implementados, pendientes de validación** hasta tener resultados de pytest/Pyright/CI y evidencia de ausencia de escrituras fuera de los temporales.

## 10. A-06 / B05-Q1 — ejecutor focal sin Docker preparado (NO ejecutado)

Se incorporó [\`run_b05_focal_isolated.ps1\`](run_b05_focal_isolated.ps1) para **Windows PowerShell 5.1**. El script crea un clon Git independiente en el directorio temporal del owner **sin hardlinks**, lo fija al \`HEAD\` de la rama \`tests_stabilization\`, elimina el remoto del clon y guarda \`git_before.txt\` antes de llamar a pytest. Requiere que el owner tenga activa su \`venv\` Python y seleccione \`tests_stabilization\`; **no ejecuta la suite general, Docker, Hyper-V, servicios del pipeline ni proveedores reales**.

**Selección exacta** (\`-o addopts=\` desactiva la selección predeterminada de \`pyproject.toml\` solo para esta corrida, sin alterar ese archivo):

1. \`tests/integration/test_recovery_flow.py::TestRecoveryAndResumeEndToEnd::test_complete_crash_recovery_and_resume_lifecycle\`
2. \`tests/integration/test_e2e_walking_skeleton.py::TestLegacyDispatcherCache::test_legacy_cache_hit_observed_across_two_dispatches\`
3. \`tests/integration/test_real_e2e.py::TestRealE2EFinOps::test_mocked_pipeline_result_exposes_finops_fields\`
4. \`tests/integration/test_pipeline_orchestration.py::TestPipelineOrchestration::test_legacy_orchestrator_handoff_with_mocked_parser\`

**Ajustes para evitar una dependencia oculta de red del test:** la caché legacy (commit \`ad8c90db\`) y el test de consumidor FinOps (commit \`2d246698\`) usan un estimador de tokens determinista, sin cargar \`tiktoken.get_encoding\`/su caché remota. Esto **no cambia** la medición real del producto: esos tests no certifican tokenización de proveedor. Si otros imports externos intentan usar red, el script **no afirma que el SO la bloquee**.

Invocación en el **checkout del owner** (después de \`git pull --ff-only origin tests_stabilization\`, con \`venv\` activa):

\`\`\`powershell
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path
\`\`\`

El ejecutor orienta \`HOME/USERPROFILE/TMP/TEMP/PYTHONPATH\` al clon, desactiva bytecode y cacheprovider pytest, aparta variables cuyo nombre coincide con patrones de secretos y las restaura al concluir. Registra \`python_version.txt\`, \`pytest_version.txt\`, \`pytest_focal.log\`, \`nodeids.txt\`, \`summary.txt\`, \`git_after.txt\` y \`status_changes.txt\`. Conserva clon e informes para inspección; **no borra recursos, no resetea ni limpia ningún checkout**. El inventario Git post no certifica ausencia de archivos creados-y-borrados durante la ejecución; por ello hay que revisar también las ubicaciones temporales y el código antes de interpretar PASS.

**Límite de seguridad explícito:** el clon es aislamiento de workspace, no una frontera de seguridad fuerte. Se usa solo sobre los cuatro testigos recién inspeccionados y remediados, no se extrapola a otros tests, import hooks o suite completa. No introducir credenciales reales en el proceso. No ejecutar en el checkout principal del owner.

**Estado al preparar el ejecutor:** artefacto focal listo, sin tests ejecutados durante su construcción. La ejecución posterior del owner se registra en §11. El gate B05/A-05/A-06 no se cierra solo por preparar el runner ni por un PASS focal. Si el owner entrega \`summary.txt\`, \`pytest_focal.log\` y \`status_changes.txt\`, clasificaremos cada caso por contrato y se documentarán fallos reales sin ajustar oráculos por conveniencia.

## 11. Primera evidencia dinámica focal B05 (owner, 2026-11-15 local / 2026-11-16 UTC)

**Sujeto exacto:** rama `tests_stabilization`, SHA `73572285f99c5556691fe91ee56b633cba5a5ffe`. El owner actualizó por fast-forward `ceaa7d8..7357228` y ejecutó `run_b05_focal_isolated.ps1` desde PowerShell con `venv` activa. La primera versión del runner falló previamente por usar `$home`, que colisionaba con la variable de solo lectura `$HOME`; se reparó esa colisión y la comparación de inventarios vacíos en el commit `7357228`.

**Evidencia aportada por el owner**, no ejecución efectuada por el asistente:

| Evidencia | Resultado observado/reportado | Interpretación |
|---|---|---|
| `summary.txt` adjunto en conversación | `source_sha=73572285f99c5556691fe91ee56b633cba5a5ffe`, `pytest_exit_code=0`, `docker_used=false`, `no_OS_level_sandbox_claim=true` | Resultado atribuible a ese checkout; no es un certificado del sistema operativo |
| `pytest_focal.log`, fragmento textual compartido | `.... [100%]` y `4 passed in 2.62s` | Los cuatro nodeids seleccionados pasaron en la misma invocación; sin fallos/skips reportados |
| `status_changes.txt`, observado por owner como vacío | No diferencias Git pre/post reportadas en el clon | Sin cambios persistentes detectados en el inventario Git; no descarta escritura transitoria, rutas externas al clon ni efectos que no dejen huella |

**Casos seleccionados:** recuperación FSM `test_complete_crash_recovery_and_resume_lifecycle`; caché legacy `test_legacy_cache_hit_observed_across_two_dispatches`; consumidor FinOps mockeado `test_mocked_pipeline_result_exposes_finops_fields`; orquestador legacy con parser mockeado `test_legacy_orchestrator_handoff_with_mocked_parser`. No se ejecutó la suite completa, Docker/Hyper-V, G3/G5 daemon, laboratorio C0–C4 ni evaluación científica.

**Veredicto y pendientes:**
- [x] **B05-Q1 — Primera ejecución focal técnica acreditada por reporte del owner:** 4 PASS/4 seleccionados, exit 0, Git del clon sin diferencias persistentes reportadas, SHA exacto.
- [ ] **B05-R1/R2/R3 — cierre formal:** sigue pendiente validación de falsadores específicos, revisión de las aserciones frente al contrato y tipado local/CI. No equiparar `COMPLETED` mockeado con PDF→PDF real ni caché legacy con W08 soportado.
- [ ] **A05 global y A06 global:** no extrapolar de cuatro pruebas a 1.474 nodeids históricos ni a las rutas de SQLite/fixtures restantes.
- [ ] **C — sensibilidad:** no se han ejecutado mutaciones ni controles negativos del SUT como parte de este resultado.
- [ ] **Ausencia total de side effects:** inventario Git pre/post no acredita ausencia de creaciones y borrados temporales, ni efectos externos al clon.

**Siguiente decisión técnica:** revisar tipado de archivos de tests modificados y preparar controles negativos focales que fallen por las razones correctas, sin Docker y sin tocar runtime ni Ground Truth; los ensayos peligrosos restantes siguen fuera del selector de prueba del owner hasta inspección.

## 12. B05-Q2 — sensibilidad negativa y tipado: preparación sin resultados inventados

**Continuación posterior a primera baseline verde:** [\`probe_b05_sensitivity.py\`](probe_b05_sensitivity.py) y el parámetro opcional \`-CheckSensitivity\` del [ejecutor B05](run_b05_focal_isolated.ps1). Se añadió un guard de no-\`None\` en el retorno de caché para que la aserción sobre el payload use un objeto comprobado, sin alterar el SUT.

**Procedimiento previsto en Windows PowerShell 5.1, desde la raíz con \`venv\` activada y rama \`tests_stabilization\` actualizada:**

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckSensitivity
\`\`\`

El runner crea **otro clon Git independiente, nuevo, sin hardlinks ni remoto**; ejecuta de nuevo los cuatro tests de baseline del SHA nuevo. **Solo si los cuatro pasan** habilita dos subprocess Python independientes. El helper modifica **en memoria** la clase SUT con \`unittest.mock.patch\`; **no edita archivos productivos**:

| Mutación | Punto de inyección temporal | Razón esperada para que el test protector falle |
|---|---|---|
| \`fsm_watchdog\` | \`AbandonedProcessWatchdog.execute_sweep\` se convierte en no-op | La lectura de FSM real permanece \`PROCESSING\` en lugar de \`STALLED\`; falla la aserción del test de recuperación |
| \`legacy_cache_read\` | \`CachedLLMProvider._read_cache\` devuelve siempre \`None\` asíncronamente | La segunda ejecución vuelve a llamar al fake: \`translate_calls == 2\` en vez de \`1\`; falla el mensaje \`Cache hit must avoid a second fake provider call\` |

**Criterio de aceptación de la herramienta:** código pytest \`1\`, exactamente \`1 failed\`, \`AssertionError\` y el indicio específico de contrato en el log; rechazar errores de recolección, \`INTERNALERROR\`, PASS accidental o fallo por infraestructura. Los resultados se guardan en \`mutation_fsm_watchdog.log\`, \`mutation_legacy_cache_read.log\`, \`mutation_summary.json\` y \`mutation_runner.log\`. El clon y las salidas se conservan para revisión. Un \`MUTATION_KILLED\` de esta herramienta solo demuestra sensibilidad al defecto **inyectado**, no ausencia de todos los defectos. Si falla la baseline, la mutación queda \`NOT_RUN\`, nunca \`KILLED\`.

**Pyright técnico, separado del check oficial:** el [\`pyrightconfig.json\`](../../../../pyrightconfig.json) versionado excluye \`tests/\`; por ello el paso \`pyright\` de [\`ci.yml\`](../../../../.github/workflows/ci.yml) no acredita el tipado B-05. Para inspeccionar estos cuatro archivos de manera explícita **sin cambiar la configuración oficial** se propone ejecutar, desde la raíz del repositorio con el ejecutable local Pyright disponible:

\`\`\`powershell
pyright tests/integration/test_recovery_flow.py tests/integration/test_e2e_walking_skeleton.py tests/integration/test_real_e2e.py tests/integration/test_pipeline_orchestration.py
\`\`\`

Registrar stdout/stderr y código de salida, incluyendo cualquier dependencia arrastrada por los imports. Si el alias local sobreescribe flags/entorno, registrar el comando realmente ejecutado; no presentar Pyright del CI como si hubiera chequeado tests.

**CI:** \`.github/workflows/ci.yml\` mantiene \`python -m pytest -m "not e2e" -q -ra\` y los casos B05 no tienen marker \`e2e\` (por fuente), por lo que son seleccionables en el check técnico; **no se disparó ni aprobó ningún workflow** como parte de esta preparación. El contraste de nodeids y markers de la colección A-01 histórica necesita reproducirse sobre el SHA remediado antes de afirmar alcance global.

**Estado:** C-control negativo \`fsm_watchdog\` y \`legacy_cache_read\` **DISEÑADOS/IMPLEMENTADOS COMO HERRAMIENTA, NO EJECUTADOS**. \`MUTATION_KILLED=0\` acreditados para esta ronda; B-05, A-05 global, A-06 global y C siguen abiertos.
