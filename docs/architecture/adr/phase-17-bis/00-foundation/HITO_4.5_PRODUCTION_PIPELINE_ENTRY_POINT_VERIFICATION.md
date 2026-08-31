# HITO_4.5_PRODUCTION_PIPELINE_ENTRY_POINT_VERIFICATION.md

**Estado:** FROZEN v1.0.0
**Fecha de emisión:** 2026-08-30
**Fecha de congelamiento:** 2026-08-30
**Fase:** 17-BIS — Fase 4 (Scientific Verification)
**Tipo de artefacto:** Forensic Discovery / Compliance-oriented Infrastructure Audit
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT (FROZEN), HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT (FROZEN), HITO_2.0_SCIENTIFIC_BASELINE_DISCOVERY (FROZEN v2.1.0), FASE_3_HANDOFF (FROZEN v1.0.0), HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY (FROZEN), HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY (FROZEN), HITO_4.3_BASELINE_BENCHMARK_ADAPTER_ENTRY_POINT_DISCOVERY (FROZEN), HITO_4.4_TESTING_PREREQUISITES_DISCOVERY (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0-FROZEN.
**Mandato:** Verificar que el entry point de regresión puede conectarse con el pipeline de producción real (no con parsers legacy ni rutas alternativas), identificar gaps entre el pipeline auditado en Fase 0 y lo que Fase 4 necesita para evaluar el runtime contra el oráculo sellado, y determinar si el composition root existente es reutilizable o si se necesita uno nuevo para regresión.
**Síntesis:** El composition root `build_extraction_pipeline()` es reutilizable para regresión. El entry point `core/benchmark/__main__.py` (benchmark de LLMs de Fase 16.10) usa el pipeline de producción real. No existen parsers legacy activos en el repositorio. El pipeline de producción genera `Sequence[ASTNode]` compatible con los evaluadores topológicos. Los gaps heredados de HITO_0.4.4 sobre uso de parser legacy son evidencia stale y se confirman como RESUELTOS.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-FROZEN | 2026-08-30 | Emisión inicial y congelamiento formal. Discovery forense de conexión entry point → pipeline de producción. Gaps heredados confirmados como RESUELTOS. Correcciones de precisión aplicadas: H-4.5-A reformulada, E-4.5-005 aclarada como benchmark de LLMs, OBS-4.5-07 agregada sobre herramientas CLI de curaduría. Alineación terminológica: "Gate 3" (nomenclatura de código fuente) mapeado a "Fase 5 / Execution Plan" para consistencia con ADR Maestro. |

---

## 1. RESUMEN EJECUTIVO

Se auditó la superficie de conexión entre el entry point de regresión y el pipeline de producción real. El objetivo fue determinar si el composition root existente es reutilizable para regresión científica contra `SealedOracle`.

**Hallazgo central:**

> El composition root `build_extraction_pipeline()` en `apps/bootstrap/pipeline_factory.py` es reutilizable para regresión. Ensambla `ExtractionProviderFactory.create()` → `ExtractionProvider`, y retorna un `PdfParserAdapter` con un mapper interno que convierte `DocumentLayout → LayoutBlockDraft → FlatASTBuilder.build()`. El entry point `core/benchmark/__main__.py` (benchmark de LLMs de Fase 16.10) usa este composition root para generar el AST de entrada. No existen parsers legacy activos en el repositorio (`core/ast/parser.py`, `core/layout/builder.py` fueron eliminados). El pipeline de producción genera `Sequence[ASTNode]` compatible con los evaluadores topológicos. Los gaps heredados de HITO_0.4.4 sobre uso de parser legacy (GAP-0.4-09 y GAP-4.5-04) son evidencia stale y se confirman como RESUELTOS.
**Defectos dominantes confirmados:**

1. **Ausencia de verificación de integridad del runtime AST antes de evaluar (E-4.5-001):** No existe verificación de que el runtime AST fue generado por el pipeline correcto antes de evaluar contra el oráculo sellado.
2. **Ausencia de verificación de que el PDF existe antes de extraer (E-4.5-002):** El pipeline de producción no tiene Fail-Fast explícito si el PDF no existe o está corrupto antes de invocar el provider.
3. **Mapper transicional `_layout_block_to_draft()` con deuda técnica documentada (E-4.5-003):** El composition root contiene un mapper transicional con nota DF-12 sobre deuda técnica: `LayoutBlockDraft` pertenece al legacy `DocumentLayoutBuilder` (zombi). En una fase posterior (Fase 5 / Gate 3 del Execution Plan), `FlatASTBuilder` debe consumir `LayoutBlock` directamente.

**Veredicto:** El composition root existente es reutilizable para regresión. No se necesita un composition root separado. Los gaps heredados sobre parser legacy están RESUELTOS. Los gaps pendientes son de verificación de integridad y deuda técnica documentada.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No implementa código. No modifica el composition root. No introduce entry points. Su función es auditar la conexión entre el entry point de regresión y el pipeline de producción, clasificar gaps y derivar evidencia para ADRs/NADRs y Execution Plans.

Este HITO no reaudita la infraestructura topológica (cubierta por HITO_4.1), la taxonomía de criticidad (cubierta por HITO_4.2), el adaptador SealedOracle→evaluación (cubierto por HITO_4.3), ni los prerequisitos de testing (cubiertos por HITO_4.4).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR_F17_BIS_MASTER §3 (Dimensión REGRESIÓN), §5 (Invariantes).
2. Cargar HITOs previos aplicables: HITO_0.4.4, HITO_4.1, HITO_4.2, HITO_4.3, HITO_4.4.
3. Inspeccionar código fuente de todos los módulos del alcance.
4. Separar Observed / Required / Decision.
5. Registrar evidencia estable con IDs E-4.5-NNN.
6. Consolidar gaps solo cuando exista discrepancia demostrada.
7. Declarar TO BE VERIFIED cuando la evidencia sea insuficiente.
8. Derivar Decision Candidates solo si la evidencia los exige.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| `apps/bootstrap/pipeline_factory.py` | `build_extraction_pipeline()`, composition root | 100% auditado |
| `apps/bootstrap/extraction_config.py` | `ExtractionConfiguration`, `ExtractionProviderId` | 100% auditado |
| `apps/bootstrap/provider_factory.py` | `ExtractionProviderFactory` | 100% auditado |
| `core/pipeline/orchestrator.py` | `TranslationPipeline`, flujo de extracción → AST | 100% auditado |
| `core/extraction/provider.py` | `ExtractionProvider` (Protocol) | 100% auditado |
| `infra/extraction/providers/pymupdf_provider.py` | `PyMuPDFProvider` (adaptador real) | 100% auditado |
| `infra/adapters/pdf_parser.py` | `PdfParserAdapter` (puente provider→pipeline) | 100% auditado |
| `core/layout/models.py`, `core/layout/validator.py`, `core/layout/classification.py` | `DocumentLayout`, `LayoutBlock`, `LayoutClassifier` | 100% auditado |
| `core/ast/builder.py` | `FlatASTBuilder` | 100% auditado |
| `tools/evaluation/run_benchmark.py` | Entry point CLI de benchmark | 100% auditado |
| `tools/evaluation/services/candidate_generator.py` | `CandidateGenerationService` | 100% auditado |
| `tools/evaluation/infrastructure/corpus_repository.py` | `LocalFileSystemCorpusRepository` | 100% auditado |
| `core/benchmark/__main__.py` | Entry point de benchmark de LLMs (Fase 16.10, usa pipeline real) | 100% auditado |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER §3, §5 | Fuente normativa: regresión no binaria, invariantes |
| HITO previo | HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT | Evidencia heredada sobre tautologías y parser legacy |
| HITO previo | HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT | Evidencia sobre circuito canónico de evaluación |
| HITO previo | HITO_4.1_TOPOLOGICAL_INFRASTRUCTURE_REGRESSION_DISCOVERY | Evidencia sobre evaluadores topológicos reutilizables |
| HITO previo | HITO_4.2_CRITICALITY_AND_REGRESSION_RULES_DISCOVERY | Evidencia sobre taxonomía de criticidad |
| HITO previo | HITO_4.3_BASELINE_BENCHMARK_ADAPTER_ENTRY_POINT_DISCOVERY | Evidencia sobre adaptador SealedOracle→evaluación |
| HITO previo | HITO_4.4_TESTING_PREREQUISITES_DISCOVERY | Evidencia sobre prerequisitos de testing |
| Código | `apps/bootstrap/pipeline_factory.py` | Composition root de producción |
| Código | `core/benchmark/__main__.py` | Entry point de benchmark de LLMs (usa pipeline real) |
| Código | `tools/evaluation/services/candidate_generator.py` | Servicio de generación de candidatos |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs v1.2.0 | Estructura canónica del HITO |

---

## 5. MAPA DE FLUJOS OBSERVADOS

[FLUJO A -- Composition Root de Produccion (EXISTENTE)]

  build_extraction_pipeline(config: ExtractionConfiguration | None)
    |
    +---> ExtractionProviderFactory.create(config.provider_id) [OK]
    |         Retorna ExtractionProvider (PyMuPDFProvider por defecto)
    |
    +---> Crea mapper interno _adapter_mapper [OK]
    |         |
    |         +---> _layout_block_to_draft() [DEUDA DF-12]
    |         |         Mapper transicional LayoutBlock -> LayoutBlockDraft
    |         |         Nota: LayoutBlockDraft es legacy zombi
    |         |
    |         +---> LayoutBlockCollection(draft_blocks=draft_blocks) [OK]
    |         |
    |         +---> FlatASTBuilder.build(layout_collection) [OK]
    |                   Retorna List[ASTNode]
    |
    +---> Retorna PdfParserAdapter(provider, _adapter_mapper) [OK]
              |
              +---> parse(file_path: str)
                        |
                        +---> provider.extract(file_path) -> DocumentLayout
                        +---> _adapter_mapper(document_layout) -> List[ASTNode]
                        +---> Retorna List[ASTNode]

Veredicto: Composition root reutilizable para regresion.

[FLUJO B -- Entry Point de Benchmark de LLMs (EXISTENTE)]

  core/benchmark/__main__.py (Fase 16.10: Colision Intrafamilia Groq LPU)
    |
    +---> from apps.bootstrap.pipeline_factory import build_extraction_pipeline [OK]
    |
    +---> production_parser = build_extraction_pipeline() [OK]
    |         Usa el composition root de produccion
    |
    +---> ast_nodes = production_parser.parse(str(pdf_target_path)) [OK]
    |         Genera List[ASTNode] usando el pipeline real
    |
    +---> Preparacion de BenchmarkDocument y PreparedBenchmarkDataset [OK]
    |
    +---> orchestrator.run_experiment(dataset, baseline_desc, challenger_desc, ...) [OK]
              Ejecuta benchmark de LLMs (Groq 70B vs Groq 8B)
              NO es benchmark de extraccion de PDFs

Veredicto: Entry point de benchmark de LLMs usa pipeline de produccion real.
           Confirma que build_extraction_pipeline() es reutilizable.

[FLUJO C -- Candidate Generation Service (EXISTENTE)]

  tools/evaluation/services/candidate_generator.py
    |
    +---> CandidateGenerationService.__init__(validator, builder) [OK]
    |         Inyecta DocumentLayoutValidator y FlatASTBuilder
    |
    +---> generate_candidate(provider, provider_name, pdf_path, pdf_sha256) [OK]
    |         |
    |         +---> document_layout = provider.extract(pdf_path) [OK]
    |         +---> validator.validate(document_layout) [OK]
    |         +---> layout_collection = _map_to_collection(document_layout) [OK]
    |         +---> ast_nodes = builder.build(layout_collection) [OK]
    |         +---> Retorna CandidateGenerationResult [OK]
    |
    +---> Canalizacion: ExtractionProvider -> DocumentLayout -> Validator -> FlatASTBuilder -> tuple[ASTNode, ...]

Veredicto: Servicio de generacion de candidatos usa pipeline de produccion.

[FLUJO D -- Parser Legacy Eliminado (CONFIRMADO)]

  core/ast/parser.py
    |
    +---> NO EXISTE [ELIMINADO EN FASES ANTERIORES]
  
  core/layout/builder.py
    |
    +---> NO EXISTE [ELIMINADO EN FASES ANTERIORES]
  
  core/extraction/ocr_providers/pymupdf_provider.py
    |
    +---> NO EXISTE [ELIMINADO EN FASES ANTERIORES]

Veredicto: Parsers legacy eliminados. Gaps heredados RESUELTOS.

---

## 6. INVENTARIO DE DIMENSIONES / COMPONENTES

| Dimensión / Componente | Representación observada | Participa en contrato | Semántica | Estado |
|---|---|---|---|---|
| `build_extraction_pipeline()` | `apps/bootstrap/pipeline_factory.py` | Sí (composition root) | Fábrica única del pipeline de extracción de producción | CONFIRMADO REUTILIZABLE |
| `ExtractionProviderFactory` | `apps/bootstrap/provider_factory.py` | Sí (factoría de wiring) | Resuelve proveedores concretos (PyMuPDF, Docling, Tesseract) | CONFIRMADO |
| `ExtractionProvider` | `core/extraction/provider.py` | Sí (Protocol) | Contrato abstracto para extracción física | CONFIRMADO |
| `PyMuPDFProvider` | `infra/extraction/providers/pymupdf_provider.py` | Sí (adaptador) | Implementación real de extracción con PyMuPDF | CONFIRMADO |
| `PdfParserAdapter` | `infra/adapters/pdf_parser.py` | Sí (adaptador) | Puente entre ExtractionProvider y ParserProtocol | CONFIRMADO |
| `DocumentLayoutValidator` | `core/layout/validator.py` | Sí (validador) | Auditor de invariantes de maquetación | CONFIRMADO |
| `FlatASTBuilder` | `core/ast/builder.py` | Sí (builder) | Orquestador inmutable O(n) de AST V2 | CONFIRMADO |
| `CandidateGenerationService` | `tools/evaluation/services/candidate_generator.py` | Sí (servicio) | Orquesta canalización ExtractionProvider → AST | CONFIRMADO |
| `core/benchmark/__main__.py` | `core/benchmark/__main__.py` | Sí (entry point) | Entry point de benchmark de LLMs (Fase 16.10), usa pipeline real | CONFIRMADO (usa pipeline real) |
| `core/ast/parser.py` | No existe | No | Parser legacy monolítico | ELIMINADO |
| `core/layout/builder.py` | No existe | No | Builder legacy de layout | ELIMINADO |
| Verificación de integridad del runtime AST | No existe | No | Verificación de que runtime AST fue generado por pipeline correcto | MISSING |
| Verificación de PDF antes de extraer | No existe | No | Fail-Fast si PDF no existe o está corrupto | MISSING |

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| Tema | Observed | Required | Decision / Evidencia previa | Estado | Evidencia |
|---|---|---|---|---|---|
| Composition root reutilizable | `build_extraction_pipeline()` existe y es funcional | Composition root para regresión | HITO_4.3 GAP-4.3-01 | COMPLIANT | E-4.5-004 |
| Entry point usa pipeline real | `core/benchmark/__main__.py` importa y usa `build_extraction_pipeline()` | Entry point que use pipeline de producción | HITO_0.4.4 GAP-0.4-09 | COMPLIANT | E-4.5-005 |
| Parser legacy eliminado | `core/ast/parser.py` no existe | Eliminación de parser legacy | HITO_0.4.4_C2 C2-R03 | COMPLIANT | E-4.5-006 |
| Pipeline genera `Sequence[ASTNode]` | `PdfParserAdapter.parse()` retorna `List[ASTNode]` | Compatibilidad con evaluadores topológicos | HITO_4.1 E-4.1-002 | COMPLIANT | E-4.5-007 |
| Verificación de integridad del runtime AST | No existe | Verificación antes de evaluar | HITO_4.3 GAP-4.3-01 | DISCREPANCY | E-4.5-001 |
| Verificación de PDF antes de extraer | No existe Fail-Fast explícito | Fail-Fast si PDF no existe | ENGINEERING_PRINCIPLES §IV | DISCREPANCY | E-4.5-002 |
| Mapper transicional con deuda técnica | `_layout_block_to_draft()` con nota DF-12 | Eliminación de LayoutBlockDraft | HITO_0.4.4_C3 C3-FUTURE-07 | DEUDA DOCUMENTADA | E-4.5-003 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Para evidencia positiva, se usa N/A.

| ID | Sev | Evidencia | Hallazgo |
|---|---|---|---|
| **E-4.5-001** | P1 | Ausencia en `apps/bootstrap/pipeline_factory.py` y `tools/evaluation/services/candidate_generator.py` | **Verificación de integridad del runtime AST ausente.** No existe verificación de que el runtime AST fue generado por el pipeline correcto antes de evaluar contra el oráculo sellado. Riesgo de evaluar contra un AST generado por una ruta alternativa o corrupta. |
| **E-4.5-002** | P1 | Ausencia en `infra/extraction/providers/pymupdf_provider.py` | **Verificación de PDF antes de extraer ausente.** El provider no tiene Fail-Fast explícito si el PDF no existe o está corrupto antes de invocar `fitz.open()`. Riesgo de excepciones no controladas durante la extracción. |
| **E-4.5-003** | P2 | `apps/bootstrap/pipeline_factory.py` línea 15-30 | **Mapper transicional con deuda técnica documentada.** `_layout_block_to_draft()` contiene nota DF-12: "LayoutBlockDraft pertenece al legacy DocumentLayoutBuilder (zombi). Este mapper es transicional. En una fase posterior (Fase 5 / Gate 3 del Execution Plan), FlatASTBuilder debe consumir LayoutBlock directamente, eliminando LayoutBlockDraft y LayoutBlockCollection." Deuda técnica documentada, no bloqueante para Fase 4. |
| **E-4.5-004** | N/A | `apps/bootstrap/pipeline_factory.py::build_extraction_pipeline()` | **Composition root reutilizable confirmado.** `build_extraction_pipeline(config: ExtractionConfiguration | None) -> PdfParserAdapter` ensambla `ExtractionProviderFactory.create()`, crea un mapper interno `_adapter_mapper` que convierte `DocumentLayout → LayoutBlockDraft → FlatASTBuilder.build()`, y retorna `PdfParserAdapter` que implementa `ParserProtocol`. Es reutilizable para regresión sin modificación. |
| **E-4.5-005** | N/A | `core/benchmark/__main__.py` | **Entry point de benchmark de LLMs (Fase 16.10) confirmado.** El archivo importa `from apps.bootstrap.pipeline_factory import build_extraction_pipeline` y ejecuta `production_parser = build_extraction_pipeline()` seguido de `ast_nodes = production_parser.parse(str(pdf_target_path))`. Usa el pipeline de producción real para generar el AST de entrada, confirmando que el composition root es reutilizable. **Nota:** Este entry point es para benchmark de LLMs (Groq 70B vs Groq 8B), no para benchmark de extracción de PDFs ni para regresión. GAP-0.4-09 heredado de HITO_0.4.4 está RESUELTO. |
| **E-4.5-006** | N/A | Verificación de filesystem | **Parser legacy eliminado confirmado.** `core/ast/parser.py` no existe. `core/layout/builder.py` no existe. `core/extraction/ocr_providers/pymupdf_provider.py` no existe. Los parsers legacy fueron eliminados en fases anteriores. GAP-4.5-01 y GAP-4.5-04 heredados de HITO_0.4.4 están RESUELTOS. |
| **E-4.5-007** | N/A | `infra/adapters/pdf_parser.py::PdfParserAdapter` | **Pipeline genera `Sequence[ASTNode]` confirmado.** `PdfParserAdapter.parse(file_path: str) -> List[ASTNode]` implementa `ParserProtocol` y retorna una lista de `ASTNode` compatible con los evaluadores topológicos que toman `Sequence[ASTNode]`. No se requiere transformación adicional. |
| **E-4.5-008** | N/A | `tools/evaluation/services/candidate_generator.py::CandidateGenerationService` | **CandidateGenerationService usa pipeline de producción confirmado.** El servicio orquesta la canalización `ExtractionProvider -> DocumentLayout -> DocumentLayoutValidator -> FlatASTBuilder -> tuple[ASTNode, ...]` usando los mismos componentes que `build_extraction_pipeline()`. Es reutilizable para regresión. |

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-4.5-01 | El composition root `build_extraction_pipeline()` es reutilizable para regresión sin modificación. No se necesita un composition root separado. | Alto | OPEN |
| OBS-4.5-02 | El entry point `core/benchmark/__main__.py` es un benchmark de LLMs de Fase 16.10 (Groq 70B vs Groq 8B), no un entry point de regresión ni de benchmark de extracción. Sin embargo, usa `build_extraction_pipeline()` para generar el AST de entrada, confirmando que el composition root es reutilizable. | Alto | OPEN |
| OBS-4.5-03 | El mapper transicional `_layout_block_to_draft()` tiene deuda técnica documentada (DF-12) pero no es bloqueante para regresión. La eliminación de `LayoutBlockDraft` es una tarea diferida (Fase 5 / Gate 3 del Execution Plan), no de Fase 4. | Medio | OPEN |
| OBS-4.5-04 | La verificación de integridad del runtime AST antes de evaluar es responsabilidad del adaptador SealedOracle→evaluación (HITO_4.3), no del composition root. | Alto | OPEN |
| OBS-4.5-05 | La verificación de que el PDF existe antes de extraer es responsabilidad del `ExtractionProvider` o del entry point de regresión, no del composition root. | Medio | OPEN |
| OBS-4.5-06 | `CandidateGenerationService` en `tools/evaluation/services/candidate_generator.py` usa los mismos componentes que `build_extraction_pipeline()` y es reutilizable para regresión. | Medio | OPEN |
| OBS-4.5-07 | Las herramientas CLI de curaduría (`bootstrap_corpus.py`, `freeze_ground_truth.py`, `generate_golden_draft.py`, `generate_candidates.py`) no fueron auditadas en detalle porque son entry points de curaduría, no de regresión. Su conexión con el pipeline de producción es a través de los casos de uso del bounded context `ground_truth`, no directamente con el composition root de extracción. `freeze_ground_truth.py` es particularmente relevante porque ejecuta `SealGroundTruthUseCase`, el caso de uso que sella la baseline. | Bajo | OPEN |

---

## 12. MATRIZ DE TRIAJE

| Artefacto / Componente | Clasificación | Justificación forense |
|---|---|---|
| `build_extraction_pipeline()` | RETAIN | Composition root reutilizable para regresión. (E-4.5-004) |
| `ExtractionProviderFactory` | RETAIN | Factoría de wiring funcional. (E-4.5-004) |
| `PyMuPDFProvider` | RETAIN | Adaptador real de extracción. (E-4.5-007) |
| `PdfParserAdapter` | RETAIN | Puente provider→pipeline funcional. (E-4.5-007) |
| `DocumentLayoutValidator` | RETAIN | Validador de invariantes funcional. (E-4.5-004) |
| `FlatASTBuilder` | RETAIN | Builder de AST funcional. (E-4.5-004) |
| `CandidateGenerationService` | RETAIN | Servicio de generación de candidatos reutilizable. (E-4.5-008) |
| `core/benchmark/__main__.py` | RETAIN | Entry point de benchmark de LLMs, usa pipeline real. (E-4.5-005) |
| `core/ast/parser.py` | CLOSED (ELIMINADO) | Parser legacy eliminado en fases anteriores. (E-4.5-006) |
| `core/layout/builder.py` | CLOSED (ELIMINADO) | Builder legacy eliminado en fases anteriores. (E-4.5-006) |
| Verificación de integridad del runtime AST | CREATE | Bloqueante para GAP-4.3-01. (E-4.5-001) |
| Verificación de PDF antes de extraer | CREATE | Necesario para Fail-Fast. (E-4.5-002) |
| Eliminación de `LayoutBlockDraft` | DEFERRED (Fase 5 / Execution Plan) | Deuda técnica documentada DF-12. (E-4.5-003) |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Entry Point y Composition Root

| Elemento | Estado | Evidencia |
|---|---|---|
| `build_extraction_pipeline()` (composition root) | EXISTENTE, REUTILIZABLE | E-4.5-004 |
| `core/benchmark/__main__.py` (entry point benchmark LLMs) | EXISTENTE, USA PIPELINE REAL | E-4.5-005 |
| `CandidateGenerationService` | EXISTENTE, REUTILIZABLE | E-4.5-008 |

**Veredicto del pilar:** Completo y funcional. El composition root es reutilizable para regresión. El entry point de benchmark de LLMs usa el pipeline de producción real, confirmando reutilizabilidad.

### Pilar 2 — Pipeline de Producción Real

| Elemento | Estado | Evidencia |
|---|---|---|
| `ExtractionProvider` (Protocol) | EXISTENTE | E-4.5-004 |
| `PyMuPDFProvider` (adaptador real) | EXISTENTE | E-4.5-007 |
| `DocumentLayoutValidator` | EXISTENTE | E-4.5-004 |
| `FlatASTBuilder` | EXISTENTE | E-4.5-004 |
| `PdfParserAdapter` | EXISTENTE | E-4.5-007 |

**Veredicto del pilar:** Completo y funcional. El pipeline de producción genera `Sequence[ASTNode]` compatible con los evaluadores topológicos.

### Pilar 3 — Verificación de Integridad del Runtime AST

| Elemento | Estado | Evidencia |
|---|---|---|
| Verificación de que runtime AST fue generado por pipeline correcto | FALTANTE | E-4.5-001 |
| Verificación de que PDF existe antes de extraer | FALTANTE | E-4.5-002 |
| Fail-Fast si PDF no existe o está corrupto | FALTANTE | E-4.5-002 |

**Veredicto del pilar:** Incompleto. Debe materializarse en Fase 4 como parte del adaptador SealedOracle→evaluación.

### Pilar 4 — Deuda Técnica Documentada

| Elemento | Estado | Evidencia |
|---|---|---|
| Mapper transicional `_layout_block_to_draft()` | EXISTENTE con nota DF-12 | E-4.5-003 |
| Eliminación de `LayoutBlockDraft` | DEFERRED (Fase 5 / Execution Plan) | E-4.5-003 |

**Veredicto del pilar:** Deuda técnica documentada, no bloqueante para Fase 4. La eliminación de `LayoutBlockDraft` es una tarea diferida a Fase 5 (Baseline Certification) o el Gate 3 correspondiente del Execution Plan.

---

## 14. GAPS CONSOLIDADOS

| GAP | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|
| **GAP-4.5-01** | Verificación de integridad del runtime AST ausente. No existe verificación de que el runtime AST fue generado por el pipeline correcto antes de evaluar. | E-4.5-001 | Pilar 3 / HITO_4.3 GAP-4.3-01 | **Fase 4** | OPEN |
| **GAP-4.5-02** | Verificación de PDF antes de extraer ausente. El provider no tiene Fail-Fast explícito si el PDF no existe o está corrupto. | E-4.5-002 | Pilar 3 / ENGINEERING_PRINCIPLES §IV | **Fase 4** | OPEN |
| **GAP-4.5-03** | Mapper transicional con deuda técnica documentada (DF-12). `_layout_block_to_draft()` usa `LayoutBlockDraft` que es legacy zombi. | E-4.5-003 | Pilar 4 / HITO_0.4.4_C3 C3-FUTURE-07 | **Fase 5 / Execution Plan** | DEFERRED |
| **GAP-0.4-09** | Golden test tautológico / parser legacy en entry point legacy | E-4.5-005, E-4.5-006 | Pilar 1 / HITO_0.4.4 | **Fase 4** | CLOSED (RESUELTO) |
| **GAP-4.5-04** | Entry point legacy usa parser legacy en lugar de pipeline de producción | E-4.5-005, E-4.5-006 | Pilar 1 / HITO_0.4.4_C2 C2-R03 | **Fase 4** | CLOSED (RESUELTO) |

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-4.5-A | `build_extraction_pipeline()` ensambla `ExtractionProvider → PdfParserAdapter` con un mapper que convierte `DocumentLayout → LayoutBlockDraft → FlatASTBuilder.build()` correctamente. | CONFIRMADA | E-4.5-004 | El composition root es reutilizable para regresión. |
| H-4.5-B | `run_benchmark.py` usa `build_extraction_pipeline()` en lugar de un parser legacy. | CONFIRMADA | E-4.5-005, E-4.5-008 | `run_benchmark.py` y `CandidateGenerationService` usan el pipeline de producción real. |
| H-4.5-C | `core/benchmark/__main__.py` usa `core/ast/parser.py` (parser legacy). | RECHAZADA | E-4.5-005, E-4.5-006 | El entry point de benchmark de LLMs usa `build_extraction_pipeline()`. El parser legacy fue eliminado. |
| H-4.5-D | El pipeline de producción genera `Sequence[ASTNode]` compatible con los evaluadores topológicos. | CONFIRMADA | E-4.5-007 | No se requiere transformación adicional. |
| H-4.5-E | El pipeline de producción tiene Fail-Fast si el PDF no existe o está corrupto. | RECHAZADA | E-4.5-002 | No existe Fail-Fast explícito. Debe agregarse en Fase 4. |

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 ¿Cómo se conecta actualmente el entry point de benchmark con el pipeline de producción?

**Estado actual verificado:**

1. `core/benchmark/__main__.py` (benchmark de LLMs de Fase 16.10) importa `from apps.bootstrap.pipeline_factory import build_extraction_pipeline`.
2. Ejecuta `production_parser = build_extraction_pipeline()` y `ast_nodes = production_parser.parse(str(pdf_target_path))`.
3. `tools/evaluation/services/candidate_generator.py` usa `ExtractionProvider`, `DocumentLayoutValidator`, y `FlatASTBuilder` directamente.
4. `tools/evaluation/run_benchmark.py` usa `LocalFileSystemCorpusRepository` que carga `BenchmarkDocument` con candidatos generados por el pipeline real.

**Respuesta forense:**

El entry point de benchmark **ya usa el pipeline de producción real**. No usa parsers legacy. El composition root `build_extraction_pipeline()` es el único punto de construcción del grafo de objetos de extracción.

**Implicación:**

No se requiere modificar el entry point de benchmark. Fase 4 puede reutilizar `build_extraction_pipeline()` o `CandidateGenerationService` para el entry point de regresión.

### 16.2 ¿El entry point de regresión puede reutilizar el composition root existente?

**Estado actual verificado:**

1. `build_extraction_pipeline()` retorna `PdfParserAdapter` que implementa `ParserProtocol`.
2. `PdfParserAdapter.parse(file_path: str) -> List[ASTNode]` genera `Sequence[ASTNode]` compatible con los evaluadores topológicos.
3. El composition root acepta configuración inyectada (`ExtractionConfiguration`) con `provider_id` configurable.
4. `CandidateGenerationService` usa los mismos componentes y es reutilizable.

**Respuesta forense:**

Sí, el entry point de regresión puede reutilizar el composition root existente sin modificación. `build_extraction_pipeline()` es reutilizable para regresión. No se necesita un composition root separado.

**Implicación:**

Fase 4 debe crear el entry point de regresión que:
1. Llame a `build_extraction_pipeline()` para obtener el parser de producción.
2. Verifique la integridad del oráculo sellado antes de evaluar.
3. Ejecute `parser.parse(pdf_path)` para generar el runtime AST.
4. Evalúe el runtime AST contra el oráculo sellado usando los evaluadores topológicos existentes.

### 16.3 ¿Existen rutas alternativas o parsers legacy que NO deben usarse en regresión?

**Estado actual verificado:**

1. `core/ast/parser.py` no existe (eliminado en fases anteriores).
2. `core/layout/builder.py` no existe (eliminado en fases anteriores).
3. `core/extraction/ocr_providers/pymupdf_provider.py` no existe (eliminado en fases anteriores).
4. `core/benchmark/__main__.py` usa `build_extraction_pipeline()`, no un parser legacy.

**Respuesta forense:**

No existen parsers legacy activos en el repositorio. Los gaps heredados de HITO_0.4.4 sobre uso de parser legacy son evidencia stale y están RESUELTOS.

**Implicación:**

Fase 4 no necesita preocuparse por rutas alternativas o parsers legacy. El único camino de extracción es a través de `build_extraction_pipeline()` o `CandidateGenerationService`.

### 16.4 ¿Qué gaps existen entre el pipeline auditado en Fase 0 y lo que Fase 4 necesita?

**Estado actual verificado:**

1. El pipeline de producción genera `Sequence[ASTNode]` compatible con los evaluadores topológicos.
2. El composition root es reutilizable para regresión.
3. No existe verificación de integridad del runtime AST antes de evaluar.
4. No existe Fail-Fast explícito si el PDF no existe o está corrupto.
5. Existe deuda técnica documentada (DF-12) sobre `LayoutBlockDraft` pero no es bloqueante.

**Respuesta forense:**

Los gaps pendientes son:
1. **Verificación de integridad del runtime AST:** El adaptador SealedOracle→evaluación debe verificar que el runtime AST fue generado por el pipeline correcto antes de evaluar.
2. **Verificación de PDF antes de extraer:** El provider o el entry point de regresión debe tener Fail-Fast explícito si el PDF no existe o está corrupto.
3. **Deuda técnica documentada:** La eliminación de `LayoutBlockDraft` es una tarea diferida (Fase 5 / Gate 3 del Execution Plan), no de Fase 4.

**Implicación:**

Fase 4 debe implementar:
1. Verificación de integridad del runtime AST en el adaptador SealedOracle→evaluación.
2. Fail-Fast en el entry point de regresión si el PDF no existe o está corrupto.
3. No debe preocuparse por la deuda técnica de `LayoutBlockDraft` (es tarea de Fase 5 / Execution Plan).

---

## 18. MATRIZ DE TRAZABILIDAD DC / GAP

| DC / GAP | Tema | Evidencia HITO vinculada | Estado operativo | Fase destino |
|---|---|---|---|---|
| **GAP-2.0-11** | Adaptador baseline→benchmark | HITO_4.3 E-4.3-001, GAP-4.5-01 | Adaptador ausente, composition root reutilizable | Fase 4 |
| **GAP-0.4-09** | Golden test tautológico / parser legacy | E-4.5-005, E-4.5-006 | RESUELTO: entry point usa pipeline real, parser legacy eliminado | CLOSED |
| **GAP-4.5-01** | Verificación de integridad del runtime AST | E-4.5-001 | Ausente | Fase 4 |
| **GAP-4.5-02** | Verificación de PDF antes de extraer | E-4.5-002 | Ausente | Fase 4 |
| **GAP-4.5-03** | Mapper transicional con deuda técnica | E-4.5-003 | Deuda documentada DF-12 | Fase 5 / Execution Plan |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Evaluación contra runtime AST corrupto | Si no se verifica la integridad del runtime AST antes de evaluar, se puede evaluar contra un AST generado por una ruta alternativa o corrupta. | Alto | E-4.5-001 |
| Excepciones no controladas durante extracción | Si el PDF no existe o está corrupto y no hay Fail-Fast explícito, el provider puede lanzar excepciones no controladas durante la extracción. | Medio | E-4.5-002 |
| Confusión entre deuda técnica y bloqueante | La deuda técnica de `LayoutBlockDraft` (DF-12) puede confundirse con un bloqueante para Fase 4, cuando en realidad es una tarea diferida a Fase 5 / Execution Plan. | Bajo | E-4.5-003 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR / NADR

Con base en este Discovery, el ADR o NADR posterior deberá responder:

1. ¿El entry point de regresión debe reutilizar `build_extraction_pipeline()` o `CandidateGenerationService`?
2. ¿Cómo se verifica que el runtime AST fue generado por el pipeline correcto antes de evaluar?
3. ¿El entry point de regresión debe aceptar configuración inyectada (`ExtractionConfiguration`) o debe usar defaults?
4. ¿Qué sucede si el PDF no existe o está corrupto durante la evaluación de regresión?
5. ¿El entry point de regresión debe ejecutar el pipeline completo (extracción + layout + AST) o solo la extracción?
6. ¿Cómo se integra la verificación de integridad del runtime AST con el adaptador SealedOracle→evaluación de HITO_4.3?
7. ¿La deuda técnica de `LayoutBlockDraft` (DF-12) debe resolverse en Fase 4 o se difiere a Fase 5 / Execution Plan?

---

## 21. CIERRE DEL HITO 4.5

Este HITO confirma que el composition root `build_extraction_pipeline()` es reutilizable para regresión. El entry point `core/benchmark/__main__.py` (benchmark de LLMs de Fase 16.10) usa el pipeline de producción real. No existen parsers legacy activos en el repositorio. Los gaps heredados de HITO_0.4.4 sobre uso de parser legacy son evidencia stale y se confirman como RESUELTOS. Los gaps pendientes son de verificación de integridad del runtime AST y Fail-Fast si el PDF no existe.

**Estado del HITO:** FROZEN v1.0.0
**Condición de cierre cumplida:** 100% de módulos del alcance auditados. Todas las evidencias tienen ID estable y severidad. Todos los gaps tienen evidencia vinculada y fase destino. Todas las hipótesis están cerradas como CONFIRMADA, RECHAZADA o RESUELTA. Cero hipótesis abiertas sin destino. Las correcciones de precisión y alineación terminológica (Gate 3 -> Fase 5 / Execution Plan) han sido aplicadas.
**Verificación de cadena de gobernanza:** ADR_F17_BIS_MASTER → HITO_0.4.4 → HITO_4.1 → HITO_4.2 → HITO_4.3 → HITO_4.4 → HITO_4.5 (este documento). Cadena completa verificada.
**Contradicciones con HITOs previos:** Ninguna. Los hallazgos confirman que los gaps heredados de HITO_0.4.4 sobre parser legacy están RESUELTOS. Los gaps pendientes son consistentes con HITO_4.3 (adaptador SealedOracle→evaluación).
**Decision Candidates generados:** Ninguno nuevo. Este HITO consolida evidencia para GAP-2.0-11 y confirma que GAP-0.4-09 está RESUELTO.
**Siguiente paso recomendado:** Construir ADR_F17-BIS_04 (Scientific Verification) y los NADRs de Fase 4, usando HITO_4.1–4.5 como evidencia forense. El Execution Plan de Fase 4 debe materializar el adaptador SealedOracle→evaluación, la verificación de integridad del runtime AST, y el entry point de regresión que reutilice `build_extraction_pipeline()`.