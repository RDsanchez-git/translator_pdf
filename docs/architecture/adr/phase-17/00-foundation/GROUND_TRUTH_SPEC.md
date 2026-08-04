# ESPECIFICACIÓN TÉCNICA DE CANONICIDAD DEL GROUND TRUTH (v1.0)

Este documento establece las directrices obligatorias para la curaduría manual de los archivos JSON del Ground Truth. Toda verificación humana debe asegurar que el árbol estructural cumpla con las siguientes invariantes semánticas y tipográficas antes de congelar el oráculo.

## 1. Continuidad Léxica y Fusión de Párrafos
Los parsers visuales tienden a fragmentar bloques de texto debido a saltos de página, números de página intercalados o layouts multi-columna.
* **Regla de Consolidación:** Si un párrafo continúa lógicamente en la columna adyacente o en la página siguiente, el curador debe fusionar los fragmentos en una única instancia de `ASTNode` con `ContentNodeType.PARAGRAPH`.
* **Remoción de Ruido de Maquetación:** Se deben extirpar del cuerpo del texto los elementos repetitivos como *headers* de página, *footers*, y foliación numérica. No deben existir nodos asignados a estos elementos de control visual.

## 2. Normalización de Bloques Matemáticos (TeX Balancing)
Las ecuaciones científicas constituyen el eje crítico de estrés del pipeline de evaluación.
* **Aislamiento Estricto:** Toda ecuación que aparezca centrada o aislada en su propia línea editorial debe tiparse estrictamente como `ContentNodeType.DISPLAY_EQUATION`.
* **Sintaxis Canónica:** El payload del nodo debe contener únicamente código LaTeX limpio y perfectamente balanceado. Se deben corregir fragmentaciones o caracteres espurios introducidos por el motor OCR (ej. reemplazar símbolos flotantes mal interpretados por comandos matemáticos válidos de AMS-LaTeX).
* **Tratamiento de Inline Math:** Las expresiones matemáticas incrustadas dentro del flujo natural de la prosa deben permanecer dentro del nodo `PARAGRAPH` envueltas de forma limpia entre delimitadores sencillos `$`, garantizando la continuidad sintáctica.

## 3. Geometría Absoluta de Bounding Boxes
* Las coordenadas espaciales del objeto `BoundingBox` (`x`, `y`, `w`, `h`) deben representar los límites físicos reales del elemento sobre el lienzo del PDF.
* No se deben aplicar márgenes de tolerancia ni umbrales de expansión en esta capa. Las cajas de colisión se registran de forma pura.

## 4. Elementos Visuales No Traducibles (Anclas Estructurales)
El alcance del Ground Truth está limitado a evaluar la calidad del contenido que será procesado por el pipeline de traducción. Las entidades visuales que se reutilizan desde el PDF original no forman parte del objeto de evaluación semántica interna, sino que actúan como delimitadores del orden de lectura.
* **Nodos Opacos (Hojas):** `ContentNodeType.TABLE` y `ContentNodeType.IMAGE` se modelan de forma estricta como nodos atómicos sin hijos.
* **Prohibición de Sub-estructuras:** No se modelan filas, columnas, celdas, ni se transcribe el texto interno de una tabla. No se modelan regiones internas ni marcadores de las imágenes. El payload topológico puede retener únicamente metadatos espaciales (`bbox`, `page`).
* **Propósito Evaluativo:** El motor topológico penalizará únicamente la omisión del nodo o su alteración secuencial en el orden de lectura.
* **Tratamiento de Epígrafes (Captions):** Los textos descriptivos asociados (ej. "Table 5. Results.") constituyen contenido estructural primario para la traducción. Deben extraerse como nodos independientes `ContentNodeType.PARAGRAPH` y ubicarse secuencialmente adyacentes al ancla, preservando el flujo natural.