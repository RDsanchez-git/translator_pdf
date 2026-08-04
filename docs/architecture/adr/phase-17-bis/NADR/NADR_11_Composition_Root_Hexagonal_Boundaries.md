# NADR-F17BIS-11: Composition Root & Hexagonal Boundaries

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-11`
* **Título:** Composition Root & Hexagonal Boundaries 
* **Clase de Decisión:** `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `DRAFT`
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Core Arch / Foundation Domain
* **Capacidad Arquitectónica:** CAP-005 (Hexagonal Physical Abstraction) — raíz de composición y enforcement global de fronteras
* **Evidencia Forense:** `OBS-P1-01`, `OBS-P1-02`, `OBS-P1-03`, `OBS-P1-05`, `OBS-P1-08`, `P1-C01`, `P4-06`, `OBS-P1-13`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (principios constitucionales de Arquitectura Hexagonal, inmutabilidad estricta y tipado explícito).
  * **Influencia:** `NADR-F17BIS-02` (pureza de la frontera de ingesta), `NADR-F17BIS-04` (cableado inmutable de validación), `NADR-F17BIS-05` (inyección del resolvedor de contexto real).
  * **Conflictúa con:** Toda raíz de composición múltiple, mutación post-construcción de dependencias, relajación de tipado en fronteras y fuga de infraestructura al dominio.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S1)
* **Operacional:** 5 — Múltiples puntos de entrada construyen el pipeline de forma parcial o divergente, produciendo comportamientos distintos según el modo de invocación.
* **Mantenibilidad:** 5 — La mutación post-construcción de colaboradores oculta el grafo de dependencias y dificulta la evolución del sistema.
* **Recuperabilidad:** 3 — La fuga de infraestructura al dominio acopla el núcleo a tecnologías concretas, imposibilitando el reemplazo aislado de adaptadores.
* **Seguridad:** 3 — El tipado laxo (`Any`) en fronteras desactiva el análisis estático, permitiendo la inyección de colaboradores incompatibles sin detección temprana.
* **Financiero:** 2 — La divergencia entre modos de ejecución impide la optimización homogénea del stack de inferencia.
* **Total Score: 18/25**

---

## 3. CONTEXTO Y EVIDENCIA FORENSE

### 3.1 Problema arquitectónico

La arquitectura del sistema adolece de cuatro defectos estructurales que comprometen la pureza hexagonal, la unicidad del cableado y la verificabilidad estática del grafo de dependencias:

1. **Raíz de composición dividida.** No existe un único punto de verdad para el ensamblaje del pipeline. Múltiples puntos de entrada asumen responsabilidades de instanciación que deberían estar centralizadas, produciendo pipelines incompletos o desalineados según el modo de invocación.

2. **Mutación post-construcción de colaboradores.** Dependencias críticas se inyectan mediante asignación imperativa de atributos tras la instanciación, en lugar de a través del constructor. Esto oculta el grafo real de dependencias, rompe la inmutabilidad del wiring y permite estados parcialmente configurados.

3. **Relajación de tipado en fronteras.** Las funciones de composición aceptan colaboradores tipados como `Any`, desactivando la verificación estática del contrato de los colaboradores inyectados y permitiendo la inyección de objetos incompatibles sin detección en tiempo de análisis.

4. **Fuga de infraestructura al dominio.** Componentes ubicados dentro del espacio de nombres del dominio importan directamente adaptadores concretos de infraestructura, invirtiendo la regla de dependencia de la Arquitectura Hexagonal y acoplando el núcleo a tecnologías específicas.

### 3.2 Manifestación concreta identificada por la auditoría

* **`OBS-P1-02` (P1):** El punto de entrada CLI asume manualmente la instanciación e interconexión de la infraestructura de inferencia, FinOps y concurrencia, duplicando responsabilidades que la fábrica central debería cubrir. Si el pipeline se invoca desde otro punto de entrada (API, daemon), se corre el riesgo de construir un pipeline incompleto.

* **`OBS-P1-03` (P1):** La función de fábrica central relaja el tipo del despachador a `Any`, mientras el orquestador exige un contrato estricto. El analizador estático es incapaz de validar la interfaz del colaborador en la frontera de inyección.

* **`P4-06` / `OBS-P1-08` (P1):** La fábrica y el punto de entrada CLI inyectan colaboradores mediante asignación imperativa post-construcción (`dispatcher.validation_pipeline = ...`, `job.enter_step = proxy_enter_step`), violando el encapsulamiento y la inmutabilidad del wiring.

* **`OBS-P1-01` / `P1-C01` (P0):** Un adaptador de persistencia ubicado dentro del espacio de nombres del dominio importa directamente un repositorio concreto de infraestructura, invirtiendo la regla de inversión de dependencias de la Arquitectura Hexagonal.

* **`OBS-P1-13` / `P1-C01` (P1):** El orquestador de aplicación instancia internamente colaboradores de dominio durante la ejecución del método de orquestación, en lugar de recibirlos inyectados, impidiendo la prueba aislada del orquestador.

### 3.3 Fundamento arquitectónico

* **`ADR_F17_BIS_MASTER` (principio constitucional 7):** *"El dominio interior no poseerá dependencias de infraestructura, I/O local ni librerías de terceros no abstractas. Los adaptadores gestionarán exclusivamente la mutación tecnológica en las fronteras."*
* **`ENGINEERING_PRINCIPLES.md`:** Arquitectura Hexagonal (Ports and Adapters), Inmutabilidad de DTOs, Explicit over Implicit.

---

## 4. DECISIÓN EJECUTIVA

**Existe una única raíz de composición exclusiva e inmutable, responsable del ensamblaje completo del pipeline, y todas las fronteras del sistema están gobernadas por la regla de inversión de dependencias de la Arquitectura Hexagonal.**

En consecuencia:
* Todo ensamblaje del pipeline de producción debe converger en un único punto de composición.
* Todo colaborador debe ser inyectado por constructor en el momento de la instanciación, prohibiéndose la mutación post-construcción del grafo de dependencias.
* Toda frontera entre capas debe estar tipada de forma estricta mediante contratos abstractos, sin relajación a `Any` ni duck-typing.
* El dominio nunca debe depender de adaptadores concretos de infraestructura; la dependencia fluye exclusivamente desde la infraestructura hacia el dominio.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Exclusividad de la raíz de composición
1. **MUST** existir una única raíz de composición responsable del ensamblaje completo del pipeline de producción.
2. Todo punto de entrada (CLI, API, daemon, herramienta de evaluación) **MUST** delegar la construcción del pipeline a la raíz de composición.
3. **MUST NOT** existir construcción parcial o divergente del pipeline fuera de la raíz de composición.
4. La raíz de composición **MUST** producir un pipeline completamente cableado y operativo, sin colaboradores pendientes de inyección.

### 5.2 Inmutabilidad del wiring
5. Todo colaborador del pipeline **MUST** ser inyectado por constructor en el momento de la instanciación.
6. **MUST NOT** existir asignación imperativa de colaboradores mediante mutación de atributos post-construcción.
7. **MUST NOT** existir reasignación de métodos de entidades de dominio para inyectar side-effects de presentación o observabilidad.
8. El grafo de dependencias **MUST** quedar completamente definido al término de la instanciación.

### 5.3 Tipado estricto de fronteras
9. Toda función de composición **MUST** declarar el tipo estricto de los colaboradores inyectados mediante contratos abstractos.
10. **MUST NOT** utilizarse `Any`, duck-typing ni introspección por atributo (`hasattr`) como mecanismo de relajación de tipos en las fronteras de inyección.
11. Los contratos abstractos del dominio **MUST** ser verificables por el analizador estático de tipos en todos los puntos de inyección.

### 5.4 Inversión de dependencias
12. El dominio **MUST NOT** importar ni depender de adaptadores concretos de infraestructura.
13. Toda dependencia entre capas **MUST** fluir desde la infraestructura hacia el dominio, nunca en sentido inverso.
14. Los adaptadores de infraestructura **MUST** implementar los contratos abstractos definidos por el dominio, no al revés.
15. **MUST** existir un mecanismo de verificación estática que detecte y bloquee las fugas de infraestructura hacia el dominio como parte de la compuerta de integración continua.

### 5.5 Inyección limpia de procesadores de dominio
16. Los procesadores especializados del dominio (clasificadores, enriquecedores, validadores) **MUST** ser inyectados al orquestador desde la raíz de composición.
17. **MUST NOT** instanciarse colaboradores especializados internamente durante la ejecución de los métodos de orquestación.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El pipeline deviene idéntico independientemente del punto de entrada que lo invoque, eliminando la divergencia de comportamiento entre modos de ejecución.
* El grafo de dependencias queda completamente visible en la raíz de composición, facilitando la evolución, el diagnóstico y la prueba aislada de cada colaborador.
* El análisis estático de tipos recupera la capacidad de detectar incompatibilidades de contrato en el momento de la inyección, previniendo fallos en tiempo de ejecución.
* El dominio queda efectivamente aislado de las tecnologías concretas, habilitando el reemplazo de adaptadores sin modificación del núcleo.
* La verificación estática de fronteras hexagonales pasa a ser un Required Status Check bloqueante en la integración continua.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de la exclusividad de la raíz de composición mediante análisis del grafo de llamadas de los puntos de entrada.
  * Verificación de la ausencia de mutación post-construcción de colaboradores (análisis estático de asignaciones de atributos sobre objetos del pipeline).
  * Verificación del tipado estricto en las fronteras de inyección (ausencia de `Any` y duck-typing).
  * Verificación del cumplimiento de la frontera hexagonal mediante contratos de análisis estático que impidan importaciones inversas desde el dominio hacia la infraestructura.
* **Validation (dinámica/comportamental):**
  * Un pipeline construido desde cualquier punto de entrada **MUST** producir el mismo comportamiento observable sobre el mismo input.
  * El analizador estático **MUST** reportar error ante la inyección de un colaborador que no satisface el contrato abstracto declarado.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa los principios constitucionales de Arquitectura Hexagonal, inmutabilidad estricta y tipado explícito. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-02` | **Influencia recíproca:** NADR-02 gobierna la pureza de la frontera de ingesta; NADR-11 gobierna el enforcement global de todas las fronteras, incluida la de ingesta. |
| `NADR-F17BIS-04` | **Dependencia inversa:** el cableado inmutable de los pipelines de validación es un caso particular de la inmutabilidad del wiring gobernada por este NADR. |
| `NADR-F17BIS-05` | **Dependencia inversa:** la inyección del resolvedor de contexto real es responsabilidad de la raíz de composición gobernada por este NADR. |
| `NADR-F17BIS-10` | El enforcement estático de fronteras hexagonales **MUST** integrarse como Required Status Check en la compuerta de CI gobernada por NADR-10. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `2.1.1` y `2.1.4` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la pureza específica de la frontera de ingesta (responsabilidad de `NADR-F17BIS-02`).
* **No gobierna** el cableado específico de los pipelines de validación (responsabilidad de `NADR-F17BIS-04`).
* **No gobierna** la inyección específica del resolvedor de contexto (responsabilidad de `NADR-F17BIS-05`).
* **No gobierna** la configuración de la compuerta de CI ni los Required Status Checks (responsabilidad de `NADR-F17BIS-10`).
* **No gobierna** la ontología del AST V2 ni los contratos abstractos de los colaboradores (Fase 16, congelada).
* **No gobierna** la infraestructura física de almacenamiento, redes ni ejecución (responsabilidad de los respectivos NADRs de capacidad).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.