# W06-R1 — Revisión de corrección fail-closed para efectos externos inciertos

**Fecha:** 2026-11-06.
**Estado:** `REVIEW ONLY / DRAFT PR / NOT MERGED / NOT PRODUCTION CERTIFIED`.
**Base funcional:** `pipeline_stabilization` en commit `5cdff2439feae4d09e30f41241459977e9c14972`.
**Motivo:** testimonio W-06 del owner: `3 passed, 1 xfailed, 2 warnings`; el fake recibió dos solicitudes para un resultado externo incierto.
**Norma aplicada (sin editarla):** NADR-F18-03 §5.2 R5–8, §5.3 R9–15, §5.6 R22; NADR-F18-04 §5.3 R8–10, §5.5 R15–16.
**Alcance permitido:** propuesta correctiva revisable y pruebas offline. No autorización de migración retroactiva, despliegue o proveedor real.

## Frontera de seguridad corregida (propuesta)

- `ControlPlaneRepository.mark_g3_external_unknown`: conserva en `queue.db` el `execution_id`, un estado no ejecutable `G3_EXTERNAL_UNKNOWN` y `error_log` estructurado con primera detección y tipo de causa, sin persistir respuesta, prompt ni secretos. CAS de `worker + execution_id`; no exige lease aún vivo para clasificar una incertidumbre posterior al efecto.
- `runtime.engine`: una excepción de inferencia `TRANSLATE/PARTIAL` se trata conservadoramente como `UNKNOWN`, nunca como `RETRYABLE_ERROR`; un `CircuitOpenError` conocido como rechazo local pre-efecto sigue liberando la tarea. `PRESERVE` conserva su bypass y recuperación. La FSM no se marca falsamente como `COMPLETED` si quedan efectos `UNKNOWN`.
- `ControlPlaneRepository.recover_expired_g3_task` y Reconciler: un lease LLM vencido sin receipt se clasifica `UNKNOWN`, salvo que el manifiesto verificado lo identifique inequívocamente como unidad `PRESERVE`, en cuyo caso sigue recuperándose a `PENDING`. Se conserva fencing de liderazgo/epoch/versión.
- `pick_task`, selector de documentos y materialización mantienen sus predicados actuales: `G3_EXTERNAL_UNKNOWN` no es runnable, no es recibo y no se publica.
- El `W06` test de seguridad deja de estar marcado `XFAIL`: debe ser PASS. Se añaden cobertura offline de reinicio, SQLite reabierto y Reconciler sobre unidad traducible.

## Reservas técnicas que impiden certificar F18 integral

1. Esta revisión trata de **cierre conservador de la vía de reintento automático**, no de resolución final de `UNKNOWN` ni de re-ejecución excepcional aprobada. Falta un instrumento específico de escalamiento, auditoría de disposición autorizada y las métricas F18-05.
2. La fila `chunk_tasks` conserva solo la **identidad del último intento** y la primera detección de su estado incierto. No se acredita aún un historial general de múltiples intentos / intent identity por llamada ni CP-08 completo.
3. La distinción `NOT_STARTED` se prueba cuando un guard previo impide físicamente llegar al fake; ante fallo ambiguo o crash de proceso, el sistema elige `UNKNOWN`. Es seguro por defecto pero puede bloquear progreso hasta revisión humana.
4. La comprobación `manifest_sha256` para `PRESERVE` valida identidad y tipo de unidad, pero no sustituye los tests de cobertura científica ni el contrato de AST completo.
5. El fake de interfaz no permite concluir ausencia universal de duplicación, especialmente si hay reintentos internos de SDK/proveedor. No hay ensayos de red real, crash físico ni disponibilidad de terceros.
6. Los tests de esta rama deben ejecutarse en el checkout y venv del owner; **no se declaran PASS en este documento**. No tocar bases reales ni actualizar estados FROZEN.

## Verificaciones de aceptación para el owner

```powershell
git fetch origin
git switch w06-r1-review
python -m pytest tests/integration/test_w06_g3_uncertain_effect_offline.py -q -ra
python -m pytest tests/integration/test_g3_b4_9_reconciler_fencing.py tests/integration/test_g3_b4_8_preserve_engine.py tests/integration/test_g3_b4_3a_engine_staging.py tests/integration/test_g3_b4_3b_publication_recovery.py -q -ra
git diff --check origin/pipeline_stabilization...HEAD
```

**Criterio:** cero `XFAIL` esperado de W-06, ningún segundo contacto con el fake incierto, reinicio no reintenta, Reconciler no transforma desconocidos a `PENDING`, `PRESERVE` conserva requeue seguro. Si alguna prueba falla, **no fusionar**; registrar traza y diagnosticar sin rebajar el oráculo.

**No cierre:** `W06-R1 = DRAFT REVIEW`; `W06 TEST RESULT = OWNER RUN PENDING`; `F18-INTEGRAL = NOT CERTIFIED`; `D1/D2 FORMAL = UNCHANGED`.
