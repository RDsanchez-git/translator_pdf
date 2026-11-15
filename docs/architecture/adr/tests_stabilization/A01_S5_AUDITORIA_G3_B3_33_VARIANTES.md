# A01-S5 — Auditoría estática de 33 variantes de respuestas estructuradas G3-B3

> **Estado:** **REVISIÓN ESTÁTICA + CORRESPONDENCIA DE 33 NODEIDS VERIFICADAS** (12 funciones: 10 no parametrizadas + 17 mutaciones de miembros + 6 rechazos de JSON). Salida de verificador de solo lectura aportada por el owner. **No** son 33 tests ejecutados ni acreditados dinámicamente. A01-S5, A-01, A-03 y A-05 continúan abiertos.
>
> **Origen:** lectura directa sobre commit de colección `86cd68672ee692f073b62869e7c9bd177e8d9e3b` de [`tests/integration/test_g3_b3_structured_result_contract.py`](../../../../tests/integration/test_g3_b3_structured_result_contract.py), [`core/chunking/result_contract.py`](../../../../core/chunking/result_contract.py) y [`core/chunking/manifest_contract.py`](../../../../core/chunking/manifest_contract.py). `test_g3_b3_structured_result_contract.py` da **33 nodos** en la colección previa, confirmados por el owner; la relación **por orden de lista de parámetros con sufijos exactos** requiere aún verificación local.
>
> **Método:** inspección de entradas, cuerpo del test, SUT realmente invocado, oráculo escrito y rama productiva que debería rechazarlas. **No se ha ejecutado test ni mutación**, ninguna garantía de PASSED. La ficha describe contratos **puros**, sin LLM, daemon, SQLite, red o PDF físico.

## 1. Resultado general y frontera

- **12 funciones = 10 simples + 2 parametrizadas; 33 casos de fuente = 10 + 17 + 6.** Las 17 mutaciones y 6 entradas inválidas son casos distintos, no 23 funciones de test adicionales.
- **SUT realmente invocado:** `parse_chunk_response` y/o `materialize_node_results`. `TokenBudgetChunker` y `ChunkPlan.build` preparan el plan; el expected principal de las pruebas positivas incluye texto/orden literal. **Ninguna prueba ejecuta transporte/provider G3, proceso físico o proyección durable**.
- **Contrato normativo:** cada `chunk_id` y miembro se vincula a `document_id`, `ast_hash` y digest del plan validado; los resultados se reordenan por miembros esperados; las traducciones obligatorias se materializan *all-or-nothing*, los `PRESERVE` se copian y `OMIT` no se materializa.
- **Niveles de independencia provisional:** `P` = texto, orden o estado esperado literal separado del resultado del SUT; `F` = código de rechazo literal en `pytest.raises`; `C` = helper fabrica el envelope **a partir del mismo plan**, correcto para un payload coherente, pero no oráculo independiente de la validez **del propio plan**; `R` = fija cardinalidad/shape del chunker o límite de tamaño que puede requerir norma explícita; `L` = caso de «duplicado» lo rechaza por longitud, no por identidad duplicada.
- **Calificación:** **REVISADO ESTÁTICAMENTE / resultado dinámico UNKNOWN**, no `CONFIABLE_PARA_SU_ALCANCE` ni `MUTATION_KILLED`. El archivo contiene **oráculos positivos literales y controles negativos específicos**; **no** presenta una tautología directa `expected = actual` como `test_golden_parser.py`.

## 2. Matriz de los 33 casos de fuente

Las etiquetas `B3-01…33` son **IDs de auditoría**, no sustituyen los nodeids reales de pytest. Para las dos funciones parametrizadas el sufijo `[i/n]` expresa el **índice de la entrada en el decorador**, no el `parameter_id` (aún por confirmar).

| ID | Función (y variante) | Líneas fuente | Tipo | Entrada / contrato ejercitado | Oráculo **escrito** | Independencia / riesgo | Defecto que debería falsar |
|---|---|---|---|---|---|---|---|
| **B3-01** | `test_two_nodes_one_chunk_response_order_is_identity_based_not_positional` | 59–71 | POS | Respuesta con miembros invertidos; recomposición ordenada por identidad | Orden `a,b`; textos literales y hash independiente de `Alfa.` | P/F | Cambiar orden a posición de respuesta; mezcla de traducciones |
| **B3-02** | `test_fragments_across_chunks_reassemble_without_added_delimiters` | 74–86 | POS | Tres fragments de mismo nodo desde chunks distintos | Texto literal unido con exactamente dos espacios de frontera; un nodo | P/R | Añadir separador extra, omitir fragmento o alterar secuencia |
| **B3-03** | `test_preserve_is_bypassed_and_partial_remains_explicit` | 89–110 | MIX | TRANSLATE, PRESERVE, PARTIAL, OMIT en mismo plan | Lista literal 3 nodos; `PRESERVE_RESPONSE_FORBIDDEN` y `CHUNK_RESPONSE_COVERAGE_MISMATCH` | P/F | Llamar respuesta a PRESERVE o materializar OMIT |
| **B3-04** | `test_only_preserve_nodes_materialize_without_provider_results` | 113–116 | POS | Plan solo PRESERVE con responses vacío | Mismo texto de entrada literal y exactamente un nodo | P | Exigir proveedor a una fórmula preservada |
| **B3-05** | `test_invalid_member_responses_fail_closed [1/17]` | 120, 138–144 | NEG | Eliminar un miembro | `MEMBER_COVERAGE_MISMATCH` por longitud | F | Aceptar nodo perdido |
| **B3-06** | `test_invalid_member_responses_fail_closed [2/17]` | 121, 138–144 | NEG | Agregar copia de miembro | `MEMBER_COVERAGE_MISMATCH` por longitud **antes de comprobar identidad** | F/L | No equivale a test específico de clave duplicada |
| **B3-07** | `test_invalid_member_responses_fail_closed [3/17]` | 122, 138–144 | NEG | Introducir `node_id=unknown` | `UNEXPECTED_MEMBER` | F | Aceptar miembro ajeno |
| **B3-08** | `test_invalid_member_responses_fail_closed [4/17]` | 123, 138–144 | NEG | Duplicar `node_id=a` con longitud constante | `DUPLICATE_MEMBER` | F | Permitir dos respuestas para el mismo miembro |
| **B3-09** | `test_invalid_member_responses_fail_closed [5/17]` | 124, 138–144 | NEG | Corromper SHA-256 de fuente | `SOURCE_HASH_MISMATCH` | F/C | Proyectar respuesta cuya fuente no coincide con plan |
| **B3-10** | `test_invalid_member_responses_fail_closed [6/17]` | 125, 138–144 | NEG | Corromper `manifest_sha256` | `RESPONSE_BINDING_MISMATCH` | F/C | Aceptar manifest incorrecto |
| **B3-11** | `test_invalid_member_responses_fail_closed [7/17]` | 126, 138–144 | NEG | Corromper `ast_hash` | `RESPONSE_BINDING_MISMATCH` | F/C | Mezclar generaciones AST |
| **B3-12** | `test_invalid_member_responses_fail_closed [8/17]` | 127, 138–144 | NEG | Corromper `document_id` | `RESPONSE_BINDING_MISMATCH` | F/C | Mezclar documentos |
| **B3-13** | `test_invalid_member_responses_fail_closed [9/17]` | 128, 138–144 | NEG | Corromper `chunk_id` | `RESPONSE_BINDING_MISMATCH` | F/C | Aplicar respuesta de chunk distinto |
| **B3-14** | `test_invalid_member_responses_fail_closed [10/17]` | 129, 138–144 | NEG | Usar schema version `2` | `UNSUPPORTED_RESPONSE_SCHEMA` | F | Aceptar esquema desconocido |
| **B3-15** | `test_invalid_member_responses_fail_closed [11/17]` | 130, 138–144 | NEG | Usar schema version `True` (bool≠int estricto) | `UNSUPPORTED_RESPONSE_SCHEMA` | F | Coerción bool por int |
| **B3-16** | `test_invalid_member_responses_fail_closed [12/17]` | 131, 138–144 | NEG | Campo extra en envelope | `INVALID_RESPONSE_ENVELOPE` | F | Aceptar envelope expansivo |
| **B3-17** | `test_invalid_member_responses_fail_closed [13/17]` | 132, 138–144 | NEG | Campo extra en miembro | `INVALID_MEMBER_ENVELOPE` | F | Aceptar payload de miembro no normativo |
| **B3-18** | `test_invalid_member_responses_fail_closed [14/17]` | 133, 138–144 | NEG | `segment_index=True` | `INVALID_MEMBER_TYPES` | F | Coerción bool por int |
| **B3-19** | `test_invalid_member_responses_fail_closed [15/17]` | 134, 138–144 | NEG | Texto traducido vacío | `EMPTY_TRANSLATION` | F | Pérdida silenciosa de contenido |
| **B3-20** | `test_invalid_member_responses_fail_closed [16/17]` | 135, 138–144 | NEG | Texto traducido solo espacios | `EMPTY_TRANSLATION` | F | Pérdida silenciosa por whitespace |
| **B3-21** | `test_invalid_member_responses_fail_closed [17/17]` | 136, 138–144 | NEG | Texto traducido con whitespace inicial | `TRANSLATION_BOUNDARY_WHITESPACE` | F | Inventar borde antes de recomposición |
| **B3-22** | `test_invalid_json_is_rejected [1/6]` | 148, 155–158 | NEG | Clave JSON duplicada en nivel raíz | `DUPLICATE_JSON_KEY` | F | Aceptar ambigüedad JSON |
| **B3-23** | `test_invalid_json_is_rejected [2/6]` | 149, 155–158 | NEG | Clave JSON duplicada anidada | `DUPLICATE_JSON_KEY` | F | Aceptar ambigüedad anidada |
| **B3-24** | `test_invalid_json_is_rejected [3/6]` | 150, 155–158 | NEG | Constante `NaN` no JSON estricto | `INVALID_JSON_CONSTANT` | F | Aceptar NaN no válido |
| **B3-25** | `test_invalid_json_is_rejected [4/6]` | 151, 155–158 | NEG | JSON sintácticamente inválido | `INVALID_RESPONSE_JSON` | F | Parseo permisivo o fallback |
| **B3-26** | `test_invalid_json_is_rejected [5/6]` | 152, 155–158 | NEG | Envelope es array `[]` | `INVALID_RESPONSE_ENVELOPE` | F | Aceptar tipo de envelope ajeno |
| **B3-27** | `test_invalid_json_is_rejected [6/6]` | 153, 155–158 | NEG | Respuesta `None`, no texto | `RESPONSE_MUST_BE_JSON_TEXT` | F | Coerción silenciosa de tipos |
| **B3-28** | `test_unknown_chunk_rejected_before_payload_parse` | 161–164 | NEG | Chunk fuera de plan con JSON `{}` | `UNKNOWN_CHUNK` antes de validar envelope | F | Parsear payload antes de validar identidad |
| **B3-29** | `test_incomplete_or_extra_chunks_never_return_partial_nodes` | 167–176 | NEG | Mapa sin respuesta obligatoria y mapa con chunk extraño | `CHUNK_RESPONSE_COVERAGE_MISMATCH` en ambos caminos | F/C | Materializar documento parcial o permitir extra |
| **B3-30** | `test_source_boundary_whitespace_preserved_through_segmented_translation` | 179–185 | POS | Texto fuente con LF y espacios en extremos de fragmentos | String de resultado literal con límites `\n ... \n` | P/R | Eliminar espacios de fuente o añadir delimitadores |
| **B3-31** | `test_whitespace_only_source_never_silently_disappears_in_translation` | 188–192 | NEG | Fuente sin caracteres no blancos | `WHITESPACE_ONLY_SOURCE` | F | Eliminar nodo fuente silenciosamente |
| **B3-32** | `test_response_size_bound_rejects_uncontrolled_payload` | 195–198 | NEG | Texto >4 MiB antes del JSON parser | `RESPONSE_TOO_LARGE` | F/R | Aceptar input sin límite de tamaño |
| **B3-33** | `test_translated_unicode_surrogates_rejected_before_projection` | 201–207 | NEG | Unicode surrogate sin pareja en translated_text | `INVALID_UNICODE` | F | Aceptar texto que no codifica UTF-8 |

**Sumario de matriz:** **33 filas únicas**, de ellas 17 entradas de mutación de miembros, seis invalidaciones JSON y diez funciones no parametrizadas. Algunas funciones mezclan positivo y negativo (`B3-03`) o dos fallos de coverage en un único nodeid (`B3-29`); por eso **las filas no equivalen a 33 aserciones independientes**.

## 3. Verificación de la independencia del oráculo

### OI-01 — Positivos con expected independiente del resultado: evidencia favorable

`B3-01` compara el orden y la traducción resultante con listas literales `[('a','Alfa.'), ('b','Beta traducida.')]`; invierte la lista recibida **antes** de parsear. `B3-02` y `B3-30` contrastan la recomposición con strings literales de texto completo y fronteras; `B3-03` comprueba exactamente `TRANSLATE/PRESERVE/PARTIAL/OMIT`; `B3-04` exige preservar la fórmula literal sin respuestas de provider. El SHA del texto final se calcula con `hashlib.sha256` sobre un **literal**, no con `_hash_text` del SUT.

**Límite:** `p.units`, `unit.chunk_id`, `plan.digest`, `plan.ast_hash` se generan en la preparación con clases productivas. Son entradas válidas para comprobar `result_contract`, pero **no** un oráculo independiente que certifique la integridad física del AST, que el chunker siempre separe de forma correcta, o que el plan esté ligado a un hash calculado desde un PDF real.

### OI-02 — Negativos con razón de rechazo específica: evidencia favorable, sensibilidad aún UNKNOWN

`B3-05…27` preparan un plan válido y **alteran exactamente una dimensión del envelope o JSON**. `pytest.raises(ValueError, match=marker)` exige una familia de error concreta. La implementación leída comprueba: identidad de documento/generación/chunk, versión estricta, campos exactos, SHA-256 de fuente, unicidad y cobertura de miembros, texto no vacío y espacios externos prohibidos; JSON duplicado/NaN inválido, tipos de envelope y tamaño máximo. `B3-28…33` cubren precedencia de chunk inexistente, cobertura completa, fronteras, texto solo whitespace, límite de bytes y surrogate Unicode.

**Límite:** tener un matcher de error correcto **no demuestra una mutación eliminada**. Los escenarios no cubren necesariamente cada campo/tipo posible, ni comportamiento de concurrencia, persistencia o red. No se debe adaptar el matcher a un mensaje distinto por mera búsqueda de resultados verdes sin comprobar la norma.

### OI-03 — Hallazgo de precisión: «miembro duplicado» puede rechazarse por causa equivocada

- **B3-06:** hace `members.append(copia)`; el SUT compara primero `len(raw_members) == len(unit.members)`, por eso se espera `MEMBER_COVERAGE_MISMATCH`. **No verifica la rama `DUPLICATE_MEMBER`.**
- **B3-08:** cambia el `node_id` del segundo miembro a `a` sin alterar la cantidad; ahí `seen` detecta la identidad repetida y se espera **`DUPLICATE_MEMBER`**.

**Decisión:** ambos son testigos útiles de barreras diferentes. Al preparar falsadores, no aceptar B3-06 como evidencia de que la unicidad interna funcione; B3-08 es el candidato correcto.

### OI-04 — Acoplamientos y áreas no certificadas

1. Los tests `B3-02`/`B3-30` esperan **exactamente tres y dos chunks** con presupuestos concretos. Si la política de división cambia sin perder cobertura, podrían romperse aunque la recomposición por fragmentos siga siendo correcta. **Riesgo de fragilidad ante refactor**; preservar el contrato de bytes y orden, no necesariamente la cantidad de chunks, salvo norma explícita.
2. El envelope válido `_response()` deriva `document_id`, `ast_hash`, `manifest_sha256`, `chunk_id` y SHA de cada `member.source_text` del **plan construido en el mismo test**. Las mutaciones negativas evalúan la barrera **frente a ese plan**. **No prueba** que el plan inicial sea independiente de entradas corruptas; esa garantía corresponde a validación `ChunkPlan.build/from_json` y oráculos de fuente.
3. Solo un ejemplo de whitespace **inicial** de traducción está parametrizado (`B3-21`). Faltan simetrías para whitespace **final**, entradas de tipos extraños adicionales, y composiciones multi-chunk para algunos fallos. **No diagnosticar defectos por cobertura no demostrada**: son candidatos a controles de fase B/C, si el contrato exige esos casos.
4. El límite **4 MiB** está fijado tanto en test como en implementación. Debe verificarse si es valor normativo contractual o constante interna; cambiar ese límite podría provocar fragilidad si no hay contrato firmado.
5. El texto esperado se calcula por entradas literales controladas, pero **la corrección lingüística** de la traducción y la fidelidad física de PDF quedan fuera del SUT de este archivo.

## 4. Falsadores prioritarios propuestos (NO EJECUTADOS)

| ID | Mutación hipotética del SUT, solo en sandbox descartable | Testigo previsto | Evidencia dinámica que se pediría |
|---|---|---|---|
| **MF-B3-01 / P0** | Sustituir orden por identidad de miembros por el orden de respuesta | B3-01 | Orden/textos del resultado dejan de coincidir con literales |
| **MF-B3-02 / P0** | Ignorar vínculo `ast_hash` o digest de plan | B3-10 / B3-11 | Respuesta de generación equivocada resulta aceptada, aunque debería rechazar |
| **MF-B3-03 / P0** | Quitar rechazo `DUPLICATE_MEMBER`, conservar check de longitud | **B3-08**, no B3-06 | Rama de identidad repetida deja de fallar; B3-06 puede seguir verde |
| **MF-B3-04 / P0** | No validar cobertura de respuesta `required` | B3-29 | Recomposición parcial/extra deja de emitir `CHUNK_RESPONSE_COVERAGE_MISMATCH` |
| **MF-B3-05 / P0** | Enviar PRESERVE al parser/provider o materializar OMIT | B3-03/B3-04 | Falta rechazo de PRESERVE o cambia lista de nodos materializados |
| **MF-B3-06 / P1** | Añadir separadores artificiales entre fragmentos o truncar whitespace de origen | B3-02/B3-30 | Literal final no coincide |
| **MF-B3-07 / P1** | Aceptar duplicate keys anidadas / coerción bool por int | B3-15/B3-18/B3-22/B3-23 | Cambia la causa contractual de rechazo |
| **MF-B3-08 / P1** | Desactivar validación Unicode o límite de bytes | B3-32/B3-33 | Texto malformado o demasiado grande pasa la frontera |

**No ejecutar en el repositorio del owner** ni durante A-01. En C, caso positivo de control y mutación puntual, aislamiento, motivo de fallo preciso, reversión y diff sin modificación de archivos persistidos.

## 5. Evidencias de cierre de esta tranche

- [x] **S5-G3-01:** inspección de **12 funciones y 33 entradas de fuente**; clasificación por contrato, input, oráculo, SUT y falsador, con 33 filas.
- [x] **S5-G3-02:** validación por lectura de las ramas correspondientes en `core/chunking/result_contract.py` y del papel asumido de `ChunkPlan.build`.
- [x] **S5-G3-03:** documentada la independencia **parcial** del expected, el riesgo de `p.units` exactos y la distinción del doble control de miembros duplicados.
- [x] **S5-G3-04 — Identidad de nodeids VERIFICADA**: salida real del owner del [verificador de solo lectura](verify_a01_s5_g3_b3_nodeids.py) confirma 33/33 IDs únicos, 12 funciones, 10 simples, 17+6 parametrizados, SHA de colección y cardinalidad; cotejo B3-01…33 registrado abajo. **Sin PASS, sin acreditación semántica dinámica ni mutation kill.**
- [ ] **S5-G3-05:** [preauditoría A-03 de independencia de oráculos](A03_PREAUDITORIA_INDEPENDENCIA_ORACULOS_G3_B3.md) realizada **estáticamente**: 4 positivos, 1 mixto, 28 negativos; límites de plan compartido, regex parcial, fronteras del chunker y UTF-8 multibyte. **Ensayos focales negativos y sensibilidad ante mutación pendientes**, posteriores a A-05/etapa C.
- [ ] **A01-S5 / A-01 / A-03:** **ABIERTOS**. No convertir revisión estática en PASSED.

**Siguiente acción:** usar el JSON de colección existente para asignar **identidad real** a los 33 casos, sin ejecutar pytest; luego trazar los controles normativos más importantes a un puerto de producción estable antes de diseñar B/C.

## 6. Comprobación reproducible de identidad de los 33 nodeids (VERIFICADA POR EL OWNER)

Después de actualizar `tests_stabilization`, el owner puede ejecutar este comando de **solo lectura** sobre la colección ya existente, sin pytest y sin creación de outputs:

```powershell
$reports = Join-Path $env:TEMP "translator-a01-isolated-k4f4mf10\reports"
.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\verify_a01_s5_g3_b3_nodeids.py --repo-root . --reports $reports
```

**Resultado recibido:** el owner ejecutó el verificador y compartió la salida completa: **SHA exacto `86cd68672ee692f073b62869e7c9bd177e8d9e3b`**, **12 funciones**, **33 nodeids únicos**, **10 simples**, **17 mutaciones de miembros**, **6 invalidaciones JSON**, y `source_and_collection_cardinality_match=true`. Sin errores del verificador. **No ejecutó ningún cuerpo de test.** Los identificadores son los emitidos por pytest; no usarlos como oráculo normativo resistente a refactors, pues sus sufijos autogenerados pueden variar.

### 6.1 Cruce de IDs de auditoría con `parameter_id` exactos de pytest

**Regla de reconstrucción:** el prefijo del nodeid real es `tests/integration/test_g3_b3_structured_result_contract.py::`. Para las **10 funciones simples**, el nodeid es el prefijo seguido del nombre de función (sin corchetes). Para **las 23 variantes**, el nodeid es el prefijo + nombre de función + `[` + el `parameter_id` textual de esta tabla + `]`.

| ID de auditoría | Función fuente | `parameter_id` emitido por pytest |
|---|---|---|
| **B3-01** | `test_two_nodes_one_chunk_response_order_is_identity_based_not_positional` | `null` (caso simple) |
| **B3-02** | `test_fragments_across_chunks_reassemble_without_added_delimiters` | `null` (caso simple) |
| **B3-03** | `test_preserve_is_bypassed_and_partial_remains_explicit` | `null` (caso simple) |
| **B3-04** | `test_only_preserve_nodes_materialize_without_provider_results` | `null` (caso simple) |
| **B3-05** | `test_invalid_member_responses_fail_closed` | `<lambda>-MEMBER_COVERAGE_MISMATCH0` |
| **B3-06** | `test_invalid_member_responses_fail_closed` | `<lambda>-MEMBER_COVERAGE_MISMATCH1` |
| **B3-07** | `test_invalid_member_responses_fail_closed` | `<lambda>-UNEXPECTED_MEMBER` |
| **B3-08** | `test_invalid_member_responses_fail_closed` | `<lambda>-DUPLICATE_MEMBER` |
| **B3-09** | `test_invalid_member_responses_fail_closed` | `<lambda>-SOURCE_HASH_MISMATCH` |
| **B3-10** | `test_invalid_member_responses_fail_closed` | `<lambda>-RESPONSE_BINDING_MISMATCH0` |
| **B3-11** | `test_invalid_member_responses_fail_closed` | `<lambda>-RESPONSE_BINDING_MISMATCH1` |
| **B3-12** | `test_invalid_member_responses_fail_closed` | `<lambda>-RESPONSE_BINDING_MISMATCH2` |
| **B3-13** | `test_invalid_member_responses_fail_closed` | `<lambda>-RESPONSE_BINDING_MISMATCH3` |
| **B3-14** | `test_invalid_member_responses_fail_closed` | `<lambda>-UNSUPPORTED_RESPONSE_SCHEMA0` |
| **B3-15** | `test_invalid_member_responses_fail_closed` | `<lambda>-UNSUPPORTED_RESPONSE_SCHEMA1` |
| **B3-16** | `test_invalid_member_responses_fail_closed` | `<lambda>-INVALID_RESPONSE_ENVELOPE` |
| **B3-17** | `test_invalid_member_responses_fail_closed` | `<lambda>-INVALID_MEMBER_ENVELOPE` |
| **B3-18** | `test_invalid_member_responses_fail_closed` | `<lambda>-INVALID_MEMBER_TYPES` |
| **B3-19** | `test_invalid_member_responses_fail_closed` | `<lambda>-EMPTY_TRANSLATION0` |
| **B3-20** | `test_invalid_member_responses_fail_closed` | `<lambda>-EMPTY_TRANSLATION1` |
| **B3-21** | `test_invalid_member_responses_fail_closed` | `<lambda>-TRANSLATION_BOUNDARY_WHITESPACE` |
| **B3-22** | `test_invalid_json_is_rejected` | `{"schema_version":1,"schema_version":1}-DUPLICATE_JSON_KEY` |
| **B3-23** | `test_invalid_json_is_rejected` | `{"a":{"key":1,"key":2}}-DUPLICATE_JSON_KEY` |
| **B3-24** | `test_invalid_json_is_rejected` | `NaN-INVALID_JSON_CONSTANT` |
| **B3-25** | `test_invalid_json_is_rejected` | `not valid json-INVALID_RESPONSE_JSON` |
| **B3-26** | `test_invalid_json_is_rejected` | `[]-INVALID_RESPONSE_ENVELOPE` |
| **B3-27** | `test_invalid_json_is_rejected` | `None-RESPONSE_MUST_BE_JSON_TEXT` |
| **B3-28** | `test_unknown_chunk_rejected_before_payload_parse` | `null` (caso simple) |
| **B3-29** | `test_incomplete_or_extra_chunks_never_return_partial_nodes` | `null` (caso simple) |
| **B3-30** | `test_source_boundary_whitespace_preserved_through_segmented_translation` | `null` (caso simple) |
| **B3-31** | `test_whitespace_only_source_never_silently_disappears_in_translation` | `null` (caso simple) |
| **B3-32** | `test_response_size_bound_rejects_uncontrolled_payload` | `null` (caso simple) |
| **B3-33** | `test_translated_unicode_surrogates_rejected_before_projection` | `null` (caso simple) |

**Comprobación:** 33 filas, 33 nodeids únicos según el verificador, sin discrepancias de cardinalidad. Los dos identificadores `<lambda>-MEMBER_COVERAGE_MISMATCH0/1` designan **eliminar** y **añadir** miembro, respectivamente; la rama `DUPLICATE_MEMBER` corresponde al caso `B3-08`. Los índices son IDs **de colección actual**, no promesa de estabilidad de nombres en futuros refactors.

### 6.2 Frontera del resultado

Este paso verifica **identidad y existencia del ítem** en `all.json`, no el resultado de su ejecución. El número de tests individualmente **acreditados por ejecución o falsación sigue siendo 0**. Para cerrar A-03/C habrá que comprobar oráculo independiente y muerte de mutación por ruptura contractual en entorno descartable, no solamente la presencia de un matcher de error.
