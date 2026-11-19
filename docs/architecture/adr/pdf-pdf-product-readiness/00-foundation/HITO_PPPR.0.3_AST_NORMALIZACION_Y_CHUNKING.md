# HITO_PPPR.0.3_AST_NORMALIZACION_Y_CHUNKING.md

**Estado:** IN_PROGRESS v1.0.2  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** N/A  
**Iniciativa:** PPPR, Fase 0 transversal — `pdf-pdf-product-readiness`  
**Tipo de artefacto:** Forensic Flow Audit (AST, normalización y construcción de plan)  
**Naturaleza:** Auditoría read-only; no prescribe arquitectura ni implementación.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@084158a9ad1f06b4d58dc38852157c2b3f01d201` (incluye PPPR.0.1/0.2 FROZEN).  
**Fuentes vinculantes:** metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y Atlas de ruta; PPPR.0.1 FROZEN v1.0.9 y PPPR.0.2 FROZEN v1.0.3; NADR-F17BIS-03 (§5.1/5.3/5.4) y NADR-F17BIS-16 (§5.2) cotejados directamente; NADR-F17BIS-01/05/06 con fronteras delimitadas.  
**Mandato:** Auditar la ruta conectada desde AST de extracción hasta enriquecimiento, normalización, segmentación, chunking semántico y `ChunkPlan`, distinguiendo identidad semántica, cobertura de miembros, preservación STEM y límites de prueba; no auditar efectos físicos de G3/G5 ni decisiones de proveedor.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura posterior al merge interno #67, con primera lectura directa de composición OCR, AST/hash, contexto, chunker y manifest; frontera provisional y cuestiones falsables. No tests ejecutados ni FROZEN. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Segunda pasada: NADR-F17BIS-03/16 contrastados; ruta OCR real vs alternativa/histórica; cobertura de manifest, contexto y tests; E-0.3-009…017, ficha P1 jerárquica, GAP local y candidatos sin decisiones anticipadas. No tests ejecutados ni FROZEN. |
| 1.0.2-IN_PROGRESS | 2026-11-19 | Tercera pasada: H-0.3-F/G clasificadas, secuencia física de encabezados y política PRESERVE verificadas; E-0.3-018…020, normalización de pre-image contrastada con NADR-03 R4; nueva ficha P1, matriz de cumplimiento y triaje de DC/DQ. Sin ejecutar pruebas, cambiar producción ni FROZEN. |

## 1. RESUMEN EJECUTIVO

La composición seleccionada en `OCRRouterDaemon._process_document` calcula `compute_ast_hash(raw_ast)`, prepara el plan contextual mediante `prepare_contextual_plan`, valida la igualdad del hash semántico después del enriquecimiento, materializa `ChunkPlan` y luego pasa a persistencia/estado de otra frontera. Esto no presupone que todos los normalizadores del repositorio se ejecuten en esa ruta.

**Hallazgo central:**

> El AST semántico y su plan de trabajo disponen de contratos explícitos de hash, pertenencia, orden y preservación, pero sus garantías son distintas del linaje físico y de la fidelidad científica.

**Revisión v1.0.2:** el hash operativo del AST se usa como identidad de generación, mientras su contrato declarado se diseñó para comparación de parsers. El pre-image omite jerarquía (E-010) y carece de normalización canónica documentada/ejecutada de contenido Unicode (E-020), contrarios a NADR-F17BIS-03 §5.1 R1/R4. Se registran **dos GAP P1 locales** que describen incumplimientos estáticos de contrato; no se infieren colisiones SHA-256, errores de reutilización realmente ocurridos ni corrupción del PDF final. Los encabezados PRESERVE y niveles UNKNOWN están observados, sin política de aceptación científica aprobada.

**Veredicto de esta pasada:** H-0.3-F/G quedan determinadas como comportamientos estáticos (no decisiones de producto). El pre-image de firma incumple dos requisitos diferenciados de NADR-F17BIS-03: jerarquía (R1) y normalización canónica (R4), sin demostrar fallo físico en una publicación. Existen guardias adicionales sobre contexto y manifest, pero no sustituyen la identidad semántica. Queda pendiente el control de cierre del perímetro. **IN_PROGRESS**, sin implementación autorizada.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **OBSERVADO:** lectura directa del código del SHA indicado, sin ejecutar los componentes; los tests existentes pueden aportar alcance de sus aserciones, no resultados nuevos.
- **REQUIRED:** trazabilidad y explicitud del scope/principios, contratos implementados de hash semántico, segmentación y manifest. Verificar literalmente NADRs aplicables antes de atribuirles obligaciones.
- **DECISION:** D-1/D-2 fijaron la ruta productiva; PPPR.0.2 congeló la frontera de extracción sin certificar orden científico. Mantener distintos el hash semántico de parser y la identidad canónica de oráculo.
- **NO VERIFICABLE EN ESTA APERTURA:** tasa de error sobre papers reales, linaje de GT, validez de una sutura concreta, calidad de traducción, persistencia y generación física.
- **NO EJECUTADO:** pytest, PyMuPDF, OCR, servicios comerciales, compilador, GT/corpus o SQLite.

## 3. ALCANCE AUDITADO — SEGUNDA PASADA

La cobertura es por **responsabilidad en la ruta elegida**, no por inferencia de inexistencia de otras rutas. `AUDITADO` significa lectura directa del símbolo del SHA, no test ejecutado ni certificación científica.

| Frontera | Código y propiedad contrastada | Estado | Límite/destino |
|---|---|---|---|
| Root OCR | `apps/ocr_router/__main__.py::_process_document`; hash, estimator, `prepare_contextual_plan`, registro posterior | **AUDITADO** | Reintentos, journal, transacciones y durabilidad: 0.5 |
| Parser→AST | `core/ast/{builder,models,cross_page,strategy}.py`, `core/layout/models.py`, mapper de `apps/bootstrap/pipeline_factory.py`; orden, tipos, metadatos y nivel | **AUDITADO focal**; reuso 0.2 | Calidad física de origen: PPPR.0.2/0.8 |
| Firma semántica | `core/ast/hashing.py::compute_ast_hash`; pre-image, exclusiones y consumidores | **AUDITADO** | Firma distinta de oráculo; integridad de mutaciones en persistencia: 0.5 |
| Contextualización conectada | `core/chunking/contextual_plan.py`, `core/normalization/enrichers/context_enricher.py`, `core/context/plan_context_contract.py` | **AUDITADO** | Identidad y efectividad del prompt/proveedor: 0.4/0.5 |
| Chunking efectivo | `core/chunking/{semantic_chunking,manifest_contract}.py`, `core/ast/models.py`; membresía, order, hash, saltos de contexto y overflows | **AUDITADO** | Calidad lingüística y límite del tokenizador de proveedor: 0.4/0.8 |
| Capacidades alternativas | `core/normalization/{pipeline,bootstrap,classifier,normalizer,explicit_math}.py`, `core/ast/{segmenter,grouper}.py`, `core/chunking/chunker.py`, `core/pipeline/orchestrator.py` | **AUDITADO para distinguir ruta seleccionada de otra**; interior completo de alternativas no auditado | No clasificar como GAP por no estar conectadas al root D-1/D-2 |
| Tests versionados | `test_g3_chunk_identity_contract`, `test_chunker_snapshot`, `test_semantic_chunker`, `test_context_enricher`, `test_w08_ocr_g3_context_wiring`, `test_w08_durable_context_boundary` | **AUDITADOS como código, NOT_RUN** | No verifican fidelidad de PDFs científicos ni proveedor real |
| Normativa y antecedente | NADR-F17BIS-03, -16, -01, -05; HITO F17-BIS 0.4.5-P3 (histórico) | **LEÍDO/CONTRASTADO** | NADR-F17BIS-06: presupuesto exacto fuera de 0.3 (PPPR.0.4) |
| Estado/FS/host/GT/G5 | Consumidores downstream y baseline | **REFERENCIADO** | PPPR.0.5–0.8; no accesos a bases, corpus o APIs externas |

**Pendiente de §8.1:** verificar el cierre final del perímetro de responsabilidades, documentación de decisiones pendientes y checklist en una pasada independiente. No confundir cobertura de código seleccionada con certificación del 100% del documento científico.

## 4. FUENTES DE EVIDENCIA Y PRECEDENCIA

**Código primario** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42` (ruta elegida): `apps/ocr_router/__main__.py`, `core/ast/{builder,hashing,models,cross_page,strategy}.py`, `core/chunking/{contextual_plan,semantic_chunking,manifest_contract}.py`, `core/normalization/enrichers/context_enricher.py`, `core/context/plan_context_contract.py`, `apps/bootstrap/pipeline_factory.py`.

**Código secundario** del mismo SHA: `core/layout/models.py`, `core/normalization/{bootstrap,pipeline,classifier,normalizer,explicit_math}.py`, `core/ast/{grouper,segmenter}.py`, `core/chunking/chunker.py`, `core/pipeline/orchestrator.py`. La existencia de esas clases no acredita selección por OCR.

**Norma FROZEN:**
- `NADR-F17BIS-03_Semantic_Hashing_Chunking_Segregation.md` **§5.1 R1–R5**, §5.3 R8–R9 y §5.4 R10–R13. R1 exige tipo, contenido normalizado, orden relativo y **posición jerárquica** en la identidad semántica de AST.
- `NADR-F17BIS-16_Cryptographic_Identity_Semantics_&_Chaining.md` **§5.2 R4–R8**: permite contratos alternativos de hash con propósito/dimensiones explícitos; el oráculo de baseline requiere identidad de nodo.
- `NADR_01_Canonical_AST_Representation.md` §5 gobierna serialización/hidratación del AST, **no** obliga al hash operativo a incorporar `node_id`.
- `NADR_05_Real_Context_Resolution.md` §5 pide contexto real, materialización con identidad contextual y fail-fast; el consumidor SQLite/LLM se profundizará en 0.4/0.5.
- Metodologías general v1.3.0 y forense v1.2.0 FROZEN; `PROJECT_SCOPE.md` §2/§4 y `ENGINEERING_PRINCIPLES.md` §§II/III/IV.

**Antecedentes:** PPPR.0.1 y PPPR.0.2 FROZEN, más `HITO_0.4.5_P3_TRANSFORMATION_SEGMENTATION_CHUNKING_AUDIT.md` de F17-BIS como corte histórico que **debe reconciliarse con HEAD**, no heredarse como estado productivo.

**Testigos solo leídos (NOT_RUN):** `tests/integration/{test_g3_chunk_identity_contract,test_chunker_snapshot,test_w08_ocr_g3_context_wiring,test_w08_durable_context_boundary}.py`, `tests/unit/{test_semantic_chunker,test_context_enricher,test_w08_inference_identity_contract,test_math_normalizer}.py`. Algunos emplean estimador por palabras, proveedores fake y SQLite temporal; no se infiere CI PASS, física TeX, oráculos científicos ni testigo específico de sensibilidad de hash a H1/H2.

## 5. MAPA DE FLUJOS OBSERVADOS (RUTA ACTUAL Y FRONTERAS)

```text
PPPR.0.2: PyMuPDF → Layout → FlatASTBuilder
             → CrossPageNormalizer → topología, estrategia y ASTNode[]
OCRRouterDaemon._process_document (seleccionado por D-1/D-2)
  → parser.parse(pdf) → raw_ast
  → profile (PPPR.0.2)
  → compute_ast_hash(raw_ast)                  [type + text_content + orden]
  → prepare_contextual_plan(raw_ast)
      → HierarchicalContextEnricher             [context_id, breadcrumbs, sin cambiar texto]
      → check compute_ast_hash(enriched) == hash(raw_ast)
      → HEADING aislado con PRESERVE_HEADING_NO_INFERENCE
      → grupos por context_id (no GLOBAL_ROOT para inferencia)
      → TokenBudgetChunker.chunk_group
          → unidades TRANSLATE / PRESERVE / PARTIAL; overflow BY_SENTENCE
      → ChunkPlan.build → validate_chunk_coverage
  → registrar AST/plan/context snapshots/estados  [PPPR.0.5]
  → G3 real/LLM, render G5                      [PPPR.0.4–0.6]

Ruta distinta: build_pipeline() → TranslationPipeline.execute()
  → SemanticNodeClassifier/StructuralAssetPlaceholder
  → HierarchicalContextEnricher → chunker inyectado
  [EXISTE; no reemplaza el root OCR seleccionado]
```

**Reconciliación histórica:** F17-BIS P3 describía `TokenBudgetChunker` alojado dentro de `core/ast/hashing.py`; en este SHA, `hashing.py` contiene solo firma, y la capacidad está en `core/chunking/semantic_chunking.py`. En consecuencia, no se reabre `P3-H02` como defecto actual. El bypass de `NormalizationPipeline` sigue observable **en el camino OCR inspeccionado**, pero no prueba por sí solo violación de una política canónica obligatoria, y la ruta `TranslationPipeline` es distinta. Los hallazgos del benchmark histórico van a PPPR.0.8.

## 10. REGISTRO DE EVIDENCIA FORENSE — SEGUNDA PASADA

| E-ID | Sev. | Observed (código del SHA fijado) | Required / Decision / límite | Estado |
|---|---|---|---|---|
| **E-0.3-001** | P2 | `OCRRouterDaemon._process_document` calcula `compute_ast_hash(raw_ast)`, llama `prepare_contextual_plan` y coteja `plan.ast_hash`. | Ruta conectada; control de SQLite/FS/egress se delega a PPPR.0.5. | CONFIRMADO |
| **E-0.3-002** | P2 | `compute_ast_hash` serializa secuencia `[{type,content}]`; excluye IDs, metadata y sequence_id explícito. | NADR-F17BIS-16 §5.2 admite hash alternativo a baseline. Excluir `node_id` no es GAP; ver E-010 sobre jerarquía. | CONFIRMADO |
| **E-0.3-003** | P2 | `prepare_contextual_plan` guarda hash original, enriquece `control_plane` y verifica igualdad de hash semántico post-enriquecimiento. | Es guard de texto/tipo/orden, no de campos ausentes del pre-image; no afirmar deriva física comprobada. | CONFIRMADO |
| **E-0.3-004** | P2 | Agrupa por `context_id` obtenido del enriquecedor y aísla `HEADING` con contexto de no-inferencia. | Contexto real seleccionado (NADR-F17BIS-05); exactitud de breadcrumb frente a PDF fuente NO VERIFICABLE aquí. | CONFIRMADO |
| **E-0.3-005** | P2 | `TokenBudgetChunker.chunk_group` aísla tipos protegidos y fracciona texto mediante `_split_by_sentence` si supera presupuesto; oración indivisible excesiva falla `G3_SENTENCE_EXCEEDS_BUDGET`. | Política explícita, no algoritmo STEM científicamente validado. | CONFIRMADO |
| **E-0.3-006** | P2 | `ChunkPlan.build` invoca `validate_chunk_coverage`: exige cobertura de miembros/segmentos, orden, fuente exacta, estrategia y hashes de payload. | Garantía sobre el AST recibido, **no** sobre contenido PDF que jamás ingresó. | CONFIRMADO |
| **E-0.3-007** | P2 | `CrossPageNormalizer` fusiona párrafos/tipos permitidos entre páginas consecutivas con heurística lexical y conserva `pages` y `bboxes` combinados. | No hay prueba de unión científica incorrecta; validación física pendiente en 0.8. | RIESGO ACOTADO |
| **E-0.3-008** | P2 | `NormalizationPipeline` y `TextNormalizer` (NFKC) existen, pero la cadena OCR→`prepare_contextual_plan` examinada no los invoca. | Distinguir capacidad disponible de etapa ejecutada; no inferir fallo de normalización universal sin contrato de activación. | RECONCILIADO |
| **E-0.3-009** | P2 | `apps/bootstrap/pipeline_factory.py::build_pipeline` inicializa registro DNL y `TranslationPipeline.execute` clasifica/corrige nodos, pero OCR seleccionado usa `prepare_contextual_plan` directo, sin ese flujo procedimental. | Dos rutas distintas; diagnósticos F17-BIS P3 no migran automáticamente a PPPR. | RECONCILIACIÓN HISTÓRICA |
| **E-0.3-010** | **P1** | `core/ast/hashing.py::compute_ast_hash` no serializa `HeadingPayload.heading_level` ni `ASTNode.depth`; el enriquecedor **sí** usa `heading_level` para construir el contexto. | NADR-F17BIS-03 §5.1 **R1** exige posición jerárquica en la firma semántica; el mismo hash puede representar jerarquías distintas con idéntico texto/tipos/orden. | **GAP-0.3-01 OPEN** |
| **E-0.3-011** | P2 | `LayoutBlockDraft` no define `level`; `FlatASTBuilder._map_native_level(getattr(block,"level",0))` recibe 0 para el DTO conectado, y `HierarchicalContextEnricher` interpreta `UNKNOWN` como H1. `HeuristicLayoutClassifier` tampoco distingue subsección en la ruta inspeccionada. | No acredita jerarquía física de subsecciones; riesgo de aplanamiento, pero no se declara tasa de error en papers reales. | LIMITACIÓN DE RECONSTRUCCIÓN |
| **E-0.3-012** | P2 | `ChunkPlan.digest` incluye unidades serializadas con `context_id`; `derive_verified_plan_contexts` recompone jerarquía y comprueba los IDs de contexto en unidades de inferencia. | Atenúa la propagación de un cambio de contexto; **no corrige** la omisión jerárquica del `ast_hash` ni acredita una colisión materializada. | GUARDIA CONECTADA |
| **E-0.3-013** | P2 | `resolve_strategy(HEADING)=TRANSLATE`, pero `prepare_contextual_plan` aísla encabezados y el chunker les asigna `PRESERVE`, aceptado por `expected_task_type`. | Política W08 explícita (no-inferencia) vs intención de traducción declarada por strategy; alcance de producto/idioma de títulos se remite a decisión, no a un GAP precipitado. | DECISION CANDIDATE |
| **E-0.3-014** | P2 | Testigos W08 crean `HeadingPayload(H1)` manualmente, usan SQLite descartable, fake provider/estimator; G3 tests validan fragmentos y `ChunkPlan` con estimador `len(split())`. | Tests existentes de mecanismos, **no** prueba de jerarquía desde PDF, proveedor/GT real ni sensibilidad H1↔H2 del hash. | ALCANCE DE TEST |
| **E-0.3-015** | P2 | `_split_by_sentence` no elimina espacios de cada segmento; `validate_chunk_coverage` reconstruye texto original por concatenación y rechaza pérdidas/duplicaciones. | Invariante reconstruible; calidad de límites oracionales, abreviaturas y términos técnicos NO VERIFICABLE aquí. | OBSERVADO |
| **E-0.3-016** | P2 | `core/ast/hashing.py` ya no contiene chunking; `TokenBudgetChunker` reside en `core/chunking/semantic_chunking.py`. `PolicyDrivenStreamingChunker`/`MarkdownSegmenter` son capacidades alternativas, no seleccionadas por el root OCR inspeccionado. | Reconciliar `P3-H02` de F17-BIS (otro SHA), sin inferir ausencia de consumidores ajenos. | HISTÓRICO RECONCILIADO |
| **E-0.3-017** | P2 | `core/context/plan_context_contract.py::derive_verified_plan_contexts` rechaza contexto de inferencia no verificable y `ChunkPlan` valida `PASSTHROUGH/KEEP_ORIGINAL` como PRESERVE. | Garantías del plano lógico; ejecución del proveedor y durabilidad física son 0.4/0.5. | OBSERVADO |

| **E-0.3-018** | P2 | `core/ast/strategy.py::resolve_strategy` define `HEADING→TRANSLATE`, pero `TokenBudgetChunker` lo aísla por `boundaries` y le asigna `PRESERVE`. `manifest_contract.py::_PROTECTED_TYPES` incluye `HEADING`; W08 test construye 2 headings + 2 párrafos y solo 2 unidades de inferencia. | **CONFIRMADA** la no-inferencia de encabezados en la ruta OCR, no su aceptabilidad para títulos científicos. `DC-0.3-01` requiere decisión de alcance de producto, no cambio anticipado. | COMPORTAMIENTO CONFIRMADO |
| **E-0.3-019** | P2 | `LayoutBlockType` permite `SUBSECTION` y `HeadingPayload` H1/H2/H3, pero `HeuristicLayoutClassifier.classify` solo emite `SECTION` para headings; `_layout_block_to_draft` y `LayoutBlockDraft` no tienen `level`. `FlatASTBuilder` produce `UNKNOWN`; `HierarchicalContextEnricher` lo interpreta como H1. | **CONFIRMADA** pérdida de diferenciación H1/H2/H3 por el camino físico seleccionado; no hay medición de jerarquía correcta en papers. `DC-0.3-02` para requisitos de jerarquía; testigo físico y GT en 0.8. | LIMITACIÓN ESTRUCTURAL CONFIRMADA |
| **E-0.3-020** | **P1** | `PyMuPDFProvider._extract_raw_content` establece `normalized=raw_text.strip()`; `_layout_block_to_draft` pasa ese campo; `compute_ast_hash` serializa `node.text_content` sin normalización Unicode. `NormalizationPipeline`/ `TextNormalizer.normalize` no se ejecutan en el root OCR. | **NADR-F17BIS-03 §5.1 R4** exige normalización canónica antes del pre-image. Secuencias Unicode canónicamente equivalentes pueden producir pre-images distintos. No se prescribe NFKC por sus riesgos STEM. | **GAP-0.3-02 OPEN** |

### Ficha extendida E-0.3-010 — sensibilidad jerárquica del hash

- **Archivo/símbolo primario:** `core/ast/hashing.py::compute_ast_hash`; `core/ast/models.py::{HeadingPayload,ASTNode}`.
- **Consumidores corroborantes:** `apps/ocr_router/__main__.py::_process_document` → `core/chunking/contextual_plan.py::prepare_contextual_plan` → `HierarchicalContextEnricher.enrich_document` → `ChunkPlan.build`.
- **Fragmentos de código observados** (`main@1d21cfe`):

```python
# core/ast/hashing.py
return {"type": n.node_type.value, "content": n.text_content}

# core/ast/models.py
heading_level: HeadingLevel = HeadingLevel.UNKNOWN
depth: int = 0

# core/normalization/enrichers/context_enricher.py
if h_level_attr == HeadingLevel.H1: level = 1
elif h_level_attr == HeadingLevel.H2: level = 2
elif h_level_attr == HeadingLevel.H3: level = 3
```

- **Observed:** dos secuencias de AST tipados pueden mantener exactamente los mismos `node_type`, `text_content` y orden mientras cambian `heading_level` de H1 a H2; el pre-image JSON será idéntico por definición. En el mismo caso, el enriquecedor construye `fingerprint_elements` distintos (`H1_I...:` vs `H2_I...:`) y por tanto identifica contextos distintos. Esto es **equivalencia por proyección omitida**, NO una colisión criptográfica SHA-256.
- **Required:** NADR-F17BIS-03 **§5.1 R1** exige incluir posición jerárquica en la firma semántica del AST; §5.3 R8 exige coherencia entre firma usada para procesar y estado del contenido. `ENGINEERING_PRINCIPLES.md` §IV exige linaje trazable. NADR-F17BIS-16 **§5.2** autoriza una firma alternativa sin `node_id`, **no** suprime el requisito de jerarquía del contrato de firma operativa.
- **Decision:** la ruta D-1/D-2 consume `compute_ast_hash` como `ast_hash` de generación del plan y estado, no solo como métrica de comparación de parsers. Las identidades de GT/baseline son otro contrato.
- **Consecuencia arquitectónica demostrada:** el `ast_hash` no distingue dos AST semánticamente jerárquicos distintos bajo ese cambio aislado, aunque el `context_id` del plan sí cambia. **No** se demuestra reutilización incorrecta real, colisión de `ChunkPlan.digest`, fallo transaccional ni impacto en un PDF G5. Son fronteras independientes, con guards adicionales (E-0.3-012/017).
- **Severidad / alcance:** **P1 / LOCAL** por contradicción estructural con contrato normativo explícito de hash semántico; no P0 por falta de evidencia de corrupción de publicación.
- **Estado:** **OPEN → GAP-0.3-01**. Fase destino: evaluación en ADR Maestro PPPR posterior a Fase 0, reglas existentes y Execution Plan aprobado; testigo puro de sensibilidad H1/H2 si resulta necesario, sin corpus privado ni implementación previa.


### Ficha extendida E-0.3-020 — normalización canónica antes del hash

- **Código fuente y símbolos:** `infra/extraction/providers/pymupdf_provider.py::_extract_raw_content`, `apps/bootstrap/pipeline_factory.py::_layout_block_to_draft`, `core/ast/hashing.py::compute_ast_hash`, `core/normalization/normalizer.py::TextNormalizer.normalize` y `core/chunking/contextual_plan.py::prepare_contextual_plan`.
- **Fragmentos literales mínimos del baseline `main@1d21cfe`:**

```python
# pymupdf_provider.py
normalized_text = raw_text.strip()

# pipeline_factory.py
content=block.content.normalized,

# hashing.py
return {"type": type_str, "content": n.text_content}

# normalizer.py (capacidad existente, NO invocada por OCR)
return unicodedata.normalize("NFKC", text)
```

- **Observed:** el valor llamado `normalized` por la ruta PyMuPDF elimina espacios extremos, pero no aplica una transformación Unicode canónica; `RawContent`, `LayoutBlockDraft` y `ASTNode` no añaden una etapa equivalente. `compute_ast_hash` se limita a proyectar el string entregado. La ruta OCR llama directamente a `prepare_contextual_plan` y esta llama al hash sin utilizar `NormalizationPipeline` ni `TextNormalizer`.
- **Required:** NADR-F17BIS-03 **§5.1 R4**: el contenido **MUST** someterse a normalización canónica antes de formar parte del pre-image de firma; §5.2 R6 exige reproducibilidad del contenido semántico. Su norma no fija aquí qué transformación Unicode es segura para todos los símbolos STEM.
- **Decision:** NADR-F17BIS-16 §5.2 permite hashes alternativos por propósito, pero no elimina las obligaciones de NADR-03 sobre el contrato de firma. D-1/D-2 fijaron la ruta, no una dispensa de normalización. La presencia de `NFKC` disponible **no autoriza** ejecutarlo ciegamente sobre fórmulas científicas.
- **Mecanismo causal y consecuencia demostrable:** dos cadenas Unicode canónicamente equivalentes —por ejemplo, `U+00E9` y `U+0065 U+0301` para «é»— no son iguales como secuencias de codepoints; sin canonización, sus `content` serializados difieren, de modo que el hash no es invariante frente a esa equivalencia. Es una propiedad del código, **no** un test PyMuPDF ejecutado ni una colisión SHA-256 observada. No se conoce aquí cuántos PDFs científicos usan esas formas.
- **Severidad:** **P1 / LOCAL**, por incumplimiento del pre-image requerido en la frontera AST→identidad semántica; no P0 ni defecto medido en la salida PDF.
- **Estado / destino:** **OPEN → GAP-0.3-02**. ADR Maestro PPPR y normativa vigente determinarán la convención canónica compatible con STEM; posterior Execution Plan aprobado para cualquier cambio. Ninguna propuesta de normalizador/algoritmo queda aprobada en este HITO.

## 14. GAPS CONSOLIDADOS (PROVISIONALES)

| GAP | Observed vs Required | Evidencia | Contrato y alcance | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-0.3-01** | `compute_ast_hash` omite jerarquía `heading_level/depth`, mientras `context_id` se deriva de esos niveles | **E-0.3-010**, E-002/004/012 | NADR-F17BIS-03 §5.1 R1; **P1 LOCAL**. NADR-F17BIS-16 permite excluir `node_id` pero no acredita equivalencia de jerarquías | PPPR pos-Fase 0: ADR Maestro/NADR existentes, Execution Plan aprobado; falsador focal sin corpus si se exige | **OPEN** |
| **GAP-0.3-02** | Solo `strip()` antes de formar el pre-image de texto Unicode, sin normalización canónica | **E-0.3-020**, E-008/009 | NADR-F17BIS-03 §5.1 R4, §5.2 R6; **P1 LOCAL**. No se escoge NFKC por decreto | PPPR pos-Fase 0: decidir semántica canónica compatible con STEM y trazabilidad; Execution Plan aprobado antes de cambiar código | **OPEN** |

**No son automáticamente GAPs:** encabezados enviados como PRESERVE, el nivel H1 por fallback, algoritmos auxiliares sin consumo en el root seleccionado, ni expresiones STEM cuya reconstrucción no se midió. Estas limitaciones están registradas para especificación de alcance/aceptación, sin abrir componentes ni autorizar refactors.

## 15. ESTADO DE HIPÓTESIS Y DISPOSICIONES (§8.2)

| ID estable | Veredicto de esta pasada | Evidencia, alcance y destino |
|---|---|---|
| **H-0.3-A** | **CONFIRMADA** | DNL `NormalizationPipeline` no está conectada en OCR; solo enriquecimiento de contexto, sin inferir desconexión global. E-008/009/020, GAP-0.3-02 por normalización canónica de firma |
| **H-0.3-B** | **CONFIRMADA con distinción normativa** | Metadata física está excluida **por diseño**; la omisión jerárquica contraviene NADR-03 R1. E-002/010, GAP-0.3-01; consumidores de estado: 0.5 |
| **H-0.3-C** | **NO VERIFICABLE** | Regla trans-página está conectada, pero errores sobre un paper requieren fuente/oráculo. **DQ-0.3-01 → PPPR.0.8**, no bloquea trazar mecanismo |
| **H-0.3-D** | **NO VERIFICABLE** | Cobertura textual del manifest observada; límites lingüísticos en textos STEM sin oráculo. **DQ-0.3-02 → PPPR.0.8**; estimador real 0.4 |
| **H-0.3-E** | **CONFIRMADA SOLO COMO CONTRATO** | PRESERVE/PARTIAL y pertenencia están validados en `ChunkPlan`; ejecución G3/G5 no certificada. **DQ-0.3-03 → PPPR.0.4/0.6** |
| **H-0.3-F** | **CONFIRMADA** | `HEADING` tiene strategy TRANSLATE pero produce unidad PRESERVE en OCR (E-013/018); no se envía por la ruta ordinaria de inferencia. Aceptabilidad del idioma de headings pendiente como **DC-0.3-01** para ADR Maestro |
| **H-0.3-G** | **CONFIRMADA** | Mapper no transmite nivel y contexto interpreta UNKNOWN como H1 (E-011/019). Impacto en estructura real **NO VERIFICABLE** → **DQ-0.3-04** PPPR.0.8; requerimiento de jerarquía en **DC-0.3-02** para ADR Maestro |
| **H-0.3-H** | **CONFIRMADA** | No existe canonización de contenido Unicode previa al pre-image en la ruta OCR inspeccionada, E-020 → GAP-0.3-02. La convención segura de equivalencia STEM corresponde al ADR/Execution Plan |

### 15.1 Deferred Questions sin afirmación de PASS

| DQ | Razón de no-verificación y no-bloqueo | Gate posterior |
|---|---|---|
| **DQ-0.3-01** | Error de sutura entre páginas requiere fuente conocida; regla y condiciones están identificadas | 0.8 |
| **DQ-0.3-02** | Calidad de cortes oracionales para abreviaturas y notación técnica requiere testigos científicos autorizados; reconstrucción literal del AST está contractualmente revisada | 0.8 |
| **DQ-0.3-03** | Fidelidad de unidades preservadas en proveedor/ensamblado exige recorrer consumidores físicos fuera del HITO | 0.4/0.6 |
| **DQ-0.3-04** | Frecuencia y efecto visual de pérdida H2/H3 necesitan PDF con jerarquía/GT independiente; el error de proyección local ya está identificado | 0.8 |

Los veredictos confirman o acotan **comportamientos**, no resuelven cuestiones de política científica por decreto. `DC-0.3-01/02` conservan sus decisiones abiertas a gobernanza, sin dejar hipótesis `TO BE VERIFIED` indeterminadas en el registro.

## 16. RESPUESTAS ACTUALIZADAS AL MANDATO

**Estado observado:** AST plano → enriquecedor de contexto → unidades semánticas → `ChunkPlan`, con estrategia y fuente textual verificadas. El hash alternativo se consume como identidad operativa y omite tanto jerarquía como canonización exigida por NADR-03, generando GAP-0.3-01/02. La ruta OCR preserva headings aun cuando `resolve_strategy` los declara TRANSLATE y aplana niveles al pasar por `LayoutBlockDraft`. El documento inventaría esas propiedades sin decidir aceptación de producto ni afirmar resultado PDF, proveedor, GT o CI. La semántica efectiva de títulos/subsecciones y normalización científica será materia de gobernanza posterior, no de implementación inmediata.

## 17. CONTRASTE NORMATIVO FOCAL (SIN CERTIFICAR PRODUCTO)

| Regla vigente | Required | Observed | Resultado | E-ID |
|---|---|---|---|---|
| **NADR-03 §5.1 R1** | Tipo, contenido normalizado, orden y jerarquía en pre-image | Tipo/contenido/orden, **sin jerarquía** | **FAIL LOCAL** | E-010 |
| **NADR-03 §5.1 R2/R3** | Excluir runtime e incluir orden relativo | Sin IDs/metadata y sensible a orden de array | **PASS estático acotado** | E-002 |
| **NADR-03 §5.1 R4** | Normalización canónica previa al pre-image | `strip()`, sin canonización de Unicode ejecutada | **FAIL LOCAL** | E-020 |
| **NADR-03 §5.4 R10–R12** | Firma y chunking separados | `hashing.py` sin chunker y `semantic_chunking.py` con chunker | **PASS estático acotado** | E-016 |
| **NADR-16 §5.2 R4–R8** | Contratos alternativos con propósito propio, canon baseline separado | Hash alternativo documentado para comparación, pero consumido también como `ast_hash` operativo de OCR | **PARTIAL — uso adicional a gobernar** | E-001/002/010 |
| **NADR-05 §5.1 R1–R3** | Contexto real y fallo explícito | Enriquecedor y checks de contexto conectados antes de G3 | **PASS estático en productor** | E-004/012/017 |
| **NADR-05 §5.2 R4–R6** | Claves de materialización vinculadas al contexto | Plan incluye `context_id`; efectos de persistencia/consumo no auditados aquí | **TO BE VERIFIED en PPPR.0.5** | E-012/017 |

Un `PASS estático` expresa únicamente el subconjunto de regla demostrado por código, no una certificación end-to-end. Los dos `FAIL LOCAL` son los GAPs existentes, no defectos duplicados.

## 18. MATRIZ DE TRAZABILIDAD DE DECISION CANDIDATES

| DC | Cuestión que requiere autoridad | Evidencia | Estado actual | Destino |
|---|---|---|---|---|
| **DC-0.3-01** | ¿Debe traducirse el contenido de títulos/encabezados o puede preservarse como política explícita? | E-013/018 | **POLÍTICA POR DECIDIR**; no-inferencia confirmada | ADR Maestro PPPR; impacto final PPPR.0.6/0.8 |
| **DC-0.3-02** | ¿Qué fidelidad jerárquica y criterio de aceptación se exige para H1/H2/H3 extraídos de PDF? | E-011/019 | **ALCANCE POR DECIDIR**; aplanamiento observado | ADR Maestro PPPR; evidencia 0.8 |
| **DC-0.3-03** | ¿Qué semántica de normalización canónica de firma evita cambios científicos indebidos? | E-020/GAP-0.3-02 | **CONTRATO INCOMPLETO/INCUMPLIDO**; no se prescribe NFKC | ADR Maestro y normas vigentes; Execution Plan posterior |

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.2.** Se resolvieron los estados de H-0.3-F/G por evidencia de código y se abrió GAP-0.3-02 sobre normalización canónica, respaldado por E-0.3-020 y NADR-03 R4. Quedan **20 E-IDs**, dos GAPs P1 locales OPEN, cuatro DQ y tres DC sin decisiones aprobadas. Pendiente: última reconciliación de cobertura y revisión formal §8.1–8.2. Sin tests ejecutados ni implementación.

**Siguiente gate:** ampliar el mismo HITO dentro del PR interno a `pdf-pdf-product-readiness`, evitando merges a `main`. El PR #66 debe permanecer Draft hasta completar la gobernanza y el Execution Plan.
