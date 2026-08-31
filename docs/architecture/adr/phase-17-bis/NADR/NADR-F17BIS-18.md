# NADR-F17BIS-18: Taxonomía de Criticidad de Nodos para Regresión Científica Graduada

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-18`
* **Título:** Taxonomía de Criticidad de Nodos para Regresión Científica Graduada
* **Clase de Decisión:** `DATA / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Phase 17-BIS, Fase 4 (Scientific Verification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Domain Engineering / Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-004 (Taxonomía de Criticidad de Nodos) — Clasificación formal de nodos del AST por impacto científico, gobernando cómo las divergencias topológicas se gradúan según la severidad del contenido afectado.
* **Evidencia Forense:** `E-4.2-001`, `E-4.2-003`, `E-4.2-006`, `GAP-4.2-01`, `GAP-4.2-03`, `GAP-4.2-06`, `E-4.1-005` (UnitCostContext sin ponderación), `E-0.4-326` (ContentNodeType sin clasificadores de criticidad), `OBS-0.4.2-04`, `DC-06` (ADR Maestro §8)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17-BIS_04` (FROZEN), `NADR-F17BIS-01` (Canonical AST Representation), `NADR-F17BIS-12` (Ground Truth Oracle Ontology), `NADR-F17BIS-13` (Ground Truth Validity & Baseline Completeness)
  * **Influencia:** `NADR-F17BIS-19` (Reglas de Regresión Topológica — consume la taxonomía para ponderar costos y emitir veredictos), `NADR-F17BIS-20` (Semántica de Evaluación Graduada — consume la criticidad para graduar divergencias)
  * **Conflictúa con:** Toda evaluación topológica que trate todos los nodos con peso uniforme sin distinción de impacto científico. Toda evaluación binaria (pasa/falla) que no gradúe la severidad de la divergencia.
  * **Reemplaza a:** `N/A`

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin taxonomía de criticidad, la pérdida de una ecuación matemática tiene exactamente el mismo peso que la pérdida de un caption. El sistema no puede distinguir entre una divergencia que destruye contenido científico primario y una que degrada un elemento auxiliar. Las regresiones críticas pasan desapercibidas o se tratan con la misma severidad que las triviales.
* **Mantenibilidad:** 4 — Sin una taxonomía formal, cada evaluación topológica futura debe reinventar la ponderación de nodos. La ausencia de un contrato centralizado de criticidad genera inconsistencias entre evaluadores y dificultad para evolucionar la taxonomía de forma coherente.
* **Recuperabilidad:** 3 — Ante una regresión detectada, la ausencia de criticidad impide priorizar la remediación. No se puede determinar si una divergencia requiere intervención inmediata (pérdida de ecuación) o puede diferirse (pérdida de caption).
* **Seguridad:** 2 — La taxonomía de criticidad no introduce vulnerabilidades de seguridad directamente, pero su ausencia permite que divergencias críticas se enmascaren como triviales, comprometiendo la integridad científica del sistema.
* **Financiero:** 2 — La ausencia de criticidad no genera costos directos, pero impide la optimización de recursos de remediación al no poder priorizar las divergencias por impacto.

* **Total Score: 16/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La taxonomía de criticidad de nodos constituye una capacidad de dominio formal que clasifica cada tipo de nodo del AST por su impacto científico, gobernando cómo las divergencias topológicas se gradúan según la severidad del contenido afectado, y garantizando que la pérdida de contenido científico primario se trate con severidad absoluta e independiente de cualquier métrica agregada.**

En consecuencia:
* Toda evaluación topológica que compare un runtime contra un oráculo sellado **DEBE** ponderar las divergencias según la criticidad del nodo afectado. Queda prohibida la evaluación con peso uniforme.
* La pérdida de cualquier nodo clasificado como crítico **DEBE** emitir un veredicto de fallo absoluto, independientemente de cualquier métrica agregada de similitud estructural.
* La taxonomía de criticidad **DEBE** cubrir exhaustivamente todos los tipos de nodo definidos en la ontología del AST. Ningún tipo de nodo puede quedar sin clasificación.
* La taxonomía **DEBE** ser extensible: la adición de nuevos tipos de nodo a la ontología **DEBE** poder clasificarse sin modificar la estructura de la taxonomía existente.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de evaluación topológica del sistema carece de una capacidad formal de clasificación de nodos por impacto científico. El motor de distancia de edición de árboles y los evaluadores de recuperación semántica operan con costos unitarios uniformes, tratando todas las divergencias topológicas con la misma severidad. Esta ausencia impide que el sistema distinga entre una regresión que destruye contenido científico primario (una ecuación perdida, una tabla eliminada) y una que degrada un elemento auxiliar (un caption ausente, una imagen faltante).

Las clases de defectos identificadas son:

1. **Ausencia de taxonomía de criticidad:** No existe ningún contrato de dominio que clasifique los tipos de nodo por impacto científico. La ontología del AST define tipos semánticos, pero no establece jerarquía de criticidad entre ellos.

2. **Costos de edición uniformes:** El contexto de costos de edición opera con penalizaciones simétricas unitarias, sin distinción de tipo de nodo. Una inserción de ecuación tiene exactamente el mismo costo que una inserción de caption.

3. **Ausencia de veredicto graduado por criticidad:** No existe mecanismo que emita un fallo absoluto ante la pérdida de nodos críticos. Toda divergencia se trata como una desviación gradual medible por métricas agregadas.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-4.2-001` / `GAP-4.2-01` (P0 — Crítico):** Ausencia total de taxonomía de criticidad. No existe ningún enum, política o contrato que mapee los tipos de nodo de la ontología del AST a niveles de criticidad (`CRITICAL`, `WARNING`, `INFO`). DC-06 del ADR Maestro §8 permanece sin materialización operativa.

* **`E-4.2-003` / `GAP-4.2-03` (P1 — Alto):** El contexto de costos de edición opera con costos unitarios simétricos (inserción=1.0, borrado=1.0, sustitución=1.0 si difiere). No existe ponderación por criticidad de nodo. La pérdida de una ecuación tiene el mismo peso que la pérdida de un caption.

* **`E-4.2-006` / `GAP-4.2-06` (P1 — Alto):** El protocolo de política de costos de edición existe como contrato abstracto, pero no tiene implementación ponderada por criticidad. La capacidad de ponderación está definida contractualmente pero no materializada.

* **`E-4.1-005` (P1 — Alto):** El contexto de costos unitarios actual aplica penalizaciones simétricas atómicas sin distinción de tipo de nodo. Es funcional para evaluación topológica básica, pero insuficiente para regresión científica graduada.

* **`OBS-0.4.2-04` (P1 — Alto):** La ontología del AST carece de métodos o clasificadores de criticidad semántica. Los tipos de nodo definen semántica pero no jerarquía de impacto.

* **`DC-06` (ADR Maestro §8):** "Taxonomía de Criticidad de Nodos: ¿Cómo se mapea la jerarquía de `ContentNodeType` preexistente en niveles de impacto de regresión (`CRITICAL`, `WARNING`, `INFO`)?" — Decision Candidate declarado en el ADR Maestro, sin materialización operativa.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Taxonomía de Criticidad de Nodos

1. Todo tipo de nodo definido en la ontología del AST **MUST** tener una clasificación de criticidad asignada. Ningún tipo de nodo puede quedar sin clasificación.

2. La taxonomía de criticidad **MUST** definir exactamente tres niveles de impacto: `CRITICAL`, `WARNING` e `INFO`. No se permiten niveles adicionales ni sub-niveles.

3. La clasificación `CRITICAL` **MUST** asignarse exclusivamente a tipos de nodo cuya pérdida destruye contenido científico primario irrecuperable. La pérdida de un nodo `CRITICAL` invalida la integridad científica del documento.

4. La clasificación `WARNING` **MUST** asignarse a tipos de nodo cuya pérdida degrada significativamente la estructura o el contenido del documento, pero no destruye contenido científico primario. La pérdida de un nodo `WARNING` compromete la calidad pero no la validez científica.

5. La clasificación `INFO` **MUST** asignarse a tipos de nodo cuya pérdida degrada elementos auxiliares o de presentación, sin comprometer la estructura principal ni el contenido científico primario del documento.

6. La taxonomía de criticidad **MUST** ser declarativa y centralizada. La clasificación de cada tipo de nodo **MUST** estar definida en un único punto de autoridad, no distribuida entre múltiples evaluadores.

7. La taxonomía de criticidad **MUST NOT** depender del contenido específico de un nodo. La clasificación se basa exclusivamente en el tipo semántico del nodo, no en su texto, geometría o metadatos.

   > **Nota aclaratoria — Supuesto de AST bien formado:** La taxonomía de criticidad asume que el AST está bien formado, es decir, que cada nodo está clasificado correctamente según su tipo semántico (por ejemplo, las ecuaciones están clasificadas como `DISPLAY_EQUATION` o `INLINE_EQUATION`, no como `HEADING` ni `PARAGRAPH`). La taxonomía de criticidad no compensa errores de clasificación del parser ni del builder del AST. Si el AST contiene nodos mal clasificados, la criticidad asignada será incorrecta, pero eso es responsabilidad de la calidad del parser, no de la taxonomía.

### 5.2 Extensibilidad de la Taxonomía

8. La taxonomía de criticidad **MUST** ser extensible. La adición de nuevos tipos de nodo a la ontología del AST **MUST** poder clasificarse sin modificar la estructura de la taxonomía existente.

9. Todo nuevo tipo de nodo añadido a la ontología **MUST** recibir una clasificación de criticidad antes de poder ser evaluado por cualquier evaluador topológico. Un tipo de nodo sin clasificación **MUST** causar un fallo explícito en la evaluación.

10. La taxonomía de criticidad **MUST NOT** ser modificada sin evidencia empírica que justifique el cambio. Toda reclasificación de un tipo de nodo **MUST** estar respaldada por un análisis de impacto sobre la baseline canónica.

### 5.3 Ponderación de Costos de Edición

11. Todo contexto de costos de edición utilizado en evaluación topológica de regresión **MUST** ponderar las operaciones de edición (inserción, borrado, sustitución) según la criticidad del nodo afectado. Queda prohibida la evaluación con costos unitarios uniformes en evaluación de regresión.

12. Los costos de edición ponderados **MUST** garantizar que la pérdida de un nodo `CRITICAL` produzca una penalización estrictamente mayor que la pérdida de un nodo `WARNING`, y que la pérdida de un nodo `WARNING` produzca una penalización estrictamente mayor que la pérdida de un nodo `INFO`.

13. Los pesos de criticidad **MUST** ser configurables mediante una política inyectada. Los valores concretos de ponderación **MUST NOT** estar codificados de forma inmutable en el motor de evaluación.

14. Los pesos de criticidad **MUST** tener valores por defecto definidos y documentados. Los valores por defecto constituyen una propuesta inicial sujeta a validación empírica sobre la baseline canónica.

15. Los pesos de criticidad **MUST** ser deterministas. Dados los mismos pesos y los mismos nodos, el costo de edición calculado **MUST** ser idéntico en cualquier ejecución.

### 5.4 Veredicto de Fallo Absoluto por Criticidad

16. La pérdida de cualquier nodo clasificado como `CRITICAL` **MUST** emitir un veredicto de fallo absoluto, independientemente de cualquier métrica agregada de similitud estructural. La pérdida de contenido científico primario no puede compensarse con métricas graduales.

17. El veredicto de fallo absoluto por pérdida de nodo `CRITICAL` **MUST** evaluarse antes de cualquier métrica agregada. La verificación de criticidad absoluta **MUST** tener precedencia sobre cualquier cálculo de similitud estructural.

18. La pérdida de nodos clasificados como `WARNING` **MUST** emitir un veredicto de advertencia si la cantidad o proporción de nodos perdidos supera un umbral configurable. La pérdida aislada de nodos `WARNING` **MAY** emitirse como veredicto de aprobación con observación.

19. La pérdida de nodos clasificados como `INFO` **MUST** emitirse como veredicto de aprobación con observación. La pérdida de nodos `INFO` **MUST NOT** causar un veredicto de fallo.

### 5.5 Trazabilidad de la Clasificación

20. Toda evaluación topológica que utilice la taxonomía de criticidad **MUST** registrar la clasificación aplicada a cada nodo evaluado. La trazabilidad de la clasificación **MUST** estar disponible para auditoría posterior.

21. La taxonomía de criticidad **MUST** estar documentada con la justificación de cada clasificación. La documentación **MUST** explicar por qué cada tipo de nodo recibió su clasificación específica.

22. Toda reclasificación de un tipo de nodo **MUST** registrarse como un evento de gobernanza con trazabilidad completa. Las reclasificaciones **MUST NOT** aplicarse silenciosamente.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La evaluación topológica de regresión deja de tratar todas las divergencias con la misma severidad. La pérdida de contenido científico primario se detecta y se trata con severidad absoluta, mientras que la pérdida de elementos auxiliares se trata con severidad proporcional.

* La taxonomía de criticidad se convierte en un contrato de dominio centralizado que gobierna la clasificación de nodos por impacto científico. Cualquier evaluación topológica futura debe consumir esta taxonomía, eliminando la inconsistencia entre evaluadores.

* Los costos de edición dejan de ser uniformes y pasan a ponderarse según la criticidad del nodo afectado. Esto garantiza que la métrica de similitud estructural refleje fielmente el impacto científico de las divergencias.

* El veredicto de regresión pasa a ser graduado y basado en criticidad, permitiendo distinguir entre fallos absolutos (pérdida de contenido científico primario), advertencias (degradación estructural significativa) y aprobaciones con observación (pérdida de elementos auxiliares).

* La taxonomía de criticidad se convierte en un artefacto de gobernanza que puede evolucionar con evidencia empírica, permitiendo reclasificaciones justificadas sin romper la estructura de la taxonomía.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que la taxonomía de criticidad cubre exhaustivamente todos los tipos de nodo definidos en la ontología del AST. Un tipo de nodo sin clasificación debe causar un fallo de compilación o de validación estática.
  * Verificación de que los pesos de criticidad son deterministas: dados los mismos pesos y los mismos nodos, el costo de edición calculado debe ser idéntico en cualquier ejecución.
  * Verificación de que la taxonomía de criticidad está declarada en un único punto de autoridad centralizado.
  * Verificación de que los pesos de criticidad son configurables mediante una política inyectada, no codificados de forma inmutable en el motor de evaluación.

* **Validation (dinámica/comportamental):**
  * Validación de que la pérdida de un nodo `CRITICAL` emite un veredicto de fallo absoluto, independientemente de cualquier métrica agregada.
  * Validación de que la pérdida de un nodo `WARNING` emite un veredicto de advertencia cuando la proporción de nodos perdidos supera el umbral configurable.
  * Validación de que la pérdida de un nodo `INFO` emite un veredicto de aprobación con observación, nunca un veredicto de fallo.
  * Validación de que los costos de edición ponderados producen una penalización estrictamente mayor para nodos `CRITICAL` que para nodos `WARNING`, y estrictamente mayor para nodos `WARNING` que para nodos `INFO`.
  * Validación de que la adición de un nuevo tipo de nodo a la ontología sin clasificación causa un fallo explícito en la evaluación.
  * Validación empírica de los pesos de criticidad por defecto sobre la baseline canónica, confirmando que producen una gradación coherente con el impacto científico esperado.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa el Decision Candidate DC-06 declarado en el ADR Maestro §8: "Taxonomía de Criticidad de Nodos: ¿Cómo se mapea la jerarquía de ContentNodeType preexistente en niveles de impacto de regresión (CRITICAL, WARNING, INFO)?" |
| `ADR_F17-BIS_04` | Este NADR implementa la capacidad de taxonomía de criticidad definida en la Arquitectura Objetivo del ADR de Fase 4 §7. La taxonomía propuesta en el ADR constituye la propuesta inicial que este NADR formaliza como capacidad de dominio. |
| `NADR-F17BIS-01` | **Dependencia directa:** Este NADR consume la ontología del AST definida en NADR-01. La taxonomía de criticidad clasifica los tipos de nodo definidos en la ontología. |
| `NADR-F17BIS-12` | **Dependencia directa:** Este NADR consume la ontología del oráculo sellado definida en NADR-12. La taxonomía de criticidad se aplica a los nodos del oráculo sellado durante la evaluación de regresión. |
| `NADR-F17BIS-13` | **Dependencia directa:** Este NADR consume el contrato de validez del oráculo definido en NADR-13. La taxonomía de criticidad se aplica a oráculos válidos. |
| `NADR-F17BIS-19` | **Influencia:** Este NADR habilita las reglas de regresión topológica definidas en NADR-19. NADR-19 consume la taxonomía de criticidad para ponderar costos de edición y emitir veredictos graduados. |
| `NADR-F17BIS-20` | **Influencia:** Este NADR habilita la semántica de evaluación graduada definida en NADR-20. NADR-20 consume la taxonomía de criticidad para graduar divergencias topológicas. |
| `PHASE_17BIS_FASE4_EXECUTION_PLAN` | Las tareas de implementación de este NADR se secuencian en el Execution Plan de Fase 4. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** las reglas específicas de emisión de veredictos de regresión (`PASS`, `WARNING`, `HARD_FAIL`) ni los umbrales de similitud estructural. Esas reglas son responsabilidad de `NADR-F17BIS-19` (Reglas de Regresión Topológica).

* **No gobierna** la semántica de evaluación graduada ni la definición de qué constituye una divergencia topológica significativa. Esa semántica es responsabilidad de `NADR-F17BIS-20` (Semántica de Evaluación Graduada).

* **No gobierna** la interacción entre la taxonomía de criticidad y la evaluación de recall semántico (`EntityRecallEvaluator`). La ponderación de criticidad en las métricas de recall es responsabilidad de `NADR-F17BIS-19` (Reglas de Regresión Topológica).

* **No gobierna** la implementación concreta del motor de distancia de edición de árboles ni de los evaluadores de recuperación semántica. Esos componentes son responsabilidad de la infraestructura topológica existente (Fase 17).

* **No gobierna** la ontología del AST ni la definición de tipos de nodo. La ontología del AST es responsabilidad de `NADR-F17BIS-01` (Canonical AST Representation).

* **No gobierna** la ontología del oráculo sellado ni el ciclo de vida del Ground Truth. Esas ontologías son responsabilidad de `NADR-F17BIS-12` (Ground Truth Oracle Ontology) y `NADR-F17BIS-13` (Ground Truth Validity & Baseline Completeness).

* **No gobierna** la materialización en disco de la baseline canónica ni el protocolo de sellado criptográfico. Esas capacidades son responsabilidad de `NADR-F17BIS-14` (Runtime Port Asymmetry & Sealing Authority) y la Fase 5 (Baseline Certification).

* **No gobierna** la integración de compuertas de regresión en CI/CD. Esa integración es responsabilidad de la Fase 6 (Continuous Verification).

* **No prescribe** tareas de implementación ni Definition of Done. Esas responsabilidades son del Execution Plan.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.