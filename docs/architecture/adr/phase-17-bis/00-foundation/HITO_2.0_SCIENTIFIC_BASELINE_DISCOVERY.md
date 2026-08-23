# HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY.md

**Estado:** FROZEN v2.1.0-SOTA
**Fecha de congelamiento:** 2026-08-22
**Fase:** 17-BIS — Fase 2 (Scientific Baseline Domain)
**Tipo de artefacto:** Forensic Discovery / Audit HITO (Metodología §3.5.1)
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** HITO_0.1–0.5 (ADR_F17_BIS_0), HITO_0.4.5 Final Integrated Report, HITO_0.5 Entregable 1 (Architecture Gap Matrix), NADR-F17BIS-01/03/09/11, ADR_F17_BIS_01, FASE_1_HANDOFF, FASE_1_DEFERRED_FINDINGS_REGISTER (DF-01-A..D), módulos primarios (`core/benchmark/corpus/`, `core/benchmark/ground_truth/`, `infra/fs/`) e insumo secundario (`tools/evaluation/`, `core/benchmark/ports.py`).
**Síntesis:** Versión integradora de V1 (disciplina metodológica + apéndices), V2 (cobertura forense completa) y las correcciones de rigor validadas por el Architecture Board. Verificada contra la cadena completa: ADR Maestro → ADR_F17_BIS_0 → HITOs 0.1–0.5 → Gap Matrix → NADRs 01–11 → Execution Plan Fase 1 → Findings Register Fase 1.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 2.0.0-SOTA | 2026-08-22 | Síntesis integradora V1+V2 con correcciones de rigor. |
| 2.1.0-FROZEN | 2026-08-22 | Adición de §15 (matriz de trazabilidad DC), nota terminológica H_physical vs H_runtime en §10.1, y anotaciones de hallazgos emergentes post-Fase 1 en E-2.0-15/17/18. Cierre formal del Cotejo #1 y Cotejo #2. |

---

## 1. RESUMEN EJECUTIVO

El Discovery forense de Fase 2 está completo. Se auditó el 100% de los módulos primarios y el insumo secundario. De los 38 componentes clasificados, **27 son RETAIN**: el sistema posee un esqueleto hexagonal sano sobre el cual Fase 2 puede formalizar la ontología sin demoler nada.

**Hallazgo central — error de categoría ontológica:**

> *El flujo actual de sellado trata la existencia de un archivo y su SHA-256 de bytes como si fueran validez científica e identidad del oráculo.*

El sistema actual opera como un catálogo físico de documentos y un almacén de archivos de ground truth, pero carece de la ontología necesaria para distinguir formalmente:

```text
Draft              ≠  Oracle
Existencia         ≠  Validez
Integridad         ≠  Identidad semántica
Archivo JSON       ≠  Ground Truth científico
Hash de bytes      ≠  compute_ast_hash / H_semantic
Manifest físico    ≠  Baseline Identity
```

**Cuatro defectos dominantes confirmados (triángulo de partial sealing + orfandad semántica):**

1. **Partial Sealing persistente (E-2.0-01):** `SealGroundTruthUseCase` omite silenciosamente oráculos ausentes. Viola *Zero Partial Sealing* (ADR Maestro §5).
2. **Firma global ciega al Ground Truth (E-2.0-02):** `manifest_hash` no incluye hashes de oráculos; un oráculo puede mutarse sin alterar la firma.
3. **Ciclo de vida inexistente (E-2.0-04):** no hay estados `Draft/Audited/Validated/Sealed`; el sello se infiere por strings opcionales.
4. **Identidad semántica huérfana (E-2.0-10):** `compute_ast_hash()` no viaja en el modelo de baseline. Materialización de DF-01-C.

**Tres hallazgos de cierre del insumo secundario:**

- `ASTFingerprintPolicy` y `compute_ast_hash()` son mecanismos **ortogonales**, no redundantes (E-2.0-16).
- `LocalFileSystemCorpusRepository` (tools) y `LocalFileSystemCorpusLoader` (infra) tienen **responsabilidades distintas**, no son duplicados.
- `GroundTruthProviderProtocol` y `GroundTruthReaderPort` tienen solapamiento **conceptual pero no técnico** (bounded contexts distintos).

**Veredicto:** Fase 2 es necesaria y urgente. El sistema puede generar y almacenar ground truth, pero no puede demostrar que ese ground truth es completo, válido, sellado, inmutable, semánticamente identificado y distinguible de un draft. Ese es exactamente el vacío que Fase 2 debe formalizar antes de que Fase 3 construya el Identity & Trust Model.

---

## 2. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `core/benchmark/corpus/` | dtos, enums, mappers, models, ports, services, use_cases | ✅ 100% |
| `core/benchmark/ground_truth/` | errors, ports, services, use_cases | ✅ 100% |
| `infra/fs/` | corpus_repository, ground_truth_store | ✅ 100% |
| `tools/evaluation/` | bootstrap_corpus, freeze_ground_truth, generate_golden_draft, benchmark_service, fingerprint, corpus_repository | ✅ 100% |
| `core/benchmark/ports.py` | Puertos de benchmark | ✅ 100% |

**Superficies referenciadas por evidencia de gobernanza previa (no re-auditadas):** `infra/serialization/ast_json.py` (certificado SOTA SRE por E-0.1-014 de Fase 0), `core/ast/hashing.py` (Task 1.2.4 DONE en Execution Plan v3.0.0).

---

## 3. MAPA DE FLUJOS OBSERVADOS (evidencia de canalización)

```text
FLUJO A — Bootstrap del manifiesto (escritura/saneamiento)
  tools/evaluation/bootstrap_corpus.py (entry point)
    → LocalFileSystemCorpusLoader + PyMuPdfDocumentMetadataExtractor [composición INLINE ⚠ E-2.0-15]
    → BootstrapCorpusManifestUseCase.execute(pdf_dir)
      → loader.load_raw_manifest()          [si no existe: DEFAULT VACÍO SILENCIOSO ⚠ E-2.0-05]
      → por doc: extractor.extract_sha256() / extract_page_count()
      → fail-fast si PDF ausente (FileNotFoundError) ✅
      → ManifestFingerprintCalculator.compute_hash()
      → loader.save_manifest_dto()          [ESCRITURA NO ATÓMICA ⚠ E-2.0-06]

FLUJO B — Generación de Golden Draft (curaduría)
  tools/evaluation/generate_golden_draft.py (entry point)
    → build_extraction_pipeline() [Composition Root ✅ NADR-11 parcial]
    → BenchmarkParserBridge (adaptador ASTExtractionPort) [instanciado 2× ⚠ OBS-2.0-11]
    → GenerateGoldenDraftUseCase.execute(doc_id)
      → extractor.extract_ast()             [vía ASTExtractionPort]
      → fail-fast si secuencia vacía (EmptyGroundTruthDraftError) ✅
      → writer.save_draft_ast()             [write_ast_json_atomic ✅]
      ⚠ NO valida el AST (sin ASTValidator)
      ⚠ NO consulta si el documento ya está sellado → puede sobrescribir oráculo [E-2.0-12]
    → entry point captura FileNotFoundError como WARNING y continúa ⚠ [E-2.0-18]

FLUJO C — Sellado (freeze)
  tools/evaluation/freeze_ground_truth.py (entry point)
    → LocalFileSystemCorpusLoader + LocalFileSystemGroundTruthArtifactAdapter [INLINE ⚠ E-2.0-15]
    → SealGroundTruthUseCase.execute(target_version="v1.0" hardcodeado ⚠ E-2.0-17)
      → loader.load_raw_manifest()
      → por doc: if artifact_exists(doc_id): hash = sha256(bytes_crudos)
                 else: OMISIÓN SILENCIOSA (sin else-branch) ⚠ PARTIAL SEALING [E-2.0-01]
      → ManifestLineageSealer.seal_manifest_with_ground_truth()
        → aplica gt_version/gt_hash donde hay match
        → rehash global EXCLUYENDO campos GT ⚠ [E-2.0-02]
      → loader.save_manifest_dto()          [no atómico]

FLUJO D — Lectura runtime del oráculo
  LoadGroundTruthUseCase.execute(doc_id)
    → reader.load_ground_truth()
      → FileNotFoundError si falta (fail-fast ✅)
      → read_ast_json() (contrato canónico NADR-01 §5.9 ✅)

FLUJO E — Lectura runtime del manifiesto
  LoadCorpusManifestUseCase.execute()
    → loader.load_raw_manifest() → hidratación O(n) [docstring dice O(1) ⚠ OBS-2.0-06]
    ⚠ manifest_hash almacenado NUNCA se verifica contra recomputado [E-2.0-08]

FLUJO F — Benchmark topológico (Fase 4, out-of-scope de Fase 2)
  TopologyBenchmarkService.evaluate_corpus(provider_name, documents)
    → por doc: metric.evaluate(doc.candidate, doc.ground_truth)
    → strategy.aggregate(...)
    ⚠ ground_truth aquí es concepto laxo (tuple[ASTNode]), no Oráculo sellado
    ⚠ NO usa ASTFingerprintPolicy (usa métricas topológicas)
```

---

## 4. REGISTRO DE EVIDENCIA FORENSE (E-2.0-xx)

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente.

| ID | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|
| **E-2.0-01** | P0 | `ground_truth/use_cases.py::SealGroundTruthUseCase.execute` → `if self._artifact_port.artifact_exists(doc_id):` sin rama `else` | **Partial Sealing confirmado.** La ausencia de oráculo se omite silenciosamente; el manifiesto se sella con $N_{GT} < N_{PDF}$. Viola *Zero Partial Sealing* (ADR Maestro §5). Verifica E-0.2-001/002 de Fase 0. |
| **E-2.0-02** | P0 | `corpus/services.py::ManifestFingerprintCalculator.compute_hash` → `document_payload = f"{doc.document_id}:{doc.fingerprint.sha256}:{traits_str}:{doc.page_count}"` | **Firma global excluye Ground Truth.** `ground_truth_sha256` y `ground_truth_version` ausentes del pre-image. Un oráculo puede mutarse/borrarse sin alterar `manifest_hash`. Verifica E-0.1-007/E-0.2-003. Gap $H_{baseline}$ materializado. |
| **E-2.0-03** | P1 | `ground_truth/services.py::ManifestGroundTruthUpdater.apply_lineage_sealing` vs `corpus/services.py::ManifestLineageSealer.seal_manifest_with_ground_truth` | **Duplicación línea por línea.** El único consumidor (`SealGroundTruthUseCase`) importa `ManifestLineageSealer`; `ManifestGroundTruthUpdater` tiene 0 llamadores. Doble autoridad de linaje huérfana. Verifica E-0.2-004. |
| **E-2.0-04** | P0 | `corpus/dtos.py::RawDocumentEntryDTO` → `ground_truth_version: Optional[str]`, `ground_truth_sha256: Optional[str]` | **Ciclo de vida inexistente.** El estado "sellado" se infiere de un string no nulo. No existe enum `Draft/Audited/Validated/Sealed`. Verifica E-0.2-006. |
| **E-2.0-05** | P1 | `infra/fs/corpus_repository.py::load_raw_manifest` → `if not self.manifest_file.exists(): return RawCorpusManifestDTO(corpus_version="v1.0", manifest_hash="", documents=[])` | **Fail-open en frontera de lectura.** Manifiesto ausente degrada a default vacío sin excepción. Viola ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos). Contrasta con `LocalFileSystemGroundTruthReader` (fail-fast). |
| **E-2.0-06** | P1 | `infra/fs/corpus_repository.py::save_manifest_dto` → `with open(...)` sin tempfile/fsync | **Escritura no atómica del manifiesto.** Inconsistente con `ground_truth_store.py` que delega en `write_ast_json_atomic` (SOTA SRE, E-0.1-014). |
| **E-2.0-07** | P0 | `SealGroundTruthUseCase.execute` → `raw_bytes = read_artifact_bytes(doc_id); detected_hashes[doc_id] = compute_sha256(raw_bytes)` | **Sellado sin validación de estructura.** Opera sobre bytes crudos sin hidratar vía contrato canónico ni ejecutar validación de dominio. Verifica E-0.2-005. Materializa gap DC-04. |
| **E-2.0-08** | P1 | `corpus/use_cases.py::LoadCorpusManifestUseCase.execute` | **Ausencia de verificación de integridad.** El `manifest_hash` almacenado nunca se contrasta con el recomputado; deriva silenciosa indetectable en lectura. |
| **E-2.0-09** | P1 | `corpus/ports.py::CorpusManifestLoaderPort` → `load_raw_manifest()` + `save_manifest_dto()` en el mismo Protocol | **Asimetría de puertos ausente en corpus.** Ruta de escritura (curaduría) y lectura (runtime) comparten contrato único. La asimetría sí existe parcialmente en ground_truth. Gap del Pilar 4. |
| **E-2.0-10** | P0 | Ausencia total: `compute_ast_hash` no aparece en ningún modelo, DTO, puerto o servicio de corpus/ground_truth | **$H_{semantic}$ huérfana en el modelo de baseline.** Lo único que viaja es `ground_truth_sha256` = SHA-256(bytes) (dimensión Integridad), excluido de la firma. La identidad semántica del Oráculo (NADR-03) no tiene hogar ontológico. Materialización de DF-01-C. |
| **E-2.0-11** | P1 | Ausencia total en los archivos auditados | **AST Schema Version inexistente.** El ADR Maestro §5 exige diferenciar AST Schema Version / Corpus Version / Identity Hash. Solo existe `CorpusVersion`. |
| **E-2.0-12** | P0 | `LocalFileSystemGroundTruthDraftWriter.save_draft_ast` escribe en `ground_truth/{doc_id}.json`, misma ruta que reader y `artifact_exists` | **Draft puede sobrescribir oráculo sellado sin guardia.** El writer no consulta estado de sello. No hay expresión a nivel de artefacto de la transición Draft→Sealed. Riesgo de corrupción de baseline por curaduría tardía. |
| **E-2.0-13** | P1 | `DocumentFingerprint` (VO: solo `sha256`) vs `ManifestFingerprintCalculator.compute_hash` (firma sobre `doc_id + sha256 + traits + page_count`) | **Desacople ontológico entre VO e identidad física firmada.** La "identidad física firmada" es una tupla de 4 campos, pero el VO porta 1. El ADR debe decidir si `DocumentFingerprint` se expande a la composición DC-02 o si la firma firma más de lo que el modelo declara. |
| **E-2.0-14** | P2 | `RawCorpusManifestDTO.documents: List[...]`, `CorpusManifest.documents: List[...]` en modelos `frozen=True` | **Mutabilidad profunda de colecciones en modelos congelados.** `frozen=True` no protege el contenido de una `List`. Viola literalmente ENGINEERING_PRINCIPLES §II ("Cero mutación in-place"). **Nota de riesgo latente:** no hay evidencia de explotación hoy; clasificación P2 por metodología de evidencia, no P1. El ADR debe decidir remediación preventiva o aceptación como deuda documentada. |
| **E-2.0-15** | P1 | `tools/evaluation/bootstrap_corpus.py` y `freeze_ground_truth.py` instancian `LocalFileSystemCorpusLoader` + adaptadores inline | **Entry points de evaluación con composición inline.** NADR-11 §5.1 R2 menciona explícitamente *herramientas de evaluación* como puntos de entrada que MUST delegar en la raíz de composición. Estos dos scripts no lo hacen. Contrasta con `generate_golden_draft.py` que sí usa `build_extraction_pipeline()`. **⚠ Hallazgo emergente post-Fase 1:** no fue documentado en Fase 0 porque las herramientas de evaluación no fueron auditadas contra NADR-11 (los HITOs 0.1–0.4.5 precedieron la promulgación de NADR-11), y Fase 1 aplicó NADR-11 exclusivamente al pipeline de producción, no a `tools/evaluation`. |
| **E-2.0-16** | P1 | `tools/evaluation/topology/fingerprint.py::ASTFingerprintPolicy` | **Fingerprint semántico vs hash global son ortogonales.** `semantic_fingerprint()` retorna tupla `(node_type, content)` para matching nodo-a-nodo; `compute_ast_hash()` es firma global del documento. **No son redundantes.** Cierra H-2.0-B. |
| **E-2.0-17** | P1 | `tools/evaluation/freeze_ground_truth.py` → `target_version="v1.0"` hardcodeado; `logger.critical()` captura excepciones genéricas pero `SealGroundTruthUseCase` no lanza excepciones por partial sealing | **Sellado con versión hardcodeada y fail-fast inefectivo.** El partial sealing (E-2.0-01) nunca dispara `logger.critical()` porque el use case no lanza excepción. Conecta con OBS-2.0-05. **⚠ Hallazgo emergente post-Fase 1:** no auditado en Fase 0 (entry points de `tools/evaluation` fuera del scope de los HITOs de runtime). |
| **E-2.0-18** | P1 | `tools/evaluation/generate_golden_draft.py` → `except FileNotFoundError as e: logger.warning(...)` y continúa | **Degradación de fail-fast.** `GenerateGoldenDraftUseCase` lanza `FileNotFoundError` si el PDF no existe, pero el entry point lo captura como WARNING y continúa. Viola ENGINEERING_PRINCIPLES §IV. **⚠ Hallazgo emergente post-Fase 1:** no auditado en Fase 0 (entry points de `tools/evaluation` fuera del scope de los HITOs de runtime). |

---

## 5. OBSERVACIONES COMPLEMENTARIAS (OBS-2.0-xx)

| ID | Observación |
|---|---|
| OBS-2.0-01 | `DocumentFingerprint.__post_init__` valida hex minúsculas pero **no longitud 64** (invariante incompleto). |
| OBS-2.0-02 | `CorpusVersion` es `str` sin validación SemVer (DC-09 sin materialización). |
| OBS-2.0-03 | Pre-image de `compute_hash`: concatenación `b"".join(parts)` **sin separador de dominios** entre versión y documentos (debilidad teórica de serialización canónica). |
| OBS-2.0-04 | `SealGroundTruthUseCase` reside en contexto `ground_truth` pero depende de `CorpusManifestLoaderPort` + `ManifestLineageSealer` (contexto `corpus`). Operación inter-contexto; frontera DDD debe formalizarse en ADR. |
| OBS-2.0-05 | El sellado **no incrementa `corpus_version`**; `target_version` aplica solo a `ground_truth_version` por documento (semántica de versionado ambigua, conecta con DC-09). |
| OBS-2.0-06 | `LoadCorpusManifestUseCase` documenta "Solo lectura O(1) RAM" pero ejecuta hidratación O(n) sin caché. |
| OBS-2.0-07 | **Biyección inversa no verificada:** artefactos GT huérfanos (presentes en disco, ausentes del manifiesto) son ignorados en el sellado. Es la otra mitad de $N_{PDF} = N_{GT}$. |
| OBS-2.0-08 | `BootstrapCorpusManifestUseCase` sí aplica fail-fast ante PDF ausente — asimetría de estrictez entre bootstrap (estricto) y sellado (permisivo). |
| OBS-2.0-09 | `CorpusToBenchmarkDatasetMapper._determine_complexity` usa matching de substrings sobre valores de traits (determinista pero frágil ante extensión del enum). |
| OBS-2.0-10 | Orden canónico interno del agregado: la serialización de `CorpusManifest` no es orden-canónica, aunque el hash sí ordena. |
| OBS-2.0-11 | `generate_golden_draft.py` instancia `BenchmarkParserBridge` dos veces (bloque duplicado). Duplicación menor de entry point, no arquitectónica. |
| OBS-2.0-12 | `LocalFileSystemCorpusRepository` (tools/evaluation) tiene nombre ambiguo; se recomienda renombrar a `BenchmarkCorpusLoader` o similar. Tarea de limpieza, no refactor arquitectónico. |

---

## 6. MATRIZ DE TRIAGE (clase por clase)

Claves: `RETAIN` (reutilizable conceptualmente) · `REFACTOR` (no retenible sin cambio de responsabilidad/contrato) · `RELOCATE` (ubicación incorrecta) · `DEPRECATE` (duplicado/obsoleto) · `MISSING` (capacidad inexistente) · `OUT-OF-SCOPE` (fuera de Fase 2, registrado).

### 6.1 `core/benchmark/corpus/`

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `RawDocumentEntryDTO` | RETAIN | DTO de transporte congelado, funcional. El linaje GT ya viaja aquí (aunque desconectado criptográficamente, E-2.0-02). |
| `RawCorpusManifestDTO` | RETAIN | Contrato de transporte estable. E-2.0-14 registrado. |
| `BootstrapCorpusResult` | RETAIN | DTO rico de salida operacional correcto. |
| `ExtractionChallengeTrait` | RETAIN | Vocabulario de curaduría tipado. |
| `CorpusToBenchmarkDatasetMapper` | RETAIN | Transformación legítima corpus→benchmark (Corolario P2: TRANSFORM ≠ VIOLATION). OBS-2.0-09 registrado. |
| `DocumentFingerprint` | RETAIN | VO de identidad física correcto en rol (precedente DF-01-D: no debe portar `ast_hash`). OBS-2.0-01 + E-2.0-13 son gaps de diseño posterior. |
| `CorpusVersion` | RETAIN | VO mínimo funcional. OBS-2.0-02 es gap de diseño posterior. |
| `CorpusDocumentMetadata` | RETAIN | Invariantes de campo correctas (`min_length`, `gt=0`, traits no vacío). |
| `CorpusManifest` | **REFACTOR** | **Defecto estructural real:** no valida no-vaciedad de `documents`, unicidad de `document_id`, orden canónico interno ni inmutabilidad profunda de la colección. Un Aggregate Root que permite `documents` vacía o duplicada no protege su propia consistencia. La clasificación REFACTOR implica tarea de corrección en el ADR/Execution Plan. |
| `DocumentMetadataExtractorPort` | RETAIN | Puerto limpio, adaptador real existente (`PyMuPdfDocumentMetadataExtractor`). |
| `CorpusManifestLoaderPort` | REFACTOR | E-2.0-09: unifica lectura/escritura; Pilar 4 exige asimetría. Dirección del cambio: decisión del ADR. |
| `ManifestFingerprintCalculator` | REFACTOR | E-2.0-02 + E-2.0-10: el pre-image debe incorporar el linaje que Fase 2 ontologice (mecanismo de encadenamiento es Fase 3). OBS-2.0-03. |
| `ManifestLineageSealer` | REFACTOR | E-2.0-01: materializa la permisividad del partial sealing; carece de invariante de biyección. **La estructura es recuperable; la política permisiva es la que debe reemplazarse.** Opera sobre DTO en vez de agregado (OBS-2.0-04). |
| `BootstrapCorpusManifestUseCase` | RETAIN | Camino de escritura sano (fail-fast en PDF ausente). Hereda E-2.0-05/E-2.0-06 del adaptador. |
| `LoadCorpusManifestUseCase` | REFACTOR | E-2.0-08: sin verificación de integridad del hash almacenado. OBS-2.0-06. |

### 6.2 `core/benchmark/ground_truth/`

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `GroundTruthError` / `EmptyGroundTruthDraftError` | RETAIN | Taxonomía de errores base correcta y usada. |
| `GroundTruthReaderPort` | RETAIN | Superficie de lectura runtime; implementada con contrato canónico (NADR-01 §5.9). |
| `GroundTruthDraftWriterPort` | RETAIN | Superficie de curaduría legítima (ver §10.3). |
| `ASTExtractionPort` | RETAIN | Desacopla del motor de extracción; implementado por `BenchmarkParserBridge`. |
| `GroundTruthArtifactPort` | RETAIN | Adaptador físico puro. Su uso actual en sellado habilita E-2.0-07; el gap no es el puerto sino la ausencia de compuerta de validez aguas arriba. |
| `ManifestGroundTruthUpdater` | **DEPRECATE** | E-2.0-03: duplicado línea por línea de `ManifestLineageSealer`, 0 llamadores. Código huérfano con autoridad duplicada. |
| `LoadGroundTruthUseCase` | RETAIN | Delgado, fail-fast en `document_id` vacío, delegación correcta. |
| `GenerateGoldenDraftUseCase` | RETAIN | Fail-fast en extracción vacía correcto. E-2.0-12 es gap de lifecycle, no del caso de uso. |
| `SealGroundTruthUseCase` | REFACTOR | E-2.0-01 + E-2.0-07: omisión silenciosa de oráculos ausentes y sellado sin validación. **Contiene lógica de dominio legítima con invariantes ausentes.** Estructura hexagonal sana (todo I/O vía puertos). |
| *Oráculo como entidad de dominio* | MISSING | No existe concepto `Oracle` en ningún archivo auditado. |
| *Estados de ciclo de vida* | MISSING | E-2.0-04. |
| *Contrato de validez Draft→Oracle (DC-04)* | MISSING | E-2.0-07. |

### 6.3 `infra/fs/`

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `LocalFileSystemCorpusLoader` | REFACTOR | E-2.0-05 (default silencioso) + E-2.0-06 (escritura no atómica). |
| `LocalFileSystemGroundTruthReader` | RETAIN | Fail-fast + contrato canónico. Sano. |
| `LocalFileSystemGroundTruthDraftWriter` | RETAIN | Escritura atómica vía `write_ast_json_atomic`. Sano. E-2.0-12 es gap de dominio. |
| `LocalFileSystemGroundTruthArtifactAdapter` | RETAIN | Contacto físico puro, sin lógica. |

### 6.4 `tools/evaluation/` (insumo secundario)

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `bootstrap_corpus.py` | REFACTOR | E-2.0-15: composición inline contraria a NADR-11 §5.1 R2. |
| `freeze_ground_truth.py` | REFACTOR | E-2.0-15 + E-2.0-17: composición inline + `target_version` hardcodeado + fail-fast inefectivo. |
| `generate_golden_draft.py` | REFACTOR | Usa `build_extraction_pipeline()` (NADR-11 parcial ✅), pero E-2.0-18 (degrada fail-fast) + OBS-2.0-11 (duplicación). |
| `TopologyBenchmarkService` | RETAIN | Servicio de aplicación puro, opera en memoria, sin I/O. (Fase 4, out-of-scope de Fase 2.) |
| `ASTFingerprintPolicy` | RETAIN | Mecanismo ortogonal a `compute_ast_hash()` (E-2.0-16). |
| `LocalFileSystemCorpusRepository` | RETAIN | NO es duplicado de `LocalFileSystemCorpusLoader`; responsabilidades distintas (carga pares candidate/GT para evaluación vs carga manifest). OBS-2.0-12 (nomenclatura). |

### 6.5 `core/benchmark/ports.py` (insumo secundario)

| Componente | Clasificación | Justificación forense |
|---|---|---|
| `BenchmarkRunnerProtocol` | RETAIN | Puerto abstracto para runners asíncronos. |
| `BenchmarkCandidateProvider` | RETAIN | Contrato abstracto para proveedores de candidatos. |
| `BenchmarkEvaluatorProtocol` | RETAIN | Contrato abstracto para métricas. |
| `GroundTruthProviderProtocol` | RETAIN | Solapamiento conceptual con `GroundTruthReaderPort` pero no técnico (bounded contexts distintos; retorna `Any` vs `Sequence[ASTNode]`). |

### 6.6 Resumen por categoría

| Categoría | Cantidad | Detalle |
|---|---|---|
| **RETAIN** | 27 | VO/DTO/enum/puertos de lectura/adaptadores GT sanos + tools/evaluation + ports.py |
| **REFACTOR** | 10 | `CorpusManifest`, `CorpusManifestLoaderPort`, `ManifestFingerprintCalculator`, `ManifestLineageSealer`, `LoadCorpusManifestUseCase`, `SealGroundTruthUseCase`, `LocalFileSystemCorpusLoader`, `bootstrap_corpus.py`, `freeze_ground_truth.py`, `generate_golden_draft.py` |
| **RELOCATE** | 0 | Frontera hexagonal respetada en todos los módulos auditados |
| **DEPRECATE** | 1 | `ManifestGroundTruthUpdater` |
| **MISSING** | 12 | Ver §8 (alineado con GAP-2.0-01..12) |

---

## 7. MATRIZ EXISTENTE / FALTANTE contra los 4 Pilares

### Pilar 1 — Ontología Pura

| Elemento | Estado | Evidencia |
|---|---|---|
| `CorpusManifest` como Aggregate Root | ✅ EXISTENTE (con defectos de invariantes internos) | `models.py`, puro, frozen |
| `DocumentFingerprint` (identidad física) | ✅ EXISTENTE (débil) | VO con invariante hex; solo SHA-256 del binario |
| `CorpusVersion` | ✅ EXISTENTE (débil) | Sin semántica SemVer (OBS-2.0-02) |
| `CorpusDocumentMetadata` | ✅ EXISTENTE | Invariantes de campo correctas |
| **El Oráculo como objeto de dominio** | ❌ FALTANTE | E-2.0-10 |
| **Hogar ontológico para $H_{semantic}$** | ❌ FALTANTE | E-2.0-10 |
| **AST Schema Version** | ❌ FALTANTE | E-2.0-11 |
| **Estado de sello en el agregado** | ❌ FALTANTE | E-2.0-04 |

### Pilar 2 — Ciclo de Vida (DC-05)

| Elemento | Estado | Evidencia |
|---|---|---|
| Estados `Draft → Audited → Validated → Sealed` | ❌ FALTANTE | No existe enum ni tipo alguno de estado |
| Tipos disjuntos Draft vs Oracle | ❌ FALTANTE | Solo existe `Sequence[ASTNode]` sin envoltorio de estado |
| Autoridad de transición | ❌ FALTANTE | El "sello" es un side-effect sobre campos Optional del DTO |
| Guardas contra transiciones ilegales | ❌ FALTANTE | E-2.0-12 |
| Eventos de invalidez de sello (DC-08) | ❌ FALTANTE | Cambio de PDF, mutación de AST o cambio de esquema no invalidan nada |

**Veredicto del pilar:** La hipótesis del mandato queda validada: modelar el ciclo de vida con tipos disjuntos es necesario. El estado actual no permite distinguir un borrador de un oráculo sellado.

### Pilar 3 — Invariantes de Validez (DC-04)

| Elemento | Estado | Evidencia |
|---|---|---|
| No-vaciedad en drafting | ✅ EXISTENTE | `EmptyGroundTruthDraftError` |
| Fail-fast ante PDF ausente (bootstrap) | ✅ EXISTENTE | `FileNotFoundError` en `BootstrapCorpusManifestUseCase` |
| Fail-fast ante oráculo ausente (lectura runtime) | ✅ EXISTENTE | `FileNotFoundError` en reader |
| Validación de campos de metadatos | ✅ EXISTENTE | `min_length=1`, `gt=0`, traits no vacío |
| **Completitud del sello (biyección $N_{PDF}=N_{GT}$)** | ❌ FALTANTE | E-2.0-01 |
| **Biyección inversa (sin GT huérfanos)** | ❌ FALTANTE | OBS-2.0-07 |
| **Validación estructural antes del sello** | ❌ FALTANTE | E-2.0-07 |
| **Verificación de integridad del manifiesto en carga** | ❌ FALTANTE | E-2.0-08 |
| Invariante de longitud de fingerprint | ❌ FALTANTE | OBS-2.0-01 |

**Veredicto del pilar:** Existen invariantes físicas básicas, pero faltan las invariantes científicas esenciales para que un AST sea considerado oráculo válido.

### Pilar 4 — Asimetría de Puertos

| Elemento | Estado | Evidencia |
|---|---|---|
| Separación Reader/Writer en ground_truth | ✅ EXISTENTE | `GroundTruthReaderPort` vs `GroundTruthDraftWriterPort` |
| Puerto de artefacto físico separado | ✅ EXISTENTE | `GroundTruthArtifactPort` |
| Puerto de extracción desacoplado | ✅ EXISTENTE | `ASTExtractionPort` → `BenchmarkParserBridge` |
| Escritura atómica de oráculos | ✅ EXISTENTE | `write_ast_json_atomic` |
| Hidratación canónica en lectura | ✅ EXISTENTE | `read_ast_json` (NADR-01 §5.9) |
| **Asimetría en corpus (Write/Curator vs Read/Oracle)** | ❌ FALTANTE | E-2.0-09 |
| **Superficie de lectura O(1)/fail-fast estricta** | ⚠ PARCIAL | Fail-fast presente en GT; ausente en manifiesto (E-2.0-05) |
| **Entry points delegan en Composition Root** | ⚠ PARCIAL | `generate_golden_draft.py` parcial; `bootstrap_corpus.py` y `freeze_ground_truth.py` no (E-2.0-15) |
| Solapamiento `GroundTruthProviderProtocol` vs `GroundTruthReaderPort` | ✅ RESUELTO | E-2.0-16: bounded contexts distintos, no técnico |

---

## 8. GAPS ARQUITECTÓNICOS CONSOLIDADOS (GAP-2.0-xx)

| GAP | Descripción | Evidencia | Pilar | Fase destino |
|---|---|---|---|---|
| **GAP-2.0-01** | Ausencia del Oráculo como entidad ontológica de dominio | E-2.0-10 | P1 | **Fase 2** |
| **GAP-2.0-02** | Ausencia total de ciclo de vida del Ground Truth (DC-05) | E-2.0-04, E-2.0-12, OBS-2.0-05 | P2 | **Fase 2** |
| **GAP-2.0-03** | Ausencia de contrato de validez Draft→Oracle (DC-04) | E-2.0-07 | P3 | **Fase 2** |
| **GAP-2.0-04** | Ausencia de asimetría de puertos en contexto corpus | E-2.0-09 | P4 | **Fase 2** |
| **GAP-2.0-05** | $H_{semantic}$ huérfana: sin linaje en el modelo de baseline (DF-01-C) | E-2.0-10, E-2.0-02 | P1/P3 | **Fase 2** (ontología); encadenamiento en **Fase 3** |
| **GAP-2.0-06** | AST Schema Version ausente del desacoplamiento de identidades | E-2.0-11 | P1 | **Fase 2** |
| **GAP-2.0-07** | Invariante de biyección incompleto (ambas direcciones) | E-2.0-01, OBS-2.0-07 | P3 | **Fase 2** |
| **GAP-2.0-08** | Sin verificación de integridad del manifiesto en lectura | E-2.0-08 | P3 | **Fase 2 / Fase 3** según ADR |
| **GAP-2.0-09** | Inconsistencia SRE en fronteras de persistencia (atomicidad + fail-fast) | E-2.0-05, E-2.0-06 | P4 | **Fase 2** si toca baseline |
| **GAP-2.0-10** | Sin semántica de invalidez de sello (DC-08) | OBS-2.0-05, E-2.0-02 | P2 | **Fase 2** (eventos); **Fase 3** (encadenamiento) |
| **GAP-2.0-11** | Adaptador de integración baseline→benchmark ausente | H-2.0-H cerrada | P4 | **Fase 4** (Scientific Verification), no Fase 2 |
| **GAP-2.0-12** | Herramienta de re-sellado/migración post-cambio-de-fórmula inexistente (`tools/reseal_corpus.py` referido por MIG-01 no existe) | OBS-P2-01, MIG-01 TODO | P3 | **Fase 3** (Identity & Trust Model), no Fase 2 |

---

## 9. ESTADO DE HIPÓTESIS DEL DISCOVERY

| ID | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| H-2.0-A | Lógica permisiva de partial sealing en `SealGroundTruthUseCase` | ✅ **CONFIRMADA** | E-2.0-01 |
| H-2.0-B | Dualidad de fingerprinting (`compute_ast_hash` vs `ASTFingerprintPolicy`) | ✅ **RESUELTA** | E-2.0-16: son mecanismos ortogonales, no redundantes |
| H-2.0-C | Divergencia entre `LocalFileSystemCorpusLoader` e `LocalFileSystemCorpusRepository` | ✅ **RESUELTA** | NO es divergencia; son responsabilidades distintas (manifest vs pares candidate/GT) |
| H-2.0-D | Ciclo de vida DC-05 sin modelar | ✅ **CONFIRMADA** | E-2.0-04 |
| H-2.0-E | Artefactos sellados pre-1.2.4 (fórmula vieja) | ⏳ **NO VERIFICABLE desde código** | MIG-01 sigue TODO; `tools/reseal_corpus.py` no existe (OBS-P2-01 confirmado). Requiere inspección de artefactos en disco. |
| H-2.0-F | `ManifestGroundTruthUpdater` duplicado superviviente de Fase 1 | ✅ **CONFIRMADA** | E-2.0-03 |
| H-2.0-G | Firma del manifiesto excluye hashes GT | ✅ **CONFIRMADA** | E-2.0-02 |
| H-2.0-H | Solapamiento `GroundTruthProviderProtocol` vs `GroundTruthReaderPort` | ✅ **RESUELTA** | Solapamiento conceptual pero no técnico; bounded contexts distintos |

**Condición de cierre:** 8 hipótesis cerradas (5 confirmadas, 3 resueltas), 1 no verificable desde código (H-2.0-E, requiere inspección de artefactos en disco — no bloquea el Discovery).

---

## 10. RESPUESTAS A LAS PREGUNTAS DEL MANDATO

### 10.1 DF-01-C — Rol ontológico de `compute_ast_hash()` y su relación con `DocumentFingerprint`

**Nota terminológica — H_physical vs H_runtime:**

Este documento utiliza la dimensión **$H_{physical}$** para referirse a la **integridad del documento fuente PDF** (SHA-256 del binario, portada por `DocumentFingerprint.sha256`). Esta dimensión corresponde a la **Dimensión 1 — INTEGRIDAD** del ADR Maestro §3 y al candidato **DC-02** (composición del hash físico).

**$H_{physical}$ NO debe confundirse con $H_{runtime}$**, definida en HITO_0.3 como la identidad operacional de los nodos AST durante el procesamiento (`node_id`, `parent_node_id`, geometrías, metadatos de confianza). $H_{runtime}$ es exclusiva de trazabilidad/renderizado y está **excluida de toda firma** por NADR-03 §5.1 R2. Ambas son "físicas" en sentidos distintos: $H_{physical}$ es integridad del artefacto fuente; $H_{runtime}$ es identidad efímera de instancia de nodo. Ninguna de las dos constituye identidad semántica ni identidad de baseline.

**Estado actual verificado (evidencia, no diseño):**

1. `compute_ast_hash()` produce $H_{semantic}$ (NADR-03 §4.1) — la identidad semántica del documento, determinista e inmune a runtime. **Hoy ese valor no viaja en ninguna parte del modelo de baseline**: no está en `CorpusManifest`, no está en `RawDocumentEntryDTO`, no está en ningún puerto auditado (E-2.0-10).
2. Lo único que viaja es `RawDocumentEntryDTO.ground_truth_sha256`, que el sellado calcula como **SHA-256 de los bytes del archivo** (`compute_sha256(raw_bytes)`) — dimensión **Integridad** (ADR Maestro §3, dimensión 1), no Identidad Semántica.
3. Ese hash de integridad está además **excluido de la firma global** (E-2.0-02), por lo que hoy no protege nada.
4. `DocumentFingerprint` porta exclusivamente el SHA-256 del binario PDF — identidad **física** ($H_{physical}$) del documento fuente.

**Taxonomía tridimensional de la identidad (NADR-03 §4.1):**

```text
compute_ast_hash()
  → H_semantic (Identidad Semántica)
  → composición: tipo semántico, contenido normalizado, orden secuencial relativo, profundidad jerárquica
  → NO incluye node_id, parent_id, bbox, session ids, worker ids
  → NO es identidad física del PDF (H_physical)
  → NO es identidad de runtime (H_runtime)
  → NO es H_baseline global

DocumentFingerprint.sha256
  → H_physical (Integridad física del documento fuente)
  → SHA-256 del binario PDF

H_baseline
  → encadena H_physical + H_semantic + CorpusVersion + AST Schema Version
  → responsabilidad de Fase 3 (mecanismo), ontología en Fase 2
```

**Respuesta arquitectónica (marco normativo, pendiente de formalización en ADR):**

- El rol ontológico de `compute_ast_hash()` es ser **la identidad semántica del Oráculo**: lo que el oráculo *es* como verdad científica, independiente del archivo que lo serializa y del runtime que lo produjo.
- La relación con `DocumentFingerprint` es de **ortogonalidad con encadenamiento futuro**: identidad física del PDF fuente e identidad semántica del oráculo son dimensiones distintas que $H_{baseline}$ debe encadenar (Fase 3), **sin colapsarlas jamás** — precedente vinculante DF-01-D (cerrado NAR en Fase 1: agregar `ast_hash` a `DocumentFingerprint` violaría ADR Maestro §3).
- El Discovery confirma que el eslabón ausente no es el hash (NADR-03 ya lo gobierna y Fase 1 lo materializó), sino **el lugar ontológico donde $H_{semantic}$ reside y el mecanismo que lo encadena** con $H_{physical}$, `CorpusVersion` y AST Schema Version.

### 10.2 Auditoría de `SealGroundTruthUseCase` y `ManifestLineageSealer`

**Veredicto: contienen lógica de dominio LEGÍTIMA con invariantes AUSENTES. No son filtraciones prematuras de Fase 3/5.**

| Pregunta | Respuesta forense |
|---|---|
| ¿I/O directo en el caso de uso? | **No.** Todo I/O delega en puertos (`CorpusManifestLoaderPort`, `GroundTruthArtifactPort`). Frontera hexagonal limpia. |
| ¿Hashing de transporte ilegítimo? | **No es ilegítimo:** `compute_sha256(bytes)` es el hash de integridad (dimensión 1) que el linaje necesita. El defecto no es que exista, sino que su resultado es **descartado criptográficamente** por `ManifestFingerprintCalculator` (E-2.0-02). |
| ¿Validación de invariantes presente? | **Parcialmente ausente:** falta la invariante de completitud (biyección, E-2.0-01) y la de validez estructural (E-2.0-07). Lo que hay (recolección de integridad + aplicación de linaje) es dominio legítimo. |
| ¿`ManifestLineageSealer`? | Servicio de dominio puro (estático, sin estado, sin I/O). Materializa la permisividad del partial sealing por diseño: itera y conserva valores previos para documentos sin hash detectado, sin compuerta de completitud. Opera sobre DTO en lugar del agregado (OBS-2.0-04). |
| ¿`ManifestGroundTruthUpdater`? | Duplicado línea por línea, 0 consumidores → **DEPRECATE** (E-2.0-03). |

### 10.3 `GroundTruthDraftWriterPort` — ¿capacidad ontológica del núcleo o herramienta de curaduría?

**Veredicto forense: el puerto es una capacidad de CURADURÍA (superficie de escritura del bootstrap); lo que pertenece al núcleo ontológico es el contrato de qué ES un Draft.**

Evidencia:
- El puerto existe exclusivamente para la campaña de generación de borradores (`GenerateGoldenDraftUseCase`), no tiene ningún consumidor en runtime (la lectura va por `GroundTruthReaderPort`).
- Su implementación es atómica (`write_ast_json_atomic`) y correcta.
- El Pilar 4 del mandato exige exactamente esta asimetría: Write/Curator Port para bootstrap, Read/Oracle Port para ejecución. En ground_truth la asimetría **ya existe** (a diferencia de corpus, E-2.0-09).
- Sin embargo, la evidencia E-2.0-12 demuestra que **el concepto ontológico de Draft no está formalizado**: draft y oráculo comparten la misma ruta física, el writer no consulta estado de sello, y nada distingue un borrador de un oráculo salvo la intención humana. El puerto se RETAIN; la ontología del Draft es MISSING y corresponde al ADR de Fase 2.

---

## 11. VERIFICACIÓN DE CUMPLIMIENTO NADR-11

NADR-11 §5.1 R2: *"Todo punto de entrada (CLI, API, daemon, herramienta de evaluación) MUST delegar la construcción del pipeline a la raíz de composición."* Nota: las herramientas de evaluación están **explícitamente** mencionadas en la regla; no procede suavizar el hallazgo clasificándolas como "scripts de curaduría fuera de la regla".

| Entry point | ¿Usa Composition Root? | ¿Cumple NADR-11 §5.1 R2? |
|---|---|---|
| `bootstrap_corpus.py` | No (composición inline) | ❌ No — E-2.0-15 |
| `freeze_ground_truth.py` | No (composición inline) | ❌ No — E-2.0-15 |
| `generate_golden_draft.py` | Sí (`build_extraction_pipeline()`) | ⚠ Parcial — usa Composition Root para el parser, pero degrada fail-fast (E-2.0-18) y tiene duplicación (OBS-2.0-11) |
| `run_benchmark.py` | No auditado en este HITO | ⏳ Pendiente (Fase 4) |

---

## 12. APÉNDICE NO NORMATIVO — Riesgos arquitectónicos para el ADR

| Riesgo | Descripción | Impacto |
|---|---|---|
| Confusión Integridad/Identidad | `ground_truth_sha256` se usa como identidad semántica | Baseline no certificable |
| Partial Sealing | Sellado sin exigir $N_{PDF} = N_{GT}$ | Viola ADR Maestro §5 |
| Draft/Oracle indistinguibles | Mismo path y mismo tipo de lectura | No hay lifecycle ni inmutabilidad |
| Duplicación de autoridad | `ManifestLineageSealer` vs `ManifestGroundTruthUpdater` | Ambigüedad de responsabilidad |
| Manifest hash ciego al GT | `manifest_hash` no cambia si cambia ground truth | No protege contra mutaciones silenciosas |
| Puerto mixto | `CorpusManifestLoaderPort` lee y escribe | Rompe asimetría read/curator |
| Fail-open en infra | Manifest ausente devuelve corpus vacío | Viola fail-fast en runtime |
| Colecciones no profundamente inmutables | `List` en modelos frozen | Riesgo de mutación accidental |
| Entry points fuera de Composition Root | `bootstrap_corpus.py`, `freeze_ground_truth.py` | Viola NADR-11 §5.1 R2 |
| Desacople VO/firma | `DocumentFingerprint` porta 1 campo, firma usa 4 | Ambigüedad ontológica (E-2.0-13) |

---

## 13. APÉNDICE NO NORMATIVO — Preguntas que el ADR_F17_BIS_02 debe responder

Con base en este Discovery, el ADR de Fase 2 deberá responder:

1. ¿El Ground Truth se modela como tipos disjuntos `Draft` y `Oracle`?
2. ¿El estado `Sealed` es un tipo inmutable construido solo tras validar invariantes?
3. ¿Qué invariante define que un AST es un oráculo válido?
4. ¿Quién posee la autoridad de sellado?
5. ¿Cómo se separan Write/Curator y Read/Oracle?
6. ¿Qué identidades viajan en el Oracle?
7. ¿Cómo se preserva la separación entre:
   - physical fingerprint,
   - artifact integrity,
   - semantic hash,
   - baseline identity?

---

## 14. CIERRE DEL HITO 2.0

Este Discovery confirma que la Fase 2 es necesaria y no puede reducirse a una limpieza de módulos. El problema central no es de I/O ni de hashing, sino de ontología de la verdad científica.

El sistema actual puede generar y almacenar ground truth, pero todavía no puede demostrar que ese ground truth es:

- completo,
- válido,
- sellado,
- inmutable,
- semánticamente identificado,
- y distinguible de un simple draft.

Ese es exactamente el vacío que Fase 2 debe formalizar antes de que Fase 3 construya el Identity & Trust Model.

**Estado del HITO 2.0:** ✅ FROZEN v2.1.0-SOTA
**Condición de cierre cumplida:** 100% de módulos primarios y secundarios auditados · 8 hipótesis cerradas · 18 evidencias forenses registradas · 12 observaciones complementarias · 12 gaps consolidados con fase destino · triaje de 38 componentes completado · matriz de trazabilidad DC integrada (§15).
**Verificación de cadena de gobernanza:** ADR Maestro → ADR_F17_BIS_0 → HITOs 0.1–0.5 → Gap Matrix → NADRs 01–11 → Execution Plan Fase 1 → Findings Register Fase 1. **Cero regresiones, cero solapamientos, cero contradicciones.**
**Siguiente paso recomendado:** Construir `ADR_F17_BIS_02` usando este HITO como Evidencia Forense Vinculante, respondiendo las 7 preguntas del §13 y materializando los gaps GAP-2.0-01..10 de Fase 2.

---

## 15. MATRIZ DE TRAZABILIDAD DC (DECISION CANDIDATES → HITO 2.0)

**Nota de gobernanza:** Los DC-01 a DC-11 fueron resueltos normativamente en Fase 0 (HITO_0.5), materializados en el corpus de NADRs según ADR Maestro §8 ("ESTADO FINAL: RESUELTOS Post-Fase 0"). Esta matriz rastrea la **materialización operativa en código**, que es lo que HITO 2.0 audita. Una resolución normativa no equivale a implementación; las fases ejecutan la implementación.

| DC | Tema (ADR Maestro §8) | Evidencia HITO 2.0 vinculada | Estado operativo en código (post-Fase 1) | Fase destino |
|---|---|---|---|---|
| **DC-01** | Mecanismo de Hash de Identidad (Merkle vs hash compuesto canónico determinista) | OBS-2.0-03 (pre-image sin separador de dominios) | Resuelto normativamente como hash compuesto determinista (no Merkle). Mecanismo de encadenamiento pendiente. | **Fase 3** |
| **DC-02** | Composición del Hash Físico $H_{physical}$ | E-2.0-13 (desacople VO/firma), OBS-2.0-01 (longitud 64) | `DocumentFingerprint` porta solo SHA-256; la firma usa 4 campos. Composición DC-02 pendiente de formalización ontológica. | **Fase 2 / Fase 3** |
| **DC-03** | Composición del Hash Global $H_{baseline}$ | GAP-2.0-05, E-2.0-02, E-2.0-10 | Ausente. El encadenamiento $H_{physical}$ + $H_{semantic}$ + versiones no existe. | **Fase 3** |
| **DC-04** | Contrato de Validez del Ground Truth (invariantes Draft vs Oráculo) | GAP-2.0-03, E-2.0-07 | Ausente. `SealGroundTruthUseCase` no invoca `ASTValidator` antes de sellar. | **Fase 2** |
| **DC-05** | Ciclo de Vida del Ground Truth (`Draft→Audited→Validated→Sealed`) | GAP-2.0-02, E-2.0-04, E-2.0-12 | Ausente. No existe enum de estados ni autoridad de transición. | **Fase 2** |
| **DC-06** | Taxonomía de Criticidad de Nodos (`ContentNodeType` → `CRITICAL/WARNING/INFO`) | — | Fuera de scope de Fase 2 (dominio de regresión topológica). | **Fase 4** |
| **DC-07** | Reglas de Regresión Topológica (`HARD FAIL` vs `WARNING`) | — | Fuera de scope de Fase 2 (dominio de regresión topológica). | **Fase 4** |
| **DC-08** | Desacoplamiento de Versiones e Invalidez de Sello | GAP-2.0-10, E-2.0-11, OBS-2.0-05 | Ausente. AST Schema Version inexistente; no hay eventos de invalidación de sello. | **Fase 2** (eventos) / **Fase 3** (encadenamiento) |
| **DC-09** | Esquema de Versionado y Compatibilidad (SemVer del corpus) | OBS-2.0-02, OBS-2.0-05 | Ausente. `CorpusVersion` es `str` sin semántica SemVer; el sellado no incrementa versión. | **Fase 2 / Fase 3** |
| **DC-10** | Desacoplamiento del Runner de CI (pytest consume casos de uso del dominio) | — | Fuera de scope de Fase 2 (dominio de CI). | **Fase 6** |
| **DC-11** | Contrato de Fronteras entre Capas (Domain/Application/Infrastructure/CI) | E-2.0-15, §11 (verificación NADR-11) | Parcial. Frontera hexagonal respetada en `core/` e `infra/`; entry points de `tools/evaluation` con composición inline. | **Fase 2** |

**Resumen de trazabilidad DC para Fase 2:** Los DCs que Fase 2 debe materializar operativamente son **DC-02 (parcial), DC-04, DC-05, DC-08 (eventos), DC-09 y DC-11**. Los DCs **DC-01, DC-03 y DC-08 (encadenamiento)** corresponden a Fase 3. Los DCs **DC-06, DC-07** corresponden a Fase 4 y **DC-10** a Fase 6.

---

**Fin del HITO 2.0 FROZEN v2.1.0-SOTA.**