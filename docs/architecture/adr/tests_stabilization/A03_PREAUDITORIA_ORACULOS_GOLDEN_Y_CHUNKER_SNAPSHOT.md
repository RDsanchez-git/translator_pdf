# A-03 — Oráculos P0: golden parser y snapshot de chunker

> **Estado:** PREAUDITORÍA ESTÁTICA COMPLETADA de TS-001/TS-002 y control técnico relacionado. **A-03 GLOBAL, A01-S5, A-05 y B-01/B-02 PERMANECEN ABIERTOS.** No se ejecutó ningún cuerpo de test ni se modificó código, fixtures, snapshots, oráculos o GT.
>
> **Fecha de revisión:** 2026-11-15. **Código inspeccionado en `tests_stabilization`:** mismo árbol de tests fuente del SHA de colección `86cd68672ee692f073b62869e7c9bd177e8d9e3b`. Fuentes: [golden parser](../../../../tests/integration/test_golden_parser.py), [chunker snapshot](../../../../tests/integration/test_chunker_snapshot.py), [composición de extracción](../../../../apps/bootstrap/pipeline_factory.py), [chunker productivo](../../../../core/chunking/semantic_chunking.py), [test de parser real](../../../../tests/integration/test_verification_pipeline_connection.py), [test técnico zero loss](../../../../tests/unit/test_semantic_chunker.py) y [contratos G3 de chunk](../../../../tests/integration/test_g3_chunk_identity_contract.py). Se inspeccionaron además los archivos de referencia en el árbol Git y la forma de los dos JSON versionados. **No se ejecutó pytest ni extracción física.**
>
> **Alcance:** solo estabilidad técnica PDF→AST→chunks y veracidad de los tests; **NO** certificación científica, Ground Truth/corpus canónico, CV ni recalibración de parámetros. El snapshot técnico histórico no es evidencia GT.

## 1. Dictamen TS-001: falso «golden» del parser (P0 confirmado por fuente)

| Punto observado | Evidencia exacta | Consecuencia |
|---|---|---|
| Fixture PDF | `tests/integration/test_golden_parser.py:13,19–22`: si falta `tests/fixtures/sample_3_pages.pdf` escribe texto `%PDF-1.4 SOTA Dummy` bajo `tests/fixtures/` | **Side effect persistente latente**; no crear archivos de referencia dentro del test |
| Fixture fingerprint | Líneas 14 y 49–52: exige `tests/golden/sample_3_pages.fingerprint.json`, pero si no existe llama `skipTest` | Un gate obligado puede volverse SKIP en vez de detectar referencia ausente |
| **Árbol Git real** | PDF `tests/fixtures/sample_3_pages.pdf` **versionado** (2.045.076 bytes); **ningún archivo `tests/golden/...` ni `*.fingerprint.json` versionado** en el árbol revisado | En **checkout limpio** se esperaría el SKIP. **No se ha observado un SKIP de ejecución real**; un archivo local no rastreado puede cambiar el resultado |
| SUT sustituido | Líneas 57–69: crea un `ASTNode` manual y parchea `adapter.parse` con `patch.object(..., return_value=mock_nodes)` | **No ejecuta el parser físico**. La llamada `parse(self.pdf_real_path)` devuelve el mock |
| **Tautología del oráculo** | Líneas 71–75: lee JSON expected, pero después hace `expected_fingerprint = current_fingerprint` | Las comparaciones posteriores miden **el valor contra sí mismo**, por lo que no detectan una regresión del parser |
| Débil incluso sin tautología | Líneas 24–47: fingerprint contiene cantidad, distribución por tipo y secuencia de `type` y `len(content.strip())`; sin texto íntegro, posiciones, integridad de assets o geometría | Un fingerprint de forma **no** debe anunciarse como certificación de extracción fiel o PDF→PDF |

**Clasificación A-03:** `DEFECTUOSO_PARA_SU_PRETENSIÓN`; la evaluación del parser real no es accesible mediante este test, ni aunque el test termine verde. La lectura del JSON no hace independiente al expected mientras se reasigna. El código de `_generate_fingerprint` podría tener valor como **función pura auxiliar** de una nueva prueba limitada, pero no como sustituto de un oráculo físico.

**Lo que NO afirmamos:** que el test se haya ejecutado, que haya pasado, que la rama de escritura se haya recorrido o que el PDF versionado sea fixture científica canónica.

## 2. Dictamen TS-002: snapshot autojustificable del chunker (P0 confirmado por fuente)

| Punto observado | Evidencia exacta | Consecuencia |
|---|---|---|
| Cache AST obligatoria | `test_chunker_snapshot.py:19,24–25`: exige `tests/fixtures/sample_3_pages.pdf.ast.json` y hace `skipTest` si falta | No acredita un gate técnico requerido ante ausencia de input |
| **Reference snapshot** | Líneas 20,80–85: si falta `tests/fixtures/sample_chunks.json`, escribe `actual_snapshot` allí **y retorna** | **Puede producir PASS sin comparar**, por creación de baseline durante ejecución; efecto persistente latente |
| **Árbol Git real** | Caché AST **versionada**, **58 nodos** (29.352 bytes); snapshot técnico **versionado**, **10 unidades** (22.631 bytes) | Las ramas «skip por AST ausente» y «autogenerar snapshot» **no serían esperables en un checkout limpio**. No hay ejecución observada; el problema de diseño existe |
| El parser no se ejerce | `setUp` instancia `build_extraction_pipeline()`, pero `test_snapshot_verification` lee la caché JSON y llama `build_semantic_chunks_as_units(real_ast, ExactBPEEstimator())`, **sin llamar `adapter.parse`** | Es prueba de **chunker + reconstrucción aproximada de AST histórico**, no de parse PDF |
| Rehidratación con degradación | Líneas 34–57: mapea tipos por coincidencia de strings, usa `PARAGRAPH` como fallback ante enum desconocido; pierde campos de la caché como metadata/parent y establece control_plane por defecto | El input reconstruido puede **diferir del AST físico original**. No afirmar fidelidad al PDF/corpus |
| Serialización más amplia que aserción | Líneas 63–77 guardan 11 campos por chunk. Líneas 91–100 comparan **longitud + chunk_id + payload_sha256 + target_payload + context_id solo si está en expected** | No compara `chunk_index`, `chunk_fingerprint`, `chunk_type`, `source_sequence_range`, `node_count`, `context_depth` ni `estimated_tokens`. Tampoco compara `members`: ni siquiera se serializan |
| Fragilidad opuesta | `len(actual)==len(expected)` e igualdad exacta de `chunk_id` pueden fallar ante **refactor legítimo de partición**, aun si cobertura, bytes e identidad contractual siguen válidos | Un snapshot no debe fijar detalles incidentales sin norma explícita |

**Datos concretos del snapshot del SHA revisado:** se contaron **10 registros** con las 11 claves anteriores; `context_id` está presente en los 10. El `if "context_id" in expected` por tanto **sí compararía** ese campo con la referencia actual, pero permitiría que una versión futura del expected omitiera el campo silenciosamente. Los `chunk_type` de la referencia incluyen `translate`, `preserve` y `partial_translate`, **sin comparación directa de la política**.

**Clasificación A-03:** `DEFECTUOSO_COMO_GUARD_DE_SNAPSHOT_INMUTABLE`. El algoritmo de chunking sí se invoca; el defecto está en **gobierno del expected, precondiciones y alcance de las aserciones**, no en haber reemplazado su SUT.

## 3. Testigos técnicos ya disponibles y su alcance real

| Test existente | SUT/producto | Qué aporta | Qué NO garantiza |
|---|---|---|---|
| [`test_verification_pipeline_connection.py`](../../../../tests/integration/test_verification_pipeline_connection.py) | `build_extraction_pipeline().parse` **real** sobre PDF creado mediante PyMuPDF en `tmp_path`; caso negativo vector no representable | Extracción con AST no vacío, identidad mínima/determinista, rechazo explícito `B02_UNREPRESENTED_VECTOR_DRAWING` | Fingerprint topológico independiente completo, semántica científica, render PDF final |
| [`test_g3_chunk_identity_contract.py`](../../../../tests/integration/test_g3_chunk_identity_contract.py) | `TokenBudgetChunker` + `ChunkPlan.build/from_json`, AST sintético y estimador simple | Contrato de miembros, hash de manifest, generación, rechazo de tampering, **concatenación exacta `"".join(m.source_text)==source`** | Parser físico; puede tener otras fronteras no cubiertas |
| [`test_semantic_chunker.py`](../../../../tests/unit/test_semantic_chunker.py) | `build_semantic_chunks_as_units` y `ExactBPEEstimator` reales, AST sintético | Chequea suma de nodos, secuencia, determinismo y contextos; útil para propiedades limitadas | Su `test_zero_loss_reconstruction` **normaliza** con `line.strip()` y elimina líneas vacías antes de comparar: **no detecta pérdidas de whitespace de frontera**, a pesar del nombre/descr. de «conservación estricta de bytes» |

**Hallazgo adicional A03-CH-01:** el test `test_zero_loss_reconstruction` no es un oráculo «byte-exact» (líneas 56–65). **No** significa que el chunker pierda bytes; significa que ese test, tal como está escrito, podría dejar pasar algunas pérdidas o normalizaciones. Antes de ampliar B-02, aprovechar el test técnico ya existente con oráculo **sin normalizar** y entradas controladas, sin duplicar toda la ruta.

## 4. Plan preciso de remediación B (PENDIENTE, NO IMPLEMENTADO)

### B-01 — Reemplazar la falsa garantía del parser, no crear GT científico

**Objetivo:** la prueba cuyo nombre promete parser de producción debe invocar `parse` **sin parchear ese método**. Usar PDF sintético **determinista y descartable**, preparado independientemente en `tmp_path` con texto visible y, de corresponder, un vector imposible de representar. **No** usar ni modificar el PDF versionado histórico como expected de ciencia. Reutilizar o fortalecer el [test de composición real existente](../../../../tests/integration/test_verification_pipeline_connection.py), en lugar de agregar por reflejo otro supuesto E2E.

**Oráculos mínimos de aceptación:**
1. Si una fixture técnica **requerida** falta o es inválida, falla la precondición explícitamente, **sin SKIP ni generación en `tests/fixtures`**.
2. Se comprueba al menos una propiedad **independientemente esperada desde el input creado** (p.ej. texto conocido presente/estructura y orden básico), además de rechazar vector no representable. Los valores no se derivan de la salida actual del parser.
3. No hay `patch.object(adapter, "parse", ...)`, `expected = actual`, ni comparación de huellas del mismo objeto.
4. No se crean ni se sobrescriben `tests/golden`, `tests/fixtures` o referencias científicas; output solo en `tmp_path`.
5. **El alcance se nombra honestamente:** prueba técnica de extracción con fixtures sintéticas, **no** certificación topológica de corpus canónico ni CV científico.
6. Un falsador que haga que el parser devuelva nodos vacíos/incorrectos debe hacer fallar **por la propiedad observable**, no solo por excepción ambiental.

**Gobierno:** si el viejo golden corresponde a una evaluación científica histórica, **preservar su clasificación y no generar un golden sustituto** para encubrirla; reemplazar su afirmación técnica falsa con witness del parser soportado.

### B-02 — Prohibir expected autogenerados y conservar propiedades de chunking

**Objetivo:** convertir la prueba en contrato técnico inmutable, preferentemente sobre AST **sintético tipado**, sin depender del cache de 58 nodos/artículo histórico para el gate esencial. Si se conserva `sample_chunks.json` como regresión optativa, debe tener **proveniencia conocida y expected preexistente**; nunca autogenerarlo en pytest.

**Oráculos mínimos de aceptación:**
1. Input/expected obligatorio ausente = **fallo explícito**, no `skipTest`, `return` verde ni escritura del expected.
2. **Cobertura de miembros y orden:** cada nodo/fragmento requerido exactamente una vez; sin duplicados, omisiones ni nodos extra; `OMIT` fuera de proyección.
3. **Preservación exacta del source:** juntar `member.source_text` por identidad/segmento y comparar **literal byte-exact**, sin `strip`, `normalize` ni eliminación de líneas.
4. **Identidad y política:** `chunk_id` y digest SHA válidos donde son normativos, `PRESERVE/PARTIAL/TRANSLATE` correctos, manifest rechazado ante drift y `context_id` presente/igual para fronteras de contexto.
5. **Determinismo:** mismos inputs/política/versiones generan la misma proyección contractual, pero un empaquetado equivalente por refactor no debe fallar por `chunk_index` u otro campo incidental salvo norma firmada.
6. **Prueba de ausencia de referencia:** controlar que cuando falta snapshot **no aparece `sample_chunks.json` nuevo**, no hay SKIP ni PASS aparente.
7. **Falsadores:** eliminar un miembro, cambiar un byte/whitespace del texto, cruzar contexto o permitir chunk protegido al LLM debe activar la barrera correcta.

**Reutilización recomendada:** partir de las propiedades de [`test_g3_chunk_identity_contract.py`](../../../../tests/integration/test_g3_chunk_identity_contract.py) y corregir la debilidad de `test_semantic_chunker.py`, antes que ampliar artificialmente el snapshot de 11 columnas por igualdad indiscriminada.

## 5. Falsadores propuestos para C, NO EJECUTADOS

| ID | Violación deliberada en sandbox desechable | Test que debería fallar | Estado actual |
|---|---|---|---|
| `FGP-01` | Parser devuelve AST vacío/omitió texto conocido del PDF sintético | B-01 técnico real, no `test_golden_parser.py` parcheado | **Pendiente de diseñar/ejecutar** |
| `FGP-02` | Alterar tipo u orden de bloque controlado | B-01 con expected explícito independiente | Pendiente |
| `FGP-03` | Eliminar fixture requerida | Preflight falla **sin escribir archivos** ni SKIP | Pendiente |
| `FCH-01` | Falta snapshot técnico obligatorio | B-02 falla sin escribir `sample_chunks.json` | Pendiente |
| `FCH-02` | Eliminar/duplicar un miembro | B-02 contrato de coverage y manifest | Pendiente |
| `FCH-03` | Cambiar un espacio o salto de línea de fuente | B-02 testigo byte-exact; **no** normalizado | Pendiente |
| `FCH-04` | Cruzar `context_id` o enviar `PRESERVE` como translate | B-02 contrato de policy/contexto | Pendiente |
| `FCH-05` | Modificar solo `chunk_type` / `node_count` conservando payload/hash cuando sea inválido | B-02 oráculo normativo de tipo/cobertura | Pendiente |

**No ejecutar C ni B todavía:** las precondiciones de seguridad A-05 (imports/artefactos ignorados/aislamiento OS) permanecen sin completar. Un fallo por entorno o por mock no cuenta como muerte del mutante.

## 6. Verificación y gates

- [x] **A03-GP-01:** el golden parser es tautológico y parchea su propio SUT; referencia `fingerprint.json` ausente del árbol Git, PDF de fuente presente.
- [x] **A03-GP-02:** la rama de fabricación de PDF y el `skipTest` están documentados como **latentes** en checkout limpio, no ejecutados.
- [x] **A03-CH-01:** snapshot versionado de **10 unidades / 11 campos** y caché AST de **58 nodos**; autoescritura y `skipTest` latentes en checkout limpio; parser no invocado por el test.
- [x] **A03-CH-02:** siete campos del snapshot se serializan pero no se comparan; miembros tampoco están en la serialización.
- [x] **A03-CH-03:** se comprobó la normalización con `strip` del test técnico `test_semantic_chunker.py`, insuficiente para afirmar zero-loss byte-exact.
- [x] **A03-GPCH-01:** propuesta B-01/B-02 sin escritura de golden, snapshot ni GT, con oráculos independientes y falsadores concretos.
- [ ] **B-01/B-02:** implementación y prueba focal bajo aislamiento; **NO iniciado**.
- [ ] **C:** demostrar sensibilidad ante mutaciones, **NO iniciado**.
- [ ] **A-03/A01-S5:** otras familias y oráculos siguen abiertos.
- [ ] **A-05:** efectos de import, side effects y aislamiento OS pendientes.

**Criterio general:** lo científico se preserva y difiere; una prueba técnica se juzga por lo que su SUT realmente ejecuta. Ni un SKIP ni un archivo expected fabricado en tiempo de prueba constituyen evidencia de estabilidad ante regresiones.

## 7. B-01/B-02 — implementación focal sin resultados de ejecución (2026-11-16)

**Distinción temporal:** §§1–6 conservan la preauditoría histórica hecha sobre el SHA de colección \`86cd6867\`. **No describen el código remediado actual**. Los siguientes cambios corresponden a \`tests_stabilization\`, con los commits indicados; no sustituyen ni modifican el Ground Truth científico.

| Hallazgo | Cambio aplicado | Contrato comprobado y límites | Estado |
|---|---|---|---|
| **B-01 / TS-001** | [\`test_golden_parser.py\`](../../../../tests/integration/test_golden_parser.py), commit \`3f06a565\` | Se eliminó por completo \`expected_fingerprint=current_fingerprint\`, el JSON golden no versionado, el \`skipTest\` y el \`patch.object(adapter, "parse")\`. El test crea con PyMuPDF **en \`tmp_path\`** un PDF de una página con dos textos literales conocidos; invoca la composición productiva \`build_extraction_pipeline().parse\`, verifica su presencia en el AST, nodos no vacíos e identidad sin duplicados. **No** certifica geometría, páginas complejas ni fidelidad científica. | **Implementado, sin pytest ni Pyright aún** |
| **B-02 / TS-002** | [\`test_chunker_snapshot.py\`](../../../../tests/integration/test_chunker_snapshot.py), commit \`03955d90\` | Se eliminó toda escritura/lectura de \`sample_chunks.json\` y de la caché AST histórica; no se genera ningún expected. El AST sintético tipado fija cinco nodos efectivos y uno \`OMIT\`, textos con espacios dobles/saltos de línea, dos contextos, tipos \`TRANSLATE/PRESERVE/PARTIAL\`. Se comprueba cobertura, orden, bytes por miembro, política, digest y roundtrip \`ChunkPlan\`. Dos negativos usan \`dataclasses.replace\` para eliminar miembro y cambiar espacios, exigiendo rechazo por \`G3_MISSING_NODE\`/\`G3_SEGMENT_COVERAGE_ERROR\` o \`G3_SOURCE_LOSS_OR_DUPLICATION\`. **No** acredita snapshots científicos ni mide tokenizer comercial. | **Implementado, sin pytest ni Pyright aún** |

**Conservación de evidencia histórica:** \`tests/fixtures/sample_3_pages.pdf\`, \`tests/fixtures/sample_3_pages.pdf.ast.json\` y \`tests/fixtures/sample_chunks.json\` siguen **versionados e intactos**; ya no se usan como oráculos de estas pruebas. El nombre de los archivos de test es histórico; los nuevos nombres de funciones y docstrings especifican el alcance real. La colección 1.474 nodeids sigue siendo evidencia **del SHA anterior**, no del HEAD remediado.

**Runner reutilizado:** [\`run_b05_focal_isolated.ps1\`](run_b05_focal_isolated.ps1) admite \`-CheckB01B02\`, que elige **exactamente cuatro nodeids** y ejecuta pytest en un clon nuevo fijado al SHA, separado del checkout habitual. No se puede combinar con \`-CheckSensitivity\` (mutaciones de B05 son otro experimento). No usa Docker, no borra clon ni GT. Conserva \`pytest_focal.log\`, \`summary.txt\`, \`status_changes.txt\`, etc. El inventario Git sin cambios no demuestra ausencia de efectos transitorios ni es una sandbox del SO.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckB01B02
pyright tests/integration/test_golden_parser.py tests/integration/test_chunker_snapshot.py
\`\`\`

**Gates abiertos:** no se ejecutaron los nuevos cuerpos de test desde esta sesión; \`B-01/B-02 PASS=UNKNOWN\`, Pyright focal no ejecutado, ninguna mutación B01/B02 acreditada, ni CI del HEAD comprobado. Una falla real de extracción o chunking debe registrarse con su mensaje/SHA; no reescribir oráculos o generar snapshots para forzar verde. El ensayo B01 es más costoso que B02 porque ejecuta el parser físico, pero se limita a un PDF sintético en temporales.
