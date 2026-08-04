# ADR_F16_5.md

# Architecture Decision Record: Fase 16.5 (Policy-Driven Atomic Chunking)

## 1. Contexto y Problema
El canal `TRANSLATE` emite un flujo continuo de nodos lógicos. Para ser procesados por un motor de inferencia (LLM), deben agruparse en lotes (*chunks*) que respeten la ventana de contexto impuesta por el proveedor. Si el agrupamiento es ciego y corta bloques estructurales (ecuaciones matriciales, tablas) o cruza fronteras lógicas incompatibles, corromperá irremediablemente la semántica y la reconstrucción del documento.

## 2. Decisión Arquitectónica
Se adopta un **Chunker Declarativo Basado en Políticas**. El motor de agrupamiento (`StreamingChunker`) es agnóstico a las reglas de negocio. Su comportamiento de fragmentación queda orquestado por tres dependencias inyectadas:
1.  **`TokenEstimator`:** Provee el peso algorítmico del nodo.
2.  **`NodeAtomicityPolicy`:** Dictamina si un nodo es estructuralmente indivisible.
3.  **`ChunkBoundaryPolicy`:** Dictamina si dos nodos pueden coexistir en el mismo lote mediante decisiones semánticas registrables (`BoundaryDecision`).

## 3. Interfaces y Contratos Hexagonales (core/chunking/protocols.py)

```python
from enum import StrEnum
from typing import Protocol
from collections.abc import Iterator
from dataclasses import dataclass
from core.ast.models import ASTNode

class BoundaryDecision(StrEnum):
    """Permite telemetría exacta sobre las razones de partición."""
    ALLOW = "ALLOW"
    HARD_BREAK = "HARD_BREAK"
    SOFT_BREAK = "SOFT_BREAK"

@dataclass(slots=True, frozen=True)
class ChunkMetadata:
    estimated_tokens: int
    node_count: int  # Métrica fundamental para observabilidad
    sequence_start: int
    sequence_end: int

@dataclass(slots=True, frozen=True)
class TranslationChunk:
    """Unidad inmutable despachada al LLM."""
    chunk_id: str
    nodes: tuple[ASTNode, ...]
    metadata: ChunkMetadata

class TokenEstimator(Protocol):
    def estimate(self, node: ASTNode) -> int:
        ...

class NodeAtomicityPolicy(Protocol):
    def is_atomic(self, node: ASTNode) -> bool:
        ...

class ChunkBoundaryPolicy(Protocol):
    def can_group(self, current_chunk_nodes: tuple[ASTNode, ...], next_node: ASTNode) -> BoundaryDecision:
        ...

class ASTChunker(Protocol):
    """Puerto de agregación puro. Consume y emite iteradores (Back-Pressure)."""
    def chunk(self, stream: Iterator[ASTNode], max_tokens: int) -> Iterator[TranslationChunk]:
        ...
```

## 4. Invariantes del Dominio y Principios Arquitectónicos

1.  **Monotonicidad del Pipeline (Zero Mutation):** Desde la Fase 16.5 en adelante, ningún componente tiene permitido transformar, mutar o re-segmentar un `ASTNode`. Todos consumen el AST sellado en la Fase 16.3. Si un nodo es inválido o inmanejable, el Chunker debe fallar, nunca alterar el árbol.
2.  **Determinismo del Estimador:** Toda implementación de `TokenEstimator` debe ser pura, determinista y libre de efectos secundarios (I/O). Estrictamente prohibido invocar APIs externas (OpenAI, Gemini) para estimar pesos; deben usarse heurísticas locales o tokenizadores *offline*.
3.  **Reutilización de Abstracciones:** Las políticas (`NodeAtomicityPolicy`, `ChunkBoundaryPolicy`) tienen prohibido reinventar reglas de negocio utilizando reflexión (ej. `isinstance(node.payload, EquationPayload)`). Deben basar sus decisiones en las abstracciones ya consolidadas en el AST (ej. `node.node_type`, `node.strategy`).
4.  **Fail-Fast por Sobredimensionamiento:** Si `is_atomic(node) == True` AND `estimate(node) > max_tokens`, el Chunker lanzará inmediatamente `AtomicNodeTooLargeException`. Jamás intentará truncar o dividir el nodo. Otros errores topológicos lanzarán `ChunkConstructionException`.
5.  **Frontera Dura:** Si `can_group` retorna `HARD_BREAK` o `SOFT_BREAK`, el Chunker cerrará el *chunk* actual sin importar la capacidad sobrante de tokens.

## 5. Excepciones de Dominio (`core/chunking/exceptions.py`)

```python
class ChunkingException(Exception):
    """Excepción base del subdominio de empaquetado."""
    pass

class AtomicNodeTooLargeException(ChunkingException):
    """Lanzada cuando un nodo indivisible supera la ventana máxima del LLM."""
    pass

class ChunkConstructionException(ChunkingException):
    """Lanzada por violaciones lógicas durante el ensamblado del bloque."""
    pass
```

## 6. Consecuencias
* **Positivas:** Simetría arquitectónica total con `core/segmenter` y `core/routing`. Trazabilidad analítica superior gracias a `BoundaryDecision` y `node_count`. El límite claro de la *Monotonicidad* protege al modelo de datos contra deuda técnica futura.
* **Negativas:** Exige que el Orquestador del Pipeline implemente estrategias de mitigación rigurosas en su bloque `try/except` para manejar `AtomicNodeTooLargeException` (ej. enviar a cuarentena, alertar al usuario), ya que el Chunker rehusará resolver el problema internamente.

---

## HITOS DE IMPLEMENTACIÓN (FASE 16.5)

### Hito 1: Estructura, Contratos y Excepciones
* Creación del directorio del subdominio `core/chunking/`.
* Implementación de los DTOs en `models.py` (`TranslationChunk`, `ChunkMetadata`, `BoundaryDecision`).
* Implementación de la jerarquía de errores en `exceptions.py` (`ChunkingException`, `AtomicNodeTooLargeException`, `ChunkConstructionException`).
* Aislamiento de los contratos hexagonales en `protocols.py` (`TokenEstimator`, `NodeAtomicityPolicy`, `ChunkBoundaryPolicy`, `ASTChunker`).

### Hito 2: Implementación de Políticas SOTA
* Creación de `core/chunking/policies.py`.
* Implementación de `ScientificNodeAtomicityPolicy`: Retorna `True` analizando exclusivamente atributos existentes como `node.node_type` (ej. `ContentNodeType.EQUATION`, `ContentNodeType.TABLE`, `ContentNodeType.CODE`).
* Implementación de `ScientificChunkBoundaryPolicy`: Emite `BoundaryDecision.HARD_BREAK` para evitar cortes antinaturales (ej. aislar un `HEADING` del primer párrafo de su sección) basándose en las propiedades semánticas del AST.

### Hito 3: Motor Streaming (El Chunker)
* Creación de `core/chunking/chunker.py`.
* Implementación de `StreamingChunker` cumpliendo estrictamente con el contrato de Back-Pressure (`Iterator`).
* Aplicación de la lógica *Fail-Fast* evaluando el tamaño de los nodos atómicos contra `max_tokens` antes de la acumulación. Acumulación inmutable y emisión $O(1)$ de los `TranslationChunk` instanciados.


# RESULTADOS CONSOLIDADOS FASE 16.5: POLICY-DRIVEN ATOMIC CHUNKING

## HITO 1: Estructura, Contratos y Excepciones (Congelado)
Se consolidó la topología aislada del subdominio `core/chunking/` respetando estrictamente la arquitectura hexagonal.
* **Modelos de Dominio:** Implementación de DTOs inmutables y optimizados (`slots=True`, `frozen=True`) para `TranslationChunk` y `ChunkMetadata`. Sustitución de booleanos por la enumeración semántica `BoundaryDecision` (`ALLOW`, `HARD_BREAK`, `SOFT_BREAK`) para trazabilidad de particiones.
* **Contratos (Puertos):** Aislamiento total de las dependencias de negocio y estimación mediante `Protocol` (`TokenEstimator`, `NodeAtomicityPolicy`, `ChunkBoundaryPolicy`, `ASTChunker`).
* **Resiliencia:** Jerarquía de excepciones (`ChunkingException`, `AtomicNodeTooLargeException`, `ChunkConstructionException`) diseñada para proteger el pipeline forzando caídas controladas frente a violaciones estructurales.

## HITO 2: Implementación de Políticas SOTA (Congelado)
Se construyó el motor de políticas abstrayendo la lógica del agrupamiento y respetando el modelo de datos consolidado de la Fase 16.1/16.3.
* **Reutilización de Abstracciones (SRP):** `StructuralNodeAtomicityPolicy` evalúa indivisibilidad en tiempo constante $O(1)$ utilizando un `frozenset` de `ContentNodeType` (ej. `DISPLAY_EQUATION`, `TABLE_COMPLEX`, `COMPOSITE_BLOCK`), erradicando la reflexión insegura (`isinstance(payload)`).
* **Protección del Dominio (YAGNI):** La política `StructuralChunkBoundaryPolicy` fue adaptada al contrato real del `ASTNode`, rechazando alteraciones (como la inyección prematura del atributo `language` en metadatos físicos) y dejando una base OCP preparada para futuras heurísticas semánticas.

## HITO 3: Motor Streaming (Congelado)
Se implementó `PolicyDrivenStreamingChunker` como un núcleo funcional puro y altamente observable.
* **Zero Mutation & Back-Pressure:** El motor es estrictamente un acumulador de solo lectura que consume y emite iteradores, garantizando una huella de memoria plana $O(1)$ sin buffers globales.
* **Fail-Fast:** Validación matemática del tamaño frente al `max_tokens`; si un nodo estructural es atómico y supera el presupuesto, se aborta la ejecución antes de corromper la sintaxis del documento.
* **Hashing Determinista Anti-Colisión:** Generación de `chunk_id` mediante SHA-256 utilizando un separador explícito (`"|".join`) y casteos seguros, asegurando inyectividad y protegiendo los mecanismos de caché.
* **Telemetría y Configuración:** Erradicación de números mágicos mediante la inyección de `ChunkerConfig` y emisión de métricas operativas exhaustivas (`nodes_processed`, `chunks_generated`, `tokens_processed`) para observabilidad en producción.

**Estado de la Fase 16.5:** 100% Congelada. Arquitectura de Grado Producción completada.