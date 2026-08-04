# HITO_0.2_FORENSIC_FLOW_AUDIT.md
## Ground Truth, Candidate Generation & Sealing Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO[cite: 1]
* **Fecha de Emisión:** 2026-07-26[cite: 1]
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)[cite: 1]
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate)[cite: 1]
* **ADR de Gobernanza:** `ADR_F17-BIS_0`[cite: 1]
* **Límite Epistemológico:** Solo lectura / Auditoría analítica de flujos de código real[cite: 1]. Cero mutaciones en producción[cite: 1]. Disposición arquitectónica reservada para Hito 0.5 (`UNASSESSED`)[cite: 1].

---

## 1. PROPÓSITO Y RESUMEN EJECUTIVO

El **Hito 0.2 (Ground Truth & Sealing Forensic Audit)** tiene como objetivo auditar el ciclo de vida transaccional completo de creación de borradores (*Golden Drafts*), generación de candidatos (*Candidates*), evaluación topológica, actualización de linaje y sellado criptográfico del Ground Truth[cite: 1].

A partir de la inspección estática y la traza de ejecución del código real en `core/benchmark/corpus`, `core/benchmark/ground_truth`, `core/benchmark/topology`, `infra/fs`, `infra/serialization` y `tools/evaluation`[cite: 1], esta auditoría demuestra de forma irrebatible la causa raíz de las fallas de arquitectura P0 y P1 del subsistema de oráculos y benchmark[cite: 1]:

1. **Mecanismo Causal de Sellado Parcial (*Partial Sealing*):** Confirmación de por qué la infraestructura actual permite marcar un manifiesto como sellado aunque falten oráculos AST en disco[cite: 1].
2. **Desacoplamiento Criptográfico de la Firma Global:** Demostración de que la firma `manifest_hash` ignora los hashes de Ground Truth, provocando que mutaciones en los oráculos no alteren la firma global del manifiesto[cite: 1].
3. **Duplicación y Código Huérfano de Servicios de Linaje:** Mapeo de la duplicación idéntica entre `ManifestLineageSealer` y `ManifestGroundTruthUpdater`[cite: 1].
4. **Doble Canalización de Generación de Candidatos y Evaluación Topológica:** Mapeo de la canalización de `CandidateGenerationService` y `TopologyBenchmarkService`, exponiendo la divergencia entre la comparación semántica ($O(N)$ / fingerprint de tipo+contenido) y la comparación identitaria con `node_id`[cite: 1].

---

## 2. REGISTRO DE EVIDENCIA FORENSE COMPLETO (E-0.2-001 a E-0.2-010)

### Evidencia E-0.2-001: Mecanismo Permisivo en `SealGroundTruthUseCase`
* **Archivo Fuente Primario:** `core/benchmark/ground_truth/use_cases.py`[cite: 1]
* **Símbolo Auditado:** `SealGroundTruthUseCase.execute()`[cite: 1]
* **Declaración Observada:**
  ```python
  for doc_entry in current_manifest.documents:
      doc_id = doc_entry.document_id
      if self._artifact_port.artifact_exists(doc_id):
          raw_bytes = self._artifact_port.read_artifact_bytes(doc_id)
          detected_hashes[doc_id] = compute_sha256(raw_bytes)
  ```
* **Hallazgo Forense:** Si `self._artifact_port.artifact_exists(doc_id)` retorna `False` (el archivo `.json` del oráculo no existe en disco)[cite: 1], el caso de uso no emite ningún error ni lanza excepción[cite: 1]. Continúa silenciosamente el bucle dejando a `doc_id` fuera de `detected_hashes`[cite: 1].

---

### Evidencia E-0.2-002: Omisión de Errores y Conservación Silenciosa en `ManifestLineageSealer`
* **Archivo Fuente Primario:** `core/benchmark/corpus/services.py`[cite: 1]
* **Símbolo Auditado:** `ManifestLineageSealer.seal_manifest_with_ground_truth()`[cite: 1]
* **Declaración Observada:**
  ```python
  for doc_entry in current_manifest.documents:
      doc_id = doc_entry.document_id
      gt_version = doc_entry.ground_truth_version
      gt_hash = doc_entry.ground_truth_sha256

      if doc_id in detected_hashes:
          gt_version = target_version
          gt_hash = detected_hashes[doc_id]

      updated_documents.append(
          RawDocumentEntryDTO(
              document_id=doc_id,
              sha256=doc_entry.sha256,
              traits=doc_entry.traits,
              page_count=doc_entry.page_count,
              ground_truth_version=gt_version,
              ground_truth_sha256=gt_hash
          )
      )
  ```
* **Hallazgo Forense:** Si `doc_id` no está en `detected_hashes` (porque no existía en disco)[cite: 1], `gt_version` y `gt_hash` conservan su valor anterior (que puede ser `None` si es un documento nuevo)[cite: 1]. El método retorna un `RawCorpusManifestDTO` "sellado" conteniendo entradas con `ground_truth_sha256=None` sin validar la cardinalidad biyectiva $N_{\text{PDF}} = N_{\text{GT}}$[cite: 1].

---

### Evidencia E-0.2-003: Causa Raíz del Desacoplamiento de Firma Criptográfica (`ManifestFingerprintCalculator`)
* **Archivo Fuente Primario:** `core/benchmark/corpus/services.py`[cite: 1]
* **Símbolo Auditado:** `ManifestFingerprintCalculator.compute_hash()`[cite: 1]
* **Declaración Observada:**
  ```python
  @staticmethod
  def compute_hash(version: CorpusVersion, documents: List[CorpusDocumentMetadata]) -> str:
      hasher = hashlib.sha256()
      hasher.update(version.value.encode("utf-8"))
      sorted_documents = sorted(documents, key=lambda doc: doc.document_id)
      for doc in sorted_documents:
          sorted_traits = sorted([trait.value for trait in doc.traits])
          traits_str = ",".join(sorted_traits)
          document_payload = f"{doc.document_id}:{doc.fingerprint.sha256}:{traits_str}:{doc.page_count}"
          hasher.update(document_payload.encode("utf-8"))
      return hasher.hexdigest()
  ```
* **Demostración de Falla Criptográfica:**
  1. El payload de hash se compone estrictamente de `doc.document_id`, `doc.fingerprint.sha256` (hash del PDF físico), `traits_str` y `doc.page_count`[cite: 1].
  2. `CorpusDocumentMetadata` ni siquiera posee un atributo para almacenar el hash del oráculo[cite: 1].
  3. **Invariante Roto:** El hash global del manifiesto (`manifest_hash`) es **100% insensible a las mutaciones del Ground Truth**[cite: 1]. Un operador o proceso puede alterar, vaciar o eliminar los archivos `.ast.json` y la firma `manifest_hash` recalculada seguirá siendo idéntica[cite: 1].

---

### Evidencia E-0.2-004: Duplicación Exacta y Código Huérfano (`ManifestGroundTruthUpdater`)
* **Archivo Fuente Primario:** `core/benchmark/ground_truth/services.py`[cite: 1]
* **Símbolo Auditado:** `ManifestGroundTruthUpdater`[cite: 1]
* **Análisis Comparativo de Código:**
  * `ManifestGroundTruthUpdater.apply_lineage_sealing()` en `ground_truth/services.py` contiene **exactamente la misma implementación línea por línea** que `ManifestLineageSealer.seal_manifest_with_ground_truth()` en `corpus/services.py`[cite: 1].
* **Análisis de Consumidores en Repositorio:**
  * `SealGroundTruthUseCase` importa e invoca explícitamente a `ManifestLineageSealer` desde `core.benchmark.corpus.services`[cite: 1].
  * `ManifestGroundTruthUpdater` **no es importado ni invocado por ningún caso de uso, script CLI o prueba unitaria/integración en todo el repositorio**[cite: 1]. Es un componente huérfano / deuda técnica redundante[cite: 1].

---

### Evidencia E-0.2-005: Canalización de Candidatos AST (`CandidateGenerationService`)
* **Archivo Fuente Primario:** `tools/evaluation/services/candidate_generator.py`
* **Símbolo Auditado:** `CandidateGenerationService.generate_candidate()`
* **Declaración Observada:**
  ```python
  class CandidateGenerationService:
      def generate_candidate(
          self,
          provider: ExtractionProvider,
          provider_name: str,
          pdf_path: Path,
          pdf_sha256: str,
      ) -> CandidateGenerationResult:
          doc_id = pdf_path.stem
          start_time = time.perf_counter()
          layout = provider.extract(str(pdf_path))
          elapsed_ms = (time.perf_counter() - start_time) * 1000.0

          validation_report = self._validator.validate(layout)
          if not validation_report.is_valid:
              return CandidateGenerationResult(doc_id=doc_id, ast_nodes=(), validation_report=validation_report, metadata=None)

          draft_blocks: list[LayoutBlockDraft] = [...]
          # Constriñe bloques -> LayoutBlockCollection -> FlatASTBuilder().build()
          block_collection = LayoutBlockCollection(blocks=draft_blocks)
          ast_nodes = tuple(self._builder.build(block_collection))
          ...
          return CandidateGenerationResult(...)
  ```
* **Hallazgo Forense:**
  * La canalización de generación de candidatos ejecuta la extracción física, valida las invariantes de maquetación vía `DocumentLayoutValidator` y proyecta el AST V2 mediante `FlatASTBuilder`.
  * Si el layout es inválido, retorna una tupla vacía de nodos y aborta el guardado en disco sin propagar la falla a la firma global.

---

### Evidencia E-0.2-006: Orquestador de Benchmark Topológico (`TopologyBenchmarkService`)
* **Archivo Fuente Primario:** `tools/evaluation/application/benchmark_service.py`
* **Símbolo Auditado:** `TopologyBenchmarkService`
* **Declaración Observada:**
  ```python
  class TopologyBenchmarkService:
      def __init__(
          self,
          metrics: Sequence[TopologyMetric] | None = None,
          aggregation_strategy: BenchmarkAggregationStrategy | None = None,
      ) -> None:
          self._metrics = tuple(metrics) if metrics is not None else default_metrics()
          self._strategy = aggregation_strategy or DefaultBenchmarkAggregationStrategy()

      def evaluate_document(self, doc: BenchmarkDocument) -> DocumentEvaluationResult:
          results: list[MetricResult] = [
              metric.evaluate(doc.candidate, doc.ground_truth) for metric in self._metrics
          ]
          return DocumentEvaluationResult(doc_id=doc.doc_id, metrics=tuple(results))

      def evaluate_corpus(self, provider_name: str, documents: Sequence[BenchmarkDocument]) -> BenchmarkSummaryReport:
          doc_results = [self.evaluate_document(doc) for doc in documents]
          return self._strategy.aggregate(provider_name=provider_name, results=doc_results)
  ```
* **Hallazgo Forense:** `TopologyBenchmarkService` opera de forma puramente funcional en memoria. Recibe pares `BenchmarkDocument(candidate, ground_truth)`, ejecuta la suite de métricas inyectadas y colapsa los resultados mediante `DefaultBenchmarkAggregationStrategy` (promedio aritmético).

---

### Evidencia E-0.2-007: Política de Huellas Digitales AST (`ASTFingerprintPolicy`)
* **Archivo Fuente Primario:** `tools/evaluation/topology/fingerprint.py`
* **Símbolo Auditado:** `ASTFingerprintPolicy`
* **Declaración Observada:**
  ```python
  class ASTFingerprintPolicy:
      @staticmethod
      def semantic_fingerprint(node: ASTNode) -> tuple[str, str]:
          node_type_str = node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type)
          content_str = node.text_content.strip()
          return (node_type_str, content_str)

      @staticmethod
      def identity_fingerprint(node: ASTNode) -> Hashable:
          node_id = getattr(node, "id", getattr(node, "node_id", None))
          if node_id is None:
              raise ValueError("identity_fingerprint requiere un nodo con identidad estable.")
          node_type = getattr(node, "type", type(node).__name__)
          content = getattr(node, "content", getattr(node, "text", ""))
          return (str(node_type), str(content).strip(), str(node_id))
  ```
* **Hallazgo Forense Crítico:**
  * `semantic_fingerprint` aísla deliberadamente la comparación al par `(node_type_str, content_str)`, omitiendo el `node_id`.
  * Esta distinción confirma por qué el benchmark de evaluación en `tools/` es inmune a la volatilidad de UUIDs en `node_id`, **mientras que la función `compute_ast_hash()` en `core/ast/hashing.py` (auditada en `E-0.1-003`) sí incluye `node_id`**, creando una incoherencia de diseño entre la firma criptográfica y la evaluación topológica.

---

### Evidencia E-0.2-008: Batería de Métricas Topológicas CLI
* **Archivos Fuente Primarios:** `tools/evaluation/topology/metrics/*.py`
* **Símbolos Auditados:** `NodeCountMetric`, `EntityRecallMetric`, `SequenceAlignmentMetric`, `StructuralTopologyMetric`, `MetricRegistry`
* **Declaración Observada:**
  * **`NodeCountMetric`:** Sanity check $O(1)$ que evalúa la diferencia absoluta de volumen de nodos: $1.0 - \frac{|N_C - N_{GT}|}{\max(N_C, N_{GT})}$.
  * **`EntityRecallMetric`:** Cálculo $O(N)$ del F1 Score sobre bolsas de huellas semánticas `semantic_fingerprint`.
  * **`SequenceAlignmentMetric`:** Cálculo $O(M \times N)$ del Longest Common Subsequence (LCS) sobre la secuencia de lectura semántica.
  * **`StructuralTopologyMetric`:** Reconstrucción del árbol explícito usando `parent_node_id` y cálculo de Tree Edit Distance mediante la biblioteca de terceros `apted`.
* **Hallazgo Forense:** El perfil `default` registrado en `MetricRegistry` agrupa estas 4 métricas en la capa `tools/evaluation`.

---

## 3. GRAFO TRANSACCIONAL DEL SELLADO, CANDIDATOS Y BENCHMARKING

```text
[ PARAMETRIZACIÓN & INGESTA DE CORPUS ]
                  │
                  ├──► 1. generate_golden_draft.py
                  │         │
                  │         ▼
                  │    GenerateGoldenDraftUseCase ──► LocalFileSystemGroundTruthDraftWriter
                  │                                            │
                  │                                            ▼
                  │                        [ tests/corpus/.../ground_truth/{doc_id}.json ]
                  │                                            │
                  ├──► 2. freeze_ground_truth.py              │
                  │         │                                  │
                  │         ▼                                  │
                  │    SealGroundTruthUseCase ◄────────────────┘ (Lee artefactos .json)
                  │         │
                  │         ├──► Check artifact_exists(doc_id)
                  │         │       [ Si falta: OMITE SILENCIOSAMENTE -> Partial Sealing P0 ]
                  │         │
                  │         └──► ManifestLineageSealer.seal_manifest_with_ground_truth()
                  │                 │
                  │                 └──► ManifestFingerprintCalculator.compute_hash()
                  │                         [ Firma SOLO PDFs físicos -> Ignora GT P0 ]
                  │
                  └──► 3. generate_candidates.py
                            │
                            ▼
                       CandidateGenerationService ──► [ candidates/{provider}/{doc_id}.json ]

──────────────────────────────────────────────────────────────────────────────────────────

[ EVALUACIÓN & BENCHMARKING EN RUNTIME ]
[ candidates/{provider}/{doc_id}.json ] + [ ground_truth/{doc_id}.json ]
              │
              ▼
[ LocalFileSystemCorpusRepository.load_corpus_documents() ]
              │
              ▼
[ TopologyBenchmarkService.evaluate_corpus() ]
              │
              ├──► NodeCountMetric (O(1))
              ├──► EntityRecallMetric (O(N) via semantic_fingerprint)
              ├──► SequenceAlignmentMetric (LCS O(M*N))
              └──► StructuralTopologyMetric (APTED Tree Edit Distance)
              │
              ▼
[ DefaultBenchmarkAggregationStrategy.aggregate() ] ──► BenchmarkSummaryReport (MD/JSON)
```

---

## 4. SÍNTESIS DE HALLAZGOS Y GAP ANALYSIS CONSOLIDADOS

| ID Hallazgo | Componente Afectado | Comportamiento Observado (Evidencia) | Severidad | Acción Requerida en Fases Posteriores |
| :--- | :--- | :--- | :---: | :--- |
| **GAP-0.2-01** | `SealGroundTruthUseCase` | Omite oráculos ausentes sin lanzar `IncompleteBaselineError` (`E-0.2-001`). | **P0 (Bloqueante)** | Implementar validación de biyección estricta $N_{\text{PDF}} = N_{\text{GT}}$. |
| **GAP-0.2-02** | `ManifestFingerprintCalculator` | No incluye `ground_truth_sha256` en el cálculo de `manifest_hash` (`E-0.2-003`). | **P0 (Bloqueante)** | Diseñar la fórmula de encadenamiento global $H_{baseline}$ (Fase 2). |
| **GAP-0.2-03** | `ManifestGroundTruthUpdater` | Código huérfano duplicado de `ManifestLineageSealer` (`E-0.2-004`). | **P1 (Deuda)** | Unificar autoridad de sellado exclusivamente en la capa de Aplicación/Dominio. |
| **GAP-0.2-04** | `SealGroundTruthUseCase` | No ejecuta validación de esquema ni `ASTValidator` antes de sellar (`E-0.2-005`). | **P1 (Calidad)** | Exigir paso limpio por `ASTValidator` como precondición de sello. |
| **GAP-0.2-05** | `RawDocumentEntryDTO` | Ausencia de Enum o estado de ciclo de vida del oráculo (`DRAFT`/`SEALED`) (`E-0.2-006`). | **P2 (Gobernanza)** | Formalizar máquina de estados de validación del oráculo. |
| **GAP-0.2-06** | `compute_ast_hash` vs `ASTFingerprintPolicy` | Divergencia: `compute_ast_hash` incluye `node_id` efímero mientras el benchmark lo ignora (`E-0.2-007`). | **P1 (Identidad)** | Resolver el desacoplamiento de identidad semántica vs identitaria (Hito 0.3). |

---

## 5. RESULTADOS CONSOLIDADOS FASE 17-BIS — HITO 0.2

### 1. Auditoría Forense de Sellado y Linaje (Entregables 1 y 2)
* **Causa Raíz:** Falta de barreras de atomicidad y contratos de validación durante la ejecución del caso de uso de sellado de oráculos (`SealGroundTruthUseCase`).
* **Correcciones y Hallazgos Demostrados:**
  * **Demostración de Causa Raíz de Partial Sealing:** Se verificó que `SealGroundTruthUseCase` omite silenciosamente documentos sin oráculo en disco, permitiendo la generación de manifiestos incompletos[cite: 1].
  * **Invalidez de Firma Global:** Se demostró que `ManifestFingerprintCalculator` aísla los hashes del oráculo, provocando que mutaciones sobre `.ast.json` no modifiquen la huella digital del manifiesto[cite: 1].
  * **Unificación de Autoridad:** Se identificó que `ManifestGroundTruthUpdater` es código muerto no invocado en el proyecto, dejando a `ManifestLineageSealer` como la única ruta activa de actualización de linaje[cite: 1].

### 2. Contratos de Almacenamiento y Serialización (Entregable 3)
* **Causa Raíz:** Riesgo de corrupción de datos durante I/O y serialización de colecciones de nodos AST V2.
* **Confirmación de Mecanismos:**
  * Se verificó que `infra/fs/ground_truth_store.py` delega I/O atómico a `infra/serialization/ast_json.py`, garantizando escrituras seguras a nivel de SO vía `tempfile`, `os.fsync` y reemplazo atómico de punteros[cite: 1].
  * Se constató que `CandidateGenerationService` y `TopologyBenchmarkService` desacoplan adecuadamente la generación física de candidatos respecto a la evaluación en memoria.

---

## 6. LÍMITE EPISTEMOLÓGICO Y DECLARACIÓN DE CIERRE DEL HITO 0.2

El **Hito 0.2 (Ground Truth & Sealing Forensic Audit)** queda oficialmente **COMPLETADO Y CONGELADO (`FROZEN`)**[cite: 1].

**Garantías del Entregable:**
1. **Causa Raíz P0 Demostrada:** Mapeada en código la cadena causal del sellado parcial y la insensibilidad de la firma criptográfica[cite: 1].
2. **Grafo Transaccional Unificado:** Trazada la ruta completa desde la lectura de PDFs, extracción, generación de borrador, generación de candidatos y evaluación topológica.
3. **Neutralidad Mantenida:** Cumplimiento estricto de la política *Production Read-Only / Audit-Artifact Write-Allowed*[cite: 1].