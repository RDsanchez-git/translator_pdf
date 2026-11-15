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
