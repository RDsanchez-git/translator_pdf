# ADR_F16_6.md

# Architecture Decision Record: Fase 16.6 (Validation Polymorphism)

## 1. Contexto y Problema
El pipeline procesa un AST heterogéneo. Aplicar reglas globales de validación provoca falsos positivos y falsos negativos. Un motor de reglas monolítico (`if/elif` masivo) escala deficientemente y acopla heurísticas ortogonales. Se requiere un mecanismo polimórfico, determinista y preparado para *streaming* donde la validación se adapte dinámicamente a la ontología del nodo sin romper el consumo de memoria plana $O(1)$.

## 2. Decisión Arquitectónica
Se adopta un **Validation Engine basado en Registry (Inversión de Control) y Streaming**.
1. Se descartan las estructuras condicionales rígidas centralizadas.
2. Cada validador inyectable (`NodeValidator`) define su propio contrato de aplicabilidad (`can_validate`).
3. **Segregación de Criterio:** Los validadores tienen prohibido mezclar dimensiones ontológicas (ej. no mezclar `ContentNodeType` con `TranslationStrategy`). Un validador es puramente estructural o puramente estratégico.
4. El orquestador del motor (`ValidationEngine`) recibe una `Sequence[NodeValidator]`, itera el flujo de nodos y cede (`yield`) exclusivamente las infracciones detectadas.

## 3. Interfaces y Contratos Hexagonales (core/validation/protocols.py)

```python
from enum import StrEnum
from typing import Protocol
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from core.ast.models import ASTNode

class ValidationSeverity(StrEnum):
    """
    SOTA: Ausencia deliberada de 'PASS'. 
    Solo se emiten anomalías para evitar contaminación del bus de eventos (ELK/Datadog).
    """
    INFO = "INFO"           # Observación telemetría
    SOFT_FAIL = "SOFT_FAIL" # Advertencia, el workflow decidirá
    HARD_FAIL = "HARD_FAIL" # Invariante roto, aborto inminente

@dataclass(slots=True, frozen=True)
class ValidationResult:
    """SOTA: DTO de infracción enriquecido con contexto topológico para trazabilidad."""
    node_id: str
    sequence_id: int
    severity: ValidationSeverity
    message: str
    validator_name: str

class NodeValidator(Protocol):
    """Contrato puro para estrategias de validación aisladas."""
    
    @property
    def name(self) -> str:
        ...

    def can_validate(self, node: ASTNode) -> bool:
        """Determina aplicabilidad basándose en UNA única dimensión del dominio."""
        ...

    def validate(self, node: ASTNode) -> Iterator[ValidationResult]:
        """Ejecuta la validación en O(1) de memoria, emitiendo infracciones de forma perezosa."""
        ...

class ValidationEngine(Protocol):
    """Puerto funcional para orquestación de validaciones en flujo continuo."""
    def validate_stream(self, stream: Iterator[ASTNode]) -> Iterator[ValidationResult]:
        ...
```

## 4. Invariantes del Dominio y Principios Arquitectónicos

1.  **Zero Mutation (Monotonicidad):** Los validadores son estrictamente observacionales. Tienen prohibido alterar, corregir o reconstruir el `ASTNode`.
2.  **Streaming End-to-End:** El motor y los validadores devuelven `Iterator[ValidationResult]`. Estrictamente prohibido materializar resultados en listas (`list[ValidationResult]`), manteniendo la coherencia de memoria plana desde la Fase 16.3.
3.  **Prohibición de Excepciones en el Motor:** El `ValidationEngine` y sus validadores jamás lanzan excepciones de validación (ej. `DocumentValidationError`). Su responsabilidad finaliza emitiendo un `HARD_FAIL`. Es el *Workflow* (capa imperativa) quien aborta el pipeline evaluando los resultados.
4.  **Consumo Pasivo de Hashes:** El `HashValidator` audita integridad consumiendo los hashes ya calculados en fases previas o en metadatos físicos. Tiene prohibido invocar algoritmos criptográficos para recalcular identidad, evitando duplicación computacional.
5.  **Ortogonalidad de Reglas:** Un mismo nodo puede activar múltiples validadores en una sola pasada.

## 5. Consecuencias
* **Positivas:** Trazabilidad absoluta de errores gracias a `node_id` y `sequence_id`. Cumplimiento total de OCP. Mantenimiento del invariante de *Back-Pressure* mediante iteradores.
* **Negativas:** La delegación de excepciones obliga a la capa `workflow` a implementar un sumidero iterativo inteligente que frene el stream del AST si un `ValidationResult` emite `HARD_FAIL`.

---

## HITOS DE IMPLEMENTACIÓN (FASE 16.6)

### Hito 1: Contratos, DTOs y Dominio de Resultados
Establecer el lenguaje común y las interfaces que usarán todas las validaciones sin acoplarse a ninguna regla de negocio específica.
* Creación del directorio del subdominio `core/validation/`.
* Implementación de estructuras inmutables en `models.py` (`ValidationSeverity`, `ValidationResult`).
* Definición de contratos en `protocols.py` asegurando el uso de `Iterator` y `Sequence` (`NodeValidator`, `ValidationEngine`).

### Hito 2: Catálogo de Validadores (Zero Mutation)
Construcción de las reglas de validación aisladas en `core/validation/validators.py`.
* Implementación de validadores estructurales basados estrictamente en `ContentNodeType` (ej. `StructuralEquationValidator` para `DISPLAY_EQUATION`).
* Implementación de validadores estratégicos basados estrictamente en `TranslationStrategy` (ej. `IntegrityHashValidator` para auditar la existencia y longitud de los hashes en nodos `PASSTHROUGH`).

### Hito 3: Motor Polimórfico en Streaming
Implementación del coordinador que amarra todo el sistema en `core/validation/engine.py`.
* Implementación de `PolymorphicValidationEngine` que recibe `Sequence[NodeValidator]`.
* Lógica del método `validate_stream` iterando el flujo $O(n)$ del AST, evaluando las reglas en tiempo constante y emitiendo `yield ValidationResult` únicamente ante infracciones detectadas, sin interrumpir el flujo directamente mediante excepciones.


TICKET: TCH-042 - Evolución de Proyección de Payloads del AST
SEVERIDAD: P3 (Mejora Arquitectónica / Deuda Técnica)
DOMINIO: core/ast

DESCRIPCIÓN: 
Actualmente, el componente `StronglyTypedTextExtractor` (core/validation/ast) depende de una verificación explícita de tipos concretos (ParagraphPayload, MathPayload, etc.) mediante `isinstance`. Esto viola parcialmente OCP ante la adición de nuevos nodos.

ACCIÓN REQUERIDA:
1. Introducir una interfaz base `TextBearingPayload(Protocol)` en el dominio del AST.
2. Alternativa SOTA: Implementar un `PayloadProjectionService` centralizado que exponga vistas polimórficas (text(), latex(), markdown()) para ser consumido por subsistemas como Validation, Chunking y Assembler.
3. Refactorizar `StronglyTypedTextExtractor` para depender exclusivamente de esta nueva abstracción.


# RESULTADOS CONSOLIDADOS FASE 16.6: VALIDATION POLYMORPHISM

## HITO 1: Bounded Context y Contratos (Congelado)
Se estableció el subdominio `core/validation/ast/` para segregar físicamente la validación pre-LLM (topológica) de la validación documental post-LLM.
* **Modelos de Dominio:** Implementación de `ValidationResult` y `ValidationSeverity` (sin estado 'PASS') para priorizar eventos de telemetría y degradación accionables.
* **Contratos:** Definición de `NodeValidator`, `ValidationEngine` y `NodeTextExtractor`, forzando la evaluación perezosa y la aplicación de la Ley de Postel (`Iterable` en entrada, `Iterator` en salida).

## HITO 2: Catálogo de Validadores y Zero-Mutation (Congelado)
Implementación de reglas de negocio aisladas sin acceso a reflexión dinámica ni serialización.
* **StructuralEquationValidator:** Algoritmo en $O(N)$ tiempo y $O(1)$ memoria que aplica validación *Fail-Fast* de sintaxis LaTeX (balanceo de llaves) sobre `ContentNodeType.DISPLAY_EQUATION`.
* **PassthroughIntegrityValidator:** Validador estratégico que verifica la existencia de anclajes espaciales (`bboxes`) para nodos estructurales, protegiendo al *Assembler*.
* **Zero-Serialization:** Sustitución de accesos directos al payload (`getattr`, `model_dump`) por inyección de un extractor tipado, preservando el encapsulamiento del AST.

## HITO 3: Motor Polimórfico y Composición (Congelado)
Despliegue del orquestador y el Factory del módulo.
* **PolymorphicValidationEngine:** Motor de Inversión de Control (IoC) inmutable. Itera el stream del AST y delega la validación de forma dinámica sin romper el *Back-Pressure*.
* **Composition Root (Factory):** Implementación de `build_validation_engine()` que ensambla las políticas de severidad y los extractores, exponiendo una API limpia al Orquestador global.

**Estado de la Fase 16.6:** 100% Congelada. Arquitectura de Grado Producción completada con ticket técnico registrado para la abstracción de payloads en futuras fases.