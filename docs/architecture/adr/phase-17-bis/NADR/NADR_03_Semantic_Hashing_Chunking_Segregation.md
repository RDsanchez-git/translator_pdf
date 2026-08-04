# NADR-F17BIS-03: Semantic Hashing & Chunking Segregation

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-03`
* **Título:** Semantic Hashing & Chunking Segregation
* **Clase de Decisión:** `DATA` / `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** AST Domain
* **Capacidad Arquitectónica:** CAP-002 (Semantic Hashing & Identity)
* **Evidencia Forense:** `E-0.1-003`, `E-0.3-001`, `E-0.3-003`, `E-0.2-007`, `GAP-P3-03`, `GAP-P3-04`, `GAP-P3-05`, `P3-H02`, `P3-H05`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-01` (la firma opera sobre la representación canónica).
  * **Influencia:** `NADR-F17BIS-08` (el linaje CQRS consume la firma real), `NADR-F17BIS-10` (los oráculos de regresión se comparan sobre firmas estables).
  * **Conflictúa con:** Toda firma que incorpore identificadores de runtime.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S1)
* **Operacional:** 5 — La firma inestable rompe el linaje en FSM/CQRS: el hash registrado no coincide con el contenido despachado, estancando documentos y corrompiendo la rematerialización.
* **Mantenibilidad:** 4 — Dos responsabilidades arquitectónicas distintas coexisten por contaminación en un mismo componente, impidiendo su evolución independiente.
* **Recuperabilidad:** 4 — Un linaje criptográfico no reproducible imposibilita la reconstrucción determinista de proyecciones tras un fallo.
* **Seguridad:** 2
* **Financiero:** 2 — La inestabilidad de firmas invalida cachés de inferencia y fuerza re-ejecuciones costosas.
* **Total Score: 17/25**

---

## 3. DECISIÓN EJECUTIVA

La organización establece que **la identidad criptográfica del AST y el empaquetado de unidades de traducción constituyen dos capacidades arquitectónicas independientes, gobernadas por superficies normativas distintas**.

La firma criptográfica de un documento o sub-árbol **debe** ser determinista, reproducible de forma aislada y completamente agnóstica a los identificadores inyectados en runtime. Esta decisión materializa los principios constitucionales **Canonical AST Identity** y **Semantic Hash Determinism** definidos en el ADR Maestro.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Taxonomía tridimensional de la identidad (concepto arquitectónico)

Este NADR adopta formalmente la taxonomía tridimensional de la identidad establecida por la auditoría de la Fase 0 (Hito 0.3). No se trata de un detalle de implementación, sino de un **invariante arquitectónico**: ninguna dimensión puede suplantar a otra.

| Dimensión | Composición | Propósito | Gobernanza |
| :--- | :--- | :--- | :--- |
| **$H_{semantic}$** — Identidad Semántica | Tipo semántico, contenido normalizado, orden secuencial relativo, profundidad jerárquica | Firma criptográfica del documento; inmune a la volatilidad de runtime | **Este NADR** |
| **$H_{runtime}$** — Identidad Física/Runtime | `node_id`, `parent_node_id`, geometría, confianza, linaje de fragmentos | Trazabilidad operacional, renderizado, depuración | Operacional; excluida de toda firma |
| **$H_{baseline}$** — Identidad de Baseline | Encadenamiento global entre versión de corpus, firmas físicas y firmas semánticas | Inmutabilidad de la baseline científica | Fases 2 y 3 de la 17-BIS |

### 4.2 Firma acoplada a identidad efímera
* **`E-0.1-003` / `E-0.3-001` (P0):** La función de firma del AST incluye el atributo `node_id` en el pre-image serializado. Dado que la segmentación multi-oracional asigna UUIDs aleatorios a los fragmentos (**`E-0.3-003`**), dos ASTs con contenido semántico idéntico producen firmas divergentes en cada ejecución.
* **`E-0.2-007`:** El subsistema de evaluación ya resolvió este problema de forma aislada mediante una huella semántica sobre `(node_type, content)`, ignorando `node_id`. Existe por tanto una incoherencia de diseño entre la firma criptográfica oficial y la evaluación topológica.

### 4.3 Desalineación cronológica de la firma
* **`GAP-P3-05` / `P3-H05`:** La firma se calcula sobre los nodos **antes** de que la estructura sea enriquecida. El hash registrado como linaje no corresponde al AST que finalmente se despacha, ensambla y persiste.

### 4.4 Contaminación ontológica del módulo de firma
* **`GAP-P3-03` / `P3-H02`:** El componente cuya responsabilidad declarada es el cálculo de firmas aloja por contaminación la lógica completa de empaquetado de unidades de traducción (agrupadores semánticos, presupuestos de tokens, fragmentación por oraciones y construcción de unidades), mientras el subdominio formal de empaquetado permanece inalcanzable en runtime.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Identidad semántica de la firma
1. La firma criptográfica del AST **MUST** calcularse exclusivamente sobre la identidad semántica del documento: tipo semántico de cada nodo, contenido normalizado, orden secuencial relativo y posición jerárquica.
2. El pre-image de la firma **MUST NOT** incorporar ningún atributo cuya finalidad sea exclusivamente operacional, diagnóstica o de trazabilidad, y cuya variación no altere la identidad semántica del documento. A título enunciativo y no exhaustivo, quedan excluidos: identificadores de nodo y de parentesco, identificadores de sesión, proceso, worker, reintento o instancia de proveedor, geometrías espaciales y métricas de confianza.
3. El orden secuencial **MUST** expresarse por la posición dentro de la secuencia, no por el valor de identificadores numéricos asignados en runtime.
4. El contenido **MUST** someterse a normalización canónica antes de formar parte del pre-image.
5. La firma **MUST** ser independiente de la estrategia de generación de identidad de fragmentos (determinista o aleatoria).

### 5.2 Determinismo y reproducibilidad
6. La firma **MUST** ser determinista: el mismo contenido semántico **MUST** producir la misma firma en toda ejecución, proceso o entorno.
7. El cálculo de la firma **MUST NOT** depender de estado externo no determinista (reloj, orden de inicialización, identificadores de proceso).

### 5.3 Coherencia cronológica del linaje
8. Toda firma registrada como linaje de una unidad de procesamiento **MUST** corresponder al estado exacto del contenido en el momento del registro.
9. **MUST NOT** registrarse firmas calculadas sobre estados previos del AST cuando el AST haya sido transformado estructuralmente con posterioridad al cálculo.

### 5.4 Segregación de capacidades
10. La capacidad de firma criptográfica y la capacidad de empaquetado **MUST** permanecer arquitectónicamente independientes y **MUST NOT** coexistir en un mismo componente.
11. La responsabilidad de empaquetado **MUST** residir exclusivamente en el subdominio arquitectónico designado para dicho propósito.
12. El componente de firma **MUST** contener exclusivamente lógica de firma.
13. Los identificadores de runtime **MAY** existir para propósitos de trazabilidad operacional, pero **MUST** quedar restringidos a ese propósito y excluidos de toda firma semántica.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Las firmas dejan de depender de la estrategia de generación de identidad de fragmentos, eliminando una clase completa de no-determinismo.
* Toda baseline persistida bajo la fórmula anterior pierde vigencia: su firma deja de ser reproducible y **MUST** ser regenerada antes de poder ser invocada como oráculo. La ejecución operativa de dicha regeneración corresponde al Execution Plan.
* La capacidad de firma y la capacidad de empaquetado evolucionan de forma independiente, cada una bajo su propia superficie de pruebas.
* El linaje criptográfico registrado en FSM/CQRS pasa a corresponder exactamente con el contenido procesado, habilitando la rematerialización determinista.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de la pureza de la proyección del pre-image: ausencia de atributos excluidos por la regla 2 (property-based testing).
  * Verificación de la segregación: ausencia de símbolos y responsabilidades de empaquetado en el componente de firma.
* **Validation (dinámica/comportamental):**
  * **Determinismo:** dos cálculos consecutivos sobre el mismo AST producen firmas byte-idénticas.
  * **Independencia de identidad:** dos ASTs semánticamente idénticos con identificadores de runtime distintos producen la misma firma.
  * **Sensibilidad:** cualquier mutación de contenido, tipo u orden produce una firma distinta.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa los principios constitucionales *Canonical AST Identity* y *Semantic Hash Determinism*. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-01` | **Dependencia directa:** la firma opera sobre la representación canónica; el pre-image es una proyección semántica de dicha representación. |
| `NADR-F17BIS-08` | El linaje CQRS consume la firma real del documento; la corrección del hash desconocido depende de esta firma determinista. |
| `NADR-F17BIS-10` | Los oráculos de regresión se comparan sobre firmas estables definidas aquí. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `1.3.1` y `1.3.2` materializan estas reglas; el paso `MIG-01` ejecuta la regeneración de baselines derivada del cambio de fórmula. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** el formato de serialización de persistencia del AST ni la hidratación de nodos (responsabilidad de `NADR-F17BIS-01`). El pre-image de firma es una proyección semántica distinta de la serialización completa de persistencia.
* **No gobierna** el encadenamiento global de la identidad de baseline ($H_{baseline}$) entre hashes físicos, versiones de esquema y versiones de corpus (responsabilidad de las Fases 2 y 3 de la 17-BIS).
* **No gobierna** las políticas de empaquetado en sí mismas (atomicidad estructural, fronteras de chunk, presupuestos de tokens); gobierna exclusivamente la segregación de capacidades.
* **No gobierna** la estrategia de generación de identidad operacional de fragmentos, siempre que la firma permanezca independiente de ella.
* **No gobierna** la evaluación topológica ni las métricas de benchmark.
* **No prescribe** tareas de implementación, procedimientos de migración ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.