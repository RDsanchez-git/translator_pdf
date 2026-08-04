# ADR_F16_4.md

# Architecture Decision Record: Fase 16.4 (Translation Router)

## 1. Contexto y Problema
En el flujo de traducción de documentos complejos (STEM, académicos), coexisten componentes con alta carga de texto lingüístico y componentes estructurales inmutables (bloques de código, ecuaciones matriciales complejas, diagramas, imágenes). Enviar componentes estructurales al motor LLM (Fase 16.9) introduce ineficiencias críticas:
* **Fuga de Capital (FinOps):** Consumo innecesario de tokens en elementos que deben mantenerse idénticos al origen.
* **Corrupción Semántica:** Riesgo latente de que el LLM altere la sintaxis interna o formatee erróneamente la notación de código o bloques LaTeX, quebrando la fidelidad en la reconstrucción final.

Se requiere un componente de dominio puro que clasifique y bifurque el flujo de nodos antes de ingresar al empaquetamiento (Chunking), evitando el uso de condicionales imperativos complejos en la orquestación.

## 2. Decisión Arquitectónica
Se adopta la implementación de un **Translation Router** como un filtro funcional puro e inmutable dentro del dominio de procesamiento (`core/pipeline/router.py`). El router consume la enumeración estática `TranslationStrategy` inyectada en la Fase 16.2 y clasifica el destino de cada entidad en tiempo constante $O(1)$. Este componente opera de forma desacoplada de la persistencia, reintentos o la lógica de red.

## 3. Semántica de Canales de Salida
El flujo se distribuye en tres canales de ejecución mutuamente excluyentes:
* **`TRANSLATE`:** El nodo requiere procesamiento lingüístico. Su flujo destino es: `Fase 16.5 (Atomic Chunking) ➔ Fase 16.6 (Validation) ➔ Fase 16.9 (Prompt System) ➔ Inferencia LLM`.
* **`PASSTHROUGH`:** El nodo es estructuralmente atómico. Elude la pila de traducción y viaja intacto directamente hacia la Fase 16.8 (Layout Compiler).
* **`OMIT`:** El nodo contiene metadatos redundantes u obsoletos para el documento de salida (ej. números de página físicos del origen, marcas de agua). Es removido de inmediato del flujo en memoria.

## 4. Interfaces y Contratos de Dominio

```python
from enum import Enum
from typing import Protocol, Mapping
from types import MappingProxyType
from core.ast.models import ASTNode
from core.ast.enums import TranslationStrategy

class RouteChannel(str, Enum):
    TRANSLATE = "TRANSLATE"
    PASSTHROUGH = "PASSTHROUGH"
    OMIT = "OMIT"

class NodeRouter(Protocol):
    """Puerto funcional para el enrutamiento topológico."""
    def route(self, node: ASTNode) -> RouteChannel:
        ...

class TranslationRouter:
    """Implementación SOTA del enrutador declarativo.
    Determina la ruta del nodo en tiempo constante sin efectos secundarios."""
    
    _ROUTING_TABLE: Mapping[TranslationStrategy, RouteChannel] = MappingProxyType({
        TranslationStrategy.TRANSLATE: RouteChannel.TRANSLATE,
        TranslationStrategy.PASSTHROUGH: RouteChannel.PASSTHROUGH,
        TranslationStrategy.KEEP_ORIGINAL: RouteChannel.PASSTHROUGH,
        TranslationStrategy.OMIT: RouteChannel.OMIT,
    })

    def route(self, node: ASTNode) -> RouteChannel:
        """Clasifica el nodo basándose en su estrategia semántica interna."""
        return self._ROUTING_TABLE.get(node.strategy, RouteChannel.TRANSLATE)
```
## 5. Invariantes del Componente
- Aislamiento de Infraestructura: El TranslationRouter no puede importar, conocer ni invocar adaptadores de persistencia (BBDD), sistemas de telemetría, ni SDKs de proveedores de IA.
- Preservación del Streaming ($O(1)$ RAM): La interfaz procesa un único ASTNode a la vez. No recibe colecciones completas ni agrupa elementos, delegando el bucle de consumo al orquestador externo para impedir el uso de buffers de memoria u operaciones como itertools.tee().
- Inmutabilidad Absoluta: El router es de solo lectura. El nodo evaluado no sufre mutaciones en sus propiedades, ni clonaciones en memoria durante este proceso.
 ## 6. ConsecuenciasPositivas
- Optimización Económica (FinOps):Reducción determinista de costos de inferencia de tokens en red al aislar de forma segura bloques como TABLE_COMPLEX, IMAGE y DISPLAY_EQUATION.
- Testabilidad Aislada: Al ser una función matemática pura sobre el DTO, las pruebas unitarias se ejecutan instantáneamente sin necesidad de configurar simulacros (mocks) de bases de datos o red.
- Estabilización del Core Funcional: El PipelineOrchestrator asume el rol de Imperative Shell, aislando la infraestructura (guardar estados de checkpointing, realizar reintentos, persistir nodos passthrough en base de datos) del flujo lógico del documento.
- Negativas / RiesgosComplejidad en el Ensamblador: Delega la responsabilidad completa a la Fase 16.8 (Layout Compiler) de recuperar sincrónicamente los nodos desviados por la vía PASSTHROUGH y fusionarlos con los nodos procedentes de la vía TRANSLATE manteniendo el sequence_id original.

## 6. Hitos a Completar

Hito 1: Definición de Canales y Contratos (Puertos)El objetivo es aislar formalmente los tipos de transporte y las interfaces de enrutamiento antes de codificar la tabla de decisiones.Ubicación: core/pipeline/router.py (o el submódulo equivalente del pipeline).Entregables:Definición del enum RouteChannel (TRANSLATE, PASSTHROUGH, OMIT).Declaración del puerto NodeRouter utilizando typing.Protocol.Invariante: Este archivo no debe importar nada externo al dominio base del AST.Hito 2: Implementación del Router Declarativo y Tests PurosImplementación de la lógica de negocio del router utilizando estructuras indexadas de tiempo constante $O(1)$.Ubicación: core/pipeline/router.pyEntregables:Clase TranslationRouter cumpliendo el protocolo.Uso de MappingProxyType para blindar la tabla de ruteo stática contra mutaciones accidentales en tiempo de ejecución.Pila de Tests Unitarios: Pruebas instantáneas que verifiquen que un ASTNode con TranslationStrategy.PASSTHROUGH devuelve estrictamente RouteChannel.PASSTHROUGH, sin levantar dependencias de base de datos ni red.Hito 3: Intercepción en el Orquestador (Imperative Shell)Integración del router en el bucle principal de procesamiento de la aplicación. Aquí es donde se materializa la bifurcación del flujo de datos en streaming.Ubicación: core/pipeline/orchestrator.py (o el componente controlador del workflow).Entregables:Inyección del NodeRouter en el constructor del orquestador.Refactorización del bucle de consumo de nodos (que viene de la Fase 16.3). Por cada nodo, se evalúa router.route(node) mediante un bloque match/case idiomático.Comportamiento del Stream: * Los nodos TRANSLATE continúan hacia el Chunker (Fase 16.5).Los nodos PASSTHROUGH se desvían de inmediato (aquí el orquestador decidirá si los escribe temporalmente en el storage de checkpoints o los guarda para el ensamblador final).Los nodos OMIT mueren en el pipeline.Criterios de Aceptación para ProducciónCero itertools.tee: El orquestador debe procesar el flujo en un único pase lineal. Si la memoria RAM se eleva proporcionalmente al número de nodos passthrough, el hito será rechazado.Tratamiento de Errores Defensivo: Si por alguna inconsistencia de una fase previa un nodo llega con una estrategia no mapeada, el router debe clasificarlo por defecto como TRANSLATE para asegurar que el contenido se procese y no se pierda información de forma silenciosa.


# RESULTADOS CONSOLIDADOS FASE 16.4: TRANSLATION ROUTER

## HITO 1: Definición de Canales y Contratos (Congelado)
Se estableció la separación topológica del subdominio de enrutamiento (`core/routing/`).
* **RouteChannel:** Se definió una enumeración semántica pura (`TRANSLATE`, `PASSTHROUGH`, `OMIT`) que actúa como lenguaje ubicuo del dominio, sin acoplamiento a la ejecución física.
* **NodeRouter (Protocol):** Se abstrajo el clasificador mediante un puerto hexagonal `route(node: ASTNode) -> RouteChannel`, permitiendo el principio *Open/Closed* para futuros motores de enrutamiento (ej. `CostAwareRouter`).
* **PassthroughSink (Protocol):** Se creó un puerto en el orquestador con un contrato de resiliencia estricto: la implementación debe garantizar la persistencia síncrona o lanzar una excepción, prohibiendo la pérdida silenciosa de nodos estructurales.

## HITO 2: Implementación Funcional Pura (Congelado)
Se implementó `StrategyRouter` como una función matemática disfrazada de objeto.
* **Complejidad $O(1)$:** El enrutamiento se resuelve mediante una tabla declarativa inmutable indexada por `TranslationStrategy`.
* **Invariante de Determinismo:** El router es referencialmente transparente. Para el mismo nodo de entrada, siempre retorna el mismo canal sin depender de estado interno, cachés o I/O.
* **Separación de Responsabilidades (Interpretación vs Decisión):** El router tiene estrictamente prohibido evaluar propiedades del nodo (ej. `node.type == TABLE`) para inferir reglas. Se limita a interpretar la estrategia precalculada en la Fase 16.2.
* **Política Fail-Open:** Ante una estrategia nula o desconocida, el sistema deriva el nodo a `TRANSLATE` por defecto, garantizando que el contenido anómalo no sea descartado inadvertidamente.

## HITO 3: Integración en la Capa de Aplicación (Congelado)
Se ensambló `RoutingWorkflow`, actuando como el *Imperative Shell* que coordina el núcleo funcional con los efectos secundarios de infraestructura.
* **Streaming y Back-Pressure Nativo:** El workflow consume el flujo a través de un `Iterator[ASTNode]`, cediendo (`yield`) los nodos traducibles sin usar *buffers* masivos, listas intermedias o `itertools.tee`. El ritmo de ejecución queda dictado por el consumidor final.
* **Resiliencia Fail-Fast:** La derivación de nodos al `PassthroughSink` no captura excepciones generadas por la infraestructura de persistencia. Un fallo en el almacenamiento aborta el pipeline, evitando la generación de un documento topológicamente corrupto o incompleto.
* **Telemetría Estructurada:** Se inyectaron métricas rigurosas (`RoutingMetrics` mediante *dataclasses* y eventos semánticos `StrEnum`) preparadas para ser indexadas en plataformas de observabilidad SOTA (ELK, Datadog), evitando la interpolación estática de strings.

**Estado de la Fase 16.4:** 100% Congelada. Arquitectura de Grado Producción completada.