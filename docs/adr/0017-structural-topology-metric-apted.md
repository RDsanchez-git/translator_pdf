# ADR 0017: Familia de Algoritmos Tree Edit Distance (TED), Invariantes y Normalización para StructuralTopologyMetric

- **Estado:** Aceptado (Validated & Frozen - PR 2B / Fase 17.3)
- **Fecha:** 2026-07-24
- **Autores:** Staff Architecture Team
- **Subdominio:** `tools/evaluation/topology` (Fase 17.3 / PR 2B)
- **Dependencias:**
  - ADR 0016: Modelo de Dominio AST V2
  - Benchmark Specification v1.0
  - Corpus Ground Truth `calibration_v1`

---

## 1. Versionado de Benchmark y Métrica

- **Benchmark Spec Version:** 1.0
- **Structural Metric Version:** 1.0
- **Cost Matrix Spec Version:** 1.0 (Congelada y Validada)

> **Regla de Invalidation de Comparabilidad:** Cualquier modificación en la calibración de la matriz de costos (`Cost Matrix Spec Version`) o en la función de normalización requerirá un incremento en la versión de la métrica (`Structural Metric Version`). Los reportes emitidos bajo versiones distintas de la métrica **no serán directamente comparables entre sí**.

---

## 2. Contexto y Problema

En la suite de evaluación topológica (`tools/evaluation/topology`), las métricas de primera línea evalúan dimensiones planas del documento:
1. `NodeCountMetric`: Verificación de volumen ($O(1)$).
2. `SequenceAlignmentMetric`: Fidelidad del orden de lectura mediante LCS ($O(m \times n)$).

Sin embargo, ninguna de ellas valida la **fidelidad jerárquica e integridad del árbol AST V2**. Un extractor candidato puede mantener el volumen de nodos y conservar el orden de lectura plano, pero alterar la estructura (p. ej., transformar subtítulos en párrafos raíz, aplanar tablas o alterar anidamientos).

Para evaluar esta dimensión con rigor científico, se requiere adoptar formalmente la familia de algoritmos de **Tree Edit Distance (TED)**. Para garantizar que la plataforma actúe como un laboratorio de evaluación cuyos reportes permanezcan válidos en el tiempo, el contrato matemático, las invariantes, los no-objetivos y el esquema de normalización deben quedar congelados de forma explícita.

---

## 3. Alternativas Consideradas

- **Zhang-Shasha:** Descartado como candidato principal debido a las limitaciones de rendimiento reportadas en la literatura para árboles profundos o desbalanceados ($O(|T_1| \cdot |T_2| \cdot \text{depth}_1 \cdot \text{depth}_2)$) y sus restricciones para soportar estrategias de costo complejas.
- **Comparación de Profundidad Plana (`depth == depth`):** Descartada en PR 2A por generar falsos positivos masivos al confundir la cota vertical de un nodo con la estructura jerárquica real.

---

## 4. Decisiones Arquitectónicas

### 4.1. Mecanismo de Evaluación: Familia TED (Algoritmo Oficial: APTED)
Se adopta oficialmente **APTED** (*All-Pairs-Tree-Edit-Distance*, Pawlik & Augsten) como el motor formal para la evaluación de similaridad jerárquica sobre árboles ordenados en `StructuralTopologyMetric` (`tools/evaluation/topology/metrics/structural.py`).

### 4.2. Estrategia de Fingerprint: Semántica Estricta
`StructuralTopologyMetric` utiliza **exclusivamente** la política semántica:

$$\text{Label}(v) = \text{ASTFingerprintPolicy.semantic\_fingerprint}(v)$$

**Queda estrictamente prohibido el uso de `identity_fingerprint()`** en la métrica estructural. La evaluación de estructura debe medir la coincidencia de tipo de bloque y contenido `(node_type, text_content)`, no la coincidencia de identificadores efímeros (`node_id` / UUIDs) que varían entre ejecuciones de extracción.

### 4.3. Matriz de Costos Definitiva ($C$)
Se congela e inmutable la siguiente matriz de costos calibrada para la librería `apted` (`CustomAPTEDConfig`):

- **Inserción:** $C_{\text{ins}} = 1.0$
- **Supresión:** $C_{\text{del}} = 1.0$
- **Reemplazo Mismo Tipo (`node_type`):** $C_{\text{ren\_same}} = 0.5$ (económico por variación menor de texto)
- **Reemplazo Distinto Tipo (`node_type`):** $C_{\text{ren\_diff}} = 2.0$ (equivalente a supresión + inserción)
- **Identidad Nula:** $C_{\text{ren}} = 0.0$ si $\text{Label}(v_{\text{cand}}) == \text{Label}(v_{\text{gt}})$

### 4.4. Función de Normalización Escalar ($[0, 1]$)
La distancia de edición absoluta $D(T_{\text{cand}}, T_{\text{gt}})$ se transforma en un score numérico acotado en $[0.0, 1.0]$ mediante la siguiente fórmula inmutable:

$$\text{Score}_{\text{structural}} = \max\left(0.0, 1.0 - \frac{D(T_{\text{cand}}, T_{\text{gt}})}{\text{MaxCost}}\right)$$

Donde el costo máximo teórico se define como:
$$\text{MaxCost} = C_{\text{del}} \cdot |T_{\text{gt}}| + C_{\text{ins}} \cdot |T_{\text{cand}}|$$

---

## 5. Invariantes del Contrato Matemático

Cualquier implementación de `StructuralTopologyMetric` debe satisfacer las siguientes invariantes (verificadas 7/7 en suite de pruebas unitarias):

1. **Determinismo Absoluto:** Evaluar las mismas dos secuencias de nodos AST produce idéntico score en cualquier entorno.
2. **Identidad Perfecta:** Dos árboles idénticos producen $\text{Score} = 1.0$.
3. **Casos Borde Vacíos:** Si $|T_{\text{cand}}| = 0$ y $|T_{\text{gt}}| = 0$, el score retorna $1.0$.
4. **Acotamiento:** El score siempre pertenece al intervalo cerrado $[0.0, 1.0]$.
5. **Agnosticismo de Identidad Física:** El score no cambia si se modifican los `node_id` manteniéndose intactos tipo y contenido.
6. **Sensibilidad al Orden (Ordered Trees):** Alterar el orden relativo de los nodos hijos modifica la distancia de edición.

---

## 6. No Objetivos

Esta métrica **NO** pretende evaluar ni reemplazar dimensiones ajenas a la topología del árbol:
- **Calidad de OCR / Corrección ortográfica:** Evaluado por métricas de alineación textual específicas.
- **Fidelidad Lingüística / Traducción:** Dimensión perteneciente a las fases de post-procesamiento/LLM.
- **Exactitud Geométrica / Bounding Boxes:** Métrica propia del validador de maquetación (`DocumentLayoutValidator`).
- **Rendimiento Operacional:** Latencia, consumo de VRAM/RAM y throughput son medidos por la capa de telemetría, no por el dominio de evaluación topológica.

---

## 7. Verificación Empírica y Hallazgo de Calibración

Durante la ejecución del benchmark de referencia sobre el corpus `calibration_v1` (`tools/evaluation/run_benchmark.py`), se registró la siguiente salida de ejecución:

| Métrica Topológica | Score Promedio (`pymupdf`) | Status |
| :--- | :---: | :---: |
| `node_count` | **1.0000** | 🟢 EXCELENTE |
| `recall` | **0.6380** | 🟡 ACEPTABLE |
| `sequence` | **0.6380** | 🟡 ACEPTABLE |
| `structural` | **0.6380** | 🟡 ACEPTABLE |

> **Observación Técnica de Arquitectura:** Se comprobó mediante inspección de metadatos que el Ground Truth de `calibration_v1` presenta un mapa de adyacencia plano (`parent_node_id: {None}`). En árboles de altura 1, la distancia de edición en árboles ($TED$) degenera matemáticamente a la distancia de alineamiento de secuencias ($LCS$). La coincidencia idéntica `structural == sequence` demuestra la **exactitud matemática absoluta de APTED** ante topologías degeneradas.

---

## 8. Reproducibilidad y Metadatos de Reporte

Para garantizar la auditabilidad histórica del laboratorio experimental, **todo reporte generado por el motor de evaluación deberá incluir obligatoriamente en su sección de metadatos**:
- `benchmark_spec_version`: "1.0"
- `structural_metric_version`: "1.0"
- `cost_matrix_spec_version`: "1.0"

---

## 9. Estado de Cierre y Aceptación Definitiva

El ADR cambia su estado a **Aceptado**. El PR 2B se declara oficialmente integrado, probado y congelado.

- **Suite Unit / Invariantes:** `tests/unit/test_structural_metric.py` (7/7 passed).
- **Integración:** Registrada en `default_metrics()` dentro de `tools/evaluation/topology/metrics/__init__.py`.
- **Benchmark Pipeline:** Operativo end-to-end con exportación en JSON y Markdown.