# NADR-F17-BIS-20: Canonical Corpus Qualification & Trait Coverage

## 1. METADATA

* **Decision ID:** `NADR-F17-BIS-20`
* **Título:** Canonical Corpus Qualification & Trait Coverage
* **Clase de Decisión:** `DATA / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.1.2
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 17-BIS — Fase 5 (Baseline Certification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-F5-01 (Canonical Corpus Qualification) — Establece las reglas normativas para cualificar documentos como miembros del corpus canónico, verificando identidad por contenido, cobertura de traits por inspección y deduplicación determinista.
* **Evidencia Forense:** `E-5.1-001`, `E-5.1-002`, `E-5.1-003`, `E-5.1-008`, `E-5.1-011`, `GAP-5.1-01`, `GAP-5.1-02`, `GAP-5.1-06`, `DC-5.0-01`, `DC-5.0-04`, `DC-5.1-001`, `DC-5.1-003`, `DC-5.1-004`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_05` (FROZEN), `NADR-F17BIS-16` (Semántica de Identidad), `NADR-F17BIS-17` (Contratos de Dominio)
  * **Influencia:** `NADR-F17BIS-21` (Ground Truth Eligibility), `NADR-F17BIS-22` (Canonical Evaluation Configuration), `NADR-F17BIS-23` (Scientific Calibration), `NADR-F17BIS-24` (Certification Tooling Integrity), `PHASE_17BIS_FASE5_EXECUTION_PLAN`
  * **Conflictúa con:** Uso de filenames como identidad de documento, selección de corpus por nombres de archivo sin inspección de contenido, tratamiento de duplicados como documentos independientes, aceptación silenciosa de campos no reconocidos en manifests.
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 25 reglas normativas en 7 dominios. |
| 1.1.0 | 2026-09-05 | Correcciones: (1) Architecture Risk Score corregido (S2 → S1); (2) R5 reformulada; (3) R26 recomputabilidad; (4) R27 idempotencia deduplicación; (5) R28 reproducibilidad cualificación. Total: 28 reglas. |
| 1.1.1 | 2026-09-05 | Correcciones menores: (1) Changelog "8 dominios" → "7 dominios"; (2) GAP-5.1-07 eliminado de evidencia; (3) NADR-22 y NADR-24 agregados a tabla de relaciones. |
| 1.1.2 | 2026-09-05 | **FROZEN.** Hardening normativo: (1) R1: "identidad física/de contenido" para no colisionar con document_id; (2) R12: "suficiente" reemplazado por relación contra catálogo vigente; (3) R18: reproducibilidad mediante registro auditable, no determinismo de inspección humana; (4) R19/R20: "al menos 20, rango objetivo 20-30"; (5) R24: hash recomputado vs hash declarado; (6) R26: payload canónico completo (6 dimensiones); (7) §4.2: cobertura de traits degradada a indicios NO DEMOSTRADOS; (8) §7: sealing eliminado como responsabilidad de NADR-20. |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin un corpus canónico cualificado, el sellado de la baseline no puede ejecutarse. La certificación de la baseline es el prerrequisito para la Fase 18 y la activación de Regression Gates en CI. Toda modificación del runtime queda sin red de seguridad.
* **Mantenibilidad:** 4 — Un corpus sin cualificación formal genera ambigüedad sobre qué documentos son autoridad científica, dificultando la evolución del sistema y la trazabilidad de decisiones.
* **Recuperabilidad:** 3 — La ausencia de identidad por contenido impide detectar corrupción o sustitución silenciosa de documentos en el corpus, comprometiendo la capacidad de recuperación ante fallos de integridad.
* **Seguridad:** 3 — La ausencia de verificación de contenido permite que documentos no cualificados contaminen la baseline científica, comprometiendo la validez de toda evaluación posterior.
* **Financiero:** 3 — La re-extracción o re-certificación de documentos no cualificados genera costo de retrabajo. Sin corpus canónico, las fases posteriores (18-21) quedan bloqueadas, generando costo de oportunidad significativo.
* **Total Score: 18/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**Todo documento que forme parte del corpus canónico debe ser cualificado mediante identidad por contenido, cobertura de traits verificada por inspección, y deduplicación determinista, antes de poder participar en el proceso de certificación de la baseline.**

En consecuencia:
* Ningún documento puede ser incluido en el corpus canónico basándose exclusivamente en su nombre de archivo o ubicación en el sistema de archivos.
* La identidad física de un documento en el corpus canónico está determinada exclusivamente por su contenido, no por su ruta, nombre o metadatos descriptivos.
* La cobertura de traits de cada documento debe ser verificada por inspección de contenido, no inferida por señales nominales.
* El manifest canónico debe ser recomputable determinísticamente y estar en el formato vigente de la arquitectura en el momento de la certificación.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de certificación de la baseline requiere un corpus canónico cualificado como prerrequisito para el sellado criptográfico de los Ground Truths. Sin embargo, la auditoría forense demostró que el estado actual del repositorio presenta tres clases de deficiencias que impiden la cualificación del corpus:

1. **Identidad por nombre de archivo:** Los documentos del corpus no tienen identidad por contenido verificada, sino que se identifican por su ubicación en el sistema de archivos, lo que permite sustitución silenciosa y confusión entre documentos.

2. **Cobertura de traits no demostrada:** El HITO 5.1 registró una cobertura declarada limitada a `native_pdf` y señaló indicios nominales de otros traits. El HITO 5.4 posteriormente clasificó dicha cobertura adicional como NO DEMOSTRADA. Los nombres de archivo son indicios, no evidencia suficiente.

3. **Duplicación física no resuelta:** El corpus contiene copias redundantes del mismo contenido identificadas como documentos independientes, lo que infla artificialmente el conteo de documentos y genera ambigüedad sobre cuál es la copia canónica.

### 4.2 Manifestación concreta identificada por la auditoría

* **`GAP-5.1-01` (P0 — Crítico):** El manifest de calibration_v1 está en formato legacy (DF-19), incompatible con el algoritmo de hashing actual. El hash almacenado (`c64a74d7...`) no coincide con el hash calculado por el algoritmo de 6 dimensiones (`2333205e...`). Esta evidencia justifica R23, R24 y R26 (manifest canónico), no R1-R4 (identidad por contenido).

* **`GAP-5.1-02` (P1 — Alto):** Cobertura de traits declarada limitada a `native_pdf` (1/7 traits). El HITO 5.1 señaló indicios nominales de variedad (doc_02_double → MULTI_COLUMN, doc_03_math → HEAVY_MATHEMATICS, doc_04_table → COMPLEX_TABLES, doc_05_graph → MIXED_CONTENT). El HITO 5.4 clasificó dicha cobertura adicional como NO DEMOSTRADA: los nombres de archivo son indicios, no evidencia suficiente.

* **`GAP-5.1-06` (P1 — Alto):** El mecanismo de validación de documentos acepta silenciosamente campos no reconocidos en los manifests, lo que permite que documentos con formato legacy pasen la validación sin detección.

* **`E-5.1-003` (P2 — Medio):** Duplicados físicos identificados por SHA-256. Grupo G1: 4 copias del mismo contenido (`84891f98...`). Grupo G2: 2 copias del mismo contenido (`21b9283a...`).

* **`DC-5.1-001` / `DC-5.0-01`:** Estructura física del corpus aún no canónica. benchmark_v1 vacío; calibration_v1 con 5 documentos.

* **`DC-5.1-003` / `DC-5.0-04`:** Déficit de 13-23 identidades respecto del objetivo de 20-30 documentos.

* **`DC-5.1-004`:** 3 PDFs legacy en la raíz del corpus sin manifest ni gobernanza, con .ast.json en formato incompatible con el contrato AST vigente.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Identidad por Contenido

1. Todo documento que forme parte del corpus canónico **MUST** tener su identidad física/de contenido determinada exclusivamente por el hash criptográfico de su contenido (SHA-256).
2. El nombre de archivo, la ruta de almacenamiento y los metadatos descriptivos **MUST NOT** constituir la identidad física de un documento en el corpus canónico.
3. Toda operación de inclusión, exclusión o verificación de un documento en el corpus **MUST** resolver primero la identidad por contenido antes de cualquier operación lógica.
4. Si dos rutas de almacenamiento apuntan al mismo contenido (mismo SHA-256), **MUST** tratarse como una única identidad de documento, no como documentos independientes.

### 5.2 Deduplicación

5. Todo documento incluido en el corpus canónico **MUST** ser único por identidad de contenido. El sistema **MUST NOT** admitir más de una entrada con el mismo SHA-256 en el corpus canónico.
6. Si se detectan múltiples rutas con el mismo contenido, el sistema **MUST** consolidarlas en una única entrada canónica, conservando trazabilidad de las rutas originales como referencia de proveniencia.
7. La deduplicación **MUST NOT** basarse en nombres de archivo, rutas o metadatos descriptivos.
8. Toda operación de deduplicación **MUST** registrar la evidencia de la consolidación (rutas originales, identidad consolidada, fecha).
9. Toda operación de deduplicación **MUST** ser idempotente: ejecutar la deduplicación múltiples veces sobre la misma colección de documentos **MUST** producir el mismo resultado.

### 5.3 Cobertura de Traits

10. La cobertura de traits de cada documento **MUST** ser verificada por inspección de contenido, no inferida por nombre de archivo, ruta o metadatos descriptivos.
11. Todo documento incluido en el corpus canónico **MUST** tener al menos un trait verificado. Un documento sin traits verificados **MUST NOT** ser incluido en el corpus canónico.
12. El conjunto de traits asignado a un documento **MUST** representar todos los desafíos de extracción y traducción observables que estén definidos por el catálogo vigente de traits y sean aplicables al contenido inspeccionado del documento.
13. Si un documento presenta un desafío de extracción o traducción no representado por los traits existentes en el catálogo vigente, **MUST** evaluarse la extensión del catálogo de traits antes de incluir el documento.

### 5.4 Qualificación e Inclusión

14. Todo documento **MUST** pasar un proceso de cualificación formal antes de ser incluido en el corpus canónico.
15. El proceso de cualificación **MUST** verificar: identidad por contenido, ausencia de duplicación, cobertura de traits, y compatibilidad con el formato de manifest vigente.
16. Un documento que no supere el proceso de cualificación **MUST NOT** ser incluido en el corpus canónico.
17. La decisión de incluir o excluir un documento **MUST** quedar registrada con evidencia (razón de inclusión o exclusión, fecha, responsable).
18. El proceso de cualificación **MUST** ser reproducible mediante un registro auditable de las entradas, reglas aplicadas, traits observados, decisión de cualificación y evidencia asociada, de modo que una reevaluación pueda reconstruir la decisión original.

### 5.5 Alta Varianza

19. El corpus canónico **MUST** satisfacer el objetivo arquitectónico de alta varianza, cubriendo diversidad relevante de layouts, estructuras documentales, desafíos de extracción y dominios científicos.
20. El corpus canónico **MUST** contener al menos 20 identidades de contenido únicas. El rango arquitectónico objetivo es 20-30 documentos.
21. La selección de documentos **MUST** priorizar la cobertura de traits no representados sobre la acumulación de documentos con traits ya cubiertos.

### 5.6 Manifest Canónico

22. Todo documento incluido en el corpus canónico **MUST** estar registrado en el manifest canónico con su identidad por contenido, traits verificados y conteo de páginas.
23. El manifest canónico **MUST** estar en el formato vigente (6 dimensiones). Un manifest en formato legacy **MUST** ser migrado antes de cualquier operación de certificación.
24. Toda modificación del manifest canónico **MUST** producir un nuevo manifest_hash mediante recomputación determinista del contenido canónico resultante. La operación **MUST** abortar si el hash declarado no coincide con el hash recomputado.
25. El manifest canónico **MUST NOT** contener entradas con campos no reconocidos sin detección explícita. La aceptación silenciosa de campos no reconocidos **MUST NOT** ser permitida.
26. El hash del manifest canónico **MUST** ser recomputable determinísticamente a partir del payload canónico vigente y su algoritmo de ordenamiento/serialización definido por la arquitectura. La misma representación canónica de las mismas dimensiones constituyentes **MUST** producir el mismo hash independientemente de la ejecución.

### 5.7 Provenance

27. Todo documento incluido en el corpus canónico **MUST** registrar su provenance: origen del documento, fecha de inclusión y responsable de la cualificación.
28. La provenance **MUST NOT** constituir la identidad del documento. La identidad física está determinada exclusivamente por el contenido (SHA-256).

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **Identidad de contenido garantizada:** La pertenencia al corpus queda definida por identidad criptográfica, eliminando el riesgo de sustitución silenciosa y confusión entre documentos. Esto garantiza que la deduplicación sea determinista y verificable.
* **Cobertura de traits demostrada:** La cobertura del corpus queda respaldada por inspección de contenido verificable contra el catálogo vigente de traits, eliminando el riesgo de cobertura ficticia basada en nombres de archivo.
* **Manifiesto íntegro y verificable:** El manifiesto del corpus queda en formato vigente con hash verificable y recomputable, eliminando el riesgo de corrupción silenciosa o incompatibilidad con el algoritmo de hashing.
* **Déficit de corpus documentado:** El déficit de identidades respecto del rango objetivo queda documentado explícitamente, habilitando la planificación de adquisición en el Execution Plan.
* **Duplicados consolidados:** Los grupos de duplicados G1 y G2 quedan consolidados en identidades únicas, eliminando el riesgo de leakage en la calibración y evaluación por presencia de copias del mismo contenido en particiones diferentes.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que todo documento en el corpus canónico tiene un hash SHA-256 válido y único.
  * Verificación de que el manifest canónico está en el formato vigente (6 dimensiones).
  * Verificación de que el hash del manifest es válido y reproducible.
  * Verificación de que el hash del manifest es recomputable a partir del payload canónico completo.
  * Verificación de que no existen entradas con campos no reconocidos sin detección explícita.
  * Verificación de que todo documento tiene al menos un trait verificado contra el catálogo vigente.
  * Verificación de que no existen documentos duplicados por SHA-256 en el manifest.

* **Validation (dinámica/comportamental):**
  * Ejecución del proceso de cualificación sobre todos los documentos candidatos, verificando que solo documentos verificados son incluidos.
  * Ejecución de la deduplicación por identidad de contenido, verificando que no existen entradas duplicadas.
  * Verificación de la idempotencia de la deduplicación: ejecutar la deduplicación dos veces produce el mismo resultado.
  * Verificación de la cobertura de traits por inspección de contenido sobre todos los documentos del corpus.
  * Verificación de que el corpus cualificado puede ser consumido por el proceso de sealing definido por NADR-21 sin violar las invariantes de este NADR.
  * Test de determinismo: la misma colección de documentos produce el mismo hash de manifest en múltiples ejecuciones.
  * Test de sensibilidad: cambiar un trait de un documento produce un hash de manifest diferente.
  * Test de sensibilidad: cambiar el contenido de un documento (y por tanto su SHA-256) produce un hash de manifest diferente.
  * Inspección de contenido de una muestra de documentos para validar que los traits declarados corresponden al contenido real.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro §6 (Golden Corpus: 20-30 documentos de alta varianza) y §5 (Determinismo y Reproducibilidad, Desacoplamiento de Identidades). |
| `ADR_F17_BIS_05` | Este NADR implementa D1 (Corpus Canónico) del ADR de Fase 5. |
| `NADR-F17BIS-16` | **Dependencia directa:** La semántica de identidad de este NADR depende de las reglas de identidad de NADR-16. |
| `NADR-F17BIS-17` | **Dependencia directa:** Los contratos de dominio de este NADR dependen de los contratos de NADR-17. |
| `NADR-F17BIS-21` | **Influencia:** NADR-21 (Ground Truth Eligibility) depende de la cualificación del corpus establecida por este NADR. |
| `NADR-F17BIS-22` | **Influencia:** NADR-22 (Canonical Evaluation Configuration) depende del corpus canónico cualificado por este NADR para evaluar el motor topológico. |
| `NADR-F17BIS-23` | **Influencia:** NADR-23 (Scientific Calibration) depende del corpus canónico cualificado por este NADR para la partición de datasets y calibración. |
| `NADR-F17BIS-24` | **Influencia:** NADR-24 (Certification Tooling Integrity) depende del corpus canónico cualificado por este NADR para la certificación. |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN` | Materializa las reglas de este NADR mediante tareas de cualificación, deduplicación y migración. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la elegibilidad, curaduría o sellado de Ground Truths (responsabilidad de `NADR-F17BIS-21`).
* **No gobierna** la configuración del motor de evaluación topológica ni el modelo de costo (responsabilidad de `NADR-F17BIS-22`).
* **No gobierna** la calibración empírica de parámetros ni la independencia de datasets (responsabilidad de `NADR-F17BIS-23`).
* **No gobierna** la integridad operacional del tooling de certificación ni la semántica de fallo (responsabilidad de `NADR-F17BIS-24`).
* **No gobierna** la integración en CI/CD de los Regression Gates (responsabilidad de Fase 6).
* **No gobierna** la infraestructura de persistencia ni la atomicidad de escrituras (responsabilidad de `NADR-F17BIS-21` y `NADR-F17BIS-16`).
* **No prescribe** la selección específica de documentos a adquirir ni las fuentes de adquisición (responsabilidad del Execution Plan y del Architecture Board).
* **No prescribe** el protocolo de inspección de contenido ni el catálogo de traits (responsabilidad del Execution Plan).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del `PHASE_17BIS_FASE5_EXECUTION_PLAN`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.