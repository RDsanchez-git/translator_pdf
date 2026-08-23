# NADR-F17BIS-14: Curation/Runtime Port Asymmetry & Sealing Authority

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-14`
* **Título:** Asimetría de Puertos de Curaduría/Runtime y Autoridad Única de Sellado
* **Clase de Decisión:** `STRUCTURAL` / `OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS (Fase 2 — Scientific Baseline Domain)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-012 (Curation/Runtime Port Asymmetry & Sealing Authority) — segregación de superficies de acceso y autoridad única de certificación.
* **Evidencia Forense:** `E-2.0-03`, `E-2.0-09`, `E-2.0-15`, `E-2.0-17`, `E-2.0-18`, `GAP-2.0-04`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-11` (frontera hexagonal y composición), `NADR-F17BIS-12` (la autoridad gobierna transiciones de ciclo de vida), `NADR-F17BIS-13` (el sellado exige validez y completitud).
  * **Influencia:** Los entry points de curaduría y los consumidores de runtime de la baseline.
  * **Conflictúa con:** Todo puerto que unifique lectura y escritura de la baseline; toda duplicación de autoridad de sellado; todo sellado ejecutable desde múltiples rutas no gobernadas.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE
* **Operacional:** 4 — Una superficie de escritura que alcanza la de lectura permite que la curaduría corrompa el oráculo consumido en runtime.
* **Mantenibilidad:** 5 — Puertos que mezclan lectura y escritura ocultan el grafo real de responsabilidades y acoplan consumidores a capacidades que no necesitan.
* **Recuperabilidad:** 3 — Con autoridad de sellado duplicada o ambigua, no es posible auditar quién certificó una baseline ni revertir un sello incorrecto.
* **Seguridad:** 3 — La superficie de curaduría sin segregar expone la baseline a escrituras no autorizadas.
* **Financiero:** 2 — Impacto acotado al laboratorio de certificación.
* **Total Score: 17/25**

**Severidad:** `S1`

---

## 3. DECISIÓN EJECUTIVA

**Las superficies de acceso a la baseline están segregadas en puertos asimétricos de curaduría y de runtime, y la certificación de un oráculo o de una baseline es gobernada por una única autoridad de sellado que aplica las invariantes de validez y completitud antes de emitir el sello.**

En consecuencia:
* Queda prohibido unificar en un mismo contrato las operaciones de escritura de curaduría y las de lectura de runtime.
* Queda prohibida la coexistencia de múltiples autoridades de sellado con lógica duplicada o divergente.
* Ningún punto de entrada puede ejecutar el sellado eludiendo la autoridad designada.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de segregar el acceso a la baseline y de centralizar su certificación está ausente o degradada. Se identifican las siguientes clases de defecto:

1. **Puerto mixto:** lectura y escritura de la baseline comparten un único contrato, rompiendo la asimetría exigida entre curaduría y runtime.
2. **Autoridad de sellado duplicada:** coexisten servicios con lógica de linaje idéntica, generando ambigüedad de responsabilidad.
3. **Superficie de curaduría no gobernada:** los puntos de entrada de evaluación construyen el sellado al margen de una raíz de composición y degradan los fallos a advertencias.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-2.0-09` / `GAP-2.0-04` (P1 — Alto):** `core/benchmark/corpus/ports.py::CorpusManifestLoaderPort` declara `load_raw_manifest()` y `save_manifest_dto()` en el mismo Protocol, unificando lectura y escritura.
* **`E-2.0-03` (P1 — Alto):** `core/benchmark/ground_truth/services.py::ManifestGroundTruthUpdater.apply_lineage_sealing` es idéntico línea por línea a `core/benchmark/corpus/services.py::ManifestLineageSealer.seal_manifest_with_ground_truth`; el primero tiene cero llamadores. Verifica `E-0.2-004` de Fase 0.
* **`E-2.0-15` / `E-2.0-17` / `E-2.0-18` (P1 — Alto):** `tools/evaluation/bootstrap_corpus.py` y `tools/evaluation/freeze_ground_truth.py` componen el flujo inline al margen de la raíz de composición; `freeze_ground_truth.py` hardcodea la versión objetivo y `generate_golden_draft.py` degrada un fallo de ausencia a advertencia y continúa.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Asimetría de puertos
1. Las operaciones de curaduría (escritura) y las operaciones de runtime (lectura) sobre la baseline **MUST** estar expuestas a través de contratos de acceso distintos.
2. Un contrato de lectura de runtime **MUST NOT** exponer capacidad de escritura ni de mutación de la baseline.
3. Un contrato de curaduría **MUST NOT** ser consumido por los caminos de runtime que leen la baseline certificada.

### 5.2 Autoridad única de sellado
4. La certificación de un oráculo o de una baseline **MUST** estar gobernada por una única autoridad de sellado.
5. **MUST NOT** coexistir múltiples autoridades de sellado con lógica duplicada o divergente.
6. Toda operación de sellado **MUST** delegar en la autoridad única; **MUST NOT** existir rutas alternativas que ejecuten el sello eludiéndola.

### 5.3 Superficie de curaduría gobernada
7. Todo punto de entrada que ejecute curaduría o sellado **MUST** componer sus dependencias conforme a la raíz de composición establecida.
8. Los fallos de integridad durante la curaduría o el sellado **MUST** propagarse como errores explícitos; **MUST NOT** degradarse a advertencias que permitan continuar.
9. Los parámetros que determinan la identidad de la baseline (por ejemplo, la versión objetivo del sello) **MUST NOT** quedar fijados implícitamente en un punto de entrada; **MUST** ser provistos de forma explícita.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El camino de runtime que lee la baseline queda aislado de cualquier operación de curaduría.
* La autoridad de sellado es unívoca y auditable; la ambigüedad de responsabilidad queda eliminada.
* Los entry points de curaduría operan bajo la misma gobernanza de composición y fail-fast que el resto del sistema.
* La duplicación de lógica de linaje queda erradicada.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Análisis de contratos que confirme la separación entre puertos de lectura y de escritura de la baseline.
  * Verificación estática de que existe una única autoridad de sellado y de que no hay lógica de linaje duplicada.
  * Contrato de análisis de imports que impida a los caminos de runtime consumir superficies de curaduría.
* **Validation (dinámica/comportamental):**
  * Ejecutar el sellado desde un punto de entrada y verificar que delega en la autoridad única.
  * Verificar que un fallo de integridad durante el sellado aborta la operación y no continúa.
  * Verificar que el camino de lectura de runtime no puede invocar operaciones de escritura.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio de Reutilización Estricta y la segregación de responsabilidades de la baseline. |
| `ADR_F17_BIS_02` | **Dependencia directa:** materializa la separación Write/Curator vs Read/Oracle declarada por el ADR de Fase. |
| `NADR-F17BIS-11` | **Dependencia directa:** la composición de entry points se rige por la frontera hexagonal y la raíz de composición. |
| `NADR-F17BIS-12` | **Dependencia directa:** la autoridad de sellado gobierna las transiciones del ciclo de vida. |
| `NADR-F17BIS-13` | **Dependencia directa:** el sellado exige las invariantes de validez y completitud como precondición. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas de Fase 2 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** los estados del ciclo de vida ni su semántica (responsabilidad de `NADR-F17BIS-12`).
* **No gobierna** las invariantes de validez ni la completitud biyectiva (responsabilidad de `NADR-F17BIS-13`).
* **No gobierna** las identidades que porta el oráculo (responsabilidad de `NADR-F17BIS-15`).
* **No gobierna** el mecanismo de encadenamiento criptográfico global (responsabilidad de la Fase 3).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.