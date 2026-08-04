# ARCHITECTURE DECISION RECORD (ADR)
## ADR F17_BIS: Scientific Baseline Architecture & Canonical Corpus Governance (ADR Maestro)

* **Estado:** FROZEN / CONGELADO (Post-Phase 0 Audit)
* **Fecha de Emisión Original:** 2026-07-26
* **Fecha de Congelamiento:** 2026-08-02
* **Autor:** Architecture Board / Staff Engineering
* **Fase:** 17-BIS (Scientific Baseline / Canonical Corpus)
* **Módulos Afectados:** `core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/benchmark/topology`, `infra/fs`, `tools/evaluation`, `core/pipeline`, `core/ast`, `apps/bootstrap`, `apps/llm_workers`, `apps/compiler`

---

## 1. CONTEXTO Y JUSTIFICACIÓN

El proyecto ha completado exitosamente la **Fase 17**, estableciendo a `ProviderKind.OCR_PARSER` (`PyMuPDFProvider`) como el motor de extracción predeterminado respaldado por evidencia de benchmark estadístico.

La siguiente etapa del roadmap, la **Fase 18 (Advanced Local Runtime)**, introducirá modificaciones profundas en el motor de ejecución: asincronía pura top-to-bottom, elisión de puentes síncronos, gestión de memoria *zero-copy* y procesamiento por lotes (*batching*).

Para ejecutar la Fase 18 sin riesgo de degradación en la calidad de extracción o alteración silenciosa de la estructura documental, la arquitectura exige congelar una **Baseline Científica Inmutable** (*Canonical Corpus & Ground Truth*). Esta baseline actuará como oráculo determinista y red de seguridad (*Safety Net*) del sistema (*Principio 6: Golden Corpus Driven Development*).

> **Pivot Normativo Post-Fase 0:**
> La Fase 0 demostró que la construcción de una Scientific Baseline depende de la alineación previa del pipeline de producción. El objetivo del ADR permanece inalterado; sin embargo, *Production Pipeline Alignment* pasa a ser un prerrequisito arquitectónico obligatorio para la certificación científica.

---

## 2. PROBLEMA ARQUITECTÓNICO Y ESTADO OBSERVADO

La inspección del repositorio confirma la existencia de infraestructura de soporte en `core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/benchmark/topology`, `infra/fs` y `tools/evaluation`. No obstante, la arquitectura presenta tres incertidumbres estructurales críticas que deben resolverse formalmente:

1. **Riesgo de Sellado Parcial (Partial Sealing):** El estado actual de la infraestructura permite continuar el proceso de sellado emitiendo advertencias en logs cuando faltan archivos de *Ground Truth* para ciertos documentos, lo que viola la completitud exigida para una baseline científica.
2. **Ambigüedad entre Identidades:** La relación entre las distintas identidades del sistema (física del PDF, versión del esquema AST, versión del corpus y firma global de baseline) no está formalmente desacoplada ni encadenada, lo que podría permitir mutaciones silenciosas en los oráculos.
3. **Ausencia de Semántica de Regresión Graduada:** No existe un contrato de dominio que gradúe las divergencias del motor topológico (`ZhangShashaEngine`, `EntityRecallMetric`), lo que deja las evaluaciones al nivel de comparaciones binarias planas o snapshots rígidos.

### 2.1. Architectural Outcome of Phase 0

La auditoría forense demostró que las limitaciones identificadas originalmente en el subsistema de Benchmark no constituían un problema aislado, sino la manifestación de inconsistencias arquitectónicas distribuidas a lo largo del pipeline de producción. 

En consecuencia:
* Quedó demostrada la **"Ilusión del Benchmark"**: el benchmark medía una ruta *legacy* aislada, mientras el pipeline productivo real estaba fracturado.
* La auditoría encontró problemas sistémicos en producción (módulos zombis, dualidad operacional, tautologías en tests).
* El benchmark deja de verse como un sistema aislado.
* **La Scientific Baseline deja de considerarse un artefacto exclusivo del benchmark y se convierte en la referencia canónica contra la cual se evalúa el comportamiento funcional y estructural del pipeline de producción.**

---

## 3. SEPARACIÓN DE CONCEPTOS FUNDAMENTALES

Para evitar confusiones entre mecanismos de serialización, auditoría y evaluación, la arquitectura de la Fase 17-BIS distingue estrictamente tres dimensiones ortogonales:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. INTEGRIDAD (File / Artifact Integrity)                               │
│    ¿El archivo físico que poseo en disco es exactamente el sellado?     │
│    Mecanismo: SHA-256 directo sobre el artefacto.                       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. IDENTIDAD (Baseline & Schema Identity)                               │
│    ¿Qué versión inmutable de la verdad científica representa esta       │
│    colección de PDFs + Oráculos AST + Esquema de AST + Versión Corpus?  │
│    Mecanismo: Hash compuesto / encadenado determinista global.          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. REGRESIÓN (Topological & Semantic Regression)                        │
│    ¿El runtime actual se ha desviado científicamente del Oráculo?       │
│    Mecanismo: Evaluación topológica (TED) + Matriz de Criticidad.       │
└─────────────────────────────────────────────────────────────────────────┘
```

* **Integridad no implica Identidad:** Un hash de archivo correcto no garantiza la completitud ni el encadenamiento de la baseline global.
* **Identidad no reemplaza la Regresión:** Un hash global valida el estado inmutable; no explica qué nodo o estructura cambió durante la ejecución del runtime.
* **Regresión no es Coincidencia Binaria (Snapshotting):** La evaluación no busca coincidencia byte-a-byte rígida, sino garantizar que cualquier evolución técnica sea evaluada de forma determinista contra la topología, jerarquía, ecuaciones y tablas del corpus canónico, aplicando una política de criticidad explícita.

---

## 4. ALCANCE Y NO-OBJETIVOS (OUT OF SCOPE)

### Dentro জেলার Alcance
El alcance de este ADR comprende tanto la remediación arquitectónica necesaria para habilitar la certificación científica como la construcción de la propia Scientific Baseline.
* Formalización y auditoría del código de dominio en `core/benchmark/corpus` y `core/benchmark/ground_truth`.
* Definición del protocolo de sellado criptográfico atómico (Zero Partial Sealing).
* Definición de la taxonomía de criticidad de nodos y políticas de regresión topológica.
* Curaduría y materialización del Corpus Canónico en disco.
* Implementación de la compuerta de regresión automatizada (`CanonicalRegressionGate`) para CI/CD.

### Fuera del Alcance (Out of Scope)
* **NO** realizar optimizaciones de rendimiento, asincronía o memoria (pertenece estrictamente a Fase 18).
* **NO** integrar nuevos adaptadores de extracción de visión computacional (pertenece a Fase 17).
* **NO** introducir infraestructura distribuida (Redis, Message Brokers, Kubernetes, DBs remotas).
* **NO** modificar componentes de dominio, crear abstracciones ni refactorizar código durante la Fase 0.
* **NO** poblar el disco con documentos masivos antes de congelar los contratos de datos y resolver los candidatos a decisión.

---

## 5. INVARIANTES Y REGLAS DE GOBERNANZA

1. **Prohibición Estricta de Diseño en Discovery (Audit First, Design Later):** Durante la Fase 0, queda estrictamente prohibido introducir nuevas abstracciones, renombrar contratos, modificar la semántica existente o escribir código de producción. Su función es exclusivamente observar, mapear, medir y documentar.
2. **Reutilización Estricta (Reuse Before Invent):** Se exige consumir la infraestructura existente en `core/benchmark/` e `infra/fs/` antes de introducir nuevos componentes o DTOs.
3. **Invariante de Sellado Estricto (Zero Partial Sealing):** Un corpus NO podrá entrar en estado `SEALED` si no existe una correspondencia biyectiva completa entre los PDFs declarados y sus oráculos AST auditados ($N_{\text{PDF}} = N_{\text{GT}}$).
4. **Determinismo y Reproducibilidad:** Todo el pipeline de evaluación, serialización y cálculo de firmas debe ser 100% determinista.
5. **Desacoplamiento de Identidades:** La arquitectura debe mantener diferenciados los conceptos de *AST Schema Version* (estructura del árbol), *Corpus Version* (conjunto de documentos) e *Identity Hash* (firma global).

---

## 6. HOJA DE RUTA DE SUB-FASES GOBERNADAS

El progreso de la Fase 17-BIS se estructurará en las siguientes capacidades arquitectónicas lógicas:

    FASE 17-BIS — Scientific Baseline / Canonical Corpus
    │
    ├── FASE 0 — Architecture & Baseline Audit Gate (COMPLETADA)
    │
    ├── FASE 1 — Production Pipeline Alignment 
    │            (Prerrequisito arquitectónico para la certificación científica) (EN EJECUCIÓN)
    │
    ├── FASE 2 — Scientific Baseline Domain 
    │            (Definición de modelos inmutables y contratos del oráculo)
    │
    ├── FASE 3 — Identity & Trust Model 
    │            (Hashes deterministas, linaje y encadenamiento criptográfico)
    │
    ├── FASE 4 — Scientific Verification 
    │            (Topological regression, semantic recall y criticality)
    │
    ├── FASE 5 — Baseline Certification 
    │            (Materialización en disco y Zero Partial Sealing)
    │
    └── FASE 6 — Continuous Verification 
                 (Integración definitiva en CI Gates)

> **Cláusula de Relación con el Execution Plan:**
> The architectural phases defined in this ADR specify the required architectural capabilities. The operational sequencing, deployment strategy, technical dependencies and implementation logistics are governed independently by `PHASE_17BIS_EXECUTION_PLAN.md`. 
> 
> The Execution Plan exists because the forensic audit demonstrated that architectural capabilities cannot be implemented independently. Production remediation must precede scientific certification according to the dependency graph identified during Phase 0.


### Flujo de Gobernanza y Transición de Estado

```
[ Estado Actual del Repositorio ]
               │
               ▼
  ┌─────────────────────────┐
  │ Fase 0                  │
  │ Architecture Audit Gate │ ──► Recopilación de evidencia en código (ADR_F17_BIS_0)
  │ (NO CODE / NO I/O)      │
  └────────────┬────────────┘
               │
   Evidencia + Resoluciones DC
               │
               ▼
   [ Revisión de Arquitectura ]
               │
               ▼
  ┌─────────────────────────┐
  │ ADR F17_BIS FROZEN      │
  │ Decisiones CERRADAS     │ ──► Habilitación para escribir código
  └────────────┬────────────┘
               │
  ┌────────────┴────────────┬────────────────────────┐
  ▼                         ▼                        ▼
Fase 1: Contratos      Fase 2: Identidad       Fase 3: Regresión y
de Dominio             Criptográfica           Criticidad
  │                         │                        │
  └─────────────────────────┼────────────────────────┘
                            ▼
                         Fase 4: Materialización y Curaduría
                            │
                            ▼
                         Fase 5: Ejecución del Sello (SEALED)
                            │
                            ▼
                         Fase 6: Integración CI Gate
```

---

## 7. ESPECIFICACIÓN DE LA FASE 0 (HISTÓRICO)

> **Historical Note:**
> This section is preserved for traceability purposes. Phase 0 has been completed and its results are materialized in `ADR_F17_BIS_0`.

La **Fase 0** es una compuerta analítica de descubrimiento y auditoría forense governed por su propio documento de arquitectura (`ADR F17_BIS_0`).

* **Regla de Blindaje:** La Fase 0 no podrá introducir abstracciones nuevas, alterar código ni realizar refactorizaciones. Su entregable es evidencia técnica pura.
* **Entradas (Inputs):** Código fuente actual en `core/benchmark/`, `infra/fs/`, `infra/adapters/`, `tools/evaluation/` y suites de prueba en `tests/`.
* **Actividades de Auditoría:**
  1. Auditar la implementación de `SealGroundTruthUseCase` y `ManifestLineageSealer` para documentar la causa raíz del sellado parcial.
  2. Inspeccionar la mecánica de hashing en `ManifestFingerprintCalculator` y analizar cómo interactúan los hashes del PDF y del AST.
  3. Mapear los componentes reusables en `core/benchmark/topology/` (`ZhangShashaEngine`, `EntityRecallMetric`, políticas de correspondencia).
  4. Analizar el modelo de nodos AST V2 (`ContentNodeType`) para auditar la separación entre contenido semántico y formato incidental.
  5. Investigar las fronteras actuales entre las capas de Dominio, Aplicación, Infraestructura y CI.
  6. Recopilar evidencia técnica empírica para fundamentar la resolución de los candidatos a decisión (**DC-01 a DC-11**).
* **Entregables Obligatorios (Outputs de la Fase 0):**
  1. **Architecture Gap Matrix:** Estado real del repositorio vs. requerimientos de la baseline.
  2. **Current State & Contract Map:** Inventario de clases, DTOs y Puertos vigentes versus componentes obsoletos.
  3. **Evidence Register & DC Resolutions:** Respuestas fundamentadas con evidencia para DC-01 hasta DC-11.
  4. **Propuesta de Congelamiento del ADR Maestro (F17_BIS):** Borrador final con las decisiones técnicas cerradas listo para revisión y paso a estado `FROZEN`.

### Flujo Temporal de Gobernanza (Registro Histórico)

    [ Estado Actual del Repositorio ]
                   │
                   ▼
      ┌─────────────────────────┐
      │ Fase 0                  │
      │ Architecture Audit Gate │ ──► Recopilación de evidencia en código (ADR_F17_BIS_0)
      │ (NO CODE / NO I/O)      │
      └────────────┬────────────┘
                   │
       Evidencia + Resoluciones DC
                   │
                   ▼
       [ Revisión de Arquitectura ]
                   │
                   ▼
      ┌─────────────────────────┐
      │ ADR F17_BIS FROZEN      │
      │ Decisiones CERRADAS     │ ──► Habilitación para escribir código
      └────────────┬────────────┘
                   │
                   ▼
            [ Implementation ]

---

## 8. REGISTRO DE DECISIONES CANDIDATAS (DECISION CANDIDATES LOG)

**ESTADO FINAL: RESUELTOS (Post-Fase 0)**
*La siguiente lista se conserva intacta como registro histórico de la evolución arquitectónica del proyecto.*

* **DC-01 (Mecanismo de Hash de Identidad):** ¿Se requiere un árbol de Merkle jerárquico o es suficiente un hash compuesto canónico determinista para la escala del corpus?
* **DC-02 (Composición del Hash Físico $H_{physical}$):** ¿Qué campos exactos del manifiesto del PDF (SHA-256, page count, traits) deben formar la semilla del hash físico?
* **DC-03 (Composición del Hash Global $H_{baseline}$):** ¿Cómo debe estructurarse y encadenarse la firma global entre $H_{physical}$, los hashes de los oráculos AST y las versiones de esquema?
* **DC-04 (Contrato de Validez del Ground Truth):** ¿Qué invariantes de dominio (no vaciedad, ordenación, integridad de nodos) definen a un AST como un oráculo válido vs. un borrador (*Draft*)?
* **DC-05 (Ciclo de Vida del Ground Truth):** ¿Cuáles son las transiciones formales de estado (`Draft` $\rightarrow$ `Audited` $\rightarrow$ `Validated` $\rightarrow$ `Sealed`) y qué componentes las gobiernan?
* **DC-06 (Taxonomía de Criticidad de Nodos):** ¿Cómo se mapea la jerarquía de `ContentNodeType` preexistente en niveles de impacto de regresión (`CRITICAL`, `WARNING`, `INFO`)?
* **DC-07 (Reglas de Regresión Topológica):** ¿Bajo qué condiciones específicas de desalineación topológica o divergencia de contenido la suite de integración emite un `HARD FAIL` vs. un `WARNING`?
* **DC-08 (Desacoplamiento de Versiones e Invalidez de Sello):** ¿Cómo interactúan *AST Schema Version*, *Corpus Version* y *Baseline Identity*, y qué eventos específicos invalidan el estado `SEALED`?
* **DC-09 (Esquema de Versionado y Compatibilidad):** ¿Cómo se estructuran los incrementos de versión del corpus y la política de compatibilidad hacia atrás ante sustitución de documentos?
* **DC-10 (Desacoplamiento del Runner de CI):** ¿Cómo se desacopla la ejecución de la prueba en `pytest` para que consuma los casos de uso del dominio sin duplicar lógica en los scripts de prueba?
* **DC-11 (Contrato de Fronteras entre Capas):** ¿Qué responsabilidades pertenecen strictly a Domain, Application, Infrastructure y CI/Test Runner, y qué dependencias quedan explícitamente prohibidas?

---

## 9. ARCHITECTURE GOVERNANCE FRAMEWORK

Para garantizar la estabilidad del sistema documental y evitar la mezcla de responsabilidades, la gobernanza del proyecto se estructura explícitamente en cuatro niveles:

    ADR F17_BIS
    Defines the architectural vision, invariants, logical capabilities and scope.
            │
            ▼
    ADR_F17_BIS_0
    Provides the forensic evidence supporting the architectural decisions.
            │
            ▼
    NADR-01 ... NADR-11
    Codify the mandatory architectural rules derived from the audit.
            │
            ▼
    PHASE_17BIS_EXECUTION_PLAN
    Defines the operational sequencing required to implement those capabilities.

> **Cláusula de Jerarquía Normativa:** No lower governance level is authorized to redefine or contradict decisions established by an upper level.

---

## 10. DEFINITION OF DONE (DoD) EN DOS NIVELES

### Nivel A: Definition of Done de la Gobernanza (COMPLETADO)
El presente documento ha pasado de estado `PROPOSED` a `FROZEN` al cumplirse:
1. **Ejecución Completa de la Fase 0:** Presentación de la *Architecture Gap Matrix* y el *Contract Map*.
2. **Resolución de Decision Candidates:** 100% de los candidatos a decisión (**DC-01 al DC-11**) resueltos con evidencia empírica del código.
3. **Contrato de Arquitectura Aprobado:** Revisión técnica final del ADR con decisiones cerradas sin ambigüedades, y jerarquía de gobernanza establecida.

### Nivel B: Definition of Done Global de la Fase 17-BIS (Baseline Operativa)
La Fase 17-BIS se considerará oficialmente finalizada y cerrada cuando se cumplan las siguientes condiciones:
1. **Production Pipeline Alignment:** All mandatory Phase Gates defined by `PHASE_17BIS_EXECUTION_PLAN` successfully completed.
2. **Contratos de Dominio e Identidad Implementados:** Fases 2 y 3 ejecutadas y verificadas.
3. **Corpus Canónico Materializado:** Colección representativa (20-30 documentos) catalogada y sellada en disco bajo la firma global $H_{baseline}$.
4. **Compuertas de CI Activas:** Pipeline en integración continua ejecutándose de forma exitosa contra los *Regression Gates*.
5. **Verificación Estática y Pruebas Limpias:** Analizadores estáticos ejecutándose con **0 errors, 0 warnings** y suite de pruebas en verde.