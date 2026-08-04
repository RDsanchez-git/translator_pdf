# HITO_0.4.5_P4_OPERATIONAL_DISPATCH_AUDIT.md
## Operational Dispatch, LLM Integration, FinOps, Cache, Rate Limiting & Resilience — Reporte Consolidado Bloque P4

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P4)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P4)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en el análisis AST del código fuente de producción y el Grafo de Inferencia y Despacho Operacional (`P4_OPERATIONAL_DISPATCH_GRAPH.md`). Cero mutaciones en código productivo. Disposición y acciones diferidas al Hito 0.5.

---

## 1. MARCO EPISTEMOLÓGICO Y DIAGNÓSTICO DE EJECUCIÓN OPERACIONAL

El escrutinio forense del Bloque P4 sobre la frontera operacional de despacho e inferencia (`Dispatch` $\rightarrow$ `LLM` $\rightarrow$ `FinOps` $\rightarrow$ `Cache` $\rightarrow$ `Resilience`) ha revelado **fracturas estructurales graves en el plano de control operacional**. 

Aunque los componentes individuales presentan un modelado conceptual sofisticado (dialectos de prompt desacoplados, medición de inferencias y capas de almacenamiento en caché), **el cableado efectivo en runtime padece de aislamiento de resiliencia, esquizofrenia en los modos de ejecución e invalidez de FinOps para entornos distribuidos**:

```text
==================================================================================================
                     FLUJO TEÓRICO DECLARADO PARA EL BLOQUE P4 (CLEAN ARCH)
==================================================================================================

  TranslationUnit ──► AsyncDispatcher ──► ContextResolver ──► PromptBuilder (con Budget BPE)
                                                                     │
  DispatchResult  ◄── CircuitBreaker ◄── RateLimitedProvider ◄── CachedLLMProvider
                                          (QuotaManager)             (SQLite / Redis)

==================================================================================================
                   FLUJO REAL OBSERVADO EN RUNTIME (IN-PROCESS CLI MODE)
==================================================================================================

  TranslationUnit Sequence
         │
         ▼
  AsyncDispatcher
         │
         ├──► DummyContextResolver (¡Contexto nulo hardcodeado!)
         ├──► PromptBuilder (Usa FastWordEstimator -> Inexacto en LaTeX)
         │
         ▼
  CachedLLMProvider (infra/db/materialized.db)
         │
         ├── [CACHE HIT] ──► Devuelve respuesta previa (posiblemente sin contexto)
         │
         └── [CACHE MISS]
                   │
                   ▼
            RateLimitedProvider
                   │
                   ├──► QuotaManager / TokenBucket (¡Solo local en memoria RAM!)
                   │
                   ├──► [BYPASS ✗] ──► GlobalCircuitBreaker (OMITIDO / ZOMBI 100%)
                   │
                   ▼
            GroqProvider / GeminiProvider
                   │
                   ▼
            API Remota (Riesgo de ContextOverflowError o HTTP 429 en cluster)
                   │
                   ▼
            ValidationPipeline & HealingPipeline (Inyectados por mutación posterior)
                   │
                   ▼
            DispatchResult
```

---

## 2. REGISTRO EXHAUSTIVO DE EVIDENCIA FORENSE Y HALLAZGOS TÉCNICOS (P4-01 A P4-07)

### 2.1. Desconexión de Resiliencia y Fallas de Circuito

#### P4-01 (Orfandad Absoluta del Motor de Resiliencia: `GlobalCircuitBreaker` Zombi) [P0 - CRÍTICO]
* **Ubicación:** `core/resilience/circuit_breaker.py` vs. `apps/llm_workers/dispatcher.py` / `rate_limiter.py`
* **Mecanismo Causal:** 
  `core/resilience/circuit_breaker.py` implementa una máquina de estados determinista (`CLOSED`, `OPEN`, `HALF_OPEN`) con poda de ventanas de tiempo deslizantes (`GlobalCircuitBreaker`) y registro de fallas por dominio (`CircuitBreakerRegistry`).
  El Grafo Estático AST confirma que **ningún punto de entrada (`apps/cli/main.py`), fábrica (`pipeline_factory.py`) ni despachador (`AsyncDispatcher`) instancía o invoca el `GlobalCircuitBreaker`**.
* **Impacto Arquitectónico:** Si un proveedor remoto (Groq o Gemini) empieza a responder con errores `500 Internal Server Error`, de degradación o latencias extremas, el pipeline no posee un mecanismo *Fail-Fast* para abrir el circuito. Continuará bombardeando la API remota con reintentos hasta agotar el tiempo de espera o colapsar el proceso por agotamiento de recursos.

---

### 2.2. Dualidad de Ejecución y Vicios de Escalamiento

#### P4-02 (Bipolaridad del Plano de Ejecución: In-Process CLI vs. Distributed Daemon) [P0 - CRÍTICO]
* **Ubicación:** `apps/llm_workers/dispatcher.py` vs. `apps/llm_workers/__main__.py` (`LLMWorkerDaemon`)
* **Mecanismo Causal:** Coexisten dos modos de despacho operacional totalmente desalineados:
  * **Modo In-Process (CLI):** `apps/cli/main.py` construye un `AsyncDispatcher` en memoria que orquesta las tareas concurrentemente usando un `asyncio.Semaphore` local. No persiste ni lee tareas desde la cola `ControlPlaneRepository`.
  * **Modo Distribuido (Daemon):** `apps/llm_workers/__main__.py` ejecuta `LLMWorkerDaemon`, el cual adquiere transaccionalmente bloques de tareas en SQLite (`ControlPlaneRepository.pick_task()`), renueva bloqueos optimistas vía `TaskLeaseHeartbeat` y actualiza la FSM.
* **Impacto Arquitectónico:** El pipeline invocado por el CLI salta por completo la arquitectura orientada a eventos y comandos (CQRS/WAL) de la FSM, haciendo imposible distribuir el procesamiento de un documento largo entre múltiples nodos o procesadores concurrentes.

#### P4-03 (Invalidez de `QuotaManager` para Escalamiento Horizontal en Cluster) [P0 - CRÍTICO]
* **Ubicación:** `apps/llm_workers/rate_limiter.py` (`QuotaManager`, `TokenBucket`)
* **Mecanismo Causal:** 
  `TokenBucket` mantiene su contador de tokens disponibles (`self.tokens`) y la marca de tiempo de refresco (`self.last_refill`) en variables simples almacenadas en la memoria RAM del proceso actual de Python.
* **Impacto ArquITECTÓNICO:** Si se despliegan múltiples trabajadores (`LLMWorkerDaemon`) o contenedores en paralelo, los baldes de tokens no comparten estado (ausencia de backend distribuido como Redis o tabla central de cuotas). Las peticiones agregadas enviadas por $N$ procesos multiplicarán por $N$ la tasa de transferencia real hacia los LLMs, gatillando bloqueos masivos por rebasamiento de cuota (`HTTP 429 Too Many Requests`).

---

### 2.3. FinOps, Presupuesto de Tokens y Contaminación de Caché

#### P4-04 (Subestimación Severa FinOps por Heurísticas de Conteo en LaTeX) [P0 - CRÍTICO]
* **Ubicación:** `core/ast/models.py` (`FastWordEstimator`) vs. `core/validation/budget.py` (`PromptBudgetCalculator`)
* **Mecanismo Causal:** 
  El cálculo de presupuesto de prompts (`PromptBudgetCalculator`) y el servicio de medición FinOps (`InferenceMeasurementService`) emplean `FastWordEstimator`. La función `FastWordEstimator.estimate_tokens()` estima los tokens multiplicando la cantidad de palabras (vía `split()`) por una constante fija de $1.3$.
* **Impacto Arquitectónico:** La expresión de una ecuación LaTeX como `\begin{equation}\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\end{equation}` contiene **una sola palabra** bajo la lógica de `split()`, pero equivale a más de $20$ tokens para los tokenizadores BPE reales (Tiktoken/Llama-3/Gemini). En documentos científicos densos en fórmulas, la estimación FinOps subestima el tamaño del prompt por un orden de magnitud, provocando que se rebase el límite de la ventana de contexto y lanzando excepciones `ContextOverflowError` no atrapadas en la API externa.

#### P4-05 (Envenenamiento de Caché por Inyección de Contexto Nulo) [P1 - ALTO]
* **Ubicación:** `apps/cli/main.py` vs. `apps/llm_workers/cache_provider.py` (`CachedLLMProvider`)
* **Mecanismo Causal:** 
  `CachedLLMProvider` genera la clave de consulta en caché usando la firma del prompt emitida por `PromptBuilder`. En `apps/cli/main.py`, se inyecta `DummyContextResolver`, el cual retorna migas de pan vacías (`breadcrumbs = ()`).
* **Impacto ArquITECTÓNICO:** Si se procesa un documento con la caché habilitada utilizando el resolvedor nulo, la respuesta del LLM traducida sin contexto jerárquico se persiste en SQLite (`infra/db/materialized.db`). En ejecuciones posteriores con un resolvedor real, el sistema devolverá un acierto de caché (*cache hit*) que contiene una traducción degradada por falta de contexto.

---

### 2.4. Inmutabilidad y Encapsulamiento en the Composition Root

#### P4-06 (Inyección Mutativa Posterior de Pipelines de Validación y Healing) [P1 - ALTO]
* **Ubicación:** `apps/bootstrap/pipeline_factory.py` vs. `apps/llm_workers/dispatcher.py`
* **Mecanismo Causal:** 
  `pipeline_factory.py` modifica el estado del `AsyncDispatcher` mediante asignación posterior de atributos tras su instanciación:
  ```python
  dispatcher.validation_pipeline = validation_pipeline
  dispatcher.healing_pipeline = healing_pipeline
  ```
* **Impacto ArquITECTÓNICO:** Si el despachador se instancía desde otro punto de entrada sin aplicar esta mutación imperativa, cae por defecto en `_default_pipeline()`, el cual configura un pipeline de validación parcial sin estrategias de auto-reparación (*healing*), perdiendo la garantía de rollback sintáctico.

#### P4-07 (Duplicación de Adaptadores de Resiliencia) [P2 - MEDIO]
* **Ubicación:** `apps/llm_workers/resilient_provider.py` vs. `core/resilience/circuit_breaker.py`
* **Mecanismo Causal:** 
  `apps/llm_workers/resilient_provider.py` define una versión alternativa de `CachedLLMProvider`, duplicando responsabilidades de manejo de excepciones transitorias que deberían residir centralizadas en `core/resilience/`.
* **Impacto Arquitectónico:** Fragmentación de la capa de resiliencia. Dificulta el mantenimiento al existir múltiples wrappers declarados con propósitos superpuestos.

---

## 3. GRAFO Y TRAZABILIDAD DEL FLUJO OPERACIONAL REAL VS. TEÓRICO

El Grafo de Inferencia y Despacho Operacional (`P4_OPERATIONAL_DISPATCH_GRAPH.md`) expone las discontinuidades del runtime:

```text
==================================================================================================
                     FLUJO TEÓRICO DECLARADO PARA EL BLOQUE P4 (CLEAN ARCH)
==================================================================================================

  TranslationUnit ──► AsyncDispatcher ──► ContextResolver ──► PromptBuilder (con Budget BPE)
                                                                     │
  DispatchResult  ◄── CircuitBreaker ◄── RateLimitedProvider ◄── CachedLLMProvider
                                          (QuotaManager)             (SQLite / Redis)

==================================================================================================
                   FLUJO REAL OBSERVADO EN RUNTIME (IN-PROCESS CLI MODE)
==================================================================================================

  TranslationUnit Sequence
         │
         ▼
  AsyncDispatcher
         │
         ├──► DummyContextResolver (¡Contexto nulo hardcodeado!)
         ├──► PromptBuilder (Usa FastWordEstimator -> Inexacto en LaTeX)
         │
         ▼
  CachedLLMProvider (infra/db/materialized.db)
         │
         ├── [CACHE HIT] ──► Devuelve respuesta previa (posiblemente sin contexto)
         │
         └── [CACHE MISS]
                   │
                   ▼
            RateLimitedProvider
                   │
                   ├──► QuotaManager / TokenBucket (¡Solo local en memoria RAM!)
                   │
                   ├──► [BYPASS ✗] ──► GlobalCircuitBreaker (OMITIDO / ZOMBI 100%)
                   │
                   ▼
            GroqProvider / GeminiProvider
                   │
                   ▼
            API Remota (Riesgo de ContextOverflowError o HTTP 429 en cluster)
                   │
                   ▼
            ValidationPipeline & HealingPipeline (Inyectados por mutación posterior)
                   │
                   ▼
            DispatchResult
```

---

## 4. TAXONOMÍA Y MATRIZ DE COMPONENTES DEL BLOQUE P4

| Componente / Módulo | Categoría Arquitectónica | Severidad | Diagnóstico Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `core/resilience/circuit_breaker.py` | Resilience Engine | **P0 (Crítico)** | `GlobalCircuitBreaker` desconectado $100\%$ en producción. | **INTEGRAR EN DISPATCHER** |
| `apps/llm_workers/rate_limiter.py` | Rate Limiter / FinOps | **P0 (Crítico)** | Estado en RAM local. Inviable para despliegue multi-process. | **EXTERNALIZAR ESTADO (REDIS/DB)** |
| `core/ast/models.py` | Token Estimator | **P0 (Crítico)** | `FastWordEstimator` subestima tokens en LaTeX/fórmulas. | **REEMPLAZAR POR BPE EXACTO** |
| `apps/llm_workers/dispatcher.py` | Operational Core | **P0 (Crítico)** | Inconsistencia entre modo CLI e `LLMWorkerDaemon`. | **UNIFICAR PLANO DE EJECUCIÓN** |
| `apps/cli/main.py` | CLI EntryPoint | **P1 (Alto)** | Inyecta `DummyContextResolver` produciendo veneno en caché. | **CONECTAR CONTEXT RESOLVER REAL** |
| `apps/bootstrap/pipeline_factory.py` | Composition Root | **P1 (Alto)** | Asignación de atributos por mutación en `dispatcher`. | **MIGRAR A CONSTRUCTOR INMUTABLE** |
| `apps/llm_workers/cache_provider.py` | Cache Layer | **P2 (Medio)** | Esquema de invalidación implícito en SQLite `materialized.db`. | **ESTABILIZAR ESQUEMA Y CLAVES** |

---

## 5. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P4-R01 A P4-R06)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P4-R01 (Cableado Mandatorio de Resiliencia - P0):** Intercept el stack de proveedores del despachador con `GlobalCircuitBreaker` (o `ResilientProvider`), garantizando que las fallas consecutivas en las APIs de los LLM abran el circuito y prevengan el agotamiento de recursos.
* **P4-R02 (Sincronización de Rate Limiting Distribuido - P0):** Refactorizar `QuotaManager` para abstraer la persistencia del `TokenBucket` detrás de un puerto de infraestructura, permitiendo coordinar las cuotas de RPM y TPM entre múltiples trabajadores mediante un almacén distribuido.
* **P4-R03 (Sustitución de Estimador de Tokens en FinOps - P0):** Reemplazar el uso de `FastWordEstimator` en el calculador de presupuesto del prompt (`PromptBudgetCalculator`) y en la medición de inferencia por un tokenizador exacto BPE/Tiktoken (`ExactBPEEstimator`), evitando desbordamientos de ventana en el backend del LLM.
* **P4-R04 (Unificación del Pipeline de Ejecución de Workers - P0):** Homologar el comportamiento de procesamiento entre `AsyncDispatcher` y `LLMWorkerDaemon`. El despachador en memoria y el worker en segundo plano deben consumir las mismas políticas de validación, reintento, caché y curación.
* **P4-R05 (Eliminación de Contextos Nulos en Caché - P1):** Retirar `DummyContextResolver` de la ruta de ejecución de producción en `apps/cli/main.py` y sustituirlo por el resolvedor jerárquico real, impidiendo la contaminación del repositorio de caché con traducciones descontextualizadas.
* **P4-R06 (Constructor Inmutable en the Dispatcher - P1):** Eliminar la inyección mutativa posterior de tuberías (`dispatcher.validation_pipeline = ...`) en `pipeline_factory.py`. Exigir la presencia inmutable de los pipelines de validación y curación desde el constructor de `AsyncDispatcher`.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Diseño Abstraído de Adaptadores y Prompts:** **SÓLIDO Y BIEN ESTRUCTURADO.** Las abstracciones de dialectos (`OpenAICompatibleDialect`), la construcción del sobre (`PromptEnvelope`), la medición FinOps y la capa de almacenamiento en caché están correctamente modeladas a nivel de clases.
2. **Integración Operacional y Resiliencia en Runtime:** **GRAVEMENTE VULNERABLE.** La falta de integración del Circuit Breaker, el Rate Limiting aislado en memoria RAM, la estimación imprecisa de tokens y la existencia de dos modos de ejecución divergentes impiden certificar el sistema para cargas de producción distribuidas.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P4

The audit for **Block P4 (Dispatch $\rightarrow$ LLM $\rightarrow$ FinOps $\rightarrow$ Cache $\rightarrow$ Resilience)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P4
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Circuit Breaker zombi y Rate Limiter no distribuido)
  Remediation Backlog      | OPEN (Reglas P4-R01 a P4-R06 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque P4. Se comprobó que el flujo de empaquetamiento e inferencia cuenta con abstracciones de calidad para prompts y caché, pero sufre de fallas estructurales graves de resiliencia (GlobalCircuitBreaker huérfano), descoordinación de cuotas para despliegues multi-proceso y riesgo de desbordamiento de contexto por estimaciones inexactas en fórmulas LaTeX. Queda strictly prohibido mutar código. Todos los hallazgos se registran en el backlog de remediación, habilitando la apertura de la auditoría del Bloque P5 (Validation $\rightarrow$ Healing $\rightarrow$ Revalidation)."*