# ARCHITECTURE DECISION RECORD (ADR)
## ADR_F17-BIS_0: Architecture & Baseline Audit Gate — Forensic Discovery, Contract Mapping & Decision Resolution

**Contexto y Problema:**
El ADR Maestro **ADR_F17-BIS** establece el marco de gobernanza general para la construcción de la **Baseline Científica Inmutable** (*Canonical Corpus & Ground Truth*), indispensable para proteger al sistema contra regresiones topológicas antes de abordar la Fase 18 (*Advanced Local Runtime*). 

Sin embargo, ejecutar directamente las Fases 1 a 6 de la Fase 17-BIS sin realizar una auditoría forense previa sobre la infraestructura preexistente (`core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/benchmark/topology`, `core/ast`, `infra/fs`, `tools/evaluation`) conlleva serios riesgos de sobreingeniería, duplicación de servicios y refactorización prematura. Asimismo, se ha descubierto que la auditoría del arnés de evaluación y regresión (Hitos 0.1 a 0.4) debe complementarse de forma imperativa con un escrutinio sobre el **pipeline real de producción y runtime** (`core/pipeline`, `core/extraction`, `core/layout`, `core/execution`, `runtime`, etc.), ya que el éxito en el benchmark no garantiza la integridad transaccional del sistema de runtime. Se han detectado incertidumbres críticas: sellado parcial (*Partial Sealing*), duplicación de responsabilidades de linaje, desacoplamiento de identidades físicas/científicas, fracturas en la canalización de ingesta real y ausencia de un contrato de CI consolidado.

**Objetivo de la Fase 0:**
Ejecutar una auditoría forense analítica y de solo lectura (*Read-Only Discovery*) sobre el repositorio para mapear el estado real de la arquitectura de evaluación y del pipeline productivo de runtime, identificar componentes reutilizables, documentar las causas raíz de los fallos de dominio y resolver con evidencia empírica los Candidatos a Decisión (**DC-01 a DC-11**), generando la propuesta de congelamiento formal del ADR Maestro **ADR_F17-BIS** antes de escribir código de producción en la Fase 1.

**Decisiones Arquitectónicas de la Fase 0:**
1. **Regla de Solo Lectura (Read-Only Audit Gate):** Queda estrictamente prohibido modificar código de producción, refactorizar clases existentes, alterar DTOs de dominio, escribir adaptadores o poblar el disco con documentos del corpus durante la Fase 0. La función exclusiva es observar, medir, trazar y documentar.
2. **Gobernanza Basada en Evidencia (Evidence First):** Ningún Candidato a Decisión (DC) se dará por resuelto mediante suposiciones o intuiciones de diseño. Toda resolución requerirá trazabilidad directa hacia líneas de código observadas, DTOs existentes o flujos de ejecución comprobados.
3. **Principio de Reutilización Estricta (Reuse Before Invent):** Se exige la auditoría y mapeo exhaustivo de componentes preexistentes (`ZhangShashaEngine`, `TreeEditDistanceEvaluator`, `EntityRecallEvaluator`, `compute_ast_hash`, `LocalFileSystemGroundTruthReader`) para evitar la creación de abstraacciones duplicadas.
4. **Descomposición Hexepartita con Escrutinio de Runtime (Hitos 0.1 a 0.5 incluyendo el Hito 0.4.5):** La Fase 0 se estructurará rigurosamente en un ciclo analítico secuencial ampliado, asegurando que la superficie de evaluación y la canalización de producción queden íntegramente auditadas antes de la consolidación de decisiones.
5. **Entregable de Cierre de Fase 0:** La Fase 0 concluirá únicamente cuando se presente la *Architecture Gap Matrix*, el *Contract Map* y la resolución fundamentada de DC-01 a DC-11, elevando la versión final del **ADR_F17-BIS (Maestro)** a estado `FROZEN`.

**No-Objetivos:**
* No se escribe ni modifica código en `core/`, `infra/`, `apps/` ni `tools/`.
* No se modifican las suites de pruebas unitarias o de integración preexistentes en `tests/`.
* No se realiza la recolección, curaduría ni ingesta de los 20–30 PDFs del corpus canónico (corresponde a la Fase 4).
* No se implementa la compuerta de regresión en CI ni los scripts de prueba (corresponde a la Fase 6).
* No se abordan optimizaciones de rendimiento, asincronía ni manejo de memoria (pertenecen a la Fase 18).

---

# ROADMAP DE EJECUCIÓN (Hitos de la Fase 0)

## Hito 0.1: Repository & Architecture Inventory
Auditoría estructural y mapeo de componentes activos en el repositorio para establecer la línea de base del código existente.
* Inventariar archivos, clases, DTOs y puertos en `core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/benchmark/topology`, `core/ast`, `infra/fs` y `tools/evaluation`.
* Mapear las dependencias reales entre la capa de aplicación, dominio e infraestructura.
* Identificar componentes vigentes vs. abstracciones obsoletas o históricas.
* **Entregables:** *Repository Inventory*, *Architecture Component Map* y *Dependency Graph*.

## Hito 0.2: Ground Truth & Sealing Forensic Audit
Auditoría forense detallada del proceso de sellado y la gestión de oráculos.
* Inspeccionar el flujo de ejecución de `SealGroundTruthUseCase` para documentar la causa raíz del sellado parcial (*Partial Sealing*).
* Analizar la duplicación de responsabilidades entre `ManifestLineageSealer` y `ManifestGroundTruthUpdater`.
* Mapear los contratos y puertos de lectura/escritura de oráculos en `infra/fs/ground_truth_store.py`.
* **Entregables:** *Ground Truth & Sealing Forensic Report* con el análisis de causa raíz y propuesta de unificación de autoridad.

## Hito 0.3: Identity, Hashing & Canonicalization Audit
Auditoría de los algoritmos de firma criptográfica y serialización determinista.
* Inspeccionar la función `compute_ast_hash` en `core/ast/hashing.py` (campos incluidos, estabilidad ante ordenación, manejo de metadatos volátiles).
* Auditar `ManifestFingerprintCalculator` y los modelos `DocumentFingerprint` y `CorpusManifest`.
* Evaluar el grado de acoplamiento/desacoplamiento entre el hash del PDF físico y el hash del oráculo AST.
* **Entregables:** *Identity & Hashing Audit Report* y *Canonicalization Map*.

## Hito 0.4: AST, Topology, Regression & Layer Boundary Audit
Auditoría de las herramientas de comparación de árboles, ontología de nodos y fronteras de arquitectura limpia.
* Auditar los evaluadores topológicos `ZhangShashaEngine`, `TreeEditDistanceEvaluator` y `EntityRecallEvaluator`.
* Inspeccionar el enum `ContentNodeType` en `core/ast/enums.py` para analizar el impacto semántico de cada tipo de nodo.
* Mapear las fronteras actuales entre las capas de Dominio, Aplicación, Infraestructura y el Test Runner de CI.
* **Entregables:** *AST & Topology Capability Matrix* y *Layer Boundary Contract Map*.

## Hito 0.4.5: Production Pipeline & Runtime Boundary Audit
Auditoría forense complementaria de la canalización real de producción (desde la ingesta física hasta la compilación de artefactos, el motor transaccional FSM/CQRS y la recuperación de fallos) para verificar la composición efectiva de los componentes y las fronteras de runtime.
* Auditar el Composition Root, los puntos de entrada (CLI y Daemons) y los orquestadores de pipeline (`core/pipeline/`).
* Trazar el flujo de ingestión física, maquetación, construcción de AST y normalización trans-página.
* Analizar los contratos del Segmenter V2, el enrutador de estrategias y los chunkers de presupuestos de tokens.
* Inspeccionar la infraestructura de dispatching hacia LLMs, control de cuotas (FinOps), caché y manejo de resiliencia.
* Auditar las canalizaciones de validación estricta y auto-reparación (*Healing*) post-traducción.
* Evaluar el motor de ensamblado documental, la serialización atómica en disco y la ejecución segura del compilador Tectonic.
* Revisar el núcleo transaccional de ejecución: máquina de estados (FSM), persistencia CQRS, event logs y daemons de recuperación (`runtime/`, `core/execution/`).
* **Entregables:** *Production Pipeline Forensic Report*, *Production Composition Map*, *Production Evidence Matrix* y *Benchmark vs Production Boundary Map*.

## Hito 0.5: Decision Consolidation & Architecture Freeze Proposal
Consolidación de los hallazgos de los Hitos 0.1 a 0.4.5 y resolución formal de las decisiones de la fase.
* Consolidar la *Architecture Gap Matrix* (Estado Actual vs. Requerimiento vs. Gap vs. Acción).
* Elaborar el *Contract Map* definitivo (`KEEP`, `EXTEND`, `REPLACE`, `DEPRECATE`).
* Registrar la resolución justificada con evidencia empírica para los Candidatos a Decisión **DC-01 a DC-11**.
* Presentar la propuesta de actualización del **ADR_F17-BIS (Maestro)** para su paso a estado `FROZEN`.

---

## TAXONOMÍA DE AUDITORÍA Y CANDIDATOS A DECISIÓN (HITO 0)

Esta matriz gobierna los puntos abiertos de arquitectura que la Fase 0 debe responder con evidencia empírica extraída del código antes de autorizar la implementación de la Fase 1.

| ID | Candidato a Decisión | Vector Afectado | Pregunta Clave de Auditoría (Fase 0) | Criterio de Resolución Basado en Evidencia |
| :--- | :--- | :--- | :--- | :--- |
| **DC-01** | Hash de Identidad (Merkle vs Composite) | `core/benchmark/corpus` | ¿Se requiere un árbol de Merkle o un hash compuesto determinista es suficiente a esta escala (20-30 docs)? | Evaluar complejidad vs reproducibilidad comprobada en `ManifestFingerprintCalculator`. |
| **DC-02** | Composición de $H_{physical}$ | `core/benchmark/corpus/models.py` | ¿Qué atributos exactos de `CorpusDocumentMetadata` y `DocumentFingerprint` deben formar la firma física del PDF? | Verificar estabilidad y determinismo de campos (`pdf_sha256`, `page_count`, `traits`). |
| **DC-03** | Composición de $H_{baseline}$ | `core/ast/hashing.py`, `corpus/` | ¿Cómo debe encadenarse $H_{physical}$ con las firmas producidas por `compute_ast_hash` y la versión de esquema? | Demostrar que `compute_ast_hash` produce firmas inmutables para oráculos `.ast.json`. |
| **DC-04** | Contrato de Validez del Ground Truth | `core/ast/validator.py` | ¿Qué invariantes de dominio en `ASTNode` separan un borrador (*Draft*) de un *Oráculo Válido*? | Inspeccionar `ASTIntegrityValidator` y verificar reglas de no-vaciedad y jerarquía. |
| **DC-05** | Ciclo de Vida y Autoridad de Sello | `ground_truth/`, `corpus/` | ¿Quién posee la autoridad de sellado y cómo se eliminan advertencias en `SealGroundTruthUseCase`? | Auditar causa raíz del Partial Sealing en `use_cases.py` y proponer Fail-Fast atómico. |
| **DC-06** | Taxonomía de Criticidad (`ContentNodeType`) | `core/ast/enums.py` | ¿Cómo se clasifican los valores de `ContentNodeType` en niveles de severidad de regresión (`CRITICAL`, `WARNING`, `INFO`)? | Mapear la jerarquía de nodos en AST V2 y diferenciar contenido semántico de formato incidental. |
| **DC-07** | Reglas de Regresión Topológica | `core/benchmark/topology/` | ¿Bajo qué condiciones específicas de desalineación topológica la evaluación emite `HARD FAIL` vs `WARNING`? | Evaluar el comportamiento de `ZhangShashaEngine` y `EntityRecallEvaluator` ante sustituciones. |
| **DC-08** | Desacoplamiento e Invalidez de Sello | `core/benchmark/` | ¿Qué eventos específicos (cambio de PDF, mutación de AST, cambio de esquema) invalidan el estado `SEALED`? | Analizar cómo la alteración de hashes componentes rompe la firma global $H_{baseline}$. |
| **DC-09** | Versionado de Corpus (`CorpusVersion`) | `corpus/models.py` | ¿Cómo se estructuran los incrementos SemVer (`MAJOR.MINOR.PATCH`) ante sustitución o adición de documentos? | Inspeccionar el VO `CorpusVersion` actual y validar su semántica de compatibilidad. |
| **DC-10** | Runner de CI Desacoplado | `tests/integration/` | ¿Cómo se invoca la prueba de regresión en `pytest` garantizando cero lógica de dominio en el test runner? | Verificar que la suite actúe como cliente puro de `EvaluateCanonicalRegressionUseCase`. |
| **DC-11** | Contrato de Fronteras entre Capas | `core/`, `infra/`, `tools/` | ¿Qué responsabilidades pertenecen a Domain, Application, Infrastructure y CI, y qué dependencias se prohíben? | Mapear los puertos existentes (`GroundTruthArtifactPort`, etc.) y certificar Clean Architecture. |

---

## CRITERIOS DE ACEPTACIÓN Y DEFINITION OF DONE (DoD) DE LA FASE 0

La **Fase 0** se considerará oficialmente completada y aprobada únicamente cuando se entreguen los siguientes artefactos sin haber mutado el código de producción:

1. **Reporte de Auditoría Forense Completo:** Documentación consolidada de los Hitos 0.1, 0.2, 0.3, 0.4 y 0.4.5 (Pipeline y Runtime) en el repositorio.
2. **Matriz de Gaps y Mapas de Contratos:** Publicación de la *Architecture Gap Matrix* y el *Contract Map* (`KEEP`, `EXTEND`, `REPLACE`, `DEPRECATE`) integrando la perspectiva de producción.
3. **Resolución Oficial de DC-01 a DC-11:** Registro de respuestas justificadas con evidencia del código para los 11 Candidatos a Decisión.
4. **Propuesta de Congelamiento Aprobada:** Actualización del borrador del **ADR Maestro (ADR_F17-BIS)** con las decisiones técnicas cerradas, listo para su paso a estado `FROZEN` y habilitando el inicio de la Fase 1.


## RESULTADOS CONSOLIDADOS FASE 17-BIS 

### HITO 0.1

#### 1. Inventario Estructural y Cobertura de Evidencia Primaria (Entregable 1)
* **Causa Raíz:** Necesidad de establecer una línea de base inmutable y contrastada contra código real antes de diseñar o implementar la Baseline Científica. Se requería erradicar las asunciones sobre componentes existentes en `core/ast`, `core/benchmark/` e `infra/`.
* **Actividades y Cobertura Ejecutadas:**
  * **Inspección Estática de Código Primario:** Análisis exhaustivo de firmas, tipos, agregados y protocolos en los 6 subdominios declarados en el alcance.
  * **Registro de Evidencia Primaria (`E-0.1-001` a `E-0.1-020`):** Mapeo de 20 artefactos de evidencia de código con sus firmas exactas, dependencias e implicaciones operacionales.
  * **Aislamiento de Límite Epistemológico:** Aplicación estricta de la regla *Production Read-Only / Audit-Artifact Write-Allowed*. Ningún componente fue clasificado como `KEEP`, `EXTEND`, `REPLACE` o `DEPRECATE`; la totalidad de las disposiciones se mantuvo formalmente como **`UNASSESSED`** para garantizar neutralidad hasta el Hito 0.5.

#### 2. Mapeo de Componentes y Diagnóstico Forense Inicial (Entregable 2)
* **Causa Raíz:** Existencia de fallas invisibles de dominio en la infraestructura heredada de benchmarking, tales como la permisividad de sellados parciales y la ambigüedad en las firmas criptográficas de los manifiestos.
* **Hallazgos Forenses Clave Registrados:**
  * **Mecanismo Causal Inmediato de *Partial Sealing* (`E-0.1-011` / `OBS-0.1-07`):** Se demostró estáticamente que `SealGroundTruthUseCase.execute()` evalúa la presencia de oráculos mediante `if self._artifact_port.artifact_exists(doc_id):`. Si un oráculo no existe, se omite silenciosamente sin lanzar excepción, permitiendo que el manifiesto se re-sella incompleto ($N_{\text{PDF}} \neq N_{\text{GT}}$).
  * **Duplicación Estructural de Servicios (`E-0.1-010` / `OBS-0.1-02`):** Confirmación de dos servicios independientes con lógica idéntica de actualización de linaje y recálculo de manifiesto: `ManifestLineageSealer` (`core/benchmark/corpus/services.py`) y `ManifestGroundTruthUpdater` (`core/benchmark/ground_truth/services.py`).
  * **Desacoplamiento Criptográfico en Manifiesto (`E-0.1-007` / `OBS-0.1-06`):** `ManifestFingerprintCalculator.compute_hash()` solo firma metadatos de los PDFs físicos (`doc_id`, `sha256`, `traits`, `page_count`). Los hashes del oráculo (`ground_truth_sha256`) no forman parte de la firma global del manifiesto, permitiendo mutaciones de AST sin alterar la huella del manifiesto.
  * **Riesgo de Volatilidad en Hash de AST (`E-0.1-003`):** La función `compute_ast_hash()` incluye `node_id` en el JSON serializado. Si el extractor genera UUIDs efímeros en runtime, dos ASTs con contenido idéntico producirán firmas totalmente divergentes.

#### 3. Grafo de Dependencias Reales y Redundancias Topológicas (Entregable 3)
* **Causa Raíz:** Incertidumbre sobre el acoplamiento entre capas y la existencia de rutas paralelas para el cálculo de distancias de edición de árboles (*Tree Edit Distance*).
* **Hallazgos Forenses Clave Registrados:**
  * **Coexistencia en `core/benchmark/` (`OBS-0.1-01`):** Mapeo de acoplamiento de espacio de nombres entre benchmarking de LLM/generativo (`GeminiBenchmarkRunner`, `LeaderboardService`) y benchmarking topológico de Parsers (`ZhangShashaEngine`, `EntityRecallEvaluator`).
  * **Doble Infraestructura Topológica (`E-0.1-019` / `OBS-0.1-04` / `OBS-0.1-08`):** Se demostró la coexistencia de dos motores paralelos de Tree Edit Distance: el motor nativo de dominio `ZhangShashaEngine` (`core/benchmark/topology/engines/zhang_shasha/`) y la métrica de herramientas `StructuralTopologyMetric` (`tools/evaluation/topology/metrics/structural.py`) acoplada a la librería externa C/Python `apted`.
  * **Ubicación de Serialización (`E-0.1-014` / `OBS-0.1-03`):** Mapeo de la dependencia crítica con `infra/serialization/ast_json.py` (`write_ast_json_atomic`), el cual ejecuta I/O con garantías SRE mediante archivos temporales intermedios y `os.fsync`.

---

### HITO 0.2

#### 1. Auditoría Forense del Ciclo de Vida y Flujo Transaccional (Entregable 1)
* **Causa Raíz:** Necesidad de auditar y trazar el flujo completo de creación de borradores (*Golden Drafts*), generación de candidatos, evaluación topológica, actualización de linaje y sellado criptográfico para determinar la causa raíz de corrupciones e inconsistencias en la Baseline.
* **Actividades y Cobertura Ejecutadas:**
  * **Inspección Forense de Casos de Uso y Servicios:** Traza analítica de `SealGroundTruthUseCase`, `GenerateGoldenDraftUseCase`, `ManifestLineageSealer`, `ManifestGroundTruthUpdater`, `ManifestFingerprintCalculator` y los puntos de entrada CLI (`freeze_ground_truth.py`, `generate_candidates.py`, `run_benchmark.py`).
  * **Registro de Evidencia Forense Primaria (`E-0.2-001` a `E-0.2-010`):** Mapeo de 10 hallazgos transaccionales sustentados en código real.
  * **Cumplimiento de Política Read-Only:** Auditoría ejecutada sin modificar archivos de producción, registrando hallazgos con disposición **`UNASSESSED`** para resolución en el Hito 0.5.

#### 2. Diagnóstico Causal de Fallas P0 y P1 (Entregable 2)
* **Causa Raíz:** Defectos estructurales en la lógica de sellado, desacoplamiento en las firmas globales de manifiesto y duplicación de autoridad de linaje.
* **Hallazgos Forenses Clave Registrados:**
  * **Mecanismo Causal de Sellado Parcial (`E-0.2-001`, `E-0.2-002` / `GAP-0.2-01`):** Demostración en código de la verificación `if self._artifact_port.artifact_exists(doc_id):` en `SealGroundTruthUseCase`. La ausencia de un archivo `.json` de oráculo no lanza excepción; omite silenciosamente el documento permitiendo que `ManifestLineageSealer` selle y re-firme un manifiesto incompleto ($N_{\text{PDF}} \neq N_{\text{GT}}$).
  * **Desacoplamiento Criptográfico de Firma Global (`E-0.2-003` / `GAP-0.2-02`):** Demostración de que `ManifestFingerprintCalculator.compute_hash()` solo firma metadatos de los PDFs físicos (`doc_id`, `sha256`, `traits`, `page_count`). Las firmas del Ground Truth (`ground_truth_sha256`) se ignoran en el hash global, haciendo que `manifest_hash` no se altere ante mutaciones o borrados del oráculo.
  * **Duplicación de Autoridad y Código Muerto (`E-0.2-004` / `GAP-0.2-03`):** Se confirmó que `ManifestGroundTruthUpdater` (`core/benchmark/ground_truth/services.py`) es idéntico línea por línea a `ManifestLineageSealer` (`core/benchmark/corpus/services.py`) y constituye código huérfano sin llamadas en todo el proyecto.
  * **Sellado sin Validación de Estructura (`E-0.2-005` / `GAP-0.2-04`):** `SealGroundTruthUseCase` lee los bytes crudos del archivo sin ejecutar `ASTValidator.validate()` ni verificar validez sintáctica de nodos JSON antes de congelar.
  * **Inexistencia de Máquina de Estados de Oráculo (`E-0.2-006` / `GAP-0.2-05`):** Ausencia de Enums de ciclo de vida (`DRAFT`/`SEALED`) en `RawDocumentEntryDTO`; la condición de sello se infiere únicamente de la presencia de un string no nulo en `ground_truth_sha256`.
  * **Incoherencia entre Identidad Criptográfica y Benchmark (`E-0.2-007` / `GAP-0.2-06`):** Confirmación de que `ASTFingerprintPolicy.semantic_fingerprint` omite `node_id` para comparar por `(node_type, content)`, mientras que `compute_ast_hash()` sí lo incluye, creando un conflicto entre la firma de oráculo y la evaluación del benchmark.

#### 3. Grafo Transaccional Unificado de Ingesta y Evaluación (Entregable 3)
* **Causa Raíz:** Falta de visibilidad de las relaciones de dependencia entre los scripts de la capa `tools/evaluation`, los servicios de aplicación en `core/` y la infraestructura de almacenamiento de artefactos en `infra/fs`.
* **Hallazgos Forenses Clave Registrados:**
  * **Mapeo de Rutas de Ejecución:** Trazado del grafo completo desde la ingesta de PDFs (`generate_golden_draft.py` → `PyMuPDFProvider` → `FlatASTBuilder` → `write_ast_json_atomic`), el sellado de la baseline (`freeze_ground_truth.py` → `SealGroundTruthUseCase`), la generación de candidatos (`CandidateGenerationService`) y la ejecución del benchmark (`TopologyBenchmarkService`).
  * **Verificación de I/O Atómico:** Confirmación de que la persistencia física de oráculos en `infra/fs/ground_truth_store.py` delega a `infra/serialization/ast_json.py`, garantizando atomicidad mediante `tempfile`, `os.fsync` y reemplazo seguro de punteros.

---

### HITO 0.3

#### 1. Auditoría de Firma Criptográfica y Serialización Determinista (Entregable 1)
* **Causa Raíz:** Necesidad de auditar los algoritmos de hashing (`compute_ast_hash`), las políticas de serialización (`json.dumps` determinista) y el manejo de identificadores en `core/ast/hashing.py`, `core/layout/identity.py`, `core/segmenter/` y `tools/evaluation/topology/fingerprint.py` para establecer la definición de Identidad Canónica Inmutable del AST V2.
* **Actividades y Cobertura Ejecutadas:**
  * **Inspección Forense de Mecanismos de Hashing e Identidad:** Traza analítica de la serialización en `compute_ast_hash()`, la generación de IDs en layout (`BlockIdentityGenerator`), la segmentación oracional (`ParagraphSegmenter` / `UUIDIdentityGenerator`), la política de huellas digitales `ASTFingerprintPolicy` y la proyección TeX `RenderUnit`.
  * **Registro de Evidencia Forense Primaria (`E-0.3-001` a `E-0.3-007`):** Mapeo de hallazgos de identidad y serialización sustentados en código real.
  * **Cumplimiento del Marco Read-Only:** Auditoría ejecutada sin modificar código fuente en `core/` ni `infra/`, formalizando la regla de No-Remediación y difiriendo las decisiones de rediseño al Hito 0.5.

#### 2. Taxonomía de Identidad y Genealogía de `node_id` (Entregable 2)
* **Causa Raíz:** Ambigüedad sobre la naturaleza y origen de `node_id` (¿identidad semántica, identidad de instancia física o identificador efímero de runtime?) y su impacto en el determinismo criptográfico del sello.
* **Hallazgos Forenses Clave Registrados:**
  * **Origen Determinista Inicial (`E-0.3-002`):** Se demostró que `node_id` nace determinista en `BlockIdentityGenerator` vía SHA-256 de `(provider, page, native_id, bbox, content)`.
  * **Incompatibilidad en `compute_ast_hash` (`E-0.3-001`, `E-0.3-003` / `GAP-0.3-01`, `GAP-0.3-02`):** Demostración en código de que `compute_ast_hash()` incluye `"node_id": n.node_id` en su serialización JSON. Dado que `ParagraphSegmenter` asigna UUIDs aleatorios v4 (`uuid.uuid4()`) a los fragmentos multi-oracionales, los ASTs segmentados producen firmas SHA-256 **variables e irreproducibles entre ejecuciones**, desacoplando la firma de la Baseline Científica.
  * **Detección de *Contract Drift* en `BoundaryPolicy` (`E-0.3-004` / `GAP-0.3-04`):** Se desmintió la hipótesis de fragmentación en párrafos de 1 sola oración (los cuales conservan su `node_id` determinista). Se identificó una discrepancia entre la documentación del protocolo `BoundaryPolicy` `(0, end_1, ...)` y la implementación real de `ScientificBoundaryPolicy` `(end_1, ...)`.
  * **Identidad Semántica en Benchmark (`E-0.3-006`):** Se constató que `tools/evaluation/topology/fingerprint.py` ignora deliberadamente `node_id` mediante `ASTFingerprintPolicy.semantic_fingerprint` para comparar únicamente la tupla `(node_type, content)`.

#### 3. Modelo Tridimensional de Identidad y Recomendación de Acción (Entregable 3)
* **Causa Raíz:** Incoherencia de diseño entre la firma de oráculo (`compute_ast_hash`) y la comparación de evaluación en el benchmark (`ASTFingerprintPolicy`).
* **Hallazgos Forenses Clave Registrados:**
  * **Modelo Tridimensional de Identidad:** Se formalizó la taxonomía separando:
    1. **Identidad Semántica ($H_{semantic}$):** Basada en tipo, contenido normalizado y secuencia relativa. Inmune a volatilidad técnico-estructural.
    2. **Identidad Física / Runtime ($H_{runtime}$):** Contiene `node_id`, `parent_node_id`, `bboxes` y metadatos de renderizado.
    3. **Identidad de Baseline ($H_{baseline}$):** Firma inmutable global que debe encadenar la versión del corpus, las firmas de PDFs físicos y $H_{semantic}$ del oráculo.
  * **Formalización de Candidatos a Decisión para Hito 0.5:** Definición de `DC-01` (rediseño de `compute_ast_hash`), `DC-03` (fórmula de encadenamiento global $H_{baseline}$), `DC-08` (determinismo de IDs de fragmentos) y `DC-09` (armonización de contrato de `BoundaryPolicy`).

---

### HITO 0.4

#### 1. Auditoría de Fronteras de Capa, Topología y Evaluación (Entregable 1)
* **Causa Raíz:** Necesidad de auditar la integridad estructural, el cumplimiento de los contratos de Arquitectura Limpia, la resiliencia de los algoritmos de maquetación $2\text{D}$, la tubería de compilación y la validez real de las barreras de regresión automatizadas en la suite de pruebas (`tests/`).
* **Actividades y Cobertura Ejecutadas:**
  * **Escrutinio Forense Exhaustivo (Bloques A, C1, C2, C3, C4 y C5):** Auditoría analítica estática sobre el $100\%$ de los módulos de evaluación topológica (`core/benchmark/topology/`), maquetación y perfilado (`core/layout/`, `core/document_profile/`), compilación y renderizado (`core/compiler/`, `apps/compiler/`), serialización (`infra/serialization/ast_json.py`), herramientas CLI (`tools/evaluation/`) y la suite completa de pruebas unitarias y de integración.
  * **Registro de Evidencias y Gaps (`E-0.4-301` a `E-0.4-390`):** Identificación y catalogación de incoherencias de dominio, duplicaciones de código heredado (*legacy*) y vicios formales en las pruebas de regresión.
  * **Gobernanza de Cero Mutación:** Aplicación estricta del marco *Production Read-Only*. Ningún componente fue modificado; todos los hallazgos y reglas normativas (`C2-R01` a `C5-R10`) fueron diferidos como Backlog de Remediación Obligatorio al Hito 0.5 (`UNASSESSED`).

#### 2. Diagnóstico Causal de Fallas de Capa y Testing Tautológico (Entregable 2)
* **Causa Raíz:** Coexistencia parasitaria de componentes heredados (Fases 11/12) con la arquitectura congelada de AST V2 (Fase 16), combinada con parches y *mocks* en la suite de pruebas que generaban una falsa sensación de cobertura.
* **Hallazgos Forenses Clave Registrados:**
  * **Falsas Barreras de Regresión y Tautologías (`GAP-0.4-09` / `E-0.4-322` / `E-0.4-385`):** Se demostró que `test_golden_parser.py` reasigna `expected_fingerprint = current_fingerprint`, forzando una comparación idéntica ($A == A$) que es incapaz de detectar regresiones topológicas. Asimismo, `test_real_parser_pipeline.py` parchea por completo `adapter.parse()`, probando la iteración sobre una lista de *mocks* en lugar del parser real.
  * **Fractura en el Pipeline de Ingesta (`E-0.4-321` / `E-0.4-325`):** Confirmación de que `core/ast/parser.py` y `core/ast/segmenter.py` destruyen el PDF hacia Markdown crudo mediante expresiones regulares planas, salteándose la capa `DocumentLayout` y perdiendo la geometría física (`BoundingBox`), mientras duplican al `FlatASTBuilder` y al `Segmenter V2`.
  * **Violación de Arquitectura Hexagonal y Leaks de Infraestructura (`GAP-0.4-11` / `E-0.4-326`):** Importación directa de la librería de infraestructura `fitz` (PyMuPDF) dentro del dominio (`core/ast/router.py`), junto a la inyección directa de la SDK `groq` en `core/benchmark/semantic_judge.py`.
  * **Falla de Doble Reconstrucción en Compilación (`E-0.4-361` / `E-0.4-362`):** `DocumentAssembler.assemble()` reconstruye el documento pero `CompilationService` descarta el resultado y vuelve a obtener los payloads del repositorio. Ante chunks sin linaje en el AST, el servicio crea silenciosamente nodos sintéticos (`orphan_*`) de tipo `PARAGRAPH` en lugar de aplicar *Fail-Fast* con `ASTConsistencyError`.
  * **Corrupción de Identidad Content-Addressed (`E-0.4-344` / `E-0.4-346`):** `SpatialMerger` modifica el contenido y la BoundingBox de los bloques al fusionarlos, pero conserva el `block_id` original sin recalcular su hash SHA-256.
  * **Ausencia de Canalización de CI/CD (`GAP-C5-05` / `E-0.4-390`):** Inexistencia del directorio `.github/workflows/` y de `pyproject.toml` en el repositorio, lo que implica la ausencia de puertas de enlace automatizadas (*Required Status Checks*) que bloqueen el *merge* remoto ante fallos.

#### 3. Grafo de Integración Canónico y Reestructuración de Capas (Entregable 3)
* **Causa Raíz:** Falta de unificación en la cadena de autoridad que va desde la ingesta de PDFs hasta la generación de artefactos y la protección en CI.
* **Hallazgos Forenses Clave Registrados:**
  * **Identificación del Núcleo SOTA Intacto:** Rescate y preservación de la arquitectura de dominio madura: `FlatASTBuilder`, `CrossPageNormalizer`, `PolymorphicValidationEngine` (`core/validation/ast/`), `Topology Benchmark Engine` (`ZhangShashaEngine`, `PostorderIndex`), `DocumentAssembler` y la serialización atómica en disco con `fsync` (`infra/serialization/ast_json.py`).
  * **Unificación de la Canalización de la Fase 17:** Definición del flujo canónico estricto: $\text{PDF} \rightarrow \text{ExtractionProvider} \rightarrow \text{DocumentLayout} \rightarrow \text{DocumentLayoutValidator} \rightarrow \text{FlatASTBuilder} \rightarrow \text{AST V2} \rightarrow \text{Segmenter V2 / Validation V2} \rightarrow \text{DocumentAssembler} \rightarrow \text{CompilationService} \rightarrow \text{TectonicRunner}$.
  * **Diseño del Regression Gate de Integración Continua:** Articulación de la cadena de autoridad para la Fase 17_BIS: $\text{Corpus Canónico} \rightarrow \text{Sealed Ground Truth} \rightarrow \text{Fingerprint Policy} \rightarrow \text{Pytest Assertion Gate} \rightarrow \text{GitHub Actions Workflow} \rightarrow \text{Merge Protection}$.

#### 4. Matriz de Cobertura Arquitectónica y Re-Scoping de Producción (Entregable 4)
* **Causa Raíz:** Descubrimiento epistemológico crítico: la auditoría previa (C1 a C5) cubrió exhaustivamente el arnés de evaluación (*Benchmark* y *Regression*), pero **omitió la arquitectura real de producción**. El éxito en el benchmark no garantiza la integridad transaccional del pipeline de runtime.
* **Hallazgos Forenses Clave Registrados:**
  * **Falsa Equivalencia de Cobertura:** Se determinó que evaluar el Benchmark $\neq$ evaluar el Pipeline Real. Subsistemas masivos (`core/pipeline`, `core/healing`, `apps/llm_workers`, `core/execution`, `infra/db`) operan fuera del alcance del benchmark topológico y permanecen inauditados.
  * **Resolución de Solapamiento Benchmark/Regresión:** Se validó que no existe duplicación. `StructuralTopologyMetric` (Benchmark) evalúa "cuál extractor es mejor" calculando distancias (TED), mientras que `ASTFingerprintPolicy` (Regresión) evalúa "si el comportamiento cambió" mediante huellas digitales binarias (Pass/Fail). Son funciones ortogonales y necesarias.
  * **Expansión Obligatoria del Alcance:** Se formalizó la apertura de una segunda campaña de auditoría dividida en 9 bloques de producción (`0.4.4-P1` a `0.4.4-P9`), abarcando desde `Extraction + Physical Layout` hasta `FSM + CQRS + Recovery` y la reconciliación final *End-to-End*.

---

### HITO 0.4.5

#### 1. Auditoría de la Canalización de Producción y Raíz de Composición (Entregables 0.4.5-1 y 0.4.5-2)
* **Causa Raíz:** Necesidad de verificar si la canalización transaccional de producción real ($\text{PDF} \rightarrow \dots \rightarrow \text{Artefacto}$) ejecuta los componentes de dominio estabilizados o si incurre en *bypasses*, duplicaciones de motores, orquestadores paralelos y módulos zombis.
* **Actividades y Cobertura Ejecutadas:**
  * **Escrutinio Forense Exhaustivo (Bloques P1 a P7):** Auditoría analítica y forense sobre el $100\%$ de la superficie productiva real: composición (`apps/bootstrap/`), ingesta física y layout (`core/extraction/`, `infra/adapters/`), AST/normalización/segmentación/chunking (`core/ast/`, `core/segmenter/`, `core/routing/`), despacho/FinOps/resiliencia (`apps/llm_workers/`, `core/resilience/`), validación/healing (`core/validation/`, `core/healing/`), compilación/TeX (`core/compiler/`, `apps/compiler/`) y gobernanza runtime/FSM/CQRS (`core/execution/`, `infra/db/`, `runtime/`).
  * **Emisión del Informe MAESTRO Integrado:** Generación de `HITO_0.4.5_FINAL_INTEGRATED_REPORT.md` articulando los 4 entregables requeridos: *Production Pipeline Forensic Report*, *Production Composition Map*, *Production Evidence Matrix* y *Benchmark vs Production Boundary Map*.
  * **Gobernanza de Cero Mutación:** Aplicación estricta de la política *Production Read-Only*. Ningún componente fue modificado en producción; todos los hallazgos y reglas normativas (`P1-R01` a `P7-R05`) fueron congelados en el Backlog de Remediación Obligatorio diferido al Hito 0.5 (`UNASSESSED`).

#### 2. Diagnóstico Causal de Bypasses, Módulos Zombis y Ruptura de Runtime (Entregable 0.4.5-3)
* **Causa Raíz:** Cisma entre el diseño teórico de Clean Architecture y la ejecución física en tiempo de ejecución, provocando que la canalización real salte módulos de grado científico en favor de atajos procedimentales y wrappers de infraestructura.
* **Hallazgos Forenses Clave Registrados:**
  * **Bypass de Layout, Segmentación y Enrutamiento (`P2-P3`):** Bypassing total de `DocumentLayoutBuilder`, `Segmenter V2` (`core/segmenter/*`) y `RoutingWorkflow` (`core/routing/*`), los cuales son $100\%$ zombis en producción. Párrafos densos viajan sin segmentar y sin filtrado de canales (`TRANSLATE`, `PASSTHROUGH`, `OMIT`).
  * **Contaminación Ontológica en Chunking (`P3`):** La capa POO `core/chunking/` está omitida. La lógica de empaquetado de unidades para LLM vive por contaminación dentro de `build_semantic_chunks_as_units()` en `core/ast/hashing.py`.
  * **Bipolaridad Operacional y Desconexión de Resiliencia (`P4`):** Ejecución in-process en CLI frente a ejecuciones distribuidas en daemons. `GlobalCircuitBreaker` está $100\%$ zombi. `QuotaManager` opera solo en RAM local (inviable en cluster). `FastWordEstimator` subestima tokens en LaTeX en un orden de magnitud (causando `ContextOverflowError`). `DummyContextResolver` envenena la caché SQLite.
  * **Orfandad Pre-LLM y Revalidación Redundante (`P5`):** `PolymorphicValidationEngine` está $100\%$ zombi. Sin embargo, la validación Post-LLM y el `HealingPipeline` demostraron un comportamiento SOTA con *rollback* atómico verificado y aborto estricto de documentos ante fallas no degradables (`VALIDATION_FAILURE`).
  * **Bypass de Compilación e Inseguridad Concurrente (`P6`):** `AssemblerWorkerDaemon` se salta `CompilationService` y `DocumentAssembler` oficiales, reconstruyendo fragmentos ad-hoc desde SQLite. `DockerRunner` no ejecuta Docker (invoca Tectonic local) y escribe en `os.getcwd()`, creando *race conditions*. `LatexEscaper` es ciego al contexto y corrompe comandos TeX válidos.
  * **Gobernanza FSM SOTA vs. Inactivación CQRS (`P7`):** El repositorio FSM garantiza exclusión mutua mediante Compare-And-Swap (CAS) con `state_version`. No obstante, `FSMStateStore` forja comandos de compilación fantasma, `CQRSReconciliationDaemon` está desactivado por bandera (`EXPERIMENTAL_ENABLED = False`) y la rematerialización WAL inyecta `"unknown_ast_hash"` estancando documentos en `PROCESSING`.

#### 3. Mapeo de la Frontera Benchmark vs. Producción (Entregable 0.4.5-4)
* **Causa Raíz:** Desconexión metodológica donde el laboratorio de evaluación (Benchmark) medía un pipeline sintético legacy que no reflejaba la realidad física del producto.
* **Hallazgos Forenses Clave Registrados:**
  * **Ruta Paralela Tóxica:** `core/benchmark/__main__.py` utilizaba `core/ast/parser.py` (parser legacy basado en Regex Markdown) en vez de `PdfParserAdapter` $\rightarrow$ `FlatASTBuilder` (AST V2 de producción), viciando las métricas históricas de laboratorio.
  * **Esquiva de Fragilidad Criptográfica:** El benchmark de `tools/evaluation/` utilizaba `ASTFingerprintPolicy.semantic_fingerprint()` ignorando `node_id`, ocultando el bug de `compute_ast_hash()` que incluye `node_id`s efímeros y rompe el determinismo en el orquestador real.
  * **Mandato de Remediación:** Se establece la exigencia normativa de reorientar el Benchmark para que consuma exclusivamente la salida de la ingesta de producción (`PdfParserAdapter` $\rightarrow$ `FlatASTBuilder`), eliminando `core/ast/parser.py`.

#### 4. Raíz de Composición Dividida y Violaciones Hexagonales
* **Causa Raíz:** Falta de unificación en the Composition Root y acoplamiento directo de infraestructura en clases de aplicación.
* **Hallazgos Forenses Clave Registrados:**
  * **Split Composition Root:** `apps/bootstrap/pipeline_factory.py` relaja tipados (`dispatcher: Any`) y muta atributos post-instanciación, mientras `apps/cli/main.py` asume manualmente la construcción de la pila de LLMs.
  * **Fuga Hexagonal Directa:** `core/pipeline/state_store.py` (dentro de `core/`) importa directamente `FSMRepository` de `infra/db/`, violando Clean Architecture.
  * **Leak de Infraestructura en Dominio:** `core/ast/router.py` importa la librería C/Python `fitz` (PyMuPDF) directamente dentro del dominio.

---

### HITO 0.5: Decision Consolidation & Architecture Freeze

#### 1. Formulación del Marco de Gobernanza (Architecture Governance Framework)
* **Causa Raíz:** Necesidad de transicionar del descubrimiento (evidencia) a la acción (implementación) sin perder la trazabilidad de las decisiones arquitectónicas ni generar deuda técnica por improvisación.
* **Resultados Consolidados:**
  * **NADR-01 a NADR-11:** Se promulgaron 11 *Normative Architecture Decision Records* que resuelven definitivamente los candidatos DC-01 a DC-11 basándose en la evidencia forense recopilada. Estos documentos actúan como leyes inmutables para la reconstrucción del código.
  * **Enmienda del ADR Maestro:** Se actualizó el `ADR F17_BIS` reconociendo la "Ilusión del Benchmark" e integrando el saneamiento del pipeline de producción (*Production Pipeline Alignment*) como prerrequisito innegociable.
  * **Plan de Ejecución Operativa:** Se materializó el `PHASE_17BIS_EXECUTION_PLAN.md` que orquesta la remediación en *Phase Gates* y *Waves*, subordinando la planificación a la gobernanza dictada por los NADRs.

#### 2. Declaración de Cierre y Congelamiento
* **Resolución de Dependencias:** El 100% de la superficie de código (evaluación y producción) fue auditada. Las contradicciones estructurales entre la teoría (diseño) y la práctica (runtime) han sido expuestas y asignadas a una ruta normativa de resolución.
* **Veredicto Arquitectónico Final:**
  * **HITO 0.5: `CLOSED & FROZEN`**.
  * **FASE 0 (Architecture & Baseline Audit Gate): `COMPLETADA`**. El repositorio abandona el estado de "Solo Lectura" (Read-Only). 
  * El equipo de ingeniería queda oficialmente autorizado para iniciar la escritura de código productivo correspondiente a la Fase 1, Wave 1, Task 1.1.1.

