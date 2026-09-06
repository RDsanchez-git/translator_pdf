# HITO_5.3_ALGORITHMIC_COMPARABILITY_AND_TOPOLOGICAL_DISTANCE_AUDIT.md

**Estado:** FROZEN v1.1.3
**Fecha de emisión:** 2026-09-04
**Fecha de congelamiento:** 2026-09-04
**Fase:** 17-BIS — Fase 5 (Baseline Certification)
**Tipo de artefacto:** Algorithmic Comparability & Topological Distance Audit
**Naturaleza:** Read-only forensic audit. No se propone código de producción ni se materializan decisiones de implementación.

**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-18 (FROZEN), NADR-F17BIS-19 (FROZEN), HITO_5.0 v1.0.2 (FROZEN), HITO_5.1 v1.1.2 (FROZEN), HITO_5.2 v1.1.0 (FROZEN), FASE_4_HANDOFF (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN), ENGINEERING_PRINCIPLES.md (FROZEN), PROJECT_TREE.txt, PROJECT_SCOPE.md, código fuente verificado directamente en `tools/evaluation/topology/fingerprint.py`, `tools/evaluation/topology/metrics/structural.py`, `core/benchmark/topology/costs/unit.py`, `core/benchmark/topology/criticality/costs.py`, `core/benchmark/topology/engines/zhang_shasha/`.

**Mandato:** Determinar, mediante evidencia reproducible y matemáticamente comparable, si las implementaciones de distancia topológica ZhangShashaEngine y StructuralTopologyMetric (APTED) representan la misma magnitud matemática, reciben representaciones semánticamente equivalentes, utilizan modelos de costo equivalentes, aplican reglas de normalización equivalentes, producen resultados numéricamente comparables, y presentan divergencias atribuibles al algoritmo o únicamente a diferencias de implementación/preprocesamiento.

**Síntesis:** El análisis forense con verificación directa de código fuente revela **5 divergencias fundamentales** que demuestran que ZhangShashaEngine y StructuralTopologyMetric (APTED v1.0.3) **no calculan la misma función de distancia bajo la configuración actual**. Las divergencias son: (1) modelo de costo diferente (UnitCostContext sub=1.0 vs CostMatrix rename=0.5/2.0) — Divergencia de configuración; (2) normalización de texto diferente (UnitCostContext sin `.strip()` vs `semantic_fingerprint` con `.strip()`) — Divergencia de configuración; (3) raíz virtual diferente (condicional vs siempre) con impacto en denominador de normalización — Divergencia de representación; (4) metodología diferente (Σ TED(windows) vs TED(full tree)) — Divergencia matemática; (5) adapter `StructuralTopologyMetric` no integra actualmente `CriticalityAwareCostContext` — Defecto de integración (la librería APTED sí tiene capacidad para soportarlo, demostrado por la firma de `rename(node1, node2)`). La clasificación final es **C — Comparable but Non-Equivalent**.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-SKELETON | 2026-09-04 | Emisión inicial del esqueleto. |
| 1.0.1-SKELETON | 2026-09-04 | 7 correcciones. |
| 1.0.2-SKELETON | 2026-09-04 | 7 correcciones adicionales. |
| 1.0.0-FROZEN | 2026-09-04 | Análisis estático inicial. |
| 1.1.0-FROZEN | 2026-09-04 | Versión combinada con análisis en capas. |
| 1.1.1-FROZEN | 2026-09-04 | Corrección de duplicación de ID E-5.3-009 → E-5.3-017. |
| 1.1.2-FROZEN | 2026-09-04 | Revisión forense con verificación directa de código. |
| 1.1.3-FROZEN | 2026-09-04 | **Correcciones forenses finales:** (1) Q2: eliminado "CASI", reemplazado por clasificación falsable; (2) Q9: separado determinismo de reproducibilidad experimental; (3) Normalización unit-cost: condicionada a igualdad de cardinalidad efectiva; (4) Q8: reemplazado "subestima/sobrestima" por "asigna menor/mayor coste"; (5) Fecha corregida a 2026-09-04; (6) API de APTED verificada por evidencia directa del código (rename() demuestra capacidad de costes por nodo); (7) Columna "Naturaleza" agregada a tabla de GAPs; (8) .strip() verificado directamente en código fuente; (9) "No hay bugs algorítmicos" matizado a "No se identificó evidencia de divergencia atribuible a la definición del algoritmo"; (10) NADR-18 R11: APTED cambiado de "N/A" a "NO CUMPLE como adapter". |

---

## NOTA DE HERENCIA

Este HITO recibe de:

**HITO 5.0:** Estado de contratos de dominio. Gaps operacionales (DF-18, rutas hardcoded). E-5.0-024: pyright 0 errors.

**HITO 5.1:** Universo físico del corpus (7 identidades únicas candidatas). GAP-5.1-07: node_id serializado.

**HITO 5.2:** Estado operacional del tooling (DF-18). Atomicidad física de persistencia verificada.

**FASE_4_HANDOFF:** run_regression.py con exit codes 0/1/2. DF-04 como carry-forward. create_topology_evaluator() como composition root.

**DF-04 (formalizado):**
- **Descripción:** Dualidad ZhangShasha/APTED — benchmark comparativo.
- **Estado:** OPEN (carry-forward) → RESUELTO por este HITO con clasificación C.
- **Restricción:** Δ<1% NO es criterio de equivalencia.
- **Resolución:** Clasificación C — Comparable but Non-Equivalent.

---

## NOTA DE DESVIACIÓN ESTRUCTURAL (secciones 5-9)

Las secciones 5-9 de METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 no aplican a este tipo de HITO:

| Sección canónica | Sección reemplazo | Justificación |
|---|---|---|
| 5. Mapa de Flujos | 5. Estado Actual Conocido | Audita implementaciones |
| 6. Inventario Dimensiones | 6. Dependencias Externas | Caracteriza APTED |
| 7. Matriz ORD | 7. Análisis Comparativo en Capas | Compara algoritmos |
| 8. Mutation Semantics | 8. Divergencias Cuantificadas | Mide divergencias |
| 9. Canonicalization | 9. Matriz de Pilares | Verifica comparabilidad |

---

## 1. RESUMEN EJECUTIVO

Se ejecutó el análisis forense completo con **verificación directa de código fuente** (no solo PROJECT_TREE). La auditoría cubrió 4 lotes de código fuente y verificación explícita de archivos críticos. Se identificaron **15 evidencias forenses únicas** (5 P1, 2 P2, 8 verificaciones).

**Hallazgo central:**

> ZhangShashaEngine y StructuralTopologyMetric (APTED v1.0.3) **no calculan la misma función de distancia bajo la configuración actual**. Existen 5 divergencias fundamentales: (1) modelo de costo diferente; (2) normalización de texto diferente (`.strip()` vs sin `.strip()`); (3) raíz virtual con impacto en denominador de normalización; (4) metodología diferente (Σ TED(windows) vs TED(full tree)); (5) adapter APTED no integra CriticalityAwareCostContext (la librería sí tiene capacidad, demostrada por `rename(node1, node2)`). La clasificación final es **C — Comparable but Non-Equivalent**.

**Veredicto:** La evidencia es suficiente para que ADR_F17_BIS_05 tome una decisión informada. Las divergencias son de **configuración, representación y metodología**, no de definición algorítmica de Tree Edit Distance. No se identificó evidencia de divergencia atribuible a la definición del algoritmo TED. Ambos algoritmos resuelven el mismo problema matemático, pero las integraciones actuales reciben configuraciones diferentes.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Lo que este HITO puede establecer

- Inventario completo de implementaciones (verificado contra PROJECT_TREE y código directo).
- Compatibilidad contractual (interfaces, tipos, precondiciones).
- Equivalencia o diferencia de representación de entrada (verificada con código directo).
- Función de costo explícitamente comparada.
- Normalización comparada bajo diferentes modelos.
- Divergencias cuantificadas y clasificadas causalmente.
- Clasificación final de comparabilidad (A-F).
- Versión, licencia y mantenimiento de APTED.
- Capacidad de la API de APTED para costes variables (verificada por firma de métodos).

### 2.2 Lo que este HITO NO puede establecer

- La validez científica del Ground Truth (HITO 5.4).
- La calibración de NSS (HITO 5.4).
- La eliminación o retención de APTED (ADR_F17_BIS_05).
- La corrección matemática completa de cada algoritmo (requiere pruebas contra oráculos matemáticos conocidos).
- Optimización de algoritmos (ENGINEERING_PRINCIPLES §I).
- El impacto práctico de `.strip()` en el corpus real (requiere análisis estadístico en HITO 5.4).

### 2.3 Restricciones operativas

- **Hardware:** 16GB RAM (ADR Maestro §4). Zhang-Shasha O(n²) en espacio.
- **DF-18 (HITO 5.2):** 4 entry points con exit 0 ante fallo.
- **pyright verificado:** 0 errors para todos los archivos auditados.

---

## 3. ALCANCE AUDITADO

### 3.1 Objetos de auditoría (verificados contra código directo)

**Zhang-Shasha (core/benchmark/topology/engines/zhang_shasha/):**
- `engine.py` → `ZhangShashaEngine`
- `forest.py` → `ForestDistanceCalculator`
- `indexer.py` → `PostorderIndexer` (valida orden de siblings)
- `tree.py` → `ZhangShashaTreeDistanceCalculator`
- `matrix.py` → `TreeDistanceTable`

**APTED (tools/evaluation/topology/metrics/structural.py) — VERIFICADO:**
- `StructuralTopologyMetric` (wrapper/adapter)
- `CustomAPTEDConfig` (configuración de costos — **hereda de `apted.Config`**)
- `CostMatrix` con `default_v1()`

**Fingerprint (tools/evaluation/topology/fingerprint.py) — VERIFICADO:**
- `ASTFingerprintPolicy.semantic_fingerprint()` → `(node_type.value, text_content.strip())`
- `ASTFingerprintPolicy.identity_fingerprint()`

**Costos — VERIFICADOS:**
- `core/benchmark/topology/costs/unit.py` → `UnitCostContext` (ins=1, del=1, sub=1 si tipo o contenido difieren, SIN `.strip()`)
- `core/benchmark/topology/criticality/costs.py` → `CriticalityAwareCostContext` (CRITICAL=5.0, WARNING=2.0, INFO=1.0)

**Evaluadores y composición:**
- `core/benchmark/topology/evaluators/ted.py` → `TreeEditDistanceEvaluator`
- `core/benchmark/topology/strategies.py` → `ParserEvaluationStrategy`
- `bootstrap/topology.py` → `create_topology_evaluator()`, `DefaultNodeMatchingPolicy`

**Políticas:**
- `core/benchmark/topology/policies/normalization.py` → `MaxBoundNormalizationPolicy`

**Tests:**
- `tests/unit/test_zhang_shasha.py` → 15 tests + UnitCostContext local
- `tests/unit/test_structural_metric.py` → 7 tests

---

## 4. DEPENDENCIAS EXTERNAS (APTED)

| Atributo | Valor | Verificación |
|---|---|---|
| Paquete | `apted` | `pip show apted` |
| Versión | **1.0.3** | `pip show apted` |
| Licencia | **MIT** | `pip show apted` |
| Autor | Joao Pimentel | `pip show apted` |
| Repo | github.com/JoaoFelipe/apted | `pip show apted` |
| Distribución | PyPI | `pip show apted` |
| **Estado de mantenimiento** | Última release conocida: 1.0.3 (2017). Sin releases recientes. Dependencia de bajo dinamismo de releases, con riesgo de obsolescencia si se convierte en componente canónico. | PyPI |
| Versión del algoritmo | APTED original (Pawlik & Augsten) | Documentación del paquete |
| **Capacidad de Config personalizado** | **VERIFICADA por evidencia directa:** `CustomAPTEDConfig.rename(node1, node2)` ya implementa lógica dependiente del par de nodos. Las firmas `delete(node)` e `insert(node)` reciben el nodo como parámetro, permitiendo costes variables. | Código fuente |

---

## 5. ESTADO ACTUAL CONOCIDO

### 5.1 Arquitectura de ZhangShasha (pipeline de producción)

```text
create_topology_evaluator()
  ├── LCSAnchorAlignmentStrategy → alinea ASTs por anchors (headings)
  ├── HeadingAnchorPartitionStrategy → particiona en ventanas
  ├── ZhangShashaEngine
  │     ├── PostorderIndexer → indexado postorder con keyroots
  │     ├── ZhangShashaTreeDistanceCalculator → DP con TreeDistanceTable
  │     └── ForestDistanceCalculator → ecuaciones de recurrencia
  ├── UnitCostContext (default) → del=1, ins=1, sub=1 si difiere (SIN .strip())
  ├── WorstCaseOverflowStrategy → fallback para ventanas >2000 nodos
  └── MaxBoundNormalizationPolicy → score = 1 - (dist / worst_case)
```

**Pipeline:** `Sequence[ASTNode]` → Align → Partition → [ZhangShasha por ventana] → Sum → Normalize → `MetricScoreDTO`

### 5.2 Arquitectura de APTED (StructuralTopologyMetric)

```text
StructuralTopologyMetric.evaluate()
  ├── _build_apted_tree() → reconstruye árbol con raíz virtual "Document" SIEMPRE
  │     └── label = ASTFingerprintPolicy.semantic_fingerprint(node) → (type, content.strip())
  ├── APTED (librería PyPI v1.0.3) → compute_edit_distance()
  │     └── CustomAPTEDConfig (hereda apted.Config) → delete=1.0, insert=1.0, rename=0.5/2.0
  └── score = max(0.0, 1.0 - (distance / max_cost))
```

**Pipeline:** `Sequence[ASTNode]` → Build Tree (con fingerprint + strip) → APTED → Normalize → `MetricResult`

---

## 6. ANÁLISIS COMPARATIVO EN CAPAS

### Capa A — Contractual

| Aspecto | ZhangShasha | APTED |
|---|---|---|
| **Protocolo** | `TopologicalEvaluatorProtocol` | `TopologyMetric` |
| **Entrada** | `Sequence[ASTNode]` | `Sequence[ASTNode]` |
| **Salida** | `MetricScoreDTO` | `MetricResult` |

**Veredicto:** Protocolos diferentes pero funcionalmente equivalentes.

### Capa B — Representacional

| Aspecto | ZhangShasha | APTED |
|---|---|---|
| **Transformación** | `EvaluationForest(nodes=Sequence[ASTNode])` | `_build_apted_tree()` → `Tree` |
| **Label** | `ASTNode` completo | `semantic_fingerprint()` → `(type.value, content.strip())` |
| **Normalización de texto** | **SIN `.strip()`** | **CON `.strip()`** |
| **Raíz virtual** | Solo si múltiples raíces | Siempre `("Document", "root")` |
| **Costo raíz virtual** | 0.0 | 1.0 (costo normal, pero empareja con coste 0) |
| **Orden siblings** | Validado explícitamente | Depende del orden de iteración |

**Veredicto:** Representaciones NO idénticas bajo la configuración actual. Estructuralmente comparables bajo proyección común (mismo orden lógico de nodos, raíz virtual compatible), pero con transformación diferente de labels (`.strip()` vs sin `.strip()`) y política de raíz diferente.

### Capa C — Matemática (Modelo de Costo)

| Operación | ZhangShasha (UnitCostContext) | APTED (CostMatrix.default_v1) |
|---|---|---|
| **delete** | 1.0 | 1.0 |
| **insert** | 1.0 | 1.0 |
| **substitute (igual)** | 0.0 (tipo Y contenido, SIN strip) | 0.0 (tipo Y contenido, CON strip) |
| **substitute (mismo tipo, dif contenido)** | **1.0** | **0.5** |
| **substitute (diferente tipo)** | **1.0** | **2.0** |

**Veredicto:** Modelos de costo diferentes bajo configuración actual. APTED asigna menor coste (0.5 vs 1.0) a sustituciones de mismo tipo con diferente contenido. APTED asigna mayor coste (2.0 vs 1.0) a cambios de tipo. No se puede afirmar cuál modelo es "correcto" sin Ground Truth científico (HITO 5.4).

### Capa D — Metodología de Aplicación

| Aspecto | ZhangShasha | APTED |
|---|---|---|
| **Scope** | Ventanas particionadas por headings | Árbol completo del documento |
| **Preprocesamiento** | Align + Partition | Ninguno |
| **Cálculo** | Σ TED(windows) | TED(documento_completo) |

**Veredicto:** Metodologías DIFERENTES. D_ZS = Σ_i TED(W_i^1, W_i^2) ≠ D_APTED = TED(T1, T2) en general. Esta es la divergencia matemática más profunda: define funciones efectivas diferentes.

### Capa E — Normalización

| Aspecto | ZhangShasha | APTED |
|---|---|---|
| **Fórmula** | `1.0 - (distance / worst_case)` | `max(0.0, 1.0 - (distance / max_cost))` |
| **worst_case/max_cost** | `Σ del_cost(gt) + Σ ins_cost(cand)` | `(del × gt_nodes) + (ins × cand_nodes)` |
| **Efecto raíz virtual** | Sin raíz → sin efecto | +1 nodo en ambos → +2 en denominador |

**Veredicto:** Fórmula de normalización bajo unit cost: algebraicamente equivalente bajo igualdad de cardinalidad efectiva. **NO necesariamente equivalente en la configuración actual** debido a la raíz virtual de APTED (+2 en denominador). Bajo CriticalityAwareCostContext: incompatible (APTED usa conteo × fixed, ZS usa Σ weight).

---

## 7. DIVERGENCIAS CUANTIFICADAS (Tabla Consolidada)

| # | Aspecto | ZhangShasha | APTED | Divergencia | Sev | Evidencia | Naturaleza |
|---|---------|-------------|-------|:---:|:---:|---|---|
| 1 | Costo inserción | 1.0 | 1.0 | ✅ Igual | — | unit.py, CostMatrix | — |
| 2 | Costo eliminación | 1.0 | 1.0 | ✅ Igual | — | unit.py, CostMatrix | — |
| 3 | Sustitución (mismo tipo, mismo contenido) | 0.0 | 0.0 | ✅ Igual | — | unit.py, CustomAPTEDConfig | — |
| 4 | Sustitución (mismo tipo, dif contenido) | **1.0** | **0.5** | ❌ | **P1** | E-5.3-001 | Divergencia de configuración |
| 5 | Sustitución (diferente tipo) | **1.0** | **2.0** | ❌ | **P1** | E-5.3-001 | Divergencia de configuración |
| 6 | Normalización de texto | Sin `.strip()` | Con `.strip()` | ❌ | **P1** | **E-5.3-002** | Divergencia de configuración |
| 7 | Raíz virtual | Condicional | Siempre | ❌ | **P1/DC** | E-5.3-003 | Divergencia de representación |
| 8 | Impacto raíz virtual en denominador | Sin efecto | +2 en max_cost | ❌ | P2 | E-5.3-003 | Divergencia de representación |
| 9 | Metodología | Σ TED(windows) | TED(full tree) | ❌ | **P1** | E-5.3-017 | Divergencia matemática |
| 10 | Soporte CriticalityAwareCostContext | ✅ Sí | ❌ Adapter no lo expone | ❌ | **P1** | E-5.3-009 | Defecto de integración |
| 11 | Normalización (unit cost) | Σ costos/nodo | count × fixed | ⚠️ Condicional | — | E-5.3-013 | Equivalencia condicional |
| 12 | Normalización (criticality) | Σ weight(n) | Incompatible | ❌ | P2 | E-5.3-009 | Defecto de integración |
| 13 | Validación orden siblings | Explícita | Implícita | ❌ | P2 | E-5.3-006 | Observación |
| 14 | UnitCostContext test vs producción | Producción: tipo+contenido. Test: solo contenido | N/A | ❌ | P2 | E-5.3-016 | Defecto de tests |
| 15 | Librería | Implementación propia | PyPI apted v1.0.3 (2017) | Info | — | E-5.3-005 | Observación |

**Resumen de severidades:** 5 P1, 2 P2, 8 verificaciones. Total: 15 evidencias únicas.

**Categorías de divergencias (columna Naturaleza):**
- **Divergencia de configuración:** Diferencia de parámetros/configuración (no es bug, requiere decisión de ADR).
- **Divergencia de representación:** Diferencia de representación de entrada (no es bug, requiere decisión de ADR).
- **Divergencia matemática:** Diferencia de función efectiva por diseño (requiere decisión de ADR).
- **Defecto de integración:** El adapter no expone capacidad de la librería (requiere refactorización).
- **Defecto de tests:** Contrato de test inconsistente con producción.
- **Observación:** Hallazgo menor sin impacto directo.

---

## 8. REGISTRO DE EVIDENCIA FORENSE

### Evidencia E-5.3-009 (P1): Adapter StructuralTopologyMetric no integra CriticalityAwareCostContext

**Archivo:** `tools/evaluation/topology/metrics/structural.py` vs `core/benchmark/topology/criticality/costs.py` — VERIFICADO DIRECTAMENTE

**Observed (adapter actual):**

```python
class StructuralTopologyMetric:
    def __init__(self, cost_matrix: CostMatrix | None = None):
        self._matrix = cost_matrix or CostMatrix.default_v1()
```

**Observed (API de APTED — CustomAPTEDConfig hereda apted.Config):**

```python
class CustomAPTEDConfig(Config):
    def delete(self, node: Tree) -> float:
        return self._matrix.delete_cost  # ← firma permite coste dependiente del nodo
    def insert(self, node: Tree) -> float:
        return self._matrix.insert_cost  # ← firma permite coste dependiente del nodo
    def rename(self, node1: Tree, node2: Tree) -> float:
        type1, content1 = node1.name
        type2, content2 = node2.name
        if type1 == type2 and content1 == content2:
            return 0.0
        if type1 == type2:
            return self._matrix.rename_same_type_cost  # ← YA implementa lógica por nodo
        return self._matrix.rename_diff_type_cost      # ← YA implementa lógica por nodo
```

**Required:** Si el sistema adopta CriticalityAwareCostContext como modelo canónico (NADR-18 §5.3), el adapter debe integrarlo.

**Hallazgo:** La **librería APTED sí permite costes dependientes del nodo** mediante `Config` personalizado. **Evidencia directa:** el método `rename(node1, node2)` ya implementa lógica dependiente del par de nodos (compara type y content). Las firmas `delete(node)` e `insert(node)` reciben el nodo como parámetro. El adapter `StructuralTopologyMetric` actualmente NO explota esta capacidad para `delete` e `insert`: solo acepta `CostMatrix` con costes fijos. Es un **defecto del adapter** (P1), no una incompatibilidad de la librería.

**Formulación correcta:** "StructuralTopologyMetric no integra actualmente CriticalityAwareCostContext. La librería APTED tiene capacidad para soportarlo mediante Config personalizado (demostrado por la firma de rename(node1, node2) que ya implementa lógica dependiente del par de nodos), pero el adapter actual no lo expone para delete e insert."

---

### Evidencia E-5.3-001 (P1): Modelo de costo DIFERENTE

**Archivo:** `core/benchmark/topology/costs/unit.py` vs `structural.py` — VERIFICADO DIRECTAMENTE

```python
# UnitCostContext (VERIFICADO)
def substitution_cost(self, candidate, ground_truth):
    return 0.0 if (candidate.node_type == ground_truth.node_type 
                   and candidate.text_content == ground_truth.text_content) else 1.0

# CostMatrix.default_v1() (VERIFICADO)
@dataclass(frozen=True)
class CostMatrix:
    delete_cost: float = 1.0
    insert_cost: float = 1.0
    rename_same_type_cost: float = 0.5   # ← DIFERENTE de 1.0
    rename_diff_type_cost: float = 2.0   # ← DIFERENTE de 1.0
```

**Hallazgo:** APTED asigna menor coste (0.5 vs 1.0) a sustituciones de mismo tipo con diferente contenido. APTED asigna mayor coste (2.0 vs 1.0) a cambios de tipo. No se puede afirmar cuál modelo es "correcto" sin Ground Truth científico (HITO 5.4).

---

### Evidencia E-5.3-002 (P1): Normalización de texto DIFERENTE (`.strip()` vs sin `.strip()`)

**Archivo:** `tools/evaluation/topology/fingerprint.py` vs `core/benchmark/topology/costs/unit.py` — VERIFICADO DIRECTAMENTE

```python
# ASTFingerprintPolicy.semantic_fingerprint (VERIFICADO)
@staticmethod
def semantic_fingerprint(node: ASTNode) -> tuple[str, str]:
    node_type_str = node.node_type.value
    content_str = node.text_content.strip()   # ← .strip() APLICADO
    return (node_type_str, content_str)

# UnitCostContext.substitution_cost (VERIFICADO)
def substitution_cost(self, candidate, ground_truth):
    return 0.0 if (candidate.node_type == ground_truth.node_type 
                   and candidate.text_content == ground_truth.text_content  # ← SIN .strip()
                   ) else 1.0
```

**Hallazgo:** Si `text_content` tiene leading/trailing whitespace, `semantic_fingerprint` lo elimina antes de comparar, pero `UnitCostContext` NO. Esto produce divergencias para contenido con whitespace:

| text_content GT | text_content Cand | UnitCostContext | APTED (fingerprint) |
|---|---|---|---|
| `"hello"` | `"hello"` | 0.0 | 0.0 |
| `"hello "` | `"hello"` | **1.0** | **0.0** |
| `" hello"` | `"hello"` | **1.0** | **0.0** |

**Impacto práctico:** Pendiente de análisis estadístico sobre el corpus real (HITO 5.4). Si el % de nodos con whitespace incidental es bajo (<1%), el impacto es mínimo. Si es alto (>5%), el impacto es significativo.

---

### Evidencia E-5.3-003 (P1/DC): Raíz virtual DIFERENTE con impacto en denominador

**Archivo:** `indexer.py` vs `structural.py` — VERIFICADO DIRECTAMENTE

```python
# PostorderIndexer (VERIFICADO)
if len(roots) > 1:
    virtual_root = ASTNode(node_id=VIRTUAL_ROOT_ID, ...)
def _del_cost(self, node, costs):
    return 0.0 if node.node_id == VIRTUAL_ROOT_ID else costs.deletion_cost(node)

# StructuralTopologyMetric._build_apted_tree (VERIFICADO)
return Tree(("Document", "root"), *children_trees), total_count
```

**Hallazgo (corregido):**

- **Distancia TED:** Cuando ambos árboles (cand y gt) tienen raíz virtual Document, se emparejan con coste 0. La raíz virtual común NO afecta la distancia TED.
- **Denominador de normalización:** APTED cuenta +1 nodo (la raíz Document) en `total_cand_nodes` y `total_gt_nodes`. El denominador `max_cost = del*gt_nodes + ins*cand_nodes` aumenta en 2.0. Esto afecta el score normalizado (NSS).

**Naturaleza:** Divergencia de representación. No es un defecto; es una decisión de diseño pendiente de ADR (DC-5.3-06).

---

### Evidencia E-5.3-017 (P1): Metodología DIFERENTE

**Archivo:** `core/benchmark/topology/evaluators/ted.py` vs `structural.py` — VERIFICADO

```python
# ted.py (VERIFICADO)
alignment = self._aligner.align(candidate_ast, ground_truth_ast)
windows = self._partitioner.partition(candidate_ast, ground_truth_ast, alignment)
for window in windows:
    accumulated_distance += self._engine.compute(window.candidate, window.ground_truth, ...)

# structural.py (VERIFICADO)
cand_tree, total_cand_nodes = self._build_apted_tree(candidate)
gt_tree, total_gt_nodes = self._build_apted_tree(ground_truth)
distance = float(APTED(cand_tree, gt_tree, self._config).compute_edit_distance())
```

**Hallazgo:** ZhangShasha particiona el documento en ventanas contextuales (por headings) y suma distancias. APTED construye un árbol único del documento completo. Son magnitudes diferentes por diseño:

```text
D_ZS(T1, T2) = Σ_i TED(W_i^1, W_i^2)    (ventanas particionadas)
D_APTED(T1, T2) = TED(T1, T2)             (árbol completo)
En general: Σ_i TED(W_i^1, W_i^2) ≠ TED(T1, T2)
```

**Naturaleza:** Divergencia matemática. Define funciones efectivas diferentes. Es la divergencia más profunda y la que más impacta la decisión de ADR.

---

### Evidencias de verificación

| ID | Tipo | Evidencia | Hallazgo |
|---|---|---|---|
| E-5.3-005 | VERIF | `pip show apted` | apted v1.0.3, MIT, última release 2017 |
| E-5.3-006 | P2 | `_validate_sibling_order` vs sin validación | ZS valida orden, APTED no |
| E-5.3-008 | VERIF | `bootstrap/topology.py` | Composition root confirma UnitCostContext |
| E-5.3-010 | VERIF | `criticality/costs.py` | Pesos: CRITICAL=5.0, WARNING=2.0, INFO=1.0 |
| E-5.3-011 | VERIF | `models.py` | Dualidad ConfusionMatrix: core/ vs tools/ |
| E-5.3-012 | VERIF | pyright ted.py → 0 errors | Sin bugs de sintaxis |
| E-5.3-013 | VERIF | `normalization.py` vs `structural.py` | Normalización algebraicamente equivalente bajo unit cost + misma cardinalidad |
| E-5.3-014 | VERIF | `bootstrap/topology.py` | UnitCostContext como default |
| E-5.3-015 | P2 | `test_zhang_shasha.py` | Tests no usan pipeline completo |
| E-5.3-016 | P2 | `test_zhang_shasha.py::UnitCostContext` | Test compara solo text_content; producción tipo+contenido |

---

## 9. MATRIZ DE PILARES

### Pilar I — Equivalencia de Representación

| Elemento | Estado | Evidencia |
|---|---|---|
| Misma estructura de árbol | ⚠️ PARTIAL | Raíz virtual diferente pero emparejable (E-5.3-003) |
| Mismas etiquetas | ❌ DIFF | `.strip()` en fingerprint vs sin strip (E-5.3-002) |
| Mismo orden de siblings | ⚠️ PARTIAL | ZS valida, APTED no (E-5.3-006) |

**Veredicto del pilar:** PARTIAL. El `.strip()` es la divergencia más importante.

### Pilar II — Equivalencia de Modelo de Costo

| Elemento | Estado | Evidencia |
|---|---|---|
| Costo inserción | ✅ EQUAL | 1.0 en ambos |
| Costo eliminación | ✅ EQUAL | 1.0 en ambos |
| Costo sustitución | ❌ DIFF | 1.0 vs 0.5/2.0 (E-5.3-001) |
| Soporte criticality | ⚠️ ADAPTER GAP | Librería capaz, adapter no expone (E-5.3-009) |

**Veredicto del pilar:** FAIL bajo configuración actual. Configurable si se unifica CostMatrix.

### Pilar III — Equivalencia de Metodología

| Elemento | Estado | Evidencia |
|---|---|---|
| Scope de cálculo | ❌ DIFF | Σ windows vs full tree (E-5.3-017) |
| Magnitud medida | ❌ DIFF | Diferentes funciones matemáticas |

**Veredicto del pilar:** FAIL. Divergencia matemática por diseño.

### Pilar IV — Equivalencia de Normalización

| Elemento | Estado | Evidencia |
|---|---|---|
| Normalización bajo unit cost | ⚠️ CONDICIONAL | Algebraicamente equivalente bajo misma cardinalidad; no garantizado con raíz virtual |
| Normalización bajo criticality | ❌ INCOMPATIBLE | Σ weight vs count × fixed (E-5.3-009) |
| Efecto raíz virtual | ⚠️ DIFF | +2 en denominador APTED (E-5.3-003) |

**Veredicto del pilar:** PARTIAL / CONDICIONAL. Equivalente solo bajo UnitCostContext y misma cardinalidad efectiva.

---

## 10. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| H-5.3-A | ZS y APTED calculan la misma función | **RECHAZADA** | E-5.3-001, 002, 003, 017 |
| H-5.3-B | La normalización es equivalente en todos los casos | **RECHAZADA** | E-5.3-013, E-5.3-009 |
| H-5.3-C | Los modelos de costo son compatibles | **RECHAZADA** | E-5.3-001 |
| H-5.3-D | La divergencia es algorítmica | **RECHAZADA** | No se identificó evidencia de divergencia atribuible a la definición del algoritmo TED. Las divergencias son de configuración, representación y metodología. |
| H-5.3-E | APTED es incapaz de soportar CriticalityAware | **RECHAZADA** | E-5.3-009: la librería sí puede (rename() lo demuestra), el adapter no lo expone |
| H-5.3-F | La raíz virtual altera la distancia TED | **RECHAZADA** | E-5.3-003: altera el denominador, no la distancia |

---

## 11. RESPUESTAS A PREGUNTAS FORENSES (Q1-Q13)

### Q1 — ¿Ambas implementaciones reciben exactamente la misma estructura?

**NO.** APTED transforma cada nodo mediante `semantic_fingerprint()` (aplica `.strip()` al contenido). ZhangShasha usa `ASTNode` directamente sin normalización de texto.

### Q2 — ¿La estructura de árbol es matemáticamente equivalente?

**NO idénticas bajo la representación actual.** Estructuralmente comparables bajo proyección común (mismo orden lógico de nodos, raíz virtual compatible), pero con transformación diferente de labels (`.strip()` vs sin `.strip()`) y política de raíz diferente.

### Q3 — ¿Utilizan el mismo modelo de costo?

**NO.** CostMatrix.default_v1() tiene rename_same=0.5, rename_diff=2.0. UnitCostContext tiene sub=1.0 uniforme. APTED asigna menor coste a sustituciones de mismo tipo y mayor coste a cambios de tipo. No se puede afirmar cuál es "correcto" sin Ground Truth científico.

### Q4 — ¿Calculan realmente la misma distancia?

**NO.** D_ZS = Σ TED(windows), D_APTED = TED(full tree). Son magnitudes diferentes por diseño.

### Q5 — ¿Las diferencias son algorítmicas?

**No se identificó evidencia de divergencia atribuible a la definición del algoritmo TED.** Las divergencias observadas son de configuración (costes, `.strip()`), representación (raíz virtual) y metodología (ventanas vs árbol completo). Ambos algoritmos resuelven el mismo problema matemático de Tree Edit Distance sobre árboles ordenados. La corrección matemática completa de cada implementación no es objeto de demostración en este HITO (requiere pruebas contra oráculos matemáticos conocidos).

### Q6-Q7 — Casos triviales y complejos

No ejecutados (HITO read-only). Requieren ejecución experimental en HITO 5.4 o posterior.

### Q8 — ¿Existe divergencia sistemática?

**Sí, por diseño.** Bajo la configuración actual: APTED asigna menor coste (0.5 vs 1.0) a sustituciones de mismo tipo con diferente contenido. APTED asigna mayor coste (2.0 vs 1.0) a cambios de tipo. APTED normaliza texto con `.strip()`, ZS no.

### Q9 — ¿La comparación es reproducible?

**PARCIAL / NO DEMOSTRADO COMO EXPERIMENTO COMPLETO.** Ambos algoritmos son deterministas bajo entrada y configuración fijas. La reproducibilidad integral de la comparación requiere congelar explícitamente: representación, costes, metodología, dependencias (apted v1.0.3), normalización, orden de nodos y entorno. Estos parámetros no son iguales en la configuración actual, por lo que la comparación directa no es reproducible como experimento controlado sin unificación previa.

### Q10 — ¿La evidencia permite tomar una decisión arquitectónica?

**SÍ.** Clasificación: **C — Comparable but Non-Equivalent**.

### Q11 — ¿Ambos algoritmos respetan el orden de siblings?

**Parcialmente.** ZS valida explícitamente. APTED depende del orden de iteración.

### Q12 — ¿Ambos algoritmos usan el mismo indexado de nodos?

**Diferente mecanismo.** ZS: PostorderIndexer con keyroots. APTED: reconstruye desde parent_node_id.

### Q13 — ¿Cuál es la versión, licencia y mantenimiento de APTED?

**VERIFICADO:** APTED v1.0.3, MIT, github.com/JoaoFelipe/apted. Última release conocida: 2017. Sin releases recientes. Dependencia de bajo dinamismo de releases, con riesgo de obsolescencia si se convierte en componente canónico.

---

## 12. CLASIFICACIÓN FINAL

### Resultado C — Comparable but Non-Equivalent

**Justificación:** Ambas implementaciones están diseñadas para calcular Tree Edit Distance, pero bajo diferentes configuraciones, representaciones y metodologías. Las divergencias observadas son atribuibles a diferencias de configuración (costes, `.strip()`), representación (raíz virtual) y metodología (ventanas vs árbol completo), no a bugs algorítmicos ni a incompatibilidad de definición matemática. No se identificó evidencia de divergencia atribuible a la definición del algoritmo TED.

**Implicación para ADR_F17_BIS_05:**

1. **Unificar es posible pero requiere decisión de diseño:** Unificar los dos motores requiere decidir (a) modelo de costo canónico, (b) política de normalización de texto, (c) política de raíz virtual, (d) metodología (ventanas vs global).
2. **El adapter APTED puede extenderse** para soportar CriticalityAwareCostContext (la librería lo permite, demostrado por `rename(node1, node2)`).
3. **La metodología de ventanas** (Σ TED(windows)) vs **árbol completo** (TED(full tree)) es la divergencia más profunda: define funciones matemáticas diferentes.
4. **La pregunta fundamental para ADR_F17_BIS_05 no es "¿Zhang-Shasha o APTED?"** sino **"¿Cuál es la función matemática que representa correctamente la pérdida estructural relevante para la fidelidad científica del documento?"**

---

## 13. GAPS CONSOLIDADOS

| GAP | Sev | Naturaleza | Descripción | Evidencia | Fase destino |
|---|---|---|---|---|---|
| **GAP-5.3-01** | **P1** | Divergencia de configuración | Modelo de costo diferente (sub 1.0 vs 0.5/2.0). No es bug; requiere decisión de ADR sobre modelo canónico. | E-5.3-001 | **ADR_F17_BIS_05** |
| **GAP-5.3-02** | **P1** | Divergencia de configuración | Normalización de texto diferente (`.strip()` vs sin `.strip()`). No es bug; requiere decisión de ADR sobre política canónica. | E-5.3-002 | **ADR_F17_BIS_05** |
| **GAP-5.3-03** | **P1/DC** | Divergencia de representación | Raíz virtual con impacto en denominador de normalización. No es defecto; requiere decisión de ADR (DC-5.3-06). | E-5.3-003 | **ADR_F17_BIS_05** |
| **GAP-5.3-04** | **P1** | Divergencia matemática | Metodología diferente (Σ windows vs full tree). Define funciones efectivas diferentes. Requiere decisión de ADR. | E-5.3-017 | **ADR_F17_BIS_05** |
| **GAP-5.3-05** | **P1** | Defecto de integración | Adapter APTED no integra CriticalityAwareCostContext. La librería sí tiene capacidad (demostrado por rename()). Requiere refactorización del adapter si se adopta criticality. | E-5.3-009 | **ADR_F17_BIS_05** |
| **GAP-5.3-06** | P2 | Observación | Tests de ZhangShasha no verifican pipeline completo (pasan EvaluationForest directo). | E-5.3-015 | **ADR_F17_BIS_05** |
| **GAP-5.3-07** | P2 | Defecto de tests | UnitCostContext de tests difiere de producción (solo text_content vs tipo+contenido). Test contract drift. | E-5.3-016 | **ADR_F17_BIS_05** |

---

## 14. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia | Fase destino |
|---|---|---|---|
| **DC-5.3-01** | Canonical Topology Engine | E-5.3-001, 002, 003, 017, 009 | ADR_F17_BIS_05 |
| **DC-5.3-02** | Alternative Engine Status | Clasificación C + E-5.3-009 | ADR_F17_BIS_05 |
| **DC-5.3-03** | Equivalence Boundary | E-5.3-017 | ADR_F17_BIS_05 |
| **DC-5.3-04** | Canonical Cost Model | E-5.3-001, E-5.3-009 | ADR_F17_BIS_05 |
| **DC-5.3-05** | Canonical Label + Text Normalization | E-5.3-002 | ADR_F17_BIS_05 |
| **DC-5.3-06** | Canonical Root Policy | E-5.3-003 | ADR_F17_BIS_05 |
| **DC-5.3-07** | Benchmark Methodology (windows vs global) | E-5.3-017 | ADR_F17_BIS_05 |

---

## 15. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia |
|---|---|---|---|
| Adapter APTED no soporta criticality | Si se adopta CriticalityAwareCostContext, adapter requiere refactorización | Medio | E-5.3-009 |
| Scores no comparables en CI | Scores de ambos motores no son directamente comparables | Alto | E-5.3-001, 002, 017 |
| Whitespace divergente | `.strip()` en APTED vs sin strip en ZS produce divergencias con contenido sucio. Impacto práctico pendiente de análisis estadístico. | Medio (pendiente) | E-5.3-002 |
| APTED sin releases recientes | Última release 2017. Riesgo de obsolescencia si se adopta como canónico. | Medio | E-5.3-005 |
| Tests permisivos | UnitCostContext de tests más permisivo que producción | Bajo | E-5.3-016 |

---

## 16. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-5.3-01 | APTED v1.0.3 (2017). Sin releases recientes. Si se adopta como canónica, el proyecto asume responsabilidad de mantenimiento. | Medio | OPEN |
| OBS-5.3-02 | ZhangShasha es implementación propia. Proyecto asume mantenimiento. | Medio | OPEN |
| OBS-5.3-03 | Composition root usa UnitCostContext. CriticalityAware no integrado aún en producción. | Bajo | OPEN |
| OBS-5.3-04 | Test zhang_shasha usa UnitCostContext local menos estricto (solo text_content vs tipo+contenido). Test contract drift. | Medio | OPEN |
| OBS-5.3-05 | Impacto práctico de `.strip()` en corpus real pendiente de análisis estadístico (HITO 5.4). Si <1% de nodos tienen whitespace, impacto mínimo. Si >5%, impacto significativo. | Bajo | OPEN |

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO NADR-18/NADR-19

| Regla | Estado | Justificación |
|---|---|---|
| NADR-18 §5.3 R11 (CriticalityAwareCostContext) | ✅ ZS cumple / ❌ APTED NO CUMPLE como adapter | ZS integra CriticalityAwareCostContext. APTED adapter no lo expone (librería sí puede). |
| NADR-18 §5.3 R12 (Ponderación determinista) | ✅ ZS cumple | APTED N/A (no integra) |
| NADR-18 §5.3 R13 (Pesos configurables) | ✅ ZS cumple | APTED N/A (no integra) |
| NADR-18 §5.3 R14 (CRITICAL > WARNING > INFO) | ✅ ZS cumple (5.0 > 2.0 > 1.0) | APTED N/A (no integra) |
| NADR-19 §5.5 R20 (Reutiliza build_extraction_pipeline) | N/A | Fuera de scope de este HITO |

---

## 18. PREGUNTAS PARA ADR_F17_BIS_05

1. **DC-5.3-01:** ¿ZhangShasha permanece como referencia canónica para regresión topológica?
2. **DC-5.3-02:** ¿APTED permanece como alternativa, benchmark engine, o candidato a retirada? (El adapter puede extenderse para soportar CriticalityAwareCostContext.)
3. **DC-5.3-04:** ¿Cuál es el modelo de costo canónico (UnitCostContext vs CostMatrix vs CriticalityAware)?
4. **DC-5.3-05:** ¿Cuál es la política canónica de normalización de texto (con `.strip()` o sin `.strip()`)?
5. **DC-5.3-06:** ¿Cuál es la política canónica de raíz virtual?
6. **DC-5.3-07:** ¿Cuál es la metodología canónica: Σ TED(windows) o TED(full tree)?
7. **DC-5.3-03:** ¿Bajo qué dominio pueden considerarse equivalentes?
8. **Pregunta fundamental:** ¿Cuál es la función matemática que representa correctamente la pérdida estructural relevante para la fidelidad científica del documento?

---

## 19. REGLA DE ORO

> **Similarity is not equivalence. Correlation is not equivalence. Performance is not correctness. A shared input source is not proof of identical input.**

> **Same algorithmic problem is not same implementation contract.** Zhang-Shasha y APTED resuelven el mismo problema matemático, pero las integraciones actuales reciben configuraciones diferentes.

> **No se elimina una implementación porque "parece redundante". Se elimina únicamente cuando la equivalencia requerida, el dominio de validez y el impacto arquitectónico han sido demostrados y posteriormente aprobados mediante ADR.**

---

## 20. CIERRE DEL HITO 5.3

Este HITO confirma que ZhangShashaEngine y StructuralTopologyMetric (APTED v1.0.3) **no calculan la misma función de distancia bajo la configuración actual**. Existen 5 divergencias fundamentales (modelo de costo, normalización de texto, raíz virtual, metodología, adapter gap). La clasificación final es **C — Comparable but Non-Equivalent**.

**Las divergencias son de configuración, representación y metodología**, no de definición algorítmica. No se identificó evidencia de divergencia atribuible a la definición del algoritmo TED. Ambos algoritmos resuelven el mismo problema matemático de Tree Edit Distance sobre árboles ordenados, pero las integraciones actuales reciben configuraciones diferentes.

**La evidencia es suficiente para que ADR_F17_BIS_05 tome una decisión informada.**

**Estado del HITO:** FROZEN v1.1.3

**Condición de cierre cumplida:**
- [x] Metadata completa y consistente
- [x] Changelog actualizado (8 versiones)
- [x] Límite epistemológico declarado
- [x] Nota de desviación estructural justificada
- [x] Todas las superficies en scope inspeccionadas (verificación directa de código)
- [x] Fuentes de evidencia listadas
- [x] 15 evidencias únicas con ID estable (5 P1, 2 P2, 8 VERIF)
- [x] Sin duplicación de IDs
- [x] 13 preguntas forenses respondidas con lenguaje falsable
- [x] 4 pilares auditados
- [x] 7 gaps consolidados con columna Naturaleza
- [x] 7 Decision Candidates formalizados
- [x] Nota de herencia completa
- [x] DF-04 resuelto con clasificación C
- [x] Clasificación final emitida con fundamentos sólidos
- [x] Regla de Oro incluida
- [x] Verificación NADR-18/NADR-19 (APTED: NO CUMPLE como adapter)
- [x] Observaciones Complementarias (5)
- [x] 4 categorías de divergencias + Naturaleza en tabla de GAPs
- [x] Fecha corregida (2026-09-04)
- [x] Q2 sin "CASI" (clasificación falsable)
- [x] Q9 separado determinismo de reproducibilidad
- [x] Normalización condicionada a cardinalidad
- [x] Q8 sin "subestima/sobrestima"
- [x] API de APTED verificada por evidencia directa (rename())
- [x] .strip() verificado directamente en código
- [x] "No hay bugs algorítmicos" matizado
- [x] Cadena de gobernanza verificada

**Verificación de cadena de gobernanza:**
ADR_F17_BIS_MASTER → NADRs 18, 19 → HITO 5.0 → HITO 5.1 → HITO 5.2 → HITO 5.3 (este) → Gaps y DCs → ADR_F17_BIS_05 → Execution Plan.

**Siguiente paso recomendado:**
- **HITO 5.4** (GT Curation & Scientific Calibration): verificar H-5.1-C, H-5.1-D, H-5.1-F. Calibrar thresholds de NSS. Ejecutar benchmarks sobre corpus natural. Análisis estadístico de impacto de `.strip()`.
- **SYNTHESIS**: ADR_F17_BIS_05 con insumos de HITO 5.0, 5.1, 5.2, 5.3, 5.4.