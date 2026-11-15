# A01-S5 — Evidencia real de puente por nodeids, priorización y alcance

> **Estado:** **S5-N4 COMPLETADO** (partición por archivos), **S5-N5/N6/N7 EN CURSO** (trazabilidad semántica, oráculos y clasificación de ámbito). **NO** se completó la auditoría de 1.474 tests: **0 nodeids acreditados semánticamente**. A01-S5, A-01 y A-05 globales permanecen abiertos.
>
> **Fecha:** 2026-11-15. **Fuente primaria:** salida JSON aportada por el owner tras ejecutar [`map_a01_s5_nodeids.py`](map_a01_s5_nodeids.py) sobre los mismos `all.json/manifest.json` de SHA `86cd68672ee692f073b62869e7c9bd177e8d9e3b`. **HEAD de la corrida local:** `78af6ec9a4a8edf124f63e1ca22e9c71bb193259`. Los JSON privados siguen locales; los recuentos provienen de la salida facilitada, no de ejecución nueva de pytest.
>
> **Revisión adicional:** inspección directa de ocho fuentes en el SHA congelado, acotada a SUT, imports, llamadas y aserciones. Las inferencias de ámbito son **provisionales por archivo**, no verificaciones de cada nodeid ni PASS.

## 1. Partición reproducible del inventario recolectado

| Métrica | Recuento | Significado estricto |
|---|---:|---|
| `all`: nodeids recolectados/únicos | **1.474 / 1.474** | Colección real anterior, **cero cuerpos ejecutados aquí** |
| Fichas documentadas | **35** | Contratos/fronteras con testigos, **no** 35 tests independientes |
| Archivos distintos vinculados a fichas | **29** | Archivo candidato revisado; **ninguna acreditación automática del resto de sus funciones** |
| Nodeids que pertenecen a esos 29 archivos | **277** (18,8 %) | **277 candidatos a cotejo función/contrato**, no tests semanticamente acreditados |
| Archivos restantes con nodos | **144** | Aún sin vínculo TR por archivo; 144 + 29 = 173 fuentes con nodeids |
| Nodeids de esos 144 archivos | **1.197** (81,2 %) | Pendientes de clasificar; **no** son 1.197 brechas del pipeline |
| Sin marker de nivel en los 29 archivos documentados | **235** | Marca de nivel ≠ presencia en CI |
| Sin marker de nivel en los 144 archivos restantes | **924** | Total `235 + 924 = 1.159` |
| Nodeids individualmente acreditados | **0** | La herramienta **no** evalúa aserciones ni oráculos por nodeid |
| Alertas confirmadas por lectura de fuente | **4 archivos / 4 nodeids** | Problemas semánticos estáticos: 2 falsas garantías, 2 desajustes de alcance |

**Checks del analizador:** `all_unique=true`, `partitions_add_to_all=true`, `group_partition_adds_to_all=true`, `all_35_TR_mapped_to_existing_files=true`, `no_tests_changed_from_collection=true`. Este último comprueba solo archivos **versionados** bajo `tests/` por diferencias Git, no detecta untracked/ignored ni prueba seguridad de imports a nivel SO.

**Invariante:** **277 + 1.197 = 1.474**; **29 + 144 = 173**; **235 + 924 = 1.159**. La clasificación preliminar de ocho archivos que sigue **no cambia la partición registrada**; siguen sin TR hasta que se creen fichas explícitas por función/contrato.

## 2. Triaging dirigido de los archivos más poblados sin ficha

Se inspeccionaron directamente las siguientes fuentes, todas existentes en el mismo SHA pinneado. De la salida local se tomaron exactamente los nodeids por archivo.

| Archivo sin TR actual | Nodos | Sin marker nivel | Ámbito provisional | Evidencia de SUT y límite real | Acción razonable |
|---|---:|---:|---|---|---|
| [`tests/unit/test_criticality_verdict.py`](../../../../tests/unit/test_criticality_verdict.py) | **40** | 40 | **CIENCIA/TOOLING — diferido** | SUT `core.benchmark.topology.criticality.*`; políticas de falso negativo crítico, warning e info, no daemon PDF→PDF | No usar como prueba de salida física PDF; conservar contrato de gobernanza de clasificación |
| [`tests/integration/test_g3_b3_structured_result_contract.py`](../../../../tests/integration/test_g3_b3_structured_result_contract.py) | **33** | 33 | **ACTIVA — G3, alta prioridad** | `parse_chunk_response` y `materialize_node_results`, AST/ChunkPlan reales y sintéticos; 17 casos de mutación de miembros y 6 de JSON inválido | Proteger orden por identidad, respuesta vinculada a generación, preservación de bytes, límites de respuesta y rechazo sin completar parciales; sin provider ni DB |
| [`tests/unit/test_corpus_models.py`](../../../../tests/unit/test_corpus_models.py) | **30** | 30 | **CIENCIA/GT — diferido** | `core.benchmark.corpus.models` y DTO de documentos/estado GT; valida invariantes de metadatos | No confundir con AST del pipeline ni modificar corpus/oráculos |
| [`tests/unit/test_cv_workflow_contract.py`](../../../../tests/unit/test_cv_workflow_contract.py) | **30** | 0 | **GOBERNANZA DE CI/CV — no SUT PDF→PDF** | Lee workflows YAML, valida `run_regression`, perfiles y gates; `pytest.importorskip('yaml')` es condición de colección/importación distinta de un test PASS | Clasificar como contrato de workflow; no ejecutar CV científico, preservar en auditoría de selección CI |
| [`tests/unit/test_math_normalizer.py`](../../../../tests/unit/test_math_normalizer.py) | **30** | 30 | **TÉCNICA COMPARTIDA — matemática** | Invoca `MathDomainNormalizer` real con strings independientes; casos de verbatim, delimitadores, errores y idempotencia | No inferir que el normalizador se invoca desde el root soportado sin trazar esa integración |
| [`tests/unit/test_ast_models.py`](../../../../tests/unit/test_ast_models.py) | **28** | 28 | **TÉCNICA COMPARTIDA — dominio AST** | Invoca `core.ast.models.ASTNode`/payloads; valida node_id/parent, inmutabilidad y lineage | **Sí es dominio AST real**, pero no parser físico ni prueba E2E; no confundir con `test_corpus_models.py` |
| [`tests/unit/test_verification_outcome.py`](../../../../tests/unit/test_verification_outcome.py) | **27** | 0 | **CIENCIA/GOBERNANZA — diferido** | Importa `core.benchmark.verification.outcome`; comprueba estados, exit codes y prioridad de fallo | No ejecutar certificación ni usar como prueba de la ruta PDF→PDF |
| [`tests/unit/test_text_render_strategy.py`](../../../../tests/unit/test_text_render_strategy.py) | **18** | 18 | **TÉCNICA COMPARTIDA — TeX/render** | `TextRenderStrategy`/`LatexEscaper` reales, entradas y esperados literales, unittest.TestCase | No implica Tectonic real ni PDF final; conservar invariantes matemáticas/escaping |

Las **ocho fuentes** examinadas suman **236 nodeids**, pero **NO deben sumarse a los 277 como acreditados**: su clasificación es por archivo y está aún pendiente de vinculación nodeid→función→TR, sin PASSED ni mutation kills. Varios ficheros del listado Top-18 siguen **sin inspección en esta tanda**; la etiqueta de «PENDING_REVIEW_NO_TR_FILE_EVIDENCE» es correcta para ellos.

### Corrección de atribución que conviene preservar

- `test_ast_models.py` **sí prueba** el dominio AST real: creación y validación `ASTNode`, IDs, fragmentos e inmutabilidad. No prueba el parser físico.
- `test_corpus_models.py` y `test_criticality_verdict.py` prueban modelos/garantías de **benchmark y corpus/GT**. No adjudicar esos tests al pipeline técnico por el volumen.
- `test_cv_workflow_contract.py` prueba **la estructura del CI/CV** y usa `pytest.importorskip('yaml')`. Su pertenencia a la colección no significa que un job científico haya sido ejecutado o certificado.

## 3. Prioridad de análisis de independencia por familia

### P0 — respuestas estructuradas G3 no vinculadas todavía a las 35 fichas

Archivo [`test_g3_b3_structured_result_contract.py`](../../../../tests/integration/test_g3_b3_structured_result_contract.py), **33 nodeids / 12 funciones declaradas**. El SUT realmente llamado incluye `parse_chunk_response` y `materialize_node_results` de `core.chunking.result_contract`, con `ChunkPlan` real construido sobre AST sintético; **sin proveedor, SQLite, daemon o PDF físico**. Hay valores esperados literales en el código (por ejemplo, orden por `node_id`, texto traducido, hash SHA-256 calculado sobre texto **fijo**), 17 variantes de mutaciones de miembros y seis de JSON inválido.

**Diagnóstico preliminar:** contrato técnico de alto valor, expresado en funciones puras y negativas; **no es oráculo tautológico evidente en sus positivos** porque varios expected son literales, pero hay que revisar las mutaciones y la independencia de cada expected. La función helper `_response` deriva ciertos bindings del `ChunkPlan` construido por el mismo dominio: eso es válido para inputs consistentes, **no** demuestra por sí solo cobertura ante todos los defectos correlacionados del plan y parser.

**Falsadores para A-03/C:** orden posicional en lugar de identidad; permitir miembros duplicados/extra/ausentes; ignorar `ast_hash`/manifest/chunk; devolver nodos incompletos; perder espacios delimitadores. Confirmar en la siguiente ronda las 33 variantes por nodeid sin pedir otra colección.

### P1 — dominio AST y salidas TeX/math de la ruta compartida

- `test_ast_models.py` — **28 nodos**, SUT `ASTNode` y payloads; independencia de oráculo de validación de IDs, parent lineage e inmutabilidad. Contrato **de dominio**, no parser real.
- `test_math_normalizer.py` — **30 nodos**, `MathDomainNormalizer` real; comparaciones con strings literales, control de verbatim, math delimiters y errores. **No** se ha trazado si se usa en el entrypoint soportado.
- `test_text_render_strategy.py` — **18 nodos**, `TextRenderStrategy` y `LatexEscaper` reales; tests de escapado y math. **No** representa compilación física ni Tectonic.

**Separar** la validez de las reglas de dominio del cableado/efecto observable en el PDF final.

### Diferido / gobernanza (no descartar ni ejecutar ciencia)

- `test_criticality_verdict.py` — **40 casos**, política de criticidad/benchmark; fuera del análisis operativo de PDF→PDF.
- `test_corpus_models.py` — **30 casos**, corpus y metadatos GT; sin intervenir corpus ni GT.
- `test_verification_outcome.py` — **27 casos**, taxonomía/exit codes de evaluación y verificación; conservar, diferir certificación.
- `test_cv_workflow_contract.py` — **30 casos**, checks de rutas y triggers YAML. Distinto de ejecutar CV. Mantener en inventario de CI/alcance.

**No afirmar que «todo lo científico no entra en CI»:** la suite `not e2e` puede incluir estos tests; «diferido para remediación» describe el **alcance de la campaña**, no el selector técnico.

## 4. Hallazgos de calidad confirmados del primer puente (sin cambios)

| Archivo (un nodeid cada uno) | Dictamen por lectura | Decisión futura |
|---|---|---|
| `tests/integration/test_golden_parser.py` | `adapter.parse` parcheado y `expected_fingerprint = current_fingerprint`: **tautología** | B-01: oráculo técnico independiente, sin autogeneración/GT |
| `tests/integration/test_chunker_snapshot.py` | Si falta snapshot, lo **escribe y retorna**: comparación no obligatoria; valida solo parte de campos | B-02: prohibir auto-baseline en test, separar expected técnico congelado |
| `tests/integration/test_real_parser_pipeline.py` | `adapter.parse` parcheado: nombre «real parser» excede SUT ejercitado | B: acotar descripción o restaurar ejercicio real bajo PDF sintético |
| `tests/integration/test_real_e2e.py` | `pipeline.execute` parcheado: no comprueba integración real | B: reconducir a test de consumidor/FinOps con alcance honesto |

**Regla:** los dos primeros son **falsas garantías**; los dos últimos son **desajustes de alcance**. No declarar que los cuatro tests fallan, ni eliminar sus aserciones aprovechables por conveniencia.

## 5. Gates y próximos hitos

- [x] **S5-N4:** herramienta ejecutada por el owner; partición completa 1.474/1.474 verificada, 277 en 29 archivos testigo y 1.197 en otros 144.
- [x] **S5-N4A:** 1.159 nodos sin marker de nivel particionados 235+924; 4 alertas estáticas del analizador confirmadas.
- [x] **S5-N4B:** ocho archivos más poblados inspeccionados y **236 nodos priorizados por ámbito de archivo**, sin elevar ningún caso a confianza.
- [ ] **S5-N5 — avance estático:** ya se inspeccionaron **12 funciones y 33 escenarios de fuente G3-B3** con entradas, SUT y expected por caso; [matriz de auditoría](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md) y [verificador de nodeids](verify_a01_s5_g3_b3_nodeids.py). **Falta ejecutar cruce exacto de los sufijos de pytest, ampliar otros contratos y probar sensibilidad**; ninguna prueba corrió.
- [ ] **S5-N6 / A-03:** revisión dirigida de expected independientes y doble frontera en G3, math, AST y los dos falsos oráculos.
- [ ] **S5-N7:** clasificar resto por SUT sin confundir `not e2e` con ruta activa; evitar ciencia/GT.
- [ ] **A01-S5 / A-01 / A-05 globales:** **ABIERTOS**. No hubo ejecución de tests, mutation kills, pipeline físico ni cambios de producción.

**Siguiente decisión técnica:** priorizar los contratos de G3 y distinguir oráculo independiente de «same object» (digest/plan) antes de diseñar B. La estabilización debe proteger comportamientos normativos y minimizar la dependencia de helpers internos ante refactors, sin rebaseline automático.
