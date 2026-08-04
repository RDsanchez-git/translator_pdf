# HITO_0.1_REPOSITORY_ARCHITECTURE_INVENTORY.md
## Baseline Audit & Architecture Discovery — Documento de Evidencia Primaria

* **Estado:** FROZEN / CONGELADO
* **Fecha de Emisión:** 2026-07-26
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Solo lectura / Observación de código primario. Cero decisiones de conservación o reemplazo (`UNASSESSED` hasta Hito 0.5).

---

## 1. PROPÓSITO Y METODOLOGÍA

Este documento actúa como el registro oficial de evidencia primaria para el **Hito 0.1 (Repository & Architecture Inventory)**. Su objetivo es mapear las estructuras, tipos, protocolos, firmas y dependencias reales observadas en el código fuente del repositorio, eliminando suposiciones y aislando los límites de la Baseline Científica Inmutable.

Cada entrada se sustenta en firmas y declaraciones de código analizadas estáticamente, asignando un identificador unívoco de evidencia (`E-0.1-XXX`) o de observación abierta (`OBS-0.1-XXX`).

---

## 2. REGISTRO DE EVIDENCIA PRIMARIA

### A. Subdominio `core/ast/`

#### Evidencia E-0.1-001: Mapeo de Ontología de Nodos y Tipología
* **Archivo Fuente Primario:** `core/ast/enums.py`
* **Símbolos Auditados:** `ContentNodeType`, `TranslationStrategy`, `HeadingLevel`, `SemanticOrigin`
* **Declaración Observada:**
  ```python
  class ContentNodeType(str, Enum):
      COMPOSITE_BLOCK = "composite_block"
      HEADING = "heading"
      PARAGRAPH = "paragraph"
      DISPLAY_EQUATION = "display_equation"
      INLINE_EQUATION = "inline_equation"
      TABLE_SIMPLE = "table_simple"
      TABLE_COMPLEX = "table_complex"
      IMAGE = "image"
      CAPTION = "caption"
      CODE = "code"
      LIST = "list"

  class TranslationStrategy(str, Enum):
      TRANSLATE = "translate"
      PASSTHROUGH = "passthrough"
      KEEP_ORIGINAL = "keep_original"
      OMIT = "omit"
      DEFER = "defer"
  ```
* **Análisis de Hallazgos:**
  * `ContentNodeType` establece 11 tipos semánticos puros para la representación plana del AST V2.
  * Ninguno de los enums declara atributos de severidad o criticidad de regresión (`CRITICAL`, `WARNING`, `INFO`).
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`. Se eleva a Hito 0.4 / DC-06 para evaluar la necesidad de la matriz `NodeCriticality`.

---

#### Evidencia E-0.1-002: Estructura del Aggregate `ASTNode` y Payloads
* **Archivo Fuente Primario:** `core/ast/models.py`
* **Símbolos Auditados:** `ASTNode`, `NodeMetadata`, Payloads (`HeadingPayload`, `ParagraphPayload`, `MathPayload`, `CodePayload`, `TablePayload`, `ImagePayload`, `ListPayload`)
* **Declaración Observada:**
  ```python
  class ASTNode(BaseModel):
      model_config = ConfigDict(frozen=True)
      node_id: str
      sequence_id: int = -1
      node_type: ContentNodeType
      strategy: TranslationStrategy = TranslationStrategy.TRANSLATE
      metadata: NodeMetadata = Field(default_factory=lambda: NodeMetadata())
      depth: int = 0
      payload: ASTPayload
      
      control_plane: Dict[str, Any] = Field(default_factory=dict)
      parent_node_id: Optional[str] = None
      segment_index: int = 0
      segment_count: int = 1
  ```
* **Análisis de Hallazgos:**
  * `ASTNode` es inmutable (`frozen=True`).
  * Contiene campos identitarios (`node_id`, `sequence_id`, `parent_node_id`) y de trazabilidad espacial (`metadata.bboxes`, `metadata.pages`).
  * La discriminación de payloads se ejecuta determinísticamente mediante `@model_validator(mode="before") _discriminate_payload`.
  * La fachada de texto `text_content` extrae de forma segura el atributo `content` del payload activo.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-003: Algoritmo de Hashing de Árbol (`compute_ast_hash`)
* **Archivo Fuente Primario:** `core/ast/hashing.py`
* **Símbolo Auditado:** `compute_ast_hash(ast: List[ASTNode]) -> str`
* **Declaración Observada:**
  ```python
  def compute_ast_hash(ast: List[ASTNode]) -> str:
      """SOTA: Generación determinística de firma para el árbol sintáctico completo."""
      def serialize_node(n: ASTNode) -> dict:
          type_str = n.node_type.value if hasattr(n.node_type, "value") else str(n.node_type)
          return {
              "node_id": n.node_id,
              "type": type_str,
              "content": n.text_content,
              "latex": getattr(n, "latex", None),
              "children": [serialize_node(c) for c in getattr(n, "children", [])] if getattr(n, "children", None) else []
          }
          
      raw = json.dumps(
          [serialize_node(n) for n in ast], 
          sort_keys=True,
          ensure_ascii=False,
          separators=(",", ":")
      )
      return hashlib.sha256(raw.encode("utf-8")).hexdigest()
  ```
* **Hallazgo Crítico de Auditoría Forense:**
  * La función interna `serialize_node` incluye explícitamente el atributo `node_id` en el diccionario que se serializa a JSON.
  * **Implicación Criptográfica:** Si el pipeline de extracción genera `node_id` efímeros o no deterministas (por ejemplo UUIDs generados al vuelo en cada ejecución), dos árboles AST con contenido semántico, secuencia y tipos 100% idénticos producirán valores de `compute_ast_hash` **diferentes**.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (COMPORTAMIENTO OBSERVADO)`
  * Disposición Arquitectónica: `UNASSESSED`. Insumo de alta prioridad para la auditoría de identidad en Hito 0.3 / DC-03 y DC-13.

---

#### Evidencia E-0.1-004: Barrera de Validación Estructural (`ASTValidator`)
* **Archivo Fuente Primario:** `core/ast/validator.py`
* **Símbolos Auditados:** `ASTValidator`, `ASTValidationError`, `ASTHealthReport`
* **Declaración Observada:**
  ```python
  class ASTValidator:
      @staticmethod
      def validate(ast: list[ASTNode], unknown_count_floor: int = 5, max_unknown_ratio: float = 0.15) -> bool:
          if not ast:
              raise ASTValidationError("Falla de integridad: El AST provisto está vacío.")

          seen_ids = set()
          for node in ast:
              if node.node_id in seen_ids:
                  raise ASTValidationError(f"Falla de integridad: ID duplicado detectado: {node.node_id}")
              seen_ids.add(node.node_id)

              if node.node_type == ContentNodeType.DISPLAY_EQUATION:
                  content = node.text_content or ""
                  has_open = bool(LATEX_MATH_OPEN.search(content))
                  has_close = bool(LATEX_MATH_CLOSE.search(content))
                  if has_open or has_close:
                      if not (has_open and has_close):
                          raise ASTValidationError(...)
          return True
  ```
* **Análisis de Hallazgos:**
  * `ASTValidator` aplica tres reglas de integridad pre-inferencia:
    1. Rechazo de listas de AST vacías (`len == 0`).
    2. Colisión de `node_id` duplicados mediante `set`.
    3. Validación de paridad de etiquetas de apertura/cierre TeX sobre nodos `DISPLAY_EQUATION`.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`. Se contrastará contra el contrato de validez de Ground Truth en Hito 0.4 / DC-04.

---

### B. Subdominio `core/benchmark/corpus/`

#### Evidencia E-0.1-005: Modelos de Dominio del Corpus
* **Archivo Fuente Primario:** `core/benchmark/corpus/models.py`
* **Símbolos Auditados:** `DocumentFingerprint`, `CorpusVersion`, `CorpusDocumentMetadata`, `CorpusManifest`
* **Declaración Observada:**
  ```python
  @dataclass(frozen=True, slots=True)
  class DocumentFingerprint:
      sha256: str
      def __post_init__(self) -> None:
          if not self.sha256.islower() or not all(c in "0123456789abcdef" for c in self.sha256):
              raise ValueError("Fallo de invariante: El hash SHA-256 debe ser hexadecimal en minúsculas.")

  class CorpusDocumentMetadata(BaseModel):
      document_id: str = Field(..., min_length=1)
      fingerprint: DocumentFingerprint
      traits: FrozenSet[ExtractionChallengeTrait] = Field(..., min_length=1)
      page_count: int = Field(..., gt=0)
      model_config = ConfigDict(frozen=True)

  class CorpusManifest(BaseModel):
      """Aggregate Root Puro. El negocio inmutable del espacio muestral."""
      corpus_version: CorpusVersion
      documents: List[CorpusDocumentMetadata]
      model_config = ConfigDict(frozen=True)
  ```
* **Análisis de Hallazgos:**
  * `DocumentFingerprint` valida sintácticamente que la firma sea un string SHA-256 hexadecimal en minúsculas.
  * `CorpusDocumentMetadata` encapsula los datos físicos de un PDF (`fingerprint`, `traits`, `page_count`).
  * `CorpusManifest` actúa como Aggregate Root. **Observación Clave:** `CorpusDocumentMetadata` en el dominio puro **no contiene campos para hashes de Ground Truth** (`ground_truth_sha256` o `ground_truth_version`), a diferencia del DTO `RawDocumentEntryDTO`.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`. Insumo relevante para auditar la separación entre identidad física de PDF e identidad de oráculo en Hito 0.3 / DC-02.

---

#### Evidencia E-0.1-006: Puertos Hexagonales de Infraestructura del Corpus
* **Archivo Fuente Primario:** `core/benchmark/corpus/ports.py`
* **Símbolos Auditados:** `DocumentMetadataExtractorPort`, `CorpusManifestLoaderPort`
* **Declaración Observada:**
  ```python
  class DocumentMetadataExtractorPort(Protocol):
      def extract_sha256(self, file_path: pathlib.Path) -> str: ...
      def extract_page_count(self, file_path: pathlib.Path) -> int: ...

  class CorpusManifestLoaderPort(Protocol):
      def load_raw_manifest(self) -> RawCorpusManifestDTO: ...
      def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None: ...
  ```
* **Análisis de Hallazgos:**
  * Abstracciones puras basadas en `typing.Protocol`.
  * `CorpusManifestLoaderPort` desacopla el almacenamiento del manifiesto en disco operando exclusivamente sobre `RawCorpusManifestDTO`.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-007: Servicios de Dominio de Firma y Linaje del Corpus
* **Archivo Fuente Primario:** `core/benchmark/corpus/services.py`
* **Símbolos Auditados:** `ManifestFingerprintCalculator`, `ManifestLineageSealer`
* **Declaración Observada:**
  ```python
  class ManifestFingerprintCalculator:
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

  class ManifestLineageSealer:
      @staticmethod
      def seal_manifest_with_ground_truth(
          current_manifest: RawCorpusManifestDTO,
          detected_hashes: Dict[str, str],
          target_version: str
      ) -> RawCorpusManifestDTO:
          ...
          for doc_entry in current_manifest.documents:
              if doc_id in detected_hashes:
                  gt_version = target_version
                  gt_hash = detected_hashes[doc_id]
              ...
  ```
* **Hallazgos Críticos de Auditoría Forense:**
  1. **Aislamiento de Firma de Manifiesto en `ManifestFingerprintCalculator`:** `compute_hash` únicamente firma la concatenación de `version.value` y el payload de PDFs físicos (`doc.document_id`, `doc.fingerprint.sha256`, `traits_str`, `doc.page_count`). **No incluye de ninguna forma los hashes de Ground Truth (`ground_truth_sha256`)**. Por ende, si un archivo `.ast.json` cambia, la firma global del manifiesto producida por este servicio **permanece idéntica**.
  2. **Permisividad de Sellado Parcial en `ManifestLineageSealer`:** Si `doc_id` no existe en `detected_hashes`, el método conserva silenciosamente el `gt_version` y `gt_hash` previos de `doc_entry` sin abortar la ejecución, permitiendo que el manifiesto retorne con el nuevo `manifest_hash` re-calculado aunque falten oráculos en disco.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (COMPORTAMIENTO OBSERVADO)`
  * Disposición Arquitectónica: `UNASSESSED`. Constituye la prueba forense del mecanismo causal de la falla de desacoplamiento de identidad y sellado parcial. Se eleva como objeto central de investigación para Hito 0.2 / OBS-0.1-02 y DC-05.

---

#### Evidencia E-0.1-008: Casos de Uso de Aplicación del Corpus
* **Archivo Fuente Primario:** `core/benchmark/corpus/use_cases.py`
* **Símbolos Auditados:** `BootstrapCorpusManifestUseCase`, `LoadCorpusManifestUseCase`
* **Declaración Observada:**
  ```python
  class BootstrapCorpusManifestUseCase:
      def __init__(self, loader: CorpusManifestLoaderPort, extractor: DocumentMetadataExtractorPort):
          self._loader = loader
          self._extractor = extractor

      def execute(self, pdf_directory: pathlib.Path) -> BootstrapCorpusResult:
          ...
          for entry in current_dto.documents:
              pdf_path = pdf_directory / f"{entry.document_id}.pdf"
              if not pdf_path.exists():
                  raise FileNotFoundError(f"Fallo de consistencia: Binario ausente {pdf_path}")
              ...
          manifest_hash = ManifestFingerprintCalculator.compute_hash(manifest.corpus_version, manifest.documents)
          self._loader.save_manifest_dto(...)
  ```
* **Análisis de Hallazgos:**
  * `BootstrapCorpusManifestUseCase` ejecuta Fail-Fast estricto (`FileNotFoundError`) si falta un binario `.pdf` en disco.
  * Reconcilia la información física recalculando SHA-256 y cantidad de páginas vía `DocumentMetadataExtractorPort`, ordenando alfabéticamente por `document_id` antes de persistir el DTO.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

### C. Subdominio `core/benchmark/ground_truth/`

#### Evidencia E-0.1-009: Puertos Hexagonales de Ground Truth
* **Archivo Fuente Primario:** `core/benchmark/ground_truth/ports.py`
* **Símbolos Auditados:** `GroundTruthReaderPort`, `GroundTruthDraftWriterPort`, `ASTExtractionPort`, `GroundTruthArtifactPort`
* **Declaración Observada:**
  ```python
  class GroundTruthReaderPort(Protocol):
      def load_ground_truth(self, document_id: str) -> Sequence[ASTNode]: ...

  class GroundTruthDraftWriterPort(Protocol):
      def save_draft_ast(self, document_id: str, nodes: Sequence[ASTNode]) -> None: ...

  class ASTExtractionPort(Protocol):
      def extract_ast(self, document_id: str) -> Sequence[ASTNode]: ...

  class GroundTruthArtifactPort(Protocol):
      def artifact_exists(self, document_id: str) -> bool: ...
      def read_artifact_bytes(self, document_id: str) -> bytes: ...
  ```
* **Análisis de Hallazgos:**
  * Abstracciones puras desacopladas de I/O directo.
  * `GroundTruthArtifactPort` aísla la verificación de existencia y lectura de bytes de los artefactos en disco.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-010: Servicio Duplicado de Linaje (`ManifestGroundTruthUpdater`)
* **Archivo Fuente Primario:** `core/benchmark/ground_truth/services.py`
* **Símbolo Auditado:** `ManifestGroundTruthUpdater`
* **Declaración Observada:**
  ```python
  class ManifestGroundTruthUpdater:
      @staticmethod
      def apply_lineage_sealing(
          current_manifest: RawCorpusManifestDTO,
          detected_hashes: Dict[str, str],
          target_version: str
      ) -> RawCorpusManifestDTO:
          ...
          for doc_entry in current_manifest.documents:
              if doc_id in detected_hashes:
                  gt_version = target_version
                  gt_hash = detected_hashes[doc_id]
          ...
          new_manifest_hash = ManifestFingerprintCalculator.compute_hash(
              version=CorpusVersion(value=current_manifest.corpus_version),
              documents=domain_documents_for_rehash
          )
          return RawCorpusManifestDTO(...)
  ```
* **Hallazgo Crítico de Auditoría Forense:**
  * `ManifestGroundTruthUpdater.apply_lineage_sealing` implementa exactamente la misma lógica de actualización y recálculo de manifiesto que `ManifestLineageSealer.seal_manifest_with_ground_truth` (`core/benchmark/corpus/services.py`).
  * **Confirmación de Duplicación:** Existen dos clases separadas en dos subdominios distintos (`corpus` vs `ground_truth`) realizando la misma responsabilidad de dominio.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (DUPLICACIÓN ESTRUCTURAL OBSERVADA)`
  * Disposición Arquitectónica: `UNASSESSED`. Objeto central de la investigación del Hito 0.2 para resolver la unificación de autoridad.

---

#### Evidencia E-0.1-011: Demostración Forense de Mecanismo Causal Inmediato de Partial Sealing (`SealGroundTruthUseCase`)
* **Archivo Fuente Primario:** `core/benchmark/ground_truth/use_cases.py`
* **Símbolo Auditado:** `SealGroundTruthUseCase.execute(target_version: str = "v1.0") -> str`
* **Declaración Observada:**
  ```python
  class SealGroundTruthUseCase:
      def __init__(self, corpus_loader: CorpusManifestLoaderPort, artifact_port: GroundTruthArtifactPort):
          self._corpus_loader = corpus_loader
          self._artifact_port = artifact_port

      def execute(self, target_version: str = "v1.0") -> str:
          current_manifest = self._corpus_loader.load_raw_manifest()
          detected_hashes: Dict[str, str] = {}

          # 1. Recolección de firmas binarias puras sin tocar modelos de dominio extraños
          for doc_entry in current_manifest.documents:
              doc_id = doc_entry.document_id
              if self._artifact_port.artifact_exists(doc_id):
                  raw_bytes = self._artifact_port.read_artifact_bytes(doc_id)
                  detected_hashes[doc_id] = compute_sha256(raw_bytes)

          # 2. Delegación inter-contexto al servicio especialista del Corpus
          sealed_manifest = ManifestLineageSealer.seal_manifest_with_ground_truth(
              current_manifest=current_manifest,
              detected_hashes=detected_hashes,
              target_version=target_version
          )

          # 3. Persistencia a través del puerto
          self._corpus_loader.save_manifest_dto(sealed_manifest)
          return sealed_manifest.manifest_hash
  ```
* **Hallazgo Forense P0 (Demostración Estática Directa):**
  1. El bucle `for doc_entry in current_manifest.documents:` realiza la verificación condicional `if self._artifact_port.artifact_exists(doc_id):`.
  2. Si `artifact_exists(doc_id)` retorna `False` (es decir, **falta el oráculo AST para ese documento**), el caso de uso **no lanza ninguna excepción ni interrumpe la ejecución**. Simplemente ignora ese `doc_id` y no lo agrega al diccionario `detected_hashes`.
  3. Al invocar `ManifestLineageSealer.seal_manifest_with_ground_truth(...)`, los documentos sin oráculo conservan su valor anterior (o `None`), se recalcula la firma general y se persiste el manifiesto re-firmado vía `self._corpus_loader.save_manifest_dto(sealed_manifest)`.
  4. **Conclusión:** Queda demostrado en código que la infraestructura actual **permite sellar un manifiesto incompleto sin asegurar cardinalidad biyectiva $N_{\text{PDF}} = N_{\text{GT}}$**.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (MECANISMO CAUSAL INMEDIATO DEMOSTRADO ESTÁTICAMENTE)`
  * Disposición Arquitectónica: `UNASSESSED`. Elevado a Hito 0.2 / DC-05 para diseñar la atomicidad estricta.

---

### D. Subdominio Infraestructura (`infra/`)

#### Evidencia E-0.1-012: Cargador Local del Manifiesto
* **Archivo Fuente Primario:** `infra/fs/corpus_repository.py`
* **Símbolo Auditado:** `LocalFileSystemCorpusLoader`
* **Declaración Observada:**
  ```python
  class LocalFileSystemCorpusLoader(CorpusManifestLoaderPort):
      def __init__(self, base_path: pathlib.Path):
          self.base_path = pathlib.Path(base_path)
          if self.base_path.is_file() or self.base_path.suffix == ".json":
              self.manifest_file = self.base_path
          else:
              self.manifest_file = self.base_path / "manifest.json"

      def load_raw_manifest(self) -> RawCorpusManifestDTO:
          if not self.manifest_file.exists():
              return RawCorpusManifestDTO(
                  corpus_version="v1.0",
                  manifest_hash="",
                  documents=[]
              )

          with open(self.manifest_file, "r", encoding="utf-8") as f:
              data = json.load(f)

          return RawCorpusManifestDTO.model_validate(data)

      def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None:
          self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
          with open(self.manifest_file, "w", encoding="utf-8") as f:
              json.dump(dto.model_dump(), f, indent=2, ensure_ascii=False)
  ```
* **Análisis de Hallazgos:**
  * Implementa `CorpusManifestLoaderPort` para I/O en disco del archivo `manifest.json`.
  * Si el archivo no existe, retorna un `RawCorpusManifestDTO` vacío en lugar de arrojar error (comportamiento por defecto para bootstrap).
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-013: Adaptadores de Almacenamiento de Ground Truth
* **Archivo Fuente Primario:** `infra/fs/ground_truth_store.py`
* **Símbolos Auditados:** `LocalFileSystemGroundTruthReader`, `LocalFileSystemGroundTruthDraftWriter`, `LocalFileSystemGroundTruthArtifactAdapter`
* **Declaración Observada:**
  ```python
  class LocalFileSystemGroundTruthReader(GroundTruthReaderPort):
      def load_ground_truth(self, document_id: str) -> Sequence[ASTNode]:
          target_path = self._ground_truth_directory / f"{document_id}.json"
          if not target_path.exists():
              raise FileNotFoundError(f"Oracle consistency error: Ground Truth for '{document_id}' not found.")
          return read_ast_json(target_path)

  class LocalFileSystemGroundTruthDraftWriter(GroundTruthDraftWriterPort):
      def save_draft_ast(self, document_id: str, nodes: Sequence[ASTNode]) -> None:
          target_path = self._ground_truth_directory / f"{document_id}.json"
          write_ast_json_atomic(list(nodes), target_path, indent=2)

  class LocalFileSystemGroundTruthArtifactAdapter(GroundTruthArtifactPort):
      def artifact_exists(self, document_id: str) -> bool:
          return (self._ground_truth_directory / f"{document_id}.json").exists()

      def read_artifact_bytes(self, document_id: str) -> bytes:
          target_path = self._ground_truth_directory / f"{document_id}.json"
          return target_path.read_bytes()
  ```
* **Análisis de Hallazgos:**
  * Se acoplan directamente a las funciones de serialización en `infra/serialization/ast_json.py` (`read_ast_json`, `write_ast_json_atomic`).
  * Los oráculos se buscan en el subdirectorio `ground_truth/{document_id}.json`.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-014: Serialización Atómica de AST JSON
* **Archivo Fuente Primario:** `infra/serialization/ast_json.py`
* **Símbolos Auditados:** `serialize_ast_json`, `deserialize_ast_json`, `write_ast_json_atomic`, `read_ast_json`
* **Declaración Observada:**
  ```python
  _AST_LIST_ADAPTER: TypeAdapter[List[ASTNode]] = TypeAdapter(List[ASTNode])

  def serialize_ast_json(nodes: List[ASTNode], indent: int | None = 2) -> str:
      return _AST_LIST_ADAPTER.dump_json(nodes, indent=indent).decode("utf-8")

  def write_ast_json_atomic(nodes: List[ASTNode], target_path: pathlib.Path, indent: int | None = 2) -> None:
      content = serialize_ast_json(nodes, indent=indent)
      target_dir = target_path.parent
      target_dir.mkdir(parents=True, exist_ok=True)
      with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
          temp_path = pathlib.Path(tf.name)
          tf.write(content)
          tf.flush()
          try:
              os.fsync(tf.fileno())
          except (AttributeError, OSError):
              pass
      temp_path.rename(target_path)
  ```
* **Análisis de Hallazgos:**
  * Utiliza Pydantic `TypeAdapter(List[ASTNode])` para la conversión directa entre JSON y DTOs `ASTNode`.
  * `write_ast_json_atomic` garantiza escrituras seguras en disco utilizando un archivo temporal intermedio, `os.fsync` y reemplazo de puntero atómico (`rename`).
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

### E. Subdominio Topología (`core/benchmark/topology/`)

#### Evidencia E-0.1-015: Puertos y Contratos de Evaluación Topológica
* **Archivo Fuente Primario:** `core/benchmark/topology/ports.py`
* **Símbolos Auditados:** `TopologicalEvaluatorProtocol`, `TreeEditEngine`, `TreeDistanceAlgorithm`, `TreeEditCostContext`, `AnchorAlignmentStrategy`, `AnchorPartitionStrategy`, `OverflowStrategy`, `NormalizationPolicy`
* **Declaración Observada:**
  ```python
  @runtime_checkable
  class TopologicalEvaluatorProtocol(Protocol):
      @property
      def metric_name(self) -> str: ...
      def evaluate(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> MetricScoreDTO: ...

  @runtime_checkable
  class TreeEditEngine(Protocol):
      def compute(
          self,
          candidate_forest: EvaluationForest,
          ground_truth_forest: EvaluationForest,
          cost_context: TreeEditCostContext
      ) -> float: ...

  @runtime_checkable
  class TreeDistanceAlgorithm(Protocol):
      def compute_distance(
          self, 
          cand_index: PostorderIndex, 
          gt_index: PostorderIndex, 
          costs: TreeEditCostContext
      ) -> float: ...
  ```
* **Análisis de Hallazgos:**
  * Define los contratos perimetrales para el motor topológico utilizando `@runtime_checkable` y `typing.Protocol`.
  * Desacopla la orquestación del evaluador (`TopologicalEvaluatorProtocol`) del cálculo algebraico de distancias de árboles (`TreeEditEngine` y `TreeDistanceAlgorithm`).
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-016: Evaluador de Distancia de Edición de Árbol (`TreeEditDistanceEvaluator`)
* **Archivo Fuente Primario:** `core/benchmark/topology/evaluators/ted.py`
* **Símbolo Auditado:** `TreeEditDistanceEvaluator`
* **Declaración Observada:**
  ```python
  class TreeEditDistanceEvaluator(TopologicalEvaluatorProtocol):
      def __init__(
          self,
          aligner: AnchorAlignmentStrategy,
          partitioner: AnchorPartitionStrategy,
          engine: TreeEditEngine,
          overflow_handler: OverflowStrategy,
          normalizer: NormalizationPolicy,
          cost_context: TreeEditCostContext,
          evaluation_context: TEDEvaluationContext | None = None
      ):
          ...
      @property
      def metric_name(self) -> str:
          return "normalized_structural_score"

      def evaluate(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> MetricScoreDTO:
          alignment = self._aligner.align(candidate_ast, ground_truth_ast)
          windows = self._partitioner.partition(candidate_ast, ground_truth_ast, alignment)
          ...
          accumulated_distance += self._engine.compute(window.candidate, window.ground_truth, self._cost_context)
          ...
          return MetricScoreDTO(...)
  ```
* **Análisis de Hallazgos:**
  * Orquesta el flujo de evaluación estructural: alineamiento de anclas (`aligner`), partición por ventanas (`partitioner`), cálculo con el motor inyectado (`engine`), manejo de desbordamiento (`overflow_handler`) y normalización de demeritación (`normalizer`).
  * Implementa `TopologicalEvaluatorProtocol` retornando un `MetricScoreDTO` con `primary_score` en el rango $[0.0, 1.0]$.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`. Insumo para la compuerta de regresión topológica en Hito 0.4 / DC-07.

---

#### Evidencia E-0.1-017: Evaluador de Recuperación por Entidad (`EntityRecallEvaluator`)
* **Archivo Fuente Primario:** `core/benchmark/topology/evaluators/recall.py`
* **Símbolo Auditado:** `EntityRecallEvaluator`
* **Declaración Observada:**
  ```python
  class EntityRecallEvaluator(TopologicalEvaluatorProtocol):
      def __init__(
          self,
          target_type: ContentNodeType,
          matching_policy: NodeMatchingPolicy
      ):
          self._target_type = target_type
          self._matching_policy = matching_policy

      @property
      def metric_name(self) -> str:
          return f"f1_score_{self._target_type.value.lower()}"

      def evaluate(
          self, 
          candidate_ast: Sequence[ASTNode],
          ground_truth_ast: Sequence[ASTNode]
      ) -> MetricScoreDTO:
          candidates = [n for n in candidate_ast if n.node_type == self._target_type]
          gts = [n for n in ground_truth_ast if n.node_type == self._target_type]
          ...
  ```
* **Análisis de Hallazgos:**
  * Micro-juez O(n) que calcula recall, precisión y F1 score sobre un `ContentNodeType` específico.
  * Utiliza un `MatchingKey` producido por la `NodeMatchingPolicy` inyectada para la búsqueda asintótica de correspondencias.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

#### Evidencia E-0.1-018: Motor Topológico Zhang-Shasha (`ZhangShashaEngine`)
* **Archivo Fuente Primario:** `core/benchmark/topology/engines/zhang_shasha/engine.py`
* **Símbolo Auditado:** `ZhangShashaEngine`
* **Declaración Observada:**
  ```python
  class ZhangShashaEngine(TreeEditEngine):
      def __init__(self, indexer: PostorderIndexer, algorithm: TreeDistanceAlgorithm):
          self._indexer = indexer
          self._algorithm = algorithm

      def compute(
          self,
          candidate_forest: EvaluationForest,
          ground_truth_forest: EvaluationForest,
          cost_context: TreeEditCostContext
      ) -> float:
          cand_index = self._indexer.build(candidate_forest.nodes)
          gt_index = self._indexer.build(ground_truth_forest.nodes)
          return self._algorithm.compute_distance(cand_index, gt_index, cost_context)
  ```
* **Análisis de Hallazgos:**
  * Implementa `TreeEditEngine` en el dominio de `core/benchmark/topology`.
  * Es una implementación nativa en Python aislada detrás del puerto `TreeDistanceAlgorithm` (`ZhangShashaTreeDistanceCalculator`).
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

### F. Herramientas de Evaluación CLI y Métricas Externas (`tools/evaluation/`)

#### Evidencia E-0.1-019: Métrica Topológica Basada en APTED Externa (`StructuralTopologyMetric`)
* **Archivo Fuente Primario:** `tools/evaluation/topology/metrics/structural.py`
* **Símbolos Auditados:** `StructuralTopologyMetric`, `CostMatrix`, `CustomAPTEDConfig`
* **Declaración Observada:**
  ```python
  from apted import APTED, Config
  from apted.helpers import Tree
  from tools.evaluation.topology.ports import TopologyMetric

  class StructuralTopologyMetric(TopologyMetric):
      def __init__(self, cost_matrix: CostMatrix | None = None) -> None:
          self._matrix = cost_matrix or CostMatrix.default_v1()
          self._config = CustomAPTEDConfig(matrix=self._matrix)

      def evaluate(
          self,
          candidate: Sequence[ASTNode],
          ground_truth: Sequence[ASTNode],
      ) -> MetricResult:
          cand_tree, total_cand_nodes = self._build_apted_tree(candidate)
          gt_tree, total_gt_nodes = self._build_apted_tree(ground_truth)
          ...
          apted = APTED(cand_tree, gt_tree, self._config)
          distance = float(apted.compute_edit_distance())
          ...
  ```
* **Hallazgo Forense Crítico (Confirmación de Duplicación Topológica OBS-0.1-04):**
  1. En `core/benchmark/topology/` existe el motor `ZhangShashaEngine` (implementación propia de Tree Edit Distance).
  2. En `tools/evaluation/topology/metrics/` existe `StructuralTopologyMetric` que calcula Tree Edit Distance acoplándose directamente a la biblioteca de terceros C/Python `apted`.
  3. **Conclusión:** Queda demostrada en código la existencia de **dos infraestructuras paralelas independientes para evaluar Tree Edit Distance** en el repositorio.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (DUPLICACIÓN Y ACOPLAMIENTO EXTERNO OBSERVADO)`
  * Disposición Arquitectónica: `UNASSESSED`. Elevado como tema prioritario para la consolidación de motores topológicos en Hito 0.4 / OBS-0.1-04.

---

#### Evidencia E-0.1-020: Punto de Entrada CLI de Sellado (`freeze_ground_truth.py`)
* **Archivo Fuente Primario:** `tools/evaluation/freeze_ground_truth.py`
* **Símbolos Auditados:** `main()`
* **Declaración Observada:**
  ```python
  def main() -> None:
      base_path = pathlib.Path("tests/corpus/benchmark_v1")

      corpus_loader = LocalFileSystemCorpusLoader(base_path)
      artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path)

      use_case = SealGroundTruthUseCase(corpus_loader=corpus_loader, artifact_port=artifact_adapter)

      logger.info("Triggering cryptographic lineage seal execution for curated Ground Truth.")
      try:
          global_manifest_hash = use_case.execute(target_version="v1.0")
          logger.info("Cryptographic lock complete. Manifest verified under global SHA-256: %s", global_manifest_hash)
      except Exception as e:
          logger.critical("Catastrophic lineage sealing breakdown: %s", str(e))
  ```
* **Análisis de Hallazgos:**
  * Actúa como Imperative Shell en la capa CLI (`tools/evaluation`).
  * Ensambla el grafo de objetos instanciando adaptadores de infraestructura (`LocalFileSystemCorpusLoader`, `LocalFileSystemGroundTruthArtifactAdapter`) e inyectándolos en `SealGroundTruthUseCase`.
* **Límite Epistemológico Hito 0.1:**
  * Estado: `CONFIRMED (ESTRUCTURAL)`
  * Disposición Arquitectónica: `UNASSESSED`.

---

## 3. GRAFO DE DEPENDENCIAS REALES DE CÓDIGO (COMPLETO)

```text
[ tools/evaluation/freeze_ground_truth.py ] (CLI Imperative Shell)
               │
               ▼
[ core/benchmark/ground_truth/use_cases.py ]
   └── SealGroundTruthUseCase
            │
            ├──► CorpusManifestLoaderPort (Protocol) ◄── [ infra/fs/corpus_repository.py ]
            │                                                 └── LocalFileSystemCorpusLoader
            │
            ├──► GroundTruthArtifactPort (Protocol)  ◄── [ infra/fs/ground_truth_store.py ]
            │                                                 └── LocalFileSystemGroundTruthArtifactAdapter
            │                                                          │
            │                                                          ▼
            │                                            [ System OS / Filesystem Bytes ]
            │
            └──► ManifestLineageSealer (Domain Service) [ core/benchmark/corpus/services.py ]
                     │
                     └──► ManifestFingerprintCalculator [ core/benchmark/corpus/services.py ]

──────────────────────────────────────────────────────────────────────────────────────────

[ EVALUACIÓN TOPOLÓGICA — RAMA DOMINIO `core/` ]
[ core/benchmark/topology/evaluators/ted.py ]
   └── TreeEditDistanceEvaluator (implements TopologicalEvaluatorProtocol)
            │
            ├──► TreeEditEngine (Protocol) ◄── [ core/benchmark/topology/engines/zhang_shasha/engine.py ]
            │                                       └── ZhangShashaEngine
            │                                                ├── PostorderIndexer
            │                                                └── ZhangShashaTreeDistanceCalculator
            │
            ├──► TreeEditCostContext (Protocol) ◄── [ core/benchmark/topology/costs/unit.py ]
            │                                             └── UnitCostContext
            │
            └──► AnchorAlignmentStrategy (Protocol) ◄── [ core/benchmark/topology/alignment/strategy.py ]
                                                             └── LCSAnchorAlignmentStrategy

──────────────────────────────────────────────────────────────────────────────────────────

[ EVALUACIÓN TOPOLÓGICA — RAMA HERRAMIENTAS `tools/` ]
[ tools/evaluation/topology/metrics/structural.py ]
   └── StructuralTopologyMetric (implements TopologyMetric)
            │
            ├──► ASTFingerprintPolicy [ tools/evaluation/topology/fingerprint.py ]
            │
            └──► apted (Librería Externa C/Python)
                     └── APTED(cand_tree, gt_tree, CustomAPTEDConfig)
```

---

## 4. REGISTRO DE OBSERVACIONES DE ARQUITECTURA CONSOLIDADAS

| ID Observación | Subdominio | Descripción del Hallazgo Observado | Impacto en Auditoría Futura |
| :--- | :--- | :--- | :--- |
| **OBS-0.1-01** | `core/benchmark/` | Coexistencia en el mismo Bounded Context de benchmarking de LLM/generativo (`GeminiBenchmarkRunner`, `StatisticalComparator`, `LeaderboardService`) con benchmarking topológico de Parsers (`ZhangShashaEngine`, `EntityRecallEvaluator`). | Auditar acoplamiento en Hito 0.4 para delimitar Clean Architecture. |
| **OBS-0.1-02** | `corpus/` vs `ground_truth/` | Duplicidad estructural de servicios de linaje: `ManifestLineageSealer` (`corpus/services.py`) y `ManifestGroundTruthUpdater` (`ground_truth/services.py`), implementando algoritmos idénticos. | Objeto central de la auditoría forense de sellado en Hito 0.2. |
| **OBS-0.1-03** | `infra/` | Ubicación de la serialización atómica JSON de AST en `infra/serialization/ast_json.py` en lugar de `infra/fs/` o `ground_truth`. | Auditar en Hito 0.3 para mapear el flujo de canonicalización. |
| **OBS-0.1-04** | `topology/` | Existencia paralela de evaluadores: `TreeEditDistanceEvaluator` basado en `ZhangShashaEngine` (`core/`) vs. `StructuralTopologyMetric` basada en la gema externa `apted` (`tools/`). | Auditar en Hito 0.4 la redundancia de motores de edición de árboles. |
| **OBS-0.1-05** | `core/ast/` | `ContentNodeType` no mapea severidad de regresión (`CRITICAL`, `WARNING`, `INFO`). Ausencia de un Enum o Value Object de criticidad en `core/ast/enums.py`. | Auditar en Hito 0.4 para alimentar el diseño de criticidad. |
| **OBS-0.1-06** | `corpus/` | `ManifestFingerprintCalculator.compute_hash` solo toma metadatos físicos del PDF (`doc_id`, `sha256`, `traits`, `page_count`). Las firmas de Ground Truth (`ground_truth_sha256`) no forman parte de la firma global del manifiesto. | Objeto principal de auditoría de identidad criptográfica en Hito 0.3 / DC-03. |
| **OBS-0.1-07** | `ground_truth/` | `SealGroundTruthUseCase.execute()` omite silenciosamente documentos sin oráculo en disco sin levantar excepciones, causando el fenómeno de *Partial Sealing*. | Mecanismo causal inmediato demostrado estáticamente. Insumo principal para Hito 0.2 / DC-05. |
| **OBS-0.1-08** | `tools/` vs `core/` | `tools/evaluation/topology/metrics/structural.py` introduce una dependencia directa de la librería externa de terceros `apted`, mientras que `core/benchmark/topology/engines/` es una implementación 100% nativa. | Evaluar dependencia externa vs. motor propio en Hito 0.4. |

---

## 5. ESTADO DE RECEPCIÓN DE FUENTES PRIMARIAS

* [x] **Bloque 1 - Grupo A (`core/ast/`):** Recibido y auditado (`models.py`, `enums.py`, `hashing.py`, `validator.py`).
* [x] **Bloque 1 - Grupo B (`core/benchmark/corpus/`):** Recibido y auditado (`models.py`, `ports.py`, `services.py`, `use_cases.py`).
* [x] **Bloque 2 (`ground_truth/` e `infra/`):** Recibido y auditado (`ports.py`, `services.py`, `use_cases.py`, `corpus_repository.py`, `ground_truth_store.py`, `ast_json.py`).
* [x] **Bloque 3 (`topology/` y `tools/evaluation/`):** Recibido y auditado (`ports.py`, `ted.py`, `recall.py`, `engine.py`, `structural.py`, `freeze_ground_truth.py`).

---

## 6. LÍMITE EPISTEMOLÓGICO Y DECLARACIÓN DE CIERRE DEL HITO 0.1

El **Hito 0.1 (Repository & Architecture Inventory)** queda oficialmente **COMPLETADO Y CERRADO**. 

**Garantías del Entregable:**
1. **Cobertura Estructural:** Los componentes y archivos declarados como alcance del Hito 0.1 han sido inspeccionados mediante evidencia primaria de código fuente.
2. **Neutralidad Arquitectónica:** Todos los componentes se mantienen marcados estrictamente como **`UNASSESSED`**. No se han tomado decisiones prematuras de refactorización, conservación o eliminación (`KEEP` / `EXTEND` / `REPLACE` / `DEPRECATE`), respetando la regla *Evidence First* del `ADR_F17-BIS_0`.
3. **Puntos de Infección Identificados:** Quedan formalmente registradas las 8 observaciones estructurales que serán investigadas con experimentos y trazado de flujos en los Hitos 0.2, 0.3 y 0.4.
```

---

# INICIO DEL HITO 0.2: GROUND TRUTH & SEALING FORENSIC AUDIT

Hito 0.1 está congelado. Entramos oficialmente al **Hito 0.2: Ground Truth & Sealing Forensic Audit**.

### Objetivo del Hito 0.2:
Demostrar el flujo transaccional completo de sellado y linaje, respondiendo con evidencia forense a las siguientes preguntas P0:
1. **Mecanismo Causal Completo del Sellado Parcial:** ¿Cómo interactúa el flujo real desde la lectura del manifiesto, la detección de archivos en disco, la llamada a `ManifestLineageSealer` (o `ManifestGroundTruthUpdater`) hasta la persistencia en `LocalFileSystemCorpusLoader`?
2. **Duplicación y Autoridad de Linaje:** ¿Por qué existen `ManifestLineageSealer` (`corpus/services.py`) y `ManifestGroundTruthUpdater` (`ground_truth/services.py`)? ¿Cuál es invocado en tiempo de ejecución por `tools/evaluation/freeze_ground_truth.py` o los tests? ¿Cuál de las dos clases es código muerto o legado?
3. **Lifecycle y Estados de Oráculo:** ¿Existe algún Enum o estado explícito (`DRAFT`, `AUDITED`, `VALIDATED`, `SEALED`) en el código actual, o el estado `SEALED` se infiere únicamente de la presencia de `ground_truth_sha256` no nulo en el JSON del manifiesto?

---

### Archivos/Fuentes Necesarias para el Hito 0.2:

Para no asumir nada y usar evidencia primaria de ejecución y pruebas, por favor provee el contenido de los siguientes archivos:

1. `core/benchmark/corpus/dtos.py` (para analizar las definiciones de `RawCorpusManifestDTO` y `RawDocumentEntryDTO`).
2. Archivos de pruebas relevantes en `tests/`:
   * `tests/unit/test_leaderboard_service.py` u otros tests en `tests/` que importen `ManifestLineageSealer`, `ManifestGroundTruthUpdater` o `SealGroundTruthUseCase`.
3. Mapeo de consumidores en el proyecto (búsqueda de dónde se importan `ManifestGroundTruthUpdater` y `ManifestLineageSealer`).

Apenas los envíes, comenzaremos a trazar el informe **`HITO_0.2_FORENSIC_FLOW_AUDIT.md`**.