# ADR_F16_8.md

# Architecture Decision Record: Fase 16.8 (Context-Aware Layout Compilation via Rendering Policies)

## Fase 16.8: 

## 1. Contexto y Problema
El pipeline preserva un `InferredDocumentProfile` (topología y taxonomía) cruzando la frontera asincrónica hasta el orquestador final. El `TexBuilder` actual opera como un generador estático y agnóstico. Acoplar directamente el `DocumentProfile` al compilador introduciría lógica de dominio heurístico en la capa de renderizado, violando el principio de responsabilidad única (SRP) y generando un crecimiento insostenible de complejidad ciclomática al manejar variaciones espaciales estáticas.

## 2. Decisión Arquitectónica
1. Introducir un `RenderContext` como Capa Anticorrupción (ACL) entre el perfil del documento y el compilador LaTeX.
2. Definir un nuevo Bounded Context interno en `core/compiler/rendering/` que aloje los contratos de políticas inyectables:
    * `LayoutRenderingPolicy`: Controla el preámbulo, clases documentales y topología general.
    * `FloatPlacementPolicy`: Decide dinámicamente el entorno LaTeX (ej. figure vs figure*) evaluando la geometría del nodo contra la topología del documento.
    * `EquationRenderingPolicy`: Gobierna las estrategias de ruptura y truncamiento matemático (split, aligned, multline).
3. `TexBuilder` delegará las decisiones estructurales a estas políticas a través del `RenderContext`, manteniéndose ciego a la heurística de inferencia original.

## 3. Consecuencias
* TexBuilder queda estrictamente como un consumidor de directivas de renderizado (Cumplimiento OCP).
* Eliminación de falsos positivos en el ensanchamiento de imágenes/tablas en formatos a doble columna (ej. IEEE).
* Preparación del pipeline para inyectar contextos de renderizado divergentes (HTML, ePub) sin alterar la lógica de traducción base.

---

# ROADMAP DE EJECUCIÓN (Hitos)

## Hito 0: Auditoría del Compilador (Discovery)
Auditoría estática de los artefactos existentes sin mutación de código.
* Mapeo del ciclo de vida en `DocumentAssembler.assemble()`.
* Identificación de puntos de inyección del preámbulo y patrones de recorrido del AST en `TexBuilder` (Visitor vs Lineal).
* Documentación de la gestión actual de flotantes y ecuaciones.
* **Entregable:** Informe de diagnóstico de puntos de acoplamiento.

## Hito 1: Diseño del RenderContext y Anti-Corruption Layer
Establecimiento de las interfaces y el factory.
* Creación del directorio `core/compiler/rendering/`.
* Definición de interfaces puras: `RenderContext`, `LayoutRenderingPolicy`, `FloatPlacementPolicy`, `EquationRenderingPolicy`.
* Implementación de `RenderContextFactory` responsable de traducir `DocumentProfile` a un `RenderContext` materializado.

## Hito 2: Refactor Inverso de TexBuilder (IoC)
Sustitución de dependencias sin añadir lógica funcional nueva.
* Modificar `TexBuilder.__init__` para exigir la inyección estricta de un objeto `RenderContext`.
* Purgar configuraciones de preámbulo hardcodeadas, enrutándolas temporalmente a través del contexto inyectado.

## Hito 3: Implementación de Políticas de Renderizado (SOTA)
Desarrollo de las implementaciones concretas de las políticas diseñadas en el Hito 1.
* Implementación de la estrategia dinámica para `twocolumn` vs `onecolumn` y sus paquetes LaTeX asociados.
* Implementación de la evaluación geométrica en `FloatPlacementPolicy` para discriminar el uso seguro de entornos con asterisco.
* Configuración estricta de entornos de ruptura en `EquationRenderingPolicy`.

## Hito 4: Integración CQRS y Composition Root
Cableado del flujo de control en la capa de aplicación.
* Actualización de `DocumentAssembler` para consumir `RenderContextFactory` e hidratar el perfil desde `ProfileStore` o la base de datos de documentos.
* Ensamblaje final en el Composition Root y resolución de dependencias.

---

### ADVERTENCIA DE VIABILIDAD TÉCNICA
El motor de renderizado de LaTeX nativo (pdflatex/xelatex) presenta deficiencias históricas en el algoritmo de posicionamiento de flotantes (Floats Algorithm) cuando se alternan anchos de página completos con diseños a doble columna. Será mandatorio que la `LayoutRenderingPolicy` inyecte pragmáticamente paquetes correctivos del estado del arte (SOTA) en el ecosistema LaTeX, específicamente `dblfloatfix` o `stfloats`, para mitigar colisiones espaciales y asegurar que las figuras a doble ancho se adhieran a los anclajes topológicos (t, b, h) sin ser desplazadas erráticamente al final de la cola del documento.


## RESULTADOS CONSOLIDADOS FASE 16.8 (Congelado)

### HITO 0: Auditoría y Hallazgos de Arquitectura (Completado)
Se realizó un *Discovery* estático del pipeline revelando la inviabilidad de acoplar directamente el `DocumentProfile` al compilador.
* **Descubrimiento 1 (Falsa equivalencia 1:N):** Se detectó que un chunk agrupa múltiples nodos, requiriendo una estrategia de consolidación semántica.
* **Descubrimiento 2 (Agujero Negro de Degradación):** El *Graceful Degradation* de la Fase 15 perdía el anclaje topológico (`translated_unit = None`), exigiendo un mecanismo de rescate.

### HITO 1 y 1.5: Anti-Corruption Layer y DTOs de Frontera (Completado)
Creación del subdominio `core/compiler/rendering/` aislando definitivamente al compilador del pipeline de NLP/Parsing.
* **RenderUnit (DTO):** Se erradicó la fuga de metadatos, hashes y linajes del `ASTNode` hacia el compilador. El `TexBuilder` ahora solo consume `RenderUnit` con geometría plana e inmutable.
* **RenderUnitMapper:** Componente vital que traduce el `ASTNode` y resuelve colisiones 1:N aplicando una jerarquía de prioridades estricta (ej. si un chunk combina texto y tabla, el bloque se protege con el renderizador de tablas).

### HITO 2 y 3: Compilador Ciego y Patrón Strategy (Completado)
Refactorización absoluta de `apps/compiler/tex_builder.py` y diseño de políticas OCP.
* **TexBuilder (IoC):** Se eliminó el 100% de la lógica de dominio (`if IMAGE`, escapes mágicos, preámbulos fijos). Ahora opera en estricto orden lineal iterando unidades y llamando a `context.render_unit()`.
* **RenderingStrategies:** Implementación de `AdaptiveFloatStrategy` (evalúa umbrales espaciales para inyectar `figure*`), `TextRenderStrategy` (MVP de sanitización) y generadores dinámicos de preámbulo condicionados a la configuración inyectada.

### HITO 4: Integración No-Invasiva y CQRS Facade (Completado)
Resolución de la orquestación final sin contaminar las responsabilidades del ensamblador existente (`DocumentAssembler`).
* **CompilationService (Facade):** Orquestador puro que consume el `DocumentAssembler`, inyecta el `ProfileStore` e hidrata la topología.
* **Bulk Fetch Indexado:** Solución al problema N+1 consultando el `ASTRegistry` en un solo viaje de red y construyendo un índice en memoria basado en `control_plane["chunk_id"]`.
* **Fallback Semántico:** Ante un fallo del LLM, el servicio recupera el nodo original por su `chunk_id`, preserva su contrato espacial y utiliza el payload intacto rescatado de la base de datos de integridad, sin degradar tablas o ecuaciones a texto plano.