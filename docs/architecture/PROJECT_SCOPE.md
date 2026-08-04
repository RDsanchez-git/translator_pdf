# Project Scope & Definition

## 1. Executive Summary
El objetivo de este proyecto es construir un pipeline automatizado SOTA para la ingesta, normalización, traducción impulsada por LLMs y reconstrucción de documentos complejos (PDFs de naturaleza académica, STEM y técnica). El sistema transforma representaciones físicas (coordenadas, píxeles) en un Árbol de Sintaxis Abstracta (AST) puro, ejecuta segmentación y empaquetamiento atómico inteligente, traduce el contenido preservando invariantes lógicas (código, matemáticas) y ensambla un documento de salida con fidelidad de layout.

## 2. In-Scope (Dentro del Alcance)
* **AST Secuencial y Polimórfico (Fase 16.2):** Conversión de bloques físicos de Layout a un AST plano secuencial con payloads estrictamente tipados.
* **Normalización Trans-página:** Sutura determinística de párrafos y componentes divididos arbitrariamente por los límites físicos del PDF original.
* **Segmentación de Alta Resolución (Fase 16.3):** Desambiguación oracional y de fronteras sin acoplar dependencias ML pesadas (SBD ligero).
* **Enrutamiento Passthrough (Fase 16.4):** Evasión estratégica de inferencia LLM para nodos lógicos que no requieren traducción (ecuaciones complejas, imágenes, tablas complejas), optimizando latencia y presupuesto de tokens (FinOps).
* **Chunking Atómico (Fase 16.5):** Algoritmos $N \to 1$ que empaquetan contexto para los modelos de lenguaje respetando invariantes de no-ruptura lógica.
* **Validación Polimórfica (Fase 16.6):** Inspección asimétrica post-traducción basada en la naturaleza del nodo.
* **Ensamblador de Layout (Fase 16.8):** Reconstrucción del documento empleando perfiles documentales (`DocumentProfile`) para alinear columnas, figuras y jerarquías estéticas.
* **Prompt System Estructurado (Fase 16.9):** Interfaz estricta con los LLMs basada en esquemas JSON validados (Pydantic), abandonando prompts basados exclusivamente en cadenas de texto.

## 3. Out-of-Scope (Fuera del Alcance / No Objetivos)
* Entrenamiento nativo o fine-tuning de modelos de Visión/OCR desde cero. El sistema confía en la abstracción de adaptadores de extracción de terceros.
* Inclusión de modelos de Machine Learning pesados (HuggingFace) dentro de los transformadores core (AST, Segmenter) para operaciones que se pueden resolver con heurísticas deterministas (SRE/Performance first).
* Análisis de sentimiento, resúmenes automáticos o transformaciones creativas del texto. El enfoque es estrictamente de traslación fiel.
* Interfaces gráficas complejas para el consumidor final en este módulo core. La prioridad es la API y el pipeline batch.

## 4. Criterios de Éxito (Success Definition)
* **Completitud Topológica:** La suma total de los tokens lógicos del documento de entrada debe ser matemáticamente rastreable y reconstruible en la salida.
* **Robustez Matemática/Técnica:** Fórmulas LaTeX, bloques de código e identificadores técnicos deben sobrevivir el ciclo de traducción inyectándose intactos vía *Passthrough*.
* **Resiliencia Operativa:** Capacidad probada de enrutar anomalías del parser o bloqueos de la red a estrategias defensivas inmutables sin corromper el runtime del pipeline completo.