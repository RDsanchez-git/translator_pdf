# Plan de estabilización y remediación de los tests del pipeline PDF→PDF

> **Código del programa:** TST-STAB  
> **Versión:** 0.1.2 — A-00 cerrado; auditoría A activa, remediaciones B focales en curso y controles negativos B05 parciales  
> **Estado:** EN EJECUCIÓN — **A-00 cerrado**; A-01…A-07 abiertos; B05 con 4 tests PASS y 2 controles negativos detectados por el owner; **B-01/B-02 con baseline focal exit 0, Pyright 0 y 2/2 mutaciones detectadas según reporte del owner**; C general abierto. Runtime, CI y Ground Truth sin modificaciones.  
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
- [ ] **A-01 — Inventario semántico (EN CURSO).** Censo estático **177/177 módulos y 1.341 declaraciones** documentado; **colección real ya realizada** en clon independiente a SHA `86cd6867`, con **1.474 nodos all, 225 unit, 70 integration_nonregression, 1.454 not e2e** y cuatro exit codes 0. [Resultado y conciliación pendiente](A01_COLECCION_PYTEST_2026-11-15.md). Ya se confirmó **1.474/1.474 nodeids únicos**, **187 nodos con ID de parametrización** y markers **unit=225, integration=70, e2e=20, regression=0, smoke=0, skipif=1**. Se confirmó coherencia de selectores **por nodeid** (cuatro discrepancias = 0) y el único `skipif` corresponde al freeze de parámetros (artefacto versionado, no ejecutado); la conciliación está completa: **1.159 casos sin marker de nivel**, **173/177 archivos con nodos**, **24 diferencias con declaraciones fuente**, **12/12 rutas focales del CI con 138 casos**, sin señales de warning/error en cuatro logs bajo las expresiones auditadas. Los **4 módulos sin nodos** fueron clasificados: 3 placeholders vacíos y un script manual de estrés ([evidencia §3.4](A01_COLECCION_PYTEST_2026-11-15.md)). **A01-S6 cerrado:** el [cotejo exhaustivo](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md) confirmó **1.341 + 133 expansiones = 1.474 nodeids**, **0 funciones fuente omitidas**, **0 nodeids huérfanos**, **24/24 diferencias justificadas** (23 arrays literales, una lista nombrada de cuatro rutas). **A01-S5 en curso:** [19 fichas primera tanda](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md) + [16 fichas segunda tanda TR-020…035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md) = **35 fichas por contrato/frontera**, que documentan SUT, dobles, aserciones y riesgos de refactor. **Puente de nodeids ejecutado por el owner:** [evidencia A01-S5](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md): **277 nodeids en 29 archivos con TR; 1.197 en 144 archivos sin TR; 0 casos semánticamente acreditados**, 1.159 sin marker de nivel (235+924); 4 alertas de calidad. Ocho archivos prioritarios (236 nodeids) clasificados preliminarmente por fuente; para G3-B3 se añadió una [auditoría estática granular de 33 variantes](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md): 12 funciones, 17 mutaciones de miembros, 6 JSON inválidos, con SUT y oráculos, y [verificador de nodeids](verify_a01_s5_g3_b3_nodeids.py) **ejecutado sobre `all.json` por el owner**: 33 nodeids únicos, 12 funciones coincidentes, 10 simples + 17 + 6 variantes, [IDs exactos B3-01…33 documentados](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md). **Persisten 0 casos certificados en ejecución**, falta independencia final de oráculos/falsación y trazabilidad restante. **Mantener [ ]**.
- [ ] **A-02 — Trazar contratos a tests (MAPEO 8/8 COMPLETADO; revisión de cierre por owner pendiente).** Las ocho fronteras del `2.4` tienen SUT, TR/testigos, positivo, negativo, evidencia por SHA y huecos en la [matriz A-02 §9](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md). No confundir trazabilidad documentada con suite/CI PASS universal ni cerrar A-04/A-07 por ello. Se conserva el checkbox abierto hasta revisión formal de cierre del owner.
- [ ] **A-03 — Evaluar independencia de oráculos y mocks (EN CURSO; P0 focales remediados).** [Clasificación de 35 fichas TR §7](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md): **7 CONFIABLE_PARA_SU_ALCANCE focal**, **9 LIMITADO**, **19 DESCONOCIDO** en ejecución focal; los resultados de un TR no acreditan todos los nodeids de ese archivo. [TS-001/TS-002](A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md) fueron corregidos con parser real/oráculo independiente y chunker sin expected autoescrito; se reportaron controles negativos focales KILLED. [G3-B3](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md) añadió UTF-8 multibyte (39 PASS y mutante detectado) y mantiene límites OI-01/02/03/05. **A-03 global sigue [ ]**: no se han inspeccionado/ejecutado todas las familias relevantes ni probado aislamiento OS/CI del HEAD. No reutilizar como estado actual los diagnósticos del SHA inicial sin contrastarlos.
- [x] **A-04 — Fichas y parametrizaciones materiales (CIERRE DOCUMENTAL ACEPTADO POR EL OWNER, 2026-11-16).** [Matriz §§7–13](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md): 1.476 nodeids / 173 archivos reconciliados por ruta y familia, 35 fichas TR y 19 funciones parametrizadas con 67 casos preservados. Clasificación final de los 35 TR: **7 `CONFIABLE_PARA_SU_ALCANCE` solo en subcontratos focales**, **28 `LIMITADO`**, **0 `DESCONOCIDO`**. El owner aceptó expresamente este criterio y autorizó pasar a A-05. **Cierre solo de clasificación y trazabilidad; NO** certifica 1.476 PASS, sensibilidad universal, seguridad OS, CI verde ni E2E físico. El JSON de colección pertenece a SHA anterior al HEAD; revisión final de cambios/CI queda en A-06/cierre técnico. Hallazgos TR-007 y riesgos de escritura registrados para A-07/A-05.
- [ ] **A-05 — Seguridad de ejecución (REVALIDACIÓN DE COLECCIÓN LIMPIA; P4/P6 GLOBALES ABIERTOS).** [Expediente A05 §24](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md): owner RAR5 de cinco informes sobre SHA `d754a56c19810f39e29e6ec485e948039b1ec686`: 1.478/225/72/1.458 nodos por cuatro selectors, exit 0, 30/30 hashes protegidos iguales y Git antes/después vacío; la mitigación de la caché `.hypothesis` quedó comprobada sin ejecutar cuerpos. El primer intento SHA `cffc57f` había detectado 271 archivos ignorados y falló correctamente. Los logs de plugins cargados corresponden al intento anterior; el RAR de revalidación solo contiene manifiesto/inventarios. Red/IO transitorio/externo y sandbox OS **no acreditados**. No ejecutar la suite técnica global sobre el checkout habitual.
- [ ] **A-06 — Baseline técnico controlado (COLECCIÓN 1.478 LIMPIA; DOS COHORTES, 43 PASS; CI REAL/GLOBAL PENDIENTES).** [Expediente A05 §§24–26](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md): colección del owner de 1.478 nodos, cuatro selectores exit 0 y clon/hash protegidos sin modificaciones persistentes en SHA `d754a56c`. Cohorte W08/G3 en SHA `13ae7e5d`: **23 passed**, Git/hashes limpios; cohorte G3 fencing/PRESERVE/cuotas en SHA `0b5fd88f`: **20 passed, 2 warnings in 3.39s**, `a06_g3_guards_requested=True`, 30 archivos protegidos SHA-256 idénticos, Git antes/después/status vacíos, sin mutaciones. **43 PASS en dos ejecuciones, no una sola suite CI; no 225 unit/1.458 technical PASS.** Antes de ampliar, conciliar nodeids y evidencia existentes contra steps explícitos/markers del `ci.yml`, excluir duplicados y auditar I/O de casos no cubiertos; no crear otro grupo por rutina, ejecutar global en checkout habitual ni declarar aislamiento OS/egress. CI HEAD y A05-P4/P6 globales abiertos.
- [ ] **A-07 — Publicar matriz de brechas priorizada (PRELIMINAR EN §6, pendiente de revisión del owner).** P0/P1/P2, defectos confirmados frente a hipótesis, dependencias, propuesta de remediación y criterio para falsar la garantía; sin declarar A-07 cerrado por redactar la matriz.

### A-06 → A-07 — conciliación de CI y matriz preliminar de brechas (2026-11-16)

**Sujeto y fuentes:** `tests_stabilization` HEAD `f7d5653b1362efe5f49ec7dedf22a65fbd6eef30`; `.github/workflows/ci.yml`, `pyproject.toml`, expedientes A-05 §§24–26, matriz A-02 §9, matriz A-04 §13 y código de los 12 archivos explícitos. La colección exacta `1.478/225/72/1.458` procede de `d754a56c19810f39e29e6ec485e948039b1ec686`, **sin ejecución de cuerpos**. Entre ese SHA y el HEAD actual se comprobaron cambios solamente en los dos documentos A-05/plan y en `run_b05_focal_isolated.ps1`, no en tests ni `ci.yml`. Los conteos por archivo proceden del `all.json` histórico de 1.476 nodeids, cruzado con rutas inalteradas; **no se ha reconstruido el JSON individual de los 1.478 en este hito**. El HEAD no tiene corrida de GitHub Actions acreditada. Todo el análisis de esta sección es **estático/documental**, sin nuevo pytest, Pyright, mutaciones o egress.

#### Conciliación exacta de selección frente a evidencia de ejecución

| Step de `ci.yml` / archivos | Nodeids seleccionables | A-06 PASS en SHA propio | PASS históricos TST-STAB identificables adicionales | Sin baseline focal individual identificada en esos informes* |
|---|---:|---:|---:|---:|
| `-m "unit"` (225) | **225** | **23** W08 `13ae7e5d` | No conciliados por nodeid aquí | No calcular saldo histórico como FAIL |
| B03 fake G3 y laboratorio offline, 2 archivos | **33** | 0 | No se identificó reporte focal de esos 33 nodeids | **33** |
| W06/G3 offline, 5 archivos | **70** | **17** (14 fencing + 3 PRESERVE), `0b5fd88f` | **4** (2 W06 UNKNOWN/restart + 2 publicación G3 missing/drift), baseline `16a68229` y C-03/C-04 KILLED en la misma campaña | **49** |
| W08 durable context, 1 archivo | **13** | 0 | No identificado en los informes consultados | **13** |
| W08 OCR/G3 y plan durable, 2 archivos | **16** | 0 | No identificado en los informes consultados | **16** |
| G3 cuota SQLite / G5 worker, 2 archivos | **6** | **3** cuota `0b5fd88f` | **3** worker G5 `97a1bbef`, con 2 mutaciones KILLED | **0** |
| **Subtotal de rutas explícitas** (12 archivos disjuntos) | **138** | **20** | **7** | **111** |
| `-m "integration and not regression"` | **72** | 0 en las dos cohortes A-06 | No conciliado por nodeid contra todos los históricos | Sin veredicto global |
| `-m "not e2e"` | **1.458** | Selecciona otra vez los **43** A-06 | Incluye las selecciones explícitas y unit/integration | **No hay baseline global** |

* **“Sin baseline focal identificada” no significa test fallido, inútil, defectuoso o jamás ejecutado en otra campaña**: significa que no hay un resultado individual asociable de los informes TST-STAB focales revisados. Las evidencias históricas pertenecen a otros SHA y no certifican un único job verde del HEAD. Los **23 PASS W08 de A-06** corresponden a dos archivos marcados `unit` y **no** a los 12 archivos de pasos explícitos; por eso no se suman al subtotal de 138. Los **20 PASS G3** sí están dentro de esos 138 (17 + 3). Las **7 evidencias históricas adicionales** son distintas de esos 20, no sumas duplicadas de parámetros. Los `8 PASS/3 SKIP` A-05 de `65385307` permanecen aparte.

**Solapamiento de CI:** los **225 unit + 72 integration + 138 explícitos** no se solapan entre sí en el inventario de marker/rutas de 1.476; cada uno vuelve a caer en `not e2e`. Son **435 nodeids sujetos a una segunda ejecución en el workflow** si los jobs alcanzan el step final; no 435 contratos nuevos, y no constituye por sí mismo un fallo. La ejecución real sigue condicionada al orden de jobs, entorno y skips. Los pushes directos a `tests_stabilization` no disparan este workflow (push solo `main`/`develop`, PR a `main`/`pipeline_stabilization`). **No declarar CI PASSED** a partir de la definición del workflow; ninguna ejecución de Actions del SHA de referencia fue acreditada.

#### Riesgo de ejecución y decisión para los 111 explícitos no acreditados focalmente

La inspección de las **fuentes de los 12 archivos CI explícitos** detectó mayormente SQLite bajo `tmp_path` o `:memory:`, fakes y AST sintético; en B03 offline se verifican incluso comandos de contenedor como **datos**, sin levantar Docker en esos tests. No se detectó en sus cuerpos un borrado fijo directo equivalente al riesgo histórico de `test_recovery_flow.py`. **Esto es evaluación parcial de fuente, no garantía de seguridad de import hooks/pytest plugins/transporte o procesos hijos.** Antes de cualquier ejecución restante, cruzar imports/fixtures/side effects con A05-P4/P6 y elegir solo casos autorizados, sin permitir que un `not e2e` masivo corra sobre el checkout del owner.

La evidencia histórica de **C-03** (2 W06 incluidos en ese step) y **C-04** (2 publicación G3 del mismo step), junto con **G5W-NEG-01/02** sobre el worker del último step, **ya falsó regresiones específicas**. No repetirlas ni convertir la ausencia de mutantes de otros nodeids en P0 sin hallazgo de oráculo. Las cohortes A-06 no ejecutaron mutaciones. Las dimensiones restantes de identidad, leases y publicación conservan límites de sensibilidad en A-02 §9.

#### Matriz A-07 preliminar P0/P1/P2 — propuesta para revisión del owner

| ID / prioridad | Hecho constatado y límite | Acción mínima / criterio falsable | Estado |
|---|---|---|---|
| **A07-P0 — ninguno nuevo confirmado** | TS-001/TS-002 fueron falsas garantías P0 históricas **ya remediadas focalmente**; esta conciliación no encontró un nuevo falso PASS P0 ni defecto productivo demostrado | Escalar a P0 solamente tras hallar test autorreferente, efecto dañino, mutante crítico superviviente o falso éxito observables | **No abrir P0 hipotético** |
| **A07-P1-01 — seguridad A05-P4/P6** | La colección previa creó 271 ignorados Hypothesis y se corrigió; el clon/30 hashes solo detectan residuos persistentes. No hay evidencia de denegación de egress de SO ni de I/O creado-borrado/extraclón | Clasificar imports/plugins/fixtures del siguiente alcance elegido; demostrar ausencia de efectos prohibidos al nivel exigido **antes** de ampliar ejecución. Si falta control host/red necesario, bloquear, no inferir hermeticidad | **ABIERTO; gate A-05** |
| **A07-P1-02 — CI HEAD no ejecutado** | El workflow selecciona 225/72/1.458 y 12 rutas explícitas (138), pero no se observó Actions del HEAD `f7d5653b` | Solo tras riesgo A-05 revisado y autorización explícita: Draft PR hacia branch que dispare CI, leer resultado por job/step y registrar PASS/FAIL/SKIP por SHA; nunca merge automático | **ABIERTO; evidencia faltante** |
| **A07-P1-03 — oráculo TR-007** | `test_bridge_rejects_unbound_provider_output` usa `pytest.raises(ValueError)` genérico en las tres variantes `plain_text/wrong_chunk/bad_response`, pese a marcadores de rechazo específicos en tests vecinos. Un ValueError ajeno también daría verde | Revisar código de parse/binding y precisar `match` **por variante** en el test existente, sin cambiar SUT/expected por conveniencia; ejecutar focal y falsar un error equivocado si procede tras autorización | **CONFIRMADO estáticamente; no bug del SUT** |
| **A07-P1-04 — alcance de ejecutables sin evidencia focal nueva** | 111/138 nodeids de rutas explícitas sin reporte focal individual en los informes conciliados; destacan **49 staging/publicación/W06**, **29 W08**, **33 B03**. **Ausencia de prueba ≠ fallo** | Revisar críticamente riesgo y oráculos por contrato prioritario; descontar evidencia histórica adicional comprobable antes de autorizar **una ejecución conjunta útil**, sin minibaterías por rutina | **BRECHA DE EVIDENCIA, no defecto P0** |
| **A07-P1-05 — selección técnica amplia e históricos** | `not e2e` incluye casos legacy sin marker E2E; A05 focal mitigó rutas SQLite/CWD/Groq, pero P4/P6 no están globalmente certificados. Los 3 SKIP A05 no son PASS | No usar el nombre ni marker como sandbox; inventariar I/O de módulos técnicos relevantes y preservar fallos/skips honestos | **ABIERTO** |
| **A07-P2-01 — repetición de CI** | 435 nodeids vuelven a ejecutarse al final por `not e2e`, si se alcanza ese step | Medir costo y flakiness con CI real antes de cambiar selectors o deduplicar; cambiar CI requiere decisión separada | **NO BLOQUEANTE** |

**Decisión técnica propuesta, no aprobación final:** no añadir scripts, tests ni mutaciones ahora. Cerrar primero trazabilidad documental A-06↔CI y someter esta A-07 preliminar al owner; después resolver riesgos A-05 para el siguiente alcance, sin correr la suite global en Windows. A-06 **[ ]**, A-07 **[ ]**, A-05-P4/P6 **[ ]**. No se modificaron runtime, CI, Ground Truth, snapshots ni el checkout local; ningún PASS/CI nuevo se atribuye a este análisis.

---

**Gate A (para pasar a B):** inventario y matriz revisables, riesgo de side effects controlado, P0 definidos con pruebas de evidencia, cobertura de CI auditada. El número de tests pendientes se informa, no se maquilla.

### A-02/A-03/B-06: primera tanda focal G3/G5 (2026-11-16)

Se abrió la [matriz de contratos críticos G3/G5](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md) (commit `31d546d5`) para contrastar **siete testigos existentes** con sus SUT reales, oráculos y efectos prohibidos. El [runner en clon independiente](run_b05_focal_isolated.ps1) incluye la selección opt-in `-CheckG3G5` (commit `9994106f`): siete funciones nominales, nueve nodeids esperados por tres fases G5 parametrizadas. **No se ejecutaron estos tests todavía ni mutaciones C-03/C-04/C-05**. Sin Docker, nuevos servicios o modificaciones al runtime/CI/GT. Solo tras baseline focal verde y revisión de oráculos se prepararán controles negativos de la ruta activa. A-02/A-03/B-06 y gates generales **permanecen abiertos**.

### A-01/A-04 — Recenso del HEAD tras remediaciones (2026-11-16)

Se incorpora [`reconcile_a01_head_collection.py`](reconcile_a01_head_collection.py), **comparador de solo lectura de los JSON de dos recolecciones**, con guard estricto: colección histórica pinneada a `86cd68672ee692f073b62869e7c9bd177e8d9e3b`, colección actual pinneada al HEAD del owner, ancestro Git verificado, manifiestos y selectores consistentes, sin nodeids duplicados. Emite exclusivamente `a01_head_reconciliation.json` **en el directorio de reportes nuevo, externo al checkout**. Registra altas, bajas, markers, parámetros, rutas explícitas de `ci.yml` y nombres E2E sin marker. **No atribuye automáticamente una baja/alta a un rename ni acredita semántica, PASS, CI o seguridad OS.**

Para producir la recolección actual se reutiliza [`collect_a01_isolated.py`](collect_a01_isolated.py) `--collect`, que clona HEAD remoto en copia independiente sin hardlinks, aplica guard Python best-effort de socket, recoge cuatro expresiones con `pytest --collect-only` y deja los reportes intactos. **Sus imports/hooks se ejecutan; no constituye una sandbox del SO ni es prueba segura para ejecutar en el working tree del owner.** Si la colección histórica ya no existe, bloquear la comparación en vez de fabricar los datos. **Todavía no se ha corrido esta recolección ni el comparador en el SHA actualizado; A-01/A-04 siguen ABIERTOS.**

También se verificó por lectura de [`ci.yml`](../../../../.github/workflows/ci.yml) que el workflow escucha pushes a `main`/`develop` y pull requests hacia `main`/`pipeline_stabilization`; **no** se activa automáticamente con un push directo a `tests_stabilization`. La tabla de rutas/markers del comparador reconstruye selección de fuente, **no resultado real de GitHub Actions**. El eventual PR Draft hacia `main` y verificación de checks siguen pendientes de decisión/revisión del owner; no abrir PR ni hacer merge implícito.

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
| 2026-11-15 | **Conciliación JSON parcial + integridad Git post-collection** | A-01/A-05 | [A-01, §3.1](A01_COLECCION_PYTEST_2026-11-15.md); [A-05, §4.8](A05_PREFLIGHT_A01_COLECCION_AISLADA.md) | 1.474 nodeids únicos, 187 parametrizados, markers unit=225/integration=70/e2e=20/skipif=1; clon limpio por Git y PDF original D sin cambios. Faltan comparación de nodeids por selectors, CI focal, efectos ignorados/logs y SUT. Checkboxes **[ ]**. |
| 2026-11-15 | **Conciliación completa de la colección y CI focal; A-01/A-05 globales abiertos** | A01-S4 / A05-P5 | [A-01, §3.3](A01_COLECCION_PYTEST_2026-11-15.md), [A-05, §4.10](A05_PREFLIGHT_A01_COLECCION_AISLADA.md) | 1.159/1.474 nodos sin marker de nivel; 173/177 archivos con casos; 24 divergencias AST; 12/12 paths CI con 138 casos; 4 selector sets reconciliados, cero señales de error/warning buscadas en logs. Faltan 4 módulos, SUT y riesgos de imports. |
| 2026-11-15 | **A01-S6 cerrado — 24 divergencias parametrizadas reconciliadas** | A01-S6 | [Matriz exhaustiva](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md); pytest collection SHA `86cd6867` | 1.341 declaraciones + 133 expansiones = 1.474 nodeids; sin funciones no recolectadas ni nodeids huérfanos; 23 matrices literales y `CERTIFICATION_MODULES` de 4 rutas. A-01 sigue abierto por fichas SUT (A01-S5); A-05 sigue pendiente. |
| 2026-11-15 | **A01-S5 en curso — primeras 19 fichas semánticas de la ruta activa** | A01-S5 | [Matriz semántica](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md); tests inspeccionados sobre SHA `86cd6867` | Lectura de código: SUT real, mocks externos, oráculos observables, contraejemplos propuestos y riesgos de refactor para CLI/OCR/G3/W06/G5. **Sin ejecutar tests ni mutaciones**; ampliar cobertura y auditar independencia antes de cerrar. |
| 2026-11-15 | **A01-S5 segunda tanda — 16 fichas adicionales; 35 acumuladas** | A01-S5 | [TR-020 a TR-035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md) | Inspección fuente: durabilidad B2/W08, G5 worker, crash **real entre procesos** C3/T05, cuotas, PRESERVE, roots, WAL, publicación, CLI foreground. Riesgos de fragilidad documentados; **sin ejecutar tests ni certificar sensibilidad**. A01-S5 permanece abierto. |
| 2026-11-15 | **A01-S5 puente nodeid/contratos en preparación** | A01-S5 | [Plan de puente y oráculos](A01_S5_PUENTE_NODEIDS_Y_ORACULOS.md); [herramienta](map_a01_s5_nodeids.py) | 35 fichas en 29 archivos; cuatro hallazgos por lectura de código, incluidos dos oráculos defectuosos. Verificación individual por nodeid y ejecución de script con reportes locales **pendientes**. No se modifica GT ni código de tests. |
| 2026-11-15 | **A01-S5 G3-B3 — 33 escenarios inspeccionados estáticamente** | A01-S5 | [Matriz de 33 variantes](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md); [verificador exacto](verify_a01_s5_g3_b3_nodeids.py) | 12 funciones, 17 mutaciones de miembros, 6 JSON inválidos. Auditoría de SUT/oráculos sin ejecución; correspondencia de `all.json` y sensibilidad por mutación aún pendientes. A-01/A-05 abiertos. |
| 2026-11-15 | **A01-S5 G3-B3 — 33 nodeids exactos reconciliados** | S5-G3-04 | [Auditoría/tabla B3-01…33](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md); [verificador](verify_a01_s5_g3_b3_nodeids.py) | Output local del owner: SHA colección `86cd6867`, 12 funciones, 33 nodeids únicos, 10 simples, 17 mutaciones y 6 JSON inválidos; cardinalidad exacta. **Sin tests PASSED ni mutation kills**; A-01/A-03/A-05 siguen abiertos. |
| 2026-11-15 | **A-03 preauditoría G3-B3 — independencia de expected** | A-03/A01-S5 | [Oráculos G3-B3](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md) | 33 nodeids clasificados: 4 positivos, 1 mixto, 28 negativos; límites de plan compartido y mensajes regex, chunking y límite UTF-8 registrados; 10 falsadores propuestos **no ejecutados**. A-03/A-01/A-05 abiertos. |
| 2026-11-15 | **A-03 oráculos P0 — golden parser y snapshot chunker** | A-03 | [Preauditoría de oráculos](A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md) | Fuente inspeccionada: parser parcheado y expected circular, golden fingerprint ausente de Git; chunker snapshot autoescribible, referencia 10 unidades/11 campos y cache AST 58 nodos versionados, comparación de solo 4 campos y test zero-loss con normalización destructiva. Criterios B-01/B-02 documentados; **sin modificar/ejecutar tests ni GT**. |
| 2026-11-15 | **A-03/A-05 — E2E históricos y peligros en ejecución** | A-03/A-05 | [Auditoría dirigida](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md); [inspector read-only](inspect_a05_isolated_artifacts.py) | `test_real_e2e` simula execute/costos/COMPLETED; walking skeleton se autoasigna cache_hit y SummaryBuilder fake; recovery test borra DB fija y parchea global sin restaurar. P4/P6 abiertos; lectura post-colección de ignorados pendiente. **Sin ejecutar tests ni alterar GT**. |
| 2026-11-15 | **A-05 postcolección: 0 artefactos no versionados/ignorados, 11 tests históricos incluidos en `not e2e`** | A05-SAFE-P3 | [Evidencia owner](A05_POSTCOLECCION_ARTEFACTOS_Y_SELECTOR_HISTORICO_2026-11-15.md) | Inspector read-only sobre clon SHA `86cd6867`: `tests/` e `infra/db/` 0 cambios/untracked/ignorados, DB riesgos ausentes. Siete archivos históricos: 11 nodeids, **los 11 en `not e2e`, 0 marcados e2e**. Sin preinventario ni aislamiento OS; A05-P4/P6 permanecen abiertos. **No ejecutar suite técnica en repo owner**. |
| 2026-11-15 | **A-05 → A-06 — Gate fail-closed de aislamiento y contrato B-05** | A-05/A-06/B-05 | [Gate de VM y remediación](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md) | Inspección de fuente confirmó borrado de DB fija, patch global, setup SQLite y cache histórica. Diseñados VM sin host shares/secretos, egress denegado, pre/post inventarios, scope focal y mitigaciones `TemporaryDirectory`/`patch`. **Sin VM verificada, sin ejecutar tests y sin remediación aplicada**. |

---
| 2026-11-15 | **Decisión: pytest/CI técnico sin Docker obligatorio; B05-R1 corregido estáticamente, no cerrado** | A-05/B05-R1 | [Gate actualizado](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); test \`test_recovery_flow.py\` commit \`06362b60\`, gate \`79bf904d\` | Owner descarta Hyper-V como vía prioritaria y confirma que Docker no será dependencia ordinaria. SQLite de recuperación aislada por \`TemporaryDirectory/addClassCleanup\`; borrado fijo y global patch eliminados. FSM watchdog/resumer reales conservados; \`COMPLETED\` simulado. **Sin pytest, CI ni mutaciones ejecutados; B05-R1 y A-05/A-06 permanecen abiertos**. |
| 2026-11-15 | **B05-R2/R3 — fuentes corregidas, pruebas NO ejecutadas** | B05-R2/R3 | [Gate, §9](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); commits \`e8a24bee\`, \`bdb85717\`, \`8552d628\` | Caché legacy: SQLite temporal, fake contado y cache hit/summary observados en SUT; consumidores legacy: \`documents.db\` en memoria, sin fabricación de PDF ni sobredeclaración de E2E. Nodeids renombrados respecto de colección 1.474; requieren nueva conciliación. **Sin baseline dinámica ni Pyright; B05/A-05/A-06/C abiertos**, CI sin Docker requerido. |
| 2026-11-15 | **B05-Q1 — ejecutor focal listo en clon Git independiente, sin pytest aún** | B05-R1/R2/R3, A-06 | [Runner PowerShell](run_b05_focal_isolated.ps1), [gate §10](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); commits \`ad8c90db\`, \`2d246698\`, \`944dd47b\`, \`51ef7cb8\` | Cuatro nodeids explícitos, clon sin hardlinks, SHA fijado, DB temporales/in-memory, snapshots Git pre/post y logs, sin Docker ni CI nuevo. Eliminado estimador \`tiktoken\` no necesario en dos tests para evitar dependencia de caché/red. **No ejecutado desde esta sesión**, sin PASS ni Pyright acreditados. |
| 2026-11-15 (23:31 AR) | **Primer testigo dinámico focal B-05: 4/4 PASS, sin diferencias Git post** | B05-Q1, A06 focal | [Gate §11](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); owner ejecutó runner sobre SHA `73572285f99c5556691fe91ee56b633cba5a5ffe` | `summary.txt`: `pytest_exit_code=0`, `docker_used=false`, sin sandbox de SO declarada; salida pytest `4 passed in 2.62s`; `status_changes.txt` vacío según owner. **Evidencia dinámica focal** pero no asegura side effects transitorios, no completa B-05/A05/A06 global, no demuestra mutation kills ni Pyright/CI. |
| 2026-11-16 | **B05-Q2 — 2/2 mutaciones KILLED, Pyright explícito 0 errores** | B05, C-00/C-07 preliminar | [Gate §13](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); owner ejecutó en clon sobre SHA `ffd702535a079f37cff87659792ae86a98b40cad`; RAR con JSON y 2 logs leídos en la conversación | Baseline previa exit 0; watchdog no-op: assert `PROCESSING != STALLED`, pytest exit 1/1 failed; cache siempre MISS: fake invocado 2 veces, assert 2 != 1, exit 1/1 failed. `mutation_summary.json`: `TWO_KILLED`. Pyright local sobre 4 archivos: **0 errors, 0 warnings, 0 informations**. No CI ni mutation coverage global acreditados; A05/A06/C global abiertos. |
| 2026-11-16 | **B-01/B-02 — baseline focal exit 0, Pyright local 0; sensibilidad diseñada** | B-01/B-02, C preliminar | [A03 §8](A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md); owner sobre SHA `edcc02f2e982506aba953ad888f21e5a18d27b41` | Runner `-CheckB01B02` sobre cuatro nodeids seleccionados en clon nuevo: `pytest exit code: 0`; Pyright explícito dos archivos: `0 errors, 0 warnings, 0 informations`. Sin log completo/status Git recibido. Se preparó en SHA posterior `probe_b01b02_sensitivity.py`: parser pierde frase conocida y chunker altera un espacio, con marcadores de aserción específicos. **0 mutaciones B01/B02 acreditadas hasta ejecución del owner.** GT, snapshots y producción intactos. |
| 2026-11-16 | **B-01/B-02 — TWO_KILLED según JSON del owner** | B-01/B-02, C-01/C-07 focales | [A03 §9](A03_PREAUDITORIA_ORACULOS_GOLDEN_Y_CHUNKER_SNAPSHOT.md); `b01b02_mutation_summary.json` compartido en conversación; SHA `5a537c9512b8ec1cb37dd2ac0022587daccf0d0d` | `parser_text_loss` y `chunk_source_byte_loss`: ambos `MUTATION_KILLED`, exit 1, marcadores `B01_KNOWN_SOURCE_TEXT_MISSING` / `B02_SOURCE_BYTES_MISMATCH`. El helper exige una sola falla por aserción con marcador y no error de infraestructura. **Logs individuales no recibidos**, atribuir como informe del verificador, no inspección directa; C general y CI siguen abiertos. |
| 2026-11-16 | **A02/A03/B06 — revisión focal G3/G5 y runner preparado, sin baseline nueva** | A-02/A-03/B-06, C-03/C-04/C-05 pendientes | [Matriz G3/G5](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md); commits `9994106f`, `31d546d5` | 7 testigos nominales, 9 nodeids esperados: W06 UNKNOWN/restart, publicación/deriva G3, fencing/recovery G5. SQLite temporal/fakes, no Docker. **Sin pytest ni Pyright nuevo del SHA, sin mutation kills G3/G5, sin resultados CI**. |
| 2026-11-16 | **G3/G5 baseline 9 PASS; C-03/C-04/C-05 preparadas, sin mutaciones ejecutadas** | A-02/A-03/B-06 focal y C-03/C-04/C-05 | [Matriz §6](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md), owner `reports.rar`, SHA `78f36678918535d3525287d1e3c9866dff5fe43e`; commits `da51a2f`, `cea3905`, `446cfe6`, `82748b7`, `5390090` | Inspección directa del RAR: `9 passed, 2 warnings in 3.31s`, exit 0, `status_changes.txt` vacío; Python 3.11/Google deprecated warnings registrados. Se añadieron tres mutaciones en memoria tras baseline verde sobre un clon, sin tocar runtime/CI/GT ni Docker. **0 mutation kills G3/G5 hasta ejecución; CI y gates globales abiertos.** |
| 2026-11-16 | **C-03/C-04/C-05 — THREE_KILLED por reporte del owner** | C-03/C-04/C-05, C-07 focal | [Matriz G3/G5 §7](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md), JSON `g3g5_mutation_summary.json` copiado en conversación; SHA `16a6822927ffc0b11caa84faf406c083fa0b15fd` | Tres casos con exit 1 y `MUTATION_KILLED`: reintento G3 incierto, proyección G3 alterada, publicación G5 con lease caducado. La herramienta exige marcador propio y un `1 failed` de aserción. **Logs individuales no revisados; no inferir mutation coverage global ni CI verde.** |
| 2026-11-16 | **B-03 — parser real: 1 PASS, Pyright 0, clon sin diferencias** | B-03 / A03-E2E-04 | [Expediente §6](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md); owner SHA `f713eafc83ea24abdcba040d0f4871b2c3c2df73` | `-CheckB03Parser`: `1 passed in 1.69s`, exit 0, `status_changes.txt` vacío según owner, Pyright sobre archivo 0 errores/0 warnings; no Docker. Prueba extracción real de PDF temporal dos páginas; **no prueba E2E ni sensibilidad B-03 o CI HEAD**. |
| 2026-11-16 | **B-04 — 8/8 PASS, Pyright focal 0, Git clon sin diferencias** | B-04 / A03-E2E-05/06 | [Expediente §7](A03_A05_TESTIGOS_E2E_Y_RIESGOS_DE_EJECUCION.md); owner SHA `41e5146fb223c803218909b5561921a1b0173e99` | Runner `-CheckB04Contracts`: `8 passed in 0.47s`, `pytest_exit_code=0`; Pyright de dos archivos 0 errores/advertencias; `status_changes.txt` vacío según owner; sin Docker. Tres contratos de LaTeX/enums y cinco de healing/telemetría; **no E2E, no mutaciones B-04, no CI acreditado; gates A/B/C abiertos**. |
| 2026-11-16 | **A-01/A-04 — colección HEAD conciliada: 1.476, 14 bajas/16 altas, CI fuente sin cambios** | A01-RC-HEAD, A04-SELECTORES | [Informe del HEAD](A01_A04_RECONCILIACION_HEAD_2026-11-16.md); owner reportó `collect_a01_isolated.py` y `a01_head_reconciliation.json`, SHA `5447963d1c2dbce257d94aede30baabb11bd9f98` | `all=1476`, `unit=225`, `integration_nonregression=72`, `technical=1456`, colección exit 0×4; 1.460 IDs compartidos, 14 antiguos eliminados, 16 nuevos, +2 netos explicados por B-02, 0 cambios de markers/param en IDs comunes. 12 rutas CI explícitas = 138 nodeids sin cambios. **Solo colección, no PASS de suite ni ejecución de CI; A-01/A-04 y A-05 globales abiertos.** |
| 2026-11-16 | **A-03 — 39/39 PASS y Pyright 0; dos falsadores preparados, pendientes** | A-03 / OI-G3-04 / TS-006 / C | [A03-G3 §7](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md); owner SHA `50ec05509d095036f883c61ad1149843391fd64e` | `39 passed in 2.56s`, exit 0, status Git clon vacío según owner, Pyright 0 sobre los dos módulos. Incluye UTF-8 multibyte y las dos frases PDF. Se añadió `probe_a03_sensitivity.py` con 2 mutaciones SUT in-memory tras baseline obligatoria `-CheckA03Sensitivity`; **ningún KILLED nuevo hasta ejecución**. CI y A03/A04 global abiertos, sin runtime/GT modificados. |
| 2026-11-16 | **A-03 — TWO_KILLED inspeccionados directamente** | A-03 / OI-G3-04 / C focal | [G3-B3 §8](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md); `reports.rar` leído íntegramente, SHA `83f99ddb0abadf216d8e051619aa05f9c73cfc77` | Baseline nueva `39 passed in 1.40s`, exit 0; dos fallos contractuales: byte cap Unicode `DID NOT RAISE`, parser pérdida de texto `B02_EXTRACTED_SOURCE_TEXT_MISSING`; cada mutante exit 1/`1 failed`, `TWO_KILLED`; `status_changes.txt` vacío, no Docker. **No CI ni mutation coverage general**. |
| 2026-11-16 | **FG-NEG-01/02 — falsadores del coordinador CLI preparados, no ejecutados** | TR-031 / NC-06 parcial | [S5 segunda tanda §7](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md); `probe_foreground_sensitivity.py` y `-CheckForegroundSensitivity` | Dos nodeids existentes: G3 incompleto no debe ejecutar G5; G5 sin PDF no debe reportar éxito. Mutación SUT en memoria, baseline verde previa obligatoria en clon. **0 KILLED FG hasta recibir logs; no E2E OCR→G3→G5 ni runtime/CI/GT modificado.** |
| 2026-11-16 | **FG-NEG-01/02 — TWO_KILLED con ambos tracebacks directamente inspeccionados; baseline 2 PASS** | TR-031 / NC-06 focal | `reports.rar` inspeccionado (6 miembros), SHA `e2d2fd5f64165357b8c9e2dbf25f23139a04c351`; [S5 §9](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md) | `2 passed in 0.62s`, pytest exit 0, sensibilidad exit 0; mutante G3 incompleto: `Failed: DID NOT RAISE`, `1 failed in 0.64s`; mutante PDF ausente: `Failed: DID NOT RAISE`, `1 failed in 0.69s`. Ambos exit 1 y `MUTATION_KILLED`; `status_changes.txt` vacío en el clon. **Evidencia directa, no E2E ni CI, sin sandbox OS; A/B/C globales abiertos**. |
| 2026-11-16 | **CLI-NEG-01/02 — TWO_KILLED confirmados por dos tracebacks y baseline de 8 PASS** | A-03/A-04 CLI / NC-06 focal | [S5 §10](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md); `reports_1.rar` leído (7 archivos), SHA `b147625064644041ac6f07f2eda5c6df061cb8b4` | `8 passed in 0.81s`, pytest exit 0, `TWO_KILLED`, sensibilidad exit 0. No fallback no atómico: `DID NOT RAISE`, 1 failed; R1: `AssertionError: R1 must not execute`, 1 failed. `status_changes.txt` vacío, no Docker. **Evidencia focal directa, no suite/CI global**. |
| 2026-11-16 | **TR-022 — G5 worker TWO_KILLED con ambos tracebacks, baseline 3 PASS** | A-03/A-04 G5 / C focal | [S5 §12](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md); `reports.rar` 7 miembros directos, SHA `97a1bbef6cd7ac798dd6bcb151afe7a2154ea6bc` | `3 passed in 1.20s`, exit 0, sensibilidad `TWO_KILLED` exit 0; mutación lease vencido: `DID NOT RAISE` y log `G5_ASSEMBLER_PDF_PUBLISHED`; fallo de compilador sin registro: FSM `COMPILING` en vez de `FAILED_RETRYABLE`. Ambos exit 1 / 1 failed, Git clon vacío, no Docker. **No E2E, CV, CI o cobertura general acreditados.** |
| 2026-11-16 | **TR-023 — C3/T05 proceso real crash/recovery: 1 PASS, Pyright 0, Git clon vacío** | A-03/A-04 / TR-023 | [S5 §12](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md); RAR del owner (3 miembros), SHA `d159271502a8f3b3bedac674b5f9ff8f1a7395ef`, selector `-CheckC3T05Process` | `pytest_focal.log`: `1 passed in 1.64s`; `summary.txt`: `pytest_exit_code=0`, `c3_t05_process_requested=True`, `docker_used=false`; `status_changes.txt` **0 bytes**; Pyright explícito sobre el archivo: `0 errors, 0 warnings, 0 informations`. Proceso hijo termina con `os._exit(73)`, segundo recupera SQLite y tercer lector verifica persistencia; **no mutation kill nuevo, no E2E/CI, sin sandbox OS**. La prioridad siguiente es **consolidar A-02/A-04/A-07 y brechas P0**, no ampliar runners o mutaciones sin hallazgo nuevo. |
| 2026-11-16 | **A-02 — trazabilidad de las ocho fronteras §2.4 completada; cierre formal pendiente** | A-02 / TR-001–035 | [Matriz A-02 §9](A02_A03_B06_MATRIZ_G3_G5_RUTA_ACTIVA.md) y [TR primera/segunda tandas](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md) | 8/8 fronteras mapeadas con SUT real, testigos positivos/negativos, oráculos y evidencia por SHA; pendientes explícitos de CI, A-04, A-07 y D-4/D-5 diferidos. **Sin scripts ni tests nuevos; ninguna garantía general declarada PASS.** |
| 2026-11-16 | **A-03/A-04 — clasificación focal de 35 TR terminada, globales abiertos** | A-03/A-04 | [Matriz semántica §7](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), sobre 35 fichas históricas y evidencias focales por SHA | 7 `CONFIABLE_PARA_SU_ALCANCE` para subcontratos realmente ensayados; 9 `LIMITADO`; 19 `DESCONOCIDO` en ejecución focal; 0 defectuosos **nuevos** probados dentro de estas 35 fichas. TS-001/TS-002 P0 históricos remediados. **No extrapolar a 1.476 nodeids/CI.** No se añadieron tests, scripts, mutaciones ni cambios de runtime/GT; quedan A-03/A-04 globales abiertos. |
| 2026-11-16 | **A-04 — delimitación histórica: 1.474 nodeids, 8 archivos sin TR clasificados por familia y 5 fuentes nuevas inspeccionadas** | A-04/A01-S5 | [Matriz semántica §8](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md); colección histórica `86cd6867` y HEAD leído en `tests_stabilization` | Partición histórica **277 + 33 + 76 + 97 + 30 + 961 = 1.474**; 173 archivos con nodos. Ocho fuentes sin TR (**236**) tenían revisión por familia; otras cinco fuentes sin TR clasificadas ahora por lectura, **sin conteos nuevos**. Se corrigió referencia histórica al riesgo `test_recovery_flow.py`: HEAD actual usa DB temporal, pero pipeline legacy mockeado. **961 sin SUT clasificado en censo histórico; A-04 no cerrado, no nuevos tests ni CI.** |
| 2026-11-16 | **A-04 — segunda tanda, 26 fuentes con tests clasificadas por alcance; riesgos legacy documentados** | A-04/A-05/A-07 por preparar | [Matriz semántica §9](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md); lectura directa del HEAD `tests_stabilization` | 10 archivos de ruta/apoyo activo, 8 técnicos/auxiliares y 8 legacy/ciencia; adicionalmente 3 root vacíos y 1 script manual sin test pytest. Hallazgos concretos: `test_tectonic_runner.py` borra log de CWD; dos suites legacy usan `infra/db/documents.db`; `test_translation_layer.py` escribe en `tests/fixtures`; `test_translation_semantics.py` calcula coseno 1 con embedding constante; SKIPs y guard transaccional G2 aún no ejecutado. **Sin recuentos nuevos de nodeids, PASS ni defectos productivos demostrados. Ningún test/script/runtime/CI/GT editado.** |
| 2026-11-16 | **A-04 — mapeo por archivos 173/173 completo, sin cierre por nodeid** | A-04 | [Matriz semántica §10](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), árbol Git `b8a669f95eaacf271bc74c24200b0523aa32c1c1` | 29 archivos con TR + 8 históricos sin TR + 31 clasificados en §§8–9 + 105 de última tanda = **173 archivos con tests**. Última tanda: 36 operativos/compartidos, 9 legacy, 4 lab offline y 56 ciencia/GT/CV. **Sin pytest/Pyright/CI nuevo, sin estimar cuántos nodeids corresponden a cada familia**; A-04 global abierto hasta cruce exacto con `all.json`. Sin SUT ni GT alterados. |
| 2026-11-16 | **A-04 — RAR del owner conciliado: 1.476/1.476 nodeids asignados por archivo/familia** | A-04 / identidad→alcance | [Matriz A-04 §11](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), `all.rar` con `all.json` y `all.log`, sin `manifest.json` | 173/173 archivos, 8 grupos exhaustivos y disjuntos: 277+236+13+172+165+20+54+539=1476; selector técnico=1456, E2E=20. **Cruce literal de identidades completado; NO acreditada eficacia de todos los oráculos, ejecución de tests ni CI del HEAD actual.** RAR carece de SHA incorporado; coincidencia con la colección `5447963d` previamente reportada. Ninguna modificación a tests/SUT/GT. |
| 2026-11-16 | **A-04 — aplicado §5.1: revisión por función y parametrización material, sin 1.476 fichas** | A-04 / umbral acordado | [Matriz A-04 §12](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), `all.json` del owner, sin SHA propio; 35 TR existentes | Entre 29 archivos TR, **277 nodeids = 229 funciones**; **19 funciones parametrizadas suman 67 casos** y 48 variantes extra. Identificadas dimensiones independientes de lease, FSM, manifest, owner, W08 y matemáticas; casos críticos sin evidencia K permanecen limitados/desconocidos, no promocionados. Mapeo de alcance completo, eficacia global NO acreditada; **gate A-04 formal aún abierto**. Sin tests/scripts/CI/runtime/GT nuevos. |
| 2026-11-16 | **A-04 — diecinueve TR críticas reclasificadas con SUT/oráculo, sin añadir tests** | A-04 / clasificación bajo §5.2 | [Matriz A-04 §13](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), lectura de testigos G3/W08/G5 | Las 19 fichas `DESCONOCIDO` en cobertura focal pasan a `LIMITADO` por SUT real/oráculos existentes, pero sensibilidad/alcance parcial. Balance **7 focales confiables + 28 limitadas + 0 desconocidas** en 35 TR; no es PASS global. **P1 TR-007:** un caso de output no ligado solo exige `ValueError` genérico; requiere evaluar motivo contractual, no corregir producción automáticamente. Riesgos de borrado CWD/DB legacy a A-05. Entregable documental A-04 completo, **checkbox pendiente de revisión del owner**, sin ejecutar pruebas ni modificar SUT/CI/GT. |
| 2026-11-16 | **A-04 cerrado documentalmente por decisión del owner; A-05 actualiza riesgos de I/O y bloquea suite amplia** | A-04 [x], A-05 [ ] | [Matriz §13](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md), [A-05 §14](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); aceptación explícita del owner | A-04: 7 TR fiables solo para alcance focal, 28 limitadas, 0 desconocidas; 1.476 nodeids mapeados, sin equivaler a PASS. A-05: pendientes `tectonic_crash.log` (CWD), `documents.db` (2 setups legacy), SQLite en `tests/fixtures`, import/egress OS; bloqueo de `pytest -m "not e2e"` en working tree. **Sin nuevas pruebas, cambio runtime/CI/GT ni afirmación de aislamiento OS.** |
| 2026-11-16 | **A-05 — tres riesgos de escritura corregidos en cuatro tests existentes; ejecución pendiente** | A-05/seguridad de tests | [A05 §15](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); autorización expresa owner | `test_tectonic_runner.py`: CWD temporal, sin borrar log ajeno, excepción verificada; `test_translation_structure.py` y `test_translation_technical.py`: SQLite en memoria y cleanup; `test_translation_layer.py`: caché SQLite/WAL en TemporaryDirectory y cleanup. Diff restringido a 4 tests + documentación, sin SUT/CI/GT. **0 nuevos tests ejecutados/0 nuevos PASS acreditados**; siguiente solo validación focal de 9 nodeids y Pyright explícito. A-05/A-06/CI globales ABIERTOS. |
| 2026-11-16 | **A-05 — focal 7 PASS/2 SKIP, Pyright 0, Git persistente limpio; P4/P6 abiertos** | A05-FS/DB | [Expediente A05 §17](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); RAR owner, SHA `6ecfc2c5726b86c5df91a839c232e73bcee52f82` | `a05_safety_requested=True`, `pytest_exit_code=0`, `7 passed, 2 skipped in 7.73s`; dos SKIP legacy por golden ausente no son PASS. Pyright explícito 0/0/0 en cuatro archivos, `git_before`, `git_after` y `status_changes` vacíos, no Docker. Tres riesgos concretos mitigados y comprobados focalmente; falta egress/plugins/import hooks, I/O transitorio/externo y CI HEAD, sin suite global ejecutada. |
| 2026-11-16 | **A-05 — test Groq opt-in explícito y guardia negativa añadida; nueva baseline pendiente** | A05-NET-01 | [A05 §18](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md), `test_embedding_smoke.py` + selector `-CheckA05Safety` | Smoke real ya no construye Groq solo por `GROQ_API_KEY`: exige `TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS=1`; control negativo sintético verifica `SkipTest`/`GroqProvider.assert_not_called()` con clave falsa y opt-in 0. Runner fuerza opt-in 0; 11 nodeids esperados (9 previos+2), **ningún PASS nuevo todavía**. No CI/runtime/GT ni prueba de no-egress a nivel SO. |
| 2026-11-16 | **A-05 — guard Groq y cuatro correcciones previas: 8 PASS/3 SKIP, Git clon limpio** | A05-P4/P6 focal | [Expediente A05 §19](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); owner RAR5 con `pytest_focal.log`, `summary.txt`, Git antes/después/status; SHA `65385307e11cc2db8795c3e6c6343d94ef9d2bdd` | `8 passed, 3 skipped, 2 warnings in 11.34s`; pytest exit 0, Pyright 0, tres inventarios Git vacíos. SKIP por golden estructural/técnico ausente y smoke Groq no habilitado; guard sintético de no-egress PASS. Las dos warnings de Google no afectan el conteo. **Evidencia de 11 casos, no suite técnica completa, CI, egress OS o efectos transitorios externos acreditados.** |
| 2026-11-16 | **A-05 P4/P6 — preflight metadata-only preparado, todavía NO ejecutado** | A05-P4/P6 → A06 | [Expediente A05 §20](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md) y `run_b05_focal_isolated.ps1` | Nuevo switch opt-in `-PreflightA06` del runner existente: clona SHA sin ejecutar pytest, registra entrypoints de plugins/versiones e inventario SHA-256 de `tests/fixtures`, `tests/golden`, `infra/db`; `-CaptureProtectedPaths` aporta comparador opcional pre/post con exit 5 para futuros tests focales. **No acredita plugins realmente cargados, egress OS ni I/O transitorio/externo**, y no autoriza suite global. Sin scripts nuevos ni SUT/CI/GT alterados. |
| 2026-11-16 | **A-05 P4/P6 — preflight exitoso: 5 plugins anunciados, 30 archivos protegidos; A-06 collect-only preparado** | A05-P4/P6 → A06 colección | [Expediente §22](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); owner `reports.rar` (5 miembros) SHA `c5277184de665f0aab416405cf31c3282c1243df` | `pytest=9.0.3`, `pytest_asyncio=1.5.0`, cinco entrypoints anunciados, 12 fixtures+18 infra/db hashes, 0 golden, Git antes/después vacío. **0 cuerpos de test y 0 colección** ejecutados en este preflight. Reutilizado `collect_a01_isolated.py` para `--trace-config`, snapshots protegidos pre/post y guard socket/credenciales; **colección del HEAD aún pendiente**, no egress OS/P6 global certificados. |
| 2026-11-16 | **A-06 colección 1.478 con fail de seguridad por 271 archivos Hypothesis ignorados; corrección de caché preparada** | A05-P4/P6 y A06-collect | [A05 §23](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md), owner RAR5 de 14 archivos, SHA `cffc57f270cbb1bd5ca4fa4d1955518b72a003e5` | Cuatro selectores colectaron `1478/225/72/1458` y exit 0 sin cuerpos; trazas identifican plugins cargados, snapshots 30/30 iguales (`protected_file_changes=[]`); `git_after` contiene exclusivamente 271 `!! .hypothesis/`, `git_before` vacío. **Gate FAIL legítimo**, no contaminación de fixtures/GT. Recolector original fija `HYPOTHESIS_STORAGE_DIRECTORY=scratch/hypothesis`; **sin revalidación todavía**, no PASS dinámicos, suite/CI/global y aislamiento SO abiertos. |
| 2026-11-16 | **A06-COLLECT — revalidación limpia; primer subconjunto W08/G3 preparado** | A05-P4/P6 / A06 | [Expediente §24](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); RAR del owner con 5 archivos, SHA `d754a56c19810f39e29e6ec485e948039b1ec686` | 1.478 all/225 unit/72 integration/1.458 technical, cuatro exit 0, 30/30 hashes protegidos iguales, 0 efectos Git persistentes: resuelto el side effect `.hypothesis` en esta colección. **No se ejecutaron cuerpos**; logs de plugins actuales no aportados. Selección nueva `-CheckA06W08 -CaptureProtectedPaths` en runner previo: tests de contexto/identidad y prohibición de caché legacy G3; **sin resultados aún**, global/egress OS/CI abiertos. |
| 2026-11-16 | **A06 — 23 W08/G3 PASS con hashes/Git intactos; siguiente cohorte G3 de 20 casos preparada** | A-06 focal | [A05 §25](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md), owner RAR5 de 8 archivos, SHA `13ae7e5da9974b5b7c6d4696edbf6b98115d239e` | `23 passed, 2 warnings in 3.50s`, pytest exit 0, no FAIL/SKIP, mutaciones no ejecutadas, 0 bytes en `git_before`, `git_after`, `status_changes` y `protected_changes`; SHA-256 de `protected_before/after.tsv` idénticos. Siguiente selección opt-in del runner, **no ejecutada**: 14 nodeids fencing G3 + 3 PRESERVE + 3 cuotas SQLite hilo, todos con DB in-memory/tmp_path y proveedores fake; `-CheckA06G3Guards -CaptureProtectedPaths`. No suite global, CI, GT ni aislamiento OS acreditados. |
| 2026-11-16 | **A06 — 20 G3 PASS (fencing/PRESERVE/quota) con Git y 30 hashes intactos; total 43 nuevos PASS** | A-06 focal | [Expediente A05 §26](A05_GATE_A06_AISLAMIENTO_Y_REMEDIACION_B05.md); owner RAR5 de 8 informes, SHA `0b5fd88f95e7f5e97b63f9c2cbef8c3eb76c731b` | `20 passed, 2 warnings in 3.39s`, exit 0, 0 FAIL/SKIP, 14 nodeids fencing + 3 PRESERVE + 3 cuotas de hilo SQLite; `git_before/after`, `status_changes` y `protected_changes` vacíos, 30 SHA-256 pre/post idénticos, sin Docker/mutaciones. Sumados a 23 W08 en SHA previo = **43 PASS distribuidos por SHA**, no CI real ni baseline global. Próximo paso: reconciliar CI vs nodeids ya acreditados y riesgos de los huecos, antes de otra selección o A-07. |

| 2026-11-16 | **A-06↔CI y A-07 preliminar: reconciliación documental sin pytest** | A-06/A-07 | [Matriz §6: A-06 → A-07](#a-06--a-07--conciliación-de-ci-y-matriz-preliminar-de-brechas), `ci.yml`, A05 §§24–26 y A-02 §9; HEAD `f7d5653b` | 12 archivos explícitos = 138 nodeids: 20 PASS A06 + 7 PASS históricos identificables (4 W06/G3 y 3 G5) + 111 sin baseline focal individual en la evidencia consultada; W08 A06 23 PASS por `unit`. 225 unit, 72 integration, 1.458 not-e2e y 435 reejecuciones potenciales. **Cero CI real nuevo, ningún nuevo PASS ni P0 productivo.** A05-P4/P6, A06 y A07 abiertos, matriz P1/P2 pendiente de aceptación del owner. |


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