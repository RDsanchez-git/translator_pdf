# HITO_0.9_F0-D_Waste_FinOps_Map.md

**Estado:** FROZEN v1.4.0
**Fecha de emisión:** 2026-10-03
**Fecha de congelamiento:** 2026-10-03
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría, Etapa 3)
**Tipo de artefacto:** Discovery (Waste/FinOps Map)
**Naturaleza:** Read-only + Medición externa. Sin código productivo nuevo (ADR_F17_BIS_MASTER: Fase 0 = Audit Gate, Prohibición Estricta de Diseño en Discovery). Sin credenciales reales. Sin thresholds inventados.
**Output obligatorio (Charter §6, Trazabilidad F0):** Evidence Register (FinOps) → §19
**Evidencia Forense Vinculante:** `FASE0_AUDIT_CHARTER.md` §5.3, §6 (Etapa 3), §9; `HITO_0.8` v1.4.0; `ADR_F17_BIS_MASTER.md` (Fase 0 = Audit Gate); `ENGINEERING_PRINCIPLES.md` (Explicit over Implicit, Absolute Traceability, Fail Fast); `ROADMAP_ARQUITECTONICO_LP.md` (Fase 18).
**Mandato (Charter §6):** F0-D Waste/FinOps Map: duplicate execution, retry waste, post-cancel work, repeated provider calls, failed persistence; baseline de waste ratio.
**Artefacto de ejecución:** `reports/waste_t1/baseline_t1_local_2026-10-02T18-13-29.json`
**Síntesis:** De los 5 canales mandatados por el Charter, 1 fue medido directamente (failed persistence, W7), 3 no pudieron ejercitarse con el instrumento actual (duplicate execution W1, post-cancel work W5, repeated provider calls W2) por limitación documentada, y 1 fue medido parcialmente como proxy (retry waste W3, quota contention bajo límites artificiales). El baseline de waste ratio es parcial: solo cubre los canales ejercitables. Se registran 2 hallazgos adicionales fuera del mandato (telemetry loss W6, profiler stateless W8) como observaciones complementarias. El Evidence Register (FinOps) se emite en §19.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-DRAFT | 2026-10-03 | Emisión inicial. Protocolo preregistrado + plan T1. |
| 1.1.0-DRAFT | 2026-10-03 | Correcciones post-revisión: proxy counter, ventanas correctas. |
| 1.2.0-FROZEN | 2026-10-03 | Ejecución T1-LOCAL completada. 5/5 canales ejecutados. |
| 1.3.0-FROZEN | 2026-10-03 | Reconciliación epistemológica. 16 correcciones documentales. |
| 1.4.0-FROZEN | 2026-10-03 | **Alineación con Charter §6.** (1) Estructura reorganizada alrededor de los 5 canales mandatados. (2) Evidence Register (FinOps) añadido como output obligatorio en §19. (3) W6/W8 movidos a hallazgos adicionales. (4) Nomenclatura alineada con "baseline de waste ratio". (5) Trazabilidad F0-D → Evidence Register explícita. (6) Correcciones epistemológicas de v1.3.0 mantenidas. |

---

## 1. RESUMEN EJECUTIVO

Se ejecutó el experimento T1-LOCAL conforme al mandato de Charter §6 Etapa 3 (F0-D), usando instrumentos existentes sobre DBs efímeras, sin modificar código productivo (ADR_F17_BIS_MASTER: "Prohibición Estricta de Diseño en Discovery", ENGINEERING_PRINCIPLES: "Reuse Before Invent").

**Cobertura del mandato Charter §6:**

| Canal mandatado | Estado | Resultado |
|---|---|---|
| Duplicate execution | **DEFERRED** (W1) | No ejercitable: adapters/SDKs no exponen base_url override sin código productivo |
| Retry waste | **MEDIDO PARCIAL** (W3) | Quota contention bajo límites artificiales: 3/20 granted |
| Post-cancel work | **DEFERRED** (W5) | No ejercitable: misma limitación que W1 |
| Repeated provider calls | **DEFERRED** (W2) | No ejercitable: misma limitación que W1 |
| Failed persistence | **MEDIDO** (W7) | 1/1 zombie write interceptado (scope: lease-expired ack) |
| Baseline de waste ratio | **PARCIAL** | Solo canales ejercitables; 3/5 deferred |

**Hallazgos adicionales (fuera del mandato, registrados como observaciones):**
- W6: SQLiteTelemetryGateway pierde 100% del buffer in-memory bajo crash abrupto
- W8: HeuristicDocumentProfiler es stateless (~1.1ms/call)

**Veredicto:** El baseline de waste ratio es **parcial**. De los 5 canales mandatados, solo 2 producen datos (W3 parcial, W7 completo). Los 3 canales restantes (W1, W2, W5) quedan deferred a F18 con causa documentada. El Evidence Register (FinOps) se emite en §19 con clasificación epistémica estricta.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO

### 2.1 Límite epistemológico
- **Medición externa exclusivamente** (Charter §5.3, ADR_F17_BIS_MASTER "NO CODE"): instrumentos existentes sobre DBs efímeras. Cero modificaciones a código productivo.
- **Waste estructural ≠ waste económico real**: sin credenciales Groq/Gemini, no hay USD reales. T2 (waste económico con credenciales) es Deferred Question con destino F18.
- **Cero thresholds inventados** (Charter §9): se reportan ratios observados. Sin gates numéricos normativos.
- **Baseline de waste ratio parcial**: 3/5 canales del Charter no ejercitables. El baseline cubre solo los canales medidos.

### 2.2 Frontera F0-C / F0-D (Charter §6)
- F0-C respondió: qué sobrevive, qué se pierde, cómo intenta recuperarse.
- F0-D responde: cuánto cuesta operacionalmente ese comportamiento.
- F0-D no re-audita propiedades de recovery.

### 2.3 Frontera canonical / carga (HITO_0.6/0.7)
- Canonical sellado NO se usa como carga.
- Workload de T1 = DBs efímeras + PDFs SMOKE en directorio temporal.

### 2.4 INV-JOURNAL: invariant semántico, no técnico
El invariant INV-JOURNAL (Charter §4) exige:
> "ningún efecto externo podrá producirse sin una intención/lease/reserva recuperable tras crash y una aplicación idempotente del resultado."

Esto es un **invariant semántico**. La técnica concreta de resolución queda abierta para F18. F0-D no prescribe técnica; documenta la ventana post-effect/pre-journal como inferencia estructural.

---

## 3. ALCANCE AUDITADO (alineado con Charter §6)

### 3.1 Canales mandatados

| Canal Charter | Wrapper ID | Fuente | Estado |
|---|---|---|---|
| Duplicate execution | W1 | GAP-0.8-04, H-0.8-D | **DEFERRED** a F18 |
| Retry waste | W3 | `rate_limiter.py` QuotaManager | ✅ MEDIDO (parcial) |
| Post-cancel work | W5 | H-0.1-B, GAP-0.1-03 | **DEFERRED** a F18 |
| Repeated provider calls | W2 | GAP-0.8-02 | **DEFERRED** a F18 |
| Failed persistence | W7 | `control_repo.py` OptimisticLockError | ✅ MEDIDO |
| Baseline de waste ratio | — | Derivado de W1-W5, W7 | **PARCIAL** |

### 3.2 Hallazgos adicionales (fuera del mandato)

| Canal | Wrapper ID | Fuente | Estado |
|---|---|---|---|
| Telemetry loss | W6 | `telemetry/gateway.py` | ✅ MEDIDO (observación) |
| Profile re-inference | W8 | `document_profile/profiler.py` | ✅ MEDIDO (observación) |
| Healing rollback | W4 | `healing/pipeline.py` | ⚠️ NOT MEASURABLE |

### 3.3 Causa de deferral (W1, W2, W5)

Los canales W1, W2 y W5 no pudieron ejercitarse con el instrumento actual porque los adapters/SDKs auditados (`AsyncGroq` en `adapters.py`, `GeminiProvider`) no exponen un `base_url` override utilizable sin modificación de código productivo. El grep de `base_url` en `adapters.py` y `provider_stack_factory.py` devolvió vacío. Añadir el override violaría Charter §5.3 y ADR_F17_BIS_MASTER ("NO CODE" en Fase 0). Destino: F18.

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso |
|---|---|---|
| Charter | §5.3, §6 (Etapa 3), §9 | Mandato, canales, output obligatorio |
| ADR Maestro | ADR_F17_BIS_MASTER.md | Fase 0 = Audit Gate, NO CODE, Reuse Before Invent |
| Principios | ENGINEERING_PRINCIPLES.md | Explicit over Implicit, Absolute Traceability, Fail Fast |
| Roadmap | ROADMAP_ARQUITECTONICO_LP.md | Fase 18 scope |
| HITO previo | HITO_0.8 v1.4.0 | Sujetos de cuantificación (GAP-0.8-01 a 07) |
| Código | 10 superficies D1-D10 | Evidencia forense primaria |
| Instrumentos | QuotaManager, HealingPipeline, SQLiteTelemetryGateway, ControlPlaneRepository, HeuristicDocumentProfiler | Reuso (Reuse Before Invent) |
| Ejecución | `tools/evaluation/waste_t1_local.py` v1.4.0 | Wrapper externo, DBs efímeras |
| Resultado | `reports/waste_t1/baseline_t1_local_2026-10-02T18-13-29.json` | Baseline cuantificado |

---

## 7. MATRIZ DE WASTE — CANALES MANDATADOS (Charter §6)

### 7.1 Mediciones

| Canal Charter | Wrapper | Métrica | Valor observado | Clasificación |
|---|---|---|---|---|
| Duplicate execution | W1 | duplicate_rate | **NO MEDIDO** (deferred) | DEFERRED |
| Retry waste | W3 | granted_ratio | 3/20 = 0.15 | CUANTIFICADO (parcial) |
| Retry waste | W3 | rejection_ratio | 17/20 = 0.85 | CUANTIFICADO (parcial) |
| Post-cancel work | W5 | post_cancel_waste | **NO MEDIDO** (deferred) | DEFERRED |
| Repeated provider calls | W2 | repeated_calls | **NO MEDIDO** (deferred) | DEFERRED |
| Failed persistence | W7 | interception_rate | 1/1 = 1.0 | CUANTIFICADO |
| Baseline de waste ratio | — | waste_ratio_global | **PARCIAL** (solo W3+W7) | PARCIAL |

### 7.2 Interpretación

| Canal | Interpretación | Limitaciones |
|---|---|---|
| W1 (duplicate execution) | INFERENCIA ESTRUCTURAL DE ALTA CONFIANZA: existe una ruta de código donde crash post-effect/pre-journal puede provocar reejecución. NO VALIDADA EXPERIMENTALMENTE. | Deferred a F18. Magnitud NO DEMOSTRADA. |
| W3 (retry waste) | Comportamiento de admisión consistente con límites configurados (rpm=3, tpm=100). No demuestra "waste" per se: un rechazo que previene trabajo inútil es protección, no desperdicio. | Límites artificialmente ajustados. No prueba refill, fairness, races, starvation. |
| W5 (post-cancel work) | NO MEDIDO. | Deferred a F18. |
| W2 (repeated provider calls) | NO MEDIDO. | Deferred a F18. |
| W7 (failed persistence) | Fencing/optimistic locking interceptó el zombie write. Scope: lease-expired acknowledgement only. | Flujo completo de zombie recovery NO ejercitado (worker_B no robó la tarea). |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### E-0.9-011: Incidente de bootstrap sobre DBs productivas
* **Archivo:** Log de ejecución del bootstrap con APP_ROOT temporal
* **Observed:** `bootstrap_all_databases()` estructuró los 4 planos en `infra/db/*.db` (ruta productiva) mientras `APP_ROOT` apuntaba a un directorio temporal.
* **Damage check:** 0 rows en todas las DBs productivas excepto 1 en `system_leases`. Sin datos reales perdidos.
* **Hallazgo:** **GAP-0.9-01.** Violación de perímetro sin daño material.
* **Severidad:** P1

### E-0.9-012: W6 — Pérdida total del buffer in-memory bajo crash abrupto (hallazgo adicional)
* **Archivo:** `core/telemetry/gateway.py`
* **Observed:** Graceful shutdown flushea 200/200. Crash abrupto (`os._exit()`) persiste 0/200.
* **Hallazgo:** Pérdida total del buffer in-memory pendiente bajo el escenario T1-LOCAL. Gap de observabilidad.
* **Severidad:** P1

### E-0.9-013: W7 — Zombie write interceptado (canal mandatado: failed persistence)
* **Archivo:** `infra/db/control_repo.py` L81, L99, L125
* **Observed:** 1/1 intentos interceptados. `task_stolen_by_worker_b = false`.
* **Hallazgo:** Fencing/optimistic locking interceptó el zombie write. Scope: lease-expired acknowledgement only.
* **Severidad:** N/A (fortaleza confirmada en scope limitado)

### E-0.9-014: W3 — Admisión bajo contención artificial (canal mandatado: retry waste)
* **Archivo:** `apps/llm_workers/rate_limiter.py`
* **Observed:** 3 granted, 17 rejected, 0 timeouts bajo rpm=3, tpm=100.
* **Hallazgo:** Comportamiento observado consistente con límites configurados. No demuestra correctness general.
* **Limitación del instrumento:** clasificación "permanent_rejections" es incorrecta; son INSUFFICIENT_RPM/TPM.
* **Severidad:** N/A (informativo)

### E-0.9-015: W8 — Profiler stateless (hallazgo adicional)
* **Archivo:** `core/document_profile/profiler.py`
* **Observed:** Cold=1.2ms, warm=1.12ms, new_cold=1.13ms. Diferencia 0.01ms.
* **Hallazgo:** No se demuestra overhead significativo atribuible al estado warm. DF-34 es structural.
* **Severidad:** N/A (confirmación estructural)

### E-0.9-016: W4 — Healing no ejercitable (hallazgo adicional)
* **Archivo:** `core/healing/pipeline.py`
* **Observed:** 10/10 NOT_APPLICABLE.
* **Hallazgo:** NOT MEASURABLE. Limitación del experimento.
* **Severidad:** P2

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Fase destino | Estado |
|---|---|---|---|---|
| **GAP-0.9-01** (P1) | `bootstrap_all_databases()` no respeta APP_ROOT | E-0.9-011 | F18 | OPEN |
| **GAP-0.9-02** (P1) | SQLiteTelemetryGateway pierde 100% del buffer in-memory bajo crash abrupto | E-0.9-012 | F18 | OPEN |
| **GAP-0.9-03** (P2) | W4 healing no ejercitable con contexto sintético | E-0.9-016 | F18 | OPEN |
| **GAP-0.9-04** (P1) | W7 zombie test no ejercita flujo completo de recovery | E-0.9-013 | F18 | OPEN |
| **GAP-0.9-05** (P1) | W1/W2/W5 no ejercitables: adapters/SDKs sin base_url override | §3.3 | F18 | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.8-D | Existe ruta de código donde crash post-effect/pre-journal puede provocar reejecución | **INFERENCIA ESTRUCTURAL DE ALTA CONFIANZA — NO VALIDADA EXPERIMENTALMENTE** | E-0.8-003 | W1 deferred |
| H-0.9-A | QuotaManager aplica límites configurados | **OBSERVADA** (comportamiento consistente) | E-0.9-014 | No demuestra correctness general |
| H-0.9-B | Telemetry sobrevive crash abrupto | **RECHAZADA** (para SQLiteTelemetryGateway bajo T1-LOCAL) | E-0.9-012 | Loss ratio = 1.0 |
| H-0.9-C | Zombie writes con lease expirado son interceptados | **CONFIRMADA** (scope: lease-expired ack only) | E-0.9-013 | Interception rate = 1.0 |
| H-0.9-D | Profiler tiene overhead cold/warm significativo | **RECHAZADA** | E-0.9-015 | Diferencia 0.01ms |
| H-0.9-E | Healing rollback medible con contexto sintético | **RECHAZADA** | E-0.9-016 | 10/10 N/A |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cuál es el baseline de waste ratio?
**PARCIAL.** Solo 2 de 5 canales mandatados producen datos:
- W3 (retry waste): 85% rejection bajo contención artificial
- W7 (failed persistence): 100% interceptación en scope limitado

W1 (duplicate execution), W2 (repeated provider calls), W5 (post-cancel work) están deferred. El waste ratio global no puede calcularse sin estos 3 canales.

### 16.2 ¿Qué canales quedan deferred y por qué?
W1, W2, W5 no pudieron ejercitarse porque los adapters/SDKs auditados no exponen `base_url` override sin código productivo (Charter §5.3, ADR_F17_BIS_MASTER "NO CODE"). Destino: F18.

### 16.3 ¿Qué NO afirma este HITO?
- Waste económico real en USD (T2 deferred).
- Duplicate-effect rate cuantificado (W1 deferred).
- Repeated provider calls cuantificado (W2 deferred).
- Post-cancel work cuantificado (W5 deferred).
- Waste ratio global (3/5 canales deferred).
- Correctness general de QuotaManager.
- Que toda la observabilidad FinOps tenga punto ciego.
- Que journal-first sea la técnica de resolución de INV-JOURNAL.

### 16.4 ¿Qué Decision Candidates se alimentan?
- **DC-08:** W7 (zombie interception) + W6 (telemetry loss) → write-policy y persistencia.
- **DC-13:** W6 (observabilidad perdida en crash) → coordinated shutdown.
- **DF-34:** W8 confirma que ProfileStore waste es structural. N y coste agregado NO DEMOSTRADOS.

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO

| Regla | Fuente | Cumplimiento |
|---|---|---|
| NO CODE productivo | Charter §5.3, ADR_F17_BIS_MASTER | ✅ |
| Medición externa | Charter §5.3 | ✅ |
| Canonical read-only | HITO_0.6/0.7 | ✅ |
| Cero thresholds inventados | Charter §9 | ✅ |
| Reuse Before Invent | ENGINEERING §VII | ✅ |
| Protocolo preregistrado | NADR-23 R4/R7 | ✅ |
| Prohibición de Diseño en Discovery | ADR_F17_BIS_MASTER | ✅ |
| Explicit over Implicit | ENGINEERING | ✅ (clasificación epistémica estricta) |
| Absolute Traceability | ENGINEERING | ✅ (Evidence Register §19) |

---

## 19. EVIDENCE REGISTER (FinOps) — OUTPUT OBLIGATORIO (Charter §6)

**Trazabilidad:** F0-D → Evidence Register (FinOps) → 2_METH_ADR_MASTER §7

| ID | Canal Charter | Evidencia | Clasificación epistémica | Valor | Fuente |
|---|---|---|---|---|---|
| ER-F01 | Duplicate execution | H-0.8-D | INFERENCIA ESTRUCTURAL — NO VALIDADA EXPERIMENTALMENTE | Magnitud desconocida | E-0.8-003 |
| ER-F02 | Retry waste | W3 granted_ratio | CUANTIFICADO (parcial, límites artificiales) | 3/20 = 0.15 | E-0.9-014 |
| ER-F03 | Retry waste | W3 rejection_ratio | CUANTIFICADO (parcial, límites artificiales) | 17/20 = 0.85 | E-0.9-014 |
| ER-F04 | Post-cancel work | W5 | NO MEDIDO (deferred) | — | §3.3 |
| ER-F05 | Repeated provider calls | W2 | NO MEDIDO (deferred) | — | §3.3 |
| ER-F06 | Failed persistence | W7 interception_rate | CUANTIFICADO (scope: lease-expired ack) | 1/1 = 1.0 | E-0.9-013 |
| ER-F07 | Baseline waste ratio | Global | **PARCIAL** (solo W3+W7 de 5 canales) | No calculable | §16.1 |
| ER-F08 | Hallazgo adicional | W6 telemetry loss | CUANTIFICADO (fuera de mandato) | 1.0 en crash abrupto | E-0.9-012 |
| ER-F09 | Hallazgo adicional | W8 profiler stateless | CUANTIFICADO (fuera de mandato) | ~1.1ms/call | E-0.9-015 |
| ER-F10 | Hallazgo adicional | W4 healing | NOT MEASURABLE | 10/10 N/A | E-0.9-016 |

**Estado del baseline de waste ratio:** PARCIAL. 2/5 canales mandatados medidos. 3/5 deferred a F18. El waste ratio global no puede calcularse hasta que W1, W2, W5 sean ejercitables.

---

## 21. CIERRE DEL HITO 0.9

**Estado del HITO:** FROZEN v1.4.0
**Condición de cierre cumplida:** Canales mandatados por Charter §6 mapeados y clasificados; Evidence Register (FinOps) emitido como output obligatorio; 2 canales medidos (W3 parcial, W7); 3 canales deferred con causa documentada (W1, W2, W5); 3 hallazgos adicionales registrados (W6, W8, W4); 5 gaps abiertos con destino explícito; cero thresholds; correcciones epistemológicas aplicadas; INV-JOURNAL como invariant semántico; H-0.8-D como inferencia estructural.
**Verificación de cadena de gobernanza:** Charter §6 → ADR_F17_BIS_MASTER → HITO_0.8 v1.4.0 → este HITO → Evidence Register → ADR_F18_MASTER.
**Contradicciones con HITOs previos:** Tensión epistemológica con F0-C sobre INV-JOURNAL resuelta: invariant semántico, técnica abierta.
**Siguiente paso recomendado:** ADR_F18_MASTER con todos los HITOs FROZEN (0.1-0.9) y Evidence Registers.

---

## CIERRE DE FASE 0: DISCOVERY COMPLETE

**Estado:** Phase 0 Discovery complete / evidence package frozen.

**Semántica:** "Fase 0 cerrada" significa que el paquete de evidencia está congelado y listo para alimentar el ADR Master. **No significa** que todas las cuestiones arquitectónicas estén resueltas.

**Items abiertos como entradas del diseño F18:**
- GAP-0.9-01 a GAP-0.9-05 (este HITO)
- GAP-0.8-01 a GAP-0.8-07 (HITO_0.8)
- W1/W2/W5 deferred (este HITO)
- DC-01 a DC-13 sin resolver
- DF-34 sin cuantificar coste agregado
- H-0.3-A (representatividad del corpus) NO DEMOSTRADA
- H-0.8-D como inferencia estructural, no validada experimentalmente
- Baseline de waste ratio PARCIAL (3/5 canales deferred)

**El ADR_F18_MASTER deberá resolver estos items como decisiones de diseño, no como auditoría adicional.**

---

## MANIFEST DE ARTEFACTOS CONGELADOS

| HITO | Versión | Rol | Output Charter §6 |
|---|---|---|---|
| 0.1 F0-B | FROZEN v1.2.0 | Discovery estático | Gap Matrix, Contract Map |
| 0.2 F0-G | FROZEN v1.2.0 | Discovery de autoridades | Contract Map (autoridades) |
| 0.3 F0-F | FROZEN v1.3.0 | Discovery de workload | Evidence Register (workload) |
| 0.4 F0-E | FROZEN v1.3.0 | Compliance audit | Contract Map + DC-02/DC-12 |
| 0.5 F0-A Protocol | FROZEN v1.2.0 | Protocolo | — |
| 0.6 Reconciliation | FROZEN v1.0.0 | Reconciliación | — |
| 0.7 F0-A Baseline | FROZEN v1.1.0 | Baseline operacional | Gap Matrix, Contract Map |
| 0.8 F0-C | FROZEN v1.4.0 | Matriz de durabilidad | Gap Matrix (durabilidad) |
| **0.9 F0-D** | **FROZEN v1.4.0** | **Waste/FinOps Map** | **Evidence Register (FinOps)** |

**Nota:** Este manifest debe ser la referencia canónica para ADR_F18_MASTER.