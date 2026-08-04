# ADR_F16_3.md

# Architecture Decision Record: Fase 16.3 (Segmenter V2)

## 1. Contexto y Problema
El sistema actual asume cortes de texto crudo basados en `splitlines()` o expresiones regulares ingenuas. Esto destruye la integridad de los bloques semánticos (partiendo ecuaciones o rompiendo jerarquías) y pierde la trazabilidad de las coordenadas físicas (`NodeMetadata`) requerida para la compilación final. Se requiere un mecanismo de segmentación escalable que aumente la resolución oracional de los párrafos (1 a N) sin afectar los nodos atómicos (1 a 1), operando sobre el `ASTNode` inmutable de la Fase 16.2.

## 2. Decisión Arquitectónica
Se adopta un diseño de **Puertos y Adaptadores (Hexagonal)** impulsado por Interfaces (`typing.Protocol`) y un **Registro de Enrutamiento (Dispatcher)**. Se elimina cualquier acoplamiento con librerías NLP pesadas en el core, delegando la desambiguación a una política científica basada en heurísticas estáticas.

## 3. Interfaces y Contratos
El diseño se basa en dos contratos estrictos:

```python
class BoundaryPolicy(Protocol):
    def find_boundaries(self, text: str) -> List[str]:
        """Detecta fronteras oracionales preservando terminología STEM."""
        ...

class NodeSegmenter(Protocol):
    def segment(self, node: ASTNode) -> Iterable[ASTNode]:
        """Transforma un nodo en N fragmentos inmutables propagando linaje."""
        ...
```
## 4. Resultados

# DOCUMENTACIÓN DE ARQUITECTURA: FASE 16.3 (SEGMENTER V2)

---

## HITO 1 (CONGELADO)

### Objetivo
Definir los contratos formales del dominio de segmentación antes de introducir cualquier lógica de procesamiento o fragmentación textual.

### Decisiones Arquitectónicas

#### 1. Evolución del AST
Se incorporan los atributos de trazabilidad lógica directamente en la raíz de `ASTNode`:
* `parent_node_id: Optional[str] = None`
* `segment_index: int = 0`

Estos atributos representan exclusivamente el linaje de transformación y no forman parte del origen físico del documento. Se mantiene una separación estricta de responsabilidades:
* **`NodeMetadata`:** Información física unidimensional proveniente exclusivamente del extractor.
* **`ASTNode`:** Identidad, topología y evolución lógica dentro del pipeline.

> Se descarta definitivamente la utilización del diccionario `control_plane` para transportar información estructurada de segmentación.

#### 2. Eliminación de `segment_count`
Se rechaza la incorporación de un contador estático en los nodos. La cardinalidad de una segmentación podrá inferirse de forma dinámica agrupando por `parent_node_id` y ordenando por `segment_index`. Esta decisión evita la duplicación de estado y elimina el riesgo de desincronización de datos durante las fases posteriores (`Chunking`, `Validation`).

#### 3. Contratos Hexagonales
Los contratos del dominio de segmentación se ubican estrictamente en el nuevo subdominio dedicado:
`core/segmenter/protocols.py`

El núcleo del AST (`core/ast`) no conoce los contratos de sus servicios de aplicación, evitando dependencias conceptuales inversas.

#### 4. `SegmentContext`
Se adopta un *Parameter Object* inmutable implementado mediante una estructura ligera de alto rendimiento:
`@dataclass(frozen=True, slots=True)`

Sustituye a `BaseModel` de Pydantic para eliminar el overhead de validación dinámica en bucles críticos. Su finalidad es estabilizar las firmas públicas de los protocolos frente a futuras ampliaciones (`DocumentProfile`, idioma, límites de tokens).

#### 5. Protocolos Puros
Se congelan dos puertos del dominio completamente *stateless*:
* `BoundaryPolicy` (Puerto de Detección Matemática)
* `NodeSegmenter` (Puerto de Transformación Estructural)

#### 6. Contrato Matemático de `BoundaryPolicy`
La política retorna exclusivamente una `tuple[int, ...]` que representa los offsets absolutos de cierre oracional dentro del texto. No retorna subcadenas ni realiza asignaciones de memoria dinámicas innecesarias.

| Invariantes del Hito 1 |
| :--- |
| AST completamente inmutable mediante transiciones de estado. |
| Cero mutaciones sobre la instancia original de `NodeMetadata`. |
| Ausencia de información redundante o contadores estáticos en el DTO. |
| Protocolos desacoplados bajo Arquitectura Hexagonal. |
| Firmas estables protegidas mediante objetos paramétricos. |
| Complejidad asintótica acotada en tiempo lineal $O(n)$. |

**Estado:** Congelado y validado por el linter estático.

---

## HITO 2 (CONGELADO)

### Objetivo
Implementar el motor de detección de fronteras oracionales para documentos científico-técnicos (STEM) operando bajo un enfoque determinista libre de dependencias ML o NLP pesadas.

### Decisiones Arquitectónicas

#### 1. Scanner Nativo Acelerado
Se adopta el uso exclusivo de `re.finditer(r'[\.\?\!]+', text)` ejecutado a nivel de capa nativa en C como un escáner de candidatos ultrarrápido. El motor de expresiones regulares no toma decisiones lingüísticas ni maneja excepciones; solo actúa como un acelerador del recorrido lineal.

#### 2. Arquitectura de Reglas (Rule Engine)
La validación de candidatos abandona el enfoque de expresiones regulares monolíticas con lookbehinds fijos. El flujo se desacopla en un pipeline composicional de predicados funcionales:

`Scanner (C-Level) ➔ BoundaryCandidate (DTO) ➔ Rule Pipeline (Short-Circuit) ➔ Offsets`

#### 3. `BoundaryCandidate`
Se introduce un objeto paramétrico inmutable de asignación barata:
`@dataclass(frozen=True, slots=True)`

Encapsula el texto completo, el índice de inicio/fin del match, la longitud total y el contexto de ejecución, estabilizando la API de las reglas frente a expansiones futuras.

#### 4. `ScientificLexicon`
Las excepciones léxicas y tokens protegidos se concentran en una estructura de datos inmutable de tiempo constante:
`frozenset`

Permite realizar búsquedas en $O(1)$ y evolucionar el glosario académico sin modificar la complejidad ciclomática del motor.

#### 5. Predicados Funcionales Puros
Cada criterio de descarte se implementa como un método estático puro (`BoundaryRule`):
* `_rule_is_decimal_or_version`: Evita cortes en números flotantes (`3.14`) o identificadores de software (`v1.4.2`).
* `_rule_is_protected_lexicon`: Protege abreviaturas e identificadores STEM (`Fig.`, `Eq.`, `et al.`).
* `_rule_invalid_continuation`: Valida si el siguiente token no vacío inicia una oración real (Mayúsculas, dígitos o brackets de citas `[`, `(`, `{`).

#### 6. Registro de Reglas de Extensión Cerrada (OCP)
La política mantiene una secuencia inmutable de evaluación perezosa (*short-circuit evaluation*):
`_RULES: Final[Tuple[BoundaryRule, ...]]`

El motor de control orquesta las reglas mediante la directiva `if any(rule(candidate) for rule in self._RULES)`. Añadir soporte para nuevas estructuras estructurales no altera el método principal de búsqueda.

#### 7. Escáner Inverso Léxico Local
La extracción de la palabra previa a la puntuación terminal abandona la dependencia del espacio en blanco. Se implementa un recorrido inverso local de punteros que procesa correctamente adjunciones físicas del layout como:
* `Eq.(7)`
* `Fig.[3]`
* `Dr.\nSmith` (Saltos de línea intermedios)

#### 8. Adopción del Modelo A de Offsets
El motor retorna tuplas de cierre indexable (e.g., `(45, 100)`). Esto se traduce matemáticamente en intervalos contiguos limpios:
* Oración 1: `text[0:45]`
* Oración 2: `text[45:100]`

Evita la redundancia de guardar el origen `0` explícitamente en la secuencia.

### Invariantes del Hito 2
* **Aislamiento Operativo:** Cero dependencias de spaCy, NLTK, Stanza o HuggingFace.
* **Evaluación Perezosa:** Las reglas se disparan únicamente cuando el escáner nativo detecta un caracter candidato `.`, `?`, `!`.
* **Zero Allocations de Texto:** No se realizan copias, rebanados (*slices*) ni instanciaciones de substrings grandes durante la fase de desambiguación.

### Matriz de Responsabilidades del Componente

| El componente SÍ realiza: | El componente NO realiza: |
| :--- | :--- |
| Detectar índices de fronteras oracionales lógicas. | Segmentar o fragmentar físicamente estructuras del AST. |
| Filtrar falsos positivos basados en el contexto léxico STEM. | Instanciar nuevos `ASTNode` o payload clones. |
| Retornar tuplas matemáticas inmutables de offsets. | Modificar coordenadas espaciales o mutar metadatos. |

**Estado:** Hito 2 Congelado y listo para producción.


## HITO 3 (CONGELADO)

### Objetivo
Diseñar e implementar los transformadores polimórficos y el enrutador central de la segmentación, garantizando un flujo de memoria plano (*streaming*), identidades opacas seguras y un aislamiento estricto de la infraestructura subyacente.

### Decisiones Arquitectónicas

#### 1. Identidades Opacas y Puerto Hexagonal
Se erradica la concatenación de *Smart IDs* (e.g., `nodo_seg_1`). La generación de identidades se delega a un puerto formal:
`NodeIdentityGenerator`
La trazabilidad semántica viaja exclusivamente a través del linaje formal del DTO (`parent_node_id`, `segment_index`), garantizando que la identidad sea un valor opaco para el resto del pipeline.

#### 2. Ocultamiento de Información (Information Hiding)
El Segmenter pierde conocimiento absoluto de la API del DTO (Pydantic). Se inyecta el método `spawn_fragment` dentro de `ASTNode` para que el modelo de dominio sea el único responsable de su propia clonación y transición de estado estructural.

#### 3. Transformación Lazy (Generadores)
El `ParagraphSegmenter` implementa su método `segment` retornando un `Iterable[ASTNode]` mediante `yield`. Esto asegura que el consumo de memoria se mantenga en $O(1)$ por bloque, evitando materializar listas intermedias masivas en memoria durante la amplificación de nodos (1 a N).

#### 4. Tipado Estructural Temporal (Protocol TextPayload)
Ante la necesidad de garantizar operaciones textuales seguras sin refactorizar el `ASTNode` en una unión nominal completa (AST V3), se adopta el uso de un `Protocol` (`TextPayload`) y un `cast` estructural.
> *Technical Debt Registrada:* Esta decisión se documenta como un compromiso temporal aceptado para mantener la compatibilidad con el Hito 16.2.

#### 5. Dispatcher Basado en Entidad (No en Enum)
El `SegmentDispatcher` modifica su firma para recibir la entidad completa (`dispatch(node: ASTNode)`). Esto blinda el contrato público para permitir que, en fases futuras, el enrutamiento dependa de propiedades dinámicas del nodo (longitud, nivel de confianza, idioma) sin alterar la interfaz.

#### 6. Tabla de Enrutamiento Inmutable y DI
El Dispatcher se vuelve un componente 100% declarativo y tonto. No instancia estrategias. Recibe el registro de enrutamiento inyectado en su constructor envuelto en un `MappingProxyType` para garantizar su inmutabilidad en tiempo de ejecución.

### Invariantes del Hito 3
* Todo segmentador atómico debe generar `yield node` intacto (1 a 1).
* La identidad generada para nuevos fragmentos no debe contener meta-semántica lógica.
* El enrutador de estrategias debe caer siempre en un fallback conservador (`AtomicSegmenter`) ante tipos de nodos desconocidos.

**Estado:** Congelado y validado.

---

## HITO 4 (CONGELADO)

### Objetivo
Desplegar la Capa de Aplicación (*Application Service*), ensamblar el caso de uso del segmentador y suturar la continuidad topológica del AST procesado.

### Decisiones Arquitectónicas

#### 1. Orquestación del Caso de Uso (SegmenterService)
Se crea el servicio de aplicación `SegmenterService` como dueño exclusivo del flujo. Su responsabilidad es:
* Iterar el AST entrante.
* Consultar el `Dispatcher`.
* Consumir el generador resultante.
* Delegar la reparación al normalizador.

La firma principal se denomina `segment_ast(nodes: Iterable[ASTNode])` para alinearse con la semántica pura del dominio lógico en lugar del origen físico.

#### 2. ASTSequenceNormalizer Funcional y Lazy
El reparador de secuencias se rediseña como un transformador *lazy*:
`yield node.with_sequence_id(idx + 1)`
El pipeline mantiene así su naturaleza de transmisión continua de extremo a extremo, delegando la materialización en memoria únicamente al llamador final. Al igual que en la clonación, se inyecta `with_sequence_id` en el dominio para ocultar la mutación de Pydantic.

#### 3. Manejo de Excepciones de Dominio (SRE Guardrails)
El bloque de captura global rechaza el enmascaramiento broad-catch (`except Exception`). Se introduce una excepción de dominio específica (`SegmenterError`). Las fallas operativas asiladas se capturan para emitir el nodo intacto como mecanismo de resiliencia (Fallback), mientras que las interrupciones del sistema o errores de código se dejan propagar libremente.

#### 4. Logging Estructurado
Se abandona la interpolación de *strings* opacos para el registro de eventos. El Application Service implementa telemetría estructurada `logger.info("Segmentation completed", extra={"event": "SEG-003", ...})`, preparándose para ser consumida e indexada eficientemente por herramientas de observabilidad modernas (Datadog, ELK).

#### 5. Purificación del Bounded Context (Expulsión de Bootstrap y Adapters)
Se respeta la jerarquía estricta de la Arquitectura Hexagonal reubicando los componentes de infraestructura y composición fuera del dominio lógico:
* `UUIDIdentityGenerator` es desplazado al directorio de infraestructura (`adapters/identity/`).
* `SegmenterBootstrap` (DI Container) es movido al nivel de orquestación de la aplicación (`composition/` o `bootstrap/`).

El módulo `core/segmenter` queda exclusivamente reservado para interfaces, políticas matemáticas y casos de uso puros.

### Invariantes del Hito 4
* El servicio de aplicación no contiene lógica de dominio, solo orquesta.
* El pipeline opera en streaming (laziness) sin arrays intermedios de acumulación.
* Las dependencias físicas y concretas se resuelven en la capa externa de la aplicación.

**Estado:** Congelado. Fase 16.3 completada exitosamente.