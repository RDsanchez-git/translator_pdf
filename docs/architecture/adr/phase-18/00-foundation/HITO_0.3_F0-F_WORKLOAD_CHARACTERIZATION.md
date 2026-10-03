# HITO_0.3_F0-F_WORKLOAD_CHARACTERIZATION.md

**Estado:** FROZEN v1.3.0
**Fecha de emisión:** 2026-10-02
**Fecha de congelamiento:** 2026-10-02
**Fase:** 18 — Advanced Local Runtime (Fase 0: Auditoría)
**Tipo de artefacto:** Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** `core/benchmark/verification/profiles.py`, `core/benchmark/corpus/models.py`, `core/benchmark/ground_truth/models.py`, `NADR-F17BIS-26`, `FASE0_AUDIT_CHARTER.md` §5.8, `FASE_6_HANDOFF.md` §5.1, `HITO_0.1_F0-B`, `HITO_0.2_F0-G`
**Mandato:** Definir el corpus de carga versionado que servirá como *anchor* para las mediciones de F0-A (Runtime Profile Baseline), sin violar la biyección ni el sellado del corpus canónico v3.9.
**Síntesis:** Se establece la necesidad de un workload corpus con identidad versionada propia, separado físicamente del oráculo científico. La composición exacta (número de documentos, tipo de estrés) queda como candidate workload composition pendiente de caracterización cuantitativa en F0-A.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-10-02 | Emisión inicial basada en auditoría de perfiles de verificación. |
| 1.1.0-FROZEN | 2026-10-02 | Cierre formal tras reconciliación de identidad y representatividad. |
| 1.2.0-FROZEN | 2026-10-02 | Corrección de E-0.3-001 (precisión forense: riesgo normativo, no criptográfico). Adición de secciones 11, 18, 19. |
| 1.3.0-FROZEN | 2026-10-02 | Reconciliación epistemológica: H-0.3-A/H-0.3-B rebajadas a NO DEMOSTRADA; separación workload corpus/profile/protocol; "5+2" rebajado a candidate composition; eliminación de implementation prescription. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la estructura del corpus canónico v3.9 y los perfiles de verificación (FULL/SMOKE) para definir un workload corpus que sirva como anchor de medición de runtime, sin violar las invariantes de sellado (NADR-26) ni la biyección manifiesto↔PDFs.

**Hallazgo central:**

> El workload corpus de Fase 18 debe ser un artefacto **separado y versionado independientemente** del oráculo científico sellado, reutilizando PDFs del corpus canónico como carga física pero sin tocar el manifiesto v3.9 ni los oráculos AST, cumpliendo §5.8 del Charter. La composición exacta del workload (número de documentos, tipo de estrés) queda como candidate workload composition pendiente de caracterización cuantitativa en F0-A.

**Hechos observados confirmados:**

1. **Separación normativa workload/oráculo (E-0.3-001):** Cualquier modificación de archivos en `tests/corpus/canonical/` durante la medición de runtime viola la inmutabilidad del sellado (NADR-26).
2. **Ausencia de workload de estrés (E-0.3-002):** Los 21 docs canónicos no fueron diseñados como stress workloads; existe necesidad justificada de ampliar el workload con escenarios de estrés, pero la cardinalidad y composición exactas no están demostradas.
3. **Ausencia de mecanismo de identidad para workload (E-0.3-003):** No existe un `WorkloadManifestCalculator` que genere identidad versionada sin oracle hashes.

**Veredicto:** Se requiere un workload corpus propio con identidad versionada, separado físicamente del oráculo científico. La composición exacta (número de documentos SMOKE, número de documentos de estrés, tipo de estrés) queda como candidate workload composition pendiente de caracterización cuantitativa en F0-A.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico
Este HITO es read-only. No define el contenido exacto de los documentos de estrés (eso es tarea de caracterización cuantitativa en F0-A). No prescribe implementación de `WorkloadManifestCalculator`. Solo establece el contrato de separación normativa, ubicación física y necesidad de identidad versionada propia.

### 2.2 Método forense
1. Cargar fuentes normativas (`NADR-F17BIS-26`, `FASE0_AUDIT_CHARTER.md` §5.8, `FASE_6_HANDOFF.md` §5.1).
2. Inspeccionar `core/benchmark/verification/profiles.py` para identificar los 5 docs SMOKE.
3. Verificar que la ubicación propuesta (`tests/corpus/workload/`) no colisiona con `tests/corpus/canonical/`.
4. Separar Observed (estructura actual) / Required (invariantes de sellado) / Decision (separación de workload).
5. Registrar evidencia estable con IDs y severidad.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/benchmark/verification/` | `profiles.py` | 100% Auditado |
| `core/benchmark/corpus/` | `models.py`, `integrity.py` | 100% Auditado |
| `tests/corpus/` | Estructura de directorios | 100% Auditado |
| `FASE_6_HANDOFF.md` | §5.1 (Active Constraints) | Referenciado |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| Código | `core/benchmark/verification/profiles.py` | Observación de perfil SMOKE (5 docs hardcoded) |
| NADR | `NADR-F17BIS-26` §5.3 R11-R12 | Required: Biyección manifiesto↔PDFs inmutable |
| Charter | `FASE0_AUDIT_CHARTER.md` §5.8 | Required: Workload corpus con identidad versionada propia |
| Handoff | `FASE_6_HANDOFF.md` §5.1 | Required: No tocar baseline sellada |

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| Corpus Canónico v3.9 | `tests/corpus/canonical/manifest.json` | Sí (oráculo científico) | 21 docs sellados, hash `727782fe...19f7d` | CONFIRMADO |
| Perfil SMOKE | `core/benchmark/verification/profiles.py::get_profile_document_ids("SMOKE")` | Sí (subset de verificación) | 5 docs hardcoded (doc_01, doc_03, doc_07, doc_11, doc_14) | CONFIRMADO |
| Perfil FULL | `core/benchmark/verification/profiles.py::get_profile_document_ids("FULL")` | Sí (verificación completa) | 21 docs (todos los del canónico) | CONFIRMADO |
| Workload Corpus (propuesto) | `tests/corpus/workload/manifest.json` (no existe aún) | No (a definir en F18) | Candidate: subset SMOKE + docs de estrés | MISSING |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-0.3-001: Riesgo de contaminación normativa del oráculo
* **Archivo Fuente Primario:** `core/benchmark/corpus/integrity.py`
* **Símbolo Auditado:** `verify_manifest_hash`, `verify_pdf_hash`
* **Declaración Observada:** Las funciones de integridad calculan SHA-256 sobre los PDFs y el manifiesto, comparando contra hashes sellados.
* **Observed:** Los hashes SHA-256 se calculan sobre el contenido binario de los archivos, no sobre timestamps ni metadata del sistema de archivos. Modificar timestamps no invalida los hashes. Sin embargo, cualquier modificación de archivos en `tests/corpus/canonical/` viola el principio de inmutabilidad de la baseline sellada (NADR-26 §5.3 R11-R12).
* **Required:** NADR-26 §5.3 R11-R12 exige biyección inmutable; `FASE_6_HANDOFF.md` §5.1 prohíbe tocar la baseline sellada.
* **Hallazgo Forense:** Medir runtime sobre el corpus canónico viola el principio de separación entre workload de carga y oráculo científico. El riesgo es de gobernanza normativa, no de invalidación criptográfica.
* **Consecuencia Arquitectónica:** Requiere un workload corpus separado físicamente para preservar la inmutabilidad normativa del oráculo.
* **Estado:** OPEN
* **Severidad:** P0

### Evidencia E-0.3-002: Ausencia de workload de estrés
* **Archivo Fuente Primario:** `core/benchmark/verification/profiles.py`
* **Símbolo Auditado:** `get_profile_document_ids`
* **Declaración Observada:** El perfil SMOKE contiene 5 docs hardcoded; el perfil FULL contiene los 21 docs canónicos.
* **Observed:** Los 21 docs canónicos no fueron diseñados como stress workloads. No hay evidencia forense de que ejerciten paths de CPU intensivo (tablas anidadas de 50+ celdas, ecuaciones LaTeX de 100+ líneas, figuras de alta resolución).
* **Required:** C10 (Local Resource Efficiency) del Charter exige medición bajo recursos finitos (16GB RAM).
* **Hallazgo Forense:** **FACT:** Existe necesidad justificada de ampliar el workload con escenarios de estrés. **INFERENCE:** Los 21 docs canónicos probablemente no cubren suficientemente determinados perfiles de presión. **NO DEMOSTRADO:** La cardinalidad exacta (cuántos documentos de estrés), el tipo de estrés (tablas 50+, ecuaciones 100+), si el estrés debe ser sintético o real, o si 16GB es el límite relevante.
* **Consecuencia Arquitectónica:** F0-A debe caracterizar cuantitativamente el workload de estrés necesario.
* **Estado:** OPEN (necesidad justificada; composición exacta pendiente de F0-A)
* **Severidad:** P1

### Evidencia E-0.3-003: Identidad versionada del workload
* **Archivo Fuente Primario:** `core/benchmark/corpus/models.py`
* **Símbolo Auditado:** `CorpusManifest`, `ManifestFingerprintCalculator`
* **Declaración Observada:** El manifiesto canónico usa `ManifestFingerprintCalculator.compute_hash()` para generar un hash global (SHA-256) que incluye hashes de PDFs, oracle hashes, ground truth state, corpus version.
* **Observed:** El workload corpus necesita un mecanismo de identidad similar, pero **sin** oracle hashes ni ground truth state (no es oráculo científico).
* **Required:** `FASE0_AUDIT_CHARTER.md` §5.8 exige "manifiesto e identidad versionada propios, **nunca sellado como oráculo**".
* **Hallazgo Forense:** El workload corpus debe tener su propio manifiesto con hash propio, calculado solo sobre los PDFs de carga (sin oracle hashes). La fórmula exacta del hash queda como decisión pendiente (DC-02).
* **Consecuencia Arquitectónica:** Requiere un mecanismo de identidad para workload (candidate: `WorkloadManifestCalculator` simplificado o reutilización de `ManifestFingerprintCalculator` con campos opcionales en `None`).
* **Estado:** OPEN
* **Severidad:** P1

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-0.3-01 | Los 5 docs SMOKE (doc_01, doc_03, doc_07, doc_11, doc_14) fueron seleccionados en Fase 6 por cobertura de traits, no por representatividad estadística del workload. | Medio | OPEN |
| OBS-0.3-02 | La copia física de PDFs de `canonical/pdf/` a `workload/pdf/` duplica espacio en disco (~50MB estimados). Considerar symlinks si el sistema de archivos lo soporta (optimization candidate / implementation detail; no parte del diseño del workload). | Bajo | OPEN |

---

## 12. MATRIZ DE TRIAJE

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `tests/corpus/canonical/` | RETAIN | Oráculo científico sellado; no se modifica. |
| `tests/corpus/archive/` | RETAIN | PDFs huérfanos documentados (DF-08); no se toca. |
| `tests/corpus/workload/` (propuesto) | MISSING | Requiere creación en F18 con manifiesto propio. |
| `core/benchmark/verification/profiles.py` | RETAIN | Define los 5 docs SMOKE; candidate como base del workload. |
| `ManifestFingerprintCalculator` | REFACTOR (parcial) | Candidate para reutilización del patrón, simplificado para workload (sin oracle hashes). |

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.3-01** | Ausencia de workload corpus separado físicamente del oráculo científico. | E-0.3-001 | NADR-26, Charter §5.8 | **Fase 18** | OPEN |
| **GAP-0.3-02** | Ausencia de workload de estrés; necesidad justificada pero composición exacta pendiente de F0-A. | E-0.3-002 | C10, Charter §3 | **Fase 18** (F0-A) | OPEN |
| **GAP-0.3-03** | Ausencia de mecanismo de identidad versionada para workload (sin oracle hashes). | E-0.3-003 | Charter §5.8 | **Fase 18** (DC-02) | OPEN |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-0.3-A | Los 5 docs SMOKE son representativos del workload canónico. | NO DEMOSTRADA | E-0.3-002 muestra que fueron seleccionados por cobertura de traits, no por representatividad estadística. OBS-0.3-01 lo confirma. | Los 5 docs SMOKE son adecuados como subset funcional de cobertura, pero no están demostrados como workload representativo. F0-A debe validar representatividad. |
| H-0.3-B | Se requieren exactamente 2 docs sintéticos de estrés para validar C10. | NO DEMOSTRADA (cardinalidad); necesidad de stress sí sustentada | E-0.3-002 justifica necesidad de ampliar workload, pero no demuestra cardinalidad exacta, tipo de estrés, o si debe ser sintético. | F0-A debe caracterizar cuantitativamente el workload de estrés necesario (número, tipo, sintético vs real). |
| H-0.3-C | El workload corpus puede ubicarse en `tests/corpus/workload/` sin colisionar con `canonical/`. | CONFIRMADA | E-0.3-001 | Separación física garantiza no contaminación normativa. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Qué documentos componen el workload corpus?

**Estado actual verificado:**

1. El perfil SMOKE contiene 5 docs hardcoded: `doc_01`, `doc_03`, `doc_07`, `doc_11`, `doc_14` (E-0.3-002).
2. Los 21 docs canónicos no fueron diseñados como stress workloads (E-0.3-002).

**Respuesta forense:**

El workload corpus debe componerse de:
- **Subset SMOKE como base candidate:** Los 5 docs SMOKE son adecuados como subset funcional de cobertura, pero su representatividad como workload debe validarse en F0-A.
- **Documentos de estrés (pendiente de F0-A):** F0-A debe caracterizar cuantitativamente el workload de estrés necesario (número de documentos, tipo de estrés, sintético vs real).

**Candidate workload composition (no decisión cerrada):**

- 5 documentos reutilizados del canónico (doc_01, doc_03, doc_07, doc_11, doc_14), copiados físicamente a `tests/corpus/workload/pdf/`.
- Documentos de estrés adicionales (número y tipo pendientes de F0-A).

**Implicación:**

F0-A debe validar la representatividad del subset SMOKE y caracterizar el workload de estrés necesario. La composición exacta queda como candidate workload composition.

### 16.2 ¿Cómo se calcula la identidad del workload corpus?

**Estado actual verificado:**

1. `ManifestFingerprintCalculator` calcula hash global incluyendo oracle hashes y ground truth state (E-0.3-003).
2. El workload corpus no tiene oráculos AST ni ground truth (no es oráculo científico).

**Respuesta forense:**

El workload corpus debe tener identidad versionada propia, calculada sin oracle hashes ni ground truth state. La fórmula exacta queda como decisión pendiente (DC-02).

**Candidate workload identity (no decisión cerrada):**

```python
workload_hash = SHA-256(
    sorted([SHA-256(pdf_bytes) for pdf in workload_pdfs]) +
    corpus_version +
    workload_metadata  # ej. "stress_docs=N"
)
```

**Nota:** `workload_metadata` podría introducir semántica operacional en identidad física. La distinción conceptual entre WorkloadInputIdentity, WorkloadProfileIdentity y WorkloadExecutionIdentity debe establecerse antes de congelar el contrato (DC-02).

**Implicación:**

DC-02 debe resolver la fórmula exacta de identidad del workload corpus, considerando la separación entre identidad física de inputs, perfil de carga y protocolo de ejecución.

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-02** | Parámetros de runtime en identity científica vs metadata operacional | E-0.3-003 | Ausente: fórmula de identidad de workload no definida | **Fase 18** (precondición para definir workload identity) |
| **DC-07** | Tiers 8k/32k/1M o batch = f(budgets) | E-0.3-002 | Ausente: no hay workload de estrés caracterizado | **Fase 18** (requiere F0-A) |
| **DC-10** | Fairness y admission deadlock-free | E-0.3-001, E-0.3-002 | Ausente: no hay workload para probar admisión | **Fase 18** (requiere workload corpus) |

---

## 19. APÉNDICE NO NORMATIVO -- RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Contaminación normativa del oráculo | Si el workload corpus se aloja en `tests/corpus/canonical/`, viola NADR-26 (inmutabilidad de baseline). | Alto (invalida CV) | E-0.3-001 |
| Workload insuficiente | Si el workload no ejerce suficiente presión, F0-A no revelará cuellos de botella reales. | Medio | E-0.3-002, H-0.3-B |
| Duplicación de PDFs | Copiar físicamente los PDFs duplica espacio en disco. Optimization candidate: symlinks (OBS-0.3-02). | Bajo | OBS-0.3-02 |
| Composición de workload incorrecta | Si la composición exacta (5+2) no es la óptima, F0-A puede requerir re-caracterización. | Medio | H-0.3-B |

---

## 21. CIERRE DEL HITO 0.3

Este HITO confirma que el workload corpus de Fase 18 debe ser un artefacto separado físicamente del oráculo científico, con identidad versionada propia. La composición exacta (número de documentos SMOKE, número de documentos de estrés, tipo de estrés) queda como candidate workload composition pendiente de caracterización cuantitativa en F0-A.

**Estado del HITO:** FROZEN v1.3.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados, todas las evidencias tienen ID estable y severidad, todos los gaps tienen fase destino explícita (Fase 18 / F0-A), hipótesis H-0.3-A/H-0.3-B rebajadas a NO DEMOSTRADA, H-0.3-C confirmada, separación workload corpus/profile/protocol establecida, eliminación de implementation prescription.
**Verificación de cadena de gobernanza:** Alineado con `NADR-F17BIS-26` (biyección inmutable), `FASE0_AUDIT_CHARTER.md` §5.8 (workload con identidad propia), `FASE_6_HANDOFF.md` §5.1 (no tocar baseline sellada).
**Contradicciones con HITOs previos:** Ninguna.
**Decision Candidates generados:** DC-02 (precondición para workload identity), DC-07 (evidencia de entrada), DC-10 (evidencia de entrada).
**Siguiente paso recomendado:** Consumir este HITO como evidencia de discovery para `ADR_F18_MASTER` §2 (Problema Arquitectónico). La composición exacta del workload queda pendiente de F0-A.