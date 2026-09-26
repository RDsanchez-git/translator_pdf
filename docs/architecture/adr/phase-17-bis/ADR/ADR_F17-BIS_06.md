# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17_BIS_06: Continuous Verification — CI Gate Integration & Operational Enforcement

* **Estado:** FROZEN
* **Versión:** 1.2.0
* **Fecha de Emisión:** 2026-09-25
* **Fecha de Congelamiento:** 2026-09-26
* **Autor:** Architecture Board / Staff Engineering
* **Fase Parent:** 17-BIS (Scientific Baseline / Canonical Corpus)
* **Evidencia Forense Vinculante:** HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md v1.0.0 (FROZEN), HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md v1.0.0 (FROZEN), HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md v1.0.0 (FROZEN), HITO_6.3_CI_REGRESSION_GATE_AND_OPERATIONAL_SEMANTICS.md v1.0.0 (FROZEN), HITO_6.4_DEPENDENCY_GRAPH_AND_READINESS_ASSESSMENT.md v1.0.0 (FROZEN), HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md (C5-R09 P0), HITO_0.5_ENTREGABLE_3_ARCHITECTURE_GOVERNANCE_FRAMEWORK_PART4.md (regla 4 MUST), HITO_0.5_ENTREGABLE_1_GAP_MATRIX.md (GAP-C5-04 P0), FASE_5_HANDOFF.md v1.0.1 (FROZEN)
* **Referencias Cruzadas:**
  * **Depende de:** ADR_F17_BIS_MASTER (FROZEN), ADR_F17_BIS_05 (FROZEN), NADR-F17BIS-19 a NADR-F17BIS-24 (FROZEN)
  * **Implementado por:** NADR-F17BIS-25 a NADR-F17BIS-2X (a promulgar)
  * **Ejecutado por:** PHASE_17BIS_FASE6_EXECUTION_PLAN (a redactar)
  * **Conflictúa con:** Ninguno

> **Nota de Gobernanza:** Este documento desarrolla una decisión arquitectónica particular dentro de la Fase 17-BIS, conforme a la arquitectura definida por el `ADR_F17_BIS_MASTER.md`. No modifica ni reemplaza las decisiones del ADR Maestro; únicamente las particulariza para la subfase de Continuous Verification. Este ADR es el artefacto de síntesis de los HITOs forenses 6.0 a 6.4 y resuelve las Decisiones Candidatas acumuladas.

> **Nota de Trazabilidad (DC-6.15):** La obligación de enforcement (DC-6.15) fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0) y permaneció pendiente durante Fases 1-5. Fase 6 asume la resolución de esta obligación pendiente. La activación efectiva de branch protection permanece fuera del perímetro del repositorio (configuración del servidor GitHub).

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-25 | Emisión inicial DRAFT. 8 decisiones (D1-D8). Basado en síntesis transversal de HITOs 6.0–6.4. |
| 1.1.0 | 2026-09-25 | ADR Review Wave 1. Correcciones: (1) DC-6.1 resuelto explícitamente: CONFORMANCE como modelo primario, con consecuencia de operatividad documentada; (2) DC-6.15 mantenido como NO DEMOSTRADO con evidence boundary explícito; (3) "Baseline Certificada" corregido a "Baseline materializada y sellada"; (4) DoD corregido: decisión arquitectónica ≠ implementación; (5) D1 reformulado de hecho a decisión arquitectónica basada en evidencia; (6) Target State simplificado: internals del pipeline eliminados; (7) D6: ADR fija capacidad, NADR fija taxonomía; (8) D5: distinción identidad física/lógica reforzada; (9) D7: ejemplos de perfiles eliminados; (10) Consecuencias de no resolver reformuladas; (11) Regla de oro sobre garantía absoluta reformulada. |
| 1.2.0 | 2026-09-26 | ADR Review Wave 2 — Resolución de DC-6.15 con evidencia forense. Correcciones: (1) D8 reformulado: obligación de enforcement documentada desde Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0), nombre del workflow "CI — Required Status Checks" como evidencia declarativa de intención, evidence boundary explícito (activación fuera del perímetro del repositorio); (2) Tabla de SEPARACIÓN DE RESPONSABILIDADES agregada a D8 clarificando roles de ADR, NADR, Execution Plan y Administrador del repositorio; (3) DoD #9 reformulado con evidencia externa explícita (API response, screenshot, o verificación manual documentada); (4) Regla de Oro #4 reformulada con evidencia forense; (5) DC-6.15 cambiado de "NO DEMOSTRADO" a "RESUELTO a nivel ADR" con precisión semántica (decisión arquitectónica RESUELTA, implementación PENDIENTE en Execution Plan, activación efectiva FUERA DEL PERÍMETRO); (6) Evidencia forense vinculante actualizada con HITOs de Fase 0 (HITO 0.4.4, HITO 0.5 ENTREGABLE_3, GAP-C5-04); (7) Nota de trazabilidad agregada: obligación pendiente desde Fase 0 asumida por Fase 6; (8) Invariante de Enforcement Documentado agregada a §6. |

---

## 1. CONTEXTO Y JUSTIFICACIÓN

La Fase 5 (Baseline Certification) materializó y selló el Corpus Canónico v3.9 con 21 identidades bajo Zero Partial Sealing (manifest hash `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`), construyó el mecanismo de regresión topológica (`DoubleProtectionMechanism` con `CriticalityAwareCostContext`), y produjo el Imperative Shell de regresión (`run_regression.py`) que conecta el production pipeline (`build_extraction_pipeline()`) con la baseline sellada. La certificación científica resultó REJECTED_WITH_DOCUMENTED_LIMITATIONS (NSS 0.7208 < 0.80, 163 Critical FN), pero el entry point de verificación y el mecanismo asociado son ejecutables localmente y producen el resultado esperado bajo las condiciones observadas (3.74 segundos para 21 documentos, sin dependencias externas, exit code 2 correcto).

Cinco HITOs forenses consecutivos (6.0 a 6.4) auditaron la frontera de Continuous Verification, produciendo un cuerpo de evidencia de 51 evidencias, 25 gaps consolidados, 15 Decision Candidates, 4 contradicciones entre arquitectura y operación, y 6 findings diferidos. La síntesis transversal de HITO 6.4 demostró que la cadena de Continuous Verification está **rota en tres puntos**: (1) CI no invoca el entry point correcto (`pytest -m "regression"` selecciona 0 tests; `run_regression.py` no es invocado — HITO 6.3 E-6.3-001), (2) la baseline no es materializable en CI (14 de 21 PDFs no trackeados, sin mecanismo de provisioning — HITO 6.2 E-6.2-001, E-6.2-002), y (3) el enforcement a nivel de merge no tiene evidencia declarativa en el repositorio (HITO 6.3 E-6.3-004; verificación forense exhaustiva confirma ausencia de archivos de configuración declarativa, workflows de activación, tests de enforcement, o dependencias de gestión declarativa de GitHub).

El hallazgo central de la auditoría es que **la capacidad de verificación existe localmente pero no está conectada a CI**: el mecanismo de verificación funciona correctamente cuando se ejecuta manualmente, pero no es invocado por la infraestructura de CI. Esto reduce significativamente el scope de Fase 6 respecto a construir un mecanismo nuevo, aunque la operacionalización completa requiere resolver materialización, semántica, evidencia y enforcement. Adicionalmente, la auditoría forense reveló que la obligación de enforcement fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0) y permaneció pendiente durante Fases 1-5; Fase 6 asume la resolución de esta obligación.

---

## 2. PROBLEMA ARQUITECTÓNICO

La arquitectura de Continuous Verification presenta cinco dimensiones estructurales que impiden la integración efectiva de los Regression Gates en CI/CD:

1. **Desconexión CI ↔ Verification Subject:** El CI ejecuta un entry point (`pytest -m "regression"`) que selecciona 0 tests. El entry point real que conecta el production pipeline con la baseline sellada (`run_regression.py`) no es invocado por CI. Existe una frontera nominal de regresión sin sujeto ejecutable (HITO 6.0 E-6.0-001, HITO 6.3 E-6.3-001, GAP-6.3-01).

2. **Ausencia de Materialización de Baseline en CI:** 14 de 21 PDFs del corpus canónico no están trackeados en git (regla `.gitignore`: `tests/corpus/canonical/pdf/`). No existe mecanismo de materialización (artifact download, object storage, cache, self-hosted runner) para que CI acceda a los PDFs completos (HITO 6.2 E-6.2-001, E-6.2-002, GAP-6.2-01, GAP-6.2-02).

3. **Semántica Operacional Ambigua:** El exit code 1 es ambiguo: puede significar WARNING (veredicto científico, NADR-19 §5.5 R22) o crash (fallo de ejecución, default de Python). El reporte de regresión no incluye el `configuration_fingerprint` ni la identity chain completa (`manifest_hash`, `parameter_identity`, `result_identity`), rompiendo la reproducibilidad (HITO 6.2 E-6.2-004, HITO 6.3 E-6.3-002, E-6.3-012, GAP-6.2-04, GAP-6.3-02, GAP-6.3-06).

4. **Protección de Integridad Incorrecta:** CI verifica inmutabilidad de `tests/fixtures/` (ruta legacy con caches y fixtures sintéticos) pero no de `tests/corpus/canonical/` (ruta canónica con la baseline sellada). Mutaciones a la baseline no serían detectadas por CI (HITO 6.3 E-6.3-003, GAP-6.3-03).

5. **Enforcement sin Evidencia Declarativa:** La verificación forense exhaustiva (búsqueda de archivos de configuración declarativa, workflows de activación, tests de enforcement, dependencias de gestión declarativa de GitHub) confirma que el repositorio no contiene evidencia declarativa de enforcement. Sin embargo, la obligación de enforcement está documentada desde Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0), y el workflow CI fue diseñado con nombre declarativo "CI — Required Status Checks" (evidencia de intención). La activación efectiva de branch protection es configuración del servidor GitHub, fuera del perímetro verificable del repositorio (HITO 6.3 E-6.3-004, GAP-6.3-04).

**Consecuencias de no resolver el problema:**
* El DoD Level B del ADR Maestro ("Compuertas de CI Activas") permanece insatisfecho.
* La obligación de enforcement pendiente desde Fase 0 (HITO 0.4.4 C5-R09 P0, GAP-C5-04 P0) permanece sin resolución.
* La Fase 18 (Advanced Local Runtime) queda sin red de seguridad para sus modificaciones profundas (asincronía, zero-copy, batching).
* La "Regression Gate Illusion" persiste: la apariencia de protección sin verificación real.
* Los cambios futuros del pipeline no disponen actualmente de una ejecución CI automatizada que confronte el resultado contra la baseline y propague su veredicto al gate de merge.
* La reproducibilidad de la verificación no está garantizada: un verdict no puede ser reconstruido sin la identity chain.

---

## 3. DECISIÓN ARQUITECTÓNICA

**La Fase 6 establecerá la conexión operativa, reproducible e íntegra entre el mecanismo de verificación existente (construido en Fase 5) y la infraestructura de CI/CD, de manera que cada cambio al pipeline de producción sea confrontado automáticamente contra la Scientific Baseline sellada, con semántica de fallo inequívoca, evidencia persistente y enforcement demostrable.**

En consecuencia, se establecen las siguientes nueve decisiones arquitectónicas:

### D1 — Continuous Verification como Integración, No Creación (DC-6.12, GAP-6.3-01)

La auditoría demuestra que el mecanismo de verificación requerido ya existe y es ejecutable localmente (HITO 6.1 E-6.1-001, E-6.1-002; HITO 6.2 E-6.2-006; HITO 6.3 E-6.3-008). Por tanto, Fase 6 adopta como decisión arquitectónica **reutilizar dicho mecanismo y limitar la fase a su operacionalización en CI**, salvo que durante la implementación aparezca evidencia de una capacidad funcional imprescindible que no esté cubierta por el mecanismo existente. La "Regression Gate Illusion" (HITO 6.0) se resuelve conectando el entry point real, no creando uno nuevo.

### D2 — Verification Subject: Production Pipeline Normativo (HITO 6.1)

El sujeto de verificación es `build_extraction_pipeline()` como composition root productiva, conforme a NADR-19 §5.5 R20. La verificación evalúa el AST candidato producido por el production pipeline contra el SealedOracle de la baseline. No se verifica un parser aislado, un provider directo, ni una ruta legacy. La correspondencia production ↔ verification está demostrada como completa en el plano de extracción (HITO 6.1 E-6.1-008, E-6.1-009). La composición interna del production pipeline permanece gobernada por sus respectivos contratos y no constituye parte de la decisión de Fase 6.

### D3 — Baseline Sellada como Referencia Inmutable (HITO 6.2, ADR_05 D3)

La baseline sellada de Fase 5 (corpus v3.9, 21 identidades, manifest `727782fe...`) es la referencia inmutable de Continuous Verification. Fase 6 NO modifica, recalibra, re-sella ni sustituye la baseline. La baseline es read-only desde la perspectiva de CI. Cualquier mutación a la baseline requiere un nuevo ciclo gobernado de re-baseline (NADR-21 §5.8 R35-R37), no una operación de Fase 6.

### D4 — Conexión CI ↔ Verification Entry Point (DC-6.3, DC-6.12, GAP-6.3-01)

CI debe invocar el verification entry point real que ejecuta el production pipeline contra la baseline sellada. La conexión actual (`pytest -m "regression"` → 0 tests) NO constituye una conexión válida. La forma específica de conexión (pytest marker con tests reales, invocación directa del entry point, wrapper, o combinación) es definida por los NADRs. El requisito arquitectónico es que la cadena EVENT → CI → ENTRY_POINT → PRODUCTION_PIPELINE → BASELINE → MECHANISM → VERDICT esté completa y demostrable.

### D5 — Contrato de Materialización de Baseline (DC-6.2, GAP-6.2-01, GAP-6.2-02)

Debe existir un mecanismo por el cual CI acceda al conjunto completo de artefactos físicos de la baseline sellada (PDFs del corpus, Ground Truths/Sealed Oracles, y manifest). La materialización CI deberá preservar la distinción entre artefactos físicos del corpus, Ground Truth/Sealed Oracle, manifest e identidad de baseline; ningún artefacto individual será considerado sustituto de la identidad global de la baseline. El mecanismo debe preservar la identidad e integridad de los artefactos (verificación SHA-256 contra manifest). La forma específica (git tracking, artifact repository, object storage, self-hosted runner, o combinación) es definida por los NADRs. El requisito arquitectónico es que el mecanismo no altere la identidad física del corpus ni viole las restricciones de distribución vigentes (O-5.0-1 de Fase 5).

### D6 — Semántica Operacional Inequívoca (DC-6.4, DC-6.9, DC-6.10, DC-6.13, GAP-6.2-04, GAP-6.3-02, GAP-6.3-06)

CI debe distinguir inequívocamente entre éxito de verificación, divergencia/regresión, y fallos operacionales o de integridad de la referencia. Un consumidor CI debe poder determinar la clase de resultado sin ambigüedad. El exit code 1 ambiguo (WARNING vs crash) debe resolverse. El reporte de regresión debe incluir la identity chain completa (`configuration_fingerprint`, `manifest_hash`, `corpus_version`) para garantizar reproducibilidad. La taxonomía normativa exacta de estados, exit codes, y estructura del reporte será establecida por los NADRs.

### D7 — Perfiles de Ejecución (DC-6.5, GAP-6.3-05)

CI debe soportar al menos un perfil de ejecución que ejecute la verificación completa contra el corpus canónico sellado. Perfiles adicionales son definidos por los NADRs. El requisito arquitectónico es que cada perfil tenga evidencia persistente y semántica de enforcement asociada.

### D8 — Protección de Integridad y Enforcement (DC-6.14, DC-6.15, GAP-6.3-03, GAP-6.3-04)

CI debe proteger la integridad de la baseline sellada (`tests/corpus/canonical/`) además de `tests/fixtures/`. La protección debe detectar mutaciones a GTs, manifest y PDFs trackeados. La forma específica de protección es definida por los NADRs.

**DECISION (Enforcement):** La obligación de enforcement está documentada desde Fase 0:
* HITO 0.4.4 C5-R09 (P0): "Configurar el workflow de CI en el repositorio remoto como un estado requerido (*Required Status Check*), bloqueando técnicamente la fusión (*merge*) de cualquier Pull Request si alguna aserción de regresión topológica o de snapshot falla."
* HITO 0.5 ENTREGABLE_3 regla 4 (MUST): "CI Enforcement: A declarative CI automation platform **MUST** be implemented, blocking merges to the main branch if any regression gate fails."
* GAP-C5-04 (P0): "Inexistencia de barreras de control remotas; posibilidad de fusionar cambios que rompan el sistema."

El workflow CI fue diseñado con nombre declarativo "CI — Required Status Checks", lo que constituye evidencia de intención de que el workflow sea un required status check. Sin embargo, el nombre es evidencia de **intención**, no de **activación**.

La verificación forense exhaustiva confirma que el repositorio NO contiene evidencia declarativa de activación:
* No hay archivo de configuración declarativa (`.github/settings.yml`, `.github/branch-protection.yml`, o similar).
* No hay workflow que configure branch protection vía API de GitHub.
* No hay tests que verifiquen enforcement.
* No hay dependencias de gestión declarativa de GitHub (probot/settings o similar).

**EVIDENCE BOUNDARY:** La activación efectiva de branch protection es configuración del servidor GitHub y permanece fuera del perímetro verificable del repositorio. La documentación establece la expectativa; la activación es responsabilidad del administrador del repositorio.

**SEPARACIÓN DE RESPONSABILIDADES:**

| Nivel | Responsabilidad | Estado |
|---|---|---|
| **ADR (este documento)** | Decide que DC-6.15 requiere documentación + evidencia externa | RESUELTO |
| **NADR** | Define qué tipos de evidencia externa son aceptables | PENDIENTE |
| **Execution Plan** | Secuencia cómo crear la documentación y obtener la evidencia | PENDIENTE |
| **Administrador del repositorio** | Activa branch protection en el servidor GitHub | FUERA DEL PERÍMETRO |

**DECISION:** Fase 6 debe:
1. **Crear documentación explícita** de la configuración esperada de branch protection (`.github/BRANCH_PROTECTION.md` o equivalente), especificando:
   * Job `regression-gates` debe ser required status check en la rama `main`.
   * Job debe ejecutarse en push y pull_request.
   * Merge bloqueado si job falla.
2. **Obtener evidencia externa de activación** como parte del DoD:
   * API response de GitHub mostrando `required_status_checks` configurado para el job `regression-gates` en la rama `main`.
   * Screenshot de la configuración de branch protection en la UI de GitHub.
   * Verificación manual documentada por el administrador del repositorio.

**DoD:** Documentación creada y commiteada. Evidencia externa de activación obtenida o documentada como pendiente de verificación por el administrador.

### D9 — Semántica de Verificación: Conformance como Modelo Primario (DC-6.1)

Fase 6 adopta **CONFORMANCE contra SealedOracle** como modelo primario de verificación: el AST candidato producido por el production pipeline se compara contra el Ground Truth sellado de la baseline. Este es el modelo implementado por el mecanismo existente (`DoubleProtectionMechanism`, HITO 6.1 E-6.1-011, E-6.1-012).

**Consecuencia de operatividad:** Con el estado actual de la baseline (163 Critical FN, NSS 0.7208 < 0.80), el modelo de conformance pura emitirá HARD_FAIL en toda ejecución (precedencia CRITICAL: Critical FN > 0 → HARD_FAIL, NADR-22 §5.7 R22-R25). Esto significa que el gate será **operativamente restrictivo** hasta que se resuelva una de las siguientes condiciones:
1. Se implemente una capacidad de **baseline de divergencia** (comparación contra divergencia esperada D₀) que permita al gate distinguir entre "divergencia conocida aceptada" y "regresión nueva". Esta capacidad es definida por los NADRs.
2. Se mejore el extractor para reducir Critical FN (fuera de scope de Fase 6, pertenece a post Fase 17-BIS).
3. Se recalibren thresholds empíricamente (fuera de scope de Fase 6, DC-6.6, ciclo de calibración posterior).

La semántica de **REGRESSION** (delta contra ejecución anterior) y **BASELINE DE DIVERGENCIA** (comparación contra divergencia esperada) son capacidades adicionales que pueden ser definidas por los NADRs si la evidencia lo requiere para la operatividad del gate.

---

## 4. OBJETIVO DE LA SUBFASE

La Fase 6 tiene como objetivo conectar el mecanismo de verificación existente (construido en Fase 5) a la infraestructura de CI/CD, de manera que cada cambio al pipeline de producción sea confrontado automáticamente contra la Scientific Baseline sellada. La conexión debe ser reproducible (identity chain completa), íntegra (baseline protegida contra mutación), y con enforcement demostrable (el gate puede bloquear merges).

El objetivo NO es construir un nuevo mecanismo de verificación (ya existe), NO es recalibrar la baseline (es read-only), NO es mejorar el extractor (pertenece a fase posterior), y NO es expandir el corpus (pertenece a re-baseline). El objetivo es exclusivamente la **conexión operativa** entre lo existente y CI, incluyendo la resolución de la obligación de enforcement pendiente desde Fase 0.

El objetivo primordial es garantizar que:
> *"Todo cambio que atraviese el gate de CI será evaluado contra la baseline sellada y su resultado será propagado al mecanismo de enforcement configurado, con evidencia persistente que permita reconstruir el verdict."*

---

## 5. ALCANCE Y NO-OBJETIVOS

### Dentro del Alcance
* Conexión del verification entry point real a la infraestructura de CI/CD.
* Materialización de la baseline sellada en el entorno de ejecución de CI.
* Semántica operacional inequívoca (capacidad de distinguir clases de resultado).
* Protección de integridad de la baseline canónica en CI.
* Perfiles de ejecución (al menos uno completo).
* Evidencia persistente y reproducible de cada ejecución.
* Documentación de la configuración esperada de enforcement (branch protection).
* Obtención de evidencia externa de activación de enforcement (API response, screenshot, o verificación manual documentada).
* Verificación de que la cadena EVENT → CI → ENTRY_POINT → PIPELINE → BASELINE → MECHANISM → VERDICT → ENFORCEMENT está completa.
* Resolución de la semántica de conformance como modelo primario (D9).
* Resolución de la obligación de enforcement pendiente desde Fase 0 (D8, DC-6.15).

### Fuera del Alcance (Out of Scope)
* **NO** construir un nuevo mecanismo de verificación (pertenece a Fase 5, ya construido).
* **NO** modificar, recalibrar ni re-sellar la baseline (la baseline es read-only; re-baseline requiere ciclo gobernado separado).
* **NO** mejorar el extractor ni integrar adaptadores alternativos (Marker, Docling, Nougat) (pertenece a post Fase 17-BIS, ADR Maestro §4).
* **NO** optimizar performance del pipeline de verificación (pertenece a Fase 18, Advanced Local Runtime).
* **NO** introducir asincronía, zero-copy, batching o ejecución distribuida (pertenece a Fase 18, ADR Maestro §4).
* **NO** expandir el corpus canónico (pertenece a re-baseline v4.0, ciclo gobernado separado).
* **NO** recalibrar thresholds NSS empíricamente (pertenece a ciclo de calibración posterior, DC-6.6).
* **NO** introducir infraestructura distribuida (Redis, Message Brokers, Kubernetes, DBs remotas) (ADR Maestro §4).
* **NO** activar directamente branch protection en el servidor GitHub (configuración del administrador del repositorio; Fase 6 documenta la expectativa y obtiene evidencia externa).

---

## 6. GOBERNANZA DE LA SUBFASE

Esta sub-fase requiere preservar las invariantes arquitectónicas fundacionales establecidas por el ADR Maestro (`ADR_F17_BIS_MASTER.md`).

Las restricciones obligatorias de implementación que garantizan el cumplimiento estricto de estas invariantes **quedan definidas y gobernadas exclusivamente en los NADRs asociados a esta fase**.

### Invariantes específicas de la Fase 6:

* **Invariante de Integración, No Creación:** Fase 6 conecta el mecanismo existente a CI. No construye un nuevo mecanismo de verificación. Cualquier nuevo componente debe demostrar que no duplica capacidad existente (ENGINEERING_PRINCIPLES §I: Reuse Before Invent).
* **Invariante de Baseline Read-Only:** La baseline sellada de Fase 5 es read-only desde la perspectiva de CI. Ningún componente de Fase 6 puede mutar, recalibrar ni sustituir artefactos de la baseline. La protección de integridad es obligatoria.
* **Invariante de Semántica Inequívoca:** Un consumidor CI debe poder distinguir entre clases de resultado (éxito, divergencia, fallo operacional, fallo de integridad) sin ambigüedad. Exit codes ambiguos violan ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos).
* **Invariante de Reproducibilidad:** Cada ejecución de Continuous Verification debe producir evidencia suficiente para reconstruir qué baseline, qué configuración y qué parámetros produjeron el verdict. Sin identity chain completa, la reproducibilidad está violada.
* **Invariante de Sujet Normativo:** El sujeto de verificación es el production pipeline (`build_extraction_pipeline()`), no un parser aislado ni una ruta legacy. La correspondencia production ↔ verification debe mantenerse (ADR Master §2.1).
* **Invariante de Conformance como Modelo Primario:** La verificación primaria es conformance contra SealedOracle. Capacidades adicionales (regression, baseline de divergencia) son extensiones que no reemplazan el modelo primario.
* **Invariante de Enforcement Documentado:** La expectativa de enforcement debe estar documentada explícitamente en el repositorio. La activación efectiva es responsabilidad del administrador del repositorio y requiere evidencia externa.

### Cláusula de Relación con Fase 5:

> *"La Fase 5 materializó y selló la Baseline y los Regression Gates como artefactos ejecutables y verificables fuera de CI. La Fase 6 integra estos artefactos en el pipeline de CI/CD. La Fase 6 NO reconstruye la baseline ni el mecanismo de verificación; únicamente los conecta a CI y define la semántica operacional."*

### Cláusula de Relación con Fase 0:

> *"La obligación de enforcement fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0) y permaneció pendiente durante Fases 1-5. La Fase 6 asume la resolución de esta obligación pendiente mediante documentación explícita de la configuración esperada y obtención de evidencia externa de activación."*

### Cláusula de Relación con Fase 18:

> *"La Fase 6 establece las Compuertas de CI Activas (DoD Level B del ADR Maestro). La Fase 18 (Advanced Local Runtime) puede ejecutar cambios en el pipeline de producción con la garantía de que las Compuertas de CI detectarán divergencias respecto a la baseline. La Fase 18 NO modifica las Compuertas de CI; únicamente las utiliza como red de seguridad. La composición interna del production pipeline puede cambiar en Fase 18 sin afectar la arquitectura de Continuous Verification de Fase 6."*

### Cláusula de Relación con el Execution Plan:

> *"Las decisiones arquitectónicas definidas en este ADR especifican las capacidades arquitectónicas requeridas. La secuenciación operativa, estrategia de despliegue, dependencias técnicas y logística de implementación son gobernadas independientemente por `PHASE_17BIS_FASE6_EXECUTION_PLAN.md`. El Execution Plan existe porque la auditoría forense (HITOs 6.0–6.4) demostró que las capacidades arquitectónicas no pueden implementarse independientemente: la conexión CI requiere resolver primero la materialización, luego la semántica operacional, y finalmente el enforcement."*

---

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

Tras la implementación de la Fase 6, la arquitectura de Continuous Verification opera como una cadena completa, reproducible e íntegra:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. CI TRIGGER                                                          │
│    GitHub event (push/PR/schedule)                                     │
│    → workflow CI                                                       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. BASELINE MATERIALIZATION                                            │
│    → Mecanismo de materialización (definido por NADRs)                 │
│    → Artefactos físicos del corpus disponibles                         │
│    → Verificación SHA-256 contra manifest                              │
│    → Baseline identity confirmada                                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. VERIFICATION ENTRY POINT                                            │
│    → Entry point real invocado por CI                                  │
│    → Configuración explícita del corpus                                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. PRODUCTION PIPELINE EXECUTION                                       │
│    → build_extraction_pipeline()                                       │
│    → Candidate AST                                                     │
│    (La composición interna del pipeline permanece gobernada por         │
│     sus respectivos contratos y no constituye parte de la decisión     │
│     de Fase 6.)                                                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. BASELINE INTEGRITY VERIFICATION                                     │
│    → Verificación de identidad documental                              │
│    → Verificación de estado sellado                                    │
│    → Verificación de integridad criptográfica                          │
│    → Verificación de completitud                                       │
│    → [Si falla: fallo de integridad de baseline, exit code inequívoco] │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. TOPOLOGICAL REGRESSION EVALUATION                                   │
│    → DoubleProtectionMechanism.evaluate()                              │
│    → NSS ponderado + CriticalityVerdict                                │
│    → Conformance contra SealedOracle (modelo primario, D9)             │
│    → Resultado: PASS / WARNING / HARD_FAIL                             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 7. EVIDENCE PERSISTENCE                                                │
│    → Reporte con identity chain completa                               │
│    → configuration_fingerprint, manifest_hash, corpus_version          │
│    → Métricas de divergencia                                           │
│    → Audit trail para reconstrucción                                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 8. EXIT CODE & CI DECISION                                             │
│    → Éxito: CI success                                                │
│    → Divergencia/regresión: CI failure                                 │
│    → Fallo operacional: CI failure                                     │
│    → Fallo de integridad de baseline: CI failure                       │
│    (Taxonomía exacta de exit codes definida por NADRs)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 9. ENFORCEMENT                                                         │
│    → Documentación de configuración esperada en repositorio            │
│      (.github/BRANCH_PROTECTION.md o equivalente)                      │
│    → Required status check en branch protection (configuración del     │
│      servidor GitHub, activación por el administrador del repositorio) │
│    → Merge bloqueado si gate falla                                     │
│    → Evidencia externa de activación: API response, screenshot,        │
│      o verificación manual documentada                                 │
│    → [Sin evidencia externa: ENFORCEMENT = NO DEMOSTRADO]              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Invariante del estado objetivo:**
> *"La Continuous Verification es una cadena completa, reproducible e íntegra: cada evento de CI materializa la baseline sellada, ejecuta el production pipeline contra ella, verifica la integridad de la referencia, evalúa la conformance topológica, produce evidencia con identity chain completa, y propaga el resultado con semántica inequívoca hasta el enforcement de merge."*

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| `ADR_F17_BIS_MASTER.md` | Este ADR particulariza las decisiones del Maestro para la subfase de Continuous Verification. Cierra el DoD Level B ("Compuertas de CI Activas"). | ✅ |
| `ADR_F17_BIS_05.md` | Este ADR consume la baseline sellada por Fase 5 como referencia inmutable. Implementa la cláusula de relación Fase 5 → Fase 6. | ✅ |
| `HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md` | Evidencia forense de Fase 0: C5-R09 (P0) Protección de Ramas vía Required Status Checks. Obligación de enforcement identificada. | ✅ |
| `HITO_0.5_ENTREGABLE_3_ARCHITECTURE_GOVERNANCE_FRAMEWORK_PART4.md` | Evidencia forense de Fase 0: regla 4 (MUST) CI Enforcement. Obligación normativa de enforcement. | ✅ |
| `HITO_0.5_ENTREGABLE_1_GAP_MATRIX.md` | Evidencia forense de Fase 0: GAP-C5-04 (P0) Inexistencia de barreras de control remotas. Gap de enforcement identificado. | ✅ |
| `HITO_6.0_ARCHITECTURE_AND_CV_BOUNDARY.md` | Evidencia forense de Fase 6: Regression Gate Illusion, gaps de CI. | ✅ |
| `HITO_6.1_PRODUCTION_PIPELINE_AND_VERIFICATION_SUBJECT.md` | Evidencia forense de Fase 6: sujeto de verificación, correspondencia. | ✅ |
| `HITO_6.2_CANONICAL_BASELINE_CONSUMPTION_AND_CORPUS_MATERIALIZATION.md` | Evidencia forense de Fase 6: materialización, integridad, identidad. | ✅ |
| `HITO_6.3_CI_REGRESSION_GATE_AND_OPERATIONAL_SEMANTICS.md` | Evidencia forense de Fase 6: entry point, exit semantics, enforcement. | ✅ |
| `HITO_6.4_DEPENDENCY_GRAPH_AND_READINESS_ASSESSMENT.md` | Evidencia forense de Fase 6: síntesis transversal, dependency graph, readiness. | ✅ |
| `NADR-F17BIS-19.md` | Regresión topológica graduada (DoubleProtectionMechanism). Este ADR NO lo modifica; extiende la taxonomía con clases de fallo adicionales. | ✅ |
| `NADR-F17BIS-20` a `NADR-F17BIS-24` | Phase 5 NADRs. Definen la baseline sellada y el tooling de regresión. Este ADR los conecta a CI. | ✅ |
| `NADR-F17BIS-25` a `NADR-F17BIS-2X` (a promulgar) | NADRs de Fase 6 que implementan las decisiones de este ADR. | ✅ |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` (a redactar) | Secuencia las tareas que materializan este ADR. | ✅ |
| `FASE_5_HANDOFF.md` | Estado de cierre Fase 5, carry-forwards. Decisión O-5.0-1 (copyright). | ✅ |
| `ENGINEERING_PRINCIPLES.md` | Functional Core / Imperative Shell (§II), Cero Fallos Silenciosos (§IV), Reuse Before Invent (§I). | ✅ |
| `ROADMAP_ARQUITECTONICO_LP.md` | "Regression Gates: Aserción estricta en CI que impida el merge de alteraciones a nodos críticos." | ✅ |

---

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Este documento actúa en estricto cumplimiento con el *Architecture Governance Framework* definido en `METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`.

* **Este ADR** define exclusivamente la visión arquitectónica de la sub-fase (el QUÉ y el POR QUÉ). Resuelve las Decisiones Candidatas acumuladas de HITOs 6.0 a 6.4 mediante decisiones arquitectónicas basadas en evidencia forense.
* Las **reglas técnicas obligatorias** y las restricciones de diseño se encuentran promulgadas en la serie normativa de NADRs aprobados para esta subfase (NADR-F17BIS-25 a NADR-F17BIS-2X, a promulgar).
* La **secuencia operativa, tareas concretas, definición de completitud (DoD) y disposición de módulos** se rigen por el Execution Plan (`PHASE_17BIS_FASE6_EXECUTION_PLAN.md`, a redactar).

Este documento **no prescribe implementaciones específicas, planificación operacional ni criterios de revisión de código.**

Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este ADR mediante los NADRs y el Execution Plan correspondientes.

---

## 10. REGISTRO DE DECISIONES CANDIDATAS RESUELTAS

| DC | Tema | Resolución | Estado | Evidencia |
|---|---|---|---|---|
| DC-6.1 | Semántica de Continuous Verification | D9: CONFORMANCE contra SealedOracle como modelo primario. Consecuencia de operatividad documentada. REGRESSION y BASELINE DE DIVERGENCIA como capacidades adicionales definibles por NADRs. | RESUELTO (con consecuencia explícita) | HITO 6.0, 6.1, 6.4 |
| DC-6.2 | Materialización del corpus en CI | D5: Debe existir mecanismo de materialización. Distinción identidad física/lógica preservada. Forma específica definida por NADRs. | RESUELTO a nivel ADR | HITO 6.2, 6.4 |
| DC-6.3 | Frontera CI ↔ dominio | D4: CI debe invocar el entry point real. Forma específica definida por NADRs. | RESUELTO a nivel ADR | HITO 6.0, 6.3, 6.4 |
| DC-6.4 | Taxonomía de estados operacionales | D6: Capacidad de distinguir clases de resultado. Taxonomía exacta definida por NADRs. | RESUELTO a nivel capacidad | HITO 6.2, 6.3, 6.4 |
| DC-6.5 | Perfiles de ejecución | D7: Al menos un perfil completo. Perfiles adicionales definidos por NADRs. | RESUELTO a nivel capacidad | HITO 6.3, 6.4 |
| DC-6.6 | Recalibración / re-baseline | Fuera de scope de Fase 6. La baseline es read-only. Recalibración pertenece a ciclo posterior. | RESUELTO (fuera de scope) | HITO 6.2, 6.4 |
| DC-6.7 | Verification boundary explícito | D2: Sujeto es production pipeline. Boundary definido por NADRs. | RESUELTO a nivel ADR | HITO 6.1, 6.4 |
| DC-6.8 | Smoke test de regresión | D7: Perfiles de ejecución definidos por NADRs. | RESUELTO a nivel capacidad | HITO 6.1, 6.3, 6.4 |
| DC-6.9 | run_entry(main) en run_regression.py | D6: Semántica inequívoca. Implementación específica definida por NADRs. | RESUELTO a nivel ADR | HITO 6.2, 6.3 |
| DC-6.10 | Verificación previa de PDFs | D6: Semántica inequívoca. Fallo de integridad para PDFs ausentes. | RESUELTO a nivel ADR | HITO 6.2, 6.3 |
| DC-6.11 | Verificación de manifest_hash y sha256 | D6: Reproducibilidad con identity chain completa. | RESUELTO a nivel ADR | HITO 6.2, 6.3 |
| DC-6.12 | Conexión CI ↔ entry point | D4: CI debe invocar el entry point real. Forma específica definida por NADRs. | RESUELTO a nivel ADR | HITO 6.0, 6.3, 6.4 |
| DC-6.13 | Identity chain en reporte | D6: Reporte con identity chain completa. Estructura definida por NADRs. | RESUELTO a nivel ADR | HITO 6.3, 6.4 |
| DC-6.14 | Protección de integridad de baseline | D8: CI protege tests/corpus/canonical/. Implementación definida por NADRs. | RESUELTO a nivel ADR | HITO 6.3, 6.4 |
| DC-6.15 | Branch protection / enforcement | D8: Obligación documentada desde Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0). Workflow diseñado como "Required Status Checks" (evidencia de intención). Verificación forense exhaustiva confirma ausencia de evidencia declarativa de activación en el repositorio. Decisión: crear documentación explícita (.github/BRANCH_PROTECTION.md) + obtener evidencia externa de activación (API response, screenshot, o verificación manual documentada). Activación efectiva fuera del perímetro del repositorio (configuración del servidor GitHub). | RESUELTO a nivel ADR. Implementación pendiente en Execution Plan. Activación efectiva fuera del perímetro. | HITO 0.4.4, HITO 0.5, GAP-C5-04, HITO 6.3, 6.4 |

---

## 11. DEFINITION OF DONE (DoD) DE LA FASE 6

La Fase 6 se considerará oficialmente finalizada cuando se cumplan las siguientes condiciones:

### DoD Nivel A: Decisiones Arquitectónicas

1. **D1-D9 resueltas:** Las 9 decisiones arquitectónicas están implementadas y verificables.
2. **Decision Candidates resueltos:** Los DCs identificados en HITOs 6.0-6.4 están resueltos a nivel arquitectónico/normativo mediante ADR y NADRs, o explícitamente diferidos/out-of-scope. La implementación se verifica en el Execution Plan.
3. **NADRs promulgados:** NADR-F17BIS-25 a NADR-F17BIS-2X están FROZEN.
4. **Execution Plan ejecutado:** PHASE_17BIS_FASE6_EXECUTION_PLAN.md está completo.

### DoD Nivel B: Compuertas de CI Activas (DoD Level B del ADR Maestro)

5. **Conexión CI ↔ Entry Point:** El verification entry point real es invocado por CI contra la baseline sellada. La cadena EVENT → CI → ENTRY_POINT → PIPELINE → BASELINE → MECHANISM → VERDICT está completa y demostrable.
6. **Materialización de Baseline:** CI puede acceder al conjunto completo de artefactos de la baseline sellada con verificación de identidad.
7. **Semántica Operacional Inequívoca:** Los exit codes distinguen las clases de resultado sin ambigüedad. El reporte incluye la identity chain completa.
8. **Protección de Integridad:** CI verifica la inmutabilidad de `tests/corpus/canonical/` (no solo `tests/fixtures/`).
9. **Enforcement Documentado con Evidencia Externa:** La configuración esperada de branch protection está documentada en el repositorio (`.github/BRANCH_PROTECTION.md` o equivalente) **Y** se obtuvo evidencia externa del servidor GitHub. La evidencia externa aceptable es una de las siguientes:
   * API response de GitHub mostrando `required_status_checks` configurado para el job `regression-gates` en la rama `main`.
   * Screenshot de la configuración de branch protection en la UI de GitHub.
   * Verificación manual documentada por el administrador del repositorio.
   
   **Nota:** La activación efectiva de branch protection es configuración del servidor GitHub y permanece fuera del perímetro verificable del repositorio. Sin evidencia externa, el estado permanece como ENFORCEMENT = NO DEMOSTRADO y el DoD Level B del ADR Maestro no se considera plenamente satisfecho. La obligación de enforcement fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0); Fase 6 asume su resolución.
10. **Evidencia Persistente:** Cada ejecución produce un reporte con identity chain completa que permite reconstruir el verdict.
11. **Regression Gate Funcional:** Al menos un perfil de ejecución demuestra que el gate detecta divergencias respecto a la baseline y produce el exit code correcto.

### DoD Nivel C: Verificación Estática y Pruebas Limpias

12. **Pyright:** 0 errors, 0 warnings.
13. **Tests:** Suite completa en verde. Baseline no degradada.
14. **Import-linter:** Architecture contract verificado.

---

## 12. REGLA DE ORO DE LA FASE 6

> **La Continuous Verification no se construye creando un nuevo mecanismo; se construye conectando el mecanismo existente a CI de manera que la cadena sea completa, reproducible e íntegra.**

> **La baseline sellada es read-only. No se recalibra, no se re-sella, no se sustituye como parte de la integración CI. Si la baseline necesita cambios, eso es un nuevo ciclo gobernado de re-baseline, no una operación de Fase 6.**

> **Un exit code ambiguo es un fallo silencioso. Si CI no puede distinguir entre clases de resultado, el gate no está funcionando.**

> **Un gate que puede fallar sin bloquear merges no es un gate. El enforcement debe ser demostrable mediante evidencia externa del servidor GitHub (API response, screenshot, o verificación manual documentada) o documentado explícitamente como NO DEMOSTRADO. La obligación de enforcement fue identificada en Fase 0 (HITO 0.4.4 C5-R09 P0, HITO 0.5 ENTREGABLE_3 regla 4 MUST, GAP-C5-04 P0) y permanece pendiente hasta que la evidencia externa esté disponible.**

> **La reproducibilidad no es opcional. Sin identity chain completa, un verdict no puede ser reconstruido, y la Continuous Verification pierde su valor forense.**

---

**Estado:** FROZEN v1.2.0
**Siguiente paso:** Promulgación de NADRs de Fase 6 (NADR-F17BIS-25 a NADR-F17BIS-2X), seguida de redacción de PHASE_17BIS_FASE6_EXECUTION_PLAN.md.