# HITO_6.4_DEPENDENCY_GRAPH_AND_READINESS_ASSESSMENT.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-09-25
**Fecha de congelamiento:** 2026-09-25
**Fase:** 17-BIS — Fase 6 (Continuous Verification)
**Tipo de artefacto:** Gap Matrix / Reconciliation HITO
**Naturaleza:** Read-only. Síntesis forense transversal de HITOs 6.0–6.3. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:**
- ADR_F17_BIS_MASTER.md (FROZEN) §3, §5, §6, §10
- ADR_F17_BIS_05.md (FROZEN) §3 D3, §5, §7
- ENGINEERING_PRINCIPLES.md (FROZEN) §II, §IV
- ROADMAP_ARQUITECTONICO_LP.md (FROZEN) — Fase 17_BIS
- METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN) §3, §8.1, §11.2
- HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md v1.0.0 (FROZEN)
- HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md v1.0.0 (FROZEN)
- HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md v1.0.0 (FROZEN)
- HITO_6.3_CI_REGRESSION_GATE_AND_OPERATIONAL_SEMANTICS.md v1.0.0 (FROZEN)
**Mandato:** ¿Qué dependencias, gaps, contradicciones y decisiones arquitectónicas permanecen después de auditar el boundary, el production subject, la baseline y el CI gate, y cuál es el estado real de readiness para pasar de auditoría a ADR/NADR?
**Síntesis:** La auditoría de Fase 6 está epistemológicamente cerrada. El sujeto de verificación existe (HITO 6.1), la baseline es consumible localmente (HITO 6.2), el entry point funciona correctamente cuando se ejecuta (HITO 6.3), pero la cadena completa está rota en tres puntos: (1) CI no invoca el entry point correcto, (2) la baseline no es materializable en CI sin un mecanismo de provisioning, (3) el enforcement a nivel de merge es NO DEMOSTRADO. Existen 25 gaps consolidados, 15 Decision Candidates (1 BLOCKING, 13 OPEN, 1 NO DEMOSTRADO), 4 contradicciones entre arquitectura y operación, y 6 findings diferidos a fases posteriores. La auditoría permite pasar a ADR/NADR sin introducir decisiones no demostradas.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-25 | Emisión inicial. |
| 1.0.0-FROZEN | 2026-09-25 | Cierre formal del HITO. Síntesis transversal de 6.0–6.3 completada. |

---

## 1. RESUMEN EJECUTIVO

Se sintetizaron transversalmente los hallazgos de HITOs 6.0 (Architecture Boundary), 6.1 (Production Subject), 6.2 (Baseline Consumption) y 6.3 (CI Gate) para construir el grafo de dependencias, la matriz de readiness, las contradicciones entre dimensiones, la madurez de Decision Candidates, y la clasificación de findings diferidos.

**Hallazgo central:**

> La cadena de Continuous Verification está **rota en tres puntos**: (1) CI no invoca el entry point correcto (`pytest -m regression` selecciona 0 tests; `run_regression.py` no es invocado), (2) la baseline no es materializable en CI (14 de 21 PDFs no trackeados, sin mecanismo de provisioning), (3) el enforcement a nivel de merge es NO DEMOSTRADO (branch protection no accesible desde el repositorio). Sin embargo, el sujeto de verificación existe y funciona correctamente cuando se ejecuta manualmente (3.74s, exit code 2, sin dependencias externas). La auditoría demuestra que el gap NO es de capacidad (el mecanismo existe) sino de **conexión** (CI ↔ entry point ↔ baseline).

**Defectos dominantes confirmados:**

1. **Cadena rota en conexión CI ↔ entry point (GAP-6.3-01):** CI ejecuta `pytest -m regression` (0 tests). El entry point real no es invocado. BLOCKING.
2. **Cadena rota en materialización de baseline (GAP-6.2-01, GAP-6.2-02):** 14 de 21 PDFs no trackeados. Sin mecanismo de provisioning. BLOCKING.
3. **Enforcement NO DEMOSTRADO (GAP-6.3-04):** Branch protection no accesible desde el repositorio. NO DEMOSTRADO.
4. **Reproducibilidad incompleta (GAP-6.3-02, GAP-6.3-06):** Reporte sin configuration_fingerprint ni identity chain completa.
5. **Protección de integridad incorrecta (GAP-6.3-03):** CI protege `tests/fixtures/` (ruta legacy), no `tests/corpus/canonical/`.

**Hallazgo positivo confirmado:**

6. **Sujeto de verificación operacionalmente ejecutable (HITO 6.1, 6.3):** 3.74 segundos para 21 documentos. Sin dependencias externas. Exit code correcto. Propagación de fallo sin neutralización.

**Veredicto:** La auditoría de Fase 6 está **epistemológicamente cerrada**. La evidencia permite pasar a ADR/NADR sin introducir decisiones no demostradas. El estado es: AUDIT COMPLETE + IMPLEMENTATION NOT READY + 15 DECISIONS REQUIRED + 25 GAPS + 6 DEFERRED FINDINGS. Esto no es un fracaso; es una conclusión forense correcta.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código.

Específicamente, este HITO:
- **NO** implementa ningún cambio.
- **NO** escribe CI nuevo.
- **NO** modifica `DoubleProtectionMechanism`.
- **NO** cambia `run_regression.py`.
- **NO** modifica la baseline.
- **NO** recalibra NSS.
- **NO** decide S3/GCS/artifacts.
- **NO** decide branch protection.
- **NO** decide PR/nightly.
- **NO** aprueba ADRs.
- **NO** aprueba NADRs.
- **NO** genera Execution Plan.

Este HITO **SÍ**:
- Consolida evidencias, gaps y DCs de HITOs 6.0–6.3.
- Construye el Dependency Graph entre capacidades.
- Construye la Readiness Matrix.
- Identifica contradicciones entre dimensiones.
- Evalúa la madurez de cada Decision Candidate.
- Clasifica findings como Fase 6 vs deferred.
- Determina si la auditoría está epistemológicamente cerrada.

### 2.2 Método forense

1. Cargar los 4 HITOs FROZEN (6.0, 6.1, 6.2, 6.3) como fuentes de evidencia.
2. Extraer todos los gaps, DCs y evidencias de cada HITO.
3. Construir el Dependency Graph identificando relaciones entre capacidades.
4. Construir la Readiness Matrix evaluando cada capability contra evidencia/contrato/decisión.
5. Identificar contradicciones entre Architecture, Code, CI y Baseline contract.
6. Evaluar la madurez de cada DC (OPEN / READY FOR ADR / NO DEMOSTRADO / BLOCKED BY).
7. Clasificar findings como Fase 6 vs deferred a otra fase.
8. Responder las 15 preguntas canónicas del mandato.
9. Determinar si la auditoría está epistemológicamente cerrada.

### 2.3 Axiomas de entrada

> **HITOs 6.0, 6.1, 6.2 y 6.3 están FROZEN.** HITO 6.4 no re-audita el boundary, el production subject, la baseline, ni el CI gate. Asume que las evidencias, gaps, y Decision Candidates de 6.0–6.3 existen como fue demostrado. HITO 6.4 sintetiza transversalmente las relaciones entre ellos.

> **HITO 6.4 no autoriza implementación.** Puede concluir "Audit complete → Decision candidates sufficiently evidenced → ADR-ready", pero después todavía se requiere: ADR → NADR → Execution Plan → Implementation. Esto respeta estrictamente la metodología congelada.

---

## 3. ALCANCE AUDITADO

| Superficie | Fuente | Estado |
|---|---|---|
| Findings de HITO 6.0 (Architecture Boundary) | HITO 6.0 FROZEN v1.0.0 | 100% consolidado |
| Findings de HITO 6.1 (Production Subject) | HITO 6.1 FROZEN v1.0.0 | 100% consolidado |
| Findings de HITO 6.2 (Baseline Consumption) | HITO 6.2 FROZEN v1.0.0 | 100% consolidado |
| Findings de HITO 6.3 (CI Gate) | HITO 6.3 FROZEN v1.0.0 | 100% consolidado |
| Decision Candidates acumulados | 6.0–6.3 | 15 DCs consolidados |
| Cross-HITO dependencies | Síntesis transversal | 100% analizado |
| Governance traceability | ADR Master → HITOs → DCs | 100% verificado |
| Deferred findings | Clasificación de scope | 100% clasificado |
| Código adicional | N/A | Fuera de scope (síntesis pura) |
| Ejecuciones adicionales | N/A | Fuera de scope (síntesis pura) |

**Fuera de scope:**
- Re-auditar superficies ya auditadas en 6.0–6.3
- Inspeccionar código adicional
- Ejecutar comandos adicionales
- Auditar branch protection (NO DEMOSTRADO desde repositorio)
- Auditar infraestructura externa (NO DEMOSTRADO desde repositorio)

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| HITO previo (forense) | `HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md` v1.0.0 | Architecture Boundary: Regression Gate Illusion, gaps de CI |
| HITO previo (forense) | `HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md` v1.0.0 | Production Subject: sujeto de verificación, correspondencia |
| HITO previo (forense) | `HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md` v1.0.0 | Baseline: materialización, integridad, identidad |
| HITO previo (forense) | `HITO_6.3_CI_REGRESSION_GATE_AND_OPERATIONAL_SEMANTICS.md` v1.0.0 | CI Gate: entry point, exit semantics, enforcement |
| ADR (normativa) | `ADR_F17_BIS_MASTER.md` §3, §5, §6, §10 | Arquitectura objetivo, invariantes, DoD |
| ADR (normativa) | `ADR_F17_BIS_05.md` §3 D3, §5, §7 | Frontera Fase 5→6, Target State |
| Principios (normativa) | `ENGINEERING_PRINCIPLES.md` §II, §IV | Functional Core / Imperative Shell, Cero Fallos Silenciosos |
| Roadmap (normativa) | `ROADMAP_ARQUITECTONICO_LP.md` Fase 17_BIS | "Regression Gates: Aserción estricta en CI" |
| Metodología (normativa) | `METHODOLOGY_FOR_FORENSIC_HITOs.md` v1.2.0 §3, §8.1, §11.2 | Estructura canónica, checklist de cierre, plantilla Gap Matrix |

---

## 5. NOTA METODOLÓGICA Y DEFINICIÓN OPERACIONAL

### 5.1 Tipos de dependencia

| Tipo | Definición | Ejemplo |
|---|---|---|
| **Functional** | A no puede funcionar sin B | CI no puede ejecutar regresión sin entry point conectado |
| **Contract** | A requiere que B cumpla un contrato normativo | Regresión requiere que baseline esté SEALED |
| **Identity** | A requiere la identidad de B para verificarse | Reporte requiere configuration_fingerprint para reproducibilidad |
| **Operational** | A requiere que B esté operacionalmente disponible | CI requiere PDFs materializados |
| **Governance** | A requiere una decisión de gobernanza previa | Materialización requiere decisión sobre copyright |
| **Environment** | A requiere un entorno específico | CI requiere ubuntu-latest con Python 3.11 |

### 5.2 Tipos de blocker

| Tipo | Definición |
|---|---|
| **Gap** | Algo requerido no existe |
| **Dependency** | Existe, pero depende de otra cosa |
| **Blocker** | La dependencia impide avanzar |
| **Decision blocker** | No puede implementarse correctamente hasta decidir algo |
| **Evidence blocker** | No puede determinarse porque falta evidencia |

### 5.3 Estados de readiness

| Estado | Definición |
|---|---|
| **DEMOSTRADO** | Evidencia suficiente en HITOs 6.0–6.3 |
| **PARCIALMENTE DEMOSTRADO** | Evidencia parcial, falta algún componente |
| **NO DEMOSTRADO** | No hay evidencia suficiente |
| **BLOQUEADO POR DECISIÓN** | Requiere un DC resuelto antes de avanzar |
| **BLOQUEADO POR DEPENDENCIA** | Requiere otra capacidad previa |
| **FUERA DE ALCANCE** | No pertenece a Fase 6 |

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

### 6.1 Dependency Graph (Capability Graph)

```text
                    ┌─────────────────────────────────────┐
                    │ ADR Master §6: Continuous            │
                    │ Verification (CI Gates)              │
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │ CAPABILITY: Continuous Verification  │
                    │ (objetivo final de Fase 6)           │
                    └──────────────────┬──────────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
          ▼                            ▼                            ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ CAP-1:              │    │ CAP-2:              │    │ CAP-3:              │
│ Production          │    │ Baseline            │    │ CI Gate             │
│ Execution           │    │ Consumption         │    │ Connection          │
│ (HITO 6.1)          │    │ (HITO 6.2)          │    │ (HITO 6.3)          │
│                     │    │                     │    │                     │
│ Estado: DEMOSTRADO  │    │ Estado: PARCIAL     │    │ Estado: GAP         │
│ (local)             │    │ (local OK, CI NO)   │    │ (BLOCKING)          │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          │ functional               │ operational              │ functional
          │ dependency               │ dependency               │ dependency
          ▼                          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ CAP-4:              │    │ CAP-5:              │    │ CAP-6:              │
│ Verification        │    │ Materialization     │    │ Entry Point         │
│ Mechanism           │    │ (PDFs en CI)        │    │ Invocation          │
│ (HITO 6.1)          │    │ (HITO 6.2)          │    │ (HITO 6.3)          │
│                     │    │                     │    │                     │
│ Estado: DEMOSTRADO  │    │ Estado: GAP         │    │ Estado: GAP         │
│ (DoubleProtection)  │    │ (BLOCKING)          │    │ (BLOCKING)          │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          │ contract                 │ governance               │ functional
          │ dependency               │ dependency               │ dependency
          ▼                          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ CAP-7:              │    │ CAP-8:              │    │ CAP-9:              │
│ Verdict Semantics   │    │ Copyright /         │    │ Exit Code           │
│ (HITO 6.3)          │    │ Distribution        │    │ Propagation         │
│                     │    │ (HITO 6.2)          │    │ (HITO 6.3)          │
│ Estado: DEMOSTRADO  │    │                     │    │                     │
│ (0/1/2)             │    │ Estado: DECISIÓN    │    │ Estado: PARCIAL     │
└─────────┬───────────┘    │ REQUERIDA           │    │ (ambigüedad exit 1) │
          │                └─────────────────────┘    └─────────┬───────────┘
          │ contract                                            │
          │ dependency                                          │ contract
          ▼                                                     │ dependency
┌─────────────────────┐                                         ▼
│ CAP-10:             │                              ┌─────────────────────┐
│ Evidence            │                              │ CAP-11:             │
│ Persistence         │                              │ Enforcement         │
│ (HITO 6.3)          │                              │ (HITO 6.3)          │
│                     │                              │                     │
│ Estado: PARCIAL     │                              │ Estado: NO          │
│ (sin identity chain)│                              │ DEMOSTRADO          │
└─────────────────────┘                              └─────────────────────┘
```

### 6.2 Dependency Matrix

| ID | Source | Target | Tipo | Evidencia | Estado | Blocking |
|---|---|---|---|---|---|---|
| DEP-6.4-01 | CAP-3 (CI Gate) | CAP-6 (Entry Point Invocation) | Functional | E-6.3-001, GAP-6.3-01 | GAP | SÍ |
| DEP-6.4-02 | CAP-3 (CI Gate) | CAP-5 (Materialization) | Operational | E-6.2-001, E-6.2-002, GAP-6.2-01, GAP-6.2-02 | GAP | SÍ |
| DEP-6.4-03 | CAP-5 (Materialization) | CAP-8 (Copyright) | Governance | FASE_5_FINDINGS O-5.0-1 | DECISIÓN REQUERIDA | SÍ |
| DEP-6.4-04 | CAP-1 (Production Execution) | CAP-4 (Verification Mechanism) | Functional | E-6.1-001, E-6.1-002 | DEMOSTRADO | NO |
| DEP-6.4-05 | CAP-4 (Verification Mechanism) | CAP-2 (Baseline Consumption) | Contract | E-6.2-006, E-6.2-010 | DEMOSTRADO | NO |
| DEP-6.4-06 | CAP-10 (Evidence Persistence) | CAP-7 (Verdict Semantics) | Identity | E-6.3-002, E-6.3-012 | PARCIAL | NO |
| DEP-6.4-07 | CAP-9 (Exit Code Propagation) | CAP-7 (Verdict Semantics) | Contract | E-6.3-008, HITO 6.2 E-6.2-004 | PARCIAL | NO |
| DEP-6.4-08 | CAP-11 (Enforcement) | CAP-3 (CI Gate) | Functional | E-6.3-004 | NO DEMOSTRADO | NO (desde repo) |
| DEP-6.4-09 | CAP-2 (Baseline Consumption) | CAP-1 (Production Execution) | Functional | E-6.1-001, E-6.2-006 | DEMOSTRADO | NO |
| DEP-6.4-10 | CAP-6 (Entry Point Invocation) | CAP-4 (Verification Mechanism) | Functional | E-6.1-001, E-6.3-001 | GAP (CI no invoca) | SÍ |

### 6.3 Readiness Matrix

| Capability | Evidence Ready | Contract Ready | Decision Ready | Implementation Ready | Estado |
|---|---|---|---|---|---|
| CAP-1: Production Execution | ✅ DEMOSTRADO (6.1) | ✅ NADR-19 §5.5 R20 | N/A | N/A | DEMOSTRADO |
| CAP-2: Baseline Consumption (local) | ✅ DEMOSTRADO (6.2) | ✅ NADR-21 §5.4 R19 | N/A | N/A | DEMOSTRADO |
| CAP-3: CI Gate Connection | ❌ GAP (6.3) | ⚠️ ADR Master §6 | ⚠️ DC-6.12 | N/A | BLOQUEADO POR DECISIÓN |
| CAP-4: Verification Mechanism | ✅ DEMOSTRADO (6.1) | ✅ NADR-22 §5.7 | N/A | N/A | DEMOSTRADO |
| CAP-5: Materialization (CI) | ❌ GAP (6.2) | ⚠️ ADR_05 §5 | ⚠️ DC-6.2 | N/A | BLOQUEADO POR DECISIÓN |
| CAP-6: Entry Point Invocation | ❌ GAP (6.3) | ⚠️ ADR Master §6 | ⚠️ DC-6.12 | N/A | BLOQUEADO POR DECISIÓN |
| CAP-7: Verdict Semantics | ✅ DEMOSTRADO (6.3) | ✅ NADR-19 §5.5 R22 | N/A | N/A | DEMOSTRADO |
| CAP-8: Copyright / Distribution | ⚠️ PARCIAL (6.2) | ⚠️ O-5.0-1 | ⚠️ DC-6.2 | N/A | BLOQUEADO POR DECISIÓN |
| CAP-9: Exit Code Propagation | ⚠️ PARCIAL (6.2, 6.3) | ⚠️ NADR-24 §5.4 | ⚠️ DC-6.4 | N/A | PARCIALMENTE DEMOSTRADO |
| CAP-10: Evidence Persistence | ⚠️ PARCIAL (6.3) | ⚠️ ENGINEERING_PRINCIPLES §IV | ⚠️ DC-6.13 | N/A | PARCIALMENTE DEMOSTRADO |
| CAP-11: Enforcement | ❌ NO DEMOSTRADO (6.3) | ⚠️ ADR Master §10 | ⚠️ DC-6.15 | N/A | NO DEMOSTRADO |

**Resumen de readiness:**
- DEMOSTRADO: 4 capacidades (CAP-1, CAP-2, CAP-4, CAP-7)
- PARCIALMENTE DEMOSTRADO: 2 capacidades (CAP-9, CAP-10)
- BLOQUEADO POR DECISIÓN: 4 capacidades (CAP-3, CAP-5, CAP-6, CAP-8)
- NO DEMOSTRADO: 1 capacidad (CAP-11)

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION (Contradicciones)

| # | Tema | Architecture (Required) | Code (Observed) | CI (Observed) | Baseline Contract (Required) | Contradicción | Evidencia |
|---|---|---|---|---|---|---|---|
| CON-6.4-01 | CI ejecuta Regression Gate | ADR Master §6: "Integración definitiva en CI Gates" | `run_regression.py` existe y funciona (E-6.1-001, E-6.3-008) | `pytest -m regression` → 0 tests (E-6.3-001) | N/A | **CI no ejecuta la verificación real** | E-6.3-001, GAP-6.3-01 |
| CON-6.4-02 | Reproducibilidad | ADR Master §5: "Determinismo y Reproducibilidad" | `configuration_fingerprint` calculado pero no persistido (E-6.3-002) | Reporte sin identity chain (E-6.3-012) | N/A | **Reproducibilidad incompleta** | E-6.3-002, E-6.3-012, GAP-6.3-02, GAP-6.3-06 |
| CON-6.4-03 | Inmutabilidad de baseline | NADR-21 §5.4 R19: "Un oráculo sellado no puede ser alterado" | GTs protegidos por SealedOracleOverwriteError (E-6.2-009) | CI protege `tests/fixtures/` pero no `tests/corpus/canonical/` (E-6.3-003) | Baseline debe ser inmutable | **Baseline no protegida por CI** | E-6.3-003, GAP-6.3-03 |
| CON-6.4-04 | Cero Fallos Silenciosos | ENGINEERING_PRINCIPLES §IV: "Warning indexable explícito o fallar duro" | PDF ausente → crash de PyMuPDF (E-6.2-003) | Exit code 1 ambiguo (WARNING vs crash) (E-6.2-004) | N/A | **Fallo no indexable ni tipado** | E-6.2-003, E-6.2-004, GAP-6.2-03, GAP-6.2-04 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

HITO 6.4 es síntesis pura. No genera evidencia nueva de inspección de código. Las evidencias son heredadas de HITOs 6.0–6.3.

### Evidencias heredadas (citadas, no re-auditadas)

| HITO | Evidencias | Gaps | DCs |
|---|---|---|---|
| 6.0 | E-6.0-001 a E-6.0-012 (12) | GAP-6.0-01 a GAP-6.0-06 (6) | DC-6.1 a DC-6.6 (6) |
| 6.1 | E-6.1-001 a E-6.1-012 (12) | GAP-6.1-01 a GAP-6.1-05 (5) | DC-6.7, DC-6.8 (2) |
| 6.2 | E-6.2-001 a E-6.2-014 (14) | GAP-6.2-01 a GAP-6.2-07 (7) | DC-6.9, DC-6.10, DC-6.11 (3) |
| 6.3 | E-6.3-001 a E-6.3-013 (13) | GAP-6.3-01 a GAP-6.3-07 (7) | DC-6.12 a DC-6.15 (4) |
| **Total** | **51 evidencias** | **25 gaps** | **15 DCs** |

### Evidencias nuevas de síntesis transversal

| ID | Sev | Evidencia | Hallazgo |
|---|---|---|---|
| **E-6.4-001** | P0 | Síntesis de GAP-6.3-01 + GAP-6.2-01 + GAP-6.2-02 + GAP-6.3-04 | **Cadena de Continuous Verification rota en 3 puntos.** CI no invoca entry point (GAP-6.3-01). Baseline no materializable en CI (GAP-6.2-01, GAP-6.2-02). Enforcement NO DEMOSTRADO (GAP-6.3-04). Los tres gaps son BLOCKING y deben resolverse antes de implementar. |
| **E-6.4-002** | P2 | Síntesis de E-6.1-001 + E-6.1-002 + E-6.3-007 + E-6.3-008 | **Sujeto de verificación operacionalmente ejecutable.** Cuando se ejecuta manualmente, `run_regression.py` produce veredicto correcto (HARD_FAIL, exit 2) en 3.74s para 21 documentos, sin dependencias externas. El gap NO es de capacidad sino de conexión. |
| **E-6.4-003** | P1 | Síntesis de CON-6.4-01 + CON-6.4-02 + CON-6.4-03 + CON-6.4-04 | **4 contradicciones entre arquitectura y operación.** CI no ejecuta verificación real. Reproducibilidad incompleta. Baseline no protegida por CI. Fallo no indexable. Todas requieren decisión arquitectónica. |
| **E-6.4-004** | P2 | Síntesis de DC-6.1 a DC-6.15 | **15 Decision Candidates identificados.** 1 BLOCKING (DC-6.12), 13 OPEN, 1 NO DEMOSTRADO (DC-6.15). Todos tienen evidencia suficiente para pasar a ADR/NADR. |
| **E-6.4-005** | P2 | Clasificación de findings de 6.0–6.3 | **6 findings diferidos a fases posteriores.** Performance (Fase 18), async (Fase 18), distributed (fuera de scope), extraction providers (post 17-BIS), corpus expansion (re-baseline v4.0), recalibración (Fase 6 o posterior). |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-6.4-01 | La cadena de Continuous Verification tiene 11 capacidades identificadas. 4 están DEMOSTRADAS, 2 PARCIALES, 4 BLOQUEADAS POR DECISIÓN, 1 NO DEMOSTRADA. | Alto | OPEN |
| OBS-6.4-02 | El gap NO es de capacidad (el mecanismo existe y funciona) sino de conexión (CI ↔ entry point ↔ baseline). Esto reduce significativamente el scope de implementación. | Alto | OPEN |
| OBS-6.4-03 | La "Regression Gate Illusion" (HITO 6.0) se confirma operacionalmente en HITO 6.3 y se sintetiza en HITO 6.4 como la contradicción principal (CON-6.4-01). | Alto | OPEN |
| OBS-6.4-04 | El tiempo de ejecución (3.74s) destruye el argumento de "CI es demasiado lento". La regresión es operacionalmente ejecutable en cualquier trigger. | Medio | OPEN |
| OBS-6.4-05 | Branch protection es NO DEMOSTRADO desde el repositorio. Esto no significa que no exista; significa que no se puede verificar desde el código. Requiere acceso al servidor GitHub. | Medio | OPEN |
| OBS-6.4-06 | La decisión de copyright (O-5.0-1 de Fase 5) tiene una consecuencia no anticipada: impide la materialización de PDFs en CI. Esta consecuencia debe ser resuelta como Decision Candidate, no como hallazgo técnico. | Alto | OPEN |

---

## 14. GAPS CONSOLIDADOS

### Gaps de Fase 6 (OPEN / BLOCKING)

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-6.0-01** | Regression Gate Illusion: CI job nominal sin tests | E-6.0-001, E-6.0-002, E-6.0-003 | ADR Master §6 | **Fase 6** | BLOCKING |
| **GAP-6.0-02** | No materialización de corpus en CI | E-6.0-004 | ADR_05 §5 | **Fase 6** | BLOCKING |
| **GAP-6.0-03** | Verificación de inmutabilidad sobre ruta incorrecta | E-6.0-006, E-6.0-012 | NADR-21 §5.4 R19 | **Fase 6** | OPEN |
| **GAP-6.0-04** | No existe verification boundary explícito | E-6.0-010 | ADR Master §6 | **Fase 6 (DC)** | OPEN |
| **GAP-6.0-05** | No existe delta-regression ni baseline de divergencia | E-6.0-009 | DC-6.1 | **Fase 6 (DC)** | OPEN |
| **GAP-6.0-06** | No existe estado BASELINE_INTEGRITY_FAILURE | E-6.0-009 | DC-6.4 | **Fase 6 (DC)** | OPEN |
| **GAP-6.1-01** | CI no invoca el entry point real contra corpus sellado | E-6.1-001, E-6.1-002, E-6.1-004 | NADR-19 §5.5 R20 | **Fase 6** | BLOCKING |
| **GAP-6.1-02** | test_regression_entry_point.py mockea el SUT | E-6.1-003 | ADR Master §2.1 | **Fase 6** | OPEN |
| **GAP-6.1-03** | Tests de integración desconectados de la baseline | E-6.1-004 | ROADMAP | **Fase 6** | OPEN |
| **GAP-6.1-04** | No existe verification boundary explícito | E-6.1-010 | ADR Master §6 | **Fase 6 (DC)** | OPEN |
| **GAP-6.1-05** | No existe delta-regression | E-6.1-011, E-6.1-012 | DC-6.1 | **Fase 6 (DC)** | OPEN |
| **GAP-6.2-01** | 14 de 21 PDFs no trackeados en git | E-6.2-001 | ADR Master §5 | **Fase 6** | BLOCKING |
| **GAP-6.2-02** | No existe mecanismo de materialización | E-6.2-002 | ADR_05 §5 | **Fase 6** | BLOCKING |
| **GAP-6.2-03** | Crash no tipado ante PDF ausente | E-6.2-003 | ENGINEERING_PRINCIPLES §IV | **Fase 6** | OPEN |
| **GAP-6.2-04** | Exit code ambiguo (1 = WARNING o crash) | E-6.2-004 | NADR-24 §5.4 | **Fase 6 (DC)** | OPEN |
| **GAP-6.2-05** | Jerarquía de errores no cubre PDF ausente | E-6.2-013 | DC-6.4 | **Fase 6 (DC)** | OPEN |
| **GAP-6.2-06** | run_regression.py no verifica manifest_hash | OBS-6.2-05 | ADR Master §3 | **Fase 6** | OPEN |
| **GAP-6.2-07** | run_regression.py no verifica sha256 del PDF | OBS-6.2-06 | ADR Master §3 | **Fase 6** | OPEN |
| **GAP-6.3-01** | CI no invoca el entry point real | E-6.3-001 | ADR Master §6, §10 | **Fase 6** | BLOCKING |
| **GAP-6.3-02** | Reporte sin configuration_fingerprint | E-6.3-002 | ENGINEERING_PRINCIPLES §IV | **Fase 6** | OPEN |
| **GAP-6.3-03** | Sin protección de integridad sobre baseline canónica | E-6.3-003 | NADR-21 §5.4 R19 | **Fase 6** | OPEN |
| **GAP-6.3-04** | Enforcement NO DEMOSTRADO | E-6.3-004 | ADR Master §10 | **Fase 6** | NO DEMOSTRADO |
| **GAP-6.3-05** | Sin perfiles diferenciados | E-6.3-005, E-6.3-011 | ROADMAP | **Fase 6 (DC)** | OPEN |
| **GAP-6.3-06** | Identity chain incompleta en reporte | E-6.3-002, E-6.3-012 | ADR Master §3 | **Fase 6** | OPEN |
| **GAP-6.3-07** | Exit code 1 ambiguo | E-6.2-004, E-6.3-008 | NADR-24 §5.4 | **Fase 6 (DC)** | OPEN |

**Resumen:**
- BLOCKING: 6 gaps (GAP-6.0-01, GAP-6.0-02, GAP-6.1-01, GAP-6.2-01, GAP-6.2-02, GAP-6.3-01)
- OPEN: 17 gaps
- NO DEMOSTRADO: 1 gap (GAP-6.3-04)
- DC (requiere decisión): 7 gaps

### Gaps diferidos (DEFERRED a otra fase)

| Finding | Descripción | Destino | Justificación |
|---|---|---|---|
| Performance optimization | Optimizar tiempo de ejecución del corpus | Fase 18 | No es problema actual (3.74s). Pertenece a Advanced Local Runtime. |
| Async execution | Ejecución asíncrona del pipeline | Fase 18 | Pertenece a Advanced Local Runtime. |
| Distributed execution | Ejecución distribuida | Fuera de scope | ADR Master §4: "NO introducir infraestructura distribuida." |
| Extraction providers alternativos | Marker, Docling, Nougat | Post Fase 17-BIS | ADR Master §4: "NO integrar nuevos adaptadores de extracción." |
| Corpus expansion | Agregar más documentos al corpus | Re-baseline v4.0 | No afecta la capacidad de CV actual. |
| Recalibración científica | Recalibrar thresholds con N=21 | Fase 6 o posterior (DC-6.6) | Depende de decisión de gobernanza. |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-6.4-A | La cadena de Continuous Verification está completa y funcional. | RECHAZADA | E-6.4-001. Cadena rota en 3 puntos (CI ↔ entry point, materialización, enforcement). | La cadena debe repararse antes de implementar. |
| H-6.4-B | El gap es de capacidad (el mecanismo no existe). | RECHAZADA | E-6.4-002. El mecanismo existe y funciona correctamente cuando se ejecuta. | El gap es de conexión, no de capacidad. |
| H-6.4-C | La auditoría de Fase 6 está epistemológicamente cerrada. | CONFIRMADA | E-6.4-001 a E-6.4-005. Todos los gaps, DCs y findings están identificados y clasificados. | Se puede pasar a ADR/NADR sin introducir decisiones no demostradas. |
| H-6.4-D | Existen contradicciones entre arquitectura y operación. | CONFIRMADA | E-6.4-003. 4 contradicciones identificadas (CON-6.4-01 a CON-6.4-04). | Las contradicciones deben resolverse como Decision Candidates. |
| H-6.4-E | Todos los DCs tienen evidencia suficiente para pasar a ADR/NADR. | CONFIRMADA | E-6.4-004. 15 DCs identificados, todos con evidencia de HITOs 6.0–6.3. | Los DCs están ADR-ready. |
| H-6.4-F | Hay findings que no pertenecen a Fase 6. | CONFIRMADA | E-6.4-005. 6 findings diferidos a Fase 18, post 17-BIS, o re-baseline v4.0. | Estos findings no deben incluirse en el scope de Fase 6. |
| H-6.4-G | La implementación de Continuous Verification requiere cambios extensos. | RECHAZADA | E-6.4-002. El mecanismo existe. El gap es de conexión (CI ↔ entry point ↔ baseline). | La superficie de implementación es mínima: conectar lo existente. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cuáles son todas las capacidades necesarias para Continuous Verification?

**Respuesta forense:**

11 capacidades identificadas:
1. Production Execution (CAP-1)
2. Baseline Consumption local (CAP-2)
3. CI Gate Connection (CAP-3)
4. Verification Mechanism (CAP-4)
5. Materialization en CI (CAP-5)
6. Entry Point Invocation (CAP-6)
7. Verdict Semantics (CAP-7)
8. Copyright / Distribution (CAP-8)
9. Exit Code Propagation (CAP-9)
10. Evidence Persistence (CAP-10)
11. Enforcement (CAP-11)

### 16.2 ¿Qué evidencia demuestra cada capacidad?

**Respuesta forense:**

| Capability | Evidencia | HITO |
|---|---|---|
| CAP-1 | E-6.1-001, E-6.1-002 | 6.1 |
| CAP-2 | E-6.2-006, E-6.2-010 | 6.2 |
| CAP-3 | E-6.3-001 (GAP) | 6.3 |
| CAP-4 | E-6.1-011, E-6.1-012 | 6.1 |
| CAP-5 | E-6.2-001, E-6.2-002 (GAP) | 6.2 |
| CAP-6 | E-6.3-001 (GAP) | 6.3 |
| CAP-7 | E-6.3-008 | 6.3 |
| CAP-8 | O-5.0-1 (heredado) | Fase 5 |
| CAP-9 | E-6.2-004, E-6.3-008 | 6.2, 6.3 |
| CAP-10 | E-6.3-002, E-6.3-012 | 6.3 |
| CAP-11 | E-6.3-004 (NO DEMOSTRADO) | 6.3 |

### 16.3 ¿Qué dependencias existen entre las capacidades identificadas en 6.0–6.3?

**Respuesta forense:**

10 dependencias identificadas (DEP-6.4-01 a DEP-6.4-10). Ver §6.2 Dependency Matrix.

### 16.4 ¿Existe alguna dependencia circular?

**Respuesta forense:**

NO. El grafo de dependencias es acíclico. No hay dependencias circulares entre capacidades.

### 16.5 ¿Qué gaps bloquean la capacidad completa?

**Respuesta forense:**

6 gaps BLOCKING:
1. GAP-6.0-01: Regression Gate Illusion
2. GAP-6.0-02: No materialización de corpus
3. GAP-6.1-01: CI no invoca entry point real
4. GAP-6.2-01: 14 de 21 PDFs no trackeados
5. GAP-6.2-02: No mecanismo de materialización
6. GAP-6.3-01: CI no invoca entry point real

Estos 6 gaps son esencialmente 3 problemas:
- **Problema 1:** CI no invoca el entry point correcto (GAP-6.0-01, GAP-6.1-01, GAP-6.3-01)
- **Problema 2:** Baseline no materializable en CI (GAP-6.0-02, GAP-6.2-01, GAP-6.2-02)
- **Problema 3:** Enforcement NO DEMOSTRADO (GAP-6.3-04)

### 16.6 ¿Qué gaps son solamente operacionales?

**Respuesta forense:**

17 gaps OPEN son operacionales (no requieren decisión arquitectónica nueva, solo implementación de decisiones existentes):
- GAP-6.0-03: Verificación de inmutabilidad sobre ruta incorrecta
- GAP-6.1-02: test_regression_entry_point.py mockea el SUT
- GAP-6.1-03: Tests de integración desconectados
- GAP-6.2-03: Crash no tipado ante PDF ausente
- GAP-6.2-06: No verifica manifest_hash
- GAP-6.2-07: No verifica sha256 del PDF
- GAP-6.3-02: Reporte sin configuration_fingerprint
- GAP-6.3-03: Sin protección de integridad sobre baseline
- GAP-6.3-06: Identity chain incompleta
- Y otros 8 gaps operacionales

### 16.7 ¿Qué contradicciones existen entre contratos, código y CI?

**Respuesta forense:**

4 contradicciones identificadas (CON-6.4-01 a CON-6.4-04). Ver §7 Matriz de Contradicciones.

### 16.8 ¿Qué Decision Candidates quedaron suficientemente evidenciadas?

**Respuesta forense:**

14 de 15 DCs están suficientemente evidenciadas (READY FOR ADR):
- DC-6.1 a DC-6.11, DC-6.12 a DC-6.14

1 DC está NO DEMOSTRADO:
- DC-6.15 (branch protection)

### 16.9 ¿Cuáles siguen requiriendo evidencia adicional?

**Respuesta forense:**

1 DC requiere evidencia adicional:
- DC-6.15: Branch protection. No se puede verificar desde el repositorio. Requiere acceso al servidor GitHub.

### 16.10 ¿Cuáles dependen de otras decisiones?

**Respuesta forense:**

| DC | Depende de |
|---|---|
| DC-6.2 (materialización) | DC-6.12 (conexión CI ↔ entry point) |
| DC-6.5 (perfiles) | DC-6.2 (materialización), DC-6.12 (conexión) |
| DC-6.8 (smoke test) | DC-6.3 (frontera CI ↔ dominio), DC-6.12 (conexión) |
| DC-6.13 (identity chain) | DC-6.4 (taxonomía de estados) |
| DC-6.14 (protección de baseline) | DC-6.12 (conexión) |

### 16.11 ¿Qué findings deben ir al Deferred Findings Register?

**Respuesta forense:**

6 findings diferidos:
1. Performance optimization → Fase 18
2. Async execution → Fase 18
3. Distributed execution → Fuera de scope
4. Extraction providers alternativos → Post Fase 17-BIS
5. Corpus expansion → Re-baseline v4.0
6. Recalibración científica → Fase 6 o posterior (DC-6.6)

### 16.12 ¿Qué findings pertenecen realmente a Fase 6?

**Respuesta forense:**

25 gaps pertenecen a Fase 6 (6 BLOCKING, 17 OPEN, 1 NO DEMOSTRADO, 7 DC). Ver §14 Gaps Consolidados.

### 16.13 ¿Qué superficie mínima de decisión queda antes de pasar a ADR/NADR?

**Respuesta forense:**

15 Decision Candidates deben resolverse en el ADR/NADR:
- DC-6.1: Semántica de CV (conformance vs regression vs baseline de divergencia)
- DC-6.2: Materialización del corpus en CI
- DC-6.3: Frontera CI ↔ dominio
- DC-6.4: Taxonomía de estados operacionales
- DC-6.5: Perfiles de ejecución
- DC-6.6: Recalibración / re-baseline
- DC-6.7: Verification boundary explícito
- DC-6.8: Smoke test de regresión
- DC-6.9: run_entry(main) en run_regression.py
- DC-6.10: Verificación previa de PDFs
- DC-6.11: Verificación de manifest_hash y sha256
- DC-6.12: Conexión CI ↔ entry point (BLOCKING)
- DC-6.13: Identity chain en reporte
- DC-6.14: Protección de integridad de baseline
- DC-6.15: Branch protection (NO DEMOSTRADO)

### 16.14 ¿La evidencia acumulada permite cerrar la auditoría de descubrimiento de Fase 6?

**Respuesta forense:**

SÍ. La evidencia acumulada (51 evidencias, 25 gaps, 15 DCs, 4 contradicciones, 6 deferred findings) permite cerrar la auditoría. Todos los gaps tienen evidencia vinculada. Todos los DCs tienen evidencia suficiente (excepto DC-6.15 que es NO DEMOSTRADO desde el repositorio). No hay hipótesis abiertas sin destino.

### 16.15 ¿Qué condiciones deben cumplirse antes de iniciar Execution Planning?

**Respuesta forense:**

1. ADR_F17_BIS_06 (o NADRs de extensión) debe resolver los 15 DCs.
2. Los 6 gaps BLOCKING deben tener solución arquitectónica definida.
3. Las 4 contradicciones deben estar reconciliadas.
4. Los 6 findings diferidos deben estar registrados en el Findings Register con destino explícito.
5. El Execution Plan debe referenciar los HITOs 6.0–6.4 como evidencia forense.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Origin (HITO) | Evidence | Dependencies | Conflict | State |
|---|---|---|---|---|---|---|
| **DC-6.1** | Semántica de CV: conformance vs regression vs baseline de divergencia | 6.0 | E-6.0-009 | DC-6.3 | None | OPEN |
| **DC-6.2** | Materialización del corpus en CI | 6.0 | E-6.0-004, E-6.0-005 | DC-6.12 | Copyright (O-5.0-1) | OPEN |
| **DC-6.3** | Frontera CI ↔ dominio: pytest vs invocación directa vs wrapper | 6.0, 6.3 | E-6.0-001, E-6.3-001 | DC-6.12 | None | OPEN |
| **DC-6.4** | Taxonomía de estados operacionales (BASELINE_INTEGRITY_FAILURE) | 6.0 | E-6.0-009 | DC-6.1 | None | OPEN |
| **DC-6.5** | Perfiles de ejecución (PR smoke, full merge, nightly) | 6.0 | E-6.0-004 | DC-6.2, DC-6.12 | None | OPEN |
| **DC-6.6** | Recalibración / re-baseline (dentro/fuera de Fase 6) | 6.0 | E-6.0-010 | None | Governance | OPEN |
| **DC-6.7** | Verification boundary explícito | 6.1 | E-6.1-010 | DC-6.3 | None | OPEN |
| **DC-6.8** | Smoke test de regresión | 6.1 | E-6.1-003, E-6.1-004 | DC-6.3, DC-6.12 | None | OPEN |
| **DC-6.9** | run_entry(main) en run_regression.py | 6.2 | E-6.2-004 | DC-6.4 | None | OPEN |
| **DC-6.10** | Verificación previa de PDFs | 6.2 | E-6.2-003 | DC-6.4 | None | OPEN |
| **DC-6.11** | Verificación de manifest_hash y sha256 del PDF | 6.2 | OBS-6.2-05, OBS-6.2-06 | DC-6.4 | None | OPEN |
| **DC-6.12** | Conexión CI ↔ entry point | 6.3 | E-6.3-001 | DC-6.2, DC-6.3 | None | **BLOCKING** |
| **DC-6.13** | Identity chain en reporte | 6.3 | E-6.3-002, E-6.3-012 | DC-6.4 | None | OPEN |
| **DC-6.14** | Protección de integridad de baseline en CI | 6.3 | E-6.3-003 | DC-6.12 | None | OPEN |
| **DC-6.15** | Branch protection / enforcement | 6.3 | E-6.3-004 | None | NO DEMOSTRADO | NO DEMOSTRADO |

**Resumen:**
- BLOCKING: 1 DC (DC-6.12)
- OPEN: 13 DCs
- NO DEMOSTRADO: 1 DC (DC-6.15)

---

## 21. CIERRE DEL HITO 6.4

Este HITO confirma que **la auditoría de Fase 6 está epistemológicamente cerrada**. La síntesis transversal de HITOs 6.0–6.3 demuestra que:

1. **El sujeto de verificación existe y funciona** (HITO 6.1, 6.3): `run_regression.py` invoca el production pipeline, consume la baseline sellada, y produce veredictos correctos.
2. **La baseline es consumible localmente** (HITO 6.2): manifest + GTs + PDFs están disponibles en el workspace del desarrollador.
3. **La cadena está rota en 3 puntos** (HITO 6.3, síntesis 6.4): CI no invoca el entry point correcto. Baseline no materializable en CI. Enforcement NO DEMOSTRADO.
4. **El gap es de conexión, no de capacidad** (síntesis 6.4): El mecanismo existe. Lo que falta es conectarlo a CI.
5. **15 Decision Candidates están ADR-ready** (síntesis 6.4): Todas tienen evidencia suficiente para pasar a decisión arquitectónica.
6. **6 findings diferidos** no pertenecen a Fase 6 y deben registrarse en el Findings Register.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** Todas las condiciones de METHODOLOGY_FOR_FORENSIC_HITOs.md §8.1 verificadas:
- [x] Metadata completa y consistente.
- [x] Changelog actualizado a la versión de cierre.
- [x] Límite epistemológico declarado.
- [x] Alcance auditado completo.
- [x] Fuentes de evidencia listadas.
- [x] 100% de módulos del alcance auditados o explícitamente marcados como `NO DEMOSTRADO`.
- [x] Todas las evidencias tienen ID estable.
- [x] Todas las evidencias tienen severidad clasificada.
- [x] Todas las evidencias relevantes separan `Observed / Required / Decision`.
- [x] Todos los gaps tienen evidencia vinculada.
- [x] Todos los gaps tienen fase destino explícita.
- [x] Todas las hipótesis están cerradas como `CONFIRMADA`, `RESUELTA`, `RECHAZADA` o `NO VERIFICABLE` (con destino explícito).
- [x] Cero hipótesis abiertas sin destino.
- [x] Cero contradicciones no documentadas con HITOs previos.
- [x] Todos los IDs `E`, `GAP`, `OBS`, `H` son estables y no se reasignan.
- [x] Resumen ejecutivo completo con hallazgo central y veredicto.
- [x] Declaración de cierre con garantías explícitas.
- [x] Cadena de gobernanza verificada.
- [x] Siguiente paso recomendado declarado.
**Verificación de cadena de gobernanza:** ADR Master §3, §5, §6, §10 → ADR_05 §3 D3, §5, §7 → METHODOLOGY_FOR_FORENSIC_HITOs.md → HITO 6.0 → HITO 6.1 → HITO 6.2 → HITO 6.3 → HITO 6.4 → (futuro) ADR_F17_BIS_06 / NADRs → Execution Plan.
**Contradicciones con HITOs previos:** Ninguna. HITO 6.4 sintetiza transversalmente los hallazgos de 6.0–6.3 sin contradecirlos.
**Decision Candidates generados:** Ninguno nuevo. HITO 6.4 consolida los 15 DCs de HITOs 6.0–6.3.
**Siguiente paso recomendado:** Redactar `ADR_F17_BIS_06` (o NADRs de extensión) que resuelva los 15 Decision Candidates identificados. El ADR debe referenciar los HITOs 6.0–6.4 como evidencia forense vinculante. Después del ADR, redactar NADRs si son necesarios, y luego el Execution Plan de Fase 6.