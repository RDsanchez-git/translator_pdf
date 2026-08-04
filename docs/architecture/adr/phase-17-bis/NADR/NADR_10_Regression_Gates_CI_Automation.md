# NADR-F17BIS-10: Regression Gates & CI Automation

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-10`
* **Título:** Regression Gates & CI Automation
* **Clase de Decisión:** `OPERATIONAL` / `DATA`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** QA / CI Team
* **Capacidad Arquitectónica:** CAP-004 (Topological Materialization) — verificación de integridad estructural
* **Evidencia Forense:** `E-0.4-385`, `E-0.4-381`, `E-0.4-382`, `E-0.4-389`, `E-0.4-390`, `GAP-C5-01`, `GAP-C5-02`, `GAP-C5-04`, `GAP-C5-05`, `GAP-0.4-09`, `P3-H04`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-01` (serialización canónica para oráculos deterministas), `NADR-F17BIS-03` (hashing semántico para fingerprints reproducibles).
  * **Influencia:** `NADR-F17BIS-02` (alineación del benchmark exige el adaptador de producción).
  * **Conflictúa con:** Toda asignación dinámica de oráculos, auto-generación de baselines y omisión de compuertas de integración.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S1)
* **Operacional:** 5 — CI aprueba silenciosamente builds con regresiones estructurales, permitiendo la fusión de código que destruye invariantes topológicas.
* **Mantenibilidad:** 5 — Tests tautológicos ocultan regresiones, generando una falsa sensación de cobertura que imposibilita el diagnóstico.
* **Recuperabilidad:** 4 — Baselines perdidas o corruptas son difíciles de reconstruir sin el oráculo original.
* **Seguridad:** 1
* **Financiero:** 1
* **Total Score: 16/25**

---

## 3. DECISIÓN EJECUTIVA

**La corrección del sistema se valida exclusivamente mediante oráculos inmutables e independientes, comparados contra la salida del pipeline de producción, y esta validación es impuesta por compuertas automatizadas de integración continua que bloquean la incorporación de cambios ante cualquier fallo.**

En consecuencia:
* Ningún oráculo de regresión puede ser generado, mutado o eludido durante la ejecución de pruebas.
* Ninguna regresión estructural, semántica o topológica puede incorporarse al sistema sin ser detectada.
* El laboratorio de benchmark evalúa exclusivamente el pipeline de producción real, no rutas alternativas ni parsers legacy.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La cadena de autoridad para la protección del código está incompleta en su último tramo. El sistema posee una base conceptual valiosa para pruebas de regresión (snapshots, inspección de sintaxis, Bounded Context de Ground Truth), pero esa base está corrompida por tres clases de defectos que invalidan la detección de regresiones:

1. **Tautologías y auto-generación de oráculos:** Las pruebas de regresión se comparan contra sí mismas o generan sus propios oráculos en ausencia de baseline, aprobando silenciosamente cualquier estado del sistema.
2. **Sustitución artificial de componentes:** Las pruebas de integración parchean los métodos principales del pipeline, validando iteraciones sobre datos mock en memoria en lugar del comportamiento real del sistema.
3. **Ausencia de compuertas automatizadas:** No existe un mecanismo de integración continua que bloquee la incorporación de cambios cuando una aserción de regresión falla.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-0.4-385` / `GAP-0.4-09` (P0 — Crítico):** La prueba de regresión del parser invalida el oráculo al reasignar la huella esperada al valor actual, transformando la aserción en una comparación idéntica (`A == A`). Adicionalmente, sustituye artificialmente el método de extracción e inyecta nodos fabricados en memoria.

* **`E-0.4-381` / `GAP-C5-01` (P0 — Crítico):** La prueba de snapshot del empaquetador contiene lógica de auto-creación: si el archivo oráculo no existe, lo genera sobre la marcha y retorna éxito de forma transparente. Un Regression Gate jamás debe aprobar la ejecución si el oráculo está ausente.

* **`E-0.4-382` / `GAP-C5-02` (P1 — Alto):** El bucle de validación del snapshot solo compara un subconjunto de los campos del DTO serializado. Mutaciones críticas en campos no verificados pasan desapercibidas.

* **`E-0.4-389` / `GAP-C5-04` (P1 — Alto):** Ausencia de una fuente centralizada y declarativa para la configuración del tooling de validación (rutas de descubrimiento, marcadores de ejecución, umbrales de cobertura, analizadores estáticos).

* **`E-0.4-390` / `GAP-C5-05` (P0 — Crítico):** No existe evidencia material de canalizaciones automatizadas de integración continua configuradas en el repositorio. No hay una barrera de control remota que bloquee la incorporación de cambios si una aserción de regresión falla.

* **`P3-H04` (P0 — Crítico):** El laboratorio de benchmark ejecuta un parser legacy basado en expresiones regulares de Markdown, en lugar del adaptador de producción (`ExtractionProvider` → `DocumentLayout` → `FlatASTBuilder`). Las métricas de laboratorio están viciadas al medir un modelo semántico obsoleto.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Independencia e Inmutabilidad del Oráculo
1. Todo oráculo de regresión **MUST** ser generado de forma independiente al código bajo prueba, mediante una herramienta de bootstrap explícita invocada manualmente por el desarrollador.
2. Los oráculos **MUST NOT** ser mutados, reasignados, sobreescritos o eludidos condicionalmente durante la ejecución de pruebas.
3. La ausencia de un oráculo de regresión durante una prueba **MUST** causar un error terminal e inmediato. La auto-generación silenciosa de baselines está prohibida.
4. La generación de oráculos **MUST** estar estrictamente separada de la ejecución normal de la suite de pruebas y requerir una invocación explícita.

### 5.2 Oráculos como Evidencia Arquitectónica
5. Los oráculos de regresión constituyen evidencia arquitectónica y, por tanto, **MUST** formar parte de la línea base del sistema.
6. Los oráculos **MUST** estar versionados, protegidos contra mutación accidental y sujetos al mismo contrato de reproducibilidad que el resto de los artefactos gobernados.

### 5.3 Compuertas de Integración Continua
7. **MUST** existir una plataforma declarativa de integración continua que ejecute automáticamente la suite completa de pruebas ante cada evento de incorporación de cambios.
8. La compuerta de integración continua **MUST** bloquear técnicamente la incorporación de cambios mientras exista cualquier incumplimiento de las invariantes de regresión.
9. La configuración del tooling de validación **MUST** estar centralizada en una única fuente declarativa.

### 5.4 Alineación del Benchmark con Producción
10. El laboratorio de benchmark **MUST** instanciar exactamente los mismos patrones de extracción y construcción de AST cableados en el Composition Root de producción.
11. **MUST NOT** utilizarse rutas alternativas de ingesta, parsers legacy ni adaptadores de prueba en la evaluación del benchmark.
12. Todo parser o adaptador de ingesta que no forme parte del pipeline de producción **MUST** ser retirado del repositorio o marcado como deprecated con un ADR explícito.

### 5.5 Exhaustividad y Determinismo de Pruebas
13. Las pruebas de regresión **MUST** comparar el 100% de los campos del DTO bajo prueba, no un subconjunto arbitrario.
14. Las pruebas de regresión **MUST NOT** sustituir artificialmente los componentes principales del pipeline mediante mecanismos de interceptación o reemplazo de comportamiento.
15. Las pruebas **MUST** ser deterministas: dos ejecuciones consecutivas sobre el mismo input **MUST** producir resultados idénticos.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Las regresiones estructurales, semánticas y topológicas dejan de incorporarse silenciosamente al sistema, garantizando la integridad del pipeline de producción.
* La suite de pruebas se convierte en una barrera científica real, no en una colección de aserciones tautológicas que generan falsa confianza.
* El laboratorio de benchmark recupera validez académica al evaluar el pipeline de producción real, no una ruta legacy desalineada.
* La ausencia de oráculos se convierte en un fallo explícito, previniendo la degradación silenciosa de la cobertura de regresión.
* La gobernanza de la validación queda centralizada en una única configuración declarativa.
* Los resultados de la integración continua pasan a constituir evidencia objetiva del cumplimiento de las invariantes arquitectónicas del sistema.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que la plataforma de integración continua existe y está configurada como barrera bloqueante.
  * Verificación de que existe una configuración declarativa única del tooling de validación.
  * Verificación de la ausencia de asignaciones tautológicas de oráculos en la suite de pruebas.
  * Verificación de la ausencia de mecanismos de interceptación sobre componentes principales del pipeline en pruebas de integración.

* **Validation (dinámica/comportamental):**
  * Una mutación deliberada en la salida del parser **MUST** ser detectada por la compuerta de integración continua y bloquear la incorporación.
  * La eliminación de un archivo oráculo **MUST** causar un fallo terminal en la ejecución de pruebas.
  * El benchmark **MUST** producir métricas topológicas consistentes con el pipeline de producción.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el Principio 6 (Golden Corpus Driven Development) y la Invariante de Determinismo y Reproducibilidad. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-01` | **Dependencia directa:** los oráculos de regresión se serializan mediante el contrato canónico de AST. |
| `NADR-F17BIS-03` | **Dependencia directa:** los fingerprints de regresión se calculan mediante el hashing semántico determinista. |
| `NADR-F17BIS-02` | **Influencia:** la alineación del benchmark con producción exige el adaptador de ingesta gobernado por NADR-02. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `1.1.1`, `1.1.2`, `1.1.3` y `2.2.3` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la implementación interna de los oráculos de regresión ni la estructura de datos de los snapshots (responsabilidad del dominio de pruebas).
* **No gobierna** la plataforma concreta de automatización de integración continua.
* **No gobierna** la curaduría del Golden Corpus ni la materialización del Ground Truth (Fases 4-5 de la 17-BIS).
* **No gobierna** la taxonomía de criticidad de nodos ni las políticas de regresión topológica graduada (responsabilidad de `NADR-F17BIS-08`).
* **No gobierna** la composición del pipeline de producción ni el cableado de adaptadores (responsabilidad de `NADR-F17BIS-11`).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.