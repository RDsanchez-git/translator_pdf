# HITO_0.4.1_TOPOLOGY_EVALUATION_AUDIT.md
## Topology Evaluation & Tree Edit Distance Forensic Audit — Reporte Sub-Hito 0.4.1

* **Estado:** FROZEN / CONGELADO (Sub-Hito 0.4.1)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Solo lectura / Auditoría analítica del motor algebraico de distancia, estrategias de particionado y políticas de costo. Cero mutaciones en código productivo. Disposición diferida al Hito 0.5 (`UNASSESSED`).

---

## 1. PROPÓSITO Y ALCANCE DEL SUB-HITO 0.4.1

El **Sub-hito 0.4.1** audita la arquitectura del motor de comparación de árboles, los algoritmos de distancia de edición (*Tree Edit Distance - TED*), el alineamiento de anclas por secuencias (LCS), el particionado por ventanas y las políticas de demeritación métrica.

Se evalúa la separación entre orquestación y matemática pura en `core/benchmark/topology/`, la gestión de bosques de múltiples raíces y los costos operacionales del sistema.

---

## 2. REGISTRO DE EVIDENCIA FORENSE Y FORTALEZAS (E-0.4-001 a E-0.4-006)

### Evidencia E-0.4-001: Desacoplamiento entre Orquestación y Algoritmo Matemático
* **Archivos Fuente Primarios:** `core/benchmark/topology/evaluators/ted.py`, `core/benchmark/topology/engines/zhang_shasha/tree.py`
* **Símbolos Auditados:** `TreeEditDistanceEvaluator`, `ZhangShashaTreeDistanceCalculator`
* **Análisis Forense:** `TreeEditDistanceEvaluator` actúa como un *Application Service* puro: coordina alineamiento, particionado, motor inyectado y normalización. No contiene lógica del algoritmo de Zhang-Shasha ni manejo de matrices DP. La matemática está 100% aislada detrás de la interfaz `TreeDistanceAlgorithm`.

---

### Evidencia E-0.4-002: Pureza Algebraica del Modelo de Costos (`TreeEditCostContext`)
* **Archivos Fuente Primarios:** `core/benchmark/topology/costs/unit.py`, `core/benchmark/topology/engines/zhang_shasha/forest.py`
* **Símbolos Auditados:** `UnitCostContext`, `ForestDistanceCalculator`
* **Análisis Forense:** Las ecuaciones de recurrencia de Zhang-Shasha no consultan la lógica de negocio ni inspeccionan condicionales de tipo (`if node_type == ...`). Requerimientos de costo se delegan de forma referencialmente transparente al puerto `TreeEditCostContext`.

---

### Evidencia E-0.4-003: Estructura Modular del Pipeline TED
* **Archivo Fuente Primario:** `core/benchmark/topology/evaluators/ted.py`
* **Símbolo Auditado:** `TreeEditDistanceEvaluator.evaluate()`
* **Análisis Forense:** El flujo sigue una secuencia unidireccional desacoplada:
  $$\text{Alignment (LCS)} \longrightarrow \text{Partition (Windows)} \longrightarrow \text{Engine (DP/Zhang-Shasha)} \longrightarrow \text{Normalization}$$
  Cada etapa está acoplada a un protocolo/puerto específico, lo que permite sustituir cualquier componente sin alterar el resto del pipeline.

---

### Evidencia E-0.4-004: Neutralización Matemáticamente Segura de la Raíz Virtual
* **Archivos Fuente Primarios:** `core/benchmark/topology/engines/zhang_shasha/indexer.py`, `forest.py`
* **Símbolos Auditados:** `PostorderIndexer.build()`, `ForestDistanceCalculator._del_cost()`, `_ins_cost()`, `_sub_cost()`
* **Análisis Forense:**
  ```python
  def _del_cost(self, node: ASTNode, costs: TreeEditCostContext) -> float:
      return 0.0 if node.node_id == VIRTUAL_ROOT_ID else costs.deletion_cost(node)
  ```
  Para soportar bosques inconexos de múltiples raíces, `PostorderIndexer` sintetiza un nodo `VIRTUAL_ROOT_ID`. `ForestDistanceCalculator` intercepta dicho identificador y fuerza su costo de borrado, inserción y sustitución a `0.0`, garantizando que la raíz virtual no distorsione la distancia real de edición.

---

### Evidencia E-0.4-005: Aislamiento de Recurrencia Tree vs. Forest
* **Archivos Fuente Primarios:** `core/benchmark/topology/engines/zhang_shasha/tree.py`, `forest.py`
* **Símbolos Auditados:** `ZhangShashaTreeDistanceCalculator`, `ForestDistanceCalculator`
* **Análisis Forense:** `TreeDistanceCalculator` administra el recorrido de los *keyroots* y la tabla global `TreeDistanceTable`, delegando la resolución de sub-bosques en cada celda a `ForestDistanceCalculator`. Esto maximiza la testabilidad unitaria de las ecuaciones de recurrencia.

---

### Evidencia E-0.4-006: Inyección de Dependencias Limpia en Bootstrap
* **Archivo Fuente Primario:** `bootstrap/topology.py`
* **Símbolo Auditado:** `create_topology_evaluator()`
* **Análisis Forense:** El ensamblado del grafo de objetos ocurre en el *Imperative Shell* del bootstrap. Las clases concretas del motor (`ForestDistanceCalculator`, `ZhangShashaEngine`, `UnitCostContext`) se inyectan satisfaciendo las abstracciones del dominio (`TreeEditEngine`, `TreeEditCostContext`).

---

## 3. REGISTRO DE OBSERVACIONES Y PUNTOS DE MEJORA (OBS-0.4.1-01 a OBS-0.4.1-04)

| ID Observación | Componente | Comportamiento Observado | Impacto Arquitectónico / Riesgo |
| :--- | :--- | :--- | :--- |
| **OBS-0.4.1-01** | `DefaultNodeMatchingPolicy` | `MatchingKey` se compone con igualdad textual directa: `f"{node.node_type}:{node.text_content}"`. | **Sensibilidad Cero a Tolerancia:** Un espacio sobrante o cambio de mayúscula invalida la coincidencia del ancla en la clave de alineamiento. |
| **OBS-0.4.1-02** | `EntityRecallEvaluator` | La complejidad lineal $O(N)$ depende de la entropía de `MatchingKey`. | **Riesgo de Performance:** Si la política produce colisiones masivas en los buckets, el recorrido sobre `gt_buckets` degrada la performance. |
| **OBS-0.4.1-03** | `TreeEditDistanceEvaluator` | Recalcula el costo total sumando `deletion_cost` e `insertion_cost` iterando sobre ambos ASTs al final. | **Costo de Recorrido Redundante:** Genera $O(N)$ iteraciones adicionales tras haber evaluado las ventanas del bosque. |
| **OBS-0.4.1-04** | Dualidad `core/` vs `tools/` | Coexistencia de `ZhangShashaEngine` (`core/`) y `StructuralTopologyMetric` (`tools/` acoplado a `apted`). | **Duplicación de Infraestructura:** Se mantienen dos subsistemas independientes para calcular Tree Edit Distance. |

---

## 4. AST & TOPOLOGY CAPABILITY MATRIX (REFINADA)

| Dimensión Evaluable | Subdominio Nativo (`core/benchmark/topology`) | Herramienta CLI (`tools/evaluation/topology`) |
| :--- | :--- | :--- |
| **Arquitectura** | Clean Architecture / Ports & Adapters purificados | Métrica plana acoplada a gema externa (`apted`) |
| **Algoritmo Base** | Zhang-Shasha (Python puro, $O(M^2 N^2)$ amortiguado) | APTED ($O(M^3 N)$ en C/Python) |
| **Particionado Escalable** | **SÍ:** Ventanas acotadas vía Alineamiento LCS | **NO:** Intenta procesar el árbol completo |
| **Modelo de Costos** | Flexible vía `TreeEditCostContext` (`UnitCostContext`) | Fijo vía `CostMatrix` |
| **Raíz Virtual** | Trato explícito de costo cero (`0.0`) | Construcción de raíz artificial `("Document", "root")` |
| **Ponderación por Tipo** | Pendiente de matriz de pesos por criticidad (`DC-06`) | Costo de rename diferenciado (0.5 vs 2.0) |

---

## 5. DISPOSICIÓN ARQUITECTÓNICA Y RECOMENDACIÓN DE ACCIÓN

1. **Consolidación sobre la Rama Nativa (`DC-10`):** El subdominio en `core/benchmark/topology/` presenta una arquitectura sólida. Se recomienda estandarizar la evaluación de la Baseline sobre este motor nativo, descartando la dependencia de `apted` en `tools/`.
2. **Normalización en `MatchingKey` (`DC-09`):** Inyectar una política de sanitización básica (stripping de espacios, normalización Unicode) en `DefaultNodeMatchingPolicy` para evitar fallos de anclaje por variaciones triviales de maquetación.
3. **Matriz de Ponderación por Criticidad (`DC-06`):** Extender `TreeEditCostContext` en el Hito 0.5 para asignar penalizaciones diferenciadas según la severidad del nodo (`HEADING` > `PARAGRAPH`).

---

## 6. DECLARACIÓN DE CIERRE DEL SUB-HITO 0.4.1

El **Sub-hito 0.4.1 (Topology Evaluation Audit)** queda **COMPLETADO Y CONGELADO (`FROZEN`)**.