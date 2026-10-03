# FASE0_AUDIT_CHARTER.md
## Charter de la Compuerta de Auditoría (Fase 0) — Fase 18 (Advanced Local Runtime)

* **Versión:** 1.0.0
* **Estado:** FROZEN (preregistro de Fase 0; congelado por aprobación del Board en kickoff)
* **Fecha:** 2026-10-01
* **Autoridad:** Architecture Board
* **Aprobación Board:** 2026-10-01 (comment de aprobación DC-06a del owner en PR #5; merge # 10f0eb8ce8c2c24575584d70947dd12ab8ae3726)
* **Ubicación:** `docs/architecture/adr/phase-18/00-foundation/FASE0_AUDIT_CHARTER.md`
* **Derivado de:** ROADMAP_ARQUITECTONICO_LP v3.0 (§IV Fase 18), ADR_F17_BIS_MASTER (§9 jerarquía),
  2_METH_ADR_MASTER v1.0.1 (§2 DoR, §7 compuerta de auditoría), METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES v1.4.0
  (§3.5.1 HITOs, §6.2 precedencia), FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED v1.0.0, PROJECT_SCOPE, ENGINEERING_PRINCIPLES
* **Naturaleza:** plan de auditoría y preregistro de medición. **NO es evidencia forense** (la evidencia
  son los HITOs que este charter genera), **NO es ADR**, **NO es Execution Plan** y por tanto **no usa
  nomenclatura Gate/Wave**, que pertenece al nivel operativo (§3.4 y §6.5 de la metodología general).

---

## 1. HIPÓTESIS DE ALCANCE (no es el ADR)

F18 madura el Execution Plane local para operar bajo recursos finitos con
concurrencia controlada, backpressure, recovery, idempotencia y cancelación,
preservando la semántica científica, las autoridades existentes y la
reproducibilidad de la evidencia científica.

**F18 modifica el mecanismo de ejecución; no modifica la verdad científica.**
Toda técnica de implementación queda subordinada a evidencia de necesidad,
compatibilidad arquitectónica y ausencia de degradación científica.

Hito provisional (sin números hasta baseline): demostrar que el Execution Plane
opera bajo recursos finitos con admisión, backpressure, recovery, cancelación e
idempotencia, preservando invariantes científicas y de identidad.

---

## 2. GOBERNANZA DEL KICKOFF (DC-06a / DC-06b)

* **DC-06a (significado del hito):** RESUELTA en kickoff por decisión de Board
  (2026-10-01, comment en PR #{N}): Opción A — pivot normativo documentado aquí
  y en §1 del futuro ADR_F18_MASTER. El hito no significa "producto completo"
  mientras existan F19–F21.
* **DC-06b (técnicas prescritas por ROADMAP v3.0):** abierto, evidence-driven.
  Si la Fase 0 **no demuestra beneficio suficiente según el criterio
  preregistrado (§9)** para una técnica prescriptiva (p.ej. async puro sin
  mejora medible, elisión del bridge con costo neto no compensado), la salida
  es decisión de Board o enmienda ROADMAP v3.0→v3.1. El ADR Maestro no
  reescribe retroactivamente el ROADMAP.

**Ciclo de vida de este documento:** se congela como **preregistro** con la
aprobación del Board en kickoff (esa congelación es la que da valor a §9: los
criterios quedan fijados antes de medir). Los HITos F0 que este charter genera
se FROZEN individualmente al completarse (§6). Este charter no se reformatea ni
se re-numera como HITO.

---

## 3. CAPACIDADES OBLIGATORIAS (C1–C13) Y TÉCNICAS CANDIDATAS

Catálogo **provisional**, sujeto a validación o refutación por la Fase 0. No es
fuente de verdad definitiva: esa calidad la adquiere el ADR_F18_MASTER FROZEN.

C1 Bounded Execution · C2 Admission Control · C3 Backpressure · C4 Recovery ·
C5 Idempotency · C6 Cancellation · C7 Concurrency Safety · C8 Scientific
Neutrality · C9 Scientific Determinism Under Operational Variation (mismo input
y parámetros científicos congelados ⇒ mismo resultado científico, independientemente
de schedule, concurrencia o variación operacional; no exige determinismo del
runtime operacional, solo del resultado científico) · C10 Local Resource
Efficiency (solo con evidencia) · C11 Operational Visibility mínima (F20 posee
forensía) · C12 Outcome-Taxonomy Integrity (presión de recursos ⇒ outcome
operacional, nunca señal científica) · C13 Verification-Path Determinism
(verification subject sin scheduler por defecto; concurrencia opt-in gobernada
sujeta a C8/C9).

**Nota de procedencia:** C13 refina el catálogo C1–C12 previo (opción B):
neutralidad científica y determinismo del mecanismo de verificación son
capacidades distintas y se norman por separado.

Técnicas candidatas (🟡 benchmark-dependent; 🔴 fuera): pure async, elisión de
SyncProviderBridge, threads/process pools, object pools, zero-copy, lazy
loading, batching adaptativo, LLM cache, SQLite cache, adaptive placement,
nuevos estados FSM, tiers 8k/32k/1M. 🔴: semantic/embedding cache (F21),
model routing (F21).

---

## 4. INVARIANTES (redacción de propiedad objetivo, no de mecanismo)

Las invariantes declaran **qué debe ser verdadero**; los mecanismos concretos
(WAL vs commit windows, at-least-once vs at-most-once con idempotency-key, etc.)
quedan abiertos a los Decision Candidates correspondientes.

* **INV-SCI-1:** misma baseline sellada + mismos `FrozenParameters` ⇒ misma
  salida científica y evidencia científica canónica, independiente de schedule,
  concurrencia, budgets y cache.
* **INV-OPS-1:** las diferencias operacionales no alteran el resultado científico
  ni falsifican la evidencia científica; viven en evidencia operacional separada.
* **INV-ASSEMBLY-ORDER (acceptance criterion, hipótesis a demostrar en M1 (§8.1)
  con el contrato de F0-E):** ejecuciones concurrentes con permutaciones forzadas
  del orden de completitud MUST producir identidad de artefacto idéntica bajo
  parámetros científicos congelados; el ensamblado mergea por identidad/lineage.
* **INV-CACHE:** un hit devuelve exactamente el valor almacenado bajo su clave;
  la clave es identidad framed (`core/shared/identity_contracts.py`); no se
  atribuye al cache garantía que el proveedor no ofrece (DC-03).
* **INV-JOURNAL (propiedad objetivo):** ningún efecto externo podrá producirse
  sin una intención/lease/reserva recuperable tras crash y una aplicación
  idempotente del resultado. **El mecanismo concreto** (SQLite WAL vs otro,
  single-writer actor vs commit windows, semántica at-least-once vs
  at-most-once con idempotency-key del proveedor, semánticas por unidad) queda
  abierto a DC-01/DC-08. La propiedad obligatoria es: **idempotent apply** y
  **ventana de duplicación acotada y medida** (waste).
* **INV-UNITS:** documento = aislamiento/recuperación; chunk = scheduling/retry;
  batch-call = costo FinOps; execution = identidad/evidencia.
* **INV-EXEC-IDENTIFIABILITY:** el modo/política de ejecución es identificable y
  reproducible y habilita testing diferencial; excluido de la identity
  científica (DC-02); sin nombres de modo congelados.
* **INV-NO-RESOURCE-SIGNAL:** agotamiento de budget ⇒ EXECUTION_FAILURE (exit 4)
  con evidencia persistida; nunca REGRESSION/PASS; shed/cancel/hold con razón
  indexable propia (sin contaminar DEAD_LETTER/RETRYING; sin nuevo estado FSM
  hasta auditar el existente, DC-11).
* **INV-VERIFICATION-ISOLATION:** el verification subject (`run_regression`,
  benchmark) corre sin scheduler ni concurrencia por defecto; concurrencia
  opt-in gobernada sujeta a INV-SCI-1.

**Nota sobre semánticas por unidad:** la semántica de entrega (at-least-once,
at-most-once con idempotency-key, exactly-once visible) puede variar por unidad
(document execution, chunk execution, provider call, artifact persistence).
INV-JOURNAL exige **idempotent apply** como propiedad obligatoria; la semántica
de entrega de cada unidad se decide en DC-01/DC-08, no se uniforma aquí.

---

## 5. REGLAS DE PROCESO DE LA FASE 0

1. **NO CODE:** no se modifica código de producción ni se introducen
   abstracciones. La Fase 0 observa, mapea, mide y documenta.
2. **NO MUTACIÓN de estado normativo:** no se modifica estado productivo,
   artefactos sellados, oráculos, ni ninguna autoridad de gobernanza (FSM,
   identity, FinOps, corpus canónico, Ground Truth). **Todo efecto operacional
   inevitable** (requests a providers, escrituras temporales, logs, locks) se
   ejecuta sobre un **entorno efímero/aislado** (temp dir, DB aislada,
   workspace de medición) y se identifica explícitamente en el protocolo de
   medición. Medir traducción real está permitido si el protocolo lo documenta
   y el estado resultante no es normativo ni persistente.
3. **Medición externa:** `tracemalloc`, `resource`, SQLite statistics, provider
   logs, subprocess wrappers, timing externo, observación de filesystem. Sin
   instrumentación interna nueva. **La Fase 0 mide; F18 instrumenta (C11).**
   Medir el sistema nuevo con la instrumentación del sistema nuevo contaminaría
   el baseline.
4. **Preregistro en dos capas:** la **forma** de métricas y criterios
   accept/reject se fija con este charter congelado (§9); los **números** se
   derivan del baseline F0-A mediante una regla de calibración preregistrada
   (§9) y no se modifican después salvo invalidación formal (§9).
5. **Protocolo reproducible:** hardware envelope, condiciones, repeticiones,
   versiones y entorno efímero documentados en F0-A/F0-D para que el baseline
   sea ancla comparable post-F18.
6. **Reuse Before Invent:** toda sustitución de autoridad existente exige
   evidencia de insuficiencia.
7. **No New Authority Without Boundary:** toda autoridad nueva propuesta en F18
   declara frontera contra FSM, reconciler, identity, FinOps, shutdown y dominio.
   Admission policy como Functional Core (pura); executors como Imperative Shell.
8. **Workload corpus:** manifiesto e identidad versionada propios, **nunca
   sellado como oráculo** (no toca biyección NADR-26 ni Ground Truth); reutilizar
   PDFs del corpus científico como carga está permitido. **Ubicación física a
   decidir en F0-F** conforme a la Guía de Documentación de Arquitectura (§2/§4);
   este charter no la pre-decide.

---

## 6. ETAPAS DE AUDITORÍA Y HITos RESULTANTES (F0-A..F0-G)

Cada F0 completado se commitea como **HITO_0.x_{NOMBRE}.md** en
`00-foundation/` (nomenclatura de metodología general §7.5). Este charter **no**
es un HITO: es el plan que los genera.

**Etapa de auditoría 1** (sin medición de runtime): **F0-B** Concurrency &
Blocking Map (stage → I/O/CPU/mixed → mecanismo actual → blocking source →
candidate executor → evidence) · **F0-F** Workload Characterization (corpus de
carga versionado con identidad propia; representatividad demostrada, no asumida;
ubicación según §5.8) · **F0-G** Authority Boundary Map · **F0-E** Scientific
Neutrality / Runtime Isolation Map + contrato de comparación del guard
diferencial (campos/hashes exactos: hash de AST por nodo, hash de artefacto
ensamblado, métricas científicas por documento, subset canónico de evidencia
científica; tolerancia = exactitud con params congelados).
No se perfila sobre workload no caracterizado ni se mapean autoridades después
de decidir.

**Etapa de auditoría 2:** **F0-A** Runtime Profile Baseline sobre anchor
(21 docs sellados) + workload corpus, por etapa (extraction, normalización,
segmentación, chunking, traducción, validación, ensamblado, TED, hashing,
serialización, SQLite): wall, CPU, peak RSS, allocations, I/O wait, provider
latency, tokens, retries.

**Etapa de auditoría 3:** **F0-C** State Durability & Recovery Map (state →
authority → storage → durability → recovery behavior → loss window; verifica
durabilidad/convergencia de activos reclamados: FSM, reconciler, chaos_runner,
supervisor) · **F0-D** Waste/FinOps Map (duplicate execution, retry waste,
post-cancel work, repeated provider calls, failed persistence; baseline de
waste ratio).

**F0-G contenido y frontera:** inventario de autoridades existentes
(FSM/NADR-09, identity_contracts, estimator/BudgetVerdict,
DaemonSupervisor/GracefulShutdown, reconciler, entry point CV) con boundary,
estado que posee y clasificación reuse/extend/replace; toda autoridad propuesta
nueva con frontera declarada (§5.7). F0-G verifica autoridad; F0-C verifica
durabilidad/recovery de los mismos activos (sin solapamiento).

**Trazabilidad F0 → outputs obligatorios de 2_METH_ADR_MASTER §7:**
F0-A/F0-B → Gap Matrix y Contract Map · F0-C → Gap Matrix (durabilidad) ·
F0-D → Evidence Register (FinOps) · F0-E → Contract Map + DC-02/DC-12 ·
F0-F → Evidence Register (workload) · F0-G → Contract Map (autoridades).

---

## 7. DECISION REGISTER (criterio de resolución, no opinión)

Cada DC se resuelve como **RESOLVED** (con evidencia) o **DEFERRED** con
**DESTINATION** (fase o mecanismo) y **TRIGGER** (condición que lo reactiva).
DEFERRED sin destination+trigger se considera mal formado y bloquea el cierre.

| DC | Pregunta | Criterio de resolución |
|---|---|---|
| DC-01 | Fork de concurrencia: async single-process + executors vs multi-process | F0-B + F0-C; subsume DF-24, decide backing de DF-34 y topología |
| DC-02 | ¿Parámetros de runtime en `configuration_identity` científica o metadata operacional? | INV-SCI-1 debe sostenerse cualquiera sea la respuesta; F0-E define el schema |
| DC-03 | ¿Qué nivel de determinismo **observable y reproducible** puede demostrarse para cada provider bajo el protocolo de Fase 0 (byte / structural / semantic / nondeterministic) y qué nivel necesita cada consumidor? | Contrato de proveedor medido empíricamente (no asumido por claim); prerequisito de INV-CACHE |
| DC-04 | Alcance de caches: pure-function 🟢 / LLM 🟡 / semantic+embedding 🔴 | Checklist de completitud de clave + evidencia disponible de comportamiento actual (F0-D); **la medición de hit-rate de una cache nueva pertenece a la implementación de F18**, no a Fase 0; semantic/embedding → F21 |
| DC-05 | ¿Unificar ExecutionContext o contextos especializados? | Test de god-object: qué boundary protege cada contexto |
| DC-06a | ¿Qué significa el hito de F18? | Decisión de Board en kickoff (pivot normativo en §1 del futuro Maestro) |
| DC-06b | ¿Las técnicas prescritas del ROADMAP sobreviven? | Evidencia de Fase 0 vs criterio preregistrado → decisión de Board o enmienda ROADMAP v3.1; el ADR no reescribe el ROADMAP |
| DC-07 | ¿Tiers 8k/32k/1M o `batch = f(budgets)`? | Unidades = tokens por call contra límites de proveedor medidos (F0-A/F0-F) |
| DC-08 | Write-policy SQLite (single-writer actor vs commit windows; pragmas por tipo de estado) + mecanismo de journal de INV-JOURNAL | Consecuencia de DC-01 + F0-C; se resuelven juntos |
| DC-09 | Semántica de producto de interrupción (documento degradado coherente con warnings) | Frontera F19; tolerancia existente del assembler como evidencia |
| DC-10 | Fairness y admission deadlock-free | F0-F + F0-B; admitir conjuntos dependency-ready o diferir sin retener recursos |
| DC-11 | Semántica de admisión-diferida sin nuevo estado FSM | Auditoría del FSM existente en F0-C; razón indexable + admission record antes que estado nuevo |
| DC-12 | Contrato y promoción del guard diferencial | Contrato en F0-E; maduración M0–M3 (§8.1) |

---

## 8. CRITERIO DE CIERRE DE LA FASE 0

La Fase 0 termina cuando:

- [ ] F0-A..F0-G commiteados como HITos en `00-foundation/`
- [ ] Los cuatro outputs obligatorios de 2_METH_ADR_MASTER §7 commiteados:
      Architecture Gap Matrix, Current State & Contract Map, Evidence Register
      & DC Resolutions, propuesta de congelamiento de `ADR_F18_MASTER`
- [ ] DC-06a aprobada por Board y registrada con fecha
- [ ] Todo DC tiene resolución **RESOLVED** (con evidencia) o **DEFERRED +
      DESTINATION + TRIGGER** (sin ambigüedad sobre qué lo reactiva)
- [ ] Protocolo de medición y preregistro presentes en F0-A/F0-D
- [ ] Regla de calibración de umbrales (§9) documentada en F0-A

Recién entonces se emite `ADR_F18_MASTER` (plantilla 2_METH_ADR_MASTER §3), con
el pivot normativo de DC-06a en su §1.

### 8.1 Maduración del guard diferencial (DC-12)

Secuencia de milestones, independiente de la numeración de gates del futuro
Execution Plan:

* **M0:** contrato de comparación definido (F0-E, Fase 0).
* **M1:** experimento implementado (mismo input, dos modos de ejecución, assert
  de igualdad de evidencia científica) en la primera etapa de implementación de
  runtime del futuro Execution Plan.
* **M2:** estabilidad demostrada (repeticiones sin falsos positivos/negativos).
* **M3:** required check en branch protection para todo PR que toque runtime.

Entre M1 y M3, el guard es obligatorio por política de review para PRs que
toquen runtime (proporcionalidad de la protección a la evidencia, y cierre de la
ventana de riesgo DF-09 durante la implementación).

---

## 9. PRE-REGISTRO DE REGLAS DE DECISIÓN (forma y calibración congeladas; números derivados)

Para cada técnica 🟡: (métrica, dirección, regla de decisión, tope de costo de
complejidad). La **forma** de cada regla y la **regla de calibración** que
deriva los umbrales desde el baseline quedan congeladas con este charter.
Los **números concretos** se instancian desde el baseline F0-A aplicando la
regla de calibración preregistrada; no se modifican después salvo invalidación
formal (ver abajo).

**Regla de calibración preregistrada:** cada umbral `{TBD}` se instancia como
función del baseline F0-A según el esquema de la tabla siguiente. La función
es pública y aplicable mecánicamente; no se re-calibra a mano después.

| Técnica | Métrica + regla de decisión | Calibración desde F0-A |
|---|---|---|
| SyncProviderBridge elision | latencia p95 por etapa I/O, ↓, sin ↑RSS | umbral = p95 baseline × (1 − δ); δ = max(minimum detectable effect, ruido medido) |
| process pools | CPU-time TED/extraction, ↓ | umbral = CPU baseline × (1 − δ); costo IPC ≤ fracción preregistrada de la ganancia |
| object pools / zero-copy | allocations y peak RSS en hotspot, ↓ | umbral = baseline − Δ significativo (potencia estadística preregistrada) |
| lazy loading | peak RSS por doc grande, ↓, sin ↑wall p95 | umbral RSS = baseline × (1 − δ); wall p95 no superior a baseline + ε |
| LLM cache | hit-rate + costo evitado, ≥ umbral (solo si DC-03 lo habilita) | umbral de hit-rate = fracción de workload repetitivo medida en F0-F; costo mínimo evitado por unidad = costo FinOps unitario de F0-A |
| batching adaptativo | tokens desperdiciados por padding, ↓, sin ↑retry rate | umbral = waste baseline × (1 − δ); retry rate no superior a baseline |

**Invalidación formal del baseline:** si F0-A presenta workload insuficiente,
comportamiento patológico, hardware no representativo, proveedor inestable,
outliers no explicados o medición contaminada, el baseline puede invalidarse
abriendo un HITO adicional (`HITO_0.x_F0-A_re-baseline`) que documente la
causa, repita la medición bajo condiciones corregidas y rederive los umbrales.
La invalidación es un acto documentado del Board, no una re-calibración ad-hoc.
Preregistration ≠ blind commitment to bad data.

---

**Nota de Gobernanza:** este charter gobierna la forma y el orden de la
compuerta de auditoría de Fase 18 y preregistra sus criterios de decisión. No
define arquitectura (eso es el ADR_F18_MASTER), no define reglas normativas
(NADRs), no define secuencia operativa (Execution Plan) y no constituye
evidencia forense (HITos). Toda afirmación conceptual nueva a partir de este
punto entra como DC o finding con evidencia, no como análisis textual.