# Plan de estabilización y remediación de los tests del pipeline PDF→PDF

> **Código del programa:** TST-STAB  
> **Versión:** 0.1.1 — A-00 documentado y cerrado por evidencia estática; resto de tareas pendiente  
> **Estado:** EN EJECUCIÓN — **A-00 cerrado** como inventario estático; **A-01 a A-07, B y C pendientes**. No se han remediado tests ni modificado runtime.  
> **Fecha de apertura:** 2026-11-15  
> **Repositorio:** `RDsanchez-git/translator_pdf`  
> **Rama de trabajo:** `tests_stabilization` (derivada de `main` @ `83ef0257f795f0d973f9393cc225e7af5b956ade`)  
> **Ubicación:** `docs/architecture/adr/tests_stabilization/PLAN_REMEDIACION_TESTS_PIPELINE.md`  
> **Objeto de control:** calidad y poder de detección de los **tests técnicos** que pretenden proteger el pipeline PDF→PDF y sus contratos observables.  
> **Aprobación de cierre:** maintainer/owner, con evidencia reproducible y PR revisado.  
> **Relación con ADRs previos:** documento **operativo, no normativo**; no sustituye ni altera ADR/NADR FROZEN, sus oráculos ni los reportes históricos.

---

## 0. Resumen ejecutivo y decisión de alcance

### 0.1 Problema

La ruta operativa única PDF→PDF existe y cuenta con testigos técnicos de laboratorio, pero el inventario conserva pruebas heredadas que pueden producir una señal verde engañosa. Los ADRs de Fase 17-BIS describieron pruebas tautológicas, autogeneración de referencias de comparación, mocks que reemplazan la función supuestamente evaluada y aserciones parciales. La inspección estática de `main` en la fecha de apertura **confirma todavía algunos de esos patrones**.

La auditoría temporal de Pyright local terminó con **0 errores en 188 archivos** y los PR #55–#61 sanearon el tipado de tests. Eso **no** demuestra que todos los tests estén bien formulados, detecten una regresión o cubran la ejecución que afirman cubrir.

### 0.2 Decisión del owner

Se aprueban **tres etapas activas, en este orden**:

1. **Auditar semánticamente** cada prueba pertinente a la ruta PDF→PDF y su relación con los contratos reales.
2. **Remediar falsas garantías comprobadas**, priorizando pruebas tautológicas, snapshots autojustificados, nombres E2E engañosos, skips silenciosos y fixtures peligrosas.
3. **Demostrar sensibilidad mediante controles negativos**: la prueba debe distinguir un comportamiento conforme de una violación relevante de su contrato.

Se difieren expresamente **hasta después del refinamiento del pipeline**:

- **D-4 — Consolidación/reejecución integral de la ruta operativa única.** No repetir ahora la campaña C0–C4, la acreditación de laboratorio ni un nuevo E2E global; reutilizar su documentación únicamente como **mapa de contratos y alcance** durante la auditoría.
- **D-5 — Evaluación científica, corpus canónico, Ground Truth y re-baseline.** No curar, re-sellar, regenerar, recalibrar ni cambiar oráculos, umbrales, estado del CV científico o tests científicos para hacerlos pasar. Las limitaciones actuales son conocidas y deliberadamente se atienden **después** de afinar el pipeline.

La salida de esta campaña **no es** `PRODUCT_READINESS=PASS` ni certificación de fidelidad científica.

### 0.3 Orden y condiciones de avance

`Auditoría (A) → Remediación (B) → Controles negativos (C) → Gate de cierre técnico → Refinamiento del pipeline (trabajo posterior) → D-4/D-5 (campañas posteriores).`

No se comienza B indiscriminadamente antes de conocer el contrato y el estatus de cada test; no se declara C aprobado si los tests conformes pasan pero **también** aceptarían entradas incorrectas. Las excepciones para reparar un riesgo inmediato de escritura accidental se registran como mitigación de seguridad, no como cierre de la auditoría.

---

## 1. Guía para quien llega por primera vez

**Pipeline PDF→PDF:** cadena que recibe un PDF, extrae y construye AST, prepara planes/contexto, procesa tareas mediante OCR/G3, materializa proyecciones y ensambla/publica el PDF mediante G5, bajo controles de FSM, SQLite, hashes, fencing y recuperación. Sus detalles de proceso se describen en el [Atlas de la ruta operativa única](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md); este plan **no rediseña** esa ruta.

**Test de contrato:** prueba que comprueba una propiedad visible del sistema que sus consumidores pueden exigir. No debe depender de una función privada, un orden accidental de llamadas, un layout interno de clases ni un nombre de implementación, salvo que ese detalle sea parte del contrato publicado y esté documentado.

**SUT (Subject Under Test):** comportamiento real que la prueba afirma comprobar. La prueba debe alcanzarlo de verdad.

**Oráculo de test:** referencia o propiedad que decide PASS/FAIL. Debe ser independiente del resultado medido; `actual == actual` nunca acredita corrección.

**Fixture:** dato preparado para ejecutar una prueba. Una fixture técnica determinista puede ser sintética y descartable. **No equivale** al Ground Truth científico sellado.

**Fake / stub / mock:** sustituto controlado de una dependencia. Un fake externo (por ejemplo, proveedor LLM sin red) es legítimo si el SUT real está aguas adentro. Mockear el propio SUT cambia el alcance: entonces se está probando al consumidor, no al SUT.

**Test unitario / integración / proceso / laboratorio:** niveles distintos de alcance y coste. Su nombre y `pytest marker` deben reflejar aquello que realmente ejecutan. “E2E” implica atravesar las fronteras pertinentes, no llamar a un método que devuelve un `MagicMock`.

**Control negativo:** entrada, estado o fallo deliberado que viola un contrato; debe ocasionar rechazo/control específico **sin efectos secundarios prohibidos**. **Prueba de sensibilidad (mutation kill):** demostración aislada de que el test fallaría si la implementación real perdiera su barrera. Son comprobaciones relacionadas, pero no equivalentes.

**Test estable frente a refactors:** conserva su validez cuando cambian implementaciones internas sin cambiar el comportamiento prometido. **No puede ser absolutamente inmutable** si el contrato funcional legítimo cambia: en ese caso, la evolución del contrato y del test debe ser explícita, versionada y revisada, nunca un ajuste automático para recuperar “verde”.

---

## 2. Objetivo, límites y definición de éxito

### 2.1 Objetivos verificables

- **O1 — Veracidad:** cada test relevante dice qué garantiza y qué *no* garantiza; identifica el SUT real, dependencias sustituidas y oráculo.
- **O2 — Independencia:** ninguna prueba obligatoria fabrica su valor esperado desde el mismo resultado, actualiza referencias al fallar ni aprueba por ausencia de material indispensable.
- **O3 — Resistencia al refactor:** privilegiar invariantes de frontera, semántica observable, propiedades y relaciones metamórficas frente a detalles de implementación.
- **O4 — Sensibilidad:** para cada contrato crítico existe al menos una violación reproducible que los tests detectan con la razón correcta y, donde aplique, con ausencia de efectos prohibidos.
- **O5 — Hermeticidad:** ensayos técnicos no ejecutan llamadas pagas/reales a LLM, no escriben en datos de producción, no mutan corpus sellado y no alteran el estado local del owner.
- **O6 — Trazabilidad:** los hallazgos, cambios, evidencias y limitaciones tienen ID, commit, test, contrato, responsable y decisión verificables.

### 2.2 Dentro de alcance

- `tests/` técnicos y helpers/fixtures pertinentes a **OCR/admisión, extracción B02, AST, plan y contexto, G3, FSM/CQRS, recuperación W06, G5, publicación, PDF foreground y fronteras SQLite/filesystem**.
- Tests heredados que, por inclusión en CI, etiqueta/nombre o ubicación, **afirmen erróneamente** cubrir la ruta operativa actual. Se clasifican; no se eliminan por mera antigüedad.
- Configuración de selección de tests y markers **solo para auditar la evidencia y proponer correcciones de alcance**. Cualquier cambio al CI requiere revisión explícita y no se presume aprobado en este plan.
- Correcciones en código de pruebas y fixtures técnicas **sin modificar contratos productivos**. Una prueba que expone un bug del runtime genera hallazgo separado; no se “arregla” ocultándolo con un mock o moviendo el esperado.
- Instrumentación descartable de fallos (inyección, monkeypatch limitado a puertos externos, SQLite temporal, archivos temporales, procesos aislados) para medir la sensibilidad real de pruebas.

### 2.3 Fuera de alcance — prohibiciones de la campaña

- Refinar, optimizar o migrar el pipeline; sustituir proveedores; rediseñar la arquitectura; desplegar o cambiar el Compose productivo.
- Repetir como nueva acreditación los testigos C0–C4 o C2 del laboratorio. Sus hechos históricos no se trasladan automáticamente a otro SHA.
- Evaluación científica, fidelidad de traducción, validación semántica STEM, performance/FinOps real, calibración o Ground Truth; tocar `tests/corpus/canonical/` o reemplazar referencias científicas.
- Hacer required el CV científico, silenciar su fallo, alterar exit codes o cambiar umbrales para volverlo verde. La [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34) conserva el bloqueo de materialización de corpus.
- Cerrar/declarar resuelta la [issue #36](https://github.com/RDsanchez-git/translator_pdf/issues/36) por aprobar tests; la deuda de cache/replay es un asunto operativo independiente.
- Eliminar tests o archivos heredados en masa, aplicar `git reset --hard`/`git clean`, restaurar outputs PDF deliberadamente borrados, tocar la configuración Pyright oficial o reescribir documentos normativos FROZEN.
- Desplegar servicios, abrir red, pedir secretos, activar proveedores pagos o usar datos reales/sensibles sin autorización específica.

### 2.4 Contratos prioritarios (no implementaciones)

| Frontera | Propiedad observable estable | Qué **no** debe fijar un test |
|---|---|---|
| Parser/extracción B02 | PDF representable → AST no vacío, nodos válidos y linaje rastreable; dibujo vectorial no representable → rechazo explícito | Conteo/orden interno de helpers o identidad de clase concreta salvo puerto normativo |
| AST/plan/contexto | Identidad semántica y binding coherente de `document_id`, `ast_hash`, `manifest_sha256`, `node_id` y tareas; sin pérdida silenciosa | Orden casual de consultas, DTO transitorio o texto exacto del prompt sin contrato |
| G3 proveedor/efecto incierto | No reenviar bajo `EXTERNAL_UNKNOWN`; no doble efecto externo, no falsa confirmación | Numero de llamadas internas inocuas; sí pueden contarse POST externos si es el contrato |
| G3 proyecciones/publicación | Solo generación correcta y materialización CURRENT aceptadas; ningún stale write publicado | Detalles privados de filas SQL si no forman parte del contrato |
| FSM/leases/recovery | Transición permitida, fencing por dueño/versión, estado durable coherente y recuperación autorizada | Secuencia interna exacta de funciones |
| G5/PDF | Lease vencido no publica PDF; falta de proyección bloquea; salida publicable con artefacto válido y estado congruente | SHA binario exacto de PDF si el renderer admite variación legítima |
| Foreground/CLI | Errores de OCR/G3/G5 no producen `COMPLETED` o PDF falsamente exitoso; no se habilita R1/R3 | Ruta de un script auxiliar no contractual |
| Límite externo | Fake determinista y sin credenciales para el proveedor; comprobar sólo sus efectos permitidos | Calidad de traducción o costos reales a partir del fake |

Los hashes y campos de identidad **sí** pueden ser aserciones exactas cuando su algoritmo/formato sea un **contrato normativo**; la decisión debe constar en la ficha del test. La estabilidad no justifica relajar identidades, condiciones de fencing o códigos de error exigidos.

---

## 3. Estado inicial y fuentes de verdad

### 3.1 Línea base documental y técnica

- **Referencia de código al abrir el plan:** `main` @ `83ef0257f795f0d973f9393cc225e7af5b956ade`, 2026-11-15. Cada revisión posterior debe registrar su propio SHA.
- **Tipado local:** último resultado aportado por el owner, 0 errors/0 warnings/0 informations en configuración local con tests. Esta es **evidencia de tipado**, no del poder de regresión.
- **CI actual:** [`.github/workflows/ci.yml`](../../../../.github/workflows/ci.yml) ejecuta `pyright` oficial sin tests y una suite técnica que incluye `pytest -m "not e2e"`; también tiene pasos focales. Los tests no marcados `e2e` pueden entrar aunque lleven “e2e” en el nombre.
- **CI científico separado:** [`continuous-verification.yml`](../../../../.github/workflows/continuous-verification.yml), no requerido para merge durante la transición. Su estado rojo actual no puede reinterpretarse como PASS ni atribuirse a la remediación técnica.
- **Rama/CI:** `tests_stabilization` se mantiene separada de `main`. El workflow técnico actual se dispara en PR **contra main o pipeline_stabilization**, no contra `tests_stabilization`. Un PR Draft de esta rama hacia `main` sirve para obtener validación continua sin fusionar. No asumir que PRs dirigidos únicamente a la rama de trabajo tienen el mismo check automático.
- **Rutas:** el [Atlas](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) distingue ruta OCR/G3/G5 de R1 biblioteca y R3 no seleccionado. Un test de R1 puede ser válido para R1, pero **no** cubrir la ruta PDF→PDF por proximidad de nombre.
- **Regla de evidencia:** una observación estática no acredita ejecución dinámica ni ausencia de side effects; resultado local, CI, laboratorio y revisión documental se registran por separado.

### 3.2 Hallazgos semilla confirmados en código (NO equivalen a inventario exhaustivo)

| ID | Test o superficie | Evidencia observada en el SHA de apertura | Riesgo | Situación |
|---|---|---|---|---|
| `TS-001` | [`test_golden_parser.py`](../../../../tests/integration/test_golden_parser.py) | `patch.object(adapter, 'parse', ...)` sustituye el SUT; `expected_fingerprint = current_fingerprint` invalida el oráculo; falta de referencia puede hacer `skipTest`. También existe rama que fabrica PDF ficticio si no encuentra fixture. | **P0 — falsa garantía** | CONFIRMADO ESTÁTICO; pendiente decidir reparación de contrato técnico |
| `TS-002` | [`test_chunker_snapshot.py`](../../../../tests/integration/test_chunker_snapshot.py) | Si falta snapshot lo escribe desde el resultado observado y retorna; AST faltante dispara skip; aserciones seleccionan menos campos que los serializados. | **P0 — falsa garantía/side effect** | CONFIRMADO ESTÁTICO; no se afirma que la rama de autogeneración se ejecute hoy: el snapshot está versionado |
| `TS-003` | [`test_real_e2e.py`](../../../../tests/integration/test_real_e2e.py) | El test parchea `pipeline.execute()` y usa resultado simulado; puede tener valor para consumidor/FinOps, **no** para E2E de ejecución. | **P1 — sobredeclaración** | CONFIRMADO ESTÁTICO; alcance funcional por precisar |
| `TS-004` | [`test_e2e_walking_skeleton.py`](../../../../tests/integration/test_e2e_walking_skeleton.py) | Fakes de proveedor, repositorio y resumen; evalúa una secuencia parcial; no acredita por sí solo el PDF físico final. | **P1 — alcance ambiguo** | CONFIRMADO ESTÁTICO; no implica que la prueba sea inútil |
| `TS-005` | [`test_pipeline_fidelity.py`](../../../../tests/test_pipeline_fidelity.py) | Las comprobaciones de masking/restauración y enums no equivalen a fidelidad integral de traducción. | **P2 — nomenclatura/cobertura** | CONFIRMADO ESTÁTICO; no desautoriza sus invariantes unitarias |
| `TS-006` | [`test_verification_pipeline_connection.py`](../../../../tests/integration/test_verification_pipeline_connection.py) | Usa extracción real sobre PDFs técnicos sintéticos y comprueba rechazo `B02_UNREPRESENTED_VECTOR_DRAWING`. | **Control potencial reutilizable** | EVIDENCIA DE CÓDIGO; falta ensayar sensibilidad específica |
| `TS-007` | Tests de recuperación W06/G3/G5 del [Atlas `6](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) | Existen testigos con SQLite/fakes sobre publicación y fencing. | **Alta criticidad**, sin defecto atribuido | PENDIENTE DE AUDITORÍA POR CONTRATO; conservar sus oráculos hasta entenderlos |

**Regla:** P0/P1/P2 aquí es prioridad de análisis/remediación, **no** severidad demostrada de un bug de producción. Los primeros dos hallazgos están corroborados por [HITO 0.4.4](../phase-17-bis/00-foundation/HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md), [HITO 4.4](../phase-17-bis/00-foundation/HITO_4.4_TESTING_PREREQUISITES_DISCOVERY.md) y el [Exit Review de Fase 4, DF-01](../phase-17-bis/reviews/FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md). El [consolidado diferido](../phase-17-bis/reports/FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md) sigue registrando esa deuda.

**ID inequívoco:** `DF-01 (Fase 4)` = tests tautológicos; `DF-01 (Fase 6)` = import-linter/OCR provider. Jamás referir “DF-01” sin fase.

---

## 4. Norma de diseño para tests duraderos y confiables

Se aplicarán las siguientes reglas a cada test creado o remediado.

**R-01 — Contract first.** Escribir antes de implementar: sujeto real, entrada, precondición, propiedad observable, salida o excepción, y efecto prohibido. Si no se puede expresar una propiedad externa verificable, el test no se anuncia como una garantía.

**R-02 — Indiferencia a detalles internos.** Preferir APIs/puertos estables y resultados sobre llamar helpers privados, inspeccionar contadores internos, mocks de objetos profundos o comparar estructuras incidentales. Sólo fijar esos detalles cuando un ADR/NADR o un consumidor los convierte en contrato.

**R-03 — Oráculo independiente.** Constantes normativas, fixtures técnicas curadas/versionadas o propiedades/metamorfismos independientes del resultado de la misma corrida; prohibido `expected = actual`, “update snapshot if mismatch”, aprobar por `len > 0` como sustituto de semántica estructural, o escribir el expected durante el test.

**R-04 — Mocks en frontera, no en el SUT.** Simular servicios externos, relojes, red, proveedores, filesystem o errores para reproducibilidad; conservar componentes reales dentro del alcance anunciado. Si se mockea la operación central, clasificar como test del consumidor/fachada y renombrar/reubicar o diseñar un test distinto para cubrir el SUT.

**R-05 — Positive + negative.** Para contratos críticos, un test feliz no basta. Añadir caso de rechazo con código/estado correcto y oráculo de efectos laterales: ninguna escritura/publicación, ningún POST adicional, ausencia de `COMPLETED` indebido, según contrato.

**R-06 — Hermeticidad.** Preferir `tmp_path`, SQLite WAL temporal, sockets loopback controlados y fakes deterministas. No usar el workspace real ni rutas locales fijas. No escribir en `tests/fixtures/` ni `tests/corpus/canonical/` durante una ejecución; una actualización deliberada de fixture exige revisión y commit separados.

**R-07 — Fixtures y referencias.** Una fixture obligatoria ausente es un fallo indexable del test o preflight, nunca un PASS/SKIP silencioso. Las pruebas opcionales se identifican como opcionales y **no cuentan** para una barrera obligatoria. No renombrar un artefacto técnico como “Golden/GT científico” para simular certificación.

**R-08 — Aserciones completas, pero no frágiles.** Afirmar todos los campos **contractuales** pertinentes (incluidos identidad, semántica, side effects y excepciones); no exigir igualdad ciega de todos los campos de un DTO si los demás son incidentales. Cada exclusión o tolerancia requiere justificación.

**R-09 — Sensibilidad demostrada.** Cada cobertura crítica debe registrar qué defecto específico detecta. Combinar casos negativos directos con mutación controlada **del comportamiento del SUT** en una copia descartable, verificando que el test falla. Restaurar la copia; no registrar resultados de una mutación no ejecutada como PASS.

**R-10 — Reproducibilidad y evidencia.** Seeds/tiempos/relojes controlados; no retry que oculta flakiness. Toda evidencia indica SHA, SO/versión Python, selección de pytest, resultado (incluidos skipped/xfail), condiciones aisladas, control negativo y archivos/escrituras observados.

**R-11 — Separación de contratos.** Los nombres `unit/integration/e2e/regression`, los markers y descripciones deben concordar con lo ejecutado. Validación de ruta técnica ≠ fidelidad científica; control de formato ≠ calidad de traducción; fixture sintética ≠ corpus sellado.

**R-12 — Cambio legítimo de contrato.** Si el refinamiento futuro cambia una conducta garantizada por decisión explícita, versionar la decisión y actualizar el test **con revisión independiente**. Nunca ajustar el expected sólo porque el test quedó rojo; clasificar primero como regresión, cambio de contrato legítimo o fixture incorrecta.

**R-13 — Sin atajos de tipado.** Mantener la auditoría local de Pyright (producción + tests) y los checks oficiales, sin convertir errores de tipado en supuestos bugs de test ni silenciarlos masivamente con `Any`/`cast`/`ignore`. La corrección de tipos no reemplaza la revisión semántica.

**R-14 — Principio de reutilización.** Antes de crear un nuevo helper, fixture, emulador, harness o test E2E, comprobar si ya existe uno que ejerza el mismo contrato. Evitar duplicación de autoridad, de rutas de pipeline y de oráculos.

---

## 5. Método de auditoría: registro y regla de decisión

### 5.1 Unidad de análisis

La unidad primaria es **un caso de prueba** (función o parametrización material); se agrupa por archivo y contrato. Un archivo con una sola prueba tautológica no invalida necesariamente los otros casos; un nombre “integration” no prueba integración.

**Ficha obligatoria `TR-###`:**

| Campo | Contenido mínimo |
|---|---|
| ID / referencia | `TR-###`, archivo, test / parametrización, SHA de origen |
| Ruta y criticidad | OCR, B02, AST, plan, G3, W06, FSM, G5, PDF, legacy; P0/P1/P2 justificada |
| Contrato | frase estable de comportamiento externo; fuente normativa o código consumidor |
| SUT y ejecución | punto de entrada, símbolo real invocado, recorrido hasta oráculo |
| Doubles | qué se sustituye, motivo, frontera, lo que **no** se está probando |
| Fixture / I/O | origen, si está versionada, tmp, SQLite, red, coste, escrituras posibles |
| Oráculo positivo | propiedades exactas y tolerancias justificadas |
| Control negativo | fallo inyectable, error/estado esperado, side effects prohibidos |
| Sensibilidad | evidencia `MUTATION_KILLED`, `NOT_KILLED` o `NOT_RUN`; método y log |
| CI / markers | ¿se selecciona realmente en CI? ¿PASS/FAIL/SKIP/XFAIL? |
| Clasificación | CONFIABLE_PARA_SU_ALCANCE / LIMITADO / DEFECTUOSO / DESCONOCIDO |
| Decisión / trazabilidad | RETENER / ENDURECER / DIVIDIR / RENOMBRAR / AISLAR / REEMPLAZAR (con justificación), PR y responsable |

### 5.2 Criterios de clasificación

- **CONFIABLE_PARA_SU_ALCANCE:** ejecuta el SUT declarado, compara con oráculo independiente, el scope está bien anunciado y cuenta con prueba de sensibilidad apropiada; no acredita comportamientos fuera de ese scope.
- **LIMITADO:** prueba legítima pero parcial, con mocks declarados, aserciones o sensibilidad insuficientes; **no** usar su PASS como garantía de una frontera más amplia.
- **DEFECTUOSO:** tautología, resultado autoaprobado, SUT sustituido presentado como SUT real, test que escribe su propia referencia, o FAIL real ocultado mediante skip/retorno.
- **DESCONOCIDO:** faltan lectura/evidencia suficientes. **No** inventar que está bien o mal.

Cada cambio de estado debe tener una referencia (PR, commit, informe local o resultado controlado). Una revisión estática puede confirmar una tautología, pero **no** demostrar que un test se ejecutó dinámicamente.

### 5.3 Prioridad

1. P0: falsas garantías ejecutadas o reportadas como barreras de regresión; corrupción/autogeneración de fixtures; falsa publicación, duplicación de efectos externos, fencing o falso éxito.
2. P1: tests relevantes que prueban otra operación, mocks demasiado profundos, skips que esconden cobertura o nombres E2E que inducen a error.
3. P2: nomenclatura, parametrizaciones redundantes y mejoras de ergonomía; no refactorizar por estética mientras subsista P0.

**Regla de cobertura:** primero barreras críticas del **camino realmente seleccionado**; después pruebas históricas con riesgo de contaminar CI. Las pruebas de R1/R3 sólo se retienen si su propósito histórico queda correctamente delimitado.

---

## 6. Hoja de ruta ejecutable (checkboxes de progreso)

**Convención de seguimiento:** `[ ]` pendiente, `[x]` cerrado con evidencia. No usar `[x]` por crear una rama, escribir un documento o recibir un CI verde. Cada tarea cerrada debe añadir en la tabla de `6.4` el SHA/PR y evidencia. No se alteran fechas de reportes históricos FROZEN.

### Etapa A — Auditoría semántica de tests (**PRIMERA**, sólo diagnóstico salvo mitigación urgente)

- [x] **A-00 — Congelar sujeto auditado.** Baseline y HEAD de observación, censo completo de **177 módulos candidatos** en **188 archivos Python de `tests/`**, workflows/selección CI, fixtures, outputs versionados y riesgos de escritura, con separación explícita de R1/R3/benchmarks frente a OCR/G3/G5. **Evidencia:** [A00_BASELINE_INVENTARIO_Y_RIESGOS.md](A00_BASELINE_INVENTARIO_Y_RIESGOS.md); **sólo auditoría estática**, no Pytest/collect-only ni validación semántica.
- [ ] **A-01 — Inventario semántico (EN CURSO).** Censo estático **177/177 módulos y 1.341 declaraciones** documentado; **colección real ya realizada** en clon independiente a SHA `86cd6867`, con **1.474 nodos all, 225 unit, 70 integration_nonregression, 1.454 not e2e** y cuatro exit codes 0. [Resultado y conciliación pendiente](A01_COLECCION_PYTEST_2026-11-15.md). Quedan por verificar `nodeid`, param IDs, marcadores/skip/xfail, selección CI por rutas y trazabilidad SUT/contrato; **mantener [ ]**.
- [ ] **A-02 — Trazar contratos a tests.** Para cada frontera del `2.4`, registrar cobertura positiva, negativa, evidencia independiente y huecos. Referenciar Atlas, contratos/normas aplicables y consumidor de puerto.
- [ ] **A-03 — Evaluar independencia de oráculos y mocks.** Inspeccionar `patch`/`monkeypatch`, expected dinámicos, snapshots, assertions débiles, `skip`, `xfail`, escrituras a fixtures, infraestructura real vs fake.
- [ ] **A-04 — Completar fichas `TR-###` y clasificaciones.** Etiquetar cada test pertinente; registrar `UNKNOWN` donde no se haya podido comprobar comportamiento. No proyectar hallazgos históricos automáticamente sobre código nuevo.
- [ ] **A-05 — Seguridad de ejecución (EN CURSO).** Riesgos A-00 documentados y [colección real en clon separado](A01_COLECCION_PYTEST_2026-11-15.md) completada sin errores de pytest; **no** se ejecutaron cuerpos de pruebas. Continúa pendiente revisar logs, markers, efectos sobre clon/working tree, egress y seguridad de imports/plugins; el clon no constituye aislamiento OS. [Preflight y seguimiento](A05_PREFLIGHT_A01_COLECCION_AISLADA.md). **Mantener [ ]**.
- [ ] **A-06 — Ejecutar baseline técnico controlado.** `pytest --collect-only`, tests focales seguros, Pyright local y CI técnico; registrar PASS/FAIL/SKIP/XFAIL y qué rutas recorrieron, sin claims E2E implícitos. Una ejecución sólo cuenta si el entorno es conocido y no modifica fixtures.
- [ ] **A-07 — Publicar matriz de brechas priorizada.** P0/P1/P2, defectos confirmados frente a hipótesis, dependencias, propuesta de remediación y criterio para falsar la garantía; revisión del owner antes de B.

**Gate A (para pasar a B):** inventario y matriz revisables, riesgo de side effects controlado, P0 definidos con pruebas de evidencia, cobertura de CI auditada. El número de tests pendientes se informa, no se maquilla.

### Etapa B — Remediar falsas garantías (**SEGUNDA**, cambios focales)

- [ ] **B-01 — `TS-001` Golden parser.** Quitar `expected_fingerprint = current_fingerprint`, mock del propio parser, fabricación de PDF en `tests/fixtures` y skip de un oráculo requerido. **Antes de reescribir**, determinar si ese caso es ruta técnica activa o regresión científica histórica. Si el baseline científico no está permitido ahora, sustituir su *afirmación* por un test **técnico** del parser real con PDF sintético descartable y propiedades contractuales independientes, y aislar/renombrar la garantía científica diferida. No generar ni retocar GT canónico.
- [ ] **B-02 — `TS-002` Snapshot de chunking.** Eliminar autogeneración durante pytest y cualquier éxito por ausencia de referencia obligatoria; exigir fixture técnica preexistente o cambiar a propiedades contractuales si el snapshot fija detalles incidentales. Justificar los campos verificados y añadir un caso de missing-fixture sin escribir baseline. **No regenerar snapshots existentes para hacer verde el test**.
- [ ] **B-03 — `TS-003/TS-004` Falsa amplitud E2E.** Determinar alcance real; conservar garantías útiles de consumidores, FinOps y fakes, pero corregir nombres, docstrings, markers y ubicación si sobredeclaran ruta completa. Cualquier reemplazo debe ejecutar el SUT real pertinente; no reabrir laboratorio completo C0–C4.
- [ ] **B-04 — `TS-005` y casos equivalentes.** Reconciliar “fidelity/integration/real” con invariantes efectivamente comprobadas; no descartar protección matemática válida sólo por un nombre impreciso.
- [ ] **B-05 — Fixtures, skips y side effects.** Sustituir rutas fijas y escrituras a `tests/fixtures`/output por `tmp_path`; distinguir tests opcionales de barreras obligatorias; registrar SKIP/XFAIL explícitos y prohibir que un skip cuente como cobertura.
- [ ] **B-06 — Revisar testigos técnicos existentes de alta criticidad.** W06, G3, G5, contexto y B02: retener garantías reales, reducir acoplamientos accidentales, sin reescribir fakes legítimos ni romper evidencia de fencing.
- [ ] **B-07 — Entregar remediaciones en cambios pequeños y revisables.** Un problema/contrato por PR o commit coherente; evidencia before/after, impacto sobre selección CI, tests focales, Pyright local y resultado técnico en GitHub.
- [ ] **B-08 — Verificar que no se relajó el contrato.** No cambiar expected para acomodar implementación, no reemplazar el SUT por un fake, no borrar tests difíciles ni convertir errores en xfail/skip para elevar PASS.
- [ ] **B-09 — Cerrar brechas P0 o registrar excepciones explícitas.** Ninguna excepción implícita: owner, alcance, riesgo, compensación técnica, test afectado y fecha de revisión.

**Gate B (para pasar a C):** cero **falsas garantías P0 conocidas** afirmadas como PASS; los tests remediados tienen contratos claros, oráculos no autorreferentes, tests focales reproducibles y ningún cambio de runtime/GT; las limitaciones no reparadas están visibles.

### Etapa C — Introducir y probar controles negativos (**TERCERA**)

- [ ] **C-00 — Diseñar matriz de mutaciones.** Para cada contrato crítico registrar mutación reproducible, punto de inyección, observación esperada, efecto prohibido, test protector y evidencia. Reutilizar las pruebas existentes.
- [ ] **C-01 — B02/parser.** PDF técnico representable produce evidencia estructural mínima verificable; dibujo vectorial no representable ocasiona rechazo indexable; una degradación silenciosa debe ser detectada por el test.
- [ ] **C-02 — AST/plan/contexto.** Inyectar discordancia de identidad `ast_hash`/`manifest_sha256`/`node_id` en **plan técnico**; exigir rechazo y ausencia de avance/publicación no autorizada. No mutar manifiesto científico canónico.
- [ ] **C-03 — G3 efecto externo incierto.** Confirmar que un estado `G3_EXTERNAL_UNKNOWN` o equivalente del contrato conserva STOP y **no** reenvía al proveedor; registrar conteo observable de POST al fake externo.
- [ ] **C-04 — G3 publicación y proyecciones.** Simular generación obsoleta o proyección CURRENT faltante; ningún stale write, ensamblado o publicación falsa.
- [ ] **C-05 — G5 lease/fencing.** Inyectar propietario/versión inválida o lease vencido en SQLite descartable; exigir rechazo y ausencia de PDF promocionado o estado `COMPLETED` indebido.
- [ ] **C-06 — FSM/foreground y fallos de etapas.** OCR sin estado, G3 fallido o G5 rechazado jamás pueden reportar éxito; demostrar error específico, transición durable coherente y ausencia de efecto físico final.
- [ ] **C-07 — Demostrar poder falsador.** Para cada P0, además del caso de entrada negativa, ejecutar al menos una **mutación controlada aislada** que invalide la barrera del SUT y comprobar que el test protector se vuelve rojo (`MUTATION_KILLED`); si no, abrir hallazgo `NOT_KILLED`, no forzar verde. Nunca mutar el árbol principal del owner.
- [ ] **C-08 — Repetibilidad y hermeticidad.** Repetir los testigos de alta criticidad en entorno limpio; comprobar invariantes, ausencia de escrituras a fixtures/corpus, no egress y resultados estables. Registrar flakiness si existe; no taparla con retries.
- [ ] **C-09 — Publicar cobertura demostrada y límites.** Tabla contrato × test × control negativo × sensibilidad, con evidencias enlazadas; separar cobertura demostrada, parcial y no ejercida.

**Gate C / cierre técnico:** controles negativos relevantes matados o hallazgos abiertos explícitos, ninguna falsa garantía P0 presentada como cubierta, selección y alcance de CI verificados, código productivo intacto, evidencia auditable por SHA y firma de aceptación del owner.

### 6.4 Registro de avance (actualizable, no basado en impresiones)

| Hito | Estado inicial | Responsable | Evidencia de cierre (SHA / PR / informe) | Revisor / decisión |
|---|---|---|---|---|
| A — Auditoría | [ ] EN CURSO — **A-00 cerrado**, A-01…A-07 pendientes | maintainer / implementación por asignar | [A-00 — inventario y riesgos](A00_BASELINE_INVENTARIO_Y_RIESGOS.md); `main` `83ef0257`, tree `9495259` | Revisión de ejecución pendiente para A-01…A-07 |
| B — Remediación | [ ] PENDIENTE | por asignar | — | — |
| C — Controles negativos | [ ] PENDIENTE | por asignar | — | — |
| Gate de cierre técnico | [ ] PENDIENTE | maintainer | — | — |
| D-4 — Consolidación ruta única | [ ] DIFERIDO, **no ejecutar ahora** | post-refinamiento | — | — |
| D-5 — GT y ciencia | [ ] DIFERIDO, **no ejecutar ahora** | post-refinamiento | — | — |

Para tareas individuales, actualizar la casilla del `6 y añadir una entrada al historial `10.2. La columna de evidencia no puede decir solo “pytest verde”: incluir qué prueba protegió qué contrato y cómo se comprobó la sensibilidad.

---

## 7. Protocolo de ejecución y PRs

### 7.1 Estrategia de ramas

1. `main` es referencia protegida y **permanece sin modificaciones** al crear esta iniciativa.
2. `tests_stabilization` es **rama de trabajo**; inicialmente contiene documentación y después, previa revisión, cambios únicamente en tests/infraestructura técnica de pruebas. No arrastrar cambios de runtime al mismo commit.
3. Mantener **un PR Draft de `tests_stabilization` → `main`** para que cada push al HEAD tenga CI técnico del workflow existente; dejarlo Draft hasta cierre de campaña y autorización expresa del owner. Si se usan ramas temporales para tareas focales, recordar que PRs con base `tests_stabilization` **no** activan automáticamente el workflow actual: deben disponer de evidencia focal propia y el PR Draft global verificará el conjunto.
4. **No hacer merge automático.** Revisar diff, HEAD/base, tests, CI requerido y alcance antes de solicitar la integración final. Conservar commits y referencias; no reescribir historia ni borrar ramas sin necesidad.
5. El plan/documentación es versionable: cada cambio de alcance exige motivo, decisión y un incremento de versión; no editar documentos históricos FROZEN para reetiquetar fallos como resueltos.

### 7.2 Entorno seguro

- Guardar por cada corrida: commit exacto, `git status --short` previo/posterior, Python/pytest/Pyright, SO, comando y selección efectiva.
- Preferir **worktree/clon descartable** para pruebas heredadas con escrituras a fixtures o mutaciones de implementación. No correr tests potencialmente mutadores directamente sobre la copia con outputs locales del owner.
- No usar credenciales, internet ni proveedores reales; fakes en puertos externos, filesystem/SQLite aislado. Nunca reciclar DBs ni identificadores de ejecuciones entre pruebas.
- Mantener el archivo `pyright-local.json` **sólo local**; GitHub continúa usando `pyrightconfig.json`. Registrar dos evidencias distintas: Pyright local con tests y check estático obligatorio GitHub sobre producción.
- En PowerShell, comandos de inventario orientativos (no implica aprobación de ejecución irrestricta):

```powershell
git status --short
git rev-parse HEAD
python -m pytest --collect-only -q
pyright --project .\pyright-local.json --pythonpath .\venv\Scripts\python.exe
```

**Precaución:** la colección puede ejecutar imports/fixtures de colección con efectos indeseados. Ejecutarla en una copia aislada si `A-05` aún no acredita ausencia de escrituras. El `pytest` completo sólo se habilita tras revisar riesgos o en aislamiento. El CI ya ejecuta el conjunto técnico actual; no implica que los tests no sean tautológicos.

### 7.3 Definition of Done por remediación (todas obligatorias)

- [ ] El test identifica explícitamente contrato, SUT real, límites y fuente normativa/consumidor.
- [ ] El oráculo es independiente; la prueba no se autoaprueba ni genera su expected.
- [ ] Los mocks se encuentran en fronteras justificadas; el nombre/marker no sobredeclara E2E.
- [ ] Happy path y al menos un rechazo relevante se demuestran, incluyendo ausencia de efectos prohibidos cuando corresponda.
- [ ] Existe evidencia de sensibilidad para P0 (o excepción explícita registrada sin marcar el contrato como cubierto).
- [ ] Fixtures, SQLite y archivos son descartables; no se modificó corpus, outputs locales ni snapshots por sorpresa.
- [ ] Pruebas focales aprueban; Pyright local no introduce nuevos errores; GitHub reporta estado técnico real y se anotan skips/xfail.
- [ ] Diff y evidencia trazados al SHA, con revisión del owner y sin cambios ajenos al objetivo.
- [ ] El estado del registro y las casillas se actualizaron en el mismo cambio o PR.

### 7.4 Condiciones de no-merge y escalado

**NO MERGE** si aparece alguna de estas condiciones: P0 de falsa garantía sin reclasificar, tests que siguen autoescribiendo expected, mutación que el protector no detecta presentada como éxito, fragilidad introducida por implementación privada, cambio de baseline científica, test que requiere proveedor real, side effect no controlado o check requerido rojo.

Si una corrección de tests revela error **productivo**, generar un issue/registro separado con reproducer y test que falla por contrato; no modificar runtime ni expected dentro de esta campaña para esconderlo. Si un test viejo depende de R1 o R3, identificarlo como tal y conservarlo cuando sea útil; no convertirlo por nombre en test de la ruta OCR/G3/G5.

---

## 8. Matriz mínima de controles negativos (diseño, no resultados)

| Control ID | Violación inyectada en entorno aislado | Veredicto exigido | Efectos que deben permanecer ausentes | Test protector / evidencia |
|---|---|---|---|---|
| `NC-01` | Parser recibe vector no representable | `B02_UNREPRESENTED_VECTOR_DRAWING` o rechazo contractual equivalente | AST publicado como completo / éxito falso | por vincular (`TS-006` candidato) |
| `NC-02` | Plan AST/manifiesto de generación equivocada | Rechazo de identidad/binding | Provider POST y publicación posterior | por vincular |
| `NC-03` | Estado de efecto G3 incierto | STOP/cuarentena según contrato G3 | **Nuevo POST externo** al fake | por vincular |
| `NC-04` | Proyección CURRENT faltante | Ensamblado denegado | Archivo PDF final | por vincular |
| `NC-05` | Lease vencido / CAS stale en G5 | Error o transición segura | `os.replace` autorizado y falso `COMPLETED` | por vincular |
| `NC-06` | Error OCR/estado FSM ausente | Rechazo de foreground | PDF final y éxito reportado | por vincular |
| `NC-07` | Fixture técnica obligatoria ausente | Fallo explícito de precondición del test | Autocreación de snapshot/expected | por vincular (`TS-002` candidato) |
| `NC-08` | Resultado real diferente del esperado por mutación del SUT | Test protector falla (mutation kill) | Aprobación por comparación circular | por vincular (`TS-001` candidato) |

**Nota:** `NC-03` se refiere a cuarentena de **efecto del proveedor G3**, no a estado del corpus de evaluación; `NC-02` se refiere al **manifest del plan técnico**, no al manifiesto sellado del Ground Truth. Cada tabla debe completar nombre del test, comando, evidencia/commit y observación antes de marcar un control como realizado.

---

## 9. Métricas de progreso, riesgos y criterios de salida

### 9.1 Métricas que se reportarán (sin fabricar porcentajes iniciales)

| Métrica | Numerador / denominador o definición | Objetivo de campaña |
|---|---|---|
| Inventario auditado | Casos pertinentes con ficha `TR-###` completa / total de casos pertinentes descubiertos | 100%, con lista de exclusiones justificada |
| Cobertura de contratos críticos | Contratos P0 con test real y control negativo probado / contratos P0 inventariados | 100% o excepción explícita **sin** declarar cobertura |
| Falsas garantías activas | Tests defectuosos P0 aún presentados como prueba válida en CI/documentación | 0 al cierre |
| Oráculos autoactualizables | Tests obligatorios que escriben expected/snapshot durante la ejecución | 0 |
| Calidad de selección | Tests incluidos, omitidos, `SKIP`, `XFAIL` y marcadores correlacionados con garantías declaradas | Trazabilidad completa, sin SKIP que simule cobertura |
| Sensibilidad | Mutaciones P0 detectadas / mutaciones P0 ejecutadas; `NOT_RUN` separado | Ningún `NOT_KILLED` aceptado como protección |
| Hermeticidad | Tests revisados que no realizan I/O no autorizado / tests técnicos auditados | 100% para ejecución normal |
| Estabilidad | Repeticiones de testigos P0 consistentes / repeticiones ejecutadas | Sin flakiness silenciosa; investigar cada anomalía |

No inferir cobertura a partir de “cantidad de tests verdes”, Pyright 0 o el nombre del archivo. No fijar cifras absolutas hasta completar A-01.

### 9.2 Registro de riesgos

| Riesgo | Impacto | Prevención / respuesta |
|---|---|---|
| Endurecer una aserción contra un detalle volátil | Tests frágiles cuando afinemos el pipeline | Exigir fuente de contrato y preferir propiedades; revisión `R-02/R-08` |
| “Arreglar” un rojo actualizando expected | Falsa garantía y pérdida de capacidad de detectar regresión | Prohibir autogeneración en pytest; revisión independiente de fixtures |
| Corrida legacy escribe en repo | Corrupción de datos, diffs falsos, borrado de output local | Identificar I/O antes de ejecutar; worktree aislado; prohibir limpieza destructiva |
| Fake demasiado profundo | Test pasa sin ejecutar el sujeto | Ficha `SUT` + evidencia de llamada real + control negativo |
| Test E2E mal nombrado | Decisiones erróneas de arquitectura/producto | Clasificar nivel real, renombrar sólo con justificación; no borrar su utilidad |
| Cambios a CI requeridos prematuramente | Bloqueo artificial de `main` o falsa cobertura | Mantener workflow/enforcement vigente; auditar selecciones; cambios futuros con decisión separada |
| Mezclar GT científico con fixture técnica | Re-baseline prematura y circularidad científica | Exclusión explícita de D-5; mantener corpus read-only |
| Refactor del pipeline a mitad de campaña | Evidencia atada a SHA obsoleto | Pin de base, reevaluación focal de test protector, sin heredar PASS |
| Mutaciones sobreviven | Contratos sin protección efectiva | Registrar `NOT_KILLED`, abrir brecha, no falsificar estado “resuelto” |

---

## 10. Gobierno, revisiones y registro de decisiones

**Roles:**
- **Owner / maintainer:** aprueba alcance, priorización, excepciones P0, cambios de CI y merge final.
- **Responsable de implementación (por tarea):** aporta patch, tests, log reproducible y actualiza matriz/checkbox.
- **Revisor técnico:** verifica independencia del oráculo, estabilidad frente a refactor, selección CI y no alteración del runtime. Cuando sólo participa una persona, hacer revisión explícita de diff y evidencias antes de solicitar merge.

**Cadencia por cambio:** problema → evidencia estática → ficha `TR-###` → propuesta mínima → prueba positiva/negativa → sensibilidad → verificación local/CI → revisión → estado actualizado.

**Política de excepciones:** sólo con ID, por qué no se cubre, riesgo residual, dueño, alternativa y disparador de reevaluación. Una excepción **no** computa como PASS ni permite rotular `PRODUCT_READINESS=PASS`.

**No duplicar fuentes normativas:** el [Atlas](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) y sus testigos sirven de referencia histórica; las decisiones congeladas prevalecen. Esta rama es un expediente de calidad de pruebas, no otra arquitectura del traductor.

### 10.1 Formato para agregar evidencia a cada tarea

```text
TST-STAB/<ID>  —  Fecha:
Contrato y fuente:
Archivo::test (parámetros) / clasificación previa → nueva:
Base SHA / Head SHA:
SUT real y doubles:
Fixture, I/O y sandbox:
Caso positivo / resultado / exit:
Caso negativo / error-estado / efectos prohibidos:
Mutación (si aplica) / KILLED | NOT_KILLED | NOT_RUN:
pytest selección / passed / failed / skipped / xfailed:
Pyright local / CI técnico requerido / CI informativo:
Diff de referencias/fixtures: sí-no y explicación:
Limitaciones; PR o commit; revisor; decisión:
```

Una nueva línea de avance en este plan **no** sustituye las evidencias identificables de un PR y su commit. Cuando la matriz crezca, **A-04 podrá introducir un registro técnico separado dentro de esta misma carpeta**, enlazado desde aquí, sin duplicar ni congelar en este plan cientos de filas cambiantes.

### 10.2 Historial de ejecución del plan

| Fecha | Cambio de estado | ID | Commit / PR | Evidencia y decisión |
|---|---|---|---|---|
| 2026-11-15 | Apertura de plan, **sin cierre de tareas** | TST-STAB | rama `tests_stabilization`, base `83ef0257` | Inventario semilla estático; revisión/ejecución futura pendiente |
| 2026-11-15 | **A-00 cerrado — censo y riesgos por inspección estática** | A-00 | [Inventario A-00](A00_BASELINE_INVENTARIO_Y_RIESGOS.md); base `83ef0257`, tree `9495259`, versión Markdown normalizada en `b97430d` | 188 archivos Python, 177 módulos candidatos, selección de CI y rutas R1/R3 contrastadas, fixtures y escrituras potencialmente destructivas registradas; **sin ejecutar tests, sin cerrar A-01…A-07** |
| 2026-11-15 | **A-01 en curso — censo completo de fuentes, no collection dinámica** | A-01 | [Índice A-01](A01_INVENTARIO_CONSOLIDADO_Y_GATES.md), 16 registros; baseline `83ef0257` | 177 módulos inspeccionados, 1.341 declaraciones estáticas; selección dinámica, markers efectivos, SUT, I/O indirectos y resultados de pytest **pendientes**. Check **[ ]** mantenido por DoD. |
| 2026-11-15 | **A-05 preflight parcial; colección no ejecutada** | A-05 | [Preflight y límites](A05_PREFLIGHT_A01_COLECCION_AISLADA.md); [ejecutor opt-in](collect_a01_isolated.py) | Repositorio sintético recolectó 5/1/3/4 nodos por selector; prueba sólo del ejecutor, **no de tests reales**. Preparación sin ejecución habilitada; control de imports/I/O y selección real pendientes. |
| 2026-11-15 | **Colección real de pytest completada, A-01/A-05 aún abiertos** | A-01/A-05 | [Informe de colección](A01_COLECCION_PYTEST_2026-11-15.md); SHA `86cd6867` | `--collect-only`: 1.474 all / 225 unit / 70 integration_nonregression / 1.454 technical; exit=0 ×4, 0 cuerpos de test ejecutados. Falta conciliar JSON y verificar efectos en working trees; no implica PASS. |

---

## 11. Actividades expresamente diferidas hasta después del refinamiento del pipeline

Este capítulo **documenta dependencias futuras, no añade trabajos al programa activo**.

### D-4 — Consolidación global de ruta operativa única (POST-REFINAMIENTO)

Se reabrirá sólo cuando el owner declare terminada la etapa de refinamiento. Se revisarán cambios de contratos, se elegirá la topología de laboratorio pertinente, se reconstruirá evidencia **nueva sobre el SHA final** y se confrontará con los testigos C0–C4 históricos sin inferir equivalencia automática. Incluye, si se justifica, un E2E técnico físico PDF→PDF, con proveedor simulado, entorno descartable y alcance explícito.

**No se ejecuta ni se acredita durante A/B/C.** La auditoría de tests puede usar el Atlas para identificar contratos y tests adecuados, pero no rehace las campañas operacionales.

### D-5 — Ciencia, corpus, Ground Truth y CV (POST-REFINAMIENTO)

Se reabrirá sólo después del refinamiento y de una decisión de gobernanza del owner. Requerirá abordar materialización autorizada y hashes del corpus canónico, curaduría independiente, limitaciones de GT tautológicos, evidencia de extracción/AST/fidelidad, calificación estadística, thresholds gobernados y condiciones contractuales para convertir CV en required. La [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34), los [hallazgos consolidados](../phase-17-bis/reports/FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md) y el [enforcement contract](../phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md) son referencias para esa etapa, no autorización para modificar la baseline ahora.

**No usar “el pipeline está afinado” como autorización automática de re-baseline**: será necesaria una decisión explícita, revisión de licencias/materialización y trazabilidad de nueva versión.

### Registro de diferimiento

- [ ] **D-4 — En espera del cierre del refinamiento y autorización posterior del owner.** No marcar por completar A/B/C.
- [ ] **D-5 — En espera del cierre del refinamiento y decisión científica separada.** No marcar por completar A/B/C.

---

## 12. Fuentes primarias, jerarquía y lectura inicial

1. [`ENGINEERING_PRINCIPLES.md`](../../../../ENGINEERING_PRINCIPLES.md): “cero fallos silenciosos”, trazabilidad y reuse-before-invent; prevalece sobre conveniencia del test.
2. [HITO 0.4.4 Regression Architecture Audit](../phase-17-bis/00-foundation/HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md): inspección forense y falsos positivos heredados, incluido `GAP-0.4-09`.
3. [HITO 4.4 Testing Prerequisites Discovery](../phase-17-bis/00-foundation/HITO_4.4_TESTING_PREREQUISITES_DISCOVERY.md): independencia de oráculos, snapshots, negative controls.
4. [FASE 4 Exit Review — DF-01 de Fase 4](../phase-17-bis/reviews/FASE_4_EXIT_REVIEW_EVIDENCE_LOG.md): deuda formal de `test_golden_parser` y `test_chunker_snapshot`.
5. [FASE 17-BIS — Deferred Findings Consolidated](../phase-17-bis/reports/FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md): confirma diferimiento de deuda de tests y separa re-baseline futuro.
6. [Atlas de la ruta operativa única](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) y [evidencia de cierre](../pipeline-stabilization/handoff/EVIDENCIA_Y_CIERRE.md): root realmente seleccionado, testigos focales y límites de la acreditación.
7. [`ci.yml`](../../../../.github/workflows/ci.yml) y [`continuous-verification.yml`](../../../../.github/workflows/continuous-verification.yml): **observar la configuración actual**, nunca sustituir la selección real por descripciones históricas.
8. [FASE 6 Enforcement Contract](../phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md): único check requerido y CV científico informativo durante transición.

**Regla de precedencia:** decisiones y contratos normativos FROZEN aplicables → código/CI de un **SHA explícito** → evidencias de ejecución del mismo SHA → este plan como instrumento operativo. Los diagnósticos históricos son pistas, no prueba de que todo el código presente siga igual.

---

## 13. Definición de cierre y handoff al refinamiento

La campaña **TST-STAB puede cerrarse** únicamente si:

- [ ] Gates A, B y C tienen evidencia vinculada a commits y revisión del owner.
- [ ] Toda prueba crítica de la ruta activa tiene alcance honesto, SUT real, oráculo independiente y al menos un control negativo significativo; las excepciones no simulan cobertura.
- [ ] Las falsas garantías históricas confirmadas fueron corregidas, aisladas/reclasificadas o registradas explícitamente sin que sus PASS se presenten como seguridad de la ruta actual.
- [ ] La ejecución técnica es hermética y reproducible en el alcance declarado; no se mutan fixtures/GT ni se usan proveedores reales.
- [ ] El CI técnico vigente es reportado con su cobertura **real**; el check requerido está verde para el HEAD candidato, con suite focal y Pyright local documentados.
- [ ] Se ha revisado el diff acumulado y se ha autorizado explícitamente integrar a `main`, sin changes de runtime.
- [ ] El handoff enumera contratos protegidos para comenzar **después** el refinamiento del pipeline y enumera vacíos/limitaciones con responsables.
- [ ] Los diferidos D-4 y D-5 siguen fuera de alcance y se transferirán únicamente cuando se cumplan sus condiciones futuras.

**Resultado esperado:** una red de protección técnica precisa y difícil de falsear, que soporte refactors profundos **sin cambiar los tests por detalles internos**, y que obligue a explicar cualquier cambio legítimo de contrato antes de ajustar un esperado. Este resultado no pretende demostrar calidad científica ni certificar el producto.
