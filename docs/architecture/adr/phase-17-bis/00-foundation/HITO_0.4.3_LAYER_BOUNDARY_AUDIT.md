# HITO_0.4.3_LAYER_BOUNDARY_AUDIT.md
## Layer Boundary, Dependency Flow & Hexagonal Architecture Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO (Sub-Hito 0.4.3)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Solo lectura / Auditoría analítica del grafo de dependencias, contratos de frontera de capas y cumplimiento de la Regla de Inversión de Dependencias (DIP). Cero mutaciones en código productivo. Disposición diferida al Hito 0.5 (`UNASSESSED`).

---

## 1. PROPÓSITO Y ALCANCE DEL SUB-HITO 0.4.3

El **Sub-hito 0.4.3** audita el grado de cumplimiento de Clean Architecture, la direccionalidad del flujo de dependencias, la pureza de los adaptadores hexagonales en `infra/`, la composición de servicios en el orquestador y la separación entre el runtime productivo (`core/pipeline`) y el subdominio de evaluación (`core/benchmark`).

A partir de la inspección del Composition Root (`apps/bootstrap/pipeline_factory.py`), el orquestador de aplicación (`core/pipeline/orchestrator.py`) y el adaptador de lectura (`infra/adapters/pdf_parser.py`), se construye el **Layer Boundary Contract Map**.

---

## 2. REGISTRO DE EVIDENCIA FORENSE Y FORTALEZAS (E-0.4-201 a E-0.4-205)

### Evidencia E-0.4-201: Cumplimiento Estricto de la Regla de Dependencias en `orchestrator.py`
* **Archivo Fuente Primario:** `core/pipeline/orchestrator.py`
* **Símbolo Auditado:** `TranslationPipeline`
* **Análisis Forense:** Las sentencias `import` en el encabezado de `orchestrator.py` pertenecen exclusivamente a `core/` (`core.pipeline`, `core.ast`, `core.metrics`, `core.normalization`, `core.compiler`). No se observan importaciones provenientes de `infra/`, `apps/`, bases de datos (`sqlite3`) ni librerías externas de E/S (`fitz` / `PyMuPDF`).

---

### Evidencia E-0.4-202: Inversión de Control por Contratos (DIP) en Constructor
* **Archivo Fuente Primario:** `core/pipeline/orchestrator.py`
* **Símbolos Auditados:** `ParserProtocol`, `ChunkerProtocol`, `DispatcherProtocol`, `AssemblerProtocol`, `AuditBuilderProtocol`, `DocumentRepositoryProtocol`
* **Análisis Forense:** `TranslationPipeline` declara y consume sus dependencias mediante interfaces `typing.Protocol`. El orquestador no instancia adaptadores de infraestructura; estos son inyectados desde el Composition Root (`pipeline_factory.py`).

---

### Evidencia E-0.4-203: Adaptador Hexagonal Delgado (`PdfParserAdapter`)
* **Archivo Fuente Primario:** `infra/adapters/pdf_parser.py`
* **Símbolos Auditados:** `PdfParserAdapter.parse()`
* **Análisis Forense:** Implementa `ParserProtocol`. Desacopla la extracción física delegando la llamada a `self._provider.extract()` y el mapeo estructural a `self._layout_to_ast_mapper`. Captura excepciones de bajo nivel y las traduce hacia excepciones de dominio (`LayoutRecoveryError`, `ASTMappingError`).

---

### Evidencia E-0.4-204: Ausencia de Dependencias Directas Hacia `core/benchmark/`
* **Archivos Fuente Primarios:** `core/pipeline/orchestrator.py`, `infra/adapters/pdf_parser.py`
* **Análisis Forense:** En los artefactos auditados del pipeline productivo no se observan importaciones ni referencias dirigidas hacia el subdominio `core/benchmark/`. La ejecución del pipeline transcurre de forma independiente a la suite de evaluación topológica.

---

### Evidencia E-0.4-205: Desacoplamiento entre Proveedor Físico y Lógica Sintáctica
* **Archivo Fuente Primario:** `apps/bootstrap/pipeline_factory.py`
* **Símbolos Auditados:** `_adapter_mapper()`, `FlatASTBuilder`
* **Análisis Forense:** `PyMuPDFProvider` emite únicamente `DocumentLayout` (maquetación física). El proveedor ignora la estructura del AST. La transformación hacia `ASTNode` la ejecuta `FlatASTBuilder.build()` dentro de la función de composición inyectada al adaptador.

---

## 3. REGISTRO DE OBSERVACIONES Y DEUDA DE ARQUITECTURA (OBS-0.4.3-01 a OBS-0.4.3-05)

| ID Observación | Componente | Comportamiento Observado | Impacto Arquitectónico / Riesgo |
| :--- | :--- | :--- | :--- |
| **OBS-0.4.3-01** | `TranslationPipeline.execute` | Realiza transformaciones in-line (normalización de viñetas con regex, sustitución de `ParagraphPayload`, forzado de `control_plane` para tablas e imágenes). | **Fuga de Lógica de Transformación:** El orquestador asume responsabilidades de modificación de datos en lugar de delegar el 100% de la limpieza a la capa `core/normalization`. |
| **OBS-0.4.3-02** | `orchestrator.py` | Declara los protocolos `ParserProtocol`, `ChunkerProtocol`, etc., dentro del mismo archivo del orquestador. | **Preferencia Organizativa:** La co-ubicación de interfaces con el consumidor es válida en Clean Architecture, aunque moverlas a un `ports.py` dedicado puede favorecer la cohesión documental. |
| **OBS-0.4.3-03** | `pipeline_factory.py` | Muta directamente el estado interno del dispatcher inyectado: `dispatcher.validation_pipeline = ...`. | **Violación Mínima de Encapsulamiento:** La fábrica asume la presencia de atributos mutables en un colaborador en lugar de inyectar las dependencias a través de su constructor o factoría. |
| **OBS-0.4.3-04** | `TranslationPipeline.execute` | Instancia colaboradores directamente (`SemanticNodeClassifier()`, `ASTIntegrityValidator()`, `HierarchicalContextEnricher()`, `StructuralAssetPlaceholder()`). | **Acoplamiento Interno:** Dificulta la sustitución de estrategias y la ejecución de pruebas unitarias aisladas al acoplar el orquestador a implementaciones concretas de la capa de aplicación. |
| **OBS-0.4.3-05** | `pipeline_factory.py` | El parámetro `dispatcher` está tipado como `Any` en la firma de `build_pipeline()`. | **Pérdida de Tipado Estático:** Desactiva la verificación del analizador estático (`pyright`) sobre el contrato del despachador en el punto de entrada de composición. |

---

## 4. LAYER BOUNDARY CONTRACT MAP

```text
[ CLIENTES / EXTERNAL INTERFACES ]
  apps/cli, apps/api, tools/evaluation
       │
       ▼
[ COMPOSITION ROOT ]
  apps/bootstrap/pipeline_factory.py (Tipado 'dispatcher: Any' -> OBS-0.4.3-05)
       │
       ├───────────────────────────────────────────┐
       │ Inyecta colaboradores vía Protocols       │ Inyecta Adaptadores Hexagonales
       ▼                                           ▼
[ APPLICATION ORCHESTRATION ]              [ INFRASTRUCTURE ADAPTERS ]
  core/pipeline/orchestrator.py               infra/adapters/pdf_parser.py
  (TranslationPipeline)                       infra/db/document_repository.py
       │                                      infra/db/fsm_repository.py
       ├─ Instancia in-line colaboradores ──┐       │
       │  (OBS-0.4.3-04)                    │       │ Implementan Protocols
       ▼                                    ▼       │
[ PURE DOMAIN CORE ] ◄───────────────────┴───────┘
  core/ast/ (ASTNode, Payloads, Enums)
  core/layout/ (LayoutBlockCollection)
  core/normalization/ (Classifier, Enricher, Fixers)
  core/compiler/ (DocumentAssembler)
       ▲
       │ Consumen ASTNode (Sin importaciones observadas desde runtime productivo)
[ BENCHMARK SUBDOMAIN (AUDITED ARTIFACTS) ]
  core/benchmark/topology/ (ZhangShasha, LCS, Evaluators)
```

---

## 5. RECOMENDACIONES ARQUITECTÓNICAS DIFERIDAS (NO BLOQUEANTES)

Las siguientes recomendaciones derivan de las observaciones realizadas durante el Sub-hito 0.4.3. No constituyen defectos funcionales ni impiden el avance del proyecto. Se registran como oportunidades de mejora evolutiva no bloqueantes para futuras fases del sistema.

### REC-0.4.3-01 — Externalizar completamente la normalización del `TranslationPipeline`
* **Origen:** `OBS-0.4.3-01`
* **Detalle:** Actualmente `TranslationPipeline.execute()` contiene transformaciones directas sobre nodos (normalización de viñetas, adaptación de payloads, re-hidratación de `control_plane` para imágenes/tablas).
* **Recomendación Futura:** Consolidar toda la lógica de transformación semántica dentro del pipeline oficial en `core/normalization/` para que el orquestador permanezca exclusivamente como coordinador de casos de uso.
* **Prioridad:** Baja.

### REC-0.4.3-02 — Reducir la instanciación directa de colaboradores dentro del Pipeline
* **Origen:** `OBS-0.4.3-04`
* **Detalle:** `TranslationPipeline.execute()` instancia directamente servicios de aplicación (`SemanticNodeClassifier`, `ASTIntegrityValidator`, `HierarchicalContextEnricher`, `StructuralAssetPlaceholder`). Aunque no viola Clean Architecture por pertenecer al mismo subdominio de aplicación, reduce la sustituibilidad mediante composición.
* **Recomendación Futura:** Evaluar la inyección de estos colaboradores desde el Composition Root (`pipeline_factory.py`) cuando aumente la variedad de estrategias o implementaciones alternativas.
* **Prioridad:** Baja.

### REC-0.4.3-03 — Formalizar completamente el contrato del Dispatcher
* **Origen:** `OBS-0.4.3-03`, `OBS-0.4.3-05`
* **Detalle:** En `pipeline_factory.py`, el `dispatcher` entra tipado como `Any` y posteriormente se mutan sus atributos (`dispatcher.validation_pipeline = ...`).
* **Recomendación Futura:** Formalizar un `DispatcherProtocol` explícito y requerir las canalizaciones de validación en su constructor para eliminar mutaciones de estado posteriores y recuperar garantías de análisis estático (`pyright`).
* **Prioridad:** Baja.

### REC-0.4.3-04 — Vigilar la amplitud de responsabilidades del `TranslationPipeline`
* **Detalle:** La auditoría confirma que el orquestador cumple su función de coordinación de forma ordenada, pero centraliza una secuencia extensa de pasos consecutivos (clasificación, normalización, validación, enriquecimiento, chunking, dispatch, ensamblado y auditoría).
* **Recomendación Futura:** Monitorear el crecimiento del orquestador en futuras fases para evitar que acumule responsabilidades excesivas a medida que el pipeline incorpore nuevos pasos.
* **Prioridad:** Baja.

---

## 6. DECLARACIÓN DE CIERRE DEL SUB-HITO 0.4.3

El **Sub-hito 0.4.3 (Layer Boundary Audit)** queda oficialmente **COMPLETADO Y CONGELADO (`FROZEN`)**.