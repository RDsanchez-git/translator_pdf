# W-06 — Resultado comunicado por el owner y diseño de corrección mínima

**Fecha de registro:** 2026-11-06.
**Clase:** `WORKING OBSERVATION / POST-TEST / NON-NORMATIVE / NO IMPLEMENTATION AUTHORIZATION`.
**Código/testigo publicado antes del ensayo:** `pipeline_stabilization`, `8771cb5b7cbbf1954688b083d750d84508045e6f`.
**Procedencia:** salida de pytest copiada por el owner en conversación; la versión exacta de su checkout y los artefactos SQLite efímeros no se verificaron de manera independiente en este registro.
**Prerregistro:** [plan y testigo W-06](W06_PLAN_Y_TESTIGOS_G3_EFECTO_INCIERTO_20261106.md); [Atlas §8.5.2 W-06](../PRODUCTION_PIPELINE_EXECUTION_ATLAS.md); [Candidate D-1/D-2 §7](../DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md); `NADR-F18-03/04/05` FROZEN.

## 1. Ejecución comunicada

El owner ejecutó en su Windows/venv Python 3.11.9:
`python -m pytest tests/integration/test_w06_g3_uncertain_effect_offline.py -q -ra`

Salida comunicada: **`3 passed, 1 xfailed, 2 warnings in 13.53s`**. `XFAIL` corresponde a `test_w06_contract_oracle_never_automatically_repeats_unknown_effect`. Los dos `FutureWarning` proceden de `google.api_core` (fin futuro de soporte Python 3.11) y de importación de `google.generativeai` deprecado; no equivalen al fallo contractual.

Interpretación, sin inflar el veredicto:
- **PASS 1:** un lease manifiestamente expirado impide el contacto con el fake pre-I/O.
- **PASS 2:** una respuesta válida queda persistida en `chunk_result_receipts`, y la tarea `RESULT_STAGED` no se vuelve a reclamar.
- **PASS 3:** el test de caracterización observó **dos invocaciones aceptadas por el fake** para la misma unidad: primera aceptación seguida de timeout simulado y segunda aceptación dentro del mismo `run_pipeline`. Un PASS de caracterización aquí **no acredita seguridad**.
- **XFAIL (estricto):** el oráculo que exige no reejecutar automáticamente un efecto `UNKNOWN` no se satisface. Es evidencia de la brecha, no un PASS de W-06.

El fake es un simulador de **interfaz de proveedor**, no una llamada HTTP real. El resultado no prueba doble cobro ni egress efectivo a Groq. La prueba tampoco cubre todavía crash real entre efecto y journaling ni reinicio de proceso; la observación es limitada al Engine actual.

**Dictamen acotado:** `W06_UNCERTAIN_EFFECT_AUTOMATIC_RETRY = OBSERVED_WITH_FAKE`; `W06_GUARANTEE = NOT_SATISFIED`; `F18_PRODUCT_CERTIFICATION = NOT_DEMONSTRATED`.

## 2. Los dos caminos de reejecución a cubrir

1. **Error de Engine:** `runtime.engine.chunk_worker_thread` captura excepciones de `stage_claimed_unit` y llama a `ControlPlaneRepository.abandon_execution`; este método fija `RETRYABLE_ERROR` (hasta agotar presupuesto) y `pick_task` selecciona `PENDING/RETRYABLE_ERROR`. La semántica de excepción no prueba ausencia de efecto externo.
2. **Lease expirado / Reconciler:** `apps.daemons.reconciler.ReconcilerDaemon._sweep_tasks` invoca `ControlPlaneRepository.recover_expired_g3_task` para G3; el método puede devolver una tarea sin receipt a `PENDING` bajo fencing/epoch. **Ausencia de receipt no prueba no inicio**; requiere clasificación durable antes de habilitar otra llamada.

El `chunk_result_receipts` existente conserva resultados confirmados y `execution_id`, pero no representa por sí solo los intentos inciertos anteriores a un segundo claim. En `stage_claimed_unit`, la respuesta se almacena **después** de ejecutar `processor.execute_chunk`; en `SyncProviderBridge` un timeout cancela el future local, sin cancelar efectos remotos ya iniciados.

## 3. Contrato mínimo que debe diseñarse/implementar en un acto separado

**No elegir todavía nueva tabla, columna ni servicio.** Primero contrastar si las estructuras autoritativas ya existentes permiten expresar una historia durable por `document_id + ast_hash + chunk_id + execution_id`, con momento de primera detección, resultado confirmado y disposición. Evitar una segunda fuente autoritativa para el mismo hecho y mantener `queue.db` como autoridad de leases de G3.

**Invariantes de comportamiento propuestos, derivados de NADR-F18-03 §§5.1–5.6 y F18-04 §5:**

1. **Antes de I/O:** persistir y verificar autoridad recuperable (lease + intento original) y el punto desde el que el efecto podría haber comenzado. Un crash en esa ventana debe clasificarse conservadoramente si no existe evidencia de no inicio, incluso aunque ello reduzca progreso automático.
2. **Resultado local confirmado:** conservar receipt durable exacto, generación, `execution_id` y proveniencia; publicar y finalizar idempotentemente sin volver a llamar al proveedor.
3. **No inicio demostrado:** permitir un reintento solo cuando un predicado recuperable de no inicio esté efectivamente probado; un `TimeoutError`, error de parseo posterior a I/O, expiración del lease o ausencia de receipt **no** bastan.
4. **Efecto incierto:** conservar un estado durable, distintivo de `PENDING`/`RETRYABLE_ERROR`, con primer momento de detección e identidad original; Engine, selector, Reconciler y cualquier resumer deben negar el retry automático, incluso después de reinicio y expiración del lease.
5. **Escalamiento:** permitir revisión/resolución por evidencia externa verificable; una reejecución excepcional requiere aceptación explícita del riesgo y trazabilidad contabilizable, nunca autorización implícita por TTL o retry budget.
6. **Compatibilidad:** `PRESERVE` no debe abrir un intento externo; mantener publicador G3/G5, fencing, proyección y casos `RESULT_STAGED` actuales. No migrar bases históricas sin procedimiento aprobado ni inventar exactly-once de proveedor.

**No basta** con una regla de `except TimeoutError` ni con un estado en memoria: el Reconciler y el reinicio deben respetar la misma decisión durable. La persistencia y la clasificación se deben verificar separadamente según F18-04.

## 4. Pruebas de aceptación de la corrección (futuras; no ejecutadas)

- `W06-A`: falla demostrable pre-I/O: **0 llamadas fake**; elegibilidad de retry solo con no inicio confirmado.
- `W06-B`: receipt durable tras respuesta: recuperación/proyección sin reinferencia tras nueva conexión o proceso.
- `W06-C`: fake acepta llamada y pierde respuesta: **1 llamada** total; intento `UNKNOWN` durable, no selección posterior; el `strict xfail` pasa a PASS únicamente después de la corrección real, nunca silenciándolo.
- `W06-D`: simular crash entre marca durable de intento y receipt; reiniciar Engine/Reconciler con el mismo SQLite temporal y comprobar **0 llamadas adicionales** sin disposición.
- `W06-E`: lease vencido + Reconciler con liderazgo vigente: no convierte un intento `UNKNOWN` en `PENDING`; niega autoridad vieja y mantiene identidad/primer timestamp.
- `W06-F`: una tarea `PRESERVE` y un plan mixto siguen publicándose normalmente; ninguna llamada extra ni regresión en tests de G3/G5.
- `W06-G`: autorización excepcional positiva con alcance y trazabilidad, solo después de definir quién tiene autoridad para otorgarla y la evidencia requerida.

Todas las futuras ejecuciones se limitarán inicialmente a `tmp_path`, SQLite descartable y fake de interfaz, sin keys ni pago. Extender a proveedor real, Docker, migraciones o operaciones sobre DB vigentes requiere autorización separada.

## 5. Decisión y continuidad

El owner autorizó los testigos W-06 y comunicó su resultado. **No se interpreta esa autorización como aprobación de editar automáticamente contratos FROZEN, migrar producción o elegir el mecanismo físico de persistencia.**

**Próximo entregable sugerido:** diseño de remediación mínima y tests offline `W06-D/E` que cubran reinicio y Reconciler; revisar el diff funcional antes de aprobar su aplicación. El plan de recuperación debe satisfacer tanto el caso `abandon_execution` como `recover_expired_g3_task`.

`W06_DIAGNOSTIC = CONFIRMED_WITH_FAKE` · `W06_REMEDIATION = PENDING` · `D1_D2_FORMAL_STATUS = UNCHANGED` · `PRODUCT_READINESS = NOT_DEMONSTRATED`.
