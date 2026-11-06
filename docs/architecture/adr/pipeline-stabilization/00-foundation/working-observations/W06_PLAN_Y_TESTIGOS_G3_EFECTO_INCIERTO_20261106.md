# W-06 — Testigos focales de efecto externo incierto en G3

**Fecha:** 2026-11-06.
**Estado:** `TEST PREPARED / NOT EXECUTED IN PROJECT ENVIRONMENT / NON-NORMATIVE`.
**Autorización:** el owner autorizó expresamente W-06 en conversación, limitado a prueba offline, aislada, sin Groq real ni alteración de código funcional o evidencias históricas.
**Sujeto estático:** rama `pipeline_stabilization`, corte `7a94fec90f4d15a09493b8b3d5d1afde2c103376`.
**Definición del testigo:** Atlas `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` §8.5.2 (W-06); contrato propuesto D-1/D-2 §7, frontera 5; NADR-F18-03/04/05 FROZEN.

## Objetivo y límites

Distinguir `NOT_STARTED`, `CONFIRMED` y `UNKNOWN` para llamadas a proveedor externo. Nunca equiparar `no hay receipt` con `el proveedor nunca recibió la solicitud`. Los testigos se ejecutan con fake Python local de **interfaz** y SQLite temporales del fixture `tmp_path`; no hacen HTTP ni evidencian costo/cobro real de proveedor. No hay Docker, keys ni escritura en `infra/db/*.db` del proyecto. No hay cambio del tratamiento de retry en este batch.

## Test preparado

`tests/integration/test_w06_g3_uncertain_effect_offline.py` (agregado prospectivo). Los siguientes casos tienen alcances independientes:

| Caso | Inyección y oráculo | Resultado conocido al preparar |
|---|---|---|
| `not_started_expired_lease` | Lease inválido antes de `stage_claimed_unit`; el fake no puede recibir una solicitud ni generarse receipt. | Implementación inspeccionada; ejecución pytest pendiente. |
| `confirmed_response_durable_receipt` | Un fake devuelve respuesta G3 válida; la fila `RESULT_STAGED` y `raw_response/sha256/execution_id` se verifican con conexión SQLite independiente; no hay segundo claim. | Implementación inspeccionada; ejecución pytest pendiente. |
| `observed_uncertain_effect_gets_replayed` | Fake recibe primera solicitud y lanza timeout *después de aceptarla*; en una segunda invocación entrega una respuesta válida; se observa si G3 vuelve a llamarlo en el mismo `run_pipeline`. | Hipótesis de reintento deducida del código; **no confirmada por ejecución**. |
| `contract_oracle_never_automatically_repeats_unknown_effect` | Mismo caso incierto, pero oráculo exigente: un efecto `UNKNOWN` no debe disparar una segunda llamada sin disposición autorizada. | `strict xfail`: falla esperada documentada, **no un PASS de garantía**. Un `XPASS` provoca fallo y exige reconciliación. |

## Justificación estática del riesgo

- `runtime/chunk_staging.py`: el lease se comprueba antes del proveedor, pero el receipt durable se escribe después de recibir el resultado.
- `apps/llm_workers/sync_bridge.py`: ante `TimeoutError`, se cancela el future local, sin demostrar que el efecto remoto no ocurrió.
- `runtime/engine.py`: el worker captura excepciones y llama a `ControlPlaneRepository.abandon_execution`; mientras queden tareas `PENDING/RETRYABLE_ERROR`, un hilo de la misma corrida puede reclamarlas.
- `infra/db/control_repo.py`: `abandon_execution` establece `RETRYABLE_ERROR` hasta agotar presupuesto; `pick_task` permite reclamar `RETRYABLE_ERROR`; el recuperador de leases G3 vencidos también puede regresar a `PENDING` sin receipt. Hay fencing de escritura, pero el fencing local de receipt no deduplica un efecto ya aceptado por un servidor externo.

**Clasificación provisional:** `EXTERNAL_EFFECT_UNCERTAINTY_RISK = STATICALLY_SUPPORTED`; `W06_DYNAMIC_VERDICT = NOT_EXECUTED`. No inferir una doble facturación real ni el incumplimiento global de F18 a partir de este test de fake.

## Procedimiento seguro en el checkout del owner

Precondiciones: HEAD incluye este test; `git status` limpio; venv existente y dependencias del repo ya instaladas. **No** inicializar Docker ni bootstrap de SQLite del proyecto.

```powershell
git status
python -m pytest tests/integration/test_w06_g3_uncertain_effect_offline.py -q -ra
```

Registrar salida completa, versión/commit, conteos `passed/xfail/failed/xpass`. El test es prospectivo: no modificar ni recalibrar el oráculo de `UNKNOWN` para convertir riesgo en PASS. Un resultado esperado con `XFAIL` es **evidencia de brecha**, no aceptación de W-06. Si aparece un `FAILED` no previsto, detener y conservar el log antes de cambiar componentes.

## Pasos siguientes, no autorizados automáticamente

Después de obtener la corrida reproducible, decidir bajo autoridad contractual F18 el mínimo delta de clasificación durable pre-I/O/intent history y disposición `UNKNOWN`, incluyendo recuperación por Reconciler, y ensayar nuevamente. No añadir tablas, migrar bases, usar claves reales, relajar fencing o desplegar un nuevo daemon solo por este documento. W-07/W-08/CP-08 permanecen frentes separados.

**No cierre:** `W06_TESTS_PREPARED`; `W06_RUNTIME_EVIDENCE=PENDING`; `F18_SAFETY_CERTIFICATION=NOT_DEMONSTRATED`; `PRODUCT_READINESS=NOT_DEMONSTRATED`.
