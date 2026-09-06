# NADR-F17-BIS-24: Certification Tooling Integrity, Failure Semantics & Execution Safety

## 1. METADATA

* **Decision ID:** `NADR-F17-BIS-24`
* **Título:** Certification Tooling Integrity, Failure Semantics & Execution Safety
* **Clase de Decisión:** `OPERATIONAL / GOVERNANCE`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.2.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 17-BIS — Fase 5 (Baseline Certification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-F5-05 (Certification Tooling Integrity & Execution Safety) — Establece las reglas normativas que garantizan que el tooling de certificación ejecuta el contrato de certificación sin falsos positivos, sin silenciamiento de errores, sin certificaciones parciales y con semántica de fallo uniforme y determinista.
* **Evidencia Forense:** `DF-18` (4 entry points con exit 0 ante fallo crítico), `GAP-5.2-01` (semántica de fallo heterogénea), `GAP-5.0-03` / `E-5.2-005` (6 de 8 entry points con rutas hardcoded), `GAP-5.2-05` / `E-5.2-009` (Certification Boundary Integrity violation en `sanitize_ground_truth_types.py`), `E-5.2-006` a `E-5.2-008` (persistencia secundaria no atómica), `E-5.2-010` (fsync silenciado), `HITO 5.2 v1.1.0` (Operational Integrity Audit)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_05` (FROZEN, D8), `ENGINEERING_PRINCIPLES` (FROZEN, §IV Cero Fallos Silenciosos), `NADR-F17BIS-20` (Corpus Qualification), `NADR-F17BIS-21` (Ground Truth Eligibility & Sealing), `NADR-F17BIS-22` (Canonical Evaluation Configuration), `NADR-F17BIS-23` (Scientific Calibration & Provenance), `NADR-F17BIS-19` (Regresión Topológica Graduada — dependencia operacional)
  * **Influencia:** `PHASE_17BIS_FASE5_EXECUTION_PLAN`, `FASE_6_CONTINUOUS_VERIFICATION` (CI/CD integration)
  * **Conflictúa con:** Exit code 0 tras fallo crítico, configuración implícita del corpus, certificación parcial, silenciamiento de errores, mutación de oráculos sellados, evidencia de certificación incompleta.
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 35 reglas normativas en 8 dominios. |
| 1.1.0 | 2026-09-05 | Corrección menor: Changelog v1.0.0 corregido (33 → 35 reglas). |
| 1.2.0 | 2026-09-05 | **FROZEN** **Hardening normativo:** (1) R25/R26: eliminada excepción de "autorización explícita" para Sealed GTs — Sealed es inmutable sin excepción, cualquier corrección produce nuevo artefacto/versionado conforme a NADR-21; (2) R4/R5: CERTIFIED definido como condición compuesta explícita (execution outcome + scientific result + evidence + invariants); (3) R7: separado PREFLIGHT (pre-condiciones) de POST-RUN VALIDATION (post-condiciones); (4) R32: determinismo operacional reformulado con "condiciones de ejecución certificables" (corpus + configuration + parameters + execution version); (5) R33: idempotencia lógica reformulada (no "filesystem limpio" sino "no reutilización no determinista de residuos"); (6) R29: corpus_identity y manifest_identity explícitamente diferenciados; (7) Relación con NADR-19: "influencia bidireccional" → "dependencia operacional"; (8) Consecuencias: "elimina el riesgo" → "elimina el riesgo identificado de"; (9) §7: agregadas verificaciones de invariante de estado (mutual exclusión de resultados). |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin semántica de fallo uniforme, el tooling de certificación puede declarar éxito falso (exit 0) tras un fallo crítico, comprometiendo toda la cadena de certificación y los Regression Gates de Fase 6.
* **Mantenibilidad:** 4 — Sin contrato de ejecución explícito y sin preflight, el diagnóstico de fallos de certificación es ambiguo y propenso a interpretaciones erróneas.
* **Recuperabilidad:** 4 — Sin semántica de recuperación idempotente, la re-ejecución tras fallo parcial puede producir artefactos inconsistentes o certificación corrupta.
* **Seguridad:** 3 — Sin protección de frontera de certificación, mecanismos de migración pueden sobrescribir oráculos sellados (GAP-5.2-05), comprometiendo la inmutabilidad de la baseline.
* **Financiero:** 3 — Una certificación falsa positiva en CI puede permitir merge de código que degrada silenciosamente la calidad, con costo de detección tardía significativo.
* **Total Score: 19/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**El tooling de certificación MUST NOT producir un estado de certificación exitoso cuando alguna precondición normativa, unidad obligatoria de evaluación, integridad requerida o evidencia obligatoria no haya sido satisfecha y verificada; y un fallo parcial de ejecución MAY ser tolerado para diagnóstico y recuperación, pero MUST NOT ser interpretado como una certificación parcial o exitosa.**

En consecuencia:
* Ningún entry point de certificación puede producir exit code 0 cuando exista un fallo que invalide la certificación.
* Ninguna certificación puede ejecutarse contra un corpus implícito, accidental o no verificado.
* Ningún mecanismo de certificación puede modificar un oráculo sellado. La inmutabilidad de Sealed es absoluta conforme a NADR-F17BIS-21.
* Ninguna certificación puede declararse completa si falta evidencia obligatoria.
* La distinción entre "certificación ejecutada con resultado rechazado" y "tooling falló" **MUST** ser explícita y verificable.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de certificación requiere que el tooling que ejecuta la certificación tenga integridad operacional verificable. La auditoría forense (HITO 5.2) demostró que el estado actual del repositorio presenta cinco clases de deficiencias que impiden confiar en los resultados del tooling de certificación:

1. **Semántica de fallo heterogénea (DF-18):** Cuatro entry points de certificación (`freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`) tienen múltiples caminos de error que terminan en exit 0, violando ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos).

2. **Configuración implícita del corpus (GAP-5.0-03):** Seis de ocho entry points tienen rutas hardcoded sin configuración explícita, lo que impide la integración en CI y permite ejecución contra corpus accidental.

3. **Certification Boundary Integrity violation (GAP-5.2-05):** El mecanismo `sanitize_ground_truth_types.py` puede sobrescribir Ground Truths sellados sin verificar el estado de sellado, constituyendo una violación de la frontera de certificación.

4. **Persistencia secundaria no atómica:** La persistencia de reportes, candidatos y artefactos de benchmark usa escritura no atómica (`json.dump`, `write_text`), lo que permite estados parciales tras fallo.

5. **Durabilidad ante power-loss parcial:** El `fsync` está silenciado con `except: pass` en operaciones críticas, degradando la durabilidad ante fallo de proceso.

### 4.2 Manifestación concreta identificada por la auditoría

* **`DF-18` / `GAP-5.2-01` (P1 — Alto):** Cuatro entry points (`freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`) tienen múltiples caminos de error que terminan en exit 0. Un proceso de certificación fallido puede ser interpretado como exitoso por CI.

* **`GAP-5.0-03` / `E-5.2-005` (P1 — Alto):** Seis de ocho entry points (`bootstrap_corpus.py`, `freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_candidates.py`, `generate_pymupdf_candidate.py`, `sanitize_ground_truth_types.py`) tienen rutas hardcoded sin configuración explícita. La integración en CI requiere modificación de código.

* **`GAP-5.2-05` / `E-5.2-009` (P1 — Alto):** `sanitize_ground_truth_types.py` puede sobrescribir Ground Truths sellados sin verificar el estado de sellado. Constituye una Certification Boundary Integrity violation.

* **`E-5.2-006` a `E-5.2-008` (P2 — Medio):** `BenchmarkPersistenceGateway`, `generate_candidates.py` y `run_regression.py` usan escritura no atómica (`json.dump`, `write_text`), permitiendo estados parciales tras fallo.

* **`E-5.2-010` (P2 — Medio):** `fsync` silenciado con `except (AttributeError, OSError): pass` en `write_ast_json_atomic()` y `save_manifest_dto()`, degradando durabilidad ante power-loss.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Certification Execution Contract

1. Toda ejecución de certificación **MUST** tener un contrato de ejecución explícito y verificable que defina: inputs requeridos, precondiciones normativas, postcondiciones de éxito, y condiciones de fallo.

2. El contrato de ejecución **MUST** identificar inequívocamente: corpus identity (SHA-256 del manifest), configuration identity (configuración canónica del motor), frozen parameters identity (parámetros calibrados congelados), y execution mode.

3. Una ejecución de certificación **MUST NOT** comenzar si las precondiciones normativas definidas en §5.2 (Preflight) no están satisfechas. El incumplimiento de precondiciones **MUST** abortar la ejecución antes de cualquier operación de certificación.

4. Una ejecución de certificación **MUST** producir exactamente uno de los siguientes resultados lógicos: (a) CERTIFIED, (b) REJECTED, (c) EXECUTION_FAILURE. **CERTIFIED es una condición compuesta que requiere simultáneamente:** (i) ejecución completada exitosamente (execution outcome = SUCCESS), (ii) resultado científico de evaluación aceptado (scientific result = ACCEPTED), (iii) evidencia completa verificada, (iv) todas las invariantes de certificación satisfechas. La ausencia de cualquier componente **MUST** impedir el estado CERTIFIED.

5. El resultado lógico de la ejecución **MUST** ser distinguible del resultado científico de la evaluación. La arquitectura distingue tres capas: (a) Execution outcome (SUCCESS / EXECUTION_FAILURE), (b) Scientific evaluation result (ACCEPTED / REJECTED), (c) Certification status (CERTIFIED / REJECTED / EXECUTION_FAILURE). La mezcla de estas capas **MUST NOT** ser permitida.

### 5.2 Preflight & Preconditions

6. Toda ejecución de certificación **MUST** ejecutar una fase PREFLIGHT antes de la fase RUN. El PREFLIGHT **MUST** verificar todas las precondiciones normativas que existen antes de la ejecución.

7. El PREFLIGHT **MUST** verificar, como mínimo: (a) corpus existe y su identidad coincide con la declarada; (b) manifest está en formato vigente y su hash es verificable; (c) todos los Ground Truths requeridos existen y están en estado Sealed; (d) los oracle_hash son verificables; (e) la configuración del motor es la canónica vigente; (f) los parámetros están congelados; (g) el calibration provenance requerido está disponible; (h) no existe leakage entre particiones prohibidas.

8. Si cualquier precondición del PREFLIGHT no se satisface, la ejecución **MUST** abortar con resultado EXECUTION_FAILURE y mensaje explícito identificando la precondición violada. La ejecución **MUST NOT** continuar con precondiciones no satisfechas.

9. El PREFLIGHT **MUST** ser idempotente: ejecutar PREFLIGHT múltiples veces sobre el mismo estado **MUST** producir el mismo resultado.

### 5.3 Explicit Configuration & Identity

10. Toda ejecución de certificación **MUST** recibir el corpus como entrada explícita. La configuración implícita del corpus (rutas hardcoded, valores por defecto no declarados) **MUST NOT** ser permitida.

11. La identidad del corpus utilizado **MUST** ser verificada contra la identidad declarada antes de la ejecución. Si la identidad verificada no coincide con la declarada, la ejecución **MUST** abortar con EXECUTION_FAILURE.

12. La configuración canónica del motor de evaluación (definida por NADR-F17BIS-22) **MUST NOT** ser mutada durante la ejecución de certificación. Cualquier tentativa de mutación **MUST** abortar la ejecución.

13. Los parámetros congelados (definidos por NADR-F17BIS-23) **MUST NOT** ser modificados durante la ejecución de certificación. Cualquier tentativa de modificación **MUST** abortar la ejecución.

14. El fallback silencioso a valores por defecto cuando la configuración es inválida o ausente **MUST NOT** ser permitido. La ausencia o invalidez de configuración **MUST** producir EXECUTION_FAILURE. Los valores por defecto que estén declarados, normados, sean deterministas, y formen parte de la configuration identity **MAY** ser permitidos.

### 5.4 Failure Semantics & Exit Contract

15. Todo entry point que forme parte de la certificación **MUST** implementar una semántica de salida uniforme y determinista. La taxonomía de códigos de salida **MUST** distinguir al menos tres categorías: (a) ejecución completada con certificación válida, (b) ejecución completada con certificación rechazada (resultado científico válido), (c) fallo de ejecución/configuración/integridad (resultado inválido).

16. Ningún camino de error que invalide la certificación **MUST** producir un código de salida de la categoría (a). La violación de esta regla constituye un falso positivo operacional.

17. La distinción entre "certificación rechazada" (resultado científico válido) y "tooling falló" (resultado inválido) **MUST** ser preservada en el código de salida. La mezcla de ambas categorías **MUST NOT** ser permitida.

18. Todo error que produzca un código de salida de la categoría (c) **MUST** incluir un mensaje de error explícito, indexable y trazable que identifique la causa raíz del fallo. El silenciamiento de errores **MUST NOT** ser permitido (ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos).

19. Las excepciones no capturadas que propagan hasta el nivel del entry point **MUST** ser traducidas a un código de salida de la categoría (c) con mensaje de error explícito. La propagación de stack traces sin traducción **MUST NOT** ser el mecanismo primario de señalización de fallo.

### 5.5 Partial Failure & Certification Atomicity

20. **Regla nuclear:** Un fallo parcial de ejecución **MAY** ser tolerado para diagnóstico y recuperación, pero **MUST NOT** ser interpretado como una certificación parcial o exitosa.

21. Una certificación que no haya completado todas las unidades requeridas por el corpus de evaluación **MUST NOT** producir estado CERTIFIED. La certificación parcial **MUST NOT** ser permitida.

22. El tooling de certificación **MAY** tolerar fallos parciales a nivel de documento individual para diagnóstico (ejemplo: 10 documentos, 7 evaluados exitosamente, 3 fallidos), pero el resultado agregado **MUST** ser EXECUTION_FAILURE si cualquier unidad obligatoria no pudo ser evaluada.

23. La distinción entre "tolerancia a fallos parciales para diagnóstico" y "certificación parcial" **MUST** ser verificable en el contrato de ejecución y en el código de salida.

24. El resultado lógico de la certificación **MUST** ser atómico a nivel de baseline: o se certifica la baseline completa, o no se certifica nada. La certificación incremental o progresiva **MUST NOT** ser permitida.

### 5.6 Certification Boundary Integrity

25. Los Ground Truths en estado Sealed **MUST NOT** ser modificados por el tooling de certificación. La inmutabilidad de Sealed es absoluta conforme a NADR-F17BIS-21 R19. Cualquier corrección o migración posterior a Sealed **MUST** producir un nuevo artefacto/versionado y atravesar nuevamente el lifecycle de elegibilidad y sealing definido por NADR-F17BIS-21. No existe "autorización explícita" que permita mutar un Sealed Ground Truth.

26. Todo mecanismo que pueda modificar Ground Truths (incluyendo migraciones, sanitizaciones, regeneraciones) **MUST** verificar el estado de sellado antes de cualquier modificación. La modificación sin verificación de estado **MUST NOT** ser permitida. El tooling de certificación no tiene autoridad de mutación sobre Ground Truths; los mecanismos de migración/corrección **MUST** operar fuera de la ejecución certificante y bajo las reglas de NADR-F17BIS-21.

27. Ningún artefacto generado durante la certificación (reportes, candidatos, evaluaciones) **MUST** adquirir autoridad de Ground Truth simplemente por existir. La frontera entre Scientific Truth, Generated Output y Certification Evidence **MUST** ser preservada.

28. Las transiciones de estado del Ground Truth (Draft → Audited → Validated → Sealed) **MUST** ser gobernadas exclusivamente por la autoridad de lifecycle definida por NADR-F17BIS-21. El tooling de certificación **MUST NOT** ejecutar transiciones de estado fuera de su autoridad.

### 5.7 Evidence Completeness & Auditability

29. Una certificación **MUST** producir evidencia completa que incluya, como mínimo: corpus identity, manifest identity (entidad distinta de corpus identity conforme a NADR-F17BIS-20), evaluation configuration identity, frozen parameters identity, evaluation provenance, per-document results, y aggregate result.

30. Si falta cualquier elemento de evidencia obligatoria, la certificación **MUST NOT** declararse completa. El resultado **MUST** ser EXECUTION_FAILURE con identificación del elemento faltante.

31. Toda evidencia de certificación **MUST** ser auditable: un verificador externo **MUST** poder reconstruir qué corpus, configuración, parámetros y resultados fueron utilizados en la certificación, sin necesidad de ejecutar nuevamente el tooling.

### 5.8 Determinism, Idempotency & Recovery

32. Dadas las mismas condiciones de ejecución certificables (corpus identity, configuration identity, frozen parameters identity, execution version/configuration), el tooling de certificación **MUST** producir un resultado operacional determinista. La distinción entre "determinismo operacional" (este NADR) y "reproducibilidad científica" (NADR-F17BIS-23) **MUST** ser preservada.

33. La re-ejecución de una certificación fallida **MUST** ser idempotente a nivel lógico: la segunda ejecución sobre el mismo estado inicial **MUST** producir el mismo resultado que la primera, y no podrá incorporar, reutilizar o mezclar de forma no determinista artefactos residuales de ejecuciones anteriores.

34. Cuando una ejecución falla parcialmente, el estado resultante **MUST** permitir determinar: (a) qué unidades fueron evaluadas, (b) qué artefactos quedaron en disco, (c) si son reutilizables o deben descartarse, (d) si una re-ejecución puede reemplazar la primera. La ambigüedad sobre el estado post-fallo **MUST NOT** ser permitida.

35. La atomicidad física completa del filesystem **MUST NOT** ser prometida si la infraestructura no la garantiza. El NADR exige resultado lógico atómico (todo-o-nada) a nivel de certificación; los detalles físicos de persistencia pertenecen al contrato de infraestructura correspondiente.

### 5.9 Post-Run Certification Validation

36. Tras completar la fase RUN, el tooling **MUST** ejecutar una fase POST-RUN VALIDATION que verifique las post-condiciones de certificación: (a) Evaluation Provenance Record completo y verificable; (b) per-document evidence presente; (c) aggregate result presente; (d) todos los elementos de evidencia obligatoria (R29) satisfechos.

37. Si la POST-RUN VALIDATION no se satisface, el resultado **MUST** ser EXECUTION_FAILURE con identificación del elemento faltante. La certificación con evidencia incompleta **MUST NOT** producir estado CERTIFIED.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **Semántica de fallo uniforme:** Todo entry point de certificación implementa semántica de salida uniforme y determinista, eliminando el riesgo identificado de falsos positivos operacionales (exit 0 tras fallo crítico). Esto habilita la integración confiable en CI.

* **Configuración explícita verificable:** El corpus utilizado en la certificación es explícito y su identidad es verificada antes de la ejecución. Esto elimina el riesgo identificado de certificación contra corpus accidental y habilita la integración en CI sin modificación de código.

* **Certification Boundary Integrity preservada:** Ningún mecanismo puede modificar oráculos sellados. La inmutabilidad de Sealed es absoluta. Cualquier corrección produce un nuevo artefacto/versionado conforme a NADR-21. Esto garantiza la inmutabilidad de la baseline científica y resuelve GAP-5.2-05.

* **Certificación atómica:** La certificación es atómica a nivel de baseline (todo-o-nada). Los fallos parciales son tolerados para diagnóstico pero nunca interpretados como certificación parcial. Esto elimina el riesgo identificado de que una ejecución incompleta sea interpretada como certificación válida.

* **Evidencia auditable completa:** Toda certificación produce evidencia completa y auditable. Esto habilita la verificación forense posterior sin necesidad de re-ejecución.

* **Distinción entre resultado científico y fallo operacional:** El tooling distingue explícitamente entre "certificación rechazada" (resultado científico válido) y "tooling falló" (resultado inválido). Esto elimina la ambigüedad identificada en la interpretación de resultados.

* **Recuperación idempotente:** La re-ejecución tras fallo es idempotente a nivel lógico y el estado post-fallo es determinable. Esto habilita la recuperación confiable sin acumulación de estado corrupto.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que todo entry point de certificación implementa semántica de salida uniforme con al menos tres categorías.
  * Verificación de que ningún camino de error crítico produce código de salida de la categoría "certificación válida".
  * Verificación de que todo entry point ejecuta PREFLIGHT antes de RUN.
  * Verificación de que ningún entry point acepta configuración implícita de corpus (análisis estático de rutas hardcoded).
  * Verificación de que ningún mecanismo modifica Ground Truths sellados sin verificación de estado.
  * Verificación de que toda certificación produce evidencia completa con los 7 elementos mínimos.
  * Verificación de que el resultado lógico es atómico a nivel de baseline.
  * Verificación de que ninguna ruta de certificación puede alcanzar CERTIFIED sin haber satisfecho todas las precondiciones y postcondiciones normativas.
  * Verificación de que CERTIFIED, REJECTED y EXECUTION_FAILURE no pueden producirse simultáneamente ni ser ambiguamente mapeados.

* **Validation (dinámica/comportamental):**
  * Fault injection: ejecutar certificación con oráculo faltante y verificar que produce EXECUTION_FAILURE (no CERTIFIED).
  * Fault injection: ejecutar certificación con manifest corrupto y verificar que produce EXECUTION_FAILURE (no CERTIFIED).
  * Fault injection: ejecutar certificación con corpus incorrecto (SHA-256 distinto) y verificar que PREFLIGHT aborta.
  * Fault injection: ejecutar certificación con parámetros no congelados y verificar que PREFLIGHT aborta.
  * Fault injection: tentativa de modificación de oráculo sellado y verificar que aborta con error explícito.
  * Fault injection: fallo parcial de documento (7/10 evaluados) y verificar que el resultado agregado es EXECUTION_FAILURE.
  * Test de idempotencia de recuperación: ejecutar certificación, fallar, re-ejecutar, verificar mismo resultado sin reutilización no determinista de residuos.
  * Test de evidencia completa: verificar que un auditor externo puede reconstruir la certificación sin re-ejecución.
  * Test de distinción de resultados: verificar que "certificación rechazada" y "tooling falló" producen códigos de salida distintos.
  * Test de condición compuesta CERTIFIED: verificar que CERTIFIED requiere simultáneamente execution SUCCESS + scientific ACCEPTED + evidence complete + invariants satisfied.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro §5 (Invariante de Sellado Estricto) y §9 (Architecture Governance Framework). |
| `ADR_F17_BIS_05` | Este NADR implementa D8 (Certification Operational Integrity) del ADR de Fase 5. |
| `ENGINEERING_PRINCIPLES` | Este NADR materializa §IV (Cero Fallos Silenciosos, Trazabilidad Absoluta). |
| `NADR-F17BIS-20` | **Dependencia directa:** El PREFLIGHT verifica la cualificación del corpus establecida por NADR-20. Corpus identity y manifest identity son entidades distintas conforme a NADR-20. |
| `NADR-F17BIS-21` | **Dependencia directa:** El PREFLIGHT verifica el estado Sealed de los oráculos; este NADR protege la frontera definida por NADR-21. La inmutabilidad de Sealed es absoluta conforme a NADR-21 R19. El tooling de certificación no tiene autoridad de mutación sobre Ground Truths. |
| `NADR-F17BIS-22` | **Dependencia directa:** El PREFLIGHT verifica la configuración canónica definida por NADR-22. |
| `NADR-F17BIS-23` | **Dependencia directa:** El PREFLIGHT verifica los parámetros congelados y el calibration provenance definidos por NADR-23. La POST-RUN VALIDATION verifica el evaluation provenance. |
| `NADR-F17BIS-19` | **Dependencia operacional:** NADR-19 define la semántica de veredictos (PASS/WARNING/HARD_FAIL) del DoubleProtectionMechanism; este NADR operacionaliza el mapeo de resultados y preserva la distinción entre "rechazo científico" y "fallo operacional". La taxonomía de códigos de salida de este NADR **MUST** reconciliarse con la taxonomía de veredictos de NADR-19 en el Execution Plan. |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN` | Materializa las reglas de este NADR mediante tareas de remediación de DF-18, GAP-5.0-03, GAP-5.2-05, y materialización del PREFLIGHT y POST-RUN VALIDATION. |
| `FASE_6_CONTINUOUS_VERIFICATION` | **Influencia:** Este NADR establece las precondiciones operacionales para la integración definitiva en CI/CD (Fase 6). |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la cualificación del corpus ni la cobertura de traits (responsabilidad de `NADR-F17BIS-20`).
* **No gobierna** la elegibilidad, curaduría o sellado de Ground Truths (responsabilidad de `NADR-F17-BIS-21`).
* **No gobierna** la configuración del motor de evaluación topológica ni el modelo de costo (responsabilidad de `NADR-F17-BIS-22`).
* **No gobierna** la calibración empírica de parámetros ni la independencia de datasets (responsabilidad de `NADR-F17-BIS-23`).
* **No gobierna** la integración en CI/CD de los Regression Gates (responsabilidad de `FASE_6_CONTINUOUS_VERIFICATION`).
* **No prescribe** los códigos de salida numéricos específicos (0/1/2 u otros). La taxonomía de códigos pertenece al Execution Plan y debe reconciliarse con NADR-19.
* **No prescribe** la infraestructura específica de persistencia (SQLite, JSON, filesystem). La implementación física pertenece al Execution Plan.
* **No prescribe** el mecanismo específico de PREFLIGHT ni POST-RUN VALIDATION (script, librería, módulo). La implementación pertenece al Execution Plan.
* **No promete** atomicidad física completa del filesystem si la infraestructura subyacente no la garantiza. Solo exige atomicidad lógica a nivel de certificación.
* **No otorga** autoridad de mutación sobre Ground Truths al tooling de certificación. La mutación pertenece exclusivamente a NADR-F17BIS-21.
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del `PHASE_17BIS_FASE5_EXECUTION_PLAN`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.