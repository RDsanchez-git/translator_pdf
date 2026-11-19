# HITO_PPPR.0.3_AST_NORMALIZACION_Y_CHUNKING.md

**Estado:** IN_PROGRESS v1.0.0  
**Fecha de emisión:** 2026-11-19  
**Fecha de congelamiento:** N/A  
**Iniciativa:** PPPR, Fase 0 transversal — `pdf-pdf-product-readiness`  
**Tipo de artefacto:** Forensic Flow Audit (AST, normalización y construcción de plan)  
**Naturaleza:** Auditoría read-only; no prescribe arquitectura ni implementación.  
**Baseline productivo observado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@084158a9ad1f06b4d58dc38852157c2b3f01d201` (incluye PPPR.0.1/0.2 FROZEN).  
**Fuentes vinculantes:** metodología general v1.3.0 FROZEN; metodología forense v1.2.0 FROZEN; `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y Atlas de ruta; PPPR.0.1 FROZEN v1.0.9 y PPPR.0.2 FROZEN v1.0.3; NADR-03 y NADR-F17BIS-16 citados por el código, con sus requisitos específicos **pendientes de comprobación directa en este HITO**.  
**Mandato:** Auditar la ruta conectada desde AST de extracción hasta enriquecimiento, normalización, segmentación, chunking semántico y `ChunkPlan`, distinguiendo identidad semántica, cobertura de miembros, preservación STEM y límites de prueba; no auditar efectos físicos de G3/G5 ni decisiones de proveedor.

### Changelog

| Versión | Fecha | Modificación |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura posterior al merge interno #67, con primera lectura directa de composición OCR, AST/hash, contexto, chunker y manifest; frontera provisional y cuestiones falsables. No tests ejecutados ni FROZEN. |

## 1. RESUMEN EJECUTIVO

La composición seleccionada en `OCRRouterDaemon._process_document` calcula `compute_ast_hash(raw_ast)`, prepara el plan contextual mediante `prepare_contextual_plan`, valida la igualdad del hash semántico después del enriquecimiento, materializa `ChunkPlan` y luego pasa a persistencia/estado de otra frontera. Esto no presupone que todos los normalizadores del repositorio se ejecuten en esa ruta.

**Hallazgo central:**

> El AST semántico y su plan de trabajo disponen de contratos explícitos de hash, pertenencia, orden y preservación, pero sus garantías son distintas del linaje físico y de la fidelidad científica.

No se declaran P0/P1 en la apertura. Los riesgos de sutura trans-página, segmentación larga y sensibilidad de hash a cambios físicos deben contrastarse con contratos normativos, consumidores y testigos **antes** de asignar severidad o abrir gaps.

**Veredicto inicial:** flujo principal parcialmente inspeccionado; cobertura total y clasificación de discrepancias pendientes. **IN_PROGRESS**, sin aprobación de diseño.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **OBSERVADO:** lectura directa del código del SHA indicado, sin ejecutar los componentes; los tests existentes pueden aportar alcance de sus aserciones, no resultados nuevos.
- **REQUIRED:** trazabilidad y explicitud del scope/principios, contratos implementados de hash semántico, segmentación y manifest. Verificar literalmente NADRs aplicables antes de atribuirles obligaciones.
- **DECISION:** D-1/D-2 fijaron la ruta productiva; PPPR.0.2 congeló la frontera de extracción sin certificar orden científico. Mantener distintos el hash semántico de parser y la identidad canónica de oráculo.
- **NO VERIFICABLE EN ESTA APERTURA:** tasa de error sobre papers reales, linaje de GT, validez de una sutura concreta, calidad de traducción, persistencia y generación física.
- **NO EJECUTADO:** pytest, PyMuPDF, OCR, servicios comerciales, compilador, GT/corpus o SQLite.

## 3. ALCANCE AUDITADO — ESTADO DE PRIMERA PASADA

| Superficie | Archivos / símbolos | Estado |
|---|---|---|
| Composición seleccionada | `apps/ocr_router/__main__.py::_process_document`; `core/chunking/contextual_plan.py::prepare_contextual_plan` | **AUDITADO focalmente** |
| Identidad del AST | `core/ast/hashing.py::compute_ast_hash` | **AUDITADO focalmente** |
| Construcción y cobertura del plan | `core/chunking/{semantic_chunking,manifest_contract}.py::TokenBudgetChunker/ChunkPlan/validate_chunk_coverage` | **AUDITADO focalmente** |
| Sutura física previa al hash | `core/ast/{builder,cross_page}.py::FlatASTBuilder/CrossPageNormalizer` | **AUDITADO focalmente**; reutilizar PPPR.0.2 |
| Normalización disponible | `core/normalization/{pipeline,normalizer,explicit_math}.py` | **LECTURA INICIAL**; conexión a la ruta aún por reconciliar |
| Arquitectura y superficies alternativas | `core/ast/{segmenter,grouper,validator,models}.py`; `core/chunking/{chunker,policies,models}.py`, `core/context/` | **REFERENCIADO / POR AUDITAR** según consumidor efectivo |
| Contractualización y tests | NADR-03/NADR-F17BIS-16; pruebas de `chunker_snapshot`, `g3_chunk_identity_contract`, normalización, matemáticas y perfiles | **POR INSPECCIONAR**; no inferir PASS |
| Persistencia/FS, G3 worker, G5, host, GT | Repositorios/plan de trabajo y rutas downstream | **REFERENCIADO**: PPPR.0.5/0.6/0.7/0.8 |
| Calidad científica del producto | PDFs reales con oráculo independiente | **NO VERIFICABLE** sin evidencia/autorización correspondiente |

Esta tabla **no cumple todavía** el requisito §8.1 de 100% del alcance auditado. El HITO se mantendrá `IN_PROGRESS` hasta reconciliarlo.

## 4. FUENTES DE EVIDENCIA

**Primarias (código de `main@1d21cfe`):**

- `apps/ocr_router/__main__.py` (hash del raw AST, plan contextual y frontera de registro).
- `core/ast/{builder,cross_page,hashing}.py` (AST plano, sutura inter-página, hash semántico).
- `core/chunking/{contextual_plan,semantic_chunking,manifest_contract}.py` (enriquecimiento, agrupamiento, unidades, restricciones de cobertura).
- `core/normalization/{pipeline,normalizer,explicit_math}.py` (implementaciones disponibles; aún no acreditadas como ejecutadas por la ruta OCR).

**Normativas:** metodologías FROZEN, scope/principios; antecedentes PPPR.0.1/0.2. **Normativa aún por cotejar:** NADR-03 y NADR-F17BIS-16. **Testigos aún por cotejar:** código de tests existente; no ejecución. **Decisiones previas:** D-1/D-2, Atlas, sin reabrir su convergencia.

## 5. MAPA DE FLUJOS OBSERVADOS (PARCIAL)

```text
CLI/OCR root (PPPR.0.1) [REFERENCIADO]
 → PyMuPDF / DocumentLayout / AST (PPPR.0.2) [REFERENCIADO]
 → FlatASTBuilder → CrossPageNormalizer [OBSERVADO]
 → OCRRouterDaemon._process_document [OBSERVADO]
    → compute_ast_hash(raw_ast) [OBSERVADO, identidad semántica]
    → prepare_contextual_plan(document_id, raw_ast, estimator) [OBSERVADO]
       → HierarchicalContextEnricher.enrich_document [CONEXIÓN OBSERVADA, interior pendiente]
       → guard igualdad de compute_ast_hash pre/post [OBSERVADO]
       → agrupación por CTX y HEADING preservado [OBSERVADO]
       → TokenBudgetChunker.chunk_group [OBSERVADO]
       → ChunkPlan.build → validate_chunk_coverage [OBSERVADO]
    → AST/plan/snapshots/estados [REFERENCIADO: PPPR.0.5]
 → G3/LLM y G5 [REFERENCIADO: PPPR.0.4–0.6]
```

Las clases `NormalizationPipeline`, `TextNormalizer`, `PolicyDrivenStreamingChunker` y `MarkdownSegmenter` están presentes en el árbol, **pero su activación en este root queda por demostrar**. Ausencia de llamadas en los archivos leídos no prueba que estén desconectadas en todo el repositorio.

## 10. REGISTRO INICIAL DE EVIDENCIA FORENSE

| ID | Sev. | Evidencia directa → observación | Required / Decision / límite | Estado |
|---|---|---|---|---|
| **E-0.3-001** | P2 | `OCRRouterDaemon._process_document` calcula hash de AST crudo y llama `prepare_contextual_plan`; verifica identidad contra el plan. | Conecta la frontera de extracción a un plan de G3; no certifica persistencia entre FS/SQLite. | OBSERVADO |
| **E-0.3-002** | P2 | `compute_ast_hash` serializa en orden `node_type` y `text_content`, excluye `node_id`, `sequence_id` y `metadata`. | **Contrato alternativo semántico declarado**, diferente del oráculo. No clasificar exclusión de metadata como GAP sin cotejar identidades exigidas por consumidores. | OBSERVADO |
| **E-0.3-003** | P2 | `prepare_contextual_plan` calcula hash antes/después de `HierarchicalContextEnricher.enrich_document` y rechaza deriva semántica. | Demuestra guard sobre el hash definido, **no** sobre campos excluidos. | OBSERVADO |
| **E-0.3-004** | P2 | `prepare_contextual_plan` agrupa por `context_id` validado; HEADING crea grupo `PRESERVE_HEADING_NO_INFERENCE`. | Ruta de contexto tipada observada, exactitud semántica de cada heading aún por comprobar. | OBSERVADO |
| **E-0.3-005** | P2 | `TokenBudgetChunker.chunk_group` aísla `PASSTHROUGH`, matemáticas, CODE, IMAGE y otras fronteras, y segmenta por oraciones cuando excede presupuesto. | Comportamiento de código; alcance frente a abreviaturas/decimales STEM y oraciones largas pendiente de evidencia. | OBSERVADO |
| **E-0.3-006** | P2 | `validate_chunk_coverage` valida orden de miembros, unicidad, reconstrucción exacta `"".join(source_text)`, IDs y estrategias; `ChunkPlan.build` lo llama. | Contrato de cobertura fuerte de AST→unidades; no demuestra que el AST represente todo el PDF físico. | OBSERVADO |
| **E-0.3-007** | P2 | `CrossPageNormalizer.should_merge` fusiona tipos compatibles en páginas adyacentes si el texto precedente carece de puntuación terminal (o termina en abreviatura), con reglas de guion; se ejecuta antes del hash. | Regla heurística observada, no una pérdida concreta. Requiere testigo/oráculo antes de declarar error de semántica científica. | HIPÓTESIS DE RIESGO |
| **E-0.3-008** | P2 | `NormalizationPipeline.process_node` expone política/hash de normalización; `TextNormalizer.normalize` usa `NFKC`, pero conexión productiva de ambas rutas no corroborada aún. | Inventario de capacidades **no** prueba activación en el OCR seleccionado. | TO BE VERIFIED |

**Interpretación de severidad:** P2 expresa límites de cobertura o riesgo latente, **no** defecto confirmado ni obligación implementativa. Se reclasificarán entradas solo mediante contraste `Observed / Required / Decision` del contrato vigente.

## 14. GAPS CONSOLIDADOS

**Ningún GAP emitido en esta apertura.** Falta auditar los contratos normativos, consumidores y tests. Diferencias entre hashes o simples mecanismos heurísticos no constituyen incumplimiento demostrado. Los IDs se asignarán únicamente cuando exista evidencia que satisfaga §4.7–4.8.

## 15. HIPÓTESIS ABIERTAS / DEFERRED QUESTIONS (IN_PROGRESS)

| ID | Pregunta falsable | Estado y próximo control |
|---|---|---|
| **H-0.3-A** | ¿Qué operaciones de normalización se ejecutan realmente en el root OCR y con qué orden? | **TO BE VERIFIED**: rastreo de composición y consumidores; `core/normalization/` y `runtime/` |
| **H-0.3-B** | ¿Una modificación de metadata física puede compartir `compute_ast_hash` con una generación que requiere identidad distinta? | **TO BE VERIFIED**: contrastar NADR de identidades con persistencia/consumidores (PPPR.0.5) antes de afirmar GAP |
| **H-0.3-C** | ¿La sutura inter-página une erróneamente párrafos de un paper real? | **TO BE VERIFIED**: falsador local y, para ciencia, evidencia física (PPPR.0.8) |
| **H-0.3-D** | ¿Segmentación heurística por oración respeta límites de términos científicos y presupuesto en casos frontera? | **TO BE VERIFIED**: tests existentes, estimador, postcondiciones de cobertura |
| **H-0.3-E** | ¿Las unidades PRESERVE/PARTIAL llegan intactas y sin inferencia al consumidor G3/G5? | **TO BE VERIFIED**: contratos de `ChunkPlan`; consumidores especializados en PPPR.0.5/0.6 |

Al cierre se exigirá `CONFIRMADA`, `RESUELTA`, `RECHAZADA` o `NO VERIFICABLE` y destino explícito para cada hipótesis conforme a §8.1–8.2. Ninguna queda resuelta por la sola lectura de su nombre o docstring.

## 16. RESPUESTAS INICIALES AL MANDATO

La cadena AST→enriquecimiento→grupos→unidades→plan está conectada por composición explícita. El hash semántico no es la identidad canónica de oráculo y los checks de chunking operan sobre el texto que **ya existe** en el AST. Queda por reconciliar normalización, segmentadores alternativos, protección de matemática, identidades de generación, fronteras de persistencia y testigos antes de un veredicto definitivo.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN.** Apertura de la auditoría PPPR.0.3 sobre la nueva base de gobernanza, no una revisión final. Pendientes obligatorios: inventario de consumidores/activación, normas relevantes, testigos, trazabilidad de los límites, hipótesis y checklist §8.1–8.2. No se ejecutó ningún test ni se creó código de producción.

**Siguiente gate:** ampliar el mismo HITO dentro del PR interno a `pdf-pdf-product-readiness`, evitando merges a `main`. El PR #66 debe permanecer Draft hasta completar la gobernanza y el Execution Plan.
