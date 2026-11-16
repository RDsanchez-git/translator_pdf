# A-01/A-04 — Reconciliación de nodeids tras remediaciones B (2026-11-16)

> **Estado:** CONCILIACIÓN DE COLECCIÓN ACREDITADA POR REPORTES DEL OWNER; **A-01/A-04 globales ABIERTOS**.
> **Modo:** \`pytest --collect-only\` en clon Git independiente, sin ejecutar cuerpos de tests.
> **Fuente primaria:** salida completa de \`collect_a01_isolated.py\`, \`reconcile_a01_head_collection.py\` y contenido íntegro de \`a01_head_reconciliation.json\` compartidos en conversación por el owner.
> **Histórico:** \`86cd68672ee692f073b62869e7c9bd177e8d9e3b\`.
> **HEAD recolectado:** \`5447963d1c2dbce257d94aede30baabb11bd9f98\` (\`tests_stabilization\`).
> **No acredita:** pytest PASS de suite, ejecución CI, hermeticidad OS, semántica de todos los oráculos ni pipeline PDF→PDF/ciencia.

## 1. Salida directa de colección del HEAD

El owner ejecutó \`collect_a01_isolated.py --repo-root . --collect\`, que crea una copia independiente sin hardlinks, fija el SHA de Git, y recolecta cuatro selectores. Reportes conservados en:
\`%LOCALAPPDATA%/Temp/translator-a01-isolated-pkzq47ks/reports\` (ruta de evidencia del owner, **no** fixture del proyecto).

| Recolección | SHA histórico | SHA actual | Exit actual |
|---|---:|---:|---:|
| \`all\` | 1.474 | **1.476** | 0 |
| \`unit\` | 225 | **225** | 0 |
| \`integration and not regression\` | 70 | **72** | 0 |
| \`not e2e\` | 1.454 | **1.456** | 0 |

Scanner estático del HEAD: **188 archivos \`tests/*.py\`**, 388 señales de llamadas AST, **0 errores de parsing**. Las señales AST no son efectos observados, y el conteo no implica más/menos seguridad que el censo anterior. No se ejecutaron cuerpos de test.

## 2. Reconciliación de identidades y markers

El comparador \`reconcile_a01_head_collection.py\` validó SHA, integridad de los cuatro JSON/manifest, ausencia de nodeids duplicados, igualdad de selectores según markers y ancestro Git. Resultado reportado:

| Identidades | Resultado |
|---|---:|
| Compartidas \`old ∩ new\` | **1.460** |
| Bajas \`old − new\` | **14** |
| Altas \`new − old\` | **16** |
| Diferencia neta | **+2** |
| Cambios de markers en nodeids **idénticos** | **0** |
| Cambios de \`parameter_id\` en nodeids **idénticos** | **0** |

El número de nodeids parametrizados permanece **187**. Los marcados \`unit=225\`, \`e2e=20\` y \`skipif=1\` no cambiaron; \`integration\` pasó de **70 a 72**. Los casos sin marker de nivel siguen siendo **1.159**; los archivos con nodos siguen siendo **173**. \`regression=0\`, \`smoke=0\`, \`skip=0\`, \`xfail=0\` son contadores de **marcas declaradas**, no estados de ejecución.

**Importante:** \`marker_changes_same_nodeid=0\` solo compara identidades sobrevivientes; no significa que los 16 casos nuevos tengan los mismos markers que sus predecesores.

## 3. Ocho archivos implicados: correspondencia de bajas y altas

| Archivo | Bajas | Altas | Causa sustentada por remediaciones | Alcance |
|---|---:|---:|---|---|
| \`test_chunker_snapshot.py\` | 1 | **3** | B-02: único test de snapshot autoescribible reemplazado por contrato de bytes/identidad/política y **dos rechazos negativos** del manifiesto | **Único +2 neto** |
| \`test_e2e_walking_skeleton.py\` | 1 | 1 | B05-R2: dispatcher/caché legacy real, no E2E; DB temporal y oráculos observables | Reemplazo de alcance/nombre |
| \`test_golden_parser.py\` | 1 | 1 | B-01: parser real en PDF sintético, sin oráculo circular | Reemplazo de SUT/oráculo |
| \`test_healing_e2e_telemetry.py\` | 5 | 5 | B-04: nombres \`test_e2e_*\` pasan a \`test_healing_*\` con las aserciones conservadas | Cambio de nombres |
| \`test_pipeline_orchestration.py\` | 1 | 1 | B05-R3: orquestación legacy con parser simulado, sin PDF físico E2E | Reclasificación |
| \`test_real_e2e.py\` | 1 | 1 | B05-R3: consumidor FinOps con \`execute\` mockeado, sin afirmación E2E | Reclasificación |
| \`test_real_parser_pipeline.py\` | 1 | 1 | B-03: parser físico de dos páginas temporales en vez de parser mockeado | Reemplazo de SUT |
| \`tests/test_pipeline_fidelity.py\` | 3 | 3 | B-04: \`TestPipelineFidelity\` pasa a \`TestMathProtectionContracts\`, sin mutación global del import path | Reclasificación |
| **TOTAL** | **14** | **16** | **Cambio neto +2 íntegramente localizado** | Identidades antiguas no reutilizadas indebidamente |

Una baja/alta del mismo archivo es un cambio de identidad observado, **no por sí sola prueba de equivalencia semántica**. Esta tabla interpreta las remediaciones ya realizadas, sus fuentes y los nodeids comunicados por el owner. Los viejos \`TR-###\` y las bases históricas no se reescriben como si describieran el HEAD nuevo.

## 4. Selección CI que sí se puede afirmar por fuente

La inspección del workflow \`.github/workflows/ci.yml\` y el JSON confirma los selectores fuente:

- \`-m "unit"\`: **225** seleccionables.
- \`-m "integration and not regression"\`: **72** seleccionables.
- \`-m "not e2e"\`: **1.456** seleccionables.

**12/12 rutas expresas de G3/G5/W06/W08** siguen siendo recolectadas, **138 nodeids en total**, los mismos por archivo en ambos inventarios. Son conteos de selección; no acreditan que el CI los haya ejecutado ni aprobado. El workflow de required checks escucha push de \`main\`/\`develop\` y PR hacia \`main\`/\`pipeline_stabilization\`; **un push directo a \`tests_stabilization\` no desencadena ese CI por sí solo**.

El detector de nombre devuelve **6 \`e2e_named_but_unmarked_candidates\`**: uno de \`test_e2e_walking_skeleton.py\` (caché legacy) y cinco de \`test_healing_e2e_telemetry.py\` (healing). **El patrón coincide por el nombre del archivo**, pese a que funciones y docstrings ya declaran correctamente su alcance técnico. No tratar estos seis como E2E reales ocultos ni retitular archivos por estética sin evidencia de riesgo.

**Contexto:** los **20** \`e2e\` marcados siguen excluidos de \`not e2e\`. La pertenencia a este selector no verifica que un caso sea bueno/seguro. Los tests del workflow técnico que utilizan rutas concretas pueden ejecutarse además de la suite global; no sumar ambas selecciones como casos únicos ejecutados.

## 5. Gates pendientes y continuidad

- [x] **A01-RC-HEAD:** recolección actual de cuatro selectores sin errores, 1.476 nodeids; reconciliación completa 1.460/14/16, 0 cambios de marker/parameter entre nodeids compartidos.
- [x] **A04-SELECTORES:** cuatro conjuntos reconciliados por JSON y 12/12 paths CI estables por selección de fuente.
- [ ] **A-01 global:** terminar fichas SUT/oráculo para nodos aún no cubiertos y contrastar contratos/casos de riesgo.
- [ ] **A-04 global:** matriz de reclasificación semántica del HEAD y relación con protección efectiva, no solo renombres.
- [ ] **A-05/A-06 global:** no hay inventario post-colección del clon de este SHA aportado aquí, ni prueba de side effects transitorios/host o egress físico.
- [ ] **B/C general:** remediaciones y falsadores focales previos no equivalen a cobertura de toda la suite.
- [ ] **CI del HEAD:** no se inspeccionó ni obtuvo un run exitoso de GitHub Actions con esta revisión.
- [ ] **D-4/D-5:** pipeline físico completo y ciencia/corpus/GT permanecen expresamente diferidos.

**Siguiente actividad recomendada:** continuar A-03/A-04 con los tests todavía semánticamente no inspeccionados que sí entran a \`not e2e\` o son paths explícitos de CI. Priorizar falsos PASS, skip silencioso y side effects persistentes sobre cambios de naming. Sólo proponer PR/merge/CI si el owner lo autoriza; no correr \`pytest -m "not e2e"\` en el checkout del owner sin resolver el gate A-05.
