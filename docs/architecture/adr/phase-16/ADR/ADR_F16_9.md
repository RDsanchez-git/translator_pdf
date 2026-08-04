# ARCHITECTURE DECISION RECORD (ADR)
## Fase 16.9: Prompt System Estructurado (Contrato de Inferencia)

**Contexto y Problema:**
El pipeline actual (Fase 14) representa la intención de traducción mediante cadenas de texto libre (`system_prompt`, `user_prompt`) dentro del DTO `PromptEnvelope`. Esta representación impide la validación estructural estricta, acopla la construcción del prompt a convenciones textuales frágiles y dificulta el soporte multi-proveedor (OpenAI, Gemini, Groq), ya que asume implícitamente un formato de diálogo universal.

**Objetivo:**
Sustituir el contrato textual interno por un contrato estructurado (validado mediante Pydantic), aislando la intención semántica de la traducción del dialecto específico requerido por cada proveedor LLM, sin alterar la topología del pipeline existente.

**Decisiones Arquitectónicas:**
1. **Contrato Estructurado de Inferencia:** Se introduce `PromptSchema` para reemplazar las cadenas de texto plano. Este esquema agrupará lógicamente *Constraints*, *Context* y *Payload*.
2. **Agnosticismo de Infraestructura:** El `PromptSchema` será estrictamente agnóstico. Se prohíbe la inclusión de configuraciones físicas de los SDKs (como `temperature`, `response_format`, `json_mode` o `seed`).
3. **Capa de Dialectos (`PromptDialect`):** Se introduce una separación explícita entre el esquema y el proveedor. El `PromptBuilder` genera el `PromptSchema`. Los adaptadores (`LLMProvider`) utilizarán un `PromptDialect` para traducir el esquema al formato nativo (JSON, arreglos de mensajes, etc.).
4. **Preservación del Pipeline:** El DTO transaccional seguirá siendo `PromptEnvelope`. El Dispatcher, Presupuestos (Budget), Caché y Telemetría continuarán operando sobre él.
5. **Determinismo de Caché:** Se introduce un `PromptCanonicalizer` encargado de transformar el `PromptSchema` en una representación JSON canónica, ordenada y determinista, sobre la cual se calcularán el hash de caché y los presupuestos FinOps.

**No-Objetivos:**
* No se modifican los Bounded Contexts anteriores: `TranslationUnit`, `DispatchResult`, `AST`, `Chunker`, `Validation`, o `Layout Compiler`.
* No se congela el modelo exacto del `PromptSchema` hasta finalizar la auditoría (Hito 0.5).
* No se incluyen reglas de negocio del trabajo documental (ej. `target_language`) dentro de las restricciones del prompt; estas pertenecen a la unidad de traducción o al perfil documental.

---

# ROADMAP DE EJECUCIÓN (Hitos)

## Hito 0: Mapa de Consumidores y Productores (Discovery)
Auditoría transversal para identificar quién lee, muta o depende del `PromptEnvelope` actualmente.
* Mapeo de `PromptBudgetCalculator.calculate()`.
* Mapeo de la jerarquía de adaptadores (`adapters.py`, `sync_bridge.py`).
* Mapeo del motor de caché (`cache_provider.py`).

## Hito 0.5: Descomposición del Prompt Actual
Análisis forense del `system_prompt` y `user_prompt` generados hoy.
* Clasificar las partes textuales actuales en: constantes, contexto histórico, instrucciones base, payload y metadata.
* Determinar qué campos exactos requiere el `PromptSchema` basándose en la realidad del código.

## Hito 1: Diseño del Contrato Estructurado (`PromptSchema`)
Implementación de las clases Pydantic agnósticas (sin inyectarlas en el pipeline aún).
* Creación de los submódulos de contexto, restricciones (constraints) y payload.

## Hito 2: Determinismo (`PromptCanonicalizer`)
Implementación del motor de hashing seguro para FinOps y Caché.
* Algoritmo de conversión a JSON canónico (`sort_keys=True`, sanitización de nulos) y hashing SHA256.

## Hito 3: Mutación del `PromptEnvelope` y `PromptBuilder`
Actualización del contrato interno.
* Modificar `PromptEnvelope` para reemplazar `system_prompt` y `user_prompt` por el nuevo campo `schema`.
* Actualizar el `PromptBuilder` para ensamblar objetos en lugar de concatenar cadenas.

## Hito 4: Alineación de Presupuestos (FinOps)
Refactorización del cálculo de tokens.
* El calculador consume el output del `PromptCanonicalizer` para medir el peso exacto de la serialización que viajará por la red.

## Hito 5: Serialización Tardía (`PromptDialect` y Adaptadores)
Delegación del formateo físico a la capa de red.
* Creación de los dialectos que transforman el `PromptSchema` en estructuras específicas de Gemini, Groq, etc.
* Actualización de los adaptadores para invocar los dialectos antes de disparar la petición HTTP.

## Hito 6: Pruebas de Contrato (Contract Tests)
Validación de integridad.
* Reemplazar las aserciones de *regex* por validaciones estructurales.
* Implementar *Contract Tests* para asegurar que los Dialectos generen las estructuras exigidas por los proveedores sin fugas silenciosas.



## TAXONOMÍA DE CONSUMIDORES DEL PROMPTENVELOPE (HITO 0)

Esta tabla clasifica el nivel de acoplamiento actual de cada componente con la representación interna del PromptEnvelope. Sirve como mapa de dependencias para el ADR, delimitando el impacto exacto y garantizando una migración sin regresiones durante la Fase 16.9.

| Componente | Tipo de Consumidor | Atributos Consumidos | Impacto y Acción (Fase 16.9) |
| :--- | :--- | :--- | :--- |
| `PromptBuilder` | **Productor** | Construye el DTO y sus hashes. | Modificar para instanciar el `PromptSchema` en lugar de concatenar cadenas. |
| `PromptBudgetCalculator` | **Consumidor Indirecto** | Ninguno (Consume `str` inyectados externamente). | Actualizar para medir los tokens exactos del JSON generado por el `PromptCanonicalizer`. |
| `GroqProvider` / `GeminiProvider` | **Consumidor Estructural** | `system_prompt`, `user_prompt`, `model_name` | Refactorizar para invocar un `PromptDialect` que transforme el `PromptSchema` al formato nativo. |
| `BypassProvider` | **No Consumidor** | `raw_payload` | Re-direccionar lectura hacia el nuevo sub-campo del esquema (ej. `payload.content`). |
| `CachedLLMProvider` | **Consumidor de Identidad** | `prompt_hash`, `prompt_version`, `model_name` | **Cero impacto.** Blindado; la idempotencia se mantiene si el canonicalizador es determinista. |


### Decisión Arquitectónica 6: Separación Ortogonal entre Intención y Restricción
El PromptSchema distinguirá explícitamente entre la intención de la tarea (Intent) y las invariantes operacionales (Constraints). La intención (TRANSLATE, PRESERVE, JUDGE) guiará el enrutamiento general del PromptDialect, mientras que las restricciones se agruparán por dominios de cohesión (Structural, Translation, Formatting) para gobernar las reglas condicionales, evitando listas planas de booleanos inextensibles.


## ACTUALIZACIÓN DEL ADR: ESTRATEGIA DE TRANSICIÓN
Se incorporan estas directivas al registro de decisiones para el Hito 3A:

- Decisión de Divergencia FinOps Transitoria:
Durante el período transitorio (Hito 3A), el cálculo de presupuestos continuará utilizando la representación legacy mediante un adaptador explícito (LegacyBudgetAdapter). La divergencia volumétrica respecto al payload JSON definitivo se considera un margen aceptable de diseño y será eliminada completamente en el Hito 4.

- Ortogonalidad de Dominio:
El enrutamiento de intenciones (PromptIntentMapper) y la generación de invariantes (ConstraintFactory) operarán como servicios de dominio separados.

- Erradicación Textual del DTO:
Se purgan definitivamente los campos system_prompt, user_prompt y raw_payload del PromptEnvelope. Cualquier necesidad transitoria de cadenas de texto será generada efímeramente y destruida en memoria.


## ACTUALIZACIÓN DEL ADR: DIALECTOS BIDIRECCIONALES Y RESULTADO DE INFERENCIA
Simetría de Fronteras (Bidirectional Dialects): Todo proveedor requerirá dos adaptadores ortogonales. Un RequestDialect que transforma el PromptSchema en parámetros nativos de red, y un ResponseDialect que transforma la respuesta cruda (JSON, XML, Texto) en un DTO de dominio unificado. El LLMProvider se restringe estrictamente a la ejecución HTTP/SDK.

Evolución del Contrato de Retorno (InferenceResult): Se abandona ProviderResult (centrado en el proveedor y en la traducción) en favor de InferenceResult (centrado en la operación de inferencia abstracta), preparando la Fase 17 para soportar jueces, evaluadores y extractores.


## ACTUALIZACIÓN FINAL DE ADRs (CIERRE FASE 16.9)
ADR: Desacople de Renderizado y Dialecto (SRP): El Dialecto no redacta prompts. Se introduce un PromptRenderer (Dominio) cuya única responsabilidad es transformar el PromptSchema en una tupla de texto lógica (system_text, user_text). El Dialecto (Infraestructura) consume esta tupla y la transforma en las estructuras físicas (messages[]).

ADR Futuro (Registrado para Fase 17): El PromptEnvelope evolucionará para transportar un DTO RenderedPrompt en lugar del PromptSchema completo, evitando que la infraestructura tenga acceso al modelo semántico de intención.

ADR: Unificación de Dialectos Estándar: Se crea OpenAICompatibleDialect. Se prohíbe crear dialectos específicos por marca si la API subyacente respeta el estándar de OpenAI.

ADR: Excepciones de Dominio para Inferencia: Se erradica el uso de ValueError genéricos en la capa de red. Toda falla de parseo o desobediencia del LLM levantará excepciones tipadas (DialectParsingError, MalformedInferenceResponse) para facilitar métricas y circuit breakers.



## RESULTADOS CONSOLIDADOS FASE 16.9 (Congelado)

### HITO 0: Auditoría Forense y Hallazgos de Arquitectura (Completado)
Se realizó una ingeniería inversa sobre el `_build_system` del `PromptBuilder` y la capa de presupuesto. Se detectó que el código actual acoplaba cuatro responsabilidades ortogonales: ingeniería de prompts (texto), reglas de negocio (constraints), serialización de red (JSON) y medición financiera (FinOps). Se dictaminó la refactorización mediante el patrón *Strangler Fig* para separar el dominio de la infraestructura sin romper el pipeline.

### HITO 1: Diseño del Contrato Estructurado (`PromptSchema`) (Completado)
Se eliminó la concatenación de *strings*. Se creó un modelo de dominio inmutable en `core/prompting/models.py` dividido en 4 cuadrantes cohesivos, totalmente agnóstico al proveedor LLM:
* `Intent`: El objetivo de la inferencia (ej. `TRANSLATE`, `PRESERVE`).
* `Context`: Metadata topológica (breadcrumbs, profundidad).
* `Constraints`: Invariantes inmutables (estructurales, traducción, presentación).
* `Payload`: La carga útil a operar.

### HITO 2: Determinismo y Canonicalización (Completado)
Se aisló la generación de identidad criptográfica para blindar la caché contra cambios en Pydantic o el intérprete de Python. Se implementó `PromptCanonicalizer` que convierte el `PromptSchema` en una representación de red lexicográficamente estable (`sort_keys=True`, `exclude_none=True`) y deriva de allí el hash SHA-256.

### HITO 3: Mutación del Contrato y Ensamblador Transitorio (Completado)
Se refactorizó el `PromptBuilder` para que funcione como una fábrica pura de objetos `PromptSchema`. Para prevenir el acoplamiento temporal y no romper el motor FinOps legacy, se implementó temporalmente un `LegacyBudgetAdapter` que proyectó el esquema de vuelta a texto, permitiendo integrar y testear el nuevo DTO inmutable manteniendo el pipeline en verde.

### HITO 4: Extracción del Bounded Context FinOps y DIP (Completado)
Se ejecutó la Inversión de Dependencias (DIP). Se creó el subdominio `core/findops/` con el protocolo `MeasurableInference`. El motor de FinOps (`PromptBudgetCalculator`) dejó de conocer qué es un prompt, evaluando únicamente un DTO volumétrico (`InferenceMeasurement`). Esto permitió medir con exactitud el peso del payload frente al *overhead estructural* (JSON/Sintaxis) elevando la observabilidad y previniendo los rechazos por límite de ventana. Se destruyó la deuda técnica (`LegacyBudgetAdapter`).

### HITO 5: Dialectos Bidireccionales SOTA y Arquitectura Hexagonal (Completado)
Se resolvió la última fuga de dominio separando la redacción del formato de red. 
* **Dominio:** `PromptRenderer` traduce el `PromptSchema` a instrucciones lógicas.
* **Infraestructura:** Se creó un dialecto unificado bidireccional (`OpenAICompatibleDialect`) que inyecta parámetros físicos (`response_format={"type": "json_object"}`) y parsea las salidas.
* **I/O:** El `GroqProvider` fue reducido a un puerto de transporte HTTP/SDK puro. 
* **Resultado:** El contrato de retorno mutó a `InferenceResult` y se introdujeron excepciones tipadas (`DialectParsingError`, `MalformedInferenceResponse`).