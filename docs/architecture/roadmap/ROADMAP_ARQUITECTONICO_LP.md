# ROADMAP ARQUITECTÓNICO Y VISIÓN A LARGO PLAZO: TRADUCTOR PDF
**Versión:** 3.0
**Estado:** Post Fase 16 (Estabilización del Core)

> **PREÁMBULO ARQUITECTÓNICO**
> Este roadmap describe la evolución de una herramienta local de alto rendimiento. La incorporación de infraestructura distribuida (Redis, Message Brokers, Kubernetes, microservicios) se considera explícitamente fuera del alcance de esta visión y sólo deberá evaluarse si los requisitos funcionales del proyecto cambian hacia un escenario multiusuario o de procesamiento distribuido.

---

## I. PRINCIPIOS ARQUITECTÓNICOS

Este documento y toda decisión técnica futura se rigen estrictamente por los siguientes principios de ingeniería.

1. **Domain-Driven Design (DDD) & Hexagonal Architecture:** El dominio es sagrado y agnóstico a la tecnología. Toda interacción con el exterior se realiza exclusivamente mediante *Ports & Adapters*.
2. **Inmutabilidad Estricta (Immutable DTOs):** Las estructuras de datos en tránsito están congeladas (`frozen=True`). No existe mutación *in-place*.
3. **FinOps First:** Ninguna petición de red se ejecuta sin un presupuesto pre-calculado. El costo es una métrica de primer orden.
4. **Fail-Fast & Tolerancia a Fallos Parciales:** Las invariantes lógicas abortan de inmediato. Los errores de infraestructura o formato aíslan el bloque afectado, permitiendo que el resto del documento se ensamble.
5. **Idempotencia & Determinismo:** Ante la misma entrada y el mismo estado, el pipeline debe producir exactamente el mismo resultado criptográfico (SHA-256).
6. **Golden Corpus Driven Development:** La calidad de la traducción se demuestra algorítmicamente contra una línea de base científica inmutable.
7. **Benchmark Before Optimization:** Ningún componente estructural se reemplaza sin evidencia estadística empírica.
8. **Optimize Before Distribution:** Los cuellos de botella se resuelven exprimiendo la eficiencia del hardware local (I/O, memoria, asincronía) antes de considerar sistemas distribuidos.

---

## II. EL EJE CONCEPTUAL

La evolución del sistema se divide en dos etapas ortogonales que separan la creación del traductor de la maduración de la herramienta.

| Etapa | Fases | Objetivo Principal | Hito Final |
| :--- | :--- | :--- | :--- |
| **ETAPA I: Core Engine** | 16, 17, 17.5, 18 | Construir el mejor traductor científico posible, priorizando exactitud y rendimiento en un solo nodo. | **El Producto Nace.** Traduce *papers* y libros con ecuaciones y topología intacta en la máquina local. |
| **ETAPA II: Product Maturity** | 19, 20, 21 | Transformar el motor en una herramienta operable, empaquetada, auditable y autoadaptativa. | **El Producto Madura.** Se opera vía CLI/Docker, autogestiona presupuestos y posee observabilidad local profunda. |

---

## III. ESTADO ACTUAL (FASE 16 COMPLETADA)

El núcleo del sistema ha superado la etapa de MVP y se considera una arquitectura estabilizada de grado de producción.

* **Componentes Congelados (Core Estructural):**
  * **AST V2 & Payload Registry:** Representación de árbol abstracta con factoría polimórfica.
  * **Segmenter V2 / Semantic Classifier:** Aislamiento lógico de bloques en O(n).
  * **Validation & Healing Pipeline:** Saneamiento perimetral, estructural y semántico en modo *Fail-Safe*.
  * **Dispatcher & FinOps Engine:** Estrangulamiento matemático de peticiones y estimación `ExactBPE`.
  * **CQRS, FSM & Telemetry:** Trazabilidad transaccional en SQLite (modo WAL).

---

## IV. ROADMAP EVOLUTIVO

### ETAPA I: CORE ENGINE

#### FASE 17: Extraction Engine Integration
* **Objetivo:** Alimentar el *Benchmark Framework* existente con motores SOTA de visión computacional para descubrir empíricamente el mejor extractor topológico.
* **Principales Entregables:**
  * Patrones *Adapter* para Marker, Docling, Nougat, PyMuPDF, etc.
  * Ejecución del `SequentialBenchmarkOrchestrator` contra los nuevos adaptadores.
  * Leaderboard de métricas estructurales (`Equation Recall`, `Tree Edit Distance`).
* **Criterios de Finalización:** Selección del motor de extracción definitivo sustentada en significancia estadística.

#### FASE 17_BIS: Scientific Baseline (Canonical Corpus)
* **Objetivo:** Establecer la "verdad absoluta" del sistema y blindar la arquitectura contra regresiones.
* **Principales Entregables:**
  * *Golden Corpus*: 20-30 documentos de alta varianza (papers IEEE, doble columna, libros densos).
  * *Ground Truth*: Congelamiento criptográfico del AST perfecto en disco.
  * *Regression Gates*: Aserción estricta en CI que impida el *merge* de alteraciones a nodos críticos.
* **Criterios de Finalización:** Cobertura de regresión automatizada sobre el corpus canónico.

#### FASE 18: Advanced Local Runtime (Hito de Madurez)
* **Objetivo:** Exprimir el rendimiento computacional local eliminando bloqueos I/O y optimizando el ciclo de CPU y memoria.
* **Principales Entregables:**
  * Asincronía pura top-to-bottom (elisión de `SyncProviderBridge`).
  * *Memory Efficiency*: Object Pools, buffers *Zero-copy*, y *lazy loading*.
  * *Pipeline Backpressure*: Prevención de *Out-Of-Memory* (OOM) en procesamiento masivo.
  * *Adaptive Batching & Scheduling*: Agrupación dinámica de *chunks* según presupuesto (8k, 32k, 1M).
  * *Cache Multinivel*: Memoria $\rightarrow$ SQLite $\rightarrow$ Semantic/Embedding Cache.
* **HITO CRÍTICO:** Al concluir esta fase, el Traductor PDF se considera funcionalmente completo para el procesamiento de documentos científicos reales.

---

### ETAPA II: PRODUCT MATURITY

#### FASE 19: Packaging & UX
* **Objetivo:** Transformar el repositorio en una herramienta de software profesional, instalable y amigable.
* **Principales Entregables:**
  * CLI (*Command Line Interface*) de grado industrial.
  * *Packaging*: Imagen Docker *standalone* garantizando el aislamiento de dependencias de *Computer Vision*.
  * Gestión centralizada de archivos de configuración (`.yaml`/`.env`) y perfiles de usuario.
  * Exportación simplificada y manejo de artefactos compilados.

#### FASE 20: Local Observability
* **Objetivo:** Instrumentar el sistema para depuración forense, auditoría de costos y análisis de rendimiento sin dependencias *Cloud*.
* **Principales Entregables:**
  * Trazabilidad estructurada y *logs* en formato JSON vinculados por `execution_id`.
  * Reportes de ejecución post-procesamiento: tiempo de CPU, *tokens* consumidos, costo exacto en USD, tasa de fallos de validación.
  * Interfaz o scripts forenses para consultas directas sobre la base de datos de telemetría SQLite.

#### FASE 21: Adaptive Intelligence
* **Objetivo:** Dotar a la herramienta de heurísticas que automaticen decisiones operativas en tiempo de ejecución.
* **Principales Entregables:**
  * *Smart Model Routing*: Delegación dinámica a LLMs según complejidad (ej. modelos rápidos para texto plano, razonamiento profundo para fórmulas matemáticas).
  * *Adaptive Healing*: Auto-ajuste de estrategias de sanación basado en el perfil del documento.
  * *Parser Routing*: Selección heurística del motor de extracción según la firma visual o editorial del PDF.

---

## V. MATRIZ DE DECISIONES DE INFRAESTRUCTURA

| Tecnología | Decisión Arquitectónica | Justificación |
| :--- | :--- | :--- |
| **SQLite (WAL)** | **Core Engine** | Soporta alta concurrencia asíncrona local y respeta la simplicidad de la herramienta. |
| **Docker** | **Core Packaging** | Aísla de forma segura las dependencias de modelos de IA (PyTorch, CUDA). |
| **Redis / Message Brokers** | No requerido para el alcance actual | Las colas asíncronas en memoria (`asyncio.Queue`) saturan el rendimiento local sin el costo de serialización en red. |
| **Microservicios** | Fuera del alcance arquitectónico del proyecto actual | El monolito asíncrono actual carece de los fallos transitorios de red que justifican el IPC. |
| **Kubernetes** | No requerido para el alcance actual | Orquestación inútil y excesiva para un entorno de ejecución de nodo único. |

---

## VI. VISIÓN A LARGO PLAZO (ESTADO OBJETIVO)

Cuando las Fases 16 a 21 concluyan, el Traductor PDF operará como una herramienta de precisión extrema, capaz de:
1. Traducir libros y *papers* científicos complejos de forma autónoma.
2. Preservar intacta la topología bidimensional original, resolviendo columnas, tablas y referencias.
3. Exprimir el hardware local con eficiencia SOTA mediante concurrencia asíncrona pura.
4. Auto-gestionar los presupuestos de inferencia LLM decidiendo qué modelo usar por cada fragmento.
5. Proveer al usuario una experiencia empaquetada profesional (CLI/Docker) con observabilidad profunda de los costos y tiempos de ejecución.