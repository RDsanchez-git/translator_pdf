# FASE_18.2_FAILURE_SCENARIO_MATRIX.md

**Documento:** `docs/architecture/adr/phase-18/reviews/FASE_18.2_FAILURE_SCENARIO_MATRIX.md`
**Versión:** 1.0.0
**Estado:** DONE
**Fecha:** 2026-10-10
**Derivado de:** `PHASE_18.2_EXECUTION_PLAN.md` v1.2.1 — Task 0.2.2
**Propósito:** Matriz formal de escenarios de fallo del modelo aprobado en ADR_F18.2 §8.1,
con mapeo a rutas de ejecución y contratos de validación requeridos.

---

## 1. MODELO DE FALLOS APROBADO (ADR_F18.2 §8.1)

| Escenario | Cobertura | Política SQLite |
|-----------|-----------|-----------------|
| Terminación coordinada (SIGTERM/SIGINT) | ✅ Cubierto | WAL + NORMAL |
| Terminación abrupta (SIGKILL) | ✅ Cubierto | WAL + NORMAL |
| Crash del proceso (excepciones no capturadas) | ✅ Cubierto | WAL + NORMAL |
| Pérdida de energía (power loss) | ❌ NO cubierto | Limitación aceptada |
| Fallo físico del almacenamiento | ❌ NO cubierto | Limitación aceptada |

**Política de durabilidad:** `WAL` + `synchronous=NORMAL` + `busy_timeout=30000`

---

## 2. RUTAS DE EJECUCIÓN EXTERNA IDENTIFICADAS

| ID Ruta | Componente | Punto de efecto externo | Authority pre-effecto | Lease check | Journal post-effecto |
|---------|-----------|------------------------|----------------------|-------------|---------------------|
| **R1** | `LLMWorkerDaemon` → `SyncProviderBridge` | `__main__.py:326` | ❌ No implementado | ✅ POST-effecto | ✅ `append_wal` |
| **R2** | `TranslationPipeline` → `AsyncDispatcher` | `dispatcher.py:105` | ❌ No implementado | ❌ AUSENTE | ❌ AUSENTE |

---

## 3. MATRIZ DE ESCENARIOS POR RUTA

### 3.1 Ruta 1: LLMWorkerDaemon (producción actual)

| Escenario | Comportamiento actual | Contrato NADR-F18-03 | Contrato NADR-F18-04 | Validación requerida |
|-----------|----------------------|----------------------|----------------------|---------------------|
| Crash pre-effecto | Lease persistido en `chunk_tasks`, task reelegible | ✅ Cumple §5.1 R1-R2 | ✅ Cumple §5.1 R1 | Chaos harness: crash antes de `execute()` |
| Crash post-effecto/pre-journal | Efecto externo completado, sin journal. Lease expira, reconciler reejecuta → **duplicación probable** | ❌ Viola §5.2 R5-R8 | ❌ Viola §5.3 R8-R10 | Chaos harness: crash entre `execute()` y `append_wal()` |
| Crash post-journal/pre-proyección | Journal como fuente de verdad, proyección reconstruible | ✅ Cumple §5.2 R5 | ✅ Cumple §5.3 R9 | Chaos harness: crash entre `append_wal` y checkpoint 3 |
| Pérdida de lease durante ejecución | Detectado POST-effecto (línea 328), lanza `OptimisticLockError`. No revierte efecto externo. | ✅ Cumple §5.1 R3 | N/A | Test de concurrencia: revocar lease durante `execute()` |
| SIGKILL (terminación abrupta) | WAL + NORMAL garantiza durabilidad bajo modelo | ✅ Cumple §5.1 R1-R2 | ✅ Cumple §5.1 R1-R4 | Chaos harness: SIGKILL en diferentes puntos |
| Power loss | NO cubierto por modelo. Limitación aceptada explícitamente. | N/A | N/A | Documentación de limitación |

### 3.2 Ruta 2: TranslationPipeline (AsyncDispatcher)

| Escenario | Comportamiento actual | Contrato NADR-F18-03 | Contrato NADR-F18-04 | Validación requerida |
|-----------|----------------------|----------------------|----------------------|---------------------|
| Crash pre-effecto | Sin authority, sin lease, sin journal. Task perdida. | ❌ Viola §5.1 R1-R2 | ❌ Viola §5.1 R1 | **IMPLEMENTACIÓN REQUERIDA** |
| Crash post-effecto/pre-journal | Sin authority, sin journal. Efecto externo completado, sin trazabilidad. Duplicación casi segura si se reintenta. | ❌ Viola §5.2 R5-R8 | ❌ Viola §5.3 R8-R10 | **IMPLEMENTACIÓN REQUERIDA** |
| Crash post-journal/pre-proyección | Sin journal, estado inconsistente. | ❌ Viola §5.2 R5 | ❌ Viola §5.3 R9 | **IMPLEMENTACIÓN REQUERIDA** |
| Pérdida de lease durante ejecución | Sin mecanismo de lease. No detecta pérdida de autoridad. | ❌ Viola §5.1 R3 | N/A | **IMPLEMENTACIÓN REQUERIDA** |
| SIGKILL (terminación abrupta) | Sin WAL, sin journal. Pérdida de estado. | ❌ Viola §5.1 R1-R2 | ❌ Viola §5.1 R1-R4 | **IMPLEMENTACIÓN REQUERIDA** |
| Power loss | NO cubierto por modelo. Limitación aceptada. | N/A | N/A | Documentación de limitación |

---

## 4. CONTRATOS DE VALIDACIÓN APROBADOS

| Contrato | Descripción | Escenarios cubiertos | Gate de validación |
|----------|-------------|---------------------|-------------------|
| **CV-01** | Convergencia bajo crash: tras crash en cualquier punto del flujo, el sistema recupera estado coherente sin duplicación no autorizada | Todos los escenarios de crash | Gate 4 |
| **CV-02** | Clasificación semántica: operaciones se clasifican correctamente como confirmadas/no-iniciadas/inciertas | Crash post-effecto/pre-journal | Gate 4 |
| **CV-03** | No-reejecución bajo incertidumbre: operaciones inciertas no se reejecutan automáticamente | Crash post-effecto/pre-journal | Gate 4 |
| **CV-04** | Idempotencia de aplicación: reaplicación de resultado confirmado no produce duplicación | Crash post-journal/pre-proyección | Gate 4 |
| **CV-05** | Reconstruibilidad de proyecciones: proyecciones reconstruibles desde journal tras recovery | Crash post-journal/pre-proyección | Gate 4 |
| **CV-06** | Fencing de autoridad obsoleta: workers con lease expirado no pueden iniciar nuevos efectos | Pérdida de lease durante ejecución | Gate 4 |

---

## 5. MATRIZ DE RESPONSABILIDADES DE PRUEBA

| Escenario | Harness requerido | Tipo de prueba | Gate |
|-----------|------------------|----------------|------|
| Crash pre-effecto | `game_day_1` extendido | Chaos (SIGKILL) | Gate 4 |
| Crash post-effecto/pre-journal | `game_day_1` extendido | Chaos (SIGKILL con mock LLM) | Gate 4 |
| Crash post-journal/pre-proyección | `game_day_1` extendido | Chaos (SIGKILL) | Gate 4 |
| Pérdida de lease | `test_fencing.py` | Unit + Integration | Gate 4 |
| SIGKILL en diferentes puntos | `game_day_1` extendido | Chaos (SIGKILL) | Gate 4 |
| Power loss | Documentación | Limitación aceptada | Gate 4 |
| Terminación coordinada | `game_day_1` existente | Chaos (SIGTERM) | Gate 4 |

---

## 6. COMPATIBILIDAD DE DATOS

| Escenario | Compatibilidad | Acción requerida |
|-----------|---------------|------------------|
| Datos persistidos antes de 18.2 | ✅ Compatible | Sin migración destructiva |
| Nuevos campos de trazabilidad | ⚠️ Requiere migración de esquema | Task 2.1.1 (NADR-F18-04 §5.1) |
| Clasificación semántica | ⚠️ Requiere extensión de modelos | Task 1.1.3 (NADR-F18-03 §5.2) |

---

## 7. PREFLIGHT DE ROLLBACK/RECOVERY

| Escenario | Rollback seguro | Condición |
|-----------|----------------|-----------|
| Rollback de código | ✅ Seguro si no hay efectos externos inciertos | Verificar queue de operaciones inciertas |
| Rollback con operaciones inciertas | ❌ NO seguro | Puede retroceder conocimiento local sin revertir efecto externo |
| Forward recovery | ✅ Seguro | Completar transiciones pendientes desde journal |

---

**Nota de Gobernanza:** Esta matriz es un artefacto de trabajo del Gate 0 (Task 0.2.2).
Define los escenarios que deben validarse en Gate 4 y los contratos que deben satisfacerse.