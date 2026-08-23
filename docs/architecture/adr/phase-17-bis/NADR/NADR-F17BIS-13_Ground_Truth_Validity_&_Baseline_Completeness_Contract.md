# NADR-F17BIS-13: Ground Truth Validity & Baseline Completeness Contract

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-13`
* **Título:** Contrato de Validez del Oráculo y Completitud Biyectiva de la Baseline
* **Clase de Decisión:** `DATA` / `OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS (Fase 2 — Scientific Baseline Domain)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Domain / Core Arch
* **Capacidad Arquitectónica:** CAP-011 (Ground Truth Validity & Baseline Completeness) — invariantes que certifican un oráculo como válido y la correspondencia biyectiva del corpus.
* **Evidencia Forense:** `E-2.0-01`, `E-2.0-07`, `OBS-2.0-07`, `OBS-2.0-08`, `GAP-2.0-03`, `GAP-2.0-07`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-12` (la completitud opera sobre entidades con estado), `NADR-F17BIS-01` (la validación estructural consume la representación canónica).
  * **Influencia:** `NADR-F17BIS-14` (la autoridad de sellado exige estas invariantes antes de sellar), `NADR-F17BIS-15` (un oráculo válido es precondition para portar identidad semántica).
  * **Conflictúa con:** Todo sellado que omita oráculos ausentes, que congele contenido no validado, o que degrade la completitud a advertencias no bloqueantes.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE
* **Operacional:** 5 — El sellado parcial permite certificar como completa una baseline que no lo es; la firma resultante no refleja la verdad científica real.
* **Mantenibilidad:** 3 — La ausencia de un contrato de validez obliga a cada consumidor a redefinir qué es un oráculo válido.
* **Recuperabilidad:** 4 — Sin validación estructural previa al sello, la corrupción se congela y solo se detecta en etapas tardías.
* **Seguridad:** 2 — El riesgo es de integridad de la baseline, no de superficie externa.
* **Financiero:** 2 — Una baseline incompleta invalida campañas de certificación y fuerza re-ejecuciones.
* **Total Score: 16/25**

**Severidad:** `S1`

---

## 3. DECISIÓN EJECUTIVA

**Un oráculo solo puede ser sellado si satisface un contrato explícito de validez estructural, y una baseline solo puede existir si mantiene una correspondencia biyectiva completa y verificada entre los documentos fuente declarados y sus oráculos, en ambas direcciones.**

En consecuencia:
* Queda prohibido sellar un oráculo cuya estructura no haya sido validada contra las invariantes de dominio.
* Queda prohibido sellar una baseline cuando existe algún documento fuente sin oráculo, o algún oráculo sin documento fuente declarado.
* La ausencia de un oráculo **MUST** abortar el sellado; no puede degradarse a advertencia.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de certificar la validez de un oráculo y la completitud de la baseline está ausente. El sellado opera sobre la mera existencia de artefactos, sin validación estructural y sin verificación de correspondencia. Se identifican las siguientes clases de defecto:

1. **Sellado sin validación:** se congela contenido cuya validez estructural jamás fue verificada.
2. **Sellado parcial:** la ausencia de un oráculo se omite silenciosamente, produciendo una baseline incompleta certificada como completa.
3. **Biyección no verificada en ambas direcciones:** se ignora tanto la falta de oráculos como la presencia de oráculos huérfanos.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-2.0-01` / `GAP-2.0-07` (P0 — Crítico):** `core/benchmark/ground_truth/use_cases.py::SealGroundTruthUseCase.execute` evalúa `if self._artifact_port.artifact_exists(doc_id):` sin rama `else`; un oráculo ausente se omite silenciosamente y el manifiesto se sella con $N_{GT} < N_{PDF}$. Verifica `E-0.2-001` de Fase 0.
* **`E-2.0-07` / `GAP-2.0-03` (P0 — Crítico):** `SealGroundTruthUseCase` lee `read_artifact_bytes(doc_id)` y computa un hash sobre bytes crudos sin hidratar ni validar estructuralmente el contenido antes de congelarlo. Verifica `E-0.2-005` de Fase 0.
* **`OBS-2.0-07` (P1 — Alto):** Ningún componente verifica la biyección inversa: artefactos de Ground Truth presentes en disco pero ausentes del manifiesto son ignorados durante el sellado.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Validez estructural del oráculo
1. Todo oráculo **MUST** satisfacer un contrato explícito de validez estructural antes de poder ser sellado.
2. El contrato de validez **MUST** incluir, como mínimo, la no-vaciedad del contenido, la integridad de los nodos y la coherencia de su estructura.
3. El sellado **MUST** rechazar de forma explícita e inmediata todo oráculo que no satisfaga el contrato de validez.

### 5.2 Completitud biyectiva (Zero Partial Sealing)
4. Una baseline **MUST** mantener una correspondencia biyectiva completa entre los documentos fuente declarados y sus oráculos.
5. La completitud **MUST** ser verificada en ambas direcciones: todo documento fuente **MUST** tener un oráculo, y todo oráculo **MUST** corresponder a un documento fuente declarado.
6. La ausencia de un oráculo para un documento fuente declarado **MUST** abortar el sellado mediante un fallo explícito.
7. La presencia de un oráculo sin documento fuente declarado **MUST** ser detectada y abortar el sellado.
8. El sellado **MUST NOT** degradar la incompletitud a advertencias no bloqueantes ni continuar el proceso emitiendo avisos.

### 5.3 Atomicidad del sellado
9. El sellado **MUST** ser una operación atómica: o bien se certifica la baseline completa y válida, o bien no se certifica nada.
10. Un sellado abortado **MUST NOT** dejar una baseline parcialmente certificada ni un manifiesto en estado inconsistente.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La baseline certificada refleja fielmente la verdad científica completa; las mutaciones u omisiones de oráculos son detectables.
* El sellado parcial queda erradicado: una baseline incompleta no puede entrar en estado sellado.
* La corrupción estructural no puede ser congelada: todo oráculo es validado antes del sello.
* El invariante *Zero Partial Sealing* del ADR Maestro §5 queda materializado como propiedad verificable del dominio.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el camino de sellado invoca la validación estructural antes de congelar.
  * Verificación de que el sellado posee una comprobación de biyección en ambas direcciones.
  * Property-based testing sobre la atomicidad: ningún estado intermedio de sellado produce una baseline parcial.
* **Validation (dinámica/comportamental):**
  * Sellar una baseline con un oráculo ausente **MUST** abortar con fallo explícito.
  * Sellar una baseline con un oráculo huérfano **MUST** abortar.
  * Sellar un oráculo estructuralmente inválido **MUST** ser rechazado.
  * Sellar una baseline completa y válida **MUST** producir un estado sellado consistente.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el invariante *Zero Partial Sealing* (§5) y el requisito de completitud de la baseline. |
| `ADR_F17_BIS_02` | **Dependencia directa:** materializa el Principio de Completitud Biyectiva declarado por el ADR de Fase. |
| `NADR-F17BIS-12` | **Dependencia directa:** la completitud opera sobre entidades con estado de ciclo de vida. |
| `NADR-F17BIS-01` | **Dependencia directa:** la validación estructural consume la representación canónica del AST. |
| `NADR-F17BIS-14` | **Influencia:** la autoridad de sellado exige estas invariantes como precondición del sello. |
| `NADR-F17BIS-15` | **Influencia:** un oráculo válido es precondición para portar identidad semántica. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas de Fase 2 materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** los estados del ciclo de vida ni su autoridad de transición (responsabilidad de `NADR-F17BIS-12`).
* **No gobierna** la segregación de superficies de acceso ni la identidad de la autoridad de sellado (responsabilidad de `NADR-F17BIS-14`).
* **No gobierna** la fórmula de la firma semántica ni el encadenamiento global de la baseline (responsabilidad de `NADR-F17BIS-03` y de la Fase 3).
* **No gobierna** la evaluación topológica ni la semántica de regresión (responsabilidad de la Fase 4).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.