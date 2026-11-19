# HITO_PPPR.0.3_AST_NORMALIZACION_Y_CHUNKING.md

**Estado:** IN_PROGRESS v1.0.1  
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

## 1. RESUMEN EJECUTIVO

La composición seleccionada en `OCRRouterDaemon._process_document` calcula `compute_ast_hash(raw_ast)`, prepara el plan contextual mediante `prepare_contextual_plan`, valida la igualdad del hash semántico después del enriquecimiento, materializa `ChunkPlan` y luego pasa a persistencia/estado de otra frontera. Esto no presupone que todos los normalizadores del repositorio se ejecuten en esa ruta.

**Hallazgo central:**

> El AST semántico y su plan de trabajo disponen de contratos explícitos de hash, pertenencia, orden y preservación, pero sus garantías son distintas del linaje físico y de la fidelidad científica.

**Revisión v1.0.1:** la omisión de jerarquía en el pre-image de `compute_ast_hash` contradice la regla explícita NADR-F17BIS-03 §5.1 R1 cuando el hash se usa como identidad de generación de un AST con encabezados jerárquicos. Se registra **un GAP P1 local** (E-0.3-010), limitado a esa proyección; no se infieren colisiones SHA-256, reutilización incorrecta efectiva de SQLite ni corrupción del PDF final. La pérdida de niveles de título y la política de preservarlos se mantienen como observaciones separadas, con disposición todavía pendiente.

**Veredicto de esta pasada:** composición OCR y contratos de integridad identificados; reconciliación con NADR e históricos iniciada. Subsisten consumidores y garantías por comprobar antes de FROZEN. **IN_PROGRESS**, sin implementación autorizada.

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

**Pendiente de §8.1:** verificar en una tercera pasada el cierre de toda frontera del mandato y el alcance de hipótesis; la matriz no se presenta todavía como certificación del 100% de contenido científico.

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

## 14. GAPS CONSOLIDADOS (PROVISIONALES)

| GAP | Observed vs Required | Evidencia | Contrato afectado / scope | Fase destino / estado |
|---|---|---|---|---|
| **GAP-0.3-01** | El pre-image de la firma operativa AST omite `heading_level/depth`, aunque cambia la identidad contextual derivada de la jerarquía | **E-0.3-010**, E-0.3-002/004/012 | NADR-F17BIS-03 §5.1 R1, identidad semántica jerárquica; **P1 LOCAL**. NADR-F17BIS-16 permite exclusión de `node_id` pero no prueba una equivalencia jerárquica | **OPEN** → gobernanza PPPR pos-Fase 0, revisar ADR Maestro y NADR aplicables; asignación de implementación únicamente en Execution Plan aprobado |

No se convierte automáticamente en GAP: la presencia de `NormalizationPipeline` no conectado al root OCR, la heurística de sutura, la ausencia de segmentador Markdown separado, la preservación de headings ni la existencia de dos hashes con distintos usos. Para estos asuntos faltan contrato de producto, prueba científica o decisión de alcance; no se inventa una solución.

## 15. HIPÓTESIS Y DECISION CANDIDATES (IN_PROGRESS)

| ID estable | Estado actual | Razón y siguiente gate |
|---|---|---|
| **H-0.3-A** | **CONFIRMADA ACOTADA** | Root OCR llama al enriquecedor directamente, no al `NormalizationPipeline` de DNL (E-008/009); no se afirma desconexión de todos los roots. Decidir si normalización adicional es requerida por producto/contrato |
| **H-0.3-B** | **CONFIRMADA PARCIALMENTE** | Firma excluye metadata física **por decisión** NADR-F17BIS-16; no es GAP por sí misma. Sensibilidad jerárquica sí falla (E-010/GAP-0.3-01). Efectos en otras dimensiones de generación: PPPR.0.5 |
| **H-0.3-C** | **NO VERIFICABLE** | Heurística de fusión trans-página conectada (E-007), pero error científico necesita papel/oráculo: DQ-0.3-01 → PPPR.0.8 |
| **H-0.3-D** | **NO VERIFICABLE** | Testigos certifican por intención bytes reconstruibles y fail-closed de oración larga; corrección lingüística requiere casos STEM físicos: DQ-0.3-02 → PPPR.0.8. Tokenizer efectivo: PPPR.0.4 |
| **H-0.3-E** | **CONFIRMADA SOLO EN CONTRATO** | Manifest exige correspondencia de PRESERVE/PARTIAL y contexto (E-006/017). G3/G5 reales NO VERIFICABLE: DQ-0.3-03 → PPPR.0.4/0.6 |
| **H-0.3-F** | **TO BE VERIFIED** | `HEADING` tiene strategy TRANSLATE, pero el root seleccionado lo envía por `PRESERVE` (E-013). Necesita criterio de producto sobre idioma de títulos; DC-0.3-01 → ADR Maestro PPPR, sin prescripción previa |
| **H-0.3-G** | **TO BE VERIFIED** | `LayoutBlockDraft` no transmite niveles y el enriquecedor interpreta UNKNOWN como H1 (E-011). Verificar suficiencia contra contrato estructural; alcance científico → PPPR.0.8, decisión PPPR posterior |

**Regla §8.1–8.2:** mientras H-0.3-F/G sigan `TO BE VERIFIED`, el HITO **no puede congelarse**. Las demás preguntas no verificables tienen razones y destinos; se revisará su no-bloqueo en la pasada de cierre.

## 16. RESPUESTAS INICIALES AL MANDATO

La ruta seleccionada está conectada desde AST hasta `ChunkPlan`, con contexto real y validación de cobertura del texto disponible. La composición OCR no activa la fachada DNL, no utiliza los segmentadores alternativos y deliberadamente PRESERVE encabezados; no se concluye todavía si esas diferencias vulneran un requisito de producto. La firma semántica operativa no es la canónica de oráculo y omite jerarquía, dando lugar al GAP-0.3-01. La calidad STEM y el impacto físico siguen fuera de prueba; no se afirma producto `PASS`.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.1.** Se contrastaron normas, consumidores OCR, preservación de texto y testigos; se abrió un GAP P1 local (E-0.3-010) con ficha extendida. Pendientes: resolver las dos cuestiones H-0.3-F/G, verificar si hay contradicciones o consumidores adicionales relevantes y completar checklist §8.1–8.2. No se ejecutó ningún test ni se modificó producción.

**Siguiente gate:** ampliar el mismo HITO dentro del PR interno a `pdf-pdf-product-readiness`, evitando merges a `main`. El PR #66 debe permanecer Draft hasta completar la gobernanza y el Execution Plan.
