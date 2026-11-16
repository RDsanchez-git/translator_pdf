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
