# HITO_0.7_F0-A_Runtime_Profile_Baseline.md

**Estado:** FROZEN v1.1.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02 (v1.1.0)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Runtime Profile Baseline
**Naturaleza:** Read-only. Reporta el baseline numérico del execution plane sobre el anchor canónico (perfil SMOKE) sin modificar código de producción ni estado normativo.
**Evidencia Forense Vinculante:** `HITO_0.4_F0-E_Scientific_Neutrality_Contract` v1.3.0; `HITO_0.5_F0-A_Runtime_Profile_Protocol` v1.2.0; `HITO_0.6_WORKLOAD_ANCHOR_RECONCILIATION` v1.1.0; `reports/f0a_baseline/baseline_profile_20261002_014448.json`; `reports/f0a_baseline/regression_report_ce814134*.json`; `FASE0_AUDIT_CHARTER.md` §5.2, §5.5, §6, §9; `FASE_6_HANDOFF` §2.2; `DF-10`; `NADR-F17BIS-27`.
**Mandato:** Establecer el baseline numérico operacional del execution plane (wall, CPU, peak WS, integridad, coverage) sobre el anchor canónico, y documentar la disponibilidad de métricas para la regla de calibración del Charter §9 sin instanciación prematura.
**Síntesis:** F0-A establece un **Runtime Profile Baseline operacional reproducible** válido en 4 canales (wall, CPU, memory, integrity) con evidencia end-to-end autocontenida. **No establece** neutralidad científica diferencial completa (INV-SCI-1 end-to-end pendiente de M1) ni calibra por sí solo técnica alguna del Charter §9 (0/6 calibradas: faltan métricas por técnica y MDE/Δ/ε abiertos). Tres planos de veredicto separados: científico (HARD_FAIL basal), validez de medición (VALID), integridad operacional (no-mutación verificada). Hardware host no conforme (31.83GB/12 CPUs vs 16GB); accelerator N/A para este baseline.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-02 | Emisión definitiva con baseline v3-final validado (tree-monitoring, CV 0.41%, peak 77.0 MB). |
| 1.1.0-FROZEN | 2026-10-02 | **Reconciliación epistémica (medición física intacta):** (1) H-0.7-D RECHAZADA tal como estaba formulada; separada en H-0.7-E (repetibilidad bajo régimen, CONFIRMADA) e INV-SCI-1 end-to-end NO DEMOSTRADO pendiente M1 (frontera de HITO_0.4 v1.3.0). (2) "3/6 técnicas instanciadas" corregido a 0/6 calibradas: con MDE/Δ/ε abiertos y sin métricas por técnica no existen thresholds numéricos. (3) Fila §17 "Determinismo científico INV-SCI-1 = PASS" eliminada. (4) Tres planos de veredicto explícitos (§16.6). (5) Gates numéricos etiquetados como heurísticas provisionales / sanity gates de instrumento. (6) ΔNSS 0.7208→0.6385 reclasificado como hipótesis causal (H-0.7-F, NO VERIFICABLE). (7) Perímetro del árbol reproducible (worker identificado; auxiliares excluidos y registrados). (8) Envelope split host/accelerator; referencias actualizadas a HITO_0.5 v1.2.0 y HITO_0.6 v1.1.0. |

---

## 1. RESUMEN EJECUTIVO

Se ejecutó F0-A conforme al protocolo de HITO_0.5 v1.2.0 sobre el anchor canónico (perfil SMOKE, 5 documentos), con perímetro normativo de HITO_0.6 v1.1.0 (consumo read-only mandatado, writes efímeros) y canal de memoria corregido vía tree-monitoring (v3-final).

**Hallazgos centrales:**

> 1. **Pipeline ejecuta end-to-end sobre canonical sin mutación** (snapshot pre = post `4cf031d1...edb90`). H-0.6-A CONFIRMADA.
> 2. **Baseline operacional válido en 4 canales**: wall time 1.659s avg (CV 0.41%), CPU time 1.448s avg, peak WS single-process 76.98 MB avg (tree-monitoring Win32), integridad canonical verificada.
> 3. **Repetibilidad bajo régimen observada**: NSS idéntico (0.6385503611043202) en 3 ejecuciones secuenciales bajo las mismas condiciones. **Esto no es INV-SCI-1**: el experimento no varió schedule, concurrencia, cache ni completion order (pendiente M1, HITO_0.4).
> 4. **Cero técnicas calibradas**: el baseline aporta métricas agregadas (wall/CPU/WS); las reglas del Charter §9 requieren métricas por técnica (CPU por etapa, allocations por hotspot, RSS por doc grande) y δ/MDE/Δ/ε definidos. Ninguna existe aún.
> 5. **Hardware host no conforme** (31.83GB/12 CPUs vs 16GB); accelerator (GPU/VRAM) **N/A** para este baseline (run_regression no ejerce GPU ni providers). Baseline válido solo como ancla comparativa pre/post-F18 en la misma máquina.

**Métricas baseline (3 repeticiones, cold cache, perfil SMOKE) — datos físicos intactos:**

| Métrica | Rep 1 | Rep 2 | Rep 3 | Avg | StdDev | CV |
|---|---|---|---|---|---|---|
| Wall time (s) | 1.669 | 1.654 | 1.655 | 1.659 | 0.007 | 0.41% |
| CPU time (s) | 1.453 | 1.453 | 1.438 | 1.448 | 0.007 | 0.48% |
| Peak WS single-process (MB) | 76.91 | 77.04 | 77.00 | 76.98 | 0.05 | 0.07% |
| Peak WS tree (MB) | 87.86 | 80.40 | 77.52 | 81.93 | 4.55 | 5.55% |
| Exit code | 2 | 2 | 2 | — | — | — |
| NSS corpus | 0.6385503611043202 | ídem | ídem | — | — | — |

**Veredicto:** Baseline operacional VALID como ancla intra-máquina. No es evidencia de neutralidad científica diferencial ni de calibración de técnicas.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Este HITO establece un **Runtime Profile Baseline operacional reproducible**; no establece todavía la neutralidad científica diferencial completa ni calibra por sí solo las técnicas de optimización. Un HITO de auditoría puede demostrar que existe una condición necesaria para una propiedad; no puede declarar demostrada la propiedad superior si falta el experimento que la conecta end-to-end (M1, HITO_0.4). No valida el envelope de 16 GB (no representativo en esta máquina).

### 2.2 Método forense
1. Ejecutar `run_regression.py --profile SMOKE` sobre `tests/corpus/canonical` (read-only, perímetro HITO_0.6 v1.1.0).
2. Tomar snapshot SHA-256 de canonical pre/post ejecución (mecanismo NADR-26 R18).
3. Medir wall/CPU/memory vía tree-monitoring (Win32 GetProcessMemoryInfo sobre proceso + hijos recursivos; perímetro documentado).
4. Extraer métricas científicas del último reporte CV emitido por `run_regression.py`.
5. Aplicar criterios de invalidación (exit {3,4} invalidan; exit {0,1,2} validan; sanity gates de instrumento; CV < 20%).
6. Documentar la regla de calibración del Charter §9 y la disponibilidad de métricas por técnica, **sin instanciación numérica prematura**.

---

## 3. ALCANCE AUDITADO

| Superficie | Estado |
|---|---|
| `tests/corpus/canonical/` (manifest + pdf/ + ground_truth/) | 100% auditado vía snapshot |
| `tools/evaluation/run_regression.py` (ejecución) | 3 repeticiones completadas |
| `reports/f0a_baseline/` (outputs) | 1 baseline JSON + reportes CV + stderr logs |
| Hardware host (RAM/CPU) | Medido, no conforme con target |
| Hardware accelerator (GPU/VRAM) | N/A para este baseline (no ejercido) |
| Memory channel | Validado vía tree-monitoring (Win32 API) con perímetro por PID |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| JSON de medición | `reports/f0a_baseline/baseline_profile_20261002_014448.json` | Wall time, CPU, peak WS, exit codes, CV, per-PID peaks |
| Reporte CV | `reports/f0a_baseline/regression_report_ce814134*.json` | coverage, corpus_verdict, corpus_nss |
| Snapshot SHA-256 | Capturado por wrapper F0-A | Integridad canonical pre/post |
| Win32 GetProcessMemoryInfo | Tree-monitoring in-process | Peak WS validado |
| Stderr logs | `reports/f0a_baseline/rep{1,2,3}_stderr.log` | Evidencia de exit codes |
| HITO previo | `HITO_0.4` v1.3.0 | Frontera: INV-SCI-1/INV-ASSEMBLY-ORDER PARTIAL pendiente M1 |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Integridad canonical | snapshot pre == post (`4cf031d1...edb90`) | No mutación post-ejecución (NADR-26 R18) | HITO_0.6 | **PASS** | E-0.7-001 |
| Cobertura | 5 docs SMOKE evaluados | Perfil SMOKE cubierto | HITO_0.5 | **PASS** | E-0.7-002 |
| Veredicto científico | HARD_FAIL (NSS 0.6385503611043202) | Estado basal DF-10 legítimo | FASE_6_HANDOFF §2.2 | **PASS (plano científico)** | E-0.7-002 |
| Exit semantics | exit 2 = HARD_FAIL | Exit 2 no invalida medición | NADR-27 | **PASS** | E-0.7-003 |
| Peak WS (tree-monitoring, perímetro worker) | 76.98 MB avg | Sanity gate [20, 200] MB (provisional) | Ninguna | **PASS (gate de instrumento)** | E-0.7-004, E-0.7-005 |
| CPU time | 1.448s avg | Sanity gate > 0.1s (provisional) | Ninguna | **PASS (gate de instrumento)** | E-0.7-005 |
| Repetibilidad bajo régimen | NSS idéntico ×3 (secuencial, mismas condiciones) | — | Ninguna | **PASS (régimen probado solamente)** | E-0.7-002 |
| INV-SCI-1 end-to-end | No variado: schedule/concurrencia/cache/ordering fijos | INV-SCI-1 cuantifica sobre esas variaciones | HITO_0.4: PARTIAL pendiente M1 | **NO DEMOSTRADO (pendiente M1)** | HITO_0.4 v1.3.0 |
| Host envelope | 31.83GB / 12 CPUs | Target 16GB RAM | Charter §5.5 | **DISCREPANCY DOCUMENTADA (limitación)** | E-0.7-006 |
| Accelerator envelope | GPU/VRAM no ejercidos | Target 4GB VRAM aplica a cargas con acelerador | Ninguna | **N/A para este baseline** | E-0.7-006 |
| Métricas por etapa | No disponibles | Charter §6 exige por etapa | Ninguna | **DEFERRED** | E-0.7-007 |
| Provider metrics | No disponibles | Charter §6 exige provider latency | Ninguna | **DEFERRED** | E-0.7-008 |
| Regla de calibración | 0/6 técnicas calibradas; solo baseline agregado disponible | Charter §9 exige métrica específica por técnica + δ/MDE/Δ/ε | v1.0.0 afirmó 3/6 | **NOT INSTANTIATED (reconciliado)** | E-0.7-009 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.7-001: Integridad canonical verificada
* **Observed:** SHA-256 pre-ejecución = SHA-256 post-ejecución = `4cf031d1f733467fe1a22e09428a5fb5f65916915ec99b66af406057cd9edb90`.
* **Hallazgo:** Ejecución read-only sobre canonical no mutó el oráculo. Cierre empírico de H-0.6-A. Mecanismo NADR-26 R18 operativo.
* **Severidad:** P0

### Evidencia E-0.7-002: Pipeline ejecuta end-to-end sobre SMOKE; repetibilidad bajo régimen
* **Observed:** Coverage = 5 docs SMOKE; corpus_verdict = HARD_FAIL; corpus_nss = 0.6385503611043202 idéntico en 3 repeticiones secuenciales bajo las mismas condiciones observadas.
* **Hallazgo:** **FACT:** el entry point completa todas sus etapas y produce veredicto científico; el NSS fue idéntico en las 3 ejecuciones del régimen probado. **NO DEMOSTRADO:** INV-SCI-1 end-to-end (el régimen no varió schedule, concurrencia, cache ni completion order); igualdad de AST por nodo, orden, ensamblado o artefacto canónico entre ejecuciones (no comparados en este experimento).
* **Severidad:** P0

### Evidencia E-0.7-003: Exit code semantics reconciliado
* **Observed:** 3 repeticiones con exit 2. Según FASE_6_HANDOFF §2.2 y DF-10, exit 2 (HARD_FAIL) es el estado basal legítimo.
* **Hallazgo:** Regla de invalidación corregida: exit {0,1,2} = medición válida; exit {3,4} = invalidación. Los exit codes no se reinterpretan: se clasifica la validez de la medición, no el veredicto científico.
* **Severidad:** P1

### Evidencia E-0.7-004: Canal de memoria corregido vía tree-monitoring con perímetro reproducible
* **Observed:** Win32 GetProcessMemoryInfo sobre proceso + hijos recursivos reporta peak WS single-process 76.98 MB avg (vs 3.5 MB en medición monoproceso previa).
* **Perímetro por PID (reproducible):**

| Rep | Parent PID (launcher) | Parent WS | Child PID (worker = componente del pipeline) | Worker WS | Auxiliares excluidos |
|---|---|---|---|---|---|
| 1 | 23956 | 3.50 MB | 304 | 76.91 MB | 15464 (5.27 MB), 24484 (6.70 MB) |
| 2 | 5412 | 3.49 MB | 5168 | 77.04 MB | — |
| 3 | 23700 | 3.49 MB | 16488 | 77.00 MB | — |

* **Hallazgo:** El baseline adopta el **worker identificado** (máximo kernel peak sobre el árbol) como componente del pipeline; launcher y auxiliares transitorios de Windows quedan excluidos y registrados por PID. `PeakWorkingSetSize` del kernel es retroactivo por proceso: aunque el attach sea tardío, el pico real queda capturado. La métrica de baseline es `peak_single_process_ws`; `peak_tree_ws` se reporta como contexto, no como métrica de decisión.
* **Severidad:** P0 (instrumento corregido)

### Evidencia E-0.7-005: Peak WS y CPU time dentro de sanity gates de instrumento
* **Observed:** Peak single-process WS 76.98 MB avg; CPU time 1.448s avg.
* **Hallazgo:** Los gates [20,200] MB y CPU > 0.1s son **sanity gates de instrumento provisionales** (detectan canal roto, como el artefacto de 3.4 MB del launcher), preregistrados antes del run v3 pero no pertenecientes a la capa congelada del Charter. No son criterios científicos calibrados.
* **Severidad:** P1

### Evidencia E-0.7-006: Envelopes de hardware (split host/accelerator)
* **Observed:** Host: 31.83 GB RAM / 12 CPUs lógicos vs target 16 GB RAM. Accelerator: GPU/VRAM no ejercidos por `run_regression.py` (sin providers ni GPU en el path medido).
* **Hallazgo:** Baseline NO válido para claims de conformidad del host envelope; válido como ancla comparativa pre/post-F18 en la misma máquina (Charter §5.5). Accelerator envelope **N/A** para este baseline: no se declara falta de conformidad GPU cuando la medición no depende de GPU.
* **Severidad:** P1

### Evidencia E-0.7-007: Métricas por etapa ausentes
* **Observed:** El wrapper no captura métricas por etapa (extraction vs TED vs evaluation).
* **Required:** Charter §6 exige descomposición por etapa.
* **Hallazgo:** Sin descomposición, la regla de calibración de process pools (CPU-time TED/extraction) no puede instanciarse. Deferred Question (F0-D o instrumentación).
* **Severidad:** P2

### Evidencia E-0.7-008: Provider metrics no medibles
* **Observed:** `run_regression.py` no importa providers ni los invoca.
* **Required:** Charter §6 exige provider latency, tokens, retries.
* **Hallazgo:** Canal estructuralmente no medible vía run_regression. Sin él, las reglas de SyncProviderBridge elision, LLM cache y batching adaptativo no pueden instanciarse. Deferred Question (F0-D).
* **Severidad:** P2

### Evidencia E-0.7-009: Regla de calibración NO instanciada (0/6 técnicas)
* **Observed:** El baseline aporta métricas agregadas (wall total, CPU total, peak WS). Las reglas del Charter §9 requieren por técnica: latencia p95 por etapa I/O, CPU-time TED/extraction, allocations y peak RSS en hotspot, peak RSS por doc grande con wall p95, hit-rate y costo evitado, tokens por padding. Ninguna de esas métricas específicas existe en este baseline. Además δ = max(MDE, ruido), Δ significativo y ε permanecen **abiertos**.
* **Hallazgo:** **FACT:** existe baseline observable utilizable como lado baseline de la función de calibración. **NO DEMOSTRADO:** que técnica alguna esté calibrada. Con MDE/Δ/ε abiertos no existen thresholds numéricos. La instanciación requiere métricas por técnica (F0-D) y protocolo preregistrado en el Execution Plan.
* **Severidad:** P1

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-0.7-01 | Rep 1 tuvo 3 child PIDs vs 1 en reps 2-3. Los auxiliares (15464: 5.27 MB, 24484: 6.70 MB) son procesos transitorios de Windows, no parte del pipeline; quedan excluidos del perímetro y registrados (E-0.7-004). | Bajo | DOCUMENTADA |
| OBS-0.7-02 | `peak_tree_ws` (87.86 MB rep 1) vs `peak_single_process_ws` (76.91 MB): la diferencia corresponde a launcher + auxiliares. La métrica de decisión es `peak_single_process_ws`; `peak_tree_ws` es contexto. | Medio | DOCUMENTADA (perímetro aplicado) |
| OBS-0.7-03 | SQLite ephemeral DBs (`fsm.db`, `queue.db`) no se crearon durante la ejecución. Confirma que `run_regression.py` no usa la infraestructura operacional del sistema. | Bajo | CONFIRMADA |
| OBS-0.7-04 | NSS 0.6385 vs DF-10 0.7208: diferencia observada entre versiones del sujeto. **Hipótesis causal (H-0.7-F): evolución del extractor; NO VERIFICADA** (requiere comparación controlada de versiones bajo protocolo). No es error de medición. | Medio | HIPÓTESIS (H-0.7-F) |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.7-01** | Métricas por etapa no capturadas (extraction, TED, evaluation) | E-0.7-007 | Charter §6 | **Fase 18** (F0-D o instrumentación) | OPEN |
| **GAP-0.7-02** | Provider metrics no medibles vía run_regression | E-0.7-008 | Charter §6 | **Fase 18** (F0-D) | OPEN |
| **GAP-0.7-03** | Host envelope no conforme; accelerator N/A para este baseline | E-0.7-006 | Charter §5.5 | **Documentado como limitación** | CLOSED (limitación) |
| **GAP-0.7-04** | Canal de memoria monoproceso inválido en Windows venv | E-0.7-004 | Metodología de medición | **Workaround aplicado** (tree-monitoring con perímetro) | CLOSED (workaround) |
| **GAP-0.7-05** | Sin thresholds numéricos: MDE/Δ/ε abiertos y métricas por técnica ausentes; 0/6 técnicas calibradas | E-0.7-009 | Charter §9 | **Fase 18** (F0-D + protocolo preregistrado en Execution Plan) | OPEN |
| **GAP-0.7-06** | INV-SCI-1 end-to-end y invariancia de completion order no demostradas | E-0.7-002; HITO_0.4 v1.3.0 | INV-SCI-1, INV-ASSEMBLY-ORDER | **Fase 18** (experimento M1, DC-12) | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.6-A | Ejecución read-only sobre canonical no muta el oráculo | **CONFIRMADA** | E-0.7-001 (snapshot pre = post) | Valida perímetro de HITO_0.6 v1.1.0 |
| H-0.7-A | Peak WS del pipeline está en el orden de decenas de MB | **CONFIRMADA** | E-0.7-004, E-0.7-005 (76.98 MB avg) | Tree-monitoring con perímetro captura el worker real |
| H-0.7-B | Exit 2 es el estado basal legítimo y no invalida la medición | **CONFIRMADA** | E-0.7-003, FASE_6_HANDOFF §2.2, DF-10 | Regla de invalidación corregida |
| H-0.7-C | Métricas por etapa y de proveedor pueden instanciarse en esta medición | **REFUTADA** | E-0.7-007, E-0.7-008 | Deferred Questions F0-D |
| H-0.7-D | El pipeline de regresión es determinista end-to-end (INV-SCI-1) | **RECHAZADA tal como estaba formulada** | E-0.7-002 muestra NSS idéntico bajo un único régimen; no se varió schedule/concurrencia/cache/ordering | Repetibilidad-bajo-régimen confirmada (H-0.7-E); INV-SCI-1 end-to-end NO DEMOSTRADO pendiente M1 |
| H-0.7-E | NSS idéntico en 3 repeticiones secuenciales bajo mismas condiciones indica repetibilidad del resultado científico en el régimen probado | **CONFIRMADA** | E-0.7-002 | Sirve como referencia M0 del guard diferencial; no implica invariancia bajo otros regímenes |
| H-0.7-F | ΔNSS 0.7208 (DF-10) → 0.6385 causado por evolución del extractor | **NO VERIFICABLE** | Sin experimento diferencial controlado entre versiones del pipeline | Hipótesis causal atribuida; requiere comparación de versiones bajo protocolo |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cuál es el baseline numérico válido?
Wall time 1.659s avg (CV 0.41%), CPU time 1.448s avg, peak single-process WS 76.98 MB avg (tree-monitoring, perímetro worker), integridad canonical verificada, coverage 5 docs SMOKE, NSS 0.6385503611043202 (HARD_FAIL basal). Válido como ancla intra-máquina pre/post-F18.

### 16.2 ¿Qué puede afirmar F0-A respecto al envelope de 16GB/4GB?
Nada sobre conformidad del host envelope. Solo comparación relativa pre/post-F18 en la misma máquina. Accelerator envelope: N/A para este baseline (run_regression no ejerce GPU ni providers).

### 16.3 ¿Qué métricas permanecen diferidas?
- Métricas por etapa (extraction, TED, evaluation) → F0-D o instrumentación adicional.
- Provider metrics (latency, tokens, retries) → F0-D (requiere providers activos).
- Comparación de AST por nodo / artefacto ensamblado entre ejecuciones → experimento M1 (HITO_0.4, DC-12).

### 16.4 ¿Cuál es la nota de plataforma obligatoria?
En este venv de Windows, `sys.executable -m ...` **siempre** spawnea un child worker process. Todo instrumento futuro (F0-D provider metrics, profiling, tracing) **debe** usar tree-monitoring con perímetro documentado. Medición monoproceso es estructuralmente inválida en este entorno.

### 16.5 ¿Cuál es el estado de la regla de calibración (Charter §9)?
**Ninguna técnica está calibrada.** F0-A aporta el lado baseline agregado; las reglas requieren métricas por técnica y δ/MDE/Δ/ε definidos:

| Técnica | Métrica requerida por la regla | Disponibilidad en este baseline | Estado |
|---|---|---|---|
| SyncProviderBridge elision | latencia p95 por etapa I/O | Ausente (por etapa + provider) | NO CALIBRADA (F0-D) |
| process pools | CPU-time TED/extraction | Ausente (descomposición por etapa) | NO CALIBRADA (F0-D) |
| object pools / zero-copy | allocations y peak RSS en hotspot | Ausente (allocations, hotspot) | NO CALIBRADA (F0-D) |
| lazy loading | peak RSS por doc grande + wall p95 | Ausente (por documento, p95) | NO CALIBRADA (F0-D) |
| LLM cache | hit-rate + costo evitado | Ausente (provider) | NO CALIBRADA (F0-D, sujeta a DC-03/DC-04) |
| batching adaptativo | tokens desperdiciados por padding | Ausente (provider) | NO CALIBRADA (F0-D) |

Con MDE, Δ y ε abiertos **no existen thresholds numéricos**. La instanciación ocurre en el Execution Plan/F0-D con protocolo preregistrado; no se re-calibra a mano después (Charter §9).

### 16.6 ¿Cuáles son los tres planos de veredicto separados?
1. **Plano científico:** NSS 0.6385503611043202 → HARD_FAIL (estado basal DF-10). **No es aprobación del pipeline.**
2. **Plano de validez de medición:** baseline VALID (exit ∈ {0,1,2}, CV 0.41%, sanity gates OK, canal de memoria corregido).
3. **Plano de integridad operacional:** canonical pre/post idéntico; writes efímeros; identidad del anchor verificada pre-run (NADR-24 R11).
Estos planos **MUST NOT** mezclarse: "baseline VALID" no implica "pipeline científicamente aprobado", ni "HARD_FAIL" implica "medición inválida".

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO ADR/NADR

| Regla | Fuente | Required | Observed | Estado | Evidencia |
|---|---|---|---|---|---|
| No mutación del oráculo | NADR-26 R18, HITO_0.6 | Snapshot pre == post | `4cf031d1...` == `4cf031d1...` | PASS | E-0.7-001 |
| Exit codes sin reinterpretar | NADR-27, carry-forward | Exit codes propagados | 0,1,2 = medición válida; 3,4 = inválida | PASS | E-0.7-003 |
| Baseline reproducible | Charter §5.5 | Repeticiones, cold cache | CV 0.41% (< 20%) | PASS | E-0.7-002 |
| Hardware envelope documentado | Charter §5.5 | Envelope real declarado | Host 31.83GB/12 CPUs no conforme; accelerator N/A | PASS | E-0.7-006 |
| Canal de memoria validado | Charter §5.3 | Instrumento corregido | Tree-monitoring Win32 con perímetro por PID | PASS | E-0.7-004 |
| Repetibilidad bajo régimen | — | NSS idéntico en régimen probado | 0.6385503611043202 × 3 | PASS (régimen solamente) | E-0.7-002 |
| INV-SCI-1 end-to-end | Charter §4, HITO_0.4 | Invariancia bajo schedule/concurrencia/cache/ordering | No variado en este experimento | **PARTIAL (pendiente M1)** | HITO_0.4 v1.3.0 |
| Regla de calibración | Charter §9 | Métrica específica por técnica + δ/MDE/Δ/ε | Solo baseline agregado; variables abiertas | **NOT INSTANTIATED** | E-0.7-009 |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado en baseline | Fase destino |
|---|---|---|---|---|
| **DC-01** | Fork de concurrencia | Wall 1.659s, CPU 1.448s, WS 76.98 MB (agregados) | Parcial (sin métricas por etapa) | **Fase 18** (F0-B/F0-D) |
| **DC-03** | Determinismo observable por proveedor | Provider metrics diferidas | No medible en este baseline | **Fase 18** (F0-D) |
| **DC-04** | Alcance de caches | No activado | No medible | **Fase 18** |
| **DC-06b** | Supervivencia de técnicas del ROADMAP | 0/6 técnicas calibradas; baseline agregado disponible | Pendiente de métricas por técnica | **Fase 18** (F0-D) |
| **DC-07** | Tiers de batching | No medible sin providers | No medible | **Fase 18** (F0-D) |
| **DC-10** | Fairness y admission | Wall time base disponible | Parcial (sin carga concurrente) | **Fase 18** |
| **DC-12** | Contrato y promoción del guard diferencial | Repetibilidad bajo régimen como referencia M0 | M0 disponible; M1 pendiente | **Fase 18** (M1) |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia |
|---|---|---|---|
| Comparación inter-máquinas inválida | Baseline no aplica a hardware diferente al medido | Alto | E-0.7-006 |
| Confundir repetibilidad-bajo-régimen con INV-SCI-1 | Tratar NSS idéntico ×3 como neutralidad diferencial llevaría a aceptar regresiones de concurrencia/ordering | Alto | E-0.7-002, GAP-0.7-06 |
| Tratar baseline agregado como calibración | Usar wall/CPU totales como threshold de técnicas violaría Charter §9 | Alto | E-0.7-009, GAP-0.7-05 |
| Medición monoproceso en Windows venv | Tree-monitoring con perímetro obligatorio | Alto | E-0.7-004 |
| ΔNSS atribuido sin experimento | Aceptar H-0.7-F como hecho ocultaría causas alternativas | Medio | OBS-0.7-04, H-0.7-F |
| Procesos auxiliares transitorios | Ruido de Windows en tree WS; mitigado por perímetro por PID | Bajo | OBS-0.7-01 |

---

## 21. CIERRE DEL HITO 0.7

**Estado del HITO:** FROZEN v1.1.0
**Condición de cierre cumplida:** Baseline v3-final con 4 canales válidos (medición física intacta); reconciliación epistémica aplicada sin re-medición: tres planos de veredicto separados, repetibilidad-bajo-régimen ≠ INV-SCI-1, 0/6 técnicas calibradas, δ/MDE/Δ/ε abiertos, gates como heurísticas provisionales, ΔNSS como hipótesis causal, perímetro del árbol reproducible; hipótesis cerradas o con destino y razón (H-0.7-D RECHAZADA, H-0.7-F NO VERIFICABLE, GAP-0.7-06 → M1).
**Verificación de cadena de gobernanza:** Charter §5.2/§5.5/§6/§9 → NADR-24 R11 / NADR-26 R18 / NADR-27 → HITO_0.4 v1.3.0 (frontera M1) → HITO_0.5 v1.2.0 (protocolo) → HITO_0.6 v1.1.0 (perímetro) → este HITO v1.1.0.
**Contradicciones con HITOs previos:** Reconcilia claims propios de v1.0.0 (H-0.7-D, 3/6 calibradas, fila INV-SCI-1 PASS) contra la frontera de HITO_0.4 v1.3.0 y evidencia E-0.7-009; reconcilia criterio de invalidación de HITO_0.5 (exit {0,1,2} válidos).
**Decision Candidates generados:** Ninguno nuevo; alimenta DC-01/DC-03/DC-04/DC-06b/DC-07/DC-10/DC-12 con baseline agregado y referencia M0 del guard diferencial.
**Siguiente paso recomendado:** Iniciar F0-B (Concurrency & Blocking Map runtime); luego F0-C y F0-D; ejecutar M1 del contrato diferencial (HITO_0.4, DC-12) antes de emitir `ADR_F18_MASTER`.