# HITO_{ID}_PRODUCTION_PIPELINE_EXECUTION_ATLAS.md

## Production Pipeline Execution Atlas
### Reconstrucción AS-IS, viabilidad de componentes y reconciliación del motor PDF → PDF

**Versión:** 0.1.0  
**Estado:** IN_PROGRESS — investigación forense  
**Fecha de apertura:** 2026-10-14  
**Unidad:** Pipeline Stabilization & Architectural Reconciliation  
**Autoridad:** Architecture Board  
**Ubicación:** `docs/architecture/adr/pipeline-stabilization/00-foundation/`  
**Identificador HITO:** pendiente de asignación conforme a la unidad aprobada  
**Baseline de investigación:** commit `95ef8a38614a1416484593fbd734443e57a74369`  
**Charter de referencia:** `PIPELINE_STABILIZATION_AUDIT_CHARTER.md`  
**Naturaleza:** evidencia forense AS-IS, no especificación TO-BE, ADR, NADR ni Execution Plan.

### Changelog

| Versión | Fecha | Descripción |
|---|---|---|
| 0.1.0 | 2026-10-14 | Creación del esqueleto del Atlas. Pendiente de investigación y consolidación de evidencias. |

---

# 0. PROTOCOLO DE LECTURA Y ESTADO DE INVESTIGACIÓN

## 0.1 Finalidad

El objetivo de este documento es reconstruir el pipeline productivo real del repositorio, evaluar la viabilidad de sus componentes e identificar las desconexiones, duplicaciones y contradicciones que impiden disponer de una ruta PDF → PDF integrada.

No pretende documentar exhaustivamente cada clase del repositorio, completar el benchmark ni reproducir las auditorías P1–P7 realizadas durante F17-BIS.

## 0.2 Separación de hechos y decisiones

- **OBSERVED:** comportamiento, conexión o implementación constatada mediante evidencia.
- **REQUIRED:** obligación derivada de contratos normativos vigentes, citados expresamente.
- **UNKNOWN:** información todavía no acreditada.
- **DECISION REQUIRED:** cuestión que deberá resolver la autoridad arquitectónica después de la investigación.

Las propuestas de conservación, integración, consolidación y retiro son candidaturas forenses, no autorizaciones para modificar código.

Los estados probatorios y los identificadores formales deberán ajustarse a `1.2_METH_FOR_FORENSIC_HITOs.md`.

## 0.3 Reglas de investigación

1. Analizar el código correspondiente al commit de baseline.
2. No equiparar existencia de archivo, importación o instanciación con ejecución productiva demostrada.
3. Separar inspección estática de reproducción dinámica.
4. Referenciar evidencias por commit, archivo, símbolo y línea.
5. Reutilizar los HITOs y GAPs existentes; registrar únicamente el delta observado.
6. No declarar código muerto sin investigar consumidores dinámicos, ejecución y obligaciones normativas.
7. No incorporar decisiones TO-BE como hechos del AS-IS.
8. Mantener el benchmark fuera del alcance principal, salvo interferencia productiva.

## 0.4 Progreso

| Bloque | Estado | Evidencia |
|---|---|---|
| Producto y frontera | PENDIENTE | — |
| Rutas productivas existentes | PENDIENTE | — |
| Capacidades indispensables | PENDIENTE | — |
| Conectividad y datos | PENDIENTE | — |
| Viabilidad de componentes | PENDIENTE | — |
| Duplicaciones y causas estructurales | PENDIENTE | — |
| Verificación E2E | PENDIENTE | — |
| Consolidación forense | PENDIENTE | — |

---

# 1. PRODUCT EXECUTION BOUNDARY

## 1.1 Qué constituye el producto

**Entrada:** PDF científico.

**Transformación esperada:** extracción, interpretación estructural, traducción de contenido elegible, preservación científica y reconstrucción documental.

**Salida:** PDF traducido, íntegro y localizable mediante el contrato de entrega correspondiente.

## 1.2 Capacidades necesarias

Registrar las capacidades imprescindibles independientemente de los archivos que actualmente las implementan.

| ID | Capacidad | Necesaria para PDF → PDF | Contrato normativo | Estado AS-IS |
|---|---|---|---|---|
| CAP-01 | Admisión e identidad documental | Sí | Por verificar | UNKNOWN |
| CAP-02 | Extracción PDF / OCR | Sí | Por verificar | UNKNOWN |
| CAP-03 | Construcción y normalización AST | Sí | Por verificar | UNKNOWN |
| CAP-04 | Segmentación, routing y chunking | Sí | Por verificar | UNKNOWN |
| CAP-05 | Planificación y ejecución de tareas | Sí | Por verificar | UNKNOWN |
| CAP-06 | Inferencia LLM | Sí | Por verificar | UNKNOWN |
| CAP-07 | Validación, healing y preservación | Sí | Por verificar | UNKNOWN |
| CAP-08 | Persistencia y materialización | Según contrato de ejecución | Por verificar | UNKNOWN |
| CAP-09 | Reconstrucción y ensamblado | Sí | Por verificar | UNKNOWN |
| CAP-10 | Renderizado y compilación PDF | Sí | Por verificar | UNKNOWN |
| CAP-11 | FSM, autoridad y recuperación | Según contratos vigentes | Por verificar | UNKNOWN |
| CAP-12 | Entrega del artefacto y estado final | Sí | Por verificar | UNKNOWN |

## 1.3 Exclusiones

Benchmark científico, recalibración de corpus, nuevas capacidades F19–F21, infraestructura distribuida no exigida y mejoras de rendimiento no bloqueantes.

## 1.4 Condición funcional mínima

Registrar aquí el criterio de aceptación PDF → PDF previamente aprobado en el Charter, sin modificarlo después de conocer los resultados.

---

# 2. PRODUCTION ENTRY POINTS & COMPETING EXECUTION ROUTES

## 2.1 Descubrimiento de puntos de entrada

Investigar todos los mecanismos que pueden iniciar o continuar una ejecución productiva: comandos CLI, módulos `__main__`, Docker Compose, scripts, workers y triggers persistentes.

| Ruta | Entry point candidato | Mecanismo de arranque | ¿Se despliega? | ¿Ejecuta trabajo? | ¿Produce PDF? |
|---|---|---|---|---|---|
| R-CLI | `apps/cli/main.py` | CLI | Por verificar | Por verificar | Por verificar |
| R-ENGINE | `runtime/engine.py` | Compose / runtime | Por verificar | Por verificar | Por verificar |
| R-LLM | `apps/llm_workers/__main__.py` | Worker daemon | Por verificar | Por verificar | Por verificar |
| R-OCR | `apps/ocr_router/__main__.py` | Router daemon | Por verificar | Por verificar | Por verificar |
| R-ASM | `apps/compiler/__main__.py` | Assembler daemon | Por verificar | Por verificar | Por verificar |
| R-OTHER | Otros identificados | Por verificar | Por verificar | Por verificar | Por verificar |

Los identificadores R-* son etiquetas locales de análisis y no reemplazan identificadores normativos.

## 2.2 Grafo AS-IS de rutas competidoras

**[INSERTAR DIAGRAMA MERMAID VERIFICADO]**

Distinguir visualmente:

- Ejecución configurada y alcanzable.
- Ejecución demostrada.
- Dependencia estática sin invocación acreditada.
- Conexión incompatible o bloqueada.
- Ruta histórica o experimental.

## 2.3 Composición e infraestructura por ruta

Para cada ruta registrar:

- Composition root y factorías utilizadas.
- Objetos construidos y adaptadores inyectados.
- Contexto de proceso: host, contenedor o daemon.
- Repositorios, bases de datos y paths utilizados.
- Configuración y variables de entorno determinantes.
- Primer punto de falla o pérdida de continuidad demostrado.
- Último resultado observable.

## 2.4 Matriz comparativa de rutas

| Dimensión | CLI | Engine | LLM daemon | Observación |
|---|---|---|---|---|
| Identidad documental | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Extracción / AST | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Contexto de inferencia | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Validación / healing | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Persistencia | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Control FSM | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Leases / autoridad | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Ensamblado PDF | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Recuperación | UNKNOWN | UNKNOWN | UNKNOWN | — |

## 2.5 Hallazgos de divergencia entre rutas

**[COMPLETAR CON EVIDENCIAS, SIN ELEGIR TODAVÍA LA RUTA DEFINITIVA]**

---

# 3. CANONICAL CAPABILITY SKELETON

Esta sección describe las capacidades que debe cumplir el producto, sin presentar ninguna implementación actual como autoritativa antes de demostrarlo.

## 3.1 Mapa funcional de alto nivel

**[INSERTAR MERMAID: PDF → EXTRACCIÓN → AST → SEGMENTACIÓN → EJECUCIÓN → VALIDACIÓN → ENSAMBLADO → PDF]**

Representar FSM, journal, persistencia y recovery como preocupaciones transversales donde corresponda.

## 3.2 Tabla de capacidades e implementaciones candidatas

| Capacidad | Implementación candidata | Implementaciones alternativas | Conectividad | Cobertura funcional |
|---|---|---|---|---|
| Ingesta / OCR | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| AST | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Segmentación | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Routing / chunking | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Inferencia | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Validación / healing | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Persistencia | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Compilación PDF | Por investigar | Por investigar | UNKNOWN | UNKNOWN |
| Recuperación | Por investigar | Por investigar | UNKNOWN | UNKNOWN |

## 3.3 Capacidades sin implementación acreditada

**[POR INVESTIGAR]**

## 3.4 Implementaciones sin capacidad productiva justificada

**[POR INVESTIGAR]**

---

# 4. EXECUTION CONNECTIVITY & DATA LINEAGE

## 4.1 Mapa de conexiones efectivas

Registrar las conexiones necesarias para que el producto avance de una etapa a otra.

| Enlace | Origen | Destino | Datos intercambiados | Estado | Evidencia |
|---|---|---|---|---|---|
| L-01 | Entrada | Extracción | PDF / identidad | UNKNOWN | — |
| L-02 | Extracción | AST | Layout / nodos | UNKNOWN | — |
| L-03 | AST | Segmentación | Nodos estructurados | UNKNOWN | — |
| L-04 | Segmentación | Planificación | Unidades / chunks | UNKNOWN | — |
| L-05 | Planificación | Ejecutor | Tarea / autoridad | UNKNOWN | — |
| L-06 | Ejecutor | Persistencia | Resultado / evidencia | UNKNOWN | — |
| L-07 | Persistencia | Assembler | AST / resultados / perfil | UNKNOWN | — |
| L-08 | Assembler | Compilador | Documento reconstruido / TeX | UNKNOWN | — |
| L-09 | Compilador | Entrega | PDF / estado final | UNKNOWN | — |

## 4.2 Contratos de identidad

Investigar creación, transformación, persistencia y consumo de:

- `document_id`
- `job_id`
- `ast_hash`
- `node_id`
- `chunk_id`
- `task_id`
- `execution_id`
- Versiones, generaciones e intentos asociados.

**[INSERTAR MAPA DE LINAJE]**

## 4.3 Fronteras críticas entre procesos

Registrar especialmente si cada proceso puede reconstruir desde almacenamiento autorizado la información producida por otro proceso.

**[INSERTAR MATRIZ DE FRONTERAS, FORMATOS Y ALMACENAMIENTO]**

## 4.4 Primer punto de ruptura por ruta

| Ruta | Última etapa demostrada | Primera ruptura | Efecto downstream | Evidencia |
|---|---|---|---|---|
| CLI | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Engine | UNKNOWN | UNKNOWN | UNKNOWN | — |
| Daemons | UNKNOWN | UNKNOWN | UNKNOWN | — |

## 4.5 Fallos ocultos detrás de una primera ruptura

Una ruta que falla en planificación puede contener también defectos no observados en validación o ensamblado. Registrar esos tramos como no verificados, sin inferir que funcionan.

---

# 5. COMPONENT ROLE, CRITICALITY & VIABILITY MATRIX

## 5.1 Finalidad

Determinar qué implementaciones existentes resultan útiles, necesarias, redundantes, incompatibles o prescindibles para la construcción de un pipeline productivo PDF → PDF integrado, verificable y mantenible.

Esta sección clasifica los archivos relevantes del repositorio según cuatro dimensiones independientes:

1. **Rol arquitectónico:** qué responsabilidad cumple el componente.
2. **Criticidad productiva:** qué consecuencias tendría su ausencia o fallo para una capacidad requerida.
3. **Estado de integración:** qué evidencia existe de su participación efectiva en las rutas de ejecución.
4. **Participación por ruta:** en qué caminos de ejecución interviene y bajo qué condiciones.

A partir de estas dimensiones se determina la **viabilidad arquitectónica** de cada implementación y su posible disposición futura: conservación, integración, corrección, consolidación o evaluación para retiro.

La unidad principal de clasificación será el archivo o módulo Python. Cuando un archivo concentre responsabilidades sustancialmente diferentes, se analizarán además sus clases o funciones relevantes para evitar clasificaciones engañosas.

El objetivo no es inventariar indiscriminadamente todos los archivos del repositorio, sino identificar aquellos que intervienen en la ejecución productiva, implementan capacidades necesarias actualmente desconectadas o presentan posibles duplicaciones y contradicciones arquitectónicas.

Las clasificaciones son conclusiones de investigación sujetas a evidencia. Este HITO no autoriza modificaciones ni decisiones definitivas de arquitectura.

---

## 5.2 Criterios de evaluación

Para cada componente se investigarán los siguientes aspectos:

1. **Responsabilidad real:** qué función cumple efectivamente, independientemente de su nombre, ubicación o documentación histórica.
2. **Capacidad productiva:** qué necesidad del pipeline PDF → PDF satisface.
3. **Consumidor efectivo:** qué componente lo invoca, mediante qué interfaz y desde qué ruta de ejecución.
4. **Compatibilidad contractual:** qué contratos normativos y técnicos le resultan aplicables y si su implementación los satisface.
5. **Evidencia funcional:** qué comportamiento correcto ha sido demostrado mediante inspección o ejecución.
6. **Alternativas y duplicaciones:** qué otras implementaciones desempeñan responsabilidades equivalentes o parcialmente superpuestas.
7. **Dependencias introducidas:** qué servicios, adaptadores, almacenamiento, recursos y configuraciones necesita.
8. **Riesgo de conservación, modificación o retiro:** qué capacidades, invariantes o consumidores podrían verse afectados.
9. **Participación real por ruta:** si forma parte de la CLI, engine, daemons u otros caminos relevantes.
10. **Importancia productiva:** si es indispensable, obligatorio por contrato, condicional o ajeno al alcance productivo.

No se inferirá funcionamiento correcto únicamente porque una clase exista, sea importada, tenga tests unitarios aprobados o aparezca en un grafo histórico.

Tampoco se inferirá que un componente es código muerto por la sola ausencia de referencias textuales o importaciones estáticas.

---

## 5.3 Clasificación por rol arquitectónico

La clasificación por rol describe la responsabilidad principal de cada componente, no su importancia relativa.

| Código | Rol arquitectónico | Responsabilidad | Ejemplo candidato |
|---|---|---|---|
| R1 | Entry Point | Recibir solicitudes, comandos o eventos que inician un proceso de ejecución | `apps/cli/main.py` |
| R2 | Composition Root | Construir e inyectar implementaciones concretas y ensamblar dependencias | `apps/bootstrap/pipeline_factory.py` |
| R3 | Orchestrator / Coordinator | Coordinar etapas, secuencias, transiciones y resultados de trabajo | `core/pipeline/orchestrator.py` |
| R4 | Capability Service | Implementar una capacidad funcional delimitada del pipeline | `core/segmenter/service.py` |
| R5 | Algorithm / Policy | Ejecutar reglas, estrategias, cálculos o transformaciones especializadas | `core/chunking/policies.py` |
| R6 | Infrastructure Adapter | Integrar servicios externos, almacenamiento, sistema de archivos o herramientas físicas | `infra/db/control_repo.py` |
| R7 | Contract / Model | Definir entidades, puertos, DTOs, identidades e invariantes compartidos | `core/execution/ports.py` |

**Reglas de clasificación:**

- Cada componente tendrá un rol arquitectónico primario.
- Se podrán registrar roles secundarios cuando existan responsabilidades adicionales demostradas.
- Si un archivo concentra varias responsabilidades relevantes, se indicará explícitamente en lugar de forzar una clasificación única engañosa.
- La pertenencia a un directorio no determina automáticamente su rol.
- Un R1 no es necesariamente más importante que un R5 o un R7.
- La mezcla injustificada de responsabilidades podrá registrarse como observación arquitectónica, sustentada en evidencia.

Las clasificaciones mostradas como ejemplos deberán confirmarse durante la investigación del código.

---

## 5.4 Clasificación por criticidad productiva

La criticidad mide el impacto que tendría la ausencia, indisponibilidad o comportamiento incorrecto de una capacidad para el escenario productivo y los contratos aplicables.

| Nivel | Denominación | Criterio |
|---|---|---|
| C0 | Critical Path Blocker | El fallo o ausencia de la capacidad impide completar el recorrido productivo PDF → PDF del escenario evaluado |
| C1 | Mandatory Production Guarantee | La capacidad es necesaria para cumplir un contrato productivo obligatorio, aunque su ausencia no impida necesariamente generar un archivo PDF |
| C2 | Conditional / Replaceable Capability | La implementación es necesaria solo bajo determinadas condiciones o puede ser sustituida por otra implementación conforme |
| C3 | Non-Product Scope | La implementación no resulta necesaria para el alcance productivo investigado |

**Reglas de aplicación:**

1. La criticidad debe fundamentarse en una capacidad requerida, un escenario de ejecución o un contrato vigente.
2. La criticidad no equivale a cantidad de código, complejidad, número de importadores o posición en el grafo.
3. Debe distinguirse la **criticidad de la capacidad** de la **indispensabilidad de una implementación concreta**: una función puede ser C0 aunque existan dos adaptadores capaces de proporcionarla.
4. Cuando un componente satisfaga obligaciones de varios niveles, se registrará el nivel más exigente aplicable, indicando el fundamento.
5. C3 no significa código muerto, defectuoso ni autorizado para eliminación.
6. Los niveles C0–C3 no sustituyen la escala de severidad P0–P2 utilizada para hallazgos forenses.
7. Cuando no exista información suficiente, la criticidad permanecerá como `UNKNOWN`.

---

## 5.5 Clasificación por estado de integración

El estado de integración describe qué se ha demostrado sobre la participación de un componente en las rutas productivas investigadas.

| Estado | Definición |
|---|---|
| EXECUTED | Existe evidencia dinámica de que el componente fue invocado en el escenario auditado |
| REACHABLE | Se acreditó una cadena estática de invocación desde un entry point, pero no su ejecución dinámica |
| BROKEN | Se acreditó un defecto o incompatibilidad de integración en la conexión investigada |
| DISCONNECTED | Se investigaron los mecanismos de conexión relevantes y no se acreditó participación en las rutas productivas delimitadas |
| UNKNOWN | La información disponible no permite establecer su estado |

**Consideraciones:**

- `EXECUTED` no implica que el componente haya funcionado correctamente. Su resultado debe evaluarse por separado.
- `REACHABLE` no demuestra que el flujo alcance esa llamada durante una ejecución real.
- `BROKEN` debe acompañarse de evidencia del defecto y de la conexión afectada.
- `DISCONNECTED` siempre es relativo a las rutas y al commit auditados, y exige investigar posibles cargas dinámicas, registros e invocaciones externas.
- Si un componente funciona en una ruta pero está roto en otra, se registrarán ambos resultados en la matriz de participación por ruta, sin reducirlos a una afirmación global engañosa.
- La investigación distinguirá evidencia estática, ejecución dinámica y comportamiento funcional demostrado, conforme a la metodología forense vigente.

---

## 5.6 Matriz principal de clasificación y viabilidad

Esta matriz será el inventario consolidado de los componentes relevantes para el pipeline productivo.

| Componente | Rol | Capacidad | Criticidad | Integración | Validez contractual | Evidencia funcional | Disposición candidata |
|---|---|---|---|---|---|---|---|
| `apps/cli/main.py` | R1, provisional | Entrada / control | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `apps/bootstrap/pipeline_factory.py` | R2, provisional | Composición | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/pipeline/orchestrator.py` | R3, provisional | Orquestación | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `runtime/engine.py` | R3, provisional | Ejecución de tareas | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `apps/llm_workers/__main__.py` | R1/R3, provisional | Worker LLM | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `apps/llm_workers/dispatcher.py` | R4, provisional | Despacho / inferencia | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/segmenter/service.py` | R4, provisional | Segmentación | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/routing/router.py` | R4/R5, provisional | Routing | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/chunking/policies.py` | R5, provisional | Políticas de chunking | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/execution/ports.py` | R7, provisional | Contratos de ejecución | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `infra/db/control_repo.py` | R6, provisional | Cola / persistencia | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `infra/db/profile_store.py` | R6, provisional | Almacenamiento de perfiles | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `core/compiler/service.py` | R4, provisional | Compilación documental | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |
| `apps/compiler/tectonic_runner.py` | R6, provisional | Generación física de PDF | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNDETERMINED |

**Campos complementarios obligatorios para cada componente investigado:**

- Etapa o etapas del pipeline en que participa.
- Ruta o rutas de ejecución asociadas.
- Clase, función o método relevante.
- Consumidor efectivo y mecanismo de invocación.
- Implementaciones alternativas o responsabilidades superpuestas.
- Dependencias relevantes.
- Referencia de evidencia verificable.
- Justificación de criticidad y disposición candidata.

Estos campos podrán registrarse en fichas complementarias o tablas auxiliares de la misma sección para preservar la legibilidad de la matriz principal.

No se deben completar por inferencia basada exclusivamente en nombres, comentarios o ubicación de los archivos.

Se ampliará la matriz únicamente con componentes relevantes para la ejecución productiva o para decisiones de integración, consolidación y eventual retiro.

---

## 5.7 Route Participation Matrix

Esta matriz identifica la participación de los componentes en las distintas rutas productivas o alternativas investigadas.

| Componente | CLI | Engine | LLM Daemon | OCR Router | Assembler | Benchmark |
|---|---|---|---|---|---|---|
| `apps/bootstrap/pipeline_factory.py` | ? | ? | ? | ? | ? | ? |
| `core/pipeline/orchestrator.py` | ? | ? | ? | ? | ? | ? |
| `apps/llm_workers/dispatcher.py` | ? | ? | ? | ? | ? | ? |
| `core/validation/pipeline.py` | ? | ? | ? | ? | ? | ? |
| `core/healing/pipeline.py` | ? | ? | ? | ? | ? | ? |
| `infra/db/control_repo.py` | ? | ? | ? | ? | ? | ? |
| `core/compiler/service.py` | ? | ? | ? | ? | ? | ? |

**Convenciones:**

- `E`: ejecución acreditada.
- `R`: conexión estática acreditada.
- `B`: conexión rota o incompatible.
- `—`: ausencia de participación acreditada dentro del alcance investigado.
- `?`: participación no verificada.

Cada celda significativa deberá poder vincularse a evidencia. Cuando existan distintas condiciones de ejecución, estas deberán documentarse.

La columna Benchmark se utiliza exclusivamente para reconocer usos alternativos y detectar posibles interferencias con producción, sin ampliar el alcance a una auditoría del benchmark.

Esta matriz complementa la investigación de §2 y no sustituye el análisis detallado de rutas allí establecido.

---

## 5.8 Critical Execution Dependency Map

Construir un grafo dirigido de las dependencias efectivas entre componentes indispensables para completar PDF → PDF.

El grafo deberá distinguir:

1. Dependencias estructurales.
2. Invocaciones efectivas acreditadas por código.
3. Ejecuciones demostradas dinámicamente.
4. Fronteras de proceso y almacenamiento.
5. Conexiones rotas o incompatibles.
6. Alternativas de implementación que compiten por una misma responsabilidad.

**[INSERTAR DIAGRAMA MERMAID BASADO EN EVIDENCIA]**

Este grafo no replicará el inventario estructural general del repositorio ni los grafos P1–P7 de F17-BIS.

Su función será identificar el subconjunto de dependencias que sostiene o impide la ejecución productiva.

Las transformaciones de datos y las rupturas de identidad se documentarán detalladamente en §4, mientras que aquí se utilizarán sus resultados para evaluar componentes.

---

## 5.9 Disposiciones candidatas de viabilidad

Las siguientes categorías permiten clasificar el tratamiento potencial de cada implementación sin adelantar una decisión arquitectónica definitiva.

| Disposición | Definición | Condición mínima para proponerla |
|---|---|---|
| KEEP | Componente justificado y aprovechable | Responsabilidad necesaria, cumplimiento contractual y evidencia funcional suficiente |
| CONNECT | Capacidad útil que no está integrada adecuadamente | Necesidad demostrada y conexión faltante identificada |
| REPAIR | Componente necesario que presenta defectos | Defecto acreditado y responsabilidad productiva justificada |
| CONSOLIDATE | Implementación redundante o divergente | Superposición real de responsabilidades y análisis de diferencias contractuales |
| RETIRE CANDIDATE | Componente aparentemente prescindible | Consumidores, contratos, referencias históricas y efectos de retiro investigados |
| UNDETERMINED | Evidencia insuficiente | Investigación pendiente o resultados inconclusos |

Una misma implementación puede presentar varios problemas, pero se registrará una disposición candidata principal y las condiciones que justifican los tratamientos secundarios.

**Estas categorías son herramientas de análisis. Las decisiones de remediación se formalizarán posteriormente mediante los mecanismos de autoridad correspondientes.**

Ninguna disposición consignada en este HITO autoriza por sí sola modificaciones, refactorizaciones, reemplazos o eliminaciones.

---

## 5.10 Componentes desconectados potencialmente aprovechables

Registrar componentes que implementen capacidades relevantes, pero cuya participación en el pipeline productivo no esté acreditada.

Para cada caso identificar:

- Capacidad implementada.
- Contrato o responsabilidad que satisface.
- Evidencia de ausencia de conexión en el alcance investigado.
- Implementaciones alternativas.
- Compatibilidad técnica con las etapas consumidoras.
- Cuestiones pendientes para determinar su aprovechamiento.

**[POR INVESTIGAR]**

---

## 5.11 Responsabilidades duplicadas e implementaciones competidoras

Registrar los componentes que presentan superposición real de responsabilidades.

Distinguir:

- Duplicación funcional.
- Implementaciones alternativas justificadas.
- Divergencia de contratos.
- Diferencias entre rutas de ejecución.
- Funcionalidades exclusivas de cada implementación.
- Riesgos de consolidación.

La existencia de dos clases con nombres similares o pertenecientes a la misma categoría R1–R7 no demuestra duplicación.

**[POR INVESTIGAR]**

El análisis causal y las contradicciones arquitectónicas de estas duplicaciones se desarrollarán en §6.

---

## 5.12 Componentes vacíos, históricos o aparentemente muertos

Investigar componentes sin implementación, sin consumidores acreditados, históricos, experimentales o aparentemente ajenos al pipeline productivo.

La clasificación distinguirá:

- Archivos vacíos.
- Interfaces o placeholders intencionales.
- Código histórico.
- Implementaciones reemplazadas.
- Componentes sin consumidores identificados.
- Capacidades utilizadas exclusivamente fuera de producción.
- Componentes cuya función no ha podido determinarse.

No se considerará código muerto de forma concluyente sin revisar los mecanismos relevantes de utilización y las obligaciones arquitectónicas vigentes.

**[POR INVESTIGAR]**

---

## 5.13 Riesgos de eliminación y dependencias ocultas

Antes de considerar la retirada de una implementación, verificar:

1. Consumidores directos e indirectos.
2. Importaciones dinámicas y registros.
3. Invocaciones mediante CLI, subprocess o servicios externos.
4. Referencias en configuración y despliegue.
5. Contratos normativos que exijan su comportamiento.
6. Efectos sobre identidad, persistencia, recuperación y preservación científica.
7. Dependencias de compatibilidad necesarias para el estado operativo actual.
8. Existencia de una implementación sustituta conforme y comprobada.

**[POR INVESTIGAR]**

La retirada efectiva de componentes pertenece a una fase posterior de decisión e implementación aprobada.

---

## 5.14 Resumen de viabilidad del repositorio productivo

Al completar la investigación, consolidar recuentos de los componentes analizados por:

| Dimensión | Resultado esperado |
|---|---|
| Rol arquitectónico | Distribución R1–R7 |
| Criticidad | Distribución C0–C3 y UNKNOWN |
| Integración | EXECUTED / REACHABLE / BROKEN / DISCONNECTED / UNKNOWN |
| Participación | Distribución por ruta productiva |
| Viabilidad | KEEP / CONNECT / REPAIR / CONSOLIDATE / RETIRE CANDIDATE / UNDETERMINED |

Distinguir claramente:

- Total de componentes productivos investigados.
- Componentes con evidencia funcional suficiente.
- Componentes con integración no acreditada.
- Componentes con defectos demostrados.
- Componentes con responsabilidades duplicadas.
- Componentes pendientes de evaluación.

Estos recuentos no constituyen porcentajes subjetivos de madurez o readiness. Su finalidad es caracterizar de forma reproducible el estado del pipeline.

**[POR INVESTIGAR]**

---

## 5.15 Conclusiones forenses y cuestiones derivadas

Consolidar exclusivamente los resultados sustentados por la investigación:

- Qué componentes cumplen una responsabilidad productiva demostrada.
- Qué capacidades necesarias carecen de integración suficiente.
- Qué implementaciones compiten por responsabilidades equivalentes.
- Qué componentes pueden aprovecharse sin reconstruir sus capacidades desde cero.
- Qué implementaciones presentan defectos o incompatibilidades acreditadas.
- Qué componentes requieren investigación adicional.
- Qué cuestiones necesitan una decisión posterior del Architecture Board.

Las decisiones definitivas sobre arquitectura canónica, integración, consolidación y retiro quedarán fuera de este HITO y se derivarán a los artefactos normativos y de ejecución correspondientes.

**[POR INVESTIGAR]**

---

# 6. ARCHITECTURAL DUPLICATION & ROOT-CAUSE ANALYSIS

## 6.1 Responsabilidades duplicadas

Investigar posibles duplicaciones en:

- Orquestación CLI / engine / daemons.
- Construcción de prompts y contexto.
- Routing y segmentación.
- Normalización, validación y healing.
- Persistencia y proyección de estados.
- Recovery, reconciler y sweeper.
- Composición de proveedores.
- Compilación y ensamblado.

## 6.2 Matriz de duplicaciones

| Responsabilidad | Implementaciones | Diferencias de contrato | ¿Coexistencia justificada? | Evidencia |
|---|---|---|---|---|
| Orquestación | Por verificar | UNKNOWN | UNKNOWN | — |
| Inferencia LLM | Por verificar | UNKNOWN | UNKNOWN | — |
| Recovery | Por verificar | UNKNOWN | UNKNOWN | — |
| Otras | Por verificar | UNKNOWN | UNKNOWN | — |

## 6.3 Causas estructurales

Investigar si las divergencias provienen de implementaciones paralelas, puertos incompatibles, cambios de composición, falta de pruebas de integración o responsabilidades sin dueño.

No registrar una causa raíz como confirmada por simple correlación.

## 6.4 Relación con hallazgos anteriores

Referenciar P1–P7, GAP Matrix y findings de F17-BIS/F18, indicando resolución histórica y vigencia actual.

---

# 7. PRODUCTION EXECUTION CONTRACTS

## 7.1 Composition roots y dependencia de infraestructura

**[POR INVESTIGAR]**

## 7.2 Identidad, persistencia y atomicidad

**[POR INVESTIGAR]**

## 7.3 FSM, cola, leases y autoridad de ejecución

**[POR INVESTIGAR]**

## 7.4 Journal, materialización y recuperación

**[POR INVESTIGAR]**

## 7.5 Preservación científica y separación TRANSLATE / PRESERVE

**[POR INVESTIGAR]**

## 7.6 Ensamblado íntegro y disponibilidad de artefactos

**[POR INVESTIGAR]**

En cada apartado distinguir los contratos FROZEN aplicables, su cumplimiento en código y su cumplimiento demostrado en la ejecución productiva.

---

# 8. PRODUCTION BLOCKERS & FAILURE TOPOLOGY

## 8.1 Bloqueantes para completar PDF → PDF

| ID | Bloqueo | Etapa afectada | Impacto demostrable | Evidencia | Relación con GAP existente |
|---|---|---|---|---|---|
| Pendiente | Por investigar | UNKNOWN | UNKNOWN | — | — |

## 8.2 Dependencias entre bloqueantes

**[INSERTAR GRAFO DE DEPENDENCIAS CAUSALES, SOLO CON RELACIONES ACREDITADAS]**

## 8.3 Fallos locales frente a incompatibilidades arquitectónicas

**[POR INVESTIGAR]**

## 8.4 Clasificación normativa

Registrar provisionalmente cada hallazgo según:

- Vía A: incumplimiento de contrato vigente.
- Vía B: vacío normativo.
- Vía C: contradicción normativa.

La decisión y planificación concretas se derivarán a los artefactos autorizados.

---

# 9. DYNAMIC EXECUTION & E2E EVIDENCE

## 9.1 Entorno y reproducibilidad

Registrar commit, sistema operativo, Python, dependencias, configuración, procesos iniciados y almacenamiento aislado.

## 9.2 E2E-0 — Caracterización AS-IS

Registrar la ejecución del PDF preregistrado por cada ruta pertinente.

| Ruta | Entrada | Última etapa alcanzada | Artefacto final | Resultado | Evidencia |
|---|---|---|---|---|---|
| CLI | Por fijar | UNKNOWN | UNKNOWN | NO EJECUTADO | — |
| Runtime / daemons | Por fijar | UNKNOWN | UNKNOWN | NO EJECUTADO | — |

## 9.3 Pruebas de integración entre fronteras

Incluir pruebas focalizadas de identidad, transacciones, persistencia multiproceso, disponibilidad de perfil, resultados materializados y compilación.

## 9.4 E2E determinista completo

**[NO EJECUTADO]**

## 9.5 E2E con proveedor real

**[NO EJECUTADO; REQUIERE AUTORIZACIÓN Y PRESUPUESTO]**

## 9.6 Limitaciones de la evidencia

No atribuir funcionamiento productivo a tests aislados, dobles, builds exitosos o PDFs históricos sin procedencia del código auditado.

---

# 10. PRODUCTION READINESS & RECONCILIATION SUMMARY

## 10.1 Estado AS-IS de capacidades

| Capacidad | Implementada | Integrada | Demostrada funcionalmente | Bloqueante |
|---|---|---|---|---|
| Ingesta | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Extracción / AST | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Segmentación / routing | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Ejecución LLM | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Persistencia | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Validación / healing | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Ensamblado / PDF | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Recuperación | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 10.2 Capacidades aprovechables demostradas

**[POR INVESTIGAR]**

## 10.3 Capacidades necesarias todavía no conectadas

**[POR INVESTIGAR]**

## 10.4 Redundancias e incompatibilidades demostradas

**[POR INVESTIGAR]**

## 10.5 Cuestiones de convergencia para el Board

Formular preguntas respaldadas por evidencia, sin elegir anticipadamente la arquitectura definitiva.

## 10.6 Riesgos residuales e incertidumbres

**[POR INVESTIGAR]**

---

# 11. EVIDENCE INDEX & TRACEABILITY

## 11.1 Registro de fuentes

| Referencia | Tipo | Commit / versión | Uso | Vigencia |
|---|---|---|---|---|
| Charter de estabilización | Preregistro | Por fijar | Autoridad de alcance | Actual |
| HITO P1–P7 de F17-BIS | Evidencia histórica | Según documentos | Baseline delta | Histórica |
| HITO_0.10 de F18 | GAP Matrix | Según documento | Reconciliación | Por verificar |
| Código productivo | Fuente primaria | `95ef8a38` | AS-IS | Baseline |
| Pruebas dinámicas | Evidencia de ejecución | Por registrar | Confirmación / refutación | Pendiente |

## 11.2 Evidencia por conexión y componente

Cada afirmación relevante debe remitir a identificadores de evidencia según la metodología vigente, con localización reproducible.

## 11.3 Trazabilidad de hallazgos heredados

**[POR INVESTIGAR]**

## 11.4 Hipótesis abiertas y condiciones de cierre

**[POR INVESTIGAR]**

---

# 12. CIERRE FORENSE Y DERIVACIÓN

## 12.1 Resultado de la investigación

Registrar exclusivamente conclusiones sustentadas por evidencia del Atlas.

## 12.2 Grado de completitud de la investigación

Declarar qué capacidades, rutas, conexiones y fronteras fueron inspeccionadas, cuáles pudieron reproducirse y cuáles permanecen no verificables.

## 12.3 GAPs y cuestiones derivadas

Referenciar la Gap Matrix y los registros correspondientes. No establecer tareas, responsables, batches ejecutables ni decisiones de retiro en este HITO.

## 12.4 Condiciones de congelamiento del Atlas

- Alcance preregistrado cubierto o limitaciones explícitas.
- Rutas productivas caracterizadas.
- Capacidades indispensables reconciliadas con implementaciones existentes.
- Conexiones críticas evaluadas y documentadas.
- Componentes candidatos a conservación, integración, corrección, consolidación o retiro identificados con evidencia.
- Hallazgos previos reconciliados sin duplicación indebida.
- Hipótesis resueltas conforme al procedimiento forense vigente.
- Cuestiones arquitectónicas pendientes derivadas a la autoridad correspondiente.

**Estado de cierre:** PENDIENTE.

---

**Fin del esqueleto v0.1.0.**