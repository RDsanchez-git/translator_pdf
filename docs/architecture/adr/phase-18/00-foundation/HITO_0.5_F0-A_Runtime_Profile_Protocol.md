# HITO_0.5_F0-A_Runtime_Profile_Protocol.md

**Estado:** FROZEN v1.2.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02 (v1.2.0)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación. Define los requisitos del protocolo de medición externa para F0-A basándose en la infraestructura de observabilidad existente.
**Evidencia Forense Vinculante:** `FASE0_AUDIT_CHARTER.md` §5.3, §5.5, §6, §9; `HITO_0.1` a `HITO_0.4`; `HITO_0.6_WORKLOAD_ANCHOR_RECONCILIATION` v1.0.0; `HITO_0.7_F0-A_RUNTIME_PROFILE_BASELINE` v1.0.0; `NADR-F17BIS-24` R11; `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.4 R16-R19; `ENGINEERING_PRINCIPLES.md`; Auditoría de código [A1]-[A10].
**Mandato:** Definir los requisitos del protocolo de medición externa para F0-A, aprovechando la infraestructura de telemetría existente (`core/telemetry`, `core/metrics`) y observación externa a nivel de sistema operativo, garantizando evidencia válida, reproducible y no contaminante.
**Síntesis:** El sistema posee infraestructura de telemetría por chunk/etapa y métricas de proveedor (capacidad confirmada), pero el entry point de F0-A (`run_regression.py`) no las consume en el protocolo ejecutado: es un gap de integración, no de capacidad. El perímetro normativo es consumo read-only del anchor canónico (mandatado por NADR-25 §7 y NADR-26 §5.1 R2/§5.4) con writes exclusivamente efímeros; el workload separado queda reservado para aumento de stress (GAP-0.3-02). El canal externo de memoria/CPU debe ser OS-level (Win32) con cobertura de árbol de procesos: el canal psutil fue falsado empíricamente en esta topología de Windows (HITO_0.7).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-02 | Emisión inicial con suposiciones no verificadas sobre ausencia de métricas. |
| 1.1.0-FROZEN | 2026-10-02 | Corrección forense basada en auditoría de código [A1]-[A10]: confirmación de `core/telemetry`, `core/metrics`, `@track_latency`; separación requisitos vs especificaciones; eliminación de `memory_maps` (inválido en Windows). |
| 1.2.0-FROZEN | 2026-10-02 | Reconciliación epistémica post-ejecución y post-revisión: (1) N=3 reformulado como mínimo exploratorio preregistrado; suficiencia estadística NO DEMOSTRADA (H-0.5-C). (2) Umbrales numéricos de §16.2 etiquetados como heurísticas operativas provisionales y sanity gates de instrumento; la forma de invalidación proviene de Charter §9. (3) Reconciliación explícita de criterios de este HITO vs gates de aceptación de HITO_0.7. (4) E-0.5-002/003 y GAP-0.5-02 reframados como gap de integración (capacidad existente no consumida por el entry point F0-A). (5) E-0.5-001/GAP-0.5-01 reconciliados con HITO_0.6 v1.0.0: lectura read-only de canonical mandatada por NADR-25 §7 y NADR-26 §5.1 R2/§5.4 R16-R19; separación aplica a writes/sellado/stress. (6) H-0.5-B corregida según evidencia de HITO_0.7 v1.0.0: canal RSS/CPU de psutil falsado en topología launcher-hijo de Windows; el protocolo manda muestreo OS-level (Win32) con cobertura de árbol. |

---

## 1. RESUMEN EJECUTIVO

Se auditó el código fuente del proyecto para verificar la disponibilidad de métricas sin instrumentación interna nueva (principio **Reuse Before Invent**). El análisis forense ([A1]-[A10]) reveló que el sistema **ya posee** una infraestructura de observabilidad robusta. La ejecución real de F0-A (HITO_0.7) validó y falsó partes de este protocolo; esta versión incorpora esa evidencia sin re-medir.

**Hallazgo central:**

> El protocolo de medición de F0-A no requiere crear nueva instrumentación científica: debe explotar la telemetría existente (`core/telemetry`, `core/metrics/summary.py`, `@track_latency`) para métricas de pipeline/proveedor, y usar **observación externa a nivel de sistema operativo** (Win32 `GetProcessMemoryInfo` con cobertura de árbol de procesos) para memoria/CPU/I/O. La capacidad de telemetría existe pero el entry point de F0-A no la consume: es un gap de integración, no de capacidad.

**Hechos observados confirmados:**

1. **Infraestructura de telemetría existente (E-0.5-002):** `SQLiteTelemetryGateway`, `ProductionTelemetryEvent` (con `latency_ms`, `input_tokens`, `output_tokens`) y `TelemetryAnalyzer` implementados. **Capacidad confirmada; integración en `run_regression.py` ausente** (GAP-0.5-02).
2. **Métricas de proveedor capturadas en runtime productivo (E-0.5-003):** adapters y dispatcher miden `latency_ms`, tokens y `quota_wait_seconds`. **No medibles vía `run_regression.py`**, que no invoca providers (Deferred Question F0-D).
3. **Perímetro normativo reconciliado (E-0.5-001):** el consumo read-only del anchor canónico está mandatado (NADR-25 §7; NADR-26 §5.1 R2, §5.4 R16-R19; Charter §5.2/§5.8) con writes exclusivamente efímeros. La separación física aplica a writes, sellado y aumento de stress (GAP-0.3-02), no a la lectura.
4. **Canal de memoria/CPU externo corregido (E-0.5-005):** psutil `memory_info().rss` y `cpu_times()` sobre el launcher fueron falsados empíricamente (3.4 MB / 0.0 s frente a 77.0 MB / 1.448 s reales del worker). El canal válido es OS-level con cobertura de árbol (HITO_0.7, instrumento v3-final).

**Veredicto:** El protocolo de F0-A es la orquestación de capacidades existentes + observación externa OS-level. Los umbrales numéricos de este documento son heurísticas operativas provisionales; la regla de calibración del Charter §9 permanece sin instanciar numéricamente hasta disponer de métricas por técnica (F0-D).

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Este HITO define **requisitos** del protocolo (qué debe medir, bajo qué condiciones, usando qué fuentes), no **especificaciones de implementación** (cómo se programa el script). Los detalles del script pertenecen al Execution Plan de F18. La v1.2.0 es reconciliación documental sobre evidencia ya producida (HITO_0.6, HITO_0.7); no re-mide.

### 2.2 Método forense
1. Cargar fuentes normativas (Charter §5.3, §5.5, §6, §9; NADR-24 R11, NADR-25 §7, NADR-26 §5.1/§5.4).
2. Auditar código existente ([A1]-[A10]) para verificar disponibilidad de métricas (Reuse Before Invent).
3. Definir requisitos de medición basados en lo que el sistema ya puede proporcionar.
4. Establecer la **forma** de los criterios de invalidación (Charter §9) y etiquetar los números como heurísticas provisionales.
5. Documentar la regla de calibración preregistrada (Charter §9) sin instanciar thresholds numéricos prematuramente.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `FASE0_AUDIT_CHARTER.md` | §5.3, §5.5, §6, §9 | 100% auditado |
| `NADR-F17BIS-24/25/26` | R11; §7; §5.1 R2, §5.4 R16-R19 | 100% auditado |
| `core/telemetry/` | `gateway.py`, `models.py`, `analyzer.py`, `ports.py` | 100% auditado (Evidencia [A3]) |
| `core/metrics/` | `summary.py`, `pricing.py` | 100% auditado (Evidencia [A4]) |
| `core/utils/telemetry.py` | `setup_distributed_logger`, `@track_latency` | 100% auditado (Evidencia [A5]) |
| `apps/llm_workers/` | `adapters.py`, `dispatcher.py`, `rate_limiter.py` | 100% auditado (Evidencia [A6]) |
| `infra/db/` | `bootstrap.py`, `connection.py` (PRAGMAs, env vars) | 100% auditado (Evidencia [A7]) |
| `tools/evaluation/run_regression.py` | Superficie de imports/escritura | 100% auditado |
| `HITO_0.3`, `HITO_0.6`, `HITO_0.7` | Reconciliaciones y baseline | Referenciados |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Charter | `FASE0_AUDIT_CHARTER.md` §5.3, §5.5, §6, §9 | Requisitos de medición externa y calibración |
| NADR | `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.4 R16-R19; `NADR-F17BIS-24` R11 | Autoridad primaria: ejecución read-only sobre canonical mandatada; inmutabilidad durante ejecución; verificación de identidad pre-run |
| Código | `core/telemetry/`, `core/metrics/`, `core/utils/telemetry.py` | Evidencia de infraestructura de observabilidad existente |
| HITO previo | `HITO_0.3_F0-F` v1.3.0; `HITO_0.6` v1.0.0; `HITO_0.7` v1.0.0 | Reconciliaciones y baseline físico |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.5-001: Perímetro normativo de medición sobre el anchor (reconciliado)
* **Archivo Fuente Primario:** `HITO_0.3_F0-F` v1.3.0; `HITO_0.6_WORKLOAD_ANCHOR_RECONCILIATION` v1.0.0; `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.4 R16-R19; `FASE0_AUDIT_CHARTER.md` §5.2, §5.8.
* **Declaración Observada:** La v1.1.0 de este HITO afirmó que "F0-A no puede ejecutarse hasta que exista workload corpus separado" (GAP-0.5-01 BLOCKING).
* **Observed:** NADR-25 §7 manda ejecutar el verification entry point contra el corpus canónico sellado; NADR-26 §5.4 R16-R19 restringe **mutación durante** la ejecución y R18 exige invalidar el uso como referencia si se detecta modificación; Charter §5.2/§5.8 permiten medición con writes efímeros y reuso de PDFs como carga. No existe cláusula de no-lectura/no-ejecución.
* **Required:** Charter §5.2 ("NO MUTACIÓN de estado normativo"); NADR-24 R11 (identidad del corpus verificada pre-ejecución).
* **Hallazgo Forense:** La separación física aplica a **writes, sellado y aumento de stress**, no a la lectura read-only. El consumo read-only con perímetro de writes efímero es conforme y mandatado. Confirmado empíricamente por HITO_0.7 (snapshot pre=post `4cf031d1…edb90`).
* **Consecuencia Arquitectónica:** GAP-0.5-01 reclasificado (ya no BLOCKING para F0-A). El workload separado permanece como necesidad real únicamente para stress docs (GAP-0.3-02).
* **Estado:** RECONCILED (per HITO_0.6 v1.0.0; confirmado por HITO_0.7)
* **Severidad:** P0 (normativa)

### Evidencia E-0.5-002: Infraestructura de telemetría por etapa/chunk existente (capacidad ≠ integración)
* **Archivo Fuente Primario:** `core/telemetry/models.py`, `core/telemetry/gateway.py`, `core/utils/telemetry.py`
* **Símbolo Auditado:** `ProductionTelemetryEvent`, `SQLiteTelemetryGateway`, `@track_latency`
* **Declaración Observada:** Eventos de telemetría con `execution_id`, `chunk_id`, `event_type`, `latency_ms`, `input_tokens`, `output_tokens`; decorador `@track_latency` que emite logs JSON con `duration_ms`.
* **Observed:** La **capacidad** de medir latencia y tokens por chunk/etapa existe en el código.
* **Required:** Charter §6 exige métricas por etapa.
* **Hallazgo Forense:** **CONFIRMADA como capacidad.** Sin embargo, el entry point de F0-A (`run_regression.py`) **no activa ni consume** esta telemetría en el protocolo ejecutado (HITO_0.7): es un **gap de integración**, no de capacidad.
* **Consecuencia Arquitectónica:** Reutilizar `TelemetryAnalyzer` y `TranslationAuditSummary` cuando el Execution Plan integre el canal; hasta entonces, métricas por etapa = Deferred Question (F0-D).
* **Estado:** CONFIRMADA (capacidad) / OPEN (integración, GAP-0.5-02)
* **Severidad:** P0

### Evidencia E-0.5-003: Métricas de proveedor capturadas en runtime productivo (no medibles vía F0-A)
* **Archivo Fuente Primario:** `apps/llm_workers/adapters.py`, `apps/llm_workers/dispatcher.py`, `apps/llm_workers/rate_limiter.py`
* **Símbolo Auditado:** `latency = (time.monotonic() - start_time) * 1000`, `quota_wait_seconds`
* **Declaración Observada:** Adapters miden `latency_ms`, `input_tokens`, `output_tokens`; rate limiter registra `quota_wait_seconds` y `quota_reservation_attempts`.
* **Observed:** Las métricas de proveedor se generan en el runtime productivo (daemon/dispatcher), no en `run_regression.py`.
* **Required:** Charter §6 exige "provider latency, tokens, retries".
* **Hallazgo Forense:** **CONFIRMADA como capacidad del runtime productivo.** **NO MEDIBLE vía `run_regression.py`**, que no importa ni invoca providers (HITO_0.7). Deferred Question con destino F0-D/F18.
* **Consecuencia Arquitectónica:** El baseline de providers requiere un instrumento distinto (F0-D) sobre el dispatcher con credenciales activas.
* **Estado:** CONFIRMADA (capacidad) / DEFERRED (medición F0-A)
* **Severidad:** P0

### Evidencia E-0.5-004: SQLite statistics disponibles
* **Archivo Fuente Primario:** `infra/db/bootstrap.py`, `infra/db/connection.py`
* **Símbolo Auditado:** `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=30000`, `PRAGMA wal_checkpoint(TRUNCATE)`; env vars `FSM_DB_PATH`, `QUEUE_DB_PATH`
* **Observed:** PRAGMAs configurados y observables; rutas de DB configurables por entorno, habilitando perímetro efímero.
* **Required:** Charter §5.3 exige "SQLite statistics"; Charter §5.2 exige writes efímeros.
* **Hallazgo Forense:** **CONFIRMADA.** En la ejecución F0-A las DBs efímeras no fueron creadas (run_regression no toca infra.db), confirmando superficie de escritura mínima.
* **Estado:** CONFIRMADA (Reuso viable)
* **Severidad:** P1

### Evidencia E-0.5-005: Canal psutil de RSS/CPU falsado en topología Windows; mandato OS-level con tree-monitoring
* **Archivo Fuente Primario:** `HITO_0.7_F0-A_RUNTIME_PROFILE_BASELINE` v1.0.0; diagnóstico de árbol de procesos (launcher 3.4 MB / 0.0 s vs worker 77.0 MB / 1.448 s).
* **Declaración Observada:** `psutil.Process.memory_info().rss` y `cpu_times()` sobre el proceso lanzado reportaron 3.4 MB / 0.0 s; el worker hijo real consumió 77.0 MB / 1.448 s (canal Win32 `GetProcessMemoryInfo`, `PeakWorkingSetSize` del kernel).
* **Observed:** En este venv de Windows, `sys.executable -m ...` spawnea un child worker; el launcher no computa. Medición monoproceso es estructuralmente inválida aquí.
* **Required:** Charter §5.3 (medición externa válida); criterios de sanidad instrumental.
* **Hallazgo Forense:** **H-0.5-B RECHAZADA tal como estaba formulada.** El protocolo debe mandar muestreo OS-level (Win32 `GetProcessMemoryInfo`, pico del kernel retroactivo) con cobertura recursiva del árbol de procesos, perímetro documentado (worker identificado como componente del pipeline; auxiliares excluidos y registrados por PID). psutil queda para orquestación de ciclo de vida, no como canal de memoria/CPU.
* **Consecuencia Arquitectónica:** Todo instrumento futuro de F18 (F0-D, profiling, tracing) debe usar tree-monitoring en este entorno (platform note de HITO_0.7).
* **Estado:** CONFIRMADA (canal corregido y validado en HITO_0.7, instrumento v3-final)
* **Severidad:** P0

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.5-01** | Workload separado como bloqueo físico de F0-A. Reclasificado: separación aplica a writes/sellado/stress; lectura read-only mandatada. | E-0.5-001 | NADR-25 §7, NADR-26 §5.4, Charter §5.2 | **Reconciliado en HITO_0.6 v1.0.0** | RECONCILED |
| **GAP-0.5-02** | Telemetría existente no activada/consumida por `run_regression.py` en el protocolo F0-A: gap de integración, no de capacidad. Métricas por etapa = Deferred. | E-0.5-002 | Charter §6 | **Fase 18** (F0-D / Execution Plan) | OPEN |
| **GAP-0.5-03** | Canal externo de memoria/CPU: psutil falsado en topología Windows; mandato OS-level con tree-monitoring. Instrumento corregido y validado en HITO_0.7 (v3-final). | E-0.5-005 | Charter §5.3 | **Cerrado por instrumento validado** | CLOSED (workaround validado) |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.5-A | El sistema posee infraestructura de telemetría y métricas por etapa/chunk reutilizable sin instrumentación nueva. | **CONFIRMADA (capacidad); integración OPEN** | E-0.5-002, E-0.5-003, GAP-0.5-02 | El protocolo explota capacidad existente; la integración en el entry point F0-A es tarea del Execution Plan/F0-D. |
| H-0.5-B | `psutil` puede capturar las métricas de proceso externas requeridas (RSS, CPU, I/O) en Windows. | **RECHAZADA (tal como estaba formulada)** | E-0.5-005 | El protocolo manda canal OS-level Win32 con tree-monitoring; psutil solo para ciclo de vida. |
| H-0.5-C | 3 repeticiones constituyen el mínimo exploratorio preregistrado suficiente para estimar variabilidad inicial. | **SUPPORTED (exploratorio); suficiencia NO DEMOSTRADA** | Estadísticas de HITO_0.7 (CV wall 0.41%) | Suficiencia se evalúa por estabilidad observada; ampliación de muestras documentada si procede. No invocar "significancia estadística" para N=3. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cuáles son los requisitos del protocolo de medición?

**Respuesta forense:**

1. **Fuentes de Métricas (Reuso + OS-level):**
   - **Por etapa/chunk:** `TelemetryAnalyzer` / logs JSON de `@track_latency` **cuando el Execution Plan integre el canal** (GAP-0.5-02); hasta entonces, Deferred.
   - **Proveedor:** `TranslationAuditSummary` / `envelope.telemetry` del runtime productivo; **no medible vía `run_regression.py`** (Deferred F0-D).
   - **Proceso (Externo, mandato):** Win32 `GetProcessMemoryInfo` (`WorkingSetSize`, `PeakWorkingSetSize` del kernel) con cobertura recursiva del árbol de procesos; perímetro documentado (worker identificado; auxiliares excluidos y registrados por PID). psutil solo para ciclo de vida. Platform note: en este venv de Windows la medición monoproceso es estructuralmente inválida.
   - **SQLite:** `PRAGMA` post-ejecución sobre DBs del perímetro efímero, antes de su limpieza.

2. **Condiciones de Corrida:**
   - **Hardware envelope:** documentar envelope real; separar **host envelope** (RAM/CPU) de **accelerator envelope** (GPU/VRAM): si la medición no ejerce GPU, declarar N/A, no "non-conformant".
   - **Perímetro efímero:** writes solo a `--output-dir` y DBs temporales vía env vars (`FSM_DB_PATH`, `QUEUE_DB_PATH`); limpieza de telemetría limitada a su propia DB; nunca tocar DBs operacionales ni el anchor.
   - **Identidad del anchor:** verificar `manifest_hash` contra el sello declarado antes de ejecutar (NADR-24 R11) y reportarlo en el baseline.
   - **Integridad del anchor:** snapshot SHA-256 pre/post (manifest + pdf/ + ground_truth/); mutación detectada ⇒ invalidación (NADR-26 R18).
   - **Repeticiones:** mínimo exploratorio preregistrado de 3; suficiencia evaluada por estabilidad observada (CV) con ampliación documentada si procede.
   - **Estado inicial:** cold cache de telemetría y DBs efímeras.

3. **Persistencia:**
   - JSON autocontenido: metadata de hardware y canal de memoria, métricas por repetición (incluyendo serie de WS y PIDs observados), ancla científica del reporte CV (coverage, verdict, NSS), integridad del anchor, estadísticas agregadas y criterios de invalidación aplicados.
   - Ubicación: `reports/f0a_baseline/baseline_profile_YYYYMMDD_HHMMSS.json`.

**Nota:** El diseño detallado del script wrapper pertenece al Execution Plan de F18, no a este HITO.

### 16.2 ¿Cuáles son los criterios de invalidación del baseline?

**Respuesta forense:**

La **forma** de los criterios proviene de Charter §9 (congelada): workload insuficiente, comportamiento patológico, hardware no representativo, outliers/varianza no explicados, medición contaminada. Los **números** siguientes son heurísticas operativas provisionales y sanity gates de instrumento, no reglas calibradas:

1. **Workload insuficiente (heurística de presión):** peak RSS < 20% de RAM disponible o CPU utilization < 30% ⇒ sospecha de carga insuficiente; requiere justificación o ampliación de workload (GAP-0.3-02).
2. **Sanity gates de instrumento:** peak WS del worker ∉ [20, 200] MB o CPU total ≤ 0.1 s ⇒ canal de medición roto (ej. artefacto de launcher), no baseline.
3. **Comportamiento patológico:** crashes, OOM kills, o timeouts de provider > 5% de requests.
4. **Hardware no representativo:** envelope real divergente del target sin documentación de alcance (host vs accelerator).
5. **Varianza inaceptable:** CV de `wall_time` o peak WS > 20% sin causa identificada.
6. **Medición contaminada:** overhead del wrapper > 5% del CPU total medido.
7. **Mutación del anchor:** snapshot pre ≠ post (NADR-26 R18).
8. **Exit codes de medición inválida:** exit ∈ {3, 4} (baseline integrity / execution failure); exit ∈ {0, 1, 2} son veredictos científicos válidos como medición (NADR-27, DF-10).

**Reconciliación con HITO_0.7:** los criterios (1) son heurísticas de **presión de workload**; los (2) son **sanity gates de instrumento** (detectan canal roto, como el artefacto de 3.4 MB del launcher). Propósitos distintos, ambos provisionales, ninguno calibrado. La transición entre los criterios de esta v1.2.0 y los gates de aceptación aplicados en HITO_0.7 queda documentada aquí.

**Implicación:** Si se invalida, abrir `HITO_0.x_F0-A_re-baseline` documentando causa y repitiendo bajo condiciones corregidas (Charter §9).

### 16.3 ¿Cuál es la regla de calibración preregistrada?

**Respuesta forense:**

Se adopta textualmente la regla del **Charter §9**: métrica → dirección → regla de decisión → threshold derivado del baseline. Con **MDE, Δ y ε aún abiertos, no existen thresholds numéricos**: F0-A aporta únicamente el lado baseline de la función. **Ninguna técnica queda calibrada por F0-A**: faltan CPU-time por etapa (process pools), allocations por hotspot (object pools/zero-copy) y peak RSS por documento grande con p95 (lazy loading).

| Técnica | Métrica + regla de decisión | Calibración desde F0-A |
|---|---|---|
| SyncProviderBridge elision | latencia p95 por etapa I/O, ↓, sin ↑RSS | umbral = p95 baseline × (1 − δ); δ = max(MDE, ruido medido) — requiere métricas por etapa (F0-D) |
| process pools | CPU-time TED/extraction, ↓ | umbral = CPU baseline × (1 − δ); costo IPC ≤ fracción preregistrada de la ganancia — requiere descomposición por etapa |
| object pools / zero-copy | allocations y peak RSS en hotspot, ↓ | umbral = baseline − Δ significativo — requiere allocations por hotspot |
| lazy loading | peak RSS por doc grande, ↓, sin ↑wall p95 | umbral RSS = baseline × (1 − δ); wall p95 ≤ baseline + ε — requiere RSS por documento |

**Implicación:** La instanciación numérica ocurre en el Execution Plan/F0-D con protocolo preregistrado, no en este HITO ni en el baseline v3-final.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-01** | Fork de concurrencia | E-0.5-002, E-0.5-005 | Baseline F0-A disponible (wall/CPU/WS); métricas por etapa pendientes | **Fase 18** (F0-B/F0-D) |
| **DC-03** | Determinismo observable por proveedor | E-0.5-003 | Capacidad en runtime productivo; no medible vía run_regression | **Fase 18** (F0-D) |
| **DC-07** | Tiers 8k/32k/1M o batch = f(budgets) | E-0.5-002, E-0.5-003 | Métricas de tokens/latencia disponibles en productivo | **Fase 18** (F0-D) |

---

## 19. APÉNDICE NO NORMATIVO -- RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Workload insuficiente | Si el perfil SMOKE no ejerce presión suficiente, el baseline no revela cuellos reales; mitigado por heurística (1) y GAP-0.3-02. | Medio | §16.2(1), GAP-0.3-02 |
| Telemetría no integrada | Si el Execution Plan no activa el canal, las métricas por etapa siguen diferidas. | Alto | GAP-0.5-02 |
| Medición monoproceso en Windows | Tree-monitoring obligatorio; single-process estructuralmente inválido en este venv. | Alto | E-0.5-005 |
| Confusión heurística ↔ threshold calibrado | Tratar los números provisionales como reglas calibradas violaría Charter §9 y el preregistro. | Alto | §16.2, §16.3 |
| Varianza alta entre repeticiones | CV > 20% exige ampliación de muestras documentada. | Medio | H-0.5-C, §16.2(5) |

---

## 21. CIERRE DEL HITO 0.5

Este HITO establece los **requisitos** del protocolo de medición externa para F0-A: reuso de telemetría existente (capacidad), observación externa OS-level con tree-monitoring (mandato), perímetro normativo de consumo read-only del anchor con writes efímeros, y regla de calibración sin instanciación numérica prematura.

**Estado del HITO:** FROZEN v1.2.0
**Condición de cierre cumplida:** Reconciliaciones post-ejecución y post-revisión encarnadas con changelog explícito (sin reescritura silenciosa); H-0.5-B rechazada con evidencia; H-0.5-C reformulada como mínimo exploratorio; criterios reconciliados con HITO_0.7 con propósitos distintos; gaps con destino explícito.
**Verificación de cadena de gobernanza:** Charter §5.2/§5.3/§5.5/§6/§9 → NADR-24 R11 / NADR-25 §7 / NADR-26 §5.1/§5.4 → HITO_0.3 → HITO_0.5 v1.1.0 → HITO_0.6 v1.0.0 → HITO_0.7 v1.0.0 → esta v1.2.0.
**Contradicciones con HITOs previos:** Dos, reconciliadas: con HITO_0.3 (vía HITO_0.6, autoridad primaria NADR-25/26) y con claims propios de v1.1.0 (vía evidencia de HITO_0.7).
**Decision Candidates generados:** DC-01, DC-03, DC-07 (con baseline F0-A disponible y canales diferidos identificados).
**Siguiente paso recomendado:** Emitir HITO_0.6 v1.1 y HITO_0.7 v1.1 con el mismo criterio de autocontención; luego F0-B.