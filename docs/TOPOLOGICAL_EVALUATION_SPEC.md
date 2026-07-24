# ESPECIFICACIÓN MATEMÁTICA DE EVALUACIÓN (HITO 0)

Este documento establece el marco algebraico, abstracto y determinista para la evaluación de fidelidad en la extracción documental. Se eliminan por completo las librerías concretas o algoritmos específicos del núcleo del diseño, reemplazándolos por políticas abstractas de coincidencia, costo y topología.

---

## 1. Formulación de Recuperación Estructural (`EntityRecallEvaluator`)

Para auditar la capacidad del parser candidato de aislar componentes anatómicos específicos sin realizar un cruce completo del árbol, se modela la exhaustividad mediante teoría de grafos y emparejamiento máximo (*Maximum Bipartite Matching*), abstrayendo la identidad y la similitud.

Definimos una relación de correspondencia válida entre un nodo candidato $c \in C_K$ y un nodo del oráculo $g \in G_K$ pertenecientes a la misma categoría semántica $K \in \text{ContentNodeType}$[cite: 3]. Esta relación está gobernada por la conjunción de dos abstracciones independientes:

$$\text{Eligible}(c, g) \iff \text{Correspondence}_K(c, g) \land \left( \text{Sim}_K(\psi(c), \psi(g)) \ge \tau_K \right)$$

Donde:
*   $\psi$: Función pura de normalización sintáctica del texto.
*   $\text{Correspondence}_K$: Política inyectada (`NodeCorrespondencePolicy`) que determina de forma binaria si ambos nodos representan la misma entidad lógica o física en el documento (independientemente de su contenido textual).
*   $\text{Sim}_K$: Política inyectada (`ContentSimilarityPolicy`) que computa un escalar real $[0, 1]$ de similitud interna para el tipo $K$.
*   $\tau_K$: Umbral de aceptación escalar $[0, 1]$ parametrizado para la campaña.

Para resolver de manera inequívoca las colisiones por múltiples coincidencias idénticas o duplicados sintácticos, construimos un grafo bipartito $B_K = (C_K, G_K, E_K)$, donde un arco no dirigido $e = (c, g) \in E_K$ existe si y solo si $\text{Eligible}(c, g)$ es verdadero.

Formalizamos los componentes de la matriz de confusión analítica a partir del **emparejamiento máximo** (biyecto parcial de cardinalidad máxima) $M_K \subseteq E_K$ sobre el grafo $B_K$:

*   **Verdaderos Positivos ($\text{TP}_K$):** Cardinalidad del emparejamiento máximo óptimo.
    $$\text{TP}_K = |M_K|$$
*   **Falsos Positivos ($\text{FP}_K$):** Nodos emitidos por el candidato que no pudieron ser emparejados legítimamente.
    $$\text{FP}_K = |C_K| - \text{TP}_K$$
*   **Falsos Negativos ($\text{FN}_K$):** Nodos del oráculo ignorados o corrompidos críticamente por el candidato.
    $$\text{FN}_K = |G_K| - \text{TP}_K$$

Las métricas universales de control emitidas por la instancia parametrizada `EntityRecallEvaluator(target_type=K)` quedan definidas como:

$$\text{Recall}_K = \frac{\text{TP}_K}{\text{TP}_K + \text{FN}_K}, \quad \text{Precision}_K = \frac{\text{TP}_K}{\text{TP}_K + \text{FP}_K}$$

$$\text{F1}_K = 2 \cdot \frac{\text{Precision}_K \cdot \text{Recall}_K}{\text{Precision}_K + \text{Recall}_K}$$

---

## 2. Espacio de Árboles y Dominio de Costos Dinámicos (`EditCostPolicy`)

Un AST se define formalmente como un árbol ordenado con etiquetas $T = (V, E)$, donde cada vértice $v \in V$ representa un `ASTNode` inmutable caracterizado únicamente por su tipo semántico y su payload textual normalizado[cite: 3]:

$$v = (t, c)$$

Donde $t \in \text{ContentNodeType}$ y $c$ es la cadena de caracteres[cite: 3]. Se elimina la profundidad relativa del vértice ($depth$); el algoritmo de distancia de edición (TED) captura y penaliza de forma nativa la topología estructural del grafo mediante mutaciones de inserción y borrado.

El costo de una operación de edición $\text{op}$ se desacopla por completo del motor de cómputo y se relega a un contrato abstracto inyectado (`EditCostPolicy`), el cual interactúa con el comparador de contenido (`ContentSimilarityPolicy`):

*   **Costo de Borrado e Inserción:**
    $$\omega(\gamma(v \to \lambda)) = \text{Cost}_{\text{del}}(v.t), \quad \omega(\gamma(\lambda \to v)) = \text{Cost}_{\text{ins}}(v.t)$$

*   **Costo de Sustitución:**
    $$\omega(\gamma(v_1 \to v_2)) = \begin{cases} 
    \text{Cost}_{\text{mismatch}}(t_1, t_2) & \text{si } t_1 \neq t_2 \\
    \text{Cost}_{\text{sub}}(t_1) \cdot \left[ 1.0 - \text{Sim}_{t_1}(\psi(c_1), \psi(c_2)) \right] & \text{si } t_1 = t_2 
    \end{cases}$$

Donde $\text{Cost}_{\text{mismatch}}$ define la penalización por demeritación taxonómica de tipos, y $\text{Sim}_{t_1}$ invoca la función de similitud escalar provista por la estrategia del tipo de contenido correspondiente.

La Puntuación de Fidelidad Estructural Normalizada, aquí denominada **Normalized Structural Score ($\text{NSS}$)**, se calcula dividiendo la distancia de edición acumulada ($\text{TED}(T_{\text{cand}}, T_{\text{gt}})$) entre los costos máximos de destrucción y reconstrucción total del espacio de estados:

$$\text{NSS}(T_{\text{cand}}, T_{\text{gt}}) = 1.0 - \frac{\text{TED}(T_{\text{cand}}, T_{\text{gt}})}{\sum_{v \in T_{\text{gt}}} \text{Cost}_{\text{del}}(v.t) + \sum_{v \in T_{\text{cand}}} \text{Cost}_{\text{ins}}(v.t)}$$

---

## 3. Modelo de Particionado: Estrategia de Segmentación por Anclajes (`AnchorPartitioningStrategy`)

Para mitigar la complejidad polinomial $O(n^3)$ asociada al cálculo de distancia de edición sobre documentos extensos, y aislar la evaluación de variaciones espaciales irrelevantes, la fragmentación del árbol se rige bajo la interfaz abstracta `AnchorPartitioningStrategy`.

1. El orquestador inyecta una estrategia concreta de particionado (ej. `HeadingAnchorPartitioning`).
2. El componente aísla una secuencia ordenada de vértices de anclaje validados por correspondencia $\mathcal{A} = \{a_1, a_2, \dots, a_m\}$ comunes a ambos árboles.
3. **Nota de Implementación Crucial:** La estrategia concreta de `AnchorPartitioningStrategy` es responsable tanto de identificar como de alinear los anclajes equivalentes entre ambos árboles (resolviendo desalineaciones u omisiones parciales) antes de realizar la partición física de los sub-bosques.
4. Estos puntos de control alineados segmentan de forma unívoca a $T_{\text{cand}}$ y $T_{\text{gt}}$ en una colección de sub-bosques independientes $F^{(i)}$.
5. La distancia de edición global se define como la sumatoria lineal de los costos locales:

$$\text{TED}_{\text{global}}(T_{\text{cand}}, T_{\text{gt}}) = \sum_{i=0}^{m} \text{TED}\left(F_{\text{cand}}^{(i)}, F_{\text{gt}}^{(i)}\right)$$

La interfaz permite encadenar implementaciones de contingencia (*Fallback*) mediante composición de estrategias si el parser candidato destruye la estructura jerárquica primaria (ej. degradando de `HeadingPartitionStrategy` $\rightarrow$ `SectionPartitionStrategy` $\rightarrow$ `PagePartitionStrategy` $\rightarrow$ `FixedWindowStrategy`), manteniendo el núcleo del orquestador completamente ajeno al mecanismo físico de segmentación.

---

## 4. Advertencias de Viabilidad Técnico-Científica

> *   **Degradación en Cascada de Estrategias de Particionado:** Si un parser candidato altera críticamente el orden de los nodos de alta jerarquía lógica, la estrategia de anclaje estructural primario fallará o se desalineará masivamente. Al activar las estrategias de fallback lineales (`FixedWindowStrategy`), el desplazamiento temporal de un solo bloque generará un desfase en cadena en las ventanas subsecuentes, provocando penalizaciones por sustitución erróneas que degradarán artificialmente el NSS.
> *   **Sensibilidad de la Asimetría de Costos:** Al desacoplar los costos hacia `EditCostPolicy`, es imperativo garantizar que la matriz de costos de sustitución taxonómica sea matemáticamente consistente. Si la penalización entre tipos similares como `PARAGRAPH` y `LIST`[cite: 3] no está calibrada con suavidad, variaciones heurísticas menores del clasificador del parser se computarán con la misma gravedad que una pérdida destructiva total de información.