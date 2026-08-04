# NADR-F17BIS-06: Token Estimation & Compilation Governance

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-06`
* **Título:** Token Estimation & Compilation Governance
* **Clase de Decisión:** `OPERATIONAL` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `PROPOSED`
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsables Técnicos:** FinOps Domain / Compiler Domain / Render Domain
* **Capacidades Arquitectónicas:** CAP-007 (Budgeting & Token Estimation), CAP-009 (Sandboxed Artifact Compilation), CAP-010 (TeX Syntax Protection)
* **Evidencia Forense:** `P4-04`, `P6-H04`, `P6-H01`
* **Referencias Cruzadas:**
  * **Ortogonal con:** `NADR-F17BIS-09` (frontera física de ejecución y aislamiento de I/O del compilador).
  * **Influencia:** `NADR-F17BIS-08` (el plano de ejecución consume presupuestos de tokens precisos).
  * **Relacionado con:** `NADR-F17BIS-04` (la validación precede a la compilación).
  * **Conflictúa con:** Estimación heurística por conteo de palabras, escapado ciego de sintaxis, y reconstrucción ad-hoc del ensamblado.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operacional:** 5 — La subestimación de tokens provoca desbordamientos de contexto en la API; el escapado ciego corrompe sintaxis TeX legítima; el bypass del servicio de compilación anula las políticas de tolerancia a fallos y la verificación de integridad.
* **Mantenibilidad:** 3 — Deuda técnica reconocida en el escapador y duplicación de lógica de ensamblado fuera del servicio canónico.
* **Recuperabilidad:** 3 — Artefactos corruptos o ensamblados ad-hoc dificultan el diagnóstico y la reconstrucción determinista.
* **Seguridad:** 1
* **Financiero:** 4 — La subestimación de tokens en contenido científico denso produce errores de desbordamiento y desperdicio de presupuesto FinOps.
* **Total Score: 16/25**

---

## 3. DECISIÓN EJECUTIVA

**La fidelidad del contenido científico debe preservarse en todas las fronteras de transformación del pipeline de compilación: la medición del presupuesto para inferencia, la protección de la sintaxis durante el renderizado y la orquestación del ensamblado final.**

Esta decisión se articula en tres dominios normativos ortogonales:

1. **Precisión de la estimación de tokens (CAP-007):** El mecanismo de estimación presupuestaria debe ser semánticamente compatible con el tokenizador real del proveedor de inferencia, no una heurística de conteo de palabras que ignore la densidad de sub-palabras del contenido matemático y técnico.

2. **Protección de sintaxis TeX en el renderizado (CAP-010):** La capa de renderizado debe preservar intacta la sintaxis matemática y TeX legítima, aplicando un escapado consciente del contexto que distinga el texto literal a escapar del marcado legítimo que debe transitar sin alteración.

3. **Gobernanza de la orquestación de compilación (CAP-009):** El ensamblado del artefacto final debe estar gobernado por el servicio de compilación canónico y sus políticas de tolerancia a fallos e integridad, sin reconstrucciones ad-hoc que las eludan.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Subestimación FinOps por Heurísticas de Conteo de Palabras (`P4-04`)
* **Mecanismo Causal:** El calculador de presupuesto de prompts y el servicio de medición de inferencia emplean un estimador que calcula tokens multiplicando la cantidad de palabras (vía `split()`) por una constante fija de $1.3$.
* **Impacto Arquitectónico:** Una ecuación LaTeX compleja (por ejemplo `\begin{equation}\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\end{equation}`) contiene una sola palabra bajo la lógica de `split()`, pero equivale a más de $20$ tokens para los tokenizadores BPE reales. En documentos científicos densos en fórmulas, la estimación subestima el tamaño del prompt por un orden de magnitud, provocando desbordamientos de ventana de contexto (`ContextOverflowError`) y presupuestación FinOps incorrecta.

### 4.2 Escapador TeX Ciego al Contexto (`P6-H04`)
* **Mecanismo Causal:** El escapador de caracteres TeX realiza una sustitución ciega de caracteres reservados (`\`, `&`, `%`, `$`, `{`, `}`). El propio código fuente reconoce la deuda técnica: *"Este escaper es ciego al contexto. TODO: Migrar a un Lexer AST-aware o inyectar contexto de escape."*
* **Impacto Arquitectónico:** Si el texto contiene comandos o entornos LaTeX legítimos que entraron por el canal de traducción (por ejemplo `\textbf{enunciado}` o `$E=mc^2$`), el escapador los convierte en `\textbackslash{}textbf\{enunciado\}` y `\$E=mc\^2\$`, destruyendo la sintaxis y provocando errores de compilación en el motor TeX.

### 4.3 Desconexión del Núcleo de Compilación (`P6-H01`)
* **Mecanismo Causal:** El daemon de ensamblado extrae las proyecciones directamente del repositorio materializado y reconstruye la lista de unidades de renderizado manualmente en un bucle, sin invocar el servicio de compilación ni el ensamblador de documentos canónicos.
* **Impacto Arquitectónico:** Las políticas institucionales de tolerancia a fallos (`AssemblyPolicy`), las reglas de degradación por ratio, la verificación de firmas SHA-256 y la validación de secuencias estrictas quedan completamente anuladas en el flujo de producción en segundo plano. El ensamblado ad-hoc elude las garantías de integridad del dominio.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Precisión de la Estimación de Tokens (CAP-007)
1. El mecanismo de estimación de tokens **MUST** producir estimaciones compatibles con el modelo de tokenización efectivo del proveedor de inferencia.
2. La estimación de tokens **MUST NOT** basarse en heurísticas de conteo de palabras que ignoren la estructura morfológica del contenido científico (ecuaciones, código, marcado técnico).
3. El cálculo presupuestario **MUST** reflejar la densidad real de sub-palabras del contenido matemático y técnico, evitando la subestimación sistemática que conduce a desbordamientos de contexto.
4. El mecanismo de estimación **MUST** ser inyectable y desacoplado, permitiendo su sustitución por un tokenizador compatible con el proveedor sin alterar la lógica de presupuestación.

### 5.2 Protección de Sintaxis TeX en el Renderizado (CAP-010)
5. La capa de renderizado **MUST** preservar intacta la sintaxis matemática y TeX legítima durante el escapado y sanitización.
6. El escapado de caracteres **MUST** ser consciente del contexto, distinguiendo el texto literal que requiere escapado del marcado TeX legítimo que debe transitar sin alteración.
7. **MUST NOT** aplicarse sustitución ciega de caracteres reservados dentro de regiones de marcado matemático o TeX legítimo.
8. La estrategia de escapado **MUST** ser verificable contra casos de prueba que incluyan sintaxis matemática válida, comandos TeX y delimitadores de entorno.

### 5.3 Gobernanza de la Orquestación de Compilación (CAP-009)
9. El ensamblado del artefacto final **MUST** estar gobernado por el servicio de compilación canónico y sus políticas de tolerancia a fallos e integridad.
10. Ningún componente del plano de ejecución **MUST** reconstruir o ensamblar artefactos de forma ad-hoc, eludiendo el servicio de compilación canónico.
11. El ensamblado **MUST** aplicar, sin elusión, la validación de secuencia, la verificación de integridad criptográfica y las políticas de degradación definidas por el servicio de compilación canónico.
12. Las decisiones de aceptación o rechazo del documento **MUST** emanar de las políticas del dominio de compilación, no de lógica de reconstrucción incrustada en el plano de ejecución.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La presupuestación FinOps deviene precisa para contenido científico denso, eliminando los desbordamientos de contexto causados por subestimación de tokens en fórmulas y marcado técnico.
* La sintaxis matemática y TeX legítima sobrevive intacta al ciclo de renderizado, eliminando la corrupción de comandos y delimitadores durante el escapado.
* El ensamblado del artefacto final recupera las garantías de integridad del dominio: validación de secuencia, verificación de firmas y políticas de tolerancia a fallos dejan de ser anuladas por reconstrucciones ad-hoc.
* La lógica de ensamblado se consolida en el servicio de compilación canónico, eliminando la duplicación de responsabilidades entre el plano de ejecución y el dominio.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el mecanismo de estimación de tokens es inyectable y no está acoplado a una heurística fija de conteo de palabras.
  * Verificación de que la capa de renderizado no aplica sustitución ciega de caracteres dentro de regiones de marcado legítimo.
  * Verificación de que el plano de ejecución no contiene lógica de reconstrucción de ensamblado que eluda el servicio de compilación canónico.

* **Validation (dinámica/comportamental):**
  * Un documento denso en ecuaciones LaTeX **MUST** producir una estimación de tokens compatible con el tokenizador del proveedor, sin desbordamiento de contexto.
  * Un fragmento con sintaxis matemática válida (`$E=mc^2$`, `\textbf{...}`, entornos `\begin{...}`) **MUST** sobrevivir intacto al renderizado.
  * El ensamblado de un documento **MUST** aplicar las políticas de tolerancia a fallos y verificación de integridad del servicio de compilación canónico, rechazando documentos corruptos en lugar de producir artefactos inválidos.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa los principios de *FinOps First* y de preservación de la fidelidad científica. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-09` | **Ortogonal:** NADR-09 gobierna la frontera física de ejecución y el aislamiento de I/O del compilador; este NADR gobierna la estimación, el renderizado y la orquestación lógica del ensamblado. |
| `NADR-F17BIS-08` | **Influencia:** el plano de ejecución distribuido consume presupuestos de tokens precisos para el despacho y el rate limiting. |
| `NADR-F17BIS-04` | **Relacionado:** la validación de contenido precede a la compilación del artefacto final. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `4.2.1`, `4.2.2` y `4.2.3` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** el aislamiento físico de I/O del compilador ni las condiciones de carrera en la escritura de artefactos (responsabilidad de `NADR-F17BIS-09`).
* **No gobierna** la integridad de eventos de la FSM ni la veracidad de nomenclatura de los ejecutores de infraestructura (responsabilidad de `NADR-F17BIS-09`).
* **No gobierna** el cableado del pipeline de validación ni el retiro de adaptadores heredados (responsabilidad de `NADR-F17BIS-04`).
* **No gobierna** el rate limiting distribuido, el circuit breaker ni el plano de ejecución (responsabilidad de `NADR-F17BIS-08`).
* **No prescribe** el tokenizador concreto ni el lexer TeX específico a utilizar (detalle de implementación).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.