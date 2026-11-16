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

**Estado al redactar §12:** ambos controles preparados, todavía no ejecutados. La evidencia dinámica posterior del owner figura en §13; B-05, A-05 global, A-06 global y C general siguen abiertos.

## 13. B05-Q2 — sensibilidad demostrada por el owner, 2026-11-16 (hora Argentina)

**Sujeto testificado:** commit \`ffd702535a079f37cff87659792ae86a98b40cad\` (\`tests_stabilization\`), clon independiente conservado bajo carpeta temporal. El owner ejecutó \`run_b05_focal_isolated.ps1 -CheckSensitivity\` con su \`venv\`, sin Docker/Hyper-V, sobre ese SHA; reportó \`pytest exit code: 0\` y \`Sensitivity exit code: 0\`. El RAR de evidencias adjunto en la conversación contiene \`mutation_summary.json\` y los dos logs completos, inspeccionados por el asistente. La salida completa de la *segunda* baseline focal no fue adjuntada, por lo que su PASS se respalda con código 0 reportado por el runner, no con un conteo de nodos visto en \`pytest_focal.log\`.

| Mutación | Resultado del archivo real | Motivo de fallo contractual | Veredicto |
|---|---|---|---|
| \`fsm_watchdog\` | Pytest exit **1**, \`1 failed in 0.91s\`; \`test_recovery_flow.py:70\` | \`AssertionError: 'PROCESSING' != 'STALLED'\`; al desactivar \`execute_sweep\`, la FSM **no** pasa a STALLED | **MUTATION_KILLED** |
| \`legacy_cache_read\` | Pytest exit **1**, \`1 failed in 0.73s\`; \`test_e2e_walking_skeleton.py:148\` | \`AssertionError: 2 != 1 : Cache hit must avoid a second fake provider call\`; dos inferencias del fake por lectura de caché siempre MISS | **MUTATION_KILLED** |

**Verificación de causa:** los logs muestran fallos del **assert del test protector**, no errores de imports/colección/infraestructura. El resumen JSON registra \`verdict=TWO_KILLED\` con \`revision_sha=ffd702535...\` y ambos casos con \`python_exit_code=1\`. Los dos controles consisten en reemplazos temporales **en memoria** de métodos del SUT, en subprocesos aislados; no alteran los archivos productivos. No implican una métrica de mutation coverage general ni testifican la ruta PDF→PDF activa.

**Tipado local explícito:** el owner ejecutó \`pyright\` señalando los cuatro archivos B05: \`0 errors, 0 warnings, 0 informations\`. La advertencia separada notifica una versión Pyright más reciente (\`v1.1.411 → v1.1.414\`); no es error de tipado. El \`pyrightconfig.json\` oficial **excluye tests/**; no se atribuye este resultado al check obligatorio de GitHub Actions.

**Alcance y gates, sobre el SHA testificado:**

- [x] **B05-Q2:** baseline focal previa exit 0 reportada + **2/2 controles negativos detectados por causa contractual**.
- [x] **Pyright local focal:** 4 archivos explícitos, **0 errores/0 advertencias** reportados.
- [ ] **B05-R1/R2/R3 cierre global:** revisar garantías residuales y efectos de fixtures/sidecars externos, y no afirmar que \`COMPLETED\` mockeado certifica el pipeline único.
- [ ] **CI GitHub de este SHA:** no se ha verificado un run/check actual; el selector \`-m "not e2e"\` sigue siendo la evidencia de inclusión por código, no un resultado CI.
- [ ] **C general:** las dos mutaciones legacy acreditadas **no sustituyen** falsadores P0 del camino OCR/G3/G5 activo.
- [ ] **A05/A06 general:** el reporte no acredita 1.474 tests, efectos temporales fuera de Git ni aislamiento del SO.

**Próxima prioridad:** continuar la auditoría de los falsos oráculos P0 de \`test_golden_parser.py\` y \`test_chunker_snapshot.py\` y la cobertura focal de barreras G3/G5 soportadas; evitar ampliar la suite sin revisar las rutas de escritura restantes. No modificar GT, producción ni el CI como atajo para conseguir PASS.

## 14. A-05 — actualización de riesgos vigentes después del cierre documental de A-04 (2026-11-16)

> **Sujeto leído:** \`tests_stabilization\` a SHA \`91285fc825aaf3149dbd7af74fa91efd3f8a2b0b\`. Esta sección **actualiza**, no borra, los riesgos históricos de §§1–13. El owner aprobó la clasificación de A-04 por función/parametrización material y pidió continuar A-05 sin sobreingeniería. **Ningún test nuevo se ejecutó** durante este análisis; A-05 global **ABIERTO**.

### 14.1 Estado real de los riesgos de ejecución (fuente actual, no informe histórico)

| Ref. | Evidencia precisa del HEAD | Riesgo y decisión de A-05 |
|---|---|---|
| **A05-FS-01 · CWD** | \`tests/unit/test_tectonic_runner.py::test_no_crash_log_written_to_cwd\` obtiene \`os.path.join(os.getcwd(), "tectonic_crash.log")\` y hace **\`os.remove(crash_log)\` antes del test y en \`finally\` si existe**. \`subprocess.run\` de Tectonic está mockeado. | **Bloquea ejecutar este test en el checkout del owner.** Puede eliminar un archivo legítimo previo; el test debería comprobar ausencia sin borrar: CWD temporal aislado/fixture de cambio de CWD o testigo equivalente que no altere el archivo ajeno. Es problema **del test**, no defecto demostrado de Tectonic. |
| **A05-DB-01 · documents.db legacy** | \`tests/integration/test_translation_structure.py\` y \`test_translation_technical.py\` hacen \`get_connection("infra/db/documents.db", timeout=30)\` en \`setUp\` **antes** de comprobar si hay golden y hacer \`skipTest\`. \`infra/db/connection.py\` resuelve por defecto bajo \`BASE_DIR\`, abre SQLite, configura WAL y permite redirección opt-in con \`SQLITE_STATE_DIR\`. | **Bloquea ejecutarlos en el checkout del owner sin redirección/aislamiento.** Un SKIP del cuerpo no impide que el setup haya tocado la DB. Mitigación B-05 mínima: conexión desechable o setup simplificado si DB no es parte del SUT; no generar expected científicos ni convertir SKIP en PASS. |
| **A05-DB-02 · cache fixture** | \`tests/integration/test_translation_layer.py\` crea \`tests/fixtures/integration_cache_<uuid>.db\` en \`asyncSetUp\`; \`asyncTearDown\` elimina DB y sidecars \`-wal\`/\`-shm\` por nombre, tolerando \`PermissionError\`. | **Bloquea ejecutar en working tree protegido**: crea/borraría bajo \`tests/fixtures\`. Mover solo esa cache SQLite a \`TemporaryDirectory\`/fixture temporal, con cleanup al finalizar. Es dispatcher/assembler **legacy**, no G3/G5 soportado. |
| **A05-NET-01 · proveedor opt-in** | \`tests/integration/test_embedding_smoke.py\` usa \`GROQ_API_KEY\`; sin ella hace \`skipTest\`, con ella invoca el proveedor Groq real. | **No ejecutar en entorno con credenciales/red**. Un \`skip\` aquí no representa cobertura del transporte. En A-06 usar seleccionadores explícitos y entorno sin secretos; guard Python de socket o clon independiente **no** acredita bloqueo OS. |
| **A05-MANUAL-01 · stress no coleccionado** | \`tests/test_pipeline.py\` contiene \`run_stress_tests()\` y rama \`if __name__ == "__main__"\`; escribe \`tests/stress_report.json\` y puede crear \`tests/output\`, invocando \`run_pipeline\`. **No** define tests \`test_*\` recolectables. | **No ejecutarlo manualmente** por tratarse de un script operativo con outputs versionados y posible proveedor; no contarlo como caso de la suite pytest. |
| **A05-FIXED-HIST · riesgos mitigados anteriormente** | \`tests/integration/test_recovery_flow.py\` usa actualmente \`TemporaryDirectory\`/\`addClassCleanup\`, sin DB fija ni monkeypatch global sin restauración; \`test_real_e2e.py\`, \`test_pipeline_orchestration.py\` y \`test_e2e_walking_skeleton.py\` fueron remediados focalmente B05-R2/R3 (véanse §§8–13 y sus evidencias). | **No reabrir como si el código histórico siguiera vigente.** Los PASS focales/controles negativos anteriores acreditan esos testigos en sus respectivos SHA, pero **no** ausencia completa de I/O de la suite. |

### 14.2 Decisión de seguridad y mínimo trabajo pendiente

1. **A05-QS1 — Inventario de peligros actuales: HECHO por revisión de fuente.** Los tres riesgos de CWD/SQLite no dependen de nombres «E2E»; \`-m "not e2e"\` puede incluirlos. La última colección es del SHA anterior a la prueba UTF-8: **no** equivale a una ejecución ni a un recenso del HEAD actual.
2. **A05-QS2 — Contención hoy: PARCIAL.** El runner de clon independiente, con \`HOME/TEMP\` propios y credenciales apartadas, permitió ejecuciones **focales** ya acreditadas con \`status_changes.txt\` vacío. No ejecutó ni verificó de forma amplia los tests inseguros anteriores. **Git post limpio no detecta archivos creados y borrados, escrituras fuera del clon ni egress.**
3. **A05-QS3 — Remediación mínima a elevar a B-05: PENDIENTE.** Solo tres puntos de edición en tests: (i) \`tectonic_crash.log\` sin borrados en CWD; (ii) \`documents.db\` de los dos setups legacy redirigida a recurso descartable; (iii) caché de \`test_translation_layer.py\` fuera de \`tests/fixtures\`. **Sin cambios al runtime, a CI, al corpus o al GT**. Cada corrección debe demostrar que preserva el oráculo original y no convierte un FAIL/SKIP científico en PASS.
4. **A05-QS4 — Seguridad para suite amplia: BLOQUEADA.** Antes de A-06 completa, exigir que esos tres peligros de ejecución estén mitigados y que los restantes imports/fixtures/plug-ins hayan sido revisados para I/O externo. Ejecutar en un clon, con pre/post inventario de archivos sensibles; para **acreditar ausencia de egress físico o aislamiento de host** se necesita control de SO independiente. **Docker/VM no son requisitos para los tests puros/focales, pero un clon no demuestra sandbox de SO.**
5. **A05-QS5 — CI y selección: PENDIENTE.** El workflow \`ci.yml\` no corre automáticamente por push directo a \`tests_stabilization\`, y un \`pytest -m "not e2e"\` como texto de workflow no es resultado dinámico de GitHub Actions. No afirmar que A-05 o A-06 estén completos por los PASS focales.

**Regla de no sobreingeniería:** no crear más probes, harnesses o archivos auxiliares para estos tres hallazgos. Resolverlos en el **test existente** en una remediación B-05 focal y verificable **cuando el owner lo autorice como cambio de código**. Mientras tanto el avance correcto de A-05 es esta matriz y el bloqueo de la suite amplia sobre el checkout habitual. **No tocar la eliminación PDF intencional del owner ni ejecutar limpieza destructiva.**

## 15. A05-FS/DB — correcciones mínimas autorizadas en tests existentes (2026-11-16)

**Autorización expresa:** el owner aprobó editar **tests** para eliminar los tres riesgos de §14, sin tocar runtime, CI ni Ground Truth. Cambios aplicados únicamente sobre \`tests_stabilization\`, sin ejecutar una suite en este entorno. Se respetan las garantías originales de los tests y **se mantiene prohibido correr la suite completa directamente sobre el working tree del owner**.

| Riesgo de §14 | Archivo/cambio aplicado | Contrato preservado y verificación todavía pendiente |
|---|---|---|
| **A05-FS-01** | \`tests/unit/test_tectonic_runner.py\`: \`test_no_crash_log_written_to_cwd\` usa \`monkeypatch.chdir(tmp_path)\`, verifica ausencia de \`tectonic_crash.log\` **solo dentro de ese CWD descartable**, y exige \`pytest.raises(Exception, match="Fallo de Tectonic")\`. Se eliminaron los dos \`os.remove(crash_log)\` del CWD del owner. | Sigue comprobando que \`HostTectonicRunner\`, al recibir código de compilador no cero, no deja log en CWD y falla. Subprocess sigue mockeado. **No hay test PASS nuevo todavía.** |
| **A05-DB-01** | \`tests/integration/test_translation_structure.py\` y \`test_translation_technical.py\`: \`SQLiteDocumentRepository\` recibe una conexión propia \`sqlite3.connect(":memory:")\` en lugar de \`get_connection("infra/db/documents.db")\`. Ambas registran \`addCleanup(self.doc_conn.close)\` y también \`addCleanup(self.db.close)\` para la FSM ya temporal. | Se conserva \`TranslationPipeline\` legacy con parser/chunker/dispatcher originales del test; las comprobaciones de snapshot siguen intactas, incluidos los **SKIP** condicionales por falta de golden. Sin conexión a DB persistente aun si \`setUp\` ocurre antes del SKIP. **No se regeneró ni se modificó golden.** |
| **A05-DB-02** | \`tests/integration/test_translation_layer.py\`: la caché \`CachedLLMProvider\` utiliza \`TemporaryDirectory\` registrado inmediatamente con \`self.addCleanup\`; sus posibles sidecars WAL/SHM quedan dentro de esa carpeta. Se elimina la escritura a \`tests/fixtures\` y el cleanup manual que silenciaba \`PermissionError\`. | Se conserva el fake de provider, los tres \`TranslationUnit\` y las aserciones de orden. La limpieza se ejecuta también tras error de \`asyncSetUp\`; conexión aiosqlite cierra por operación según SUT. **No afirmar que certifica G3/G5 o un ensamblado PDF real.** |

**Revisión estática posterior a la edición:** se reabrieron los cuatro archivos y se verificó que no quedan \`os.remove(crash_log)\`, \`get_connection("infra/db/documents.db")\` ni \`tests/fixtures/integration_cache_<uuid>.db\`; las cuatro funciones \`test_*\` afectadas mantienen sus identidades, y las conexiones/temporales tienen cleanup. El diff de producción, CI, snapshots y GT es nulo. **A05-QS3: corrección de fuente IMPLEMENTADA, VALIDACIÓN DINÁMICA PENDIENTE**.

**Próxima comprobación estrictamente focal, no otra campaña:** ejecutar únicamente los **9 tests existentes** en un clon independiente sin hardlinks, sin credenciales/proveedor real y con CWD controlado: seis \`test_*\` de \`test_tectonic_runner.py\`, uno de cada test legacy \`translation_structure\`, \`translation_technical\`, y uno de \`translation_layer\`. Registrar SHA, conteo **PASS/FAIL/SKIP** (los goldens pueden causar SKIP), Pyright local sobre los cuatro archivos, \`status_changes.txt\` y residuos SQLite/log bajo clon. **SKIP no es PASS de contrato científico**, pero la ausencia de DB persistente debe poder verificarse por inspección de código y de inventario. No usar \`-m "not e2e"\` global.

**Riesgo residual A05-P4/P6:** no hay sandbox OS/egress acreditado; Git limpio no prueba ausencia de efectos creados-y-borrados. La selección CI global y los imports/plug-ins todavía requieren revisión/contención antes de declarar A-05 o A-06 cerrado. No modificar \`docs\` históricos FROZEN: este apéndice es la evidencia incremental de cambios aprobados.

## 16. Selección focal A-05 lista para validación del owner (2026-11-16)

Después de las correcciones a los cuatro archivos de tests registradas en §15, se extendió el **ejecutor existente**, sin crear otro script, con el switch aislado \`-CheckA05Safety\`. El cambio selecciona exactamente **cuatro entradas pytest** (el archivo entero \`test_tectonic_runner.py\`, que contiene seis tests, y tres nodeids completos legacy), **nueve tests previstos**, sin invocar mutaciones, Tectonic externo ni proveedor real. El runner sigue creando clon Git \`--no-hardlinks\`, HEAD detached y sin remoto; redirige HOME/TEMP/cachés y retira variables de entorno que parecen secretos. Además de \`pytest_exit_code\`, en este modo devuelve **exit 4** cuando \`status_changes.txt\` no está vacío. No implica control del egress a nivel OS ni ausencia de I/O transitorio.

\`\`\`powershell
git pull --ff-only origin tests_stabilization

& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 \`
  -RepoRoot (Get-Location).Path \`
  -CheckA05Safety

pyright tests/unit/test_tectonic_runner.py \`
        tests/integration/test_translation_structure.py \`
        tests/integration/test_translation_technical.py \`
        tests/integration/test_translation_layer.py
\`\`\`

**Evidencia solicitada:** \`summary.txt\`, \`pytest_focal.log\`, \`status_changes.txt\`, \`git_before.txt\`, \`git_after.txt\` y salida de Pyright. Deben distinguirse explícitamente **PASS / FAIL / SKIP**: un golden inexistente puede provocar SKIP legítimo de los dos contratos legacy, y ni un SKIP ni un test del renderer con subprocess mockeado acreditan una compilación científica. Antes de recibir esos resultados **no existe baseline dinámica nueva de A-05 para este SHA**. No ejecutar la suite técnica global en el working tree del owner; no limpiar ni restaurar la eliminación PDF intencional.

## 17. A-05 — ejecución focal acreditada y preflight restante (2026-11-16)

**Fuente primaria:** el owner adjuntó \`reports.rar\` (RAR5) con **cinco archivos inspeccionados directamente**: \`summary.txt\`, \`pytest_focal.log\`, \`git_before.txt\`, \`git_after.txt\` y \`status_changes.txt\`. La revisión reportada es exactamente **\`6ecfc2c5726b86c5df91a839c232e73bcee52f82\`**, con \`a05_safety_requested=True\`, \`pytest_exit_code=0\`, \`docker_used=false\` y \`no_OS_level_sandbox_claim=true\`. El owner también ejecutó Pyright explícito sobre los **cuatro archivos de tests** modificados, con **\`0 errors, 0 warnings, 0 informations\`**; el aviso de versión más nueva es informativo y separado del tipado.

| Testigos de las correcciones §15 | Evidencia real | Dictamen |
|---|---|---|
| \`tests/unit/test_tectonic_runner.py\` | **6 PASS**; Tectonic está simulado por \`subprocess.run\`, y el test de log usa CWD \`tmp_path\` con excepción esperada | **PASS focal** de contrato de runner; no ejecución física de Tectonic |
| \`tests/integration/test_translation_structure.py\` | **SKIP**: \`test_structural_integrity_against_golden_snapshot\`, golden estructural ausente (línea 57) | **SKIP legítimo, NO PASS** del snapshot legacy |
| \`tests/integration/test_translation_technical.py\` | **SKIP**: \`test_latex_token_sets_and_balances\`, golden técnico ausente (línea 57) | **SKIP legítimo, NO PASS** del snapshot/LaTeX legacy |
| \`tests/integration/test_translation_layer.py\` | **1 PASS**, fake provider y SQLite cache en directorio temporal | **PASS focal** del flujo legacy acotado |
| **Resumen** | **\`7 passed, 2 skipped in 7.73s\`**, 0 FAIL; \`git_before.txt\`, \`git_after.txt\` y \`status_changes.txt\` **0 bytes** cada uno | **A05-FS-01/DB-01/DB-02: mitigaciones implementadas y focal ejecutada**, sin cambios Git persistentes en el clon |

**Interpretación estricta:** los dos SKIP muestran que los testigos legacy con golden no ejecutaron su cuerpo; la mitigación de su setup proviene de inspección directa de \`sqlite3.connect(":memory:")\` y \`addCleanup\`, y del hecho de que el runner no dejó diferencias Git. **No certificar la integridad de los golden ni ausencia universal de efectos transitorios**. Tampoco existe un aislamiento OS de red/host por usar un clon.

### 17.1 Preflight de fuente de imports, plugins y selección actual

Se contrastaron \`pyproject.toml\`, \`tests/smoke/conftest.py\`, \`.github/workflows/ci.yml\`, \`test_embedding_smoke.py\` y el ejecutor focal, todos en \`tests_stabilization\`:

- \`pyproject.toml\` configura **\`addopts = -m "not e2e"\`** para la ejecución por defecto. En CI, \`ci.yml\` selecciona además \`unit\`, \`integration and not regression\` y \`not e2e\`; el nombre del archivo NO excluye automáticamente pruebas con red, mocks o SKIP.
- \`tests/smoke/conftest.py\` define \`reliability_pipeline\` como fixture y construye sus validadores **dentro de la función de la fixture**, no directamente al importar \`conftest\`. Los imports de sus dependencias y la carga de plugins por pytest siguen siendo superficies de ejecución que no se han confinado a nivel SO.
- \`tests/integration/test_embedding_smoke.py\` no tiene marker \`e2e\` propio, por lo que **puede ser seleccionado** por \`not e2e\`. Si existe \`GROQ_API_KEY\`, \`GroqProvider.translate\` intenta transporte **real**. No se seleccionó ese archivo en la corrida A-05; el ejecutor aislado sí retira variables con patrones de secretos. **No afirmar que el CI garantiza cero egress solo por su selección actual**.
- \`run_b05_focal_isolated.ps1\` crea clon independiente sin hardlinks, elimina su remoto, establece \`PYTHONDONTWRITEBYTECODE\`, \`HOME/TEMP\` y purga variables de secretos; **no establece \`PYTEST_DISABLE_PLUGIN_AUTOLOAD\` ni un firewall físico**. Sus inventarios \`git_before/after\` y \`status_changes\` permiten certificar **solo** ausencia de cambios persistentes Git en el clon para estos nueve tests.
- \`ci.yml\` responde a \`push\` de \`main\`/\`develop\` y PR contra \`main\`/\`pipeline_stabilization\`, no a un push directo de \`tests_stabilization\`. **Ningún resultado de GitHub Actions del HEAD fue inspeccionado**. La ausencia de \`tests/conftest.py\` y \`pytest.ini\` no descarta \`conftest\` anidados, \`pyproject.toml\` ni plugins instalados.

### 17.2 Cierre focal vs. gate completo

- [x] **A05-QS3, tres riesgos concretos:** fuente corregida en **cuatro tests**, focal \`7 PASS/2 SKIP\`, Pyright 0 y Git persistente limpio según cinco reportes del owner. **No** requiere repetir mutaciones ni regenerar golden.
- [ ] **A05-P4, imports/decoradores/plugins/egress:** la revisión estática por fuentes se amplió y se identificó como riesgo específico el smoke Groq seleccionado si hay credenciales; falta una **condición verificable de no-egress** para ejecutar la suite amplia. El clon y la purga de secretos son mitigaciones de mejor esfuerzo; no prueba OS sandbox.
- [ ] **A05-P6, efectos completos:** el antes/después Git en el clon está limpio en esta focal; no hay observación independiente de archivos ignorados, efectos creados y borrados ni rutas externas al clon bajo ejecución global.
- [ ] **A05/A06 global y CI HEAD:** no autorizados todavía. **Siguiente decisión mínima**: imponer una condición explícita y verificable para no activar tests con proveedor real durante ejecución técnica, y conservar la ejecución global exclusivamente en entorno descartable/aislado con evidencia de procesos y filesystem. **No** ejecutar \`pytest -m "not e2e"\` en el checkout habitual. A-06 se abre solo después de satisfacer esos pre-requisitos.

**No se modificaron tests/producción/CI/GT en esta evaluación de resultados y fuentes.**

## 18. A-05 — no-egress opt-in para smoke Groq (2026-11-16)

**Fuente observada antes del cambio:** \`tests/integration/test_embedding_smoke.py::TestProviderSmoke::test_isolated_generation_request\` no tiene marker \`e2e\` y estaba seleccionado por \`not e2e\`. Ejecutaba \`GroqProvider.translate\` si \`GROQ_API_KEY\` estaba presente; esa condición **no constituía autorización del owner para acceder a red**. El selector global \`pyproject.toml\`/CI no era barrera de egress.

**Corrección mínima en el test existente, sin cambios a runtime/CI:** \`test_isolated_generation_request\` ahora **primero** exige \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=1\`, y **después** exige \`GROQ_API_KEY\`. Cuando cualquiera falta, levanta \`unittest.SkipTest\` **antes de construir** el proveedor. Se agregó una comprobación negativa dentro del mismo archivo, \`test_live_provider_requires_explicit_opt_in\`: inyecta solo una credencial sintética, fuerza opt-in \`0\`, espera \`SkipTest\` y comprueba \`GroqProvider.assert_not_called()\`. No se realiza request ni se usan credenciales reales en ese control. **El smoke real conserva su comportamiento cuando ambas condiciones están habilitadas voluntariamente**; no convertirlo en fake PASS.

**Runner focal reutilizado:** \`-CheckA05Safety\` selecciona ahora los nueve tests previos **más los dos casos de \`test_embedding_smoke.py\`**, total **11 nodeids nominales**. El entorno del clon fija expresamente \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=0\` además de eliminar credenciales de variables de entorno. Resultado esperado de selección, **no resultado observado**: **8 PASS / 3 SKIP** si los tests previos conservan los 7 PASS/2 SKIP y el nuevo control pasa; el smoke de red debe figurar SKIP. El control de Git final del clon continúa en vigor.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 \`
  -RepoRoot (Get-Location).Path \`
  -CheckA05Safety

pyright tests/integration/test_embedding_smoke.py \`
        tests/unit/test_tectonic_runner.py \`
        tests/integration/test_translation_structure.py \`
        tests/integration/test_translation_technical.py \`
        tests/integration/test_translation_layer.py
\`\`\`

**Acreditación pendiente de owner:** \`pytest_focal.log\`, \`summary.txt\`, \`status_changes.txt\`, \`git_before.txt\`, \`git_after.txt\` y Pyright focal. **No afirmar PASS ni ausencia física de egress antes de ejecutarlos**. El opt-in bloquea **esta llamada Groq desde este test**, no todos los posibles caminos de socket/import/plugin. A05-P4/P6 y suite técnica completa siguen abiertos; no ejecutar la suite global en working tree, no modificar GT/corpus ni requerir Docker para estos casos puros. Si se quisiera certificar ausencia de egress de toda la suite sería necesaria una condición adicional del entorno de ejecución (aislamiento de red independiente), no otro mock presentado como firewall.

## 19. A-05 — corrida de once tests verificada y condiciones de paso a A-06 (owner, 2026-11-16)

**Evidencia fuente inspeccionada en el RAR5 adjunto \`reports.rar\`:** \`git_after.txt\` (0 bytes), \`git_before.txt\` (0 bytes), \`pytest_focal.log\`, \`status_changes.txt\` (0 bytes), \`summary.txt\`. El SHA **\`65385307e11cc2db8795c3e6c6343d94ef9d2bdd\`** está presente en \`summary.txt\` con \`a05_safety_requested=True\`, \`pytest_exit_code=0\`, \`docker_used=false\`, \`no_OS_level_sandbox_claim=true\` y \`sensitivity_requested=False\`/\`sensitivity_exit_code=-1\` (no hubo mutaciones). El usuario aportó Pyright explícito: **0 errors, 0 warnings, 0 informations**.

| Testigos seleccionados en A-05 | Resultado del log | Interpretación |
|---|---|---|
| Seis pruebas de \`test_tectonic_runner.py\` | **6 PASS** | Subprocess Tectonic mockeado, CWD temporal; no compilación real |
| \`test_translation_layer.py\` | **1 PASS** | Cache SQLite en temporal, proveedor fake; alcance legacy |
| \`test_embedding_smoke.py::test_live_provider_requires_explicit_opt_in\` | **1 PASS** | Con credencial sintética y opt-in deshabilitado, verifica \`SkipTest\`/proveedor no construido; no request |
| \`test_translation_structure.py\` | **1 SKIP** (golden estructural ausente) | No certifica estructura científica, aunque setup SQLite ya no use DB persistente |
| \`test_translation_technical.py\` | **1 SKIP** (golden técnico ausente) | No certifica tokens/LaTeX científico |
| \`test_embedding_smoke.py::test_isolated_generation_request\` | **1 SKIP** por \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS\` distinto de 1 | Evitó ejecutar request real de Groq en el smoke |
| **Total** | **\`8 passed, 3 skipped, 2 warnings in 11.34s\`**, \`pytest_exit_code=0\` | **Baseline de 11 casos sin fallos**, tres saltos explícitos; Git antes/después y cambios persistentes del clon vacíos |

Las **dos advertencias** observadas no son resultado de los casos: (1) \`google.api_core\` advierte de soporte futuro de Python 3.11; (2) \`google.generativeai\` advierte de paquete descontinuado. Son deuda de dependencias a gestionar con su proceso propio, **no** permiso para migrar SDK o producción dentro de A-05. El mensaje de actualización disponible de Pyright tampoco es fallo de tipado.

### 19.1 Preflight mínimo para la suite técnica posterior — sin herramienta adicional

1. **No-ejecutar sobre checkout personal:** usar el clon independiente no enlazado, HEAD detached y sin remoto. Conservar la copia y los informes tras cualquier fallo; no reset/clean ni tocar la eliminación PDF intencional del owner.
2. **Sin red real voluntaria:** \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=0\`, retirar credenciales/secretos como ya hace el runner focal; excluir cualquier test opt-in de proveedor externo. Esto **evita la petición de Groq desde el smoke auditado**, pero **no** demuestra bloqueo de egress físico para imports, otros procesos o sockets inesperados.
3. **Plugins controlados:** el \`pyproject.toml\` y el runner focal no establecen \`PYTEST_DISABLE_PLUGIN_AUTOLOAD\`; \`tests/smoke/conftest.py\` importa validadores al cargar y construye la fixture al solicitarla. Para una ejecución amplia, **registrar el conjunto de plugins cargados**; si se decide desactivar autoload, habilitar explícitamente los plugins realmente requeridos, especialmente \`pytest-asyncio\`, y no declarar PASS si hay skips/errores por plugins omitidos. No se exige cambiar el CI actual dentro de este expediente.
4. **Efectos persistentes y transitorios:** verificar inventarios Git antes/después, outputs y SQLite/sidecars en temporales. Un Git limpio y el CWD aislado son garantías acotadas: **no observan todo I/O fuera del clon o creación y borrado entre inventarios**. Control OS independiente de red/host si se exige atestación de ausencia física de egress.
5. **Selección A-06:** partir de los selectores existentes (\`unit\`, \`integration and not regression\`, \`not e2e\`), identificar qué se selecciona realmente y registrar **PASS, FAIL, SKIP, XFAIL** y SHA. Sin tratar el smoke proveedor omitido como PASS ni extender automáticamente E2E científico/GT. La ejecución completa sigue **pendiente** y debe autorizarse en entorno controlado, no en working tree.

**Estado:** las cuatro ediciones de tests A-05 y el guard explícito Groq cuentan con fuente inspeccionada y baseline focal de 11 nodeids. **A-05-P4/P6 siguen ABIERTOS** en cuanto a una ejecución amplia y control/observación real de imports, plugins, red y efectos transitorios; no se ha certificado aislamiento OS. No se agregaron tests/scripts, no se corrió la suite completa y no se alteraron producción, CI, corpus ni GT en este registro.

## 20. A-05 P4/P6 — preflight sin ejecución preparado (2026-11-16)

**Decisión:** no repetir los 11 tests acreditados en §19, no abrir otro harness ni exigir Docker por rutina. Se reutilizó \`run_b05_focal_isolated.ps1\` para añadir una opción **\`-PreflightA06\` exclusivamente documental y de solo lectura** y un switch opcional **\`-CaptureProtectedPaths\` para futuras ejecuciones autorizadas en clon**. Ninguna de las dos modalidades ejecutadas hasta recibir evidencia del owner. **P4/P6 siguen [ ]**; preparar un control no certifica haberlo superado.

### 20.1 Comando mínimo de preflight (sin pytest)

\`\`\`powershell
git pull --ff-only origin tests_stabilization

& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 \`
  -RepoRoot (Get-Location).Path \`
  -PreflightA06
\`\`\`

El ejecutor: comprueba rama/SHA, crea clon nuevo \`--no-hardlinks\` y HEAD detached sin remoto, verifica estado Git limpio, calcula \`protected_before.tsv\` para archivos de **\`tests/fixtures\`, \`tests/golden\`, \`infra/db\`** (incluye ocultos/ignorados y SHA-256; rechaza reparse points observados), y lee **metadatos de entrypoints \`pytest11\` y versiones de \`pytest\`/\`pytest-asyncio\`** con \`python -I -B -c\`, sin importar plugins ni pytest. Conserva \`plugin_entrypoints.txt\`, \`preflight_summary.txt\`, \`protected_before.tsv\`, \`git_before.txt\`, \`git_after.txt\`. No toca corpus canónico ni snapshots, ni modifica el working tree personal.

**Importante:** \`plugin_entrypoints.txt\` enumera *plugins instalados anunciados*, **no** cuáles pytest cargó durante una colección. El informe fija \`loaded_pytest_plugins=NOT_INSPECTED\`, \`pytest_collection=NOT_RUN\`, \`network_os_isolation=NOT_VERIFIED\` y \`external_file_effects=NOT_VERIFIED\`. Una lista de plugins instalados es una decisión de P4 informada, no un cierre de P4. No se ha demostrado bloqueo del egress por firewall SO ni ausencia de hooks/imports con efectos.

### 20.2 Comparación opcional P6 cuando A-06 autorice un subconjunto controlado

El mismo ejecutor acepta \`-CaptureProtectedPaths\` **solo junto a un modo focal de tests ya existente y autorizado**, no junto a \`-PreflightA06\`. Antes y después de esa ejecución genera \`protected_before.tsv\` y \`protected_after.tsv\`; si difieren los SHA-256 de los inventarios, el proceso devuelve exit **5**. Incluye archivos ignorados bajo los tres subárboles técnicos protegidos. **No comparar ese inventario con el de otro clon ni de un SHA distinto.**

**Límites explícitos del instrumento:** los snapshots previos/posteriores no observan archivos creados y eliminados durante pytest, procesos hijos, actividades de import/plugin fuera de esas rutas o escrituras externas al clon. Para certificar *aislamiento real* de filesystem/red hay que comprobar controles del host/OS por separado. Por eso \`-CaptureProtectedPaths\` **no acredita P6 global solo porque el inventario quede igual**. Una eventual ejecución técnica extensa no se autoriza con el flag por sí solo, ni en el checkout original. El instrumento observa; no hace sandbox.

### 20.3 Gate de decisión tras leer el preflight

- **Si Pytest o \`pytest-asyncio\` no están disponibles, o el clon tiene rutas redirigidas/reparse points, el preflight bloquea el avance.** No corregirlo ocultando tests ni reescribiendo la suite.
- **Si el preflight termina correctamente**, evaluar los metadatos de plugins y decidir un **subconjunto A-06 seguro**, en el que cada test tenga I/O y provider controlados; no correr la selección global \`-m "not e2e"\` automáticamente. En el clon, usar el comando existente y más tarde la opción opcional de hashes protegidos sin convertir ausencia de diferencias en garantía OS.
- **A05-P4/P6 permanecen formalmente abiertos**, pues requieren evidencia real de imports/plugins seleccionados y seguridad del entorno de la corrida más amplia. Preparación técnica suficiente para *proponer* A-06 focal controlada, **no** aprobación de A-06 global.
- **Sin resultados nuevos de tests, Pyright o CI en esta modificación.** \`main\`, runtime, \`ci.yml\`, corpus científico, GT y la eliminación deliberada del PDF local quedan intocados.

## 21. A05-P4 — corrección del preflight PowerShell 5.1 (2026-11-16)

**Fallo real reportado por el owner:** al ejecutar \`-PreflightA06\` desde Windows PowerShell 5.1 sobre SHA \`26eb668420f947670f5dd38f3fb3a0d5cf0a6e9b\`, el clon independiente se creó y se fijó al SHA, pero el paso \`python -I -B -c $pluginProbe\` falló con **\`File "<string>", line 1\`** (error de sintaxis por comillas dentro del argumento de un comando nativo). PowerShell señaló la línea 140 del runner. **No se ejecutaron pytest, tests, ni importaciones de plugins**. No se recibió \`preflight_summary.txt\` de esa corrida: **no contar el preflight como PASS**. Clon previo retenido por política; no limpiar a ciegas.

**Corrección mínima, en el mismo ejecutor:** sustituir únicamente el argumento \`python -c\` con comillas anidadas por un **here-string de PowerShell enviado como texto literal a \`python -I -B -\` por stdin**, manteniendo exactamente el propósito: \`importlib.metadata\` enumera pytest, pytest-asyncio y entrypoints \`pytest11\` sin importarlos. Sin nuevo script, sin modificar el clon del owner, tests, runtime, CI, corpus o Ground Truth.

**Validación disponible:** el mismo cuerpo Python se ejecutó correctamente con \`python -I -B -\` en entorno Linux de revisión y listó versiones/entrypoints. **Eso no constituye validación en Windows PowerShell 5.1 ni ejecución del preflight completo**. El owner debe repetir solamente el preflight del nuevo SHA; P4/P6 siguen abiertos.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 \`
  -RepoRoot (Get-Location).Path \`
  -PreflightA06
\`\`\`

Si termina con éxito, conservar \`preflight_summary.txt\`, \`plugin_entrypoints.txt\`, \`protected_before.tsv\`, \`git_before.txt\` y \`git_after.txt\`. **No repetir los once tests focales ni iniciar A-06 global por esta corrección de quoting.**

## 22. A05-P4/P6 — preflight del owner verificado y colección A-06 preparada (2026-11-16)

**Adjunto inspeccionado directamente:** \`reports.rar\` (RAR5, cinco archivos). \`preflight_summary.txt\` registra \`source_sha=c5277184de665f0aab416405cf31c3282c1243df\`, \`mode=A06_PREFLIGHT_METADATA_ONLY\`, \`pytest_bodies=NOT_RUN\`, \`pytest_collection=NOT_RUN\`, \`loaded_pytest_plugins=NOT_INSPECTED\`, \`network_os_isolation=NOT_VERIFIED\` y \`external_file_effects=NOT_VERIFIED\`. \`git_before.txt\` y \`git_after.txt\` tienen **0 bytes**. Preflight **completado sin repetir el error de PowerShell**, pero **no** es una ejecución de pytest.

\`plugin_entrypoints.txt\` contiene **pytest 9.0.3**, **pytest-asyncio 1.5.0**, y cinco entrypoints anunciados: \`anyio\`, \`asyncio\`, \`faker\`, \`hypothesispytest\` y \`pytest_cov\`. Son **plugins instalados**, no evidencia de carga efectiva. \`protected_before.tsv\` presenta **30 rutas únicas**, todas con tamaño y SHA-256: **12** bajo \`tests/fixtures\`, **18** bajo \`infra/db\`, **0** bajo \`tests/golden\`; no hay archivos \`.db\` persistentes ni sidecars WAL/SHM en ese snapshot. Esta es la **línea base estática de ese clon/SHA**, no un inventario comparable a otro clon ni prueba de ausencia de I/O transitorio.

**Decisión:** P4 y P6 cuentan con preparación y preflight concretos; permanecen **PARCIALES** hasta observar carga real de pytest y diferencias antes/después de una operación controlada. El resultado **habilita únicamente una fase A-06 de colección sin cuerpos**, no \`pytest -m "not e2e"\` ni el cierre de A-05.

### 22.1 Instrumento de colección existente endurecido sin otro script

Se reutilizó \`collect_a01_isolated.py\` con \`--collect\`, que ya hace clon independiente sin hardlinks, checkout detached, elimina remoto, separa \`HOME/TEMP\`, retira credenciales y aplica guard Python de socket **best-effort** (no firewall/aislamiento OS). Ahora, **solo cuando se solicita \`--collect\`**:

- Fija \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=0\` en el proceso pytest.
- Registra plugins efectivamente cargados en los logs mediante \`pytest --trace-config\`; **no desactiva arbitrariamente \`pytest-asyncio\`**.
- Guarda \`protected_before.json\` y \`protected_after.json\` con SHA-256 y tamaños de archivos bajo \`tests/fixtures\`, \`tests/golden\` e \`infra/db\` (incluidos ignorados y comprobación contra symlinks en el árbol observado).
- Guarda \`git_before.txt\` y \`git_after.txt\` (\`--ignored\` incluido). El \`manifest.json\` registra \`protected_file_changes\`, \`git_status_before_equals_after\`, cuatro selectores de colección y el SHA. Si hay cambios persistentes o error de colección, informa **FAIL**, no un falso verde.

**No se modificaron tests, runtime, CI, corpus ni Ground Truth** y **no se ha ejecutado esta nueva colección** en el entorno del owner.

\`\`\`powershell
git pull --ff-only origin tests_stabilization

python -B docs/architecture/adr/tests_stabilization/collect_a01_isolated.py --collect
\`\`\`

**Leer antes de ejecutar:** \`--collect\` sí importa tests, decoradores, conftests y plugins aunque no corre los cuerpos de tests. Solo ejecutar si se acepta **ese** alcance en clon descartable: el guard de Python y el clon **no bloquean físicamente procesos hijos/egress a nivel SO**. Ante cualquier error, conservar el clon/reportes y **no** ejecutar \`pytest\` directamente en el working tree.

**Evidencia solicitada para el gate siguiente:** \`manifest.json\`, cuatro logs \`all.log\`, \`unit.log\`, \`integration_nonregression.log\`, \`technical.log\`, \`protected_before.json\`, \`protected_after.json\`, \`git_before.txt\`, \`git_after.txt\` (y opcionalmente los JSON de colección). Con ello se decide si P4/P6 están suficientemente controlados para **un subconjunto A-06**, sin inferir que una suite completa sea segura ni declarar CI verde.

## 23. A06-COLLECT — colección con caché Hypothesis detectada y remediación mínima (owner, 2026-11-16)

**Evidencia primaria:** el owner ejecutó \`collect_a01_isolated.py --collect\` sobre \`cffc57f270cbb1bd5ca4fa4d1955518b72a003e5\` y adjuntó \`reports.rar\` RAR5 (14 miembros), leídos directamente: \`manifest.json\`, cuatro \`*.log\`, cuatro \`*.json\` de colección, \`protected_before.json\`, \`protected_after.json\`, \`git_before.txt\`, \`git_after.txt\`, \`static_signals.json\`. **No se ejecutaron cuerpos de tests.**

| Señal | Resultado comprobado | Dictamen honesto |
|---|---|---|
| Cuatro colecciones pytest | \`all=1478\`, \`unit=225\`, \`integration_nonregression=72\`, \`technical=1458\`, **exit 0 × 4** | **Colección ejecutada sin error**, 1.478 IDs únicos; **no PASS de tests** |
| Scanner de fuente | 188 archivos Python, 388 llamadas estáticas, 0 errores AST | Dato de scanner, **no** lista exhaustiva de efectos reales |
| Protectores de tests | **30 archivos pre / 30 post**, \`protected_file_changes=[]\` (12 \`tests/fixtures\`, 18 \`infra/db\`, 0 \`tests/golden\`) | **No se modificó contenido persistente protegido** durante la colección |
| Git del clon | \`git_before.txt\` vacío, \`git_after.txt\` con **271 líneas \`!!\`**, todas bajo **\`.hypothesis/\`**: 270 constantes + \`.gitignore\` | **Side effect real, creado durante import/collect**, con artefactos ignorados; el gate **FAIL correctamente** |
| Plugins realmente cargados | \`--trace-config\` registra \`anyio\`, \`faker\`, \`_hypothesis_pytestplugin\`, \`pytest_asyncio\`, \`pytest_cov\`, el plugin observacional y \`tests/smoke/conftest.py\` | **P4: carga observada**, distinta del catálogo de entrypoints anunciado en el preflight |
| Warnings | dos mensajes: \`google.api_core\` sobre futuro fin de soporte de Python 3.11 y \`google.generativeai\` deprecated | Son avisos de dependencia; no errores de colección ni autorización para migrar SDK |

**Causa:** al cargar tests/plugins Hypothesis crea \`.hypothesis/constants/\` en el CWD del clon. La salida ignorada no está dentro de los tres árboles de inputs protegidos, pero **viola la política de no dejar artefactos en el checkout**. No imputar el FAIL a cambios de golden, a corrupción de SQLite o a un defecto probado del traductor.

**Cambio focal aplicado en el recolector existente:** \`child_environment()\` fija \`HYPOTHESIS_STORAGE_DIRECTORY\` a \`scratch/hypothesis\` **fuera del clon** y registra ese destino en el manifiesto. No se suprimió el gate, no se ocultaron entradas \`!!\` de Git, no se eliminó la caché ni se hizo \`git clean\`. Se conserva el guard de sockets Python best-effort y el opt-in Groq en 0. **No se han repetido aún las colecciones con esta corrección:** el gate A06-collect sigue **FAIL** en el SHA anterior y **PENDIENTE DE REVALIDACIÓN** en el nuevo SHA.

**Repetición mínima necesaria:** una sola \`python -B docs/architecture/adr/tests_stabilization/collect_a01_isolated.py --collect\` tras \`git pull --ff-only origin tests_stabilization\`, sobre un clon nuevo, sin ejecutar cuerpos de tests. Revisar \`manifest.json\`, los cuatro logs, \`git_before.txt\`, \`git_after.txt\` y \`protected_before/after.json\`. Si la variable de almacenamiento no surte efecto o algún otro import crea archivos, conservar el fallo sin autorizar la suite amplia. **Clones previos retenidos, sin limpieza destructiva ni efecto sobre el PDF eliminado intencionalmente en el working tree original.**

**Límites restantes:** que Git y hashes del clon estén limpios después de la colección **no demuestra ausencia de I/O transitorio, accesos externos ni aislamiento OS de red**. A05-P4/P6 siguen PARCIALES y A-06 ejecución de cuerpos sigue PENDIENTE. No se editó producción, CI, tests, corpus ni Ground Truth.

## 24. A-06 — colección revalidada y primera cohorte W08/G3 preparada (2026-11-16)

**Evidencia primaria del owner:** \`reports.rar\` RAR5 con **cinco archivos**, leídos directamente: \`manifest.json\`, \`protected_before.json\`, \`protected_after.json\`, \`git_before.txt\`, \`git_after.txt\`. El manifiesto fija \`revision_sha=d754a56c19810f39e29e6ec485e948039b1ec686\`, cuatro selectores con **exit 0** (\`all=1478\`, \`unit=225\`, \`integration_nonregression=72\`, \`technical=1458\`), \`protected_file_changes=[]\` y \`git_status_before_equals_after=true\`. Los dos inventarios protegidos son **idénticos**: 30 archivos (12 \`tests/fixtures\`, 18 \`infra/db\`, 0 \`tests/golden\`). Ambos inventarios Git tienen **0 bytes**. \`hypothesis_cache_redirect\` confirma la configuración bajo \`scratch/hypothesis\`, fuera del clon.

**Veredicto de A06-COLLECT:** **PASS** de colección y ausencia de diferencias persistentes en el clon durante esta operación **sin cuerpos de tests**. El primer intento en SHA \`cffc57f\` seguía siendo **FAIL** por 271 \`.hypothesis/\` ignorados; la mitigación del SHA \`d754a56c\` fue revalidada. El RAR final **no incluye los cuatro logs**, por lo que la observación sobre plugins realmente cargados procede de la evidencia previa del intento \`cffc57f\`, **no** de una inspección directa de logs del SHA \`d754a56c\`. No afirmar que ese SHA de revalidación probó ausencia de egress, I/O transitorio, CI verde ni ejecución del SUT.

### 24.1 Primer subconjunto ejecutable de A-06 — selección nueva, no redundante

Se reabrió el código fuente en \`tests_stabilization\` de dos archivos unitarios **no incluidos en las once pruebas focales A-05**:

- \`tests/unit/test_w08_inference_identity_contract.py\`: SUT real \`ContextSnapshotV1\` e \`InferenceReuseIdentityV1\`, hashes sensibles a estructura/generación, reserialización y errores contractuales; \`pytest.mark.unit\`, datos puros, **sin SQLite, archivos físicos ni cliente LLM**. Parametrizaciones de marco inválido (4) y dimensión de identidad (11) deben conservarse.
- \`tests/unit/test_w08_g3_cache_barrier.py\`: \`engine._create_chunk_processor\` y \`build_provider_stack\` reales en la frontera de composición, con \`monkeypatch\` y provider sintético que falla si se invoca \`translate\`; comprueba \`cache_db_path=None\` y conservación de wrapper circuit-breaker. **No acredita caché versionada completa, replay, proveedor real ni G3→G5 E2E**.

Se añadió **solo un selector opt-in** \`-CheckA06W08\` al ejecutor Git aislado ya existente \`run_b05_focal_isolated.ps1\`. El selector de esos dos archivos no se combina con otras selecciones o mutaciones. El runner limpia credenciales de proceso, fija \`TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=0\` y redirige \`HYPOTHESIS_STORAGE_DIRECTORY\` fuera del clon. Debe ejecutarse **con** \`-CaptureProtectedPaths\` para comparar hashes pre/post de inputs técnicos. El gate Git final usa el mismo exit 4 que A-05 cuando detecta artefactos persistentes; si los hashes protegidos difieren, sale con exit 5. **No se ejecutó aún esta cohorte; ningún PASS nuevo queda acreditado.**

\`\`\`powershell
git pull --ff-only origin tests_stabilization

& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 \`
  -RepoRoot (Get-Location).Path \`
  -CheckA06W08 \`
  -CaptureProtectedPaths
\`\`\`

**Evidencia a compartir:** \`summary.txt\`, \`pytest_focal.log\`, \`status_changes.txt\`, \`protected_before.tsv\`, \`protected_after.tsv\`, \`protected_changes.txt\`, \`git_before.txt\`, \`git_after.txt\`. Registrar el número real **PASS/FAIL/SKIP** (incluidas las parametrizaciones); no extrapolar al conjunto de 225 tests marcados unitarios ni a los 1.458 técnicos. Si la prueba genera otro tipo de artefactos, mantener el fallo e inspeccionar el clon retenido. **No ejecutar la suite amplia en el checkout original**, ni tocar el PDF eliminado deliberadamente.

**Estado:** A05-P4/P6 **mitigados para las operaciones focales realizadas**, no certificados globalmente; A06-COLLECT **cerrado para el SHA probado** y **baseline A-06 de tests aún pendiente**. No se ha modificado runtime, CI, corpus, GT ni tests para preparar esta cohorte.
