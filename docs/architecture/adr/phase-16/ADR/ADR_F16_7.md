# ADR_F16_7.md

# Architecture Decision Record: Fase 16.7 (Document Profiling & Characteristics)

## 1. Contexto y Problema
El pipeline opera mediante streaming de nodos individuales ($O(1)$). Sin embargo, políticas de fases avanzadas (ej. validación semántica, umbrales de partición) requieren contexto macro-estructural (saber si el documento es un *paper* a doble columna o un libro). Al no disponer de un mecanismo de inferencia anticipado, las fases posteriores operan a ciegas.

## 2. Decisión Arquitectónica
Se introduce el Bounded Context **`core/document_profile/`** con las siguientes directrices:
1. **Reutilización del Dominio Central:** Se prohíbe redefinir conceptos ya existentes en el *Aggregate Root*. Se reutilizarán `DocumentType` y `PageOrientation` desde `core.domain.documents`.
2. **Encapsulamiento del Input:** Se define `ProfileInput`, una ventana de observación finita, protegiendo el contrato contra el *Parameter Creep*.
3. **DTO de Inferencia Desacoplado:** El resultado se denominará `DocumentCharacteristics` para evitar colisión de lenguaje ubicuo con el `DocumentProfile` del *Aggregate Root*. Posteriormente, el Orquestador utilizará este DTO para enriquecer el perfil maestro del documento.
4. **Orquestación Dirigida (DAG):** Se implementa un `SequentialDocumentProfiler` que ejecuta los detectores físicos, recoge sus resultados, y los inyecta como contexto en los detectores semánticos.
5. **Segregación de Dominio y Observabilidad:** Las características inferidas (`DocumentCharacteristics`) se aíslan de las métricas de certidumbre (`ProfileDiagnostics`).

## 3. Modelos de Dominio y Diagnóstico (core/document_profile/models.py)

```python
from enum import StrEnum
from dataclasses import dataclass
from collections.abc import Sequence
from core.ast.models import ASTNode

# REUTILIZACIÓN SOTA: Importación directa del Aggregate Root
from core.domain.documents import DocumentType, PageOrientation

class PageLayout(StrEnum):
    SINGLE_COLUMN = "single_column"
    DOUBLE_COLUMN = "double_column"
    UNKNOWN = "unknown"

@dataclass(slots=True, frozen=True)
class ProfileInput:
    """DTO que encapsula la ventana de observación (Nodos de muestra)."""
    nodes: Sequence[ASTNode]
    sampled_pages: int
    provider_id: str | None = None

@dataclass(slots=True, frozen=True)
class LayoutDetection:
    layout: PageLayout
    confidence: float

@dataclass(slots=True, frozen=True)
class TypeDetection:
    document_type: DocumentType
    confidence: float

@dataclass(slots=True, frozen=True)
class DocumentCharacteristics:
    """
    SOTA: DTO inmutable resultante de la inferencia heurística.
    No colisiona con el Aggregate Root (DocumentProfile).
    """
    layout: PageLayout
    document_type: DocumentType

@dataclass(slots=True, frozen=True)
class ProfileDiagnostics:
    """SOTA: DTO de telemetría y observabilidad de la inferencia."""
    layout_confidence: float
    type_confidence: float
    sample_size: int
```

## 4. Interfaces y Contratos Hexagonales (core/document_profile/protocols.py)

```python
from typing import Protocol
from core.document_profile.models import (
    ProfileInput, 
    LayoutDetection, 
    TypeDetection, 
    DocumentCharacteristics, 
    ProfileDiagnostics
)

class LayoutDetector(Protocol):
    """Evalúa topología física consumiendo metadatos espaciales."""
    def detect(self, input_data: ProfileInput) -> LayoutDetection:
        ...

class DocumentTypeDetector(Protocol):
    """Evalúa taxonomía semántica consumiendo el layout resuelto."""
    def detect(self, input_data: ProfileInput, layout: LayoutDetection) -> TypeDetection:
        ...

class DocumentProfiler(Protocol):
    """
    Contrato del orquestador secuencial de perfilado.
    """
    def profile(self, input_data: ProfileInput) -> tuple[DocumentCharacteristics, ProfileDiagnostics]:
        ...
```

## 5. Invariantes del Dominio y Principios Arquitectónicos
1. **Zero Mutation Absoluto:** El proceso no altera los `ASTNode` de la muestra.
2. **Integración Externa:** El `SequentialDocumentProfiler` y sus detectores se instanciarán y ensamblarán exclusivamente en el *Composition Root* oficial del proyecto (`apps/bootstrap/pipeline_factory.py`).
3. **Aislamiento de Responsabilidades:** Los detectores físicos no conocen a los semánticos. El profiler traza el puente de dependencias explícitamente.

---

## HITOS DE IMPLEMENTACIÓN (FASE 16.7)

### Hito 1: Dominio, DTOs y Contratos
* Creación del Bounded Context `core/document_profile/`.
* Implementación de DTOs en `models.py` (`ProfileInput`, `DocumentCharacteristics`, `ProfileDiagnostics`), importando explícitamente `DocumentType` desde `core.domain.documents`.
* Definición de contratos hexagonales en `protocols.py` (Detectores y Profiler).

### Hito 2: Motores Detectores (Heurísticas Físicas y Semánticas)
* Creación de `core/document_profile/detectors/layout.py`. Implementación de `HeuristicLayoutDetector` evaluando `bboxes` para retornar un `LayoutDetection`.
* Creación de `core/document_profile/detectors/semantic.py`. Implementación de `HeuristicTypeDetector` cruzando la densidad del AST con el layout.

### Hito 3: Orquestador Secuencial e Integración (Composition Root)
* Creación de `core/document_profile/profiler.py`. Implementación del `SequentialDocumentProfiler` que coordina los detectores.
* Modificación de `apps/bootstrap/pipeline_factory.py` para instanciar el orquestador e inyectar el paso en el flujo global.
* **Ciclo de Cierre:** El Orquestador consumirá el `DocumentCharacteristics` resultante para actualizar el *Aggregate Root* (`DocumentLayout.profile`) antes de iniciar el streaming profundo.


TICKET: TCH-043 - Evolución Polimórfica de Detectores de Perfilado
SEVERIDAD: P3 (Arquitectura / Escalabilidad Futura)
DOMINIO: core/document_profile

ACCIÓN FUTURA: 
Para fases >16.7, refactorizar los detectores específicos (LayoutDetector, DocumentTypeDetector) hacia una interfaz genérica `ProfileDetector(Protocol)` operada por un Registry interno. Esto permitirá escalar hacia heurísticas ortogonales (LanguageDetector, FontDetector, PageSizeDetector) sin modificar el orquestador principal, replicando el patrón SOTA de `core/validation/ast/`. Se mantiene el DAG estático actual como MVP.


TICKET: TCH-044 - Segregación de Inferencia y Política de Clasificación
SEVERIDAD: P2 (Arquitectura Core)
DOMINIO: core/document_profile
ACCIÓN FUTURA: 
Refactorizar `HeuristicTypeDetector`. Actualmente mezcla la extracción de evidencia (ratios) con la política de puntuación (pesos). Evolucionar hacia un modelo donde los detectores actúen como `EvidenceContributor` (retornando objetos de evidencia puros) y un `ClassificationPolicy` centralizado asigne los pesos para determinar el `DocumentType`.

TICKET: TCH-045 - Evolución de Proyección Geométrica
SEVERIDAD: P3 (Extensibilidad)
DOMINIO: core/document_profile
ACCIÓN FUTURA: 
Evolucionar `NodeGeometry` hacia un Value Object más rico (`GeometryProjection`) que contenga `center_x`, `center_y`, `bbox`, `page`, etc., acompañado de un `PageGeometryProvider` para evitar la redundancia de datos de página (ej. `page_width`) a nivel de nodo individual.


# RESULTADOS CONSOLIDADOS FASE 16.7: DOCUMENT PROFILE

## HITO 1: Bounded Context y Contratos (Congelado)
Se estableció el subdominio puro `core/document_profile/` para segregar físicamente la inferencia estructural y semántica de las capas de persistencia y orquestación del pipeline global.
* **Modelos de Dominio:** Implementación inmutable de `InferredDocumentProfile` y `ProfileDiagnostics`, encapsulando las variables topológicas (esquema de columnas) y taxonómicas (libro, informe, paper) sin estados intermedios inválidos.
* **Contratos:** Definición de los puertos abstractos `LayoutDetector`, `DocumentTypeDetector` y `ProfileStore`, forzando la inversión de dependencias y desacoplando el subdominio de herramientas concretas de renderizado o bases de datos físicas.

## HITO 2: Motor Heurístico y Detectores Puros (Congelado)
Implementación de los servicios de dominio puros encargados de ejecutar el DAG de inferencia estructural.
* **HeuristicDocumentProfiler:** Encapsula la lógica de orquestación interna aislando el ensamblado de DTOs en el método privado `_build_result`, previniendo deuda técnica ante futuras expansiones del clasificador.
* **Detectores Puros:** Algoritmos basados en análisis de varianza posicional (`center_x`) y densidad semántica de nodos, descartando sobreingeniería de modelos pesados de Machine Learning para mantener la latencia en mínimos tolerables.
* **Zero-Hack Conformity:** Eliminación de aserciones estructurales artificiales (`_ : Protocol = ...`), delegando la verificación de cumplimiento de contratos de forma nativa a la validación estricta de tipos de Pylance en el Composition Root.

## HITO 3A: Ensamblaje Hexagonal y Composición (Congelado)
Despliegue del cableado de dependencias e inyección limpia sobre los componentes existentes.
* **Ownership de Infraestructura:** Traslado de las clases concretas `NodeGeometryAdapter` y `NodeSemanticAdapter` al bounded context de infraestructura (`infra/adapters/`), blindando al dominio de mutaciones en los esquemas lógicos o metadatos de PDFium/PyMuPDF.
* **DDD Aggregate Root Expansion:** Inyección del método `with_profile()` dentro de `DocumentLayout`, delegando la consistencia e invariantes estructurales al propio Aggregate mediante copias inmutables, en lugar de mutar propiedades de forma laxa en la capa de aplicación (Router).
* **Anti-Corruption Layer en Factory:** Refactorización de `build_pipeline()` en `pipeline_factory.py` para aplanar colecciones paginadas jerárquicas hacia estructuras planas (`LayoutBlockCollection`) requeridas por el compilador del AST, resolviendo problemas de contravarianza.

## HITO 3B: Bounded Workload y Persistencia CQRS (Congelado)
Resolución de fronteras asincrónicas y blindaje de rendimiento ante documentos masivos.
* **FirstPagesSamplingPolicy:** Implementación de una política de muestreo topológico configurable basada en ventanas de páginas físicas útiles en lugar de un número rígido de nodos, garantizando una carga de trabajo acotada (*Bounded Workload*) en la CPU del demonio.
* **ProfileStore (Abstracción Temporal):** Creación del puerto e implementación `InMemoryProfileStore` en la capa de infraestructura para actuar como puente de intercambio efímero, permitiendo que el perfil inferido sobreviva de manera segura a la frontera asincrónica (CQRS) que separa al Router del Assembler final.
* **Pydantic Strict Refactor:** Reescritura del motor de segmentación en `parser.py` para erradicar diccionarios implícitos y strings crudos, forzando la instanciación estricta de las uniones polimórficas del payload (`ParagraphPayload`, `ImagePayload`) y metadatos estructurados (`NodeMetadata`).

**Estado de la Fase 16.7:** Baseline cerrado para esta iteración. Arquitectura de Grado Producción completada de extremo a extremo, validada bajo tipado estricto y preparada para evolución adaptativa sin introducir acoplamientos cruzados.