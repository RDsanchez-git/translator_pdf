# HITO_0.6_WORKLOAD_ANCHOR_RECONCILIATION.md

**Estado:** FROZEN v1.1.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02 (v1.1.0)
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Reconciliation HITO
**Naturaleza:** Read-only. Reconcilia una contradicción entre HITO_0.3 v1.3.0 (FROZEN) y evidencia forense nueva. No reescribe el HITO previo.
**Evidencia Forense Vinculante:** `HITO_0.3_F0-F` v1.3.0; `HITO_0.5_F0-A_Runtime_Profile_Protocol` v1.2.0; `HITO_0.7_F0-A_Runtime_Profile_Baseline` v1.0.0; `NADR-F17BIS-24` R11; `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.3 R11-R12, §5.4 R16-R19, §7; `FASE0_AUDIT_CHARTER.md` §5.2, §5.8; `.github/workflows/ci.yml`; `.github/workflows/continuous-verification.yml`; `tests/unit/test_cv_workflow_contract.py`; `infra/db/connection.py`; `tools/evaluation/run_regression.py`
**Mandato:** Reconciliar la contradicción entre la interpretación de separación física de HITO_0.3 y el perímetro normativo real de consumo del anchor, y definir la superficie de medición conforme para F0-A.
**Síntesis:** HITO_0.3 sobre-interpretó Charter §5.8: la separación obligatoria aplica a **escrituras, sellado y aumentos de stress**, no a la **lectura read-only** del anchor. La autoridad primaria de esa lectura es normativa (NADR-25 §7 manda ejecutar el entry point contra el corpus sellado; NADR-26 §5.1 R2/§5.4 R16-R19/§7 restringen mutación y mandan consumo de solo lectura; Charter §5.2/§5.8 permiten medición con writes efímeros); el CI de Fase 6 es corroboración operativa, no autoridad. F0-A midió sobre canonical bajo ese patrón y verificó no-mutación empíricamente (HITO_0.7). El workload paralelo se reclasifica como seed sin identidad para stress docs futuros.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-10-02 | Emisión inicial. Reconciliación formal de HITO_0.3 con evidencia [I1]-[I4]. |
| 1.1.0-FROZEN | 2026-10-02 | Reconciliación post-revisión y post-ejecución: (1) autoridad normativa primaria citada textualmente (NADR-25 §7; NADR-26 §5.1 R2, §5.3 R11-R12, §5.4 R16-R19, §7; NADR-24 R11; Charter §5.2/§5.8); CI Fase 6 degradado a corroboración operativa (F18-0.6-01). (2) Hardware envelope separado en host (RAM/CPU, no conforme) y accelerator (GPU/VRAM, no ejercido por run_regression → N/A) (F18-0.6-03). (3) H-0.6-A cerrada como CONFIRMADA con evidencia empírica de HITO_0.7 (snapshot pre=post en 3 repeticiones). (4) GAP-0.6-01 CLOSED: checksums pre/post implementados y verificados en HITO_0.7 (mecanismo NADR-26 R18 operativo). (5) GAP-0.6-02 permanece OPEN pendiente de confirmación de eliminación, sin efecto sobre F0-A. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la contradicción entre HITO_0.3 v1.3.0 (que declaró BLOCKING la separación física del workload para cualquier medición) y el perímetro normativo real de consumo del anchor sellado.

**Hallazgo central:**

> La prohibición normativa (NADR-26) recae sobre **mutar/re-sellar/romper biyección** del oráculo, no sobre **leerlo**; y NADR-25 §7 **manda** ejecutar el verification entry point contra el corpus canónico sellado. El patrón conforme es "ejecutar read-only sobre canonical + verificar checksums pre/post". HITO_0.3 convirtió una restricción de escritura en una restricción de lectura: sobre-interpretación. El CI de Fase 6 corrobora operativamente este patrón, pero la autoridad es normativa, no operacional.

**Defectos dominantes confirmados:**

1. **Contradicción documental (E-0.6-001, E-0.6-002, E-0.6-008):** HITO_0.3 GAP-0.3-01 vs. autoridad normativa primaria y patrón CI Fase 6.
2. **Identidad inválida en workload (E-0.6-007):** `tests/corpus/workload/manifest.json` contiene un hash calculado con algoritmo no-autorizado y BOM UTF-8; es una identidad falsa que debe eliminarse.
3. **Hardware no representativo (E-0.6-006):** host envelope 31.83GB/12 CPUs vs target 16GB; accelerator envelope (GPU/VRAM) no ejercido por run_regression → N/A para este baseline.

**Hechos confirmados post-ejecución:**

4. **No-mutación verificada empíricamente (H-0.6-A CONFIRMADA):** snapshot pre=post `4cf031d1…edb90` en 3 repeticiones (HITO_0.7 E-0.7-001).
5. **Identidad del anchor verificada pre-ejecución (NADR-24 R11):** `anchor_manifest_hash = 727782fe…19f7d` coincide con el sello v3.9 (HITO_0.7).

**Veredicto:** F0-A midió sobre `tests/corpus/canonical` (perfil SMOKE) con checksums de no-mutación pre/post replicando el patrón CI. GAP-0.3-01 se reclasifica; GAP-0.3-02 (stress workload) permanece OPEN como única necesidad real de corpus separado.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Este HITO no ejecuta medición. Reconcilia documentación contra evidencia normativa y forense, y define condiciones de conformidad. La hipótesis de no-mutación en nuestra ejecución específica se cerró en HITO_0.7 con checksums pre/post.

### 2.2 Método forense
1. Cargar HITO_0.3 v1.3.0 y Charter §5.2/§5.8.
2. Verificar texto literal de NADR-24 R11, NADR-25 §7 y NADR-26 §5.1/§5.3/§5.4/§7 mediante grep normativo (autoridad primaria).
3. Inspeccionar workflows de CI y tests de contrato ([I4]) como corroboración operativa.
4. Inspeccionar superficie de escritura de `run_regression.py` ([I2], [I3]) y configurabilidad de DBs ([I1]).
5. Reconciliar Observed / Required / Decision según §9.3 de la metodología de HITOs.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `NADR-F17BIS-24/25/26` | R11; §7; §5.1 R2, §5.3 R11-R12, §5.4 R16-R19, §7 | 100% auditado (grep normativo) |
| `.github/workflows/` | `ci.yml`, `continuous-verification.yml` | 100% auditado (corroboración) |
| `tests/unit/test_cv_workflow_contract.py` | Tests de contrato de no-mutación | 100% auditado (corroboración) |
| `tools/evaluation/run_regression.py` | Superficie de imports/escritura | 100% auditado |
| `infra/db/connection.py` | Configurabilidad de rutas | 100% auditado |
| `infra/adapters/pdf_parser.py`, `apps/bootstrap/pipeline_factory.py` | Writes de extracción | 100% auditado |
| `tests/corpus/workload/` | Artefactos creados en intento previo | 100% auditado |
| `HITO_0.7` v1.0.0 | Evidencia empírica de no-mutación e identidad | Referenciado |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| NADR (autoridad primaria) | `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.3 R11-R12, §5.4 R16-R19, §7; `NADR-F17BIS-24` R11 | Mandato de ejecución sobre canonical sellado; inmutabilidad durante ejecución; consumo de solo lectura; verificación de identidad pre-run |
| Charter | `FASE0_AUDIT_CHARTER.md` §5.2, §5.8 | Medición permitida con writes efímeros; reuso de PDFs como carga |
| Workflow CI (corroboración) | `ci.yml:67-69`, `continuous-verification.yml:40-42` | Patrón operativo vigente |
| Test de contrato (corroboración) | `test_cv_workflow_contract.py:110,116,177` | Verificación de no-mutación como requisito gobernado |
| Código | `run_regression.py` (imports), `connection.py:9-65` | Superficie de escritura y configurabilidad |
| HITO previo | `HITO_0.3_F0-F` v1.3.0; `HITO_0.7` v1.0.0 | Documento reconciliado; evidencia empírica de cierre |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Medición sobre canonical | CI Fase 6 ejecuta run_regression sobre canonical en cada push; F0-A lo ejecutó con checksums pre/post | NADR-25 §7 manda ejecución contra corpus sellado; NADR-26 §5.4 R16-R19 restringe mutación durante ejecución; Charter §5.2/§5.8 permiten medición con writes efímeros | HITO_0.3 interpretó separación como bloqueo físico total | **DISCREPANCY RECONCILED (autoridad primaria verificada v1.1)** | E-0.6-008, E-0.6-001, E-0.6-002 |
| Superficie de escritura de run_regression | Solo `--output-dir`; sin imports de infra.db/telemetría; extracción sin cache en disco | Charter §5.2: efectos operacionales en entorno efímero | Ninguna | **COMPLIANT** | E-0.6-003, E-0.6-004 |
| Identidad del corpus pre-ejecución | `anchor_manifest_hash = 727782fe…19f7d` en baseline JSON | NADR-24 R11: verificar identidad contra declarada antes de ejecutar | Ninguna | **COMPLIANT** | E-0.6-009 |
| Identidad del workload manifest | Hash inventado en PowerShell + BOM UTF-8 | Toda identidad de baseline debe provenir de autoridad congelada (NADR-26 §5.2/§5.3); el esquema de identidad de workload está INDEFINIDO por gobernanza congelada | Ninguna | **DISCREPANCY (artefacto deprecado)** | E-0.6-007 |
| Host envelope | 31.83GB RAM / 12 CPUs | Target 16GB RAM | Ninguna | **DISCREPANCY DOCUMENTADA (limitación)** | E-0.6-006 |
| Accelerator envelope | GPU/VRAM no ejercidos por run_regression (sin providers ni GPU en el path medido) | Target 4GB VRAM aplica a cargas que usan acelerador | Ninguna | **N/A para este baseline** | E-0.6-006 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.6-001: CI Fase 6 ejecuta sobre canonical (corroboración operativa)
* **Archivo:** `.github/workflows/ci.yml:67-69`; `.github/workflows/continuous-verification.yml:40-42`
* **Observed:** `python -m tools.evaluation.run_regression --corpus-dir tests/corpus/canonical --pdf-dir tests/corpus/canonical/pdf`.
* **Hallazgo:** La ejecución read-only sobre el anchor sellado es práctica operativa vigente y gobernada. **Corroboración operativa; la autoridad primaria es E-0.6-008.**
* **Severidad:** P0

### Evidencia E-0.6-002: No-mutación es requisito de contrato (corroboración operativa)
* **Archivo:** `tests/unit/test_cv_workflow_contract.py:110,116,177`
* **Observed:** `test_regression_gates_verifies_corpus_mutation`, `..._oracle_mutation`, `test_cv_workflow_verifies_corpus_mutation`.
* **Hallazgo:** El patrón conforme es "ejecutar + verificar checksums pre/post", no "no ejecutar". **Corroboración; la autoridad primaria es NADR-26 R18 (E-0.6-008).**
* **Severidad:** P0

### Evidencia E-0.6-003: Superficie de escritura mínima
* **Archivo:** `tools/evaluation/run_regression.py` (imports L29-101)
* **Observed:** Sin imports de `infra.db` ni `core.telemetry`. Única escritura: `--output-dir`.
* **Severidad:** P1

### Evidencia E-0.6-004: Extracción sin cache en disco
* **Archivo:** `infra/adapters/pdf_parser.py`, `apps/bootstrap/pipeline_factory.py`
* **Observed:** Cero matches para patrones de escritura/cache. No hay writes colaterales.
* **Severidad:** P2

### Evidencia E-0.6-005: DBs configurables por env vars
* **Archivo:** `infra/db/connection.py:9,15-18,28,64`
* **Observed:** `APP_ROOT`, `FSM_DB_PATH`, `QUEUE_DB_PATH` resolubles por entorno. Aislamiento efímero disponible aunque no requerido por run_regression (E-0.6-003). En el wrapper v3-final se setearon defensivamente a directorio temporal.
* **Severidad:** P2

### Evidencia E-0.6-006: Envelopes de hardware (split host/accelerator)
* **Observed:** Host: 31.83GB RAM / 12 CPUs lógicos vs target 16GB RAM. Accelerator: GPU/VRAM no ejercidos por `run_regression.py` (no invoca providers ni usa GPU en el path medido).
* **Hallazgo:** El baseline F0-A vale como ancla comparativa pre/post-F18 en la misma máquina (Charter §5.5); prohíbe claims de conformidad del host envelope. El accelerator envelope es **N/A** para este baseline, no "non-conformant": no se declara falta de conformidad GPU cuando la medición no depende de GPU.
* **Severidad:** P1

### Evidencia E-0.6-007: Identidad inválida en workload manifest
* **Archivo:** `tests/corpus/workload/manifest.json`
* **Observed:** Hash calculado con algoritmo no-autorizado (concatenación PowerShell) y BOM UTF-8 que rompe el parser del proyecto.
* **Hallazgo:** Artefacto con identidad falsa; debe eliminarse para evitar confusión con oráculo. El esquema de identidad de un workload futuro está INDEFINIDO por gobernanza congelada y requerirá decisión (DC/NADR), no un HITO.
* **Severidad:** P1

### Evidencia E-0.6-008: Autoridad normativa primaria de lectura/ejecución read-only
* **Archivo:** `NADR-F17BIS-25` §7; `NADR-F17BIS-26` §5.1 R2, §5.3 R11-R12, §5.4 R16-R19, §7; `NADR-F17BIS-24` R11; `FASE0_AUDIT_CHARTER.md` §5.2, §5.8.
* **Observed:** NADR-25 §7: "Ejecución del verification entry point contra el corpus canónico sellado…". NADR-26 §5.1 R2: materialización física mandatada; §5.4 R16-R19: "Los artefactos de la baseline MUST permanecer inmutables durante una ejecución…"; "El entorno de ejecución MUST NOT modificar los artefactos canónicos… como efecto de la verificación"; "Una modificación detectada… MUST invalidar su utilización como referencia"; §7: "referencia de solo lectura durante la ejecución". NADR-26 §5.3 R11-R12: biyección inmutable (agregar/quitar PDFs). Charter §5.2: medición permitida con writes efímeros; §5.8: reuso de PDFs como carga permitido.
* **Hallazgo:** **No existe cláusula de no-lectura/no-ejecución.** La restricción es de mutación/sustitución/biyección; el consumo read-only está mandatado y reglado. Cierre de F18-0.6-01 con autoridad primaria congelada.
* **Severidad:** P0

### Evidencia E-0.6-009: Identidad del anchor verificada pre-ejecución
* **Archivo:** `reports/f0a_baseline/baseline_profile_20261002_014448.json` (`anchor_manifest_hash`); `NADR-F17BIS-24` R11.
* **Observed:** El hash del anchor reportado coincide con el sello v3.9 (`727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`).
* **Hallazgo:** El protocolo F0-A cumple NADR-24 R11 (identidad verificada contra declarada antes de ejecutar).
* **Severidad:** P1

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.3-01 (RECLASIFICADO)** | Separación física aplica a writes/sellado/aumento de stress, no a lectura read-only del anchor. Deja de ser BLOCKING para F0-A. | E-0.6-008, E-0.6-001, E-0.6-002 | NADR-25 §7, NADR-26 §5.4, Charter §5.2 | **Reconciliado en este HITO** | RECONCILED |
| **GAP-0.3-02 (persiste)** | Workload de stress (docs sintéticos) aún inexistente; única necesidad real de corpus separado. | HITO_0.3 | C10 | **Fase 18** | OPEN |
| **GAP-0.6-01** | Checksums de no-mutación pre/post sobre canonical. Implementados y verificados en HITO_0.7 v3-final (snapshot pre=post; mecanismo NADR-26 R18 operativo). | E-0.6-002, E-0.6-008; HITO_0.7 E-0.7-001 | Charter §5.2, NADR-26 R18 | **Cerrado por HITO_0.7** | CLOSED |
| **GAP-0.6-02** | `tests/corpus/workload/manifest.json` con identidad inválida debe eliminarse. Sin efecto sobre F0-A (el protocolo v3 ya no lo lee). | E-0.6-007 | Identity governance | **Cleanup pendiente de confirmación** | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.6-A | Una ejecución read-only de run_regression sobre canonical produce cero mutación en nuestro entorno. | **CONFIRMADA** | HITO_0.7 E-0.7-001: snapshot pre=post `4cf031d1…edb90` en 3 repeticiones | El patrón de medición es conforme en la práctica, no solo en diseño. |
| H-0.6-B | La superficie de escritura de run_regression se limita a `--output-dir`. | CONFIRMADA | E-0.6-003, E-0.6-004 | Output-dir efímero basta para Charter §5.2. |
| H-0.6-C | Las DBs operacionales son aislables por env vars. | CONFIRMADA (no requerida para run_regression; aplicada defensivamente en wrapper v3) | E-0.6-005, E-0.6-003 | Perímetro efímero completo. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Es conforme medir F0-A sobre canonical?
Sí, con autoridad primaria normativa (E-0.6-008) y condicionado a: (a) cero escrituras en canonical (diseño confirmado E-0.6-003/004 y verificado empíricamente en HITO_0.7), (b) `--output-dir` efímero, (c) checksums pre/post de manifest+PDFs+GTs replicando el patrón CI y el mecanismo NADR-26 R18 (implementados y verificados), (d) DB env vars apuntadas a temp defensivamente, (e) identidad del anchor verificada pre-ejecución (NADR-24 R11, cumplido).

### 16.2 ¿Qué ocurre con tests/corpus/workload?
Se elimina `manifest.json` (identidad inválida; eliminación pendiente de confirmación, GAP-0.6-02). Se conservan `pdf/` y `ground_truth/` como **seed sin identidad** para los stress docs futuros de GAP-0.3-02. Ningún documento de gobernanza los referencia como corpus con identidad; cualquier identidad futura de workload requiere decisión gobernada (DC/NADR), no un HITO.

### 16.3 ¿Qué puede afirmar F0-A dado el hardware?
Host envelope (31.83GB/12 CPUs): solo comparación relativa pre/post-F18 en la misma máquina; cero claims de conformidad con 16GB. Accelerator envelope (4GB VRAM): **N/A** para este baseline porque run_regression no ejerce GPU ni providers. Las métricas de traducción/provider quedan como Deferred Question (run_regression no invoca providers).

---

## 21. CIERRE DEL HITO 0.6

**Estado del HITO:** FROZEN v1.1.0
**Condición de cierre cumplida:** Contradicción con HITO_0.3 documentada, evidenciada y reconciliada según §9.3 con autoridad primaria normativa verificada textualmente; H-0.6-A cerrada con evidencia empírica; gaps con destino explícito; envelopes separados.
**Verificación de cadena de gobernanza:** NADR-24 R11 / NADR-25 §7 / NADR-26 §5.1/§5.3/§5.4/§7 → Charter §5.2/§5.8 → HITO_0.3 v1.3.0 → este HITO v1.0.0 → HITO_0.7 v1.0.0 → esta v1.1.0.
**Contradicciones con HITOs previos:** Una, reconciliada aquí (HITO_0.3 GAP-0.3-01), ahora con autoridad primaria además de corroboración operativa.
**Decision Candidates generados:** Ninguno nuevo; alimenta DC-01/DC-03/DC-07 vía HITO_0.7.
**Siguiente paso recomendado:** Emitir HITO_0.7 v1.1.0 (reconciliación epistémica: tres planos de veredicto, repetibilidad-bajo-régimen ≠ INV-SCI-1, 0/6 técnicas calibradas, δ/MDE/Δ/ε abiertos, perímetro del árbol reproducible, ΔNSS como hipótesis causal); luego F0-B.