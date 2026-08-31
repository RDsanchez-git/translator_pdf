# NADR-F17BIS-19: Reglas de Regresión Topológica Graduada

## 1. METADATA

* **Decision ID:** `NADR-F17BIS-19`
* **Título:** Reglas de Regresión Topológica Graduada y Veredicto Científico
* **Clase de Decisión:** `OPERATIONAL / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS, Fase 4 (Scientific Verification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Domain Engineering / Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-005 (Reglas de Regresión Topológica Graduada) — Contrato formal que gobierna la emisión de veredictos científicos graduados (PASS / WARNING / HARD_FAIL) sobre la desviación topológica del runtime contra el oráculo sellado, basándose en un doble mecanismo de protección (NSS ponderado por criticidad + regla absoluta de pérdida de contenido científico primario), verificación criptográfica previa y reutilización del pipeline de producción.
* **Evidencia Forense:** `E-4.2-002`, `GAP-4.2-02`, `E-4.3-001`, `GAP-4.3-01`, `GAP-4.3-02`, `GAP-4.3-04`, `GAP-4.3-05`, `E-4.5-004`, `E-4.5-005`, `DC-07` (ADR Maestro §8), `E-4.1-005` (UnitCostContext sin ponderación)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17-BIS_04` (FROZEN), `NADR-F17BIS-12` (Ground Truth Oracle Ontology), `NADR-F17BIS-13` (Ground Truth Validity & Baseline Completeness), `NADR-F17BIS-14` (Runtime Port Asymmetry & Sealing Authority), `NADR-F17BIS-16` (Cryptographic Identity Semantics), `NADR-F17BIS-17` (Identity Encoding Integrity), `NADR-F17BIS-18` (Taxonomía de Criticidad de Nodos)
  * **Influencia:** `NADR-F17BIS-20` (Semántica de Evaluación Graduada), `Fase 6` (Continuous Verification — CI/CD integration)
  * **Conflictúa con:** Toda evaluación topológica binaria (pasa/falla) sin graduación. Todo snapshot rígido (byte-a-byte comparison). Toda evaluación que utilice el oráculo sin verificación criptográfica previa.
  * **Reemplaza a:** `N/A`

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin reglas formales de veredicto graduado, el sistema no puede distinguir entre una regresión que destruye contenido científico primario (ecuación perdida) y una que degrada un elemento auxiliar (caption ausente). Las regresiones críticas pasan desapercibidas o se tratan con la misma severidad que las triviales.

* **Mantenibilidad:** 4 — Sin reglas formales centralizadas, cada evaluación topológica futura debe reinventar las condiciones de emisión de veredictos. La ausencia de un contrato unificado de veredicto genera inconsistencias entre evaluadores y dificultad para evolucionar las reglas de forma coherente.

* **Recuperabilidad:** 4 — Ante una regresión detectada, la ausencia de veredicto graduado impide priorizar la remediación. No se puede determinar si una divergencia requiere intervención inmediata (pérdida de ecuación → `HARD_FAIL`) o puede diferirse (pérdida de caption → `PASS` con observación).

* **Seguridad:** 2 — La evaluación de regresión no introduce vulnerabilidades de seguridad directamente, pero su ausencia permite que regresiones críticas se enmascaren como triviales, comprometiendo la integridad científica del sistema.

* **Financiero:** 2 — La ausencia de veredicto graduado no genera costos directos, pero impide la optimización de recursos de remediación al no poder priorizar las divergencias por impacto científico.

* **Total Score: 17/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La regresión topológica del runtime contra el oráculo sellado se gobierna mediante reglas formales que emiten veredictos graduados (PASS / WARNING / HARD_FAIL) basados en un doble mecanismo de protección (NSS ponderado por criticidad + regla absoluta de pérdida de contenido científico primario), verificando la integridad criptográfica y el estado de ciclo de vida del oráculo antes de evaluar, reutilizando el composition root del pipeline de producción para generar el runtime AST, y emitiendo un reporte de regresión determinista y consumible por CI/CD.**

En consecuencia:
* Toda evaluación de regresión **DEBE** emitir un veredicto graduado de tres niveles (`PASS`, `WARNING`, `HARD_FAIL`) basado en la magnitud y criticidad de la desviación topológica. Queda prohibida la evaluación binaria (pasa/falla) y la comparación byte-a-byte (snapshotting).
* El veredicto de regresión **DEBE** basarse en un doble mecanismo complementario: (1) NSS ponderado por criticidad para desviación gradual, y (2) regla absoluta de pérdida de nodo `CRITICAL` para protección de contenido científico primario.
* La evaluación **DEBE** verificar la integridad criptográfica del oráculo (`oracle_hash`), el estado de ciclo de vida (`ground_truth_state == SEALED`) y la completitud biyectiva antes de evaluar. Si cualquier verificación falla, la evaluación **DEBE** abortar inmediatamente (Fail-Fast).
* El runtime AST **DEBE** generarse mediante el composition root del pipeline de producción. Queda prohibida la creación de un pipeline separado para regresión y el uso de parsers legacy o rutas alternativas.
* El reporte de regresión **DEBE** ser determinista y consumible por CI/CD, incluyendo el veredicto, las métricas que lo fundamentan y la identidad del oráculo utilizado.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de evaluación topológica del sistema carece de un contrato formal de veredicto graduado. Aunque el motor de distancia de edición de árboles y los evaluadores de recuperación semántica existen y son funcionales, no existe un mecanismo que:
1. Emita veredictos graduados (`PASS` / `WARNING` / `HARD_FAIL`) basados en la magnitud y criticidad de la desviación.
2. Conecte el oráculo sellado (`SealedOracle`) con la evaluación topológica.
3. Verifique la integridad criptográfica del oráculo antes de evaluar.
4. Genere el runtime AST mediante el pipeline de producción real.

Las clases de defectos identificadas son:

1. **Ausencia de veredicto graduado:** No existe mecanismo que emita juicios diferenciados basados en la magnitud de la desviación topológica. Toda divergencia se trata como una métrica continua sin veredicto explícito.

2. **Ausencia de conexión SealedOracle→evaluación:** El oráculo sellado (`SealedOracle`) no se consume como referencia canónica de evaluación. Los evaluadores operan sobre Ground Truth genérico sin verificación de integridad criptográfica.

3. **Ausencia de verificación previa:** No se verifica `oracle_hash`, `ground_truth_state` ni completitud biyectiva antes de evaluar. Riesgo de evaluar contra un oráculo mutado, no sellado o incompleto.

4. **Ausencia de entry point de regresión:** No existe entry point dedicado que ejecute la evaluación de regresión del runtime contra el oráculo sellado reutilizando el composition root del pipeline de producción.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-4.2-002` / `GAP-4.2-02` (P0 — Crítico):** Ausencia total de mecanismo de veredicto graduado. No existe `RegressionVerdict` ni ningún modelo de veredicto. DC-07 del ADR Maestro §8 permanece sin materialización operativa.

* **`E-4.3-001` / `GAP-4.3-01` (P0 — Crítico):** Ausencia total de conexión `SealedOracle` → evaluación topológica. Ningún componente de `core/benchmark/topology/` ni de `tools/evaluation/` consume `SealedOracle` ni lo conecta con los evaluadores topológicos.

* **`GAP-4.3-02` (P0 — Crítico):** Ausencia de verificación de `oracle_hash` antes de evaluar. Riesgo de evaluar contra un oráculo mutado en disco.

* **`GAP-4.3-04` (P0 — Crítico):** Ausencia de entry point de regresión. No existe CLI tool que ejecute la evaluación de regresión del runtime contra el oráculo sellado.

* **`GAP-4.3-05` (P1 — Alto):** Ausencia de verificación de completitud biyectiva en contexto de evaluación. `BaselineCompletenessVerifier` existe pero no se usa antes de evaluar.

* **`E-4.5-004` (N/A — Positivo):** Composition root `build_extraction_pipeline()` confirmado como reutilizable para regresión. No se requiere pipeline separado.

* **`E-4.5-005` (N/A — Positivo):** `core/benchmark/__main__.py` (benchmark de LLMs de Fase 16.10) usa `build_extraction_pipeline()`, confirmando que el composition root es funcional y reutilizable.

* **`E-4.1-005` (P1 — Alto):** `UnitCostContext` aplica costos unitarios sin ponderación. Insuficiente para regresión científica graduada. NADR-F17BIS-18 resuelve esto con `CriticalityAwareCostContext`.

* **`DC-07` (ADR Maestro §8):** "Reglas de Regresión Topológica: ¿Bajo qué condiciones específicas de desalineación topológica o divergencia de contenido la suite de integración emite un HARD FAIL vs. un WARNING?" — Decision Candidate declarado en el ADR Maestro, sin materialización operativa.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Veredicto de Regresión Graduado

1. El veredicto de regresión **MUST** definir exactamente tres niveles: `PASS`, `WARNING` y `HARD_FAIL`. No se permiten niveles adicionales ni sub-niveles.

2. El veredicto de regresión **MUST** emitirse por documento individual y por corpus completo.

3. El veredicto por corpus **MUST** ser el peor veredicto de todos los documentos individuales del corpus. Si al menos un documento es `HARD_FAIL`, el corpus es `HARD_FAIL`. Si al menos un documento es `WARNING` y ninguno es `HARD_FAIL`, el corpus es `WARNING`. Solo si todos los documentos son `PASS`, el corpus es `PASS`.

4. El veredicto `HARD_FAIL` **MUST** emitirse ante cualquiera de las siguientes condiciones:
   * Pérdida de cualquier nodo clasificado como `CRITICAL` (definido por NADR-F17BIS-18).
   * NSS ponderado por criticidad inferior al umbral crítico (definido en §5.3).

5. El veredicto `WARNING` **MUST** emitirse ante cualquiera de las siguientes condiciones, siempre que no se cumpla ninguna condición de `HARD_FAIL`:
   * Pérdida de nodos clasificados como `WARNING` que supera el umbral configurable de proporción o cantidad.
   * NSS ponderado por criticidad entre el umbral crítico y el umbral de advertencia.

6. El veredicto `PASS` **MUST** emitirse cuando:
   * No se pierde ningún nodo clasificado como `CRITICAL`.
   * La pérdida de nodos clasificados como `WARNING` no supera el umbral configurable.
   * El NSS ponderado por criticidad es superior al umbral de advertencia.

7. La pérdida de nodos clasificados como `INFO` **MUST NOT** causar un veredicto de fallo (`WARNING` o `HARD_FAIL`). La pérdida de nodos `INFO` **MAY** registrarse como observación en el reporte de regresión.

### 5.2 Doble Mecanismo de Protección

8. El veredicto de regresión **MUST** basarse en un doble mecanismo complementario:
   * **Mecanismo 1 (protección gradual):** NSS ponderado por criticidad, que captura la desviación estructural gradual.
   * **Mecanismo 2 (protección absoluta):** Regla de pérdida de nodo `CRITICAL`, que emite `HARD_FAIL` independiente del NSS.

9. El Mecanismo 2 (regla absoluta de pérdida `CRITICAL`) **MUST** tener precedencia sobre el Mecanismo 1 (NSS ponderado). Si se pierde un nodo `CRITICAL`, el veredicto es `HARD_FAIL` sin importar el valor del NSS.

10. Ambos mecanismos **MUST** evaluarse antes de emitir el veredicto final. El veredicto final es el peor resultado de ambos mecanismos.

11. El NSS ponderado **MUST** utilizar el `CriticalityAwareCostContext` (definido por NADR-F17BIS-18) como contexto de costos de edición. **MUST NOT** utilizar el `UnitCostContext` para evaluación de regresión.

### 5.3 Umbrales de NSS

12. Los umbrales de NSS **MUST** ser configurables mediante una política inyectada. Los valores concretos **MUST NOT** estar hardcodeados en el motor de evaluación.

13. Los umbrales de NSS **MUST** tener valores por defecto definidos y documentados. Los valores por defecto constituyen una propuesta inicial sujeta a validación empírica sobre la baseline canónica.

14. Los umbrales de NSS **MUST** ser deterministas. Dados los mismos inputs (runtime AST, oráculo sellado, umbrales), el veredicto emitido **MUST** ser idéntico en cualquier ejecución.

### 5.4 Prerrequisitos de Integridad Pre-Evaluación

15. Antes de evaluar el runtime contra el oráculo sellado, el sistema **MUST** verificar la integridad criptográfica del oráculo mediante el cálculo de la identidad semántica (`OracleSemanticIdentityCalculator`) comparado contra el `oracle_hash` almacenado en el manifiesto.

16. Antes de evaluar, el sistema **MUST** verificar que el estado de ciclo de vida del documento es `ground_truth_state == SEALED`. Un oráculo que no esté en estado `SEALED` **MUST NOT** ser utilizado como referencia de evaluación.

17. Antes de evaluar, el sistema **MUST** verificar la completitud biyectiva del corpus (manifest ↔ oráculos) mediante el verificador de completitud (`BaselineCompletenessVerifier`).

18. Si cualquiera de las verificaciones anteriores (Reglas 15-17) falla, el sistema **MUST** abortar inmediatamente (Fail-Fast). **MUST NOT** degradar silenciosamente ni evaluar contra un oráculo no verificado.

19. El error emitido ante una verificación fallida **MUST** ser un error explícito y tipado, nunca un warning silencioso. Cada tipo de fallo **MUST** tener su propio tipo de error para permitir diagnóstico preciso.

### 5.5 Reutilización del Pipeline de Producción

20. El runtime AST **MUST** generarse mediante el composition root del pipeline de producción. **MUST NOT** crearse un pipeline de extracción separado para regresión.

21. La evaluación de regresión **MUST NOT** utilizar parsers legacy ni rutas alternativas de extracción. El único camino de extracción válido es el composition root del pipeline de producción.

22. El runtime AST **MUST** ser determinista. Dados los mismos inputs (PDF de entrada, configuración del pipeline), el AST generado **MUST** ser idéntico en cualquier ejecución.

### 5.6 Interacción con Recall Semántico

23. La evaluación de recall semántico **MUST** ponderar los resultados por criticidad de nodo. Un recall bajo de nodos `CRITICAL` **MUST** tratarse con mayor severidad que un recall bajo de nodos `INFO`.

24. El recall **MUST** evaluarse por tipo de nodo, utilizando la taxonomía de criticidad definida por NADR-F17BIS-18 para ponderar la severidad de las divergencias.

25. La evaluación de regresión **MUST** asumir que el framing del identificador de matching es inyectivo (garantizado por NADR-F17BIS-17). Si el framing es ambiguo, la evaluación **MAY** producir falsos positivos o negativos, pero esa responsabilidad pertenece a NADR-17 y NADR-18, no a este NADR.

### 5.7 Reporte de Regresión

26. El reporte de regresión **MUST** ser determinista. Dados los mismos inputs, el reporte generado **MUST** ser idéntico en cualquier ejecución.

27. El reporte de regresión **MUST** incluir, como mínimo:
   * El veredicto por documento y por corpus.
   * El NSS calculado y los umbrales utilizados.
   * Los nodos `CRITICAL` perdidos (si aplica).
   * La identidad del oráculo utilizado (`oracle_hash`, `document_id`, `ground_truth_state`).

28. El reporte de regresión **MUST** ser emitido en formato estructurado (JSON) para consumo programático por CI/CD. **SHOULD** incluir un formato legible para humanos (Markdown) como salida secundaria.

29. El reporte de regresión **MUST NOT** incluir marcas de tiempo físicas ni factores no deterministas que rompan la reproducibilidad del reporte. Si se requiere una marca temporal, **MUST** ser inyectada como parámetro externo.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La evaluación de regresión deja de ser una comparación binaria (pasa/falla) o un snapshot rígido (byte-a-byte) y pasa a ser una evaluación científica graduada basada en la magnitud y criticidad de la desviación topológica.

* El doble mecanismo de protección garantiza que la pérdida de contenido científico primario (nodos `CRITICAL`) siempre se detecte como `HARD_FAIL`, independientemente de métricas agregadas. Esto cierra la brecha donde un NSS alto podría enmascarar la pérdida de una ecuación entre miles de nodos.

* La verificación criptográfica previa garantiza que la evaluación siempre se ejecute contra un oráculo íntegro, sellado y completo. Elimina el riesgo de evaluar contra un oráculo mutado, no sellado o incompleto.

* La reutilización del composition root del pipeline de producción garantiza que el runtime AST evaluado es exactamente el mismo que se genera en producción, eliminando la divergencia entre "lo que se evalúa" y "lo que se ejecuta".

* El reporte de regresión determinista y consumible por CI/CD habilita la integración futura con compuertas de regresión automatizadas (Fase 6 — Continuous Verification).

* El veredicto por corpus como "peor veredicto de todos los documentos" garantiza que una sola regresión crítica en un documento bloquee todo el corpus, evitando que regresiones locales se diluyan en promedios.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el veredicto de regresión tiene exactamente tres niveles (`PASS`, `WARNING`, `HARD_FAIL`).
  * Verificación de que los umbrales de NSS son configurables mediante política inyectada y no están hardcodeados.
  * Verificación de que las verificaciones de integridad (Reglas 15-17) se ejecutan antes de la evaluación.
  * Verificación de que el runtime AST se genera mediante el composition root del pipeline de producción.
  * Verificación de que el reporte de regresión es determinista (mismos inputs → mismo reporte).
  * Verificación de que el veredicto por corpus es el peor veredicto de todos los documentos.

* **Validation (dinámica/comportamental):**
  * Validación de que la pérdida de un nodo `CRITICAL` emite `HARD_FAIL` independientemente del NSS.
  * Validación de que la pérdida de nodos `WARNING` emite `WARNING` cuando supera el umbral configurable.
  * Validación de que la pérdida de nodos `INFO` no causa fallo.
  * Validación de que el NSS ponderado por criticidad produce veredictos coherentes con el impacto científico.
  * Validación de que la evaluación aborta con error explícito si el oráculo no está en estado `SEALED`.
  * Validación de que la evaluación aborta con error explícito si el `oracle_hash` no coincide.
  * Validación de que la evaluación aborta con error explícito si la completitud biyectiva falla.
  * Validación de que el reporte de regresión es consumible por CI/CD (formato JSON estructurado).
  * Validación de que el veredicto por corpus es el peor veredicto de todos los documentos.
  * Validación empírica de los umbrales de NSS por defecto sobre la baseline canónica, confirmando que producen una gradación coherente con el impacto científico esperado.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa el Decision Candidate DC-07 declarado en el ADR Maestro §8 y la Dimensión 3 (REGRESIÓN) del ADR Maestro §3. |
| `ADR_F17-BIS_04` | Este NADR implementa la capacidad de regresión graduada definida en la Arquitectura Objetivo del ADR de Fase 4 §7. |
| `NADR-F17BIS-12` | **Dependencia directa:** Este NADR consume la ontología del `SealedOracle` definida por NADR-12. |
| `NADR-F17BIS-13` | **Dependencia directa:** Este NADR consume `BaselineCompletenessVerifier` para verificar la completitud biyectiva antes de evaluar. |
| `NADR-F17BIS-14` | **Dependencia directa:** Este NADR consume la asimetría de puertos para la lectura del oráculo en runtime. |
| `NADR-F17BIS-16` | **Dependencia directa:** Este NADR consume `OracleSemanticIdentityCalculator` para verificar la integridad criptográfica del oráculo. |
| `NADR-F17BIS-17` | **Dependencia directa:** Este NADR asume que el framing del identificador de matching es inyectivo (garantizado por NADR-17). |
| `NADR-F17BIS-18` | **Dependencia directa:** Este NADR consume la taxonomía de criticidad y los pesos definidos por NADR-18 para ponderar el NSS y emitir veredictos. |
| `NADR-F17BIS-20` | **Influencia:** Este NADR habilita la semántica de evaluación graduada definida por NADR-20. |
| `Fase 6 (Continuous Verification)` | **Influencia:** Este NADR habilita la integración de la regresión en CI/CD mediante el reporte determinista y consumible. |
| `PHASE_17BIS_FASE4_EXECUTION_PLAN` | Las tareas de implementación de este NADR se secuencian en el Execution Plan de Fase 4. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la taxonomía de criticidad de nodos ni los pesos de criticidad. Esos son responsabilidad de `NADR-F17BIS-18` (Taxonomía de Criticidad de Nodos).

* **No gobierna** la semántica de evaluación graduada (qué significa conceptualmente "regresión graduada" vs "snapshotting binario"). Esa semántica es responsabilidad de `NADR-F17BIS-20` (Semántica de Evaluación Graduada).

* **No gobierna** la ontología del AST ni la definición de tipos de nodo. La ontología del AST es responsabilidad de `NADR-F17BIS-01` (Canonical AST Representation).

* **No gobierna** la ontología del oráculo sellado ni el ciclo de vida del Ground Truth. Esas ontologías son responsabilidad de `NADR-F17BIS-12` (Ground Truth Oracle Ontology).

* **No gobierna** la validez estructural del oráculo ni la completitud biyectiva como capacidad de dominio. Esas son responsabilidad de `NADR-F17BIS-13` (Ground Truth Validity & Baseline Completeness). Este NADR solo CONSUME esas capacidades como prerrequisito.

* **No gobierna** la asimetría de puertos ni la autoridad de sellado. Esas son responsabilidad de `NADR-F17BIS-14` (Runtime Port Asymmetry & Sealing Authority). Este NADR solo CONSUME el puerto de lectura.

* **No gobierna** la identidad semántica del oráculo ni el cálculo del `oracle_hash`. Esa es responsabilidad de `NADR-F17BIS-16` (Cryptographic Identity Semantics). Este NADR solo CONSUME el calculador.

* **No gobierna** el framing del identificador de matching ni la inyectividad del framing. Esa es responsabilidad de `NADR-F17BIS-17` (Identity Encoding Integrity). Este NADR ASUME que el framing es inyectivo.

* **No gobierna** la implementación concreta del motor de distancia de edición de árboles (`ZhangShashaEngine`) ni de los evaluadores de recuperación semántica (`EntityRecallEvaluator`). Esos son componentes reutilizables de la infraestructura existente (HITO_4.1).

* **No gobierna** la integración de compuertas de regresión en CI/CD. Esa integración es responsabilidad de la **Fase 6** (Continuous Verification). Este NADR solo habilita esa integración mediante el reporte determinista y consumible.

* **No gobierna** la materialización en disco de la baseline canónica ni el protocolo de sellado criptográfico. Esas capacidades son responsabilidad de la **Fase 5** (Baseline Certification).

* **No prescribe** tareas de implementación ni Definition of Done. Esas responsabilidades son del **Execution Plan**.

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.