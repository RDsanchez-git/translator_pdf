# NADR-F17BIS-25: Verification Boundary & Production Subject



## 1. METADATA

* **Decision ID:** `NADR-F17BIS-25`
* **Título:** Verification Boundary & Production Subject
* **Clase de Decisión:** `STRUCTURAL / OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 6 (Continuous Verification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Equipo de Arquitectura / Fase 6
* **Capacidad Arquitectónica:** CAP-1 (Verification Boundary) — Establece la frontera normativa entre el sujeto de verificación (production pipeline) y los mecanismos auxiliares de evaluación, garantizando que la Continuous Verification evalúe exclusivamente el pipeline productivo canónico y no rutas alternativas, componentes aislados, ni fixtures legacy.
* **Evidencia Forense:** `E-6.0-001`, `E-6.1-001`, `E-6.1-002`, `E-6.1-008`, `E-6.1-009`, `E-6.3-001`, `GAP-6.3-01`, `DC-6.1` (dimensión boundary), `DC-6.3`, `DC-6.7`, `DC-6.12`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_06` v1.2.0 (FROZEN), `NADR-F17BIS-19` (Regresión Topológica Graduada), `NADR-F17BIS-21` (Baseline Sealing)
  * **Influencia:** `NADR-F17BIS-26` (Baseline Materialization), `NADR-F17BIS-27` (Failure Semantics), `NADR-F17BIS-28` (Evidence & Identity Chain), `NADR-F17BIS-29` (Execution Profiles), `NADR-F17BIS-30` (CI Enforcement), `PHASE_17BIS_FASE6_EXECUTION_PLAN`
  * **Conflictúa con:** Cualquier práctica que verifique rutas legacy, componentes aislados, o fixtures sintéticos como sustituto del production pipeline canónico.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin una frontera de verificación clara, CI puede ejecutar tests que no evalúan el production pipeline real, creando una falsa sensación de protección (Regression Gate Illusion). Esto permite que regresiones topológicas pasen desapercibidas hasta la producción.
* **Mantenibilidad:** 4 — Sin un sujeto normativo explícito, cada nuevo componente de evaluación puede definir su propio "sujeto de verificación", fragmentando la capacidad de Continuous Verification y dificultando la trazabilidad de regresiones.
* **Recuperabilidad:** 3 — Si la frontera no está clara, diagnosticar una regresión requiere determinar primero qué se verificó realmente, añadiendo complejidad forense.
* **Seguridad:** 3 — Sin frontera explícita, un atacante o error de configuración podría sustituir el sujeto de verificación por un componente que siempre pasa, eludiendo el gate.
* **Financiero:** 2 — El costo directo es bajo, pero la detección tardía de regresiones en producción implica retrabajo significativo.

* **Total Score: 17/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**La Continuous Verification MUST evaluar exclusivamente el production pipeline canónico como sujeto de verificación, conectando la infraestructura de CI al verification entry point existente sin crear mecanismos alternativos, rutas paralelas, ni fixtures sintéticos como sustituto.**

En consecuencia:

* Queda PROHIBIDO verificar componentes aislados (un parser, un provider, un builder) como sustituto del production pipeline completo.
* Queda PROHIBIDO usar fixtures sintéticos o rutas legacy como referencia de verificación en CI.
* Queda REQUERIDO que CI invoque el verification entry point normativo que conecta el production pipeline con la baseline sellada.
* Queda PROHIBIDO crear un segundo mecanismo de verificación que duplique la capacidad existente.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de Continuous Verification requiere un sujeto de verificación claramente definido. Sin este sujeto, la infraestructura de CI puede ejecutar tests que no evalúan el pipeline productivo real, creando la "Regression Gate Illusion" identificada en HITO 6.0: la apariencia de protección sin verificación efectiva.

Las clases de defectos identificados son:

1. **Desconexión CI ↔ Verification Subject:** La infraestructura de CI ejecuta un selector de tests que no invoca el verification entry point real. El production pipeline no es evaluado por CI.

2. **Sujeto de verificación no normativo:** Sin una frontera explícita, existe el riesgo de verificar componentes aislados, rutas legacy, o fixtures sintéticos como sustituto del production pipeline canónico.

3. **Duplicación de mecanismos:** Sin una regla de integración, existe el riesgo de crear un segundo mecanismo de verificación que duplique la capacidad existente, fragmentando la trazabilidad.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-6.0-001` / `GAP-6.3-01` (P0 — Crítico):** El CI ejecuta un selector de tests (`pytest -m "regression"`) que selecciona 0 tests. El verification entry point real (`tools/evaluation/run_regression.py`) no es invocado por CI. Existe una frontera nominal de regresión sin sujeto ejecutable.

* **`E-6.1-001` / `E-6.1-002` (P1 — Alto):** El verification entry point real (`tools/evaluation/run_regression.py`) invoca el production pipeline canónico (`apps/bootstrap/pipeline_factory.py::build_extraction_pipeline()`) y ejecuta la extracción real sobre PDFs del corpus. La correspondencia production ↔ verification está demostrada como completa en el plano de extracción.

* **`E-6.1-008` / `E-6.1-009` (P2 — Medio):** El production pipeline canónico está compuesto por una composition root (`apps/bootstrap/pipeline_factory.py::build_extraction_pipeline()`) que instancia un adapter de parsing (`infra/adapters/pdf_parser.py::PdfParserAdapter`) que a su vez usa un provider de extracción (`infra/extraction/providers/pymupdf_provider.py::PyMuPDFProvider`). La composición interna del pipeline es gobernada por sus respectivos contratos.

* **`E-6.3-001` (P0 — Crítico):** La verificación forense exhaustiva confirma que CI no invoca el verification entry point real. La cadena EVENT → CI → ENTRY_POINT → PRODUCTION_PIPELINE → BASELINE → MECHANISM → VERDICT está rota en el primer eslabón.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Sujeto de Verificación Normativo

1. La Continuous Verification **MUST** evaluar el production pipeline canónico como sujeto de verificación. El sujeto es la composition root productiva que orquesta la extracción completa, no un componente aislado.

2. La Continuous Verification **MUST NOT** verificar componentes aislados (un parser, un provider, un builder) como sustituto del production pipeline completo.

3. La Continuous Verification **MUST NOT** usar fixtures sintéticos, rutas legacy, o artefactos de test como referencia de verificación en CI.

4. La correspondencia entre el sujeto productivo y el sujeto de verificación **MUST** ser demostrable: el verification entry point **MUST** invocar el production pipeline canónico y ejecutar la extracción real sobre los artefactos del corpus.

### 5.2 Conexión CI ↔ Verification Entry Point

5. La infraestructura de CI **MUST** invocar el verification entry point normativo que conecta el production pipeline con la baseline sellada.

6. La infraestructura de CI **MUST NOT** ejecutar selectores de tests que no invoquen el verification entry point real como mecanismo de Continuous Verification.

7. La cadena EVENT → CI → ENTRY_POINT → PRODUCTION_PIPELINE → BASELINE → MECHANISM → VERDICT **MUST** estar completa y demostrable para cada perfil de ejecución.

### 5.3 Integración, No Creación

8. La Continuous Verification **MUST** reutilizar el verification entry point y el mecanismo de evaluación existentes. Queda **PROHIBIDO** crear un segundo mecanismo de verificación que duplique la capacidad existente.

9. Si durante la implementación aparece evidencia de una capacidad funcional imprescindible no cubierta por el mecanismo existente, **MUST** registrarse como Finding / Decision Candidate y **MUST NOT** implementarse hasta que el ADR correspondiente lo autorice.

10. La composición interna del production pipeline **MUST NOT** ser modificada como parte de la integración de Continuous Verification. La composición interna es gobernada por sus respectivos contratos y puede cambiar en fases posteriores sin afectar la frontera de verificación.

### 5.4 Frontera de Verificación

11. La frontera de verificación **MUST** distinguir entre:
    * **Sujeto de verificación:** El production pipeline canónico y su salida (Candidate AST).
    * **Referencia de verificación:** La baseline sellada (Sealed Oracle).
    * **Mecanismo de evaluación:** El motor de regresión topológica.
    * **Infraestructura de CI:** El orquestador que invoca el verification entry point.

12. La frontera de verificación **MUST NOT** confundir el sujeto de verificación con el mecanismo de evaluación. El mecanismo evalúa al sujeto contra la referencia; no es parte del sujeto.

13. La frontera de verificación **MUST NOT** confundir la referencia de verificación (baseline sellada) con fixtures de test. La referencia **MUST** ser la baseline sellada del corpus canónico.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La Continuous Verification evalúa exclusivamente el production pipeline canónico, garantizando que las regresiones topológicas sean detectadas en el sujeto real de producción.

* La "Regression Gate Illusion" queda eliminada: CI invoca el verification entry point real, no un selector de tests vacío.

* La trazabilidad de regresiones es directa: una regresión detectada por CI puede atribuirse inequívocamente a un cambio en el production pipeline.

* La capacidad de Continuous Verification no se fragmenta: un único verification entry point conecta el production pipeline con la baseline sellada.

* La composición interna del production pipeline puede evolucionar en fases posteriores (Fase 18: Advanced Local Runtime) sin afectar la frontera de verificación, siempre que el sujeto de verificación permanezca siendo el production pipeline canónico.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Inspección del workflow de CI para verificar que invoca el verification entry point real.
  * Grep para verificar que no existen selectores de tests vacíos como mecanismo de Continuous Verification.
  * Inspección del verification entry point para verificar que invoca el production pipeline canónico.
  * Import-linter para verificar que el verification entry point no importa componentes aislados como sustituto del production pipeline.

* **Validation (dinámica/comportamental):**
  * Ejecución del verification entry point contra el corpus canónico sellado, verificando que produce el resultado esperado (HARD_FAIL con el estado actual de la baseline).
  * Verificación de que la cadena EVENT → CI → ENTRY_POINT → PRODUCTION_PIPELINE → BASELINE → MECHANISM → VERDICT está completa en al menos un perfil de ejecución.
  * Verificación de que el verification entry point no puede ser sustituido por un fixture sintético sin violar las reglas.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro para la capacidad de Verification Boundary en la subfase de Continuous Verification. |
| `ADR_F17_BIS_06` v1.2.0 | Este NADR implementa las decisiones D1 (Integración, No Creación), D2 (Verification Subject), y D4 (Conexión CI ↔ Entry Point) del ADR de Fase 6. |
| `NADR-F17BIS-19` | **Dependencia directa:** Este NADR gobierna el sujeto de verificación; NADR-19 gobierna el mecanismo de evaluación (DoubleProtectionMechanism). Ambos son necesarios para la Continuous Verification. |
| `NADR-F17BIS-21` | **Dependencia directa:** Este NADR gobierna el sujeto de verificación; NADR-21 gobierna la baseline sellada que sirve como referencia de verificación. El sujeto se verifica contra la referencia. |
| `NADR-F17BIS-26` | **Influencia:** Este NADR establece el sujeto de verificación; NADR-26 establece cómo se materializa la baseline que sirve como referencia de verificación. |
| `NADR-F17BIS-27` | **Influencia:** Este NADR establece el sujeto de verificación; NADR-27 establece la semántica de fallo del resultado de la verificación. |
| `NADR-F17BIS-28` | **Influencia:** Este NADR establece el sujeto de verificación; NADR-28 establece la evidencia persistente y la identity chain del reporte de verificación. |
| `NADR-F17BIS-29` | **Influencia:** Este NADR establece el sujeto de verificación; NADR-29 establece los perfiles de ejecución que invocan al sujeto. |
| `NADR-F17BIS-30` | **Influencia:** Este NADR establece el sujeto de verificación; NADR-30 establece el enforcement de merge protection que protege el resultado de la verificación. |
| `PHASE_17BIS_FASE6_EXECUTION_PLAN` | Las tareas que materializan estas reglas son gobernadas por el Execution Plan de Fase 6. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la materialización de la baseline en CI (responsabilidad de `NADR-F17BIS-26`).
* **No gobierna** la semántica de fallo ni la taxonomía de exit codes (responsabilidad de `NADR-F17BIS-27`).
* **No gobierna** la identity chain ni la reproducibilidad del reporte (responsabilidad de `NADR-F17BIS-28`).
* **No gobierna** los perfiles de ejecución ni su frecuencia (responsabilidad de `NADR-F17BIS-29`).
* **No gobierna** el enforcement de branch protection ni la evidencia externa de activación (responsabilidad de `NADR-F17BIS-30`).
* **No gobierna** la composición interna del production pipeline (responsabilidad de los contratos de extracción y fases posteriores).
* **No gobierna** el mecanismo de evaluación topológica (responsabilidad de `NADR-F17BIS-19`).
* **No gobierna** el sellado de la baseline ni el ciclo de vida del Ground Truth (responsabilidad de `NADR-F17BIS-21`).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.