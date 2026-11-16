# A-03 — Preauditoría estática de oráculos G3-B3 (33 nodeids)

> **Estado:** revisión de independencia estática documentada para 33 casos. **A-03, A01-S5, A-01 y A-05 permanecen abiertos.** No se ejecutó pytest, mutaciones, pipeline o evaluación GT.
>
> **Fuentes verificadas:** `tests/integration/test_g3_b3_structured_result_contract.py`, `core/chunking/result_contract.py`, `core/chunking/manifest_contract.py` y `core/chunking/semantic_chunking.py`, correspondientes al SHA de colección `86cd68672ee692f073b62869e7c9bd177e8d9e3b`; [matriz con 33 nodeids y parameter_id reales](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md). Fecha: 2026-11-15.

## 1. Clasificación explícita de oráculos

| Grupo | Identificadores | Nodos | ¿Qué expected se usa? | Conclusión |
|---|---|---:|---|---|
| Positivos | B3-01/02/04/30 | **4** | Texto/orden/identidad esperados **literales**, SHA calculado con `hashlib.sha256("Alfa.")` y no con el SUT | Independencia **parcial favorable** para resultado de `result_contract` |
| Mixto | B3-03 | **1** | Lista literal de nodos visibles y dos códigos de rechazo para `PRESERVE`/coverage | Independencia parcial para política y recomposición |
| Negativos | B3-05…29 y B3-31…33 | **28** | `pytest.raises(ValueError, match=...)` con token de error literal y entrada negativa construida deliberadamente | Rechazo específico escrito, **sin sensibilidad demostrada** |

**4 + 1 + 28 = 33 nodeids.** B3-29 contiene dos subcasos de cobertura en **un solo test**. B3-03 combina un positivo y dos rechazos; la cantidad de nodeids no es la cantidad de aserciones independientes.

## 2. Hallazgos por lectura conjunta de test y SUT

### OI-G3-01 — El plan no es un oráculo independiente del AST (P1)

`_plan` llama a `TokenBudgetChunker.chunk_group` y `ChunkPlan.build`. `_response` obtiene `document_id`, `ast_hash`, `manifest_sha256` y `chunk_id` **del mismo plan**, y computa `source_sha256` sobre `unit.members[].source_text`. Esto construye un **input válido y coherente** para la frontera pura de parser/recomposición; no es una tautología de `actual == expected` porque las salidas positivas se contrastan con valores literales.

**Garantía real:** aceptar o rechazar respuestas **respecto de un ChunkPlan validado**. **No** demuestra que el plan esté ligado al AST/PDF físico. Detalle concreto: `_plan(generation="ast_b3")` pasa ese string al parámetro `ast_hash`, y `ChunkPlan.build` comprueba que el campo sea no vacío y la cobertura de unidades; **no calcula en ese método el hash del AST real**. B3-11 detecta un *binding diferente al del plan*, no alteración del AST físico.

### OI-G3-02 — Frágil ante cambio legítimo del algoritmo de chunking (P1)

B3-02 y B3-30 fijan `len(p.units) == 3` y `== 2` bajo un estimador fake y presupuestos específicos. El contrato robusto de `materialize_node_results` es **preservación de bytes, orden, identidad y cobertura completa**, no necesariamente una estrategia única de partición. Separar la prueba del chunker (si esa política exacta es normativa) de la de recomposición. **Riesgo de refactor**, no defecto probado.

### OI-G3-03 — El matcher de excepciones es substring regex (P1)

`pytest.raises(ValueError, match=marker)` busca un **patrón regex** dentro del mensaje. Exigir `"DUPLICATE_MEMBER"` no comprueba por sí solo un código estructurado exacto, y un fallo con causa distinta que contenga ese token podría satisfacer el matcher.

**Caso causal:** B3-06 agrega un miembro duplicado **y cambia la longitud**: `parse_chunk_response` verifica longitud primero y da `MEMBER_COVERAGE_MISMATCH`. **No prueba detección de identidad duplicada**. B3-08 sustituye el ID manteniendo cantidad; el SUT entra en el guard `seen` y declara `DUPLICATE_MEMBER`. Ambas pruebas son útiles, pero cubren barreras diferentes. Propuesta para fase B/C: código de error contractual exacto o error tipado público, sin acoplar el test a detalles humanos o nombre de helper.

### OI-G3-04 — Byte limit y Unicode: bordes aún no probados (P2)

B3-32 pasa **4 MiB + 1 de caracteres ASCII** y espera `RESPONSE_TOO_LARGE`; implementación limita **bytes UTF-8**. El test **no distingue** una implementación incorrecta que limite por caracteres en lugar de bytes. Falsador nuevo propuesto: cadena multibyte cuya cuenta de caracteres esté dentro de la cuota pero el tamaño UTF-8 la exceda; opcionalmente comprobar borde exacto con envelope válido.

B3-33 envía `json.dumps` de un surrogate sin pareja (se transforma en escape ASCII en JSON); `json.loads` lo decodifica y `_hash_text(translated_text)` rechaza UTF-8 inválido. Es un control escrito de encoding, **no** una prueba de render ni de PDF.

### OI-G3-05 — «All-or-nothing» es puro, no persistencia ni red (P0 de alcance)

`materialize_node_results` exige `set(raw_responses) == required`, valida todos los chunks y **retorna una tupla** de `NodeMaterialization`; **no escribe SQLite, no llama provider y no publica PDF**. B3-29 comprueba el rechazo puro para mapa incompleto o extra, **no** un rollback externo. Las garantías de fencing/persistencia/publicación corresponden a tests G3/W06/G5 separados, no a este archivo.

## 3. Falsadores propuestos — NO EJECUTADOS

| Violación normativa hipotética | Testigo fuente | Oracle que debería detectar la violación | Limitación |
|---|---|---|---|
| Reordenar resultados por orden de respuesta | B3-01 | Lista literal de IDs/textos diferente | No sustituir por comparación de conjuntos |
| Ignorar digest o generación del plan | B3-10, B3-11 | Rechazo de binding exacto | No valida hash AST físico |
| Eliminar guard de identidad duplicada, conservar guard de longitud | **B3-08** | `DUPLICATE_MEMBER` deja de ocurrir o cambia a aceptación | **B3-06 no es testigo de esa rama** |
| Aceptar chunks obligatorios faltantes/extra | B3-29, B3-03 | `CHUNK_RESPONSE_COVERAGE_MISMATCH` | Dos subcasos dentro de B3-29 |
| Materializar `OMIT` o requerir provider para `PRESERVE` | B3-03, B3-04 | Lista literal de nodos o error contractual | No comprueba egress real |
| Alterar whitespace de origen entre segmentos | B3-02, B3-30 | Resultado textual literal alterado | Cantidad exacta de chunks puede fallar antes |
| Ignorar `source_sha256` | B3-09 | `SOURCE_HASH_MISMATCH` deja de emitirse | Hash relativo al plan |
| Aceptar `NaN` o surrogate inválido | B3-24, B3-33 | Rechazo de JSON/Unicode | Dos fronteras distintas |
| Limitar **caracteres** en vez de **bytes** UTF-8 | **B3-32 insuficiente** | Requiere nuevo test con caracteres multibyte | Hueco de sensibilidad estática, **no** fallo actual |
| Aceptar resultado parcial | B3-29 | No debe devolverse materialización parcial | Solo función pura |

**Política de futura ejecución:** sandbox de SO descartable y gate A-05 completado, SUT original como control, **una mutación por contrato** y fallo del test **por causa contractual**, no por import error, timeout, fixture rota o entorno. No tocar el checkout del owner.

## 4. Decisiones sobre estabilidad ante refactors

- **Conservar P0:** binding plan/miembro, no duplicados, all-or-nothing, reglas `PRESERVE/OMIT`, bytes matemáticos/texto reconstruido. Son los contratos útiles.
- **Refinar P1 solamente si se aprueba B:** expectativas de longitud de chunks, código contractual de error vs substring de regex, separar expected de recomposición de construcción del plan.
- **Ampliar P2 tras revisar norma:** UTF-8 multibyte, fronteras exactas, trailing whitespace y combinaciones multi-chunk. Sin corpus GT ni rebaseline.
- **No hacer ahora:** modificar tests, producción, workflow, parámetros, fixtures, snapshots, límites científicos, ni declarar un mutation kill.

## 5. Gates

- [x] **A03-G3-01:** 33/33 nodeids clasificados por procedencia del expected (4 positivos, 1 mixto, 28 negativos).
- [x] **A03-G3-02:** contrastar expectativas del test contra `result_contract`, `manifest_contract` y `semantic_chunking`.
- [x] **A03-G3-03:** registrar cinco límites y diez falsadores candidatos, sin ejecutar.
- [ ] **A03-G3-04:** validar eficacia mediante ejecución focal y mutantes bajo A-05/C; **0 casos acreditados dinámicamente**.
- [ ] **A-03 / A01-S5:** faltan otras familias, golden/chunker y oráculos de frontera externa.
- [ ] **A-05:** faltan condiciones de aislamiento y efectos de importación.

**Conclusión:** independencia estática **parcial favorable** de oráculos sobre la **frontera pura** G3-B3; alcance deliberadamente limitado. La auditoría no constituye PASS ni validación científica.

## 6. Corrección focal del hueco UTF-8 y validación pendiente (2026-11-16)

**Sujetos de esta corrección, frente al censo congelado §1–5:** \`tests_stabilization\` con cambios **solo a tests**:

- [\`test_g3_b3_structured_result_contract.py\`](../../../../tests/integration/test_g3_b3_structured_result_contract.py): se añadió \`test_response_limit_is_utf8_bytes_not_character_count\` (commit \`c68595df\`). Construye un envelope válido con una traducción de \`é\` repetida: **cantidad de caracteres del JSON menor que 4 MiB**, pero **cantidad de bytes de su representación UTF-8 mayor que 4 MiB**. Exige \`G3_B3_RESPONSE_TOO_LARGE\` desde el SUT real \`parse_chunk_response\`; las dos desigualdades previas validan que el input discrimina inequívocamente caracteres de bytes. No cambia la constante, la implementación ni el contrato normativo. Corrige el hueco estático **OI-G3-04**; no equivale todavía a un mutante externo KILLED.
- [\`test_verification_pipeline_connection.py\`](../../../../tests/integration/test_verification_pipeline_connection.py): \`test_pipeline_extracts_nonempty_ast_from_text_pdf\` ahora también exige **dos frases literales independientes**, ya insertadas en el PDF creado en \`tmp_path\` (commit \`2e4c001f\`). Un AST no vacío que pierda el texto original debe fallar con \`B02_EXTRACTED_SOURCE_TEXT_MISSING\`. No se sustituyó el parser real por mock. Se conservaron las pruebas de identidad/determinismo y el rechazo \`B02_UNREPRESENTED_VECTOR_DRAWING\` para dibujo vectorial no representable.

**Ejecución focal prevista:** el [runner de clon independiente](run_b05_focal_isolated.ps1) ofrece \`-CheckA03Boundaries\` (commit \`c8fe3887\`). Selecciona exactamente los dos archivos de test señalados, no el selector amplio \`not e2e\`. Históricamente el módulo G3-B3 aportaba **33** nodeids y el parser **5**; con el nuevo caso se esperan **39 nodeids**, sujeto a confirmación de pytest, **no cifra acreditada por colección**. Los dobles solo construyen un plan válido/fake estimator; los SUT \`parse_chunk_response\` y \`build_extraction_pipeline().parse\` permanecen reales.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckA03Boundaries
pyright tests/integration/test_g3_b3_structured_result_contract.py tests/integration/test_verification_pipeline_connection.py
\`\`\`

Revisar \`summary.txt\`, \`pytest_focal.log\`, \`status_changes.txt\` y resultado de Pyright; no presentar Pyright verde como prueba de eficacia semántica. En caso de falla, conservar el error completo; **no ajustar el input a ASCII ni cambiar el límite del runtime para obtener PASS**. La colección HEAD de A-01/A-04 que dio **1.476** nodeids corresponde al SHA previo \`5447963d\`, **no** al HEAD que incorpora esta prueba adicional. La recolección formal del nuevo SHA queda pendiente.

**Estado:** cambios de pruebas implementados, **pytest/Pyright no ejecutados aún sobre estos cambios**; A-03, A-04, A-05 global, CI del HEAD y controles de sensibilidad general siguen abiertos. No se tocaron GT, corpus científico, snapshots, runtime ni el workflow.

## 7. Evidencia dinámica A-03 y dos falsadores disponibles (2026-11-16)

**Baseline aportada por el owner (SHA exacto \`50ec05509d095036f883c61ad1149843391fd64e\`):**
- \`pytest_focal.log\`: **\`39 passed in 2.56s\`**; \`pytest_exit_code=0\`; selector \`a03_boundaries_requested=True\`.
- \`summary.txt\`: clon independiente \`tst-stab-b05-8ea29af26ac1427e90fbcb27d271bf71\`, \`docker_used=false\`, \`no_OS_level_sandbox_claim=true\`, \`sensitivity_exit_code=-1\` (no se pidió ensayo de sensibilidad).
- \`status_changes.txt\` **vacío según owner**: sin diferencias persistentes Git del clon.
- Pyright explícito sobre \`test_g3_b3_structured_result_contract.py\` y \`test_verification_pipeline_connection.py\`: **\`0 errors, 0 warnings, 0 informations\`**; el aviso \`v1.1.411 → v1.1.414\` no es advertencia de tipado.
- Los 39 tests son **34 G3-B3** (33 históricos + 1 nuevo multibyte) y **5 de la frontera PDF→AST**. La colección histórica global de 1.476 nodeids del SHA anterior requiere nueva conciliación al HEAD que incorpora el test nuevo.

**Interpretación:** se acredita una baseline técnica **39/39 positiva** para los oráculos reforzados, sin Docker, con tipado limpio. No atribuir a esta ejecución ningún \`MUTATION_KILLED\`, GitHub Actions, CV científico, evaluación lingüística, OS sandbox o ausencia de efectos transitorios.

**Sensibilidad preparada después de esta evidencia, pero NO EJECUTADA:**

| ID | Mutación del SUT en memoria y subproceso independiente | Test protector | Veredicto contractual esperado |
|---|---|---|---|
| **A03-NEG-UTF8** | \`result_contract.parse_chunk_response\` acepta erróneamente JSON cuya cuenta de caracteres está bajo 4 MiB aunque su UTF-8 exceda la cuota (guard de bytes relajado solo para ese caso) | \`test_response_limit_is_utf8_bytes_not_character_count\` | \`Failed: DID NOT RAISE\` al faltar \`G3_B3_RESPONSE_TOO_LARGE\` |
| **A03-NEG-EXTRACTION** | \`PdfParserAdapter.parse\` ejecuta el parser real, pero su AST devuelto pierde la frase conocida \`Scientific observations must remain traceable.\` | \`test_pipeline_extracts_nonempty_ast_from_text_pdf\` | \`AssertionError: B02_EXTRACTED_SOURCE_TEXT_MISSING\` |

Los falsadores se implementaron en [\`probe_a03_sensitivity.py\`](probe_a03_sensitivity.py) y la opción \`-CheckA03Sensitivity\` de [\`run_b05_focal_isolated.ps1\`](run_b05_focal_isolated.ps1). El runner crea **otro clon independiente fijado al SHA actual**, exige primero que pasen los 39 tests y solo entonces crea dos procesos Python, cada uno con un patch del SUT **en memoria**, sin editar archivos del runtime ni Ground Truth. Verificador fail-closed: \`exit=1\`, exactamente \`1 failed\`, marcador de fallo del contrato y ninguna señal \`ERROR collecting\`/\`INTERNALERROR\`. Los informes \`a03_mutation_summary.json\`, \`a03_mutation_g3_utf8_byte_limit.log\` y \`a03_mutation_parser_dropped_source.log\` son evidencia **solo después de ejecutar**.

\`\`\`powershell
git pull --ff-only origin tests_stabilization
& .\docs\architecture\adr\tests_stabilization\run_b05_focal_isolated.ps1 -RepoRoot (Get-Location).Path -CheckA03Sensitivity
\`\`\`

**Estado:** 39 PASS y Pyright 0 sobre el SHA anterior acreditados; **0 mutaciones A03 acreditadas hasta recibir una nueva ejecución**. A-03/A-04 globales, CI del HEAD y gate A-05 del entorno permanecen abiertos. El wrapper de Python no proporciona seguridad de red a nivel SO; no se ejecuta la suite completa.
