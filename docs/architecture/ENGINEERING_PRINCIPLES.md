# Engineering Principles & Architectural Manifesto

Este documento establece las directrices inmutables de ingeniería para el desarrollo del proyecto. Cualquier modelo de IA, desarrollador o arquitecto que interactúe con este repositorio debe adherirse estrictamente a estos principios para garantizar software de grado producción (SOTA).

## I. Mindset & Objetividad Técnica
* **Cero Sesgo de Confirmación:** Las decisiones arquitectónicas deben basarse en métricas, invariantes comprobables y escalabilidad real, no en preferencias estéticas o inercias de diseño.
* **Calidad sobre Velocidad:** No se acepta deuda técnica deliberada ("hacks" o "placeholders") en el dominio core. Las soluciones deben ser definitivas y robustas desde su concepción.
* **YAGNI (You Aren't Gonna Need It):** No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas. Cada componente responde a una necesidad actual y medible.

## II. Paradigmas Arquitectónicos
* **Arquitectura Hexagonal (Ports and Adapters):** Separación estricta entre el Dominio (Lógica pura, AST, Modelos) y la Infraestructura (OCR, LLMs, File I/O). 
* **Functional Core, Imperative Shell:** El núcleo del procesamiento de datos (ej. manipulación del AST, segmentación, chunking) se construirá con funciones puras sin efectos secundarios. La mutabilidad y el I/O se empujan a los bordes del sistema.
* **Estructuras Planas (Flat Design):** Se prefieren secuencias lineales unidimensionales (Flat AST) enriquecidas con metadatos topológicos (`depth`, `parent_id`) en lugar de árboles multidimensionales anidados, garantizando recorridos en tiempo constante $O(n)$.
* **Stateless Components:** Los servicios, orquestadores y resolutores (ej. `StrategyResolver`, `Segmenter`) no deben retener estado en memoria entre ejecuciones. 

## III. Estándares de Código
* **Explicit over Implicit:** Cero "magia" en el código. No se permite delegar instanciaciones complejas a comportamientos ocultos de frameworks (ej. Pydantic validators adivinando tipos). Uso de factorías explícitas y tipado estricto estático.
* **Open/Closed Principle (OCP):** El diseño debe ser abierto para la extensión y cerrado para la modificación. Se exige el uso de Registros Estáticos (`Registries`) y Protocolos/Interfaces para instanciar lógicas variables en lugar de cadenas de `if/elif` o `switch`.
* **Inmutabilidad de DTOs:** Las entidades de transporte de datos (`Payloads`, `Metadata`) deben ser inmutables (`frozen=True`). Cualquier transición de estado requiere retornar una copia nueva del objeto.

## IV. Production & SRE First (Site Reliability Engineering)
* **Cero Fallos Silenciosos:** Si un componente recibe un dato anómalo o un tipo no mapeado, el sistema debe emitir un Warning indexable explícito (ej. `[AST-001]`) o fallar duro (Raise Exception). Nunca se degrada silenciosamente la calidad del dato para "que siga funcionando".
* **Trazabilidad Absoluta:** El linaje del dato (origen semántico, índices físicos, índices lógicos) es sagrado y debe propagarse intacto a través de todas las transformaciones del pipeline sin corromperse.