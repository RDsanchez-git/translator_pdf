# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17_BIS_02: Scientific Baseline Domain — Formalización Ontológica del Oráculo

* **Estado:** DRAFT
* **Versión:** 1.0.0
* **Fecha de Emisión:** 2026-08-22
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** 17-BIS (Scientific Baseline / Canonical Corpus)
* **Evidencia Forense Vinculante:** HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY v2.1.0 (E-2.0-01..18, GAP-2.0-01..12, OBS-2.0-01..12); HITO_0.2 (E-0.2-001..007); HITO_0.3 (taxonomía tridimensional de identidad); FASE_1_DEFERRED_FINDINGS_REGISTER (DF-01-C, DF-01-D).
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER.md` (ADR Maestro), `ADR_F17_BIS_01.md` (Production Pipeline Alignment).
  * **Implementado por:** Serie normativa de NADRs de Fase 2 (a promulgar), que gobernarán: ontología del oráculo y ciclo de vida; contrato de validez y completitud; asimetría de puertos y autoridad de sellado; identidad semántica en el modelo de baseline.
  * **Ejecutado por:** `PHASE_17BIS_EXECUTION_PLAN.md` (tareas de Fase 2 a secuenciar).
  * **Conflictúa con:** Ninguno.

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 17-BIS, conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para esta subfase.

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 1 (Production Pipeline Alignment) concluyó con el pipeline de producción alineado a los NADRs normativos, pero no abordó el dominio de la baseline científica. El Discovery forense de Fase 2 (HITO_2.0) auditó el 100% de `core/benchmark/corpus`, `core/benchmark/ground_truth`, `infra/fs` y los entry points de `tools/evaluation`, confirmando que los defectos documentados en Fase 0 (HITO_0.2, HITO_0.3) permanecen vigentes: Partial Sealing (E-2.0-01), firma global ciega al Ground Truth (E-2.0-02), ciclo de vida inexistente (E-2.0-04) e identidad semántica huérfana (E-2.0-10).

El hallazgo central del Discovery es un **error de categoría ontológica**: el flujo actual de sellado trata la existencia de un archivo y su SHA-256 de bytes como si fueran validez científica e identidad del oráculo. El sistema opera como un catálogo físico de documentos y un almacén de artefactos, pero carece de la ontología para distinguir formalmente Draft de Oracle, existencia de validez, integridad de identidad semántica, y archivo JSON de Ground Truth científico (GAP-2.0-01..12).

Este ADR particulariza la visión del ADR Maestro para la Fase 2, formalizando la ontología que convierte un conjunto de archivos serializados en una verdad científica inmutable, y responde a los carry-forwards DF-01-C (rol ontológico de la identidad semántica), la auditoría de la autoridad de sellado, y la naturaleza del puerto de escritura de borradores.

---

## 2. PROBLEMA ARQUITECTÓNICO

La Scientific Baseline no puede certificarse porque el dominio carece de una ontología que distinga la verdad científica de su representación física. El problema no es de I/O ni de hashing, sino de **ausencia de objetos de dominio que gobiernen la validez, el estado y la identidad del oráculo**.

Dimensiones estructurales afectadas:

1. **Orfandad ontológica de la verdad científica:** No existe una entidad de dominio que represente el oráculo como verdad certificada; la "verdad" se reduce a la existencia de un artefacto serializado, sin contrato que la distinga de un borrador.
2. **Ausencia de gobierno del ciclo de vida:** Las transiciones entre borrador y oráculo sellado no están gobernadas por una autoridad formal; el estado de sello se infiere de datos incidentales en lugar de ser un estado explícito y transitable.
3. **Colapso de las dimensiones de identidad:** La integridad física del artefacto (hash de bytes) se confunde con la identidad semántica del contenido científico, impidiendo el encadenamiento de confianza y habilitando mutaciones silenciosas.
4. **Simetría indebida de las superficies de acceso:** Las rutas de curaduría (escritura) y de runtime (lectura) no están segregadas, permitiendo que la primera sobrescriba o corrompa la segunda sin guardia.

Consecuencias de no resolver el problema:

* **Baseline no certificable:** el sistema no puede demostrar completitud, validez, sello ni identidad semántica de sus oráculos.
* **Regresiones silenciosas:** la firma global es ciega al Ground Truth, por lo que las mutaciones de oráculos son indetectables.
* **Corrupción por curaduría tardía:** un borrador puede sobrescribir un oráculo sellado sin que el dominio lo detecte.
* **Bloqueo de la cadena de certificación:** Fase 3 (Identity & Trust Model) no puede construirse sobre una ontología inexistente.

---

## 3. DECISIÓN ARQUITECTÓNICA

**La verdad científica del sistema se modela como una ontología de dominio pura en la que el Oráculo de Ground Truth es una entidad inmutable, sellada y semánticamente identificada, ontológicamente distinta de su borrador, de su representación serializada en disco y de su hash de integridad, y gobernada por un ciclo de vida formal con autoridad única de transición y por superficies de acceso asimétricas de curaduría y de runtime.**

En consecuencia:

* Un artefacto serializado en disco no constituye un Oráculo; es únicamente su representación, que debe ser hidratada y validada mediante el contrato canónico antes de ser considerada verdad científica.
* El estado de sello no puede inferirse de la presencia de un archivo ni de un campo incidental; debe ser un estado formal de un ciclo de vida gobernado por una autoridad única de transición.
* La identidad semántica del oráculo, la integridad del artefacto y la identidad física del documento fuente son dimensiones ortogonales que coexisten sin colapsarse, conforme al ADR Maestro §3.
* Las superficies de escritura (curaduría) y de lectura (runtime) están segregadas en puertos asimétricos; la curaduría no puede alcanzar ni corromper un oráculo sellado.
* El sellado exige completitud biyectiva entre documentos fuente y oráculos, y validación estructural previa, materializando el invariante *Zero Partial Sealing* del ADR Maestro §5.

---

## 4. OBJETIVO DE LA SUBFASE

Formalizar la ontología del Scientific Baseline Domain: los modelos inmutables que representan el corpus y el oráculo, el ciclo de vida que gobierna sus transiciones, el contrato de validez que distingue un borrador de un oráculo, y los puertos asimétricos que segregan la curaduría del consumo en runtime.

La subfase establece el lugar ontológico donde reside cada identidad (física, semántica, de integridad y de esquema), preparando el sustrato de dominio sobre el cual Fase 3 construirá el encadenamiento criptográfico, sin implementar dicho mecanismo.

El objetivo primordial es garantizar que:

> *"Un Oráculo no es un artefacto que existe; es una verdad que ha sido validada, sellada e identificada semánticamente."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance
* Formalización ontológica del Oráculo y del Borrador como tipos disjuntos del dominio.
* Definición del ciclo de vida formal del Ground Truth (`Draft → Audited → Validated → Sealed`) y de su autoridad única de transición.
* Definición del contrato de validez (DC-04): invariantes que separan un borrador de un oráculo válido.
* Definición de la asimetría de puertos: superficie de curaduría (escritura) vs superficie de runtime (lectura).
* Establecimiento del lugar ontológico de la identidad semántica, la integridad del artefacto, la identidad física y la versión de esquema, como dimensiones diferenciadas.
* Definición de la autoridad única de sellado y de los eventos de invalidez de sello (DC-08) a nivel ontológico.
* Definición de la invariante de completitud biyectiva (*Zero Partial Sealing*) como propiedad del dominio.

### Fuera del Alcance (Out of Scope)
* **NO** definir el mecanismo de encadenamiento criptográfico global ni la fórmula de $H_{baseline}$ (pertenece a la **Fase 3 — Identity & Trust Model**).
* **NO** materializar en disco los documentos del corpus canónico ni ejecutar el sellado operativo (pertenece a la **Fase 5 — Baseline Certification**).
* **NO** definir la evaluación topológica, el semantic recall ni la taxonomía de criticidad (pertenece a la **Fase 4 — Scientific Verification**).
* **NO** implementar compuertas de regresión en integración continua (pertenece a la **Fase 6 — Continuous Verification**).
* **NO** rediseñar el algoritmo de firma semántica (gobernado por **NADR-03 FROZEN**).
* **NO** realizar optimizaciones de rendimiento, asincronía o memoria (pertenece a la **Fase 18**).

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

Invariants específicas de la subfase, declaradas como principios (no como reglas normativas):

* **Principio de Disyunción Ontológica:** el Borrador y el Oráculo son tipos de dominio disjuntos; ningún estado del ciclo de vida permite que un borrador sea tratado como oráculo ni viceversa.
* **Principio de No-Inferencia de Estado:** el estado de un Ground Truth nunca se deduce de la presencia de un artefacto o de un dato incidental; es un estado explícito producido por una transición gobernada.
* **Principio de Separación de Identidades:** la identidad semántica, la integridad del artefacto y la identidad física del documento fuente son dimensiones ortogonales (heredado del ADR Maestro §3).
* **Principio de Completitud Biyectiva:** la pertenencia de un documento a la baseline exige correspondencia biyectiva entre el documento fuente y su oráculo (heredado del ADR Maestro §5, *Zero Partial Sealing*).

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

Tras la implementación de esta subfase, el dominio de la baseline científica posee una ontología explícita donde el corpus cataloga documentos fuente, cada documento sostiene una correspondencia biyectiva con un Ground Truth, y ese Ground Truth transita por un ciclo de vida gobernado desde borrador mutable hasta oráculo inmutable sellado. Las superficies de curaduría y de runtime están segregadas, y las identidades física, semántica, de integridad y de esquema residen en lugares ontológicos diferenciados.

```text
                 ┌───────────────────────────────────────────────┐
                 │            CORPUS  (Aggregate Root)           │
                 │    CorpusVersion · Identidad del catálogo     │
                 └──────────────────────┬────────────────────────┘
                                        │ 1..N
                 ┌──────────────────────▼────────────────────────┐
                 │           REGISTRO DE DOCUMENTO               │
                 │   Identidad física (H_physical) · traits      │
                 └──────────────────────┬────────────────────────┘
                                        │ 1..1 (biyectivo)
            ┌───────────────────────────┴───────────────────────────┐
            │                                                       │
   ┌────────▼─────────────┐                        ┌────────────────▼───────────┐
   │   GROUND TRUTH       │   compuerta de         │   GROUND TRUTH ORACLE      │
   │   DRAFT              │   validez + sello      │   (inmutable · sellado)    │
   │   (mutable)          ├───────────────────────►│   porta H_semantic         │
   │   superficie de      │   autoridad única      │   superficie de runtime    │
   │   curaduría          │   de transición        │   (lectura)                │
   └──────────────────────┘                        └────────────────────────────┘

   Ciclo de vida:  Draft ─► Audited ─► Validated ─► Sealed
   Identidades:    H_physical · H_semantic · integridad de artefacto · AST Schema Version
```

Invariante del estado objetivo:

> *"Un documento pertenece a la Scientific Baseline si y solo si existe una correspondencia biyectiva entre el documento fuente y un Oráculo válido, sellado y semánticamente identificado, y esa condición es determinista y verificable sin ambigüedad de estado."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la subfase de ontología del oráculo | ✅ |
| `ADR_F17_BIS_01.md` | Continuidad: la alineación del pipeline (Fase 1) es prerrequisito cumplido sobre el cual se formaliza la ontología (Fase 2) | ✅ |
| `HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY` | Evidencia forense vinculante que fundamenta la decisión | ✅ |
| NADRs de Fase 2 (a promulgar) | Materializan las reglas normativas derivadas de esta decisión | ✅ |
| `NADR-F17BIS-01` / `NADR-F17BIS-03` / `NADR-F17BIS-11` | Restricciones vigentes que condicionan la ontología (representación canónica, firma semántica, frontera hexagonal) | ✅ |
| `PHASE_17BIS_EXECUTION_PLAN.md` | Secuencia las tareas que materializan este ADR | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ).
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase.
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan.

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.